# EVOLVED_SOFTWARE_ARCHITECTURE_SYNTHESIS_INTAKE

Revision ESA-2026-09-06-r1 · cut-off 2026-09-06.

Candidate grouping: **SSS — Software Architecture / Software Maintenance and Evolution / Software Product Line Engineering**. This grouping is provisional, not an established scholarly school. The present intake contains only the independently researched Software Architecture lane.

`SIBLING_CORPORA_NOT_CONSULTED`  
`CROSS_TRIFECTA_SYNTHESIS_NOT_PERFORMED`

## Within-tradition synthesis

The conditional core links consequential concerns to structure/interface choices, quality scenarios, alternatives, legitimate decisions, real implementation/operation and revisable evidence of effects. Views and rationale communicate the account; conformance and observation can reopen the affected choice. Analysis, synthesis and evaluation interleave. Formal analysis, runtime control, family design, distributed deployment and fuller governance are guarded alternative configurations, not mandatory stages. This is an analytical composition, not a recognised school or a tested whole-system effect.

Native concepts include information hiding, uses relations, components/connectors, architectural styles, concerns/views/viewpoints, quality scenarios/tactics, sensitivity/trade-off points, rationale, reflexion mapping, drift/erosion and architectural revision. Documented intersections include family variability, maintenance/debt, bounded semantic contexts, service interactions, socio-technical coordination, formal models, learned/data dependencies and sustainability. Preserve their different units and evidence roles.

## Stable population and dependency model

There are **68 examined candidates**, **55 crosswalk-worthy candidates**, **13 other dispositions**, **66 source records**, and **65 composition relations**. See [EVOLVED_SOFTWARE_ARCHITECTURE_PROPERTY_LEDGER.json](EVOLVED_SOFTWARE_ARCHITECTURE_PROPERTY_LEDGER.json), [EVOLVED_SOFTWARE_ARCHITECTURE_SOURCE_TABLE.json](EVOLVED_SOFTWARE_ARCHITECTURE_SOURCE_TABLE.json), and [EVOLVED_SOFTWARE_ARCHITECTURE_COMPOSITION_MODEL.json](EVOLVED_SOFTWARE_ARCHITECTURE_COMPOSITION_MODEL.json). Their IDs and denominator are frozen; a later integration must not delete unfavourable rows or count overlapping studies as independent evidence.

Criteria become operative only when coupled to an establishing method and a consumer: significance requires consequence inquiry; scenarios require selected observations; conformance requires a justified mapping; a decision requires a real actor able to act. Conversely, a workshop, model or controller is ceremony when it has no relevant decision/effect consumer. The composition relations distinguish REQUIRES, ENABLES, CONSTRAINS, evidence, communication, action, feedback, alternatives, conflict, refinement, supersession and bounded shared ancestry.

## Complete mechanism/interface export

Every global key below resolves to its full property record. Inputs, outputs, costs and assumptions are research interfaces, not proposed components or permissions. Non-retained records are exported as negative/unresolved boundaries rather than implementation requirements.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-001` — Consequence-bound architectural significance

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Identify decisions whose cross-cutting consequences, dependency reach, qualities or change costs justify architectural treatment; state why each is significant rather than relying on job title or diagram level.

**Trigger and required inputs:** A decision can change a stakeholder outcome beyond its local implementation or would be costly to reverse. Knowledge of affected consumers and constraints; significance must be revisable as consequences become better understood.

**Produced constraint/evidence:** A reviewer can connect the claimed architectural decision to an affected concern, boundary or costly dependency. Its consumer is: Design participants and those accountable for affected product/operating concerns.

**Costs, substitution and omission:** Handle genuinely local, reversible choices within ordinary design and code review; do not create an architectural record for every edit.

**Assumptions, conflicts and failure:** Importance is relative to a system and stakeholder; “hard to change” can reward needless rigidity and miss cheap but safety-critical choices.

**Retirement/reopening:** Reopen classification when the change becomes local/reversible or newly affects external commitments.

**Abstraction:** Consequential software structures and decisions, at a declared scope rather than a fixed diagram granularity. **Evidence boundary:** Assess named consequences such as latency limits, compatibility or expected change propagation; there is no universal significance score. Importance is relative to a system and stakeholder; “hard to change” can reward needless rigidity and miss cheap but safety-critical choices.

**Relations:** ESA-REL001, ESA-REL029, ESA-REL052, ESA-REL061. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S002, ESA-S010.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-002` — Stakeholder concerns connected to decisions

Status: `STRONGLY_RETAINED`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Connect each material concern to an architectural question, a scenario or constraint and the decision that consumes it; expose conflicts and missing participation.

**Trigger and required inputs:** Different users, maintainers, operators or sponsors bear materially different consequences. Affected people can contribute or be represented; concern selection is not confined to the loudest or most powerful participant.

**Produced constraint/evidence:** Affected concerns have a traceable design/evaluation consequence, including documented disagreement or uncertainty. Its consumer is: Those making trade-offs and those who will bear their consequences; elicitors facilitate rather than acquire unilateral authority.

**Costs, substitution and omission:** For a small shared-understanding team, discuss the few consequential concerns directly and retain only what later action needs.

**Assumptions, conflicts and failure:** Workshop voting can suppress rare hazards or minority needs; stakeholder agreement does not validate the design.

**Retirement/reopening:** Reopen when stakeholders, operating conditions or commitments change, or an omitted concern is discovered.

**Abstraction:** Stakeholder concerns related to system-wide and boundary-level choices. **Evidence boundary:** Check whether selected scenarios include relevant environments, users and response measures, not how many concerns were listed. Workshop voting can suppress rare hazards or minority needs; stakeholder agreement does not validate the design.

**Relations:** ESA-REL001, ESA-REL002. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S011, ESA-S017, ESA-S020, ESA-S021.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-003` — Architecture, description and belief distinguished

Status: `STRONGLY_RETAINED`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Keep intended structure, its representation and claims about the actual system distinguishable; attach a basis and observation scope to assertions of correspondence.

**Trigger and required inputs:** A decision depends on a diagram, repository model, recovered graph or architect’s account being true of the real system. Access to evidence about the realised structure and knowledge of what each representation includes and omits.

**Produced constraint/evidence:** A consumer can tell what is intended, what is observed and what remains an assumption. Its consumer is: Implementers, reviewers and operators relying on architectural claims.

**Costs, substitution and omission:** Inspect the relevant code/configuration/execution directly when the system is small; a separate comprehensive model is unnecessary.

**Assumptions, conflicts and failure:** A beautiful or agreed model can be false; source extraction can also omit deployment and runtime relations.

**Retirement/reopening:** Reopen correspondence after configuration, interface, deployment or model changes.

**Abstraction:** Intended architecture, architecture description and realised software/configuration as separate referents. **Evidence boundary:** Measure discrepancies in the relation relevant to the decision, not similarity of pictures. A beautiful or agreed model can be false; source extraction can also omit deployment and runtime relations.

**Relations:** ESA-REL005, ESA-REL020, ESA-REL062. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S002, ESA-S011, ESA-S045, ESA-S026.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-004` — Conceptual integrity without mandatory centralisation

Status: `CONTEXT_DEPENDENT`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Keep the user-visible and developer-facing concepts and essential invariants coherent across decisions, while allowing local variation that does not damage them.

**Trigger and required inputs:** Independent decisions would expose incompatible meanings or behaviours to common consumers. Agreement about which concepts require common meaning and which variations are harmless or valuable.

**Produced constraint/evidence:** Cross-boundary use does not require consumers to reconcile contradictory core concepts without an explicit translation. Its consumer is: People responsible for shared interfaces and product coherence, with local teams retaining bounded design discretion.

**Costs, substitution and omission:** Use shared examples and a small vocabulary in one team; do not impose a chief architect or one technology solely to look unified.

**Assumptions, conflicts and failure:** Centralised approval can bottleneck learning; uniform implementation is not the same as conceptual integrity.

**Retirement/reopening:** Reopen the shared concept when domains diverge or maintaining uniformity costs more than explicit translation.

**Abstraction:** System concepts and cross-component behavioural commitments. **Evidence boundary:** Exercise cross-boundary user journeys or invariant checks; stylistic uniformity is a poor stand-alone proxy. Centralised approval can bottleneck learning; uniform implementation is not the same as conceptual integrity.

**Relations:** ESA-REL010. **Tensions:** ESA-T001. **Source IDs:** ESA-S008, ESA-S010, ESA-S025, ESA-S041, ESA-S039.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-005` — Accountable authority for consequential trade-offs

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Make it clear who can accept a consequential trade-off, who must be consulted and who can execute it; neither identifying a concern nor holding a meeting grants permission to act.

**Trigger and required inputs:** A change alters commitments or transfers risk/cost across roles, teams or external parties. Actual organisational or contractual authority, implementation capability and access to affected perspectives.

**Produced constraint/evidence:** The decision and its execution can be attributed to authorised participants, with unresolved disagreement visible. Its consumer is: Trade-off decision makers, implementers and affected consumers; authority is supplied by the real context, not this ledger.

**Costs, substitution and omission:** Existing role agreements and a direct decision conversation may suffice; do not invent a new approval body.

**Assumptions, conflicts and failure:** Formal governance can become a veto bottleneck or hide whose interests dominate; the literature does not supply a universal authority hierarchy.

**Retirement/reopening:** Reopen when responsibility, exposure or the original decision mandate changes.

**Abstraction:** Consequential decisions and commitments at organisational/software interfaces. **Evidence boundary:** Confirm the specific decision was authorised and implemented; neither count approvals nor infer benefit from permission. Formal governance can become a veto bottleneck or hide whose interests dominate; the literature does not supply a universal authority hierarchy.

**Relations:** ESA-REL002, ESA-REL004, ESA-REL051. **Tensions:** ESA-T001. **Source IDs:** ESA-S017, ESA-S020, ESA-S035, ESA-S030, ESA-S031.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-006` — Architecture as an unrestricted important-decisions label

Status: `NO_GENERAL_PROPERTY`. Kind: `REJECTED_UNIVERSAL_OR_CEREMONIAL_CLAIM`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. Candidate shorthand groups salient decisions, but without a scope or consequence test it does not determine what architectural work should occur. Disposition: NO_GENERAL_PROPERTY.

**Trigger and required inputs:** The label is used to claim authority over all important engineering or business matters. An explicit definition and unit of analysis would be needed for a usable narrower claim.

**Produced constraint/evidence:** No general engineering postcondition follows from relabelling a decision as architecture. Its consumer is: Researchers and practitioners choosing the scope of an architectural inquiry.

**Costs, substitution and omission:** Use the consequence-bound criterion in ESA-001 and state the architectural object.

**Assumptions, conflicts and failure:** The shorthand is circular when importance is undefined and can annex detailed design, governance or enterprise strategy.

**Retirement/reopening:** Reconsider only with a discriminating definition, not a new slogan.

**Abstraction:** Definitional boundary between architecture and other consequential work. **Evidence boundary:** Not applicable as an operating-quality measure: this is a rejected universal definition, not a quality mechanism. The shorthand is circular when importance is undefined and can annex detailed design, governance or enterprise strategy.

**Relations:** ESA-REL052. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S002, ESA-S010.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-007` — Change-oriented information hiding

Status: `STRONGLY_RETAINED`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Place knowledge of a plausibly varying design decision behind an interface whose clients need not depend on that decision; separate stable obligations from hidden choices.

**Trigger and required inputs:** A likely change currently propagates through clients that need only the stable service or invariant. A defensible change hypothesis and an interface that can express required behaviour without leaking the hidden choice.

**Produced constraint/evidence:** The selected change can be made without corresponding changes in clients that should be insulated. Its consumer is: Module designers and dependent implementers/maintainers.

**Costs, substitution and omission:** Keep a straightforward local implementation where the variation is unlikely or the extra boundary costs more than the expected change.

**Assumptions, conflicts and failure:** Wrong change predictions, performance-sensitive interfaces and hidden semantic dependencies defeat the isolation; more modules are not automatically better.

**Retirement/reopening:** Reopen the boundary when the actual change pattern or performance needs contradict its original rationale.

**Abstraction:** Module responsibilities and design-knowledge boundaries, not deployment units. **Evidence boundary:** Try a representative change and observe affected obligations and components; do not equate module count with modifiability. Wrong change predictions, performance-sensitive interfaces and hidden semantic dependencies defeat the isolation; more modules are not automatically better.

**Relations:** ESA-REL006, ESA-REL026, ESA-REL041, ESA-REL048, ESA-REL065. **Tensions:** ESA-T002, ESA-T003. **Source IDs:** ESA-S001, ESA-S006, ESA-S026.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-008` — Semantic interface assumptions made testable

Status: `STRONGLY_RETAINED`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Express consequential assumptions about state, control, ordering, data meaning, faults and side effects at the interface; check the assumptions actually relied on by both sides.

**Trigger and required inputs:** Parts are composed, reused or replaced and nominal signatures do not capture their operating expectations. Access to both producer and consumer assumptions, including implicit shared resources and environment behaviour.

**Produced constraint/evidence:** A selected interaction works under stated preconditions, and incompatible assumptions are detected before being treated as safe composition. Its consumer is: Both sides of the interface and integration reviewers; no side may silently expand the other’s obligations.

**Costs, substitution and omission:** Use concrete examples, assertions or focused integration tests for a narrow local interface; a full formal contract is not mandatory.

**Assumptions, conflicts and failure:** Contracts can be incomplete or interpreted differently; tests sample behaviour and a formal model still needs implementation correspondence.

**Retirement/reopening:** Reopen on changed error, state, timing or version semantics, even if the signature is unchanged.

**Abstraction:** Semantic contracts at component, service or connector boundaries. **Evidence boundary:** Exercise ordering, failure, shared-state and side-effect cases relevant to the integration. Contracts can be incomplete or interpreted differently; tests sample behaviour and a formal model still needs implementation correspondence.

**Relations:** ESA-REL006, ESA-REL007, ESA-REL011, ESA-REL012, ESA-REL019, ESA-REL026, ESA-REL031, ESA-REL036, ESA-REL043, ESA-REL044, ESA-REL050, ESA-REL051. **Tensions:** ESA-T002, ESA-T006. **Source IDs:** ESA-S026, ESA-S015, ESA-S035.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-009` — Connectors as explicit interaction mechanisms

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Model or inspect the actual interaction mechanism—call, event, stream, shared store or protocol—and its control/data consequences instead of treating an arrow as self-explanatory.

**Trigger and required inputs:** Interaction semantics affect coupling, performance, consistency, failure handling or allowed composition. Knowledge of communication direction, synchrony, state and failure behaviour.

**Produced constraint/evidence:** Consumers can explain what an interaction does and which participant or shared resource controls it. Its consumer is: Component authors, protocol designers and integration/operations staff.

**Costs, substitution and omission:** Name and test a simple direct call; do not create a connector abstraction or framework when ordinary language captures the needed semantics.

**Assumptions, conflicts and failure:** Reifying every connector adds machinery; an explicitly drawn connector can still hide transport, state or callback assumptions.

**Retirement/reopening:** Reopen when transport, synchrony, multiplicity or shared-resource behaviour changes.

**Abstraction:** Runtime and logical interaction relations, at the level required by the concern. **Evidence boundary:** Test the selected interaction’s response, blocking and failure properties rather than count arrows. Reifying every connector adds machinery; an explicitly drawn connector can still hide transport, state or callback assumptions.

**Relations:** ESA-REL007, ESA-REL019, ESA-REL026, ESA-REL043, ESA-REL048, ESA-REL050, ESA-REL051. **Tensions:** ESA-T002. **Source IDs:** ESA-S002, ESA-S004, ESA-S015, ESA-S026.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-010` — Dependency kinds and uses relations distinguished

Status: `STRONGLY_RETAINED`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Distinguish compile/import, invocation, data, correctness, deployment and change dependencies; choose the relation that can answer the architectural question.

**Trigger and required inputs:** A dependency graph is being used to infer independence, change impact or coordination needs. A declared definition for every edge and a known extraction/observation scope.

**Produced constraint/evidence:** Claims about change or failure propagation use an appropriate dependency kind with missing edges acknowledged. Its consumer is: Analysts and engineers making impact or boundary decisions from dependency evidence.

**Costs, substitution and omission:** Inspect the few relevant dependencies manually; do not build a global graph when a local semantic explanation suffices.

**Assumptions, conflicts and failure:** An acyclic import graph can coexist with shared-state or runtime cycles; co-change can reflect work habits rather than necessary coupling.

**Retirement/reopening:** Reopen when generated code, configuration, shared data or usage introduces a different dependency kind.

**Abstraction:** Typed relationships between software responsibilities, runtime units and work items. **Evidence boundary:** Compare predicted propagation with representative changes or executions; graph density alone is not correctness dependence. An acyclic import graph can coexist with shared-state or runtime cycles; co-change can reflect work habits rather than necessary coupling.

**Relations:** ESA-REL006, ESA-REL008, ESA-REL044. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S006, ESA-S045, ESA-S031, ESA-S005, ESA-S026.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-011` — Demonstrated containment rather than nominal isolation

Status: `ASSUMPTION_SENSITIVE`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Demonstrate the claimed containment property under the relevant fault or change, including shared state, resources and management channels; distinguish naming a boundary from enforcing it.

**Trigger and required inputs:** A design relies on independent failure, deployment, access or change behaviour. Explicit containment scope, admissible fault/change model and control over the channels crossing the boundary.

**Produced constraint/evidence:** The stated disturbance remains within its declared effect envelope under the examined conditions. Its consumer is: Engineers and operators relying on independence for a specific quality or change.

**Costs, substitution and omission:** Do not claim independence where it is unnecessary; a coordinated shared unit can be the simpler honest design.

**Assumptions, conflicts and failure:** Shared databases, resource exhaustion, hidden consumers and common administration can invalidate isolation despite separate processes.

**Retirement/reopening:** Reopen after a shared dependency, privileged path or workload undermines the containment assumptions.

**Abstraction:** Fault, state and change-containment boundaries across components or deployments. **Evidence boundary:** Fault/change injection or concrete dependency checks within a defined envelope; passing one test is not universal isolation. Shared databases, resource exhaustion, hidden consumers and common administration can invalidate isolation despite separate processes.

**Relations:** ESA-REL007. **Tensions:** ESA-T006. **Source IDs:** ESA-S026, ESA-S035, ESA-S056, ESA-S054.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-012` — Coordination-aware boundary placement

Status: `CONTEXT_DEPENDENT`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Place boundaries by considering change coupling, communication, translation and operation costs together; compare local and distributed alternatives.

**Trigger and required inputs:** A boundary can reduce change propagation but creates a material coordination or runtime burden. Workload and change hypotheses, team capabilities and known cross-boundary invariants.

**Produced constraint/evidence:** The chosen boundary has a rationale in terms of avoided propagation and incurred coordination, with a viable comparison. Its consumer is: Component teams and those accountable for end-to-end delivery and operation.

**Costs, substitution and omission:** Keep collaborating responsibilities in a coherent local module/deployment when independent operation has no demonstrated consumer.

**Assumptions, conflicts and failure:** Both premature fragmentation and oversized shared units can raise costs; organisational matching studies do not prescribe exact boundaries.

**Retirement/reopening:** Reopen when teams, release cadence, scaling or semantic coupling stop matching the boundary rationale.

**Abstraction:** Logical, team and deployment boundary choices, which need not coincide. **Evidence boundary:** Observe changes requiring cross-team work and operational overhead under representative demand. Both premature fragmentation and oversized shared units can raise costs; organisational matching studies do not prescribe exact boundaries.

**Relations:** ESA-REL008, ESA-REL009, ESA-REL011, ESA-REL030. **Tensions:** ESA-T006. **Source IDs:** ESA-S001, ESA-S031, ESA-S039, ESA-S026, ESA-S037, ESA-S060.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-013` — Commonality and variability within an architectural family

Status: `DOMAIN_SPECIFIC`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Identify common and varying obligations across a genuine set of related systems, then arrange abstractions and uses relations to support required variants or subsets.

**Trigger and required inputs:** Multiple related products or configurations have known shared structure and deliberate variation. An examined family scope, variation constraints and dependencies that permit the desired combinations.

**Produced constraint/evidence:** Required family members or subsets can be constructed without accidentally importing incompatible obligations. Its consumer is: Family/product architects and developers selecting valid members; economic product-line decisions remain a later interface.

**Costs, substitution and omission:** Build the single required system directly when a family is speculative; defer variation points with no credible consumer.

**Assumptions, conflicts and failure:** Generalising too early creates unused flexibility; feature combinations may violate quality assumptions even when structurally available.

**Retirement/reopening:** Reopen when a new family member changes commonality or invalidates permitted combinations.

**Abstraction:** Architecture of related program families, shared assets and variation boundaries. **Evidence boundary:** Check required variants against functional/quality constraints and the cost of producing them, not raw reuse percentage. Generalising too early creates unused flexibility; feature combinations may violate quality assumptions even when structurally available.

**Relations:** ESA-REL011, ESA-REL012, ESA-REL041, ESA-REL065. **Tensions:** ESA-T003, ESA-T010. **Source IDs:** ESA-S006, ESA-S064, ESA-S007, ESA-S066.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-014` — Measurable quality-attribute scenarios

Status: `STRONGLY_RETAINED`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Express a quality concern through stimulus, source, environment, affected artefact, response and response measure, tailoring detail to the decision being made.

**Trigger and required inputs:** A quality term such as fast, secure, usable or modifiable must discriminate between designs. Relevant stimulus/environment and an agreed meaning for the response measure and acceptable range.

**Produced constraint/evidence:** An alternative can be judged against a testable quality condition rather than a generic adjective. Its consumer is: Stakeholders, designers, evaluators and testers consuming a shared condition.

**Costs, substitution and omission:** A short, concrete example with an observable acceptable response can suffice; do not fill six empty boxes ceremonially.

**Assumptions, conflicts and failure:** A precisely measured scenario can still be irrelevant or exclude important people and conditions.

**Retirement/reopening:** Reopen on changed demand, environment, acceptance criteria or evidence that the measure misses the concern.

**Abstraction:** Quality requirements at the system or affected architectural element. **Evidence boundary:** The scenario’s own response measure—e.g. percentile latency under stated load or effort for a specified change. A precisely measured scenario can still be irrelevant or exclude important people and conditions.

**Relations:** ESA-REL001, ESA-REL002, ESA-REL003, ESA-REL027, ESA-REL046, ESA-REL048. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S016, ESA-S017, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-015` — Scenario population and selection validity

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Examine which users, operating states, changes and adverse cases the scenario set represents; add decision-changing omissions and preserve uncertainty rather than treating prioritisation as completeness.

**Trigger and required inputs:** An evaluation or design claim depends on a selected set of scenarios. Knowledge of relevant stakeholders and operating variation plus a means to challenge the initial scenario selection.

**Produced constraint/evidence:** The conclusion states the population to which scenarios apply and the consequential conditions not covered. Its consumer is: Evaluators and affected participants, including dissenting or absent-user representatives where warranted.

**Costs, substitution and omission:** Use a few explicit favourable, adverse and boundary cases for a small decision, with limits stated; avoid exhaustive catalogues with no consumer.

**Assumptions, conflicts and failure:** Rare but serious conditions can lose a vote; familiar workloads and author reference cases can anchor the assessment.

**Retirement/reopening:** Reopen when a new user, failure, workload or change pattern could reverse the decision.

**Abstraction:** Scenario population, sampling and prioritisation at evaluation scope. **Evidence boundary:** Coverage is judged against the decision’s concern population; number of scenarios alone does not establish representativeness. Rare but serious conditions can lose a vote; familiar workloads and author reference cases can anchor the assessment.

**Relations:** ESA-REL002, ESA-REL003, ESA-REL015, ESA-REL044. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S017, ESA-S020, ESA-S021, ESA-S023, ESA-S060.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-016` — Tactics tied to explanatory quality models

Status: `ASSUMPTION_SENSITIVE`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Connect a tactic to the model parameters it changes and to the response sought; account for interactions, overhead and assumptions that make the causal explanation plausible.

**Trigger and required inputs:** A structural or behavioural intervention is proposed to improve a quality attribute. A suitable causal/analytic model and valid workload, fault, timing or human-use assumptions.

**Produced constraint/evidence:** Predicted quality effects have an explicit explanation and are checked at the level needed for the decision. Its consumer is: Designers selecting interventions and evaluators testing their consequences.

**Costs, substitution and omission:** Use a targeted prototype or direct simplification instead of a tactic taxonomy when it answers the causal question more cheaply.

**Assumptions, conflicts and failure:** Redundancy may share faults; caches can break freshness; abstraction can add overhead. A tactic name proves none of its claimed effects.

**Retirement/reopening:** Reopen when workload, failure independence or model calibration no longer supports the tactic.

**Abstraction:** Architectural tactic acting on performance, availability, security, modifiability or other modelled qualities. **Evidence boundary:** Compare the affected quality response before/after or across viable alternatives while monitoring competing responses. Redundancy may share faults; caches can break freshness; abstraction can add overhead. A tactic name proves none of its claimed effects.

**Relations:** ESA-REL003, ESA-REL013, ESA-REL015, ESA-REL025, ESA-REL026, ESA-REL048. **Tensions:** ESA-T002. **Source IDs:** ESA-S016, ESA-S024, ESA-S026, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-017` — Explicit interacting-quality trade-offs and constraints

Status: `STRONGLY_RETAINED`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Separate hard constraints from preferences, compare effects on multiple concerns and make the chosen sacrifice explicit; do not aggregate away unacceptable consequences.

**Trigger and required inputs:** Improving one response can worsen another or transfer cost to a different stakeholder. Identified concerns, non-negotiable limits, feasible alternatives and legitimate trade-off authority.

**Produced constraint/evidence:** The chosen alternative remains within its stated constraints and its foregone benefits/costs are visible. Its consumer is: Affected stakeholders and authorised trade-off decision makers.

**Costs, substitution and omission:** Eliminate dominated or infeasible options through a brief explicit comparison when elaborate utility modelling adds no decision value.

**Assumptions, conflicts and failure:** Utility weights can launder unacceptable harms or double-count dependent benefits; apparent Pareto improvements can omit a cost boundary.

**Retirement/reopening:** Reopen when a hard limit is violated, a preference changes or a formerly omitted consequence becomes material.

**Abstraction:** Multi-quality architectural alternatives and external constraints. **Evidence boundary:** Check each critical scenario plus cost/latency/coordination consequences; a single composite score is insufficient evidence. Utility weights can launder unacceptable harms or double-count dependent benefits; apparent Pareto improvements can omit a cost boundary.

**Relations:** ESA-REL003, ESA-REL012, ESA-REL013, ESA-REL014, ESA-REL024, ESA-REL026, ESA-REL031, ESA-REL036, ESA-REL043, ESA-REL046, ESA-REL050, ESA-REL053. **Tensions:** ESA-T006, ESA-T008. **Source IDs:** ESA-S016, ESA-S020, ESA-S022, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-018` — Representative workload and failure observations

Status: `STRONGLY_RETAINED`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Validate important predictions against observations whose workload, faults, configuration and measurement boundary are representative of the decision; distinguish the measurement from the whole quality claim.

**Trigger and required inputs:** A prototype, benchmark, trace or field observation is being used to accept an architecture. Measurement validity, declared test configuration and knowledge of the target operating envelope.

**Produced constraint/evidence:** The accepted claim identifies the examined conditions and fails or reopens when observations depart from them. Its consumer is: Testers, operators and decision makers relying on measured outcomes.

**Costs, substitution and omission:** Use the smallest representative experiment or inspect existing evidence; do not run a broad benchmark suite unrelated to the risk.

**Assumptions, conflicts and failure:** Passing benchmarks can conceal workload shifts, hidden energy costs, averaged tail behaviour or silently broken monitors.

**Retirement/reopening:** Reopen after load, hardware, dependencies or telemetry changes, or when production contradicts the prediction.

**Abstraction:** Empirical evidence about realised architectural behaviour, not just models. **Evidence boundary:** Use response distributions and failure observations tied to the scenario, with uncertainty and unobserved paths disclosed. Passing benchmarks can conceal workload shifts, hidden energy costs, averaged tail behaviour or silently broken monitors.

**Relations:** ESA-REL013, ESA-REL015, ESA-REL036, ESA-REL037, ESA-REL038, ESA-REL040, ESA-REL043, ESA-REL044, ESA-REL046, ESA-REL051, ESA-REL055, ESA-REL062. **Tensions:** ESA-T007. **Source IDs:** ESA-S016, ESA-S020, ESA-S054, ESA-S048, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-019` — Independent maximisation of every quality

Status: `REJECTED_OR_DISFAVOURED`. Kind: `REJECTED_UNIVERSAL_OR_CEREMONIAL_CLAIM`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. Independent maximisation ignores interaction and feasibility; it is not retained as an engineering rule. Disposition: REJECTED_OR_DISFAVOURED.

**Trigger and required inputs:** A proposal claims every quality improves without defining resource, stakeholder or environmental boundaries. Only demonstrably independent, compatible objectives could support a local version; independence must be shown, not assumed.

**Produced constraint/evidence:** No general postcondition exists; improvement in all measured values can still omit an external cost. Its consumer is: Anyone interpreting a multi-quality improvement claim.

**Costs, substitution and omission:** Use ESA-017 to compare constrained alternatives and identify any genuine dominated option.

**Assumptions, conflicts and failure:** Finite resources and competing mechanisms invalidate the universal claim; EcoFaaS explicitly exchanges mean latency for energy.

**Retirement/reopening:** Reconsider a local all-better result only with a complete declared comparison and measurement boundary.

**Abstraction:** An inadmissible general optimisation claim over architectural qualities. **Evidence boundary:** Not applicable as a universal measure; use separate scenario outcomes and boundary-complete costs. Finite resources and competing mechanisms invalidate the universal claim; EcoFaaS explicitly exchanges mean latency for energy.

**Relations:** ESA-REL053. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S016, ESA-S020, ESA-S022, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-020` — Concern-selected views and viewpoints

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Select viewpoints by the concerns and decisions they enable, then create only the views needed to communicate or analyse those concerns.

**Trigger and required inputs:** One representation obscures materially different structural, runtime, deployment or development questions. Clear purpose and audience for each view, consistent vocabulary and a way to relate overlapping elements.

**Produced constraint/evidence:** Each retained view has a consumer and an architectural question that could not be adequately answered more cheaply. Its consumer is: Description authors and the actual stakeholders or analysts using each view.

**Costs, substitution and omission:** A single annotated sketch or direct walkthrough may suffice when it answers every consequential question at hand.

**Assumptions, conflicts and failure:** Mandating a familiar view set produces obsolete or redundant documents; notation can be mistaken for semantic content.

**Retirement/reopening:** Reopen or retire views when their concern, consumer or decision disappears or a cheaper representation suffices.

**Abstraction:** Architecture descriptions and viewpoint conventions at concern-specific abstraction levels. **Evidence boundary:** Check stakeholder interpretation and decision usability, not completeness against an arbitrary diagram template. Mandating a familiar view set produces obsolete or redundant documents; notation can be mistaken for semantic content.

**Relations:** ESA-REL016, ESA-REL047, ESA-REL054. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S003, ESA-S011, ESA-S014, ESA-S012, ESA-S013, ESA-S010.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-021` — Correspondence between views and realisation

Status: `STRONGLY_RETAINED`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Identify how entities and relations in different views correspond, then check consequential consistency and the link to implementation/configuration/operation.

**Trigger and required inputs:** A decision combines claims from several views or uses a model as evidence about implementation. Defined mapping rules and dependency meanings; evidence about the real artefacts to which the views refer.

**Produced constraint/evidence:** Relevant contradictions are explained or corrected, and unverified correspondences are not presented as facts. Its consumer is: Design, deployment, development and evaluation participants relying on combined descriptions.

**Costs, substitution and omission:** Check a small set of named correspondences manually rather than maintain a universal metamodel.

**Assumptions, conflicts and failure:** Consistent views can be consistently wrong; transformation correctness does not validate the input model.

**Retirement/reopening:** Reopen after mapping, model or implementation changes that affect a relied-upon correspondence.

**Abstraction:** Cross-view and description–implementation relations, not visual layout similarity. **Evidence boundary:** Trace selected obligations through views to code/configuration or execution, recording unmatched or ambiguous elements. Consistent views can be consistently wrong; transformation correctness does not validate the input model.

**Relations:** ESA-REL005, ESA-REL016, ESA-REL017, ESA-REL020, ESA-REL038, ESA-REL040, ESA-REL062. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S003, ESA-S011, ESA-S045, ESA-S026.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-022` — Formal architectural descriptions with bounded guarantees

Status: `DOMAIN_SPECIFIC`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Use a formal description when a consequential property can be expressed and analysed under a tractable model; keep the guarantee, assumptions and implementation mapping explicit.

**Trigger and required inputs:** An interaction/configuration property justifies stronger analysis than informal review or testing alone. Formal semantics, competent modelling, tractable state space and defensible abstraction/refinement.

**Produced constraint/evidence:** The stated property is established for the specified model, without silently extending it to unmodelled behaviour. Its consumer is: Modellers, verification specialists and engineers responsible for implementing the model’s assumptions.

**Costs, substitution and omission:** A focused protocol model, contract or ordinary test can dominate a whole-system ADL when it answers the risk.

**Assumptions, conflicts and failure:** State explosion, model drift and environmental mismatch can make formally correct analysis operationally irrelevant.

**Retirement/reopening:** Reopen on changed semantics, topology, implementation mapping or environment assumptions.

**Abstraction:** Formal component/connector/configuration or behaviour models. **Evidence boundary:** Proof/check results plus explicit correspondence obligations; proof alone is not a field-outcome measure. State explosion, model drift and environmental mismatch can make formally correct analysis operationally irrelevant.

**Relations:** ESA-REL017, ESA-REL018, ESA-REL019, ESA-REL047. **Tensions:** ESA-T004. **Source IDs:** ESA-S014, ESA-S015.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-023` — Mandatory complete 4+1 documentation

Status: `CEREMONY_NOT_GENERAL_PROPERTY`. Kind: `REJECTED_UNIVERSAL_OR_CEREMONIAL_CLAIM`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. Completing a prescribed view set regardless of its consumers is ceremony, not a generally useful mechanism. Disposition: CEREMONY_NOT_GENERAL_PROPERTY.

**Trigger and required inputs:** A review treats the existence of all five views as evidence of architectural adequacy. Only a specific contractual or analytical need can justify a mandatory set; that need is not inherent in the brand.

**Produced constraint/evidence:** No general quality postcondition follows from completing five diagrams. Its consumer is: Documentation consumers and reviewers, not a template’s nominal owner.

**Costs, substitution and omission:** Select views through ESA-020; omit views that add no needed distinction or communication.

**Assumptions, conflicts and failure:** The original method explicitly permits irrelevant views to be omitted; mandatory forms can hide obsolete content.

**Retirement/reopening:** Retire mandatory views when no external obligation or actual consumer needs them.

**Abstraction:** An unconditional documentation ritual rather than a system property. **Evidence boundary:** Not applicable to system quality; document presence is merely an artefact count. The original method explicitly permits irrelevant views to be omitted; mandatory forms can hide obsolete content.

**Relations:** ESA-REL054. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S003.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-024` — Triangulated architecture reconstruction with uncertainty

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Combine appropriate static, configuration, dynamic and human evidence to reconstruct only the architectural facts needed; label extraction scope, ambiguity and unobserved behaviour.

**Trigger and required inputs:** Reliable architectural knowledge is missing or an existing description is suspect. Accessible artefacts and runs, known relation semantics and a question against which the reconstruction can be checked.

**Produced constraint/evidence:** Recovered claims carry evidence and uncertainty, and conflicting observations can revise the reconstruction. Its consumer is: Maintainers, migration designers and reviewers who need specific missing knowledge.

**Costs, substitution and omission:** Inspect the relevant implementation paths with an experienced maintainer before building an automated whole-system reconstruction.

**Assumptions, conflicts and failure:** Static imports omit runtime bindings; traces miss unexecuted paths; classifier labels and cluster scores do not recover intent.

**Retirement/reopening:** Reopen when new artefacts, traces or domain testimony contradict the recovered structure.

**Abstraction:** Inferred architectural structures and behaviours from realised artefacts. **Evidence boundary:** Validate sampled recovered relations against source/configuration/execution and known cases, not a diagram’s apparent completeness. Static imports omit runtime bindings; traces miss unexecuted paths; classifier labels and cluster scores do not recover intent.

**Relations:** ESA-REL005, ESA-REL008, ESA-REL020, ESA-REL034, ESA-REL045, ESA-REL058. **Tensions:** ESA-T007. **Source IDs:** ESA-S045, ESA-S014, ESA-S026, ESA-S047, ESA-S046, ESA-S063.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-025` — Styles and patterns as conditional mechanisms

Status: `CONTEXT_DEPENDENT`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Use a style or pattern as a conditional mechanism with an explicit problem, constraints and trade-offs; document purposeful hybrids and their interaction obligations.

**Trigger and required inputs:** A recurring architectural problem matches the style’s assumptions closely enough to reduce design or analysis effort. Understanding of the style’s actual semantics, not only its name; compatibility of combined mechanisms.

**Produced constraint/evidence:** The adopted structure exhibits the relevant mechanism and satisfies its selected concerns under stated assumptions. Its consumer is: Designers and reviewers selecting, combining or declining architectural mechanisms.

**Costs, substitution and omission:** Use a direct design without a pattern label when the pattern adds indirection or excludes a better local arrangement.

**Assumptions, conflicts and failure:** Pattern fashion, architectural mismatch and incoherent hybrids can create complexity while preserving only the label.

**Retirement/reopening:** Reopen or remove the pattern when its motivating problem vanishes or its constraints prevent the desired qualities.

**Abstraction:** Component-and-connector styles and recurring architectural solution structures. **Evidence boundary:** Test the style’s claimed response and imposed costs in the target scenario; adoption frequency is not effectiveness. Pattern fashion, architectural mismatch and incoherent hybrids can create complexity while preserving only the label.

**Relations:** ESA-REL007, ESA-REL041. **Tensions:** ESA-T010. **Source IDs:** ESA-S004, ESA-S014, ESA-S034, ESA-S026, ESA-S037, ESA-S039.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-026` — Comparison with feasible alternatives and no change

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Compare feasible architectural options, including retaining the present design or a smaller intervention, against the same concerns and assumptions; expose excluded options.

**Trigger and required inputs:** A consequential investment or restructuring is being justified. Common evaluation conditions, feasible options and transparent reasons for excluding infeasible or unacceptable designs.

**Produced constraint/evidence:** The decision can be explained relative to an actual alternative and the cost of doing nothing, not just the favoured design’s virtues. Its consumer is: Design sponsors, implementers and stakeholders accepting costs or foregone options.

**Costs, substitution and omission:** Use a short explicit comparison when one option is plainly dominated; do not fabricate many alternatives for a form.

**Assumptions, conflicts and failure:** Anchoring on an incumbent or fashionable replacement can determine the result before analysis; unequal prototypes can bias comparison.

**Retirement/reopening:** Reopen when an excluded option becomes feasible or evidence changes the comparison.

**Abstraction:** Architectural alternatives and decision counterfactuals. **Evidence boundary:** Compare response measures, costs and risks under equivalent scenarios; identify missing evidence rather than invent utility values. Anchoring on an incumbent or fashionable replacement can determine the result before analysis; unequal prototypes can bias comparison.

**Relations:** ESA-REL003, ESA-REL021, ESA-REL024, ESA-REL025, ESA-REL027, ESA-REL029, ESA-REL035, ESA-REL045. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S019, ESA-S020, ESA-S022, ESA-S010, ESA-S037, ESA-S039, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-027` — Change-scenario architectural evaluation

Status: `CONTEXT_DEPENDENT`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Walk representative modifications through an architecture, identify affected elements and interacting scenarios, and compare the resulting burdens across alternatives.

**Trigger and required inputs:** Modifiability or the consequences of planned change are material and can be expressed as concrete scenarios. Architecture knowledge, credible change scenarios and estimates grounded in how modifications would actually be made.

**Produced constraint/evidence:** The evaluation reveals where changes propagate and where multiple changes depend on the same structural decision. Its consumer is: Evaluators and maintainers choosing a design or restructuring.

**Costs, substitution and omission:** Walk a single realistic change through the current code and a proposed alternative if a full workshop is unnecessary.

**Assumptions, conflicts and failure:** Scenario choice and assessor expertise dominate; counting affected elements can misrepresent effort or hidden semantic work.

**Retirement/reopening:** Reopen when actual changes differ materially from the scenario population.

**Abstraction:** Architecture under prospective functional or quality-related modifications. **Evidence boundary:** Compare explained change impact and, when available, actual later change work; do not equate workshop completion with prediction accuracy. Scenario choice and assessor expertise dominate; counting affected elements can misrepresent effort or hidden semantic work.

**Relations:** ESA-REL021, ESA-REL022, ESA-REL047. **Tensions:** ESA-T004. **Source IDs:** ESA-S019, ESA-S023.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-028` — Multi-quality risk and sensitivity evaluation

Status: `CONTEXT_DEPENDENT`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Bring business/mission drivers, architecture and quality scenarios into a structured review to identify assumptions, risks, sensitivity points and trade-offs that need a decision.

**Trigger and required inputs:** Several consequential qualities interact and missing assumptions justify a facilitated multi-stakeholder review. Sufficient architecture detail, informed stakeholders, capable evaluators and ability to act on discovered risks.

**Produced constraint/evidence:** Decision makers receive actionable, assumption-bound risks and trade-offs rather than an unexplained approval stamp. Its consumer is: Stakeholders, evaluation facilitators and people authorised to accept or mitigate the identified risks.

**Costs, substitution and omission:** Use a focused risk/assumption review with the necessary participants for a small decision; the full event structure is not mandatory.

**Assumptions, conflicts and failure:** The reviewed evidence largely concerns discovered risks and perceived usefulness; prediction and downstream economic benefit are less well established.

**Retirement/reopening:** Reopen non-risks and trade-offs when the assumptions or operating scenario change.

**Abstraction:** Multi-quality evaluation of an architectural candidate. **Evidence boundary:** Assess the relevance and handling of identified risks; separately test any claimed effect on deployed qualities or cost. The reviewed evidence largely concerns discovered risks and perceived usefulness; prediction and downstream economic benefit are less well established.

**Relations:** ESA-REL003, ESA-REL021, ESA-REL022, ESA-REL023, ESA-REL045, ESA-REL047, ESA-REL055. **Tensions:** ESA-T004. **Source IDs:** ESA-S020, ESA-S021, ESA-S023.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-029` — Economic evaluation with uncertainty and dependency

Status: `ASSUMPTION_SENSITIVE`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Establish feasible options and hard constraints first, then explore plausible costs, utilities, dependencies and sensitivity rather than treating one estimated ratio as an objective answer.

**Trigger and required inputs:** Several acceptable alternatives compete for constrained resources and economic consequences may change the choice. Meaningful stakeholder preferences, comparable costs, explicit uncertainty and defensible treatment of dependent benefits.

**Produced constraint/evidence:** The preferred option and the assumptions under which it would change are visible to decision makers. Its consumer is: Budget/benefit decision makers and affected stakeholders; the model advises rather than owns the decision.

**Costs, substitution and omission:** Use cost ranges, break-even reasoning or dominance checks when a detailed utility model adds unjustified precision.

**Assumptions, conflicts and failure:** Additive utility can double-count coupled benefits, conceal unequal burdens or trade away a hard limit; elicited numbers may be unstable.

**Retirement/reopening:** Reopen when costs, utility judgements, dependencies or opportunity costs cross a decision-changing boundary.

**Abstraction:** Architectural investment alternatives, costs and stakeholder preference models. **Evidence boundary:** Use ranges and sensitivity of the actual decision, not spurious confidence percentages or monetised values unsupported by evidence. Additive utility can double-count coupled benefits, conceal unequal burdens or trade away a hard limit; elicited numbers may be unstable.

**Relations:** ESA-REL014, ESA-REL021, ESA-REL023, ESA-REL024, ESA-REL046, ESA-REL047. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S022, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-030` — Targeted prototypes and calibrated analytic models

Status: `CONTEXT_DEPENDENT`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Choose a focused prototype, simulation or analytic model for the uncertainty at hand; calibrate it where possible and distinguish omitted behaviour from demonstrated behaviour.

**Trigger and required inputs:** A consequential prediction cannot be judged adequately by reasoning or existing observations alone. A discriminating question, representative model inputs and awareness of what the prototype leaves out.

**Produced constraint/evidence:** The experiment changes or supports the architectural decision with a bounded claim and observable result. Its consumer is: Designers and evaluators responsible for uncertainty reduction, not for treating an experiment as automatic release authority.

**Costs, substitution and omission:** Use a small experiment or direct inspection of the uncertain mechanism rather than a production-like prototype of everything.

**Assumptions, conflicts and failure:** A prototype can omit precisely the error handling, scale or coordination that dominates real operation; calibration can overfit one workload.

**Retirement/reopening:** Reopen when the operating regime or implementation diverges from what the prototype represented.

**Abstraction:** Prototype, simulation or analytic model tied to a real architectural decision. **Evidence boundary:** Compare predicted and observed responses within the modelled envelope; disclose external-validity gaps. A prototype can omit precisely the error handling, scale or coordination that dominates real operation; calibration can overfit one workload.

**Relations:** ESA-REL015, ESA-REL018, ESA-REL021, ESA-REL025, ESA-REL027. **Tensions:** ESA-T004. **Source IDs:** ESA-S016, ESA-S020, ESA-S024, ESA-S008, ESA-S054, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-031` — Review success as a guarantee of operating quality

Status: `REJECTED_OR_DISFAVOURED`. Kind: `REJECTED_UNIVERSAL_OR_CEREMONIAL_CLAIM`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. A review can establish that a process occurred and risks were considered; it cannot by itself guarantee the real system under unexamined conditions. Disposition: REJECTED_OR_DISFAVOURED.

**Trigger and required inputs:** An approval, risk list or completed workshop is used as conclusive evidence that the system will meet its qualities. A stronger local claim requires valid scenarios, sound analysis and implementation/environment correspondence.

**Produced constraint/evidence:** No general runtime guarantee follows from review success alone. Its consumer is: People accepting a design or relying on its review status.

**Costs, substitution and omission:** Keep the review’s actual conclusions and obtain the missing representative evidence through ESA-018.

**Assumptions, conflicts and failure:** Omissions, model mismatch and unrepresentative workloads break the implication even when the review was performed competently.

**Retirement/reopening:** Reject the inference whenever a necessary assumption or observation is absent; reconsider only the narrower supported claim.

**Abstraction:** Inference from evaluation process completion to realised performance or correctness. **Evidence boundary:** Not applicable as a direct quality measure: approval status and operating response are different observations. Omissions, model mismatch and unrepresentative workloads break the implication even when the review was performed competently.

**Relations:** ESA-REL055. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S020, ESA-S021, ESA-S023, ESA-S054.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-032` — Recoverable decision rationale for later consumers

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Preserve the context, selected option, significant alternatives, consequences and assumptions that a future actor needs to understand or revise a consequential decision.

**Trigger and required inputs:** A decision is non-obvious, likely to recur or needs to survive turnover and distributed work. A known future consumer and links to the affected structures or obligations; alternatives are an analytical addition where needed, not a universal template field.

**Produced constraint/evidence:** A later actor can explain the choice and identify evidence that would justify changing it without reconstructing everything from scratch. Its consumer is: Current decision participants and later maintainers, reviewers or successors.

**Costs, substitution and omission:** A short linked note or direct shared understanding can suffice for a local reversible decision; do not record all reasoning exhaustively.

**Assumptions, conflicts and failure:** Records become stale, verbose or retrofitted justifications; survey perceptions do not prove a universal return on documentation effort.

**Retirement/reopening:** Reopen when an assumption, excluded alternative or accepted consequence changes materially.

**Abstraction:** Architectural decision knowledge linked to structures, constraints and evidence. **Evidence boundary:** Test a realistic later question against the retained rationale; record count and word count are not adequacy measures. Records become stale, verbose or retrofitted justifications; survey perceptions do not prove a universal return on documentation effort.

**Relations:** ESA-REL016, ESA-REL023, ESA-REL028, ESA-REL045, ESA-REL047, ESA-REL049, ESA-REL057. **Tensions:** ESA-T009. **Source IDs:** ESA-S009, ESA-S027, ESA-S028, ESA-S029.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-033` — Decision ageing, supersession and reopening

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Keep a decision’s status and reopening conditions visible; distinguish superseding it from erasing the evidence that once justified it.

**Trigger and required inputs:** Architectural choices outlive their original workload, team, dependency or business assumptions. Identifiable decision context, current evidence and someone able to revise the affected commitment.

**Produced constraint/evidence:** Consumers can distinguish current guidance from historical rationale and know why it changed. Its consumer is: Maintainers and authorised decision revisers; a record itself does not grant revision authority.

**Costs, substitution and omission:** Update a short status/link at the affected decision; no periodic meeting is needed when nothing decision-relevant has changed.

**Assumptions, conflicts and failure:** Keeping every obsolete record without navigable status can increase confusion; automated expiry dates can trigger meaningless reviews.

**Retirement/reopening:** The stated assumption or consequence changes, a better option appears, or the decision is no longer consequential.

**Abstraction:** Time-indexed architectural decisions and their dependency links. **Evidence boundary:** Check whether a changed assumption reaches the appropriate decision and whether superseded material is clearly marked. Keeping every obsolete record without navigable status can increase confusion; automated expiry dates can trigger meaningless reviews.

**Relations:** ESA-REL023, ESA-REL028, ESA-REL029, ESA-REL033, ESA-REL036, ESA-REL037, ESA-REL040, ESA-REL044, ESA-REL049. **Tensions:** ESA-T005, ESA-T009. **Source IDs:** ESA-S020, ESA-S029, ESA-S027.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-034` — Socio-technical coordination of consequential dependencies

Status: `ASSUMPTION_SENSITIVE`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Identify consequential technical/work dependencies and arrange adequate communication across the people who must coordinate them; test the actual coordination problem rather than copying an organisation chart.

**Trigger and required inputs:** Cross-team dependencies cause misunderstandings, delay or incompatible changes. Correctly identified work dependencies and an understanding of existing formal and informal communication channels.

**Produced constraint/evidence:** The relevant participants can resolve dependent decisions in time to preserve the shared obligation. Its consumer is: Teams and organisational decision makers able to alter coordination arrangements.

**Costs, substitution and omission:** Use a direct conversation or temporary collaboration when a lasting team or system reorganisation would cost more.

**Assumptions, conflicts and failure:** Observed congruence and mirroring are not deterministic causal laws; forcing communication everywhere can overwhelm teams.

**Retirement/reopening:** Reopen when work dependencies, team membership, sites or communication channels change.

**Abstraction:** Coupling between software/work dependencies and human communication. **Evidence boundary:** Examine concrete coordination failures and time-to-resolution with confounding disclosed, not just chart alignment. Observed congruence and mirroring are not deterministic causal laws; forcing communication everywhere can overwhelm teams.

**Relations:** ESA-REL008, ESA-REL030, ESA-REL056. **Tensions:** ESA-T001. **Source IDs:** ESA-S030, ESA-S031, ESA-S032.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-035` — Distributed decisions constrained by shared consequences

Status: `CONTEXT_DEPENDENT`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Allow local choices inside explicit shared contracts and escalate or negotiate only decisions that change cross-boundary consequences; preserve a way to resolve conflicts.

**Trigger and required inputs:** Multiple teams need autonomy but share users, data, quality limits or release obligations. Stable shared obligations, actual local competence and an agreed path for resolving non-local effects.

**Produced constraint/evidence:** Local progress does not silently change another team’s contract or an end-to-end constraint. Its consumer is: Local teams and those accountable for shared constraints; delegation is contextual rather than asserted by the method.

**Costs, substitution and omission:** A single team’s common understanding can replace formal delegation structures; avoid review boards for isolated implementation choices.

**Assumptions, conflicts and failure:** Too many global rules remove autonomy; too few create incompatible local optima. A bounded context is not permission to ignore shared invariants.

**Retirement/reopening:** Reopen the allocation when dependency reach or local decision capability changes.

**Abstraction:** Architectural decision allocation across component, product and team boundaries. **Evidence boundary:** Test cross-boundary effects and resolution of real conflicts; number of decentralised decisions is not a quality outcome. Too many global rules remove autonomy; too few create incompatible local optima. A bounded context is not permission to ignore shared invariants.

**Relations:** ESA-REL004, ESA-REL010, ESA-REL028, ESA-REL030, ESA-REL031. **Tensions:** ESA-T001, ESA-T006. **Source IDs:** ESA-S010, ESA-S033, ESA-S036, ESA-S030, ESA-S031, ESA-S039, ESA-S060.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-036` — Deterministic organisational mirroring

Status: `REJECTED_OR_DISFAVOURED`. Kind: `REJECTED_UNIVERSAL_OR_CEREMONIAL_CLAIM`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. No deterministic rule mapping an organisation chart to software architecture is admitted; communication and technical structures influence each other under contingent conditions. Disposition: REJECTED_OR_DISFAVOURED.

**Trigger and required inputs:** A reorganisation is asserted to guarantee a desired architecture or every structural similarity is treated as inevitable. A local causal claim requires evidence about channels, decisions, confounders and alternative explanations.

**Produced constraint/evidence:** No inevitable software topology follows from the organisation chart alone. Its consumer is: Organisational designers and architects considering a socio-technical intervention.

**Costs, substitution and omission:** Investigate the actual dependency/coordination mechanisms through ESA-034.

**Assumptions, conflicts and failure:** Observational matched cases and single-firm regressions do not establish a universal mapping law.

**Retirement/reopening:** Revisit a bounded causal hypothesis only with new discriminating evidence, not rhetorical invocation of a law.

**Abstraction:** Claimed necessary relationship between organisational and software structures. **Evidence boundary:** Not applicable as a deterministic measure; investigate mechanism and outcome in the actual setting. Observational matched cases and single-firm regressions do not establish a universal mapping law.

**Relations:** ESA-REL056. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S030, ESA-S031, ESA-S032.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-037` — Documentation quantity as architectural evidence

Status: `CEREMONY_NOT_GENERAL_PROPERTY`. Kind: `REJECTED_UNIVERSAL_OR_CEREMONIAL_CLAIM`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. Document quantity alone is not retained as a proxy for architectural knowledge, correctness or maintenance value. Disposition: CEREMONY_NOT_GENERAL_PROPERTY.

**Trigger and required inputs:** Page counts, completed templates or a large repository of records are used as assurance. A useful documentation intervention requires a consumer, question and maintained link to the relevant system.

**Produced constraint/evidence:** No useful knowledge postcondition follows merely from more text. Its consumer is: Document authors, maintainers and the users of their explanations.

**Costs, substitution and omission:** Ask a real consumer to recover a needed decision or check a correspondence using the smallest adequate material.

**Assumptions, conflicts and failure:** Fragments, obsolete rationale and conflicting copies can make extensive documentation worse than a concise current account.

**Retirement/reopening:** Retire content whose consumer and decision relevance have disappeared, subject to genuine record-retention obligations.

**Abstraction:** Documentation volume as a candidate architectural quality indicator. **Evidence boundary:** Not a document-volume metric; use retrieval, interpretation and decision correctness for the intended task. Fragments, obsolete rationale and conflicting copies can make extensive documentation worse than a concise current account.

**Relations:** ESA-REL057. **Tensions:** ESA-T009. **Source IDs:** ESA-S009, ESA-S029, ESA-S027, ESA-S041.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-038` — Conformance to a justified, mapped baseline

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Check a declared, justified architectural constraint against appropriately extracted or observed relationships; attach the relevant baseline, mapping and evidence to each finding.

**Trigger and required inputs:** A system depends on a structural or behavioural restriction that implementation changes might violate. A still-relevant constraint and correct mapping between the policy and the realised relationship.

**Produced constraint/evidence:** A finding identifies an actual relation, the applicable rule and the protected concern, allowing informed adjudication. Its consumer is: Constraint owners, implementers and reviewers able to accept or revise the affected design.

**Costs, substitution and omission:** Use a focused code/configuration review or small dependency check; a universal conformance framework is unnecessary.

**Assumptions, conflicts and failure:** Stale rules, incomplete extraction and wrong edge semantics produce false assurance or false alarms; departure alone does not establish harm.

**Retirement/reopening:** Reopen when the baseline’s rationale, extraction scope or relevant system relation changes.

**Abstraction:** Intended constraints mapped to realised static or dynamic architectural relationships. **Evidence boundary:** Validate findings against the protected invariant or quality; measure false positives and missed relations where possible. Stale rules, incomplete extraction and wrong edge semantics produce false assurance or false alarms; departure alone does not establish harm.

**Relations:** ESA-REL005, ESA-REL008, ESA-REL017, ESA-REL020, ESA-REL029, ESA-REL031, ESA-REL032, ESA-REL033, ESA-REL034, ESA-REL047. **Tensions:** ESA-T005. **Source IDs:** ESA-S045, ESA-S002, ESA-S026, ESA-S048, ESA-S046.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-039` — Adjudication of drift and authorised improvement

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** For a deviation, decide whether the implementation is harmful, the model is stale, the change is authorised improvement or evidence is insufficient; revise the correct object.

**Trigger and required inputs:** A realised relationship departs from an architectural baseline. Access to current concerns, baseline rationale, deviation evidence and legitimate change authority.

**Produced constraint/evidence:** The finding has a reasoned disposition tied to current consequences rather than a binary historic-match demand. Its consumer is: Maintainers, evaluators and authorised architecture decision makers.

**Costs, substitution and omission:** Explain and update a simple obsolete rule directly when the improvement and authority are clear; do not force a rollback to satisfy a metric.

**Assumptions, conflicts and failure:** Calling everything “evolution” can excuse erosion; calling everything “violation” can block a better architecture.

**Retirement/reopening:** Reopen when new evidence changes whether the deviation harms a still-valid obligation.

**Abstraction:** Deviations between intended, documented and realised architectures over time. **Evidence boundary:** Test the affected invariant, quality or change burden and verify the adjudicated revision. Calling everything “evolution” can excuse erosion; calling everything “violation” can block a better architecture.

**Relations:** ESA-REL032, ESA-REL033, ESA-REL037, ESA-REL059. **Tensions:** ESA-T005. **Source IDs:** ESA-S002, ESA-S020, ESA-S045, ESA-S041, ESA-S048, ESA-S046.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-040` — Architectural smells as defeasible risk indicators

Status: `USEFUL_BUT_EASILY_GAMED`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Use a smell or detector output to prioritise investigation, then connect it to actual quality, invariant or change burden before prescribing repair.

**Trigger and required inputs:** There are enough suspected structural problems that triage may save investigation effort. Defined detector semantics, calibration/known errors and a link between the indicator and the concern of interest.

**Produced constraint/evidence:** An acted-upon smell has supporting evidence of a relevant consequence, or is dismissed/held uncertain with reasons. Its consumer is: Maintainers and reviewers selecting what to investigate or repair.

**Costs, substitution and omission:** Investigate a concrete recurring failure directly; skip a detector when its noise costs more than manual diagnosis.

**Assumptions, conflicts and failure:** Optimising the score can move complexity elsewhere; balanced classifier datasets distort operational precision and performance effects are heterogeneous.

**Retirement/reopening:** Reopen on detector/version/domain changes or evidence that its flagged patterns are benign or missed harms dominate.

**Abstraction:** Potential architectural risk indicators extracted from code, graphs or review text. **Evidence boundary:** Use target-specific precision/recall and measured consequences where feasible; score reduction alone is not remediation value. Optimising the score can move complexity elsewhere; balanced classifier datasets distort operational precision and performance effects are heterogeneous.

**Relations:** ESA-REL034. **Tensions:** ESA-T007. **Source IDs:** ESA-S046, ESA-S047, ESA-S048.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-041` — Recovered structure as a substitute for intended rationale

Status: `REJECTED_OR_DISFAVOURED`. Kind: `REJECTED_UNIVERSAL_OR_CEREMONIAL_CLAIM`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. Recovered structure cannot by itself establish the stakeholders, alternatives or rationale behind it; inferred intent must be labelled and corroborated. Disposition: REJECTED_OR_DISFAVOURED.

**Trigger and required inputs:** A recovered graph or generated description is treated as a replacement for absent decision history. Historical records or corroborating testimony are needed for a historical-rationale claim.

**Produced constraint/evidence:** No historical-intent postcondition follows from structure alone. Its consumer is: Maintainers and researchers reconstructing why decisions were made.

**Costs, substitution and omission:** Retain observed facts, ask a knowledgeable participant or state the intent as unresolved rather than manufacture it.

**Assumptions, conflicts and failure:** The same structure can result from deliberate trade-off, accident, obsolete conditions or constraints invisible in code.

**Retirement/reopening:** Reconsider an inferred rationale when contemporary records or participants provide evidence.

**Abstraction:** Distinction between recovered architecture and missing design rationale. **Evidence boundary:** Not applicable as direct intent measurement; triangulate independent historical evidence where it exists. The same structure can result from deliberate trade-off, accident, obsolete conditions or constraints invisible in code.

**Relations:** ESA-REL058. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S045, ESA-S026, ESA-S027.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-042` — Zero deviations from a historical architecture

Status: `REJECTED_OR_DISFAVOURED`. Kind: `REJECTED_UNIVERSAL_OR_CEREMONIAL_CLAIM`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. Zero departures from any historical model is not admitted as a general quality requirement. Disposition: REJECTED_OR_DISFAVOURED.

**Trigger and required inputs:** A historical rule is enforced despite changed requirements or evidence that its violation is an improvement. A continuing external or design obligation must justify each enforced baseline; age alone is not authority.

**Produced constraint/evidence:** No guarantee of current quality follows from perfect agreement with an obsolete model. Its consumer is: Reviewers and maintainers choosing whether the implementation or baseline should change.

**Costs, substitution and omission:** Adjudicate the rule and change through ESA-038/039, preserving the current protected obligation.

**Assumptions, conflicts and failure:** The rule can entrench harmful structure and turn conformance metrics into theatre.

**Retirement/reopening:** Retire or revise the obsolete rule once its relevant obligation has changed or disappeared.

**Abstraction:** Historical model compliance as an unconditional architectural objective. **Evidence boundary:** Not a zero-count objective; measure the current protected quality and correctness of adjudicated changes. The rule can entrench harmful structure and turn conformance metrics into theatre.

**Relations:** ESA-REL059. **Tensions:** ESA-T005. **Source IDs:** ESA-S002, ESA-S045, ESA-S041, ESA-S048, ESA-S046.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-043` — Architecture debt distinguished from mere imperfection

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Identify the specific structural compromise, its current benefit, the future work or recurring penalty it may cause and the plausible cost of remedy; distinguish observed interest from a prediction.

**Trigger and required inputs:** A known architectural choice is causing or credibly expected to cause recurring change/operation burden. A causal account linking the structure to burden, a time horizon and feasible remediation alternatives.

**Produced constraint/evidence:** The decision to retain, repay or monitor the compromise has evidence and a stated revision condition. Its consumer is: Maintainers and resource decision makers comparing remediation with other investments.

**Costs, substitution and omission:** Leave a harmless imperfection alone; use an ordinary defect or planned enhancement description when debt adds no explanatory value.

**Assumptions, conflicts and failure:** Calling all disliked design debt inflates obligations; qualitative accounts do not justify fabricated monetary principal or interest rates.

**Retirement/reopening:** Reopen when interest materialises, the affected feature retires or repair becomes cheaper/more costly.

**Abstraction:** Architecture-level compromises and their temporal costs. **Evidence boundary:** Observe extra work or recurring constraints and estimate remedy cost with uncertainty; do not infer interest from a smell score. Calling all disliked design debt inflates obligations; qualitative accounts do not justify fabricated monetary principal or interest rates.

**Relations:** ESA-REL034, ESA-REL035. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S049, ESA-S050, ESA-S056.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-044` — Incremental migration with coexistence and compatibility

Status: `CONTEXT_DEPENDENT`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Plan migration steps that preserve required behaviour and compatibility while old and new structures coexist; include routing/data transitions and an explicit end to temporary arrangements.

**Trigger and required inputs:** A consequential replacement must proceed while service or development continues. Known compatibility obligations, feasible transition states and a way to evaluate each step and handle failure.

**Produced constraint/evidence:** Each actual transition preserves the required commitments and obsolete compatibility machinery is retired when its consumer disappears. Its consumer is: Migration engineers, operators and stakeholders accepting continuity or interruption costs.

**Costs, substitution and omission:** A direct replacement or brief planned outage may be safer and cheaper for a small, low-exposure system.

**Assumptions, conflicts and failure:** Temporary bridges become permanent, dual writes diverge and rollback may be impossible after irreversible data changes.

**Retirement/reopening:** Reopen when transition risk, compatibility needs or the feasibility of safe reversal changes.

**Abstraction:** Sequences and coexistence states between architectural configurations. **Evidence boundary:** Exercise transition-state contracts and observe real migration outcomes; a final-state diagram is insufficient. Temporary bridges become permanent, dual writes diverge and rollback may be impossible after irreversible data changes.

**Relations:** ESA-REL004, ESA-REL020, ESA-REL028, ESA-REL033, ESA-REL035, ESA-REL036. **Tensions:** ESA-T003. **Source IDs:** ESA-S040, ESA-S051, ESA-S026, ESA-S050, ESA-S060.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-045` — Revisable fitness functions and continuous evaluation

Status: `USEFUL_BUT_EASILY_GAMED`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Use maintained checks to detect changes in selected architectural characteristics, and periodically challenge whether the checks still measure the concern and preserve competing constraints.

**Trigger and required inputs:** Repeated changes threaten a sufficiently observable characteristic and feedback can influence decisions. Valid measures, traceable concern/constraint, a real consumer and an explicit path for justified exceptions or revision.

**Produced constraint/evidence:** A relevant deterioration reaches an authorised decision process; a green score is not represented as whole-system health. Its consumer is: Developers, operators and reviewers who can respond to findings; a check does not acquire independent authority.

**Costs, substitution and omission:** A manual review or occasional targeted test is adequate when changes are infrequent or the property is poorly automatable.

**Assumptions, conflicts and failure:** Proxies can be gamed, frozen goals block improvement and monitoring can silently fail; automation does not fix the oracle problem.

**Retirement/reopening:** Reopen or retire the check when the concern, valid baseline, measurement or consumer changes.

**Abstraction:** Continuous or periodic checks on selected architectural properties. **Evidence boundary:** Validate the check against known positive/negative cases and actual outcomes, including false reassurance and maintenance cost. Proxies can be gamed, frozen goals block improvement and monitoring can silently fail; automation does not fix the oracle problem.

**Relations:** ESA-REL015, ESA-REL029, ESA-REL033, ESA-REL037, ESA-REL047. **Tensions:** ESA-T005, ESA-T007. **Source IDs:** ESA-S043, ESA-S044, ESA-S020, ESA-S054, ESA-S062.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-046` — Architecture-based observation and runtime adaptation

Status: `DOMAIN_SPECIFIC`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Observe the running system, interpret observations in an architecture model, choose among allowed changes and execute them through available effectors; keep system-specific translation explicit.

**Trigger and required inputs:** Operating variation warrants runtime reconfiguration and appropriate actions are available. Observable state, timely valid sensors/model, specified strategies and effectors capable of making the intended changes.

**Produced constraint/evidence:** The requested adaptation is actually enacted and subsequent observations show its bounded consequence. Its consumer is: Runtime controllers within delegated limits, with engineers/operators responsible for those limits and failures.

**Costs, substitution and omission:** Use a stable configuration, an operator procedure or a simple established controller when architecture-level adaptation adds no value.

**Assumptions, conflicts and failure:** An outdated model, invalid probe or ineffective action can break the loop; reusable infrastructure still needs expensive system-specific engineering.

**Retirement/reopening:** Reopen when sensors, strategy, model mapping or available actions change or become invalid.

**Abstraction:** Runtime architectural configurations, monitors, model and control actions. **Evidence boundary:** Observe model freshness, action completion and post-change qualities under the stated operating envelope. An outdated model, invalid probe or ineffective action can break the loop; reusable infrastructure still needs expensive system-specific engineering.

**Relations:** ESA-REL004, ESA-REL005, ESA-REL017, ESA-REL038, ESA-REL039, ESA-REL047, ESA-REL064. **Tensions:** ESA-T008. **Source IDs:** ESA-S051, ESA-S052, ESA-S053, ESA-S054, ESA-S055.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-047` — Constrained adaptation and post-change assurance

Status: `ASSUMPTION_SENSITIVE`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Constrain allowed changes by the relevant system and external obligations, then assess the actual post-change state; local metric improvement is evidence for only that metric.

**Trigger and required inputs:** Runtime or automated changes can violate an invariant, external commitment or competing quality. Explicit constraints, a valid model/observation basis, executable bounded actions and a defined response when assurance fails.

**Produced constraint/evidence:** The executed change satisfies the examined constraints, or the uncertainty/failure prevents an unjustified success claim. Its consumer is: Delegating engineers/owners and bounded controllers/operators; a optimiser cannot grant itself new commitments.

**Costs, substitution and omission:** Keep a known-safe static choice or require operator judgement when the admissible change envelope cannot be adequately established.

**Assumptions, conflicts and failure:** Incomplete constraints, delayed measurements, interacting controllers and irreversible actions can invalidate local assurance.

**Retirement/reopening:** Reopen or stop using the policy when assumptions, observations or external constraints no longer support it.

**Abstraction:** Admissible architectural transition set and post-change system state. **Evidence boundary:** Check end-to-end and external responses after change, not only the controller’s objective or planned state. Incomplete constraints, delayed measurements, interacting controllers and irreversible actions can invalidate local assurance.

**Relations:** ESA-REL014, ESA-REL015, ESA-REL038, ESA-REL039, ESA-REL040, ESA-REL060. **Tensions:** ESA-T008. **Source IDs:** ESA-S015, ESA-S052, ESA-S053, ESA-S054, ESA-S055, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-048` — Self-authorisation through local metric improvement

Status: `REJECTED_OR_DISFAVOURED`. Kind: `REJECTED_UNIVERSAL_OR_CEREMONIAL_CLAIM`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. An improved local objective neither authorises an architectural change nor establishes its external consequences. Disposition: REJECTED_OR_DISFAVOURED.

**Trigger and required inputs:** A controller or decision-support tool treats its own score as sufficient permission and proof of success. Any delegated authority and acceptable change envelope must come from outside the score being optimised.

**Produced constraint/evidence:** No legitimate global success postcondition follows from a local score increase. Its consumer is: Engineers and operators interpreting automated recommendations or actions.

**Costs, substitution and omission:** Apply independently established constraints and observe the actual consequences through ESA-047.

**Assumptions, conflicts and failure:** The change may break another quality, violate an external commitment, exploit a proxy or corrupt its own observation basis.

**Retirement/reopening:** Reconsider only a bounded delegation with independently justified constraints; the objective cannot justify its own expansion.

**Abstraction:** Self-authorisation claim for metric-driven architectural change. **Evidence boundary:** Not applicable as a universal acceptance measure; use separate authority, constraint and outcome checks. The change may break another quality, violate an external commitment, exploit a proxy or corrupt its own observation basis.

**Relations:** ESA-REL060. **Tensions:** ESA-T008. **Source IDs:** ESA-S052, ESA-S053, ESA-S054, ESA-S056, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-049` — Investment in future flexibility proportionate to change hypotheses

Status: `ASSUMPTION_SENSITIVE`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Invest in flexibility when a credible change family and its expected cost justify the present complexity; preserve simpler reversible choices where evidence is weak.

**Trigger and required inputs:** A proposed abstraction, extension point or distributed boundary is justified primarily by future changes. A plausible change hypothesis, comparative implementation/change costs and understanding of reversibility.

**Produced constraint/evidence:** The flexibility has an identified consumer or learning value, and its ongoing cost remains visible. Its consumer is: Designers and investment decision makers accepting current complexity for future capability.

**Costs, substitution and omission:** Defer the extension or implement the currently needed case directly when later change is tolerable.

**Assumptions, conflicts and failure:** Forecasts can be wrong in either direction; overgeneralisation imposes present costs while underinvestment can make later migration prohibitive.

**Retirement/reopening:** Reopen when predicted changes fail to occur, new changes emerge or the flexibility premium becomes disproportionate.

**Abstraction:** Architectural options, abstraction/variation points and temporal cost of change. **Evidence boundary:** Compare actual change experience with the hypothesis and estimate the premium paid for unused options. Forecasts can be wrong in either direction; overgeneralisation imposes present costs while underinvestment can make later migration prohibitive.

**Relations:** ESA-REL012, ESA-REL029, ESA-REL035, ESA-REL041. **Tensions:** ESA-T002, ESA-T003. **Source IDs:** ESA-S001, ESA-S006, ESA-S008, ESA-S010, ESA-S037, ESA-S041, ESA-S039.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-050` — Microservices conditional on deployment and operating needs

Status: `CONTEXT_DEPENDENT`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Select independent deployments where workload, release, failure or ownership needs warrant their distributed-system and operational costs; validate data and interaction independence.

**Trigger and required inputs:** Different parts genuinely need separate release/scaling or bounded operational control and teams can support it. Mature enough delivery/operations, explicit inter-service contracts and a plan for shared data, partial failure and end-to-end observation.

**Produced constraint/evidence:** The intended independence is exercised without unacceptable inconsistency, coordination or operation overhead. Its consumer is: Service teams and end-to-end operators/stakeholders accepting the distribution trade-off.

**Costs, substitution and omission:** Use a modular monolith or shared deployment when releases, scaling, permissions and operations largely move together.

**Assumptions, conflicts and failure:** Small services can be a distributed monolith; more teams or endpoints do not prove independence or business benefit.

**Retirement/reopening:** Reopen when independence is not used, coupling dominates or operating capability no longer supports the architecture.

**Abstraction:** Service decomposition and deployment topology, distinct from source-code modularity. **Evidence boundary:** Observe independent changes/deployments, end-to-end latency/failure and coordination effort under representative demand. Small services can be a distributed monolith; more teams or endpoints do not prove independence or business benefit.

**Relations:** ESA-REL007, ESA-REL009, ESA-REL041, ESA-REL042. **Tensions:** ESA-T006, ESA-T010. **Source IDs:** ESA-S036, ESA-S001, ESA-S026, ESA-S037, ESA-S039, ESA-S060.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-051` — Modular monoliths and justified consolidation

Status: `CONTEXT_DEPENDENT`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Preserve useful logical boundaries inside a shared deployment, or consolidate services whose separation adds costs without a needed independent capability.

**Trigger and required inputs:** Shared release, scale, trust or operations make independent deployment unnecessary or harmful. Knowledge of necessary logical invariants and the consequences of consolidating failure/resource/release domains.

**Produced constraint/evidence:** The system retains required modular reasoning while removing unneeded distributed coordination. Its consumer is: Application teams and operators accountable for shared deployment consequences.

**Costs, substitution and omission:** A simple unlayered local application may suffice when even internal abstraction has no change or comprehension consumer.

**Assumptions, conflicts and failure:** A shared deployment can still create release and failure contention; consolidation is not proof that every boundary should disappear.

**Retirement/reopening:** Reopen when parts acquire genuinely different scaling, release, fault or authority needs.

**Abstraction:** Logical modules within a deployment and transitions from distributed to consolidated structure. **Evidence boundary:** Compare operational overhead, release coupling and change impact with the previous or proposed alternative. A shared deployment can still create release and failure contention; consolidation is not proof that every boundary should disappear.

**Relations:** ESA-REL009, ESA-REL041, ESA-REL042. **Tensions:** ESA-T003, ESA-T010. **Source IDs:** ESA-S001, ESA-S037, ESA-S038, ESA-S039, ESA-S036.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-052` — Serverless architecture with provider and workload boundaries

Status: `DOMAIN_SPECIFIC`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Model provider-managed execution and service dependencies, including data locality, lifecycle, communication, resource and failure assumptions relevant to the workload.

**Trigger and required inputs:** A design delegates execution/resource management to a serverless platform. Version-specific platform contracts, workload characteristics and evidence about dependencies outside application code.

**Produced constraint/evidence:** The architecture meets its selected response and cost boundaries on the actual chosen platform, with provider assumptions explicit. Its consumer is: Application teams and provider-facing operators; provider controls constrain what the application can observe or change.

**Costs, substitution and omission:** Use a simpler long-running process or managed service when latency, state or steady demand makes function decomposition costly.

**Assumptions, conflicts and failure:** Historical provider limits cannot be carried forward as current facts; cost/energy may merely move outside the measured boundary.

**Retirement/reopening:** Reopen when provider semantics, workload shape, data movement or pricing/contract assumptions change.

**Abstraction:** Function, platform and external-service composition in a serverless deployment. **Evidence boundary:** Observe relevant latency distribution, workload cost and failure behaviour; evaluate energy only within a declared measurement boundary. Historical provider limits cannot be carried forward as current facts; cost/energy may merely move outside the measured boundary.

**Relations:** ESA-REL043. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S057, ESA-S035, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-053` — Architecture for learned components and data dependencies

Status: `DOMAIN_SPECIFIC`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Include training/serving data, model behaviour, undeclared consumers and feedback paths in architectural reasoning; treat distribution and model changes as potential contract changes.

**Trigger and required inputs:** Learned components influence consequential system outputs or are reused by downstream consumers. Known data/model provenance, population assumptions, consumer contracts and observations of relevant system-level effects.

**Produced constraint/evidence:** A change in model or data is assessed for affected consumers and feedback, not judged only by an isolated model score. Its consumer is: Model, data, application and operations participants responsible for affected system consequences.

**Costs, substitution and omission:** A deterministic rule or isolated advisory component may be simpler when learning adds no justified capability.

**Assumptions, conflicts and failure:** Code-level modularity does not contain learned entanglement; hidden feedback and changing populations can invalidate previous behaviour.

**Retirement/reopening:** Reopen after data-distribution, model, consumer or feedback changes, even when ordinary interfaces are unchanged.

**Abstraction:** Learned components embedded in data, software and organisational processes. **Evidence boundary:** Use system-level quality scenarios under relevant populations and feedback conditions; an offline accuracy score is insufficient. Code-level modularity does not contain learned entanglement; hidden feedback and changing populations can invalidate previous behaviour.

**Relations:** ESA-REL044. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S056, ESA-S008.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-054` — Evidence-checked AI assistance for architectural work

Status: `ASSUMPTION_SENSITIVE`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Use generated alternatives, descriptions or risk suggestions as candidates; independently check their evidence, semantics, metrics and fit to the actual system before relying on them.

**Trigger and required inputs:** AI assistance could reduce search/drafting effort and adequate validation is available. Accessible underlying evidence, explicit task scope, recorded model/prompt context and an evaluator not simply reusing the generated claim as its oracle.

**Produced constraint/evidence:** Accepted AI-assisted claims have an independent basis and unsupported material remains labelled or rejected. Its consumer is: Human or otherwise authorised reviewers who retain decision responsibility; generated text has no operative mandate.

**Costs, substitution and omission:** Use direct human analysis, deterministic extraction or established checks when verification costs exceed the assistance benefit.

**Assumptions, conflicts and failure:** Fluent diagrams, hallucinated metrics, selected educational tasks and single-run benchmarks do not demonstrate reliable deployment decisions.

**Retirement/reopening:** Reopen when model, retrieval corpus, prompt, requirement scope or validation evidence changes.

**Abstraction:** AI-produced architectural representations, options, risk analyses and boundary proposals. **Evidence boundary:** Compare externally checked correctness and total effort including verification, not model confidence or self-reported quality. Fluent diagrams, hallucinated metrics, selected educational tasks and single-run benchmarks do not demonstrate reliable deployment decisions.

**Relations:** ESA-REL045, ESA-REL064. **Tensions:** ESA-T007. **Source IDs:** ESA-S059, ESA-S062, ESA-S063.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-055` — Sustainability as an explicitly bounded architectural concern

Status: `CONTEXT_DEPENDENT`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Declare the sustainability concern and system/lifecycle boundary, then evaluate architectural alternatives against measurable impacts and competing constraints rather than assuming a fashionable deployment is greener.

**Trigger and required inputs:** Energy, emissions, resource use or longer-term maintainability are material stakeholder concerns. An appropriate measurement/accounting boundary, relevant workload and explicit treatment of externalised impacts.

**Produced constraint/evidence:** A claimed improvement is tied to the measured concern and boundary, with omitted lifecycle or social effects stated. Its consumer is: Stakeholders setting impact priorities and engineers able to measure and alter relevant mechanisms.

**Costs, substitution and omission:** Use a targeted operational measurement or omit a specialised control when its impact is negligible and its own cost dominates.

**Assumptions, conflicts and failure:** Energy is not carbon, package energy is not facility/lifecycle impact and efficiency can induce greater use; the latter is an analytical transfer concern here.

**Retirement/reopening:** Reopen when workload, energy supply, lifecycle scope or external costs change the impact comparison.

**Abstraction:** Architectural choices affecting operational and lifecycle resource consequences. **Evidence boundary:** Use the actual chosen impact measure plus performance/availability constraints; do not extrapolate a benchmark saving to whole-system sustainability. Energy is not carbon, package energy is not facility/lifecycle impact and efficiency can induce greater use; the latter is an analytical transfer concern here.

**Relations:** ESA-REL014, ESA-REL046. **Tensions:** ESA-T008. **Source IDs:** ESA-S058, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-056` — Proportional governance and retirement of controls

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Keep only the architectural control, artefact or coordination mechanism whose consumer and avoided risk justify its cost; choose the smallest coherent arrangement and retire obsolete controls.

**Trigger and required inputs:** Architecture work imposes review, documentation, modelling or coordination cost. A named protected concern, real consumer and visibility of control cost and failure consequences.

**Produced constraint/evidence:** The retained machinery supports a decision or protects an obligation, and unnecessary machinery can be removed without losing that function. Its consumer is: Those using and funding architectural work, with affected stakeholders participating in trade-offs.

**Costs, substitution and omission:** No extra intervention is appropriate when existing shared understanding and ordinary engineering already address the concern adequately.

**Assumptions, conflicts and failure:** “Lightweight” can hide omitted obligations; “rigorous” can hide waste. No universal document count, team size or review cadence determines adequacy.

**Retirement/reopening:** Retire when the risk, consumer or dependency disappears; strengthen when credible harm exceeds the cheap path’s capability.

**Abstraction:** Architecture methods and governance arrangements applied to a particular system. **Evidence boundary:** Compare actual decision/risk coverage and control burden with a cheaper alternative or no added control. “Lightweight” can hide omitted obligations; “rigorous” can hide waste. No universal document count, team size or review cadence determines adequacy.

**Relations:** ESA-REL047, ESA-REL057, ESA-REL061. **Tensions:** ESA-T004, ESA-T009. **Source IDs:** ESA-S003, ESA-S009, ESA-S010, ESA-S017, ESA-S037, ESA-S041, ESA-S042, ESA-S039.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-057` — Service and REST constraints distinguished from labels

Status: `SUPERSEDED_BY_STRONGER_FORM`. Kind: `SUPERSEDED_MIXED_CANDIDATE`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. The useful warning is retained through separate REST constraints (ESA-065) and service interaction/effect contracts (ESA-066), whose assumptions and consumers differ. Disposition: SUPERSEDED_BY_STRONGER_FORM.

**Trigger and required inputs:** A design relies on “service-oriented” or “RESTful” as if the word alone establishes interoperability or quality. Select the specific subject and obligations instead of treating REST and SOA as synonyms.

**Produced constraint/evidence:** The successor mechanism makes the relevant contract or constraint explicit; this umbrella is not an extra independent obligation. Its consumer is: Interface and architecture designers distinguishing their selected mechanisms.

**Costs, substitution and omission:** Name and check the actual required interaction property without imposing either complete style.

**Assumptions, conflicts and failure:** A single broad label obscures different abstraction levels and applicability conditions.

**Retirement/reopening:** Use the successor records when the design or terminology changes; do not count this row as an additional retained mechanism.

**Abstraction:** Superseded umbrella over architectural styles and reference-model concepts. **Evidence boundary:** No separate response measure; use the selected successor’s concern-specific measure. A single broad label obscures different abstraction levels and applicability conditions.

**Relations:** ESA-REL063. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S034, ESA-S035, ESA-S026.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-058` — Emergence as a reason to omit architectural reasoning

Status: `REJECTED_OR_DISFAVOURED`. Kind: `REJECTED_UNIVERSAL_OR_CEREMONIAL_CLAIM`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. Emergence is not a general exemption from examining architecture-relevant consequences; reason just enough, and revise as the system and knowledge change. Disposition: REJECTED_OR_DISFAVOURED.

**Trigger and required inputs:** An evolutionary or agile label is used to avoid considering a consequential interface, quality or migration decision. A locally evolving design still needs access to affected consequences and a way to detect failures.

**Produced constraint/evidence:** No general quality postcondition follows from omitting architectural reasoning. Its consumer is: Development teams and stakeholders exposed to evolving structural choices.

**Costs, substitution and omission:** Use timely local reasoning, concrete experiments and brief rationale rather than a speculative full upfront design.

**Assumptions, conflicts and failure:** Accidental dependencies and irreversible choices arise without explicit plans; conversely excessive anticipation can obstruct learning.

**Retirement/reopening:** Reopen reasoning whenever a local choice becomes consequential; do not schedule all architecture only at project start.

**Abstraction:** Architectural reasoning across time, distinct from a mandatory upfront document phase. **Evidence boundary:** Assess actual decisions and consequences rather than whether the process is labelled emergent or planned. Accidental dependencies and irreversible choices arise without explicit plans; conversely excessive anticipation can obstruct learning.

**Relations:** ESA-REL061. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S008, ESA-S010, ESA-S041, ESA-S026, ESA-S056.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-059` — Description-standard conformance as quality certification

Status: `REJECTED_OR_DISFAVOURED`. Kind: `REJECTED_UNIVERSAL_OR_CEREMONIAL_CLAIM`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. Conformance of an architecture description is not admitted as a certificate that the actual architecture satisfies stakeholder concerns. Disposition: REJECTED_OR_DISFAVOURED.

**Trigger and required inputs:** A standards claim about documentation is offered as proof of performance, security, maintainability or other operating quality. Any conformance claim requires the applicable edition and actual inspected normative obligations; this packet does not perform such a compliance audit.

**Produced constraint/evidence:** No realised-quality guarantee follows solely from descriptive conformance. Its consumer is: Standards users, reviewers and recipients of assurance claims.

**Costs, substitution and omission:** Use the standard for the description purpose and separately establish the selected system-quality claim.

**Assumptions, conflicts and failure:** A fully compliant description could faithfully describe a poor architecture, or be disconnected from implementation.

**Retirement/reopening:** Reassess separately when the description edition or the implemented architecture changes.

**Abstraction:** Boundary between architecture-description requirements and realised architecture quality. **Evidence boundary:** Description conformance and observed quality are separate measures with separate evidence. A fully compliant description could faithfully describe a poor architecture, or be disconnected from implementation.

**Relations:** ESA-REL062. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S011, ESA-S012, ESA-S065, ESA-S020, ESA-S054.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-060` — Autonomous architecting under open-ended requirements

Status: `UNRESOLVED`. Kind: `UNRESOLVED_CAPABILITY_CLAIM`. Crosswalk-worthy: NO unconditional obligation.

**Mechanism/criterion:** Not an unconditional obligation. No general method for reliable autonomous architecting under evolving open-ended requirements is established by the examined evidence; preserve it as a research question rather than a prohibition or accepted capability. Disposition: UNRESOLVED.

**Trigger and required inputs:** A proposed system is expected to choose, authorise, implement and validate consequential architecture with little or no external judgement. A broader claim would require a valid objective/constraint process, sustained implementation correspondence and representative evidence of outcomes and revision handling.

**Produced constraint/evidence:** No demonstrated general postcondition in this corpus; bounded task success remains admissible evidence for its own scope. Its consumer is: Researchers and anyone proposing delegated architectural authority; the evidence does not supply that delegation.

**Costs, substitution and omission:** Use bounded assistance or a constrained controller with explicit admissible actions and independent evaluation.

**Assumptions, conflicts and failure:** Diagram quality, student risk lists and structural clustering do not cover authority, live operation, changing stakeholders or external consequences.

**Retirement/reopening:** Reopen when representative end-to-end evidence or a rigorously bounded new capability materially changes the claim.

**Abstraction:** Autonomous architecture decision and change process under open-ended requirements. **Evidence boundary:** Future tests should assess end-to-end correctness, consequences, recovery and total cost under changing requirements, not just generated artefact ratings. Diagram quality, student risk lists and structural clustering do not cover authority, live operation, changing stakeholders or external consequences.

**Relations:** ESA-REL064. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S059, ESA-S062, ESA-S063.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-061` — Bounded semantic models and explicit translation

Status: `CONTEXT_DEPENDENT`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** State where a model’s terms and rules are valid, map actual relations to other models, and make required translation or shared meaning explicit.

**Trigger and required inputs:** Different domains or teams use similar terms with incompatible meanings or need different model evolution. Concrete domain usage, known consumers and clarity about which relationships share or translate semantics.

**Produced constraint/evidence:** Cross-context exchanges preserve the intended meaning or expose a deliberate limitation, rather than silently conflating models. Its consumer is: Domain experts and software teams on both sides of the boundary.

**Costs, substitution and omission:** A single shared model and conversation can suffice where meanings genuinely coincide; do not invent contexts solely to match teams.

**Assumptions, conflicts and failure:** Translation adds cost, a shared kernel adds coordination and a bounded context is not automatically a network or deployment boundary.

**Retirement/reopening:** Reopen when domain meaning, upstream/downstream obligations or the cost of translation changes.

**Abstraction:** Domain model validity and semantic relationships, distinct from physical topology. **Evidence boundary:** Test representative cross-context examples and changes for semantic compatibility, not context count. Translation adds cost, a shared kernel adds coordination and a bounded context is not automatically a network or deployment boundary.

**Relations:** ESA-REL010, ESA-REL011, ESA-REL065. **Tensions:** ESA-T001, ESA-T006, ESA-T010. **Source IDs:** ESA-S033, ESA-S035, ESA-S026, ESA-S060.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-062` — Usability concerns allowed to reshape architecture

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Allow a concrete user-interaction concern to change architecture when satisfying it requires system state, control, responsiveness or recoverability beyond visual layout.

**Trigger and required inputs:** A user scenario cannot be met by presentation changes alone. Understanding of the user task, relevant response and which backend or interaction mechanism constrains it.

**Produced constraint/evidence:** The architectural intervention enables the specified user response in the real task, not merely a new UI affordance. Its consumer is: Users or their representatives, interaction designers and system engineers.

**Costs, substitution and omission:** Keep the change in local interface design when it has no substantive architectural implication; the source method itself discards such scenarios.

**Assumptions, conflicts and failure:** Scenario catalogues are not universal requirements and architectural support alone does not establish usability for the intended users.

**Retirement/reopening:** Reopen when tasks, user populations or implementation constraints change the relevant scenario.

**Abstraction:** Coupling between user interaction and architectural state/control mechanisms. **Evidence boundary:** Evaluate the concrete interaction and response with appropriate user/task evidence; architecture-pattern presence is insufficient. Scenario catalogues are not universal requirements and architectural support alone does not establish usability for the intended users.

**Relations:** ESA-REL048. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S018, ESA-S017.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-063` — Safe change of adaptation policies and assurance assumptions

Status: `ASSUMPTION_SENSITIVE`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Treat changes to sensors, architectural models, adaptation policies and assurance assumptions as consequential changes requiring bounded validation and continuity checks, not as automatically safe self-repair.

**Trigger and required inputs:** A running adaptation mechanism or its evidence/decision rules are being revised. A known prior basis for acceptance, controlled change boundary, checks of observation/action continuity and an authorised response to loss of assurance.

**Produced constraint/evidence:** The revised mechanism remains connected to trustworthy observations and permitted actions, or its use is withheld with the gap explicit. Its consumer is: Engineers/operators authorised to revise control rules; self-revision is only within an independently justified delegation.

**Costs, substitution and omission:** Use a reviewed offline policy change or retain the existing validated configuration where live self-revision adds avoidable risk.

**Assumptions, conflicts and failure:** A controller may invalidate its own evidence, silently accept bad data or expand its objective; the inspected literature does not establish unrestricted recursive self-authorisation.

**Retirement/reopening:** Reopen or stop relying on the revised mechanism when continuity or its assumptions cannot be established.

**Abstraction:** Adaptation controller, monitoring model, policy and their revision boundaries. **Evidence boundary:** Test sensor/model validity, policy constraints and actual transition consequences across the update. A controller may invalidate its own evidence, silently accept bad data or expand its objective; the inspected literature does not establish unrestricted recursive self-authorisation.

**Relations:** ESA-REL004, ESA-REL039, ESA-REL040, ESA-REL060. **Tensions:** ESA-T008. **Source IDs:** ESA-S052, ESA-S053, ESA-S054, ESA-S055, ESA-S061.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-064` — Rationalised design explanation distinguished from actual history

Status: `RETAINED_IN_EVOLVED_FORM`. Kind: `CRITERION_COUPLED_TO_ESTABLISHING_METHOD`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Provide a coherent explanation of why the current design is defensible while separately labelling historical records and reconstructed reasoning; do not make a tidy story into fabricated provenance.

**Trigger and required inputs:** A later consumer needs an understandable design account and the original process was incomplete, iterative or poorly recorded. Access to the current design and supporting reasons; historical claims require contemporaneous evidence or qualified testimony.

**Produced constraint/evidence:** The reader can distinguish present justification, documented history and inferred history. Its consumer is: Documentation authors, maintainers and researchers relying on provenance.

**Costs, substitution and omission:** A concise explanation marked as reconstructed is better than reconstructing a fictitious complete decision chronology.

**Assumptions, conflicts and failure:** Reconstruction can rationalise accidents or erase rejected options; the rational account still needs adversarial checking.

**Retirement/reopening:** Reopen when evidence contradicts the rationale or reveals that the historical account was inferred.

**Abstraction:** Design rationale and its historical/propositional status. **Evidence boundary:** Test explanatory adequacy against the current design; test historical accuracy against independent records, not narrative coherence. Reconstruction can rationalise accidents or erase rejected options; the rational account still needs adversarial checking.

**Relations:** ESA-REL049, ESA-REL058. **Tensions:** ESA-T009. **Source IDs:** ESA-S009, ESA-S027, ESA-S029.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-065` — REST interaction constraints

Status: `DOMAIN_SPECIFIC`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Where its context fits, apply REST’s client/server, stateless interaction, cache, uniform-interface and layered constraints together, with optional code-on-demand and their associated trade-offs.

**Trigger and required inputs:** An Internet-scale distributed-hypermedia interaction problem benefits from visibility, intermediaries and independent evolution. Actual resource/representation and interaction semantics, cache validity and adherence to the selected style’s constraints.

**Produced constraint/evidence:** The real interactions exhibit the claimed REST constraints and the selected consequences are evaluated. Its consumer is: Client/server and intermediary designers and their independent consumers.

**Costs, substitution and omission:** Use a simpler local interface or another protocol/style where its constraints impose costs without those benefits; do not call every HTTP API REST.

**Assumptions, conflicts and failure:** Stateless interaction does not mean no persistent data; generic interfaces can cost efficiency and cache assumptions can fail.

**Retirement/reopening:** Reopen when application semantics or efficiency needs no longer justify the style’s constraints.

**Abstraction:** Network interaction style at distributed-hypermedia scope. **Evidence boundary:** Check protocol semantics and quality responses in the declared workload; transport choice or naming is not conformance. Stateless interaction does not mean no persistent data; generic interfaces can cost efficiency and cache assumptions can fail.

**Relations:** ESA-REL050, ESA-REL063. **Tensions:** ESA-T010. **Source IDs:** ESA-S034, ESA-S026.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-066` — Service visibility, interaction and real-world-effect contracts

Status: `DOMAIN_SPECIFIC`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** For a service relationship, distinguish awareness/reachability/willingness, the exchanged information/actions and the consequence that the consumer seeks, including policy or contract conditions.

**Trigger and required inputs:** A consumer relies on another participant’s capability across a service boundary. Mutually understood action/information semantics, actual access and applicable conditions; a discoverable endpoint does not establish permission or success.

**Produced constraint/evidence:** The consumer can determine whether the intended interaction is possible, allowed and actually produced the relevant effect. Its consumer is: Providers and consumers within their real policies/contracts; each retains its actual authority boundary.

**Costs, substitution and omission:** A direct internal function contract may suffice when there is no separate service/participant relation to manage.

**Assumptions, conflicts and failure:** Message exchange can succeed without the desired state change; declared willingness does not commit a provider to every requested operation.

**Retirement/reopening:** Reopen when capability, access conditions, semantics or the promised effect changes.

**Abstraction:** Service relationship and externally meaningful effects, not merely interface syntax. **Evidence boundary:** Check both interaction completion and the promised state/information consequence under the specified conditions. Message exchange can succeed without the desired state change; declared willingness does not commit a provider to every requested operation.

**Relations:** ESA-REL007, ESA-REL051, ESA-REL063. **Tensions:** ESA-T010. **Source IDs:** ESA-S035, ESA-S026.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-067` — Driver-based recursive architectural design

Status: `CONTEXT_DEPENDENT`. Kind: `OPERATING_OR_ANALYSIS_MECHANISM`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** Use prioritised requirements and constraints to select a consequential element, choose design concepts, allocate responsibilities, define interfaces and refine the resulting obligations; revisit earlier choices when evaluation reveals a problem.

**Trigger and required inputs:** A system or element needs deliberate architectural decomposition and the significant drivers are understood sufficiently to guide a choice. Sufficient prioritised drivers, feasible design concepts and ability to evaluate their consequences; requirements need not be complete forever.

**Produced constraint/evidence:** The chosen decomposition and interfaces can be traced to the drivers, and child obligations are made explicit. Its consumer is: Designers and affected stakeholders; algorithmic decomposition does not replace trade-off judgement.

**Costs, substitution and omission:** Use a focused local design decision when recursive decomposition would only reproduce the obvious.

**Assumptions, conflicts and failure:** Recursion can become a paperwork tree or freeze speculative requirements; following eight steps does not validate the chosen design.

**Retirement/reopening:** Reopen when child-level analysis, prototyping or changed drivers invalidate the parent choice.

**Abstraction:** Design of a system or architectural element through requirement allocation and interfaces. **Evidence boundary:** Evaluate whether the allocated elements can satisfy the selected scenarios and constraints, rather than count completed steps. Recursion can become a paperwork tree or freeze speculative requirements; following eight steps does not validate the chosen design.

**Relations:** ESA-REL021, ESA-REL025, ESA-REL026, ESA-REL027, ESA-REL047, ESA-REL061. **Tensions:** no separate named tension; local assumption/cost boundary still applies. **Source IDs:** ESA-S024, ESA-S025, ESA-S016, ESA-S010, ESA-S041.

### `EVOLVED_SOFTWARE_ARCHITECTURE::ESA-068` — Connector compatibility under well-formedness constraints

Status: `DOMAIN_SPECIFIC`. Kind: `CONDITIONAL_FORMAL_RESULT`. Crosswalk-worthy: YES, subject to trigger.

**Mechanism/criterion:** When using the Wright/CSP formalism, establish both connector conservatism and deadlock freedom along with port/role compatibility before transferring the theorem’s deadlock-freedom result to an instantiated connector.

**Trigger and required inputs:** A connector composition relies specifically on this formal deadlock-freedom guarantee. The theorem’s exact CSP semantics and compatibility relation; a conservative deadlock-free connector; implementation/model correspondence for any real-system claim.

**Produced constraint/evidence:** The specified instantiated connector is deadlock-free in the formal model under those conditions. Its consumer is: Formal modellers and implementers responsible for matching real interactions to the model.

**Costs, substitution and omission:** Use an ordinary protocol review or targeted model for a smaller obligation; do not impose Wright on unrelated architectures.

**Assumptions, conflicts and failure:** Compatibility alone is insufficient; non-conservative glue permits the source’s counterexample. Model checking and implementation refinement remain separate obligations.

**Retirement/reopening:** Reopen when glue, roles, port behaviour, topology or implementation mapping changes.

**Abstraction:** Formal component ports, connector roles and glue in the Wright/CSP model. **Evidence boundary:** Check the theorem conditions and formal result, then separately examine actual protocol refinement; no empirical deployment guarantee is implied. Compatibility alone is insufficient; non-conservative glue permits the source’s counterexample. Model checking and implementation refinement remain separate obligations.

**Relations:** ESA-REL019. **Tensions:** ESA-T004. **Source IDs:** ESA-S015.

## Reconciliation questions for Software Maintenance and Evolution

How does that independently studied lane distinguish observed maintenance burden from a hypothetical future change cost? Compare its object and measures with ESA-043/049 before equating “debt”, “changeability” or “interest”.

Do its change-impact methods recover the same dependency kinds as ESA-010/024, or are they complementary observations? Which assumptions and sampling limits remain after combination?

Can its change-control and migration mechanisms supply the observation, compatibility or transition obligations in ESA-033/038/039/044? Conversely, does this architecture lane supply a justified baseline or invariant that its maintenance process needs? These are questions, not findings about the unread lane.

When a departure improves the system, which lane establishes baseline revision and which establishes the actual maintenance consequence? Preserve the separation between detecting a change, authorising it and observing benefit.

## Reconciliation questions for Software Product Line Engineering

Does the independently studied family scope match the commonality/variation object in ESA-013, or does it include additional production, asset and economic commitments? Do not merge them solely because both say “family”.

Which per-variant obligations follow from architectural interfaces and quality trade-offs, and which require additional product-line mechanisms? How is variation constrained so that one configuration does not silently break another’s assumptions?

Can one interface or asset satisfy both ESA-007’s hidden-change function and the other lane’s variability function? What costs, incompatible variation models or additional verification obligations appear when combined?

When is a single product or a simpler variation point adequate? Does the other lane provide evidence strong enough to justify wider reuse investment, rather than treating this lane’s historical family discussion as proof of product-line economics?

## Required reconciliation tests

For each proposed merger, test **semantic equivalence** (same mechanism, object and consequence), **complementarity** (different necessary contributions), **redundancy** (one adequate implementation can serve both), **abstraction level** (criterion versus mechanism versus implementation), **incompatible assumptions**, **shared mechanisms/evidence**, and **new composition obligations**. A similar name or shared citation alone passes none of these tests.

Preserve selection, substitution, omission and retirement conditions. One mechanism may address multiple properties without erasing their lineage or criticism. A stronger later property may supersede a weaker formulation only with an explicit preserved link; it may not silently shrink the original denominator. Reconcile shared datasets before making evidence-strength claims.

## Evidence and authority boundary

The strongest formal result is model-relative. Field observations are setting-bound. Process superiority, universal economic benefit and open-ended autonomy are not established. This intake does not answer for either unread lane and does not establish target adoption. A later target-native crosswalk belongs in a new artefact and needs its own evidence and authority. The present export authorises no mutation.
