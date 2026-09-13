# Evolved Software Product Line Engineering

**Independent tradition study · revision ESPLE-2026-09-06-r1 · research cut-off 6 September 2026**

**Analytical label:** `EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING`. This is the name of this criticism-tested synthesis, not a claim that an academic school with that compound name already exists. The established subject is Software Product Line Engineering (SPLE). The future SSS grouping is provisional and supplies no evidence for this study.

## Executive judgement

The strongest surviving idea is not “reuse as much as possible”. It is **make a defensible family-production commitment, realise it through controlled shared and variable assets, and keep the resulting products and the commitment itself answerable to evidence**. The family must be worth treating as a family. Its selectable distinctions must mean something. Its production mechanism must actually realise those distinctions. Its assurance claims must identify what was checked. Its supported products must survive, or be explicitly migrated through, changes to shared knowledge and assets. These responsibilities are coupled, but their implementation does not require one fixed process, representation, team structure or toolchain. This is the study's synthesis of the family-design, domain-engineering, industrial-production and assurance branches, not a single proposition proved by any one source. [ESPLE-S003; ESPLE-S005; ESPLE-S007; ESPLE-S009; ESPLE-S011; ESPLE-S019]

This judgement is conditional in two important ways. First, a product line can be technically coherent yet economically inferior to independent products, selective reuse or clone-and-own. Second, a powerful mechanism can be justified only in a restricted domain: variability-aware analysis requires a faithful supported representation; dynamic supervisory control requires a suitable model of states, events and control; feature-model migration does not automatically preserve product behaviour. A complete method cannot resolve these restrictions by simply demanding all the mechanisms at once. Its coherence lies in the **selection rules, shared boundaries and feedback**, not maximal machinery. [ESPLE-S010; ESPLE-S012; ESPLE-S020; ESPLE-S023; ESPLE-S026; ESPLE-S031; ESPLE-S040]

The examined population contains **62 candidates**. Nine are strongly retained, eighteen retained in evolved form, twelve context-dependent, four domain-specific and four assumption-sensitive. One is useful but easily bureaucratised, one useful but easily gamed, one unresolved, nine rejected or disfavoured, two not general properties and one ceremony rather than a general property. These are primary dispositions, not separate votes or confidence scores. All 62 remain visible, including the adverse judgements. The unresolved candidate concerns the stronger claim that learned regeneration can replace maintained family variability with superior lifecycle adequacy; examination did not establish that claim.

The corpus includes **45 distinct source records**, with full-text, chapter, public-scope, excerpt, abstract and metadata access distinguished. It is a bounded research synthesis, not an exhaustive bibliometric review. The major mandatory questions were examined; unavailable text was not silently counted as read. Research through the cut-off includes published 2025/2026 work, current preprints and the announced 2026 conference arrangements. Publication, deposit, experiment and event dates are kept separate. All evidence comes from external scholarship and issuing bodies; no target repository or sibling research output supplied findings.

## How to use this packet

The explanatory report and its ordered ledgers are the human entry point. `PROPERTY_LEDGER.json` contains the complete records, domain profiles, criticism and ceremony ledgers, internal tensions and evidence-study records. `SOURCE_TABLE.json` identifies exact works, actual inspected claim locators and access limits. `COMPOSITION_MODEL.json` contains the nine domain models, 53 guarded property relations, alternative configurations, genealogy and discriminating cases. `RESEARCH_COVERAGE.json` records the examined scope and search decisions. The three intakes serve different later consumers: a neutral audit, public explanation, and reconciliation with independently researched traditions.

A source citation such as **ESPLE-S021, §6.1** identifies a work and an inspected locator; the source table resolves it to authors, date and URL/DOI. A property citation such as **ESPLE-025** identifies a complete judgement rather than just a slogan. The exact-ID denominator must survive later integration even when one implementation addresses several properties. Source roles remain separate: guidance is not measured effectiveness, a taxonomy is not an adoption survey, a model-level result is not a deployment guarantee, and our analytic response to criticism is not a claim of academic consensus.

## 1. What the tradition is—and what its object changes

SPLE concerns related products engineered through managed commonality and variability, reusable core assets and an approach to deriving particular products. Its distinctive unit is the **family and its production capability**, not merely a single program with options. That does not mean every family requires multiple repositories, a separate platform department or a generator. It means that there is a consequential relationship among product needs, shared investment, intentional differences and a way of producing the intended member of the family. The industrial accounts connect core assets, products and management; the domain/application framework separates responsibilities while retaining feedback. [ESPLE-S008, publisher preface; ESPLE-S009, chapter 2; ESPLE-S011, production-plan development]

The distinction matters because superficially similar practices can have different mechanisms. A library can be reused without a family scope or production plan. A configurable application may instantiate a family if its variations and derived products are deliberately governed, but an inventory of flags alone does not establish that. A roadmap organises intended offerings, not necessarily reusable assets or derivation. A supply chain identifies dependencies and suppliers, not necessarily the commonality and variability of products. An ecosystem may coordinate independently implemented compatible products without one organisation owning a common core. These are useful neighbouring arrangements, not defective versions of one compulsory model. [ESPLE-S009; ESPLE-S011; ESPLE-S029, taxonomy and implications; ESPLE-S044, §§1, 3–5]

The family claim is therefore a hypothesis with consequences. It commits some needs to shared treatment and leaves others variable, local or outside scope. It creates dependencies among products: a common fix can help many members, while a common defect or inappropriate abstraction can affect many. It changes who must communicate with whom. It can exchange repeated local effort for shared investment and coordination. It should be challenged before a technically elaborate model turns the initial hypothesis into an expensive assumption.

## 2. Plural origins rather than a linear ladder

The older reuse and program-family work supplies different parts of the problem. McIlroy's component-production proposal discusses deliberately related components with differing characteristics; the inspected transcript distinguishes the 1968 conference, the 1969 report and its later transcription. Parnas's 1976 program-family paper is an important bibliographic origin, but its full text was not obtained here. The separately inspected 1979 paper on extension and contraction supplies primary evidence for designing related programs around decisions that can change. Neither source is treated as the complete later SPLE lifecycle, and similarity does not justify inventing a direct influence edge between them. [ESPLE-S001, opening and component-family discussion; ESPLE-S002, bibliographic/abstract access; ESPLE-S003]

Domain analysis makes reusable knowledge itself an engineering object. FODA's feature diagrams belong to a wider analysis involving context, domain structure and behaviour, information sources and rationale. Reducing that report to a tree of checkboxes loses the method that gives the tree its meaning. The 1992 Neighbors retrospective was available only at abstract level; it supports a historical positioning, not a reconstructed detailed algorithm. FODA's own scope limitations also matter: its modelling contribution cannot be used as an economic proof merely because economics later became central to product-line adoption. [ESPLE-S004, abstract; ESPLE-S005, context/domain modelling and §7.3.2]

FAST and PuLSE are not successive names for the same thing. The inspected FAST case combines commonality analysis with an application-oriented language and production mechanism. PuLSE responds to practical problems of domain-engineering scope and deployment through product-focused and customisable method components. The SEI industrial school emphasises the interdependence of core assets, product production and management. The Pohl–Böckle–van der Linden framework gives domain and application engineering an explicit conceptual structure and identifies antecedents, including industrial initiatives and earlier work. These branches can inform each other without being collapsed into a single canonical sequence. [ESPLE-S006; ESPLE-S007; ESPLE-S008; ESPLE-S009]

The feature-oriented, constraint, delta and verification branches develop different mechanisms. AHEAD concerns systematic refinement and composition across artefacts. Feature-model reasoning formalises represented choices and dependencies. Delta-oriented programming supports additions, removals and modifications rather than only additive refinements. Family-aware analysis shares computations across variants; product and compositional strategies remain alternatives or complements. Dynamic product lines move some selection into operation, where state transitions become a separate concern. None of these developments implies that all mature families must adopt the newest or most formal branch. [ESPLE-S014; ESPLE-S016; ESPLE-S017; ESPLE-S018; ESPLE-S019; ESPLE-S030; ESPLE-S031]

## 3. Warranted scope, commonality and the decision to share

**P1 is the first discriminating obligation:** what warrants treating these products as a family? It is not answered by an arbitrary percentage of common code. Shared code can implement incompatible assumptions; valuable domain commonality can exist before a common implementation. The scoping decision needs representative product requirements, actual variation, expert knowledge and plausible contrary products. It should identify exclusions as well as inclusions. PuLSE's product-focused scope and the domain-analysis accounts support this attention to relevant rather than unlimited domains. [ESPLE-S005; ESPLE-S007; ESPLE-S009]

An analyst should separate three kinds of differences. Some are required product distinctions. Others are consequences of history, such as alternative local implementations of the same need. Still others expose incompatible assumptions that might be expensive or impossible to reconcile within the proposed boundary. Automatically making all observed differences selectable features converts historical accidents into permanent obligations. Automatically removing all differences imposes a false commonality. The mature decision is to establish what each difference means and who needs it.

**ESPLE-001–003** therefore preserve warranted scope, evidence of commonality and value-bound variability admission. A small comparison table reviewed by knowledgeable participants can be sufficient. A detailed domain model is justified when its distinctions materially affect repeated production or assurance. The evidence does not establish a universal scoping metric. Reverse-engineered industrial variation is especially useful as a challenge to a clean model, not as a complete specification of all products that should exist. [ESPLE-S041, §§3–6]

This decision remains revisable. Future demand can fail to arrive. Formerly common needs can diverge. A new product can reveal that a supposed invariant was only an artefact of the initial sample. Reopening scope is not necessarily evidence that the method failed; refusing to reopen a disproved scope can be. But revision has costs: supported products may still depend on the old boundary. Scope revision and product support must therefore communicate, rather than treating a new model as permission to erase the old products.

## 4. Domain and application engineering as coupled responsibilities

**P2 concerns a relationship, not a mandatory organisational chart.** Domain engineering establishes and evolves reusable family knowledge and assets. Application engineering derives and adapts a particular product. Product observations can reveal mistakes in domain assumptions or deficiencies in shared assets; domain changes can affect product feasibility and support. The framework is not adequately reconstructed as “finish all domain engineering, then begin all application engineering”. The inspected generative and framework sources include feedback, while the adoption literature supplies proactive, reactive and extractive paths. [ESPLE-S006; ESPLE-S009; ESPLE-S010]

The important separation is between decisions with family consequences and decisions local to a product. The same individual may perform both roles, provided those consequences are not confused. Conversely, two departments do not establish the relationship if product failures cannot change shared assets or if the shared team imposes inappropriate requirements without product evidence. A production plan needs consumers capable of using it, not merely an owner named in a document.

Product-specific exceptions deserve a positive account. An exception can be an appropriate response to an unusual obligation, a temporarily unsupported capability or an incompatible release schedule. It should retain enough ancestry to identify what it shares, what has diverged and which family assurances no longer apply. Neither permanent uncontrolled cloning nor immediate forced reintegration is the universal answer. The industrial cloning evidence reports both pragmatic motives and later difficulties, so **ESPLE-006** retains justified exceptions with support responsibility rather than an unconditional ban. [ESPLE-S026, findings; ESPLE-S041, legacy and mixed-artefact discussion]

The adoption branch is likewise conditional. Proactive work is more credible when needs and reuse are predictable and investment is supportable. Reactive growth reduces speculative commitment but can make later consolidation difficult. Extraction uses existing evidence but must distinguish accidental similarity from intended commonality. Mixed strategies can be sensible across time or subsystems. The rejected claim **ESPLE-050** is that complete upfront modelling is always required; the retained candidate **ESPLE-007** is selection among routes with their actual costs exposed. [ESPLE-S007; ESPLE-S010; ESPLE-S025]

## 5. Features and constraints: useful distinctions with limited reach

**P3 begins with semantics.** A feature can express a stakeholder-visible capability or a domain characteristic, but a feature is not automatically a requirement, code module, command-line option or runtime service. Those relations may be many-to-many. Optionality, alternatives, cardinalities, attributes and cross-tree constraints represent different aspects of intended variation. A richer representation is useful when the domain needs those distinctions, not because richer syntax is inherently more mature. [ESPLE-S005, feature model; ESPLE-S014, grammar/formula translation; ESPLE-S017, realisation discussion; ESPLE-S032, language levels]

Let `Cφ` denote assignments satisfying an encoded variability model `φ`. A satisfiability result concerns membership or existence in `Cφ`. Dead-feature, false-optional and void-model diagnostics reveal properties of that representation. An explanation can help a person understand why selections conflict. These are substantive mechanisms: they can prevent inconsistent decisions and expose surprising restrictions. They do not establish that every relevant domain rule was encoded, that feature meanings remain agreed or that a generator implements the selection correctly. [ESPLE-S014, SAT reasoning; ESPLE-S015, analysis-operations taxonomy]

This boundary is not a reason to dismiss solvers. It identifies the work needed around them. Domain experts must challenge omitted or mistaken constraints; implementers must connect selections to realisation; product acceptance must examine relevant behaviour. Model consistency is valuable precisely when its claim is kept precise. **ESPLE-009** is strongly retained within that boundary, while **ESPLE-052**, “satisfiable means correct product”, is rejected.

Understandability and maintenance can defeat an otherwise precise approach. A generated dependency expression may accurately describe observed code yet be difficult to relate to domain meaning. A global feature model can become stale when no sustainable update responsibility exists. The Bosch report motivates narrower, subsystem-related modelling and domain review of extraction results, not abandonment of explicit variability. The mature form protects a maintained semantic consumer; **ESPLE-051** rejects a feature tree whose presence alone substitutes for that relationship. [ESPLE-S041, §§2–6]

## 6. Realisation, binding time and the actual product

**P4 separates choosing a product from making it.** Variability can be realised by parameters, conditional compilation, components, plugins, inheritance, feature modules, aspects, deltas, models and generators. The detailed comparative mechanism reconstruction here relies on inspected feature-oriented and delta work; the older realisation taxonomy was only abstract-accessible and is not used as a source for uninspected details. Different techniques expose different change and interaction boundaries. Their names are not a ranking. [ESPLE-S017, §§4.3–4.4; ESPLE-S018; ESPLE-S042, access limit]

Feature modules can make selected concerns explicit, while annotations can preserve a familiar code organisation. Deltas can express modifications and removals that are awkward in purely additive composition, but then applicability and ordering require attention. A generator can remove repeated manual derivation effort, while creating a common transformation on which many products depend. Mixed realisation may be necessary, but it adds the burden of reconciling configuration layers and maintaining meaningful traceability.

Binding time changes the obligation. Compile-time choice can reduce runtime complexity but requires rebuilding to alter it. Deployment-time choice postpones some decisions while keeping them outside ordinary operation. Runtime choice can serve genuine context-dependent needs, but introduces state, observation and transition requirements. Later binding is not simply earlier binding plus a free option. **ESPLE-013** retains deliberate selection; **ESPLE-054** rejects the unqualified claim that later is always better. [ESPLE-S017; ESPLE-S030; ESPLE-S031]

The realisation relation can be written analytically as `R(D(A,c,t,e), c)`: derivation `D` uses assets `A`, configuration `c`, tools `t` and relevant environment `e`, and its output must realise the intended selection under relation `R`. This notation is this report's model, not a cited universal formalism. It reveals why `c ∈ Cφ` is insufficient. A defective template can emit the wrong capability from a valid selection. A build dependency can select a version incompatible with the feature model. A product can compile while violating a requirement. The historical JHipster configuration campaign supplies direct evidence that generated configuration outcomes and higher-level product choices must not be collapsed. [ESPLE-S021, experimental setup and §6.1]

## 7. Core assets, production and identity

**P5 extends beyond shared source code.** Requirements, architectural decisions, tests, documentation, production instructions and supporting tools can all be reusable assets when particular products actually consume them. A reference architecture can be useful guidance without automatically constraining derivation. The analyst must identify where the intended invariant is enforced, checked or merely suggested. A catalogue of assets is not the same thing as a production capability. [ESPLE-S008, preface; ESPLE-S009, chapter 2; ESPLE-S011, production-plan development]

The production plan ties the chosen product to its relevant assets and activities. It may be substantially automated, partly manual or quite modest. What matters is whether it is usable, whether adaptation decisions are controlled and whether the result can be attributed to the intended baseline. A plan that nobody follows and a build script whose hidden inputs change unpredictably can fail in different ways despite both being called “the production process”.

**ESPLE-021** concerns configuration and baseline identity. Which model version, asset revisions, dependency selections and production tools materially affected this product? **ESPLE-022** concerns repeatability under a declared equivalence. Exact byte identity is appropriate in some settings; in others nondeterministic metadata can differ while a meaningful structural or behavioural equivalence is the relevant requirement. This synthesis does not infer that production-plan guidance proves bit-for-bit reproducible builds. It requires the repeatability claim to say what is meant and what evidence checks it. [ESPLE-S011, version management; analytical reconstruction]

The cheap form is often a normal versioned repository, a recorded configuration and a short reliable production instruction. More elaborate provenance is warranted when hidden dependencies, generated artefacts, long-lived support or failure attribution demand it. The standardisation branch does not overturn that proportionality: the inspected public scope of ISO/IEC 26580 concerns a particular feature-based approach, not a proof that complete automation defines every legitimate SPLE practice. [ESPLE-S033, public scope only]

## 8. Assurance across configurations, features and products

**P6 requires several boundaries at once.** The model may permit a configuration; the realisation may correctly build its selected features; the implementation may nevertheless have an interaction defect; a family analysis may cover represented configurations but not every input or environment. A product may inherit some evidence from shared assets while retaining local obligations. Treating all these as one “coverage” number destroys the distinctions needed to decide what is safe to conclude. [ESPLE-S019, strategy classification; ESPLE-S020, assumptions; ESPLE-S040, validity discussion]

Product-based checks directly examine selected members but can repeat work or miss untested variants. Family-based approaches share computation over variability, provided the representation and underlying analysis support the family. Feature-based or compositional approaches use local information and contracts, but must discharge assumptions about composition and interference. Sampling controls cost by intentionally reducing the configurations exercised. These approaches can complement each other, but their combination is justified by distinct failure coverage, not by an obligation to collect every possible report.

The sampling literature is especially important because it challenges claims that a convenient strategy is uniformly best. The inspected comparison varies assumptions about build information, headers, constraints and scope. The historical JHipster study links many configuration failures to a small number of root faults, including higher-order interaction. Thus many failing configurations are not many independent defects, and a large exercised sample is not automatically complete assurance. **ESPLE-025** remains assumption-sensitive, not rejected; **ESPLE-053**, the universal completeness claim for pairwise testing, is rejected. [ESPLE-S020, study design/results; ESPLE-S021, interaction and sampling results]

The same restraint applies to static analysis. Variability-aware parsing addresses language and preprocessor variation; subsequent analyses can exploit shared structure. Their reports are conditional on those representations and on the underlying analysis. The inspected scale study explicitly limits the interpretation of warnings and underlying analysis precision. It does not support counting every reported warning as a confirmed bug, nor extrapolating benchmark scale to arbitrary languages and generated artefacts. [ESPLE-S022; ESPLE-S040, pp. 1–3 and 26]

The composed system therefore keeps **ESPLE-028**, actual product acceptance, as a distinct consumer of evidence. This does not require manually retesting every imaginable product after every change. It requires the party accepting a particular product to know which inherited results apply, which local obligations remain and what observation establishes them. A failed observation can interrupt a planned shared rollout; it is not merely a datum to archive after declaring success.

## 9. Evolution, migration and justified divergence

**P7 is not just “update the feature model”.** Models, code, architectural constraints, generators, configurations and tests can evolve independently. A feature rename may preserve intent; an unchanged feature name may hide changed behaviour. Model-edit analysis can classify relationships between represented configuration sets, but that is a narrower object than the behaviour and obligations of supported products. [ESPLE-S023, edit classification; ESPLE-S024, configuration evolution]

Migration should preserve product intent under the destination family's actual semantics. Finding the nearest satisfying assignment is useful only when the distance metric and encoded obligations match what the product needs. A low edit count can still remove an essential capability. A valid destination configuration can be realised incorrectly by an updated generator. This is why migration is connected to feature meaning, baseline identity and product acceptance rather than treated as an isolated solver operation.

Shared changes create both economies and risks. A repair may propagate efficiently, yet break one variant with a different resource or compatibility constraint. The method needs an impact decision: common change, differentiated backport, supported older baseline, local exception or explicit withdrawal of support under the relevant obligations. No source establishes that every old variant must live forever; neither does a new model establish permission to abandon one. The industrial evidence on cloning and legacy variation makes both sides material. [ESPLE-S011, version management; ESPLE-S026, propagation difficulties; ESPLE-S041, §3]

Extraction is a legitimate route to recovery, not an oracle. Feature-model synthesis from existing variants and industrial variability recovery can reveal relationships and support incremental consolidation. They can also omit artefacts, mistake implementation effects for domain rules or overfit the observed variants. **ESPLE-034** retains recovery with domain reconciliation. It rejects neither extraction nor expert judgement; it couples them so that each can challenge the other's limitations. [ESPLE-S025; ESPLE-S041, §§4–6]

Recent test-evolution work is relevant because maintaining tests is itself a family cost. Its comparison of preserving, repairing and regenerating configuration-oriented tests gives alternatives with different objectives. The reported dissimilarity/effort limitation prevents treating a convenient distance metric as measured human labour. Passing feature-model mutation tests also does not prove that all product behaviour survived. **ESPLE-035** is consequently context-dependent, and **ESPLE-061** separately retains support-aware retirement of variation when its consumer disappears. [ESPLE-S037, pp. 13–15; ESPLE-S041; ESPLE-S045, §§5.4, 7]

## 10. Economics and the legitimacy of alternatives

**P8 asks whether the family is preferable, not merely feasible.** A product-line investment includes preparation of reusable assets, organisational capability, derivation infrastructure, coordination, assurance, migration and support. It may save repeated product work. Both sides depend on the horizon, demand, variation rate and the quality of the alternative. A universal break-even number suppresses the very variables that determine the decision. SIMPLE supplies structured economic reasoning, not one universal answer. [ESPLE-S012, equations and scenario updates]

Clone-and-own deserves the same analytical seriousness as the favoured approach. The exploratory industrial study records reasons for its use as well as difficulties. The BSH comparison gives a selected industrial task setting in which the prepared product-line approach performs favourably; it does not price the entire transition or establish that every portfolio should follow it. The later variability-debt record is available only at abstract level, so it supports a bounded warning rather than detailed effect claims. [ESPLE-S026, design/findings; ESPLE-S027, design/results/threats; ESPLE-S028, institutional abstract]

The mature comparison is between **adequate alternatives**. An intentionally weak cloning baseline cannot establish the value of SPLE. An already prepared platform cannot make its preparation cost disappear. Conversely, comparing a carefully maintained shared family with unmanaged copies that must repeatedly receive the same fixes may legitimately favour the family. The discriminating evidence is the actual work and obligations over the relevant horizon, not a moral preference for sharing or autonomy.

The smallest economic account can be a handful of credible scenarios. It should state what reverses the decision: fewer future products, rising coordination cost, unanticipated product exceptions, expensive assurance or a simpler shared component satisfying most reuse needs. Observed results should revise the initial estimates. Configuration count may describe a model's size, but should not stand in for useful products or realised benefit. **ESPLE-059** is retained only in that narrow, easily gamed descriptive role.

## 11. Organisation, authority and externally specified constraints

**P9 supplies the operating conditions often missing from technical diagrams.** Someone must maintain reusable assets, judge variation requests, coordinate incompatible product needs and act on defect evidence. Industrial guidance documents the importance of business alignment, governance and production capability, but this is not a measured universal failure-rate model. A technically expressive feature language cannot supply staffing, incentives, decision rights or a working relationship between product and shared teams. [ESPLE-S013, experience-based obstacles and responses]

The synthesis separates three things: making a distinction, being authorised and able to act on it, and achieving the consequence. A solver can identify a conflict; it does not determine whose requirement should change. A product team can report a failure; it may not have authority to alter a common supplier interface. A shared-team approval can authorise a repair; it does not prove that all affected products received it correctly. Communication must therefore carry actionable evidence to the appropriate consumer, and consequences must be observed at the relevant boundary.

This is not a proposal for one new owner or approval meeting per property. Responsibilities can be combined. The minimum requirement is that material decisions do not become orphaned or silently exercise authority over others. Participation matters where a shared decision changes another product's obligations; a ritual meeting with no evidence or decision consumer does not establish that participation.

Ecosystem and community arrangements make the authority boundary explicit. The inspected ecosystem work extends attention beyond a single organisation. The current community-driven taxonomy describes independently implemented interoperable systems that need not share one core or central production process. These are documented external relationships, not a licence to relabel every community as a classical product line. Interoperability and negotiated compatibility can be the common concern while implementation and release decisions remain distributed. [ESPLE-S029; ESPLE-S044, §§1, 3–5]

Licensing, contractual, security and mission obligations belong in the model when an authorised external source actually specifies them. This report does not invent their legal content. A common asset can amplify a common exposure, so evidence of sharing is not evidence that the obligations have been discharged. **ESPLE-042** retains the boundary: identify the actual constraint and consumer; do not derive external permission from an internally valid configuration.

## 12. Dynamic families and the current frontier

**P10 investigates runtime variability without equating it with all adaptation.** A dynamic product line relates observed context to permitted configurations and to a mechanism for changing between them. The model-driven work connects context, variability and middleware, while also leaving safe reconfiguration as a substantive concern. Dynamic product-line overviews identify the branch, but the detailed mechanism here is grounded in inspected primary work rather than the inaccessible parts of the overview. [ESPLE-S030, models and discussion; ESPLE-S043, abstract access]

Two individually valid configurations need not admit a safe transition. Intermediate state, synchronisation, in-flight work, resource possession and uncontrollable events can matter. Supervisory-control work supplies a formal response under discrete-event modelling assumptions, distinguishing modelled constraints and control capabilities. Its nonblocking guarantee concerns reachable completion within that model; it does not mean every real execution inevitably makes progress, or that an abstract benchmark proves physical deployment safety. **ESPLE-044** is a strongly retained boundary; **ESPLE-045** is a domain-specific method for addressing it. [ESPLE-S031, §§4–8]

Recent interchange and evolution research also matters without runtime adaptation. UVL develops representational levels and shared language semantics to address model/tool fragmentation. This is interoperability work, not evidence that more expressive models universally outperform simpler ones. The 2026 journal issue on changing feature models and tests extends a concrete maintenance problem, with an earlier online publication date. An announcement of a conference or accepted paper supplies current research direction, not a replicated result. [ESPLE-S032, introduction and §§4–5; ESPLE-S037, publication information and §§6–9]

The official VARIABILITY 2026 event combines SPLC, VaMoS and ICSR and is scheduled for **29 September–2 October 2026**, after this study's cut-off. The conference has not been treated as already completed. Current learned-assistance and regeneration proposals were searched separately. The 2025 LLM co-evolution paper was accessible only as metadata; no methods or performance claims are imported from it. The June 2026 regeneration proposal was inspected, while a later HAL version was located but blocked. Adjacent DSL migration experiments inform transfer questions, not direct industrial SPLE effectiveness. [ESPLE-S035, official announcement/programme; ESPLE-S036, access limit; ESPLE-S034; ESPLE-S038]

The resulting judgement is deliberately asymmetric. **ESPLE-047** retains learned proposals as assumption-sensitive assistance subject to independent validation. **ESPLE-048** leaves regeneration's stronger replacement/lifecycle superiority unresolved. A separate current proposal on small and null variability supports reconsidering unnecessary options and earlier binding. Its qualified account of outputs must not be caricatured; nevertheless, fixed configuration choices do not alone establish independence from input, state or environment. **ESPLE-062** rejects that stronger inference while preserving the useful distinction. [ESPLE-S034; ESPLE-S038; ESPLE-S045, §§7.2–7.3]

## 13. What counts as evidence here

Historical provenance is strongest when a source documents an actual formulation or transmission. A citation can show acquaintance without proving derivation; a similar term can show convergence or analogy without influence. The genealogy therefore records explicit extensions, imports, criticisms, shared ancestry and unresolved relationships separately. It does not turn every branch into a single progress story.

Formal strength and empirical strength can diverge. Constraint reasoning can be strong within the encoded model while domain adequacy remains uncertain. A supervisory theorem can hold while its plant abstraction is incomplete. A family analysis can correctly reproduce an underlying imprecise analysis. The report records model, guarantee, assumptions and implementation obligations separately rather than averaging them into a confidence percentage.

Empirical units require equal care. Eleven practitioners are not eleven independent organisations. Forty task observations from ten people are not forty independent participants. Thousands of generated configurations failing because of six faults are not thousands of independent root causes. Mutants and historical releases share their families. Repeated descriptions of the same industrial programme do not create replication. These distinctions change the allowable generalisation, not just a footnote to otherwise universal benefit claims. The study register below supplies the actual samples, comparisons and validity threats.

The resulting “Evolved” system is consequently an **explicit analytical composition**. Its logical counterexamples test whether the decision rules make inappropriate inferences; they do not empirically validate adoption outcomes. Its minimal and richer configurations are reasoned selections from sourced mechanisms; they are not newly standardised methodologies. This separation permits a coherent system without pretending to have stronger evidence than the field or this inspection provides.

## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_TIMELINE

The dated record below distinguishes the problem’s early formulations from later mechanisms. Dates are publication/event dates unless explicitly identified as deposits. A recent upload does not make an older result current research.

| Date | Branch / event | Contribution and limit | Sources |
| --- | --- | --- | --- |
| 1968 conference / 1969 report | Component production and reuse | A precursor problem framing for systematic reuse. Does not supply the later domain/application engineering lifecycle; transcript is from 1998. | ESPLE-S001 |
| 1976; related extension in 1979 | Program families and design for change | Family as a design unit, not just a code-reuse inventory. 1976 full text not obtained; the 1979 primary paper supplies inspected mechanisms. No unsupported direct McIlroy-to-Parnas influence edge. | ESPLE-S002, ESPLE-S003 |
| 1990; 1992 retrospective | Domain analysis and FODA | Feature modelling plus rules and rationale in a broader domain analysis. FODA is a feasibility report and excludes some economic/legal matters; Neighbors retrospective is abstract-only. | ESPLE-S004, ESPLE-S005 |
| 1999 | PuLSE | A documented response to impractical scope and adoption burden. Tailoring is not evidence that every tailored programme becomes economic. | ESPLE-S007 |
| 2000 inspected case paper | FAST and industrial generative families | An operative generative branch with a production mechanism. Lucent-related experience is one programme, not dozens of independent causal replications. | ESPLE-S006 |
| 2001/2002; 2002; 2005; 2010 | Industrial core-assets, production and management school | Makes organisational and production responsibilities explicit. Book access is publisher excerpts; detailed production/economic reports and negative experience were inspected separately. | ESPLE-S008, ESPLE-S011, ESPLE-S012, ESPLE-S013 |
| 2001 workshop / 2002 proceedings; 2005 framework | Adoption routes and domain/application engineering | Separates reusable-family and product-specific responsibilities without making them once-only phases. Framework chapter draws explicitly on earlier industrial and ITEA work; adoption claims are not universal returns. | ESPLE-S009, ESPLE-S010 |
| 2004; 2009 overview | AHEAD and feature-oriented development | Links feature selection to multi-artefact production. Algebraic composition does not establish arbitrary product behaviour or force one feature into one module. | ESPLE-S016, ESPLE-S017 |
| 2005; 2010 review | Constraint-based feature analysis | Precise represented configuration sets and automated assistance. Encoded consistency is not domain completeness or implementation correctness. | ESPLE-S014, ESPLE-S015 |
| 2008 | Dynamic and model-driven product lines | Moves permitted product variation into operation. Static feature validity does not supply transition safety; 2008 overview access limited, model-driven paper inspected. | ESPLE-S030, ESPLE-S043 |
| 2009–2026 | Configuration and family evolution | Continuity becomes a separate engineering obligation. Configuration-set preservation is not behavioural preservation; 2025 evolution-plan full proof was not accessible. | ESPLE-S023, ESPLE-S024, ESPLE-S025, ESPLE-S037, ESPLE-S039, ESPLE-S041 |
| 2009 | Software ecosystems beyond a single product-line organisation | Broadens the ownership/coordination question while preserving important distinctions from classical SPLE. Participant-observer examples do not establish comparative governance effectiveness; biological analogy is not documentary engineering ancestry. | ESPLE-S029 |
| 2010 | Delta-oriented programming | An alternative realisation supporting negative and changing variation. Ordering, applicability and interference remain obligations; not the universal successor to FOP. | ESPLE-S018 |
| 2011–2019 | Family assurance and configurable-system analysis | Shares computations or limits sampled configurations with explicit coverage. Analysis assumptions, unconfirmed warnings and higher-order faults limit general claims. | ESPLE-S019, ESPLE-S020, ESPLE-S021, ESPLE-S022, ESPLE-S040 |
| 2018 initiative; 2025 work; 2021 scoped standard | Variability interchange and feature-based industrial guidance | Interoperability is a distinct concern from adding more variability. Only ISO public scope inspected; language availability and specification do not prove adoption or economic benefit. | ESPLE-S032, ESPLE-S033 |
| 2023 journal; earlier versions identified in paper | Supervisory-control import into dynamic configuration | Formal control of modelled safety/nonblocking under stated control assumptions. Body Comfort System is an industrial-origin benchmark, not evidence of vehicle deployment or physical completeness. | ESPLE-S031 |
| 2025–2026 | Learned assistance, regeneration and variability reduction | New alternatives and sharper questions about where variability resides and what must be revalidated. Current exploratory work is not a mature replacement consensus; LLM co-evolution metadata alone supports no performance claim. | ESPLE-S034, ESPLE-S036, ESPLE-S038, ESPLE-S045 |
| 2026 | Community-driven variability | A documented contemporary distinction from centrally managed common-core production. Fourteen selected ecosystems and proxy-based taxonomy do not prove superior governance or adoption rates. | ESPLE-S044 |

The 2026 conference announcement is current institutional evidence, but its September–October event lies after the cut-off. The 2025/2026 papers and preprints were inspected according to their recorded access levels; conference affiliation supplies no additional replication.

## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_GENEALOGY

The genealogy is plural: component reuse, program families, domain analysis, industrial production, feature composition, logical configuration and runtime control solve related but non-identical problems. The following edge classifications are deliberately narrower than a claim that all mechanisms descend from one founder. Each node also records its problem, mechanism and limit in the composition JSON.

| Edge | From → to | Relationship | Documentary basis | Sources |
| --- | --- | --- | --- | --- |
| ESPLE-GE01 | ESPLE-G01 → ESPLE-G02 | UNRESOLVED_RELATIONSHIP | Both concern related reusable programs; inspected evidence is insufficient to assert direct transmission between these exact works. | ESPLE-S001, ESPLE-S002, ESPLE-S003 |
| ESPLE-GE02 | ESPLE-G02 → ESPLE-G03 | SHARED_ANCESTRY | Domain analysis and program-family design share the problem of reusable knowledge; this edge does not assert derivation of FODA from one paper alone. | ESPLE-S003, ESPLE-S005 |
| ESPLE-GE03 | ESPLE-G03 → ESPLE-G05 | CRITICISM_AND_RESPONSE | PuLSE explicitly responds to limitations of large, insufficiently product-focused domain-engineering approaches. | ESPLE-S007 |
| ESPLE-GE04 | ESPLE-G04 → ESPLE-G07 | DOCUMENTED_INFLUENCE | Pohl et al. chapter 2 explicitly identifies Weiss and Lai and industrial initiatives among framework antecedents; this is framework-level, not a claim that every operation originated in FAST. | ESPLE-S009 |
| ESPLE-GE05 | ESPLE-G06 → ESPLE-G07 | SHARED_ANCESTRY | Related industrial product-line practice informs both; different representations preserve coupled product/core responsibilities. | ESPLE-S008, ESPLE-S009, ESPLE-S011 |
| ESPLE-GE06 | ESPLE-G03 → ESPLE-G09 | EXPLICIT_EXTENSION | Feature-model analysis papers explicitly formalise and analyse feature-model constraints associated with the FODA lineage. | ESPLE-S014, ESPLE-S015 |
| ESPLE-GE07 | ESPLE-G08 → ESPLE-G10 | CRITICISM_AND_RESPONSE | Delta-oriented programming explicitly addresses expressiveness limitations of additive feature-oriented programming. | ESPLE-S018 |
| ESPLE-GE08 | ESPLE-G08 → ESPLE-G11 | EXPLICIT_EXTENSION | Family assurance investigates how feature-oriented and other variability realisations can be analysed without only enumerating products. | ESPLE-S017, ESPLE-S019 |
| ESPLE-GE09 | ESPLE-G09 → ESPLE-G12 | EXPLICIT_EXTENSION | Configuration-set semantics become the basis for classifying edits and adapting configurations/tests. | ESPLE-S023, ESPLE-S024, ESPLE-S037 |
| ESPLE-GE10 | ESPLE-G03 → ESPLE-G12 | DOMAIN_TRANSLATION | Extraction and feature modelling are applied to existing cloned or industrial variants, subject to missing-domain-knowledge limits. | ESPLE-S025, ESPLE-S041 |
| ESPLE-GE11 | ESPLE-G09 → ESPLE-G13 | DOMAIN_TRANSLATION | Feature selection is applied to runtime adaptation; transition behaviour adds obligations beyond static configuration. | ESPLE-S030, ESPLE-S043 |
| ESPLE-GE12 | ESPLE-G13 → ESPLE-G14 | DOCUMENTED_IMPORT | The paper explicitly combines product-line dynamic reconfiguration with discrete-event supervisory control and identifies prior approaches it extends. | ESPLE-S031 |
| ESPLE-GE13 | ESPLE-G06 → ESPLE-G15 | EXPLICIT_EXTENSION | Bosch explicitly argues for organisational expansion from product lines to ecosystems; the later community taxonomy describes a distinct coordination arrangement. | ESPLE-S029 |
| ESPLE-GE14 | ESPLE-G15 → ESPLE-G18 | DOMAIN_TRANSLATION | The 2026 paper explicitly contrasts independently developed interoperable implementations with classical common-core product-line arrangements. This edge records the documented comparison, not an assertion of direct derivation from Bosch alone. | ESPLE-S044 |
| ESPLE-GE15 | ESPLE-G09 → ESPLE-G16 | EXPLICIT_EXTENSION | UVL explicitly addresses fragmentation in feature modelling and documents the MODEVAR initiative and language levels. | ESPLE-S032 |
| ESPLE-GE16 | ESPLE-G12 → ESPLE-G17 | HYBRIDISATION | Learned tools are proposed for evolution/derivation tasks; inspected evidence varies from metadata to exploratory evaluations, so replacement benefit is not established. | ESPLE-S034, ESPLE-S036, ESPLE-S038 |
| ESPLE-GE17 | ESPLE-G08 → ESPLE-G17 | CRITICISM_AND_RESPONSE | New proposals question maintained configuration machinery; this study retains reduction as conditional and regeneration superiority as unresolved. | ESPLE-S034, ESPLE-S045 |


**Attribution discipline.** McIlroy and Parnas are not joined by an invented direct-influence claim. The relationship is left unresolved at that level. The Pohl framework’s explicit antecedents, delta programming’s response to additive composition, and supervisory control’s documented import warrant more specific edges. The ecosystem/community distinction records a documented comparison and translation, not proof that one exact paper caused the later taxonomy. Biology remains analogy unless a technical mechanism is separately documented. No sibling corpus supplied an edge.

## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_SCOPE_AND_CARICATURES

The examined scope is a production-and-evolution tradition, not a synonym for all reuse. Its minimum distinguishing relationships are justified family scope, common and variable needs, reusable assets, product derivation, and feedback over the supported family. The system can be modest, iterative and partly manual.

| Caricature | Correction | Relevant IDs |
| --- | --- | --- |
| Any shared library makes a product line | Ordinary component reuse may lack a family scope or common derivation commitment. | ESPLE-001, ESPLE-002, ESPLE-020 |
| A feature tree is the method | Feature semantics, domain constraints, realisation and consumers supply the operation. | ESPLE-008–ESPLE-014, ESPLE-051 |
| One feature means one module | Feature-to-artefact relations can be many-to-many and cross-cutting. | ESPLE-015, ESPLE-016, ESPLE-055 |
| Every product line is fully generated | Controlled manual derivation may be adequate; automated methods have scoped applicability. | ESPLE-020–ESPLE-022, ESPLE-056 |
| Cloning is always immature | Autonomy and startup cost can favour cloning; propagation debt can later change the comparison. | ESPLE-007, ESPLE-036–ESPLE-038, ESPLE-057 |
| Formal validity is product correctness | Model, realisation, configuration coverage and actual product behaviour are different objects. | ESPLE-009, ESPLE-017, ESPLE-023–ESPLE-029, ESPLE-052 |
| Every runtime adaptation is a dynamic product line | The dynamic branch relates context to permitted family configurations and transitions. | ESPLE-043–ESPLE-045 |
| More variants means more value | Model-space size is a descriptive quantity, not demonstrated benefit. | ESPLE-003, ESPLE-036, ESPLE-059, ESPLE-061 |

**Limits of scope.** This is not a full legal analysis, tool benchmark, industry census or assessment of any host system. Canonical books and several papers were not all accessible in full; those limits are explicit. The study instead reconstructs required mechanisms from inspected primary works and marks narrower evidence where that reconstruction cannot establish a stronger claim.

## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER

The complete denominator is **62/62 examined**. Primary dispositions sum to 62; the unresolved candidate is examined, not unfinished. Each row below points to the full JSON record in the adjacent payload. The ledger includes all mandatory common fields and all ten discipline-specific domain-profile fields, plus property-specific bindings. It also retains criticism, evidence partitions and the source locators behind each record.

| Primary disposition | Count |
| --- | --- |
| ASSUMPTION_SENSITIVE | 4 |
| CEREMONY_NOT_GENERAL_PROPERTY | 1 |
| CONTEXT_DEPENDENT | 12 |
| DOMAIN_SPECIFIC | 4 |
| NO_GENERAL_PROPERTY | 2 |
| REJECTED_OR_DISFAVOURED | 9 |
| RETAINED_IN_EVOLVED_FORM | 18 |
| STRONGLY_RETAINED | 9 |
| UNRESOLVED | 1 |
| USEFUL_BUT_EASILY_BUREAUCRATISED | 1 |
| USEFUL_BUT_EASILY_GAMED | 1 |

| Property ID | Candidate | Disposition | Examination | Full record |
| --- | --- | --- | --- | --- |
| ESPLE-001 | Warranted family boundary | STRONGLY_RETAINED | EXAMINED_WITH_EVIDENCE_LIMIT | [0](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/0) |
| ESPLE-002 | Evidence of commonality and variability | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT | [1](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/1) |
| ESPLE-003 | Value-bound admission of variability | RETAINED_IN_EVOLVED_FORM | EXAMINED | [2](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/2) |
| ESPLE-004 | Coupled domain and application responsibilities | STRONGLY_RETAINED | EXAMINED_WITH_EVIDENCE_LIMIT | [3](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/3) |
| ESPLE-005 | Product-to-core feedback | RETAINED_IN_EVOLVED_FORM | EXAMINED | [4](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/4) |
| ESPLE-006 | Product exceptions with retained lineage | RETAINED_IN_EVOLVED_FORM | EXAMINED | [5](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/5) |
| ESPLE-007 | Selection among proactive, reactive and extractive adoption | CONTEXT_DEPENDENT | EXAMINED_WITH_EVIDENCE_LIMIT | [6](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/6) |
| ESPLE-008 | Explicit feature semantics | STRONGLY_RETAINED | EXAMINED | [7](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/7) |
| ESPLE-009 | Constraint-consistency diagnostics | STRONGLY_RETAINED | EXAMINED | [8](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/8) |
| ESPLE-010 | Validation of domain-constraint adequacy | RETAINED_IN_EVOLVED_FORM | EXAMINED | [9](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/9) |
| ESPLE-011 | Explanation-assisted configuration | CONTEXT_DEPENDENT | EXAMINED | [10](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/10) |
| ESPLE-012 | Richer variability types when the domain requires them | CONTEXT_DEPENDENT | EXAMINED | [11](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/11) |
| ESPLE-013 | Deliberate binding-time selection | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT | [12](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/12) |
| ESPLE-014 | Feature-to-realisation traceability | USEFUL_BUT_EASILY_BUREAUCRATISED | EXAMINED | [13](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/13) |
| ESPLE-015 | A portfolio of variability realisation techniques | CONTEXT_DEPENDENT | EXAMINED | [14](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/14) |
| ESPLE-016 | Ordered and conditional delta composition | DOMAIN_SPECIFIC | EXAMINED | [15](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/15) |
| ESPLE-017 | Validation of generator realisation | RETAINED_IN_EVOLVED_FORM | EXAMINED | [16](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/16) |
| ESPLE-018 | Reusable non-code assets with consumers | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT | [17](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/17) |
| ESPLE-019 | Family architectural invariants and variation boundaries | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT | [18](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/18) |
| ESPLE-020 | A versioned product-derivation plan | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT | [19](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/19) |
| ESPLE-021 | Configuration, asset and tool baseline identity | RETAINED_IN_EVOLVED_FORM | EXAMINED | [20](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/20) |
| ESPLE-022 | Repeatable derivation at a declared equivalence level | CONTEXT_DEPENDENT | EXAMINED | [21](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/21) |
| ESPLE-023 | Layer-specific assurance claims | STRONGLY_RETAINED | EXAMINED | [22](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/22) |
| ESPLE-024 | Interaction-aware coverage | RETAINED_IN_EVOLVED_FORM | EXAMINED | [23](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/23) |
| ESPLE-025 | Constrained and risk-informed sampling | ASSUMPTION_SENSITIVE | EXAMINED | [24](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/24) |
| ESPLE-026 | Family-based sharing of analysis | DOMAIN_SPECIFIC | EXAMINED | [25](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/25) |
| ESPLE-027 | Compositional feature contracts | ASSUMPTION_SENSITIVE | EXAMINED | [26](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/26) |
| ESPLE-028 | Acceptance of the actual derived product | STRONGLY_RETAINED | EXAMINED | [27](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/27) |
| ESPLE-029 | Analysis of build, macro and configuration layers | CONTEXT_DEPENDENT | EXAMINED | [28](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/28) |
| ESPLE-030 | Semantic classification of feature-model edits | CONTEXT_DEPENDENT | EXAMINED_WITH_EVIDENCE_LIMIT | [29](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/29) |
| ESPLE-031 | Intent-preserving configuration migration | RETAINED_IN_EVOLVED_FORM | EXAMINED | [30](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/30) |
| ESPLE-032 | Impact and regression analysis of shared changes | STRONGLY_RETAINED | EXAMINED | [31](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/31) |
| ESPLE-033 | Supported baseline and release relationships | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT | [32](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/32) |
| ESPLE-034 | Recovery of variability with domain reconciliation | CONTEXT_DEPENDENT | EXAMINED | [33](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/33) |
| ESPLE-035 | Co-evolution of configuration-oriented tests | CONTEXT_DEPENDENT | EXAMINED | [34](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/34) |
| ESPLE-036 | Lifecycle economics with uncertainty | ASSUMPTION_SENSITIVE | EXAMINED_WITH_EVIDENCE_LIMIT | [35](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/35) |
| ESPLE-037 | An explicit adequate non-product-line alternative | STRONGLY_RETAINED | EXAMINED_WITH_EVIDENCE_LIMIT | [36](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/36) |
| ESPLE-038 | Economic reassessment without a sunk-cost veto | RETAINED_IN_EVOLVED_FORM | EXAMINED | [37](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/37) |
| ESPLE-039 | Authority and arbitration for shared assets | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT | [38](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/38) |
| ESPLE-040 | Capability, incentives and resource alignment | CONTEXT_DEPENDENT | EXAMINED_WITH_EVIDENCE_LIMIT | [39](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/39) |
| ESPLE-041 | An explicit ecosystem participation boundary | CONTEXT_DEPENDENT | EXAMINED_WITH_EVIDENCE_LIMIT | [40](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/40) |
| ESPLE-042 | Traceability of externally specified obligations | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT | [41](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/41) |
| ESPLE-043 | Context-to-configuration mapping for dynamic families | DOMAIN_SPECIFIC | EXAMINED_WITH_EVIDENCE_LIMIT | [42](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/42) |
| ESPLE-044 | Transition safety and state continuity | STRONGLY_RETAINED | EXAMINED | [43](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/43) |
| ESPLE-045 | Supervisory control under plant assumptions | DOMAIN_SPECIFIC | EXAMINED | [44](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/44) |
| ESPLE-046 | Semantic fidelity in variability interchange | CONTEXT_DEPENDENT | EXAMINED_WITH_EVIDENCE_LIMIT | [45](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/45) |
| ESPLE-047 | AI-assisted migration as a validated proposal | ASSUMPTION_SENSITIVE | EXAMINED_WITH_EVIDENCE_LIMIT | [46](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/46) |
| ESPLE-048 | LLM regeneration as a superior replacement for maintained variability | UNRESOLVED | EXAMINED_WITH_EVIDENCE_LIMIT | [47](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/47) |
| ESPLE-049 | A universal break-even product count | REJECTED_OR_DISFAVOURED | EXAMINED_WITH_EVIDENCE_LIMIT | [48](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/48) |
| ESPLE-050 | A complete upfront platform as a prerequisite | REJECTED_OR_DISFAVOURED | EXAMINED | [49](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/49) |
| ESPLE-051 | A feature-tree artefact as sufficient variability management | CEREMONY_NOT_GENERAL_PROPERTY | EXAMINED | [50](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/50) |
| ESPLE-052 | Feature-model satisfiability as delivered-product correctness | REJECTED_OR_DISFAVOURED | EXAMINED | [51](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/51) |
| ESPLE-053 | Pairwise coverage as family correctness | REJECTED_OR_DISFAVOURED | EXAMINED | [52](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/52) |
| ESPLE-054 | Later binding as universally better | REJECTED_OR_DISFAVOURED | EXAMINED_WITH_EVIDENCE_LIMIT | [53](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/53) |
| ESPLE-055 | A universal one-feature/one-module correspondence | NO_GENERAL_PROPERTY | EXAMINED | [54](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/54) |
| ESPLE-056 | Total automation as the definition of SPLE | NO_GENERAL_PROPERTY | EXAMINED_WITH_EVIDENCE_LIMIT | [55](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/55) |
| ESPLE-057 | Clone-and-own as universally inadmissible | REJECTED_OR_DISFAVOURED | EXAMINED | [56](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/56) |
| ESPLE-058 | Stable names or configuration sets as behavioural compatibility | REJECTED_OR_DISFAVOURED | EXAMINED | [57](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/57) |
| ESPLE-059 | Raw configuration count as a benefit measure | USEFUL_BUT_EASILY_GAMED | EXAMINED | [58](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/58) |
| ESPLE-060 | Formal modelling as operational authority | REJECTED_OR_DISFAVOURED | EXAMINED | [59](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/59) |
| ESPLE-061 | Support-aware retirement of variability | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT | [60](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/60) |
| ESPLE-062 | Null configurability as context-independent behaviour | REJECTED_OR_DISFAVOURED | EXAMINED_WITH_EVIDENCE_LIMIT | [61](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_PROPERTY_LEDGER.json#/properties/61) |

No candidate was renumbered to hide an adverse disposition. ESPLE-061 separates retirement from admission; ESPLE-062 separates a criticised behavioural inference from the useful early-binding distinction. No exact duplicate is counted as a second retained mechanism. There are no `NOT_EXAMINED` candidates.

## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_DOMAIN_MODELS

The following nine models are **analytical reconstructions** of sourced mechanisms. Their notation and combination belong to this study. They are not asserted as a recognised unified formalism, nor as proof of an implementation. Each model makes state, operation, observations and a cheaper adequate form explicit.

### ESPLE-DM-01 — Warranted family scoping

**Purpose.** Determine whether and where joint product production is technically meaningful and economically worth considering.

**Objects and state.** Let P be candidate products, N(p) their needs and A(p) their domain assumptions. A scope S is a selected subset with explicit exclusions, expected demand and candidate common assets. Similarity of names or files is evidence to investigate, not the membership predicate.

**Operation and decisions.** Compare products and counterexamples; identify which assumptions can be common and which require variation. Estimate the burden of the resulting family and compare an adequate non-family alternative. A contradiction may split S, keep a product local or reject the family proposal. Scope can be revised from product feedback.

**Observed consequence.** The decision records included/excluded products, common assumptions, intended variation and what demand or contradiction would reopen it. Economic adequacy is a separate judgement, not proved by the existence of S.

**Boundary and cheap form.** A small comparison table and direct expert review can be enough. No similarity threshold or universal break-even count is inferred.

Properties: `ESPLE-001`, `ESPLE-002`, `ESPLE-003`, `ESPLE-036`, `ESPLE-037`, `ESPLE-038`, `ESPLE-059`. Sources: [ESPLE-S003; ESPLE-S005; ESPLE-S007; ESPLE-S012; ESPLE-S026; ESPLE-S041].

### ESPLE-DM-02 — Domain/application feedback and decision responsibility

**Purpose.** Keep reusable capability development connected to actual product production without forcing a serial lifecycle.

**Objects and state.** Domain state contains assets, constraints and production knowledge; application state contains requested/realised products, local differences and observations. Responsibility for these states may be held by the same people.

**Operation and decisions.** Product requests and failures flow to asset maintainers with baseline context. Maintainers may revise a core asset or model, decline generalisation, retain an exception or reopen scope. New core releases return constraints and evidence to products. Work can proceed concurrently on compatible baselines; conflicts require a decision rather than an automatic merge.

**Observed consequence.** Every consequential feedback item has a consumer and a disposition; product builders can identify the baseline and limits they inherit. Observing a problem, being able/authorised to change it and establishing the result are separate steps.

**Boundary and cheap form.** Use direct coordination in a small family. No new team, meeting ritual or autonomous controller follows from the model.

Properties: `ESPLE-004`, `ESPLE-005`, `ESPLE-006`, `ESPLE-007`, `ESPLE-039`, `ESPLE-040`. Sources: [ESPLE-S006; ESPLE-S008; ESPLE-S009; ESPLE-S010; ESPLE-S013; ESPLE-S041].

### ESPLE-DM-03 — Feature and constraint semantics

**Purpose.** Describe permitted selections and the meaning needed to use them in product decisions.

**Objects and state.** For Boolean features F and encoded constraints φ, Cφ = {c in {0,1}^F | φ(c)}. Richer models replace Boolean valuations with typed domains. Domain-valid choices Cdomain need not equal Cφ. A feature interpretation links selections to stakeholder meaning.

**Operation and decisions.** Check satisfiability, forced/dead options and conflicts; explain actionable repairs; validate accepted and rejected combinations against domain evidence. Translation or model evolution uses explicit feature correspondence rather than names alone.

**Observed consequence.** A SAT witness establishes membership of Cφ, not membership of Cdomain without adequacy evidence and not correctness of an implementation. An anomaly is a diagnostic to interpret, not automatically an error.

**Boundary and cheap form.** Use explicit enumeration or a decision table when small. Arithmetic, cardinality and typed extensions are optional but must not be discarded silently by tools.

Properties: `ESPLE-008`, `ESPLE-009`, `ESPLE-010`, `ESPLE-011`, `ESPLE-012`, `ESPLE-030`, `ESPLE-046`. Sources: [ESPLE-S005; ESPLE-S014; ESPLE-S015; ESPLE-S023; ESPLE-S032; ESPLE-S041].

### ESPLE-DM-04 — Variability realisation and binding

**Purpose.** Relate domain selections to actual artefacts and determine when unresolved choices become fixed.

**Objects and state.** M is a possibly many-to-many relation between features, artefact fragments and variation points. Each variation point has a resolution stage. A product transformation D consumes asset versions, configuration and relevant tool/environment inputs.

**Operation and decisions.** Choose conditional selection, parameters, modules, plugins/inheritance, aspects, deltas or generators according to the variation. Deltas require applicable ordered transformations; annotated systems require faithful presence conditions. Late binding carries additional runtime state and transition obligations.

**Observed consequence.** A realisation check establishes R(D(A,c,t,e), c): that the produced artefacts realise the intended selection. Successful generation or compilation alone does not establish R or required behaviour.

**Boundary and cheap form.** This equation is an analytical schema, not a universal deterministic generator theorem. A reviewed manual derivation may implement D adequately.

Properties: `ESPLE-013`, `ESPLE-014`, `ESPLE-015`, `ESPLE-016`, `ESPLE-017`, `ESPLE-054`, `ESPLE-055`. Sources: [ESPLE-S016; ESPLE-S017; ESPLE-S018; ESPLE-S030; ESPLE-S041; ESPLE-S042].

### ESPLE-DM-05 — Asset and derivation provenance

**Purpose.** Make a produced product supportable and keep evidence attached to the baseline that actually generated it.

**Objects and state.** A product identity includes relevant model/configuration, core assets, generator/build/dependency versions, consequential environment inputs and the resulting artefact identity. The needed equivalence relation may be semantic, structural or byte-level.

**Operation and decisions.** Execute a version-related production plan, record or retain the inputs needed for the declared reconstruction claim and validate output at the relevant level. Reference architectures supply enforceable obligations only where the real process checks or constrains conformance.

**Observed consequence.** A second builder can reproduce the needed result or explain differences; a failure report can be located in configuration and baseline space. Hash identity cannot establish semantic adequacy.

**Boundary and cheap form.** No universal requirement for byte-for-byte builds or full automation. Retention is scoped to support and assurance needs.

Properties: `ESPLE-018`, `ESPLE-019`, `ESPLE-020`, `ESPLE-021`, `ESPLE-022`, `ESPLE-056`. Sources: [ESPLE-S006; ESPLE-S009; ESPLE-S011; ESPLE-S021; ESPLE-S033; ESPLE-S041].

### ESPLE-DM-06 — Configuration-space assurance

**Purpose.** Choose and compose evidence without confusing configuration coverage with product correctness.

**Objects and state.** The relevant space is Ω = configurations × ordinary inputs × environments × baselines, restricted by actual obligations. An analysis or test covers a declared subset or property of Ω. A model check, a parser and a behavioural test have different objects.

**Operation and decisions.** Select product-based, feature/compositional, family-based or hybrid analysis. Reuse results only with checked premises. Sampling trades execution cost against omitted cases; known interactions can justify risk-directed additions. Shared failures interrupt the normal derivation path and trigger impact analysis.

**Observed consequence.** Each claim names what is quantified, its oracle and the product identities to which it applies. Conditional static warnings remain warnings unless confirmed; complete configuration coverage does not mean all behaviours were checked.

**Boundary and cheap form.** The smallest adequate form can be all supported products plus targeted tests. Family-wide symbolic work is optional and may lose to ordinary analysis for small families.

Properties: `ESPLE-023`, `ESPLE-024`, `ESPLE-025`, `ESPLE-026`, `ESPLE-027`, `ESPLE-028`, `ESPLE-029`, `ESPLE-052`, `ESPLE-053`. Sources: [ESPLE-S019; ESPLE-S020; ESPLE-S021; ESPLE-S022; ESPLE-S040; ESPLE-S041].

### ESPLE-DM-07 — Family evolution, migration and retirement

**Purpose.** Preserve or explicitly revise supported product obligations through changes in models, assets and production.

**Objects and state.** At baseline k the family has model φk, assets Ak, supported product identities Pk and evidence Ek. A migration m maps old products/selections to new ones with explicit feature correspondence and intent. Legacy admission to new products is distinct from support of old ones.

**Operation and decisions.** Classify model differences, identify shared-asset impact, select migration or parallel support, update tests and accept actual products. Extracted constraints can repair a stale model only after domain reconciliation. Retirement may first forbid new selection while preserving older baselines.

**Observed consequence.** A migrated product meets the intended preserved obligations or records accepted changes. Ek is not automatically evidence for baseline k+1. Configuration-distance minimisation is not a proof of minimal labour or unchanged behaviour.

**Boundary and cheap form.** Manual migration or a supported old baseline can be adequate. No compulsory simultaneous release or eventual reintegration of every exception.

Properties: `ESPLE-030`, `ESPLE-031`, `ESPLE-032`, `ESPLE-033`, `ESPLE-034`, `ESPLE-035`, `ESPLE-058`, `ESPLE-061`. Sources: [ESPLE-S011; ESPLE-S023; ESPLE-S024; ESPLE-S025; ESPLE-S037; ESPLE-S041].

### ESPLE-DM-08 — Organisational economics and external constraints

**Purpose.** Choose a feasible production arrangement while accounting for the parties who bear its costs and obligations.

**Objects and state.** For an explicit horizon compare SPL cost = organisational transition + core assets + product derivation + assurance + coordination + support/migration/exit with equivalent-outcome alternatives. These are cost categories, not measured universal coefficients. Authority and external obligations constrain admissible alternatives before cost ranking.

**Operation and decisions.** Use scenarios and observed product experience to revisit investment, team capacity, exceptions and scope. Negotiate with external participants where there is no internal authority. A shared specification ecosystem is not automatically one product-production organisation.

**Observed consequence.** The decision identifies cost bearers, demand assumptions, omitted costs and conditions that reverse preference. No claimed causal benefit follows merely from adopting a standard or successful organisation.

**Boundary and cheap form.** A coarse comparison can be sufficient; no universal ROI, break-even count or required governance structure is asserted.

Properties: `ESPLE-036`, `ESPLE-037`, `ESPLE-038`, `ESPLE-039`, `ESPLE-040`, `ESPLE-041`, `ESPLE-042`, `ESPLE-049`, `ESPLE-057`, `ESPLE-059`. Sources: [ESPLE-S012; ESPLE-S013; ESPLE-S026; ESPLE-S027; ESPLE-S028; ESPLE-S029; ESPLE-S041; ESPLE-S044].

### ESPLE-DM-09 — Dynamic configuration transitions and learned proposals

**Purpose.** Keep runtime or learned changes inside justified configuration, transition, authority and evidence boundaries.

**Objects and state.** A dynamic state is (c,s,e): feature selection, operational state and relevant environment. Edges represent feasible actions with guards, effects and controllability. A learned proposal is an input to checking, not an edge that is automatically authorised.

**Operation and decisions.** Observe context, propose a permitted target, check a feasible safe path, execute authorised actions and observe the result. A safe offline phase or actual atomic transfer can justify transitions otherwise unsafe, but cannot be assumed. Model/tool changes require re-establishing the guarantees they affect.

**Observed consequence.** Safe endpoints do not prove safe edges. Supervisory nonblocking is reachability of marked states, not inevitable completion. Issuing a command does not establish its effect. Fixed features do not imply fixed environmental behaviour.

**Boundary and cheap form.** Choose static/deployment binding, deterministic migration or advisory-only output when richer operation is not warranted. Physical safety and learned-output generalisation remain assumption-bound.

Properties: `ESPLE-043`, `ESPLE-044`, `ESPLE-045`, `ESPLE-046`, `ESPLE-047`, `ESPLE-048`, `ESPLE-060`, `ESPLE-062`. Sources: [ESPLE-S030; ESPLE-S031; ESPLE-S032; ESPLE-S034; ESPLE-S038; ESPLE-S043; ESPLE-S045].

### Domain-profile resolution

Every property contains all ten domain dimensions. The reusable P1–P10 profiles state family scope, commonality assumptions, feature semantics, binding time, asset/product relation, derivation identity, interaction coverage, evolution obligations, ownership/exception policy and economics/non-family alternatives. Each record additionally binds those dimensions to its own trigger, inputs, mechanism, acceptance boundary and retirement condition. Shared profile text does not erase a property’s distinct prerequisites; consumers must read the property-specific binding as well as the family profile.

| Family | Profile | Examined question focus | Candidate IDs |
| --- | --- | --- | --- |
| P1 | Product-family scope and evidence of commonality | Which shared assumptions warrant this family, and which plausible product would invalidate them? | ESPLE-001, ESPLE-002, ESPLE-003 |
| P2 | Domain engineering and application engineering | How are shared capabilities and product-specific realisation distinguished without blocking feedback? | ESPLE-004, ESPLE-005, ESPLE-006, ESPLE-007, ESPLE-050 |
| P3 | Features, variability models and constraints | What does selecting this feature commit the resulting product to provide? | ESPLE-008, ESPLE-009, ESPLE-010, ESPLE-011, ESPLE-012, ESPLE-051 |
| P4 | Variability realisation and binding time | What information arrives late enough to justify retaining this variation point until that stage? | ESPLE-013, ESPLE-014, ESPLE-015, ESPLE-016, ESPLE-017, ESPLE-054, ESPLE-055 |
| P5 | Core assets, reference architectures and product derivation | Which reusable non-code assets materially support products, and which are merely maintained because a template expects them? | ESPLE-018, ESPLE-019, ESPLE-020, ESPLE-021, ESPLE-022, ESPLE-056 |
| P6 | Feature interaction and verification across a family | Which conclusion follows from this evidence, and which additional premise would be needed for the stronger conclusion being asserted? | ESPLE-023, ESPLE-024, ESPLE-025, ESPLE-026, ESPLE-027, ESPLE-028, ESPLE-029, ESPLE-052, ESPLE-053 |
| P7 | Family evolution and configuration migration | Which products become possible or impossible after the edit, under what mapping of feature meanings? | ESPLE-030, ESPLE-031, ESPLE-032, ESPLE-033, ESPLE-034, ESPLE-035, ESPLE-058, ESPLE-061 |
| P8 | Adoption strategies, economics and alternatives | Under which plausible assumptions does the product-line investment cease to be preferable? | ESPLE-036, ESPLE-037, ESPLE-038, ESPLE-049, ESPLE-057, ESPLE-059 |
| P9 | Organisations, governance and ecosystems | Who may change shared assets, and how are affected product obligations represented in that decision? | ESPLE-039, ESPLE-040, ESPLE-041, ESPLE-042 |
| P10 | Dynamic product lines and modern derivatives | What observed context justifies each runtime configuration change, and how is the actual resulting state established? | ESPLE-043, ESPLE-044, ESPLE-045, ESPLE-046, ESPLE-047, ESPLE-048, ESPLE-060, ESPLE-062 |



## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_CEREMONY_STRIPPING_LEDGER

The protected object is a useful decision, constraint, product or observation—not the presence of an artefact. The complete JSON ceremony ledger has one entry for every candidate, including rejected and unresolved candidates. For retained mechanisms it names the consumer, prerequisites, cheaper path, trigger for a fuller form, simplification risk and retirement condition. The grouped comparison below exposes the principal practical choices. These are analytical selection rules, not reported controlled trials of removing paperwork.

| Artefact or practice | Real function and consumer | Minimal adequate alternative | Trigger for fuller form / omission boundary |
| --- | --- | --- | --- |
| Scoping workshop and portfolio matrix | Test actual family assumptions with product representatives. | Reviewed examples and explicit exclusions. | Use richer analysis when disputed assumptions or investment could change the decision; omit a family programme for incidental reuse. |
| Separate domain/application departments | Keep shared and product consequences visible. | The same people can perform both responsibilities with explicit feedback. | Separate teams only when workload and ownership justify them; do not add a team per property. |
| Feature tree or language | Represent consequential choices and constraints for configurators and domain experts. | A decision table or clear configuration instruction. | Richer types/solvers when interactions exceed reliable manual reasoning; retire orphaned models. |
| Traceability repository | Connect a failing product or change to its feature, asset and build origin. | Versioned mappings at the boundaries actually used in diagnosis. | Detailed traceability when impact/provenance demand it; stale links are not useful assurance. |
| Generator framework | Avoid repeated derivation while preserving intended realisation. | A reviewed template or manual procedure for a small stable family. | Generation when repeated work warrants it; remove generator-specific controls if generation disappears. |
| Reference architecture document | Constrain products where invariants matter or communicate reusable design. | Small interface/constraint descriptions consumed by derivation and acceptance. | More detail when it changes implementation or review; a document alone cannot enforce itself. |
| Universal configuration campaign | Establish specified product outcomes across a space. | Risk-directed product checks or justified sampling. | Exhaustive work only when feasible and consequential; never turn sample coverage into a general correctness claim. |
| Formal family analysis | Share a supported computation across represented variants. | Ordinary product analysis for a few products or unsupported languages. | Use when representation and sharing benefit are demonstrable; retire when infrastructure dominates. |
| Migration plan and change board | Preserve supported product intent and coordinate shared changes. | A small explicit impact decision and checks by affected owners. | Richer coordination when multiple products or obligations conflict; no universal committee requirement. |
| ROI spreadsheet | Compare real alternatives under uncertainty. | Coarse scenarios with reversal conditions. | More precision only when credible and decision-relevant; configuration count is not benefit. |
| Runtime adaptation supervisor | Control permitted transitions under actual sensing and action assumptions. | Earlier binding or a simple verified transition protocol. | Synthesis for the modelled dynamic problem, not generic flexibility; omit runtime machinery from static families. |
| Learned recommendation | Generate a candidate configuration or change for independent evaluation. | Conventional derivation or bounded manual change. | Use only where validation and total cost are adequate; the assistant cannot authorise its own output. |

**Retirement is not abandonment of evidence.** Removing an obsolete model, tool or variation point may reduce cost. Removing the only information needed to support an existing product may instead destroy the mechanism. ESPLE-061 therefore couples retirement to support and migration, while each individual ceremony record states the consequence that simplification must preserve.

## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_CRITICISM_LEDGER

Criticism was allowed to change the primary judgements. The ledger separates observed problems, model restrictions and this study’s inference. An adverse implementation does not refute a theorem whose assumptions it violates; it can still refute a claim that the implementation delivered the promised assurance. Conversely, describing a failed programme as “not real SPLE” is not a substitute for examining its actual mechanisms.

### ESPLE-C01

Affected: `ESPLE-001`, `ESPLE-002`, `ESPLE-003`, `ESPLE-038`. **Strongest objection:** Precise family models can formalise the wrong scope; too-broad commonality makes unrelated products pay for each other.

**Evidence and locator:** PuLSE explicitly responds to impractical domain-engineering scope. Bosch reports mixed dependencies across selected products and the inadequacy of one stale global model. [ESPLE-S007; ESPLE-S041]; S007 motivation/scoping; S041 Sections 2, 4–6.

**Response and later findings:** Product-focused scope and subsystem-aligned models narrow the coordination boundary; neither requires erasing common knowledge.

**Present judgement (NARROWED):** Retain warranted scope, reject vocabulary or code duplication as sufficient family evidence. Split or narrow when assumptions conflict.

**Residual uncertainty:** No universal similarity measure predicts useful family scope or future demand.

### ESPLE-C02

Affected: `ESPLE-007`, `ESPLE-036`, `ESPLE-049`, `ESPLE-050`. **Strongest objection:** Upfront platform investment can outrun uncertain demand and consume resources before any payoff.

**Evidence and locator:** Adoption methods explicitly propose reactive/extractive alternatives; SIMPLE makes returns depend on multiple cost terms rather than a universal product count. [ESPLE-S010; ESPLE-S012; ESPLE-S013]; S010 introduction/Section 4; S012 economic scenarios; S013 failure discussion.

**Response and later findings:** Choose a staged route or no product-line transition when the business and asset conditions do not justify anticipation.

**Present judgement (REFINED):** Retain strategy selection and sensitivity analysis; reject compulsory full upfront platforms and universal break-even numbers.

**Residual uncertainty:** Forecast error and unreported failed programmes prevent a general probability of success.

### ESPLE-C03

Affected: `ESPLE-006`, `ESPLE-007`, `ESPLE-037`, `ESPLE-057`. **Strongest objection:** Shared production can cost more than locally independent variants; cloning is not necessarily careless engineering.

**Evidence and locator:** Qualitative industrial accounts describe autonomy and startup advantages. A small BSH task comparison favours SPLE in its setting, while later debt evidence describes unsynchronised-asset burdens. [ESPLE-S026; ESPLE-S027; ESPLE-S028]; S026 study design/results; S027 experiment and validity; S028 institutional abstract.

**Response and later findings:** Use a lifecycle and obligation-matched comparison; bounded exceptions or selective reuse can preserve autonomy without losing all provenance.

**Present judgement (STILL_CONTESTED):** Reject anti-cloning universality, but do not infer lifetime cloning superiority from practitioners explaining why they use it.

**Residual uncertainty:** Matched longitudinal portfolio comparisons including transition and exit costs remain scarce in the inspected corpus.

### ESPLE-C04

Affected: `ESPLE-008`, `ESPLE-011`, `ESPLE-014`, `ESPLE-051`. **Strongest objection:** Models and traces can become elaborate but unused documentation.

**Evidence and locator:** Original FODA includes rationale and dependency information; Bosch reports central models falling out of use and a tension between simplified formulas and traceability to code. [ESPLE-S005; ESPLE-S015; ESPLE-S041]; S005 Section 7.3.2; S015 analysis-operation discussion; S041 Sections 2, 3.5.

**Response and later findings:** Require a real configuration, derivation or impact consumer; align representation and ownership with maintained assets.

**Present judgement (REFINED):** Retain semantics and needed traceability; feature-tree presence is ceremony, not fulfilment.

**Residual uncertainty:** The minimum useful representation varies with team knowledge and interaction scale.

### ESPLE-C05

Affected: `ESPLE-009`, `ESPLE-010`, `ESPLE-012`, `ESPLE-034`, `ESPLE-052`. **Strongest objection:** A consistent or reverse-engineered constraint set can permit products that make no sense in the domain.

**Evidence and locator:** The Bosch case explicitly distinguishes feature-effect constraints from complete domain knowledge and describes omitted artefact types and approximations. [ESPLE-S014; ESPLE-S015; ESPLE-S041]; S014 logic encoding; S041 Section 6 construct validity.

**Response and later findings:** Use independent positive/negative domain cases and expert review; keep encoded validity separate from domain and implementation validity.

**Present judgement (NARROWED):** Strong formal consistency survives, while claims of comprehensive validity are narrowed.

**Residual uncertainty:** No finite example set establishes complete domain knowledge without further assumptions.

### ESPLE-C06

Affected: `ESPLE-013`, `ESPLE-014`, `ESPLE-015`, `ESPLE-016`, `ESPLE-055`. **Strongest objection:** Neither annotation nor feature modularity universally avoids scattering, interaction glue and coordination problems.

**Evidence and locator:** FOSD discusses complementary implementation mechanisms; deltas add removals/changes; Bosch combines component selection and conditional compilation. [ESPLE-S017; ESPLE-S018; ESPLE-S041]; S017 Sections 4.3–4.4; S018 delta construction; S041 Section 2.

**Response and later findings:** Select mechanisms by granularity, binding time and change needs; expose many-to-many realisation and ordering obligations.

**Present judgement (HYBRIDISED):** Retain a portfolio; do not prescribe one feature/one module or replace every conditional with specialised machinery.

**Residual uncertainty:** Comparative lifecycle benefits of mixed realisation remain highly setting-dependent.

### ESPLE-C07

Affected: `ESPLE-017`, `ESPLE-021`, `ESPLE-023`, `ESPLE-028`, `ESPLE-052`. **Strongest objection:** Configuration validity does not ensure a working generated stack.

**Evidence and locator:** The bounded JHipster study reports thousands of failing valid configurations associated with a small number of interaction faults; the text contains a one-configuration count discrepancy. [ESPLE-S021]; S021 Sections 5–7 and results for version 3.6.1.

**Response and later findings:** Separate model, generation/build and product-behaviour claims; preserve failing configuration and baseline identity.

**Present judgement (REJECTED):** Reject SAT-to-product correctness. The empirical result demonstrates possibility and materiality in one version, not current prevalence.

**Residual uncertainty:** No universal failure rate follows from a single generator or its historical test workflow.

### ESPLE-C08

Affected: `ESPLE-024`, `ESPLE-025`, `ESPLE-026`, `ESPLE-053`. **Strongest objection:** Pairwise coverage misses higher-order or non-configuration faults, and sampling rankings depend on realistic cost and extraction assumptions.

**Evidence and locator:** Sampling comparisons and exhaustive bounded testing expose different trade-offs. Variability-aware static analysis compares warnings, not adjudicated bug incidence. [ESPLE-S020; ESPLE-S021; ESPLE-S040]; S020 RQ1–RQ3; S021 sampling comparison; S040 validity discussion.

**Response and later findings:** Select by claim and budget; add risk-directed checks or family analysis when supported. Report actual costs and residual coverage.

**Present judgement (NARROWED):** Retain sampling conditionally; reject completeness claims and warnings-as-fault-prevalence.

**Residual uncertainty:** Risk distributions in future products and omitted environments are not known from these benchmarks.

### ESPLE-C09

Affected: `ESPLE-023`, `ESPLE-026`, `ESPLE-027`, `ESPLE-029`, `ESPLE-045`. **Strongest objection:** A sound analysis of an incomplete representation gives false confidence about an implementation or physical environment.

**Evidence and locator:** Missing build layers, approximate extraction, pointer-analysis limits and modelled controllability constrain transfer. [ESPLE-S019; ESPLE-S022; ESPLE-S031; ESPLE-S040; ESPLE-S041]; S019 strategy assumptions; S031 Sections 4–8; S040 printed p. 26; S041 Section 6.

**Response and later findings:** Keep the theorem or analysis result, but expose and check representation and implementation obligations separately.

**Present judgement (NARROWED):** Strong internal validity is compatible with weak deployment evidence; do not weaken the theorem or exaggerate its reach.

**Residual uncertainty:** Model adequacy is an engineering evidence burden, not supplied by syntactic proof completion.

### ESPLE-C10

Affected: `ESPLE-030`, `ESPLE-031`, `ESPLE-032`, `ESPLE-035`, `ESPLE-058`. **Strongest objection:** Preserved configuration sets or minimal selection changes do not prove preserved product intent, behaviour or maintenance effort.

**Evidence and locator:** Model comparison and migration algorithms operate on declared representations. Test-evolution research acknowledges that configuration distance may not represent real editing effort. [ESPLE-S023; ESPLE-S024; ESPLE-S037]; S023 semantic edit classification; S024 migration model; S037 Sections 6–9.

**Response and later findings:** Add explicit feature correspondence and product acceptance; choose regression and novelty-oriented test objectives deliberately.

**Present judgement (REFINED):** Retain model-level methods with bounded claims; reject behavioural compatibility inferred from names or set equality.

**Residual uncertainty:** Real-world effort and higher-order evolution need more direct evidence.

### ESPLE-C11

Affected: `ESPLE-007`, `ESPLE-036`, `ESPLE-037`, `ESPLE-040`. **Strongest objection:** A short industrial task experiment is not a causal estimate of whole-programme SPLE return.

**Evidence and locator:** Ten engineers each perform four tasks: forty task observations are clustered within people, not forty independent engineers. Platform preparation and migration investment are not measured. [ESPLE-S027]; S027 participant design, tasks, results and validity discussion.

**Response and later findings:** Treat the observed task comparison as local evidence. Our methodological caution does not reanalyse unavailable raw data or claim a published correction.

**Present judgement (NARROWED):** Retain the local favourable finding, reject its use as a universal payoff or independent-sample denominator.

**Residual uncertainty:** A robust longitudinal comparison would measure repeated changes, preparation, support and participant clustering.

### ESPLE-C12

Affected: `ESPLE-004`, `ESPLE-005`, `ESPLE-006`, `ESPLE-039`, `ESPLE-040`. **Strongest objection:** Central asset ownership can create bottlenecks and misaligned incentives while product teams carry delivery obligations.

**Evidence and locator:** Failures and practical variation strategies reveal organisational constraints not solved by code reuse or tool deployment. [ESPLE-S013; ESPLE-S026; ESPLE-S028; ESPLE-S041]; S013 experience/failure discussion; S026 industrial findings; S028 abstract; S041 Section 2.

**Response and later findings:** Make decision rights and resources explicit; decentralise where responsibilities and model composition support it; permit bounded exceptions.

**Present judgement (REFINED):** Retain accountable shared decisions, not a universal central team or committee.

**Residual uncertainty:** There is no evidence here for a universally optimal team topology or meeting frequency.

### ESPLE-C13

Affected: `ESPLE-013`, `ESPLE-043`, `ESPLE-044`, `ESPLE-054`, `ESPLE-060`. **Strongest objection:** Valid endpoints can be joined by unsafe transitions, and a modelled atomic action may not be realisable.

**Evidence and locator:** Early dynamic work leaves transition safety open; supervisory-control work explicitly models events and requirements. [ESPLE-S030; ESPLE-S031]; S030 discussion of safe/quiescent reconfiguration; S031 Sections 4–7.

**Response and later findings:** Check path/state continuity, actual controllability and safe reconfiguration phases; prefer offline selection when live operation cannot be justified.

**Present judgement (REFINED):** Transition safety is strongly retained when live rebinding occurs; runtime flexibility is not universally preferred.

**Residual uncertainty:** Sensor accuracy, timing and physical actuation may remain outside the analysed model.

### ESPLE-C14

Affected: `ESPLE-043`, `ESPLE-044`, `ESPLE-045`. **Strongest objection:** An industrial-origin benchmark is mistaken for deployment evidence or safety certification.

**Evidence and locator:** The Body Comfort System demonstrates model construction and synthesis, not a reported operational vehicle deployment. [ESPLE-S031]; S031 Section 8 and model-assumption discussion.

**Response and later findings:** Preserve the formal result and bounded case scale, while requiring separate model/plant and operational evidence.

**Present judgement (DOMAIN_SPECIFIC):** Supervisory control remains domain-specific; nonblocking is not inevitable progress on all executions.

**Residual uncertainty:** Independent deployment validation and behaviour under model mismatch are not established here.

### ESPLE-C15

Affected: `ESPLE-012`, `ESPLE-046`, `ESPLE-056`. **Strongest objection:** A shared syntax or a specialised standard is universalised into semantic interoperability or a definition of all SPLE.

**Evidence and locator:** UVL has defined expressive levels and tool boundaries. The ISO public scope calls feature-based PLE a specialisation of a broader reference model. [ESPLE-S032; ESPLE-S033]; S032 language levels and discussion; S033 public scope.

**Response and later findings:** Check supported versions/semantics and state the narrow normative scope actually inspected.

**Present judgement (NARROWED):** Retain checked interchange; reject total automation as a universal field definition.

**Residual uncertainty:** Unseen normative clauses and the legal history of earlier language initiatives are not inferred.

### ESPLE-C16

Affected: `ESPLE-047`, `ESPLE-048`. **Strongest objection:** Plausible learned changes or small examples are promoted into reliable autonomous product-family evolution.

**Evidence and locator:** The inspected regeneration proposal is exploratory; adjacent DSL evaluation exposes scale/complexity limits. A direct SPLC co-evolution paper and later regeneration version remain access-limited. [ESPLE-S034; ESPLE-S036; ESPLE-S038]; S034 exploratory study/limitations; S036 access-limited record; S038 design/results.

**Response and later findings:** Use learned output as a proposal with independent validation and matched deterministic/manual alternatives.

**Present judgement (STILL_CONTESTED):** Retain bounded assistance as assumption-sensitive; leave replacement superiority unresolved rather than adopt or dismiss it without evidence.

**Residual uncertainty:** Repeated-change continuity, unseen-version results and full lifecycle comparisons could change the replacement judgement.

### ESPLE-C17

Affected: `ESPLE-003`, `ESPLE-038`, `ESPLE-059`, `ESPLE-061`. **Strongest objection:** More variability is treated as progress; removal is treated as harmless because current products rarely use an option.

**Evidence and locator:** Legacy variation can remain needed for old products, while smaller programs also demonstrate that options can be bound earlier or removed. [ESPLE-S041; ESPLE-S045]; S041 legacy-variability treatment; S045 Sections 5.4, 7 and 8.

**Response and later findings:** Separate admission to new products from existing support; keep usage uncertainty and migration costs explicit.

**Present judgement (REFINED):** Retain support-aware retirement, not maximal variability or automatic deletion of low-frequency options.

**Residual uncertainty:** Observed use can miss rare but consequential requirements; code-size correlations do not establish causal maintenance savings.

### ESPLE-C18

Affected: `ESPLE-001`, `ESPLE-041`. **Strongest objection:** A shared ecosystem specification is assumed to imply a centrally managed core and enforceable product derivation.

**Evidence and locator:** Community-driven variability distinguishes autonomous proposal/implementation evolution from classical product-line production. [ESPLE-S029; ESPLE-S044]; S029 organisational boundary; S044 Sections 1, 4–5.

**Response and later findings:** Keep ecosystem interfaces and documentary intersections, but do not impose internal SPLE control over independent participants.

**Present judgement (NARROWED):** Preserve a conditional external interface; full unification with autonomous ecosystems is not established.

**Residual uncertainty:** Taxonomy and classification do not demonstrate effective governance or the payoff of proposed feature-oriented tooling.

### ESPLE-C19

Affected: `ESPLE-002`, `ESPLE-007`, `ESPLE-024`, `ESPLE-026`, `ESPLE-036`, `ESPLE-037`, `ESPLE-045`, `ESPLE-047`. **Strongest objection:** Repeated papers or reports about the same industrial programme or benchmark are counted as independent replication.

**Evidence and locator:** SEI/Lucent experience, TypeChef/configurable-C subjects, BCS and repeated observations within studies create evidence dependence. [ESPLE-S006; ESPLE-S013; ESPLE-S020; ESPLE-S021; ESPLE-S027; ESPLE-S031; ESPLE-S040]; Cross-source programme/dataset metadata in source table and empirical register.

**Response and later findings:** Record programme and dataset clusters and distinguish units, organisations, products, tasks and model runs.

**Present judgement (REFINED):** No aggregate confidence percentage or pooled causal effect is computed.

**Residual uncertainty:** Complete overlap cannot be established for inaccessible datasets; possible overlap is retained as uncertainty.

### ESPLE-C20

Affected: `ESPLE-001`, `ESPLE-012`, `ESPLE-013`, `ESPLE-043`, `ESPLE-046`, `ESPLE-047`, `ESPLE-048`. **Strongest objection:** Bibliographic discovery or abstract access is presented as full reconstruction of methodology, clauses or empirical outcomes.

**Evidence and locator:** Several canonical works, normative text and recent publications were accessible only in part despite lawful alternate attempts. [ESPLE-S002; ESPLE-S004; ESPLE-S008; ESPLE-S028; ESPLE-S033; ESPLE-S036; ESPLE-S039; ESPLE-S042; ESPLE-S043]; Access levels and claim locators in source table.

**Response and later findings:** Use separate inspected primary works for mechanisms; retain the limited work only for supported history or problem scope.

**Present judgement (NARROWED):** Examination may be complete within an explicit evidence limit without inventing the missing content.

**Residual uncertainty:** These access limits bound historical detail and particular modern results; they are not negative findings about the works.

### ESPLE-C21

Affected: `ESPLE-013`, `ESPLE-061`, `ESPLE-062`. **Strongest objection:** Early binding of all selectable features is used to infer context-independent behaviour.

**Evidence and locator:** The proposal also allows non-identical outputs; its broad wording is not a proof that ordinary inputs, state or environment have no effect. [ESPLE-S045]; S045 Sections 7.2 P3, 7.3 and 8.

**Response and later findings:** Retain fixed configurability as a useful distinction; separately model ordinary execution and environmental assumptions.

**Present judgement (NARROWED):** Reject the stronger implication with an analytical counterexample, without attributing a claim of identical output for every input to the authors.

**Residual uncertainty:** A narrower formal semantics could clarify the intended behavioural consistency; it would not establish arbitrary environmental robustness.

### ESPLE-C22

Affected: `ESPLE-018`, `ESPLE-019`, `ESPLE-020`, `ESPLE-021`, `ESPLE-022`, `ESPLE-056`. **Strongest objection:** A complete-looking asset inventory, architecture document or automated build can remain disconnected from the actually produced product.

**Evidence and locator:** Production-plan guidance names the assets and production relationships; configurable-generator and reverse-engineering studies expose realisation and heterogeneous-artefact limits. [ESPLE-S011; ESPLE-S021; ESPLE-S041]; S011 production-plan development and version management; S021 Results/Discussion; S041 Sections 3–6.

**Response and later findings:** Retain only consequential asset and tool identity, make the plan consumable by derivation, define repeatability equivalence and test outputs independently.

**Present judgement (REFINED):** Retain production control, not maximal documentation or universal byte-for-byte build identity. This is a synthesis of distinct evidence, not a reported comparative trial of provenance policies.

**Residual uncertainty:** The least costly sufficient provenance and architecture enforcement depend on the failure consequences and actual build environment.

### ESPLE-C23

Affected: `ESPLE-006`, `ESPLE-032`, `ESPLE-033`, `ESPLE-039`, `ESPLE-042`, `ESPLE-061`. **Strongest objection:** Uniform propagation and forced simplification can violate the obligations of a supported product; preserving every exception can in turn destroy the economics of sharing.

**Evidence and locator:** Industrial cloning and Bosch observations show heterogeneous product obligations and propagation/support difficulties; ecosystem work separates organisational authorities. [ESPLE-S011; ESPLE-S026; ESPLE-S029; ESPLE-S041]; S011 version management; S026 findings on propagation; S029 organisational expansion; S041 Section 3 legacy/commonality discussion.

**Response and later findings:** Coordinate impact, preserve identified support baselines where justified, and explicitly decide differentiated repair or retirement with those responsible for the product.

**Present judgement (NARROWED):** Support and external obligations constrain core change, but no source establishes an unlimited duty to maintain every variant indefinitely. Exact legal or contractual content remains an external input.

**Residual uncertainty:** No universal exception budget or support duration follows from this tradition.



## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_EVOLUTION_UNDER_CRITICISM

Evolution under criticism does not mean steadily adding machinery. The following transitions describe actual changes in method or in the warranted interpretation of a result. The historical sources and analytical response remain distinguishable in each criticism record.

| Earlier claim or mechanism | Pressure | Surviving change | Relevant records |
| --- | --- | --- | --- |
| Broad domain-engineering investment | Impractical scope and uncertain product demand | Narrow to product-focused scope and choose proactive/reactive/extractive entry. | ESPLE-C01, ESPLE-C02; ESPLE-G05, ESPLE-G07 |
| Implicit or tree-only feature reasoning | Dependencies, false optionality, missing meanings | Add explicit semantics and diagnostics while preserving the domain-adequacy boundary. | ESPLE-C04, ESPLE-C05 |
| Purely additive feature composition | Removal/modification and cross-cutting variation | Keep delta-oriented and other realisations as guarded alternatives, not a universal replacement. | ESPLE-C06; ESPLE-G10 |
| One central variability model | Staleness, mixed artefacts and unsustainable update responsibility | Narrow model ownership and scope; reconcile boundaries and domain intent. | ESPLE-C04, ESPLE-C05; ESPLE-CASE-10 |
| Sampling or family analysis as complete assurance | Higher-order faults, unsupported representations, warning imprecision | Narrow claims and combine evidence only where the combination covers different failures. | ESPLE-C08, ESPLE-C09 |
| Model-set preservation as product continuity | Changed meanings, generators and obligations | Couple configuration migration with intent, realisation and acceptance; co-evolve tests. | ESPLE-C10 |
| Universal adoption benefit / cloning prohibition | Industrial autonomy, setup cost and propagation debt | Retain adequate alternatives and scenario-based lifecycle comparison. | ESPLE-C03, ESPLE-C11 |
| Static validity reused at runtime | Unsafe intermediates and uncontrollable actions | Add transition and control assumptions; earlier binding remains an alternative. | ESPLE-C13, ESPLE-C14 |
| Ever-increasing configuration flexibility | Unused options, assurance and support burden | Admit and retire variation according to consumers and support obligations. | ESPLE-C17, ESPLE-C21, ESPLE-C23 |
| Learned regeneration as a replacement | Uncertain continuity, provenance and lifecycle costs | Keep validated assistance; leave replacement superiority unresolved. | ESPLE-C16 |

Some responses remain incompatible. A highly autonomous product can retain a local exception instead of accepting a common asset. A small family can prefer direct testing to a specialised family analyser. A runtime requirement may make earlier binding inadequate, while a static family has no reason to pay dynamic transition costs. The method resolves these alternatives through their assumptions and evidence, not the word “balance”.

## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_INTERNAL_TENSIONS

The protected values below are genuinely in tension. Selection is based on a discriminator, and every proposed hybrid has a possible failure mode. Cost is therefore not treated as something outside the technical method.

### ESPLE-T01 — Reuse versus Low coupling and domain fit

Properties: `ESPLE-001`, `ESPLE-002`, `ESPLE-003`, `ESPLE-019`, `ESPLE-037`.

**First side is favoured when:** Stable shared assumptions and recurrent product demand justify a common asset.

**Second side is favoured when:** Incompatible operational assumptions or incidental code similarity favour separate products or smaller common libraries.

**Supported hybrid:** A narrow shared layer plus distinct product architectures.

**Hybrid failure:** A supposedly small shared abstraction accumulates all product exceptions and becomes the original monolith.

**Uncertainty/discriminator:** Future demand and coordination costs require observation, not a similarity threshold.

### ESPLE-T02 — Standardisation versus Product autonomy

Properties: `ESPLE-004`, `ESPLE-005`, `ESPLE-006`, `ESPLE-032`, `ESPLE-039`.

**First side is favoured when:** Shared safety/interface assumptions require coordinated core decisions.

**Second side is favoured when:** A local obligation has little reuse and shared generalisation would disrupt other supported products.

**Supported hybrid:** Explicit product exception on an identified baseline with shared-fix visibility.

**Hybrid failure:** Every local difference becomes permanent undocumented drift, or every exception is forced back into the core.

**Uncertainty/discriminator:** No universal threshold says when an exception should become a new family.

### ESPLE-T03 — Anticipatory investment versus Responsiveness under uncertainty

Properties: `ESPLE-007`, `ESPLE-036`, `ESPLE-038`, `ESPLE-049`, `ESPLE-050`.

**First side is favoured when:** Known high reuse and expensive later redesign justify proactive assets.

**Second side is favoured when:** Demand is uncertain or working variants already exist; reactive or extractive routes limit sunk cost.

**Supported hybrid:** Stage investment around demonstrable commonality while retaining product delivery.

**Hybrid failure:** A nominally incremental plan still mandates a full future platform before useful products.

**Uncertainty/discriminator:** Scenario estimates should be updated from actual derivation and support costs.

### ESPLE-T04 — Product variety versus Assurability and supportability

Properties: `ESPLE-003`, `ESPLE-024`, `ESPLE-025`, `ESPLE-059`, `ESPLE-061`.

**First side is favoured when:** Valuable differentiated products justify additional variants and checks.

**Second side is favoured when:** Unused options and unmanageable interaction costs favour restriction or retirement.

**Supported hybrid:** Admit new variation only with a product case and coverage/support plan; retain old support separately.

**Hybrid failure:** A metric rewards raw configurations while test and support budgets stay fixed.

**Uncertainty/discriminator:** Rare demand and high-consequence variants can defeat frequency-only retirement.

### ESPLE-T05 — Shared assurance efficiency versus Product-specific validity

Properties: `ESPLE-023`, `ESPLE-025`, `ESPLE-026`, `ESPLE-027`, `ESPLE-028`.

**First side is favoured when:** Many products share analyzable structure and premises can be checked.

**Second side is favoured when:** A product has unique environment, integration or unrepresented behaviour.

**Supported hybrid:** Family or compositional analysis plus product checks for residual obligations.

**Hybrid failure:** Shared proof is used to skip checks of premises, or every product repeats all work despite valid reusable evidence.

**Uncertainty/discriminator:** The cheapest adequate assurance mix depends on actual properties, not labels.

### ESPLE-T06 — Runtime flexibility versus Transition safety and simplicity

Properties: `ESPLE-013`, `ESPLE-043`, `ESPLE-044`, `ESPLE-045`, `ESPLE-054`.

**First side is favoured when:** The needed context changes faster than safe offline selection can respond.

**Second side is favoured when:** Runtime change is rare, unnecessary or cannot be safely enacted with available controls.

**Supported hybrid:** Static hardware/resource choices with bounded dynamic choices in an analysed safe envelope.

**Hybrid failure:** Endpoint validity masks unsafe intermediate states or assumed atomicity.

**Uncertainty/discriminator:** Physical timing and observation limits may invalidate a modelled safe path.

### ESPLE-T07 — Automated recovery versus Domain fidelity

Properties: `ESPLE-010`, `ESPLE-012`, `ESPLE-034`.

**First side is favoured when:** Implementation constraints and relevant artefact semantics are recoverable.

**Second side is favoured when:** Domain rules or customer obligations are absent from implementation and require human input.

**Supported hybrid:** Extract candidate constraints with provenance, then reconcile with domain knowledge.

**Hybrid failure:** Extracted historical products are treated as the entire valid domain or expert additions destroy implementation consistency.

**Uncertainty/discriminator:** No extraction method establishes the value of every historical difference.

### ESPLE-T08 — Regression continuity versus Attention to new products

Properties: `ESPLE-030`, `ESPLE-031`, `ESPLE-035`.

**First side is favoured when:** Old obligations persist and existing tests are expensive to recreate.

**Second side is favoured when:** The model admits materially new configurations or fresh generation is cheaper than repair.

**Supported hybrid:** Preserve valid regression configurations and add targeted novelty coverage.

**Hybrid failure:** Configuration similarity is mistaken for low oracle-repair cost or change-specific tests abandon old obligations.

**Uncertainty/discriminator:** The current mutation study does not establish universal human-effort rankings.

### ESPLE-T09 — Shared compatibility versus Independent participation

Properties: `ESPLE-039`, `ESPLE-041`, `ESPLE-046`.

**First side is favoured when:** Internal assets have accountable decision rights or negotiated interface obligations.

**Second side is favoured when:** Independent ecosystem participants cannot be directed by one production organisation.

**Supported hybrid:** Share specifications and bounded compatibility evidence without forcing shared implementation ownership.

**Hybrid failure:** A common syntax is treated as authority over external products or as proof of actual interoperability.

**Uncertainty/discriminator:** Community taxonomy is not evidence that one governance pattern improves outcomes.

### ESPLE-T10 — Cheap generated change versus Continuity of assurance and intent

Properties: `ESPLE-017`, `ESPLE-021`, `ESPLE-022`, `ESPLE-047`, `ESPLE-048`.

**First side is favoured when:** A bounded learned suggestion can be independently checked at acceptable cost.

**Second side is favoured when:** Validation or repeated regeneration exceeds the cost of maintaining conventional assets.

**Supported hybrid:** Learned proposal plus deterministic checks and authorised review.

**Hybrid failure:** The generator judges its own output or changes model versions without renewed validation.

**Uncertainty/discriminator:** Lifecycle superiority of regeneration remains unresolved in the inspected corpus.



## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_COMPOSED_SYSTEM

### Purpose, state and environment

The composed system organises the warranted production and evolution of a family while preserving the choice not to establish that family. Its state includes the declared scope and assumptions, intended features and constraints, shared and local assets, product configurations and baselines, production mechanisms, evidence with scope, support commitments, and economic expectations. Its environment supplies needs, observed product behaviour, supplier/interface changes and—only in a dynamic branch—operating context and events.

The nine domain models expose different views of this state. They are coupled by the 53 relations below. A relation can require information, constrain an action, supply evidence, return feedback or offer an alternative. It is not automatically a temporal step. Domain work and product derivation may proceed concurrently; a supported baseline may remain while a successor evolves; a failed product observation can interrupt a proposed shared rollout.

### Actors, communication and real effects

Product stakeholders and domain engineers supply needs, differences and counterexamples. Asset producers maintain reusable implementations and production capability. Product teams choose or adapt a product and return concrete configuration/baseline evidence. Portfolio and support decision-makers bear investment and continuation consequences. These are responsibilities, not a prescription for distinct departments. Suppliers and independently governed communities may retain authority outside the common core.

Communication has a specified consumer: a failing configuration and its provenance permit diagnosis; a product exception informs support and invalidates inappropriate inherited guarantees; a changed need can reopen scope; a failed economic assumption can reduce or end shared investment. Real actions include changing an asset, deriving a product, accepting or withholding a release, maintaining a supported baseline, migrating a configuration, retiring a variation point, and controlling a runtime transition where actually authorised and possible. An internal recommendation does none of these merely by existing.

### Coupled loops and interrupts

**The scope/economics loop** consumes commonality evidence, candidate demand and adequate alternatives. It chooses a family boundary and level of investment, then revisits them using actual product demand, cost and support evidence. Admission and retirement are different decisions because retirement must preserve or explicitly discharge existing obligations.

**The production/assurance loop** maps product choices through real assets and tools to an identified output. Encoded consistency, intended realisation and product behaviour remain separate. Analysis and tests return evidence to product acceptance and to the relevant model or asset owner. A failure can block the affected claim without requiring the entire family to stop forever.

**The evolution/support loop** evaluates shared changes against supported products, updates models and tests where needed, and decides between common repair, differentiated backport, continued baseline support or a justified exception. Recovered variability is reviewed against domain intent rather than simply promoted to authority.

**The optional runtime loop** observes a specified context, selects a permitted configuration and executes a permitted transition under real control assumptions. Feedback establishes whether the transition occurred. Without adequate observation, the command is not evidence of the postcondition. There is no universal safe fallback inferred by this report.

### The smallest coherent form

A modest family can have one group of people, a reviewed comparison of product needs, a small decision table, normal shared modules and product parameters, a versioned configuration and production instruction, checks appropriate to the accepted products, and an explicit way to return failures and reconsider shared investment. It does not need a feature DSL, a SAT solver, an automatic generator, separate teams or a supervisor merely to qualify.

Richer representations are triggered by consequential configuration complexity; generators by repeated derivation work; family analysis by supported sharing opportunities; additional provenance by attribution/support needs; dynamic control by an actual runtime requirement. A non-product-line outcome remains selectable when it is the lower-cost adequate option. This is the reconciliation that makes the system one conditional account rather than a catalogue of simultaneously mandatory methods.

### Revision and continuity

The tradition supports revising scope, models, assets and methods in response to evidence. It does not supply a self-authorising mechanism in which a changed model approves its own operational effects. An authorised revision must identify which obligations remain continuous, what evidence transfers, and what must be checked anew. This packet itself is a frozen analytical judgement, not a running adaptive controller.

### Guarded relational account

Each machine-readable relation additionally records shared and incompatible assumptions, evidence status, added cost and unresolved obligations. All 53 are labelled analytical composition of cited mechanisms, not a single published proof of the combined system.

| Relation | From → to | Type / guard | Composition mechanism | Cost / failure |
| --- | --- | --- | --- | --- |
| ESPLE-R001 | ESPLE-001 → ESPLE-002, ESPLE-036, ESPLE-037 | REQUIRES — Before committing to a shared production scope. | The scope decision consumes evidence of actual commonality and a comparison with adequate alternatives. | Scoping can delay useful local work; forecasts can still be wrong. |
| ESPLE-R002 | ESPLE-002 → ESPLE-008, ESPLE-010 | PROVIDES_EVIDENCE_FOR — Domain observations are representative enough to challenge proposed features. | Examples, expert explanations and contrary products inform semantic definitions and missing constraints, not just a feature tree. | Historical products can bias future scope. |
| ESPLE-R003 | ESPLE-036, ESPLE-038 → ESPLE-001, ESPLE-003, ESPLE-061 | FEEDBACK_TO — Observed demand, costs or support obligations change. | Reassess the family boundary, admit only justified variation and retire options whose support obligations can be discharged. | Measurement overhead and premature removal of low-frequency but important options. |
| ESPLE-R004 | ESPLE-004 → ESPLE-005, ESPLE-006 | ENABLES — Domain and product responsibilities exist, even in the same person. | Product observations reach asset decision-makers; exceptions can remain local with explicit loss of inherited guarantees. | Coordination bottlenecks or uncontrolled divergence. |
| ESPLE-R005 | ESPLE-005 → ESPLE-002, ESPLE-003, ESPLE-010, ESPLE-032 | FEEDBACK_TO — A derived product exposes an absent requirement, defect or incompatible assumption. | Route concrete product evidence back to domain knowledge and core-change decisions rather than automatically generalising the local repair. | Over-generalisation can spread product-specific assumptions. |
| ESPLE-R006 | ESPLE-007 → ESPLE-004, ESPLE-018, ESPLE-020 | ACTS_THROUGH — Select proactive, reactive, extractive or mixed adoption according to uncertainty and existing assets. | The strategy changes which assets and production capability are established first; the coupled responsibilities remain. | Over-investment, delayed capability or extraction debt. |
| ESPLE-R007 | ESPLE-009, ESPLE-011, ESPLE-012 → ESPLE-008 | REQUIRES — Formal or assisted configuration claims concern product needs. | Feature meanings and value domains make diagnostic and explanation results interpretable; richer types are introduced only when needed. | A formally precise encoding can conceal semantic disagreement. |
| ESPLE-R008 | ESPLE-009 → ESPLE-010 | CONSTRAINS — A solver reports satisfiable, dead, false-optional or void configurations. | Treat the result as a statement about encoded constraints; domain adequacy remains a separate check. | False assurance if omitted constraints are forgotten. |
| ESPLE-R009 | ESPLE-012 → ESPLE-046 | ENABLES — Models need interchange across tools. | Typed features and language levels supply representational distinctions that a transfer must preserve. | Unequal tool support can silently lose semantics. |
| ESPLE-R010 | ESPLE-013 → ESPLE-015, ESPLE-016, ESPLE-017, ESPLE-043, ESPLE-044 | CONSTRAINS — Choosing when variability is bound. | Binding time changes admissible realisation mechanisms and determines whether runtime transition obligations arise. | Late binding adds footprint and transition cost; early binding adds rebuild or redeployment cost. |
| ESPLE-R011 | ESPLE-014 → ESPLE-017, ESPLE-021, ESPLE-029, ESPLE-032 | PROVIDES_EVIDENCE_FOR — A change or result must be traced to selected features and actual assets. | Mappings connect domain choices to generator/build layers and change impact; they are maintained only at consequential boundaries. | Stale mappings can be more misleading than an explicit evidence gap. |
| ESPLE-R012 | ESPLE-015 → ESPLE-016 | ALTERNATIVE_TO — A product can be realised through annotations, components or feature modules instead of deltas. | Choose the realisation whose evolution and composition obligations are manageable; deltas support removal and modification but introduce ordering and applicability constraints. | Hybrids can multiply mappings and make interactions opaque. |
| ESPLE-R013 | ESPLE-018, ESPLE-019 → ESPLE-020 | ENABLES — Shared requirements, architecture, code, tests and documentation support intended products. | A production plan identifies how these assets are selected, adapted and combined while preserving family invariants. | A reference architecture can remain merely advisory unless derivation actually consumes it. |
| ESPLE-R014 | ESPLE-020 → ESPLE-021, ESPLE-022 | REQUIRES — A derivation result is claimed to correspond to an intended family baseline. | Identify relevant configuration, assets, tools and dependencies; define the equivalence under which a repeat derivation is judged. | Recording irrelevant environment details wastes effort; omitting relevant ones breaks attribution. |
| ESPLE-R015 | ESPLE-017, ESPLE-021, ESPLE-022 → ESPLE-028 | PROVIDES_EVIDENCE_FOR — A generated or composed product is ready for acceptance. | Realisation checks and provenance support acceptance but do not replace product-specific behavioural observations. | A reproducibly wrong product remains wrong. |
| ESPLE-R016 | ESPLE-023 → ESPLE-009, ESPLE-017, ESPLE-024, ESPLE-025, ESPLE-026, ESPLE-027, ESPLE-028, ESPLE-029 | CONSTRAINS — Any claim of validity or correctness is communicated. | Distinguish model consistency, derivation correctness, configuration coverage, input/environment coverage and product acceptance. | More explicit assurance boundaries can expose inconvenient unsupported claims. |
| ESPLE-R017 | ESPLE-024 → ESPLE-025, ESPLE-026, ESPLE-027, ESPLE-028 | ENABLES — A family assurance plan needs a choice of analysis strategy. | Interaction hypotheses and risk determine whether sampling, shared family analysis, compositional reasoning or direct product checks are adequate. | No strategy necessarily dominates across languages, defects and environments. |
| ESPLE-R018 | ESPLE-025 → ESPLE-026, ESPLE-027 | ALTERNATIVE_TO — Exhaustive or symbolic analysis is too costly or unsupported. | Choose bounded configuration sampling for an explicitly narrower claim; combine with analysis where it covers different failure classes. | Untested higher-order interactions remain possible. |
| ESPLE-R019 | ESPLE-026 → ESPLE-028 | PROVIDES_EVIDENCE_FOR — A family result applies to the product representation and underlying analysis. | Project conditional results to the derived configuration and retain language, build and analysis assumptions. | Warnings are not confirmed defects and model coverage is not total behavioural coverage. |
| ESPLE-R020 | ESPLE-027 → ESPLE-019, ESPLE-028 | CONSTRAINS — Local feature or component contracts are used to justify composition. | Check assumptions and interference at composition boundaries; product obligations may exceed local contracts. | Contract incompleteness or invalid environmental assumptions can defeat the composition argument. |
| ESPLE-R021 | ESPLE-029 → ESPLE-009, ESPLE-017, ESPLE-026 | CONSTRAINS — Variability spans build files, preprocessor rules, dependencies or non-code assets. | Reconcile configuration layers so the represented family agrees with the actually built family. | Extraction and model-maintenance costs; unresolved macro and generator behaviour. |
| ESPLE-R022 | ESPLE-028 → ESPLE-005, ESPLE-010, ESPLE-024, ESPLE-032 | FEEDBACK_TO — A product observation fails or contradicts a family assumption. | A concrete configuration/baseline failure updates domain constraints, assurance strategy or shared assets; acceptance is withheld rather than inferred from process completion. | A local failure may be misattributed to a common asset. |
| ESPLE-R023 | ESPLE-030 → ESPLE-031, ESPLE-033, ESPLE-035 | ENABLES — A feature model changes. | Classify represented configuration-set effects and identify affected products and tests before migration; behavioural compatibility needs additional evidence. | Name matching and set equivalence can hide semantic changes. |
| ESPLE-R024 | ESPLE-031 → ESPLE-008, ESPLE-021, ESPLE-028 | REQUIRES — A supported product is migrated across model or asset changes. | Preserve the product intention and identify the destination baseline, then verify the resulting product rather than merely find any satisfying assignment. | Optimisation can choose a technically valid but unacceptable replacement. |
| ESPLE-R025 | ESPLE-032 → ESPLE-006, ESPLE-033, ESPLE-034, ESPLE-035 | ACTS_THROUGH — A shared change affects supported variants. | Impact analysis may use a common repair, differentiated backports, preserved baselines or an explicit exception; tests and recovered lineage are updated accordingly. | Multiple supported baselines and exception support consume capacity. |
| ESPLE-R026 | ESPLE-033 → ESPLE-003, ESPLE-061 | CONSTRAINS — New-product simplification intersects with legacy obligations. | An option may leave the new-product scope while retained baselines continue to serve supported products; retirement requires an explicit support decision. | Legacy support can erase anticipated simplification savings. |
| ESPLE-R027 | ESPLE-034 → ESPLE-002, ESPLE-010, ESPLE-014, ESPLE-030 | PROVIDES_EVIDENCE_FOR — A family is extracted or reconciled from diverged products. | Recovered differences and dependencies become hypotheses reviewed against domain intent, rather than a claim that observed variants are the complete domain. | Incomplete artefact extraction and accidental constraints. |
| ESPLE-R028 | ESPLE-035 → ESPLE-024, ESPLE-025, ESPLE-028 | FEEDBACK_TO — Product-space changes alter existing test configurations. | Repair, retain or regenerate test selections according to preserved obligations and actual coverage; syntactic distance is only one cost proxy. | Efficient model mutation coverage may not predict behavioural defect detection. |
| ESPLE-R029 | ESPLE-037 → ESPLE-007 | ALTERNATIVE_TO — A non-product-line approach meets obligations at lower credible lifecycle cost. | Independent products, selective reuse or clone-and-own are selectable outcomes, not failures to adopt the tradition. | Local savings can hide future propagation debt. |
| ESPLE-R030 | ESPLE-039 → ESPLE-003, ESPLE-006, ESPLE-032, ESPLE-033, ESPLE-061 | CONSTRAINS — A decision changes the shared family or product obligations. | An authorised party with affected product participation decides admission, exceptions, repair, support or retirement; analysis alone is not authority. | Central bottlenecks, veto deadlocks or unrepresented stakeholders. |
| ESPLE-R031 | ESPLE-040 → ESPLE-004, ESPLE-005, ESPLE-039 | ENABLES — People must maintain and contribute to shared assets. | Capability, incentives and accessible decision paths make the feedback and change responsibilities operational. | Training and shared-team overhead can exceed avoided duplication. |
| ESPLE-R032 | ESPLE-041 → ESPLE-019, ESPLE-039, ESPLE-046 | CONSTRAINS — Family assets cross independent organisations or communities. | Separate common-core ownership from interoperable independent implementations, supplier interfaces and negotiated compatibility. | Distributed authority can produce protocol drift without a central repair power. |
| ESPLE-R033 | ESPLE-042 → ESPLE-003, ESPLE-020, ESPLE-028, ESPLE-032 | CONSTRAINS — External licence, security, contractual or mission obligations are actually specified. | Treat the obligations as inputs to scope, derivation, acceptance and impact decisions; do not manufacture their legal content from product-line models. | A common asset can amplify exposure; an organisational model does not confer external permission. |
| ESPLE-R034 | ESPLE-043 → ESPLE-044 | REQUIRES — Permitted configurations can change during operation. | Context-to-feature mapping must be accompanied by a safe transition relation and actual observation/control assumptions. | Sensor errors, unmodelled actions or unobservable states can defeat the guarantee. |
| ESPLE-R035 | ESPLE-044 → ESPLE-009 | REFINES — Both endpoint configurations satisfy static constraints. | Require a permitted path through intermediate states or a genuinely atomic transition; endpoint validity alone is insufficient. | Extra transition states or quiescence can interrupt service. |
| ESPLE-R036 | ESPLE-045 → ESPLE-044 | PROVIDES_EVIDENCE_FOR — A supervisory-control model satisfies its assumptions. | Synthesis restricts controllable actions to meet modelled safety and nonblocking requirements; deployment still needs model/plant correspondence. | State-space explosion, uncontrollable unsafe actions and abstraction error. |
| ESPLE-R037 | ESPLE-047 → ESPLE-017, ESPLE-028, ESPLE-030, ESPLE-031, ESPLE-035 | ACTS_THROUGH — Learned assistance proposes a configuration, model edit, migration or test repair. | Treat generated outputs as candidate changes and validate them with the same semantic, realisation and acceptance boundaries. | Plausible but unsupported proposals and unstable model behaviour. |
| ESPLE-R038 | ESPLE-017, ESPLE-021, ESPLE-022, ESPLE-028, ESPLE-036 → ESPLE-048 | CONSTRAINS — Regeneration is proposed as a replacement for maintained family assets. | A regeneration replacement must preserve relevant realisation, identity, repeatable obligations, acceptance and lifecycle adequacy; current examples leave that stronger claim unresolved. These boundaries do not reject regeneration by definition. | Loss of accumulated assurance and repeated revalidation cost. |
| ESPLE-R039 | ESPLE-049 → ESPLE-036 | CONFLICTS_WITH — A fixed product count is asserted as a universal investment threshold. | Reject the general threshold because startup, per-product cost, uncertainty and horizon vary. | A convenient benchmark can hide an uneconomic programme. |
| ESPLE-R040 | ESPLE-050 → ESPLE-007, ESPLE-037 | CONFLICTS_WITH — Complete upfront modelling is asserted as mandatory. | Reactive, extractive and non-product-line branches provide documented alternatives. | Over-investment and delayed learning. |
| ESPLE-R041 | ESPLE-051 → ESPLE-008, ESPLE-010, ESPLE-014 | CONFLICTS_WITH — The presence of a feature diagram is offered as evidence of control. | Require a maintained semantic consumer and a realised connection to product decisions; a diagram alone is ceremony. | False assurance and maintenance overhead. |
| ESPLE-R042 | ESPLE-052 → ESPLE-009, ESPLE-017, ESPLE-023, ESPLE-028 | CONFLICTS_WITH — Satisfiability is equated with product correctness. | Reject the inference across representation and behaviour boundaries. | Invalid products pass a misplaced gate. |
| ESPLE-R043 | ESPLE-053 → ESPLE-024, ESPLE-025 | CONFLICTS_WITH — Pairwise coverage is equated with absence of all interaction faults. | Retain pairwise sampling as bounded evidence and reject the general completeness claim. | Higher-order defects remain unseen. |
| ESPLE-R044 | ESPLE-054 → ESPLE-013, ESPLE-044 | CONFLICTS_WITH — Later binding is assumed to improve every family. | Account for transition, footprint and operational costs alongside flexibility. | Unnecessary runtime state space. |
| ESPLE-R045 | ESPLE-055 → ESPLE-008, ESPLE-014, ESPLE-015 | CONFLICTS_WITH — A universal one-feature/one-module mapping is demanded. | Allow many-to-many realisation with checked interactions; modularity is a technique, not feature identity. | Artificial splitting or obscured cross-cutting behaviour. |
| ESPLE-R046 | ESPLE-056 → ESPLE-020, ESPLE-022 | CONFLICTS_WITH — Full automation is treated as the definition of a product line. | A controlled manual production process can be adequate; a feature-based automation standard has a narrower scope. | Automation investment without sufficient reuse. |
| ESPLE-R047 | ESPLE-057 → ESPLE-037 | CONFLICTS_WITH — Cloning is ruled out regardless of circumstances. | Keep a lifecycle comparison and observed support burden rather than a moral ranking of reuse methods. | Ignoring either near-term autonomy or later propagation debt. |
| ESPLE-R048 | ESPLE-058 → ESPLE-030, ESPLE-031, ESPLE-035 | CONFLICTS_WITH — Unchanged names or equal configuration sets are taken as behavioural compatibility. | Add semantics and product-obligation checks; set-level equivalence remains useful at its own level. | Silent behavioural change despite a stable model. |
| ESPLE-R049 | ESPLE-059 → ESPLE-003, ESPLE-036, ESPLE-061 | CONSTRAINS — Possible configuration count is used as a progress metric. | Use count to describe a represented space, not realised utility; include demand, support and assurance burden. | Combinatorial growth can reward useless options. |
| ESPLE-R050 | ESPLE-060 → ESPLE-039, ESPLE-042, ESPLE-047 | CONFLICTS_WITH — A formal or learned recommendation is treated as permission to act. | Separate evidence about an option from legitimate authority, capability and observed consequence. | Unauthorised or ineffective changes. |
| ESPLE-R051 | ESPLE-061 → ESPLE-003 | FEEDBACK_TO — An existing variation point has lost its consumer or imposes unjustified burden. | Retirement revises admission assumptions after checking support and migration, rather than continuously expanding the family. | Premature retirement and lost legacy knowledge. |
| ESPLE-R052 | ESPLE-062 → ESPLE-013, ESPLE-023, ESPLE-061 | CONFLICTS_WITH — Fixed feature selection is used to infer context-independent behaviour. | Restrict null configurability to the binding distinction and continue ordinary input, state and environmental analysis. | False assurance from conflating configuration and execution. |
| ESPLE-R053 | ESPLE-021, ESPLE-028 → ESPLE-005, ESPLE-032 | COMMUNICATES_TO — A product observation is returned to those responsible for shared assets or a proposed shared change. | Transmit the concrete result, expected obligation and baseline/configuration identity so the recipient can distinguish domain error, realisation error, local exception and shared defect. | Missing provenance or an unresponsive recipient makes feedback inert; collecting irrelevant details can waste effort. |

### Alternative configurations

**ESPLE-ALT-01 — Small stable family with mostly manual derivation.** Selection: Repeated related products, modest variation, stable obligations and a credible cost case. Operation: Reviewed commonality and decision table; ordinary shared modules; versioned product configuration; repeatable production instruction; product acceptance and feedback. Omission: Do not require a dedicated platform team, SAT solver, feature language, automatic generator or runtime supervisor. Retirement: Return to selective reuse or independent products if support and coordination cease to earn their cost. Properties: `ESPLE-001`, `ESPLE-002`, `ESPLE-004`, `ESPLE-008`, `ESPLE-013`, `ESPLE-018`, `ESPLE-020`, `ESPLE-021`, `ESPLE-023`, `ESPLE-028`, `ESPLE-036`, `ESPLE-039`.

**ESPLE-ALT-02 — Large static or generated family.** Selection: Configuration complexity or repeated production makes formal diagnostics, generation or shared analysis worthwhile. Operation: Choose complementary diagnostics, analysis and sampling under a common model/realisation/acceptance boundary. Omission: No obligation to use all three analysis strategies; unsupported or low-value techniques are excluded. Retirement: Remove a specialised tool when supported products and analysis needs no longer justify it. Properties: `ESPLE-009`, `ESPLE-010`, `ESPLE-012`, `ESPLE-014`, `ESPLE-017`, `ESPLE-020`, `ESPLE-021`, `ESPLE-024`, `ESPLE-025`, `ESPLE-026`, `ESPLE-027`, `ESPLE-029`, `ESPLE-030`, `ESPLE-031`, `ESPLE-035`, `ESPLE-046`.

**ESPLE-ALT-03 — Extractive or incrementally consolidated portfolio.** Selection: Existing variants have useful commonality but cannot immediately move to one maintained core. Operation: Recover differences and provenance; review with domain experts; consolidate selectively while keeping justified exceptions and supported baselines. Omission: Do not require immediate eradication of every clone or a complete future feature model. Retirement: Stop consolidation where expected savings do not exceed semantic recovery and migration burden. Properties: `ESPLE-002`, `ESPLE-005`, `ESPLE-006`, `ESPLE-007`, `ESPLE-014`, `ESPLE-032`, `ESPLE-033`, `ESPLE-034`, `ESPLE-037`, `ESPLE-039`.

**ESPLE-ALT-04 — Dynamic product line.** Selection: Runtime variation responds to a specified operational need rather than generic flexibility. Operation: Permitted states plus context observations and a transition protocol; supervisory synthesis only when its model and control assumptions fit. Omission: Do not infer safe transitions from valid endpoints, and do not require dynamic machinery for static families. Retirement: Prefer earlier binding when runtime benefit disappears or operational assurance cannot be justified. Properties: `ESPLE-008`, `ESPLE-009`, `ESPLE-013`, `ESPLE-021`, `ESPLE-023`, `ESPLE-028`, `ESPLE-043`, `ESPLE-044`, `ESPLE-045`.

**ESPLE-ALT-05 — Inter-organisational or community arrangement.** Selection: Independent owners share compatibility or platform interests but lack a single common-core authority. Operation: Explicit interfaces, contribution/compatibility expectations and independently accountable product acceptance. Omission: Do not assume this is identical to one organisation deriving all products from one core. Retirement: Reduce shared coordination where no interoperability or shared-asset obligation remains. Properties: `ESPLE-001`, `ESPLE-019`, `ESPLE-021`, `ESPLE-028`, `ESPLE-039`, `ESPLE-041`, `ESPLE-042`, `ESPLE-046`.

**ESPLE-ALT-06 — Adequate non-product-line alternative.** Selection: Incidental similarity, weak demand, incompatible assumptions or a lower-cost adequate cloning/selective-reuse route. Operation: Maintain independent products or a small shared utility; retain enough change and support knowledge for actual obligations. Omission: The family programme itself may be omitted without a presumed engineering deficiency. Retirement: Reconsider if observed propagation cost or recurrent demand changes the comparison. Properties: `ESPLE-001`, `ESPLE-007`, `ESPLE-036`, `ESPLE-037`, `ESPLE-038`.

### Discriminating cases

The nine constructed cases are analytical tests, three of which include executed Boolean/graph/arithmetic checks. They are not empirical validation. The two published cases are kept separate and retain their actual setting limits.

#### ESPLE-CASE-01 — Three similar products with incompatible assumptions

**Evidence status:** ANALYTICAL_TEST_NOT_EMPIRICAL_VALIDATION.

**Given:** A batch collector tolerates reordering, a controller requires bounded response, and an offline recorder must survive disconnection. All share a serialisation library.

**Response:** Do not infer one production family or one scheduler from the library. Test whether a narrow common layer plus explicit variations can meet all assumptions at acceptable cost; split scope if not.

**Discriminating observation:** A proposed invariant that requires permanent connectivity is contradicted by the recorder. Sharing serialisation remains possible.

**Limit:** This does not prove that the three products can never form a family under a different architecture. Properties: `ESPLE-001`, `ESPLE-002`, `ESPLE-003`, `ESPLE-019`, `ESPLE-037`. No empirical source is claimed for this constructed case.

#### ESPLE-CASE-02 — Valid feature model, defective generator

**Evidence status:** ANALYTICAL_TEST_NOT_EMPIRICAL_VALIDATION.

**Given:** The model requires exactly one of A or B; configuration A=true,B=false is valid, but the generator emits B.

**Response:** Pass encoded consistency, fail the intended realisation relation and withhold product acceptance. Retain configuration and generator identity for diagnosis.

**Discriminating observation:** The emitted capability disagrees with the selected feature despite successful compilation.

**Limit:** The toy oracle checks a simple mapping, not arbitrary product behaviour. Properties: `ESPLE-009`, `ESPLE-017`, `ESPLE-021`, `ESPLE-023`, `ESPLE-028`, `ESPLE-052`. No empirical source is claimed for this constructed case.

#### ESPLE-CASE-03 — Shared security repair breaks a supported variant

**Evidence status:** ANALYTICAL_TEST_NOT_EMPIRICAL_VALIDATION.

**Given:** A common security repair exceeds the memory budget of one still-supported product.

**Response:** Do not claim family-wide completion. Assess differentiated backport, a supportable baseline or an explicit product exception with the relevant decision authority.

**Discriminating observation:** The repaired high-resource products pass, but the low-resource product fails its acceptance obligation; this result interrupts blanket propagation.

**Limit:** No specific vulnerability, legal requirement or acceptable security exception is invented. Properties: `ESPLE-006`, `ESPLE-021`, `ESPLE-028`, `ESPLE-032`, `ESPLE-033`, `ESPLE-039`, `ESPLE-042`. No empirical source is claimed for this constructed case.

#### ESPLE-CASE-04 — Pairwise coverage misses a three-way fault

**Evidence status:** EXECUTED_LOGICAL_CHECK_NOT_EMPIRICAL_VALIDATION.

**Given:** For three unconstrained Boolean features, sample 000,011,101,110. A fault activates only at 111.

**Response:** Recognise complete pairwise assignment coverage but no general interaction-correctness guarantee. Add a higher-order test when the risk or interaction hypothesis warrants it.

**Discriminating observation:** The executable check confirms all 2-variable assignments occur and 111 is absent.

**Limit:** This counterexample disproves the universal completeness inference; it does not show pairwise testing is useless. Properties: `ESPLE-024`, `ESPLE-025`, `ESPLE-053`. No empirical source is claimed for this constructed case.

#### ESPLE-CASE-05 — Safe endpoints, unsafe transition

**Evidence status:** EXECUTED_LOGICAL_CHECK_NOT_EMPIRICAL_VALIDATION.

**Given:** Exactly one provider must be active. Endpoints (1,0) and (0,1) are safe; the platform only changes one Boolean variable at a time.

**Response:** No safe path exists under those actions. Require a genuinely atomic transfer, a separately specified safe quiescent protocol, or reject the transition.

**Discriminating observation:** Enumerating the one-bit graph shows both intermediate states (0,0) and (1,1) violate the invariant.

**Limit:** An atomic or quiescent mechanism cannot be assumed merely to make the model work. Properties: `ESPLE-043`, `ESPLE-044`, `ESPLE-045`, `ESPLE-054`. No empirical source is claimed for this constructed case.

#### ESPLE-CASE-06 — Small portfolio where cloning is adequate

**Evidence status:** EXECUTED_ARITHMETIC_SCENARIO_NOT_EMPIRICAL_VALIDATION.

**Given:** Hypothetical equivalent obligations: a two-product clone-and-own route costs 60 effort units over the decision horizon; establishing and operating the family costs 120. Estimates already include the stated support work.

**Response:** Select the lower-cost adequate alternative and revisit the decision if demand, propagation or support assumptions change.

**Discriminating observation:** 60 < 120 under the declared scenario; no product-count threshold is inferred.

**Limit:** The values are invented to test the decision rule, not estimates from an industrial study. Properties: `ESPLE-007`, `ESPLE-036`, `ESPLE-037`, `ESPLE-049`, `ESPLE-057`. No empirical source is claimed for this constructed case.

#### ESPLE-CASE-07 — A favourable modest static family

**Evidence status:** ANALYTICAL_TEST_NOT_EMPIRICAL_VALIDATION.

**Given:** Several metering products share stable measurement semantics and differ in a declared display and communication option. A maintained library and deployment-time parameter file realise those differences.

**Response:** Use a small decision table, versioned assets/configuration, a repeatable derivation instruction and appropriate product checks. No runtime supervisor or feature DSL is required.

**Discriminating observation:** Derived products satisfy their declared measurement and interface obligations; actual saved work can be compared with maintained alternatives.

**Limit:** Technical coherence in this invented example is not empirical proof of return on investment. Properties: `ESPLE-001`, `ESPLE-004`, `ESPLE-008`, `ESPLE-013`, `ESPLE-018`, `ESPLE-020`, `ESPLE-021`, `ESPLE-028`, `ESPLE-036`. No empirical source is claimed for this constructed case.

#### ESPLE-CASE-08 — The actuator command is not the observed transition

**Evidence status:** ANALYTICAL_TEST_NOT_EMPIRICAL_VALIDATION.

**Given:** A controller issues a reconfiguration command, but the state observer is stale and the physical action may have failed.

**Response:** Do not equate a decision, permission or issued command with achieved state. Use warranted feedback or enter the explicitly designed failure response.

**Discriminating observation:** Independent current state evidence is missing, so the transition postcondition is not established.

**Limit:** The study does not prescribe a universal safe fallback for every plant. Properties: `ESPLE-023`, `ESPLE-028`, `ESPLE-043`, `ESPLE-044`, `ESPLE-045`, `ESPLE-060`. No empirical source is claimed for this constructed case.

#### ESPLE-CASE-09 — A changed assurance assumption

**Evidence status:** ANALYTICAL_TEST_NOT_EMPIRICAL_VALIDATION.

**Given:** A family-analysis result assumed a particular build constraint, but a generator upgrade changes which module is included.

**Response:** Invalidate or narrow the inherited result until model/implementation correspondence is re-established; do not carry the old guarantee solely because feature names match.

**Discriminating observation:** The represented configuration no longer matches the built product.

**Limit:** This is an analytical obligation derived from assurance boundaries, not a reported incident. Properties: `ESPLE-021`, `ESPLE-023`, `ESPLE-026`, `ESPLE-029`, `ESPLE-032`. No empirical source is claimed for this constructed case.

#### ESPLE-CASE-10 — Industrial global model becomes stale

**Evidence status:** PUBLISHED_FIELD_OBSERVATION.

**Given:** The Bosch PS-EC report describes formerly used high-level feature models becoming outdated and falling out of use, and studies dependencies across seven selected projects.

**Response:** Retain maintainable, subsystem-aligned models with domain review and cross-boundary consistency, rather than demand one comprehensive central model.

**Discriminating observation:** The report documents maintenance and extraction limits; it does not establish a controlled ROI comparison for the proposed model organisation.

**Limit:** One family and purposive project selection; not a universal failure rate. Properties: `ESPLE-002`, `ESPLE-010`, `ESPLE-014`, `ESPLE-034`, `ESPLE-039`. Sources: [ESPLE-S041].

#### ESPLE-CASE-11 — Configuration-dependent generator failures

**Evidence status:** PUBLISHED_CONFIGURABLE_SYSTEM_STUDY.

**Given:** The historical JHipster study reports 9,376 failed configurations out of 26,256 in Results §6.1, with a minor denominator discrepancy elsewhere.

**Response:** Treat feature/configuration validity and generated-product outcomes separately; use the reported fault interactions to judge sampling limits in that version.

**Discriminating observation:** The study reports six faults including a higher-order interaction, not a general defect rate for all configurable generators.

**Limit:** One historical version; infrastructure/configuration conditions and the paper denominator discrepancy are retained. Properties: `ESPLE-017`, `ESPLE-024`, `ESPLE-025`, `ESPLE-028`. Sources: [ESPLE-S021].

The executed pairwise check covers each assignment of each pair in {000,011,101,110}, while 111 is absent. The transition check finds no edge between the two safe states under single-bit actions. The economic example merely verifies the comparison under its invented costs. These checks refute particular overclaims and exercise the decision rules; they do not establish the general effectiveness of the composed system.

## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_HYBRIDISATION_AND_EXTERNAL_RELATIONS

Native family scope, commonality, variation and production are not erased by legitimate imports. The following relationships preserve the difference between a borrowed mechanism and a similarly named idea.

| Neighbour / branch | Relationship | What is imported or shared | Limit / reconciliation question |
| --- | --- | --- | --- |
| Software architecture | Documented intersection and shared design concerns | Family invariants, architectural variation and permitted product structures. | Does a reference architecture guide or actually constrain derivation? The unread architecture lane must answer for its own evidence. |
| Software maintenance and evolution | Documented intersection | Change impact, configuration migration, support and test co-evolution. | What continuity is required at configuration, asset and behaviour levels? No sibling judgement is assumed. |
| Generative programming and model-driven engineering | Documented implementation branch / hybridisation | Models, transformations and generators participate in product derivation. | Model validity does not establish transformation or product correctness. |
| Formal methods | Documented import and shared techniques | Logic for configuration, analysis and modelled transition guarantees. | A proof’s model and environment assumptions must remain visible. |
| Control theory | Documented import in dynamic configuration | Discrete-event supervisory synthesis. | A suitable control model is required; nonblocking is not universal real-world progress. |
| Ecosystems and communities | Documented extension / translation | Independent ownership, interfaces and compatibility coordination. | Not every arrangement has a shared core or central derivation authority. |
| Learned assistance | Current hybridisation and adjacent-domain transfer | Candidate configuration, migration or derivation proposals. | Independent validation and lifecycle evidence remain required; replacement superiority unresolved. |
| Biological ecosystems | Analogy only unless a mechanism is separately documented | A vocabulary for interdependent participants. | No biological ancestry, optimisation law or engineering guarantee is inferred. |

The provisional SSS label is an organisational aid for future research. It does not establish that the three subjects already form one recognised school. Native concepts and source IDs are exported without consulting sibling findings, and later semantic equivalence must be tested rather than presumed.

## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_STRONGEST_SURVIVING_PROPERTIES

These nine candidates have the strongest retained bounded role. “Strongly retained” describes the present analytic disposition, not an overall empirical confidence score or universal mandate for machinery.

**ESPLE-001 — Warranted family boundary.** State which products and foreseeable needs belong together; test shared domain assumptions against counterexamples before committing to shared production. Boundary: For incidental shared utilities, use ordinary component reuse or independent products without introducing a family programme. [ESPLE-S002; ESPLE-S003; ESPLE-S007; ESPLE-S009; ESPLE-S013; ESPLE-S026; ESPLE-S041]

**ESPLE-004 — Coupled domain and application responsibilities.** Maintain a functional distinction between creating family capabilities and instantiating products, with explicit exchange of requirements, constraints and feasibility evidence. Boundary: The same people may perform both activities; a small family needs no separate departments or serial phases. [ESPLE-S006; ESPLE-S008; ESPLE-S009; ESPLE-S013; ESPLE-S041]

**ESPLE-008 — Explicit feature semantics.** Define what each feature denotes, who interprets it and how selections relate to requirements, implementation and runtime capability. Boundary: A compact glossary plus explicit configuration rules can be sufficient; a tree is optional. [ESPLE-S005; ESPLE-S009; ESPLE-S014; ESPLE-S015; ESPLE-S041]

**ESPLE-009 — Constraint-consistency diagnostics.** Check the model's declared semantics for consistency and investigate diagnoses relative to intended configurations; report the exact model and solver interpretation. Boundary: Exhaustive enumeration or a manually checked decision table may suffice for a tiny model. [ESPLE-S014; ESPLE-S015; ESPLE-S041]

**ESPLE-023 — Layer-specific assurance claims.** State each assurance claim's object, quantified configurations, inputs, environment and baseline; identify the realisation obligations needed to carry it to a product. Boundary: A concise claim-and-boundary statement attached to the result can be sufficient. [ESPLE-S014; ESPLE-S019; ESPLE-S021; ESPLE-S031; ESPLE-S040; ESPLE-S041]

**ESPLE-028 — Acceptance of the actual derived product.** Check the actual derived artefacts against the selected product obligations and operating context, reusing family evidence only where its premises apply. Boundary: Reuse valid existing evidence and perform only the additional product checks needed for unestablished obligations; repeated full testing is not automatically required. [ESPLE-S006; ESPLE-S009; ESPLE-S021; ESPLE-S019]

**ESPLE-032 — Impact and regression analysis of shared changes.** Identify affected products and assumptions, select appropriate regression evidence and coordinate propagation, exceptions or supported parallel versions. Boundary: Use local regression when the changed asset is demonstrably product-local; reuse established evidence for unaffected products. [ESPLE-S009; ESPLE-S011; ESPLE-S021; ESPLE-S041; ESPLE-S028]

**ESPLE-037 — An explicit adequate non-product-line alternative.** Compare SPLE with clone-and-own, selective component reuse, a modular single product or independent development under the same quality and support obligations. Boundary: Keep the adequate non-product-line method when its total burden is lower or the product-line benefit is not established. [ESPLE-S010; ESPLE-S012; ESPLE-S026; ESPLE-S013; ESPLE-S027; ESPLE-S028]

**ESPLE-044 — Transition safety and state continuity.** Check the transition path, quiescence or state transfer and actual controllability; preserve safety requirements throughout the operating phase or enter a separately justified safe reconfiguration phase. Boundary: Stop and restart in a known safe condition, or prohibit runtime switching, when live transition assurance is disproportionate. [ESPLE-S030; ESPLE-S031]

Together they protect warranted scope, the domain/product relationship, semantic and consistency distinctions, evidence boundaries, product acceptance, shared-change impact, legitimate alternatives and runtime transition safety when runtime variation actually exists.

## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_CONTEXT_SPECIFIC_PROPERTIES

Selection conditions matter as much as the techniques. Context dependence is not an instruction to “balance” without a discriminator; the table states the actual trigger and adequate alternative for every such candidate.

| ID / disposition | Trigger | Cheaper path or non-trigger | Critical limit |
| --- | --- | --- | --- |
| ESPLE-007 / CONTEXT_DEPENDENT | Starting a product line or changing how an existing portfolio is produced. | Reuse a few stable assets or retain clone-and-own while collecting evidence; no immediate platform conversion is required. | Reactive growth can accumulate hidden debt, extraction can preserve accidental variation, and proactive design can overfit forecasts. |
| ESPLE-011 / CONTEXT_DEPENDENT | Configuration choices are numerous, cross-constrained or made by users without implementation expertise. | A domain expert can explain a small stable set of rules directly; automated minimal explanations are not always needed. | Logical minimality need not yield human usefulness. Simplified formulas may obscure their relation to implementation evidence. |
| ESPLE-012 / CONTEXT_DEPENDENT | The domain requires multiplicity, arithmetic, typed values or constraints not expressible adequately by simple selection. | Keep a Boolean model or a small typed table when that already captures consequential decisions. | Richer languages can damage understandability and solver scalability. Approximate Booleanisation may lose numeric distinctions. |
| ESPLE-014 / USEFUL_BUT_EASILY_BUREAUCRATISED | Consequential changes or product construction depend on understanding how a feature is realised. | Local naming, module structure and a small checked mapping can replace a comprehensive trace database. | Trace completeness metrics are easy to satisfy with stale or meaningless links. Perfect one-to-one mapping is often impossible. |
| ESPLE-015 / CONTEXT_DEPENDENT | Designing or restructuring the realisation of family variation. | Retain an ordinary parameter or small conditional when it is understandable and adequately checked. | Annotations can scatter concerns; modules can require complex interaction glue; combining mechanisms can hide configuration layers. |
| ESPLE-016 / DOMAIN_SPECIFIC | Product differences naturally require structured additions, removals or changes over a shared base. | Use direct modules or parameters where no meaningful transformation sequence is needed. | Order conflicts and base assumptions can be subtle; mechanism-level examples do not establish lower industrial lifecycle cost. |
| ESPLE-022 / CONTEXT_DEPENDENT | Support, certification, comparison or distribution requires reliable reconstruction of a product. | Behavioural or structural equivalence may be adequate; do not impose bit-for-bit output where timestamps or tool differences are immaterial. | Byte identity can coexist with the same defect; behavioural equivalence can be difficult to establish; environment capture can be expensive. |
| ESPLE-025 / ASSUMPTION_SENSITIVE | Full enumeration is infeasible and a bounded sample can provide useful assurance. | Test every supported configuration when the family is small, or analyse a relevant shared property once when a sound family analysis is cheaper. | Algorithm rankings change with constraints, headers, build systems and budgets; pairwise coverage cannot generally detect higher-order faults. |
| ESPLE-026 / DOMAIN_SPECIFIC | Many products share analyzable structure and the analysis implementation supports their variability semantics. | Ordinary product analysis is preferable for a few configurations or unsupported languages and artefacts. | State explosion can remain; preprocessor/build omissions undermine coverage; reported warnings may be false positives rather than confirmed defects. |
| ESPLE-027 / ASSUMPTION_SENSITIVE | Stable interfaces and separable properties make local reasoning reusable across products. | Check the whole derived product when contracts would be harder to specify or maintain than the verification itself. | Emergent behaviour, shared resources and nonlocal properties can defeat separability. Contracts can become circular or omit the decisive assumption. |
| ESPLE-029 / CONTEXT_DEPENDENT | Build, dependency or generator configuration affects product realisation or static-analysis reach. | A single checked configuration layer is enough when the derivation genuinely has no hidden variation elsewhere. | Full extraction can be expensive and tool-specific; approximate parsing may trade speed for missed constraints or warnings. |
| ESPLE-030 / CONTEXT_DEPENDENT | A feature model, cross-tree constraint or feature vocabulary changes. | Enumerate and compare all configurations for a small family rather than introduce a specialised solver. | Equal feature names can conceal changed meaning; different feature universes require careful projection; formal comparison cannot recover omitted domain intent. |
| ESPLE-034 / CONTEXT_DEPENDENT | Consolidating variants, repairing stale models or reducing dependence on tacit configuration knowledge. | Compare a few existing products manually; do not introduce a general extraction framework for a tiny stable portfolio. | Observed products under-sample the possible family; mixed versions can yield contradictory relations; approximate extraction may omit macros or generators. |
| ESPLE-035 / CONTEXT_DEPENDENT | A feature-model change alters permitted products or test-selection assumptions. | Retain still-valid tests and manually add a few relevant configurations when changes are small. | Mutation-score and configuration-distance results are proxies, not deployed fault coverage or measured human repair labour. Higher-order mutations and richer models can change the ranking. |
| ESPLE-036 / ASSUMPTION_SENSITIVE | An investment or continuation decision depends on product-line benefits. | Use a coarse scenario comparison when precise estimates are not credible; keep assumptions visible rather than manufacture precision. | Forecasts may be wrong; reported case benefits are selected and confounded; small task experiments omit transition investment. |
| ESPLE-040 / CONTEXT_DEPENDENT | A product-line plan requires work or coordination beyond the existing organisation's supported practice. | Start with a limited shared capability and existing staff rather than create a full platform organisation before demand is known. | Reorganisation can cost more than reuse saves; no universal team structure follows from the tradition. |
| ESPLE-041 / CONTEXT_DEPENDENT | Suppliers, open-source participants or independent platform users determine material variation. | Manage a bounded component dependency when no broader ecosystem coordination is required. | Ecosystem taxonomy does not prove effective governance or economic superiority. Central product-line controls can be both infeasible and inappropriate in autonomous communities. |
| ESPLE-043 / DOMAIN_SPECIFIC | A product must change its selected capabilities during execution as conditions change. | Select a static or deployment-time variant when runtime rebinding is not required. | Sensors can be stale, context models incomplete and adaptation goals conflicting. Arbitrary adaptation does not become a DSPL merely by being dynamic. |
| ESPLE-045 / DOMAIN_SPECIFIC | A finite-state or otherwise supported discrete-event model adequately captures a consequential dynamic product-line problem. | A reviewed transition table or offline configuration can suffice where synthesis adds no justified assurance. | Nonblocking permits reachability of a marked state, not inevitable progress on every run. Industrial-origin benchmark success does not certify a deployed physical system. |
| ESPLE-046 / CONTEXT_DEPENDENT | Variability models move across tools, organisations or analysis backends. | Keep one stable representation and tool when interchange has no real consumer. | A common syntax is not universal semantic compatibility, and community adoption does not establish economic benefit. |
| ESPLE-047 / ASSUMPTION_SENSITIVE | Learned tools assist feature modelling, configuration advice, migration or variant generation. | Use deterministic constraint solving, a conventional transformation or manual review when these are cheaper and adequate. | Benchmarks are limited and version-specific; adjacent textual DSL results do not establish complete SPLE migration effectiveness. A relevant SPLC 2025 full text was inaccessible. |
| ESPLE-059 / USEFUL_BUT_EASILY_GAMED | Configuration-space size is used in an investment or maturity claim. | Count supported or demanded products and their costs when theoretical possibilities do not affect the decision. | Counts can be inflated by irrelevant options or inconsistent feature granularity; large spaces may nonetheless matter for assurance planning. |



## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_REJECTED_OR_SUPERSEDED_PRACTICES

The following twelve candidates are not unconditional obligations. They are retained in the denominator so later consumers can see what was rejected rather than importing it from a slogan. No candidate is labelled historically superseded without evidence of an actual replacement relation.

| ID | Primary disposition | Rejected generalisation / reason | Narrower response |
| --- | --- | --- | --- |
| ESPLE-049 | REJECTED_OR_DISFAVOURED | A universal break-even product count — Different asset investments and reuse frequencies yield different break-even points; some portfolios never recover the investment. | No general mechanism supports the universal threshold. Replace the claim with a horizon-specific comparison of investment, derivation, coordination and support costs. |
| ESPLE-050 | REJECTED_OR_DISFAVOURED | A complete upfront platform as a prerequisite — Some safety-critical or stable high-volume domains need substantial anticipatory investment; rejecting universality does not forbid that branch. | Reject the universal prerequisite; use the proactive, reactive, extractive or hybrid route justified by the actual starting conditions. |
| ESPLE-051 | CEREMONY_NOT_GENERAL_PROPERTY | A feature-tree artefact as sufficient variability management — Removing all models would also destroy useful communication or automation; the objection is to empty observance, not representation. | Reject artefact sufficiency; require meaningful features, usable constraints, a relation to realisation and an actual configuration or change consumer. |
| ESPLE-052 | REJECTED_OR_DISFAVOURED | Feature-model satisfiability as delivered-product correctness — This does not refute the solver theorem: implementation failure or omitted assumptions lie outside its guarantee. | Reject the implication. Keep model consistency, realisation correctness and product behaviour as separate claims with explicit connecting premises. |
| ESPLE-053 | REJECTED_OR_DISFAVOURED | Pairwise coverage as family correctness — Pairwise testing remains useful and may be adequate for some budgets; rejecting the guarantee is not evidence that pairwise is useless. | Reject the guarantee; use pairwise testing only as a bounded selection strategy within an explicit assurance argument. |
| ESPLE-054 | REJECTED_OR_DISFAVOURED | Later binding as universally better — Earlier binding can be unacceptable when context changes faster than redeployment; the ranking fails in both directions. | Reject a universal ranking and select binding time by the timing of needed knowledge and the costs of retained flexibility. |
| ESPLE-055 | NO_GENERAL_PROPERTY | A universal one-feature/one-module correspondence — Feature modularity can improve separation and reasoning in appropriate languages; the rejected part is universality, not modularity. | Reject the universal correspondence; model the relations needed for derivation and impact, allowing many-to-many mappings and interaction artefacts. |
| ESPLE-056 | NO_GENERAL_PROPERTY | Total automation as the definition of SPLE — Manual derivation can become error-prone or too slow at scale; some specialised approaches do require stronger automation within their stated scope. | Reject total automation as a universal definition; require a defined, adequate derivation method and evidence for the resulting products. |
| ESPLE-057 | REJECTED_OR_DISFAVOURED | Clone-and-own as universally inadmissible — Uncontrolled divergence can make fixes costly and inconsistent; industrial motives for cloning are not proof of long-term superiority. | Reject universal inadmissibility; compare cloning's immediate adequacy and future synchronisation costs with the actual product-line alternative. |
| ESPLE-058 | REJECTED_OR_DISFAVOURED | Stable names or configuration sets as behavioural compatibility — Model-set equivalence remains valuable for its own purpose; it is not disproved by an implementation change outside the model. | Reject the equivalence; preserve or explicitly change feature intent and verify the actual migrated product's obligations. |
| ESPLE-060 | REJECTED_OR_DISFAVOURED | Formal modelling as operational authority — This is an analytical authority boundary, not a claim that supervisory-control theory itself confuses permission and controllability. | Reject self-authorising control; separately establish observation, actual actuation capability, external permission and the expected consequence. |
| ESPLE-062 | REJECTED_OR_DISFAVOURED | Null configurability as context-independent behaviour — The source's qualification about non-identical outputs must be preserved; this criticism targets the broad inference, not every formulation or the value of fixed-function software. | Reject that stronger implication. Retain the narrower distinction that selected features are fixed after a declared binding time; analyse inputs, state, timing and environment separately. |

ESPLE-048 is separately **UNRESOLVED**, not rejected by default: the stronger regeneration replacement claim requires longitudinal continuity and whole-lifecycle evidence. ESPLE-059 retains only a descriptive configuration-count use and must not be converted into a value metric.

## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_CURRENT_STATE_AND_RESEARCH_FRONTIER

Current evidence does not replace the field’s foundations with one new technique. It sharpens several boundaries: preserving tests under model evolution, semantic model interchange, independent-implementation communities, smaller variability spaces, and learned support for costly changes. The most recent inspected materials are not all equally mature or accessible.

| Source | Date / state | Inspected contribution | Not established |
| --- | --- | --- | --- |
| ESPLE-S028 | 2024; AUTHOR_INSTITUTION_ABSTRACT_ONLY | Three systems in one large company; artefact analysis and stakeholder survey; duplication and unsynchronised assets complicate evolution.; Time pressure and managerial/technical differences in perceived costs. | Full article unavailable through attempted publisher/author routes.; No unreported participant counts, measures, causal effect or debt interest rate inferred.; Earlier review, 2023 study and 2024 report may share evidence; not counted as independent replication. |
| ESPLE-S031 | 2023; FULL_TEXT_TARGETED_INSPECTION | Explicit extensions of 2016 and 2020 work; imports supervisory control and discrete-event models.; Controllable/uncontrollable events, strict/relaxed constraints, transitional requirements and synthesis guarantees.; Body Comfort System benchmark, not deployed physical-system certification. | Correctness is relative to adequate models and actual controllability; marked-state reachability is not inevitable progress.; Atomic simultaneous reconfiguration must be physically implementable.; BCS is a reused industrial-origin benchmark; scale is not deployment. |
| ESPLE-S032 | 2025; FULL_TEXT_TARGETED_INSPECTION | MODEVAR community initiative and interoperability motivation.; Boolean/arithmetic/type levels, syntax and semantics; Figure 3 screenshot inspected.; Authors report CVL and ISO-26558 limitations; original legal history not independently verified. | Community language is not automatically a ratified ISO standard or universal semantic interchange guarantee.; Tool/version/language-level support needs checking.; No inference that interoperability proves economic superiority. |
| ESPLE-S034 | 2026-06-17; FULL_TEXT_TARGETED_INSPECTION | Ten C/C++ projects and a small regeneration illustration.; Variability by regeneration using an LLM and specifications. | Unreplicated exploratory proposal, not validated industrial superiority or safety.; Generation-time variability predates LLMs; broad historical novelty is not accepted.; A July 2026 HAL v2/conference manuscript was discovered but access protection prevented reading; conclusions are explicitly bounded to the inspected June arXiv v1, not claimed identical to v2. |
| ESPLE-S035 | 2026; inspected 2026-09-06; PUBLIC_PAGE | SPLC, VaMoS and ICSR come together as VARIABILITY 2026; event is after research cut-off. | Programme is not completed conference outcomes, publication validation or replication. |
| ESPLE-S036 | 2025; METADATA_AND_ACCESS_LIMIT | A 2025 SPLC contribution specifically studies LLM-based co-evolution. | HAL document blocked by access protection and ACM full text not returned.; No method accuracy or outcome claimed from the title/search snippet. |
| ESPLE-S037 | 2025 online; 2026 journal; FULL_TEXT_TARGETED_INSPECTION | Configuration-oriented tests after FM edits; regeneration, repair and change-specific tests have distinct objectives. Mutation results and acknowledged dissimilarity-to-effort limitation. | Tests are configurations and FM mutation discrimination, not full behavioural regression tests.; Artificial model mutations are not independent industrial migrations; dissimilarity may not track real repair labour.; 2025-10-08 online publication differs from the 2026 journal volume; 2023/2024 predecessors share the research programme. |
| ESPLE-S038 | 2026-02-12; FULL_TEXT_TARGETED_INSPECTION | Ten textual DSL cases and repeated model runs; correctness and human-oriented information.; Scaling and grammar complexity limit co-evolution; validation remains necessary. | Textual DSL migration is an adjacent-domain transfer claim, not direct evidence for complete product-family migration.; Models, prompts and cases are version-specific; repeated runs do not create independent organisations. |
| ESPLE-S039 | 2025; AUTHOR_ABSTRACT_ONLY | Interval-based feature models, temporal/spatial scopes and modular soundness of evolution-plan updates. | Formal proof and detailed benchmark not inspected; only the stated problem and result scope are reported.; 2023 conference antecedent and 2025 extension are not counted as independent replications. |
| ESPLE-S044 | 2026-03-21; FULL_TEXT_TARGETED_INSPECTION | Proposal catalogues, independent implementations, interoperability and autonomous evolution differ from a centrally managed product-production system.; Fourteen selected ecosystems classified; feature-oriented techniques proposed without enforcing SPLE processes. | Taxonomic classification and illustrative ecosystem evidence, not causal proof of economic superiority.; De-facto agreement uses proxies and researcher judgement; underlying source dates differ from 2026 publication.; 2025 precursor belongs to the same programme, not independent replication. |
| ESPLE-S045 | 2026-04-17; FULL_TEXT_TARGETED_INSPECTION | Coreutils 9.1, 108 programs, historical subset of 20 programs across 85 releases; option counting excludes external-library/build-script variability.; Removing or earlier binding options; proposed null variability; behavioural-consistency wording qualified by non-identical outputs. | Within-program/codebase correlations do not identify causal maintainability gains.; Ordinary inputs and environmental effects must not be collapsed into configurable features.; Our objection concerns inferring environment independence from early feature binding, not the existence of useful fixed-function programs. |

The community taxonomy and small-configurability proposals widen the alternatives worth examining, but do not establish universal superiority. Learned outputs remain candidates requiring checks. The announced 2026 event is future relative to this cut-off; it contributes a current research venue, not completed proceedings evidence beyond the individual works separately inspected.

## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_ADVERSARIAL_SYNTHESIS_VERDICT

The strongest core survives adversarial examination because it does not depend on the questionable claims that reuse is always cheaper, every family needs a global model, all derivation should be automatic or one assurance technique proves every product. It instead preserves the relationships that make a family-production claim meaningful: a justified boundary, explicit distinctions, a usable realisation, identified products, scoped evidence, continuity and accountable decisions.

The strongest objection to unification is that these relationships can become an expensive administrative superstructure. A sufficiently broad framework can appear to explain everything while deciding nothing. The answer here is not another universal control. It is the six selectable configurations, explicit cheap paths, real non-family alternative, per-property retirement conditions and the requirement that each artefact have a consequential consumer. A later implementation that adds a new procedure for every row would contradict this synthesis.

A second objection is evidential: much industrial knowledge is observational, while formal work proves narrower properties than the business claims people attach to it. This objection changes dispositions. Economics and learned assistance are assumption-sensitive; several techniques are domain-specific; cloning remains admissible; regeneration replacement remains unresolved. The report does not hide these limits behind one confidence score.

A third objection concerns power and operation. Correct information can be inert when nobody can act on it, and formal permission inside a model can be mistaken for real authority. The composed system therefore distinguishes observations, decisions, authorised interventions and observed consequences. This is an analytic clarification grounded in the production, organisational and control mechanisms, not a claim that the tradition grants a universal authority model.

**Verdict:** a coherent conditional within-tradition synthesis is warranted. It supports governed selection among family-production mechanisms and adequate alternatives, with explicit feedback and evidence boundaries. It does **not** establish universal SPLE superiority, a complete formal proof of the combined system, a mature learned-regeneration replacement, a required target architecture, or adoption by any real host system. The analytical cases expose invalid inferences; they do not certify effectiveness outside their constructed assumptions.


## EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_OPEN_QUESTIONS_AND_EVIDENCE_LIMITS

The study closes its examined scope, not all open research. The following uncertainties remain material: how to forecast useful family demand; how to quantify coordination and support costs without false precision; how to recover intended variability from incomplete artefacts; how to preserve behavioural meaning when models evolve; which interactions matter beyond an affordable sample; how to validate runtime model/plant correspondence; and whether learned regeneration can preserve accumulated assurance with lower lifecycle burden.

None of these is silently recorded as `NOT_EXAMINED`. The mechanisms, major objections and relevant inspected evidence have dispositions. A later real system must supply its own products, obligations, models, production paths, outcomes and costs before transfer can be justified.

### Empirical evidence and dependence register

**ESPLE-E01 — ESPLE-S026.** Units: Practitioners and industrial product lines. Sample: 11 practitioners; 6 product lines; 3 organisations in automotive, aerospace/defence and storage. Comparison: Qualitative comparison of reasons for cloning and difficulties, not randomised economic treatment. Outcome: Documents pragmatic adoption motives, autonomy and propagation/consistency difficulties; no general causal effect estimated. Limits: Exploratory selection, self-report and limited organisations; no representative prevalence or universal cost threshold. Dependence: Multiple observations within organisations and product lines are not independent deployments.

**ESPLE-E02 — ESPLE-S027.** Units: Engineers performing prescribed maintenance tasks. Sample: 10 engineers, 5 in each arm, 4 tasks each: 40 task observations, not 40 independent people; BSH setting. Comparison: Clone-and-own versus a prepared SPL implementation for the selected tasks. Outcome: Reported task-level performance favours the SPL condition in this setting. This packet does not extrapolate a universal effect or reanalyse unavailable raw data. Limits: Small groups, repeated tasks, preparedness and excluded setup/platform investment limit transfer. Correlation/power concerns are this study’s analytical caution, not a reported retraction. Dependence: One company/study; repeated task observations share participants and artefacts.

**ESPLE-E03 — ESPLE-S021.** Units: Generated JHipster configurations. Sample: Historical JHipster 3.6.1; Results §6.1: 26,256 configurations, 9,376 failures (35.70%); introduction differs by one. Comparison: Exhaustive attempted configuration campaign and sampling alternatives in the reported space. Outcome: Six faults reported, including interaction order up to four; distinguishes compilation/derivation outcomes from a high-level configuration model. Limits: One generator/version and recorded environment; failed configurations are not independent root causes; no current prevalence claim. Dependence: Thousands of failing products share a small set of faults and the same generator.

**ESPLE-E04 — ESPLE-S020.** Units: Configuration-related faults and sampling algorithms. Sample: 135 faults in the study corpus; ten sampling algorithms with varied assumptions. Comparison: Sampling strategies under different handling of headers, build information and constraints. Outcome: Relative conclusions and cost/coverage depend materially on these assumptions. Limits: Benchmark selection, analysed languages and configuration knowledge limit transfer; fault count is not system count. Dependence: Configurable-system corpora overlap the wider analysis literature; not independent replications merely because papers differ.

**ESPLE-E05 — ESPLE-S040.** Units: Analyses applied to configurable C systems. Sample: Seven analyses on five systems: BusyBox, OpenSSL, SQLite, Linux x86 and uClibc. Comparison: Variability-aware analysis and relevant product-oriented baselines under specified settings. Outcome: Shows scale and sharing trade-offs; outputs include warnings, not an established count of independently confirmed defects. Limits: Underlying analyses can be imprecise; configuration/build representation and measured setups bound conclusions. Dependence: Overlaps TypeChef-related research and common open-source subjects.

**ESPLE-E06 — ESPLE-S041.** Units: Selected industrial products and artefacts. Sample: Seven purposively selected diverse projects in Bosch PS-EC; mixed configuration/code-management dependencies. Comparison: Reverse-engineered variability compared and interpreted with domain knowledge. Outcome: Stale central models, heterogeneous dependencies and extraction limitations are reported; subsystem modelling is motivated. Limits: One family; not entire codebase; raw feature counts withheld; no controlled economic test of the proposed response. Dependence: Seven projects in one industrial programme, not seven independent industrial replications.

**ESPLE-E07 — ESPLE-S028.** Units: Systems within a company. Sample: Three systems in one company; accessible institutional abstract only. Comparison: Field description of opportunistic reuse and variability debt. Outcome: The abstract supports the existence of observed debt concerns, not uninspected metrics, methods or effect sizes. Limits: Full methods, sampling and measures inaccessible; no detailed causal inference. Dependence: Possible relation to authors’ thesis/programme; no independence claim.

**ESPLE-E08 — ESPLE-S037.** Units: Feature-model families, evolutions and configuration tests. Sample: 13 model families; 35 natural evolutions; over 3,200 mutants, as reported. Comparison: Repair/retention/regeneration alternatives for test configurations under feature-model evolution. Outcome: Demonstrates trade-offs in model/test evolution; distance-based effort proxies are not measured human maintenance labour. Limits: Mutation and model-configuration coverage are not full behavioural defect detection; selected family corpus limits transfer. Dependence: Multiple mutants/evolutions reuse families; not thousands of independent systems.

**ESPLE-E09 — ESPLE-S044.** Units: Selected software ecosystems and their variability arrangements. Sample: 14 selected ecosystems plus two Bitcoin-related interviews. Comparison: Taxonomic classification using project evidence and proxy measures. Outcome: Identifies independently implemented, interoperability-oriented community-driven variability as a distinct arrangement. Limits: Researcher judgement, selection and proxy data; no causal evidence that one governance arrangement is superior. Dependence: Related 2025 precursor is ancestry, not an independent replication.

**ESPLE-E10 — ESPLE-S045.** Units: Small command-line programs and historical releases. Sample: 108 GNU coreutils 9.1 programs; longitudinal subset of 20 across 85 releases from 2003–2022. Comparison: Descriptive option/variability patterns and historical relations. Outcome: Supports investigation of small and earlier-bound variability; does not prove environmental independence or causal maintainability improvement. Limits: External libraries/build variability excluded; option counts are proxies; correlation is not causation. Dependence: Many programs share a project and releases; 2025 precursor mentioned but not independently counted.

**ESPLE-E11 — ESPLE-S034.** Units: Exploratory generated examples. Sample: Inspected June 2026 v1 includes ten small C/C++ examples and a wc-oriented demonstration. Comparison: Illustrative regeneration proposal, not a long-term industrial comparison against a competent maintained family. Outcome: Establishes a research proposal and examples; lifecycle superiority remains unresolved. Limits: Small examples, changing learned models, limited continuity evidence; later HAL version blocked. Dependence: Repeated generated examples from one proposal do not constitute independent replications.

**ESPLE-E12 — ESPLE-S038.** Units: Textual DSL migration experiments. Sample: Ten DSLs with repeated runs, as described in the inspected preprint. Comparison: Learned support for co-evolution of definitions and instances. Outcome: Useful adjacent evidence on migration assistance and validation limits; not direct SPLE family-production effectiveness. Limits: Language scale and selected tasks; repeated runs are not independent domains; transfer is a new claim. Dependence: DOMAIN_TRANSLATION into SPLE, not counted as a direct industrial SPLE replication.

### Formal result boundaries

**ESPLE-F01.** Model: An explicitly encoded Boolean or richer variability model. Guarantee: Satisfiability and diagnostic queries concern assignments satisfying the encoded constraints. Assumptions: Correct encoding and supported solver semantics. Implementation obligation: Establish domain adequacy and model-to-built-product correspondence separately. [ESPLE-S014; ESPLE-S015]

**ESPLE-F02.** Model: Configuration sets induced by old and new feature models and the specified correspondence. Guarantee: Classification of edits as specialisation, generalisation, refactoring or other set change. Assumptions: Defined configuration semantics and correctly related features. Implementation obligation: Feature names and configuration-set equality do not prove behavioural or requirement continuity. [ESPLE-S023]

**ESPLE-F03.** Model: Variability-aware program representation and an underlying analysis. Guarantee: Results retain configuration conditions and share computations; the exact claim is inherited from the underlying analysis. Assumptions: Supported language/build/preprocessor semantics and faithful represented family. Implementation obligation: Expose unsupported artefacts and distinguish warnings from confirmed product faults. [ESPLE-S019; ESPLE-S022; ESPLE-S040]

**ESPLE-F04.** Model: Discrete-event models of features, behaviour and controllable/uncontrollable events. Guarantee: Specified model-level safety and nonblocking through supervisory synthesis. Assumptions: Correct plant abstraction, observable/control assumptions and feasible synthesis. Implementation obligation: Nonblocking means a marked completion remains reachable, not that every real execution inevitably progresses; validate physical and operational correspondence. [ESPLE-S031]

**ESPLE-F05.** Model: Feature-model evolution plans, per author abstract. Guarantee: A modular soundness-checking approach is claimed by the abstract. Assumptions: Full proof and precise technical assumptions were not accessible. Implementation obligation: No detailed theorem or implementation guarantee is imported into this synthesis from abstract-only access. [ESPLE-S039]

### Access limits and coverage

| Source | Access | Disposition |
| --- | --- | --- |
| ESPLE-S002 | BIBLIOGRAPHIC_AND_ABSTRACT_LIMIT | Publisher page did not expose full text; author-upload download failed.; Detailed reconstruction instead uses the separately identified 1979 original and explicit reception in later inspected work; no unread theorem is attributed to this paper. Inspected only at the stated level. Unavailable content supplies no methodological detail, effect size or proof in this packet. |
| ESPLE-S004 | ABSTRACT_ONLY | Full text not exposed by the author-work record.; 1991 SBES precursor located but not retrieved; no assertion that the conference and journal versions are identical.; The 1980 domain-analysis ancestry is documented in FODA, not inferred from the 2011 upload date. Inspected only at the stated level. Unavailable content supplies no methodological detail, effect size or proof in this packet. |
| ESPLE-S008 | PUBLISHER_EXCERPTS | Not full-book access.; Publication/copyright/citation-year differences are recorded, not treated as different schools.; Publisher benefit descriptions do not independently verify industrial effect sizes. Inspected only at the stated level. Unavailable content supplies no methodological detail, effect size or proof in this packet. |
| ESPLE-S028 | AUTHOR_INSTITUTION_ABSTRACT_ONLY | Full article unavailable through attempted publisher/author routes.; No unreported participant counts, measures, causal effect or debt interest rate inferred.; Earlier review, 2023 study and 2024 report may share evidence; not counted as independent replication. Inspected only at the stated level. Unavailable content supplies no methodological detail, effect size or proof in this packet. |
| ESPLE-S033 | PUBLIC_SCOPE_ONLY | Full normative clauses not inspected; no clause-level compliance obligations invented.; Issuing-body benefit language is not independent effectiveness evidence.; Later draft temporal-management standard is a discovery lead, not treated as adopted normative text. Inspected only at the stated level. Unavailable content supplies no methodological detail, effect size or proof in this packet. |
| ESPLE-S036 | METADATA_AND_ACCESS_LIMIT | HAL document blocked by access protection and ACM full text not returned.; No method accuracy or outcome claimed from the title/search snippet. Inspected only at the stated level. Unavailable content supplies no methodological detail, effect size or proof in this packet. |
| ESPLE-S039 | AUTHOR_ABSTRACT_ONLY | Formal proof and detailed benchmark not inspected; only the stated problem and result scope are reported.; 2023 conference antecedent and 2025 extension are not counted as independent replications. Inspected only at the stated level. Unavailable content supplies no methodological detail, effect size or proof in this packet. |
| ESPLE-S042 | ABSTRACT_ONLY | Author-hosted PDF failed twice; no taxonomy details inferred from later citing snippets.; Detailed realisation comparisons in this packet instead use inspected FOSD, delta, FAST and Bosch sources. Inspected only at the stated level. Unavailable content supplies no methodological detail, effect size or proof in this packet. |
| ESPLE-S043 | ABSTRACT_ONLY | Original full text not exposed; operational reconstruction relies on separate full Bencomo and Thuijsman/Reniers texts.; Host shows May; volume 41(4) corresponds to April issue; year is unambiguous. Inspected only at the stated level. Unavailable content supplies no methodological detail, effect size or proof in this packet. |
| ESPLE-S034 | LATER_VERSION_ACCESS_BLOCKED | June 2026 arXiv v1 inspected; later July HAL v2 located but unavailable. No claim that the inspected version is the final or only current version. Replacement superiority remains UNRESOLVED; later unavailable content is not assumed to confirm or refute it. |

All ten mandatory families and all 62 candidates were examined; the exact coverage and grouped search record are in [RESEARCH_COVERAGE.json](EVOLVED_SOFTWARE_PRODUCT_LINE_ENGINEERING_RESEARCH_COVERAGE.json). Search saturation refers to candidate-changing mechanisms, criticisms, assumptions and relations, not an exhaustive search of every publication. The 45 source records are not 45 independent empirical studies.

### Freeze meaning

Revision **ESPLE-2026-09-06-r1** fixes this scope, denominator, source-access record and present judgements at **2026-09-06**. One primary property disposition remains unresolved. Frozen means stable and inspectable, not universally certain. The manifest and external archive receipt attest exact-byte custody; they do not strengthen substantive evidence. No sibling corpora were consulted and no cross-trifecta synthesis was performed.

## Source directory

Exact works and inspected locators follow. The JSON source table retains additional version, evidence-role and dependence metadata.

### ESPLE-S001

Mass Produced Software Components. M. Douglas McIlroy. **Date:** 1968 conference; 1969 report. **Version/edition:** Author-hosted transcript dated 1998-10-15; report pp. 138–155. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.cs.dartmouth.edu/~doug/components.txt

- `ESPLE-S001-L01` — Transcript opening: Separates conference, proceedings and transcription dates.
- `ESPLE-S001-L02` — Component families discussion: Components varied by precision, robustness, generality and time/space trade-offs.

Limits: Transcript changes some layout and spelling; not a 1998 founding work. A precursor to systematic reuse, not the entire later SPLE lifecycle.

### ESPLE-S002

On the Design and Development of Program Families. David L. Parnas. **Date:** 1976. **Version/edition:** IEEE TSE SE-2(1), pp. 1–9. **Access:** BIBLIOGRAPHIC_AND_ABSTRACT_LIMIT on 2026-09-06.

Locator: https://doi.org/10.1109/TSE.1976.233797

- `ESPLE-S002-L01` — Publisher/author-upload bibliographic record: Original title, authorship, journal and date; family-design framing.

Limits: Publisher page did not expose full text; author-upload download failed. Detailed reconstruction instead uses the separately identified 1979 original and explicit reception in later inspected work; no unread theorem is attributed to this paper.

### ESPLE-S003

Designing Software for Ease of Extension and Contraction. David L. Parnas. **Date:** 1979. **Version/edition:** IEEE TSE journal version; distinct from the 1978 conference antecedent. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.dre.vanderbilt.edu/~schmidt/PDF/family.pdf

- `ESPLE-S003-L01` — Opening and program-families discussion, PDF pp. 1–2: Family membership is pragmatically motivated by studying common aspects together.
- `ESPLE-S003-L02` — Design principles and extension/contraction discussion: Design decisions and module structures affect the ability to add or remove capabilities.

Limits: Architectural argument and examples, not comparative product-portfolio economics. The phrase that joint study pays does not by itself establish what pays in a particular market.

### ESPLE-S004

The Evolution from Software Components to Domain Analysis. James M. Neighbors. **Date:** 1992. **Version/edition:** International Journal of Software Engineering and Knowledge Engineering 2(3), pp. 325–354; digitised record displays 2011. **Access:** ABSTRACT_ONLY on 2026-09-06.

Locator: https://doi.org/10.1142/S0218194092000166

- `ESPLE-S004-L01` — Author-work abstract on ResearchGate, publication/2378303: Retrospective component/domain-analysis rationale and acknowledgement of limiting factors.

Limits: Full text not exposed by the author-work record. 1991 SBES precursor located but not retrieved; no assertion that the conference and journal versions are identical. The 1980 domain-analysis ancestry is documented in FODA, not inferred from the 2011 upload date.

### ESPLE-S005

Feature-Oriented Domain Analysis (FODA) Feasibility Study. Kyo C. Kang; Sholom G. Cohen; James A. Hess; William E. Novak; A. Spencer Peterson. **Date:** 1990-11. **Version/edition:** CMU/SEI-90-TR-21; original report, 163-page author-upload PDF. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.sei.cmu.edu/library/feature-oriented-domain-analysis-foda-feasibility-study/

- `ESPLE-S005-L01` — Introduction/definitions, PDF pp. 13–15: Domain analysis, users, experts and scope; economic/legal issues excluded.
- `ESPLE-S005-L02` — Historical review, PDF pp. 23–24: Prior domain-analysis approaches and Neighbors ancestry.
- `ESPLE-S005-L03` — Printed p. 26, Figure 3-3 and Table 3-1: Abstraction/reuse relation and limitations of information sources; screenshot inspected.
- `ESPLE-S005-L04` — Section 7.3.2, printed pp. 63ff: Feature model includes dependencies, rationale and existing-system information, not only a diagram.

Limits: Feasibility report rather than controlled adoption trial. Feature and architectural models require domain validation; economic benefit is outside its declared analysis.

### ESPLE-S006

Software Product Lines: a Case Study. Mark Ardis; Nigel Daley; Daniel Hoffman; Harvey Siy; David Weiss. **Date:** 2000. **Version/edition:** Software—Practice & Experience 30, pp. 825–847; author-upload text. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.researchgate.net/publication/2391127_Software_Product_Lines_a_Case_Study

- `ESPLE-S006-L01` — FAST overview and domain/application activities: Commonality analysis, domain knowledge and product feedback.
- `ESPLE-S006-L02` — Header Table example and testing sections: Worked generation and test construction, including nontrivial test-oracle work.
- `ESPLE-S006-L03` — Opening experience claims: Lucent programme experience reported, not independent controlled samples.

Limits: Worked example plus same-programme experience; large productivity claims lack a reported general comparative denominator. Weiss and Lai 1999 book is referenced by this original but was not read in full.

### ESPLE-S007

PuLSE: A Methodology to Develop Software Product Lines. Joachim Bayer; Oliver Flege; Peter Knauber; Roland Laqua; Dirk Muthig; Klaus Schmid; Tanya Widen; Jean-Marc DeBaud. **Date:** 1999. **Version/edition:** SSR 1999, pp. 122–131; DOI 10.1145/303008.303063. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.researchgate.net/publication/221563923_PuLSE_a_Methodology_to_Develop_Software_Product_Lines

- `ESPLE-S007-L01` — Introduction and motivation: Over-broad domain scope, deployment complexity and inadequate customisation are explicit objections.
- `ESPLE-S007-L02` — PuLSE framework and deployment: Enterprise-focused scoping, customisable components and incremental introduction.

Limits: Method and transfer experience, not an independent quantified comparison of all adoption strategies.

### ESPLE-S008

Software Product Lines: Practices and Patterns. Paul Clements; Linda Northrop. **Date:** 2001 publication; commonly cited 2002. **Version/edition:** First edition; publisher preface, contents and excerpts only; ISBN 9780201703320. **Access:** PUBLISHER_EXCERPTS on 2026-09-06.

Locator: https://www.informit.com/store/software-product-lines-practices-and-patterns-9780201703320

- `ESPLE-S008-L01` — Preface/three essential activities: Core-asset development, product development, and technical/organisational management are coupled.
- `ESPLE-S008-L02` — Contents and publisher excerpts: Practice areas and patterns organise a broader programme than code reuse.

Limits: Not full-book access. Publication/copyright/citation-year differences are recorded, not treated as different schools. Publisher benefit descriptions do not independently verify industrial effect sizes.

### ESPLE-S009

Software Product Line Engineering: Foundations, Principles, and Techniques — Chapter 2. Klaus Pohl; Günter Böckle; Frank J. van der Linden. **Date:** 2005. **Version/edition:** Author-hosted chapter preview, printed pp. 19–38, not the whole book. **Access:** FULL_CHAPTER_TARGETED_INSPECTION on 2026-09-06.

Locator: https://sple.de/fileadmin/sse/user_upload/Files/SPLE-Book_Chap02.pdf

- `ESPLE-S009-L01` — Printed pp. 19–21: Planned reuse can cost more than scratch; distinct but coupled domain/application activities.
- `ESPLE-S009-L02` — Printed p. 21: Explicit references to Weiss/Lai and ESAPS, CAFÉ and FAMILIES projects; screenshot inspected.
- `ESPLE-S009-L03` — Chapter 2 requirements/design/realisation/testing and feedback: Variability, reusable assets and application feedback across engineering activities.

Limits: Framework argument and programme-derived synthesis, not a randomised productivity comparison. Other book chapters were not silently claimed as read.

### ESPLE-S010

Easing the Transition to Software Mass Customization. Charles W. Krueger. **Date:** 2001 workshop; 2002 proceedings. **Version/edition:** PFE-4 paper; 13-page original preprint. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://static.aminer.org/pdf/PDF/000/539/830/easing_the_transition_to_software_mass_customization.pdf

- `ESPLE-S010-L01` — Introduction: Upfront cost, effort, risk and latency constrain adoption.
- `ESPLE-S010-L02` — Section 4 and subsections 4.1–4.3: Extractive, reactive and proactive approaches, including mixed sequences.

Limits: Author is the BigLever vendor principal; mechanism description does not independently establish GEARS superiority. Mass-customisation terminology overlaps with but does not exhaust SPLE.

### ESPLE-S011

Guidelines for Developing a Product Line Production Plan. Gary Chastek; John D. McGregor. **Date:** 2002-06. **Version/edition:** CMU/SEI-2002-TR-006; DOI 10.1184/R1/6574031.v1. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.sei.cmu.edu/documents/676/2002_005_001_14024.pdf

- `ESPLE-S011-L01` — Introduction and plan guidance: How a product uses the correct core assets depends on organisational context.
- `ESPLE-S011-L02` — Maintaining the production plan, printed pp. 26–27: Versioned product-specific plans link to core assets; support duration changes upgrade policy.
- `ESPLE-S011-L03` — Printed p. 27, Figure 7: Plan/product/core-asset version relationships; screenshot inspected.

Limits: Guidance, not evidence that a specific production plan is actually followed. Does not mandate the particular cryptographic identity tuple proposed analytically in this packet.

### ESPLE-S012

The Structured Intuitive Model for Product Line Economics (SIMPLE). Paul Clements; John McGregor; Sholom Cohen. **Date:** 2005-02. **Version/edition:** CMU/SEI-2005-TR-003; DOI 10.1184/R1/6585293.v1. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.sei.cmu.edu/documents/746/2005_005_001_14579.pdf

- `ESPLE-S012-L01` — Cost functions and time-period discussion, PDF pp. 22ff: Organisational, asset, unique-product, reuse and update costs depend on time and adoption mode.
- `ESPLE-S012-L02` — Printed pp. 16–19, equations 7–13: Standalone/product-line evolution comparison and scenario-specific returns; screenshot inspected.
- `ESPLE-S012-L03` — Section 4.5 decomposition: Costs include training, data collection, reorganisation and migration.

Limits: Illustrative numerical scenarios are not measured industrial returns. Cost decomposition needs locally defensible estimates; no universal break-even count follows.

### ESPLE-S013

Clearing the Way for Software Product Line Success. Lawrence G. Jones; Linda M. Northrop. **Date:** 2010. **Version/edition:** IEEE Software, pp. 22–28; original seven-page article. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://homepages.dcc.ufmg.br/~figueiredo/disciplinas/2014b/reuse/05452145.pdf

- `ESPLE-S013-L01` — Printed pp. 22–26: SEI experience includes failed/abandoned and struggling efforts; strategy, organisation and rollout issues.
- `ESPLE-S013-L02` — Production-plan and code-only reuse discussions: Core assets without a workable product-production approach do not realise promised benefit.
- `ESPLE-S013-L03` — First page: Author identities checked by screenshot.

Limits: Experience across programmes over fifteen years; no disclosed denominator from which a failure rate can be calculated. SEI successes repeated elsewhere are not new replications.

### ESPLE-S014

Feature Models, Grammars, and Propositional Formulas. Don Batory. **Date:** 2005. **Version/edition:** Author report TR-05-14; SPLC DOI 10.1007/11554844_3. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.cs.utexas.edu/ftp/predator/TR-05-14.pdf

- `ESPLE-S014-L01` — Grammar/formula translation, PDF pp. 3–4: Boolean semantics of features and non-tree constraints; screenshot inspected.
- `ESPLE-S014-L02` — SAT-based reasoning and guidance sections: Consistency and decision support within encoded feature semantics.

Limits: Logical results concern the encoding, not unmodelled stakeholder constraints, generators or runtime behaviour.

### ESPLE-S015

Automated Analysis of Feature Models 20 Years Later: A Literature Review. David Benavides; Sergio Segura; Antonio Ruiz-Cortés. **Date:** 2010. **Version/edition:** Information Systems 35(6), pp. 615–636; DOI 10.1016/j.is.2010.01.001. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.researchgate.net/publication/223760542_Automated_analysis_of_feature_models_20_years_later_A_literature_review

- `ESPLE-S015-L01` — Analysis operations taxonomy: Void models, dead/false-optional features, configuration, explanations and related operations.
- `ESPLE-S015-L02` — Discussion of analysis techniques and limitations: Different feature extensions and encodings support different operations.

Limits: Review organises evidence; underlying papers are not independent replications of the review. Model consistency must not be upgraded to delivered-product correctness.

### ESPLE-S016

Scaling Step-Wise Refinement. Don Batory; Jacob Neal Sarvela; Axel Rauschmayer. **Date:** 2004. **Version/edition:** IEEE TSE 30(6), pp. 355–371; author manuscript. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.cs.utexas.edu/~schwartz/ATS/fopdocs/AHEAD-Theory.pdf

- `ESPLE-S016-L01` — AHEAD representation and hierarchical composition: Feature refinements compose related code and non-code artefacts.
- `ESPLE-S016-L02` — Examples and discussion: Algebraic organisation does not eliminate interaction obligations.

Limits: Formal representation and examples are not a proof about every language/toolchain or market outcome.

### ESPLE-S017

An Overview of Feature-Oriented Software Development. Sven Apel; Christian Kästner. **Date:** 2009. **Version/edition:** Journal of Object Technology 8(4); author manuscript. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.cs.cmu.edu/~ckaestne/pdf/JOT09_OverviewFOSD.pdf

- `ESPLE-S017-L01` — Sections on feature modelling, implementation and interaction: Problem/solution spaces, feature modules, interactions and refinements.
- `ESPLE-S017-L02` — Printed pp. 16–18, sections 4.3–4.4: Annotation/composition trade-off; full generation is a FOSD goal, not a definition of every SPLE approach; screenshot inspected.

Limits: School overview includes author-developed technologies; taxonomy is not an unbiased experiment comparing all techniques. Interaction-code factoring scalability remains qualified.

### ESPLE-S018

Delta-Oriented Programming of Software Product Lines. Ina Schaefer; Lorenzo Bettini; Viviana Bono; Ferruccio Damiani; Nico Tanzarella. **Date:** 2010. **Version/edition:** SPLC, pp. 77–91; DOI 10.1007/978-3-642-15579-6_6. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.researchgate.net/publication/220789518_Delta-Oriented_Programming_of_Software_Product_Lines

- `ESPLE-S018-L01` — Introduction and core/delta construction: Adds, removes and modifies elements, addressing limits of purely additive feature composition.
- `ESPLE-S018-L02` — Delta applicability and ordering: Selection and composition order are distinct obligations.

Limits: Mechanism-specific guarantees under the presented language; not a universal migration or interoperability theorem.

### ESPLE-S019

A Classification and Survey of Analysis Strategies for Software Product Lines. Thomas Thüm; Sven Apel; Christian Kästner; Ina Schaefer; Gunter Saake. **Date:** 2014. **Version/edition:** ACM Computing Surveys 47(1), article 6; DOI 10.1145/2580950. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.researchgate.net/publication/269853958_A_Classification_and_Survey_of_Analysis_Strategies_for_Software_Product_Lines

- `ESPLE-S019-L01` — Strategy classification and comparison: Product-based, feature-based, family-based and combined analyses have different reuse/coverage obligations.
- `ESPLE-S019-L02` — Discussion of research challenges: Implementation-language, scalability and evaluation boundaries.

Limits: Survey taxonomy is not direct proof of each surveyed analysis nor independent adoption evidence.

### ESPLE-S020

A Comparison of 10 Sampling Algorithms for Configurable Systems. Flávio Medeiros; Christian Kästner; Márcio Ribeiro; Rohit Gheyi; Sven Apel. **Date:** 2016. **Version/edition:** ICSE; DOI 10.1145/2884781.2884793; arXiv v3. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://arxiv.org/html/1602.02052v3

- `ESPLE-S020-L01` — Study design, assumptions and results: Sampling ranking depends on constraints, headers, file/global scope and build variability.
- `ESPLE-S020-L02` — Discussion and threats: No one universally best technique; realistic assumptions change applicability.

Limits: Fault corpus and open-source subjects overlap other configuration studies; not an industrial portfolio trial. Bug-detection comparisons do not prove arbitrary higher-order correctness.

### ESPLE-S021

Test them all, is it worth it? Assessing configuration sampling on the JHipster Web development stack. Axel Halin; Alexandre Nuttinck; Mathieu Acher; Xavier Devroey; Gilles Perrouin; Patrick Heymans. **Date:** 2018 online; 2019 journal. **Version/edition:** Empirical Software Engineering; DOI 10.1007/s10664-018-9635-4; empirical target JHipster 3.6.1. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://link.springer.com/article/10.1007/s10664-018-9635-4

- `ESPLE-S021-L01` — Experimental setup and section 6.1: Bounded configuration-space execution: 26,256 tested configurations and 9,376 failures.
- `ESPLE-S021-L02` — Interaction and sampling results: Six faults involving up to four options; generation success did not ensure build/test success.
- `ESPLE-S021-L03` — Cost and threats: 4,376 CPU-hours, not elapsed wall time; version/tool-stack-specific study.
- `ESPLE-S021-L04` — Section 7, interview with lead developer: Version 3.6.1 is the studied release; not a current failure-rate estimate.

Limits: Introduction also prints 26,257; results denominator 26,256 is used without inventing a reconciliation. One generator family and test oracle; repeated later uses of JHipster are not independent replications.

### ESPLE-S022

Variability-Aware Parsing in the Presence of Lexical Macros and Conditional Compilation. Christian Kästner; Paolo G. Giarrusso; Tillmann Rendel; Sebastian Erdweg; Klaus Ostermann; Thorsten Berger. **Date:** 2011. **Version/edition:** OOPSLA; DOI 10.1145/2048066.2048128; author manuscript. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.mathematik.uni-marburg.de/~rendel/kaestner11variability-aware.pdf

- `ESPLE-S022-L01` — Lexer/parser architecture and examples: Conditional compilation, macros and include context jointly affect the analysed program.
- `ESPLE-S022-L02` — Section 7: Case-study evaluation of parsing, not behavioural correctness.

Limits: Parsing success is not testing or proof of application requirements. External feature/build inputs remain part of the analysis boundary.

### ESPLE-S023

Reasoning about Edits to Feature Models. Thomas Thüm; Don Batory; Christian Kästner. **Date:** 2009. **Version/edition:** ICSE, pp. 254–264; DOI 10.1109/ICSE.2009.5070526. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.cs.utexas.edu/ftp/predator/ICSE2009.pdf

- `ESPLE-S023-L01` — Edit classification and formal comparison: Refactoring, generalisation, specialisation and arbitrary change compare represented configuration sets.
- `ESPLE-S023-L02` — Reasoning and evaluation: Automated classification remains indexed to feature semantics and model representation.

Limits: Configuration-set equivalence is not implementation-behaviour equivalence. Names and changing feature universes require an explicit correspondence.

### ESPLE-S024

Evolving Feature Model Configurations in Software Product Lines. Jules White; José A. Galindo; Tripti Saxena; Brian Dougherty; David Benavides; Douglas C. Schmidt. **Date:** 2013 preprint/online; 2014 journal. **Version/edition:** Journal of Systems and Software 87, pp. 119–136; DOI 10.1016/j.jss.2013.10.010. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.cs.wm.edu/~dcschmidt/PDF/JSS-14.pdf

- `ESPLE-S024-L01` — Multi-step configuration problem and CSP formulation: Configuration paths include interim costs, requirements and feature-model drift.
- `ESPLE-S024-L02` — Section 6 experiments: Scalability experiments over model size and time steps; constraint-solver performance.

Limits: Synthetic/generated model evaluation is not a deployed migration outcome. Encoded path validity does not establish business intent or real actuator safety. The paper uses loose null-hypothesis language; no claim of universally proven performance is adopted.

### ESPLE-S025

Incremental Feature Model Synthesis for Clone-and-Own Software Systems in MATLAB/Simulink. Alexander Schlie; Alexander Knüppel; Christoph Seidl; Ina Schaefer. **Date:** 2020. **Version/edition:** SPLC; DOI 10.1145/3382025.3414973. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://pure.itu.dk/ws/files/85551491/Incremental_Feature_Model_Synthesis.pdf

- `ESPLE-S025-L01` — Approach and synthesis workflow: Extracted models and manual domain refinements must coexist during incremental regeneration.
- `ESPLE-S025-L02` — Evaluation and limitations: MATLAB/Simulink variants provide a bounded extraction setting.

Limits: Observed variants underdetermine allowed but unseen products. Model extraction in a cyber-physical tool does not certify physical safety.

### ESPLE-S026

An Exploratory Study of Cloning in Industrial Software Product Lines. Yael Dubinsky; Julia Rubin; Thorsten Berger; Slawomir Duszynski; Martin Becker; Krzysztof Czarnecki. **Date:** 2013. **Version/edition:** CSMR; original ten-page paper. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://gsd.uwaterloo.ca/sites/default/files/2013-csmr-cloning.pdf

- `ESPLE-S026-L01` — Research design and questionnaire: Eleven practitioners, six product lines, three organisations; interviews/survey.
- `ESPLE-S026-L02` — Results and threats: Perceived simplicity, availability and team autonomy coexist with propagation/maintenance problems.

Limits: Convenience access and self-report; no randomised lifetime-cost estimate. Uses a broader descriptive SPL category than a strictly prescribed core-asset production definition; adverse cases are not excluded.

### ESPLE-S027

An Empirical Study of Performance Using Clone & Own and Software Product Lines in an Industrial Context. Jorge Echeverría; Francisca Pérez; José Ignacio Panach; Carlos Cetina. **Date:** 2021 journal; online chronology separately limited. **Version/edition:** Author manuscript hosted by Panach; BSH induction-hob experiment. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.uv.es/joigpana/Files/Journals/IST2021_An_empirical_study_of_performance_using_Clone.pdf

- `ESPLE-S027-L01` — Experimental design, tasks and measures, PDF pp. 8–10: Ten engineers, five per approach, four tasks each; effectiveness, efficiency and satisfaction.
- `ESPLE-S027-L02` — Results and threats, PDF pp. 10–14: SPL-favouring task outcomes; training, tool, task and setting limits.
- `ESPLE-S027-L03` — Participant observations: Generator confidence, change visibility and useful rather than merely numerous configurations.

Limits: Forty task observations are not forty independent engineers; repeated tasks create clustering. Upfront adoption and long-term support cost not measured. Claim that observed power excludes false rejection is not accepted; this is an analytical statistical objection, not a published retraction.

### ESPLE-S028

Variability debt in opportunistic reuse: A multi-project field study. Daniele Wolfart; Jabier Martinez; Wesley K. G. Assunção; Thelma E. Colanzi; Alexander Egyed. **Date:** 2024. **Version/edition:** Journal of Systems and Software 210, article 111969. **Access:** AUTHOR_INSTITUTION_ABSTRACT_ONLY on 2026-09-06.

Locator: https://research.jku.at/en/publications/variability-debt-in-opportunistic-reuse-a-multi-project-field-stu/

- `ESPLE-S028-L01` — Institutional abstract: Three systems in one large company; artefact analysis and stakeholder survey; duplication and unsynchronised assets complicate evolution.
- `ESPLE-S028-L02` — Abstract results: Time pressure and managerial/technical differences in perceived costs.

Limits: Full article unavailable through attempted publisher/author routes. No unreported participant counts, measures, causal effect or debt interest rate inferred. Earlier review, 2023 study and 2024 report may share evidence; not counted as independent replication.

### ESPLE-S029

From Software Product Lines to Software Ecosystems. Jan Bosch. **Date:** 2009. **Version/edition:** SPLC 2009, pp. 111–119; author-upload manuscript. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.researchgate.net/publication/220789544_From_software_product_lines_to_software_ecosystem

- `ESPLE-S029-L01` — Introduction and method statement: Opening the platform beyond organisational boundaries; participant-observer basis and public examples.
- `ESPLE-S029-L02` — Taxonomy and implications: Platforms, participants and transactions expand the coordination boundary.

Limits: Author explicitly supplies illustrative public examples without detailed references; no causal ecosystem-effect estimate. Ecological ancestry is a documented analogy, not proof that biological laws transfer. Not every ecosystem thereby implements managed product derivation.

### ESPLE-S030

Dynamically Adaptive Systems are Product Lines too: Using Model-Driven Techniques to Capture Dynamic Variability of Adaptive Systems. Nelly Bencomo; Pete Sawyer; Gordon Blair; Paul Grace. **Date:** 2008. **Version/edition:** Workshop/early model-driven dynamic variability paper; author manuscript. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://staffwww.dcs.shef.ac.uk/people/A.Simons/remodel/papers/BencomoDynAdapt.pdf

- `ESPLE-S030-L01` — Models, Genie and middleware mapping: Links runtime context, variability models and system reconfiguration.
- `ESPLE-S030-L02` — Discussion, PDF p. 8: Safe/quiescent reconfiguration is an explicit research obligation, not an established general guarantee.

Limits: Prototype/examples rather than deployed safety validation. Adaptive-system techniques are a documented hybrid, not all native SPLE invention.

### ESPLE-S031

Supervisory Control for Dynamic Feature Configuration in Product Lines. Sander Thuijsman; Michel Reniers. **Date:** 2023. **Version/edition:** arXiv 2211.07382 v3, 2023-05-16; TECS DOI 10.1145/3579644. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://arxiv.org/html/2211.07382v3

- `ESPLE-S031-L01` — Sections 1.1 and 2: Explicit extensions of 2016 and 2020 work; imports supervisory control and discrete-event models.
- `ESPLE-S031-L02` — Sections 4–7: Controllable/uncontrollable events, strict/relaxed constraints, transitional requirements and synthesis guarantees.
- `ESPLE-S031-L03` — Section 8: Body Comfort System benchmark, not deployed physical-system certification.

Limits: Correctness is relative to adequate models and actual controllability; marked-state reachability is not inevitable progress. Atomic simultaneous reconfiguration must be physically implementable. BCS is a reused industrial-origin benchmark; scale is not deployment.

### ESPLE-S032

UVL: Feature modelling with the Universal Variability Language. David Benavides; Chico Sundermann; Kevin Feichtinger; José A. Galindo; Rick Rabiser; Thomas Thüm. **Date:** 2025. **Version/edition:** JSS 225, 112326; pre-proof 2025-01-09; KIT deposit 2026-02-01; DOI 10.1016/j.jss.2024.112326. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://publikationen.bibliothek.kit.edu/1000179027/156998841

- `ESPLE-S032-L01` — Introduction: MODEVAR community initiative and interoperability motivation.
- `ESPLE-S032-L02` — Sections 4–5, printed pp. 10ff: Boolean/arithmetic/type levels, syntax and semantics; Figure 3 screenshot inspected.
- `ESPLE-S032-L03` — Discussion of earlier standardisation attempts: Authors report CVL and ISO-26558 limitations; original legal history not independently verified.

Limits: Community language is not automatically a ratified ISO standard or universal semantic interchange guarantee. Tool/version/language-level support needs checking. No inference that interoperability proves economic superiority.

### ESPLE-S033

ISO/IEC 26580:2021 — Methods and tools for the feature-based approach to software and systems product line engineering. ISO/IEC. **Date:** 2021-04. **Version/edition:** First edition; official public scope/metadata only. **Access:** PUBLIC_SCOPE_ONLY on 2026-09-06.

Locator: https://www.iso.org/standard/43139.html

- `ESPLE-S033-L01` — Official abstract/scope: Feature-based PLE is a specialisation of the more general ISO/IEC 26550 reference model; includes digital engineering work products.

Limits: Full normative clauses not inspected; no clause-level compliance obligations invented. Issuing-body benefit language is not independent effectiveness evidence. Later draft temporal-management standard is a discovery lead, not treated as adopted normative text.

### ESPLE-S034

Where Did the Variability Go? From Vibe Coding to Product Lines by Regeneration. Xhevahire Tërnava. **Date:** 2026-06-17. **Version/edition:** arXiv 2606.19042 v1. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://arxiv.org/html/2606.19042v1

- `ESPLE-S034-L01` — Exploratory study and limitations: Ten C/C++ projects and a small regeneration illustration.
- `ESPLE-S034-L02` — Proposal and future work: Variability by regeneration using an LLM and specifications.

Limits: Unreplicated exploratory proposal, not validated industrial superiority or safety. Generation-time variability predates LLMs; broad historical novelty is not accepted. A July 2026 HAL v2/conference manuscript was discovered but access protection prevented reading; conclusions are explicitly bounded to the inspected June arXiv v1, not claimed identical to v2.

### ESPLE-S035

VARIABILITY 2026 — official conference announcement and programme. VARIABILITY 2026 organisers. **Date:** 2026; inspected 2026-09-06. **Version/edition:** Scheduled 29 September–2 October 2026, Limassol. **Access:** PUBLIC_PAGE on 2026-09-06.

Locator: https://conf.researchr.org/home/variability-2026

- `ESPLE-S035-L01` — Conference welcome and dates: SPLC, VaMoS and ICSR come together as VARIABILITY 2026; event is after research cut-off.

Limits: Programme is not completed conference outcomes, publication validation or replication.

### ESPLE-S036

LLM-based Co-Evolution of Configurable Software Systems. Nada Zine; Clément Quinton; Romain Rouvoy. **Date:** 2025. **Version/edition:** SPLC volume A, pp. 27–38; DOI 10.1145/3744915.3748460; HAL record 05090995 v1. **Access:** METADATA_AND_ACCESS_LIMIT on 2026-09-06.

Locator: https://hal.science/hal-05090995

- `ESPLE-S036-L01` — HAL/publisher bibliographic record: A 2025 SPLC contribution specifically studies LLM-based co-evolution.

Limits: HAL document blocked by access protection and ACM full text not returned. No method accuracy or outcome claimed from the title/search snippet.

### ESPLE-S037

My feature model has changed... What should I do with my tests?. Andrea Bombarda; Silvia Bonfanti; Angelo Gargantini. **Date:** 2025 online; 2026 journal. **Version/edition:** JSS 231, 112645; DOI 10.1016/j.jss.2025.112645. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://aisberg.unibg.it/retrieve/14a1d2af-3462-4419-aeb0-afd898ffa9ab/1-s2.0-S0164121225003140-main.pdf

- `ESPLE-S037-L01` — Printed pp. 1, 13–15; Sections 6–9; Table 10 screenshot inspected: Configuration-oriented tests after FM edits; regeneration, repair and change-specific tests have distinct objectives. Mutation results and acknowledged dissimilarity-to-effort limitation.

Limits: Tests are configurations and FM mutation discrimination, not full behavioural regression tests. Artificial model mutations are not independent industrial migrations; dissimilarity may not track real repair labour. 2025-10-08 online publication differs from the 2026 journal volume; 2023/2024 predecessors share the research programme.

### ESPLE-S038

Leveraging LLMs to support co-evolution between definitions and instances of textual DSLs: A Systematic Evaluation. Weixing Zhang; Bowen Jiang; Yuhong Fu; Anne Koziolek; Regina Hebig; Daniel Strüber. **Date:** 2026-02-12. **Version/edition:** arXiv 2602.11904 v1; journal counterpart DOI 10.1007/s10270-026-01402-9. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://arxiv.org/html/2602.11904v1

- `ESPLE-S038-L01` — Research questions and study design: Ten textual DSL cases and repeated model runs; correctness and human-oriented information.
- `ESPLE-S038-L02` — Results, discussion and limitations: Scaling and grammar complexity limit co-evolution; validation remains necessary.

Limits: Textual DSL migration is an adjacent-domain transfer claim, not direct evidence for complete product-family migration. Models, prompts and cases are version-specific; repeated runs do not create independent organisations.

### ESPLE-S039

Modular soundness checking of feature model evolution plans. Crystal Chang Din; Charaf Eddine Dridi; Ida Sandberg Motzfeldt; Violet Ka I Pun; Volker Stolz; Ingrid Chieh Yu. **Date:** 2025. **Version/edition:** Theoretical Computer Science 1054, 115451; DOI 10.1016/j.tcs.2025.115451. **Access:** AUTHOR_ABSTRACT_ONLY on 2026-09-06.

Locator: https://violet.foldr.org/publication/fmep-tcs25/

- `ESPLE-S039-L01` — Author abstract: Interval-based feature models, temporal/spatial scopes and modular soundness of evolution-plan updates.

Limits: Formal proof and detailed benchmark not inspected; only the stated problem and result scope are reported. 2023 conference antecedent and 2025 extension are not counted as independent replications.

### ESPLE-S040

Variability-Aware Static Analysis at Scale: An Empirical Study. Alexander von Rhein; Jörg Liebig; Andreas Janker; Christian Kästner; Sven Apel. **Date:** 2018. **Version/edition:** Author manuscript dated October 2018; placeholder DOI omitted. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://www.se.cs.uni-saarland.de/publications/docs/RLJ%2B18.pdf

- `ESPLE-S040-L01` — Printed pp. 1–3: Seven control/data-flow analyses across five C systems; variability-aware sharing compared with sampling.
- `ESPLE-S040-L02` — Printed p. 26, validity discussion: Warnings are not adjudicated confirmed bugs; limitations of pointer analysis and false-positive evidence.

Limits: TypeChef and configurable-C benchmarks overlap with other analysis studies. Completeness is relative to the underlying analysis and supplied configuration information, not all defects. No measured warning count is represented as a failure prevalence.

### ESPLE-S041

Reverse Engineering Variability in an Industrial Product Line: Observations and Lessons Learned. Sascha El-Sharkawy; Saura Jyoti Dhar; Adam Krafczyk; Slawomir Duszynski; Tobias Beichter; Klaus Schmid. **Date:** 2018 conference; 2021-10-12 arXiv deposit. **Version/edition:** SPLC 2018; DOI 10.1145/3233027.3233047; arXiv 2110.05869 v1. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://arxiv.org/html/2110.05869v1

- `ESPLE-S041-L01` — Section 2: Bosch PS-EC shifts from monolithic central variation and stale central models to mixed realisation and subsystem modelling.
- `ESPLE-S041-L02` — Sections 3.2–3.6: Legacy support, non-Boolean values, mixed artefacts and extracted-constraint readability.
- `ESPLE-S041-L03` — Sections 4–6: Seven selected delivered product projects; omitted sources and approximate extraction; domain knowledge must supplement feature-effect constraints.

Limits: Seven purposefully diverse projects in one product line, not seven independent organisations. Prospective reduced configuration effort is not measured realised savings. Model extraction does not establish all domain obligations; raw feature counts withheld for confidentiality.

### ESPLE-S042

A Taxonomy of Variability Realization Techniques. Mikael Svahnberg; Jilles van Gurp; Jan Bosch. **Date:** 2005. **Version/edition:** Software: Practice and Experience 35(8), pp. 705–754; DOI 10.1002/spe.652. **Access:** ABSTRACT_ONLY on 2026-09-06.

Locator: https://www.researchgate.net/publication/2589218_A_Taxonomy_of_Variability_Realization_Techniques

- `ESPLE-S042-L01` — Original-work abstract and metadata at top of author-work page: Variability implementation is governed by multiple factors, not only postponing decisions.

Limits: Author-hosted PDF failed twice; no taxonomy details inferred from later citing snippets. Detailed realisation comparisons in this packet instead use inspected FOSD, delta, FAST and Bosch sources.

### ESPLE-S043

Dynamic Software Product Lines. Svein Hallsteinsen; Mike Hinchey; Sooyong Park; Klaus Schmid. **Date:** 2008. **Version/edition:** Computer 41(4), pp. 93–95; DOI 10.1109/MC.2008.123. **Access:** ABSTRACT_ONLY on 2026-09-06.

Locator: https://www.researchgate.net/publication/2962230_Dynamic_Software_Product_Lines

- `ESPLE-S043-L01` — Original-work abstract and bibliographic record: Runtime binding is central to DSPL; mixed static and dynamic binding remains viable.

Limits: Original full text not exposed; operational reconstruction relies on separate full Bencomo and Thuijsman/Reniers texts. Host shows May; volume 41(4) corresponds to April issue; year is unambiguous.

### ESPLE-S044

Community-driven variability: characterizing a new software variability paradigm. Roman Bögli; Alexander Boll; Alexander Schultheiß; Timo Kehrer. **Date:** 2026-03-21. **Version/edition:** Automated Software Engineering 33, article 67; DOI 10.1007/s10515-026-00594-0. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://link.springer.com/article/10.1007/s10515-026-00594-0

- `ESPLE-S044-L01` — Sections 1, 3 and 4: Proposal catalogues, independent implementations, interoperability and autonomous evolution differ from a centrally managed product-production system.
- `ESPLE-S044-L02` — Section 5 and closing research vision: Fourteen selected ecosystems classified; feature-oriented techniques proposed without enforcing SPLE processes.

Limits: Taxonomic classification and illustrative ecosystem evidence, not causal proof of economic superiority. De-facto agreement uses proxies and researcher judgement; underlying source dates differ from 2026 publication. 2025 precursor belongs to the same programme, not independent replication.

### ESPLE-S045

Small Yet Configurable: Unveiling Null Variability in Software. Xhevahire Tërnava; Georges Aaron Randrianaina; Luc Lesoil; Mathieu Acher. **Date:** 2026-04-17. **Version/edition:** arXiv 2604.15957 v1; author site mentions a 2025 precursor not separately inspected. **Access:** FULL_TEXT_TARGETED_INSPECTION on 2026-09-06.

Locator: https://arxiv.org/html/2604.15957v1

- `ESPLE-S045-L01` — Sections 4 and 8: Coreutils 9.1, 108 programs, historical subset of 20 programs across 85 releases; option counting excludes external-library/build-script variability.
- `ESPLE-S045-L02` — Sections 5.4 and 7.2–7.3: Removing or earlier binding options; proposed null variability; behavioural-consistency wording qualified by non-identical outputs.

Limits: Within-program/codebase correlations do not identify causal maintainability gains. Ordinary inputs and environmental effects must not be collapsed into configurable features. Our objection concerns inferring environment independence from early feature binding, not the existence of useful fixed-function programs.

