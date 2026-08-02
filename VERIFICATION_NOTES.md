# Verification notes

**Release:** EvalSeal 0.1.0

**Last updated:** 2026-08-02

## Scope

This record covers repository verification of the schemas, policy contracts,
evidence-pack structure, deterministic validation engine, command-line release
gate, reference CI workflow, documentation, and fictional worked example.

EvalSeal is one procedural control inside a protected release process. It
consumes organization-owned policies, an external identity boundary, and an
accountable human decision; it supplies none of them.

## Implemented release components

| Capability | Implemented evidence | Status |
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

## Architecture and alternative analysis

The release uses JSON Schema Draft 2020-12 because the immediate consumer is a portable deterministic gate. NIST OSCAL informed the structured evidence direction but was not copied because no current integration consumes OSCAL. Promptfoo, DeepEval, and similar tools can execute evaluations, while managed platforms such as IBM watsonx.governance and Credo AI can provide broader inventory and workflow. This release does not duplicate those products.

Its narrower production job is to connect LLM-specific candidate identity, evidence, risks, controls, change scope, governance authority, and a final release decision in a vendor-neutral package. The sources and limitations supporting this choice are recorded in [SOURCE_REGISTER.md](SOURCE_REGISTER.md), especially S31 through S40.

## Standards and legal claims

The [claims ledger](CLAIMS_LEDGER.md) records the claim-by-claim corrections for standards, law, metrics, security, tools, and fairness. The implementation preserves its key conclusions:

- NIST AI RMF is treated as voluntary risk-management guidance, not certification.
- OWASP provides a risk taxonomy, not official Critical, High, or Medium ratings for each item.
- MITRE ATLAS is treated as a changing knowledge base, without a hard-coded technique count.
- ISO/IEC 42001 mappings are not asserted beyond the public standard scope.
- EU AI Act applicability remains role-, risk-, date-, and context-specific and requires current qualified assessment.
- Tool metrics, sample sizes, thresholds, and model graders require local validation rather than universal defaults.
- Prompt instructions and classifiers are not treated as deterministic authorization or security boundaries.

Operational claims were checked against the primary or authoritative sources in the source register. The release pins `jsonschema[format]` 4.26.0, setuptools 83.0.0 for the build, and complete GitHub Action commit SHAs. The Linux CPython 3.13 runtime dependency set is exact and hash-locked.

## Verification record

The following checks completed successfully, most recently on 2026-08-02:

- 72 of 72 automated tests passed locally on Windows; the public workflow runs the suite on Linux with Python 3.11 and 3.13.
- All 13 bundled schemas loaded and passed Draft 2020-12 schema validation.
- The suite exercised a real, non-mocked positive production engine path that returned `APPROVE` with `authorizes_deployment=true` and zero issues.
- The complete fictional pack returned `SIMULATED_APPROVE`, `authorizes_deployment=false`, and exit 3.
- Hash-generated JSON uses canonical LF bytes on every operating system, and the release manifest is generated from staged Git blobs rather than platform-dependent working-tree bytes.
- Negative coverage included changed hashes, stale and expired evidence, newer failures, open blockers, unauthorized acceptance, missing roles, self-verification, excessive conditions, invalid change scope, duplicate keys, non-reciprocal risk/control links, incomplete approval evidence, approval chronology, and review-basis expiry.
- A positive remediation lifecycle demonstrates that historical failed evidence can be tracked, fixed, distinctly retested, and approved without relabeling the historical failure as passing evidence.
- The final wheel installed in an isolated target and its packaged `init` and `hash` commands completed successfully. The earlier release checks also covered change assessment, preflight, decision, provenance digest, and exit behavior.
- The public Linux CPython 3.13 job installs the 17 pinned runtime artifacts with `--require-hashes` and binary-only enforcement before running the suite.
- The GitHub Actions YAML parsed successfully and its protected release job structure was checked.
- On 2026-08-02 the pinned GitHub Action commit SHAs were resolved against their official release tags, the pinned jsonschema and setuptools versions were confirmed on PyPI, the referenced tool repositories (NVIDIA/garak, microsoft/PyRIT, confident-ai/deepeval) resolved, the NIST AI RMF revision notice was confirmed current, and the Regulation (EU) 2026/1744 high-risk application dates (2027-12-02 and 2028-08-02) were confirmed against EUR-Lex and the European Commission.
- On 2026-08-02 every local Markdown link resolved, `RELEASE_MANIFEST.sha256` matched the staged Git blobs, the wheel contents matched the source tree byte for byte, and the fictional example returned `SIMULATED_APPROVE` with exit 3 through the installed CLI.

The final wheel is:

`dist/evaluation_methodology_gate-0.1.0-py3-none-any.whl`

SHA-256: `6d8ec6b75d0cf725450327b999ba2d0b942879d33e3de6b2297c09cd6a473ef9`

The complete release-file checksums are in `RELEASE_MANIFEST.sha256`. The manifest includes these notes and the wheel but excludes itself.

## Required production controls outside this repository

Before relying on an `APPROVE` result, the adopting organization must:

1. Replace every example/reference policy with approved organization-owned policy files and authenticated actor identities.
2. Generate evidence through protected systems and preserve the relationship between reports and the exact candidate bytes.
3. Protect the release directory, policy files, approval records, workflow, default branch, and `evaluation-governance` environment from unilateral candidate-author changes.
4. Make deployment consume the exact approved candidate revision, prompt/configuration hashes, model identifiers, retrieval versions, and policy bindings.
5. Preserve the JSON gate report and deployment provenance, then monitor, respond to incidents, and reassess on configured triggers.
6. Obtain current legal, privacy, security, and standards review where the system's context requires it.

## Residual limitations

The gate validates supplied bytes and deterministic relationships. It cannot establish that a report is truthful, that a test harness reached the intended production-equivalent system, that a typed actor name is authenticated, that an organizational policy is legally sufficient, that the deployed bytes match the approved bytes, or that a probabilistic system will never fail.

Those are explicit trust-boundary dependencies, not unfinished gate features. Adding attestations, OSCAL exchange, hosted identity, evaluation execution, deployment verification, or continuous monitoring belongs in a later release only when a real adopting system supplies the consumer and acceptance criteria.
