# EVOLVED_SYSTEMS_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE

**Research state:** `FROZEN`  
**Purpose:** source-grounded public explanation without repository mapping  
**Source key:** `EVOLVED_SYSTEMS_ENGINEERING_SOURCE_TABLE.json`

## Source-grounded explanation

Systems engineering emerged through several interacting lineages rather than one invented method: large telecommunications and industrial systems; wartime and post-war systems analysis; missile, aerospace and space programme engineering; defence technical management; requirements, architecture, interface/configuration and V&V specialisms; concurrent engineering; systems-of-systems; formal/model-based work; and later digital, agile and mission-engineering translations. Early texts were already concerned with objectives, alternatives, whole-system consequences and coordinated design—not merely with writing requirements. Standards subsequently created shared lifecycle/process interfaces, but current ISO/IEC/IEEE guidance explicitly allows iterative, concurrent and recursive use rather than prescribing a universal waterfall.

After stripping branding and artefact ritual, the strongest surviving form is a conditional lifecycle coherence discipline. It keeps authoritative stakeholder intent, requirements, assumptions, architecture decisions, interfaces, configuration and evidence mutually consistent while the system changes; explores alternatives before irreversible commitment; integrates risky boundaries early; distinguishes specified conformance from intended-use fitness; and scales modelling, traceability, review and V&V to consequence, coupling, uncertainty, distribution, irreversibility and evidence fragility. Documents, boards, SysML, digital threads and twins are optional implementations whose value depends on a live decision or failure-mode consumer.

## Strongest surviving engineering properties

### P001 — Ground stakeholder and mission intent in authoritative, current evidence

- **Mature form:** A living intent model whose authority, recency, conflicts, measures and affected decisions are explicit; revalidate after material change.
- **Trigger:** Multiple stakeholders; costly or irreversible design; regulated/contractual commitments; uncertain mission; long lifecycle; changed operating context.
- **Cheap path:** For a small reversible task with one empowered user and immediate feedback, a dated goal statement plus direct confirmation is enough.
- **Source IDs:** `S003`, `S024`, `S064`, `S085`

### P002 — Separate validated need and problem from proposed solution

- **Mature form:** Maintain an explicit need–solution boundary, with exceptions justified by named authority and revisited when constraints change.
- **Trigger:** Early concept selection; competing technologies; high switching cost; ambiguous requests; procurement language that embeds a product.
- **Cheap path:** Where the mandated implementation is genuinely fixed by law, interoperability or owner authority, record that constraint and skip artificial alternative generation.
- **Source IDs:** `S024`, `S039`, `S063`, `S064`

### P006 — Preserve requirement provenance, authority and rationale

- **Mature form:** Semantic provenance that supports legitimacy and change decisions, not merely backward hyperlinks.
- **Trigger:** Large or long-lived baselines; regulated/contracted work; reused requirements; multiple issuers; frequent change.
- **Cheap path:** For a directly confirmed, low-cost request, source, date and owner may be sufficient.
- **Source IDs:** `S010`, `S062`, `S067`, `S003`

### P010 — Manage assumptions as owned, testable and expiring engineering claims

- **Mature form:** Assumption currentness is a first-class relation separate from ordinary traceability, with explicit falsification and change propagation.
- **Trigger:** Reuse; supplier boundaries; uncertain environment; models/simulation; long lifecycle; autonomous constituents.
- **Cheap path:** For local reversible work, state the one or two assumptions that could overturn the decision and test them directly.
- **Source IDs:** `S064`, `S067`, `S077`, `S017`

### P014 — Record architecture decisions, alternatives and rationale

- **Mature form:** Decision-centred architecture knowledge linked to current implementation and evidence; diagrams are optional views.
- **Trigger:** Long-lived systems; personnel turnover; costly choices; multiple alternatives; reuse/platform decisions.
- **Cheap path:** For a small reversible choice, a concise decision note with the rejected alternative and trigger is sufficient.
- **Source IDs:** `S024`, `S068`, `S070`, `S072`

### P023 — Specify interface semantics, timing, state and failure contracts

- **Mature form:** A current behavioural/semantic contract whose precision is proportionate to risk; documents, schemas, types and tests are interchangeable carriers.
- **Trigger:** Cross-team integration; data exchange; real-time systems; safety/performance coupling; supplier APIs.
- **Cheap path:** For obvious low-risk local interfaces, executable types/tests and one shared example may be enough.
- **Source IDs:** `S003`, `S076`, `S077`, `S078`

### P024 — Verify interface assumptions and currentness

- **Mature form:** Interface assurance couples current semantic agreement, configuration identity and composition evidence.
- **Trigger:** Frequent interface evolution; independent suppliers; reused components; high-consequence interactions.
- **Cheap path:** Stable local interfaces can rely on automated compatibility tests plus change notification.
- **Source IDs:** `S043`, `S044`, `S076`, `S077`

### P026 — Establish authoritative configuration identity and baselines

- **Mature form:** Identity sufficient to answer exactly what was decided, built, integrated, tested, delivered and operated—without mandating frozen documents.
- **Trigger:** Multiple teams/suppliers; releases/builds; physical units; certification; long lifecycle; evidence reuse.
- **Cheap path:** For a small reversible prototype, an immutable build identifier, dependency lock and dated test record may suffice.
- **Source IDs:** `S003`, `S034`, `S035`, `S036`

### P028 — Propagate change impact across technical relationships

- **Mature form:** Evidence-bearing impact analysis that admits uncertainty and feeds implementation, integration and revalidation—not a form approval.
- **Trigger:** High coupling; shared resources; reused assets; safety/performance effects; cross-organisation changes.
- **Cheap path:** For a local isolated change, deterministic dependency analysis plus focused regression is the cheap path.
- **Source IDs:** `S003`, `S080`, `S081`, `S082`

### P029 — Re-establish evidence currentness after change

- **Mature form:** Evidence is a versioned claim with an applicability boundary and refresh rule, not a timeless attachment.
- **Trigger:** Any claim carried across versions; certification; reused analyses/models; operational updates.
- **Cheap path:** No-op or provably irrelevant changes can retain evidence with a concise impact proof.
- **Source IDs:** `S003`, `S017`, `S081`, `S084`

### P032 — Integrate early, incrementally and at risky boundaries

- **Mature form:** Integration cadence proportional to risk and reversibility, with escalating fidelity and truthful limits.
- **Trigger:** Novel interactions; distributed teams; change-prone software; high coupling; long supplier chains.
- **Cheap path:** Where physical integration is destructive or extraordinarily costly, use earlier models/fixtures and fewer evidence-rich physical events.
- **Source IDs:** `S037`, `S042`, `S047`, `S083`

### P036 — Distinguish verification from validation

- **Mature form:** Two explicit assurance questions with distinct evidence and consumers, applied iteratively across levels.
- **Trigger:** Any consequential system; especially where requirements may be wrong, incomplete or stale.
- **Cheap path:** For tiny direct-user work, one feedback event may simultaneously inform both questions, but the two claims remain distinct.
- **Source IDs:** `S003`, `S015`, `S084`, `S085`

### P039 — Validate with real users, operations and mission context

- **Mature form:** Continuous, context-aware validation connected to authoritative need and post-deployment evidence.
- **Trigger:** Human-facing systems; new workflows; mission capability; autonomous/AI systems; complex operations.
- **Cheap path:** For a small direct-user service, observe actual use and incorporate rapid feedback rather than stage a formal validation event.
- **Source IDs:** `S050`, `S085`, `S111`, `S114`

### P044 — Tailor systems-engineering depth to consequence, complexity, uncertainty and reversibility

- **Mature form:** A trigger-based assurance architecture with explicit escalation and de-escalation, not project-size folklore or blanket waivers.
- **Trigger:** Every project; especially heterogeneous portfolios and mixed hardware/software.
- **Cheap path:** Local reversible work should use direct evidence, short records and immediate feedback unless a trigger appears.
- **Source IDs:** `S001`, `S005`, `S009`, `S052`

### P050 — Reuse evidence only within explicit applicability boundaries

- **Mature form:** Evidence reuse as a bounded inference with explicit source identity, delta analysis and authority—not document inheritance.
- **Trigger:** Product families; software updates; supplier reuse; models; digital threads; certification-heavy domains.
- **Cheap path:** Rerun a cheap decisive test rather than writing an elaborate similarity argument.
- **Source IDs:** `S017`, `S044`, `S084`, `S112`

## Common caricatures and ceremonies to reject

- Systems engineering is inherently waterfall.
- A complete requirements set or traceability matrix proves coherence.
- Architecture is a collection of approved diagrams.
- An ICD signature means the interface is solved.
- Verification proves the right system was built, or acceptance proves technical truth.
- More reviews, gates and artefacts automatically create assurance.
- MBSE means moving documents into SysML.
- A digital twin or single source of truth is automatically authoritative and correct.
- More model detail or link count means more engineering value.
- Standards/process compliance proves effectiveness or ROI.

## Important criticisms and limits

- Whole-discipline SE effectiveness evidence is dominated by observational, case and self-report designs; causal property-level evidence is limited.
- Exhaustive upfront requirements can lock in solutions and hide uncertainty or changed needs.
- Traceability helps particular tasks but is costly to maintain and can be semantically false or stale.
- Decomposition can erase cross-cutting interactions and local optimisation can defeat system outcomes.
- Formal interface documents frequently miss semantics, timing, state, units, failure behaviour and version currentness.
- Late integration concentrates composition failures after options and schedule margin have collapsed.
- Review boards can exist without independent challenge, current evidence, authority or follow-through.
- MBSE adoption can increase cost, effort and specialist/tool dependence; measured comparative benefits remain sparse.
- Digital-thread/twin and single-source claims can overstate semantic continuity, fidelity and trust.
- AI-assisted engineering outputs do not inherit stakeholder authority, correctness, provenance or validation.

## Evolution from document/lifecycle-centric representation

The strongest historical evolution is not from documents to one giant model, but from static artefacts toward current, queryable, evidence-bearing relations: needs carry authority and validity; requirements carry provenance and assumptions; architecture carries decisions and rationale; interfaces carry semantic contracts and versions; baselines bind product/model/test/environment identity; evidence carries intended use and limitations; and change invalidates or reconfirms those relations. Model-based and digital environments can lower reconciliation and analysis cost, but only when their semantics, parity, currentness, credibility, interoperability and decision utility are governed.

## Citation-ready factual claims

### C01

- **Claim:** ISO/IEC/IEEE 15288:2023 defines a common system lifecycle-process framework while permitting iterative, concurrent and recursive application; it does not establish one universal waterfall sequence.
- **Epistemic label:** `STANDARD_OR_GUIDANCE_REQUIREMENT`
- **Source IDs:** `S001`

### C02

- **Claim:** Book-length systems-engineering treatments by Goode and Machol (1957) and Hall (1962) already framed large-system design as an integrated problem of objectives, alternatives, analysis and coordinated choice.
- **Epistemic label:** `SOURCE_ESTABLISHED`
- **Source IDs:** `S023`, `S024`

### C03

- **Claim:** Early U.S. defence standards codified systems-engineering management and configuration control, helping create common programme and supplier interfaces but also creating conditions for process/document bureaucracy.
- **Epistemic label:** `HISTORICAL_INFERENCE`
- **Source IDs:** `S033`, `S034`

### C04

- **Claim:** The familiar V/Vee is plural rather than canonical: the Rook software-testing lineage, German V-Modell lineage and Forsberg–Mooz project-cycle Vee are historically non-identical.
- **Epistemic label:** `SOURCE_ESTABLISHED`
- **Source IDs:** `S030`, `S031`, `S032`

### C05

- **Claim:** NASA's current handbook presents systems engineering as iterative and recursive across stakeholder expectations, requirements, design, realization, integration, verification, validation and technical management; it is guidance rather than a universal directive.
- **Epistemic label:** `STANDARD_OR_GUIDANCE_REQUIREMENT`
- **Source IDs:** `S003`

### C06

- **Claim:** The Mars Climate Orbiter loss shows that documented organisational processes do not prevent a unit/semantic interface mismatch from propagating when interface control and checking are ineffective.
- **Epistemic label:** `PROGRAMME_OR_CASE_EVIDENCE`
- **Source IDs:** `S043`

### C07

- **Claim:** A controlled traceability study reported faster and more correct performance on the studied maintenance tasks when maintained traceability was available, but practitioner research documents material cost, tool and collaboration barriers.
- **Epistemic label:** `EMPIRICAL_OR_DOMAIN_FINDING`
- **Source IDs:** `S057`, `S058`

### C08

- **Claim:** A systematic mapping of requirements quality found many proposed quality attributes but comparatively little evidence-backed definition or evaluation, so quality checklists should be treated as aids rather than correctness certificates.
- **Epistemic label:** `EMPIRICAL_OR_DOMAIN_FINDING`
- **Source IDs:** `S059`

### C09

- **Claim:** Architecture standards distinguish architecture description and evaluation; peer-reviewed work separately treats rationale, decision traceability and erosion, supporting architecture as a decision structure rather than a diagram set.
- **Epistemic label:** `SOURCE_INTERPRETATION`
- **Source IDs:** `S011`, `S012`, `S068`, `S071`, `S072`

### C10

- **Claim:** Government cross-programme evidence repeatedly associates earlier acquisition of design, manufacturing and integration knowledge with better programme positioning, while recent acquisition reviews still document slow linear oversight and unmet needs.
- **Epistemic label:** `PROGRAMME_OR_CASE_EVIDENCE`
- **Source IDs:** `S047`, `S048`, `S050`

### C11

- **Claim:** Verification of a specified claim and validation of intended-use fitness are distinct; qualification and acceptance add domain or authority decisions rather than collapsing that distinction.
- **Epistemic label:** `STANDARD_OR_GUIDANCE_REQUIREMENT`
- **Source IDs:** `S003`, `S015`, `S084`, `S085`, `S086`

### C12

- **Claim:** Systems-of-systems engineering becomes materially distinct when constituent systems retain operational and managerial independence and evolve under distributed authority.
- **Epistemic label:** `SOURCE_ESTABLISHED`
- **Source IDs:** `S014`, `S089`, `S090`

### C13

- **Claim:** A 2021 review found that about two-thirds of claimed MBSE benefits were supported only by perceived evidence and only two reviewed papers reported measured benefits; aggregate value evidence was therefore inconclusive.
- **Epistemic label:** `EMPIRICAL_OR_DOMAIN_FINDING`
- **Source IDs:** `S053`

### C14

- **Claim:** Recent MBSE and digital-engineering studies treat adoption as a sociotechnical transformation involving skills, management, usability, collaboration and governance—not a tool installation.
- **Epistemic label:** `EMPIRICAL_OR_DOMAIN_FINDING`
- **Source IDs:** `S055`, `S056`

### C15

- **Claim:** SysML v2 and the Systems Modeling API were formalised in 2025, improving the standards infrastructure for machine-readable modelling without proving that any particular model is correct, current or valuable.
- **Epistemic label:** `STANDARD_OR_GUIDANCE_REQUIREMENT`
- **Source IDs:** `S021`, `S022`

### C16

- **Claim:** Current digital-thread literature reports divergent definitions and architectures; current NIST work on digital twins foregrounds interoperability, provenance, security and trust boundaries.
- **Epistemic label:** `SOURCE_ESTABLISHED`
- **Source IDs:** `S094`, `S095`, `S096`, `S119`

### C17

- **Claim:** Model-based development does not require immediate global consistency among all models; inconsistency can need explicit identification, prioritisation and governed resolution.
- **Epistemic label:** `EMPIRICAL_OR_DOMAIN_FINDING`
- **Source IDs:** `S097`

### C18

- **Claim:** AI-assisted requirements and MBSE research is expanding rapidly, but recent reviews continue to identify early study maturity, hallucination, reproducibility, interpretability and governance limits.
- **Epistemic label:** `CONTESTED`
- **Source IDs:** `S101`, `S103`

## Explicit evidence limits

- Standards and handbooks establish current accepted guidance, terminology and obligations; they do not prove the optimality or causal payoff of a practice.
- Mishap reports establish concrete failure mechanisms in particular programmes, not universal incidence rates.
- GAO programme comparisons support knowledge/evidence principles but confound engineering, acquisition, funding, incentives and industrial-base effects.
- Requirements/traceability evidence is strongest for bounded tasks and software-intensive settings; transfer to every system type is not automatic.
- MBSE and digital-engineering benefit evidence remains case-heavy, self-reported and weakly replicated.
- Systems-of-systems and mission-engineering governance is substantially defence/aerospace shaped and domain-specific.
- Digital-twin authority is use-, model-, data-, configuration-, latency- and security-bounded.
- AI-assisted SE is a rapidly moving frontier; no autonomous authority/correctness claim is supported.
- The frozen 72-property denominator is an analytical synthesis, not a claim that one recognised methodology has exactly 72 canonical principles.

## Claims not to make

- Do not claim that one person, programme, institution or V-model invented systems engineering.
- Do not claim that systems engineering is synonymous with waterfall, stage gates, requirements writing or documentation.
- Do not claim that standards compliance, certification or acceptance establishes system coherence or mission fitness.
- Do not claim that more requirements, trace links, model elements or reviews necessarily reduce risk.
- Do not claim that SysML, MBSE, a digital thread or a digital twin is required for mature systems engineering.
- Do not claim that a single source eliminates semantic conflict or that model currentness implies correctness.
- Do not claim that MBSE/digital engineering has broadly demonstrated ROI across domains.
- Do not claim that verification and validation are interchangeable.
- Do not claim that systems-of-systems engineering is merely ordinary interface management at larger scale.
- Do not claim that AI-generated requirements, architecture or traces are authoritative without human/source/evidence governance.

## Suggested public page outline

- 1. What systems engineering was trying to solve
- 2. A plural historical genealogy
- 3. The anti-waterfall correction
- 4. The surviving coherence loop: intent → requirements → architecture/interfaces → integration → V&V → change
- 5. The 15 strongest surviving properties
- 6. Interfaces, assumptions and configuration as hidden system boundaries
- 7. Verification versus validation
- 8. When formal SE machinery pays off—and the cheap path
- 9. What MBSE and digital engineering genuinely add
- 10. Common ceremonies and claims to reject
- 11. Evidence strength and unresolved research questions
- 12. Durable sources and further reading

## Direct lineage versus convergence and domain translation

| Tradition | Relationship | Established relationship | Boundary | Source IDs |
| --- | --- | --- | --- | --- |
| Early large-system and telecommunications engineering | SYSTEMS_ENGINEERING_NATIVE | Whole-system performance, interfaces and coordinated design are documented precursors/direct lineage. | No single-inventor claim and no assertion that all modern properties came from Bell Labs. | `S023`, `S024`, `S122` |
| Systems analysis and operations research | SYSTEMS_ANALYSIS_IMPORT_OR_ANCESTRY | Problem framing, alternatives, effectiveness and uncertainty influenced early defence SE. | Decision analysis is not the whole lifecycle/technical-coherence discipline. | `S039`, `S040`, `S123` |
| Aerospace, missile and space programme engineering | SYSTEMS_ENGINEERING_NATIVE | Programme-level integration, technical control, configuration, interfaces and V&V materially shaped codified SE. | Acquisition/certification artefacts remain domain-specific. | `S033`, `S041`, `S124`, `S125` |
| Reliability engineering | RELIABILITY_IMPORT_OR_SHARED_ANCESTRY | Reliability measures, redundancy and verification feed system architecture and technical performance. | No independent reliability-property synthesis is imported. | `S003`, `S041` |
| Safety engineering | SAFETY_IMPORT_OR_SHARED_ANCESTRY | High-consequence hazards alter requirements, architecture, independence, V&V and change control. | Safety methods/properties are not adjudicated as an independent lane here. | `S003`, `S016` |
| Human factors / human systems integration | HUMAN_FACTORS_IMPORT_OR_SHARED_ANCESTRY | SE includes allocation across humans/technology and operational validation; NASA has explicit HSI guidance. | No independent cognitive/human-factors synthesis is imported. | `S003`, `S111` |
| Software engineering and agile/DevSecOps | SOFTWARE_ENGINEERING_TRANSLATION | Continuous integration, iterative requirements, automated evidence and rapid feedback reshape lifecycle implementation. | Physical irreversibility and cross-supplier qualification limit direct transfer. | `S009`, `S108`, `S120` |
| Model-based engineering and formal models | MODEL_BASED_GENERALISATION | Formal MBSE, SysML and model credibility translate engineering relations into structured/modelled forms. | A model or language is not automatically authoritative or valuable. | `S027`, `S013`, `S021`, `S053` |
| Digital engineering | DIGITAL_ENGINEERING_TRANSLATION | Lifecycle data continuity, model federation, machine-readable knowledge and digital twins extend model/configuration/traceability concerns. | Current claims are sociotechnical and evidence-limited. | `S019`, `S056`, `S094`, `S096` |
| Mission and capability engineering | DOMAIN_TRANSLATION | Mission threads and capability outcomes generalise beyond one product in defence practice. | Governance and terminology are not universally transferable. | `S114`, `S115` |
| Product-line/platform engineering | CONVERGENT_PROPERTY | Variability, reuse, common architecture and evidence reuse intersect SE configuration and architecture. | Distinct industrial/software lineage; not all product families are SoS. | `S112`, `S113` |
| AI/autonomy engineering | DOMAIN_TRANSLATION | Adaptive behaviour changes assumptions, model credibility, operational validation and continuous evidence needs. | Modern translation rather than direct historical origin; evidence remains immature. | `S101`, `S103`, `S104`, `S105` |

## Current-state and frontier notes

### Frontier 1: Lifecycle standards are explicitly non-prescriptive and increasingly agility-aware.

- **Current state (2026):** ISO/IEC/IEEE 15288:2023 permits iterative, concurrent and recursive process use; 24748-1/-2 were revised in 2024 and planning/agility parts appeared in 2026.
- **Disposition:** STRONGLY_RETAINED framework; no universal lifecycle sequence.
- **Evidence limit:** Standards establish accepted process vocabulary/guidance, not optimality or causal ROI.
- **Property IDs:** P007, P032, P044, P061
- **Source IDs:** `S001`, `S006`, `S007`, `S008`, `S009`

### Frontier 2: SysML v2 and standard modelling APIs.

- **Current state (2026):** OMG formalised SysML v2 and a Systems Modeling API in 2025, strengthening textual/API access and machine-actionable exchange.
- **Disposition:** PROMISING infrastructure.
- **Evidence limit:** Language/API standardisation does not establish model quality, organisational adoption, semantic portability or ROI.
- **Property IDs:** P047, P048
- **Source IDs:** `S021`, `S022`

### Frontier 3: Model credibility and use-bounded validation.

- **Current state (2026):** NASA-STD-7009B (2024) and NASA-HDBK-7009B (2026) formalise credibility assessment for models and simulations.
- **Disposition:** STRONGLY_RETAINED for consequential model use.
- **Evidence limit:** Domain/application tailoring remains necessary; credibility for one use cannot be inherited by another.
- **Property IDs:** P041, P050
- **Source IDs:** `S016`, `S017`

### Frontier 4: MBSE organisational transformation.

- **Current state (2026):** Systematic reviews and organisational studies continue to report communication, consistency and analysis benefits alongside skills, understandability, effort, adoption and governance barriers.
- **Disposition:** CONTEXT_DEPENDENT; fit-for-purpose model use retained, blanket MBSE adoption not retained.
- **Evidence limit:** Measured comparative benefits remain sparse and susceptible to case-selection and self-report bias.
- **Property IDs:** P047, P048, P071
- **Source IDs:** `S053`, `S054`, `S055`, `S056`, `S098`

### Frontier 5: Digital thread and authoritative lifecycle data.

- **Current state (2026):** DoD policy and current research promote connected digital engineering environments and traceable lifecycle data.
- **Disposition:** PROMISING, evidence-limited translation.
- **Evidence limit:** Definitions, measures, semantic interoperability and broad ROI remain immature; integration can reproduce silos.
- **Property IDs:** P029, P030, P048, P049, P060
- **Source IDs:** `S019`, `S020`, `S056`, `S094`, `S100`, `S116`, `S117`

### Frontier 6: Digital twins, interoperability, security and trust.

- **Current state (2026):** NIST programmes and IR 8356 emphasise interoperability, security and trust rather than treating a twin as automatically authoritative.
- **Disposition:** CONTEXT_DEPENDENT and ASSUMPTION_SENSITIVE.
- **Evidence limit:** Fidelity, latency, observability, data provenance and valid-use boundaries dominate transferability.
- **Property IDs:** P041, P049, P050
- **Source IDs:** `S095`, `S096`, `S119`

### Frontier 7: Semantic model federation and inconsistency management.

- **Current state (2026):** Research increasingly treats multiple models, repositories and viewpoints as federated and potentially inconsistent rather than assuming one monolith.
- **Disposition:** RETAINED_IN_EVOLVED_FORM.
- **Evidence limit:** Automated transformations can lose meaning; governance and analyst judgement remain necessary.
- **Property IDs:** P030, P048, P070
- **Source IDs:** `S078`, `S097`, `S098`

### Frontier 8: Continuous and agile systems engineering.

- **Current state (2026):** Current standards and domain guidance accommodate agility, DevSecOps and iterative V&V; hybrid frameworks continue to emerge for hardware/software systems.
- **Disposition:** HYBRIDISED.
- **Evidence limit:** Hardware irreversibility, qualification, supplier boundaries and long-lead items constrain direct software-method transfer.
- **Property IDs:** P007, P032, P044, P059
- **Source IDs:** `S009`, `S108`, `S109`, `S110`, `S120`

### Frontier 9: AI-assisted requirements, architecture and MBSE.

- **Current state (2026):** Systematic reviews and government programmes show rapidly expanding generation, extraction, modelling and assistant use cases.
- **Disposition:** CONTESTED but promising for bounded assistance.
- **Evidence limit:** Authority, hallucination, provenance, data leakage, semantic validation, reproducibility and model drift preclude autonomous truth claims.
- **Property IDs:** P057
- **Source IDs:** `S101`, `S102`, `S103`, `S104`, `S105`

### Frontier 10: AI-enabled and adaptive system V&V.

- **Current state (2026):** Current defence guidance emphasises operationally representative testing, data/model context and continuous assessment for AI-enabled systems.
- **Disposition:** DOMAIN_TRANSLATION of V&V/currentness properties.
- **Evidence limit:** Open-world behaviour and changing data defeat exhaustive pre-deployment proof; runtime monitoring and bounded claims remain necessary.
- **Property IDs:** P004, P010, P035, P039, P041, P043
- **Source IDs:** `S104`

### Frontier 11: Systems-of-systems and mission engineering.

- **Current state (2026):** SoS standards/guides and mission engineering continue to address independent constituents, capability threads and distributed governance.
- **Disposition:** DOMAIN_SPECIFIC but materially distinct.
- **Evidence limit:** Defence-origin governance and terminology do not automatically transfer; authority often remains structurally incomplete.
- **Property IDs:** P045, P046, P056
- **Source IDs:** `S014`, `S089`, `S090`, `S091`, `S114`, `S115`

### Frontier 12: Property-level measures and digital-engineering ROI.

- **Current state (2026):** Research programmes are developing measures; isolated studies report benefits in particular sustainment contexts.
- **Disposition:** STILL_CONTESTED.
- **Evidence limit:** Few replicated, prospective, comparative studies separate engineering properties from organisational maturity and programme selection.
- **Property IDs:** P005, P044, P047, P072
- **Source IDs:** `S051`, `S052`, `S053`, `S100`, `S116`, `S117`

### Frontier 13: Product lines, platforms and evidence reuse.

- **Current state (2026):** Industrial work supports reuse/variability methods, while testing and commonality create distinct configuration and common-mode risks.
- **Disposition:** CONTEXT_DEPENDENT.
- **Evidence limit:** Transfer depends on stable variation points, product identity and applicability-bounded evidence.
- **Property IDs:** P016, P050, P055
- **Source IDs:** `S112`, `S113`

### Frontier 14: Acquisition reform and evidence speed.

- **Current state (2026):** GAO's June 2026 review reports persistent slow, linear oversight and argues for knowledge/leading-practice reform rather than simple process accumulation.
- **Disposition:** CRITIQUE OF ORGANISATIONAL IMPLEMENTATION.
- **Evidence limit:** Acquisition outcomes conflate governance, funding, industrial base, incentives and engineering; they cannot isolate one SE mechanism.
- **Property IDs:** P019, P032, P044, P052, P058, P072
- **Source IDs:** `S047`, `S048`, `S049`, `S050`

## Public explanation boundary

This intake may support public documentation of the external research corpus. It must not be used to imply that a target implementation owns, lacks or should adopt any property. It must preserve the distinction between current guidance, historical provenance, empirical evidence, case evidence and contested frontier claims.
