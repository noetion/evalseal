# Governance setup

## Required decisions

The organization must name real people or accountable positions for:

- governance authority;
- system and risk ownership;
- control ownership;
- evaluation ownership;
- release authority;
- security, privacy, legal, fairness, accessibility, and independent review where applicable; and
- executive risk authority for the highest permitted residual risks.

## Authority configuration

`governance.json` defines:

- active actors and the roles they actually hold;
- the maximum residual-risk level each role may accept;
- the organization-wide ceiling for accepted residual risk and conditional-finding severity;
- maximum risk-acceptance and release-condition durations;
- roles required for conditional approval, not-applicable dispositions, and false-positive dispositions;
- allowed verifier roles for each evidence type;
- the maximum evidence-artifact size accepted by the gate;
- roles that must not be exercised by the same approver at specified tiers;
- the policy approver; and
- the policy review date.

The reference configuration permits `governance_authority` to disposition a critical inherent risk as genuinely not applicable, but the organization-wide tolerance prohibits accepting critical residual risk for release. High residual risk still requires a role with sufficient authority and remains subject to the global ceiling. An organization may adopt stricter limits. It must not configure acceptance that applicable law, contracts, or internal policy prohibit.

Every treated or directly accepted residual risk needs a named, time-bounded acceptance. Every not-applicable risk or control needs a named disposition. Conditional release additionally requires the configured exception role, remains severity-bounded, and cannot outlast the configured condition window.

## Identity trust boundary

The gate verifies that a recorded actor holds the recorded role. It cannot prove who edited the JSON file. Production use therefore requires an external identity and integrity boundary, such as:

- protected branches and required code owners;
- signed commits or attestations;
- an identity-provider-backed governance workflow;
- a controlled evidence store; or
- a deployment environment requiring named human approval.

The policy files should be outside the candidate-controlled evidence directory and supplied to the gate from a protected source. The pack binds their exact hashes, and the final approval binds the pack plus every decision-input record.

## Separation of duties

For Tier 3 and Tier 4 systems, the reference configuration separates release authority from independent review. Tier 4 also separates release and security approval. The gate prevents Tier 3 or Tier 4 evidence from being self-verified, applies evidence-type verifier-role policy, and prevents a control owner from verifying evidence used to mark that control `Verified`.

Small teams may assign several operational roles to one person, but they need a compensating independent approval wherever the adopted policy requires separation.
