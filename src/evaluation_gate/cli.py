from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .engine import assess_change, evaluate_pack
from .onboarding import init_workspace, refresh_hashes


def _as_of(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("--as-of must include a timezone")
    return parsed.astimezone(timezone.utc)


def _write_report(report: dict[str, object], output: str | None, output_format: str) -> None:
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if output:
        Path(output).write_text(rendered + "\n", encoding="utf-8")
    if output_format == "json":
        print(rendered)
        return
    print(f"Decision: {report['decision']}")
    print(f"Gate version: {report.get('gate_version', 'unknown')}")
    print(f"Mode: {report.get('mode') or 'unknown'}")
    print(f"Authorizes deployment: {str(bool(report.get('authorizes_deployment'))).lower()}")
    if report.get("tier"):
        print(f"Tier: {report['tier']}")
    print(f"Blocking issues: {len(report.get('blocking_issues', []))}")
    print(f"Warnings: {len(report.get('warnings', []))}")
    for issue in report.get("blocking_issues", []):
        print(f"BLOCK {issue['code']} {issue['path']}: {issue['message']}")
    for issue in report.get("warnings", []):
        print(f"WARN  {issue['code']} {issue['path']}: {issue['message']}")


def _write_change_report(report: dict[str, object], output: str | None, output_format: str) -> None:
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if output:
        Path(output).write_text(rendered + "\n", encoding="utf-8")
    if output_format == "json":
        print(rendered)
        return
    print(f"Change assessment: {report['decision']}")
    print(f"Required reassessment scope: {report.get('required_scope') or 'unavailable'}")
    evidence_types = report.get("required_evidence_types", [])
    print(f"Required evidence types: {', '.join(evidence_types) if evidence_types else 'none'}")
    requires_new_approval = report.get("requires_new_approval")
    approval_text = "unknown" if requires_new_approval is None else str(bool(requires_new_approval)).lower()
    print(f"Requires new approval: {approval_text}")
    print(f"Issues: {len(report.get('issues', []))}")
    for issue in report.get("issues", []):
        print(f"ISSUE {issue['code']} {issue['path']}: {issue['message']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evaluation-gate",
        description="Validate a methodology evidence pack and compute its release decision.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_pack_arguments(command: argparse.ArgumentParser) -> None:
        command.add_argument("--pack", required=True, help="Evidence-pack directory containing pack.json")
        command.add_argument("--governance", required=True, help="Approved governance policy JSON")
        command.add_argument("--tailoring", required=True, help="Approved tailoring policy JSON")
        command.add_argument("--change-policy", required=True, help="Approved change-trigger policy JSON")
        command.add_argument("--as-of", help="UTC-aware ISO-8601 replay time; fictional packs only; production always uses now")
        command.add_argument("--allow-fictional", action="store_true", help="Permit a fictional example pack; never use for deployment")
        command.add_argument("--format", choices=("text", "json"), default="text")
        command.add_argument("--output", help="Also write the JSON report to this path")

    gate = subparsers.add_parser("gate", help="Validate an approved evidence pack and return APPROVE, CONDITIONAL, or REJECT")
    add_pack_arguments(gate)
    gate.add_argument("--allow-conditional", action="store_true", help="Return success for a valid conditional approval")

    preflight = subparsers.add_parser("preflight", help="Validate evidence before accountable human approval")
    add_pack_arguments(preflight)

    change = subparsers.add_parser("assess-change", help="Compute the minimum reassessment scope for a change record")
    change.add_argument("--assessment", required=True, help="Change-assessment JSON")
    change.add_argument("--policy", required=True, help="Change-trigger policy JSON")
    change.add_argument("--format", choices=("text", "json"), default="text")
    change.add_argument("--output", help="Also write the JSON report to this path")

    init = subparsers.add_parser("init", help="Create a minimal, non-approvable Tier 1 starter workspace")
    init.add_argument("directory", help="Empty directory to create or populate")
    init.add_argument("--candidate-id", required=True, help="Stable identifier such as CAND-SUPPORT-001")
    init.add_argument("--name", required=True, help="Human-readable candidate name")

    hashes = subparsers.add_parser("hash", help="Refresh declared file hashes; this does not validate evidence truth")
    hashes.add_argument("--pack", required=True, help="Evidence-pack directory containing pack.json")
    hashes.add_argument("--governance", required=True, help="Governance policy JSON")
    hashes.add_argument("--tailoring", required=True, help="Tailoring policy JSON")
    hashes.add_argument("--change-policy", required=True, help="Change-trigger policy JSON")
    hashes.add_argument("--approval", action="store_true", help="Also bind the approval decision to current input files")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            target, pack = init_workspace(Path(args.directory), args.candidate_id, args.name)
            print(f"Created starter workspace: {target}")
            print(f"Evidence pack: {pack}")
            print("Status: template only; replace placeholders and obtain real approval before production use")
            return 0

        if args.command == "hash":
            refreshed = refresh_hashes(
                Path(args.pack),
                Path(args.governance),
                Path(args.tailoring),
                Path(args.change_policy),
                include_approval=args.approval,
            )
            print(f"Refreshed {len(refreshed)} declared hashes")
            print("Hashing binds bytes; it does not establish that evidence is truthful or sufficient")
            return 0

        if args.command in {"gate", "preflight"}:
            report = evaluate_pack(
                pack_dir=Path(args.pack),
                governance_path=Path(args.governance),
                tailoring_path=Path(args.tailoring),
                change_policy_path=Path(args.change_policy),
                as_of=_as_of(args.as_of),
                allow_fictional=args.allow_fictional,
                preflight=args.command == "preflight",
            )
            payload = report.to_dict()
            _write_report(payload, args.output, args.format)
            if report.decision in {"APPROVE", "ELIGIBLE", "ELIGIBLE_WITH_CONDITIONS"}:
                return 0
            if report.decision in {"SIMULATED_APPROVE", "SIMULATED_CONDITIONAL"}:
                return 3
            if report.decision == "CONDITIONAL" and args.allow_conditional:
                return 0
            return 2 if report.decision == "CONDITIONAL" else 1

        payload = assess_change(Path(args.assessment), Path(args.policy))
        _write_change_report(payload, args.output, args.format)
        return 0 if payload["decision"] == "VALID" else 1
    except (OSError, ValueError) as exc:
        print(f"evaluation-gate: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
