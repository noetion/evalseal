# 04 - Governance, evidence, release, and operation

## 1. Purpose

Governance connects each material risk and requirement to a decision-maker, a control owner, current evidence, and an escalation path. The model is a component. Accountability remains with the people and organization that design, provide, deploy, and operate the system.

This document supplies templates. Every example is hypothetical and has status **Proposed** unless linked evidence proves otherwise.

## 2. Roles and separation of duties

Assign roles by name or accountable organizational position:

| Role | Accountability |
|---|---|
| System owner | Intended purpose, scope, resources, and overall lifecycle decision |
| Risk owner | Understands a risk and ensures it is treated or escalated |
| Control owner | Implements and maintains a specific control |
| Evaluation owner | Maintains cases, metrics, evaluator validation, and reports |
| Data/privacy owner | Data authority, minimization, access, retention, and rights processes |
| Security owner | Threat model, security verification, red-team authorization, and remediation |
| Release authority | Makes the go, conditional-go, or no-go decision within delegated authority |
| Risk acceptor | Accepts stated residual risk within a documented mandate |
| Independent reviewer | Challenges evidence and conflicts of interest for high-impact decisions |
| Incident commander | Coordinates containment, notification, recovery, and post-incident work |

The same person may hold multiple roles in a small team, but conflicts and compensating review must be documented. A control owner should not be the sole verifier of a high-impact control.

## 3. Governance map

Every material risk, including low-likelihood catastrophic risks, must appear in the governance map or have a recorded rationale for exclusion.

For executable use, adopt an organization-owned [governance configuration](config/governance.example.json) containing real active actors, approval roles, risk-acceptance limits, separation rules, and policy review dates. The supplied file is a template and cannot authorize production until it is tailored, approved, and protected by the organization. See [governance setup](docs/GOVERNANCE_SETUP.md).

| Field | Required content |
|---|---|
| Risk ID and statement | Cause, event, affected asset/person, and impact |
| Applicability | Use, population, data, environment, and jurisdiction |
| Inherent risk | Rating, rationale, evidence, and uncertainty |
| Treatment | Avoid, mitigate, transfer/share, or accept |
| Control | Specific technical, administrative, contractual, or human measure |
| Control owner | Named accountable person/role |
| Status | Proposed, Implemented, Verified, Ineffective, Not applicable, or Retired |
| Evidence | Immutable identifier or URI for code/config/procedure and current test result |
| Reviewer and date | Who verified the evidence and when |
| Residual risk | Rating and rationale after verified controls |
| Risk acceptor | Named authority and date |
| Conditions and trigger | Expiry, monitoring, reassessment, or rollback condition |

Example only:

| Risk ID | Risk | Treatment/control | Owner | Evidence | Status | Residual risk |
|---|---|---|---|---|---|---|
| R-EXAMPLE-01 | Cross-tenant retrieval could disclose another tenant's document | Enforce caller authorization before vector search; reject unscoped queries | Application security role | None | Proposed | Not assessed |

Do not mark a control `Active` based on its appearance in a design. The minimum valid progression is Proposed to Implemented to Verified.

## 4. System card

A system card is a transparency and decision artifact. It may support governance or technical documentation, but it is not by itself proof of compliance with [ISO/IEC 42001](https://www.iso.org/standard/42001) or the [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj).

### Required sections

1. **Identity:** name, owner, version, release date, and version manifest.
2. **Purpose:** intended uses, prohibited uses, users, affected people, jurisdictions, and operating environment.
3. **Architecture:** models, prompts, retrieval, data, tools, permissions, guardrails, renderers, human decisions, and suppliers.
4. **Data:** source, provenance, authority, quality limits, update cadence, privacy class, and retention.
5. **Evaluation:** case-set version, metrics, thresholds, uncertainty, grader validation, slices, and exact report links.
6. **Security:** threat-model version, material findings, verified controls, and unresolved residual risks.
7. **Fairness and impact:** affected groups, harm analysis, metrics, results, uncertainty, and mitigations.
8. **Human oversight:** who can intervene, information and training provided, time available, and evidence that oversight is meaningful.
9. **Limitations:** known failures, unsupported tasks, model/provider dependencies, and monitoring blind spots.
10. **Operation:** monitoring, incident reporting, safe fallback, rollback, change triggers, and next review.
11. **Approval:** decision, named approvers, conditions, residual-risk acceptors, and expiry/review triggers.

Use `Not evaluated` or `Evidence unavailable` rather than inventing a metric or placeholder result. Example percentages must be visibly labeled hypothetical and must never appear in a real system card.

## 5. Evidence and event records

### 5.1 Evidence record

Each control or release decision should link to:

- the exact system/version assessed;
- evidence type and location;
- collection method and environment;
- result, exclusions, and uncertainty;
- verifier, date, and tool/version;
- retention and access classification; and
- expiry or invalidation trigger.

### 5.2 Event logging

Log only fields required for defined security, safety, operational, contractual, or legal purposes. Raw prompts, retrieved chunks, model outputs, and chain-of-thought are not universally mandatory and can create privacy, confidentiality, and security risk.

Candidate event fields:

| Field | Use | Handling note |
|---|---|---|
| `trace_id`, event time, event type | Correlation and chronology | Use synchronized clocks and stable IDs |
| system/model/prompt/index/tool versions | Reproduce behavior | Prefer hashes or deployment manifest references |
| pseudonymous actor/session and authorization context | Investigate access and actions | Avoid direct identifiers unless necessary and authorized |
| input/output classification or safe digest | Investigate content-related events | Store full content only when required and protected |
| retrieved source IDs and authorization decision | RAG traceability | Full chunk content may be unnecessary |
| tool name, normalized arguments, approval, and result | Agent accountability | Redact secrets and sensitive payloads |
| policy/guardrail decisions | Safety and security analysis | Record policy version |
| latency, usage, retries, and error class | Reliability and cost | Include end-to-end and component timings where useful |
| evaluation result and evaluator version | Offline/online quality evidence | Separate model-graded signal from verified fact |

Apply data minimization, purpose limitation, access control, encryption, integrity protection, monitoring, retention limits, and deletion. Use append-only or tamper-evident storage where the threat model or applicable rule requires it. “Immutable” is not a universal logging requirement and can conflict with data-erasure or minimization duties if designed carelessly.

### 5.3 Retention

Set retention from purpose, applicable law, contracts, limitation periods, incident needs, and data-protection principles. Do not use a generic 12-month or three-year rule.

For providers of high-risk systems within scope, Article 18 of the [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) requires specified technical and conformity documentation to remain available for 10 years after the system is placed on the market or put into service. Articles 19 and 26(6) set a minimum of six months for automatically generated logs under provider or deployer control, unless other applicable Union or national law provides otherwise. These are distinct records and duties. The [2026 amendment](https://eur-lex.europa.eu/eli/reg/2026/1744/oj) changed relevant application dates. Obtain a current role and applicability assessment before relying on these periods.

## 6. Data governance

For each evaluation and monitoring dataset record:

- source and provenance;
- collection purpose and legal/contractual authority;
- license and permitted uses;
- privacy and confidentiality classification;
- representativeness and known gaps;
- annotation process and quality checks;
- transformations, de-identification, and residual re-identification risk;
- approved providers and transfer locations;
- access, retention, deletion, and incident handling; and
- dataset/version hash and owner.

Synthetic data must be labeled as synthetic and reviewed for realism, leakage, stereotype amplification, and coverage gaps. Authorized, minimized real data may be needed for representativeness. “Synthetic only” is not a general compliance requirement.

## 7. Release gate

### 7.1 Layers

| Gate | Purpose | Typical contents | Required result |
|---|---|---|---|
| Deterministic | Fast direct checks | Unit/schema tests, authorization, policy rules, static/dependency checks, side-effect guards | All blocking checks pass |
| Behavioral | System behavior on versioned cases | Task, RAG, abstention, security, fairness, tool-use, and regression tests | Predeclared decision rules pass |
| Assurance | Accountable review | Evidence completeness, legal/privacy/security review, residual risk, operational readiness | Authorized approval recorded |

Do not prescribe universal run times or a three-release warning period. New metrics can be non-blocking only when the risk owner documents why, how long, and what compensating decision evidence remains.

### 7.2 Decision record

```yaml
release_decision:
  candidate_manifest: "sha256:..."
  evaluation_report: "evidence://..."
  security_report: "evidence://..."
  fairness_impact_record: "evidence://..."
  decision: "approve | approve_with_conditions | reject"
  blocking_failures: []
  conditions: []
  residual_risks:
    - risk_id: "R-..."
      acceptor: "named-role"
      expires: "YYYY-MM-DD"
  approvers:
    - role: "release-authority"
      identity: "..."
      decided_at: "..."
  rollback_target: "manifest://..."
  next_review_trigger: "..."
```

## 8. Incident response

Severity and response targets are organizational policy, not universal facts. Define them from harm, affected scope, legal/contractual notification windows, reversibility, and current exposure.

| Severity | Example decision rule | Required response |
|---|---|---|
| Critical | Ongoing or credible imminent severe harm, major unauthorized action, or broad sensitive-data exposure | Immediate command, containment, evidence preservation, and notification assessment |
| High | Material harm or exploit with limited scope or effective containment | Urgent owner assignment, containment, impact analysis, and executive/risk notification |
| Medium | Degraded control or bounded failure without current material harm | Planned remediation with deadline and monitoring |
| Low | Minor issue with low impact and established workaround | Backlog and trend review |

### Workflow

1. Detect and preserve relevant evidence under the data policy.
2. Triage impact, scope, affected people, current exploitability, and notification duties.
3. Contain with the safest available mechanism: disable a tool/feature, restrict traffic, revoke credentials, isolate data, roll back, or switch to a validated safe fallback.
4. Communicate through the approved incident and regulatory paths.
5. Remove the root cause and verify the fix against the exploit and adjacent variants.
6. Recover gradually with heightened monitoring.
7. Complete a blameless post-incident review, update risks and cases, and track corrective actions.

A smaller model is not automatically a safer fallback. Every fallback must have its own approved behavior and permissions.

## 9. Monitoring

Select indicators from the threat model and product requirements. Values below are categories, not universal thresholds:

| Category | Candidate indicators |
|---|---|
| Security | Unauthorized-action attempts/successes, cross-tenant retrieval, injection signals, egress, unusual tool chains |
| Safety/quality | Confirmed unsupported claims, high-severity policy failures, escalation accuracy, complaint themes |
| Fairness/impact | Disaggregated error/selection/service rates with privacy-protected support counts and uncertainty |
| Retrieval/data | Source authorization, freshness, coverage, failed ingestion, corpus/index version drift |
| Operations | Availability, errors, p95/p99 latency, retries, token/compute use, cost, rate-limit events |
| Model/evaluator | Provider/version changes, score distribution, grader disagreement, invalid-output rate |

For each alert define the measurement window, baseline, seasonality, minimum support, threshold rationale, owner, playbook, privacy control, and false-alert review. A raw embedding-distance value such as 0.1, a 5% thumbs-down rate, or a 1.5-second p95 is not portable across systems.

## 10. Compliance positioning

| Source | Verified statement | Methodology use and limit |
|---|---|---|
| [NIST AI RMF 1.0](https://doi.org/10.6028/NIST.AI.100-1) | Voluntary framework with GOVERN, MAP, MEASURE, MANAGE | Structures risk work; mapping is not certification |
| [ISO/IEC 42001:2023](https://www.iso.org/standard/42001) | Requirements for an AI management system | Supports an AIMS; exact clause/Annex A mapping requires the licensed standard |
| [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) | Role- and risk-specific duties, including high-risk risk management, data governance, technical documentation, logging capability, and provider/deployer obligations | Requires applicability analysis; this repository is not a conformity checklist |
| [Regulation (EU) 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj) | Amends the AI Act and delays Chapter III Sections 1-3 for relevant high-risk categories | Use amended dates and current consolidated law |

Avoid unverified ISO subclause mappings. The previous draft incorrectly mapped AI risk assessment to Annex A.4 and incident management to Annex A.8 as if those labels alone established conformity.

## 11. Governance approval checklist

- [ ] Scope, intended/prohibited uses, affected people, roles, data, and jurisdictions are current.
- [ ] All material risks have owners, treatments, verification, residual-risk decisions, and review triggers.
- [ ] Control status is evidence-based; no proposed example is labeled implemented or active.
- [ ] Evaluation, security, privacy/data, fairness/impact, and operational evidence refer to the exact candidate.
- [ ] Logging is purpose-limited and tested for access, integrity, retention, and deletion.
- [ ] Incident containment and rollback mechanisms are exercised.
- [ ] Legal and standards claims are reviewed against current primary text and system applicability.
- [ ] The decision, conditions, approvers, risk acceptors, and expiry/review triggers are recorded.
