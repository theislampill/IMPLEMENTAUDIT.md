# CSS-L3 — Systems Safety

> **Current scientific reading route — 13 November 2026:** the substantial [CSS-L3 account](current/CSS-L3.md) and [full scientific readers](current/README.md) now provide the normalized current interpretation. Disclosure and withholding statements in the retained record below describe its earlier cutoff; immutable programme and increment records remain historical.


[Family](README.md) · [Genealogy](GENEALOGY.md) · [Synthesis](CSS-S.md) · [Rough work outlines](RLGWO_OUTLINES.md) · [Completeness](COMPLETENESS.md)

## Two evidence layers

This reader explains the **68-property historical public corpus**. The separately qualified current CSS-L3 subject has **68 selected property identities**. The original history and dispositions below remain attached to the historical source; they are not relabelled as the corrected study or as current implementation acceptance. [Current identities and exact review pins](../../PROGRAMME.json) · [Original family overview](../css.md).

The corrected current study and its accepted reviews are documented in the private family interpretation. Detailed current scientific publication awaits a source-specific disclosure decision. The public reader does not fill that gap with historical text. The [component assessment](COMPLETENESS.md) keeps those limits explicit.

## Explanation from the public predecessor

### What the public predecessor supports

Systems Safety begins with a bounded unacceptable loss and the hazardous system state that could lead to it. ESS-002 distinguishes that state from a failed component; ESS-003 requires a feasible, allocated and assessable constraint. The underlying concern may be unsafe intended interaction, timing or feedback. A failure label is not a prerequisite for analysing it, and completing an analysis is not evidence that the constraint is enforced. [Safety ledger, ESS-001–ESS-003 and ESS-008–ESS-012][h-ledger]

**Illustrative case: stopping without confirmed containment.** A control can acknowledge a stop while the downstream process remains active or its state cannot be observed. ESS-035 requires the containment objective, timing, actuation and feedback appropriate to the consequence. ESS-037 requires restored constraints and observability before recovery or restart. In a simple local reversible case, direct stop and immediate observation can be enough; the corpus does not require emergency-control machinery where there is no credible propagation path. [Safety ledger, ESS-035 and ESS-037][h-ledger]

Stopping and continuing can each be hazardous in some settings. ESS-036 therefore treats degraded operation as a bounded design question: the actual loss/mission relation, mode, time limit, authority, feedback and recovery path matter. “Keep running” is not an alternative that becomes acceptable merely because a stop is inconvenient. Equally, “always stop” is not a complete safety theory. ESS-020 scales the control to consequence, reversibility, coupling, latency and recovery difficulty. [Safety ledger, ESS-020 and ESS-036][h-ledger]

Configuration-bound assurance is another distinct requirement. Evidence for one interface, assumption or operating state may not support a changed one. ESS-028/029/051 retain identity, impact and assumption validity. ESS-013/014/025 ask whether different channels or reviewers share causes and information. More channels, documents or signatures can add cost without protecting the failure direction at issue. [Safety ledger][h-ledger]

### Relationship to IMPLEMENTAUDIT

R002C/#196 is still open. Its public terminal census preserves accepted property/source/helper accounting while identifying a missing exact-final ordinary installed-activation receipt. The active continuation records later bounded source and local-task results, together with an original case B diagnostic gap and a readiness NONVERDICT. Those observations should be retained at their actual scopes; they neither erase the accepted source work nor close the whole original safety contract. [R002C terminal census][196-census] · [Exact active source continuation][active-safety]

The current public planning owner requires target state, feedback, containment and recovery for high consequence, rejects nominal override, and retains a cheap path for local reversible work with direct readback. Its deterministic cases classify declared conditions; they do not demonstrate production safety, authentic effect isolation or current installed behaviour by themselves. The existing owner and original acceptance remain the route for those questions. [Native planning source][planning-source] · [Four rough outlines](RLGWO_OUTLINES.md#css-l3--systems-safety)

## Historical property reader

Every one of the 68 rows is represented below, including rejected, contextual and unresolved dispositions. Wording under the labelled fields is transcribed from the public ledger. The evidence profile is the corpus author’s assessment at that freeze, not a new evidence review. Packet-local source identities resolve through the [source table](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json). The [machine-readable map](PUBLIC_PROPERTY_SOURCE_MAP.json) binds each entry to its exact ledger field and rendered anchor.

The full ledger retains additional structured profiles and source context: [immutable ledger](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json).

[ESS-001](#ess-001) · [ESS-002](#ess-002) · [ESS-003](#ess-003) · [ESS-004](#ess-004) · [ESS-005](#ess-005) · [ESS-006](#ess-006) · [ESS-007](#ess-007) · [ESS-008](#ess-008) · [ESS-009](#ess-009) · [ESS-010](#ess-010) · [ESS-011](#ess-011) · [ESS-012](#ess-012) · [ESS-013](#ess-013) · [ESS-014](#ess-014) · [ESS-015](#ess-015) · [ESS-016](#ess-016) · [ESS-017](#ess-017) · [ESS-018](#ess-018) · [ESS-019](#ess-019) · [ESS-020](#ess-020) · [ESS-021](#ess-021) · [ESS-022](#ess-022) · [ESS-023](#ess-023) · [ESS-024](#ess-024) · [ESS-025](#ess-025) · [ESS-026](#ess-026) · [ESS-027](#ess-027) · [ESS-028](#ess-028) · [ESS-029](#ess-029) · [ESS-030](#ess-030) · [ESS-031](#ess-031) · [ESS-032](#ess-032) · [ESS-033](#ess-033) · [ESS-034](#ess-034) · [ESS-035](#ess-035) · [ESS-036](#ess-036) · [ESS-037](#ess-037) · [ESS-038](#ess-038) · [ESS-039](#ess-039) · [ESS-040](#ess-040) · [ESS-041](#ess-041) · [ESS-042](#ess-042) · [ESS-043](#ess-043) · [ESS-044](#ess-044) · [ESS-045](#ess-045) · [ESS-046](#ess-046) · [ESS-047](#ess-047) · [ESS-048](#ess-048) · [ESS-049](#ess-049) · [ESS-050](#ess-050) · [ESS-051](#ess-051) · [ESS-052](#ess-052) · [ESS-053](#ess-053) · [ESS-054](#ess-054) · [ESS-055](#ess-055) · [ESS-056](#ess-056) · [ESS-057](#ess-057) · [ESS-058](#ess-058) · [ESS-059](#ess-059) · [ESS-060](#ess-060) · [ESS-061](#ess-061) · [ESS-062](#ess-062) · [ESS-063](#ess-063) · [ESS-064](#ess-064) · [ESS-065](#ess-065) · [ESS-066](#ess-066) · [ESS-067](#ess-067) · [ESS-068](#ess-068)

<a id="ess-001"></a>
### ESS-001 — Explicit unacceptable-loss framing

**Historical origin:** Military/aerospace system safety; later STPA made losses an explicit first step.

**Original form:** Define mishaps/accidents and unacceptable consequences before selecting hazards and controls.

**Development:** Evolved from accident categories to stakeholder-explicit loss models linked to hazards, constraints and acceptance authority.

**Evolved form in this historical corpus:** A concise, current, decision-linked definition of unacceptable loss that bounds later analysis without pretending completeness.

**Problem:** Safety work can optimise compliance or component metrics without knowing what outcome must be prevented.

**Mechanism:** Name losses, affected stakeholders and decision authority; derive hazardous system states and constraints from them.

**Trigger and context:** Any consequential system, material change, novel operation or unresolved safety decision.

**Preconditions:** Stakeholders and authority must be known; loss statements must be specific enough to discriminate decisions.

**Authority and control preconditions:** A competent owner must be authorised to define tolerability and resolve conflicts among safety, mission and availability.

**Required feedback:** Evidence that the loss set still matches current use, users, environment and public exposure.

**Decision or consumer:** Design authority, operator, regulator or risk-acceptance authority.

**Nontrigger or cheaper adequate path:** For trivial reversible work, state the bounded loss in one line and use the authoritative deterministic check; no elaborate taxonomy.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Losses framed too broadly become slogans; too narrowly omit public/mission harms; economic inconvenience can be mislabelled as safety.

**Criticism:** Different domains define accident, mishap and harm differently; not every adverse outcome is a safety loss.

**Contrary evidence:** No source establishes one universal loss vocabulary or acceptable threshold.

**Unresolved questions:** How should distributional, long-latency and intergenerational harms be represented without making every objective a safety loss?

**Property versus ceremony:** The property is the decision boundary; a “loss list” document or STPA worksheet is optional.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: MODERATE — mechanism is coherent but depends on model scope and assumptions.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S014, S015, S018, S033; critical/contrary: S038, S066.

**Primary source identities:** S012; S014; S015; S018; S033

**Critical source identities:** S038; S066

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/0`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-002"></a>
### ESS-002 — Hazardous system-state framing distinct from failure

**Historical origin:** Direct system safety and process safety; sharpened by STAMP/STPA and SOTIF.

**Original form:** Identify a system condition that, with a particular environment or set of conditions, can lead to loss.

**Development:** Evolved from hardware-energy and failure hazards to system-state, interaction, intended-function and sociotechnical hazards.

**Evolved form in this historical corpus:** A current loss-linked hazardous-state model with explicit boundary, exposure and causal assumptions.

**Problem:** Teams equate hazards with failed parts and therefore miss unsafe nominal behaviour, exposure and interaction.

**Mechanism:** Model hazards separately from causes; then search failures, interactions, environmental conditions and control flaws that can create them.

**Trigger and context:** Systems with software, humans, adaptive functions, hazardous energy/material, changing environments or nontrivial interfaces.

**Preconditions:** A defined system boundary, environment and loss relation; hazards must be controllable enough to inform design or operation.

**Authority and control preconditions:** Ownership of system boundary and authority to impose constraints across components/interfaces.

**Required feedback:** Observable indicators of hazardous state, exposure and boundary conditions—not only component health.

**Decision or consumer:** System architect, safety engineer, operations authority and design teams.

**Nontrigger or cheaper adequate path:** A simple local task with a complete deterministic invariant may use that invariant directly rather than a separate hazard ontology.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Hazards become vague nouns, duplicate losses, or are listed without a consumer/control.

**Criticism:** Hazard definitions differ across MIL-STD-882, IEC/ISO, process safety and STPA; terminology should not be forced.

**Contrary evidence:** No practical method can prove that all hazards have been identified in an open sociotechnical system.

**Unresolved questions:** What evidence is sufficient to bound a hazard search in adaptive or open-world systems?

**Property versus ceremony:** The property is the loss-capable state model; exact hazard-log columns are not required.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: MODERATE — mechanism is coherent but depends on model scope and assumptions.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S014, S015, S018, S025, S033; critical/contrary: S017, S109.

**Primary source identities:** S012; S014; S015; S018; S025; S033

**Critical source identities:** S017; S109

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/1`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-003"></a>
### ESS-003 — Enforceable safety constraints

**Historical origin:** System-safety requirements and design-control traditions; explicit constraint concept in STAMP/STPA.

**Original form:** Translate hazards into requirements, prohibitions, limits and control obligations.

**Development:** Evolved from safety requirements to allocated control constraints with runtime observability, change impact and recovery semantics.

**Evolved form in this historical corpus:** The minimum sufficient constraint is explicit, allocated, enforceable, verified and paired with feedback or bounded assurance.

**Problem:** Hazards are identified but no enforceable design/operational condition prevents or limits them.

**Mechanism:** Derive constraints from hazards; allocate them to controllers/components/procedures; verify implementation and operational enforcement.

**Trigger and context:** Whenever a credible hazard remains after elimination or redesign.

**Preconditions:** Constraint must be testable or otherwise assessable and tied to a controller with feasible authority.

**Authority and control preconditions:** The allocated controller must possess real control authority and resources; responsibility without authority is insufficient.

**Required feedback:** State/feedback showing the constraint is maintained and alarms when it is violated or unverifiable.

**Decision or consumer:** Design authority, controller owner, verifier, operator and acceptance authority.

**Nontrigger or cheaper adequate path:** Where a deterministic existing rule already proves the safe condition, record/reuse it rather than create duplicate safety requirements.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Vague “shall be safe” statements, contradictory constraints, unenforceable human instructions, and unmonitored assumptions.

**Criticism:** Constraint language can become model bureaucracy; not all safety behaviour is reducible to static rules.

**Contrary evidence:** Constraint satisfaction cannot prove safety if the hazard model or environment assumptions are wrong.

**Unresolved questions:** How should adaptive controllers revise constraints without invalidating their assurance basis?

**Property versus ceremony:** A requirements database is optional; live allocation and enforcement are the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S015, S018, S029, S100; critical/contrary: S048, S066.

**Primary source identities:** S012; S015; S018; S029; S100

**Critical source identities:** S048; S066

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/2`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-004"></a>
### ESS-004 — Lifecycle hazard identification with explicit completeness boundaries

**Historical origin:** Military/aerospace programme safety, process hazard analysis and medical-device lifecycle risk management.

**Original form:** Perform preliminary, system, subsystem, operating/support and change hazard analysis across lifecycle phases.

**Development:** Evolved from fixed phase analyses to bounded, trigger-driven, multi-method lifecycle searches with explicit residual uncertainty.

**Evolved form in this historical corpus:** Claim bounded coverage over a declared population; never claim that all possible hazards are known.

**Problem:** Hazards introduced in manufacture, operation, maintenance, disposal or changed environment are omitted from design-only analysis.

**Mechanism:** Define search scope, phases, methods, expertise, exclusions, assumptions and residual unknowns; revisit on triggers.

**Trigger and context:** Novel/high-consequence systems; phase transitions; operational change; significant incidents; emerging evidence.

**Preconditions:** Access to lifecycle knowledge and representative operators/maintainers; explicit stopping/saturation criteria.

**Authority and control preconditions:** A named owner must decide when coverage is sufficient and when reopening is required.

**Required feedback:** Coverage ledger, unresolved assumptions, operational signals and change triggers.

**Decision or consumer:** Safety manager, system owner, change authority and risk acceptor.

**Nontrigger or cheaper adequate path:** Low-consequence reversible work needs only a bounded check of known hazards and the deterministic discriminator, not a comprehensive workshop.

**Disposition at the historical freeze:** USEFUL_BUT_EASILY_BUREAUCRATISED

**Failure modes:** Checklist completion, duplicate analyses, expertise gaps, search stopping by schedule, and stale hazard logs.

**Criticism:** True completeness is unprovable for open systems; exhaustive process can consume effort without changing design.

**Contrary evidence:** No comparative evidence establishes a universal optimal analysis depth or meeting format.

**Unresolved questions:** What stopping rules best balance unknown-hazard discovery against analysis cost for continuously changing systems?

**Property versus ceremony:** The property is coverage and reopening discipline; a prescribed list of analysis reports is domain-specific.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: MODERATE — mechanism is coherent but depends on model scope and assumptions.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S014, S015, S027, S094; critical/contrary: S038, S048, S109.

**Primary source identities:** S012; S014; S015; S027; S094

**Critical source identities:** S038; S048; S109

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/3`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-005"></a>
### ESS-005 — Component failure-effects analysis as a bounded complement

**Historical origin:** MIL-P-1629/FMECA reliability ancestry, later generalised in IEC 60812.

**Original form:** Enumerate item/function failure modes and trace local and system effects, causes, detection and treatment.

**Development:** Evolved from exhaustive hardware tables to function/interface-focused, risk-significant analyses combined with top-down and interaction methods.

**Evolved form in this historical corpus:** Use FMEA for what it represents well; do not treat a completed FMEA as a complete system-safety analysis.

**Problem:** Single-point or component-level failure mechanisms remain undiscovered until integration or operation.

**Mechanism:** Perform function/item-based FMEA/FMECA focused on safety-significant elements and feed results into system hazard/control analysis.

**Trigger and context:** Hardware/component/process failure modes are material and interfaces are sufficiently defined.

**Preconditions:** Defined functions/boundaries, knowledgeable participants and connection to system consequences and controls.

**Authority and control preconditions:** Owners must be able to change design, detection, maintenance or architecture based on findings.

**Required feedback:** Failure detection coverage, field failures, common-cause data and control effectiveness.

**Decision or consumer:** Component designer, system safety analyst, reliability engineer and verifier.

**Nontrigger or cheaper adequate path:** Skip a full worksheet where the component is non-safety-significant, trivially replaceable, or a validated deterministic test already exhausts the relevant failure set.

**Disposition at the historical freeze:** CONTEXT_DEPENDENT

**Failure modes:** Mechanical worksheet completion, arbitrary ranking, omission of interactions/software/operational context and stale failure libraries.

**Criticism:** Bottom-up FMEA can miss unsafe interactions without component failure and is often undermined by weak occurrence data.

**Contrary evidence:** Comparative evidence that FMEA improves safety outcomes is limited and confounded by implementation quality.

**Unresolved questions:** How can automated model-based FMEA preserve expert challenge rather than scale stale assumptions?

**Property versus ceremony:** The property is structured failure search and effect propagation; the worksheet and RPN are not general requirements.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_WITHIN_REPRESENTED_CLASS — technique semantics are established; completeness outside its representation is not.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: CONTEXT_DEPENDENT — transfer requires matching the technique to the causal/hazard class.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S005, S006, S007, S012; critical/contrary: S019, S036, S109.

**Primary source identities:** S005; S006; S007; S012

**Critical source identities:** S019; S036; S109

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/4`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-006"></a>
### ESS-006 — Top-down causal-path and logical analysis

**Historical origin:** Fault-tree analysis from Minuteman launch-control safety; event-tree/PRA expansion in aerospace and nuclear safety.

**Original form:** Start from an undesired top event and decompose necessary/sufficient combinations; model consequence branches after initiators.

**Development:** Evolved into qualitative/quantitative hybrid analysis with explicit uncertainty, common-cause models and combination with interaction methods.

**Evolved form in this historical corpus:** Use top-down logic where the event structure is meaningful; pair it with other searches for unmodelled interactions and organisational causes.

**Problem:** Critical combinations, cut sets, dependencies or escalation paths are not visible in bottom-up lists.

**Mechanism:** Construct qualitative logic first; quantify only with defensible data/dependence models; use event trees for post-initiator progression.

**Trigger and context:** A well-defined top event, architecture and causal logic; quantitative use requires data and dependence modelling.

**Preconditions:** Stable boundary, meaningful decomposition and explicit common-cause/uncertainty assumptions.

**Authority and control preconditions:** Decision owner can act on dominant cut sets, barriers or design alternatives.

**Required feedback:** Configuration currentness, event definitions, dependency/common-cause evidence and operational data.

**Decision or consumer:** System safety/PRA analyst, architect, operations and risk authority.

**Nontrigger or cheaper adequate path:** For a simple deterministic invariant, use direct proof/test; do not construct a tree that merely restates the invariant.

**Disposition at the historical freeze:** CONTEXT_DEPENDENT

**Failure modes:** Omitted events, false independence, boundary truncation, unjustified probabilities and treating tree completeness as world completeness.

**Criticism:** Trees represent only modelled causes and may omit organisational/software interactions and adaptive behaviour.

**Contrary evidence:** Sparse catastrophic data and unknown interactions limit quantitative calibration.

**Unresolved questions:** How should causal models represent adaptive software and organisational decisions without becoming unmaintainable?

**Property versus ceremony:** The property is transparent causal decomposition; gate symbols and large diagrams are optional.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_WITHIN_REPRESENTED_CLASS — technique semantics are established; completeness outside its representation is not.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: CONTEXT_DEPENDENT — transfer requires matching the technique to the causal/hazard class.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S008, S009, S040, S041, S096; critical/contrary: S017, S038, S109.

**Primary source identities:** S008; S009; S040; S041; S096

**Critical source identities:** S017; S038; S109

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/5`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-007"></a>
### ESS-007 — Structured process-deviation search

**Historical origin:** ICI process safety, HAZOP development from 1963; later IEC 61882.

**Original form:** Apply guidewords to design intent and process parameters in a multidisciplinary review to find deviations, causes, consequences and safeguards.

**Development:** Evolved into proportionate, procedure/software/change HAZOP variants integrated with barrier and risk analysis.

**Evolved form in this historical corpus:** Structured deviation prompts plus empowered expertise and action closure; method depth proportional to hazard and change.

**Problem:** Credible hazardous deviations and operability problems are missed because reviewers follow normal-flow narratives.

**Mechanism:** Use guidewords or equivalent structured prompts at nodes/functions; record decisions, actions and unresolved assumptions.

**Trigger and context:** Hazardous processes, complex flows/procedures or modifications where deviation search has decision value.

**Preconditions:** Accurate design intent, competent multidisciplinary team, bounded nodes and action follow-through.

**Authority and control preconditions:** Facilitator/review team must be able to obtain design changes or escalate unresolved hazards.

**Required feedback:** Action completion, safeguard state, deviations/near misses and change currentness.

**Decision or consumer:** Process design authority, operations, maintenance and hazard owner.

**Nontrigger or cheaper adequate path:** Do not convene a full HAZOP for a tiny reversible change with a complete change discriminator; use focused review.

**Disposition at the historical freeze:** CONTEXT_DEPENDENT

**Failure modes:** Guideword ritual, excessive scope, fatigue, repeated low-value findings and action lists without closure.

**Criticism:** Conventional HAZOP does not by itself estimate likelihood or establish complete causal coverage.

**Contrary evidence:** No evidence supports HAZOP as a universal method outside matching process/deviation problems.

**Unresolved questions:** What automated assistance improves coverage without anchoring teams to generated but shallow deviations?

**Property versus ceremony:** The property is disciplined deviation search; exact guideword tables and workshop duration are not universal.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_WITHIN_REPRESENTED_CLASS — technique semantics are established; completeness outside its representation is not.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: CONTEXT_DEPENDENT — transfer requires matching the technique to the causal/hazard class.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S010, S011, S094, S095; critical/contrary: S038, S066.

**Primary source identities:** S010; S011; S094; S095

**Critical source identities:** S038; S066

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/6`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-008"></a>
### ESS-008 — Unsafe interaction and unsafe-control analysis

**Historical origin:** General system-safety interaction reasoning; control-theoretic reformulation in STAMP/STPA; convergent evidence in SOTIF and accident analysis.

**Original form:** Search for system-level hazardous interactions and control actions that are missing, provided, mistimed, misordered, too long or too short.

**Development:** Evolved toward hybrid analyses that combine failure, interaction, scenario and formal verification around the actual hazard class.

**Evolved form in this historical corpus:** Explicitly reason about unsafe composition and control context, using the cheapest adequate representation and complementary techniques.

**Problem:** Locally correct or nonfailed components, software, humans and organisations compose into a hazardous state.

**Mechanism:** Model controllers, controlled processes, actions, context and feedback; identify unsafe combinations and causal scenarios.

**Trigger and context:** Software-intensive, autonomous, tightly coupled, multi-controller or human-automation systems.

**Preconditions:** A usable control/interaction model, representative operational knowledge and explicit system boundary.

**Authority and control preconditions:** Controllers must have clear authority and conflict-resolution rules; analysis findings need a design/operations consumer.

**Required feedback:** Actual action timing/order/duration, process state, controller modes, feedback quality and handoffs.

**Decision or consumer:** System architect, software/control designer, human factors, operations and safety authority.

**Nontrigger or cheaper adequate path:** Where a simple component failure fully determines the hazard, use the cheaper failure analysis and direct control; do not force a control diagram.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Subjective models, analyst-dependent results, diagram growth, unvalidated completeness and failure to connect scenarios to controls.

**Criticism:** STPA is not uniquely entitled to interaction reasoning; other system safety, SOTIF, HAZOP and scenario methods can contribute.

**Contrary evidence:** Comparative evidence does not establish STPA as universally more effective or scalable than all alternatives.

**Unresolved questions:** Which interaction-analysis combinations provide reproducible coverage for adaptive AI-enabled systems?

**Property versus ceremony:** The property is interaction/control reasoning; STPA terminology and diagrams are optional.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S014, S017, S018, S020, S025, S109; critical/contrary: S019, S020, S109.

**Primary source identities:** S014; S017; S018; S020; S025; S109

**Critical source identities:** S019; S020; S109

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/7`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-009"></a>
### ESS-009 — Closed-loop control and feedback integrity

**Historical origin:** Control engineering imported into system safety; explicit in STAMP/STPA and protection-system practice.

**Original form:** Treat safety as maintaining constraints through controllers, actions, controlled processes and feedback.

**Development:** Evolved from simple interlocks to integrity-monitored, time-aware feedback with explicit unobservable/degraded-state behaviour.

**Evolved form in this historical corpus:** Every consequential control has evidence sufficient to establish intended state, or the system treats state as unknown and constrains operation.

**Problem:** A command is assumed to equal achieved state, or feedback is absent, stale, wrong or semantically insufficient.

**Mechanism:** Specify required state feedback, freshness, validity and independent confirmation; design fallback for unobservable state.

**Trigger and context:** Consequential control actions, remote/autonomous actuation, interlocks, shutdown, recovery and distributed control.

**Preconditions:** Sensor/feedback path coverage, semantics and timing must match the safety decision.

**Authority and control preconditions:** Controller must be authorised to act on missing/invalid feedback and to enter a safe/degraded mode.

**Required feedback:** State-based confirmation, feedback freshness/integrity, actuator/process health and observability gaps.

**Decision or consumer:** Controller, operator, safety monitor and restart authority.

**Nontrigger or cheaper adequate path:** For local directly observable reversible actions, immediate observation/test can serve as the feedback path without additional instrumentation.

**Disposition at the historical freeze:** CONTROL_LOOP_PROPERTY

**Failure modes:** Common-mode sensor errors, feedback derived from the command rather than process, alarm flooding and unhandled uncertainty.

**Criticism:** Additional sensors can share failure modes; feedback can create complexity or false confidence.

**Contrary evidence:** No feedback architecture eliminates epistemic uncertainty or common-mode failure.

**Unresolved questions:** How should systems express and govern “unknown safety state” without causing unsafe service loss?

**Property versus ceremony:** The property is state confirmation and bounded response; a particular control diagram is not required.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S018, S051, S058, S089, S101; critical/contrary: S050, S074.

**Primary source identities:** S018; S051; S058; S089; S101

**Critical source identities:** S050; S074

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/8`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-010"></a>
### ESS-010 — Controller process-model and mode consistency

**Historical origin:** Human factors mode-awareness work and STAMP/STPA process-model concept.

**Original form:** Ensure the controller’s model of process state, mode, environment and control authority matches reality sufficiently for safe action.

**Development:** Evolved toward explicit state/mode contracts, confidence/uncertainty handling and transition verification.

**Evolved form in this historical corpus:** Make safety-relevant process-model assumptions visible, monitored and fail-bounded.

**Problem:** Operator, automation or organisation acts rationally on a stale, incomplete or wrong model.

**Mechanism:** Expose modes and assumptions; reconcile state estimates; detect divergence; design transitions and fallback behaviour.

**Trigger and context:** Mode-rich automation, distributed systems, remote operation, delayed observability or adaptive functions.

**Preconditions:** Model variables must be linked to observable state and updated at a rate adequate to the hazard dynamics.

**Authority and control preconditions:** Controller must be able to refuse action or escalate when model confidence is insufficient.

**Required feedback:** Current mode/state, transition completion, environment, authority and model-confidence indicators.

**Decision or consumer:** Automation designer, interface/human-factors engineer, operator and controller owner.

**Nontrigger or cheaper adequate path:** A stateless local action with directly visible conditions may require only a simple precondition check.

**Disposition at the historical freeze:** CONTROL_LOOP_PROPERTY

**Failure modes:** Hidden modes, inconsistent displays, stale caches, unverifiable AI state and overloading operators with mode detail.

**Criticism:** Perfect model agreement is impossible; excessive transparency can increase workload.

**Contrary evidence:** Adaptive and learned systems can make internal state difficult to interpret or validate.

**Unresolved questions:** What minimum external state representation is sufficient for safe oversight of opaque adaptive controllers?

**Property versus ceremony:** The property is model-state consistency; a STPA “process model” box is optional.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S018, S063, S064, S088, S089, S106; critical/contrary: S074, S109.

**Primary source identities:** S018; S063; S064; S088; S089; S106

**Critical source identities:** S074; S109

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/9`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-011"></a>
### ESS-011 — Timing, ordering, duration and transition semantics

**Historical origin:** Real-time control/system safety; explicit unsafe-control-action classes in STPA.

**Original form:** Analyse not only whether an action occurs but when, in what order, for how long and during which transition.

**Development:** Evolved into explicit transition-state assurance, runtime monitors and targeted temporal formal methods.

**Evolved form in this historical corpus:** Apply temporal rigour where timing can change safety; use direct atomic checks where it cannot.

**Problem:** Correct commands become unsafe because of latency, reordering, repetition, premature stop or excessive duration.

**Mechanism:** Specify temporal constraints, transition guards, timeouts, idempotence/repetition bounds and completion feedback.

**Trigger and context:** Real-time, distributed, asynchronous, autonomous, start-up/shutdown and handoff operations.

**Preconditions:** Known timing budgets, transition states, clock/order assumptions and failure handling.

**Authority and control preconditions:** Controller/arbitrator can enforce ordering and block unsafe transitions.

**Required feedback:** Timestamped actions, transition state, completion, retries, timeout and causal order.

**Decision or consumer:** Control/software architect, operator and verifier.

**Nontrigger or cheaper adequate path:** A synchronous local operation with atomic deterministic semantics may need only a direct timeout/completion check.

**Disposition at the historical freeze:** CONTROL_LOOP_PROPERTY

**Failure modes:** Unrealistic timing models, unsynchronised clocks, hidden queues and excessive temporal-state complexity.

**Criticism:** Temporal formalisation can be expensive and false precision can hide uncertain physical timing.

**Contrary evidence:** Formal timing proof remains model-bound and may omit physical/organisational delays.

**Unresolved questions:** How should temporal assurance remain valid under variable network, human and learned-system latency?

**Property versus ceremony:** The property is temporal safety semantics; sequence diagrams or temporal logic are optional implementations.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S018, S049, S089, S100; critical/contrary: S038, S049.

**Primary source identities:** S018; S049; S089; S100

**Critical source identities:** S038; S049

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/10`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-012"></a>
### ESS-012 — Interface assumptions and safety contracts

**Historical origin:** Systems engineering/interface control, aerospace system safety and software assurance; repeatedly exposed by accidents.

**Original form:** Record what each subsystem/controller assumes and guarantees at interfaces, including units, ranges, modes, timing, environment and failure semantics.

**Development:** Evolved from interface control documents to executable contracts, integration tests and live assumption monitors.

**Evolved form in this historical corpus:** Safety-relevant assumptions are explicit, version-bound, validated and invalidated by change.

**Problem:** Components satisfy local requirements while incompatible assumptions create a system hazard.

**Mechanism:** Make safety-relevant assumptions explicit, owned, testable and change-linked; validate at integration and operation.

**Trigger and context:** Reuse, supplier integration, distributed control, configuration change, multiple organisations or novel environment.

**Preconditions:** Stable interface identity, access to supplier evidence and ability to test cross-boundary behaviour.

**Authority and control preconditions:** An integrator must own end-to-end safety; suppliers need change-notification obligations.

**Required feedback:** Interface conformance, assumption validity, integration state, version and environment.

**Decision or consumer:** System integrator, supplier manager, architect and change authority.

**Nontrigger or cheaper adequate path:** A local isolated component with no safety-relevant interface can use a direct type/range check.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Document-only contracts, untestable assumptions, version drift and organisational gaps in authority.

**Criticism:** Formal contracts can omit human/physical context and create false completeness.

**Contrary evidence:** Complete interface contracts are difficult in open sociotechnical systems.

**Unresolved questions:** How can supplier evidence expose sufficient assumptions without disclosing protected design details?

**Property versus ceremony:** The property is managed assumption/guarantee integrity; a particular ICD format is not required.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S029, S083, S090, S100; critical/contrary: S048, S109.

**Primary source identities:** S012; S029; S083; S090; S100

**Critical source identities:** S048; S109

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/11`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-013"></a>
### ESS-013 — Common-cause, common-mode and dependent-failure reasoning

**Historical origin:** Reliability/PRA and defence-in-depth; strengthened by software-diversity experiments and accident evidence.

**Original form:** Analyse dependencies that can defeat multiple channels, barriers, versions or evidence sources at once.

**Development:** Evolved from hardware common-cause models to shared-requirement/tool/data/organisation and informational-dependence analysis.

**Evolved form in this historical corpus:** Claim independence only after identifying shared causes and monitoring the assumptions that sustain it.

**Problem:** Nominal redundancy is treated as independent even though channels share requirements, sensors, environment, tools, power, people or assumptions.

**Mechanism:** Map shared resources/assumptions and environmental causes; diversify where effective; monitor isolation and test common-cause scenarios.

**Trigger and context:** Redundant/high-integrity architectures, multi-version software, layered barriers and independent evidence claims.

**Preconditions:** Architecture/dependency visibility and data or justified bounds for quantitative claims.

**Authority and control preconditions:** System authority can change architecture and reject nominal independence claims.

**Required feedback:** Shared-resource health, coincident failures, barrier independence, environment and evidence lineage.

**Decision or consumer:** Architect, PRA/reliability analyst, assurance authority and operator.

**Nontrigger or cheaper adequate path:** No detailed common-cause model is needed when there is only one simple reversible control and failure is directly detectable.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Unknown dependencies, poorly justified beta factors, added complexity and diversity that is only cosmetic.

**Criticism:** Diversity can add faults and maintenance burden; common-cause probabilities are often data-poor.

**Contrary evidence:** Quantitative common-cause estimates are highly assumption-sensitive, especially for novel software.

**Unresolved questions:** How should dependence among AI models trained on overlapping data be assessed as safety evidence?

**Property versus ceremony:** The property is dependence-aware reasoning; a specific common-cause worksheet is not required.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S040, S041, S050, S051, S056, S087; critical/contrary: S050, S038.

**Primary source identities:** S040; S041; S050; S051; S056; S087

**Critical source identities:** S050; S038

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/12`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-014"></a>
### ESS-014 — Redundancy with demonstrated independence, diversity and observability

**Historical origin:** Reliability engineering, fault tolerance, defence-in-depth and high-reliability operations.

**Original form:** Add alternate paths/channels/barriers so one failure does not cause loss.

**Development:** Evolved from channel count to monitored, dependency-aware and mission-contextual fault tolerance.

**Evolved form in this historical corpus:** Use the simplest architecture that meets the loss constraint, with explicit dependence and degraded-mode semantics.

**Problem:** Single-point failure or unavailable function causes catastrophic loss.

**Mechanism:** Use redundancy only with justified independence/diversity, disagreement handling, health monitoring, maintenance and safe voting/arbitration.

**Trigger and context:** High-consequence single-point failures where alternate means are feasible and do not create greater interaction risk.

**Preconditions:** Independent failure modes, bounded interaction complexity, monitoring and maintainability.

**Authority and control preconditions:** Architecture owner must control shared resources and resolve channel disagreement.

**Required feedback:** Channel health, disagreement, latent failures, common resources and degraded capability.

**Decision or consumer:** System architect, operator and maintenance authority.

**Nontrigger or cheaper adequate path:** Do not add redundancy to low-consequence reversible functions when a simpler reliable design and direct detection is safer.

**Disposition at the historical freeze:** RETAINED_IN_EVOLVED_FORM

**Failure modes:** Common-mode failures, mode confusion, latent standby failure, voter failure, maintenance error and workaround complexity.

**Criticism:** More redundancy is not monotonically safer; software diversity experiments reject naive independence.

**Contrary evidence:** Effect size depends heavily on architecture, maintenance and common-cause exposure.

**Unresolved questions:** When does added redundancy create more software/human interaction risk than risk reduction?

**Property versus ceremony:** The property is effective alternate control; a fixed number of channels is not general.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S050, S051, S056, S057, S067; critical/contrary: S050, S087, S089.

**Primary source identities:** S050; S051; S056; S057; S067

**Critical source identities:** S050; S087; S089

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/13`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-015"></a>
### ESS-015 — Scenario and causal-path coverage through complementary methods

**Historical origin:** Convergence of system hazard analyses, FTA/ETA, HAZOP, PRA, scenario analysis and STPA.

**Original form:** Use multiple representations to search different causal classes and reconcile their findings.

**Development:** Evolved from prescribed task lists to objectives-driven, risk-informed portfolios with explicit coverage and stop rules.

**Evolved form in this historical corpus:** Use the smallest complementary portfolio that covers the credible causal classes and changes a live decision.

**Problem:** A single method’s blind spots are mistaken for absence of hazards.

**Mechanism:** Choose methods by hazard class; cross-check top-down, bottom-up, deviation, interaction and operational scenarios; stop when marginal decision value is low.

**Trigger and context:** Complex/high-consequence systems with heterogeneous causal mechanisms or deep uncertainty.

**Preconditions:** Explicit method assumptions, shared system model, reconciliation of conflicting results and action consumers.

**Authority and control preconditions:** Safety lead can tailor methods and reject duplicative analysis.

**Required feedback:** Coverage by causal class, unresolved contradictions, new evidence and decision changes attributable to each method.

**Decision or consumer:** Safety programme lead, architect and acceptance authority.

**Nontrigger or cheaper adequate path:** Use one cheap deterministic analysis when it exhausts the relevant causal question; do not stack methods for prestige.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Method accumulation, duplicated artefacts from the same assumptions, inconsistent boundaries and no decision impact.

**Criticism:** Comparative method studies are limited; “more methods” can consume experts and dilute attention.

**Contrary evidence:** No robust universal ranking of hazard-analysis methods exists.

**Unresolved questions:** How can marginal hazard-discovery value be measured without using discovered hazard count as a gameable proxy?

**Property versus ceremony:** The property is representation coverage; named-method maximalism is ceremony.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_WITHIN_REPRESENTED_CLASS — technique semantics are established; completeness outside its representation is not.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: CONTEXT_DEPENDENT — transfer requires matching the technique to the causal/hazard class.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S014, S016, S020, S094, S096, S098; critical/contrary: S019, S038, S109.

**Primary source identities:** S014; S016; S020; S094; S096; S098

**Critical source identities:** S019; S038; S109

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/14`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-016"></a>
### ESS-016 — Human–automation coordination and mode awareness

**Historical origin:** Human factors, aviation automation research, medical usability and systems safety.

**Original form:** Design allocation, displays, modes, handoffs and fallback so humans and automation maintain a shared actionable model.

**Development:** Evolved from operator-error control to joint-system design, local-rationality analysis and validated critical-task performance.

**Evolved form in this historical corpus:** Allocate work and authority around realistic human/automation capabilities, with observable modes and verified handoffs.

**Problem:** Automation and human each behave locally as designed while coordination, attention or authority fails.

**Mechanism:** Analyse joint cognitive work, critical tasks, mode/state visibility, workload, takeover time and fallback authority.

**Trigger and context:** Automated/highly interactive systems, degraded modes and safety-critical handoffs.

**Preconditions:** Representative users, realistic scenarios and authority to change automation/interface design.

**Authority and control preconditions:** Clear authority for takeover, inhibit, escalation and refusal; operator responsibility must match information/control.

**Required feedback:** Mode/state, automation intent, limits, alert salience, workload and handoff completion.

**Decision or consumer:** Human-factors engineer, automation designer, operator authority and safety assessor.

**Nontrigger or cheaper adequate path:** For a transparent local tool with direct reversible effect, use simple status/confirmation rather than a full human-factors programme.

**Disposition at the historical freeze:** SOCIO_TECHNICAL_CONTEXT_PROPERTY

**Failure modes:** Training used to compensate for poor design, alarm overload, impossible takeover expectations and blame after loss.

**Criticism:** Human performance is variable; interface validation in tests may not cover rare operational combinations.

**Contrary evidence:** Generalisation across tasks, training and operational contexts is limited.

**Unresolved questions:** How should safe takeover be demonstrated for rare events that cannot be ethically or realistically rehearsed?

**Property versus ceremony:** The property is coordinated control; a generic “human in the loop” claim is not evidence.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: MODERATE — mechanism is coherent but depends on model scope and assumptions.; ACCIDENT_CASE_STRENGTH: HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S063, S064, S088, S089, S106; critical/contrary: S074, S109.

**Primary source identities:** S063; S064; S088; S089; S106

**Critical source identities:** S074; S109

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/15`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-017"></a>
### ESS-017 — Authority, responsibility, stop and handoff clarity

**Historical origin:** System-safety programme management, high-reliability operations, accident investigation and control theory.

**Original form:** Assign who may act, stop, inhibit, accept risk, escalate, restart and resolve conflicts.

**Development:** Evolved toward explicit control-authority maps, protected reporting, dynamic handoffs and consequence-based independence.

**Evolved form in this historical corpus:** Every consequential constraint has an actor with information, competence and authority to enforce it; handoffs transfer state as well as responsibility.

**Problem:** Responsibility is assigned without real authority, or overlapping authorities create gaps/conflict at the critical moment.

**Mechanism:** Define decision rights, stop authority, escalation, handoff state and independent acceptance for consequential exceptions.

**Trigger and context:** Multi-team, supplier, regulator, autonomous/human and emergency operations; any high-consequence exception.

**Preconditions:** Competence, accessible information, non-retaliatory escalation and feasible control options.

**Authority and control preconditions:** Authority must be real, resourced and insulated enough to counter production pressure; acceptance authority must be named.

**Required feedback:** Open decisions, escalations, handoff acknowledgement, stop response and unresolved hazards.

**Decision or consumer:** System owner, operators, safety authority, management and regulator.

**Nontrigger or cheaper adequate path:** A single-person low-consequence local task needs only clear ownership and undo capability.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Nominal stop authority without protection, committee diffusion, approval bottlenecks and responsibility dumping.

**Criticism:** Rigid authority can suppress local adaptation; independence can slow feedback and fragment ownership.

**Contrary evidence:** No authority design eliminates incentive conflict or information asymmetry.

**Unresolved questions:** How can stop authority remain credible when false stops impose large mission/public-service costs?

**Property versus ceremony:** The property is effective authority; titles, boards and RACI charts are optional artefacts.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: MODERATE — mechanism is coherent but depends on model scope and assumptions.; ACCIDENT_CASE_STRENGTH: HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S018, S067, S081, S082, S087, S112; critical/contrary: S048, S066.

**Primary source identities:** S012; S018; S067; S081; S082; S087; S112

**Critical source identities:** S048; S066

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/16`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-018"></a>
### ESS-018 — Traceability from hazards and constraints to implementation and verification

**Historical origin:** System safety, development assurance, functional safety and safety-case practice.

**Original form:** Connect each safety-significant hazard/constraint to design implementation, verification, operational control and evidence.

**Development:** Evolved toward model/tool-supported impact analysis, evidence provenance and live orphan detection.

**Evolved form in this historical corpus:** Maintain only decision-relevant traceability sufficient to show current hazard-to-control-to-evidence closure.

**Problem:** Safety requirements exist but are unimplemented, unverified, tested against the wrong configuration or orphaned after change.

**Mechanism:** Maintain bidirectional, configuration-bound links and test whether every claim has a control and every control has a hazard rationale.

**Trigger and context:** Consequential controls, regulated development and systems with many suppliers/changes.

**Preconditions:** Stable identifiers, configuration management and semantic—not merely hyperlink—traceability.

**Authority and control preconditions:** Owners must be able to resolve orphaned requirements/evidence and block release where links fail.

**Required feedback:** Current configuration, verification result, unresolved links, waivers and operational monitoring.

**Decision or consumer:** Design authority, verifier, assurance case owner and change authority.

**Nontrigger or cheaper adequate path:** For a tiny local deterministic change, one direct link from hazard/invariant to test result may be sufficient.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Trace-link volume without semantic review, auto-generated false completeness and unmaintainable matrices.

**Criticism:** Traceability is not proof; linked requirements can all be wrong or derived from one flawed assumption.

**Contrary evidence:** Automated traceability quality and causal payoff have uneven empirical validation.

**Unresolved questions:** How can semantic trace quality be measured without rewarding link count?

**Property versus ceremony:** The property is semantic current linkage; a traceability matrix format is not required.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S029, S031, S042, S047, S100; critical/contrary: S048, S049.

**Primary source identities:** S029; S031; S042; S047; S100

**Critical source identities:** S048; S049

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/17`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-019"></a>
### ESS-019 — Uncertainty-aware risk representation rather than score-only governance

**Historical origin:** PRA/risk-analysis traditions and later explicit uncertainty critiques.

**Original form:** Represent consequences, frequencies/probabilities, uncertainty, assumptions, dependence and knowledge strength.

**Development:** Evolved from matrix scores and point estimates toward plural representations, uncertainty analysis and consequence constraints.

**Evolved form in this historical corpus:** Choose the least elaborate representation that preserves decision-relevant consequence and uncertainty; never call the score the risk.

**Problem:** An ordinal score or point estimate is treated as objective risk and drives acceptance/allocation without showing uncertainty.

**Mechanism:** Use scores only as transparent prompts; retain consequence and uncertainty separately; quantify where data/model warrant and sensitivity-test decisions.

**Trigger and context:** Risk comparisons, prioritisation and residual-risk decisions where uncertainty can change action.

**Preconditions:** Defined decision, data provenance, calibrated model and authority capable of reasoning under uncertainty.

**Authority and control preconditions:** Risk authority must be able to reject unsupported precision and choose precaution/learning/monitoring.

**Required feedback:** Data quality, model sensitivity, uncertainty bounds, near misses and assumption validity.

**Decision or consumer:** Risk acceptor, designer, regulator and resource allocator.

**Nontrigger or cheaper adequate path:** If a deterministic constraint settles the decision, do not estimate probability merely to fill a matrix.

**Disposition at the historical freeze:** USEFUL_BUT_EASILY_GAMED

**Failure modes:** Opaque expert judgement, incomparable ordinal arithmetic, threshold gaming and expensive quantification with no decision effect.

**Criticism:** Quantitative models can also mislead; deep uncertainty may resist probability assignment.

**Contrary evidence:** Rare-event probabilities and dependence remain weakly identified; uncertainty frameworks do not guarantee better decisions.

**Unresolved questions:** Which uncertainty representations are usable under time pressure without collapsing back into colour categories?

**Property versus ceremony:** The property is explicit uncertainty and decision linkage; coloured matrices are optional and often harmful.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S034, S036, S037, S038, S039, S040; critical/contrary: S036, S037, S038.

**Primary source identities:** S034; S036; S037; S038; S039; S040

**Critical source identities:** S036; S037; S038

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/18`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-020"></a>
### ESS-020 — Consequence, reversibility, coupling and observability proportionality

**Historical origin:** Risk-informed system safety, ALARP/SFAIRP, safety-integrity/development-assurance grading and tailored regulatory practice.

**Original form:** Grade rigour, independence, containment, evidence and authority according to credible consequence and the difficulty of detecting/reversing loss.

**Development:** Evolved from fixed process classes to multidimensional, change-aware tailoring with explicit cheap paths and escalation triggers.

**Evolved form in this historical corpus:** Control strength rises with credible loss and irreversibility/coupling/latency, while deterministic low-risk work remains cheap.

**Problem:** Uniform maximal process wastes effort on trivial changes, while weak controls are applied to irreversible tightly coupled hazards.

**Mechanism:** Assess consequence, reversibility, coupling, observability latency, recovery difficulty and uncertainty; select control strength and cheap path accordingly.

**Trigger and context:** All work, with greatest value where harm is severe, irreversible, coupled, latent or hard to test.

**Preconditions:** Credible consequence model, change classification and authority to tailor both upward and downward.

**Authority and control preconditions:** A competent risk/safety owner must be able to demand more or less control and document the basis.

**Required feedback:** Actual propagation/recovery performance, false-stop cost, near misses and whether controls change decisions.

**Decision or consumer:** Safety/risk authority, programme leadership and operations.

**Nontrigger or cheaper adequate path:** Local, cheap, reversible, immediately observable work with an authoritative discriminator uses a minimal check and normal engineering review.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Risk-class gaming, simplistic matrices, certification-category lock-in and underestimating systemic coupling.

**Criticism:** Proportionality is not permission to ignore uncertain catastrophic hazards; ALARP interpretation is contested.

**Contrary evidence:** No universal scalar combines consequence, reversibility, coupling and observability without information loss.

**Unresolved questions:** How should proportionality account for low-probability public harms when evidence is sparse and false stops are also dangerous?

**Property versus ceremony:** The property is justified tailoring; classification boards and matrices are implementations, not ends.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S014, S029, S035, S052, S053, S095, S104; critical/contrary: S036, S038, S113.

**Primary source identities:** S014; S029; S035; S052; S053; S095; S104

**Critical source identities:** S036; S038; S113

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/19`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-021"></a>
### ESS-021 — Explicit residual-risk acceptance by competent authority

**Historical origin:** Military system-safety risk-acceptance practice, medical-device risk management, safety cases and ALARP governance.

**Original form:** After feasible controls, document the remaining hazard, assumptions and evidence and obtain acceptance at an authority level commensurate with consequence.

**Development:** Evolved toward explicit residual-risk statements, bounded delegated authority, expiry conditions and operational monitoring.

**Evolved form in this historical corpus:** A current, named and revisable decision by a competent authority over a residual hazard whose controls, uncertainty, exposure and alternatives are visible.

**Problem:** Residual risk disappears into an analyst score, is implicitly accepted by delivery pressure, or is approved by someone without mandate or knowledge.

**Mechanism:** State the residual hazard and uncertainty, identify the exposed parties and control status, obtain time/configuration-bounded acceptance and reopen on change or evidence.

**Trigger and context:** Consequential residual hazards that cannot presently be eliminated or further reduced at proportionate cost.

**Preconditions:** Current hazard/control evidence, explicit alternatives and uncertainty, identified exposure and a defined acceptance policy.

**Authority and control preconditions:** The acceptor must have legal/organisational mandate, relevant competence and authority over resources or operational restrictions.

**Required feedback:** Barrier health, exposure, assumptions, incidents, time/configuration limits and effectiveness of compensating controls.

**Decision or consumer:** Design authority, operator, regulator, accountable executive and affected operational owner.

**Nontrigger or cheaper adequate path:** No separate acceptance ritual is needed when an authoritative deterministic check proves the hazard absent or a trivial reversible effect remains within ordinary authority.

**Disposition at the historical freeze:** USEFUL_BUT_EASILY_GAMED

**Failure modes:** Rubber-stamp boards, risk laundering through matrices, acceptance by authority remote from consequences and indefinite waivers.

**Criticism:** Formal acceptance cannot make an intolerable risk acceptable and may exclude affected publics or workers from the decision.

**Contrary evidence:** Authority hierarchies do not resolve distributive ethics, unknown hazards or weak evidence and can legitimise production pressure.

**Unresolved questions:** How should acceptance incorporate those exposed to public or worker risk when they do not control the system?

**Property versus ceremony:** A signed form is not the property; accountable and evidence-bounded acceptance is.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S027, S034, S042; critical/contrary: S036, S038, S113.

**Primary source identities:** S012; S027; S034; S042

**Critical source identities:** S036; S038; S113

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/20`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-022"></a>
### ESS-022 — Proportionate risk reduction under ALARP or SFAIRP reasoning

**Historical origin:** UK health-and-safety law and regulatory decision practice, with analogous practicability and proportionality reasoning elsewhere.

**Original form:** Reduce risk so far as reasonably practicable rather than stop at a numerical threshold or demand literal zero risk.

**Development:** Evolved toward transparent option analysis, good-practice presumptions, explicit uncertainty and higher burdens for catastrophic exposure.

**Evolved form in this historical corpus:** Use proportionality as disciplined justification for control sufficiency, not as a numerical escape hatch or universal legal export.

**Problem:** Either cheap meaningful controls are omitted because a score is below threshold, or disproportionate burdens are imposed without material safety gain.

**Mechanism:** Identify feasible controls, establish good practice, examine remaining risk and sacrifice transparently, and require stronger justification as consequence rises.

**Trigger and context:** Material occupational/process/public hazards where feasible alternatives and control costs matter.

**Preconditions:** Legally appropriate jurisdiction, credible consequence evidence, feasible options and competent judgement.

**Authority and control preconditions:** The duty holder retains the burden to show sufficient reduction; a calculator or consultant cannot own the legal judgement.

**Required feedback:** Control effectiveness, changing good practice, exposure, sacrifice estimates and evidence that adopted controls remain operative.

**Decision or consumer:** Duty holder, regulator, workforce/public representative and design/operations authority.

**Nontrigger or cheaper adequate path:** Where a binding deterministic rule or clearly trivial reversible hazard settles the decision, use it directly rather than manufacture a cost-benefit case.

**Disposition at the historical freeze:** HIGH_CONSEQUENCE_CONTEXT_PROPERTY

**Failure modes:** Back-calculated numbers, monetisation controversy, threshold gaming and invoking cost before identifying controls.

**Criticism:** ALARP is jurisdiction-specific, ethically contested and frequently misunderstood; it is not a universal optimisation formula.

**Contrary evidence:** No strong comparative evidence establishes ALARP as the optimal decision rule across cultures, rights regimes or catastrophic uncertainty.

**Unresolved questions:** How should practicability reasoning handle low-frequency harms whose burdens fall on nonconsenting third parties?

**Property versus ceremony:** The transferable property is reasoned proportionality; the exact legal test and paperwork are domain-specific.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S034, S035, S113; critical/contrary: S036, S038, S113.

**Primary source identities:** S034; S035; S113

**Critical source identities:** S036; S038; S113

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/21`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-023"></a>
### ESS-023 — Defence in depth with barrier independence and degradation monitoring

**Historical origin:** Nuclear safety and process protection, converging with layered aerospace and functional-safety architectures.

**Original form:** Provide multiple preventive, control, mitigation and emergency layers so one error or failure does not directly produce catastrophic loss.

**Development:** Evolved from redundant layer count toward functional diversity, independence claims, degradation monitoring and severe-accident mitigation.

**Evolved form in this historical corpus:** A hazard-specific barrier architecture whose layers have distinct functions, credible independence and live health evidence.

**Problem:** A single protection, assumption or operator response is treated as sufficient for a high-consequence hazard.

**Mechanism:** Allocate distinct barrier purposes, analyse common cause and dependencies, monitor availability and preserve escalation/mitigation when prevention fails.

**Trigger and context:** Severe, irreversible hazards for which no single control can be shown sufficiently dependable.

**Preconditions:** Barrier functions and dependencies are explicit; surveillance and maintenance can detect degradation; emergency arrangements exist.

**Authority and control preconditions:** Owners must be able to maintain, test, isolate and restore layers and to restrict operation when defence is impaired.

**Required feedback:** Barrier demand and success, independence, common utilities, bypass status, test coverage and degraded configurations.

**Decision or consumer:** Architect, operations, maintenance, emergency management and regulator.

**Nontrigger or cheaper adequate path:** Do not add nominal layers to a trivial reversible task or where one simple physically enforced elimination removes the hazard.

**Disposition at the historical freeze:** HIGH_CONSEQUENCE_CONTEXT_PROPERTY

**Failure modes:** Layer counting, shared common modes, hidden coupling, added complexity and compensatory complacency.

**Criticism:** Fukushima and multiversion evidence show that apparent multiplicity does not establish effective independence.

**Contrary evidence:** Additional layers can add software, testing and organisational complexity; cross-domain optimal layer counts are not established.

**Unresolved questions:** What evidence is sufficient to claim independence among software, organisational and supplier-controlled barriers?

**Property versus ceremony:** A bow-tie or layer diagram is optional; demonstrably effective, independent and monitored barriers are the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S056, S057, S087, S103, S104; critical/contrary: S050, S087.

**Primary source identities:** S056; S057; S087; S103; S104

**Critical source identities:** S050; S087

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/22`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-024"></a>
### ESS-024 — Safety-integrity and development-assurance rigour tied to safety functions

**Historical origin:** IEC 61508 safety integrity levels and aviation/automotive development-assurance classifications.

**Original form:** Classify safety functions or failure conditions and attach graded architectural, development and verification rigour.

**Development:** Evolved toward explicit scope boundaries, complementary intended-function/security analyses and assurance claims about functions rather than the whole system.

**Evolved form in this historical corpus:** Use graded integrity objectives as one hazard-derived assurance mechanism, never as a numerical certificate of total system safety.

**Problem:** An assurance level is treated as a direct probability that the whole system is safe, or assigned without a valid hazard-to-function allocation.

**Mechanism:** Derive integrity/assurance needs from hazards and functions; meet domain architecture and process objectives; verify actual function and complement with interaction analysis.

**Trigger and context:** Safety-related E/E/PE, airborne software/hardware and automotive functions whose failure conditions justify graded assurance.

**Preconditions:** Valid hazard classification, allocated safety function, domain applicability and evidence that architecture and verification objectives are met.

**Authority and control preconditions:** Certification/design authorities must control classification and independence; suppliers must disclose relevant development evidence.

**Required feedback:** Function demand/success, diagnostic coverage, systematic-defect controls, requirement/verification coverage and configuration identity.

**Decision or consumer:** System safety assessor, functional-safety manager, certification authority and integrator.

**Nontrigger or cheaper adequate path:** Do not assign a high assurance level to low-consequence code or use the classification where a direct deterministic test fully settles a local reversible change.

**Disposition at the historical freeze:** DOMAIN_SPECIFIC

**Failure modes:** Level inflation, lowest-bid evidence production, rote objective completion and scope gaps such as intended-function hazards.

**Criticism:** Standards authority is strong but comparative evidence for exact level/process prescriptions is limited; SOTIF exists because malfunction-only scope is incomplete.

**Contrary evidence:** Exact process prescriptions and claimed probability correspondences have limited independent outcome validation.

**Unresolved questions:** How should integrity classifications be recalibrated for learning/adaptive functions whose behaviour changes in service?

**Property versus ceremony:** The general property is consequence-linked rigour; SIL, ASIL and DAL taxonomies are domain artefacts.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S021, S022, S023, S024, S029, S031, S032; critical/contrary: S025, S036, S050.

**Primary source identities:** S021; S022; S023; S024; S029; S031; S032

**Critical source identities:** S025; S036; S050

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/23`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-025"></a>
### ESS-025 — Informational independence and diversity of assurance evidence

**Historical origin:** Independent verification/validation, diverse design and assurance-case confidence traditions.

**Original form:** Seek evidence generated by mechanisms, people, data and assumptions sufficiently independent to expose common blind spots.

**Development:** Evolved from organisational separation alone toward evidence-dependence graphs, diverse failure mechanisms and risk-based independence.

**Evolved form in this historical corpus:** Require independently informative evidence in proportion to consequence and explicitly disclose shared assumptions and sources.

**Problem:** Many reviews or artefacts derived from one requirement/model/test oracle are counted as independent confirmation.

**Mechanism:** Map evidence provenance and dependence; combine analytic, test, operational and independent challenge where each can fail differently.

**Trigger and context:** High-consequence claims whose error cannot be cheaply discovered after deployment.

**Preconditions:** Evidence methods have explicit failure modes and provenance; independent assessors have access, competence and challenge authority.

**Authority and control preconditions:** The independent function needs organisational freedom and information access, but informational independence must be assessed separately.

**Required feedback:** Disagreements, common inputs, oracle diversity, defect yield, challenge closure and configuration coverage.

**Decision or consumer:** Safety case owner, IV&V, certification authority and risk acceptor.

**Nontrigger or cheaper adequate path:** One direct authoritative discriminator suffices when it conclusively decides a local reversible claim; reviewer multiplication adds no information.

**Disposition at the historical freeze:** ASSURANCE_PROPERTY

**Failure modes:** Independence theatre, duplicated tests, shared flawed specifications, costly segregation and delayed feedback.

**Criticism:** Experimental multiversion evidence directly undermines naive independence assumptions; independence can also impede fast integrated learning.

**Contrary evidence:** The optimal balance between separation and integrated rapid feedback remains domain and lifecycle dependent.

**Unresolved questions:** How can evidence dependence be measured cheaply enough to guide assurance portfolios in rapid delivery?

**Property versus ceremony:** A separate reviewer or document is not automatically independent evidence.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S044, S046, S049, S050, S099; critical/contrary: S048, S050.

**Primary source identities:** S044; S046; S049; S050; S099

**Critical source identities:** S048; S050

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/24`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-026"></a>
### ESS-026 — Claim–argument–evidence safety assurance

**Historical origin:** Nuclear and defence safety cases, later structured assurance cases and Goal Structuring Notation.

**Original form:** Make safety claims, reasoning, evidence, assumptions and context explicit enough for challenge and acceptance.

**Development:** Evolved toward modular, challenge-driven, confidence-aware and living cases integrated with hazard and configuration state.

**Evolved form in this historical corpus:** A current, defeasible decision argument connecting consequential claims to relevant evidence, assumptions, uncertainty and authority.

**Problem:** Evidence accumulates without showing what it establishes, or claims are accepted because a document appears complete.

**Mechanism:** Construct the minimum argument needed for live decisions; expose premises, evidence relevance, uncertainty and unresolved challenges; bind it to current configuration.

**Trigger and context:** Consequential safety decisions requiring synthesis across heterogeneous evidence and organisations.

**Preconditions:** Defined claims and consumers, trustworthy evidence, current system boundary and willingness to record uncertainty/defeaters.

**Authority and control preconditions:** The case owner must not control all challenge; acceptance authority needs power to reject or demand evidence.

**Required feedback:** Evidence validity, claim coverage, assumptions, challenge status, operational indicators and configuration/change events.

**Decision or consumer:** Design authority, operator, regulator/certifier and residual-risk acceptor.

**Nontrigger or cheaper adequate path:** A direct deterministic proof/test and a brief recorded rationale may be the whole case for a narrow reversible claim.

**Disposition at the historical freeze:** ASSURANCE_PROPERTY

**Failure modes:** Argument theatre, template completion, rhetorical overclaim, stale evidence and safety case detached from engineering work.

**Criticism:** Nimrod is powerful counterevidence to equating a voluminous accepted case with safety; formal coherence cannot establish premise truth.

**Contrary evidence:** Outcome evidence comparing assurance-case formats is limited and argument quality remains judgement-sensitive.

**Unresolved questions:** Which machine-checkable assurance structures improve decisions rather than merely increasing trace volume?

**Property versus ceremony:** GSN and a monolithic document are optional notations; explicit justified reasoning is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S042, S043, S044, S045, S046, S108; critical/contrary: S048, S107, S108.

**Primary source identities:** S042; S043; S044; S045; S046; S108

**Critical source identities:** S048; S107; S108

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/25`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-027"></a>
### ESS-027 — Defeaters, counterevidence and authorised challenge in assurance

**Historical origin:** Critical argumentation, independent review and Assurance 2.0 reforms of confirmatory safety cases.

**Original form:** Actively search for conditions that would defeat a claim, invalidate evidence or reverse a safety decision.

**Development:** Evolved from review sign-off toward explicit defeater logs, confidence arguments and closure/acceptance of unresolved challenges.

**Evolved form in this historical corpus:** A consequential claim remains provisional until material defeaters are eliminated, controlled, or explicitly accepted by the right authority.

**Problem:** Assurance gathers only confirming evidence and treats unresolved objections as editorial defects.

**Mechanism:** Record defeaters and contrary evidence, empower technically competent challenge, assign closure criteria and preserve unresolved uncertainty in acceptance.

**Trigger and context:** High-consequence or model-sensitive claims, novel systems and changes that invalidate prior assumptions.

**Preconditions:** Psychological/organisational safety for dissent, traceable challenge state and a decision process that can change course.

**Authority and control preconditions:** Challengers need access and non-retaliation; decision authority must answer rather than merely receive objections.

**Required feedback:** Open objections, negative tests, anomaly trends, premise failures, response quality and whether decisions changed.

**Decision or consumer:** Independent assessor, workforce/operator, safety board and accountable decision owner.

**Nontrigger or cheaper adequate path:** For a settled low-consequence deterministic claim, one sanity check is enough; adversarial boards add no value.

**Disposition at the historical freeze:** ASSURANCE_PROPERTY

**Failure modes:** Performative red teaming, endless objections without decision criteria, retaliation and burying challenges in appendices.

**Criticism:** Challenge quality is difficult to measure; more reviewers can repeat the same assumptions or paralyse decisions.

**Contrary evidence:** Adversarial effort can become ritual or denial-of-service when loss relevance and closure rules are absent.

**Unresolved questions:** How should assurance distinguish a material defeater from speculative objection without suppressing weak signals?

**Property versus ceremony:** A “devil’s advocate” meeting is not required; live disconfirming evidence and authority to act are.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S044, S045, S046, S112; critical/contrary: S048, S050.

**Primary source identities:** S044; S045; S046; S112

**Critical source identities:** S048; S050

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/26`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-028"></a>
### ESS-028 — Configuration identity binding for safety evidence

**Historical origin:** Configuration management in military/aerospace system safety, software assurance and safety-case practice.

**Original form:** Bind hazards, assumptions, analyses, tests, approvals and operating limits to an identifiable system configuration and environment.

**Development:** Evolved toward machine-linked evidence provenance, deployed-state attestation and assumption/configuration impact graphs.

**Evolved form in this historical corpus:** No consequential safety claim is reusable without demonstrating that its configuration, environment and assumptions still match.

**Problem:** Apparently green evidence refers to a different build, calibration, supplier component, model, procedure or operating context.

**Mechanism:** Record decision-relevant configuration identifiers and evidence provenance; verify deployed identity and invalidate/reassess affected claims on divergence.

**Trigger and context:** Any safety-relevant change, distributed deployment, supplier substitution or long-lived assurance claim.

**Preconditions:** Controlled baselines, deployment observability, supplier/change notification and an impact model.

**Authority and control preconditions:** Release/operations authority must be able to block unknown or mismatched configurations.

**Required feedback:** Build/component IDs, calibration, parameters, environment, evidence version, deployment inventory and deviations.

**Decision or consumer:** Configuration manager, release authority, safety case owner, operator and assessor.

**Nontrigger or cheaper adequate path:** For a local disposable reversible experiment, identify only the artefact and conditions necessary to reproduce the decisive check.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Identifier bureaucracy without semantic impact, uncontrolled runtime adaptation and false confidence in nominal version labels.

**Criticism:** A hash or baseline name does not prove behavioural equivalence; operational environment and hidden dependencies may still differ.

**Contrary evidence:** Behavioural identity for adaptive, cloud and supplier-controlled systems remains technically difficult.

**Unresolved questions:** What minimal equivalence evidence is sufficient to reuse assurance across rapidly changing distributed deployments?

**Property versus ceremony:** The property is identity/equivalence sufficient for the decision; a particular CM database is not required.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S029, S042, S047, S052, S100; critical/contrary: S048, S095.

**Primary source identities:** S012; S029; S042; S047; S052; S100

**Critical source identities:** S048; S095

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/27`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-029"></a>
### ESS-029 — Safety impact analysis and proportionate re-assurance after change

**Historical origin:** Military/aerospace modification assessment, process management of change, nuclear modification and incremental medical-device assurance.

**Original form:** Classify a change, identify affected hazards/controls/assumptions/interfaces/evidence, reuse unaffected evidence and re-establish affected claims.

**Development:** Evolved from document change control toward model-linked differential assurance, predetermined change plans and post-change monitoring.

**Evolved form in this historical corpus:** Re-establish exactly the safety claims whose system, assumptions, controls or evidence may have changed; justify both reuse and new work.

**Problem:** A “small” change bypasses safety reasoning, or every change triggers a full undifferentiated re-certification.

**Mechanism:** Use traceable impact analysis from change to hazards, interactions, constraints and evidence; test the affected frontier and monitor uncertain effects.

**Trigger and context:** Software, hardware, supplier, environment, procedure, security and organisational changes with plausible hazard reach.

**Preconditions:** Current baseline, dependency/interface model, hazard state and authority to classify/escalate change.

**Authority and control preconditions:** Change authority must be able to stop release, demand wider evidence and approve bounded reuse.

**Required feedback:** Diff/configuration identity, changed assumptions, affected tests, operational telemetry, regression and rollback readiness.

**Decision or consumer:** Change control, release authority, system safety, operator and regulator/certifier.

**Nontrigger or cheaper adequate path:** A trivial local reversible change with a decisive regression discriminator uses that check and records only the necessary identity.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Form-based classification, hidden cumulative change, reusing stale evidence, certification avoidance and blanket rework.

**Criticism:** Incremental assurance depends on accurate impact models; complex adaptive interactions can defeat locality assumptions.

**Contrary evidence:** No general method guarantees complete impact discovery in tightly coupled adaptive systems.

**Unresolved questions:** How can cumulative small changes and emergent interactions be detected before differential assurance becomes falsely local?

**Property versus ceremony:** A change board is optional; causal impact, authority and current evidence are not.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S052, S053, S054, S055, S095, S098; critical/contrary: S048, S095.

**Primary source identities:** S052; S053; S054; S055; S095; S098

**Critical source identities:** S048; S095

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/28`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-030"></a>
### ESS-030 — Living, current and operationally connected assurance

**Historical origin:** Through-life safety cases, dynamic safety cases and objectives-driven case-assured regulation.

**Original form:** Maintain claims, evidence, assumptions, hazard controls and operational indicators as the system and context change.

**Development:** Evolved from static documents toward event-driven modular re-assurance with explicit evidence freshness and human authority.

**Evolved form in this historical corpus:** Assurance remains valid only while named configuration, assumptions, controls and evidence are current; relevant changes trigger bounded reassessment.

**Problem:** A once-approved case remains nominally valid while configuration, environment, usage, threats or control performance drift.

**Mechanism:** Define change and operational triggers, connect leading evidence to claims, reassess affected arguments and require decision closure.

**Trigger and context:** Long-lived software-intensive, autonomous, security-exposed or operationally adapting systems.

**Preconditions:** Stable claim architecture, configuration identity, trusted telemetry, trigger thresholds and resourced decision owners.

**Authority and control preconditions:** Owners need authority to restrict, degrade, rollback or re-assure on adverse evidence.

**Required feedback:** Configuration, control health, incidents/precursors, assumption monitors, evidence expiry and operational-envelope excursions.

**Decision or consumer:** Operator, safety case owner, release authority, regulator and maintenance organisation.

**Nontrigger or cheaper adequate path:** Static assurance can suffice for a stable, bounded, short-lived and readily observed system; update only when a relevant trigger occurs.

**Disposition at the historical freeze:** ASSURANCE_PROPERTY

**Failure modes:** Dashboard theatre, noisy triggers, automated circular evidence, alert fatigue and impossible real-time completeness.

**Criticism:** Continuous assurance cannot observe unknown hazards and may privilege measurable proxies over causal control state.

**Contrary evidence:** Automation may create false confidence and costly latency; operational data can be biased or insufficient for rare hazards.

**Unresolved questions:** Which claims can be monitored continuously, and which still require episodic independent re-analysis?

**Property versus ceremony:** Continuous document editing is not required; current decision-relevant assurance state is.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S047, S055, S098; critical/contrary: S048, S074, S108.

**Primary source identities:** S047; S055; S098

**Critical source identities:** S048; S074; S108

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/29`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-031"></a>
### ESS-031 — Independent assessment and IV&V where consequence warrants

**Historical origin:** Military/aerospace independent verification and validation, certification and nuclear independent review.

**Original form:** Use technically competent assessors outside the delivery decision chain to challenge high-consequence claims and evidence.

**Development:** Evolved toward consequence-based scoping, early continuous involvement and explicit informational-independence analysis.

**Evolved form in this historical corpus:** Deploy independent assessment only where its distinct information and challenge authority justify cost, and measure it by decisions/findings rather than signatures.

**Problem:** The producing team is the sole judge of its own assumptions, implementation and verification, or independent review becomes duplicate checklist work.

**Mechanism:** Define risk-based scope, give assessors evidence/tool/access rights, seek independent information and close material findings before acceptance.

**Trigger and context:** Catastrophic or irreversible failure conditions, novel technology, weak testability, conflicted suppliers or mandated domains.

**Preconditions:** Competence, access, independence, clear claim scope and response authority.

**Authority and control preconditions:** The assessor must be able to report to an authority that can change design, release or operation.

**Required feedback:** Independent defect findings, evidence provenance, unresolved dissent, retest results and configuration coverage.

**Decision or consumer:** Risk acceptor, certification authority, programme executive and operator.

**Nontrigger or cheaper adequate path:** Routine peer review or one deterministic check is sufficient for low-consequence reversible work; separate IV&V should not trigger by label alone.

**Disposition at the historical freeze:** HIGH_CONSEQUENCE_CONTEXT_PROPERTY

**Failure modes:** Expensive late paperwork, adversarial handoff, duplicated evidence and false inference that separation guarantees independence.

**Criticism:** Controlled multiversion evidence and assurance failures show that nominal independence can remain correlated.

**Contrary evidence:** Independence can slow feedback and create responsibility diffusion if integrated poorly.

**Unresolved questions:** What evidence demonstrates that an IV&V activity is independently informative rather than merely organisationally separate?

**Property versus ceremony:** A separate organisation is not the property; independently informative challenge is.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S029, S042, S099, S100; critical/contrary: S048, S050.

**Primary source identities:** S029; S042; S099; S100

**Critical source identities:** S048; S050

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/30`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-032"></a>
### ESS-032 — Evidence triangulation and targeted formal verification

**Historical origin:** Formal-methods research, IV&V, quantitative analysis and assurance-case synthesis.

**Original form:** Match claim-critical uncertainties to evidence methods with complementary strengths, including formal proof where a precise model materially reduces uncertainty.

**Development:** Evolved from “formal versus testing” toward claim-driven portfolios, model validation and explicit evidence-dependence reasoning.

**Evolved form in this historical corpus:** Use formal methods selectively where a precise hazard-linked property and abstraction make them decisively informative, then triangulate model correspondence.

**Problem:** Testing alone misses rare state spaces, proof establishes the wrong model, or many weak methods are combined without a claim-specific rationale.

**Mechanism:** For each consequential claim, select the least set of analyses/tests/inspections/operational evidence that attacks distinct failure modes; prove only tractable decisive properties.

**Trigger and context:** Complex logic, concurrency, control laws, protection functions or rare combinations where exhaustive empirical testing is infeasible.

**Preconditions:** Precise property and model, validated abstraction, configuration mapping, trustworthy tools and a decision consumer.

**Authority and control preconditions:** Assurance authority decides where proof/test diversity is necessary and owns residual model risk.

**Required feedback:** Proof obligations, model assumptions, code/configuration correspondence, test coverage and operational anomalies.

**Decision or consumer:** Designer, verifier, safety case owner and independent assessor.

**Nontrigger or cheaper adequate path:** Use direct execution, inspection or deterministic testing when it fully settles a simple claim; formalisation must earn its cost.

**Disposition at the historical freeze:** ASSURANCE_PROPERTY

**Failure modes:** Proof theatre, unverifiable models, tool-chain dependence, duplicated evidence and formal work disconnected from hazard decisions.

**Criticism:** Formal proof establishes only the modelled property under assumptions; outcome superiority over disciplined testing is context dependent.

**Contrary evidence:** Specification and abstraction errors remain common-mode limits and formalisation can consume disproportionate resources.

**Unresolved questions:** Which claim/evidence selection rules best predict when formal verification will change a safety decision?

**Property versus ceremony:** A proof certificate is not a safety claim about the physical system without validated assumptions and configuration linkage.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S044, S049, S098, S100; critical/contrary: S048, S050.

**Primary source identities:** S044; S049; S098; S100

**Critical source identities:** S048; S050

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/31`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-033"></a>
### ESS-033 — Joint safety–security analysis for cyber-physical control

**Historical origin:** Functional safety, automotive cybersecurity, medical-device cybersecurity and nuclear safety/security interface guidance.

**Original form:** Analyse malicious, accidental and mixed pathways that alter safety-critical control, feedback, availability, configuration or recovery.

**Development:** Evolved toward shared cyber-physical control models, coordinated change assurance and explicit conflict resolution.

**Evolved form in this historical corpus:** Co-engineer safety and security whenever they share control, feedback, configuration or availability dependencies; keep domain analyses complementary.

**Problem:** Safety assumes benign faults while security changes disable controls, spoof feedback or make a safe shutdown unavailable.

**Mechanism:** Share system/control boundaries, identify safety consequences of threats and security consequences of safety controls, coordinate mitigations and changes.

**Trigger and context:** Networked, updateable, remotely supported, autonomous or adversarially exposed safety-relevant systems.

**Preconditions:** Shared architecture/configuration view, threat and hazard expertise, coordinated authority and secure observability.

**Authority and control preconditions:** Safety and security owners need a joint escalation/acceptance path; neither may unilaterally break the other control objective.

**Required feedback:** Security events, control/feedback integrity, patch/configuration status, availability, anomalies and attack-path assumptions.

**Decision or consumer:** Safety, security, operations, supplier and risk-acceptance authorities.

**Nontrigger or cheaper adequate path:** Do not impose a full threat programme on an isolated trivial reversible function with no plausible adversarial safety pathway.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Duplicated registers, safety/security priority conflict, secrecy blocking evidence and emergency patching without safety impact analysis.

**Criticism:** Integrated methods and comparative effectiveness evidence are still developing; total model completeness is impossible.

**Contrary evidence:** Cross-domain empirical comparison of integrated methods remains limited and secrecy can constrain evidence.

**Unresolved questions:** How should urgent vulnerability remediation preserve safety evidence when exploit exposure and safety regression demand opposite tempos?

**Property versus ceremony:** A combined workshop or merged document is optional; the shared causal paths and authority are not.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S026, S028, S061; critical/contrary: S055, S074.

**Primary source identities:** S026; S028; S061

**Critical source identities:** S055; S074

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/32`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-034"></a>
### ESS-034 — Actionable hazard detection and alarm burden control

**Historical origin:** Process protection, aviation/medical human factors and alarm-management practice.

**Original form:** Detect hazardous or degraded states early enough for a named consumer to take an effective action, while controlling nuisance and overload.

**Development:** Evolved from instrument installation toward hazard-linked performance requirements, prioritisation, human factors and consumer/action verification.

**Evolved form in this historical corpus:** An alarm is justified only when its signal is trustworthy, timely, discriminating and connected to an effective authorised response.

**Problem:** Detection is counted as control although no one can interpret or act on it, or excessive alarms hide the critical signal.

**Mechanism:** Link each safety-significant alarm to hazard, timing, decision, response and confirmation; monitor false/missed alarm performance and rationalise burden.

**Trigger and context:** Hazards requiring detection before irreversible progression, especially remote or highly automated processes.

**Preconditions:** Detectable precursor, sufficient response time, reliable signal semantics, trained/authorised consumer and maintained sensors.

**Authority and control preconditions:** The receiver needs authority and resources to diagnose, stop, isolate or escalate; alarm ownership must be explicit.

**Required feedback:** Detection probability/latency, false/nuisance rate, acknowledgement, action completion, alarm floods and sensor health.

**Decision or consumer:** Operator, automated safety controller, maintenance and emergency response.

**Nontrigger or cheaper adequate path:** Direct physical prevention or immediate observation may be cheaper than alarms; do not alert when no safe action exists.

**Disposition at the historical freeze:** CONTEXT_DEPENDENT

**Failure modes:** Alarm fatigue, automation bias, disabled alarms, alert storms, threshold gaming and no-action dashboards.

**Criticism:** More detection can reduce safety when attention and response capacity are saturated; alarm counts are poor proxies.

**Contrary evidence:** Performance varies greatly by domain and automated detection of novel hazards remains limited.

**Unresolved questions:** How should alarm systems adapt thresholds without creating unassured drift or masking weak signals?

**Property versus ceremony:** A dashboard tile or alarm count is ceremony without a live decision and burden budget.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S074, S075, S101, S106; critical/contrary: S073, S074.

**Primary source identities:** S074; S075; S101; S106

**Critical source identities:** S073; S074

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/33`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-035"></a>
### ESS-035 — Containment, isolation and emergency stop with state confirmation

**Historical origin:** Process emergency shutdown/isolation, interlocks and system-safety fail-safe design.

**Original form:** When prevention fails or a hazard is detected, interrupt propagation, isolate energy/material/control paths and confirm the intended safe condition.

**Development:** Evolved toward end-to-end state confirmation, periodic proof testing, partial/degraded modes and explicit stop-versus-continue tradeoffs.

**Evolved form in this historical corpus:** Containment is achieved only when the hazardous process state is demonstrably bounded, not when a command is issued.

**Problem:** A stop request or valve command is treated as containment although actuation, isolation integrity or process response is unconfirmed.

**Mechanism:** Define containment objective and time, provide independent actuation/feedback where warranted, test the whole path and restrict operation on degraded protection.

**Trigger and context:** Hazards whose progression can still be bounded after detection and before irreversible loss.

**Preconditions:** Reachable safe/contained state, sufficient time, maintained actuation and feedback, and known interactions with mission/availability.

**Authority and control preconditions:** Controller/operator must have stop authority; restart authority is separate and requires restoration evidence.

**Required feedback:** Command receipt, actuator position, process state, leak/energy isolation, residual inventory and containment integrity.

**Decision or consumer:** Operator, automated protection, emergency response and restart authority.

**Nontrigger or cheaper adequate path:** For a local reversible state, a direct stop and immediate observation may suffice; do not add emergency machinery without a credible propagation path.

**Disposition at the historical freeze:** CONTROL_LOOP_PROPERTY

**Failure modes:** False assumption of fail-safe position, bypasses, inaccessible controls, common utility failure and emergency stop creating a worse hazard.

**Criticism:** HSE safety alerts show nominal safe-position claims can fail physically; fail-safe is not universal where service continuity prevents harm.

**Contrary evidence:** Containment efficacy under novel coupled failures and adversarial conditions can remain uncertain.

**Unresolved questions:** What independent state evidence is necessary when the same failure can impair both actuation and confirmation?

**Property versus ceremony:** Emergency-stop hardware is context-specific; verified propagation control is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S051, S058, S101, S102, S103; critical/contrary: S058, S074.

**Primary source identities:** S051; S058; S101; S102; S103

**Critical source identities:** S058; S074

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/34`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-036"></a>
### ESS-036 — Context-sensitive fail-safe, fail-operational and graceful-degradation design

**Historical origin:** Reliability/system-safety fail-safe design, nuclear/aviation continuity requirements and modern automated-system degradation modes.

**Original form:** Choose whether to stop, continue, isolate or degrade based on which state minimises credible loss under the actual failure and mission context.

**Development:** Evolved from binary fail-safe rules toward hazard-specific degraded envelopes, graceful degradation and explicit transition/recovery assurance.

**Evolved form in this historical corpus:** Select and assure the lowest-loss response for each credible condition, with observable bounded degraded operation and timely recovery.

**Problem:** “Fail safe” is interpreted as always shut down, or availability is prioritised without bounded degraded operation.

**Mechanism:** Define mode-specific safe/degraded envelopes, transition logic, time limits, operator authority and feedback; prove both continuation and stopping hazards.

**Trigger and context:** Systems where stopping and continuing can each be hazardous: aircraft, medical support, nuclear cooling, transport and emergency services.

**Preconditions:** Explicit mission/loss model, reliable mode detection, bounded degraded capability and containment/recovery path.

**Authority and control preconditions:** Automation and operators need defined transition/override authority; degraded operation must have an accountable expiry/recovery owner.

**Required feedback:** Mode, remaining capability, environmental demand, barrier health, time in degraded state and operator comprehension.

**Decision or consumer:** System architect, operator, mission owner and safety authority.

**Nontrigger or cheaper adequate path:** For noncritical reversible functions, stop cleanly and recover normally; elaborate degradation architectures are unnecessary.

**Disposition at the historical freeze:** RETAINED_IN_EVOLVED_FORM

**Failure modes:** Mode confusion, latent degradation, excessive complexity, optimistic remaining-capability estimates and normalisation of temporary modes.

**Criticism:** Continued service can be necessary for safety, but fail-operational complexity and human understanding can introduce new hazards.

**Contrary evidence:** No universal rule resolves competing losses, and complex degradation logic may be hard to validate.

**Unresolved questions:** How should adaptive autonomy explain and bound degraded capability to operators under time pressure?

**Property versus ceremony:** A named “safe state” is not automatically safe across modes; the underlying loss comparison and controlled transition are the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S051, S059, S060, S103; critical/contrary: S058, S089, S090.

**Primary source identities:** S051; S059; S060; S103

**Critical source identities:** S058; S089; S090

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/35`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-037"></a>
### ESS-037 — Recovery, rollback and restart only after restored safety constraints

**Historical origin:** Nuclear operating limits, process isolation/restart, software rollback and through-life system-safety practice.

**Original form:** Separate containment from recovery and restart; restore constraints, configuration and observability before returning to service.

**Development:** Evolved toward explicit recovery states, staged return, rollback assurance, compensating controls and post-restart monitoring.

**Evolved form in this historical corpus:** Recovery is complete only when relevant safety constraints and feedback are re-established and an authorised owner accepts the remaining uncertainty.

**Problem:** Service restoration or command success is treated as proof that the hazard and its causal mechanism are controlled.

**Mechanism:** Define recovery objectives, known-safe configuration, validation/proof tests, staged restart, monitoring and explicit restart authority.

**Trigger and context:** Consequential incidents, emergency stops, failed changes, degraded modes and repairs that can leave latent hazard.

**Preconditions:** Recoverable baseline, rollback compatibility, diagnostic evidence, barrier tests and an escalation path when state is uncertain.

**Authority and control preconditions:** Restart authority must be distinct from the person merely restoring service and able to demand continued restriction.

**Required feedback:** Constraint/barrier status, configuration identity, residual damage, test results, anomaly trend and staged operating feedback.

**Decision or consumer:** Operations, maintenance, release/change authority, incident owner and safety/risk acceptor.

**Nontrigger or cheaper adequate path:** A trivial reversible action can be retried after direct verification; no recovery board is needed.

**Disposition at the historical freeze:** CONTROL_LOOP_PROPERTY

**Failure modes:** Checklist reset, rollback to vulnerable/unsafe configuration, restart pressure, test-induced risk and permanent temporary controls.

**Criticism:** Proof testing can itself be hazardous or incomplete; exact recovery architecture is highly domain specific.

**Contrary evidence:** Generic empirical comparisons of restart criteria are scarce and emergency conditions constrain evidence quality.

**Unresolved questions:** What minimum evidence supports restart when delaying restoration itself creates rising safety harm?

**Property versus ceremony:** A restart checklist is optional; demonstrable restored control and separate authority are not.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S060, S102, S103, S104, S105; critical/contrary: S058, S095.

**Primary source identities:** S060; S102; S103; S104; S105

**Critical source identities:** S058; S095

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/36`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-038"></a>
### ESS-038 — Bounded emergency or temporary risk acceptance with compensating controls

**Historical origin:** Military/aerospace waivers, nuclear technical specifications, process-management-of-change and operational deviation practice.

**Original form:** Permit exceptional operation only within explicit scope, time, configuration and compensating-control limits, with expiry and restoration obligations.

**Development:** Evolved toward machine-visible expiry, exposure budgets, independent monitoring and explicit restoration/re-acceptance criteria.

**Evolved form in this historical corpus:** Exceptional operation is safe enough only within an observable, time/configuration-bounded envelope whose compensating controls and authority remain current.

**Problem:** A temporary deviation silently becomes normal operation, or emergency pressure removes all hazard discrimination.

**Mechanism:** State the impaired control and hazard, select credible compensation, limit exposure/time, monitor conditions, assign expiry and require reauthorisation or restoration.

**Trigger and context:** Urgent mission, repair, emergency change or safety-critical-service continuity where immediate full restoration is impossible.

**Preconditions:** Known hazard/control state, feasible compensation, monitorable envelope, restoration plan and authority commensurate with consequence.

**Authority and control preconditions:** A named emergency/risk authority must own the decision; operators need stop authority if compensation degrades.

**Required feedback:** Time/exposure, compensating-control health, changed conditions, incidents, handoffs and restoration progress.

**Decision or consumer:** Operations, emergency command, maintenance/change owner and residual-risk authority.

**Nontrigger or cheaper adequate path:** Do not create a waiver for trivial work already inside ordinary authority, and do not use temporary acceptance to avoid feasible permanent correction.

**Disposition at the historical freeze:** HIGH_CONSEQUENCE_CONTEXT_PROPERTY

**Failure modes:** Waiver culture, deadline renewal, paper compensations, authority diffusion and production pressure redefining emergencies.

**Criticism:** Temporary acceptance is especially susceptible to normalisation and may externalise harm; some hazards should not be accepted.

**Contrary evidence:** Comparative evidence on waiver governance is limited and emergency decisions may remain ethically contested.

**Unresolved questions:** How should cumulative simultaneous deviations be modelled so individually accepted waivers do not compose into an unsafe state?

**Property versus ceremony:** A waiver form is not the property; bounded exposure, live compensation, expiry and restoration are.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: MODERATE — mechanism is coherent but depends on model scope and assumptions.; ACCIDENT_CASE_STRENGTH: HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S042, S095, S103, S105; critical/contrary: S062, S073.

**Primary source identities:** S012; S042; S095; S103; S105

**Critical source identities:** S062; S073

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/37`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-039"></a>
### ESS-039 — Incident, near-miss and precursor reporting connected to learning

**Historical origin:** Industrial accident reporting, aviation voluntary reporting, healthcare safety reporting and precursor-analysis programmes.

**Original form:** Capture adverse events, close calls and weak signals before severe loss, protect reporting where appropriate and route information to hazard/control decisions.

**Development:** Evolved from incident counting toward protected reporting, precursor/control-state interpretation, causal triage and verified learning loops.

**Evolved form in this historical corpus:** Collect only information with a plausible hazard/control consumer, interpret counts with exposure and incentives, and close the loop through action or justified no-action.

**Problem:** Zero reports are read as zero risk, or reports accumulate without triage, causal analysis, feedback or action.

**Mechanism:** Define safety-relevant reportability, protect good-faith disclosure, prioritise by credible hazard/control degradation, investigate proportionately and feed actions/status back.

**Trigger and context:** Operational systems with sparse severe events, latent failures, weak signals or learning distributed across workers/users.

**Preconditions:** Accessible channel, just reporting conditions, triage competence, hazard linkage and a consumer able to change design or operation.

**Authority and control preconditions:** Reporting recipients require authority or an escalation path; reporters need protection from inappropriate retaliation while reckless conduct remains separately governed.

**Required feedback:** Report volume and exposure denominator, severity/precursor linkage, time to triage/action, repeat events, closure quality and reporter feedback.

**Decision or consumer:** Operations, safety management, designers, regulators/investigators and corrective-action owners.

**Nontrigger or cheaper adequate path:** For an immediately observed trivial defect already corrected and deterministically verified, a lightweight record or no separate report may be appropriate.

**Disposition at the historical freeze:** RETAINED_IN_EVOLVED_FORM

**Failure modes:** Reporting quotas, count-based culture metrics, duplicate low-value reports, confidentiality barriers, underreporting and recommendation inflation.

**Criticism:** Near-miss counts are strongly incentive- and exposure-dependent; not every near miss predicts catastrophe and reporting alone does not improve safety.

**Contrary evidence:** Comparative evidence for specific reporting schemes is mixed and sparse-event signal validity is limited.

**Unresolved questions:** How can reporting systems distinguish rising hazard exposure from healthier reporting behaviour without suppressing either?

**Property versus ceremony:** A reporting portal is not the property; observable weak signals, protected transmission and decision closure are.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: MODERATE — mechanism is coherent but depends on model scope and assumptions.; ACCIDENT_CASE_STRENGTH: HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S076, S078, S079, S080, S097, S116; critical/contrary: S071, S072.

**Primary source identities:** S076; S078; S079; S080; S097; S116

**Critical source identities:** S071; S072

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/38`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-040"></a>
### ESS-040 — Multi-factor causal investigation grounded in local rationality

**Historical origin:** Human-factors critique of “human error”, Reason/local-rationality work, systems accident models and modern RCA reforms.

**Original form:** Reconstruct how technical, human, organisational and environmental conditions made actions locally reasonable and combined into loss.

**Development:** Evolved from single-cause RCA toward multiple interacting mechanisms, local rationality, control deficiencies and action-centred RCA².

**Evolved form in this historical corpus:** Investigate until the credible causal mechanisms needed to select and verify controls are sufficiently discriminated, without treating error labels as explanations.

**Problem:** Investigation stops at operator error, one root cause or rule violation and therefore controls only the last visible act.

**Mechanism:** Preserve evidence, build competing causal scenarios, test counterfactual control changes, distinguish contributing mechanisms and stop when additional evidence no longer changes action.

**Trigger and context:** Serious incidents, recurring near misses and unexplained control/interaction failures.

**Preconditions:** Timely access to technical/organisational evidence, multidisciplinary competence and separation between learning and inappropriate punishment.

**Authority and control preconditions:** Investigators need independence and access; organisations must empower consumers to change upstream controls rather than only retrain operators.

**Required feedback:** Timeline/state reconstruction, alternative explanations, missing/stale feedback, goal conflicts, control deficiencies, action implementation and recurrence.

**Decision or consumer:** Investigator, design/operations authority, regulator and corrective-action owner.

**Nontrigger or cheaper adequate path:** A simple, directly observed and deterministically reproducible defect can be corrected without an elaborate sociotechnical investigation.

**Disposition at the historical freeze:** SOCIO_TECHNICAL_CONTEXT_PROPERTY

**Failure modes:** Infinite causal chains, fashionable systems diagrams, weak counterfactuals, no root prioritisation and recommendations beyond available evidence.

**Criticism:** Systems analyses remain judgement-sensitive; “no root cause” must not become refusal to identify controllable mechanisms or accountability.

**Contrary evidence:** Comparative evidence that one systems method yields better prevention than another remains limited and retrospective causal claims are vulnerable to hindsight.

**Unresolved questions:** What stopping rule best balances additional causal discrimination against post-hoc narrative growth and delayed action?

**Property versus ceremony:** A specific RCA diagram is optional; evidence-preserving causal discrimination and action linkage are the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: MODERATE — mechanism is coherent but depends on model scope and assumptions.; ACCIDENT_CASE_STRENGTH: HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S063, S064, S076, S077, S109, S110; critical/contrary: S066, S107.

**Primary source identities:** S063; S064; S076; S077; S109; S110

**Critical source identities:** S066; S107

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/39`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-041"></a>
### ESS-041 — Corrective-action ownership, implementation and effectiveness verification

**Historical origin:** Accident-investigation recommendation systems and RCA² reform of analysis without action.

**Original form:** Convert a causal finding into a hazard-relevant action with a responsible owner, due state, implementation evidence and effectiveness/recurrence check.

**Development:** Evolved from report issuance toward SMARTER causal actions, public status classification, implementation verification and outcome/precursor monitoring.

**Evolved form in this historical corpus:** No safety finding is closed merely by documentation: close the causal-control loop or explicitly record why no further action has decision value.

**Problem:** An investigation or recommendation is counted as closed when issued, accepted, trained or documented rather than when the causal control improves.

**Mechanism:** For each material mechanism, specify the control change and expected indicator, assign authority/resources, verify implementation, test effectiveness and monitor recurrence/side effects.

**Trigger and context:** Material incidents, recurring precursors, audit findings and accepted safety recommendations.

**Preconditions:** Causal mechanism sufficiently understood, feasible action, named empowered owner, current configuration and measurable verification condition.

**Authority and control preconditions:** The owner must control resources/design/operations or have escalation; the investigator should not declare effectiveness solely from paperwork.

**Required feedback:** Implementation evidence, changed control performance, recurrence/precursors, side effects, overdue status and reason for closure.

**Decision or consumer:** Design/operations management, regulator/investigator, safety board and affected workforce/users.

**Nontrigger or cheaper adequate path:** For a trivial directly fixed defect, the repair plus decisive regression check can close the action without a separate tracker.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Recommendation proliferation, weak “retrain/rewrite” actions, closure gaming, orphaned recommendations and unmeasured displacement of risk.

**Criticism:** Effectiveness is hard to infer for rare events; absence of recurrence over short exposure is weak evidence.

**Contrary evidence:** Public closure classifications may still measure correspondence rather than actual loss reduction.

**Unresolved questions:** What evidence is sufficient to close an action when the target accident is too rare for direct recurrence statistics?

**Property versus ceremony:** An action database is optional; an empowered consumer and verified causal effect are not.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: MODERATE — mechanism is coherent but depends on model scope and assumptions.; ACCIDENT_CASE_STRENGTH: HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S076, S078, S079, S093, S115; critical/contrary: S071, S072.

**Primary source identities:** S076; S078; S079; S093; S115

**Critical source identities:** S071; S072

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/40`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-042"></a>
### ESS-042 — Leading indicators tied to explicit hazards and control performance

**Historical origin:** Process-safety precursor analysis, nuclear maintenance monitoring, organisational migration models and resilience-oriented monitoring.

**Original form:** Monitor conditions that causally bear on barrier, control, assumption or exposure state before lagging loss occurs.

**Development:** Evolved from lagging counts toward hazard-specific control-health and assumption indicators with explicit consumers and periodic validation.

**Evolved form in this historical corpus:** A leading indicator is retained only when its causal relevance, denominator, decision threshold and consumer remain credible.

**Problem:** Generic activity counts, safety-culture scores or injury rates are treated as proof that high-consequence controls work.

**Mechanism:** Derive a small set of indicators from the hazard/control model, state expected direction and threshold, validate against operations and pair every threshold with a decision.

**Trigger and context:** Sparse-event, latent-failure or slowly degrading systems where incident rates provide delayed or statistically weak feedback.

**Preconditions:** Explicit causal hypothesis, reliable data and exposure denominator, stable semantics and authorised response.

**Authority and control preconditions:** An owner must be able to inspect, restrict, maintain or redesign on adverse trends and to retire misleading indicators.

**Required feedback:** Barrier availability, overdue proof tests, excursions, workload/override patterns, weak signals, exposure and decision response.

**Decision or consumer:** Operations, maintenance, safety management and risk authority.

**Nontrigger or cheaper adequate path:** Use direct control-state inspection when available; do not create proxy metrics where a deterministic discriminator already answers the question.

**Disposition at the historical freeze:** USEFUL_BUT_EASILY_GAMED

**Failure modes:** Metric fixation, target manipulation, false reassurance, excessive alerting and treating correlation as causation.

**Criticism:** Evidence linking broad culture/leading scores to accident prevention is mixed; indicators are model-dependent and can be gamed.

**Contrary evidence:** Comparative predictive validity is usually domain-specific and rare-event calibration remains weak.

**Unresolved questions:** How should indicator sets be validated and pruned without waiting for catastrophic outcomes?

**Property versus ceremony:** A KPI dashboard is not a property; timely control-state information that changes action is.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: MODERATE — mechanism is coherent but depends on model scope and assumptions.; ACCIDENT_CASE_STRENGTH: HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S062, S097, S104; critical/contrary: S071, S072, S074.

**Primary source identities:** S062; S097; S104

**Critical source identities:** S071; S072; S074

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/41`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-043"></a>
### ESS-043 — Organisational control, incentives and production-pressure analysis

**Historical origin:** Major accident investigations, Rasmussen boundary migration, high-reliability studies and systems accident models.

**Original form:** Treat budgets, schedules, staffing, communication, authority, contracting and performance pressures as parts of the safety control structure.

**Development:** Evolved from “safety culture” exhortation toward observable control, incentive, resource, feedback and authority mechanisms.

**Evolved form in this historical corpus:** Analyse and change the upstream decisions and feedback loops that shape risk, while retaining named accountability for controllable choices.

**Problem:** Safety is delegated to frontline compliance while upstream decisions systematically weaken barriers, suppress evidence or reward risk-taking.

**Mechanism:** Map decision/control paths and incentives, identify where authority and safety information diverge, install escalation/stop rights and monitor boundary migration.

**Trigger and context:** Complex organisations, outsourced supply chains, long operations, high schedule pressure and hazards spanning multiple management levels.

**Preconditions:** Access to real work and decision data, leadership willingness to expose tradeoffs, protected reporting and feasible upstream controls.

**Authority and control preconditions:** Leaders controlling resources and priorities must own safety consequences; frontline responsibility requires matching authority.

**Required feedback:** Staffing/workload, deferred maintenance, waivers, schedule overrides, unresolved findings, reporting quality, barrier health and escalation outcomes.

**Decision or consumer:** Executives, programme/operations management, regulators, workforce and system safety.

**Nontrigger or cheaper adequate path:** Do not invent culture programmes for a simple local technical defect; correct the direct mechanism and verify it.

**Disposition at the historical freeze:** SOCIO_TECHNICAL_CONTEXT_PROPERTY

**Failure modes:** Vague culture rhetoric, retrospective moralising, endless organisational diagrams and accountability dilution.

**Criticism:** Organisational causation is difficult to quantify and broad systems explanations can obscure specific decision responsibility.

**Contrary evidence:** Causal attribution across levels can become unfalsifiable, and “system blame” can improperly erase individual misconduct or competence duties.

**Unresolved questions:** How can organisational safety controls be evaluated prospectively without reducing them to gameable culture scores?

**Property versus ceremony:** A culture survey or values statement is not the property; decision-relevant organisational control is.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: MODERATE — mechanism is coherent but depends on model scope and assumptions.; ACCIDENT_CASE_STRENGTH: HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S062, S065, S067, S081, S082, S085, S087, S091; critical/contrary: S066, S071, S072.

**Primary source identities:** S062; S065; S067; S081; S082; S085; S087; S091

**Critical source identities:** S066; S071; S072

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/42`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-044"></a>
### ESS-044 — Supplier and contractor boundary assurance with change notification

**Historical origin:** Defence/aerospace system-safety programmes, medical-device supply control, nuclear modification and process contractor management.

**Original form:** Preserve safety requirements, assumptions, evidence, configuration identity and notification duties across organisational boundaries.

**Development:** Evolved toward risk-tiered supplier assurance, software bills/provenance, continuous notification and integration-focused evidence reuse.

**Evolved form in this historical corpus:** Match supplier assurance to system consequence and interface uncertainty, but keep the integrator responsible for composed safety.

**Problem:** The integrator assumes supplier compliance establishes system safety, or a supplier changes a safety-relevant component/process without impact analysis.

**Mechanism:** Allocate hazard-linked obligations and interface assumptions, require evidence and change/anomaly notification, verify integration and retain integrator accountability.

**Trigger and context:** Safety-relevant purchased software/hardware, outsourced operations/maintenance and multi-tier supply chains.

**Preconditions:** Clear technical/contract boundary, component criticality, integration testability, configuration provenance and enforceable notification terms.

**Authority and control preconditions:** The integrator must retain system-level acceptance authority; suppliers need authority/resources to disclose and correct defects.

**Required feedback:** Supplier versions, deviations, anomalies, process/evidence changes, interface conformance and field performance.

**Decision or consumer:** Integrator, supplier quality/safety, procurement, configuration/change authority and operator.

**Nontrigger or cheaper adequate path:** Commodity low-consequence components with a decisive acceptance test can use that test rather than imposing a full supplier safety system.

**Disposition at the historical freeze:** HIGH_CONSEQUENCE_CONTEXT_PROPERTY

**Failure modes:** Flow-down paperwork, supplier scorecards, proprietary evidence dead ends, duplicated audits and false transfer of responsibility.

**Criticism:** Contracts cannot reveal unknown interactions or guarantee candour; excessive requirements can reduce supplier diversity and agility.

**Contrary evidence:** Opaque AI/cloud suppliers and continuous service changes may defeat traditional configuration and evidence access.

**Unresolved questions:** What minimum evidence and contract rights make third-party adaptive services auditable without requiring full internal disclosure?

**Property versus ceremony:** A supplier certificate is not the property; current boundary evidence, notification and integration control are.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S027, S029, S042, S052, S054, S055; critical/contrary: S048, S095.

**Primary source identities:** S012; S027; S029; S042; S052; S054; S055

**Critical source identities:** S048; S095

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/43`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-045"></a>
### ESS-045 — Operational monitoring and adaptive safety-envelope governance

**Historical origin:** Operational limits, dynamic risk monitoring, resilience engineering and continuous assurance.

**Original form:** Monitor whether operation remains inside validated safety constraints and adapt restrictions or assurance when environment, demand or performance changes.

**Development:** Evolved toward runtime assurance, explicit operational design domains, dynamic cases and bounded adaptive control rather than unrestricted flexibility.

**Evolved form in this historical corpus:** Permit adaptation only inside an observable, hazard-linked and authority-bounded envelope, with fallback and change-aware re-assurance.

**Problem:** Certification-time assumptions remain fixed while operations migrate, or adaptive response changes behaviour without bounded authority/evidence.

**Mechanism:** Define observable envelope variables and assumptions, detect excursions, restrict/degrade or learn within authorised bounds, and re-assure material adaptations.

**Trigger and context:** Long-lived, variable-environment, autonomous or rapidly updated systems where predeployment evidence cannot cover all operational states.

**Preconditions:** Validated envelope, trustworthy telemetry, anomaly/assumption monitors, safe fallback and authority to intervene or revise constraints.

**Authority and control preconditions:** Operations must have stop/degrade authority; adaptation outside the assured envelope requires explicit change/risk authority.

**Required feedback:** Envelope variables, assumption validity, control effectiveness, anomalies, drift, exposure and recovery performance.

**Decision or consumer:** Operator, autonomy supervisor, safety case owner, release authority and regulator.

**Nontrigger or cheaper adequate path:** Stable bounded systems with direct deterministic protection may only need periodic checks; continuous dashboards are unnecessary.

**Disposition at the historical freeze:** CONTEXT_DEPENDENT

**Failure modes:** Monitoring theatre, alert overload, unsafe online experimentation, proxy drift and adaptation masking deteriorating margins.

**Criticism:** Resilience concepts can be vague and monitoring cannot guarantee discovery of unknown hazards; intervention itself can destabilise service.

**Contrary evidence:** Adaptive envelopes may be difficult to specify for open-world autonomy and can shift burden to operators.

**Unresolved questions:** How can runtime evidence update assurance without circularly treating the system’s own fallible telemetry as proof of safety?

**Property versus ceremony:** “Resilience” language or a dashboard is not enough; explicit constraints, feedback, decisions and limits are required.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S047, S055, S062, S069, S070, S098, S103, S104; critical/contrary: S070, S111.

**Primary source identities:** S047; S055; S062; S069; S070; S098; S103; S104

**Critical source identities:** S070; S111

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/44`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-046"></a>
### ESS-046 — Cheap authoritative discriminator for low-consequence reversible work

**Historical origin:** Tailoring provisions in mature aerospace/system-safety guidance and goal-setting, risk-informed regulation; synthesized anti-bureaucracy property.

**Original form:** When a narrow, deterministic and authoritative check settles a local safety question, use it directly and escalate only on failed assumptions or wider consequence.

**Development:** Evolved from blanket exemptions toward explicit non-trigger conditions, bounded delegation and automatic escalation on uncertainty/coupling.

**Evolved form in this historical corpus:** Use the least costly discriminator that conclusively controls the credible loss; never perform a safety ritual solely because its template exists.

**Problem:** Full hazard-analysis, assurance-case and review machinery is applied despite zero expected decision value, consuming attention and provoking bypass.

**Mechanism:** Classify consequence and scope, apply the decisive test/guard, record only necessary identity/result, and define escalation triggers for ambiguity or coupling.

**Trigger and context:** Local, cheap, reversible, immediately observable work with stable assumptions and an authoritative deterministic discriminator.

**Preconditions:** The discriminator actually covers the safety question, the result is observable and rollback/containment remains available.

**Authority and control preconditions:** Ordinary engineering authority may act within bounded delegation; anyone detecting scope expansion can escalate.

**Required feedback:** Check result, exact local configuration, rollback success if used and evidence that assumptions did not widen.

**Decision or consumer:** Engineer/operator, change authority and safety function defining the tailoring boundary.

**Nontrigger or cheaper adequate path:** This property is itself the cheap path; it does not apply when consequence, irreversibility, coupling, latent effects or uncertain interactions are material.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Under-classification, calling uncertain work “reversible”, hidden propagation and using cheap path to evade inconvenient scrutiny.

**Criticism:** Tailoring can be gamed and no deterministic check is authoritative outside its proven scope.

**Contrary evidence:** Direct empirical comparison of tailoring policies is limited and under-control risk depends on classification quality.

**Unresolved questions:** What simple scope tests best detect when apparently local reversible work can propagate into a consequential interaction?

**Property versus ceremony:** No special artefact is required beyond sufficient evidence of scope, result and escalation conditions.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S029, S035, S098; critical/contrary: S038, S073, S074.

**Primary source identities:** S029; S035; S098

**Critical source identities:** S038; S073; S074

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/45`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-047"></a>
### ESS-047 — Retirement of controls whose hazard or decision consumer has disappeared

**Historical origin:** Living assurance, management of change, alarm rationalisation and adaptive safety-management practice.

**Original form:** Periodically remove, merge or redesign a control, alarm, metric or artefact when its hazard, causal mechanism, assumption or authorised consumer no longer exists.

**Development:** Evolved toward expiry metadata, consumer/use telemetry, periodic rationalisation and change-aware decommissioning.

**Evolved form in this historical corpus:** Retain a safety control only while a current hazard/decision link and justified expected value remain; remove it with the same causal discipline used to add it.

**Problem:** Legacy controls accumulate indefinitely, obscure live hazards, conflict with current work and are preserved because removal itself is procedurally difficult.

**Mechanism:** Require each control to retain a hazard/constraint link, owner, consumer and effectiveness signal; decommission through impact analysis and verify no residual dependency.

**Trigger and context:** Long-lived systems with substantial change, accumulated waivers, alarms, checklists, reports or certification artefacts.

**Preconditions:** Current hazard/configuration model, evidence of non-use or replacement, dependency analysis and authority to remove safely.

**Authority and control preconditions:** The control owner and affected risk/operations authority must approve removal; users need a path to reveal hidden dependence.

**Required feedback:** Consumer use, action triggered, false-positive/bypass burden, control effectiveness, dependencies and post-retirement anomalies.

**Decision or consumer:** Control owner, operator, assurance/change authority and affected decision consumer.

**Nontrigger or cheaper adequate path:** Do not run a retirement review for a transient local check that naturally ends with the task.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Premature removal, undocumented informal dependence, metric gaming and “cleanup” that erases historical evidence.

**Criticism:** Absence of recent activation may reflect successful prevention or rare demand, not obsolescence.

**Contrary evidence:** Rare-demand controls can look unused, so retirement requires hazard analysis rather than activity counts.

**Unresolved questions:** How should organisations distinguish genuinely obsolete controls from dormant barriers protecting rare catastrophic states?

**Property versus ceremony:** A control register is optional; live ownership, consumer and retirement logic are the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S042, S047, S075, S095; critical/contrary: S071, S074.

**Primary source identities:** S042; S047; S075; S095

**Critical source identities:** S071; S074

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/46`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-048"></a>
### ESS-048 — Live decision consumer for every safety artefact and control

**Historical origin:** System-safety programme management, safety-case practice and criticism of recommendation/paper assurance.

**Original form:** Create and maintain a safety artefact only when a named person/process uses it to design, accept, operate, stop, recover or learn.

**Development:** Evolved from deliverable compliance toward decision-first assurance, machine-linked traceability and consumer/expiry tests.

**Evolved form in this historical corpus:** Every artefact must earn existence through a current or credibly latent consequential decision and an owner who can act on it.

**Problem:** Hazard logs, matrices, reports, models and reviews are produced for compliance without changing any authorised decision.

**Mechanism:** State the decision, consumer, trigger and required information before producing the artefact; observe use and retire or redesign if it does not change action.

**Trigger and context:** Any recurring safety analysis, review, metric, report, case or control.

**Preconditions:** Real decision need, current evidence, accessible representation and consumer authority.

**Authority and control preconditions:** The consumer must be able to act or escalate; the producer cannot substitute document delivery for control.

**Required feedback:** Decision made, challenge raised, action/acceptance changed, use frequency, stale age and unresolved consumer feedback.

**Decision or consumer:** Designer, operator, risk acceptor, reviewer/investigator and regulator.

**Nontrigger or cheaper adequate path:** Do not create a separate artefact when the decisive information is already embedded in an authoritative engineering/operational control.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Artificially naming a consumer, rubber-stamp use, hidden secondary consumers and deleting records needed for future learning.

**Criticism:** Some assurance artefacts serve latent legal/public accountability and rare future decisions, so immediate use alone is not sufficient.

**Contrary evidence:** Direct empirical measurement of artefact decision value is sparse and public-accountability value may be delayed.

**Unresolved questions:** How should latent regulatory, legal and intergenerational consumers be represented without preserving every obsolete artefact forever?

**Property versus ceremony:** No document format is required; durable current decision information is.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S042, S044, S078, S079; critical/contrary: S048, S107.

**Primary source identities:** S012; S042; S044; S078; S079

**Critical source identities:** S048; S107

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/47`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-049"></a>
### ESS-049 — Hazard-control hierarchy favouring elimination and engineered control

**Historical origin:** Industrial hygiene/occupational safety hierarchy, military system-safety design order and standards safety principles.

**Original form:** Prefer elimination, substitution, inherently safer design and engineered prevention before warnings, procedures, training or personal response where feasible.

**Development:** Evolved from slogans toward hazard-specific option analysis, prevention-through-design and monitored combinations.

**Evolved form in this historical corpus:** Eliminate or physically constrain credible hazards where practicable; justify reliance on weaker human/procedural layers and analyse the hazards controls create.

**Problem:** Administrative controls are accepted because they are cheap to document even though the hazard can be designed out or physically bounded.

**Mechanism:** Search controls in strength order, document why stronger options are infeasible or harmful, and monitor residual lower-level controls.

**Trigger and context:** Identified hazards with feasible design, substitution, guarding, interlock, isolation or exposure-reduction options.

**Preconditions:** Early design influence, feasible alternatives, system-level tradeoff analysis and authority/resources to change architecture.

**Authority and control preconditions:** Design/risk authority must be able to reject administrative substitution for feasible engineering control.

**Required feedback:** Hazard presence, barrier demand, human/procedural dependence, bypass, exposure and side effects of stronger controls.

**Decision or consumer:** Designer, operations, occupational/process safety and risk acceptor.

**Nontrigger or cheaper adequate path:** No hierarchy exercise is needed when the hazard is absent or a simple direct constraint already eliminates it.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Rigid hierarchy that ignores mission/secondary risk, “elimination” shifting hazard elsewhere and engineered controls with hidden common modes.

**Criticism:** No control class is infallible; engineered automation can create interaction hazards and fail-operational contexts complicate the order.

**Contrary evidence:** Over-automated engineered controls can create mode, feedback and availability hazards.

**Unresolved questions:** When does an engineered automatic control create more system risk than a well-supported human/procedural control?

**Property versus ceremony:** A hierarchy poster is ceremony; actual design-option search and justified residual dependence are the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S033, S034, S094; critical/contrary: S058, S073.

**Primary source identities:** S012; S033; S034; S094

**Critical source identities:** S058; S073

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/48`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-050"></a>
### ESS-050 — Safety margins, operating envelopes and boundary separation

**Historical origin:** Structural/aerospace margins, nuclear operating limits, process safe operating envelopes and Rasmussen boundary models.

**Original form:** Maintain measurable separation between normal operation and hazardous thresholds, including uncertainty, degradation and response time.

**Development:** Evolved toward multidimensional envelopes, real-time margin monitoring, explicit uncertainty and change-controlled allocation.

**Evolved form in this historical corpus:** Maintain enough observable separation from hazardous boundaries to absorb credible uncertainty and response latency, while revising limits when evidence changes.

**Problem:** Operation is permitted exactly at a nominal limit, or a margin is treated as static despite model error, ageing, environment and coupling.

**Mechanism:** Define hazard-linked limits and uncertainty allowance, instrument relevant variables, restrict excursions and reassess margins after change/degradation.

**Trigger and context:** High-energy, structural, thermal, control or capacity hazards with identifiable boundaries and cliff-edge consequences.

**Preconditions:** A credible boundary model, calibrated measurement, operational authority and recovery/containment before limit crossing.

**Authority and control preconditions:** Operators/controllers must be able to reduce demand, stop or degrade; change authority owns margin allocation.

**Required feedback:** Distance to limit, uncertainty, rate of approach, ageing/degradation, excursions, recovery time and barrier availability.

**Decision or consumer:** Architect, operator, maintenance, regulator and risk authority.

**Nontrigger or cheaper adequate path:** For a low-consequence reversible state with immediate deterministic feedback, ordinary tolerance checks may suffice.

**Disposition at the historical freeze:** HIGH_CONSEQUENCE_CONTEXT_PROPERTY

**Failure modes:** Arbitrary factors, margin hoarding, false precision, hidden multidimensional boundaries and workarounds around over-conservative limits.

**Criticism:** Margins can mask design weakness or reduce necessary service; not all sociotechnical hazards have a scalar boundary.

**Contrary evidence:** Complex interactions may create moving or unknown boundaries, and excessive margins can create mission/availability harms.

**Unresolved questions:** How should safety envelopes represent interacting dimensions and model uncertainty without becoming unusably conservative?

**Property versus ceremony:** A fixed safety factor is domain-specific; controlled separation and margin evidence are the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S040, S056, S062, S103, S105; critical/contrary: S068, S073.

**Primary source identities:** S040; S056; S062; S103; S105

**Critical source identities:** S068; S073

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/49`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-051"></a>
### ESS-051 — Explicit assumption validity and monitoring

**Historical origin:** Safety cases, STPA process models, change assessment and dynamic risk/continuous assurance.

**Original form:** Make decision-critical assumptions about environment, interfaces, users, independence, data, demand and controls explicit and monitor or revalidate them.

**Development:** Evolved from contextual footnotes toward critical-assumption ownership, runtime monitors and automatic change/assurance triggers.

**Evolved form in this historical corpus:** A safety claim is valid only while its material assumptions are evidenced; monitor the few premises whose failure can change control or acceptance.

**Problem:** Evidence remains apparently valid after an unstated premise changes or was never true in operation.

**Mechanism:** Identify claim-critical assumptions, assign evidence/owner/validity period, monitor observable ones and trigger restriction or reassessment on violation.

**Trigger and context:** Novel, changing, autonomous, outsourced or environment-sensitive systems and any reused safety evidence.

**Preconditions:** Claim/hazard model, observable discriminators or periodic revalidation, configuration linkage and action authority.

**Authority and control preconditions:** Assumption owners and operators must be able to restrict use, escalate or change the case when validity is uncertain.

**Required feedback:** Premise status, environmental range, interface/provider behaviour, data drift, independence evidence and violations.

**Decision or consumer:** Safety case owner, system architect, operations, supplier and change authority.

**Nontrigger or cheaper adequate path:** Do not create a register for obvious transient facts already enforced by a deterministic check; record only assumptions whose failure changes a decision.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Assumption-log bloat, tautologies, unmonitorable claims, green dashboards from correlated telemetry and no response to violation.

**Criticism:** Unknown unknowns remain outside the register and monitoring can be circular or lagging.

**Contrary evidence:** Complete assumption elicitation is impossible and monitors may not be independent of the system they supervise.

**Unresolved questions:** How can critical assumptions be ranked and independently monitored without reproducing the entire safety case at runtime?

**Property versus ceremony:** An assumption spreadsheet is optional; explicit, current and actionable premise state is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S018, S042, S044, S047, S052, S055, S062; critical/contrary: S048, S070.

**Primary source identities:** S018; S042; S044; S047; S052; S055; S062

**Critical source identities:** S048; S070

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/50`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-052"></a>
### ESS-052 — Durable current hazard, constraint and decision state

**Historical origin:** Military/aerospace hazard tracking, process hazard records and safety-case/hazard-log practice.

**Original form:** Preserve each material hazard, causal scenarios, controls/constraints, evidence, owner, residual decision and current status across the lifecycle.

**Development:** Evolved toward model-linked, configuration-aware, consumer-driven hazard/constraint state with automated staleness and orphan checks.

**Evolved form in this historical corpus:** Preserve current decision-relevant hazard/control memory in any implementation that exposes ownership, evidence, assumptions, change and residual acceptance.

**Problem:** Hazards are repeatedly rediscovered, lost at handoff or marked closed while controls/evidence/configuration change.

**Mechanism:** Maintain the minimum durable state needed to understand current hazard/control/acceptance closure; update through change and retire obsolete entries explicitly.

**Trigger and context:** Long-lived, multi-team or regulated systems and hazards requiring multiple controls/decisions over time.

**Preconditions:** Clear semantics, ownership, configuration identity, change triggers and a live decision consumer.

**Authority and control preconditions:** Hazard/control owners and acceptance authority must be named; unresolved hazards cannot disappear through administrative closure.

**Required feedback:** Control/evidence status, owner/acceptance, configuration, open scenarios, incidents, changes and review/expiry dates.

**Decision or consumer:** System safety, design/change authority, operator, assessor and risk acceptor.

**Nontrigger or cheaper adequate path:** A local ephemeral hazard fully eliminated and verified can be recorded in the ordinary work item; a dedicated log is unnecessary.

**Disposition at the historical freeze:** USEFUL_BUT_EASILY_BUREAUCRATISED

**Failure modes:** Hazard-log bureaucracy, entry count as quality, stale closure, generic hazards, duplicate analysis and detached spreadsheets.

**Criticism:** No log establishes hazard completeness or control effectiveness; it can become a powerful compliance theatre.

**Contrary evidence:** Comparative evidence for hazard-log tooling is weak and completeness cannot be validated by entry volume.

**Unresolved questions:** What compact state model preserves decision memory without turning every minor concern into a permanent hazard record?

**Property versus ceremony:** A spreadsheet or prescribed schema is not required; durable current semantic state is.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.; ACCIDENT_CASE_STRENGTH: HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S042, S047, S095; critical/contrary: S048, S107.

**Primary source identities:** S012; S042; S047; S095

**Critical source identities:** S048; S107

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/51`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-053"></a>
### ESS-053 — Integrated verification that a safety control achieves the intended state

**Historical origin:** System test/IV&V, functional-safety verification, control-theoretic feedback and end-to-end protection testing.

**Original form:** Verify the full path from hazard trigger through controller/action/interface/actuation/process response/feedback, not only each component or command.

**Development:** Evolved toward scenario/model-based end-to-end verification, hardware/software-in-the-loop, operational monitoring and claim-linked evidence.

**Evolved form in this historical corpus:** A control is accepted only when current evidence shows that it drives and maintains the intended safe process state under relevant conditions.

**Problem:** Every component passes its own test while the composed control fails in timing, units, mode, authority or physical effect.

**Mechanism:** Derive end-to-end acceptance criteria from the safety constraint, exercise representative normal/fault/transition scenarios and confirm physical/system state.

**Trigger and context:** Consequential interlocks, shutdown, autonomous control, recovery and multi-component protective functions.

**Preconditions:** Testable state criteria, representative configuration/environment, safe test containment and independent observation where warranted.

**Authority and control preconditions:** Verification authority needs access across component/organisational boundaries and power to block acceptance.

**Required feedback:** Trigger, command, timing, actuation, process state, feedback semantics, degraded modes and post-control stability.

**Decision or consumer:** Integrator, operator, verifier/IV&V, safety case owner and acceptance authority.

**Nontrigger or cheaper adequate path:** A single local direct test suffices when the control path is simple, fully observable and reversible.

**Disposition at the historical freeze:** CONTROL_LOOP_PROPERTY

**Failure modes:** Unsafe testing, unrepresentative simulation, test-only instrumentation, excessive scenario sets and confusing test completion with field assurance.

**Criticism:** Testing cannot cover all interactions and formal/model evidence is still needed for rare or dangerous states.

**Contrary evidence:** Representative integrated testing can be expensive, hazardous or incomplete, especially for catastrophic rare states.

**Unresolved questions:** How should simulation, formal proof, fault injection and operational evidence be combined to justify end-to-end control effectiveness?

**Property versus ceremony:** A test report is not the property; hazard-linked state achievement and feedback confirmation are.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S018, S049, S058, S099, S100, S102; critical/contrary: S050, S074.

**Primary source identities:** S018; S049; S058; S099; S100; S102

**Critical source identities:** S050; S074

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/52`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-054"></a>
### ESS-054 — Safety management of lifecycle transitions and temporary configurations

**Historical origin:** Military system-safety lifecycle programmes, nuclear commissioning/decommissioning and process modification/start-up practice.

**Original form:** Analyse and control hazards unique to assembly, installation, commissioning, migration, maintenance, start-up, shutdown and decommissioning.

**Development:** Evolved toward explicit transitional configurations, integrated readiness evidence, staged cutover, rollback and decommissioning hazard closure.

**Evolved form in this historical corpus:** Treat every materially different lifecycle state as a real system configuration with its own hazards, controls, feedback and authorised exit criteria.

**Problem:** Only steady-state operation is assured although temporary configurations remove barriers, alter authority and create nonroutine interfaces.

**Mechanism:** Define transition states and hazards, sequence controls, temporary barriers/authority, hold points, configuration verification and exit/recovery criteria.

**Trigger and context:** High-consequence installation, major upgrade, migration, maintenance outage, commissioning or decommissioning.

**Preconditions:** Transition plan/state model, temporary configuration identity, competent coordination and restoration/rollback path.

**Authority and control preconditions:** A transition controller must have cross-boundary authority and explicit handoff/hold-point release; normal operations authority may be insufficient.

**Required feedback:** Temporary configuration, barrier availability, sequence/hold point, personnel/authority, tests, residual energy/material and exit criteria.

**Decision or consumer:** Project/commissioning manager, operator, maintenance, supplier/contractor and safety authority.

**Nontrigger or cheaper adequate path:** Routine local reversible transitions with an established direct check use the ordinary procedure and observation.

**Disposition at the historical freeze:** HIGH_CONSEQUENCE_CONTEXT_PROPERTY

**Failure modes:** Plan ceremony, excessive hold points, outdated procedures, transition fatigue and informal workarounds caused by impractical sequencing.

**Criticism:** Transition models can be incomplete and over-control can prolong exposure to a temporary hazardous state.

**Contrary evidence:** Additional hold points can increase time in vulnerable configurations and may be bypassed under schedule pressure.

**Unresolved questions:** How should transition assurance minimise both premature progression and prolonged exposure to temporary risk?

**Property versus ceremony:** A commissioning checklist is domain-specific; controlled transitional-state reasoning is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — origin and transmission are documented in primary or authoritative historical sources.; FORMAL_OR_MODEL_STRENGTH: HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.; ACCIDENT_CASE_STRENGTH: MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.; EMPIRICAL_COMPARATIVE_STRENGTH: LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.; DOMAIN_PRACTICE_STRENGTH: HIGH — established in mature high-consequence practice when properly scoped.; STANDARD_OR_REGULATORY_STRENGTH: HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.; TRANSFERABILITY_STRENGTH: MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.; ASSUMPTION_SENSITIVITY: HIGH — value depends on boundary, model, data, authority, independence and current configuration.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — implementation failures and scope critiques materially constrain use.; SOURCE_BASIS: Primary: S012, S054, S060, S095, S103; critical/contrary: S058, S073.

**Primary source identities:** S012; S054; S060; S095; S103

**Critical source identities:** S058; S073

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/53`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-055"></a>
### ESS-055 — Risk-matrix cell treated as objective risk or sufficient decision evidence

**Historical origin:** Later administrative simplification of qualitative/semiquantitative risk assessment; not the whole historical risk-analysis tradition.

**Original form:** Assign ordinal severity and likelihood categories, often multiply or combine them, colour a cell and treat its rank as the risk.

**Development:** Later practice increasingly treats matrices as limited aids, supplements them with uncertainty and consequence constraints, or replaces them.

**Evolved form in this historical corpus:** NO_GENERAL_PROPERTY in the claim that a matrix score is risk; retain explicit, uncertainty-aware and decision-linked risk representation instead.

**Problem:** The matrix suppresses uncertainty, dependence, exposure and category sensitivity while authorising consequential decisions.

**Mechanism:** Reject the cell as truth; preserve only the weaker property of explicit consequence/uncertainty discrimination and use a representation matched to the decision.

**Trigger and context:** At most as a transparent workshop prompt or coarse triage aid where rankings are not treated as quantitative or dispositive.

**Preconditions:** Users must understand the representation limits, disclose category choices and retain authority to override rankings.

**Authority and control preconditions:** No authority should accept catastrophic residual risk solely from a colour or product score.

**Required feedback:** Sensitivity to bins, uncertainty, exposure denominator, dependence and whether the ranking changes under plausible alternatives.

**Decision or consumer:** Risk analyst, decision owner and workshop participants.

**Nontrigger or cheaper adequate path:** Use direct constraints, separate consequence/uncertainty narratives, sensitivity analysis or quantitative models with defensible data instead.

**Disposition at the historical freeze:** REJECTED_OR_DISFAVOURED

**Failure modes:** False precision, inversion, range compression, category gaming, low-frequency underestimation and “red-to-yellow” paperwork controls.

**Criticism:** Mathematical and regulatory critiques directly undermine universal ranking validity; prevalence and standard use are not effectiveness proof.

**Contrary evidence:** Some tailored matrices may support bounded prioritisation, but that does not rescue the objective or sufficient-evidence claim.

**Unresolved questions:** Under what narrow conditions can a matrix improve communication without becoming a threshold-gaming authority?

**Property versus ceremony:** The coloured grid is optional ceremony and becomes harmful when it substitutes for evidence or judgement.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW_OR_NONE — no general property is admitted in this form.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: HIGH — theory, cases or empirical studies directly undermine the universal claim.; SOURCE_BASIS: Primary: S034, S036, S037, S038; critical/contrary: S036, S037, S038.

**Primary source identities:** S034; S036; S037; S038

**Critical source identities:** S036; S037; S038

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/54`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-056"></a>
### ESS-056 — Maximal safety process on every change

**Historical origin:** Bureaucratic overextension of certification and stage-gate practices rather than a defensible historical system-safety principle.

**Original form:** Require the same full hazard analyses, boards, evidence and re-certification regardless of consequence, reversibility, scope or existing discriminator.

**Development:** Modern practice moves toward incremental, objectives-driven and risk-informed assurance with bounded reuse and cheap paths.

**Evolved form in this historical corpus:** NO_GENERAL_PROPERTY in uniform maximal treatment; apply only the control depth needed to discriminate and control the credible loss.

**Problem:** Low-value ritual consumes scarce expertise, delays safety fixes and encourages undeclared workarounds while adding no decision information.

**Mechanism:** Replace with change-impact analysis and consequence/reversibility/coupling tailoring; re-establish only affected claims and escalate uncertainty.

**Trigger and context:** No general trigger. Deep process is warranted only where credible consequence, coupling, irreversibility, novelty or weak observability makes it informative.

**Preconditions:** Reliable change classification, current baseline, deterministic discriminators where claimed and escalation authority.

**Authority and control preconditions:** Safety/change authority must be able to tailor down as well as up without hiding significant change.

**Required feedback:** Decision changes, defects found, false-stop/delay cost, workaround rate and whether affected safety claims were actually re-established.

**Decision or consumer:** Change authority, delivery team and safety/risk owner.

**Nontrigger or cheaper adequate path:** Use the cheap authoritative check for local reversible work and ordinary peer/change control for routine bounded work.

**Disposition at the historical freeze:** CEREMONY_NOT_GENERAL_PROPERTY

**Failure modes:** Checklist proliferation, long queues, shadow changes, stale assumptions preserved by process inertia and high false-positive cost.

**Criticism:** Official guidance explicitly supports tailoring and affected-scope assessment; maximality has no cross-domain optimality evidence.

**Contrary evidence:** Under-tailoring remains a real danger, so rejection of maximality does not justify informal change.

**Unresolved questions:** Which classification and escalation tests best prevent both bureaucratic over-control and hidden high-impact change?

**Property versus ceremony:** Universal full-process templates are ceremony, not safety.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW_OR_NONE — no general property is admitted in this form.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: HIGH — theory, cases or empirical studies directly undermine the universal claim.; SOURCE_BASIS: Primary: S029, S035, S052, S053, S054, S055, S098; critical/contrary: S038, S073, S074.

**Primary source identities:** S029; S035; S052; S053; S054; S055; S098

**Critical source identities:** S038; S073; S074

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/55`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-057"></a>
### ESS-057 — Compliance or certification treated as proof of current system safety

**Historical origin:** Proxy/compliance gaming arising around mature standards and certification regimes; not the stated purpose of system safety itself.

**Original form:** Infer that a system is safe now because required objectives, reviews or certificates were once accepted.

**Development:** Evolved practice emphasises continuing airworthiness/operation, living cases, change-aware assurance and explicit certification limits.

**Evolved form in this historical corpus:** Certification is a bounded governance/evidence decision, not a guarantee that all hazards are identified, controlled or unchanged.

**Problem:** Certification scope, assumptions, configuration and operational change are ignored, and compliance replaces live hazard control.

**Mechanism:** Treat compliance as one bounded evidence source; preserve current configuration/assumptions, operational monitoring, change impact and residual-risk authority.

**Trigger and context:** Certification is relevant where law/domain requires it, but never sufficient for total current safety.

**Preconditions:** Accurate scope, current evidence, configuration identity, operational controls and independent challenge.

**Authority and control preconditions:** Operator/design authority retains responsibility; a certificate does not transfer control of ongoing risk.

**Required feedback:** Operational anomalies, changes, control/barrier health, assumptions and evidence validity after acceptance.

**Decision or consumer:** Regulator/certifier, operator, design authority and public risk governance.

**Nontrigger or cheaper adequate path:** For nonregulated low-consequence work use direct engineering evidence rather than importing certification ceremony.

**Disposition at the historical freeze:** REJECTED_OR_DISFAVOURED

**Failure modes:** Tick-box compliance, scope laundering, certification freeze, paper safety and suppressed post-certification evidence.

**Criticism:** Nimrod, Columbia, 737 MAX and other investigations supply direct counterexamples to acceptance equalling current safety.

**Contrary evidence:** Certification can materially improve baseline discipline; rejection concerns the proxy claim, not all certification value.

**Unresolved questions:** How should public communication state certification assurance without implying a guarantee the evidence cannot support?

**Property versus ceremony:** The certificate is domain-specific; current hazard/control/evidence integrity is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW_OR_NONE — no general property is admitted in this form.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: HIGH — theory, cases or empirical studies directly undermine the universal claim.; SOURCE_BASIS: Primary: S029, S030, S031, S032, S042; critical/contrary: S048, S082, S089, S090.

**Primary source identities:** S029; S030; S031; S032; S042

**Critical source identities:** S048; S082; S089; S090

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/56`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-058"></a>
### ESS-058 — Zero observed incidents treated as proof that controls work

**Historical origin:** Lagging-metric simplification in industrial and organisational safety management.

**Original form:** Use a short incident-free period or low count as sufficient evidence of low true risk and effective controls.

**Development:** Modern practice uses precursors, control-state monitoring and multiple evidence streams while treating incident counts cautiously.

**Evolved form in this historical corpus:** NO_GENERAL_PROPERTY in incident-free proof; require evidence proportionate to rarity, exposure and causal control state.

**Problem:** Rare-event statistics, exposure, underreporting and latent degradation make silence compatible with high risk.

**Mechanism:** Reject the inference; combine incident data with exposure, control/barrier health, precursors, assumptions and causal evidence.

**Trigger and context:** Incident counts may contribute to trend analysis only with adequate exposure/definition and never stand alone for rare catastrophic hazards.

**Preconditions:** Stable reporting and exposure definitions, enough data and a model linking outcomes to controls.

**Authority and control preconditions:** Decision owners must be able to investigate weak signals rather than reward zero-report targets.

**Required feedback:** Exposure-adjusted events, near misses, reporting quality, barrier demand/success and precursor trends.

**Decision or consumer:** Safety management, operator and risk authority.

**Nontrigger or cheaper adequate path:** Use direct inspections/tests/control-state measures or an authoritative deterministic discriminator where available.

**Disposition at the historical freeze:** REJECTED_OR_DISFAVOURED

**Failure modes:** Incentive to suppress reports, celebratory complacency, regression to the mean and delayed detection of latent risk.

**Criticism:** Sparse catastrophic data cannot validate absence of risk; leading indicators also have validity/gaming limits.

**Contrary evidence:** Long exposure without incidents can update probability under a valid stable model, but rarely proves control efficacy by itself.

**Unresolved questions:** What evidence combination is sufficient to update confidence for rare hazards without pretending that absence of loss is proof?

**Property versus ceremony:** Zero-incident boards and targets are potentially harmful ceremony when they suppress learning.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW_OR_NONE — no general property is admitted in this form.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: HIGH — theory, cases or empirical studies directly undermine the universal claim.; SOURCE_BASIS: Primary: S039, S080, S097, S104; critical/contrary: S071, S072, S081, S082.

**Primary source identities:** S039; S080; S097; S104

**Critical source identities:** S071; S072; S081; S082

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/57`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-059"></a>
### ESS-059 — Human error used as the root-cause endpoint

**Historical origin:** Early accident prevention and blame-oriented investigation simplification, later explicitly criticised by human-factors and systems safety.

**Original form:** Conclude that an operator made an error or violated a procedure and close with retraining, discipline or reminder.

**Development:** Evolved through Reason/local rationality, just culture and system-control analysis toward context-sensitive causal mechanisms.

**Evolved form in this historical corpus:** Human action is analysed as part of a sociotechnical control system; “error” alone never closes causal or corrective-action burdens.

**Problem:** The label redescribes the unsafe action but does not explain information, workload, design, goals, authority or defences that made it possible.

**Mechanism:** Reject human error as terminal cause; investigate the action in context, preserve individual competence/accountability questions separately, and change upstream controls.

**Trigger and context:** Human action remains relevant as a causal event but not as a self-explanatory root cause.

**Preconditions:** Access to work context, human-factors competence and a fair learning/accountability process.

**Authority and control preconditions:** Investigators and managers must be able to change design/organisation, not merely discipline the nearest actor.

**Required feedback:** Interface/mode/workload evidence, feedback, competing goals, procedure usability, staffing, prior signals and recurrence.

**Decision or consumer:** Investigator, designer, operator management and just-culture authority.

**Nontrigger or cheaper adequate path:** For an unambiguous deliberate violation under adequate conditions, ordinary accountability may apply, but still test whether system controls were sufficient.

**Disposition at the historical freeze:** REJECTED_OR_DISFAVOURED

**Failure modes:** Blame displacement, shallow retraining, underreporting and removal of useful operator discretion.

**Criticism:** Systems approaches can overcorrect by erasing culpable misconduct or individual skill duties; accountability and explanation are distinct.

**Contrary evidence:** Some events involve intentional wrongdoing or profound incompetence, which systems analysis must not euphemise away.

**Unresolved questions:** How can just accountability be preserved while preventing blame from terminating the safety investigation?

**Property versus ceremony:** A Swiss-cheese or human-error taxonomy is optional; context/control evidence is required.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW_OR_NONE — no general property is admitted in this form.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: HIGH — theory, cases or empirical studies directly undermine the universal claim.; SOURCE_BASIS: Primary: S063, S064, S076, S077, S106, S112; critical/contrary: S084, S088, S109.

**Primary source identities:** S063; S064; S076; S077; S106; S112

**Critical source identities:** S084; S088; S109

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/58`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-060"></a>
### ESS-060 — More redundancy treated as automatically safer

**Historical origin:** Reliability engineering simplification and architectural rule-of-thumb detached from common-cause and interaction analysis.

**Original form:** Add duplicate components/channels and infer safety improvement from nominal multiplicity.

**Development:** Evolved toward function-specific independence/diversity claims, common-cause analysis, degradation monitoring and simpler architectures where appropriate.

**Evolved form in this historical corpus:** Use the minimum architecture that controls the hazard with demonstrable independence and manageable interaction complexity.

**Problem:** Shared design, requirements, software, sensors, utilities, maintenance or environment creates correlated failure; complexity creates new interactions.

**Mechanism:** Reject automaticity; state the hazard and redundancy purpose, analyse common cause/dependence, use diversity where informative, monitor degradation and test arbitration.

**Trigger and context:** Redundancy is justified where continued/backup function materially controls a hazard and credible independence can be evidenced.

**Preconditions:** Explicit failure/interaction model, independence evidence, diagnostic coverage and manageable complexity.

**Authority and control preconditions:** Architecture authority must own the tradeoff and operations must restrict use when redundant capacity is degraded.

**Required feedback:** Common inputs, latent channel state, disagreement, voting/arbitration, shared maintenance/utilities and demand success.

**Decision or consumer:** Architect, reliability/system safety, verifier and operator.

**Nontrigger or cheaper adequate path:** A simpler single channel with strong elimination/containment and direct verification may be safer for low-complexity hazards.

**Disposition at the historical freeze:** REJECTED_OR_DISFAVOURED

**Failure modes:** Common-mode failure, mode confusion, latent fault accumulation, false confidence and complexity-induced defects.

**Criticism:** Multiversion experiments, Ariane/Fukushima/737 evidence and systems theory directly refute naive independence.

**Contrary evidence:** No universal metric captures the safety tradeoff between added tolerance and added complexity.

**Unresolved questions:** How can independence claims be validated for diverse AI/software channels trained or specified from shared data?

**Property versus ceremony:** Channel count is ceremony without hazard purpose, independence and health evidence.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW_OR_NONE — no general property is admitted in this form.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: HIGH — theory, cases or empirical studies directly undermine the universal claim.; SOURCE_BASIS: Primary: S050, S056, S057; critical/contrary: S050, S083, S087, S089, S090.

**Primary source identities:** S050; S056; S057

**Critical source identities:** S050; S083; S087; S089; S090

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/59`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-061"></a>
### ESS-061 — Reviewer or evidence-item count treated as assurance strength

**Historical origin:** Compliance metric and organisational-independence simplification around review, audit and safety-case practice.

**Original form:** Infer stronger assurance from more signatures, reviews, documents, tests or evidence items without analysing information content and dependence.

**Development:** Evolved toward confidence arguments, defeaters, evidence provenance and risk-based independent assessment.

**Evolved form in this historical corpus:** Assurance strength depends on relevance, validity, currentness and independently informative failure modes—not artefact or reviewer count.

**Problem:** Correlated evidence and confirmation bias are hidden by volume, while scarce challenge effort is spread thinly.

**Mechanism:** Reject count as strength; map what each evidence item can detect, its provenance/dependence and whether review changed a consequential decision.

**Trigger and context:** Additional review is justified only when it contributes distinct competence, evidence or challenge proportional to consequence.

**Preconditions:** Explicit claim/evidence model, provenance, competence and challenge authority.

**Authority and control preconditions:** Independent reviewers need access and escalation, but the acceptance authority must judge informational contribution rather than headcount.

**Required feedback:** Distinct findings, shared sources, changed decisions, unresolved dissent, defect yield and review latency/cost.

**Decision or consumer:** Assurance owner, IV&V, certifier and risk acceptor.

**Nontrigger or cheaper adequate path:** One decisive direct check is enough for a narrow reversible claim; avoid reviewer multiplication.

**Disposition at the historical freeze:** REJECTED_OR_DISFAVOURED

**Failure modes:** Signature collection, duplicate test sets, document inflation, delayed feedback and responsibility diffusion.

**Criticism:** Experimental independence evidence and Nimrod directly undermine volume/organisational-separation proxies.

**Contrary evidence:** Measuring informational independence itself remains difficult and may require qualitative judgement.

**Unresolved questions:** What operational metrics reveal distinct assurance information without encouraging another gameable count?

**Property versus ceremony:** Review boards and evidence inventories are implementations, not properties.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW_OR_NONE — no general property is admitted in this form.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: HIGH — theory, cases or empirical studies directly undermine the universal claim.; SOURCE_BASIS: Primary: S044, S046, S099; critical/contrary: S048, S050.

**Primary source identities:** S044; S046; S099

**Critical source identities:** S048; S050

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/60`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-062"></a>
### ESS-062 — Complete safety case treated as proof the system is safe

**Historical origin:** Misinterpretation of safety-case completeness and certification acceptance.

**Original form:** Infer system truth from a complete, coherent or accepted claim–argument–evidence document.

**Development:** Evolved toward modular, living, challenge-led and evidence-provenance-aware assurance.

**Evolved form in this historical corpus:** A case is a defeasible justification for a bounded decision, never a proof that all system hazards are absent or controlled.

**Problem:** Arguments can omit hazards, contain false premises, cite dependent/stale evidence or represent a different configuration while remaining coherent.

**Mechanism:** Reject the inference; retain defeasible claim–evidence reasoning tied to actual configuration, assumptions, counterevidence, operational monitoring and authority.

**Trigger and context:** A safety case is useful for consequential synthesis/acceptance but is never a guarantee.

**Preconditions:** Valid evidence, complete-enough hazard boundary, current configuration, active challenge and live consumer.

**Authority and control preconditions:** Acceptance authority must be able to reject the case and reopen it after change or adverse evidence.

**Required feedback:** Evidence freshness, assumptions, defeaters, system correspondence, operational anomalies and decision use.

**Decision or consumer:** Case owner, operator, assessor/regulator and risk acceptor.

**Nontrigger or cheaper adequate path:** Use a compact rationale/direct evidence for narrow reversible claims rather than manufacturing a full case.

**Disposition at the historical freeze:** REJECTED_OR_DISFAVOURED

**Failure modes:** Paper safety, template compliance, argumentative overconfidence, stale cases and disconnect from engineering reality.

**Criticism:** Nimrod is direct and authoritative counterevidence; safety-case scholars also stress limits and confidence.

**Contrary evidence:** No practical assurance method can prove hazard completeness for open sociotechnical systems.

**Unresolved questions:** How should cases communicate bounded confidence to decision-makers and the public without either overclaiming or becoming unusably qualified?

**Property versus ceremony:** The monolithic completed document is not a general property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW_OR_NONE — no general property is admitted in this form.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: HIGH — theory, cases or empirical studies directly undermine the universal claim.; SOURCE_BASIS: Primary: S042, S043, S044, S045, S108; critical/contrary: S048, S107, S108.

**Primary source identities:** S042; S043; S044; S045; S108

**Critical source identities:** S048; S107; S108

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/61`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-063"></a>
### ESS-063 — One universal hazard-analysis technique

**Historical origin:** Method advocacy and textbook simplification across FMEA, FTA, HAZOP, STPA and other schools.

**Original form:** Select one named technique and treat it as sufficient for every failure, interaction, process, organisational and uncertainty class.

**Development:** Modern practice hybridises failure, interaction, scenario, process and assurance methods around the actual hazard class.

**Evolved form in this historical corpus:** Use the minimum complementary method set needed to represent credible causal classes and make decisions; declare what remains outside.

**Problem:** The representation systematically excludes relevant causes while analysts mistake worksheet completion for hazard completeness.

**Mechanism:** Reject universality; select and combine techniques by hazard/causal coverage, consequence and decision need, and state residual blind spots.

**Trigger and context:** Each method triggers only where its representation matches the problem and expected findings can change design or operation.

**Preconditions:** Method competence, explicit assumptions/boundary and a coverage/complementarity rationale.

**Authority and control preconditions:** Safety authority must choose and tailor methods rather than accept tool/vendor branding.

**Required feedback:** Hazards/scenarios found, method overlap/gaps, decisions changed, unresolved uncertainty and model/analyst sensitivity.

**Decision or consumer:** Safety analyst, system architect, human factors/operations and acceptance authority.

**Nontrigger or cheaper adequate path:** A direct deterministic analysis may suffice for a narrow simple hazard; do not run every named method.

**Disposition at the historical freeze:** REJECTED_OR_DISFAVOURED

**Failure modes:** Method wars, redundant workshops, inconsistent taxonomies, false completeness and tool-driven scope.

**Criticism:** STPA empirical comparison is limited; FMEA/FTA/HAZOP each have well-established but bounded semantics.

**Contrary evidence:** Method complementarity can itself become maximalist ceremony without a stopping rule.

**Unresolved questions:** How can coverage portfolios be evaluated prospectively without assuming an unknowable complete hazard set?

**Property versus ceremony:** Named-method ritual is not a property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW_OR_NONE — no general property is admitted in this form.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: HIGH — theory, cases or empirical studies directly undermine the universal claim.; SOURCE_BASIS: Primary: S007, S009, S011, S018, S096; critical/contrary: S019, S020, S038.

**Primary source identities:** S007; S009; S011; S018; S096

**Critical source identities:** S019; S020; S038

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/62`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-064"></a>
### ESS-064 — Zero-risk or absolute-safety requirement as a general engineering target

**Historical origin:** Public rhetoric and overconservative simplification, not mature risk/standards doctrine.

**Original form:** Demand proof of no risk or elimination of every conceivable hazard before operation/change.

**Development:** Modern evolved form uses explicit unacceptable loss, residual risk and proportionality while preserving categorical constraints where justified.

**Evolved form in this historical corpus:** NO_GENERAL_PROPERTY in absolute safety; engineer against specified unacceptable losses with bounded evidence and transparent residual uncertainty.

**Problem:** Impossible proof burdens obscure residual uncertainty, prevent beneficial/safety-critical service and encourage hidden risk acceptance.

**Mechanism:** Reject absolute proof; define unacceptable losses, eliminate/control hazards, state residual risk/uncertainty and apply proportionate authority.

**Trigger and context:** No general engineering trigger; strict prohibitions may apply to particular intolerable states or legal duties.

**Preconditions:** Explicit loss and tolerance criteria, feasible controls and honest uncertainty.

**Authority and control preconditions:** Legitimate public/legal authority defines intolerability; engineers cannot manufacture zero through documentation.

**Required feedback:** Residual hazards, uncertainty, exposure, alternatives, operational evidence and competing service harms.

**Decision or consumer:** Public authority, risk acceptor, designer and operator.

**Nontrigger or cheaper adequate path:** Use deterministic prohibitions for specific unacceptable states, not a universal claim that all risk is zero.

**Disposition at the historical freeze:** REJECTED_OR_DISFAVOURED

**Failure modes:** Paralysis, risk transfer, dishonest “zero” certification, excessive false stops and suppression of uncertainty.

**Criticism:** Standards distinguish safety from freedom from all risk and HSE doctrine explicitly reasons about tolerability/practicability.

**Contrary evidence:** Some domains legitimately prohibit particular single failures or exposures; rejection is of universal absolute risk elimination.

**Unresolved questions:** Which losses should be governed by categorical constraints rather than tradeable risk reasoning?

**Property versus ceremony:** “Zero risk” slogans are ceremony unless attached to a specific enforceable prohibition.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW_OR_NONE — no general property is admitted in this form.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: HIGH — theory, cases or empirical studies directly undermine the universal claim.; SOURCE_BASIS: Primary: S033, S034, S035; critical/contrary: S113, S068.

**Primary source identities:** S033; S034; S035

**Critical source identities:** S113; S068

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/63`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-065"></a>
### ESS-065 — Generic safety-culture score treated as direct control or safety evidence

**Historical origin:** Organisational safety-culture programmes and survey measurement, often detached from specific hazards and decisions.

**Original form:** Measure broad attitudes or perceptions, aggregate a score and infer that control effectiveness or accident risk has improved.

**Development:** Evolved toward mixed-method, mechanism-specific organisational diagnostics and hazard-linked leading indicators.

**Evolved form in this historical corpus:** Use “culture” only as a hypothesis about observable decision/control patterns, never as self-validating evidence from a composite score.

**Problem:** Construct ambiguity, common-method bias and weak causal linkage allow a favourable score alongside degraded barriers and incentives.

**Mechanism:** Reject the score as direct evidence; retain observable organisational control, reporting, authority, incentive and barrier mechanisms, using surveys only as one diagnostic input.

**Trigger and context:** A targeted survey can trigger inquiry where a plausible mechanism and consumer exist, not certify safety.

**Preconditions:** Defined construct, validated measure, exposure/context, triangulation and authority to act on findings.

**Authority and control preconditions:** Leaders must change resources/incentives/controls; communications teams cannot own the safety consequence.

**Required feedback:** Specific escalation, reporting, staffing, maintenance, waiver and control behaviours plus survey uncertainty.

**Decision or consumer:** Leadership, workforce, regulator and safety management.

**Nontrigger or cheaper adequate path:** Use direct work/control evidence for a known hazard; no culture programme is needed for a simple technical defect.

**Disposition at the historical freeze:** REJECTED_OR_DISFAVOURED

**Failure modes:** Score chasing, positivity pressure, generic training, survey fatigue and displacement of material hazards.

**Criticism:** Reviews find substantial definitional and measurement uncertainty and warn against simple outcome claims.

**Contrary evidence:** Longitudinal causal evidence connecting interventions, scores and rare accidents remains weak.

**Unresolved questions:** Which observable organisational mechanisms should replace broad culture scores in prospective safety decisions?

**Property versus ceremony:** A culture survey, campaign or slogan is not a general safety property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW_OR_NONE — no general property is admitted in this form.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: HIGH — theory, cases or empirical studies directly undermine the universal claim.; SOURCE_BASIS: Primary: S071, S072; critical/contrary: S066, S071, S072.

**Primary source identities:** S071; S072

**Critical source identities:** S066; S071; S072

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/64`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-066"></a>
### ESS-066 — Swiss-cheese diagram used as an engine-level causal explanation

**Historical origin:** James Reason’s layered-defence metaphor and its widespread textbook transmission.

**Original form:** Represent accidents as hazard trajectories aligning through holes in multiple defence layers.

**Development:** Evolved toward barrier-management, bow-tie and systems/control models with explicit functions, dependencies and feedback.

**Evolved form in this historical corpus:** SUPERSEDED_BY_STRONGER_FORM for detailed analysis; retain only a bounded communication metaphor subordinate to explicit mechanisms.

**Problem:** The metaphor identifies neither the concrete control action, interaction, timing, feedback, authority nor causal mechanism needed for design.

**Mechanism:** Retain only the intuition that multiple defences can be breached; replace mechanism claims with explicit barrier dependence, causal scenarios and control/feedback models.

**Trigger and context:** Useful as high-level communication after the actual mechanisms and barrier functions are established.

**Preconditions:** Defined hazard, barriers and mechanisms; audience understands metaphor limitations.

**Authority and control preconditions:** No special authority; engineering decisions must rest on more specific evidence.

**Required feedback:** Actual barrier state, dependencies, control actions, timing and causal scenario—not hole count.

**Decision or consumer:** Educator, investigator and communicating authority.

**Nontrigger or cheaper adequate path:** Use a direct causal/control model for engineering decisions; omit the diagram when it adds no consumer value.

**Disposition at the historical freeze:** SUPERSEDED_BY_STRONGER_FORM

**Failure modes:** Layer-counting, hidden common cause, blame relocation, generic recommendations and false causal completeness.

**Criticism:** Reason’s broader contribution on latent conditions survives, but the popular diagram is often overextended beyond explanatory capacity.

**Contrary evidence:** The metaphor can still efficiently communicate layered defence to non-specialists when carefully qualified.

**Unresolved questions:** What minimum mechanism annotations prevent a defence-layer diagram from becoming a causal stopping point?

**Property versus ceremony:** The diagram is not required and should not authorise controls by itself.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW — should not be transferred as a general property.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: HIGH — theory, cases or empirical studies directly undermine the universal claim.; SOURCE_BASIS: Primary: S063; critical/contrary: S066, S109, S110.

**Primary source identities:** S063

**Critical source identities:** S066; S109; S110

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/65`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-067"></a>
### ESS-067 — STPA treated as a universal replacement for other hazard analyses

**Historical origin:** Overgeneralisation of STAMP/STPA advocacy beyond the method’s supported reformulation and evidence base.

**Original form:** Use STPA for all hazard classes and infer that FMEA, FTA, HAZOP, quantitative reliability and domain analyses are obsolete.

**Development:** Evolved toward hybrid STPA–FTA/FMEA/formal/scenario workflows and narrower claims about representational contribution.

**Evolved form in this historical corpus:** CONTESTED as a universal method; retain STPA as one strong representation for control/interaction hazards with explicit limits and complementary analyses.

**Problem:** Control-structure modelling can be subjective, large and weak on component probabilities/material mechanisms while comparative effectiveness remains limited.

**Mechanism:** Reject universal replacement; retain unsafe-interaction/control reasoning and combine STPA with failure, process, quantitative, human-factors or formal methods as the hazard requires.

**Trigger and context:** STPA is especially relevant for software-intensive, multi-controller and interaction hazards where its findings have design consumers.

**Preconditions:** Competent modelling, operational participation, bounded system/control scope and complementary coverage rationale.

**Authority and control preconditions:** Safety authority chooses the portfolio and must not equate STPA completion with hazard completeness.

**Required feedback:** Inter-analyst consistency, scenarios/controls found, decisions changed, omitted causal classes, analysis effort and field feedback.

**Decision or consumer:** System safety, designers, operators and research community.

**Nontrigger or cheaper adequate path:** Use direct failure analysis or another adequate method for simple bounded hazards; no STPA diagram is obligatory.

**Disposition at the historical freeze:** CONTESTED

**Failure modes:** Diagram explosion, subjective unsafe-action contexts, weak quantitative integration, tool lock-in and method branding.

**Criticism:** Reviews and FAA evaluation find promise and useful gaps but call for stronger empirical comparison, scalability evidence and real-world validation.

**Contrary evidence:** Some studies report additional hazards and design value, but universality and superiority are not established.

**Unresolved questions:** Which comparative protocols can measure hazard coverage and decision impact across STPA and complementary methods without assuming a known complete truth set?

**Property versus ceremony:** STPA terminology/diagrams are not universal properties.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: MODERATE_FOR_CONTROL_INTERACTION_PROPERTY_LOW_FOR_UNIVERSAL_REPLACEMENT — transfer depends on system/control fit.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: MODERATE — criticism limits universality but does not reject STPA’s core representational contribution.; SOURCE_BASIS: Primary: S017, S018; critical/contrary: S019, S020, S109.

**Primary source identities:** S017; S018

**Critical source identities:** S019; S020; S109

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/66`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

<a id="ess-068"></a>
### ESS-068 — Resilience or adaptation terminology without hazard, control or decision specificity

**Historical origin:** Resilience engineering and Safety-II discourse when reduced to broad capacity/positive-performance language.

**Original form:** Invoke resilience, adaptation, flexibility or “work as done” as a safety property without defining the loss, boundary, control, feedback or measurable decision.

**Development:** Evolved toward bounded runtime assurance, explicit adaptive envelopes, recovery metrics and integration with hazard/control models.

**Evolved form in this historical corpus:** CONTESTED as a standalone general property; admit only specific, observable and authority-bounded adaptive mechanisms linked to unacceptable loss.

**Problem:** Vague desirable language cannot discriminate safe from unsafe adaptation and may legitimise migration or under-specified continuation.

**Mechanism:** Retain adaptive monitoring, graceful degradation, local rationality and recovery only when tied to explicit hazards, constraints, feedback, authority and evaluation.

**Trigger and context:** Relevant for variable environments and surprise where bounded adaptation is necessary and observable.

**Preconditions:** Defined loss/constraint, observable adaptive capacity, authority envelope, fallback and evidence that adaptation does not externalise risk.

**Authority and control preconditions:** Operators need discretion within bounded authority plus escalation/stop support; adaptation beyond the envelope requires re-assurance.

**Required feedback:** Envelope excursions, successful/failed adaptations, resource reserve, recovery time, control state and adverse side effects.

**Decision or consumer:** Operations, human factors, resilience/safety management and system authority.

**Nontrigger or cheaper adequate path:** Do not create a resilience programme for a simple deterministic hazard; use the direct control.

**Disposition at the historical freeze:** CONTESTED

**Failure modes:** Buzzword adoption, unvalidated indices, romanticising frontline coping, shifting design burden to operators and measuring only successful adaptation.

**Criticism:** Systematic reviews report fragmented indicators and conceptual ambiguity; resilience theory also usefully redirects attention to variability and successful performance.

**Contrary evidence:** The lineage contributes important insights on variability, recovery and local adaptation despite weak generic measurement.

**Unresolved questions:** Which resilience capacities have prospective, hazard-specific predictive validity rather than retrospective narrative appeal?

**Property versus ceremony:** A resilience workshop, score or vocabulary is not required.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH — the practice or simplification is well documented.; FORMAL_OR_MODEL_STRENGTH: LOW_OR_NEGATIVE — the claimed inference is invalid or materially underdetermined.; ACCIDENT_CASE_STRENGTH: MODERATE_TO_HIGH_AGAINST — accident evidence supplies counterexamples.; EMPIRICAL_COMPARATIVE_STRENGTH: MODERATE_AGAINST_OR_UNRESOLVED — available studies do not justify the universal claim.; DOMAIN_PRACTICE_STRENGTH: PRESENT_AS_CEREMONY_OR_SHORTCUT — prevalence does not establish value.; STANDARD_OR_REGULATORY_STRENGTH: VARIABLE — some artefacts appear in standards, but the rejected inference is not warranted.; TRANSFERABILITY_STRENGTH: LOW_FOR_GENERIC_LABEL_MODERATE_FOR_SPECIFIC_BOUNDED_MECHANISMS.; ASSUMPTION_SENSITIVITY: VERY_HIGH — apparent validity usually depends on hidden assumptions.; CONTRARY_EVIDENCE_STRENGTH: MODERATE_TO_HIGH — conceptual/indicator heterogeneity materially limits general claims.; SOURCE_BASIS: Primary: S069, S111; critical/contrary: S070, S111, S065.

**Primary source identities:** S069; S111

**Critical source identities:** S070; S111; S065

Source: [EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json), JSON pointer `/PROPERTIES/67`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json).

## Source references

[c-page]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/portal/pages/research-lineage-cognitive-systems-engineering.html
[s-page]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/portal/pages/research-lineage-statistical-engineering.html
[h-page]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/portal/pages/research-lineage-systems-safety.html
[css-page]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/portal/pages/research-lineage-evolved-css.html
[css-readme]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/README.md
[c-ledger]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-cognitive-systems-engineering/corpus/EVOLVED_COGNITIVE_SYSTEMS_ENGINEERING_PROPERTY_LEDGER.json
[c-sources]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-cognitive-systems-engineering/corpus/EVOLVED_COGNITIVE_SYSTEMS_ENGINEERING_SOURCE_TABLE.json
[c-intake]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-cognitive-systems-engineering/corpus/EVOLVED_COGNITIVE_SYSTEMS_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE.md
[s-ledger]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json
[s-sources]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json
[s-intake]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE.md
[h-ledger]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json
[h-sources]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json
[h-intake]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PUBLIC_DOCUMENTATION_INTAKE.md
[current-css]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/current-programme/v1/families/css.md
[194-receipt]: https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/194#issuecomment-5312867827
[195]: https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/195
[195-receipt]: https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/195#issuecomment-5312877164
[196-census]: https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/196#issuecomment-5312877705
[effect-source]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/skills/implementaudit/references/repo-state-comparison.md
[phase-source]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/skills/implementaudit/references/phase-design.md
[planning-source]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/skills/implementaudit/references/planning-depth.md
[active-safety]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/ed2c060daa41b6b88c1d49b325a3aa920088aed8/docs/maintenance/four-rockstar-integration.md
[203]: https://github.com/theislampill/IMPLEMENTAUDIT.md/pull/203
[206]: https://github.com/theislampill/IMPLEMENTAUDIT.md/pull/206
