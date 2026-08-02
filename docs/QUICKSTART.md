# Ten-minute starter

This path creates the smallest Tier 1 workspace. It reduces setup work, not the
production trust standard. The final gate remains fail-closed and applies the
same evidence, authority, freshness, and candidate-binding rules.

## 1. Create the workspace

```bash
evalseal init my-assessment \
  --candidate-id CAND-MY-SYSTEM-001 \
  --name "My system"
```

The command creates:

```text
my-assessment/
├── governance/
│   ├── governance.json
│   ├── tailoring.json
│   └── change-triggers.json
└── evidence/current/
    ├── pack.json
    ├── system-manifest.json
    ├── risk-register.json
    ├── controls.json
    ├── evaluation-cases.json
    ├── evidence-index.json
    ├── findings.json
    ├── change-assessment.json
    ├── approval-decision.json
    └── artifacts/
```

The result is deliberately a non-approvable template. It cannot authorize a
deployment until placeholders are replaced, policies are adopted, real evidence
is attached, and an accountable decision is recorded.

## 2. Complete six non-negotiables

1. **Identity:** bind the exact candidate, model, prompt, configuration, data,
   tools, exposure, and rollback target.
2. **Risk:** record the material risks and their owners.
3. **Controls and tests:** link each material risk to implemented controls and
   production-like evaluation cases.
4. **Evidence:** attach real reports and results, with current independent
   verification where policy requires it.
5. **Findings:** preserve failures, remediation, retests, and authorized
   residual-risk dispositions.
6. **Authority:** obtain the roles and human decision required by the adopted
   governance policy.

The supplied Tier 1 profile is only appropriate when all four risk dimensions
are genuinely low: low impact, assistive autonomy, public data, and isolated
exposure. The computed tier overrides an understated declaration.

## 3. Refresh byte hashes

After editing artifacts and records, refresh the declared hashes:

```bash
evalseal hash \
  --pack my-assessment/evidence/current \
  --governance my-assessment/governance/governance.json \
  --tailoring my-assessment/governance/tailoring.json \
  --change-policy my-assessment/governance/change-triggers.json
```

This command only binds bytes. It cannot determine whether a report is true,
whether a test reached the intended system, or whether evidence is sufficient.
Review every changed hash before committing it.

## 4. Preflight, approve, and bind the decision

Run preflight using the command in the operating guide. When it reports
eligibility, freeze the evidence inputs. While `approval-decision.json` is still
`draft`, bind the decision record to those exact files:

```bash
evalseal hash \
  --pack my-assessment/evidence/current \
  --governance my-assessment/governance/governance.json \
  --tailoring my-assessment/governance/tailoring.json \
  --change-policy my-assessment/governance/change-triggers.json \
  --approval
```

Now have the authorized human review the bound evidence and change the approval
record from draft to its final decision. Do not run the hash command with
`--approval` afterward. It refuses to rebind a final approval; any changed input
requires a new draft and a new accountable decision.

## 5. Run the final gate

Run the final command in the operating guide from a protected pipeline. Deploy
only the exact candidate bound by a valid `APPROVE`, or by a `CONDITIONAL`
decision when organizational policy and the deployment job explicitly allow it.

## What this starter is not

It is not a lightweight self-certification route. It does not authenticate
people, execute evaluations, verify report truth, provide legal advice, certify
a standard, or prove that deployed bytes match approved bytes. Those controls
must come from the adopting organization's protected systems and reviewers.
