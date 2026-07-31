# Evidence pack template

Copy this directory for each release candidate. Replace every template value, set every artifact to `final`, bind the exact approved policy hashes, add the required evidence files under `artifacts/`, and run preflight. Freeze the decision inputs, record their exact hashes in `approval-decision.json`, obtain accountable approval, and then run the final gate.

The template is intentionally **not production-approvable**. Its pack mode is `template`, its risk is unresolved, and its decision is `reject`. This prevents an untouched example from being mistaken for approval evidence.

| File | Team output |
|---|---|
| `pack.json` | Root identity, policy bindings, and file map |
| `system-manifest.json` | Exact candidate, scope, components, data, risk profile, and applicability |
| `risk-register.json` | Material risks, treatments, controls, owners, and acceptances |
| `controls.json` | Implementation and current verification evidence for each control |
| `evaluation-cases.json` | Versioned requirement- and risk-linked evaluation cases |
| `evidence-index.json` | Hash-bound reports, plans, exercises, owners, verifiers, and validity |
| `findings.json` | Findings, blocking status, remediation, acceptance, and retest evidence |
| `change-assessment.json` | Changes from the last approved baseline and reassessment scope |
| `approval-decision.json` | Human approval, exact decision-input hashes, evidence snapshot, residual risks, conditions, rollback, and review date |
| `artifacts/` | Human-readable and machine-produced reports referenced by `evidence-index.json` |

Do not store secrets, unnecessary personal data, or hidden model reasoning in the pack. Apply the organization's access, retention, and deletion rules.
