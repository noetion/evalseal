from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from evalseal.cli import main as cli_main
from evalseal.engine import GateReport, _schema_bundle, assess_change, evaluate_pack
from evalseal.onboarding import refresh_hashes


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "fictional-support-assistant"
AS_OF = datetime(2026, 7, 31, 12, 30, tzinfo=timezone.utc)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def codes(report) -> set[str]:
    return {issue.code for issue in report.blocking_issues}


class GateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.pack = self.base / "evidence-pack"
        shutil.copytree(EXAMPLE / "evidence-pack", self.pack)
        self.governance = self.base / "governance.json"
        shutil.copy2(EXAMPLE / "governance.json", self.governance)
        self.tailoring = ROOT / "config" / "tailoring.reference.json"
        self.change_policy = ROOT / "config" / "change-triggers.reference.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def evaluate(self, *, allow_fictional: bool = True, as_of: datetime = AS_OF):
        return evaluate_pack(
            self.pack,
            self.governance,
            self.tailoring,
            self.change_policy,
            as_of=as_of,
            allow_fictional=allow_fictional,
        )

    def test_all_schemas_are_valid(self) -> None:
        schemas, _ = _schema_bundle()
        self.assertEqual(13, len(schemas))

    @patch("evalseal.cli.evaluate_pack")
    def test_cli_omitted_as_of_uses_live_production_time(self, mocked_evaluate) -> None:
        mocked_evaluate.return_value = GateReport(
            "APPROVE", "PACK-PRODUCTION", "CAND-PRODUCTION-001", "tier_3",
            "2026-07-31T20:00:00+00:00", (), (), (), mode="production", authorizes_deployment=True
        )
        result = cli_main([
            "gate", "--pack", "pack", "--governance", "governance.json",
            "--tailoring", "tailoring.json", "--change-policy", "change.json"
        ])
        self.assertEqual(0, result)
        self.assertIsNone(mocked_evaluate.call_args.kwargs["as_of"])

    @patch("evalseal.cli.evaluate_pack")
    def test_cli_explicit_as_of_is_passed_for_engine_rejection(self, mocked_evaluate) -> None:
        mocked_evaluate.return_value = GateReport(
            "REJECT", "PACK-PRODUCTION", "CAND-PRODUCTION-001", "tier_3",
            "2026-07-30T20:00:00+00:00", (), (), (), mode="production"
        )
        result = cli_main([
            "gate", "--pack", "pack", "--governance", "governance.json",
            "--tailoring", "tailoring.json", "--change-policy", "change.json",
            "--as-of", "2026-07-30T20:00:00Z"
        ])
        self.assertEqual(1, result)
        self.assertIsNotNone(mocked_evaluate.call_args.kwargs["as_of"])

    def test_init_creates_minimal_non_approvable_workspace(self) -> None:
        target = self.base / "starter"
        result = cli_main([
            "init", str(target),
            "--candidate-id", "CAND-QUICKSTART-001",
            "--name", "Quickstart assistant",
        ])
        self.assertEqual(0, result)
        pack = read_json(target / "evidence" / "current" / "pack.json")
        manifest = read_json(target / "evidence" / "current" / "system-manifest.json")
        self.assertEqual("template", pack["mode"])
        self.assertEqual("CAND-QUICKSTART-001", pack["candidate_id"])
        self.assertEqual("tier_1", manifest["declared_tier"])
        self.assertEqual("Quickstart assistant", manifest["name"])
        self.assertTrue((target / "governance" / "governance.json").is_file())

        report = evaluate_pack(
            target / "evidence" / "current",
            target / "governance" / "governance.json",
            target / "governance" / "tailoring.json",
            target / "governance" / "change-triggers.json",
            as_of=AS_OF,
        )
        self.assertEqual("REJECT", report.decision)
        self.assertIn("NON_PRODUCTION_PACK", codes(report))

    def test_init_refuses_to_overwrite_nonempty_directory(self) -> None:
        target = self.base / "occupied"
        target.mkdir()
        (target / "keep.txt").write_text("preserve", encoding="utf-8")
        result = cli_main([
            "init", str(target),
            "--candidate-id", "CAND-QUICKSTART-001",
            "--name", "Quickstart assistant",
        ])
        self.assertEqual(1, result)
        self.assertEqual("preserve", (target / "keep.txt").read_text(encoding="utf-8"))

    def test_hash_refreshes_artifact_and_approval_bindings(self) -> None:
        artifact = self.pack / "artifacts" / "evaluation-report.md"
        artifact.write_text(artifact.read_text(encoding="utf-8") + "\nclarification\n", encoding="utf-8")
        self.assertIn("EVIDENCE_HASH_MISMATCH", codes(self.evaluate()))

        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["artifact_status"] = "draft"
        approval["decision"] = "reject"
        write_json(approval_path, approval)

        refresh_hashes(
            self.pack,
            self.governance,
            self.tailoring,
            self.change_policy,
            include_approval=True,
        )
        approval = read_json(approval_path)
        approval["artifact_status"] = "final"
        approval["decision"] = "approve"
        write_json(approval_path, approval)
        report = self.evaluate()
        self.assertEqual("SIMULATED_APPROVE", report.decision)
        self.assertFalse(report.blocking_issues)

    def test_hash_refuses_to_rebind_final_approval(self) -> None:
        before = {
            path.name: path.read_bytes()
            for path in self.pack.glob("*.json")
        }
        with self.assertRaisesRegex(ValueError, "refusing to rebind a final approval"):
            refresh_hashes(
                self.pack,
                self.governance,
                self.tailoring,
                self.change_policy,
                include_approval=True,
            )
        after = {
            path.name: path.read_bytes()
            for path in self.pack.glob("*.json")
        }
        self.assertEqual(before, after)

    def test_hash_writes_canonical_lf_json(self) -> None:
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["artifact_status"] = "draft"
        approval["decision"] = "reject"
        approval_path.write_bytes(
            (json.dumps(approval, indent=2) + "\n").replace("\n", "\r\n").encode("utf-8")
        )

        refresh_hashes(
            self.pack,
            self.governance,
            self.tailoring,
            self.change_policy,
            include_approval=True,
        )

        for name in (
            "pack.json",
            "system-manifest.json",
            "evaluation-cases.json",
            "evidence-index.json",
            "approval-decision.json",
        ):
            self.assertNotIn(b"\r\n", (self.pack / name).read_bytes())

    def test_template_is_schema_valid_but_never_approvable(self) -> None:
        report = evaluate_pack(
            ROOT / "evidence-pack-template",
            ROOT / "config" / "governance.example.json",
            self.tailoring,
            self.change_policy,
            as_of=AS_OF,
        )
        self.assertEqual("REJECT", report.decision)
        self.assertIn("NON_PRODUCTION_PACK", codes(report))
        self.assertNotIn("SCHEMA_INVALID", codes(report))

    def test_template_approval_binds_exact_template_inputs(self) -> None:
        template = ROOT / "evidence-pack-template"
        pack = read_json(template / "pack.json")
        approval = read_json(template / "approval-decision.json")

        for key, expected in approval["input_hashes"].items():
            relative = "pack.json" if key == "pack" else pack["file_map"][key]
            actual = hashlib.sha256((template / relative).read_bytes()).hexdigest()
            self.assertEqual(expected, actual, key)

    def test_json_schema_date_time_format_is_enforced(self) -> None:
        pack_path = self.pack / "pack.json"
        pack = read_json(pack_path)
        pack["created_at"] = "not-a-timestamp"
        write_json(pack_path, pack)

        report = self.evaluate()

        self.assertIn("SCHEMA_INVALID", codes(report))
        self.assertTrue(
            any("date-time" in issue.message for issue in report.blocking_issues)
        )

    def test_duplicate_json_object_keys_are_rejected(self) -> None:
        path = self.pack / "pack.json"
        rendered = path.read_text(encoding="utf-8")
        rendered = rendered.replace(
            '"pack_id": "PACK-SUPPORT-20260731",',
            '"pack_id": "PACK-SUPPORT-20260731",\n  "pack_id": "PACK-DUPLICATE",',
        )
        path.write_text(rendered, encoding="utf-8")
        report = self.evaluate()
        self.assertIn("LOAD_ERROR", codes(report))
        self.assertIn("duplicate JSON object key", report.blocking_issues[0].message)

    def test_complete_fictional_pack_is_approved(self) -> None:
        report = self.evaluate()
        self.assertEqual("SIMULATED_APPROVE", report.decision)
        self.assertEqual("tier_3", report.tier)
        self.assertFalse(report.blocking_issues)
        self.assertFalse(report.authorizes_deployment)
        self.assertEqual("fictional", report.mode)
        self.assertEqual("0.1.0", report.gate_version)
        self.assertIn("gate_source", report.digests)
        self.assertIn("approval_decision", report.digests)

    def test_preflight_is_eligible_before_final_approval_checks(self) -> None:
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["artifact_status"] = "draft"
        approval["decision"] = "reject"
        approval["approvers"] = [{"actor_id": "ACT-RELEASE", "role": "release_authority", "approved_at": "2026-07-31T12:00:00Z"}]
        write_json(approval_path, approval)
        report = evaluate_pack(
            self.pack,
            self.governance,
            self.tailoring,
            self.change_policy,
            as_of=AS_OF,
            allow_fictional=True,
            preflight=True,
        )
        self.assertEqual("ELIGIBLE", report.decision)

    def test_fictional_pack_is_rejected_without_explicit_flag(self) -> None:
        report = self.evaluate(allow_fictional=False)
        self.assertEqual("REJECT", report.decision)
        self.assertIn("NON_PRODUCTION_PACK", codes(report))

    def test_missing_evidence_file_is_rejected(self) -> None:
        (self.pack / "artifacts" / "security-report.md").unlink()
        report = self.evaluate()
        self.assertEqual("REJECT", report.decision)
        self.assertIn("EVIDENCE_FILE_MISSING", codes(report))

    def test_changed_evidence_hash_is_rejected(self) -> None:
        path = self.pack / "artifacts" / "evaluation-report.md"
        path.write_text(path.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
        report = self.evaluate()
        self.assertIn("EVIDENCE_HASH_MISMATCH", codes(report))

    def test_changed_prompt_bundle_hash_is_rejected(self) -> None:
        path = self.pack / "artifacts" / "prompt-bundle.txt"
        path.write_text(path.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
        report = self.evaluate()
        self.assertIn("MANIFEST_HASH_MISMATCH", codes(report))

    def test_changed_evaluation_dataset_hash_is_rejected(self) -> None:
        path = self.pack / "artifacts" / "evaluation-dataset.json"
        path.write_text("[]\n", encoding="utf-8")
        report = self.evaluate()
        self.assertIn("EVALUATION_DATASET_HASH_MISMATCH", codes(report))

    def test_expired_evidence_is_rejected(self) -> None:
        path = self.pack / "evidence-index.json"
        value = read_json(path)
        value["evidence"][0]["valid_until"] = "2026-07-31T12:00:00Z"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("EVIDENCE_EXPIRED", codes(report))

    def test_expired_control_verification_is_rejected(self) -> None:
        path = self.pack / "controls.json"
        value = read_json(path)
        value["controls"][0]["verification_valid_until"] = "2026-07-31T12:00:00Z"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("CONTROL_VERIFICATION_EXPIRED", codes(report))

    def test_open_blocking_finding_is_rejected(self) -> None:
        path = self.pack / "findings.json"
        value = read_json(path)
        value["findings"][0]["status"] = "open"
        value["findings"][0].pop("retest_evidence_id")
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("BLOCKING_FINDING_OPEN", codes(report))

    def test_unauthorized_risk_acceptance_is_rejected(self) -> None:
        path = self.pack / "risk-register.json"
        value = read_json(path)
        risk = value["risks"][0]
        risk["treatment"] = "accept"
        risk["status"] = "accepted"
        risk["control_ids"] = []
        risk["acceptance"] = {
            "actor_id": "ACT-SYSTEM",
            "role": "system_owner",
            "accepted_at": "2026-07-31T11:00:00Z",
            "expires_at": "2026-09-30T11:00:00Z",
            "rationale": "Fictional attempt to accept more risk than this role is permitted to accept."
        }
        write_json(path, value)
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["residual_risk_ids"] = [risk["risk_id"]]
        write_json(approval_path, approval)
        report = self.evaluate()
        self.assertIn("RISK_ACCEPTANCE_EXCEEDS_AUTHORITY", codes(report))

    def test_missing_conditional_approval_role_is_rejected(self) -> None:
        path = self.pack / "approval-decision.json"
        value = read_json(path)
        value["approvers"] = [item for item in value["approvers"] if item["role"] != "privacy_reviewer"]
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("APPROVAL_ROLE_MISSING", codes(report))

    def test_approver_before_required_evidence_is_rejected(self) -> None:
        path = self.pack / "approval-decision.json"
        value = read_json(path)
        value["approvers"][0]["approved_at"] = "2026-07-29T08:00:00Z"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("APPROVER_PREDATES_EVIDENCE", codes(report))

    def test_nonblocking_finding_with_bounded_condition_is_conditional(self) -> None:
        findings_path = self.pack / "findings.json"
        findings = read_json(findings_path)
        findings["findings"].append({
            "finding_id": "FIND-DOCS-01",
            "source_evidence_id": "EVID-EVALUATION",
            "risk_id": "RISK-UNSUPPORTED",
            "title": "Minor operator wording needs clarification",
            "severity": "low",
            "blocking": False,
            "status": "remediating",
            "owner_actor_id": "ACT-SYSTEM",
            "remediation": "Clarify the operator-facing limitation wording before the recorded due date."
        })
        write_json(findings_path, findings)
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["decision"] = "approve_with_conditions"
        approval["input_hashes"]["findings"] = hashlib.sha256(findings_path.read_bytes()).hexdigest()
        approval["approvers"].append({"actor_id": "ACT-GOVERNANCE", "role": "executive_risk_authority", "approved_at": "2026-07-31T11:50:00Z"})
        approval["conditions"] = [{
            "condition_id": "COND-DOCS-01",
            "description": "Clarify the operator-facing limitation wording.",
            "owner_actor_id": "ACT-SYSTEM",
            "finding_ids": ["FIND-DOCS-01"],
            "due_at": "2026-08-14T12:00:00Z",
            "status": "open"
        }]
        approval["next_review_at"] = "2026-08-14T12:00:00Z"
        write_json(approval_path, approval)
        report = self.evaluate()
        self.assertEqual("SIMULATED_CONDITIONAL", report.decision)
        self.assertFalse(report.blocking_issues)

    def test_conditional_approvers_cannot_predate_optional_finding_source(self) -> None:
        evidence_path = self.pack / "evidence-index.json"
        evidence_index = read_json(evidence_path)
        source = dict(evidence_index["evidence"][-1])
        source.update({
            "evidence_id": "EVID-OPTIONAL-FINDING",
            "produced_at": "2026-07-31T11:58:00Z",
            "scope": "Optional evidence that produced a bounded non-blocking finding late in the approval workflow.",
        })
        evidence_index["evidence"].append(source)
        write_json(evidence_path, evidence_index)
        findings_path = self.pack / "findings.json"
        findings = read_json(findings_path)
        findings["findings"].append({
            "finding_id": "FIND-OPTIONAL-LATE",
            "source_evidence_id": "EVID-OPTIONAL-FINDING",
            "risk_id": "RISK-UNSUPPORTED",
            "title": "Late optional finding requires a bounded condition",
            "severity": "low",
            "blocking": False,
            "status": "remediating",
            "owner_actor_id": "ACT-SYSTEM",
            "remediation": "Clarify and verify the affected operator guidance before the bounded condition expires.",
        })
        write_json(findings_path, findings)
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["decision"] = "approve_with_conditions"
        approval["input_hashes"]["evidence_index"] = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        approval["input_hashes"]["findings"] = hashlib.sha256(findings_path.read_bytes()).hexdigest()
        approval["approvers"].append({
            "actor_id": "ACT-GOVERNANCE",
            "role": "executive_risk_authority",
            "approved_at": "2026-07-31T11:59:00Z",
        })
        approval["conditions"] = [{
            "condition_id": "COND-OPTIONAL-LATE",
            "description": "Resolve the late optional finding.",
            "owner_actor_id": "ACT-SYSTEM",
            "finding_ids": ["FIND-OPTIONAL-LATE"],
            "due_at": "2026-08-14T12:00:00Z",
            "status": "open",
        }]
        approval["next_review_at"] = "2026-08-14T12:00:00Z"
        write_json(approval_path, approval)
        report = self.evaluate()
        self.assertIn("APPROVER_PREDATES_BASIS", codes(report))

    def test_conditional_release_requires_exception_authority(self) -> None:
        findings_path = self.pack / "findings.json"
        findings = read_json(findings_path)
        findings["findings"].append({
            "finding_id": "FIND-COND-AUTH", "source_evidence_id": "EVID-EVALUATION",
            "risk_id": "RISK-UNSUPPORTED", "title": "Minor conditional documentation finding",
            "severity": "low", "blocking": False, "status": "remediating",
            "owner_actor_id": "ACT-SYSTEM", "remediation": "Clarify the operator wording before the bounded due date."
        })
        write_json(findings_path, findings)
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["decision"] = "approve_with_conditions"
        approval["input_hashes"]["findings"] = hashlib.sha256(findings_path.read_bytes()).hexdigest()
        approval["conditions"] = [{
            "condition_id": "COND-AUTH", "description": "Clarify the operator wording.",
            "owner_actor_id": "ACT-SYSTEM", "finding_ids": ["FIND-COND-AUTH"],
            "due_at": "2026-08-14T12:00:00Z", "status": "open"
        }]
        write_json(approval_path, approval)
        report = self.evaluate()
        self.assertIn("APPROVAL_ROLE_MISSING", codes(report))

    def test_conditional_finding_severity_is_bounded(self) -> None:
        findings_path = self.pack / "findings.json"
        findings = read_json(findings_path)
        findings["findings"].append({
            "finding_id": "FIND-COND-HIGH", "source_evidence_id": "EVID-EVALUATION",
            "risk_id": "RISK-UNSUPPORTED", "title": "High severity finding mislabeled nonblocking",
            "severity": "high", "blocking": False, "status": "remediating",
            "owner_actor_id": "ACT-SYSTEM", "remediation": "Correct the high severity issue before any release."
        })
        write_json(findings_path, findings)
        report = self.evaluate()
        self.assertIn("FINDING_OUTSIDE_CONDITIONAL_TOLERANCE", codes(report))

    def test_condition_duration_is_bounded(self) -> None:
        findings_path = self.pack / "findings.json"
        findings = read_json(findings_path)
        findings["findings"].append({
            "finding_id": "FIND-COND-LONG", "source_evidence_id": "EVID-EVALUATION",
            "risk_id": "RISK-UNSUPPORTED", "title": "Minor but overlong release condition",
            "severity": "low", "blocking": False, "status": "remediating",
            "owner_actor_id": "ACT-SYSTEM", "remediation": "Resolve the wording issue within the configured exception window."
        })
        write_json(findings_path, findings)
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["decision"] = "approve_with_conditions"
        approval["input_hashes"]["findings"] = hashlib.sha256(findings_path.read_bytes()).hexdigest()
        approval["approvers"].append({"actor_id": "ACT-GOVERNANCE", "role": "executive_risk_authority", "approved_at": "2026-07-31T11:50:00Z"})
        approval["conditions"] = [{
            "condition_id": "COND-LONG", "description": "Resolve the wording issue.",
            "owner_actor_id": "ACT-SYSTEM", "finding_ids": ["FIND-COND-LONG"],
            "due_at": "2026-10-01T12:00:00Z", "status": "open"
        }]
        write_json(approval_path, approval)
        report = self.evaluate()
        self.assertIn("CONDITION_TOO_LONG", codes(report))

    def test_newer_failed_required_evidence_overrides_older_pass(self) -> None:
        path = self.pack / "evidence-index.json"
        value = read_json(path)
        failed = dict(value["evidence"][0])
        failed.update({"evidence_id": "EVID-EVALUATION-FAILED", "produced_at": "2026-07-31T11:00:00Z", "status": "fail"})
        value["evidence"].append(failed)
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("LATEST_REQUIRED_EVIDENCE_FAILED", codes(report))
        self.assertIn("FAILED_EVIDENCE_WITHOUT_FINDING", codes(report))

    def test_failed_retest_cannot_verify_a_fix(self) -> None:
        path = self.pack / "evidence-index.json"
        value = read_json(path)
        for item in value["evidence"]:
            if item["evidence_id"] == "EVID-INJECTION-RETEST":
                item["status"] = "fail"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("FINDING_RETEST_FAILED", codes(report))

    def test_approval_must_include_retest_evidence_in_its_basis(self) -> None:
        path = self.pack / "approval-decision.json"
        value = read_json(path)
        value["evidence_ids"].remove("EVID-INJECTION-RETEST")
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("APPROVAL_BASIS_EVIDENCE_INCOMPLETE", codes(report))

    def test_failed_source_can_be_remediated_and_approved_with_passing_retest(self) -> None:
        evidence_path = self.pack / "evidence-index.json"
        evidence_index = read_json(evidence_path)
        source = dict(evidence_index["evidence"][-1])
        source.update({
            "evidence_id": "EVID-FAILED-SOURCE",
            "produced_at": "2026-07-30T11:15:00Z",
            "status": "fail",
            "scope": "Historical failed evidence retained for a finding that was subsequently remediated and retested.",
        })
        evidence_index["evidence"].append(source)
        write_json(evidence_path, evidence_index)
        findings_path = self.pack / "findings.json"
        findings = read_json(findings_path)
        findings["findings"].append({
            "finding_id": "FIND-REMEDIATED-02",
            "source_evidence_id": "EVID-FAILED-SOURCE",
            "risk_id": "RISK-INJECTION",
            "title": "Historical failed test was remediated",
            "severity": "high",
            "blocking": True,
            "status": "verified_fixed",
            "owner_actor_id": "ACT-CONTROL",
            "remediation": "The historical failed behavior was corrected and verified by a distinct passing retest.",
            "retest_evidence_id": "EVID-INJECTION-RETEST",
        })
        write_json(findings_path, findings)
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["input_hashes"]["evidence_index"] = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        approval["input_hashes"]["findings"] = hashlib.sha256(findings_path.read_bytes()).hexdigest()
        write_json(approval_path, approval)
        report = self.evaluate()
        self.assertEqual("SIMULATED_APPROVE", report.decision)
        self.assertFalse(report.blocking_issues)

    def test_approval_cannot_predate_retest_evidence(self) -> None:
        path = self.pack / "evidence-index.json"
        value = read_json(path)
        for item in value["evidence"]:
            if item["evidence_id"] == "EVID-INJECTION-RETEST":
                item["produced_at"] = "2026-07-31T12:15:00Z"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("APPROVAL_PREDATES_BASIS", codes(report))

    def test_approval_cannot_predate_control_verification(self) -> None:
        path = self.pack / "controls.json"
        value = read_json(path)
        value["controls"][0]["verified_at"] = "2026-07-31T12:15:00Z"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("APPROVAL_PREDATES_BASIS", codes(report))

    def test_approval_cannot_predate_false_positive_disposition(self) -> None:
        path = self.pack / "findings.json"
        value = read_json(path)
        finding = value["findings"][0]
        finding["status"] = "false_positive"
        finding.pop("retest_evidence_id")
        finding["false_positive_disposition"] = {
            "actor_id": "ACT-INDEPENDENT",
            "role": "independent_reviewer",
            "decided_at": "2026-07-31T12:15:00Z",
            "rationale": "Independent review determined that the recorded behavior did not cross the declared trust boundary.",
            "evidence_ids": ["EVID-INJECTION-RETEST"],
        }
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("APPROVAL_PREDATES_BASIS", codes(report))

    def test_stale_nonrequired_approval_evidence_is_rejected(self) -> None:
        evidence_path = self.pack / "evidence-index.json"
        evidence_index = read_json(evidence_path)
        stale = dict(evidence_index["evidence"][-1])
        stale.update({
            "evidence_id": "EVID-STALE-SUPPLEMENT",
            "produced_at": "2025-01-01T00:00:00Z",
            "valid_until": "2026-08-01T00:00:00Z",
            "scope": "A deliberately stale supplemental record included in the signed approval basis.",
        })
        evidence_index["evidence"].append(stale)
        write_json(evidence_path, evidence_index)
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["evidence_ids"].append("EVID-STALE-SUPPLEMENT")
        write_json(approval_path, approval)
        report = self.evaluate()
        self.assertIn("APPROVAL_EVIDENCE_STALE", codes(report))

    def test_control_verification_cannot_outlast_its_evidence(self) -> None:
        path = self.pack / "controls.json"
        value = read_json(path)
        value["controls"][0]["verification_valid_until"] = "2026-10-28T10:00:01Z"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("CONTROL_VERIFICATION_OUTLASTS_EVIDENCE", codes(report))

    def test_risk_acceptance_cannot_outlast_its_control(self) -> None:
        path = self.pack / "risk-register.json"
        value = read_json(path)
        value["risks"][0]["acceptance"]["expires_at"] = "2026-10-28T10:00:01Z"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("RISK_ACCEPTANCE_OUTLASTS_CONTROL", codes(report))

    def test_risk_and_control_links_must_be_reciprocal(self) -> None:
        path = self.pack / "controls.json"
        value = read_json(path)
        value["controls"][0]["risk_ids"] = ["RISK-UNSUPPORTED"]
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("RISK_CONTROL_LINK_NOT_RECIPROCAL", codes(report))
        self.assertIn("CONTROL_RISK_LINK_NOT_RECIPROCAL", codes(report))

    def test_approval_must_bind_exact_decision_inputs(self) -> None:
        path = self.pack / "system-manifest.json"
        value = read_json(path)
        value["name"] = "Changed after human approval"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("APPROVAL_INPUT_HASH_MISMATCH", codes(report))

    def test_rollback_target_must_match_manifest(self) -> None:
        path = self.pack / "approval-decision.json"
        value = read_json(path)
        value["rollback_target"] = "different-target"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("ROLLBACK_TARGET_MISMATCH", codes(report))

    def test_residual_risk_cannot_exceed_organizational_tolerance(self) -> None:
        path = self.pack / "risk-register.json"
        value = read_json(path)
        risk = value["risks"][0]
        risk["residual_risk_level"] = "critical"
        risk["acceptance"]["actor_id"] = "ACT-GOVERNANCE"
        risk["acceptance"]["role"] = "executive_risk_authority"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("RISK_OUTSIDE_TOLERANCE", codes(report))

    def test_not_applicable_risk_requires_authorized_disposition(self) -> None:
        path = self.pack / "risk-register.json"
        value = read_json(path)
        risk = value["risks"][0]
        risk["status"] = "not_applicable"
        risk["treatment"] = "not_applicable"
        risk["control_ids"] = []
        risk.pop("acceptance")
        risk["not_applicable_approval"] = {
            "actor_id": "ACT-SYSTEM",
            "role": "system_owner",
            "decided_at": "2026-07-31T10:30:00Z",
            "rationale": "An intentionally unauthorized fictional disposition for the regression test."
        }
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("RISK_NOT_APPLICABLE_UNAUTHORIZED", codes(report))

    def test_not_applicable_risk_respects_inherent_risk_authority(self) -> None:
        path = self.pack / "risk-register.json"
        value = read_json(path)
        risk = value["risks"][0]
        risk["status"] = "not_applicable"
        risk["treatment"] = "not_applicable"
        risk["control_ids"] = []
        risk.pop("acceptance")
        risk["not_applicable_approval"] = {
            "actor_id": "ACT-SYSTEM", "role": "risk_manager",
            "decided_at": "2026-07-31T10:30:00Z",
            "rationale": "A risk manager cannot exclude this fictional critical inherent risk."
        }
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("RISK_NOT_APPLICABLE_EXCEEDS_AUTHORITY", codes(report))

    def test_treated_risk_requires_recorded_acceptance(self) -> None:
        path = self.pack / "risk-register.json"
        value = read_json(path)
        value["risks"][0].pop("acceptance")
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("SCHEMA_INVALID", codes(report))

    def test_false_positive_requires_disposition_evidence(self) -> None:
        path = self.pack / "findings.json"
        value = read_json(path)
        finding = value["findings"][0]
        finding["status"] = "false_positive"
        finding.pop("retest_evidence_id")
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("SCHEMA_INVALID", codes(report))

    def test_duplicate_risk_authority_role_is_rejected(self) -> None:
        governance = read_json(self.governance)
        governance["risk_acceptance_authority"].append(dict(governance["risk_acceptance_authority"][0]))
        write_json(self.governance, governance)
        pack_path = self.pack / "pack.json"
        pack = read_json(pack_path)
        pack["policy_bindings"][0]["sha256"] = hashlib.sha256(self.governance.read_bytes()).hexdigest()
        write_json(pack_path, pack)
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["input_hashes"]["pack"] = hashlib.sha256(pack_path.read_bytes()).hexdigest()
        write_json(approval_path, approval)
        report = self.evaluate()
        self.assertIn("RISK_AUTHORITY_DUPLICATE", codes(report))

    def test_artifact_size_limit_is_enforced(self) -> None:
        governance = read_json(self.governance)
        governance["resource_limits"]["maximum_artifact_bytes"] = 1024
        write_json(self.governance, governance)
        pack_path = self.pack / "pack.json"
        pack = read_json(pack_path)
        pack["policy_bindings"][0]["sha256"] = hashlib.sha256(self.governance.read_bytes()).hexdigest()
        write_json(pack_path, pack)
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["input_hashes"]["pack"] = hashlib.sha256(pack_path.read_bytes()).hexdigest()
        write_json(approval_path, approval)
        report = self.evaluate()
        self.assertIn("ARTIFACT_TOO_LARGE", codes(report))

    def test_production_rejects_historical_as_of_override(self) -> None:
        path = self.pack / "pack.json"
        value = read_json(path)
        value["mode"] = "production"
        write_json(path, value)
        report = self.evaluate(allow_fictional=False)
        self.assertIn("PRODUCTION_AS_OF_OVERRIDE", codes(report))

    def test_real_engine_positive_production_path_authorizes_deployment(self) -> None:
        tailoring_path = self.base / "tailoring.production-test.json"
        tailoring = read_json(self.tailoring)
        tailoring["status"] = "approved"
        write_json(tailoring_path, tailoring)
        change_policy_path = self.base / "change-policy.production-test.json"
        change_policy = read_json(self.change_policy)
        change_policy["status"] = "approved"
        write_json(change_policy_path, change_policy)

        pack_path = self.pack / "pack.json"
        pack = read_json(pack_path)
        pack["mode"] = "production"
        policy_paths = {
            "governance": self.governance,
            "tailoring": tailoring_path,
            "change_triggers": change_policy_path,
        }
        for binding in pack["policy_bindings"]:
            binding["sha256"] = hashlib.sha256(policy_paths[binding["policy_type"]].read_bytes()).hexdigest()
        write_json(pack_path, pack)
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["input_hashes"]["pack"] = hashlib.sha256(pack_path.read_bytes()).hexdigest()
        write_json(approval_path, approval)

        class FixedDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                return AS_OF if tz is not None else AS_OF.replace(tzinfo=None)

        with patch("evalseal.engine.datetime", FixedDateTime):
            report = evaluate_pack(
                self.pack,
                self.governance,
                tailoring_path,
                change_policy_path,
            )
        self.assertEqual("APPROVE", report.decision)
        self.assertEqual("production", report.mode)
        self.assertTrue(report.authorizes_deployment)
        self.assertFalse(report.blocking_issues)

    def test_production_rejects_staging_manifest(self) -> None:
        manifest_path = self.pack / "system-manifest.json"
        manifest = read_json(manifest_path)
        manifest["environment"] = "staging"
        write_json(manifest_path, manifest)
        report = self.evaluate()
        self.assertIn("ENVIRONMENT_NOT_PRODUCTION_CANDIDATE", codes(report))

    def test_retrieval_versions_are_required_when_enabled(self) -> None:
        path = self.pack / "system-manifest.json"
        value = read_json(path)
        value["retrieval"]["index_version"] = None
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("SCHEMA_INVALID", codes(report))

    def test_at_least_one_evaluation_case_must_be_active(self) -> None:
        path = self.pack / "evaluation-cases.json"
        value = read_json(path)
        for case in value["cases"]:
            case["status"] = "retired"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("NO_ACTIVE_EVALUATION_CASE", codes(report))

    def test_tools_must_activate_external_action_requirements(self) -> None:
        path = self.pack / "system-manifest.json"
        value = read_json(path)
        value["tools"] = [{"name": "ticket-writer", "permission_scope": "write tickets", "high_impact": True}]
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("MANIFEST_APPLICABILITY_CONFLICT", codes(report))

    def test_model_versions_must_be_pinned(self) -> None:
        path = self.pack / "system-manifest.json"
        value = read_json(path)
        value["models"][0]["version_pinned"] = False
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("MODEL_VERSION_UNPINNED", codes(report))

    def test_approval_review_cannot_outlast_its_basis(self) -> None:
        path = self.pack / "approval-decision.json"
        value = read_json(path)
        value["next_review_at"] = "2026-09-14T12:00:00Z"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("APPROVAL_REVIEW_AFTER_BASIS_EXPIRY", codes(report))

    def test_evidence_verifier_must_hold_configured_role(self) -> None:
        path = self.pack / "evidence-index.json"
        value = read_json(path)
        value["evidence"][0]["verifier_actor_id"] = "ACT-CONTROL"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("EVIDENCE_VERIFIER_UNAUTHORIZED", codes(report))

    def test_unlinked_nonblocking_finding_is_rejected(self) -> None:
        findings_path = self.pack / "findings.json"
        findings = read_json(findings_path)
        findings["findings"].append({
            "finding_id": "FIND-DOCS-02",
            "source_evidence_id": "EVID-EVALUATION",
            "risk_id": "RISK-UNSUPPORTED",
            "title": "Minor operator wording needs clarification",
            "severity": "low",
            "blocking": False,
            "status": "open",
            "owner_actor_id": "ACT-SYSTEM",
            "remediation": "Clarify the operator-facing limitation wording before release-condition expiry."
        })
        write_json(findings_path, findings)
        approval_path = self.pack / "approval-decision.json"
        approval = read_json(approval_path)
        approval["decision"] = "approve_with_conditions"
        approval["conditions"] = [{
            "condition_id": "COND-OTHER-01",
            "description": "A condition that does not bind the open finding.",
            "owner_actor_id": "ACT-SYSTEM",
            "finding_ids": ["FIND-INJECTION-01"],
            "due_at": "2026-08-14T12:00:00Z",
            "status": "open"
        }]
        write_json(approval_path, approval)
        report = self.evaluate()
        self.assertIn("CONDITION_RECORD_MISSING", codes(report))

    def test_change_scope_below_policy_minimum_is_rejected(self) -> None:
        path = self.pack / "change-assessment.json"
        value = read_json(path)
        value["declared_scope"] = "targeted"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("CHANGE_SCOPE_TOO_NARROW", codes(report))

    def test_unknown_change_type_fails_closed(self) -> None:
        path = self.pack / "change-assessment.json"
        value = read_json(path)
        value["changes"] = [{"change_type": "mystery_change", "description": "A material change that is absent from the approved trigger policy."}]
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("CHANGE_TYPE_UNKNOWN", codes(report))

    def test_first_release_trigger_is_required_without_baseline(self) -> None:
        path = self.pack / "change-assessment.json"
        value = read_json(path)
        value["changes"] = [{"change_type": "documentation_only", "description": "Documentation update incorrectly used for a candidate without a baseline."}]
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("FIRST_RELEASE_TRIGGER_MISSING", codes(report))

    def test_policy_hash_mismatch_is_rejected(self) -> None:
        value = read_json(self.governance)
        value["organization"] = "Changed after binding"
        write_json(self.governance, value)
        report = self.evaluate()
        self.assertIn("POLICY_HASH_MISMATCH", codes(report))

    def test_production_pack_cannot_use_reference_policies(self) -> None:
        path = self.pack / "pack.json"
        value = read_json(path)
        value["mode"] = "production"
        write_json(path, value)
        report = self.evaluate(allow_fictional=False)
        self.assertIn("POLICY_NOT_APPROVED", codes(report))

    def test_tier_three_control_cannot_be_self_verified(self) -> None:
        governance = read_json(self.governance)
        for actor in governance["actors"]:
            if actor["actor_id"] == "ACT-CONTROL":
                actor["roles"].append("security_reviewer")
        write_json(self.governance, governance)
        pack_path = self.pack / "pack.json"
        pack = read_json(pack_path)
        pack["policy_bindings"][0]["sha256"] = hashlib.sha256(self.governance.read_bytes()).hexdigest()
        write_json(pack_path, pack)
        evidence_path = self.pack / "evidence-index.json"
        evidence = read_json(evidence_path)
        for item in evidence["evidence"]:
            if item["evidence_id"] == "EVID-SECURITY":
                item["verifier_actor_id"] = "ACT-CONTROL"
        write_json(evidence_path, evidence)
        report = self.evaluate()
        self.assertIn("CONTROL_SELF_VERIFIED", codes(report))

    def test_expired_policy_review_is_rejected(self) -> None:
        report = self.evaluate(as_of=datetime(2027, 2, 1, 0, 0, tzinfo=timezone.utc))
        self.assertIn("POLICY_REVIEW_DUE", codes(report))

    def test_candidate_mismatch_is_rejected(self) -> None:
        path = self.pack / "findings.json"
        value = read_json(path)
        value["candidate_id"] = "CAND-OTHER-001"
        write_json(path, value)
        report = self.evaluate()
        self.assertIn("CANDIDATE_MISMATCH", codes(report))

    def test_change_assessment_command_computes_full_scope(self) -> None:
        report = assess_change(self.pack / "change-assessment.json", self.change_policy)
        self.assertEqual("VALID", report["decision"])
        self.assertEqual("full", report["required_scope"])
        self.assertTrue(report["requires_new_approval"])
        self.assertIn("evaluation_report", report["required_evidence_types"])

    def test_change_assessment_cli_text_reports_actionable_result(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            result = cli_main([
                "assess-change",
                "--assessment", str(self.pack / "change-assessment.json"),
                "--policy", str(self.change_policy),
            ])
        rendered = output.getvalue()
        self.assertEqual(0, result)
        self.assertIn("Change assessment: VALID", rendered)
        self.assertIn("Required reassessment scope: full", rendered)
        self.assertIn("Required evidence types:", rendered)
        self.assertIn("evaluation_report", rendered)
        self.assertIn("Requires new approval: true", rendered)
        self.assertNotIn("Gate version: unknown", rendered)

    def test_change_policy_rejects_duplicate_triggers(self) -> None:
        path = self.base / "duplicate-change-policy.json"
        policy = read_json(self.change_policy)
        policy["triggers"].append(dict(policy["triggers"][0]))
        write_json(path, policy)
        report = assess_change(self.pack / "change-assessment.json", path)
        self.assertEqual("INVALID", report["decision"])
        self.assertIn("CHANGE_TRIGGER_DUPLICATE", {issue["code"] for issue in report["issues"]})

    def test_every_change_trigger_requires_fresh_approval(self) -> None:
        path = self.base / "unsafe-change-policy.json"
        policy = read_json(self.change_policy)
        policy["triggers"][0]["requires_new_approval"] = False
        write_json(path, policy)
        report = assess_change(self.pack / "change-assessment.json", path)
        self.assertEqual("INVALID", report["decision"])
        self.assertIn("SCHEMA_INVALID", {issue["code"] for issue in report["issues"]})


if __name__ == "__main__":
    unittest.main()
