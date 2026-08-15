# EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_AUDIT_INTAKE

**Analytical label:** `EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING`  
**Replacement freeze:** 12 August 2026  
**Population:** 50/50 properties retained and re-profiled  
**Scope boundary:** independent external research; this intake asks questions and does not inspect, diagnose or prescribe changes to any target repository.

## Population and source receipt

- `PROPERTY_POPULATION_TOTAL`: 50.
- `PROPERTY_POPULATION_EXAMINED`: 50.
- `DENOMINATOR_CHANGE_FROM_PROVISIONAL_SOURCE_BASE`: NONE.
- `PROPERTY_PROFILE_DEPTH_REPAIR`: COMPLETE, 50/50.
- `SOURCE_RECORDS`: 113.
- `SOURCE_IDENTITY_AND_LOCATOR_REAUDIT`: COMPLETE.
- `CURRENT_FRONTIER_RECHECK_THROUGH`: 12 August 2026.

The crosswalk should never infer real-world assurance merely from a formal proof. For each property it must separately inspect claim meaning, assumptions, abstraction, model/implementation/environment correspondence, trusted tools, replay/currentness and the live decision consumer. The profiles below are audit questions and evidence obligations, not findings about any target.

## CEREMONIES_TO_NOT_BLINDLY_ADOPT

| PROPERTY_ID | PROPERTY_NAME | STATUS / UNRESOLVED BOUNDARY |
| --- | --- | --- |
| P038 | Ceremony/proxy rejection | CEREMONY_NOT_GENERAL_PROPERTY |
| P041 | Certification/formality ceremony boundary | USEFUL_BUT_EASILY_BUREAUCRATISED |
| P043 | Prove everything | REJECTED_OR_DISFAVOURED |
| P044 | Proof eliminates testing | REJECTED_OR_DISFAVOURED |
| P045 | Model checking explores every real behaviour | REJECTED_OR_DISFAVOURED |
| P046 | Type safety means functional correctness | REJECTED_OR_DISFAVOURED |
| P047 | Proof assistant cannot be wrong | ASSUMPTION_SENSITIVE |

## CONTEXTS_WHERE_PROPERTY_SHOULD_NOT_TRIGGER

| PROPERTY_ID | PROPERTY_NAME | STATUS / UNRESOLVED BOUNDARY |
| --- | --- | --- |
| P016 | Exhaustive finite-state challenge where warranted | MODEL_CHECKING_PROPERTY |
| P021 | Mechanical proof replay | THEOREM_PROVING_PROPERTY |
| P025 | Symbolic execution/path constraint scope | CONTEXT_DEPENDENT |
| P028 | Dependent/refinement types as selective proof carriers | STATIC_ANALYSIS_TYPE_PROPERTY |
| P031 | Runtime monitor scope | RUNTIME_VERIFICATION_PROPERTY |
| P033 | Verified compiler/toolchain scope | VERIFIED_TOOLCHAIN_PROPERTY |
| P037 | Lightweight proportional formalisation | RETAINED_IN_EVOLVED_FORM |
| P042 | Cost/payoff trigger discipline | RETAINED_IN_EVOLVED_FORM |
| P050 | Domain-specific verified libraries/protocols | DOMAIN_SPECIFIC |

## PROPERTIES_REQUIRING_PRECISE_FORMAL_CLAIM

| PROPERTY_ID | PROPERTY_NAME | STATUS / UNRESOLVED BOUNDARY |
| --- | --- | --- |
| P001 | Precise property before proof | SPECIFICATION_PROPERTY |
| P002 | Explicit assumptions and preconditions | STRONGLY_RETAINED |
| P005 | State invariant as cheap mechanical guard | INVARIANT_TEMPORAL_PROPERTY |
| P006 | Inductive invariant obligation | INVARIANT_TEMPORAL_PROPERTY |
| P007 | Safety versus liveness distinction | INVARIANT_TEMPORAL_PROPERTY |
| P009 | Property-class matching | INVARIANT_TEMPORAL_PROPERTY |
| P010 | Contracts, preconditions and postconditions | CONTRACT_COMPOSITION_PROPERTY |
| P016 | Exhaustive finite-state challenge where warranted | MODEL_CHECKING_PROPERTY |
| P018 | Bounded checking scope disclosure | USEFUL_BUT_EASILY_GAMED |
| P020 | Vacuity and specification-strength checks | USEFUL_BUT_EASILY_GAMED |
| P021 | Mechanical proof replay | THEOREM_PROVING_PROPERTY |
| P024 | Solver/encoding trust boundary | CONTEXT_DEPENDENT |
| P027 | Type-system claim boundary | STATIC_ANALYSIS_TYPE_PROPERTY |
| P029 | Concurrency/distributed protocol modelling | DOMAIN_SPECIFIC |
| P030 | Linearizability/serialisability/refinement properties | DOMAIN_SPECIFIC |
| P031 | Runtime monitor scope | RUNTIME_VERIFICATION_PROPERTY |
| P034 | Translation validation per-run evidence | VERIFIED_TOOLCHAIN_PROPERTY |
| P039 | Specification gaming and golden theorem drift | USEFUL_BUT_EASILY_GAMED |
| P040 | AI-assisted formalisation boundary | CONTEXT_DEPENDENT |
| P049 | Stakeholder/world-machine validation | SPECIFICATION_PROPERTY |

## PROPERTIES_REQUIRING_ENVIRONMENT_OR_MODEL_CORRESPONDENCE

| PROPERTY_ID | PROPERTY_NAME | STATUS / UNRESOLVED BOUNDARY |
| --- | --- | --- |
| P001 | Precise property before proof | SPECIFICATION_PROPERTY |
| P002 | Explicit assumptions and preconditions | STRONGLY_RETAINED |
| P003 | Environment model boundary | ASSUMPTION_SENSITIVE |
| P004 | Explicit state and transition model | STRONGLY_RETAINED |
| P010 | Contracts, preconditions and postconditions | CONTRACT_COMPOSITION_PROPERTY |
| P012 | Assume/guarantee and compositional verification | CONTRACT_COMPOSITION_PROPERTY |
| P013 | Sound abstraction discipline | ABSTRACTION_REFINEMENT_PROPERTY |
| P014 | Refinement/simulation correspondence | ABSTRACTION_REFINEMENT_PROPERTY |
| P015 | Model-code correspondence | ASSUMPTION_SENSITIVE |
| P029 | Concurrency/distributed protocol modelling | DOMAIN_SPECIFIC |
| P030 | Linearizability/serialisability/refinement properties | DOMAIN_SPECIFIC |
| P031 | Runtime monitor scope | RUNTIME_VERIFICATION_PROPERTY |
| P032 | Monitor currentness and fail-open/fail-closed design | RUNTIME_VERIFICATION_PROPERTY |
| P033 | Verified compiler/toolchain scope | VERIFIED_TOOLCHAIN_PROPERTY |
| P034 | Translation validation per-run evidence | VERIFIED_TOOLCHAIN_PROPERTY |
| P036 | Hybrid proof + testing/fuzzing/runtime evidence | STRONGLY_RETAINED |
| P039 | Specification gaming and golden theorem drift | USEFUL_BUT_EASILY_GAMED |
| P040 | AI-assisted formalisation boundary | CONTEXT_DEPENDENT |
| P041 | Certification/formality ceremony boundary | USEFUL_BUT_EASILY_BUREAUCRATISED |
| P044 | Proof eliminates testing | REJECTED_OR_DISFAVOURED |
| P045 | Model checking explores every real behaviour | REJECTED_OR_DISFAVOURED |
| P049 | Stakeholder/world-machine validation | SPECIFICATION_PROPERTY |
| P050 | Domain-specific verified libraries/protocols | DOMAIN_SPECIFIC |

## PROPERTIES_REQUIRING_MECHANICAL_REPLAY

| PROPERTY_ID | PROPERTY_NAME | STATUS / UNRESOLVED BOUNDARY |
| --- | --- | --- |
| P005 | State invariant as cheap mechanical guard | INVARIANT_TEMPORAL_PROPERTY |
| P010 | Contracts, preconditions and postconditions | CONTRACT_COMPOSITION_PROPERTY |
| P016 | Exhaustive finite-state challenge where warranted | MODEL_CHECKING_PROPERTY |
| P018 | Bounded checking scope disclosure | USEFUL_BUT_EASILY_GAMED |
| P020 | Vacuity and specification-strength checks | USEFUL_BUT_EASILY_GAMED |
| P021 | Mechanical proof replay | THEOREM_PROVING_PROPERTY |
| P022 | Trusted kernel/certificate boundary | THEOREM_PROVING_PROPERTY |
| P023 | Proof maintenance and currentness | RETAINED_IN_EVOLVED_FORM |
| P024 | Solver/encoding trust boundary | CONTEXT_DEPENDENT |
| P026 | Sound versus unsound static analysis boundary | STATIC_ANALYSIS_TYPE_PROPERTY |
| P027 | Type-system claim boundary | STATIC_ANALYSIS_TYPE_PROPERTY |
| P028 | Dependent/refinement types as selective proof carriers | STATIC_ANALYSIS_TYPE_PROPERTY |
| P031 | Runtime monitor scope | RUNTIME_VERIFICATION_PROPERTY |
| P032 | Monitor currentness and fail-open/fail-closed design | RUNTIME_VERIFICATION_PROPERTY |
| P033 | Verified compiler/toolchain scope | VERIFIED_TOOLCHAIN_PROPERTY |
| P034 | Translation validation per-run evidence | VERIFIED_TOOLCHAIN_PROPERTY |
| P035 | Proof-carrying/certificate evidence | VERIFIED_TOOLCHAIN_PROPERTY |
| P036 | Hybrid proof + testing/fuzzing/runtime evidence | STRONGLY_RETAINED |
| P040 | AI-assisted formalisation boundary | CONTEXT_DEPENDENT |
| P041 | Certification/formality ceremony boundary | USEFUL_BUT_EASILY_BUREAUCRATISED |
| P047 | Proof assistant cannot be wrong | ASSUMPTION_SENSITIVE |
| P048 | Retirement of stale formal artefacts | RETAINED_IN_EVOLVED_FORM |
| P050 | Domain-specific verified libraries/protocols | DOMAIN_SPECIFIC |

## PROPERTIES_REQUIRING_TRUSTED_TOOLCHAIN_BOUNDARY

| PROPERTY_ID | PROPERTY_NAME | STATUS / UNRESOLVED BOUNDARY |
| --- | --- | --- |
| P021 | Mechanical proof replay | THEOREM_PROVING_PROPERTY |
| P022 | Trusted kernel/certificate boundary | THEOREM_PROVING_PROPERTY |
| P024 | Solver/encoding trust boundary | CONTEXT_DEPENDENT |
| P026 | Sound versus unsound static analysis boundary | STATIC_ANALYSIS_TYPE_PROPERTY |
| P027 | Type-system claim boundary | STATIC_ANALYSIS_TYPE_PROPERTY |
| P028 | Dependent/refinement types as selective proof carriers | STATIC_ANALYSIS_TYPE_PROPERTY |
| P033 | Verified compiler/toolchain scope | VERIFIED_TOOLCHAIN_PROPERTY |
| P034 | Translation validation per-run evidence | VERIFIED_TOOLCHAIN_PROPERTY |
| P035 | Proof-carrying/certificate evidence | VERIFIED_TOOLCHAIN_PROPERTY |
| P040 | AI-assisted formalisation boundary | CONTEXT_DEPENDENT |
| P047 | Proof assistant cannot be wrong | ASSUMPTION_SENSITIVE |
| P050 | Domain-specific verified libraries/protocols | DOMAIN_SPECIFIC |

## PROPERTIES_WITH_STRONG_FORMAL_BUT_WEAK_REAL_WORLD_CORRESPONDENCE

| PROPERTY_ID | PROPERTY_NAME | STATUS / UNRESOLVED BOUNDARY |
| --- | --- | --- |
| P006 | Inductive invariant obligation | INVARIANT_TEMPORAL_PROPERTY |
| P007 | Safety versus liveness distinction | INVARIANT_TEMPORAL_PROPERTY |
| P014 | Refinement/simulation correspondence | ABSTRACTION_REFINEMENT_PROPERTY |
| P016 | Exhaustive finite-state challenge where warranted | MODEL_CHECKING_PROPERTY |
| P021 | Mechanical proof replay | THEOREM_PROVING_PROPERTY |
| P022 | Trusted kernel/certificate boundary | THEOREM_PROVING_PROPERTY |
| P024 | Solver/encoding trust boundary | CONTEXT_DEPENDENT |
| P027 | Type-system claim boundary | STATIC_ANALYSIS_TYPE_PROPERTY |
| P028 | Dependent/refinement types as selective proof carriers | STATIC_ANALYSIS_TYPE_PROPERTY |
| P030 | Linearizability/serialisability/refinement properties | DOMAIN_SPECIFIC |
| P033 | Verified compiler/toolchain scope | VERIFIED_TOOLCHAIN_PROPERTY |
| P035 | Proof-carrying/certificate evidence | VERIFIED_TOOLCHAIN_PROPERTY |
| P040 | AI-assisted formalisation boundary | CONTEXT_DEPENDENT |

## PROPERTIES_WITH_STRONG_INDUSTRIAL_OR_DOMAIN_SUPPORT

| PROPERTY_ID | PROPERTY_NAME | STATUS / UNRESOLVED BOUNDARY |
| --- | --- | --- |
| P005 | State invariant as cheap mechanical guard | INVARIANT_TEMPORAL_PROPERTY |
| P010 | Contracts, preconditions and postconditions | CONTRACT_COMPOSITION_PROPERTY |
| P013 | Sound abstraction discipline | ABSTRACTION_REFINEMENT_PROPERTY |
| P016 | Exhaustive finite-state challenge where warranted | MODEL_CHECKING_PROPERTY |
| P021 | Mechanical proof replay | THEOREM_PROVING_PROPERTY |
| P026 | Sound versus unsound static analysis boundary | STATIC_ANALYSIS_TYPE_PROPERTY |
| P027 | Type-system claim boundary | STATIC_ANALYSIS_TYPE_PROPERTY |
| P029 | Concurrency/distributed protocol modelling | DOMAIN_SPECIFIC |
| P033 | Verified compiler/toolchain scope | VERIFIED_TOOLCHAIN_PROPERTY |
| P036 | Hybrid proof + testing/fuzzing/runtime evidence | STRONGLY_RETAINED |
| P037 | Lightweight proportional formalisation | RETAINED_IN_EVOLVED_FORM |
| P042 | Cost/payoff trigger discipline | RETAINED_IN_EVOLVED_FORM |
| P050 | Domain-specific verified libraries/protocols | DOMAIN_SPECIFIC |

## PROPERTIES_WITH_MIXED_OR_WEAK_SUPPORT

| PROPERTY_ID | PROPERTY_NAME | STATUS / UNRESOLVED BOUNDARY |
| --- | --- | --- |
| P008 | Fairness and scheduler assumptions | ASSUMPTION_SENSITIVE |
| P012 | Assume/guarantee and compositional verification | CONTRACT_COMPOSITION_PROPERTY |
| P020 | Vacuity and specification-strength checks | USEFUL_BUT_EASILY_GAMED |
| P023 | Proof maintenance and currentness | RETAINED_IN_EVOLVED_FORM |
| P024 | Solver/encoding trust boundary | CONTEXT_DEPENDENT |
| P025 | Symbolic execution/path constraint scope | CONTEXT_DEPENDENT |
| P028 | Dependent/refinement types as selective proof carriers | STATIC_ANALYSIS_TYPE_PROPERTY |
| P030 | Linearizability/serialisability/refinement properties | DOMAIN_SPECIFIC |
| P031 | Runtime monitor scope | RUNTIME_VERIFICATION_PROPERTY |
| P032 | Monitor currentness and fail-open/fail-closed design | RUNTIME_VERIFICATION_PROPERTY |
| P034 | Translation validation per-run evidence | VERIFIED_TOOLCHAIN_PROPERTY |
| P035 | Proof-carrying/certificate evidence | VERIFIED_TOOLCHAIN_PROPERTY |
| P039 | Specification gaming and golden theorem drift | USEFUL_BUT_EASILY_GAMED |
| P040 | AI-assisted formalisation boundary | CONTEXT_DEPENDENT |
| P041 | Certification/formality ceremony boundary | USEFUL_BUT_EASILY_BUREAUCRATISED |
| P048 | Retirement of stale formal artefacts | RETAINED_IN_EVOLVED_FORM |
| P049 | Stakeholder/world-machine validation | SPECIFICATION_PROPERTY |

## SPECIFICATION_OR_VACUITY_GAMING_RISKS

| PROPERTY_ID | PROPERTY_NAME | STATUS / UNRESOLVED BOUNDARY |
| --- | --- | --- |
| P001 | Precise property before proof | SPECIFICATION_PROPERTY |
| P002 | Explicit assumptions and preconditions | STRONGLY_RETAINED |
| P005 | State invariant as cheap mechanical guard | INVARIANT_TEMPORAL_PROPERTY |
| P006 | Inductive invariant obligation | INVARIANT_TEMPORAL_PROPERTY |
| P008 | Fairness and scheduler assumptions | ASSUMPTION_SENSITIVE |
| P010 | Contracts, preconditions and postconditions | CONTRACT_COMPOSITION_PROPERTY |
| P016 | Exhaustive finite-state challenge where warranted | MODEL_CHECKING_PROPERTY |
| P018 | Bounded checking scope disclosure | USEFUL_BUT_EASILY_GAMED |
| P020 | Vacuity and specification-strength checks | USEFUL_BUT_EASILY_GAMED |
| P027 | Type-system claim boundary | STATIC_ANALYSIS_TYPE_PROPERTY |
| P031 | Runtime monitor scope | RUNTIME_VERIFICATION_PROPERTY |
| P038 | Ceremony/proxy rejection | CEREMONY_NOT_GENERAL_PROPERTY |
| P039 | Specification gaming and golden theorem drift | USEFUL_BUT_EASILY_GAMED |
| P040 | AI-assisted formalisation boundary | CONTEXT_DEPENDENT |
| P041 | Certification/formality ceremony boundary | USEFUL_BUT_EASILY_BUREAUCRATISED |
| P045 | Model checking explores every real behaviour | REJECTED_OR_DISFAVOURED |
| P046 | Type safety means functional correctness | REJECTED_OR_DISFAVOURED |
| P049 | Stakeholder/world-machine validation | SPECIFICATION_PROPERTY |

## UNRESOLVED_PROPERTIES

| PROPERTY_ID | PROPERTY_NAME | STATUS / UNRESOLVED BOUNDARY |
| --- | --- | --- |
| P008 | Fairness and scheduler assumptions | How can fairness assumptions be calibrated against empirical scheduler/network distributions without converting a deterministic theorem into false certainty? |
| P012 | Assume/guarantee and compositional verification | How can global liveness and resource properties be decomposed without circular proof? |
| P020 | Vacuity and specification-strength checks | Which specification-strength metrics correlate with field defect prevention rather than benchmark score? |
| P023 | Proof maintenance and currentness | Which proof architectures minimise semantic maintenance cost across realistic software evolution? |
| P024 | Solver/encoding trust boundary | Can practical certificates cover all high-performance preprocessing and theory combinations? |
| P028 | Dependent/refinement types as selective proof carriers | How can refinement/dependent proofs survive API and library evolution with lower repair cost? |
| P030 | Linearizability/serialisability/refinement properties | How can history/refinement proofs scale under weak memory and highly optimised implementations? |
| P031 | Runtime monitor scope | How can monitor uncertainty and inconclusive verdicts be presented in operational decisions? |
| P032 | Monitor currentness and fail-open/fail-closed design | How should fail-open/fail-closed choices be optimised when safety and availability hazards compete? |
| P034 | Translation validation per-run evidence | How can validators cover aggressive transformations and property-specific semantics with acceptable cost? |
| P035 | Proof-carrying/certificate evidence | How can certificate ecosystems remain interoperable and stable across tool evolution? |
| P039 | Specification gaming and golden theorem drift | How can semantic theorem diffs be made understandable to non-logician decision owners? |
| P040 | AI-assisted formalisation boundary | What scalable method establishes semantic equivalence between natural-language engineering requirements and generated formal statements? |
| P042 | Cost/payoff trigger discipline | What common outcome measures permit credible cross-project comparisons of proof, model checking, static analysis and testing? |
| P048 | Retirement of stale formal artefacts | Can semantic dependency analysis reliably distinguish harmless prover/library churn from assurance-relevant change? |
| P049 | Stakeholder/world-machine validation | How can uncertain physical/human domain models be linked to deterministic proofs without laundering uncertainty? |

## COMPLETE_CROSSWALK_PROPERTY_PROFILES

### P001 — Precise property before proof

**PROPERTY_ID:** `P001`  
**PROPERTY_NAME:** Precise property before proof

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** A claim must be formal enough to distinguish conforming from non-conforming behaviours before proof or checking is meaningful. It is intended to prevent: Informal acceptance claims such as “the protocol is safe” or “the function is correct” do not identify the bad behaviours, initial states, outputs, timing conditions or observers that a checker must discriminate. Without a claim precise enough to be false, proof activity can optimise notation and tactics while leaving the engineering decision undefined.

**MATURE_FORM:** No proof campaign begins from a slogan. The accepted object is a reviewable, versioned claim package whose formal statement discriminates material behaviours, whose translation has been challenged by positive and negative examples, and whose scope, assumptions and consumer are explicit. Mechanical proof then answers that exact claim—nothing broader.

**TRIGGER:** Trigger before any mechanically checked claim that will control a consequential decision, especially where prose admits multiple interpretations or generated formalisation is used.

**CHEAP_PATH:** For a local deterministic rule, use a typed assertion, truth table, executable example set or property-based test if it provides the needed discrimination more cheaply than a separate specification language.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Precise property before proof",
  "ENGINEERING_CLAIM": "A claim must be formal enough to distinguish conforming from non-conforming behaviours before proof or checking is meaningful.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying precise property before proof; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The formula must be satisfiable, nontrivial, typed/unit-consistent, explicit about undefined and exceptional cases, and traceable to the engineering claim.",
  "ENVIRONMENT_MODEL": "World phenomena and controllable/observable interfaces needed for the claim must be stated rather than silently treated as program variables.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide precise property before proof; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: A precise formula formalises a convenient surrogate rather than the stakeholder requirement.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which construct a versioned formal-claim profile that links the engineering claim to a typed formal statement, examples and anti-examples, assumptions, environment and failure model, property class, model scope, implementation correspondence and named decision consumer.",
  "SAFETY_LIVENESS_CLASS": "specification",
  "ABSTRACTION": "Any omitted detail must be shown irrelevant to the claim or recorded as a scope limit.",
  "IMPLEMENTATION_CORRESPONDENCE": "Not established by this property; the claim package must say whether it governs a design model, source, binary, configuration or observed runtime.",
  "CHEAP_PATH": "For a local deterministic rule, use a typed assertion, truth table, executable example set or property-based test if it provides the needed discrimination more cheaply than a separate specification language.",
  "MATURE_FORM": "No proof campaign begins from a slogan. The accepted object is a reviewable, versioned claim package whose formal statement discriminates material behaviours, whose translation has been challenged by positive and negative examples, and whose scope, assumptions and consumer are explicit. Mechanical proof then answers that exact claim—nothing broader.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P001; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to precise property before proof.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Informal acceptance claims such as “the protocol is safe” or “the function is correct” do not identify the bad behaviours, initial states, outputs, timing conditions or observers that a checker must discriminate. Without a claim precise enough to be false, proof activity can optimise notation and tactics while leaving the engineering decision undefined..",
  "RELATION": "Not established by this property; the claim package must say whether it governs a design model, source, binary, configuration or observed runtime.",
  "SOUNDNESS_DUTY": "Any omitted detail must be shown irrelevant to the claim or recorded as a scope limit.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Fetzer’s program/execution distinction and world–machine requirements analysis show that formal precision is not semantic validity [S056, S081, S082].",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "No proof campaign begins from a slogan. The accepted object is a reviewable, versioned claim package whose formal statement discriminates material behaviours, whose translation has been challenged by positive and negative examples, and whose scope, assumptions and consumer are explicit. Mechanical proof then answers that exact claim—nothing broader.",
  "KNOWN_GAP": "A precise formula formalises a convenient surrogate rather than the stakeholder requirement."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for precise property before proof.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For a local deterministic rule, use a typed assertion, truth table, executable example set or property-based test if it provides the needed discrimination more cheaply than a separate specification language."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Precise property before proof may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger before any mechanically checked claim that will control a consequential decision, especially where prose admits multiple interpretations or generated formalisation is used.",
  "CHEAPER_EVIDENCE": "For a local deterministic rule, use a typed assertion, truth table, executable example set or property-based test if it provides the needed discrimination more cheaply than a separate specification language."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P001.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Not established by this property; the claim package must say whether it governs a design model, source, binary, configuration or observed runtime.",
  "ENVIRONMENT_BOUNDARY": "World phenomena and controllable/observable interfaces needed for the claim must be stated rather than silently treated as program variables.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Parsers, translators and generated-formula pipelines that can alter the statement belong in the trusted or independently checked boundary.",
  "DRIFT_DETECTOR": "Requirement and formal-statement identities must change together; replay alone is insufficient if the engineering meaning changed.",
  "KNOWN_ESCAPE": "A precise formula formalises a convenient surrogate rather than the stakeholder requirement."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter precise property before proof.",
  "IDENTITIES_TO_BIND": "Requirement and formal-statement identities must change together; replay alone is insufficient if the engineering meaning changed.",
  "REPLAY_OR_RECHECK": "Parsers, translators and generated-formula pipelines that can alter the statement belong in the trusted or independently checked boundary.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Construct a versioned formal-claim profile that links the engineering claim to a typed formal statement, examples and anti-examples, assumptions, environment and failure model, property class, model scope, implementation correspondence and named decision consumer. Check satisfiability, witness behaviours, non-vacuity and expected edge cases before investing in proof.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should quantitative and human/physical requirements be linked to deterministic formal predicates without false precision?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The formula must be satisfiable, nontrivial, typed/unit-consistent, explicit about undefined and exceptional cases, and traceable to the engineering claim.
- Abstraction: Any omitted detail must be shown irrelevant to the claim or recorded as a scope limit.
- Environment: World phenomena and controllable/observable interfaces needed for the claim must be stated rather than silently treated as program variables.
- Model/code correspondence: Not established by this property; the claim package must say whether it governs a design model, source, binary, configuration or observed runtime.
- Trusted tools: Parsers, translators and generated-formula pipelines that can alter the statement belong in the trusted or independently checked boundary.
- Currentness/replay: Requirement and formal-statement identities must change together; replay alone is insufficient if the engineering meaning changed.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Direct primary lineage from Floyd/Hoare through formal specification and requirements semantics documents why a formal claim precedes proof. | S001, S002, S010, S012, S081, S084 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_FORMAL_ELIGIBILITY | Precision is logically necessary for checking, but no theorem establishes that the chosen statement is the intended one. | S001, S002, S081 |
| MECHANICAL_REPLAY_STRENGTH | MEDIUM | Once encoded, syntax and theorem can be replayed; semantic validation of the prose-to-formal translation remains partly human. | S021, S100, S101, S102 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_BY_ITSELF | A precise property does not connect model to source, binary, hardware or deployment without separate correspondence evidence. | S056, S082, S092 |
| INDUSTRIAL_CASE_STRENGTH | MEDIUM_HIGH | AWS, aviation guidance and deductive-verification practice all require explicit properties, but cases are selective. | S029, S052, S054, S100 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Qualitative practitioner and current translation benchmarks support the failure mode; controlled comparative productivity evidence is limited. | S100, S101, S102 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_IN_ASSURANCE_DOMAINS | DO-333 explicitly requires defined formal properties and sound formal-method objectives. | S051, S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH | Every formal technique requires a discriminating statement, although the notation and validation method vary. | S062, S065, S084 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Small changes in intended meaning, quantification, initial states or units can reverse the claim while leaving a proof valid. | S059, S060, S081, S101 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Specification-problem, vacuity, empirical defect and autoformalisation evidence directly limits overclaiming. | S055, S056, S059, S060, S092, S100, S101, S102 |

**CRITICISMS:**
- Fetzer’s program/execution distinction and world–machine requirements analysis show that formal precision is not semantic validity [S056, S081, S082].
- Vacuity research shows that even a syntactically substantive formula may hold for an irrelevant reason [S059, S060].
- Dafny practitioner evidence reports specification errors that testing or review can reveal although verification succeeds [S100].
- Current autoformalisation work shows that a type-correct translated statement can differ semantically from its source [S101, S102].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—No proof campaign begins from a slogan. The accepted object is a reviewable, versioned claim package whose formal statement discriminates material behaviours, whose translation has been challenged by positive and negative examples, and whose scope, assumptions and consumer are explicit. Mechanical proof then answers that exact claim—nothing broader.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P049 — Stakeholder/world-machine validation, P020 — Vacuity and specification-strength checks. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P001 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while a precise formula formalises a convenient surrogate rather than the stakeholder requirement?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P001?
- Would the cheap path — For a local deterministic rule, use a typed assertion, truth table, executable example set or property-based test if it provides the needed discrimination more cheaply than a separate specification language — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P001, what decision changes, and should the artefact be retired if no live consumer remains?


### P002 — Explicit assumptions and preconditions

**PROPERTY_ID:** `P002`  
**PROPERTY_NAME:** Explicit assumptions and preconditions

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Every formal result must expose assumptions, axioms, preconditions, initial states and accepted fault/environment models. It is intended to prevent: A result can be mathematically valid yet irrelevant or vacuous because the failing case is excluded by a hidden precondition, an inconsistent axiom set, an unreachable initial state, an idealised scheduler or a fault model that deployment does not satisfy.

**MATURE_FORM:** Every formal result carries a complete, versioned assumption set with satisfiability evidence and an owner/discharge mode for each item. Hidden defaults, imported axioms and environmental premises are surfaced; assumptions that can be enforced or monitored become executable obligations; results are downgraded when deployment cannot establish them.

**TRIGGER:** Trigger for every theorem, model-check result, static-analysis claim, certificate or monitor verdict that will be consumed outside the immediate authoring context.

**CHEAP_PATH:** For a trivial local check, encode the precondition directly in the function type/assertion and test the rejection path; do not create a separate assumption bureaucracy.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Explicit assumptions and preconditions",
  "ENGINEERING_CLAIM": "Every formal result must expose assumptions, axioms, preconditions, initial states and accepted fault/environment models.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying explicit assumptions and preconditions; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Assumptions must be separated from guarantees and must not make the initial condition empty or the desired behaviour impossible to violate.",
  "ENVIRONMENT_MODEL": "Scheduler, network, hardware, clock, user and operator premises need evidence or explicit residual-risk acceptance.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide explicit assumptions and preconditions; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Assumptions are scattered across code, tactics, library imports and prose rather than enumerated.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which maintain an assumption register attached to each theorem/model run: logical axioms, type/units, preconditions, initial-state predicate, rely/fairness conditions, failure semantics, hardware/runtime conditions and configuration.",
  "SAFETY_LIVENESS_CLASS": "strongly retained",
  "ABSTRACTION": "Assumptions introduced solely to make an abstraction tractable must be labelled and justified against omitted behaviours.",
  "IMPLEMENTATION_CORRESPONDENCE": "Code/configuration must satisfy input domains, memory models, build options and shims presupposed by the result.",
  "CHEAP_PATH": "For a trivial local check, encode the precondition directly in the function type/assertion and test the rejection path; do not create a separate assumption bureaucracy.",
  "MATURE_FORM": "Every formal result carries a complete, versioned assumption set with satisfiability evidence and an owner/discharge mode for each item. Hidden defaults, imported axioms and environmental premises are surfaced; assumptions that can be enforced or monitored become executable obligations; results are downgraded when deployment cannot establish them.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P002; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to explicit assumptions and preconditions.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in A result can be mathematically valid yet irrelevant or vacuous because the failing case is excluded by a hidden precondition, an inconsistent axiom set, an unreachable initial state, an idealised scheduler or a fault model that deployment does not satisfy..",
  "RELATION": "Code/configuration must satisfy input domains, memory models, build options and shims presupposed by the result.",
  "SOUNDNESS_DUTY": "Assumptions introduced solely to make an abstraction tractable must be labelled and justified against omitted behaviours.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Vacuity and inconsistent-environment cases can make a property pass without exercising its subject [S059, S060].",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Every formal result carries a complete, versioned assumption set with satisfiability evidence and an owner/discharge mode for each item. Hidden defaults, imported axioms and environmental premises are surfaced; assumptions that can be enforced or monitored become executable obligations; results are downgraded when deployment cannot establish them.",
  "KNOWN_GAP": "Assumptions are scattered across code, tactics, library imports and prose rather than enumerated."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for explicit assumptions and preconditions.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For a trivial local check, encode the precondition directly in the function type/assertion and test the rejection path; do not create a separate assumption bureaucracy."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Explicit assumptions and preconditions may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger for every theorem, model-check result, static-analysis claim, certificate or monitor verdict that will be consumed outside the immediate authoring context.",
  "CHEAPER_EVIDENCE": "For a trivial local check, encode the precondition directly in the function type/assertion and test the rejection path; do not create a separate assumption bureaucracy."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P002.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Code/configuration must satisfy input domains, memory models, build options and shims presupposed by the result.",
  "ENVIRONMENT_BOUNDARY": "Scheduler, network, hardware, clock, user and operator premises need evidence or explicit residual-risk acceptance.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Imported axioms, oracle calls, admitted lemmas, unsafe extensions and solver semantics must be enumerated.",
  "DRIFT_DETECTOR": "Assumption changes invalidate the engineering claim even when theorem text and proof term replay unchanged.",
  "KNOWN_ESCAPE": "Assumptions are scattered across code, tactics, library imports and prose rather than enumerated."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter explicit assumptions and preconditions.",
  "IDENTITIES_TO_BIND": "Assumption changes invalidate the engineering claim even when theorem text and proof term replay unchanged.",
  "REPLAY_OR_RECHECK": "Imported axioms, oracle calls, admitted lemmas, unsafe extensions and solver semantics must be enumerated.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Maintain an assumption register attached to each theorem/model run: logical axioms, type/units, preconditions, initial-state predicate, rely/fairness conditions, failure semantics, hardware/runtime conditions and configuration. Check consistency and satisfiability, generate witnesses for initial states, instrument testable assumptions, and require downstream consumers to discharge or accept each assumption.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should assurance degrade when an assumption is probabilistic or only partially observable?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Assumptions must be separated from guarantees and must not make the initial condition empty or the desired behaviour impossible to violate.
- Abstraction: Assumptions introduced solely to make an abstraction tractable must be labelled and justified against omitted behaviours.
- Environment: Scheduler, network, hardware, clock, user and operator premises need evidence or explicit residual-risk acceptance.
- Model/code correspondence: Code/configuration must satisfy input domains, memory models, build options and shims presupposed by the result.
- Trusted tools: Imported axioms, oracle calls, admitted lemmas, unsafe extensions and solver semantics must be enumerated.
- Currentness/replay: Assumption changes invalidate the engineering claim even when theorem text and proof term replay unchanged.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Preconditions and assumptions are explicit from Hoare/Dijkstra onward and recur in temporal, refinement and certification sources. | S002, S003, S006, S010, S052 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH | Formal soundness is always conditional; exposing premises preserves the exact conditional theorem. | S002, S044, S093, S094 |
| MECHANICAL_REPLAY_STRENGTH | HIGH_FOR_LOGICAL_PREMISES | Kernels can replay the implication, while operational discharge of premises needs separate evidence. | S021, S022, S095 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_LOW_BY_ITSELF | The register identifies correspondence obligations but does not prove they hold. | S092, S093, S094 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_SELECTED_SYSTEMS | seL4, CompCert, distributed verification and aviation practice make scope assumptions concrete. | S025, S030, S031, S052, S093, S110 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM_HIGH | Empirical distributed defects and proof-version studies show practical assumption/currentness failures. | S092, S095, S100 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH | DO-333 and reusable-component guidance explicitly bind credit to assumptions and usage domain. | S052, S113 |
| TRANSFERABILITY_STRENGTH | HIGH | The property transfers across proof, model checking, static analysis, runtime monitoring and certification. | S062, S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | The conclusion can collapse when even one precondition, scheduler premise or imported axiom changes. | S059, S060, S093 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Vacuity, TCB analysis and field defects provide direct contrary evidence against implicit-premise confidence. | S059, S060, S092, S093, S094 |

**CRITICISMS:**
- Vacuity and inconsistent-environment cases can make a property pass without exercising its subject [S059, S060].
- seL4 and CompCert analyses show that strong proofs still depend on hardware, semantics, low-level code, axioms or external algorithms [S093, S094].
- Verified distributed-system defects often arose where implementation or environment violated proof assumptions [S092].
- Certification documents can make assumptions visible yet still rely on organisational discipline to enforce them [S052, S113].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Every formal result carries a complete, versioned assumption set with satisfiability evidence and an owner/discharge mode for each item. Hidden defaults, imported axioms and environmental premises are surfaced; assumptions that can be enforced or monitored become executable obligations; results are downgraded when deployment cannot establish them.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P008 — Fairness and scheduler assumptions, P039 — Specification gaming and golden theorem drift. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P002 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while assumptions are scattered across code, tactics, library imports and prose rather than enumerated?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P002?
- Would the cheap path — For a trivial local check, encode the precondition directly in the function type/assertion and test the rejection path; do not create a separate assumption bureaucracy — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P002, what decision changes, and should the artefact be retired if no live consumer remains?


### P003 — Environment model boundary

**PROPERTY_ID:** `P003`  
**PROPERTY_NAME:** Environment model boundary

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** A proof or model is an engineering claim only relative to a declared boundary between system, implementation, and environment. It is intended to prevent: Software correctness claims routinely fail at the boundary the model did not include: hardware timing, DMA, weak memory, network loss, clocks, operator action, physical sensing, deployment configuration or unobserved external state.

**MATURE_FORM:** A formal claim identifies exactly which world phenomena are represented and which are assumed. Environment behaviours with material decision impact are either modelled adversarially, enforced by architecture, tested under representative conditions, monitored online, or accepted as named residual risk. Scope changes trigger re-analysis.

**TRIGGER:** Trigger whenever the property depends on networks, clocks, devices, hardware, users, physical processes, external services or any component outside the verified artefact.

**CHEAP_PATH:** For a pure deterministic transformation over fully controlled values, document the input domain and use ordinary pre/postconditions; a separate environment model may add little.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Environment model boundary",
  "ENGINEERING_CLAIM": "A proof or model is an engineering claim only relative to a declared boundary between system, implementation, and environment.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying environment model boundary; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The engineering claim must say whether it concerns abstract design behaviour, source execution, binary execution or world outcomes.",
  "ENVIRONMENT_MODEL": "All material external phenomena are classified and evidence-backed; “the environment behaves” is not an admissible premise.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide environment model boundary; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: The environment is represented as nondeterministic input but important physical constraints or adversarial behaviours are absent.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which define the system/environment cut, controlled and monitored variables, admissible environment transitions, faults, timing and observation model.",
  "SAFETY_LIVENESS_CLASS": "assumption sensitive",
  "ABSTRACTION": "Environment abstraction must over-approximate relevant hostile/fault behaviours for universal claims or disclose under-approximation.",
  "IMPLEMENTATION_CORRESPONDENCE": "Adapters, drivers, shims and deployment configuration crossing the boundary require conformance evidence.",
  "CHEAP_PATH": "For a pure deterministic transformation over fully controlled values, document the input domain and use ordinary pre/postconditions; a separate environment model may add little.",
  "MATURE_FORM": "A formal claim identifies exactly which world phenomena are represented and which are assumed. Environment behaviours with material decision impact are either modelled adversarially, enforced by architecture, tested under representative conditions, monitored online, or accepted as named residual risk. Scope changes trigger re-analysis.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P003; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to environment model boundary.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Software correctness claims routinely fail at the boundary the model did not include: hardware timing, DMA, weak memory, network loss, clocks, operator action, physical sensing, deployment configuration or unobserved external state..",
  "RELATION": "Adapters, drivers, shims and deployment configuration crossing the boundary require conformance evidence.",
  "SOUNDNESS_DUTY": "Environment abstraction must over-approximate relevant hostile/fault behaviours for universal claims or disclose under-approximation.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Fetzer and world–machine analysis reject the inference from abstract program theorem to physical execution [S056, S082].",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "A formal claim identifies exactly which world phenomena are represented and which are assumed. Environment behaviours with material decision impact are either modelled adversarially, enforced by architecture, tested under representative conditions, monitored online, or accepted as named residual risk. Scope changes trigger re-analysis.",
  "KNOWN_GAP": "The environment is represented as nondeterministic input but important physical constraints or adversarial behaviours are absent."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for environment model boundary.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For a pure deterministic transformation over fully controlled values, document the input domain and use ordinary pre/postconditions; a separate environment model may add little."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Environment model boundary may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger whenever the property depends on networks, clocks, devices, hardware, users, physical processes, external services or any component outside the verified artefact.",
  "CHEAPER_EVIDENCE": "For a pure deterministic transformation over fully controlled values, document the input domain and use ordinary pre/postconditions; a separate environment model may add little."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P003.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Adapters, drivers, shims and deployment configuration crossing the boundary require conformance evidence.",
  "ENVIRONMENT_BOUNDARY": "All material external phenomena are classified and evidence-backed; “the environment behaves” is not an admissible premise.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Simulation/emulation, trace collection and model extraction tools that encode environment behaviour are in scope.",
  "DRIFT_DETECTOR": "Platform, device, network policy, scheduler and service-version changes can invalidate the boundary even with unchanged source.",
  "KNOWN_ESCAPE": "The environment is represented as nondeterministic input but important physical constraints or adversarial behaviours are absent."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter environment model boundary.",
  "IDENTITIES_TO_BIND": "Platform, device, network policy, scheduler and service-version changes can invalidate the boundary even with unchanged source.",
  "REPLAY_OR_RECHECK": "Simulation/emulation, trace collection and model extraction tools that encode environment behaviour are in scope.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Define the system/environment cut, controlled and monitored variables, admissible environment transitions, faults, timing and observation model. Classify each external phenomenon as modelled, assumed, monitored, tested, independently assured or out of scope; then connect the formal guarantee to that boundary rather than to an undefined “system”.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should monitor uncertainty be represented in acceptance decisions for partially observable systems?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The engineering claim must say whether it concerns abstract design behaviour, source execution, binary execution or world outcomes.
- Abstraction: Environment abstraction must over-approximate relevant hostile/fault behaviours for universal claims or disclose under-approximation.
- Environment: All material external phenomena are classified and evidence-backed; “the environment behaves” is not an admissible premise.
- Model/code correspondence: Adapters, drivers, shims and deployment configuration crossing the boundary require conformance evidence.
- Trusted tools: Simulation/emulation, trace collection and model extraction tools that encode environment behaviour are in scope.
- Currentness/replay: Platform, device, network policy, scheduler and service-version changes can invalidate the boundary even with unchanged source.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Reactive-system and requirements lineages explicitly distinguish system from environment, reinforced by current verified-system assumption documents. | S006, S017, S081, S082, S093 |
| FORMAL_SOUNDNESS_STRENGTH | CONDITIONAL | A theorem over an environment transition relation is sound for that relation, not evidence that the relation matches reality. | S017, S056 |
| MECHANICAL_REPLAY_STRENGTH | MEDIUM | Models and monitors replay mechanically, but physical/environment observations and calibrations are not reduced to proof replay. | S066, S068, S099 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_TO_MEDIUM | This property defines the correspondence burden; empirical failures show it is often incompletely discharged. | S092, S093 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_FOR_CRITICAL_CASES | seL4, FSCQ, AWS and distributed systems provide concrete boundary practice. | S025, S028, S029, S030, S093 |
| EMPIRICAL_COMPARATIVE_STRENGTH | HIGH_NEGATIVE_EVIDENCE | The distributed-systems defect study directly observes boundary failures; broad comparative benefit studies remain sparse. | S092 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_IN_AVIATION_AND_SECURITY | Assurance guidance and high-assurance kernels require usage/environment assumptions. | S052, S093, S113 |
| TRANSFERABILITY_STRENGTH | HIGH_CONCEPTUALLY | Every deployed formal claim has an environment boundary, though modelling technique is domain-specific. | S065, S082 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Hardware, timing, failure and observability assumptions determine whether the theorem has operational force. | S093, S099, S106 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Philosophical critique, explicit proof assumptions and empirical failures all directly constrain the property. | S056, S092, S093, S099 |

**CRITICISMS:**
- Fetzer and world–machine analysis reject the inference from abstract program theorem to physical execution [S056, S082].
- seL4 explicitly excludes or assumes DMA, side channels, low-level code and hardware properties depending on proof [S093].
- Empirical study of verified distributed systems found failures in unverified interfaces, shims and assumptions [S092].
- Runtime-verification theory emphasises finite-prefix and partial-observation uncertainty [S099].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A formal claim identifies exactly which world phenomena are represented and which are assumed. Environment behaviours with material decision impact are either modelled adversarially, enforced by architecture, tested under representative conditions, monitored online, or accepted as named residual risk. Scope changes trigger re-analysis.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P015 — Model-code correspondence, P031 — Runtime monitor scope. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P003 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while the environment is represented as nondeterministic input but important physical constraints or adversarial behaviours are absent?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P003?
- Would the cheap path — For a pure deterministic transformation over fully controlled values, document the input domain and use ordinary pre/postconditions; a separate environment model may add little — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P003, what decision changes, and should the artefact be retired if no live consumer remains?


### P004 — Explicit state and transition model

**PROPERTY_ID:** `P004`  
**PROPERTY_NAME:** Explicit state and transition model

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Dynamic behaviour should be represented as states, initial conditions and transitions when failures are ordering/state dependent. It is intended to prevent: Ordering, retry, lifecycle and concurrency defects cannot be expressed adequately as static input/output prose. Reviews miss illegal intermediate states, unexpected transition sequences, dead ends and races because the reachable-state structure is implicit.

**MATURE_FORM:** Use a state/transition representation when the risk is sequence-dependent. The model is typed, executable or mechanically analysable, includes invalid and recovery paths, documents atomicity and environment actions, and has a maintained mapping to the artefact or decision it governs.

**TRIGGER:** Trigger for protocols, workflows, lifecycle controllers, distributed coordination, recovery logic, device modes and any defect depending on event order.

**CHEAP_PATH:** For a stateless pure function, a pre/postcondition or property-based test is usually cheaper and more direct.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Explicit state and transition model",
  "ENGINEERING_CLAIM": "Dynamic behaviour should be represented as states, initial conditions and transitions when failures are ordering/state dependent.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying explicit state and transition model; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Initial and transition predicates must be satisfiable and include error/exception paths relevant to acceptance.",
  "ENVIRONMENT_MODEL": "External events and scheduling choices are explicit transitions or declared assumptions.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide explicit state and transition model; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: State variables omit history or environmental facts needed for the property.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which define typed state variables, initial states, atomic actions/transitions, enabling conditions and nondeterminism.",
  "SAFETY_LIVENESS_CLASS": "strongly retained",
  "ABSTRACTION": "Merged states and atomic steps preserve the temporal/invariant distinctions being checked.",
  "IMPLEMENTATION_CORRESPONDENCE": "Each material model action maps to code/API/runtime events with compatible atomicity and data domains.",
  "CHEAP_PATH": "For a stateless pure function, a pre/postcondition or property-based test is usually cheaper and more direct.",
  "MATURE_FORM": "Use a state/transition representation when the risk is sequence-dependent. The model is typed, executable or mechanically analysable, includes invalid and recovery paths, documents atomicity and environment actions, and has a maintained mapping to the artefact or decision it governs.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P004; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to explicit state and transition model.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Ordering, retry, lifecycle and concurrency defects cannot be expressed adequately as static input/output prose. Reviews miss illegal intermediate states, unexpected transition sequences, dead ends and races because the reachable-state structure is implicit..",
  "RELATION": "Each material model action maps to code/API/runtime events with compatible atomicity and data domains.",
  "SOUNDNESS_DUTY": "Merged states and atomic steps preserve the temporal/invariant distinctions being checked.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Finite or abstract state models can be complete for their own transition relation while incomplete for deployment [S045, S056].",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Use a state/transition representation when the risk is sequence-dependent. The model is typed, executable or mechanically analysable, includes invalid and recovery paths, documents atomicity and environment actions, and has a maintained mapping to the artefact or decision it governs.",
  "KNOWN_GAP": "State variables omit history or environmental facts needed for the property."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Dynamic behaviour should be represented as states, initial conditions and transitions when failures are ordering/state dependent.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for explicit state and transition model.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Merged states and atomic steps preserve the temporal/invariant distinctions being checked.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against State variables omit history or environmental facts needed for the property..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Makes illegal states and transition gaps visible, enables counterexample traces, and replaces repeated narrative reasoning about lifecycle or concurrency with a checkable behavioural object."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Explicit state and transition model may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger for protocols, workflows, lifecycle controllers, distributed coordination, recovery logic, device modes and any defect depending on event order.",
  "CHEAPER_EVIDENCE": "For a stateless pure function, a pre/postcondition or property-based test is usually cheaper and more direct."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P004.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Each material model action maps to code/API/runtime events with compatible atomicity and data domains.",
  "ENVIRONMENT_BOUNDARY": "External events and scheduling choices are explicit transitions or declared assumptions.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Parser, simulator/model checker and any model extractor must preserve declared semantics.",
  "DRIFT_DETECTOR": "Event/state schema changes, protocol version changes and implementation refactors trigger model replay and mapping review.",
  "KNOWN_ESCAPE": "State variables omit history or environmental facts needed for the property."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter explicit state and transition model.",
  "IDENTITIES_TO_BIND": "Event/state schema changes, protocol version changes and implementation refactors trigger model replay and mapping review.",
  "REPLAY_OR_RECHECK": "Parser, simulator/model checker and any model extractor must preserve declared semantics.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Define typed state variables, initial states, atomic actions/transitions, enabling conditions and nondeterminism. Execute, simulate, enumerate or prove over the transition system; generate traces for forbidden states, deadlocks and temporal obligations; link actions to implementation events where needed.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "What coverage measures best reveal omitted transitions rather than merely explored model states?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Initial and transition predicates must be satisfiable and include error/exception paths relevant to acceptance.
- Abstraction: Merged states and atomic steps preserve the temporal/invariant distinctions being checked.
- Environment: External events and scheduling choices are explicit transitions or declared assumptions.
- Model/code correspondence: Each material model action maps to code/API/runtime events with compatible atomicity and data domains.
- Trusted tools: Parser, simulator/model checker and any model extractor must preserve declared semantics.
- Currentness/replay: Event/state schema changes, protocol version changes and implementation refactors trigger model replay and mapping review.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Operational/state-machine and model-checking lineages directly establish transition systems as the core representation. | S001, S007, S009, S017, S020 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH | Reachability and temporal results are mathematically strong for the stated transition system. | S006, S007, S017 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Executable models and model checkers replay deterministically under pinned semantics. | S009, S016, S029 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_LOW | Mapping model actions and atomicity to implementation remains an additional engineering proof or test burden. | S092, S106 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | SPIN, AWS, IronFleet and Verdi provide varied practical cases. | S009, S029, S030, S031 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Case evidence is strong; controlled comparisons of state-model use versus alternative design review are limited. | S062, S065 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM_HIGH | State models are recognised in safety/security assurance, but certification does not establish model adequacy. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH_WHEN_SEQUENCE_MATTERS | The property transfers across domains with ordering/state risk, not to every local computation. | S020, S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Initial states, atomicity, environment and abstraction choices dominate result relevance. | S017, S045 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | State explosion and model-code defect evidence strongly delimit overclaiming. | S019, S045, S092, S103 |

**CRITICISMS:**
- Finite or abstract state models can be complete for their own transition relation while incomplete for deployment [S045, S056].
- State explosion makes naïve enumeration infeasible [S008, S019].
- A clean model may not correspond to implementation atomicity or weak-memory behaviour [S092, S106].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Use a state/transition representation when the risk is sequence-dependent. The model is typed, executable or mechanically analysable, includes invalid and recovery paths, documents atomicity and environment actions, and has a maintained mapping to the artefact or decision it governs.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P013 — Sound abstraction discipline, P015 — Model-code correspondence. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P004 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while state variables omit history or environmental facts needed for the property?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P004?
- Would the cheap path — For a stateless pure function, a pre/postcondition or property-based test is usually cheaper and more direct — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P004, what decision changes, and should the artefact be retired if no live consumer remains?


### P005 — State invariant as cheap mechanical guard

**PROPERTY_ID:** `P005`  
**PROPERTY_NAME:** State invariant as cheap mechanical guard

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** A meaningful always-true condition should be executable or mechanically checked before being entrusted to repeated review. It is intended to prevent: Recurring illegal-state defects are repeatedly rediscovered by review or tests because a simple domain rule—nonnegative balance, unique owner, monotone phase, bounded index, valid status combination—is never encoded at the point where state changes.

**MATURE_FORM:** Prefer a small executable invariant when it eliminates a recurring illegal state more cheaply than a full model or theorem. State whether it is continuous, transition-boundary or sampled; prove inductiveness only when making all-reachable-state claims; and connect violation to diagnosis and safe handling.

**TRIGGER:** Trigger for a simple, repeatedly violated state relation with clear local observability and cheap enforcement.

**CHEAP_PATH:** Do not promote every comment to an invariant; use a unit test or ordinary validation where the rule is one-off, noncritical or not continuously meaningful.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "State invariant as cheap mechanical guard",
  "ENGINEERING_CLAIM": "A meaningful always-true condition should be executable or mechanically checked before being entrusted to repeated review.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying state invariant as cheap mechanical guard; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Predicate is nontrivial, satisfiable, tied to acceptance, and explicit about transient/recovery exceptions.",
  "ENVIRONMENT_MODEL": "External updates or concurrent writers are included in enforcement or bounded as assumptions.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide state invariant as cheap mechanical guard; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: The invariant is true but too weak to exclude the actual defect.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which express the smallest decision-relevant state predicate as a compile-time check, database constraint, assertion, static-analysis rule, model invariant or runtime monitor.",
  "SAFETY_LIVENESS_CLASS": "invariant temporal",
  "ABSTRACTION": "The variables checked faithfully represent the state relation; no lossy projection hides violation.",
  "IMPLEMENTATION_CORRESPONDENCE": "The check executes on the authoritative state and cannot be bypassed by an alternate mutation path.",
  "CHEAP_PATH": "Do not promote every comment to an invariant; use a unit test or ordinary validation where the rule is one-off, noncritical or not continuously meaningful.",
  "MATURE_FORM": "Prefer a small executable invariant when it eliminates a recurring illegal state more cheaply than a full model or theorem. State whether it is continuous, transition-boundary or sampled; prove inductiveness only when making all-reachable-state claims; and connect violation to diagnosis and safe handling.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P005; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to state invariant as cheap mechanical guard.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Recurring illegal-state defects are repeatedly rediscovered by review or tests because a simple domain rule—nonnegative balance, unique owner, monotone phase, bounded index, valid status combination—is never encoded at the point where state changes..",
  "RELATION": "The check executes on the authoritative state and cannot be bypassed by an alternate mutation path.",
  "SOUNDNESS_DUTY": "The variables checked faithfully represent the state relation; no lossy projection hides violation.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "More invariants do not imply stronger assurance; strength depends on relation to failure modes and check points.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Prefer a small executable invariant when it eliminates a recurring illegal state more cheaply than a full model or theorem. State whether it is continuous, transition-boundary or sampled; prove inductiveness only when making all-reachable-state claims; and connect violation to diagnosis and safe handling.",
  "KNOWN_GAP": "The invariant is true but too weak to exclude the actual defect."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "A meaningful always-true condition should be executable or mechanically checked before being entrusted to repeated review.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for state invariant as cheap mechanical guard.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "The variables checked faithfully represent the state relation; no lossy projection hides violation.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against The invariant is true but too weak to exclude the actual defect..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Eliminates entire classes of local state corruption at low implementation and review cost, shortens debugging by producing immediate witnesses, and provides a stable acceptance hook."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "State invariant as cheap mechanical guard may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger for a simple, repeatedly violated state relation with clear local observability and cheap enforcement.",
  "CHEAPER_EVIDENCE": "Do not promote every comment to an invariant; use a unit test or ordinary validation where the rule is one-off, noncritical or not continuously meaningful."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P005.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "The check executes on the authoritative state and cannot be bypassed by an alternate mutation path.",
  "ENVIRONMENT_BOUNDARY": "External updates or concurrent writers are included in enforcement or bounded as assumptions.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Assertion compiler, analyser, schema engine or monitor semantics are tested or qualified proportionally.",
  "DRIFT_DETECTOR": "Schema/status/unit changes require invariant review; obsolete invariants are removed rather than left permanently green.",
  "KNOWN_ESCAPE": "The invariant is true but too weak to exclude the actual defect."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter state invariant as cheap mechanical guard.",
  "IDENTITIES_TO_BIND": "Schema/status/unit changes require invariant review; obsolete invariants are removed rather than left permanently green.",
  "REPLAY_OR_RECHECK": "Assertion compiler, analyser, schema engine or monitor semantics are tested or qualified proportionally.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Express the smallest decision-relevant state predicate as a compile-time check, database constraint, assertion, static-analysis rule, model invariant or runtime monitor. Exercise it against known bad states and instrument transition points so violation yields a diagnostic witness.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "When does runtime invariant overhead or false alarm rate exceed the avoided defect cost?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Predicate is nontrivial, satisfiable, tied to acceptance, and explicit about transient/recovery exceptions.
- Abstraction: The variables checked faithfully represent the state relation; no lossy projection hides violation.
- Environment: External updates or concurrent writers are included in enforcement or bounded as assumptions.
- Model/code correspondence: The check executes on the authoritative state and cannot be bypassed by an alternate mutation path.
- Trusted tools: Assertion compiler, analyser, schema engine or monitor semantics are tested or qualified proportionally.
- Currentness/replay: Schema/status/unit changes require invariant review; obsolete invariants are removed rather than left permanently green.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Assertions and invariants are direct foundational objects in program logic and refinement methods. | S001, S002, S010, S011 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_THE_PREDICATE | A checked predicate is exact at its check points; it is not automatically inductive or complete. | S002, S006 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Assertions, static checks and model invariants are readily replayable when enabled and versioned. | S032, S050, S066 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM | Executable placement can give strong code binding, but sampled/bypass paths reduce correspondence. | S066, S099 |
| INDUSTRIAL_CASE_STRENGTH | MEDIUM_HIGH | Astrée, VST and production-focused verification demonstrate use; evidence varies by domain. | S032, S050, S107 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | The 2025 unit-proof study offers bounded empirical support; broad causal ROI evidence remains limited. | S107 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM | Assertions and proof obligations are accepted assurance mechanisms but usually need coverage and configuration evidence. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH_FOR_LOCAL_RULES | The mechanism transfers widely where the predicate is simple and authoritative. | S015, S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Meaning depends on check timing, transient-state policy and authoritative state. | S059, S066 |
| CONTRARY_EVIDENCE_STRENGTH | MEDIUM_HIGH | Vacuity and monitoring-limit literature directly constrain claims; little evidence rejects well-selected local invariants. | S059, S060, S099 |

**CRITICISMS:**
- More invariants do not imply stronger assurance; strength depends on relation to failure modes and check points.
- Vacuous or unreachable-state invariants can pass without constraining behaviour [S059, S060].
- Runtime checks detect a violation but do not by themselves contain or recover from it [S066, S099].
- Focused unit-proof evidence is promising but bounded and not a universal ROI result [S107].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Prefer a small executable invariant when it eliminates a recurring illegal state more cheaply than a full model or theorem. State whether it is continuous, transition-boundary or sampled; prove inductiveness only when making all-reachable-state claims; and connect violation to diagnosis and safe handling.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P006 — Inductive invariant obligation, P042 — Cost/payoff trigger discipline. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P005 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while the invariant is true but too weak to exclude the actual defect?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P005?
- Would the cheap path — Do not promote every comment to an invariant; use a unit test or ordinary validation where the rule is one-off, noncritical or not continuously meaningful — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P005, what decision changes, and should the artefact be retired if no live consumer remains?


### P006 — Inductive invariant obligation

**PROPERTY_ID:** `P006`  
**PROPERTY_NAME:** Inductive invariant obligation

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** An invariant used as all-reachable-states evidence must hold initially and be preserved by every relevant transition. It is intended to prevent: An invariant may hold in observed tests or intended states yet fail after an unexamined transition. Calling it an invariant without proving initiation and consecution confuses sampled evidence with an all-reachable-state theorem.

**MATURE_FORM:** Use inductive proof only when claiming that every reachable state satisfies a predicate. Keep initiation, preservation and transition completeness separate; treat inferred strengthening as reviewable evidence; and downgrade to sampled/runtime evidence when full transition correspondence is unavailable.

**TRIGGER:** Trigger when acceptance requires “all reachable states” rather than checks at selected observations.

**CHEAP_PATH:** Use runtime assertions or bounded exploration when the transition system is unstable, incomplete or the universal claim is unnecessary.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Inductive invariant obligation",
  "ENGINEERING_CLAIM": "An invariant used as all-reachable-states evidence must hold initially and be preserved by every relevant transition.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying inductive invariant obligation; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Initiation and preservation obligations are stated separately; auxiliary invariants do not change the target claim.",
  "ENVIRONMENT_MODEL": "Environment interference appears as transitions or rely conditions.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide inductive invariant obligation; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Initial-state predicate is narrower than deployment initialisation or recovery.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which prove two obligations: every allowed initial state satisfies the predicate, and each enabled transition preserves it assuming it held before.",
  "SAFETY_LIVENESS_CLASS": "invariant temporal",
  "ABSTRACTION": "Abstract transitions conservatively cover concrete steps relevant to preservation.",
  "IMPLEMENTATION_CORRESPONDENCE": "Every concrete state mutation is represented by a preserving abstract step or a proved refinement sequence.",
  "CHEAP_PATH": "Use runtime assertions or bounded exploration when the transition system is unstable, incomplete or the universal claim is unnecessary.",
  "MATURE_FORM": "Use inductive proof only when claiming that every reachable state satisfies a predicate. Keep initiation, preservation and transition completeness separate; treat inferred strengthening as reviewable evidence; and downgrade to sampled/runtime evidence when full transition correspondence is unavailable.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P006; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to inductive invariant obligation.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in An invariant may hold in observed tests or intended states yet fail after an unexamined transition. Calling it an invariant without proving initiation and consecution confuses sampled evidence with an all-reachable-state theorem..",
  "RELATION": "Every concrete state mutation is represented by a preserving abstract step or a proved refinement sequence.",
  "SOUNDNESS_DUTY": "Abstract transitions conservatively cover concrete steps relevant to preservation.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Inductiveness is a proof property, not evidence that the invariant is meaningful or sufficient.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Use inductive proof only when claiming that every reachable state satisfies a predicate. Keep initiation, preservation and transition completeness separate; treat inferred strengthening as reviewable evidence; and downgrade to sampled/runtime evidence when full transition correspondence is unavailable.",
  "KNOWN_GAP": "Initial-state predicate is narrower than deployment initialisation or recovery."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "An invariant used as all-reachable-states evidence must hold initially and be preserved by every relevant transition.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for inductive invariant obligation.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Abstract transitions conservatively cover concrete steps relevant to preservation.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Initial-state predicate is narrower than deployment initialisation or recovery..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Converts a recurring assertion into a universal reachability claim, pinpoints the transition that breaks the rule, and supports modular refinement and model checking."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Inductive invariant obligation may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger when acceptance requires “all reachable states” rather than checks at selected observations.",
  "CHEAPER_EVIDENCE": "Use runtime assertions or bounded exploration when the transition system is unstable, incomplete or the universal claim is unnecessary."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P006.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Every concrete state mutation is represented by a preserving abstract step or a proved refinement sequence.",
  "ENVIRONMENT_BOUNDARY": "Environment interference appears as transitions or rely conditions.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Invariant inference and SMT discharge are either checked by proof/certificate or included in the trust boundary.",
  "DRIFT_DETECTOR": "Any initialisation, state schema or transition change invalidates preservation evidence until replayed and correspondence-reviewed.",
  "KNOWN_ESCAPE": "Initial-state predicate is narrower than deployment initialisation or recovery."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter inductive invariant obligation.",
  "IDENTITIES_TO_BIND": "Any initialisation, state schema or transition change invalidates preservation evidence until replayed and correspondence-reviewed.",
  "REPLAY_OR_RECHECK": "Invariant inference and SMT discharge are either checked by proof/certificate or included in the trust boundary.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Prove two obligations: every allowed initial state satisfies the predicate, and each enabled transition preserves it assuming it held before. Strengthen with auxiliary invariants when necessary; generate counterexamples to failed initiation/preservation; ensure the transition set is complete.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should induction be adapted when the implementation exposes non-atomic weak-memory steps?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Initiation and preservation obligations are stated separately; auxiliary invariants do not change the target claim.
- Abstraction: Abstract transitions conservatively cover concrete steps relevant to preservation.
- Environment: Environment interference appears as transitions or rely conditions.
- Model/code correspondence: Every concrete state mutation is represented by a preserving abstract step or a proved refinement sequence.
- Trusted tools: Invariant inference and SMT discharge are either checked by proof/certificate or included in the trust boundary.
- Currentness/replay: Any initialisation, state schema or transition change invalidates preservation evidence until replayed and correspondence-reviewed.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Initiation and preservation are foundational, explicitly stated proof obligations from Floyd/Hoare through B/Event-B. | S001, S002, S010, S011 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH | Induction is mathematically decisive for reachability over a complete transition system. | S001, S005 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Proof assistants and SMT-backed tools can replay base/preservation obligations exactly. | S044, S050 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_LOW | The all-code claim depends on transition completeness, atomicity and refinement not supplied by induction alone. | S092, S106 |
| INDUSTRIAL_CASE_STRENGTH | MEDIUM_HIGH | Refinement and verified-system cases use inductive invariants extensively, though reports seldom isolate their marginal benefit. | S025, S027, S030 |
| EMPIRICAL_COMPARATIVE_STRENGTH | LOW_MEDIUM | Formal validity is strong; comparative empirical evidence on inferred/readable invariant quality is limited. | S062, S096 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_IN_FORMAL_ASSURANCE | Invariant proof obligations are central in B/Event-B and recognised formal-method assurance. | S010, S011, S052 |
| TRANSFERABILITY_STRENGTH | HIGH_FOR_STATE_SYSTEMS | The structure transfers to any transition system, but not to claims lacking a state/reachability semantics. | S007, S017 |
| ASSUMPTION_SENSITIVITY | HIGH | Completeness of initial states/transitions and auxiliary invariant meaning are decisive. | S059, S092 |
| CONTRARY_EVIDENCE_STRENGTH | MEDIUM_HIGH | Model-code and vacuity criticisms directly qualify engineering use without undermining the induction theorem itself. | S059, S060, S092 |

**CRITICISMS:**
- Inductiveness is a proof property, not evidence that the invariant is meaningful or sufficient.
- Strengthening an invariant can hide failing states if initial/reachability conditions are also narrowed.
- Implementation correspondence and atomicity remain outside a model-only induction proof [S092, S106].
- Automation may produce opaque auxiliary invariants whose engineering interpretation is weak.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Use inductive proof only when claiming that every reachable state satisfies a predicate. Keep initiation, preservation and transition completeness separate; treat inferred strengthening as reviewable evidence; and downgrade to sampled/runtime evidence when full transition correspondence is unavailable.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P005 — State invariant as cheap mechanical guard, P019 — State explosion management. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P006 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while initial-state predicate is narrower than deployment initialisation or recovery?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P006?
- Would the cheap path — Use runtime assertions or bounded exploration when the transition system is unstable, incomplete or the universal claim is unnecessary — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P006, what decision changes, and should the artefact be retired if no live consumer remains?


### P007 — Safety versus liveness distinction

**PROPERTY_ID:** `P007`  
**PROPERTY_NAME:** Safety versus liveness distinction

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Acceptance must distinguish no-bad-state properties from progress/eventuality/termination/availability obligations. It is intended to prevent: A system can preserve every invariant while never completing work, granting service, recovering, electing a leader or terminating. Conversely, a progress test can pass while an unsafe intermediate state occurs. Treating “correctness” as one undifferentiated predicate hides these distinct obligations.

**MATURE_FORM:** Acceptance separates “nothing bad” from “something good” and names the assumptions or time bound behind progress. A safety proof cannot substitute for liveness evidence; an unbounded eventuality cannot substitute for service-level usefulness; monitorability limits are explicit.

**TRIGGER:** Trigger for reactive, concurrent, distributed, workflow, recovery or termination claims where absence of bad states does not guarantee completion.

**CHEAP_PATH:** For a finite terminating function, an ordinary total-correctness contract may cover both result and termination without a temporal model.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Safety versus liveness distinction",
  "ENGINEERING_CLAIM": "Acceptance must distinguish no-bad-state properties from progress/eventuality/termination/availability obligations.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying safety versus liveness distinction; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Safety and liveness clauses are separate; eventualities state fairness and, where needed, deadlines.",
  "ENVIRONMENT_MODEL": "Service availability, retries, message delivery, scheduling and time premises are explicit.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide safety versus liveness distinction; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Only safety is proved while deadlock, starvation or nontermination remains possible.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which classify each obligation as safety, liveness/progress, termination, bounded response, trace/hyperproperty or combination.",
  "SAFETY_LIVENESS_CLASS": "invariant temporal",
  "ABSTRACTION": "Abstraction preserves the property class; stuttering or trace quotienting does not erase relevant progress.",
  "IMPLEMENTATION_CORRESPONDENCE": "Implementation events and scheduler behaviours correspond to the temporal model.",
  "CHEAP_PATH": "For a finite terminating function, an ordinary total-correctness contract may cover both result and termination without a temporal model.",
  "MATURE_FORM": "Acceptance separates “nothing bad” from “something good” and names the assumptions or time bound behind progress. A safety proof cannot substitute for liveness evidence; an unbounded eventuality cannot substitute for service-level usefulness; monitorability limits are explicit.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P007; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to safety versus liveness distinction.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in A system can preserve every invariant while never completing work, granting service, recovering, electing a leader or terminating. Conversely, a progress test can pass while an unsafe intermediate state occurs. Treating “correctness” as one undifferentiated predicate hides these distinct obligations..",
  "RELATION": "Implementation events and scheduler behaviours correspond to the temporal model.",
  "SOUNDNESS_DUTY": "Abstraction preserves the property class; stuttering or trace quotienting does not erase relevant progress.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Liveness proofs are often assumption-heavy and more difficult to automate than safety proofs [S008, S105].",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Acceptance separates “nothing bad” from “something good” and names the assumptions or time bound behind progress. A safety proof cannot substitute for liveness evidence; an unbounded eventuality cannot substitute for service-level usefulness; monitorability limits are explicit.",
  "KNOWN_GAP": "Only safety is proved while deadlock, starvation or nontermination remains possible."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Acceptance must distinguish no-bad-state properties from progress/eventuality/termination/availability obligations.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for safety versus liveness distinction.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Abstraction preserves the property class; stuttering or trace quotienting does not erase relevant progress.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Only safety is proved while deadlock, starvation or nontermination remains possible..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Prevents green safety proofs from masking deadlock or starvation, directs method selection, and makes progress assumptions reviewable and testable."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Safety versus liveness distinction may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger for reactive, concurrent, distributed, workflow, recovery or termination claims where absence of bad states does not guarantee completion.",
  "CHEAPER_EVIDENCE": "For a finite terminating function, an ordinary total-correctness contract may cover both result and termination without a temporal model."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P007.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Implementation events and scheduler behaviours correspond to the temporal model.",
  "ENVIRONMENT_BOUNDARY": "Service availability, retries, message delivery, scheduling and time premises are explicit.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Liveness algorithms, fairness settings and monitor verdict semantics are pinned and reviewable.",
  "DRIFT_DETECTOR": "Scheduler, timeout, retry and queue-policy changes trigger liveness re-analysis even if safety invariants remain unchanged.",
  "KNOWN_ESCAPE": "Only safety is proved while deadlock, starvation or nontermination remains possible."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter safety versus liveness distinction.",
  "IDENTITIES_TO_BIND": "Scheduler, timeout, retry and queue-policy changes trigger liveness re-analysis even if safety invariants remain unchanged.",
  "REPLAY_OR_RECHECK": "Liveness algorithms, fairness settings and monitor verdict semantics are pinned and reviewable.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Classify each obligation as safety, liveness/progress, termination, bounded response, trace/hyperproperty or combination. Use invariants/reachability for bad prefixes; ranking, fairness and temporal reasoning for eventuality; timed formalisms for deadlines; and maintain separate evidence and counterexamples.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "What reviewer-facing forms best communicate hyperproperties and multi-trace obligations?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Safety and liveness clauses are separate; eventualities state fairness and, where needed, deadlines.
- Abstraction: Abstraction preserves the property class; stuttering or trace quotienting does not erase relevant progress.
- Environment: Service availability, retries, message delivery, scheduling and time premises are explicit.
- Model/code correspondence: Implementation events and scheduler behaviours correspond to the temporal model.
- Trusted tools: Liveness algorithms, fairness settings and monitor verdict semantics are pinned and reviewable.
- Currentness/replay: Scheduler, timeout, retry and queue-policy changes trigger liveness re-analysis even if safety invariants remain unchanged.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Pnueli and Alpern–Schneider provide direct foundational provenance, continued in TLA/model checking. | S006, S017, S086 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH | The formal distinction and corresponding theorems are strong for specified traces and fairness. | S006, S086 |
| MECHANICAL_REPLAY_STRENGTH | HIGH_FOR_STATIC_PROOFS | Safety/liveness model checks and theorem proofs replay; runtime liveness verdicts are inherently prefix-limited. | S007, S099, S105 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_LOW | Temporal event and scheduler correspondence requires separate implementation/runtime evidence. | S092, S105 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_CONCURRENT_SYSTEMS | AWS, IronFleet, Verdi and current liveness frameworks demonstrate engineering relevance. | S029, S030, S031, S105 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Case and defect evidence is substantial; comparative ROI evidence remains thin. | S092, S100 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM_HIGH | Safety/liveness obligations appear in critical-system assurance, though exact formalisation is method-specific. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH_FOR_REACTIVE_CLAIMS | The distinction transfers widely but is less salient for simple terminating transformations. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH_FOR_LIVENESS | Fairness, scheduling, timing and environment assumptions dominate progress conclusions. | S008, S105 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Monitorability and fairness criticism materially narrow claims without displacing the distinction. | S021, S092, S099 |

**CRITICISMS:**
- Liveness proofs are often assumption-heavy and more difficult to automate than safety proofs [S008, S105].
- Fairness can make an execution disappear mathematically without making a scheduler fair in deployment.
- Runtime monitors cannot generally decide arbitrary liveness from a finite prefix [S099].
- Security hyperproperties demonstrate that the safety/liveness dichotomy over single traces is not the entire property universe [S021].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Acceptance separates “nothing bad” from “something good” and names the assumptions or time bound behind progress. A safety proof cannot substitute for liveness evidence; an unbounded eventuality cannot substitute for service-level usefulness; monitorability limits are explicit.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P008 — Fairness and scheduler assumptions, P009 — Property-class matching. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P007 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while only safety is proved while deadlock, starvation or nontermination remains possible?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P007?
- Would the cheap path — For a finite terminating function, an ordinary total-correctness contract may cover both result and termination without a temporal model — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P007, what decision changes, and should the artefact be retired if no live consumer remains?


### P008 — Fairness and scheduler assumptions

**PROPERTY_ID:** `P008`  
**PROPERTY_NAME:** Fairness and scheduler assumptions

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Liveness/progress claims must state fairness, scheduling and retry assumptions, and whether they hold in the real runtime. It is intended to prevent: A liveness theorem can be won by assuming that every continuously or repeatedly enabled action eventually runs, every message is retried/delivered, or every process takes steps—conditions that actual schedulers, overload, partitions or failures may not guarantee.

**MATURE_FORM:** A liveness claim lists the precise scheduler, delivery and resource assumptions; each is either enforced, stress-tested, monitored or accepted as a residual condition. Where only unbounded fairness is available, the claim is not presented as a latency or availability guarantee.

**TRIGGER:** Trigger whenever progress depends on scheduling, retries, message delivery, resource allocation or repeated opportunities.

**CHEAP_PATH:** For a synchronous finite procedure with controlled execution, prove termination or enforce a timeout directly rather than introduce abstract fairness.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Fairness and scheduler assumptions",
  "ENGINEERING_CLAIM": "Liveness/progress claims must state fairness, scheduling and retry assumptions, and whether they hold in the real runtime.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying fairness and scheduler assumptions; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Fairness scope is minimal and separate from the property being proved; no global fairness wildcard.",
  "ENVIRONMENT_MODEL": "Delivery, retry, clock, queue and resource assumptions have operational evidence.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide fairness and scheduler assumptions; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Fairness is globally enabled in a model checker although only some actions deserve it.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which state the exact fairness class and subject actions; prove liveness conditionally; identify the runtime mechanism that enforces or approximates it (queue policy, timeout, retry, admission control, watchdog); test hostile schedules and monitor starvation/backlog indicators.",
  "SAFETY_LIVENESS_CLASS": "assumption sensitive",
  "ABSTRACTION": "Abstraction preserves enablement and scheduling distinctions relevant to fairness.",
  "IMPLEMENTATION_CORRESPONDENCE": "Implementation scheduling and retry behaviour match the model’s fairness granularity.",
  "CHEAP_PATH": "For a synchronous finite procedure with controlled execution, prove termination or enforce a timeout directly rather than introduce abstract fairness.",
  "MATURE_FORM": "A liveness claim lists the precise scheduler, delivery and resource assumptions; each is either enforced, stress-tested, monitored or accepted as a residual condition. Where only unbounded fairness is available, the claim is not presented as a latency or availability guarantee.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P008; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to fairness and scheduler assumptions.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in A liveness theorem can be won by assuming that every continuously or repeatedly enabled action eventually runs, every message is retried/delivered, or every process takes steps—conditions that actual schedulers, overload, partitions or failures may not guarantee..",
  "RELATION": "Implementation scheduling and retry behaviour match the model’s fairness granularity.",
  "SOUNDNESS_DUTY": "Abstraction preserves enablement and scheduling distinctions relevant to fairness.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Fairness is often a modelling convenience rather than a deployable mechanism.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "A liveness claim lists the precise scheduler, delivery and resource assumptions; each is either enforced, stress-tested, monitored or accepted as a residual condition. Where only unbounded fairness is available, the claim is not presented as a latency or availability guarantee.",
  "KNOWN_GAP": "Fairness is globally enabled in a model checker although only some actions deserve it."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Liveness/progress claims must state fairness, scheduling and retry assumptions, and whether they hold in the real runtime.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for fairness and scheduler assumptions.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Abstraction preserves enablement and scheduling distinctions relevant to fairness.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Fairness is globally enabled in a model checker although only some actions deserve it..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Exposes hidden progress dependencies, prevents misleading eventuality proofs, and directs engineering toward retries, queue discipline, admission control or bounded-response mechanisms."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Fairness and scheduler assumptions may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger whenever progress depends on scheduling, retries, message delivery, resource allocation or repeated opportunities.",
  "CHEAPER_EVIDENCE": "For a synchronous finite procedure with controlled execution, prove termination or enforce a timeout directly rather than introduce abstract fairness."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P008.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Implementation scheduling and retry behaviour match the model’s fairness granularity.",
  "ENVIRONMENT_BOUNDARY": "Delivery, retry, clock, queue and resource assumptions have operational evidence.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Model-checker fairness settings and liveness algorithms are recorded, not implicit defaults.",
  "DRIFT_DETECTOR": "Priority, timeout, retry, admission-control and infrastructure changes invalidate fairness discharge.",
  "KNOWN_ESCAPE": "Fairness is globally enabled in a model checker although only some actions deserve it."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter fairness and scheduler assumptions.",
  "IDENTITIES_TO_BIND": "Priority, timeout, retry, admission-control and infrastructure changes invalidate fairness discharge.",
  "REPLAY_OR_RECHECK": "Model-checker fairness settings and liveness algorithms are recorded, not implicit defaults.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: State the exact fairness class and subject actions; prove liveness conditionally; identify the runtime mechanism that enforces or approximates it (queue policy, timeout, retry, admission control, watchdog); test hostile schedules and monitor starvation/backlog indicators.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "When should an unbounded liveness theorem be replaced by probabilistic or timed evidence?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Fairness scope is minimal and separate from the property being proved; no global fairness wildcard.
- Abstraction: Abstraction preserves enablement and scheduling distinctions relevant to fairness.
- Environment: Delivery, retry, clock, queue and resource assumptions have operational evidence.
- Model/code correspondence: Implementation scheduling and retry behaviour match the model’s fairness granularity.
- Trusted tools: Model-checker fairness settings and liveness algorithms are recorded, not implicit defaults.
- Currentness/replay: Priority, timeout, retry, admission-control and infrastructure changes invalidate fairness discharge.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Fairness is a documented temporal-logic and concurrent-composition concept with direct use in distributed proofs. | S006, S017, S088, S105 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_CONDITIONALLY | Given the fairness premise, the liveness proof can be rigorous; the premise itself is not proved by temporal logic. | S017, S105 |
| MECHANICAL_REPLAY_STRENGTH | HIGH_FOR_MODEL_RESULT | Proof replay preserves the conditional result; runtime observation cannot generally confirm infinite fairness. | S099, S105 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_TO_MEDIUM | Scheduler and network correspondence are often the weak link and require empirical/architectural evidence. | S092 |
| INDUSTRIAL_CASE_STRENGTH | MEDIUM_HIGH | IronFleet/Verdi and recent liveness frameworks show practical relevance, but protocols remain selective. | S030, S031, S105 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Empirical defect evidence supports the risk; controlled studies of fairness-assumption validity are scarce. | S092 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM | Critical assurance recognises timing/progress assumptions but rarely provides universal fairness validation. | S052 |
| TRANSFERABILITY_STRENGTH | CONTEXT_DEPENDENT | Highly transferable to reactive concurrency, largely irrelevant to controlled finite calculations. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | The conclusion is dominated by scheduler, delivery and resource premises. | S017, S105 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Operational and empirical criticism directly shows why a valid conditional theorem can overclaim deployment progress. | S092, S099 |

**CRITICISMS:**
- Fairness is often a modelling convenience rather than a deployable mechanism.
- Conditional liveness may be mathematically correct but operationally weak under overload or adversarial scheduling.
- Distributed-system defects and current liveness research show that failure and ranking assumptions need explicit validation [S092, S105].
- Finite runtime traces generally cannot establish future fairness [S099].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A liveness claim lists the precise scheduler, delivery and resource assumptions; each is either enforced, stress-tested, monitored or accepted as a residual condition. Where only unbounded fairness is available, the claim is not presented as a latency or availability guarantee.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P007 — Safety versus liveness distinction, P003 — Environment model boundary. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P008 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while fairness is globally enabled in a model checker although only some actions deserve it?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P008?
- Would the cheap path — For a synchronous finite procedure with controlled execution, prove termination or enforce a timeout directly rather than introduce abstract fairness — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P008, what decision changes, and should the artefact be retired if no live consumer remains?


### P009 — Property-class matching

**PROPERTY_ID:** `P009`  
**PROPERTY_NAME:** Property-class matching

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** The method must match property class: invariant, trace, hyperproperty, real-time, probabilistic, information-flow or resource bound. It is intended to prevent: Using the wrong method can produce a green result that does not express the claim: a type checker for functional correctness, an invariant for information flow, bounded search for unbounded termination, or single-trace monitoring for a hyperproperty.

**MATURE_FORM:** Every assurance result states its property class, method fit, approximation and non-covered classes. A type, invariant, monitor, bounded search or theorem is not promoted beyond the semantic guarantee its logic supports.

**TRIGGER:** Trigger whenever a method is being selected or a narrow formal result is used to support a broader class of claim.

**CHEAP_PATH:** For an obvious local property—such as nullness or array bounds—use the direct analyser/type check without a separate taxonomy exercise.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Property-class matching",
  "ENGINEERING_CLAIM": "The method must match property class: invariant, trace, hyperproperty, real-time, probabilistic, information-flow or resource bound.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying property-class matching; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The formal statement’s semantic domain and quantification over states/traces/executions are explicit.",
  "ENVIRONMENT_MODEL": "Timing, probability, observation and adversary models match the selected property class.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide property-class matching; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: A security noninterference claim is encoded as absence of a local bad state.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which classify the claim by semantic shape—state, transition, finite trace, infinite trace, set of traces, quantitative probability, time, resource, refinement/equivalence or type—and select a logic/tool whose soundness theorem covers that class.",
  "SAFETY_LIVENESS_CLASS": "invariant temporal",
  "ABSTRACTION": "Any reduction from one property class to another states side conditions and lost information.",
  "IMPLEMENTATION_CORRESPONDENCE": "The implementation relation preserves the kind of observation used by the property.",
  "CHEAP_PATH": "For an obvious local property—such as nullness or array bounds—use the direct analyser/type check without a separate taxonomy exercise.",
  "MATURE_FORM": "Every assurance result states its property class, method fit, approximation and non-covered classes. A type, invariant, monitor, bounded search or theorem is not promoted beyond the semantic guarantee its logic supports.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P009; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to property-class matching.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Using the wrong method can produce a green result that does not express the claim: a type checker for functional correctness, an invariant for information flow, bounded search for unbounded termination, or single-trace monitoring for a hyperproperty..",
  "RELATION": "The implementation relation preserves the kind of observation used by the property.",
  "SOUNDNESS_DUTY": "Any reduction from one property class to another states side conditions and lost information.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Tool branding encourages method-first rather than claim-first selection.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Every assurance result states its property class, method fit, approximation and non-covered classes. A type, invariant, monitor, bounded search or theorem is not promoted beyond the semantic guarantee its logic supports.",
  "KNOWN_GAP": "A security noninterference claim is encoded as absence of a local bad state."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "The method must match property class: invariant, trace, hyperproperty, real-time, probabilistic, information-flow or resource bound.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for property-class matching.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Any reduction from one property class to another states side conditions and lost information.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against A security noninterference claim is encoded as absence of a local bad state..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Avoids category errors, reduces wasted formalisation, and makes gaps between safety, progress, information flow, timing and quantitative behaviour explicit."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Property-class matching may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger whenever a method is being selected or a narrow formal result is used to support a broader class of claim.",
  "CHEAPER_EVIDENCE": "For an obvious local property—such as nullness or array bounds—use the direct analyser/type check without a separate taxonomy exercise."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P009.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "The implementation relation preserves the kind of observation used by the property.",
  "ENVIRONMENT_BOUNDARY": "Timing, probability, observation and adversary models match the selected property class.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Tool front ends and encodings do not silently reinterpret arithmetic, time, probability or trace semantics.",
  "DRIFT_DETECTOR": "Changes in claim class or observation model require method reassessment, not merely rerunning the old checker.",
  "KNOWN_ESCAPE": "A security noninterference claim is encoded as absence of a local bad state."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter property-class matching.",
  "IDENTITIES_TO_BIND": "Changes in claim class or observation model require method reassessment, not merely rerunning the old checker.",
  "REPLAY_OR_RECHECK": "Tool front ends and encodings do not silently reinterpret arithmetic, time, probability or trace semantics.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Classify the claim by semantic shape—state, transition, finite trace, infinite trace, set of traces, quantitative probability, time, resource, refinement/equivalence or type—and select a logic/tool whose soundness theorem covers that class. Record what is reduced or approximated.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should quantitative uncertainty be combined with deterministic formal obligations?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The formal statement’s semantic domain and quantification over states/traces/executions are explicit.
- Abstraction: Any reduction from one property class to another states side conditions and lost information.
- Environment: Timing, probability, observation and adversary models match the selected property class.
- Model/code correspondence: The implementation relation preserves the kind of observation used by the property.
- Trusted tools: Tool front ends and encodings do not silently reinterpret arithmetic, time, probability or trace semantics.
- Currentness/replay: Changes in claim class or observation model require method reassessment, not merely rerunning the old checker.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Plural foundational lineages explicitly define distinct semantic property classes. | S002, S006, S018, S019, S021, S045 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH | Method soundness is strong when the property belongs to the logic’s semantic class and side conditions hold. | S005, S021 |
| MECHANICAL_REPLAY_STRENGTH | HIGH_WITHIN_METHOD | Checks replay mechanically; cross-logic translations and classification choices remain review obligations. | S038, S044, S099 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_LOW | Property-class fit does not itself establish implementation observations or environment semantics. | S092, S106 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | Industrial cases use different methods for different claims: Astrée, AWS, CompCert, crypto and runtime monitoring. | S029, S032, S077, S099 |
| EMPIRICAL_COMPARATIVE_STRENGTH | LOW_MEDIUM | The taxonomy is theoretically strong; comparative evidence that classification improves outcomes is indirect. | S062, S065 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_IN_DOMAIN_GUIDANCE | DO-333 distinguishes theorem proving, model checking and abstract interpretation and their objectives. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH | Claim-shaped method selection is broadly transferable even though particular methods are specialised. | S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Semantic class, arithmetic, observation and environment choices can invalidate a method match. | S021, S106 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Hyperproperty, boundedness, monitorability and type-boundary evidence directly counters one-method overclaiming. | S021, S099, S106 |

**CRITICISMS:**
- Tool branding encourages method-first rather than claim-first selection.
- Reductions can be sound only under side conditions that disappear in user-facing reports.
- Hyperproperties and weak-memory formalisms demonstrate that ordinary trace/invariant models can be structurally inadequate [S021, S106].
- Specialised methods improve fit but increase expertise and integration cost.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Every assurance result states its property class, method fit, approximation and non-covered classes. A type, invariant, monitor, bounded search or theorem is not promoted beyond the semantic guarantee its logic supports.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P007 — Safety versus liveness distinction, P042 — Cost/payoff trigger discipline. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P009 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while a security noninterference claim is encoded as absence of a local bad state?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P009?
- Would the cheap path — For an obvious local property—such as nullness or array bounds—use the direct analyser/type check without a separate taxonomy exercise — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P009, what decision changes, and should the artefact be retired if no live consumer remains?


### P010 — Contracts, preconditions and postconditions

**PROPERTY_ID:** `P010`  
**PROPERTY_NAME:** Contracts, preconditions and postconditions

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Component obligations should be stated as pre/postconditions and frame/interface contracts when substitution/composition matters. It is intended to prevent: Components fail in composition because callers and implementers hold different beliefs about valid inputs, outputs, side effects, exceptions, ownership, timing or protocol state. Interface prose is precise-looking but not executable or substitution-safe.

**MATURE_FORM:** A contract is a machine-consumed boundary artefact: callers can be checked against assumptions, implementations against guarantees, side effects and exceptional behaviour are explicit, and substitution/version changes are verified. Unenforced prose is not counted as contract evidence.

**TRIGGER:** Trigger at reusable component, library, API, plugin or service boundaries where independent change or substitution is expected.

**CHEAP_PATH:** For an internal one-use helper with obvious typed inputs, ordinary type checks and tests may be cheaper than a full contract layer.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Contracts, preconditions and postconditions",
  "ENGINEERING_CLAIM": "Component obligations should be stated as pre/postconditions and frame/interface contracts when substitution/composition matters.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying contracts, preconditions and postconditions; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Normal, exceptional and side-effect behaviour is covered; preconditions are not an escape hatch for likely failures.",
  "ENVIRONMENT_MODEL": "External service, clock, storage or user assumptions at the boundary are explicit.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide contracts, preconditions and postconditions; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Preconditions shift responsibility to callers and exclude common misuse without detection.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which attach typed preconditions, postconditions, exceptional outcomes, frame/effect clauses and invariants to an interface; statically prove or dynamically check callers and implementations; generate tests/witnesses for boundary cases; enforce behavioural-subtyping rules for replacement components.",
  "SAFETY_LIVENESS_CLASS": "contract composition",
  "ABSTRACTION": "Contract abstractions retain observations needed by clients and do not hide relevant resource or temporal effects.",
  "IMPLEMENTATION_CORRESPONDENCE": "Contracts are generated from, compiled with, or checked against the actual interface implementation/version.",
  "CHEAP_PATH": "For an internal one-use helper with obvious typed inputs, ordinary type checks and tests may be cheaper than a full contract layer.",
  "MATURE_FORM": "A contract is a machine-consumed boundary artefact: callers can be checked against assumptions, implementations against guarantees, side effects and exceptional behaviour are explicit, and substitution/version changes are verified. Unenforced prose is not counted as contract evidence.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P010; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to contracts, preconditions and postconditions.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Components fail in composition because callers and implementers hold different beliefs about valid inputs, outputs, side effects, exceptions, ownership, timing or protocol state. Interface prose is precise-looking but not executable or substitution-safe..",
  "RELATION": "Contracts are generated from, compiled with, or checked against the actual interface implementation/version.",
  "SOUNDNESS_DUTY": "Contract abstractions retain observations needed by clients and do not hide relevant resource or temporal effects.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Contracts can become blame-shifting documentation rather than assurance if preconditions are not enforced.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "A contract is a machine-consumed boundary artefact: callers can be checked against assumptions, implementations against guarantees, side effects and exceptional behaviour are explicit, and substitution/version changes are verified. Unenforced prose is not counted as contract evidence.",
  "KNOWN_GAP": "Preconditions shift responsibility to callers and exclude common misuse without detection."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Component obligations should be stated as pre/postconditions and frame/interface contracts when substitution/composition matters.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for contracts, preconditions and postconditions.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Contract abstractions retain observations needed by clients and do not hide relevant resource or temporal effects.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Preconditions shift responsibility to callers and exclude common misuse without detection..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Localises defects at component boundaries, supports safe substitution and modular verification, generates focused tests, and reduces integration ambiguity."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Contracts, preconditions and postconditions may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger at reusable component, library, API, plugin or service boundaries where independent change or substitution is expected.",
  "CHEAPER_EVIDENCE": "For an internal one-use helper with obvious typed inputs, ordinary type checks and tests may be cheaper than a full contract layer."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P010.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Contracts are generated from, compiled with, or checked against the actual interface implementation/version.",
  "ENVIRONMENT_BOUNDARY": "External service, clock, storage or user assumptions at the boundary are explicit.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Contract compiler, verifier, wrapper or runtime checker is within the assurance boundary.",
  "DRIFT_DETECTOR": "API/schema/version changes trigger caller and implementation rechecking; stale consumers are identified.",
  "KNOWN_ESCAPE": "Preconditions shift responsibility to callers and exclude common misuse without detection."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter contracts, preconditions and postconditions.",
  "IDENTITIES_TO_BIND": "API/schema/version changes trigger caller and implementation rechecking; stale consumers are identified.",
  "REPLAY_OR_RECHECK": "Contract compiler, verifier, wrapper or runtime checker is within the assurance boundary.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Attach typed preconditions, postconditions, exceptional outcomes, frame/effect clauses and invariants to an interface; statically prove or dynamically check callers and implementations; generate tests/witnesses for boundary cases; enforce behavioural-subtyping rules for replacement components.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How can human-readable contracts remain aligned with machine-oriented verification conditions?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Normal, exceptional and side-effect behaviour is covered; preconditions are not an escape hatch for likely failures.
- Abstraction: Contract abstractions retain observations needed by clients and do not hide relevant resource or temporal effects.
- Environment: External service, clock, storage or user assumptions at the boundary are explicit.
- Model/code correspondence: Contracts are generated from, compiled with, or checked against the actual interface implementation/version.
- Trusted tools: Contract compiler, verifier, wrapper or runtime checker is within the assurance boundary.
- Currentness/replay: API/schema/version changes trigger caller and implementation rechecking; stale consumers are identified.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Hoare logic, Larch, separation logic and behavioural subtyping give direct historical and formal provenance. | S002, S014, S048, S089 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH | Pre/post/frame obligations are mathematically precise for sequential or specified interface semantics. | S002, S048 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Static contracts and runtime checks are replayable when bound to exact code and configuration. | S047, S050 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_HIGH_WHEN_EXECUTABLE | Binding can be strong at compiled/runtime boundaries, but prose or generated-stub drift remains possible. | S100 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | VST, refinement-type practice and industrial verifiers demonstrate component-contract use. | S047, S050, S100 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Practitioner evidence supports workflow value and cost; controlled comparative effects remain limited. | S100 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_IN_FORMAL_SOFTWARE_ASSURANCE | Contract/proof obligations are accepted evidence forms in DO-333 contexts. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH_AT_COMPONENT_BOUNDARIES | The property transfers broadly, though temporal/concurrent interfaces need stronger forms. | S065, S089 |
| ASSUMPTION_SENSITIVITY | HIGH | Completeness, exception/effect scope and enforcement determine engineering value. | S089, S100 |
| CONTRARY_EVIDENCE_STRENGTH | MEDIUM_HIGH | Criticism mainly narrows scope and enforcement; little contrary evidence rejects well-designed executable contracts. | S055, S100 |

**CRITICISMS:**
- Contracts can become blame-shifting documentation rather than assurance if preconditions are not enforced.
- Local pre/postconditions may not express temporal protocol, concurrency or whole-system liveness.
- Behavioural subtyping depends on a sufficiently complete behavioural specification [S089].
- Dynamic contract checking samples executions and can add overhead; static proof adds annotation and maintenance cost.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A contract is a machine-consumed boundary artefact: callers can be checked against assumptions, implementations against guarantees, side effects and exceptional behaviour are explicit, and substitution/version changes are verified. Unenforced prose is not counted as contract evidence.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P011 — Local reasoning, frame and ownership conditions, P012 — Assume/guarantee and compositional verification. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P010 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while preconditions shift responsibility to callers and exclude common misuse without detection?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P010?
- Would the cheap path — For an internal one-use helper with obvious typed inputs, ordinary type checks and tests may be cheaper than a full contract layer — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P010, what decision changes, and should the artefact be retired if no live consumer remains?


### P011 — Local reasoning, frame and ownership conditions

**PROPERTY_ID:** `P011`  
**PROPERTY_NAME:** Local reasoning, frame and ownership conditions

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Heap/resource effects must be bounded by frame/ownership conditions where local reasoning is decisive. It is intended to prevent: Whole-state specifications make modular verification brittle: every unrelated heap extension, alias or concurrent update can invalidate a proof. Unstated footprints allow components to corrupt memory/resources outside their intended authority.

**MATURE_FORM:** For aliasing or shared-resource risk, each component has a machine-checkable footprint, frame/effect condition and transfer protocol. Safe interfaces encapsulate verified unsafe kernels; non-memory effects are either modelled or explicitly excluded.

**TRIGGER:** Trigger for pointer-rich, aliasing, concurrent, resource-owning or unsafe-code components where mutation authority is central.

**CHEAP_PATH:** For immutable data or simple value-passing code, ordinary types and pre/postconditions are often sufficient.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Local reasoning, frame and ownership conditions",
  "ENGINEERING_CLAIM": "Heap/resource effects must be bounded by frame/ownership conditions where local reasoning is decisive.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying local reasoning, frame and ownership conditions; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Footprints include exceptional exits and non-memory resources material to clients.",
  "ENVIRONMENT_MODEL": "External actors cannot mutate owned state except through modelled interfaces.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide local reasoning, frame and ownership conditions; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Aliasing violates the assumed disjointness or ownership partition.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which specify the footprint a component owns, the resources it may mutate, the invariants protecting shared resources, and the protocol for ownership transfer.",
  "SAFETY_LIVENESS_CLASS": "contract composition",
  "ABSTRACTION": "Logical resources faithfully represent concrete ownership and interference; ghost state is justified.",
  "IMPLEMENTATION_CORRESPONDENCE": "Compiler/runtime memory and concurrency semantics support the ownership claims, including unsafe code.",
  "CHEAP_PATH": "For immutable data or simple value-passing code, ordinary types and pre/postconditions are often sufficient.",
  "MATURE_FORM": "For aliasing or shared-resource risk, each component has a machine-checkable footprint, frame/effect condition and transfer protocol. Safe interfaces encapsulate verified unsafe kernels; non-memory effects are either modelled or explicitly excluded.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P011; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to local reasoning, frame and ownership conditions.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Whole-state specifications make modular verification brittle: every unrelated heap extension, alias or concurrent update can invalidate a proof. Unstated footprints allow components to corrupt memory/resources outside their intended authority..",
  "RELATION": "Compiler/runtime memory and concurrency semantics support the ownership claims, including unsafe code.",
  "SOUNDNESS_DUTY": "Logical resources faithfully represent concrete ownership and interference; ghost state is justified.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Local reasoning is only as sound as the semantic account of resources and interference.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "For aliasing or shared-resource risk, each component has a machine-checkable footprint, frame/effect condition and transfer protocol. Safe interfaces encapsulate verified unsafe kernels; non-memory effects are either modelled or explicitly excluded.",
  "KNOWN_GAP": "Aliasing violates the assumed disjointness or ownership partition."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Heap/resource effects must be bounded by frame/ownership conditions where local reasoning is decisive.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for local reasoning, frame and ownership conditions.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Logical resources faithfully represent concrete ownership and interference; ghost state is justified.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Aliasing violates the assumed disjointness or ownership partition..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Reduces proof blast radius, prevents unauthorised mutation/use-after-free classes, supports parallel reasoning, and enables reusable verified libraries behind stable interfaces."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Local reasoning, frame and ownership conditions may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger for pointer-rich, aliasing, concurrent, resource-owning or unsafe-code components where mutation authority is central.",
  "CHEAPER_EVIDENCE": "For immutable data or simple value-passing code, ordinary types and pre/postconditions are often sufficient."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P011.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Compiler/runtime memory and concurrency semantics support the ownership claims, including unsafe code.",
  "ENVIRONMENT_BOUNDARY": "External actors cannot mutate owned state except through modelled interfaces.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "The separation-logic verifier, SMT encoding and language semantics belong to the trusted/certified chain.",
  "DRIFT_DETECTOR": "Representation, alias, unsafe-block and concurrency-protocol changes trigger local and dependent proof replay.",
  "KNOWN_ESCAPE": "Aliasing violates the assumed disjointness or ownership partition."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter local reasoning, frame and ownership conditions.",
  "IDENTITIES_TO_BIND": "Representation, alias, unsafe-block and concurrency-protocol changes trigger local and dependent proof replay.",
  "REPLAY_OR_RECHECK": "The separation-logic verifier, SMT encoding and language semantics belong to the trusted/certified chain.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Specify the footprint a component owns, the resources it may mutate, the invariants protecting shared resources, and the protocol for ownership transfer. Apply frame/locality rules to extend a local proof to disjoint state; verify unsafe or foreign-code boundaries separately.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should proof refactoring preserve ghost-state and resource-algebra abstractions?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Footprints include exceptional exits and non-memory resources material to clients.
- Abstraction: Logical resources faithfully represent concrete ownership and interference; ghost state is justified.
- Environment: External actors cannot mutate owned state except through modelled interfaces.
- Model/code correspondence: Compiler/runtime memory and concurrency semantics support the ownership claims, including unsafe code.
- Trusted tools: The separation-logic verifier, SMT encoding and language semantics belong to the trusted/certified chain.
- Currentness/replay: Representation, alias, unsafe-block and concurrency-protocol changes trigger local and dependent proof replay.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Separation logic and concurrent local reasoning directly establish frame/ownership mechanisms. | S048, S049 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH | Frame and ownership theorems are strong under the stated heap/resource semantics. | S048, S049 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Proof-assistant and VST developments replay detailed local proofs mechanically. | S050 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_HIGH_IN_VERIFIED_LANGUAGES | Correspondence can be strong with a formal C/Rust semantics, but unsafe/FFI/device effects remain boundaries. | S046, S050 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_SYSTEMS_AND_LANGUAGES | VST and RustBelt provide substantial domain evidence; wider ordinary-industry evidence is selective. | S046, S050 |
| EMPIRICAL_COMPARATIVE_STRENGTH | LOW_MEDIUM | Formal case studies dominate; comparative empirical maintenance/productivity evidence is sparse. | S096 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM_HIGH | Memory/resource proofs can support high-assurance evidence, though certification rarely mandates this specific logic. | S052 |
| TRANSFERABILITY_STRENGTH | CONTEXT_DEPENDENT | Highly transferable to mutable shared resources, less useful for pure or coarse-grained systems. | S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Aliasing, unsafe code, resource semantics and weak memory determine sound applicability. | S046, S106 |
| CONTRARY_EVIDENCE_STRENGTH | MEDIUM_HIGH | Criticism narrows modelling and cost boundaries; no strong evidence rejects the property in its proper domain. | S096, S106 |

**CRITICISMS:**
- Local reasoning is only as sound as the semantic account of resources and interference.
- Physical resources, timing and distributed ownership may not fit a heap-disjointness model.
- RustBelt demonstrates that unsafe libraries still require deep semantic verification beneath a safe type interface [S046].
- Concurrency and weak-memory behaviours can invalidate naïve ownership intuitions [S106].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—For aliasing or shared-resource risk, each component has a machine-checkable footprint, frame/effect condition and transfer protocol. Safe interfaces encapsulate verified unsafe kernels; non-memory effects are either modelled or explicitly excluded.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P010 — Contracts, preconditions and postconditions, P012 — Assume/guarantee and compositional verification. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P011 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while aliasing violates the assumed disjointness or ownership partition?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P011?
- Would the cheap path — For immutable data or simple value-passing code, ordinary types and pre/postconditions are often sufficient — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P011, what decision changes, and should the artefact be retired if no live consumer remains?


### P012 — Assume/guarantee and compositional verification

**PROPERTY_ID:** `P012`  
**PROPERTY_NAME:** Assume/guarantee and compositional verification

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Large systems require component guarantees checked against explicit assumptions rather than monolithic unstated context. It is intended to prevent: Monolithic verification does not scale, but independently verified components may not compose because each assumes behaviour the others do not guarantee. Hidden cross-component dependencies survive local proofs.

**MATURE_FORM:** Large systems are decomposed by explicit, versioned assumptions and guarantees that compose mechanically. Circularity, global invariants, liveness and shared resource bounds are checked separately; contracts with no live consumer are not retained as ceremony.

**TRIGGER:** Trigger for independently developed or replaceable components where whole-system exploration/proof is infeasible.

**CHEAP_PATH:** For a tiny tightly coupled component set, direct integration tests or one finite model may be clearer and cheaper.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Assume/guarantee and compositional verification",
  "ENGINEERING_CLAIM": "Large systems require component guarantees checked against explicit assumptions rather than monolithic unstated context.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying assume/guarantee and compositional verification; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Assumptions and guarantees are separately satisfiable, noncircular and cover exceptions/faults.",
  "ENVIRONMENT_MODEL": "Peers and external environment can demonstrably meet each rely condition.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide assume/guarantee and compositional verification; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Rely conditions are stronger than peer guarantees or deployment behaviour.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which for each component state an assumption about environment actions and a guarantee about its own actions.",
  "SAFETY_LIVENESS_CLASS": "contract composition",
  "ABSTRACTION": "Interface abstractions preserve interactions relevant to the global claim.",
  "IMPLEMENTATION_CORRESPONDENCE": "Runtime component boundaries and versions match contract identities and event semantics.",
  "CHEAP_PATH": "For a tiny tightly coupled component set, direct integration tests or one finite model may be clearer and cheaper.",
  "MATURE_FORM": "Large systems are decomposed by explicit, versioned assumptions and guarantees that compose mechanically. Circularity, global invariants, liveness and shared resource bounds are checked separately; contracts with no live consumer are not retained as ceremony.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P012; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to assume/guarantee and compositional verification.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Monolithic verification does not scale, but independently verified components may not compose because each assumes behaviour the others do not guarantee. Hidden cross-component dependencies survive local proofs..",
  "RELATION": "Runtime component boundaries and versions match contract identities and event semantics.",
  "SOUNDNESS_DUTY": "Interface abstractions preserve interactions relevant to the global claim.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Assume/guarantee can relocate rather than eliminate the specification problem.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Large systems are decomposed by explicit, versioned assumptions and guarantees that compose mechanically. Circularity, global invariants, liveness and shared resource bounds are checked separately; contracts with no live consumer are not retained as ceremony.",
  "KNOWN_GAP": "Rely conditions are stronger than peer guarantees or deployment behaviour."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Large systems require component guarantees checked against explicit assumptions rather than monolithic unstated context.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for assume/guarantee and compositional verification.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Interface abstractions preserve interactions relevant to the global claim.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Rely conditions are stronger than peer guarantees or deployment behaviour..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Reduces verification state/proof size, supports independent teams and safe substitution, and makes hidden integration assumptions reviewable."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Assume/guarantee and compositional verification may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger for independently developed or replaceable components where whole-system exploration/proof is infeasible.",
  "CHEAPER_EVIDENCE": "For a tiny tightly coupled component set, direct integration tests or one finite model may be clearer and cheaper."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P012.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Runtime component boundaries and versions match contract identities and event semantics.",
  "ENVIRONMENT_BOUNDARY": "Peers and external environment can demonstrably meet each rely condition.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Compositional checker and contract translator preserve conjunction, hiding and refinement semantics.",
  "DRIFT_DETECTOR": "Component, dependency or interface changes trigger compatibility and affected-global-property replay.",
  "KNOWN_ESCAPE": "Rely conditions are stronger than peer guarantees or deployment behaviour."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter assume/guarantee and compositional verification.",
  "IDENTITIES_TO_BIND": "Component, dependency or interface changes trigger compatibility and affected-global-property replay.",
  "REPLAY_OR_RECHECK": "Compositional checker and contract translator preserve conjunction, hiding and refinement semantics.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: For each component state an assumption about environment actions and a guarantee about its own actions. Check local correctness under the rely condition, compatibility between guarantees and peers’ relies, invariant closure, circularity/well-foundedness and interface refinement. Recheck composition on substitution.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should empirical service-level behaviour discharge quantitative assume/guarantee conditions?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Assumptions and guarantees are separately satisfiable, noncircular and cover exceptions/faults.
- Abstraction: Interface abstractions preserve interactions relevant to the global claim.
- Environment: Peers and external environment can demonstrably meet each rely condition.
- Model/code correspondence: Runtime component boundaries and versions match contract identities and event semantics.
- Trusted tools: Compositional checker and contract translator preserve conjunction, hiding and refinement semantics.
- Currentness/replay: Component, dependency or interface changes trigger compatibility and affected-global-property replay.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Owicki–Gries and Jones provide direct foundational compositional lineages. | S087, S088 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_CONDITIONALLY | Local and composition theorems are rigorous when compatibility, circularity and closure conditions hold. | S087, S088 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Contracts and composition proofs can be replayed with exact component versions. | S030, S031 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM | Interface-to-code correspondence and unmodelled integration shims remain separate burdens. | S092 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_VERIFIED_DISTRIBUTED_AND_KERNEL_CASES | Verdi, IronFleet and CertiKOS use layered/compositional structures. | S027, S030, S031 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Case evidence is strong; controlled evidence on optimal contract granularity is weak. | S062, S096 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM_HIGH | Compositional evidence is compatible with assurance standards but method-specific. | S052 |
| TRANSFERABILITY_STRENGTH | HIGH_FOR_MODULAR_SYSTEMS | Broadly transferable where boundaries are real and stable; not universally cheapest. | S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Compatibility, circularity, global liveness and interface fidelity determine validity. | S088, S092 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Integration defects and hidden-assumption criticism materially constrain naïve compositional confidence. | S055, S092 |

**CRITICISMS:**
- Assume/guarantee can relocate rather than eliminate the specification problem.
- Checking interface compatibility may still require global reasoning for cyclic liveness or quantitative resources.
- Contracts can become bureaucratic if no substitution or decision consumes them.
- Empirical model-code defects show that verified component abstractions can fail at integration shims [S092].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Large systems are decomposed by explicit, versioned assumptions and guarantees that compose mechanically. Circularity, global invariants, liveness and shared resource bounds are checked separately; contracts with no live consumer are not retained as ceremony.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P003 — Environment model boundary, P015 — Model-code correspondence. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P012 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while rely conditions are stronger than peer guarantees or deployment behaviour?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P012?
- Would the cheap path — For a tiny tightly coupled component set, direct integration tests or one finite model may be clearer and cheaper — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P012, what decision changes, and should the artefact be retired if no live consumer remains?


### P013 — Sound abstraction discipline

**PROPERTY_ID:** `P013`  
**PROPERTY_NAME:** Sound abstraction discipline

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Abstraction must preserve properties needed by the claim and mark over/under-approximation explicitly. It is intended to prevent: Concrete programs and systems are too large or infinite to analyse directly. Removing details can make analysis tractable, but an unsound or claim-inappropriate abstraction can miss real failures or generate unusable spurious alarms.

**MATURE_FORM:** Every abstract result states approximation direction, preserved property, omitted distinctions and spurious-result policy. Sound over-approximation supports absence claims only for the modelled concrete semantics; under-approximation supports witness finding only. Precision is tuned to a named decision.

**TRIGGER:** Trigger when exact state exploration or proof is infeasible but a conservative or witness-seeking approximation can answer a material question.

**CHEAP_PATH:** For small finite systems or deterministic local rules, analyse the concrete state directly instead of introducing abstraction risk.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Sound abstraction discipline",
  "ENGINEERING_CLAIM": "Abstraction must preserve properties needed by the claim and mark over/under-approximation explicitly.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying sound abstraction discipline; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The property is preserved by the chosen abstraction relation.",
  "ENVIRONMENT_MODEL": "Concrete semantics includes relevant environment/hardware effects before abstraction.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide sound abstraction discipline; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: An under-approximation is reported as proof of absence.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which define concrete and abstract domains, abstraction/concretisation relation, direction of approximation and property-preservation theorem.",
  "SAFETY_LIVENESS_CLASS": "abstraction refinement",
  "ABSTRACTION": "Soundness theorem, domain/transfer-function correctness and precision controls are explicit.",
  "IMPLEMENTATION_CORRESPONDENCE": "The “concrete” analysed model corresponds to source/binary/runtime at the claimed level.",
  "CHEAP_PATH": "For small finite systems or deterministic local rules, analyse the concrete state directly instead of introducing abstraction risk.",
  "MATURE_FORM": "Every abstract result states approximation direction, preserved property, omitted distinctions and spurious-result policy. Sound over-approximation supports absence claims only for the modelled concrete semantics; under-approximation supports witness finding only. Precision is tuned to a named decision.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P013; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to sound abstraction discipline.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Concrete programs and systems are too large or infinite to analyse directly. Removing details can make analysis tractable, but an unsound or claim-inappropriate abstraction can miss real failures or generate unusable spurious alarms..",
  "RELATION": "The “concrete” analysed model corresponds to source/binary/runtime at the claimed level.",
  "SOUNDNESS_DUTY": "Soundness theorem, domain/transfer-function correctness and precision controls are explicit.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Soundness and usefulness trade off: a perfectly sound analysis can be operationally unusable.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Every abstract result states approximation direction, preserved property, omitted distinctions and spurious-result policy. Sound over-approximation supports absence claims only for the modelled concrete semantics; under-approximation supports witness finding only. Precision is tuned to a named decision.",
  "KNOWN_GAP": "An under-approximation is reported as proof of absence."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Abstraction must preserve properties needed by the claim and mark over/under-approximation explicitly.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for sound abstraction discipline.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Soundness theorem, domain/transfer-function correctness and precision controls are explicit.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against An under-approximation is reported as proof of absence..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Makes otherwise intractable analysis possible, supports scalable static checking/model checking, and turns spurious traces into a disciplined refinement loop."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Sound abstraction discipline may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger when exact state exploration or proof is infeasible but a conservative or witness-seeking approximation can answer a material question.",
  "CHEAPER_EVIDENCE": "For small finite systems or deterministic local rules, analyse the concrete state directly instead of introducing abstraction risk."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P013.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "The “concrete” analysed model corresponds to source/binary/runtime at the claimed level.",
  "ENVIRONMENT_BOUNDARY": "Concrete semantics includes relevant environment/hardware effects before abstraction.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Abstract transformers, widening, solver and front-end encodings are trusted or checked.",
  "DRIFT_DETECTOR": "Code/semantics/property changes can invalidate domain assumptions and require abstraction regression.",
  "KNOWN_ESCAPE": "An under-approximation is reported as proof of absence."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter sound abstraction discipline.",
  "IDENTITIES_TO_BIND": "Code/semantics/property changes can invalidate domain assumptions and require abstraction regression.",
  "REPLAY_OR_RECHECK": "Abstract transformers, widening, solver and front-end encodings are trusted or checked.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Define concrete and abstract domains, abstraction/concretisation relation, direction of approximation and property-preservation theorem. For over-approximation, all concrete behaviours must be represented; for under-approximation, claims are explicitly bug-finding only. Validate precision through counterexamples, CEGAR, domain-specific abstractions and sound numerical models.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should learned/AI-generated abstractions be independently validated?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The property is preserved by the chosen abstraction relation.
- Abstraction: Soundness theorem, domain/transfer-function correctness and precision controls are explicit.
- Environment: Concrete semantics includes relevant environment/hardware effects before abstraction.
- Model/code correspondence: The “concrete” analysed model corresponds to source/binary/runtime at the claimed level.
- Trusted tools: Abstract transformers, widening, solver and front-end encodings are trusted or checked.
- Currentness/replay: Code/semantics/property changes can invalidate domain assumptions and require abstraction regression.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Cousot–Cousot and CEGAR provide direct mathematical and algorithmic provenance. | S005, S061 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_CONDITIONALLY | Sound over-approximation provides rigorous absence results under its concrete semantics; under-approximation does not. | S005 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Static analyses and model-checking abstraction loops are mechanically repeatable. | S032, S033 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_LOW | The abstraction theorem starts from a formal concrete model, not necessarily deployed code/environment. | S092 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_SELECTED_DOMAINS | Astrée and SDV demonstrate major industrial applications of tailored abstraction. | S032, S033 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Industrial cases are strong but comparative false-positive/effort data are domain-dependent. | S064, S065 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_FOR_ABSTRACT_INTERPRETATION_IN_AVIATION | DO-333 case studies treat abstract interpretation as a recognised formal-method technique. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH_AS_A_PRINCIPLE | Approximation discipline transfers broadly; individual domains and soundness costs do not. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Direction, concrete semantics, property preservation and precision determine the result. | S005, S061 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | State-explosion, spuriousness, incompleteness and empirical correspondence evidence strongly constrain use. | S061, S092, S103 |

**CRITICISMS:**
- Soundness and usefulness trade off: a perfectly sound analysis can be operationally unusable.
- Abstraction theorems cover only the formal concrete semantics, which may itself omit implementation/environment behaviour.
- CEGAR does not guarantee rapid convergence or a sufficiently expressive predicate domain [S061].
- Recent work continues to show fundamental incompleteness/scalability limits and hard reduction problems [S103].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Every abstract result states approximation direction, preserved property, omitted distinctions and spurious-result policy. Sound over-approximation supports absence claims only for the modelled concrete semantics; under-approximation supports witness finding only. Precision is tuned to a named decision.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P014 — Refinement/simulation correspondence, P019 — State explosion management. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P013 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while an under-approximation is reported as proof of absence?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P013?
- Would the cheap path — For small finite systems or deterministic local rules, analyse the concrete state directly instead of introducing abstraction risk — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P013, what decision changes, and should the artefact be retired if no live consumer remains?


### P014 — Refinement/simulation correspondence

**PROPERTY_ID:** `P014`  
**PROPERTY_NAME:** Refinement/simulation correspondence

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** A lower-level implementation/model must refine the abstract property through a stated simulation/equivalence relation. It is intended to prevent: A property proved of an abstract design does not automatically hold for a lower-level model or implementation. Representation changes, new nondeterminism, compiler transformations or concurrency can introduce behaviours absent from the abstraction.

**MATURE_FORM:** A high-level proof controls implementation only through a versioned, composable refinement/correspondence chain with explicit observations, divergence/termination treatment and unmodelled code boundary. Where full refinement is too costly, use conformance tests or translation validation and narrow the claim.

**TRIGGER:** Trigger whenever evidence at one abstraction level is used to control a lower-level model, source, binary or component substitution.

**CHEAP_PATH:** For a direct executable specification or tiny transformation, differential/conformance testing may supply enough correspondence more cheaply.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Refinement/simulation correspondence",
  "ENGINEERING_CLAIM": "A lower-level implementation/model must refine the abstract property through a stated simulation/equivalence relation.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying refinement/simulation correspondence; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The abstract property is invariant under the chosen refinement relation.",
  "ENVIRONMENT_MODEL": "Both levels use compatible environment, fault and scheduler assumptions.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide refinement/simulation correspondence; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: The refinement relation preserves outputs but not timing, confidentiality or liveness observations.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which state an observation relation and refinement criterion; construct retrieve relation or forward/backward simulation showing initial-state correspondence and step/trace preservation, including stuttering, termination and divergence conditions.",
  "SAFETY_LIVENESS_CLASS": "abstraction refinement",
  "ABSTRACTION": "Retrieve/simulation relation covers representation and nondeterminism without hiding material observations.",
  "IMPLEMENTATION_CORRESPONDENCE": "Every deployed transformation/layer is either in the refinement chain or explicitly trusted/validated.",
  "CHEAP_PATH": "For a direct executable specification or tiny transformation, differential/conformance testing may supply enough correspondence more cheaply.",
  "MATURE_FORM": "A high-level proof controls implementation only through a versioned, composable refinement/correspondence chain with explicit observations, divergence/termination treatment and unmodelled code boundary. Where full refinement is too costly, use conformance tests or translation validation and narrow the claim.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P014; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to refinement/simulation correspondence.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in A property proved of an abstract design does not automatically hold for a lower-level model or implementation. Representation changes, new nondeterminism, compiler transformations or concurrency can introduce behaviours absent from the abstraction..",
  "RELATION": "Every deployed transformation/layer is either in the refinement chain or explicitly trusted/validated.",
  "SOUNDNESS_DUTY": "Retrieve/simulation relation covers representation and nondeterminism without hiding material observations.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Refinement proves the chosen observational relation, not every desired property.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "A high-level proof controls implementation only through a versioned, composable refinement/correspondence chain with explicit observations, divergence/termination treatment and unmodelled code boundary. Where full refinement is too costly, use conformance tests or translation validation and narrow the claim.",
  "KNOWN_GAP": "The refinement relation preserves outputs but not timing, confidentiality or liveness observations."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "A lower-level implementation/model must refine the abstract property through a stated simulation/equivalence relation.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for refinement/simulation correspondence.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Retrieve/simulation relation covers representation and nondeterminism without hiding material observations.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against The refinement relation preserves outputs but not timing, confidentiality or liveness observations..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Allows abstract reasoning to survive implementation detail, supports verified compilation and layered systems, and makes model-code gaps concrete proof obligations."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Refinement/simulation correspondence may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger whenever evidence at one abstraction level is used to control a lower-level model, source, binary or component substitution.",
  "CHEAPER_EVIDENCE": "For a direct executable specification or tiny transformation, differential/conformance testing may supply enough correspondence more cheaply."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P014.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Every deployed transformation/layer is either in the refinement chain or explicitly trusted/validated.",
  "ENVIRONMENT_BOUNDARY": "Both levels use compatible environment, fault and scheduler assumptions.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Semantics, proof assistant, translator and certificate checker are bounded.",
  "DRIFT_DETECTOR": "Any layer, compiler option, source semantics or observation change triggers affected refinement replay.",
  "KNOWN_ESCAPE": "The refinement relation preserves outputs but not timing, confidentiality or liveness observations."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter refinement/simulation correspondence.",
  "IDENTITIES_TO_BIND": "Any layer, compiler option, source semantics or observation change triggers affected refinement replay.",
  "REPLAY_OR_RECHECK": "Semantics, proof assistant, translator and certificate checker are bounded.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: State an observation relation and refinement criterion; construct retrieve relation or forward/backward simulation showing initial-state correspondence and step/trace preservation, including stuttering, termination and divergence conditions. Compose refinements across layers and check side conditions.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "When is translation validation more economical than a global compiler/refinement proof?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The abstract property is invariant under the chosen refinement relation.
- Abstraction: Retrieve/simulation relation covers representation and nondeterminism without hiding material observations.
- Environment: Both levels use compatible environment, fault and scheduler assumptions.
- Model/code correspondence: Every deployed transformation/layer is either in the refinement chain or explicitly trusted/validated.
- Trusted tools: Semantics, proof assistant, translator and certificate checker are bounded.
- Currentness/replay: Any layer, compiler option, source semantics or observation change triggers affected refinement replay.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | VDM/Z/B, process semantics and verified compiler/kernel work provide direct plural provenance. | S010, S012, S019, S024, S027 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH | Simulation/refinement theorems are mathematically strong for their observation and semantic models. | S017, S024 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Machine-checked refinement chains and per-run certificates are replayable. | S024, S025, S098 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | HIGH_WHEN_END_TO_END | Correspondence can be very strong in CompCert/seL4-like chains, but drops sharply at omitted layers. | S024, S025, S093, S094 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | CompCert, seL4, CertiKOS, FSCQ and verified verifiers provide major cases. | S024, S025, S027, S028, S098 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Strong cases exist; empirical comparative evidence and maintenance economics are limited. | S092, S096 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_IN_HIGH_ASSURANCE | Formal correspondence is central to certification credit and high-assurance architectures. | S052, S093 |
| TRANSFERABILITY_STRENGTH | HIGH_AS_A_CROSS_LEVEL_PROPERTY | Any abstraction-to-implementation claim needs correspondence, though the exact relation is domain-specific. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Observation choice, undefined behaviour, divergence and omitted layers determine what transfers. | S094 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | TCB analyses and empirical defects directly show why refinement scope must be stated. | S092, S094 |

**CRITICISMS:**
- Refinement proves the chosen observational relation, not every desired property.
- Semantic preservation can be weak or vacuous for undefined/unspecified source behaviour.
- Simulation proofs are technically strong but can hide human-selected correspondence relations.
- Empirical verified-system defects show gaps outside the proved refinement layers [S092].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A high-level proof controls implementation only through a versioned, composable refinement/correspondence chain with explicit observations, divergence/termination treatment and unmodelled code boundary. Where full refinement is too costly, use conformance tests or translation validation and narrow the claim.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P013 — Sound abstraction discipline, P015 — Model-code correspondence. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P014 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while the refinement relation preserves outputs but not timing, confidentiality or liveness observations?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P014?
- Would the cheap path — For a direct executable specification or tiny transformation, differential/conformance testing may supply enough correspondence more cheaply — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P014, what decision changes, and should the artefact be retired if no live consumer remains?


### P015 — Model-code correspondence

**PROPERTY_ID:** `P015`  
**PROPERTY_NAME:** Model-code correspondence

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** A verified model must be tied to the actual source/binary/configuration or treated as design evidence only. It is intended to prevent: The model may be correct while the deployed code, build options, generated artefacts, adapters, configuration or binary does something else. “The design was verified” is therefore not implementation assurance.

**MATURE_FORM:** Every real-world formal claim states its correspondence level: design only, source linked, generated source, compiled binary validated, or deployed instance attested. Gaps and glue code receive targeted tests/review; evidence is invalidated when identities diverge.

**TRIGGER:** Trigger whenever a formal result is used to claim anything about source code, binaries, configured services or deployed hardware.

**CHEAP_PATH:** For design exploration only, label the result design-level and avoid pretending to establish implementation correctness.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Model-code correspondence",
  "ENGINEERING_CLAIM": "A verified model must be tied to the actual source/binary/configuration or treated as design evidence only.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying model-code correspondence; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The formal claim states the concrete artefact level to which it is intended to apply.",
  "ENVIRONMENT_MODEL": "Deployment platform/configuration is within the modelled usage domain.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide model-code correspondence; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Manual code diverges from a verified design model.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which maintain a traceable identity chain from requirement/model to source, generated code, compiler/linker options, binary, configuration and deployed instance.",
  "SAFETY_LIVENESS_CLASS": "assumption sensitive",
  "ABSTRACTION": "Mappings preserve relevant events, data domains and observations.",
  "IMPLEMENTATION_CORRESPONDENCE": "This is the property itself: an explicit, checked link rather than naming similarity or process documentation.",
  "CHEAP_PATH": "For design exploration only, label the result design-level and avoid pretending to establish implementation correctness.",
  "MATURE_FORM": "Every real-world formal claim states its correspondence level: design only, source linked, generated source, compiled binary validated, or deployed instance attested. Gaps and glue code receive targeted tests/review; evidence is invalidated when identities diverge.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P015; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to model-code correspondence.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in The model may be correct while the deployed code, build options, generated artefacts, adapters, configuration or binary does something else. “The design was verified” is therefore not implementation assurance..",
  "RELATION": "This is the property itself: an explicit, checked link rather than naming similarity or process documentation.",
  "SOUNDNESS_DUTY": "Mappings preserve relevant events, data domains and observations.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "This is often the weakest evidence dimension despite very strong in-model proof.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Every real-world formal claim states its correspondence level: design only, source linked, generated source, compiled binary validated, or deployed instance attested. Gaps and glue code receive targeted tests/review; evidence is invalidated when identities diverge.",
  "KNOWN_GAP": "Manual code diverges from a verified design model."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "A verified model must be tied to the actual source/binary/configuration or treated as design evidence only.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for model-code correspondence.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Mappings preserve relevant events, data domains and observations.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Manual code diverges from a verified design model..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Prevents model-only assurance from controlling a deployment decision, focuses verification on risky transformations and glue, and makes the provenance of “formally verified” artefacts auditable."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model-code correspondence may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger whenever a formal result is used to claim anything about source code, binaries, configured services or deployed hardware.",
  "CHEAPER_EVIDENCE": "For design exploration only, label the result design-level and avoid pretending to establish implementation correctness."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P015.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "This is the property itself: an explicit, checked link rather than naming similarity or process documentation.",
  "ENVIRONMENT_BOUNDARY": "Deployment platform/configuration is within the modelled usage domain.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Generators, compilers, extractors, linkers, build tools and validators are proved, validated or trusted explicitly.",
  "DRIFT_DETECTOR": "Hash/version/configuration mismatch immediately downgrades or invalidates correspondence evidence.",
  "KNOWN_ESCAPE": "Manual code diverges from a verified design model."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter model-code correspondence.",
  "IDENTITIES_TO_BIND": "Hash/version/configuration mismatch immediately downgrades or invalidates correspondence evidence.",
  "REPLAY_OR_RECHECK": "Generators, compilers, extractors, linkers, build tools and validators are proved, validated or trusted explicitly.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Maintain a traceable identity chain from requirement/model to source, generated code, compiler/linker options, binary, configuration and deployed instance. Establish correspondence by refinement proof, verified generation, translation validation, conformance/model-based tests, binary equivalence or runtime trace checking. Record any unverified glue.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should reproducible build and attestation evidence compose with semantic refinement proofs?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The formal claim states the concrete artefact level to which it is intended to apply.
- Abstraction: Mappings preserve relevant events, data domains and observations.
- Environment: Deployment platform/configuration is within the modelled usage domain.
- Model/code correspondence: This is the property itself: an explicit, checked link rather than naming similarity or process documentation.
- Trusted tools: Generators, compilers, extractors, linkers, build tools and validators are proved, validated or trusted explicitly.
- Currentness/replay: Hash/version/configuration mismatch immediately downgrades or invalidates correspondence evidence.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Refinement, translation validation and verified compilation provide direct lineage. | S023, S024, S025 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_WHEN_FORMALISED | A semantic refinement or binary validation theorem can be rigorous for the covered chain. | S024, S098 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Certificates, proofs and reproducible identity checks can be replayed per artefact. | S023, S034, S098 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | VARIABLE_FROM_LOW_TO_HIGH | This dimension is the property: design-only evidence is low; end-to-end binary/refinement chains can be high. | S025, S093 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_FLAGSHIP_CASES | CompCert, seL4 and per-run verifier validation demonstrate mechanisms. | S024, S025, S098 |
| EMPIRICAL_COMPARATIVE_STRENGTH | HIGH_NEGATIVE_EVIDENCE | Fonseca et al. directly document model/implementation boundary failures. | S092 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH | Certification and reusable-component guidance require configuration/traceability and usage-domain control. | S051, S052, S113 |
| TRANSFERABILITY_STRENGTH | HIGH_AS_A_NECESSARY_BOUNDARY | Any deployed claim needs it; technique and attainable strength vary. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Build, configuration, platform, glue and semantic mapping assumptions dominate. | S093, S094 |
| CONTRARY_EVIDENCE_STRENGTH | VERY_HIGH | Empirical defects and TCB analyses provide unusually direct contrary evidence against implicit correspondence. | S092, S093, S094 |

**CRITICISMS:**
- This is often the weakest evidence dimension despite very strong in-model proof.
- The empirical study of verified distributed systems found concrete defects outside verified models [S092].
- seL4 and CompCert sources explicitly document residual source/binary/hardware and toolchain boundaries [S093, S094].
- Certification documentation can establish traceability procedures without proving live deployed identity.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Every real-world formal claim states its correspondence level: design only, source linked, generated source, compiled binary validated, or deployed instance attested. Gaps and glue code receive targeted tests/review; evidence is invalidated when identities diverge.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P003 — Environment model boundary, P014 — Refinement/simulation correspondence. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P015 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while manual code diverges from a verified design model?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P015?
- Would the cheap path — For design exploration only, label the result design-level and avoid pretending to establish implementation correctness — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P015, what decision changes, and should the artefact be retired if no live consumer remains?


### P016 — Exhaustive finite-state challenge where warranted

**PROPERTY_ID:** `P016`  
**PROPERTY_NAME:** Exhaustive finite-state challenge where warranted

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Finite/bounded state models should be exhaustively searched when the state space is decision-relevant and tractable. It is intended to prevent: Reviews and conventional tests sample executions and miss rare interleavings, corner states and transition combinations. For a finite tractable model, exhaustive search can settle reachability or temporal properties and return witnesses.

**MATURE_FORM:** Use exhaustive exploration when a decision-relevant finite state space can be justified and completed. Publish the model, property, bounds, reductions, explored state/transition counts and completion status; pair with correspondence and vacuity checks.

**TRIGGER:** Trigger for finite protocols, controllers, configurations or small concurrent designs where exhaustive exploration is tractable and consequential.

**CHEAP_PATH:** Use simulation, testing or bounded search when the model cannot be made finite without excluding the failure class or when a simple invariant suffices.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Exhaustive finite-state challenge where warranted",
  "ENGINEERING_CLAIM": "Finite/bounded state models should be exhaustively searched when the state space is decision-relevant and tractable.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying exhaustive finite-state challenge where warranted; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Formula is nonvacuous and its witnesses/counterexamples have engineering meaning.",
  "ENVIRONMENT_MODEL": "Relevant nondeterministic/fault behaviours are included in the finite model.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide exhaustive finite-state challenge where warranted; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: State space is finite only because relevant data, faults or participants were bounded away.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which construct a finite or finitised transition model, enumerate or symbolically compute reachable states, check invariant/temporal formulas, and emit counterexample traces.",
  "SAFETY_LIVENESS_CLASS": "model checking",
  "ABSTRACTION": "Finitisation and reductions preserve the checked property; under-approximations are labelled.",
  "IMPLEMENTATION_CORRESPONDENCE": "Model states/actions correspond to the claimed design or implementation level.",
  "CHEAP_PATH": "Use simulation, testing or bounded search when the model cannot be made finite without excluding the failure class or when a simple invariant suffices.",
  "MATURE_FORM": "Use exhaustive exploration when a decision-relevant finite state space can be justified and completed. Publish the model, property, bounds, reductions, explored state/transition counts and completion status; pair with correspondence and vacuity checks.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P016; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to exhaustive finite-state challenge where warranted.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Reviews and conventional tests sample executions and miss rare interleavings, corner states and transition combinations. For a finite tractable model, exhaustive search can settle reachability or temporal properties and return witnesses..",
  "RELATION": "Model states/actions correspond to the claimed design or implementation level.",
  "SOUNDNESS_DUTY": "Finitisation and reductions preserve the checked property; under-approximations are labelled.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Exhaustiveness applies to represented states, not every real behaviour.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Use exhaustive exploration when a decision-relevant finite state space can be justified and completed. Publish the model, property, bounds, reductions, explored state/transition counts and completion status; pair with correspondence and vacuity checks.",
  "KNOWN_GAP": "State space is finite only because relevant data, faults or participants were bounded away."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Finite/bounded state models should be exhaustively searched when the state space is decision-relevant and tractable.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for exhaustive finite-state challenge where warranted.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Finitisation and reductions preserve the checked property; under-approximations are labelled.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against State space is finite only because relevant data, faults or participants were bounded away..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Finds rare ordering/state defects with concrete traces and can prove absence within a finite model more decisively than sampled testing."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Exhaustive finite-state challenge where warranted may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger for finite protocols, controllers, configurations or small concurrent designs where exhaustive exploration is tractable and consequential.",
  "CHEAPER_EVIDENCE": "Use simulation, testing or bounded search when the model cannot be made finite without excluding the failure class or when a simple invariant suffices."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P016.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Model states/actions correspond to the claimed design or implementation level.",
  "ENVIRONMENT_BOUNDARY": "Relevant nondeterministic/fault behaviours are included in the finite model.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Search algorithm, state encoding, reductions and solver back ends are trusted or validated.",
  "DRIFT_DETECTOR": "Model/property/tool changes require fresh completion metrics and replay.",
  "KNOWN_ESCAPE": "State space is finite only because relevant data, faults or participants were bounded away."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter exhaustive finite-state challenge where warranted.",
  "IDENTITIES_TO_BIND": "Model/property/tool changes require fresh completion metrics and replay.",
  "REPLAY_OR_RECHECK": "Search algorithm, state encoding, reductions and solver back ends are trusted or validated.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Construct a finite or finitised transition model, enumerate or symbolically compute reachable states, check invariant/temporal formulas, and emit counterexample traces. Record state count, reductions, fairness, resource limits and whether exploration was genuinely complete.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "When does reduction complexity exceed the value of checking the full state space?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Formula is nonvacuous and its witnesses/counterexamples have engineering meaning.
- Abstraction: Finitisation and reductions preserve the checked property; under-approximations are labelled.
- Environment: Relevant nondeterministic/fault behaviours are included in the finite model.
- Model/code correspondence: Model states/actions correspond to the claimed design or implementation level.
- Trusted tools: Search algorithm, state encoding, reductions and solver back ends are trusted or validated.
- Currentness/replay: Model/property/tool changes require fresh completion metrics and replay.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Model checking, SPIN, symbolic model checking and Alloy directly establish finite exhaustive analysis. | S007, S008, S009, S016 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_COMPLETED_MODEL | Exhaustive reachability/temporal checking is rigorous for a finite model and sound reductions. | S007 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Model-check runs are replayable with pinned model/tool/resources. | S009 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_TO_MEDIUM_BY_ITSELF | Exhaustion says nothing about model-code/environment adequacy. | S045, S092 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | Hardware/software model checking, SPIN and AWS provide substantial practice evidence. | S009, S029, S054 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Defect-finding cases are strong; controlled comparative effectiveness and model-cost evidence are mixed. | S062, S065 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH | Model checking is explicitly recognised in DO-333 practice. | S052, S054 |
| TRANSFERABILITY_STRENGTH | CONTEXT_DEPENDENT | Very strong for finite tractable transition systems; poor fit for open, data-rich or rapidly changing systems. | S015 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Finitisation, reductions, property, initial states and environment define the theorem. | S008, S103 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | State explosion, vacuity and correspondence evidence directly prevent “all real behaviours” claims. | S059, S060, S092, S103 |

**CRITICISMS:**
- Exhaustiveness applies to represented states, not every real behaviour.
- State explosion can make complete search impossible even for finite models [S008, S103].
- Abstraction and reduction introduce proof obligations and possible spuriousness.
- No counterexample is weak evidence when bounds or coverage are unclear.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Use exhaustive exploration when a decision-relevant finite state space can be justified and completed. Publish the model, property, bounds, reductions, explored state/transition counts and completion status; pair with correspondence and vacuity checks.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P019 — State explosion management, P042 — Cost/payoff trigger discipline. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P016 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while state space is finite only because relevant data, faults or participants were bounded away?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P016?
- Would the cheap path — Use simulation, testing or bounded search when the model cannot be made finite without excluding the failure class or when a simple invariant suffices — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P016, what decision changes, and should the artefact be retired if no live consumer remains?


### P017 — Counterexample usefulness and trace review

**PROPERTY_ID:** `P017`  
**PROPERTY_NAME:** Counterexample usefulness and trace review

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Counterexamples are high-value engineering artefacts only when trace feasibility and abstraction validity are checked. It is intended to prevent: A failed proof obligation or red status may not reveal a repairable defect. Engineers need the concrete sequence, state assignment or witness showing how the property fails—and whether that witness is feasible in the intended system.

**MATURE_FORM:** Every counterexample is reviewed for feasibility, property validity, abstraction origin and correspondence. Accepted traces become regression tests or model/specification revisions; spurious traces drive abstraction refinement; unresolved traces remain open evidence rather than being suppressed.

**TRIGGER:** Trigger whenever a checker finds a violation or failed obligation that must drive design/code/specification action.

**CHEAP_PATH:** For a direct deterministic assertion failure, the ordinary failing input and stack trace may already be the cheapest witness.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Counterexample usefulness and trace review",
  "ENGINEERING_CLAIM": "Counterexamples are high-value engineering artefacts only when trace feasibility and abstraction validity are checked.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying counterexample usefulness and trace review; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The violated property is reviewed before attributing blame.",
  "ENVIRONMENT_MODEL": "The trace’s environment choices are feasible or intentionally adversarial.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide counterexample usefulness and trace review; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Counterexample exists only in an over-abstract model.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which generate minimal or readable counterexample traces; map model states/actions to domain events; validate initial-state feasibility, abstraction concretisability and implementation reproducibility; classify as product defect, specification defect, abstraction artefact or expected excluded behaviour.",
  "SAFETY_LIVENESS_CLASS": "model checking",
  "ABSTRACTION": "Spuriousness/concretisability can be tested or clearly bounded.",
  "IMPLEMENTATION_CORRESPONDENCE": "Actions and state values can be mapped to implementation events or explicitly labelled design-only.",
  "CHEAP_PATH": "For a direct deterministic assertion failure, the ordinary failing input and stack trace may already be the cheapest witness.",
  "MATURE_FORM": "Every counterexample is reviewed for feasibility, property validity, abstraction origin and correspondence. Accepted traces become regression tests or model/specification revisions; spurious traces drive abstraction refinement; unresolved traces remain open evidence rather than being suppressed.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P017; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to counterexample usefulness and trace review.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in A failed proof obligation or red status may not reveal a repairable defect. Engineers need the concrete sequence, state assignment or witness showing how the property fails—and whether that witness is feasible in the intended system..",
  "RELATION": "Actions and state values can be mapped to implementation events or explicitly labelled design-only.",
  "SOUNDNESS_DUTY": "Spuriousness/concretisability can be tested or clearly bounded.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "A counterexample to an abstraction is not necessarily an implementation bug [S061].",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Every counterexample is reviewed for feasibility, property validity, abstraction origin and correspondence. Accepted traces become regression tests or model/specification revisions; spurious traces drive abstraction refinement; unresolved traces remain open evidence rather than being suppressed.",
  "KNOWN_GAP": "Counterexample exists only in an over-abstract model."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Counterexamples are high-value engineering artefacts only when trace feasibility and abstraction validity are checked.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for counterexample usefulness and trace review.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Spuriousness/concretisability can be tested or clearly bounded.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Counterexample exists only in an over-abstract model..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Shortens diagnosis, converts exhaustive reasoning into actionable reproductions, and exposes incorrect assumptions/specifications early."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Counterexample usefulness and trace review may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger whenever a checker finds a violation or failed obligation that must drive design/code/specification action.",
  "CHEAPER_EVIDENCE": "For a direct deterministic assertion failure, the ordinary failing input and stack trace may already be the cheapest witness."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P017.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Actions and state values can be mapped to implementation events or explicitly labelled design-only.",
  "ENVIRONMENT_BOUNDARY": "The trace’s environment choices are feasible or intentionally adversarial.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Trace generation, minimisation and explanation preserve a real violating path.",
  "DRIFT_DETECTOR": "Accepted counterexamples are tied to model/code versions and retained as regressions after repair.",
  "KNOWN_ESCAPE": "Counterexample exists only in an over-abstract model."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter counterexample usefulness and trace review.",
  "IDENTITIES_TO_BIND": "Accepted counterexamples are tied to model/code versions and retained as regressions after repair.",
  "REPLAY_OR_RECHECK": "Trace generation, minimisation and explanation preserve a real violating path.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Generate minimal or readable counterexample traces; map model states/actions to domain events; validate initial-state feasibility, abstraction concretisability and implementation reproducibility; classify as product defect, specification defect, abstraction artefact or expected excluded behaviour.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should counterexamples from probabilistic, timed or hyperproperty analyses be presented?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The violated property is reviewed before attributing blame.
- Abstraction: Spuriousness/concretisability can be tested or clearly bounded.
- Environment: The trace’s environment choices are feasible or intentionally adversarial.
- Model/code correspondence: Actions and state values can be mapped to implementation events or explicitly labelled design-only.
- Trusted tools: Trace generation, minimisation and explanation preserve a real violating path.
- Currentness/replay: Accepted counterexamples are tied to model/code versions and retained as regressions after repair.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Counterexample generation is a defining model-checking contribution. | S007, S009, S016 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_AS_A_WITNESS | A valid trace is decisive evidence that the formal model violates the formal property. | S007 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Counterexample reproduction and regression are mechanically replayable when model/tool are pinned. | S009 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM | Concretisation and event mapping determine whether the witness implicates implementation. | S061, S092 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | SPIN, Alloy, AWS and CEGAR practice demonstrate engineering value. | S009, S016, S029, S061 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Case evidence is strong; comparative studies of trace explanation/minimisation quality are limited. | S062 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_FOR_MODEL_CHECKING_ASSURANCE | Counterexample review supports formal-method objectives but is not itself certification. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH | Witness-oriented diagnosis transfers across model finding, symbolic execution and testing. | S034, S085 |
| ASSUMPTION_SENSITIVITY | HIGH | Feasibility, abstraction and property correctness strongly condition interpretation. | S061 |
| CONTRARY_EVIDENCE_STRENGTH | MEDIUM_HIGH | Spurious-trace literature directly limits automatic product-defect attribution. | S061, S092 |

**CRITICISMS:**
- A counterexample to an abstraction is not necessarily an implementation bug [S061].
- Diagnostic value depends on model-code mapping and comprehensibility.
- Counterexamples can encourage local patching without strengthening the specification or model.
- Unsat/no-counterexample evidence does not share the same intuitive witness strength.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Every counterexample is reviewed for feasibility, property validity, abstraction origin and correspondence. Accepted traces become regression tests or model/specification revisions; spurious traces drive abstraction refinement; unresolved traces remain open evidence rather than being suppressed.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P013 — Sound abstraction discipline, P020 — Vacuity and specification-strength checks. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P017 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while counterexample exists only in an over-abstract model?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P017?
- Would the cheap path — For a direct deterministic assertion failure, the ordinary failing input and stack trace may already be the cheapest witness — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P017, what decision changes, and should the artefact be retired if no live consumer remains?


### P018 — Bounded checking scope disclosure

**PROPERTY_ID:** `P018`  
**PROPERTY_NAME:** Bounded checking scope disclosure

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Bounded model checking/model finding must publish the bound/scope and never sell no-counterexample as unbounded proof. It is intended to prevent: Finite-depth reasoning is powerful for bug finding but is easily marketed as proof. A green run may merely mean no counterexample exists within the chosen depth, loop unwind, integer width, object scope or participant count.

**MATURE_FORM:** A bounded result states exact depth/scope/width/participants, resource termination, completeness status and decision meaning. It is accepted as proof only with a valid cutoff/diameter/induction argument; otherwise it is labelled strong bounded challenge or bug-finding evidence.

**TRIGGER:** Trigger whenever SAT/SMT/model-finding/symbolic search limits depth, objects, participants, loops or numeric domains.

**CHEAP_PATH:** If a finite state space is genuinely exhausted, report that directly; if one deterministic edge case is at issue, use a direct test.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Bounded checking scope disclosure",
  "ENGINEERING_CLAIM": "Bounded model checking/model finding must publish the bound/scope and never sell no-counterexample as unbounded proof.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying bounded checking scope disclosure; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The claim is phrased to match bounded or unbounded evidence.",
  "ENVIRONMENT_MODEL": "Bounded fault/event schedules do not silently exclude the motivating failure.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide bounded checking scope disclosure; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Bound omitted from reports or user interface.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which record every bound and completeness threshold; distinguish bug-finding result from proof; prove a completeness diameter/cutoff when possible; add unwinding assertions; increase bounds systematically; report timeout/unknown separately; use induction or unbounded proof for universal claims.",
  "SAFETY_LIVENESS_CLASS": "useful but easily gamed",
  "ABSTRACTION": "Finitisation effects are explicit and do not masquerade as concrete completeness.",
  "IMPLEMENTATION_CORRESPONDENCE": "Loop/data/participant bounds match the claimed implementation scenario.",
  "CHEAP_PATH": "If a finite state space is genuinely exhausted, report that directly; if one deterministic edge case is at issue, use a direct test.",
  "MATURE_FORM": "A bounded result states exact depth/scope/width/participants, resource termination, completeness status and decision meaning. It is accepted as proof only with a valid cutoff/diameter/induction argument; otherwise it is labelled strong bounded challenge or bug-finding evidence.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P018; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to bounded checking scope disclosure.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Finite-depth reasoning is powerful for bug finding but is easily marketed as proof. A green run may merely mean no counterexample exists within the chosen depth, loop unwind, integer width, object scope or participant count..",
  "RELATION": "Loop/data/participant bounds match the claimed implementation scenario.",
  "SOUNDNESS_DUTY": "Finitisation effects are explicit and do not masquerade as concrete completeness.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "No counterexample up to k is not proof beyond k absent a completeness argument.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "A bounded result states exact depth/scope/width/participants, resource termination, completeness status and decision meaning. It is accepted as proof only with a valid cutoff/diameter/induction argument; otherwise it is labelled strong bounded challenge or bug-finding evidence.",
  "KNOWN_GAP": "Bound omitted from reports or user interface."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Bounded model checking/model finding must publish the bound/scope and never sell no-counterexample as unbounded proof.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for bounded checking scope disclosure.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Finitisation effects are explicit and do not masquerade as concrete completeness.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Bound omitted from reports or user interface..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Preserves the high bug-finding value and automation of bounded reasoning without allowing it to control unbounded correctness claims."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Bounded checking scope disclosure may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger whenever SAT/SMT/model-finding/symbolic search limits depth, objects, participants, loops or numeric domains.",
  "CHEAPER_EVIDENCE": "If a finite state space is genuinely exhausted, report that directly; if one deterministic edge case is at issue, use a direct test."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P018.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Loop/data/participant bounds match the claimed implementation scenario.",
  "ENVIRONMENT_BOUNDARY": "Bounded fault/event schedules do not silently exclude the motivating failure.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Unwinding, SAT/SMT encoding and unknown/timeout handling are correct and visible.",
  "DRIFT_DETECTOR": "Bounds and completeness arguments are versioned with the model/property and rerun after change.",
  "KNOWN_ESCAPE": "Bound omitted from reports or user interface."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter bounded checking scope disclosure.",
  "IDENTITIES_TO_BIND": "Bounds and completeness arguments are versioned with the model/property and rerun after change.",
  "REPLAY_OR_RECHECK": "Unwinding, SAT/SMT encoding and unknown/timeout handling are correct and visible.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Record every bound and completeness threshold; distinguish bug-finding result from proof; prove a completeness diameter/cutoff when possible; add unwinding assertions; increase bounds systematically; report timeout/unknown separately; use induction or unbounded proof for universal claims.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "For which domain patterns can trustworthy cutoffs be inferred automatically?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The claim is phrased to match bounded or unbounded evidence.
- Abstraction: Finitisation effects are explicit and do not masquerade as concrete completeness.
- Environment: Bounded fault/event schedules do not silently exclude the motivating failure.
- Model/code correspondence: Loop/data/participant bounds match the claimed implementation scenario.
- Trusted tools: Unwinding, SAT/SMT encoding and unknown/timeout handling are correct and visible.
- Currentness/replay: Bounds and completeness arguments are versioned with the model/property and rerun after change.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | BMC, CBMC and Alloy directly establish bounded reasoning and explicit finite scope. | S016, S036, S037 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_WITHIN_BOUND | SAT-based checking is rigorous for the encoded finite horizon, assuming correct encoding. | S036 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Runs and bounds are mechanically replayable. | S037 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_BY_ITSELF | Bound disclosure does not establish model-code correspondence or unbounded behaviour. | S045 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_FOR_BUG_FINDING | CBMC/Alloy and industrial SAT methods show strong bounded value. | S016, S037 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Bug-finding success is well documented; universal cost/coverage effects are context-dependent. | S062 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_WHEN_USED_UNDER_DO_333 | Guidance requires sound scope/coverage treatment for certification credit. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH_AS_A_DISCLOSURE_RULE | Any bounded technique needs it; actual bounded method remains contextual. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Depth, width, scope, timeout and cutoff assumptions define the result. | S036, S037 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Caricature and benchmark-transfer evidence directly constrain overclaiming. | S045, S101, S111 |

**CRITICISMS:**
- No counterexample up to k is not proof beyond k absent a completeness argument.
- Small scopes often find structural bugs but there is no universal guarantee.
- Bounds can be selected after seeing outcomes, enabling assurance gaming.
- AI-generated specifications/benchmarks can leak expected theorem structure [S101, S111].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A bounded result states exact depth/scope/width/participants, resource termination, completeness status and decision meaning. It is accepted as proof only with a valid cutoff/diameter/induction argument; otherwise it is labelled strong bounded challenge or bug-finding evidence.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P016 — Exhaustive finite-state challenge where warranted, P038 — Ceremony/proxy rejection. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P018 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while bound omitted from reports or user interface?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P018?
- Would the cheap path — If a finite state space is genuinely exhausted, report that directly; if one deterministic edge case is at issue, use a direct test — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P018, what decision changes, and should the artefact be retired if no live consumer remains?


### P019 — State explosion management

**PROPERTY_ID:** `P019`  
**PROPERTY_NAME:** State explosion management

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Partial-order/symmetry/symbolic/abstraction methods are retained as scalability mechanisms, not proof of model adequacy. It is intended to prevent: The product of variables, processes, data values and interleavings makes exhaustive exploration computationally infeasible, causing tools to terminate, simplify away failure modes or consume more engineering effort than the risk warrants.

**MATURE_FORM:** Use reductions with explicit preservation arguments and report both reduced and conceptual scope. If tractability requires excluding material behaviours, narrow the claim or switch to hybrid evidence. State explosion is a method-selection constraint, not a reason to hide bounds.

**TRIGGER:** Trigger when state-space estimates or failed runs show combinatorial blow-up in a decision-relevant model.

**CHEAP_PATH:** Do not introduce sophisticated reductions for a small model; use direct exploration or a simpler invariant.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "State explosion management",
  "ENGINEERING_CLAIM": "Partial-order/symmetry/symbolic/abstraction methods are retained as scalability mechanisms, not proof of model adequacy.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying state explosion management; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The property is compatible with the equivalence/reduction used.",
  "ENVIRONMENT_MODEL": "Fault/environment behaviours are not selectively removed just to achieve tractability.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide state explosion management; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Reduction relies on an invalid independence relation.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which exploit structure through symbolic state sets, partial-order equivalence, symmetry, abstraction, compositional decomposition, parameter cutoffs and bounded/sat search.",
  "SAFETY_LIVENESS_CLASS": "model checking",
  "ABSTRACTION": "Independence, symmetry, cutoff or abstract-domain assumptions are justified.",
  "IMPLEMENTATION_CORRESPONDENCE": "Reduction preserves implementation-relevant identities and event orders.",
  "CHEAP_PATH": "Do not introduce sophisticated reductions for a small model; use direct exploration or a simpler invariant.",
  "MATURE_FORM": "Use reductions with explicit preservation arguments and report both reduced and conceptual scope. If tractability requires excluding material behaviours, narrow the claim or switch to hybrid evidence. State explosion is a method-selection constraint, not a reason to hide bounds.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P019; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to state explosion management.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in The product of variables, processes, data values and interleavings makes exhaustive exploration computationally infeasible, causing tools to terminate, simplify away failure modes or consume more engineering effort than the risk warrants..",
  "RELATION": "Reduction preserves implementation-relevant identities and event orders.",
  "SOUNDNESS_DUTY": "Independence, symmetry, cutoff or abstract-domain assumptions are justified.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "No reduction eliminates worst-case complexity; scaling claims are structure-dependent.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Use reductions with explicit preservation arguments and report both reduced and conceptual scope. If tractability requires excluding material behaviours, narrow the claim or switch to hybrid evidence. State explosion is a method-selection constraint, not a reason to hide bounds.",
  "KNOWN_GAP": "Reduction relies on an invalid independence relation."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Partial-order/symmetry/symbolic/abstraction methods are retained as scalability mechanisms, not proof of model adequacy.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for state explosion management.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Independence, symmetry, cutoff or abstract-domain assumptions are justified.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Reduction relies on an invalid independence relation..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Extends exhaustive or systematic challenge to larger systems while retaining trace diagnostics and makes cost/scalability trade-offs explicit."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "State explosion management may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger when state-space estimates or failed runs show combinatorial blow-up in a decision-relevant model.",
  "CHEAPER_EVIDENCE": "Do not introduce sophisticated reductions for a small model; use direct exploration or a simpler invariant."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P019.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Reduction preserves implementation-relevant identities and event orders.",
  "ENVIRONMENT_BOUNDARY": "Fault/environment behaviours are not selectively removed just to achieve tractability.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Reduction algorithms, hashing, symbolic encodings and resource termination statuses are trustworthy.",
  "DRIFT_DETECTOR": "Model/property changes trigger state-space/reduction revalidation; cached reductions are not presumed reusable.",
  "KNOWN_ESCAPE": "Reduction relies on an invalid independence relation."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter state explosion management.",
  "IDENTITIES_TO_BIND": "Model/property changes trigger state-space/reduction revalidation; cached reductions are not presumed reusable.",
  "REPLAY_OR_RECHECK": "Reduction algorithms, hashing, symbolic encodings and resource termination statuses are trustworthy.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Exploit structure through symbolic state sets, partial-order equivalence, symmetry, abstraction, compositional decomposition, parameter cutoffs and bounded/SAT search. Measure explored state/transition counts, memory/time, reduction ratios and soundness conditions; retreat to focused properties/models when scale remains prohibitive.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "When should a team stop refining a model and invest in architecture simplification or runtime evidence instead?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The property is compatible with the equivalence/reduction used.
- Abstraction: Independence, symmetry, cutoff or abstract-domain assumptions are justified.
- Environment: Fault/environment behaviours are not selectively removed just to achieve tractability.
- Model/code correspondence: Reduction preserves implementation-relevant identities and event orders.
- Trusted tools: Reduction algorithms, hashing, symbolic encodings and resource termination statuses are trustworthy.
- Currentness/replay: Model/property changes trigger state-space/reduction revalidation; cached reductions are not presumed reusable.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Symbolic model checking, SPIN reductions, BMC and CEGAR provide direct historical lineage. | S008, S009, S036, S061 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_CONDITIONALLY | Reductions preserve results when their formal conditions hold. | S009, S061 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Reduced searches are replayable with pinned heuristics/resources. | S009 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_BY_ITSELF | Scalability mechanisms do not improve model-code correspondence. | S092 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | Symbolic/partial-order/abstraction methods underpin major tools and cases. | S009, S032, S033 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Industrial use is clear; comparative reduction cost/benefit varies widely. | S062, S064 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_FOR_RECOGNISED_TECHNIQUES | Model checking and abstract interpretation are accepted in formal assurance with soundness obligations. | S052, S054 |
| TRANSFERABILITY_STRENGTH | CONTEXT_DEPENDENT | Every large model faces scale, but no single reduction transfers universally. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | System structure, property, independence, data bounds and resources determine success. | S008, S103 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Foundational complexity and practical spuriousness evidence directly oppose “state explosion solved” claims. | S061, S103 |

**CRITICISMS:**
- No reduction eliminates worst-case complexity; scaling claims are structure-dependent.
- Engineering effort to design abstractions/reductions can exceed direct testing or redesign.
- State-count headlines are poor cross-model assurance metrics.
- Reduction soundness says nothing about model adequacy.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Use reductions with explicit preservation arguments and report both reduced and conceptual scope. If tractability requires excluding material behaviours, narrow the claim or switch to hybrid evidence. State explosion is a method-selection constraint, not a reason to hide bounds.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P013 — Sound abstraction discipline, P016 — Exhaustive finite-state challenge where warranted. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P019 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while reduction relies on an invalid independence relation?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P019?
- Would the cheap path — Do not introduce sophisticated reductions for a small model; use direct exploration or a simpler invariant — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P019, what decision changes, and should the artefact be retired if no live consumer remains?


### P020 — Vacuity and specification-strength checks

**PROPERTY_ID:** `P020`  
**PROPERTY_NAME:** Vacuity and specification-strength checks

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** A green theorem/model-checking result must be challenged for vacuity, unreachable states and overly weak properties. It is intended to prevent: A proof may succeed because assumptions are inconsistent, initial states unreachable, antecedents never occur, behaviour disabled or the property too weak. The result is logically true but supplies little or no assurance.

**MATURE_FORM:** A critical formal property must demonstrate satisfiable scope, reachable meaningful cases, sensitivity to each material clause and rejection of known bad scenarios. The theorem/specification change history is reviewed to distinguish legitimate correction from proof gaming.

**TRIGGER:** Trigger for critical temporal/invariant/contract/theorem claims, especially after unexpectedly easy proof or repeated specification changes.

**CHEAP_PATH:** For a direct local predicate with obvious positive/negative unit cases, run those cases rather than a heavyweight vacuity framework.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Vacuity and specification-strength checks",
  "ENGINEERING_CLAIM": "A green theorem/model-checking result must be challenged for vacuity, unreachable states and overly weak properties.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying vacuity and specification-strength checks; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Assumptions and initial states have witnesses; each material clause can affect an allowed behaviour.",
  "ENVIRONMENT_MODEL": "The environment model permits realistic triggering/failing cases.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide vacuity and specification-strength checks; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: A request–response property passes because no request can occur.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which check model and assumption satisfiability; require witnesses for preconditions/initial states; perform semantic vacuity analysis; mutate property clauses, assumptions and transitions; test known negative examples; measure whether each clause affects outcomes; review proof obligations changed after failures.",
  "SAFETY_LIVENESS_CLASS": "useful but easily gamed",
  "ABSTRACTION": "Vacuity is not an artefact of abstraction eliminating trigger behaviours.",
  "IMPLEMENTATION_CORRESPONDENCE": "Negative examples and triggers map to implementation/deployment scenarios where the claim is operational.",
  "CHEAP_PATH": "For a direct local predicate with obvious positive/negative unit cases, run those cases rather than a heavyweight vacuity framework.",
  "MATURE_FORM": "A critical formal property must demonstrate satisfiable scope, reachable meaningful cases, sensitivity to each material clause and rejection of known bad scenarios. The theorem/specification change history is reviewed to distinguish legitimate correction from proof gaming.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P020; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to vacuity and specification-strength checks.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in A proof may succeed because assumptions are inconsistent, initial states unreachable, antecedents never occur, behaviour disabled or the property too weak. The result is logically true but supplies little or no assurance..",
  "RELATION": "Negative examples and triggers map to implementation/deployment scenarios where the claim is operational.",
  "SOUNDNESS_DUTY": "Vacuity is not an artefact of abstraction eliminating trigger behaviours.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Formula truth and proof checking do not measure specification strength.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "A critical formal property must demonstrate satisfiable scope, reachable meaningful cases, sensitivity to each material clause and rejection of known bad scenarios. The theorem/specification change history is reviewed to distinguish legitimate correction from proof gaming.",
  "KNOWN_GAP": "A request–response property passes because no request can occur."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "A green theorem/model-checking result must be challenged for vacuity, unreachable states and overly weak properties.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for vacuity and specification-strength checks.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Vacuity is not an artefact of abstraction eliminating trigger behaviours.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against A request–response property passes because no request can occur..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Detects false confidence before release, exposes weak/irrelevant specifications, and makes proof success harder to obtain by excluding the problem."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Vacuity and specification-strength checks may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger for critical temporal/invariant/contract/theorem claims, especially after unexpectedly easy proof or repeated specification changes.",
  "CHEAPER_EVIDENCE": "For a direct local predicate with obvious positive/negative unit cases, run those cases rather than a heavyweight vacuity framework."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P020.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Negative examples and triggers map to implementation/deployment scenarios where the claim is operational.",
  "ENVIRONMENT_BOUNDARY": "The environment model permits realistic triggering/failing cases.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Vacuity/mutation engines preserve formula semantics and report unsupported constructs.",
  "DRIFT_DETECTOR": "Specification and proof-obligation diffs are reviewed; strength tests replay after every relevant change.",
  "KNOWN_ESCAPE": "A request–response property passes because no request can occur."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter vacuity and specification-strength checks.",
  "IDENTITIES_TO_BIND": "Specification and proof-obligation diffs are reviewed; strength tests replay after every relevant change.",
  "REPLAY_OR_RECHECK": "Vacuity/mutation engines preserve formula semantics and report unsupported constructs.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Check model and assumption satisfiability; require witnesses for preconditions/initial states; perform semantic vacuity analysis; mutate property clauses, assumptions and transitions; test known negative examples; measure whether each clause affects outcomes; review proof obligations changed after failures.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "What governance best distinguishes legitimate specification revision from outcome-driven weakening?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Assumptions and initial states have witnesses; each material clause can affect an allowed behaviour.
- Abstraction: Vacuity is not an artefact of abstraction eliminating trigger behaviours.
- Environment: The environment model permits realistic triggering/failing cases.
- Model/code correspondence: Negative examples and triggers map to implementation/deployment scenarios where the claim is operational.
- Trusted tools: Vacuity/mutation engines preserve formula semantics and report unsupported constructs.
- Currentness/replay: Specification and proof-obligation diffs are reviewed; strength tests replay after every relevant change.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Beer and Kupferman–Vardi directly establish vacuity as a distinct verification-quality problem. | S059, S060 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_DETECTED_FORMS | Semantic vacuity and satisfiability checks are formally rigorous for supported logics. | S059, S060 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Vacuity/mutation runs are replayable with versioned model/property. | S060 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_BY_ITSELF | A nonvacuous in-model property still may not correspond to code or stakeholder intent. | S092, S100 |
| INDUSTRIAL_CASE_STRENGTH | MEDIUM_HIGH | Vacuity is mature in hardware/model checking and increasingly relevant to software/specification practice. | S052, S065 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Practitioner/AI translation evidence supports the risk; comparative field-effect evidence is limited. | S100, S101, S102 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_FOR_FORMAL_METHOD_CREDIT | DO-333 requires meaningful coverage/soundness, though it does not reduce all weakness to a metric. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH | The anti-vacuity principle transfers across logics even though algorithms differ. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Initial states, assumptions, triggers and environment determine whether truth is meaningful. | S059, S060 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Foundational vacuity results and current translation evidence directly challenge proof-as-assurance proxies. | S059, S060, S100, S101, S102 |

**CRITICISMS:**
- Formula truth and proof checking do not measure specification strength.
- Vacuity detectors themselves cover particular logics and definitions; nonvacuity is not full correctness.
- Mutation scores can become another proxy and be gamed.
- Human validation remains necessary to decide whether a changed clause matters to stakeholders.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A critical formal property must demonstrate satisfiable scope, reachable meaningful cases, sensitivity to each material clause and rejection of known bad scenarios. The theorem/specification change history is reviewed to distinguish legitimate correction from proof gaming.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P001 — Precise property before proof, P039 — Specification gaming and golden theorem drift. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P020 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while a request–response property passes because no request can occur?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P020?
- Would the cheap path — For a direct local predicate with obvious positive/negative unit cases, run those cases rather than a heavyweight vacuity framework — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P020, what decision changes, and should the artefact be retired if no live consumer remains?


### P021 — Mechanical proof replay

**PROPERTY_ID:** `P021`  
**PROPERTY_NAME:** Mechanical proof replay

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Critical logical arguments should be replayable by a proof checker against explicit assumptions when proof evidence is material. It is intended to prevent: A persuasive hand proof, review note or one-time interactive session cannot reliably establish that every inference remains valid, that dependencies are available, or that the theorem still follows after change.

**MATURE_FORM:** A proof claim is accepted only with a clean, repeatable kernel check tied to exact theorem/model/code identities and a disclosed assumption/dependency set. Replay failure is an assurance failure; replay success is scoped to the checked statement and version.

**TRIGGER:** Trigger for any theorem intended to survive author/session context, support assurance credit or be independently consumed.

**CHEAP_PATH:** For a tiny decidable check, a deterministic verifier/test with archived input/output may be more economical than an interactive proof development.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Mechanical proof replay",
  "ENGINEERING_CLAIM": "Critical logical arguments should be replayable by a proof checker against explicit assumptions when proof evidence is material.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying mechanical proof replay; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The replayed theorem is exactly the reviewed engineering statement; no unreviewed weakening or axiom change.",
  "ENVIRONMENT_MODEL": "External assumptions are recorded; replay does not count as discharging them.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide mechanical proof replay; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Proof script succeeds only with undeclared local state, cache or plugin.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which store theorem statement, proof source/term, assumptions, dependency graph, prover/library versions and deterministic build command.",
  "SAFETY_LIVENESS_CLASS": "theorem proving",
  "ABSTRACTION": "Model/abstraction version is bound to the proof identity.",
  "IMPLEMENTATION_CORRESPONDENCE": "Source/model/binary identifiers consumed by the theorem are recorded separately.",
  "CHEAP_PATH": "For a tiny decidable check, a deterministic verifier/test with archived input/output may be more economical than an interactive proof development.",
  "MATURE_FORM": "A proof claim is accepted only with a clean, repeatable kernel check tied to exact theorem/model/code identities and a disclosed assumption/dependency set. Replay failure is an assurance failure; replay success is scoped to the checked statement and version.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P021; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Mechanical proof replay governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Model/abstraction version is bound to the proof identity.",
  "ESCALATION_TRIGGER": "Trigger for any theorem intended to survive author/session context, support assurance credit or be independently consumed.",
  "CHEAP_PATH": "For a tiny decidable check, a deterministic verifier/test with archived input/output may be more economical than an interactive proof development."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for mechanical proof replay.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For a tiny decidable check, a deterministic verifier/test with archived input/output may be more economical than an interactive proof development."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "Critical logical arguments should be replayable by a proof checker against explicit assumptions when proof evidence is material.",
  "ASSUMPTIONS_AND_AXIOMS": "Pinned theorem source, proof artefact, dependency versions, build environment and clean replay command.",
  "CHECKER_OR_KERNEL_BOUNDARY": "Kernel, parser, logic definition, axioms and any proof-import checker are bounded.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for mechanical proof replay.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Clean replay occurs after theorem, proof, model, code, library, prover or relevant configuration change.",
  "CORRESPONDENCE_DUTY": "Source/model/binary identifiers consumed by the theorem are recorded separately.",
  "MISUSE_TO_PREVENT": "Mechanical replay validates derivation, not requirement translation, assumptions or implementation correspondence."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P021.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Source/model/binary identifiers consumed by the theorem are recorded separately.",
  "ENVIRONMENT_BOUNDARY": "External assumptions are recorded; replay does not count as discharging them.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Kernel, parser, logic definition, axioms and any proof-import checker are bounded.",
  "DRIFT_DETECTOR": "Clean replay occurs after theorem, proof, model, code, library, prover or relevant configuration change.",
  "KNOWN_ESCAPE": "Proof script succeeds only with undeclared local state, cache or plugin."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter mechanical proof replay.",
  "IDENTITIES_TO_BIND": "Clean replay occurs after theorem, proof, model, code, library, prover or relevant configuration change.",
  "REPLAY_OR_RECHECK": "Kernel, parser, logic definition, axioms and any proof-import checker are bounded.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Store theorem statement, proof source/term, assumptions, dependency graph, prover/library versions and deterministic build command. Re-run the kernel checker from a clean environment; archive logs and artefact hashes; distinguish reconstructed proof, admitted axiom and external oracle result.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "What reproducibility threshold is practical for resource-intensive industrial proof builds?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The replayed theorem is exactly the reviewed engineering statement; no unreviewed weakening or axiom change.
- Abstraction: Model/abstraction version is bound to the proof identity.
- Environment: External assumptions are recorded; replay does not count as discharging them.
- Model/code correspondence: Source/model/binary identifiers consumed by the theorem are recorded separately.
- Trusted tools: Kernel, parser, logic definition, axioms and any proof-import checker are bounded.
- Currentness/replay: Clean replay occurs after theorem, proof, model, code, library, prover or relevant configuration change.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | HOL/Isabelle/Coq and verified-software practice directly establish kernel-based replay. | S042, S043, S044, S050 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH | Kernel checking provides strong evidence that the formal derivation follows in the declared logic. | S042, S044 |
| MECHANICAL_REPLAY_STRENGTH | VERY_HIGH | Replay is the property itself when artefacts and environment are complete. | S044, S095 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_BY_ITSELF | Replay does not connect the theorem to current implementation or environment. | S092, S100 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_FLAGSHIP_PROJECTS | CompCert, seL4, VST and CakeML maintain replayable proof corpora. | S024, S025, S050, S080 |
| EMPIRICAL_COMPARATIVE_STRENGTH | HIGH_FOR_MAINTENANCE_RISK | The Isabelle compatibility study supplies large empirical evidence of replay breakage; productivity comparisons remain limited. | S095 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH | Machine-replayable formal evidence is central to high-assurance use, subject to tool qualification and scope. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH_FOR_THEOREM_PROVING | Universal within mechanised proof, but unnecessary for simple non-theorem checks. | S096 |
| ASSUMPTION_SENSITIVITY | HIGH | Logic, axioms, dependencies, resources and identity determine what replay establishes. | S095, S096 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Compatibility and specification evidence strongly constrain “proof once passed” confidence. | S095, S100 |

**CRITICISMS:**
- Mechanical replay validates derivation, not requirement translation, assumptions or implementation correspondence.
- Large proof builds can be expensive, brittle and difficult to reproduce [S095, S096].
- A short replay log may hide a large trusted base or generated code path.
- A proof that compiles after theorem weakening is current syntactically but not semantically equivalent.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A proof claim is accepted only with a clean, repeatable kernel check tied to exact theorem/model/code identities and a disclosed assumption/dependency set. Replay failure is an assurance failure; replay success is scoped to the checked statement and version.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P023 — Proof maintenance and currentness, P047 — Proof assistant cannot be wrong. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P021 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while proof script succeeds only with undeclared local state, cache or plugin?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P021?
- Would the cheap path — For a tiny decidable check, a deterministic verifier/test with archived input/output may be more economical than an interactive proof development — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P021, what decision changes, and should the artefact be retired if no live consumer remains?


### P022 — Trusted kernel/certificate boundary

**PROPERTY_ID:** `P022`  
**PROPERTY_NAME:** Trusted kernel/certificate boundary

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Tool trust must identify the checker kernel, axioms, oracle/solver calls, generated code and unsafe extensions. It is intended to prevent: A result from a large prover, solver, optimiser or verifier is only as trustworthy as millions of lines of implementation and translation code unless success can be checked by a smaller, independently understandable base.

**MATURE_FORM:** For critical automated results, the acceptance artefact is a replayable proof/certificate checked by an independently bounded kernel, not merely a tool’s “valid/unsat” status. The remaining trusted code and logical axioms are enumerated; non-certifying modes are explicitly downgraded.

**TRIGGER:** Trigger for high-consequence theorem, UNSAT, compiler/verifier or code-acceptance results where trusting the full producer is unacceptable.

**CHEAP_PATH:** For low-risk local checks, solver diversity, fuzzing and regression tests may be proportionate; document raw solver trust rather than pretending a certificate exists.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Trusted kernel/certificate boundary",
  "ENGINEERING_CLAIM": "Tool trust must identify the checker kernel, axioms, oracle/solver calls, generated code and unsafe extensions.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying trusted kernel/certificate boundary; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The certificate binds the exact formal statement and assumptions reviewed.",
  "ENVIRONMENT_MODEL": "Physical/deployment assumptions remain outside logical certificate unless separately represented.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide trusted kernel/certificate boundary; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: The certificate omits preprocessing, quantifier instantiation or theory lemmas.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which generate proof terms or certificates; check them with a small kernel or independent checker; disclose axioms, parser/logic definitions, preprocessing rules and certificate coverage.",
  "SAFETY_LIVENESS_CLASS": "theorem proving",
  "ABSTRACTION": "Certificates justify abstraction/preprocessing transformations relevant to soundness.",
  "IMPLEMENTATION_CORRESPONDENCE": "Certificate covers the transformation/model relation actually used, not only a back-end formula.",
  "CHEAP_PATH": "For low-risk local checks, solver diversity, fuzzing and regression tests may be proportionate; document raw solver trust rather than pretending a certificate exists.",
  "MATURE_FORM": "For critical automated results, the acceptance artefact is a replayable proof/certificate checked by an independently bounded kernel, not merely a tool’s “valid/unsat” status. The remaining trusted code and logical axioms are enumerated; non-certifying modes are explicitly downgraded.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P022; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Trusted kernel/certificate boundary governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Certificates justify abstraction/preprocessing transformations relevant to soundness.",
  "ESCALATION_TRIGGER": "Trigger for high-consequence theorem, UNSAT, compiler/verifier or code-acceptance results where trusting the full producer is unacceptable.",
  "CHEAP_PATH": "For low-risk local checks, solver diversity, fuzzing and regression tests may be proportionate; document raw solver trust rather than pretending a certificate exists."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for trusted kernel/certificate boundary.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For low-risk local checks, solver diversity, fuzzing and regression tests may be proportionate; document raw solver trust rather than pretending a certificate exists."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "Tool trust must identify the checker kernel, axioms, oracle/solver calls, generated code and unsafe extensions.",
  "ASSUMPTIONS_AND_AXIOMS": "Certificate-capable producer, specified proof format, independent checker, logic/axiom inventory and coverage statement.",
  "CHECKER_OR_KERNEL_BOUNDARY": "Checker, parser, logic kernel, axioms and compiler/runtime needed to execute it are explicitly bounded.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for trusted kernel/certificate boundary.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Certificates are regenerated and rechecked for each changed statement, encoding, producer or checker version.",
  "CORRESPONDENCE_DUTY": "Certificate covers the transformation/model relation actually used, not only a back-end formula.",
  "MISUSE_TO_PREVENT": "“Small kernel” is a relative reduction, not zero trust."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P022.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Certificate covers the transformation/model relation actually used, not only a back-end formula.",
  "ENVIRONMENT_BOUNDARY": "Physical/deployment assumptions remain outside logical certificate unless separately represented.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Checker, parser, logic kernel, axioms and compiler/runtime needed to execute it are explicitly bounded.",
  "DRIFT_DETECTOR": "Certificates are regenerated and rechecked for each changed statement, encoding, producer or checker version.",
  "KNOWN_ESCAPE": "The certificate omits preprocessing, quantifier instantiation or theory lemmas."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter trusted kernel/certificate boundary.",
  "IDENTITIES_TO_BIND": "Certificates are regenerated and rechecked for each changed statement, encoding, producer or checker version.",
  "REPLAY_OR_RECHECK": "Checker, parser, logic kernel, axioms and compiler/runtime needed to execute it are explicitly bounded.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Generate proof terms or certificates; check them with a small kernel or independent checker; disclose axioms, parser/logic definitions, preprocessing rules and certificate coverage. Cross-check critical artefacts with independent implementations where feasible.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "When is differential solver checking cheaper and sufficient compared with proof certificates?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The certificate binds the exact formal statement and assumptions reviewed.
- Abstraction: Certificates justify abstraction/preprocessing transformations relevant to soundness.
- Environment: Physical/deployment assumptions remain outside logical certificate unless separately represented.
- Model/code correspondence: Certificate covers the transformation/model relation actually used, not only a back-end formula.
- Trusted tools: Checker, parser, logic kernel, axioms and compiler/runtime needed to execute it are explicitly bounded.
- Currentness/replay: Certificates are regenerated and rechecked for each changed statement, encoding, producer or checker version.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | LCF kernels, PCC and modern solver certificates provide direct lineage. | S022, S042, S108, S109 |
| FORMAL_SOUNDNESS_STRENGTH | VERY_HIGH_FOR_COVERED_RULES | A small sound checker gives strong derivational assurance for covered logic and transformations. | S022, S108 |
| MECHANICAL_REPLAY_STRENGTH | VERY_HIGH | Independent certificate replay is central to the mechanism. | S108, S109 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_BY_ITSELF | Certificate validity does not validate model/code/environment correspondence. | S094, S098 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_PROOF_AND_CODE_ACCEPTANCE | PCC, proof assistants and certifying verifiers demonstrate practical mechanisms; general deployment varies. | S022, S098 |
| EMPIRICAL_COMPARATIVE_STRENGTH | HIGH_NEGATIVE_SOLVER_EVIDENCE | OpFuzz supplies direct empirical motivation; certificate cost-benefit comparisons are limited. | S097 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_FOR_TOOL_TRUST_REDUCTION | Assurance standards value independently checkable/qualified evidence, though no single certificate format is mandated. | S052 |
| TRANSFERABILITY_STRENGTH | HIGH_AS_A_TRUST_PATTERN | The producer/checker split transfers widely, while feasibility depends on tool and theory. | S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Logic, parser, axioms, preprocessing coverage and checker independence dominate residual trust. | S094, S108, S109 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Solver bugs and TCB analyses provide strong contrary evidence against “proof assistant/solver cannot be wrong”. | S094, S097 |

**CRITICISMS:**
- “Small kernel” is a relative reduction, not zero trust.
- The trusted base includes statement parsing, logic semantics, axioms and hardware/runtime as relevant.
- Certificate production and reconstruction may impose major performance/coverage cost [S108, S109].
- Solver bug evidence shows why the boundary matters but not that every result requires a full certificate [S097].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—For critical automated results, the acceptance artefact is a replayable proof/certificate checked by an independently bounded kernel, not merely a tool’s “valid/unsat” status. The remaining trusted code and logical axioms are enumerated; non-certifying modes are explicitly downgraded.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P024 — Solver/encoding trust boundary, P047 — Proof assistant cannot be wrong. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P022 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while the certificate omits preprocessing, quantifier instantiation or theory lemmas?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P022?
- Would the cheap path — For low-risk local checks, solver diversity, fuzzing and regression tests may be proportionate; document raw solver trust rather than pretending a certificate exists — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P022, what decision changes, and should the artefact be retired if no live consumer remains?


### P023 — Proof maintenance and currentness

**PROPERTY_ID:** `P023`  
**PROPERTY_NAME:** Proof maintenance and currentness

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Proofs must replay after code/spec/library/tool changes or be marked stale. It is intended to prevent: Code, specifications, libraries, tactics and provers evolve. A previously checked proof can fail, silently target an old artefact, or be “repaired” by changing the theorem. Proof cost therefore includes lifetime maintenance, not only initial construction.

**MATURE_FORM:** A formal result has an owner, dependency manifest, clean continuous replay, theorem/assumption diff review, impact rules and retirement threshold. Repair is accepted only when the checked claim is unchanged or the change is explicitly revalidated.

**TRIGGER:** Trigger for proofs intended to govern evolving production artefacts or survive tool/library upgrades.

**CHEAP_PATH:** For one-off exploratory proofs with no future consumer, archive scope and do not create a permanent maintenance obligation.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Proof maintenance and currentness",
  "ENGINEERING_CLAIM": "Proofs must replay after code/spec/library/tool changes or be marked stale.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying proof maintenance and currentness; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Statement and assumption diffs are first-class review items, not hidden inside proof repair.",
  "ENVIRONMENT_MODEL": "Changes in configuration/platform assumptions enter the dependency graph.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide proof maintenance and currentness; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: A minor library/prover upgrade breaks thousands of proof steps.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which track theorem/proof/model/code dependency graphs; run proofs continuously; classify semantic versus syntactic breakage; perform change-impact analysis; review theorem and assumption diffs; use automated repair only with replay and equivalence checks; budget ownership and deprecation.",
  "SAFETY_LIVENESS_CLASS": "retained in evolved form",
  "ABSTRACTION": "Abstraction interfaces are stable or their downstream proof impact is known.",
  "IMPLEMENTATION_CORRESPONDENCE": "Code/model linkage detects when implementation changes should invalidate or rerun proof.",
  "CHEAP_PATH": "For one-off exploratory proofs with no future consumer, archive scope and do not create a permanent maintenance obligation.",
  "MATURE_FORM": "A formal result has an owner, dependency manifest, clean continuous replay, theorem/assumption diff review, impact rules and retirement threshold. Repair is accepted only when the checked claim is unchanged or the change is explicitly revalidated.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P023; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Proof maintenance and currentness governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Abstraction interfaces are stable or their downstream proof impact is known.",
  "ESCALATION_TRIGGER": "Trigger for proofs intended to govern evolving production artefacts or survive tool/library upgrades.",
  "CHEAP_PATH": "For one-off exploratory proofs with no future consumer, archive scope and do not create a permanent maintenance obligation."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for proof maintenance and currentness.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For one-off exploratory proofs with no future consumer, archive scope and do not create a permanent maintenance obligation."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "Proofs must replay after code/spec/library/tool changes or be marked stale.",
  "ASSUMPTIONS_AND_AXIOMS": "Version control, dependency graph, proof owner, CI/replay resources and semantic review process.",
  "CHECKER_OR_KERNEL_BOUNDARY": "Prover/library/tactic/solver version changes are captured and revalidated.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for proof maintenance and currentness.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Continuous clean replay and semantic diff review are mandatory; age alone is not currentness.",
  "CORRESPONDENCE_DUTY": "Code/model linkage detects when implementation changes should invalidate or rerun proof.",
  "MISUSE_TO_PREVENT": "Proof brittleness can slow iteration and create incentives to avoid necessary design changes."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P023.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Code/model linkage detects when implementation changes should invalidate or rerun proof.",
  "ENVIRONMENT_BOUNDARY": "Changes in configuration/platform assumptions enter the dependency graph.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Prover/library/tactic/solver version changes are captured and revalidated.",
  "DRIFT_DETECTOR": "Continuous clean replay and semantic diff review are mandatory; age alone is not currentness.",
  "KNOWN_ESCAPE": "A minor library/prover upgrade breaks thousands of proof steps."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter proof maintenance and currentness.",
  "IDENTITIES_TO_BIND": "Continuous clean replay and semantic diff review are mandatory; age alone is not currentness.",
  "REPLAY_OR_RECHECK": "Prover/library/tactic/solver version changes are captured and revalidated.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Track theorem/proof/model/code dependency graphs; run proofs continuously; classify semantic versus syntactic breakage; perform change-impact analysis; review theorem and assumption diffs; use automated repair only with replay and equivalence checks; budget ownership and deprecation.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "What empirical ROI models include multi-year proof maintenance and avoided regressions?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Statement and assumption diffs are first-class review items, not hidden inside proof repair.
- Abstraction: Abstraction interfaces are stable or their downstream proof impact is known.
- Environment: Changes in configuration/platform assumptions enter the dependency graph.
- Model/code correspondence: Code/model linkage detects when implementation changes should invalidate or rerun proof.
- Trusted tools: Prover/library/tactic/solver version changes are captured and revalidated.
- Currentness/replay: Continuous clean replay and semantic diff review are mandatory; age alone is not currentness.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Proof-repair, user surveys and proof-engineering literature directly establish maintenance as a modern lineage. | S074, S075, S076, S096 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_PRESERVED_THEOREM | Formal soundness remains high after valid repair, but semantic preservation of the statement must be checked. | S074 |
| MECHANICAL_REPLAY_STRENGTH | VERY_HIGH_RELEVANCE | Replay is the primary detector of syntactic/tool incompatibility. | S095 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_LOW | A current proof can still target a stale model unless correspondence dependencies are explicit. | S092 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_LARGE_PROOF_PROJECTS | CompCert, seL4, VST and AFP demonstrate sustained maintenance, though public cost detail varies. | S024, S025, S050, S095 |
| EMPIRICAL_COMPARATIVE_STRENGTH | HIGH_FOR_COMPATIBILITY | 12,079 Isabelle compatibility issues provide substantial empirical evidence; cross-tool generalisation remains bounded. | S095 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH | Lifecycle/configuration control is required for assurance credit and reusable components. | S051, S052, S113 |
| TRANSFERABILITY_STRENGTH | HIGH_FOR_LIVING_PROOFS | Universal for evolving proof-backed systems, irrelevant to intentionally archival one-offs. | S096 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Tool, library, theorem, model and code versions all determine currentness. | S095 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Compatibility data and user surveys directly rebut “proof once passed”. | S076, S095 |

**CRITICISMS:**
- Proof brittleness can slow iteration and create incentives to avoid necessary design changes.
- Syntactic compatibility is not semantic currentness.
- Automated repair may optimise compilation rather than preserve engineering meaning.
- Empirical compatibility evidence is currently concentrated in particular prover ecosystems [S095].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A formal result has an owner, dependency manifest, clean continuous replay, theorem/assumption diff review, impact rules and retirement threshold. Repair is accepted only when the checked claim is unchanged or the change is explicitly revalidated.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P021 — Mechanical proof replay, P048 — Retirement of stale formal artefacts. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P023 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while a minor library/prover upgrade breaks thousands of proof steps?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P023?
- Would the cheap path — For one-off exploratory proofs with no future consumer, archive scope and do not create a permanent maintenance obligation — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P023, what decision changes, and should the artefact be retired if no live consumer remains?


### P024 — Solver/encoding trust boundary

**PROPERTY_ID:** `P024`  
**PROPERTY_NAME:** Solver/encoding trust boundary

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** SAT/SMT results require checked encodings, theory declarations, solver version/status and certificate strategy where risk warrants. It is intended to prevent: An UNSAT/SAT result can be wrong because the engineering property was encoded incorrectly, arithmetic/bit widths differ, quantifiers trigger incompletely, the solver returns UNKNOWN/timeout, or the solver itself has a soundness defect.

**MATURE_FORM:** A solver-mediated claim records formula hash, logic, solver/version/options, result class and encoding source. Critical UNSAT results carry independently checked certificates or redundant evidence; UNKNOWN/timeout never becomes pass; arithmetic and units are reviewed.

**TRIGGER:** Trigger whenever an SMT/SAT result discharges a material proof obligation or controls acceptance.

**CHEAP_PATH:** For a small decidable predicate, use a direct evaluator/exhaustive table; for low-risk checks, archive solver inputs and cross-check selectively.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Solver/encoding trust boundary",
  "ENGINEERING_CLAIM": "SAT/SMT results require checked encodings, theory declarations, solver version/status and certificate strategy where risk warrants.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying solver/encoding trust boundary; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Engineering units, domains, undefined behaviour and quantification are represented faithfully.",
  "ENVIRONMENT_MODEL": "Hardware numerical semantics and runtime domains match the encoded theory.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide solver/encoding trust boundary; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Wrong sign, units, quantifier scope or bit-vector width in encoding.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which specify logic/theories and exact encoding; distinguish sat, unsat, unknown and timeout; cross-check or fuzz solvers; validate front-end translation; request proof certificates/unsat cores/models; reconstruct critical unsat proofs independently; test floating-point and nonlinear corner semantics.",
  "SAFETY_LIVENESS_CLASS": "context dependent",
  "ABSTRACTION": "Encoding approximations and theory relaxations preserve the claimed direction.",
  "IMPLEMENTATION_CORRESPONDENCE": "Verification-condition generator and front-end translation are validated or trusted explicitly.",
  "CHEAP_PATH": "For a small decidable predicate, use a direct evaluator/exhaustive table; for low-risk checks, archive solver inputs and cross-check selectively.",
  "MATURE_FORM": "A solver-mediated claim records formula hash, logic, solver/version/options, result class and encoding source. Critical UNSAT results carry independently checked certificates or redundant evidence; UNKNOWN/timeout never becomes pass; arithmetic and units are reviewed.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P024; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Solver/encoding trust boundary governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Encoding approximations and theory relaxations preserve the claimed direction.",
  "ESCALATION_TRIGGER": "Trigger whenever an SMT/SAT result discharges a material proof obligation or controls acceptance.",
  "CHEAP_PATH": "For a small decidable predicate, use a direct evaluator/exhaustive table; for low-risk checks, archive solver inputs and cross-check selectively."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for solver/encoding trust boundary.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For a small decidable predicate, use a direct evaluator/exhaustive table; for low-risk checks, archive solver inputs and cross-check selectively."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "SAT/SMT results require checked encodings, theory declarations, solver version/status and certificate strategy where risk warrants.",
  "ASSUMPTIONS_AND_AXIOMS": "Exact formula/encoding, theory semantics, solver/options, result handling and certificate/cross-check policy.",
  "CHECKER_OR_KERNEL_BOUNDARY": "Solver, parser, preprocessing, certificate producer/checker and front-end translator are bounded.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for solver/encoding trust boundary.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Formula, encoder, solver/options or theory-version changes require new result/certificate.",
  "CORRESPONDENCE_DUTY": "Verification-condition generator and front-end translation are validated or trusted explicitly.",
  "MISUSE_TO_PREVENT": "SMT automation can make the most trusted step the least visible to engineers."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P024.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Verification-condition generator and front-end translation are validated or trusted explicitly.",
  "ENVIRONMENT_BOUNDARY": "Hardware numerical semantics and runtime domains match the encoded theory.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Solver, parser, preprocessing, certificate producer/checker and front-end translator are bounded.",
  "DRIFT_DETECTOR": "Formula, encoder, solver/options or theory-version changes require new result/certificate.",
  "KNOWN_ESCAPE": "Wrong sign, units, quantifier scope or bit-vector width in encoding."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter solver/encoding trust boundary.",
  "IDENTITIES_TO_BIND": "Formula, encoder, solver/options or theory-version changes require new result/certificate.",
  "REPLAY_OR_RECHECK": "Solver, parser, preprocessing, certificate producer/checker and front-end translator are bounded.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Specify logic/theories and exact encoding; distinguish SAT, UNSAT, UNKNOWN and timeout; cross-check or fuzz solvers; validate front-end translation; request proof certificates/unsat cores/models; reconstruct critical UNSAT proofs independently; test floating-point and nonlinear corner semantics.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should solver uncertainty and timeout be integrated into assurance decisions?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Engineering units, domains, undefined behaviour and quantification are represented faithfully.
- Abstraction: Encoding approximations and theory relaxations preserve the claimed direction.
- Environment: Hardware numerical semantics and runtime domains match the encoded theory.
- Model/code correspondence: Verification-condition generator and front-end translation are validated or trusted explicitly.
- Trusted tools: Solver, parser, preprocessing, certificate producer/checker and front-end translator are bounded.
- Currentness/replay: Formula, encoder, solver/options or theory-version changes require new result/certificate.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | SAT/SMT foundations and standards provide direct provenance. | S038, S039, S040, S041 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_CONDITIONALLY | Decision procedures are sound for supported theories/encodings, but quantifiers and incomplete theories can yield UNKNOWN. | S038, S040 |
| MECHANICAL_REPLAY_STRENGTH | VERY_HIGH_WITH_CERTIFICATE | Independent certificate reconstruction gives strong replay; raw solver logs give less. | S108, S109 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_LOW | Front-end encoding/model-code connection is separate and has documented failure risk. | S098 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | SMT underpins major program verifiers, static analyses and hardware/software checks. | S038, S050, S098 |
| EMPIRICAL_COMPARATIVE_STRENGTH | HIGH_NEGATIVE_EVIDENCE | OpFuzz documents hundreds of confirmed soundness bugs; controlled benefit comparisons are less direct. | S097 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_WITH_TOOL_QUALIFICATION | Critical assurance demands sound method/tool treatment; raw solver branding is insufficient. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH_AS_A_BOUNDARY | Solver/encoding trust applies wherever SMT/SAT is used, but certificate intensity is contextual. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Encoding, theory, result class, preprocessing and solver version determine validity. | S039, S097 |
| CONTRARY_EVIDENCE_STRENGTH | VERY_HIGH | Solver-bug and verifier-translation evidence directly contradicts blind trust. | S097, S098, S108, S109 |

**CRITICISMS:**
- SMT automation can make the most trusted step the least visible to engineers.
- Solver diversity may share algorithms/code or the same encoding error.
- Certificates can be huge or incomplete for preprocessing/theory reasoning [S108, S109].
- Unsat cores explain logical dependence, not engineering correctness.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A solver-mediated claim records formula hash, logic, solver/version/options, result class and encoding source. Critical UNSAT results carry independently checked certificates or redundant evidence; UNKNOWN/timeout never becomes pass; arithmetic and units are reviewed.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P022 — Trusted kernel/certificate boundary, P047 — Proof assistant cannot be wrong. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P024 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while wrong sign, units, quantifier scope or bit-vector width in encoding?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P024?
- Would the cheap path — For a small decidable predicate, use a direct evaluator/exhaustive table; for low-risk checks, archive solver inputs and cross-check selectively — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P024, what decision changes, and should the artefact be retired if no live consumer remains?


### P025 — Symbolic execution/path constraint scope

**PROPERTY_ID:** `P025`  
**PROPERTY_NAME:** Symbolic execution/path constraint scope

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Symbolic execution gives path evidence and generated tests under explicit path/environment/solver bounds. It is intended to prevent: Concrete tests cover one input/path at a time and miss deep branches. Symbolic execution can systematically generate inputs that exercise paths and reveal assertion, memory, arithmetic or protocol failures.

**MATURE_FORM:** Use symbolic execution for path-sensitive bug finding or focused bounded proof, with exact loop/path/environment bounds, concrete replay of witnesses and complementary fuzzing/testing. Universal claims require a completeness argument or another method.

**TRIGGER:** Trigger for input-rich, branch-heavy code where concrete witness generation is valuable and semantics/environment can be modelled.

**CHEAP_PATH:** Use fuzzing/property-based tests for cheap broad exploration, or direct proof/static analysis when all-path assurance is required and tractable.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Symbolic execution/path constraint scope",
  "ENGINEERING_CLAIM": "Symbolic execution gives path evidence and generated tests under explicit path/environment/solver bounds.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying symbolic execution/path constraint scope; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Assertions/properties checked are meaningful and not merely crash proxies.",
  "ENVIRONMENT_MODEL": "System calls, files, network, time and nondeterminism are modelled or bounded explicitly.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide symbolic execution/path constraint scope; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Path explosion prevents broad coverage.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which execute program semantics over symbolic values, fork at branches, solve path constraints, generate concrete witnesses and combine with search heuristics, state merging, summaries, concolic execution and environment models.",
  "SAFETY_LIVENESS_CLASS": "context dependent",
  "ABSTRACTION": "Stubs, summaries and state merging preserve witness validity or are labelled approximate.",
  "IMPLEMENTATION_CORRESPONDENCE": "Generated witness is replayed on the actual implementation/build where feasible.",
  "CHEAP_PATH": "Use fuzzing/property-based tests for cheap broad exploration, or direct proof/static analysis when all-path assurance is required and tractable.",
  "MATURE_FORM": "Use symbolic execution for path-sensitive bug finding or focused bounded proof, with exact loop/path/environment bounds, concrete replay of witnesses and complementary fuzzing/testing. Universal claims require a completeness argument or another method.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P025; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Symbolic execution/path constraint scope governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Stubs, summaries and state merging preserve witness validity or are labelled approximate.",
  "ESCALATION_TRIGGER": "Trigger for input-rich, branch-heavy code where concrete witness generation is valuable and semantics/environment can be modelled.",
  "CHEAP_PATH": "Use fuzzing/property-based tests for cheap broad exploration, or direct proof/static analysis when all-path assurance is required and tractable."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for symbolic execution/path constraint scope.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "Use fuzzing/property-based tests for cheap broad exploration, or direct proof/static analysis when all-path assurance is required and tractable."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "Symbolic execution gives path evidence and generated tests under explicit path/environment/solver bounds.",
  "ASSUMPTIONS_AND_AXIOMS": "Executable semantics, constraint theories, environment models, search/bound disclosure and concrete replay harness.",
  "CHECKER_OR_KERNEL_BOUNDARY": "Symbolic interpreter, solver, constraint encoding and concrete test generator are trusted/tested.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for symbolic execution/path constraint scope.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Witnesses and exploration campaigns rerun after code/semantics/environment changes.",
  "CORRESPONDENCE_DUTY": "Generated witness is replayed on the actual implementation/build where feasible.",
  "MISUSE_TO_PREVENT": "Path coverage is not environment or behavioural completeness."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P025.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Generated witness is replayed on the actual implementation/build where feasible.",
  "ENVIRONMENT_BOUNDARY": "System calls, files, network, time and nondeterminism are modelled or bounded explicitly.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Symbolic interpreter, solver, constraint encoding and concrete test generator are trusted/tested.",
  "DRIFT_DETECTOR": "Witnesses and exploration campaigns rerun after code/semantics/environment changes.",
  "KNOWN_ESCAPE": "Path explosion prevents broad coverage."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter symbolic execution/path constraint scope.",
  "IDENTITIES_TO_BIND": "Witnesses and exploration campaigns rerun after code/semantics/environment changes.",
  "REPLAY_OR_RECHECK": "Symbolic interpreter, solver, constraint encoding and concrete test generator are trusted/tested.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Execute program semantics over symbolic values, fork at branches, solve path constraints, generate concrete witnesses and combine with search heuristics, state merging, summaries, concolic execution and environment models. Report path/time bounds and solver UNKNOWN separately.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should path coverage be related to specification coverage rather than branch counts?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Assertions/properties checked are meaningful and not merely crash proxies.
- Abstraction: Stubs, summaries and state merging preserve witness validity or are labelled approximate.
- Environment: System calls, files, network, time and nondeterminism are modelled or bounded explicitly.
- Model/code correspondence: Generated witness is replayed on the actual implementation/build where feasible.
- Trusted tools: Symbolic interpreter, solver, constraint encoding and concrete test generator are trusted/tested.
- Currentness/replay: Witnesses and exploration campaigns rerun after code/semantics/environment changes.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | King, KLEE and surveys give direct symbolic-execution lineage. | S085, S034, S035 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_EXPLORED_PATHS | Path-condition reasoning is strong for represented semantics; completeness is usually absent. | S085 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Generated path constraints and concrete witnesses are replayable. | S034 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_HIGH_FOR_WITNESSES | Concrete replay can bind defects to code; absence claims remain weak. | S034 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | KLEE and later industrial/research tools show practical bug-finding value. | S034, S035 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM_HIGH | Numerous defect studies exist, but comparative field effectiveness depends on domain and harness. | S035 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM | Can support assurance/testing objectives but is not automatically an unbounded proof method. | S052 |
| TRANSFERABILITY_STRENGTH | CONTEXT_DEPENDENT | Strong for path-sensitive software; weak for open concurrency or opaque environments. | S035 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Bounds, stubs, solver theories and language semantics define coverage. | S034, S035 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Path-explosion and environment limitations are well-established. | S035 |

**CRITICISMS:**
- Path coverage is not environment or behavioural completeness.
- Generated tests inherit the symbolic semantics and stubs; differential execution is needed.
- Search heuristics can overfit familiar benchmarks or shallow defects.
- Symbolic execution is often strongest as test generation, not proof.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Use symbolic execution for path-sensitive bug finding or focused bounded proof, with exact loop/path/environment bounds, concrete replay of witnesses and complementary fuzzing/testing. Universal claims require a completeness argument or another method.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P018 — Bounded checking scope disclosure, P036 — Hybrid proof + testing/fuzzing/runtime evidence. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P025 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while path explosion prevents broad coverage?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P025?
- Would the cheap path — Use fuzzing/property-based tests for cheap broad exploration, or direct proof/static analysis when all-path assurance is required and tractable — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P025, what decision changes, and should the artefact be retired if no live consumer remains?


### P026 — Sound versus unsound static analysis boundary

**PROPERTY_ID:** `P026`  
**PROPERTY_NAME:** Sound versus unsound static analysis boundary

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Static analysis claims must identify whether the analysis is sound for the language/property and what false positives/negatives mean. It is intended to prevent: A green static-analysis dashboard is ambiguous unless users know whether the analyser over-approximates all behaviours, intentionally misses cases, suppresses warnings, or only applies to a language/platform subset.

**MATURE_FORM:** Every static-analysis result declares whether absence of warnings is a sound guarantee, a bounded guarantee or a heuristic. Unsupported code, suppressions and modelling assumptions are measurable; high-consequence claims use sound or independently validated analysis.

**TRIGGER:** Trigger whenever a static analyser’s green/red result is used as evidence beyond local developer feedback.

**CHEAP_PATH:** Use fast unsound linting freely for low-risk feedback, but label it and do not demand proof-grade governance.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Sound versus unsound static analysis boundary",
  "ENGINEERING_CLAIM": "Static analysis claims must identify whether the analysis is sound for the language/property and what false positives/negatives mean.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying sound versus unsound static analysis boundary; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The defect classes checked are named; no warning is not conflated with functional correctness.",
  "ENVIRONMENT_MODEL": "Libraries, concurrency, inputs and hardware assumptions are within analyser semantics.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide sound versus unsound static analysis boundary; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: An unsound analyser’s silence is marketed as proof.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which publish the soundness target, concrete semantics, supported constructs, false-negative policy and alarm interpretation.",
  "SAFETY_LIVENESS_CLASS": "static analysis type",
  "ABSTRACTION": "Transfer functions and widening preserve soundness for claimed classes.",
  "IMPLEMENTATION_CORRESPONDENCE": "The exact source/build analysed is captured and unsupported portions identified.",
  "CHEAP_PATH": "Use fast unsound linting freely for low-risk feedback, but label it and do not demand proof-grade governance.",
  "MATURE_FORM": "Every static-analysis result declares whether absence of warnings is a sound guarantee, a bounded guarantee or a heuristic. Unsupported code, suppressions and modelling assumptions are measurable; high-consequence claims use sound or independently validated analysis.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P026; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Sound versus unsound static analysis boundary governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Transfer functions and widening preserve soundness for claimed classes.",
  "ESCALATION_TRIGGER": "Trigger whenever a static analyser’s green/red result is used as evidence beyond local developer feedback.",
  "CHEAP_PATH": "Use fast unsound linting freely for low-risk feedback, but label it and do not demand proof-grade governance."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for sound versus unsound static analysis boundary.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "Use fast unsound linting freely for low-risk feedback, but label it and do not demand proof-grade governance."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "Static analysis claims must identify whether the analysis is sound for the language/property and what false positives/negatives mean.",
  "ASSUMPTIONS_AND_AXIOMS": "Documented language/platform semantics, soundness target, supported-code inventory and suppression governance.",
  "CHECKER_OR_KERNEL_BOUNDARY": "Front end, abstract interpreter, solver and configuration are qualified/tested proportionally.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for sound versus unsound static analysis boundary.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Analysis reruns on source/config/tool changes; suppressions expire or are revalidated.",
  "CORRESPONDENCE_DUTY": "The exact source/build analysed is captured and unsupported portions identified.",
  "MISUSE_TO_PREVENT": "Soundness can impose false-positive and usability costs; unsoundness can improve adoption but weakens absence claims."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P026.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "The exact source/build analysed is captured and unsupported portions identified.",
  "ENVIRONMENT_BOUNDARY": "Libraries, concurrency, inputs and hardware assumptions are within analyser semantics.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Front end, abstract interpreter, solver and configuration are qualified/tested proportionally.",
  "DRIFT_DETECTOR": "Analysis reruns on source/config/tool changes; suppressions expire or are revalidated.",
  "KNOWN_ESCAPE": "An unsound analyser’s silence is marketed as proof."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter sound versus unsound static analysis boundary.",
  "IDENTITIES_TO_BIND": "Analysis reruns on source/config/tool changes; suppressions expire or are revalidated.",
  "REPLAY_OR_RECHECK": "Front end, abstract interpreter, solver and configuration are qualified/tested proportionally.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Publish the soundness target, concrete semantics, supported constructs, false-negative policy and alarm interpretation. For sound analysers, treat alarms as possible behaviours requiring triage/refinement; for unsound analysers, treat green as heuristic evidence only. Measure suppressions and unanalysed code.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "Can proof-producing analyses deliver soundness with acceptable industrial performance across broader domains?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The defect classes checked are named; no warning is not conflated with functional correctness.
- Abstraction: Transfer functions and widening preserve soundness for claimed classes.
- Environment: Libraries, concurrency, inputs and hardware assumptions are within analyser semantics.
- Model/code correspondence: The exact source/build analysed is captured and unsupported portions identified.
- Trusted tools: Front end, abstract interpreter, solver and configuration are qualified/tested proportionally.
- Currentness/replay: Analysis reruns on source/config/tool changes; suppressions expire or are revalidated.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Abstract interpretation and industrial analyser lineages directly establish sound/unsound distinctions. | S005, S032, S033 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_SOUND_ANALYSIS | Sound absence claims are rigorous for supported concrete semantics; unsound green results are not proofs. | S005 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Static analyses are readily repeatable with pinned source/configuration. | S032 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM | Source binding can be strong, but compiler/hardware/environment and skipped code remain boundaries. | S032, S094 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_DOMAIN_SPECIFIC_CASES | Astrée and SDV show strong industrial success; general transfer is mixed. | S032, S033 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM_HIGH | Professional surveys and empirical studies support benefits/barriers; false-positive/negative rates vary. | S064, S065 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_FOR_ABSTRACT_INTERPRETATION | DO-333 recognises abstract interpretation with soundness/tool obligations. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH_AS_A_CLAIM_BOUNDARY | The disclosure rule transfers universally; sound analysis feasibility is domain-specific. | S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Semantics, unsupported code, suppressions and concurrency assumptions determine assurance. | S032 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Usability and transfer limitations provide substantial contrary evidence against universal sound-analysis claims. | S064, S065 |

**CRITICISMS:**
- Soundness can impose false-positive and usability costs; unsoundness can improve adoption but weakens absence claims.
- The analyser’s concrete semantics may differ from compiler/hardware behaviour.
- Domain-specific success such as Astrée may not transfer to arbitrary software.
- Suppression and configuration governance can dominate theoretical soundness.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Every static-analysis result declares whether absence of warnings is a sound guarantee, a bounded guarantee or a heuristic. Unsupported code, suppressions and modelling assumptions are measurable; high-consequence claims use sound or independently validated analysis.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P036 — Hybrid proof + testing/fuzzing/runtime evidence, P042 — Cost/payoff trigger discipline. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P026 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while an unsound analyser’s silence is marketed as proof?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P026?
- Would the cheap path — Use fast unsound linting freely for low-risk feedback, but label it and do not demand proof-grade governance — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P026, what decision changes, and should the artefact be retired if no live consumer remains?


### P027 — Type-system claim boundary

**PROPERTY_ID:** `P027`  
**PROPERTY_NAME:** Type-system claim boundary

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Type safety, memory safety and noninterference are retained as precise claims, not functional correctness by implication. It is intended to prevent: “Type-safe” is often inflated into “correct”. Ordinary typing prevents specific representation and operation mismatches but may say nothing about algorithmic result, liveness, security policy, numerical validity or stakeholder requirement.

**MATURE_FORM:** A type-system claim names the prevented failure classes, unsafe boundary and remaining obligations. Stronger types are introduced where they eliminate material misuse or encode stable invariants; functional or temporal correctness is claimed only when represented and proved in the type.

**TRIGGER:** Trigger whenever type safety, Rust ownership, session/refinement/dependent types or “compiles” is used as an assurance claim.

**CHEAP_PATH:** Use ordinary types for ordinary representation safety; do not encode volatile business logic at the type level without clear payoff.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Type-system claim boundary",
  "ENGINEERING_CLAIM": "Type safety, memory safety and noninterference are retained as precise claims, not functional correctness by implication.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying type-system claim boundary; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The proposition encoded by the type matches the claimed failure class.",
  "ENVIRONMENT_MODEL": "External data and foreign components are validated before entering trusted typed invariants.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide type-system claim boundary; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: A well-typed program computes the wrong result.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which state the exact typing theorem and excluded stuck/error classes; map each type feature to an engineering claim; identify unsafe casts, foreign interfaces, dynamic checks and semantic gaps.",
  "SAFETY_LIVENESS_CLASS": "static analysis type",
  "ABSTRACTION": "Type abstraction does not hide value/behaviour distinctions material to clients.",
  "IMPLEMENTATION_CORRESPONDENCE": "Compiler/runtime faithfully implements the type semantics and deployed code avoids unchecked escape hatches.",
  "CHEAP_PATH": "Use ordinary types for ordinary representation safety; do not encode volatile business logic at the type level without clear payoff.",
  "MATURE_FORM": "A type-system claim names the prevented failure classes, unsafe boundary and remaining obligations. Stronger types are introduced where they eliminate material misuse or encode stable invariants; functional or temporal correctness is claimed only when represented and proved in the type.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P027; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Type-system claim boundary governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Type abstraction does not hide value/behaviour distinctions material to clients.",
  "ESCALATION_TRIGGER": "Trigger whenever type safety, Rust ownership, session/refinement/dependent types or “compiles” is used as an assurance claim.",
  "CHEAP_PATH": "Use ordinary types for ordinary representation safety; do not encode volatile business logic at the type level without clear payoff."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for type-system claim boundary.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "Use ordinary types for ordinary representation safety; do not encode volatile business logic at the type level without clear payoff."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "Type safety, memory safety and noninterference are retained as precise claims, not functional correctness by implication.",
  "ASSUMPTIONS_AND_AXIOMS": "Published language/type soundness scope, compiler/runtime assumptions and inventory of unsafe/dynamic boundaries.",
  "CHECKER_OR_KERNEL_BOUNDARY": "Type checker, compiler, elaborator, SMT back end and unsafe libraries are bounded.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for type-system claim boundary.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Type and unsafe-boundary checks rerun after language/compiler/library/API changes.",
  "CORRESPONDENCE_DUTY": "Compiler/runtime faithfully implements the type semantics and deployed code avoids unchecked escape hatches.",
  "MISUSE_TO_PREVENT": "Type safety is a precise but narrow meta-theorem."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P027.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Compiler/runtime faithfully implements the type semantics and deployed code avoids unchecked escape hatches.",
  "ENVIRONMENT_BOUNDARY": "External data and foreign components are validated before entering trusted typed invariants.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Type checker, compiler, elaborator, SMT back end and unsafe libraries are bounded.",
  "DRIFT_DETECTOR": "Type and unsafe-boundary checks rerun after language/compiler/library/API changes.",
  "KNOWN_ESCAPE": "A well-typed program computes the wrong result."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter type-system claim boundary.",
  "IDENTITIES_TO_BIND": "Type and unsafe-boundary checks rerun after language/compiler/library/API changes.",
  "REPLAY_OR_RECHECK": "Type checker, compiler, elaborator, SMT back end and unsafe libraries are bounded.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: State the exact typing theorem and excluded stuck/error classes; map each type feature to an engineering claim; identify unsafe casts, foreign interfaces, dynamic checks and semantic gaps. Use richer types only where the encoded proposition and proof obligations justify the cost.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should type-level quantitative/unit properties interact with runtime data uncertainty?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The proposition encoded by the type matches the claimed failure class.
- Abstraction: Type abstraction does not hide value/behaviour distinctions material to clients.
- Environment: External data and foreign components are validated before entering trusted typed invariants.
- Model/code correspondence: Compiler/runtime faithfully implements the type semantics and deployed code avoids unchecked escape hatches.
- Trusted tools: Type checker, compiler, elaborator, SMT back end and unsafe libraries are bounded.
- Currentness/replay: Type and unsafe-boundary checks rerun after language/compiler/library/API changes.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Type theory, refinement types, RustBelt and behavioural subtyping provide direct lineage. | S045, S046, S047, S089 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_STATED_TYPE_THEOREM | Progress/preservation or richer typing theorems are rigorous but intentionally narrow. | S045, S046 |
| MECHANICAL_REPLAY_STRENGTH | VERY_HIGH | Type checking is deterministic and routinely replayed as part of builds. | S046, S047 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | HIGH_WITHIN_LANGUAGE | Binding to source is strong, but compiler/runtime/unsafe boundaries remain. | S046 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | Industrial safe-language and verified-library use is broad; exact stronger-type evidence varies. | S046, S077, S078 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Large adoption evidence exists for type safety, but comparative proof of functional-correctness impact is property-specific. | S064 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_FOR_LANGUAGE-BASED_ASSURANCE | Strong types can support certification evidence but do not replace requirements/testing. | S052 |
| TRANSFERABILITY_STRENGTH | HIGH_FOR_NARROW_FAILURE_CLASSES | Widely transferable for representation/memory/interface properties, not whole correctness. | S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Unsafe code, compiler semantics and exact encoded proposition determine scope. | S046, S047 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Formal scope itself and unsafe-boundary evidence directly rebut “type safe means correct”. | S046, S089 |

**CRITICISMS:**
- Type safety is a precise but narrow meta-theorem.
- Strong types can shift complexity into casts, proof terms or awkward APIs.
- Behavioural subtyping and refinement types depend on specifications/SMT encodings [S047, S089].
- Safe-language boundaries still require verification of unsafe libraries [S046].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A type-system claim names the prevented failure classes, unsafe boundary and remaining obligations. Stronger types are introduced where they eliminate material misuse or encode stable invariants; functional or temporal correctness is claimed only when represented and proved in the type.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P046 — Type safety means functional correctness, P049 — Stakeholder/world-machine validation. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P027 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while a well-typed program computes the wrong result?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P027?
- Would the cheap path — Use ordinary types for ordinary representation safety; do not encode volatile business logic at the type level without clear payoff — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P027, what decision changes, and should the artefact be retired if no live consumer remains?


### P028 — Dependent/refinement types as selective proof carriers

**PROPERTY_ID:** `P028`  
**PROPERTY_NAME:** Dependent/refinement types as selective proof carriers

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Specification-rich types can carry selected proof obligations when properties fit type-level automation/review. It is intended to prevent: Some stable value-level invariants—length relations, protocol states, units, bounds or functional equations—must travel with data/functions. External proofs can drift from the code they justify.

**MATURE_FORM:** Use dependent/refinement types as proof carriers for compact, stable invariants that callers must preserve. The type’s proposition, SMT/axiom boundary, extraction path and unsafe escape hatches are reviewed; volatile system behaviour remains in contracts, models or tests.

**TRIGGER:** Trigger when a stable data/API invariant is repeatedly violated and can be encoded locally with manageable proof burden.

**CHEAP_PATH:** Use runtime validation or ordinary types for volatile policy, uncertain sensor input or properties whose proof cost exceeds reuse value.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Dependent/refinement types as selective proof carriers",
  "ENGINEERING_CLAIM": "Specification-rich types can carry selected proof obligations when properties fit type-level automation/review.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying dependent/refinement types as selective proof carriers; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The type proposition expresses the intended value relation and handles partial/exceptional cases.",
  "ENVIRONMENT_MODEL": "Untrusted external inputs are checked before constructing trusted typed values.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide dependent/refinement types as selective proof carriers; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: The encoded proposition is weaker/different from the engineering requirement.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which encode selected propositions in dependent/refinement types; require inhabitants/proof terms or discharge refinements through smt; extract or execute verified functions; keep trusted escape hatches and erasure/runtime semantics explicit.",
  "SAFETY_LIVENESS_CLASS": "static analysis type",
  "ABSTRACTION": "Type indices/refinements preserve relevant runtime semantics after erasure.",
  "IMPLEMENTATION_CORRESPONDENCE": "Elaboration, extraction/compiler and FFI preserve typed guarantees.",
  "CHEAP_PATH": "Use runtime validation or ordinary types for volatile policy, uncertain sensor input or properties whose proof cost exceeds reuse value.",
  "MATURE_FORM": "Use dependent/refinement types as proof carriers for compact, stable invariants that callers must preserve. The type’s proposition, SMT/axiom boundary, extraction path and unsafe escape hatches are reviewed; volatile system behaviour remains in contracts, models or tests.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P028; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Dependent/refinement types as selective proof carriers governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Type indices/refinements preserve relevant runtime semantics after erasure.",
  "ESCALATION_TRIGGER": "Trigger when a stable data/API invariant is repeatedly violated and can be encoded locally with manageable proof burden.",
  "CHEAP_PATH": "Use runtime validation or ordinary types for volatile policy, uncertain sensor input or properties whose proof cost exceeds reuse value."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for dependent/refinement types as selective proof carriers.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "Use runtime validation or ordinary types for volatile policy, uncertain sensor input or properties whose proof cost exceeds reuse value."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "Specification-rich types can carry selected proof obligations when properties fit type-level automation/review.",
  "ASSUMPTIONS_AND_AXIOMS": "Stable invariant, supporting libraries/automation, programmer expertise and bounded extraction/unsafe interfaces.",
  "CHECKER_OR_KERNEL_BOUNDARY": "Kernel/type checker, axioms, SMT solver and extraction path are disclosed.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for dependent/refinement types as selective proof carriers.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Types/proofs rebuild after API/library/tool changes; repaired types are semantically diff-reviewed.",
  "CORRESPONDENCE_DUTY": "Elaboration, extraction/compiler and FFI preserve typed guarantees.",
  "MISUSE_TO_PREVENT": "Maximal dependent typing can impair readability, interoperability and iteration speed."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P028.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Elaboration, extraction/compiler and FFI preserve typed guarantees.",
  "ENVIRONMENT_BOUNDARY": "Untrusted external inputs are checked before constructing trusted typed values.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Kernel/type checker, axioms, SMT solver and extraction path are disclosed.",
  "DRIFT_DETECTOR": "Types/proofs rebuild after API/library/tool changes; repaired types are semantically diff-reviewed.",
  "KNOWN_ESCAPE": "The encoded proposition is weaker/different from the engineering requirement."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter dependent/refinement types as selective proof carriers.",
  "IDENTITIES_TO_BIND": "Types/proofs rebuild after API/library/tool changes; repaired types are semantically diff-reviewed.",
  "REPLAY_OR_RECHECK": "Kernel/type checker, axioms, SMT solver and extraction path are disclosed.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Encode selected propositions in dependent/refinement types; require inhabitants/proof terms or discharge refinements through SMT; extract or execute verified functions; keep trusted escape hatches and erasure/runtime semantics explicit.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How can extracted-code and foreign-interface correspondence be made routine?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The type proposition expresses the intended value relation and handles partial/exceptional cases.
- Abstraction: Type indices/refinements preserve relevant runtime semantics after erasure.
- Environment: Untrusted external inputs are checked before constructing trusted typed values.
- Model/code correspondence: Elaboration, extraction/compiler and FFI preserve typed guarantees.
- Trusted tools: Kernel/type checker, axioms, SMT solver and extraction path are disclosed.
- Currentness/replay: Types/proofs rebuild after API/library/tool changes; repaired types are semantically diff-reviewed.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Intuitionistic type theory, Coq/Rocq and refinement types directly establish the lineage. | S045, S043, S047 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH | Inhabitation/type checking provides strong proof for the encoded proposition under the calculus. | S045 |
| MECHANICAL_REPLAY_STRENGTH | VERY_HIGH | Kernel/type-checker replay is intrinsic. | S043, S047 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_HIGH | Binding to source/API can be strong; extraction, erasure, FFI and unsafe code reduce end-to-end strength. | S046, S080 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_VERIFIED_LIBRARIES | HACL*, EverCrypt and CakeML show strong selective use. | S077, S078, S080 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Case evidence is strong; broad comparative maintenance/ROI evidence is limited. | S096 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM_HIGH | Can support high-assurance component evidence, but standards remain method-neutral. | S052 |
| TRANSFERABILITY_STRENGTH | CONTEXT_DEPENDENT | Powerful for stable local propositions; excessive for volatile/open-system properties. | S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Specification, axioms, extraction and unsafe boundaries dominate applicability. | S046, S047 |
| CONTRARY_EVIDENCE_STRENGTH | MEDIUM_HIGH | Maintenance and specification criticisms narrow use without undermining checked type proofs. | S076, S096 |

**CRITICISMS:**
- Maximal dependent typing can impair readability, interoperability and iteration speed.
- Proof by type checking is only as meaningful as the type specification.
- Automation and library coupling create maintenance costs.
- Not all environmental, temporal or quantitative uncertainty fits a static type.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Use dependent/refinement types as proof carriers for compact, stable invariants that callers must preserve. The type’s proposition, SMT/axiom boundary, extraction path and unsafe escape hatches are reviewed; volatile system behaviour remains in contracts, models or tests.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P027 — Type-system claim boundary, P042 — Cost/payoff trigger discipline. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P028 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while the encoded proposition is weaker/different from the engineering requirement?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P028?
- Would the cheap path — Use runtime validation or ordinary types for volatile policy, uncertain sensor input or properties whose proof cost exceeds reuse value — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P028, what decision changes, and should the artefact be retired if no live consumer remains?


### P029 — Concurrency/distributed protocol modelling

**PROPERTY_ID:** `P029`  
**PROPERTY_NAME:** Concurrency/distributed protocol modelling

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Interleavings, message loss/reorder, crash/recovery, consensus and weak memory need explicit formal semantics when they determine failure. It is intended to prevent: Concurrent/distributed failures arise from enormous interleaving spaces, races, deadlocks, stale messages, partitions, retries, weak memory and failures that ordinary sequential reasoning or happy-path testing misses.

**MATURE_FORM:** Formalise the smallest protocol core and failure model that governs coordination risk; separate safety, liveness, consistency and availability; state fairness/network/memory assumptions; establish implementation correspondence or downgrade to design evidence; retain empirical chaos/fault testing at the boundary.

**TRIGGER:** Trigger for coordination, replication, concurrency, distributed workflows, lock-free algorithms, weak-memory code or fault-tolerant protocols.

**CHEAP_PATH:** For simple isolated concurrency, race detectors/stress tests or a small state machine may remove the risk more cheaply than full protocol proof.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Concurrency/distributed protocol modelling",
  "ENGINEERING_CLAIM": "Interleavings, message loss/reorder, crash/recovery, consensus and weak memory need explicit formal semantics when they determine failure.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying concurrency/distributed protocol modelling; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Safety, liveness, consistency, availability and durability claims are separated.",
  "ENVIRONMENT_MODEL": "Network, scheduler, clock, storage and failure-detector assumptions are justified.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide concurrency/distributed protocol modelling; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Network/failure model excludes duplication, reordering, corruption, partitions or recovery.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which model processes, messages/shared memory, network/failure semantics, scheduler/fairness and protocol state; check invariants, deadlock, liveness and refinement; use partial-order/symmetry reduction, compositional contracts, linearizability/serialisability and implementation transformers; stress assumptions empirically.",
  "SAFETY_LIVENESS_CLASS": "domain specific",
  "ABSTRACTION": "Data/participant/reduction abstractions preserve the protocol property and failure behaviours.",
  "IMPLEMENTATION_CORRESPONDENCE": "Serialization, retries, shims, persistence and weak-memory semantics are covered or separately assured.",
  "CHEAP_PATH": "For simple isolated concurrency, race detectors/stress tests or a small state machine may remove the risk more cheaply than full protocol proof.",
  "MATURE_FORM": "Formalise the smallest protocol core and failure model that governs coordination risk; separate safety, liveness, consistency and availability; state fairness/network/memory assumptions; establish implementation correspondence or downgrade to design evidence; retain empirical chaos/fault testing at the boundary.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P029; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to concurrency/distributed protocol modelling.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Concurrent/distributed failures arise from enormous interleaving spaces, races, deadlocks, stale messages, partitions, retries, weak memory and failures that ordinary sequential reasoning or happy-path testing misses..",
  "RELATION": "Serialization, retries, shims, persistence and weak-memory semantics are covered or separately assured.",
  "SOUNDNESS_DUTY": "Data/participant/reduction abstractions preserve the protocol property and failure behaviours.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Famous verified systems still exhibited defects outside model/proof boundaries [S092].",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Formalise the smallest protocol core and failure model that governs coordination risk; separate safety, liveness, consistency and availability; state fairness/network/memory assumptions; establish implementation correspondence or downgrade to design evidence; retain empirical chaos/fault testing at the boundary.",
  "KNOWN_GAP": "Network/failure model excludes duplication, reordering, corruption, partitions or recovery."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Interleavings, message loss/reorder, crash/recovery, consensus and weak memory need explicit formal semantics when they determine failure.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for concurrency/distributed protocol modelling.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Data/participant/reduction abstractions preserve the protocol property and failure behaviours.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Network/failure model excludes duplication, reordering, corruption, partitions or recovery..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Finds rare interleaving and protocol-design defects before deployment, clarifies fault/consistency semantics, and provides reusable invariants for implementation and operations."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Concurrency/distributed protocol modelling may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger for coordination, replication, concurrency, distributed workflows, lock-free algorithms, weak-memory code or fault-tolerant protocols.",
  "CHEAPER_EVIDENCE": "For simple isolated concurrency, race detectors/stress tests or a small state machine may remove the risk more cheaply than full protocol proof."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P029.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Serialization, retries, shims, persistence and weak-memory semantics are covered or separately assured.",
  "ENVIRONMENT_BOUNDARY": "Network, scheduler, clock, storage and failure-detector assumptions are justified.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Model checker/prover, distributed semantics, reductions and extraction/generation tools are bounded.",
  "DRIFT_DETECTOR": "Protocol, topology, timeout, storage, compiler and infrastructure changes trigger model/proof/fault-test replay.",
  "KNOWN_ESCAPE": "Network/failure model excludes duplication, reordering, corruption, partitions or recovery."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter concurrency/distributed protocol modelling.",
  "IDENTITIES_TO_BIND": "Protocol, topology, timeout, storage, compiler and infrastructure changes trigger model/proof/fault-test replay.",
  "REPLAY_OR_RECHECK": "Model checker/prover, distributed semantics, reductions and extraction/generation tools are bounded.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Model processes, messages/shared memory, network/failure semantics, scheduler/fairness and protocol state; check invariants, deadlock, liveness and refinement; use partial-order/symmetry reduction, compositional contracts, linearizability/serialisability and implementation transformers; stress assumptions empirically.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should deterministic protocol proofs combine with probabilistic infrastructure and performance evidence?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Safety, liveness, consistency, availability and durability claims are separated.
- Abstraction: Data/participant/reduction abstractions preserve the protocol property and failure behaviours.
- Environment: Network, scheduler, clock, storage and failure-detector assumptions are justified.
- Model/code correspondence: Serialization, retries, shims, persistence and weak-memory semantics are covered or separately assured.
- Trusted tools: Model checker/prover, distributed semantics, reductions and extraction/generation tools are bounded.
- Currentness/replay: Protocol, topology, timeout, storage, compiler and infrastructure changes trigger model/proof/fault-test replay.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Process calculi, TLA and distributed verification cases provide direct plural provenance. | S017, S018, S019, S029, S030, S031 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_CONDITIONALLY | Safety/liveness/refinement proofs are strong for stated network, failure, fairness and memory semantics. | S030, S105 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Models/proofs replay mechanically; large state/proof cost can be substantial. | S029, S030 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_LOW_ON_AVERAGE | Flagship systems have mappings, but empirical defects show unverified layers remain. | S092 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | AWS, IronFleet and Verdi are major industrial/research cases. | S029, S030, S031 |
| EMPIRICAL_COMPARATIVE_STRENGTH | HIGH_NEGATIVE_AND_CASE_EVIDENCE | Fonseca et al. provide direct defect evidence; broad comparative productivity evidence is limited. | S092 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_IN_CRITICAL_PROTOCOLS | Formal protocol evidence is used in security/safety domains, but exact certification credit is contextual. | S052, S079 |
| TRANSFERABILITY_STRENGTH | DOMAIN_SPECIFIC_BUT_IMPORTANT | Highly transferable within concurrency/distribution, not a universal software property. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Fault, fairness, memory, participant/data bounds and implementation stack determine validity. | S092, S105, S106 |
| CONTRARY_EVIDENCE_STRENGTH | VERY_HIGH | Empirical verified-system failures and current complexity/weak-memory research strongly constrain hype. | S092, S103, S106 |

**CRITICISMS:**
- Famous verified systems still exhibited defects outside model/proof boundaries [S092].
- Concurrency reductions and liveness automation remain hard and assumption-sensitive [S103, S105].
- Weak-memory formalisms show that sequentially consistent interleavings are insufficient for low-level code [S106].
- Operational availability/performance may conflict with strong consistency/refinement properties.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Formalise the smallest protocol core and failure model that governs coordination risk; separate safety, liveness, consistency and availability; state fairness/network/memory assumptions; establish implementation correspondence or downgrade to design evidence; retain empirical chaos/fault testing at the boundary.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P003 — Environment model boundary, P019 — State explosion management. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P029 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while network/failure model excludes duplication, reordering, corruption, partitions or recovery?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P029?
- Would the cheap path — For simple isolated concurrency, race detectors/stress tests or a small state machine may remove the risk more cheaply than full protocol proof — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P029, what decision changes, and should the artefact be retired if no live consumer remains?


### P030 — Linearizability/serialisability/refinement properties

**PROPERTY_ID:** `P030`  
**PROPERTY_NAME:** Linearizability/serialisability/refinement properties

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Concurrent object/database claims require explicit observational equivalence/refinement criteria. It is intended to prevent: “Thread-safe”, “consistent” or “transactional” is too vague. Concurrent operations can return individually plausible values while histories violate atomic-object or database semantics; alternatively, a strong consistency property may be unnecessary or too costly.

**MATURE_FORM:** A concurrency-consistency claim names its history model, observer, operations, real-time/memory semantics and non-covered properties. Proof or checking is bound to implementation events; progress, persistence and business invariants are not inferred from safety equivalence.

**TRIGGER:** Trigger when multiple operations overlap or transactions interleave and correctness depends on observable history.

**CHEAP_PATH:** For single-threaded or externally serialised components, direct invariants/tests may be enough.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Linearizability/serialisability/refinement properties",
  "ENGINEERING_CLAIM": "Concurrent object/database claims require explicit observational equivalence/refinement criteria.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying linearizability/serialisability/refinement properties; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The selected consistency property matches consumer expectations and does not stand in for omitted liveness/durability.",
  "ENVIRONMENT_MODEL": "Clock/order, storage and external side-effect assumptions are explicit.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide linearizability/serialisability/refinement properties; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Linearizability is claimed without real-time event capture or for only a subset of operations.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which choose the required history/refinement condition; define operations, invocation/response events, transaction conflicts and observer; prove history inclusion, linearisation points, simulation or serial-equivalence; separately check progress, durability and application invariants.",
  "SAFETY_LIVENESS_CLASS": "domain specific",
  "ABSTRACTION": "History abstraction preserves real-time/conflict/observation distinctions.",
  "IMPLEMENTATION_CORRESPONDENCE": "Invocation/response/commit events and memory semantics map to actual implementation.",
  "CHEAP_PATH": "For single-threaded or externally serialised components, direct invariants/tests may be enough.",
  "MATURE_FORM": "A concurrency-consistency claim names its history model, observer, operations, real-time/memory semantics and non-covered properties. Proof or checking is bound to implementation events; progress, persistence and business invariants are not inferred from safety equivalence.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P030; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to linearizability/serialisability/refinement properties.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in “Thread-safe”, “consistent” or “transactional” is too vague. Concurrent operations can return individually plausible values while histories violate atomic-object or database semantics; alternatively, a strong consistency property may be unnecessary or too costly..",
  "RELATION": "Invocation/response/commit events and memory semantics map to actual implementation.",
  "SOUNDNESS_DUTY": "History abstraction preserves real-time/conflict/observation distinctions.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Linearizability is a safety property, not progress, availability, durability or total application correctness [S090].",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "A concurrency-consistency claim names its history model, observer, operations, real-time/memory semantics and non-covered properties. Proof or checking is bound to implementation events; progress, persistence and business invariants are not inferred from safety equivalence.",
  "KNOWN_GAP": "Linearizability is claimed without real-time event capture or for only a subset of operations."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Concurrent object/database claims require explicit observational equivalence/refinement criteria.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for linearizability/serialisability/refinement properties.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "History abstraction preserves real-time/conflict/observation distinctions.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Linearizability is claimed without real-time event capture or for only a subset of operations..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Replaces ambiguous consistency labels with discriminating acceptance criteria, finds concurrency anomalies and supports safe implementation substitutions."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Linearizability/serialisability/refinement properties may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger when multiple operations overlap or transactions interleave and correctness depends on observable history.",
  "CHEAPER_EVIDENCE": "For single-threaded or externally serialised components, direct invariants/tests may be enough."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P030.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Invocation/response/commit events and memory semantics map to actual implementation.",
  "ENVIRONMENT_BOUNDARY": "Clock/order, storage and external side-effect assumptions are explicit.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "History checker/prover and event instrumentation preserve ordering semantics.",
  "DRIFT_DETECTOR": "Optimisation, memory-model, transaction or operation changes trigger proof/history-test replay.",
  "KNOWN_ESCAPE": "Linearizability is claimed without real-time event capture or for only a subset of operations."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter linearizability/serialisability/refinement properties.",
  "IDENTITIES_TO_BIND": "Optimisation, memory-model, transaction or operation changes trigger proof/history-test replay.",
  "REPLAY_OR_RECHECK": "History checker/prover and event instrumentation preserve ordering semantics.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Choose the required history/refinement condition; define operations, invocation/response events, transaction conflicts and observer; prove history inclusion, linearisation points, simulation or serial-equivalence; separately check progress, durability and application invariants.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should external side effects and irreversible actions be incorporated into serialisability models?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The selected consistency property matches consumer expectations and does not stand in for omitted liveness/durability.
- Abstraction: History abstraction preserves real-time/conflict/observation distinctions.
- Environment: Clock/order, storage and external side-effect assumptions are explicit.
- Model/code correspondence: Invocation/response/commit events and memory semantics map to actual implementation.
- Trusted tools: History checker/prover and event instrumentation preserve ordering semantics.
- Currentness/replay: Optimisation, memory-model, transaction or operation changes trigger proof/history-test replay.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Papadimitriou and Herlihy–Wing provide direct foundational definitions. | S090, S091 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH | History-equivalence/refinement theorems are rigorous for specified events and semantics. | S090, S091 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Mechanised proofs and history checkers can replay exact traces/models. | S030 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM | Event instrumentation, memory model and implementation mapping remain key gaps. | S092, S106 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_DATABASES_AND_CONCURRENT_OBJECTS | The properties are standard in their domains and used in verified systems. | S030, S031 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Substantial theory/case evidence exists; comparative evidence on property choice versus user outcomes is mixed. | S065 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM_HIGH | Can support high-assurance concurrency evidence, but standards do not make one consistency condition universal. | S052 |
| TRANSFERABILITY_STRENGTH | DOMAIN_SPECIFIC | Transfer is strong within concurrent objects/databases, not to unrelated claims. | S090, S091 |
| ASSUMPTION_SENSITIVITY | HIGH | Observer, event, memory and progress/durability boundaries are decisive. | S090, S106 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Formal definitions themselves and empirical implementation-gap evidence directly constrain overclaiming. | S092, S106 |

**CRITICISMS:**
- Linearizability is a safety property, not progress, availability, durability or total application correctness [S090].
- Serializability can admit behaviours users consider anomalous and excludes external effects [S091].
- History-based proofs depend on precise event and memory semantics [S106].
- The strongest property is not always the best engineering trade-off.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A concurrency-consistency claim names its history model, observer, operations, real-time/memory semantics and non-covered properties. Proof or checking is bound to implementation events; progress, persistence and business invariants are not inferred from safety equivalence.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P014 — Refinement/simulation correspondence, P029 — Concurrency/distributed protocol modelling. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P030 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while linearizability is claimed without real-time event capture or for only a subset of operations?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P030?
- Would the cheap path — For single-threaded or externally serialised components, direct invariants/tests may be enough — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P030, what decision changes, and should the artefact be retired if no live consumer remains?


### P031 — Runtime monitor scope

**PROPERTY_ID:** `P031`  
**PROPERTY_NAME:** Runtime monitor scope

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Runtime verification checks observed traces against formal properties but must state observability, latency and enforcement limits. It is intended to prevent: Some properties cannot be proved statically because code is opaque, environment uncertain or deployment configuration dynamic. Yet observing a finite execution cannot establish unobserved behaviour or arbitrary future liveness.

**MATURE_FORM:** Use runtime verification for observable violations and dynamic assumptions. Publish monitorability, event coverage, verdict meaning, overhead and response. Green means no observed violation under current instrumentation—not proof of all executions.

**TRIGGER:** Trigger for dynamic, partially opaque or environment-dependent properties that are observable at runtime and materially actionable.

**CHEAP_PATH:** Use a simple assertion/log query when the property is local and immediate; use static proof when violation cannot safely be allowed even once.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Runtime monitor scope",
  "ENGINEERING_CLAIM": "Runtime verification checks observed traces against formal properties but must state observability, latency and enforcement limits.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying runtime monitor scope; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Property semantics over finite traces and inconclusive cases are explicit.",
  "ENVIRONMENT_MODEL": "Observation loss, clock uncertainty, privacy and distributed order are modelled.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide runtime monitor scope; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Relevant events are not instrumented or are dropped/reordered.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which compile a monitorable property into an online/offline monitor; define event instrumentation, observation granularity, verdict semantics (true/false/inconclusive), clock/order handling and response.",
  "SAFETY_LIVENESS_CLASS": "runtime verification",
  "ABSTRACTION": "Event projection preserves violations relevant to the claim.",
  "IMPLEMENTATION_CORRESPONDENCE": "Instrumentation is bound to the actual execution points and cannot silently miss alternate paths.",
  "CHEAP_PATH": "Use a simple assertion/log query when the property is local and immediate; use static proof when violation cannot safely be allowed even once.",
  "MATURE_FORM": "Use runtime verification for observable violations and dynamic assumptions. Publish monitorability, event coverage, verdict meaning, overhead and response. Green means no observed violation under current instrumentation—not proof of all executions.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P031; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to runtime monitor scope.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Some properties cannot be proved statically because code is opaque, environment uncertain or deployment configuration dynamic. Yet observing a finite execution cannot establish unobserved behaviour or arbitrary future liveness..",
  "RELATION": "Instrumentation is bound to the actual execution points and cannot silently miss alternate paths.",
  "SOUNDNESS_DUTY": "Event projection preserves violations relevant to the claim.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Runtime verification observes only executed and instrumented behaviour.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Use runtime verification for observable violations and dynamic assumptions. Publish monitorability, event coverage, verdict meaning, overhead and response. Green means no observed violation under current instrumentation—not proof of all executions.",
  "KNOWN_GAP": "Relevant events are not instrumented or are dropped/reordered."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for runtime monitor scope.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "Use a simple assertion/log query when the property is local and immediate; use static proof when violation cannot safely be allowed even once."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Runtime monitor scope may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger for dynamic, partially opaque or environment-dependent properties that are observable at runtime and materially actionable.",
  "CHEAPER_EVIDENCE": "Use a simple assertion/log query when the property is local and immediate; use static proof when violation cannot safely be allowed even once."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P031.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Instrumentation is bound to the actual execution points and cannot silently miss alternate paths.",
  "ENVIRONMENT_BOUNDARY": "Observation loss, clock uncertainty, privacy and distributed order are modelled.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Monitor synthesis/runtime, event transport, clock/order reconstruction and storage are bounded.",
  "DRIFT_DETECTOR": "Property, event schema, instrumentation and deployment version changes require monitor regeneration/validation.",
  "KNOWN_ESCAPE": "Relevant events are not instrumented or are dropped/reordered."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter runtime monitor scope.",
  "IDENTITIES_TO_BIND": "Property, event schema, instrumentation and deployment version changes require monitor regeneration/validation.",
  "REPLAY_OR_RECHECK": "Monitor synthesis/runtime, event transport, clock/order reconstruction and storage are bounded.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Compile a monitorable property into an online/offline monitor; define event instrumentation, observation granularity, verdict semantics (true/false/inconclusive), clock/order handling and response. Validate monitor against synthetic traces and measure coverage/overhead.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "When does runtime enforcement reduce risk versus create a new failure mode?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Property semantics over finite traces and inconclusive cases are explicit.
- Abstraction: Event projection preserves violations relevant to the claim.
- Environment: Observation loss, clock uncertainty, privacy and distributed order are modelled.
- Model/code correspondence: Instrumentation is bound to the actual execution points and cannot silently miss alternate paths.
- Trusted tools: Monitor synthesis/runtime, event transport, clock/order reconstruction and storage are bounded.
- Currentness/replay: Property, event schema, instrumentation and deployment version changes require monitor regeneration/validation.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Runtime verification and distributed RV surveys provide direct lineage. | S066, S067, S068 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_OBSERVED_PREFIX | Monitor verdicts are formally meaningful for the observed trace and monitorable property. | S066, S099 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Trace replay and monitor execution are mechanically reproducible when logs are complete. | S067 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_HIGH_FOR_OBSERVED_EVENTS | Binding can be direct at runtime, but omitted/dropped events reduce coverage. | S068, S099 |
| INDUSTRIAL_CASE_STRENGTH | MEDIUM_HIGH | RV has broad research and selected industrial use, but public comparative deployment evidence is uneven. | S066, S068 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM_HIGH | Overhead studies and case work provide empirical evidence; general effectiveness comparisons remain limited. | S104 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM | Runtime monitoring can supplement certification/operations but rarely substitutes for design verification. | S052 |
| TRANSFERABILITY_STRENGTH | CONTEXT_DEPENDENT | Highly transferable to observable dynamic properties; unsuitable for unmonitorable/unrecoverable claims. | S099 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Observability, event integrity, finite-prefix semantics and response determine value. | S068, S099 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Monitorability and overhead evidence directly limits “green monitor means safe”. | S099, S104 |

**CRITICISMS:**
- Runtime verification observes only executed and instrumented behaviour.
- Liveness and hyperproperties may be inconclusive or unmonitorable from finite single traces [S021, S099].
- Instrumentation overhead and trace infrastructure can be material [S104].
- A formal monitor does not make its event source authoritative.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Use runtime verification for observable violations and dynamic assumptions. Publish monitorability, event coverage, verdict meaning, overhead and response. Green means no observed violation under current instrumentation—not proof of all executions.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P003 — Environment model boundary, P032 — Monitor currentness and fail-open/fail-closed design. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P031 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while relevant events are not instrumented or are dropped/reordered?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P031?
- Would the cheap path — Use a simple assertion/log query when the property is local and immediate; use static proof when violation cannot safely be allowed even once — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P031, what decision changes, and should the artefact be retired if no live consumer remains?


### P032 — Monitor currentness and fail-open/fail-closed design

**PROPERTY_ID:** `P032`  
**PROPERTY_NAME:** Monitor currentness and fail-open/fail-closed design

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** A monitor is assurance only if tied to current property/source/configuration and failure mode policy. It is intended to prevent: A correct monitor can still be stale, disabled, partitioned, overloaded or configured against an old schema. Its response can either permit unsafe behaviour (fail open) or create outages/denial of service (fail closed).

**MATURE_FORM:** A production monitor has identity binding, self-health evidence, tested failure modes, explicit containment policy and automatic downgrade when event coverage or version correspondence is lost. Detection and enforcement claims are separated.

**TRIGGER:** Trigger when runtime-monitor output controls traffic, shutdown, admission, release or regulatory evidence.

**CHEAP_PATH:** For advisory low-risk metrics, ordinary alerting with clear non-assurance status may be enough.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Monitor currentness and fail-open/fail-closed design",
  "ENGINEERING_CLAIM": "A monitor is assurance only if tied to current property/source/configuration and failure mode policy.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying monitor currentness and fail-open/fail-closed design; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Detection, enforcement and degraded-mode guarantees are distinct.",
  "ENVIRONMENT_MODEL": "Partitions, overload, clock skew and log loss are included in monitor-failure analysis.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide monitor currentness and fail-open/fail-closed design; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Monitor silently stops receiving events.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which version property, monitor code, event schema and target configuration together; heartbeat and self-monitor the monitor; define fail-open/fail-closed/degraded response by hazard; test monitor failure, backlog and schema drift; retain violation provenance and rollback/update controls.",
  "SAFETY_LIVENESS_CLASS": "runtime verification",
  "ABSTRACTION": "Schema transforms and event aggregation preserve violation semantics.",
  "IMPLEMENTATION_CORRESPONDENCE": "Target and monitor versions/configurations are automatically matched.",
  "CHEAP_PATH": "For advisory low-risk metrics, ordinary alerting with clear non-assurance status may be enough.",
  "MATURE_FORM": "A production monitor has identity binding, self-health evidence, tested failure modes, explicit containment policy and automatic downgrade when event coverage or version correspondence is lost. Detection and enforcement claims are separated.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P032; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to monitor currentness and fail-open/fail-closed design.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in A correct monitor can still be stale, disabled, partitioned, overloaded or configured against an old schema. Its response can either permit unsafe behaviour (fail open) or create outages/denial of service (fail closed)..",
  "RELATION": "Target and monitor versions/configurations are automatically matched.",
  "SOUNDNESS_DUTY": "Schema transforms and event aggregation preserve violation semantics.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Monitoring creates another software system and trusted operational dependency.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "A production monitor has identity binding, self-health evidence, tested failure modes, explicit containment policy and automatic downgrade when event coverage or version correspondence is lost. Detection and enforcement claims are separated.",
  "KNOWN_GAP": "Monitor silently stops receiving events."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for monitor currentness and fail-open/fail-closed design.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For advisory low-risk metrics, ordinary alerting with clear non-assurance status may be enough."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Monitor currentness and fail-open/fail-closed design may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger when runtime-monitor output controls traffic, shutdown, admission, release or regulatory evidence.",
  "CHEAPER_EVIDENCE": "For advisory low-risk metrics, ordinary alerting with clear non-assurance status may be enough."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P032.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Target and monitor versions/configurations are automatically matched.",
  "ENVIRONMENT_BOUNDARY": "Partitions, overload, clock skew and log loss are included in monitor-failure analysis.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Deployment controller, event pipeline and enforcement actuator join the monitor TCB.",
  "DRIFT_DETECTOR": "Stale identity or failed heartbeat revokes assurance; monitor regressions replay on every schema/property update.",
  "KNOWN_ESCAPE": "Monitor silently stops receiving events."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter monitor currentness and fail-open/fail-closed design.",
  "IDENTITIES_TO_BIND": "Stale identity or failed heartbeat revokes assurance; monitor regressions replay on every schema/property update.",
  "REPLAY_OR_RECHECK": "Deployment controller, event pipeline and enforcement actuator join the monitor TCB.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Version property, monitor code, event schema and target configuration together; heartbeat and self-monitor the monitor; define fail-open/fail-closed/degraded response by hazard; test monitor failure, backlog and schema drift; retain violation provenance and rollback/update controls.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "What provenance is sufficient to reconstruct distributed verdicts after partial log loss?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Detection, enforcement and degraded-mode guarantees are distinct.
- Abstraction: Schema transforms and event aggregation preserve violation semantics.
- Environment: Partitions, overload, clock skew and log loss are included in monitor-failure analysis.
- Model/code correspondence: Target and monitor versions/configurations are automatically matched.
- Trusted tools: Deployment controller, event pipeline and enforcement actuator join the monitor TCB.
- Currentness/replay: Stale identity or failed heartbeat revokes assurance; monitor regressions replay on every schema/property update.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | MEDIUM_HIGH | The lifecycle concern is a modern extension of runtime-verification and distributed-monitoring practice. | S066, S068 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_DEFINED_FAILURE_LOGIC | Fail-mode and version-state invariants can be formalised, but operational availability remains empirical. | S099 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Monitor-failure tests and trace replay are mechanically reproducible. | S104 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | HIGH_WHEN_IDENTITY_AUTOMATED | Direct deployment binding can be strong; pipeline health remains a live assumption. | S068 |
| INDUSTRIAL_CASE_STRENGTH | MEDIUM | Operational practices exist, but peer-reviewed case evidence on fail-mode governance is thinner than core RV theory. | S068 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM_HIGH | Overhead and distributed-observability studies support the risks; comparative response-policy evidence is limited. | S104 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM | Monitoring may support operational assurance but certification guidance is not monitor-specific. | S052 |
| TRANSFERABILITY_STRENGTH | CONTEXT_DEPENDENT | Critical for production enforcement, excessive for advisory telemetry. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Event pipeline, version identity, monitor health and response policy dominate. | S068, S104 |
| CONTRARY_EVIDENCE_STRENGTH | MEDIUM_HIGH | Known operational and overhead limits constrain claims; direct negative field studies remain sparse. | S104 |

**CRITICISMS:**
- Monitoring creates another software system and trusted operational dependency.
- Safety and availability pressures can conflict in failure response.
- Overhead/backpressure can alter the monitored system [S104].
- Frequent specification change can make monitors stale faster than proof artefacts.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A production monitor has identity binding, self-health evidence, tested failure modes, explicit containment policy and automatic downgrade when event coverage or version correspondence is lost. Detection and enforcement claims are separated.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P031 — Runtime monitor scope, P048 — Retirement of stale formal artefacts. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P032 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while monitor silently stops receiving events?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P032?
- Would the cheap path — For advisory low-risk metrics, ordinary alerting with clear non-assurance status may be enough — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P032, what decision changes, and should the artefact be retired if no live consumer remains?


### P033 — Verified compiler/toolchain scope

**PROPERTY_ID:** `P033`  
**PROPERTY_NAME:** Verified compiler/toolchain scope

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Verified compilers/toolchains provide semantic-preservation evidence for a specified language/toolchain, not total system correctness. It is intended to prevent: Source-level correctness can be destroyed by compiler miscompilation, extraction, linker, assembler, runtime or hardware behaviour. Conversely, verifying the compiler does not prove the source program or its requirement.

**MATURE_FORM:** A verified-toolchain claim names source language subset, defined behaviours, preserved observation/property, passes and unverified stages; the deployed binary is tied to exact source/options/tool identity. Source correctness and environment assurance remain separate.

**TRIGGER:** Trigger when source-level formal evidence controls a binary-level claim in critical code or compiler-introduced defects are material.

**CHEAP_PATH:** For low-risk software, compiler diversity, translation validation of critical builds or extensive testing may be cheaper than adopting a verified compiler.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Verified compiler/toolchain scope",
  "ENGINEERING_CLAIM": "Verified compilers/toolchains provide semantic-preservation evidence for a specified language/toolchain, not total system correctness.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying verified compiler/toolchain scope; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The source program’s property is separately established and compatible with compiler preservation theorem.",
  "ENVIRONMENT_MODEL": "Runtime ABI, hardware and system libraries satisfy target semantics.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide verified compiler/toolchain scope; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Source program invokes undefined/unspecified behaviour outside theorem scope.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which prove semantic preservation for defined source/target languages and passes; identify undefined behaviour and accepted subsets; validate or verify remaining compiler/linker/assembler stages; bind exact source/options/target to binary; test and analyse the tcb.",
  "SAFETY_LIVENESS_CLASS": "verified toolchain",
  "ABSTRACTION": "Source/target semantics model relevant observations, including undefined behaviour and property-specific effects.",
  "IMPLEMENTATION_CORRESPONDENCE": "Exact source/options/compiler output are bound to deployed binary; no unverified postprocessing.",
  "CHEAP_PATH": "For low-risk software, compiler diversity, translation validation of critical builds or extensive testing may be cheaper than adopting a verified compiler.",
  "MATURE_FORM": "A verified-toolchain claim names source language subset, defined behaviours, preserved observation/property, passes and unverified stages; the deployed binary is tied to exact source/options/tool identity. Source correctness and environment assurance remain separate.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P033; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to verified compiler/toolchain scope.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Source-level correctness can be destroyed by compiler miscompilation, extraction, linker, assembler, runtime or hardware behaviour. Conversely, verifying the compiler does not prove the source program or its requirement..",
  "RELATION": "Exact source/options/compiler output are bound to deployed binary; no unverified postprocessing.",
  "SOUNDNESS_DUTY": "Source/target semantics model relevant observations, including undefined behaviour and property-specific effects.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "CompCert TCB analysis documents modelling, external-algorithm and toolchain loopholes [S094].",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "A verified-toolchain claim names source language subset, defined behaviours, preserved observation/property, passes and unverified stages; the deployed binary is tied to exact source/options/tool identity. Source correctness and environment assurance remain separate.",
  "KNOWN_GAP": "Source program invokes undefined/unspecified behaviour outside theorem scope."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for verified compiler/toolchain scope.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For low-risk software, compiler diversity, translation validation of critical builds or extensive testing may be cheaper than adopting a verified compiler."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "Verified compilers/toolchains provide semantic-preservation evidence for a specified language/toolchain, not total system correctness.",
  "ASSUMPTIONS_AND_AXIOMS": "Supported source subset, target semantics, build options, residual stage inventory and source-to-binary provenance.",
  "CHECKER_OR_KERNEL_BOUNDARY": "Parser, extraction, assembler/linker, external algorithms, proof assistant and build system are declared.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for verified compiler/toolchain scope.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Compiler, options, source, target, linker/runtime or hardware changes require rebuild and proof/provenance revalidation.",
  "CORRESPONDENCE_DUTY": "Exact source/options/compiler output are bound to deployed binary; no unverified postprocessing.",
  "MISUSE_TO_PREVENT": "CompCert TCB analysis documents modelling, external-algorithm and toolchain loopholes [S094]."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P033.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Exact source/options/compiler output are bound to deployed binary; no unverified postprocessing.",
  "ENVIRONMENT_BOUNDARY": "Runtime ABI, hardware and system libraries satisfy target semantics.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Parser, extraction, assembler/linker, external algorithms, proof assistant and build system are declared.",
  "DRIFT_DETECTOR": "Compiler, options, source, target, linker/runtime or hardware changes require rebuild and proof/provenance revalidation.",
  "KNOWN_ESCAPE": "Source program invokes undefined/unspecified behaviour outside theorem scope."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter verified compiler/toolchain scope.",
  "IDENTITIES_TO_BIND": "Compiler, options, source, target, linker/runtime or hardware changes require rebuild and proof/provenance revalidation.",
  "REPLAY_OR_RECHECK": "Parser, extraction, assembler/linker, external algorithms, proof assistant and build system are declared.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Prove semantic preservation for defined source/target languages and passes; identify undefined behaviour and accepted subsets; validate or verify remaining compiler/linker/assembler stages; bind exact source/options/target to binary; test and analyse the TCB.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should verified toolchains handle evolving language standards and undefined behaviour?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The source program’s property is separately established and compatible with compiler preservation theorem.
- Abstraction: Source/target semantics model relevant observations, including undefined behaviour and property-specific effects.
- Environment: Runtime ABI, hardware and system libraries satisfy target semantics.
- Model/code correspondence: Exact source/options/compiler output are bound to deployed binary; no unverified postprocessing.
- Trusted tools: Parser, extraction, assembler/linker, external algorithms, proof assistant and build system are declared.
- Currentness/replay: Compiler, options, source, target, linker/runtime or hardware changes require rebuild and proof/provenance revalidation.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | CompCert and CakeML provide direct verified-toolchain lineage. | S024, S080 |
| FORMAL_SOUNDNESS_STRENGTH | VERY_HIGH_FOR_STATED_SEMANTICS | Machine-checked semantic preservation is strong for defined source behaviours and targets. | S024 |
| MECHANICAL_REPLAY_STRENGTH | VERY_HIGH | Compiler proofs and build validations are replayable. | S024, S080 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | HIGH_ONLY_WITH_PROVENANCE | Proof-to-binary strength is high when supported stages/identity are covered; otherwise it drops. | S093, S110 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | CompCert, CakeML and seL4 binary verification are flagship cases. | S024, S080, S093 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM_HIGH | Compiler testing evidence supports reduced wrong-code risk, while broad ROI comparison is limited. | S024, S094 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_IN_CRITICAL_SOFTWARE | Verified compilers can support high-assurance arguments, with tool/configuration obligations. | S051, S052 |
| TRANSFERABILITY_STRENGTH | DOMAIN_SPECIFIC_BUT_STRONG | Highly valuable for critical compiled code; not a universal prerequisite. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Undefined behaviour, target, options, residual stages and preserved property define scope. | S094, S110 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | TCB analysis directly counters whole-toolchain overclaiming. | S094 |

**CRITICISMS:**
- CompCert TCB analysis documents modelling, external-algorithm and toolchain loopholes [S094].
- Semantic preservation is property-relative; ordinary compiler correctness may not preserve side-channel or real-time properties.
- Verified compilation cannot repair an incorrect source specification/program.
- Binary provenance and configuration remain separate evidence.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A verified-toolchain claim names source language subset, defined behaviours, preserved observation/property, passes and unverified stages; the deployed binary is tied to exact source/options/tool identity. Source correctness and environment assurance remain separate.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P034 — Translation validation per-run evidence, P050 — Domain-specific verified libraries/protocols. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P033 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while source program invokes undefined/unspecified behaviour outside theorem scope?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P033?
- Would the cheap path — For low-risk software, compiler diversity, translation validation of critical builds or extensive testing may be cheaper than adopting a verified compiler — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P033, what decision changes, and should the artefact be retired if no live consumer remains?


### P034 — Translation validation per-run evidence

**PROPERTY_ID:** `P034`  
**PROPERTY_NAME:** Translation validation per-run evidence

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Per-run validation is valuable when compiler verification is unavailable or optimization/configuration is variable. It is intended to prevent: A complex or rapidly evolving translator may be too costly to verify globally, yet one wrong translation can invalidate a proof, compiler result or generated model. Global testing cannot guarantee the particular accepted run.

**MATURE_FORM:** Use per-run validation where whole-translator proof is uneconomic. The accepted artefact includes source/target hashes, options, preserved observation, validation result and independent certificate/checker; bypasses and downstream stages are explicit.

**TRIGGER:** Trigger for consequential generated code/models/verification conditions where producer verification is unavailable or stale.

**CHEAP_PATH:** For simple deterministic generators, exhaustive/differential tests or direct proof may be cheaper.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Translation validation per-run evidence",
  "ENGINEERING_CLAIM": "Per-run validation is valuable when compiler verification is unavailable or optimization/configuration is variable.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying translation validation per-run evidence; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The source statement/program is separately validated.",
  "ENVIRONMENT_MODEL": "Runtime/platform assumptions are compatible across source/target semantics.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide translation validation per-run evidence; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Validator checks only a weakened equivalence or selected outputs.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which for each translation, generate a relation or certificate showing source and target semantic correspondence; check it independently; bind source/target/options/version; reject or fall back if validation fails.",
  "SAFETY_LIVENESS_CLASS": "verified toolchain",
  "ABSTRACTION": "Validation relation preserves all properties claimed downstream.",
  "IMPLEMENTATION_CORRESPONDENCE": "Every downstream transformation after validation is covered or trusted.",
  "CHEAP_PATH": "For simple deterministic generators, exhaustive/differential tests or direct proof may be cheaper.",
  "MATURE_FORM": "Use per-run validation where whole-translator proof is uneconomic. The accepted artefact includes source/target hashes, options, preserved observation, validation result and independent certificate/checker; bypasses and downstream stages are explicit.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P034; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to translation validation per-run evidence.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in A complex or rapidly evolving translator may be too costly to verify globally, yet one wrong translation can invalidate a proof, compiler result or generated model. Global testing cannot guarantee the particular accepted run..",
  "RELATION": "Every downstream transformation after validation is covered or trusted.",
  "SOUNDNESS_DUTY": "Validation relation preserves all properties claimed downstream.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Per-run validation may be incomplete or expensive for optimised transformations.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Use per-run validation where whole-translator proof is uneconomic. The accepted artefact includes source/target hashes, options, preserved observation, validation result and independent certificate/checker; bypasses and downstream stages are explicit.",
  "KNOWN_GAP": "Validator checks only a weakened equivalence or selected outputs."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for translation validation per-run evidence.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For simple deterministic generators, exhaustive/differential tests or direct proof may be cheaper."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Translation validation per-run evidence may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger for consequential generated code/models/verification conditions where producer verification is unavailable or stale.",
  "CHEAPER_EVIDENCE": "For simple deterministic generators, exhaustive/differential tests or direct proof may be cheaper."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P034.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Every downstream transformation after validation is covered or trusted.",
  "ENVIRONMENT_BOUNDARY": "Runtime/platform assumptions are compatible across source/target semantics.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Validator/checker, semantic models and parser are bounded; ideally proof certificate is independently checked.",
  "DRIFT_DETECTOR": "Validation is per run; cached results cannot cross changed source, target, options or tool versions.",
  "KNOWN_ESCAPE": "Validator checks only a weakened equivalence or selected outputs."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter translation validation per-run evidence.",
  "IDENTITIES_TO_BIND": "Validation is per run; cached results cannot cross changed source, target, options or tool versions.",
  "REPLAY_OR_RECHECK": "Validator/checker, semantic models and parser are bounded; ideally proof certificate is independently checked.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: For each translation, generate a relation or certificate showing source and target semantic correspondence; check it independently; bind source/target/options/version; reject or fall back if validation fails. Select the observation/property preserved rather than assuming full equivalence.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should chains of partial validators compose into end-to-end evidence?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The source statement/program is separately validated.
- Abstraction: Validation relation preserves all properties claimed downstream.
- Environment: Runtime/platform assumptions are compatible across source/target semantics.
- Model/code correspondence: Every downstream transformation after validation is covered or trusted.
- Trusted tools: Validator/checker, semantic models and parser are bounded; ideally proof certificate is independently checked.
- Currentness/replay: Validation is per run; cached results cannot cross changed source, target, options or tool versions.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Pnueli–Siegel–Singerman and current certifying-verifier work provide direct lineage. | S023, S098 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_PRESERVED_RELATION | Per-run equivalence/simulation proof is rigorous for covered transformations and semantics. | S023, S098 |
| MECHANICAL_REPLAY_STRENGTH | VERY_HIGH | Per-run certificate checking is explicitly replayable. | S098 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | HIGH_FOR_TRANSLATION_STEP | Strong source-target binding for that step; end-to-end chain still requires provenance. | S098 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_COMPILERS_AND_VERIFIERS | Translation validation has substantial research and growing practical tooling evidence. | S023, S098 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Case evaluations support feasibility; independent comparative defect/ROI evidence is limited. | S098 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_FOR_TOOL_QUALIFICATION_ALTERNATIVES | Per-run evidence can reduce tool trust but certification acceptance is context-specific. | S051, S052 |
| TRANSFERABILITY_STRENGTH | HIGH_AS_A_PATTERN | Transfers to compilers, generators and verifier translations when semantics are available. | S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Validator coverage, semantics, independence and downstream stages determine scope. | S098 |
| CONTRARY_EVIDENCE_STRENGTH | MEDIUM_HIGH | TCB and translation-risk evidence strongly motivates validation; evidence does not show universal cost-effectiveness. | S094, S098 |

**CRITICISMS:**
- Per-run validation may be incomplete or expensive for optimised transformations.
- A validator becomes another trusted tool unless it emits a checkable certificate.
- Equivalence under one semantics does not establish deployment environment or provenance.
- Validation can encourage neglect of systematic translator defects if only outputs are checked.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Use per-run validation where whole-translator proof is uneconomic. The accepted artefact includes source/target hashes, options, preserved observation, validation result and independent certificate/checker; bypasses and downstream stages are explicit.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P033 — Verified compiler/toolchain scope, P035 — Proof-carrying/certificate evidence. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P034 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while validator checks only a weakened equivalence or selected outputs?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P034?
- Would the cheap path — For simple deterministic generators, exhaustive/differential tests or direct proof may be cheaper — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P034, what decision changes, and should the artefact be retired if no live consumer remains?


### P035 — Proof-carrying/certificate evidence

**PROPERTY_ID:** `P035`  
**PROPERTY_NAME:** Proof-carrying/certificate evidence

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Certificates should be small, consumer-checkable and bound to exact artefact/policy. It is intended to prevent: Consumers cannot feasibly trust every producer, compiler, solver or remote service. They need compact evidence that an exact artefact satisfies a local policy, checked without rerunning expensive search.

**MATURE_FORM:** Accept an artefact only when a bounded checker verifies a certificate for the exact consumer policy, artefact identity, assumptions and version. Unsupported certificate gaps and environment obligations are explicit; stale certificates are automatically rejected.

**TRIGGER:** Trigger when artefacts cross trust boundaries or expensive verification must be consumed repeatedly by independent parties.

**CHEAP_PATH:** For one local build under one trusted team, direct replay may be simpler than packaging a portable certificate.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Proof-carrying/certificate evidence",
  "ENGINEERING_CLAIM": "Certificates should be small, consumer-checkable and bound to exact artefact/policy.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying proof-carrying/certificate evidence; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Policy is validated against consumer failure modes and not merely easy to prove.",
  "ENVIRONMENT_MODEL": "Runtime assumptions remain separately discharged or encoded in policy where possible.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide proof-carrying/certificate evidence; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Certificate proves a weak policy unrelated to consumer risk.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which define consumer policy; bind certificate to artefact hash and assumptions; use a small checker; reject malformed/stale certificates; include provenance and version; regenerate after change.",
  "SAFETY_LIVENESS_CLASS": "verified toolchain",
  "ABSTRACTION": "Certificate semantics cover relevant transformation/abstraction steps.",
  "IMPLEMENTATION_CORRESPONDENCE": "Certificate cryptographically/semantically binds exact code/binary/configuration.",
  "CHEAP_PATH": "For one local build under one trusted team, direct replay may be simpler than packaging a portable certificate.",
  "MATURE_FORM": "Accept an artefact only when a bounded checker verifies a certificate for the exact consumer policy, artefact identity, assumptions and version. Unsupported certificate gaps and environment obligations are explicit; stale certificates are automatically rejected.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P035; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Proof-carrying/certificate evidence governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Certificate semantics cover relevant transformation/abstraction steps.",
  "ESCALATION_TRIGGER": "Trigger when artefacts cross trust boundaries or expensive verification must be consumed repeatedly by independent parties.",
  "CHEAP_PATH": "For one local build under one trusted team, direct replay may be simpler than packaging a portable certificate."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for proof-carrying/certificate evidence.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For one local build under one trusted team, direct replay may be simpler than packaging a portable certificate."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "Certificates should be small, consumer-checkable and bound to exact artefact/policy.",
  "ASSUMPTIONS_AND_AXIOMS": "Consumer policy, certificate format/checker, artefact identity/provenance and revocation/currentness rules.",
  "CHECKER_OR_KERNEL_BOUNDARY": "Checker, parser, policy semantics, cryptographic hash and logic kernel are bounded.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for proof-carrying/certificate evidence.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Any artefact, policy, assumption or checker change invalidates/requires regeneration.",
  "CORRESPONDENCE_DUTY": "Certificate cryptographically/semantically binds exact code/binary/configuration.",
  "MISUSE_TO_PREVENT": "Proof-carrying evidence shifts specification responsibility to the consumer; a bad policy is still bad."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P035.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Certificate cryptographically/semantically binds exact code/binary/configuration.",
  "ENVIRONMENT_BOUNDARY": "Runtime assumptions remain separately discharged or encoded in policy where possible.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Checker, parser, policy semantics, cryptographic hash and logic kernel are bounded.",
  "DRIFT_DETECTOR": "Any artefact, policy, assumption or checker change invalidates/requires regeneration.",
  "KNOWN_ESCAPE": "Certificate proves a weak policy unrelated to consumer risk."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter proof-carrying/certificate evidence.",
  "IDENTITIES_TO_BIND": "Any artefact, policy, assumption or checker change invalidates/requires regeneration.",
  "REPLAY_OR_RECHECK": "Checker, parser, policy semantics, cryptographic hash and logic kernel are bounded.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Define consumer policy; bind certificate to artefact hash and assumptions; use a small checker; reject malformed/stale certificates; include provenance and version; regenerate after change. Separate certificate validity from policy adequacy and environment assumptions.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should certificate revocation and dynamic configuration be handled?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Policy is validated against consumer failure modes and not merely easy to prove.
- Abstraction: Certificate semantics cover relevant transformation/abstraction steps.
- Environment: Runtime assumptions remain separately discharged or encoded in policy where possible.
- Model/code correspondence: Certificate cryptographically/semantically binds exact code/binary/configuration.
- Trusted tools: Checker, parser, policy semantics, cryptographic hash and logic kernel are bounded.
- Currentness/replay: Any artefact, policy, assumption or checker change invalidates/requires regeneration.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Proof-carrying code and translation/certificate lineages are direct. | S022, S023 |
| FORMAL_SOUNDNESS_STRENGTH | VERY_HIGH_FOR_POLICY | A valid certificate gives strong evidence for the exact formal policy under checker semantics. | S022 |
| MECHANICAL_REPLAY_STRENGTH | VERY_HIGH | Cheap independent replay is the mechanism. | S022, S108 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | HIGH_WITH_STRONG_BINDING | Artefact-hash binding can be strong, but runtime environment remains external. | S022 |
| INDUSTRIAL_CASE_STRENGTH | MEDIUM_HIGH | PCC influenced verified toolchains; broad production evidence is less extensive than theorem-prover use. | S022, S098 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Feasibility studies exist; comparative adoption/operational evidence is limited. | S108, S109 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM_HIGH | Portable checkable evidence aligns with high-assurance goals but certification treatment is domain-specific. | S052 |
| TRANSFERABILITY_STRENGTH | CONTEXT_DEPENDENT | Strong across trust boundaries, unnecessary overhead in many local contexts. | S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Policy adequacy, binding, checker coverage and revocation determine value. | S108, S109 |
| CONTRARY_EVIDENCE_STRENGTH | MEDIUM_HIGH | Certificate-coverage and TCB criticism directly narrows claims; no broad evidence rejects the pattern. | S094, S109 |

**CRITICISMS:**
- Proof-carrying evidence shifts specification responsibility to the consumer; a bad policy is still bad.
- Small checkers and formats remain trusted.
- Certificates do not prove provenance of external inputs or runtime environment.
- Practical certificate coverage for SMT/theory preprocessing remains incomplete [S108, S109].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Accept an artefact only when a bounded checker verifies a certificate for the exact consumer policy, artefact identity, assumptions and version. Unsupported certificate gaps and environment obligations are explicit; stale certificates are automatically rejected.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P022 — Trusted kernel/certificate boundary, P034 — Translation validation per-run evidence. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P035 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while certificate proves a weak policy unrelated to consumer risk?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P035?
- Would the cheap path — For one local build under one trusted team, direct replay may be simpler than packaging a portable certificate — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P035, what decision changes, and should the artefact be retired if no live consumer remains?


### P036 — Hybrid proof + testing/fuzzing/runtime evidence

**PROPERTY_ID:** `P036`  
**PROPERTY_NAME:** Hybrid proof + testing/fuzzing/runtime evidence

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Formal proof should be combined with tests, fuzzing, conformance and runtime evidence where assumptions/environment/integration are empirical. It is intended to prevent: Proof is exhaustive only over its formal model, while testing observes the real implementation/environment but samples behaviours. Relying on either alone leaves distinct defects: wrong specification/model versus untested rare paths.

**MATURE_FORM:** For each material claim, identify what proof establishes and what remains uncertain; assign testing, fuzzing, review or monitoring to those residuals. Independent evidence must have a distinct oracle/model where possible. Remove layers that do not change the decision.

**TRIGGER:** Trigger when a consequential claim spans formal model and real implementation/environment, or any major trusted/unverified boundary remains.

**CHEAP_PATH:** For a simple deterministic transformation exhaustively tested over its finite domain, a proof layer may add little; for a pure theorem, physical testing may be irrelevant.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Hybrid proof + testing/fuzzing/runtime evidence",
  "ENGINEERING_CLAIM": "Formal proof should be combined with tests, fuzzing, conformance and runtime evidence where assumptions/environment/integration are empirical.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying hybrid proof + testing/fuzzing/runtime evidence; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Tests include requirement/specification challenge, not only conformance to the same formula.",
  "ENVIRONMENT_MODEL": "Fault injection, performance, hardware and operational tests cover unproved assumptions.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide hybrid proof + testing/fuzzing/runtime evidence; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Testing merely repeats examples already encoded in the proof.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which build an evidence stack: prove or model-check critical invariants/refinements; test specification assumptions and model-code correspondence; use property/model-based test generation, fuzzing and differential testing; monitor deployment; mutation-test both tests and specifications; focus independent evidence on the tcb.",
  "SAFETY_LIVENESS_CLASS": "strongly retained",
  "ABSTRACTION": "Concrete tests target details omitted by abstraction and spurious counterexamples are classified.",
  "IMPLEMENTATION_CORRESPONDENCE": "Conformance/differential tests directly connect model predictions to implementation traces.",
  "CHEAP_PATH": "For a simple deterministic transformation exhaustively tested over its finite domain, a proof layer may add little; for a pure theorem, physical testing may be irrelevant.",
  "MATURE_FORM": "For each material claim, identify what proof establishes and what remains uncertain; assign testing, fuzzing, review or monitoring to those residuals. Independent evidence must have a distinct oracle/model where possible. Remove layers that do not change the decision.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P036; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to hybrid proof + testing/fuzzing/runtime evidence.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Proof is exhaustive only over its formal model, while testing observes the real implementation/environment but samples behaviours. Relying on either alone leaves distinct defects: wrong specification/model versus untested rare paths..",
  "RELATION": "Conformance/differential tests directly connect model predictions to implementation traces.",
  "SOUNDNESS_DUTY": "Concrete tests target details omitted by abstraction and spurious counterexamples are classified.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "“More evidence” can become unbounded ceremony unless each layer addresses a distinct failure mode.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "For each material claim, identify what proof establishes and what remains uncertain; assign testing, fuzzing, review or monitoring to those residuals. Independent evidence must have a distinct oracle/model where possible. Remove layers that do not change the decision.",
  "KNOWN_GAP": "Testing merely repeats examples already encoded in the proof."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for hybrid proof + testing/fuzzing/runtime evidence.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For a simple deterministic transformation exhaustively tested over its finite domain, a proof layer may add little; for a pure theorem, physical testing may be irrelevant."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Hybrid proof + testing/fuzzing/runtime evidence may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger when a consequential claim spans formal model and real implementation/environment, or any major trusted/unverified boundary remains.",
  "CHEAPER_EVIDENCE": "For a simple deterministic transformation exhaustively tested over its finite domain, a proof layer may add little; for a pure theorem, physical testing may be irrelevant."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P036.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Conformance/differential tests directly connect model predictions to implementation traces.",
  "ENVIRONMENT_BOUNDARY": "Fault injection, performance, hardware and operational tests cover unproved assumptions.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Testing/fuzzing also exercises proof toolchain, compiler and checker where practical.",
  "DRIFT_DETECTOR": "Proofs and complementary tests rerun together after relevant change; evidence versions are linked.",
  "KNOWN_ESCAPE": "Testing merely repeats examples already encoded in the proof."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter hybrid proof + testing/fuzzing/runtime evidence.",
  "IDENTITIES_TO_BIND": "Proofs and complementary tests rerun together after relevant change; evidence versions are linked.",
  "REPLAY_OR_RECHECK": "Testing/fuzzing also exercises proof toolchain, compiler and checker where practical.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Build an evidence stack: prove or model-check critical invariants/refinements; test specification assumptions and model-code correspondence; use property/model-based test generation, fuzzing and differential testing; monitor deployment; mutation-test both tests and specifications; focus independent evidence on the TCB.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should conflicting formal and empirical evidence be adjudicated without automatically privileging either?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Tests include requirement/specification challenge, not only conformance to the same formula.
- Abstraction: Concrete tests target details omitted by abstraction and spurious counterexamples are classified.
- Environment: Fault injection, performance, hardware and operational tests cover unproved assumptions.
- Model/code correspondence: Conformance/differential tests directly connect model predictions to implementation traces.
- Trusted tools: Testing/fuzzing also exercises proof toolchain, compiler and checker where practical.
- Currentness/replay: Proofs and complementary tests rerun together after relevant change; evidence versions are linked.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Symbolic execution, assurance guidance and verified-system practice provide direct hybrid lineage. | S034, S052, S054, S093 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_AS_COMPLEMENT | Formal and empirical evidence remain individually scoped; combination improves coverage when failure modes are distinct. | S052, S100 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Proofs and automated tests/fuzzers are replayable; field/environment evidence may vary. | S034 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | HIGHER_THAN_PROOF_ALONE | Conformance and binary/runtime tests directly strengthen correspondence, though not universally. | S092, S100 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | Aviation cases, verified systems and industrial practice support hybrid stacks. | S054, S065, S093 |
| EMPIRICAL_COMPARATIVE_STRENGTH | HIGH | Practitioner interviews and empirical defects directly support complementary roles. | S092, S100 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | VERY_HIGH | Certification frameworks explicitly retain testing/lifecycle evidence alongside formal methods. | S051, S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH | The principle transfers broadly, with evidence intensity proportional to risk. | S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Independence, oracle diversity and residual-boundary targeting determine added value. | S100 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Empirical specification/integration defects directly refute proof-eliminates-testing. | S092, S100 |

**CRITICISMS:**
- “More evidence” can become unbounded ceremony unless each layer addresses a distinct failure mode.
- Independence is difficult when tests are generated from the same model.
- Empirical evidence and formal proof may conflict because they speak about different artefact levels.
- Verification practitioners explicitly report tests/review catching specification errors [S100].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—For each material claim, identify what proof establishes and what remains uncertain; assign testing, fuzzing, review or monitoring to those residuals. Independent evidence must have a distinct oracle/model where possible. Remove layers that do not change the decision.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P043 — Prove everything, P044 — Proof eliminates testing. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P036 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while testing merely repeats examples already encoded in the proof?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P036?
- Would the cheap path — For a simple deterministic transformation exhaustively tested over its finite domain, a proof layer may add little; for a pure theorem, physical testing may be irrelevant — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P036, what decision changes, and should the artefact be retired if no live consumer remains?


### P037 — Lightweight proportional formalisation

**PROPERTY_ID:** `P037`  
**PROPERTY_NAME:** Lightweight proportional formalisation

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Use the cheapest formal representation that removes a material failure class and has a live consumer. It is intended to prevent: Full formalisation can cost more than the risk, arrive after design decisions, or create maintenance burdens. The alternative need not be no formal method: a small model or invariant may eliminate the dominant failure class cheaply.

**MATURE_FORM:** Formalise only the material claim and choose the cheapest sound representation that can remove its failure class. State bounds and non-covered claims; bind artefact to a consumer and lifecycle; escalate to deeper proof only when residual risk justifies it.

**TRIGGER:** Trigger when a recurring/high-cost failure can be isolated into a small checkable property and full proof is disproportionate.

**CHEAP_PATH:** Do not formalise low-risk one-off prose merely because a tool is available; ordinary review/test may be sufficient.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Lightweight proportional formalisation",
  "ENGINEERING_CLAIM": "Use the cheapest formal representation that removes a material failure class and has a live consumer.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying lightweight proportional formalisation; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The focused property still represents the material failure and its scope is disclosed.",
  "ENVIRONMENT_MODEL": "Do not select a local property when the dominant uncertainty lies in environment/integration.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide lightweight proportional formalisation; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: “Lightweight” becomes unprincipled under-specification.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which rank failure classes and claims by consequence, recurrence, ambiguity and tractability; choose the least expensive formal artefact that discriminates the failure—truth table, assertion, contract, finite model, focused proof or validated translation.",
  "SAFETY_LIVENESS_CLASS": "retained in evolved form",
  "ABSTRACTION": "Simplification is sound for the selected claim or labelled bounded/bug-finding.",
  "IMPLEMENTATION_CORRESPONDENCE": "Use executable checks/conformance where cheap; otherwise label design-only value.",
  "CHEAP_PATH": "Do not formalise low-risk one-off prose merely because a tool is available; ordinary review/test may be sufficient.",
  "MATURE_FORM": "Formalise only the material claim and choose the cheapest sound representation that can remove its failure class. State bounds and non-covered claims; bind artefact to a consumer and lifecycle; escalate to deeper proof only when residual risk justifies it.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P037; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to lightweight proportional formalisation.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Full formalisation can cost more than the risk, arrive after design decisions, or create maintenance burdens. The alternative need not be no formal method: a small model or invariant may eliminate the dominant failure class cheaply..",
  "RELATION": "Use executable checks/conformance where cheap; otherwise label design-only value.",
  "SOUNDNESS_DUTY": "Simplification is sound for the selected claim or labelled bounded/bug-finding.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Lightweight methods still require sound scope and specification discipline; incomplete does not mean unsound.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Formalise only the material claim and choose the cheapest sound representation that can remove its failure class. State bounds and non-covered claims; bind artefact to a consumer and lifecycle; escalate to deeper proof only when residual risk justifies it.",
  "KNOWN_GAP": "“Lightweight” becomes unprincipled under-specification."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Use the cheapest formal representation that removes a material failure class and has a live consumer.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for lightweight proportional formalisation.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Simplification is sound for the selected claim or labelled bounded/bug-finding.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against “Lightweight” becomes unprincipled under-specification..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Captures much of formal reasoning’s defect-prevention value earlier and at lower cost, increases adoption and avoids proving low-value system detail."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Lightweight proportional formalisation may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger when a recurring/high-cost failure can be isolated into a small checkable property and full proof is disproportionate.",
  "CHEAPER_EVIDENCE": "Do not formalise low-risk one-off prose merely because a tool is available; ordinary review/test may be sufficient."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P037.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Use executable checks/conformance where cheap; otherwise label design-only value.",
  "ENVIRONMENT_BOUNDARY": "Do not select a local property when the dominant uncertainty lies in environment/integration.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Prefer simple transparent checkers unless deeper automation’s payoff justifies trust cost.",
  "DRIFT_DETECTOR": "Low-cost artefacts remain live/replayed or are retired; no decorative formal documents.",
  "KNOWN_ESCAPE": "“Lightweight” becomes unprincipled under-specification."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter lightweight proportional formalisation.",
  "IDENTITIES_TO_BIND": "Low-cost artefacts remain live/replayed or are retired; no decorative formal documents.",
  "REPLAY_OR_RECHECK": "Prefer simple transparent checkers unless deeper automation’s payoff justifies trust cost.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Rank failure classes and claims by consequence, recurrence, ambiguity and tractability; choose the least expensive formal artefact that discriminates the failure—truth table, assertion, contract, finite model, focused proof or validated translation. Stop when marginal assurance no longer changes a decision.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "What maintenance-adjusted comparisons are possible across assertions, models, proofs and tests?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The focused property still represents the material failure and its scope is disclosed.
- Abstraction: Simplification is sound for the selected claim or labelled bounded/bug-finding.
- Environment: Do not select a local property when the dominant uncertainty lies in environment/integration.
- Model/code correspondence: Use executable checks/conformance where cheap; otherwise label design-only value.
- Trusted tools: Prefer simple transparent checkers unless deeper automation’s payoff justifies trust cost.
- Currentness/replay: Low-cost artefacts remain live/replayed or are retired; no decorative formal documents.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Lightweight formal methods and Alloy provide direct lineage. | S015, S016 |
| FORMAL_SOUNDNESS_STRENGTH | VARIABLE_BY_METHOD | Formal soundness ranges from exact invariant/proof to bounded bug finding; mature use discloses which. | S015, S016 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Small artefacts are generally cheap to replay. | S016, S107 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | VARIABLE | Executable assertions/contracts can bind strongly; abstract design models less so. | S015 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_BUT_HETEROGENEOUS | Industrial surveys and focused cases support selective use across domains. | S062, S065 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Unit-proof and practitioner studies add empirical support, but universal ROI evidence is absent. | S100, S107, S112 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_AS_PROPORTIONAL_USE | Guidance supports method selection/proportional evidence rather than maximal proof. | S052, S053 |
| TRANSFERABILITY_STRENGTH | HIGH | The selection principle is broadly transferable. | S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Risk selection, bounds, environment and maintenance determine payoff. | S107, S112 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Cost/adoption studies and boundedness criticism prevent “lightweight equals automatically mature”. | S064, S107, S112 |

**CRITICISMS:**
- Lightweight methods still require sound scope and specification discipline; incomplete does not mean unsound.
- Selection can be biased toward tractable rather than important claims.
- Evidence on ROI is heterogeneous and often case-based [S062–S065, S107].
- A cheap check is wasteful if no consumer or recurring failure class exists.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Formalise only the material claim and choose the cheapest sound representation that can remove its failure class. State bounds and non-covered claims; bind artefact to a consumer and lifecycle; escalate to deeper proof only when residual risk justifies it.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P042 — Cost/payoff trigger discipline, P043 — Prove everything. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P037 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while “lightweight” becomes unprincipled under-specification?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P037?
- Would the cheap path — Do not formalise low-risk one-off prose merely because a tool is available; ordinary review/test may be sufficient — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P037, what decision changes, and should the artefact be retired if no live consumer remains?


### P038 — Ceremony/proxy rejection

**PROPERTY_ID:** `P038`  
**PROPERTY_NAME:** Ceremony/proxy rejection

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Notation, proof count, line count, certification paperwork or green tool status are not transferable assurance properties. It is intended to prevent: Organisations substitute visible proxies—formal notation pages, proof lines, theorem counts, zero warnings, certified tool brands or “formally verified” labels—for evidence that a material failure class is controlled.

**MATURE_FORM:** A notation, tool or certification practice is retained only when it produces a checkable claim, witness, correspondence link or current decision. Metrics describe effort/coverage, never substitute for specification strength or real-world assurance.

**TRIGGER:** Trigger when adoption or acceptance is justified primarily by labels, counts, document volume, tool pedigree or certification status.

**CHEAP_PATH:** Do not attack simple documentation/replay records that directly enable evidence consumption; ceremony stripping is not minimalism for its own sake.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Ceremony/proxy rejection",
  "ENGINEERING_CLAIM": "Notation, proof count, line count, certification paperwork or green tool status are not transferable assurance properties.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying ceremony/proxy rejection; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Metrics cannot replace claim validation or strength checks.",
  "ENVIRONMENT_MODEL": "Certification or process completion is not treated as environment conformance.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide ceremony/proxy rejection; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Proof count rises by splitting trivial lemmas.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which for every formal artefact identify claim, failure mode, consumer, assumptions, correspondence and decision changed.",
  "SAFETY_LIVENESS_CLASS": "ceremony not general",
  "ABSTRACTION": "Tool/notation identity is not treated as evidence of abstraction adequacy.",
  "IMPLEMENTATION_CORRESPONDENCE": "“Verified” labels state actual artefact/correspondence level.",
  "CHEAP_PATH": "Do not attack simple documentation/replay records that directly enable evidence consumption; ceremony stripping is not minimalism for its own sake.",
  "MATURE_FORM": "A notation, tool or certification practice is retained only when it produces a checkable claim, witness, correspondence link or current decision. Metrics describe effort/coverage, never substitute for specification strength or real-world assurance.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P038; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Ceremony/proxy rejection governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Tool/notation identity is not treated as evidence of abstraction adequacy.",
  "ESCALATION_TRIGGER": "Trigger when adoption or acceptance is justified primarily by labels, counts, document volume, tool pedigree or certification status.",
  "CHEAP_PATH": "Do not attack simple documentation/replay records that directly enable evidence consumption; ceremony stripping is not minimalism for its own sake."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for ceremony/proxy rejection.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "Do not attack simple documentation/replay records that directly enable evidence consumption; ceremony stripping is not minimalism for its own sake."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Ceremony/proxy rejection may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger when adoption or acceptance is justified primarily by labels, counts, document volume, tool pedigree or certification status.",
  "CHEAPER_EVIDENCE": "Do not attack simple documentation/replay records that directly enable evidence consumption; ceremony stripping is not minimalism for its own sake."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P038.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "“Verified” labels state actual artefact/correspondence level.",
  "ENVIRONMENT_BOUNDARY": "Certification or process completion is not treated as environment conformance.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Tool pedigree supplements, not replaces, bounded trust evidence.",
  "DRIFT_DETECTOR": "Stale formal artefacts lose status even if historical counts remain.",
  "KNOWN_ESCAPE": "Proof count rises by splitting trivial lemmas."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter ceremony/proxy rejection.",
  "IDENTITIES_TO_BIND": "Stale formal artefacts lose status even if historical counts remain.",
  "REPLAY_OR_RECHECK": "Tool pedigree supplements, not replaces, bounded trust evidence.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: For every formal artefact identify claim, failure mode, consumer, assumptions, correspondence and decision changed. Reject metrics that increase without strengthening those links; audit counterfactuals (could the proxy rise while assurance falls?); retire artefacts with no live consumer.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "Where does necessary certification traceability end and bureaucratic duplication begin?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Metrics cannot replace claim validation or strength checks.
- Abstraction: Tool/notation identity is not treated as evidence of abstraction adequacy.
- Environment: Certification or process completion is not treated as environment conformance.
- Model/code correspondence: “Verified” labels state actual artefact/correspondence level.
- Trusted tools: Tool pedigree supplements, not replaces, bounded trust evidence.
- Currentness/replay: Stale formal artefacts lose status even if historical counts remain.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Direct critical lineage from DeMillo, Hall, Bowen/Hinchey and industry surveys. | S055, S057, S058, S062 |
| FORMAL_SOUNDNESS_STRENGTH | NOT_A_FORMAL_THEOREM | The property is governance/engineering causality, not a logical soundness result. | S055 |
| MECHANICAL_REPLAY_STRENGTH | MEDIUM | Replay can expose whether artefacts are live, but cannot alone detect proxy selection/gaming. | S095 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | HIGH_RELEVANCE | Explicit correspondence levels directly counter branding, although governance must enforce them. | S092 |
| INDUSTRIAL_CASE_STRENGTH | HIGH | Industry surveys document heterogeneous adoption and barriers inconsistent with universal proxy claims. | S063, S064, S065, S112 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Professional/qualitative evidence is substantial; controlled proxy-gaming studies are sparse. | S064, S100 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_AS_A_LIMIT | Certification sources themselves distinguish objectives/tool credit from whole-system truth. | S051, S052 |
| TRANSFERABILITY_STRENGTH | HIGH | Anti-proxy reasoning transfers across all formal techniques. | S065 |
| ASSUMPTION_SENSITIVITY | MEDIUM_HIGH | Organisational incentives and consumer use determine gaming risk. | S112 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Historical criticism and modern empirical evidence strongly oppose ceremony-as-property. | S055, S057, S112 |

**CRITICISMS:**
- Some process/formality is necessary for reproducibility, review and certification; stripping ceremony cannot mean stripping evidence.
- Quantitative proxies can aid capacity planning if not treated as assurance outcomes.
- Public communication needs concise labels, creating unavoidable compression risk.
- Evidence of proxy gaming is often qualitative rather than experimentally quantified.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A notation, tool or certification practice is retained only when it produces a checkable claim, witness, correspondence link or current decision. Metrics describe effort/coverage, never substitute for specification strength or real-world assurance.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P041 — Certification/formality ceremony boundary, P039 — Specification gaming and golden theorem drift. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P038 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while proof count rises by splitting trivial lemmas?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P038?
- Would the cheap path — Do not attack simple documentation/replay records that directly enable evidence consumption; ceremony stripping is not minimalism for its own sake — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P038, what decision changes, and should the artefact be retired if no live consumer remains?


### P039 — Specification gaming and golden theorem drift

**PROPERTY_ID:** `P039`  
**PROPERTY_NAME:** Specification gaming and golden theorem drift

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Changes to the theorem/specification after failures require review as possible legitimate revision or proof gaming. It is intended to prevent: A team can make verification green by weakening the property, strengthening assumptions, disabling behaviour or changing the expected theorem after observing failure. Some revisions are legitimate corrections; others destroy the original acceptance meaning.

**MATURE_FORM:** Every material statement/assumption change is traceable to an engineering rationale, reviewed against original failure modes and old counterexamples, and classified as correction, scope change or weakening. Green status cannot erase prior evidence.

**TRIGGER:** Trigger after proof/model failure, assumption changes, repeated theorem edits or generated specifications based on known expected outcomes.

**CHEAP_PATH:** For low-risk exploratory models, maintain ordinary version history and rationale rather than a heavy approval board.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Specification gaming and golden theorem drift",
  "ENGINEERING_CLAIM": "Changes to the theorem/specification after failures require review as possible legitimate revision or proof gaming.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying specification gaming and golden theorem drift; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Legitimate correction remains possible but cannot silently reduce accepted behaviour/failure coverage.",
  "ENVIRONMENT_MODEL": "Environment assumptions cannot be strengthened without evidence and scope decision.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide specification gaming and golden theorem drift; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Precondition is strengthened to exclude a discovered defect.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which version and diff engineering claim, formal statement, assumptions and known examples; require rationale/classification for changes; replay old counterexamples; run vacuity/mutation/strength tests; separate legitimate specification correction from product workaround; preserve decision-owner approval.",
  "SAFETY_LIVENESS_CLASS": "useful but easily gamed",
  "ABSTRACTION": "Changes to abstraction bounds/reductions are treated as claim changes where they alter behaviours.",
  "IMPLEMENTATION_CORRESPONDENCE": "Specification changes are reconciled with code/test/runtime expectations rather than changed in isolation.",
  "CHEAP_PATH": "For low-risk exploratory models, maintain ordinary version history and rationale rather than a heavy approval board.",
  "MATURE_FORM": "Every material statement/assumption change is traceable to an engineering rationale, reviewed against original failure modes and old counterexamples, and classified as correction, scope change or weakening. Green status cannot erase prior evidence.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P039; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to specification gaming and golden theorem drift.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in A team can make verification green by weakening the property, strengthening assumptions, disabling behaviour or changing the expected theorem after observing failure. Some revisions are legitimate corrections; others destroy the original acceptance meaning..",
  "RELATION": "Specification changes are reconciled with code/test/runtime expectations rather than changed in isolation.",
  "SOUNDNESS_DUTY": "Changes to abstraction bounds/reductions are treated as claim changes where they alter behaviours.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Not every changed theorem is gaming; formalisation legitimately discovers requirement errors.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Every material statement/assumption change is traceable to an engineering rationale, reviewed against original failure modes and old counterexamples, and classified as correction, scope change or weakening. Green status cannot erase prior evidence.",
  "KNOWN_GAP": "Precondition is strengthened to exclude a discovered defect."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for specification gaming and golden theorem drift.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For low-risk exploratory models, maintain ordinary version history and rationale rather than a heavy approval board."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Specification gaming and golden theorem drift may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger after proof/model failure, assumption changes, repeated theorem edits or generated specifications based on known expected outcomes.",
  "CHEAPER_EVIDENCE": "For low-risk exploratory models, maintain ordinary version history and rationale rather than a heavy approval board."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P039.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Specification changes are reconciled with code/test/runtime expectations rather than changed in isolation.",
  "ENVIRONMENT_BOUNDARY": "Environment assumptions cannot be strengthened without evidence and scope decision.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Generated diffs/strength analyses are advisory and replayable.",
  "DRIFT_DETECTOR": "Old witnesses and regression properties remain executable after legitimate revisions where applicable.",
  "KNOWN_ESCAPE": "Precondition is strengthened to exclude a discovered defect."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter specification gaming and golden theorem drift.",
  "IDENTITIES_TO_BIND": "Old witnesses and regression properties remain executable after legitimate revisions where applicable.",
  "REPLAY_OR_RECHECK": "Generated diffs/strength analyses are advisory and replayable.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Version and diff engineering claim, formal statement, assumptions and known examples; require rationale/classification for changes; replay old counterexamples; run vacuity/mutation/strength tests; separate legitimate specification correction from product workaround; preserve decision-owner approval.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "What benchmark governance best detects theorem leakage and contamination in AI-assisted verification?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Legitimate correction remains possible but cannot silently reduce accepted behaviour/failure coverage.
- Abstraction: Changes to abstraction bounds/reductions are treated as claim changes where they alter behaviours.
- Environment: Environment assumptions cannot be strengthened without evidence and scope decision.
- Model/code correspondence: Specification changes are reconciled with code/test/runtime expectations rather than changed in isolation.
- Trusted tools: Generated diffs/strength analyses are advisory and replayable.
- Currentness/replay: Old witnesses and regression properties remain executable after legitimate revisions where applicable.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | MEDIUM_HIGH | Vacuity and requirements lineages establish the mechanisms; “golden theorem drift” is a convergent governance extension. | S059, S060, S081 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_FORMAL_COMPARISONS | Logical implication/equivalence can compare some versions, but engineering intent is not fully formal. | S060, S102 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Versioned proofs, old counterexamples and mutation runs are replayable. | S095 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM | Code/test reconciliation can strengthen correspondence, but governance is needed. | S100 |
| INDUSTRIAL_CASE_STRENGTH | MEDIUM | Industrial experience recognises specification changes; detailed public gaming cases are sparse. | S100 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Vacuity and AI benchmark/translation evidence support risk; causal incidence estimates are unavailable. | S101, S102, S111 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_AS_CHANGE_CONTROL | Certification/lifecycle guidance requires controlled requirements and evidence changes. | S051, S052 |
| TRANSFERABILITY_STRENGTH | HIGH | Outcome-driven weakening risk transfers across formal techniques. | S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Intent, assumptions, examples and organisational incentives determine whether a revision is legitimate. | S081, S100 |
| CONTRARY_EVIDENCE_STRENGTH | MEDIUM_HIGH | Strong theoretical/benchmark criticism exists, though direct field evidence of deliberate gaming is limited. | S059, S101, S111 |

**CRITICISMS:**
- Not every changed theorem is gaming; formalisation legitimately discovers requirement errors.
- Rigid “golden theorem” control can preserve a wrong specification.
- Intent classification requires governance and domain judgement beyond proof checking.
- Metrics for theorem strength can themselves be gamed.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Every material statement/assumption change is traceable to an engineering rationale, reviewed against original failure modes and old counterexamples, and classified as correction, scope change or weakening. Green status cannot erase prior evidence.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P001 — Precise property before proof, P020 — Vacuity and specification-strength checks. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P039 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while precondition is strengthened to exclude a discovered defect?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P039?
- Would the cheap path — For low-risk exploratory models, maintain ordinary version history and rationale rather than a heavy approval board — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P039, what decision changes, and should the artefact be retired if no live consumer remains?


### P040 — AI-assisted formalisation boundary

**PROPERTY_ID:** `P040`  
**PROPERTY_NAME:** AI-assisted formalisation boundary

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** LLM assistance is useful for search/translation/repair only when the checked statement and translation review are bounded. It is intended to prevent: LLMs can reduce search and translation labour, but may hallucinate statements, exploit benchmark leakage, generate a valid proof of the wrong theorem, use unsafe shortcuts or fail to transfer from curated mathematics to real verification repositories.

**MATURE_FORM:** AI proposes; trusted formal tools check derivations; independent methods validate statement fidelity; humans retain authority over engineering meaning and assumptions. Evaluation uses held-out, repository-realistic tasks and reports search budget, unsafe features, equivalence and transfer—not only type-check pass rate.

**TRIGGER:** Trigger for assistance with formal statement generation, tactic/proof search, invariant/model generation, explanation or proof repair—not as autonomous acceptance authority.

**CHEAP_PATH:** For a small deterministic property, direct human encoding/checking may be cheaper and more trustworthy than an AI translation layer.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "AI-assisted formalisation boundary",
  "ENGINEERING_CLAIM": "LLM assistance is useful for search/translation/repair only when the checked statement and translation review are bounded.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying ai-assisted formalisation boundary; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Generated statement is compared semantically with requirement and challenged by independent examples/equivalence methods.",
  "ENVIRONMENT_MODEL": "AI does not invent environmental assumptions; all are independently sourced/discharged.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide ai-assisted formalisation boundary; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Generated statement type-checks but changes quantifiers, conditions or units.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which use llms as untrusted proposal generators for statements, tactics, invariants, models and repairs.",
  "SAFETY_LIVENESS_CLASS": "context dependent",
  "ABSTRACTION": "Generated models/invariants disclose omitted behaviours and are not accepted solely because checking succeeds.",
  "IMPLEMENTATION_CORRESPONDENCE": "Generated proofs/models bind to exact code/spec versions and correspondence evidence.",
  "CHEAP_PATH": "For a small deterministic property, direct human encoding/checking may be cheaper and more trustworthy than an AI translation layer.",
  "MATURE_FORM": "AI proposes; trusted formal tools check derivations; independent methods validate statement fidelity; humans retain authority over engineering meaning and assumptions. Evaluation uses held-out, repository-realistic tasks and reports search budget, unsafe features, equivalence and transfer—not only type-check pass rate.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P040; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to ai-assisted formalisation boundary.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in LLMs can reduce search and translation labour, but may hallucinate statements, exploit benchmark leakage, generate a valid proof of the wrong theorem, use unsafe shortcuts or fail to transfer from curated mathematics to real verification repositories..",
  "RELATION": "Generated proofs/models bind to exact code/spec versions and correspondence evidence.",
  "SOUNDNESS_DUTY": "Generated models/invariants disclose omitted behaviours and are not accepted solely because checking succeeds.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Kernel checking validates only the generated formal statement.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "AI proposes; trusted formal tools check derivations; independent methods validate statement fidelity; humans retain authority over engineering meaning and assumptions. Evaluation uses held-out, repository-realistic tasks and reports search budget, unsafe features, equivalence and transfer—not only type-check pass rate.",
  "KNOWN_GAP": "Generated statement type-checks but changes quantifiers, conditions or units."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "LLM assistance is useful for search/translation/repair only when the checked statement and translation review are bounded.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for ai-assisted formalisation boundary.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Generated models/invariants disclose omitted behaviours and are not accepted solely because checking succeeds.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Generated statement type-checks but changes quantifiers, conditions or units..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Can lower formalisation/search/repair labour, broaden access and explain counterexamples while retaining kernel-level derivational assurance—provided translation and benchmark controls prevent false confidence."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "LLM assistance is useful for search/translation/repair only when the checked statement and translation review are bounded.",
  "ASSUMPTIONS_AND_AXIOMS": "Trusted checker, prompt/model/version provenance, statement-fidelity validation, contamination-aware evaluation and qualified human reviewer.",
  "CHECKER_OR_KERNEL_BOUNDARY": "LLM is untrusted; kernel, parser, libraries, unsafe commands, retrieval corpus and equivalence checker are bounded.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for ai-assisted formalisation boundary.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Store generated artefacts and replay deterministically; model/prompt/library changes require revalidation and semantic diff.",
  "CORRESPONDENCE_DUTY": "Generated proofs/models bind to exact code/spec versions and correspondence evidence.",
  "MISUSE_TO_PREVENT": "Kernel checking validates only the generated formal statement."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P040.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Generated proofs/models bind to exact code/spec versions and correspondence evidence.",
  "ENVIRONMENT_BOUNDARY": "AI does not invent environmental assumptions; all are independently sourced/discharged.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "LLM is untrusted; kernel, parser, libraries, unsafe commands, retrieval corpus and equivalence checker are bounded.",
  "DRIFT_DETECTOR": "Store generated artefacts and replay deterministically; model/prompt/library changes require revalidation and semantic diff.",
  "KNOWN_ESCAPE": "Generated statement type-checks but changes quantifiers, conditions or units."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter ai-assisted formalisation boundary.",
  "IDENTITIES_TO_BIND": "Store generated artefacts and replay deterministically; model/prompt/library changes require revalidation and semantic diff.",
  "REPLAY_OR_RECHECK": "LLM is untrusted; kernel, parser, libraries, unsafe commands, retrieval corpus and equivalence checker are bounded.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Use LLMs as untrusted proposal generators for statements, tactics, invariants, models and repairs. Require native kernel checking, axiom/unsafe-command audit, independent semantic/roundtrip translation validation, held-out contamination-aware evaluation, code/spec correspondence review and human approval of the engineering claim.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "What human-review interface best exposes hidden assumptions and near-miss translations?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Generated statement is compared semantically with requirement and challenged by independent examples/equivalence methods.
- Abstraction: Generated models/invariants disclose omitted behaviours and are not accepted solely because checking succeeds.
- Environment: AI does not invent environmental assumptions; all are independently sourced/discharged.
- Model/code correspondence: Generated proofs/models bind to exact code/spec versions and correspondence evidence.
- Trusted tools: LLM is untrusted; kernel, parser, libraries, unsafe commands, retrieval corpus and equivalence checker are bounded.
- Currentness/replay: Store generated artefacts and replay deterministically; model/prompt/library changes require revalidation and semantic diff.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | MEDIUM_HIGH | Rapid lineage is documented by surveys, LeanDojo and 2026 benchmarks, but remains young. | S069, S070, S071, S101 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_CHECKED_PROOF_ONLY | Kernel checking is strong for the actual statement; no corresponding strength transfers automatically to translation. | S071, S101 |
| MECHANICAL_REPLAY_STRENGTH | HIGH_FOR_ACCEPTED_ARTEFACT | Generated proof terms/scripts can be replayed; stochastic search process need not be trusted. | S071 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_BY_ITSELF | LLM output supplies no implementation/environment correspondence unless separately built. | S111 |
| INDUSTRIAL_CASE_STRENGTH | LOW_TO_MEDIUM | Current evidence is mainly research benchmarks and early tools, not broad industrial comparative adoption. | S069, S070 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM_HIGH_BUT_FRONTIER | ITPEval, roundtrip studies and repository benchmarks provide direct empirical evidence with important limitations. | S101, S102, S111 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | LOW | No mature general certification practice grants assurance credit merely for LLM assistance. | S052 |
| TRANSFERABILITY_STRENGTH | CONTESTED_AND_TASK_SPECIFIC | Proof-search gains may transfer; statement fidelity and software-verification transfer remain weak. | S101, S111 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Prompt/context, corpus contamination, formalisation semantics, libraries and reviewer competence dominate. | S101, S102, S111 |
| CONTRARY_EVIDENCE_STRENGTH | VERY_HIGH | Current 2026 evidence directly demonstrates type-check/fidelity gaps and incomplete transfer. | S101, S102, S111 |

**CRITICISMS:**
- Kernel checking validates only the generated formal statement.
- ITPEval found native type-checking can substantially overstate cross-prover statement fidelity [S101].
- Roundtrip/equivalence repair improves but does not eliminate semantic drift [S102].
- Benchmarks may be unrepresentative, contaminated or structurally leaked.
- LLM assistance adds model/version/prompt provenance and nondeterminism to proof maintenance.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—AI proposes; trusted formal tools check derivations; independent methods validate statement fidelity; humans retain authority over engineering meaning and assumptions. Evaluation uses held-out, repository-realistic tasks and reports search budget, unsafe features, equivalence and transfer—not only type-check pass rate.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P001 — Precise property before proof, P021 — Mechanical proof replay. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P040 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while generated statement type-checks but changes quantifiers, conditions or units?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P040?
- Would the cheap path — For a small deterministic property, direct human encoding/checking may be cheaper and more trustworthy than an AI translation layer — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P040, what decision changes, and should the artefact be retired if no live consumer remains?


### P041 — Certification/formality ceremony boundary

**PROPERTY_ID:** `P041`  
**PROPERTY_NAME:** Certification/formality ceremony boundary

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Certification recognition of formal methods is evidence-framework participation, not automatic truth of the engineering claim. It is intended to prevent: A formal proof, model-check report or qualified tool can become certification ceremony: an artefact produced to satisfy an objective but detached from the exact product configuration, operational assumptions, live consumer or engineering consequence. Conversely, dismissing certification as mere paperwork ignores its legitimate role in forcing traceability and independent scrutiny.

**MATURE_FORM:** Certification is retained as an independent evidence-governance layer, not as a correctness property. A formal artefact earns credit only for a named objective and exact configuration under declared assumptions; its live engineering status is separately established through correspondence, replay, change impact and residual-risk review.

**TRIGGER:** Trigger when formal evidence is used for regulatory, contractual or independent-assurance credit, or when a reusable verified component carries inherited assurance claims.

**CHEAP_PATH:** For an internal low-risk invariant with no certification consumer, retain ordinary replay, review and change control rather than manufacturing certification-style paperwork.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Certification/formality ceremony boundary",
  "ENGINEERING_CLAIM": "Certification recognition of formal methods is evidence-framework participation, not automatic truth of the engineering claim.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying certification/formality ceremony boundary; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The certified objective and the actual formal claim are identical or explicitly related; compliance wording cannot substitute for a discriminating requirement.",
  "ENVIRONMENT_MODEL": "Operational and installation assumptions are included in the certified usage domain and verified at integration.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide certification/formality ceremony boundary; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: A standard objective is marked complete because a formal-method document exists, without checking the property proved.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which map each formal artefact to the exact assurance objective, claim, configuration item, usage domain, assumptions, tool-credit basis and decision authority it serves.",
  "SAFETY_LIVENESS_CLASS": "useful but easily bureaucratised",
  "ABSTRACTION": "Any abstract model used for credit states coverage, omissions and justification against certification objectives.",
  "IMPLEMENTATION_CORRESPONDENCE": "The certified model/proof is tied to the exact implementation and configuration, or its credit is limited to design evidence.",
  "CHEAP_PATH": "For an internal low-risk invariant with no certification consumer, retain ordinary replay, review and change control rather than manufacturing certification-style paperwork.",
  "MATURE_FORM": "Certification is retained as an independent evidence-governance layer, not as a correctness property. A formal artefact earns credit only for a named objective and exact configuration under declared assumptions; its live engineering status is separately established through correspondence, replay, change impact and residual-risk review.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P041; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to certification/formality ceremony boundary.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in A formal proof, model-check report or qualified tool can become certification ceremony: an artefact produced to satisfy an objective but detached from the exact product configuration, operational assumptions, live consumer or engineering consequence. Conversely, dismissing certification as mere paperwork ignores its legitimate role in forcing traceability and independent scrutiny..",
  "RELATION": "The certified model/proof is tied to the exact implementation and configuration, or its credit is limited to design evidence.",
  "SOUNDNESS_DUTY": "Any abstract model used for credit states coverage, omissions and justification against certification objectives.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Standards establish process and evidentiary obligations, not independent proof that a product meets its mission.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Certification is retained as an independent evidence-governance layer, not as a correctness property. A formal artefact earns credit only for a named objective and exact configuration under declared assumptions; its live engineering status is separately established through correspondence, replay, change impact and residual-risk review.",
  "KNOWN_GAP": "A standard objective is marked complete because a formal-method document exists, without checking the property proved."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for certification/formality ceremony boundary.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For an internal low-risk invariant with no certification consumer, retain ordinary replay, review and change control rather than manufacturing certification-style paperwork."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Certification/formality ceremony boundary may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger when formal evidence is used for regulatory, contractual or independent-assurance credit, or when a reusable verified component carries inherited assurance claims.",
  "CHEAPER_EVIDENCE": "For an internal low-risk invariant with no certification consumer, retain ordinary replay, review and change control rather than manufacturing certification-style paperwork."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P041.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "The certified model/proof is tied to the exact implementation and configuration, or its credit is limited to design evidence.",
  "ENVIRONMENT_BOUNDARY": "Operational and installation assumptions are included in the certified usage domain and verified at integration.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Tool qualification/validation applies to the exact role, version, options and error-detection obligations claimed.",
  "DRIFT_DETECTOR": "Product, requirement, tool, model and environment changes trigger impact analysis and re-establishment or withdrawal of credit.",
  "KNOWN_ESCAPE": "A standard objective is marked complete because a formal-method document exists, without checking the property proved."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter certification/formality ceremony boundary.",
  "IDENTITIES_TO_BIND": "Product, requirement, tool, model and environment changes trigger impact analysis and re-establishment or withdrawal of credit.",
  "REPLAY_OR_RECHECK": "Tool qualification/validation applies to the exact role, version, options and error-detection obligations claimed.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Map each formal artefact to the exact assurance objective, claim, configuration item, usage domain, assumptions, tool-credit basis and decision authority it serves. Require live traceability from requirement to model/proof to implementation evidence; separate compliance status from product-correctness status; record residual obligations that certification does not discharge; re-evaluate credit after change.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should tool qualification evolve for solver-backed, certificate-producing and AI-assisted verification pipelines?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The certified objective and the actual formal claim are identical or explicitly related; compliance wording cannot substitute for a discriminating requirement.
- Abstraction: Any abstract model used for credit states coverage, omissions and justification against certification objectives.
- Environment: Operational and installation assumptions are included in the certified usage domain and verified at integration.
- Model/code correspondence: The certified model/proof is tied to the exact implementation and configuration, or its credit is limited to design evidence.
- Trusted tools: Tool qualification/validation applies to the exact role, version, options and error-detection obligations claimed.
- Currentness/replay: Product, requirement, tool, model and environment changes trigger impact analysis and re-establishment or withdrawal of credit.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | FAA/RTCA/NASA sources directly establish the certification lineage and formal-method supplement obligations. | S051, S052, S053, S054, S113 |
| FORMAL_SOUNDNESS_STRENGTH | CONDITIONAL | Formal soundness belongs to the underlying proof/model method; certification status adds no theorem beyond its stated objectives. | S052, S054 |
| MECHANICAL_REPLAY_STRENGTH | MEDIUM_HIGH_WHERE_REQUIRED | Replayable artefacts strengthen certification evidence, but many lifecycle judgements remain documentary and human. | S052, S054, S095 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM | Standards demand traceability and configuration control, yet actual correspondence depends on programme evidence. | S051, S052, S113 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_REGULATED_DOMAINS | Formal-method credit and reusable-component constraints are established practice in aviation and analogous assurance settings. | S051, S052, S054, S113 |
| EMPIRICAL_COMPARATIVE_STRENGTH | LOW_TO_MEDIUM | Comparative field evidence that isolates certification-formalism effects from broader assurance practice remains sparse. | S063, S064, S112 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | VERY_HIGH | This property is native to certification/domain practice and directly supported by current guidance. | S051, S052, S113 |
| TRANSFERABILITY_STRENGTH | MEDIUM | The anti-ceremony boundary transfers widely; exact certification mechanisms are domain-specific. | S041, S062, S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Credit is sensitive to objective, configuration, usage domain, assumptions and tool role. | S052, S113 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH_AS_LIMIT | Industry studies and standards themselves contradict any inference from compliance completion to whole-system correctness. | S063, S064, S112, S113 |

**CRITICISMS:**
- Standards establish process and evidentiary obligations, not independent proof that a product meets its mission.
- Certification credit can be costly and selective, and public comparative outcome evidence is limited.
- A qualified tool can still be misconfigured or used with an incorrect encoding.
- Document traceability can remain nominal if product identity and operational assumptions are not live.
- Continuous delivery and mutable configurations strain one-time certification models.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Certification is retained as an independent evidence-governance layer, not as a correctness property. A formal artefact earns credit only for a named objective and exact configuration under declared assumptions; its live engineering status is separately established through correspondence, replay, change impact and residual-risk review.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P038 — Ceremony/proxy rejection, P048 — Retirement of stale formal artefacts. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P041 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while a standard objective is marked complete because a formal-method document exists, without checking the property proved?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P041?
- Would the cheap path — For an internal low-risk invariant with no certification consumer, retain ordinary replay, review and change control rather than manufacturing certification-style paperwork — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P041, what decision changes, and should the artefact be retired if no live consumer remains?


### P042 — Cost/payoff trigger discipline

**PROPERTY_ID:** `P042`  
**PROPERTY_NAME:** Cost/payoff trigger discipline

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Formalisation is warranted when proof/checking cost is lower than expected failure/review/rework cost for the claim. It is intended to prevent: Formalisation consumes scarce domain, modelling, proof and maintenance effort. Without a trigger discipline, teams prove what is tractable or prestigious rather than what changes a material decision, or continue deepening proof after a cheaper invariant, finite model or test has already eliminated the relevant failure class.

**MATURE_FORM:** Formalisation is a graduated assurance investment. The selected technique is the least costly one that can soundly discriminate the material failure class at the required scope; escalation, stopping, reuse and retirement are governed by decision value and currentness rather than prestige or proof volume.

**TRIGGER:** Trigger whenever a project considers adding, deepening, maintaining or retiring a formal-method obligation.

**CHEAP_PATH:** When an existing deterministic test or type/checker already fully discriminates the relevant failure class at lower trust and maintenance cost, use it and document why escalation is unnecessary.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Cost/payoff trigger discipline",
  "ENGINEERING_CLAIM": "Formalisation is warranted when proof/checking cost is lower than expected failure/review/rework cost for the claim.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying cost/payoff trigger discipline; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The benefit estimate is tied to a specific claim rather than generic “correctness”.",
  "ENVIRONMENT_MODEL": "External uncertainty that cannot be reduced by proof is not counted as if formalisation removed it.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide cost/payoff trigger discipline; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Formal effort targets easy functions rather than high-consequence uncertainty.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which before choosing a method, define the failure class, consequence, uncertainty, decision consumer, cheapest discriminating check, tractability, expected reuse and maintenance horizon.",
  "SAFETY_LIVENESS_CLASS": "retained in evolved form",
  "ABSTRACTION": "Cost savings from abstraction are balanced against lost correspondence and spurious-result handling.",
  "IMPLEMENTATION_CORRESPONDENCE": "Payoff estimates include the cost of binding the result to implementation and deployment.",
  "CHEAP_PATH": "When an existing deterministic test or type/checker already fully discriminates the relevant failure class at lower trust and maintenance cost, use it and document why escalation is unnecessary.",
  "MATURE_FORM": "Formalisation is a graduated assurance investment. The selected technique is the least costly one that can soundly discriminate the material failure class at the required scope; escalation, stopping, reuse and retirement are governed by decision value and currentness rather than prestige or proof volume.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P042; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Cost/payoff trigger discipline governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Cost savings from abstraction are balanced against lost correspondence and spurious-result handling.",
  "ESCALATION_TRIGGER": "Trigger whenever a project considers adding, deepening, maintaining or retiring a formal-method obligation.",
  "CHEAP_PATH": "When an existing deterministic test or type/checker already fully discriminates the relevant failure class at lower trust and maintenance cost, use it and document why escalation is unnecessary."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for cost/payoff trigger discipline.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "When an existing deterministic test or type/checker already fully discriminates the relevant failure class at lower trust and maintenance cost, use it and document why escalation is unnecessary."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Cost/payoff trigger discipline may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger whenever a project considers adding, deepening, maintaining or retiring a formal-method obligation.",
  "CHEAPER_EVIDENCE": "When an existing deterministic test or type/checker already fully discriminates the relevant failure class at lower trust and maintenance cost, use it and document why escalation is unnecessary."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P042.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Payoff estimates include the cost of binding the result to implementation and deployment.",
  "ENVIRONMENT_BOUNDARY": "External uncertainty that cannot be reduced by proof is not counted as if formalisation removed it.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Automation, solver/certificate and qualification costs are included rather than externalised.",
  "DRIFT_DETECTOR": "Recurring replay, repair, library/tool upgrade and retirement costs are part of the decision.",
  "KNOWN_ESCAPE": "Formal effort targets easy functions rather than high-consequence uncertainty."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter cost/payoff trigger discipline.",
  "IDENTITIES_TO_BIND": "Recurring replay, repair, library/tool upgrade and retirement costs are part of the decision.",
  "REPLAY_OR_RECHECK": "Automation, solver/certificate and qualification costs are included rather than externalised.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Before choosing a method, define the failure class, consequence, uncertainty, decision consumer, cheapest discriminating check, tractability, expected reuse and maintenance horizon. Escalate from executable assertion/test to bounded model, static analysis, model checking or theorem proof only while marginal assurance value exceeds modelling/proof/currentness cost. Record stop and retirement criteria.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "Can organisations predict which small formal models will eliminate recurring failure classes before incurring modelling cost?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The benefit estimate is tied to a specific claim rather than generic “correctness”.
- Abstraction: Cost savings from abstraction are balanced against lost correspondence and spurious-result handling.
- Environment: External uncertainty that cannot be reduced by proof is not counted as if formalisation removed it.
- Model/code correspondence: Payoff estimates include the cost of binding the result to implementation and deployment.
- Trusted tools: Automation, solver/certificate and qualification costs are included rather than externalised.
- Currentness/replay: Recurring replay, repair, library/tool upgrade and retirement costs are part of the decision.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Hall, Bowen/Hinchey and lightweight-formal-methods sources directly establish proportionality as a mature strand. | S015, S057, S058 |
| FORMAL_SOUNDNESS_STRENGTH | NOT_A_SINGLE_FORMAL_THEOREM | Individual method soundness can be formal; cross-method economic optimality is an engineering decision under uncertainty. | S015, S042 |
| MECHANICAL_REPLAY_STRENGTH | MEDIUM | Replay cost is measurable for a chosen artefact, but expected decision value is not mechanically established. | S095, S107 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM | Correspondence cost can be incorporated and tested, but estimates remain project-specific. | S092, S100 |
| INDUSTRIAL_CASE_STRENGTH | MEDIUM_HIGH | Surveys and case studies show selective use and focused successes rather than universal deployment. | S029, S062, S063, S064, S107, S112 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM_LOW | Recent empirical work measures selected proof effort/defects, but controlled comparative ROI remains weak. | S100, S107, S112 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM | Guidance encourages method fit and objective-based credit, not a universal cost formula. | S052, S053, S054 |
| TRANSFERABILITY_STRENGTH | HIGH_AS_DECISION_DISCIPLINE | The escalation/cheap-path principle transfers widely although thresholds are domain-specific. | S058, S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Risk, tractability, expertise, reuse, change rate and nonformal uncertainty determine payoff. | S063, S064, S100, S112 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Both historical criticism and current industry evidence contradict universal “too expensive” or “always worthwhile” claims. | S057, S063, S064, S112 |

**CRITICISMS:**
- Reliable comparative cost/benefit evidence is limited and confounded by domain, team expertise and project selection.
- Expected-loss calculations can falsely quantify uncertain specification and correspondence benefits.
- High-consequence claims may justify proof despite weak short-term ROI.
- Cheap methods can miss rare behaviours and create under-assurance if escalation criteria are weak.
- Learning and reusable-library benefits are difficult to allocate to one property.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Formalisation is a graduated assurance investment. The selected technique is the least costly one that can soundly discriminate the material failure class at the required scope; escalation, stopping, reuse and retirement are governed by decision value and currentness rather than prestige or proof volume.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P016 — Exhaustive finite-state challenge where warranted, P037 — Lightweight proportional formalisation. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P042 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while formal effort targets easy functions rather than high-consequence uncertainty?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P042?
- Would the cheap path — When an existing deterministic test or type/checker already fully discriminates the relevant failure class at lower trust and maintenance cost, use it and document why escalation is unnecessary — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P042, what decision changes, and should the artefact be retired if no live consumer remains?


### P043 — Prove everything

**PROPERTY_ID:** `P043`  
**PROPERTY_NAME:** Prove everything

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Full-system proof is not generally retained as a universal requirement; selective critical-property proof is mature. It is intended to prevent: The practice is a rejected overgeneralisation: attempting to prove every behaviour and component can consume disproportionate effort, force false environmental closure, delay feedback, create vast stale proof estates and distract from the few claims that control material risk.

**MATURE_FORM:** NO_GENERAL_PROPERTY: never require proof breadth as an end in itself. Establish the minimum sufficient formal perimeter around the critical claim, make residual boundaries explicit, and widen only when additional proof changes the decision more than a cheaper evidence source would.

**TRIGGER:** This rejected practice should be challenged whenever breadth, proof percentage or “fully verified” status is proposed without a claim- and boundary-specific payoff argument.

**CHEAP_PATH:** A whole-system proof may be justified for a small stable high-consequence system with a bounded environment; it is evaluated as a context-specific investment rather than a universal maturity requirement.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Prove everything",
  "ENGINEERING_CLAIM": "Full-system proof is not generally retained as a universal requirement; selective critical-property proof is mature.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying prove everything; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Completeness is always relative to an enumerated property set; “all correctness” is inadmissible.",
  "ENVIRONMENT_MODEL": "Physical/human/operational uncertainty remains outside unless explicitly modelled and validated.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide prove everything; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Specification effort grows without a stable stakeholder claim.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which do not adopt “prove everything” as a property.",
  "SAFETY_LIVENESS_CLASS": "rejected or disfavoured",
  "ABSTRACTION": "Any claimed breadth discloses abstracted and excluded behaviour.",
  "IMPLEMENTATION_CORRESPONDENCE": "Breadth claims require end-to-end identity/correspondence, not only source proof coverage.",
  "CHEAP_PATH": "A whole-system proof may be justified for a small stable high-consequence system with a bounded environment; it is evaluated as a context-specific investment rather than a universal maturity requirement.",
  "MATURE_FORM": "NO_GENERAL_PROPERTY: never require proof breadth as an end in itself. Establish the minimum sufficient formal perimeter around the critical claim, make residual boundaries explicit, and widen only when additional proof changes the decision more than a cheaper evidence source would.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P043; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Prove everything governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Any claimed breadth discloses abstracted and excluded behaviour.",
  "ESCALATION_TRIGGER": "This rejected practice should be challenged whenever breadth, proof percentage or “fully verified” status is proposed without a claim- and boundary-specific payoff argument.",
  "CHEAP_PATH": "A whole-system proof may be justified for a small stable high-consequence system with a bounded environment; it is evaluated as a context-specific investment rather than a universal maturity requirement."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for prove everything.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "A whole-system proof may be justified for a small stable high-consequence system with a bounded environment; it is evaluated as a context-specific investment rather than a universal maturity requirement."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Prove everything may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "This rejected practice should be challenged whenever breadth, proof percentage or “fully verified” status is proposed without a claim- and boundary-specific payoff argument.",
  "CHEAPER_EVIDENCE": "A whole-system proof may be justified for a small stable high-consequence system with a bounded environment; it is evaluated as a context-specific investment rather than a universal maturity requirement."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P043.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Breadth claims require end-to-end identity/correspondence, not only source proof coverage.",
  "ENVIRONMENT_BOUNDARY": "Physical/human/operational uncertainty remains outside unless explicitly modelled and validated.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "A larger proof estate often enlarges libraries, generators and maintenance dependencies even with a small kernel.",
  "DRIFT_DETECTOR": "Broad claims require sustainable full replay and change-impact mechanisms; otherwise breadth accelerates staleness.",
  "KNOWN_ESCAPE": "Specification effort grows without a stable stakeholder claim."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter prove everything.",
  "IDENTITIES_TO_BIND": "Broad claims require sustainable full replay and change-impact mechanisms; otherwise breadth accelerates staleness.",
  "REPLAY_OR_RECHECK": "A larger proof estate often enlarges libraries, generators and maintenance dependencies even with a small kernel.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Do not adopt “prove everything” as a property. Replace it with claim decomposition, critical-kernel selection, method-fit analysis, explicit nonformal boundaries, hybrid evidence and escalation by consequence and tractability. Whole-system proof remains a context-specific option where scope and payoff justify it.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "When does compositional proof genuinely approximate whole-system assurance rather than conceal interface assumptions?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Completeness is always relative to an enumerated property set; “all correctness” is inadmissible.
- Abstraction: Any claimed breadth discloses abstracted and excluded behaviour.
- Environment: Physical/human/operational uncertainty remains outside unless explicitly modelled and validated.
- Model/code correspondence: Breadth claims require end-to-end identity/correspondence, not only source proof coverage.
- Trusted tools: A larger proof estate often enlarges libraries, generators and maintenance dependencies even with a small kernel.
- Currentness/replay: Broad claims require sustainable full replay and change-impact mechanisms; otherwise breadth accelerates staleness.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | MEDIUM_HIGH | The maximalist target is historically visible mainly through advocacy/critique; lightweight and practice sources clearly document its rejection. | S015, S055, S057, S058 |
| FORMAL_SOUNDNESS_STRENGTH | NOT_APPLICABLE_AS_REJECTED_RULE | No formal theorem proves that every engineering-relevant behaviour should or can be formalised. | S056 |
| MECHANICAL_REPLAY_STRENGTH | LOW_AS_A_GENERAL_RULE | Replayability of individual proofs does not justify universal scope. | S096 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_AS_A_GENERAL_RULE | Whole-system correspondence is precisely the unresolved boundary the slogan suppresses. | S092, S093, S094 |
| INDUSTRIAL_CASE_STRENGTH | CONTEXT_SPECIFIC | Deep successes exist in kernels, compilers and protocols, but industry use remains selective. | S024, S025, S029, S030, S112 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Surveys support selective applicability and cost barriers, not a controlled universal counterfactual. | S063, S064, S100, S112 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | REJECTED_AS_UNIVERSAL | Assurance standards permit objective-specific method use rather than mandating total proof. | S052, S053 |
| TRANSFERABILITY_STRENGTH | LOW | The universal practice does not transfer; the selective replacement does. | S015, S058 |
| ASSUMPTION_SENSITIVITY | EXTREME | Feasibility and value depend on system scale, stability, environment and claim. | S063, S064 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Historical criticism, current maintenance evidence and selective industrial adoption strongly oppose the universal rule. | S055, S095, S112 |

**CRITICISMS:**
- The phrase conflates mathematical completeness in a model with complete assurance of a deployed system.
- Empirical evidence does not support universal economic superiority.
- Selective verified systems demonstrate strong value without establishing that their scope should be universal.
- Some domains may rationally require unusually broad proof, so rejection is of the universal rule, not of deep verification itself.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—NO_GENERAL_PROPERTY: never require proof breadth as an end in itself. Establish the minimum sufficient formal perimeter around the critical claim, make residual boundaries explicit, and widen only when additional proof changes the decision more than a cheaper evidence source would.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P037 — Lightweight proportional formalisation, P042 — Cost/payoff trigger discipline. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P043 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while specification effort grows without a stable stakeholder claim?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P043?
- Would the cheap path — A whole-system proof may be justified for a small stable high-consequence system with a bounded environment; it is evaluated as a context-specific investment rather than a universal maturity requirement — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P043, what decision changes, and should the artefact be retired if no live consumer remains?


### P044 — Proof eliminates testing

**PROPERTY_ID:** `P044`  
**PROPERTY_NAME:** Proof eliminates testing

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** The false dichotomy is rejected: proofs and testing supply different evidence over formal model versus empirical system. It is intended to prevent: This is a rejected substitution claim. A proof can establish a theorem about a model or program semantics while tests reveal wrong requirements, unmodelled integration, compiler/runtime/hardware behaviour, performance, usability, operational configuration and violated assumptions.

**MATURE_FORM:** Proof and testing have noninterchangeable scopes. Remove a test only when the formal result soundly subsumes its objective and remaining model, tool, integration and environmental assumptions are covered elsewhere. Prefer independent evidence whose failure modes are not perfectly correlated.

**TRIGGER:** Trigger whenever formal proof is proposed as a reason to remove, narrow or waive testing/fuzzing/integration evidence.

**CHEAP_PATH:** When a proof demonstrably subsumes a deterministic test objective and replay is cheaper, retire that redundant test while preserving tests for distinct assumptions and integration boundaries.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Proof eliminates testing",
  "ENGINEERING_CLAIM": "The false dichotomy is rejected: proofs and testing supply different evidence over formal model versus empirical system.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying proof eliminates testing; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Tests challenge the intended requirement and edge cases rather than merely restating the formal theorem.",
  "ENVIRONMENT_MODEL": "Physical, network, hardware, human and configuration premises are exercised or monitored where feasible.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide proof eliminates testing; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Tests are removed after a narrow functional proof, leaving integration defects undetected.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which do not treat proof as a test waiver except for the exact objective for which sound formal evidence supplies accepted coverage.",
  "SAFETY_LIVENESS_CLASS": "rejected or disfavoured",
  "ABSTRACTION": "Tests target behaviours omitted or coarsened by the abstraction and validate counterexample concretisation.",
  "IMPLEMENTATION_CORRESPONDENCE": "Binary/integration/conformance tests or validated translation connect the proved model/source to deployment.",
  "CHEAP_PATH": "When a proof demonstrably subsumes a deterministic test objective and replay is cheaper, retire that redundant test while preserving tests for distinct assumptions and integration boundaries.",
  "MATURE_FORM": "Proof and testing have noninterchangeable scopes. Remove a test only when the formal result soundly subsumes its objective and remaining model, tool, integration and environmental assumptions are covered elsewhere. Prefer independent evidence whose failure modes are not perfectly correlated.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P044; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to proof eliminates testing.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in This is a rejected substitution claim. A proof can establish a theorem about a model or program semantics while tests reveal wrong requirements, unmodelled integration, compiler/runtime/hardware behaviour, performance, usability, operational configuration and violated assumptions..",
  "RELATION": "Binary/integration/conformance tests or validated translation connect the proved model/source to deployment.",
  "SOUNDNESS_DUTY": "Tests target behaviours omitted or coarsened by the abstraction and validate counterexample concretisation.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Testing cannot prove absence over an unbounded state space, so hybridisation must not demote strong proofs to “just another test”.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Proof and testing have noninterchangeable scopes. Remove a test only when the formal result soundly subsumes its objective and remaining model, tool, integration and environmental assumptions are covered elsewhere. Prefer independent evidence whose failure modes are not perfectly correlated.",
  "KNOWN_GAP": "Tests are removed after a narrow functional proof, leaving integration defects undetected."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for proof eliminates testing.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "When a proof demonstrably subsumes a deterministic test objective and replay is cheaper, retire that redundant test while preserving tests for distinct assumptions and integration boundaries."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Proof eliminates testing may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger whenever formal proof is proposed as a reason to remove, narrow or waive testing/fuzzing/integration evidence.",
  "CHEAPER_EVIDENCE": "When a proof demonstrably subsumes a deterministic test objective and replay is cheaper, retire that redundant test while preserving tests for distinct assumptions and integration boundaries."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P044.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Binary/integration/conformance tests or validated translation connect the proved model/source to deployment.",
  "ENVIRONMENT_BOUNDARY": "Physical, network, hardware, human and configuration premises are exercised or monitored where feasible.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Solvers, checkers, compilers and generators are subject to independent tests/certificates appropriate to their role.",
  "DRIFT_DETECTOR": "Proof and test suites co-evolve; retiring an objective is reversed when proof scope/currentness is lost.",
  "KNOWN_ESCAPE": "Tests are removed after a narrow functional proof, leaving integration defects undetected."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter proof eliminates testing.",
  "IDENTITIES_TO_BIND": "Proof and test suites co-evolve; retiring an objective is reversed when proof scope/currentness is lost.",
  "REPLAY_OR_RECHECK": "Solvers, checkers, compilers and generators are subject to independent tests/certificates appropriate to their role.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Do not treat proof as a test waiver except for the exact objective for which sound formal evidence supplies accepted coverage. Construct a hybrid evidence map: proof discharges defined logical obligations; testing/fuzzing validates examples, assumptions, integration, binaries, environment and negative spaces; runtime monitoring covers observable residual conditions.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "What mutation strategies best test whether a proof/specification would detect realistic defects?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Tests challenge the intended requirement and edge cases rather than merely restating the formal theorem.
- Abstraction: Tests target behaviours omitted or coarsened by the abstraction and validate counterexample concretisation.
- Environment: Physical, network, hardware, human and configuration premises are exercised or monitored where feasible.
- Model/code correspondence: Binary/integration/conformance tests or validated translation connect the proved model/source to deployment.
- Trusted tools: Solvers, checkers, compilers and generators are subject to independent tests/certificates appropriate to their role.
- Currentness/replay: Proof and test suites co-evolve; retiring an objective is reversed when proof scope/currentness is lost.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Formal-method practice principles and assurance guidance directly reject proof-versus-testing substitution. | S052, S053, S057, S058 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_WITHIN_EACH_SCOPE | Proof soundness and empirical test evidence retain their distinct logical strengths and limitations. | S002, S052 |
| MECHANICAL_REPLAY_STRENGTH | HIGH_FOR_PROOF; EMPIRICAL_FOR_TESTS | Formal artefacts replay exactly; tests are repeatable but sample behaviours. | S095, S100 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | HIGHER_AS_HYBRID | Integration and environment tests directly strengthen correspondence that proof alone lacks. | S092, S093 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_SELECTED_CASES | Verified systems continue to report testing/evaluation and standards integrate formal and conventional evidence. | S024, S025, S028, S030, S052 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Practitioner evidence and solver/compiler defect campaigns support complementarity; portfolio-level comparative trials are limited. | S097, S100 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH | DO-333 explicitly integrates formal methods with DO-178C objectives rather than abolishing all testing. | S051, S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH | The complementarity principle transfers widely, though the mix varies by claim. | S058, S065 |
| ASSUMPTION_SENSITIVITY | HIGH | Optimal allocation depends on proof scope, environment uncertainty and evidence correlation. | S092, S100 |
| CONTRARY_EVIDENCE_STRENGTH | VERY_HIGH | Specification, correspondence, solver and field evidence directly contradict proof-eliminates-testing claims. | S055, S092, S097, S100 |

**CRITICISMS:**
- Testing cannot prove absence over an unbounded state space, so hybridisation must not demote strong proofs to “just another test”.
- Some test objectives may legitimately be replaced by formal evidence under standards.
- Poorly designed hybrid stacks duplicate cost without independent failure sensitivity.
- Physical and probabilistic environments may need experiments/statistics rather than conventional software tests.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Proof and testing have noninterchangeable scopes. Remove a test only when the formal result soundly subsumes its objective and remaining model, tool, integration and environmental assumptions are covered elsewhere. Prefer independent evidence whose failure modes are not perfectly correlated.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P036 — Hybrid proof + testing/fuzzing/runtime evidence, P049 — Stakeholder/world-machine validation. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P044 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while tests are removed after a narrow functional proof, leaving integration defects undetected?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P044?
- Would the cheap path — When a proof demonstrably subsumes a deterministic test objective and replay is cheaper, retire that redundant test while preserving tests for distinct assumptions and integration boundaries — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P044, what decision changes, and should the artefact be retired if no live consumer remains?


### P045 — Model checking explores every real behaviour

**PROPERTY_ID:** `P045`  
**PROPERTY_NAME:** Model checking explores every real behaviour

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Model checking explores behaviours represented by the model/scope; real behaviour correspondence is an added claim. It is intended to prevent: This is a rejected scope inflation. Exhausting a finite or abstract transition system says nothing about behaviours omitted by the model, bounded beyond the search depth, introduced by code generation, weak memory, deployment configuration, hardware or environment.

**MATURE_FORM:** Claim only that the specified property holds over the identified formal transition system at the disclosed bounds and reduction assumptions. Promote this to an implementation/deployment claim only after separately establishing model construction, refinement/correspondence and environmental adequacy.

**TRIGGER:** Challenge whenever “all behaviours”, “exhaustive” or “no counterexample” is used without an explicit model/bound/environment qualifier.

**CHEAP_PATH:** For a genuinely finite, directly executable state machine whose inputs and transitions are complete, ordinary exhaustive enumeration may be sufficient without a large model-checking framework.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Model checking explores every real behaviour",
  "ENGINEERING_CLAIM": "Model checking explores behaviours represented by the model/scope; real behaviour correspondence is an added claim.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying model checking explores every real behaviour; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The checked property is non-vacuous and covers the intended safety/liveness case.",
  "ENVIRONMENT_MODEL": "All environment/failure actions relevant to the claim are modelled or explicitly excluded.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide model checking explores every real behaviour; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Bounded model checking success is reported as proof.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which state the explored universe precisely: initial states, transition relation, bounds, reductions, fairness, data/domain limits and environment.",
  "SAFETY_LIVENESS_CLASS": "rejected or disfavoured",
  "ABSTRACTION": "Over/under-approximation and reduction preservation conditions are established and spurious traces managed.",
  "IMPLEMENTATION_CORRESPONDENCE": "Implementation is generated from, extracted to, or proven/tested conformant with the checked model.",
  "CHEAP_PATH": "For a genuinely finite, directly executable state machine whose inputs and transitions are complete, ordinary exhaustive enumeration may be sufficient without a large model-checking framework.",
  "MATURE_FORM": "Claim only that the specified property holds over the identified formal transition system at the disclosed bounds and reduction assumptions. Promote this to an implementation/deployment claim only after separately establishing model construction, refinement/correspondence and environmental adequacy.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P045; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to model checking explores every real behaviour.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in This is a rejected scope inflation. Exhausting a finite or abstract transition system says nothing about behaviours omitted by the model, bounded beyond the search depth, introduced by code generation, weak memory, deployment configuration, hardware or environment..",
  "RELATION": "Implementation is generated from, extracted to, or proven/tested conformant with the checked model.",
  "SOUNDNESS_DUTY": "Over/under-approximation and reduction preservation conditions are established and spurious traces managed.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "State explosion forces bounds, abstraction and reductions that narrow literal exhaustiveness.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "Claim only that the specified property holds over the identified formal transition system at the disclosed bounds and reduction assumptions. Promote this to an implementation/deployment claim only after separately establishing model construction, refinement/correspondence and environmental adequacy.",
  "KNOWN_GAP": "Bounded model checking success is reported as proof."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "PROPERTY_TO_CHECK": "Model checking explores behaviours represented by the model/scope; real behaviour correspondence is an added claim.",
  "SEARCH_DOMAIN": "A finite, bounded or abstract transition space whose coverage claim is explicit for model checking explores every real behaviour.",
  "EXHAUSTIVENESS_STATUS": "Must be labelled exhaustive for the represented finite model, bounded to a stated horizon, or heuristic; these are not interchangeable.",
  "REDUCTIONS_OR_ABSTRACTIONS": "Over/under-approximation and reduction preservation conditions are established and spurious traces managed.",
  "COUNTEREXAMPLE_DUTY": "Replay and validate any trace against the concrete boundary; specifically guard against Bounded model checking success is reported as proof..",
  "VACUITY_DUTY": "Show reachability/non-emptiness and exercise the antecedents or behaviours that give the property engineering meaning.",
  "DECISION_RULE": "Preserves model checking’s exceptional ability to exhaust finite concurrency/state combinations and produce actionable traces without allowing “exhaustive” to become an unbounded marketing claim."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking explores every real behaviour may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Challenge whenever “all behaviours”, “exhaustive” or “no counterexample” is used without an explicit model/bound/environment qualifier.",
  "CHEAPER_EVIDENCE": "For a genuinely finite, directly executable state machine whose inputs and transitions are complete, ordinary exhaustive enumeration may be sufficient without a large model-checking framework."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P045.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Implementation is generated from, extracted to, or proven/tested conformant with the checked model.",
  "ENVIRONMENT_BOUNDARY": "All environment/failure actions relevant to the claim are modelled or explicitly excluded.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Checker, encoding, reduction and counterexample generation are versioned; certificates or cross-checks used where consequence warrants.",
  "DRIFT_DETECTOR": "Model, bounds, fairness and code/config identities are replayed after change; an old exhaustive run is not current evidence.",
  "KNOWN_ESCAPE": "Bounded model checking success is reported as proof."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter model checking explores every real behaviour.",
  "IDENTITIES_TO_BIND": "Model, bounds, fairness and code/config identities are replayed after change; an old exhaustive run is not current evidence.",
  "REPLAY_OR_RECHECK": "Checker, encoding, reduction and counterexample generation are versioned; certificates or cross-checks used where consequence warrants.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: State the explored universe precisely: initial states, transition relation, bounds, reductions, fairness, data/domain limits and environment. Label results as exhaustive, symbolic, bounded or under-approximating. Validate abstraction and model-code correspondence, concretise counterexamples, and test omitted boundaries.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should reductions be certified when their optimal construction is computationally hard?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The checked property is non-vacuous and covers the intended safety/liveness case.
- Abstraction: Over/under-approximation and reduction preservation conditions are established and spurious traces managed.
- Environment: All environment/failure actions relevant to the claim are modelled or explicitly excluded.
- Model/code correspondence: Implementation is generated from, extracted to, or proven/tested conformant with the checked model.
- Trusted tools: Checker, encoding, reduction and counterexample generation are versioned; certificates or cross-checks used where consequence warrants.
- Currentness/replay: Model, bounds, fairness and code/config identities are replayed after change; an old exhaustive run is not current evidence.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Foundational model-checking, symbolic and SPIN sources precisely define exhaustive search over formal models. | S007, S008, S009 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_DISCLOSED_MODEL | Sound algorithms establish the property for their exact state semantics and reduction assumptions. | S007, S008, S061 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Runs/counterexamples replay under pinned tools and models; search feasibility may vary. | S009, S036 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_BY_ITSELF | Exhaustion establishes no implementation or world correspondence without additional evidence. | S092, S106 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_SELECTED_DOMAINS | AWS and protocol/hardware applications demonstrate value at model/design level. | S029, S062 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Case evidence and defect studies are strong, but comparative prevalence/ROI remains selective. | S092, S100 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_IN_ASSURANCE_USE | DO-333 recognises model checking with scope, coverage and soundness obligations. | S052, S054 |
| TRANSFERABILITY_STRENGTH | HIGH_FOR_FINITE_MODELS | The bounded claim transfers widely; real-world exhaustiveness never does automatically. | S016, S065 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | State semantics, bounds, abstraction, fairness and environment determine the conclusion. | S036, S061, S103 |
| CONTRARY_EVIDENCE_STRENGTH | VERY_HIGH | State explosion, reduction complexity, weak memory and empirical correspondence defects directly refute the caricature. | S092, S103, S106 |

**CRITICISMS:**
- State explosion forces bounds, abstraction and reductions that narrow literal exhaustiveness.
- Spurious counterexamples can dominate over-approximations; under-approximations miss behaviours.
- Current complexity work shows optimal partial-order reduction itself can be hard [S103].
- Verified distributed-system defects show model/code/environment gaps despite strong model-level results [S092].
- No counterexample is not evidence about properties the model never expressed.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Claim only that the specified property holds over the identified formal transition system at the disclosed bounds and reduction assumptions. Promote this to an implementation/deployment claim only after separately establishing model construction, refinement/correspondence and environmental adequacy.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P003 — Environment model boundary, P016 — Exhaustive finite-state challenge where warranted. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P045 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while bounded model checking success is reported as proof?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P045?
- Would the cheap path — For a genuinely finite, directly executable state machine whose inputs and transitions are complete, ordinary exhaustive enumeration may be sufficient without a large model-checking framework — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P045, what decision changes, and should the artefact be retired if no live consumer remains?


### P046 — Type safety means functional correctness

**PROPERTY_ID:** `P046`  
**PROPERTY_NAME:** Type safety means functional correctness

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Type safety and related guarantees are precise but narrower than functional correctness. It is intended to prevent: This is a rejected inference: a program can satisfy its language’s type-safety theorem while computing the wrong value, violating a domain invariant, leaking information, deadlocking, exhausting resources or failing an unstated protocol requirement.

**MATURE_FORM:** A type-safety claim names the excluded error class, soundness assumptions and escape hatches. Functional correctness is claimed only when the relevant function/property is actually represented in the type and checked under a sound, terminating logic with validated specification.

**TRIGGER:** Challenge whenever “type safe”, “Rust safe”, “dependent typed” or “proof by type checking” is used to support a broader functional, temporal or deployment claim.

**CHEAP_PATH:** Use ordinary type checking as the cheap path when the decision concerns exactly the language-defined type error class; do not add theorem proving for already-subsumed obligations.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Type safety means functional correctness",
  "ENGINEERING_CLAIM": "Type safety and related guarantees are precise but narrower than functional correctness.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying type safety means functional correctness; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Any semantic property encoded in a type is reviewed like any other formal specification.",
  "ENVIRONMENT_MODEL": "External components, network, runtime and hardware satisfy the assumptions behind the type guarantee.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide type safety means functional correctness; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Nominal or structural typing is marketed as semantic correctness.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which publish the exact typing judgement and meta-theorem: progress/preservation, memory safety, absence of a particular error, ownership/race condition, refinement predicate or protocol discipline.",
  "SAFETY_LIVENESS_CLASS": "rejected or disfavoured",
  "ABSTRACTION": "Type abstractions preserve the relevant resource/protocol semantics and disclose erased runtime behaviour.",
  "IMPLEMENTATION_CORRESPONDENCE": "The compiled/executed artefact preserves the checked type discipline and escape hatches are bounded.",
  "CHEAP_PATH": "Use ordinary type checking as the cheap path when the decision concerns exactly the language-defined type error class; do not add theorem proving for already-subsumed obligations.",
  "MATURE_FORM": "A type-safety claim names the excluded error class, soundness assumptions and escape hatches. Functional correctness is claimed only when the relevant function/property is actually represented in the type and checked under a sound, terminating logic with validated specification.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P046; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Type safety means functional correctness governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Type abstractions preserve the relevant resource/protocol semantics and disclose erased runtime behaviour.",
  "ESCALATION_TRIGGER": "Challenge whenever “type safe”, “Rust safe”, “dependent typed” or “proof by type checking” is used to support a broader functional, temporal or deployment claim.",
  "CHEAP_PATH": "Use ordinary type checking as the cheap path when the decision concerns exactly the language-defined type error class; do not add theorem proving for already-subsumed obligations."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for type safety means functional correctness.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "Use ordinary type checking as the cheap path when the decision concerns exactly the language-defined type error class; do not add theorem proving for already-subsumed obligations."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Type safety means functional correctness may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Challenge whenever “type safe”, “Rust safe”, “dependent typed” or “proof by type checking” is used to support a broader functional, temporal or deployment claim.",
  "CHEAPER_EVIDENCE": "Use ordinary type checking as the cheap path when the decision concerns exactly the language-defined type error class; do not add theorem proving for already-subsumed obligations."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P046.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "The compiled/executed artefact preserves the checked type discipline and escape hatches are bounded.",
  "ENVIRONMENT_BOUNDARY": "External components, network, runtime and hardware satisfy the assumptions behind the type guarantee.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Type checker, compiler, macros/generators, logical axioms and unsafe features are in scope.",
  "DRIFT_DETECTOR": "Language/compiler/library/API changes trigger re-type-checking and review of changed soundness/unsafe boundaries.",
  "KNOWN_ESCAPE": "Nominal or structural typing is marketed as semantic correctness."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter type safety means functional correctness.",
  "IDENTITIES_TO_BIND": "Language/compiler/library/API changes trigger re-type-checking and review of changed soundness/unsafe boundaries.",
  "REPLAY_OR_RECHECK": "Type checker, compiler, macros/generators, logical axioms and unsafe features are in scope.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Publish the exact typing judgement and meta-theorem: progress/preservation, memory safety, absence of a particular error, ownership/race condition, refinement predicate or protocol discipline. Treat untyped/unsafe/FFI/reflection boundaries and logical consistency explicitly; add contracts/proofs/tests for functional and temporal claims not encoded by the type.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should reviewers quantify residual risk at unsafe, FFI and generated-code boundaries?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Any semantic property encoded in a type is reviewed like any other formal specification.
- Abstraction: Type abstractions preserve the relevant resource/protocol semantics and disclose erased runtime behaviour.
- Environment: External components, network, runtime and hardware satisfy the assumptions behind the type guarantee.
- Model/code correspondence: The compiled/executed artefact preserves the checked type discipline and escape hatches are bounded.
- Trusted tools: Type checker, compiler, macros/generators, logical axioms and unsafe features are in scope.
- Currentness/replay: Language/compiler/library/API changes trigger re-type-checking and review of changed soundness/unsafe boundaries.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Martin-Löf lineage and modern refinement/ownership work directly establish plural type guarantees. | S045, S046, S047 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_FOR_EXACT_META_THEOREM | Type soundness can be rigorous for the stated calculus; it proves no unencoded requirement. | S045, S046 |
| MECHANICAL_REPLAY_STRENGTH | HIGH | Type checking is mechanically replayable under pinned language/compiler semantics. | S046, S047 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_LOW | Compilation, unsafe and FFI boundaries require separate correspondence evidence. | S046, S094 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_FOR_DEFECT_CLASSES | Ownership and refinement systems show practical strength, but no universal functional-correctness inference follows. | S046, S047 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Evidence supports defect prevention and usability trade-offs; broad comparative functional-correctness data is limited. | S064, S100 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM | Strong typing contributes to assurance but certification credit remains claim/objective-specific. | S052 |
| TRANSFERABILITY_STRENGTH | HIGH_WITH_CLAIM_BOUNDARY | The bounded principle transfers across type systems; exact guarantees are language-specific. | S045, S089 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Soundness depends on calculus, termination, unsafe interfaces, runtime and encoded predicate. | S046, S047 |
| CONTRARY_EVIDENCE_STRENGTH | VERY_HIGH | Foundational semantics and integration boundaries directly contradict type-safety-equals-correctness. | S045, S046, S089 |

**CRITICISMS:**
- The guarantee is exactly as strong as the type language and soundness theorem, not the word “typed”.
- Dependent types shift specification and proof burden into types; they do not validate the predicate.
- Strong types can increase annotation/evolution cost and may be bypassed at integration boundaries.
- Behavioural subtyping requires semantic obligations beyond nominal subtyping [S089].

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A type-safety claim names the excluded error class, soundness assumptions and escape hatches. Functional correctness is claimed only when the relevant function/property is actually represented in the type and checked under a sound, terminating logic with validated specification.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P027 — Type-system claim boundary, P049 — Stakeholder/world-machine validation. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P046 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while nominal or structural typing is marketed as semantic correctness?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P046?
- Would the cheap path — Use ordinary type checking as the cheap path when the decision concerns exactly the language-defined type error class; do not add theorem proving for already-subsumed obligations — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P046, what decision changes, and should the artefact be retired if no live consumer remains?


### P047 — Proof assistant cannot be wrong

**PROPERTY_ID:** `P047`  
**PROPERTY_NAME:** Proof assistant cannot be wrong

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Proof assistants reduce proof-checking risk but depend on kernels, axioms, libraries, unsafe features and build environment. It is intended to prevent: The caricature hides residual trust in kernel implementation, parser/elaboration, axioms, unsafe commands, code extraction, external solvers/oracles, operating system/hardware and—most importantly—the formal statement. Small trust is not zero trust.

**MATURE_FORM:** A checked theorem carries a bounded trust statement: exact kernel, logic, axioms, parser/elaborator, external oracle/certificate path, libraries and artefact provenance. Consequential results favour independently checkable certificates or reconstruction and treat proof validity as only one layer of the engineering claim.

**TRIGGER:** Trigger whenever kernel checking, proof-assistant use or a “verified” tool is cited as eliminating the possibility of tool or statement error.

**CHEAP_PATH:** For low-consequence local proofs, ordinary kernel replay plus axiom/unsafe checks may be sufficient; independent checker diversification is consequence-driven.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Proof assistant cannot be wrong",
  "ENGINEERING_CLAIM": "Proof assistants reduce proof-checking risk but depend on kernels, axioms, libraries, unsafe features and build environment.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying proof assistant cannot be wrong; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Kernel acceptance cannot substitute for validating the theorem statement against engineering intent.",
  "ENVIRONMENT_MODEL": "Hardware/runtime and distribution integrity assumptions are bounded or accepted.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide proof assistant cannot be wrong; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: Kernel or elaborator bug accepts an invalid term.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which inventory the trusted computing base and theorem dependencies; reject admitted/unsafe constructs unless explicitly authorised; inspect axioms; pin kernel/library/tool versions; prefer proof terms/certificates checked by a small independent verifier; diversify or fuzz critical checkers/solvers; validate the claimed statement and binary/provenance boundary separately.",
  "SAFETY_LIVENESS_CLASS": "assumption sensitive",
  "ABSTRACTION": "The checker proves only the encoded abstract semantics; omitted behaviours remain explicit.",
  "IMPLEMENTATION_CORRESPONDENCE": "Extraction/compilation/binary correspondence is separately proven, validated or tested.",
  "CHEAP_PATH": "For low-consequence local proofs, ordinary kernel replay plus axiom/unsafe checks may be sufficient; independent checker diversification is consequence-driven.",
  "MATURE_FORM": "A checked theorem carries a bounded trust statement: exact kernel, logic, axioms, parser/elaborator, external oracle/certificate path, libraries and artefact provenance. Consequential results favour independently checkable certificates or reconstruction and treat proof validity as only one layer of the engineering claim.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P047; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Proof assistant cannot be wrong governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "The checker proves only the encoded abstract semantics; omitted behaviours remain explicit.",
  "ESCALATION_TRIGGER": "Trigger whenever kernel checking, proof-assistant use or a “verified” tool is cited as eliminating the possibility of tool or statement error.",
  "CHEAP_PATH": "For low-consequence local proofs, ordinary kernel replay plus axiom/unsafe checks may be sufficient; independent checker diversification is consequence-driven."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for proof assistant cannot be wrong.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For low-consequence local proofs, ordinary kernel replay plus axiom/unsafe checks may be sufficient; independent checker diversification is consequence-driven."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "Proof assistants reduce proof-checking risk but depend on kernels, axioms, libraries, unsafe features and build environment.",
  "ASSUMPTIONS_AND_AXIOMS": "Defined logic and kernel, dependency/axiom audit, tool provenance, external-oracle policy and statement validation.",
  "CHECKER_OR_KERNEL_BOUNDARY": "The trusted base is explicit, minimal where practical, and independently challenged for high-consequence claims.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for proof assistant cannot be wrong.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Proofs replay on the pinned toolchain; kernel/library upgrades trigger revalidation and compatibility review.",
  "CORRESPONDENCE_DUTY": "Extraction/compilation/binary correspondence is separately proven, validated or tested.",
  "MISUSE_TO_PREVENT": "TCB analyses of CompCert and seL4 document nontrivial external assumptions [S093, S094]."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P047.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Extraction/compilation/binary correspondence is separately proven, validated or tested.",
  "ENVIRONMENT_BOUNDARY": "Hardware/runtime and distribution integrity assumptions are bounded or accepted.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "The trusted base is explicit, minimal where practical, and independently challenged for high-consequence claims.",
  "DRIFT_DETECTOR": "Proofs replay on the pinned toolchain; kernel/library upgrades trigger revalidation and compatibility review.",
  "KNOWN_ESCAPE": "Kernel or elaborator bug accepts an invalid term."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter proof assistant cannot be wrong.",
  "IDENTITIES_TO_BIND": "Proofs replay on the pinned toolchain; kernel/library upgrades trigger revalidation and compatibility review.",
  "REPLAY_OR_RECHECK": "The trusted base is explicit, minimal where practical, and independently challenged for high-consequence claims.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Inventory the trusted computing base and theorem dependencies; reject admitted/unsafe constructs unless explicitly authorised; inspect axioms; pin kernel/library/tool versions; prefer proof terms/certificates checked by a small independent verifier; diversify or fuzz critical checkers/solvers; validate the claimed statement and binary/provenance boundary separately.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "Can proof-assistant distributions provide end-to-end reproducible provenance without making maintenance impractical?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Kernel acceptance cannot substitute for validating the theorem statement against engineering intent.
- Abstraction: The checker proves only the encoded abstract semantics; omitted behaviours remain explicit.
- Environment: Hardware/runtime and distribution integrity assumptions are bounded or accepted.
- Model/code correspondence: Extraction/compilation/binary correspondence is separately proven, validated or tested.
- Trusted tools: The trusted base is explicit, minimal where practical, and independently challenged for high-consequence claims.
- Currentness/replay: Proofs replay on the pinned toolchain; kernel/library upgrades trigger revalidation and compatibility review.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | LCF/HOL/Isabelle/Coq directly establish the small-kernel lineage. | S042, S043, S044 |
| FORMAL_SOUNDNESS_STRENGTH | HIGH_BUT_CONDITIONAL | Kernel soundness arguments are strong for the defined logic and implementation assumptions. | S042, S044 |
| MECHANICAL_REPLAY_STRENGTH | VERY_HIGH | Proof terms/scripts and certificates permit mechanical replay, subject to current tool identity. | S043, S095, S108 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | LOW_BY_ITSELF | Kernel checking supplies no model-code/environment correspondence. | S093, S094 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_IN_MAJOR_PROJECTS | seL4, CompCert and large proof developments make the TCB concrete. | S024, S025, S093, S094, S096 |
| EMPIRICAL_COMPARATIVE_STRENGTH | HIGH_FOR_TOOL_RISK | Compatibility and SMT-fuzzing studies provide direct empirical evidence of tooling defects/change risk. | S095, S097 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | MEDIUM_HIGH | Assurance practice values bounded/qualified tools but does not declare them infallible. | S051, S052 |
| TRANSFERABILITY_STRENGTH | HIGH | Bounded-trust architecture transfers across proof assistants, solvers and certificate systems. | S022, S035 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Logic, axioms, unsafe features, tool version, external oracles and statement meaning all matter. | S043, S094 |
| CONTRARY_EVIDENCE_STRENGTH | VERY_HIGH | TCB analyses, solver soundness bugs and compatibility failures decisively refute infallibility. | S094, S095, S097 |

**CRITICISMS:**
- TCB analyses of CompCert and seL4 document nontrivial external assumptions [S093, S094].
- SMT fuzzing found confirmed soundness bugs, showing mature automated reasoners are fallible [S097].
- A tiny kernel reduces attack/error surface but can concentrate trust and does not validate semantics outside logic.
- Independent checking can share libraries, semantics or generated-certificate bugs.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A checked theorem carries a bounded trust statement: exact kernel, logic, axioms, parser/elaborator, external oracle/certificate path, libraries and artefact provenance. Consequential results favour independently checkable certificates or reconstruction and treat proof validity as only one layer of the engineering claim.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P022 — Trusted kernel/certificate boundary, P024 — Solver/encoding trust boundary. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P047 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while kernel or elaborator bug accepts an invalid term?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P047?
- Would the cheap path — For low-consequence local proofs, ordinary kernel replay plus axiom/unsafe checks may be sufficient; independent checker diversification is consequence-driven — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P047, what decision changes, and should the artefact be retired if no live consumer remains?


### P048 — Retirement of stale formal artefacts

**PROPERTY_ID:** `P048`  
**PROPERTY_NAME:** Retirement of stale formal artefacts

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Formal artefacts with no current replay, model-code link, or live decision consumer should be retired or downgraded. It is intended to prevent: A formally impressive artefact can remain green in reports while no longer replaying, no longer matching the source/configuration, depending on obsolete tooling, lacking an owner or serving no current decision. Keeping it as assurance evidence creates false confidence and maintenance drag.

**MATURE_FORM:** Every formal artefact is ACTIVE, STALE, RETIRED or HISTORICAL. ACTIVE requires a current consumer, identity binding, reproducible replay and satisfied correspondence assumptions. STALE status automatically revokes assurance credit; RETIRED artefacts remain archived with provenance, witnesses and re-entry conditions.

**TRIGGER:** Trigger for every persistent proof, model, certificate, static-analysis baseline or runtime specification used across releases.

**CHEAP_PATH:** One-off exploratory checks may be archived without maintenance if clearly labelled non-assurance and no downstream consumer relies on them.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Retirement of stale formal artefacts",
  "ENGINEERING_CLAIM": "Formal artefacts with no current replay, model-code link, or live decision consumer should be retired or downgraded.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying retirement of stale formal artefacts; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Claim/spec version is part of freshness; unchanged theorem text does not imply unchanged meaning.",
  "ENVIRONMENT_MODEL": "Configuration, hardware/network assumptions and operational use are freshness dependencies.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide retirement of stale formal artefacts; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: An old PDF proof is cited although sources and libraries have changed.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which give each artefact a consumer, exact claim, source/model/tool/configuration identities, dependency graph, replay command and freshness policy.",
  "SAFETY_LIVENESS_CLASS": "retained in evolved form",
  "ABSTRACTION": "Model/abstraction changes trigger status review even when code is unchanged.",
  "IMPLEMENTATION_CORRESPONDENCE": "Active status requires current correspondence to the governed implementation/binary/configuration.",
  "CHEAP_PATH": "One-off exploratory checks may be archived without maintenance if clearly labelled non-assurance and no downstream consumer relies on them.",
  "MATURE_FORM": "Every formal artefact is ACTIVE, STALE, RETIRED or HISTORICAL. ACTIVE requires a current consumer, identity binding, reproducible replay and satisfied correspondence assumptions. STALE status automatically revokes assurance credit; RETIRED artefacts remain archived with provenance, witnesses and re-entry conditions.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P048; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "INDIRECT_OR_NOT_NORMALLY_REQUIRED",
  "RATIONALE": "Retirement of stale formal artefacts governs claim, trust, lifecycle or proportionality rather than requiring a particular abstraction proof.",
  "MINIMUM_DUTY": "Model/abstraction changes trigger status review even when code is unchanged.",
  "ESCALATION_TRIGGER": "Trigger for every persistent proof, model, certificate, static-analysis baseline or runtime specification used across releases.",
  "CHEAP_PATH": "One-off exploratory checks may be archived without maintenance if clearly labelled non-assurance and no downstream consumer relies on them."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for retirement of stale formal artefacts.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "One-off exploratory checks may be archived without maintenance if clearly labelled non-assurance and no downstream consumer relies on them."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Retirement of stale formal artefacts may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger for every persistent proof, model, certificate, static-analysis baseline or runtime specification used across releases.",
  "CHEAPER_EVIDENCE": "One-off exploratory checks may be archived without maintenance if clearly labelled non-assurance and no downstream consumer relies on them."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "SUPPORTING_OR_CONDITIONAL",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P048.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Active status requires current correspondence to the governed implementation/binary/configuration.",
  "ENVIRONMENT_BOUNDARY": "Configuration, hardware/network assumptions and operational use are freshness dependencies.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Archived and active toolchains are identified; checker/library upgrades are impact-assessed.",
  "DRIFT_DETECTOR": "This property is itself the currentness gate: replay and semantic impact determine active status; otherwise evidence is withdrawn.",
  "KNOWN_ESCAPE": "An old PDF proof is cited although sources and libraries have changed."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter retirement of stale formal artefacts.",
  "IDENTITIES_TO_BIND": "This property is itself the currentness gate: replay and semantic impact determine active status; otherwise evidence is withdrawn.",
  "REPLAY_OR_RECHECK": "Archived and active toolchains are identified; checker/library upgrades are impact-assessed.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Give each artefact a consumer, exact claim, source/model/tool/configuration identities, dependency graph, replay command and freshness policy. Automatically mark stale after relevant changes; repair/revalidate when decision value warrants; otherwise retire from active assurance while preserving an immutable historical archive and rationale.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should organisations value dormant proof assets that may become relevant after future redesign?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Claim/spec version is part of freshness; unchanged theorem text does not imply unchanged meaning.
- Abstraction: Model/abstraction changes trigger status review even when code is unchanged.
- Environment: Configuration, hardware/network assumptions and operational use are freshness dependencies.
- Model/code correspondence: Active status requires current correspondence to the governed implementation/binary/configuration.
- Trusted tools: Archived and active toolchains are identified; checker/library upgrades are impact-assessed.
- Currentness/replay: This property is itself the currentness gate: replay and semantic impact determine active status; otherwise evidence is withdrawn.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | MEDIUM_HIGH | Mechanised proof and lifecycle-control lineages establish replay/currentness; explicit retirement is a modern governance synthesis. | S052, S096, S113 |
| FORMAL_SOUNDNESS_STRENGTH | NOT_A_NEW_SOUNDNESS_THEOREM | Retirement protects claim status; it does not change the underlying theorem. | S096 |
| MECHANICAL_REPLAY_STRENGTH | VERY_HIGH | Replay status is directly machine-checkable when artefacts and environments are preserved. | S095 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | HIGH_IF_IDENTITY_BOUND | Currentness controls can strongly protect correspondence, though they cannot establish semantic adequacy alone. | S113 |
| INDUSTRIAL_CASE_STRENGTH | MEDIUM_HIGH | Large proof projects and certification practice have real maintenance/configuration burdens. | S096, S113 |
| EMPIRICAL_COMPARATIVE_STRENGTH | HIGH_FOR_COMPATIBILITY | The Isabelle study reports 12,079 cross-version issues and concrete repair categories; broader frequencies remain uncertain. | S095 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH | Configuration/change control and reusable evidence obligations are established in assurance guidance. | S052, S113 |
| TRANSFERABILITY_STRENGTH | HIGH | Stale-evidence retirement transfers to every persistent formal artefact. | S065, S096 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | Tool/library/code/spec/environment change and consumer need determine whether evidence remains live. | S095, S113 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | Empirical compatibility failures and proof-engineering burdens directly contradict “proof once passed means proof forever”. | S095, S096 |

**CRITICISMS:**
- Aggressive retirement can discard reusable knowledge and make future re-entry expensive.
- Fresh replay does not prove specification or correspondence freshness.
- Version compatibility failures may be superficial syntax/API churn rather than lost theorem truth.
- Archiving complete reproducible toolchains can be costly and insecure.
- Freshness intervals are poor substitutes for semantic change-impact analysis.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—Every formal artefact is ACTIVE, STALE, RETIRED or HISTORICAL. ACTIVE requires a current consumer, identity binding, reproducible replay and satisfied correspondence assumptions. STALE status automatically revokes assurance credit; RETIRED artefacts remain archived with provenance, witnesses and re-entry conditions.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P023 — Proof maintenance and currentness, P041 — Certification/formality ceremony boundary. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P048 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while an old pdf proof is cited although sources and libraries have changed?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P048?
- Would the cheap path — One-off exploratory checks may be archived without maintenance if clearly labelled non-assurance and no downstream consumer relies on them — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P048, what decision changes, and should the artefact be retired if no live consumer remains?


### P049 — Stakeholder/world-machine validation

**PROPERTY_ID:** `P049`  
**PROPERTY_NAME:** Stakeholder/world-machine validation

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** The formal statement must be validated against stakeholder/mission/world requirements, not only internal consistency. It is intended to prevent: A formal statement can be exact and fully proved yet encode the wrong stakeholder outcome, use unobservable variables, confuse a desired world condition with a software output, omit domain laws or validate only internal machine states. Precision (P001) is insufficient without meaning validation at the world–machine boundary.

**MATURE_FORM:** A mechanically checked property controls a real engineering claim only when its variables, units, observations and outputs are traceable to stakeholder/world phenomena, its domain assumptions are independently supported, and a named operational or assurance consumer can interpret the result. Proof validity and requirement validity remain separate statuses.

**TRIGGER:** Trigger when a formal claim represents an external outcome, safety/security objective, human workflow, physical process, sensor/actuator relation or AI-generated translation from stakeholder prose.

**CHEAP_PATH:** For a purely internal algebraic transformation with an agreed mathematical contract, direct examples and peer review may suffice without a full world–machine model.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Stakeholder/world-machine validation",
  "ENGINEERING_CLAIM": "The formal statement must be validated against stakeholder/mission/world requirements, not only internal consistency.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying stakeholder/world-machine validation; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "The formal statement is traceable to the stakeholder/world claim and tested against representative interpretations.",
  "ENVIRONMENT_MODEL": "Domain laws, sensors, actuators, humans and external systems are evidenced, monitored or clearly residual.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide stakeholder/world-machine validation; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: The theorem proves an internal flag while the real-world condition remains unmet.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which model stakeholders/mission, monitored and controlled phenomena, domain assumptions, machine interfaces and the causal/observational relation from machine behaviour to world outcome.",
  "SAFETY_LIVENESS_CLASS": "specification",
  "ABSTRACTION": "Abstraction preserves the phenomena and causal distinctions needed for the stakeholder decision.",
  "IMPLEMENTATION_CORRESPONDENCE": "Implementation outputs and observations implement the formal interface and are tied to deployed configuration.",
  "CHEAP_PATH": "For a purely internal algebraic transformation with an agreed mathematical contract, direct examples and peer review may suffice without a full world–machine model.",
  "MATURE_FORM": "A mechanically checked property controls a real engineering claim only when its variables, units, observations and outputs are traceable to stakeholder/world phenomena, its domain assumptions are independently supported, and a named operational or assurance consumer can interpret the result. Proof validity and requirement validity remain separate statuses.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P049; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to stakeholder/world-machine validation.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in A formal statement can be exact and fully proved yet encode the wrong stakeholder outcome, use unobservable variables, confuse a desired world condition with a software output, omit domain laws or validate only internal machine states. Precision (P001) is insufficient without meaning validation at the world–machine boundary..",
  "RELATION": "Implementation outputs and observations implement the formal interface and are tied to deployed configuration.",
  "SOUNDNESS_DUTY": "Abstraction preserves the phenomena and causal distinctions needed for the stakeholder decision.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "World-level validation cannot generally be reduced to deductive proof because physical and human environments are uncertain.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "A mechanically checked property controls a real engineering claim only when its variables, units, observations and outputs are traceable to stakeholder/world phenomena, its domain assumptions are independently supported, and a named operational or assurance consumer can interpret the result. Proof validity and requirement validity remain separate statuses.",
  "KNOWN_GAP": "The theorem proves an internal flag while the real-world condition remains unmet."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for stakeholder/world-machine validation.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For a purely internal algebraic transformation with an agreed mathematical contract, direct examples and peer review may suffice without a full world–machine model."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Stakeholder/world-machine validation may be enforced or assessed without an interactive theorem proof.",
  "PROOF_ESCALATION_TRIGGER": "Trigger when a formal claim represents an external outcome, safety/security objective, human workflow, physical process, sensor/actuator relation or AI-generated translation from stakeholder prose.",
  "CHEAPER_EVIDENCE": "For a purely internal algebraic transformation with an agreed mathematical contract, direct examples and peer review may suffice without a full world–machine model."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P049.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "Implementation outputs and observations implement the formal interface and are tied to deployed configuration.",
  "ENVIRONMENT_BOUNDARY": "Domain laws, sensors, actuators, humans and external systems are evidenced, monitored or clearly residual.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Requirement translators, units/data conversions and AI autoformalisation are untrusted unless independently checked.",
  "DRIFT_DETECTOR": "Changes in mission, domain assumptions, sensors, units or operational interpretation invalidate claim status even if proof replay succeeds.",
  "KNOWN_ESCAPE": "The theorem proves an internal flag while the real-world condition remains unmet."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "CONDITIONAL",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter stakeholder/world-machine validation.",
  "IDENTITIES_TO_BIND": "Changes in mission, domain assumptions, sensors, units or operational interpretation invalidate claim status even if proof replay succeeds.",
  "REPLAY_OR_RECHECK": "Requirement translators, units/data conversions and AI autoformalisation are untrusted unless independently checked.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Model stakeholders/mission, monitored and controlled phenomena, domain assumptions, machine interfaces and the causal/observational relation from machine behaviour to world outcome. Validate the formalisation with domain experts, scenarios, counterexamples, units/data provenance and operational measures; use independent or roundtrip translation challenge for generated formal claims.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "How should conflicting stakeholder goals and normative trade-offs be represented without pretending they are logical facts?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: The formal statement is traceable to the stakeholder/world claim and tested against representative interpretations.
- Abstraction: Abstraction preserves the phenomena and causal distinctions needed for the stakeholder decision.
- Environment: Domain laws, sensors, actuators, humans and external systems are evidenced, monitored or clearly residual.
- Model/code correspondence: Implementation outputs and observations implement the formal interface and are tied to deployed configuration.
- Trusted tools: Requirement translators, units/data conversions and AI autoformalisation are untrusted unless independently checked.
- Currentness/replay: Changes in mission, domain assumptions, sensors, units or operational interpretation invalidate claim status even if proof replay succeeds.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | Zave/Jackson, Parnas/Madey and goal-oriented requirements provide direct lineage for world–machine validation. | S081, S082, S083, S084 |
| FORMAL_SOUNDNESS_STRENGTH | LOW_AS_WORLD_VALIDATION | Logical soundness applies after formalisation; it cannot prove that stakeholder meaning or domain assumptions were selected correctly. | S081, S082 |
| MECHANICAL_REPLAY_STRENGTH | MEDIUM | Formal artefacts and examples replay, while domain interpretation and empirical evidence require renewed review/measurement. | S100, S102 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_HIGH_WHEN_ENGINEERED | Explicit monitored/controlled phenomena and operational traces can strongly link model and system, but do not eliminate physical uncertainty. | S083, S092 |
| INDUSTRIAL_CASE_STRENGTH | MEDIUM_HIGH | Aviation, verified systems and practitioner studies repeatedly expose requirement/environment validation needs. | S052, S092, S100 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Practitioner and 2026 translation studies give direct evidence; controlled world–machine validation comparisons remain limited. | S100, S101, S102 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_IN_ASSURANCE_DOMAINS | Requirements traceability and environmental assumptions are established assurance obligations. | S051, S052 |
| TRANSFERABILITY_STRENGTH | HIGH_FOR_EXTERNAL_CLAIMS | The property transfers broadly wherever software is intended to change or observe a world beyond itself. | S081, S084 |
| ASSUMPTION_SENSITIVITY | EXTREME | Stakeholder meaning, domain assumptions, sensor semantics and operational change dominate validity. | S082, S083 |
| CONTRARY_EVIDENCE_STRENGTH | VERY_HIGH | Fetzer-style execution criticism, empirical specification defects and autoformalisation fidelity gaps directly constrain the claim. | S056, S100, S101, S102 |

**CRITICISMS:**
- World-level validation cannot generally be reduced to deductive proof because physical and human environments are uncertain.
- Stakeholders disagree, requirements evolve and some goals are normative rather than factual.
- Executable examples can still share the same conceptual error as the formal statement.
- Roundtrip or cross-prover equivalence checks detect some translation drift but do not certify stakeholder intent [S101, S102].
- Domain validation can become expensive and bureaucratic if every local predicate requires a full goal model.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A mechanically checked property controls a real engineering claim only when its variables, units, observations and outputs are traceable to stakeholder/world phenomena, its domain assumptions are independently supported, and a named operational or assurance consumer can interpret the result. Proof validity and requirement validity remain separate statuses.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P001 — Precise property before proof, P044 — Proof eliminates testing. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P049 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while the theorem proves an internal flag while the real-world condition remains unmet?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P049?
- Would the cheap path — For a purely internal algebraic transformation with an agreed mathematical contract, direct examples and peer review may suffice without a full world–machine model — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P049, what decision changes, and should the artefact be retired if no live consumer remains?


### P050 — Domain-specific verified libraries/protocols

**PROPERTY_ID:** `P050`  
**PROPERTY_NAME:** Domain-specific verified libraries/protocols

**ENGINEERING_CLAIM_OR_FAILURE_MODE:** Verified crypto, kernels, compilers and protocol libraries are strong evidence for narrow claims under exact assumptions. It is intended to prevent: Many systems cannot afford end-to-end proof, but repeatedly depend on small high-consequence primitives. Reusing verified components can concentrate assurance effort—yet their guarantees are easily overextended beyond language subset, API contract, algorithm, side-channel model, hardware, build, configuration or usage domain.

**MATURE_FORM:** A reusable verified component is an assurance-bearing package: exact theorem/property set, API contract, supported configuration and targets, residual TCB/assumptions, source-to-binary provenance, integration tests and current replay. Downstream claims are limited to compositions that discharge its usage-domain obligations.

**TRIGGER:** Trigger for stable high-consequence components reused across products or serving as a narrow trusted computing base.

**CHEAP_PATH:** For low-risk, rapidly changing application glue, conventional types/tests/static analysis may outperform a reusable deep-proof investment.

**FORMAL_CLAIM_PROFILE:**
```json
{
  "PROPERTY": "Domain-specific verified libraries/protocols",
  "ENGINEERING_CLAIM": "Verified crypto, kernels, compilers and protocol libraries are strong evidence for narrow claims under exact assumptions.",
  "FORMAL_STATEMENT": "A target-system instantiation must state a falsifiable predicate, relation or temporal obligation embodying domain-specific verified libraries/protocols; notation is selected only after the claim class is known.",
  "ASSUMPTIONS": "Verified properties cover the component behaviour consumers actually rely on, including error and exceptional cases.",
  "ENVIRONMENT_MODEL": "Platform, calling context, entropy, clocks, memory, hardware and adversary/fault assumptions are discharged downstream.",
  "STATE_SPACE": "Only states, traces, values or artefact versions necessary to decide domain-specific verified libraries/protocols; excluded states must be declared.",
  "INITIAL_CONDITION": "The admitted starting states must not exclude the first known failure mode: A verified library is called outside its preconditions or with invalid state.",
  "TRANSITION_RELATION": "Transitions must expose the behaviour through which select a stable critical kernel/library; define exact functional/security/refinement properties and public api preconditions; verify implementation and, where warranted, compilation/binary correspondence; publish assumptions/tcb/usage domain; validate wrappers, ffi, build provenance and deployment configuration; maintain regression proofs and algorithm/version lifecycle.",
  "SAFETY_LIVENESS_CLASS": "domain specific",
  "ABSTRACTION": "Cryptographic, hardware, concurrency and leakage abstractions are explicit and justified for intended deployments.",
  "IMPLEMENTATION_CORRESPONDENCE": "The exact source/binary/configuration used by consumers corresponds to the verified artefact; wrappers and FFI are included or separately assured.",
  "CHEAP_PATH": "For low-risk, rapidly changing application glue, conventional types/tests/static analysis may outperform a reusable deep-proof investment.",
  "MATURE_FORM": "A reusable verified component is an assurance-bearing package: exact theorem/property set, API contract, supported configuration and targets, residual TCB/assumptions, source-to-binary provenance, integration tests and current replay. Downstream claims are limited to compositions that discharge its usage-domain obligations.",
  "PROFILE_SCOPE_NOTE": "This profile instantiates P050; it is not evidence that a target already satisfies the property."
}
```

**ABSTRACTION_REFINEMENT_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "CONCRETE_DOMAIN": "The target behaviour, artefact identities and environment relevant to domain-specific verified libraries/protocols.",
  "ABSTRACT_DOMAIN": "The smallest representation preserving the failure distinction in Many systems cannot afford end-to-end proof, but repeatedly depend on small high-consequence primitives. Reusing verified components can concentrate assurance effort—yet their guarantees are easily overextended beyond language subset, API contract, algorithm, side-channel model, hardware, build, configuration or usage domain..",
  "RELATION": "The exact source/binary/configuration used by consumers corresponds to the verified artefact; wrappers and FFI are included or separately assured.",
  "SOUNDNESS_DUTY": "Cryptographic, hardware, concurrency and leakage abstractions are explicit and justified for intended deployments.",
  "COMPLETENESS_OR_PRECISION_BOUNDARY": "Assurance is highly domain- and property-specific; reuse does not automatically transfer to a new environment.",
  "REFINEMENT_OR_VALIDATION_EVIDENCE": "A reusable verified component is an assurance-bearing package: exact theorem/property set, API contract, supported configuration and targets, residual TCB/assumptions, source-to-binary provenance, integration tests and current replay. Downstream claims are limited to compositions that discharge its usage-domain obligations.",
  "KNOWN_GAP": "A verified library is called outside its preconditions or with invalid state."
}
```

**MODEL_CHECKING_PROFILE:**
```json
{
  "APPLICABILITY": "NOT_PRIMARY",
  "RATIONALE": "Model checking is not the native evidence form for domain-specific verified libraries/protocols.",
  "POSSIBLE_SUPPORTING_USE": "A finite lifecycle, configuration or workflow state model may still challenge the property where the trigger is met.",
  "NON_TRIGGER": "For low-risk, rapidly changing application glue, conventional types/tests/static analysis may outperform a reusable deep-proof investment."
}
```

**PROOF_ENGINEERING_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT_OR_PLAUSIBLE",
  "THEOREM_OR_CERTIFICATE": "Verified crypto, kernels, compilers and protocol libraries are strong evidence for narrow claims under exact assumptions.",
  "ASSUMPTIONS_AND_AXIOMS": "Stable specification/API, proof-maintenance owner, supported targets/configurations, usage-domain declaration, integration and provenance pipeline.",
  "CHECKER_OR_KERNEL_BOUNDARY": "Compiler/extraction/linker/build and proof TCB are published and reduced with verified compilation/validation where warranted.",
  "PROOF_ARTEFACT": "A replayable derivation or independently checkable certificate tied to the exact statement and artefact versions for domain-specific verified libraries/protocols.",
  "DEPENDENCY_AND_CHANGE_IMPACT": "Proofs, algorithms, dependencies and supported usage domains replay and are reissued/retired after security or platform change.",
  "CORRESPONDENCE_DUTY": "The exact source/binary/configuration used by consumers corresponds to the verified artefact; wrappers and FFI are included or separately assured.",
  "MISUSE_TO_PREVENT": "Assurance is highly domain- and property-specific; reuse does not automatically transfer to a new environment."
}
```

**MODEL_CODE_CORRESPONDENCE_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "MODEL_IDENTITY": "Pin the specification/model version that instantiates P050.",
  "IMPLEMENTATION_IDENTITY": "Pin source, generated code, build inputs and deployed configuration whenever the claim crosses into implementation.",
  "CORRESPONDENCE_RELATION": "The exact source/binary/configuration used by consumers corresponds to the verified artefact; wrappers and FFI are included or separately assured.",
  "ENVIRONMENT_BOUNDARY": "Platform, calling context, entropy, clocks, memory, hardware and adversary/fault assumptions are discharged downstream.",
  "PROVENANCE_OR_BUILD_EVIDENCE": "Compiler/extraction/linker/build and proof TCB are published and reduced with verified compilation/validation where warranted.",
  "DRIFT_DETECTOR": "Proofs, algorithms, dependencies and supported usage domains replay and are reissued/retired after security or platform change.",
  "KNOWN_ESCAPE": "A verified library is called outside its preconditions or with invalid state."
}
```

**CURRENTNESS_REPLAY_PROFILE:**
```json
{
  "APPLICABILITY": "DIRECT",
  "INVALIDATION_EVENTS": "Any change to the claim, assumptions, model, source, generated artefact, proof/library dependency, checker/solver, build configuration, environment or consumer that can alter domain-specific verified libraries/protocols.",
  "IDENTITIES_TO_BIND": "Proofs, algorithms, dependencies and supported usage domains replay and are reissued/retired after security or platform change.",
  "REPLAY_OR_RECHECK": "Compiler/extraction/linker/build and proof TCB are published and reduced with verified compilation/validation where warranted.",
  "CHANGE_IMPACT_DUTY": "Demonstrate whether the change touches the mechanism: Select a stable critical kernel/library; define exact functional/security/refinement properties and public API preconditions; verify implementation and, where warranted, compilation/binary correspondence; publish assumptions/TCB/usage domain; validate wrappers, FFI, build provenance and deployment configuration; maintain regression proofs and algorithm/version lifecycle.",
  "RETIREMENT_RULE": "Mark evidence stale or retire it when identity/currentness cannot be established or no live decision consumes it.",
  "OPEN_CURRENTNESS_RISK": "Which composition certificates let downstream systems reuse component proofs safely?"
}
```

**REQUIRED_PRECONDITIONS:**
- Specification: Verified properties cover the component behaviour consumers actually rely on, including error and exceptional cases.
- Abstraction: Cryptographic, hardware, concurrency and leakage abstractions are explicit and justified for intended deployments.
- Environment: Platform, calling context, entropy, clocks, memory, hardware and adversary/fault assumptions are discharged downstream.
- Model/code correspondence: The exact source/binary/configuration used by consumers corresponds to the verified artefact; wrappers and FFI are included or separately assured.
- Trusted tools: Compiler/extraction/linker/build and proof TCB are published and reduced with verified compilation/validation where warranted.
- Currentness/replay: Proofs, algorithms, dependencies and supported usage domains replay and are reissued/retired after security or platform change.

**EVIDENCE_STRENGTH:**

| DIMENSION | RATING | PROPERTY-SPECIFIC BASIS | SOURCES |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | HIGH | CompCert, seL4 and verified crypto/TLS sources provide direct primary lineage. | S024, S025, S077, S078, S079, S080 |
| FORMAL_SOUNDNESS_STRENGTH | VERY_HIGH_FOR_STATED_PROPERTIES | Machine-checked functional/refinement/security theorems can be exceptionally strong within their models. | S024, S025, S077, S079 |
| MECHANICAL_REPLAY_STRENGTH | VERY_HIGH | Major projects provide replayable proof developments and generated artefacts. | S024, S025, S096 |
| MODEL_CODE_CORRESPONDENCE_STRENGTH | MEDIUM_TO_HIGH_WHEN_END_TO_END | Binary verification, verified compilation and integration evidence can be strong; wrappers/environment remain variable. | S026, S093, S094, S110 |
| INDUSTRIAL_CASE_STRENGTH | HIGH_BUT_SELECTED | Flagship compilers, kernels and cryptographic libraries show real deployment relevance, though selection bias remains. | S024, S025, S077, S078, S080 |
| EMPIRICAL_COMPARATIVE_STRENGTH | MEDIUM | Case evidence is strong; comparative defect/cost/maintenance evidence across ordinary alternatives is limited. | S062, S100 |
| CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH | HIGH_IN_REUSABLE_ASSURANCE_CONTEXTS | Usage-domain/configuration control is established in assurance guidance. | S113 |
| TRANSFERABILITY_STRENGTH | MEDIUM | The reusable-kernel pattern transfers; theorem content and integration obligations remain domain-specific. | S058, S113 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH | API use, platform, side channels, algorithms, build chain and configuration determine transfer. | S093, S094, S110 |
| CONTRARY_EVIDENCE_STRENGTH | HIGH | TCB analyses and explicit project assumptions materially narrow broad “verified component” marketing claims. | S093, S094 |

**CRITICISMS:**
- Assurance is highly domain- and property-specific; reuse does not automatically transfer to a new environment.
- Verified implementations can be slower, harder to integrate or dependent on specialised toolchains.
- The trusted base can include extraction, assemblers, linkers, hardware and external algorithms [S093, S094].
- Public industrial evidence is strongest for selected flagship projects, creating selection bias.
- Component proof does not establish system-level composition or usability/operability.

**ANTI_CEREMONY_BOUNDARY:** Do not adopt the named notation, proof count, certificate, model-checker run or review ritual as the property. Credit only the mature mechanism—A reusable verified component is an assurance-bearing package: exact theorem/property set, API contract, supported configuration and targets, residual TCB/assumptions, source-to-binary provenance, integration tests and current replay. Downstream claims are limited to compositions that discharge its usage-domain obligations.—when its preconditions and decision consumer are live.

**POSSIBLE_CONFLICTING_PROPERTY:** P033 — Verified compiler/toolchain scope, P042 — Cost/payoff trigger discipline. These are tensions or boundary checks, not instructions to discard either property.

**QUESTIONS_FOR_REPOSITORY_AUDIT:**
- What exact target-system claim would P050 control, and is it formal enough for a counterexample or failed check to discriminate acceptance from rejection?
- Could the target remain green while a verified library is called outside its preconditions or with invalid state?
- Which assumptions, environment states, source/model identities, tool versions and runtime configurations would invalidate evidence for P050?
- Would the cheap path — For low-risk, rapidly changing application glue, conventional types/tests/static analysis may outperform a reusable deep-proof investment — eliminate the same failure class with less modelling and maintenance cost?
- Who consumes the result of P050, what decision changes, and should the artefact be retired if no live consumer remains?


## Audit-use boundary

A crosswalk may conclude `NO_GENERAL_PROPERTY`, `NOT_TRIGGERED`, `CHEAP_PATH_SUFFICIENT`, `ASSUMPTION_SENSITIVE`, `CORRESPONDENCE_NOT_ESTABLISHED`, `STALE_EVIDENCE`, or `UNRESOLVED`. It must not convert source prestige, proof size, notation choice, certification labels or a green tool result into an adoption decision without the property-specific duties above. Questions in this intake deliberately remain unanswered.

EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_RESEARCH_STATE: FROZEN
PROPERTY_POPULATION_TOTAL: 50
PROPERTY_POPULATION_EXAMINED: 50
PROPERTY_COVERAGE: 50/50
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_AUDIT_INTAKE: COMPLETE
PUBLIC_DOCUMENTATION_INTAKE: COMPLETE
FROZEN_PACKET_PACKAGED: YES
EXTERNAL_RESEARCH_READY_FOR_REPOSITORY_CROSSWALK: YES
