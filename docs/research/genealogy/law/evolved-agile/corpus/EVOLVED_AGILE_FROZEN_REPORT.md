# EVOLVED_AGILE — Frozen external research packet

```text
ANALYTICAL_LABEL                 EVOLVED_AGILE
RESEARCH_CONTINUATION            PASS_1 → FINAL_FREEZE
EVIDENCE_CUTOFF                  2026-08-11
IMPLEMENTAUDIT_ANALYSIS          EXCLUDED
REPOSITORY_ANALYSIS              EXCLUDED
FINAL_PROPERTY_DENOMINATOR       28
FINAL_PROPERTY_RECORDS_EXAMINED  28
SOURCE_COMPLETENESS              BOUNDED_AND_ADEQUATE_FOR_FREEZE
```

`EVOLVED_AGILE` remains an analytical label, not the name of a purported formal method. Freezing means that the external evidence search and property denominator are now sufficiently complete for a later crosswalk. It does not mean that the literature is exhaustive or that future evidence cannot change a judgement.

## Controlling conclusions

The historical and empirical record does **not** support the proposition that a branded whole method—Scrum, XP, SAFe, Kanban or any combination of them—is generally causal of superior outcomes. A 1,002-project study reported positive associations between Agile use and project efficiency and stakeholder satisfaction. A later preregistered meta-analysis also found positive associations across workplace outcomes, but 35 of its 41 studies were correlational, 90% used cross-sectional correlations, published effects were larger than unpublished effects, and the authors expressly rejected causal interpretation. Earlier and large-scale reviews likewise found heterogeneous definitions, weak comparisons and experience-report-heavy evidence. ([pure.psu.edu](https://pure.psu.edu/en/publications/does-agile-work-a-quantitative-analysis-of-agile-project-success/))

The evidence is more defensible at the level of **narrower mechanisms**. Continuous integration, for example, has a literature containing both benefits and technical/process costs; a 2022 review retained 101 empirical studies from 479 candidates. TDD and pair programming have mixed, context-sensitive findings rather than universal superiority. ([link.springer.com](https://link.springer.com/article/10.1007/s10664-021-10114-1))

The final synthesis therefore admits engineering properties only where all of the following can be stated:

```text
a failure mechanism;
a plausible control mechanism;
a trigger or context;
a cheap/non-trigger path;
material prerequisites;
known ways the property can fail or be gamed;
an evidence-strength boundary.
```

A named ceremony is not admitted merely because it is common.

## Closure of pass-1 unresolved burdens

| Burden | Frozen disposition |
|---|---|
| **Whole-method causality** | `POSITIVE_ASSOCIATIONS_BUT_CAUSAL_IDENTIFICATION_WEAK`. Whole-method studies do not identify which practice, team capability, organisational selection effect or technical substrate caused an outcome. Property-level evidence is preferred. |
| **Feedback-cadence economics** | `NO_UNIVERSAL_SHORTEST_CADENCE`. Feedback is valuable only when it is informative, actionable and arrives before avoidable commitment. A system-dynamics study found both long cycles and monthly cycles could generate disruptive schedule-pressure fluctuations; its modelled two-to-three-month optimum is a model result, not a universal prescription. ([journals.sagepub.com](https://journals.sagepub.com/doi/abs/10.1177/8756972818802714)) |
| **Batch reduction under expensive setup or qualification** | `ECONOMIC_OPTIMUM_NOT_BATCH_OF_ONE`. Continuous Delivery itself says large batches persist because handoffs have high fixed cost and that the engineering objective is to change those economics. Where qualification, fabrication, mobilisation or exposure has irreducible fixed cost, aggregate the expensive boundary while keeping upstream learning and integration smaller. ([continuousdelivery.com](https://continuousdelivery.com/principles/)) |
| **Architecture threshold** | `QUALITATIVE_TRIGGER_CLOSED_NUMERIC_THRESHOLD_UNRESOLVED`. No credible universal threshold says when architecture must be designed up front. Deliberate analysis becomes increasingly justified with irreversibility, quality-attribute trade-offs, external contracts, cross-team coupling, blast radius, asset longevity and expensive verification. ATAM and CBAM offer structured technical and economic analysis, not a universal number. ([sei.cmu.edu](https://www.sei.cmu.edu/library/the-architecture-tradeoff-analysis-method/)) |
| **Scaling-framework evidence** | `SYSTEM_COORDINATION_RETAINED_FRAMEWORK_UNIVERSALISM_REJECTED`. A 2024 study covering 4,013 teams found scaling-framework differences small to nonexistent in practical effect and largely disappearing after controls. Reviews still find genuine architecture, requirements, coordination and organisational-interface problems. ([link.springer.com](https://link.springer.com/article/10.1007/s10664-024-10481-5)) |
| **Long-latency outcome governance** | `SHORT_PROXY_REQUIRES_VALIDATION`. Short-cycle metrics cannot simply stand in for retention, safety or other delayed outcomes. Netflix found that a learned 14-day surrogate often—but not perfectly—reproduced day-63 decisions. Surrogate validity rests on assumptions that can fail, while long-running experiments have their own selection, survival and instrumentation hazards. ([arxiv.org](https://arxiv.org/html/2311.11922v2)) |
| **Proxy and metric gaming** | `DIAGNOSTIC_PORTFOLIO_WITH_COUNTERMETRICS`. DORA warns against targets, dissimilar-team comparisons, competition and single metrics. SPACE rejects one-dimensional developer productivity. Story points changed after sprint assignment in about 10% of 19,349 studied work items, often following scope or information changes. ([dora.dev](https://dora.dev/guides/dora-metrics/)) |
| **Hardware, regulated and safety-critical work** | `RISK_BASED_HYBRID`. NASA does not require one lifecycle model; NIST integrates security into any lifecycle; FDA requires risk-appropriate evidence; cyber-physical CI/CD combines continuous and periodic builds, simulation and hardware-in-the-loop. Adaptation survives, but release authority, traceability, configuration control, assurance and independent V&V may remain mandatory. ([nodis3.gsfc.nasa.gov](https://nodis3.gsfc.nasa.gov/displayDir.cfm?Internal_ID=N_PR_7150_002D_&page_name=Chapter1)) |
| **Property prerequisites** | `PARTIAL_ORDER_FROZEN`. Technical adaptability depends on regression verification → frequent integration → refactoring/changeability → release readiness → controlled exposure. Product adaptation depends on direct evidence plus multi-horizon planning and long-outcome controls. Organisational autonomy depends on system-level dependency management and bounded cognitive load. |
| **Lineage classification** | `CLOSED_WITH_NON_COLLAPSE_RULE`. Lean software, Kanban, DevOps, SRE, product discovery and platform engineering are not all descendants in one straight Agile lineage. The final genealogy distinguishes direct lineage, shared ancestry, hybridisation, reaction, convergence and analogy. |

## Evidence vocabulary

| Grade | Meaning |
|---|---|
| `STRONG_CONVERGENT` | Multiple authoritative or standards sources plus substantial empirical or operational convergence; not necessarily randomised causality. |
| `MODERATE_CONVERGENT` | Coherent mechanism supported by several studies, cases or authoritative practices, with meaningful contextual limits. |
| `MIXED` | Material supporting and contrary findings, heterogeneous implementations or weak causal attribution. |
| `STRONG_CONTEXTUAL` | Strong obligation or evidence in a stated regulated, safety, security or operational context, not universal outside it. |
| `EMERGING` | Mature practitioner formulation but limited independent comparative evidence. |
| `HISTORICAL_ONLY` | Establishes origin or claimed intent, not effectiveness. |

## Source register

All sources were accessed **2026-08-11**. The source IDs below are used in the machine-readable ledgers.

### Primary history and current engineering sources

| ID | Source, date and stable locator | Class and exact locator | Claim supported; contrary boundary | Access |
|---|---|---|---|---|
| `H01` | Craig Larman and Victor Basili, *Iterative and Incremental Development: A Brief History*, 2003, DOI `10.1109/MC.2003.1204375` | Scholarly history, pp. 47–56 | IID, test-first work and evolutionary delivery predate 2001. Authors say examples are representative, not exhaustive. ([craiglarman.com](https://www.craiglarman.com/wiki/downloads/misc/history-of-iterative-larman-and-basili-ieee-computer.pdf)) | Open copy |
| `H02` | Barry Boehm, *A Spiral Model of Software Development and Enhancement*, 1988, DOI `10.1109/2.59` | Primary paper, entire spiral model | Iteration can be governed by risk retirement rather than a fixed cadence. Does not contain the later Agile package. ([computer.org](https://www.computer.org/csdl/magazine/co/1988/05/r5061/13rRUwwslzm)) | Metadata/paywalled |
| `H03` | Tom Gilb and Susannah Finzi, *Principles of Software Engineering Management*, 1988 | Primary monograph, evolutionary delivery and measurable-objective chapters | Small measurable steps, value, risk and reversal precede Agile. Book-level prescription is not independent outcome evidence. ([researchgate.net](https://www.researchgate.net/publication/225070548_Principles_of_Software_Engineering_Management)) | Partial |
| `H04` | Hirotaka Takeuchi and Ikujiro Nonaka, *The New New Product Development Game*, January 1986, HBR product `86116` | Primary case-based article, pp. 137–146 in original issue | Overlapping phases and cross-functional self-organisation influenced Scrum. Cases primarily concerned product/hardware development and cannot establish universal team design. ([hbr.org](https://hbr.org/1986/01/the-new-new-product-development-game)) | Partial |
| `H05` | Ken Schwaber, *SCRUM Development Process*, OOPSLA 1995 workshop; published 1997, pp. 117–134 | Primary method description | Early empirical Scrum management. It is not a complete technical engineering system. ([scrum.org](https://www.scrum.org/resources/scrum-development-process)) | Official locator |
| `H06` | Kent Beck, *Embracing Change with Extreme Programming*, 1999, DOI `10.1109/2.796139` | Primary method paper | XP tied adaptation to testing, integration, design and collaboration. Initial project conditions were narrower than later enterprise claims. ([computer.org](https://www.computer.org/csdl/magazine/co/1999/10/rx070/13rRUEgs2Pl)) | Metadata/paywalled |
| `H07` | Seventeen authors, *Manifesto for Agile Software Development*, 2001 | Primary declaration, complete text | Four comparative values; right-hand items retain value. Not a lifecycle or causal study. ([agilemanifesto.org](https://agilemanifesto.org/)) | Open |
| `H08` | Seventeen authors, *Principles behind the Agile Manifesto*, 2001 | Primary declaration, twelve principles | Frequent delivery, technical excellence, sustainable pace and reflection. Does not prescribe Scrum ceremonies. ([agilemanifesto.org](https://agilemanifesto.org/principles.html)) | Open |
| `H09` | Jim Highsmith, *History: The Agile Manifesto*, 2001 | Participant history, complete page | Snowbird represented XP, Scrum, DSDM, Crystal, FDD, ASD and related methods. Participant perspective, not independent historiography. ([agilemanifesto.org](https://agilemanifesto.org/history.html)) | Open |
| `H10` | Ken Schwaber and Jeff Sutherland, *The Scrum Guide*, November 2020 | Official current definition, pp. 3–12 | Scrum is purposefully incomplete; inspection without adaptation is pointless; increments must be usable and verified. Story points, velocity and two-week sprints are not required. ([scrumguides.org](https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf)) | Open |
| `H11` | Agile Alliance, *What is Extreme Programming?*, current | Authoritative method summary, practices and applicability sections | XP is unusually specific about software engineering and its practices are interdependent. Applicability remains contextual. ([agilealliance.org](https://agilealliance.org/glossary/xp/)) | Open |
| `H12` | Mary and Tom Poppendieck, *Lean Software Development: An Agile Toolkit*, 2003 | Primary practitioner monograph, official publisher description | Lean principles entered software through a hybrid, not solely through Manifesto lineage. Method claims remain practitioner-derived. ([informit.com](https://www.informit.com/store/lean-software-development-an-agile-toolkit-an-agile-9780133812930)) | Partial |
| `H13` | Coleman et al., *The Kanban Guide*, version 2025.5 | Official current guide, Definition of Workflow and Flow Metrics | Explicit WIP control, cycle time, work-item age, throughput and probabilistic SLEs. Metrics remain meaningless unless used for decisions. ([kanbanguides.org](https://kanbanguides.org/the-kanban-guide/)) | Open |
| `H14` | Martin Fowler, *Continuous Integration*, 2006, updated | Original practitioner synthesis, practices and prerequisites | Real CI means frequent mainline integration, automation and immediate repair—not merely owning a CI server. Practitioner source, not causal trial. ([martinfowler.com](https://martinfowler.com/articles/continuousIntegration.html)) | Open |
| `H15` | Jez Humble et al., *Continuous Delivery* and *Principles*, current; original monograph 2010 | Authoritative current practice source, principles and small-batch sections | Release-ready state, quality built in, small batches and automation. It explicitly identifies fixed handoff cost as the economic cause of large batches. ([continuousdelivery.com](https://continuousdelivery.com/)) | Open |
| `H16` | Patrick Debois, Agile infrastructure work, 2008; John Allspaw and Paul Hammond, *10+ Deploys per Day*, 2009 | Primary practitioner history and presentation | DevOps reacted to development/operations separation through shared responsibility and automation. Not a controlled comparison. ([jedi.be](https://jedi.be/blog/)) | Open |
| `H17` | Betsy Beyer et al., *Site Reliability Engineering*, “Embracing Risk”, 2016 | Primary practitioner monograph, error-budget section | SLOs and error budgets provide a concrete speed–reliability control and require authority to stop releases. Primarily online-service experience. ([sre.google](https://sre.google/sre-book/embracing-risk/)) | Open |
| `H18` | Betsy Beyer et al., *Site Reliability Engineering*, “Postmortem Culture”, 2016 | Primary practitioner monograph, complete chapter | Incident learning requires blameless causal analysis and tracked action. A meeting alone does not create learning. ([sre.google](https://sre.google/sre-book/postmortem-culture/)) | Open |
| `H19` | Teresa Torres, *Everyone Can Do Continuous Discovery—Even You!*, current formulation | Original practitioner source, “What Is Discovery?” | Direct recurring customer research in pursuit of an outcome. Weekly cadence is an implementation prescription, not a universal engineering constant. ([producttalk.org](https://www.producttalk.org/getting-started-with-discovery/?srsltid=AfmBOoqTiIu-TV_zrwhxZotGBYWGJU1KqeEXQvurS9n_px1crqpYhYjr)) | Open |
| `H20` | Sriram Narayan, *Products Over Projects*, 2017 | Practitioner synthesis, product-mode definition and benefits | Durable outcome ownership and alignment with business and architecture boundaries. Comparative causal evidence remains sparse. ([martinfowler.com](https://martinfowler.com/articles/products-over-projects.html)) | Open |
| `H21` | CNCF TAG App Delivery, *Platforms White Paper*, current | Authoritative industry white paper, attributes and challenges | Self-service platforms can reduce duplicated infrastructure work and cognitive load; top-down mandated platforms can create resistance. ([tag-app-delivery.cncf.io](https://tag-app-delivery.cncf.io/whitepapers/platforms/)) | Open |
| `H22` | Matthew Skelton and Manuel Pais, *Team Topologies: Key Concepts*, current | Original/current method source, team types, interaction modes and cognitive load | Bounded team responsibilities and explicit interactions address flow at team-of-teams scale. Independent comparative evidence is limited. ([teamtopologies.com](https://teamtopologies.com/key-concepts)) | Open |
| `H23` | Neal Ford, Rebecca Parsons, Patrick Kua and Pramod Sadalage, *Building Evolutionary Architectures*, second edition | Original practitioner monograph, fitness-function description | Automated fitness functions permit selected architectural qualities to evolve under continuous evaluation. Does not eliminate deliberate architecture. ([thoughtworks.com](https://www.thoughtworks.com/en-us/insights/books/building-evolutionaryarchitectures-second-edition)) | Partial |
| `H24` | Rick Kazman et al., *The Architecture Tradeoff Analysis Method*, 1998, `CMU/SEI-98-TR-008` | Authoritative technical report, method | Architecture requires explicit quality-attribute trade-off and risk analysis. It supplies no universal trigger threshold. ([sei.cmu.edu](https://www.sei.cmu.edu/library/the-architecture-tradeoff-analysis-method/)) | Open |
| `H25` | Robert Nord et al., *Integrating ATAM with CBAM*, 2003, DOI `10.1184/R1/6574613.v1` | Authoritative technical note, pp. 1–23 | Adds cost, benefit and roadmap economics to technical architecture analysis. Estimates themselves can be uncertain. ([sei.cmu.edu](https://www.sei.cmu.edu/library/integrating-the-architecture-tradeoff-analysis-method-atam-with-the-cost-benefit-analysis-method-cbam/)) | Open |
| `H26` | ISO/IEC/IEEE 42010:2022, *Architecture Description* | International standard | Architecture descriptions serve communication, evaluation and conformity needs. A standard does not prescribe how much architecture every context needs. ([standards.ieee.org](https://standards.ieee.org/ieee/42010/6846/)) | Metadata/paywalled |

### Empirical and critical evidence

| ID | Source and stable locator | Exact evidence and relation | Limit |
|---|---|---|---|
| `E01` | Tore Dybå and Torgeir Dingsøyr, *Empirical Studies of Agile Software Development: A Systematic Review*, 2008, DOI `10.1016/j.infsof.2008.01.006` | 36 retained empirical studies from 1,996 publications; promising but methodologically weak whole-method evidence. ([ouci.dntb.gov.ua](https://ouci.dntb.gov.ua/en/works/96ODOe07/)) | Search ends in 2005. |
| `E02` | Pedro Serrador and Jeffrey Pinto, *Does Agile Work?*, 2015, DOI `10.1016/j.ijproman.2015.01.006` | Positive association with efficiency and stakeholder satisfaction across 1,002 projects. ([pure.psu.edu](https://pure.psu.edu/en/publications/does-agile-work-a-quantitative-analysis-of-agile-project-success/)) | Observational and dependent on reported Agile use. |
| `E03` | Jan Koch, Ivana Drazic and Carsten Schermuly, *The Affective, Behavioural and Cognitive Outcomes of Agile Project Management*, 2023, DOI `10.1111/joop.12429` | Preregistered meta-analysis, 41 studies and 73,825 participants; positive associations. ([researchgate.net](https://www.researchgate.net/publication/368720215_The_affective_behavioural_and_cognitive_outcomes_of_agile_project_management_A_preliminary_meta-analysis)) | Ninety per cent cross-sectional; no causal inference; probable publication effects. ([researchgate.net](https://www.researchgate.net/publication/368720215_The_affective_behavioural_and_cognitive_outcomes_of_agile_project_management_A_preliminary_meta-analysis)) |
| `E04` | Kim van Oorschot, Kishore Sengupta and Luk Van Wassenhove, *Under Pressure*, 2018, DOI `10.1177/8756972818802714` | System-dynamics model finds both very long and monthly cycles can amplify schedule pressure. ([journals.sagepub.com](https://journals.sagepub.com/doi/abs/10.1177/8756972818802714)) | Simulation assumptions do not establish a universal optimum. |
| `E05` | Christiaan Verwijs and Daniel Russo, *Do Agile Scaling Approaches Make a Difference?*, 2024, DOI `10.1007/s10664-024-10481-5` | 4,013 teams; scaling approach had negligible practical effect after controls. ([link.springer.com](https://link.springer.com/article/10.1007/s10664-024-10481-5)) | Cross-sectional, self-selected survey; not organisation-level financial evidence. |
| `E06` | Kim Dikert, Maria Paasivaara and Casper Lassenius, *Challenges and Success Factors for Large-Scale Agile Transformations*, 2016, DOI `10.1016/j.jss.2016.06.013` | 52 publications and 42 cases identify coordination and organisational burdens. ([research.aalto.fi](https://research.aalto.fi/en/publications/challenges-and-success-factors-for-large-scale-agile-transformati/)) | Almost 90% were experience reports. |
| `E07` | Rashidah Kasauli et al., *Requirements Engineering Challenges and Practices in Large-Scale Agile System Development*, 2021, DOI `10.1016/j.jss.2020.110851` | Seven large software/hardware system cases find requirements, value, traceability and V&V gaps not fully covered by scaling frameworks. ([sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0164121220302417)) | Case-study generalisation is limited. |
| `E08` | Eliezio Soares et al., *The Effects of Continuous Integration on Software Development*, 2022, DOI `10.1007/s10664-021-10114-1` | Systematic review of 101 empirical studies reports positive and negative CI effects. ([link.springer.com](https://link.springer.com/article/10.1007/s10664-021-10114-1)) | Heterogeneous CI definitions and study quality. |
| `E09` | Fiorella Zampetti et al., *An Empirical Characterization of Bad Practices in Continuous Integration*, 2020, DOI `10.1007/s10664-019-09785-8` | Thirteen expert interviews, more than 2,300 developer posts and a 26-person validation survey produced 79 CI bad-practice categories. ([ifi.uzh.ch](https://www.ifi.uzh.ch/seal/people/vassallo/ZampettiEMSE2019.pdf)) | Does not estimate universal prevalence. |
| `E10` | Yahya Rafique and Vojislav Mišić, *The Effects of Test-Driven Development on External Quality and Productivity*, 2013, DOI `10.1109/TSE.2012.28` | Meta-analysis finds context, task size and experience affect TDD results; quality effects are more consistent than productivity effects. ([raidoninc.com](https://raidoninc.com/assets/research/tddMetaAnalysis.pdf)) | Study heterogeneity and academic/industrial differences. |
| `E11` | Jo Hannay et al., *The Effectiveness of Pair Programming: A Meta-Analysis*, 2009, DOI `10.1016/j.infsof.2009.02.001` | Pairing trades time, quality and task characteristics rather than dominating universally. ([researchgate.net](https://www.researchgate.net/publication/222408325_The_effectiveness_of_pair_programming_A_meta-analysis)) | Diverse tasks and experience levels. |
| `E12` | Fiorella Zampetti et al., *Continuous Integration and Delivery Practices for Cyber-Physical Systems*, 2023, DOI `10.1145/3571854` | Ten organisations in eight domains plus 55-professional validation; hybrid continuous/periodic builds, simulation and HiL. ([digitalcollection.zhaw.ch](https://digitalcollection.zhaw.ch/items/a9ec28d1-4e39-42d9-803a-5b3611588960)) | Interview-based and domain-specific. |
| `E13` | Chakkrit Tantithamthavorn et al., *Story Points Changes in Agile Iterative Development*, 2022, DOI `10.1007/s10664-022-10192-9` | 19,349 work items; about 10% changed points, often after scope/information changes. ([link.springer.com](https://link.springer.com/article/10.1007/s10664-022-10192-9)) | Seven open-source projects. |
| `E14` | DORA, *Software Delivery Performance Metrics*, updated 2026 | Throughput and instability measures plus explicit warnings against targets, competition and dissimilar comparisons. ([dora.dev](https://dora.dev/guides/dora-metrics/)) | Primarily observational and software-service oriented. |
| `E15` | Nicole Forsgren et al., *The SPACE of Developer Productivity*, 2021 | Productivity cannot be represented by one metric or dimension. ([microsoft.com](https://www.microsoft.com/en-us/research/publication/the-space-of-developer-productivity-theres-more-to-it-than-you-think/)) | Framework guides measurement; it does not settle all causal relationships. |
| `E16` | Vickie Zhang et al., *Evaluating the Surrogate Index Using 200 A/B Tests at Netflix*, arXiv `2311.11922v2`, 2024 | Compares 14-day surrogate decisions with day-63 effects across 1,098 arms. ([arxiv.org](https://arxiv.org/html/2311.11922v2)) | Netflix setting and imperfect launch-decision recall. |
| `E17` | Pavel Dmitriev et al., *Pitfalls of Long-Term Online Controlled Experiments*, 2016 | Long experiments face survivorship, selection, cookie-stability and trend problems. ([microsoft.com](https://www.microsoft.com/en-us/research/publication/pitfalls-of-long-term-online-controlled-experiments/)) | Online experimentation setting. |
| `E18` | Susan Athey, Raj Chetty, Guido Imbens and Hyungseung Kang, *The Surrogate Index*, 2025 | Short proxies identify long-term effects only under stated surrogacy assumptions and validation. ([restud.com](https://www.restud.com/the-surrogate-index-combining-short-term-proxies-to-estimate-long-term-treatment-effects-more-rapidly-and-precisely/)) | Assumption violations introduce bias. |

### Standards and high-assurance sources

| ID | Source | Claim and exact locator | Boundary |
|---|---|---|---|
| `S01` | NASA, *NPR 7150.2D Software Engineering Requirements*, effective 2022–2027 | Chapter 1.1.4 says no specific lifecycle model is required; later requirements retain architecture, risk, test, configuration, records and assurance obligations. ([nodis3.gsfc.nasa.gov](https://nodis3.gsfc.nasa.gov/displayDir.cfm?Internal_ID=N_PR_7150_002D_&page_name=Chapter1)) | NASA-specific consequence profile. |
| `S02` | NIST, *SP 800-218 Secure Software Development Framework v1.1*, 2022, DOI `10.6028/NIST.SP.800-218` | Security practices are integrated into every SDLC because most lifecycle models omit sufficient security detail. ([csrc.nist.gov](https://csrc.nist.gov/pubs/sp/800/218/final)) | High-level practices require tailoring. |
| `S03` | FDA, *Content of Premarket Submissions for Device Software Functions*, June 2023 | Introduction and risk-based documentation sections require safety/effectiveness evidence generated through development, verification and validation. ([fda.gov](https://www.fda.gov/media/153781/download)) | Nonbinding guidance within regulated device context. |
| `S04` | NASA, *Independent Verification and Validation Overview*, current | IV&V provides independent technical, managerial and financial assessment throughout the lifecycle. ([nasa.gov](https://www.nasa.gov/ivv-overview/)) | Independence intensity is risk-tailored. |

### Original-author and practitioner criticism

| ID | Source | Claim supported | Boundary |
|---|---|---|---|
| `C01` | Dave Thomas, *Agile Is Dead (Long Live Agility)*, 2014 | Commercial noun and method branding became detached from small-step feedback and adjustment. ([pragdave.me](https://pragdave.me/thoughts/active/2014-03-04-time-to-kill-agile.html)) | Retrospective argument, not prevalence study. |
| `C02` | Andy Hunt, *The Failure of Agile*, 2015 | Organisations converted “inspect and adapt” into invariant rules and failed to adapt the methods themselves. ([toolshed.com](https://toolshed.com/2015/05/the-failure-of-agile.html)) | Practitioner interpretation. |
| `C03` | Ron Jeffries, *Developers Should Abandon Agile*, 2018 | Poor corporate Agile can increase interference, pressure and defects; retain technical disciplines rather than brands. ([ronjeffries.com](https://ronjeffries.com/articles/018-01ff/abandon-1/)) | Practitioner testimony. |
| `C04` | Martin Fowler, *Flaccid Scrum*, 2009 | Scrum ceremonies without XP-like engineering allow code deterioration and declining delivery. ([martinfowler.com](https://martinfowler.com/bliki/FlaccidScrum.html)) | Anecdotal pattern report. |
| `C05` | Martin Fowler, *Agile Software Guide*, updated 2019 | Semantic diffusion, imposed process, neglected technical excellence and project organisation are principal internal criticisms. ([martinfowler.com](https://martinfowler.com/agile.html)) | Practitioner synthesis. |

---

## EVOLVED_AGILE_TIMELINE

| Date/epoch | Material development | Frozen interpretation |
|---|---|---|
| **1930s–1960s** | Shewhart/Deming improvement cycles; X-15, Mercury and IBM iterative work; executable expanding models. | Feedback, iteration and test-first work are `SHARED_ANCESTRY`, not Agile inventions. ([craiglarman.com](https://www.craiglarman.com/wiki/downloads/misc/history-of-iterative-larman-and-basili-ieee-computer.pdf)) |
| **1970s** | Iterative enhancement, large defence/avionics increments and integration engineering coexist with substantial specification. | Iteration and formal engineering are historically compatible. |
| **1976–1988** | Gilb’s measurable evolutionary delivery and Boehm’s risk-driven spiral. | Risk retirement and measurable outcomes are stronger antecedents than arbitrary calendar iteration. |
| **1980s–early 1990s** | Prototyping, RAD and object-oriented evolutionary development expand. | “Early working evidence” has several distinct purposes and evidential strengths. |
| **1986** | Takeuchi and Nonaka describe overlapping, cross-functional product development. | Direct influence on Scrum, but not evidence that one team form fits every product. |
| **1994–2000** | DSDM, Scrum, XP, Crystal, FDD, ASD and neighbouring iterative methods emerge. | The pre-Manifesto field is plural: governance-heavy, management-focused and engineering-focused approaches coexist. |
| **1995–1999** | Scrum formalises empirical management; XP formalises a technical changeability system. | Management cadence and engineering capability must not be conflated. |
| **2001** | Manifesto and twelve principles create a thin common declaration. | Values and principles, not an executable method. |
| **2003** | Lean software imports waste, learning, delayed commitment, flow and whole-system optimisation. | `HYBRID`, not merely a later Scrum practice. |
| **2006 onward** | Software Kanban makes WIP, cycle time, pull and continuous flow explicit. | Fixed iteration is contextually replaced while feedback and exposure control survive. |
| **2008 onward** | Empirical reviews find encouraging but weak whole-method evidence. | Universal method claims are not justified. |
| **2009–2010** | DevOps and Continuous Delivery extend responsibility to deployment and operations. | “Working software” becomes integrated, deployable and operationally observed. |
| **2010s** | Evolutionary architecture, product mode and continuous discovery address design erosion and output bias. | Earlier principles are narrowed and supplied with missing controls. |
| **2014–2019** | Manifesto authors and early practitioners attack branding, certification, faux-Agile and flaccid Scrum. | The movement’s own authors separate agility from the Agile industry. |
| **2016 onward** | SRE supplies SLO/error-budget controls and disciplined incident learning. | `CONVERGENT_ENGINEERING`, later hybridised with delivery practice. |
| **2020 onward** | Platforms and Team Topologies respond to overloaded local ownership and organisation-level flow. | Autonomy is bounded by cognitive load, shared services and system architecture. |
| **2022–2026** | Current security, safety and regulatory sources remain lifecycle-neutral but evidence-strict. | Adaptive development survives inside risk-governed assurance systems. |
| **2024** | Large scaling comparison finds framework selection practically negligible after controls. | Scaling problems are real; branded framework choice is not a surviving general property. |

## EVOLVED_AGILE_GENEALOGY

```text
quality-improvement feedback
        ├── iterative/incremental development
        │     ├── evolutionary delivery
        │     ├── risk-driven spiral
        │     ├── prototyping/RAD
        │     └── object-oriented evolutionary development
        │
overlapping product development ── pre-2001 Scrum
software craft/testing/refactoring ── Extreme Programming
DSDM / Crystal / FDD / ASD / related lightweight methods
        │
        └──────── 2001 AGILE MANIFESTO
                         │
                         ├── Scrum-dominant organisational diffusion
                         ├── Lean-software hybrid
                         ├── software-Kanban flow hybrid/reaction
                         ├── CI → Continuous Delivery generalisation
                         ├── DevOps reaction to development/operations split
                         ├── continuous discovery reaction to delivery bias
                         ├── product mode reaction to project handoff
                         ├── evolutionary-architecture correction
                         └── platform/team-topology organisational hybrid

independent reliability engineering ── SRE ── later delivery hybrid
systems/safety/security engineering ── risk-governed adaptive hybrids
```

| Tradition | Relationship classification | Reason |
|---|---|---|
| Iterative and incremental development | `SHARED_ANCESTRY` | Predates and supplies recurring feedback/increment mechanisms. |
| Evolutionary delivery | `SHARED_ANCESTRY` | Direct antecedent to measurable incremental value and stopping. |
| Spiral development | `SHARED_ANCESTRY` and later `HYBRID` | Risk governs sequencing and commitment. |
| Prototyping and RAD | `SHARED_ANCESTRY` | Early learning and timeboxing, but not identical production-delivery logic. |
| Scrum, XP, Crystal, DSDM, FDD, ASD | `DIRECT_LINEAGE` | Represented in or immediately surrounding the Manifesto coalition. |
| Lean software | `HYBRID` | Combines Lean/Toyota/quality ancestry with adaptive software development. |
| Software Kanban | `HYBRID` and `REACTION_TO_AGILE` | Imports flow/WIP controls and rejects fixed iteration as a universal default. |
| Continuous Delivery | `HYBRID` and `GENERALISATION` | Combines XP/CI, automation, Lean batches and release engineering. |
| DevOps | `REACTION_TO_AGILE` and `HYBRID` | Corrects the development-only boundary and operational handoff. |
| SRE | `CONVERGENT_ENGINEERING` | Originates in reliability operations rather than Manifesto lineage. |
| Continuous discovery | `REACTION_TO_AGILE` and `HYBRID` | Corrects backlog delivery and customer-proxy bias using product/UX research. |
| Product operating models | `REACTION_TO_AGILE` and `HYBRID` | Replaces temporary scope delivery with durable outcome ownership. |
| Platform engineering | `CONVERGENT_ENGINEERING` and `HYBRID` | Corrects duplicated operational burden and cognitive overload. |
| Safety, security and regulated assurance | `CONVERGENT_ENGINEERING` and `HYBRID` | Supply obligations that Agile values did not discharge. |
| Generic “agility” outside documented ancestry | `ONLY_ANALOGOUS` | Shared vocabulary alone does not establish lineage. |

## EVOLVED_AGILE_PROPERTY_LEDGER

The following YAML is the frozen, machine-readable property ledger. Source identifiers resolve to the cited register above.

```yaml
EVOLVED_AGILE_PROPERTY_LEDGER:
  denominator: 28
  examined: 28

  properties:
    - PROPERTY_ID: EA-01
      PROPERTY_NAME: Actionability-weighted feedback-loop selection
      HISTORICAL_ORIGIN: [H01, H02, H03, H08, H10]
      ORIGINAL_FORM: "Short iterations, frequent delivery, inspection and adaptation."
      PROBLEM_IT_ADDRESSED: "Commitment accumulated before assumptions were tested against reality."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Late discovery, sunk-cost lock-in and long open-loop development."
      MECHANISM: "Select a feedback loop whose evidence is informative, affordable, actionable and early enough to alter a still-reversible decision."
      TRIGGER_OR_CONTEXT: "Material uncertainty exists and near-term evidence could change a decision."
      NON_TRIGGER_OR_CHEAP_PATH: "For stable routine work or costly/noisy feedback, use sampling, simulation, milestone review or a longer risk-aligned cadence."
      DEPENDENCIES_OR_PRECONDITIONS: ["observable result", "decision authority", "defined claim", "remaining reversibility"]
      EXPECTED_ENGINEERING_PAYOFF: "Earlier correction with less accumulated rework and commitment."
      KNOWN_FAILURE_MODES: ["cadence overhead", "noisy feedback", "deadline pressure", "local feedback that ignores system effects"]
      IMPORTANT_CRITICISMS: "Shorter is not monotonically better; one cadence cannot serve code, product, strategy, qualification and long outcomes."
      HOW_THE_PROPERTY_EVOLVED: "One iteration clock became a portfolio of technical, integration, product, planning, release and outcome loops."
      MATURE_OR_EVOLVED_FORM: "Minimise decision-relevant feedback latency, not calendar duration."
      CEREMONY_VS_PROPERTY: "A sprint is one implementation; it is not the property."
      CURRENT_STATUS: RETAINED_IN_EVOLVED_FORM
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H01, H02, H03, H08, H10]
      CRITICAL_SOURCES: [E04, C02]
      EMPIRICAL_SOURCES: [E01, E03, E04]
      OPEN_QUESTIONS: ["Domain-specific cadence economics and attention costs remain undermeasured."]

    - PROPERTY_ID: EA-02
      PROPERTY_NAME: Integrated working evidence
      HISTORICAL_ORIGIN: [H01, H03, H06, H08, H10]
      ORIGINAL_FORM: "Working software and usable increments as the primary evidence of progress."
      PROBLEM_IT_ADDRESSED: "Documents, task completion and component demonstrations masqueraded as integrated progress."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Late integration and false confidence in disconnected artefacts."
      MECHANISM: "Regularly exercise the integrated system against the behaviour relevant to the current decision."
      TRIGGER_OR_CONTEXT: "Components interact, feasibility is uncertain or progress claims depend on actual behaviour."
      NON_TRIGGER_OR_CHEAP_PATH: "Use a prototype, model, proof or simulation when that is the cheapest evidence appropriate to the claim."
      DEPENDENCIES_OR_PRECONDITIONS: ["configuration identity", "representative environment", "test oracle", "known evidence scope"]
      EXPECTED_ENGINEERING_PAYOFF: "Earlier exposure of incompatibility, infeasibility and misunderstanding."
      KNOWN_FAILURE_MODES: ["demo theatre", "happy-path-only evidence", "mocked dependencies mistaken for integration", "working mistaken for valuable or safe"]
      IMPORTANT_CRITICISMS: "Executable behaviour does not by itself establish usefulness, reliability, security or qualification."
      HOW_THE_PROPERTY_EVOLVED: "Working increment became integrated, verified, deployable and operationally observable evidence."
      MATURE_OR_EVOLVED_FORM: "Match the evidence state to the claim being made."
      CEREMONY_VS_PROPERTY: "A sprint demo is optional and can fail to provide integrated evidence."
      CURRENT_STATUS: STRONGLY_RETAINED
      EVIDENCE_STRENGTH: MODERATE_TO_STRONG_CONVERGENT
      PRIMARY_SOURCES: [H01, H06, H08, H10, H15]
      CRITICAL_SOURCES: [C04, E09]
      EMPIRICAL_SOURCES: [E08, E09, E12]
      OPEN_QUESTIONS: ["How should evidence sufficiency be expressed across mixed software/hardware systems?"]

    - PROPERTY_ID: EA-03
      PROPERTY_NAME: Risk-driven sequencing and early risk retirement
      HISTORICAL_ORIGIN: [H02, H03, H01]
      ORIGINAL_FORM: "Evolutionary steps and spiral cycles ordered by risk."
      PROBLEM_IT_ADDRESSED: "Low-risk feature work advanced while assumptions capable of invalidating the programme remained unresolved."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Catastrophic late discovery after major investment."
      MECHANISM: "Identify high-exposure assumptions and perform the cheapest discriminating work before dependent commitment."
      TRIGGER_OR_CONTEXT: "Novel technology, architecture, supplier, safety, usability, scale or requirements risk."
      NON_TRIGGER_OR_CHEAP_PATH: "For repetitive low-risk work, normal value/flow ordering may suffice."
      DEPENDENCIES_OR_PRECONDITIONS: ["explicit risk model", "authority to reorder work", "discriminating evidence"]
      EXPECTED_ENGINEERING_PAYOFF: "Reduced expected loss and earlier cancellation or redesign."
      KNOWN_FAILURE_MODES: ["risk register theatre", "confusing urgency with risk", "never converting learning into a decision"]
      IMPORTANT_CRITICISMS: "Risk scores can be subjective and can suppress user value if treated as the only ordering rule."
      HOW_THE_PROPERTY_EVOLVED: "Risk-driven development was combined with value, flow, architecture and assurance decisions."
      MATURE_OR_EVOLVED_FORM: "Order irreversible commitment by exposure reduction; order routine flow by value and delay."
      CEREMONY_VS_PROPERTY: "A risk workshop or spike is optional; retirement of risk is the property."
      CURRENT_STATUS: STRONGLY_RETAINED
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H02, H03, H24, H25]
      CRITICAL_SOURCES: [E07]
      EMPIRICAL_SOURCES: [E07, E12]
      OPEN_QUESTIONS: ["Comparative evidence for risk-first versus value-first sequencing remains sparse."]

    - PROPERTY_ID: EA-04
      PROPERTY_NAME: Economically small incremental batches
      HISTORICAL_ORIGIN: [H01, H03, H06, H12, H15]
      ORIGINAL_FORM: "Small releases, short increments and frequent delivery."
      PROBLEM_IT_ADDRESSED: "Large handoffs accumulated delay, integration risk and costly diagnosis."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Late defect discovery, large sunk cost and difficult rollback."
      MECHANISM: "Reduce the unit of build, integration or exposure until marginal learning/reversal benefit no longer exceeds transaction and qualification cost."
      TRIGGER_OR_CONTEXT: "Queueing, changing requirements, expensive integration failure or high reversal value."
      NON_TRIGGER_OR_CHEAP_PATH: "Where fabrication, mobilisation or certification has irreducible setup cost, batch the expensive boundary while keeping upstream evidence smaller."
      DEPENDENCIES_OR_PRECONDITIONS: ["modularity", "automation or reduced handoff cost", "coherent value slicing"]
      EXPECTED_ENGINEERING_PAYOFF: "Shorter delay, easier diagnosis, less inventory and cheaper reversal."
      KNOWN_FAILURE_MODES: ["fragmented non-value slices", "transaction-cost explosion", "micro-release overhead", "qualification repeated without benefit"]
      IMPORTANT_CRITICISMS: "Small batches are not intrinsically cheap and may not correspond to a useful or qualifiable increment."
      HOW_THE_PROPERTY_EVOLVED: "Calendar-small releases became economically and assurance-meaningful batch design."
      MATURE_OR_EVOLVED_FORM: "Use the smallest coherent batch justified by total economics and consequence."
      CEREMONY_VS_PROPERTY: "A story or sprint is not automatically a batch of value."
      CURRENT_STATUS: CONTEXT_DEPENDENT
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H03, H12, H15]
      CRITICAL_SOURCES: [E04, E12]
      EMPIRICAL_SOURCES: [E08, E12]
      OPEN_QUESTIONS: ["Quantitative batch optima under certification, hardware and field-test cost remain domain-specific."]

    - PROPERTY_ID: EA-05
      PROPERTY_NAME: Explicit work-in-progress and flow control
      HISTORICAL_ORIGIN: [H12, H13]
      ORIGINAL_FORM: "Pull work, limit WIP and measure cycle time."
      PROBLEM_IT_ADDRESSED: "Too much work was started, queues were hidden and ageing work received no control."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Congestion, context switching, long lead time and unfinished inventory."
      MECHANISM: "Define start/finish, control concurrent work and use age/cycle-time evidence to unblock or stop work."
      TRIGGER_OR_CONTEXT: "Demand exceeds capacity, work waits between specialities or ageing work is common."
      NON_TRIGGER_OR_CHEAP_PATH: "A very small, naturally serial workflow may need only an informal one-item focus rule."
      DEPENDENCIES_OR_PRECONDITIONS: ["visible workflow", "stable start/finish definitions", "authority to stop starting"]
      EXPECTED_ENGINEERING_PAYOFF: "Shorter and more predictable flow, earlier blocker exposure and less switching."
      KNOWN_FAILURE_MODES: ["gaming item size", "hidden queues outside the board", "local flow that harms global value", "limits ignored under urgency"]
      IMPORTANT_CRITICISMS: "Throughput and cycle time are not value, quality or outcome measures."
      HOW_THE_PROPERTY_EVOLVED: "Iteration capacity became continuous system-level flow management."
      MATURE_OR_EVOLVED_FORM: "Control WIP across the actual end-to-end system and pair flow with quality and outcome evidence."
      CEREMONY_VS_PROPERTY: "A Kanban board is a representation; WIP control is the property."
      CURRENT_STATUS: RETAINED_IN_EVOLVED_FORM
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H12, H13]
      CRITICAL_SOURCES: [E14]
      EMPIRICAL_SOURCES: [E06, E07, E14]
      OPEN_QUESTIONS: ["How should heterogeneous work classes be aggregated without making flow metrics meaningless?"]

    - PROPERTY_ID: EA-06
      PROPERTY_NAME: Automated regression verification
      HISTORICAL_ORIGIN: [H01, H06, H11, H14]
      ORIGINAL_FORM: "Test-first work, TDD and automated unit/acceptance tests."
      PROBLEM_IT_ADDRESSED: "Every change could silently invalidate prior behaviour."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Regression fear, delayed testing and change paralysis."
      MECHANISM: "Encode fast repeatable checks at suitable levels and execute them when relevant change occurs."
      TRIGGER_OR_CONTEXT: "Software or programmable behaviour changes repeatedly and regressions are material."
      NON_TRIGGER_OR_CHEAP_PATH: "For throwaway exploration or unautomatable physical behaviour, use targeted manual, simulation or sampled verification."
      DEPENDENCIES_OR_PRECONDITIONS: ["testable design", "credible oracles", "maintained test data", "manageable execution time"]
      EXPECTED_ENGINEERING_PAYOFF: "Faster defect localisation and safer change."
      KNOWN_FAILURE_MODES: ["flaky tests", "overfitting to implementation", "false coverage confidence", "disabled checks", "maintenance burden"]
      IMPORTANT_CRITICISMS: "TDD's red-green-refactor sequence is not universally superior; productivity effects are mixed."
      HOW_THE_PROPERTY_EVOLVED: "A named test-first practice was generalised into risk-appropriate automated regression."
      MATURE_OR_EVOLVED_FORM: "Automate repeated high-value verification while preserving exploratory and independent testing."
      CEREMONY_VS_PROPERTY: "TDD is one implementation; automated regression is the surviving property."
      CURRENT_STATUS: STRONGLY_RETAINED
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H06, H11, H14, H15]
      CRITICAL_SOURCES: [E09, E10]
      EMPIRICAL_SOURCES: [E08, E09, E10]
      OPEN_QUESTIONS: ["Optimal test portfolios and acceptable feedback time remain system-specific."]

    - PROPERTY_ID: EA-07
      PROPERTY_NAME: Frequent real integration and a healthy mainline
      HISTORICAL_ORIGIN: [H01, H06, H11, H14]
      ORIGINAL_FORM: "Continuous integration and collective integration several times per day."
      PROBLEM_IT_ADDRESSED: "Long-lived isolation allowed incompatible work to accumulate."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Integration hell, divergent assumptions and unreleasable branches."
      MECHANISM: "Merge into an authoritative mainline frequently, run credible verification and repair failures immediately."
      TRIGGER_OR_CONTEXT: "Multiple changes or contributors interact in a shared system."
      NON_TRIGGER_OR_CHEAP_PATH: "A solo or low-change system may integrate at each coherent change rather than on a clock."
      DEPENDENCIES_OR_PRECONDITIONS: ["version control", "automated build", "fast regression feedback", "mainline authority"]
      EXPECTED_ENGINEERING_PAYOFF: "Reduced merge complexity, faster incompatibility detection and a known integrated state."
      KNOWN_FAILURE_MODES: ["CI server without integration", "long-lived branches", "ignored red builds", "arbitrarily skipped stages"]
      IMPORTANT_CRITICISMS: "Frequent merging without credible tests merely moves instability faster."
      HOW_THE_PROPERTY_EVOLVED: "XP CI became trunk-oriented integration, deployment pipelines and cross-environment verification."
      MATURE_OR_EVOLVED_FORM: "Keep an authoritative integrated state healthy enough to support the next decision."
      CEREMONY_VS_PROPERTY: "A green badge is not the property; real integration and truthful health are."
      CURRENT_STATUS: STRONGLY_RETAINED
      EVIDENCE_STRENGTH: MODERATE_TO_STRONG_CONVERGENT
      PRIMARY_SOURCES: [H06, H14, H15]
      CRITICAL_SOURCES: [E09, C04]
      EMPIRICAL_SOURCES: [E08, E09, E12]
      OPEN_QUESTIONS: ["The appropriate integration boundary in very large product lines remains contextual."]

    - PROPERTY_ID: EA-08
      PROPERTY_NAME: Maintained technical changeability
      HISTORICAL_ORIGIN: [H06, H11, H14, H23]
      ORIGINAL_FORM: "Refactoring, simple design, collective ownership and technical debt control."
      PROBLEM_IT_ADDRESSED: "The cost and danger of change rose with every feature."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Architectural erosion, regression-prone code and eventual inability to adapt."
      MECHANISM: "Continuously restructure behaviour-preservingly, remove friction and budget deliberate debt repayment."
      TRIGGER_OR_CONTEXT: "The system is expected to evolve and internal quality is slowing safe change."
      NON_TRIGGER_OR_CHEAP_PATH: "For a disposable prototype or imminently retired component, isolate or replace rather than perfect it."
      DEPENDENCIES_OR_PRECONDITIONS: ["EA-06", "EA-07", "design skill", "capacity authority"]
      EXPECTED_ENGINEERING_PAYOFF: "A flatter long-run change-cost curve and lower regression risk."
      KNOWN_FAILURE_MODES: ["unbounded polishing", "unsafe large rewrites", "debt registers without repayment", "local cleanliness that ignores system design"]
      IMPORTANT_CRITICISMS: "Refactoring benefits are difficult to isolate empirically; short-term feature incentives can suppress it."
      HOW_THE_PROPERTY_EVOLVED: "Simple design became explicit changeability investment, debt economics and architectural fitness."
      MATURE_OR_EVOLVED_FORM: "Preserve the options that future evidence is likely to require."
      CEREMONY_VS_PROPERTY: "A refactoring sprint or debt backlog is optional and can itself become theatre."
      CURRENT_STATUS: RETAINED_IN_EVOLVED_FORM
      EVIDENCE_STRENGTH: MIXED_TO_MODERATE
      PRIMARY_SOURCES: [H06, H11, H23]
      CRITICAL_SOURCES: [C04, C05]
      EMPIRICAL_SOURCES: [E08, E10]
      OPEN_QUESTIONS: ["Reliable economic measures of changeability investment remain immature."]

    - PROPERTY_ID: EA-09
      PROPERTY_NAME: Architecture proportional to irreversibility and coupling
      HISTORICAL_ORIGIN: [H02, H24, H25, H26, H23]
      ORIGINAL_FORM: "Risk-driven architecture, architecture-centred development and evolutionary design."
      PROBLEM_IT_ADDRESSED: "Either premature comprehensive design or uncontrolled local emergence governed every decision."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Expensive lock-in, system incoherence and architecture-by-accident."
      MECHANISM: "Classify decisions by reversibility, blast radius and quality-attribute trade-offs; analyse costly commitments and continuously test evolvable constraints."
      TRIGGER_OR_CONTEXT: "Public interfaces, persistent data, safety/security boundaries, high coupling, long asset life or expensive migration."
      NON_TRIGGER_OR_CHEAP_PATH: "For local reversible decisions, use simple design, short experiments and automated fitness checks."
      DEPENDENCIES_OR_PRECONDITIONS: ["quality-attribute scenarios", "system boundary", "decision records", "architecture authority"]
      EXPECTED_ENGINEERING_PAYOFF: "Reduced irreversible rework while preserving evolution where it remains cheap."
      KNOWN_FAILURE_MODES: ["analysis paralysis", "architecture astronautics", "emergent-only entropy", "fitness metrics that miss real qualities"]
      IMPORTANT_CRITICISMS: "No universal numeric threshold identifies when deliberate architecture becomes worthwhile."
      HOW_THE_PROPERTY_EVOLVED: "The emergent-versus-up-front dispute became a portfolio of deliberate commitments and evolutionary constraints."
      MATURE_OR_EVOLVED_FORM: "Deliberate architecture in proportion to commitment cost, coupled to continuous fitness evidence."
      CEREMONY_VS_PROPERTY: "An architecture board or diagram is neither necessary nor sufficient."
      CURRENT_STATUS: RETAINED_IN_EVOLVED_FORM
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H02, H23, H24, H25, H26]
      CRITICAL_SOURCES: [E07, C04]
      EMPIRICAL_SOURCES: [E07, E12]
      OPEN_QUESTIONS: ["A generally validated architecture-investment threshold remains unresolved."]

    - PROPERTY_ID: EA-10
      PROPERTY_NAME: Release-ready state with deployment and release decoupled
      HISTORICAL_ORIGIN: [H14, H15, H16]
      ORIGINAL_FORM: "Continuous Delivery and an always-deployable mainline."
      PROBLEM_IT_ADDRESSED: "Release was an exceptional integration event tied to iteration or project completion."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Release fear, manual drift, large deployment batches and unavailable rollback."
      MECHANISM: "Continuously build, verify and package an authoritative candidate while making exposure a separate authorised decision."
      TRIGGER_OR_CONTEXT: "Software can be reproduced and staged more frequently than it should be exposed."
      NON_TRIGGER_OR_CHEAP_PATH: "For hardware or regulated releases, maintain reproducible qualified candidates without pretending physical release is continuous."
      DEPENDENCIES_OR_PRECONDITIONS: ["EA-06", "EA-07", "environment/configuration control", "deployment automation"]
      EXPECTED_ENGINEERING_PAYOFF: "Lower release transaction cost, reduced batch risk and flexible exposure timing."
      KNOWN_FAILURE_MODES: ["false green pipeline", "environment mismatch", "manual hidden steps", "database incompatibility"]
      IMPORTANT_CRITICISMS: "Automation can rapidly propagate insufficiently verified change."
      HOW_THE_PROPERTY_EVOLVED: "Sprint completion was separated from technical deployability and business release."
      MATURE_OR_EVOLVED_FORM: "Continuously prove release readiness; expose only under appropriate authority and risk."
      CEREMONY_VS_PROPERTY: "A sprint review or release train is not release readiness."
      CURRENT_STATUS: STRONGLY_RETAINED
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H14, H15, H16]
      CRITICAL_SOURCES: [E09, S01, S03]
      EMPIRICAL_SOURCES: [E08, E09, E12, E14]
      OPEN_QUESTIONS: ["How much of release readiness can be automated in high-assurance systems?"]

    - PROPERTY_ID: EA-11
      PROPERTY_NAME: Progressive exposure and operational reversibility
      HISTORICAL_ORIGIN: [H15, H17]
      ORIGINAL_FORM: "Canaries, phased rollout, feature controls and rollback."
      PROBLEM_IT_ADDRESSED: "A change reached its full population before real-environment hazards were known."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Large blast radius and slow recovery from latent defects."
      MECHANISM: "Expose change in bounded stages, observe guardrails and preserve a tested recovery or containment path."
      TRIGGER_OR_CONTEXT: "Production effects are uncertain and exposure can be segmented or reversed."
      NON_TRIGGER_OR_CHEAP_PATH: "For irreversible, physical or safety-critical exposure, use simulation, qualification and controlled pilots before deployment."
      DEPENDENCIES_OR_PRECONDITIONS: ["observability", "compatible state transitions", "rollback/containment", "release authority"]
      EXPECTED_ENGINEERING_PAYOFF: "Reduced blast radius and faster detection of production-only effects."
      KNOWN_FAILURE_MODES: ["flag debt", "untested rollback", "non-reversible data change", "biased pilot population"]
      IMPORTANT_CRITICISMS: "A canary is not safe when the hazard is rare, delayed or irreversible."
      HOW_THE_PROPERTY_EVOLVED: "Frequent release became risk-bounded exposure rather than universal continuous deployment."
      MATURE_OR_EVOLVED_FORM: "Choose exposure size and reversal mechanism according to consequence and observability."
      CEREMONY_VS_PROPERTY: "A feature flag is one implementation and requires lifecycle control."
      CURRENT_STATUS: CONTEXT_DEPENDENT
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H15, H17]
      CRITICAL_SOURCES: [E17, S03]
      EMPIRICAL_SOURCES: [E12, E14]
      OPEN_QUESTIONS: ["Rare-event and long-latency rollout safety remains difficult to infer from small cohorts."]

    - PROPERTY_ID: EA-12
      PROPERTY_NAME: Direct problem, user and environment evidence
      HISTORICAL_ORIGIN: [H03, H08, H19]
      ORIGINAL_FORM: "On-site customer, customer collaboration and frequent demonstrations."
      PROBLEM_IT_ADDRESSED: "Requirements passed through proxies without confronting actual use."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Efficient delivery of misunderstood or irrelevant functionality."
      MECHANISM: "Expose the people making product decisions to representative users, workflows, behaviour and operating environments."
      TRIGGER_OR_CONTEXT: "Need, usability, adoption or workflow assumptions are uncertain."
      NON_TRIGGER_OR_CHEAP_PATH: "For mandated or stable requirements, use representative acceptance evidence and domain expertise without artificial weekly interviews."
      DEPENDENCIES_OR_PRECONDITIONS: ["representative access", "research competence", "decision authority", "ethical/privacy controls"]
      EXPECTED_ENGINEERING_PAYOFF: "Earlier rejection of false assumptions and better problem framing."
      KNOWN_FAILURE_MODES: ["fake customer proxy", "convenience samples", "vocal-user bias", "feedback without decision effect"]
      IMPORTANT_CRITICISMS: "Direct feedback does not replace strategy, domain expertise, ethics or delayed-outcome evidence."
      HOW_THE_PROPERTY_EVOLVED: "A single customer representative became continuous discovery and behavioural outcome evidence."
      MATURE_OR_EVOLVED_FORM: "Use multiple direct evidence channels appropriate to the decision and population."
      CEREMONY_VS_PROPERTY: "User-story syntax and a weekly interview quota are not the property."
      CURRENT_STATUS: RETAINED_IN_EVOLVED_FORM
      EVIDENCE_STRENGTH: MIXED
      PRIMARY_SOURCES: [H03, H08, H19]
      CRITICAL_SOURCES: [E07, E17]
      EMPIRICAL_SOURCES: [E01, E16, E17]
      OPEN_QUESTIONS: ["Independent causal evidence for continuous-discovery packages remains limited."]

    - PROPERTY_ID: EA-13
      PROPERTY_NAME: Evidence-triggered multi-horizon planning and reprioritisation
      HISTORICAL_ORIGIN: [H02, H03, H07, H08, H10]
      ORIGINAL_FORM: "Adaptive planning and responding to change."
      PROBLEM_IT_ADDRESSED: "Detailed long-range plans remained authoritative after their assumptions failed."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Plan-conformance waste and inability to exploit material new evidence."
      MECHANISM: "Keep long-horizon intent stable enough to coordinate, detail near-term work, and change commitments when evidence exceeds switching cost."
      TRIGGER_OR_CONTEXT: "Material assumptions remain uncertain or external conditions can change."
      NON_TRIGGER_OR_CHEAP_PATH: "For fixed legal, physical or contractual commitments, adapt implementation and risk response while preserving the constraint."
      DEPENDENCIES_OR_PRECONDITIONS: ["clear strategy", "decision rights", "switching-cost visibility", "WIP control"]
      EXPECTED_ENGINEERING_PAYOFF: "Less false precision without surrendering direction and coordination."
      KNOWN_FAILURE_MODES: ["strategic thrashing", "continuous interruption", "no stable goal", "change justified by opinion rather than evidence"]
      IMPORTANT_CRITICISMS: "Responding to change is often misread as anti-planning or permission for arbitrary reprioritisation."
      HOW_THE_PROPERTY_EVOLVED: "Single backlog ordering became rolling-wave plans across strategic, product, architecture and delivery horizons."
      MATURE_OR_EVOLVED_FORM: "Change plans at the cheapest horizon that can absorb the new evidence."
      CEREMONY_VS_PROPERTY: "Sprint planning and backlog refinement are optional implementations."
      CURRENT_STATUS: RETAINED_IN_EVOLVED_FORM
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H02, H03, H07, H08, H10]
      CRITICAL_SOURCES: [E04, E13]
      EMPIRICAL_SOURCES: [E02, E03, E04]
      OPEN_QUESTIONS: ["Evidence thresholds for interrupting in-progress work remain weakly operationalised."]

    - PROPERTY_ID: EA-14
      PROPERTY_NAME: Long-latency outcome and proxy governance
      HISTORICAL_ORIGIN: [H19, H20, E16, E18]
      ORIGINAL_FORM: "Outcome-oriented product development and experimentation."
      PROBLEM_IT_ADDRESSED: "Short-cycle activity or engagement metrics substituted for the delayed objective."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Optimising a proxy that is neutral or harmful to the real outcome."
      MECHANISM: "Define the long outcome, validate surrogate relationships, retain delayed follow-up or holdouts, and monitor proxy drift."
      TRIGGER_OR_CONTEXT: "The true outcome arrives after the delivery or decision cadence."
      NON_TRIGGER_OR_CHEAP_PATH: "Use the directly observed outcome when it is timely; when no valid proxy exists, preserve uncertainty and wait or use qualified models."
      DEPENDENCIES_OR_PRECONDITIONS: ["causal model", "longitudinal data", "population stability", "guardrails"]
      EXPECTED_ENGINEERING_PAYOFF: "Faster decisions without silently abandoning long-term value."
      KNOWN_FAILURE_MODES: ["surrogacy violation", "selection bias", "novelty effects", "metric drift", "premature launch"]
      IMPORTANT_CRITICISMS: "Neither short proxies nor long experiments are automatically trustworthy."
      HOW_THE_PROPERTY_EVOLVED: "Rapid customer feedback was constrained by causal and longitudinal validation."
      MATURE_OR_EVOLVED_FORM: "Operate short and long evidence loops together and quantify their inferential gap."
      CEREMONY_VS_PROPERTY: "An OKR review or experiment dashboard is not proof of proxy validity."
      CURRENT_STATUS: RETAINED_IN_EVOLVED_FORM
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H19, H20]
      CRITICAL_SOURCES: [E17, E18]
      EMPIRICAL_SOURCES: [E16, E17, E18]
      OPEN_QUESTIONS: ["Validated surrogates are domain- and intervention-specific."]

    - PROPERTY_ID: EA-15
      PROPERTY_NAME: Guarded experimentation with stopping rules
      HISTORICAL_ORIGIN: [H02, H03, H19]
      ORIGINAL_FORM: "Prototype, spike, experiment and test-and-learn."
      PROBLEM_IT_ADDRESSED: "Teams committed to solutions before discriminating among assumptions."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Large investment in invalid solutions and post-hoc interpretation of ambiguous trials."
      MECHANISM: "State hypothesis, decision rule, population, guardrails and stop conditions before bounded exposure."
      TRIGGER_OR_CONTEXT: "A material uncertain choice can be tested ethically, safely and reversibly."
      NON_TRIGGER_OR_CHEAP_PATH: "For dangerous or irreversible interventions, use analysis, simulation, independent review or restricted qualification."
      DEPENDENCIES_OR_PRECONDITIONS: ["measurement design", "sufficient power or qualitative discrimination", "ethical authority", "reversal/containment"]
      EXPECTED_ENGINEERING_PAYOFF: "Cheaper rejection, lower sunk cost and more credible learning."
      KNOWN_FAILURE_MODES: ["p-hacking", "underpowered tests", "novelty effects", "unsafe exposure", "experiments that never cause decisions"]
      IMPORTANT_CRITICISMS: "Experimentation can externalise risk and cannot resolve every strategic or moral question."
      HOW_THE_PROPERTY_EVOLVED: "Informal iteration became explicit decision experiments with operational and causal guardrails."
      MATURE_OR_EVOLVED_FORM: "Use the cheapest safe test capable of changing the decision."
      CEREMONY_VS_PROPERTY: "A discovery sprint or A/B-test count is not the property."
      CURRENT_STATUS: CONTEXT_DEPENDENT
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H02, H03, H19]
      CRITICAL_SOURCES: [E17, S03]
      EMPIRICAL_SOURCES: [E16, E17, E18]
      OPEN_QUESTIONS: ["How organisations prevent experiment-volume incentives from degrading evidence quality remains under-studied."]

    - PROPERTY_ID: EA-16
      PROPERTY_NAME: Authorised evidence-driven process adaptation
      HISTORICAL_ORIGIN: [H01, H10, H12, H13]
      ORIGINAL_FORM: "Inspect and adapt, retrospectives and continuous improvement."
      PROBLEM_IT_ADDRESSED: "The process remained fixed despite repeated evidence of delay, defects or overload."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Persistent systemic causes hidden behind recurring local heroics."
      MECHANISM: "Observe, analyse cause, authorise a process change, implement it and measure the subsequent result."
      TRIGGER_OR_CONTEXT: "Repeated friction, incident, queue or quality signal indicates a changeable system cause."
      NON_TRIGGER_OR_CHEAP_PATH: "Correct an obvious low-risk problem immediately rather than waiting for a scheduled meeting."
      DEPENDENCIES_OR_PRECONDITIONS: ["authority", "psychological safety", "capacity", "follow-up evidence"]
      EXPECTED_ENGINEERING_PAYOFF: "The work system becomes capable of correcting its own recurring failure modes."
      KNOWN_FAILURE_MODES: ["retrospective theatre", "action lists without ownership", "local change blocked by organisation", "blame"]
      IMPORTANT_CRITICISMS: "Frequent reflection does not imply learning when participants cannot change system conditions."
      HOW_THE_PROPERTY_EVOLVED: "Team retrospective became continuous, incident-based and system-level improvement."
      MATURE_OR_EVOLVED_FORM: "Close the complete observation-to-remeasurement loop at the level that owns the cause."
      CEREMONY_VS_PROPERTY: "A retrospective meeting is neither necessary nor sufficient."
      CURRENT_STATUS: STRONGLY_RETAINED
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H10, H12, H13, H18]
      CRITICAL_SOURCES: [C02, C03]
      EMPIRICAL_SOURCES: [E06, E09]
      OPEN_QUESTIONS: ["Causal attribution for process changes remains difficult when many changes occur together."]

    - PROPERTY_ID: EA-17
      PROPERTY_NAME: System-level diagnostic measurement with anti-gaming controls
      HISTORICAL_ORIGIN: [H03, H13, E14, E15]
      ORIGINAL_FORM: "Working software, velocity, flow and outcome metrics."
      PROBLEM_IT_ADDRESSED: "Managers lacked timely evidence about flow, quality, value and reliability."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Decision by anecdote or invisible deterioration."
      MECHANISM: "Use a balanced local portfolio, countermetrics, trends and qualitative interpretation; audit whether behaviour changed to optimise the number."
      TRIGGER_OR_CONTEXT: "A repeated decision would benefit from observable system state."
      NON_TRIGGER_OR_CHEAP_PATH: "Use a small qualitative review when measurement cost exceeds its decision value."
      DEPENDENCIES_OR_PRECONDITIONS: ["operational definitions", "comparable boundary", "data quality", "anti-retaliation and anti-ranking policy"]
      EXPECTED_ENGINEERING_PAYOFF: "Earlier diagnosis without collapsing performance into one proxy."
      KNOWN_FAILURE_MODES: ["Goodhart effects", "team ranking", "work-item manipulation", "measurement bureaucracy", "local optimisation"]
      IMPORTANT_CRITICISMS: "Story points, velocity, deployments and throughput are not intrinsic value or productivity units."
      HOW_THE_PROPERTY_EVOLVED: "Single output measures became balanced flow, instability, quality, human and outcome portfolios."
      MATURE_OR_EVOLVED_FORM: "Metrics remain diagnostic instruments owned by the decision loop, not production quotas."
      CEREMONY_VS_PROPERTY: "A dashboard, burndown or velocity chart is optional and can be actively harmful."
      CURRENT_STATUS: USEFUL_BUT_EASILY_GAMED
      EVIDENCE_STRENGTH: STRONG_ANTI_GAMING_RATIONALE_MIXED_MEASURE_VALIDITY
      PRIMARY_SOURCES: [H03, H13]
      CRITICAL_SOURCES: [C03, C05]
      EMPIRICAL_SOURCES: [E13, E14, E15]
      OPEN_QUESTIONS: ["Robust sociotechnical metric portfolios remain context-specific."]

    - PROPERTY_ID: EA-18
      PROPERTY_NAME: Bounded cross-functional ownership and local autonomy
      HISTORICAL_ORIGIN: [H04, H06, H10, H16]
      ORIGINAL_FORM: "Cross-functional, self-organising or self-managing teams."
      PROBLEM_IT_ADDRESSED: "Serial handoffs and distant decision authority delayed learning and action."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Waiting, information loss, responsibility gaps and permission queues."
      MECHANISM: "Place sufficient skills and authority near the work while defining system guardrails and escalation boundaries."
      TRIGGER_OR_CONTEXT: "A durable flow of work is repeatedly delayed by handoffs or external approval."
      NON_TRIGGER_OR_CHEAP_PATH: "Use a specialist shared service when expertise is rare, high-risk or too costly to duplicate, with a clear service interface."
      DEPENDENCIES_OR_PRECONDITIONS: ["coherent boundary", "decision authority", "competence", "EA-19", "EA-27 where load is high"]
      EXPECTED_ENGINEERING_PAYOFF: "Faster local decisions and clearer end-to-end responsibility."
      KNOWN_FAILURE_MODES: ["pseudo-autonomy", "cognitive overload", "duplicated infrastructure", "local optimisation", "ticket-factory management"]
      IMPORTANT_CRITICISMS: "Local autonomy cannot resolve architecture, funding, compliance or shared-platform constraints by itself."
      HOW_THE_PROPERTY_EVOLVED: "Unbounded ‘you build it, you run it’ became bounded autonomy supported by platforms and explicit interactions."
      MATURE_OR_EVOLVED_FORM: "Maximise local authority only within a supportable cognitive and system boundary."
      CEREMONY_VS_PROPERTY: "Scrum roles and a team charter do not create actual authority."
      CURRENT_STATUS: CONTEXT_DEPENDENT
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H04, H10, H16, H22]
      CRITICAL_SOURCES: [C03, E07]
      EMPIRICAL_SOURCES: [E03, E05, E06, E07]
      OPEN_QUESTIONS: ["Reliable measures of team cognitive-load capacity remain immature."]

    - PROPERTY_ID: EA-19
      PROPERTY_NAME: System-level dependency, interface and coordination control
      HISTORICAL_ORIGIN: [H02, H12, H13, H22, S01]
      ORIGINAL_FORM: "Cross-team planning, integration and architecture coordination."
      PROBLEM_IT_ADDRESSED: "Autonomous teams optimised locally while shared dependencies controlled actual delivery."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Dependency gridlock, incompatible interfaces, queue transfer and late system integration."
      MECHANISM: "Expose dependencies, assign interface authority, integrate at system boundaries and measure end-to-end rather than team-local flow."
      TRIGGER_OR_CONTEXT: "Multiple teams, suppliers or components share interfaces, resources or release constraints."
      NON_TRIGGER_OR_CHEAP_PATH: "Truly independent teams need no scaling framework; retain only lightweight interface and integration checks."
      DEPENDENCIES_OR_PRECONDITIONS: ["system boundary", "interface ownership", "EA-09", "EA-07", "cross-team authority"]
      EXPECTED_ENGINEERING_PAYOFF: "Reduced cross-team waiting and earlier system incoherence detection."
      KNOWN_FAILURE_MODES: ["coordination bureaucracy", "universal synchronisation", "dependency board without removal", "local metrics"]
      IMPORTANT_CRITICISMS: "Scaling frameworks can add ceremonies without changing architecture or dependency structure."
      HOW_THE_PROPERTY_EVOLVED: "Scrum-of-Scrums and release trains were narrowed into explicit system-flow, interface and organisational design."
      MATURE_OR_EVOLVED_FORM: "Remove avoidable dependencies; govern unavoidable ones at the smallest authoritative system level."
      CEREMONY_VS_PROPERTY: "A scaling event or framework is not the property."
      CURRENT_STATUS: STRONGLY_RETAINED
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H02, H13, H22, S01]
      CRITICAL_SOURCES: [E05, E06, E07]
      EMPIRICAL_SOURCES: [E05, E06, E07]
      OPEN_QUESTIONS: ["Comparative evidence among dependency-removal organisational designs remains limited."]

    - PROPERTY_ID: EA-20
      PROPERTY_NAME: Durable product or problem ownership
      HISTORICAL_ORIGIN: [H19, H20]
      ORIGINAL_FORM: "Product over project; long-lived outcome-oriented teams."
      PROBLEM_IT_ADDRESSED: "Temporary project teams delivered scope and handed off consequences."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Orphaned systems, output accountability and repeated relearning."
      MECHANISM: "Maintain durable responsibility for a bounded problem, product lifecycle and outcome."
      TRIGGER_OR_CONTEXT: "The capability has continuing users, operation, evolution and strategic value."
      NON_TRIGGER_OR_CHEAP_PATH: "A finite one-off build, migration or commodity procurement may remain a project with explicit acceptance and handover."
      DEPENDENCIES_OR_PRECONDITIONS: ["stable problem boundary", "outcome authority", "lifecycle funding", "operational access"]
      EXPECTED_ENGINEERING_PAYOFF: "Preserved knowledge, faster feedback and accountability beyond initial delivery."
      KNOWN_FAILURE_MODES: ["immortal teams without value", "weak strategy", "product renaming without authority", "local KPI optimisation"]
      IMPORTANT_CRITICISMS: "Product mode is not appropriate to every finite endeavour and has limited comparative causal evidence."
      HOW_THE_PROPERTY_EVOLVED: "Project delivery was hybridised with durable product and operational ownership."
      MATURE_OR_EVOLVED_FORM: "Use durability where the problem and consequences persist; use explicit handover where they do not."
      CEREMONY_VS_PROPERTY: "A Product Owner title or product roadmap does not create product ownership."
      CURRENT_STATUS: RETAINED_IN_EVOLVED_FORM
      EVIDENCE_STRENGTH: MIXED
      PRIMARY_SOURCES: [H19, H20]
      CRITICAL_SOURCES: [E05, E07]
      EMPIRICAL_SOURCES: [E05, E06]
      OPEN_QUESTIONS: ["Independent product-mode versus project-mode outcome studies remain sparse."]

    - PROPERTY_ID: EA-21
      PROPERTY_NAME: Operational observability and incident learning
      HISTORICAL_ORIGIN: [H16, H18]
      ORIGINAL_FORM: "DevOps feedback, monitoring and blameless postmortems."
      PROBLEM_IT_ADDRESSED: "Development decisions were detached from actual runtime behaviour and incidents."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Repeated failures, slow diagnosis and cost externalised to operations."
      MECHANISM: "Instrument relevant behaviour, link changes to outcomes, analyse incidents systemically and complete corrective actions."
      TRIGGER_OR_CONTEXT: "Software operates in an environment whose real behaviour cannot be completely predicted before release."
      NON_TRIGGER_OR_CHEAP_PATH: "For offline or embedded products, use field-test, maintenance, defect and service evidence."
      DEPENDENCIES_OR_PRECONDITIONS: ["telemetry", "event/configuration identity", "shared responsibility", "psychological safety"]
      EXPECTED_ENGINEERING_PAYOFF: "Faster diagnosis, recurrence reduction and design informed by actual operation."
      KNOWN_FAILURE_MODES: ["dashboard overload", "blame", "postmortem backlog", "missing causal identity", "privacy intrusion"]
      IMPORTANT_CRITICISMS: "More telemetry does not equal understanding and can create surveillance or noise."
      HOW_THE_PROPERTY_EVOLVED: "Customer collaboration expanded to operations, incidents and production behaviour."
      MATURE_OR_EVOLVED_FORM: "Collect only actionable operational evidence and feed it into authorised engineering changes."
      CEREMONY_VS_PROPERTY: "An incident review or on-call rotation is one implementation."
      CURRENT_STATUS: STRONGLY_RETAINED
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H16, H18]
      CRITICAL_SOURCES: [E09]
      EMPIRICAL_SOURCES: [E08, E09, E12, E14]
      OPEN_QUESTIONS: ["How to quantify postmortem action effectiveness without discouraging reporting remains open."]

    - PROPERTY_ID: EA-22
      PROPERTY_NAME: Explicit reliability objectives and change-risk budgets
      HISTORICAL_ORIGIN: [H17]
      ORIGINAL_FORM: "SLOs and error budgets."
      PROBLEM_IT_ADDRESSED: "Release speed and reliability were negotiated politically without an agreed control variable."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Unbounded release pressure or overengineering for unattainable perfection."
      MECHANISM: "Define user-relevant reliability, measure it and alter release behaviour as the tolerated failure budget is consumed."
      TRIGGER_OR_CONTEXT: "Online or continuously operated services face a speed–reliability trade-off."
      NON_TRIGGER_OR_CHEAP_PATH: "Safety-critical hazards require hard constraints and assurance rather than trading failures through an ordinary error budget."
      DEPENDENCIES_OR_PRECONDITIONS: ["valid SLI", "agreed SLO", "neutral measurement", "authority to slow or halt change"]
      EXPECTED_ENGINEERING_PAYOFF: "Aligned product/operations incentives and explicit release-risk control."
      KNOWN_FAILURE_MODES: ["wrong SLO", "budget treated as failure quota", "unmeasured user harm", "no authority to enforce"]
      IMPORTANT_CRITICISMS: "SLOs can omit rare, security, safety or long-latency harms."
      HOW_THE_PROPERTY_EVOLVED: "Sustainable delivery acquired a quantitative operational constraint."
      MATURE_OR_EVOLVED_FORM: "Use consequence-appropriate reliability and risk bounds that can actually constrain change."
      CEREMONY_VS_PROPERTY: "An SLO review is not the property; binding decision authority is."
      CURRENT_STATUS: RETAINED_IN_EVOLVED_FORM
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H17]
      CRITICAL_SOURCES: [S01, S03]
      EMPIRICAL_SOURCES: [E14]
      OPEN_QUESTIONS: ["Generalising error-budget economics beyond online services remains unresolved."]

    - PROPERTY_ID: EA-23
      PROPERTY_NAME: Security, quality and reliability built into the lifecycle
      HISTORICAL_ORIGIN: [H06, H15, S01, S02, S03]
      ORIGINAL_FORM: "Technical excellence, build quality in and shift verification earlier."
      PROBLEM_IT_ADDRESSED: "Quality and assurance were deferred to downstream inspection or external teams."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Late defect discovery and delivery speed that externalises harm."
      MECHANISM: "Integrate threat, hazard and quality controls into design, implementation, integration and release while retaining independent checks where warranted."
      TRIGGER_OR_CONTEXT: "Universal as a concern; control intensity follows consequence and exposure."
      NON_TRIGGER_OR_CHEAP_PATH: "Low-risk work may use a minimal baseline rather than a full high-assurance regime."
      DEPENDENCIES_OR_PRECONDITIONS: ["quality/threat/hazard model", "credible verification", "EA-06", "EA-07", "release authority"]
      EXPECTED_ENGINEERING_PAYOFF: "Earlier correction, lower assurance debt and reduced escaped harm."
      KNOWN_FAILURE_MODES: ["tool-checkbox security", "false automated gate", "quality sacrificed to cadence", "independent review too late"]
      IMPORTANT_CRITICISMS: "Continuous delivery does not itself prove safety, security or reliability."
      HOW_THE_PROPERTY_EVOLVED: "XP technical excellence and Lean quality were hybridised with security, safety and assurance engineering."
      MATURE_OR_EVOLVED_FORM: "Continuous internal controls plus consequence-triggered independent evidence."
      CEREMONY_VS_PROPERTY: "A Definition of Done or pipeline scan is only one implementation."
      CURRENT_STATUS: STRONGLY_RETAINED
      EVIDENCE_STRENGTH: STRONG_CONVERGENT
      PRIMARY_SOURCES: [H06, H15, S01, S02, S03]
      CRITICAL_SOURCES: [E09, E12]
      EMPIRICAL_SOURCES: [E08, E09, E12]
      OPEN_QUESTIONS: ["Automated assurance coverage for emergent and systemic hazards remains limited."]

    - PROPERTY_ID: EA-24
      PROPERTY_NAME: Risk-based documentation, traceability, configuration and governance
      HISTORICAL_ORIGIN: [H02, H26, S01, S02, S03, S04]
      ORIGINAL_FORM: "Documentation and controls were de-emphasised relative to working software."
      PROBLEM_IT_ADDRESSED: "Both excessive unused paperwork and insufficient organisational/assurance memory."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Stale compliance theatre on one side; untraceable decisions, configurations and hazards on the other."
      MECHANISM: "Maintain authoritative living evidence proportional to consequence, longevity, turnover, interface and external obligation."
      TRIGGER_OR_CONTEXT: "Regulation, safety, security, multiple organisations, long asset life, maintenance or auditability."
      NON_TRIGGER_OR_CHEAP_PATH: "For a low-risk small system, retain only the decision, interface, operation and recovery information needed by its actual users."
      DEPENDENCIES_OR_PRECONDITIONS: ["source authority", "configuration identity", "ownership", "update trigger"]
      EXPECTED_ENGINEERING_PAYOFF: "Reproducibility, memory, assurance and clearer authority without blanket paperwork."
      KNOWN_FAILURE_MODES: ["stale documents", "duplicate sources of truth", "traceability without use", "governance queues"]
      IMPORTANT_CRITICISMS: "‘Working software over comprehensive documentation’ was often distorted into anti-documentation doctrine."
      HOW_THE_PROPERTY_EVOLVED: "Minimal documentation became risk-based living evidence and automated traceability where useful."
      MATURE_OR_EVOLVED_FORM: "Document what another decision, operator, maintainer or authority must be able to know and verify."
      CEREMONY_VS_PROPERTY: "A template, wiki or audit packet is not intrinsically valuable."
      CURRENT_STATUS: RETAINED_IN_EVOLVED_FORM
      EVIDENCE_STRENGTH: STRONG_CONTEXTUAL
      PRIMARY_SOURCES: [H07, H26, S01, S02, S03, S04]
      CRITICAL_SOURCES: [E07]
      EMPIRICAL_SOURCES: [E07, E12]
      OPEN_QUESTIONS: ["The minimum sufficient evidence set remains domain- and consequence-specific."]

    - PROPERTY_ID: EA-25
      PROPERTY_NAME: Sustainable capacity, workload control and recovery
      HISTORICAL_ORIGIN: [H06, H08, H10]
      ORIGINAL_FORM: "Forty-hour week and sustainable pace."
      PROBLEM_IT_ADDRESSED: "Overtime and heroics were used as the normal response to uncertainty and overload."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Quality erosion, burnout, turnover and declining long-run throughput."
      MECHANISM: "Bound demand and WIP, preserve maintenance/learning capacity and require recovery after genuine emergencies."
      TRIGGER_OR_CONTEXT: "Continuous knowledge work, operational duty or repeated delivery cadence."
      NON_TRIGGER_OR_CHEAP_PATH: "A true time-bounded emergency may temporarily exceed normal load only with explicit recovery and root-cause action."
      DEPENDENCIES_OR_PRECONDITIONS: ["capacity authority", "visible demand", "EA-05", "leadership support"]
      EXPECTED_ENGINEERING_PAYOFF: "More stable quality, retention and long-run delivery capability."
      KNOWN_FAILURE_MODES: ["sprints as recurring deadlines", "hidden overtime", "pace used to excuse under-resourcing", "no slack"]
      IMPORTANT_CRITICISMS: "Manifesto language did not prevent organisations from using Agile cadence to intensify work."
      HOW_THE_PROPERTY_EVOLVED: "A personal work-hours rule became system workload, WIP, incident and recovery control."
      MATURE_OR_EVOLVED_FORM: "Normal demand must fit durable capacity; emergencies must remain exceptional and corrective."
      CEREMONY_VS_PROPERTY: "A capacity-planning meeting does not create sustainable capacity."
      CURRENT_STATUS: STRONGLY_RETAINED
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      PRIMARY_SOURCES: [H06, H08, H10]
      CRITICAL_SOURCES: [C03, E04]
      EMPIRICAL_SOURCES: [E03, E04]
      OPEN_QUESTIONS: ["Comparable measures of sustainable engineering pace remain weak."]

    - PROPERTY_ID: EA-26
      PROPERTY_NAME: Shared stewardship and knowledge distribution
      HISTORICAL_ORIGIN: [H06, H11]
      ORIGINAL_FORM: "Collective code ownership, pair programming and shared standards."
      PROBLEM_IT_ADDRESSED: "Knowledge and change authority were trapped with one individual or silo."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Bus-factor risk, review delay and locally incompatible code."
      MECHANISM: "Distribute understanding through pairing, ensemble work, rotation, review, documentation and common conventions."
      TRIGGER_OR_CONTEXT: "Critical knowledge is concentrated or cross-area change is frequent."
      NON_TRIGGER_OR_CHEAP_PATH: "Retain specialist ownership for rare/high-risk domains while establishing backups and explicit interfaces."
      DEPENDENCIES_OR_PRECONDITIONS: ["trust", "tests", "standards", "time for learning"]
      EXPECTED_ENGINEERING_PAYOFF: "Reduced single-person dependency and faster collaborative change."
      KNOWN_FAILURE_MODES: ["forced pairing fatigue", "diffused accountability", "shallow rotation", "loss of specialist depth"]
      IMPORTANT_CRITICISMS: "Pair programming has mixed time/quality trade-offs and should not be mandatory for every task."
      HOW_THE_PROPERTY_EVOLVED: "Universal pairing was narrowed to a portfolio of knowledge-distribution mechanisms."
      MATURE_OR_EVOLVED_FORM: "No critical area should depend on one inaccessible knower; use the cheapest suitable sharing mechanism."
      CEREMONY_VS_PROPERTY: "Pair programming is contextual; knowledge resilience is the property."
      CURRENT_STATUS: CONTEXT_DEPENDENT
      EVIDENCE_STRENGTH: MIXED
      PRIMARY_SOURCES: [H06, H11]
      CRITICAL_SOURCES: [E11]
      EMPIRICAL_SOURCES: [E11]
      OPEN_QUESTIONS: ["Long-term knowledge-resilience effects are harder to measure than short task performance."]

    - PROPERTY_ID: EA-27
      PROPERTY_NAME: Platform and paved-road enablement under cognitive-load constraints
      HISTORICAL_ORIGIN: [H16, H21, H22]
      ORIGINAL_FORM: "Internal developer platforms, platform teams and thinnest viable platforms."
      PROBLEM_IT_ADDRESSED: "Every autonomous team repeatedly built and operated undifferentiated infrastructure and controls."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Duplicated effort, cognitive overload, inconsistent security and operational fragmentation."
      MECHANISM: "Provide self-service, optional, composable and secure-by-default capabilities as an internal product."
      TRIGGER_OR_CONTEXT: "Many teams repeatedly need the same complex infrastructure, delivery, observability or compliance capability."
      NON_TRIGGER_OR_CHEAP_PATH: "For few teams or a simple stack, use shared templates, documentation or managed services rather than building a platform."
      DEPENDENCIES_OR_PRECONDITIONS: ["platform user research", "product management", "self-service automation", "escape path", "adoption evidence"]
      EXPECTED_ENGINEERING_PAYOFF: "Reduced repeated work and cognitive load with safer common defaults."
      KNOWN_FAILURE_MODES: ["central platform bureaucracy", "mandatory lowest-common-denominator path", "poor developer experience", "platform expansion without users"]
      IMPORTANT_CRITICISMS: "Independent comparative evidence remains emerging; platform programmes can reproduce central IT bottlenecks."
      HOW_THE_PROPERTY_EVOLVED: "Complete local ownership was bounded by shared enabling products."
      MATURE_OR_EVOLVED_FORM: "Build only the thinnest shared capability that earns adoption and reduces total system cost."
      CEREMONY_VS_PROPERTY: "A portal, platform team or golden-path brand is not the property."
      CURRENT_STATUS: CONTEXT_DEPENDENT
      EVIDENCE_STRENGTH: EMERGING
      PRIMARY_SOURCES: [H21, H22]
      CRITICAL_SOURCES: [E05, E06]
      EMPIRICAL_SOURCES: [E05, E06]
      OPEN_QUESTIONS: ["Strong independent causal evidence for platform engineering remains limited."]

    - PROPERTY_ID: EA-28
      PROPERTY_NAME: Active stopping, abandonment and option expiry
      HISTORICAL_ORIGIN: [H03, H08, H12, H19]
      ORIGINAL_FORM: "Simplicity, eliminate waste, fail cheaply and maximise work not done."
      PROBLEM_IT_ADDRESSED: "Backlogs and projects accumulated work regardless of changed value or evidence."
      FAILURE_MODE_IT_TRIES_TO_PREVENT: "Sunk-cost continuation and permanent demand inventories."
      MECHANISM: "Define stop criteria, review remaining expected value against cost/risk and explicitly delete, defer or terminate work."
      TRIGGER_OR_CONTEXT: "New evidence lowers expected value, raises risk or reveals a superior option."
      NON_TRIGGER_OR_CHEAP_PATH: "Mandatory legal, safety or contractual work should be completed to the minimum compliant outcome rather than abandoned."
      DEPENDENCIES_OR_PRECONDITIONS: ["decision authority", "outcome/risk evidence", "sunk-cost independence", "safe partial-state handling"]
      EXPECTED_ENGINEERING_PAYOFF: "Capacity returned earlier and less investment in low-value output."
      KNOWN_FAILURE_MODES: ["premature cancellation", "short-termism", "political avoidance", "unfinished operational residue"]
      IMPORTANT_CRITICISMS: "Rapid stopping can sacrifice strategic, infrastructure or long-latency investments whose value has not yet appeared."
      HOW_THE_PROPERTY_EVOLVED: "Backlog prioritisation became explicit option expiry and termination governance."
      MATURE_OR_EVOLVED_FORM: "Continue only while remaining expected value justifies remaining cost, risk and opportunity cost."
      CEREMONY_VS_PROPERTY: "Backlog grooming does not count unless low-value work can actually disappear."
      CURRENT_STATUS: RETAINED_IN_EVOLVED_FORM
      EVIDENCE_STRENGTH: MIXED
      PRIMARY_SOURCES: [H03, H08, H12, H19]
      CRITICAL_SOURCES: [E16, E17]
      EMPIRICAL_SOURCES: [E16, E17]
      OPEN_QUESTIONS: ["Reliable stopping rules for strategic and infrastructural work remain difficult."]
```

### Pass-1 property reconciliation

No pass-1 provisional property was silently dropped.

```text
PASS1 EA-P001 → EA-01
PASS1 EA-P002 → EA-02
PASS1 EA-P003 → EA-03
PASS1 EA-P004 → EA-06 + EA-07 + EA-08
PASS1 EA-P005 → EA-04
PASS1 EA-P006 → EA-05
PASS1 EA-P007 → EA-12
PASS1 EA-P008 → EA-13
PASS1 EA-P009 → EA-16
PASS1 EA-P010 → EA-09
PASS1 EA-P011 → EA-10 + EA-11
PASS1 EA-P012 → EA-21 + EA-22
PASS1 EA-P013 → EA-18
PASS1 EA-P014 → EA-25
PASS1 EA-P015 → EA-24
PASS1 EA-P016 → EA-28
```

The expansions separate prerequisite mechanisms that cannot truthfully be treated as one property. For example, “maintained changeability” requires distinct regression, integration and structural-change controls.

## EVOLVED_AGILE_CEREMONY_STRIPPING_LEDGER

The current Scrum Guide requires Scrum’s own events and accountabilities but does not require story points, velocity, user-story syntax, a two-week sprint or release only at sprint end. Its Daily Scrum structure is selected by developers, and its empirical theory says inspection without adaptation is pointless. ([scrumguides.org](https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf))

| Practice | Underlying property | What it can buy | When it fails | Required as general engineering? | Alternative implementations | Modern disposition |
|---|---|---|---|---|---|---|
| Daily stand-up | EA-01, EA-05, EA-19 | Fast coordination and blocker visibility | Upward status report; no action; interruption exceeds value | No | Async state, flow board, ad-hoc swarm, automated alerts | `CEREMONY_NOT_GENERAL_PROPERTY` |
| Fixed sprint | EA-01, EA-13 | Protected goal and bounded inspection horizon | Artificial batching, deadline pressure, work does not fit cadence | No | Continuous flow, risk increments, rolling plans | `CONTEXT_DEPENDENT` |
| Two-week sprint | None beyond one cadence choice | Familiar rhythm | Selected by convention rather than economics | No | Any justified cadence | `NO_GENERAL_PROPERTY` |
| Sprint planning | EA-13, EA-05 | Near-term intent, capacity and trade-off discussion | Becomes task allocation or false commitment | No | Replenishment, rolling-wave planning, risk review | Optional implementation |
| Sprint review/demo | EA-02, EA-12 | Evidence and stakeholder learning | Staged demo, wrong audience, no decision changes | No | Field test, user session, telemetry review, acceptance test | Optional implementation |
| Retrospective | EA-16 | Process reflection | No authority, ownership or follow-up | No | Continuous improvement, postmortem, flow review | Property retained; meeting optional |
| Product backlog | EA-13, EA-28 | Visible ordered options | Infinite demand warehouse; nothing deleted | No | Opportunity tree, option portfolio, roadmap, risk register | Representation only |
| Backlog refinement | EA-03, EA-13 | Reduce uncertainty before commitment | Excess analysis of low-priority work | No | Just-in-time analysis, example mapping, discovery | Contextual |
| Product Owner | EA-12, EA-13, EA-20 | Clear value-ordering authority | Proxy bottleneck, ticket writer, no user evidence | No | Product trio, domain owner, delegated authority policy | Contextual role pattern |
| Scrum Master | EA-16, EA-25 | Facilitation and impediment removal | Process police, ceremony administrator, no system authority | No | Team facilitator, manager, coach, rotating stewardship | Contextual role pattern |
| User story | EA-12, EA-04 | User-oriented conversation and small slicing | Formula replaces analysis; omits quality/system constraints | No | Use case, scenario, example, specification, hypothesis | `CEREMONY_NOT_GENERAL_PROPERTY` |
| Story points | EA-13, EA-17 | Local sizing conversation | Quota, team comparison, false unit of productivity | No | Historical throughput, cycle distributions, decomposition, no-estimate pull | `USEFUL_BUT_EASILY_GAMED` |
| Velocity | EA-17 | Local historical planning signal | Target, output proxy, cross-team ranking | No | Probabilistic flow forecast and outcome/quality evidence | Disfavoured as performance metric |
| Planning poker | EA-13 | Expose divergent assumptions | Number production becomes the purpose | No | Independent risk estimates, reference classes, decomposition | Optional technique |
| Burndown/burn-up | EA-17 | Visualise work movement | Scope manipulation, false completion signal | No | Cumulative flow, ageing, milestone evidence | Diagnostic only |
| Pair programming | EA-26, EA-06 | Continuous review and knowledge spread | Fatigue, forced use, task/skill mismatch | No | Ensemble work, review, rotation, mentoring | `CONTEXT_DEPENDENT` |
| TDD red–green–refactor | EA-06, EA-08 | Very fast regression/design feedback | Weak oracle, overfitted tests, unsuitable task | No | Test-after, property tests, model-based tests, simulation | Specific method; broader properties retained |
| Definition of Done | EA-02, EA-23 | Explicit completion/quality boundary | Weak checklist; deferred assurance; unverifiable language | No named artefact required | Acceptance policy, release gate, assurance case | Strong underlying property |
| Release train | EA-19, EA-24 | Coordinate expensive/shared release boundary | Reintroduces avoidable batching and waiting | No | On-demand release, independent release slots, qualified windows | Context-specific |
| Scrum of Scrums | EA-19 | Cross-team dependency visibility | Status hierarchy without dependency removal | No | Interface forum, architecture integration, dependency service | Ceremony not property |
| Feature flag | EA-10, EA-11 | Separate deployment from exposure and limit blast radius | Flag debt, security path, incompatible states | No | Separate deployment, configuration versioning, canary environment | Contextual implementation |
| Postmortem | EA-16, EA-21 | Incident learning and corrective action | Blame, document-only closure, repeated findings | No fixed format | Immediate causal review, operational learning loop | Trigger-based implementation |
| Weekly discovery cadence | EA-12, EA-15 | Regular direct evidence | Interview quota, wrong users, no decisions | No | Event-triggered research, telemetry, field observation | Cadence contextual |
| Face-to-face communication | High-bandwidth interaction | Fast rich exchange | Excludes distributed expertise; undocumented decisions | No | Video, async records, collaborative models, written decisions | Original preference narrowed |

## EVOLVED_AGILE_CRITICISM_LEDGER

| ID | Criticism | Target class | Valid core | Overclaim boundary | Frozen disposition |
|---|---|---|---|---|---|
| `AC-01` | Cargo-cult Agile / Agile theatre | `IMPLEMENTATION_FAILURE` | Visible form can survive after causal mechanism disappears. | Does not show that feedback or integration themselves are useless. | Valid; ceremony receives no presumption of value. |
| `AC-02` | Scrum became synonymous with Agile | `A_SPECIFIC_METHOD` | Scrum’s management structure displaced richer technical and governance traditions. | Criticism of Scrum adoption is not criticism of every adaptive method. | Valid historical narrowing. |
| `AC-03` | Flaccid Scrum | `IMPLEMENTATION_FAILURE` | Cadence without testing, integration and refactoring can expose but not fix declining changeability. | Scrum officially calls itself incomplete. | Valid; EA-06–EA-10 are separate prerequisites. |
| `AC-04` | Story-point and velocity gaming | `METRIC_GAMING` | Abstract local estimates become quotas and false productivity units. | A team may still use them privately as a conversation aid. | No general property; EA-17 governs. |
| `AC-05` | Output replaces value | `METRIC_GAMING` | Features, tickets or deployment counts can rise while outcomes do not. | Some output measures remain useful diagnostics. | Replace target output with evidence portfolio. |
| `AC-06` | Local team optimisation | `SCALING` | Dependencies, platforms and architecture can dominate local speed. | Small independent teams may not require additional coordination. | EA-19 strongly retained. |
| `AC-07` | Architecture neglect | `THE_PRINCIPLE` / `IMPLEMENTATION_FAILURE` | “Emergent” can become architecture-by-accident. | Comprehensive up-front architecture is not therefore always justified. | EA-09 hybrid retained. |
| `AC-08` | Anti-documentation interpretation | `THE_PRINCIPLE` | Minimal records can destroy memory, assurance and reproducibility. | Comprehensive documentation can still be unused waste. | EA-24 risk-based replacement. |
| `AC-09` | Anti-planning / strategic thrashing | `MANAGEMENT_ADOPTION` | Constant reprioritisation can destroy focus and strategic accumulation. | Fixed plans under uncertainty also fail. | EA-13 multi-horizon replacement. |
| `AC-10` | Product Owner bottleneck / fake customer | `A_SPECIFIC_METHOD` | One proxy can centralise ignorance and delay. | Clear decision authority remains valuable. | Direct evidence plus bounded authority. |
| `AC-11` | Scaling-framework bureaucracy | `SCALING` | Frameworks can reproduce phase gates and hierarchy in Agile language. | Scale still creates real coordination burdens. | Framework choice not property; EA-19 retained. |
| `AC-12` | Technical debt hidden by cadence | `IMPLEMENTATION_FAILURE` | Feature completion can rise as future changeability collapses. | Not every shortcut warrants immediate repayment. | EA-08 retained with economic boundary. |
| `AC-13` | Perpetual sprint pressure | `MANAGEMENT_ADOPTION` | Recurring timeboxes can become recurring emergencies. | A protected cadence can also reduce interruption. | EA-25 retained; sprint contextual. |
| `AC-14` | Autonomy became a ticket factory | `MANAGEMENT_ADOPTION` | Teams may organise tasks locally but lack product, architecture or release authority. | Local work management still has value. | EA-18 requires real bounded authority. |
| `AC-15` | Shallow retrospectives | `A_SPECIFIC_CEREMONY` | Observation without authorised change is an open loop. | Informal improvement can work without a meeting. | EA-16 retained; meeting optional. |
| `AC-16` | CI/CD theatre | `IMPLEMENTATION_FAILURE` | Automation can preserve false green signals or bypass failed controls. | Bad implementation does not negate frequent truthful integration. | EA-06–EA-11 require trustworthy evidence. |
| `AC-17` | Short feedback cannot resolve delayed outcomes | `CONTEXT_MISMATCH` | Weekly evidence cannot directly identify effects that mature over months or years. | Validated surrogates can sometimes accelerate decisions. | EA-14 admitted. |
| `AC-18` | Agile mismatches hardware/regulation/safety | `CONTEXT_MISMATCH` | Physical and assurance boundaries impose costly, irreversible commitments. | Adaptive work can operate below those boundaries. | Risk-based hybrid, not blanket rejection. |
| `AC-19` | Distributed communication failure | `IMPLEMENTATION_FAILURE` | Informal synchronous communication alone scales poorly across time, geography and organisations. | Co-location is not a universal requirement. | Reintroduce durable interfaces and records. |
| `AC-20` | Agile industrial complex | `MANAGEMENT_ADOPTION` | Certification and consulting incentives can favour reproducible ceremony over contextual engineering. | Commercial support is not inherently harmful. | No method-branded practice is admitted without mechanism evidence. |

Original-author criticism strongly supports `AC-01`, `AC-02`, `AC-03`, `AC-13` and `AC-20`, but remains practitioner testimony rather than prevalence measurement. ([ronjeffries.com](https://ronjeffries.com/articles/018-01ff/abandon-1/))

## EVOLVED_AGILE_EVOLUTION_UNDER_CRITICISM

| Earlier formulation | Criticism encountered | Evolved response | Classification |
|---|---|---|---|
| Fixed iteration | Artificial batching and deadline pressure | Continuous flow or risk-aligned cadence | `REPLACED` in some contexts |
| One sprint clock | Different evidence loops have different latency/economics | Multi-cadence control system | `GENERALIZED` |
| Working software | Functioning feature may be unintegrated, unsafe or unused | Integrated, verified, deployable and outcome-observed evidence | `GENERALIZED` |
| Frequent release | Exposure can be unsafe or irreversible | Release readiness plus progressive/authorised exposure | `NARROWED` |
| Respond to change | Interruption and strategic thrashing | Evidence threshold, switching cost and protected horizons | `REFINED` |
| Emergent architecture | Architectural erosion and expensive lock-in | Deliberate irreversible decisions plus evolutionary fitness functions | `HYBRIDISED` |
| Customer representative | Proxy ignorance and bottleneck | Direct discovery plus behavioural and delayed evidence | `REFINED` |
| Velocity/story points | Goodhart effects and false comparability | Flow, quality, reliability, human and outcome portfolio | `REPLACED` as performance measurement |
| Team retrospective | Local meeting cannot alter system constraints | Authorised system improvement and incident learning | `GENERALIZED` |
| Local autonomy | Cognitive overload and duplicated infrastructure | Bounded ownership, explicit dependencies and platforms | `HYBRIDISED` |
| Project delivery | Handoff and orphaned consequences | Durable product/problem ownership where lifecycle persists | `HYBRIDISED` |
| Development complete at code handoff | Operational cost externalised | DevOps and operational feedback | `GENERALIZED` |
| Delivery speed | Reliability treated as an obstacle | SLO/error-budget or consequence-specific release controls | `HYBRIDISED` |
| Minimal documentation | Memory, traceability and assurance gaps | Risk-based living evidence and configuration authority | `REFINED` |
| Manual downstream quality gate | Late discovery and queueing | Continuous controls plus independent checks where consequence demands | `HYBRIDISED` |
| Feature backlog | Output bias and sunk-cost continuation | Outcome options, experiments and explicit stopping | `REFINED` |

## EVOLVED_AGILE_INTERNAL_TENSIONS

| Tension | Side A | Side B | Context favouring A | Context favouring B | Hybrid resolution | Unresolved risk |
|---|---|---|---|---|---|---|
| Adaptability vs stability | EA-13 | stable strategy/baselines | High uncertainty and reversibility | Shared commitments and costly switching | Stable intent, adaptive detail | “Evidence” can be invoked opportunistically |
| Local autonomy vs system coherence | EA-18 | EA-19 | Independent product boundary | Shared architecture/resources | Bounded authority and explicit interfaces | Boundaries may be politically rather than technically drawn |
| Emergent vs deliberate architecture | evolutionary part of EA-09 | deliberate part of EA-09 | Local reversible decision | Irreversible/high-blast decision | Reversibility classification and fitness functions | No universal threshold |
| Rapid delivery vs qualification | EA-10 | EA-23/EA-24 | Low-consequence digital release | Safety, regulation, hardware | Continuous evidence inside authorised release envelope | Qualification can become a bottleneck or be under-scoped |
| Customer feedback vs strategy | EA-12 | EA-13/EA-14 | Uncertain need/use | Long-horizon positioning and externalities | Direct evidence constrained by strategy and delayed outcomes | Strategy may become excuse to ignore evidence |
| Continuous change vs configuration control | EA-07/EA-10 | EA-24 | Cheap reproducible change | Long-lived certified baselines | Versioned automated configuration and authorised exposure | State/data migration remains difficult |
| Minimal records vs organisational memory | low document cost | EA-24 | Small low-risk co-located system | Turnover, longevity, regulation | Risk-based living evidence | Minimum sufficiency remains contextual |
| Team flow vs cross-team dependency | EA-05 | EA-19 | Independent value stream | Shared system releases/interfaces | End-to-end flow and dependency removal | Local metrics can hide transferred queues |
| Experimentation vs safety/security | EA-15 | EA-23/EA-24 | Reversible bounded exposure | Irreversible or vulnerable population | Simulation, staged pilots and independent review | Rare hazards may evade small trials |
| Short feedback vs long outcomes | EA-01 | EA-14 | Immediate reliable signal | Delayed retention/safety/social effect | Validated surrogates plus delayed follow-up | Proxy drift |
| Decentralisation vs authoritative ownership | EA-18 | EA-20/EA-24 | Local information dominates | System/portfolio obligation dominates | Explicit decision domains and escalation | Ambiguous authority can persist |
| Small batches vs fixed setup cost | EA-04 | qualification/fabrication economics | Low handoff cost | High fixed mobilisation/certification | Reduce avoidable setup, batch irreducible boundary | Teams may assert fixed cost without testing it |
| Platform standardisation vs team freedom | EA-27 | EA-18 | Repeated undifferentiated need | Unique product need | Optional composable paved road and escape path | “Optional” platform can become de facto mandate |
| Measurement vs gaming | EA-17 | human adaptation | Stable diagnostic use | Measures tied to reward/ranking | Countermetrics, local trends and qualitative review | Any public measure can become a target |
| Sustainable pace vs urgency | EA-25 | risk response | Normal operation | Genuine bounded emergency | Recovery and root-cause obligation | Emergency can become the permanent operating model |

## EVOLVED_AGILE_HYBRIDISATION_PRESSURES

| Pressure exposed by history | Imported or convergent tradition | Resulting evolved property |
|---|---|---|
| Feature/value ordering did not retire existential technical risks | Spiral and evolutionary delivery | EA-03 |
| Iterations accumulated queues and artificial boundaries | Lean and Kanban | EA-04, EA-05 |
| Agile management lacked a sufficient technical substrate | XP, CI and refactoring | EA-06, EA-07, EA-08 |
| Emergent-only design failed at irreversible boundaries | Systems architecture, ATAM/CBAM, evolutionary architecture | EA-09 |
| Sprint completion did not produce release readiness | Continuous Delivery | EA-10, EA-11 |
| Product Owner proxy did not establish real need | UX research and continuous discovery | EA-12, EA-15 |
| Short-cycle outputs did not establish long-term value | Experimentation and causal inference | EA-14 |
| Team retrospectives could not alter organisational constraints | Lean improvement and SRE incident learning | EA-16, EA-21 |
| Local autonomy did not solve dependencies | Systems engineering, Team Topologies | EA-18, EA-19 |
| Temporary projects abandoned operational consequences | Product operating models | EA-20 |
| Development–operations separation externalised failure | DevOps and SRE | EA-21, EA-22 |
| Speed omitted security, safety and assurance | NIST, NASA, FDA and systems assurance | EA-23, EA-24 |
| Complete operational ownership overloaded every team | Platform engineering | EA-27 |
| Backlogs expanded without deletion | Lean, evolutionary delivery and discovery | EA-28 |

The synthesis therefore rejects the claim that later practice simply “added DevOps to Agile”. Several later systems arose independently or in reaction to deficiencies in branded Agile adoption.

## EVOLVED_AGILE_STRONGEST_SURVIVING_PROPERTIES

The strongest retained properties are not stand-ups, sprints or backlogs. They are:

1. **EA-02 — Integrated working evidence.** Progress must eventually be demonstrated in the integrated system at the evidential level relevant to the claim.
2. **EA-03 — Early risk retirement.** Work capable of invalidating large commitments should not be deferred behind easy feature output.
3. **EA-06 — Automated regression verification.** Repeated change requires repeatable evidence that prior behaviour remains intact.
4. **EA-07 — Frequent real integration.** Isolated work must not accumulate beyond the system’s ability to expose incompatibility cheaply.
5. **EA-10 — Release-ready state with exposure decoupled.** Iteration, deployment readiness and actual release are separate decisions.
6. **EA-16 — Authorised process adaptation.** Observation must lead to an owned change and subsequent measurement.
7. **EA-19 — System-level dependency control.** Local autonomy does not remove shared interfaces or queues.
8. **EA-21 — Operational feedback and incident learning.** Production consequences must return to engineering decisions.
9. **EA-23 — Security, quality and reliability built into the lifecycle.** Delivery speed does not discharge engineering consequence.
10. **EA-25 — Sustainable capacity.** Chronic overload is a process defect, not evidence of agility.

EA-01, EA-04, EA-05, EA-08, EA-09, EA-12, EA-13, EA-14, EA-17 and EA-24 are also substantial survivors, but their useful form requires particularly careful contextualisation or anti-gaming controls.

## EVOLVED_AGILE_CONTEXT_SPECIFIC_PROPERTIES

| Property | Principal context boundary |
|---|---|
| EA-04 | Small batches cease to dominate when setup, mobilisation or qualification has irreducible fixed cost. |
| EA-09 | Deliberate architectural investment rises with irreversibility, coupling, public commitment and consequence. |
| EA-11 | Progressive exposure requires segmentation, observability and a credible recovery or containment path. |
| EA-12 | Direct user evidence is less determinative for mandated, latent-risk or long-horizon strategic requirements. |
| EA-15 | Experimentation must not trigger where exposure is unethical, dangerous or irreversibly harmful. |
| EA-18 | Local autonomy must fit actual competence, authority, system boundaries and cognitive capacity. |
| EA-20 | Durable product ownership does not automatically suit one-off or intentionally finite work. |
| EA-22 | Error budgets fit service reliability; hard safety constraints may not be tradable. |
| EA-24 | Evidence burden rises sharply with consequence, longevity, interfaces and regulation. |
| EA-26 | Pairing and collective ownership are contextual implementations of knowledge resilience. |
| EA-27 | Platforms pay off only where repeated shared complexity exceeds platform creation and governance cost. |
| EA-28 | Rapid stopping must not erase long-latency, infrastructural or mandatory value. |

## EVOLVED_AGILE_REJECTED_OR_SUPERSEDED_PRACTICES

| Practice or proposition | Final disposition | Reason |
|---|---|---|
| “Shorter iteration is always better” | `REJECTED_OR_DISFAVOURED` | Feedback value is non-monotone and loop-specific. |
| Universal two-week sprint | `CEREMONY_NOT_GENERAL_PROPERTY` | No general economic or evidential basis for that duration. |
| Fixed iteration as the default for all work | `SUPERSEDED_BY_STRONGER_FORM` | Continuous flow or risk-aligned cadence may be superior. |
| Story points as productivity | `REJECTED_OR_DISFAVOURED` | Local estimate unit is not comparable output. |
| Velocity targets or team ranking | `REJECTED_OR_DISFAVOURED` | Strong proxy-gaming risk. |
| Mandatory user-story sentence template | `CEREMONY_NOT_GENERAL_PROPERTY` | Requirement representation must follow the information needed. |
| Daily status stand-up | `REJECTED_OR_DISFAVOURED` | Coordination property survives; reporting theatre does not. |
| Retrospective meeting as proof of learning | `CEREMONY_NOT_GENERAL_PROPERTY` | Closed-loop change is required. |
| Scrum alone as a complete engineering system | `REJECTED_OR_DISFAVOURED` | Scrum is officially purposefully incomplete. |
| Emergent architecture only | `REJECTED_OR_DISFAVOURED` | Irreversible/high-coupling decisions require deliberate analysis. |
| Comprehensive up-front architecture for every decision | `REJECTED_OR_DISFAVOURED` | Reversible decisions can be evolved more cheaply. |
| Anti-documentation interpretation | `REJECTED_OR_DISFAVOURED` | Risk-based evidence, memory and traceability survive. |
| Anti-planning interpretation | `REJECTED_OR_DISFAVOURED` | Multi-horizon planning survives. |
| Release only at sprint end | `SUPERSEDED_BY_STRONGER_FORM` | Deployability and release are decoupled. |
| Universal continuous deployment | `REJECTED_OR_DISFAVOURED` | Exposure requires consequence-appropriate authority. |
| Universal TDD sequence | `CONTEXT_DEPENDENT` | Regression verification survives; one sequence does not. |
| Universal pair programming | `CONTEXT_DEPENDENT` | Knowledge resilience survives; pairing trade-offs vary. |
| Absolute local team autonomy | `REJECTED_OR_DISFAVOURED` | System coherence, specialist capability and cognitive load constrain it. |
| Single Product Owner as universal design | `CONTEXT_DEPENDENT` | Decision authority survives; one-role implementation does not. |
| Universal scaling framework | `REJECTED_OR_DISFAVOURED` | Framework selection has weak comparative evidence and negligible observed practical effect after controls. |
| Mandatory release train | `CONTEXT_DEPENDENT` | May be justified by shared qualification; otherwise increases batch delay. |
| Face-to-face-only communication | `REJECTED_OR_DISFAVOURED` | High-bandwidth exchange survives, but durable distributed alternatives are valid. |
| Backlog growth without deletion | `REJECTED_OR_DISFAVOURED` | EA-28 requires active stopping and option expiry. |
| One-number productivity | `REJECTED_OR_DISFAVOURED` | Sociotechnical performance requires multiple dimensions. |

## EVOLVED_AGILE_OPEN_QUESTIONS

The evidence search is complete enough to freeze, but these questions remain explicitly unresolved:

1. **Whole-method causal decomposition:** which combinations of technical practice, autonomy, product access and organisational selection account for observed Agile associations?
2. **Feedback economics:** can domains derive practical models that include signal quality, delay, attention cost, decision authority and reversibility rather than iteration length alone?
3. **Architecture investment:** can irreversibility, coupling and quality-attribute exposure be converted into validated architecture-investment thresholds?
4. **Qualification-aware batching:** what batch sizes minimise total delay and assurance cost for hardware, medical, automotive, aerospace and other high-fixed-cost systems?
5. **Long-outcome surrogates:** how should proxy validity be maintained under population, product and strategy drift?
6. **Metric resistance:** which diagnostic portfolios remain informative once teams understand how rewards depend on them?
7. **Platform effectiveness:** when does an internal platform lower total cognitive and operational cost rather than creating another dependency?
8. **Product-mode causality:** does durable product ownership outperform explicit project-to-operations handover after organisational and product differences are controlled?
9. **Sustainable pace:** what measures distinguish healthy slack and learning capacity from delay, under-resourcing or concealed overload?
10. **Adaptive high assurance:** which combinations of continuous evidence and independent assurance produce the best safety and verification outcomes?
11. **Continuous discovery:** which benefits come from direct user evidence itself and which require the surrounding product authority and experimental capability?
12. **Stopping strategic work:** how can organisations abandon weak options without systematically underinvesting in infrastructure and delayed-return capabilities?

---

# EVOLVED_AGILE_AUDIT_INTAKE

```yaml
EVOLVED_AGILE_AUDIT_INTAKE:
  PROPERTY_POPULATION_TOTAL: 28
  PROPERTY_POPULATION_EXAMINED: 28
  PROPERTY_COVERAGE: "28/28"

  TOP_CROSSWALK_PROPERTIES:
    - EA-01
    - EA-02
    - EA-03
    - EA-05
    - EA-06
    - EA-07
    - EA-08
    - EA-09
    - EA-10
    - EA-16
    - EA-17
    - EA-19
    - EA-21
    - EA-23
    - EA-24
    - EA-25
    - EA-28

  CROSSWALK_WORTHY_PROPERTIES:
    - PROPERTY_ID: EA-01
      PROPERTY_NAME: Actionability-weighted feedback-loop selection
      FAILURE_MODE: "Evidence arrives after avoidable commitment, or cadence creates noise and pressure rather than learning."
      MATURE_FORM: "Select loop frequency by information value, actionability, reversibility and total cost."
      TRIGGER: "Uncertainty can be reduced before a material decision."
      CHEAP_PATH: "Use existing telemetry, sampling, simulation or milestone evidence; do not create a sprint merely to create cadence."
      REQUIRED_PRECONDITIONS: ["observable signal", "decision authority", "reversible decision"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["shorter is not always better", "one cadence cannot govern every uncertainty"]
      ANTI_CEREMONY_BOUNDARY: "No mandatory iteration length, stand-up or review meeting."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-24 qualification/configuration stability"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Does the target system already shorten decision-relevant feedback through a different native mechanism?"
        - "Are any recurring cadences producing evidence that actually changes decisions?"
        - "Could a cheaper event-triggered or risk-triggered loop replace a calendar ceremony?"
        - "Does shortening this loop create attention, qualification or schedule-pressure costs greater than its benefit?"

    - PROPERTY_ID: EA-02
      PROPERTY_NAME: Integrated working evidence
      FAILURE_MODE: "Progress is inferred from documents, tickets or isolated components while the integrated system remains unknown."
      MATURE_FORM: "Demonstrate integrated behaviour at the evidential level relevant to the claim."
      TRIGGER: "A progress, compatibility or feasibility claim depends on interacting parts."
      CHEAP_PATH: "Use a focused executable model or prototype when full production integration is unnecessary."
      REQUIRED_PRECONDITIONS: ["configuration identity", "test oracle", "representative boundary"]
      EVIDENCE_STRENGTH: MODERATE_TO_STRONG_CONVERGENT
      CRITICISMS: ["working does not imply valuable", "demo theatre can misrepresent integration"]
      ANTI_CEREMONY_BOUNDARY: "No sprint demo is required; evidence scope must be explicit."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-24 formal evidence requirements"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "What is the target system's strongest integrated evidence state?"
        - "Are completion claims stronger than the evidence actually exercised?"
        - "Does a cheaper existing proof, simulation or integration test already answer the relevant question?"
        - "Are demonstrations incorrectly standing in for safety, security, scale or qualification evidence?"

    - PROPERTY_ID: EA-03
      PROPERTY_NAME: Risk-driven sequencing and early risk retirement
      FAILURE_MODE: "High-exposure assumptions remain unresolved while low-risk output accumulates."
      MATURE_FORM: "Perform the cheapest discriminating work before dependent irreversible commitment."
      TRIGGER: "A technical, architectural, user, supplier or assurance uncertainty could invalidate substantial work."
      CHEAP_PATH: "Use ordinary value/flow ordering for repetitive low-risk work."
      REQUIRED_PRECONDITIONS: ["explicit risk", "discriminating test", "authority to reorder"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["risk estimates can be subjective", "risk-first can crowd out value"]
      ANTI_CEREMONY_BOUNDARY: "A spike or risk workshop is optional; evidence-based retirement is required."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-12 user-value discovery"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Are the assumptions capable of invalidating the most work identified?"
        - "Does current ordering retire those assumptions before dependent commitment?"
        - "Is risk represented by evidence and exposure rather than urgency labels?"
        - "Does the target already possess a cheaper native risk-retirement path?"

    - PROPERTY_ID: EA-04
      PROPERTY_NAME: Economically small incremental batches
      FAILURE_MODE: "Large handoffs delay feedback and make diagnosis, integration and reversal expensive."
      MATURE_FORM: "Use the smallest coherent batch justified by total transaction, qualification and consequence economics."
      TRIGGER: "Batch delay or failure exposure dominates fixed setup cost."
      CHEAP_PATH: "Keep upstream integration small while batching only the irreducibly expensive release or qualification boundary."
      REQUIRED_PRECONDITIONS: ["coherent slicing", "known fixed cost", "modularity"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["batch of one can be uneconomic", "tiny fragments may not carry value"]
      ANTI_CEREMONY_BOUNDARY: "A story or sprint is not presumed to be a useful batch."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-24 assurance and release baselines"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Where does batch size actually create delay or reversal risk?"
        - "Which setup or qualification costs are irreducible and which are products of the current process?"
        - "Would smaller upstream evidence add value even if final release remains batched?"
        - "Does the target already use a superior economic batching mechanism?"

    - PROPERTY_ID: EA-05
      PROPERTY_NAME: Explicit WIP and flow control
      FAILURE_MODE: "Started work, queues and ageing accumulate without an authoritative stop-start rule."
      MATURE_FORM: "Control concurrent work across the actual end-to-end system and act on age and blockage."
      TRIGGER: "Demand exceeds capacity or work repeatedly waits between states."
      CHEAP_PATH: "Use a simple one-at-a-time focus rule for a small serial workflow."
      REQUIRED_PRECONDITIONS: ["real workflow visibility", "start/finish definitions", "authority to limit work"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["flow is not value", "work-item size can be gamed"]
      ANTI_CEREMONY_BOUNDARY: "A board alone is not WIP control."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-03 risk-driven expedited work"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Where is started-but-unfinished work currently visible?"
        - "Can the target refuse new work when existing work is blocked or ageing?"
        - "Do current metrics hide queues outside the measured boundary?"
        - "Would a lightweight focus limit outperform a formal Kanban ceremony?"

    - PROPERTY_ID: EA-06
      PROPERTY_NAME: Automated regression verification
      FAILURE_MODE: "Frequent change silently breaks prior behaviour or makes change too frightening and expensive."
      MATURE_FORM: "Automate repeated high-value verification at risk-appropriate levels."
      TRIGGER: "Behaviour changes repeatedly and regression consequences are material."
      CHEAP_PATH: "Use targeted manual, simulation or sampled verification where automation cost exceeds repetition value."
      REQUIRED_PRECONDITIONS: ["credible oracle", "testable boundary", "maintained data"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["TDD sequence is not universally superior", "coverage creates false confidence"]
      ANTI_CEREMONY_BOUNDARY: "Do not require TDD merely to claim the broader property."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-04 test execution/qualification cost"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Which regressions are both likely and cheap enough to check repeatedly?"
        - "Are current tests credible, maintained and fast enough for their decision loop?"
        - "Is a named TDD practice being substituted for actual regression coverage?"
        - "Does the target already have a superior verification mechanism?"

    - PROPERTY_ID: EA-07
      PROPERTY_NAME: Frequent real integration and healthy mainline
      FAILURE_MODE: "Long-lived isolated work accumulates incompatible assumptions and late merge risk."
      MATURE_FORM: "Integrate into an authoritative verified state before divergence becomes expensive."
      TRIGGER: "Parallel changes interact in a shared system."
      CHEAP_PATH: "Integrate at every coherent change for a low-volume or solo workflow."
      REQUIRED_PRECONDITIONS: ["version control", "build", "EA-06", "failure-repair authority"]
      EVIDENCE_STRENGTH: MODERATE_TO_STRONG_CONVERGENT
      CRITICISMS: ["CI theatre", "frequent unstable merging can accelerate disruption"]
      ANTI_CEREMONY_BOUNDARY: "A CI server or green badge is not evidence of real integration."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-24 controlled baselines"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "What state is authoritative and how old can unintegrated work become?"
        - "Do all critical integration checks actually run?"
        - "Can a failed authoritative state remain broken while new work continues?"
        - "Is branch or component success being mistaken for system integration?"

    - PROPERTY_ID: EA-08
      PROPERTY_NAME: Maintained technical changeability
      FAILURE_MODE: "Feature cadence continues while internal structure makes every later change slower and riskier."
      MATURE_FORM: "Invest continuously in behaviour-preserving restructuring and option preservation."
      TRIGGER: "Internal quality is materially increasing change cost."
      CHEAP_PATH: "Isolate, replace or retire disposable code rather than polishing it."
      REQUIRED_PRECONDITIONS: ["EA-06", "EA-07", "design skill", "allocated capacity"]
      EVIDENCE_STRENGTH: MIXED_TO_MODERATE
      CRITICISMS: ["difficult economic measurement", "refactoring can become unbounded polishing"]
      ANTI_CEREMONY_BOUNDARY: "A debt backlog or refactoring sprint is not proof of maintained changeability."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-28 stopping or replacing low-value components"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Is rising change cost detected before delivery collapses?"
        - "Does the target preserve structural options through a native mechanism?"
        - "Are debt records connected to decisions and repayment?"
        - "Would replacement or abandonment be cheaper than refactoring?"

    - PROPERTY_ID: EA-09
      PROPERTY_NAME: Architecture proportional to irreversibility and coupling
      FAILURE_MODE: "Either speculative architecture or irreversible architecture-by-accident controls the system."
      MATURE_FORM: "Analyse costly commitments deliberately and evolve reversible decisions under fitness evidence."
      TRIGGER: "High blast radius, persistent data, public interface, safety/security, cross-team coupling or expensive migration."
      CHEAP_PATH: "Use simple design and short experiments for local reversible choices."
      REQUIRED_PRECONDITIONS: ["quality attributes", "decision boundary", "architecture authority"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["no validated universal threshold", "architecture analysis can become bureaucracy"]
      ANTI_CEREMONY_BOUNDARY: "No mandatory architecture board, diagram set or sprint zero."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-01 rapid learning"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Which decisions are genuinely expensive or impossible to reverse?"
        - "Does the target already distinguish irreversible from locally evolvable choices?"
        - "Are architectural claims continuously checked where automation is feasible?"
        - "Would additional architecture work reduce expected loss or merely add ceremony?"

    - PROPERTY_ID: EA-10
      PROPERTY_NAME: Release-ready state and exposure decoupling
      FAILURE_MODE: "Release remains a large manual event tied to project or sprint completion."
      MATURE_FORM: "Continuously maintain a reproducible verified candidate while release remains an authorised decision."
      TRIGGER: "Build and verification can occur more frequently than exposure."
      CHEAP_PATH: "Maintain reproducible qualified packages for hardware or regulated systems without demanding continuous deployment."
      REQUIRED_PRECONDITIONS: ["EA-06", "EA-07", "configuration control", "representative environment"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["pipeline automation can propagate weak verification", "deployability can be overstated"]
      ANTI_CEREMONY_BOUNDARY: "Sprint completion or a release train is not release readiness."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-23/EA-24 release assurance"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Can the target produce a known release candidate without exceptional manual reconstruction?"
        - "Are deployment readiness and actual exposure represented as separate decisions?"
        - "What verification or authority should block exposure?"
        - "Is a cheaper native release-ready path already present?"

    - PROPERTY_ID: EA-11
      PROPERTY_NAME: Progressive exposure and reversibility
      FAILURE_MODE: "An uncertain change reaches full blast radius before real-environment hazards are visible."
      MATURE_FORM: "Bound exposure, monitor guardrails and preserve recovery or containment."
      TRIGGER: "Population can be segmented and effects are observable before full exposure."
      CHEAP_PATH: "Use simulation, pilot qualification or independent review where rollback is impossible."
      REQUIRED_PRECONDITIONS: ["observability", "state compatibility", "rollback or containment"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["rare or delayed hazards evade canaries", "feature flags create debt"]
      ANTI_CEREMONY_BOUNDARY: "A flag or canary tool is not sufficient without tested recovery."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-24 stable controlled baseline"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Which changes can actually be reversed after exposure?"
        - "Are rollout cohorts representative of the relevant risk?"
        - "Does rollback include data and external side effects?"
        - "Would pre-exposure assurance be superior to progressive rollout for this context?"

    - PROPERTY_ID: EA-12
      PROPERTY_NAME: Direct problem, user and environment evidence
      FAILURE_MODE: "A proxy stakeholder or backlog transmits untested assumptions as requirements."
      MATURE_FORM: "Use representative direct evidence from users, behaviour and operating context."
      TRIGGER: "Need, usability, adoption or workflow is uncertain."
      CHEAP_PATH: "Use representative domain acceptance evidence for stable or mandated requirements."
      REQUIRED_PRECONDITIONS: ["representative access", "research competence", "authority to respond"]
      EVIDENCE_STRENGTH: MIXED
      CRITICISMS: ["feedback can be noisy or biased", "users do not replace strategy"]
      ANTI_CEREMONY_BOUNDARY: "No mandatory user-story form, Product Owner proxy or weekly interview quota."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-14 long-term strategy/outcome"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Who supplies evidence about the actual problem and population?"
        - "Is that evidence direct, representative and capable of changing decisions?"
        - "Does the target already possess a superior native requirements-validation mechanism?"
        - "Would additional customer ceremony add signal or merely duplicate existing evidence?"

    - PROPERTY_ID: EA-13
      PROPERTY_NAME: Evidence-triggered multi-horizon planning
      FAILURE_MODE: "Plans remain fixed after invalidation, or constant reprioritisation destroys focus and direction."
      MATURE_FORM: "Keep intent stable, detail near work and revise at the cheapest horizon justified by evidence."
      TRIGGER: "Material assumptions remain uncertain."
      CHEAP_PATH: "Preserve fixed external commitments while adapting implementation and risk response."
      REQUIRED_PRECONDITIONS: ["strategy", "decision authority", "switching-cost visibility", "EA-05"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["responding to change can become interruption", "backlogs can erase strategy"]
      ANTI_CEREMONY_BOUNDARY: "No mandatory sprint-planning or backlog-refinement meeting."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-25 protected sustainable focus"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Which planning horizons are currently distinguished?"
        - "What evidence is sufficient to change work already in progress?"
        - "Are switching and abandonment costs visible?"
        - "Does an existing native plan already adapt at the appropriate resolution?"

    - PROPERTY_ID: EA-14
      PROPERTY_NAME: Long-latency outcome and proxy governance
      FAILURE_MODE: "Short-cycle proxies improve while delayed value, safety or retention worsens."
      MATURE_FORM: "Validate surrogate relationships and retain long follow-up, holdouts or explicit uncertainty."
      TRIGGER: "The real outcome arrives after the decision cadence."
      CHEAP_PATH: "Use the direct outcome when timely; decline premature inference when no valid proxy exists."
      REQUIRED_PRECONDITIONS: ["causal assumptions", "longitudinal data", "drift monitoring"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["surrogates can fail", "long experiments also contain bias"]
      ANTI_CEREMONY_BOUNDARY: "An outcome dashboard or OKR is not proxy validation."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-01 short feedback"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Which important outcomes mature beyond the target's normal feedback window?"
        - "Are current proxies empirically linked to those outcomes?"
        - "Is proxy drift or population change monitored?"
        - "Would preserving uncertainty be safer than forcing a short-cycle metric?"

    - PROPERTY_ID: EA-15
      PROPERTY_NAME: Guarded experimentation and stopping rules
      FAILURE_MODE: "Ambiguous trials are interpreted post hoc or unsafe experiments externalise risk."
      MATURE_FORM: "Predefine hypothesis, decision rule, guardrails, population and stop condition."
      TRIGGER: "A material choice is uncertain and can be tested safely and reversibly."
      CHEAP_PATH: "Use analysis, simulation or independent review where exposure is dangerous."
      REQUIRED_PRECONDITIONS: ["credible design", "ethics/safety authority", "containment"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["p-hacking", "underpowered tests", "experimentation cannot decide every strategic question"]
      ANTI_CEREMONY_BOUNDARY: "Experiment count, discovery sprint or A/B tooling is not evidence quality."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-23 safety/security constraints"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "What decision would the proposed experiment change?"
        - "Are guardrails, stop criteria and affected populations explicit?"
        - "Could a cheaper non-exposure test discriminate the same assumption?"
        - "Does the target already prevent experiments from becoming activity metrics?"

    - PROPERTY_ID: EA-16
      PROPERTY_NAME: Authorised process adaptation
      FAILURE_MODE: "Repeated observations and retrospectives do not change the system producing the problem."
      MATURE_FORM: "Observe, analyse, authorise, change and remeasure at the level owning the cause."
      TRIGGER: "A repeated defect, delay, incident or overload has a changeable systemic cause."
      CHEAP_PATH: "Make an obvious local correction immediately when risk is low."
      REQUIRED_PRECONDITIONS: ["authority", "capacity", "psychological safety", "follow-up"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["retrospective theatre", "local teams may not own organisational causes"]
      ANTI_CEREMONY_BOUNDARY: "No retrospective format is required."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-24 controlled process change"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Can identified process defects lead to authorised changes?"
        - "Are changes assigned, implemented and subsequently measured?"
        - "Does the review occur at the level that owns the causal condition?"
        - "Would a scheduled retrospective add anything beyond an existing native correction loop?"

    - PROPERTY_ID: EA-17
      PROPERTY_NAME: System diagnostic measurement with anti-gaming
      FAILURE_MODE: "No evidence exists, or a proxy becomes a quota and drives dysfunctional behaviour."
      MATURE_FORM: "Use balanced local measures, countermetrics and qualitative interpretation solely for decisions and improvement."
      TRIGGER: "A repeated engineering decision requires observable system state."
      CHEAP_PATH: "Use a small qualitative review when precise instrumentation costs more than the decision."
      REQUIRED_PRECONDITIONS: ["operational definitions", "data quality", "no ranking/quota incentive"]
      EVIDENCE_STRENGTH: STRONG_ANTI_GAMING_RATIONALE_MIXED_MEASURE_VALIDITY
      CRITICISMS: ["Goodhart effects", "one-dimensional productivity", "local optimisation"]
      ANTI_CEREMONY_BOUNDARY: "No velocity, point, burndown or DORA target should be adopted as ritual."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-25 humane sustainable work"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "What decision does each current measure support?"
        - "Could participants improve the measure without improving the system?"
        - "Are quality, reliability, outcome and human countermetrics present?"
        - "Would measurement add more value than its collection and behavioural cost?"

    - PROPERTY_ID: EA-18
      PROPERTY_NAME: Bounded cross-functional ownership and autonomy
      FAILURE_MODE: "Handoffs and permission queues dominate, or nominal autonomy overloads teams without real authority."
      MATURE_FORM: "Put sufficient capability and authority near the work within explicit system and cognitive boundaries."
      TRIGGER: "Repeated delays arise from external handoffs or fragmented responsibility."
      CHEAP_PATH: "Use a well-defined specialist service where duplication is uneconomic or unsafe."
      REQUIRED_PRECONDITIONS: ["coherent boundary", "competence", "authority", "EA-19"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["pseudo-autonomy", "cognitive overload", "local optimisation"]
      ANTI_CEREMONY_BOUNDARY: "Scrum-team labels do not establish authority or capability."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-27 shared platform/specialist capability"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Which decisions can the working unit actually make without escalation?"
        - "Does it possess the skills and information needed for its claimed outcome?"
        - "Is autonomy externalising duplicated or compliance-heavy work?"
        - "Would a shared service or platform be cheaper than duplicating capability?"

    - PROPERTY_ID: EA-19
      PROPERTY_NAME: System-level dependency and interface control
      FAILURE_MODE: "Independent team plans collide at shared interfaces, resources or release boundaries."
      MATURE_FORM: "Remove avoidable dependencies and govern unavoidable ones at the smallest authoritative system level."
      TRIGGER: "Multiple teams or suppliers share architecture, integration or qualification."
      CHEAP_PATH: "Independent teams need only lightweight interface and integration evidence."
      REQUIRED_PRECONDITIONS: ["system boundary", "interface ownership", "EA-07", "EA-09"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["scaling frameworks create bureaucracy", "coordination can become universal synchronisation"]
      ANTI_CEREMONY_BOUNDARY: "No scaling framework, Scrum-of-Scrums or release train is presumed necessary."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-18 local autonomy"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Which dependencies actually control end-to-end completion?"
        - "Are interface and integration authorities explicit?"
        - "Can dependencies be removed rather than merely scheduled?"
        - "Would a framework add capability or only coordination ceremony?"

    - PROPERTY_ID: EA-20
      PROPERTY_NAME: Durable product or problem ownership
      FAILURE_MODE: "Temporary delivery teams hand off systems, knowledge and consequences."
      MATURE_FORM: "Maintain lifecycle responsibility where the problem and operation persist."
      TRIGGER: "The system has continuing users, operation and evolution."
      CHEAP_PATH: "Use an explicit acceptance and handover path for genuinely finite work."
      REQUIRED_PRECONDITIONS: ["stable problem boundary", "lifecycle funding", "outcome authority"]
      EVIDENCE_STRENGTH: MIXED
      CRITICISMS: ["not all work is a durable product", "product renaming can be cosmetic"]
      ANTI_CEREMONY_BOUNDARY: "A Product Owner title or product roadmap is insufficient."
      POSSIBLE_CONFLICTING_PROPERTY: "Finite project governance"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Do the consequences of the work persist after initial delivery?"
        - "Who retains knowledge and operational responsibility?"
        - "Would durable ownership improve decisions or create an immortal team without continuing value?"
        - "Does a strong existing handover model already provide the cheaper path?"

    - PROPERTY_ID: EA-21
      PROPERTY_NAME: Operational observability and incident learning
      FAILURE_MODE: "Production consequences remain invisible to development or incidents repeat without causal correction."
      MATURE_FORM: "Collect actionable operational evidence and close incident-learning actions."
      TRIGGER: "Runtime behaviour materially affects value, reliability or safety."
      CHEAP_PATH: "Use field-test and maintenance evidence for offline or embedded products."
      REQUIRED_PRECONDITIONS: ["telemetry", "change identity", "shared responsibility", "follow-up authority"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["telemetry overload", "blame", "privacy and surveillance"]
      ANTI_CEREMONY_BOUNDARY: "A dashboard, postmortem meeting or on-call rota is not the property."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-24 privacy and evidence governance"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Can operational effects be linked to the configuration or change that produced them?"
        - "Which signals are actionable rather than merely collected?"
        - "Do incident findings produce verified engineering changes?"
        - "Would additional observability create privacy or noise costs greater than its value?"

    - PROPERTY_ID: EA-22
      PROPERTY_NAME: Explicit reliability objectives and risk budgets
      FAILURE_MODE: "Release speed and reliability are negotiated politically or one side dominates without evidence."
      MATURE_FORM: "Bind change rate to user-relevant reliability or consequence limits."
      TRIGGER: "A continuously operated service faces a release–reliability trade-off."
      CHEAP_PATH: "Use hard hazard or qualification limits where failure is not legitimately tradeable."
      REQUIRED_PRECONDITIONS: ["valid SLI/SLO", "neutral measurement", "stop authority"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["wrong SLO", "failure budget treated as quota", "rare harms omitted"]
      ANTI_CEREMONY_BOUNDARY: "An SLO dashboard without release authority is ceremonial."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-10 rapid release readiness"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "What reliability or consequence boundary should constrain change?"
        - "Is it measured from the affected user's perspective?"
        - "Can the authority responsible actually slow or halt exposure?"
        - "Would a hard assurance constraint be more appropriate than an error budget?"

    - PROPERTY_ID: EA-23
      PROPERTY_NAME: Security, quality and reliability built into the lifecycle
      FAILURE_MODE: "Delivery speed externalises defects, vulnerabilities, hazards or operational instability."
      MATURE_FORM: "Continuous internal controls plus consequence-triggered independent evidence."
      TRIGGER: "Always relevant; depth follows consequence and exposure."
      CHEAP_PATH: "Use a minimal justified baseline for low-risk work."
      REQUIRED_PRECONDITIONS: ["quality/threat/hazard model", "credible verification", "release authority"]
      EVIDENCE_STRENGTH: STRONG_CONVERGENT
      CRITICISMS: ["tool-checkbox assurance", "automated gates can be falsely reassuring"]
      ANTI_CEREMONY_BOUNDARY: "A Definition of Done, scan or security sprint is not sufficient."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-01/EA-10 feedback and release speed"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Which quality, security and reliability obligations are currently downstream or externalised?"
        - "Can relevant controls be moved earlier without weakening independence?"
        - "Do automated gates establish the claims attributed to them?"
        - "Where is independent assurance still required?"

    - PROPERTY_ID: EA-24
      PROPERTY_NAME: Risk-based documentation, traceability, configuration and governance
      FAILURE_MODE: "Either compliance paperwork goes unused or critical knowledge and authority cannot be reconstructed."
      MATURE_FORM: "Maintain authoritative living evidence proportional to consequence, longevity and external obligation."
      TRIGGER: "Regulation, safety, security, long life, multiple organisations or significant turnover."
      CHEAP_PATH: "Retain a minimal decision/interface/operation record for low-risk small work."
      REQUIRED_PRECONDITIONS: ["source authority", "configuration identity", "update ownership"]
      EVIDENCE_STRENGTH: STRONG_CONTEXTUAL
      CRITICISMS: ["stale documentation", "traceability theatre", "approval queues"]
      ANTI_CEREMONY_BOUNDARY: "No template, document count or review board is intrinsically valuable."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-01 low-latency adaptation"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "What must a maintainer, operator, reviewer or authority be able to reconstruct?"
        - "Is current evidence authoritative, current and used in decisions?"
        - "Could documentation be generated or updated from existing source evidence?"
        - "Would an added artefact close a real knowledge/authority gap or only add ceremony?"

    - PROPERTY_ID: EA-25
      PROPERTY_NAME: Sustainable capacity and workload control
      FAILURE_MODE: "Chronic overtime and recurring deadlines erode quality, learning and retention."
      MATURE_FORM: "Normal demand fits durable capacity; emergencies require recovery and causal correction."
      TRIGGER: "Continuous knowledge work, on-call or repeated delivery demand."
      CHEAP_PATH: "A genuine bounded emergency may temporarily exceed normal load with explicit recovery."
      REQUIRED_PRECONDITIONS: ["visible demand", "capacity authority", "EA-05"]
      EVIDENCE_STRENGTH: MODERATE_CONVERGENT
      CRITICISMS: ["sprints can intensify work", "sustainable pace can mask under-resourcing"]
      ANTI_CEREMONY_BOUNDARY: "Capacity planning or a velocity cap does not itself create sustainability."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-03 urgent risk retirement"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Is emergency effort exceptional or the normal operating model?"
        - "Does current demand leave capacity for maintenance, learning and recovery?"
        - "Are workload signals hidden by individual heroics?"
        - "Would limiting WIP or stopping low-value work be cheaper than adding ceremony?"

    - PROPERTY_ID: EA-26
      PROPERTY_NAME: Shared stewardship and knowledge distribution
      FAILURE_MODE: "Critical change capability depends on one individual or isolated speciality."
      MATURE_FORM: "Use the cheapest suitable mix of pairing, review, rotation, records and backup ownership."
      TRIGGER: "Bus-factor or cross-area change risk is material."
      CHEAP_PATH: "Retain specialist ownership with explicit backup and interface evidence."
      REQUIRED_PRECONDITIONS: ["trust", "learning capacity", "tests or review evidence"]
      EVIDENCE_STRENGTH: MIXED
      CRITICISMS: ["forced pairing can reduce productivity or well-being", "diffuse ownership can weaken accountability"]
      ANTI_CEREMONY_BOUNDARY: "Pair programming and collective ownership are not mandatory."
      POSSIBLE_CONFLICTING_PROPERTY: "Deep specialist authority"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Which critical areas depend on one inaccessible knower?"
        - "Does the target already distribute knowledge through a different native path?"
        - "Would pairing, review, documentation or rotation be the cheapest control?"
        - "Could broad ownership undermine needed specialist accountability?"

    - PROPERTY_ID: EA-27
      PROPERTY_NAME: Platform and paved-road enablement
      FAILURE_MODE: "Teams repeatedly build undifferentiated infrastructure or a central platform becomes another mandatory queue."
      MATURE_FORM: "Offer the thinnest self-service, optional, secure-by-default shared capability that earns adoption."
      TRIGGER: "Repeated shared complexity and duplicated cognitive burden exceed platform cost."
      CHEAP_PATH: "Use managed services, templates or documentation for a simple/few-team environment."
      REQUIRED_PRECONDITIONS: ["internal user research", "platform product ownership", "escape path", "adoption evidence"]
      EVIDENCE_STRENGTH: EMERGING
      CRITICISMS: ["platform bureaucracy", "weak independent causal evidence", "mandated lowest common denominator"]
      ANTI_CEREMONY_BOUNDARY: "A platform team, portal or golden-path label is not sufficient."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-18 local autonomy"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Which repeated undifferentiated burdens are consuming multiple teams?"
        - "Would a shared template or managed service be cheaper than a platform?"
        - "Can teams escape the paved path for justified needs?"
        - "How would platform value and user burden be measured without adoption quotas?"

    - PROPERTY_ID: EA-28
      PROPERTY_NAME: Active stopping and option expiry
      FAILURE_MODE: "Backlogs and projects continue because work has started rather than because remaining value justifies remaining cost."
      MATURE_FORM: "Delete, defer or terminate work when remaining expected value no longer covers cost, risk and opportunity cost."
      TRIGGER: "New evidence materially changes expected value or exposes a superior option."
      CHEAP_PATH: "Complete only the minimum mandatory outcome for legal, safety or contractual obligations."
      REQUIRED_PRECONDITIONS: ["stop authority", "outcome/risk evidence", "safe partial-state handling"]
      EVIDENCE_STRENGTH: MIXED
      CRITICISMS: ["premature stopping", "short-termism", "infrastructure value may be delayed"]
      ANTI_CEREMONY_BOUNDARY: "Backlog grooming does not count unless work can actually be removed."
      POSSIBLE_CONFLICTING_PROPERTY: "EA-14 long-latency value"
      QUESTIONS_FOR_REPOSITORY_AUDIT:
        - "Can low-value work actually be deleted or stopped?"
        - "Are sunk costs being confused with remaining value?"
        - "Does the target already possess a native expiry or abandonment mechanism?"
        - "Could stopping now destroy strategically necessary or delayed-return capability?"

  CEREMONIES_TO_NOT_BLINDLY_ADOPT:
    - daily_standup
    - universal_fixed_sprint
    - two_week_sprint
    - sprint_planning_meeting
    - retrospective_meeting_format
    - sprint_demo
    - user_story_template
    - story_points
    - velocity_targets
    - planning_poker
    - burndown_chart
    - product_backlog_as_infinite_inventory
    - single_product_owner_role
    - scrum_master_role
    - mandatory_pair_programming
    - universal_tdd_sequence
    - scrum_of_scrums
    - release_train
    - feature_flags_without_lifecycle_control
    - weekly_discovery_quota
    - face_to_face_only_communication
    - universal_scaling_framework

  CONTEXTS_WHERE_PROPERTY_SHOULD_NOT_TRIGGER:
    - "Feedback is too noisy, costly or late to change the decision."
    - "The relevant decision is already stable, routine and cheaply reversible."
    - "A proposed small batch repeats irreducible qualification or mobilisation cost without additional learning."
    - "Progressive exposure cannot contain or reverse the harm."
    - "An experiment would expose subjects or systems to unethical or irreversible risk."
    - "A durable product team would outlive a genuinely finite problem without continuing value."
    - "A platform would cost more than shared templates or managed services."
    - "A specialist service is safer and cheaper than duplicating expertise across teams."
    - "A hard safety or legal constraint cannot legitimately be traded through an ordinary error budget."
    - "The long-term outcome has no validated short-term surrogate."
    - "Measurement cost and behavioural distortion exceed the value of the decision it supports."
    - "Documentation would duplicate an existing authoritative, current and usable source without closing a real evidence gap."

  PROPERTIES_WITH_STRONG_EMPIRICAL_OR_CONVERGENT_SUPPORT:
    - EA-02
    - EA-06
    - EA-07
    - EA-10
    - EA-16
    - EA-19
    - EA-21
    - EA-23
    - EA-25

  PROPERTIES_WITH_MIXED_OR_CONTEXTUAL_SUPPORT:
    - EA-01
    - EA-03
    - EA-04
    - EA-05
    - EA-08
    - EA-09
    - EA-11
    - EA-12
    - EA-13
    - EA-14
    - EA-15
    - EA-17
    - EA-18
    - EA-20
    - EA-22
    - EA-24
    - EA-26
    - EA-27
    - EA-28

  UNRESOLVED_PROPERTIES:
    - PROPERTY_ID: EA-09
      UNRESOLVED_ASPECT: "No generally validated numeric architecture-investment threshold."
    - PROPERTY_ID: EA-14
      UNRESOLVED_ASPECT: "Surrogate validity must be established separately for each domain and intervention."
    - PROPERTY_ID: EA-20
      UNRESOLVED_ASPECT: "Comparative causal evidence for product-mode over explicit project handover is sparse."
    - PROPERTY_ID: EA-27
      UNRESOLVED_ASPECT: "Independent comparative evidence for internal platform engineering is emerging."
    - PROPERTY_ID: EA-28
      UNRESOLVED_ASPECT: "Stopping rules for long-latency strategic and infrastructural work remain weakly validated."

  FROZEN_SYNTHESIS:
    DESCRIPTION: >
      EVOLVED_AGILE is an adaptive engineering orientation that shortens feedback
      only where the signal is decision-relevant; reduces batches and WIP only
      where total economics support it; integrates and verifies continuously where
      accumulated integration risk dominates; maintains technical changeability;
      exposes product assumptions to representative evidence; protects deliberate
      architecture, configuration and assurance where commitment is expensive;
      connects development to operational and long-latency outcomes; constrains
      change by reliability, safety and security; and changes its own process only
      through authorised and measured learning loops.
    EXPLICITLY_NOT:
      - "Scrum plus DevOps plus additional meetings"
      - "a universal sprint cadence"
      - "a licence to omit planning, architecture, documentation or governance"
      - "continuous deployment in every context"
      - "local autonomy without system responsibility"
      - "a branded scaling framework"
      - "a set of proxy metrics or productivity quotas"
```

EVOLVED_AGILE_RESEARCH_STATE: FROZEN
PROPERTY_POPULATION_TOTAL: 28
PROPERTY_POPULATION_EXAMINED: 28
PROPERTY_COVERAGE: 28/28
EVOLVED_AGILE_AUDIT_INTAKE: COMPLETE
EXTERNAL_RESEARCH_READY_FOR_REPOSITORY_CROSSWALK: YES
