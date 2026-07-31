# 05 - Security and adversarial testing

## 1. Scope and authorization

Security testing must be authorized in writing and limited to named systems, environments, identities, data, dates, and techniques. Rules of engagement must prohibit unintended production effects, attacks on third-party services, collection of real secrets, and persistence outside the test environment unless separately authorized.

Use staging or an isolated test tenant with production-equivalent controls. If production testing is necessary, obtain explicit authority, define stop conditions, protect users and data, and coordinate incident response. Generated payloads, transcripts, and findings are sensitive security data.

This methodology tests the application boundary, not just the model endpoint.

## 2. Test objectives

Map each objective to the threat model and a measurable impact:

- alter intended behavior through direct or indirect prompt injection;
- bypass safety or use-policy controls;
- access or disclose unauthorized information;
- influence retrieval through poisoned or manipulated content;
- cause unauthorized or high-impact tool actions;
- exploit generated output at a downstream interpreter;
- cross user, tenant, role, or session boundaries;
- exhaust compute, token, storage, tool, or financial resources;
- exploit supply-chain or configuration changes; and
- evade detection, approval, or audit controls.

## 3. Prompt injection and jailbreak testing

[OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) distinguishes the risk of inputs changing behavior or output in unintended ways and notes that no foolproof prevention is known. Treat jailbreaks that target model safety behavior and prompt injection that subverts application instructions as related but distinct test intents.

### Coverage axes

| Axis | Examples |
|---|---|
| Source | User message, document, website, email, tool result, memory, metadata, image, audio |
| Delivery | Direct, indirect, multi-turn, nested, quoted, translated, encoded, Unicode-obfuscated |
| Objective | Policy bypass, prompt/context disclosure, unauthorized data, tool use, transaction, egress, misinformation |
| State | Fresh session, long context, prior authorization, role change, tool failure, retry |
| Target | Main model, router, grader, summarizer, query rewriter, retrieval/index pipeline, downstream agent |
| Outcome | Refusal, safe completion, escalation, blocked action, disclosure, side effect, cost amplification |

No universal minimum number of 30 cases proves adequate coverage. Select techniques from the threat model, vary them, run sufficient repetitions for stochastic behavior, and protect a release set from routine tuning.

### Pass criteria

Define observable safe outcomes before execution. Depending on the task, pass can mean:

- complete the authorized task while ignoring the injected instruction;
- refuse or clarify when the requested task itself is prohibited or ambiguous;
- prevent unauthorized data from entering model context;
- reject or require approval for an action at the deterministic tool boundary;
- prevent outbound requests or executable rendering; and
- emit an alert without exposing sensitive content.

Model text that says “I refuse” is not sufficient if a tool call, retrieval, egress, or downstream side effect still occurs. Conversely, a harmless system-prompt paraphrase is not automatically a security failure if prompts contain no secrets and external controls remain effective.

## 4. Defense-in-depth verification

Test controls independently and end to end.

| Boundary | Required control themes | Verification |
|---|---|---|
| Ingestion | Authenticated source, provenance, type/size limits, malware/content handling, quarantine, review | Unauthorized/poisoned items cannot enter trusted corpus; rollback works |
| Context assembly | Caller authorization, tenant isolation, data minimization, trust labels, token budget | No unauthorized item reaches model context |
| Prompt/model | Task constraint, untrusted-content separation, robust parsing | Behavior tests across attack variants; not relied on for authorization |
| Tool broker | Allowlisted narrow functions, strict schema, caller-context authorization, limits, idempotency | Invalid, unauthorized, replayed, and high-impact actions are blocked or approved |
| Human approval | Clear actor, action, target, data, consequence, and expiry | Approver can detect manipulation; stale or altered actions require reapproval |
| Output sink | Context-aware encoding, safe URL handling, schema/AST validation, no implicit execution | Payload reaches the real renderer/interpreter safely |
| Runtime | Isolation, secrets management, egress controls, resource limits, monitoring | Sandbox escape/egress and resource-boundary tests appropriate to the platform |

Prompt roles, delimiters, and input classifiers are helpful layers but not security boundaries. Filtering cannot enumerate every semantic attack. Authorization and side-effect policy must be deterministic and auditable.

## 5. Red-team protocol

### Plan

Record:

- authorization and sponsor;
- exact target manifest and environment;
- in-scope and out-of-scope assets, providers, users, and data;
- threat actors, objectives, and relevant OWASP/ATLAS references;
- test identities and permitted privileges;
- allowed automation, rate, concurrency, and cost;
- data handling, retention, and disclosure rules;
- monitoring coordination and whether defenders are informed;
- stop conditions, emergency contacts, cleanup, and rollback; and
- severity and retest criteria.

### Execute

1. Verify target identity, isolation, test data, backups, and stop mechanism.
2. Run deterministic boundary tests before adaptive attacks.
3. Run automated probes with rate/cost limits and versioned configurations.
4. Conduct manual, application-specific and multi-step attacks.
5. Capture reproducible evidence, including non-text side effects and authorization decisions.
6. Stop and escalate on unexpected production impact, real sensitive data, third-party effect, or scope ambiguity.
7. Remove test artifacts and revoke test credentials.

### Findings

| Field | Content |
|---|---|
| Finding ID/title | Stable identifier and concise outcome |
| Target manifest | Exact system and environment |
| Preconditions and attack path | Required access, content, state, and steps |
| Observed evidence | Output, tool trace, network/event record, and repetitions |
| Impact and affected scope | Confidentiality, integrity, availability, safety, privacy, cost, and users |
| Likelihood/exploitability | Assumptions, repeatability, and required capability |
| Severity | Local method and rationale |
| Root cause/control gap | Boundary that failed, not only the adversarial wording |
| Remediation | Smallest control change that addresses the cause |
| Status and owner | Open, remediating, risk accepted, or verified fixed |
| Retest | Exact cases, adjacent variants, date, and evidence |

Do not recommend “sanitize all text before the LLM” as a complete fix for semantic prompt injection. Remediation must limit the impact through authorization, isolation, tool design, egress control, and verified behavior.

## 6. Output and tool security

[OWASP LLM05:2025](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/) describes risks from passing model output to downstream components without suitable validation, encoding, and handling.

### Browser and document rendering

- Escape or sanitize for the exact HTML/Markdown context with a maintained library.
- Disable raw HTML unless required and reviewed.
- Allowlist URL schemes and destinations; control link previews, image fetching, and server-side fetches.
- Apply Content Security Policy as an additional browser control, not a substitute for encoding.

### Structured output and tools

- Validate against a closed schema with length, type, range, enum, and unknown-field rejection.
- Recompute authorization from authenticated user and server-side state. Never trust a model-supplied user, tenant, price, permission, or approval flag.
- Use narrow functions instead of open-ended shell, URL-fetch, SQL, or file-system tools.
- Show high-impact actions to an approver in human-readable form and bind approval to the exact normalized action.

### SQL, code, paths, and templates

- Prefer fixed queries or a constrained query builder. Parameterized values do not make arbitrary model-generated SQL structure safe.
- If generated queries are allowed, parse and allowlist the AST, use a read-only least-privilege identity where possible, bound cost/rows/time, and test on isolated data.
- Do not execute generated code in the application's primary environment. Use a hardened, ephemeral isolation boundary with no ambient credentials, explicit egress policy, resource limits, and teardown. A default container alone is not a complete sandbox guarantee.
- Normalize and constrain paths to an approved root; reject traversal, devices, links, and unsafe archive behavior.
- Escape content for email, logs, templates, and command contexts separately.

## 7. Data leakage and boundary tests

- Verify authorization before retrieval and again before returning sensitive data.
- Test cross-user, cross-tenant, role downgrade, stale session, shared cache, conversation memory, and background-job boundaries.
- Keep secrets, credentials, and authorization policy out of prompts. [OWASP LLM07:2025](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/) states that system prompts should not be treated as secret or as security controls.
- Use synthetic canaries or approved test records to detect leakage. Do not probe a provider for real personal or proprietary training data without explicit legal and security authorization.
- Validate that logs, traces, graders, analytics, and support tools do not become secondary leakage paths.
- Regex and named-entity recognition can aid detection but have false negatives and positives. They do not replace data minimization or authorization.

## 8. Resource and availability tests

Test:

- input and context size limits;
- output-token and wall-clock limits;
- recursion and tool-step limits;
- retry storms and partial dependency failure;
- concurrency and per-user/tenant quotas;
- expensive search/query patterns;
- cache isolation and amplification; and
- budget alerts, circuit breakers, and graceful degradation.

Record end-to-end cost and side effects, not only model token count.

## 9. Tooling

Tools accelerate coverage but do not prove security. Pin versions, review data sent to providers, validate detectors, and keep manual application-specific testing.

| Tool | Verified scope | Primary source |
|---|---|---|
| Garak | Open-source probes and detectors for undesirable LLM/dialog-system behavior | [NVIDIA/garak](https://github.com/NVIDIA/garak) |
| PyRIT | Open-source framework for security risk identification and red teaming of generative-AI systems | [microsoft/PyRIT](https://github.com/microsoft/PyRIT) |
| Promptfoo | Evaluation, red-team, and CI/CD workflows for prompts and LLM applications | [Promptfoo red-team guide](https://www.promptfoo.dev/docs/red-team/) and [CI/CD guide](https://www.promptfoo.dev/docs/integrations/ci-cd/) |

Tool findings require validation. A detector pass can be wrong, a generated attack may be invalid, and unsupported application paths require custom harnesses.

## 10. Release checklist

- [ ] Written authorization and rules of engagement cover the executed tests.
- [ ] The exact release candidate and production-equivalent permissions were tested.
- [ ] All untrusted input channels and high-impact outcomes have mapped cases.
- [ ] Authorization, tenant isolation, egress, rendering, and tool side effects were verified at deterministic boundaries.
- [ ] Direct and indirect injection, multi-turn, encoding, and application-specific attacks were included.
- [ ] No secrets or security-critical policy depend on system-prompt confidentiality.
- [ ] Blocking findings are fixed and retested; accepted residual risks name the authorized acceptor and expiry.
- [ ] Test data and artifacts are secured, cleaned up, and retained only as authorized.
- [ ] Monitoring and incident playbooks cover the tested failure modes.
