# LLM Trust and Evaluation Methodology

**Publication status:** Approved as a reference methodology on 2026-07-31. See [PUBLICATION_AUDIT.md](PUBLICATION_AUDIT.md).

**Operational release:** Version 1.0.0 of the evidence schemas and release gate is approved for adoption in production governance pipelines. See [OPERATIONAL_RELEASE_AUDIT.md](OPERATIONAL_RELEASE_AUDIT.md).

**System status:** The repository contains an executable gate and a complete fictional example, but no real LLM application, real evaluation result, deployed control, monitoring system, or production approval. It therefore does not prove that any actual LLM application is ready for production.

## Purpose

This methodology helps engineering, product, security, privacy, legal, and risk teams decide whether an LLM application is ready for a defined use and operating environment. It covers six connected layers:

1. Threat modelling and risk assessment
2. Quality and task evaluation
3. Bias, fairness, calibration, and abstention
4. Security and adversarial testing
5. Governance and accountability
6. Release gates, monitoring, and incident response

The method must be tailored to the system's intended purpose, affected people, autonomy, data, jurisdictions, and potential harms. It is not a certification scheme, a substitute for legal advice, or evidence of conformity with any standard or law.

## Quick start

```powershell
python -m pip install --no-deps dist/evaluation_methodology_gate-1.0.0-py3-none-any.whl
evaluation-gate --help
```

Start with [the operating guide](docs/OPERATING_GUIDE.md). Adopt organization-owned governance, tailoring, and change policies before assessing a real candidate. The supplied example and reference policies cannot authorize a production deployment.

## Governing principles

> The model proposes. Deterministic controls and accountable people decide what the system may accept or do.

- Treat model input and output as untrusted at every security boundary.
- Enforce authorization, data access, transaction limits, and tool permissions outside the model.
- Derive evaluation coverage and release thresholds from the system's risks and requirements. Do not copy universal scores or sample sizes.
- Prefer deterministic tests and qualified human review where they can directly establish the requirement.
- Treat model-graded evaluation as a fallible measurement instrument that must be validated for the task.
- A control is not implemented until evidence shows it exists. It is not verified until a current test shows it works.

## Evidence status

Every control, test, and governance record must use one of these statuses:

| Status | Meaning | Minimum evidence |
|---|---|---|
| **Proposed** | An intention or recommendation only | Owner and target date |
| **Implemented** | The control exists in the assessed version | Code, configuration, procedure, or deployed resource |
| **Verified** | Current, scoped evidence shows the control met its acceptance criterion | Dated test or review result linked to the assessed version |
| **Ineffective** | Evidence shows the control failed or is insufficient | Finding and remediation owner |
| **Not applicable** | A documented scope decision excludes the control | Rationale and approver |
| **Retired** | The control is no longer used | Replacement or risk disposition |

Terms such as `active`, `complete`, `compliant`, and `production-ready` must not be used without a linked evidence record and an identified approver.

## Document map

| Document | Purpose |
|---|---|
| [01-framework.md](01-framework.md) | Core components, measurement rules, lifecycle, and release gate |
| [02-threat-modelling-for-llm-apps.md](02-threat-modelling-for-llm-apps.md) | System boundaries, threat analysis, OWASP and ATLAS use, and risk treatment |
| [03-golden-set-design.md](03-golden-set-design.md) | Evaluation-set design, RAG evaluation, model-graded evaluation, and statistical rules |
| [04-governance-mapping.md](04-governance-mapping.md) | Accountability, evidence status, records, release decisions, monitoring, and incidents |
| [05-security-testing.md](05-security-testing.md) | Authorized adversarial testing and deterministic security controls |
| [06-bias-and-fairness.md](06-bias-and-fairness.md) | Harm analysis, disaggregated evaluation, fairness metrics, and legal cautions |
| [SOURCE_REGISTER.md](SOURCE_REGISTER.md) | Authoritative sources and the claims they support |
| [PUBLICATION_AUDIT.md](PUBLICATION_AUDIT.md) | Final fact-check, corrections, scope limits, and sign-off |
| [OPERATIONAL_RELEASE_AUDIT.md](OPERATIONAL_RELEASE_AUDIT.md) | Implementation verification, review findings, operational sign-off, and release manifest |
| [docs/OPERATING_GUIDE.md](docs/OPERATING_GUIDE.md) | Installation, evidence workflow, preflight, final gate, and protected CI requirements |
| [docs/TAILORING_GUIDE.md](docs/TAILORING_GUIDE.md) | Risk-tier scaling and conditional evidence requirements |
| [docs/CHANGE_TRIGGERS.md](docs/CHANGE_TRIGGERS.md) | Partial, full, incident, and documentation reassessment rules |
| [docs/GOVERNANCE_SETUP.md](docs/GOVERNANCE_SETUP.md) | Real roles, authority limits, identity boundary, and separation of duties |
| [evidence-pack-template/](evidence-pack-template/README.md) | Copyable production evidence-pack structure |
| [machine-readable schemas](src/evaluation_gate/schemas/common.schema.json) | JSON Schema Draft 2020-12 contracts for policies and evidence |
| [fictional worked example](examples/fictional-support-assistant/README.md) | Completed Tier 3 example that demonstrates the whole decision flow |

## Adoption workflow

1. **Classify the system.** Document intended and prohibited uses, users and affected people, data, jurisdictions, autonomy, and worst credible harms.
2. **Model the system and threats.** Include all external models, retrieval sources, tools, identities, human decisions, and downstream renderers.
3. **Create the evidence pack.** Build requirement-linked tests, risk treatments, data records, human-review protocols, and an incident plan.
4. **Set release criteria before testing.** Define blocking scenarios, statistical decision rules, acceptable residual risk, and named approval authority.
5. **Evaluate the exact release candidate.** Record model and prompt versions, code revision, retrieval index, tool configuration, environment, and repeated-run policy.
6. **Run preflight.** Use the executable gate to identify missing, stale, inconsistent, or unauthorized evidence before asking people to approve.
7. **Make an evidence-based decision.** Approve, approve with conditions, or reject. Bind the decision to the exact evidence and candidate. A failed blocking requirement cannot be averaged away by a high overall score.
8. **Run the final gate and deploy the exact candidate.** Preserve the machine-readable gate report with the deployment record.
9. **Monitor and reassess.** Re-evaluate after material changes, incidents, drift, provider updates, evidence expiry, and changes in law or intended use.

## Standards and legal positioning

- [NIST AI RMF 1.0](https://doi.org/10.6028/NIST.AI.100-1) is voluntary, use-case agnostic guidance organized around GOVERN, MAP, MEASURE, and MANAGE. NIST [states that AI RMF 1.0 is being revised](https://www.nist.gov/itl/ai-risk-management-framework), so mappings must be reviewed when the revision is published.
- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/) supplies a risk taxonomy. OWASP does not assign the custom Critical, High, or Medium priorities that appeared in the earlier draft.
- [MITRE ATLAS](https://atlas.mitre.org/) is a living knowledge base of adversary tactics and techniques. Use stable tactic and technique identifiers in records; do not rely on a hard-coded item count.
- [ISO/IEC 42001:2023](https://www.iso.org/standard/42001) specifies requirements for an artificial intelligence management system. This methodology can support an AIMS but does not establish conformity or certification. Exact clause or Annex A mappings require access to the licensed standard and review by a qualified assessor.
- The [EU AI Act, Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj), as amended by [Regulation (EU) 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj), applies different duties according to role and risk classification. The 2026 amendment moved the application of Chapter III Sections 1 to 3 to 2 December 2027 for Annex III high-risk systems and 2 August 2028 for Article 6(1)/Annex I systems. Obtain a current applicability assessment rather than treating this repository as a compliance checklist.

## Glossary

| Term | Definition |
|---|---|
| **Evaluation set** | Versioned cases used to measure a system against specified requirements and risks. "Golden set" is used only as a familiar label, not as a claim that labels are infallible. |
| **Model-graded evaluation** | Use of a model to classify or score outputs against a rubric. It requires task-specific validation and human escalation rules. |
| **Faithfulness** | The degree to which claims in a response are supported by the supplied evidence. It is distinct from whether the evidence itself is true or complete. |
| **Retrieval quality** | The ability of a retriever to return relevant, authorized evidence with useful ranking and coverage. |
| **Non-inferiority gate** | A pre-specified statistical decision that a candidate is not worse than a baseline by more than an accepted margin. A raw score delta alone is not such a test. |
| **Abstention** | A system response that declines, defers, requests clarification, or routes to a human when the required evidence or authority is absent. |
| **Calibration** | Agreement between a declared probability and the observed frequency of the event that probability represents. |
| **Release gate** | An automated or human-controlled decision point that evaluates required evidence and blocks a release when a blocking criterion fails. |

## Maintenance

- Review external references at least every six months and after a material legal or framework update.
- Record source access dates and methodology changes in [SOURCE_REGISTER.md](SOURCE_REGISTER.md), [PUBLICATION_AUDIT.md](PUBLICATION_AUDIT.md), and [OPERATIONAL_RELEASE_AUDIT.md](OPERATIONAL_RELEASE_AUDIT.md).
- Re-run the publication audit before a major version is issued.
