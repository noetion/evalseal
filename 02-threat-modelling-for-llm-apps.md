# 02 - Threat modelling for LLM applications

## 1. Purpose

Threat modelling identifies how an LLM-enabled system could cause harm or be abused, then connects each material scenario to a treatment, owner, and verification method. The assessment must cover the whole application, including conventional application-security risks. An LLM does not replace authentication, authorization, validation, isolation, monitoring, or human accountability.

## 2. Required process

1. **Define intended and prohibited use.** Identify users, affected people, decisions, data, autonomy, deployment environment, and worst credible impacts.
2. **Draw the system and trust boundaries.** Include clients, APIs, prompts, model endpoints, retrieval stores, ingestion, tools, identities, approval services, logs, and downstream renderers.
3. **Trace data and authority.** Record where untrusted content enters, where data changes classification, which identity performs each action, and what can leave the environment.
4. **Identify threat actors and accidental failure sources.** Include malicious and curious users, compromised content suppliers, insiders, supply-chain actors, model/provider failures, operator mistakes, and unsafe normal use.
5. **Enumerate misuse and failure scenarios.** Use application requirements, [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/), conventional AppSec analysis, privacy/impact assessment, and relevant [MITRE ATLAS](https://atlas.mitre.org/) techniques.
6. **Estimate inherent risk.** Use the local scoring method and state the assumptions and evidence.
7. **Choose treatment.** Avoid, mitigate, transfer/share, or accept. Risk acceptance requires named authority and expiry or review criteria.
8. **Define verification.** Link each control to one or more deterministic, model-behavior, human-review, operational, or adversarial tests.
9. **Estimate residual risk.** Do not mark a risk mitigated until the control is implemented and verified.
10. **Review on change.** Reassess after architecture, model, data, tool, permission, use, provider, incident, or regulatory changes.

Dependencies that are outside the team's assessment authority, such as a cloud or identity provider, remain inside the system model. Record them as inherited controls, assumptions, and supplier risks rather than omitting them.

## 3. OWASP LLM Top 10 2025 mapping

OWASP's 2025 list is a risk taxonomy. It does not provide official Critical, High, or Medium labels for each entry. Assign severity from the application's actual impact and exposure.

| Ref | OWASP risk | Example application scenario | Primary control themes | Verification examples |
|---|---|---|---|---|
| LLM01 | Prompt Injection | User or retrieved content changes behavior, causes disclosure, or triggers a tool | Minimize authority; segregate untrusted content; validate tool intent and arguments; require approval for high-impact actions; monitor | Direct/indirect, multilingual, encoded, multimodal, and multi-turn cases against the full application |
| LLM02 | Sensitive Information Disclosure | The system exposes personal, tenant, confidential, or training/context data | Data minimization; retrieval authorization; context scoping; secrets exclusion; output controls; provider/data agreements | Cross-user/tenant tests, canaries, policy-boundary tests, and log review |
| LLM03 | Supply Chain | A model, package, adapter, dataset, prompt asset, or service is compromised or changes unexpectedly | Inventory/SBOM; provenance; signatures/hashes; version pinning; supplier review; update testing | Dependency and artifact checks, change detection, rollback exercise |
| LLM04 | Data and Model Poisoning | Malicious or low-quality content influences training, fine-tuning, retrieval, or feedback loops | Ingestion authorization; provenance; review/quarantine; anomaly detection; trusted-source ranking; rollback | Poisoned-source tests, provenance checks, index rebuild and recovery tests |
| LLM05 | Improper Output Handling | Generated HTML, Markdown, URLs, SQL, paths, code, or tool arguments reach an interpreter unsafely | Context-aware encoding; strict schema and allowlists; parameterization; least privilege; isolation; safe rendering | XSS/URL/path/SQL/command cases at the downstream sink, not only model-output inspection |
| LLM06 | Excessive Agency | An agent has unnecessary functions, permissions, or autonomy | Minimize tools and permissions; user-context credentials; deterministic authorization; bounded transactions; approval and idempotency | Unauthorized and high-impact action attempts, confused-deputy tests, replay and rollback tests |
| LLM07 | System Prompt Leakage | A prompt contains secrets or reveals controls that were assumed to be hidden | Do not put secrets in prompts; do not use prompt secrecy as a security boundary; enforce policy outside the model | Secret scanning and tests showing disclosed prompt text cannot bypass authorization |
| LLM08 | Vector and Embedding Weaknesses | Cross-tenant retrieval, unauthorized chunks, ranking manipulation, or embedding/index attacks | Access filtering before retrieval; namespace isolation; source provenance; index validation; ingestion quotas | Tenant-isolation, authorization, collision/manipulation, and stale-index tests |
| LLM09 | Misinformation | Unsupported, incorrect, fabricated, or misleading output affects a user or decision | Authoritative sources; claim/citation checks; uncertainty and abstention; qualified review for consequential use | Known-answer, unanswerable, conflicting-source, temporal, and high-impact cases |
| LLM10 | Unbounded Consumption | Long contexts, repeated generation, recursive tools, or expensive queries exhaust resources | Authentication; quotas; rate/size/time/tool-step limits; budgets; circuit breakers; caching where safe | Boundary, concurrency, retry-loop, recursive-tool, and cost-amplification tests |

Important control limits:

- API roles, delimiters, instruction wording, classifiers, and filters can reduce risk but do not create an authorization boundary.
- A standard refusal is not the universal success response. Safe success may be to ignore an injected instruction and complete the authorized task.
- Retrieval-augmented generation and fine-tuning do not eliminate prompt injection. [OWASP LLM01](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) recommends layered impact reduction.
- The system prompt must not contain secrets or act as a security control. [OWASP LLM07](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/) explicitly makes this distinction.
- For agentic systems, limit functionality, permissions, and autonomy independently. [OWASP LLM06](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) recommends least privilege and approval for high-impact actions.

## 4. MITRE ATLAS use

[MITRE ATLAS](https://atlas.mitre.org/) is a living knowledge base modeled after MITRE ATT&CK. Use it to describe plausible adversary behavior, build multi-step attack paths, and select mitigations. Record stable tactic and technique identifiers plus an access date. Do not make coverage claims from a hard-coded count because the matrix changes.

Use an attack path when a harmful outcome requires multiple preconditions. Example:

```text
Goal: exfiltrate another user's retrieved content
  1. Place malicious instructions in a source the target can retrieve
  2. Cause the target application to retrieve that source
  3. Influence the model to include protected context in an outbound request
  4. Reach an attacker-controlled destination through a renderer or tool
```

Tests must cover the controls at every step: source authorization, retrieval isolation, tool/renderer egress, output validation, and monitoring. Blocking only the phrasing used in one injected document is not sufficient.

Attack trees are useful for complex chains but are not automatically mandatory for every application. The threat-model owner records why a table, data-flow analysis, attack tree, or combination is adequate.

## 5. Risk scoring

The following 5 by 5 scheme is an internal default, not an industry standard. Replace it if the organization has an established method.

### Likelihood

| Score | Meaning |
|---|---|
| 1 | Rare under the defined exposure and assumptions |
| 2 | Unlikely but plausible |
| 3 | Possible with known techniques or normal failure conditions |
| 4 | Likely given exposure, attacker capability, or observed failures |
| 5 | Expected or repeatedly observed without additional controls |

### Impact

| Score | Meaning |
|---|---|
| 1 | Negligible and readily reversible effect |
| 2 | Limited, reversible effect on a small scope |
| 3 | Material operational, financial, privacy, or user harm |
| 4 | Major harm, reportable event, or broad compromise |
| 5 | Severe or potentially irreversible harm, systemic compromise, or threat to life/safety |

`Inherent score = likelihood × impact` before planned controls. `Residual score` is reassessed only after implemented controls have evidence.

| Score | Default band | Default action |
|---|---|---|
| 1-4 | Low | Monitor or accept within delegated authority |
| 5-9 | Medium | Treat or explicitly accept with owner and review date |
| 10-16 | High | Treat before release or escalate to designated risk authority |
| 17-25 | Critical | Block release unless the organization's highest applicable authority permits a documented exception and no law or policy prohibits acceptance |

The score does not replace qualitative analysis. Record affected people, scale, duration, reversibility, detectability, legal duties, and uncertainty. Catastrophic low-likelihood scenarios can be release-blocking regardless of the numeric band.

## 6. Templates

### Threat record

| Field | Required content |
|---|---|
| Threat ID | Stable local identifier |
| Scenario | Actor/failure, precondition, action, asset, and impact |
| External references | OWASP, ATLAS, conventional CWE/CAPEC, or legal/impact reference where relevant |
| Affected components and people | System scope and population |
| Inherent likelihood/impact | Scores, rationale, and evidence |
| Treatment | Avoid, mitigate, transfer/share, or accept |
| Controls | Specific controls and owners |
| Verification | Case IDs, procedure, environment, and acceptance criteria |
| Status | Proposed, Implemented, Verified, Ineffective, Not applicable, or Retired |
| Residual risk | Reassessment, uncertainty, acceptor, and review trigger |

### Governance-ready risk register

| Risk ID | Threat IDs | Risk statement | Inherent risk | Treatment | Control owner | Evidence | Status | Residual risk | Risk acceptor | Review trigger |
|---|---|---|---|---|---|---|---|---|---|---|
| R-EXAMPLE-01 | T-EXAMPLE-01 | Hypothetical cross-tenant retrieval could disclose another tenant's document | High | Mitigate | Application security role | None: example only | Proposed | Not assessed | Unassigned | Before first release |

The row is illustrative. It is not evidence that a control exists.

## 7. Worked example: hypothetical document Q&A system

**Example status:** Proposed design only. No implementation or test result is claimed.

| Threat | Inherent risk | Proposed treatment | Required verification before “Verified” |
|---|---|---|---|
| Direct injection changes answer policy | Medium | Task-bound prompt plus deterministic policy checks | Representative attacks show no prohibited output or action across repeated runs |
| Uploaded document contains indirect injection | High | Quarantine and provenance on ingestion; isolate document text; no tool authority from retrieved content | Poisoned documents across supported formats cannot trigger unauthorized tools or disclosure |
| Cross-tenant retrieval | Critical | Authorization filter enforced before retrieval using caller identity | Deterministic tests prove zero unauthorized chunks for every role/tenant boundary |
| Unsupported answer | High | Source requirement, claim checks, and abstention/escalation | Unanswerable/conflicting cases meet predeclared unsafe-answer and over-refusal bounds |
| Generated link exfiltrates context | High | Allowlisted link handling; no automatic remote fetch; egress restriction | Crafted Markdown/HTML cannot cause unauthorized outbound requests |
| Resource exhaustion | Medium | Request, token, tool-step, time, and concurrency limits | Boundary and load tests show bounded cost and graceful failure |

## 8. Review checklist

- [ ] The diagram includes every external model, data source, tool, identity, renderer, log store, and human decision.
- [ ] Untrusted inputs include retrieved files, web content, tool results, messages, memory, multimodal content, and metadata.
- [ ] Authorization is enforced before data or actions are exposed to the model.
- [ ] Prompt text and hidden model behavior are not treated as security boundaries.
- [ ] Every material threat has a treatment, owner, test, status, and residual-risk decision.
- [ ] Conventional AppSec, privacy, safety, misuse, and operational failure modes are included.
- [ ] Supplier and inherited controls have evidence or explicit assumptions.
- [ ] The model is updated after material change, incident, or new threat intelligence.
