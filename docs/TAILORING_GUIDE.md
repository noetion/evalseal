# Tailoring guide

The reference policy scales assurance according to four dimensions. These values are an editable organizational default, not a legal or industry-standard classification.

| Dimension | Tier 1 example | Tier 2 example | Tier 3 example | Tier 4 example |
|---|---|---|---|---|
| Impact | Low and readily reversible | Moderate and bounded | High or materially consequential | Critical or potentially irreversible |
| Autonomy | Assists a person | Recommends an outcome | Performs bounded transactions | Acts autonomously in a high-impact context |
| Data sensitivity | Public | Internal | Confidential | Restricted |
| Exposure | Isolated | Internal | Limited external | Public |

The reference calculation uses the highest dimension score. This conservative rule prevents a low value in one dimension from averaging away a critical value in another.

## Reference tier effects

| Tier | Main assurance increase |
|---|---|
| Tier 1 | Core evaluation, security, monitoring, incident, rollback, and release approval |
| Tier 2 | Adds security approval and tighter evidence age |
| Tier 3 | Adds red teaming, human-oversight evidence, independent review, and tighter evidence age |
| Tier 4 | Adds incident exercise, legal applicability, executive risk authority, and strongest separation of duties |

Conditional requirements apply independently of the tier:

- personal data requires privacy/data evidence and privacy approval;
- effects on rights or access require fairness/impact evidence, legal applicability, and the corresponding reviewers;
- a model grader requires grader-validation evidence;
- external actions require human-oversight and red-team evidence;
- material accessibility impact requires an accessibility review; and
- regulated use requires a legal-applicability assessment.

Tier policy does not override governance tolerance. A candidate still fails when a residual risk exceeds the organization-wide ceiling, a nonblocking finding exceeds the permitted conditional severity, a verifier lacks an allowed evidence-type role, or a review date outlasts the evidence freshness rule.

## Adoption rules

Before changing a tier or requirement, document:

1. the customer or affected-person harm being controlled;
2. why the proposed evidence is sufficient for the decision;
3. who has authority to approve the policy change;
4. whether applicable law or contracts impose a stronger requirement; and
5. when the policy will be reviewed.

Do not lower a tier simply to make an existing candidate pass. Tailoring is a governance-policy decision made before evaluating the candidate.
