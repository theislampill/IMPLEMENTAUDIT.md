# EVOLVED_SYSTEMS_SAFETY_AUDIT_INTAKE

> Frozen external-research intake. It does not analyse or answer questions about any target repository or system. All target-system statements below remain questions for a separate audit.

## Population receipt

- **PROPERTY_POPULATION_TOTAL:** 68
- **PROPERTY_POPULATION_EXAMINED:** 68
- **PROPERTY_COVERAGE:** 68/68
- **ADMITTED_OR_CONTEXTUAL_PROPERTIES:** 54
- **REJECTED_SUPERSEDED_CEREMONIAL_OR_CONTESTED:** 14
- **SOURCE_POPULATION_SUMMARY:** 116 exact source records; source classes {"AUTHORITATIVE_ASSURANCE_REVIEW": 1, "AUTHORITATIVE_GOVERNMENT_HANDBOOK": 4, "AUTHORITATIVE_POLICY_ANALYSIS": 1, "AUTHORITATIVE_PRACTICE_GUIDANCE": 1, "AUTHORITATIVE_TECHNICAL_GUIDANCE": 1, "AVIATION_SAFETY_ASSESSMENT_GUIDANCE": 1, "COMMUNITY_TECHNICAL_STANDARD": 1, "CURRENT_ACCIDENT_INVESTIGATION_AUTHORITY_PROCESS": 2, "CURRENT_AVIATION_AUTHORITY_NOTICE": 1, "CURRENT_AVIATION_CHANGE_GUIDANCE": 1, "CURRENT_AVIATION_GUIDANCE": 4, "CURRENT_AVIATION_REGULATORY_GUIDANCE": 1, "CURRENT_GOVERNMENT_CLINICAL_SAFETY_GUIDANCE": 2, "CURRENT_GOVERNMENT_GUIDANCE": 1, "CURRENT_GOVERNMENT_PRACTICE_GUIDANCE": 1, "CURRENT_GOVERNMENT_SOFTWARE_ASSURANCE_GUIDANCE": 1, "CURRENT_GOVERNMENT_STANDARD": 1, "CURRENT_INTERGOVERNMENTAL_REQUIREMENTS": 1, "CURRENT_INTERGOVERNMENTAL_SAFETY_GUIDE": 2, "CURRENT_INTERGOVERNMENTAL_TECHNICAL_GUIDANCE": 1, "CURRENT_INTERGOVERNMENTAL_TECHNICAL_REPORT": 1, "CURRENT_INTERNATIONAL_STANDARD_ABSTRACT": 10, "CURRENT_OFFICIAL_ASSURANCE_MANUAL": 1, "CURRENT_OFFICIAL_GUIDANCE_PORTAL": 1, "CURRENT_PRIMARY_MILITARY_STANDARD": 1, "CURRENT_RAIL_REGULATORY_GUIDANCE": 1, "CURRENT_REGULATION": 2, "CURRENT_REGULATORY_GUIDANCE": 2, "CURRENT_REGULATORY_GUIDANCE_PORTAL": 1, "CURRENT_REGULATORY_GUIDE": 1, "CURRENT_REGULATORY_INCIDENT_ALERT": 1, "CURRENT_REGULATORY_POLICY": 1, "CURRENT_REGULATORY_TECHNICAL_GUIDANCE": 6, "FOUNDATIONAL_EDITED_BOOK": 1, "FOUNDATIONAL_HIGH_RELIABILITY_ORGANISATION_STUDY": 1, "FOUNDATIONAL_PEER_REVIEWED_SYSTEMS_PAPER": 1, "FOUNDATIONAL_SOCIOLOGICAL_BOOK": 1, "GOVERNMENT_COMMISSIONED_CRITICAL_REVIEW": 1, "GOVERNMENT_SPONSORED_COMPARATIVE_EVALUATION": 1, "GOVERNMENT_TECHNICAL_RESEARCH": 1, "HUMAN_FACTORS_PRIMARY_TECHNICAL_WRITING": 1, "INDEPENDENT_TECHNICAL_REVIEW": 1, "INTERGOVERNMENTAL_SAFETY_REPORT": 1, "INTERNATIONAL_SAFETY_GUIDE": 1, "MAJOR_ACCIDENT_INDEPENDENT_REVIEW": 2, "MAJOR_ACCIDENT_INTERGOVERNMENTAL_REPORT": 1, "MAJOR_ACCIDENT_OFFICIAL_REPORT": 7, "MAJOR_OPERATIONAL_SAFETY_REVIEW": 1, "OFFICIAL_FOLLOW_UP_REPORT": 1, "OFFICIAL_GOVERNANCE_PROCESS": 1, "OFFICIAL_ORGANISATIONAL_HISTORY": 1, "OFFICIAL_PERFORMANCE_REPORTING": 1, "OFFICIAL_REGULATORY_POLICY": 1, "OFFICIAL_TECHNICAL_GUIDANCE": 1, "ORIGINAL_METHOD_HANDBOOK": 1, "ORIGINAL_PEER_REVIEWED_THEORY_PAPER": 1, "PEER_REVIEWED_ACCIDENT_ANALYSIS": 1, "PEER_REVIEWED_ASSURANCE_RESEARCH": 1, "PEER_REVIEWED_CONCEPTUAL_ANALYSIS": 1, "PEER_REVIEWED_CONCEPTUAL_ARTICLE": 1, "PEER_REVIEWED_CONTROLLED_EXPERIMENT": 1, "PEER_REVIEWED_CRITICAL_ESSAY": 1, "PEER_REVIEWED_CRITICAL_REVIEW": 1, "PEER_REVIEWED_HISTORICAL_CRITICISM": 1, "PEER_REVIEWED_LITERATURE_REVIEW": 1, "PEER_REVIEWED_META_ANALYSIS": 1, "PEER_REVIEWED_METHOD_CRITICISM": 1, "PEER_REVIEWED_POLICY_ANALYSIS": 1, "PEER_REVIEWED_REVIEW": 1, "PEER_REVIEWED_SCOPING_REVIEW": 1, "PEER_REVIEWED_SYSTEMATIC_REVIEW": 4, "PEER_REVIEWED_THEORY_AND_CRITIQUE": 1, "PRIMARY_GOVERNMENT_TECHNICAL_PAPER": 1, "PRIMARY_HISTORICAL_BOOK_CATALOGUE": 1, "PRIMARY_HISTORICAL_GOVERNMENT_REPORT_CATALOGUE": 1, "PRIMARY_HISTORICAL_MILITARY_PROCEDURE": 1, "PRIMARY_HISTORICAL_SYSTEM_SAFETY_PAPER": 1, "PRIMARY_MILITARY_STANDARD": 1, "PRIMARY_PRACTITIONER_HISTORICAL_RETROSPECTIVE": 1, "TECHNICAL_CRITICAL_REVIEW": 1, "TECHNICAL_RESEARCH_PAPER": 1}; evidence labels {"ACCIDENT_CASE_EVIDENCE": 14, "CONTESTED": 2, "EMPIRICAL_OR_DOMAIN_FINDING": 6, "FORMAL_OR_MODEL_DEPENDENT": 6, "SOURCE_ESTABLISHED": 88}.

## EVIDENCE_STRENGTH_PARTITIONS

- **HISTORICAL_PROVENANCE:** Generally high for FMECA, FTA, HAZOP, military/aerospace system safety, functional safety, safety cases, STAMP/STPA and major accident reports because primary or authoritative records are present.
- **FORMAL_OR_MODEL:** High for the semantics and limits of FTA, formal methods, risk-matrix mathematics and control-loop representation; this is not equivalent to high field-effect evidence.
- **ACCIDENT_CASE:** High for the existence of interaction, organisational, stale-assumption, common-mode and assurance failure mechanisms; cases do not estimate universal intervention effect sizes.
- **EMPIRICAL_COMPARATIVE:** Uneven and usually low-to-moderate. STPA, assurance-case formats, resilience indicators, culture interventions and exact process prescriptions lack broad controlled comparison.
- **DOMAIN_PRACTICE:** High for lifecycle hazard management, configuration/change control, defence in depth, functional/development assurance, operational limits, incident investigation and recommendation tracking in their domains.
- **STANDARD_OR_REGULATORY:** High as evidence of recognised/required practice, explicitly not proof that a prescribed implementation is optimal.
- **TRANSFERABILITY:** Highest for mechanism-level properties such as explicit loss/hazard framing, unsafe interaction, current feedback, configuration identity, action verification and proportionality; lower for domain labels, levels and certification artefacts.
- **ASSUMPTION_SENSITIVITY:** High throughout because safety evidence depends on boundary, configuration, environment, authority, independence and observability.

## TOP_CROSSWALK_PROPERTIES

All 54 admitted or contextual properties are crosswalk-worthy. Inclusion here does not imply target-system applicability or adoption.

### ESS-001 — Explicit unacceptable-loss framing

- **PROPERTY_ID:** ESS-001
- **PROPERTY_NAME:** Explicit unacceptable-loss framing
- **LOSS_OR_HAZARD:** Unacceptable injury, fatality, mission loss, environmental harm, critical-service loss or other explicitly governed loss.
- **FAILURE_MODE:** Analysis and controls are aimed at proxies while the actual loss remains unarticulated or shifts unnoticed.
- **MATURE_FORM:** A concise, current, decision-linked definition of unacceptable loss that bounds later analysis without pretending completeness.
- **TRIGGER:** Any consequential system, material change, novel operation or unresolved safety decision.
- **CHEAP_PATH:** For trivial reversible work, state the bounded loss in one line and use the authoritative deterministic check; no elaborate taxonomy.
- **REQUIRED_PRECONDITIONS:** Stakeholders and authority must be known; loss statements must be specific enough to discriminate decisions.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Evidence that the loss set still matches current use, users, environment and public exposure.
- **AUTHORITY_BOUNDARY:** A competent owner must be authorised to define tolerability and resolve conflicts among safety, mission and availability.
- **CRITICISMS:** Different domains define accident, mishap and harm differently; not every adverse outcome is a safety loss.
- **ANTI_CEREMONY_BOUNDARY:** The property is the decision boundary; a “loss list” document or STPA worksheet is optional.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Explicit unacceptable-loss framing
- **LOSS_OR_HAZARD:** Unacceptable injury, fatality, mission loss, environmental harm, critical-service loss or other explicitly governed loss.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Explicit unacceptable-loss framing.
- **CONTROL_ACTION:** Name losses, affected stakeholders and decision authority; derive hazardous system states and constraints from them.
- **REQUIRED_FEEDBACK:** Evidence that the loss set still matches current use, users, environment and public exposure.
- **PROCESS_MODEL_ASSUMPTION:** Stakeholders and authority must be known; loss statements must be specific enough to discriminate decisions.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** A competent owner must be authorised to define tolerability and resolve conflicts among safety, mission and availability.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** For trivial reversible work, state the bounded loss in one line and use the authoritative deterministic check; no elaborate taxonomy.
- **MATURE_FORM:** A concise, current, decision-linked definition of unacceptable loss that bounds later analysis without pretending completeness.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Explicit unacceptable-loss framing
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** For trivial reversible work, state the bounded loss in one line and use the authoritative deterministic check; no elaborate taxonomy.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** A concise, current, decision-linked definition of unacceptable loss that bounds later analysis without pretending completeness.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** MODERATE — mechanism is coherent but depends on model scope and assumptions.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S014, S015, S018, S033; critical/contrary: S038, S066.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Explicit unacceptable-loss framing, rather than only a proxy, component check or document status?
- When the trigger is present — Any consequential system, material change, novel operation or unresolved safety decision. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Evidence that the loss set still matches current use, users, environment and public exposure. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: A competent owner must be authorised to define tolerability and resolve conflicts among safety, mission and availability.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: For trivial reversible work, state the bounded loss in one line and use the authoritative deterministic check; no elaborate taxonomy.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-002 — Hazardous system-state framing distinct from failure

- **PROPERTY_ID:** ESS-002
- **PROPERTY_NAME:** Hazardous system-state framing distinct from failure
- **LOSS_OR_HAZARD:** A system state or condition capable of contributing to unacceptable loss.
- **FAILURE_MODE:** No component is classified as failed, yet the system enters an unsafe state through context, interaction, performance insufficiency or exposure.
- **MATURE_FORM:** A current loss-linked hazardous-state model with explicit boundary, exposure and causal assumptions.
- **TRIGGER:** Systems with software, humans, adaptive functions, hazardous energy/material, changing environments or nontrivial interfaces.
- **CHEAP_PATH:** A simple local task with a complete deterministic invariant may use that invariant directly rather than a separate hazard ontology.
- **REQUIRED_PRECONDITIONS:** A defined system boundary, environment and loss relation; hazards must be controllable enough to inform design or operation.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Observable indicators of hazardous state, exposure and boundary conditions—not only component health.
- **AUTHORITY_BOUNDARY:** Ownership of system boundary and authority to impose constraints across components/interfaces.
- **CRITICISMS:** Hazard definitions differ across MIL-STD-882, IEC/ISO, process safety and STPA; terminology should not be forced.
- **ANTI_CEREMONY_BOUNDARY:** The property is the loss-capable state model; exact hazard-log columns are not required.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Hazardous system-state framing distinct from failure
- **LOSS_OR_HAZARD:** A system state or condition capable of contributing to unacceptable loss.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Hazardous system-state framing distinct from failure.
- **CONTROL_ACTION:** Model hazards separately from causes; then search failures, interactions, environmental conditions and control flaws that can create them.
- **REQUIRED_FEEDBACK:** Observable indicators of hazardous state, exposure and boundary conditions—not only component health.
- **PROCESS_MODEL_ASSUMPTION:** A defined system boundary, environment and loss relation; hazards must be controllable enough to inform design or operation.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Ownership of system boundary and authority to impose constraints across components/interfaces.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** A simple local task with a complete deterministic invariant may use that invariant directly rather than a separate hazard ontology.
- **MATURE_FORM:** A current loss-linked hazardous-state model with explicit boundary, exposure and causal assumptions.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Hazardous system-state framing distinct from failure
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** A simple local task with a complete deterministic invariant may use that invariant directly rather than a separate hazard ontology.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** A current loss-linked hazardous-state model with explicit boundary, exposure and causal assumptions.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** MODERATE — mechanism is coherent but depends on model scope and assumptions.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S014, S015, S018, S025, S033; critical/contrary: S017, S109.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Hazardous system-state framing distinct from failure, rather than only a proxy, component check or document status?
- When the trigger is present — Systems with software, humans, adaptive functions, hazardous energy/material, changing environments or nontrivial interfaces. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Observable indicators of hazardous state, exposure and boundary conditions—not only component health. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Ownership of system boundary and authority to impose constraints across components/interfaces.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: A simple local task with a complete deterministic invariant may use that invariant directly rather than a separate hazard ontology.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-003 — Enforceable safety constraints

- **PROPERTY_ID:** ESS-003
- **PROPERTY_NAME:** Enforceable safety constraints
- **LOSS_OR_HAZARD:** Loss arising because the system permits a hazardous state or action outside its safe envelope.
- **FAILURE_MODE:** A “control” is documented but not allocated, implemented, verified, monitored or enforceable in operation.
- **MATURE_FORM:** The minimum sufficient constraint is explicit, allocated, enforceable, verified and paired with feedback or bounded assurance.
- **TRIGGER:** Whenever a credible hazard remains after elimination or redesign.
- **CHEAP_PATH:** Where a deterministic existing rule already proves the safe condition, record/reuse it rather than create duplicate safety requirements.
- **REQUIRED_PRECONDITIONS:** Constraint must be testable or otherwise assessable and tied to a controller with feasible authority.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** State/feedback showing the constraint is maintained and alarms when it is violated or unverifiable.
- **AUTHORITY_BOUNDARY:** The allocated controller must possess real control authority and resources; responsibility without authority is insufficient.
- **CRITICISMS:** Constraint language can become model bureaucracy; not all safety behaviour is reducible to static rules.
- **ANTI_CEREMONY_BOUNDARY:** A requirements database is optional; live allocation and enforcement are the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-036 context-sensitive fail-operational behaviour and ESS-046 cheap path can conflict with overly rigid constraint enforcement.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Enforceable safety constraints
- **LOSS_OR_HAZARD:** Hazardous state permitted or loss not bounded
- **CONTROLLER:** Allocated controller or design authority
- **CONTROLLED_PROCESS:** System behaviour and operating envelope
- **SAFETY_CONSTRAINT:** The identified hazardous state/action shall be prevented, bounded or mitigated
- **CONTROL_ACTION:** Design interlock, algorithmic limit, procedure, authority rule or barrier
- **REQUIRED_FEEDBACK:** Current state, constraint status, exceptions and barrier health
- **PROCESS_MODEL_ASSUMPTION:** The model correctly links the constraint to the hazard under current conditions
- **DELAY_OR_OBSERVABILITY_RISK:** Delayed or missing confirmation can leave a documented constraint unenforced
- **AUTHORITY_BOUNDARY:** The controller must possess actual authority; acceptance authority owns exceptions
- **FAILURE_IF_OVER_APPLIED:** Overly rigid constraints can suppress necessary safe adaptation or create bypasses
- **CHEAP_PATH:** Use an existing deterministic guard when it completely discriminates the condition
- **MATURE_FORM:** Allocated, enforceable, monitored and change-current constraint


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Enforceable safety constraints
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Where a deterministic existing rule already proves the safe condition, record/reuse it rather than create duplicate safety requirements.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** The minimum sufficient constraint is explicit, allocated, enforceable, verified and paired with feedback or bounded assurance.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S015, S018, S029, S100; critical/contrary: S048, S066.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Enforceable safety constraints, rather than only a proxy, component check or document status?
- When the trigger is present — Whenever a credible hazard remains after elimination or redesign. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — State/feedback showing the constraint is maintained and alarms when it is violated or unverifiable. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: The allocated controller must possess real control authority and resources; responsibility without authority is insufficient.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Where a deterministic existing rule already proves the safe condition, record/reuse it rather than create duplicate safety requirements.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-004 — Lifecycle hazard identification with explicit completeness boundaries

- **PROPERTY_ID:** ESS-004
- **PROPERTY_NAME:** Lifecycle hazard identification with explicit completeness boundaries
- **LOSS_OR_HAZARD:** Unacceptable loss from an unsearched lifecycle phase, stakeholder or operational scenario.
- **FAILURE_MODE:** The hazard population is treated as complete because a meeting or worksheet ended, despite unsearched boundaries or new evidence.
- **MATURE_FORM:** Claim bounded coverage over a declared population; never claim that all possible hazards are known.
- **TRIGGER:** Novel/high-consequence systems; phase transitions; operational change; significant incidents; emerging evidence.
- **CHEAP_PATH:** Low-consequence reversible work needs only a bounded check of known hazards and the deterministic discriminator, not a comprehensive workshop.
- **REQUIRED_PRECONDITIONS:** Access to lifecycle knowledge and representative operators/maintainers; explicit stopping/saturation criteria.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Coverage ledger, unresolved assumptions, operational signals and change triggers.
- **AUTHORITY_BOUNDARY:** A named owner must decide when coverage is sufficient and when reopening is required.
- **CRITICISMS:** True completeness is unprovable for open systems; exhaustive process can consume effort without changing design.
- **ANTI_CEREMONY_BOUNDARY:** The property is coverage and reopening discipline; a prescribed list of analysis reports is domain-specific.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Lifecycle hazard identification with explicit completeness boundaries
- **LOSS_OR_HAZARD:** Unacceptable loss from an unsearched lifecycle phase, stakeholder or operational scenario.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Lifecycle hazard identification with explicit completeness boundaries.
- **CONTROL_ACTION:** Define search scope, phases, methods, expertise, exclusions, assumptions and residual unknowns; revisit on triggers.
- **REQUIRED_FEEDBACK:** Coverage ledger, unresolved assumptions, operational signals and change triggers.
- **PROCESS_MODEL_ASSUMPTION:** Access to lifecycle knowledge and representative operators/maintainers; explicit stopping/saturation criteria.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** A named owner must decide when coverage is sufficient and when reopening is required.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Low-consequence reversible work needs only a bounded check of known hazards and the deterministic discriminator, not a comprehensive workshop.
- **MATURE_FORM:** Claim bounded coverage over a declared population; never claim that all possible hazards are known.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Lifecycle hazard identification with explicit completeness boundaries
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Low-consequence reversible work needs only a bounded check of known hazards and the deterministic discriminator, not a comprehensive workshop.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Claim bounded coverage over a declared population; never claim that all possible hazards are known.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** MODERATE — mechanism is coherent but depends on model scope and assumptions.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S014, S015, S027, S094; critical/contrary: S038, S048, S109.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Lifecycle hazard identification with explicit completeness boundaries, rather than only a proxy, component check or document status?
- When the trigger is present — Novel/high-consequence systems; phase transitions; operational change; significant incidents; emerging evidence. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Coverage ledger, unresolved assumptions, operational signals and change triggers. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: A named owner must decide when coverage is sufficient and when reopening is required.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Low-consequence reversible work needs only a bounded check of known hazards and the deterministic discriminator, not a comprehensive workshop.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-005 — Component failure-effects analysis as a bounded complement

- **PROPERTY_ID:** ESS-005
- **PROPERTY_NAME:** Component failure-effects analysis as a bounded complement
- **LOSS_OR_HAZARD:** Loss caused by a plausible item/function failure and its propagated effects.
- **FAILURE_MODE:** A component failure has hazardous effects, is undetected, or combines with other conditions not represented in design.
- **MATURE_FORM:** Use FMEA for what it represents well; do not treat a completed FMEA as a complete system-safety analysis.
- **TRIGGER:** Hardware/component/process failure modes are material and interfaces are sufficiently defined.
- **CHEAP_PATH:** Skip a full worksheet where the component is non-safety-significant, trivially replaceable, or a validated deterministic test already exhausts the relevant failure set.
- **REQUIRED_PRECONDITIONS:** Defined functions/boundaries, knowledgeable participants and connection to system consequences and controls.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Failure detection coverage, field failures, common-cause data and control effectiveness.
- **AUTHORITY_BOUNDARY:** Owners must be able to change design, detection, maintenance or architecture based on findings.
- **CRITICISMS:** Bottom-up FMEA can miss unsafe interactions without component failure and is often undermined by weak occurrence data.
- **ANTI_CEREMONY_BOUNDARY:** The property is structured failure search and effect propagation; the worksheet and RPN are not general requirements.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-008 unsafe-interaction analysis prevents component-failure analysis from claiming sufficiency.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Component failure-effects analysis as a bounded complement
- **LOSS_OR_HAZARD:** Loss caused by a plausible item/function failure and its propagated effects.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Component failure-effects analysis as a bounded complement.
- **CONTROL_ACTION:** Perform function/item-based FMEA/FMECA focused on safety-significant elements and feed results into system hazard/control analysis.
- **REQUIRED_FEEDBACK:** Failure detection coverage, field failures, common-cause data and control effectiveness.
- **PROCESS_MODEL_ASSUMPTION:** Defined functions/boundaries, knowledgeable participants and connection to system consequences and controls.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Owners must be able to change design, detection, maintenance or architecture based on findings.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Skip a full worksheet where the component is non-safety-significant, trivially replaceable, or a validated deterministic test already exhausts the relevant failure set.
- **MATURE_FORM:** Use FMEA for what it represents well; do not treat a completed FMEA as a complete system-safety analysis.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Component failure-effects analysis as a bounded complement
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Skip a full worksheet where the component is non-safety-significant, trivially replaceable, or a validated deterministic test already exhausts the relevant failure set.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Use FMEA for what it represents well; do not treat a completed FMEA as a complete system-safety analysis.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_WITHIN_REPRESENTED_CLASS — technique semantics are established; completeness outside its representation is not.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** CONTEXT_DEPENDENT — transfer requires matching the technique to the causal/hazard class.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S005, S006, S007, S012; critical/contrary: S019, S036, S109.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Component failure-effects analysis as a bounded complement, rather than only a proxy, component check or document status?
- When the trigger is present — Hardware/component/process failure modes are material and interfaces are sufficiently defined. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Failure detection coverage, field failures, common-cause data and control effectiveness. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Owners must be able to change design, detection, maintenance or architecture based on findings.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Skip a full worksheet where the component is non-safety-significant, trivially replaceable, or a validated deterministic test already exhausts the relevant failure set.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-006 — Top-down causal-path and logical analysis

- **PROPERTY_ID:** ESS-006
- **PROPERTY_NAME:** Top-down causal-path and logical analysis
- **LOSS_OR_HAZARD:** A defined hazardous top event or consequence sequence.
- **FAILURE_MODE:** The top event occurs through a combination of failures/conditions that was not understood or quantitatively bounded.
- **MATURE_FORM:** Use top-down logic where the event structure is meaningful; pair it with other searches for unmodelled interactions and organisational causes.
- **TRIGGER:** A well-defined top event, architecture and causal logic; quantitative use requires data and dependence modelling.
- **CHEAP_PATH:** For a simple deterministic invariant, use direct proof/test; do not construct a tree that merely restates the invariant.
- **REQUIRED_PRECONDITIONS:** Stable boundary, meaningful decomposition and explicit common-cause/uncertainty assumptions.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Configuration currentness, event definitions, dependency/common-cause evidence and operational data.
- **AUTHORITY_BOUNDARY:** Decision owner can act on dominant cut sets, barriers or design alternatives.
- **CRITICISMS:** Trees represent only modelled causes and may omit organisational/software interactions and adaptive behaviour.
- **ANTI_CEREMONY_BOUNDARY:** The property is transparent causal decomposition; gate symbols and large diagrams are optional.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-015 technique complementarity limits overconfidence in a single top-down model.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Top-down causal-path and logical analysis
- **LOSS_OR_HAZARD:** A defined hazardous top event or consequence sequence.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Top-down causal-path and logical analysis.
- **CONTROL_ACTION:** Construct qualitative logic first; quantify only with defensible data/dependence models; use event trees for post-initiator progression.
- **REQUIRED_FEEDBACK:** Configuration currentness, event definitions, dependency/common-cause evidence and operational data.
- **PROCESS_MODEL_ASSUMPTION:** Stable boundary, meaningful decomposition and explicit common-cause/uncertainty assumptions.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Decision owner can act on dominant cut sets, barriers or design alternatives.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** For a simple deterministic invariant, use direct proof/test; do not construct a tree that merely restates the invariant.
- **MATURE_FORM:** Use top-down logic where the event structure is meaningful; pair it with other searches for unmodelled interactions and organisational causes.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Top-down causal-path and logical analysis
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** For a simple deterministic invariant, use direct proof/test; do not construct a tree that merely restates the invariant.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Use top-down logic where the event structure is meaningful; pair it with other searches for unmodelled interactions and organisational causes.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_WITHIN_REPRESENTED_CLASS — technique semantics are established; completeness outside its representation is not.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** CONTEXT_DEPENDENT — transfer requires matching the technique to the causal/hazard class.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S008, S009, S040, S041, S096; critical/contrary: S017, S038, S109.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Top-down causal-path and logical analysis, rather than only a proxy, component check or document status?
- When the trigger is present — A well-defined top event, architecture and causal logic; quantitative use requires data and dependence modelling. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Configuration currentness, event definitions, dependency/common-cause evidence and operational data. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Decision owner can act on dominant cut sets, barriers or design alternatives.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: For a simple deterministic invariant, use direct proof/test; do not construct a tree that merely restates the invariant.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-007 — Structured process-deviation search

- **PROPERTY_ID:** ESS-007
- **PROPERTY_NAME:** Structured process-deviation search
- **LOSS_OR_HAZARD:** Loss from process deviation, abnormal operation or interaction between process parameters and safeguards.
- **FAILURE_MODE:** A deviation arises outside assumed intent or a safeguard is inadequate/dependent.
- **MATURE_FORM:** Structured deviation prompts plus empowered expertise and action closure; method depth proportional to hazard and change.
- **TRIGGER:** Hazardous processes, complex flows/procedures or modifications where deviation search has decision value.
- **CHEAP_PATH:** Do not convene a full HAZOP for a tiny reversible change with a complete change discriminator; use focused review.
- **REQUIRED_PRECONDITIONS:** Accurate design intent, competent multidisciplinary team, bounded nodes and action follow-through.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Action completion, safeguard state, deviations/near misses and change currentness.
- **AUTHORITY_BOUNDARY:** Facilitator/review team must be able to obtain design changes or escalate unresolved hazards.
- **CRITICISMS:** Conventional HAZOP does not by itself estimate likelihood or establish complete causal coverage.
- **ANTI_CEREMONY_BOUNDARY:** The property is disciplined deviation search; exact guideword tables and workshop duration are not universal.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Structured process-deviation search
- **LOSS_OR_HAZARD:** Loss from process deviation, abnormal operation or interaction between process parameters and safeguards.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Structured process-deviation search.
- **CONTROL_ACTION:** Use guidewords or equivalent structured prompts at nodes/functions; record decisions, actions and unresolved assumptions.
- **REQUIRED_FEEDBACK:** Action completion, safeguard state, deviations/near misses and change currentness.
- **PROCESS_MODEL_ASSUMPTION:** Accurate design intent, competent multidisciplinary team, bounded nodes and action follow-through.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Facilitator/review team must be able to obtain design changes or escalate unresolved hazards.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Do not convene a full HAZOP for a tiny reversible change with a complete change discriminator; use focused review.
- **MATURE_FORM:** Structured deviation prompts plus empowered expertise and action closure; method depth proportional to hazard and change.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Structured process-deviation search
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Do not convene a full HAZOP for a tiny reversible change with a complete change discriminator; use focused review.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Structured deviation prompts plus empowered expertise and action closure; method depth proportional to hazard and change.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_WITHIN_REPRESENTED_CLASS — technique semantics are established; completeness outside its representation is not.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** CONTEXT_DEPENDENT — transfer requires matching the technique to the causal/hazard class.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S010, S011, S094, S095; critical/contrary: S038, S066.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Structured process-deviation search, rather than only a proxy, component check or document status?
- When the trigger is present — Hazardous processes, complex flows/procedures or modifications where deviation search has decision value. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Action completion, safeguard state, deviations/near misses and change currentness. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Facilitator/review team must be able to obtain design changes or escalate unresolved hazards.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Do not convene a full HAZOP for a tiny reversible change with a complete change discriminator; use focused review.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-008 — Unsafe interaction and unsafe-control analysis

- **PROPERTY_ID:** ESS-008
- **PROPERTY_NAME:** Unsafe interaction and unsafe-control analysis
- **LOSS_OR_HAZARD:** Loss arising from unsafe coordination/control rather than a single failed component.
- **FAILURE_MODE:** An action is unsafe in context, missing when required, delivered at the wrong time/order/duration, or combined with conflicting actions.
- **MATURE_FORM:** Explicitly reason about unsafe composition and control context, using the cheapest adequate representation and complementary techniques.
- **TRIGGER:** Software-intensive, autonomous, tightly coupled, multi-controller or human-automation systems.
- **CHEAP_PATH:** Where a simple component failure fully determines the hazard, use the cheaper failure analysis and direct control; do not force a control diagram.
- **REQUIRED_PRECONDITIONS:** A usable control/interaction model, representative operational knowledge and explicit system boundary.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Actual action timing/order/duration, process state, controller modes, feedback quality and handoffs.
- **AUTHORITY_BOUNDARY:** Controllers must have clear authority and conflict-resolution rules; analysis findings need a design/operations consumer.
- **CRITICISMS:** STPA is not uniquely entitled to interaction reasoning; other system safety, SOTIF, HAZOP and scenario methods can contribute.
- **ANTI_CEREMONY_BOUNDARY:** The property is interaction/control reasoning; STPA terminology and diagrams are optional.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-005/006 failure analyses may be cheaper or stronger for simple physical failure mechanisms.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Unsafe interaction and unsafe-control analysis
- **LOSS_OR_HAZARD:** Loss from locally correct but jointly unsafe actions
- **CONTROLLER:** One or more technical, human or organisational controllers
- **CONTROLLED_PROCESS:** Shared system process with coupled states
- **SAFETY_CONSTRAINT:** Control actions shall be safe for the current system context, timing, order and duration
- **CONTROL_ACTION:** Issue, withhold, sequence, bound or coordinate actions and resolve conflicts
- **REQUIRED_FEEDBACK:** Process state, action receipt/effect, modes, peer-controller actions and environmental context
- **PROCESS_MODEL_ASSUMPTION:** Each controller’s process model reflects the actual shared state and authority of other controllers
- **DELAY_OR_OBSERVABILITY_RISK:** Delayed/stale feedback can make individually rational commands jointly unsafe
- **AUTHORITY_BOUNDARY:** Overlapping controllers need explicit precedence, arbitration and escalation
- **FAILURE_IF_OVER_APPLIED:** Over-modelled control structures can consume effort without changing a decision and can obscure simple hazards
- **CHEAP_PATH:** Use direct interface tests or a compact state table where they fully discriminate interactions
- **MATURE_FORM:** Hazard-linked interaction model with enforceable coordination constraints and current feedback


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Unsafe interaction and unsafe-control analysis
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Where a simple component failure fully determines the hazard, use the cheaper failure analysis and direct control; do not force a control diagram.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Explicitly reason about unsafe composition and control context, using the cheapest adequate representation and complementary techniques.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S014, S017, S018, S020, S025, S109; critical/contrary: S019, S020, S109.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Unsafe interaction and unsafe-control analysis, rather than only a proxy, component check or document status?
- When the trigger is present — Software-intensive, autonomous, tightly coupled, multi-controller or human-automation systems. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Actual action timing/order/duration, process state, controller modes, feedback quality and handoffs. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Controllers must have clear authority and conflict-resolution rules; analysis findings need a design/operations consumer.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Where a simple component failure fully determines the hazard, use the cheaper failure analysis and direct control; do not force a control diagram.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-009 — Closed-loop control and feedback integrity

- **PROPERTY_ID:** ESS-009
- **PROPERTY_NAME:** Closed-loop control and feedback integrity
- **LOSS_OR_HAZARD:** Loss because the controlled process did not reach or remain in the intended safe state.
- **FAILURE_MODE:** The controller issues a nominally safe command but actuation fails, process response differs, or feedback falsely confirms success.
- **MATURE_FORM:** Every consequential control has evidence sufficient to establish intended state, or the system treats state as unknown and constrains operation.
- **TRIGGER:** Consequential control actions, remote/autonomous actuation, interlocks, shutdown, recovery and distributed control.
- **CHEAP_PATH:** For local directly observable reversible actions, immediate observation/test can serve as the feedback path without additional instrumentation.
- **REQUIRED_PRECONDITIONS:** Sensor/feedback path coverage, semantics and timing must match the safety decision.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** State-based confirmation, feedback freshness/integrity, actuator/process health and observability gaps.
- **AUTHORITY_BOUNDARY:** Controller must be authorised to act on missing/invalid feedback and to enter a safe/degraded mode.
- **CRITICISMS:** Additional sensors can share failure modes; feedback can create complexity or false confidence.
- **ANTI_CEREMONY_BOUNDARY:** The property is state confirmation and bounded response; a particular control diagram is not required.
- **POSSIBLE_CONFLICTING_PROPERTY:** Availability and latency can conflict with repeated confirmation; see ESS-036.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Closed-loop control and feedback integrity
- **LOSS_OR_HAZARD:** Loss because commanded safe behaviour was not physically achieved
- **CONTROLLER:** Technical or human controller
- **CONTROLLED_PROCESS:** Physical/software/organisational process
- **SAFETY_CONSTRAINT:** The intended safety state shall be achieved and confirmed within the required time
- **CONTROL_ACTION:** Issue control and verify effect; inhibit or degrade when confirmation is invalid
- **REQUIRED_FEEDBACK:** Independent, current and semantically adequate process-state feedback
- **PROCESS_MODEL_ASSUMPTION:** Feedback measures the process rather than merely echoing the command
- **DELAY_OR_OBSERVABILITY_RISK:** Latency can permit hazard progression before mismatch is detected
- **AUTHORITY_BOUNDARY:** Controller needs authority to stop, retry, isolate or degrade on uncertain state
- **FAILURE_IF_OVER_APPLIED:** Excessive confirmation latency or false alarms can make necessary service unavailable
- **CHEAP_PATH:** Direct observation or deterministic state check for local reversible action
- **MATURE_FORM:** State-confirmed closed loop with explicit invalid/stale-feedback semantics


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Closed-loop control and feedback integrity
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** For local directly observable reversible actions, immediate observation/test can serve as the feedback path without additional instrumentation.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Every consequential control has evidence sufficient to establish intended state, or the system treats state as unknown and constrains operation.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S018, S051, S058, S089, S101; critical/contrary: S050, S074.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Closed-loop control and feedback integrity, rather than only a proxy, component check or document status?
- When the trigger is present — Consequential control actions, remote/autonomous actuation, interlocks, shutdown, recovery and distributed control. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — State-based confirmation, feedback freshness/integrity, actuator/process health and observability gaps. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Controller must be authorised to act on missing/invalid feedback and to enter a safe/degraded mode.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: For local directly observable reversible actions, immediate observation/test can serve as the feedback path without additional instrumentation.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-010 — Controller process-model and mode consistency

- **PROPERTY_ID:** ESS-010
- **PROPERTY_NAME:** Controller process-model and mode consistency
- **LOSS_OR_HAZARD:** Loss from mode confusion, automation surprise, incorrect state inference or hidden environmental change.
- **FAILURE_MODE:** A command is safe in the believed state but unsafe in the actual state.
- **MATURE_FORM:** Make safety-relevant process-model assumptions visible, monitored and fail-bounded.
- **TRIGGER:** Mode-rich automation, distributed systems, remote operation, delayed observability or adaptive functions.
- **CHEAP_PATH:** A stateless local action with directly visible conditions may require only a simple precondition check.
- **REQUIRED_PRECONDITIONS:** Model variables must be linked to observable state and updated at a rate adequate to the hazard dynamics.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Current mode/state, transition completion, environment, authority and model-confidence indicators.
- **AUTHORITY_BOUNDARY:** Controller must be able to refuse action or escalate when model confidence is insufficient.
- **CRITICISMS:** Perfect model agreement is impossible; excessive transparency can increase workload.
- **ANTI_CEREMONY_BOUNDARY:** The property is model-state consistency; a STPA “process model” box is optional.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Controller process-model and mode consistency
- **LOSS_OR_HAZARD:** Loss from mode confusion, automation surprise, incorrect state inference or hidden environmental change.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Controller process-model and mode consistency.
- **CONTROL_ACTION:** Expose modes and assumptions; reconcile state estimates; detect divergence; design transitions and fallback behaviour.
- **REQUIRED_FEEDBACK:** Current mode/state, transition completion, environment, authority and model-confidence indicators.
- **PROCESS_MODEL_ASSUMPTION:** Model variables must be linked to observable state and updated at a rate adequate to the hazard dynamics.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Controller must be able to refuse action or escalate when model confidence is insufficient.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** A stateless local action with directly visible conditions may require only a simple precondition check.
- **MATURE_FORM:** Make safety-relevant process-model assumptions visible, monitored and fail-bounded.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Controller process-model and mode consistency
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** A stateless local action with directly visible conditions may require only a simple precondition check.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Make safety-relevant process-model assumptions visible, monitored and fail-bounded.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S018, S063, S064, S088, S089, S106; critical/contrary: S074, S109.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Controller process-model and mode consistency, rather than only a proxy, component check or document status?
- When the trigger is present — Mode-rich automation, distributed systems, remote operation, delayed observability or adaptive functions. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Current mode/state, transition completion, environment, authority and model-confidence indicators. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Controller must be able to refuse action or escalate when model confidence is insufficient.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: A stateless local action with directly visible conditions may require only a simple precondition check.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-011 — Timing, ordering, duration and transition semantics

- **PROPERTY_ID:** ESS-011
- **PROPERTY_NAME:** Timing, ordering, duration and transition semantics
- **LOSS_OR_HAZARD:** Loss during transient states or because control timing violates the safe envelope.
- **FAILURE_MODE:** Action sequencing and state transitions compose into a hazardous condition despite correct static requirements.
- **MATURE_FORM:** Apply temporal rigour where timing can change safety; use direct atomic checks where it cannot.
- **TRIGGER:** Real-time, distributed, asynchronous, autonomous, start-up/shutdown and handoff operations.
- **CHEAP_PATH:** A synchronous local operation with atomic deterministic semantics may need only a direct timeout/completion check.
- **REQUIRED_PRECONDITIONS:** Known timing budgets, transition states, clock/order assumptions and failure handling.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Timestamped actions, transition state, completion, retries, timeout and causal order.
- **AUTHORITY_BOUNDARY:** Controller/arbitrator can enforce ordering and block unsafe transitions.
- **CRITICISMS:** Temporal formalisation can be expensive and false precision can hide uncertain physical timing.
- **ANTI_CEREMONY_BOUNDARY:** The property is temporal safety semantics; sequence diagrams or temporal logic are optional implementations.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Timing, ordering, duration and transition semantics
- **LOSS_OR_HAZARD:** Loss during transient states or because control timing violates the safe envelope.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Timing, ordering, duration and transition semantics.
- **CONTROL_ACTION:** Specify temporal constraints, transition guards, timeouts, idempotence/repetition bounds and completion feedback.
- **REQUIRED_FEEDBACK:** Timestamped actions, transition state, completion, retries, timeout and causal order.
- **PROCESS_MODEL_ASSUMPTION:** Known timing budgets, transition states, clock/order assumptions and failure handling.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Controller/arbitrator can enforce ordering and block unsafe transitions.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** A synchronous local operation with atomic deterministic semantics may need only a direct timeout/completion check.
- **MATURE_FORM:** Apply temporal rigour where timing can change safety; use direct atomic checks where it cannot.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Timing, ordering, duration and transition semantics
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** A synchronous local operation with atomic deterministic semantics may need only a direct timeout/completion check.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Apply temporal rigour where timing can change safety; use direct atomic checks where it cannot.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S018, S049, S089, S100; critical/contrary: S038, S049.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Timing, ordering, duration and transition semantics, rather than only a proxy, component check or document status?
- When the trigger is present — Real-time, distributed, asynchronous, autonomous, start-up/shutdown and handoff operations. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Timestamped actions, transition state, completion, retries, timeout and causal order. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Controller/arbitrator can enforce ordering and block unsafe transitions.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: A synchronous local operation with atomic deterministic semantics may need only a direct timeout/completion check.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-012 — Interface assumptions and safety contracts

- **PROPERTY_ID:** ESS-012
- **PROPERTY_NAME:** Interface assumptions and safety contracts
- **LOSS_OR_HAZARD:** Loss from interface mismatch, hidden dependency, incompatible reuse or supplier boundary.
- **FAILURE_MODE:** An assumption changes or was never true, but downstream evidence remains apparently valid.
- **MATURE_FORM:** Safety-relevant assumptions are explicit, version-bound, validated and invalidated by change.
- **TRIGGER:** Reuse, supplier integration, distributed control, configuration change, multiple organisations or novel environment.
- **CHEAP_PATH:** A local isolated component with no safety-relevant interface can use a direct type/range check.
- **REQUIRED_PRECONDITIONS:** Stable interface identity, access to supplier evidence and ability to test cross-boundary behaviour.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Interface conformance, assumption validity, integration state, version and environment.
- **AUTHORITY_BOUNDARY:** An integrator must own end-to-end safety; suppliers need change-notification obligations.
- **CRITICISMS:** Formal contracts can omit human/physical context and create false completeness.
- **ANTI_CEREMONY_BOUNDARY:** The property is managed assumption/guarantee integrity; a particular ICD format is not required.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Interface assumptions and safety contracts
- **LOSS_OR_HAZARD:** Loss from interface mismatch, hidden dependency, incompatible reuse or supplier boundary.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Interface assumptions and safety contracts.
- **CONTROL_ACTION:** Make safety-relevant assumptions explicit, owned, testable and change-linked; validate at integration and operation.
- **REQUIRED_FEEDBACK:** Interface conformance, assumption validity, integration state, version and environment.
- **PROCESS_MODEL_ASSUMPTION:** Stable interface identity, access to supplier evidence and ability to test cross-boundary behaviour.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** An integrator must own end-to-end safety; suppliers need change-notification obligations.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** A local isolated component with no safety-relevant interface can use a direct type/range check.
- **MATURE_FORM:** Safety-relevant assumptions are explicit, version-bound, validated and invalidated by change.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Interface assumptions and safety contracts
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** A local isolated component with no safety-relevant interface can use a direct type/range check.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Safety-relevant assumptions are explicit, version-bound, validated and invalidated by change.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S029, S083, S090, S100; critical/contrary: S048, S109.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Interface assumptions and safety contracts, rather than only a proxy, component check or document status?
- When the trigger is present — Reuse, supplier integration, distributed control, configuration change, multiple organisations or novel environment. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Interface conformance, assumption validity, integration state, version and environment. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: An integrator must own end-to-end safety; suppliers need change-notification obligations.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: A local isolated component with no safety-relevant interface can use a direct type/range check.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-013 — Common-cause, common-mode and dependent-failure reasoning

- **PROPERTY_ID:** ESS-013
- **PROPERTY_NAME:** Common-cause, common-mode and dependent-failure reasoning
- **LOSS_OR_HAZARD:** Loss after multiple supposedly protective elements fail or misbehave together.
- **FAILURE_MODE:** A shared cause or dependency invalidates multiplication of individual reliabilities or barrier-count confidence.
- **MATURE_FORM:** Claim independence only after identifying shared causes and monitoring the assumptions that sustain it.
- **TRIGGER:** Redundant/high-integrity architectures, multi-version software, layered barriers and independent evidence claims.
- **CHEAP_PATH:** No detailed common-cause model is needed when there is only one simple reversible control and failure is directly detectable.
- **REQUIRED_PRECONDITIONS:** Architecture/dependency visibility and data or justified bounds for quantitative claims.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Shared-resource health, coincident failures, barrier independence, environment and evidence lineage.
- **AUTHORITY_BOUNDARY:** System authority can change architecture and reject nominal independence claims.
- **CRITICISMS:** Diversity can add faults and maintenance burden; common-cause probabilities are often data-poor.
- **ANTI_CEREMONY_BOUNDARY:** The property is dependence-aware reasoning; a specific common-cause worksheet is not required.
- **POSSIBLE_CONFLICTING_PROPERTY:** Added common-cause controls can increase complexity; see ESS-014 and rejected ESS-060.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Common-cause, common-mode and dependent-failure reasoning
- **LOSS_OR_HAZARD:** Loss after multiple supposedly protective elements fail or misbehave together.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Common-cause, common-mode and dependent-failure reasoning.
- **CONTROL_ACTION:** Map shared resources/assumptions and environmental causes; diversify where effective; monitor isolation and test common-cause scenarios.
- **REQUIRED_FEEDBACK:** Shared-resource health, coincident failures, barrier independence, environment and evidence lineage.
- **PROCESS_MODEL_ASSUMPTION:** Architecture/dependency visibility and data or justified bounds for quantitative claims.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** System authority can change architecture and reject nominal independence claims.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** No detailed common-cause model is needed when there is only one simple reversible control and failure is directly detectable.
- **MATURE_FORM:** Claim independence only after identifying shared causes and monitoring the assumptions that sustain it.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Common-cause, common-mode and dependent-failure reasoning
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** No detailed common-cause model is needed when there is only one simple reversible control and failure is directly detectable.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Claim independence only after identifying shared causes and monitoring the assumptions that sustain it.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S040, S041, S050, S051, S056, S087; critical/contrary: S050, S038.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Common-cause, common-mode and dependent-failure reasoning, rather than only a proxy, component check or document status?
- When the trigger is present — Redundant/high-integrity architectures, multi-version software, layered barriers and independent evidence claims. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Shared-resource health, coincident failures, barrier independence, environment and evidence lineage. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: System authority can change architecture and reject nominal independence claims.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: No detailed common-cause model is needed when there is only one simple reversible control and failure is directly detectable.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-014 — Redundancy with demonstrated independence, diversity and observability

- **PROPERTY_ID:** ESS-014
- **PROPERTY_NAME:** Redundancy with demonstrated independence, diversity and observability
- **LOSS_OR_HAZARD:** Loss from failure of a critical function or barrier with no effective alternative.
- **FAILURE_MODE:** Redundant channels share a cause, disagree without resolution, mask latent failure or increase complexity beyond operational control.
- **MATURE_FORM:** Use the simplest architecture that meets the loss constraint, with explicit dependence and degraded-mode semantics.
- **TRIGGER:** High-consequence single-point failures where alternate means are feasible and do not create greater interaction risk.
- **CHEAP_PATH:** Do not add redundancy to low-consequence reversible functions when a simpler reliable design and direct detection is safer.
- **REQUIRED_PRECONDITIONS:** Independent failure modes, bounded interaction complexity, monitoring and maintainability.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Channel health, disagreement, latent failures, common resources and degraded capability.
- **AUTHORITY_BOUNDARY:** Architecture owner must control shared resources and resolve channel disagreement.
- **CRITICISMS:** More redundancy is not monotonically safer; software diversity experiments reject naive independence.
- **ANTI_CEREMONY_BOUNDARY:** The property is effective alternate control; a fixed number of channels is not general.
- **POSSIBLE_CONFLICTING_PROPERTY:** Architectural simplicity may outperform nominal redundancy when common-mode complexity dominates.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Redundancy with demonstrated independence, diversity and observability
- **LOSS_OR_HAZARD:** Loss from failure of a critical function or barrier with no effective alternative.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Redundancy with demonstrated independence, diversity and observability.
- **CONTROL_ACTION:** Use redundancy only with justified independence/diversity, disagreement handling, health monitoring, maintenance and safe voting/arbitration.
- **REQUIRED_FEEDBACK:** Channel health, disagreement, latent failures, common resources and degraded capability.
- **PROCESS_MODEL_ASSUMPTION:** Independent failure modes, bounded interaction complexity, monitoring and maintainability.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Architecture owner must control shared resources and resolve channel disagreement.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Do not add redundancy to low-consequence reversible functions when a simpler reliable design and direct detection is safer.
- **MATURE_FORM:** Use the simplest architecture that meets the loss constraint, with explicit dependence and degraded-mode semantics.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Redundancy with demonstrated independence, diversity and observability
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Do not add redundancy to low-consequence reversible functions when a simpler reliable design and direct detection is safer.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Use the simplest architecture that meets the loss constraint, with explicit dependence and degraded-mode semantics.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S050, S051, S056, S057, S067; critical/contrary: S050, S087, S089.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Redundancy with demonstrated independence, diversity and observability, rather than only a proxy, component check or document status?
- When the trigger is present — High-consequence single-point failures where alternate means are feasible and do not create greater interaction risk. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Channel health, disagreement, latent failures, common resources and degraded capability. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Architecture owner must control shared resources and resolve channel disagreement.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Do not add redundancy to low-consequence reversible functions when a simpler reliable design and direct detection is safer.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-015 — Scenario and causal-path coverage through complementary methods

- **PROPERTY_ID:** ESS-015
- **PROPERTY_NAME:** Scenario and causal-path coverage through complementary methods
- **LOSS_OR_HAZARD:** Loss through a failure, interaction, environmental, organisational or recovery path outside the selected technique’s representation.
- **FAILURE_MODE:** Method scope determines what can be found, but scope is implicit or unchallenged.
- **MATURE_FORM:** Use the smallest complementary portfolio that covers the credible causal classes and changes a live decision.
- **TRIGGER:** Complex/high-consequence systems with heterogeneous causal mechanisms or deep uncertainty.
- **CHEAP_PATH:** Use one cheap deterministic analysis when it exhausts the relevant causal question; do not stack methods for prestige.
- **REQUIRED_PRECONDITIONS:** Explicit method assumptions, shared system model, reconciliation of conflicting results and action consumers.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Coverage by causal class, unresolved contradictions, new evidence and decision changes attributable to each method.
- **AUTHORITY_BOUNDARY:** Safety lead can tailor methods and reject duplicative analysis.
- **CRITICISMS:** Comparative method studies are limited; “more methods” can consume experts and dilute attention.
- **ANTI_CEREMONY_BOUNDARY:** The property is representation coverage; named-method maximalism is ceremony.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Scenario and causal-path coverage through complementary methods
- **LOSS_OR_HAZARD:** Loss through a failure, interaction, environmental, organisational or recovery path outside the selected technique’s representation.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Scenario and causal-path coverage through complementary methods.
- **CONTROL_ACTION:** Choose methods by hazard class; cross-check top-down, bottom-up, deviation, interaction and operational scenarios; stop when marginal decision value is low.
- **REQUIRED_FEEDBACK:** Coverage by causal class, unresolved contradictions, new evidence and decision changes attributable to each method.
- **PROCESS_MODEL_ASSUMPTION:** Explicit method assumptions, shared system model, reconciliation of conflicting results and action consumers.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Safety lead can tailor methods and reject duplicative analysis.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Use one cheap deterministic analysis when it exhausts the relevant causal question; do not stack methods for prestige.
- **MATURE_FORM:** Use the smallest complementary portfolio that covers the credible causal classes and changes a live decision.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Scenario and causal-path coverage through complementary methods
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Use one cheap deterministic analysis when it exhausts the relevant causal question; do not stack methods for prestige.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Use the smallest complementary portfolio that covers the credible causal classes and changes a live decision.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_WITHIN_REPRESENTED_CLASS — technique semantics are established; completeness outside its representation is not.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** CONTEXT_DEPENDENT — transfer requires matching the technique to the causal/hazard class.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S014, S016, S020, S094, S096, S098; critical/contrary: S019, S038, S109.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Scenario and causal-path coverage through complementary methods, rather than only a proxy, component check or document status?
- When the trigger is present — Complex/high-consequence systems with heterogeneous causal mechanisms or deep uncertainty. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Coverage by causal class, unresolved contradictions, new evidence and decision changes attributable to each method. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Safety lead can tailor methods and reject duplicative analysis.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Use one cheap deterministic analysis when it exhausts the relevant causal question; do not stack methods for prestige.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-016 — Human–automation coordination and mode awareness

- **PROPERTY_ID:** ESS-016
- **PROPERTY_NAME:** Human–automation coordination and mode awareness
- **LOSS_OR_HAZARD:** Loss from mode confusion, automation surprise, out-of-the-loop performance, workload or ambiguous handoff.
- **FAILURE_MODE:** Control transfers without comprehension, warning or adequate time; automation masks or creates unsafe state.
- **MATURE_FORM:** Allocate work and authority around realistic human/automation capabilities, with observable modes and verified handoffs.
- **TRIGGER:** Automated/highly interactive systems, degraded modes and safety-critical handoffs.
- **CHEAP_PATH:** For a transparent local tool with direct reversible effect, use simple status/confirmation rather than a full human-factors programme.
- **REQUIRED_PRECONDITIONS:** Representative users, realistic scenarios and authority to change automation/interface design.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Mode/state, automation intent, limits, alert salience, workload and handoff completion.
- **AUTHORITY_BOUNDARY:** Clear authority for takeover, inhibit, escalation and refusal; operator responsibility must match information/control.
- **CRITICISMS:** Human performance is variable; interface validation in tests may not cover rare operational combinations.
- **ANTI_CEREMONY_BOUNDARY:** The property is coordinated control; a generic “human in the loop” claim is not evidence.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Human–automation coordination and mode awareness
- **LOSS_OR_HAZARD:** Loss from mode confusion, automation surprise, out-of-the-loop performance, workload or ambiguous handoff.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Human–automation coordination and mode awareness.
- **CONTROL_ACTION:** Analyse joint cognitive work, critical tasks, mode/state visibility, workload, takeover time and fallback authority.
- **REQUIRED_FEEDBACK:** Mode/state, automation intent, limits, alert salience, workload and handoff completion.
- **PROCESS_MODEL_ASSUMPTION:** Representative users, realistic scenarios and authority to change automation/interface design.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Clear authority for takeover, inhibit, escalation and refusal; operator responsibility must match information/control.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** For a transparent local tool with direct reversible effect, use simple status/confirmation rather than a full human-factors programme.
- **MATURE_FORM:** Allocate work and authority around realistic human/automation capabilities, with observable modes and verified handoffs.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Human–automation coordination and mode awareness
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** For a transparent local tool with direct reversible effect, use simple status/confirmation rather than a full human-factors programme.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Allocate work and authority around realistic human/automation capabilities, with observable modes and verified handoffs.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** MODERATE — mechanism is coherent but depends on model scope and assumptions.
- **ACCIDENT_CASE_STRENGTH:** HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S063, S064, S088, S089, S106; critical/contrary: S074, S109.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Human–automation coordination and mode awareness, rather than only a proxy, component check or document status?
- When the trigger is present — Automated/highly interactive systems, degraded modes and safety-critical handoffs. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Mode/state, automation intent, limits, alert salience, workload and handoff completion. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Clear authority for takeover, inhibit, escalation and refusal; operator responsibility must match information/control.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: For a transparent local tool with direct reversible effect, use simple status/confirmation rather than a full human-factors programme.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-017 — Authority, responsibility, stop and handoff clarity

- **PROPERTY_ID:** ESS-017
- **PROPERTY_NAME:** Authority, responsibility, stop and handoff clarity
- **LOSS_OR_HAZARD:** Loss because no actor can or will enforce the safety constraint or because handoff leaves a control gap.
- **FAILURE_MODE:** Unsafe action proceeds under schedule pressure, ambiguous ownership or ineffective escalation.
- **MATURE_FORM:** Every consequential constraint has an actor with information, competence and authority to enforce it; handoffs transfer state as well as responsibility.
- **TRIGGER:** Multi-team, supplier, regulator, autonomous/human and emergency operations; any high-consequence exception.
- **CHEAP_PATH:** A single-person low-consequence local task needs only clear ownership and undo capability.
- **REQUIRED_PRECONDITIONS:** Competence, accessible information, non-retaliatory escalation and feasible control options.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Open decisions, escalations, handoff acknowledgement, stop response and unresolved hazards.
- **AUTHORITY_BOUNDARY:** Authority must be real, resourced and insulated enough to counter production pressure; acceptance authority must be named.
- **CRITICISMS:** Rigid authority can suppress local adaptation; independence can slow feedback and fragment ownership.
- **ANTI_CEREMONY_BOUNDARY:** The property is effective authority; titles, boards and RACI charts are optional artefacts.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Authority, responsibility, stop and handoff clarity
- **LOSS_OR_HAZARD:** Loss because no actor can or will enforce the safety constraint or because handoff leaves a control gap.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Authority, responsibility, stop and handoff clarity.
- **CONTROL_ACTION:** Define decision rights, stop authority, escalation, handoff state and independent acceptance for consequential exceptions.
- **REQUIRED_FEEDBACK:** Open decisions, escalations, handoff acknowledgement, stop response and unresolved hazards.
- **PROCESS_MODEL_ASSUMPTION:** Competence, accessible information, non-retaliatory escalation and feasible control options.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Authority must be real, resourced and insulated enough to counter production pressure; acceptance authority must be named.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** A single-person low-consequence local task needs only clear ownership and undo capability.
- **MATURE_FORM:** Every consequential constraint has an actor with information, competence and authority to enforce it; handoffs transfer state as well as responsibility.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Authority, responsibility, stop and handoff clarity
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** A single-person low-consequence local task needs only clear ownership and undo capability.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Every consequential constraint has an actor with information, competence and authority to enforce it; handoffs transfer state as well as responsibility.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** MODERATE — mechanism is coherent but depends on model scope and assumptions.
- **ACCIDENT_CASE_STRENGTH:** HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S018, S067, S081, S082, S087, S112; critical/contrary: S048, S066.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Authority, responsibility, stop and handoff clarity, rather than only a proxy, component check or document status?
- When the trigger is present — Multi-team, supplier, regulator, autonomous/human and emergency operations; any high-consequence exception. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Open decisions, escalations, handoff acknowledgement, stop response and unresolved hazards. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Authority must be real, resourced and insulated enough to counter production pressure; acceptance authority must be named.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: A single-person low-consequence local task needs only clear ownership and undo capability.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-018 — Traceability from hazards and constraints to implementation and verification

- **PROPERTY_ID:** ESS-018
- **PROPERTY_NAME:** Traceability from hazards and constraints to implementation and verification
- **LOSS_OR_HAZARD:** Loss because a necessary constraint is absent or its implementation/evidence does not match the claim.
- **FAILURE_MODE:** Documentation indicates compliance while the actual control path is incomplete.
- **MATURE_FORM:** Maintain only decision-relevant traceability sufficient to show current hazard-to-control-to-evidence closure.
- **TRIGGER:** Consequential controls, regulated development and systems with many suppliers/changes.
- **CHEAP_PATH:** For a tiny local deterministic change, one direct link from hazard/invariant to test result may be sufficient.
- **REQUIRED_PRECONDITIONS:** Stable identifiers, configuration management and semantic—not merely hyperlink—traceability.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Current configuration, verification result, unresolved links, waivers and operational monitoring.
- **AUTHORITY_BOUNDARY:** Owners must be able to resolve orphaned requirements/evidence and block release where links fail.
- **CRITICISMS:** Traceability is not proof; linked requirements can all be wrong or derived from one flawed assumption.
- **ANTI_CEREMONY_BOUNDARY:** The property is semantic current linkage; a traceability matrix format is not required.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Traceability from hazards and constraints to implementation and verification
- **LOSS_OR_HAZARD:** Loss because a necessary constraint is absent or its implementation/evidence does not match the claim.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Traceability from hazards and constraints to implementation and verification.
- **CONTROL_ACTION:** Maintain bidirectional, configuration-bound links and test whether every claim has a control and every control has a hazard rationale.
- **REQUIRED_FEEDBACK:** Current configuration, verification result, unresolved links, waivers and operational monitoring.
- **PROCESS_MODEL_ASSUMPTION:** Stable identifiers, configuration management and semantic—not merely hyperlink—traceability.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Owners must be able to resolve orphaned requirements/evidence and block release where links fail.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** For a tiny local deterministic change, one direct link from hazard/invariant to test result may be sufficient.
- **MATURE_FORM:** Maintain only decision-relevant traceability sufficient to show current hazard-to-control-to-evidence closure.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Traceability from hazards and constraints to implementation and verification
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** For a tiny local deterministic change, one direct link from hazard/invariant to test result may be sufficient.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Maintain only decision-relevant traceability sufficient to show current hazard-to-control-to-evidence closure.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S029, S031, S042, S047, S100; critical/contrary: S048, S049.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Traceability from hazards and constraints to implementation and verification, rather than only a proxy, component check or document status?
- When the trigger is present — Consequential controls, regulated development and systems with many suppliers/changes. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Current configuration, verification result, unresolved links, waivers and operational monitoring. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Owners must be able to resolve orphaned requirements/evidence and block release where links fail.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: For a tiny local deterministic change, one direct link from hazard/invariant to test result may be sufficient.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-019 — Uncertainty-aware risk representation rather than score-only governance

- **PROPERTY_ID:** ESS-019
- **PROPERTY_NAME:** Uncertainty-aware risk representation rather than score-only governance
- **LOSS_OR_HAZARD:** Loss because uncertain catastrophic risk was underestimated, misranked or threshold-gamed.
- **FAILURE_MODE:** Sparse data, dependence, model error and category choices produce false precision or ranking inversion.
- **MATURE_FORM:** Choose the least elaborate representation that preserves decision-relevant consequence and uncertainty; never call the score the risk.
- **TRIGGER:** Risk comparisons, prioritisation and residual-risk decisions where uncertainty can change action.
- **CHEAP_PATH:** If a deterministic constraint settles the decision, do not estimate probability merely to fill a matrix.
- **REQUIRED_PRECONDITIONS:** Defined decision, data provenance, calibrated model and authority capable of reasoning under uncertainty.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Data quality, model sensitivity, uncertainty bounds, near misses and assumption validity.
- **AUTHORITY_BOUNDARY:** Risk authority must be able to reject unsupported precision and choose precaution/learning/monitoring.
- **CRITICISMS:** Quantitative models can also mislead; deep uncertainty may resist probability assignment.
- **ANTI_CEREMONY_BOUNDARY:** The property is explicit uncertainty and decision linkage; coloured matrices are optional and often harmful.
- **POSSIBLE_CONFLICTING_PROPERTY:** Precaution under deep uncertainty can conflict with quantitative comparability and service availability.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Uncertainty-aware risk representation rather than score-only governance
- **LOSS_OR_HAZARD:** Loss because uncertain catastrophic risk was underestimated, misranked or threshold-gamed.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Uncertainty-aware risk representation rather than score-only governance.
- **CONTROL_ACTION:** Use scores only as transparent prompts; retain consequence and uncertainty separately; quantify where data/model warrant and sensitivity-test decisions.
- **REQUIRED_FEEDBACK:** Data quality, model sensitivity, uncertainty bounds, near misses and assumption validity.
- **PROCESS_MODEL_ASSUMPTION:** Defined decision, data provenance, calibrated model and authority capable of reasoning under uncertainty.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Risk authority must be able to reject unsupported precision and choose precaution/learning/monitoring.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** If a deterministic constraint settles the decision, do not estimate probability merely to fill a matrix.
- **MATURE_FORM:** Choose the least elaborate representation that preserves decision-relevant consequence and uncertainty; never call the score the risk.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Uncertainty-aware risk representation rather than score-only governance
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** If a deterministic constraint settles the decision, do not estimate probability merely to fill a matrix.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Choose the least elaborate representation that preserves decision-relevant consequence and uncertainty; never call the score the risk.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S034, S036, S037, S038, S039, S040; critical/contrary: S036, S037, S038.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Uncertainty-aware risk representation rather than score-only governance, rather than only a proxy, component check or document status?
- When the trigger is present — Risk comparisons, prioritisation and residual-risk decisions where uncertainty can change action. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Data quality, model sensitivity, uncertainty bounds, near misses and assumption validity. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Risk authority must be able to reject unsupported precision and choose precaution/learning/monitoring.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: If a deterministic constraint settles the decision, do not estimate probability merely to fill a matrix.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-020 — Consequence, reversibility, coupling and observability proportionality

- **PROPERTY_ID:** ESS-020
- **PROPERTY_NAME:** Consequence, reversibility, coupling and observability proportionality
- **LOSS_OR_HAZARD:** Either under-control of high-consequence work or over-control that creates delay, workaround and service loss.
- **FAILURE_MODE:** Process depth follows labels or bureaucracy rather than actual propagation, reversibility and knowledge conditions.
- **MATURE_FORM:** Control strength rises with credible loss and irreversibility/coupling/latency, while deterministic low-risk work remains cheap.
- **TRIGGER:** All work, with greatest value where harm is severe, irreversible, coupled, latent or hard to test.
- **CHEAP_PATH:** Local, cheap, reversible, immediately observable work with an authoritative discriminator uses a minimal check and normal engineering review.
- **REQUIRED_PRECONDITIONS:** Credible consequence model, change classification and authority to tailor both upward and downward.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Actual propagation/recovery performance, false-stop cost, near misses and whether controls change decisions.
- **AUTHORITY_BOUNDARY:** A competent risk/safety owner must be able to demand more or less control and document the basis.
- **CRITICISMS:** Proportionality is not permission to ignore uncertain catastrophic hazards; ALARP interpretation is contested.
- **ANTI_CEREMONY_BOUNDARY:** The property is justified tailoring; classification boards and matrices are implementations, not ends.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-031 independent assurance demands more control while ESS-046 preserves a cheap path.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Consequence, reversibility, coupling and observability proportionality
- **LOSS_OR_HAZARD:** Either under-control of high-consequence work or over-control that creates delay, workaround and service loss.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Consequence, reversibility, coupling and observability proportionality.
- **CONTROL_ACTION:** Assess consequence, reversibility, coupling, observability latency, recovery difficulty and uncertainty; select control strength and cheap path accordingly.
- **REQUIRED_FEEDBACK:** Actual propagation/recovery performance, false-stop cost, near misses and whether controls change decisions.
- **PROCESS_MODEL_ASSUMPTION:** Credible consequence model, change classification and authority to tailor both upward and downward.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** A competent risk/safety owner must be able to demand more or less control and document the basis.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Local, cheap, reversible, immediately observable work with an authoritative discriminator uses a minimal check and normal engineering review.
- **MATURE_FORM:** Control strength rises with credible loss and irreversibility/coupling/latency, while deterministic low-risk work remains cheap.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Consequence, reversibility, coupling and observability proportionality
- **CONSEQUENCE_DIMENSION:** Magnitude/distribution of credible harm and public/mission exposure
- **REVERSIBILITY_DIMENSION:** Whether change or loss can be rolled back before harm and at what cost
- **COUPLING_DIMENSION:** Propagation across technical, organisational and environmental boundaries
- **OBSERVABILITY_LATENCY:** Time between unsafe condition, reliable detection and effective response
- **RECOVERY_DIFFICULTY:** Feasibility and burden of containment, restoration and compensation
- **CONTROL_STRENGTH_RELATION:** Increase rigour nonlinearly when severe harm combines with irreversibility, tight coupling, delayed detection or scarce empirical test
- **CHEAP_PATH:** One direct authoritative check for local reversible work; escalate only on failed assumptions or widened consequence
- **OVER_CONTROL_FAILURE:** Maximal controls can cause unavailable safety-critical service, delay, alarm fatigue and procedural bypass
- **MATURE_FORM:** Multidimensional tailoring with explicit escalation and de-escalation rationale; not a universal risk score


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S014, S029, S035, S052, S053, S095, S104; critical/contrary: S036, S038, S113.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Consequence, reversibility, coupling and observability proportionality, rather than only a proxy, component check or document status?
- When the trigger is present — All work, with greatest value where harm is severe, irreversible, coupled, latent or hard to test. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Actual propagation/recovery performance, false-stop cost, near misses and whether controls change decisions. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: A competent risk/safety owner must be able to demand more or less control and document the basis.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Local, cheap, reversible, immediately observable work with an authoritative discriminator uses a minimal check and normal engineering review.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-021 — Explicit residual-risk acceptance by competent authority

- **PROPERTY_ID:** ESS-021
- **PROPERTY_NAME:** Explicit residual-risk acceptance by competent authority
- **LOSS_OR_HAZARD:** Unacceptable loss from a known but incompletely controlled hazard whose ownership and acceptance basis are obscure.
- **FAILURE_MODE:** Risk is silently transferred, severity or uncertainty is downplayed, or acceptance persists after its assumptions expire.
- **MATURE_FORM:** A current, named and revisable decision by a competent authority over a residual hazard whose controls, uncertainty, exposure and alternatives are visible.
- **TRIGGER:** Consequential residual hazards that cannot presently be eliminated or further reduced at proportionate cost.
- **CHEAP_PATH:** No separate acceptance ritual is needed when an authoritative deterministic check proves the hazard absent or a trivial reversible effect remains within ordinary authority.
- **REQUIRED_PRECONDITIONS:** Current hazard/control evidence, explicit alternatives and uncertainty, identified exposure and a defined acceptance policy.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Barrier health, exposure, assumptions, incidents, time/configuration limits and effectiveness of compensating controls.
- **AUTHORITY_BOUNDARY:** The acceptor must have legal/organisational mandate, relevant competence and authority over resources or operational restrictions.
- **CRITICISMS:** Formal acceptance cannot make an intolerable risk acceptable and may exclude affected publics or workers from the decision.
- **ANTI_CEREMONY_BOUNDARY:** A signed form is not the property; accountable and evidence-bounded acceptance is.
- **POSSIBLE_CONFLICTING_PROPERTY:** Risk acceptance can conflict with categorical unacceptable-loss constraints in ESS-001/003.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Explicit residual-risk acceptance by competent authority
- **LOSS_OR_HAZARD:** Unacceptable loss from a known but incompletely controlled hazard whose ownership and acceptance basis are obscure.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Explicit residual-risk acceptance by competent authority.
- **CONTROL_ACTION:** State the residual hazard and uncertainty, identify the exposed parties and control status, obtain time/configuration-bounded acceptance and reopen on change or evidence.
- **REQUIRED_FEEDBACK:** Barrier health, exposure, assumptions, incidents, time/configuration limits and effectiveness of compensating controls.
- **PROCESS_MODEL_ASSUMPTION:** Current hazard/control evidence, explicit alternatives and uncertainty, identified exposure and a defined acceptance policy.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** The acceptor must have legal/organisational mandate, relevant competence and authority over resources or operational restrictions.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** No separate acceptance ritual is needed when an authoritative deterministic check proves the hazard absent or a trivial reversible effect remains within ordinary authority.
- **MATURE_FORM:** A current, named and revisable decision by a competent authority over a residual hazard whose controls, uncertainty, exposure and alternatives are visible.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Explicit residual-risk acceptance by competent authority
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** No separate acceptance ritual is needed when an authoritative deterministic check proves the hazard absent or a trivial reversible effect remains within ordinary authority.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** A current, named and revisable decision by a competent authority over a residual hazard whose controls, uncertainty, exposure and alternatives are visible.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S027, S034, S042; critical/contrary: S036, S038, S113.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Explicit residual-risk acceptance by competent authority, rather than only a proxy, component check or document status?
- When the trigger is present — Consequential residual hazards that cannot presently be eliminated or further reduced at proportionate cost. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Barrier health, exposure, assumptions, incidents, time/configuration limits and effectiveness of compensating controls. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: The acceptor must have legal/organisational mandate, relevant competence and authority over resources or operational restrictions.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: No separate acceptance ritual is needed when an authoritative deterministic check proves the hazard absent or a trivial reversible effect remains within ordinary authority.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-022 — Proportionate risk reduction under ALARP or SFAIRP reasoning

- **PROPERTY_ID:** ESS-022
- **PROPERTY_NAME:** Proportionate risk reduction under ALARP or SFAIRP reasoning
- **LOSS_OR_HAZARD:** Preventable serious harm, or secondary harm and mission loss caused by indiscriminate over-control.
- **FAILURE_MODE:** Cost, sacrifice, benefit and uncertainty are compared opaquely; gross disproportionality is treated as a formula; good practice becomes stale.
- **MATURE_FORM:** Use proportionality as disciplined justification for control sufficiency, not as a numerical escape hatch or universal legal export.
- **TRIGGER:** Material occupational/process/public hazards where feasible alternatives and control costs matter.
- **CHEAP_PATH:** Where a binding deterministic rule or clearly trivial reversible hazard settles the decision, use it directly rather than manufacture a cost-benefit case.
- **REQUIRED_PRECONDITIONS:** Legally appropriate jurisdiction, credible consequence evidence, feasible options and competent judgement.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Control effectiveness, changing good practice, exposure, sacrifice estimates and evidence that adopted controls remain operative.
- **AUTHORITY_BOUNDARY:** The duty holder retains the burden to show sufficient reduction; a calculator or consultant cannot own the legal judgement.
- **CRITICISMS:** ALARP is jurisdiction-specific, ethically contested and frequently misunderstood; it is not a universal optimisation formula.
- **ANTI_CEREMONY_BOUNDARY:** The transferable property is reasoned proportionality; the exact legal test and paperwork are domain-specific.
- **POSSIBLE_CONFLICTING_PROPERTY:** Practicability reasoning may conflict with rights-based or categorical prohibitions.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Proportionate risk reduction under ALARP or SFAIRP reasoning
- **LOSS_OR_HAZARD:** Preventable serious harm, or secondary harm and mission loss caused by indiscriminate over-control.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Proportionate risk reduction under ALARP or SFAIRP reasoning.
- **CONTROL_ACTION:** Identify feasible controls, establish good practice, examine remaining risk and sacrifice transparently, and require stronger justification as consequence rises.
- **REQUIRED_FEEDBACK:** Control effectiveness, changing good practice, exposure, sacrifice estimates and evidence that adopted controls remain operative.
- **PROCESS_MODEL_ASSUMPTION:** Legally appropriate jurisdiction, credible consequence evidence, feasible options and competent judgement.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** The duty holder retains the burden to show sufficient reduction; a calculator or consultant cannot own the legal judgement.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Where a binding deterministic rule or clearly trivial reversible hazard settles the decision, use it directly rather than manufacture a cost-benefit case.
- **MATURE_FORM:** Use proportionality as disciplined justification for control sufficiency, not as a numerical escape hatch or universal legal export.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Proportionate risk reduction under ALARP or SFAIRP reasoning
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Where a binding deterministic rule or clearly trivial reversible hazard settles the decision, use it directly rather than manufacture a cost-benefit case.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Use proportionality as disciplined justification for control sufficiency, not as a numerical escape hatch or universal legal export.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S034, S035, S113; critical/contrary: S036, S038, S113.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Proportionate risk reduction under ALARP or SFAIRP reasoning, rather than only a proxy, component check or document status?
- When the trigger is present — Material occupational/process/public hazards where feasible alternatives and control costs matter. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Control effectiveness, changing good practice, exposure, sacrifice estimates and evidence that adopted controls remain operative. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: The duty holder retains the burden to show sufficient reduction; a calculator or consultant cannot own the legal judgement.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Where a binding deterministic rule or clearly trivial reversible hazard settles the decision, use it directly rather than manufacture a cost-benefit case.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-023 — Defence in depth with barrier independence and degradation monitoring

- **PROPERTY_ID:** ESS-023
- **PROPERTY_NAME:** Defence in depth with barrier independence and degradation monitoring
- **LOSS_OR_HAZARD:** Catastrophic release, loss of critical function or public harm after one failed or bypassed layer.
- **FAILURE_MODE:** Layers share power, sensors, software, maintenance, environment or organisational assumptions, or degrade unnoticed.
- **MATURE_FORM:** A hazard-specific barrier architecture whose layers have distinct functions, credible independence and live health evidence.
- **TRIGGER:** Severe, irreversible hazards for which no single control can be shown sufficiently dependable.
- **CHEAP_PATH:** Do not add nominal layers to a trivial reversible task or where one simple physically enforced elimination removes the hazard.
- **REQUIRED_PRECONDITIONS:** Barrier functions and dependencies are explicit; surveillance and maintenance can detect degradation; emergency arrangements exist.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Barrier demand and success, independence, common utilities, bypass status, test coverage and degraded configurations.
- **AUTHORITY_BOUNDARY:** Owners must be able to maintain, test, isolate and restore layers and to restrict operation when defence is impaired.
- **CRITICISMS:** Fukushima and multiversion evidence show that apparent multiplicity does not establish effective independence.
- **ANTI_CEREMONY_BOUNDARY:** A bow-tie or layer diagram is optional; demonstrably effective, independent and monitored barriers are the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** Additional layers can conflict with simplicity and introduce common-mode complexity.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Defence in depth with barrier independence and degradation monitoring
- **LOSS_OR_HAZARD:** Catastrophic release, loss of critical function or public harm after one failed or bypassed layer.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Defence in depth with barrier independence and degradation monitoring.
- **CONTROL_ACTION:** Allocate distinct barrier purposes, analyse common cause and dependencies, monitor availability and preserve escalation/mitigation when prevention fails.
- **REQUIRED_FEEDBACK:** Barrier demand and success, independence, common utilities, bypass status, test coverage and degraded configurations.
- **PROCESS_MODEL_ASSUMPTION:** Barrier functions and dependencies are explicit; surveillance and maintenance can detect degradation; emergency arrangements exist.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Owners must be able to maintain, test, isolate and restore layers and to restrict operation when defence is impaired.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Do not add nominal layers to a trivial reversible task or where one simple physically enforced elimination removes the hazard.
- **MATURE_FORM:** A hazard-specific barrier architecture whose layers have distinct functions, credible independence and live health evidence.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Defence in depth with barrier independence and degradation monitoring
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Do not add nominal layers to a trivial reversible task or where one simple physically enforced elimination removes the hazard.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** A hazard-specific barrier architecture whose layers have distinct functions, credible independence and live health evidence.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S056, S057, S087, S103, S104; critical/contrary: S050, S087.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Defence in depth with barrier independence and degradation monitoring, rather than only a proxy, component check or document status?
- When the trigger is present — Severe, irreversible hazards for which no single control can be shown sufficiently dependable. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Barrier demand and success, independence, common utilities, bypass status, test coverage and degraded configurations. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Owners must be able to maintain, test, isolate and restore layers and to restrict operation when defence is impaired.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Do not add nominal layers to a trivial reversible task or where one simple physically enforced elimination removes the hazard.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-024 — Safety-integrity and development-assurance rigour tied to safety functions

- **PROPERTY_ID:** ESS-024
- **PROPERTY_NAME:** Safety-integrity and development-assurance rigour tied to safety functions
- **LOSS_OR_HAZARD:** Loss because a critical safety function lacks commensurate integrity, or because a process label masks unsafe interactions outside its scope.
- **FAILURE_MODE:** Misallocation, systematic defects, independence assumptions, “SIL washing” and conflating process compliance with achieved reliability.
- **MATURE_FORM:** Use graded integrity objectives as one hazard-derived assurance mechanism, never as a numerical certificate of total system safety.
- **TRIGGER:** Safety-related E/E/PE, airborne software/hardware and automotive functions whose failure conditions justify graded assurance.
- **CHEAP_PATH:** Do not assign a high assurance level to low-consequence code or use the classification where a direct deterministic test fully settles a local reversible change.
- **REQUIRED_PRECONDITIONS:** Valid hazard classification, allocated safety function, domain applicability and evidence that architecture and verification objectives are met.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Function demand/success, diagnostic coverage, systematic-defect controls, requirement/verification coverage and configuration identity.
- **AUTHORITY_BOUNDARY:** Certification/design authorities must control classification and independence; suppliers must disclose relevant development evidence.
- **CRITICISMS:** Standards authority is strong but comparative evidence for exact level/process prescriptions is limited; SOTIF exists because malfunction-only scope is incomplete.
- **ANTI_CEREMONY_BOUNDARY:** The general property is consequence-linked rigour; SIL, ASIL and DAL taxonomies are domain artefacts.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Safety-integrity and development-assurance rigour tied to safety functions
- **LOSS_OR_HAZARD:** Loss because a critical safety function lacks commensurate integrity, or because a process label masks unsafe interactions outside its scope.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Safety-integrity and development-assurance rigour tied to safety functions.
- **CONTROL_ACTION:** Derive integrity/assurance needs from hazards and functions; meet domain architecture and process objectives; verify actual function and complement with interaction analysis.
- **REQUIRED_FEEDBACK:** Function demand/success, diagnostic coverage, systematic-defect controls, requirement/verification coverage and configuration identity.
- **PROCESS_MODEL_ASSUMPTION:** Valid hazard classification, allocated safety function, domain applicability and evidence that architecture and verification objectives are met.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Certification/design authorities must control classification and independence; suppliers must disclose relevant development evidence.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Do not assign a high assurance level to low-consequence code or use the classification where a direct deterministic test fully settles a local reversible change.
- **MATURE_FORM:** Use graded integrity objectives as one hazard-derived assurance mechanism, never as a numerical certificate of total system safety.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Safety-integrity and development-assurance rigour tied to safety functions
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Do not assign a high assurance level to low-consequence code or use the classification where a direct deterministic test fully settles a local reversible change.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Use graded integrity objectives as one hazard-derived assurance mechanism, never as a numerical certificate of total system safety.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S021, S022, S023, S024, S029, S031, S032; critical/contrary: S025, S036, S050.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Safety-integrity and development-assurance rigour tied to safety functions, rather than only a proxy, component check or document status?
- When the trigger is present — Safety-related E/E/PE, airborne software/hardware and automotive functions whose failure conditions justify graded assurance. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Function demand/success, diagnostic coverage, systematic-defect controls, requirement/verification coverage and configuration identity. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Certification/design authorities must control classification and independence; suppliers must disclose relevant development evidence.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Do not assign a high assurance level to low-consequence code or use the classification where a direct deterministic test fully settles a local reversible change.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-025 — Informational independence and diversity of assurance evidence

- **PROPERTY_ID:** ESS-025
- **PROPERTY_NAME:** Informational independence and diversity of assurance evidence
- **LOSS_OR_HAZARD:** Unsafe acceptance caused by correlated evidence error, common specification defects or organisational confirmation bias.
- **FAILURE_MODE:** Nominally separate teams share sources, tools, incentives, training, data or process models and reproduce the same mistake.
- **MATURE_FORM:** Require independently informative evidence in proportion to consequence and explicitly disclose shared assumptions and sources.
- **TRIGGER:** High-consequence claims whose error cannot be cheaply discovered after deployment.
- **CHEAP_PATH:** One direct authoritative discriminator suffices when it conclusively decides a local reversible claim; reviewer multiplication adds no information.
- **REQUIRED_PRECONDITIONS:** Evidence methods have explicit failure modes and provenance; independent assessors have access, competence and challenge authority.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Disagreements, common inputs, oracle diversity, defect yield, challenge closure and configuration coverage.
- **AUTHORITY_BOUNDARY:** The independent function needs organisational freedom and information access, but informational independence must be assessed separately.
- **CRITICISMS:** Experimental multiversion evidence directly undermines naive independence assumptions; independence can also impede fast integrated learning.
- **ANTI_CEREMONY_BOUNDARY:** A separate reviewer or document is not automatically independent evidence.
- **POSSIBLE_CONFLICTING_PROPERTY:** Organisational separation can conflict with rapid integrated feedback.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Informational independence and diversity of assurance evidence
- **LOSS_OR_HAZARD:** Unsafe acceptance caused by correlated evidence error, common specification defects or organisational confirmation bias.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Informational independence and diversity of assurance evidence.
- **CONTROL_ACTION:** Map evidence provenance and dependence; combine analytic, test, operational and independent challenge where each can fail differently.
- **REQUIRED_FEEDBACK:** Disagreements, common inputs, oracle diversity, defect yield, challenge closure and configuration coverage.
- **PROCESS_MODEL_ASSUMPTION:** Evidence methods have explicit failure modes and provenance; independent assessors have access, competence and challenge authority.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** The independent function needs organisational freedom and information access, but informational independence must be assessed separately.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** One direct authoritative discriminator suffices when it conclusively decides a local reversible claim; reviewer multiplication adds no information.
- **MATURE_FORM:** Require independently informative evidence in proportion to consequence and explicitly disclose shared assumptions and sources.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Informational independence and diversity of assurance evidence
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** One direct authoritative discriminator suffices when it conclusively decides a local reversible claim; reviewer multiplication adds no information.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Require independently informative evidence in proportion to consequence and explicitly disclose shared assumptions and sources.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S044, S046, S049, S050, S099; critical/contrary: S048, S050.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Informational independence and diversity of assurance evidence, rather than only a proxy, component check or document status?
- When the trigger is present — High-consequence claims whose error cannot be cheaply discovered after deployment. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Disagreements, common inputs, oracle diversity, defect yield, challenge closure and configuration coverage. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: The independent function needs organisational freedom and information access, but informational independence must be assessed separately.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: One direct authoritative discriminator suffices when it conclusively decides a local reversible claim; reviewer multiplication adds no information.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-026 — Claim–argument–evidence safety assurance

- **PROPERTY_ID:** ESS-026
- **PROPERTY_NAME:** Claim–argument–evidence safety assurance
- **LOSS_OR_HAZARD:** Unjustified operation or certification when the argument omits a hazard, rests on false premises or cites stale evidence.
- **FAILURE_MODE:** Circular reasoning, unsupported inference, hidden context, confirmation bias and argument completion after design decisions.
- **MATURE_FORM:** A current, defeasible decision argument connecting consequential claims to relevant evidence, assumptions, uncertainty and authority.
- **TRIGGER:** Consequential safety decisions requiring synthesis across heterogeneous evidence and organisations.
- **CHEAP_PATH:** A direct deterministic proof/test and a brief recorded rationale may be the whole case for a narrow reversible claim.
- **REQUIRED_PRECONDITIONS:** Defined claims and consumers, trustworthy evidence, current system boundary and willingness to record uncertainty/defeaters.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Evidence validity, claim coverage, assumptions, challenge status, operational indicators and configuration/change events.
- **AUTHORITY_BOUNDARY:** The case owner must not control all challenge; acceptance authority needs power to reject or demand evidence.
- **CRITICISMS:** Nimrod is powerful counterevidence to equating a voluminous accepted case with safety; formal coherence cannot establish premise truth.
- **ANTI_CEREMONY_BOUNDARY:** GSN and a monolithic document are optional notations; explicit justified reasoning is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Claim–argument–evidence safety assurance
- **LOSS_OR_HAZARD:** Unjustified operation or certification when the argument omits a hazard, rests on false premises or cites stale evidence.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Claim–argument–evidence safety assurance.
- **CONTROL_ACTION:** Construct the minimum argument needed for live decisions; expose premises, evidence relevance, uncertainty and unresolved challenges; bind it to current configuration.
- **REQUIRED_FEEDBACK:** Evidence validity, claim coverage, assumptions, challenge status, operational indicators and configuration/change events.
- **PROCESS_MODEL_ASSUMPTION:** Defined claims and consumers, trustworthy evidence, current system boundary and willingness to record uncertainty/defeaters.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** The case owner must not control all challenge; acceptance authority needs power to reject or demand evidence.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** A direct deterministic proof/test and a brief recorded rationale may be the whole case for a narrow reversible claim.
- **MATURE_FORM:** A current, defeasible decision argument connecting consequential claims to relevant evidence, assumptions, uncertainty and authority.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Claim–argument–evidence safety assurance
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** A direct deterministic proof/test and a brief recorded rationale may be the whole case for a narrow reversible claim.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** A current, defeasible decision argument connecting consequential claims to relevant evidence, assumptions, uncertainty and authority.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S042, S043, S044, S045, S046, S108; critical/contrary: S048, S107, S108.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Claim–argument–evidence safety assurance, rather than only a proxy, component check or document status?
- When the trigger is present — Consequential safety decisions requiring synthesis across heterogeneous evidence and organisations. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Evidence validity, claim coverage, assumptions, challenge status, operational indicators and configuration/change events. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: The case owner must not control all challenge; acceptance authority needs power to reject or demand evidence.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: A direct deterministic proof/test and a brief recorded rationale may be the whole case for a narrow reversible claim.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-027 — Defeaters, counterevidence and authorised challenge in assurance

- **PROPERTY_ID:** ESS-027
- **PROPERTY_NAME:** Defeaters, counterevidence and authorised challenge in assurance
- **LOSS_OR_HAZARD:** Loss after a plausible counter-scenario, adverse test or invalid assumption was ignored or normalised.
- **FAILURE_MODE:** Confirmation bias, authority gradients, schedule pressure and challenge without closure suppress disconfirming information.
- **MATURE_FORM:** A consequential claim remains provisional until material defeaters are eliminated, controlled, or explicitly accepted by the right authority.
- **TRIGGER:** High-consequence or model-sensitive claims, novel systems and changes that invalidate prior assumptions.
- **CHEAP_PATH:** For a settled low-consequence deterministic claim, one sanity check is enough; adversarial boards add no value.
- **REQUIRED_PRECONDITIONS:** Psychological/organisational safety for dissent, traceable challenge state and a decision process that can change course.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Open objections, negative tests, anomaly trends, premise failures, response quality and whether decisions changed.
- **AUTHORITY_BOUNDARY:** Challengers need access and non-retaliation; decision authority must answer rather than merely receive objections.
- **CRITICISMS:** Challenge quality is difficult to measure; more reviewers can repeat the same assumptions or paralyse decisions.
- **ANTI_CEREMONY_BOUNDARY:** A “devil’s advocate” meeting is not required; live disconfirming evidence and authority to act are.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Defeaters, counterevidence and authorised challenge in assurance
- **LOSS_OR_HAZARD:** Loss after a plausible counter-scenario, adverse test or invalid assumption was ignored or normalised.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Defeaters, counterevidence and authorised challenge in assurance.
- **CONTROL_ACTION:** Record defeaters and contrary evidence, empower technically competent challenge, assign closure criteria and preserve unresolved uncertainty in acceptance.
- **REQUIRED_FEEDBACK:** Open objections, negative tests, anomaly trends, premise failures, response quality and whether decisions changed.
- **PROCESS_MODEL_ASSUMPTION:** Psychological/organisational safety for dissent, traceable challenge state and a decision process that can change course.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Challengers need access and non-retaliation; decision authority must answer rather than merely receive objections.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** For a settled low-consequence deterministic claim, one sanity check is enough; adversarial boards add no value.
- **MATURE_FORM:** A consequential claim remains provisional until material defeaters are eliminated, controlled, or explicitly accepted by the right authority.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Defeaters, counterevidence and authorised challenge in assurance
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** For a settled low-consequence deterministic claim, one sanity check is enough; adversarial boards add no value.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** A consequential claim remains provisional until material defeaters are eliminated, controlled, or explicitly accepted by the right authority.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S044, S045, S046, S112; critical/contrary: S048, S050.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Defeaters, counterevidence and authorised challenge in assurance, rather than only a proxy, component check or document status?
- When the trigger is present — High-consequence or model-sensitive claims, novel systems and changes that invalidate prior assumptions. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Open objections, negative tests, anomaly trends, premise failures, response quality and whether decisions changed. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Challengers need access and non-retaliation; decision authority must answer rather than merely receive objections.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: For a settled low-consequence deterministic claim, one sanity check is enough; adversarial boards add no value.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-028 — Configuration identity binding for safety evidence

- **PROPERTY_ID:** ESS-028
- **PROPERTY_NAME:** Configuration identity binding for safety evidence
- **LOSS_OR_HAZARD:** Unsafe release or operation based on valid historical evidence that no longer describes the actual system.
- **FAILURE_MODE:** Silent drift, untracked field modification, document/code divergence, wrong test article or environment mismatch.
- **MATURE_FORM:** No consequential safety claim is reusable without demonstrating that its configuration, environment and assumptions still match.
- **TRIGGER:** Any safety-relevant change, distributed deployment, supplier substitution or long-lived assurance claim.
- **CHEAP_PATH:** For a local disposable reversible experiment, identify only the artefact and conditions necessary to reproduce the decisive check.
- **REQUIRED_PRECONDITIONS:** Controlled baselines, deployment observability, supplier/change notification and an impact model.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Build/component IDs, calibration, parameters, environment, evidence version, deployment inventory and deviations.
- **AUTHORITY_BOUNDARY:** Release/operations authority must be able to block unknown or mismatched configurations.
- **CRITICISMS:** A hash or baseline name does not prove behavioural equivalence; operational environment and hidden dependencies may still differ.
- **ANTI_CEREMONY_BOUNDARY:** The property is identity/equivalence sufficient for the decision; a particular CM database is not required.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Configuration identity binding for safety evidence
- **LOSS_OR_HAZARD:** Unsafe release or operation based on valid historical evidence that no longer describes the actual system.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Configuration identity binding for safety evidence.
- **CONTROL_ACTION:** Record decision-relevant configuration identifiers and evidence provenance; verify deployed identity and invalidate/reassess affected claims on divergence.
- **REQUIRED_FEEDBACK:** Build/component IDs, calibration, parameters, environment, evidence version, deployment inventory and deviations.
- **PROCESS_MODEL_ASSUMPTION:** Controlled baselines, deployment observability, supplier/change notification and an impact model.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Release/operations authority must be able to block unknown or mismatched configurations.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** For a local disposable reversible experiment, identify only the artefact and conditions necessary to reproduce the decisive check.
- **MATURE_FORM:** No consequential safety claim is reusable without demonstrating that its configuration, environment and assumptions still match.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Configuration identity binding for safety evidence
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** For a local disposable reversible experiment, identify only the artefact and conditions necessary to reproduce the decisive check.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** No consequential safety claim is reusable without demonstrating that its configuration, environment and assumptions still match.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S029, S042, S047, S052, S100; critical/contrary: S048, S095.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Configuration identity binding for safety evidence, rather than only a proxy, component check or document status?
- When the trigger is present — Any safety-relevant change, distributed deployment, supplier substitution or long-lived assurance claim. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Build/component IDs, calibration, parameters, environment, evidence version, deployment inventory and deviations. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Release/operations authority must be able to block unknown or mismatched configurations.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: For a local disposable reversible experiment, identify only the artefact and conditions necessary to reproduce the decisive check.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-029 — Safety impact analysis and proportionate re-assurance after change

- **PROPERTY_ID:** ESS-029
- **PROPERTY_NAME:** Safety impact analysis and proportionate re-assurance after change
- **LOSS_OR_HAZARD:** Loss from changed behaviour or assumptions; or safety debt/workarounds caused by excessive change burden.
- **FAILURE_MODE:** Scope is inferred from file count or label rather than causal reach; indirect interfaces, suppliers and operational context are missed.
- **MATURE_FORM:** Re-establish exactly the safety claims whose system, assumptions, controls or evidence may have changed; justify both reuse and new work.
- **TRIGGER:** Software, hardware, supplier, environment, procedure, security and organisational changes with plausible hazard reach.
- **CHEAP_PATH:** A trivial local reversible change with a decisive regression discriminator uses that check and records only the necessary identity.
- **REQUIRED_PRECONDITIONS:** Current baseline, dependency/interface model, hazard state and authority to classify/escalate change.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Diff/configuration identity, changed assumptions, affected tests, operational telemetry, regression and rollback readiness.
- **AUTHORITY_BOUNDARY:** Change authority must be able to stop release, demand wider evidence and approve bounded reuse.
- **CRITICISMS:** Incremental assurance depends on accurate impact models; complex adaptive interactions can defeat locality assumptions.
- **ANTI_CEREMONY_BOUNDARY:** A change board is optional; causal impact, authority and current evidence are not.
- **POSSIBLE_CONFLICTING_PROPERTY:** Stable baseline and re-assurance can conflict with adaptive delivery and urgent safety/security change.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Safety impact analysis and proportionate re-assurance after change
- **LOSS_OR_HAZARD:** Loss from changed behaviour or assumptions; or safety debt/workarounds caused by excessive change burden.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Safety impact analysis and proportionate re-assurance after change.
- **CONTROL_ACTION:** Use traceable impact analysis from change to hazards, interactions, constraints and evidence; test the affected frontier and monitor uncertain effects.
- **REQUIRED_FEEDBACK:** Diff/configuration identity, changed assumptions, affected tests, operational telemetry, regression and rollback readiness.
- **PROCESS_MODEL_ASSUMPTION:** Current baseline, dependency/interface model, hazard state and authority to classify/escalate change.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Change authority must be able to stop release, demand wider evidence and approve bounded reuse.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** A trivial local reversible change with a decisive regression discriminator uses that check and records only the necessary identity.
- **MATURE_FORM:** Re-establish exactly the safety claims whose system, assumptions, controls or evidence may have changed; justify both reuse and new work.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Safety impact analysis and proportionate re-assurance after change
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** A trivial local reversible change with a decisive regression discriminator uses that check and records only the necessary identity.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Re-establish exactly the safety claims whose system, assumptions, controls or evidence may have changed; justify both reuse and new work.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S052, S053, S054, S055, S095, S098; critical/contrary: S048, S095.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Safety impact analysis and proportionate re-assurance after change, rather than only a proxy, component check or document status?
- When the trigger is present — Software, hardware, supplier, environment, procedure, security and organisational changes with plausible hazard reach. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Diff/configuration identity, changed assumptions, affected tests, operational telemetry, regression and rollback readiness. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Change authority must be able to stop release, demand wider evidence and approve bounded reuse.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: A trivial local reversible change with a decisive regression discriminator uses that check and records only the necessary identity.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-030 — Living, current and operationally connected assurance

- **PROPERTY_ID:** ESS-030
- **PROPERTY_NAME:** Living, current and operationally connected assurance
- **LOSS_OR_HAZARD:** Operation continues under stale assurance that no longer represents current hazard exposure or control health.
- **FAILURE_MODE:** Update latency, disconnected telemetry, alert overload, unowned evidence expiry and dashboards without decision authority.
- **MATURE_FORM:** Assurance remains valid only while named configuration, assumptions, controls and evidence are current; relevant changes trigger bounded reassessment.
- **TRIGGER:** Long-lived software-intensive, autonomous, security-exposed or operationally adapting systems.
- **CHEAP_PATH:** Static assurance can suffice for a stable, bounded, short-lived and readily observed system; update only when a relevant trigger occurs.
- **REQUIRED_PRECONDITIONS:** Stable claim architecture, configuration identity, trusted telemetry, trigger thresholds and resourced decision owners.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Configuration, control health, incidents/precursors, assumption monitors, evidence expiry and operational-envelope excursions.
- **AUTHORITY_BOUNDARY:** Owners need authority to restrict, degrade, rollback or re-assure on adverse evidence.
- **CRITICISMS:** Continuous assurance cannot observe unknown hazards and may privilege measurable proxies over causal control state.
- **ANTI_CEREMONY_BOUNDARY:** Continuous document editing is not required; current decision-relevant assurance state is.
- **POSSIBLE_CONFLICTING_PROPERTY:** Continuous monitoring can conflict with evidence independence and alarm burden.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Living, current and operationally connected assurance
- **LOSS_OR_HAZARD:** Operation continues under stale assurance that no longer represents current hazard exposure or control health.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Living, current and operationally connected assurance.
- **CONTROL_ACTION:** Define change and operational triggers, connect leading evidence to claims, reassess affected arguments and require decision closure.
- **REQUIRED_FEEDBACK:** Configuration, control health, incidents/precursors, assumption monitors, evidence expiry and operational-envelope excursions.
- **PROCESS_MODEL_ASSUMPTION:** Stable claim architecture, configuration identity, trusted telemetry, trigger thresholds and resourced decision owners.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Owners need authority to restrict, degrade, rollback or re-assure on adverse evidence.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Static assurance can suffice for a stable, bounded, short-lived and readily observed system; update only when a relevant trigger occurs.
- **MATURE_FORM:** Assurance remains valid only while named configuration, assumptions, controls and evidence are current; relevant changes trigger bounded reassessment.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Living, current and operationally connected assurance
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Static assurance can suffice for a stable, bounded, short-lived and readily observed system; update only when a relevant trigger occurs.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Assurance remains valid only while named configuration, assumptions, controls and evidence are current; relevant changes trigger bounded reassessment.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S047, S055, S098; critical/contrary: S048, S074, S108.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Living, current and operationally connected assurance, rather than only a proxy, component check or document status?
- When the trigger is present — Long-lived software-intensive, autonomous, security-exposed or operationally adapting systems. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Configuration, control health, incidents/precursors, assumption monitors, evidence expiry and operational-envelope excursions. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Owners need authority to restrict, degrade, rollback or re-assure on adverse evidence.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Static assurance can suffice for a stable, bounded, short-lived and readily observed system; update only when a relevant trigger occurs.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-031 — Independent assessment and IV&V where consequence warrants

- **PROPERTY_ID:** ESS-031
- **PROPERTY_NAME:** Independent assessment and IV&V where consequence warrants
- **LOSS_OR_HAZARD:** Undetected systematic defect, optimistic interpretation or conflicted acceptance in consequential systems.
- **FAILURE_MODE:** Shared oracles, insufficient access, ceremonial sign-off, late review and organisational independence without informational independence.
- **MATURE_FORM:** Deploy independent assessment only where its distinct information and challenge authority justify cost, and measure it by decisions/findings rather than signatures.
- **TRIGGER:** Catastrophic or irreversible failure conditions, novel technology, weak testability, conflicted suppliers or mandated domains.
- **CHEAP_PATH:** Routine peer review or one deterministic check is sufficient for low-consequence reversible work; separate IV&V should not trigger by label alone.
- **REQUIRED_PRECONDITIONS:** Competence, access, independence, clear claim scope and response authority.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Independent defect findings, evidence provenance, unresolved dissent, retest results and configuration coverage.
- **AUTHORITY_BOUNDARY:** The assessor must be able to report to an authority that can change design, release or operation.
- **CRITICISMS:** Controlled multiversion evidence and assurance failures show that nominal independence can remain correlated.
- **ANTI_CEREMONY_BOUNDARY:** A separate organisation is not the property; independently informative challenge is.
- **POSSIBLE_CONFLICTING_PROPERTY:** Independent review can conflict with speed and shared technical context.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Independent assessment and IV&V where consequence warrants
- **LOSS_OR_HAZARD:** Undetected systematic defect, optimistic interpretation or conflicted acceptance in consequential systems.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Independent assessment and IV&V where consequence warrants.
- **CONTROL_ACTION:** Define risk-based scope, give assessors evidence/tool/access rights, seek independent information and close material findings before acceptance.
- **REQUIRED_FEEDBACK:** Independent defect findings, evidence provenance, unresolved dissent, retest results and configuration coverage.
- **PROCESS_MODEL_ASSUMPTION:** Competence, access, independence, clear claim scope and response authority.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** The assessor must be able to report to an authority that can change design, release or operation.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Routine peer review or one deterministic check is sufficient for low-consequence reversible work; separate IV&V should not trigger by label alone.
- **MATURE_FORM:** Deploy independent assessment only where its distinct information and challenge authority justify cost, and measure it by decisions/findings rather than signatures.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Independent assessment and IV&V where consequence warrants
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Routine peer review or one deterministic check is sufficient for low-consequence reversible work; separate IV&V should not trigger by label alone.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Deploy independent assessment only where its distinct information and challenge authority justify cost, and measure it by decisions/findings rather than signatures.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S029, S042, S099, S100; critical/contrary: S048, S050.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Independent assessment and IV&V where consequence warrants, rather than only a proxy, component check or document status?
- When the trigger is present — Catastrophic or irreversible failure conditions, novel technology, weak testability, conflicted suppliers or mandated domains. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Independent defect findings, evidence provenance, unresolved dissent, retest results and configuration coverage. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: The assessor must be able to report to an authority that can change design, release or operation.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Routine peer review or one deterministic check is sufficient for low-consequence reversible work; separate IV&V should not trigger by label alone.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-032 — Evidence triangulation and targeted formal verification

- **PROPERTY_ID:** ESS-032
- **PROPERTY_NAME:** Evidence triangulation and targeted formal verification
- **LOSS_OR_HAZARD:** Unsafe acceptance after untested corner states, invalid formal assumptions or common evidence blind spots.
- **FAILURE_MODE:** Model–implementation gap, specification error, unqualified tools, oracle weakness and evidence dependence.
- **MATURE_FORM:** Use formal methods selectively where a precise hazard-linked property and abstraction make them decisively informative, then triangulate model correspondence.
- **TRIGGER:** Complex logic, concurrency, control laws, protection functions or rare combinations where exhaustive empirical testing is infeasible.
- **CHEAP_PATH:** Use direct execution, inspection or deterministic testing when it fully settles a simple claim; formalisation must earn its cost.
- **REQUIRED_PRECONDITIONS:** Precise property and model, validated abstraction, configuration mapping, trustworthy tools and a decision consumer.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Proof obligations, model assumptions, code/configuration correspondence, test coverage and operational anomalies.
- **AUTHORITY_BOUNDARY:** Assurance authority decides where proof/test diversity is necessary and owns residual model risk.
- **CRITICISMS:** Formal proof establishes only the modelled property under assumptions; outcome superiority over disciplined testing is context dependent.
- **ANTI_CEREMONY_BOUNDARY:** A proof certificate is not a safety claim about the physical system without validated assumptions and configuration linkage.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Evidence triangulation and targeted formal verification
- **LOSS_OR_HAZARD:** Unsafe acceptance after untested corner states, invalid formal assumptions or common evidence blind spots.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Evidence triangulation and targeted formal verification.
- **CONTROL_ACTION:** For each consequential claim, select the least set of analyses/tests/inspections/operational evidence that attacks distinct failure modes; prove only tractable decisive properties.
- **REQUIRED_FEEDBACK:** Proof obligations, model assumptions, code/configuration correspondence, test coverage and operational anomalies.
- **PROCESS_MODEL_ASSUMPTION:** Precise property and model, validated abstraction, configuration mapping, trustworthy tools and a decision consumer.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Assurance authority decides where proof/test diversity is necessary and owns residual model risk.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Use direct execution, inspection or deterministic testing when it fully settles a simple claim; formalisation must earn its cost.
- **MATURE_FORM:** Use formal methods selectively where a precise hazard-linked property and abstraction make them decisively informative, then triangulate model correspondence.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Evidence triangulation and targeted formal verification
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Use direct execution, inspection or deterministic testing when it fully settles a simple claim; formalisation must earn its cost.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Use formal methods selectively where a precise hazard-linked property and abstraction make them decisively informative, then triangulate model correspondence.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S044, S049, S098, S100; critical/contrary: S048, S050.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Evidence triangulation and targeted formal verification, rather than only a proxy, component check or document status?
- When the trigger is present — Complex logic, concurrency, control laws, protection functions or rare combinations where exhaustive empirical testing is infeasible. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Proof obligations, model assumptions, code/configuration correspondence, test coverage and operational anomalies. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Assurance authority decides where proof/test diversity is necessary and owns residual model risk.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Use direct execution, inspection or deterministic testing when it fully settles a simple claim; formalisation must earn its cost.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-033 — Joint safety–security analysis for cyber-physical control

- **PROPERTY_ID:** ESS-033
- **PROPERTY_NAME:** Joint safety–security analysis for cyber-physical control
- **LOSS_OR_HAZARD:** Physical or health loss caused or amplified by compromised digital/organisational control.
- **FAILURE_MODE:** Separate teams use incompatible assets, threat/hazard models, timing assumptions and change controls; security fixes introduce new safety hazards.
- **MATURE_FORM:** Co-engineer safety and security whenever they share control, feedback, configuration or availability dependencies; keep domain analyses complementary.
- **TRIGGER:** Networked, updateable, remotely supported, autonomous or adversarially exposed safety-relevant systems.
- **CHEAP_PATH:** Do not impose a full threat programme on an isolated trivial reversible function with no plausible adversarial safety pathway.
- **REQUIRED_PRECONDITIONS:** Shared architecture/configuration view, threat and hazard expertise, coordinated authority and secure observability.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Security events, control/feedback integrity, patch/configuration status, availability, anomalies and attack-path assumptions.
- **AUTHORITY_BOUNDARY:** Safety and security owners need a joint escalation/acceptance path; neither may unilaterally break the other control objective.
- **CRITICISMS:** Integrated methods and comparative effectiveness evidence are still developing; total model completeness is impossible.
- **ANTI_CEREMONY_BOUNDARY:** A combined workshop or merged document is optional; the shared causal paths and authority are not.
- **POSSIBLE_CONFLICTING_PROPERTY:** Urgent security remediation can conflict with safety regression assurance and availability.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Joint safety–security analysis for cyber-physical control
- **LOSS_OR_HAZARD:** Physical or health loss caused or amplified by compromised digital/organisational control.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Joint safety–security analysis for cyber-physical control.
- **CONTROL_ACTION:** Share system/control boundaries, identify safety consequences of threats and security consequences of safety controls, coordinate mitigations and changes.
- **REQUIRED_FEEDBACK:** Security events, control/feedback integrity, patch/configuration status, availability, anomalies and attack-path assumptions.
- **PROCESS_MODEL_ASSUMPTION:** Shared architecture/configuration view, threat and hazard expertise, coordinated authority and secure observability.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Safety and security owners need a joint escalation/acceptance path; neither may unilaterally break the other control objective.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Do not impose a full threat programme on an isolated trivial reversible function with no plausible adversarial safety pathway.
- **MATURE_FORM:** Co-engineer safety and security whenever they share control, feedback, configuration or availability dependencies; keep domain analyses complementary.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Joint safety–security analysis for cyber-physical control
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Do not impose a full threat programme on an isolated trivial reversible function with no plausible adversarial safety pathway.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Co-engineer safety and security whenever they share control, feedback, configuration or availability dependencies; keep domain analyses complementary.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S026, S028, S061; critical/contrary: S055, S074.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Joint safety–security analysis for cyber-physical control, rather than only a proxy, component check or document status?
- When the trigger is present — Networked, updateable, remotely supported, autonomous or adversarially exposed safety-relevant systems. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Security events, control/feedback integrity, patch/configuration status, availability, anomalies and attack-path assumptions. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Safety and security owners need a joint escalation/acceptance path; neither may unilaterally break the other control objective.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Do not impose a full threat programme on an isolated trivial reversible function with no plausible adversarial safety pathway.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-034 — Actionable hazard detection and alarm burden control

- **PROPERTY_ID:** ESS-034
- **PROPERTY_NAME:** Actionable hazard detection and alarm burden control
- **LOSS_OR_HAZARD:** Uncontained hazard due to missed, late, stale, ambiguous or ignored warning; secondary loss from needless stops.
- **FAILURE_MODE:** Poor sensor coverage, threshold design, prioritisation, mode context, alarm floods and absent response authority.
- **MATURE_FORM:** An alarm is justified only when its signal is trustworthy, timely, discriminating and connected to an effective authorised response.
- **TRIGGER:** Hazards requiring detection before irreversible progression, especially remote or highly automated processes.
- **CHEAP_PATH:** Direct physical prevention or immediate observation may be cheaper than alarms; do not alert when no safe action exists.
- **REQUIRED_PRECONDITIONS:** Detectable precursor, sufficient response time, reliable signal semantics, trained/authorised consumer and maintained sensors.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Detection probability/latency, false/nuisance rate, acknowledgement, action completion, alarm floods and sensor health.
- **AUTHORITY_BOUNDARY:** The receiver needs authority and resources to diagnose, stop, isolate or escalate; alarm ownership must be explicit.
- **CRITICISMS:** More detection can reduce safety when attention and response capacity are saturated; alarm counts are poor proxies.
- **ANTI_CEREMONY_BOUNDARY:** A dashboard tile or alarm count is ceremony without a live decision and burden budget.
- **POSSIBLE_CONFLICTING_PROPERTY:** More detection conflicts with alarm burden, attention and false-stop cost.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Actionable hazard detection and alarm burden control
- **LOSS_OR_HAZARD:** Uncontained hazard due to missed, late, stale, ambiguous or ignored warning; secondary loss from needless stops.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Actionable hazard detection and alarm burden control.
- **CONTROL_ACTION:** Link each safety-significant alarm to hazard, timing, decision, response and confirmation; monitor false/missed alarm performance and rationalise burden.
- **REQUIRED_FEEDBACK:** Detection probability/latency, false/nuisance rate, acknowledgement, action completion, alarm floods and sensor health.
- **PROCESS_MODEL_ASSUMPTION:** Detectable precursor, sufficient response time, reliable signal semantics, trained/authorised consumer and maintained sensors.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** The receiver needs authority and resources to diagnose, stop, isolate or escalate; alarm ownership must be explicit.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Direct physical prevention or immediate observation may be cheaper than alarms; do not alert when no safe action exists.
- **MATURE_FORM:** An alarm is justified only when its signal is trustworthy, timely, discriminating and connected to an effective authorised response.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Actionable hazard detection and alarm burden control
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Direct physical prevention or immediate observation may be cheaper than alarms; do not alert when no safe action exists.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** An alarm is justified only when its signal is trustworthy, timely, discriminating and connected to an effective authorised response.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S074, S075, S101, S106; critical/contrary: S073, S074.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Actionable hazard detection and alarm burden control, rather than only a proxy, component check or document status?
- When the trigger is present — Hazards requiring detection before irreversible progression, especially remote or highly automated processes. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Detection probability/latency, false/nuisance rate, acknowledgement, action completion, alarm floods and sensor health. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: The receiver needs authority and resources to diagnose, stop, isolate or escalate; alarm ownership must be explicit.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Direct physical prevention or immediate observation may be cheaper than alarms; do not alert when no safe action exists.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-035 — Containment, isolation and emergency stop with state confirmation

- **PROPERTY_ID:** ESS-035
- **PROPERTY_NAME:** Containment, isolation and emergency stop with state confirmation
- **LOSS_OR_HAZARD:** Escalating release, collision, energy transfer or public exposure after a failed prevention layer.
- **FAILURE_MODE:** Actuator failure, shared utility loss, inaccessible isolation, delayed action, feedback echo and unsafe stop sequence.
- **MATURE_FORM:** Containment is achieved only when the hazardous process state is demonstrably bounded, not when a command is issued.
- **TRIGGER:** Hazards whose progression can still be bounded after detection and before irreversible loss.
- **CHEAP_PATH:** For a local reversible state, a direct stop and immediate observation may suffice; do not add emergency machinery without a credible propagation path.
- **REQUIRED_PRECONDITIONS:** Reachable safe/contained state, sufficient time, maintained actuation and feedback, and known interactions with mission/availability.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Command receipt, actuator position, process state, leak/energy isolation, residual inventory and containment integrity.
- **AUTHORITY_BOUNDARY:** Controller/operator must have stop authority; restart authority is separate and requires restoration evidence.
- **CRITICISMS:** HSE safety alerts show nominal safe-position claims can fail physically; fail-safe is not universal where service continuity prevents harm.
- **ANTI_CEREMONY_BOUNDARY:** Emergency-stop hardware is context-specific; verified propagation control is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** Stopping/isolating can conflict with safety-critical availability; see ESS-036.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Containment, isolation and emergency stop with state confirmation
- **LOSS_OR_HAZARD:** Hazard propagation after prevention fails
- **CONTROLLER:** Protection system and authorised operator
- **CONTROLLED_PROCESS:** Hazardous physical/software process and its energy/material/control paths
- **SAFETY_CONSTRAINT:** On trigger, propagation shall be interrupted and the contained/safe condition confirmed within the available time
- **CONTROL_ACTION:** Trip, isolate, inhibit, vent, arrest or segregate and then verify effect
- **REQUIRED_FEEDBACK:** Independent actuator/process state, residual energy/material and barrier integrity
- **PROCESS_MODEL_ASSUMPTION:** The selected stop/containment sequence is safe for the current mode and utilities remain available
- **DELAY_OR_OBSERVABILITY_RISK:** Late or echo-only feedback can permit progression while indicating command success
- **AUTHORITY_BOUNDARY:** Stop authority may be broad; restart authority must be distinct and evidence-based
- **FAILURE_IF_OVER_APPLIED:** False trips or indiscriminate shutdown can remove safety-critical service or induce bypass
- **CHEAP_PATH:** Direct stop plus immediate observation for a local reversible process
- **MATURE_FORM:** End-to-end confirmed containment with degraded-protection restrictions and separate restart criteria


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Containment, isolation and emergency stop with state confirmation
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** For a local reversible state, a direct stop and immediate observation may suffice; do not add emergency machinery without a credible propagation path.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Containment is achieved only when the hazardous process state is demonstrably bounded, not when a command is issued.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S051, S058, S101, S102, S103; critical/contrary: S058, S074.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Containment, isolation and emergency stop with state confirmation, rather than only a proxy, component check or document status?
- When the trigger is present — Hazards whose progression can still be bounded after detection and before irreversible loss. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Command receipt, actuator position, process state, leak/energy isolation, residual inventory and containment integrity. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Controller/operator must have stop authority; restart authority is separate and requires restoration evidence.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: For a local reversible state, a direct stop and immediate observation may suffice; do not add emergency machinery without a credible propagation path.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-036 — Context-sensitive fail-safe, fail-operational and graceful-degradation design

- **PROPERTY_ID:** ESS-036
- **PROPERTY_NAME:** Context-sensitive fail-safe, fail-operational and graceful-degradation design
- **LOSS_OR_HAZARD:** Loss caused either by hazardous continued operation or by removal of a service necessary to protect life/mission.
- **FAILURE_MODE:** Wrong safe-state assumption, hidden mode transition, degraded function outside envelope, common-mode protection loss or unannounced capability reduction.
- **MATURE_FORM:** Select and assure the lowest-loss response for each credible condition, with observable bounded degraded operation and timely recovery.
- **TRIGGER:** Systems where stopping and continuing can each be hazardous: aircraft, medical support, nuclear cooling, transport and emergency services.
- **CHEAP_PATH:** For noncritical reversible functions, stop cleanly and recover normally; elaborate degradation architectures are unnecessary.
- **REQUIRED_PRECONDITIONS:** Explicit mission/loss model, reliable mode detection, bounded degraded capability and containment/recovery path.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Mode, remaining capability, environmental demand, barrier health, time in degraded state and operator comprehension.
- **AUTHORITY_BOUNDARY:** Automation and operators need defined transition/override authority; degraded operation must have an accountable expiry/recovery owner.
- **CRITICISMS:** Continued service can be necessary for safety, but fail-operational complexity and human understanding can introduce new hazards.
- **ANTI_CEREMONY_BOUNDARY:** A named “safe state” is not automatically safe across modes; the underlying loss comparison and controlled transition are the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** Fail-operational continuity conflicts with fail-safe containment and architecture simplicity.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Context-sensitive fail-safe, fail-operational and graceful-degradation design
- **LOSS_OR_HAZARD:** Loss caused either by hazardous continued operation or by removal of a service necessary to protect life/mission.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Context-sensitive fail-safe, fail-operational and graceful-degradation design.
- **CONTROL_ACTION:** Define mode-specific safe/degraded envelopes, transition logic, time limits, operator authority and feedback; prove both continuation and stopping hazards.
- **REQUIRED_FEEDBACK:** Mode, remaining capability, environmental demand, barrier health, time in degraded state and operator comprehension.
- **PROCESS_MODEL_ASSUMPTION:** Explicit mission/loss model, reliable mode detection, bounded degraded capability and containment/recovery path.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Automation and operators need defined transition/override authority; degraded operation must have an accountable expiry/recovery owner.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** For noncritical reversible functions, stop cleanly and recover normally; elaborate degradation architectures are unnecessary.
- **MATURE_FORM:** Select and assure the lowest-loss response for each credible condition, with observable bounded degraded operation and timely recovery.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Context-sensitive fail-safe, fail-operational and graceful-degradation design
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** For noncritical reversible functions, stop cleanly and recover normally; elaborate degradation architectures are unnecessary.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Select and assure the lowest-loss response for each credible condition, with observable bounded degraded operation and timely recovery.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S051, S059, S060, S103; critical/contrary: S058, S089, S090.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Context-sensitive fail-safe, fail-operational and graceful-degradation design, rather than only a proxy, component check or document status?
- When the trigger is present — Systems where stopping and continuing can each be hazardous: aircraft, medical support, nuclear cooling, transport and emergency services. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Mode, remaining capability, environmental demand, barrier health, time in degraded state and operator comprehension. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Automation and operators need defined transition/override authority; degraded operation must have an accountable expiry/recovery owner.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: For noncritical reversible functions, stop cleanly and recover normally; elaborate degradation architectures are unnecessary.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-037 — Recovery, rollback and restart only after restored safety constraints

- **PROPERTY_ID:** ESS-037
- **PROPERTY_NAME:** Recovery, rollback and restart only after restored safety constraints
- **LOSS_OR_HAZARD:** Recurrence, latent damaged state or new loss during premature restart or unsafe rollback.
- **FAILURE_MODE:** Pressure to resume, incomplete diagnosis, incompatible rollback, untested repairs, reset alarms and missing proof of barrier restoration.
- **MATURE_FORM:** Recovery is complete only when relevant safety constraints and feedback are re-established and an authorised owner accepts the remaining uncertainty.
- **TRIGGER:** Consequential incidents, emergency stops, failed changes, degraded modes and repairs that can leave latent hazard.
- **CHEAP_PATH:** A trivial reversible action can be retried after direct verification; no recovery board is needed.
- **REQUIRED_PRECONDITIONS:** Recoverable baseline, rollback compatibility, diagnostic evidence, barrier tests and an escalation path when state is uncertain.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Constraint/barrier status, configuration identity, residual damage, test results, anomaly trend and staged operating feedback.
- **AUTHORITY_BOUNDARY:** Restart authority must be distinct from the person merely restoring service and able to demand continued restriction.
- **CRITICISMS:** Proof testing can itself be hazardous or incomplete; exact recovery architecture is highly domain specific.
- **ANTI_CEREMONY_BOUNDARY:** A restart checklist is optional; demonstrable restored control and separate authority are not.
- **POSSIBLE_CONFLICTING_PROPERTY:** Conservative restart evidence can conflict with harms caused by prolonged service loss.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Recovery, rollback and restart after restored constraints
- **LOSS_OR_HAZARD:** Recurrence or new loss during premature restoration
- **CONTROLLER:** Recovery and restart authority
- **CONTROLLED_PROCESS:** Stopped, isolated, degraded or modified system
- **SAFETY_CONSTRAINT:** The system shall return to service only after relevant constraints, configuration and observability are restored or residual risk is explicitly accepted
- **CONTROL_ACTION:** Diagnose, repair/rollback, proof-test, stage restart and monitor
- **REQUIRED_FEEDBACK:** Configuration, barrier status, diagnostics, staged performance and recurrence indicators
- **PROCESS_MODEL_ASSUMPTION:** The recovery baseline is compatible and the causal mechanism is controlled
- **DELAY_OR_OBSERVABILITY_RISK:** Latent damage or delayed recurrence may escape immediate proof tests
- **AUTHORITY_BOUNDARY:** Service restoration authority and safety restart acceptance must be explicit and may be separate
- **FAILURE_IF_OVER_APPLIED:** Overly conservative restart can withhold safety-critical service and create workarounds
- **CHEAP_PATH:** Direct verify-and-retry for a trivial reversible action
- **MATURE_FORM:** Constraint-restored, configuration-bound, staged restart with separate acceptance and post-restart feedback


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Recovery, rollback and restart only after restored safety constraints
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** A trivial reversible action can be retried after direct verification; no recovery board is needed.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Recovery is complete only when relevant safety constraints and feedback are re-established and an authorised owner accepts the remaining uncertainty.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S060, S102, S103, S104, S105; critical/contrary: S058, S095.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Recovery, rollback and restart only after restored safety constraints, rather than only a proxy, component check or document status?
- When the trigger is present — Consequential incidents, emergency stops, failed changes, degraded modes and repairs that can leave latent hazard. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Constraint/barrier status, configuration identity, residual damage, test results, anomaly trend and staged operating feedback. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Restart authority must be distinct from the person merely restoring service and able to demand continued restriction.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: A trivial reversible action can be retried after direct verification; no recovery board is needed.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-038 — Bounded emergency or temporary risk acceptance with compensating controls

- **PROPERTY_ID:** ESS-038
- **PROPERTY_NAME:** Bounded emergency or temporary risk acceptance with compensating controls
- **LOSS_OR_HAZARD:** Loss while a known protection is unavailable or while an exceptional configuration accumulates unexamined risk.
- **FAILURE_MODE:** Weak authority, indefinite waiver, ineffective compensation, changed exposure, handoff failure and no restoration owner.
- **MATURE_FORM:** Exceptional operation is safe enough only within an observable, time/configuration-bounded envelope whose compensating controls and authority remain current.
- **TRIGGER:** Urgent mission, repair, emergency change or safety-critical-service continuity where immediate full restoration is impossible.
- **CHEAP_PATH:** Do not create a waiver for trivial work already inside ordinary authority, and do not use temporary acceptance to avoid feasible permanent correction.
- **REQUIRED_PRECONDITIONS:** Known hazard/control state, feasible compensation, monitorable envelope, restoration plan and authority commensurate with consequence.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Time/exposure, compensating-control health, changed conditions, incidents, handoffs and restoration progress.
- **AUTHORITY_BOUNDARY:** A named emergency/risk authority must own the decision; operators need stop authority if compensation degrades.
- **CRITICISMS:** Temporary acceptance is especially susceptible to normalisation and may externalise harm; some hazards should not be accepted.
- **ANTI_CEREMONY_BOUNDARY:** A waiver form is not the property; bounded exposure, live compensation, expiry and restoration are.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Bounded emergency or temporary risk acceptance with compensating controls
- **LOSS_OR_HAZARD:** Loss while a known protection is unavailable or while an exceptional configuration accumulates unexamined risk.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Bounded emergency or temporary risk acceptance with compensating controls.
- **CONTROL_ACTION:** State the impaired control and hazard, select credible compensation, limit exposure/time, monitor conditions, assign expiry and require reauthorisation or restoration.
- **REQUIRED_FEEDBACK:** Time/exposure, compensating-control health, changed conditions, incidents, handoffs and restoration progress.
- **PROCESS_MODEL_ASSUMPTION:** Known hazard/control state, feasible compensation, monitorable envelope, restoration plan and authority commensurate with consequence.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** A named emergency/risk authority must own the decision; operators need stop authority if compensation degrades.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Do not create a waiver for trivial work already inside ordinary authority, and do not use temporary acceptance to avoid feasible permanent correction.
- **MATURE_FORM:** Exceptional operation is safe enough only within an observable, time/configuration-bounded envelope whose compensating controls and authority remain current.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Bounded emergency or temporary risk acceptance with compensating controls
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Do not create a waiver for trivial work already inside ordinary authority, and do not use temporary acceptance to avoid feasible permanent correction.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Exceptional operation is safe enough only within an observable, time/configuration-bounded envelope whose compensating controls and authority remain current.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** MODERATE — mechanism is coherent but depends on model scope and assumptions.
- **ACCIDENT_CASE_STRENGTH:** HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S042, S095, S103, S105; critical/contrary: S062, S073.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Bounded emergency or temporary risk acceptance with compensating controls, rather than only a proxy, component check or document status?
- When the trigger is present — Urgent mission, repair, emergency change or safety-critical-service continuity where immediate full restoration is impossible. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Time/exposure, compensating-control health, changed conditions, incidents, handoffs and restoration progress. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: A named emergency/risk authority must own the decision; operators need stop authority if compensation degrades.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Do not create a waiver for trivial work already inside ordinary authority, and do not use temporary acceptance to avoid feasible permanent correction.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-039 — Incident, near-miss and precursor reporting connected to learning

- **PROPERTY_ID:** ESS-039
- **PROPERTY_NAME:** Incident, near-miss and precursor reporting connected to learning
- **LOSS_OR_HAZARD:** Repeated or escalating loss because precursor evidence was suppressed, fragmented, misclassified or never consumed.
- **FAILURE_MODE:** Blame fear, reporting burden, denominator changes, selection bias, weak taxonomy, alert flooding and no authorised action owner.
- **MATURE_FORM:** Collect only information with a plausible hazard/control consumer, interpret counts with exposure and incentives, and close the loop through action or justified no-action.
- **TRIGGER:** Operational systems with sparse severe events, latent failures, weak signals or learning distributed across workers/users.
- **CHEAP_PATH:** For an immediately observed trivial defect already corrected and deterministically verified, a lightweight record or no separate report may be appropriate.
- **REQUIRED_PRECONDITIONS:** Accessible channel, just reporting conditions, triage competence, hazard linkage and a consumer able to change design or operation.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Report volume and exposure denominator, severity/precursor linkage, time to triage/action, repeat events, closure quality and reporter feedback.
- **AUTHORITY_BOUNDARY:** Reporting recipients require authority or an escalation path; reporters need protection from inappropriate retaliation while reckless conduct remains separately governed.
- **CRITICISMS:** Near-miss counts are strongly incentive- and exposure-dependent; not every near miss predicts catastrophe and reporting alone does not improve safety.
- **ANTI_CEREMONY_BOUNDARY:** A reporting portal is not the property; observable weak signals, protected transmission and decision closure are.
- **POSSIBLE_CONFLICTING_PROPERTY:** Protected reporting can conflict with accountability, privacy and security.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Incident, near-miss and precursor reporting connected to learning
- **LOSS_OR_HAZARD:** Repeated or escalating loss because precursor evidence was suppressed, fragmented, misclassified or never consumed.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Incident, near-miss and precursor reporting connected to learning.
- **CONTROL_ACTION:** Define safety-relevant reportability, protect good-faith disclosure, prioritise by credible hazard/control degradation, investigate proportionately and feed actions/status back.
- **REQUIRED_FEEDBACK:** Report volume and exposure denominator, severity/precursor linkage, time to triage/action, repeat events, closure quality and reporter feedback.
- **PROCESS_MODEL_ASSUMPTION:** Accessible channel, just reporting conditions, triage competence, hazard linkage and a consumer able to change design or operation.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Reporting recipients require authority or an escalation path; reporters need protection from inappropriate retaliation while reckless conduct remains separately governed.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** For an immediately observed trivial defect already corrected and deterministically verified, a lightweight record or no separate report may be appropriate.
- **MATURE_FORM:** Collect only information with a plausible hazard/control consumer, interpret counts with exposure and incentives, and close the loop through action or justified no-action.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Incident, near-miss and precursor reporting connected to learning
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** For an immediately observed trivial defect already corrected and deterministically verified, a lightweight record or no separate report may be appropriate.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Collect only information with a plausible hazard/control consumer, interpret counts with exposure and incentives, and close the loop through action or justified no-action.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** MODERATE — mechanism is coherent but depends on model scope and assumptions.
- **ACCIDENT_CASE_STRENGTH:** HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S076, S078, S079, S080, S097, S116; critical/contrary: S071, S072.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Incident, near-miss and precursor reporting connected to learning, rather than only a proxy, component check or document status?
- When the trigger is present — Operational systems with sparse severe events, latent failures, weak signals or learning distributed across workers/users. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Report volume and exposure denominator, severity/precursor linkage, time to triage/action, repeat events, closure quality and reporter feedback. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Reporting recipients require authority or an escalation path; reporters need protection from inappropriate retaliation while reckless conduct remains separately governed.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: For an immediately observed trivial defect already corrected and deterministically verified, a lightweight record or no separate report may be appropriate.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-040 — Multi-factor causal investigation grounded in local rationality

- **PROPERTY_ID:** ESS-040
- **PROPERTY_NAME:** Multi-factor causal investigation grounded in local rationality
- **LOSS_OR_HAZARD:** Recurrence because upstream design, feedback, workload, authority, incentives, interfaces and defences remain unchanged.
- **FAILURE_MODE:** Hindsight bias, blame seeking, evidence loss, linear storytelling, causal overreach and recommendation lists not linked to mechanisms.
- **MATURE_FORM:** Investigate until the credible causal mechanisms needed to select and verify controls are sufficiently discriminated, without treating error labels as explanations.
- **TRIGGER:** Serious incidents, recurring near misses and unexplained control/interaction failures.
- **CHEAP_PATH:** A simple, directly observed and deterministically reproducible defect can be corrected without an elaborate sociotechnical investigation.
- **REQUIRED_PRECONDITIONS:** Timely access to technical/organisational evidence, multidisciplinary competence and separation between learning and inappropriate punishment.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Timeline/state reconstruction, alternative explanations, missing/stale feedback, goal conflicts, control deficiencies, action implementation and recurrence.
- **AUTHORITY_BOUNDARY:** Investigators need independence and access; organisations must empower consumers to change upstream controls rather than only retrain operators.
- **CRITICISMS:** Systems analyses remain judgement-sensitive; “no root cause” must not become refusal to identify controllable mechanisms or accountability.
- **ANTI_CEREMONY_BOUNDARY:** A specific RCA diagram is optional; evidence-preserving causal discrimination and action linkage are the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** Broader causal analysis can conflict with timely action and named individual accountability.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Multi-factor causal investigation grounded in local rationality
- **LOSS_OR_HAZARD:** Recurrence because upstream design, feedback, workload, authority, incentives, interfaces and defences remain unchanged.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Multi-factor causal investigation grounded in local rationality.
- **CONTROL_ACTION:** Preserve evidence, build competing causal scenarios, test counterfactual control changes, distinguish contributing mechanisms and stop when additional evidence no longer changes action.
- **REQUIRED_FEEDBACK:** Timeline/state reconstruction, alternative explanations, missing/stale feedback, goal conflicts, control deficiencies, action implementation and recurrence.
- **PROCESS_MODEL_ASSUMPTION:** Timely access to technical/organisational evidence, multidisciplinary competence and separation between learning and inappropriate punishment.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Investigators need independence and access; organisations must empower consumers to change upstream controls rather than only retrain operators.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** A simple, directly observed and deterministically reproducible defect can be corrected without an elaborate sociotechnical investigation.
- **MATURE_FORM:** Investigate until the credible causal mechanisms needed to select and verify controls are sufficiently discriminated, without treating error labels as explanations.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Multi-factor causal investigation grounded in local rationality
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** A simple, directly observed and deterministically reproducible defect can be corrected without an elaborate sociotechnical investigation.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Investigate until the credible causal mechanisms needed to select and verify controls are sufficiently discriminated, without treating error labels as explanations.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** MODERATE — mechanism is coherent but depends on model scope and assumptions.
- **ACCIDENT_CASE_STRENGTH:** HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S063, S064, S076, S077, S109, S110; critical/contrary: S066, S107.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Multi-factor causal investigation grounded in local rationality, rather than only a proxy, component check or document status?
- When the trigger is present — Serious incidents, recurring near misses and unexplained control/interaction failures. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Timeline/state reconstruction, alternative explanations, missing/stale feedback, goal conflicts, control deficiencies, action implementation and recurrence. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Investigators need independence and access; organisations must empower consumers to change upstream controls rather than only retrain operators.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: A simple, directly observed and deterministically reproducible defect can be corrected without an elaborate sociotechnical investigation.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-041 — Corrective-action ownership, implementation and effectiveness verification

- **PROPERTY_ID:** ESS-041
- **PROPERTY_NAME:** Corrective-action ownership, implementation and effectiveness verification
- **LOSS_OR_HAZARD:** Repeat loss because recommendations have no capable consumer, address symptoms, are not implemented or create new hazards.
- **FAILURE_MODE:** Owner ambiguity, action inflation, output metrics, weak causal link, status self-report and no post-implementation observation.
- **MATURE_FORM:** No safety finding is closed merely by documentation: close the causal-control loop or explicitly record why no further action has decision value.
- **TRIGGER:** Material incidents, recurring precursors, audit findings and accepted safety recommendations.
- **CHEAP_PATH:** For a trivial directly fixed defect, the repair plus decisive regression check can close the action without a separate tracker.
- **REQUIRED_PRECONDITIONS:** Causal mechanism sufficiently understood, feasible action, named empowered owner, current configuration and measurable verification condition.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Implementation evidence, changed control performance, recurrence/precursors, side effects, overdue status and reason for closure.
- **AUTHORITY_BOUNDARY:** The owner must control resources/design/operations or have escalation; the investigator should not declare effectiveness solely from paperwork.
- **CRITICISMS:** Effectiveness is hard to infer for rare events; absence of recurrence over short exposure is weak evidence.
- **ANTI_CEREMONY_BOUNDARY:** An action database is optional; an empowered consumer and verified causal effect are not.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Corrective-action ownership, implementation and effectiveness verification
- **LOSS_OR_HAZARD:** Repeat loss because recommendations have no capable consumer, address symptoms, are not implemented or create new hazards.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Corrective-action ownership, implementation and effectiveness verification.
- **CONTROL_ACTION:** For each material mechanism, specify the control change and expected indicator, assign authority/resources, verify implementation, test effectiveness and monitor recurrence/side effects.
- **REQUIRED_FEEDBACK:** Implementation evidence, changed control performance, recurrence/precursors, side effects, overdue status and reason for closure.
- **PROCESS_MODEL_ASSUMPTION:** Causal mechanism sufficiently understood, feasible action, named empowered owner, current configuration and measurable verification condition.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** The owner must control resources/design/operations or have escalation; the investigator should not declare effectiveness solely from paperwork.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** For a trivial directly fixed defect, the repair plus decisive regression check can close the action without a separate tracker.
- **MATURE_FORM:** No safety finding is closed merely by documentation: close the causal-control loop or explicitly record why no further action has decision value.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Corrective-action ownership, implementation and effectiveness verification
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** For a trivial directly fixed defect, the repair plus decisive regression check can close the action without a separate tracker.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** No safety finding is closed merely by documentation: close the causal-control loop or explicitly record why no further action has decision value.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** MODERATE — mechanism is coherent but depends on model scope and assumptions.
- **ACCIDENT_CASE_STRENGTH:** HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S076, S078, S079, S093, S115; critical/contrary: S071, S072.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Corrective-action ownership, implementation and effectiveness verification, rather than only a proxy, component check or document status?
- When the trigger is present — Material incidents, recurring precursors, audit findings and accepted safety recommendations. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Implementation evidence, changed control performance, recurrence/precursors, side effects, overdue status and reason for closure. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: The owner must control resources/design/operations or have escalation; the investigator should not declare effectiveness solely from paperwork.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: For a trivial directly fixed defect, the repair plus decisive regression check can close the action without a separate tracker.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-042 — Leading indicators tied to explicit hazards and control performance

- **PROPERTY_ID:** ESS-042
- **PROPERTY_NAME:** Leading indicators tied to explicit hazards and control performance
- **LOSS_OR_HAZARD:** Latent degradation and migration toward hazard boundaries remain invisible until a severe event.
- **FAILURE_MODE:** Proxy gaming, indicator drift, Goodhart effects, missing denominators, unvalidated causal link and dashboard overload.
- **MATURE_FORM:** A leading indicator is retained only when its causal relevance, denominator, decision threshold and consumer remain credible.
- **TRIGGER:** Sparse-event, latent-failure or slowly degrading systems where incident rates provide delayed or statistically weak feedback.
- **CHEAP_PATH:** Use direct control-state inspection when available; do not create proxy metrics where a deterministic discriminator already answers the question.
- **REQUIRED_PRECONDITIONS:** Explicit causal hypothesis, reliable data and exposure denominator, stable semantics and authorised response.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Barrier availability, overdue proof tests, excursions, workload/override patterns, weak signals, exposure and decision response.
- **AUTHORITY_BOUNDARY:** An owner must be able to inspect, restrict, maintain or redesign on adverse trends and to retire misleading indicators.
- **CRITICISMS:** Evidence linking broad culture/leading scores to accident prevention is mixed; indicators are model-dependent and can be gamed.
- **ANTI_CEREMONY_BOUNDARY:** A KPI dashboard is not a property; timely control-state information that changes action is.
- **POSSIBLE_CONFLICTING_PROPERTY:** Indicator coverage can conflict with metric burden and Goodhart effects.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Leading indicators tied to explicit hazards and control performance
- **LOSS_OR_HAZARD:** Latent degradation and migration toward hazard boundaries remain invisible until a severe event.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Leading indicators tied to explicit hazards and control performance.
- **CONTROL_ACTION:** Derive a small set of indicators from the hazard/control model, state expected direction and threshold, validate against operations and pair every threshold with a decision.
- **REQUIRED_FEEDBACK:** Barrier availability, overdue proof tests, excursions, workload/override patterns, weak signals, exposure and decision response.
- **PROCESS_MODEL_ASSUMPTION:** Explicit causal hypothesis, reliable data and exposure denominator, stable semantics and authorised response.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** An owner must be able to inspect, restrict, maintain or redesign on adverse trends and to retire misleading indicators.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Use direct control-state inspection when available; do not create proxy metrics where a deterministic discriminator already answers the question.
- **MATURE_FORM:** A leading indicator is retained only when its causal relevance, denominator, decision threshold and consumer remain credible.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Leading indicators tied to explicit hazards and control performance
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Use direct control-state inspection when available; do not create proxy metrics where a deterministic discriminator already answers the question.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** A leading indicator is retained only when its causal relevance, denominator, decision threshold and consumer remain credible.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** MODERATE — mechanism is coherent but depends on model scope and assumptions.
- **ACCIDENT_CASE_STRENGTH:** HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S062, S097, S104; critical/contrary: S071, S072, S074.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Leading indicators tied to explicit hazards and control performance, rather than only a proxy, component check or document status?
- When the trigger is present — Sparse-event, latent-failure or slowly degrading systems where incident rates provide delayed or statistically weak feedback. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Barrier availability, overdue proof tests, excursions, workload/override patterns, weak signals, exposure and decision response. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: An owner must be able to inspect, restrict, maintain or redesign on adverse trends and to retire misleading indicators.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Use direct control-state inspection when available; do not create proxy metrics where a deterministic discriminator already answers the question.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-043 — Organisational control, incentives and production-pressure analysis

- **PROPERTY_ID:** ESS-043
- **PROPERTY_NAME:** Organisational control, incentives and production-pressure analysis
- **LOSS_OR_HAZARD:** Catastrophic loss arising from normal organisational adaptation, resource choices and authority/information failures.
- **FAILURE_MODE:** Conflicting goals, diffused responsibility, normalisation, weak feedback upward, authority gradients and metrics that externalise risk.
- **MATURE_FORM:** Analyse and change the upstream decisions and feedback loops that shape risk, while retaining named accountability for controllable choices.
- **TRIGGER:** Complex organisations, outsourced supply chains, long operations, high schedule pressure and hazards spanning multiple management levels.
- **CHEAP_PATH:** Do not invent culture programmes for a simple local technical defect; correct the direct mechanism and verify it.
- **REQUIRED_PRECONDITIONS:** Access to real work and decision data, leadership willingness to expose tradeoffs, protected reporting and feasible upstream controls.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Staffing/workload, deferred maintenance, waivers, schedule overrides, unresolved findings, reporting quality, barrier health and escalation outcomes.
- **AUTHORITY_BOUNDARY:** Leaders controlling resources and priorities must own safety consequences; frontline responsibility requires matching authority.
- **CRITICISMS:** Organisational causation is difficult to quantify and broad systems explanations can obscure specific decision responsibility.
- **ANTI_CEREMONY_BOUNDARY:** A culture survey or values statement is not the property; decision-relevant organisational control is.
- **POSSIBLE_CONFLICTING_PROPERTY:** Constraint enforcement can conflict with mission/production; unmanaged conflict creates workarounds.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Organisational control, incentives and production-pressure analysis
- **LOSS_OR_HAZARD:** Catastrophic loss arising from normal organisational adaptation, resource choices and authority/information failures.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Organisational control, incentives and production-pressure analysis.
- **CONTROL_ACTION:** Map decision/control paths and incentives, identify where authority and safety information diverge, install escalation/stop rights and monitor boundary migration.
- **REQUIRED_FEEDBACK:** Staffing/workload, deferred maintenance, waivers, schedule overrides, unresolved findings, reporting quality, barrier health and escalation outcomes.
- **PROCESS_MODEL_ASSUMPTION:** Access to real work and decision data, leadership willingness to expose tradeoffs, protected reporting and feasible upstream controls.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Leaders controlling resources and priorities must own safety consequences; frontline responsibility requires matching authority.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Do not invent culture programmes for a simple local technical defect; correct the direct mechanism and verify it.
- **MATURE_FORM:** Analyse and change the upstream decisions and feedback loops that shape risk, while retaining named accountability for controllable choices.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Organisational control, incentives and production-pressure analysis
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Do not invent culture programmes for a simple local technical defect; correct the direct mechanism and verify it.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Analyse and change the upstream decisions and feedback loops that shape risk, while retaining named accountability for controllable choices.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** MODERATE — mechanism is coherent but depends on model scope and assumptions.
- **ACCIDENT_CASE_STRENGTH:** HIGH — major investigations repeatedly identify authority, incentive, communication and adaptation mechanisms.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** MODERATE — observational evidence is substantial; causal identification and transfer remain difficult.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S062, S065, S067, S081, S082, S085, S087, S091; critical/contrary: S066, S071, S072.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Organisational control, incentives and production-pressure analysis, rather than only a proxy, component check or document status?
- When the trigger is present — Complex organisations, outsourced supply chains, long operations, high schedule pressure and hazards spanning multiple management levels. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Staffing/workload, deferred maintenance, waivers, schedule overrides, unresolved findings, reporting quality, barrier health and escalation outcomes. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Leaders controlling resources and priorities must own safety consequences; frontline responsibility requires matching authority.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Do not invent culture programmes for a simple local technical defect; correct the direct mechanism and verify it.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-044 — Supplier and contractor boundary assurance with change notification

- **PROPERTY_ID:** ESS-044
- **PROPERTY_NAME:** Supplier and contractor boundary assurance with change notification
- **LOSS_OR_HAZARD:** Loss from hidden component behaviour, interface mismatch, counterfeit/substituted part, evidence opacity or divided authority.
- **FAILURE_MODE:** Contract gaps, proprietary barriers, incompatible hazard models, unmanaged subcontractors and responsibility without control.
- **MATURE_FORM:** Match supplier assurance to system consequence and interface uncertainty, but keep the integrator responsible for composed safety.
- **TRIGGER:** Safety-relevant purchased software/hardware, outsourced operations/maintenance and multi-tier supply chains.
- **CHEAP_PATH:** Commodity low-consequence components with a decisive acceptance test can use that test rather than imposing a full supplier safety system.
- **REQUIRED_PRECONDITIONS:** Clear technical/contract boundary, component criticality, integration testability, configuration provenance and enforceable notification terms.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Supplier versions, deviations, anomalies, process/evidence changes, interface conformance and field performance.
- **AUTHORITY_BOUNDARY:** The integrator must retain system-level acceptance authority; suppliers need authority/resources to disclose and correct defects.
- **CRITICISMS:** Contracts cannot reveal unknown interactions or guarantee candour; excessive requirements can reduce supplier diversity and agility.
- **ANTI_CEREMONY_BOUNDARY:** A supplier certificate is not the property; current boundary evidence, notification and integration control are.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Supplier and contractor boundary assurance with change notification
- **LOSS_OR_HAZARD:** Loss from hidden component behaviour, interface mismatch, counterfeit/substituted part, evidence opacity or divided authority.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Supplier and contractor boundary assurance with change notification.
- **CONTROL_ACTION:** Allocate hazard-linked obligations and interface assumptions, require evidence and change/anomaly notification, verify integration and retain integrator accountability.
- **REQUIRED_FEEDBACK:** Supplier versions, deviations, anomalies, process/evidence changes, interface conformance and field performance.
- **PROCESS_MODEL_ASSUMPTION:** Clear technical/contract boundary, component criticality, integration testability, configuration provenance and enforceable notification terms.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** The integrator must retain system-level acceptance authority; suppliers need authority/resources to disclose and correct defects.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Commodity low-consequence components with a decisive acceptance test can use that test rather than imposing a full supplier safety system.
- **MATURE_FORM:** Match supplier assurance to system consequence and interface uncertainty, but keep the integrator responsible for composed safety.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Supplier and contractor boundary assurance with change notification
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Commodity low-consequence components with a decisive acceptance test can use that test rather than imposing a full supplier safety system.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Match supplier assurance to system consequence and interface uncertainty, but keep the integrator responsible for composed safety.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S027, S029, S042, S052, S054, S055; critical/contrary: S048, S095.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Supplier and contractor boundary assurance with change notification, rather than only a proxy, component check or document status?
- When the trigger is present — Safety-relevant purchased software/hardware, outsourced operations/maintenance and multi-tier supply chains. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Supplier versions, deviations, anomalies, process/evidence changes, interface conformance and field performance. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: The integrator must retain system-level acceptance authority; suppliers need authority/resources to disclose and correct defects.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Commodity low-consequence components with a decisive acceptance test can use that test rather than imposing a full supplier safety system.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-045 — Operational monitoring and adaptive safety-envelope governance

- **PROPERTY_ID:** ESS-045
- **PROPERTY_NAME:** Operational monitoring and adaptive safety-envelope governance
- **LOSS_OR_HAZARD:** Loss from envelope excursion, unobserved degradation, novel context or adaptation that invalidates prior assurance.
- **FAILURE_MODE:** Incomplete state sensing, concept drift, threshold gaming, delayed feedback, adaptation beyond authority and false belief that monitoring covers unknowns.
- **MATURE_FORM:** Permit adaptation only inside an observable, hazard-linked and authority-bounded envelope, with fallback and change-aware re-assurance.
- **TRIGGER:** Long-lived, variable-environment, autonomous or rapidly updated systems where predeployment evidence cannot cover all operational states.
- **CHEAP_PATH:** Stable bounded systems with direct deterministic protection may only need periodic checks; continuous dashboards are unnecessary.
- **REQUIRED_PRECONDITIONS:** Validated envelope, trustworthy telemetry, anomaly/assumption monitors, safe fallback and authority to intervene or revise constraints.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Envelope variables, assumption validity, control effectiveness, anomalies, drift, exposure and recovery performance.
- **AUTHORITY_BOUNDARY:** Operations must have stop/degrade authority; adaptation outside the assured envelope requires explicit change/risk authority.
- **CRITICISMS:** Resilience concepts can be vague and monitoring cannot guarantee discovery of unknown hazards; intervention itself can destabilise service.
- **ANTI_CEREMONY_BOUNDARY:** “Resilience” language or a dashboard is not enough; explicit constraints, feedback, decisions and limits are required.
- **POSSIBLE_CONFLICTING_PROPERTY:** Adaptive operation conflicts with fixed configuration identity and predeployment assurance.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Operational monitoring and adaptive safety-envelope governance
- **LOSS_OR_HAZARD:** Loss from envelope excursion, unobserved degradation, novel context or adaptation that invalidates prior assurance.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Operational monitoring and adaptive safety-envelope governance.
- **CONTROL_ACTION:** Define observable envelope variables and assumptions, detect excursions, restrict/degrade or learn within authorised bounds, and re-assure material adaptations.
- **REQUIRED_FEEDBACK:** Envelope variables, assumption validity, control effectiveness, anomalies, drift, exposure and recovery performance.
- **PROCESS_MODEL_ASSUMPTION:** Validated envelope, trustworthy telemetry, anomaly/assumption monitors, safe fallback and authority to intervene or revise constraints.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Operations must have stop/degrade authority; adaptation outside the assured envelope requires explicit change/risk authority.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Stable bounded systems with direct deterministic protection may only need periodic checks; continuous dashboards are unnecessary.
- **MATURE_FORM:** Permit adaptation only inside an observable, hazard-linked and authority-bounded envelope, with fallback and change-aware re-assurance.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Operational monitoring and adaptive safety-envelope governance
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Stable bounded systems with direct deterministic protection may only need periodic checks; continuous dashboards are unnecessary.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Permit adaptation only inside an observable, hazard-linked and authority-bounded envelope, with fallback and change-aware re-assurance.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S047, S055, S062, S069, S070, S098, S103, S104; critical/contrary: S070, S111.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Operational monitoring and adaptive safety-envelope governance, rather than only a proxy, component check or document status?
- When the trigger is present — Long-lived, variable-environment, autonomous or rapidly updated systems where predeployment evidence cannot cover all operational states. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Envelope variables, assumption validity, control effectiveness, anomalies, drift, exposure and recovery performance. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Operations must have stop/degrade authority; adaptation outside the assured envelope requires explicit change/risk authority.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Stable bounded systems with direct deterministic protection may only need periodic checks; continuous dashboards are unnecessary.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-046 — Cheap authoritative discriminator for low-consequence reversible work

- **PROPERTY_ID:** ESS-046
- **PROPERTY_NAME:** Cheap authoritative discriminator for low-consequence reversible work
- **LOSS_OR_HAZARD:** Indirect safety loss from delayed repair/service, attention dilution and procedural noncompliance; wasted cost without improved discrimination.
- **FAILURE_MODE:** Process is triggered by label, document type or change count rather than credible loss, reversibility and uncertainty.
- **MATURE_FORM:** Use the least costly discriminator that conclusively controls the credible loss; never perform a safety ritual solely because its template exists.
- **TRIGGER:** Local, cheap, reversible, immediately observable work with stable assumptions and an authoritative deterministic discriminator.
- **CHEAP_PATH:** This property is itself the cheap path; it does not apply when consequence, irreversibility, coupling, latent effects or uncertain interactions are material.
- **REQUIRED_PRECONDITIONS:** The discriminator actually covers the safety question, the result is observable and rollback/containment remains available.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Check result, exact local configuration, rollback success if used and evidence that assumptions did not widen.
- **AUTHORITY_BOUNDARY:** Ordinary engineering authority may act within bounded delegation; anyone detecting scope expansion can escalate.
- **CRITICISMS:** Tailoring can be gamed and no deterministic check is authoritative outside its proven scope.
- **ANTI_CEREMONY_BOUNDARY:** No special artefact is required beyond sufficient evidence of scope, result and escalation conditions.
- **POSSIBLE_CONFLICTING_PROPERTY:** Cheap-path tailoring conflicts with hazard-completeness caution when scope is uncertain.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Cheap authoritative discriminator for low-consequence reversible work
- **LOSS_OR_HAZARD:** Indirect safety loss from delayed repair/service, attention dilution and procedural noncompliance; wasted cost without improved discrimination.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Cheap authoritative discriminator for low-consequence reversible work.
- **CONTROL_ACTION:** Classify consequence and scope, apply the decisive test/guard, record only necessary identity/result, and define escalation triggers for ambiguity or coupling.
- **REQUIRED_FEEDBACK:** Check result, exact local configuration, rollback success if used and evidence that assumptions did not widen.
- **PROCESS_MODEL_ASSUMPTION:** The discriminator actually covers the safety question, the result is observable and rollback/containment remains available.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Ordinary engineering authority may act within bounded delegation; anyone detecting scope expansion can escalate.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** This property is itself the cheap path; it does not apply when consequence, irreversibility, coupling, latent effects or uncertain interactions are material.
- **MATURE_FORM:** Use the least costly discriminator that conclusively controls the credible loss; never perform a safety ritual solely because its template exists.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Cheap authoritative discriminator for low-consequence reversible work
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** This property is itself the cheap path; it does not apply when consequence, irreversibility, coupling, latent effects or uncertain interactions are material.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Use the least costly discriminator that conclusively controls the credible loss; never perform a safety ritual solely because its template exists.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S029, S035, S098; critical/contrary: S038, S073, S074.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Cheap authoritative discriminator for low-consequence reversible work, rather than only a proxy, component check or document status?
- When the trigger is present — Local, cheap, reversible, immediately observable work with stable assumptions and an authoritative deterministic discriminator. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Check result, exact local configuration, rollback success if used and evidence that assumptions did not widen. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Ordinary engineering authority may act within bounded delegation; anyone detecting scope expansion can escalate.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: This property is itself the cheap path; it does not apply when consequence, irreversibility, coupling, latent effects or uncertain interactions are material.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-047 — Retirement of controls whose hazard or decision consumer has disappeared

- **PROPERTY_ID:** ESS-047
- **PROPERTY_NAME:** Retirement of controls whose hazard or decision consumer has disappeared
- **LOSS_OR_HAZARD:** Safety attention dilution, alarm fatigue, workaround, unavailable service or false belief that an obsolete control remains protective.
- **FAILURE_MODE:** No ownership/expiry, changed architecture, orphaned requirement, vanished consumer and process incentives rewarding control count.
- **MATURE_FORM:** Retain a safety control only while a current hazard/decision link and justified expected value remain; remove it with the same causal discipline used to add it.
- **TRIGGER:** Long-lived systems with substantial change, accumulated waivers, alarms, checklists, reports or certification artefacts.
- **CHEAP_PATH:** Do not run a retirement review for a transient local check that naturally ends with the task.
- **REQUIRED_PRECONDITIONS:** Current hazard/configuration model, evidence of non-use or replacement, dependency analysis and authority to remove safely.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Consumer use, action triggered, false-positive/bypass burden, control effectiveness, dependencies and post-retirement anomalies.
- **AUTHORITY_BOUNDARY:** The control owner and affected risk/operations authority must approve removal; users need a path to reveal hidden dependence.
- **CRITICISMS:** Absence of recent activation may reflect successful prevention or rare demand, not obsolescence.
- **ANTI_CEREMONY_BOUNDARY:** A control register is optional; live ownership, consumer and retirement logic are the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** Control retirement conflicts with preserving dormant rare-demand barriers and historical evidence.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Retirement of controls whose hazard or decision consumer has disappeared
- **LOSS_OR_HAZARD:** Safety attention dilution, alarm fatigue, workaround, unavailable service or false belief that an obsolete control remains protective.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Retirement of controls whose hazard or decision consumer has disappeared.
- **CONTROL_ACTION:** Require each control to retain a hazard/constraint link, owner, consumer and effectiveness signal; decommission through impact analysis and verify no residual dependency.
- **REQUIRED_FEEDBACK:** Consumer use, action triggered, false-positive/bypass burden, control effectiveness, dependencies and post-retirement anomalies.
- **PROCESS_MODEL_ASSUMPTION:** Current hazard/configuration model, evidence of non-use or replacement, dependency analysis and authority to remove safely.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** The control owner and affected risk/operations authority must approve removal; users need a path to reveal hidden dependence.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Do not run a retirement review for a transient local check that naturally ends with the task.
- **MATURE_FORM:** Retain a safety control only while a current hazard/decision link and justified expected value remain; remove it with the same causal discipline used to add it.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Retirement of controls whose hazard or decision consumer has disappeared
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Do not run a retirement review for a transient local check that naturally ends with the task.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Retain a safety control only while a current hazard/decision link and justified expected value remain; remove it with the same causal discipline used to add it.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S042, S047, S075, S095; critical/contrary: S071, S074.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Retirement of controls whose hazard or decision consumer has disappeared, rather than only a proxy, component check or document status?
- When the trigger is present — Long-lived systems with substantial change, accumulated waivers, alarms, checklists, reports or certification artefacts. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Consumer use, action triggered, false-positive/bypass burden, control effectiveness, dependencies and post-retirement anomalies. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: The control owner and affected risk/operations authority must approve removal; users need a path to reveal hidden dependence.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Do not run a retirement review for a transient local check that naturally ends with the task.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-048 — Live decision consumer for every safety artefact and control

- **PROPERTY_ID:** ESS-048
- **PROPERTY_NAME:** Live decision consumer for every safety artefact and control
- **LOSS_OR_HAZARD:** Uncontrolled hazard masked by document completion, plus attention/cost displaced from effective controls.
- **FAILURE_MODE:** No consumer, no authority, unclear decision threshold, stale update cycle and metrics rewarding artefact quantity.
- **MATURE_FORM:** Every artefact must earn existence through a current or credibly latent consequential decision and an owner who can act on it.
- **TRIGGER:** Any recurring safety analysis, review, metric, report, case or control.
- **CHEAP_PATH:** Do not create a separate artefact when the decisive information is already embedded in an authoritative engineering/operational control.
- **REQUIRED_PRECONDITIONS:** Real decision need, current evidence, accessible representation and consumer authority.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Decision made, challenge raised, action/acceptance changed, use frequency, stale age and unresolved consumer feedback.
- **AUTHORITY_BOUNDARY:** The consumer must be able to act or escalate; the producer cannot substitute document delivery for control.
- **CRITICISMS:** Some assurance artefacts serve latent legal/public accountability and rare future decisions, so immediate use alone is not sufficient.
- **ANTI_CEREMONY_BOUNDARY:** No document format is required; durable current decision information is.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Live decision consumer for every safety artefact and control
- **LOSS_OR_HAZARD:** Uncontrolled hazard masked by document completion, plus attention/cost displaced from effective controls.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Live decision consumer for every safety artefact and control.
- **CONTROL_ACTION:** State the decision, consumer, trigger and required information before producing the artefact; observe use and retire or redesign if it does not change action.
- **REQUIRED_FEEDBACK:** Decision made, challenge raised, action/acceptance changed, use frequency, stale age and unresolved consumer feedback.
- **PROCESS_MODEL_ASSUMPTION:** Real decision need, current evidence, accessible representation and consumer authority.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** The consumer must be able to act or escalate; the producer cannot substitute document delivery for control.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Do not create a separate artefact when the decisive information is already embedded in an authoritative engineering/operational control.
- **MATURE_FORM:** Every artefact must earn existence through a current or credibly latent consequential decision and an owner who can act on it.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Live decision consumer for every safety artefact and control
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Do not create a separate artefact when the decisive information is already embedded in an authoritative engineering/operational control.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Every artefact must earn existence through a current or credibly latent consequential decision and an owner who can act on it.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S042, S044, S078, S079; critical/contrary: S048, S107.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Live decision consumer for every safety artefact and control, rather than only a proxy, component check or document status?
- When the trigger is present — Any recurring safety analysis, review, metric, report, case or control. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Decision made, challenge raised, action/acceptance changed, use frequency, stale age and unresolved consumer feedback. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: The consumer must be able to act or escalate; the producer cannot substitute document delivery for control.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Do not create a separate artefact when the decisive information is already embedded in an authoritative engineering/operational control.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-049 — Hazard-control hierarchy favouring elimination and engineered control

- **PROPERTY_ID:** ESS-049
- **PROPERTY_NAME:** Hazard-control hierarchy favouring elimination and engineered control
- **LOSS_OR_HAZARD:** Preventable exposure or catastrophic demand on humans/procedures after a feasible stronger control was omitted.
- **FAILURE_MODE:** Cost/schedule bias, late analysis, overconfidence in training, new hazards introduced by redesign and absolute hierarchy use without context.
- **MATURE_FORM:** Eliminate or physically constrain credible hazards where practicable; justify reliance on weaker human/procedural layers and analyse the hazards controls create.
- **TRIGGER:** Identified hazards with feasible design, substitution, guarding, interlock, isolation or exposure-reduction options.
- **CHEAP_PATH:** No hierarchy exercise is needed when the hazard is absent or a simple direct constraint already eliminates it.
- **REQUIRED_PRECONDITIONS:** Early design influence, feasible alternatives, system-level tradeoff analysis and authority/resources to change architecture.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Hazard presence, barrier demand, human/procedural dependence, bypass, exposure and side effects of stronger controls.
- **AUTHORITY_BOUNDARY:** Design/risk authority must be able to reject administrative substitution for feasible engineering control.
- **CRITICISMS:** No control class is infallible; engineered automation can create interaction hazards and fail-operational contexts complicate the order.
- **ANTI_CEREMONY_BOUNDARY:** A hierarchy poster is ceremony; actual design-option search and justified residual dependence are the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** Engineered automation can conflict with human adaptability and create unsafe control interactions.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Hazard-control hierarchy favouring elimination and engineered control
- **LOSS_OR_HAZARD:** Preventable exposure or catastrophic demand on humans/procedures after a feasible stronger control was omitted.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Hazard-control hierarchy favouring elimination and engineered control.
- **CONTROL_ACTION:** Search controls in strength order, document why stronger options are infeasible or harmful, and monitor residual lower-level controls.
- **REQUIRED_FEEDBACK:** Hazard presence, barrier demand, human/procedural dependence, bypass, exposure and side effects of stronger controls.
- **PROCESS_MODEL_ASSUMPTION:** Early design influence, feasible alternatives, system-level tradeoff analysis and authority/resources to change architecture.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Design/risk authority must be able to reject administrative substitution for feasible engineering control.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** No hierarchy exercise is needed when the hazard is absent or a simple direct constraint already eliminates it.
- **MATURE_FORM:** Eliminate or physically constrain credible hazards where practicable; justify reliance on weaker human/procedural layers and analyse the hazards controls create.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Hazard-control hierarchy favouring elimination and engineered control
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** No hierarchy exercise is needed when the hazard is absent or a simple direct constraint already eliminates it.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Eliminate or physically constrain credible hazards where practicable; justify reliance on weaker human/procedural layers and analyse the hazards controls create.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S033, S034, S094; critical/contrary: S058, S073.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Hazard-control hierarchy favouring elimination and engineered control, rather than only a proxy, component check or document status?
- When the trigger is present — Identified hazards with feasible design, substitution, guarding, interlock, isolation or exposure-reduction options. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Hazard presence, barrier demand, human/procedural dependence, bypass, exposure and side effects of stronger controls. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Design/risk authority must be able to reject administrative substitution for feasible engineering control.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: No hierarchy exercise is needed when the hazard is absent or a simple direct constraint already eliminates it.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-050 — Safety margins, operating envelopes and boundary separation

- **PROPERTY_ID:** ESS-050
- **PROPERTY_NAME:** Safety margins, operating envelopes and boundary separation
- **LOSS_OR_HAZARD:** Abrupt transition into an unrecoverable hazardous state after small variation, delay or latent degradation.
- **FAILURE_MODE:** Unknown boundary, optimistic model, cumulative erosion, hidden interactions, production pressure and margin consumed by change.
- **MATURE_FORM:** Maintain enough observable separation from hazardous boundaries to absorb credible uncertainty and response latency, while revising limits when evidence changes.
- **TRIGGER:** High-energy, structural, thermal, control or capacity hazards with identifiable boundaries and cliff-edge consequences.
- **CHEAP_PATH:** For a low-consequence reversible state with immediate deterministic feedback, ordinary tolerance checks may suffice.
- **REQUIRED_PRECONDITIONS:** A credible boundary model, calibrated measurement, operational authority and recovery/containment before limit crossing.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Distance to limit, uncertainty, rate of approach, ageing/degradation, excursions, recovery time and barrier availability.
- **AUTHORITY_BOUNDARY:** Operators/controllers must be able to reduce demand, stop or degrade; change authority owns margin allocation.
- **CRITICISMS:** Margins can mask design weakness or reduce necessary service; not all sociotechnical hazards have a scalar boundary.
- **ANTI_CEREMONY_BOUNDARY:** A fixed safety factor is domain-specific; controlled separation and margin evidence are the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** Large margins can conflict with availability and induce bypass or workaround.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Safety margins, operating envelopes and boundary separation
- **LOSS_OR_HAZARD:** Abrupt transition into an unrecoverable hazardous state after small variation, delay or latent degradation.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Safety margins, operating envelopes and boundary separation.
- **CONTROL_ACTION:** Define hazard-linked limits and uncertainty allowance, instrument relevant variables, restrict excursions and reassess margins after change/degradation.
- **REQUIRED_FEEDBACK:** Distance to limit, uncertainty, rate of approach, ageing/degradation, excursions, recovery time and barrier availability.
- **PROCESS_MODEL_ASSUMPTION:** A credible boundary model, calibrated measurement, operational authority and recovery/containment before limit crossing.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Operators/controllers must be able to reduce demand, stop or degrade; change authority owns margin allocation.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** For a low-consequence reversible state with immediate deterministic feedback, ordinary tolerance checks may suffice.
- **MATURE_FORM:** Maintain enough observable separation from hazardous boundaries to absorb credible uncertainty and response latency, while revising limits when evidence changes.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Safety margins, operating envelopes and boundary separation
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** For a low-consequence reversible state with immediate deterministic feedback, ordinary tolerance checks may suffice.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Maintain enough observable separation from hazardous boundaries to absorb credible uncertainty and response latency, while revising limits when evidence changes.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_LIMITS_MODERATE_FOR_ESTIMATES — mathematical critiques are strong; quantitative estimates remain data/model sensitive.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — decision-quality comparisons are limited and domain dependent.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S040, S056, S062, S103, S105; critical/contrary: S068, S073.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Safety margins, operating envelopes and boundary separation, rather than only a proxy, component check or document status?
- When the trigger is present — High-energy, structural, thermal, control or capacity hazards with identifiable boundaries and cliff-edge consequences. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Distance to limit, uncertainty, rate of approach, ageing/degradation, excursions, recovery time and barrier availability. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Operators/controllers must be able to reduce demand, stop or degrade; change authority owns margin allocation.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: For a low-consequence reversible state with immediate deterministic feedback, ordinary tolerance checks may suffice.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-051 — Explicit assumption validity and monitoring

- **PROPERTY_ID:** ESS-051
- **PROPERTY_NAME:** Explicit assumption validity and monitoring
- **LOSS_OR_HAZARD:** Unsafe behaviour outside the analysed context, common-mode failure or false assurance caused by premise drift.
- **FAILURE_MODE:** Hidden assumptions, non-observable premises, too many unprioritised assumptions and monitoring the same source that created the assumption.
- **MATURE_FORM:** A safety claim is valid only while its material assumptions are evidenced; monitor the few premises whose failure can change control or acceptance.
- **TRIGGER:** Novel, changing, autonomous, outsourced or environment-sensitive systems and any reused safety evidence.
- **CHEAP_PATH:** Do not create a register for obvious transient facts already enforced by a deterministic check; record only assumptions whose failure changes a decision.
- **REQUIRED_PRECONDITIONS:** Claim/hazard model, observable discriminators or periodic revalidation, configuration linkage and action authority.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Premise status, environmental range, interface/provider behaviour, data drift, independence evidence and violations.
- **AUTHORITY_BOUNDARY:** Assumption owners and operators must be able to restrict use, escalate or change the case when validity is uncertain.
- **CRITICISMS:** Unknown unknowns remain outside the register and monitoring can be circular or lagging.
- **ANTI_CEREMONY_BOUNDARY:** An assumption spreadsheet is optional; explicit, current and actionable premise state is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Explicit assumption validity and monitoring
- **LOSS_OR_HAZARD:** Unsafe behaviour outside the analysed context, common-mode failure or false assurance caused by premise drift.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Explicit assumption validity and monitoring.
- **CONTROL_ACTION:** Identify claim-critical assumptions, assign evidence/owner/validity period, monitor observable ones and trigger restriction or reassessment on violation.
- **REQUIRED_FEEDBACK:** Premise status, environmental range, interface/provider behaviour, data drift, independence evidence and violations.
- **PROCESS_MODEL_ASSUMPTION:** Claim/hazard model, observable discriminators or periodic revalidation, configuration linkage and action authority.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Assumption owners and operators must be able to restrict use, escalate or change the case when validity is uncertain.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Do not create a register for obvious transient facts already enforced by a deterministic check; record only assumptions whose failure changes a decision.
- **MATURE_FORM:** A safety claim is valid only while its material assumptions are evidenced; monitor the few premises whose failure can change control or acceptance.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Explicit assumption validity and monitoring
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Do not create a register for obvious transient facts already enforced by a deterministic check; record only assumptions whose failure changes a decision.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** A safety claim is valid only while its material assumptions are evidenced; monitor the few premises whose failure can change control or acceptance.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S018, S042, S044, S047, S052, S055, S062; critical/contrary: S048, S070.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Explicit assumption validity and monitoring, rather than only a proxy, component check or document status?
- When the trigger is present — Novel, changing, autonomous, outsourced or environment-sensitive systems and any reused safety evidence. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Premise status, environmental range, interface/provider behaviour, data drift, independence evidence and violations. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Assumption owners and operators must be able to restrict use, escalate or change the case when validity is uncertain.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Do not create a register for obvious transient facts already enforced by a deterministic check; record only assumptions whose failure changes a decision.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-052 — Durable current hazard, constraint and decision state

- **PROPERTY_ID:** ESS-052
- **PROPERTY_NAME:** Durable current hazard, constraint and decision state
- **LOSS_OR_HAZARD:** Known hazard reappears or remains uncontrolled because organisational memory and decision status are stale or fragmented.
- **FAILURE_MODE:** Spreadsheet rot, duplicate IDs, ambiguous closure, no consumer, status without evidence and poor configuration/change linkage.
- **MATURE_FORM:** Preserve current decision-relevant hazard/control memory in any implementation that exposes ownership, evidence, assumptions, change and residual acceptance.
- **TRIGGER:** Long-lived, multi-team or regulated systems and hazards requiring multiple controls/decisions over time.
- **CHEAP_PATH:** A local ephemeral hazard fully eliminated and verified can be recorded in the ordinary work item; a dedicated log is unnecessary.
- **REQUIRED_PRECONDITIONS:** Clear semantics, ownership, configuration identity, change triggers and a live decision consumer.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Control/evidence status, owner/acceptance, configuration, open scenarios, incidents, changes and review/expiry dates.
- **AUTHORITY_BOUNDARY:** Hazard/control owners and acceptance authority must be named; unresolved hazards cannot disappear through administrative closure.
- **CRITICISMS:** No log establishes hazard completeness or control effectiveness; it can become a powerful compliance theatre.
- **ANTI_CEREMONY_BOUNDARY:** A spreadsheet or prescribed schema is not required; durable current semantic state is.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Durable current hazard, constraint and decision state
- **LOSS_OR_HAZARD:** Known hazard reappears or remains uncontrolled because organisational memory and decision status are stale or fragmented.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Durable current hazard, constraint and decision state.
- **CONTROL_ACTION:** Maintain the minimum durable state needed to understand current hazard/control/acceptance closure; update through change and retire obsolete entries explicitly.
- **REQUIRED_FEEDBACK:** Control/evidence status, owner/acceptance, configuration, open scenarios, incidents, changes and review/expiry dates.
- **PROCESS_MODEL_ASSUMPTION:** Clear semantics, ownership, configuration identity, change triggers and a live decision consumer.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Hazard/control owners and acceptance authority must be named; unresolved hazards cannot disappear through administrative closure.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** A local ephemeral hazard fully eliminated and verified can be recorded in the ordinary work item; a dedicated log is unnecessary.
- **MATURE_FORM:** Preserve current decision-relevant hazard/control memory in any implementation that exposes ownership, evidence, assumptions, change and residual acceptance.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Durable current hazard, constraint and decision state
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** A local ephemeral hazard fully eliminated and verified can be recorded in the ordinary work item; a dedicated log is unnecessary.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Preserve current decision-relevant hazard/control memory in any implementation that exposes ownership, evidence, assumptions, change and residual acceptance.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_ARGUMENT_STRUCTURE_MODERATE_FOR_SYSTEM_TRUTH — logic can expose gaps but cannot make premises/evidence true.
- **ACCIDENT_CASE_STRENGTH:** HIGH — Nimrod and other cases directly show coherent or voluminous assurance failing to represent the actual system.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S042, S047, S095; critical/contrary: S048, S107.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Durable current hazard, constraint and decision state, rather than only a proxy, component check or document status?
- When the trigger is present — Long-lived, multi-team or regulated systems and hazards requiring multiple controls/decisions over time. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Control/evidence status, owner/acceptance, configuration, open scenarios, incidents, changes and review/expiry dates. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Hazard/control owners and acceptance authority must be named; unresolved hazards cannot disappear through administrative closure.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: A local ephemeral hazard fully eliminated and verified can be recorded in the ordinary work item; a dedicated log is unnecessary.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-053 — Integrated verification that a safety control achieves the intended state

- **PROPERTY_ID:** ESS-053
- **PROPERTY_NAME:** Integrated verification that a safety control achieves the intended state
- **LOSS_OR_HAZARD:** Hazard remains or recurs despite nominally verified requirements and components.
- **FAILURE_MODE:** Mocked interfaces, shared test oracle, unrealistic environment, untested failure/degraded modes and command-echo feedback.
- **MATURE_FORM:** A control is accepted only when current evidence shows that it drives and maintains the intended safe process state under relevant conditions.
- **TRIGGER:** Consequential interlocks, shutdown, autonomous control, recovery and multi-component protective functions.
- **CHEAP_PATH:** A single local direct test suffices when the control path is simple, fully observable and reversible.
- **REQUIRED_PRECONDITIONS:** Testable state criteria, representative configuration/environment, safe test containment and independent observation where warranted.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Trigger, command, timing, actuation, process state, feedback semantics, degraded modes and post-control stability.
- **AUTHORITY_BOUNDARY:** Verification authority needs access across component/organisational boundaries and power to block acceptance.
- **CRITICISMS:** Testing cannot cover all interactions and formal/model evidence is still needed for rare or dangerous states.
- **ANTI_CEREMONY_BOUNDARY:** A test report is not the property; hazard-linked state achievement and feedback confirmation are.
- **POSSIBLE_CONFLICTING_PROPERTY:** ESS-020 consequence/reversibility proportionality and ESS-046 cheap path constrain over-application; other system-specific tensions require adjudication.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Integrated verification that a safety control achieves the intended state
- **LOSS_OR_HAZARD:** Hazard remains or recurs despite nominally verified requirements and components.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Integrated verification that a safety control achieves the intended state.
- **CONTROL_ACTION:** Derive end-to-end acceptance criteria from the safety constraint, exercise representative normal/fault/transition scenarios and confirm physical/system state.
- **REQUIRED_FEEDBACK:** Trigger, command, timing, actuation, process state, feedback semantics, degraded modes and post-control stability.
- **PROCESS_MODEL_ASSUMPTION:** Testable state criteria, representative configuration/environment, safe test containment and independent observation where warranted.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** Verification authority needs access across component/organisational boundaries and power to block acceptance.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** A single local direct test suffices when the control path is simple, fully observable and reversible.
- **MATURE_FORM:** A control is accepted only when current evidence shows that it drives and maintains the intended safe process state under relevant conditions.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Integrated verification that a safety control achieves the intended state
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** A single local direct test suffices when the control path is simple, fully observable and reversible.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** A control is accepted only when current evidence shows that it drives and maintains the intended safe process state under relevant conditions.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S018, S049, S058, S099, S100, S102; critical/contrary: S050, S074.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Integrated verification that a safety control achieves the intended state, rather than only a proxy, component check or document status?
- When the trigger is present — Consequential interlocks, shutdown, autonomous control, recovery and multi-component protective functions. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Trigger, command, timing, actuation, process state, feedback semantics, degraded modes and post-control stability. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: Verification authority needs access across component/organisational boundaries and power to block acceptance.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: A single local direct test suffices when the control path is simple, fully observable and reversible.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

### ESS-054 — Safety management of lifecycle transitions and temporary configurations

- **PROPERTY_ID:** ESS-054
- **PROPERTY_NAME:** Safety management of lifecycle transitions and temporary configurations
- **LOSS_OR_HAZARD:** Loss during transition, test, construction, maintenance or retirement when normal controls are absent or roles/configurations are ambiguous.
- **FAILURE_MODE:** Temporary power/logic, incomplete systems, parallel old/new control, handoff, latent energy/material, unfamiliar work and restart pressure.
- **MATURE_FORM:** Treat every materially different lifecycle state as a real system configuration with its own hazards, controls, feedback and authorised exit criteria.
- **TRIGGER:** High-consequence installation, major upgrade, migration, maintenance outage, commissioning or decommissioning.
- **CHEAP_PATH:** Routine local reversible transitions with an established direct check use the ordinary procedure and observation.
- **REQUIRED_PRECONDITIONS:** Transition plan/state model, temporary configuration identity, competent coordination and restoration/rollback path.
- **REQUIRED_FEEDBACK_OR_OBSERVABILITY:** Temporary configuration, barrier availability, sequence/hold point, personnel/authority, tests, residual energy/material and exit criteria.
- **AUTHORITY_BOUNDARY:** A transition controller must have cross-boundary authority and explicit handoff/hold-point release; normal operations authority may be insufficient.
- **CRITICISMS:** Transition models can be incomplete and over-control can prolong exposure to a temporary hazardous state.
- **ANTI_CEREMONY_BOUNDARY:** A commissioning checklist is domain-specific; controlled transitional-state reasoning is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** Additional hold points can prolong exposure to a hazardous temporary configuration.

#### SAFETY_CONTROL_LOOP_PROFILE

- **PROPERTY:** Safety management of lifecycle transitions and temporary configurations
- **LOSS_OR_HAZARD:** Loss during transition, test, construction, maintenance or retirement when normal controls are absent or roles/configurations are ambiguous.
- **CONTROLLER:** The decision owner or engineering function responsible for this property.
- **CONTROLLED_PROCESS:** The design, operation, change or assurance process in which the hazard can arise.
- **SAFETY_CONSTRAINT:** The system shall not enter or remain in the hazardous condition addressed by Safety management of lifecycle transitions and temporary configurations.
- **CONTROL_ACTION:** Define transition states and hazards, sequence controls, temporary barriers/authority, hold points, configuration verification and exit/recovery criteria.
- **REQUIRED_FEEDBACK:** Temporary configuration, barrier availability, sequence/hold point, personnel/authority, tests, residual energy/material and exit criteria.
- **PROCESS_MODEL_ASSUMPTION:** Transition plan/state model, temporary configuration identity, competent coordination and restoration/rollback path.
- **DELAY_OR_OBSERVABILITY_RISK:** Delay, missing data or stale configuration can leave the controller acting on an obsolete model.
- **AUTHORITY_BOUNDARY:** A transition controller must have cross-boundary authority and explicit handoff/hold-point release; normal operations authority may be insufficient.
- **FAILURE_IF_OVER_APPLIED:** Excessive analysis or intervention can delay low-consequence reversible work and induce bypass.
- **CHEAP_PATH:** Routine local reversible transitions with an established direct check use the ordinary procedure and observation.
- **MATURE_FORM:** Treat every materially different lifecycle state as a real system configuration with its own hazards, controls, feedback and authorised exit criteria.


#### CONSEQUENCE_REVERSIBILITY_PROFILE

- **PROPERTY:** Safety management of lifecycle transitions and temporary configurations
- **CONSEQUENCE_DIMENSION:** Control depth increases with credible harm to people, mission, environment, critical service or public exposure.
- **REVERSIBILITY_DIMENSION:** More assurance is warranted where effects cannot be cheaply rolled back or compensated.
- **COUPLING_DIMENSION:** Tighter coupling and broader propagation increase the value of explicit modelling and containment.
- **OBSERVABILITY_LATENCY:** Longer delay between unsafe action and observable consequence increases anticipatory analysis needs.
- **RECOVERY_DIFFICULTY:** Difficult or ethically impossible recovery/testing increases dependence on analytical and independent evidence.
- **CONTROL_STRENGTH_RELATION:** Scale analysis, independence, evidence and recovery controls to consequence and uncertainty, not to labels.
- **CHEAP_PATH:** Routine local reversible transitions with an established direct check use the ordinary procedure and observation.
- **OVER_CONTROL_FAILURE:** Uniform maximal treatment wastes scarce safety attention and can provoke workarounds or unavailable service.
- **MATURE_FORM:** Treat every materially different lifecycle state as a real system configuration with its own hazards, controls, feedback and authorised exit criteria.


#### EVIDENCE_STRENGTH

- **HISTORICAL_PROVENANCE_STRENGTH:** HIGH — origin and transmission are documented in primary or authoritative historical sources.
- **FORMAL_OR_MODEL_STRENGTH:** HIGH_FOR_REPRESENTATION_MODERATE_FOR_EFFECTIVENESS — control theory cleanly represents constraints, actions and feedback; comparative outcome evidence remains limited.
- **ACCIDENT_CASE_STRENGTH:** MODERATE — multiple cases exhibit the mechanism, but case evidence is not a controlled estimate of effect size.
- **EMPIRICAL_COMPARATIVE_STRENGTH:** LOW_TO_MODERATE — controlled or comparative field evidence is uneven across domains.
- **DOMAIN_PRACTICE_STRENGTH:** HIGH — established in mature high-consequence practice when properly scoped.
- **STANDARD_OR_REGULATORY_STRENGTH:** HIGH — required or recognised in one or more authoritative regimes; this is practice authority, not optimality proof.
- **TRANSFERABILITY_STRENGTH:** MODERATE_TO_HIGH — mechanism transfers when the same hazard/control conditions exist; artefacts do not automatically transfer.
- **ASSUMPTION_SENSITIVITY:** HIGH — value depends on boundary, model, data, authority, independence and current configuration.
- **CONTRARY_EVIDENCE_STRENGTH:** MODERATE — implementation failures and scope critiques materially constrain use.
- **SOURCE_BASIS:** Primary: S012, S054, S060, S095, S103; critical/contrary: S058, S073.


#### QUESTIONS_FOR_REPOSITORY_AUDIT

- Does the target system explicitly represent the loss or hazard addressed by Safety management of lifecycle transitions and temporary configurations, rather than only a proxy, component check or document status?
- When the trigger is present — High-consequence installation, major upgrade, migration, maintenance outage, commissioning or decommissioning. — what enforceable mechanism implements the mature form, and who can change or stop the decision?
- Is the available feedback sufficient and current to establish the intended state — Temporary configuration, barrier availability, sequence/hold point, personnel/authority, tests, residual energy/material and exit criteria. — rather than merely command or workflow success?
- Do assigned responsibilities possess the actual authority, access and resources stated here: A transition controller must have cross-boundary authority and explicit handoff/hold-point release; normal operations authority may be insufficient.?
- Can evidence or control remain apparently valid after configuration, assumptions, environment or exposure have changed?
- Does the target preserve this non-trigger or cheap path without underclassifying wider consequences: Routine local reversible transitions with an established direct check use the ordinary procedure and observation.?
- Does any artefact associated with this property have a live decision consumer, or is it compliance ceremony?

## CEREMONIES_TO_NOT_BLINDLY_ADOPT

- **ESS-055 — Risk-matrix cell treated as objective risk or sufficient decision evidence:** NO_GENERAL_PROPERTY in the claim that a matrix score is risk; retain explicit, uncertainty-aware and decision-linked risk representation instead. Anti-ceremony boundary: The coloured grid is optional ceremony and becomes harmful when it substitutes for evidence or judgement.
- **ESS-056 — Maximal safety process on every change:** NO_GENERAL_PROPERTY in uniform maximal treatment; apply only the control depth needed to discriminate and control the credible loss. Anti-ceremony boundary: Universal full-process templates are ceremony, not safety.
- **ESS-057 — Compliance or certification treated as proof of current system safety:** Certification is a bounded governance/evidence decision, not a guarantee that all hazards are identified, controlled or unchanged. Anti-ceremony boundary: The certificate is domain-specific; current hazard/control/evidence integrity is the property.
- **ESS-058 — Zero observed incidents treated as proof that controls work:** NO_GENERAL_PROPERTY in incident-free proof; require evidence proportionate to rarity, exposure and causal control state. Anti-ceremony boundary: Zero-incident boards and targets are potentially harmful ceremony when they suppress learning.
- **ESS-059 — Human error used as the root-cause endpoint:** Human action is analysed as part of a sociotechnical control system; “error” alone never closes causal or corrective-action burdens. Anti-ceremony boundary: A Swiss-cheese or human-error taxonomy is optional; context/control evidence is required.
- **ESS-060 — More redundancy treated as automatically safer:** Use the minimum architecture that controls the hazard with demonstrable independence and manageable interaction complexity. Anti-ceremony boundary: Channel count is ceremony without hazard purpose, independence and health evidence.
- **ESS-061 — Reviewer or evidence-item count treated as assurance strength:** Assurance strength depends on relevance, validity, currentness and independently informative failure modes—not artefact or reviewer count. Anti-ceremony boundary: Review boards and evidence inventories are implementations, not properties.
- **ESS-062 — Complete safety case treated as proof the system is safe:** A case is a defeasible justification for a bounded decision, never a proof that all system hazards are absent or controlled. Anti-ceremony boundary: The monolithic completed document is not a general property.
- **ESS-063 — One universal hazard-analysis technique:** Use the minimum complementary method set needed to represent credible causal classes and make decisions; declare what remains outside. Anti-ceremony boundary: Named-method ritual is not a property.
- **ESS-064 — Zero-risk or absolute-safety requirement as a general engineering target:** NO_GENERAL_PROPERTY in absolute safety; engineer against specified unacceptable losses with bounded evidence and transparent residual uncertainty. Anti-ceremony boundary: “Zero risk” slogans are ceremony unless attached to a specific enforceable prohibition.
- **ESS-065 — Generic safety-culture score treated as direct control or safety evidence:** Use “culture” only as a hypothesis about observable decision/control patterns, never as self-validating evidence from a composite score. Anti-ceremony boundary: A culture survey, campaign or slogan is not a general safety property.
- **ESS-066 — Swiss-cheese diagram used as an engine-level causal explanation:** SUPERSEDED_BY_STRONGER_FORM for detailed analysis; retain only a bounded communication metaphor subordinate to explicit mechanisms. Anti-ceremony boundary: The diagram is not required and should not authorise controls by itself.
- **ESS-067 — STPA treated as a universal replacement for other hazard analyses:** CONTESTED as a universal method; retain STPA as one strong representation for control/interaction hazards with explicit limits and complementary analyses. Anti-ceremony boundary: STPA terminology/diagrams are not universal properties.
- **ESS-068 — Resilience or adaptation terminology without hazard, control or decision specificity:** CONTESTED as a standalone general property; admit only specific, observable and authority-bounded adaptive mechanisms linked to unacceptable loss. Anti-ceremony boundary: A resilience workshop, score or vocabulary is not required.
- Hazard-log spreadsheet, risk-matrix colour, GSN notation, review board, certification checklist, FMEA worksheet, STPA diagram, alarm dashboard and corrective-action database are implementations—not general properties.

## CONTEXTS_WHERE_PROPERTY_SHOULD_NOT_TRIGGER

- Local, cheap and reversible work whose consequence is immediately observable and conclusively settled by an authoritative deterministic discriminator.
- Work already governed by an existing control whose coverage and configuration equivalence are demonstrated; duplicate analysis would add no information.
- Named-method ceremonies whose causal representation does not match the hazard class.
- Review, reporting, alarm or artefact production with no live or credibly latent consequential decision consumer.
- Situations where the safety control would create greater, less recoverable loss by making a necessary safety-critical service unavailable.
- Historical or already eliminated hazards after dependency-aware control retirement and evidence preservation.

## HIGH_CONSEQUENCE_ONLY_PROPERTIES

- ESS-022 — Proportionate risk reduction under ALARP or SFAIRP reasoning
- ESS-023 — Defence in depth with barrier independence and degradation monitoring
- ESS-031 — Independent assessment and IV&V where consequence warrants
- ESS-038 — Bounded emergency or temporary risk acceptance with compensating controls
- ESS-044 — Supplier and contractor boundary assurance with change notification
- ESS-050 — Safety margins, operating envelopes and boundary separation
- ESS-054 — Safety management of lifecycle transitions and temporary configurations
- ESS-031 independent IV&V and the strongest forms of ESS-025 evidence diversity also require consequence, novelty or conflict sufficient to justify separation cost.

## DOMAIN_CERTIFICATION_SPECIFIC_PROPERTIES

- ESS-024 safety-integrity/development-assurance grading: SIL, ASIL, DAL and objective sets are domain-specific.
- IEC 61508, ISO 26262, ISO 21448, ARP4754/ARP4761, DO-178/DO-254, ISO 14971, nuclear technical specifications and rail CSM machinery must not be generalised wholesale.
- ESS-022 ALARP/SFAIRP has a transferable proportionality mechanism but a jurisdiction-specific legal form.
- ESS-023 defence in depth, ESS-036 fail-operational architecture and ESS-054 transition controls are strongly domain-shaped.

## PROPERTIES_REQUIRING_INDEPENDENT_ASSURANCE

- ESS-021 — Explicit residual-risk acceptance by competent authority
- ESS-024 — Safety-integrity and development-assurance rigour tied to safety functions
- ESS-025 — Informational independence and diversity of assurance evidence
- ESS-026 — Claim–argument–evidence safety assurance
- ESS-027 — Defeaters, counterevidence and authorised challenge in assurance
- ESS-028 — Configuration identity binding for safety evidence
- ESS-029 — Safety impact analysis and proportionate re-assurance after change
- ESS-030 — Living, current and operationally connected assurance
- ESS-031 — Independent assessment and IV&V where consequence warrants
- ESS-032 — Evidence triangulation and targeted formal verification
- ESS-044 — Supplier and contractor boundary assurance with change notification
- ESS-053 — Integrated verification that a safety control achieves the intended state

## INTERACTION_HAZARD_PROPERTIES

- ESS-002 — Hazardous system-state framing distinct from failure
- ESS-008 — Unsafe interaction and unsafe-control analysis
- ESS-009 — Closed-loop control and feedback integrity
- ESS-010 — Controller process-model and mode consistency
- ESS-011 — Timing, ordering, duration and transition semantics
- ESS-012 — Interface assumptions and safety contracts
- ESS-013 — Common-cause, common-mode and dependent-failure reasoning
- ESS-014 — Redundancy with demonstrated independence, diversity and observability
- ESS-015 — Scenario and causal-path coverage through complementary methods
- ESS-016 — Human–automation coordination and mode awareness
- ESS-017 — Authority, responsibility, stop and handoff clarity
- ESS-033 — Joint safety–security analysis for cyber-physical control
- ESS-035 — Containment, isolation and emergency stop with state confirmation
- ESS-036 — Context-sensitive fail-safe, fail-operational and graceful-degradation design
- ESS-045 — Operational monitoring and adaptive safety-envelope governance
- ESS-053 — Integrated verification that a safety control achieves the intended state
- ESS-054 — Safety management of lifecycle transitions and temporary configurations

## PROPERTIES_WITH_STRONG_ACCIDENT_OR_DOMAIN_EVIDENCE

- ESS-002 — Hazardous system-state framing distinct from failure
- ESS-008 — Unsafe interaction and unsafe-control analysis
- ESS-009 — Closed-loop control and feedback integrity
- ESS-012 — Interface assumptions and safety contracts
- ESS-013 — Common-cause, common-mode and dependent-failure reasoning
- ESS-014 — Redundancy with demonstrated independence, diversity and observability
- ESS-016 — Human–automation coordination and mode awareness
- ESS-017 — Authority, responsibility, stop and handoff clarity
- ESS-023 — Defence in depth with barrier independence and degradation monitoring
- ESS-025 — Informational independence and diversity of assurance evidence
- ESS-026 — Claim–argument–evidence safety assurance
- ESS-028 — Configuration identity binding for safety evidence
- ESS-029 — Safety impact analysis and proportionate re-assurance after change
- ESS-035 — Containment, isolation and emergency stop with state confirmation
- ESS-036 — Context-sensitive fail-safe, fail-operational and graceful-degradation design
- ESS-039 — Incident, near-miss and precursor reporting connected to learning
- ESS-040 — Multi-factor causal investigation grounded in local rationality
- ESS-041 — Corrective-action ownership, implementation and effectiveness verification
- ESS-043 — Organisational control, incentives and production-pressure analysis
- ESS-044 — Supplier and contractor boundary assurance with change notification
- ESS-049 — Hazard-control hierarchy favouring elimination and engineered control
- ESS-053 — Integrated verification that a safety control achieves the intended state
- ESS-054 — Safety management of lifecycle transitions and temporary configurations

## PROPERTIES_WITH_MIXED_OR_WEAK_SUPPORT

- ESS-020’s multidimensional proportionality mechanism is strongly reasoned and cross-domain, but no universal weighting rule is validated.
- ESS-022 ALARP/SFAIRP is authoritative in its jurisdiction but ethically and methodologically contested in transfer.
- ESS-030 living/continuous assurance has strong need and emerging practice but limited comparative outcome evidence.
- ESS-042 leading indicators are useful only when hazard-linked; broad predictive validity is weak and gaming risk high.
- ESS-045 adaptive/runtime safety envelopes are promising but difficult under open-world autonomy and partial observability.
- ESS-047 control retirement is strongly anti-bureaucratic but rare-demand barriers make inactivity ambiguous.
- ESS-067 STPA universal replacement and ESS-068 generic resilience remain contested; their narrower mechanism properties survive elsewhere.

## RISK_QUANTIFICATION_LIMITS

- Severity–likelihood cells are not objective risk and can reverse rankings or compress materially different risks.
- Ordinal arithmetic, threshold boundaries and category choices can be gamed.
- Sparse catastrophic data, changing exposure and dependence make rare-event frequency estimates highly assumption-sensitive.
- Common-cause and organisational/software interactions invalidate naive independence.
- SIL/ASIL/DAL are graded assurance/integrity classifications, not direct probabilities that the total system is safe.
- Expected value can conflict with categorical unacceptable-loss constraints and distributional/rights considerations.
- ALARP/SFAIRP is reasoned proportionality, not an automatic cost-benefit formula or universal legal rule.
- Quantification should change a decision; when a deterministic constraint settles it, extra probability work is ceremony.

## UNRESOLVED_PROPERTIES

- **Population-level UNRESOLVED status:** none. Relevant evidence searches were completed sufficiently to freeze each candidate as retained, contextual, rejected, superseded, ceremonial or contested.
- **Contested:** ESS-067 universal STPA replacement and ESS-068 generic resilience/adaptation language.
- Every retained property preserves an OPEN_QUESTIONS field; freezing does not claim that comparative effect sizes, hazard completeness or all domain transfers are settled.

## Denominator disposition

- **68/68 examined.** No candidate was silently omitted because it failed admission.
- **54** properties survive in general, evolved, control-loop, assurance, sociotechnical, high-consequence, context-dependent or domain-specific form.
- **14** candidates are explicitly rejected, ceremonial, superseded or contested.
