# EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE

**Analytical label:** `EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING`  
**Replacement freeze:** 12 August 2026  
**Population:** 50 properties examined; denominator unchanged.

## Tradition and plural genealogy

Formal methods and verification engineering did not descend from one notation or tool. Program-logical traditions grew from assertions, Hoare logic and predicate transformers; specification and refinement traditions developed through abstract data types, VDM, Z, B/Event-B and refinement calculi; temporal logic, process algebras and model checking addressed traces, concurrency and finite transition systems; abstract interpretation, type systems, symbolic execution and SAT/SMT automation pursued scalable static guarantees; theorem provers and dependent type theories made derivations mechanically replayable; runtime verification observed live executions; and verified compilers, kernels, certificates and translation validation reduced selected toolchain gaps.

The surviving engineering core is conditional rather than ceremonial. A mature use makes the intended property and assumptions explicit, chooses a representation and method fitted to the claim, checks the smallest decision-relevant obligation, binds evidence to model/code/tool/environment identity, and states what remains outside the proof. Lightweight finite models, contracts, static analyses and runtime monitors are not failed versions of whole-system theorem proving; they are different evidence forms whose value depends on soundness, scope, correspondence, failure cost and maintenance burden.

## 15 strongest surviving engineering properties

| ID | PROPERTY | PUBLIC-FACING MATURE FORM |
| --- | --- | --- |
| P001 | Precise property before proof | No proof campaign begins from a slogan. The accepted object is a reviewable, versioned claim package whose formal statement discriminates material behaviours, whose translation has been challenged by positive and negative examples, and whose scope, assumptions and consumer are explicit. Mechanical proof then answers that exact claim—nothing broader. |
| P002 | Explicit assumptions and preconditions | Every formal result carries a complete, versioned assumption set with satisfiability evidence and an owner/discharge mode for each item. Hidden defaults, imported axioms and environmental premises are surfaced; assumptions that can be enforced or monitored become executable obligations; results are downgraded when deployment cannot establish them. |
| P003 | Environment model boundary | A formal claim identifies exactly which world phenomena are represented and which are assumed. Environment behaviours with material decision impact are either modelled adversarially, enforced by architecture, tested under representative conditions, monitored online, or accepted as named residual risk. Scope changes trigger re-analysis. |
| P005 | State invariant as cheap mechanical guard | Prefer a small executable invariant when it eliminates a recurring illegal state more cheaply than a full model or theorem. State whether it is continuous, transition-boundary or sampled; prove inductiveness only when making all-reachable-state claims; and connect violation to diagnosis and safe handling. |
| P007 | Safety versus liveness distinction | Acceptance separates “nothing bad” from “something good” and names the assumptions or time bound behind progress. A safety proof cannot substitute for liveness evidence; an unbounded eventuality cannot substitute for service-level usefulness; monitorability limits are explicit. |
| P010 | Contracts, preconditions and postconditions | A contract is a machine-consumed boundary artefact: callers can be checked against assumptions, implementations against guarantees, side effects and exceptional behaviour are explicit, and substitution/version changes are verified. Unenforced prose is not counted as contract evidence. |
| P013 | Sound abstraction discipline | Every abstract result states approximation direction, preserved property, omitted distinctions and spurious-result policy. Sound over-approximation supports absence claims only for the modelled concrete semantics; under-approximation supports witness finding only. Precision is tuned to a named decision. |
| P015 | Model-code correspondence | Every real-world formal claim states its correspondence level: design only, source linked, generated source, compiled binary validated, or deployed instance attested. Gaps and glue code receive targeted tests/review; evidence is invalidated when identities diverge. |
| P016 | Exhaustive finite-state challenge where warranted | Use exhaustive exploration when a decision-relevant finite state space can be justified and completed. Publish the model, property, bounds, reductions, explored state/transition counts and completion status; pair with correspondence and vacuity checks. |
| P020 | Vacuity and specification-strength checks | A critical formal property must demonstrate satisfiable scope, reachable meaningful cases, sensitivity to each material clause and rejection of known bad scenarios. The theorem/specification change history is reviewed to distinguish legitimate correction from proof gaming. |
| P021 | Mechanical proof replay | A proof claim is accepted only with a clean, repeatable kernel check tied to exact theorem/model/code identities and a disclosed assumption/dependency set. Replay failure is an assurance failure; replay success is scoped to the checked statement and version. |
| P023 | Proof maintenance and currentness | A formal result has an owner, dependency manifest, clean continuous replay, theorem/assumption diff review, impact rules and retirement threshold. Repair is accepted only when the checked claim is unchanged or the change is explicitly revalidated. |
| P036 | Hybrid proof + testing/fuzzing/runtime evidence | For each material claim, identify what proof establishes and what remains uncertain; assign testing, fuzzing, review or monitoring to those residuals. Independent evidence must have a distinct oracle/model where possible. Remove layers that do not change the decision. |
| P037 | Lightweight proportional formalisation | Formalise only the material claim and choose the cheapest sound representation that can remove its failure class. State bounds and non-covered claims; bind artefact to a consumer and lifecycle; escalate to deeper proof only when residual risk justifies it. |
| P049 | Stakeholder/world-machine validation | A mechanically checked property controls a real engineering claim only when its variables, units, observations and outputs are traceable to stakeholder/world phenomena, its domain assumptions are independently supported, and a named operational or assurance consumer can interpret the result. Proof validity and requirement validity remain separate statuses. |

## Common caricatures and ceremonies to reject

1. **“Formal verification proves the software is correct.”** It proves a stated result under assumptions and a trust/correspondence boundary.
2. **“Model checking explores every possible real-world behaviour.”** It explores the represented state/trace space, sometimes only to a bound.
3. **“Theorem proving eliminates testing.”** Tests remain valuable for assumptions, tools, integration, environment and unintended properties.
4. **“A proof assistant cannot be wrong.”** Kernels, axioms, parsers, code generators, libraries, hardware and users form a bounded trusted base.
5. **“A precise specification is correct.”** Precision removes ambiguity; it does not establish stakeholder or world validity.
6. **“Type safety means functional correctness.”** A type system guarantees only properties encoded by its judgments and assumptions.
7. **“A verified compiler verifies the whole system.”** Compiler preservation does not establish source correctness, binary provenance, linker/hardware correctness or deployment assumptions.
8. **“More proof obligations, proof lines or formal documents mean more assurance.”** These are proxy counts unless tied to material failure classes and live decisions.
9. **“Lightweight formal methods are merely incomplete full formalisation.”** Bounded models, contracts and executable invariants can be the economically mature form.
10. **“AI-generated, type-checked proof makes the engineering claim trustworthy.”** Checking validates the generated formal statement, not the translation from requirement to statement.

## Important criticisms and limits

1. The **specification problem** permits rigorous proof of the wrong or too-weak claim.
2. **Model-code and model-world gaps** can leave verified abstractions disconnected from deployed behaviour.
3. **State explosion and path explosion** force reductions, bounds and incompleteness trade-offs.
4. **Vacuity, unreachable initial states and inconsistent assumptions** can produce green but meaningless results.
5. **Tool, solver, encoding and certificate trust** remain unless independently checked or reconstructed.
6. **Proof and model maintenance** can be brittle under source, specification, library, prover or configuration change.
7. **Industrial cost and expertise burdens** are highly contextual; comparative causal evidence is thinner than flagship case evidence.
8. **Runtime monitoring is partial observation**, and detection is not containment or recovery.
9. **Concurrency, weak memory and distributed liveness** remain assumption-sensitive and difficult to scale compositionally.
10. **AI assistance can improve search and repair while mistranslating the claim**, leaking benchmarks or optimising to a known theorem.

## How the tradition evolved under criticism

The literature does not show a simple march from informal engineering to total proof. It shows repeated narrowing and hybridisation: assertions became compositional logics; explicit-state exploration gained symbolic, partial-order and abstraction techniques; monolithic proofs yielded to modules, contracts and assume/guarantee rules; trusted solvers increasingly emit or reconstruct certificates; verified compilers coexist with translation validation; static proof is combined with fuzzing and runtime evidence; and proof artefacts are increasingly treated as versioned dependencies rather than timeless certificates. Current AI assistance continues this pattern only when generated statements and proofs are checked separately and semantic translation remains under independent review.

## Citation-ready factual claims

| CLAIM_ID | FACTUAL CLAIM | DURABLE SOURCE IDS |
| --- | --- | --- |
| F01 | Floyd’s 1967 flowchart method attached mathematical assertions to control points and reduced correctness to inductive verification conditions. | S001 |
| F02 | Hoare’s 1969 axiomatic basis made preconditions, postconditions and inference rules central to reasoning about programs. | S002 |
| F03 | Dijkstra’s weakest-precondition calculus recast program construction and verification as predicate transformation. | S003 |
| F04 | Cousot and Cousot’s abstract interpretation supplied a lattice/fixpoint foundation for sound static approximation. | S005 |
| F05 | Pnueli’s temporal-logic programme distinguished reasoning over executions from state-only assertions. | S004 |
| F06 | Model checking made exhaustive finite-state exploration and diagnostic counterexamples practical, while state explosion remained a central scalability limit. | S006, S007, S008 |
| F07 | Alloy’s lightweight analysis uses bounded relational model finding; absence of a counterexample is bounded evidence, not an unqualified proof. | S018 |
| F08 | Vacuity can let a model-checked formula pass without exercising the behaviour that gives it intended meaning. | S021 |
| F09 | Separation logic’s frame rule supports local reasoning about disjoint mutable state, but depends on ownership/aliasing models that match implementation behaviour. | S012, S013 |
| F10 | CompCert gives a high-assurance compiler-correctness result under a defined source/target semantics and toolchain boundary; it does not prove the source program correct. | S027, S028 |
| F11 | seL4’s functional-correctness result is tied to explicit hardware, boot, assembly and environment assumptions rather than proving an unconstrained deployed system. | S029, S030 |
| F12 | Runtime verification observes executions against monitors but cannot infer unobserved behaviour, and instrumentation/monitoring overhead can be material. | S032, S103, S104 |
| F13 | Industrial evidence reports important successes and recurring specification, expertise, integration and maintenance costs; it does not support either “formal methods never work” or “formalise everything”. | S040, S041, S090, S112, S113 |
| F14 | Recent proof-maintenance evidence shows theorem-prover upgrades can break large proof corpora, making version identity and replay lifecycle obligations. | S086, S087 |
| F15 | Recent AI autoformalisation work shows native type-checking can accept proofs of mistranslated statements; independent semantic-equivalence checking materially lowers that false-confidence risk. | S096, S097, S098 |
| F16 | Current solver-assurance research increasingly checks certificates, reconstructs proofs, or translates verification conditions into a separate trusted backend rather than trusting a single solver/verifier end to end. | S089, S091, S092, S108, S109 |
| F17 | Weak-memory and concurrent-program verification remains sensitive to the exact memory, scheduler and environment model, with no universal abstraction eliminating that burden. | S101, S102 |
| F18 | Repository-scale proof benchmarks and empirical unit-proof studies are beginning to test proof generation and proof-to-defect correspondence beyond isolated theorem puzzles, but broad external validity remains unresolved. | S107, S111 |

## Evidence limits and claims not to make

- Do not claim that a mechanically checked theorem establishes the intended real-world requirement without specification and correspondence evidence.
- Do not generalise flagship projects such as CompCert or seL4 into universal cost, feasibility or whole-system assurance claims.
- Do not equate bounded model-finder success, lack of warnings, solver `UNSAT`, type-checking or monitor silence with unconditional correctness.
- Do not claim a standard or certification objective demonstrates field effectiveness; it establishes an obligation or accepted evidence form in a defined domain.
- Do not claim that proof assistants have no trusted base, or that a small kernel removes parser, axiom, build, extraction and hardware risks.
- Do not treat 2025–2026 AI benchmark gains as mature industrial or certification evidence.
- Do not claim that formal methods are always too expensive; cost and return depend on failure recurrence, finite structure, criticality, reuse, automation and maintenance.
- Do not claim that the 50-property population is a universal ontology. It is a frozen analytical denominator supported by this independent source corpus.

## Suggested public page outline

1. What formal methods can and cannot prove.
2. The plural genealogy: logic, specification/refinement, model checking, theorem proving, static/type analysis, runtime and toolchains.
3. Property before proof: claim, assumptions, environment and correspondence.
4. Choosing evidence by claim shape: invariant, temporal, contract, refinement, type, certificate or monitor.
5. Lightweight and selective formalisation.
6. Model checking, counterexamples, bounds and vacuity.
7. Proof engineering, trusted bases and replay after change.
8. Verified toolchains and provenance.
9. Hybrid evidence with testing, fuzzing and runtime observation.
10. Criticism, failure modes and anti-ceremony boundaries.
11. Current AI-assisted and solver-assurance frontier.
12. Evidence limits and open questions.

## Direct lineage, convergence and domain translation

- `FORMAL_METHODS_NATIVE`: formal specification, refinement, model checking, proof engineering, abstraction, contracts and runtime verification.
- `PROGRAM_LOGIC_ANCESTRY`: Floyd assertions, Hoare logic, predicate transformers and separation logic.
- `MATHEMATICAL_LOGIC_IMPORT`: proof theory, type theory, decidability, induction and theorem-prover kernels.
- `SOFTWARE_ENGINEERING_IMPORT_OR_SHARED_ANCESTRY`: contracts, modularity, testing, configuration/currentness and requirements validation.
- `HARDWARE_VERIFICATION_IMPORT`: SAT/SMT, symbolic checking, equivalence and industrial proof automation.
- `SECURITY_ASSURANCE_IMPORT_OR_SHARED_ANCESTRY`: information flow, proof-carrying code and verified kernels; no security-lane synthesis was imported.
- `SAFETY_ASSURANCE_IMPORT_OR_SHARED_ANCESTRY`: certification objectives and high-assurance evidence; no safety-lane synthesis was imported.
- `DISTRIBUTED_SYSTEMS_IMPORT_OR_SHARED_ANCESTRY`: temporal reasoning, refinement, process models and linearizability; no distributed-systems packet was consulted.
- `HYBRID_RESOLUTION`: proof plus testing/fuzzing/runtime evidence and selective verified kernels.
- `DOMAIN_TRANSLATION`: AI-assisted formalisation, cryptographic libraries, weak memory, protocols and numerical verification.

## Current-state and frontier notes without hype

As of 12 August 2026, research is moving toward semantic evaluation of autoformalisation, repository-scale proof tasks, proof repair across prover versions, independently checkable SMT evidence, verifier translation to trusted backends, realistic runtime-monitor cost measurement, and more explicit uncertainty/partial-observation semantics. These are promising translations of established verification duties. They do not remove the specification problem, model-world correspondence burden, maintenance cost or need for domain authority. The most defensible public claim is therefore conditional: mechanical checking greatly strengthens evidence for the exact formal statement and artefact identity checked; engineering assurance requires the surrounding translation, correspondence, trust and currentness chain.

EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_RESEARCH_STATE: FROZEN
PROPERTY_POPULATION_TOTAL: 50
PROPERTY_POPULATION_EXAMINED: 50
PROPERTY_COVERAGE: 50/50
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_AUDIT_INTAKE: COMPLETE
PUBLIC_DOCUMENTATION_INTAKE: COMPLETE
FROZEN_PACKET_PACKAGED: YES
EXTERNAL_RESEARCH_READY_FOR_REPOSITORY_CROSSWALK: YES
