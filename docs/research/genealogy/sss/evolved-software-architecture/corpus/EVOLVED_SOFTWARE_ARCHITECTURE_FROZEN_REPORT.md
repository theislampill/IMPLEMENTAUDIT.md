# Evolved Software Architecture

**Independent tradition study — revision ESA-2026-09-06-r1**  
**Analytical label:** `EVOLVED_SOFTWARE_ARCHITECTURE`  
**Research cut-off and run date:** 6 September 2026  
**Corpus:** 68 examined candidates; 66 exact source records; nine examined mandatory families.

“Evolved” denotes this report’s source-grounded, criticism-tested reconstruction. It is not the name of an established academic school, a claim of historical inevitability, or a certification of any implementation. Software Architecture is the established subject. The later SSS grouping is provisional; neither of its other two research corpora was consulted, and no cross-trifecta synthesis was performed.

## Executive judgement

The strongest surviving account is **consequence-bound architectural reasoning coupled to action and evidence**. A system has consequential structures and interactions whether or not anyone produces a diagram. Architectural work earns its place when it helps people distinguish relevant dependencies and quality consequences, compare feasible choices, coordinate affected parties, make legitimate changes, and discover when the resulting system no longer matches the reasons for those choices. A document, meeting, pattern, model or automated check can supply one of those functions. Its mere presence cannot establish the function’s success. This is the report’s analytical synthesis, not an independently tested package.

The conditional core does not select microservices over monoliths, central architects over autonomous teams, or formal models over direct inspection. It asks what each alternative protects, under what assumptions, at whose cost, and with what evidence. Decomposition is not synonymous with distribution. Functional equivalence is not equivalence of operating qualities. Conformance is not the preservation of every historical rule. A bounded controller is not an open-ended architect. These distinctions alter both the retained mechanisms and the rejected candidate denominator. [ESA-S001, decomposition criteria; ESA-S017, scenario construction; ESA-S039, consolidation rationale; ESA-S045, reflexion mapping; ESA-S054, robustness results.]

The study retains nine candidates strongly as criteria or mechanisms, fifteen in evolved form, thirteen as context-dependent, eight as assumption-sensitive, eight as domain-specific, and two as useful but easily gamed. These **55 crosswalk-worthy candidates are not 55 mandatory controls**. Another eight are rejected/disfavoured, two are ceremony rather than a general property, one has no general property, one mixed candidate is superseded, and one capability claim remains unresolved. “Strongly retained” describes the adjudication of a bounded mechanism, not strong comparative causal evidence for all settings.

## 1. What architecture is—and what an architecture description cannot do

The field does not have one uncontested definition that can replace inquiry. Perry and Wolf’s elements, form and rationale make architectural organisation an object of study. The later importance, shared-understanding and cost-of-change formulations discussed by Fowler help identify consequential choices, but they do not supply a context-free threshold. A local implementation detail can acquire architectural significance when a shared invariant or external obligation depends on it. Conversely, a visually prominent box can be an inconsequential representation choice. The mature criterion is therefore a stated relation between a decision and its consequences, not its altitude on a diagram. [ESA-S002, foundations; ESA-S010, definitions and architect roles.]

This report distinguishes software architecture from detailed design without pretending that the boundary is fixed for every project. It also distinguishes software from enterprise, hardware and systems architecture, and from organisational structure. Those fields can constrain or interact with software architecture; they are not annexed simply because a decision matters. The software/organisation interface is studied where communication, ownership or authority affects software decisions. The architecture/product-family interface is studied where commonality and variation alter software structures. Neither intersection completes the neighbouring discipline.

Three objects must remain separate: the architecture attributed to the real system, its description, and an actor’s belief about either. A description can be internally consistent and obsolete; a recovered graph can be current and semantically incomplete; an architect can know an unwritten constraint that the implemented system does not actually enforce. Evidence of one does not automatically establish the others. A useful description states its relevant object, relationship definitions and observation limits. Correspondence work then investigates the particular assertion on which a decision depends. [ESA-S011, introductory conceptual scope; ESA-S026, mismatch assumptions; ESA-S045, high-level/source mappings.]

IEEE 1471-2000 and the 2011 and 2022 editions of ISO/IEC/IEEE 42010 belong to the history of architecture **description**. The official abstracts and the 2022 introductory preview support that distinction. Their full normative texts were not inspected in this run. Consequently this packet supplies neither a clause-level compliance checklist nor a claim that standard-conforming descriptions yield good operating architecture. Publication, adoption, compliance and benefit are different propositions. [ESA-S065, official abstract and publication metadata; ESA-S012, official abstract; ESA-S011, foreword/introduction/scope preview.]

## 2. A plural genealogy rather than a procession of fashions

Software architecture’s later research vocabulary drew attention to problems already present in software construction. Dijkstra’s account of THE organises reasoning through levels of abstraction. Parnas asks a different decomposition question: which design knowledge should each responsibility hide so that selected changes need not propagate? Early reuse aspirations, conceptual integrity, program families, and honest explanation of design all contribute distinct concerns. None implies that the whole modern field descends from a single paper, nor that the later vocabulary retroactively identifies a unified school in every precursor. [ESA-S005, system organisation; ESA-S001, modularisation criteria; ESA-S006, extension/contraction and uses relations; ESA-S007, inspected opening; ESA-S008 and ESA-S009, design arguments.]

The 1990s architecture programme made styles, components, connectors and system-wide relationships explicit research objects. It developed several answers, not one methodology: multiple views for different concerns; languages with analysable semantics; scenarios for quality evaluation; reusable structures and families; and mappings between intended and realised organisation. Each can compensate for another’s omissions, but each also has an independent burden. A formal connector model is not an economic evaluation. A deployment view does not recover the rationale for a shared data model. An evaluation workshop cannot make an unobserved fault impossible. [ESA-S002–004; ESA-S014–015; ESA-S019–020; ESA-S045, identified locators in source table.]

Later decision-knowledge, continuous-evaluation and runtime-adaptation work shifts attention from a one-time picture towards change. Service orientation, REST, domain-driven design and microservices add distinguishable interaction, semantic and deployment concerns. Learned components and serverless platforms change dependency and environmental assumptions. Sustainability and LLM assistance are contemporary research subjects, not automatic replacements for information hiding or quality reasoning. Some links are explicit imports; others are convergence or analogy. The dated genealogy below records which interpretation is warranted.

## 3. Decomposition works by controlling dependence, not multiplying boxes

Information hiding’s useful unit is a responsibility and its concealed design knowledge. Its payoff depends on a plausible change hypothesis and an interface that does not force clients to know the hidden choice. A processing-step decomposition can be appropriate for one purpose and poor for another. A module is not necessarily a process, service, team or deployment. The expected protection is tested by asking which obligations and clients must change when the selected decision changes. Wrong predictions, leaky semantics or communication overhead can defeat that protection. [ESA-S001, KWIC alternatives and critique; ESA-S006, uses and family design.]

Interfaces must therefore preserve more than signatures. Aesop’s mismatch experience concerns assumptions about control, data and other environmental properties carried by supposedly reusable parts. A shared table, callback discipline, state interpretation or administrative channel can cross a nominal boundary without appearing in a simple import graph. The mature response is not to specify everything about everything: it is to expose and test the assumptions consequential to the intended composition. Concrete examples and focused integration tests may be sufficient; formalisation becomes valuable when its extra reach justifies its cost. [ESA-S026, mismatch categories and case; ESA-S015, connector semantics.]

Dependency kinds must be selected for the question. A calls graph concerns invocation; a uses relation concerns correctness dependence; configuration and shared data can determine runtime effects; co-change can reveal a work pattern without proving logical necessity. Claims of operational independence require evidence about the channels that can propagate the relevant change or failure. Separate deployments alone do not provide that evidence. This is especially important for learned systems, where data distributions, feedback and undeclared consumers can alter behaviour without a source-interface edit. [ESA-S006, uses relation; ESA-S031, dependency construction; ESA-S056, hidden dependency/feedback discussion.]

The same discipline prevents a false choice between uncontrolled monoliths and universal microservices. Shopify’s account describes deliberate componentisation within a monolith. Istio’s account explains control-plane consolidation where shared release, scale and administration undermined the value of splitting services; it did not remove the separate data-plane proxies. These are consequential counterexamples to a universal maturity ladder, not proof that either deployment style always wins. Selective boundaries, explicit translations and justified consolidation remain available alternatives. [ESA-S038, componentisation account; ESA-S039, istiod rationale.]

## 4. Qualities need scenarios, mechanisms and representative observations

A quality attribute becomes useful to design when its response is stated under an environment and stimulus. A latency aspiration without load, a resilience aspiration without faults, or a modifiability aspiration without a change class does not yet discriminate architectures. Quality Attribute Workshops and related scenario methods make those conditions discussable. They also expose a selection problem: voting, familiar examples or available participants may omit consequential users, rare conditions or non-negotiable limits. Consensus is an achievement of coordination, not proof of scenario coverage. [ESA-S017, scenario generation and prioritisation; ESA-S020, utility/scenario analysis.]

Tactics explain how a structural or behavioural choice influences parameters of a quality model. They are not guarantees. Redundancy, caching, isolation, abstraction and indirection can protect one consequence while changing another. The tactic must therefore be coupled to its causal explanation, the applicable assumptions, and a check of the resulting response. Usability belongs in this inquiry when a user interaction—such as cancellation, recovery or continuity—requires architectural support; it is not always repairable at the presentation layer. Equally, not every usability concern requires architecture machinery. [ESA-S016, quality-model/tactic reasoning; ESA-S018, scenario selection and architectural implications.]

Trade-offs are not resolved by declaring every quality equally important. Hard constraints first limit which options are admissible; legitimately negotiable qualities can then be compared with their costs and uncertainties. Economic models can expose preferences and sensitivity, but weighted scores do not by themselves grant permission to violate an external obligation. Nor is one choice’s benefit established by movement in a convenient proxy. The architecture, workload, hardware and other interventions can change together, making causal attribution difficult. [ESA-S020, trade-off and sensitivity points; ESA-S022, cost/utility reasoning.]

EcoFaaS provides a useful contemporary discriminator rather than a universal prescription. Its comparison concerns specified benchmarks, server clusters, energy measurements and an application SLO defined relative to unloaded warm latency. Reported energy/tail improvements coexist with higher mean latency relative to a baseline. A legitimate judgement depends on the permitted trade-off and measurement boundary. Package/DRAM energy cannot be silently upgraded to whole-lifecycle carbon savings, and a serverless label supplies neither conclusion. [ESA-S061, evaluation design and latency/energy results; ESA-S058, sustainability evidence gaps.]

## 5. Representation and formal analysis are instruments with correspondence burdens

Kruchten’s 4+1 approach supplies distinct perspectives for different problems and explicitly allows unnecessary views to be omitted. Its value lies in the questions the views answer and the relationships among them, not in completing five artefacts. Other viewpoint selections can be adequate. Where two views matter to one decision, their correspondence must be understood: a logical component might map to several deployment units, or several responsibilities to one executable. A notation is not the semantic relation it represents. [ESA-S003, view description and iterative approach.]

ADLs can make architectural interaction precise enough for stronger analysis. In the inspected Wright account, a conditional result connects compatible ports, conservative deadlock-free connector glue and deadlock freedom of the instantiated connector. The additional conditions matter: compatibility alone permits an inference the counterexample defeats. Even the correct theorem concerns a specified CSP model. A deployment with omitted channels or a faulty implementation is not covered merely because its diagram resembles that model. Strong formal validity and weak transfer evidence can coexist. [ESA-S015, §8 and Theorem 1; counterexample and well-formedness discussion.]

Reconstruction has a similar but non-identical limitation. Reflexion models relate a high-level model to extracted source relations through explicit mappings. Their results identify convergence, divergence or absence for those mappings; they do not recover all intended rationale or runtime behaviour. Static analysis, configuration inspection and dynamic observation may be complementary, but their combination does not magically become complete. The analyst should disclose which relations were observed, inferred, sampled or still unknown. [ESA-S045, mapping and reflexion relations; ESA-S046–048, empirical limitations.]

## 6. Evaluation, design and decisions form an interleaved activity

SAAM makes scenario interactions and change consequences discussable. ATAM adds multi-quality risk, sensitivity and trade-off reasoning. CBAM examines uncertain economic preferences and design investments. Driver-based design supplies a constructive method: identify the drivers that matter, select design concepts, allocate responsibilities/interfaces, and check the developing alternative. The general architectural design model explicitly accommodates interleaving analysis, synthesis and evaluation. A fixed one-pass pipeline would destroy that feedback rather than preserve the tradition. [ESA-S019–020; ESA-S022; ESA-S024, method steps; ESA-S025, general model.]

The evidence does not establish that a full method is always worth its cost. The SEI risk-theme study examines 18 ATAM reports and 99 themes, not randomised downstream outcomes. The 2017 internal replication compares evaluation tasks using 16 convenience-sampled practitioner students; it reports some advantages for a comparator without detecting efficiency/ease advantages. Small samples, training, reference judgements and shared research materials constrain transfer. These findings support neither unconditional ATAM superiority nor a conclusion that architectural evaluation is useless. They support choosing the smallest evaluation capable of resolving the consequential uncertainty and escalating when its residual risk is unacceptable. [ESA-S021, sample and results; ESA-S023, design, results and validity threats.]

Decision knowledge completes an otherwise disconnected relationship between analysis and later change. The relevant record preserves enough context, choice, consequences and status for a real inheritor. Nygard’s concise ADR form supplies an important economical practice; this synthesis adds explicitly recoverable alternatives and reopening conditions where the later consumer needs them, rather than falsely attributing every expanded field to his template. Rationale surveys concern perceived usefulness and barriers, not causal proof that documentation volume improves systems. [ESA-S027, survey design/results; ESA-S029, proposed sections.]

An honest rationalised account can make a discovered design understandable without pretending the actual discovery followed that order. Keep explanation and historical provenance separate. Likewise keep architectural expertise, decision authority and execution capability separate. An evaluator can identify a risk without being authorised to accept it; an authorised decision can still fail to be implemented; a successful deployment can still miss its intended quality. Architectural communication must reach the people who can decide or act, while preserving the interests of those bearing the consequences. [ESA-S009, rational-process argument; ESA-S020, stakeholder roles; ESA-S035, interaction and effects.]

## 7. Conformance and evolution require revisable baselines

A useful conformance finding has a current baseline, a defined mapping and an affected concern. Departure from a diagram does not by itself establish harmful erosion. The right response may be correction, an explained exception, or a better design with a revised baseline. A smell score is a triage signal whose meaning must be investigated. The examined smell/performance study uses two systems and selected refactorings; improvements are not uniform across every measured method. Review-comment studies and classifiers identify discussion or text labels, not ground truth about every architectural harm. [ESA-S002, drift/erosion vocabulary; ESA-S045, conformance mapping; ESA-S046–048, methods/results.]

Architectural debt is similarly weakened by indiscriminate use. A disliked design or future-change worry is not automatically a measured debt burden. The debt metaphor can usefully distinguish an expedient choice, the cost of changing it and recurring consequences, but numerical interest requires evidence. The examined architecture-debt study offers a qualitative account across seven sites in five companies. It does not establish a universal interest curve or a duty to repay every imperfection. A valid outcome can be deliberate retention when intervention costs exceed the burden. [ESA-S049, original experience; ESA-S050, methods and qualitative model.]

Migration adds intermediate-state obligations: compatibility, data interpretation, operational continuity and eventual retirement of scaffolding. Fitness functions can repeatedly check selected conditions, but selected conditions are not the whole architecture. A stale fitness function can obstruct a justified improvement or reward gaming. Monitoring and governance should therefore be revisable and retireable, not permanent merely because they once protected a risk. Future flexibility is an investment under a change hypothesis; abstraction can be narrowed or removed when that hypothesis fails. [ESA-S040, incremental migration; ESA-S043–044, fitness-function guidance; ESA-S006, extension/contraction.]

## 8. Runtime adaptation and current frontiers

Architecture-based adaptation makes the connection between information and operation explicit. Probes and gauges provide observations; models support decisions; policies constrain actions; effectors change the running system. None of those transformations should be silently identified with another. The Rainbow robustness experiments show why: corrupted or inadequate architectural state can undermine adaptation while leaving the controller apparently active. The 2023 industry survey broadens reported contexts, but its selected respondent population cannot prove that self-adaptation is generally superior. [ESA-S051–055, identified source locators.]

Changing the policy or adaptation mechanism itself requires the same attention to observation, authority, effect and continuity. Improving one metric cannot grant a new mandate or erase an external constraint. A safer fallback may be a simpler controller or human operation; in some settings the cost of delay makes that choice difficult. The composition exposes that decision rather than inventing a universal shutdown rule. Bounded runtime adaptation remains a domain-specific mechanism; self-revision is assumption-sensitive; open-ended autonomous architecting is a separate unresolved claim.

The current-year literature reinforces that separation. The examined LLM-assisted evaluation study uses seven analysed student groups after exclusions. The architectural-pattern study uses one execution per configuration and reports problems with self-reported metrics. Decomposition comparisons rely on benchmark structures and mix reported with reproduced results. These are evidence about selected tasks, not successful long-lived autonomous architecture operation. Assistance may still be useful when independently checked and economical; the available evidence does not warrant handing its outputs unreviewed authority. [ESA-S059, experiment and exclusions; ESA-S062, experiment/threats and metrics; ESA-S063, comparison provenance.]

## How to read the evidence architecture

The following seventeen labelled sections are the frozen explanatory index. The complete property JSON contains all required common fields and all ten domain-profile fields for every candidate. The coverage JSON also carries the detailed genealogy, criticism, ceremony, tension, domain-model and case registers. The composition JSON makes every relation’s direction, guard, shared/incompatible assumptions, costs and unresolved obligation explicit. Its 65 relations do not imply 65 workflow steps.

Evidence roles are kept separate throughout. Standards establish specified concepts or obligations only within inspected access. Formal results establish conclusions inside their models. Field accounts establish observed settings. Comparative studies establish their reported comparisons, with their samples and validity limits. This report’s synthesis is a researcher interpretation over that material. Shared programmes and datasets—including ATAM, Aesop, Rainbow, erosion studies and reused microservice survey/benchmark material—are not counted as independent replications. There is no aggregate confidence percentage and no demonstrated effectiveness estimate for the assembled Evolved system.

## EVOLVED_SOFTWARE_ARCHITECTURE_TIMELINE

Dates distinguish original events, publication, accessed revision and metadata. A later web upload is not a new founding publication. The full dating qualifications remain in the source and coverage tables.

| Date or period | Development | Sources |
|---|---|---|
| 1968; inspected later transcription | Structured abstraction and layered responsibility | ESA-S005 |
| 1968; empirical studies 2008 and inspected 2011 working-paper revision | Socio-technical coordination and mirroring | ESA-S030, ESA-S031, ESA-S032 |
| 1968 event/1969 report; 1995 case; institutional collection inspected 2026 | Reusable components, software families and architectural mismatch | ESA-S007, ESA-S026, ESA-S066 |
| 1972; 1976 bibliographic anchor; 1979 | Information hiding, uses relations and program families | ESA-S001, ESA-S006, ESA-S064 |
| 1986 inspected texts; 1975 book an uninspected historical lead | Conceptual integrity and realistic design explanation | ESA-S008, ESA-S009, ESA-S010 |
| 1992–1994 | Software architecture as a distinct research object: structures, styles and connectors | ESA-S002, ESA-S004 |
| 1992 debt account; 2014 architecture-debt field study; 2019 guidance; 2024 revised migration essay | Architectural debt, incremental migration and continuous evaluation | ESA-S049, ESA-S050, ESA-S040, ESA-S043, ESA-S044 |
| SAAM 1994; ATAM 2000; CBAM 2001; QAW 2003; subsequent evaluations | Scenario-based quality evaluation and economic reasoning | ESA-S019, ESA-S020, ESA-S022, ESA-S017, ESA-S021, ESA-S023 |
| 1995 onwards | Multiple views and concern-selected representation | ESA-S003, ESA-S014, ESA-S011 |
| 1995; 2022–2025 | Conformance, reconstruction, erosion and smell analysis | ESA-S045, ESA-S046, ESA-S047, ESA-S048 |
| 1990s; 1997 paper/1998 inspected revision; 2000 taxonomy | ADLs and formal connector reasoning | ESA-S014, ESA-S015 |
| 1998–1999; Rainbow 2004; robustness 2014; industrial survey 2023 | Architecture-based runtime change and self-adaptation | ESA-S051, ESA-S052, ESA-S053, ESA-S054, ESA-S055 |
| 2000 dissertation | REST as a constrained hypermedia architectural style | ESA-S034 |
| 2000-10-09 publication | IEEE 1471 architecture-description recommendation | ESA-S065, ESA-S013 |
| 2003 book as historical lead; inspected author reference dated 2015 | Domain-driven design intersection: bounded semantic models | ESA-S033, ESA-S036 |
| 2005 inspected report; 2005 decision-paper abstract; 2011 ADR article | Architectural decisions, rationale and compact records | ESA-S027, ESA-S028, ESA-S029 |
| OASIS Reference Model 1.0, 2006 | Service-oriented reference modelling | ESA-S035 |
| ADD v2.0 2006; general model 2007, online 2006 | Driver-based recursive design and interleaved design/evaluation | ESA-S024, ESA-S025, ESA-S016 |
| 2011 | ISO/IEC/IEEE 42010 first edition | ESA-S012, ESA-S013 |
| 2014 account; 2015 caution; 2019 and 2020 field cases; 2024–2026 research | Microservices, modular monoliths and consolidation | ESA-S036, ESA-S037, ESA-S038, ESA-S039, ESA-S060, ESA-S063 |
| 2015 engineering account and current continuation | Architecture for learned components | ESA-S056, ESA-S062 |
| 2019 Berkeley report; 2024 energy-control study | Serverless and provider-managed architectural boundaries | ESA-S057, ESA-S061 |
| 2022 | ISO/IEC/IEEE 42010 second edition | ESA-S011 |
| 2024 comparative experiment; 2025 rapid meta-review | Sustainability as an architecture concern | ESA-S061, ESA-S058 |
| 2026 studies through the 2026-09-06 cut-off | LLM-based architectural assistance and autonomous-architecting claims | ESA-S059, ESA-S062, ESA-S063 |

## EVOLVED_SOFTWARE_ARCHITECTURE_GENEALOGY

The genealogy is plural and typed. A shared problem is not documentary proof of influence. Standard editions are separate nodes; later interpretations and inaccessible originals are explicitly qualified.

### ESA-G01 — Structured abstraction and layered responsibility

Reason about concurrent system behaviour and make implementation manageable. A hierarchy of levels and carefully delimited abstractions organise a small multiprogramming system. An early concrete account of organising software through abstraction rather than a later architecture-description notation.

**Evolution and reception:** Later architecture discussions share abstraction concerns; direct influence on every branch is not inferred. **Limit:** One author-reported system and partial testing; not evidence that all modern layers yield reliability. [ESA-S005.]

### ESA-G02 — Information hiding, uses relations and program families

Processing-step decomposition exposes design choices and makes anticipated changes propagate. Assign responsibilities around hidden decisions; distinguish uses from calls and plan feasible family extension/contraction. A semantic criterion for decomposition and an architectural family/change account.

**Evolution and reception:** The 1979 paper extends the author’s earlier decomposition concern and exposes limits in simple hierarchical accounts. **Limit:** Change hypotheses can be wrong; the KWIC illustration is not an industrial causal estimate. The 1976 item was inspected as metadata only. [ESA-S001, ESA-S006, ESA-S064.]

### ESA-G03 — Conceptual integrity and realistic design explanation

Incoherent concepts and an idealised sequential account make design hard to communicate or maintain. Seek conceptual coherence and preserve a rationalised explanation while accepting iteration and discovery. Integrity is a system-level concern; explanatory order need not match the actual path of invention.

**Evolution and reception:** Fowler’s later architect-role discussion challenges detached central authority without dispensing with significant design decisions. **Limit:** The 1975 monograph was not read in this run. Neither coherence nor retrospective rationalisation licenses one-person control or false provenance. [ESA-S008, ESA-S009, ESA-S010.]

### ESA-G04 — Software architecture as a distinct research object: structures, styles and connectors

Programming-level accounts do not sufficiently describe consequential overall organisation. Describe elements, form and rationale; classify recurring component-and-connector organisations and combinations. A plural research programme for system structures, interactions and quality consequences.

**Evolution and reception:** View-based descriptions, formal languages and quality evaluation develop related but non-identical answers. **Limit:** Styles overlap and combine; categorisation is not proof of a best architecture. [ESA-S002, ESA-S004.]

### ESA-G05 — Multiple views and concern-selected representation

A single structural drawing cannot serve every stakeholder and design question. Use views with distinct concerns and semantics; scenarios expose their interaction; keep correspondences explicit. 4+1 is a worked view scheme, not a claim that all five artefacts are necessary everywhere.

**Evolution and reception:** Description standardisation generalises concern/viewpoint vocabulary without validating design effectiveness. **Limit:** Views can disagree, become stale or omit runtime/configuration relations. [ESA-S003, ESA-S014, ESA-S011.]

### ESA-G06 — ADLs and formal connector reasoning

Informal interaction arrows omit assumptions needed to reason about composition. Give components/connectors semantic models and check compatibility under well-formedness conditions. Wright supplies a conditional deadlock result and a counterexample to compatibility alone.

**Evolution and reception:** Formal capability survives as a selective branch; no evidence warrants universal ADL adoption. **Limit:** CSP model assumptions and implementation correspondence remain obligations; taxonomy completeness is historical, not a claim about every current tool. [ESA-S014, ESA-S015.]

### ESA-G07 — Scenario-based quality evaluation and economic reasoning

Quality slogans and a preferred design conceal trade-offs, risks and alternatives. Elicit scenarios; explore sensitivity and trade-offs; estimate utility/cost under assumptions. Structured evaluation can make quality reasoning and stakeholder differences explicit.

**Evolution and reception:** Evaluation evolves into lighter or more specialised alternatives and uncertain economic models rather than a quality certificate. **Limit:** Selected scenarios may miss decisive conditions; risk reports are not downstream controlled outcomes; comparative evidence is small and mixed. [ESA-S019, ESA-S020, ESA-S022, ESA-S017, ESA-S021, ESA-S023.]

### ESA-G08 — Architectural decisions, rationale and compact records

Later actors see structures but cannot recover why alternatives were rejected. Preserve context, decision status and consequences; maintain supersession and links where useful. Decision knowledge supplements structural descriptions and can aid handover/reconsideration.

**Evolution and reception:** Concise records reduce ceremony but still require a real consumer and ageing/reopening discipline. **Limit:** Survey perceptions do not prove benefit; the Archium paper was abstract-only and does not support detailed tool claims. [ESA-S027, ESA-S028, ESA-S029.]

### ESA-G09 — Conformance, reconstruction, erosion and smell analysis

The implemented dependency structure can diverge from intended design without being recognised. Map extracted relations to a high-level model; inspect convergence/divergence; investigate risks and context. Conformance is relative to mappings and rules, not a judgement that old intent is always correct.

**Evolution and reception:** Modern classifiers and smell studies add evidence channels while preserving baseline and observation validity obligations. **Limit:** Extraction omits semantics; smell/performance effects vary; code-review comments measure discussion rather than prevalence of harmful erosion. [ESA-S045, ESA-S046, ESA-S047, ESA-S048.]

### ESA-G10 — Socio-technical coordination and mirroring

The people who must coordinate may not match the consequential dependencies in their work. Compare task/software dependencies with observed communication; investigate organisational/design relationships. An architectural intersection with work coordination rather than an org-chart design algorithm.

**Evolution and reception:** Bounded coordination hypotheses survive; simplistic organisational mirroring is rejected. **Limit:** Single-organisation and matched-product studies are observational and confounded; deterministic causal readings are unsupported. [ESA-S030, ESA-S031, ESA-S032.]

### ESA-G11 — Architecture-based runtime change and self-adaptation

Static descriptions cannot guide or explain structural changes during operation. Connect probes, models, policies and effectors; constrain changes and evaluate effects. Architecture becomes an operative runtime abstraction, not merely documentation.

**Evolution and reception:** Robustness experiments sharpen observation obligations, while industry survey results broaden reported settings without estimating causal benefit. **Limit:** Model-state corruption and silent observation failures can defeat decisions; prototypes/surveys are not general autonomy evidence. [ESA-S051, ESA-S052, ESA-S053, ESA-S054, ESA-S055.]

### ESA-G12 — Reusable components, software families and architectural mismatch

Reuse and interchangeability promise leverage, but compatible-looking parts carry hidden assumptions. Component reuse must reconcile control, data, state and platform assumptions; family architecture preserves commonality/variation. McIlroy’s opening supplies an early aspiration; Aesop provides a concrete negative integration experience.

**Evolution and reception:** The mismatch critique narrows naive component substitution rather than refuting all reuse. **Limit:** The McIlroy opening and collection entry descriptions do not support uninspected implementation details or economic outcomes. Aesop publications share one programme. [ESA-S007, ESA-S026, ESA-S066.]

### ESA-G13 — Domain-driven design intersection: bounded semantic models

Different business contexts require different meanings for apparently shared terms. Bound a model’s applicability and map explicit relationships/translations between contexts. A semantic boundary is distinct from a code module or deployment boundary.

**Evolution and reception:** Microservice guidance explicitly uses bounded-context ideas, but that does not justify one service per context. **Limit:** The original book was not read; bounded contexts are not automatically services and translations have costs. [ESA-S033, ESA-S036.]

### ESA-G14 — REST as a constrained hypermedia architectural style

Distributed hypermedia needs evolvability, scalability and interactions among independently developed participants. Combine client/server, stateless interaction, cacheability, uniform interface, layering and optional code-on-demand. Uniform-interface constraints include resource identification, representations, self-descriptive messages and hypermedia application state.

**Evolution and reception:** The domain-specific constraint set remains distinguishable from generic service orientation. **Limit:** A generic interface sacrifices some application-specific efficiency; REST is not every HTTP service and statelessness does not remove persistent resource state. [ESA-S034.]

### ESA-G15 — Service-oriented reference modelling

Services cross ownership and access boundaries and need a common conceptual account. Relate visibility, interaction, service descriptions, execution context and real-world effects. Awareness, willingness and reachability are not interchangeable with authorisation or successful effect.

**Evolution and reception:** Service concepts overlap later microservice discourse, but a single unambiguous genealogy is not established. **Limit:** A reference model does not prescribe one stack or establish service economics. [ESA-S035.]

### ESA-G16 — Microservices, modular monoliths and consolidation

Large products may need differentiated deployment and team change, but distributed boundaries introduce operational coordination. Select deployment boundaries according to genuine independence needs; preserve modularity or consolidate when boundaries supply little benefit. Shopify and Istio show that purposeful internal modules or consolidation can be legitimate outcomes.

**Evolution and reception:** Maturity need not mean more services: Istio consolidated its control plane while retaining separate proxies. **Limit:** These are context-specific author/project accounts, not randomised comparisons. Benchmark decomposition metrics are not operating outcomes. [ESA-S036, ESA-S037, ESA-S038, ESA-S039, ESA-S060, ESA-S063.]

### ESA-G17 — Architectural debt, incremental migration and continuous evaluation

Expedient choices and changing conditions can accumulate costs that a one-off design description conceals. Distinguish debt consequences, migrate through viable intermediate states and monitor selected architecture-related conditions. Architecture evaluation and revision can be continuous, and simplification can be an improvement.

**Evolution and reception:** The mature form couples observations to revisable decisions rather than preserving every old rule or buying every future option. **Limit:** Debt metaphors are not monetary measurements; fitness functions are selected proxies; migration adds coexistence costs. [ESA-S049, ESA-S050, ESA-S040, ESA-S043, ESA-S044.]

### ESA-G18 — Architecture for learned components

Data, feedback and undeclared consumers cross ordinary software boundaries. Treat data/configuration/feedback obligations as architectural dependencies and evaluate system behaviour, not code alone. A documented domain translation of dependency, interface and debt reasoning.

**Evolution and reception:** Current LLM work expands assistance but does not remove hidden coupling or validation burdens. **Limit:** The 2015 account is practitioner evidence, not a controlled architecture intervention; generated structural proposals do not validate learned-system behaviour. [ESA-S056, ESA-S062.]

### ESA-G19 — Serverless and provider-managed architectural boundaries

Invocation-managed platforms shift state, timing, resource and administrative assumptions. Design around provider execution boundaries and measure actual workload/cold-start/resource consequences. Serverless is an architectural translation with distinctive constraints, not an automatic simplification or sustainability guarantee.

**Evolution and reception:** EcoFaaS tests a specific energy/latency trade-off under stated platform and SLO assumptions. **Limit:** The 2019 service descriptions are historical; no current price, quota or provider feature is inferred. [ESA-S057, ESA-S061.]

### ESA-G20 — Sustainability as an architecture concern

Energy and resource use can be obscured by architecture proxies or isolated efficiency claims. Declare measurement boundary and workload, then consider energy with latency, reliability and other constraints. Architecture can contribute to sustainability while requiring broader lifecycle/context evidence.

**Evolution and reception:** The field supports a bounded concern and exposes evidence gaps rather than establishing one universally green architecture. **Limit:** Measured package/DRAM energy is not whole-lifecycle carbon; a rapid review and focus group do not prove universal prescriptions. [ESA-S061, ESA-S058.]

### ESA-G21 — LLM-based architectural assistance and autonomous-architecting claims

Generating alternatives and evaluating architectural material is costly; tools promise automation. Compare generated analyses/proposals with independent criteria and real-system evidence where available. Current work provides evidence about assistance and structural proposal tasks.

**Evolution and reception:** Assistance remains assumption-sensitive; autonomous architecting under changing requirements remains an examined unresolved candidate. **Limit:** Small educational cases, one-run configurations and benchmark metrics do not establish dependable open-ended architecting. [ESA-S059, ESA-S062, ESA-S063.]

### ESA-G22 — Driver-based recursive design and interleaved design/evaluation

A list of desirable qualities does not choose responsibilities, interfaces or useful decompositions. Choose drivers, select design concepts, decompose, allocate responsibilities and evaluate; iterate or recurse where uncertainty requires it. Makes architectural synthesis operative while allowing analysis, synthesis and evaluation to interleave.

**Evolution and reception:** Small work can use direct alternatives and checks; the fuller method is selected when driver conflicts or scope justify it. **Limit:** Method-author synthesis and guidance are not independent comparative proof; recursion can become premature design expansion. [ESA-S024, ESA-S025, ESA-S016.]

### ESA-G23 — IEEE 1471 architecture-description recommendation

Architecture descriptions need a common conceptual vocabulary and concern/viewpoint organisation. Standardise recommendations for describing software-intensive-system architecture. A description standard, not a quality certification.

**Evolution and reception:** Replaced by ISO/IEC/IEEE 42010:2011 within the architecture-description scope. **Limit:** Only official abstract and later history were inspected; no normative-clause claim is made. [ESA-S065, ESA-S013.]

### ESA-G24 — ISO/IEC/IEEE 42010 first edition

Continue harmonised architecture-description concepts. Specify an architecture-description framework rather than choosing a design for the user. An identifiable edition must be distinguished from its predecessors and successor.

**Evolution and reception:** The 2022 second edition is a distinct inspected bibliographic and introductory object. **Limit:** Official abstract/metadata only; no clause-level comparison or compliance checklist is derived. [ESA-S012, ESA-S013.]

### ESA-G25 — ISO/IEC/IEEE 42010 second edition

Update the architecture-description conceptual framework. Relate entities, architecture, descriptions and stakeholder concerns within the standard’s stated scope. Maintains the distinction between architecture and architecture description.

**Evolution and reception:** Current standardisation evidence establishes description scope, not adoption or causal engineering superiority. **Limit:** Only official abstract and introductory preview were inspected; full normative clauses are an explicit access limit. [ESA-S011.]

### Material genealogical relationships

**ESA-GE01 · ESA-G01 → ESA-G02 · ONLY_ANALOGOUS.** Both use abstraction, but processing hierarchy and hiding likely changes are different mechanisms; direct transmission is not established by this inspection. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S005, ESA-S001, ESA-S006.]

**ESA-GE02 · ESA-G02 → ESA-G12 · SHARED_ANCESTRY.** Program-family architecture and modular design share responsibility/commonality concerns; the collection documents later intersections, not a universal line of descent. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S001, ESA-S006, ESA-S066.]

**ESA-GE03 · ESA-G03 → ESA-G08 · CONVERGENT_DEVELOPMENT.** Rationalised design explanation and decision records address lost design knowledge through different forms; no exclusive direct derivation is claimed. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S009, ESA-S027, ESA-S029.]

**ESA-GE04 · ESA-G04 → ESA-G05 · EXPLICIT_EXTENSION.** Kruchten explicitly relates the 4+1 account to the elements/form/rationale architecture account and supplies multiple views. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S002, ESA-S003.]

**ESA-GE05 · ESA-G04 → ESA-G06 · EXPLICIT_EXTENSION.** Architectural language and connector work supplies semantics and analysis for component-and-connector organisations. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S004, ESA-S014, ESA-S015.]

**ESA-GE06 · ESA-G12 → ESA-G06 · CRITICISM_AND_RESPONSE.** Mismatch exposes assumptions that formal interaction reasoning can address in a bounded model. This is a source-grounded problem/response relationship, not a claim that the entire Wright design was caused by the Aesop experience. [ESA-S026, ESA-S015.]

**ESA-GE07 · ESA-G04 → ESA-G07 · CONVERGENT_DEVELOPMENT.** Structural accounts and scenario evaluations develop complementary architecture questions; a sole founding lineage is not inferred. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S002, ESA-S019, ESA-S020.]

**ESA-GE08 · ESA-G07 → ESA-G22 · DOCUMENTED_INFLUENCE.** ADD explicitly organises design around architectural drivers and quality reasoning; the general model includes evaluation in design. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S016, ESA-S024, ESA-S025.]

**ESA-GE09 · ESA-G22 → ESA-G07 · HYBRIDISATION.** The general design model interleaves architectural analysis, synthesis and evaluation rather than insisting on a once-only sequence. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S025.]

**ESA-GE10 · ESA-G05 → ESA-G23 · SHARED_ANCESTRY.** View/concern practices and architecture-description standardisation share an explicit descriptive problem; exclusive derivation from 4+1 is not asserted. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S003, ESA-S065, ESA-S013.]

**ESA-GE11 · ESA-G23 → ESA-G24 · REPLACEMENT_WITHIN_A_SCOPE.** The first 42010 edition supersedes IEEE 1471 for architecture description. Bibliographic/scope relation only; unread clauses cannot establish which normative duties changed. [ESA-S065, ESA-S012, ESA-S013.]

**ESA-GE12 · ESA-G24 → ESA-G25 · EXPLICIT_EXTENSION.** The 2022 second edition succeeds the 2011 edition. Edition history and introductory scope only, not a clause-by-clause assessment. [ESA-S011, ESA-S012, ESA-S013.]

**ESA-GE13 · ESA-G05 → ESA-G09 · CONVERGENT_DEVELOPMENT.** Multiple descriptions and model/source comparison address different sides of correspondence. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S003, ESA-S045.]

**ESA-GE14 · ESA-G10 → ESA-G16 · DOCUMENTED_IMPORT.** Microservice discussion explicitly connects service ownership and team organisation; empirical coordination findings remain conditional. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S030, ESA-S036, ESA-S060.]

**ESA-GE15 · ESA-G13 → ESA-G16 · DOCUMENTED_IMPORT.** Microservice guidance explicitly uses bounded-context ideas from domain-driven design. The inspected 2015 author reference explains the concept; it is not asserted to have caused a 2014 essay. The original 2003 book was not read. [ESA-S033, ESA-S036.]

**ESA-GE16 · ESA-G15 → ESA-G16 · UNRESOLVED_RELATIONSHIP.** Microservices are often related to service orientation, but the examined accounts do not settle a single uncontested derivation or equivalence. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S035, ESA-S036.]

**ESA-GE17 · ESA-G14 → ESA-G15 · ONLY_ANALOGOUS.** Both concern distributed interactions; REST’s specific style constraints are not the SOA reference model. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S034, ESA-S035.]

**ESA-GE18 · ESA-G02 → ESA-G17 · DOMAIN_TRANSLATION.** Change-oriented structures contribute to later migration/debt decisions, while debt measures and transition mechanisms add different obligations. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S006, ESA-S040, ESA-S049, ESA-S050.]

**ESA-GE19 · ESA-G09 → ESA-G17 · HYBRIDISATION.** Continuous architectural checks can carry mapped conformance conditions, provided the baseline and metrics are revisable. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S045, ESA-S043, ESA-S044.]

**ESA-GE20 · ESA-G11 → ESA-G17 · CONVERGENT_DEVELOPMENT.** Runtime adaptation and evolutionary-architecture checks both revisit architecture, but one changes runtime state and the other need not do so. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S051, ESA-S052, ESA-S043.]

**ESA-GE21 · ESA-G17 → ESA-G18 · DOCUMENTED_IMPORT.** The ML engineering account explicitly applies technical-debt reasoning to data, feedback and system dependencies. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S049, ESA-S056.]

**ESA-GE22 · ESA-G19 → ESA-G20 · DOMAIN_TRANSLATION.** Serverless resource management supplies a concrete setting for energy/latency architectural trade-offs, not a universal sustainability result. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S057, ESA-S061, ESA-S058.]

**ESA-GE23 · ESA-G07 → ESA-G21 · DOMAIN_TRANSLATION.** A 2026 study applies LLM assistance to ATAM-related work; the original method’s evidence limits remain and new validation limits appear. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S020, ESA-S059.]

**ESA-GE24 · ESA-G16 → ESA-G21 · DOMAIN_TRANSLATION.** Recent generated pattern/decomposition studies examine modern architecture tasks but measure narrower outcomes than operating independence. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S036, ESA-S062, ESA-S063.]

**ESA-GE25 · ESA-G11 → ESA-G21 · ONLY_ANALOGOUS.** A bounded architectural controller and an open-ended architecting assistant both decide over models, but their guarantees, observations and authority differ. The edge supports only the stated relationship; similarity does not prove exclusive ancestry. [ESA-S053, ESA-S054, ESA-S062.]


## EVOLVED_SOFTWARE_ARCHITECTURE_SCOPE_AND_CARICATURES

The object is consequential software organisation: responsibilities, relationships, interaction, decision assumptions and quality consequences at a declared scope. Architecture description, detailed design, organisational arrangements and systems-level constraints can matter without becoming identical objects. The study examined all nine mandated families; its completeness is relative to those questions and the registered population, not all software engineering.

The caricatures rejected here are consequential: architecture is not all important work, all centralised approval, all diagrams, all up-front design, all distribution, or the absence of emergence. Equally, criticism of excess documentation does not erase interface assumptions, quality trade-offs or dependencies. The no-intervention path must preserve the real property, not merely remove its most visible artefact. The low-machinery configuration is a positive coherent option, not a deficient version of the fullest method.

[ESA-S001; ESA-S003; ESA-S010; ESA-S025; ESA-S037; ESA-S041–042. The precise support is in their source-table locators.]

## EVOLVED_SOFTWARE_ARCHITECTURE_PROPERTY_LEDGER

**Complete denominator: 68 candidates; 68 examined.** The stable ESA-057 remains counted after its separation into ESA-065 and ESA-066. IDs are not reordered or removed to improve a retention rate. Full records, evidence partitions and all domain profiles are in [EVOLVED_SOFTWARE_ARCHITECTURE_PROPERTY_LEDGER.json](EVOLVED_SOFTWARE_ARCHITECTURE_PROPERTY_LEDGER.json), under `properties` by `PROPERTY_ID`.

| Disposition | Count |
|---|---:|
| `ASSUMPTION_SENSITIVE` | 8 |
| `CEREMONY_NOT_GENERAL_PROPERTY` | 2 |
| `CONTEXT_DEPENDENT` | 13 |
| `DOMAIN_SPECIFIC` | 8 |
| `NO_GENERAL_PROPERTY` | 1 |
| `REJECTED_OR_DISFAVOURED` | 8 |
| `RETAINED_IN_EVOLVED_FORM` | 15 |
| `STRONGLY_RETAINED` | 9 |
| `SUPERSEDED_BY_STRONGER_FORM` | 1 |
| `UNRESOLVED` | 1 |
| `USEFUL_BUT_EASILY_GAMED` | 2 |

| ID | Candidate | Primary disposition |
|---|---|---|
| ESA-001 | Consequence-bound architectural significance | `RETAINED_IN_EVOLVED_FORM` |
| ESA-002 | Stakeholder concerns connected to decisions | `STRONGLY_RETAINED` |
| ESA-003 | Architecture, description and belief distinguished | `STRONGLY_RETAINED` |
| ESA-004 | Conceptual integrity without mandatory centralisation | `CONTEXT_DEPENDENT` |
| ESA-005 | Accountable authority for consequential trade-offs | `RETAINED_IN_EVOLVED_FORM` |
| ESA-006 | Architecture as an unrestricted important-decisions label | `NO_GENERAL_PROPERTY` |
| ESA-007 | Change-oriented information hiding | `STRONGLY_RETAINED` |
| ESA-008 | Semantic interface assumptions made testable | `STRONGLY_RETAINED` |
| ESA-009 | Connectors as explicit interaction mechanisms | `RETAINED_IN_EVOLVED_FORM` |
| ESA-010 | Dependency kinds and uses relations distinguished | `STRONGLY_RETAINED` |
| ESA-011 | Demonstrated containment rather than nominal isolation | `ASSUMPTION_SENSITIVE` |
| ESA-012 | Coordination-aware boundary placement | `CONTEXT_DEPENDENT` |
| ESA-013 | Commonality and variability within an architectural family | `DOMAIN_SPECIFIC` |
| ESA-014 | Measurable quality-attribute scenarios | `STRONGLY_RETAINED` |
| ESA-015 | Scenario population and selection validity | `RETAINED_IN_EVOLVED_FORM` |
| ESA-016 | Tactics tied to explanatory quality models | `ASSUMPTION_SENSITIVE` |
| ESA-017 | Explicit interacting-quality trade-offs and constraints | `STRONGLY_RETAINED` |
| ESA-018 | Representative workload and failure observations | `STRONGLY_RETAINED` |
| ESA-019 | Independent maximisation of every quality | `REJECTED_OR_DISFAVOURED` |
| ESA-020 | Concern-selected views and viewpoints | `RETAINED_IN_EVOLVED_FORM` |
| ESA-021 | Correspondence between views and realisation | `STRONGLY_RETAINED` |
| ESA-022 | Formal architectural descriptions with bounded guarantees | `DOMAIN_SPECIFIC` |
| ESA-023 | Mandatory complete 4+1 documentation | `CEREMONY_NOT_GENERAL_PROPERTY` |
| ESA-024 | Triangulated architecture reconstruction with uncertainty | `RETAINED_IN_EVOLVED_FORM` |
| ESA-025 | Styles and patterns as conditional mechanisms | `CONTEXT_DEPENDENT` |
| ESA-026 | Comparison with feasible alternatives and no change | `RETAINED_IN_EVOLVED_FORM` |
| ESA-027 | Change-scenario architectural evaluation | `CONTEXT_DEPENDENT` |
| ESA-028 | Multi-quality risk and sensitivity evaluation | `CONTEXT_DEPENDENT` |
| ESA-029 | Economic evaluation with uncertainty and dependency | `ASSUMPTION_SENSITIVE` |
| ESA-030 | Targeted prototypes and calibrated analytic models | `CONTEXT_DEPENDENT` |
| ESA-031 | Review success as a guarantee of operating quality | `REJECTED_OR_DISFAVOURED` |
| ESA-032 | Recoverable decision rationale for later consumers | `RETAINED_IN_EVOLVED_FORM` |
| ESA-033 | Decision ageing, supersession and reopening | `RETAINED_IN_EVOLVED_FORM` |
| ESA-034 | Socio-technical coordination of consequential dependencies | `ASSUMPTION_SENSITIVE` |
| ESA-035 | Distributed decisions constrained by shared consequences | `CONTEXT_DEPENDENT` |
| ESA-036 | Deterministic organisational mirroring | `REJECTED_OR_DISFAVOURED` |
| ESA-037 | Documentation quantity as architectural evidence | `CEREMONY_NOT_GENERAL_PROPERTY` |
| ESA-038 | Conformance to a justified, mapped baseline | `RETAINED_IN_EVOLVED_FORM` |
| ESA-039 | Adjudication of drift and authorised improvement | `RETAINED_IN_EVOLVED_FORM` |
| ESA-040 | Architectural smells as defeasible risk indicators | `USEFUL_BUT_EASILY_GAMED` |
| ESA-041 | Recovered structure as a substitute for intended rationale | `REJECTED_OR_DISFAVOURED` |
| ESA-042 | Zero deviations from a historical architecture | `REJECTED_OR_DISFAVOURED` |
| ESA-043 | Architecture debt distinguished from mere imperfection | `RETAINED_IN_EVOLVED_FORM` |
| ESA-044 | Incremental migration with coexistence and compatibility | `CONTEXT_DEPENDENT` |
| ESA-045 | Revisable fitness functions and continuous evaluation | `USEFUL_BUT_EASILY_GAMED` |
| ESA-046 | Architecture-based observation and runtime adaptation | `DOMAIN_SPECIFIC` |
| ESA-047 | Constrained adaptation and post-change assurance | `ASSUMPTION_SENSITIVE` |
| ESA-048 | Self-authorisation through local metric improvement | `REJECTED_OR_DISFAVOURED` |
| ESA-049 | Investment in future flexibility proportionate to change hypotheses | `ASSUMPTION_SENSITIVE` |
| ESA-050 | Microservices conditional on deployment and operating needs | `CONTEXT_DEPENDENT` |
| ESA-051 | Modular monoliths and justified consolidation | `CONTEXT_DEPENDENT` |
| ESA-052 | Serverless architecture with provider and workload boundaries | `DOMAIN_SPECIFIC` |
| ESA-053 | Architecture for learned components and data dependencies | `DOMAIN_SPECIFIC` |
| ESA-054 | Evidence-checked AI assistance for architectural work | `ASSUMPTION_SENSITIVE` |
| ESA-055 | Sustainability as an explicitly bounded architectural concern | `CONTEXT_DEPENDENT` |
| ESA-056 | Proportional governance and retirement of controls | `RETAINED_IN_EVOLVED_FORM` |
| ESA-057 | Service and REST constraints distinguished from labels | `SUPERSEDED_BY_STRONGER_FORM` |
| ESA-058 | Emergence as a reason to omit architectural reasoning | `REJECTED_OR_DISFAVOURED` |
| ESA-059 | Description-standard conformance as quality certification | `REJECTED_OR_DISFAVOURED` |
| ESA-060 | Autonomous architecting under open-ended requirements | `UNRESOLVED` |
| ESA-061 | Bounded semantic models and explicit translation | `CONTEXT_DEPENDENT` |
| ESA-062 | Usability concerns allowed to reshape architecture | `RETAINED_IN_EVOLVED_FORM` |
| ESA-063 | Safe change of adaptation policies and assurance assumptions | `ASSUMPTION_SENSITIVE` |
| ESA-064 | Rationalised design explanation distinguished from actual history | `RETAINED_IN_EVOLVED_FORM` |
| ESA-065 | REST interaction constraints | `DOMAIN_SPECIFIC` |
| ESA-066 | Service visibility, interaction and real-world-effect contracts | `DOMAIN_SPECIFIC` |
| ESA-067 | Driver-based recursive architectural design | `CONTEXT_DEPENDENT` |
| ESA-068 | Connector compatibility under well-formedness constraints | `DOMAIN_SPECIFIC` |

A rejected claim can motivate a retained corrective mechanism; it does not become a second mandatory control. Domain-specific and assumption-sensitive candidates must pass their own triggers before any later target inquiry treats them as applicable.

## EVOLVED_SOFTWARE_ARCHITECTURE_DOMAIN_MODELS

These eight prose models define objects, observations and operations. They are analytical reconstructions grounded in the cited work, not new mathematical formalisms. The ten-field profile in every property record specialises them to that candidate.

### ESA-DM01 — Architectural significance and concerns

**Objects/state:** A software system, its environment, stakeholder concerns, candidate choices, affected obligations and the evidence believed to support them.

A choice is significant relative to the reach of its consequences, not a fixed file size or job role. Concerns attach to choices through scenarios/constraints. An authorised decision and an implemented result remain separate state changes. Users, maintainers, operators and sponsors supply concerns; designers explain consequences; actual authorised participants accept trade-offs; implementers change real artefacts.

**Evidence:** Trace a claimed concern through a selected choice to an observation. Agreement shows coordination, not successful operation. **Smallest form:** A short conversation, a few explicit constraints and a check of the real effect can be coherent for one team.

Analytical: choosing a colour token is normally local, but a colour-encoding decision becomes architectural when every alarm channel and accessibility commitment depends on it.

Properties: ESA-001, ESA-002, ESA-003, ESA-004, ESA-005, ESA-006, ESA-056. Sources: ESA-S002, ESA-S010, ESA-S011, ESA-S017, ESA-S020, ESA-S035.

### ESA-DM02 — Decomposition and interface contracts

**Objects/state:** Responsibilities, hidden decisions, model meanings, interfaces, connectors, shared resources and typed dependencies.

Information hiding partitions knowledge; connector semantics govern interaction; containment constrains propagation. A module boundary, domain context, deployment boundary and team boundary are related but non-identical partitions. Producers and consumers negotiate meaningful obligations, implement or adapt interfaces, and exercise change/failure cases across them.

**Evidence:** An import graph establishes only its extracted relation. Correctness dependence, shared state and external effects require additional evidence. Wright provides a conditional formal branch, not automatic semantic closure. **Smallest form:** A direct local interface with explicit meaning and a few integration cases; no network boundary is required.

Analytical: two services with separate repositories share a global database trigger; their apparent isolation fails when one change alters the other’s invariant.

Properties: ESA-007, ESA-008, ESA-009, ESA-010, ESA-011, ESA-012, ESA-013, ESA-025, ESA-061, ESA-065, ESA-066, ESA-068. Sources: ESA-S001, ESA-S006, ESA-S015, ESA-S026, ESA-S033, ESA-S034, ESA-S035.

### ESA-DM03 — Quality-attribute trade-offs

**Objects/state:** Concern-specific scenarios, response measures, constraints, preferences, mechanisms and environmental assumptions.

A tactic changes a quality model parameter, not an abstract quality in isolation. The system response depends on interaction with other tactics and workload. Hard limits restrict acceptable options before preference comparison. Stakeholders define acceptable responses; designers propose interventions; evaluators construct models/tests; operators supply observations.

**Evidence:** Use workload, fault and population scope and a declared accounting boundary. The same functional answer can be unacceptable because of latency, information disclosure or resource use. **Smallest form:** One concrete scenario and competing-cost check are sufficient for a narrow reversible decision.

Published: EcoFaaS’s chosen energy/tail-latency benefits coexist with worse mean latency versus its full-frequency baseline; its energy boundary is package/DRAM, not total carbon.

Properties: ESA-014, ESA-015, ESA-016, ESA-017, ESA-018, ESA-019, ESA-055, ESA-062. Sources: ESA-S016, ESA-S017, ESA-S018, ESA-S020, ESA-S022, ESA-S061.

### ESA-DM04 — Views and correspondence

**Objects/state:** Views of structure, interaction, deployment/development organisation, their viewpoint rules and mappings to realised artefacts.

A view selects facts for a concern. Correspondences connect elements/relations across views and to implementation; consistency among views is weaker than truth about implementation. Recovery produces hypotheses with provenance. Different consumers ask different questions. Authors map shared elements and explain differences; analysts inspect source, configuration or traces to check relevant claims.

**Evidence:** Formal semantics can establish a model property; relation extraction and implementation refinement have separate obligations. A sampled trace cannot certify every possible runtime path. **Smallest form:** Use the least number of views that answer the concern, with explicit labels and a manual correspondence check.

Analytical: a logical service view is consistent with a deployment drawing but both omit a production sidecar that changes network and failure behaviour.

Properties: ESA-003, ESA-020, ESA-021, ESA-022, ESA-023, ESA-024, ESA-041, ESA-059. Sources: ESA-S003, ESA-S011, ESA-S014, ESA-S015, ESA-S045.

### ESA-DM05 — Alternative evaluation

**Objects/state:** Feasible alternatives including no change, architectural drivers, scenarios, assumptions, risk/sensitivity findings and costs.

SAAM emphasises changes; ATAM exposes multi-quality risks; CBAM examines utility/cost under assumptions; prototypes and formal models supply different evidence. They can substitute or complement, not automatically all execute. Analysis, design synthesis and evaluation interleave: a risk may change requirements, an experiment may reveal a new option, and a local design may proceed while another uncertainty is studied.

**Evidence:** Method outputs are not outcomes. Compare alternatives under equivalent conditions and preserve exclusions, weak baselines and uncertainty. **Smallest form:** A focused alternative-and-risk conversation with one discriminating experiment can be enough.

Analytical: a successful review is followed by a workload dominated by an omitted write path; the previous non-risk is reopened, not defended by the review’s approval.

Properties: ESA-015, ESA-017, ESA-026, ESA-027, ESA-028, ESA-029, ESA-030, ESA-031, ESA-067. Sources: ESA-S019, ESA-S020, ESA-S021, ESA-S022, ESA-S023, ESA-S024, ESA-S025.

### ESA-DM06 — Decision knowledge and coordination

**Objects/state:** Current decisions, rationale, assumptions, status/history and the people whose work or commitments depend on them.

Decision dependencies make knowledge transfer useful. Communication requirements follow relevant technical/work coupling, but neither a record nor an organisation chart mechanically produces coherent design. Teams exchange decisions and exceptions; later actors retrieve rationale; authorised participants revise it when assumptions fail. Reconstructed explanation remains separate from documentary history.

**Evidence:** Check a real later question and a real cross-team dependency. Surveys and observational congruence are not universal causal evidence. **Smallest form:** One shared explanation and a short retained note for a non-obvious decision; no board or permanent extra role is inherent.

Analytical: a successor can explain why an interface was chosen but discovers a critical workload assumption no longer holds; the old record guides revision rather than preventing it.

Properties: ESA-004, ESA-005, ESA-032, ESA-033, ESA-034, ESA-035, ESA-036, ESA-037, ESA-064. Sources: ESA-S009, ESA-S010, ESA-S027, ESA-S028, ESA-S029, ESA-S030, ESA-S031, ESA-S032.

### ESA-DM07 — Conformance and reconstruction

**Objects/state:** Baseline constraints, extracted/observed relations, mappings, deviations, evidence and adjudicated dispositions.

A conformance result relates one mapping and dependency kind to one baseline. A smell is a candidate risk signal. The target of correction may be code, configuration, description, rule or an unsupported inference. Analysts report findings; maintainers explain context; authorised reviewers evaluate consequences and change the right artefact. Rechecking establishes whether the actual disposition took effect.

**Evidence:** Positive and negative cases expose missed edges and false alarms. Harm requires a current invariant/quality/burden argument, not mere divergence. **Smallest form:** A focused dependency assertion or manual relation comparison with a retained reason for the rule.

Analytical: an approved caching improvement violates an old layering rule; if current freshness and security constraints remain satisfied, revise the rule rather than revert for a green count.

Properties: ESA-010, ESA-021, ESA-024, ESA-038, ESA-039, ESA-040, ESA-041, ESA-042, ESA-045. Sources: ESA-S002, ESA-S045, ESA-S046, ESA-S047, ESA-S048.

### ESA-DM08 — Architecture evolution and revision

**Objects/state:** Current architecture, plausible future variants, transition/coexistence states, debt claims, change evidence and optional runtime controllers.

Change may alter structure, knowledge, baseline or policy. A transition must preserve selected continuity obligations; new evidence can reopen earlier decisions. Runtime adaptation adds a model/action feedback loop whose own assumptions need review. Engineers implement and migrate; operators observe actual effects; delegated controllers may execute specified actions. External stakeholders or commitments constrain what those actors may optimise.

**Evidence:** Tests must cover transition states and post-change consequences. The controller cannot validate itself merely by increasing its score or changing its objective. **Smallest form:** Direct reviewed change followed by a relevant observation; richer migration/automation only where continuity or operating variability warrants it.

Analytical: autoscaling reduces latency but exceeds an external resource cap; the transition is not accepted as overall success even though its local metric improved.

Properties: ESA-013, ESA-033, ESA-043, ESA-044, ESA-045, ESA-046, ESA-047, ESA-048, ESA-049, ESA-050, ESA-051, ESA-052, ESA-053, ESA-054, ESA-055, ESA-056, ESA-060, ESA-063. Sources: ESA-S020, ESA-S040, ESA-S049, ESA-S050, ESA-S051, ESA-S052, ESA-S053, ESA-S054, ESA-S055, ESA-S056, ESA-S061.


## EVOLVED_SOFTWARE_ARCHITECTURE_CEREMONY_STRIPPING_LEDGER

Simplification is selected by function, not hostility to documents or meetings. The eighteen entries jointly cover all 55 crosswalk-worthy candidates; every individual property also records its cheap path and reopening condition. No entry requires a separate owner, tool or artefact.

### ESA-CS01 — Architecture board, charter or grand vision document

**Protected function:** Consequential concerns, coherent meanings and legitimate decisions must not disappear behind rank or rhetoric. **Consumer:** People making and bearing the trade-off.

**Prerequisites:** A real cross-boundary consequence and actual authority. **Minimal alternative:** Direct discussion, a few constraints and a traceable choice using existing roles.

**Fuller-form trigger:** Conflicting commitments, turnover, many independent teams or a consequential unresolved decision. **Cost of simplification:** A short form may lose durable context or omit less-visible stakeholders.

**Omission/retirement:** No material unresolved consequence, existing communication is adequate, or the extra board merely duplicates authority. Properties: ESA-001, ESA-002, ESA-003, ESA-004, ESA-005, ESA-035, ESA-056. Source support resolves through those complete property records.

### ESA-CS02 — Component diagrams, abstraction frameworks and boundary workshops

**Protected function:** Hide the right decisions and preserve interface/invariant semantics; arrows and process boundaries do not demonstrate independence. **Consumer:** Both sides of an interface and maintainers making changes.

**Prerequisites:** Plausible change/fault hypotheses and knowledge of shared state. **Minimal alternative:** A local module, direct call, explicit example and focused integration/change test.

**Fuller-form trigger:** Independent deployment, multiple semantic domains, fault containment or repeated costly propagation. **Cost of simplification:** Less explicit modelling can conceal non-local assumptions as teams or interactions multiply.

**Omission/retirement:** Retire boundaries that add translation/coordination without protecting a relevant obligation. Properties: ESA-007, ESA-008, ESA-009, ESA-010, ESA-011, ESA-012, ESA-025, ESA-061. Source support resolves through those complete property records.

### ESA-CS03 — Platform reuse framework and exhaustive variability catalogue

**Protected function:** Commonality and legitimate variations must be clear without buying every imaginable future. **Consumer:** Family designers and actual variant consumers.

**Prerequisites:** Credible family scope and future-change evidence. **Minimal alternative:** One straightforward product or a small explicit variation point.

**Fuller-form trigger:** Several required variants and consequential shared-asset or configuration interactions. **Cost of simplification:** A cheap form may duplicate work or make later shared-asset changes harder.

**Omission/retirement:** No credible variant demand, or maintaining flexibility costs more than observed/expected benefit. Properties: ESA-013, ESA-049. Source support resolves through those complete property records.

### ESA-CS04 — Quality workshop, utility tree and tactics catalogue

**Protected function:** Consequential scenarios and trade-offs need measurable responses and representative conditions. **Consumer:** Users/operators/designers/evaluators of affected qualities.

**Prerequisites:** Access to actual workload/fault assumptions and representation of affected interests. **Minimal alternative:** A few concrete examples, hard limits and an observed/prototyped response.

**Fuller-form trigger:** Conflicting qualities, rare consequential states, broad stakeholder disagreement or poorly understood mechanisms. **Cost of simplification:** Some scenario diversity or causal explanation may be lost; retain rare hard constraints even when votes are few.

**Omission/retirement:** No consequential uncertainty remains or the catalogue/workshop produces unused labels instead of decisions. Properties: ESA-014, ESA-015, ESA-016, ESA-017, ESA-018, ESA-062. Source support resolves through those complete property records.

### ESA-CS05 — 4+1 documents and view repositories

**Protected function:** Views must answer concerns and correspond to each other and realisation. **Consumer:** The person deciding from a particular view.

**Prerequisites:** Declared notation/relations, observation scope and update responsibility in existing work. **Minimal alternative:** A single adequate sketch plus targeted code/configuration/execution inspection.

**Fuller-form trigger:** Multiple concerns need genuinely different perspectives or changing systems make omissions costly. **Cost of simplification:** Implicit views may not expose contradictions to new participants.

**Omission/retirement:** Omit or retire a view with no consumer; never preserve a stale view merely to complete a set. Properties: ESA-020, ESA-021, ESA-024. Source support resolves through those complete property records.

### ESA-CS06 — ADL, connector specification and model-checking run

**Protected function:** Check precisely stated interaction properties under valid model and well-formedness assumptions. **Consumer:** Designers/verifiers deciding whether composition is safe in the examined sense.

**Prerequisites:** Faithful model, applicable theorem/check, trained users and implementation correspondence. **Minimal alternative:** A simpler contract/review or focused test when its residual risk is acceptable.

**Fuller-form trigger:** High-consequence interaction uncertainty or repeatable formal checks justify modelling cost. **Cost of simplification:** The cheaper alternative usually loses exhaustive coverage within the formal model.

**Omission/retirement:** No relevant analysed property, stale semantics, missing implementation mapping or cost exceeding the supported assurance benefit. Properties: ESA-022, ESA-068. Source support resolves through those complete property records.

### ESA-CS07 — ATAM/SAAM event, scorecard and economic spreadsheet

**Protected function:** Compare feasible alternatives and expose risks without claiming a certificate. **Consumer:** Those choosing design trade-offs and accepting uncertainty.

**Prerequisites:** Real alternatives, adequate scenarios and available expertise. **Minimal alternative:** Focused review or prototype of the decisive uncertainty, including no change.

**Fuller-form trigger:** Many interacting qualities, large consequences or uncertain investments demand broader structured evaluation. **Cost of simplification:** A lightweight review may miss interactions or make assumptions harder to challenge.

**Omission/retirement:** The full method adds no decision value, or assumptions have changed so much that repeating a scorecard would mislead. Properties: ESA-026, ESA-027, ESA-028, ESA-029, ESA-030. Source support resolves through those complete property records.

### ESA-CS08 — ADR template, rationale database and design history

**Protected function:** Later actors need recoverable reasons and status, not fictitious linear history. **Consumer:** Decision inheritors, reviewers and maintainers.

**Prerequisites:** A future consumer and access to the actual context/options/consequences. **Minimal alternative:** A concise note attached to existing work or direct stable shared understanding.

**Fuller-form trigger:** Turnover, distributed decisions, costly reversals or repeatedly rediscovered rationale. **Cost of simplification:** Very short notes can omit rejected alternatives or evidence needed to reopen.

**Omission/retirement:** Retire obsolete prescriptions but preserve supersession where history matters; omit records for local reversible trivia. Properties: ESA-032, ESA-033, ESA-064. Source support resolves through those complete property records.

### ESA-CS09 — Org-chart redesign and dependency/communication dashboard

**Protected function:** Coordinate consequential dependencies without treating correlations as an organisational law. **Consumer:** People doing interdependent work and those authorised to change coordination.

**Prerequisites:** Appropriate dependency definitions and sufficiently complete communication observations. **Minimal alternative:** A direct cross-team conversation or task-specific liaison using existing roles.

**Fuller-form trigger:** Persistent coordination delays or mismatches with material design consequences. **Cost of simplification:** Local remedies may not expose repeated systemic coordination costs.

**Omission/retirement:** The dashboard’s proxies no longer reflect work or reorganisation costs dominate the demonstrated problem. Properties: ESA-034. Source support resolves through those complete property records.

### ESA-CS10 — Architecture test gates, smell scores and deviation backlogs

**Protected function:** A current justified baseline and informative findings should guide improvement, not preserve obsolete rules. **Consumer:** Engineers who can interpret a finding and choose repair, exception or baseline revision.

**Prerequisites:** Mappings, evidence of affected concern and an authorised rule revision path. **Minimal alternative:** Inspect the specific dependency/change and record a reasoned exception or fix.

**Fuller-form trigger:** Repeated harmful classes or broad scope make reliable automated checks economical. **Cost of simplification:** Manual checking may miss regressions and offer less continuous coverage.

**Omission/retirement:** Retire a test when its protected concern disappears, proxy fails or the baseline is superseded; a zero score is not a goal by itself. Properties: ESA-038, ESA-039, ESA-040, ESA-045. Source support resolves through those complete property records.

### ESA-CS11 — Debt register, migration programme and future-proofing roadmap

**Protected function:** Explain actual or hypothesised cost and preserve intermediate operating obligations. **Consumer:** Those prioritising change and operating during coexistence.

**Prerequisites:** A cost/impact hypothesis, compatibility constraints and feasible transition slices. **Minimal alternative:** Leave harmless imperfection alone or perform a small direct improvement.

**Fuller-form trigger:** Observed recurring cost, required incompatible change or high-risk replacement needs staged work. **Cost of simplification:** A simple form can understate coexistence cost or future interest; a large programme can create them.

**Omission/retirement:** Retire debt items disproved by observed changes and migration scaffolding after compatibility consumers disappear. Properties: ESA-043, ESA-044. Source support resolves through those complete property records.

### ESA-CS12 — Runtime architecture model and self-adaptation controller

**Protected function:** Observed state, allowable action and post-change constraints must remain aligned. **Consumer:** Operators and bounded control mechanisms acting under real authority.

**Prerequisites:** Trustworthy probes, model mapping, actuator semantics, policy constraints and recovery paths. **Minimal alternative:** Manual operation or a simpler fixed controller where change is slow or uncertainty manageable.

**Fuller-form trigger:** Rapid recurring adaptation needs with tractable policy/observation boundaries. **Cost of simplification:** Manual control can miss timing requirements; a simplified controller may cover fewer states.

**Omission/retirement:** Disable or fall back when state correspondence, policy validity or actuator effects cannot be established; retire needless autonomy. Properties: ESA-046, ESA-047, ESA-063. Source support resolves through those complete property records.

### ESA-CS13 — Microservice platform and monolith purity campaigns

**Protected function:** Deployment architecture should match actual change/operating needs and costs. **Consumer:** Teams deploying, operating and changing the software.

**Prerequisites:** Evidence about scaling, failure, releases, ownership and shared data. **Minimal alternative:** A modular single deployment or selective consolidation.

**Fuller-form trigger:** Demonstrated independent change/scaling or failure requirements justify distribution. **Cost of simplification:** Consolidation can lose real deployment/failure independence; splitting can add overhead without obtaining it.

**Omission/retirement:** Remove boundaries with no protected independence; do not consolidate a boundary that still enforces a required separation. Properties: ESA-050, ESA-051. Source support resolves through those complete property records.

### ESA-CS14 — Serverless-first platform mandate

**Protected function:** Provider execution/resource assumptions must support the workload and constraints. **Consumer:** Implementers/operators and budget/quality decision makers.

**Prerequisites:** Version-specific provider evidence, invocation/state model and workload measurements. **Minimal alternative:** An ordinary process/service when it meets the same needs with less uncertainty.

**Fuller-form trigger:** Elastic invocation or administrative requirements outweigh platform-specific costs and restrictions. **Cost of simplification:** A simpler platform can lose managed elasticity or administrative benefits.

**Omission/retirement:** Reconsider when workload, quotas, latency, state or exit costs invalidate the premise; no current provider claim is frozen here. Properties: ESA-052. Source support resolves through those complete property records.

### ESA-CS15 — ML architecture map and AI architect assistant

**Protected function:** Data/feedback coupling and generated architectural claims require independently grounded evidence. **Consumer:** Engineers deciding and operating learned-system changes.

**Prerequisites:** Known data/configuration consumers, representative evaluation and human accountability for generated work. **Minimal alternative:** Direct code/data inspection or ordinary unaided reasoning on the small consequential question.

**Fuller-form trigger:** Complex data interactions or costly proposal analysis justify additional assistance and validation. **Cost of simplification:** Less modelling can miss feedback; less automation may slow exploration but can avoid hallucinated certainty.

**Omission/retirement:** Discard unsupported generated claims; retire tools whose verification cost exceeds their demonstrated assistance value. Properties: ESA-053, ESA-054. Source support resolves through those complete property records.

### ESA-CS16 — Green architecture badge and energy dashboard

**Protected function:** Measured energy/resource effects must use a declared boundary and respect other constraints. **Consumer:** People choosing workload/platform/design changes and affected quality consumers.

**Prerequisites:** Workload, measurement boundary, uncertainty and non-negotiable response limits. **Minimal alternative:** A focused measurement of the actual dominant resource question.

**Fuller-form trigger:** Material energy/resource consequences or competing design options justify broader lifecycle investigation. **Cost of simplification:** Narrow measurement can miss embodied/operational effects elsewhere; broader estimates may increase uncertainty.

**Omission/retirement:** Retire a misleading proxy or a control whose remaining resource consequence is immaterial; never infer lifecycle carbon from CPU counters alone. Properties: ESA-055. Source support resolves through those complete property records.

### ESA-CS17 — RESTful/SOA certification by naming

**Protected function:** Actual interaction constraints and service effects must be distinguished from generic API labels. **Consumer:** Producers, consumers and service owners.

**Prerequisites:** A relevant hypermedia or service-reference context and explicit semantics. **Minimal alternative:** An ordinary well-specified local interface when the fuller style/model is unnecessary.

**Fuller-form trigger:** Independent hypermedia evolution or cross-ownership service interactions make the specific constraints useful. **Cost of simplification:** Omitting constraints may lose the properties the chosen style was intended to support.

**Omission/retirement:** Drop the label rather than claim constraints not implemented; omit a domain-specific style outside its problem setting. Properties: ESA-065, ESA-066. Source support resolves through those complete property records.

### ESA-CS18 — Recursive ADD decomposition tree

**Protected function:** Architectural drivers must lead to considered design choices and evaluation, not endless tree expansion. **Consumer:** Designers allocating responsibilities and evaluators of driver satisfaction.

**Prerequisites:** Real drivers and uncertainty that can be reduced by decomposition/alternative analysis. **Minimal alternative:** A direct design choice, one or two alternatives and a focused check.

**Fuller-form trigger:** Large scope, interacting drivers or repeated decisions justify systematic recursion. **Cost of simplification:** Too little structure can hide unresolved allocations; too much freezes guesses as design.

**Omission/retirement:** Stop recursion when additional detail no longer changes a consequential decision; ordinary detailed design can continue separately. Properties: ESA-067. Source support resolves through those complete property records.


## EVOLVED_SOFTWARE_ARCHITECTURE_CRITICISM_LEDGER

Objections were allowed to change dispositions, not appended as a ceremonial limitations paragraph. Published criticism, field failures, empirical null/conditional findings and this study’s analytical objections remain distinguishable. The source-table locators resolve the inspected evidence behind each entry.

### ESA-CR001 — “Architecture is important decisions” can become circular and give architects unlimited jurisdiction.

**Evidence:** Foundational definitions differ; Fowler presents contextual definitions and competing architect roles, while Spolsky criticises detached generalisation. **Response:** Use consequence-bound significance and a named consumer rather than rank or diagram altitude.

**Present judgement:** ESA-006 has no general operational property; ESA-001 survives in a bounded form; conceptual integrity does not require central approval. **Residual uncertainty:** No universal threshold separates architecture from detailed design.

Affected: ESA-001, ESA-004, ESA-006, ESA-056. Sources: ESA-S002, ESA-S010, ESA-S042. Transition: `NARROWED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR002 — A component boundary or matching signature does not expose its control, state or environmental assumptions.

**Evidence:** Parnas identifies a flaw in his illustrative boundary; the Aesop experience reports integration failures from architectural assumptions. **Response:** Combine information hiding with explicit semantic assumptions and appropriate dependency kinds.

**Present judgement:** Retain decomposition; reject nominal isolation and style-name compatibility as sufficient evidence. **Residual uncertainty:** Which assumptions to expose economically depends on credible changes and failures.

Affected: ESA-007, ESA-008, ESA-009, ESA-010, ESA-011, ESA-025. Sources: ESA-S001, ESA-S026. Transition: `REFINED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR003 — More independently deployed components can increase coordination without yielding useful independence.

**Evidence:** Istio’s 1.5 control-plane consolidation and Shopify’s modular-monolith account are positive alternatives; practitioner survey reports data and testing burdens. **Response:** Select or consolidate boundaries by actual scale, release, trust and change needs.

**Present judgement:** Both microservices and local modularity remain conditional alternatives, not sequential maturity levels. **Residual uncertainty:** Company accounts are selected, self-reported and not controlled economic comparisons.

Affected: ESA-012, ESA-049, ESA-050, ESA-051, ESA-056. Sources: ESA-S037, ESA-S038, ESA-S039, ESA-S060. Transition: `NARROWED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR004 — A well-run workshop can select the wrong population of scenarios or omit costly concerns.

**Evidence:** QAW prioritisation is time-bounded; the risk-theme study found many omissions; controlled method comparison has narrow tasks. **Response:** Challenge scenario selection, preserve dissent and separate review outputs from operating evidence.

**Present judgement:** ESA-031 is rejected; scenario methods remain valuable but do not provide coverage by ceremony. **Residual uncertainty:** Reliable low-cost discovery of rare or unknown scenarios remains difficult.

Affected: ESA-002, ESA-014, ESA-015, ESA-028, ESA-031. Sources: ESA-S017, ESA-S020, ESA-S021, ESA-S023. Transition: `REFINED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR005 — Quality objectives interact and apparent improvements can hide costs outside the chosen metric.

**Evidence:** Tactic/utility models have assumptions; EcoFaaS improves selected energy/tail responses while increasing mean latency versus one baseline. **Response:** Declare hard constraints, measurement boundaries and accepted sacrifices.

**Present judgement:** ESA-019 is rejected; ESA-017 is retained as a core constraint on every optimisation claim. **Residual uncertainty:** Complete externality accounting and stable stakeholder utility are not generally available.

Affected: ESA-016, ESA-017, ESA-018, ESA-019, ESA-055. Sources: ESA-S016, ESA-S022, ESA-S061. Transition: `REJECTED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR006 — A complete-looking architecture description can be redundant, stale or consistently false.

**Evidence:** Kruchten explicitly permits omission of irrelevant views; standards concern descriptions; reflexion requires mappings. **Response:** Choose concern-specific views and verify decision-relevant correspondence.

**Present judgement:** Mandatory 4+1 completion and description conformance as quality certification are rejected. **Residual uncertainty:** The cheapest sufficient representation and update mechanism vary by consumer and change rate.

Affected: ESA-020, ESA-021, ESA-023, ESA-037, ESA-059. Sources: ESA-S003, ESA-S011, ESA-S045. Transition: `NARROWED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR007 — Port compatibility alone does not preserve the deadlock property people may infer from it.

**Evidence:** Wright’s author revision provides a non-conservative-glue counterexample and a theorem with additional conditions. **Response:** Require the theorem’s conservatism/deadlock-freedom conditions and separate realisation correspondence.

**Present judgement:** Retain the formal result only inside its exact model and assumptions. **Residual uncertainty:** Obtaining an adequate real-system abstraction can dominate the cost of proof.

Affected: ESA-022, ESA-068. Sources: ESA-S015. Transition: `REFINED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR008 — Method structure, adoption and risk discovery do not independently establish predictive or economic superiority.

**Evidence:** The internal replication uses 16 practitioner-students and finds no efficiency/ease advantage; ATAM risk reports are not downstream outcome trials. **Response:** Use a review proportional to the decision and test the consequences it predicts.

**Present judgement:** No universal full-method obligation is retained; formal economic modelling remains assumption-sensitive. **Residual uncertainty:** Independent longitudinal studies with credible counterfactuals are limited in the inspected evidence.

Affected: ESA-026, ESA-027, ESA-028, ESA-029, ESA-030. Sources: ESA-S021, ESA-S022, ESA-S023. Transition: `NARROWED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR009 — Decision records may be unread, stale or retroactive justifications.

**Evidence:** Rationale survey respondents report barriers; rational reconstruction differs from actual history. **Response:** Capture only decision-relevant context, mark status/reopening conditions and distinguish reconstructed explanation.

**Present judgement:** Knowledge preservation survives; documentation volume does not. **Residual uncertainty:** The total cost/benefit of documentation across turnover and distributed teams is not causally estimated here.

Affected: ESA-032, ESA-033, ESA-037, ESA-064. Sources: ESA-S009, ESA-S027, ESA-S029. Transition: `REFINED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR010 — A deterministic Conway slogan confuses communication with hierarchy and association with cause.

**Evidence:** Single-firm congruence and matched-product mirroring studies have selected populations, proxies and confounding. **Response:** Investigate the actual dependency and coordination mechanism before changing teams or architecture.

**Present judgement:** ESA-036 is rejected; coordination remains assumption-sensitive, not an inevitable organisational law. **Residual uncertainty:** Which coordination intervention causes benefit in a new setting requires new evidence.

Affected: ESA-004, ESA-005, ESA-034, ESA-035, ESA-036. Sources: ESA-S030, ESA-S031, ESA-S032. Transition: `NARROWED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR011 — Recovered structure and deviation counts do not establish harmful erosion or historical intent.

**Evidence:** Reflexion is mapping-relative; review labels capture discussions; smell refactoring has heterogeneous effects. **Response:** Validate relations, connect deviations to current concerns and adjudicate baseline versus implementation.

**Present judgement:** Zero historical deviations and reconstructed-intent substitution are rejected; smell scores are defeasible triage. **Residual uncertainty:** Ground-truth erosion and operational detector calibration remain unsettled.

Affected: ESA-024, ESA-038, ESA-039, ESA-040, ESA-041, ESA-042. Sources: ESA-S045, ESA-S046, ESA-S047, ESA-S048. Transition: `REFINED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR012 — “Debt” can become a moral category for disliked design, with fictitious interest and compelled repayment.

**Evidence:** The original metaphor and qualitative architecture-debt studies do not supply universal monetary rates. **Response:** Identify a compromise, specific causal burden, time horizon and feasible remedy/no-remedy alternative.

**Present judgement:** Retain burden-based architecture debt; no general duty to repay every imperfection. **Residual uncertainty:** Future interest and remediation cost are often uncertain or confounded with ordinary growth.

Affected: ESA-043, ESA-044, ESA-049. Sources: ESA-S049, ESA-S050, ESA-S056. Transition: `NARROWED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR013 — A self-adaptive system can silently lose a trustworthy model and still appear to be controlling correctly.

**Evidence:** Rainbow fault-injection tests reveal silent invalid/stale state; industrial survey reports assurance and trust concerns. **Response:** Validate observation and action translation, constrain changes and evaluate actual post-change state; assess controller revisions separately.

**Present judgement:** Local metric self-authorisation is rejected; adaptation and its self-revision remain conditional. **Residual uncertainty:** The inspected evidence does not justify unrestricted changing objectives or recursive self-authorisation.

Affected: ESA-045, ESA-046, ESA-047, ESA-048, ESA-063. Sources: ESA-S053, ESA-S054, ESA-S055. Transition: `REFINED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR014 — Reusable families and semantic contexts can introduce incompatible variation and expensive translation.

**Evidence:** Family-design mechanisms rely on useful subsets; mismatch exposes hidden assumptions; bounded contexts explicitly have relationships. **Response:** Limit family scope, test combinations and select shared meaning versus translation deliberately.

**Present judgement:** Family mechanisms remain domain-specific; one context does not imply one service or one team. **Residual uncertainty:** Economics of family selection belong to later product-line inquiry, not a conclusion supplied by this lane.

Affected: ESA-013, ESA-049, ESA-061. Sources: ESA-S006, ESA-S026, ESA-S033. Transition: `DOMAIN_SPECIFIC`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR015 — Serverless and “green” labels can move rather than remove cost and resource consumption.

**Evidence:** 2019 serverless analysis identifies storage/communication issues; EcoFaaS uses a narrow energy boundary and chosen SLO. **Response:** Use actual provider contracts and workload/lifecycle boundaries; compare feasible deployment alternatives.

**Present judgement:** No inherent cost, latency or sustainability superiority is retained. **Residual uncertainty:** Lifecycle carbon, rebound and provider-hidden effects require additional target evidence.

Affected: ESA-052, ESA-055. Sources: ESA-S057, ESA-S058, ESA-S061. Transition: `NARROWED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR016 — Learned components can change behaviour through data and feedback without any source-level interface change.

**Evidence:** ML engineering experience identifies entanglement, undeclared consumers and feedback loops. **Response:** Expand architectural dependencies and evaluation to data/model/population context.

**Present judgement:** Deterministic-interface reasoning is not transferred unchanged to learned components. **Residual uncertainty:** Unknown consumers and feedback may be difficult to detect; deployment benefit is not quantified here.

Affected: ESA-011, ESA-043, ESA-053. Sources: ESA-S056. Transition: `DOMAIN_SPECIFIC`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR017 — Automated text, diagram and clustering success can be mistaken for validated architecture or trustworthy metrics.

**Evidence:** 2026 studies use bounded tasks, author or proxy judgements and sometimes one run per configuration; self-reported metrics can be wrong. **Response:** Independently check generated semantics and evidence; use AI to propose rather than self-certify.

**Present judgement:** Assistance is assumption-sensitive; open-ended autonomous architecting remains unresolved, not proved impossible. **Residual uncertainty:** Representative longitudinal autonomy, total verification cost and changing requirements remain open.

Affected: ESA-024, ESA-040, ESA-054, ESA-060. Sources: ESA-S047, ESA-S059, ESA-S062, ESA-S063. Transition: `STILL_CONTESTED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR018 — Elaborate architectural process may burden a stable small system more than it protects it.

**Evidence:** Original methods include tailoring; practitioner critiques document the forces favouring expediency and simpler forms. **Response:** Use the smallest coherent concern–decision–realisation–feedback arrangement, adding technique only for a demonstrated need.

**Present judgement:** Reject both maximal ceremony and “emergence means no reasoning”; ADD remains a selectable method. **Residual uncertainty:** Evidence does not provide a universal small-team threshold or control-retirement formula.

Affected: ESA-056, ESA-058, ESA-067. Sources: ESA-S003, ESA-S008, ESA-S010, ESA-S017, ESA-S041, ESA-S042. Transition: `NARROWED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR019 — Usability cannot always be repaired in the presentation layer, but not every usability scenario has architectural consequences.

**Evidence:** The usability/architecture scenario construction explicitly removed scenarios without substantive architectural implications. **Response:** Trace a user task to the state/control mechanism before moving responsibility across layers.

**Present judgement:** Retain architectural consideration for consequential user interactions without turning the scenario catalogue into mandatory features. **Residual uncertainty:** Architectural support is necessary in some cases but does not itself demonstrate usability for a population.

Affected: ESA-062, ESA-014, ESA-016. Sources: ESA-S018. Transition: `REFINED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.

### ESA-CR020 — Weighted optimisation can conceal external obligations and stakeholder inequality.

**Evidence:** CBAM’s additive utility assumptions and EcoFaaS’s chosen latency/energy boundary delimit their valid interpretations. **Response:** Treat hard constraints separately and disclose whose cost/benefit is measured; analytical extension, not a theorem supplied by either method.

**Present judgement:** No automatic scalarisation of all concerns; the composed system preserves vetoing constraints where legitimately specified. **Residual uncertainty:** Resolving conflicting legitimate stakeholder constraints may require decisions outside software architecture.

Affected: ESA-029, ESA-047, ESA-055. Sources: ESA-S022, ESA-S061. Transition: `NARROWED`. Sourced objection/evidence distinguished from this packet’s present synthesis; not every proposed response is an empirically validated intervention.


## EVOLVED_SOFTWARE_ARCHITECTURE_EVOLUTION_UNDER_CRITICISM

Maturity here often means narrower claims, cheaper practice or stronger correspondence obligations. The following transitions state what changes; a new label alone is not an improvement. When the response is this report’s reconstruction rather than a documented historical causal sequence, that limitation is preserved.

| Transition | Pressure | Present response | Class |
|---|---|---|---|
| ESA-EV01 / ESA-CR001 | “Architecture is important decisions” can become circular and give architects unlimited jurisdiction. | ESA-006 has no general operational property; ESA-001 survives in a bounded form; conceptual integrity does not require central approval. | `NARROWED` |
| ESA-EV02 / ESA-CR002 | A component boundary or matching signature does not expose its control, state or environmental assumptions. | Retain decomposition; reject nominal isolation and style-name compatibility as sufficient evidence. | `REFINED` |
| ESA-EV03 / ESA-CR003 | More independently deployed components can increase coordination without yielding useful independence. | Both microservices and local modularity remain conditional alternatives, not sequential maturity levels. | `NARROWED` |
| ESA-EV04 / ESA-CR004 | A well-run workshop can select the wrong population of scenarios or omit costly concerns. | ESA-031 is rejected; scenario methods remain valuable but do not provide coverage by ceremony. | `REFINED` |
| ESA-EV05 / ESA-CR005 | Quality objectives interact and apparent improvements can hide costs outside the chosen metric. | ESA-019 is rejected; ESA-017 is retained as a core constraint on every optimisation claim. | `REJECTED` |
| ESA-EV06 / ESA-CR006 | A complete-looking architecture description can be redundant, stale or consistently false. | Mandatory 4+1 completion and description conformance as quality certification are rejected. | `NARROWED` |
| ESA-EV07 / ESA-CR007 | Port compatibility alone does not preserve the deadlock property people may infer from it. | Retain the formal result only inside its exact model and assumptions. | `REFINED` |
| ESA-EV08 / ESA-CR008 | Method structure, adoption and risk discovery do not independently establish predictive or economic superiority. | No universal full-method obligation is retained; formal economic modelling remains assumption-sensitive. | `NARROWED` |
| ESA-EV09 / ESA-CR009 | Decision records may be unread, stale or retroactive justifications. | Knowledge preservation survives; documentation volume does not. | `REFINED` |
| ESA-EV10 / ESA-CR010 | A deterministic Conway slogan confuses communication with hierarchy and association with cause. | ESA-036 is rejected; coordination remains assumption-sensitive, not an inevitable organisational law. | `NARROWED` |
| ESA-EV11 / ESA-CR011 | Recovered structure and deviation counts do not establish harmful erosion or historical intent. | Zero historical deviations and reconstructed-intent substitution are rejected; smell scores are defeasible triage. | `REFINED` |
| ESA-EV12 / ESA-CR012 | “Debt” can become a moral category for disliked design, with fictitious interest and compelled repayment. | Retain burden-based architecture debt; no general duty to repay every imperfection. | `NARROWED` |
| ESA-EV13 / ESA-CR013 | A self-adaptive system can silently lose a trustworthy model and still appear to be controlling correctly. | Local metric self-authorisation is rejected; adaptation and its self-revision remain conditional. | `REFINED` |
| ESA-EV14 / ESA-CR014 | Reusable families and semantic contexts can introduce incompatible variation and expensive translation. | Family mechanisms remain domain-specific; one context does not imply one service or one team. | `DOMAIN_SPECIFIC` |
| ESA-EV15 / ESA-CR015 | Serverless and “green” labels can move rather than remove cost and resource consumption. | No inherent cost, latency or sustainability superiority is retained. | `NARROWED` |
| ESA-EV16 / ESA-CR016 | Learned components can change behaviour through data and feedback without any source-level interface change. | Deterministic-interface reasoning is not transferred unchanged to learned components. | `DOMAIN_SPECIFIC` |
| ESA-EV17 / ESA-CR017 | Automated text, diagram and clustering success can be mistaken for validated architecture or trustworthy metrics. | Assistance is assumption-sensitive; open-ended autonomous architecting remains unresolved, not proved impossible. | `STILL_CONTESTED` |
| ESA-EV18 / ESA-CR018 | Elaborate architectural process may burden a stable small system more than it protects it. | Reject both maximal ceremony and “emergence means no reasoning”; ADD remains a selectable method. | `NARROWED` |
| ESA-EV19 / ESA-CR019 | Usability cannot always be repaired in the presentation layer, but not every usability scenario has architectural consequences. | Retain architectural consideration for consequential user interactions without turning the scenario catalogue into mandatory features. | `REFINED` |
| ESA-EV20 / ESA-CR020 | Weighted optimisation can conceal external obligations and stakeholder inequality. | No automatic scalarisation of all concerns; the composed system preserves vetoing constraints where legitimately specified. | `NARROWED` |

## EVOLVED_SOFTWARE_ARCHITECTURE_INTERNAL_TENSIONS

A tension is resolved only as far as an admissible discriminator permits. The hybrids below are not requests to maximise both sides simultaneously. They retain failure conditions and uncertainty.

### ESA-T001 — Conceptual integrity versus Local autonomy

**Costs:** Central bottlenecks versus semantic incompatibility. **First side favoured:** Shared users/invariants require a common meaning across decisions. **Second side favoured:** Decisions are local, reversible and do not alter others’ obligations.

**Supported hybrid:** Share essential contracts and permit independent implementations or explicit translations. **Hybrid failure:** A supposedly local exception changes a shared invariant, or shared rules expand to stylistic micromanagement.

**Discriminator:** Can this choice change an external consumer’s required behaviour or meaning? If yes, negotiate that consequence; otherwise leave it local. **Uncertainty:** Which semantics truly need common ownership is often contested.

Affected: ESA-004, ESA-005, ESA-034, ESA-035, ESA-061. [ESA-S010, ESA-S031, ESA-S033.]

### ESA-T002 — Abstraction and information hiding versus Transparency and directness

**Costs:** Indirection and runtime overhead versus propagated change and exposed implementation knowledge. **First side favoured:** A credible recurring change can be insulated by a stable semantic contract. **Second side favoured:** The direct mechanism is stable, cheap to change and clearer for its consumers.

**Supported hybrid:** Expose relevant behaviour/diagnostics while hiding the varying implementation choice. **Hybrid failure:** An interface hides information the consumer needs for correctness or diagnosis, or abstraction predicts the wrong changes.

**Discriminator:** Try the likely change and a realistic diagnosis/performance case; compare affected obligations and overhead. **Uncertainty:** Future change frequency and debugging cost cannot always be predicted.

Affected: ESA-007, ESA-008, ESA-009, ESA-016, ESA-049. [ESA-S001, ESA-S006, ESA-S026.]

### ESA-T003 — Future modifiability versus Present simplicity

**Costs:** Paid flexibility premium versus potentially expensive later migration. **First side favoured:** Repeated credible variants or changes have high rework costs. **Second side favoured:** Future variants are speculative and later correction remains cheap.

**Supported hybrid:** Implement stable seams for plausible changes while deferring unused generality. **Hybrid failure:** Seams leak semantics or temporary flexibility becomes a permanent platform without consumers.

**Discriminator:** What evidence makes this change likely, and which break-even assumptions would reverse the investment? **Uncertainty:** Neither blanket anticipation nor blanket deferral dominates every domain.

Affected: ESA-007, ESA-013, ESA-044, ESA-049, ESA-051. [ESA-S001, ESA-S006, ESA-S010, ESA-S037.]

### ESA-T004 — Stronger evaluation versus Decision latency and modelling cost

**Costs:** Slow review, stale models and opportunity cost versus undetected consequential errors. **First side favoured:** Failure consequences are high, model assumptions tractable and stronger evidence can change the decision. **Second side favoured:** A small reversible choice is already understood and extra analysis adds little information.

**Supported hybrid:** Analyse the risky interaction formally and evaluate the remaining design with focused scenarios/prototypes. **Hybrid failure:** The formal island ignores the actual failure boundary or a rushed lightweight review omits a critical scenario.

**Discriminator:** Will the added method discriminate feasible options or protect an otherwise unexamined severe consequence? **Uncertainty:** There is no validated universal effort threshold.

Affected: ESA-022, ESA-027, ESA-028, ESA-030, ESA-056, ESA-068. [ESA-S015, ESA-S020, ESA-S023.]

### ESA-T005 — Conformance and continuity versus Justified evolution

**Costs:** Unreviewed erosion versus entrenching obsolete constraints. **First side favoured:** The baseline still protects a current invariant or external commitment. **Second side favoured:** The baseline’s rationale no longer holds and an alternative preserves or improves current obligations.

**Supported hybrid:** Adjudicate deviations and revise implementation or baseline with explicit rationale. **Hybrid failure:** Convenient exception names hide harm, or perfect conformance is rewarded despite worsening outcomes.

**Discriminator:** Which currently valid concern would this deviation harm, and what evidence supports that link? **Uncertainty:** Unknown long-term consequences may keep the deviation unresolved.

Affected: ESA-033, ESA-038, ESA-039, ESA-042, ESA-045. [ESA-S002, ESA-S020, ESA-S045, ESA-S048.]

### ESA-T006 — Flexible boundaries versus Cross-boundary invariant preservation

**Costs:** Coordination/transaction cost versus inconsistent state or meaning. **First side favoured:** A shared invariant genuinely requires coordinated action across participants. **Second side favoured:** Local changes can be decoupled without violating the consumer’s obligations.

**Supported hybrid:** Use the weakest coordination sufficient for the actual invariant, with explicit compensations only when acceptable. **Hybrid failure:** Compensation cannot undo an external effect; eventual consistency is used for a constraint that requires immediate validity.

**Discriminator:** Can a temporarily inconsistent or irreversible state be accepted by the actual affected consumer? **Uncertainty:** Invariant ownership and acceptable inconsistency require contextual authority.

Affected: ESA-008, ESA-011, ESA-012, ESA-017, ESA-035, ESA-050, ESA-061. [ESA-S026, ESA-S035, ESA-S036, ESA-S060.]

### ESA-T007 — Fast automated feedback versus Evidence validity and interpretability

**Costs:** Cheap signal and scale versus false positives, self-reported metrics and missing paths. **First side favoured:** The indicator is calibrated and can prioritise a large repeated problem. **Second side favoured:** The target is small or the proxy is too disconnected from the consequence.

**Supported hybrid:** Automate candidate detection and independently adjudicate high-consequence conclusions. **Hybrid failure:** Human review rubber-stamps a score, or verification cost exceeds saved effort.

**Discriminator:** Does the signal predict the actual concern on positive, negative and changed-condition cases, and at what total cost? **Uncertainty:** Ground-truth datasets and natural operational base rates can be missing.

Affected: ESA-018, ESA-024, ESA-040, ESA-045, ESA-054. [ESA-S045, ESA-S047, ESA-S048, ESA-S062.]

### ESA-T008 — Adaptive performance/efficiency versus Stable external obligations and assurance

**Costs:** Adaptation overhead and controller risk versus lost opportunity under changing demand. **First side favoured:** Conditions vary and bounded actions preserve explicitly checked constraints. **Second side favoured:** Observations/actions are unreliable or the safe static arrangement is adequate.

**Supported hybrid:** Constrain objectives, monitor post-change effects and permit reviewed policy updates. **Hybrid failure:** A local gain breaks an external limit or the controller edits away its own evidence requirement.

**Discriminator:** Is the realised transition inside a currently justified acceptance envelope, not merely better on its objective? **Uncertainty:** Multiple interacting controllers and changing objectives remain difficult.

Affected: ESA-017, ESA-046, ESA-047, ESA-048, ESA-055, ESA-063. [ESA-S053, ESA-S054, ESA-S061.]

### ESA-T009 — Durable knowledge versus Documentation and governance cost

**Costs:** Turnover/reconstruction burden versus obsolete or unread records. **First side favoured:** Non-obvious decisions must survive handovers or distributed coordination. **Second side favoured:** One stable team shares sufficient context for local reversible decisions.

**Supported hybrid:** Short linked records for consequential decisions with clear status and retirement criteria. **Hybrid failure:** Many short records become an unindexed archive or reconstructed stories masquerade as contemporary history.

**Discriminator:** Can a plausible later consumer answer the consequential question without rediscovery, and what does upkeep cost? **Uncertainty:** Causal return on record keeping varies and is poorly estimated.

Affected: ESA-032, ESA-033, ESA-037, ESA-056, ESA-064. [ESA-S009, ESA-S027, ESA-S029.]

### ESA-T010 — Reuse and generality versus Domain fit and specialised efficiency

**Costs:** Translation/variation-management cost versus repeated independent implementation. **First side favoured:** Related contexts share stable obligations and the reuse mechanism preserves them. **Second side favoured:** Semantics or operating qualities differ enough that adaptation defeats the saving.

**Supported hybrid:** Share compatible mechanisms while keeping distinct semantic models and explicit adapters. **Hybrid failure:** A universal framework silently assumes a common control model or feature combination that does not exist.

**Discriminator:** Which exact assumptions are shared, and what must be translated or ruled out for the intended composition? **Uncertainty:** Cross-family benefits require product/maintenance evidence beyond this lane.

Affected: ESA-013, ESA-025, ESA-050, ESA-051, ESA-061, ESA-065, ESA-066. [ESA-S006, ESA-S026, ESA-S033, ESA-S034, ESA-S035.]


## EVOLVED_SOFTWARE_ARCHITECTURE_COMPOSED_SYSTEM

The machine-readable model is [EVOLVED_SOFTWARE_ARCHITECTURE_COMPOSITION_MODEL.json](EVOLVED_SOFTWARE_ARCHITECTURE_COMPOSITION_MODEL.json). Its ten nodes group examined functions; they are not new software components or compulsory organisational posts. Its 65 guarded relations make dependencies, evidence flows, alternatives, conflict and revision explicit. The composition is an analytical synthesis; no study has tested this exact assembled system as an intervention.

### Purpose, state and agency

The purpose is to make consequential software organisation understandable, evaluable and changeable in relation to actual commitments. State includes real responsibilities, interfaces, deployment/configuration and operating behaviour; descriptions and recovered observations; stakeholder concerns; candidate alternatives; decision rationale; and any current conformance or adaptation policy. These are not interchangeable representations of one automatically known truth.

Users, domain participants, maintainers, operators and sponsors can supply different concerns. Designers construct alternatives. Evaluators challenge assumptions and compare consequences. Actual authorised participants accept or reject trade-offs. Implementers and operators change code, configuration, interfaces, deployment or traffic. External parties may own services or constraints that these actors cannot unilaterally revise. The same person may perform several functions; the account does not create an office for each.

Communication carries both information and obligations. A scenario must reach a design/evaluation consumer; a changed interface must reach the dependent party; a conformance finding must reach someone able to judge the baseline; a runtime command must reach an effective actuator. A model update is not a deployment. A decision record is not permission. Permission is not successful execution. Success under one observation is not success under every relevant environment. [ESA-S017; ESA-S020; ESA-S025; ESA-S035; ESA-S045; ESA-S051–054.]

### The coupled architecture activity

Concern/significance reasoning constrains the scope of work. Interface/dependency reasoning identifies what alternatives must preserve. Quality scenarios supply discriminating conditions. Design mechanisms construct candidates; evaluation supplies evidence and reveals omissions. Descriptions and rationale communicate the current account to those who implement, operate or later revise it. Correspondence and operating observations feed back to the affected choice, not automatically to every previous step.

The feedback can reopen a concern, invalidate a change hypothesis, revise a view, repair an implementation or retire a stale rule. Design and evaluation can interleave; independent local decisions can proceed concurrently when shared obligations remain intact. An external constraint or invalid observation can interrupt a proposed action. Nothing requires a completed multi-view specification before any code changes, nor does local progress authorise a cross-boundary commitment. This control structure is supported by the interleaved design model and by the different observation/action roles in conformance and adaptation; the precise combined arrangement is this study’s synthesis. [ESA-S025; ESA-S045; ESA-S051–054.]

### Selection instead of accumulation

The smallest coherent configuration contains a consequential concern, a feasible choice with adequate interface/quality reasoning, the legitimate ability to act, and a check of the real consequence. A brief conversation, ordinary design work and a focused test may implement it. Neither a separate document nor automation is intrinsically required. The fuller branches below are activated by their conditions, not by a maturity score.

**ESA-CFG01 — Small stable one-team application**

Guard: Few consequential interfaces, shared current understanding, low change exposure.

Selected functions: ESA-001, ESA-002, ESA-007, ESA-008, ESA-014, ESA-017, ESA-018, ESA-026, ESA-056

Form: Direct conversation, simple local design, one relevant alternative/quality check, and a short rationale only for a non-obvious durable choice.

Omissions: No automatic ATAM event, ADL, multi-view package, service split, debt programme or adaptation controller. Ordinary engineering can supply the functions.

Escalation trigger: Growing consequence reach, turnover, unobserved risk or recurring cross-boundary change.

Retirement: Remove a control when its protected concern or consumer disappears without undermining another obligation.

**ESA-CFG02 — Long-lived multi-team product**

Guard: Cross-team semantic/quality obligations, turnover and significant change.

Selected functions: ESA-002, ESA-004, ESA-005, ESA-008, ESA-010, ESA-012, ESA-014, ESA-015, ESA-017, ESA-020, ESA-021, ESA-024, ESA-026, ESA-028, ESA-032, ESA-033, ESA-034, ESA-035, ESA-038, ESA-039, ESA-043, ESA-044, ESA-045, ESA-056

Form: Selected shared contracts and views, retrievable decisions, contextual conformance and proportionate evaluations; local design proceeds concurrently inside shared constraints.

Omissions: No forced one-team-per-component mapping, universal documentation set or full review for every edit.

Escalation trigger: A concrete high-consequence interaction may justify focused formal analysis or a migration experiment.

Retirement: Collapse coordination/description layers that no longer protect active cross-team obligations.

**ESA-CFG03 — High-consequence modelled interaction**

Guard: A tractable formal property is material and its realisation can be checked.

Selected functions: ESA-003, ESA-008, ESA-009, ESA-014, ESA-015, ESA-017, ESA-018, ESA-021, ESA-022, ESA-026, ESA-030, ESA-038, ESA-056, ESA-068

Form: Focused formal analysis with explicit theorem conditions plus empirical/correspondence checks for the environment.

Omissions: No claim that the whole system is verified or that formal proof supplies stakeholder authority.

Escalation trigger: Model mismatch, new interaction or a consequence outside the chosen semantics.

Retirement: Use a cheaper model/test when the formally protected interaction no longer exists or its consequence is no longer material.

**ESA-CFG04 — Bounded runtime adaptation**

Guard: Changing operation justifies automated reconfiguration and a valid action/evidence envelope exists.

Selected functions: ESA-003, ESA-005, ESA-008, ESA-014, ESA-017, ESA-018, ESA-021, ESA-033, ESA-045, ESA-046, ESA-047, ESA-056, ESA-063

Form: Valid observations and model translations feed a constrained decision mechanism; effectors change the system; subsequent observations test the outcome; engineers retain policy-revision accountability.

Omissions: No open-ended self-authorisation or automatic revision of external constraints.

Escalation trigger: Lost observation validity, unavailable effectors, interacting-controller risk or a needed action outside delegation.

Retirement: Prefer stable configuration/operator procedure if variability or net benefit disappears.

**ESA-CFG05 — Family or heterogeneous domain composition**

Guard: Real variants or multiple semantic contexts require shared and distinct obligations.

Selected functions: ESA-007, ESA-008, ESA-010, ESA-012, ESA-013, ESA-017, ESA-026, ESA-033, ESA-035, ESA-044, ESA-049, ESA-056, ESA-061

Form: Explicit commonality/variation and model-context boundaries with tested translation and valid combination conditions.

Omissions: No conclusion about unread product-line economics or mandatory microservice deployment.

Escalation trigger: New variant/context invalidates an interface or shared quality assumption.

Retirement: Remove unused variation points and translations after consumers disappear.

### Explicit relation account

The direction of `REQUIRES` is FROM needs TO under the guard. Evidence relations contribute warrant without claiming proof; alternatives are selected rather than accumulated; negative candidates appear as conflicts, not requirements. These relation groups expose the operative structure; every individual guard and cost is in the composition model.

**REQUIRES** — FROM needs the TO condition/mechanism under the guard; not a global sequencing rule. Entries: ESA-REL001, ESA-REL006, ESA-REL012, ESA-REL013, ESA-REL031, ESA-REL036, ESA-REL038, ESA-REL040, ESA-REL043, ESA-REL046.

**ENABLES** — FROM supplies a capability or input TO can use. Entries: ESA-REL003, ESA-REL007, ESA-REL011, ESA-REL030, ESA-REL048.

**CONSTRAINS** — FROM limits admissible use of TO. Entries: ESA-REL004, ESA-REL005, ESA-REL010, ESA-REL014, ESA-REL021, ESA-REL039, ESA-REL041, ESA-REL047.

**PROVIDES_EVIDENCE_FOR** — FROM contributes evidence to TO without automatically proving it. Entries: ESA-REL008, ESA-REL017, ESA-REL020, ESA-REL023, ESA-REL025, ESA-REL034, ESA-REL035, ESA-REL045.

**COMMUNICATES_TO** — FROM carries information or commitments to the consumer in TO. Entries: ESA-REL002, ESA-REL016, ESA-REL028, ESA-REL032, ESA-REL037.

**ACTS_THROUGH** — FROM is realised through the mechanisms named in TO. Entries: ESA-REL026, ESA-REL050, ESA-REL051.

**FEEDBACK_TO** — Observations/findings at FROM can reopen or revise TO. Entries: ESA-REL015, ESA-REL024, ESA-REL027, ESA-REL029, ESA-REL033.

**ALTERNATIVE_TO** — Guarded selection/substitution, not simultaneous mandatory use. Entries: ESA-REL009, ESA-REL018, ESA-REL022, ESA-REL042.

**CONFLICTS_WITH** — Incompatible claims/assumptions; rejected candidates are not requirements. Entries: ESA-REL052, ESA-REL053, ESA-REL054, ESA-REL055, ESA-REL056, ESA-REL057, ESA-REL058, ESA-REL059, ESA-REL060, ESA-REL061, ESA-REL062, ESA-REL064.

**REFINES** — FROM narrows or adds conditions to TO. Entries: ESA-REL019, ESA-REL044, ESA-REL049.

**SUPERSEDES** — FROM replaces the specified candidate meaning in TO while preserving the denominator. Entries: ESA-REL063.

**SHARES_ANCESTRY_WITH** — Bounded common design ancestry, not necessarily a verified direct influence. Entries: ESA-REL065.

### Revision and adversarial case tests

Revision can affect a decision, model, software structure or bounded policy, according to the actual mandate. It must preserve the distinction between earlier and current assumptions and examine transition-state consequences. A successor policy cannot warrant itself merely by improving its own score. The following invented cases test the coherence and discriminating power of this account; they are not empirical validation.

**ESA-CASE01 — One-team stable application versus long-lived multi-team product (analytical).** Two systems have comparable functionality; one has stable shared understanding and cheap local change, the other many teams, turnover and cross-boundary commitments. The small team uses ordinary code review plus a few consequential checks. The multi-team product preserves interface obligations, decisions and correspondence where consumers need them.

Required observation: Whether consequential decisions are actually understood and whether changes violate another consumer’s commitments. Verdict: No mandatory architecture office, multi-view package or ADR per edit. More coordination is warranted only where the second context creates a real dependency. Defeater: The supposedly simple application acquires a critical external contract, or the multi-team artefacts have no demonstrable consumer. Properties: ESA-001, ESA-002, ESA-007, ESA-032, ESA-035, ESA-056.

**ESA-CASE02 — Identical functional output, different operating qualities (analytical).** Two implementations return the same answers, but one times out under the required load and another consumes an unacceptable resource budget. Evaluate the declared response measures under the relevant load and resource boundary; choose a feasible trade-off rather than output equivalence alone.

Required observation: Latency distribution, throughput/failure behaviour and the actual resource measure under stated conditions. Verdict: Functional equivalence is insufficient for the architecture choice. The relevant quality constraints can discriminate. Defeater: The load or resource boundary is unrepresentative, or neither implementation can satisfy the external constraint. Properties: ESA-014, ESA-016, ESA-017, ESA-018, ESA-030.

**ESA-CASE03 — Authorised improvement violates an obsolete rule (analytical).** An old layering rule forbids a new dependency; a reviewed replacement preserves the protected invariant with lower cost. Investigate the finding, confirm authority and real effect, then supersede the rule/mapping rather than force the old structure.

Required observation: The invariant still holds; obsolete consumers are absent; the new relation is represented accurately. Verdict: Deviation is not automatically erosion. Conformance supplies a finding, not a veto over justified evolution. Defeater: The old rule protected an overlooked security or failure boundary, or the proposed change was not actually authorised. Properties: ESA-021, ESA-033, ESA-038, ESA-039, ESA-042, ESA-045.

**ESA-CASE04 — Apparently isolated component with hidden shared state (analytical).** Two separately deployed services share a mutable table and are forced to release together whenever its interpretation changes. Inspect semantic/data dependencies. Either enforce the needed independence or accept a coordinated unit rather than count deployments as isolation.

Required observation: A representative schema/semantic change and fault demonstrate the actual propagation boundary. Verdict: Naming and process separation do not establish operational independence. A modular monolith or explicit shared contract may dominate. Defeater: A genuine independent scaling/failure constraint makes consolidation unacceptable; stronger data contracts may instead be justified. Properties: ESA-007, ESA-008, ESA-010, ESA-011, ESA-050, ESA-051.

**ESA-CASE05 — Successful review, unrepresentative workload (analytical).** An architecture review finds no major risks for a small steady workload; production has bursty traffic and a previously omitted failure mode. Treat the new evidence as a reason to reopen scenarios and the affected choice, not as proof the review procedure was faithfully predictive.

Required observation: Production-relevant load/fault observations, with the earlier assumptions retained for comparison. Verdict: The review’s coordination/risk-discovery result can remain real while its operational prediction is invalid outside scope. Defeater: The supposed production observation is itself sampled or misattributed; causal contribution requires separating changed architecture from unrelated interventions. Properties: ESA-015, ESA-018, ESA-028, ESA-030, ESA-031.

**ESA-CASE06 — Runtime adaptation improves a metric and violates an external constraint (analytical).** A controller saves energy by consolidating work but exceeds a non-negotiable response-time or separation constraint. Exclude the action from admissible policies, restore an acceptable state and examine the policy/model observation boundary.

Required observation: Both energy and the external constraint after the actual change, not the controller’s own score. Verdict: Local improvement neither authorises the change nor establishes whole-system improvement. Defeater: The external constraint was actually negotiable under the authorised trade-off and the new response is within that agreed range. Properties: ESA-017, ESA-046, ESA-047, ESA-048, ESA-055, ESA-063.

**ESA-CASE07 — Failed observation creates a fictitious successful adaptation (analytical).** A stale probe reports a healthy node after the actuator has failed to move work. Suspend the unsupported claim, use independent state evidence or a safe fallback, and repair the observation/actuation mapping.

Required observation: Real deployment and request behaviour establish whether the action happened and whether constraints hold. Verdict: A model transition is not a real transition. The composed account fails closed on the claim, not by pretending all operation can stop without cost. Defeater: A bounded degraded mode is unavailable; the residual operating risk then requires explicit accountable judgement rather than fictional assurance. Properties: ESA-003, ESA-021, ESA-024, ESA-046, ESA-047, ESA-063.

The source-backed cases provide narrower checks on particular mechanisms, not validation of the whole composition:

**ESA-PCASE01 — Aesop architectural mismatch.** Nominally reusable parts can impose incompatible control/data assumptions. One programme; its several publications are not independent replications. [ESA-S026.]

**ESA-PCASE02 — Istio control-plane consolidation.** Shared deployment/scaling/administration can make separate services costly without producing intended independence. Specific control plane; data-plane proxies remained separate; not universal anti-microservices evidence. [ESA-S039.]

**ESA-PCASE03 — Shopify modular monolith.** Deliberate architectural componentisation need not require independent deployment units. Historical project account; does not prove an inevitable size-based architecture progression. [ESA-S038.]

**ESA-PCASE04 — Rainbow robustness tests.** Faults in observed architectural state can lead to silent failures in tested adaptation systems. Injected tests in Znn/DCAS; not production failure frequencies. [ESA-S054.]

**ESA-PCASE05 — EcoFaaS energy/latency experiment.** Resource-control benefits must be read alongside the chosen SLO and latency trade-off; mean latency can worsen while reported energy/tail metrics improve. Specific hardware, workloads and measurement boundary; not whole-lifecycle carbon or every serverless deployment. [ESA-S061.]


## EVOLVED_SOFTWARE_ARCHITECTURE_HYBRIDISATION_AND_EXTERNAL_RELATIONS

Architecture’s productive intersections are preserved without annexing neighbouring traditions. Information hiding and family design overlap product-line architecture through commonality and variation; change, conformance and debt overlap maintenance/evolution; domain-driven design supplies semantic boundaries; coordination research supplies organisational hypotheses; formal methods supply model-relative guarantees; service and platform work supply interaction/environment constraints; and sustainability supplies additional measured concerns.

These are not all the same kind of relation. REST supplies a specific constrained style; the SOA reference model supplies an interaction vocabulary; DDD’s context boundary need not be a deployment boundary; a fitness function need not be a runtime controller. CSP-based analysis is a documented formal-method import, not proof that every architecture should be formalised. The general design model explicitly draws on wider design-process ideas, including function/behaviour/structure reasoning; this does not make software architecture identical to design theory. [ESA-S015; ESA-S025; ESA-S033–035; ESA-S043–044.]

The interface to the two unread SSS lanes asks what is equivalent, complementary, redundant, contradictory or at a different abstraction level. It does not answer on their behalf. A later integration must retain lineage identifiers and shared evidence while permitting one implementation to serve several properties. No new control, owner or artefact is required for every row.

## EVOLVED_SOFTWARE_ARCHITECTURE_STRONGEST_SURVIVING_PROPERTIES

The nine strongest retentions are below. Their common strength is a defensible, discriminating function. Their comparative and deployment evidence is separately qualified; none is an unconditional guarantee.

**ESA-002 — Stakeholder concerns connected to decisions.** Connect each material concern to an architectural question, a scenario or constraint and the decision that consumes it; expose conflicts and missing participation. Trigger: Different users, maintainers, operators or sponsors bear materially different consequences. Cheaper path: For a small shared-understanding team, discuss the few consequential concerns directly and retain only what later action needs. [ESA-S011, ESA-S017, ESA-S020.]

**ESA-003 — Architecture, description and belief distinguished.** Keep intended structure, its representation and claims about the actual system distinguishable; attach a basis and observation scope to assertions of correspondence. Trigger: A decision depends on a diagram, repository model, recovered graph or architect’s account being true of the real system. Cheaper path: Inspect the relevant code/configuration/execution directly when the system is small; a separate comprehensive model is unnecessary. [ESA-S002, ESA-S011, ESA-S045.]

**ESA-007 — Change-oriented information hiding.** Place knowledge of a plausibly varying design decision behind an interface whose clients need not depend on that decision; separate stable obligations from hidden choices. Trigger: A likely change currently propagates through clients that need only the stable service or invariant. Cheaper path: Keep a straightforward local implementation where the variation is unlikely or the extra boundary costs more than the expected change. [ESA-S001, ESA-S006.]

**ESA-008 — Semantic interface assumptions made testable.** Express consequential assumptions about state, control, ordering, data meaning, faults and side effects at the interface; check the assumptions actually relied on by both sides. Trigger: Parts are composed, reused or replaced and nominal signatures do not capture their operating expectations. Cheaper path: Use concrete examples, assertions or focused integration tests for a narrow local interface; a full formal contract is not mandatory. [ESA-S026, ESA-S015, ESA-S035.]

**ESA-010 — Dependency kinds and uses relations distinguished.** Distinguish compile/import, invocation, data, correctness, deployment and change dependencies; choose the relation that can answer the architectural question. Trigger: A dependency graph is being used to infer independence, change impact or coordination needs. Cheaper path: Inspect the few relevant dependencies manually; do not build a global graph when a local semantic explanation suffices. [ESA-S006, ESA-S045, ESA-S031, ESA-S005.]

**ESA-014 — Measurable quality-attribute scenarios.** Express a quality concern through stimulus, source, environment, affected artefact, response and response measure, tailoring detail to the decision being made. Trigger: A quality term such as fast, secure, usable or modifiable must discriminate between designs. Cheaper path: A short, concrete example with an observable acceptable response can suffice; do not fill six empty boxes ceremonially. [ESA-S016, ESA-S017.]

**ESA-017 — Explicit interacting-quality trade-offs and constraints.** Separate hard constraints from preferences, compare effects on multiple concerns and make the chosen sacrifice explicit; do not aggregate away unacceptable consequences. Trigger: Improving one response can worsen another or transfer cost to a different stakeholder. Cheaper path: Eliminate dominated or infeasible options through a brief explicit comparison when elaborate utility modelling adds no decision value. [ESA-S016, ESA-S020, ESA-S022.]

**ESA-018 — Representative workload and failure observations.** Validate important predictions against observations whose workload, faults, configuration and measurement boundary are representative of the decision; distinguish the measurement from the whole quality claim. Trigger: A prototype, benchmark, trace or field observation is being used to accept an architecture. Cheaper path: Use the smallest representative experiment or inspect existing evidence; do not run a broad benchmark suite unrelated to the risk. [ESA-S016, ESA-S020.]

**ESA-021 — Correspondence between views and realisation.** Identify how entities and relations in different views correspond, then check consequential consistency and the link to implementation/configuration/operation. Trigger: A decision combines claims from several views or uses a model as evidence about implementation. Cheaper path: Check a small set of named correspondences manually rather than maintain a universal metamodel. [ESA-S003, ESA-S011, ESA-S045.]


## EVOLVED_SOFTWARE_ARCHITECTURE_CONTEXT_SPECIFIC_PROPERTIES

Formal languages, quality review methods, economic models, program-family mechanisms, continuous checks, runtime adaptation and deployment styles remain selectable branches. Their populations below include refined mechanisms that still have triggers: retention never erases those conditions.

**RETAINED_IN_EVOLVED_FORM (15):** ESA-001, ESA-005, ESA-009, ESA-015, ESA-020, ESA-024, ESA-026, ESA-032, ESA-033, ESA-038, ESA-039, ESA-043, ESA-056, ESA-062, ESA-064.

**CONTEXT_DEPENDENT (13):** ESA-004, ESA-012, ESA-025, ESA-027, ESA-028, ESA-030, ESA-035, ESA-044, ESA-050, ESA-051, ESA-055, ESA-061, ESA-067.

**ASSUMPTION_SENSITIVE (8):** ESA-011, ESA-016, ESA-029, ESA-034, ESA-047, ESA-049, ESA-054, ESA-063.

**DOMAIN_SPECIFIC (8):** ESA-013, ESA-022, ESA-046, ESA-052, ESA-053, ESA-065, ESA-066, ESA-068.

**USEFUL_BUT_EASILY_GAMED (2):** ESA-040, ESA-045.

The audit intake develops each trigger, prerequisite, cost, cheap path and evidence request. A target may already satisfy the function, have no relevant risk, use a simpler adequate mechanism, or lack enough evidence for a judgement. Domain-specific candidates are not converted into universal obligations by being included in this study.

## EVOLVED_SOFTWARE_ARCHITECTURE_REJECTED_OR_SUPERSEDED_PRACTICES

The following complete non-retained/unresolved population prevents a favourable-only denominator. Unresolved capability is separated from rejection; supersession preserves ancestry.

**ESA-006 — Architecture as an unrestricted important-decisions label · NO_GENERAL_PROPERTY.** The shorthand is circular when importance is undefined and can annex detailed design, governance or enterprise strategy. Alternative or boundary: Use the consequence-bound criterion in ESA-001 and state the architectural object.

**ESA-019 — Independent maximisation of every quality · REJECTED_OR_DISFAVOURED.** Finite resources and competing mechanisms invalidate the universal claim; EcoFaaS explicitly exchanges mean latency for energy. Alternative or boundary: Use ESA-017 to compare constrained alternatives and identify any genuine dominated option.

**ESA-023 — Mandatory complete 4+1 documentation · CEREMONY_NOT_GENERAL_PROPERTY.** The original method explicitly permits irrelevant views to be omitted; mandatory forms can hide obsolete content. Alternative or boundary: Select views through ESA-020; omit views that add no needed distinction or communication.

**ESA-031 — Review success as a guarantee of operating quality · REJECTED_OR_DISFAVOURED.** Omissions, model mismatch and unrepresentative workloads break the implication even when the review was performed competently. Alternative or boundary: Keep the review’s actual conclusions and obtain the missing representative evidence through ESA-018.

**ESA-036 — Deterministic organisational mirroring · REJECTED_OR_DISFAVOURED.** Observational matched cases and single-firm regressions do not establish a universal mapping law. Alternative or boundary: Investigate the actual dependency/coordination mechanisms through ESA-034.

**ESA-037 — Documentation quantity as architectural evidence · CEREMONY_NOT_GENERAL_PROPERTY.** Fragments, obsolete rationale and conflicting copies can make extensive documentation worse than a concise current account. Alternative or boundary: Ask a real consumer to recover a needed decision or check a correspondence using the smallest adequate material.

**ESA-041 — Recovered structure as a substitute for intended rationale · REJECTED_OR_DISFAVOURED.** The same structure can result from deliberate trade-off, accident, obsolete conditions or constraints invisible in code. Alternative or boundary: Retain observed facts, ask a knowledgeable participant or state the intent as unresolved rather than manufacture it.

**ESA-042 — Zero deviations from a historical architecture · REJECTED_OR_DISFAVOURED.** The rule can entrench harmful structure and turn conformance metrics into theatre. Alternative or boundary: Adjudicate the rule and change through ESA-038/039, preserving the current protected obligation.

**ESA-048 — Self-authorisation through local metric improvement · REJECTED_OR_DISFAVOURED.** The change may break another quality, violate an external commitment, exploit a proxy or corrupt its own observation basis. Alternative or boundary: Apply independently established constraints and observe the actual consequences through ESA-047.

**ESA-057 — Service and REST constraints distinguished from labels · SUPERSEDED_BY_STRONGER_FORM.** A single broad label obscures different abstraction levels and applicability conditions. Alternative or boundary: Name and check the actual required interaction property without imposing either complete style.

**ESA-058 — Emergence as a reason to omit architectural reasoning · REJECTED_OR_DISFAVOURED.** Accidental dependencies and irreversible choices arise without explicit plans; conversely excessive anticipation can obstruct learning. Alternative or boundary: Use timely local reasoning, concrete experiments and brief rationale rather than a speculative full upfront design.

**ESA-059 — Description-standard conformance as quality certification · REJECTED_OR_DISFAVOURED.** A fully compliant description could faithfully describe a poor architecture, or be disconnected from implementation. Alternative or boundary: Use the standard for the description purpose and separately establish the selected system-quality claim.

**ESA-060 — Autonomous architecting under open-ended requirements · UNRESOLVED.** Diagram quality, student risk lists and structural clustering do not cover authority, live operation, changing stakeholders or external consequences. Alternative or boundary: Use bounded assistance or a constrained controller with explicit admissible actions and independent evaluation.


## EVOLVED_SOFTWARE_ARCHITECTURE_CURRENT_STATE_AND_RESEARCH_FRONTIER

The current search reaches 2026 rather than treating historical architectural fashions as the present frontier. Three contemporary directions are particularly discriminating.

First, decomposition and reconstruction automation are advancing on labelled comments and recurring benchmark systems. The unresolved transfer is from a proxy—structural modularity, a classifier label, a generated diagram—to actual quality, independent change and operating cost. The erosion classifier’s balanced dataset must not be interpreted as deployment prevalence. Reused projects and earlier results also limit the independence of apparent confirmations. [ESA-S047–048; ESA-S063.]

Second, LLMs can generate and assess architectural material, but the examined studies leave important gaps: educational/reference judgements, excluded groups, single executions per configuration and no long-term deployment. Structural adherence and confident self-reported metrics are not trustworthy substitutes for independently observed behaviour. ESA-054 remains assumption-sensitive; ESA-060 remains unresolved. This is not an impossibility claim about future research. [ESA-S059; ESA-S062.]

Third, self-adaptation and sustainability place stronger demands on architectural state and measurement boundaries. Industry survey evidence reports actual uses but not population-wide comparative benefit. Energy-focused experiments can illuminate real trade-offs without proving whole-lifecycle sustainability. The 2025 rapid review organises a research agenda but depends on secondary literature and a small practitioner discussion. A mature architecture method keeps these assumptions inspectable rather than covering them with labels. [ESA-S055; ESA-S058; ESA-S061.]

The historical core has not become obsolete. Information hiding still asks which change is insulated; interface reasoning still asks what assumptions compose; evaluation still asks which scenarios discriminate; conformance still asks which baseline is justified. Contemporary systems make those questions harder and sometimes change their objects. They do not answer them automatically.

## EVOLVED_SOFTWARE_ARCHITECTURE_ADVERSARIAL_SYNTHESIS_VERDICT

**Verdict: a conditional coherent core is defensible; universal machinery and universal effectiveness are not.** The composition survives the analytical cases because it can select no extra mechanism, distinguish a quality failure from a functional success, permit justified baseline change, expose hidden coupling, reopen an unrepresentative evaluation, and reject a locally improved but inadmissible adaptation. Those are substantive discriminators rather than generic invitations to “balance” everything.

The strongest objection to unification is that a very general core could merely redescribe competent engineering. The response is not to add more ceremony. It is to retain the explicit interfaces and failure obligations: concerns need consumers; models need correspondence; tactics need environmental assumptions; comparison needs feasible alternatives; decisions need legitimate actors; runtime action needs actual effects; rules need continuing justification. Removing those couplings would make the property catalogue inert. Their exact economical implementation remains contextual.

A second objection is that evidence for individual parts does not validate the assembled system. That objection is accepted. This packet claims a reconciled analytical composition, not an experimentally superior methodology. The optional formal branch has strong model-relative support, while much economic/process benefit remains weakly identified. Field cases inform selection but cannot estimate frequency. An adversarial evaluator may reasonably choose fewer artefacts, a different decomposition, manual operation, or no architectural intervention when the relevant burden is absent.

A third objection concerns authority and conflicting interests. Architectural analysis can reveal consequences but cannot manufacture a legitimate preference order or make every stakeholder whole. Some conflicts require external organisational or contractual judgement. The system therefore separates epistemic findings from authorisation and achieved consequences; it does not solve that political problem by silently maximising a score.

The resulting core is richer than a checklist and smaller than compulsory simultaneous adoption of all 55 crosswalk-worthy candidates. It remains revisable by later evidence, including evidence against this composition.

## EVOLVED_SOFTWARE_ARCHITECTURE_OPEN_QUESTIONS_AND_EVIDENCE_LIMITS

**Examined unresolved candidate:** ESA-060, autonomous architecting under open-ended requirements. Current assistance and bounded-adaptation evidence does not determine when such a capability remains reliable through changing concerns, missing requirements and long-lived operating consequences.

**Examined unresolved composition questions:** the economical amount of evaluation/documentation; affordable scenario/model adequacy in open environments; legitimate resolution of conflicting stakeholder obligations; and reliable open-ended architecting. These are explicitly recorded as ESA-UCO01–04 in the composition model. None is hidden unperformed work.

**Access limits:** full normative clauses of IEEE 1471 and ISO/IEC/IEEE 42010 were not read; the 1976 program-family item and the 2005 decisions paper had limited access; selected original monographs were not inspected; some newer candidate full texts could not be reached. The report uses the official abstracts, author texts and accessible alternatives actually inspected and does not infer unread clauses or outcomes.

**Validity limits:** the corpus mixes conceptual arguments, standards/guidance, proofs, author field accounts, observational studies, selected comparisons and contemporary preprints. Toy cases, small samples, missing baselines, benchmark reuse, incomplete observation, proxy validity, publication/selection bias and shared industrial programmes constrain generalisation. No numerical global confidence or representative effect estimate is justified.

**Bounded completion:** all nine mandatory families and all 68 registered candidates were examined. The coverage register’s uncompleted-burdens array is empty because no promised in-scope research or artefact is deferred. It is not a claim that all publications were retrieved or all questions solved. Freeze stabilises this evidence and judgement revision; it does not make uncertainty disappear.

## Packet navigation and source index

[EVOLVED_SOFTWARE_ARCHITECTURE_PROPERTY_LEDGER.json](EVOLVED_SOFTWARE_ARCHITECTURE_PROPERTY_LEDGER.json)

[EVOLVED_SOFTWARE_ARCHITECTURE_SOURCE_TABLE.json](EVOLVED_SOFTWARE_ARCHITECTURE_SOURCE_TABLE.json)

[EVOLVED_SOFTWARE_ARCHITECTURE_AUDIT_INTAKE.md](EVOLVED_SOFTWARE_ARCHITECTURE_AUDIT_INTAKE.md)

[EVOLVED_SOFTWARE_ARCHITECTURE_PUBLIC_DOCUMENTATION_INTAKE.md](EVOLVED_SOFTWARE_ARCHITECTURE_PUBLIC_DOCUMENTATION_INTAKE.md)

[EVOLVED_SOFTWARE_ARCHITECTURE_SYNTHESIS_INTAKE.md](EVOLVED_SOFTWARE_ARCHITECTURE_SYNTHESIS_INTAKE.md)

[EVOLVED_SOFTWARE_ARCHITECTURE_COMPOSITION_MODEL.json](EVOLVED_SOFTWARE_ARCHITECTURE_COMPOSITION_MODEL.json)

[EVOLVED_SOFTWARE_ARCHITECTURE_RESEARCH_COVERAGE.json](EVOLVED_SOFTWARE_ARCHITECTURE_RESEARCH_COVERAGE.json)

### Exact inspected source records

The JSON source table is authoritative for access level, empirical/formal details, evidence roles and property links. The concise index below supplies titles, dates and claim locators for citation.

**ESA-S001 — On the Criteria To Be Used in Decomposing Systems into Modules.** David L. Parnas. Date: 1972-12; CACM 15(12), 1053–1058. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: pp. 1053–1058: KWIC alternatives; criteria; efficiency; hierarchical structure. Inspected support: Responsibility assignments hide design decisions expected to change; modular decomposition differs from processing order and program hierarchy.

Location: https://wstomv.win.tue.nl/edu/2ip30/references/criteria_for_modularization.pdf; https://doi.org/10.1145/361598.361623.

Evidence limit: Small worked comparison, not a controlled industrial causal study; the author exposes an ordering assumption in his own example.

**ESA-S002 — Foundations for the Study of Software Architecture.** Dewayne E. Perry; Alexander L. Wolf. Date: 1992-10; Software Engineering Notes 17(4), 40–52. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §§2.2–3.3, especially elements/form/rationale, multiple views and evolution. Inspected support: Architecture is reconstructed through elements, form and rationale; drift and erosion are distinguished rather than equated with every change.

Location: https://webhome.csc.uvic.ca/~hausi/480/papers/perry.pdf; https://doi.org/10.1145/141874.141884.

Evidence limit: A foundational research programme with illustrative analogies; not a validated universal taxonomy or economic comparison.

**ESA-S003 — Architectural Blueprints—The ‘4+1’ View Model of Software Architecture.** Philippe Kruchten. Date: 1995-11; IEEE Software 12(6), 42–50; author copy deposited in 2020. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Logical/process/development/physical views; scenarios; pp. 11–14 of author copy, correspondence and tailoring. Inspected support: Views serve different concerns and scenarios integrate them; irrelevant views may be omitted.

Location: https://arxiv.org/pdf/2006.04975.

Evidence limit: Author experience and worked architectures, not comparative evidence that five views are always necessary; 2020 is the deposit date.

**ESA-S004 — An Introduction to Software Architecture.** David Garlan; Mary Shaw. Date: 1994-01; CMU/SEI-94-TR-021 / CMU-CS-94-166; related 1993 chapter. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §3 styles, associated advantages/disadvantages; heterogeneous architectures and examples. Inspected support: Styles constrain components, connectors and composition; different styles protect different properties and can be combined.

Location: https://www.cse.msu.edu/~cse870/Materials/Design/intro_softarch-Garlan-Shaw.pdf.

Evidence limit: Examples explain mechanisms, not independent replications or a requirement for stylistic purity.

**ESA-S005 — The structure of the ‘THE’-multiprogramming system.** Edsger W. Dijkstra. Date: 1968-05; CACM 11(5), 341–346; 2006 transcription of EWD196. Access: FULL_TEXT, 2026-09-06.

Locator: Hierarchy of abstract machines; system construction and concluding qualifications. Inspected support: Layered abstractions support staged construction and reasoning in the reported operating-system project.

Location: https://www.cs.utexas.edu/~EWD/transcriptions/EWD01xx/EWD196.html.

Evidence limit: Small specialised team; acknowledged unfinished tests and peripheral-device difficulties. The author’s confidence is not independent verification.

**ESA-S006 — Designing Software for Ease of Extension and Contraction.** David L. Parnas. Date: 1979-03; IEEE TSE SE-5(2), 128–138. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §IV-D uses relation; hierarchical subsets; concluding limits. Inspected support: Semantic uses relations differ from invocation, and useful family subsets depend on requirements and abstraction choices.

Location: https://www.dre.vanderbilt.edu/~schmidt/PDF/family.pdf.

Evidence limit: The proposed relation assumes knowledge of correctness dependencies; acyclicity alone is not evidence of valuable product variants.

**ESA-S007 — Mass Produced Software Components.** M. Douglas McIlroy. Date: 1968-10; 1968 NATO conference contribution; report published 1969, §8.2 pp. 138–155; author transcription 1998-10-15. Access: PARTIAL_FULL_TEXT, 2026-09-06.

Locator: Author transcription front matter, abstract and opening proposal. Inspected support: Component families and disciplined reusable production were explicit early ambitions, including quality and cost concerns.

Location: https://www.cs.dartmouth.edu/~doug/components.txt.

Evidence limit: Opening and provenance inspected; no claim that the industrial vision was achieved. Physical-component analogy is not empirical validation.

**ESA-S008 — No Silver Bullet—Essence and Accidents of Software Engineering.** Frederick P. Brooks, Jr.. Date: 1986-09; UNC Technical Report TR86-020; not the later magazine edition. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Complexity/conformity/changeability/invisibility; §§5.2–5.3 requirements refinement, prototyping and growing software. Inspected support: Software’s design burdens are not removed by one technique; iterative clarification and incremental growth are compatible with architectural reasoning.

Location: https://www.cs.unc.edu/techreports/86-020.pdf.

Evidence limit: Time-bounded forecast and experienced argument, not a permanent impossibility theorem. The 1975 book was not inspected.

**ESA-S009 — A Rational Design Process: How and Why to Fake It.** David L. Parnas; Paul C. Clements. Date: 1986-02; IEEE TSE 12(2). Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §II real design difficulties; §III rational process; documentation discussion. Inspected support: A rational explanation can be reconstructed for understanding even when discovery was non-linear.

Location: https://www.cs.tufts.edu/~nr/cs257/archive/david-parnas/fake-it.pdf.

Evidence limit: Normative argument, not permission to falsify history or evidence; documentation benefit is not measured by quantity.

**ESA-S010 — Who Needs an Architect?.** Martin Fowler. Date: 2003-07; IEEE Software 20(4), July/August, pp. 2–4. Access: FULL_TEXT, 2026-09-06.

Locator: Entire three-page essay: competing definitions, architect roles and cost of change. Inspected support: Architectural significance varies with consequences and expertise; architects can enable change rather than centralise every decision.

Location: https://martinfowler.com/ieeeSoftware/whoNeedsArchitect.pdf.

Evidence limit: Reasoned practitioner essay; “important” and “hard to change” are contested formulations, not universal definitions.

**ESA-S011 — ISO/IEC/IEEE 42010:2022, Software, systems and enterprise—Architecture description.** ISO; IEC; IEEE. Date: 2022-11; Second edition. Access: PUBLIC_ABSTRACT_AND_PREVIEW_ONLY, 2026-09-06.

Locator: Official abstract; preview foreword, introduction and scope. Inspected support: The standard concerns architecture descriptions; second-edition changes include entity-of-interest and revised description concepts.

Location: https://www.iso.org/standard/74393.html; https://webstore.ansi.org/preview-pages/iso/preview_iso%2Biec%2Bieee%2B42010-2022.pdf.

Evidence limit: Normative clauses outside the preview were not inspected; no clause-by-clause compliance or quality certification is asserted. Catalogue checked at cut-off.

**ESA-S012 — ISO/IEC/IEEE 42010:2011, Systems and software engineering—Architecture description.** ISO; IEC; IEEE. Date: 2011; First joint ISO/IEC/IEEE edition. Access: PUBLIC_ABSTRACT_ONLY, 2026-09-06.

Locator: Official title, scope and edition/supersession metadata. Inspected support: 2011 is a distinct predecessor edition of the architecture-description standard.

Location: https://www.iso.org/standard/50508.html.

Evidence limit: Normative text not inspected; metadata supports history and stated scope only.

**ESA-S013 — ISO/IEC/IEEE 42010 Update.** Richard Martin. Date: 2022-01-30; INCOSE International Workshop working-group presentation; pre-publication account. Access: FULL_TEXT_TARGETED_SLIDES, 2026-09-06.

Locator: Slides 3–5: history, scope and then-proposed revision. Inspected support: Working-group history links IEEE 1471 and the 2011 and developing 2022 editions.

Location: https://www.omgwiki.org/MBSE/lib/exe/fetch.php?media=mbse:incose_mbse_iw_2022:iw2022_iso_iec_ieee_42010_update.pdf.

Evidence limit: Draft-development account is not final normative wording; used for genealogy only.

**ESA-S014 — A Classification and Comparison Framework for Software Architecture Description Languages.** Nenad Medvidovic; Richard N. Taylor. Date: 2000-01; IEEE TSE 26(1), 70–93. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Taxonomy of components, connectors and configurations; capabilities and comparison. Inspected support: ADLs are differentiated by semantic and analytical capabilities, not simply by graphical appearance.

Location: https://ics.uci.edu/~taylor/documents/2000-ADLs-TSE.pdf; https://doi.org/10.1109/32.825767.

Evidence limit: Classification of research languages is not industrial effectiveness evidence. Its historical tool capabilities are not current-version claims.

**ESA-S015 — A Formal Basis for Architectural Connection.** Robert Allen; David Garlan. Date: 1998-06; Author revision of the July 1997 TOSEM work; revision kept distinct. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §4 ports/roles/glue; §8 compatibility counterexample and Theorem 1; §9 analysis tools. Inspected support: Compatibility alone does not preserve connector deadlock freedom; conservatism and deadlock-free connector assumptions matter.

Location: https://www.cs.cmu.edu/afs/cs/project/able/ftp/wright-tosem97-revision/wright-tosem97-revision.pdf.

Evidence limit: Guarantee is inside the CSP model; implementation correspondence and environmental assumptions require separate evidence. Finite-state checks face model-size limits.

**ESA-S016 — Illuminating the Fundamental Contributors to Software Architecture Quality.** Felix Bachmann; Len Bass; Mark Klein. Date: 2002-08; CMU/SEI-2002-TR-025. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §§3.1–3.5 scenarios and quality models; §§4.1–4.3 tactic reasoning. Inspected support: Tactics affect parameters of quality models, and measurable scenarios give those effects a context.

Location: https://www.sei.cmu.edu/documents/689/2002_005_001_14063.pdf.

Evidence limit: Causal modelling guidance, not guarantees that every tactic improves a deployed system; affected-module counts are proxies for modification effort.

**ESA-S017 — Quality Attribute Workshops (QAWs), Third Edition.** Mario Barbacci; Robert Ellison; Anthony Lattanze; Judith Stafford; Charles Weinstock; William Wood. Date: 2003-08; Third edition; report cover date, distinct from later web posting. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §§3.5–3.8 generation, prioritisation and six-part refinement; scope of third edition. Inspected support: Stakeholders generate and refine prioritised quality scenarios before detailed architecture is available.

Location: https://people.computing.clemson.edu/~johnmc/courses/cpsc875/resources/qaw.pdf.

Evidence limit: Workshop voting and time limits can omit minority or rare conditions; agreement does not validate operating quality. Third edition narrows the method’s purpose.

**ESA-S018 — Linking Usability to Software Architecture Patterns through General Scenarios.** Len Bass; Bonnie E. John. Date: 2003; Journal of Systems and Software author preprint. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Introduction; scenario construction and affinity analysis; architectural implications. Inspected support: Some usability concerns affect architectural mechanisms beyond separating interface code from application logic.

Location: https://www.cs.cmu.edu/~bej/usa/publications/JSS-U&SA.pdf; https://doi.org/10.1016/S0164-1212(02)00076-6.

Evidence limit: Scenario/pattern construction, not representative user-outcome comparison; scenarios without substantive architectural consequences were removed. Preprint contains production placeholders.

**ESA-S019 — SAAM: A Method for Analyzing the Properties of Software Architectures.** Rick Kazman; Len Bass; Gregory Abowd; Mike Webb. Date: 1994; ICSE 1994, pp. 81–90; later SEI-hosted copy. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Scenario-based comparison, functional partitioning, change interaction and Serpent example. Inspected support: Change scenarios expose the architectural consequences of modifications and competing decompositions.

Location: https://www.sei.cmu.edu/documents/150/2007_019_001_29297.pdf.

Evidence limit: Example-based demonstration; 2007 in the URL is not the original publication date. No downstream causal benefit estimate.

**ESA-S020 — ATAM: Method for Architecture Evaluation.** Rick Kazman; Mark Klein; Paul Clements. Date: 2000-08; CMU/SEI-2000-TR-004. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §7 risks, non-risks, sensitivity and trade-off points; §8 method steps. Inspected support: ATAM identifies assumption-bound architectural risks and trade-offs; a non-risk must be reconsidered when assumptions change.

Location: https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf.

Evidence limit: Structured review does not establish complete scenario coverage, operating correctness or universal return on evaluation cost.

**ESA-S021 — A Study of Architecture Risk Themes.** Len Bass; Robert Nord; William Wood; David Zubrow. Date: 2006-09; CMU/SEI-2006-TR-012. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Study population, coding of themes, results and limitations. Inspected support: Risk themes often concern omissions; associations with business goals or domains were not demonstrated in this dataset.

Location: https://www.sei.cmu.edu/documents/771/2006_005_001_14783.pdf.

Evidence limit: Outputs of evaluations, not observed future failure rates or a causal comparison of ATAM with no review. Related later publication shares evidence.

**ESA-S022 — Using Economic Considerations to Choose Amongst Architecture Design Alternatives.** Jai Asundi; Rick Kazman; Mark Klein. Date: 2001-12; CMU/SEI-2001-TR-035. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §4 utility/cost ranges, sensitivity and dependencies; additive-utility appendix. Inspected support: Economic selection depends on elicited utility, uncertain costs and interactions between strategies.

Location: https://www.sei.cmu.edu/documents/670/2001_005_001_13916.pdf.

Evidence limit: Stakeholder utility is not objective money or social welfare; additive assumptions and infeasible combinations must be examined. Case results are not used as independent benefit estimates.

**ESA-S023 — Evaluating Software Architecture Evaluation Methods: An Internal Replication.** Silvia Abrahão; Emilio Insfran. Date: 2017; EASE 2017, pp. 144–153. Access: FULL_TEXT_AUTHOR_UPLOAD, 2026-09-06.

Locator: Experiment design, participant selection, outcomes and threats to validity. Inspected support: The comparison favoured QuaDAI on some measures but did not demonstrate efficiency or ease-of-use superiority.

Location: https://www.researchgate.net/publication/316701760_Evaluating_Software_Architecture_Evaluation_Methods_An_Internal_Replication; https://doi.org/10.1145/3084226.3084253.

Evidence limit: Sixteen inexperienced practitioner-students, short tasks and author reference solutions; same materials/researchers as earlier student experiments, hence internal replication only.

**ESA-S024 — Attribute-Driven Design (ADD), Version 2.0.** Rob Wojcik; Felix Bachmann; Len Bass; Paul Clements; Paulo Merson; Robert Nord; Bill Wood. Date: 2006-11; CMU/SEI-2006-TR-023. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §3 inputs/outputs; §4 eight steps, architectural drivers, allocation and interfaces. Inspected support: Prioritised drivers guide recursive design, interface definition and verification/refinement of child requirements.

Location: https://www.sei.cmu.edu/documents/775/2006_005_001_14795.pdf.

Evidence limit: Prescribed method revised in response to learning difficulties; not a controlled effectiveness comparison or mandatory recursion depth.

**ESA-S025 — A General Model of Software Architecture Design Derived from Five Industrial Approaches.** Christine Hofmeister; Philippe Kruchten; Robert L. Nord; Henk Obbink; Alexander Ran; Pierre America. Date: 2007; JSS 80, 106–126; online 2006-07-05. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §1 five approaches; §3 analysis/synthesis/evaluation and their interleaving. Inspected support: A common account permits interleaved analysis, synthesis and evaluation rather than a predictable one-pass sequence.

Location: https://courses.ece.ubc.ca/417/public/Hofmeister.pdf; https://doi.org/10.1016/j.jss.2006.05.024.

Evidence limit: Method authors synthesise selected approaches; no independent randomised comparison. The general design model explicitly draws on Gero’s FBS work.

**ESA-S026 — Architectural Mismatch: Why Reuse Is So Hard.** David Garlan; Robert Allen; John Ockerbloom. Date: 1995-11; IEEE Software 12(6), 17–26; journal version. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Aesop integration account; assumptions about components, connectors, topology and construction. Inspected support: Apparently compatible reusable parts can disagree about control, data and surrounding structure.

Location: https://john.cs.olemiss.edu/~hcc/csci658/notes/localcopy/ArchitecturalMismatch.pdf.

Evidence limit: One industrial/research construction programme; the distinct ICSE paper and later retrospective are not additional independent failures.

**ESA-S027 — A Survey on Architecture Design Rationale.** Antony Tang; Muhammad Ali Babar; Ian Gorton; Jun Han. Date: 2005-05-31; SUTICT-TR2005.02 / SUT.CeCSES-TR008; inspected report, not 2006 journal version. Access: FULL_TEXT_AUTHOR_UPLOAD, 2026-09-06.

Locator: Report title page; survey findings and validity limitations. Inspected support: Practitioners report rationale’s value and obstacles to recording and using it.

Location: https://www.researchgate.net/publication/222665704_A_survey_of_architecture_design_rationale.

Evidence limit: Landing page names the later 2006 article; actual inspected full text is the 2005 report. Self-reported value is not measured causal maintenance benefit.

**ESA-S028 — Software Architecture as a Set of Architectural Design Decisions.** Anton Jansen; Jan Bosch. Date: 2005; WICSA 2005 contribution; institutional publication record carries 2006 metadata. Access: ABSTRACT_ONLY, 2026-09-06.

Locator: Institutional abstract and bibliographic record. Inspected support: Architecture can be analysed as connected design decisions; loss of decision knowledge motivates the approach.

Location: https://research.rug.nl/en/publications/software-architecture-as-a-set-of-architectural-design-decisions/.

Evidence limit: Full Archium methods and evaluation not inspected. Date ambiguity is preserved rather than inventing an edition reconciliation.

**ESA-S029 — Documenting Architecture Decisions.** Michael Nygard. Date: 2011-11-15; Original practitioner article. Access: FULL_TEXT, 2026-09-06.

Locator: Whole article: context, decision, status, consequences and supersession. Inspected support: Short records preserve significant decisions and their changing status for later readers.

Location: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions.

Evidence limit: Small-team practice report, not a causal trial. A compulsory alternatives field is an analytical extension here, not attributed to the original template.

**ESA-S030 — How Do Committees Invent?.** Melvin E. Conway. Date: 1968-04; Datamation article; author web transcription includes a much later preface. Access: FULL_TEXT, 2026-09-06.

Locator: Original article’s communication argument, design interfaces and organisational incentives; preface distinguished. Inspected support: Organisation and design interaction can constrain each other through communication requirements.

Location: https://www.melconway.com/research/committees.html.

Evidence limit: Not a deterministic empirical law; communication networks are not identical to organisation charts and the argument has assumptions.

**ESA-S031 — Socio-technical Congruence: A Framework for Assessing the Impact of Technical and Work Dependencies on Software Development Productivity.** Marcelo Cataldo; James D. Herbsleb; Kathleen M. Carley. Date: 2008; ESEM 2008. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Research setting, dependency/congruence measures, regression results and validity discussion. Inspected support: Coordination aligned with work dependencies is associated with shorter modification-request resolution in the studied organisation.

Location: https://herbsleb.org/web-pubs/pdfs/cataldo-socio-2008.pdf; https://doi.org/10.1145/1414004.1414008.

Evidence limit: Association, not experimentally identified causal effect; recorded coordination omits channels and logical dependencies are constructed from changes.

**ESA-S032 — Exploring the Duality between Product and Organizational Architectures: A Test of the “Mirroring” Hypothesis.** Alan MacCormack; John Rusnak; Carliss Baldwin. Date: 2011; HBS working paper 08-039; inspected cover copyrights 2007, 2008, 2011. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Matched-product selection, dependency-structure analysis and limitations. Inspected support: Matched product comparisons connect development organisation with measured dependency structure.

Location: https://www.hbs.edu/ris/Publication%20Files/08-039_1861e507-1dc1-4602-85b8-90d71559d85b.pdf.

Evidence limit: Five matched product families; overlapping operating-system comparisons are not extra independent pairs. C call-graph propagation proxies and selection prevent deterministic causal inference.

**ESA-S033 — Domain-Driven Design Reference: Definitions and Pattern Summaries.** Eric Evans. Date: 2015-03; Reference booklet, not the original 2003 monograph. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Bounded Context and Context Map, printed pp. 28–29; strategic-design relationships. Inspected support: A domain model has a bounded context; relations between models and teams require explicit mapping.

Location: https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf.

Evidence limit: 2016 URL upload is not publication date. Domain semantic boundaries do not imply one deployable microservice per context. Outcome effectiveness not tested here.

**ESA-S034 — Architectural Styles and the Design of Network-based Software Architectures, Chapter 5: Representational State Transfer.** Roy Thomas Fielding. Date: 2000; Doctoral dissertation, chapter 5. Access: FULL_TEXT_TARGETED_CHAPTER, 2026-09-06.

Locator: §5.1 derivation of constraints; §5.2 architectural elements. Inspected support: REST derives a specialised distributed-hypermedia style from interacting constraints rather than a service branding label.

Location: https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm.

Evidence limit: Argument is scoped to its architectural context; uniform-interface and stateless-interaction trade-offs are not requirements for every application. Chapter inspection does not cover the whole dissertation.

**ESA-S035 — Reference Model for Service Oriented Architecture 1.0.** OASIS SOA Reference Model Technical Committee. Date: 2006-10-12; OASIS Standard, version 1.0. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §3.2 visibility and interaction; action/process models and real-world effects; service descriptions. Inspected support: Visibility, interaction and consequences distinguish a service relationship from a mere named endpoint.

Location: https://docs.oasis-open.org/soa-rm/v1.0/soa-rm.pdf.

Evidence limit: Reference-model definitions are not comparative evidence. Visibility and willingness do not automatically authorise every action or establish that the promised consequence occurs.

**ESA-S036 — Microservices.** James Lewis; Martin Fowler. Date: 2014-03; Original architectural-style practitioner article. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Characteristics, decentralised governance, operational implications and evolutionary design. Inspected support: Microservice practice combines independently deployable services with operational and organisational responsibilities.

Location: https://martinfowler.com/articles/microservices.html.

Evidence limit: Popularisation, not proof of first invention or universal advantage. Reported practices are not an independent effectiveness trial.

**ESA-S037 — Monolith First.** Martin Fowler. Date: 2015-06; Practitioner essay. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Boundary discovery, microservice premium and qualifications/counterpositions. Inspected support: A simpler initial deployment may allow domain and boundary learning before costly distribution.

Location: https://martinfowler.com/bliki/MonolithFirst.html.

Evidence limit: Experienced judgement, not a universal causal law; circumstances favouring services from the start are not ruled out.

**ESA-S038 — Deconstructing the Monolith: Designing Software that Maximizes Developer Productivity.** Kirsten Westeinde; Shopify Engineering. Date: 2019-02-21; Historical engineering account. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Modular-monolith approach and motivation. Inspected support: Modularisation inside a monolith is a documented alternative to distributing every component.

Location: https://shopify.engineering/deconstructing-monolith-designing-software-maximizes-developer-productivity.

Evidence limit: Company-authored account; no controlled productivity effect is inferred from the title or selected experience. Not a claim about Shopify’s current architecture.

**ESA-S039 — Introducing istiod: simplifying the control plane.** Istio project authors. Date: 2020; Istio 1.5 control-plane consolidation account. Access: FULL_TEXT, 2026-09-06.

Locator: Reasons for consolidation and retained separation from the Envoy data plane. Inspected support: Shared scaling, release, language and administrative needs weakened the case for separate control-plane services.

Location: https://istio.io/latest/blog/2020/istiod/.

Evidence limit: Historical version-specific account, not an independent cost comparison or proof that all microservices should merge.

**ESA-S040 — Strangler Fig Application.** Martin Fowler. Date: 2024-08-22; Substantially revised article with 2004 original-post ancestry. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Incremental replacement argument and revision note. Inspected support: Replacement can proceed by progressively redirecting behaviour while old and new parts coexist.

Location: https://martinfowler.com/bliki/StranglerFigApplication.html.

Evidence limit: Current text is a 2024 revision, not verbatim 2004 evidence. Coexistence, data compatibility and retirement costs are not eliminated by the metaphor.

**ESA-S041 — Big Ball of Mud.** Brian Foote; Joseph Yoder. Date: 1997; PLoP 1997 ancestry; 2000 book version; web document last modified 2012-11-21. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Introduction and forces; throwaway code, piecemeal growth, keeping it working. Inspected support: Expediency and organisational conditions can rationally explain structures that violate tidy architectural ideals.

Location: https://www.laputan.org/mud/mud.html.

Evidence limit: Pattern argument and collected experience, not a measured prevalence survey. Describing a force does not prove an unstructured design is optimal.

**ESA-S042 — Don’t Let Architecture Astronauts Scare You.** Joel Spolsky. Date: 2001-04-21; Practitioner polemic. Access: FULL_TEXT, 2026-09-06.

Locator: Whole essay on abstraction detached from concrete user problems. Inspected support: Architectural rhetoric can evade the useful problem rather than solve it.

Location: https://www.joelonsoftware.com/2001/04/21/dont-let-architecture-astronauts-scare-you/.

Evidence limit: Polemical criticism, not an industrial comparison or evidence that all abstraction is waste.

**ESA-S043 — Architectural Fitness Functions / Fitness Function Katas.** Neal Ford; Rebecca Parsons; Patrick Kua and companion-site contributors. Date: UNDATED; Author companion site, inspected snapshot 2026-09-06. Access: FULL_TEXT, 2026-09-06.

Locator: Definition, evolution-computing analogy and interacting-characteristic examples. Inspected support: Fitness functions assess architectural characteristics and can expose conflicting changes.

Location: https://evolutionaryarchitecture.com/ffkatas/index.html.

Evidence limit: Book ancestry is attributed, not a claim that all editions were read; the web page supplies no causal comparative evidence. Analogy is not a biological guarantee.

**ESA-S044 — Fitness Function-Driven Development.** Paula Paul; Rosemary Wang. Date: 2019-01-11; Thoughtworks practitioner article. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Fitness functions, feedback, examples and revisiting goals. Inspected support: Continuous checks can expose architecture-relevant changes earlier when the tests remain aligned with intended qualities.

Location: https://www.thoughtworks.com/en-us/insights/articles/fitness-function-driven-development.

Evidence limit: Vendor guidance; illustrative thresholds and approval counts are not general engineering requirements. Automated proxies can be misleading.

**ESA-S045 — Software Reflexion Models: Bridging the Gap between Source and High-Level Models.** Gail C. Murphy; David Notkin; Kevin Sullivan. Date: 1995-10; FSE 1995, pp. 18–28. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Reflexion construction, mapping and interpretation; §6 formalisation and case examples. Inspected support: Mapped source relations are compared with a high-level model to expose convergences, divergences and absences for human interpretation.

Location: https://www.cs.ubc.ca/~murphy/papers/rm/reflexion_model_fse95.pdf; https://doi.org/10.1145/222132.222136.

Evidence limit: Formal comparison is relative to chosen mapping and relation extraction; case scale is not proof of semantic completeness.

**ESA-S046 — Symptoms of Architecture Erosion in Code Reviews: A Study of Two OpenStack Projects.** Ruiyin Li; Mohamed Soliman; Peng Liang; Paris Avgeriou. Date: 2022-01; arXiv:2201.01184 author manuscript. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Study selection/coding; symptoms, responses and limitations. Inspected support: Review discussions reveal erosion symptoms and different responses, not just automatic correction.

Location: https://arxiv.org/pdf/2201.01184.

Evidence limit: Comment selection cannot estimate the true prevalence of harmful erosion; overlaps with later erosion-classifier datasets must not be counted as independent replication.

**ESA-S047 — Towards Automated Identification of Violation Symptoms of Architecture Erosion.** Ruiyin Li and co-authors. Date: 2025-08-22; arXiv:2306.08616v5; original preprint 2023. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Dataset construction; classifiers/LLM combinations; evaluation and limitations. Inspected support: Text classifiers may help locate review comments about violations, but detection requires validation beyond benchmark scores.

Location: https://arxiv.org/html/2306.08616v5.

Evidence limit: Four-project comments from 2014–2020, not a 2025 production cohort; balanced training/test sample changes base rates and shares prior study material.

**ESA-S048 — Impact of Architectural Smells on Software Performance: an Exploratory Study.** Francesca Arcelli Fontana; Matteo Camilli; Davide Rendina; Andrei Gabriel Taraboi; Catia Trubiani. Date: 2023; EASE author preprint; stale generic proceedings footer not treated as publication date. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Refactoring/setup; performance results; threats to validity. Inspected support: Selected smell-removing refactorings can affect performance, with heterogeneous and null effects.

Location: https://cs.gssi.it/catia.trubiani/download/2023-EASE-Impact-of-Architectural-Smells-on-Software-Performance-preprint.pdf.

Evidence limit: Two systems and selected method timings do not establish that every smell is harmful or that removal improves whole-application throughput.

**ESA-S049 — The WyCash Portfolio Management System.** Ward Cunningham. Date: 1992-03-26; OOPSLA 1992 experience-report text. Access: FULL_TEXT, 2026-09-06.

Locator: Entire experience account, incremental growth and debt metaphor. Inspected support: The debt metaphor concerns the need to consolidate understanding as software grows, not a universal label for imperfection.

Location: https://c2.com/doc/oopsla92.html.

Evidence limit: One first-person development account; no quantified principal/interest model or general causal estimate.

**ESA-S050 — Architecture Technical Debt: Understanding Causes and a Qualitative Model.** Antonio Martini; Jan Bosch; Michel Chaudron. Date: 2014; SEAA 2014, pp. 85–92. Access: FULL_TEXT_AUTHOR_UPLOAD_TARGETED, 2026-09-06.

Locator: Research approach; causal/qualitative model; reported limitations. Inspected support: Architecture debt arises through interacting organisational and technical pressures and requires diagnosis rather than indiscriminate clean-up.

Location: https://www.researchgate.net/publication/265822240_Architecture_Technical_Debt_Understanding_Causes_and_a_Qualitative_Model.

Evidence limit: Seven sites in five large Scandinavian companies; qualitative accounts do not supply monetary interest rates. Later reports may extend the same programme.

**ESA-S051 — Architecture-Based Runtime Software Evolution.** Peyman Oreizy; Nenad Medvidovic; Richard N. Taylor. Date: 1998-04; ICSE 1998, pp. 177–186. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Architectural runtime model, change specification and implementation approach. Inspected support: Architecture-level representations and explicit connectors can support changes while a system runs.

Location: https://www.ics.uci.edu/~peymano/papers/ICSE98.pdf.

Evidence limit: Prototype and proposed change machinery, not proof that arbitrary runtime changes are safe or worthwhile.

**ESA-S052 — An Architecture-Based Approach to Self-Adaptive Software.** Peyman Oreizy; Michael M. Gorlick; Richard N. Taylor; Dennis Heimbigner; Gregory Johnson; Nenad Medvidovic; Alex Quilici; David S. Rosenblum; Alexander L. Wolf. Date: 1999-05; IEEE Intelligent Systems 14(3), 54–62. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Adaptation spectrum; observation/assessment/change; costs and scenario. Inspected support: Adaptation requires observations, decisions and executable changes, with explicit costs and environmental limits.

Location: https://ics.uci.edu/~peymano/papers/ieee-is99.pdf.

Evidence limit: The UAV scenario is illustrative, not evidence of an operational deployment. Mechanism proposal is not a general assurance result.

**ESA-S053 — Rainbow: Architecture-Based Self-Adaptation with Reusable Infrastructure.** Shang-Wen Cheng; An-Cheng Huang; David Garlan; Bradley Schmerl; Peter Steenkiste. Date: 2004; ICAC 2004 author full text; distinct from the Computer article of similar title. Access: FULL_TEXT_AUTHOR_UPLOAD_TARGETED, 2026-09-06.

Locator: ICAC title/authors/footer; §2 probes, gauges, model, strategy and effectors; §3 case introduction. Inspected support: Reusable infrastructure must be specialised with system knowledge and translations between runtime observations/actions and architecture.

Location: https://www.researchgate.net/publication/2956204_Rainbow_architecture-based_self-adaptation_with_reusable_infrastructure.

Evidence limit: Host-page metadata resembles the Computer article; only the inspected ICAC text is used. Case feasibility is not universal autonomous operation.

**ESA-S054 — Robustness Evaluation of the Rainbow Framework for Self-Adaptation.** Javier Cámara; Rogério de Lemos; Nuno Laranjeiro; Rafael Ventura; Marco Vieira. Date: 2014; SAC 2014. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Experimental setup; probe-input mutation; failure classification and results. Inspected support: Malformed or unexpected observations can silently corrupt architectural adaptation state.

Location: https://www-users.york.ac.uk/~jcm567/files/SAC2014.pdf; https://doi.org/10.1145/2554850.2554935.

Evidence limit: Injected-test proportions are not deployment failure frequencies; two applications share the same framework and constrained test environments.

**ESA-S055 — Self-Adaptation in Industry: A Survey.** Danny Weyns; Ilias Gerostathopoulos and co-authors. Date: 2023; TAAS author manuscript hosted by a co-author. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Recruitment and demographics; practitioner responses; threats to validity. Inspected support: Industrial self-adaptation includes bounded resource/configuration changes and faces assurance and trust concerns.

Location: https://iliasger.github.io/pubs/2023-TAAS-SASinINDUSTRY.pdf.

Evidence limit: Non-probabilistic recruitment and survey framing constrain representativeness; author-manuscript template volume data are not treated as final issue metadata.

**ESA-S056 — Hidden Technical Debt in Machine Learning Systems.** D. Sculley; Gary Holt; Daniel Golovin; Eugene Davydov; Todd Phillips; Dietmar Ebner; Vinay Chaudhary; Michael Young; Jean-François Crespo; Dan Dennison. Date: 2015; NIPS 2015, pp. 2503–2511. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §§1–4 entanglement, data dependencies, undeclared consumers and feedback loops. Inspected support: Learned behaviour creates consequential data and feedback dependencies beyond ordinary code interfaces.

Location: https://papers.neurips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems.pdf.

Evidence limit: Experienced engineering analysis, not controlled ML-versus-non-ML architecture comparison; no universal debt frequency or cost estimate.

**ESA-S057 — Cloud Programming Simplified: A Berkeley View on Serverless Computing.** Eric Jonas and co-authors. Date: 2019-02-09; arXiv:1902.03383v1. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Definitions; §§3.3–3.4 communication/storage/coordination; challenges and predictions. Inspected support: Serverless changes resource and service boundaries while leaving storage, communication and coordination constraints.

Location: https://arxiv.org/pdf/1902.03383.

Evidence limit: 2019 provider behaviour and predictions are historical, not current limits/prices or proof that serverless is superior.

**ESA-S058 — Injecting Sustainability in Software Architecture: A Rapid Review.** Markus Funke; Patricia Lago. Date: 2025-11-27; arXiv:2512.00106v1; later workshop template not final publication evidence. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Rapid-review protocol, practitioner focus group, findings and threats. Inspected support: Sustainability introduces measurement, decision and coordination concerns not exhausted by a single energy metric.

Location: https://arxiv.org/html/2512.00106v1.

Evidence limit: Rapid-review search and screening constraints; practitioner opinions are not carbon-impact measurements. Secondary evidence is not counted as independent replication of included work.

**ESA-S059 — Towards Supporting Quality Architecture Evaluation with LLM Tools.** Rafael Capilla and co-authors. Date: 2026-03-30; arXiv:2603.28914v1. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Study setup, risk comparison, results and threats. Inspected support: LLM support can propose architecture-evaluation material, but its usefulness depends on context and human validation.

Location: https://arxiv.org/html/2603.28914v1.

Evidence limit: Undergraduate course, author reference judgements and small selected group population; neither industrial replication nor autonomous approval evidence.

**ESA-S060 — Insights on Microservice Architecture Through the Eyes of Industry Practitioners.** Vinicius L. Nogueira; Fernando S. Felizardo; Aline M. M. M. Amaral; Wesley K. G. Assunção; Thelma E. Colanzi. Date: 2024-08-19; arXiv:2408.10434v1. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §III methods; §IV data/coordination challenges; §VI threats. Inspected support: Practitioners describe deployment/scaling motivations alongside data-consistency, testing and coordination burdens.

Location: https://arxiv.org/html/2408.10434v1.

Evidence limit: 53 microservice users include 35 from a prior survey plus 18 new users; two new questions have only 18 answers. Motivation is not measured achieved benefit.

**ESA-S061 — EcoFaaS: Rethinking the Design of Serverless Environments for Energy Efficiency.** Jovan Stojkovic; Nikoleta Iliakopoulou; Tianyin Xu; Hubertus Franke; Josep Torrellas. Date: 2024; ISCA 2024 author paper. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: §§V–VIII; Table I and Figures 13–18 visually inspected. Inspected support: Energy-aware core pools and end-to-end latency budgets improve selected energy/tail measures while intentionally increasing mean latency relative to the full-frequency baseline.

Location: https://tianyin.github.io/pub/ecofaas.pdf; https://doi.org/10.1109/ISCA59077.2024.00042.

Evidence limit: Five-to-twenty Haswell servers and selected benchmarks; measured package/DRAM energy is not whole-lifecycle carbon. Results are mainly shown for OpenWhisk, with KNative described as similar.

**ESA-S062 — An Empirical Evaluation of Large Language Models Applying Software Architectural Patterns.** Christos Hadjichristofi; Michail Tsilimigkounakis; Georgios Sotiropoulos; Vassilios Vescoukis. Date: 2026-05-27; AI 7(6), 195; publisher full text mirrored on ResearchGate. Access: PUBLISHED_ARTICLE_FULL_TEXT_VIA_AUTHOR_UPLOAD, 2026-09-06.

Locator: §3 design; §4 architectural/metric findings; §5 threats. Inspected support: Generated diagrams and self-reported architectural metrics require separate validation; the latter can disagree with the generated structure.

Location: https://www.researchgate.net/publication/405351366_An_Empirical_Evaluation_of_Large_Language_Models_Applying_Software_Architectural_Patterns; https://doi.org/10.3390/ai7060195.

Evidence limit: Each configuration was run once; four author evaluators; structural outputs are not running systems. Published 27 May, not the later hosting/upload date.

**ESA-S063 — From Monolith to Microservices: A Comparative Evaluation of Decomposition Frameworks.** Mineth Weerasinghe; Himindu Kularathne; Methmini Madhushika; Danuka Lakshan; Nisansa de Silva; Adeesha Wijayasiri; Srinath Perera. Date: 2026-01-30; arXiv:2601.23141v1. Access: FULL_TEXT_TARGETED_SECTIONS, 2026-09-06.

Locator: Study design and benchmark/metric comparison; limitations implicit in reproduced versus reported results. Inspected support: Automated boundary proposals can be compared on structural proxies, which do not establish operational independence.

Location: https://arxiv.org/html/2601.23141v1.

Evidence limit: Mixes reproduced outputs with published results; shared benchmark families and metrics are not independent industrial deployments.

**ESA-S064 — On the Design and Development of Program Families.** David L. Parnas. Date: 1976; Historical work identified through later collected reprint metadata. Access: METADATA_ONLY, 2026-09-06.

Locator: Title/date and reprint identification. Inspected support: Program-family research predates the 1979 extension/contraction paper.

Location: https://link.springer.com/chapter/10.1007/978-1-4612-6315-9_25.

Evidence limit: Full original text not inspected. Substantive family mechanisms in this packet rely on ESA-S006, not an invented reading of this work.

**ESA-S065 — IEEE 1471-2000: Recommended Practice for Architectural Description of Software-Intensive Systems.** IEEE. Date: 2000; Original IEEE recommended practice. Access: PUBLIC_ABSTRACT_ONLY, 2026-09-06.

Locator: Official description of conceptual framework and architectural descriptions. Inspected support: The original standard formalises architecture-description concepts and content.

Location: https://standards.ieee.org/standard/1471-2000.html.

Evidence limit: Normative clauses inaccessible in this run; scope and historical identity only. No assumed conformance checklist.

**ESA-S066 — Software Product Lines Collection.** Carnegie Mellon University Software Engineering Institute. Date: UNDATED; Institutional collection snapshot at 2026-09-06. Access: COLLECTION_DESCRIPTIONS_ONLY, 2026-09-06.

Locator: Entries for architecture reconstruction (2001), product-line architecture views/evolution (2007), and service/product-line intersections (2008–2010). Inspected support: The institutional programme explicitly connects product lines with architectural reconstruction, descriptions and service variation.

Location: https://www.sei.cmu.edu/library/software-product-lines-collection/.

Evidence limit: Underlying case reports were not all read; collection descriptions establish documented intersections and discovery leads, not benefits or the contents of uninspected methods.

