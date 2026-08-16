# EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_FROZEN_REPORT

**Replacement freeze:** depth-repaired packet  
**Run date:** 2026-08-12  
**Analytical label:** `EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING`  
**Independence constraint:** no repository or sibling evolved packet was inspected or used.  
**Provisional source base:** retained and corrected; genealogy was preserved rather than restarted.  
**Denominator decision:** all 50 IDs retained; no evidence forced a split, merge or additional candidate.

## Executive synthesis

The replacement research supports the hypothesis that mature formal-methods engineering is not “prove everything”. It is the disciplined construction of a decision-relevant claim whose assumptions, state/trace semantics, abstraction, environment and governed artefact identity are explicit enough to challenge mechanically; selection of the cheapest sound method that can eliminate the material failure class; and maintenance of a live correspondence and trust chain from requirement through model/proof to code, binary, configuration and observation.

The strongest mechanically checked result remains conditional. Proof strength and engineering correspondence strength are deliberately partitioned: a theorem can be formally very strong while its specification, world translation, implementation relation or deployment assumptions remain weak. Conversely, a small executable invariant, finite model or certificate can be the mature form when it cheaply removes a recurring failure class and remains bound to a live consumer.

This replacement fixes the provisional packet’s central defect. Each property now has its own historical form, addressed problem, mechanism, failure modes, criticism, evolution, mature form, payoff, open questions and ten-dimensional evidence partition. No field is populated by a formal-methods-wide boilerplate template.

## Replacement-freeze finding

- `PROPERTY_POPULATION`: 50.
- `DENOMINATOR_CHANGE`: NONE.
- `SPLITS_FORCED_BY_EVIDENCE`: NONE.
- `MERGES_FORCED_BY_EVIDENCE`: NONE.
- `MISSING_CANDIDATES_FORCED_BY_EVIDENCE`: NONE.
- `PROFILE_DEPTH_REPAIR`: COMPLETE FOR 50/50.
- `SOURCE_TABLE`: 113 source records after retaining the provisional base, adding decision-relevant sources and correcting bibliographic defects found during re-audit.
- `CURRENT_2026_FRONTIER_RECHECK`: COMPLETE THROUGH 12 AUGUST 2026.

P029 (concurrency/distributed modelling), P030 (history/refinement correctness criteria) and P050 (reusable domain-specific verified components) remain separate because their claims, mechanisms and transfer conditions differ. P001 (formal precision) and P049 (stakeholder/world validity) remain separate because a statement can be precise without representing the intended world property. P021/P023/P048 remain separate because derivation replay, proof maintainability and active/stale evidence status are different lifecycle controls.

## Research and evidence method

The source standard prioritised primary formal papers and monographs, exact current tool/project scope, peer-reviewed industrial/empirical studies, authoritative assurance guidance and direct criticism. Search-result snippets were not used as evidence records. Each property’s evidence partition independently rates provenance, formal soundness, mechanical replay, model-code correspondence, industrial cases, empirical comparison, certification/domain practice, transferability, assumption sensitivity and contrary evidence. A high formal-soundness rating never raises correspondence or real-world support automatically.

## Evidence limits

The literature is much stronger at proving conditional formal results and documenting selected flagship systems than at controlled cross-project cost/benefit comparisons. Industrial adoption studies are heterogeneous and selection-prone. Current 2026 AI/formalisation results are benchmark and preprint evidence, not mature certification or broad field evidence. Runtime, physical, organisational and human environments remain only partially formal and observable. `UNRESOLVED` therefore survives where evidence cannot establish a general threshold or causal effect; this does not block the freeze.

## Current-state and 2026 frontier recheck

As of 12 August 2026, the decision-relevant frontier does not overturn the 50-property denominator; it sharpens assumption and evidence boundaries.

- Cross-prover AI translation is still low-yield and semantically fragile. ITPEval reports 29.1% statement pass@1 and 10.5% proof pass@1 across its evaluated translations, and its deterministic Lean equivalence check confirms only 54.0% of a selected set of native-verified source-to-Lean statement translations [S101]. This directly supports P040’s separation between type-checking and faithful translation.
- Roundtrip autoformalisation can improve formal equivalence substantially—45–61% initial equivalence to 83–85% after diagnosis-guided repair in the reported traffic-rule experiment—but formally self-consistent outputs still show semantic drift and the study is bounded to one statutory corpus and two models [S102].
- Proof currentness is an empirical engineering issue, not a hypothetical one: the Isabelle compatibility study collected 12,079 issues across four releases and classified causes and repairs [S095].
- Solver trust is moving toward independently checkable reconstruction and proof skeletons. Current work reconstructs cvc5/Alethe proofs in Isabelle and decomposes SMT evidence across preprocessing, clausification, SAT and theory reasoning rather than trusting only an UNSAT verdict [S108, S109].
- Focused bounded proof has measurable potential but not universal ROI. The unit-proof study created 73 proofs for four embedded operating systems and reported substantial recreated/new defect detection together with nontrivial development/execution cost and bounded generalisability [S107].
- Runtime verification remains observation-limited and cost-sensitive: current theory foregrounds finite-prefix knowledge and inconclusive verdicts, while empirical work shows instrumentation and event selection materially affect overhead [S099, S104].
- Concurrency verification increasingly has to name the exact memory model and reduction conditions; weak-memory formalisms and partial-order-reduction complexity prevent source-order interleaving or “optimal reduction” from being treated as free assumptions [S103, S106].
- Current industrial evidence remains heterogeneous. The Verum Dezyne study supplies a detailed modern case, while broader surveys still show domain, expertise, integration and organisational dependence rather than a universal adoption rule [S063, S064, S112].

The required canonical sections follow in the specified order.


## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_TIMELINE

| DATE | DEVELOPMENT | LINEAGE | SOURCES |
| --- | --- | --- | --- |
| 1967 | Floyd’s inductive assertions turn program correctness into assertions at control points and verification conditions. | PROGRAM_LOGIC_LINEAGE | S001 |
| 1969 | Hoare logic gives compositional axioms and rules for pre/postcondition reasoning. | PROGRAM_LOGIC_LINEAGE | S002 |
| 1975 | Dijkstra’s weakest-precondition calculus makes correctness obligations calculational and exposes termination/precondition structure. | PROGRAM_LOGIC_LINEAGE / REFINEMENT_LINEAGE | S003 |
| 1976 | Owicki–Gries addresses interference in parallel-program proofs; King formalises symbolic execution for path reasoning and test generation. | CONCURRENCY_PROCESS_ALGEBRA_LINEAGE / SMT_SAT_SYMBOLIC_LINEAGE | S087, S085 |
| 1977 | Cousot & Cousot establish abstract interpretation; Pnueli introduces temporal logic for ongoing computations. | STATIC_ANALYSIS_AND_ABSTRACT_INTERPRETATION_LINEAGE / TEMPORAL_LOGIC_LINEAGE | S005, S006 |
| 1978–1983 | VDM, Z/B precursors, algebraic specification, CSP/CCS and rely/guarantee diversify specification, refinement and concurrency reasoning. | FORMAL_SPECIFICATION_LINEAGE / REFINEMENT_LINEAGE / CONCURRENCY_PROCESS_ALGEBRA_LINEAGE | S013, S018, S019, S088 |
| 1985 | Alpern–Schneider gives the canonical safety/liveness decomposition; model checking foundations mature around temporal-state exploration. | TEMPORAL_LOGIC_LINEAGE / MODEL_CHECKING_LINEAGE | S086, S007 |
| 1989–1992 | Symbolic model checking uses BDDs to represent very large finite state sets and transitions. | MODEL_CHECKING_LINEAGE | S008 |
| 1990 | Linearizability defines a local concurrent-object correctness relation; database serialisability already provides a distinct transaction-history criterion. | CONCURRENCY_PROCESS_ALGEBRA_LINEAGE / DOMAIN_SPECIFIC | S090, S091 |
| 1993–1997 | SPIN operationalises explicit-state protocol checking and partial-order reduction; Larch, Z, B and VDM tool ecosystems mature. | MODEL_CHECKING_LINEAGE / FORMAL_SPECIFICATION_LINEAGE | S009, S010, S012, S014 |
| 1994 | Behavioural subtyping connects interface substitution to semantic pre/post/history obligations. | TYPE_SYSTEM_AND_DEPENDENT_TYPE_LINEAGE / CONTRACT_COMPOSITION | S089 |
| 1996–1998 | Lightweight formal methods, Alloy-style bounded analysis, proof-carrying code and translation validation shift attention to focused, consumer-checkable evidence. | LIGHTWEIGHT_FORMAL_METHODS_LINEAGE / VERIFIED_TOOLCHAIN_LINEAGE | S015, S016, S022, S023 |
| 1997–2001 | Separation logic, CEGAR and bounded model checking address local heap reasoning, abstraction refinement and SAT-backed finite-depth search. | PROGRAM_LOGIC_LINEAGE / MODEL_CHECKING_LINEAGE / SMT_SAT_SYMBOLIC_LINEAGE | S048, S061, S036 |
| 2002–2008 | SMT solving, hyperproperties, modern symbolic execution and richer type/refinement systems broaden mechanically checkable claim classes. | SMT_SAT_SYMBOLIC_LINEAGE / TYPE_SYSTEM_AND_DEPENDENT_TYPE_LINEAGE | S021, S034, S038, S047 |
| 2009 | CompCert and seL4 demonstrate large machine-checked semantic-preservation and kernel-functional-correctness results with explicit residual assumptions. | VERIFIED_TOOLCHAIN_LINEAGE / THEOREM_PROVING_LINEAGE | S024, S025, S093, S094 |
| 2014–2017 | TLA+ industrial reports, Verdi/IronFleet and other distributed verification show design and implementation gains; empirical defect analysis exposes model/code/shim/environment gaps. | DOMAIN_SPECIFIC / HYBRID | S029–S031, S092 |
| 2015–2019 | Crash-safety logics, certified abstraction layers, runtime-verification surveys and proof-engineering research emphasise recovery, composition, monitoring and maintainability. | THEOREM_PROVING_LINEAGE / RUNTIME_VERIFICATION_LINEAGE / HYBRID | S027, S028, S066, S068, S096 |
| 2020–2022 | Expert/industry surveys and solver fuzzing clarify selective adoption and trusted-tool defects; CompCert TCB analysis narrows verified-compiler marketing. | CONVERGENT_ENGINEERING / VERIFIED_TOOLCHAIN_LINEAGE | S063, S064, S097, S094 |
| 2024 | Current work validates verifier front-end translations with certificates, measures runtime-monitor overhead, and automates substantial distributed-liveness obligations while preserving assumptions. | VERIFIED_TOOLCHAIN_LINEAGE / RUNTIME_VERIFICATION_LINEAGE / DOMAIN_SPECIFIC | S098, S104, S105 |
| 2025 | Proof-version compatibility, focused unit proofs, partial-order-reduction complexity and a detailed industrial case sharpen maintenance, cost and applicability limits. | THEOREM_PROVING_LINEAGE / LIGHTWEIGHT_FORMAL_METHODS_LINEAGE / MODEL_CHECKING_LINEAGE | S095, S103, S107, S112 |
| 2026 | Runtime-verification uncertainty, weak-memory survey work, repository-scale Lean benchmarks, cross-prover translation tests, roundtrip autoformalisation and SMT proof skeletons define the current frontier. | HYBRID / CURRENT_FRONTIER | S099, S101, S102, S106, S109, S111 |

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_GENEALOGY

The genealogy is plural. No single notation or prover owns the retained property set.

- `PROGRAM_LOGIC_LINEAGE`: Floyd assertions, Hoare triples, weakest preconditions, separation logic and concurrent program logics establish local proof obligations, induction over program structure and ownership/interference control [S001–S003, S048, S049, S087, S088].
- `FORMAL_SPECIFICATION_LINEAGE`: VDM, Z, B/Event-B, Larch and algebraic/abstract-data-type traditions establish explicit state, operations, invariants, schemas, abstract machines and model validation [S010–S014].
- `REFINEMENT_LINEAGE`: data refinement, simulation, refinement calculus and certified abstraction layers establish that correctness can be transported only through an explicit relation between levels [S010, S011, S017, S027, S030].
- `TEMPORAL_LOGIC_LINEAGE`: Pnueli, safety/liveness theory and TLA distinguish invariance, eventuality, fairness and stuttering-sensitive/insensitive behaviour [S006, S017, S086].
- `MODEL_CHECKING_LINEAGE`: explicit-state, symbolic, bounded and abstraction-refinement methods establish exhaustive or systematic counterexample search over a disclosed formal state space [S007–S009, S036, S061].
- `THEOREM_PROVING_LINEAGE`: LCF/HOL, Isabelle, Coq/Rocq, PVS/ACL2 and large proof engineering establish replayable derivations, small kernels, explicit axioms and maintainable proof architectures [S042–S044, S096].
- `STATIC_ANALYSIS_AND_ABSTRACT_INTERPRETATION_LINEAGE`: lattice fixpoints, sound over-approximation, widening/narrowing and production analysers establish scalable class-specific guarantees with false-positive and modelling trade-offs [S005, S032, S033].
- `SMT_SAT_SYMBOLIC_LINEAGE`: SAT, SMT, bounded model checking, symbolic execution and solver certificates establish high automation over encoded theories and paths while exposing encoding, bound, path and solver-trust boundaries [S034–S041, S085, S097, S108, S109].
- `TYPE_SYSTEM_AND_DEPENDENT_TYPE_LINEAGE`: propositions-as-types, refinement/dependent types, ownership, typestate and behavioural subtyping establish compositional exclusion of precisely stated error classes [S045–S047, S089].
- `CONCURRENCY_PROCESS_ALGEBRA_LINEAGE`: CSP, CCS, rely/guarantee, linearizability, serialisability and weak-memory formalisms establish history-, interference- and memory-model-specific correctness notions [S018, S019, S088–S091, S106].
- `RUNTIME_VERIFICATION_LINEAGE`: assertion and trace monitoring establishes online evidence over observed finite executions, with monitorability, observability and overhead constraints [S066–S068, S099, S104].
- `VERIFIED_TOOLCHAIN_LINEAGE`: proof-carrying code, translation validation, verified compilers, kernels and certificate reconstruction establish consumer-checkable evidence across transformation boundaries [S022–S026, S094, S098, S108, S109].
- `LIGHTWEIGHT_FORMAL_METHODS_LINEAGE`: focused modelling, bounded model finding, executable contracts and unit proofs establish that partial formalisation can be mature when its claim and scope are explicit [S015, S016, S037, S107].
- `DOMAIN_SPECIFIC`: hardware, cryptography, kernels, compilers, databases and distributed protocols retain stronger local traditions whose assumptions and payoff do not automatically transfer [S024–S031, S077–S080, S090–S093].
- `HYBRID` and `CONVERGENT_ENGINEERING`: proof plus testing, runtime evidence, configuration control, requirements validation and certification evolved through multiple traditions. Similarity is not treated as documentary transmission unless sources establish it [S051–S054, S081–S084, S092, S100].

## FORMAL_VERIFICATION_VS_FORMALITY_CARICATURE

| CARICATURE | EVIDENCE-BASED CORRECTION | PROPERTY IDS |
| --- | --- | --- |
| “Formal verification proves the software is correct.” | It proves a formal statement under explicit semantics and assumptions; implementation and environment correspondence remain separate. | P001–P003, P015, P049 |
| “Model checking explores every possible real-world behaviour.” | It explores the disclosed finite/symbolic model, bounds and reductions—not omitted world behaviour. | P016–P020, P045 |
| “Theorem proving eliminates testing.” | Proof can subsume exact test objectives, but testing still challenges requirements, integration, tools and environment. | P036, P044 |
| “A proof assistant cannot be wrong.” | Small kernels reduce trust; axioms, implementation, parsers, solvers, extraction, hardware and statement meaning remain. | P022, P047 |
| “If the specification is precise, it is correct.” | Precision is necessary for checking, not sufficient for stakeholder/world validity. | P001, P049 |
| “More invariants mean stronger verification.” | Only meaningful, sufficiently strong, inductive and correspondence-relevant invariants add assurance. | P005, P006, P020 |
| “No counterexample means deployment is safe.” | The conclusion is bounded by model, search depth, abstraction, property, code and environment. | P018, P045 |
| “Formal methods are always too expensive.” | Cost is claim-, domain-, reuse- and change-specific; focused checks can be cheap while deep proof can be costly. | P037, P042 |
| “Lightweight formal methods are incomplete formal methods.” | They are mature when a bounded claim is decision-sufficient and scope is disclosed. | P037 |
| “Type safety means functional correctness.” | A type theorem excludes only the encoded error class under its soundness boundary. | P027, P028, P046 |
| “A verified compiler makes the whole system verified.” | It preserves defined source semantics for supported programs/targets; source correctness, build provenance and runtime remain. | P033, P034, P050 |
| “AI-generated proof makes the AI-generated claim trustworthy.” | Kernel checking filters invalid proof terms; translation fidelity and engineering meaning need independent validation. | P040 |

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PROPERTY_LEDGER

### P001 — Precise property before proof

**CURRENT_STATUS:** `SPECIFICATION_PROPERTY`  
**LINEAGE_CLASS:** `PROGRAM_LOGIC_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `specification`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** program logic / assertion lineage

**ORIGINAL_FORM:** Floyd’s 1967 inductive assertions and Hoare’s 1969 triples made a program claim a predicate over explicitly identified program points or a relation between pre-state and post-state. Z/VDM/B later moved this precision into state-and-operation specifications, while requirements work by Zave, Jackson, Parnas and van Lamsweerde made clear that the formal object must also represent a world-level requirement rather than merely a program-level predicate [S001, S002, S010–S013, S081–S084].

**PROBLEM_IT_ADDRESSED:** Informal acceptance claims such as “the protocol is safe” or “the function is correct” do not identify the bad behaviours, initial states, outputs, timing conditions or observers that a checker must discriminate. Without a claim precise enough to be false, proof activity can optimise notation and tactics while leaving the engineering decision undefined.

**ENGINEERING_CLAIM:** A claim must be formal enough to distinguish conforming from non-conforming behaviours before proof or checking is meaningful.

**MECHANISM:** Construct a versioned formal-claim profile that links the engineering claim to a typed formal statement, examples and anti-examples, assumptions, environment and failure model, property class, model scope, implementation correspondence and named decision consumer. Check satisfiability, witness behaviours, non-vacuity and expected edge cases before investing in proof.

**TRIGGER_OR_CONTEXT:** Trigger before any mechanically checked claim that will control a consequential decision, especially where prose admits multiple interpretations or generated formalisation is used.

**NON_TRIGGER_OR_CHEAP_PATH:** For a local deterministic rule, use a typed assertion, truth table, executable example set or property-based test if it provides the needed discrimination more cheaply than a separate specification language.

**DEPENDENCIES_OR_PRECONDITIONS:** A named decision, identified stakeholders/mission, domain vocabulary, representative good/bad cases, and ownership of requirement changes.

**SPECIFICATION_PRECONDITIONS:** The formula must be satisfiable, nontrivial, typed/unit-consistent, explicit about undefined and exceptional cases, and traceable to the engineering claim.

**ABSTRACTION_PRECONDITIONS:** Any omitted detail must be shown irrelevant to the claim or recorded as a scope limit.

**ENVIRONMENT_PRECONDITIONS:** World phenomena and controllable/observable interfaces needed for the claim must be stated rather than silently treated as program variables.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Not established by this property; the claim package must say whether it governs a design model, source, binary, configuration or observed runtime.

**TRUSTED_TOOL_PRECONDITIONS:** Parsers, translators and generated-formula pipelines that can alter the statement belong in the trusted or independently checked boundary.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Requirement and formal-statement identities must change together; replay alone is insufficient if the engineering meaning changed.

**KNOWN_FAILURE_MODES:**
- A precise formula formalises a convenient surrogate rather than the stakeholder requirement.
- The statement omits exceptional, undefined, quantitative or environmental behaviour.
- A theorem is strengthened or weakened to fit automation without recording the changed engineering meaning.
- Examples used to validate the translation are leaked into generated specifications or benchmarks.
- The formal statement is current but the prose requirement or operational mission has changed.

**IMPORTANT_CRITICISMS:**
- Fetzer’s program/execution distinction and world–machine requirements analysis show that formal precision is not semantic validity [S056, S081, S082].
- Vacuity research shows that even a syntactically substantive formula may hold for an irrelevant reason [S059, S060].
- Dafny practitioner evidence reports specification errors that testing or review can reveal although verification succeeds [S100].
- Current autoformalisation work shows that a type-correct translated statement can differ semantically from its source [S101, S102].

**HOW_THE_PROPERTY_EVOLVED:** The property evolved from assertion placement and total/partial correctness predicates into plural claim forms: temporal formulas, refinement relations, hyperproperties, probabilistic or timed properties, monitorable trace properties and certificate policies. Modern practice adds requirement-to-formula traceability, satisfiability/vacuity checks, executable examples, mutation or countermodel challenge, and independent translation validation for machine- or AI-generated specifications.

**MATURE_OR_EVOLVED_FORM:** No proof campaign begins from a slogan. The accepted object is a reviewable, versioned claim package whose formal statement discriminates material behaviours, whose translation has been challenged by positive and negative examples, and whose scope, assumptions and consumer are explicit. Mechanical proof then answers that exact claim—nothing broader.

**EXPECTED_ENGINEERING_PAYOFF:** Avoids the highest-cost formal-methods failure: expending proof effort on a statement that cannot support the intended release, safety, security or design decision. It also exposes disagreements early, enables cheaper counterexample search, and makes later theorem changes auditable.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which empirical techniques best detect semantically weak but satisfiable formal requirements before proof?
- How much independent review or roundtrip equivalence is sufficient for AI-generated engineering specifications?
- How should quantitative and human/physical requirements be linked to deterministic formal predicates without false precision?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S001, S002, S010, S012, S081, S084, S013, S011, S082, S083  
**CRITICAL_SOURCES:** S055, S056, S059, S060, S092, S100, S101, S102, S081, S082  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S029, S052, S054, S100, S051  
**CONTRARY_EVIDENCE:** S055, S056, S059, S060, S092, S100, S101, S102

**SOURCE IDENTITIES USED:**
- S001: Robert W. Floyd, *Assigning Meanings to Programs* (1967)
- S002: C. A. R. Hoare, *An Axiomatic Basis for Computer Programming* (1969)
- S010: Jean-Raymond Abrial, *The B-Book: Assigning Programs to Meanings* (1996)
- S012: J. M. Spivey, *The Z Notation: A Reference Manual* (1992, 2nd ed.)
- S081: Pamela Zave and Michael Jackson, *Four Dark Corners of Requirements Engineering* (1997)
- S084: Axel van Lamsweerde, *Formal Specification: A Roadmap* (2000)
- S013: Dines Bjørner and Cliff B. Jones, eds., *The Vienna Development Method: The Meta-Language* (1978)
- S011: Jean-Raymond Abrial, *Modeling in Event-B: System and Software Engineering* (2010)
- S082: Michael Jackson, *The World and the Machine* (1995/1997 lineage)
- S083: David L. Parnas and Jan Madey, *Functional Documents for Computer Systems* (1995)
- S055: Richard A. De Millo, Richard J. Lipton, and Alan J. Perlis, *Social Processes and Proofs of Theorems and Programs* (1979)
- S056: James H. Fetzer, *Program Verification: The Very Idea* (1988)
- S059: Ilan Beer et al., *Efficient Detection of Vacuity in ACTL Formulas* (1997)
- S060: Orna Kupferman and Moshe Y. Vardi, *Vacuity Detection in Temporal Model Checking* (2003)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S100: Eric Mugnier, Yuanyuan Zhou, Ranjit Jhala, and Michael Coblenz, *On the Impact of Formal Verification on Software Development* (2025)
- S101: Jiayi Wu, Robert Joseph George, and Anima Anandkumar, *ITPEval: Benchmarking Formal Translation Across Interactive Theorem Provers* (2026, v1)
- S102: Daneshvar Amrollahi, Jerry Lopez, and Clark Barrett, *Faithful Autoformalization via Roundtrip Verification and Repair* (2026, v1)
- S029: Chris Newcombe et al., *How Amazon Web Services Uses Formal Methods* (2015)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)
- S051: Federal Aviation Administration, *AC 20-115D: Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178* (2017)


### P002 — Explicit assumptions and preconditions

**CURRENT_STATUS:** `STRONGLY_RETAINED`  
**LINEAGE_CLASS:** `PROGRAM_LOGIC_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `strongly retained`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** program logic / assertion lineage

**ORIGINAL_FORM:** Hoare triples exposed preconditions; Dijkstra made weakest preconditions calculational; temporal and refinement systems added initial-state, fairness and invariant assumptions. Later assurance cases and verified systems began publishing axioms, hardware models, fault models and proof assumptions as first-class scope [S002, S003, S006, S017, S025, S052, S093].

**PROBLEM_IT_ADDRESSED:** A result can be mathematically valid yet irrelevant or vacuous because the failing case is excluded by a hidden precondition, an inconsistent axiom set, an unreachable initial state, an idealised scheduler or a fault model that deployment does not satisfy.

**ENGINEERING_CLAIM:** Every formal result must expose assumptions, axioms, preconditions, initial states and accepted fault/environment models.

**MECHANISM:** Maintain an assumption register attached to each theorem/model run: logical axioms, type/units, preconditions, initial-state predicate, rely/fairness conditions, failure semantics, hardware/runtime conditions and configuration. Check consistency and satisfiability, generate witnesses for initial states, instrument testable assumptions, and require downstream consumers to discharge or accept each assumption.

**TRIGGER_OR_CONTEXT:** Trigger for every theorem, model-check result, static-analysis claim, certificate or monitor verdict that will be consumed outside the immediate authoring context.

**NON_TRIGGER_OR_CHEAP_PATH:** For a trivial local check, encode the precondition directly in the function type/assertion and test the rejection path; do not create a separate assumption bureaucracy.

**DEPENDENCIES_OR_PRECONDITIONS:** An identified claim owner, access to tool/library configuration, environment/fault-domain knowledge, and a method to test assumption consistency.

**SPECIFICATION_PRECONDITIONS:** Assumptions must be separated from guarantees and must not make the initial condition empty or the desired behaviour impossible to violate.

**ABSTRACTION_PRECONDITIONS:** Assumptions introduced solely to make an abstraction tractable must be labelled and justified against omitted behaviours.

**ENVIRONMENT_PRECONDITIONS:** Scheduler, network, hardware, clock, user and operator premises need evidence or explicit residual-risk acceptance.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Code/configuration must satisfy input domains, memory models, build options and shims presupposed by the result.

**TRUSTED_TOOL_PRECONDITIONS:** Imported axioms, oracle calls, admitted lemmas, unsafe extensions and solver semantics must be enumerated.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Assumption changes invalidate the engineering claim even when theorem text and proof term replay unchanged.

**KNOWN_FAILURE_MODES:**
- Assumptions are scattered across code, tactics, library imports and prose rather than enumerated.
- A precondition excludes precisely the input or fault that motivates assurance.
- Assumption sets are mutually inconsistent, making arbitrary conclusions possible.
- A fairness or retry premise is mathematically explicit but operationally unenforced.
- Library axioms or unsafe proof-assistant features enter transitively without review.
- A reused component is deployed outside its certified usage domain.

**IMPORTANT_CRITICISMS:**
- Vacuity and inconsistent-environment cases can make a property pass without exercising its subject [S059, S060].
- seL4 and CompCert analyses show that strong proofs still depend on hardware, semantics, low-level code, axioms or external algorithms [S093, S094].
- Verified distributed-system defects often arose where implementation or environment violated proof assumptions [S092].
- Certification documents can make assumptions visible yet still rely on organisational discipline to enforce them [S052, S113].

**HOW_THE_PROPERTY_EVOLVED:** What began as a precondition on a procedure evolved into assumption/guarantee contracts, environment and fault models, trusted-computing-base declarations, certified usage domains and machine-readable proof manifests. Mature practice distinguishes assumptions proved internally, checked at integration, monitored at runtime, supplied by certification evidence, and merely accepted as residual risk.

**MATURE_OR_EVOLVED_FORM:** Every formal result carries a complete, versioned assumption set with satisfiability evidence and an owner/discharge mode for each item. Hidden defaults, imported axioms and environmental premises are surfaced; assumptions that can be enforced or monitored become executable obligations; results are downgraded when deployment cannot establish them.

**EXPECTED_ENGINEERING_PAYOFF:** Prevents vacuous or out-of-domain assurance, directs tests and reviews toward the residual trusted boundary, and lets decision makers compare two proofs by what they assume rather than by proof size or tool brand.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can large proof developments expose transitive axioms and semantic defaults in a reviewer-usable form?
- Which environmental assumptions are economically monitorable rather than merely documented?
- How should assurance degrade when an assumption is probabilistic or only partially observable?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S002, S003, S006, S010, S052, S044, S093, S094, S017, S025  
**CRITICAL_SOURCES:** S059, S060, S092, S093, S094, S052, S113  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S025, S030, S031, S052, S093, S110, S113  
**CONTRARY_EVIDENCE:** S059, S060, S092, S093, S094

**SOURCE IDENTITIES USED:**
- S002: C. A. R. Hoare, *An Axiomatic Basis for Computer Programming* (1969)
- S003: Edsger W. Dijkstra, *Guarded Commands, Nondeterminacy and Formal Derivation of Programs* (1975)
- S006: Amir Pnueli, *The Temporal Logic of Programs* (1977)
- S010: Jean-Raymond Abrial, *The B-Book: Assigning Programs to Meanings* (1996)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S044: Tobias Nipkow, Lawrence C. Paulson, and Markus Wenzel, *Isabelle/HOL: A Proof Assistant for Higher-Order Logic* (2002)
- S093: seL4 Project, *What the Proofs Assume* (current site, accessed 2026-08-12)
- S094: David Monniaux and Sylvain Boulmé, *The Trusted Computing Base of the CompCert Verified Compiler* (2022)
- S017: Leslie Lamport, *The Temporal Logic of Actions* (1994)
- S025: Gerwin Klein et al., *seL4: Formal Verification of an OS Kernel* (2009)
- S059: Ilan Beer et al., *Efficient Detection of Vacuity in ACTL Formulas* (1997)
- S060: Orna Kupferman and Moshe Y. Vardi, *Vacuity Detection in Temporal Model Checking* (2003)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S113: Federal Aviation Administration, *AC 20-148: Reusable Software Components* (current guidance lineage, accessed 2026-08-12)
- S030: Chris Hawblitzel et al., *IronFleet: Proving Practical Distributed Systems Correct* (2015)
- S031: James R. Wilcox et al., *Verdi: A Framework for Implementing and Formally Verifying Distributed Systems* (2015)
- S110: CompCert project, *CompCert C Reference Manual* (current manual, accessed 2026-08-12)


### P003 — Environment model boundary

**CURRENT_STATUS:** `ASSUMPTION_SENSITIVE`  
**LINEAGE_CLASS:** `CONVERGENT_ENGINEERING`  
**FORMAL_PROPERTY_CLASS:** `assumption sensitive`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** convergent engineering property

**ORIGINAL_FORM:** Early program logics treated an abstract machine state as the universe. Requirements engineering later separated the machine from the world, while reactive, distributed, runtime and verified-kernel work introduced explicit environment actions, oracles, devices, networks and observation boundaries [S006, S017, S066, S068, S081, S082, S093].

**PROBLEM_IT_ADDRESSED:** Software correctness claims routinely fail at the boundary the model did not include: hardware timing, DMA, weak memory, network loss, clocks, operator action, physical sensing, deployment configuration or unobserved external state.

**ENGINEERING_CLAIM:** A proof or model is an engineering claim only relative to a declared boundary between system, implementation, and environment.

**MECHANISM:** Define the system/environment cut, controlled and monitored variables, admissible environment transitions, faults, timing and observation model. Classify each external phenomenon as modelled, assumed, monitored, tested, independently assured or out of scope; then connect the formal guarantee to that boundary rather than to an undefined “system”.

**TRIGGER_OR_CONTEXT:** Trigger whenever the property depends on networks, clocks, devices, hardware, users, physical processes, external services or any component outside the verified artefact.

**NON_TRIGGER_OR_CHEAP_PATH:** For a pure deterministic transformation over fully controlled values, document the input domain and use ordinary pre/postconditions; a separate environment model may add little.

**DEPENDENCIES_OR_PRECONDITIONS:** System context, interfaces, fault model, observability map, platform/configuration identity and owners for external assumptions.

**SPECIFICATION_PRECONDITIONS:** The engineering claim must say whether it concerns abstract design behaviour, source execution, binary execution or world outcomes.

**ABSTRACTION_PRECONDITIONS:** Environment abstraction must over-approximate relevant hostile/fault behaviours for universal claims or disclose under-approximation.

**ENVIRONMENT_PRECONDITIONS:** All material external phenomena are classified and evidence-backed; “the environment behaves” is not an admissible premise.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Adapters, drivers, shims and deployment configuration crossing the boundary require conformance evidence.

**TRUSTED_TOOL_PRECONDITIONS:** Simulation/emulation, trace collection and model extraction tools that encode environment behaviour are in scope.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Platform, device, network policy, scheduler and service-version changes can invalidate the boundary even with unchanged source.

**KNOWN_FAILURE_MODES:**
- The environment is represented as nondeterministic input but important physical constraints or adversarial behaviours are absent.
- The model assumes reliable clocks, messages, storage or schedulers that deployment does not provide.
- Hardware memory/DMA behaviour violates the abstract machine model.
- A monitor cannot observe events needed to decide the property.
- Human or operational actions are treated as impossible rather than as environmental transitions.
- The boundary shifts during integration without invalidating the formal claim.

**IMPORTANT_CRITICISMS:**
- Fetzer and world–machine analysis reject the inference from abstract program theorem to physical execution [S056, S082].
- seL4 explicitly excludes or assumes DMA, side channels, low-level code and hardware properties depending on proof [S093].
- Empirical study of verified distributed systems found failures in unverified interfaces, shims and assumptions [S092].
- Runtime-verification theory emphasises finite-prefix and partial-observation uncertainty [S099].

**HOW_THE_PROPERTY_EVOLVED:** The property moved from implicit machine semantics to open-system models, rely/guarantee conditions, explicit fault and network semantics, hardware memory models, environment contracts and runtime observation models. The evolved form does not demand a complete world model; it demands a justified boundary and complementary evidence for what remains outside.

**MATURE_OR_EVOLVED_FORM:** A formal claim identifies exactly which world phenomena are represented and which are assumed. Environment behaviours with material decision impact are either modelled adversarially, enforced by architecture, tested under representative conditions, monitored online, or accepted as named residual risk. Scope changes trigger re-analysis.

**EXPECTED_ENGINEERING_PAYOFF:** Prevents an in-model proof from being sold as a deployment guarantee, concentrates empirical testing on the unproved boundary, and exposes integration hazards before certification or release.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can environment models remain tractable without excluding correlated or rare failure modes?
- What evidence is sufficient to justify a physical/hardware assumption that cannot itself be proved in the software logic?
- How should monitor uncertainty be represented in acceptance decisions for partially observable systems?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S006, S017, S081, S082, S093, S056, S066, S068  
**CRITICAL_SOURCES:** S056, S092, S093, S099, S082  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S025, S028, S029, S030, S093, S052, S113  
**CONTRARY_EVIDENCE:** S056, S092, S093, S099

**SOURCE IDENTITIES USED:**
- S006: Amir Pnueli, *The Temporal Logic of Programs* (1977)
- S017: Leslie Lamport, *The Temporal Logic of Actions* (1994)
- S081: Pamela Zave and Michael Jackson, *Four Dark Corners of Requirements Engineering* (1997)
- S082: Michael Jackson, *The World and the Machine* (1995/1997 lineage)
- S093: seL4 Project, *What the Proofs Assume* (current site, accessed 2026-08-12)
- S056: James H. Fetzer, *Program Verification: The Very Idea* (1988)
- S066: Martin Leucker and Christian Schallhart, *A Brief Account of Runtime Verification* (2009)
- S068: Adrian Francalanza, Jorge A. Pérez, and César Sánchez, *Runtime Verification for Decentralised and Distributed Systems* (2018)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S099: Benedikt Bollig, *Runtime Verification: Monitoring, Knowledge, and Uncertainty* (2026, v1)
- S025: Gerwin Klein et al., *seL4: Formal Verification of an OS Kernel* (2009)
- S028: Haogang Chen et al., *Using Crash Hoare Logic for Certifying the FSCQ File System* (2015)
- S029: Chris Newcombe et al., *How Amazon Web Services Uses Formal Methods* (2015)
- S030: Chris Hawblitzel et al., *IronFleet: Proving Practical Distributed Systems Correct* (2015)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S113: Federal Aviation Administration, *AC 20-148: Reusable Software Components* (current guidance lineage, accessed 2026-08-12)


### P004 — Explicit state and transition model

**CURRENT_STATUS:** `STRONGLY_RETAINED`  
**LINEAGE_CLASS:** `MODEL_CHECKING_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `strongly retained`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** model checking lineage

**ORIGINAL_FORM:** Floyd’s flowchart points, operational semantics, automata and Statecharts represented behaviour as configurations linked by steps; temporal-logic and model-checking traditions made an initial-state set and transition relation the object explored or proved [S001, S006–S009, S017, S020].

**PROBLEM_IT_ADDRESSED:** Ordering, retry, lifecycle and concurrency defects cannot be expressed adequately as static input/output prose. Reviews miss illegal intermediate states, unexpected transition sequences, dead ends and races because the reachable-state structure is implicit.

**ENGINEERING_CLAIM:** Dynamic behaviour should be represented as states, initial conditions and transitions when failures are ordering/state dependent.

**MECHANISM:** Define typed state variables, initial states, atomic actions/transitions, enabling conditions and nondeterminism. Execute, simulate, enumerate or prove over the transition system; generate traces for forbidden states, deadlocks and temporal obligations; link actions to implementation events where needed.

**TRIGGER_OR_CONTEXT:** Trigger for protocols, workflows, lifecycle controllers, distributed coordination, recovery logic, device modes and any defect depending on event order.

**NON_TRIGGER_OR_CHEAP_PATH:** For a stateless pure function, a pre/postcondition or property-based test is usually cheaper and more direct.

**DEPENDENCIES_OR_PRECONDITIONS:** A bounded vocabulary of state, events and atomic actions plus representative failure/recovery scenarios.

**SPECIFICATION_PRECONDITIONS:** Initial and transition predicates must be satisfiable and include error/exception paths relevant to acceptance.

**ABSTRACTION_PRECONDITIONS:** Merged states and atomic steps preserve the temporal/invariant distinctions being checked.

**ENVIRONMENT_PRECONDITIONS:** External events and scheduling choices are explicit transitions or declared assumptions.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Each material model action maps to code/API/runtime events with compatible atomicity and data domains.

**TRUSTED_TOOL_PRECONDITIONS:** Parser, simulator/model checker and any model extractor must preserve declared semantics.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Event/state schema changes, protocol version changes and implementation refactors trigger model replay and mapping review.

**KNOWN_FAILURE_MODES:**
- State variables omit history or environmental facts needed for the property.
- Atomic transitions hide interleavings that exist in code.
- Initial-state predicate excludes recovery, upgrade or malformed states.
- Nondeterminism is accidentally resolved by modelling convenience.
- Hierarchy or symmetry merges states that differ for the claim.
- The model becomes a decorative diagram with no executable or proof semantics.

**IMPORTANT_CRITICISMS:**
- Finite or abstract state models can be complete for their own transition relation while incomplete for deployment [S045, S056].
- State explosion makes naïve enumeration infeasible [S008, S019].
- A clean model may not correspond to implementation atomicity or weak-memory behaviour [S092, S106].

**HOW_THE_PROPERTY_EVOLVED:** Flat flowcharts and automata evolved into hierarchical statecharts, labelled transition systems, action-based temporal specifications, symbolic transition relations, process calculi and code-extracted models. Modern use favours the smallest executable transition model that exposes the failure class, with explicit atomicity and correspondence obligations.

**MATURE_OR_EVOLVED_FORM:** Use a state/transition representation when the risk is sequence-dependent. The model is typed, executable or mechanically analysable, includes invalid and recovery paths, documents atomicity and environment actions, and has a maintained mapping to the artefact or decision it governs.

**EXPECTED_ENGINEERING_PAYOFF:** Makes illegal states and transition gaps visible, enables counterexample traces, and replaces repeated narrative reasoning about lifecycle or concurrency with a checkable behavioural object.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can implementation atomicity be extracted or validated cheaply for rapidly changing systems?
- When does a state-machine model become less readable than scenario- or trace-based evidence?
- What coverage measures best reveal omitted transitions rather than merely explored model states?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S001, S007, S009, S017, S020, S006, S008  
**CRITICAL_SOURCES:** S019, S045, S092, S103, S056, S008, S106  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S009, S029, S030, S031, S052, S054  
**CONTRARY_EVIDENCE:** S019, S045, S092, S103

**SOURCE IDENTITIES USED:**
- S001: Robert W. Floyd, *Assigning Meanings to Programs* (1967)
- S007: E. M. Clarke, E. A. Emerson, and J. Sifakis, *Model Checking: Algorithmic Verification and Debugging* (2009; roots in 1981 work)
- S009: Gerard J. Holzmann, *The Model Checker SPIN* (1997)
- S017: Leslie Lamport, *The Temporal Logic of Actions* (1994)
- S020: David Harel, *Statecharts: A Visual Formalism for Complex Systems* (1987)
- S006: Amir Pnueli, *The Temporal Logic of Programs* (1977)
- S008: J. R. Burch, E. M. Clarke, K. L. McMillan, D. L. Dill, and L. J. Hwang, *Symbolic Model Checking: 10^20 States and Beyond* (1992)
- S019: Robin Milner, *A Calculus of Communicating Systems* (1980)
- S045: Per Martin-Löf, *Intuitionistic Type Theory* (1984)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S103: Frédéric Herbreteau, Sarah Larroze-Jardiné, and Igor Walukiewicz, *Partial-Order Reduction Is Hard* (2025)
- S056: James H. Fetzer, *Program Verification: The Very Idea* (1988)
- S106: Roger C. Su and Robert J. Colvin, *Weak Memory Model Formalisms: Introduction and Survey* (2026, Concurrency and Computation: Practice and Experience 38(2))
- S029: Chris Newcombe et al., *How Amazon Web Services Uses Formal Methods* (2015)
- S030: Chris Hawblitzel et al., *IronFleet: Proving Practical Distributed Systems Correct* (2015)
- S031: James R. Wilcox et al., *Verdi: A Framework for Implementing and Formally Verifying Distributed Systems* (2015)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P005 — State invariant as cheap mechanical guard

**CURRENT_STATUS:** `INVARIANT_TEMPORAL_PROPERTY`  
**LINEAGE_CLASS:** `PROGRAM_LOGIC_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `invariant temporal`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** program logic / assertion lineage

**ORIGINAL_FORM:** Floyd assertions and Hoare loop invariants made “always true at this point” predicates central to proof. B/Event-B turned invariants into persistent machine proof obligations; assertions, static analysers and runtime monitors later made many invariants executable [S001, S002, S010, S011, S032, S066].

**PROBLEM_IT_ADDRESSED:** Recurring illegal-state defects are repeatedly rediscovered by review or tests because a simple domain rule—nonnegative balance, unique owner, monotone phase, bounded index, valid status combination—is never encoded at the point where state changes.

**ENGINEERING_CLAIM:** A meaningful always-true condition should be executable or mechanically checked before being entrusted to repeated review.

**MECHANISM:** Express the smallest decision-relevant state predicate as a compile-time check, database constraint, assertion, static-analysis rule, model invariant or runtime monitor. Exercise it against known bad states and instrument transition points so violation yields a diagnostic witness.

**TRIGGER_OR_CONTEXT:** Trigger for a simple, repeatedly violated state relation with clear local observability and cheap enforcement.

**NON_TRIGGER_OR_CHEAP_PATH:** Do not promote every comment to an invariant; use a unit test or ordinary validation where the rule is one-off, noncritical or not continuously meaningful.

**DEPENDENCIES_OR_PRECONDITIONS:** A named failure class, authoritative state representation, defined check points and response to violation.

**SPECIFICATION_PRECONDITIONS:** Predicate is nontrivial, satisfiable, tied to acceptance, and explicit about transient/recovery exceptions.

**ABSTRACTION_PRECONDITIONS:** The variables checked faithfully represent the state relation; no lossy projection hides violation.

**ENVIRONMENT_PRECONDITIONS:** External updates or concurrent writers are included in enforcement or bounded as assumptions.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** The check executes on the authoritative state and cannot be bypassed by an alternate mutation path.

**TRUSTED_TOOL_PRECONDITIONS:** Assertion compiler, analyser, schema engine or monitor semantics are tested or qualified proportionally.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Schema/status/unit changes require invariant review; obsolete invariants are removed rather than left permanently green.

**KNOWN_FAILURE_MODES:**
- The invariant is true but too weak to exclude the actual defect.
- It is checked only at sampled or public boundaries while internal transitions can violate it.
- It is disabled in production or compiled out.
- The predicate duplicates a stale schema or unit convention.
- Too many low-value invariants create alarm fatigue and maintenance burden.
- An invariant blocks legitimate transient/recovery states.

**IMPORTANT_CRITICISMS:**
- More invariants do not imply stronger assurance; strength depends on relation to failure modes and check points.
- Vacuous or unreachable-state invariants can pass without constraining behaviour [S059, S060].
- Runtime checks detect a violation but do not by themselves contain or recover from it [S066, S099].
- Focused unit-proof evidence is promising but bounded and not a universal ROI result [S107].

**HOW_THE_PROPERTY_EVOLVED:** The loop-proof auxiliary assertion evolved into a general low-cost guard spanning design models, database schemas, static analysis, dependent/refinement types and runtime telemetry. Mature practice selects invariants from concrete failure classes, tests their mutation sensitivity, defines when they must hold, and pairs detection with response.

**MATURE_OR_EVOLVED_FORM:** Prefer a small executable invariant when it eliminates a recurring illegal state more cheaply than a full model or theorem. State whether it is continuous, transition-boundary or sampled; prove inductiveness only when making all-reachable-state claims; and connect violation to diagnosis and safe handling.

**EXPECTED_ENGINEERING_PAYOFF:** Eliminates entire classes of local state corruption at low implementation and review cost, shortens debugging by producing immediate witnesses, and provides a stable acceptance hook.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which mutation/specification-strength metrics best identify invariants that add no real constraint?
- How should transient violations during recovery or distributed convergence be represented?
- When does runtime invariant overhead or false alarm rate exceed the avoided defect cost?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S001, S002, S010, S011, S006, S032, S066  
**CRITICAL_SOURCES:** S059, S060, S099, S066, S107  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S032, S050, S107, S052, S054  
**CONTRARY_EVIDENCE:** S059, S060, S099

**SOURCE IDENTITIES USED:**
- S001: Robert W. Floyd, *Assigning Meanings to Programs* (1967)
- S002: C. A. R. Hoare, *An Axiomatic Basis for Computer Programming* (1969)
- S010: Jean-Raymond Abrial, *The B-Book: Assigning Programs to Meanings* (1996)
- S011: Jean-Raymond Abrial, *Modeling in Event-B: System and Software Engineering* (2010)
- S006: Amir Pnueli, *The Temporal Logic of Programs* (1977)
- S032: Astrée project / Cousot lineage, *Astrée static analyzer project materials* (current accessed 2026-08-12)
- S066: Martin Leucker and Christian Schallhart, *A Brief Account of Runtime Verification* (2009)
- S059: Ilan Beer et al., *Efficient Detection of Vacuity in ACTL Formulas* (1997)
- S060: Orna Kupferman and Moshe Y. Vardi, *Vacuity Detection in Temporal Model Checking* (2003)
- S099: Benedikt Bollig, *Runtime Verification: Monitoring, Knowledge, and Uncertainty* (2026, v1)
- S107: Paschal C. Amusuo, Owen Cochell, Taylor Le Lievre, Parth V. Patil, Aravind Machiry, and James C. Davis, *Do Unit Proofs Work? An Empirical Study of Compositional Bounded Model Checking for Memory Safety Verification* (2025 preprint)
- S050: Andrew W. Appel et al., *Verified Software Toolchain / Verifiable C materials* (2010s-current)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P006 — Inductive invariant obligation

**CURRENT_STATUS:** `INVARIANT_TEMPORAL_PROPERTY`  
**LINEAGE_CLASS:** `PROGRAM_LOGIC_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `invariant temporal`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** program logic / assertion lineage

**ORIGINAL_FORM:** Floyd’s inductive assertion method and Hoare’s loop rule required an assertion to hold initially and be preserved by each program step. B/Event-B and theorem provers institutionalised base and preservation proof obligations over machines and refinements [S001, S002, S010, S011].

**PROBLEM_IT_ADDRESSED:** An invariant may hold in observed tests or intended states yet fail after an unexamined transition. Calling it an invariant without proving initiation and consecution confuses sampled evidence with an all-reachable-state theorem.

**ENGINEERING_CLAIM:** An invariant used as all-reachable-states evidence must hold initially and be preserved by every relevant transition.

**MECHANISM:** Prove two obligations: every allowed initial state satisfies the predicate, and each enabled transition preserves it assuming it held before. Strengthen with auxiliary invariants when necessary; generate counterexamples to failed initiation/preservation; ensure the transition set is complete.

**TRIGGER_OR_CONTEXT:** Trigger when acceptance requires “all reachable states” rather than checks at selected observations.

**NON_TRIGGER_OR_CHEAP_PATH:** Use runtime assertions or bounded exploration when the transition system is unstable, incomplete or the universal claim is unnecessary.

**DEPENDENCIES_OR_PRECONDITIONS:** Complete initialisation and transition model, explicit atomicity, and a meaningful target predicate.

**SPECIFICATION_PRECONDITIONS:** Initiation and preservation obligations are stated separately; auxiliary invariants do not change the target claim.

**ABSTRACTION_PRECONDITIONS:** Abstract transitions conservatively cover concrete steps relevant to preservation.

**ENVIRONMENT_PRECONDITIONS:** Environment interference appears as transitions or rely conditions.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Every concrete state mutation is represented by a preserving abstract step or a proved refinement sequence.

**TRUSTED_TOOL_PRECONDITIONS:** Invariant inference and SMT discharge are either checked by proof/certificate or included in the trust boundary.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Any initialisation, state schema or transition change invalidates preservation evidence until replayed and correspondence-reviewed.

**KNOWN_FAILURE_MODES:**
- Initial-state predicate is narrower than deployment initialisation or recovery.
- A transition is omitted or its guard is modelled too strongly.
- The proposed invariant is true but not inductive and proof succeeds only after excluding reachable states.
- Auxiliary invariants encode unreviewed assumptions or become harder to validate than the target property.
- Concurrency/weak memory invalidates the atomic preservation step.
- Proof is preserved after code changes because the model transition did not change.

**IMPORTANT_CRITICISMS:**
- Inductiveness is a proof property, not evidence that the invariant is meaningful or sufficient.
- Strengthening an invariant can hide failing states if initial/reachability conditions are also narrowed.
- Implementation correspondence and atomicity remain outside a model-only induction proof [S092, S106].
- Automation may produce opaque auxiliary invariants whose engineering interpretation is weak.

**HOW_THE_PROPERTY_EVOLVED:** Manual loop invariants evolved into automated invariant inference, abstract-interpretation fixpoints, IC3/PDR-style inductive reasoning, refinement invariants and generated proof obligations. The evolved engineering form requires a readable target invariant, reviewed auxiliary facts and a complete transition/correspondence story.

**MATURE_OR_EVOLVED_FORM:** Use inductive proof only when claiming that every reachable state satisfies a predicate. Keep initiation, preservation and transition completeness separate; treat inferred strengthening as reviewable evidence; and downgrade to sampled/runtime evidence when full transition correspondence is unavailable.

**EXPECTED_ENGINEERING_PAYOFF:** Converts a recurring assertion into a universal reachability claim, pinpoints the transition that breaks the rule, and supports modular refinement and model checking.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can automatically inferred inductive invariants be ranked for semantic relevance rather than solver utility?
- What practical evidence establishes transition completeness for code-extracted or distributed models?
- How should induction be adapted when the implementation exposes non-atomic weak-memory steps?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S001, S002, S010, S011, S005  
**CRITICAL_SOURCES:** S059, S060, S092, S106  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S025, S027, S030, S010, S011, S052  
**CONTRARY_EVIDENCE:** S059, S060, S092

**SOURCE IDENTITIES USED:**
- S001: Robert W. Floyd, *Assigning Meanings to Programs* (1967)
- S002: C. A. R. Hoare, *An Axiomatic Basis for Computer Programming* (1969)
- S010: Jean-Raymond Abrial, *The B-Book: Assigning Programs to Meanings* (1996)
- S011: Jean-Raymond Abrial, *Modeling in Event-B: System and Software Engineering* (2010)
- S005: Patrick Cousot and Radhia Cousot, *Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints* (1977)
- S059: Ilan Beer et al., *Efficient Detection of Vacuity in ACTL Formulas* (1997)
- S060: Orna Kupferman and Moshe Y. Vardi, *Vacuity Detection in Temporal Model Checking* (2003)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S106: Roger C. Su and Robert J. Colvin, *Weak Memory Model Formalisms: Introduction and Survey* (2026, Concurrency and Computation: Practice and Experience 38(2))
- S025: Gerwin Klein et al., *seL4: Formal Verification of an OS Kernel* (2009)
- S027: Ronghui Gu et al., *CertiKOS: An Extensible Architecture for Building Certified Concurrent OS Kernels* (2016)
- S030: Chris Hawblitzel et al., *IronFleet: Proving Practical Distributed Systems Correct* (2015)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P007 — Safety versus liveness distinction

**CURRENT_STATUS:** `INVARIANT_TEMPORAL_PROPERTY`  
**LINEAGE_CLASS:** `TEMPORAL_LOGIC_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `invariant temporal`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** temporal logic lineage

**ORIGINAL_FORM:** Pnueli introduced temporal logic for program computations; Alpern and Schneider later characterised safety as exclusion of finite bad prefixes and liveness as perpetual possibility of eventual acceptance. TLA and model checking operationalised both classes [S006, S007, S017, S086].

**PROBLEM_IT_ADDRESSED:** A system can preserve every invariant while never completing work, granting service, recovering, electing a leader or terminating. Conversely, a progress test can pass while an unsafe intermediate state occurs. Treating “correctness” as one undifferentiated predicate hides these distinct obligations.

**ENGINEERING_CLAIM:** Acceptance must distinguish no-bad-state properties from progress/eventuality/termination/availability obligations.

**MECHANISM:** Classify each obligation as safety, liveness/progress, termination, bounded response, trace/hyperproperty or combination. Use invariants/reachability for bad prefixes; ranking, fairness and temporal reasoning for eventuality; timed formalisms for deadlines; and maintain separate evidence and counterexamples.

**TRIGGER_OR_CONTEXT:** Trigger for reactive, concurrent, distributed, workflow, recovery or termination claims where absence of bad states does not guarantee completion.

**NON_TRIGGER_OR_CHEAP_PATH:** For a finite terminating function, an ordinary total-correctness contract may cover both result and termination without a temporal model.

**DEPENDENCIES_OR_PRECONDITIONS:** Clear event semantics, scheduler/environment model and operational definition of useful progress.

**SPECIFICATION_PRECONDITIONS:** Safety and liveness clauses are separate; eventualities state fairness and, where needed, deadlines.

**ABSTRACTION_PRECONDITIONS:** Abstraction preserves the property class; stuttering or trace quotienting does not erase relevant progress.

**ENVIRONMENT_PRECONDITIONS:** Service availability, retries, message delivery, scheduling and time premises are explicit.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Implementation events and scheduler behaviours correspond to the temporal model.

**TRUSTED_TOOL_PRECONDITIONS:** Liveness algorithms, fairness settings and monitor verdict semantics are pinned and reviewable.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Scheduler, timeout, retry and queue-policy changes trigger liveness re-analysis even if safety invariants remain unchanged.

**KNOWN_FAILURE_MODES:**
- Only safety is proved while deadlock, starvation or nontermination remains possible.
- Liveness is proved under unrealistic fairness or retry assumptions.
- An eventuality has no bound and is operationally useless.
- Termination yields an error or empty result rather than useful completion.
- A bounded response is modelled without clock drift or scheduling delay.
- A hyperproperty such as noninterference is reduced incorrectly to a single-trace invariant.

**IMPORTANT_CRITICISMS:**
- Liveness proofs are often assumption-heavy and more difficult to automate than safety proofs [S008, S105].
- Fairness can make an execution disappear mathematically without making a scheduler fair in deployment.
- Runtime monitors cannot generally decide arbitrary liveness from a finite prefix [S099].
- Security hyperproperties demonstrate that the safety/liveness dichotomy over single traces is not the entire property universe [S021].

**HOW_THE_PROPERTY_EVOLVED:** The initial temporal-logic distinction expanded to safety/liveness decompositions, stuttering-invariant specifications, ranking functions, real-time logics, probabilistic temporal properties and hyperproperties. Mature practice now records both property class and evidence limits, rather than labelling every assertion an invariant.

**MATURE_OR_EVOLVED_FORM:** Acceptance separates “nothing bad” from “something good” and names the assumptions or time bound behind progress. A safety proof cannot substitute for liveness evidence; an unbounded eventuality cannot substitute for service-level usefulness; monitorability limits are explicit.

**EXPECTED_ENGINEERING_PAYOFF:** Prevents green safety proofs from masking deadlock or starvation, directs method selection, and makes progress assumptions reviewable and testable.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which liveness obligations can be reduced to safety without obscuring fairness or ranking assumptions?
- How should operationally useful bounded progress be specified when timing is stochastic?
- What reviewer-facing forms best communicate hyperproperties and multi-trace obligations?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S006, S017, S086, S007  
**CRITICAL_SOURCES:** S021, S092, S099, S008, S105  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S029, S030, S031, S105, S052, S054  
**CONTRARY_EVIDENCE:** S021, S092, S099

**SOURCE IDENTITIES USED:**
- S006: Amir Pnueli, *The Temporal Logic of Programs* (1977)
- S017: Leslie Lamport, *The Temporal Logic of Actions* (1994)
- S086: Bowen Alpern and Fred B. Schneider, *Defining Liveness* (1985)
- S007: E. M. Clarke, E. A. Emerson, and J. Sifakis, *Model Checking: Algorithmic Verification and Debugging* (2009; roots in 1981 work)
- S021: Michael R. Clarkson and Fred B. Schneider, *Hyperproperties* (2008/2010)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S099: Benedikt Bollig, *Runtime Verification: Monitoring, Knowledge, and Uncertainty* (2026, v1)
- S008: J. R. Burch, E. M. Clarke, K. L. McMillan, D. L. Dill, and L. J. Hwang, *Symbolic Model Checking: 10^20 States and Beyond* (1992)
- S105: Jingyi Yao, Runzhou Tao, Ronghui Gu, and Jason Nieh, *Mostly Automated Verification of Liveness Properties for Distributed Protocols with Ranking Functions* (2024)
- S029: Chris Newcombe et al., *How Amazon Web Services Uses Formal Methods* (2015)
- S030: Chris Hawblitzel et al., *IronFleet: Proving Practical Distributed Systems Correct* (2015)
- S031: James R. Wilcox et al., *Verdi: A Framework for Implementing and Formally Verifying Distributed Systems* (2015)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P008 — Fairness and scheduler assumptions

**CURRENT_STATUS:** `ASSUMPTION_SENSITIVE`  
**LINEAGE_CLASS:** `TEMPORAL_LOGIC_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `assumption sensitive`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** temporal logic lineage

**ORIGINAL_FORM:** Temporal proofs introduced fairness constraints to exclude computations that forever postpone an enabled action. TLA and distributed-protocol proofs made weak/strong fairness, delivery and scheduling premises explicit; rely/guarantee gave a related compositional account of environmental interference [S006, S017, S088, S105].

**PROBLEM_IT_ADDRESSED:** A liveness theorem can be won by assuming that every continuously or repeatedly enabled action eventually runs, every message is retried/delivered, or every process takes steps—conditions that actual schedulers, overload, partitions or failures may not guarantee.

**ENGINEERING_CLAIM:** Liveness/progress claims must state fairness, scheduling and retry assumptions, and whether they hold in the real runtime.

**MECHANISM:** State the exact fairness class and subject actions; prove liveness conditionally; identify the runtime mechanism that enforces or approximates it (queue policy, timeout, retry, admission control, watchdog); test hostile schedules and monitor starvation/backlog indicators.

**TRIGGER_OR_CONTEXT:** Trigger whenever progress depends on scheduling, retries, message delivery, resource allocation or repeated opportunities.

**NON_TRIGGER_OR_CHEAP_PATH:** For a synchronous finite procedure with controlled execution, prove termination or enforce a timeout directly rather than introduce abstract fairness.

**DEPENDENCIES_OR_PRECONDITIONS:** Named actions/processes, scheduler/network semantics, resource limits and a clear operational notion of enablement.

**SPECIFICATION_PRECONDITIONS:** Fairness scope is minimal and separate from the property being proved; no global fairness wildcard.

**ABSTRACTION_PRECONDITIONS:** Abstraction preserves enablement and scheduling distinctions relevant to fairness.

**ENVIRONMENT_PRECONDITIONS:** Delivery, retry, clock, queue and resource assumptions have operational evidence.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Implementation scheduling and retry behaviour match the model’s fairness granularity.

**TRUSTED_TOOL_PRECONDITIONS:** Model-checker fairness settings and liveness algorithms are recorded, not implicit defaults.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Priority, timeout, retry, admission-control and infrastructure changes invalidate fairness discharge.

**KNOWN_FAILURE_MODES:**
- Fairness is globally enabled in a model checker although only some actions deserve it.
- A retry loop assumes eventual network delivery during permanent partition.
- Weak fairness is used where an action is enabled intermittently and requires strong fairness.
- Scheduler priority or resource exhaustion violates proof premises.
- Fairness hides a design with no bounded progress guarantee.
- Operational instrumentation cannot observe whether an action remained enabled.

**IMPORTANT_CRITICISMS:**
- Fairness is often a modelling convenience rather than a deployable mechanism.
- Conditional liveness may be mathematically correct but operationally weak under overload or adversarial scheduling.
- Distributed-system defects and current liveness research show that failure and ranking assumptions need explicit validation [S092, S105].
- Finite runtime traces generally cannot establish future fairness [S099].

**HOW_THE_PROPERTY_EVOLVED:** Unqualified eventuality evolved into named weak/strong fairness, justice/compassion constraints, ranking and prophecy mechanisms, scheduler contracts, probabilistic progress and bounded service objectives. Mature practice links each premise to architecture or runtime evidence instead of leaving it in a tool option.

**MATURE_OR_EVOLVED_FORM:** A liveness claim lists the precise scheduler, delivery and resource assumptions; each is either enforced, stress-tested, monitored or accepted as a residual condition. Where only unbounded fairness is available, the claim is not presented as a latency or availability guarantee.

**EXPECTED_ENGINEERING_PAYOFF:** Exposes hidden progress dependencies, prevents misleading eventuality proofs, and directs engineering toward retries, queue discipline, admission control or bounded-response mechanisms.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can fairness assumptions be calibrated against empirical scheduler/network distributions without converting a deterministic theorem into false certainty?
- Which runtime indicators can falsify a fairness premise early enough to recover?
- When should an unbounded liveness theorem be replaced by probabilistic or timed evidence?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S006, S017, S088, S105  
**CRITICAL_SOURCES:** S092, S099, S105  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S030, S031, S105, S052  
**CONTRARY_EVIDENCE:** S092, S099

**SOURCE IDENTITIES USED:**
- S006: Amir Pnueli, *The Temporal Logic of Programs* (1977)
- S017: Leslie Lamport, *The Temporal Logic of Actions* (1994)
- S088: Cliff B. Jones, *Tentative Steps Toward a Development Method for Interfering Programs* (1983)
- S105: Jingyi Yao, Runzhou Tao, Ronghui Gu, and Jason Nieh, *Mostly Automated Verification of Liveness Properties for Distributed Protocols with Ranking Functions* (2024)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S099: Benedikt Bollig, *Runtime Verification: Monitoring, Knowledge, and Uncertainty* (2026, v1)
- S030: Chris Hawblitzel et al., *IronFleet: Proving Practical Distributed Systems Correct* (2015)
- S031: James R. Wilcox et al., *Verdi: A Framework for Implementing and Formally Verifying Distributed Systems* (2015)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P009 — Property-class matching

**CURRENT_STATUS:** `INVARIANT_TEMPORAL_PROPERTY`  
**LINEAGE_CLASS:** `TEMPORAL_LOGIC_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `invariant temporal`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** temporal logic lineage

**ORIGINAL_FORM:** Formal methods diversified from state predicates and Hoare triples to temporal trace properties, process equivalences, real-time and probabilistic models, information-flow hyperproperties, resource bounds and dependent/refinement types [S002, S006, S018, S019, S021, S045, S047].

**PROBLEM_IT_ADDRESSED:** Using the wrong method can produce a green result that does not express the claim: a type checker for functional correctness, an invariant for information flow, bounded search for unbounded termination, or single-trace monitoring for a hyperproperty.

**ENGINEERING_CLAIM:** The method must match property class: invariant, trace, hyperproperty, real-time, probabilistic, information-flow or resource bound.

**MECHANISM:** Classify the claim by semantic shape—state, transition, finite trace, infinite trace, set of traces, quantitative probability, time, resource, refinement/equivalence or type—and select a logic/tool whose soundness theorem covers that class. Record what is reduced or approximated.

**TRIGGER_OR_CONTEXT:** Trigger whenever a method is being selected or a narrow formal result is used to support a broader class of claim.

**NON_TRIGGER_OR_CHEAP_PATH:** For an obvious local property—such as nullness or array bounds—use the direct analyser/type check without a separate taxonomy exercise.

**DEPENDENCIES_OR_PRECONDITIONS:** A clear engineering claim and access to method soundness/scope documentation.

**SPECIFICATION_PRECONDITIONS:** The formal statement’s semantic domain and quantification over states/traces/executions are explicit.

**ABSTRACTION_PRECONDITIONS:** Any reduction from one property class to another states side conditions and lost information.

**ENVIRONMENT_PRECONDITIONS:** Timing, probability, observation and adversary models match the selected property class.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** The implementation relation preserves the kind of observation used by the property.

**TRUSTED_TOOL_PRECONDITIONS:** Tool front ends and encodings do not silently reinterpret arithmetic, time, probability or trace semantics.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Changes in claim class or observation model require method reassessment, not merely rerunning the old checker.

**KNOWN_FAILURE_MODES:**
- A security noninterference claim is encoded as absence of a local bad state.
- A bounded model checker is treated as an unbounded prover.
- A runtime monitor is assigned an unmonitorable liveness or hyperproperty.
- Floating-point/resource bounds are discharged in an incompatible arithmetic theory.
- A type-level property excludes only representational errors while marketing claims behaviour.
- A probabilistic guarantee is collapsed into a deterministic invariant.

**IMPORTANT_CRITICISMS:**
- Tool branding encourages method-first rather than claim-first selection.
- Reductions can be sound only under side conditions that disappear in user-facing reports.
- Hyperproperties and weak-memory formalisms demonstrate that ordinary trace/invariant models can be structurally inadequate [S021, S106].
- Specialised methods improve fit but increase expertise and integration cost.

**HOW_THE_PROPERTY_EVOLVED:** The field evolved from competing universal formalisms toward a portfolio: safety model checking, liveness/ranking proof, probabilistic/timed checking, separation logic, refinement types, relational/hyperproperty logics and runtime monitoring. Mature engineering starts with the property class and uses hybrid evidence when no single method spans it.

**MATURE_OR_EVOLVED_FORM:** Every assurance result states its property class, method fit, approximation and non-covered classes. A type, invariant, monitor, bounded search or theorem is not promoted beyond the semantic guarantee its logic supports.

**EXPECTED_ENGINEERING_PAYOFF:** Avoids category errors, reduces wasted formalisation, and makes gaps between safety, progress, information flow, timing and quantitative behaviour explicit.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can engineering tools help classify claims without oversimplifying mixed properties?
- Which cross-logic translations preserve enough semantics for integrated assurance?
- How should quantitative uncertainty be combined with deterministic formal obligations?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S002, S006, S018, S019, S021, S045, S005, S047  
**CRITICAL_SOURCES:** S021, S099, S106  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S029, S032, S077, S099, S052, S054  
**CONTRARY_EVIDENCE:** S021, S099, S106

**SOURCE IDENTITIES USED:**
- S002: C. A. R. Hoare, *An Axiomatic Basis for Computer Programming* (1969)
- S006: Amir Pnueli, *The Temporal Logic of Programs* (1977)
- S018: C. A. R. Hoare, *Communicating Sequential Processes* (1978)
- S019: Robin Milner, *A Calculus of Communicating Systems* (1980)
- S021: Michael R. Clarkson and Fred B. Schneider, *Hyperproperties* (2008/2010)
- S045: Per Martin-Löf, *Intuitionistic Type Theory* (1984)
- S005: Patrick Cousot and Radhia Cousot, *Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints* (1977)
- S047: Niki Vazou et al., *Refinement Types for Haskell* (2014)
- S099: Benedikt Bollig, *Runtime Verification: Monitoring, Knowledge, and Uncertainty* (2026, v1)
- S106: Roger C. Su and Robert J. Colvin, *Weak Memory Model Formalisms: Introduction and Survey* (2026, Concurrency and Computation: Practice and Experience 38(2))
- S029: Chris Newcombe et al., *How Amazon Web Services Uses Formal Methods* (2015)
- S032: Astrée project / Cousot lineage, *Astrée static analyzer project materials* (current accessed 2026-08-12)
- S077: Jonathan Protzenko et al., *EverCrypt: A Fast, Verified, Cross-Platform Cryptographic Provider* (2020)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P010 — Contracts, preconditions and postconditions

**CURRENT_STATUS:** `CONTRACT_COMPOSITION_PROPERTY`  
**LINEAGE_CLASS:** `PROGRAM_LOGIC_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `contract composition`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** program logic / assertion lineage

**ORIGINAL_FORM:** Hoare triples gave procedures preconditions and postconditions; algebraic/interface specification, design by contract and behavioural subtyping extended these obligations across modules and substitution. Separation logic later added explicit frame/resource conditions [S002, S014, S048, S089].

**PROBLEM_IT_ADDRESSED:** Components fail in composition because callers and implementers hold different beliefs about valid inputs, outputs, side effects, exceptions, ownership, timing or protocol state. Interface prose is precise-looking but not executable or substitution-safe.

**ENGINEERING_CLAIM:** Component obligations should be stated as pre/postconditions and frame/interface contracts when substitution/composition matters.

**MECHANISM:** Attach typed preconditions, postconditions, exceptional outcomes, frame/effect clauses and invariants to an interface; statically prove or dynamically check callers and implementations; generate tests/witnesses for boundary cases; enforce behavioural-subtyping rules for replacement components.

**TRIGGER_OR_CONTEXT:** Trigger at reusable component, library, API, plugin or service boundaries where independent change or substitution is expected.

**NON_TRIGGER_OR_CHEAP_PATH:** For an internal one-use helper with obvious typed inputs, ordinary type checks and tests may be cheaper than a full contract layer.

**DEPENDENCIES_OR_PRECONDITIONS:** Authoritative interface schema, ownership of both caller and implementation obligations, and enforcement/checking path.

**SPECIFICATION_PRECONDITIONS:** Normal, exceptional and side-effect behaviour is covered; preconditions are not an escape hatch for likely failures.

**ABSTRACTION_PRECONDITIONS:** Contract abstractions retain observations needed by clients and do not hide relevant resource or temporal effects.

**ENVIRONMENT_PRECONDITIONS:** External service, clock, storage or user assumptions at the boundary are explicit.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Contracts are generated from, compiled with, or checked against the actual interface implementation/version.

**TRUSTED_TOOL_PRECONDITIONS:** Contract compiler, verifier, wrapper or runtime checker is within the assurance boundary.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** API/schema/version changes trigger caller and implementation rechecking; stale consumers are identified.

**KNOWN_FAILURE_MODES:**
- Preconditions shift responsibility to callers and exclude common misuse without detection.
- Postconditions omit side effects, exceptional paths or resource changes.
- Contracts are disabled or checked only in debug builds.
- A subtype strengthens preconditions or weakens guarantees.
- Cross-service contracts use incompatible units, versions or temporal semantics.
- The written contract is formal but disconnected from actual API/binary behaviour.

**IMPORTANT_CRITICISMS:**
- Contracts can become blame-shifting documentation rather than assurance if preconditions are not enforced.
- Local pre/postconditions may not express temporal protocol, concurrency or whole-system liveness.
- Behavioural subtyping depends on a sufficiently complete behavioural specification [S089].
- Dynamic contract checking samples executions and can add overhead; static proof adds annotation and maintenance cost.

**HOW_THE_PROPERTY_EVOLVED:** Procedure triples evolved into executable contracts, interface description logics, behavioural subtyping, refinement types, effect systems, session/typestate protocols and assume/guarantee component contracts. Mature practice selects the smallest enforceable contract that supports substitution and includes exceptions, effects and versioning.

**MATURE_OR_EVOLVED_FORM:** A contract is a machine-consumed boundary artefact: callers can be checked against assumptions, implementations against guarantees, side effects and exceptional behaviour are explicit, and substitution/version changes are verified. Unenforced prose is not counted as contract evidence.

**EXPECTED_ENGINEERING_PAYOFF:** Localises defects at component boundaries, supports safe substitution and modular verification, generates focused tests, and reduces integration ambiguity.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How should behavioural contracts evolve compatibly across independently deployed services?
- When are temporal/session contracts more cost-effective than ordinary request/response validation?
- How can human-readable contracts remain aligned with machine-oriented verification conditions?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S002, S014, S048, S089  
**CRITICAL_SOURCES:** S055, S100, S089  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S047, S050, S100, S052, S054  
**CONTRARY_EVIDENCE:** S055, S100

**SOURCE IDENTITIES USED:**
- S002: C. A. R. Hoare, *An Axiomatic Basis for Computer Programming* (1969)
- S014: John V. Guttag and James J. Horning, *Larch: Languages and Tools for Formal Specification* (1993)
- S048: John C. Reynolds, *Separation Logic: A Logic for Shared Mutable Data Structures* (2002)
- S089: Barbara H. Liskov and Jeannette M. Wing, *A Behavioral Notion of Subtyping* (1994)
- S055: Richard A. De Millo, Richard J. Lipton, and Alan J. Perlis, *Social Processes and Proofs of Theorems and Programs* (1979)
- S100: Eric Mugnier, Yuanyuan Zhou, Ranjit Jhala, and Michael Coblenz, *On the Impact of Formal Verification on Software Development* (2025)
- S047: Niki Vazou et al., *Refinement Types for Haskell* (2014)
- S050: Andrew W. Appel et al., *Verified Software Toolchain / Verifiable C materials* (2010s-current)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P011 — Local reasoning, frame and ownership conditions

**CURRENT_STATUS:** `CONTRACT_COMPOSITION_PROPERTY`  
**LINEAGE_CLASS:** `PROGRAM_LOGIC_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `contract composition`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** program logic / assertion lineage

**ORIGINAL_FORM:** Classical Hoare logic reasoned over whole program states. Separation logic introduced separating conjunction and the frame rule so a command could be proved using only the heap/resources it owns; concurrent separation logic added resource invariants and ownership transfer [S048, S049].

**PROBLEM_IT_ADDRESSED:** Whole-state specifications make modular verification brittle: every unrelated heap extension, alias or concurrent update can invalidate a proof. Unstated footprints allow components to corrupt memory/resources outside their intended authority.

**ENGINEERING_CLAIM:** Heap/resource effects must be bounded by frame/ownership conditions where local reasoning is decisive.

**MECHANISM:** Specify the footprint a component owns, the resources it may mutate, the invariants protecting shared resources, and the protocol for ownership transfer. Apply frame/locality rules to extend a local proof to disjoint state; verify unsafe or foreign-code boundaries separately.

**TRIGGER_OR_CONTEXT:** Trigger for pointer-rich, aliasing, concurrent, resource-owning or unsafe-code components where mutation authority is central.

**NON_TRIGGER_OR_CHEAP_PATH:** For immutable data or simple value-passing code, ordinary types and pre/postconditions are often sufficient.

**DEPENDENCIES_OR_PRECONDITIONS:** A precise resource semantics, alias model, ownership-transfer protocol and identified unsafe/foreign boundaries.

**SPECIFICATION_PRECONDITIONS:** Footprints include exceptional exits and non-memory resources material to clients.

**ABSTRACTION_PRECONDITIONS:** Logical resources faithfully represent concrete ownership and interference; ghost state is justified.

**ENVIRONMENT_PRECONDITIONS:** External actors cannot mutate owned state except through modelled interfaces.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Compiler/runtime memory and concurrency semantics support the ownership claims, including unsafe code.

**TRUSTED_TOOL_PRECONDITIONS:** The separation-logic verifier, SMT encoding and language semantics belong to the trusted/certified chain.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Representation, alias, unsafe-block and concurrency-protocol changes trigger local and dependent proof replay.

**KNOWN_FAILURE_MODES:**
- Aliasing violates the assumed disjointness or ownership partition.
- A frame condition omits hidden global, I/O, cache or external resource effects.
- Unsafe code or FFI bypasses the ownership discipline.
- Concurrency transfers ownership without preserving the shared invariant.
- Ghost ownership proves a logical protocol not enforced by the implementation runtime.
- Fine-grained ownership annotations impose maintenance cost disproportionate to risk.

**IMPORTANT_CRITICISMS:**
- Local reasoning is only as sound as the semantic account of resources and interference.
- Physical resources, timing and distributed ownership may not fit a heap-disjointness model.
- RustBelt demonstrates that unsafe libraries still require deep semantic verification beneath a safe type interface [S046].
- Concurrency and weak-memory behaviours can invalidate naïve ownership intuitions [S106].

**HOW_THE_PROPERTY_EVOLVED:** Heap-local frame rules evolved into concurrent separation logics, permissions, fractional ownership, resource algebras, effect systems and language-level borrowing/ownership. The mature form uses ownership where it buys modularity and contains unsafe boundaries rather than forcing every domain fact into a heap logic.

**MATURE_OR_EVOLVED_FORM:** For aliasing or shared-resource risk, each component has a machine-checkable footprint, frame/effect condition and transfer protocol. Safe interfaces encapsulate verified unsafe kernels; non-memory effects are either modelled or explicitly excluded.

**EXPECTED_ENGINEERING_PAYOFF:** Reduces proof blast radius, prevents unauthorised mutation/use-after-free classes, supports parallel reasoning, and enables reusable verified libraries behind stable interfaces.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can ownership reasoning scale cleanly across distributed resources and external devices?
- Which unsafe-boundary proof obligations give the best cost/benefit for systems languages?
- How should proof refactoring preserve ghost-state and resource-algebra abstractions?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S048, S049  
**CRITICAL_SOURCES:** S096, S106, S046  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S046, S050, S052  
**CONTRARY_EVIDENCE:** S096, S106

**SOURCE IDENTITIES USED:**
- S048: John C. Reynolds, *Separation Logic: A Logic for Shared Mutable Data Structures* (2002)
- S049: Peter W. O'Hearn, *Resources, Concurrency, and Local Reasoning* (2007)
- S096: Talia Ringer, Karl Palmskog, Ilya Sergey, Milos Gligoric, and Zachary Tatlock, *QED at Large: A Survey of Engineering of Formally Verified Software* (2019)
- S106: Roger C. Su and Robert J. Colvin, *Weak Memory Model Formalisms: Introduction and Survey* (2026, Concurrency and Computation: Practice and Experience 38(2))
- S046: Ralf Jung et al., *RustBelt: Securing the Foundations of the Rust Programming Language* (2018)
- S050: Andrew W. Appel et al., *Verified Software Toolchain / Verifiable C materials* (2010s-current)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P012 — Assume/guarantee and compositional verification

**CURRENT_STATUS:** `CONTRACT_COMPOSITION_PROPERTY`  
**LINEAGE_CLASS:** `CONCURRENCY_PROCESS_ALGEBRA_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `contract composition`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** concurrency/process algebra lineage

**ORIGINAL_FORM:** Owicki–Gries exposed interference obligations for parallel components; Jones’s rely/guarantee split each component’s environmental assumptions from its promised interference. Later interface theories and compositional model checking generalised the idea [S087, S088].

**PROBLEM_IT_ADDRESSED:** Monolithic verification does not scale, but independently verified components may not compose because each assumes behaviour the others do not guarantee. Hidden cross-component dependencies survive local proofs.

**ENGINEERING_CLAIM:** Large systems require component guarantees checked against explicit assumptions rather than monolithic unstated context.

**MECHANISM:** For each component state an assumption about environment actions and a guarantee about its own actions. Check local correctness under the rely condition, compatibility between guarantees and peers’ relies, invariant closure, circularity/well-foundedness and interface refinement. Recheck composition on substitution.

**TRIGGER_OR_CONTEXT:** Trigger for independently developed or replaceable components where whole-system exploration/proof is infeasible.

**NON_TRIGGER_OR_CHEAP_PATH:** For a tiny tightly coupled component set, direct integration tests or one finite model may be clearer and cheaper.

**DEPENDENCIES_OR_PRECONDITIONS:** Stable architectural boundaries, explicit shared state/events, contract owners and a compatibility checker or proof method.

**SPECIFICATION_PRECONDITIONS:** Assumptions and guarantees are separately satisfiable, noncircular and cover exceptions/faults.

**ABSTRACTION_PRECONDITIONS:** Interface abstractions preserve interactions relevant to the global claim.

**ENVIRONMENT_PRECONDITIONS:** Peers and external environment can demonstrably meet each rely condition.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Runtime component boundaries and versions match contract identities and event semantics.

**TRUSTED_TOOL_PRECONDITIONS:** Compositional checker and contract translator preserve conjunction, hiding and refinement semantics.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Component, dependency or interface changes trigger compatibility and affected-global-property replay.

**KNOWN_FAILURE_MODES:**
- Rely conditions are stronger than peer guarantees or deployment behaviour.
- Circular assumptions allow every component to “prove” its guarantee conditionally.
- Shared resources or emergent timing effects are absent from contracts.
- Composition covers safety but not global liveness/deadlock.
- Versioned components evolve contracts incompatibly.
- Compositional reductions hide a counterexample requiring more global state.

**IMPORTANT_CRITICISMS:**
- Assume/guarantee can relocate rather than eliminate the specification problem.
- Checking interface compatibility may still require global reasoning for cyclic liveness or quantitative resources.
- Contracts can become bureaucratic if no substitution or decision consumes them.
- Empirical model-code defects show that verified component abstractions can fail at integration shims [S092].

**HOW_THE_PROPERTY_EVOLVED:** Interference checks evolved into rely/guarantee, interface automata, contract-based design, compositional model checking, separation-logic resource protocols and layered refinement. Mature practice uses contracts at architectural seams, checks compatibility mechanically and escalates only unresolved global properties.

**MATURE_OR_EVOLVED_FORM:** Large systems are decomposed by explicit, versioned assumptions and guarantees that compose mechanically. Circularity, global invariants, liveness and shared resource bounds are checked separately; contracts with no live consumer are not retained as ceremony.

**EXPECTED_ENGINEERING_PAYOFF:** Reduces verification state/proof size, supports independent teams and safe substitution, and makes hidden integration assumptions reviewable.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can global liveness and resource properties be decomposed without circular proof?
- What contract granularity minimises both hidden coupling and maintenance cost?
- How should empirical service-level behaviour discharge quantitative assume/guarantee conditions?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S087, S088  
**CRITICAL_SOURCES:** S055, S092  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S027, S030, S031, S052  
**CONTRARY_EVIDENCE:** S055, S092

**SOURCE IDENTITIES USED:**
- S087: Susan Owicki and David Gries, *An Axiomatic Proof Technique for Parallel Programs I* (1976)
- S088: Cliff B. Jones, *Tentative Steps Toward a Development Method for Interfering Programs* (1983)
- S055: Richard A. De Millo, Richard J. Lipton, and Alan J. Perlis, *Social Processes and Proofs of Theorems and Programs* (1979)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S027: Ronghui Gu et al., *CertiKOS: An Extensible Architecture for Building Certified Concurrent OS Kernels* (2016)
- S030: Chris Hawblitzel et al., *IronFleet: Proving Practical Distributed Systems Correct* (2015)
- S031: James R. Wilcox et al., *Verdi: A Framework for Implementing and Formally Verifying Distributed Systems* (2015)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P013 — Sound abstraction discipline

**CURRENT_STATUS:** `ABSTRACTION_REFINEMENT_PROPERTY`  
**LINEAGE_CLASS:** `STATIC_ANALYSIS_AND_ABSTRACT_INTERPRETATION_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `abstraction refinement`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** static analysis and abstract interpretation lineage

**ORIGINAL_FORM:** Abstract interpretation formalised sound approximation of concrete semantics in lattices; model checking later used predicate abstraction and CEGAR, while data refinement used abstract state representations and retrieve relations [S005, S010, S061].

**PROBLEM_IT_ADDRESSED:** Concrete programs and systems are too large or infinite to analyse directly. Removing details can make analysis tractable, but an unsound or claim-inappropriate abstraction can miss real failures or generate unusable spurious alarms.

**ENGINEERING_CLAIM:** Abstraction must preserve properties needed by the claim and mark over/under-approximation explicitly.

**MECHANISM:** Define concrete and abstract domains, abstraction/concretisation relation, direction of approximation and property-preservation theorem. For over-approximation, all concrete behaviours must be represented; for under-approximation, claims are explicitly bug-finding only. Validate precision through counterexamples, CEGAR, domain-specific abstractions and sound numerical models.

**TRIGGER_OR_CONTEXT:** Trigger when exact state exploration or proof is infeasible but a conservative or witness-seeking approximation can answer a material question.

**NON_TRIGGER_OR_CHEAP_PATH:** For small finite systems or deterministic local rules, analyse the concrete state directly instead of introducing abstraction risk.

**DEPENDENCIES_OR_PRECONDITIONS:** Defined concrete semantics, target property, approximation direction and a strategy for spurious/missed behaviour.

**SPECIFICATION_PRECONDITIONS:** The property is preserved by the chosen abstraction relation.

**ABSTRACTION_PRECONDITIONS:** Soundness theorem, domain/transfer-function correctness and precision controls are explicit.

**ENVIRONMENT_PRECONDITIONS:** Concrete semantics includes relevant environment/hardware effects before abstraction.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** The “concrete” analysed model corresponds to source/binary/runtime at the claimed level.

**TRUSTED_TOOL_PRECONDITIONS:** Abstract transformers, widening, solver and front-end encodings are trusted or checked.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Code/semantics/property changes can invalidate domain assumptions and require abstraction regression.

**KNOWN_FAILURE_MODES:**
- An under-approximation is reported as proof of absence.
- Over-approximation is sound but produces overwhelming false positives.
- The abstraction merges states whose distinction is essential to the property.
- Widening loses an invariant needed to prove safety.
- Environment or floating-point semantics are abstracted inconsistently.
- A spurious counterexample is dismissed without refining the responsible abstraction.

**IMPORTANT_CRITICISMS:**
- Soundness and usefulness trade off: a perfectly sound analysis can be operationally unusable.
- Abstraction theorems cover only the formal concrete semantics, which may itself omit implementation/environment behaviour.
- CEGAR does not guarantee rapid convergence or a sufficiently expressive predicate domain [S061].
- Recent work continues to show fundamental incompleteness/scalability limits and hard reduction problems [S103].

**HOW_THE_PROPERTY_EVOLVED:** Manual data abstraction evolved into abstract domains, widening/narrowing, predicate abstraction, CEGAR, symmetry and partial-order reductions, compositional summaries and domain-specific analysers such as Astrée. Mature use treats abstraction design and counterexample validation as engineering work, not a hidden solver detail.

**MATURE_OR_EVOLVED_FORM:** Every abstract result states approximation direction, preserved property, omitted distinctions and spurious-result policy. Sound over-approximation supports absence claims only for the modelled concrete semantics; under-approximation supports witness finding only. Precision is tuned to a named decision.

**EXPECTED_ENGINEERING_PAYOFF:** Makes otherwise intractable analysis possible, supports scalable static checking/model checking, and turns spurious traces into a disciplined refinement loop.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can abstractions be synthesised for semantic relevance rather than benchmark performance?
- What practical thresholds identify a sound analyser whose false-positive burden destroys net value?
- How should learned/AI-generated abstractions be independently validated?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S005, S061, S010  
**CRITICAL_SOURCES:** S061, S092, S103  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S032, S033, S052, S054  
**CONTRARY_EVIDENCE:** S061, S092, S103

**SOURCE IDENTITIES USED:**
- S005: Patrick Cousot and Radhia Cousot, *Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints* (1977)
- S061: Edmund Clarke, Orna Grumberg, Somesh Jha, Yuan Lu, and Helmut Veith, *Counterexample-Guided Abstraction Refinement* (2000)
- S010: Jean-Raymond Abrial, *The B-Book: Assigning Programs to Meanings* (1996)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S103: Frédéric Herbreteau, Sarah Larroze-Jardiné, and Igor Walukiewicz, *Partial-Order Reduction Is Hard* (2025)
- S032: Astrée project / Cousot lineage, *Astrée static analyzer project materials* (current accessed 2026-08-12)
- S033: Microsoft Research / Windows, *Static Driver Verifier and SLAM technology* (2000s-current)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P014 — Refinement/simulation correspondence

**CURRENT_STATUS:** `ABSTRACTION_REFINEMENT_PROPERTY`  
**LINEAGE_CLASS:** `REFINEMENT_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `abstraction refinement`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** refinement lineage

**ORIGINAL_FORM:** Data refinement in VDM/Z/B related abstract and concrete states; simulation and process equivalence supplied behavioural correspondence; CompCert and verified systems later used chains of forward/backward simulation or contextual refinement [S010–S013, S019, S024, S027].

**PROBLEM_IT_ADDRESSED:** A property proved of an abstract design does not automatically hold for a lower-level model or implementation. Representation changes, new nondeterminism, compiler transformations or concurrency can introduce behaviours absent from the abstraction.

**ENGINEERING_CLAIM:** A lower-level implementation/model must refine the abstract property through a stated simulation/equivalence relation.

**MECHANISM:** State an observation relation and refinement criterion; construct retrieve relation or forward/backward simulation showing initial-state correspondence and step/trace preservation, including stuttering, termination and divergence conditions. Compose refinements across layers and check side conditions.

**TRIGGER_OR_CONTEXT:** Trigger whenever evidence at one abstraction level is used to control a lower-level model, source, binary or component substitution.

**NON_TRIGGER_OR_CHEAP_PATH:** For a direct executable specification or tiny transformation, differential/conformance testing may supply enough correspondence more cheaply.

**DEPENDENCIES_OR_PRECONDITIONS:** Formal semantics at both levels, observation relation, initial-state mapping and complete transformation/layer inventory.

**SPECIFICATION_PRECONDITIONS:** The abstract property is invariant under the chosen refinement relation.

**ABSTRACTION_PRECONDITIONS:** Retrieve/simulation relation covers representation and nondeterminism without hiding material observations.

**ENVIRONMENT_PRECONDITIONS:** Both levels use compatible environment, fault and scheduler assumptions.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Every deployed transformation/layer is either in the refinement chain or explicitly trusted/validated.

**TRUSTED_TOOL_PRECONDITIONS:** Semantics, proof assistant, translator and certificate checker are bounded.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Any layer, compiler option, source semantics or observation change triggers affected refinement replay.

**KNOWN_FAILURE_MODES:**
- The refinement relation preserves outputs but not timing, confidentiality or liveness observations.
- Forward simulation is insufficient in the presence of nondeterminism/divergence without additional conditions.
- Undefined source behaviour makes the compiler theorem permissive.
- A representation invariant is assumed rather than established at initialisation.
- Layer proofs do not compose because observation models differ.
- Implementation contains unmodelled code paths or optimisations.

**IMPORTANT_CRITICISMS:**
- Refinement proves the chosen observational relation, not every desired property.
- Semantic preservation can be weak or vacuous for undefined/unspecified source behaviour.
- Simulation proofs are technically strong but can hide human-selected correspondence relations.
- Empirical verified-system defects show gaps outside the proved refinement layers [S092].

**HOW_THE_PROPERTY_EVOLVED:** Manual data refinement evolved into refinement calculus, action-system refinement, contextual refinement, concurrent separation-logic refinement, compiler semantic preservation, translation validation and per-run certificates. The mature form names the observer and property class preserved at each layer.

**MATURE_OR_EVOLVED_FORM:** A high-level proof controls implementation only through a versioned, composable refinement/correspondence chain with explicit observations, divergence/termination treatment and unmodelled code boundary. Where full refinement is too costly, use conformance tests or translation validation and narrow the claim.

**EXPECTED_ENGINEERING_PAYOFF:** Allows abstract reasoning to survive implementation detail, supports verified compilation and layered systems, and makes model-code gaps concrete proof obligations.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which refinement notions best combine functional, temporal, security and quantitative observations?
- How can refinement chains be maintained incrementally across architecture and compiler changes?
- When is translation validation more economical than a global compiler/refinement proof?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S010, S012, S019, S024, S027, S017, S013, S011  
**CRITICAL_SOURCES:** S092, S094  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S024, S025, S027, S028, S098, S052, S093  
**CONTRARY_EVIDENCE:** S092, S094

**SOURCE IDENTITIES USED:**
- S010: Jean-Raymond Abrial, *The B-Book: Assigning Programs to Meanings* (1996)
- S012: J. M. Spivey, *The Z Notation: A Reference Manual* (1992, 2nd ed.)
- S019: Robin Milner, *A Calculus of Communicating Systems* (1980)
- S024: Xavier Leroy, *Formal Verification of a Realistic Compiler* (2009)
- S027: Ronghui Gu et al., *CertiKOS: An Extensible Architecture for Building Certified Concurrent OS Kernels* (2016)
- S017: Leslie Lamport, *The Temporal Logic of Actions* (1994)
- S013: Dines Bjørner and Cliff B. Jones, eds., *The Vienna Development Method: The Meta-Language* (1978)
- S011: Jean-Raymond Abrial, *Modeling in Event-B: System and Software Engineering* (2010)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S094: David Monniaux and Sylvain Boulmé, *The Trusted Computing Base of the CompCert Verified Compiler* (2022)
- S025: Gerwin Klein et al., *seL4: Formal Verification of an OS Kernel* (2009)
- S028: Haogang Chen et al., *Using Crash Hoare Logic for Certifying the FSCQ File System* (2015)
- S098: Gaurav Parthasarathy, Thibault Dardinier, Benjamin Bonneau, Peter Müller, and Alexander J. Summers, *Towards Trustworthy Automated Program Verifiers: Formally Validating Translations into an Intermediate Verification Language* (2024)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S093: seL4 Project, *What the Proofs Assume* (current site, accessed 2026-08-12)


### P015 — Model-code correspondence

**CURRENT_STATUS:** `ASSUMPTION_SENSITIVE`  
**LINEAGE_CLASS:** `VERIFIED_TOOLCHAIN_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `assumption sensitive`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** verified toolchain lineage

**ORIGINAL_FORM:** Formal specification methods originally relied on disciplined refinement or code generation to connect model and program. Translation validation, verified compilers, binary verification and model extraction made this link an explicit artefact rather than an informal claim [S023–S026].

**PROBLEM_IT_ADDRESSED:** The model may be correct while the deployed code, build options, generated artefacts, adapters, configuration or binary does something else. “The design was verified” is therefore not implementation assurance.

**ENGINEERING_CLAIM:** A verified model must be tied to the actual source/binary/configuration or treated as design evidence only.

**MECHANISM:** Maintain a traceable identity chain from requirement/model to source, generated code, compiler/linker options, binary, configuration and deployed instance. Establish correspondence by refinement proof, verified generation, translation validation, conformance/model-based tests, binary equivalence or runtime trace checking. Record any unverified glue.

**TRIGGER_OR_CONTEXT:** Trigger whenever a formal result is used to claim anything about source code, binaries, configured services or deployed hardware.

**NON_TRIGGER_OR_CHEAP_PATH:** For design exploration only, label the result design-level and avoid pretending to establish implementation correctness.

**DEPENDENCIES_OR_PRECONDITIONS:** Immutable artefact identities, build provenance, model/source mappings, configuration capture and transformation inventory.

**SPECIFICATION_PRECONDITIONS:** The formal claim states the concrete artefact level to which it is intended to apply.

**ABSTRACTION_PRECONDITIONS:** Mappings preserve relevant events, data domains and observations.

**ENVIRONMENT_PRECONDITIONS:** Deployment platform/configuration is within the modelled usage domain.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** This is the property itself: an explicit, checked link rather than naming similarity or process documentation.

**TRUSTED_TOOL_PRECONDITIONS:** Generators, compilers, extractors, linkers, build tools and validators are proved, validated or trusted explicitly.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Hash/version/configuration mismatch immediately downgrades or invalidates correspondence evidence.

**KNOWN_FAILURE_MODES:**
- Manual code diverges from a verified design model.
- Generated code is edited or regenerated with different tool/version/options.
- The verified source is not the source used for the deployed binary.
- Adapters, shims or configuration violate model assumptions.
- Code extraction/model extraction mistranslates semantics.
- A model-checker counterexample is infeasible in code—or code has behaviours absent from the model.

**IMPORTANT_CRITICISMS:**
- This is often the weakest evidence dimension despite very strong in-model proof.
- The empirical study of verified distributed systems found concrete defects outside verified models [S092].
- seL4 and CompCert sources explicitly document residual source/binary/hardware and toolchain boundaries [S093, S094].
- Certification documentation can establish traceability procedures without proving live deployed identity.

**HOW_THE_PROPERTY_EVOLVED:** Informal refinement claims evolved into generated-code chains, verified compilers, translation validation, per-run proof certificates, binary verification, reproducible builds and attestation. Mature practice grades correspondence strength instead of treating it as binary.

**MATURE_OR_EVOLVED_FORM:** Every real-world formal claim states its correspondence level: design only, source linked, generated source, compiled binary validated, or deployed instance attested. Gaps and glue code receive targeted tests/review; evidence is invalidated when identities diverge.

**EXPECTED_ENGINEERING_PAYOFF:** Prevents model-only assurance from controlling a deployment decision, focuses verification on risky transformations and glue, and makes the provenance of “formally verified” artefacts auditable.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can model-code mappings be kept current at low cost in fast-changing codebases?
- What correspondence evidence is sufficient for dynamic configuration, plugins and remote services?
- How should reproducible build and attestation evidence compose with semantic refinement proofs?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S023, S024, S025, S098, S026  
**CRITICAL_SOURCES:** S092, S093, S094  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S024, S025, S098, S051, S052, S113  
**CONTRARY_EVIDENCE:** S092, S093, S094

**SOURCE IDENTITIES USED:**
- S023: Amir Pnueli, Michael Siegel, and Eli Singerman, *Translation Validation* (1998)
- S024: Xavier Leroy, *Formal Verification of a Realistic Compiler* (2009)
- S025: Gerwin Klein et al., *seL4: Formal Verification of an OS Kernel* (2009)
- S098: Gaurav Parthasarathy, Thibault Dardinier, Benjamin Bonneau, Peter Müller, and Alexander J. Summers, *Towards Trustworthy Automated Program Verifiers: Formally Validating Translations into an Intermediate Verification Language* (2024)
- S026: seL4 Foundation / seL4 project, *seL4 Proofs and Proof Architecture* (current site, accessed 2026-08-12)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S093: seL4 Project, *What the Proofs Assume* (current site, accessed 2026-08-12)
- S094: David Monniaux and Sylvain Boulmé, *The Trusted Computing Base of the CompCert Verified Compiler* (2022)
- S051: Federal Aviation Administration, *AC 20-115D: Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178* (2017)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S113: Federal Aviation Administration, *AC 20-148: Reusable Software Components* (current guidance lineage, accessed 2026-08-12)


### P016 — Exhaustive finite-state challenge where warranted

**CURRENT_STATUS:** `MODEL_CHECKING_PROPERTY`  
**LINEAGE_CLASS:** `MODEL_CHECKING_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `model checking`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** model checking lineage

**ORIGINAL_FORM:** Foundational model checking algorithmically explored all reachable states of a finite transition system; SPIN operationalised explicit-state search, symbolic model checking represented sets of states compactly, and Alloy popularised finite bounded model finding [S007–S009, S016].

**PROBLEM_IT_ADDRESSED:** Reviews and conventional tests sample executions and miss rare interleavings, corner states and transition combinations. For a finite tractable model, exhaustive search can settle reachability or temporal properties and return witnesses.

**ENGINEERING_CLAIM:** Finite/bounded state models should be exhaustively searched when the state space is decision-relevant and tractable.

**MECHANISM:** Construct a finite or finitised transition model, enumerate or symbolically compute reachable states, check invariant/temporal formulas, and emit counterexample traces. Record state count, reductions, fairness, resource limits and whether exploration was genuinely complete.

**TRIGGER_OR_CONTEXT:** Trigger for finite protocols, controllers, configurations or small concurrent designs where exhaustive exploration is tractable and consequential.

**NON_TRIGGER_OR_CHEAP_PATH:** Use simulation, testing or bounded search when the model cannot be made finite without excluding the failure class or when a simple invariant suffices.

**DEPENDENCIES_OR_PRECONDITIONS:** Finite state encoding, complete transition/environment model, explicit property, resource-completion evidence and sound reductions.

**SPECIFICATION_PRECONDITIONS:** Formula is nonvacuous and its witnesses/counterexamples have engineering meaning.

**ABSTRACTION_PRECONDITIONS:** Finitisation and reductions preserve the checked property; under-approximations are labelled.

**ENVIRONMENT_PRECONDITIONS:** Relevant nondeterministic/fault behaviours are included in the finite model.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Model states/actions correspond to the claimed design or implementation level.

**TRUSTED_TOOL_PRECONDITIONS:** Search algorithm, state encoding, reductions and solver back ends are trusted or validated.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Model/property/tool changes require fresh completion metrics and replay.

**KNOWN_FAILURE_MODES:**
- State space is finite only because relevant data, faults or participants were bounded away.
- Search terminates by timeout/memory limit but is reported as exhaustive.
- Symmetry/partial-order reduction is unsound for the property.
- State hash compression or bitstate search sacrifices completeness without disclosure.
- The model omits environment or implementation behaviours.
- A property passes vacuously or due to unreachable initial states.

**IMPORTANT_CRITICISMS:**
- Exhaustiveness applies to represented states, not every real behaviour.
- State explosion can make complete search impossible even for finite models [S008, S103].
- Abstraction and reduction introduce proof obligations and possible spuriousness.
- No counterexample is weak evidence when bounds or coverage are unclear.

**HOW_THE_PROPERTY_EVOLVED:** Explicit search evolved into BDD symbolic checking, SAT/SMT bounded checking, partial-order/symmetry reduction, abstraction/CEGAR, compositional and probabilistic/timed model checking. Mature use distinguishes exhaustive finite proof from bounded bug finding and chooses a small model around the risky mechanism.

**MATURE_OR_EVOLVED_FORM:** Use exhaustive exploration when a decision-relevant finite state space can be justified and completed. Publish the model, property, bounds, reductions, explored state/transition counts and completion status; pair with correspondence and vacuity checks.

**EXPECTED_ENGINEERING_PAYOFF:** Finds rare ordering/state defects with concrete traces and can prove absence within a finite model more decisively than sampled testing.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which coverage and mutation measures best expose omitted behaviours in an “exhaustive” model?
- How should parameterised-system cutoffs be justified to engineers?
- When does reduction complexity exceed the value of checking the full state space?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S007, S008, S009, S016  
**CRITICAL_SOURCES:** S059, S060, S092, S103, S008  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S009, S029, S054, S052  
**CONTRARY_EVIDENCE:** S059, S060, S092, S103

**SOURCE IDENTITIES USED:**
- S007: E. M. Clarke, E. A. Emerson, and J. Sifakis, *Model Checking: Algorithmic Verification and Debugging* (2009; roots in 1981 work)
- S008: J. R. Burch, E. M. Clarke, K. L. McMillan, D. L. Dill, and L. J. Hwang, *Symbolic Model Checking: 10^20 States and Beyond* (1992)
- S009: Gerard J. Holzmann, *The Model Checker SPIN* (1997)
- S016: Daniel Jackson, *Software Abstractions: Logic, Language, and Analysis* (2006/2012)
- S059: Ilan Beer et al., *Efficient Detection of Vacuity in ACTL Formulas* (1997)
- S060: Orna Kupferman and Moshe Y. Vardi, *Vacuity Detection in Temporal Model Checking* (2003)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S103: Frédéric Herbreteau, Sarah Larroze-Jardiné, and Igor Walukiewicz, *Partial-Order Reduction Is Hard* (2025)
- S029: Chris Newcombe et al., *How Amazon Web Services Uses Formal Methods* (2015)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P017 — Counterexample usefulness and trace review

**CURRENT_STATUS:** `MODEL_CHECKING_PROPERTY`  
**LINEAGE_CLASS:** `MODEL_CHECKING_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `model checking`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** model checking lineage

**ORIGINAL_FORM:** Model checking distinguished itself from traditional proof by producing diagnostic counterexample executions; SPIN error trails and Alloy instances made falsifying traces/structures central engineering artefacts [S007, S009, S016].

**PROBLEM_IT_ADDRESSED:** A failed proof obligation or red status may not reveal a repairable defect. Engineers need the concrete sequence, state assignment or witness showing how the property fails—and whether that witness is feasible in the intended system.

**ENGINEERING_CLAIM:** Counterexamples are high-value engineering artefacts only when trace feasibility and abstraction validity are checked.

**MECHANISM:** Generate minimal or readable counterexample traces; map model states/actions to domain events; validate initial-state feasibility, abstraction concretisability and implementation reproducibility; classify as product defect, specification defect, abstraction artefact or expected excluded behaviour.

**TRIGGER_OR_CONTEXT:** Trigger whenever a checker finds a violation or failed obligation that must drive design/code/specification action.

**NON_TRIGGER_OR_CHEAP_PATH:** For a direct deterministic assertion failure, the ordinary failing input and stack trace may already be the cheapest witness.

**DEPENDENCIES_OR_PRECONDITIONS:** Trace semantics, domain mapping, concretisation/reproduction path and defect-classification process.

**SPECIFICATION_PRECONDITIONS:** The violated property is reviewed before attributing blame.

**ABSTRACTION_PRECONDITIONS:** Spuriousness/concretisability can be tested or clearly bounded.

**ENVIRONMENT_PRECONDITIONS:** The trace’s environment choices are feasible or intentionally adversarial.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Actions and state values can be mapped to implementation events or explicitly labelled design-only.

**TRUSTED_TOOL_PRECONDITIONS:** Trace generation, minimisation and explanation preserve a real violating path.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Accepted counterexamples are tied to model/code versions and retained as regressions after repair.

**KNOWN_FAILURE_MODES:**
- Counterexample exists only in an over-abstract model.
- Trace starts from an impossible initial state or violates an unstated assumption.
- The tool truncates or renders a trace too opaquely to diagnose.
- A real counterexample is dismissed because it conflicts with design intent.
- The property is wrong, but the witness is misclassified as a code defect.
- Teams optimise trace length rather than causal usefulness.

**IMPORTANT_CRITICISMS:**
- A counterexample to an abstraction is not necessarily an implementation bug [S061].
- Diagnostic value depends on model-code mapping and comprehensibility.
- Counterexamples can encourage local patching without strengthening the specification or model.
- Unsat/no-counterexample evidence does not share the same intuitive witness strength.

**HOW_THE_PROPERTY_EVOLVED:** Raw state dumps evolved into shortest traces, causal slicing, counterexample explanation, CEGAR concretisation checks, test-case generation and proof-assistant/LLM explanation aids. Mature practice treats the trace as evidence to be validated and classified, not automatic blame.

**MATURE_OR_EVOLVED_FORM:** Every counterexample is reviewed for feasibility, property validity, abstraction origin and correspondence. Accepted traces become regression tests or model/specification revisions; spurious traces drive abstraction refinement; unresolved traces remain open evidence rather than being suppressed.

**EXPECTED_ENGINEERING_PAYOFF:** Shortens diagnosis, converts exhaustive reasoning into actionable reproductions, and exposes incorrect assumptions/specifications early.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which causal/minimal trace criteria best predict human debugging success?
- How can LLM explanations be grounded so they do not invent causes beyond the trace?
- How should counterexamples from probabilistic, timed or hyperproperty analyses be presented?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S007, S009, S016  
**CRITICAL_SOURCES:** S061, S092  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S009, S016, S029, S061, S052, S054  
**CONTRARY_EVIDENCE:** S061, S092

**SOURCE IDENTITIES USED:**
- S007: E. M. Clarke, E. A. Emerson, and J. Sifakis, *Model Checking: Algorithmic Verification and Debugging* (2009; roots in 1981 work)
- S009: Gerard J. Holzmann, *The Model Checker SPIN* (1997)
- S016: Daniel Jackson, *Software Abstractions: Logic, Language, and Analysis* (2006/2012)
- S061: Edmund Clarke, Orna Grumberg, Somesh Jha, Yuan Lu, and Helmut Veith, *Counterexample-Guided Abstraction Refinement* (2000)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S029: Chris Newcombe et al., *How Amazon Web Services Uses Formal Methods* (2015)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P018 — Bounded checking scope disclosure

**CURRENT_STATUS:** `USEFUL_BUT_EASILY_GAMED`  
**LINEAGE_CLASS:** `MODEL_CHECKING_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `useful but easily gamed`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** model checking lineage

**ORIGINAL_FORM:** Bounded model checking encoded executions up to depth k as SAT, and CBMC applied bounded unwinding to C programs. Alloy similarly made finite scope an explicit analysis choice [S016, S036, S037].

**PROBLEM_IT_ADDRESSED:** Finite-depth reasoning is powerful for bug finding but is easily marketed as proof. A green run may merely mean no counterexample exists within the chosen depth, loop unwind, integer width, object scope or participant count.

**ENGINEERING_CLAIM:** Bounded model checking/model finding must publish the bound/scope and never sell no-counterexample as unbounded proof.

**MECHANISM:** Record every bound and completeness threshold; distinguish bug-finding result from proof; prove a completeness diameter/cutoff when possible; add unwinding assertions; increase bounds systematically; report timeout/unknown separately; use induction or unbounded proof for universal claims.

**TRIGGER_OR_CONTEXT:** Trigger whenever SAT/SMT/model-finding/symbolic search limits depth, objects, participants, loops or numeric domains.

**NON_TRIGGER_OR_CHEAP_PATH:** If a finite state space is genuinely exhausted, report that directly; if one deterministic edge case is at issue, use a direct test.

**DEPENDENCIES_OR_PRECONDITIONS:** Complete list of bounds, resource outcomes and any completeness/cutoff theorem.

**SPECIFICATION_PRECONDITIONS:** The claim is phrased to match bounded or unbounded evidence.

**ABSTRACTION_PRECONDITIONS:** Finitisation effects are explicit and do not masquerade as concrete completeness.

**ENVIRONMENT_PRECONDITIONS:** Bounded fault/event schedules do not silently exclude the motivating failure.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Loop/data/participant bounds match the claimed implementation scenario.

**TRUSTED_TOOL_PRECONDITIONS:** Unwinding, SAT/SMT encoding and unknown/timeout handling are correct and visible.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Bounds and completeness arguments are versioned with the model/property and rerun after change.

**KNOWN_FAILURE_MODES:**
- Bound omitted from reports or user interface.
- Loop unwinding assumptions suppress deeper defects.
- A small-scope hypothesis is treated as a theorem.
- Integer/bit-width choice removes overflow or enlarges semantics incorrectly.
- Timeout is converted into pass.
- Benchmark success rewards shallow expected counterexamples and hides transfer limits.

**IMPORTANT_CRITICISMS:**
- No counterexample up to k is not proof beyond k absent a completeness argument.
- Small scopes often find structural bugs but there is no universal guarantee.
- Bounds can be selected after seeing outcomes, enabling assurance gaming.
- AI-generated specifications/benchmarks can leak expected theorem structure [S101, S111].

**HOW_THE_PROPERTY_EVOLVED:** Bounded search evolved with incremental SAT/SMT, k-induction, interpolation, completeness thresholds and explicit unwind checks. The mature property is not bounded checking itself but honest scope disclosure and escalation rules.

**MATURE_OR_EVOLVED_FORM:** A bounded result states exact depth/scope/width/participants, resource termination, completeness status and decision meaning. It is accepted as proof only with a valid cutoff/diameter/induction argument; otherwise it is labelled strong bounded challenge or bug-finding evidence.

**EXPECTED_ENGINEERING_PAYOFF:** Preserves the high bug-finding value and automation of bounded reasoning without allowing it to control unbounded correctness claims.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which automatic summaries best communicate multiple interacting bounds to non-specialists?
- How can adaptive bound selection avoid outcome-driven cherry-picking?
- For which domain patterns can trustworthy cutoffs be inferred automatically?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S016, S036, S037  
**CRITICAL_SOURCES:** S045, S101, S111  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S016, S037, S052, S054  
**CONTRARY_EVIDENCE:** S045, S101, S111

**SOURCE IDENTITIES USED:**
- S016: Daniel Jackson, *Software Abstractions: Logic, Language, and Analysis* (2006/2012)
- S036: Armin Biere, Alessandro Cimatti, Edmund Clarke, and Yunshan Zhu, *Symbolic Model Checking without BDDs* (1999)
- S037: Edmund Clarke, Daniel Kroening, and Flavio Lerda, *A Tool for Checking ANSI-C Programs* (2004)
- S045: Per Martin-Löf, *Intuitionistic Type Theory* (1984)
- S101: Jiayi Wu, Robert Joseph George, and Anima Anandkumar, *ITPEval: Benchmarking Formal Translation Across Interactive Theorem Provers* (2026, v1)
- S111: Yutong Xin, Qiaochu Chen, Greg Durrett, and Işil Dillig, *VeriSoftBench: Repository-Scale Formal Verification Benchmarks for Lean* (2026 preprint)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P019 — State explosion management

**CURRENT_STATUS:** `MODEL_CHECKING_PROPERTY`  
**LINEAGE_CLASS:** `MODEL_CHECKING_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `model checking`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** model checking lineage

**ORIGINAL_FORM:** Explicit-state model checking encountered combinatorial state explosion; symbolic BDDs, partial-order and symmetry reductions, SAT-based bounded checking, abstraction and CEGAR were successive responses [S008, S009, S036, S061].

**PROBLEM_IT_ADDRESSED:** The product of variables, processes, data values and interleavings makes exhaustive exploration computationally infeasible, causing tools to terminate, simplify away failure modes or consume more engineering effort than the risk warrants.

**ENGINEERING_CLAIM:** Partial-order/symmetry/symbolic/abstraction methods are retained as scalability mechanisms, not proof of model adequacy.

**MECHANISM:** Exploit structure through symbolic state sets, partial-order equivalence, symmetry, abstraction, compositional decomposition, parameter cutoffs and bounded/SAT search. Measure explored state/transition counts, memory/time, reduction ratios and soundness conditions; retreat to focused properties/models when scale remains prohibitive.

**TRIGGER_OR_CONTEXT:** Trigger when state-space estimates or failed runs show combinatorial blow-up in a decision-relevant model.

**NON_TRIGGER_OR_CHEAP_PATH:** Do not introduce sophisticated reductions for a small model; use direct exploration or a simpler invariant.

**DEPENDENCIES_OR_PRECONDITIONS:** Property-preserving reduction theorem/condition, performance metrics and fallback decision rule.

**SPECIFICATION_PRECONDITIONS:** The property is compatible with the equivalence/reduction used.

**ABSTRACTION_PRECONDITIONS:** Independence, symmetry, cutoff or abstract-domain assumptions are justified.

**ENVIRONMENT_PRECONDITIONS:** Fault/environment behaviours are not selectively removed just to achieve tractability.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Reduction preserves implementation-relevant identities and event orders.

**TRUSTED_TOOL_PRECONDITIONS:** Reduction algorithms, hashing, symbolic encodings and resource termination statuses are trustworthy.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Model/property changes trigger state-space/reduction revalidation; cached reductions are not presumed reusable.

**KNOWN_FAILURE_MODES:**
- Reduction relies on an invalid independence relation.
- Symbolic representation blows up despite compact headline potential.
- Symmetry merges identities relevant to the property.
- Abstraction produces endless spurious counterexamples.
- Parameter cutoff is guessed rather than proved.
- Scale pressure leads to omission of faults/data values without disclosure.
- Optimal reduction search itself becomes computationally hard [S103].

**IMPORTANT_CRITICISMS:**
- No reduction eliminates worst-case complexity; scaling claims are structure-dependent.
- Engineering effort to design abstractions/reductions can exceed direct testing or redesign.
- State-count headlines are poor cross-model assurance metrics.
- Reduction soundness says nothing about model adequacy.

**HOW_THE_PROPERTY_EVOLVED:** The field moved from larger hardware and explicit search to symbolic encodings, partial-order/symmetry algorithms, CEGAR, compositional and parameterised verification, and hybrid testing/model checking. Current complexity results reinforce that mature practice selects risk-focused models rather than promising universal exhaustive scale.

**MATURE_OR_EVOLVED_FORM:** Use reductions with explicit preservation arguments and report both reduced and conceptual scope. If tractability requires excluding material behaviours, narrow the claim or switch to hybrid evidence. State explosion is a method-selection constraint, not a reason to hide bounds.

**EXPECTED_ENGINEERING_PAYOFF:** Extends exhaustive or systematic challenge to larger systems while retaining trace diagnostics and makes cost/scalability trade-offs explicit.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can reduction soundness and omitted independence assumptions be reviewed cheaply?
- Which learned heuristics improve scale without benchmark overfitting or hidden unsoundness?
- When should a team stop refining a model and invest in architecture simplification or runtime evidence instead?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S008, S009, S036, S061  
**CRITICAL_SOURCES:** S061, S103  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S009, S032, S033, S052, S054  
**CONTRARY_EVIDENCE:** S061, S103

**SOURCE IDENTITIES USED:**
- S008: J. R. Burch, E. M. Clarke, K. L. McMillan, D. L. Dill, and L. J. Hwang, *Symbolic Model Checking: 10^20 States and Beyond* (1992)
- S009: Gerard J. Holzmann, *The Model Checker SPIN* (1997)
- S036: Armin Biere, Alessandro Cimatti, Edmund Clarke, and Yunshan Zhu, *Symbolic Model Checking without BDDs* (1999)
- S061: Edmund Clarke, Orna Grumberg, Somesh Jha, Yuan Lu, and Helmut Veith, *Counterexample-Guided Abstraction Refinement* (2000)
- S103: Frédéric Herbreteau, Sarah Larroze-Jardiné, and Igor Walukiewicz, *Partial-Order Reduction Is Hard* (2025)
- S032: Astrée project / Cousot lineage, *Astrée static analyzer project materials* (current accessed 2026-08-12)
- S033: Microsoft Research / Windows, *Static Driver Verifier and SLAM technology* (2000s-current)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P020 — Vacuity and specification-strength checks

**CURRENT_STATUS:** `USEFUL_BUT_EASILY_GAMED`  
**LINEAGE_CLASS:** `MODEL_CHECKING_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `useful but easily gamed`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** model checking lineage

**ORIGINAL_FORM:** Vacuity detection arose in temporal model checking to identify formulas true because a subformula or antecedent was irrelevant. Specification mutation, satisfiability checking and coverage analysis broadened this into tests of whether a formal property can actually distinguish intended failures [S059, S060].

**PROBLEM_IT_ADDRESSED:** A proof may succeed because assumptions are inconsistent, initial states unreachable, antecedents never occur, behaviour disabled or the property too weak. The result is logically true but supplies little or no assurance.

**ENGINEERING_CLAIM:** A green theorem/model-checking result must be challenged for vacuity, unreachable states and overly weak properties.

**MECHANISM:** Check model and assumption satisfiability; require witnesses for preconditions/initial states; perform semantic vacuity analysis; mutate property clauses, assumptions and transitions; test known negative examples; measure whether each clause affects outcomes; review proof obligations changed after failures.

**TRIGGER_OR_CONTEXT:** Trigger for critical temporal/invariant/contract/theorem claims, especially after unexpectedly easy proof or repeated specification changes.

**NON_TRIGGER_OR_CHEAP_PATH:** For a direct local predicate with obvious positive/negative unit cases, run those cases rather than a heavyweight vacuity framework.

**DEPENDENCIES_OR_PRECONDITIONS:** Known good/bad examples, satisfiability tooling, mutation policy and auditable statement history.

**SPECIFICATION_PRECONDITIONS:** Assumptions and initial states have witnesses; each material clause can affect an allowed behaviour.

**ABSTRACTION_PRECONDITIONS:** Vacuity is not an artefact of abstraction eliminating trigger behaviours.

**ENVIRONMENT_PRECONDITIONS:** The environment model permits realistic triggering/failing cases.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Negative examples and triggers map to implementation/deployment scenarios where the claim is operational.

**TRUSTED_TOOL_PRECONDITIONS:** Vacuity/mutation engines preserve formula semantics and report unsupported constructs.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Specification and proof-obligation diffs are reviewed; strength tests replay after every relevant change.

**KNOWN_FAILURE_MODES:**
- A request–response property passes because no request can occur.
- An invariant is true only because initial states are empty.
- An implication antecedent is permanently false.
- A property omits the failing behaviour and remains green under mutation.
- Engineers weaken the “golden theorem” until automation succeeds.
- Generated specifications reproduce benchmark answers or expected examples rather than general intent.

**IMPORTANT_CRITICISMS:**
- Formula truth and proof checking do not measure specification strength.
- Vacuity detectors themselves cover particular logics and definitions; nonvacuity is not full correctness.
- Mutation scores can become another proxy and be gamed.
- Human validation remains necessary to decide whether a changed clause matters to stakeholders.

**HOW_THE_PROPERTY_EVOLVED:** ACTL/LTL vacuity algorithms evolved into semantic vacuity, coverage, mutation model checking, proof-obligation audits, assumption consistency checks and generated-specification challenge sets. Current AI work adds held-out examples, roundtrip equivalence and contamination controls.

**MATURE_OR_EVOLVED_FORM:** A critical formal property must demonstrate satisfiable scope, reachable meaningful cases, sensitivity to each material clause and rejection of known bad scenarios. The theorem/specification change history is reviewed to distinguish legitimate correction from proof gaming.

**EXPECTED_ENGINEERING_PAYOFF:** Detects false confidence before release, exposes weak/irrelevant specifications, and makes proof success harder to obtain by excluding the problem.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which specification-strength metrics correlate with field defect prevention rather than benchmark score?
- How can vacuity and mutation analyses scale to theorem-prover specifications and hyperproperties?
- What governance best distinguishes legitimate specification revision from outcome-driven weakening?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S059, S060  
**CRITICAL_SOURCES:** S059, S060, S100, S101, S102  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S052, S065, S054  
**CONTRARY_EVIDENCE:** S059, S060, S100, S101, S102

**SOURCE IDENTITIES USED:**
- S059: Ilan Beer et al., *Efficient Detection of Vacuity in ACTL Formulas* (1997)
- S060: Orna Kupferman and Moshe Y. Vardi, *Vacuity Detection in Temporal Model Checking* (2003)
- S100: Eric Mugnier, Yuanyuan Zhou, Ranjit Jhala, and Michael Coblenz, *On the Impact of Formal Verification on Software Development* (2025)
- S101: Jiayi Wu, Robert Joseph George, and Anima Anandkumar, *ITPEval: Benchmarking Formal Translation Across Interactive Theorem Provers* (2026, v1)
- S102: Daneshvar Amrollahi, Jerry Lopez, and Clark Barrett, *Faithful Autoformalization via Roundtrip Verification and Repair* (2026, v1)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S065: Maurice H. ter Beek, Rod Chapman, Rance Cleaveland, Hubert Garavel, Rong Gu, Ivo ter Horst, Jeroen J. A. Keiren, Thierry Lecomte, Michael Leuschel, Kristin Yvonne Rozier, Augusto Sampaio, Cristina Seceleanu, Martyn Thomas, Tim A. C. Willemse, and Lijun Zhang, *Formal Methods in Industry* (2025)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P021 — Mechanical proof replay

**CURRENT_STATUS:** `THEOREM_PROVING_PROPERTY`  
**LINEAGE_CLASS:** `THEOREM_PROVING_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `theorem proving`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** theorem proving lineage

**ORIGINAL_FORM:** LCF-style provers made every theorem derive through a small trusted inference kernel; HOL, Isabelle and Coq/Rocq developed interactive proof scripts, tactics and proof objects that could be replayed mechanically. Large verified-software projects turned replay into a build artefact [S042–S044, S050].

**PROBLEM_IT_ADDRESSED:** A persuasive hand proof, review note or one-time interactive session cannot reliably establish that every inference remains valid, that dependencies are available, or that the theorem still follows after change.

**ENGINEERING_CLAIM:** Critical logical arguments should be replayable by a proof checker against explicit assumptions when proof evidence is material.

**MECHANISM:** Store theorem statement, proof source/term, assumptions, dependency graph, prover/library versions and deterministic build command. Re-run the kernel checker from a clean environment; archive logs and artefact hashes; distinguish reconstructed proof, admitted axiom and external oracle result.

**TRIGGER_OR_CONTEXT:** Trigger for any theorem intended to survive author/session context, support assurance credit or be independently consumed.

**NON_TRIGGER_OR_CHEAP_PATH:** For a tiny decidable check, a deterministic verifier/test with archived input/output may be more economical than an interactive proof development.

**DEPENDENCIES_OR_PRECONDITIONS:** Pinned theorem source, proof artefact, dependency versions, build environment and clean replay command.

**SPECIFICATION_PRECONDITIONS:** The replayed theorem is exactly the reviewed engineering statement; no unreviewed weakening or axiom change.

**ABSTRACTION_PRECONDITIONS:** Model/abstraction version is bound to the proof identity.

**ENVIRONMENT_PRECONDITIONS:** External assumptions are recorded; replay does not count as discharging them.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Source/model/binary identifiers consumed by the theorem are recorded separately.

**TRUSTED_TOOL_PRECONDITIONS:** Kernel, parser, logic definition, axioms and any proof-import checker are bounded.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Clean replay occurs after theorem, proof, model, code, library, prover or relevant configuration change.

**KNOWN_FAILURE_MODES:**
- Proof script succeeds only with undeclared local state, cache or plugin.
- Admitted axioms or unsafe commands are hidden in transitive dependencies.
- Tactics are nondeterministic or time/resource sensitive.
- The theorem replays but refers to a stale model or old code version.
- A proof term is unavailable, so success depends on a large tactic/solver stack.
- Library/prover upgrade breaks proof despite unchanged intended theorem.

**IMPORTANT_CRITICISMS:**
- Mechanical replay validates derivation, not requirement translation, assumptions or implementation correspondence.
- Large proof builds can be expensive, brittle and difficult to reproduce [S095, S096].
- A short replay log may hide a large trusted base or generated code path.
- A proof that compiles after theorem weakening is current syntactically but not semantically equivalent.

**HOW_THE_PROPERTY_EVOLVED:** Interactive checking evolved into proof terms, declarative proofs, continuous proof builds, dependency manifests, hermetic containers, proof certificates and independent reconstruction. Current proof engineering treats proofs as maintained software with regression and provenance.

**MATURE_OR_EVOLVED_FORM:** A proof claim is accepted only with a clean, repeatable kernel check tied to exact theorem/model/code identities and a disclosed assumption/dependency set. Replay failure is an assurance failure; replay success is scoped to the checked statement and version.

**EXPECTED_ENGINEERING_PAYOFF:** Eliminates hand-waved inference steps, detects proof breakage early, supports independent review and archival reproducibility, and lets automation be used without trusting its reasoning narrative.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which proof artefact formats best support long-term replay across prover evolution?
- How can large dependency graphs be summarised without concealing axioms or semantic changes?
- What reproducibility threshold is practical for resource-intensive industrial proof builds?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S042, S043, S044, S050  
**CRITICAL_SOURCES:** S095, S100, S096  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S024, S025, S050, S080, S052, S054  
**CONTRARY_EVIDENCE:** S095, S100

**SOURCE IDENTITIES USED:**
- S042: M. J. C. Gordon and T. F. Melham, eds., *Introduction to HOL: A Theorem Proving Environment for Higher Order Logic* (1993)
- S043: The Rocq/Coq proof assistant project, *The Rocq Prover / Coq proof assistant documentation* (current accessed 2026-08-12)
- S044: Tobias Nipkow, Lawrence C. Paulson, and Markus Wenzel, *Isabelle/HOL: A Proof Assistant for Higher-Order Logic* (2002)
- S050: Andrew W. Appel et al., *Verified Software Toolchain / Verifiable C materials* (2010s-current)
- S095: Xiaokun Luan, David Sanán, Zhe Hou, Qiyuan Xu, Chengwei Liu, Yufan Cai, Yang Liu, and Meng Sun, *Why the Proof Fails in Different Versions of Theorem Provers: An Empirical Study of Compatibility Issues in Isabelle* (2025)
- S100: Eric Mugnier, Yuanyuan Zhou, Ranjit Jhala, and Michael Coblenz, *On the Impact of Formal Verification on Software Development* (2025)
- S096: Talia Ringer, Karl Palmskog, Ilya Sergey, Milos Gligoric, and Zachary Tatlock, *QED at Large: A Survey of Engineering of Formally Verified Software* (2019)
- S024: Xavier Leroy, *Formal Verification of a Realistic Compiler* (2009)
- S025: Gerwin Klein et al., *seL4: Formal Verification of an OS Kernel* (2009)
- S080: Ramana Kumar, Magnus O. Myreen, Michael Norrish, and Scott Owens, *CakeML: A Verified Implementation of ML* (2014)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P022 — Trusted kernel/certificate boundary

**CURRENT_STATUS:** `THEOREM_PROVING_PROPERTY`  
**LINEAGE_CLASS:** `THEOREM_PROVING_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `theorem proving`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** theorem proving lineage

**ORIGINAL_FORM:** The LCF architecture concentrated trust in a small kernel; proof-carrying code shifted checking to a small consumer; proof-producing SAT/SMT and certificate reconstruction extended this idea beyond interactive theorem provers [S022, S042–S044, S108, S109].

**PROBLEM_IT_ADDRESSED:** A result from a large prover, solver, optimiser or verifier is only as trustworthy as millions of lines of implementation and translation code unless success can be checked by a smaller, independently understandable base.

**ENGINEERING_CLAIM:** Tool trust must identify the checker kernel, axioms, oracle/solver calls, generated code and unsafe extensions.

**MECHANISM:** Generate proof terms or certificates; check them with a small kernel or independent checker; disclose axioms, parser/logic definitions, preprocessing rules and certificate coverage. Cross-check critical artefacts with independent implementations where feasible.

**TRIGGER_OR_CONTEXT:** Trigger for high-consequence theorem, UNSAT, compiler/verifier or code-acceptance results where trusting the full producer is unacceptable.

**NON_TRIGGER_OR_CHEAP_PATH:** For low-risk local checks, solver diversity, fuzzing and regression tests may be proportionate; document raw solver trust rather than pretending a certificate exists.

**DEPENDENCIES_OR_PRECONDITIONS:** Certificate-capable producer, specified proof format, independent checker, logic/axiom inventory and coverage statement.

**SPECIFICATION_PRECONDITIONS:** The certificate binds the exact formal statement and assumptions reviewed.

**ABSTRACTION_PRECONDITIONS:** Certificates justify abstraction/preprocessing transformations relevant to soundness.

**ENVIRONMENT_PRECONDITIONS:** Physical/deployment assumptions remain outside logical certificate unless separately represented.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Certificate covers the transformation/model relation actually used, not only a back-end formula.

**TRUSTED_TOOL_PRECONDITIONS:** Checker, parser, logic kernel, axioms and compiler/runtime needed to execute it are explicitly bounded.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Certificates are regenerated and rechecked for each changed statement, encoding, producer or checker version.

**KNOWN_FAILURE_MODES:**
- The certificate omits preprocessing, quantifier instantiation or theory lemmas.
- The checker is small but parses a complex untrusted format incorrectly.
- Unsafe axioms/extensions permit false theorems.
- The proof assistant kernel is correct but extraction/code-generation path is not covered.
- Certificate generation is disabled on hard cases and raw solver trust silently resumes.
- Independent checkers share the same flawed semantics or generated code.

**IMPORTANT_CRITICISMS:**
- “Small kernel” is a relative reduction, not zero trust.
- The trusted base includes statement parsing, logic semantics, axioms and hardware/runtime as relevant.
- Certificate production and reconstruction may impose major performance/coverage cost [S108, S109].
- Solver bug evidence shows why the boundary matters but not that every result requires a full certificate [S097].

**HOW_THE_PROPERTY_EVOLVED:** LCF kernels evolved into proof objects, proof-carrying code, DRAT/LRAT and Alethe certificates, proof reconstruction, certifying compilers and per-run verifier translation proofs. The mature form chooses the smallest checker proportionate to claim criticality and records unsupported certificate gaps.

**MATURE_OR_EVOLVED_FORM:** For critical automated results, the acceptance artefact is a replayable proof/certificate checked by an independently bounded kernel, not merely a tool’s “valid/unsat” status. The remaining trusted code and logical axioms are enumerated; non-certifying modes are explicitly downgraded.

**EXPECTED_ENGINEERING_PAYOFF:** Permits aggressive automation while sharply reducing trust in search heuristics and solver internals, supports independent verification and long-term archival checking.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can certificate formats cover preprocessing and theory combinations without prohibitive size?
- What diversity is required for “independent” checkers to reduce common-mode semantic bugs?
- When is differential solver checking cheaper and sufficient compared with proof certificates?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S022, S042, S108, S109, S044, S043  
**CRITICAL_SOURCES:** S094, S097, S108, S109  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S022, S098, S052  
**CONTRARY_EVIDENCE:** S094, S097

**SOURCE IDENTITIES USED:**
- S022: George C. Necula, *Proof-Carrying Code* (1997)
- S042: M. J. C. Gordon and T. F. Melham, eds., *Introduction to HOL: A Theorem Proving Environment for Higher Order Logic* (1993)
- S108: Hanna Lachnitt, Mathias Fleury, Haniel Barbosa, Jibiana Jakpor, Bruno Andreotti, Andrew Reynolds, Hans-Jörg Schurr, Clark Barrett, and Cesare Tinelli, *Improving the SMT Proof Reconstruction Pipeline in Isabelle/HOL* (2025)
- S109: Joseph E. Reeves, Haniel Barbosa, Andrew Reynolds, and Marijn J. H. Heule, *A General Approach for SMT Proof Skeletons* (2026)
- S044: Tobias Nipkow, Lawrence C. Paulson, and Markus Wenzel, *Isabelle/HOL: A Proof Assistant for Higher-Order Logic* (2002)
- S043: The Rocq/Coq proof assistant project, *The Rocq Prover / Coq proof assistant documentation* (current accessed 2026-08-12)
- S094: David Monniaux and Sylvain Boulmé, *The Trusted Computing Base of the CompCert Verified Compiler* (2022)
- S097: Dominik Winterer, Chengyu Zhang, and Zhendong Su, *On the Unusual Effectiveness of Type-Aware Operator Mutations for Testing SMT Solvers* (2020)
- S098: Gaurav Parthasarathy, Thibault Dardinier, Benjamin Bonneau, Peter Müller, and Alexander J. Summers, *Towards Trustworthy Automated Program Verifiers: Formally Validating Translations into an Intermediate Verification Language* (2024)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P023 — Proof maintenance and currentness

**CURRENT_STATUS:** `RETAINED_IN_EVOLVED_FORM`  
**LINEAGE_CLASS:** `THEOREM_PROVING_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `retained in evolved form`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** theorem proving lineage

**ORIGINAL_FORM:** Early formal proofs were often published as fixed mathematical artefacts. Large mechanised developments exposed proofs as version-coupled software; proof repair and empirical compatibility research made change impact and maintenance a distinct engineering problem [S074–S076, S095, S096].

**PROBLEM_IT_ADDRESSED:** Code, specifications, libraries, tactics and provers evolve. A previously checked proof can fail, silently target an old artefact, or be “repaired” by changing the theorem. Proof cost therefore includes lifetime maintenance, not only initial construction.

**ENGINEERING_CLAIM:** Proofs must replay after code/spec/library/tool changes or be marked stale.

**MECHANISM:** Track theorem/proof/model/code dependency graphs; run proofs continuously; classify semantic versus syntactic breakage; perform change-impact analysis; review theorem and assumption diffs; use automated repair only with replay and equivalence checks; budget ownership and deprecation.

**TRIGGER_OR_CONTEXT:** Trigger for proofs intended to govern evolving production artefacts or survive tool/library upgrades.

**NON_TRIGGER_OR_CHEAP_PATH:** For one-off exploratory proofs with no future consumer, archive scope and do not create a permanent maintenance obligation.

**DEPENDENCIES_OR_PRECONDITIONS:** Version control, dependency graph, proof owner, CI/replay resources and semantic review process.

**SPECIFICATION_PRECONDITIONS:** Statement and assumption diffs are first-class review items, not hidden inside proof repair.

**ABSTRACTION_PRECONDITIONS:** Abstraction interfaces are stable or their downstream proof impact is known.

**ENVIRONMENT_PRECONDITIONS:** Changes in configuration/platform assumptions enter the dependency graph.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Code/model linkage detects when implementation changes should invalidate or rerun proof.

**TRUSTED_TOOL_PRECONDITIONS:** Prover/library/tactic/solver version changes are captured and revalidated.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Continuous clean replay and semantic diff review are mandatory; age alone is not currentness.

**KNOWN_FAILURE_MODES:**
- A minor library/prover upgrade breaks thousands of proof steps.
- Automation change finds a different proof but obscures changed assumptions.
- Code change has no dependency edge to the proof model, leaving it falsely green.
- Proof repair weakens the statement or adds axioms.
- Forked libraries prevent reproducible replay.
- Maintenance cost causes teams to freeze code or abandon proof artefacts.

**IMPORTANT_CRITICISMS:**
- Proof brittleness can slow iteration and create incentives to avoid necessary design changes.
- Syntactic compatibility is not semantic currentness.
- Automated repair may optimise compilation rather than preserve engineering meaning.
- Empirical compatibility evidence is currently concentrated in particular prover ecosystems [S095].

**HOW_THE_PROPERTY_EVOLVED:** Proof scripts evolved toward stable declarative proofs, abstraction layers, reusable libraries, dependency analysis, proof-repair datasets, equivalence-aware repair and continuous integration. Mature projects treat proof architecture and deprecation as lifecycle design.

**MATURE_OR_EVOLVED_FORM:** A formal result has an owner, dependency manifest, clean continuous replay, theorem/assumption diff review, impact rules and retirement threshold. Repair is accepted only when the checked claim is unchanged or the change is explicitly revalidated.

**EXPECTED_ENGINEERING_PAYOFF:** Prevents stale assurance, exposes maintenance cost before adoption, preserves trustworthy change velocity and supports selective investment in stable critical interfaces.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which proof architectures minimise semantic maintenance cost across realistic software evolution?
- How reliably can tools distinguish harmless refactoring from changed theorem meaning?
- What empirical ROI models include multi-year proof maintenance and avoided regressions?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S074, S075, S076, S096, S095  
**CRITICAL_SOURCES:** S076, S095  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S024, S025, S050, S095, S051, S052, S113  
**CONTRARY_EVIDENCE:** S076, S095

**SOURCE IDENTITIES USED:**
- S074: Talia Ringer, RanDair Porter, Nathaniel Yazdani, John Leo, and Dan Grossman, *Proof Repair across Type Equivalences* (2021)
- S075: Tom Reichel, R. Wesley Henderson, Andrew Touchet, Andrew Gardner, and Talia Ringer, *Proof Repair Infrastructure for Supervised Models: Building a Large Proof Repair Dataset* (2023)
- S076: Ana de Almeida Borges, Annalí Casanueva Artís, Jean-Rémy Falleri, Emilio Jesús Gallego Arias, Érik Martin-Dorel, Karl Palmskog, Alexander Serebrenik, and Théo Zimmermann, *Lessons for Interactive Theorem Proving Researchers from a Survey of Coq Users* (2025)
- S096: Talia Ringer, Karl Palmskog, Ilya Sergey, Milos Gligoric, and Zachary Tatlock, *QED at Large: A Survey of Engineering of Formally Verified Software* (2019)
- S095: Xiaokun Luan, David Sanán, Zhe Hou, Qiyuan Xu, Chengwei Liu, Yufan Cai, Yang Liu, and Meng Sun, *Why the Proof Fails in Different Versions of Theorem Provers: An Empirical Study of Compatibility Issues in Isabelle* (2025)
- S024: Xavier Leroy, *Formal Verification of a Realistic Compiler* (2009)
- S025: Gerwin Klein et al., *seL4: Formal Verification of an OS Kernel* (2009)
- S050: Andrew W. Appel et al., *Verified Software Toolchain / Verifiable C materials* (2010s-current)
- S051: Federal Aviation Administration, *AC 20-115D: Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178* (2017)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S113: Federal Aviation Administration, *AC 20-148: Reusable Software Components* (current guidance lineage, accessed 2026-08-12)


### P024 — Solver/encoding trust boundary

**CURRENT_STATUS:** `CONTEXT_DEPENDENT`  
**LINEAGE_CLASS:** `SMT_SAT_SYMBOLIC_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `context dependent`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** SMT/SAT/symbolic lineage

**ORIGINAL_FORM:** SAT decision procedures and SMT combination frameworks enabled automated discharge over propositional logic, arithmetic, arrays, bit-vectors and uninterpreted functions. Modern program verifiers encode proof obligations into SMT, often trusting front-end translation and solver answers [S038–S041].

**PROBLEM_IT_ADDRESSED:** An UNSAT/SAT result can be wrong because the engineering property was encoded incorrectly, arithmetic/bit widths differ, quantifiers trigger incompletely, the solver returns UNKNOWN/timeout, or the solver itself has a soundness defect.

**ENGINEERING_CLAIM:** SAT/SMT results require checked encodings, theory declarations, solver version/status and certificate strategy where risk warrants.

**MECHANISM:** Specify logic/theories and exact encoding; distinguish SAT, UNSAT, UNKNOWN and timeout; cross-check or fuzz solvers; validate front-end translation; request proof certificates/unsat cores/models; reconstruct critical UNSAT proofs independently; test floating-point and nonlinear corner semantics.

**TRIGGER_OR_CONTEXT:** Trigger whenever an SMT/SAT result discharges a material proof obligation or controls acceptance.

**NON_TRIGGER_OR_CHEAP_PATH:** For a small decidable predicate, use a direct evaluator/exhaustive table; for low-risk checks, archive solver inputs and cross-check selectively.

**DEPENDENCIES_OR_PRECONDITIONS:** Exact formula/encoding, theory semantics, solver/options, result handling and certificate/cross-check policy.

**SPECIFICATION_PRECONDITIONS:** Engineering units, domains, undefined behaviour and quantification are represented faithfully.

**ABSTRACTION_PRECONDITIONS:** Encoding approximations and theory relaxations preserve the claimed direction.

**ENVIRONMENT_PRECONDITIONS:** Hardware numerical semantics and runtime domains match the encoded theory.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Verification-condition generator and front-end translation are validated or trusted explicitly.

**TRUSTED_TOOL_PRECONDITIONS:** Solver, parser, preprocessing, certificate producer/checker and front-end translator are bounded.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Formula, encoder, solver/options or theory-version changes require new result/certificate.

**KNOWN_FAILURE_MODES:**
- Wrong sign, units, quantifier scope or bit-vector width in encoding.
- Timeout/UNKNOWN is coerced to success or failure.
- Solver model is misinterpreted because of partial/underspecified functions.
- Unsat core omits a preprocessing bug or is treated as proof of requirement relevance.
- Solver soundness bug returns false UNSAT [S097].
- Front-end to intermediate-language translation is unsound [S098].
- Floating-point operation is approximated as real arithmetic.

**IMPORTANT_CRITICISMS:**
- SMT automation can make the most trusted step the least visible to engineers.
- Solver diversity may share algorithms/code or the same encoding error.
- Certificates can be huge or incomplete for preprocessing/theory reasoning [S108, S109].
- Unsat cores explain logical dependence, not engineering correctness.

**HOW_THE_PROPERTY_EVOLVED:** Raw solver trust evolved toward standardised SMT-LIB, differential fuzzing, model validation, proof-producing solvers, Alethe/LRAT-style certificates, independent reconstruction and certifying verifier front ends. Mature use scales trust controls with consequence.

**MATURE_OR_EVOLVED_FORM:** A solver-mediated claim records formula hash, logic, solver/version/options, result class and encoding source. Critical UNSAT results carry independently checked certificates or redundant evidence; UNKNOWN/timeout never becomes pass; arithmetic and units are reviewed.

**EXPECTED_ENGINEERING_PAYOFF:** Retains high automation and scalability while reducing false proof from encoding and solver defects, and makes solver outputs reproducible and diagnosable.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Can practical certificates cover all high-performance preprocessing and theory combinations?
- Which differential/fuzzing strategies best detect encoding bugs rather than only solver bugs?
- How should solver uncertainty and timeout be integrated into assurance decisions?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S038, S039, S040, S041  
**CRITICAL_SOURCES:** S097, S098, S108, S109  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S038, S050, S098, S052, S054  
**CONTRARY_EVIDENCE:** S097, S098, S108, S109

**SOURCE IDENTITIES USED:**
- S038: Leonardo de Moura and Nikolaj Bjørner, *Z3: An Efficient SMT Solver* (2008)
- S039: SMT-LIB initiative, *The SMT-LIB Standard: Language and Logics* (current accessed 2026-08-12)
- S040: Greg Nelson and Derek C. Oppen, *Simplification by Cooperating Decision Procedures* (1979)
- S041: Martin Davis, George Logemann, and Donald Loveland, *A Machine Program for Theorem-Proving* (1962)
- S097: Dominik Winterer, Chengyu Zhang, and Zhendong Su, *On the Unusual Effectiveness of Type-Aware Operator Mutations for Testing SMT Solvers* (2020)
- S098: Gaurav Parthasarathy, Thibault Dardinier, Benjamin Bonneau, Peter Müller, and Alexander J. Summers, *Towards Trustworthy Automated Program Verifiers: Formally Validating Translations into an Intermediate Verification Language* (2024)
- S108: Hanna Lachnitt, Mathias Fleury, Haniel Barbosa, Jibiana Jakpor, Bruno Andreotti, Andrew Reynolds, Hans-Jörg Schurr, Clark Barrett, and Cesare Tinelli, *Improving the SMT Proof Reconstruction Pipeline in Isabelle/HOL* (2025)
- S109: Joseph E. Reeves, Haniel Barbosa, Andrew Reynolds, and Marijn J. H. Heule, *A General Approach for SMT Proof Skeletons* (2026)
- S050: Andrew W. Appel et al., *Verified Software Toolchain / Verifiable C materials* (2010s-current)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P025 — Symbolic execution/path constraint scope

**CURRENT_STATUS:** `CONTEXT_DEPENDENT`  
**LINEAGE_CLASS:** `SMT_SAT_SYMBOLIC_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `context dependent`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** SMT/SAT/symbolic lineage

**ORIGINAL_FORM:** King’s symbolic execution represented inputs symbolically and accumulated path conditions; KLEE and modern concolic tools coupled path exploration with constraint solvers and test generation [S085, S034, S035].

**PROBLEM_IT_ADDRESSED:** Concrete tests cover one input/path at a time and miss deep branches. Symbolic execution can systematically generate inputs that exercise paths and reveal assertion, memory, arithmetic or protocol failures.

**ENGINEERING_CLAIM:** Symbolic execution gives path evidence and generated tests under explicit path/environment/solver bounds.

**MECHANISM:** Execute program semantics over symbolic values, fork at branches, solve path constraints, generate concrete witnesses and combine with search heuristics, state merging, summaries, concolic execution and environment models. Report path/time bounds and solver UNKNOWN separately.

**TRIGGER_OR_CONTEXT:** Trigger for input-rich, branch-heavy code where concrete witness generation is valuable and semantics/environment can be modelled.

**NON_TRIGGER_OR_CHEAP_PATH:** Use fuzzing/property-based tests for cheap broad exploration, or direct proof/static analysis when all-path assurance is required and tractable.

**DEPENDENCIES_OR_PRECONDITIONS:** Executable semantics, constraint theories, environment models, search/bound disclosure and concrete replay harness.

**SPECIFICATION_PRECONDITIONS:** Assertions/properties checked are meaningful and not merely crash proxies.

**ABSTRACTION_PRECONDITIONS:** Stubs, summaries and state merging preserve witness validity or are labelled approximate.

**ENVIRONMENT_PRECONDITIONS:** System calls, files, network, time and nondeterminism are modelled or bounded explicitly.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Generated witness is replayed on the actual implementation/build where feasible.

**TRUSTED_TOOL_PRECONDITIONS:** Symbolic interpreter, solver, constraint encoding and concrete test generator are trusted/tested.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Witnesses and exploration campaigns rerun after code/semantics/environment changes.

**KNOWN_FAILURE_MODES:**
- Path explosion prevents broad coverage.
- Environment/system calls are stubbed unrealistically.
- Constraint solver cannot decide nonlinear, floating-point or complex theories.
- Infeasible paths consume resources due to weak constraints.
- Loop/recursion bounds hide deeper failures.
- Undefined behaviour or language semantics differ from the symbolic interpreter.
- High branch coverage is treated as functional correctness.

**IMPORTANT_CRITICISMS:**
- Path coverage is not environment or behavioural completeness.
- Generated tests inherit the symbolic semantics and stubs; differential execution is needed.
- Search heuristics can overfit familiar benchmarks or shallow defects.
- Symbolic execution is often strongest as test generation, not proof.

**HOW_THE_PROPERTY_EVOLVED:** Pure symbolic execution evolved into concolic execution, selective/path-directed search, compositional summaries, state merging, fuzzing hybrids and bounded model checking. Mature practice uses it to generate high-value witnesses and tests with explicit scope rather than claiming universal verification.

**MATURE_OR_EVOLVED_FORM:** Use symbolic execution for path-sensitive bug finding or focused bounded proof, with exact loop/path/environment bounds, concrete replay of witnesses and complementary fuzzing/testing. Universal claims require a completeness argument or another method.

**EXPECTED_ENGINEERING_PAYOFF:** Finds difficult path-specific defects and produces reproducible inputs more efficiently than manual test design for suitable code.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can environment models and complex libraries be represented without dominating false positives?
- Which hybrid fuzzing/symbolic policies give robust transfer beyond benchmark suites?
- How should path coverage be related to specification coverage rather than branch counts?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S085, S034, S035  
**CRITICAL_SOURCES:** S035  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S034, S035, S052  
**CONTRARY_EVIDENCE:** S035

**SOURCE IDENTITIES USED:**
- S085: James C. King, *Symbolic Execution and Program Testing* (1976)
- S034: Cristian Cadar, Daniel Dunbar, and Dawson Engler, *KLEE: Unassisted and Automatic Generation of High-Coverage Tests for Complex Systems Programs* (2008)
- S035: Cristian Cadar and Koushik Sen, *Symbolic Execution for Software Testing: Three Decades Later* (2013)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P026 — Sound versus unsound static analysis boundary

**CURRENT_STATUS:** `STATIC_ANALYSIS_TYPE_PROPERTY`  
**LINEAGE_CLASS:** `STATIC_ANALYSIS_AND_ABSTRACT_INTERPRETATION_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `static analysis type`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** static analysis and abstract interpretation lineage

**ORIGINAL_FORM:** Abstract interpretation framed sound static analysis as conservative approximation; industrial analysers such as Astrée pursued absence-of-runtime-error claims, while many developer-oriented analysers deliberately traded soundness for speed and usability [S005, S032, S033].

**PROBLEM_IT_ADDRESSED:** A green static-analysis dashboard is ambiguous unless users know whether the analyser over-approximates all behaviours, intentionally misses cases, suppresses warnings, or only applies to a language/platform subset.

**ENGINEERING_CLAIM:** Static analysis claims must identify whether the analysis is sound for the language/property and what false positives/negatives mean.

**MECHANISM:** Publish the soundness target, concrete semantics, supported constructs, false-negative policy and alarm interpretation. For sound analysers, treat alarms as possible behaviours requiring triage/refinement; for unsound analysers, treat green as heuristic evidence only. Measure suppressions and unanalysed code.

**TRIGGER_OR_CONTEXT:** Trigger whenever a static analyser’s green/red result is used as evidence beyond local developer feedback.

**NON_TRIGGER_OR_CHEAP_PATH:** Use fast unsound linting freely for low-risk feedback, but label it and do not demand proof-grade governance.

**DEPENDENCIES_OR_PRECONDITIONS:** Documented language/platform semantics, soundness target, supported-code inventory and suppression governance.

**SPECIFICATION_PRECONDITIONS:** The defect classes checked are named; no warning is not conflated with functional correctness.

**ABSTRACTION_PRECONDITIONS:** Transfer functions and widening preserve soundness for claimed classes.

**ENVIRONMENT_PRECONDITIONS:** Libraries, concurrency, inputs and hardware assumptions are within analyser semantics.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** The exact source/build analysed is captured and unsupported portions identified.

**TRUSTED_TOOL_PRECONDITIONS:** Front end, abstract interpreter, solver and configuration are qualified/tested proportionally.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Analysis reruns on source/config/tool changes; suppressions expire or are revalidated.

**KNOWN_FAILURE_MODES:**
- An unsound analyser’s silence is marketed as proof.
- A sound analyser’s false positives are mass-suppressed without justification.
- Unsupported language/assembly/library constructs are skipped.
- Concurrency/environment semantics are approximated inadequately.
- Widening or configuration loses useful precision.
- A warning count becomes an assurance proxy independent of severity/coverage.

**IMPORTANT_CRITICISMS:**
- Soundness can impose false-positive and usability costs; unsoundness can improve adoption but weakens absence claims.
- The analyser’s concrete semantics may differ from compiler/hardware behaviour.
- Domain-specific success such as Astrée may not transfer to arbitrary software.
- Suppression and configuration governance can dominate theoretical soundness.

**HOW_THE_PROPERTY_EVOLVED:** Static analysis diversified into sound domain-specific analysers, scalable unsound bug finders, gradual verification, refinement types and proof-producing/certified analyses. Mature practice makes the soundness/coverage contract explicit and chooses the trade-off by decision consequence.

**MATURE_OR_EVOLVED_FORM:** Every static-analysis result declares whether absence of warnings is a sound guarantee, a bounded guarantee or a heuristic. Unsupported code, suppressions and modelling assumptions are measurable; high-consequence claims use sound or independently validated analysis.

**EXPECTED_ENGINEERING_PAYOFF:** Prevents overclaiming green dashboards, helps teams balance false positives against missed defects, and directs qualification effort to analysers whose absence claims matter.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can organisations empirically tune soundness/usability without normalising false negatives?
- Which suppression-review practices preserve trust over time?
- Can proof-producing analyses deliver soundness with acceptable industrial performance across broader domains?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S005, S032, S033  
**CRITICAL_SOURCES:** S064, S065  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S032, S033, S052, S054  
**CONTRARY_EVIDENCE:** S064, S065

**SOURCE IDENTITIES USED:**
- S005: Patrick Cousot and Radhia Cousot, *Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints* (1977)
- S032: Astrée project / Cousot lineage, *Astrée static analyzer project materials* (current accessed 2026-08-12)
- S033: Microsoft Research / Windows, *Static Driver Verifier and SLAM technology* (2000s-current)
- S064: Mario Gleirscher and Diego Marmsoler, *Formal Methods in Dependable Systems Engineering: A Survey of Professionals from Europe and North America* (2020)
- S065: Maurice H. ter Beek, Rod Chapman, Rance Cleaveland, Hubert Garavel, Rong Gu, Ivo ter Horst, Jeroen J. A. Keiren, Thierry Lecomte, Michael Leuschel, Kristin Yvonne Rozier, Augusto Sampaio, Cristina Seceleanu, Martyn Thomas, Tim A. C. Willemse, and Lijun Zhang, *Formal Methods in Industry* (2025)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P027 — Type-system claim boundary

**CURRENT_STATUS:** `STATIC_ANALYSIS_TYPE_PROPERTY`  
**LINEAGE_CLASS:** `TYPE_SYSTEM_AND_DEPENDENT_TYPE_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `static analysis type`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** type system and dependent type lineage

**ORIGINAL_FORM:** Type systems formalised well-formedness and type safety through progress/preservation; dependent, refinement, ownership, effect and session types later encoded richer properties in typing judgements [S045–S047, S089].

**PROBLEM_IT_ADDRESSED:** “Type-safe” is often inflated into “correct”. Ordinary typing prevents specific representation and operation mismatches but may say nothing about algorithmic result, liveness, security policy, numerical validity or stakeholder requirement.

**ENGINEERING_CLAIM:** Type safety, memory safety and noninterference are retained as precise claims, not functional correctness by implication.

**MECHANISM:** State the exact typing theorem and excluded stuck/error classes; map each type feature to an engineering claim; identify unsafe casts, foreign interfaces, dynamic checks and semantic gaps. Use richer types only where the encoded proposition and proof obligations justify the cost.

**TRIGGER_OR_CONTEXT:** Trigger whenever type safety, Rust ownership, session/refinement/dependent types or “compiles” is used as an assurance claim.

**NON_TRIGGER_OR_CHEAP_PATH:** Use ordinary types for ordinary representation safety; do not encode volatile business logic at the type level without clear payoff.

**DEPENDENCIES_OR_PRECONDITIONS:** Published language/type soundness scope, compiler/runtime assumptions and inventory of unsafe/dynamic boundaries.

**SPECIFICATION_PRECONDITIONS:** The proposition encoded by the type matches the claimed failure class.

**ABSTRACTION_PRECONDITIONS:** Type abstraction does not hide value/behaviour distinctions material to clients.

**ENVIRONMENT_PRECONDITIONS:** External data and foreign components are validated before entering trusted typed invariants.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Compiler/runtime faithfully implements the type semantics and deployed code avoids unchecked escape hatches.

**TRUSTED_TOOL_PRECONDITIONS:** Type checker, compiler, elaborator, SMT back end and unsafe libraries are bounded.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Type and unsafe-boundary checks rerun after language/compiler/library/API changes.

**KNOWN_FAILURE_MODES:**
- A well-typed program computes the wrong result.
- Unsafe/FFI code violates type invariants.
- Nontermination is permitted by the type system.
- Effects, concurrency or information flow are outside the type discipline.
- A nominal type preserves syntax but not units or behavioural contract.
- Compiler/runtime unsoundness breaks the language theorem.

**IMPORTANT_CRITICISMS:**
- Type safety is a precise but narrow meta-theorem.
- Strong types can shift complexity into casts, proof terms or awkward APIs.
- Behavioural subtyping and refinement types depend on specifications/SMT encodings [S047, S089].
- Safe-language boundaries still require verification of unsafe libraries [S046].

**HOW_THE_PROPERTY_EVOLVED:** Simple static types evolved into algebraic/dependent/refinement types, ownership/borrowing, effects, typestate, sessions and information-flow types. Mature use treats each as a selective proof carrier, never as a generic correctness label.

**MATURE_OR_EVOLVED_FORM:** A type-system claim names the prevented failure classes, unsafe boundary and remaining obligations. Stronger types are introduced where they eliminate material misuse or encode stable invariants; functional or temporal correctness is claimed only when represented and proved in the type.

**EXPECTED_ENGINEERING_PAYOFF:** Eliminates broad classes of representational, memory, protocol-state or interface misuse early and cheaply, while preventing marketing overreach.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which richer type guarantees deliver the best maintenance-adjusted payoff in evolving APIs?
- How can unsafe/FFI boundaries be audited compositionally?
- How should type-level quantitative/unit properties interact with runtime data uncertainty?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S045, S046, S047, S089  
**CRITICAL_SOURCES:** S046, S089, S047  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S046, S077, S078, S052  
**CONTRARY_EVIDENCE:** S046, S089

**SOURCE IDENTITIES USED:**
- S045: Per Martin-Löf, *Intuitionistic Type Theory* (1984)
- S046: Ralf Jung et al., *RustBelt: Securing the Foundations of the Rust Programming Language* (2018)
- S047: Niki Vazou et al., *Refinement Types for Haskell* (2014)
- S089: Barbara H. Liskov and Jeannette M. Wing, *A Behavioral Notion of Subtyping* (1994)
- S077: Jonathan Protzenko et al., *EverCrypt: A Fast, Verified, Cross-Platform Cryptographic Provider* (2020)
- S078: Jean-Karim Zinzindohoué et al., *HACL*: A Verified Modern Cryptographic Library* (2017)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P028 — Dependent/refinement types as selective proof carriers

**CURRENT_STATUS:** `STATIC_ANALYSIS_TYPE_PROPERTY`  
**LINEAGE_CLASS:** `TYPE_SYSTEM_AND_DEPENDENT_TYPE_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `static analysis type`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** type system and dependent type lineage

**ORIGINAL_FORM:** Martin-Löf type theory embodied propositions as types; proof assistants used dependent types for machine-checked mathematics/programs; refinement types coupled logical predicates to ordinary programming languages and SMT automation [S045, S043, S047].

**PROBLEM_IT_ADDRESSED:** Some stable value-level invariants—length relations, protocol states, units, bounds or functional equations—must travel with data/functions. External proofs can drift from the code they justify.

**ENGINEERING_CLAIM:** Specification-rich types can carry selected proof obligations when properties fit type-level automation/review.

**MECHANISM:** Encode selected propositions in dependent/refinement types; require inhabitants/proof terms or discharge refinements through SMT; extract or execute verified functions; keep trusted escape hatches and erasure/runtime semantics explicit.

**TRIGGER_OR_CONTEXT:** Trigger when a stable data/API invariant is repeatedly violated and can be encoded locally with manageable proof burden.

**NON_TRIGGER_OR_CHEAP_PATH:** Use runtime validation or ordinary types for volatile policy, uncertain sensor input or properties whose proof cost exceeds reuse value.

**DEPENDENCIES_OR_PRECONDITIONS:** Stable invariant, supporting libraries/automation, programmer expertise and bounded extraction/unsafe interfaces.

**SPECIFICATION_PRECONDITIONS:** The type proposition expresses the intended value relation and handles partial/exceptional cases.

**ABSTRACTION_PRECONDITIONS:** Type indices/refinements preserve relevant runtime semantics after erasure.

**ENVIRONMENT_PRECONDITIONS:** Untrusted external inputs are checked before constructing trusted typed values.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Elaboration, extraction/compiler and FFI preserve typed guarantees.

**TRUSTED_TOOL_PRECONDITIONS:** Kernel/type checker, axioms, SMT solver and extraction path are disclosed.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Types/proofs rebuild after API/library/tool changes; repaired types are semantically diff-reviewed.

**KNOWN_FAILURE_MODES:**
- The encoded proposition is weaker/different from the engineering requirement.
- Proof obligations become annotation-heavy and brittle.
- SMT automation times out or depends on fragile qualifiers.
- Proof erasure or extraction introduces a runtime gap.
- Inconsistent axioms or partiality permit unsound inhabitants.
- Developers bypass types with unsafe casts or admitted terms.

**IMPORTANT_CRITICISMS:**
- Maximal dependent typing can impair readability, interoperability and iteration speed.
- Proof by type checking is only as meaningful as the type specification.
- Automation and library coupling create maintenance costs.
- Not all environmental, temporal or quantitative uncertainty fits a static type.

**HOW_THE_PROPERTY_EVOLVED:** Fully dependently typed programming diversified into refinement types, gradual verification, proof irrelevance/erasure, certified extraction and domain-specific verified libraries. Mature practice uses strong types selectively at stable, high-value boundaries.

**MATURE_OR_EVOLVED_FORM:** Use dependent/refinement types as proof carriers for compact, stable invariants that callers must preserve. The type’s proposition, SMT/axiom boundary, extraction path and unsafe escape hatches are reviewed; volatile system behaviour remains in contracts, models or tests.

**EXPECTED_ENGINEERING_PAYOFF:** Makes important invariants impossible or difficult to violate through ordinary construction, couples evidence to APIs and enables verified reusable components.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can refinement/dependent proofs survive API and library evolution with lower repair cost?
- Which specifications should remain dynamic to avoid overconstraining systems?
- How can extracted-code and foreign-interface correspondence be made routine?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S045, S043, S047  
**CRITICAL_SOURCES:** S076, S096  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S077, S078, S080, S052  
**CONTRARY_EVIDENCE:** S076, S096

**SOURCE IDENTITIES USED:**
- S045: Per Martin-Löf, *Intuitionistic Type Theory* (1984)
- S043: The Rocq/Coq proof assistant project, *The Rocq Prover / Coq proof assistant documentation* (current accessed 2026-08-12)
- S047: Niki Vazou et al., *Refinement Types for Haskell* (2014)
- S076: Ana de Almeida Borges, Annalí Casanueva Artís, Jean-Rémy Falleri, Emilio Jesús Gallego Arias, Érik Martin-Dorel, Karl Palmskog, Alexander Serebrenik, and Théo Zimmermann, *Lessons for Interactive Theorem Proving Researchers from a Survey of Coq Users* (2025)
- S096: Talia Ringer, Karl Palmskog, Ilya Sergey, Milos Gligoric, and Zachary Tatlock, *QED at Large: A Survey of Engineering of Formally Verified Software* (2019)
- S077: Jonathan Protzenko et al., *EverCrypt: A Fast, Verified, Cross-Platform Cryptographic Provider* (2020)
- S078: Jean-Karim Zinzindohoué et al., *HACL*: A Verified Modern Cryptographic Library* (2017)
- S080: Ramana Kumar, Magnus O. Myreen, Michael Norrish, and Scott Owens, *CakeML: A Verified Implementation of ML* (2014)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P029 — Concurrency/distributed protocol modelling

**CURRENT_STATUS:** `DOMAIN_SPECIFIC`  
**LINEAGE_CLASS:** `CONCURRENCY_PROCESS_ALGEBRA_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `domain specific`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** concurrency/process algebra lineage

**ORIGINAL_FORM:** CSP/CCS, temporal logic and labelled transition systems formalised communication and interleavings; distributed verification later added message loss/reordering, faults, replicated state, refinement and mechanised protocol proofs in TLA+, IronFleet and Verdi [S017–S019, S029–S031].

**PROBLEM_IT_ADDRESSED:** Concurrent/distributed failures arise from enormous interleaving spaces, races, deadlocks, stale messages, partitions, retries, weak memory and failures that ordinary sequential reasoning or happy-path testing misses.

**ENGINEERING_CLAIM:** Interleavings, message loss/reorder, crash/recovery, consensus and weak memory need explicit formal semantics when they determine failure.

**MECHANISM:** Model processes, messages/shared memory, network/failure semantics, scheduler/fairness and protocol state; check invariants, deadlock, liveness and refinement; use partial-order/symmetry reduction, compositional contracts, linearizability/serialisability and implementation transformers; stress assumptions empirically.

**TRIGGER_OR_CONTEXT:** Trigger for coordination, replication, concurrency, distributed workflows, lock-free algorithms, weak-memory code or fault-tolerant protocols.

**NON_TRIGGER_OR_CHEAP_PATH:** For simple isolated concurrency, race detectors/stress tests or a small state machine may remove the risk more cheaply than full protocol proof.

**DEPENDENCIES_OR_PRECONDITIONS:** Explicit process/network/memory/failure model, property classes, implementation event mapping and fault-test plan.

**SPECIFICATION_PRECONDITIONS:** Safety, liveness, consistency, availability and durability claims are separated.

**ABSTRACTION_PRECONDITIONS:** Data/participant/reduction abstractions preserve the protocol property and failure behaviours.

**ENVIRONMENT_PRECONDITIONS:** Network, scheduler, clock, storage and failure-detector assumptions are justified.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Serialization, retries, shims, persistence and weak-memory semantics are covered or separately assured.

**TRUSTED_TOOL_PRECONDITIONS:** Model checker/prover, distributed semantics, reductions and extraction/generation tools are bounded.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Protocol, topology, timeout, storage, compiler and infrastructure changes trigger model/proof/fault-test replay.

**KNOWN_FAILURE_MODES:**
- Network/failure model excludes duplication, reordering, corruption, partitions or recovery.
- Fairness/eventual delivery assumptions do not hold under overload.
- State explosion forces tiny participant/data bounds.
- Protocol proof omits implementation shim, serialization or storage behaviour.
- Weak-memory hardware permits executions absent from source interleaving model.
- Parameterised correctness is inferred from small instances without cutoff.
- A safety proof omits liveness or availability.

**IMPORTANT_CRITICISMS:**
- Famous verified systems still exhibited defects outside model/proof boundaries [S092].
- Concurrency reductions and liveness automation remain hard and assumption-sensitive [S103, S105].
- Weak-memory formalisms show that sequentially consistent interleavings are insufficient for low-level code [S106].
- Operational availability/performance may conflict with strong consistency/refinement properties.

**HOW_THE_PROPERTY_EVOLVED:** Process algebra and temporal specifications evolved into executable TLA+/PlusCal models, mechanised state-machine refinement, distributed separation logics, parameterised verification, liveness ranking frameworks and weak-memory logics. Mature practice combines design-level formal challenge with implementation fault injection, testing and monitoring.

**MATURE_OR_EVOLVED_FORM:** Formalise the smallest protocol core and failure model that governs coordination risk; separate safety, liveness, consistency and availability; state fairness/network/memory assumptions; establish implementation correspondence or downgrade to design evidence; retain empirical chaos/fault testing at the boundary.

**EXPECTED_ENGINEERING_PAYOFF:** Finds rare interleaving and protocol-design defects before deployment, clarifies fault/consistency semantics, and provides reusable invariants for implementation and operations.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can parameterised verification scale to realistic data, membership change and failure combinations?
- What practical methods keep model-code links current across distributed implementation stacks?
- How should deterministic protocol proofs combine with probabilistic infrastructure and performance evidence?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S017, S018, S019, S029, S030, S031, S105  
**CRITICAL_SOURCES:** S092, S103, S106, S105  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S029, S030, S031, S052, S079  
**CONTRARY_EVIDENCE:** S092, S103, S106

**SOURCE IDENTITIES USED:**
- S017: Leslie Lamport, *The Temporal Logic of Actions* (1994)
- S018: C. A. R. Hoare, *Communicating Sequential Processes* (1978)
- S019: Robin Milner, *A Calculus of Communicating Systems* (1980)
- S029: Chris Newcombe et al., *How Amazon Web Services Uses Formal Methods* (2015)
- S030: Chris Hawblitzel et al., *IronFleet: Proving Practical Distributed Systems Correct* (2015)
- S031: James R. Wilcox et al., *Verdi: A Framework for Implementing and Formally Verifying Distributed Systems* (2015)
- S105: Jingyi Yao, Runzhou Tao, Ronghui Gu, and Jason Nieh, *Mostly Automated Verification of Liveness Properties for Distributed Protocols with Ranking Functions* (2024)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S103: Frédéric Herbreteau, Sarah Larroze-Jardiné, and Igor Walukiewicz, *Partial-Order Reduction Is Hard* (2025)
- S106: Roger C. Su and Robert J. Colvin, *Weak Memory Model Formalisms: Introduction and Survey* (2026, Concurrency and Computation: Practice and Experience 38(2))
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S079: Karthikeyan Bhargavan et al., *miTLS: Verifying Protocol Implementations against Real-World Attacks* (2016)


### P030 — Linearizability/serialisability/refinement properties

**CURRENT_STATUS:** `DOMAIN_SPECIFIC`  
**LINEAGE_CLASS:** `CONCURRENCY_PROCESS_ALGEBRA_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `domain specific`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** concurrency/process algebra lineage

**ORIGINAL_FORM:** Serializability related database schedules to serial executions; linearizability related concurrent object histories to legal sequential histories respecting real-time order. Refinement traditions generalised these as observational correctness conditions [S090, S091].

**PROBLEM_IT_ADDRESSED:** “Thread-safe”, “consistent” or “transactional” is too vague. Concurrent operations can return individually plausible values while histories violate atomic-object or database semantics; alternatively, a strong consistency property may be unnecessary or too costly.

**ENGINEERING_CLAIM:** Concurrent object/database claims require explicit observational equivalence/refinement criteria.

**MECHANISM:** Choose the required history/refinement condition; define operations, invocation/response events, transaction conflicts and observer; prove history inclusion, linearisation points, simulation or serial-equivalence; separately check progress, durability and application invariants.

**TRIGGER_OR_CONTEXT:** Trigger when multiple operations overlap or transactions interleave and correctness depends on observable history.

**NON_TRIGGER_OR_CHEAP_PATH:** For single-threaded or externally serialised components, direct invariants/tests may be enough.

**DEPENDENCIES_OR_PRECONDITIONS:** Event/history semantics, observer, operation spec, memory model and progress/durability companion claims.

**SPECIFICATION_PRECONDITIONS:** The selected consistency property matches consumer expectations and does not stand in for omitted liveness/durability.

**ABSTRACTION_PRECONDITIONS:** History abstraction preserves real-time/conflict/observation distinctions.

**ENVIRONMENT_PRECONDITIONS:** Clock/order, storage and external side-effect assumptions are explicit.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Invocation/response/commit events and memory semantics map to actual implementation.

**TRUSTED_TOOL_PRECONDITIONS:** History checker/prover and event instrumentation preserve ordering semantics.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Optimisation, memory-model, transaction or operation changes trigger proof/history-test replay.

**KNOWN_FAILURE_MODES:**
- Linearizability is claimed without real-time event capture or for only a subset of operations.
- Serializability omits application invariants or external side effects.
- A proof uses sequential consistency while hardware is weak-memory.
- Linearisation points change under optimisation and proof/model drifts.
- Strong safety holds but system starves or is unavailable.
- A weaker consistency model is marketed with linearizable language.

**IMPORTANT_CRITICISMS:**
- Linearizability is a safety property, not progress, availability, durability or total application correctness [S090].
- Serializability can admit behaviours users consider anomalous and excludes external effects [S091].
- History-based proofs depend on precise event and memory semantics [S106].
- The strongest property is not always the best engineering trade-off.

**HOW_THE_PROPERTY_EVOLVED:** Classical serializability/linearizability led to contextual refinement, mechanised concurrent-object proofs, weak-memory variants, relaxed consistency models and automated history checking. Mature practice selects and names the weakest property sufficient for the consumer, with separate liveness and durability evidence.

**MATURE_OR_EVOLVED_FORM:** A concurrency-consistency claim names its history model, observer, operations, real-time/memory semantics and non-covered properties. Proof or checking is bound to implementation events; progress, persistence and business invariants are not inferred from safety equivalence.

**EXPECTED_ENGINEERING_PAYOFF:** Replaces ambiguous consistency labels with discriminating acceptance criteria, finds concurrency anomalies and supports safe implementation substitutions.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can history/refinement proofs scale under weak memory and highly optimised implementations?
- Which relaxed consistency properties best align with user-visible correctness?
- How should external side effects and irreversible actions be incorporated into serialisability models?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S090, S091  
**CRITICAL_SOURCES:** S092, S106, S090, S091  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S030, S031, S052  
**CONTRARY_EVIDENCE:** S092, S106

**SOURCE IDENTITIES USED:**
- S090: Maurice P. Herlihy and Jeannette M. Wing, *Linearizability: A Correctness Condition for Concurrent Objects* (1990)
- S091: Christos H. Papadimitriou, *The Serializability of Concurrent Database Updates* (1979)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S106: Roger C. Su and Robert J. Colvin, *Weak Memory Model Formalisms: Introduction and Survey* (2026, Concurrency and Computation: Practice and Experience 38(2))
- S030: Chris Hawblitzel et al., *IronFleet: Proving Practical Distributed Systems Correct* (2015)
- S031: James R. Wilcox et al., *Verdi: A Framework for Implementing and Formally Verifying Distributed Systems* (2015)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P031 — Runtime monitor scope

**CURRENT_STATUS:** `RUNTIME_VERIFICATION_PROPERTY`  
**LINEAGE_CLASS:** `RUNTIME_VERIFICATION_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `runtime verification`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** runtime verification lineage

**ORIGINAL_FORM:** Runtime verification emerged as trace monitoring against formal properties, often using automata, rewriting or temporal logic. Distributed RV extended the model to decentralised traces and imperfect event order [S066–S068].

**PROBLEM_IT_ADDRESSED:** Some properties cannot be proved statically because code is opaque, environment uncertain or deployment configuration dynamic. Yet observing a finite execution cannot establish unobserved behaviour or arbitrary future liveness.

**ENGINEERING_CLAIM:** Runtime verification checks observed traces against formal properties but must state observability, latency and enforcement limits.

**MECHANISM:** Compile a monitorable property into an online/offline monitor; define event instrumentation, observation granularity, verdict semantics (true/false/inconclusive), clock/order handling and response. Validate monitor against synthetic traces and measure coverage/overhead.

**TRIGGER_OR_CONTEXT:** Trigger for dynamic, partially opaque or environment-dependent properties that are observable at runtime and materially actionable.

**NON_TRIGGER_OR_CHEAP_PATH:** Use a simple assertion/log query when the property is local and immediate; use static proof when violation cannot safely be allowed even once.

**DEPENDENCIES_OR_PRECONDITIONS:** Monitorable formal property, authoritative event schema, instrumentation, verdict/response design and overhead budget.

**SPECIFICATION_PRECONDITIONS:** Property semantics over finite traces and inconclusive cases are explicit.

**ABSTRACTION_PRECONDITIONS:** Event projection preserves violations relevant to the claim.

**ENVIRONMENT_PRECONDITIONS:** Observation loss, clock uncertainty, privacy and distributed order are modelled.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Instrumentation is bound to the actual execution points and cannot silently miss alternate paths.

**TRUSTED_TOOL_PRECONDITIONS:** Monitor synthesis/runtime, event transport, clock/order reconstruction and storage are bounded.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Property, event schema, instrumentation and deployment version changes require monitor regeneration/validation.

**KNOWN_FAILURE_MODES:**
- Relevant events are not instrumented or are dropped/reordered.
- A finite green prefix is interpreted as global safety or future liveness.
- The property is not monitorable under available observations.
- Clock skew and distributed order yield incorrect verdicts.
- Instrumentation changes system timing or behaviour.
- Monitor itself fails, lags or is bypassed.
- A detected violation has no containment/recovery action.

**IMPORTANT_CRITICISMS:**
- Runtime verification observes only executed and instrumented behaviour.
- Liveness and hyperproperties may be inconclusive or unmonitorable from finite single traces [S021, S099].
- Instrumentation overhead and trace infrastructure can be material [S104].
- A formal monitor does not make its event source authoritative.

**HOW_THE_PROPERTY_EVOLVED:** Assertions and offline trace checks evolved into synthesised temporal monitors, decentralised/distributed monitoring, quantitative/timed monitoring, partial-observation epistemic semantics and runtime enforcement. The mature form distinguishes detection, diagnosis and containment.

**MATURE_OR_EVOLVED_FORM:** Use runtime verification for observable violations and dynamic assumptions. Publish monitorability, event coverage, verdict meaning, overhead and response. Green means no observed violation under current instrumentation—not proof of all executions.

**EXPECTED_ENGINEERING_PAYOFF:** Adds live assurance where static models cannot cover deployment, catches configuration/environment drift and provides auditable violation traces.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can monitor uncertainty and inconclusive verdicts be presented in operational decisions?
- What decentralised monitoring designs best balance order accuracy, privacy and overhead?
- When does runtime enforcement reduce risk versus create a new failure mode?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S066, S067, S068, S099  
**CRITICAL_SOURCES:** S099, S104, S021  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S066, S068, S052  
**CONTRARY_EVIDENCE:** S099, S104

**SOURCE IDENTITIES USED:**
- S066: Martin Leucker and Christian Schallhart, *A Brief Account of Runtime Verification* (2009)
- S067: Klaus Havelund and Grigore Roşu, *Monitoring Programs Using Rewriting* (2001)
- S068: Adrian Francalanza, Jorge A. Pérez, and César Sánchez, *Runtime Verification for Decentralised and Distributed Systems* (2018)
- S099: Benedikt Bollig, *Runtime Verification: Monitoring, Knowledge, and Uncertainty* (2026, v1)
- S104: Kevin Guan and Owolabi Legunsen, *An In-Depth Study of Runtime Verification Overheads during Software Testing* (2024)
- S021: Michael R. Clarkson and Fred B. Schneider, *Hyperproperties* (2008/2010)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P032 — Monitor currentness and fail-open/fail-closed design

**CURRENT_STATUS:** `RUNTIME_VERIFICATION_PROPERTY`  
**LINEAGE_CLASS:** `RUNTIME_VERIFICATION_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `runtime verification`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** runtime verification lineage

**ORIGINAL_FORM:** Runtime assertions traditionally failed immediately or logged violations. As monitors moved into production and distributed systems, their configuration, update path, failure semantics and fail-open/fail-closed behaviour became assurance properties in their own right [S066, S068].

**PROBLEM_IT_ADDRESSED:** A correct monitor can still be stale, disabled, partitioned, overloaded or configured against an old schema. Its response can either permit unsafe behaviour (fail open) or create outages/denial of service (fail closed).

**ENGINEERING_CLAIM:** A monitor is assurance only if tied to current property/source/configuration and failure mode policy.

**MECHANISM:** Version property, monitor code, event schema and target configuration together; heartbeat and self-monitor the monitor; define fail-open/fail-closed/degraded response by hazard; test monitor failure, backlog and schema drift; retain violation provenance and rollback/update controls.

**TRIGGER_OR_CONTEXT:** Trigger when runtime-monitor output controls traffic, shutdown, admission, release or regulatory evidence.

**NON_TRIGGER_OR_CHEAP_PATH:** For advisory low-risk metrics, ordinary alerting with clear non-assurance status may be enough.

**DEPENDENCIES_OR_PRECONDITIONS:** Version registry, monitor health channel, failure/response analysis, event-retention policy and operator ownership.

**SPECIFICATION_PRECONDITIONS:** Detection, enforcement and degraded-mode guarantees are distinct.

**ABSTRACTION_PRECONDITIONS:** Schema transforms and event aggregation preserve violation semantics.

**ENVIRONMENT_PRECONDITIONS:** Partitions, overload, clock skew and log loss are included in monitor-failure analysis.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Target and monitor versions/configurations are automatically matched.

**TRUSTED_TOOL_PRECONDITIONS:** Deployment controller, event pipeline and enforcement actuator join the monitor TCB.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Stale identity or failed heartbeat revokes assurance; monitor regressions replay on every schema/property update.

**KNOWN_FAILURE_MODES:**
- Monitor silently stops receiving events.
- Schema change maps fields incorrectly while verdict remains green.
- Fail-closed action causes cascading outage.
- Fail-open action permits a known unsafe state.
- Monitor version lags target deployment.
- Alert-only detection is mistaken for enforcement.
- Distributed monitors disagree due to partitions or clock/order uncertainty.

**IMPORTANT_CRITICISMS:**
- Monitoring creates another software system and trusted operational dependency.
- Safety and availability pressures can conflict in failure response.
- Overhead/backpressure can alter the monitored system [S104].
- Frequent specification change can make monitors stale faster than proof artefacts.

**HOW_THE_PROPERTY_EVOLVED:** One-shot assertions evolved into managed policy-as-code, monitor synthesis, health checking, distributed verdict protocols, adaptive/degraded enforcement and provenance-rich incident evidence. Mature practice treats monitor lifecycle and failure as part of the formal claim.

**MATURE_OR_EVOLVED_FORM:** A production monitor has identity binding, self-health evidence, tested failure modes, explicit containment policy and automatic downgrade when event coverage or version correspondence is lost. Detection and enforcement claims are separated.

**EXPECTED_ENGINEERING_PAYOFF:** Prevents stale or failed monitors from manufacturing false confidence, makes enforcement trade-offs explicit, and improves incident diagnosis and recovery.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How should fail-open/fail-closed choices be optimised when safety and availability hazards compete?
- Can monitor self-assurance avoid infinite regress without an oversized trusted stack?
- What provenance is sufficient to reconstruct distributed verdicts after partial log loss?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S066, S068, S099  
**CRITICAL_SOURCES:** S104  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S068, S052  
**CONTRARY_EVIDENCE:** S104

**SOURCE IDENTITIES USED:**
- S066: Martin Leucker and Christian Schallhart, *A Brief Account of Runtime Verification* (2009)
- S068: Adrian Francalanza, Jorge A. Pérez, and César Sánchez, *Runtime Verification for Decentralised and Distributed Systems* (2018)
- S099: Benedikt Bollig, *Runtime Verification: Monitoring, Knowledge, and Uncertainty* (2026, v1)
- S104: Kevin Guan and Owolabi Legunsen, *An In-Depth Study of Runtime Verification Overheads during Software Testing* (2024)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P033 — Verified compiler/toolchain scope

**CURRENT_STATUS:** `VERIFIED_TOOLCHAIN_PROPERTY`  
**LINEAGE_CLASS:** `VERIFIED_TOOLCHAIN_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `verified toolchain`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** verified toolchain lineage

**ORIGINAL_FORM:** Compiler correctness became a formal semantic-preservation theorem in CompCert; CakeML, verified kernels and certified systems extended the verified chain to language implementation, OS kernels and selected build stages [S024, S025, S080].

**PROBLEM_IT_ADDRESSED:** Source-level correctness can be destroyed by compiler miscompilation, extraction, linker, assembler, runtime or hardware behaviour. Conversely, verifying the compiler does not prove the source program or its requirement.

**ENGINEERING_CLAIM:** Verified compilers/toolchains provide semantic-preservation evidence for a specified language/toolchain, not total system correctness.

**MECHANISM:** Prove semantic preservation for defined source/target languages and passes; identify undefined behaviour and accepted subsets; validate or verify remaining compiler/linker/assembler stages; bind exact source/options/target to binary; test and analyse the TCB.

**TRIGGER_OR_CONTEXT:** Trigger when source-level formal evidence controls a binary-level claim in critical code or compiler-introduced defects are material.

**NON_TRIGGER_OR_CHEAP_PATH:** For low-risk software, compiler diversity, translation validation of critical builds or extensive testing may be cheaper than adopting a verified compiler.

**DEPENDENCIES_OR_PRECONDITIONS:** Supported source subset, target semantics, build options, residual stage inventory and source-to-binary provenance.

**SPECIFICATION_PRECONDITIONS:** The source program’s property is separately established and compatible with compiler preservation theorem.

**ABSTRACTION_PRECONDITIONS:** Source/target semantics model relevant observations, including undefined behaviour and property-specific effects.

**ENVIRONMENT_PRECONDITIONS:** Runtime ABI, hardware and system libraries satisfy target semantics.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Exact source/options/compiler output are bound to deployed binary; no unverified postprocessing.

**TRUSTED_TOOL_PRECONDITIONS:** Parser, extraction, assembler/linker, external algorithms, proof assistant and build system are declared.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Compiler, options, source, target, linker/runtime or hardware changes require rebuild and proof/provenance revalidation.

**KNOWN_FAILURE_MODES:**
- Source program invokes undefined/unspecified behaviour outside theorem scope.
- Parser, assembler, linker or runtime is unverified.
- Optimisation preserves functional behaviour but not timing/constant-time/security properties.
- Deployment uses unsupported language feature, target or compiler option.
- Verified compiler version differs from build version.
- Hardware semantics diverge from the target model.
- Marketing infers whole-system verification from compiler verification.

**IMPORTANT_CRITICISMS:**
- CompCert TCB analysis documents modelling, external-algorithm and toolchain loopholes [S094].
- Semantic preservation is property-relative; ordinary compiler correctness may not preserve side-channel or real-time properties.
- Verified compilation cannot repair an incorrect source specification/program.
- Binary provenance and configuration remain separate evidence.

**HOW_THE_PROPERTY_EVOLVED:** Whole-compiler proof evolved alongside translation validation, verified extraction, secure compilation, binary verification, reproducible/attested builds and property-preserving compiler variants. Mature practice composes only the guarantees actually preserved.

**MATURE_OR_EVOLVED_FORM:** A verified-toolchain claim names source language subset, defined behaviours, preserved observation/property, passes and unverified stages; the deployed binary is tied to exact source/options/tool identity. Source correctness and environment assurance remain separate.

**EXPECTED_ENGINEERING_PAYOFF:** Removes compiler-introduced wrong-code risk for covered programs, strengthens source-level proof, and concentrates testing/review on residual build/runtime/hardware boundaries.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can property-specific preservation (constant time, timing, concurrency) be composed economically with general compiler correctness?
- What end-to-end provenance mechanisms best bind proof to deployed binary?
- How should verified toolchains handle evolving language standards and undefined behaviour?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S024, S080, S025  
**CRITICAL_SOURCES:** S094  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S024, S080, S093, S051, S052  
**CONTRARY_EVIDENCE:** S094

**SOURCE IDENTITIES USED:**
- S024: Xavier Leroy, *Formal Verification of a Realistic Compiler* (2009)
- S080: Ramana Kumar, Magnus O. Myreen, Michael Norrish, and Scott Owens, *CakeML: A Verified Implementation of ML* (2014)
- S025: Gerwin Klein et al., *seL4: Formal Verification of an OS Kernel* (2009)
- S094: David Monniaux and Sylvain Boulmé, *The Trusted Computing Base of the CompCert Verified Compiler* (2022)
- S093: seL4 Project, *What the Proofs Assume* (current site, accessed 2026-08-12)
- S051: Federal Aviation Administration, *AC 20-115D: Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178* (2017)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P034 — Translation validation per-run evidence

**CURRENT_STATUS:** `VERIFIED_TOOLCHAIN_PROPERTY`  
**LINEAGE_CLASS:** `VERIFIED_TOOLCHAIN_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `verified toolchain`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** verified toolchain lineage

**ORIGINAL_FORM:** Translation validation proposed checking each compiler run rather than proving the compiler once. The idea now covers optimisation validation, binary equivalence and per-run proof generation for verifier front-end translations [S023, S098].

**PROBLEM_IT_ADDRESSED:** A complex or rapidly evolving translator may be too costly to verify globally, yet one wrong translation can invalidate a proof, compiler result or generated model. Global testing cannot guarantee the particular accepted run.

**ENGINEERING_CLAIM:** Per-run validation is valuable when compiler verification is unavailable or optimization/configuration is variable.

**MECHANISM:** For each translation, generate a relation or certificate showing source and target semantic correspondence; check it independently; bind source/target/options/version; reject or fall back if validation fails. Select the observation/property preserved rather than assuming full equivalence.

**TRIGGER_OR_CONTEXT:** Trigger for consequential generated code/models/verification conditions where producer verification is unavailable or stale.

**NON_TRIGGER_OR_CHEAP_PATH:** For simple deterministic generators, exhaustive/differential tests or direct proof may be cheaper.

**DEPENDENCIES_OR_PRECONDITIONS:** Formal source/target semantics, preserved observation, per-run identities and validator/certificate path.

**SPECIFICATION_PRECONDITIONS:** The source statement/program is separately validated.

**ABSTRACTION_PRECONDITIONS:** Validation relation preserves all properties claimed downstream.

**ENVIRONMENT_PRECONDITIONS:** Runtime/platform assumptions are compatible across source/target semantics.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Every downstream transformation after validation is covered or trusted.

**TRUSTED_TOOL_PRECONDITIONS:** Validator/checker, semantic models and parser are bounded; ideally proof certificate is independently checked.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Validation is per run; cached results cannot cross changed source, target, options or tool versions.

**KNOWN_FAILURE_MODES:**
- Validator checks only a weakened equivalence or selected outputs.
- Source/target semantics omit undefined, exceptional or timing behaviour.
- Validator shares code/bugs with translator.
- Unsupported translation patterns silently bypass validation.
- Validation passes but source program/specification is wrong.
- Validated intermediate result is changed by later unvalidated stages.

**IMPORTANT_CRITICISMS:**
- Per-run validation may be incomplete or expensive for optimised transformations.
- A validator becomes another trusted tool unless it emits a checkable certificate.
- Equivalence under one semantics does not establish deployment environment or provenance.
- Validation can encourage neglect of systematic translator defects if only outputs are checked.

**HOW_THE_PROPERTY_EVOLVED:** Compiler translation validation evolved into proof-producing validation, verified validators, continuous translation validation and certifying verifier front ends. Mature use records coverage and composes validators across the actual pipeline.

**MATURE_OR_EVOLVED_FORM:** Use per-run validation where whole-translator proof is uneconomic. The accepted artefact includes source/target hashes, options, preserved observation, validation result and independent certificate/checker; bypasses and downstream stages are explicit.

**EXPECTED_ENGINEERING_PAYOFF:** Provides strong evidence for the exact generated artefact, supports rapidly changing optimisers/verifiers, and localises trust without requiring full producer verification.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can validators cover aggressive transformations and property-specific semantics with acceptable cost?
- What independence criteria prevent translator/validator common-mode errors?
- How should chains of partial validators compose into end-to-end evidence?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S023, S098  
**CRITICAL_SOURCES:** S094, S098  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S023, S098, S051, S052  
**CONTRARY_EVIDENCE:** S094, S098

**SOURCE IDENTITIES USED:**
- S023: Amir Pnueli, Michael Siegel, and Eli Singerman, *Translation Validation* (1998)
- S098: Gaurav Parthasarathy, Thibault Dardinier, Benjamin Bonneau, Peter Müller, and Alexander J. Summers, *Towards Trustworthy Automated Program Verifiers: Formally Validating Translations into an Intermediate Verification Language* (2024)
- S094: David Monniaux and Sylvain Boulmé, *The Trusted Computing Base of the CompCert Verified Compiler* (2022)
- S051: Federal Aviation Administration, *AC 20-115D: Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178* (2017)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P035 — Proof-carrying/certificate evidence

**CURRENT_STATUS:** `VERIFIED_TOOLCHAIN_PROPERTY`  
**LINEAGE_CLASS:** `VERIFIED_TOOLCHAIN_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `verified toolchain`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** verified toolchain lineage

**ORIGINAL_FORM:** Proof-carrying code required a producer to supply a proof of a consumer-defined safety policy; translation validation and proof-producing solvers broadened this into certificates that travel with code, compilation or solver results [S022, S023, S108, S109].

**PROBLEM_IT_ADDRESSED:** Consumers cannot feasibly trust every producer, compiler, solver or remote service. They need compact evidence that an exact artefact satisfies a local policy, checked without rerunning expensive search.

**ENGINEERING_CLAIM:** Certificates should be small, consumer-checkable and bound to exact artefact/policy.

**MECHANISM:** Define consumer policy; bind certificate to artefact hash and assumptions; use a small checker; reject malformed/stale certificates; include provenance and version; regenerate after change. Separate certificate validity from policy adequacy and environment assumptions.

**TRIGGER_OR_CONTEXT:** Trigger when artefacts cross trust boundaries or expensive verification must be consumed repeatedly by independent parties.

**NON_TRIGGER_OR_CHEAP_PATH:** For one local build under one trusted team, direct replay may be simpler than packaging a portable certificate.

**DEPENDENCIES_OR_PRECONDITIONS:** Consumer policy, certificate format/checker, artefact identity/provenance and revocation/currentness rules.

**SPECIFICATION_PRECONDITIONS:** Policy is validated against consumer failure modes and not merely easy to prove.

**ABSTRACTION_PRECONDITIONS:** Certificate semantics cover relevant transformation/abstraction steps.

**ENVIRONMENT_PRECONDITIONS:** Runtime assumptions remain separately discharged or encoded in policy where possible.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Certificate cryptographically/semantically binds exact code/binary/configuration.

**TRUSTED_TOOL_PRECONDITIONS:** Checker, parser, policy semantics, cryptographic hash and logic kernel are bounded.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Any artefact, policy, assumption or checker change invalidates/requires regeneration.

**KNOWN_FAILURE_MODES:**
- Certificate proves a weak policy unrelated to consumer risk.
- Artefact/certificate binding is missing or hash covers the wrong representation.
- Checker or proof format omits a soundness-critical rule.
- Certificate is replayed under different axioms/semantics.
- Size/checking overhead defeats distribution benefits.
- Revoked or stale certificates remain accepted after code/configuration change.

**IMPORTANT_CRITICISMS:**
- Proof-carrying evidence shifts specification responsibility to the consumer; a bad policy is still bad.
- Small checkers and formats remain trusted.
- Certificates do not prove provenance of external inputs or runtime environment.
- Practical certificate coverage for SMT/theory preprocessing remains incomplete [S108, S109].

**HOW_THE_PROPERTY_EVOLVED:** PCC evolved into typed assembly, certified compilation, proof witnesses for SAT/SMT, proof reconstruction, attestation-linked evidence and per-run verifier certificates. Mature practice combines semantic certificate and identity/provenance controls.

**MATURE_OR_EVOLVED_FORM:** Accept an artefact only when a bounded checker verifies a certificate for the exact consumer policy, artefact identity, assumptions and version. Unsupported certificate gaps and environment obligations are explicit; stale certificates are automatically rejected.

**EXPECTED_ENGINEERING_PAYOFF:** Enables independent, scalable trust decisions across organisational boundaries and avoids trusting expensive proof search or producer implementation.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can certificate ecosystems remain interoperable and stable across tool evolution?
- What policy languages are expressive enough without making checking expensive or opaque?
- How should certificate revocation and dynamic configuration be handled?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S022, S023, S108, S109  
**CRITICAL_SOURCES:** S094, S109, S108  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S022, S098, S052  
**CONTRARY_EVIDENCE:** S094, S109

**SOURCE IDENTITIES USED:**
- S022: George C. Necula, *Proof-Carrying Code* (1997)
- S023: Amir Pnueli, Michael Siegel, and Eli Singerman, *Translation Validation* (1998)
- S108: Hanna Lachnitt, Mathias Fleury, Haniel Barbosa, Jibiana Jakpor, Bruno Andreotti, Andrew Reynolds, Hans-Jörg Schurr, Clark Barrett, and Cesare Tinelli, *Improving the SMT Proof Reconstruction Pipeline in Isabelle/HOL* (2025)
- S109: Joseph E. Reeves, Haniel Barbosa, Andrew Reynolds, and Marijn J. H. Heule, *A General Approach for SMT Proof Skeletons* (2026)
- S094: David Monniaux and Sylvain Boulmé, *The Trusted Computing Base of the CompCert Verified Compiler* (2022)
- S098: Gaurav Parthasarathy, Thibault Dardinier, Benjamin Bonneau, Peter Müller, and Alexander J. Summers, *Towards Trustworthy Automated Program Verifiers: Formally Validating Translations into an Intermediate Verification Language* (2024)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P036 — Hybrid proof + testing/fuzzing/runtime evidence

**CURRENT_STATUS:** `STRONGLY_RETAINED`  
**LINEAGE_CLASS:** `HYBRID`  
**FORMAL_PROPERTY_CLASS:** `strongly retained`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** hybrid formal/empirical evidence lineage

**ORIGINAL_FORM:** Formal-methods case practice and criticism rejected a proof/testing dichotomy. Symbolic execution generated tests; DO-333 case studies integrated theorem proving/model checking/abstract interpretation with lifecycle evidence; verified-system authors continued testing assumptions and unverified boundaries [S034, S052–S054].

**PROBLEM_IT_ADDRESSED:** Proof is exhaustive only over its formal model, while testing observes the real implementation/environment but samples behaviours. Relying on either alone leaves distinct defects: wrong specification/model versus untested rare paths.

**ENGINEERING_CLAIM:** Formal proof should be combined with tests, fuzzing, conformance and runtime evidence where assumptions/environment/integration are empirical.

**MECHANISM:** Build an evidence stack: prove or model-check critical invariants/refinements; test specification assumptions and model-code correspondence; use property/model-based test generation, fuzzing and differential testing; monitor deployment; mutation-test both tests and specifications; focus independent evidence on the TCB.

**TRIGGER_OR_CONTEXT:** Trigger when a consequential claim spans formal model and real implementation/environment, or any major trusted/unverified boundary remains.

**NON_TRIGGER_OR_CHEAP_PATH:** For a simple deterministic transformation exhaustively tested over its finite domain, a proof layer may add little; for a pure theorem, physical testing may be irrelevant.

**DEPENDENCIES_OR_PRECONDITIONS:** Claim-to-evidence map, independent or diverse oracles, model-code test harness, TCB inventory and decision rules.

**SPECIFICATION_PRECONDITIONS:** Tests include requirement/specification challenge, not only conformance to the same formula.

**ABSTRACTION_PRECONDITIONS:** Concrete tests target details omitted by abstraction and spurious counterexamples are classified.

**ENVIRONMENT_PRECONDITIONS:** Fault injection, performance, hardware and operational tests cover unproved assumptions.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Conformance/differential tests directly connect model predictions to implementation traces.

**TRUSTED_TOOL_PRECONDITIONS:** Testing/fuzzing also exercises proof toolchain, compiler and checker where practical.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Proofs and complementary tests rerun together after relevant change; evidence versions are linked.

**KNOWN_FAILURE_MODES:**
- Testing merely repeats examples already encoded in the proof.
- Proof and tests share the same faulty oracle/specification.
- Teams treat any test failure as refuting the theorem rather than locating a boundary defect.
- Hybrid stacks accumulate tools without a clear claim-to-evidence map.
- Testing of unverified glue is inadequate.
- Proof confidence reduces exploratory/adversarial testing effort.

**IMPORTANT_CRITICISMS:**
- “More evidence” can become unbounded ceremony unless each layer addresses a distinct failure mode.
- Independence is difficult when tests are generated from the same model.
- Empirical evidence and formal proof may conflict because they speak about different artefact levels.
- Verification practitioners explicitly report tests/review catching specification errors [S100].

**HOW_THE_PROPERTY_EVOLVED:** Proof-plus-test moved from informal complementarity to model-based testing, symbolic test generation, proof-guided fuzzing, translation validation, runtime verification and targeted testing of assumptions/TCB. Mature practice designs orthogonal evidence rather than stacking redundant tools.

**MATURE_OR_EVOLVED_FORM:** For each material claim, identify what proof establishes and what remains uncertain; assign testing, fuzzing, review or monitoring to those residuals. Independent evidence must have a distinct oracle/model where possible. Remove layers that do not change the decision.

**EXPECTED_ENGINEERING_PAYOFF:** Catches specification, integration, toolchain, environment and runtime defects that formal proof cannot, while proof covers state spaces testing cannot sample.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can independence and marginal information gain of evidence layers be measured?
- Which mutation schemes best test assumptions and model-code correspondence?
- How should conflicting formal and empirical evidence be adjudicated without automatically privileging either?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S034, S052, S054, S093, S100, S053  
**CRITICAL_SOURCES:** S092, S100  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S054, S065, S093, S051, S052  
**CONTRARY_EVIDENCE:** S092, S100

**SOURCE IDENTITIES USED:**
- S034: Cristian Cadar, Daniel Dunbar, and Dawson Engler, *KLEE: Unassisted and Automatic Generation of High-Coverage Tests for Complex Systems Programs* (2008)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)
- S093: seL4 Project, *What the Proofs Assume* (current site, accessed 2026-08-12)
- S100: Eric Mugnier, Yuanyuan Zhou, Ranjit Jhala, and Michael Coblenz, *On the Impact of Formal Verification on Software Development* (2025)
- S053: NASA, *NASA Formal Methods Guidebook for Software and Computer Systems* (1995/1998)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S065: Maurice H. ter Beek, Rod Chapman, Rance Cleaveland, Hubert Garavel, Rong Gu, Ivo ter Horst, Jeroen J. A. Keiren, Thierry Lecomte, Michael Leuschel, Kristin Yvonne Rozier, Augusto Sampaio, Cristina Seceleanu, Martyn Thomas, Tim A. C. Willemse, and Lijun Zhang, *Formal Methods in Industry* (2025)
- S051: Federal Aviation Administration, *AC 20-115D: Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178* (2017)


### P037 — Lightweight proportional formalisation

**CURRENT_STATUS:** `RETAINED_IN_EVOLVED_FORM`  
**LINEAGE_CLASS:** `LIGHTWEIGHT_FORMAL_METHODS_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `retained in evolved form`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** lightweight formal methods lineage

**ORIGINAL_FORM:** Jackson and Wing named “lightweight formal methods”: partial, focused use of formal languages and tools rather than complete specification/proof. Alloy’s small-scope analysis, executable models, contracts and unit proofs exemplify the approach [S015, S016, S107].

**PROBLEM_IT_ADDRESSED:** Full formalisation can cost more than the risk, arrive after design decisions, or create maintenance burdens. The alternative need not be no formal method: a small model or invariant may eliminate the dominant failure class cheaply.

**ENGINEERING_CLAIM:** Use the cheapest formal representation that removes a material failure class and has a live consumer.

**MECHANISM:** Rank failure classes and claims by consequence, recurrence, ambiguity and tractability; choose the least expensive formal artefact that discriminates the failure—truth table, assertion, contract, finite model, focused proof or validated translation. Stop when marginal assurance no longer changes a decision.

**TRIGGER_OR_CONTEXT:** Trigger when a recurring/high-cost failure can be isolated into a small checkable property and full proof is disproportionate.

**NON_TRIGGER_OR_CHEAP_PATH:** Do not formalise low-risk one-off prose merely because a tool is available; ordinary review/test may be sufficient.

**DEPENDENCIES_OR_PRECONDITIONS:** Risk/failure evidence, named consumer, tractable property and explicit escalation/retirement rule.

**SPECIFICATION_PRECONDITIONS:** The focused property still represents the material failure and its scope is disclosed.

**ABSTRACTION_PRECONDITIONS:** Simplification is sound for the selected claim or labelled bounded/bug-finding.

**ENVIRONMENT_PRECONDITIONS:** Do not select a local property when the dominant uncertainty lies in environment/integration.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Use executable checks/conformance where cheap; otherwise label design-only value.

**TRUSTED_TOOL_PRECONDITIONS:** Prefer simple transparent checkers unless deeper automation’s payoff justifies trust cost.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Low-cost artefacts remain live/replayed or are retired; no decorative formal documents.

**KNOWN_FAILURE_MODES:**
- “Lightweight” becomes unprincipled under-specification.
- Small scopes/bounds are overclaimed as complete proof.
- A local formalisation ignores the system boundary where failures occur.
- Teams formalise easy properties rather than high-risk ones.
- Prototype models become stale documentation.
- Tool adoption cost exceeds avoided defects.

**IMPORTANT_CRITICISMS:**
- Lightweight methods still require sound scope and specification discipline; incomplete does not mean unsound.
- Selection can be biased toward tractable rather than important claims.
- Evidence on ROI is heterogeneous and often case-based [S062–S065, S107].
- A cheap check is wasteful if no consumer or recurring failure class exists.

**HOW_THE_PROPERTY_EVOLVED:** The early “lightweight” argument matured into small-scope model finding, gradual verification, selective verified kernels/libraries, unit proofs, executable invariants and pyramid-style portfolios. Criticism shifted focus from formalisation amount to decision value and maintenance cost.

**MATURE_OR_EVOLVED_FORM:** Formalise only the material claim and choose the cheapest sound representation that can remove its failure class. State bounds and non-covered claims; bind artefact to a consumer and lifecycle; escalate to deeper proof only when residual risk justifies it.

**EXPECTED_ENGINEERING_PAYOFF:** Captures much of formal reasoning’s defect-prevention value earlier and at lower cost, increases adoption and avoids proving low-value system detail.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which empirical predictors identify where small formal artefacts yield durable ROI?
- How can organisations prevent “lightweight” from becoming a euphemism for unsound or stale analysis?
- What maintenance-adjusted comparisons are possible across assertions, models, proofs and tests?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S015, S016, S107  
**CRITICAL_SOURCES:** S064, S107, S112, S062, S065, S063  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S062, S065, S052, S053  
**CONTRARY_EVIDENCE:** S064, S107, S112

**SOURCE IDENTITIES USED:**
- S015: Daniel Jackson and Jeannette M. Wing, *Lightweight Formal Methods* (1996)
- S016: Daniel Jackson, *Software Abstractions: Logic, Language, and Analysis* (2006/2012)
- S107: Paschal C. Amusuo, Owen Cochell, Taylor Le Lievre, Parth V. Patil, Aravind Machiry, and James C. Davis, *Do Unit Proofs Work? An Empirical Study of Compositional Bounded Model Checking for Memory Safety Verification* (2025 preprint)
- S064: Mario Gleirscher and Diego Marmsoler, *Formal Methods in Dependable Systems Engineering: A Survey of Professionals from Europe and North America* (2020)
- S112: Michele Chiari, Matteo Camilli, Marcello M. Bersani, Rutger van Beusekom, and Damian A. Tamburri, *Reality Check on Formal Methods in Industry: A Study of Verum Dezyne* (2025, Journal of Software: Evolution and Process 37(12))
- S062: Jim Woodcock, Peter Gorm Larsen, Juan Bicarregui, and John S. Fitzgerald, *Formal Methods: Practice and Experience* (2009)
- S065: Maurice H. ter Beek, Rod Chapman, Rance Cleaveland, Hubert Garavel, Rong Gu, Ivo ter Horst, Jeroen J. A. Keiren, Thierry Lecomte, Michael Leuschel, Kristin Yvonne Rozier, Augusto Sampaio, Cristina Seceleanu, Martyn Thomas, Tim A. C. Willemse, and Lijun Zhang, *Formal Methods in Industry* (2025)
- S063: Hubert Garavel, Maurice H. ter Beek, and Jaco van de Pol, *The 2020 Expert Survey on Formal Methods* (2020)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S053: NASA, *NASA Formal Methods Guidebook for Software and Computer Systems* (1995/1998)


### P038 — Ceremony/proxy rejection

**CURRENT_STATUS:** `CEREMONY_NOT_GENERAL_PROPERTY`  
**LINEAGE_CLASS:** `CONVERGENT_ENGINEERING`  
**FORMAL_PROPERTY_CLASS:** `ceremony not general`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** convergent engineering property

**ORIGINAL_FORM:** Formal-methods criticism from DeMillo, Hall and Bowen/Hinchey challenged proofs as social substitutes, myths and process rituals. Industry evidence later reinforced that notation, proof volume and certification labels are not engineering outcomes [S055, S057, S058, S062–S065].

**PROBLEM_IT_ADDRESSED:** Organisations substitute visible proxies—formal notation pages, proof lines, theorem counts, zero warnings, certified tool brands or “formally verified” labels—for evidence that a material failure class is controlled.

**ENGINEERING_CLAIM:** Notation, proof count, line count, certification paperwork or green tool status are not transferable assurance properties.

**MECHANISM:** For every formal artefact identify claim, failure mode, consumer, assumptions, correspondence and decision changed. Reject metrics that increase without strengthening those links; audit counterfactuals (could the proxy rise while assurance falls?); retire artefacts with no live consumer.

**TRIGGER_OR_CONTEXT:** Trigger when adoption or acceptance is justified primarily by labels, counts, document volume, tool pedigree or certification status.

**NON_TRIGGER_OR_CHEAP_PATH:** Do not attack simple documentation/replay records that directly enable evidence consumption; ceremony stripping is not minimalism for its own sake.

**DEPENDENCIES_OR_PRECONDITIONS:** Named engineering decision, causal failure-mode theory and ability to trace artefact to evidence consumption.

**SPECIFICATION_PRECONDITIONS:** Metrics cannot replace claim validation or strength checks.

**ABSTRACTION_PRECONDITIONS:** Tool/notation identity is not treated as evidence of abstraction adequacy.

**ENVIRONMENT_PRECONDITIONS:** Certification or process completion is not treated as environment conformance.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** “Verified” labels state actual artefact/correspondence level.

**TRUSTED_TOOL_PRECONDITIONS:** Tool pedigree supplements, not replaces, bounded trust evidence.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Stale formal artefacts lose status even if historical counts remain.

**KNOWN_FAILURE_MODES:**
- Proof count rises by splitting trivial lemmas.
- Specification volume grows while requirements remain unvalidated.
- A certification checklist records tool use but not live model/code identity.
- Teams select easy properties to improve coverage metrics.
- A badge hides a narrow theorem or large assumption set.
- Anti-ceremony rhetoric is used to avoid necessary rigor.

**IMPORTANT_CRITICISMS:**
- Some process/formality is necessary for reproducibility, review and certification; stripping ceremony cannot mean stripping evidence.
- Quantitative proxies can aid capacity planning if not treated as assurance outcomes.
- Public communication needs concise labels, creating unavoidable compression risk.
- Evidence of proxy gaming is often qualitative rather than experimentally quantified.

**HOW_THE_PROPERTY_EVOLVED:** Early philosophical and practitioner criticism matured into assurance-case thinking, property/claim profiles, tool qualification boundaries, reproducible proof artefacts and proportional formalisation. The evolved form strips only non-causal ceremony while preserving traceability and replay.

**MATURE_OR_EVOLVED_FORM:** A notation, tool or certification practice is retained only when it produces a checkable claim, witness, correspondence link or current decision. Metrics describe effort/coverage, never substitute for specification strength or real-world assurance.

**EXPECTED_ENGINEERING_PAYOFF:** Prevents waste and assurance theatre, makes narrow formal successes honestly reusable, and directs investment toward mechanisms that change failure probability or decision confidence.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which observable indicators reveal formal-method proxy gaming without creating new proxies?
- How can public “verified” claims communicate scope without unreadable caveats?
- Where does necessary certification traceability end and bureaucratic duplication begin?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S055, S057, S058, S062, S065, S063, S064  
**CRITICAL_SOURCES:** S055, S057, S112  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S063, S064, S065, S112, S051, S052  
**CONTRARY_EVIDENCE:** S055, S057, S112

**SOURCE IDENTITIES USED:**
- S055: Richard A. De Millo, Richard J. Lipton, and Alan J. Perlis, *Social Processes and Proofs of Theorems and Programs* (1979)
- S057: Anthony Hall, *Seven Myths of Formal Methods* (1990)
- S058: Jonathan P. Bowen and Michael G. Hinchey, *Ten Commandments of Formal Methods* (1995)
- S062: Jim Woodcock, Peter Gorm Larsen, Juan Bicarregui, and John S. Fitzgerald, *Formal Methods: Practice and Experience* (2009)
- S065: Maurice H. ter Beek, Rod Chapman, Rance Cleaveland, Hubert Garavel, Rong Gu, Ivo ter Horst, Jeroen J. A. Keiren, Thierry Lecomte, Michael Leuschel, Kristin Yvonne Rozier, Augusto Sampaio, Cristina Seceleanu, Martyn Thomas, Tim A. C. Willemse, and Lijun Zhang, *Formal Methods in Industry* (2025)
- S063: Hubert Garavel, Maurice H. ter Beek, and Jaco van de Pol, *The 2020 Expert Survey on Formal Methods* (2020)
- S064: Mario Gleirscher and Diego Marmsoler, *Formal Methods in Dependable Systems Engineering: A Survey of Professionals from Europe and North America* (2020)
- S112: Michele Chiari, Matteo Camilli, Marcello M. Bersani, Rutger van Beusekom, and Damian A. Tamburri, *Reality Check on Formal Methods in Industry: A Study of Verum Dezyne* (2025, Journal of Software: Evolution and Process 37(12))
- S051: Federal Aviation Administration, *AC 20-115D: Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178* (2017)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P039 — Specification gaming and golden theorem drift

**CURRENT_STATUS:** `USEFUL_BUT_EASILY_GAMED`  
**LINEAGE_CLASS:** `CONVERGENT_ENGINEERING`  
**FORMAL_PROPERTY_CLASS:** `useful but easily gamed`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** convergent engineering property

**ORIGINAL_FORM:** Vacuity analysis exposed formulas that succeed trivially; broader verification practice encountered post-failure weakening of preconditions, excluded states and “golden theorem” changes. Requirements and proof-engineering work made specification history an assurance concern [S059, S060, S081, S100].

**PROBLEM_IT_ADDRESSED:** A team can make verification green by weakening the property, strengthening assumptions, disabling behaviour or changing the expected theorem after observing failure. Some revisions are legitimate corrections; others destroy the original acceptance meaning.

**ENGINEERING_CLAIM:** Changes to the theorem/specification after failures require review as possible legitimate revision or proof gaming.

**MECHANISM:** Version and diff engineering claim, formal statement, assumptions and known examples; require rationale/classification for changes; replay old counterexamples; run vacuity/mutation/strength tests; separate legitimate specification correction from product workaround; preserve decision-owner approval.

**TRIGGER_OR_CONTEXT:** Trigger after proof/model failure, assumption changes, repeated theorem edits or generated specifications based on known expected outcomes.

**NON_TRIGGER_OR_CHEAP_PATH:** For low-risk exploratory models, maintain ordinary version history and rationale rather than a heavy approval board.

**DEPENDENCIES_OR_PRECONDITIONS:** Versioned claim/spec/assumption history, original counterexamples, decision owner and change classification.

**SPECIFICATION_PRECONDITIONS:** Legitimate correction remains possible but cannot silently reduce accepted behaviour/failure coverage.

**ABSTRACTION_PRECONDITIONS:** Changes to abstraction bounds/reductions are treated as claim changes where they alter behaviours.

**ENVIRONMENT_PRECONDITIONS:** Environment assumptions cannot be strengthened without evidence and scope decision.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Specification changes are reconciled with code/test/runtime expectations rather than changed in isolation.

**TRUSTED_TOOL_PRECONDITIONS:** Generated diffs/strength analyses are advisory and replayable.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Old witnesses and regression properties remain executable after legitimate revisions where applicable.

**KNOWN_FAILURE_MODES:**
- Precondition is strengthened to exclude a discovered defect.
- An invariant clause is removed without stakeholder review.
- Initial states are narrowed to the successful deployment path.
- A benchmark theorem is leaked into prompt/context, inflating proof success.
- Tests and formal spec are changed together, erasing the original oracle.
- A genuine requirement error is frozen to avoid any theorem change.

**IMPORTANT_CRITICISMS:**
- Not every changed theorem is gaming; formalisation legitimately discovers requirement errors.
- Rigid “golden theorem” control can preserve a wrong specification.
- Intent classification requires governance and domain judgement beyond proof checking.
- Metrics for theorem strength can themselves be gamed.

**HOW_THE_PROPERTY_EVOLVED:** Vacuity and change control evolved into semantic diffs, proof-obligation histories, mutation challenge, held-out counterexamples, benchmark contamination controls and independent requirement approval. Mature practice preserves learning while preventing outcome-driven weakening.

**MATURE_OR_EVOLVED_FORM:** Every material statement/assumption change is traceable to an engineering rationale, reviewed against original failure modes and old counterexamples, and classified as correction, scope change or weakening. Green status cannot erase prior evidence.

**EXPECTED_ENGINEERING_PAYOFF:** Prevents formal success from being manufactured, preserves trustworthy acceptance criteria and makes legitimate requirement learning auditable.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can semantic theorem diffs be made understandable to non-logician decision owners?
- Which automatic strength relations are useful across changing representations?
- What benchmark governance best detects theorem leakage and contamination in AI-assisted verification?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S059, S060, S081, S102, S100  
**CRITICAL_SOURCES:** S059, S101, S111  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S100, S051, S052  
**CONTRARY_EVIDENCE:** S059, S101, S111

**SOURCE IDENTITIES USED:**
- S059: Ilan Beer et al., *Efficient Detection of Vacuity in ACTL Formulas* (1997)
- S060: Orna Kupferman and Moshe Y. Vardi, *Vacuity Detection in Temporal Model Checking* (2003)
- S081: Pamela Zave and Michael Jackson, *Four Dark Corners of Requirements Engineering* (1997)
- S102: Daneshvar Amrollahi, Jerry Lopez, and Clark Barrett, *Faithful Autoformalization via Roundtrip Verification and Repair* (2026, v1)
- S100: Eric Mugnier, Yuanyuan Zhou, Ranjit Jhala, and Michael Coblenz, *On the Impact of Formal Verification on Software Development* (2025)
- S101: Jiayi Wu, Robert Joseph George, and Anima Anandkumar, *ITPEval: Benchmarking Formal Translation Across Interactive Theorem Provers* (2026, v1)
- S111: Yutong Xin, Qiaochu Chen, Greg Durrett, and Işil Dillig, *VeriSoftBench: Repository-Scale Formal Verification Benchmarks for Lean* (2026 preprint)
- S051: Federal Aviation Administration, *AC 20-115D: Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178* (2017)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P040 — AI-assisted formalisation boundary

**CURRENT_STATUS:** `CONTEXT_DEPENDENT`  
**LINEAGE_CLASS:** `THEOREM_PROVING_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `context dependent`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** theorem proving lineage

**ORIGINAL_FORM:** Machine-learning assistance first targeted premise selection, tactic generation and proof search, then autoformalisation, proof repair and cross-prover translation. LeanDojo and later benchmarks embedded models in proof-assistant feedback loops [S069–S075, S101, S111].

**PROBLEM_IT_ADDRESSED:** LLMs can reduce search and translation labour, but may hallucinate statements, exploit benchmark leakage, generate a valid proof of the wrong theorem, use unsafe shortcuts or fail to transfer from curated mathematics to real verification repositories.

**ENGINEERING_CLAIM:** LLM assistance is useful for search/translation/repair only when the checked statement and translation review are bounded.

**MECHANISM:** Use LLMs as untrusted proposal generators for statements, tactics, invariants, models and repairs. Require native kernel checking, axiom/unsafe-command audit, independent semantic/roundtrip translation validation, held-out contamination-aware evaluation, code/spec correspondence review and human approval of the engineering claim.

**TRIGGER_OR_CONTEXT:** Trigger for assistance with formal statement generation, tactic/proof search, invariant/model generation, explanation or proof repair—not as autonomous acceptance authority.

**NON_TRIGGER_OR_CHEAP_PATH:** For a small deterministic property, direct human encoding/checking may be cheaper and more trustworthy than an AI translation layer.

**DEPENDENCIES_OR_PRECONDITIONS:** Trusted checker, prompt/model/version provenance, statement-fidelity validation, contamination-aware evaluation and qualified human reviewer.

**SPECIFICATION_PRECONDITIONS:** Generated statement is compared semantically with requirement and challenged by independent examples/equivalence methods.

**ABSTRACTION_PRECONDITIONS:** Generated models/invariants disclose omitted behaviours and are not accepted solely because checking succeeds.

**ENVIRONMENT_PRECONDITIONS:** AI does not invent environmental assumptions; all are independently sourced/discharged.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Generated proofs/models bind to exact code/spec versions and correspondence evidence.

**TRUSTED_TOOL_PRECONDITIONS:** LLM is untrusted; kernel, parser, libraries, unsafe commands, retrieval corpus and equivalence checker are bounded.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Store generated artefacts and replay deterministically; model/prompt/library changes require revalidation and semantic diff.

**KNOWN_FAILURE_MODES:**
- Generated statement type-checks but changes quantifiers, conditions or units.
- Proof uses an unintended axiom, inconsistency or trivialisation.
- Benchmark theorem/solution contamination inflates performance.
- Model succeeds on mathlib-like tasks but fails on repository software obligations [S111].
- Auto-repair weakens theorem or adds assumptions.
- Proof search cost is impractical despite pass@k headline.
- Human reviewers overtrust fluent explanation after kernel success.

**IMPORTANT_CRITICISMS:**
- Kernel checking validates only the generated formal statement.
- ITPEval found native type-checking can substantially overstate cross-prover statement fidelity [S101].
- Roundtrip/equivalence repair improves but does not eliminate semantic drift [S102].
- Benchmarks may be unrepresentative, contaminated or structurally leaked.
- LLM assistance adds model/version/prompt provenance and nondeterminism to proof maintenance.

**HOW_THE_PROPERTY_EVOLVED:** Free-text proof generation evolved into retrieval-augmented tactic agents, verifier-in-the-loop search, autoformalisation benchmarks, equivalence/roundtrip validation, repository-derived evaluation and proof repair. The frontier is shifting from “does it compile?” to “is it faithful, uncontaminated, reproducible and useful in a live proof ecosystem?”.

**MATURE_OR_EVOLVED_FORM:** AI proposes; trusted formal tools check derivations; independent methods validate statement fidelity; humans retain authority over engineering meaning and assumptions. Evaluation uses held-out, repository-realistic tasks and reports search budget, unsafe features, equivalence and transfer—not only type-check pass rate.

**EXPECTED_ENGINEERING_PAYOFF:** Can lower formalisation/search/repair labour, broaden access and explain counterexamples while retaining kernel-level derivational assurance—provided translation and benchmark controls prevent false confidence.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- What scalable method establishes semantic equivalence between natural-language engineering requirements and generated formal statements?
- How severe is benchmark contamination across proprietary and public proof corpora?
- Can AI proof repair preserve theorem meaning and proof architecture across long-lived projects?
- What human-review interface best exposes hidden assumptions and near-miss translations?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S069, S070, S071, S101, S075, S111, S072, S073, S074  
**CRITICAL_SOURCES:** S101, S102, S111  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S069, S070, S052  
**CONTRARY_EVIDENCE:** S101, S102, S111

**SOURCE IDENTITIES USED:**
- S069: Ke Weng, Lun Du, Sirui Li, Wangyue Lu, Haozhe Sun, Hengyu Liu, and Tiancheng Zhang, *Autoformalization in the Era of Large Language Models: A Survey* (2025)
- S070: Kaiyu Yang, Gabriel Poesia, Jingxuan He, Wenda Li, Kristin E. Lauter, Swarat Chaudhuri, and Dawn Song, *Formal Reasoning Meets LLMs: Toward AI for Mathematics and Verification* (2026)
- S071: Kaiyu Yang, Aidan M. Swope, Alex Gu, Rahul Chalamala, Peiyang Song, Shixing Yu, Saad Godil, Ryan Prenger, and Anima Anandkumar, *LeanDojo: Theorem Proving with Retrieval-Augmented Language Models* (2023)
- S101: Jiayi Wu, Robert Joseph George, and Anima Anandkumar, *ITPEval: Benchmarking Formal Translation Across Interactive Theorem Provers* (2026, v1)
- S075: Tom Reichel, R. Wesley Henderson, Andrew Touchet, Andrew Gardner, and Talia Ringer, *Proof Repair Infrastructure for Supervised Models: Building a Large Proof Repair Dataset* (2023)
- S111: Yutong Xin, Qiaochu Chen, Greg Durrett, and Işil Dillig, *VeriSoftBench: Repository-Scale Formal Verification Benchmarks for Lean* (2026 preprint)
- S072: Yuhuai Wu, Albert Q. Jiang, Wenda Li, Markus N. Rabe, Charles Staats, Mateja Jamnik, and Christian Szegedy, *Autoformalization with Large Language Models* (2022)
- S073: Zhitao He, Zongwei Lyu, Dazhong Chen, Dadi Guo, and Yi R. Fung, *MATP-BENCH: Can MLLM Be a Good Automated Theorem Prover for Multimodal Problems?* (2025)
- S074: Talia Ringer, RanDair Porter, Nathaniel Yazdani, John Leo, and Dan Grossman, *Proof Repair across Type Equivalences* (2021)
- S102: Daneshvar Amrollahi, Jerry Lopez, and Clark Barrett, *Faithful Autoformalization via Roundtrip Verification and Repair* (2026, v1)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P041 — Certification/formality ceremony boundary

**CURRENT_STATUS:** `USEFUL_BUT_EASILY_BUREAUCRATISED`  
**LINEAGE_CLASS:** `DOMAIN_SPECIFIC`  
**FORMAL_PROPERTY_CLASS:** `useful but easily bureaucratised`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** domain-specific verified practice

**ORIGINAL_FORM:** Formal-method evidence entered regulated assurance through lifecycle standards and supplements such as DO-333, where mathematically based methods can satisfy defined verification objectives if soundness, coverage, assumptions, tool qualification and lifecycle integration are established. Reusable-component guidance likewise conditions credit on configuration and usage domain [S051–S054, S113].

**PROBLEM_IT_ADDRESSED:** A formal proof, model-check report or qualified tool can become certification ceremony: an artefact produced to satisfy an objective but detached from the exact product configuration, operational assumptions, live consumer or engineering consequence. Conversely, dismissing certification as mere paperwork ignores its legitimate role in forcing traceability and independent scrutiny.

**ENGINEERING_CLAIM:** Certification recognition of formal methods is evidence-framework participation, not automatic truth of the engineering claim.

**MECHANISM:** Map each formal artefact to the exact assurance objective, claim, configuration item, usage domain, assumptions, tool-credit basis and decision authority it serves. Require live traceability from requirement to model/proof to implementation evidence; separate compliance status from product-correctness status; record residual obligations that certification does not discharge; re-evaluate credit after change.

**TRIGGER_OR_CONTEXT:** Trigger when formal evidence is used for regulatory, contractual or independent-assurance credit, or when a reusable verified component carries inherited assurance claims.

**NON_TRIGGER_OR_CHEAP_PATH:** For an internal low-risk invariant with no certification consumer, retain ordinary replay, review and change control rather than manufacturing certification-style paperwork.

**DEPENDENCIES_OR_PRECONDITIONS:** Named assurance objective and authority, configuration baseline, usage domain, traceability, method-soundness argument, tool-credit basis and change-control mechanism.

**SPECIFICATION_PRECONDITIONS:** The certified objective and the actual formal claim are identical or explicitly related; compliance wording cannot substitute for a discriminating requirement.

**ABSTRACTION_PRECONDITIONS:** Any abstract model used for credit states coverage, omissions and justification against certification objectives.

**ENVIRONMENT_PRECONDITIONS:** Operational and installation assumptions are included in the certified usage domain and verified at integration.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** The certified model/proof is tied to the exact implementation and configuration, or its credit is limited to design evidence.

**TRUSTED_TOOL_PRECONDITIONS:** Tool qualification/validation applies to the exact role, version, options and error-detection obligations claimed.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Product, requirement, tool, model and environment changes trigger impact analysis and re-establishment or withdrawal of credit.

**KNOWN_FAILURE_MODES:**
- A standard objective is marked complete because a formal-method document exists, without checking the property proved.
- Tool qualification is treated as a blanket truth guarantee outside the qualified configuration or use case.
- A reusable component is integrated outside its declared usage domain.
- Certification freezes a model while field configuration and environment evolve.
- Proof volume, notation or tool pedigree substitutes for correspondence evidence.
- Teams reject useful lightweight checks because they do not resemble certification artefacts.

**IMPORTANT_CRITICISMS:**
- Standards establish process and evidentiary obligations, not independent proof that a product meets its mission.
- Certification credit can be costly and selective, and public comparative outcome evidence is limited.
- A qualified tool can still be misconfigured or used with an incorrect encoding.
- Document traceability can remain nominal if product identity and operational assumptions are not live.
- Continuous delivery and mutable configurations strain one-time certification models.

**HOW_THE_PROPERTY_EVOLVED:** Formal certification evolved from notation- and review-heavy submissions toward explicit method soundness, tool qualification, objective substitution, assumption/usage-domain control and reusable evidence. The modern direction is evidence-based and configuration-aware assurance: artefacts are machine-replayable where possible, tied to exact identities, and downgraded when the certified assumptions or product configuration no longer hold.

**MATURE_OR_EVOLVED_FORM:** Certification is retained as an independent evidence-governance layer, not as a correctness property. A formal artefact earns credit only for a named objective and exact configuration under declared assumptions; its live engineering status is separately established through correspondence, replay, change impact and residual-risk review.

**EXPECTED_ENGINEERING_PAYOFF:** Creates disciplined traceability, independent challenge and reusable evidence in high-assurance domains while preventing compliance completion from being mistaken for proof of the deployed system.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can continuous or incremental certification preserve independence without freezing obsolete formal artefacts?
- Which assurance objectives gain demonstrable outcome value from formal evidence rather than conventional review/testing?
- How should tool qualification evolve for solver-backed, certificate-producing and AI-assisted verification pipelines?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S051, S052, S053, S054, S113  
**CRITICAL_SOURCES:** S063, S064, S112, S113  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S051, S052, S054, S113  
**CONTRARY_EVIDENCE:** S063, S064, S112, S113

**SOURCE IDENTITIES USED:**
- S051: Federal Aviation Administration, *AC 20-115D: Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178* (2017)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S053: NASA, *NASA Formal Methods Guidebook for Software and Computer Systems* (1995/1998)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)
- S113: Federal Aviation Administration, *AC 20-148: Reusable Software Components* (current guidance lineage, accessed 2026-08-12)
- S063: Hubert Garavel, Maurice H. ter Beek, and Jaco van de Pol, *The 2020 Expert Survey on Formal Methods* (2020)
- S064: Mario Gleirscher and Diego Marmsoler, *Formal Methods in Dependable Systems Engineering: A Survey of Professionals from Europe and North America* (2020)
- S112: Michele Chiari, Matteo Camilli, Marcello M. Bersani, Rutger van Beusekom, and Damian A. Tamburri, *Reality Check on Formal Methods in Industry: A Study of Verum Dezyne* (2025, Journal of Software: Evolution and Process 37(12))


### P042 — Cost/payoff trigger discipline

**CURRENT_STATUS:** `RETAINED_IN_EVOLVED_FORM`  
**LINEAGE_CLASS:** `LIGHTWEIGHT_FORMAL_METHODS_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `retained in evolved form`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** lightweight formal methods lineage

**ORIGINAL_FORM:** Early industrial formal-method advocates already argued for method selection and economic judgement rather than universal maximal proof. Hall, Bowen and Hinchey made proportional use explicit; lightweight formal methods, practitioner surveys and recent “unit proof” work translated this into focused obligations with measured effort [S015, S057, S058, S062–S065, S100, S107, S112].

**PROBLEM_IT_ADDRESSED:** Formalisation consumes scarce domain, modelling, proof and maintenance effort. Without a trigger discipline, teams prove what is tractable or prestigious rather than what changes a material decision, or continue deepening proof after a cheaper invariant, finite model or test has already eliminated the relevant failure class.

**ENGINEERING_CLAIM:** Formalisation is warranted when proof/checking cost is lower than expected failure/review/rework cost for the claim.

**MECHANISM:** Before choosing a method, define the failure class, consequence, uncertainty, decision consumer, cheapest discriminating check, tractability, expected reuse and maintenance horizon. Escalate from executable assertion/test to bounded model, static analysis, model checking or theorem proof only while marginal assurance value exceeds modelling/proof/currentness cost. Record stop and retirement criteria.

**TRIGGER_OR_CONTEXT:** Trigger whenever a project considers adding, deepening, maintaining or retiring a formal-method obligation.

**NON_TRIGGER_OR_CHEAP_PATH:** When an existing deterministic test or type/checker already fully discriminates the relevant failure class at lower trust and maintenance cost, use it and document why escalation is unnecessary.

**DEPENDENCIES_OR_PRECONDITIONS:** Named failure class and consumer, consequence estimate, candidate cheap paths, tractability evidence, expertise/tool cost, reuse horizon and maintenance owner.

**SPECIFICATION_PRECONDITIONS:** The benefit estimate is tied to a specific claim rather than generic “correctness”.

**ABSTRACTION_PRECONDITIONS:** Cost savings from abstraction are balanced against lost correspondence and spurious-result handling.

**ENVIRONMENT_PRECONDITIONS:** External uncertainty that cannot be reduced by proof is not counted as if formalisation removed it.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Payoff estimates include the cost of binding the result to implementation and deployment.

**TRUSTED_TOOL_PRECONDITIONS:** Automation, solver/certificate and qualification costs are included rather than externalised.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Recurring replay, repair, library/tool upgrade and retirement costs are part of the decision.

**KNOWN_FAILURE_MODES:**
- Formal effort targets easy functions rather than high-consequence uncertainty.
- Proof cost excludes specification validation, integration, tooling and long-term maintenance.
- Sunk-cost pressure prevents abandoning an unproductive proof architecture.
- A one-off proof has no live release or design consumer.
- A cheap checker is rejected because it lacks formal-method branding.
- ROI claims use defect counts or proof lines without a counterfactual.
- Automation lowers initial proof cost but raises opaque maintenance or trust costs.

**IMPORTANT_CRITICISMS:**
- Reliable comparative cost/benefit evidence is limited and confounded by domain, team expertise and project selection.
- Expected-loss calculations can falsely quantify uncertain specification and correspondence benefits.
- High-consequence claims may justify proof despite weak short-term ROI.
- Cheap methods can miss rare behaviours and create under-assurance if escalation criteria are weak.
- Learning and reusable-library benefits are difficult to allocate to one property.

**HOW_THE_PROPERTY_EVOLVED:** The debate moved from “formal methods are too expensive” versus “prove everything” to lightweight, incremental, risk-focused and portfolio approaches. Modern practice combines bounded model finding, contracts, static analyses, proof of critical kernels, translation validation, runtime monitors and selective deep proof, with explicit maintenance and replay costs.

**MATURE_OR_EVOLVED_FORM:** Formalisation is a graduated assurance investment. The selected technique is the least costly one that can soundly discriminate the material failure class at the required scope; escalation, stopping, reuse and retirement are governed by decision value and currentness rather than prestige or proof volume.

**EXPECTED_ENGINEERING_PAYOFF:** Concentrates expert effort on consequential uncertainty, captures high-leverage cheap invariants, prevents both reflexive underuse and maximalist overinvestment, and makes formal assurance sustainable through change.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- What common outcome measures permit credible cross-project comparisons of proof, model checking, static analysis and testing?
- How should long-run maintenance and reusable-library externalities enter assurance ROI?
- Can organisations predict which small formal models will eliminate recurring failure classes before incurring modelling cost?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S015, S057, S058, S042, S062, S065, S100, S107, S112, S063, S064  
**CRITICAL_SOURCES:** S057, S063, S064, S112  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S029, S062, S063, S064, S107, S112, S052, S053, S054  
**CONTRARY_EVIDENCE:** S057, S063, S064, S112

**SOURCE IDENTITIES USED:**
- S015: Daniel Jackson and Jeannette M. Wing, *Lightweight Formal Methods* (1996)
- S057: Anthony Hall, *Seven Myths of Formal Methods* (1990)
- S058: Jonathan P. Bowen and Michael G. Hinchey, *Ten Commandments of Formal Methods* (1995)
- S042: M. J. C. Gordon and T. F. Melham, eds., *Introduction to HOL: A Theorem Proving Environment for Higher Order Logic* (1993)
- S062: Jim Woodcock, Peter Gorm Larsen, Juan Bicarregui, and John S. Fitzgerald, *Formal Methods: Practice and Experience* (2009)
- S065: Maurice H. ter Beek, Rod Chapman, Rance Cleaveland, Hubert Garavel, Rong Gu, Ivo ter Horst, Jeroen J. A. Keiren, Thierry Lecomte, Michael Leuschel, Kristin Yvonne Rozier, Augusto Sampaio, Cristina Seceleanu, Martyn Thomas, Tim A. C. Willemse, and Lijun Zhang, *Formal Methods in Industry* (2025)
- S100: Eric Mugnier, Yuanyuan Zhou, Ranjit Jhala, and Michael Coblenz, *On the Impact of Formal Verification on Software Development* (2025)
- S107: Paschal C. Amusuo, Owen Cochell, Taylor Le Lievre, Parth V. Patil, Aravind Machiry, and James C. Davis, *Do Unit Proofs Work? An Empirical Study of Compositional Bounded Model Checking for Memory Safety Verification* (2025 preprint)
- S112: Michele Chiari, Matteo Camilli, Marcello M. Bersani, Rutger van Beusekom, and Damian A. Tamburri, *Reality Check on Formal Methods in Industry: A Study of Verum Dezyne* (2025, Journal of Software: Evolution and Process 37(12))
- S063: Hubert Garavel, Maurice H. ter Beek, and Jaco van de Pol, *The 2020 Expert Survey on Formal Methods* (2020)
- S064: Mario Gleirscher and Diego Marmsoler, *Formal Methods in Dependable Systems Engineering: A Survey of Professionals from Europe and North America* (2020)
- S029: Chris Newcombe et al., *How Amazon Web Services Uses Formal Methods* (2015)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S053: NASA, *NASA Formal Methods Guidebook for Software and Computer Systems* (1995/1998)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P043 — Prove everything

**CURRENT_STATUS:** `REJECTED_OR_DISFAVOURED`  
**LINEAGE_CLASS:** `CONVERGENT_ENGINEERING`  
**FORMAL_PROPERTY_CLASS:** `rejected or disfavoured`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** convergent engineering property

**ORIGINAL_FORM:** Some early rhetoric and later caricature treated complete formal specification and proof of an entire software system as the natural endpoint of rigor. Criticism by DeMillo, Lipton and Perlis, Hall’s myth corrections, Bowen and Hinchey’s practice principles, and the lightweight-formal-methods movement rejected universal whole-system proof as an engineering prescription [S015, S055, S057, S058].

**PROBLEM_IT_ADDRESSED:** The practice is a rejected overgeneralisation: attempting to prove every behaviour and component can consume disproportionate effort, force false environmental closure, delay feedback, create vast stale proof estates and distract from the few claims that control material risk.

**ENGINEERING_CLAIM:** Full-system proof is not generally retained as a universal requirement; selective critical-property proof is mature.

**MECHANISM:** Do not adopt “prove everything” as a property. Replace it with claim decomposition, critical-kernel selection, method-fit analysis, explicit nonformal boundaries, hybrid evidence and escalation by consequence and tractability. Whole-system proof remains a context-specific option where scope and payoff justify it.

**TRIGGER_OR_CONTEXT:** This rejected practice should be challenged whenever breadth, proof percentage or “fully verified” status is proposed without a claim- and boundary-specific payoff argument.

**NON_TRIGGER_OR_CHEAP_PATH:** A whole-system proof may be justified for a small stable high-consequence system with a bounded environment; it is evaluated as a context-specific investment rather than a universal maturity requirement.

**DEPENDENCIES_OR_PRECONDITIONS:** For any broad proof proposal: stable specification, tractable semantics, explicit environment, correspondence plan, maintenance capacity and demonstrable decision value.

**SPECIFICATION_PRECONDITIONS:** Completeness is always relative to an enumerated property set; “all correctness” is inadmissible.

**ABSTRACTION_PRECONDITIONS:** Any claimed breadth discloses abstracted and excluded behaviour.

**ENVIRONMENT_PRECONDITIONS:** Physical/human/operational uncertainty remains outside unless explicitly modelled and validated.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Breadth claims require end-to-end identity/correspondence, not only source proof coverage.

**TRUSTED_TOOL_PRECONDITIONS:** A larger proof estate often enlarges libraries, generators and maintenance dependencies even with a small kernel.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Broad claims require sustainable full replay and change-impact mechanisms; otherwise breadth accelerates staleness.

**KNOWN_FAILURE_MODES:**
- Specification effort grows without a stable stakeholder claim.
- Proof excludes physical, human or integration uncertainty while marketing claims whole-system correctness.
- Low-risk glue receives more proof effort than high-risk environment interfaces.
- Rapidly changing code makes the proof estate continuously stale.
- The programme postpones tests and field feedback until formal completion.
- A maximal proof architecture becomes organisationally irreversible.

**IMPORTANT_CRITICISMS:**
- The phrase conflates mathematical completeness in a model with complete assurance of a deployed system.
- Empirical evidence does not support universal economic superiority.
- Selective verified systems demonstrate strong value without establishing that their scope should be universal.
- Some domains may rationally require unusually broad proof, so rejection is of the universal rule, not of deep verification itself.

**HOW_THE_PROPERTY_EVOLVED:** Whole-program verification survived in bounded, high-value domains—compilers, kernels, cryptographic routines, protocols—while engineering practice broadened into lightweight models, modular proofs, static analyses, certificates, translation validation, testing and runtime monitoring. The evolved principle is selective completeness relative to a named claim and boundary.

**MATURE_OR_EVOLVED_FORM:** NO_GENERAL_PROPERTY: never require proof breadth as an end in itself. Establish the minimum sufficient formal perimeter around the critical claim, make residual boundaries explicit, and widen only when additional proof changes the decision more than a cheaper evidence source would.

**EXPECTED_ENGINEERING_PAYOFF:** Avoids maximalist waste and false closure while preserving the option of deep proof for critical kernels and stable, tractable interfaces.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Which system structures and change rates make broad end-to-end proof economically sustainable?
- How can selective verification demonstrate that omitted components do not dominate residual risk?
- When does compositional proof genuinely approximate whole-system assurance rather than conceal interface assumptions?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S015, S055, S057, S058, S056  
**CRITICAL_SOURCES:** S055, S095, S112  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S024, S025, S029, S030, S112, S052, S053  
**CONTRARY_EVIDENCE:** S055, S095, S112

**SOURCE IDENTITIES USED:**
- S015: Daniel Jackson and Jeannette M. Wing, *Lightweight Formal Methods* (1996)
- S055: Richard A. De Millo, Richard J. Lipton, and Alan J. Perlis, *Social Processes and Proofs of Theorems and Programs* (1979)
- S057: Anthony Hall, *Seven Myths of Formal Methods* (1990)
- S058: Jonathan P. Bowen and Michael G. Hinchey, *Ten Commandments of Formal Methods* (1995)
- S056: James H. Fetzer, *Program Verification: The Very Idea* (1988)
- S095: Xiaokun Luan, David Sanán, Zhe Hou, Qiyuan Xu, Chengwei Liu, Yufan Cai, Yang Liu, and Meng Sun, *Why the Proof Fails in Different Versions of Theorem Provers: An Empirical Study of Compatibility Issues in Isabelle* (2025)
- S112: Michele Chiari, Matteo Camilli, Marcello M. Bersani, Rutger van Beusekom, and Damian A. Tamburri, *Reality Check on Formal Methods in Industry: A Study of Verum Dezyne* (2025, Journal of Software: Evolution and Process 37(12))
- S024: Xavier Leroy, *Formal Verification of a Realistic Compiler* (2009)
- S025: Gerwin Klein et al., *seL4: Formal Verification of an OS Kernel* (2009)
- S029: Chris Newcombe et al., *How Amazon Web Services Uses Formal Methods* (2015)
- S030: Chris Hawblitzel et al., *IronFleet: Proving Practical Distributed Systems Correct* (2015)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S053: NASA, *NASA Formal Methods Guidebook for Software and Computer Systems* (1995/1998)


### P044 — Proof eliminates testing

**CURRENT_STATUS:** `REJECTED_OR_DISFAVOURED`  
**LINEAGE_CLASS:** `HYBRID`  
**FORMAL_PROPERTY_CLASS:** `rejected or disfavoured`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** hybrid formal/empirical evidence lineage

**ORIGINAL_FORM:** The caricature that proof eliminates testing arose from treating deductive correctness as a complete validation mechanism. Formal-method practice and assurance guidance instead retained testing for specification validation, integration, tool/assumption challenge, hardware/environment behaviour and properties outside the proof [S052–S054, S057, S058].

**PROBLEM_IT_ADDRESSED:** This is a rejected substitution claim. A proof can establish a theorem about a model or program semantics while tests reveal wrong requirements, unmodelled integration, compiler/runtime/hardware behaviour, performance, usability, operational configuration and violated assumptions.

**ENGINEERING_CLAIM:** The false dichotomy is rejected: proofs and testing supply different evidence over formal model versus empirical system.

**MECHANISM:** Do not treat proof as a test waiver except for the exact objective for which sound formal evidence supplies accepted coverage. Construct a hybrid evidence map: proof discharges defined logical obligations; testing/fuzzing validates examples, assumptions, integration, binaries, environment and negative spaces; runtime monitoring covers observable residual conditions.

**TRIGGER_OR_CONTEXT:** Trigger whenever formal proof is proposed as a reason to remove, narrow or waive testing/fuzzing/integration evidence.

**NON_TRIGGER_OR_CHEAP_PATH:** When a proof demonstrably subsumes a deterministic test objective and replay is cheaper, retire that redundant test while preserving tests for distinct assumptions and integration boundaries.

**DEPENDENCIES_OR_PRECONDITIONS:** Coverage map by engineering uncertainty, independent oracles where possible, exact proof scope, test identities and change-impact rules.

**SPECIFICATION_PRECONDITIONS:** Tests challenge the intended requirement and edge cases rather than merely restating the formal theorem.

**ABSTRACTION_PRECONDITIONS:** Tests target behaviours omitted or coarsened by the abstraction and validate counterexample concretisation.

**ENVIRONMENT_PRECONDITIONS:** Physical, network, hardware, human and configuration premises are exercised or monitored where feasible.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Binary/integration/conformance tests or validated translation connect the proved model/source to deployment.

**TRUSTED_TOOL_PRECONDITIONS:** Solvers, checkers, compilers and generators are subject to independent tests/certificates appropriate to their role.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Proof and test suites co-evolve; retiring an objective is reversed when proof scope/currentness is lost.

**KNOWN_FAILURE_MODES:**
- Tests are removed after a narrow functional proof, leaving integration defects undetected.
- Proof and tests share the same wrong oracle/specification.
- Certification credit is misunderstood as eliminating all structural or robustness testing.
- Testing exercises only proved behaviour and never challenges assumptions.
- Duplicate evidence consumes cost without covering a distinct uncertainty.
- A test failure causes the theorem to be weakened instead of diagnosing correspondence.

**IMPORTANT_CRITICISMS:**
- Testing cannot prove absence over an unbounded state space, so hybridisation must not demote strong proofs to “just another test”.
- Some test objectives may legitimately be replaced by formal evidence under standards.
- Poorly designed hybrid stacks duplicate cost without independent failure sensitivity.
- Physical and probabilistic environments may need experiments/statistics rather than conventional software tests.

**HOW_THE_PROPERTY_EVOLVED:** The false dichotomy evolved into proof-guided testing, model-based test generation, property-based testing, fuzzing of compilers/solvers, mutation and vacuity checks, translation validation, runtime verification and independent implementation checks. Evidence sources are selected by which uncertainty they can falsify.

**MATURE_OR_EVOLVED_FORM:** Proof and testing have noninterchangeable scopes. Remove a test only when the formal result soundly subsumes its objective and remaining model, tool, integration and environmental assumptions are covered elsewhere. Prefer independent evidence whose failure modes are not perfectly correlated.

**EXPECTED_ENGINEERING_PAYOFF:** Combines exhaustive or deductive assurance for formal obligations with empirical challenge of translation, integration and environment, reducing both residual defects and redundant assurance work.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How should evidence portfolios measure independence and correlated specification error?
- Which testing obligations can safely be retired after formal evidence in rapidly changing systems?
- What mutation strategies best test whether a proof/specification would detect realistic defects?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S052, S053, S057, S058, S002, S054  
**CRITICAL_SOURCES:** S055, S092, S097, S100  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S024, S025, S028, S030, S052, S051, S054  
**CONTRARY_EVIDENCE:** S055, S092, S097, S100

**SOURCE IDENTITIES USED:**
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S053: NASA, *NASA Formal Methods Guidebook for Software and Computer Systems* (1995/1998)
- S057: Anthony Hall, *Seven Myths of Formal Methods* (1990)
- S058: Jonathan P. Bowen and Michael G. Hinchey, *Ten Commandments of Formal Methods* (1995)
- S002: C. A. R. Hoare, *An Axiomatic Basis for Computer Programming* (1969)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)
- S055: Richard A. De Millo, Richard J. Lipton, and Alan J. Perlis, *Social Processes and Proofs of Theorems and Programs* (1979)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S097: Dominik Winterer, Chengyu Zhang, and Zhendong Su, *On the Unusual Effectiveness of Type-Aware Operator Mutations for Testing SMT Solvers* (2020)
- S100: Eric Mugnier, Yuanyuan Zhou, Ranjit Jhala, and Michael Coblenz, *On the Impact of Formal Verification on Software Development* (2025)
- S024: Xavier Leroy, *Formal Verification of a Realistic Compiler* (2009)
- S025: Gerwin Klein et al., *seL4: Formal Verification of an OS Kernel* (2009)
- S028: Haogang Chen et al., *Using Crash Hoare Logic for Certifying the FSCQ File System* (2015)
- S030: Chris Hawblitzel et al., *IronFleet: Proving Practical Distributed Systems Correct* (2015)
- S051: Federal Aviation Administration, *AC 20-115D: Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178* (2017)


### P045 — Model checking explores every real behaviour

**CURRENT_STATUS:** `REJECTED_OR_DISFAVOURED`  
**LINEAGE_CLASS:** `MODEL_CHECKING_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `rejected or disfavoured`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** model checking lineage

**ORIGINAL_FORM:** Explicit-state and symbolic model checking promised exhaustive exploration of all states and transitions in a finite formal model satisfying the chosen semantics. Popular accounts sometimes collapsed “all states of the model” into “all possible real-world behaviours” [S007–S009, S016, S036].

**PROBLEM_IT_ADDRESSED:** This is a rejected scope inflation. Exhausting a finite or abstract transition system says nothing about behaviours omitted by the model, bounded beyond the search depth, introduced by code generation, weak memory, deployment configuration, hardware or environment.

**ENGINEERING_CLAIM:** Model checking explores behaviours represented by the model/scope; real behaviour correspondence is an added claim.

**MECHANISM:** State the explored universe precisely: initial states, transition relation, bounds, reductions, fairness, data/domain limits and environment. Label results as exhaustive, symbolic, bounded or under-approximating. Validate abstraction and model-code correspondence, concretise counterexamples, and test omitted boundaries.

**TRIGGER_OR_CONTEXT:** Challenge whenever “all behaviours”, “exhaustive” or “no counterexample” is used without an explicit model/bound/environment qualifier.

**NON_TRIGGER_OR_CHEAP_PATH:** For a genuinely finite, directly executable state machine whose inputs and transitions are complete, ordinary exhaustive enumeration may be sufficient without a large model-checking framework.

**DEPENDENCIES_OR_PRECONDITIONS:** Finite/symbolic state semantics, explicit bounds and reductions, property, model-generation provenance and correspondence plan.

**SPECIFICATION_PRECONDITIONS:** The checked property is non-vacuous and covers the intended safety/liveness case.

**ABSTRACTION_PRECONDITIONS:** Over/under-approximation and reduction preservation conditions are established and spurious traces managed.

**ENVIRONMENT_PRECONDITIONS:** All environment/failure actions relevant to the claim are modelled or explicitly excluded.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Implementation is generated from, extracted to, or proven/tested conformant with the checked model.

**TRUSTED_TOOL_PRECONDITIONS:** Checker, encoding, reduction and counterexample generation are versioned; certificates or cross-checks used where consequence warrants.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Model, bounds, fairness and code/config identities are replayed after change; an old exhaustive run is not current evidence.

**KNOWN_FAILURE_MODES:**
- Bounded model checking success is reported as proof.
- A finite data scope excludes overflow or resource exhaustion.
- Partial-order or symmetry reduction violates its preservation conditions.
- Environment actions or failures are absent.
- Model checking exhausts a design model that implementation does not refine.
- A weak-memory execution is missing from a sequentially consistent model.
- A property passes vacuously because triggering behaviour is unreachable.

**IMPORTANT_CRITICISMS:**
- State explosion forces bounds, abstraction and reductions that narrow literal exhaustiveness.
- Spurious counterexamples can dominate over-approximations; under-approximations miss behaviours.
- Current complexity work shows optimal partial-order reduction itself can be hard [S103].
- Verified distributed-system defects show model/code/environment gaps despite strong model-level results [S092].
- No counterexample is not evidence about properties the model never expressed.

**HOW_THE_PROPERTY_EVOLVED:** The original exhaustive-search value was retained but narrowed to an explicit model. Symbolic checking, bounded SAT/SMT methods, CEGAR, partial-order/symmetry reductions, timed/probabilistic checkers and code/model extraction expanded tractability. Mature reporting now couples coverage/bound disclosure with vacuity, abstraction and correspondence evidence.

**MATURE_OR_EVOLVED_FORM:** Claim only that the specified property holds over the identified formal transition system at the disclosed bounds and reduction assumptions. Promote this to an implementation/deployment claim only after separately establishing model construction, refinement/correspondence and environmental adequacy.

**EXPECTED_ENGINEERING_PAYOFF:** Preserves model checking’s exceptional ability to exhaust finite concurrency/state combinations and produce actionable traces without allowing “exhaustive” to become an unbounded marketing claim.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can model coverage be communicated in engineering rather than syntactic terms?
- Which code-to-model extraction methods provide useful independent correspondence rather than shared translation risk?
- How should reductions be certified when their optimal construction is computationally hard?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S007, S008, S009, S061, S016, S036  
**CRITICAL_SOURCES:** S092, S103, S106  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S029, S062, S052, S054  
**CONTRARY_EVIDENCE:** S092, S103, S106

**SOURCE IDENTITIES USED:**
- S007: E. M. Clarke, E. A. Emerson, and J. Sifakis, *Model Checking: Algorithmic Verification and Debugging* (2009; roots in 1981 work)
- S008: J. R. Burch, E. M. Clarke, K. L. McMillan, D. L. Dill, and L. J. Hwang, *Symbolic Model Checking: 10^20 States and Beyond* (1992)
- S009: Gerard J. Holzmann, *The Model Checker SPIN* (1997)
- S061: Edmund Clarke, Orna Grumberg, Somesh Jha, Yuan Lu, and Helmut Veith, *Counterexample-Guided Abstraction Refinement* (2000)
- S016: Daniel Jackson, *Software Abstractions: Logic, Language, and Analysis* (2006/2012)
- S036: Armin Biere, Alessandro Cimatti, Edmund Clarke, and Yunshan Zhu, *Symbolic Model Checking without BDDs* (1999)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S103: Frédéric Herbreteau, Sarah Larroze-Jardiné, and Igor Walukiewicz, *Partial-Order Reduction Is Hard* (2025)
- S106: Roger C. Su and Robert J. Colvin, *Weak Memory Model Formalisms: Introduction and Survey* (2026, Concurrency and Computation: Practice and Experience 38(2))
- S029: Chris Newcombe et al., *How Amazon Web Services Uses Formal Methods* (2015)
- S062: Jim Woodcock, Peter Gorm Larsen, Juan Bicarregui, and John S. Fitzgerald, *Formal Methods: Practice and Experience* (2009)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S054: NASA, *Formal Methods Case Studies for DO-333* (2014)


### P046 — Type safety means functional correctness

**CURRENT_STATUS:** `REJECTED_OR_DISFAVOURED`  
**LINEAGE_CLASS:** `TYPE_SYSTEM_AND_DEPENDENT_TYPE_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `rejected or disfavoured`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** type system and dependent type lineage

**ORIGINAL_FORM:** Type systems were designed to rule out defined classes of ill-formed programs and later grew to express ownership, effects, protocols, refinements and dependent propositions. The slogan “well typed programs do not go wrong” was often overextended into functional correctness [S045–S047, S089].

**PROBLEM_IT_ADDRESSED:** This is a rejected inference: a program can satisfy its language’s type-safety theorem while computing the wrong value, violating a domain invariant, leaking information, deadlocking, exhausting resources or failing an unstated protocol requirement.

**ENGINEERING_CLAIM:** Type safety and related guarantees are precise but narrower than functional correctness.

**MECHANISM:** Publish the exact typing judgement and meta-theorem: progress/preservation, memory safety, absence of a particular error, ownership/race condition, refinement predicate or protocol discipline. Treat untyped/unsafe/FFI/reflection boundaries and logical consistency explicitly; add contracts/proofs/tests for functional and temporal claims not encoded by the type.

**TRIGGER_OR_CONTEXT:** Challenge whenever “type safe”, “Rust safe”, “dependent typed” or “proof by type checking” is used to support a broader functional, temporal or deployment claim.

**NON_TRIGGER_OR_CHEAP_PATH:** Use ordinary type checking as the cheap path when the decision concerns exactly the language-defined type error class; do not add theorem proving for already-subsumed obligations.

**DEPENDENCIES_OR_PRECONDITIONS:** Explicit typing rules/meta-theorem, language/runtime version, unsafe/FFI inventory, specification for any refinement/dependent predicate.

**SPECIFICATION_PRECONDITIONS:** Any semantic property encoded in a type is reviewed like any other formal specification.

**ABSTRACTION_PRECONDITIONS:** Type abstractions preserve the relevant resource/protocol semantics and disclose erased runtime behaviour.

**ENVIRONMENT_PRECONDITIONS:** External components, network, runtime and hardware satisfy the assumptions behind the type guarantee.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** The compiled/executed artefact preserves the checked type discipline and escape hatches are bounded.

**TRUSTED_TOOL_PRECONDITIONS:** Type checker, compiler, macros/generators, logical axioms and unsafe features are in scope.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Language/compiler/library/API changes trigger re-type-checking and review of changed soundness/unsafe boundaries.

**KNOWN_FAILURE_MODES:**
- Nominal or structural typing is marketed as semantic correctness.
- Unsafe code, foreign interfaces or casts escape the theorem.
- A refinement type encodes a weak or mistranslated predicate.
- Termination/consistency assumptions turn a programming language into an unsound logic.
- Session/typestate guarantees omit network failure or global liveness.
- Type inference succeeds while units, ranges or business rules remain wrong.

**IMPORTANT_CRITICISMS:**
- The guarantee is exactly as strong as the type language and soundness theorem, not the word “typed”.
- Dependent types shift specification and proof burden into types; they do not validate the predicate.
- Strong types can increase annotation/evolution cost and may be bypassed at integration boundaries.
- Behavioural subtyping requires semantic obligations beyond nominal subtyping [S089].

**HOW_THE_PROPERTY_EVOLVED:** Simple representation and control-flow checks evolved into parametricity, effect/ownership systems, typestate/session protocols, refinement types and dependent proof-carrying programs. Mature practice presents types as selective proof carriers and composes them with other evidence for unencoded behaviour.

**MATURE_OR_EVOLVED_FORM:** A type-safety claim names the excluded error class, soundness assumptions and escape hatches. Functional correctness is claimed only when the relevant function/property is actually represented in the type and checked under a sound, terminating logic with validated specification.

**EXPECTED_ENGINEERING_PAYOFF:** Retains cheap, compositional prevention of large defect classes while avoiding the false confidence and under-testing caused by calling every type-correct program correct.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can rich type guarantees remain usable and stable under API evolution?
- Which global distributed/temporal properties can be encoded compositionally without hidden assumptions?
- How should reviewers quantify residual risk at unsafe, FFI and generated-code boundaries?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S045, S046, S047, S089  
**CRITICAL_SOURCES:** S045, S046, S089  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S046, S047, S052  
**CONTRARY_EVIDENCE:** S045, S046, S089

**SOURCE IDENTITIES USED:**
- S045: Per Martin-Löf, *Intuitionistic Type Theory* (1984)
- S046: Ralf Jung et al., *RustBelt: Securing the Foundations of the Rust Programming Language* (2018)
- S047: Niki Vazou et al., *Refinement Types for Haskell* (2014)
- S089: Barbara H. Liskov and Jeannette M. Wing, *A Behavioral Notion of Subtyping* (1994)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P047 — Proof assistant cannot be wrong

**CURRENT_STATUS:** `ASSUMPTION_SENSITIVE`  
**LINEAGE_CLASS:** `THEOREM_PROVING_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `assumption sensitive`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** theorem proving lineage

**ORIGINAL_FORM:** The LCF architecture reduced trust by deriving theorems through an abstract kernel datatype; HOL, Isabelle and Coq/Rocq retained small trusted kernels and replayable proof objects or scripts. This engineering success was sometimes caricatured as making proof assistants incapable of error [S042–S044].

**PROBLEM_IT_ADDRESSED:** The caricature hides residual trust in kernel implementation, parser/elaboration, axioms, unsafe commands, code extraction, external solvers/oracles, operating system/hardware and—most importantly—the formal statement. Small trust is not zero trust.

**ENGINEERING_CLAIM:** Proof assistants reduce proof-checking risk but depend on kernels, axioms, libraries, unsafe features and build environment.

**MECHANISM:** Inventory the trusted computing base and theorem dependencies; reject admitted/unsafe constructs unless explicitly authorised; inspect axioms; pin kernel/library/tool versions; prefer proof terms/certificates checked by a small independent verifier; diversify or fuzz critical checkers/solvers; validate the claimed statement and binary/provenance boundary separately.

**TRIGGER_OR_CONTEXT:** Trigger whenever kernel checking, proof-assistant use or a “verified” tool is cited as eliminating the possibility of tool or statement error.

**NON_TRIGGER_OR_CHEAP_PATH:** For low-consequence local proofs, ordinary kernel replay plus axiom/unsafe checks may be sufficient; independent checker diversification is consequence-driven.

**DEPENDENCIES_OR_PRECONDITIONS:** Defined logic and kernel, dependency/axiom audit, tool provenance, external-oracle policy and statement validation.

**SPECIFICATION_PRECONDITIONS:** Kernel acceptance cannot substitute for validating the theorem statement against engineering intent.

**ABSTRACTION_PRECONDITIONS:** The checker proves only the encoded abstract semantics; omitted behaviours remain explicit.

**ENVIRONMENT_PRECONDITIONS:** Hardware/runtime and distribution integrity assumptions are bounded or accepted.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Extraction/compilation/binary correspondence is separately proven, validated or tested.

**TRUSTED_TOOL_PRECONDITIONS:** The trusted base is explicit, minimal where practical, and independently challenged for high-consequence claims.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Proofs replay on the pinned toolchain; kernel/library upgrades trigger revalidation and compatibility review.

**KNOWN_FAILURE_MODES:**
- Kernel or elaborator bug accepts an invalid term.
- A theorem depends transitively on an unreviewed axiom or admitted lemma.
- Unsafe extension or oracle bypasses kernel guarantees.
- Parser/pretty-printer ambiguity changes what reviewers think was proved.
- Code extraction/compiler/binary lies outside the theorem.
- Hardware fault or malicious tool distribution corrupts checking.
- A completely valid proof establishes the wrong property.

**IMPORTANT_CRITICISMS:**
- TCB analyses of CompCert and seL4 document nontrivial external assumptions [S093, S094].
- SMT fuzzing found confirmed soundness bugs, showing mature automated reasoners are fallible [S097].
- A tiny kernel reduces attack/error surface but can concentrate trust and does not validate semantics outside logic.
- Independent checking can share libraries, semantics or generated-certificate bugs.

**HOW_THE_PROPERTY_EVOLVED:** The “trusted prover” model evolved toward de Bruijn-style proof objects, LCF kernels, certificate-producing SAT/SMT solvers, proof reconstruction, fuzzing, TCB manifests, reproducible builds and in some projects binary verification. The mature aim is auditable minimised and diversified trust, not infallibility.

**MATURE_OR_EVOLVED_FORM:** A checked theorem carries a bounded trust statement: exact kernel, logic, axioms, parser/elaborator, external oracle/certificate path, libraries and artefact provenance. Consequential results favour independently checkable certificates or reconstruction and treat proof validity as only one layer of the engineering claim.

**EXPECTED_ENGINEERING_PAYOFF:** Preserves the major assurance gain of small replayable checkers while making residual tool, axiom, translation and physical trust visible and reducible.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- What is the best machine-readable TCB manifest across heterogeneous proof and solver pipelines?
- How much checker diversity yields meaningful independence rather than common-mode semantics?
- Can proof-assistant distributions provide end-to-end reproducible provenance without making maintenance impractical?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S042, S043, S044  
**CRITICAL_SOURCES:** S094, S095, S097, S093  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S024, S025, S093, S094, S096, S051, S052  
**CONTRARY_EVIDENCE:** S094, S095, S097

**SOURCE IDENTITIES USED:**
- S042: M. J. C. Gordon and T. F. Melham, eds., *Introduction to HOL: A Theorem Proving Environment for Higher Order Logic* (1993)
- S043: The Rocq/Coq proof assistant project, *The Rocq Prover / Coq proof assistant documentation* (current accessed 2026-08-12)
- S044: Tobias Nipkow, Lawrence C. Paulson, and Markus Wenzel, *Isabelle/HOL: A Proof Assistant for Higher-Order Logic* (2002)
- S094: David Monniaux and Sylvain Boulmé, *The Trusted Computing Base of the CompCert Verified Compiler* (2022)
- S095: Xiaokun Luan, David Sanán, Zhe Hou, Qiyuan Xu, Chengwei Liu, Yufan Cai, Yang Liu, and Meng Sun, *Why the Proof Fails in Different Versions of Theorem Provers: An Empirical Study of Compatibility Issues in Isabelle* (2025)
- S097: Dominik Winterer, Chengyu Zhang, and Zhendong Su, *On the Unusual Effectiveness of Type-Aware Operator Mutations for Testing SMT Solvers* (2020)
- S093: seL4 Project, *What the Proofs Assume* (current site, accessed 2026-08-12)
- S024: Xavier Leroy, *Formal Verification of a Realistic Compiler* (2009)
- S025: Gerwin Klein et al., *seL4: Formal Verification of an OS Kernel* (2009)
- S096: Talia Ringer, Karl Palmskog, Ilya Sergey, Milos Gligoric, and Zachary Tatlock, *QED at Large: A Survey of Engineering of Formally Verified Software* (2019)
- S051: Federal Aviation Administration, *AC 20-115D: Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178* (2017)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)


### P048 — Retirement of stale formal artefacts

**CURRENT_STATUS:** `RETAINED_IN_EVOLVED_FORM`  
**LINEAGE_CLASS:** `HYBRID`  
**FORMAL_PROPERTY_CLASS:** `retained in evolved form`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** hybrid formal/empirical evidence lineage

**ORIGINAL_FORM:** Traditional proofs were often archival mathematical artefacts, but mechanised developments made replay and dependency management possible. Large proof engineering, certification configuration control and recent compatibility studies exposed that formal evidence can lose operational validity as code, specifications, provers, libraries and environments evolve [S052, S095, S096, S113].

**PROBLEM_IT_ADDRESSED:** A formally impressive artefact can remain green in reports while no longer replaying, no longer matching the source/configuration, depending on obsolete tooling, lacking an owner or serving no current decision. Keeping it as assurance evidence creates false confidence and maintenance drag.

**ENGINEERING_CLAIM:** Formal artefacts with no current replay, model-code link, or live decision consumer should be retired or downgraded.

**MECHANISM:** Give each artefact a consumer, exact claim, source/model/tool/configuration identities, dependency graph, replay command and freshness policy. Automatically mark stale after relevant changes; repair/revalidate when decision value warrants; otherwise retire from active assurance while preserving an immutable historical archive and rationale.

**TRIGGER_OR_CONTEXT:** Trigger for every persistent proof, model, certificate, static-analysis baseline or runtime specification used across releases.

**NON_TRIGGER_OR_CHEAP_PATH:** One-off exploratory checks may be archived without maintenance if clearly labelled non-assurance and no downstream consumer relies on them.

**DEPENDENCIES_OR_PRECONDITIONS:** Artefact registry, named consumer/owner, identity/provenance hashes, dependency graph, replay environment and retirement authority.

**SPECIFICATION_PRECONDITIONS:** Claim/spec version is part of freshness; unchanged theorem text does not imply unchanged meaning.

**ABSTRACTION_PRECONDITIONS:** Model/abstraction changes trigger status review even when code is unchanged.

**ENVIRONMENT_PRECONDITIONS:** Configuration, hardware/network assumptions and operational use are freshness dependencies.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Active status requires current correspondence to the governed implementation/binary/configuration.

**TRUSTED_TOOL_PRECONDITIONS:** Archived and active toolchains are identified; checker/library upgrades are impact-assessed.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** This property is itself the currentness gate: replay and semantic impact determine active status; otherwise evidence is withdrawn.

**KNOWN_FAILURE_MODES:**
- An old PDF proof is cited although sources and libraries have changed.
- CI omits the proof because the prover no longer builds.
- A model has no release/design consumer but is maintained ceremonially.
- A certificate cannot be regenerated or checked with archived tools.
- Minor code diff bypasses proof impact despite semantic dependency.
- Artefact retirement deletes historical counterexamples or decision provenance.
- Teams retain stale green status to avoid admitting assurance loss.

**IMPORTANT_CRITICISMS:**
- Aggressive retirement can discard reusable knowledge and make future re-entry expensive.
- Fresh replay does not prove specification or correspondence freshness.
- Version compatibility failures may be superficial syntax/API churn rather than lost theorem truth.
- Archiving complete reproducible toolchains can be costly and insecure.
- Freshness intervals are poor substitutes for semantic change-impact analysis.

**HOW_THE_PROPERTY_EVOLVED:** Proof maintenance evolved from manual porting into continuous replay, semantic dependency graphs, proof repair, compatibility testing, containerised/reproducible environments and change-impact analysis. The mature governance addition is explicit deactivation: stale evidence is no longer counted as live simply because it once passed.

**MATURE_OR_EVOLVED_FORM:** Every formal artefact is ACTIVE, STALE, RETIRED or HISTORICAL. ACTIVE requires a current consumer, identity binding, reproducible replay and satisfied correspondence assumptions. STALE status automatically revokes assurance credit; RETIRED artefacts remain archived with provenance, witnesses and re-entry conditions.

**EXPECTED_ENGINEERING_PAYOFF:** Prevents zombie assurance, concentrates maintenance on live high-value claims, preserves reproducibility and historical learning, and makes loss of verification status visible after change.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- Can semantic dependency analysis reliably distinguish harmless prover/library churn from assurance-relevant change?
- What minimum archive permits long-term replay without preserving vulnerable obsolete environments?
- How should organisations value dormant proof assets that may become relevant after future redesign?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S052, S096, S113, S095  
**CRITICAL_SOURCES:** S095, S096  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S096, S113, S052  
**CONTRARY_EVIDENCE:** S095, S096

**SOURCE IDENTITIES USED:**
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S096: Talia Ringer, Karl Palmskog, Ilya Sergey, Milos Gligoric, and Zachary Tatlock, *QED at Large: A Survey of Engineering of Formally Verified Software* (2019)
- S113: Federal Aviation Administration, *AC 20-148: Reusable Software Components* (current guidance lineage, accessed 2026-08-12)
- S095: Xiaokun Luan, David Sanán, Zhe Hou, Qiyuan Xu, Chengwei Liu, Yufan Cai, Yang Liu, and Meng Sun, *Why the Proof Fails in Different Versions of Theorem Provers: An Empirical Study of Compatibility Issues in Isabelle* (2025)


### P049 — Stakeholder/world-machine validation

**CURRENT_STATUS:** `SPECIFICATION_PROPERTY`  
**LINEAGE_CLASS:** `FORMAL_SPECIFICATION_LINEAGE`  
**FORMAL_PROPERTY_CLASS:** `specification`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** formal specification lineage

**ORIGINAL_FORM:** Requirements engineering distinguished the machine from the world it is intended to affect. Zave and Jackson framed requirements, domain assumptions and machine specifications as different statements; Jackson’s world/machine view and Parnas/Madey’s monitored/controlled variables made observable phenomena and interfaces explicit [S081–S084].

**PROBLEM_IT_ADDRESSED:** A formal statement can be exact and fully proved yet encode the wrong stakeholder outcome, use unobservable variables, confuse a desired world condition with a software output, omit domain laws or validate only internal machine states. Precision (P001) is insufficient without meaning validation at the world–machine boundary.

**ENGINEERING_CLAIM:** The formal statement must be validated against stakeholder/mission/world requirements, not only internal consistency.

**MECHANISM:** Model stakeholders/mission, monitored and controlled phenomena, domain assumptions, machine interfaces and the causal/observational relation from machine behaviour to world outcome. Validate the formalisation with domain experts, scenarios, counterexamples, units/data provenance and operational measures; use independent or roundtrip translation challenge for generated formal claims.

**TRIGGER_OR_CONTEXT:** Trigger when a formal claim represents an external outcome, safety/security objective, human workflow, physical process, sensor/actuator relation or AI-generated translation from stakeholder prose.

**NON_TRIGGER_OR_CHEAP_PATH:** For a purely internal algebraic transformation with an agreed mathematical contract, direct examples and peer review may suffice without a full world–machine model.

**DEPENDENCIES_OR_PRECONDITIONS:** Identified stakeholders/mission, domain experts, observable phenomena, units/data provenance, interface definition, positive/negative scenarios and operational consumer.

**SPECIFICATION_PRECONDITIONS:** The formal statement is traceable to the stakeholder/world claim and tested against representative interpretations.

**ABSTRACTION_PRECONDITIONS:** Abstraction preserves the phenomena and causal distinctions needed for the stakeholder decision.

**ENVIRONMENT_PRECONDITIONS:** Domain laws, sensors, actuators, humans and external systems are evidenced, monitored or clearly residual.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** Implementation outputs and observations implement the formal interface and are tied to deployed configuration.

**TRUSTED_TOOL_PRECONDITIONS:** Requirement translators, units/data conversions and AI autoformalisation are untrusted unless independently checked.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Changes in mission, domain assumptions, sensors, units or operational interpretation invalidate claim status even if proof replay succeeds.

**KNOWN_FAILURE_MODES:**
- The theorem proves an internal flag while the real-world condition remains unmet.
- A sensor variable is treated as ground truth without accuracy/latency/failure semantics.
- Stakeholder concepts are collapsed into implementation data types.
- Domain assumptions are incorrect or change after deployment.
- Human/operator behaviour is omitted because it is difficult to formalise.
- A fluent autoformalisation preserves syntax but changes meaning.
- Operational success cannot be observed, so the formal claim has no empirical consumer.

**IMPORTANT_CRITICISMS:**
- World-level validation cannot generally be reduced to deductive proof because physical and human environments are uncertain.
- Stakeholders disagree, requirements evolve and some goals are normative rather than factual.
- Executable examples can still share the same conceptual error as the formal statement.
- Roundtrip or cross-prover equivalence checks detect some translation drift but do not certify stakeholder intent [S101, S102].
- Domain validation can become expensive and bureaucratic if every local predicate requires a full goal model.

**HOW_THE_PROPERTY_EVOLVED:** The requirements problem evolved from prose-to-spec translation into explicit domain assumptions, world/machine interfaces, goal-oriented refinement, scenario/counterexample validation, traceability to operational indicators and continuous monitoring of assumptions. AI autoformalisation adds a new translation boundary, strengthening the need for semantic equivalence and qualified human review.

**MATURE_OR_EVOLVED_FORM:** A mechanically checked property controls a real engineering claim only when its variables, units, observations and outputs are traceable to stakeholder/world phenomena, its domain assumptions are independently supported, and a named operational or assurance consumer can interpret the result. Proof validity and requirement validity remain separate statuses.

**EXPECTED_ENGINEERING_PAYOFF:** Prevents technically perfect proofs of irrelevant surrogates, exposes sensor/interface/domain assumptions early, and connects formal evidence to observable mission or stakeholder outcomes.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How can uncertain physical/human domain models be linked to deterministic proofs without laundering uncertainty?
- What evidence best validates generated formal requirements at scale?
- How should conflicting stakeholder goals and normative trade-offs be represented without pretending they are logical facts?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S081, S082, S083, S084  
**CRITICAL_SOURCES:** S056, S100, S101, S102  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S052, S092, S100, S051  
**CONTRARY_EVIDENCE:** S056, S100, S101, S102

**SOURCE IDENTITIES USED:**
- S081: Pamela Zave and Michael Jackson, *Four Dark Corners of Requirements Engineering* (1997)
- S082: Michael Jackson, *The World and the Machine* (1995/1997 lineage)
- S083: David L. Parnas and Jan Madey, *Functional Documents for Computer Systems* (1995)
- S084: Axel van Lamsweerde, *Formal Specification: A Roadmap* (2000)
- S056: James H. Fetzer, *Program Verification: The Very Idea* (1988)
- S100: Eric Mugnier, Yuanyuan Zhou, Ranjit Jhala, and Michael Coblenz, *On the Impact of Formal Verification on Software Development* (2025)
- S101: Jiayi Wu, Robert Joseph George, and Anima Anandkumar, *ITPEval: Benchmarking Formal Translation Across Interactive Theorem Provers* (2026, v1)
- S102: Daneshvar Amrollahi, Jerry Lopez, and Clark Barrett, *Faithful Autoformalization via Roundtrip Verification and Repair* (2026, v1)
- S052: RTCA, *DO-333 Formal Methods Supplement to DO-178C and DO-278A* (2011)
- S092: Pedro Fonseca et al., *An Empirical Study on the Correctness of Formally Verified Distributed Systems* (2017)
- S051: Federal Aviation Administration, *AC 20-115D: Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178* (2017)


### P050 — Domain-specific verified libraries/protocols

**CURRENT_STATUS:** `DOMAIN_SPECIFIC`  
**LINEAGE_CLASS:** `DOMAIN_SPECIFIC`  
**FORMAL_PROPERTY_CLASS:** `domain specific`  
**DENOMINATOR_DECISION:** `RETAINED_WITHOUT_SPLIT_MERGE_OR_ADDITION`

**HISTORICAL_ORIGIN:** domain-specific verified practice

**ORIGINAL_FORM:** Large verification projects demonstrated that a carefully scoped compiler, kernel, cryptographic implementation, protocol or library can carry reusable machine-checked guarantees. CompCert, seL4, verified TLS/crypto work and certified compilation shifted formal assurance from one-off proofs toward reusable critical components [S024–S026, S077–S080].

**PROBLEM_IT_ADDRESSED:** Many systems cannot afford end-to-end proof, but repeatedly depend on small high-consequence primitives. Reusing verified components can concentrate assurance effort—yet their guarantees are easily overextended beyond language subset, API contract, algorithm, side-channel model, hardware, build, configuration or usage domain.

**ENGINEERING_CLAIM:** Verified crypto, kernels, compilers and protocol libraries are strong evidence for narrow claims under exact assumptions.

**MECHANISM:** Select a stable critical kernel/library; define exact functional/security/refinement properties and public API preconditions; verify implementation and, where warranted, compilation/binary correspondence; publish assumptions/TCB/usage domain; validate wrappers, FFI, build provenance and deployment configuration; maintain regression proofs and algorithm/version lifecycle.

**TRIGGER_OR_CONTEXT:** Trigger for stable high-consequence components reused across products or serving as a narrow trusted computing base.

**NON_TRIGGER_OR_CHEAP_PATH:** For low-risk, rapidly changing application glue, conventional types/tests/static analysis may outperform a reusable deep-proof investment.

**DEPENDENCIES_OR_PRECONDITIONS:** Stable specification/API, proof-maintenance owner, supported targets/configurations, usage-domain declaration, integration and provenance pipeline.

**SPECIFICATION_PRECONDITIONS:** Verified properties cover the component behaviour consumers actually rely on, including error and exceptional cases.

**ABSTRACTION_PRECONDITIONS:** Cryptographic, hardware, concurrency and leakage abstractions are explicit and justified for intended deployments.

**ENVIRONMENT_PRECONDITIONS:** Platform, calling context, entropy, clocks, memory, hardware and adversary/fault assumptions are discharged downstream.

**MODEL_CODE_CORRESPONDENCE_PRECONDITIONS:** The exact source/binary/configuration used by consumers corresponds to the verified artefact; wrappers and FFI are included or separately assured.

**TRUSTED_TOOL_PRECONDITIONS:** Compiler/extraction/linker/build and proof TCB are published and reduced with verified compilation/validation where warranted.

**CURRENTNESS_OR_REPLAY_PRECONDITIONS:** Proofs, algorithms, dependencies and supported usage domains replay and are reissued/retired after security or platform change.

**KNOWN_FAILURE_MODES:**
- A verified library is called outside its preconditions or with invalid state.
- Unverified wrappers, dispatch logic, FFI or configuration dominate the deployed path.
- Functional correctness omits timing, power, cache or microarchitectural side channels.
- A verified compiler accepts only a language subset but ordinary source exceeds it.
- The deployed binary or build flags do not match the proved artefact.
- Cryptographic algorithm assumptions become obsolete.
- Reusers infer whole-system correctness from one verified component.

**IMPORTANT_CRITICISMS:**
- Assurance is highly domain- and property-specific; reuse does not automatically transfer to a new environment.
- Verified implementations can be slower, harder to integrate or dependent on specialised toolchains.
- The trusted base can include extraction, assemblers, linkers, hardware and external algorithms [S093, S094].
- Public industrial evidence is strongest for selected flagship projects, creating selection bias.
- Component proof does not establish system-level composition or usability/operability.

**HOW_THE_PROPERTY_EVOLVED:** One-off verified artefacts evolved into layered refinement, certified compilers, reusable verified crypto providers, maintained proof libraries and explicit usage-domain documentation. Binary verification, translation validation, verified low-level code and continuous replay progressively shrink—but do not erase—the integration/TCB boundary.

**MATURE_OR_EVOLVED_FORM:** A reusable verified component is an assurance-bearing package: exact theorem/property set, API contract, supported configuration and targets, residual TCB/assumptions, source-to-binary provenance, integration tests and current replay. Downstream claims are limited to compositions that discharge its usage-domain obligations.

**EXPECTED_ENGINEERING_PAYOFF:** Amortises deep proof across many systems, removes recurring defects from critical primitives, creates stable assurance boundaries and allows selective formalisation to deliver system-level leverage.

**DECISION_OR_CONSUMER:** Designer, reviewer, safety/security assessor, maintainer, release gate, certifier, operator, or downstream verifier.

**CEREMONY_VS_PROPERTY:** Notation, tool brand, proof count, certification label or 'formally verified' marketing is not the property; the retained property is the bounded checkable claim.

**OPEN_QUESTIONS:**
- How much assurance survives across wrappers, provider dispatch, FFI and platform changes?
- What economic and governance models sustain long-lived verified libraries after research funding?
- How can side-channel and hardware assumptions be made portable without exploding proof cost?
- Which composition certificates let downstream systems reuse component proofs safely?

**EVIDENCE-STRENGTH PARTITION:**

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

**PRIMARY_SOURCES:** S024, S025, S077, S078, S079, S080, S026  
**CRITICAL_SOURCES:** S093, S094  
**INDUSTRIAL_OR_DOMAIN_EVIDENCE:** S024, S025, S077, S078, S080, S113  
**CONTRARY_EVIDENCE:** S093, S094

**SOURCE IDENTITIES USED:**
- S024: Xavier Leroy, *Formal Verification of a Realistic Compiler* (2009)
- S025: Gerwin Klein et al., *seL4: Formal Verification of an OS Kernel* (2009)
- S077: Jonathan Protzenko et al., *EverCrypt: A Fast, Verified, Cross-Platform Cryptographic Provider* (2020)
- S078: Jean-Karim Zinzindohoué et al., *HACL*: A Verified Modern Cryptographic Library* (2017)
- S079: Karthikeyan Bhargavan et al., *miTLS: Verifying Protocol Implementations against Real-World Attacks* (2016)
- S080: Ramana Kumar, Magnus O. Myreen, Michael Norrish, and Scott Owens, *CakeML: A Verified Implementation of ML* (2014)
- S026: seL4 Foundation / seL4 project, *seL4 Proofs and Proof Architecture* (current site, accessed 2026-08-12)
- S093: seL4 Project, *What the Proofs Assume* (current site, accessed 2026-08-12)
- S094: David Monniaux and Sylvain Boulmé, *The Trusted Computing Base of the CompCert Verified Compiler* (2022)
- S113: Federal Aviation Administration, *AC 20-148: Reusable Software Components* (current guidance lineage, accessed 2026-08-12)


## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_FORMAL_CLAIM_MODEL

A mature formal claim is a versioned relation among engineering meaning, formal syntax and governed artefact identity:

```text
FORMAL_CLAIM_PROFILE = {
  PROPERTY, ENGINEERING_CLAIM, FORMAL_STATEMENT,
  ASSUMPTIONS, ENVIRONMENT_MODEL, FAILURE_MODEL,
  STATE_SPACE, INITIAL_CONDITION, TRANSITION_RELATION,
  SAFETY_LIVENESS_CLASS, ABSTRACTION,
  IMPLEMENTATION_CORRESPONDENCE, TRUSTED_TOOL_BOUNDARY,
  CURRENTNESS_AND_REPLAY, DECISION_CONSUMER,
  CHEAP_PATH, MATURE_FORM
}
```

Admission gates are sequential but revisable: (1) the claim is falsifiable and decision-relevant; (2) positive/negative examples challenge its translation; (3) assumptions are satisfiable and owned; (4) property class matches the method; (5) abstraction is sound for the claim; (6) the governed implementation/environment corresponds or the result is labelled model-only; (7) trusted tools are bounded; (8) replay is current. A checked derivation cannot compensate for failure at an earlier semantic gate [P001–P003, P009, P015, P021–P024, P049].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_INVARIANT_TEMPORAL_MODEL

The retained model separates state predicates from temporal obligations. P005 admits executable invariants as a cheap path; P006 requires initiation and consecution rather than sampled checking; P007 distinguishes bad-prefix exclusion from eventual progress; P008 makes fairness/scheduler premises operational; P009 matches invariant, termination, bounded-response, trace and hyperproperty claims to appropriate evidence. The mature profile records `STATE`, `INIT`, `NEXT`, invariant candidate, inductiveness obligations, temporal class, fairness, clock/bound semantics, monitorability and code/event correspondence. A green state invariant is never promoted to liveness or useful bounded progress without the missing obligations [S006–S008, S017, S021, S086, S105].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_CONTRACT_COMPOSITION_MODEL

Contracts are retained when they allocate executable obligations across callers, callees and interfering components. P010 covers pre/post/frame and exceptional behaviour; P011 covers local heap/ownership reasoning; P012 covers assume/guarantee, rely/guarantee and component composition. A mature contract identifies observable inputs/outputs, frame/ownership, rely and guarantee sets, substitution rules, failure/timeout behaviour and version compatibility. Composition is admitted only after assumptions mutually discharge and hidden shared state or cross-component interference is excluded or modelled [S002, S048, S049, S087–S089].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_ABSTRACTION_REFINEMENT_MODEL

P013 requires a declared abstraction function or concretisation relation and the direction of approximation; P014 requires simulation/refinement obligations across levels; P015 requires independent evidence that the governed source/binary/configuration implements the verified model. The profile records concrete and abstract domains, relation, preserved observations, over/under-approximation, reduction conditions, spurious-counterexample handling, refinement chain and identity/provenance. Sound abstract proof is not implementation correspondence; safe over-approximation may be unusable if alarms dominate; under-approximation cannot support absence claims [S005, S010, S011, S017, S023, S061, S092, S098].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_MODEL_CHECKING_MODEL

P016 retains exhaustive finite-state challenge when the state universe is explicit and tractable; P017 retains counterexamples as diagnostic evidence requiring concretisation and review; P018 requires bounded-depth/scope disclosure; P019 treats state-explosion management as a preservation obligation rather than free optimisation; P020 adds vacuity and specification-strength challenge. The profile records model generation, property, bounds, fairness, reductions, coverage, result class, witness validity, vacuity and correspondence. “No counterexample” ranges from a bounded negative result to a finite-model theorem and must be labelled accordingly [S007–S009, S016, S036, S059–S061, S103].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PROOF_ENGINEERING_MODEL

P021 retains mechanical replay of derivations; P022 bounds kernels, axioms, libraries, external oracles and certificates; P023 treats architecture, automation, dependency and repair as lifecycle engineering; P047 rejects prover infallibility; P048 withdraws stale evidence. The profile records theorem/logic, proof object or script, dependency/axiom graph, automation/oracles, kernel/checker, build identity, replay command, maintenance owner, change impact and active/stale status. Proof size or terseness is not an assurance metric without semantic and trust context [S042–S044, S095–S098, S108, S109].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_SMT_SAT_SYMBOLIC_MODEL

P024 separates encoding, theory fragment, solver result, timeout/unknown and certificate trust; P025 treats symbolic execution as path evidence bounded by path, environment and solver coverage. A mature profile records source-to-formula translation, bit-width/floating-point semantics, quantifier strategy, preprocessing, solver version/options, SAT/UNSAT/UNKNOWN meaning, certificate/reconstruction coverage, explored path condition and concretisation. UNSAT has no engineering force if encoding is wrong; timeout is not falsity; symbolic path coverage is not environmental completeness [S036–S041, S085, S097–S099, S108, S109].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_STATIC_ANALYSIS_TYPE_MODEL

P026 requires an explicit sound/unsound analysis boundary and alarm semantics; P027 limits type claims to their actual meta-theorem; P028 retains dependent/refinement types as selective proof carriers; P046 rejects type-safety-as-functional-correctness. The profile records abstract domain or type judgement, property class, soundness conditions, false-positive/false-negative policy, widening/escape hatches, unsafe/FFI boundaries and compilation/runtime preservation. Fast unsound analysers may be valuable triage but cannot be represented as proofs; sound alarms are not product defects until concretised [S005, S032, S033, S045–S047, S089].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_CONCURRENCY_DISTRIBUTED_VERIFICATION_MODEL

P029 covers interleavings, message/failure semantics, fairness, parameterisation and weak memory; P030 separates linearizability, serialisability, refinement and progress. The profile names histories/events, memory model, network and crash semantics, scheduler/fairness, consistency criterion, progress criterion, parameter bounds and implementation extraction/refinement. A linearizable object may be unavailable or non-durable; a serialisable schedule may violate real-time or application invariants; a sequentially consistent model may omit hardware executions [S018, S019, S030, S031, S087–S092, S105, S106].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_RUNTIME_VERIFICATION_MODEL

P031 bounds monitors by observable event vocabulary and monitorability; P032 adds monitor version, overhead, failure and fail-open/fail-closed policy. The profile records trace semantics, instrumentation, observation completeness, verdict lattice (satisfied/violated/inconclusive), latency, overhead budget, distributed ordering, monitor trust, response and source/spec identity. A green monitor means only that no observable violating prefix was reported; detection is not containment; unobservable or future liveness remains unresolved [S066–S068, S099, S104].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_VERIFIED_TOOLCHAIN_MODEL

P033 scopes compiler/interpreter/kernel semantic-preservation theorems; P034 retains per-run translation validation; P035 retains consumer-checkable certificates; P050 packages reusable verified components with usage-domain and provenance evidence. The profile follows exact source language/subset, target, undefined behaviour, passes, assembler/linker/runtime/hardware boundary, validation result, certificate checker, build identity and deployment provenance. A verified compiler does not make the source correct, and a valid translation does not establish runtime assumptions [S022–S026, S093, S094, S098, S108–S110].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_VACUITY_SPECIFICATION_GAMING_MODEL

P020 tests whether antecedents/triggers are reachable, assumptions consistent and clauses influential; P039 governs statement/assumption changes after failure. Challenge methods include witness generation, mutation, clause removal, antecedent coverage, unsat-core review, old-counterexample replay, semantic diffs and independent change approval. A legitimate requirement correction remains possible, but green status cannot be manufactured by silently excluding the original failing behaviour [S059, S060, S081, S100–S102].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PROOF_TEST_HYBRID_MODEL

P036 allocates proof, model checking, static analysis, testing, fuzzing and monitoring by distinct uncertainty; P044 rejects proof as a universal testing substitute. The strongest stack uses formal evidence for exhaustive/deductive obligations, property-based or generated tests for examples and translation, fuzzing/differential checks for tools and robustness, conformance/integration tests for model-code links, and runtime monitors for live assumptions. Redundant evidence may be retired only when one method soundly subsumes the same objective [S052–S054, S092, S097, S100].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PROOF_CURRENTNESS_CHANGE_MODEL

P023 makes proof architecture and dependencies maintainable; P048 governs ACTIVE, STALE, RETIRED and HISTORICAL status. Exact code/spec/model/library/prover/solver/config identities, semantic dependency graphs, replay logs, change-impact rules and owners are required. A theorem text can remain unchanged while its assumptions or library semantics change; a small code diff can have a large proof impact; an archived artefact is not live assurance merely because it exists [S095, S096, S113].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_LIGHTWEIGHT_COST_EFFECTIVE_MODEL

P005 retains small executable invariants; P037 legitimises bounded and selective formalisation; P042 requires failure-class/payoff triggers; P043 rejects proof breadth as maturity. Escalation begins with the cheapest sound discriminant—type/assertion/truth table/test—then bounded model, static analysis/model checking, selective theorem proof or verified kernel as decision value warrants. The model includes initial and recurring maintenance cost, reuse, trust/correspondence cost, stop criteria and retirement [S015, S016, S057, S058, S063, S064, S107, S112].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_AI_ASSISTED_FORMALISATION_FRONTIER

P040 treats LLMs as untrusted proposal generators for statements, tactics, invariants, models, explanations and repairs. Native checking is mandatory but insufficient: the statement must be semantically validated, unsafe axioms/commands audited, model/prompt/retrieval provenance stored, evaluation contamination controlled, and repository-realistic transfer reported. ITPEval’s type-check/equivalence gap, VeriSoftBench’s repository-transfer difficulty and roundtrip repair’s residual semantic drift make “proof compiles” an inadmissible proxy for faithful engineering formalisation [S101, S102, S111].

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_CEREMONY_STRIPPING_LEDGER

| CEREMONY | SURVIVING PROPERTY | BOUNDARY | PROPERTY IDS |
| --- | --- | --- | --- |
| Named notation or prover | A discriminating claim and method fit | No brand is required if another representation checks the same material failure class. | P001, P009, P037 |
| Large formal specification document | Reviewable, executable claim package | Document size and mathematical typography do not establish meaning, use or currentness. | P001, P038, P049 |
| Proof count/lines | Decision-relevant obligations discharged | Counts reward decomposition and verbosity and ignore specification/correspondence. | P038 |
| “Exhaustive” model-check label | Disclosed finite/symbolic universe and preservation assumptions | Exhaustiveness is model-relative. | P016, P018, P045 |
| Small-kernel slogan | Bounded, audited TCB and current replay | A small kernel is valuable but not infallible or semantically complete. | P022, P047 |
| Type-safe badge | Exact type theorem and escape-hatch boundary | Type safety is not functional, temporal or deployment correctness. | P027, P046 |
| Verified compiler badge | Exact semantic-preservation and build/provenance chain | Source correctness and deployment remain separate. | P033, P034 |
| Certification completion | Named objective, configuration and live correspondence | Compliance evidence is not whole-product truth. | P041 |
| AI proof pass rate | Checked derivation plus faithful statement and held-out transfer | Native checking cannot validate mistranslation or contamination. | P040 |
| Permanent proof archive | ACTIVE replayable evidence with consumer, or explicit retirement | Historical availability is not current assurance. | P023, P048 |

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_CRITICISM_LEDGER

| CRITICISM | TARGET | EVOLUTION STATUS | PROPERTY IDS | SOURCES |
| --- | --- | --- | --- | --- |
| Specification problem / wrong theorem | SPECIFICATION | PRESERVED_AND_DEEPENED | P001, P049 | S055, S056, S081–S084, S100–S102 |
| Hidden/inconsistent assumptions and vacuity | SPECIFICATION / MODEL_ASSUMPTION | REFINED | P002, P020, P039 | S059, S060, S093 |
| Model-code/environment gap | MODEL_CODE_CORRESPONDENCE | PRESERVED_AS_SEPARATE_GATE | P003, P015, P045 | S092–S094 |
| State explosion | MODEL_CHECKING | REFINED_NOT_SOLVED | P018, P019 | S007–S009, S061, S103 |
| Spurious/unsound abstraction | ABSTRACTION | REFINED | P013, P014 | S005, S061, S098 |
| Proof maintenance/brittleness | THEOREM_PROVING | REFINED_AND_OPERATIONALISED | P023, P048 | S095, S096 |
| Expertise and cost | UNDERLYING_FORMAL_PROPERTY | NARROWED_AND_PROPORTIONAL | P037, P042, P043 | S057, S063, S064, S107, S112 |
| Solver/encoding defects | SMT_SAT_OR_SYMBOLIC | HYBRIDISED_WITH_CERTIFICATES_AND_FUZZING | P022, P024, P035 | S097–S099, S108, S109 |
| Type safety overclaim | STATIC_ANALYSIS_OR_TYPES | NARROWED | P027, P046 | S045–S047, S089 |
| Runtime partial observability/overhead | RUNTIME_VERIFICATION | NARROWED_AND_REFINED | P031, P032 | S068, S099, S104 |
| Verified toolchain gaps | TRUSTED_TOOLCHAIN | REFINED | P033–P035, P050 | S093, S094, S098, S110 |
| Proof versus testing false dichotomy | CERTIFICATION_OR_FORMALITY_CEREMONY | HYBRIDISED | P036, P044 | S052–S054, S092, S100 |
| Certification paperwork as proxy | CERTIFICATION_OR_FORMALITY_CEREMONY | NARROWED | P041 | S051–S054, S113 |
| Benchmark/proof gaming | SPECIFICATION / PROXY | STILL_CONTESTED_WITH_CONTROLS | P039, P040 | S059, S101, S102, S111 |
| Proofs omit usability/performance/operations | UNDERLYING_FORMAL_PROPERTY | BOUNDARY_PRESERVED | P003, P036, P042, P049 | S056, S100, S104 |

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_EVOLUTION_UNDER_CRITICISM

| EARLIER FORM | INTERMEDIATE RESPONSE | MATURE/EVOLVED FORM | PROPERTY IDS |
| --- | --- | --- | --- |
| Ambiguous prose requirement | Precise but potentially wrong formula | Reviewable claim profile with examples, world interface and translation validation | P001, P049 |
| Implicit precondition | Explicit logical precondition | Versioned assumption register with discharge/monitoring owner | P002 |
| Whole-system proof ambition | Modular proof | Selective critical-kernel proof plus hybrid residual evidence | P012, P036, P037, P043, P050 |
| Explicit-state explosion | Symbolic/bounded/reduced search | Preservation-justified abstraction/reduction plus scope disclosure | P018, P019 |
| Monolithic proof script | Tactic automation | Proof architecture, certificates, dependencies and maintenance/currentness | P021–P023, P035, P048 |
| Trusted solver verdict | Solver cross-check | Checked certificate/reconstruction including preprocessing and theory reasoning | P024, P035 |
| Static proof only | Runtime assertion | Hybrid static proof, integration challenge and scope-bounded monitoring | P031, P032, P036 |
| Design model proof | Manual implementation review | Explicit refinement/model-code/binary correspondence chain | P014, P015, P033, P034 |
| Notation-heavy complete spec | Lightweight bounded model | Cheapest sound formal representation tied to decision/payoff | P037, P042 |
| Free-text AI answer | Kernel-checked generated proof | Untrusted proposal + kernel check + semantic translation/equivalence + held-out transfer | P040 |
| One-time proof pass | Archived proof artefact | Identity-bound continuous replay, semantic change impact and retirement | P023, P048 |

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_INTERNAL_TENSIONS

| ID | POLE A | POLE B | FAILURE IF UNGOVERNED | MATURE RECONCILIATION | PROPERTY IDS |
| --- | --- | --- | --- | --- | --- |
| T01 | Proof depth | Engineering cost | Under-assurance or proof overinvestment | Escalate by failure class and marginal decision value. | P037, P042, P043 |
| T02 | Specification precision | Specification/validation effort | Precise wrong theorem or analysis paralysis | Cheap examples/countermodels first; deepen only for consequential ambiguity. | P001, P049 |
| T03 | Abstraction | Fidelity | Spurious alarms or omitted failures | Declare approximation; refine against decision-relevant traces. | P013–P015 |
| T04 | Soundness | False positives/usability | Ignored sound tool or misleading unsound green | Label guarantee class and allocate triage/concretisation. | P026 |
| T05 | Completeness | Scalability | State explosion or incomplete search overclaim | Disclose bounds/reductions and choose targeted proof. | P016–P019 |
| T06 | Compositionality | Hidden cross-component assumptions | Locally proved components that do not compose | Mechanically discharge interface/rely contracts. | P010–P012 |
| T07 | Formal proof | Empirical environment uncertainty | Model certainty laundered into world certainty | Separate proof from correspondence and monitor/test assumptions. | P003, P036, P049 |
| T08 | Liveness theorem | Runtime unpredictability | Fairness-based progress without operational mechanism | Link fairness to scheduler/retry/resource evidence or bound claim. | P007, P008 |
| T09 | Strong types | Flexibility/evolution | Unsafe escape hatches or annotation friction | Use types for stable error classes; bound escapes and supplement. | P027, P028, P046 |
| T10 | Automation | Transparency | Opaque, brittle or wrongly trusted proof search | Retain checked artefacts, dependency/TCB disclosure and explainable failure. | P021–P024, P040 |
| T11 | Solver speed | Independent certificates | Unchecked UNSAT or unusable certificate overhead | Risk-tier certificate/reconstruction and cross-checking. | P024, P035 |
| T12 | Model simplicity | Failure-mode coverage | Tractable but irrelevant state space | Explicit environment/failure model and abstraction challenge. | P003, P013, P029 |
| T13 | Proof maintenance | Code iteration speed | Stale evidence or slowed delivery | Modular architecture, semantic impact, automatic stale status. | P023, P048 |
| T14 | Runtime monitoring | Overhead/observability | Disabled monitoring or blind green verdicts | Measure event-level overhead and use three-valued/inconclusive semantics. | P031, P032 |
| T15 | Certification stability | Live configuration change | Certified but obsolete baseline | Configuration-bound replay and incremental re-credit. | P041, P048 |
| T16 | Readable engineering argument | Machine-oriented artefact | Reviewers cannot validate meaning or developers cannot replay | Dual representation with linked source IDs and executable check. | P001, P021, P049 |
| T17 | AI assistance | Translation/benchmark contamination | Fast proof of wrong or leaked theorem | Untrusted generation, equivalence challenge, held-out repository evaluation. | P039, P040 |

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_HYBRIDISATION_PRESSURES

Formal traditions hybridised because no single evidence form controls every link in the engineering claim:

- specification proof needs stakeholder/world validation (P001 + P049);
- model proof needs implementation and environment correspondence (P003 + P014 + P015);
- model checking needs abstraction, vacuity and boundedness controls (P013 + P018–P020);
- theorem proving needs certificates/TCB and lifecycle replay (P021–P024 + P047–P048);
- static proof needs tests/fuzzing for tools, integration and unmodelled behaviour (P026–P028 + P036);
- runtime monitoring needs static reasoning about monitor generation and empirical overhead/observability evidence (P031–P032);
- verified toolchains need provenance, build identity and integration tests (P033–P035 + P050);
- AI assistance needs kernel checking, semantic translation validation, contamination controls and human claim review (P039–P040).

The mature hybrid is not “use every method”. It is a deliberately nonredundant evidence stack whose elements fail differently and whose combined scope covers the decision-relevant uncertainty.

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_STRONGEST_SURVIVING_PROPERTIES

| ID | PROPERTY | MATURE FORM | STATUS |
| --- | --- | --- | --- |
| P001 | Precise property before proof | No proof campaign begins from a slogan. The accepted object is a reviewable, versioned claim package whose formal statement discriminates material behaviours, whose translation has been challenged by positive and negative examples, and whose scope, assumptions and consumer are explicit. Mechanical proof then answers that exact claim—nothing broader. | SPECIFICATION_PROPERTY |
| P002 | Explicit assumptions and preconditions | Every formal result carries a complete, versioned assumption set with satisfiability evidence and an owner/discharge mode for each item. Hidden defaults, imported axioms and environmental premises are surfaced; assumptions that can be enforced or monitored become executable obligations; results are downgraded when deployment cannot establish them. | STRONGLY_RETAINED |
| P005 | State invariant as cheap mechanical guard | Prefer a small executable invariant when it eliminates a recurring illegal state more cheaply than a full model or theorem. State whether it is continuous, transition-boundary or sampled; prove inductiveness only when making all-reachable-state claims; and connect violation to diagnosis and safe handling. | INVARIANT_TEMPORAL_PROPERTY |
| P006 | Inductive invariant obligation | Use inductive proof only when claiming that every reachable state satisfies a predicate. Keep initiation, preservation and transition completeness separate; treat inferred strengthening as reviewable evidence; and downgrade to sampled/runtime evidence when full transition correspondence is unavailable. | INVARIANT_TEMPORAL_PROPERTY |
| P007 | Safety versus liveness distinction | Acceptance separates “nothing bad” from “something good” and names the assumptions or time bound behind progress. A safety proof cannot substitute for liveness evidence; an unbounded eventuality cannot substitute for service-level usefulness; monitorability limits are explicit. | INVARIANT_TEMPORAL_PROPERTY |
| P009 | Property-class matching | Every assurance result states its property class, method fit, approximation and non-covered classes. A type, invariant, monitor, bounded search or theorem is not promoted beyond the semantic guarantee its logic supports. | INVARIANT_TEMPORAL_PROPERTY |
| P010 | Contracts, preconditions and postconditions | A contract is a machine-consumed boundary artefact: callers can be checked against assumptions, implementations against guarantees, side effects and exceptional behaviour are explicit, and substitution/version changes are verified. Unenforced prose is not counted as contract evidence. | CONTRACT_COMPOSITION_PROPERTY |
| P012 | Assume/guarantee and compositional verification | Large systems are decomposed by explicit, versioned assumptions and guarantees that compose mechanically. Circularity, global invariants, liveness and shared resource bounds are checked separately; contracts with no live consumer are not retained as ceremony. | CONTRACT_COMPOSITION_PROPERTY |
| P013 | Sound abstraction discipline | Every abstract result states approximation direction, preserved property, omitted distinctions and spurious-result policy. Sound over-approximation supports absence claims only for the modelled concrete semantics; under-approximation supports witness finding only. Precision is tuned to a named decision. | ABSTRACTION_REFINEMENT_PROPERTY |
| P014 | Refinement/simulation correspondence | A high-level proof controls implementation only through a versioned, composable refinement/correspondence chain with explicit observations, divergence/termination treatment and unmodelled code boundary. Where full refinement is too costly, use conformance tests or translation validation and narrow the claim. | ABSTRACTION_REFINEMENT_PROPERTY |
| P015 | Model-code correspondence | Every real-world formal claim states its correspondence level: design only, source linked, generated source, compiled binary validated, or deployed instance attested. Gaps and glue code receive targeted tests/review; evidence is invalidated when identities diverge. | ASSUMPTION_SENSITIVE |
| P020 | Vacuity and specification-strength checks | A critical formal property must demonstrate satisfiable scope, reachable meaningful cases, sensitivity to each material clause and rejection of known bad scenarios. The theorem/specification change history is reviewed to distinguish legitimate correction from proof gaming. | USEFUL_BUT_EASILY_GAMED |
| P021 | Mechanical proof replay | A proof claim is accepted only with a clean, repeatable kernel check tied to exact theorem/model/code identities and a disclosed assumption/dependency set. Replay failure is an assurance failure; replay success is scoped to the checked statement and version. | THEOREM_PROVING_PROPERTY |
| P023 | Proof maintenance and currentness | A formal result has an owner, dependency manifest, clean continuous replay, theorem/assumption diff review, impact rules and retirement threshold. Repair is accepted only when the checked claim is unchanged or the change is explicitly revalidated. | RETAINED_IN_EVOLVED_FORM |
| P036 | Hybrid proof + testing/fuzzing/runtime evidence | For each material claim, identify what proof establishes and what remains uncertain; assign testing, fuzzing, review or monitoring to those residuals. Independent evidence must have a distinct oracle/model where possible. Remove layers that do not change the decision. | STRONGLY_RETAINED |
| P037 | Lightweight proportional formalisation | Formalise only the material claim and choose the cheapest sound representation that can remove its failure class. State bounds and non-covered claims; bind artefact to a consumer and lifecycle; escalate to deeper proof only when residual risk justifies it. | RETAINED_IN_EVOLVED_FORM |
| P042 | Cost/payoff trigger discipline | Formalisation is a graduated assurance investment. The selected technique is the least costly one that can soundly discriminate the material failure class at the required scope; escalation, stopping, reuse and retirement are governed by decision value and currentness rather than prestige or proof volume. | RETAINED_IN_EVOLVED_FORM |
| P048 | Retirement of stale formal artefacts | Every formal artefact is ACTIVE, STALE, RETIRED or HISTORICAL. ACTIVE requires a current consumer, identity binding, reproducible replay and satisfied correspondence assumptions. STALE status automatically revokes assurance credit; RETIRED artefacts remain archived with provenance, witnesses and re-entry conditions. | RETAINED_IN_EVOLVED_FORM |
| P049 | Stakeholder/world-machine validation | A mechanically checked property controls a real engineering claim only when its variables, units, observations and outputs are traceable to stakeholder/world phenomena, its domain assumptions are independently supported, and a named operational or assurance consumer can interpret the result. Proof validity and requirement validity remain separate statuses. | SPECIFICATION_PROPERTY |

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_CONTEXT_SPECIFIC_PROPERTIES

| ID | PROPERTY | TRIGGER | NON-TRIGGER / CHEAP PATH |
| --- | --- | --- | --- |
| P008 | Fairness and scheduler assumptions | Trigger whenever progress depends on scheduling, retries, message delivery, resource allocation or repeated opportunities. | For a synchronous finite procedure with controlled execution, prove termination or enforce a timeout directly rather than introduce abstract fairness. |
| P016 | Exhaustive finite-state challenge where warranted | Trigger for finite protocols, controllers, configurations or small concurrent designs where exhaustive exploration is tractable and consequential. | Use simulation, testing or bounded search when the model cannot be made finite without excluding the failure class or when a simple invariant suffices. |
| P018 | Bounded checking scope disclosure | Trigger whenever SAT/SMT/model-finding/symbolic search limits depth, objects, participants, loops or numeric domains. | If a finite state space is genuinely exhausted, report that directly; if one deterministic edge case is at issue, use a direct test. |
| P019 | State explosion management | Trigger when state-space estimates or failed runs show combinatorial blow-up in a decision-relevant model. | Do not introduce sophisticated reductions for a small model; use direct exploration or a simpler invariant. |
| P022 | Trusted kernel/certificate boundary | Trigger for high-consequence theorem, UNSAT, compiler/verifier or code-acceptance results where trusting the full producer is unacceptable. | For low-risk local checks, solver diversity, fuzzing and regression tests may be proportionate; document raw solver trust rather than pretending a certificate exists. |
| P024 | Solver/encoding trust boundary | Trigger whenever an SMT/SAT result discharges a material proof obligation or controls acceptance. | For a small decidable predicate, use a direct evaluator/exhaustive table; for low-risk checks, archive solver inputs and cross-check selectively. |
| P025 | Symbolic execution/path constraint scope | Trigger for input-rich, branch-heavy code where concrete witness generation is valuable and semantics/environment can be modelled. | Use fuzzing/property-based tests for cheap broad exploration, or direct proof/static analysis when all-path assurance is required and tractable. |
| P026 | Sound versus unsound static analysis boundary | Trigger whenever a static analyser’s green/red result is used as evidence beyond local developer feedback. | Use fast unsound linting freely for low-risk feedback, but label it and do not demand proof-grade governance. |
| P028 | Dependent/refinement types as selective proof carriers | Trigger when a stable data/API invariant is repeatedly violated and can be encoded locally with manageable proof burden. | Use runtime validation or ordinary types for volatile policy, uncertain sensor input or properties whose proof cost exceeds reuse value. |
| P029 | Concurrency/distributed protocol modelling | Trigger for coordination, replication, concurrency, distributed workflows, lock-free algorithms, weak-memory code or fault-tolerant protocols. | For simple isolated concurrency, race detectors/stress tests or a small state machine may remove the risk more cheaply than full protocol proof. |
| P030 | Linearizability/serialisability/refinement properties | Trigger when multiple operations overlap or transactions interleave and correctness depends on observable history. | For single-threaded or externally serialised components, direct invariants/tests may be enough. |
| P031 | Runtime monitor scope | Trigger for dynamic, partially opaque or environment-dependent properties that are observable at runtime and materially actionable. | Use a simple assertion/log query when the property is local and immediate; use static proof when violation cannot safely be allowed even once. |
| P032 | Monitor currentness and fail-open/fail-closed design | Trigger when runtime-monitor output controls traffic, shutdown, admission, release or regulatory evidence. | For advisory low-risk metrics, ordinary alerting with clear non-assurance status may be enough. |
| P033 | Verified compiler/toolchain scope | Trigger when source-level formal evidence controls a binary-level claim in critical code or compiler-introduced defects are material. | For low-risk software, compiler diversity, translation validation of critical builds or extensive testing may be cheaper than adopting a verified compiler. |
| P034 | Translation validation per-run evidence | Trigger for consequential generated code/models/verification conditions where producer verification is unavailable or stale. | For simple deterministic generators, exhaustive/differential tests or direct proof may be cheaper. |
| P035 | Proof-carrying/certificate evidence | Trigger when artefacts cross trust boundaries or expensive verification must be consumed repeatedly by independent parties. | For one local build under one trusted team, direct replay may be simpler than packaging a portable certificate. |
| P040 | AI-assisted formalisation boundary | Trigger for assistance with formal statement generation, tactic/proof search, invariant/model generation, explanation or proof repair—not as autonomous acceptance authority. | For a small deterministic property, direct human encoding/checking may be cheaper and more trustworthy than an AI translation layer. |
| P041 | Certification/formality ceremony boundary | Trigger when formal evidence is used for regulatory, contractual or independent-assurance credit, or when a reusable verified component carries inherited assurance claims. | For an internal low-risk invariant with no certification consumer, retain ordinary replay, review and change control rather than manufacturing certification-style paperwork. |
| P050 | Domain-specific verified libraries/protocols | Trigger for stable high-consequence components reused across products or serving as a narrow trusted computing base. | For low-risk, rapidly changing application glue, conventional types/tests/static analysis may outperform a reusable deep-proof investment. |

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_REJECTED_OR_SUPERSEDED_PRACTICES

| ID | PRACTICE/CARICATURE | DISPOSITION | EVOLVED REPLACEMENT |
| --- | --- | --- | --- |
| P038 | Ceremony/proxy rejection | CEREMONY_NOT_GENERAL_PROPERTY | A notation, tool or certification practice is retained only when it produces a checkable claim, witness, correspondence link or current decision. Metrics describe effort/coverage, never substitute for specification strength or real-world assurance. |
| P043 | Prove everything | REJECTED_OR_DISFAVOURED | NO_GENERAL_PROPERTY: never require proof breadth as an end in itself. Establish the minimum sufficient formal perimeter around the critical claim, make residual boundaries explicit, and widen only when additional proof changes the decision more than a cheaper evidence source would. |
| P044 | Proof eliminates testing | REJECTED_OR_DISFAVOURED | Proof and testing have noninterchangeable scopes. Remove a test only when the formal result soundly subsumes its objective and remaining model, tool, integration and environmental assumptions are covered elsewhere. Prefer independent evidence whose failure modes are not perfectly correlated. |
| P045 | Model checking explores every real behaviour | REJECTED_OR_DISFAVOURED | Claim only that the specified property holds over the identified formal transition system at the disclosed bounds and reduction assumptions. Promote this to an implementation/deployment claim only after separately establishing model construction, refinement/correspondence and environmental adequacy. |
| P046 | Type safety means functional correctness | REJECTED_OR_DISFAVOURED | A type-safety claim names the excluded error class, soundness assumptions and escape hatches. Functional correctness is claimed only when the relevant function/property is actually represented in the type and checked under a sound, terminating logic with validated specification. |
| P047 | Proof assistant cannot be wrong | ASSUMPTION_SENSITIVE | A checked theorem carries a bounded trust statement: exact kernel, logic, axioms, parser/elaborator, external oracle/certificate path, libraries and artefact provenance. Consequential results favour independently checkable certificates or reconstruction and treat proof validity as only one layer of the engineering claim. |

P038 is a retained anti-property: ceremony and proxy rejection has engineering value, but the ceremonies themselves are not general properties. P047 is assumption-sensitive rather than simply rejected because small-kernel proof checking remains strongly retained; only the infallibility claim is rejected.

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_CURRENT_STATE_AND_RESEARCH_FRONTIER

As of 12 August 2026, the decision-relevant frontier does not overturn the 50-property denominator; it sharpens assumption and evidence boundaries.

- Cross-prover AI translation is still low-yield and semantically fragile. ITPEval reports 29.1% statement pass@1 and 10.5% proof pass@1 across its evaluated translations, and its deterministic Lean equivalence check confirms only 54.0% of a selected set of native-verified source-to-Lean statement translations [S101]. This directly supports P040’s separation between type-checking and faithful translation.
- Roundtrip autoformalisation can improve formal equivalence substantially—45–61% initial equivalence to 83–85% after diagnosis-guided repair in the reported traffic-rule experiment—but formally self-consistent outputs still show semantic drift and the study is bounded to one statutory corpus and two models [S102].
- Proof currentness is an empirical engineering issue, not a hypothetical one: the Isabelle compatibility study collected 12,079 issues across four releases and classified causes and repairs [S095].
- Solver trust is moving toward independently checkable reconstruction and proof skeletons. Current work reconstructs cvc5/Alethe proofs in Isabelle and decomposes SMT evidence across preprocessing, clausification, SAT and theory reasoning rather than trusting only an UNSAT verdict [S108, S109].
- Focused bounded proof has measurable potential but not universal ROI. The unit-proof study created 73 proofs for four embedded operating systems and reported substantial recreated/new defect detection together with nontrivial development/execution cost and bounded generalisability [S107].
- Runtime verification remains observation-limited and cost-sensitive: current theory foregrounds finite-prefix knowledge and inconclusive verdicts, while empirical work shows instrumentation and event selection materially affect overhead [S099, S104].
- Concurrency verification increasingly has to name the exact memory model and reduction conditions; weak-memory formalisms and partial-order-reduction complexity prevent source-order interleaving or “optimal reduction” from being treated as free assumptions [S103, S106].
- Current industrial evidence remains heterogeneous. The Verum Dezyne study supplies a detailed modern case, while broader surveys still show domain, expertise, integration and organisational dependence rather than a universal adoption rule [S063, S064, S112].

The frontier therefore strengthens five evolved requirements: semantic validation before proof credit; independently checkable or reconstructable solver evidence for high consequence; realistic repository and change-maintenance evaluation; explicit observation/uncertainty semantics at runtime; and exact concurrency/memory/environment models. It does not support replacing human/domain claim authority with AI, treating pass@k as engineering assurance, or treating a 2026 benchmark result as mature industrial effectiveness.

## EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_OPEN_QUESTIONS

The following remain genuinely unresolved after the targeted search. They do not change the 50-property denominator but can change triggers, methods or strength in future revisions.

1. Which empirical techniques best detect semantically weak but satisfiable formal requirements before proof?
2. How much independent review or roundtrip equivalence is sufficient for AI-generated engineering specifications?
3. How should quantitative and human/physical requirements be linked to deterministic formal predicates without false precision?
4. How can large proof developments expose transitive axioms and semantic defaults in a reviewer-usable form?
5. Which environmental assumptions are economically monitorable rather than merely documented?
6. How should assurance degrade when an assumption is probabilistic or only partially observable?
7. How can environment models remain tractable without excluding correlated or rare failure modes?
8. What evidence is sufficient to justify a physical/hardware assumption that cannot itself be proved in the software logic?
9. How should monitor uncertainty be represented in acceptance decisions for partially observable systems?
10. How can implementation atomicity be extracted or validated cheaply for rapidly changing systems?
11. When does a state-machine model become less readable than scenario- or trace-based evidence?
12. What coverage measures best reveal omitted transitions rather than merely explored model states?
13. Which mutation/specification-strength metrics best identify invariants that add no real constraint?
14. How should transient violations during recovery or distributed convergence be represented?
15. When does runtime invariant overhead or false alarm rate exceed the avoided defect cost?
16. How can automatically inferred inductive invariants be ranked for semantic relevance rather than solver utility?
17. What practical evidence establishes transition completeness for code-extracted or distributed models?
18. How should induction be adapted when the implementation exposes non-atomic weak-memory steps?
19. Which liveness obligations can be reduced to safety without obscuring fairness or ranking assumptions?
20. How should operationally useful bounded progress be specified when timing is stochastic?
21. What reviewer-facing forms best communicate hyperproperties and multi-trace obligations?
22. How can fairness assumptions be calibrated against empirical scheduler/network distributions without converting a deterministic theorem into false certainty?
23. Which runtime indicators can falsify a fairness premise early enough to recover?
24. When should an unbounded liveness theorem be replaced by probabilistic or timed evidence?
25. How can engineering tools help classify claims without oversimplifying mixed properties?
26. Which cross-logic translations preserve enough semantics for integrated assurance?
27. How should quantitative uncertainty be combined with deterministic formal obligations?
28. How should behavioural contracts evolve compatibly across independently deployed services?
29. When are temporal/session contracts more cost-effective than ordinary request/response validation?
30. How can human-readable contracts remain aligned with machine-oriented verification conditions?
31. How can ownership reasoning scale cleanly across distributed resources and external devices?
32. Which unsafe-boundary proof obligations give the best cost/benefit for systems languages?
33. How should proof refactoring preserve ghost-state and resource-algebra abstractions?
34. How can global liveness and resource properties be decomposed without circular proof?
35. What contract granularity minimises both hidden coupling and maintenance cost?
36. How should empirical service-level behaviour discharge quantitative assume/guarantee conditions?
37. How can abstractions be synthesised for semantic relevance rather than benchmark performance?
38. What practical thresholds identify a sound analyser whose false-positive burden destroys net value?
39. How should learned/AI-generated abstractions be independently validated?
40. Which refinement notions best combine functional, temporal, security and quantitative observations?
41. How can refinement chains be maintained incrementally across architecture and compiler changes?
42. When is translation validation more economical than a global compiler/refinement proof?
43. How can model-code mappings be kept current at low cost in fast-changing codebases?
44. What correspondence evidence is sufficient for dynamic configuration, plugins and remote services?
45. How should reproducible build and attestation evidence compose with semantic refinement proofs?
46. Which coverage and mutation measures best expose omitted behaviours in an “exhaustive” model?
47. How should parameterised-system cutoffs be justified to engineers?
48. When does reduction complexity exceed the value of checking the full state space?
49. Which causal/minimal trace criteria best predict human debugging success?
50. How can LLM explanations be grounded so they do not invent causes beyond the trace?
51. How should counterexamples from probabilistic, timed or hyperproperty analyses be presented?
52. Which automatic summaries best communicate multiple interacting bounds to non-specialists?
53. How can adaptive bound selection avoid outcome-driven cherry-picking?
54. For which domain patterns can trustworthy cutoffs be inferred automatically?
55. How can reduction soundness and omitted independence assumptions be reviewed cheaply?
56. Which learned heuristics improve scale without benchmark overfitting or hidden unsoundness?
57. When should a team stop refining a model and invest in architecture simplification or runtime evidence instead?
58. Which specification-strength metrics correlate with field defect prevention rather than benchmark score?
59. How can vacuity and mutation analyses scale to theorem-prover specifications and hyperproperties?
60. What governance best distinguishes legitimate specification revision from outcome-driven weakening?
61. Which proof artefact formats best support long-term replay across prover evolution?
62. How can large dependency graphs be summarised without concealing axioms or semantic changes?
63. What reproducibility threshold is practical for resource-intensive industrial proof builds?
64. How can certificate formats cover preprocessing and theory combinations without prohibitive size?
65. What diversity is required for “independent” checkers to reduce common-mode semantic bugs?
66. When is differential solver checking cheaper and sufficient compared with proof certificates?
67. Which proof architectures minimise semantic maintenance cost across realistic software evolution?
68. How reliably can tools distinguish harmless refactoring from changed theorem meaning?
69. What empirical ROI models include multi-year proof maintenance and avoided regressions?
70. Can practical certificates cover all high-performance preprocessing and theory combinations?
71. Which differential/fuzzing strategies best detect encoding bugs rather than only solver bugs?
72. How should solver uncertainty and timeout be integrated into assurance decisions?
73. How can environment models and complex libraries be represented without dominating false positives?
74. Which hybrid fuzzing/symbolic policies give robust transfer beyond benchmark suites?
75. How should path coverage be related to specification coverage rather than branch counts?
76. How can organisations empirically tune soundness/usability without normalising false negatives?
77. Which suppression-review practices preserve trust over time?
78. Can proof-producing analyses deliver soundness with acceptable industrial performance across broader domains?
79. Which richer type guarantees deliver the best maintenance-adjusted payoff in evolving APIs?
80. How can unsafe/FFI boundaries be audited compositionally?
81. How should type-level quantitative/unit properties interact with runtime data uncertainty?
82. How can refinement/dependent proofs survive API and library evolution with lower repair cost?
83. Which specifications should remain dynamic to avoid overconstraining systems?
84. How can extracted-code and foreign-interface correspondence be made routine?
85. How can parameterised verification scale to realistic data, membership change and failure combinations?
86. What practical methods keep model-code links current across distributed implementation stacks?
87. How should deterministic protocol proofs combine with probabilistic infrastructure and performance evidence?
88. How can history/refinement proofs scale under weak memory and highly optimised implementations?
89. Which relaxed consistency properties best align with user-visible correctness?
90. How should external side effects and irreversible actions be incorporated into serialisability models?
91. How can monitor uncertainty and inconclusive verdicts be presented in operational decisions?
92. What decentralised monitoring designs best balance order accuracy, privacy and overhead?
93. When does runtime enforcement reduce risk versus create a new failure mode?
94. How should fail-open/fail-closed choices be optimised when safety and availability hazards compete?
95. Can monitor self-assurance avoid infinite regress without an oversized trusted stack?
96. What provenance is sufficient to reconstruct distributed verdicts after partial log loss?
97. How can property-specific preservation (constant time, timing, concurrency) be composed economically with general compiler correctness?
98. What end-to-end provenance mechanisms best bind proof to deployed binary?
99. How should verified toolchains handle evolving language standards and undefined behaviour?
100. How can validators cover aggressive transformations and property-specific semantics with acceptable cost?
101. What independence criteria prevent translator/validator common-mode errors?
102. How should chains of partial validators compose into end-to-end evidence?
103. How can certificate ecosystems remain interoperable and stable across tool evolution?
104. What policy languages are expressive enough without making checking expensive or opaque?
105. How should certificate revocation and dynamic configuration be handled?
106. How can independence and marginal information gain of evidence layers be measured?
107. Which mutation schemes best test assumptions and model-code correspondence?
108. How should conflicting formal and empirical evidence be adjudicated without automatically privileging either?
109. Which empirical predictors identify where small formal artefacts yield durable ROI?
110. How can organisations prevent “lightweight” from becoming a euphemism for unsound or stale analysis?
111. What maintenance-adjusted comparisons are possible across assertions, models, proofs and tests?
112. Which observable indicators reveal formal-method proxy gaming without creating new proxies?
113. How can public “verified” claims communicate scope without unreadable caveats?
114. Where does necessary certification traceability end and bureaucratic duplication begin?
115. How can semantic theorem diffs be made understandable to non-logician decision owners?
116. Which automatic strength relations are useful across changing representations?
117. What benchmark governance best detects theorem leakage and contamination in AI-assisted verification?
118. What scalable method establishes semantic equivalence between natural-language engineering requirements and generated formal statements?
119. How severe is benchmark contamination across proprietary and public proof corpora?
120. Can AI proof repair preserve theorem meaning and proof architecture across long-lived projects?
121. What human-review interface best exposes hidden assumptions and near-miss translations?
122. How can continuous or incremental certification preserve independence without freezing obsolete formal artefacts?
123. Which assurance objectives gain demonstrable outcome value from formal evidence rather than conventional review/testing?
124. How should tool qualification evolve for solver-backed, certificate-producing and AI-assisted verification pipelines?
125. What common outcome measures permit credible cross-project comparisons of proof, model checking, static analysis and testing?
126. How should long-run maintenance and reusable-library externalities enter assurance ROI?
127. Can organisations predict which small formal models will eliminate recurring failure classes before incurring modelling cost?
128. Which system structures and change rates make broad end-to-end proof economically sustainable?
129. How can selective verification demonstrate that omitted components do not dominate residual risk?
130. When does compositional proof genuinely approximate whole-system assurance rather than conceal interface assumptions?
131. How should evidence portfolios measure independence and correlated specification error?
132. Which testing obligations can safely be retired after formal evidence in rapidly changing systems?
133. What mutation strategies best test whether a proof/specification would detect realistic defects?
134. How can model coverage be communicated in engineering rather than syntactic terms?
135. Which code-to-model extraction methods provide useful independent correspondence rather than shared translation risk?
136. How should reductions be certified when their optimal construction is computationally hard?
137. How can rich type guarantees remain usable and stable under API evolution?
138. Which global distributed/temporal properties can be encoded compositionally without hidden assumptions?
139. How should reviewers quantify residual risk at unsafe, FFI and generated-code boundaries?
140. What is the best machine-readable TCB manifest across heterogeneous proof and solver pipelines?
141. How much checker diversity yields meaningful independence rather than common-mode semantics?
142. Can proof-assistant distributions provide end-to-end reproducible provenance without making maintenance impractical?
143. Can semantic dependency analysis reliably distinguish harmless prover/library churn from assurance-relevant change?
144. What minimum archive permits long-term replay without preserving vulnerable obsolete environments?
145. How should organisations value dormant proof assets that may become relevant after future redesign?
146. How can uncertain physical/human domain models be linked to deterministic proofs without laundering uncertainty?
147. What evidence best validates generated formal requirements at scale?
148. How should conflicting stakeholder goals and normative trade-offs be represented without pretending they are logical facts?
149. How much assurance survives across wrappers, provider dispatch, FFI and platform changes?
150. What economic and governance models sustain long-lived verified libraries after research funding?
151. How can side-channel and hardware assumptions be made portable without exploding proof cost?
152. Which composition certificates let downstream systems reuse component proofs safely?

## Replacement freeze gates

```text
historical_genealogy_complete = YES
major_school_relationships_dispositioned = YES
major_criticism_families_searched = YES
current_state_and_recent_frontier_searched = YES
formal_claim_model_complete = YES
invariant_temporal_model_complete = YES
contract_composition_model_complete = YES
abstraction_refinement_model_complete = YES
model_checking_model_complete = YES
proof_engineering_model_complete = YES
smt_sat_symbolic_model_complete = YES
static_analysis_type_model_complete = YES
concurrency_distributed_verification_model_complete = YES
runtime_verification_model_complete = YES
verified_toolchain_model_complete = YES
vacuity_specification_gaming_model_complete = YES
proof_test_hybrid_model_complete = YES
proof_currentness_change_model_complete = YES
lightweight_cost_effective_model_complete = YES
ai_assisted_formalisation_frontier_complete = YES
ceremony_stripping_complete = YES
final_property_population_frozen = YES
all_properties_dispositioned = YES
source_table_complete = YES
criticism_ledger_complete = YES
internal_tensions_complete = YES
audit_intake_complete = YES
public_documentation_intake_complete = YES
frozen_artifacts_packaged = YES
manifest_hashes_complete = YES
```

EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_RESEARCH_STATE: FROZEN
PROPERTY_POPULATION_TOTAL: 50
PROPERTY_POPULATION_EXAMINED: 50
PROPERTY_COVERAGE: 50/50
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_AUDIT_INTAKE: COMPLETE
PUBLIC_DOCUMENTATION_INTAKE: COMPLETE
FROZEN_PACKET_PACKAGED: YES
EXTERNAL_RESEARCH_READY_FOR_REPOSITORY_CROSSWALK: YES
