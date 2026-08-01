from __future__ import annotations

import json
import re
import shutil
import sysconfig
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
from typing import Any

from .engine import _load_json, _safe_file, _sha256


_CANDIDATE_ID = re.compile(r"^CAND-[A-Z0-9][A-Z0-9._-]{2,79}$")
_POLICY_FILENAMES = {
    "governance": "governance.json",
    "tailoring": "tailoring.json",
    "change_triggers": "change-triggers.json",
}


def _write_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def _template_root() -> Path:
    source_root = Path(__file__).resolve().parents[2]
    if (source_root / "evidence-pack-template").is_dir():
        return source_root

    try:
        installed = distribution("evaluation-methodology-gate")
    except PackageNotFoundError:
        installed = None
    if installed is not None:
        distribution_root = Path(
            installed.locate_file("share/evaluation-methodology")
        ).resolve()
        if (distribution_root / "evidence-pack-template").is_dir():
            return distribution_root

    installed_root = Path(sysconfig.get_path("data")) / "share" / "evaluation-methodology"
    if (installed_root / "evidence-pack-template").is_dir():
        return installed_root

    raise ValueError("installed scaffold templates were not found; reinstall the release package")


def _required_file(root: Path, relative: str, label: str) -> Path:
    path = _safe_file(root, relative)
    if path is None:
        raise ValueError(f"{label} file is missing or escapes the pack: {relative}")
    return path


def refresh_hashes(
    pack_dir: Path,
    governance_path: Path,
    tailoring_path: Path,
    change_policy_path: Path,
    *,
    include_approval: bool = False,
) -> dict[str, str]:
    """Refresh declared file hashes without judging the truth of their contents."""

    pack_dir = pack_dir.resolve()
    pack_path = _required_file(pack_dir, "pack.json", "pack")
    pack = _load_json(pack_path)
    file_map = pack.get("file_map")
    if not isinstance(file_map, dict):
        raise ValueError("pack.json.file_map must be an object")

    approval_path: Path | None = None
    approval: dict[str, Any] | None = None
    if include_approval:
        approval_path = _required_file(pack_dir, file_map.get("approval_decision", ""), "approval decision")
        approval = _load_json(approval_path)
        if approval.get("artifact_status") == "final":
            raise ValueError(
                "refusing to rebind a final approval; return it to draft, refresh hashes, "
                "and obtain a new accountable decision"
            )
        if not isinstance(approval.get("input_hashes"), dict):
            raise ValueError("approval-decision.json.input_hashes must be an object")

    policy_paths = {
        "governance": governance_path.resolve(),
        "tailoring": tailoring_path.resolve(),
        "change_triggers": change_policy_path.resolve(),
    }
    bindings = pack.get("policy_bindings")
    if not isinstance(bindings, list):
        raise ValueError("pack.json.policy_bindings must be an array")

    seen_policy_types: set[str] = set()
    for binding in bindings:
        policy_type = binding.get("policy_type") if isinstance(binding, dict) else None
        if policy_type not in policy_paths or policy_type in seen_policy_types:
            raise ValueError("pack.json must contain one binding for each supported policy type")
        policy = _load_json(policy_paths[policy_type])
        binding["policy_id"] = policy.get("policy_id")
        binding["version"] = policy.get("version")
        binding["sha256"] = _sha256(policy_paths[policy_type])
        seen_policy_types.add(policy_type)
    if seen_policy_types != set(policy_paths):
        raise ValueError("pack.json must bind governance, tailoring, and change_triggers policies")

    manifest_path = _required_file(pack_dir, file_map.get("system_manifest", ""), "system manifest")
    manifest = _load_json(manifest_path)
    for path_key, hash_key, label in (
        ("prompt_bundle_path", "prompt_bundle_sha256", "prompt bundle"),
        ("configuration_path", "configuration_sha256", "runtime configuration"),
    ):
        artifact = _required_file(pack_dir, manifest.get(path_key, ""), label)
        manifest[hash_key] = _sha256(artifact)

    cases_path = _required_file(pack_dir, file_map.get("evaluation_cases", ""), "evaluation cases")
    cases = _load_json(cases_path)
    dataset = _required_file(pack_dir, cases.get("dataset_path", ""), "evaluation dataset")
    cases["dataset_sha256"] = _sha256(dataset)

    evidence_path = _required_file(pack_dir, file_map.get("evidence_index", ""), "evidence index")
    evidence_index = _load_json(evidence_path)
    evidence_items = evidence_index.get("evidence")
    if not isinstance(evidence_items, list):
        raise ValueError("evidence-index.json.evidence must be an array")
    for item in evidence_items:
        if not isinstance(item, dict):
            raise ValueError("evidence-index.json contains a non-object evidence record")
        artifact = _required_file(pack_dir, item.get("path", ""), f"evidence {item.get('evidence_id', '')}")
        item["sha256"] = _sha256(artifact)

    _write_json(manifest_path, manifest)
    _write_json(cases_path, cases)
    _write_json(evidence_path, evidence_index)

    _write_json(pack_path, pack)

    refreshed = {
        "pack": _sha256(pack_path),
        "system_manifest": _sha256(manifest_path),
        "evaluation_cases": _sha256(cases_path),
        "evidence_index": _sha256(evidence_path),
    }

    if include_approval:
        assert approval_path is not None and approval is not None
        input_hashes = approval.get("input_hashes")
        assert isinstance(input_hashes, dict)
        for key in tuple(input_hashes):
            relative = "pack.json" if key == "pack" else file_map.get(key)
            if not isinstance(relative, str):
                raise ValueError(f"approval input {key} has no matching pack file")
            input_path = _required_file(pack_dir, relative, f"approval input {key}")
            input_hashes[key] = _sha256(input_path)
            refreshed[key] = input_hashes[key]
        _write_json(approval_path, approval)

    return refreshed


def init_workspace(target: Path, candidate_id: str, name: str) -> tuple[Path, Path]:
    """Create a non-approvable Tier 1 starter using the released templates."""

    if not _CANDIDATE_ID.fullmatch(candidate_id):
        raise ValueError("candidate ID must match CAND-[A-Z0-9][A-Z0-9._-]{2,79}")
    if not name.strip():
        raise ValueError("candidate name cannot be empty")

    target = target.resolve()
    if target.exists() and any(target.iterdir()):
        raise ValueError(f"target directory is not empty: {target}")

    template_root = _template_root()
    governance_dir = target / "governance"
    pack_dir = target / "evidence" / "current"
    governance_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template_root / "evidence-pack-template", pack_dir)
    for source_name, destination_name in (
        ("governance.example.json", "governance.json"),
        ("tailoring.reference.json", "tailoring.json"),
        ("change-triggers.reference.json", "change-triggers.json"),
    ):
        shutil.copy2(template_root / "config" / source_name, governance_dir / destination_name)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    for path in pack_dir.glob("*.json"):
        document = _load_json(path)
        if "candidate_id" in document:
            document["candidate_id"] = candidate_id
        if path.name == "pack.json":
            document["pack_id"] = ("PACK-" + candidate_id.removeprefix("CAND-"))[:64]
            document["created_at"] = now
        elif path.name == "system-manifest.json":
            document["name"] = name.strip()
        elif path.name == "change-assessment.json":
            document["assessed_at"] = now
        elif path.name == "approval-decision.json":
            document["decided_at"] = now
        _write_json(path, document)

    refresh_hashes(
        pack_dir,
        governance_dir / _POLICY_FILENAMES["governance"],
        governance_dir / _POLICY_FILENAMES["tailoring"],
        governance_dir / _POLICY_FILENAMES["change_triggers"],
        include_approval=True,
    )
    return target, pack_dir
