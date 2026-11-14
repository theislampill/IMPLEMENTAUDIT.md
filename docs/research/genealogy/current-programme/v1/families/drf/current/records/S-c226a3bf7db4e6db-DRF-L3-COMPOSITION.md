> **Original scientific report, normalized for public reading.** Scientific source SHA-256 `c226a3bf7db4e6dbd5a2032bddfc3ec88d4200eb3185686d358146846809e6b4`. Author-state and earlier review statements are dated source history; the [current account](../DRF-L3.md) and [original qualification identities](../QUALIFICATION_AND_REVIEW_BINDINGS.json) distinguish later accepted status. Acquisition and runtime identifiers are omitted; no new scientific execution is claimed.

# Guarded composition and novelty assessment

These are neutral within-lineage relations with explicit shared objects, partial contributions, independently examined reverses and cheap alternatives. Generic co-use grants no implication. No irreducible new property is admitted by the examined novelty tests.

## Composition

<a id="r01"></a>
### R01 — Inductive evidence contributes to safety

**Id:** R01

**Name:** Inductive evidence contributes to safety

**Source properties:** [P006](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Receiving properties:** [P007](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Shared object:** One transition system, an invariant I with initiation and consecution, and an implication from I to the selected safety predicate P.

**Joint guard:** One transition system, an invariant I with initiation and consecution, and an implication from I to the selected safety predicate P.

**Material contribution:** Establishes P for reachable states; liveness, fairness and implementation correspondence remain separate.

**Reverse direction assessment:** Safety alone does not establish that P itself is inductive; C03 refutes that reverse inference.

**Counterexample and positive control:** [C03](../SOURCE_MAP.md#s-0be00f7164600b45), [C04](../SOURCE_MAP.md#s-0be00f7164600b45).

**Nontrigger and cheap path:** A direct reachability argument or finite enumeration may already establish P.

**Cost:** Added checks are warranted only if this contribution changes a consequence-sensitive decision; no empirical superiority is demonstrated by the local case.

**Authority boundary:** Neutral within-lineage research; no target adoption, execution authority or cross-lineage acceptance.

**Novelty assessment:** No new property: this is the inherited induction and consequence rule.

**Evidence sources:** [S001](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S003](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

**Reentry:** Reopen if an inherited relation no longer subsumes the proposed composite or if a specific claim's semantics/premises change.

<a id="r02"></a>
### R02 — Abstraction transports a completed search result

**Id:** R02

**Name:** Abstraction transports a completed search result

**Source properties:** [P013](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Receiving properties:** [P016](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Shared object:** A sound over-approximation for the selected universal property and an actually completed abstract check.

**Joint guard:** A sound over-approximation for the selected universal property and an actually completed abstract check.

**Material contribution:** Can establish safety of the concrete model; the preservation relation and any model-to-code correspondence remain premises.

**Reverse direction assessment:** An abstract counterexample can guide model repair without establishing a sound relation or a concrete failure; C05 gives a spurious witness.

**Counterexample and positive control:** [C05](../SOURCE_MAP.md#s-0be00f7164600b45), [C06](../SOURCE_MAP.md#s-0be00f7164600b45), [C15](../SOURCE_MAP.md#s-0be00f7164600b45).

**Nontrigger and cheap path:** Concrete enumeration can avoid abstraction; an under-approximate witness uses a different inference direction.

**Cost:** Added checks are warranted only if this contribution changes a consequence-sensitive decision; no empirical superiority is demonstrated by the local case.

**Authority boundary:** Neutral within-lineage research; no target adoption, execution authority or cross-lineage acceptance.

**Novelty assessment:** No new property: the existing abstraction and checking rules express the relation.

**Evidence sources:** [S005](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S061](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

**Reentry:** Reopen if an inherited relation no longer subsumes the proposed composite or if a specific claim's semantics/premises change.

<a id="r03"></a>
### R03 — Contracts and frames support modular composition

**Id:** R03

**Name:** Contracts and frames support modular composition

**Source properties:** [P010](../SOURCE_MAP.md#s-460b1f2b7104c948), [P011](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Receiving properties:** [P012](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Shared object:** Compatible preconditions and postconditions, shared state semantics and justified frame or ownership conditions; circular rules require their own soundness conditions.

**Joint guard:** Compatible preconditions and postconditions, shared state semantics and justified frame or ownership conditions; circular rules require their own soundness conditions.

**Material contribution:** Discharges part of a composition argument; environment, progress and unmodeled sharing can remain open.

**Reverse direction assessment:** A system goal can inform component-contract design, but it does not prove that each component satisfies the contract.

**Counterexample and positive control:** [C07](../SOURCE_MAP.md#s-0be00f7164600b45), [C08](../SOURCE_MAP.md#s-0be00f7164600b45).

**Nontrigger and cheap path:** A small monolithic model or direct proof can be adequate.

**Cost:** Added checks are warranted only if this contribution changes a consequence-sensitive decision; no empirical superiority is demonstrated by the local case.

**Authority boundary:** Neutral within-lineage research; no target adoption, execution authority or cross-lineage acceptance.

**Novelty assessment:** No new property: contract and frame composition already express this material partial contribution.

**Evidence sources:** [S002](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S048](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [N004](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

**Reentry:** Reopen if an inherited relation no longer subsumes the proposed composite or if a specific claim's semantics/premises change.

<a id="r04"></a>
### R04 — Certificate checking strengthens a solver result

**Id:** R04

**Name:** Certificate checking strengthens a solver result

**Source properties:** [P022](../SOURCE_MAP.md#s-460b1f2b7104c948), [P035](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Receiving properties:** [P024](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Shared object:** A complete accepted certificate bound to the intended encoded query under identified checker rules and assumptions.

**Joint guard:** A complete accepted certificate bound to the intended encoded query under identified checker rules and assumptions.

**Material contribution:** Reduces reliance on the search implementation while leaving encoding adequacy, parsing, runtime and checker trust explicit.

**Reverse direction assessment:** A solver can produce checker input; its raw answer does not establish the correctness of the checker or the encoding.

**Counterexample and positive control:** [C09](../SOURCE_MAP.md#s-0be00f7164600b45), [C13](../SOURCE_MAP.md#s-0be00f7164600b45).

**Nontrigger and cheap path:** Direct evaluation can suffice; explicitly accepted solver trust may be proportionate to a low-consequence decision.

**Cost:** Added checks are warranted only if this contribution changes a consequence-sensitive decision; no empirical superiority is demonstrated by the local case.

**Authority boundary:** Neutral within-lineage research; no target adoption, execution authority or cross-lineage acceptance.

**Novelty assessment:** No new property: the certificate interface and encoding boundary already express the conditions.

**Evidence sources:** [S108](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S109](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [N007](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [N008](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

**Reentry:** Reopen if an inherited relation no longer subsumes the proposed composite or if a specific claim's semantics/premises change.

<a id="r05"></a>
### R05 — Compiler preservation contributes to application correspondence

**Id:** R05

**Name:** Compiler preservation contributes to application correspondence

**Source properties:** [P033](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Receiving properties:** [P015](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Shared object:** The actual source and target objects match the proved compilation stage and versions, and the selected property is preserved by the stated relation.

**Joint guard:** The actual source and target objects match the proved compilation stage and versions, and the selected property is preserved by the stated relation.

**Material contribution:** Supports one correspondence edge; front ends, linking, hardware, environment and omitted observations retain their own duties.

**Reverse direction assessment:** An application property can identify necessary compiler observations; it does not prove semantic preservation by the compiler.

**Counterexample and positive control:** [C11](../SOURCE_MAP.md#s-0be00f7164600b45), [C15](../SOURCE_MAP.md#s-0be00f7164600b45).

**Nontrigger and cheap path:** A direct exhaustive check or test can be adequate for a narrower claim.

**Cost:** Added checks are warranted only if this contribution changes a consequence-sensitive decision; no empirical superiority is demonstrated by the local case.

**Authority boundary:** Neutral within-lineage research; no target adoption, execution authority or cross-lineage acceptance.

**Novelty assessment:** No new property: composing established relations does not confer automatic whole-system assurance.

**Evidence sources:** [S110](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S094](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

**Reentry:** Reopen if an inherited relation no longer subsumes the proposed composite or if a specific claim's semantics/premises change.

<a id="r06"></a>
### R06 — Runtime evidence challenges an empirical proof premise

**Id:** R06

**Name:** Runtime evidence challenges an empirical proof premise

**Source properties:** [P031](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Receiving properties:** [P036](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Shared object:** The monitor observes events relevant to a testable application premise with the required domain, coverage and timing.

**Joint guard:** The monitor observes events relevant to a testable application premise with the required domain, coverage and timing.

**Material contribution:** A violating observation can falsify the premise. A confirming observation supports only its stated observed trace and coverage; it is not proof of all future behavior.

**Reverse direction assessment:** A formal claim can identify what to observe, but it does not create observability or intervention authority.

**Counterexample and positive control:** [C10](../SOURCE_MAP.md#s-0be00f7164600b45), [C01](../SOURCE_MAP.md#s-0be00f7164600b45).

**Nontrigger and cheap path:** A pure theorem needs no physical monitor; a simple assertion can be sufficient for the selected empirical check.

**Cost:** Added checks are warranted only if this contribution changes a consequence-sensitive decision; no empirical superiority is demonstrated by the local case.

**Authority boundary:** Neutral within-lineage research; no target adoption, execution authority or cross-lineage acceptance.

**Novelty assessment:** No new property: this is a relation between evidence roles, with no implicit prevention guarantee.

**Evidence sources:** [S099](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S092](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S100](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

**Reentry:** Reopen if an inherited relation no longer subsumes the proposed composite or if a specific claim's semantics/premises change.

<a id="r07"></a>
### R07 — Proof checking and statement validation bound AI assistance

**Id:** R07

**Name:** Proof checking and statement validation bound AI assistance

**Source properties:** [P021](../SOURCE_MAP.md#s-460b1f2b7104c948), [P049](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Receiving properties:** [P040](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Shared object:** The intended statement is identified, translation adequacy is justified at the claimed scope, and the actual proof checks under its explicit assumptions.

**Joint guard:** The intended statement is identified, translation adequacy is justified at the claimed scope, and the actual proof checks under its explicit assumptions.

**Material contribution:** Establishes the formal claim and the separately justified translation result; shared omissions and data exposure can remain unresolved.

**Reverse direction assessment:** Formal diagnostics can inform an AI-assisted repair, but they do not prove intent preservation or a universal cost advantage.

**Counterexample and positive control:** [C13](../SOURCE_MAP.md#s-0be00f7164600b45), [C02](../SOURCE_MAP.md#s-0be00f7164600b45).

**Nontrigger and cheap path:** A human encoding or whole-regeneration baseline can be adequate or superior under a particular comparison.

**Cost:** Added checks are warranted only if this contribution changes a consequence-sensitive decision; no empirical superiority is demonstrated by the local case.

**Authority boundary:** Neutral within-lineage research; no target adoption, execution authority or cross-lineage acceptance.

**Novelty assessment:** No new property: the existing statement/proof distinction and qualified repair relation suffice.

**Evidence sources:** [S102](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S111](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [N007](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

**Reentry:** Reopen if an inherited relation no longer subsumes the proposed composite or if a specific claim's semantics/premises change.

<a id="r08"></a>
### R08 — Change impact supports justified reuse

**Id:** R08

**Name:** Change impact supports justified reuse

**Source properties:** [P023](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Receiving properties:** [P050](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Shared object:** The claim, dependencies, artifacts and use boundaries remain compatible, with affected changes identified.

**Joint guard:** The claim, dependencies, artifacts and use boundaries remain compatible, with affected changes identified.

**Material contribution:** Retains unaffected evidence and permits justified reuse; changed premises receive proportionate reconsideration.

**Reverse direction assessment:** A reuse context supplies assumptions for change-impact analysis; it does not establish proof-script replay.

**Counterexample and positive control:** [C12](../SOURCE_MAP.md#s-0be00f7164600b45), [C18](../SOURCE_MAP.md#s-0be00f7164600b45), [C11](../SOURCE_MAP.md#s-0be00f7164600b45).

**Nontrigger and cheap path:** Unchanged accepted use can avoid a full reproof; a dormant result can be retained as historical evidence.

**Cost:** Added checks are warranted only if this contribution changes a consequence-sensitive decision; no empirical superiority is demonstrated by the local case.

**Authority boundary:** Neutral within-lineage research; no target adoption, execution authority or cross-lineage acceptance.

**Novelty assessment:** No new property: currentness and correspondence conditions already express this relation.

**Evidence sources:** [S095](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S113](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

**Reentry:** Reopen if an inherited relation no longer subsumes the proposed composite or if a specific claim's semantics/premises change.

## Novelty

<a id="v01"></a>
### V01 — A new invariant-plus-runtime assurance property

**Id:** V01

**Candidate:** A new invariant-plus-runtime assurance property

**Parents:** [P006](../SOURCE_MAP.md#s-460b1f2b7104c948), [P031](../SOURCE_MAP.md#s-460b1f2b7104c948), [P036](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Ablation:** Removing induction leaves observed traces only; removing monitoring can leave a valid pure-model safety proof. Neither component is universally necessary.

**Failure witness:** C01, C03 and C10 separate model validity, unsafe extension and missing observations.

**Subsumption:** Native P036 already conditions complementary evidence on unresolved empirical premises; R06 records the partial relation.

**Decision:** NO_IRREDUCIBLE_NEW_PROPERTY_ADMITTED

<a id="v02"></a>
### V02 — A new certificate-plus-translation correctness property

**Id:** V02

**Candidate:** A new certificate-plus-translation correctness property

**Parents:** [P022](../SOURCE_MAP.md#s-460b1f2b7104c948), [P024](../SOURCE_MAP.md#s-460b1f2b7104c948), [P034](../SOURCE_MAP.md#s-460b1f2b7104c948), [P035](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Ablation:** A certificate cannot repair the encoding by itself; an exact small truth table can settle the query without a portable certificate. Component necessity is conditional.

**Failure witness:** C09 includes wrong 8-bit encoding and a tampered resolution certificate.

**Subsumption:** The existing encoding, certificate and translation boundaries, plus R04, already express the conditions.

**Decision:** NO_IRREDUCIBLE_NEW_PROPERTY_ADMITTED

<a id="v03"></a>
### V03 — A new AI roundtrip proof guarantee

**Id:** V03

**Candidate:** A new AI roundtrip proof guarantee

**Parents:** [P001](../SOURCE_MAP.md#s-460b1f2b7104c948), [P021](../SOURCE_MAP.md#s-460b1f2b7104c948), [P040](../SOURCE_MAP.md#s-460b1f2b7104c948), [P049](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Ablation:** Removing intent validation permits a shared omission; removing AI can leave a human statement and valid proof. AI is not necessary for the underlying guarantee.

**Failure witness:** C13 has two translations omitting q; S102 provides qualified baseline counterevidence.

**Subsumption:** The existing statement/proof separation and guarded repair relation R07 subsume this candidate.

**Decision:** NO_IRREDUCIBLE_NEW_PROPERTY_ADMITTED

<a id="v04"></a>
### V04 — A new currentness-and-reuse safety property

**Id:** V04

**Candidate:** A new currentness-and-reuse safety property

**Parents:** [P023](../SOURCE_MAP.md#s-460b1f2b7104c948), [P048](../SOURCE_MAP.md#s-460b1f2b7104c948), [P050](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Ablation:** Unchanged theorem truth can survive loss of current build evidence. A changed application needs correspondence without invalidating earlier mathematics. Universal retirement adds no justified property.

**Failure witness:** C12 separates statement, proof and environment changes; C18 separates one-way implication and redundant conjunction.

**Subsumption:** Affected-scope currentness and component reuse already express R08.

**Decision:** NO_IRREDUCIBLE_NEW_PROPERTY_ADMITTED

## Tensions

<a id="1"></a>
### 1 — Expressiveness and automation

**Tension:** Expressiveness and automation

**Analysis:** Richer properties can increase annotation/proof burden; a tractable fragment can be the intended result.

**Properties:** [P009](../SOURCE_MAP.md#s-460b1f2b7104c948), [P018](../SOURCE_MAP.md#s-460b1f2b7104c948), [P028](../SOURCE_MAP.md#s-460b1f2b7104c948), [P042](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Decision:** Use a stronger language only when its extra distinctions affect the decision.

<a id="2"></a>
### 2 — Universal soundness and useful bug finding

**Tension:** Universal soundness and useful bug finding

**Analysis:** Overapproximation supports universal transfer but may warn spuriously; underapproximation can establish a concrete witness.

**Properties:** [P013](../SOURCE_MAP.md#s-460b1f2b7104c948), [P017](../SOURCE_MAP.md#s-460b1f2b7104c948), [P025](../SOURCE_MAP.md#s-460b1f2b7104c948), [P026](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Decision:** Judge each inference direction against the actual question.

<a id="3"></a>
### 3 — Local modularity and hidden interference

**Tension:** Local modularity and hidden interference

**Analysis:** Smaller proofs need valid interfaces, frames and environment reasoning.

**Properties:** [P010](../SOURCE_MAP.md#s-460b1f2b7104c948), [P011](../SOURCE_MAP.md#s-460b1f2b7104c948), [P012](../SOURCE_MAP.md#s-460b1f2b7104c948), [P029](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Decision:** A whole small model may be cheaper than an elaborate decomposition.

<a id="4"></a>
### 4 — Small trusted base and complete semantic chain

**Tension:** Small trusted base and complete semantic chain

**Analysis:** Certificate checkers can reduce search-tooltrust while leaving encoding/parsing/runtime assumptions.

**Properties:** [P022](../SOURCE_MAP.md#s-460b1f2b7104c948), [P024](../SOURCE_MAP.md#s-460b1f2b7104c948), [P034](../SOURCE_MAP.md#s-460b1f2b7104c948), [P035](../SOURCE_MAP.md#s-460b1f2b7104c948), [P047](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Decision:** Identify which boundary is reduced; do not count tools as independent guarantees.

<a id="5"></a>
### 5 — Stable proof statements and changing needs

**Tension:** Stable proof statements and changing needs

**Analysis:** Preserving a theorem can conflict with a legitimate requirement change; repairing scripts can hide weakening.

**Properties:** [P023](../SOURCE_MAP.md#s-460b1f2b7104c948), [P039](../SOURCE_MAP.md#s-460b1f2b7104c948), [P048](../SOURCE_MAP.md#s-460b1f2b7104c948), [P049](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Decision:** Review meaning and impacted uses rather than preserving green status at all costs.

<a id="6"></a>
### 6 — Early detection and operational disruption

**Tension:** Early detection and operational disruption

**Analysis:** Instrumentation/control can introduce overhead and false blocking; passive evidence can still be useful.

**Properties:** [P031](../SOURCE_MAP.md#s-460b1f2b7104c948), [P032](../SOURCE_MAP.md#s-460b1f2b7104c948), [P036](../SOURCE_MAP.md#s-460b1f2b7104c948), [P042](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Decision:** State role and actionauthority before assigning fail-closed duties.

<a id="7"></a>
### 7 — Reuse and context sensitivity

**Tension:** Reuse and context sensitivity

**Analysis:** A reusable verifiedcomponent may lower cost, but a newplatform/use can violate assumptions.

**Properties:** [P015](../SOURCE_MAP.md#s-460b1f2b7104c948), [P033](../SOURCE_MAP.md#s-460b1f2b7104c948), [P050](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Decision:** No-change is justified only for compatibleuses; no universal fullreproof.

<a id="8"></a>
### 8 — Powerful AI search and statement fidelity

**Tension:** Powerful AI search and statement fidelity

**Analysis:** Checked proofs may be reliable while translation remains mistaken; additional repair can increase cost without benefit.

**Properties:** [P001](../SOURCE_MAP.md#s-460b1f2b7104c948), [P020](../SOURCE_MAP.md#s-460b1f2b7104c948), [P021](../SOURCE_MAP.md#s-460b1f2b7104c948), [P040](../SOURCE_MAP.md#s-460b1f2b7104c948), [P049](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Decision:** Use matched baselines and independent semantic discriminators.
