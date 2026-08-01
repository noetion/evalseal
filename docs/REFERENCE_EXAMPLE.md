# End-to-end fictional example

The directory `examples/fictional-support-assistant/` contains a complete Tier 3 example.

## Scenario

A fictional internal assistant answers support-policy questions using caller-authorized retrieval. It has no external tools. It processes confidential internal material and synthetic personal test data, and it uses a model grader for supported-claim evaluation.

The highest risk-profile dimension is confidential data, so the reference policy computes Tier 3. The personal-data and model-grader flags add privacy review and grader-validation evidence.

## Evidence path

1. `system-manifest.json` binds the candidate, prompt bundle, runtime configuration, model versions, retrieval versions, scope, and applicability.
2. `risk-register.json` records disclosure, injection, unsupported-answer, privacy, and availability risks.
3. `controls.json` links each treated risk to implemented and independently verified controls.
4. `evaluation-cases.json` links representative, abstention, cross-tenant, injection, privacy, and over-refusal cases to requirements and risks.
5. `evidence-index.json` binds ten fictional reports, plans, and retest records by SHA-256, owner, authorized verifier, candidate, result, and validity period.
6. `findings.json` shows a blocking renderer finding that was fixed and linked to distinct passing retest evidence.
7. `change-assessment.json` selects a full assessment because this is the first release.
8. `approval-decision.json` records release, security, privacy, and independent approval; accepts every treated residual risk; and binds the hashes of all decision inputs.

## Run it

```powershell
evaluation-gate gate `
  --pack examples/fictional-support-assistant/evidence-pack `
  --governance examples/fictional-support-assistant/governance.json `
  --tailoring config/tailoring.reference.json `
  --change-policy config/change-triggers.reference.json `
  --as-of 2026-07-31T12:30:00Z `
  --allow-fictional
```

Expected result:

```text
Decision: SIMULATED_APPROVE
Gate version: 0.1.0
Mode: fictional
Authorizes deployment: false
Tier: tier_3
Blocking issues: 0
Warnings: 0
```

The explicit `--allow-fictional` flag is required. `SIMULATED_APPROVE` returns exit 3, not success, and `authorizes_deployment` is false. This is intentional: a preserved example report cannot be mistaken for production authority. Without the flag, the pack is rejected.
