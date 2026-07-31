# 06 - Bias, fairness, and impact evaluation

## 1. Scope

Fairness is a socio-technical property of a system and its use. A model can have equal aggregate accuracy yet produce unequal errors, access, service quality, allocation, stereotyping, or downstream harm. No single metric establishes that a system is fair or lawful.

Before choosing a metric, document:

- who uses the system and who is affected;
- the decision, service, content, or resource influenced;
- beneficial and harmful outcomes for each group;
- relevant protected characteristics and intersectional groups by jurisdiction and context;
- whether the system is decision support or makes a decision, and whether human review is meaningful;
- the source and validity of outcome labels; and
- which disparities are unacceptable and who has authority to decide.

Involve domain experts, legal/privacy owners, accessibility expertise, and representatives of affected people in proportion to impact.

## 2. Legal positioning

This methodology is not legal advice. Applicability depends on role, system classification, sector, jurisdiction, data, and use.

- The [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) includes data-governance and bias-related requirements for high-risk systems that use techniques involving model training with data, including Article 10 requirements concerning relevant, sufficiently representative, and, to the best extent possible, error-free and complete training, validation, and test data for the intended purpose, plus examination of certain biases. These duties do not apply identically to every high-risk system or every LLM application. [Regulation (EU) 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj) changed the application dates for the relevant high-risk provisions.
- Section 19 of the [UK Equality Act 2010](https://www.legislation.gov.uk/ukpga/2010/15/section/19) defines indirect discrimination through a provision, criterion, or practice that creates particular disadvantage and cannot be shown to be a proportionate means of achieving a legitimate aim. It is not an AI-specific ban on automated decisions.
- UK data-protection rules for automated decision-making changed under the Data (Use and Access) Act 2025. Use current [ICO automated-decision guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/rights-related-to-automated-decision-making-including-profiling/) and legal review rather than relying on an older summary of Article 22.
- In US employment selection, the four-fifths rule in [29 CFR 1607.4(D)](https://www.ecfr.gov/current/title-29/subtitle-B/chapter-XIV/part-1607/section-1607.4) is a rule of thumb for evidence of adverse impact. A ratio below 0.8 is not automatically a finding of unlawful discrimination, and a ratio above 0.8 is not a fairness or legal safe harbor. It is not a general threshold for lending or every “financial use case.”

## 3. Harm and bias model

Assess failure across the lifecycle:

| Stage | Example source | Example impact |
|---|---|---|
| Problem framing | Objective excludes an affected group's needs | Service optimized for majority users only |
| Data collection | Under-coverage, historical discrimination, or proxy features | Lower performance or unequal allocation |
| Labeling/measurement | Labels encode subjective or unequal past decisions | Model reproduces invalid ground truth |
| Modeling | Aggregate optimization hides subgroup errors | Different false-negative rates |
| Evaluation | Test set omits languages, disabilities, or intersections | Release evidence misses material failures |
| Deployment | Users or context differ from the assessed setting | Performance and access degrade in practice |
| Human interaction | Automation bias, poor explanation, inaccessible appeal | Human review becomes a rubber stamp |
| Feedback loop | Model outputs influence future labels/data | Existing disparity compounds over time |
| Model grading | Position, verbosity, or self-enhancement bias | Evaluation favors a system for irrelevant reasons |

Also assess representational harms such as stereotyping, denigration, erasure, and unequal quality even when the system does not produce a binary decision.

## 4. Metric selection

Use metrics that correspond to the identified harm. Report base rates, group support, point estimates, uncertainty, and the task metric from which each disparity is derived.

| Metric | Definition | Suitable question | Limitation |
|---|---|---|---|
| Selection-rate difference/ratio | Compare $P(\hat{Y}=1 \mid A=a)$ across groups | Are favorable outcomes allocated at different rates? | Does not account for label validity or qualifications |
| Demographic parity | Equal selection rates across groups | Is group membership associated with allocation? | May conflict with other goals when outcome base rates differ |
| Equal opportunity | Equal true-positive rates across groups | Are qualified/positive cases missed at different rates? | Ignores false positives and depends on valid ground truth |
| Equalized odds | Equal true-positive and false-positive rates across groups | Are error rates comparable in both directions? | May be infeasible alongside calibration when base rates differ; depends on label quality |
| Predictive parity | Equal positive predictive value across groups | Is a positive prediction equally reliable? | Ignores false negatives and can conflict with equalized odds |
| Group calibration | Predicted probabilities correspond to outcome rates within each group | Is the score equally interpretable? | Requires meaningful probabilities and valid outcomes |
| Disaggregated task performance | Accuracy, error type, faithfulness, refusal, latency, or service quality by group | Does the system work comparably for each group? | Requires adequate, ethically collected group information |
| Counterfactual consistency | Outcome changes under a justified intervention on an attribute while relevant facts remain fixed | Is the system sensitive to an attribute that should not affect this task? | Requires causal assumptions; simple name swaps rarely hold everything else constant |
| Individual consistency | Similar cases under a justified similarity definition receive similar treatment | Are like cases treated alike? | The similarity function embeds value judgments |

Fairness criteria can be mutually incompatible except in constrained cases. [Kleinberg, Mullainathan, and Raghavan](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2017.43) prove this for three common conditions on risk scores. Record the chosen objective, rejected alternatives, trade-offs, and accountable decision.

## 5. Evaluation protocol

1. **Classify the use and decision.** Identify legal/sector context, human role, affected people, and potential allocation, quality, and representational harms.
2. **Define outcomes and labels.** Document why ground truth is valid. Historical decisions can encode discrimination and should not be assumed correct.
3. **Choose groups and slices.** Use characteristics relevant and lawful to evaluate. Include intersections where harms can differ, while protecting privacy and avoiding re-identification.
4. **Design cases.** Combine representative outcome data, controlled counterfactuals where causally defensible, linguistic/accessibility tests, and targeted stereotype or quality probes.
5. **Pre-register metrics and decisions.** Define the estimand, minimum disparity of concern, statistical method, correction for multiple testing, and mitigation/escalation rule.
6. **Determine sample size.** Use expected prevalence, variability, effect size, significance/coverage, desired power or precision, repeated runs, and available group support. There is no universal `n > 100` per subgroup.
7. **Execute the exact system.** Include retrieval, tools, policy, and human workflow, not just a bare model.
8. **Analyze.** Report each group and intersection, confidence intervals, practical effect sizes, data gaps, and model/evaluator uncertainty. Statistical non-significance is not proof of equality, especially with low support.
9. **Investigate mechanism.** Trace disparities to data, retrieval, prompt, model, tool, policy, interface, or human process.
10. **Mitigate and retest.** Consider problem reframing, data quality/coverage, access improvements, policy/threshold changes, human process, product limits, or stopping the use. Prompt changes alone may not address the cause.
11. **Monitor and provide recourse.** Track relevant outcomes with privacy protection and ensure affected people can report, challenge, or obtain review where required.

### Counterfactual tests

Changing a culturally associated name does not isolate race or ethnicity reliably and can encode stereotypes in the test itself. Prefer clearly defined attributes, multiple indicators and templates, matched content, randomized ordering, repeated generations, and expert/affected-stakeholder review. Treat such tests as sensitivity probes, not direct estimates of population discrimination unless the causal design supports that inference.

## 6. Four-fifths rule example

For an in-scope US employment selection procedure, compute each group's selection rate and compare it with the group having the highest rate as specified in the applicable Uniform Guidelines. Example:

```text
selection rate for group A = selected_A / applicants_A
selection rate for group B = selected_B / applicants_B
impact ratio = lower selection rate / higher selection rate
```

Interpret the result with sample size, statistical and practical significance, job-related validity, the full selection process, applicable law, and counsel. Do not write “legally actionable bias” solely because the ratio is below 0.8. Do not write “fair” solely because it is at least 0.8.

## 7. Model-grader bias

Model graders can display position, verbosity, self-enhancement, and other biases. [Zheng et al.](https://papers.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html) document several of these limitations, and [Wang et al.](https://aclanthology.org/2024.acl-long.511/) specifically demonstrate position bias.

Validate:

- pairwise order swaps and randomized presentation;
- concise correct versus verbose flawed answers;
- generator/model-family and writing-style effects;
- performance by language, topic, group, and severity;
- sensitivity to rubric wording and irrelevant demographic cues; and
- false-pass and false-fail rates against adjudicated human labels.

Mitigations such as order balancing, reference answers, structured evidence, independent human review, or multiple graders must themselves be validated. A panel of model graders does not automatically remove correlated bias.

## 8. Tools

| Tool | Verified scope | Limit |
|---|---|---|
| [Fairlearn](https://fairlearn.org/main/user_guide/assessment/perform_fairness_assessment.html) | Disaggregated assessment and common group disparity metrics for structured outcomes | Metric calculation does not choose the ethical/legal objective or validate labels |
| [AI Fairness 360](https://aif360.readthedocs.io/en/latest/) | Open-source datasets, metrics, explanations, and mitigation algorithms | Many methods assume structured data and may not apply directly to free-form generation |

Do not claim a tool proves compliance or fairness. Pin versions and validate preprocessing, group definitions, labels, and metric configuration.

## 9. Report template

```markdown
# Fairness and impact assessment

## Scope
- System/version:
- Intended decision/service:
- Affected people and jurisdictions:
- Human role and recourse:

## Harm model and metric rationale
| Harm | Group/slice | Metric | Decision rule | Owner |

## Data and study design
- Provenance/authority:
- Label validity:
- Sample-size or precision rationale:
- Counterfactual assumptions:

## Results
| Group/slice | Support | Metric | Estimate and interval | Decision |

## Limitations and missing evidence

## Mitigations, residual risk, and monitoring

## Review and approval
```

## 10. Release checklist

- [ ] Affected people, harms, protected characteristics, intersections, and legal context are documented.
- [ ] Outcome labels and proxies are validated rather than assumed neutral.
- [ ] Metric choice follows the harm model; trade-offs and incompatible criteria are recorded.
- [ ] Group data collection and processing are authorized, minimized, protected, and retained appropriately.
- [ ] Sample size or achievable precision is justified per group and metric.
- [ ] Results include support, uncertainty, effect size, and data/evaluator limitations.
- [ ] Counterfactual tests document causal assumptions and avoid treating names as definitive demographic labels.
- [ ] Model graders are validated for bias and error on the assessed slices.
- [ ] A qualified owner reviews legal and impact implications; a numeric ratio is not treated as a legal verdict.
- [ ] Mitigation, recourse, monitoring, residual risk, and approval are recorded.
