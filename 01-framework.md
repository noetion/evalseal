# 01 - Evaluation framework

## 1. Scope and decision standard

This framework supports a go, conditional-go, or no-go decision for a specific version of an LLM application in a defined operating context. It evaluates the whole socio-technical system, not only the foundation model.

An approval is valid only for the recorded combination of:

- application code and configuration;
- model provider, model identifier, and relevant model snapshot or release;
- system and developer prompts;
- retrieval corpus, index, embedding model, and ranking configuration;
- tools, permissions, identities, and approval flows;
- guardrails and downstream renderers;
- intended use, users, affected groups, data classes, jurisdictions, and deployment environment.

This methodology cannot prove that a probabilistic system is error-free or secure against every future attack. It can produce traceable evidence that named requirements were met, named risks were treated or accepted by the right authority, and known limitations are monitored.

## 2. Component model

| ID | Component | Required output | Primary owner |
|---|---|---|---|
| C1 | System and threat model | Boundaries, data flows, actors, misuse cases, and threats | Security and system owner |
| C2 | Risk register | Inherent risk, treatment, residual risk, owner, and acceptance | Risk owner |
| C3 | Evaluation set | Versioned, requirement-linked cases with provenance | Evaluation owner |
| C4 | Measurement plan | Metric definitions, uncertainty, slices, thresholds, and decision rules | Evaluation owner |
| C5 | Retrieval evaluation | Retrieval coverage, ranking, authorization, and source-quality tests | Search/RAG owner |
| C6 | Model-grader protocol | Rubric, validation data, agreement results, and escalation | Evaluation owner |
| C7 | Bias and fairness assessment | Harm model, disaggregated results, uncertainty, and mitigations | Product, legal/privacy, and evaluation owners |
| C8 | Abstention and escalation policy | When to answer, clarify, refuse, defer, or route to a human | Product and risk owners |
| C9 | Prompt-injection suite | Direct and indirect attack cases across every input channel | Security owner |
| C10 | Red-team protocol | Authorization, scope, findings, severity, and retest evidence | Security owner |
| C11 | Output and tool security | Context-specific validation, authorization, isolation, and egress controls | Application owner |
| C12 | System card | Intended use, architecture, data, results, limitations, and oversight | System owner |
| C13 | Governance map | Risks, controls, owners, evidence, reviewers, and status | Governance owner |
| C14 | Evidence and audit records | Versioned decisions and risk-proportionate event records | Governance and privacy owners |
| C15 | Release gate | Automated checks plus accountable human approval where required | Release owner |
| C16 | Production monitoring | Operational, safety, security, quality, and business indicators | Operations owner |
| C17 | Feedback loop | Incident and production findings converted into requirements and tests | Product and evaluation owners |
| C18 | Incident response | Detection, containment, notification, recovery, and learning | Incident commander |

Dependencies are directional. C1 and product requirements drive C2, C3, C4, C7, C8, and C9. C15 consumes verified results from those components. C16 and C18 feed C17, which updates the threat model and evaluation set.

## 3. Measurement rules

### 3.1 Choose the measurement unit before the threshold

| Dimension | Suitable measures | Required cautions |
|---|---|---|
| Task success | Exact or schema match, execution result, SME rubric, error taxonomy | Define the unit of success and severity of errors per task |
| Retrieval | Recall@k, precision@k, MRR/nDCG, authorized-source rate, or labeled context relevance | Requires relevance labels or a validated grader; separate authorization from relevance |
| Faithfulness | Supported-claim rate, unsupported-claim rate, contradiction rate | Supplied context may itself be wrong or incomplete; faithfulness is not truth |
| Answer quality | Completeness, relevance, correctness, clarity, and actionability as separate dimensions | Avoid one opaque “quality” score |
| Citations | Citation precision, citation completeness, and source-authority checks | A syntactically valid citation can still be irrelevant or low quality |
| Abstention | Unsafe-answer rate on must-abstain cases, unnecessary-refusal rate on answerable cases, coverage-risk curve | Overall refusal rate is not a quality target |
| Security | Attack success rate by technique and impact, blocking-case pass/fail, unauthorized-action rate | Report case coverage and severity; a 0% observed rate is not proof of immunity |
| Fairness | Disaggregated task metrics, error rates, selection rates, calibration, and uncertainty | Select metrics from the harm model and legal context; no single metric proves fairness |
| Calibration | Reliability diagram, Brier score, ECE or adaptive alternatives | Use only when the system emits a probability for a defined event with outcome labels |
| Operations | p50/p95/p99 latency, error rate, token/compute use, unit cost, availability | Measure under representative load and include retries and tool calls |

### 3.2 Threshold policy

There are no universal production thresholds such as faithfulness greater than 0.85, ECE below 0.1, a 2% non-inferiority margin, or a fixed number of evaluation cases. [NIST AI RMF 1.0](https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/) states that human judgment is needed to select context-specific metrics and precise threshold values.

For every release metric, record:

1. the requirement or risk it represents;
2. the population and slices to which it applies;
3. the measurement method and its known error;
4. the minimum practically important difference or maximum tolerated failure rate;
5. sample-size or precision rationale;
6. the decision rule, including confidence interval or paired-test method where statistical inference is used;
7. the consequence of failure and who may accept residual risk.

Use three kinds of gate:

- **Blocking scenario gate:** every predeclared catastrophic or prohibited scenario must pass. Failure blocks the release even if the aggregate score is high.
- **Absolute performance gate:** the measured result must meet a risk-derived target. Use the appropriate lower or upper confidence bound when sampling or stochastic uncertainty applies; use the exact result when the evaluated cases are the full defined population and no such uncertainty applies.
- **Comparative gate:** the candidate must meet a pre-specified superiority, equivalence, or non-inferiority rule against the approved baseline on paired cases.

Do not set a safety threshold solely from the current baseline. A poor baseline does not define acceptable harm.

### 3.3 Stochastic execution

Record the number of repeats and aggregation rule for non-deterministic cases. A single successful run is insufficient where failure probability matters. Pin every available version and configuration; if a hosted model cannot be pinned, record the provider identifier and run time and treat provider updates as a change risk.

## 4. Lifecycle

### Phase A: foundation

Complete before the first production decision:

1. Define intended purpose, prohibited uses, affected people, operating environment, and success criteria.
2. Create the system/data-flow model and threat model.
3. Populate the risk register, including privacy, safety, security, fairness, operational, and misuse risks.
4. Choose risk treatments and identify release-blocking requirements.
5. Build representative, boundary, adversarial, regression, and must-abstain evaluation cases.
6. Validate human rubrics and any model grader.
7. Run a baseline for measurement planning, not to manufacture acceptable safety thresholds.
8. Establish the governance map, incident plan, monitoring plan, and evidence retention schedule.

### Phase B: per-change release evaluation

Every material change must be classified. Examples include a prompt or policy change, model change, retrieval change, new data source, tool or permission change, output renderer change, guardrail change, or change in intended use.

1. Run deterministic unit, schema, authorization, and policy checks.
2. Run the affected evaluation slices and all blocking regression cases.
3. Run the full release suite when the change can affect multiple risks or when required by policy.
4. Compare the exact candidate with the approved baseline using the predeclared decision rules.
5. Review failures, judge disagreements, flaky cases, and material uncertainty.
6. Record the decision, approver, residual risks, conditions, and rollback target.

Execution time is implementation-specific. This methodology does not prescribe one-minute or 15-minute gates.

### Phase C: production operation

1. Monitor deterministic security and operational events continuously where practicable.
2. Sample and review semantic quality at a risk-appropriate cadence, with privacy controls.
3. Detect distribution, retrieval-corpus, model, cost, and behavior changes using indicators validated for the system.
4. Trigger incident response when a threshold, prohibited event, or credible report occurs.
5. Convert confirmed failures into sanitized regression cases and update the risk assessment.
6. Reauthorize after material change or when accumulated drift invalidates the approval basis.

## 5. Production evidence gate

A system is not eligible for production approval until all required records exist and are marked **Verified** for the exact release candidate.

| Evidence | Minimum content |
|---|---|
| Scope record | Intended/prohibited uses, users, affected groups, data, jurisdictions, autonomy, and environment |
| Version manifest | Code revision, model, prompts, retrieval index, tools, policies, and dependencies |
| Threat and risk records | Boundaries, threats, inherent/residual risk, treatments, owners, and acceptance |
| Measurement plan | Metrics, slices, sample rationale, thresholds, decision rules, and grader validation |
| Evaluation report | Dated results, uncertainty, failures, reruns, and artifacts for the exact candidate |
| Security report | Authorized test scope, attack coverage, findings, remediation, and retest |
| Fairness/impact record | Applicable harms, affected groups, disaggregated results, limitations, and decisions |
| Data/privacy record | Provenance, lawful basis or authority, minimization, access, retention, and deletion |
| System card | Accurate current architecture, uses, limitations, and human oversight |
| Operational plan | Monitoring, alert ownership, rollback/kill mechanism, incident contacts, and exercises |
| Approval record | Decision, conditions, named approvers, date, expiry/review trigger, and residual risk |

Permitted decisions:

- **Approve:** all blocking criteria pass and residual risk is accepted by authorized owners.
- **Approve with conditions:** no blocking criterion fails; bounded follow-up actions, compensating controls, expiry, and owner are recorded.
- **Reject:** a blocking criterion fails, required evidence is absent, or residual risk exceeds authority or tolerance.

### Executable enforcement

The version 0.1.0 `evalseal` command operationalizes this evidence gate. It validates the candidate pack against organization-approved governance, tailoring, and change-trigger policies, then returns `APPROVE`, `CONDITIONAL`, or `REJECT` for the recorded decision. Run `preflight` before human approval and the final `gate` before deployment. See [the operating guide](docs/OPERATING_GUIDE.md).

The command verifies structure, references, hashes, freshness, authority, and decision consistency. It does not prove that a report is truthful, authenticate a person outside the file, execute an evaluation, or confirm that the deployment used the approved bytes. Protected evidence generation, authenticated approvals, CI integrity, and deployment provenance remain required.

## 6. Standards alignment

### NIST AI RMF

[NIST AI RMF 1.0](https://doi.org/10.6028/NIST.AI.100-1) is voluntary guidance with four functions: GOVERN, MAP, MEASURE, and MANAGE. Its trustworthy-AI characteristics are valid and reliable; safe; secure and resilient; accountable and transparent; explainable and interpretable; privacy-enhanced; and fair with harmful bias managed. The mappings below are interpretive, not a claim of conformity:

| AI RMF function | Methodology evidence |
|---|---|
| GOVERN | Scope, roles, policies, governance map, evidence records, and review |
| MAP | Context, affected people, system boundary, threat model, and risk register |
| MEASURE | Evaluation set, measurement plan, security/fairness testing, uncertainty, and limitations |
| MANAGE | Risk treatment, release decision, monitoring, incident response, and improvement |

The [NIST Generative AI Profile](https://doi.org/10.6028/NIST.AI.600-1) is a useful companion for generative-AI-specific risks and actions.

### OWASP and MITRE

[OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/) is used as a security risk taxonomy, not as a complete threat model or an official severity scale. [MITRE ATLAS](https://atlas.mitre.org/) is used to identify and record relevant adversary tactics and techniques. Both must be supplemented with application-specific abuse cases and conventional application-security analysis.

### ISO/IEC 42001

[ISO/IEC 42001:2023](https://www.iso.org/standard/42001) specifies requirements for establishing, implementing, maintaining, and continually improving an artificial intelligence management system. This framework supplies candidate engineering evidence but does not reproduce the standard, verify its controls, or establish certification. Use a licensed copy for clause-level mapping.

### EU AI Act

The [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj), as amended by the [2026 Digital Omnibus on AI](https://eur-lex.europa.eu/eli/reg/2026/1744/oj), has role-specific and risk-specific requirements. For systems classified as high-risk, the original Act includes risk management (Article 9), data and data governance (Article 10), technical documentation (Article 11 and Annex IV), record-keeping capability (Article 12), accuracy/robustness/cybersecurity (Article 15), and provider/deployer duties. Regulation (EU) 2026/1744 changed the application dates for Chapter III Sections 1 to 3 to 2 December 2027 for Article 6(2)/Annex III systems and 2 August 2028 for Article 6(1)/Annex I systems. Applicability and transition provisions require current legal review.

## 7. Pre-production checklist

### Scope and governance

- [ ] Intended purpose, prohibited uses, users, affected people, data, jurisdictions, and autonomy are approved.
- [ ] The exact release candidate has a version manifest.
- [ ] Every material risk has an owner, treatment, residual-risk decision, and evidence status.
- [ ] Legal, privacy, security, accessibility, and sector-specific applicability have been assessed by qualified owners.

### Evaluation

- [ ] Cases trace to requirements, risks, or incidents and cover material slices and boundaries.
- [ ] Labels and rubrics have documented provenance and review.
- [ ] Sample size or precision is justified for each decision, not copied from a generic rule.
- [ ] Model graders, if used, are validated on representative data and have human escalation rules.
- [ ] The exact candidate passed every blocking case and each statistical decision rule.
- [ ] Material failures, missing measurements, and limitations are disclosed rather than averaged away.

### Security and data

- [ ] Authorization and tool permissions are enforced outside the model and tested end to end.
- [ ] Direct and indirect prompt injection are tested across every untrusted input channel.
- [ ] Output is validated and encoded for each downstream context.
- [ ] Sensitive data cannot enter prompts, retrieval context, logs, or external providers without authority and controls.
- [ ] High-impact actions require deterministic policy checks and appropriate approval.

### Operation

- [ ] Monitoring indicators, alert thresholds, owners, and privacy controls are tested.
- [ ] Rollback, containment, and safe fallback mechanisms are exercised.
- [ ] Incident reporting and external notification duties are mapped.
- [ ] Approval names the release, conditions, expiry or review triggers, and accepted residual risks.
