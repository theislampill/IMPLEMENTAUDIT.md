> **Original scientific report, normalized for public reading.** Scientific source SHA-256 `0be00f7164600b45f742351f493a868e825193e25dec57730576996017e823bd`. Author-state and earlier review statements are dated source history; the [current account](../DRF-L3.md) and [original qualification identities](../QUALIFICATION_AND_REVIEW_BINDINGS.json) distinguish later accepted status. Acquisition and runtime identifiers are omitted; no new scientific execution is claimed.

# Discriminating author cases

Nineteen author-designed constructions. All were designed after exposure to the native lineage and relevant source arguments. They are neither held out nor independent replication. Some output fields are explicit scope disclosures or direct analytical deductions rather than values from a general prover. The saved script, expected/observed records and final selected-byte execution identify the actual computation.

The machine-readable [case results](../SOURCE_MAP.md#s-0d2a9b3aa4145692) retain every exact formal statement, expected output, observed output and scope limit. The [script](../SOURCE_MAP.md#s-be073f4151020da7) is the executed implementation. The [final script review](../SOURCE_MAP.md#s-41dd9d1049214903) and [selected-byte execution](../SOURCE_MAP.md#s-e84e31939fe3d790) identify actual actions; initial script/results remain in cases/history. No actual external solver, prover, compiler, model call or industrial artifact is run by this suite.

<a id="c01"></a>
## C01 — Pure finite theorem and unsupported deployment extension

The three-state cycle is exhaustively safe under its own relation. Adding a fourth reachable state changes the system and defeats the attempted deployment extension. The model-only theorem remains the positive control; no implementation correspondence was supplied or required for that theorem.

**Native ancestry:** [P004](../SOURCE_MAP.md#s-460b1f2b7104c948), [P015](../SOURCE_MAP.md#s-460b1f2b7104c948), [P016](../SOURCE_MAP.md#s-460b1f2b7104c948), [P036](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** Init={0}; Next={(0,1),(1,2),(2,0)}. Every reachable state satisfies 0<=s<=2.

**Expected:**
```json
{
  "model_reachable": [
    0,
    1,
    2
  ],
  "model_safe": true,
  "changed_reachable": [
    0,
    1,
    2,
    3
  ],
  "deployment_correspondence_supplied": false
}
```


**Observed:**
```json
{
  "model_reachable": [
    0,
    1,
    2
  ],
  "model_safe": true,
  "changed_reachable": [
    0,
    1,
    2,
    3
  ],
  "deployment_correspondence_supplied": false
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Accept the finite theorem. Refuse only the unsupported extension; no implementation bridge is needed for its model-only statement.

**Limits:** No deployment, target code or physical process was examined. Exhaustiveness is this three-state model only.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S001](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S009](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c02"></a>
## C02 — Wrong goal, legitimate narrow lemma and inconsistent application

Finite enumeration separates the true nonnegative-square lemma, a constant implementation satisfying a weak postcondition, failure of the intended square function and vacuous implication from an inconsistent antecedent. A deliberate narrow lemma is not a mistranslation or evidence of deception. The executed domain is the five integers from −2 through 2.

**Native ancestry:** [P001](../SOURCE_MAP.md#s-460b1f2b7104c948), [P002](../SOURCE_MAP.md#s-460b1f2b7104c948), [P020](../SOURCE_MAP.md#s-460b1f2b7104c948), [P039](../SOURCE_MAP.md#s-460b1f2b7104c948), [P049](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** Over integer domain[-2,2], x*x>=0 is a valid narrow lemma; y=0 also meets y>=0 but fails y=x*x.

**Expected:**
```json
{
  "narrow_lemma": true,
  "wrong_implementation_meets_weak_goal": true,
  "wrong_implementation_meets_intended_goal": false,
  "inconsistent_antecedent_witnesses": [],
  "vacuous_implication": true
}
```


**Observed:**
```json
{
  "narrow_lemma": true,
  "wrong_implementation_meets_weak_goal": true,
  "wrong_implementation_meets_intended_goal": false,
  "inconsistent_antecedent_witnesses": [],
  "vacuous_implication": true
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Truth, intended relevance, consistency, and deliberate fraud are distinct. Deliberately narrow correct lemmas remain admissible.

**Limits:** Finite enumeration is not an independently checked proof over every integer; nonnegativity over all integers also has a direct elementary argument. No deception intent is inferred.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S002](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S059](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S102](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c03"></a>
## C03 — Reachable invariant need not itself be inductive

The only reachable state is 0, so excluding state 2 is a true invariant. State 1 is included in that predicate but has a transition to 2, so the same predicate is not inductive. The stronger predicate selecting only 0 is inductive. A separate chain shows that safe samples do not prove all reachable states safe.

**Native ancestry:** [P005](../SOURCE_MAP.md#s-460b1f2b7104c948), [P006](../SOURCE_MAP.md#s-460b1f2b7104c948), [P016](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** States={0,1,2};Init={0};Next=0->0,1->2,2->2;P(s):s!=2. I(s):s=0 is a strengthening.

**Expected:**
```json
{
  "P_reachable_invariant": true,
  "P_inductive": false,
  "I_inductive": true,
  "sample_safe": true,
  "other_model_safe": false
}
```


**Observed:**
```json
{
  "P_reachable_invariant": true,
  "P_inductive": false,
  "I_inductive": true,
  "sample_safe": true,
  "other_model_safe": false
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Initiation/consecution is a sufficient proof rule; finite reachability or a stronger inductive invariant can establish a non-inductive reachable invariant.

**Limits:** This explicit finite relation settles only the example. A failed induction attempt need not refute reachable safety.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S001](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S003](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c04"></a>
## C04 — Safety, fairness and deadlines have different quantifiers

The repeating pending-state behavior is safe and non-progressing, with service continuously enabled but never taken; it violates weak fairness. A toggling behavior makes service enabled infinitely often without continuous enablement, distinguishing strong from weak fairness. Arbitrarily long finite delays before service show analytically why fairness supplies no fixed deadline; the script also evaluates three concrete delay examples.

**Native ancestry:** [P007](../SOURCE_MAP.md#s-460b1f2b7104c948), [P008](../SOURCE_MAP.md#s-460b1f2b7104c948), [P009](../SOURCE_MAP.md#s-460b1f2b7104c948), [P029](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** Pending state 0 permits stutter 0->0 or serve 0->1; state 1 self-loops. Service is continuously enabled on the perpetual-0 run, which weak fairness excludes.

**Expected:**
```json
{
  "perpetual_pending_safe": true,
  "perpetual_pending_eventually_serves": false,
  "perpetual_pending_weak_fair": false,
  "finite_delay_counterexamples": {
    "1": {
      "first_service": 3,
      "exceeds_deadline": true
    },
    "2": {
      "first_service": 4,
      "exceeds_deadline": true
    },
    "5": {
      "first_service": 7,
      "exceeds_deadline": true
    }
  },
  "toggle_enabling_can_starve_under_weak_fairness": true,
  "same_toggle_is_strong_fair": false
}
```


**Observed:**
```json
{
  "perpetual_pending_safe": true,
  "perpetual_pending_eventually_serves": false,
  "perpetual_pending_weak_fair": false,
  "finite_delay_counterexamples": {
    "1": {
      "first_service": 3,
      "exceeds_deadline": true
    },
    "2": {
      "first_service": 4,
      "exceeds_deadline": true
    },
    "5": {
      "first_service": 7,
      "exceeds_deadline": true
    }
  },
  "toggle_enabling_can_starve_under_weak_fairness": true,
  "same_toggle_is_strong_fair": false
}
```


**Result:** AS_PREDICTED

**Warranted inference:** State safety does not imply progress. Weak fairness rules out continuous starvation, supplies no fixed response bound, and differs from strong fairness.

**Limits:** Lasso predicates are evaluated for the explicitly repeating cycles, not by a generic temporal-logic checker. For toggle 0<->1, service is enabled only at 0, so weak fairness has a false antecedent; strong fairness excludes infinite enabled visits without service.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S006](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S086](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c05"></a>
## C05 — Abstraction directions and a valid partial claim

The exact sets make the inference direction visible: the over-approximation contains a spurious bad value, while the under-approximation supplies a real witness but misses another concrete value. Universal safety can transfer from the larger set to the concrete set. A lack of witnesses in the smaller set cannot establish universal concrete absence.

**Native ancestry:** [P013](../SOURCE_MAP.md#s-460b1f2b7104c948), [P017](../SOURCE_MAP.md#s-460b1f2b7104c948), [P026](../SOURCE_MAP.md#s-460b1f2b7104c948), [P045](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** Concrete reachable valuesC={0,2}; interval abstractionA={0,1,2}; underapproximationU={0}. Badvalue1.

**Expected:**
```json
{
  "C_subset_A": true,
  "U_subset_C": true,
  "abstract_bad1": true,
  "concrete_bad1": false,
  "under_has0": true,
  "under_absent2": true,
  "concrete_absent2": false,
  "abstract_proves_range": true
}
```


**Observed:**
```json
{
  "C_subset_A": true,
  "U_subset_C": true,
  "abstract_bad1": true,
  "concrete_bad1": false,
  "under_has0": true,
  "under_absent2": true,
  "concrete_absent2": false,
  "abstract_proves_range": true
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Overapproximate safety transfers in the universal direction; underapproximate existence and scoped absence are useful. Neither direction licenses its converse.

**Limits:** The set inclusions are explicit; this does not validate a production abstraction transformer. A parity refinement{0,2} eliminates the spurious witness here.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S005](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S061](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c06"></a>
## C06 — Bounded absence, full exhaustion and UNKNOWN

The actual breadth-first procedure finishes at depth two without a counterexample, finds the bad path at depth three, reports UNKNOWN under a one-expansion budget and completely exhausts a safe three-state cycle. The forced budget is not a measured wall-clock timeout or a call to an external solver.

**Native ancestry:** [P016](../SOURCE_MAP.md#s-460b1f2b7104c948), [P018](../SOURCE_MAP.md#s-460b1f2b7104c948), [P019](../SOURCE_MAP.md#s-460b1f2b7104c948), [P024](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** A four-state chain has badstate3; breadth-first bounded exploration atdepth2 cannot reach it. Three-statecycle is completely safe.

**Expected:**
```json
{
  "depth2": {
    "status": "BOUNDED_NO_COUNTEREXAMPLE",
    "path": null,
    "expansions": 2
  },
  "depth3": {
    "status": "COUNTEREXAMPLE",
    "path": [
      0,
      1,
      2,
      3
    ],
    "expansions": 3
  },
  "budget1": {
    "status": "UNKNOWN_RESOURCE_LIMIT",
    "path": null,
    "expansions": 1
  },
  "full_cycle": {
    "status": "FINITE_DOMAIN_SAFE",
    "path": null,
    "expansions": 3
  }
}
```


**Observed:**
```json
{
  "depth2": {
    "status": "BOUNDED_NO_COUNTEREXAMPLE",
    "path": null,
    "expansions": 2
  },
  "depth3": {
    "status": "COUNTEREXAMPLE",
    "path": [
      0,
      1,
      2,
      3
    ],
    "expansions": 3
  },
  "budget1": {
    "status": "UNKNOWN_RESOURCE_LIMIT",
    "path": null,
    "expansions": 1
  },
  "full_cycle": {
    "status": "FINITE_DOMAIN_SAFE",
    "path": null,
    "expansions": 3
  }
}
```


**Result:** AS_PREDICTED

**Warranted inference:** A completed bounded claim and completed finite-domain proof are valid at their scopes. Neither should be rejected merely for not proving an unbounded different domain.

**Limits:** The forced limit is an actual bounded budget, not an observed wall-clock timeout or solverUNKNOWN. Status distinctions are explicit.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S009](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S016](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S036](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c07"></a>
## C07 — Interface composition and guarded circularity

The producer guarantee x ≥ 0 does not imply the consumer assumption x > 0 on the explicit finite domain; x ≥ 1 repairs this interface. Two circular implications alone allow both propositions to be false. A separate base-and-step construction demonstrates a valid simultaneous-induction pattern, not a reimplementation of a general assume-guarantee theorem.

**Native ancestry:** [P010](../SOURCE_MAP.md#s-460b1f2b7104c948), [P011](../SOURCE_MAP.md#s-460b1f2b7104c948), [P012](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** Producerpostx>=0 on{0,1,2}; consumerprex>0. Post does not entail pre. Changingproducerpost tox>=1 closes this finite gap.

**Expected:**
```json
{
  "original_compatible": false,
  "repaired_compatible": true,
  "circular_boolean_counterexamples": [
    {
      "A": false,
      "B": false
    }
  ],
  "base_and_step_pair_preserves_true": true
}
```


**Observed:**
```json
{
  "original_compatible": false,
  "repaired_compatible": true,
  "circular_boolean_counterexamples": [
    {
      "A": false,
      "B": false
    }
  ],
  "base_and_step_pair_preserves_true": true
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Local contracts retain their local validity; system composition requires connecting premises. A cycle label alone does not distinguish sound from unsound compositional reasoning.

**Limits:** The simultaneous-induction example is not a reimplementation of Abadi–Lamport Theorem2. Its own base/step premises supply a transparent well-founded argument.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S002](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S048](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [N004](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c08"></a>
## C08 — Aliasing defeats a frame claim without separation

Updating one heap location preserves the framed value at a distinct location and changes it when the names alias. The same construction separates returning an integer from computing the intended increment. A stronger refinement can name that functional requirement; no production type checker or unsafe-language implementation was run.

**Native ancestry:** [P011](../SOURCE_MAP.md#s-460b1f2b7104c948), [P027](../SOURCE_MAP.md#s-460b1f2b7104c948), [P028](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** Write4toheapcellx; framedclaimheap[y]=3 remains true whenx!=yanddoesnotwhenx=y.

**Expected:**
```json
{
  "disjoint_frame_preserved": true,
  "aliased_frame_preserved": false,
  "constant_function_is_int": true,
  "constant_function_meets_increment": false,
  "refined_witness_at2": true
}
```


**Observed:**
```json
{
  "disjoint_frame_preserved": true,
  "aliased_frame_preserved": false,
  "constant_function_is_int": true,
  "constant_function_meets_increment": false,
  "refined_witness_at2": true
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Type guarantees and separation premises are valuable specific guarantees; neither implies unspecified functional correctness or arbitrary frame preservation.

**Limits:** No production type checker or unsafeRustcode was executed. A checked refinement/type theorem must still name its language semantics and unsafe boundary.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S048](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S049](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S046](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c09"></a>
## C09 — Witness, refutation certificate and shared wrong encoding

A satisfying assignment, a resolution refutation and complete truth-table enumeration give their stated formula-level results. A prematurely empty resolvent is rejected. Integer arithmetic and 8-bit wraparound disagree at 255 + 1, exposing a shared encoding risk. The two checking algorithms share Python and their input representation; they are not independent human validation or a verified kernel.

**Native ancestry:** [P022](../SOURCE_MAP.md#s-460b1f2b7104c948), [P024](../SOURCE_MAP.md#s-460b1f2b7104c948), [P035](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** CNF {x1, not x1 or x2, not x2} has a resolution refutation; a separate author-written truth-table algorithm checks all four assignments. Another CNF has witness x1=false, x2=true.

**Expected:**
```json
{
  "sat_witness_checked": true,
  "unsat_certificate_checked": true,
  "unsat_by_truth_table": true,
  "tampered_certificate_checked": false,
  "integer_increment_grows": true,
  "uint8_increment_grows": false
}
```


**Observed:**
```json
{
  "sat_witness_checked": true,
  "unsat_certificate_checked": true,
  "unsat_by_truth_table": true,
  "tampered_certificate_checked": false,
  "integer_increment_grows": true,
  "uint8_increment_grows": false
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Certificates reduce dependence on search but do not certify that the encoding represents the intended machine. Multiple solving routes sharing the encoding do not repair semantic omission.

**Limits:** The checker is small author code, not a verified trusted kernel, solverbenchmark or independent human assessment. Two algorithms here sharePython and the input encoding.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S097](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S108](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S109](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c10"></a>
## C10 — Passive detection, missing events and controlled intervention

The passive detector sees a dangerous event without preventing it. Filtering that event creates a clean observed trace while the actual trace remains unsafe. An explicitly controlled command channel permits a separate enforcement example. An acknowledgment is a positive finite co-safety witness. The late alarm uses constructed times 5 + 3 > 6, not measured instrumentation latency.

**Native ancestry:** [P031](../SOURCE_MAP.md#s-460b1f2b7104c948), [P032](../SOURCE_MAP.md#s-460b1f2b7104c948), [P036](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** Safety:noeventdanger. Fulltraceopen,danger,close violates; filteredtraceopen,close hidesviolation. Co-safety:eventuallyack admits positive finitewitnessack.

**Expected:**
```json
{
  "passive_detects": true,
  "passive_prevents": false,
  "missing_event_monitor_reports_no_observed_violation": true,
  "actual_safety": false,
  "controlled_output_safe": true,
  "cosafety_positive_witness": true,
  "safety_prefix_proves_all_future": false,
  "delayed_alarm_misses_deadline": true
}
```


**Observed:**
```json
{
  "passive_detects": true,
  "passive_prevents": false,
  "missing_event_monitor_reports_no_observed_violation": true,
  "actual_safety": false,
  "controlled_output_safe": true,
  "cosafety_positive_witness": true,
  "safety_prefix_proves_all_future": false,
  "delayed_alarm_misses_deadline": true
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Passive detection is a legitimate partial contribution. Positive runtime verdicts depend on property semantics; enforcement requires an actual controlled action path.

**Limits:** No external intervention or real instrumentation occurred. The separate late-event arithmetic fixes danger at time 5, reporting delay 3 and alarm deadline 6; it is a constructed deadline violation, not measured latency.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S066](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S068](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S099](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c11"></a>
## C11 — Semantic preservation, identity and unproved interfaces

A target behavior set containing only 1 is included in allowed source behaviors {0,1}; a target containing 2 is not. Different byte labels fail an identity check. Timing and hardware correspondence are explicitly unprovided premises, not empirically tested failures. No compiler or kernel build was executed.

**Native ancestry:** [P014](../SOURCE_MAP.md#s-460b1f2b7104c948), [P015](../SOURCE_MAP.md#s-460b1f2b7104c948), [P033](../SOURCE_MAP.md#s-460b1f2b7104c948), [P034](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** For observablevalue semantics, targetbehavior{1}subsetofallowedsource{0,1};target{2}isnot. A theorem aboutbytesAdoesnotidentifybytesB.

**Expected:**
```json
{
  "good_refinement": true,
  "bad_refinement": false,
  "build_identity_matches": false,
  "timing_correspondence_supplied": false,
  "hardware_correspondence_supplied": false
}
```


**Observed:**
```json
{
  "good_refinement": true,
  "bad_refinement": false,
  "build_identity_matches": false,
  "timing_correspondence_supplied": false,
  "hardware_correspondence_supplied": false
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Refinement may select permitted nondeterminism. Preserve the component result; its endpoint, observations and actual artifact identity limit application.

**Limits:** These are abstract behavior sets and byte labels; noCompCert/seL4 build was executed or inspected.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S093](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S094](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S110](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c12"></a>
## C12 — Proof maintenance versus theorem and environment change

Statement and proof-label hashes separate an unchanged theorem with different illustrative tactics from a weakened statement. A larger environment invalidates the old application's safety while leaving the earlier finite proposition unchanged. The strings are labels rather than executed Lean or Isabelle scripts, so this is not a tool-compatibility test.

**Native ancestry:** [P021](../SOURCE_MAP.md#s-460b1f2b7104c948), [P023](../SOURCE_MAP.md#s-460b1f2b7104c948), [P039](../SOURCE_MAP.md#s-460b1f2b7104c948), [P048](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** Unchanged theorem text can have two different proof scripts. WeakenedstatementTrue and enlargedruntimevalue3 are separatechanges.

**Expected:**
```json
{
  "same_statement_digest": true,
  "different_proof_digest": true,
  "weakened_statement_digest_same": false,
  "old_application_safe": true,
  "new_application_safe": false
}
```


**Observed:**
```json
{
  "same_statement_digest": true,
  "different_proof_digest": true,
  "weakened_statement_digest_same": false,
  "old_application_safe": true,
  "new_application_safe": false
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Currentness has separate statement, proof, tool, build and environment dimensions. Recheck affectedscope; retain unaffected historical mathematics.

**Limits:** The two strings are illustrative proof-script labels, not executedLean/Isabellescripts. Direct finite truth and identity checks do not establish toolreplaycompatibility.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S095](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S096](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S110](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c13"></a>
## C13 — Checked fixed statement versus faithful translation

Both formal translations retain p while the intended meaning is p ∧ q; agreement fails to detect the omission at p=true, q=false. A separate intended Boolean identity is checked at its full finite domain. An AI-origin label supplies no additional logical premise, and no actual model call or benchmark replication was performed.

**Native ancestry:** [P001](../SOURCE_MAP.md#s-460b1f2b7104c948), [P039](../SOURCE_MAP.md#s-460b1f2b7104c948), [P040](../SOURCE_MAP.md#s-460b1f2b7104c948), [P049](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** OriginalmeaningpANDq; two translation/roundtripformulasbothp. Equality offormaltranslations holdsbutdoesnotentailoriginalmeaning.

**Expected:**
```json
{
  "roundtrip_equivalence": true,
  "faithful_to_original": false,
  "counterexample": {
    "p": true,
    "q": false
  },
  "fixed_intended_boolean_identity": true,
  "benchmark_replication_executed": false
}
```


**Observed:**
```json
{
  "roundtrip_equivalence": true,
  "faithful_to_original": false,
  "counterexample": {
    "p": true,
    "q": false
  },
  "fixed_intended_boolean_identity": true,
  "benchmark_replication_executed": false
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Checked proof of afixedintendedstatement is admissible regardless of origin. Formalroundtrip agreementalone cannot establish semanticfidelity or empiricalbenchmarktransfer.

**Limits:** NoAIcall/proverbenchmarkwasrun. This author-produced finiteexample was exposed to therelevantpaper limitations, so itisnotheldoutvalidation.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S101](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S102](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S111](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c14"></a>
## C14 — Cheap complete method and no irreducible novelty

All four inputs of the stateless two-input XOR rule are checked. For that complete intended domain, an additional control is unnecessary. A duplicate truth table adds no logical restriction. The example does not establish a temporal or physical-hardware claim, and no practical cost measurement was taken.

**Native ancestry:** [P037](../SOURCE_MAP.md#s-460b1f2b7104c948), [P038](../SOURCE_MAP.md#s-460b1f2b7104c948), [P041](../SOURCE_MAP.md#s-460b1f2b7104c948), [P042](../SOURCE_MAP.md#s-460b1f2b7104c948), [P043](../SOURCE_MAP.md#s-460b1f2b7104c948), [P050](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** A2inputBooleancontrollerhas4inputrows. Truth-tablevalidationofXORiscompleteforitsstatedstatelessdomain.

**Expected:**
```json
{
  "all_input_rows": 4,
  "xor_equals_one_true": true,
  "no_added_control_adequate_for_stated_domain": true,
  "duplicate_changes_truth_set": false,
  "unmodeled_temporal_property_established": false
}
```


**Observed:**
```json
{
  "all_input_rows": 4,
  "xor_equals_one_true": true,
  "no_added_control_adequate_for_stated_domain": true,
  "duplicate_changes_truth_set": false,
  "unmodeled_temporal_property_established": false
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Acheapcompletecheckcanbeadequate. Repetitionorrenamingdoesnotestablishirreduciblenovelty. Continuingthecurrentpracticecanbethewarranteddecision.

**Limits:** Adequacyisconditionalontheexplicitstatelessrequirementandtrustedinputinterpretation;noclaimaboutphysicalhardware,costmeasurementorallcontrollers.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S015](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S016](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c15"></a>
## C15 — Trace refinement can break a non-downward-closed hyperproperty

The permissive finite relation exposes equal possible low-output sets for either secret. A refinement selecting the secret as output reduces the trace set but violates this particular possibilistic noninterference condition. A constant-output refinement preserves it. The example is neither probabilistic noninterference nor a claim that all hyperproperties fail under refinement.

**Native ancestry:** [P009](../SOURCE_MAP.md#s-460b1f2b7104c948), [P014](../SOURCE_MAP.md#s-460b1f2b7104c948), [P027](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** Possibilistic noninterference here means equalsets ofpossiblelowoutputs forhighinput0and1. Permissivemodelpermitsbothoutputsforeachinput.

**Expected:**
```json
{
  "permissive_noninterference": true,
  "leaky_noninterference": false,
  "leaky_is_trace_subset": true,
  "constant_noninterference": true,
  "every_leaky_output_is_boolean": true
}
```


**Observed:**
```json
{
  "permissive_noninterference": true,
  "leaky_noninterference": false,
  "leaky_is_trace_subset": true,
  "constant_noninterference": true,
  "every_leaky_output_is_boolean": true
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Specify the securityquantifiers; ordinarytracesubsetrefinementdoesnotpreservearbitraryhyperproperties. Hypersafety/downwardclosedcasesneedseparatetreatment.

**Limits:** This is a finitepossibilisticrelation,notprobabilisticorcryptographicnoninterference. Thecounterexampleisnotaclaimagainstallhyperpropertyrefinement.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S021](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c16"></a>
## C16 — Linearizability, serial order and progress

The enumerator checks complete finite register histories. A read of 1 after a completed write of 1 has a valid order; a stale read of 0 has none respecting real time, though an order exists when real time is ignored. The pending-operation observation is a separate semantic argument, not an implemented branch of this enumerator. Linearizability does not compel actual progress.

**Native ancestry:** [P029](../SOURCE_MAP.md#s-460b1f2b7104c948), [P030](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** Registerinitial0:write1completesbefore read. Read1islinearizable;read0hasasequentialorderingonlyifrealtimeorderisignored.

**Expected:**
```json
{
  "good_orders": [
    [
      "w",
      "r"
    ]
  ],
  "stale_realtime_orders": [],
  "stale_orders_ignoring_realtime": [
    [
      "r",
      "w"
    ]
  ],
  "pending_operation_forces_actual_return": false
}
```


**Observed:**
```json
{
  "good_orders": [
    [
      "w",
      "r"
    ]
  ],
  "stale_realtime_orders": [],
  "stale_orders_ignoring_realtime": [
    [
      "r",
      "w"
    ]
  ],
  "pending_operation_forces_actual_return": false
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Respectreal-timeorderforlinearizability; do notconflate thepropertyallowingaresponse with animplementationguaranteeingprogress.

**Limits:** Enumerationimplementscompletefinitehistoriesonly. Thependingexampleisaseparatesemanticargumentviadroppingpendingoperations,notpassedthroughthisenumerator.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S090](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S091](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c17"></a>
## C17 — Memory-model choice changes a concurrency result

The explicit sequentially consistent model has 13 reachable states and three outcome pairs. The FIFO store-buffer model has 34 states and adds the pair (0,0), with a saved witness. This establishes a difference between these two small semantics, not a hardware measurement or complete ISA, compiler or language-memory proof.

**Native ancestry:** [P003](../SOURCE_MAP.md#s-460b1f2b7104c948), [P013](../SOURCE_MAP.md#s-460b1f2b7104c948), [P029](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** Eachoftwothreadsstores1toitsownlocationthenloadstheotherlocation. AllSCinterleavingsareenumerated;anexplicitbufferedmodeladdsflushsteps.

**Expected:**
```json
{
  "SC_outcomes": [
    [
      0,
      1
    ],
    [
      1,
      0
    ],
    [
      1,
      1
    ]
  ],
  "buffered_outcomes": [
    [
      0,
      0
    ],
    [
      0,
      1
    ],
    [
      1,
      0
    ],
    [
      1,
      1
    ]
  ],
  "buffered_zero_witness_exists": true
}
```


**Observed:**
```json
{
  "SC_outcomes": [
    [
      0,
      1
    ],
    [
      1,
      0
    ],
    [
      1,
      1
    ]
  ],
  "buffered_outcomes": [
    [
      0,
      0
    ],
    [
      0,
      1
    ],
    [
      1,
      0
    ],
    [
      1,
      1
    ]
  ],
  "buffered_zero_witness_exists": true
}
```


**Auxiliary observation:**
```json
{
  "SC": {
    "outcomes": [
      [
        0,
        1
      ],
      [
        1,
        0
      ],
      [
        1,
        1
      ]
    ],
    "zero_zero_witness": null,
    "reachable_states": 13
  },
  "buffered": {
    "outcomes": [
      [
        0,
        0
      ],
      [
        0,
        1
      ],
      [
        1,
        0
      ],
      [
        1,
        1
      ]
    ],
    "zero_zero_witness": [
      "t0:store",
      "t0:load=0",
      "t1:store",
      "t1:load=0",
      "t0:flush",
      "t1:flush"
    ],
    "reachable_states": 34
  }
}
```


**Result:** AS_PREDICTED

**Warranted inference:** A proofunderone memorysemanticsdoesnotestablishitsconclusionunderadifferentone withoutacorrespondenceargument.

**Limits:** Finite operationaltoyhasonependingstoreperthreadandno compiler,tearing,fences,undefinedbehaviororcachemodel. Counterexamplewitnessisinauxiliaryresult.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S106](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [N011](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c18"></a>
## C18 — Typed relation direction, shared evidence and negative control

On the selected integer domain, 0 ≤ x ≤ 2 implies x ≤ 2, while the reverse fails at −1. Conjoining the two is equivalent to the stronger premise. The declared one-study/two-version example illustrates accounting, not a measured empirical dependence. Generic co-use supplies no logical connecting premise and no irreducible novelty.

**Native ancestry:** [P012](../SOURCE_MAP.md#s-460b1f2b7104c948), [P036](../SOURCE_MAP.md#s-460b1f2b7104c948), [P038](../SOURCE_MAP.md#s-460b1f2b7104c948), [P050](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** A:0<=x<=2 entailsB:x<=2 ondomain[-1,3];reversefailsat-1. ConjoiningAandBislogicallyequivalenttoA.

**Expected:**
```json
{
  "A_implies_B": true,
  "B_implies_A": false,
  "reverse_counterexamples": [
    -1
  ],
  "A_and_B_adds_truth_restriction": false,
  "versions": [
    "paper_v1",
    "paper_v3"
  ],
  "underlying_study_families": 1,
  "generic_couse_entailment_established": false
}
```


**Observed:**
```json
{
  "A_implies_B": true,
  "B_implies_A": false,
  "reverse_counterexamples": [
    -1
  ],
  "A_and_B_adds_truth_restriction": false,
  "versions": [
    "paper_v1",
    "paper_v3"
  ],
  "underlying_study_families": 1,
  "generic_couse_entailment_established": false
}
```


**Result:** AS_PREDICTED

**Warranted inference:** Test eachdirection andconnectingpremise. Usefulpartialrelationsandnonewnovelty remain admissible; sharedsourcefamiliesareexplicit.

**Limits:** Logicalredundancydiffersfrompracticalcostandepistemicindependence. Study-familyexampleisa declaredaccountingconstruction,notanempiricaldependenceestimate.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S102](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S111](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).

<a id="c19"></a>
## C19 — Declared analyzer escape and a concrete missed violation

The deliberately constructed analyzer skips an explicitly marked path containing value 3. Its analyzed subset is safe while full enumeration finds the violation. This declared escape is distinct from an implementation defect violating a tool's claimed semantics. The external solver-fuzzing study is cited documentary evidence, not reproduced by this toy.

**Native ancestry:** [P024](../SOURCE_MAP.md#s-460b1f2b7104c948), [P026](../SOURCE_MAP.md#s-460b1f2b7104c948), [P027](../SOURCE_MAP.md#s-460b1f2b7104c948), [P047](../SOURCE_MAP.md#s-460b1f2b7104c948).

**Formal statement and scope:** A toy analyzer checks values <= 2 but explicitly skips the unsafe_escape path. The full finite program has values 0 and 3.

**Expected:**
```json
{
  "analyzed_subset_safe": true,
  "complete_domain_safe": false,
  "skipped_paths": [
    "unsafe_escape"
  ],
  "counterexample": {
    "path": "unsafe_escape",
    "value": 3
  }
}
```


**Observed:**
```json
{
  "analyzed_subset_safe": true,
  "complete_domain_safe": false,
  "skipped_paths": [
    "unsafe_escape"
  ],
  "counterexample": {
    "path": "unsafe_escape",
    "value": 3
  }
}
```


**Result:** AS_PREDICTED

**Warranted inference:** A declared unsound escape limits the advertised domain even if the checked subset is sound. A tool implementation defect is a separate evidence question.

**Limits:** This is deliberately constructed analyzer code, not a discovered defect in a production analyzer. The S097 study is external documentary evidence, not reproduced here.

**Design origin:** Fresh author construction after reading native lineage and primary sources; not held out.

**Execution class:** LOCAL_FINITE_CONSTRUCTION_OR_DIRECT_FINITE_DERIVATION

**Independent review:** NOT_PERFORMED_BY_THIS_AUTHOR

**Source context, not a claim of artifact replication:** [S005](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S046](../SOURCE_MAP.md#s-ef8b5e90ae1cf427), [S097](../SOURCE_MAP.md#s-ef8b5e90ae1cf427).
