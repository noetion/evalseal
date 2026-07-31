from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from importlib.metadata import version as distribution_version
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


SCHEMA_FILES = {
    "common": "common.schema.json",
    "pack": "pack.schema.json",
    "system_manifest": "system-manifest.schema.json",
    "risk_register": "risk-register.schema.json",
    "controls": "controls.schema.json",
    "evaluation_cases": "evaluation-cases.schema.json",
    "evidence_index": "evidence-index.schema.json",
    "findings": "findings.schema.json",
    "approval_decision": "approval-decision.schema.json",
    "change_assessment": "change-assessment.schema.json",
    "governance": "governance.schema.json",
    "tailoring": "tailoring.schema.json",
    "change_policy": "change-policy.schema.json",
}

GATE_VERSION = "1.0.0"
MAX_JSON_BYTES = 10 * 1024 * 1024
RISK_RANK = {"low": 1, "moderate": 2, "high": 3, "critical": 4}
SCOPE_RANK = {"documentation": 1, "targeted": 2, "full": 3, "incident": 4}


class _DuplicateJsonKey(ValueError):
    pass


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class GateReport:
    decision: str
    pack_id: str | None
    candidate_id: str | None
    tier: str | None
    as_of: str
    required_evidence_types: tuple[str, ...]
    blocking_issues: tuple[Issue, ...]
    warnings: tuple[Issue, ...]
    mode: str | None = None
    authorizes_deployment: bool = False
    gate_version: str = GATE_VERSION
    digests: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "pack_id": self.pack_id,
            "candidate_id": self.candidate_id,
            "tier": self.tier,
            "as_of": self.as_of,
            "required_evidence_types": list(self.required_evidence_types),
            "blocking_issues": [asdict(issue) for issue in self.blocking_issues],
            "warnings": [asdict(issue) for issue in self.warnings],
            "mode": self.mode,
            "authorizes_deployment": self.authorizes_deployment,
            "gate_version": self.gate_version,
            "digests": self.digests or {},
        }


def _load_json(path: Path) -> dict[str, Any]:
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise _DuplicateJsonKey(key)
            value[key] = item
        return value

    try:
        size = path.stat().st_size
        if size > MAX_JSON_BYTES:
            raise ValueError(f"JSON file exceeds the {MAX_JSON_BYTES}-byte limit: {path}")
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    except FileNotFoundError as exc:
        raise ValueError(f"required file is missing: {path}") from exc
    except _DuplicateJsonKey as exc:
        raise ValueError(f"duplicate JSON object key {exc.args[0]!r} in {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: line {exc.lineno}, column {exc.colno}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"top-level JSON value must be an object: {path}")
    return value


def _schema_bundle() -> tuple[dict[str, dict[str, Any]], Registry[Any]]:
    directory = Path(__file__).with_name("schemas")
    schemas: dict[str, dict[str, Any]] = {}
    registry: Registry[Any] = Registry()
    for key, filename in SCHEMA_FILES.items():
        schema = _load_json(directory / filename)
        Draft202012Validator.check_schema(schema)
        schemas[key] = schema
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return schemas, registry


def _validate_schema(
    value: dict[str, Any],
    schema_key: str,
    display_path: str,
    schemas: dict[str, dict[str, Any]],
    registry: Registry[Any],
) -> list[Issue]:
    validator = Draft202012Validator(
        schemas[schema_key],
        registry=registry,
        format_checker=FormatChecker(),
    )
    issues: list[Issue] = []
    for error in sorted(validator.iter_errors(value), key=lambda item: tuple(str(part) for part in item.absolute_path)):
        suffix = ".".join(str(part) for part in error.absolute_path)
        path = f"{display_path}.{suffix}" if suffix else display_path
        issues.append(Issue("SCHEMA_INVALID", path, error.message))
    return issues


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp must include a timezone: {value}")
    return parsed.astimezone(timezone.utc)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _gate_source_digest() -> str:
    directory = Path(__file__).parent
    files = sorted(directory.glob("*.py")) + sorted((directory / "schemas").glob("*.json"))
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(directory).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _safe_file(root: Path, relative: str) -> Path | None:
    candidate = (root / relative).resolve()
    root = root.resolve()
    if candidate == root or root not in candidate.parents or not candidate.is_file():
        return None
    return candidate


def _unique_by_id(items: list[dict[str, Any]], key: str, path: str) -> tuple[dict[str, dict[str, Any]], list[Issue]]:
    result: dict[str, dict[str, Any]] = {}
    issues: list[Issue] = []
    for index, item in enumerate(items):
        identifier = item.get(key)
        if identifier in result:
            issues.append(Issue("DUPLICATE_ID", f"{path}[{index}].{key}", f"duplicate identifier {identifier}"))
        elif isinstance(identifier, str):
            result[identifier] = item
    return result, issues


def _policy_binding_issues(
    pack: dict[str, Any],
    policies: dict[str, tuple[Path, dict[str, Any]]],
    allow_reference: bool,
) -> list[Issue]:
    issues: list[Issue] = []
    bindings = {item["policy_type"]: item for item in pack.get("policy_bindings", [])}
    for policy_type, (path, policy) in policies.items():
        binding = bindings.get(policy_type)
        if binding is None:
            issues.append(Issue("POLICY_BINDING_MISSING", "pack.json.policy_bindings", f"missing {policy_type} binding"))
            continue
        if binding.get("policy_id") != policy.get("policy_id") or binding.get("version") != policy.get("version"):
            issues.append(Issue("POLICY_VERSION_MISMATCH", f"pack.json.policy_bindings.{policy_type}", "policy identity or version does not match"))
        if binding.get("sha256") != _sha256(path):
            issues.append(Issue("POLICY_HASH_MISMATCH", f"pack.json.policy_bindings.{policy_type}", "policy file hash does not match the signed binding"))
        if policy.get("status") != "approved" and not allow_reference:
            issues.append(Issue("POLICY_NOT_APPROVED", str(path), "production decisions require an approved policy"))
    return issues


def _computed_tier(manifest: dict[str, Any], tailoring: dict[str, Any], issues: list[Issue]) -> str | None:
    scores: list[int] = []
    for dimension, value in manifest.get("risk_profile", {}).items():
        mapping = tailoring.get("dimensions", {}).get(dimension, {})
        score = mapping.get(value)
        if not isinstance(score, int):
            issues.append(Issue("UNMAPPED_RISK_VALUE", f"system-manifest.json.risk_profile.{dimension}", f"{value!r} is not mapped by the tailoring policy"))
        else:
            scores.append(score)
    if not scores:
        return None
    tier = tailoring.get("tier_by_score", {}).get(str(max(scores)))
    if tier is None:
        issues.append(Issue("UNMAPPED_TIER_SCORE", "tailoring.tier_by_score", f"score {max(scores)} has no tier mapping"))
    return tier


def _required_evidence(
    manifest: dict[str, Any],
    tier: str,
    tailoring: dict[str, Any],
    change_assessment: dict[str, Any],
    change_policy: dict[str, Any],
) -> tuple[set[str], set[str], int, dict[str, int]]:
    tier_policy = tailoring["tiers"][tier]
    required = set(tier_policy["required_evidence_types"])
    approval_roles = set(tier_policy["required_approval_roles"])
    for rule in tailoring.get("conditional_requirements", []):
        if manifest.get("applicability", {}).get(rule["manifest_flag"]) == rule["equals"]:
            required.update(rule["evidence_types"])
            approval_roles.update(rule["approval_roles"])
    trigger_map = {trigger["change_type"]: trigger for trigger in change_policy["triggers"]}
    required_scope = 1
    for change in change_assessment["changes"]:
        trigger = trigger_map.get(change["change_type"])
        if trigger:
            required.update(trigger["required_evidence_types"])
            required_scope = max(required_scope, SCOPE_RANK[trigger["minimum_scope"]])
    return required, approval_roles, required_scope, tier_policy.get("evidence_max_age_days", {})


def _actor_has_role(actors: dict[str, dict[str, Any]], actor_id: str, role: str) -> bool:
    actor = actors.get(actor_id, {})
    return bool(actor.get("active")) and role in actor.get("roles", [])


def _actor_is_active(actors: dict[str, dict[str, Any]], actor_id: str) -> bool:
    return bool(actors.get(actor_id, {}).get("active"))


def evaluate_pack(
    pack_dir: Path,
    governance_path: Path,
    tailoring_path: Path,
    change_policy_path: Path,
    as_of: datetime | None = None,
    allow_fictional: bool = False,
    preflight: bool = False,
) -> GateReport:
    as_of_was_overridden = as_of is not None
    if as_of is not None and as_of.tzinfo is None:
        raise ValueError("as_of must include a timezone")
    as_of = (as_of or datetime.now(timezone.utc)).astimezone(timezone.utc)
    pack_dir = pack_dir.resolve()
    schemas, registry = _schema_bundle()
    blocking: list[Issue] = []
    warnings: list[Issue] = []

    try:
        pack = _load_json(pack_dir / "pack.json")
        governance = _load_json(governance_path.resolve())
        tailoring = _load_json(tailoring_path.resolve())
        change_policy = _load_json(change_policy_path.resolve())
    except ValueError as exc:
        return GateReport("REJECT", None, None, None, as_of.isoformat(), (), (Issue("LOAD_ERROR", "input", str(exc)),), ())

    blocking.extend(_validate_schema(pack, "pack", "pack.json", schemas, registry))
    blocking.extend(_validate_schema(governance, "governance", str(governance_path), schemas, registry))
    blocking.extend(_validate_schema(tailoring, "tailoring", str(tailoring_path), schemas, registry))
    blocking.extend(_validate_schema(change_policy, "change_policy", str(change_policy_path), schemas, registry))
    if blocking:
        return GateReport("REJECT", pack.get("pack_id"), pack.get("candidate_id"), None, as_of.isoformat(), (), tuple(blocking), (), mode=pack.get("mode"))

    mode = pack["mode"]
    if mode == "template" or (mode == "fictional" and not allow_fictional):
        blocking.append(Issue("NON_PRODUCTION_PACK", "pack.json.mode", "template and fictional packs cannot authorize deployment"))
    if mode == "production" and as_of_was_overridden:
        blocking.append(Issue("PRODUCTION_AS_OF_OVERRIDE", "as_of", "production decisions must use the gate runner's current UTC time"))

    policies = {
        "governance": (governance_path.resolve(), governance),
        "tailoring": (tailoring_path.resolve(), tailoring),
        "change_triggers": (change_policy_path.resolve(), change_policy),
    }
    blocking.extend(_policy_binding_issues(pack, policies, mode == "fictional" and allow_fictional))
    try:
        if _parse_time(pack["created_at"]) > as_of:
            blocking.append(Issue("PACK_FROM_FUTURE", "pack.json.created_at", "pack creation date is after the decision time"))
        for policy_name, policy in (("governance", governance), ("tailoring", tailoring), ("change policy", change_policy)):
            approved_at = _parse_time(policy["approved_at"])
            effective_at = _parse_time(policy["effective_at"])
            next_review_at = _parse_time(policy["next_review_at"])
            if approved_at > as_of or effective_at > as_of:
                blocking.append(Issue("POLICY_NOT_YET_EFFECTIVE", policy_name, "policy approval or effective date is after the decision time"))
            if effective_at < approved_at:
                blocking.append(Issue("POLICY_TIME_INVALID", policy_name, "policy effective date cannot predate approval"))
            if next_review_at <= effective_at:
                blocking.append(Issue("POLICY_TIME_INVALID", policy_name, "policy review date must follow its effective date"))
            if next_review_at <= as_of:
                blocking.append(Issue("POLICY_REVIEW_DUE", policy_name, "policy review date has passed"))
    except ValueError as exc:
        blocking.append(Issue("TIME_INVALID", "policy or pack", str(exc)))

    documents: dict[str, dict[str, Any]] = {}
    for key, relative in pack["file_map"].items():
        path = _safe_file(pack_dir, relative)
        if path is None:
            blocking.append(Issue("PACK_FILE_MISSING", f"pack.json.file_map.{key}", f"missing or unsafe file path {relative}"))
            continue
        try:
            documents[key] = _load_json(path)
        except ValueError as exc:
            blocking.append(Issue("LOAD_ERROR", relative, str(exc)))
            continue
        blocking.extend(_validate_schema(documents[key], key, relative, schemas, registry))
    if blocking:
        return GateReport("REJECT", pack["pack_id"], pack["candidate_id"], None, as_of.isoformat(), (), tuple(blocking), tuple(warnings), mode=mode)

    candidate_id = pack["candidate_id"]
    if pack["artifact_status"] != "final":
        blocking.append(Issue("PACK_NOT_FINAL", "pack.json.artifact_status", "release gate requires a final evidence pack"))
    for key, document in documents.items():
        if document.get("candidate_id") != candidate_id:
            blocking.append(Issue("CANDIDATE_MISMATCH", pack["file_map"][key], "document does not describe the pack candidate"))
        if document.get("artifact_status") != "final" and not (preflight and key == "approval_decision"):
            blocking.append(Issue("ARTIFACT_NOT_FINAL", f"{pack['file_map'][key]}.artifact_status", "release gate requires final artifacts"))

    manifest = documents["system_manifest"]
    risk_register = documents["risk_register"]
    controls_document = documents["controls"]
    evidence_document = documents["evidence_index"]
    findings_document = documents["findings"]
    approval = documents["approval_decision"]
    change_assessment = documents["change_assessment"]
    maximum_artifact_bytes = governance["resource_limits"]["maximum_artifact_bytes"]
    if mode != "template" and manifest["environment"] != "production_candidate":
        blocking.append(Issue("ENVIRONMENT_NOT_PRODUCTION_CANDIDATE", "system-manifest.json.environment", "a production release decision requires a production_candidate manifest"))
    if mode != "template":
        for index, model in enumerate(manifest["models"]):
            if not model["version_pinned"]:
                blocking.append(Issue("MODEL_VERSION_UNPINNED", f"system-manifest.json.models[{index}].version_pinned", "release candidates require pinned model versions"))
    if manifest["tools"] and not manifest["applicability"]["has_external_actions"]:
        blocking.append(Issue("MANIFEST_APPLICABILITY_CONFLICT", "system-manifest.json.applicability.has_external_actions", "a manifest with tools must declare external actions"))
    for label, path_key, hash_key in (
        ("prompt bundle", "prompt_bundle_path", "prompt_bundle_sha256"),
        ("runtime configuration", "configuration_path", "configuration_sha256"),
    ):
        bound_file = _safe_file(pack_dir, manifest[path_key])
        if bound_file is None:
            blocking.append(Issue("MANIFEST_FILE_MISSING", f"system-manifest.json.{path_key}", f"{label} is missing or outside the evidence pack"))
        elif bound_file.stat().st_size > maximum_artifact_bytes:
            blocking.append(Issue("ARTIFACT_TOO_LARGE", f"system-manifest.json.{path_key}", f"{label} exceeds the configured artifact-size limit"))
        elif _sha256(bound_file) != manifest[hash_key]:
            blocking.append(Issue("MANIFEST_HASH_MISMATCH", f"system-manifest.json.{hash_key}", f"{label} hash does not match"))

    trigger_types = {trigger["change_type"] for trigger in change_policy["triggers"]}
    if len(trigger_types) != len(change_policy["triggers"]):
        blocking.append(Issue("CHANGE_TRIGGER_DUPLICATE", "change policy.triggers", "change policy contains duplicate change types"))
    declared_change_types = {change["change_type"] for change in change_assessment["changes"]}
    for change_type in declared_change_types - trigger_types:
        blocking.append(Issue("CHANGE_TYPE_UNKNOWN", "change-assessment.json.changes", f"no policy trigger exists for {change_type}"))
    if change_assessment["baseline_candidate_id"] is None and "first_release" not in declared_change_types:
        blocking.append(Issue("FIRST_RELEASE_TRIGGER_MISSING", "change-assessment.json.changes", "a candidate without an approved baseline must declare first_release"))
    if change_assessment["baseline_candidate_id"] is not None and "first_release" in declared_change_types:
        blocking.append(Issue("FIRST_RELEASE_TRIGGER_INVALID", "change-assessment.json.changes", "first_release cannot be used when a baseline candidate is recorded"))
    if _parse_time(change_assessment["assessed_at"]) > as_of:
        blocking.append(Issue("CHANGE_ASSESSMENT_FROM_FUTURE", "change-assessment.json.assessed_at", "change assessment date is after the decision time"))

    tier = _computed_tier(manifest, tailoring, blocking)
    if tier and manifest["declared_tier"] != tier:
        blocking.append(Issue("TIER_MISMATCH", "system-manifest.json.declared_tier", f"declared {manifest['declared_tier']} but policy computes {tier}"))
    if tier not in tailoring["tiers"]:
        blocking.append(Issue("TIER_POLICY_MISSING", "tailoring.tiers", f"no policy exists for {tier}"))
        return GateReport("REJECT", pack["pack_id"], candidate_id, tier, as_of.isoformat(), (), tuple(blocking), tuple(warnings), mode=mode)

    required_evidence, required_roles, required_scope_rank, max_age = _required_evidence(
        manifest, tier, tailoring, change_assessment, change_policy
    )
    if SCOPE_RANK[change_assessment["declared_scope"]] < required_scope_rank:
        blocking.append(Issue("CHANGE_SCOPE_TOO_NARROW", "change-assessment.json.declared_scope", "declared reassessment scope is below the change-policy minimum"))

    actors, actor_issues = _unique_by_id(governance["actors"], "actor_id", "governance.actors")
    blocking.extend(actor_issues)
    authority_roles = [item["role"] for item in governance["risk_acceptance_authority"]]
    if len(set(authority_roles)) != len(authority_roles):
        blocking.append(Issue("RISK_AUTHORITY_DUPLICATE", "governance.risk_acceptance_authority", "risk-acceptance authority contains duplicate roles"))
    governance_approver = governance["approved_by_actor_id"]
    if not _actor_has_role(actors, governance_approver, "governance_authority"):
        blocking.append(Issue("GOVERNANCE_APPROVER_UNAUTHORIZED", str(governance_path), "governance policy approver must hold governance_authority"))
    for policy_name, policy in (("tailoring", tailoring), ("change policy", change_policy)):
        if not _actor_has_role(actors, policy["approved_by_actor_id"], "governance_authority"):
            blocking.append(Issue("POLICY_APPROVER_UNAUTHORIZED", policy_name, "policy approver must hold governance_authority in the bound governance policy"))
    if not _actor_is_active(actors, pack["owner_actor_id"]):
        blocking.append(Issue("PACK_OWNER_UNKNOWN", "pack.json.owner_actor_id", "pack owner is not in the governance policy"))
    if not _actor_is_active(actors, change_assessment["assessed_by_actor_id"]):
        blocking.append(Issue("CHANGE_ASSESSOR_UNKNOWN", "change-assessment.json.assessed_by_actor_id", "change assessor is not in the governance policy"))
    for actor_id, actor in actors.items():
        if not actor["active"]:
            warnings.append(Issue("INACTIVE_ACTOR", f"governance.actors.{actor_id}", "inactive actor cannot exercise authority"))
    risks, risk_issues = _unique_by_id(risk_register["risks"], "risk_id", "risk-register.json.risks")
    controls, control_issues = _unique_by_id(controls_document["controls"], "control_id", "controls.json.controls")
    evidence, evidence_issues = _unique_by_id(evidence_document["evidence"], "evidence_id", "evidence-index.json.evidence")
    findings, finding_issues = _unique_by_id(findings_document["findings"], "finding_id", "findings.json.findings")
    blocking.extend(risk_issues + control_issues + evidence_issues + finding_issues)
    cases, case_issues = _unique_by_id(documents["evaluation_cases"]["cases"], "case_id", "evaluation-cases.json.cases")
    blocking.extend(case_issues)
    if not any(case["status"] == "active" for case in cases.values()):
        blocking.append(Issue("NO_ACTIVE_EVALUATION_CASE", "evaluation-cases.json.cases", "at least one evaluation case must be active"))
    dataset_path = _safe_file(pack_dir, documents["evaluation_cases"]["dataset_path"])
    if dataset_path is None:
        blocking.append(Issue("EVALUATION_DATASET_MISSING", "evaluation-cases.json.dataset_path", "evaluation dataset is missing or outside the evidence pack"))
    elif dataset_path.stat().st_size > maximum_artifact_bytes:
        blocking.append(Issue("ARTIFACT_TOO_LARGE", "evaluation-cases.json.dataset_path", "evaluation dataset exceeds the configured artifact-size limit"))
    elif _sha256(dataset_path) != documents["evaluation_cases"]["dataset_sha256"]:
        blocking.append(Issue("EVALUATION_DATASET_HASH_MISMATCH", "evaluation-cases.json.dataset_sha256", "evaluation dataset hash does not match"))
    for case_id, case in cases.items():
        for risk_id in case["risk_ids"]:
            if risk_id not in risks:
                blocking.append(Issue("CASE_RISK_UNKNOWN", f"evaluation-cases.json.{case_id}.risk_ids", f"unknown risk {risk_id}"))

    evidence_by_type: dict[str, list[dict[str, Any]]] = {}
    verifier_roles = governance["evidence_verifier_roles"]
    for evidence_id, item in evidence.items():
        evidence_by_type.setdefault(item["evidence_type"], []).append(item)
        if item["candidate_id"] != candidate_id:
            blocking.append(Issue("EVIDENCE_CANDIDATE_MISMATCH", f"evidence-index.json.{evidence_id}", "evidence belongs to another candidate"))
        if not _actor_is_active(actors, item["owner_actor_id"]) or not _actor_is_active(actors, item["verifier_actor_id"]):
            blocking.append(Issue("EVIDENCE_ACTOR_UNKNOWN", f"evidence-index.json.{evidence_id}", "evidence owner or verifier is not in the governance policy"))
        else:
            allowed_roles = set(verifier_roles.get(item["evidence_type"], []))
            actual_roles = set(actors[item["verifier_actor_id"]]["roles"])
            if not allowed_roles:
                blocking.append(Issue("EVIDENCE_VERIFIER_POLICY_MISSING", f"governance.evidence_verifier_roles.{item['evidence_type']}", "no verifier-role policy exists for this evidence type"))
            elif not allowed_roles & actual_roles:
                blocking.append(Issue("EVIDENCE_VERIFIER_UNAUTHORIZED", f"evidence-index.json.{evidence_id}.verifier_actor_id", "verifier does not hold an allowed role for this evidence type"))
            if tier in {"tier_3", "tier_4"} and item["owner_actor_id"] == item["verifier_actor_id"]:
                blocking.append(Issue("EVIDENCE_SELF_VERIFIED", f"evidence-index.json.{evidence_id}.verifier_actor_id", "tier 3 and 4 evidence requires a verifier other than its owner"))
        artifact = _safe_file(pack_dir, item["path"])
        if artifact is None:
            blocking.append(Issue("EVIDENCE_FILE_MISSING", f"evidence-index.json.{evidence_id}.path", "artifact is missing or outside the evidence pack"))
        elif artifact.stat().st_size > maximum_artifact_bytes:
            blocking.append(Issue("ARTIFACT_TOO_LARGE", f"evidence-index.json.{evidence_id}.path", "evidence artifact exceeds the configured artifact-size limit"))
        elif _sha256(artifact) != item["sha256"]:
            blocking.append(Issue("EVIDENCE_HASH_MISMATCH", f"evidence-index.json.{evidence_id}.sha256", "artifact hash does not match"))
        try:
            produced = _parse_time(item["produced_at"])
            expires = _parse_time(item["valid_until"])
            if produced > as_of:
                blocking.append(Issue("EVIDENCE_FROM_FUTURE", f"evidence-index.json.{evidence_id}.produced_at", "evidence date is after the decision time"))
            if expires <= produced:
                blocking.append(Issue("EVIDENCE_TIME_INVALID", f"evidence-index.json.{evidence_id}.valid_until", "evidence expiry must follow production"))
            if expires <= as_of:
                blocking.append(Issue("EVIDENCE_EXPIRED", f"evidence-index.json.{evidence_id}.valid_until", "evidence has expired"))
        except ValueError as exc:
            blocking.append(Issue("TIME_INVALID", f"evidence-index.json.{evidence_id}", str(exc)))

    selected_required_evidence: list[dict[str, Any]] = []
    for evidence_type in sorted(required_evidence):
        records = evidence_by_type.get(evidence_type, [])
        if not records:
            blocking.append(Issue("REQUIRED_EVIDENCE_MISSING", "evidence-index.json", f"no {evidence_type} evidence"))
            continue
        newest_time = max(_parse_time(item["produced_at"]) for item in records)
        newest_records = [item for item in records if _parse_time(item["produced_at"]) == newest_time]
        if any(item["status"] != "pass" for item in newest_records):
            blocking.append(Issue("LATEST_REQUIRED_EVIDENCE_FAILED", "evidence-index.json", f"the newest {evidence_type} evidence is not passing"))
            continue
        for newest in newest_records:
            selected_required_evidence.append(newest)

    authority_by_role = {item["role"]: item["max_risk_level"] for item in governance["risk_acceptance_authority"]}
    risk_tolerance = governance["risk_tolerance"]
    exception_rules = governance["exception_rules"]
    for control_id, control in controls.items():
        if not _actor_is_active(actors, control["owner_actor_id"]):
            blocking.append(Issue("CONTROL_OWNER_UNKNOWN", f"controls.json.{control_id}.owner_actor_id", "control owner is not in the governance policy"))
        for risk_id in control["risk_ids"]:
            if risk_id not in risks:
                blocking.append(Issue("CONTROL_RISK_UNKNOWN", f"controls.json.{control_id}.risk_ids", f"unknown risk {risk_id}"))
            elif control_id not in risks[risk_id]["control_ids"]:
                blocking.append(Issue("CONTROL_RISK_LINK_NOT_RECIPROCAL", f"controls.json.{control_id}.risk_ids", f"risk {risk_id} does not link back to control {control_id}"))
        for evidence_id in control.get("verification_evidence_ids", []):
            if evidence_id not in evidence:
                blocking.append(Issue("CONTROL_EVIDENCE_UNKNOWN", f"controls.json.{control_id}.verification_evidence_ids", f"unknown evidence {evidence_id}"))
            elif evidence[evidence_id]["status"] != "pass":
                blocking.append(Issue("CONTROL_EVIDENCE_FAILED", f"controls.json.{control_id}.verification_evidence_ids", f"evidence {evidence_id} is not passing"))
            elif tier in {"tier_3", "tier_4"} and evidence[evidence_id]["verifier_actor_id"] == control["owner_actor_id"]:
                blocking.append(Issue("CONTROL_SELF_VERIFIED", f"controls.json.{control_id}.verification_evidence_ids", "tier 3 and 4 controls require a verifier other than the control owner"))
        if control["status"] == "Verified":
            try:
                verified_at = _parse_time(control["verified_at"])
                valid_until = _parse_time(control["verification_valid_until"])
                if verified_at > as_of:
                    blocking.append(Issue("CONTROL_VERIFICATION_FROM_FUTURE", f"controls.json.{control_id}.verified_at", "verification date is after the decision time"))
                if valid_until <= verified_at:
                    blocking.append(Issue("CONTROL_VERIFICATION_TIME_INVALID", f"controls.json.{control_id}.verification_valid_until", "control verification expiry must follow verification"))
                if valid_until <= as_of:
                    blocking.append(Issue("CONTROL_VERIFICATION_EXPIRED", f"controls.json.{control_id}.verification_valid_until", "control verification has expired"))
                for evidence_id in control["verification_evidence_ids"]:
                    if evidence_id in evidence and _parse_time(evidence[evidence_id]["produced_at"]) > verified_at:
                        blocking.append(Issue("CONTROL_VERIFICATION_PREDATES_EVIDENCE", f"controls.json.{control_id}.verified_at", f"control verification predates evidence {evidence_id}"))
                    if evidence_id in evidence:
                        item = evidence[evidence_id]
                        age_limit = max_age.get(item["evidence_type"], tailoring["default_evidence_max_age_days"])
                        evidence_cutoff = min(
                            _parse_time(item["valid_until"]),
                            _parse_time(item["produced_at"]) + timedelta(days=age_limit),
                        )
                        if valid_until > evidence_cutoff:
                            blocking.append(Issue("CONTROL_VERIFICATION_OUTLASTS_EVIDENCE", f"controls.json.{control_id}.verification_valid_until", f"control verification outlasts evidence {evidence_id}"))
            except ValueError as exc:
                blocking.append(Issue("TIME_INVALID", f"controls.json.{control_id}", str(exc)))
        if control["status"] == "Not applicable":
            disposition = control["not_applicable_approval"]
            role = disposition["role"]
            actor_id = disposition["actor_id"]
            if role not in exception_rules["not_applicable_approval_roles"] or not _actor_has_role(actors, actor_id, role):
                blocking.append(Issue("CONTROL_NOT_APPLICABLE_UNAUTHORIZED", f"controls.json.{control_id}.not_applicable_approval", "not-applicable control disposition lacks an authorized approver"))
            if _parse_time(disposition["decided_at"]) > as_of:
                blocking.append(Issue("CONTROL_NOT_APPLICABLE_FROM_FUTURE", f"controls.json.{control_id}.not_applicable_approval.decided_at", "not-applicable disposition is after the gate time"))

    for risk_id, risk in risks.items():
        if not _actor_is_active(actors, risk["owner_actor_id"]):
            blocking.append(Issue("RISK_OWNER_UNKNOWN", f"risk-register.json.{risk_id}.owner_actor_id", "owner is not in governance policy"))
        if risk["status"] == "open":
            blocking.append(Issue("RISK_UNRESOLVED", f"risk-register.json.{risk_id}.status", "material risk has no completed treatment or acceptance"))
        if risk["status"] == "treated":
            if risk["treatment"] == "accept":
                blocking.append(Issue("RISK_TREATMENT_INCONSISTENT", f"risk-register.json.{risk_id}.treatment", "treated risk cannot use the accept treatment"))
            if not risk["control_ids"]:
                blocking.append(Issue("RISK_CONTROL_MISSING", f"risk-register.json.{risk_id}.control_ids", "treated risk has no control"))
            for control_id in risk["control_ids"]:
                control = controls.get(control_id)
                if control is None:
                    blocking.append(Issue("RISK_CONTROL_UNKNOWN", f"risk-register.json.{risk_id}.control_ids", f"unknown control {control_id}"))
                elif risk_id not in control["risk_ids"]:
                    blocking.append(Issue("RISK_CONTROL_LINK_NOT_RECIPROCAL", f"risk-register.json.{risk_id}.control_ids", f"control {control_id} does not link back to risk {risk_id}"))
                elif control["status"] != "Verified":
                    blocking.append(Issue("CONTROL_NOT_VERIFIED", f"controls.json.{control_id}.status", "a treated risk relies on a control that is not Verified"))
        if risk["status"] == "accepted":
            if risk["treatment"] != "accept":
                blocking.append(Issue("RISK_TREATMENT_INCONSISTENT", f"risk-register.json.{risk_id}.treatment", "accepted risk must use the accept treatment"))
        if risk["status"] in {"treated", "accepted"}:
            acceptance = risk["acceptance"]
            actor_id = acceptance["actor_id"]
            role = acceptance["role"]
            if not _actor_has_role(actors, actor_id, role):
                blocking.append(Issue("RISK_ACCEPTOR_UNAUTHORIZED", f"risk-register.json.{risk_id}.acceptance", "actor does not hold the stated role"))
            maximum = authority_by_role.get(role)
            if maximum is None or RISK_RANK[risk["residual_risk_level"]] > RISK_RANK[maximum]:
                blocking.append(Issue("RISK_ACCEPTANCE_EXCEEDS_AUTHORITY", f"risk-register.json.{risk_id}.acceptance", "role cannot accept this residual-risk level"))
            if RISK_RANK[risk["residual_risk_level"]] > RISK_RANK[risk_tolerance["maximum_accepted_residual_risk"]]:
                blocking.append(Issue("RISK_OUTSIDE_TOLERANCE", f"risk-register.json.{risk_id}.residual_risk_level", "accepted residual risk exceeds organizational tolerance"))
            accepted_at = _parse_time(acceptance["accepted_at"])
            expires_at = _parse_time(acceptance["expires_at"])
            if expires_at <= as_of:
                blocking.append(Issue("RISK_ACCEPTANCE_EXPIRED", f"risk-register.json.{risk_id}.acceptance.expires_at", "risk acceptance has expired"))
            if accepted_at > as_of:
                blocking.append(Issue("RISK_ACCEPTANCE_FROM_FUTURE", f"risk-register.json.{risk_id}.acceptance.accepted_at", "risk acceptance date is after the decision time"))
            if expires_at <= accepted_at:
                blocking.append(Issue("RISK_ACCEPTANCE_TIME_INVALID", f"risk-register.json.{risk_id}.acceptance", "risk acceptance expiry must follow acceptance"))
            elif expires_at - accepted_at > timedelta(days=exception_rules["maximum_acceptance_days"]):
                blocking.append(Issue("RISK_ACCEPTANCE_TOO_LONG", f"risk-register.json.{risk_id}.acceptance", "risk acceptance exceeds the configured maximum duration"))
            if risk["status"] == "treated":
                latest_control_verification = max((_parse_time(controls[control_id]["verified_at"]) for control_id in risk["control_ids"] if control_id in controls and controls[control_id]["status"] == "Verified"), default=None)
                if latest_control_verification and accepted_at < latest_control_verification:
                    blocking.append(Issue("RISK_ACCEPTANCE_PREDATES_CONTROL", f"risk-register.json.{risk_id}.acceptance.accepted_at", "residual risk was accepted before its controls were verified"))
                control_expiries = [_parse_time(controls[control_id]["verification_valid_until"]) for control_id in risk["control_ids"] if control_id in controls and controls[control_id]["status"] == "Verified"]
                if control_expiries and expires_at > min(control_expiries):
                    blocking.append(Issue("RISK_ACCEPTANCE_OUTLASTS_CONTROL", f"risk-register.json.{risk_id}.acceptance.expires_at", "residual-risk acceptance outlasts a relied-on control verification"))
        if risk["status"] == "not_applicable":
            if risk["treatment"] != "not_applicable":
                blocking.append(Issue("RISK_TREATMENT_INCONSISTENT", f"risk-register.json.{risk_id}.treatment", "not-applicable risk must use the not_applicable treatment"))
            disposition = risk["not_applicable_approval"]
            role = disposition["role"]
            actor_id = disposition["actor_id"]
            if role not in exception_rules["not_applicable_approval_roles"] or not _actor_has_role(actors, actor_id, role):
                blocking.append(Issue("RISK_NOT_APPLICABLE_UNAUTHORIZED", f"risk-register.json.{risk_id}.not_applicable_approval", "not-applicable risk disposition lacks an authorized approver"))
            maximum = authority_by_role.get(role)
            if maximum is None or RISK_RANK[risk["inherent_risk_level"]] > RISK_RANK[maximum]:
                blocking.append(Issue("RISK_NOT_APPLICABLE_EXCEEDS_AUTHORITY", f"risk-register.json.{risk_id}.not_applicable_approval", "approver cannot disposition this inherent-risk level as not applicable"))
            if _parse_time(disposition["decided_at"]) > as_of:
                blocking.append(Issue("RISK_NOT_APPLICABLE_FROM_FUTURE", f"risk-register.json.{risk_id}.not_applicable_approval.decided_at", "not-applicable disposition is after the gate time"))

    conditional = False
    unresolved_nonblocking_findings: set[str] = set()
    finding_source_ids = {finding["source_evidence_id"] for finding in findings.values()}
    for evidence_id, item in evidence.items():
        if item["status"] == "fail" and evidence_id not in finding_source_ids:
            blocking.append(Issue("FAILED_EVIDENCE_WITHOUT_FINDING", f"evidence-index.json.{evidence_id}", "failed evidence must have a tracked finding"))
    for finding_id, finding in findings.items():
        if finding["source_evidence_id"] not in evidence:
            blocking.append(Issue("FINDING_EVIDENCE_UNKNOWN", f"findings.json.{finding_id}.source_evidence_id", "finding references unknown evidence"))
        if finding["risk_id"] not in risks:
            blocking.append(Issue("FINDING_RISK_UNKNOWN", f"findings.json.{finding_id}.risk_id", "finding references unknown risk"))
        unresolved = finding["status"] not in {"verified_fixed", "false_positive"}
        if finding["blocking"] and unresolved:
            blocking.append(Issue("BLOCKING_FINDING_OPEN", f"findings.json.{finding_id}.status", "blocking finding is not verified fixed or false positive"))
        elif unresolved:
            conditional = True
            unresolved_nonblocking_findings.add(finding_id)
            warnings.append(Issue("NON_BLOCKING_FINDING_OPEN", f"findings.json.{finding_id}.status", "non-blocking finding requires a release condition"))
            if RISK_RANK[finding["severity"]] > RISK_RANK[risk_tolerance["maximum_conditional_finding_severity"]]:
                blocking.append(Issue("FINDING_OUTSIDE_CONDITIONAL_TOLERANCE", f"findings.json.{finding_id}.severity", "finding severity exceeds organizational tolerance for conditional release"))
        if not _actor_is_active(actors, finding["owner_actor_id"]):
            blocking.append(Issue("FINDING_OWNER_UNKNOWN", f"findings.json.{finding_id}.owner_actor_id", "finding owner is not in the governance policy"))
        if finding["status"] == "verified_fixed":
            retest_id = finding.get("retest_evidence_id")
            retest = evidence.get(retest_id)
            if retest is None:
                blocking.append(Issue("FINDING_RETEST_MISSING", f"findings.json.{finding_id}.retest_evidence_id", "verified fix lacks retest evidence"))
            elif retest["status"] != "pass":
                blocking.append(Issue("FINDING_RETEST_FAILED", f"findings.json.{finding_id}.retest_evidence_id", "verified fix requires passing retest evidence"))
            elif retest_id == finding["source_evidence_id"]:
                blocking.append(Issue("FINDING_RETEST_NOT_DISTINCT", f"findings.json.{finding_id}.retest_evidence_id", "retest evidence must be distinct from the source evidence"))
            elif finding["source_evidence_id"] in evidence and _parse_time(retest["produced_at"]) < _parse_time(evidence[finding["source_evidence_id"]]["produced_at"]):
                blocking.append(Issue("FINDING_RETEST_PREDATES_SOURCE", f"findings.json.{finding_id}.retest_evidence_id", "retest evidence predates the source evidence"))
        if finding["status"] == "risk_accepted":
            acceptance = finding["acceptance"]
            role = acceptance["role"]
            actor_id = acceptance["actor_id"]
            if not _actor_has_role(actors, actor_id, role):
                blocking.append(Issue("FINDING_ACCEPTOR_UNAUTHORIZED", f"findings.json.{finding_id}.acceptance", "actor does not hold the stated role"))
            maximum = authority_by_role.get(role)
            if maximum is None or RISK_RANK[finding["severity"]] > RISK_RANK[maximum]:
                blocking.append(Issue("FINDING_ACCEPTANCE_EXCEEDS_AUTHORITY", f"findings.json.{finding_id}.acceptance", "role cannot accept this finding severity"))
            accepted_at = _parse_time(acceptance["accepted_at"])
            expires_at = _parse_time(acceptance["expires_at"])
            if expires_at <= as_of:
                blocking.append(Issue("FINDING_ACCEPTANCE_EXPIRED", f"findings.json.{finding_id}.acceptance.expires_at", "finding acceptance has expired"))
            if accepted_at > as_of:
                blocking.append(Issue("FINDING_ACCEPTANCE_FROM_FUTURE", f"findings.json.{finding_id}.acceptance.accepted_at", "finding acceptance date is after the decision time"))
            source = evidence.get(finding["source_evidence_id"])
            if source is not None and accepted_at < _parse_time(source["produced_at"]):
                blocking.append(Issue("FINDING_ACCEPTANCE_PREDATES_EVIDENCE", f"findings.json.{finding_id}.acceptance.accepted_at", "finding acceptance predates its source evidence"))
            if expires_at <= accepted_at:
                blocking.append(Issue("FINDING_ACCEPTANCE_TIME_INVALID", f"findings.json.{finding_id}.acceptance", "finding acceptance expiry must follow acceptance"))
            elif expires_at - accepted_at > timedelta(days=exception_rules["maximum_acceptance_days"]):
                blocking.append(Issue("FINDING_ACCEPTANCE_TOO_LONG", f"findings.json.{finding_id}.acceptance", "finding acceptance exceeds the configured maximum duration"))
        if finding["status"] == "false_positive":
            disposition = finding["false_positive_disposition"]
            role = disposition["role"]
            actor_id = disposition["actor_id"]
            if role not in exception_rules["false_positive_approval_roles"] or not _actor_has_role(actors, actor_id, role):
                blocking.append(Issue("FALSE_POSITIVE_UNAUTHORIZED", f"findings.json.{finding_id}.false_positive_disposition", "false-positive disposition lacks an authorized reviewer"))
            if tier in {"tier_3", "tier_4"} and actor_id == finding["owner_actor_id"]:
                blocking.append(Issue("FALSE_POSITIVE_SELF_APPROVED", f"findings.json.{finding_id}.false_positive_disposition", "tier 3 and 4 false-positive dispositions require an independent actor"))
            decided_at = _parse_time(disposition["decided_at"])
            if decided_at > as_of:
                blocking.append(Issue("FALSE_POSITIVE_FROM_FUTURE", f"findings.json.{finding_id}.false_positive_disposition.decided_at", "false-positive disposition is after the gate time"))
            source = evidence.get(finding["source_evidence_id"])
            if source is not None and decided_at < _parse_time(source["produced_at"]):
                blocking.append(Issue("FALSE_POSITIVE_PREDATES_EVIDENCE", f"findings.json.{finding_id}.false_positive_disposition.decided_at", "false-positive disposition predates its source evidence"))
            for evidence_id in disposition["evidence_ids"]:
                if evidence_id not in evidence:
                    blocking.append(Issue("FALSE_POSITIVE_EVIDENCE_UNKNOWN", f"findings.json.{finding_id}.false_positive_disposition.evidence_ids", f"unknown disposition evidence {evidence_id}"))
                elif evidence[evidence_id]["status"] != "pass":
                    blocking.append(Issue("FALSE_POSITIVE_EVIDENCE_FAILED", f"findings.json.{finding_id}.false_positive_disposition.evidence_ids", f"disposition evidence {evidence_id} is not passing"))
                elif decided_at < _parse_time(evidence[evidence_id]["produced_at"]):
                    blocking.append(Issue("FALSE_POSITIVE_PREDATES_DISPOSITION_EVIDENCE", f"findings.json.{finding_id}.false_positive_disposition.decided_at", f"false-positive disposition predates evidence {evidence_id}"))

    decision_basis_evidence_ids = {item["evidence_id"] for item in selected_required_evidence}
    relied_control_ids = {
        control_id
        for risk in risks.values()
        if risk["status"] == "treated"
        for control_id in risk["control_ids"]
        if control_id in controls and controls[control_id]["status"] == "Verified"
    }
    for control_id in relied_control_ids:
        decision_basis_evidence_ids.update(controls[control_id]["verification_evidence_ids"])
    for finding in findings.values():
        if finding["status"] == "verified_fixed":
            decision_basis_evidence_ids.add(finding["retest_evidence_id"])
        if finding["status"] == "false_positive":
            decision_basis_evidence_ids.update(finding["false_positive_disposition"]["evidence_ids"])
    for evidence_id in sorted(decision_basis_evidence_ids):
        item = evidence.get(evidence_id)
        if item is None:
            continue
        age_limit = max_age.get(item["evidence_type"], tailoring["default_evidence_max_age_days"])
        if _parse_time(item["produced_at"]) < as_of - timedelta(days=age_limit):
            blocking.append(Issue("EVIDENCE_STALE", f"evidence-index.json.{evidence_id}", f"decision-basis evidence exceeds the {age_limit}-day policy limit"))

    if preflight:
        if blocking:
            preflight_decision = "NEEDS_ACTION"
        elif conditional:
            preflight_decision = "ELIGIBLE_WITH_CONDITIONS"
        else:
            preflight_decision = "ELIGIBLE"
        return GateReport(
            preflight_decision,
            pack["pack_id"],
            candidate_id,
            tier,
            as_of.isoformat(),
            tuple(sorted(required_evidence)),
            tuple(blocking),
            tuple(warnings),
            mode=mode,
        )

    approvals_by_role: dict[str, set[str]] = {}
    if conditional or any(condition["status"] == "open" for condition in approval["conditions"]):
        required_roles.update(exception_rules["required_conditional_approval_roles"])
    decision_input_paths = {"pack": pack_dir / "pack.json"}
    decision_input_paths.update(
        {
            key: _safe_file(pack_dir, pack["file_map"][key])
            for key in ("system_manifest", "risk_register", "controls", "evaluation_cases", "evidence_index", "findings", "change_assessment")
        }
    )
    for key, path in decision_input_paths.items():
        if path is None or approval["input_hashes"][key] != _sha256(path):
            blocking.append(Issue("APPROVAL_INPUT_HASH_MISMATCH", f"approval-decision.json.input_hashes.{key}", "approval does not bind the exact decision input"))
    for index, approver in enumerate(approval["approvers"]):
        actor_id = approver["actor_id"]
        role = approver["role"]
        if not _actor_has_role(actors, actor_id, role):
            blocking.append(Issue("APPROVER_UNAUTHORIZED", f"approval-decision.json.approvers[{index}]", "actor does not hold the stated approval role"))
        elif not actors[actor_id]["active"]:
            blocking.append(Issue("APPROVER_INACTIVE", f"approval-decision.json.approvers[{index}]", "inactive actor cannot approve"))
        approvals_by_role.setdefault(role, set()).add(actor_id)
    for role in sorted(required_roles):
        if not approvals_by_role.get(role):
            blocking.append(Issue("APPROVAL_ROLE_MISSING", "approval-decision.json.approvers", f"missing required approval role {role}"))

    tier_rank = tailoring["tier_order"].index(tier)
    for rule in governance["separation_rules"]:
        if tier_rank < tailoring["tier_order"].index(rule["minimum_tier"]):
            continue
        left, right = rule["roles"]
        if approvals_by_role.get(left, set()) & approvals_by_role.get(right, set()):
            blocking.append(Issue("SEPARATION_OF_DUTIES_FAILED", "approval-decision.json.approvers", f"one actor cannot approve as both {left} and {right}"))

    required_evidence_ids = {item["evidence_id"] for item in selected_required_evidence}
    approval_evidence_ids = set(approval["evidence_ids"])
    if not required_evidence_ids.issubset(approval_evidence_ids):
        blocking.append(Issue("APPROVAL_EVIDENCE_INCOMPLETE", "approval-decision.json.evidence_ids", "approval does not bind every selected required evidence record"))
    if not decision_basis_evidence_ids.issubset(approval_evidence_ids):
        missing_basis = sorted(decision_basis_evidence_ids - approval_evidence_ids)
        blocking.append(Issue("APPROVAL_BASIS_EVIDENCE_INCOMPLETE", "approval-decision.json.evidence_ids", f"approval omits control, retest, or disposition evidence: {missing_basis}"))
    for evidence_id in approval["evidence_ids"]:
        if evidence_id not in evidence:
            blocking.append(Issue("APPROVAL_EVIDENCE_UNKNOWN", "approval-decision.json.evidence_ids", f"approval references unknown evidence {evidence_id}"))
        elif evidence[evidence_id]["status"] != "pass":
            blocking.append(Issue("APPROVAL_EVIDENCE_FAILED", "approval-decision.json.evidence_ids", f"approval references non-passing evidence {evidence_id}"))
        else:
            item = evidence[evidence_id]
            age_limit = max_age.get(item["evidence_type"], tailoring["default_evidence_max_age_days"])
            if _parse_time(item["produced_at"]) < as_of - timedelta(days=age_limit):
                blocking.append(Issue("APPROVAL_EVIDENCE_STALE", f"approval-decision.json.evidence_ids.{evidence_id}", f"approval evidence exceeds the {age_limit}-day policy limit"))
    approval_basis_evidence_ids = decision_basis_evidence_ids | {evidence_id for evidence_id in approval_evidence_ids if evidence_id in evidence}
    residual_risk_ids = {risk_id for risk_id, risk in risks.items() if risk["status"] in {"treated", "accepted"}}
    if set(approval["residual_risk_ids"]) != residual_risk_ids:
        blocking.append(Issue("APPROVAL_RESIDUAL_RISK_MISMATCH", "approval-decision.json.residual_risk_ids", "approval does not exactly list accepted residual risks"))
    if approval["rollback_target"] != manifest["rollback_target"]:
        blocking.append(Issue("ROLLBACK_TARGET_MISMATCH", "approval-decision.json.rollback_target", "approval rollback target does not match the system manifest"))

    decision_time = _parse_time(approval["decided_at"])
    if decision_time > as_of:
        blocking.append(Issue("APPROVAL_FROM_FUTURE", "approval-decision.json.decided_at", "approval date is after the gate decision time"))
    if decision_time < _parse_time(change_assessment["assessed_at"]):
        blocking.append(Issue("APPROVAL_PREDATES_CHANGE_ASSESSMENT", "approval-decision.json.decided_at", "approval predates the change assessment"))
    if decision_time < _parse_time(pack["created_at"]):
        blocking.append(Issue("APPROVAL_PREDATES_PACK", "approval-decision.json.decided_at", "approval predates the final evidence pack"))
    for risk_id in residual_risk_ids:
        if _parse_time(risks[risk_id]["acceptance"]["accepted_at"]) > decision_time:
            blocking.append(Issue("APPROVAL_PREDATES_RISK_ACCEPTANCE", f"risk-register.json.{risk_id}.acceptance.accepted_at", "approval predates residual-risk acceptance"))
    for risk_id, risk in risks.items():
        if risk["status"] == "not_applicable" and _parse_time(risk["not_applicable_approval"]["decided_at"]) > decision_time:
            blocking.append(Issue("APPROVAL_PREDATES_RISK_DISPOSITION", f"risk-register.json.{risk_id}.not_applicable_approval.decided_at", "approval predates the not-applicable risk disposition"))
    for control_id, control in controls.items():
        if control["status"] == "Not applicable" and _parse_time(control["not_applicable_approval"]["decided_at"]) > decision_time:
            blocking.append(Issue("APPROVAL_PREDATES_CONTROL_DISPOSITION", f"controls.json.{control_id}.not_applicable_approval.decided_at", "approval predates the not-applicable control disposition"))
    if selected_required_evidence and decision_time < max(_parse_time(item["produced_at"]) for item in selected_required_evidence):
        blocking.append(Issue("APPROVAL_PREDATES_EVIDENCE", "approval-decision.json.decided_at", "approval predates required evidence"))
    latest_required_evidence = max((_parse_time(item["produced_at"]) for item in selected_required_evidence), default=None)
    approval_basis_times = [
        _parse_time(pack["created_at"]),
        _parse_time(change_assessment["assessed_at"]),
        _parse_time(governance["approved_at"]),
        _parse_time(governance["effective_at"]),
        _parse_time(tailoring["approved_at"]),
        _parse_time(tailoring["effective_at"]),
        _parse_time(change_policy["approved_at"]),
        _parse_time(change_policy["effective_at"]),
    ]
    approval_basis_times.extend(_parse_time(evidence[evidence_id]["produced_at"]) for evidence_id in approval_basis_evidence_ids)
    approval_basis_times.extend(
        _parse_time(evidence[finding["source_evidence_id"]]["produced_at"])
        for finding in findings.values()
        if finding["source_evidence_id"] in evidence
    )
    approval_basis_times.extend(_parse_time(controls[control_id]["verified_at"]) for control_id in relied_control_ids)
    approval_basis_times.extend(_parse_time(risks[risk_id]["acceptance"]["accepted_at"]) for risk_id in residual_risk_ids)
    approval_basis_times.extend(
        _parse_time(risk["not_applicable_approval"]["decided_at"])
        for risk in risks.values()
        if risk["status"] == "not_applicable"
    )
    approval_basis_times.extend(
        _parse_time(control["not_applicable_approval"]["decided_at"])
        for control in controls.values()
        if control["status"] == "Not applicable"
    )
    approval_basis_times.extend(
        _parse_time(finding["acceptance"]["accepted_at"])
        for finding in findings.values()
        if finding["status"] == "risk_accepted"
    )
    approval_basis_times.extend(
        _parse_time(finding["false_positive_disposition"]["decided_at"])
        for finding in findings.values()
        if finding["status"] == "false_positive"
    )
    latest_approval_basis = max(approval_basis_times)
    if decision_time < latest_approval_basis:
        blocking.append(Issue("APPROVAL_PREDATES_BASIS", "approval-decision.json.decided_at", "approval decision predates part of its complete policy, evidence, control, risk, or disposition basis"))
    for index, approver in enumerate(approval["approvers"]):
        approved_at = _parse_time(approver["approved_at"])
        if approved_at > decision_time or approved_at > as_of:
            blocking.append(Issue("APPROVER_TIME_INVALID", f"approval-decision.json.approvers[{index}].approved_at", "approver timestamp is after the decision or gate time"))
        if latest_required_evidence and approved_at < latest_required_evidence:
            blocking.append(Issue("APPROVER_PREDATES_EVIDENCE", f"approval-decision.json.approvers[{index}].approved_at", "approver signed before required evidence was produced"))
        if approved_at < latest_approval_basis:
            blocking.append(Issue("APPROVER_PREDATES_BASIS", f"approval-decision.json.approvers[{index}].approved_at", "approver signed before the complete decision basis was established"))

    open_conditions = [condition for condition in approval["conditions"] if condition["status"] == "open"]
    condition_finding_ids: set[str] = set()
    for condition in approval["conditions"]:
        if not _actor_is_active(actors, condition["owner_actor_id"]):
            blocking.append(Issue("CONDITION_OWNER_UNKNOWN", f"approval-decision.json.conditions.{condition['condition_id']}", "condition owner is not in governance policy"))
        for finding_id in condition["finding_ids"]:
            if finding_id not in findings:
                blocking.append(Issue("CONDITION_FINDING_UNKNOWN", f"approval-decision.json.conditions.{condition['condition_id']}.finding_ids", f"unknown finding {finding_id}"))
            if condition["status"] == "open":
                condition_finding_ids.add(finding_id)
        if condition["status"] == "open" and _parse_time(condition["due_at"]) <= as_of:
            blocking.append(Issue("CONDITION_OVERDUE", f"approval-decision.json.conditions.{condition['condition_id']}.due_at", "open condition is already overdue"))
        if condition["status"] == "open":
            due_at = _parse_time(condition["due_at"])
            if due_at <= decision_time:
                blocking.append(Issue("CONDITION_TIME_INVALID", f"approval-decision.json.conditions.{condition['condition_id']}.due_at", "condition due date must follow the approval decision"))
            elif due_at - decision_time > timedelta(days=exception_rules["maximum_condition_days"]):
                blocking.append(Issue("CONDITION_TOO_LONG", f"approval-decision.json.conditions.{condition['condition_id']}.due_at", "condition exceeds the configured maximum duration"))
    approval_review_at = _parse_time(approval["next_review_at"])
    if approval_review_at <= as_of:
        blocking.append(Issue("APPROVAL_REVIEW_DUE", "approval-decision.json.next_review_at", "approval review date is not in the future"))
    basis_expiries = [
        _parse_time(governance["next_review_at"]),
        _parse_time(tailoring["next_review_at"]),
        _parse_time(change_policy["next_review_at"]),
    ]
    for evidence_id in approval_basis_evidence_ids:
        item = evidence[evidence_id]
        age_limit = max_age.get(item["evidence_type"], tailoring["default_evidence_max_age_days"])
        basis_expiries.append(
            min(
                _parse_time(item["valid_until"]),
                _parse_time(item["produced_at"]) + timedelta(days=age_limit),
            )
        )
    basis_expiries.extend(
        _parse_time(control["verification_valid_until"])
        for control in controls.values()
        if control["status"] == "Verified"
    )
    basis_expiries.extend(_parse_time(risks[risk_id]["acceptance"]["expires_at"]) for risk_id in residual_risk_ids)
    basis_expiries.extend(
        _parse_time(finding["acceptance"]["expires_at"])
        for finding in findings.values()
        if finding["status"] == "risk_accepted"
    )
    basis_expiries.extend(_parse_time(condition["due_at"]) for condition in open_conditions)
    if basis_expiries and approval_review_at > min(basis_expiries):
        blocking.append(Issue("APPROVAL_REVIEW_AFTER_BASIS_EXPIRY", "approval-decision.json.next_review_at", "approval review date exceeds the earliest expiry of its supporting basis"))
    conditional = conditional or bool(open_conditions)
    missing_condition_links = unresolved_nonblocking_findings - condition_finding_ids
    if missing_condition_links:
        blocking.append(Issue("CONDITION_RECORD_MISSING", "approval-decision.json.conditions", f"unresolved findings lack an open bounded condition: {sorted(missing_condition_links)}"))

    expected_decision = "approve_with_conditions" if conditional else "approve"
    if approval["decision"] == "reject":
        blocking.append(Issue("RECORDED_REJECTION", "approval-decision.json.decision", "the accountable release authority rejected this candidate"))
    elif approval["decision"] != expected_decision:
        blocking.append(Issue("DECISION_INCONSISTENT", "approval-decision.json.decision", f"evidence state requires {expected_decision}"))

    if blocking:
        decision = "REJECT"
    elif conditional:
        decision = "CONDITIONAL"
    else:
        decision = "APPROVE"
    authorizes_deployment = mode == "production" and decision == "APPROVE"
    if mode == "fictional" and allow_fictional and decision in {"APPROVE", "CONDITIONAL"}:
        decision = f"SIMULATED_{decision}"
    digests = {
        "gate_source": _gate_source_digest(),
        "runtime:jsonschema_version": distribution_version("jsonschema"),
        "policy:governance": _sha256(governance_path.resolve()),
        "policy:tailoring": _sha256(tailoring_path.resolve()),
        "policy:change_triggers": _sha256(change_policy_path.resolve()),
        "approval_decision": _sha256(_safe_file(pack_dir, pack["file_map"]["approval_decision"])),
    }
    digests.update({f"decision_input:{key}": _sha256(path) for key, path in decision_input_paths.items() if path is not None})
    return GateReport(
        decision,
        pack["pack_id"],
        candidate_id,
        tier,
        as_of.isoformat(),
        tuple(sorted(required_evidence)),
        tuple(blocking),
        tuple(warnings),
        mode=mode,
        authorizes_deployment=authorizes_deployment,
        digests=digests,
    )


def assess_change(assessment_path: Path, policy_path: Path) -> dict[str, Any]:
    schemas, registry = _schema_bundle()
    assessment = _load_json(assessment_path.resolve())
    policy = _load_json(policy_path.resolve())
    issues = _validate_schema(assessment, "change_assessment", str(assessment_path), schemas, registry)
    issues.extend(_validate_schema(policy, "change_policy", str(policy_path), schemas, registry))
    if issues:
        return {"decision": "INVALID", "required_scope": None, "required_evidence_types": [], "requires_new_approval": None, "issues": [asdict(issue) for issue in issues]}
    change_types = [trigger["change_type"] for trigger in policy["triggers"]]
    if len(set(change_types)) != len(change_types):
        issues.append(Issue("CHANGE_TRIGGER_DUPLICATE", "change policy.triggers", "change policy contains duplicate change types"))
    trigger_map = {trigger["change_type"]: trigger for trigger in policy["triggers"]}
    required_scope = 1
    evidence: set[str] = set()
    for change in assessment["changes"]:
        trigger = trigger_map.get(change["change_type"])
        if trigger is None:
            issues.append(Issue("CHANGE_TYPE_UNKNOWN", "change-assessment.json.changes", f"no policy trigger for {change['change_type']}"))
            continue
        required_scope = max(required_scope, SCOPE_RANK[trigger["minimum_scope"]])
        evidence.update(trigger["required_evidence_types"])
    declared_types = {change["change_type"] for change in assessment["changes"]}
    if assessment["baseline_candidate_id"] is None and "first_release" not in declared_types:
        issues.append(Issue("FIRST_RELEASE_TRIGGER_MISSING", "change-assessment.json.changes", "a candidate without a baseline must declare first_release"))
    if assessment["baseline_candidate_id"] is not None and "first_release" in declared_types:
        issues.append(Issue("FIRST_RELEASE_TRIGGER_INVALID", "change-assessment.json.changes", "first_release cannot be used with a baseline"))
    scope_name = next(name for name, rank in SCOPE_RANK.items() if rank == required_scope)
    if SCOPE_RANK[assessment["declared_scope"]] < required_scope:
        issues.append(Issue("CHANGE_SCOPE_TOO_NARROW", "change-assessment.json.declared_scope", f"minimum scope is {scope_name}"))
    return {
        "decision": "VALID" if not issues else "INVALID",
        "required_scope": scope_name,
        "required_evidence_types": sorted(evidence),
        "requires_new_approval": True,
        "issues": [asdict(issue) for issue in issues],
    }
