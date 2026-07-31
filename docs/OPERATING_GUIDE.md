# Operating guide

## What the release gate does

The gate validates a release candidate's machine-readable evidence pack against approved organizational policies. It checks:

- JSON Schema conformance;
- exact candidate identity across records;
- risk tier and required evidence;
- evidence, policy, and exact approval-input hashes;
- evidence and control-verification freshness;
- newest-result precedence so an older pass cannot hide a newer failure;
- risk, control, finding, and evaluation-case references, including reciprocal risk-to-control mappings;
- unambiguous JSON records, with duplicate object keys rejected;
- unresolved blocking findings;
- residual-risk acceptance, not-applicable and false-positive disposition authority, and expiry;
- required approver roles and separation of duties;
- evidence-verifier roles, conditional-release limits, and artifact-size limits;
- change-trigger scope; and
- consistency between the evidence state, rollback target, review horizon, and recorded decision.

It does not execute model evaluations, prove that a report is truthful, provide legal advice, certify ISO conformity, authenticate a person's identity, or deploy an application. Those responsibilities remain with evaluation tools, protected identity and source-control systems, qualified reviewers, and the deployment platform.

## Install

Requires Python 3.11 or newer.

```powershell
python -m pip install --no-deps dist/evaluation_methodology_gate-1.0.0-py3-none-any.whl
evaluation-gate --help
```

The only direct runtime dependency is the pinned `jsonschema[format]` package. Install it through the applicable locked environment before using `--no-deps`. The schemas use JSON Schema Draft 2020-12. The released Linux CI path uses the hash-locked transitive dependency set in `ci/requirements-linux-py313.lock` and the verified wheel under `dist/`.

## One-time organizational setup

1. Copy `config/governance.example.json` to a protected organization-owned location.
2. Replace every fictional or placeholder actor with real accountable identities and roles.
3. Decide the organization's risk-acceptance limits and separation rules.
4. Configure the global risk tolerance, exception duration and roles, evidence-verifier roles, and artifact-size limit.
5. Copy and tailor `config/tailoring.reference.json` and `config/change-triggers.reference.json`.
6. Change each adopted policy to `approved`, record its approver and review date, and protect it through branch rules, repository permissions, or a trusted policy store.
7. Do not use the example or reference policy files for a real deployment.

See [GOVERNANCE_SETUP.md](GOVERNANCE_SETUP.md) and [TAILORING_GUIDE.md](TAILORING_GUIDE.md).

## Per-candidate workflow

### 1. Create the evidence pack

Copy `evidence-pack-template/` to a candidate-specific directory. Give the pack and candidate stable identifiers. Populate all nine JSON records and place source reports under `artifacts/`.

### 2. Bind immutable inputs

Record SHA-256 hashes for:

- the approved governance, tailoring, and change-trigger policies;
- the canonical prompt bundle and runtime configuration;
- the evaluation dataset; and
- every evidence artifact.

The gate rejects a changed file when its recorded hash is not updated. Policy updates require a new binding and accountable review. After preflight, freeze `pack.json`, the manifest, risk register, controls, evaluation cases, evidence index, findings, and change assessment. The final human approval must record the exact hash of each in `approval-decision.json`; any later edit invalidates the approval.

### 3. Assess the change

```powershell
evaluation-gate assess-change `
  --assessment evidence/current/change-assessment.json `
  --policy governance/change-triggers.json `
  --format json
```

The declared scope must be at least as broad as the strictest applicable trigger. Change types are accountable declarations supported by protected diffs and review, not values the gate derives automatically. Every final candidate requires fresh approval even when the minimum reassessment is documentation-only.

### 4. Run preflight before approval

```powershell
evaluation-gate preflight `
  --pack evidence/current `
  --governance governance/governance.json `
  --tailoring governance/tailoring.json `
  --change-policy governance/change-triggers.json `
  --output artifacts/preflight-report.json
```

Preflight returns:

- `ELIGIBLE` when evidence is complete and no release conditions are needed;
- `ELIGIBLE_WITH_CONDITIONS` when only non-blocking, bounded findings remain; or
- `NEEDS_ACTION` when a blocking issue remains.

Preflight deliberately does not grant production approval.

### 5. Obtain accountable approval

Approvers inspect the human-readable evidence, residual risks, limitations, and conditions. Record the exact identities, roles, timestamps, decision-input hashes, affirmative passing evidence IDs, all treated or directly accepted residual risks, rollback target, and next review in `approval-decision.json`. Historical failed source evidence remains bound by the hashed evidence index and finding record; the distinct passing retest belongs in the affirmative approval evidence list. The review date cannot exceed the earliest policy review, evidence freshness cutoff, artifact validity, control verification, risk acceptance, finding acceptance, or open-condition due date.

The identity and approval record must come from a protected process. A name typed into JSON is not a digital signature. Recommended trust mechanisms include protected pull-request approvals, a governed workflow system, signed attestations, or an identity-provider-backed approval service.

### 6. Run the final gate

```powershell
evaluation-gate gate `
  --pack evidence/current `
  --governance governance/governance.json `
  --tailoring governance/tailoring.json `
  --change-policy governance/change-triggers.json `
  --output artifacts/release-gate-report.json
```

Final decisions and exit behavior:

| Decision | Meaning | Default exit |
|---|---|---:|
| `APPROVE` | Evidence passes and required human approval is recorded | 0 |
| `CONDITIONAL` | No blocker remains, but bounded conditions are open | 2 |
| `REJECT` | Evidence, authority, freshness, scope, or blocking requirements fail | 1 |
| `SIMULATED_APPROVE` / `SIMULATED_CONDITIONAL` | Fictional validation only; never deployment authority | 3 |

Use `--allow-conditional` only if organizational policy permits the deployment pipeline to proceed on a valid conditional approval. Without that flag, conditional approval stops automated deployment for an explicit human decision.

`--as-of` is restricted to fictional replay. Production mode rejects any explicit historical time and uses the gate runner's current UTC clock. `--allow-fictional` must never appear in a deployment workflow.

### 7. Deploy the exact candidate

The deployment job must consume the same candidate revision, prompt/configuration hashes, model identifiers, retrieval versions, and policy bindings that the gate approved. Store the JSON gate report with the deployment record. The report includes mode, deployment authority, gate version, a digest of the installed gate source and schemas, the runtime jsonschema version, policy digests, approval digest, and every decision-input digest.

## Protected CI requirements

- Run the final gate in a protected pipeline, not solely on a developer workstation.
- Make policy and approval changes subject to designated reviewers.
- Keep deployment credentials unavailable to pull-request code from untrusted forks.
- Upload the gate report as an immutable build artifact.
- Make deployment depend on a successful final-gate job.
- Prevent the job from replacing evidence, policies, or approval records after validation.
- Install the gate from a protected, manifest-verified release, never from candidate-controlled application source.

See the reusable reference workflow in `ci/github-actions.yml`.
