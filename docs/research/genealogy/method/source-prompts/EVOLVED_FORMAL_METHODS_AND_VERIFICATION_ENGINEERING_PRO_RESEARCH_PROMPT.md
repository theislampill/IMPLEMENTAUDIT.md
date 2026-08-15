@Web search

# Pro Research — Evolved Formal Methods and Verification Engineering: specifications, invariants, abstraction, refinement, model checking, theorem proving, runtime verification, proof trust, and cost-effective assurance

I want to develop a rigorous concept I am provisionally calling **Evolved Formal
Methods and Verification Engineering**.

For this research, use the analytical label:

`EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING`

This label does **not** assert that one formal methodology called “Evolved
Formal Methods and Verification Engineering” exists. It is an analytical
construct for identifying the engineering properties that survive after tracing
program verification, formal specification, refinement, model checking, theorem
proving, abstract interpretation, type systems, SMT/SAT-based verification,
runtime verification, verified toolchains and related assurance traditions
through their history, criticism, industrial application, misuse and modern
evolution.

Use web search extensively and cite sources. Prefer original primary formal
methods papers and monographs, current peer-reviewed FM/verification research,
industrial case studies, NASA/DoD/FAA or analogous authoritative evidence where
formal methods establish current practice, standards where they directly
establish verification/assurance obligations, systematic reviews, empirical
studies and serious criticism.

Do **not** analyse IMPLEMENTAUDIT or any of my repositories in this thread.

Do **not** inspect the IMPLEMENTAUDIT repository.

Do **not** read or rely on Evolved-LAW, Evolved-CSS, Evolved-SSD, Evolved
Systems Engineering, Evolved Systems Security Engineering, Evolved Systems
Safety, Evolved Statistical Engineering, Evolved Distributed Systems
Engineering, Evolved Reliability & Maintainability Engineering, or sibling
frozen packets. Informational independence matters because a later audit will
compare the corpora.

Do **not** suggest RXX numbers, GitHub issues, source changes, adoption
decisions, or repository-specific mappings.

This is an independent external research lane. Its frozen output will later be
supplied to a separate repository-audit thread.

Your job here is to produce the strongest possible external evidence corpus.


# Single-shot completion contract — research, freeze, and package in one run

Work **autonomously and continuously** from initial source discovery through
historical genealogy, current-state research, criticism, empirical/formal
limitation analysis, final property extraction, audit intake,
public-documentation intake, freeze, and packaging.

Do **not** stop after:

- a historical overview;
- a list of famous principles or algorithms;
- a current-practice survey;
- a first property hypothesis set;
- a source bibliography;
- a “next research burdens” section;
- a request for me to choose a subfield;
- a partial denominator;
- or a provisional synthesis.

Internal research phases are allowed, but they are not terminal deliverables.
Continue until every material genealogy, property family, criticism family,
assumption boundary, modern frontier and evidence burden is either dispositioned
or explicitly bounded by an evidence limit.

Use a **saturation/evidence-completeness stop rule**, not a fixed number of
rounds, sources, or minutes. Spend materially more research time rather than
returning early when an unresolved point could change the final property
population, trigger, cheap path, authority boundary, assumption set, or mature
form.

If a scholarly or empirical question remains genuinely unresolved after the
relevant search has been performed, preserve it as `UNRESOLVED`; that does not
prevent freezing.

If the platform compacts context, preserve state and continue. Do not restart or
return a provisional instalment merely because compaction occurred.

Only a genuine tool/platform impossibility may produce
`INTERRUPTED_IN_PROGRESS`. If that happens, provide exact completed/remaining
burdens and denominator status. Otherwise, the first terminal response must
already be **FROZEN and packaged**.

Once frozen, do not reopen research merely to create files. Packaging must
preserve the exact frozen research state.


# Recency and current-state duty

Research both historical genealogy and the **current state of formal methods and
verification engineering as of the run date**.

Explicitly search for:

- recent formal-methods and software/hardware-verification review literature;
- current model checking, theorem proving, SMT/SAT and abstract-interpretation
  research;
- recent industrial applications of TLA+, Alloy, B/Event-B, Z/VDM, SPIN,
  theorem provers, static analysers and related methods where evidence is
  available;
- current formally verified compilers, kernels, cryptographic libraries,
  protocols and hardware;
- recent compositional, concurrent and distributed-system verification;
- runtime verification and monitoring;
- translation validation and proof-carrying/certificate approaches;
- proof-assistant engineering, proof automation and proof-maintenance research;
- current evidence on specification quality, vacuity, state explosion,
  abstraction errors and model-code correspondence;
- recent cost/benefit, adoption and industrial empirical evidence;
- current safety/security certification use where formal evidence is materially
  involved;
- AI/LLM-assisted formalisation and proof generation as a modern translation,
  with proof-checking and specification-quality criticism;
- proof repair/maintenance under changing code/specification;
- hybrid verification approaches combining testing, fuzzing, static analysis,
  model checking, theorem proving and runtime monitoring;
- current research on lightweight/formal specification methods that preserve
  value without maximal formalisation.

Search recent work through at least the current year and prior 2–5 years where
relevant, while preserving historical primary sources needed for genealogy.

Do not assume more formalisation is more mature. Separate mechanical proof of a
formal statement from evidence that the statement, abstraction, implementation
and environment match the engineering property that matters.

# Central research question

Reconstruct:

1. how formal specification and program verification developed from early
   assertions, program logic and mathematical semantics;
2. how refinement, algebraic/specification methods, temporal logic, model
   checking, theorem proving, static analysis and type systems addressed
   different classes of correctness;
3. how safety, liveness, invariant, refinement, information-flow, concurrency
   and real-time properties differ;
4. what model checking contributed through exhaustive state exploration and
   counterexamples, and what state explosion/abstraction limits remain;
5. what theorem proving contributed and what specification/proof-maintenance
   burdens remain;
6. what abstract interpretation, SMT/SAT, symbolic execution, contracts,
   dependent types and runtime verification add as different evidence forms;
7. how industrial successes and failures expose the specification problem,
   model-code gap, environmental assumptions, vacuous proofs and trusted-tool
   boundaries;
8. when lightweight formalisation, executable invariants or model checking
   deliver more value than full theorem proving;
9. which properties survive independently of Z, B, TLA+, Alloy, SPIN, Coq,
   Isabelle, Lean, SMT solvers, proof assistants or certification branding;
10. what a mature engineering system must establish before a mechanically
    checked proof can legitimately control a real engineering claim.

The end product should answer:

> If notation wars, theorem-prover branding, certification ceremony and
> “formally verified” marketing are stripped away, what defensible engineering
> properties remain for making critical assumptions, invariants, transitions
> and acceptance obligations mechanically checkable — and when is formalisation
> worth its modelling, proof and maintenance cost?

# Historical genealogy — plural formal traditions

Build a dated genealogy.

Investigate, where supported:

- mathematical logic/computability only where directly relevant;
- Floyd assertions;
- Hoare logic;
- Dijkstra predicate transformers/weakest preconditions;
- denotational/operational/axiomatic semantics where they contribute distinct
  engineering properties;
- data refinement;
- abstract data types/algebraic specification;
- VDM;
- Z;
- B/Event-B;
- Larch where relevant;
- temporal logic and Pnueli;
- model checking: Clarke/Emerson/Sifakis and related foundations;
- symbolic model checking;
- SPIN;
- statecharts/formal state-machine methods where distinct;
- CSP/CCS/process calculi where they contribute concurrency properties;
- refinement calculus;
- theorem proving;
- HOL, Isabelle, Coq, PVS, ACL2 and related systems;
- dependent types;
- SMT/SAT solving;
- abstract interpretation;
- static analysis;
- symbolic execution;
- separation logic;
- contracts/design by contract where formal property-relevant;
- Alloy/lightweight formal methods;
- TLA+/PlusCal;
- proof-carrying code;
- translation validation;
- verified compilation/CompCert;
- formally verified kernels such as seL4 where relevant;
- hardware verification;
- protocol/distributed-system verification;
- runtime verification;
- hybrid testing + formal methods;
- modern Lean and proof-engineering translations;
- AI-assisted formalisation/proof as a domain translation.

Do not force these into one genealogy.

Classify lineage as:

`PROGRAM_LOGIC_LINEAGE`
`FORMAL_SPECIFICATION_LINEAGE`
`REFINEMENT_LINEAGE`
`TEMPORAL_LOGIC_LINEAGE`
`MODEL_CHECKING_LINEAGE`
`THEOREM_PROVING_LINEAGE`
`STATIC_ANALYSIS_AND_ABSTRACT_INTERPRETATION_LINEAGE`
`SMT_SAT_SYMBOLIC_LINEAGE`
`TYPE_SYSTEM_AND_DEPENDENT_TYPE_LINEAGE`
`CONCURRENCY_PROCESS_ALGEBRA_LINEAGE`
`RUNTIME_VERIFICATION_LINEAGE`
`VERIFIED_TOOLCHAIN_LINEAGE`
`LIGHTWEIGHT_FORMAL_METHODS_LINEAGE`
`DOMAIN_SPECIFIC`
`HYBRID`
`CONVERGENT_ENGINEERING`
`ONLY_ANALOGOUS`

For influence claims, distinguish documentary transmission from retrospective
similarity.

# Correct common formal-methods caricatures

Give explicit attention to reductions such as:

> “Formal verification proves the software is correct.”

> “Model checking explores every possible real-world behaviour.”

> “Theorem proving eliminates testing.”

> “A proof assistant cannot be wrong.”

> “If the specification is precise, it is correct.”

> “More invariants mean stronger verification.”

> “No counterexample means the property holds in deployment.”

> “Formal methods are always too expensive.”

> “Lightweight formal methods are just incomplete formal methods.”

> “Type safety means functional correctness.”

> “A verified compiler makes the whole system verified.”

> “AI-generated proof means AI-generated claim is trustworthy.”

Separate:

`HISTORICAL_FORMAL_PROPERTY`
`FORMAL_SPECIFICATION`
`PROOF_OR_MODEL_CHECKING_TECHNIQUE`
`STATIC_ANALYSIS_OR_TYPE_TECHNIQUE`
`REAL_DEPLOYED_PRACTICE`
`CERTIFICATION_OR_ASSURANCE_CEREMONY`
`FORMAL_METHODS_MARKETING`
`CRITIQUE_OF_THE_PROPERTY`
`CRITIQUE_OF_MODEL_OR_ASSUMPTION`
`MODERN_EVOLVED_FORM`

# Property before proof — specification and claim formation

Give especially deep treatment to the **specification problem**.

Investigate:

- what property is being claimed;
- stakeholder/mission meaning;
- preconditions;
- postconditions;
- invariants;
- assumptions;
- environment;
- interfaces;
- failure model;
- nondeterminism;
- safety;
- liveness;
- fairness;
- real-time bounds;
- information flow;
- resource bounds;
- quantitative properties;
- undefined/unspecified behaviour;
- exceptional behaviour;
- partial functions;
- refinement relation;
- observational equivalence;
- model scope;
- excluded states;
- units/data types;
- ambiguity;
- requirement errors.

Test distinctions:

```text
formal statement precise != formal statement correct
proved theorem != intended property
invariant inductive != invariant meaningful
safety property proved != liveness property established
model complete for proof != model complete for deployment
```

For relevant properties create a `FORMAL_CLAIM_PROFILE`:

```text
PROPERTY
ENGINEERING_CLAIM
FORMAL_STATEMENT
ASSUMPTIONS
ENVIRONMENT_MODEL
STATE_SPACE
INITIAL_CONDITION
TRANSITION_RELATION
SAFETY_LIVENESS_CLASS
ABSTRACTION
IMPLEMENTATION_CORRESPONDENCE
CHEAP_PATH
MATURE_FORM
```

# Safety, liveness, invariants and temporal properties

Investigate:

- state invariants;
- inductive invariants;
- safety properties;
- liveness;
- progress;
- termination;
- deadlock freedom;
- starvation freedom;
- fairness;
- bounded response;
- eventuality;
- temporal logic;
- temporal refinement;
- stuttering;
- real-time properties;
- trace properties;
- hyperproperties where materially useful.

Test distinctions:

```text
nothing bad happens != something good eventually happens
liveness under fairness != liveness under actual scheduler/environment
invariant holds at sampled points != invariant holds on every transition
termination proved != useful result produced
```

# Contracts, preconditions, postconditions and compositional reasoning

Investigate:

- Hoare triples;
- contracts;
- assume/guarantee;
- interface contracts;
- modular verification;
- frame conditions;
- separation logic;
- ownership;
- rely/guarantee;
- compositional model checking;
- contracts across components;
- behavioural subtyping;
- protocol/session types where relevant;
- contract evolution;
- hidden environment assumptions;
- component substitution.

Ask what makes a contract **executable/reviewable evidence** rather than precise
but disconnected prose.

# Abstraction, refinement and model correspondence

Give deep treatment to abstraction.

Investigate:

- data abstraction;
- state abstraction;
- simulation/refinement relations;
- forward/backward simulation;
- bisimulation where relevant;
- predicate abstraction;
- abstract interpretation;
- CEGAR;
- symmetry reduction;
- partial-order reduction;
- environment abstraction;
- interface abstraction;
- quotienting;
- over/under-approximation;
- soundness;
- completeness;
- abstraction leakage;
- refinement gaps;
- implementation correspondence.

Test distinctions:

```text
model proof sound != implementation refines model
over-approximation safe != useful if spurious counterexamples dominate
under-approximation bug-free != complete correctness
abstract state covers code != environment/device/protocol correspondence proved
```

Create an `ABSTRACTION_REFINEMENT_PROFILE`.

# Model checking and counterexamples

Investigate:

- explicit-state model checking;
- symbolic model checking;
- bounded model checking;
- SAT/SMT-backed checking;
- state explosion;
- partial-order reduction;
- symmetry;
- abstraction;
- CEGAR;
- fairness;
- deadlock;
- counterexample traces;
- counterexample validity;
- liveness checking;
- probabilistic model checking where distinct;
- timed model checking;
- model generation;
- vacuity;
- coverage.

Test distinctions:

```text
no counterexample in bounded depth != proof
counterexample in abstraction != implementation bug necessarily
state space exhausted != environment model correct
property holds != non-vacuously meaningful
```

For relevant properties create a `MODEL_CHECKING_PROFILE`.

# Theorem proving and proof engineering

Investigate:

- interactive theorem proving;
- automated theorem proving;
- proof assistants;
- tactics;
- proof terms;
- kernel checking;
- libraries;
- axioms;
- trusted base;
- automation;
- induction;
- coinduction;
- refinement proof;
- functional correctness;
- concurrency proofs;
- program extraction;
- proof reuse;
- proof maintenance;
- proof brittleness;
- proof refactoring;
- generated proofs;
- proof certificates;
- proof replay;
- theorem dependency graphs.

Test distinctions:

```text
proof checked != assumptions trustworthy
kernel small != toolchain/environment irrelevant
proof compiles != model/code version current
short proof != low assurance risk
large proof != stronger engineering value automatically
```

Create a `PROOF_ENGINEERING_PROFILE`.

# SMT, SAT, symbolic execution and solver-mediated assurance

Investigate:

- SAT;
- SMT;
- decidable theories;
- bit-vectors;
- arrays;
- arithmetic;
- uninterpreted functions;
- quantifiers;
- symbolic execution;
- path explosion;
- bounded reasoning;
- solver timeouts;
- unknown;
- unsat cores;
- proof certificates;
- solver bugs;
- trusted solver versus checked certificate;
- floating-point reasoning;
- nonlinear arithmetic;
- encoding correctness.

Test distinctions:

```text
SAT/SMT UNSAT != engineering property true if encoding wrong
solver timeout != property false
symbolic path coverage != all environment behaviour
constraint solved != units/domain assumptions valid
```

# Static analysis, abstract interpretation and type systems

Investigate:

- abstract interpretation;
- dataflow analysis;
- sound/unsound analyses;
- false positives;
- widening/narrowing;
- taint;
- nullness;
- bounds;
- concurrency analyses;
- type systems;
- refinement types;
- dependent types;
- ownership/borrowing;
- effect systems;
- typestate;
- session types;
- proof by type checking;
- gradual verification;
- linting versus formal analysis.

Test distinctions:

```text
type correct != functionally correct
no static warning != verified
sound analyser false positive != product defect
unsound fast analyser green != proof
```

# Concurrency and distributed-system verification

Investigate formal reasoning for:

- interleavings;
- race freedom;
- deadlock;
- linearizability;
- serialisability;
- weak memory;
- memory models;
- distributed protocols;
- consensus;
- replication;
- message loss/reordering;
- refinement to implementation;
- network/environment models;
- failure detectors;
- fairness assumptions;
- state explosion;
- parameterised systems;
- model extraction from code.

Critically investigate famous successes and the remaining model-code/deployment
gap.

# Runtime verification, monitors and enforcement

Investigate:

- runtime monitors;
- temporal monitoring;
- contracts/assertions;
- reference monitors where formal-method distinct;
- runtime enforcement;
- monitor overhead;
- partial observability;
- false confidence;
- monitor soundness;
- monitor synthesis;
- distributed runtime verification;
- logging/provenance;
- online property checking;
- fail-open/fail-closed;
- monitor failure;
- specification evolution.

Test distinctions:

```text
runtime monitor green != unobserved behaviour safe
assertion absent != property false
monitor detects violation != violation contained
monitor implementation verified != monitored source authoritative
```

# Verified compilers, translation validation and proof-carrying evidence

Investigate:

- verified compilers;
- compiler correctness;
- translation validation;
- proof-carrying code;
- certified compilation;
- proof certificates;
- verified interpreters;
- verified kernels;
- build/toolchain trust;
- assembler/linker/hardware gaps;
- undefined behaviour;
- source-to-binary correspondence;
- trusted computing base;
- reproducible/checkable proof artefacts.

Test distinctions:

```text
compiler verified != source program correct
verified source-to-assembly != deployed binary provenance established
translation validation pass != environment/runtime assumptions satisfied
```

# Vacuity, specification gaming and proof proxy failure

Give adversarial attention to formal false confidence.

Investigate:

- vacuous truth;
- overly weak specifications;
- missing preconditions;
- unreachable initial states;
- inconsistent assumptions;
- trivially true invariants;
- overly strong assumptions;
- disabled behaviour;
- proof over a reduced state space;
- omitted environment;
- selective properties;
- proof count/coverage metrics;
- proof obligations changed after failure;
- golden theorem changes;
- “prove the implementation” by weakening spec;
- benchmark overfitting;
- proof automation optimised to expected statement;
- generated formalisation that leaks intended theorem.

Separate:

`PRODUCT_DEFECT`
`SPECIFICATION_DEFECT`
`ABSTRACTION_DEFECT`
`PROOF_DEFECT`
`MODEL_CODE_CORRESPONDENCE_DEFECT`
`TRUSTED_TOOL_DEFECT`
`LEGITIMATE_SPECIFICATION_REVISION`
`PROXY_OR_PROOF_GAMING`
`UNRESOLVED`

# Formal evidence and testing — complement, not false dichotomy

Investigate:

- proof versus testing;
- testing model assumptions;
- property-based testing;
- fuzzing;
- differential testing;
- conformance testing;
- model-based testing;
- mutation testing;
- test generation from formal models;
- proof-guided testing;
- testing the trusted base;
- runtime verification;
- formal proof of critical kernel plus testing of environment/integration;
- independent implementation checks.

Ask when a hybrid evidence stack is stronger than either pure testing or maximal
proof.

# Proof/model currentness and change

Investigate:

- proof invalidation after code/spec change;
- incremental proof;
- proof dependency;
- proof repair;
- model drift;
- generated code drift;
- refactoring;
- API changes;
- environment/configuration changes;
- compiler/tool version changes;
- theorem library upgrades;
- solver version;
- proof cache;
- stale certificates;
- reproducibility;
- archived proof artefacts;
- semantic versioning of specifications;
- change-impact analysis.

Test distinctions:

```text
proof once passed != proof current
unchanged theorem text != same assumptions/library/tool semantics
code diff small != proof impact small
proof artifact available != replay reproducible
```

# Lightweight and cost-effective formal methods

Give deep treatment to proportionality.

Investigate:

- lightweight formal methods;
- bounded model finding;
- executable specifications;
- assertions/contracts;
- small state machines;
- finite model checking;
- focused proof obligations;
- proof of critical kernel;
- assume/guarantee boundaries;
- gradual verification;
- selective formalisation;
- highest-risk properties;
- proof return on investment;
- tool learning curve;
- proof maintenance;
- automation;
- reusable libraries;
- “formal methods lite” criticism.

Ask:

> When can 20 lines of an executable invariant or a finite state model eliminate
> a whole class of recurring failures more cheaply than repeated review?

Do not assume the answer is “always”.

# AI/LLM-assisted formalisation and proof — current frontier

Investigate current research on:

- theorem proving with LLM assistance;
- autoformalisation;
- tactic generation;
- proof repair;
- specification generation;
- model generation;
- counterexample explanation;
- theorem retrieval;
- benchmark contamination;
- proof checking;
- hallucinated statements;
- incorrect formalisation with valid proof;
- proof-search cost;
- human review;
- trustworthy kernels.

Treat mechanically checked output as stronger than free-text reasoning **only for
the formal statement actually checked**. Do not allow proof checking to hide a
bad translation from the engineering requirement.

# Formal-methods ceremony stripping

Separate transferable properties from named notations/tools.

Examples:

```text
TLA+ model
    property? concurrent state transitions/invariants/liveness assumptions can
              be exhaustively or systematically challenged
    TLA+ required? no

proof assistant
    property? a critical logical argument is mechanically replayable against
              explicit assumptions
    full-system theorem proving required? no

design by contract
    property? pre/post/ownership obligations are explicit and machine-checkable
    special OO framework required? no

model checker
    property? bounded/finite transition space is searched for invariant or
              temporal counterexamples
    every feature modelled? only if decision value warrants it

formal specification document
    property? the claim is precise enough to discriminate implementation states
    giant notation-heavy document required? no
```

Return a `CEREMONY_STRIPPING_LEDGER`.

# Criticism and failure history

Give criticism equal status to advocacy.

Investigate, where supported:

- specification problem / proving the wrong thing;
- formal model not matching implementation;
- deployment/environment omitted from proof;
- state explosion;
- abstraction-induced spurious results;
- unsound abstraction or translation;
- proof maintenance/brittleness;
- steep expertise/tooling cost;
- vacuous truth;
- fairness/liveness assumptions detached from runtime;
- floating-point/numerical mismatches;
- compiler/linker/hardware gaps;
- trusted-base/toolchain bugs;
- solver/encoding mistakes;
- proof assistant axioms/unsafe extensions;
- “formal verification” marketing over narrow properties;
- certification paperwork with weak live model correspondence;
- model extraction errors;
- theorem proving used where a deterministic test would be cheaper;
- type safety overclaimed as correctness;
- model checking bounded depth overclaimed as proof;
- proof generated for specification leaked from expected answer;
- benchmark-driven proof automation without external transfer;
- industrial studies showing high cost or selective applicability;
- formal artefacts going stale after code/configuration change;
- proofs that fail to address operability/usability/performance;
- proof counts/lines used as assurance proxies.

Distinguish criticism of:

`UNDERLYING_FORMAL_PROPERTY`
`SPECIFICATION`
`ABSTRACTION`
`MODEL_CHECKING`
`THEOREM_PROVING`
`SMT_SAT_OR_SYMBOLIC`
`STATIC_ANALYSIS_OR_TYPES`
`RUNTIME_VERIFICATION`
`MODEL_CODE_CORRESPONDENCE`
`TRUSTED_TOOLCHAIN`
`CERTIFICATION_OR_FORMALITY_CEREMONY`

# Evolution under criticism

For every major criticism determine whether later practice:

`PRESERVED`
`REFINED`
`GENERALIZED`
`NARROWED`
`REJECTED`
`REPLACED`
`HYBRIDISED`
`DOMAIN_SPECIFIC`
`STILL_CONTESTED`

Investigate developments such as:

- prose requirement → precise executable property;
- whole-system proof ambition → critical-kernel/selective formalisation;
- manual proof → proof automation with checked kernel;
- explicit-state explosion → symbolic/abstraction/partial-order methods;
- one monolithic proof → compositional assume/guarantee;
- proof alone → proof + testing/runtime evidence;
- theorem proof → proof certificate/replay;
- static proof → currentness/change-impact/replay;
- code-centric verification → environment/interface assumptions;
- maximal notation → lightweight executable models;
- free-text AI reasoning → machine-checked proof with translation validation;
- known examples → held-out/vacuity/specification-strength controls.

Do not assume each evolution solved its originating problem.

# Property extraction contract

Freeze a complete final property population.

For **every final property** require:

```text
PROPERTY_ID
PROPERTY_NAME
HISTORICAL_ORIGIN
LINEAGE_CLASS
ORIGINAL_FORM
PROBLEM_IT_ADDRESSED
ENGINEERING_CLAIM
FAILURE_MODE_IT_TRIES_TO_PREVENT
FORMAL_PROPERTY_CLASS
MECHANISM
TRIGGER_OR_CONTEXT
NON_TRIGGER_OR_CHEAP_PATH
DEPENDENCIES_OR_PRECONDITIONS
SPECIFICATION_PRECONDITIONS
ABSTRACTION_PRECONDITIONS
ENVIRONMENT_PRECONDITIONS
MODEL_CODE_CORRESPONDENCE_PRECONDITIONS
TRUSTED_TOOL_PRECONDITIONS
CURRENTNESS_OR_REPLAY_PRECONDITIONS
EXPECTED_ENGINEERING_PAYOFF
DECISION_OR_CONSUMER
KNOWN_FAILURE_MODES
IMPORTANT_CRITICISMS
HOW_THE_PROPERTY_EVOLVED
MATURE_OR_EVOLVED_FORM
CEREMONY_VS_PROPERTY
CURRENT_STATUS
EVIDENCE_STRENGTH
PRIMARY_SOURCES
CRITICAL_SOURCES
INDUSTRIAL_OR_DOMAIN_EVIDENCE
CONTRARY_EVIDENCE
OPEN_QUESTIONS
```

`CURRENT_STATUS` must use one of:

```text
STRONGLY_RETAINED
RETAINED_IN_EVOLVED_FORM
SPECIFICATION_PROPERTY
INVARIANT_TEMPORAL_PROPERTY
CONTRACT_COMPOSITION_PROPERTY
ABSTRACTION_REFINEMENT_PROPERTY
MODEL_CHECKING_PROPERTY
THEOREM_PROVING_PROPERTY
STATIC_ANALYSIS_TYPE_PROPERTY
RUNTIME_VERIFICATION_PROPERTY
VERIFIED_TOOLCHAIN_PROPERTY
CONTEXT_DEPENDENT
ASSUMPTION_SENSITIVE
USEFUL_BUT_EASILY_GAMED
USEFUL_BUT_EASILY_BUREAUCRATISED
DOMAIN_SPECIFIC
SUPERSEDED_BY_STRONGER_FORM
CEREMONY_NOT_GENERAL_PROPERTY
REJECTED_OR_DISFAVOURED
CONTESTED
UNRESOLVED
```

Do not silently omit candidates that fail final admission.

# Explicit property families to investigate — do not assume retention

At minimum investigate:

- precise property before proof;
- explicit assumptions/preconditions;
- safety versus liveness distinction;
- state invariants;
- transition-system models;
- contracts/preconditions/postconditions;
- assume/guarantee composition;
- abstraction/refinement correspondence;
- environment model;
- model-code correspondence;
- exhaustive finite-state challenge where warranted;
- counterexample usefulness;
- vacuity detection;
- specification-strength checks;
- theorem/proof replay;
- small trusted kernel/certificate where applicable;
- solver/encoding trust;
- sound versus unsound static analysis;
- type-system claim boundaries;
- concurrency/distributed properties;
- runtime monitor scope/currentness;
- proof/toolchain provenance;
- proof invalidation after change;
- proof maintenance/replay;
- hybrid proof + testing;
- lightweight formalisation proportionality;
- cheap deterministic invariant before repeated model reasoning;
- rejection of proof-count/formality proxies;
- retirement of stale formal artefacts with no live consumer.

Add additional properties discovered from the literature.

# Internal tensions

Identify genuine tensions, including:

- proof depth versus engineering cost;
- specification precision versus specification effort;
- abstraction versus fidelity;
- soundness versus false positives/usability;
- completeness versus scalability;
- compositionality versus hidden cross-component assumptions;
- formal proof versus empirical environment uncertainty;
- whole-system proof versus critical-kernel focus;
- liveness assumptions versus runtime unpredictability;
- strong types versus flexibility/evolution;
- proof automation versus transparency;
- solver trust versus independently checked certificates;
- model simplicity versus omitted failure modes;
- proof maintenance versus code iteration speed;
- runtime monitoring versus overhead;
- formal certification versus live configuration change;
- deterministic theorem proof versus uncertain physical/human environment;
- general reusable proof libraries versus version/assumption coupling;
- AI proof assistance versus specification/benchmark contamination;
- readable engineering argument versus machine-oriented proof artefact.

Record the standard tension fields.

# Evolved Formal Methods and Verification Engineering synthesis

Construct an evidence-backed candidate description of
`EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING`.

It should **not** mean:

> “formally prove everything.”

Test whether the evidence instead supports something closer to:

> an engineering discipline that makes the property and assumptions precise
> enough to challenge mechanically; chooses the cheapest formal representation
> capable of eliminating a material failure class; distinguishes safety,
> liveness, refinement and environment obligations; uses model checking,
> theorem proving, static analysis or runtime monitoring according to claim
> shape; binds proof to current model/code/tool identity; and treats a checked
> proof as evidence for the formal statement rather than automatic proof of the
> real-world requirement.

Treat that sentence only as a hypothesis to test.

# Relationship to other engineering traditions — informational independence

This lane must remain independent of Evolved Distributed Systems Engineering,
Evolved Reliability & Maintainability Engineering, Evolved Systems Engineering,
Evolved Systems Security Engineering, Evolved Systems Safety, Evolved
Statistical Engineering, Evolved Decision & Operations Engineering and
Evolved-LAW.

Do not read or rely on their frozen reports.

The source literature may document relationships among formal methods, software
engineering, hardware verification, security, safety, distributed systems,
control and mathematics. Record source-established relationships without
importing another lane’s synthesis.

Use:

`FORMAL_METHODS_NATIVE`
`PROGRAM_LOGIC_ANCESTRY`
`MATHEMATICAL_LOGIC_IMPORT`
`SOFTWARE_ENGINEERING_IMPORT_OR_SHARED_ANCESTRY`
`HARDWARE_VERIFICATION_IMPORT`
`SECURITY_ASSURANCE_IMPORT_OR_SHARED_ANCESTRY`
`SAFETY_ASSURANCE_IMPORT_OR_SHARED_ANCESTRY`
`DISTRIBUTED_SYSTEMS_IMPORT_OR_SHARED_ANCESTRY`
`HYBRID_RESOLUTION`
`CONVERGENT_PROPERTY`
`DOMAIN_TRANSLATION`
`ONLY_ANALOGOUS`
`UNRESOLVED_TENSION`


# Source standard

Prefer, according to claim:

1. original historical/primary sources;
2. foundational mathematical/engineering papers and monographs;
3. current authoritative standards/guidance where they directly establish
   engineering practice;
4. peer-reviewed empirical/field research;
5. systematic reviews/meta-analyses;
6. serious industrial/programme case studies with enough detail to establish
   engineering mechanisms;
7. strong criticism, replication and negative evidence;
8. tool/vendor documentation only to establish implementation behaviour, never
   as independent effectiveness evidence.

For every important source provide:

```text
SOURCE_ID
stable URL / DOI / publisher locator
author/organisation
exact title
date/version/edition
source class
exact section/page/theorem/table/figure/locator
claim supported
relation to property
contrary evidence if any
access date
open-access status
```

Do not rely on search-result snippets.

Use quotations sparingly and within copyright limits.

Separate:

`SOURCE_ESTABLISHED`
`SOURCE_INTERPRETATION`
`FORMAL_OR_THEORETICAL_RESULT`
`EMPIRICAL_OR_DOMAIN_FINDING`
`INCIDENT_OR_OUTAGE_EVIDENCE`
`HISTORICAL_INFERENCE`
`MODEL_ASSUMPTION_DEPENDENT`
`IMPLEMENTATION_OR_CASE_EVIDENCE`
`STANDARD_OR_GUIDANCE_REQUIREMENT`
`CONTESTED`
`UNVERIFIED`

Do not treat mathematical correctness under assumptions, standards compliance,
tool output, or a successful demonstration as evidence that the assumptions,
environment, integration boundary, or real engineering consequence are valid.


# Adversarial duties

For every important property ask:

- What engineering claim is actually being proved?
- Are the assumptions explicit and current?
- Could the proof be vacuous?
- Is the specification too weak or mistranslated?
- Does the abstraction soundly cover the relevant implementation behaviour?
- Does the implementation actually refine/correspond to the verified model?
- What environment/hardware/network/human behaviour is outside the model?
- Is the trusted toolchain appropriately bounded?
- Is proof replay current after source/library/tool/configuration change?
- Would a finite checker, state machine, assertion or deterministic test remove
  the failure more cheaply?
- Does another proof obligation materially change the engineering decision?
- Is model checking bounded or exhaustive?
- Is a type/static-analysis guarantee being overclaimed?
- Did later practice retain, narrow, hybridise or reject the property?

`NO_GENERAL_PROPERTY` is a valid result.

# Evidence-strength partition

For each property distinguish, where applicable:

```text
HISTORICAL_PROVENANCE_STRENGTH
FORMAL_SOUNDNESS_STRENGTH
MECHANICAL_REPLAY_STRENGTH
MODEL_CODE_CORRESPONDENCE_STRENGTH
INDUSTRIAL_CASE_STRENGTH
EMPIRICAL_COMPARATIVE_STRENGTH
CERTIFICATION_OR_DOMAIN_PRACTICE_STRENGTH
TRANSFERABILITY_STRENGTH
ASSUMPTION_SENSITIVITY
CONTRARY_EVIDENCE_STRENGTH
```

Explicitly distinguish proof strength from engineering correspondence strength.

# Required final sections

The final Markdown report must contain, in this order near its end:

```text
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_TIMELINE
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_GENEALOGY
FORMAL_VERIFICATION_VS_FORMALITY_CARICATURE
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PROPERTY_LEDGER
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_FORMAL_CLAIM_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_INVARIANT_TEMPORAL_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_CONTRACT_COMPOSITION_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_ABSTRACTION_REFINEMENT_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_MODEL_CHECKING_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PROOF_ENGINEERING_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_SMT_SAT_SYMBOLIC_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_STATIC_ANALYSIS_TYPE_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_CONCURRENCY_DISTRIBUTED_VERIFICATION_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_RUNTIME_VERIFICATION_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_VERIFIED_TOOLCHAIN_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_VACUITY_SPECIFICATION_GAMING_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PROOF_TEST_HYBRID_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PROOF_CURRENTNESS_CHANGE_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_LIGHTWEIGHT_COST_EFFECTIVE_MODEL
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_AI_ASSISTED_FORMALISATION_FRONTIER
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_CEREMONY_STRIPPING_LEDGER
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_CRITICISM_LEDGER
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_EVOLUTION_UNDER_CRITICISM
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_INTERNAL_TENSIONS
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_HYBRIDISATION_PRESSURES
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_STRONGEST_SURVIVING_PROPERTIES
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_CONTEXT_SPECIFIC_PROPERTIES
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_REJECTED_OR_SUPERSEDED_PRACTICES
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_CURRENT_STATE_AND_RESEARCH_FRONTIER
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_OPEN_QUESTIONS
```

# Final audit intake

Then produce the complete:

`EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_AUDIT_INTAKE`

with the standard population/source fields and, for every crosswalk-worthy
property:

```text
PROPERTY_ID
PROPERTY_NAME
ENGINEERING_CLAIM_OR_FAILURE_MODE
MATURE_FORM
TRIGGER
CHEAP_PATH
FORMAL_CLAIM_PROFILE
ABSTRACTION_REFINEMENT_PROFILE
MODEL_CHECKING_PROFILE
PROOF_ENGINEERING_PROFILE
MODEL_CODE_CORRESPONDENCE_PROFILE
CURRENTNESS_REPLAY_PROFILE
REQUIRED_PRECONDITIONS
EVIDENCE_STRENGTH
CRITICISMS
ANTI_CEREMONY_BOUNDARY
POSSIBLE_CONFLICTING_PROPERTY
QUESTIONS_FOR_REPOSITORY_AUDIT
```

Also include:

```text
CEREMONIES_TO_NOT_BLINDLY_ADOPT
CONTEXTS_WHERE_PROPERTY_SHOULD_NOT_TRIGGER
PROPERTIES_REQUIRING_PRECISE_FORMAL_CLAIM
PROPERTIES_REQUIRING_ENVIRONMENT_OR_MODEL_CORRESPONDENCE
PROPERTIES_REQUIRING_MECHANICAL_REPLAY
PROPERTIES_REQUIRING_TRUSTED_TOOLCHAIN_BOUNDARY
PROPERTIES_WITH_STRONG_FORMAL_BUT_WEAK_REAL_WORLD_CORRESPONDENCE
PROPERTIES_WITH_STRONG_INDUSTRIAL_OR_DOMAIN_SUPPORT
PROPERTIES_WITH_MIXED_OR_WEAK_SUPPORT
SPECIFICATION_OR_VACUITY_GAMING_RISKS
UNRESOLVED_PROPERTIES
```

`QUESTIONS_FOR_REPOSITORY_AUDIT` must remain questions. Examples:

> Is an executor-ready state represented as an invariant/state transition that
> can be checked mechanically, or only as prose the model must remember?

> Can a proof/test remain green after the model, assumptions, source or runtime
> configuration it refers to changes?

> Does the target distinguish “property proved in model” from “implementation
> and environment correspond to model”?

> Could the acceptance theorem be vacuously true because the initial state or
> precondition excludes the failing case?

> Is a heavyweight proof being used where a small deterministic invariant or
> finite state checker would eliminate the failure class more cheaply?

Do **not** answer those target-system questions here.


# Public-documentation intake

Also produce the lineage-specific:

`EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE`

containing:

- a 1–2 paragraph source-grounded explanation of the tradition and its plural
  genealogy;
- 8–15 strongest surviving engineering properties;
- 5–10 common caricatures/ceremonies to reject;
- 5–10 important criticisms/limits;
- a concise explanation of how the tradition evolved under criticism;
- 10–20 citation-ready factual claims linked to durable source IDs;
- explicit evidence limits and claims not to make;
- a suggested public page outline;
- direct-lineage versus convergence/domain-translation distinctions;
- current-state/frontier notes suitable for public explanation without hype.

Do not mention IMPLEMENTAUDIT or map properties to a repository in this intake.



# Automatic packaging contract — same run, no follow-up prompt

After freezing, automatically create downloadable artefacts. Do **not** wait for
a packaging request.

Create these exact or semantically equivalent filenames:

```text
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_FROZEN_REPORT.md
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PROPERTY_LEDGER.json
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_SOURCE_TABLE.json
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_AUDIT_INTAKE.md
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE.md
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_FROZEN_MANIFEST.json
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_FROZEN_PACKET.zip
```

The machine-readable property ledger must contain the **entire frozen
denominator**, including rejected, ceremonial, contested, assumption-sensitive,
domain-specific, superseded and unresolved properties.

The source table must contain the exact source identities/locators actually
supporting the report.

The manifest must include:

```text
filename
byte_count
sha256
```

for every packaged artefact.

The ZIP must contain the complete frozen artefact set.

Packaging must not reopen or revise frozen research. Record syntax-only
normalisation required for machine readability.

If file-generation tools are unavailable, emit all complete artefacts inline in
clearly delimited blocks and state `PACKAGING_TOOL_UNAVAILABLE`; do not omit
ledgers/intakes merely because packaging cannot be automated.


# Final completion gates

Do not issue the terminal answer until all are true:

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

# Required terminal receipt

End the frozen report and the user-facing final response with exactly:

```text
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_RESEARCH_STATE: FROZEN
PROPERTY_POPULATION_TOTAL: <N>
PROPERTY_POPULATION_EXAMINED: <N>
PROPERTY_COVERAGE: <N>/<N>
EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_AUDIT_INTAKE: COMPLETE
PUBLIC_DOCUMENTATION_INTAKE: COMPLETE
FROZEN_PACKET_PACKAGED: YES
EXTERNAL_RESEARCH_READY_FOR_REPOSITORY_CROSSWALK: YES
```

Do not return a provisional research instalment in place of this receipt.
