# Historical publication review record

> Historical content review performed before the executable reference
> implementation was added. It is retained as a claim-correction ledger, not as
> independent assurance, certification, or current production authorization.

**Audit date:** 2026-07-31  
**Scope:** All Markdown files in this repository and the external claims they contain  
**Historical result:** The reviewed draft was considered suitable for publication as a reference methodology.

**Production-system decision:** **NOT GRANTED**. No production system or control implementation was provided for assessment.

## 1. Decision basis

The methodology has been rewritten to remove or qualify unsupported universal thresholds, inaccurate legal claims, invented framework priorities, brittle framework counts, and security guidance that relied too heavily on prompt behavior. External factual claims in the revised publication are linked to primary or authoritative sources in [SOURCE_REGISTER.md](SOURCE_REGISTER.md).

This approval means the documents are suitable for use as a risk-based evaluation reference and template set. It does not mean:

- any LLM application passed the methodology;
- any listed control is implemented;
- any example result is real;
- the repository conforms to ISO/IEC 42001;
- any system complies with the EU AI Act, UK law, US law, or sector rules; or
- production deployment is authorized.

## 2. Evidence available

Repository inventory at audit start:

- `README.md`
- `01-framework.md`
- `02-threat-modelling-for-llm-apps.md`
- `03-golden-set-design.md`
- `04-governance-mapping.md`
- `05-security-testing.md`
- `06-bias-and-fairness.md`

No application code, architecture manifest, threat model for a real system, risk register, evaluation dataset, test harness, CI/CD configuration, evaluation output, security report, monitoring configuration, incident exercise, system card, approval record, or production evidence was present.

## 3. Implemented facts versus intentions

| Component | What exists in this repository | Evidence status |
|---|---|---|
| C1 Threat model | Template and method only | Proposed guidance; no system implementation evidence |
| C2 Risk register | Template only | Proposed guidance; no populated system register |
| C3 Evaluation set | Schema and examples only | Proposed guidance; no dataset |
| C4 Measurement plan | Metric and decision guidance only | Proposed guidance; no system thresholds or results |
| C5 Retrieval evaluation | Method only | Not applicable to this documentation repository; no RAG system supplied |
| C6 Model grader | Protocol and prompt pattern only | No grader, calibration set, or validation result |
| C7 Fairness assessment | Method and report template only | No system, data, affected-group study, or result |
| C8 Abstention policy | Measurement guidance only | No product policy or test evidence |
| C9 Injection suite | Coverage guidance only | No suite or execution result |
| C10 Red-team protocol | Rules and template only | No authorization, engagement, finding, or retest |
| C11 Output/tool security | Control guidance only | No code, configuration, or verification |
| C12 System card | Required sections only | No real system card |
| C13 Governance map | Schema and hypothetical row only | No owners or real evidence |
| C14 Audit/evidence records | Schema guidance only | No logging implementation or records |
| C15 Release gate | Decision model and sample record only | No pipeline or executed gate |
| C16 Monitoring | Indicator guidance only | No telemetry, thresholds, alert, or dashboard |
| C17 Feedback loop | Process guidance only | No production failures or case updates |
| C18 Incident response | Process and severity framework only | No deployed mechanism or exercise |

Any future claim that one of these is implemented must link to evidence for the exact assessed version. Any claim that it is verified must also link to a current test or review result.

## 4. Claim audit ledger

The ledger covers the material externally verifiable, governance, strategic, legal, statistical, tool, and technical claims in the pre-audit publication. Purely normative internal design choices are retained only when labeled as policy or examples.

### Framework and standards

| ID | Prior claim | Verdict | Publication action |
|---|---|---|---|
| F01 | The repository was a “comprehensive, production-grade framework” | Unverifiable marketing claim | Replaced with reference-methodology scope and explicit non-certification limits |
| F02 | Evaluation “proves” the surrounding system correctly bounds the model | Overstated | Replaced with evidence-based, version-scoped assurance language |
| F03 | The six layers and 18 components were standards-derived facts | Internal design, not external fact | Retained as the methodology's component model and labeled as such |
| F04 | NIST AI RMF 1.0 has GOVERN, MAP, MEASURE, MANAGE | Verified | Retained with [NIST source](https://doi.org/10.6028/NIST.AI.100-1) |
| F05 | NIST has seven trustworthiness characteristics | Verified with wording correction | Full grouped names restored, including “fair with harmful bias managed” |
| F06 | NIST mappings establish compliance | False implication | Mappings labeled interpretive; NIST is voluntary and not a checklist/certification |
| F07 | OWASP assigns Critical/High/Medium priorities to individual 2025 risks | Inaccurate | All custom priorities removed; local severity must come from the application |
| F08 | OWASP 2025 risk names LLM01-LLM10 | Verified | Retained and linked to official 2025 list |
| F09 | MITRE ATLAS had 84 techniques as of 2026, per the prior audit | Inaccurate/currently obsolete | Official site reported 16 tactics and 173 techniques on audit date; methodology omits brittle counts |
| F10 | ISO/IEC 42001 provides exact structures for model cards, audit trails, and the draft's Annex mappings | Not established from cited evidence | Limited to verified AIMS scope; exact mapping requires licensed standard and qualified review |
| F11 | ISO/IEC 42001 has exactly 38 Annex A controls | Commonly reported but not independently verified from the accessible official catalog | Count removed; a licensed copy must be used for any exact Annex A statement or mapping |
| F12 | The methodology “satisfies” EU AI Act requirements | Inaccurate compliance claim | Replaced with applicability-specific support language and no conformity claim |
| F13 | EU AI Act requirements applied uniformly to LLM applications | Inaccurate | Role, risk classification, sector, use, and transition provisions made explicit |
| F14 | EU high-risk dates from the original 2024 Act remained current | Outdated | Added Regulation (EU) 2026/1744 and amended 2027/2028 dates |
| F15 | Google SAIF exists and has six core elements that directly ground this process | Existence/count verified; direct process attribution not established | Removed from normative alignment; SAIF remains optional security reference material |
| F16 | Anthropic's RSP uses capability thresholds and AI Safety Levels and directly grounds an application release gate | Policy concepts verified; direct application-gate attribution is inapposite | Removed from normative alignment because the RSP is a provider-specific frontier-risk policy |
| F17 | An official OpenAI “two-tier gate” grounded the process | Unverifiable reference | No official primary source for that named construct was identified; removed |
| F18 | CoSAI was the source standard for the incident component | Framework exists; the draft's unversioned attribution and “standard” language were overstated | Removed from normative mapping; incident process is local guidance aligned at a high level with NIST MANAGE |

### Metrics, thresholds, and evaluation design

| ID | Prior claim | Verdict | Publication action |
|---|---|---|---|
| M01 | Faithfulness and relevance should universally exceed 0.85 | Unsupported universal threshold | Removed; thresholds must be risk- and measurement-specific |
| M02 | Citation accuracy must universally be 100% for “high-risk” | Unsupported as a portable metric | Split into citation precision, completeness, and source authority with risk-derived gates |
| M03 | Abstention rate merely had to be greater than 0% | Technically meaningless | Replaced with unsafe-answer, unnecessary-refusal, coverage, and answered-case accuracy |
| M04 | 100% observed injection resilience proves security | False assurance | Blocking known cases may require all-pass, but results must include attack coverage, repetitions, severity, and residual risk |
| M05 | ECE below 0.1 is a universal calibration target | Unsupported | Removed; ECE limited to defined probabilistic predictions with labels |
| M06 | A raw “no more than 2% lower” comparison is a non-inferiority test | Incomplete | Requires a pre-specified margin, paired/statistical design, uncertainty, and decision rule |
| M07 | Safety thresholds can be set from the baseline | Unsafe reasoning | Baseline retained for comparison only; a poor baseline cannot define acceptable harm |
| M08 | Evaluation gates take under one minute and 10-15 minutes | Implementation-specific and unsupported | Durations removed |
| M09 | New metrics should warn for exactly three releases | Arbitrary | Removed; any non-blocking period requires explicit risk rationale and duration |
| M10 | 30-50 cases is a production minimum | Unsupported universal count | Described only as a possible smoke suite; coverage and precision drive size |
| M11 | 150-200 cases is a production baseline and 500+ is enterprise-grade | Unsupported universal count | Removed |
| M12 | 300-400 cases generally detects a 5% regression at 95% confidence | Under-specified and not generally valid | Replaced with estimand-specific power/precision analysis using NIST statistical guidance |
| M13 | More than 100 cases per subgroup is generally definitive | Unsupported | Removed; power, prevalence, effect, variance, clustering, and multiplicity must be considered |
| M14 | Fixed 60/15/15/10 evaluation-set allocation is robust | Unsubstantiated heuristic | Replaced with requirement/risk coverage matrix |
| M15 | Representative cases should universally pass above 95% | Unsupported | Removed; task and harm define the decision rule |
| M16 | Golden-set labels are an absolute source of truth | Overstated | “Golden” labels are governed, versioned, reviewable measurement artifacts |
| M17 | Evaluation data must be synthetic only | Incorrect as a general rule | Replaced with authorized, minimized mixed-source data and explicit provenance/privacy controls |
| M18 | Only generation is probabilistic | Incorrect | Reproducibility now covers model, retrieval, tools, provider changes, repeats, and run time |
| M19 | LLM evaluation cannot use exact/string matching | Incorrect | Deterministic schema/exact checks are preferred when they directly measure the requirement |

### RAG and model graders

| ID | Prior claim | Verdict | Publication action |
|---|---|---|---|
| J01 | “RAGAS triad” was the authoritative name for context relevance, faithfulness, and answer relevance | Imprecise attribution | Reframed as component-level RAG evaluation; cited RAGAS paper and current metrics |
| J02 | Low faithfulness should be fixed by lowering temperature or adding “use only context” | Unsupported as a reliable remedy | Replaced with root-cause analysis and verification across retrieval, evidence, generation, and controls |
| J03 | Every grader must use a 1-5 rubric | Unsupported | Rubric scale must fit the construct; binary, ordinal, categorical, and pairwise are permitted |
| J04 | A grader must output chain-of-thought before its score | Unnecessary and unsafe as a requirement | Replaced with structured verdict and short evidence references; no hidden reasoning requirement |
| J05 | One or at most two dimensions is an evidence-based universal rule | Over-specific | Replaced with one coherent construct per rubric and local validation |
| J06 | A different model family removes self-enhancement bias | Possible mitigation, not guarantee | Requires measured task-specific validation |
| J07 | A calibration set of 30-200 is generally sufficient | Arbitrary | Replaced with stratified sample and precision/error rationale |
| J08 | Cohen's kappa or Gwet's AC2 could be used interchangeably for the described 1-5 setup | Methodologically incomplete | Statistic must match nominal/ordinal scale and number of raters; weighted method required for ordinal distance |
| J09 | More than 85% “inter-rater agreement” calibrates a grader | No universal threshold; conflates agreement measures | Removed; pre-register task-specific false-pass/false-fail and agreement criteria with intervals |
| J10 | Grader disagreement is almost always an ambiguous rubric | Unsupported | Disagreement can arise from cases, labels, model limits, bias, drift, parsing, or rubric; investigate empirically |
| J11 | Abstention tests measure ECE | Incorrect | Separated abstention behavior from probabilistic calibration |

### Threat modelling and security

| ID | Prior claim | Verdict | Publication action |
|---|---|---|---|
| S01 | A “standard” 5 by 5 risk matrix with the listed bands was complete | Incorrect; scores 7, 13, 14, and 21-24 were unclassified | Labeled method as internal default and replaced bands with complete ranges |
| S02 | Every threat must have a mitigating control | Incomplete risk treatment model | Added avoid, mitigate, transfer/share, and authorized acceptance |
| S03 | Cloud and SSO providers can be removed from the system boundary as out of scope | Unsafe modelling | Dependencies remain modeled as inherited controls, assumptions, and supplier risk |
| S04 | API roles/delimiters separate instructions from data as a security boundary | Overstated | Retained only as a layer; deterministic authorization and impact controls required |
| S05 | A second LLM classifier is a reliable injection control | Overstated | Classifiers treated as fallible detection layers, not authorization controls |
| S06 | A standard refusal is the injection-test pass condition | Incorrect for safe task completion | Pass outcome now depends on authorized task, data, tool, and side effects |
| S07 | Defensive prompt text prevents system-prompt leakage | Inaccurate | Prompt is not secret/security boundary; remove secrets and enforce external controls per OWASP LLM07 |
| S08 | Prompt injection can be solved through semantic sanitization | Inaccurate | Emphasis moved to least privilege, authorization, isolation, egress, tool design, and monitoring |
| S09 | Direct injection and jailbreaking are the same category | Imprecise | Related intents are distinguished for coverage |
| S10 | Attack trees are mandatory for every agent/tool system | Arbitrary | Representation choice must be justified by complexity and risk |
| S11 | A fixed 30-case security suite is robust | Unsupported | Coverage, variation, stochastic repetitions, and impact drive selection |
| S12 | Successful system-prompt extraction is always a security failure | Overbroad | Failure depends on secrets or bypassable controls; prompt itself is not trusted as confidential |
| S13 | Parameterization alone makes arbitrary model-generated SQL safe | Incomplete | Prefer fixed/constrained queries; add AST allowlist, least privilege, bounds, and isolation |
| S14 | A Docker container with no network is necessarily a tight sandbox | Incomplete | Requires a hardened ephemeral isolation boundary, no ambient credentials, egress policy, resource limits, and teardown |
| S15 | NER/regex prevents PII leakage | Incomplete | Detection is fallible and supplements, not replaces, authorization/minimization |
| S16 | Memorization can be tested by asking for real proprietary data | Unsafe without authority | Use authorized synthetic canaries or specifically approved data/tests |
| S17 | Garak ownership/current reference was generic | Updated | Current authoritative repository is NVIDIA/garak |
| S18 | PyRIT repository/namespace was Azure | Updated | Current authoritative repository is microsoft/PyRIT after its 2026 move |
| S19 | Promptmap and Giskard setup claims were necessary to the method | Unnecessary/current capability not fully audited | Removed from core list; retained tools are linked to current authoritative sources |
| S20 | DeepEval is an open-source LLM evaluation framework whose metrics can serve as pass criteria without local validation | Tool existence verified; authority implication unsupported | Tool is optional and omitted from the core list; any adoption must pin its version and validate each metric for the decision |

### Governance, logging, and law

| ID | Prior claim | Verdict | Publication action |
|---|---|---|---|
| G01 | Hypothetical RAG controls and results were “Active” | Unverifiable and misleading | All examples explicitly marked Proposed with no evidence |
| G02 | A system card by itself aligns or complies with ISO/IEC 42001 | Overstated | Card is evidence input only; no conformity claim |
| G03 | ISO/IEC 42001 and the EU AI Act require the draft's universal audit-trail schema | Inaccurate | Logging is purpose/risk/applicability based; raw content is not universally mandatory |
| G04 | Every interaction must store raw input, context, and output | Privacy/security overcollection | Replaced with data-minimized candidate fields and classification/digests where sufficient |
| G05 | Audit logs must always be immutable | Overbroad | Append-only/tamper-evident storage used where threat/applicable requirement warrants, balanced with data rights |
| G06 | Standard retention is 12 months and high-risk EU retention is 3 years | Inaccurate | EU high-risk provider documentation is 10 years; controlled automatic logs are at least six months, subject to applicable law |
| G07 | Golden sets should be retained indefinitely | Unsupported and can conflict with data obligations | Retention now purpose-, authority-, and data-based |
| G08 | ISO Annex A.4 is AI risk assessment/treatment | Incorrect mapping | Mapping removed; licensed standard required |
| G09 | ISO Annex A.8 directly equals incident management | Overstated/incomplete mapping | Mapping removed; licensed standard required |
| G10 | AI Review Board composition is universally mandated | Internal policy choice | Replaced with accountable roles and local separation-of-duty design |
| G11 | One smaller model is automatically a safe incident fallback | Incorrect | Every fallback needs its own approved behavior and permissions |
| G12 | Universal production alerts include 5% thumbs-down, 2% block spike, 20% token increase, 1.5s p95, and 0.1 embedding shift | Unsupported and non-portable | Replaced with locally validated indicators and threshold rationale |

### Bias and fairness

| ID | Prior claim | Verdict | Publication action |
|---|---|---|---|
| B01 | The EU AI Act mandates strict bias testing for all LLM systems | Overbroad | Restricted to applicable role/risk provisions and current legal assessment |
| B02 | The UK Equality Act 2010 specifically prohibits automated decisions with disparate impact | Inaccurate | Corrected to the general section 19 indirect-discrimination rule |
| B03 | The four-fifths ratio applies to employment and financial systems generally | Inaccurate | Restricted to applicable US employment selection context |
| B04 | A ratio below 0.8 means “legally actionable bias” | Inaccurate legal conclusion | Described as rule of thumb/evidence, not a legal verdict |
| B05 | A ratio above 0.8 is a required fairness pass | Inaccurate | No safe harbor or universal fairness conclusion |
| B06 | Demographic parity can be dismissed as hiring “less qualified” people | Loaded and assumes valid qualifications/labels | Replaced with neutral metric limitation and label-validity analysis |
| B07 | Names such as John Smith and Aisha Johnson isolate race/gender | Methodologically weak | Name swaps treated as noisy sensitivity probes with causal limits |
| B08 | 500 name-varied resumes establish discrimination | Unsupported design | Replaced with pre-registered, powered, context-valid study design |
| B09 | Chi-square/t-tests are always appropriate for LLM demographic testing | Over-generalized | Statistical method must match outcome, pairing, clustering, repeats, and multiple comparisons |
| B10 | A diverse panel of model judges removes bias | Unsupported guarantee | Any panel and aggregation must be validated against human reference by slice |
| B11 | AIF360 has a stable “70+ metrics” capability claim | Brittle marketing/count claim | Removed; retained only verified general library scope |
| B12 | Google What-If Tool should be recommended as an active standard tool | Current support not established | Removed from the core tooling list |

## 5. Conditions on reuse

The review conclusions remain applicable while all of the following hold:

1. The documents retain their explicit guidance-only and non-certification scope.
2. Hypothetical examples are not relabeled as real evidence.
3. Production approvals require the evidence pack in [01-framework.md](01-framework.md).
4. Legal applicability is reviewed against current law for each system.
5. External sources are reviewed by 2027-01-31 or earlier if NIST AI RMF 1.0 is replaced, OWASP or MITRE materially changes, the EU AI Act is amended again, or relevant law/guidance changes.

## 6. Verification record

Verification completed on 2026-07-31:

- all nine Markdown artifacts were read after the final edits;
- 92 material claim families from the pre-audit publication and supplied prior review were adjudicated in the ledger;
- all 106 Markdown link references were parsed, covering 39 unique external destinations, with no missing local targets;
- every external source used by the seven core methodology documents appears in [SOURCE_REGISTER.md](SOURCE_REGISTER.md);
- primary or authoritative sources were reviewed for each standards, legal, statistical, research, and tool claim family; canonical official index or search results were used where a site rejected automated direct access;
- every fenced code block is balanced and every contiguous Markdown table has a consistent column count;
- all files decode as strict UTF-8, with no detected mojibake, unresolved publication markers, or em dashes; and
- a fresh second-pass review found no blocking publication issue. It confirmed the remaining scope boundary: this is documentation assurance, not implementation or production-system assurance.

The historical embedded hash table was removed after later edits made five of
its eight entries stale. Current release bytes are recorded only in
`RELEASE_MANIFEST.sha256`, which is regenerated as part of release preparation.

## 7. Review status

- The claim-correction ledger remains useful as historical review evidence.
- It does not approve deployment of an actual system.
- It does not establish ISO/IEC 42001 conformity or legal compliance.
- No human legal reviewer, accredited assessor, or independent technical
  reviewer signed this review.

Publication and production authority remain with the accountable repository and
system owners.
