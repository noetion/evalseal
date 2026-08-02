# Operational verification record

**Release:** Evaluation Methodology Gate 0.1.0 reference implementation

**Last updated:** 2026-08-01

**Current status:** **REFERENCE IMPLEMENTATION FOR CONTROLLED ADOPTION**

**Candidate decisions:** Made by adopting organizations using protected policies, evidence, and accountable approval.

## 1. Scope of this record

This record covers repository verification of the schemas, policy contracts,
evidence-pack structure, deterministic validation engine, command-line release
gate, reference CI workflow, documentation, and fictional worked example.

It shows that the reference implementation passed the checks listed below. It is
not an independent audit, production endorsement, or assurance opinion. An
organization may evaluate it as one procedural control in a protected release
process, but must establish its own policies, trust mechanisms, validation, and
accountable approval.

Candidate-specific evidence, authenticated approvals, deployment controls, and operational monitoring are supplied and governed by the adopting organization. No ISO/IEC 42001 conformity, legal compliance, or product certification is claimed.

## 2. Implemented release components

| Requested capability | Implemented evidence | Release status |
|---|---|---|
| Machine-readable system, risk, control, case, evidence, finding, and decision records | 13 JSON Schema Draft 2020-12 contracts under `src/evaluation_gate/schemas/` | Implemented and executable |
| Reference evidence pack | `evidence-pack-template/` contains the nine records and bound artifact layout expected from a candidate team | Implemented; deliberately non-approvable until populated |
| Automated completeness and freshness validation | `evaluation_gate.engine` checks structure, identities, hashes, evidence age and validity, failed-result precedence, findings, control verification, risk acceptance, authority, chronology, reassessment, and review expiry | Implemented and tested |
| Release-gate command and CI workflow | `evaluation-gate` returns `APPROVE`, `CONDITIONAL`, or `REJECT`; `ci/github-actions.yml` verifies the release manifest, installs hash-locked dependencies and the wheel, runs preflight, and enforces the final decision | Implemented; adopting organization must protect the workflow and environment |
| End-to-end worked example | `examples/fictional-support-assistant/` contains completed Tier 3 records and reports | Implemented; returns `SIMULATED_APPROVE`, exit 3, and never deployment authority |
| Risk-scaled tailoring | `config/tailoring.reference.json` maps impact, autonomy, data sensitivity, and exposure to evidence and approval requirements | Implemented as reference policy; organization adoption is required |
| Formal change triggers | `config/change-triggers.reference.json` defines documentation, targeted, full, and incident reassessment requirements and requires fresh approval for every final candidate | Implemented as reference policy; protected change evidence is required |
| Organization-specific governance | `config/governance.example.json` defines actors, roles, authority limits, tolerance, exception rules, verifier roles, separation rules, and resource limits | Implemented as a schema and example; real identities and authority are intentionally not supplied |
| Onboarding and hash automation | `evaluation-gate init` creates a non-approvable Tier 1 starter; `evaluation-gate hash` calculates policy, artifact, and optional frozen-decision bindings | Implemented and tested; hashing establishes byte integrity, not evidence truth |

## 3. Architecture and alternative analysis

The release uses JSON Schema Draft 2020-12 because the immediate consumer is a portable deterministic gate. NIST OSCAL informed the structured evidence direction but was not copied because no current integration consumes OSCAL. Promptfoo, DeepEval, and similar tools can execute evaluations, while managed platforms such as IBM watsonx.governance and Credo AI can provide broader inventory and workflow. This release does not duplicate those products.

Its narrower production job is to connect LLM-specific candidate identity, evidence, risks, controls, change scope, governance authority, and a final release decision in a vendor-neutral package. The sources and limitations supporting this choice are recorded in [SOURCE_REGISTER.md](SOURCE_REGISTER.md), especially S31 through S40.

## 4. Factual and technical audit

The earlier publication audit remains the claim-by-claim record for standards, law, metrics, security, tools, and fairness. The operational implementation preserves its key corrections:

- NIST AI RMF is treated as voluntary risk-management guidance, not certification.
- OWASP provides a risk taxonomy, not official Critical, High, or Medium ratings for each item.
- MITRE ATLAS is treated as a changing knowledge base, without a hard-coded technique count.
- ISO/IEC 42001 mappings are not asserted beyond the public standard scope.
- EU AI Act applicability remains role-, risk-, date-, and context-specific and requires current qualified assessment.
- Tool metrics, sample sizes, thresholds, and model graders require local validation rather than universal defaults.
- Prompt instructions and classifiers are not treated as deterministic authorization or security boundaries.

Operational claims were checked against the primary or authoritative sources in the source register. The release pins `jsonschema[format]` 4.26.0, setuptools 83.0.0 for the build, and complete GitHub Action commit SHAs. The Linux CPython 3.13 runtime dependency set is exact and hash-locked.

## 5. Verification record

The following checks completed successfully, most recently on 2026-08-01:

- 70 of 70 automated tests passed against the pinned runtime dependency set.
- All 13 bundled schemas loaded and passed Draft 2020-12 schema validation.
- The suite exercised a real, non-mocked positive production engine path that returned `APPROVE` with `authorizes_deployment=true` and zero issues.
- The complete fictional pack returned `SIMULATED_APPROVE`, `authorizes_deployment=false`, and exit 3.
- Hash-generated JSON uses canonical LF bytes on every operating system, and the release manifest is generated from staged Git blobs rather than platform-dependent working-tree bytes.
- Negative coverage included changed hashes, stale and expired evidence, newer failures, open blockers, unauthorized acceptance, missing roles, self-verification, excessive conditions, invalid change scope, duplicate keys, non-reciprocal risk/control links, incomplete approval evidence, approval chronology, and review-basis expiry.
- A positive remediation lifecycle proved that historical failed evidence can be tracked, fixed, distinctly retested, and approved without relabeling the historical failure as passing evidence.
- The final wheel installed in an isolated target and its packaged `init` and `hash` commands completed successfully. The earlier release checks also covered change assessment, preflight, decision, provenance digest, and exit behavior.
- All 17 Linux CPython 3.13 runtime artifacts resolved successfully with `--require-hashes` and binary-only enforcement.
- The GitHub Actions YAML parsed successfully and its protected release job structure was checked.

The final wheel is:

`dist/evaluation_methodology_gate-0.1.0-py3-none-any.whl`

SHA-256: `f8615fabf8e7880d865dca20ef85601bbaa054709d1c40d8f163cd4469c1abd4`

The complete release-file checksums are in `RELEASE_MANIFEST.sha256`. That manifest includes this audit and the wheel but excludes itself.

## 6. Repository review and corrections

A separate read-only review pass was performed during implementation. This was
not an independent human or third-party audit. Its reported blockers were
reproduced, corrected, and covered by regression tests. Material corrections
included:

- production time uses the live UTC clock and rejects historical overrides;
- CI installs a protected wheel and hash-locked dependencies, verifies a release manifest, pins official actions to full commits, quotes caller inputs, and requires a protected governance environment;
- approvals bind every decision-input file and all affirmative required, control, retest, and disposition evidence;
- approvers and decisions must postdate the complete policy, pack, change, evidence, control, risk, finding, and disposition basis;
- control validity cannot outlast its evidence, and risk acceptance cannot outlast relied-on control verification;
- risk-to-control mappings must be reciprocal;
- duplicate JSON object keys fail closed;
- the change-assessment text command reports its required scope, evidence types, fresh-approval requirement, and issues;
- historical failed evidence remains immutable and tracked while approval relies on a distinct passing retest; and
- optional finding sources still participate in approval chronology, including conditional decisions;
- repository text is normalized to LF while wheels are explicitly binary; and
- CI fails unless the fictional example returns exit 3 with `SIMULATED_APPROVE` and no deployment authority.

The review found no remaining repository test blocker at that time, with the
complete 70-test suite passing. Adopting organizations remain responsible for
candidate-specific validation and deployment controls.

## 7. Required production controls outside this repository

Before relying on an `APPROVE` result, the adopting organization must:

1. Replace every example/reference policy with approved organization-owned policy files and authenticated actor identities.
2. Generate evidence through protected systems and preserve the relationship between reports and the exact candidate bytes.
3. Protect the release directory, policy files, approval records, workflow, default branch, and `evaluation-governance` environment from unilateral candidate-author changes.
4. Make deployment consume the exact approved candidate revision, prompt/configuration hashes, model identifiers, retrieval versions, and policy bindings.
5. Preserve the JSON gate report and deployment provenance, then monitor, respond to incidents, and reassess on configured triggers.
6. Obtain current legal, privacy, security, and standards review where the system's context requires it.

## 8. Residual limitations

The gate validates supplied bytes and deterministic relationships. It cannot establish that a report is truthful, that a test harness reached the intended production-equivalent system, that a typed actor name is authenticated, that an organizational policy is legally sufficient, that the deployed bytes match the approved bytes, or that a probabilistic system will never fail.

Those are explicit trust-boundary dependencies, not unfinished gate features. Adding attestations, OSCAL exchange, hosted identity, evaluation execution, deployment verification, or continuous monitoring belongs in a later release only when a real adopting system supplies the consumer and acceptance criteria.

The next maturity milestone is documented feedback from controlled adoption
with authenticated human reviewers. Those findings should inform subsequent
releases and any broader adoption claims.

## 9. Release status

- **Reference implementation:** Version 0.1.0, designed for controlled adoption.
- **Repository checks:** Passed as recorded in this file and updated release
  records.
- **Adoption requirement:** Validate candidate-specific evidence, policies, and
  deployment controls before relying on a gate decision.
- **ISO/IEC 42001 conformity or legal compliance:** Not assessed or certified.

This file is a repository verification record, not a technical sign-off.
Organizational production authority cannot be delegated to this repository or
its authors.
