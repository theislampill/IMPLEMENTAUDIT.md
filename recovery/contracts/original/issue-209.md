# R0035 (legacy R53): Dependency-correct work-conserving DAG execution — closed frontier, required JOIN, currentness and single-writer authority

LAB_GRADE_DRAFT=YES
RXX_SUBJECT=R0035
CONTROLLER_AT_DRAFT=v0333-release
RUN_ROOT_AT_DRAFT=v0400-s3e-release-controller-KYxl3h
CONTINUITY_AT_DRAFT=e60
WORK_ORDER_DEPTH_ANDON=ACTIVE
PUBLICATION=FORBIDDEN
SOURCE_MUTATION_AUTHORIZED=NO
EXTERNAL_MUTATION_AUTHORIZED=NO
FUTURE_SOURCE_MUTATION_BLOCKED_UNTIL_EXACT_R53_PUBLICATION_READBACK=YES

## Classification and bounded decision

R0035 owns one new first-class v0.4 control-architecture contract: for a declared
finite work population, `/implementaudit` must derive a complete and current
dependency graph, expose a closed `DONE + ACTIVE + READY + BLOCKED`
partition, dispatch only genuinely independent READY cells within bounded
capacity, preserve one semantic writer for each shared owner, wait for every
named required JOIN, reject incomplete or stale results, and recompute before a
dependent conclusion or mutation proceeds.

JOIN/currentness/single-writer predicates remain merged into R0035. They are
consequential graph-edge and transition controls. They do not form another
public subsystem, another lifecycle, another skill, or another RXX.

```text
NEW_RXX_REQUIRED=YES
CURRENT_IMPLEMENTATION_ALREADY_SATISFIES=PARTIAL_WITH_SUBSTANTIAL_R34_SCHEDULING_EVIDENCE
SOURCE_RUNTIME_DELTA_REQUIRED=UNDECIDED_UNTIL_FUTURE_EXACT_ACCEPTANCE
ACCEPTANCE_TEST_DELTA_REQUIRED=LIKELY_BUT_MUST_BE_REANCHORED
PACKAGE_DELTA_REQUIRED=ONLY_IF_PACKAGED_RUNTIME_BYTES_CHANGE
ACCEPTANCE_QUALIFICATION_REQUIRED=YES
```

This work order does not infer source RED from the existence of a new RXX or
from the absence of an R53-named checker. A first-class architecture owner can
be new while its component behavior is already partly or wholly present. Only
a preserved, predicate-specific failure against the future exact candidate can
admit a runtime repair.

## Authority and final topology that R0035 must preserve

The final v0.4 topology is fixed for this work order:

```text
PUBLIC_DEFAULT_GOVERNOR=/implementaudit
CHILD_SKILLS=audit-state,audit-assess,audit-implement,audit-andon
CHILD_SKILL_COUNT=4
INTERNAL_ONLY_CHILDREN=audit-state,audit-assess,audit-implement
DUAL_ENTRY_CHILD=audit-andon
ANDON_RESPONSE_OWNER=one shared bounded cognitive contract with governed L4 and explicit direct envelopes
H4_SHARED_DIRECT_AND_GOVERNED_ANDON=ACCEPTED_UPSTREAM_ARCHITECTURE
```

Historical W04 source evidence still contains `audit-hqyqh`; later packet
adjudication selected `audit-implement` and retained the physical rename as
downstream source work. That historical checkout is evidence of what was
inspected, not authority to restore the old name. R0035 owns neither that rename
nor internal-skill population changes. If a future R0035 executor finds the
final topology unresolved in the candidate, it must stop and route the upstream
topology prerequisite; it must not repair topology under the DAG issue.

The post-N7Y Andon investigation is also closed for this draft. H1—a narrow,
progressively loaded governor reference—is retained only as the historical and
retirement comparator; it is not the current governed route. H2 was dominated
and H3 duplicated the semantic owner. A corrected matched V1
review established that even an explicit diagnosis-only request through the
broad governor expanded into live campaign context, while the direct envelope
remained evidence-bounded. H4 therefore establishes `audit-andon` as the fourth
governor child, uniquely with an additional direct entrypoint. Its governed use
is `L4 -> audit-andon -> L4/governor`. R0035 neither creates nor owns that
capability, does not make it a DAG node, and does not substitute an alternate
reference route for the governor/L4-owned child route.

Publication, issue allocation, source changes, commit, push, merge, package
release, hosted mutation, public readback, tracker action and closure remain
separately authorized effects. This draft authorizes none of them.

## Historical evidence identity versus future execution identity

The following identities bind the evidence used to write this work order. They
are historical work-order-freeze inputs, not the candidate a future executor
may modify or qualify:

- W04 checkout at inspection: commit
  `e75a50743e5111a655fddd3c64f331a8df26d682`, HEAD tree
  `b9a0a499fb5d35c3fd87044c91151073d9d0d4b1`, with 26 modified and five
  untracked paths. A dirty working tree has no single derived tree identity.
- Prior R53 draft: 5,271 UTF-8 bytes, SHA-256
  `077b1862908861758e2f5d6b9c2fcf86badb4594da26557997753d6409dddf8b`.
- Work-order depth baseline: 14,475 bytes, SHA-256
  `d84f245b81c9893c5d64d8a66527142e8c67e1a4f95d689aa7b1b42231652d20`.
- Canonical 658-row crosswalk: 36,194,594 bytes, SHA-256
  `9b8e088094c208cf07601ca0f44c66c8062364055b82c976d66043de5b7ce7be`.
- Population adjudication: 28,763 bytes, SHA-256
  `aa0f61670d972c4f075e93b35549e18bc85835113f4668f4c4e861906a240319`.
- Genealogy adjudication: 8,695 bytes, SHA-256
  `957baff13e115b1dfe13a5d63a878e4b79bcbfb913dc43ab96674cf8d4e220e8`.
- Final post-N7Y Andon reconciliation: 5,335 bytes, SHA-256
  `af847ead0e000e683ce7a21cae6a496e309af62c744594019629d7a930a3b84e`.

The future executor must not check out, reset to, or claim qualification on
those identities merely because they appear here. It must acquire a new exact
repository/candidate/package/install/host identity at execution time, preserve
the historical identities as ancestry, and invalidate only evidence affected
by observed drift.

## Observed problem and weakest supported cause

W04 already contains substantial component controls:

- `skills/implementaudit/references/child-agents.md` defines a materially
  decomposable ready-cell frontier, dependency/read/write/acceptance/resource/
  authority boundaries, the serial cheap path, material transition triggers,
  a closed `DONE + ACTIVE + READY + BLOCKED` population, deterministic
  capacity/free/dispatch arithmetic, bounded WIP, unknown/stale refusal and a
  named join point.
- `scripts/check-action-selection-contract.sh` mechanically evaluates topology,
  scheduling and frontier-accounting cases. It distinguishes disjoint cells,
  shared owners, conflict serialization, current authorization, open authority
  boundaries, operator ceilings, unknown independence, material drift,
  recomputation and exact dispatch cardinality.
- `tests/action-selection-contract.test.sh` preserves mutation negatives for
  missing reconciliation, false work-conserving activation, unknown
  independence, cheap serial execution, reminder redispatch, open authority,
  stale/unknown population, recomputation, occupied-capacity arithmetic and
  deterministic-tool ownership.
- `scripts/check-fanout-coverage-contract.sh` and
  `tests/fanout-coverage-contract.test.sh` protect specialist-lane coverage,
  non-authority, serial fallback, no silent lane drop, prompt contract and
  independence against seeded false diversity.

Those controls show real implementation progress. They do not yet establish
the complete R0035 composition on one exact candidate. In the inspected focused
owners, the only direct JOIN contract is “Keep the named join point.” The
focused checker/test surfaces do not explicitly discriminate all of these
states as one contract:

1. the READY count is correct but one required JOIN result is absent;
2. a result was valid when produced but its graph/source/evidence/currentness
   identity changed before consumption;
3. two concurrently ready cells share one semantic writer despite distinct
   lane labels or files;
4. a JOIN completed but the governor consumed it without normalizing the
   result population and recomputing the frontier;
5. a transport success envelope contains a non-verdict or incomplete result;
6. a parent counts correlated or duplicate evidence as independent JOIN input.

The missing first-class contract is therefore not “a DAG does not exist.” It
is the lack of one accepted closed-frontier → bounded dispatch → required JOIN
→ normalized/current result → single-writer commit → recompute postcondition.
The weakest supported cause is distributed ownership: R0022 scheduling,
child-agent lane execution, currentness/fencing, effect authority and evidence
independence are locally strong, but no current accepted RXX owns their complete
decision-consumed transition.

## Semantic centre and complete mechanism

### Trigger

Activate R0035 when a governed run has at least three material cells or otherwise
has a consequential dependency, JOIN, writer, resource, authority, stale-result
or partial-failure relation whose treatment can change dispatch or acceptance.
Material cells may be implementation, research, verification, review,
documentation, package, hosted, publication or acceptance work.

### Non-trigger and cheap path

Use the serial cheap path for fewer than three material units, one READY cell, a
strict dependency chain, host capacity below two, operator ceiling zero/one,
unknown independence, unresolved authority, irreversible external effects, or
when dispatch and reconciliation cost exceeds expected engineering or
information value. Do not create a queue artifact, dashboard, mandatory child
lane, minimum agent count, utilization target, graph database, scheduler
service, or R0035 worksheet for that path. Serial execution still rechecks drift
and currentness before consuming results.

### Required graph input

Before dispatch, the governor must be able to reconstruct, from current
evidence, for every cell:

- stable cell identity and declared population membership;
- state: exactly one of `DONE`, `ACTIVE`, `READY`, or `BLOCKED`;
- named predecessor and JOIN dependencies;
- read set, write set and semantic owner;
- acceptance, resource and authority boundaries;
- reversibility/effect class and current authorization;
- required lane/result schema where execution is delegated;
- graph version or digest and the evidence identities from which it was
  derived; and
- final-composed-only status where local completion cannot establish the
  consumer claim.

The partition must conserve the declared population. Unknown, duplicate,
missing or stale state is not silently relabeled `BLOCKED` or omitted to create
free capacity.

### Dispatch calculation

Use deterministic tooling for cardinality and occupancy:

```text
DONE + ACTIVE + READY + BLOCKED = declared population
capacity = 0 when operator ceiling is 0
capacity = host capacity when no positive ceiling is supplied
capacity = min(host capacity, positive operator ceiling) otherwise
free = max(0, capacity - ACTIVE)
dispatch = min(eligible READY, free)
```

`eligible READY` excludes cells with unresolved dependency, independence,
write, acceptance, resource, authority, reversibility or currentness
boundaries. Work-conserving means no safe, useful and genuinely READY cell is
left idle when value exceeds coordination cost. It does not mean maximum
utilization, speculative fanout, zero slack or spending every available slot.

### Lane envelope

When a READY cell is executed by a child agent, specialist or serialized
fresh-context pass, the parent supplies a bounded lane identity, question,
owner/source, read/write scope, authority fence, tools, evidence boundary,
expected output, stop conditions and cleanup/resource identity. The lane is an
executor of one cell, not the definition of the graph and not an authority.
Transport completion, PASS-like prose, reviewer count or arrival order cannot
satisfy the cell.

### Required JOIN envelope

Every consequential JOIN must name:

- `join_id` and consuming cell/conclusion;
- exact required predecessor cell and lane IDs;
- expected result schema and terminal/nonterminal statuses;
- graph version/digest at dispatch and at consumption;
- source, evidence and candidate identities;
- independence/common-dependency classification;
- semantic owner and the sole writer allowed after the JOIN;
- policy for `PARTIAL`, `UNKNOWN`, `NONVERDICT`, transport failure and omitted
  results; and
- the transition whose completion forces recomputation.

A JOIN is satisfied only when its required population is complete, each result
is normalized, current and decision-usable, and the parent has re-read the live
owner/source needed to consume it. An optional lane may be absent only when the
graph declared it optional before dispatch and the resulting evidence ceiling
remains explicit. A required lane cannot disappear through retry, serialization
or transport substitution.

### Single-writer commit and recomputation

Disjoint preimages may execute concurrently. Mutations over one semantic owner,
registry, package graph, generated projection, issue body, public surface or
acceptance authority serialize through one writer. Different files do not make
two cells independent when they change the same semantic owner or acceptance
decision.

After completion, blockage, JOIN, capacity change, owner/source drift,
authorization change, conflict discovery, scope change, package/currentness
change or evidence that changes topology, the governor must:

1. fence or reject results bound to superseded graph/evidence identity;
2. normalize completed, partial, non-verdict and failed lane results;
3. re-read affected owner/source and reconcile authority;
4. update the closed population without inferring other `ACTIVE=0`;
5. recompute dependencies, JOINs, conflicts, capacity and READY eligibility;
6. consume or commit only through the sole current semantic writer; and
7. expose the new frontier before any further dispatch.

An unchanged reminder or status message is not a transition and does not
redispatch work. Evidence-responsive replanning may alter future cells only
when new evidence changes dependency, scope, risk, authority, acceptance or
value. It must preserve completed evidence and cannot widen authorization.

## Boundary map: what R0035 is and is not

### R0035 versus child-agent orchestration

R0035 decides which cells are currently eligible, which may overlap, what must
JOIN, which writer may commit and when the graph must be recomputed. The
child-agent contract decides how an eligible bounded lane is prompted,
executed, fenced, normalized and returned under parent custody. A perfectly
formed child lane can still be prematurely scheduled or consumed without its
required JOIN; a correct DAG can still dispatch a defective lane. These are
independently failing contracts. R0036 owns the complete child-agent contract.

### R0035 versus internal skills

`audit-state`, `audit-assess`, and `audit-implement` are internal-only,
governor-routed cognitive capabilities. They are not DAG cells, workers,
parallel lanes, lifecycle stages, evidence authorities or JOIN owners merely
because the governor may invoke one while reasoning about a cell. At most one
internal child is routed per governor derivation, it returns to the governor,
and the governor re-derives before another route. No child can establish READY,
mutation authority, PASS, release, closure or `AUDIT_COMPLETE`.

### R0035 versus L1–L5

L1 Planner, L2 Run, L3 Phase, interrupting L4 Andon and converging L5 Audit-fix
are nested control loops. They are not the cell population and their labels are
not skill or agent counts. R0035 may schedule work inside or across a loop only
without changing loop authority. L4 can interrupt any active cell, register and
contain the abnormality, fence affected results and force recomputation. For a
non-trivial Andon, L4/governor may route `audit-andon` through the governed
envelope and receive the result back to L4/governor before re-derivation; cheap
deterministic Andons bypass cognition. L5 closure still requires all obligations
terminal and cannot be replaced by a green JOIN or child result.

### R0035 versus deterministic and public surfaces

Deterministic tools establish population arithmetic, schema, identity,
currentness and mechanically checkable transitions. They do not decide
semantic independence or grant lifecycle authority. Source, generated, built,
packaged, installed, discovered, routed, activated, hosted, public and
cross-repository states remain distinct. A source/checker PASS cannot promote
an unproved installed, hosted or public leg.

## Genealogy, convergence and non-duplication

R0035 derives from and composes R0002, R0003, R0008, R0009, R000A, R000E, R0013, R001F, R0022,
R0024, R002D, R002E, R002F, R0030, R0031 and R0032. The decisive nearest owners are:

- R0002: verification-window freeze and invalidation after live-surface change;
- R0003: landed mutation postconditions and generated/identity discipline;
- R001F: receiver-reconstructible executor work and exact scope/acceptance;
- R0022: closed frontier, capacity, proportionality, cheap path and conflict
  serialization;
- R0024: observed-state mutation and effect authority;
- R002D: cross-boundary integration/readiness, current interfaces and one writer
  per native owner;
- R0030: stale/fenced result and changed-authority handling;
- R0031: partial/unknown outcomes, correlated failure, restoration and recovery
  capacity;
- R0032: temporal/property/currentness partition and weakest-leg evidence; and
- R002A/R002B: collision/common-dependency, decision-linked evidence,
  independence, stopping and anti-gaming discipline.

R0022 does not already own R0035: it owns the narrower frontier/capacity family.
R0036 does not own R0035: it owns lane execution. R0037 does not own R0035: it owns
nested loop composition. R002D remains valid architecture ancestry and component
integration evidence, not the complete dedicated DAG/JOIN contract.

### Canonical 658-row research support

The crosswalk contains 55 explicit `ARC_DAG_PARALLELISM` relations: 45
positive convergent supports, nine negative/anti-ceremony boundaries and one
domain/scope constraint. It contains 40 explicit
`ARC_JOIN_WRITER_AUTHORITY` relations: 38 positive supports and two
tension/unresolved constraints. These counts are index aids, not independent
proof and not a substitute for the exact rows.

The material convergences are:

- Cognitive and Safety: transition/pending obligation visibility, workload and
  reserve capacity, temporal guards, stop/handoff authority, independent
  evidence and lifecycle-transition control (`ECSE-08`, `ECSE-21`,
  `ECSE-36`, `ESS-011`, `ESS-017`, `ESS-025`, `ESS-054`).
- Systems and Decision/Operations: change-impact propagation, integration
  readiness, real precedence/resource/acceptance conflicts, bounded queues,
  admission, capacity reserve, schedule recomputation and switching-cost-aware
  replanning (`P028`, `P031`, Decision/Operations `P021`, `P023`–`P034`).
- Distributed and Reliability: minimal coordination for non-confluent
  invariants, bounded queues/backpressure, fencing, one-writer cheap path,
  acknowledgement versus effect, durable completion, failover authority,
  current topology, common cause, containment and recovery headroom
  (`P02`, `P13`–`P16`, `P21`, `P27`, `P29`–`P34`, `P37`, `P40`, `P41`,
  `ERM-P008`, `ERM-P010`, `ERM-P016`, `ERM-P029`, `ERM-P034`, `ERM-P036`).
- Formal V&V: explicit fairness/scheduler assumptions, local ownership and
  frame conditions, proof maintenance/currentness, concurrency model and
  linearizability/serializability/refinement boundaries (`P008`, `P011`,
  `P023`, `P029`, `P030`, `P032`).
- Lean/Agile/Waterfall: end-to-end flow, reversible increments, dependency and
  interface control, adaptive planning and multi-level integration, with
  explicit rejection of universal WIP, maximum utilization, zero slack and
  mandatory small batches (`EL-002`, `EL-004`, `EL-005`, `EL-008`, `EL-009`,
  `EL-034`, `EL-035`, `EA-04`, `EA-05`, `EA-13`, `EA-19`, `EA-25`,
  `EW-P009`, `EW-P011`, `EW-P023`).

The tensions constrain the mechanism rather than cancel it:

- more microstate/schedule visibility can itself be stale, noisy or costly;
- additional coordination, confirmation and assurance can create latency,
  role ambiguity, correlated ceremony and false confidence;
- nominally optimal schedules are fragile to duration/availability error;
- invariant protection and atomicity can conflict with availability/latency;
- queue pressure and maximum utilization can destroy recovery headroom;
- fail-safe containment can conflict with graceful degradation and local
  adaptation; and
- failure/recovery evidence may share a failed control plane, divergent clocks
  or contaminated artifacts.

Therefore R0035 requires only decision-changing graph detail, preserves UNKNOWN,
permits intentional idle time, records common dependencies, and retires the
control when its consumer/payoff disappears.

## Rejected alternatives and changed assumptions

1. **A DAG label or static dependency list is sufficient — rejected.** It can
   coexist with an open/unknown frontier, missed READY work, omitted JOIN,
   duplicate writer or stale result.
2. **R0022 alone is the complete owner — rejected.** Existing scheduling cases
   are strong but do not yet prove all required JOIN/currentness/writer
   negatives as one decision-consumed transition.
3. **Create a separate JOIN/writer RXX — rejected.** JOIN completeness,
   current-result acceptance and single-writer commit change the same DAG
   transition and source owner; splitting duplicates acceptance and writer
   custody.
4. **Put DAG authority in child-agent orchestration — rejected.** Agent
   machinery executes a lane; it cannot decide dependencies or promote its own
   result.
5. **Treat internal skills as workers or stages — rejected.** They are
   cross-cutting cognition under the sole governor and have no lifecycle,
   dispatch, mutation or closure authority.
6. **Add a scheduler service, dashboard or mandatory queue artifact — rejected.**
   The runtime is a governed procedure; existing deterministic fixture/checker
   owners can discriminate the contract without a new product subsystem.
7. **Maximum utilization or fixed parallelism is work-conserving — rejected.**
   Capacity is an upper bound, WIP is bounded by current occupancy, and slack
   may be protective.
8. **More reviewer/agent outputs create independent JOIN evidence — rejected.**
   Independence is about evidence/source/method/common cause, not count.
9. **Any absent R53-named test is source RED — rejected.** Missing acceptance
   coverage, missing runtime behavior and failed behavior are different states.
10. **Historical freeze identity is the future candidate — rejected.** The
    future executor must re-anchor live state and retain historical identity
    only as genealogy.

## Native owners and smallest future write set

The preferred future source owner remains
`skills/implementaudit/references/child-agents.md`, adjacent to
`### Work-conserving ready-cell frontier`. The preferred deterministic
acceptance owner remains the existing action-selection family:

- `fixtures/audit-action-selection/engineering-value-cases.json`;
- `scripts/check-action-selection-contract.sh`; and
- `tests/action-selection-contract.test.sh`.

The future executor should extend those surfaces only if the re-anchored owner
census confirms they remain canonical and the focused R0035 cases are not already
discriminated. A compact `dag_join`/equivalent case family inside the existing
checker is preferred over a new helper. A dedicated R0035 helper/fixture/test is
admissible only if the existing checker cannot express required JOIN population,
identity/currentness and one-writer semantics without materially obscuring its
current contract. Record that failure and an R001E applicability/reachability
decision before adding a helper.

By default, do not edit:

- `scripts/check-fanout-coverage-contract.sh` or its test merely to restate DAG
  authority; run them for R0036 no-regression;
- any internal child `SKILL.md`, child topology/routing test or package
  population to implement R0035;
- L1–L5, Andon, continuity, release, public or tracker owners unless a focused
  R0035 failure proves an exact collision; or
- package manifests, builders, installers or docs when only repository test
  coverage changes and packaged runtime bytes remain identical.

If the future owner/source has moved, a generated owner is mistaken for source,
or more than one current writer claims the same semantic contract, stop with
`owner-unclear` or `generated-artifact-mismatch`; do not force this historical
write set.

## Truthful source-delta decision procedure

### Smoke A: reacquire before adding a claim

On the future exact candidate, run the current canonical focused checks first:

```bash
bash scripts/check-action-selection-contract.sh
bash tests/action-selection-contract.test.sh
bash scripts/check-fanout-coverage-contract.sh
bash tests/fanout-coverage-contract.test.sh
bash tests/internal-skill-topology.test.sh
bash tests/internal-skill-routing.test.sh
```

Capture all pre-existing failures. A missing shell, wrong working directory,
syntax/setup failure, permissions error, timeout, transport failure or unrelated
baseline defect is not R0035 RED.

Then express each R0035 case against the current semantic owner without changing
its expected result to fit observed behavior. A new-file-missing failure proves
only that the acceptance artifact does not exist. Runtime/source RED requires a
current candidate that accepts a specifically invalid graph/JOIN/writer state
or cannot produce the required valid postcondition under the existing owner.

### Delta classification

- If all focused R0035 cases are already discriminated by current runtime owner
  and behavior, set `SOURCE_RUNTIME_DELTA_REQUIRED=NO`; add only the minimum
  durable acceptance registration needed to preserve the proof.
- If the runtime contract is semantically adequate but checker coverage is
  absent, set `SOURCE_RUNTIME_DELTA_REQUIRED=NO` and
  `ACCEPTANCE_TEST_DELTA_REQUIRED=YES`.
- If a preserved focused case is wrongly accepted by current owner/behavior,
  set `SOURCE_RUNTIME_DELTA_REQUIRED=YES` for the smallest owner-local clause
  and matching checker/test change.
- If evidence is inconclusive, identity is stale, or the owner is unresolved,
  set the state to `UNVERIFIED` or `BLOCKED`; do not infer RED.

Every changed expectation, oracle, threshold, fixture or graph schema after a
failure must preserve the original witness and obtain independent justification.

## Acceptance-inheritance matrix

| NEW_REQUIREMENT | EXISTING_OWNER(S) | EXISTING_ACCEPTANCE_INHERITED | ADDITIONAL_FAILURE_MODE | ADDITIONAL_DISCRIMINATOR | ADDITIONAL_ACCEPTANCE_BURDEN |
|---|---|---|---|---|---|
| Closed, current finite population before dispatch | R001F, R0022, R002D | Receiver-reconstructible scope; `DONE + ACTIVE + READY + BLOCKED` conservation; unknown/stale refusal | An omitted/duplicated/unknown cell creates apparent spare capacity while existing local cases remain green | Same population with one unknown or duplicated cell must produce reacquire/hold, not dispatch | R0035 case rows and mutation negatives only; no new queue artifact |
| Dependency-correct READY eligibility | R001F, R0022, R002D | Named dependencies, current dependency evidence, conflict/authority closure | A cell is marked READY before a required predecessor or authority boundary closes | Paired graphs differing only in predecessor/authority closure must diverge READY versus HOLD | One focused dependency/authority pair |
| Work-conserving bounded dispatch | R0022, R002F | Capacity/ceiling/free arithmetic, current occupancy, cheap serial path | Safe useful work is left idle, or spare ceiling dispatches more cells than READY/current WIP permits | Positive bounded dispatch plus missed-ready and overspend negatives | Reuse existing scheduling/frontier checker family |
| Required JOIN completeness | R001F, R0022, R002D, R0031 | Named reconciliation point, partial/non-verdict preservation, receiver completeness | READY count and lane execution are correct, but a required result is missing and dependent work proceeds | Identical result set with and without one required lane; only complete set may satisfy JOIN | Add explicit JOIN population/schema and one omission mutation |
| Result identity and currentness at consumption | R0002, R000E, R0024, R0030, R0032 | Verification freeze, evidence/candidate identity, stale-result fencing, weakest-leg currentness | Result was current at production but graph/source/evidence changed before consumption | Same result under matching versus superseded graph/evidence digest; stale arm must reject and preserve witness | One current/stale pair plus graph-drift held-out |
| One semantic writer after JOIN | R0003, R0022, R0024, R002D | Shared-owner conflict serialization, observed mutation authority, one native owner/writer | Two disjoint-looking cells concurrently commit to one semantic owner or registry | Same two lanes with disjoint versus shared semantic owner; shared arm serializes before dispatch/commit | Extend topology case with semantic-owner identity, not file-name proxy |
| Normalize partial, non-verdict and transport results | R0009, R0028, R0031, R0036 | Parent custody, report state, non-verdict not consumed, no silent lane drop | Success-shaped transport envelope or partial result is counted as terminal JOIN input | Terminal valid result versus `PARTIAL`, `UNKNOWN`, `REVIEWER_RUNTIME_NON_VERDICT`, error envelope | Reuse lane status vocabulary; no second report schema unless necessary |
| Recompute after JOIN/material transition | R0002, R0022, R002D, R0030 | Completion/blockage/drift/capacity/authority recomputation | JOIN completes, but stale frontier is consumed or old capacity is reused | Paired post-JOIN states differing only in recompute; no-recompute arm must hold | One mutation negative bound to exact graph version |
| Evidence independence at JOIN | R0023, R0028, R002A, R002B, R0036 | Prompt/evaluator independence, common-dependency accounting, anti-gaming | Duplicate/correlated lane outputs inflate required evidence while count is correct | Same cardinality with independent versus common-source duplicate results | One common-cause held-out; no reviewer-count threshold |
| Evidence-responsive replanning without authority widening | R001F, R0022, R0024, R002D | Current scope, owner/source, authorization and rollback boundaries | New evidence changes graph, but executor silently adds unauthorized work or discards completed evidence | Material dependency change may alter future frontier; non-material reminder must not redispatch or widen scope | Reuse drift/reminder controls plus one authorization-bound replan case |
| Serial cheap path and protective slack | R0022, R002A, R002B, R0031 | Fewer-than-three/one-ready/capacity-one path; proportional information value; recovery headroom | R0035 creates mandatory fanout/dashboard or treats full utilization as acceptance | One-cell and zero-ceiling cases pass without graph ceremony; max-utilization mutation fails | Negative source-token/behavior check only where stable |
| Orthogonality to child skills, child agents and L1–L5 | R002A, R0033, R0036, R0037 | Sole governor, exact four child skills, capability-specific entry policy, parent custody, loop authority, L4 interruptibility | Child PASS, direct cord pull, lane completion or green JOIN acquires READY/mutation/PASS/closure authority | Adjacent cases: child says PASS; direct audit-andon claims stop authority; L4 interrupts; lane correct but JOIN omitted; all retain caller/governor/loop authority | Run topology/routing/fanout/nested-loop regression owners; no R53-owned topology delta |

The matrix inherits only predicates that R0035 depends upon, strengthens or can
collide with. It does not import predecessor denominators or unrelated
implementation work.

## Discriminating acceptance family

The future acceptance artifact must use stable case IDs, exact expected
dispositions, distractors where model-facing evidence is used, and mutation
negatives that prove the oracle changes for the intended reason.

| Case | Class | Setup | Required observation |
|---|---|---|---|
| `R53-DAG-P01-CLOSED-JOINED-COMMIT` | positive | Current closed population; two independent READY preimages; complete named JOIN; one semantic writer | Bounded dispatch, complete normalized JOIN, sole-writer commit, then new frontier |
| `R53-DAG-P02-DISJOINT-CONCURRENT` | positive | Disjoint read/write/acceptance/resource/authority sets with one later composed consumer | Concurrent execution allowed; consumer remains blocked until named JOIN |
| `R53-DAG-N01-OMITTED-REQUIRED-JOIN` | negative | Correct READY/cardinality and terminal lane results except one required result absent | JOIN unsatisfied; dependent conclusion and mutation blocked |
| `R53-DAG-N02-STALE-AFTER-GRAPH-DRIFT` | negative | Result produced under graph/evidence version A; consumption attempted under B | Result fenced/rejected; occurrence preserved; affected frontier recomputed |
| `R53-DAG-N03-DUPLICATE-SEMANTIC-WRITER` | negative | Two lane/file identities, one semantic owner and overlapping acceptance | Serialize before dispatch/commit; no first-arrival authority |
| `R53-DAG-N04-NO-POST-JOIN-RECOMPUTE` | negative | Complete valid JOIN followed by direct consumption of old frontier | Hold with `RECOMPUTE_REQUIRED` or equivalent exact disposition |
| `R53-DAG-N05-SUCCESS-ENVELOPE-NONVERDICT` | negative | Transport success with partial/non-verdict/error metadata | Normalize as nonterminal; cannot satisfy JOIN or coverage |
| `R53-DAG-N06-CORRELATED-COUNT-INFLATION` | negative | Required cardinality met by duplicate/common-source evidence | Independence claim rejected or evidence ceiling reduced; no count-based PASS |
| `R53-DAG-N07-UNBOUNDED-FANOUT` | negative | READY exceeds free capacity or a positive operator ceiling | Dispatch bounded by current occupancy and ceiling; no silent cell drop |
| `R53-DAG-N08-UNKNOWN-LAUNDERED-BLOCKED` | negative | One UNKNOWN cell relabeled BLOCKED to close the population | Mutation negative fails; original state requires reacquire/serialize |
| `R53-DAG-B01-ZERO-CEILING` | boundary | Current READY cells with operator ceiling zero | Recompute allowed; dispatch remains zero |
| `R53-DAG-B02-ONE-CELL-CHEAP-PATH` | boundary | One READY cell, no consequential JOIN/conflict | Serial direct execution; no mandatory queue/dashboard/agent |
| `R53-DAG-B03-L4-INTERRUPT` | boundary | L4 Andon occurs while a lane is active | L4 stops/registers/contains; affected result is fenced; governor recomputes; no child authority |
| `R53-DAG-A01-AGENT-CORRECT-DAG-WRONG` | adjacent | Lane prompt/result fully satisfies R0036, but parent omits required JOIN | R0036 can pass while R0035 fails |
| `R53-DAG-A02-DAG-CORRECT-AGENT-WRONG` | adjacent | Graph is correct, but a warranted lane silently drops or returns generic prose | R0035 scheduling cannot promote defective R0036 execution |
| `R53-DAG-A03-INTERNAL-CHILD-PASS-LIKE` | adjacent | Internal child returns PASS-like or closure-shaped prose | Reject authority/closure; result returns to governor and cannot satisfy JOIN alone |
| `R53-DAG-H01-SAME-LABEL-DIFFERENT-DIGEST` | held-out | Cell/lane labels reused with changed graph/source/evidence bytes | Identity substitution rejected |
| `R53-DAG-H02-COMPLETION-PRESERVES-ACTIVE` | held-out | One cell completes while another remains ACTIVE | Recompute from observed census; do not infer all ACTIVE work vanished |
| `R53-DAG-H03-REMINDER-NO-REDISPATCH` | held-out | No material evidence/state/topology change | No redispatch and no new acceptance credit |
| `R53-DAG-H04-FINAL-COMPOSED-PARTIAL` | held-out | Useful increment completes while whole-target JOIN remains blocked | Preserve partial evidence; do not claim target acceptance |

For deterministic cases, the checker must derive the result from observations,
not trust the fixture's expected label. For any model-facing/installed cell,
the mission must omit `R53`, target property names, intended dispositions and
protected answer phrases; expected values, distractors, forbidden phrases,
package identity and evaluator identity remain fixed before execution. Do not
rerun merely to obtain green.

## Ordered future execution and DAG

### F0 — exact future re-anchor

1. Resolve the repository root and read the closest `AGENTS.override.md` and
   `AGENTS.md` chain.
2. Record branch, exact HEAD commit, HEAD tree, full dirty/untracked status,
   upstream relation and current controller/run-root authority. Do not clean,
   reset or adopt historical W04 state.
3. Re-read the current R0035 publication/allocation state. If R0035 remains
   unpublished, issue creation stays a separate owner-authorized gate and no
   source mutation becomes READY. If it is published, bind issue number, title,
   exact body bytes/hash, state and all normative additive comments by
   independent direct readback before source mutation.
4. Re-read current R0033/R0034/R0036/R0037 and R002A dispositions needed by this boundary.
   Verify exactly four child skills named `audit-state`, `audit-assess`,
   `audit-implement`, `audit-andon`; only `audit-andon` is directly invocable;
   accepted H4 governed/direct placement, sole governor and one atomic package.
   STOP on conflict.
5. Hash and inspect the current semantic owner, action-selection fixture/
   checker/test, fanout owners, internal topology/routing tests, package
   contract, validation registry and generated-source rules. Resolve whether
   this work order's preferred write set is still current.
6. Recompute the closed work population and bind every future cell to current
   owner/source, acceptance, write set, dependencies, effect class and rollback.

Required F0 outcome: one re-anchor receipt that separates historical identities
above from the exact future candidate and declares
`SOURCE_RUNTIME_DELTA_REQUIRED`, `ACCEPTANCE_TEST_DELTA_REQUIRED`, package
impact, owner/source and STOP conditions. Without it, no mutation is READY.

### F1 — current baseline and focused acceptance preimage

Run the six focused checks listed under Smoke A and record exact outputs. Add or
prepare the smallest R0035 case preimage without changing expected results after
observation. Prove whether each case is already discriminated. Preserve an
actual failing semantic witness before runtime repair. A test that fails only
because a new file/registration is absent is acceptance-artifact RED, not
runtime RED.

### F2 — smallest accepted owner delta

If runtime RED is established, add the minimum JOIN/currentness/single-writer
contract adjacent to the ready-cell frontier and the minimum deterministic
logic needed to derive the case dispositions. If runtime behavior is already
adequate, leave runtime source unchanged and add only accepted coverage. Keep
shared-writer edits serialized. Do not modify internal skill topology, Andon
placement or L1–L5 semantics.

### F3 — focused verification and adversarial mutations

Run every R0035 case plus mutation negatives that remove JOIN membership, alter
graph digest, reopen writer conflict, suppress recomputation, inflate evidence
count, overspend capacity and relabel UNKNOWN. Then rerun action-selection,
fanout, internal topology/routing, currentness/evidence and nested-loop focused
owners affected by the actual delta.

### F4 — package/install/activation only at the proved layer

If packaged runtime bytes changed, serialize the package writer; run the
canonical package gate, deterministic build, inventory/hash, isolated install
and archive-to-install parity for every claimed host route. Prove installed
discovery/activation separately where the R0035 runtime claim requires it. If
only repository tests changed and package bytes did not, record
`NOT_TRIGGERED_NO_PACKAGED_DELTA`; do not manufacture a package RED or install
claim.

### F5 — joined live corroboration and exact-tree review

Exercise one bounded governed run with at least two genuinely independent
cells, a named required JOIN, a shared-writer or stale-result boundary, and
post-transition recomputation. Bind the receipt to exact source/package/host
identity. This corroborates only the exercised contract. Then obtain a fresh
independent exact-tree cold review that does not reuse authoring context and
returns `PASS`, `GAP-REVISE`, `BLOCKED` or `OWNER DECISION` with exact identity.

### F6 — hosted/public/closure gates

Hosted CI, publication, issue comments, release, public projection, tracker
mutation and closure remain serial external effects requiring their own current
authorization. Post an exact evidence comment only after all applicable earlier
layers pass, independently read back its bytes/state/identity, and close R0035
manually only after terminal acceptance. A PR auto-close, issue creation
receipt, command success or elapsed timeout is not closure.

## No-regression contract, mechanism by mechanism

- **Sole governor and exact child population:** `/implementaudit` remains sole
  public/default governor; `audit-state`, `audit-assess`, `audit-implement` and
  `audit-andon` are its four children. Only `audit-andon` has a direct entry;
  direct invocation creates no peer governor. R0035 creates no skill or chain.
- **Progressive cognition:** at most one child per derivation, mandatory return
  and re-derivation remain. No child result establishes graph truth or closure.
- **Planning and execution:** planning/execution/repair remain governor-owned
  progressive references. A DAG cell does not create a lifecycle stage.
- **L1–L5 and Jidoka/Andon:** L4 can interrupt/fence/recompute; the shared
  cognitive contract is conditional and returns to L4/governor; explicit direct
  entry returns to the caller and creates no authority; cheap Andons stay
  deterministic; L5 retains final obligation closure.
- **Currentness, authority and effect:** R0002/R000E/R0024/R0030 evidence identity,
  fencing and landed-effect boundaries remain stronger than lane prose or JOIN
  cardinality.
- **R001E reachability and R0021 semantics:** any new helper or packaged reference
  proves applicability/reachability; package compaction cannot delete semantic
  safeguards.
- **R0023/R0028/R002B independence:** same-root, repeated-prompt or shared-source
  outputs do not become independent by count; evaluator/expected-result changes
  preserve original witnesses.
- **R0031 partial failure and recovery:** `PARTIAL`, `UNKNOWN`, non-verdict and
  transport states remain explicit; recovery closes only on required function
  and authoritative state.
- **Package/install/public:** source, generated, built, packaged, installed,
  discovered, routed, hosted and public identities remain separate. No weaker
  leg promotes a stronger claim.
- **Cheap path:** ordinary bounded work gains no mandatory graph artifact,
  agent, model call, review quota, dashboard, mode or utilization target.

## No-bloat, WIP and proof economy

R0035 earns a first-class RXX because the composed failure can occur while every
component owner is locally green and because one stable owner prevents repeated
JOIN/writer/currentness ambiguity across campaigns. It does not earn a new
runtime subsystem.

Cost is controlled as follows:

- discovery cost: no new public command, mode or internal skill;
- routing cost: the always-loaded governor keeps only the existing conditional
  route to the ready-frontier owner;
- context cost: add only the missing composed contract near existing frontier
  semantics; no research corpus enters runtime;
- WIP cost: dispatch is bounded by current READY cardinality, occupied capacity,
  operator ceiling, rollback margin and value; no minimum fanout;
- package cost: no package delta for test-only coverage; any runtime delta uses
  the existing package graph and budget owner;
- test cost: prefer one compact case family and existing checker over
  per-property tests or a 95-row runtime suite;
- documentation cost: no new dashboard, lifecycle, user guide or child docs
  unless shipped behavior creates a real consumer;
- maintenance cost: one semantic owner and one writer; related mutation
  negatives share an oracle without hiding distinct failure modes; and
- version-coherence cost: no independently versioned R0035 artifact or child.

The 55 DAG and 40 JOIN research relations guide selection; they do not create
95 implementation cells. Reuse deterministic source/schema checks for graph
arithmetic and identity, bounded behavioral evidence for governor judgment, one
live joined run for corroboration, and package/install evidence only if that
layer changed.

## Rollback, compensation, recombination and retirement

### Pre-publication and source rollback

Before publication, withhold the body or source candidate if any required gate
fails. Revert only the R53-specific owner clause, fixture/checker/test
registration and package projection actually added. Restore the prior package
from canonical source and verify no task-created generated, installed or ignored
residue remains. Never roll back pre-existing R0002/R0003/R001F/R0022/R0024/R0028/R002A/R002D/
R0030/R0031/R0032 behavior or historical failed evidence.

### Post-publication compensation

After separately authorized publication, preserve the original issue body and
history. Correct a defective work order or evidence claim through a separately
reviewed additive normative/superseding comment with independent readback.
Never silently rewrite or delete published evidence to make acceptance appear
green.

### Recombination

If a dedicated R0035 helper/test is introduced and later proves duplicative,
recombine its stable deterministic cases into the action-selection owner,
preserving case IDs, original failures, acceptance meaning and package
reachability. If JOIN/writer clauses drift into multiple owners, consolidate
one current semantic writer and leave references from dependent owners rather
than copy the contract.

### Retirement

Retire an R53-specific source clause/helper only when no live consequential
consumer remains or exact evidence shows that an existing owner completely and
more cheaply discriminates every R0035 failure. Retirement must retain the cheap
path, historical issue/evidence record and no-regression controls. H4 Andon
implementation/qualification, host concurrency changes or a new agent product
do not automatically retire or expand R0035; they retain their own genealogy and
collision review.

## STOP and Andon conditions

Stop and record the exact abnormality before proceeding when:

- final topology differs from exactly four children—`audit-state`,
  `audit-assess`, `audit-implement`, `audit-andon`—or audit-andon's unique
  direct-entry policy transfers governor/DAG authority;
- the future repository/candidate/issue/package identity cannot be established;
- current owner/source is ambiguous, generated or concurrently written;
- the work population cannot be closed or contains unknown/stale/duplicate
  cells;
- a required JOIN population or result identity is missing;
- shared semantic writers cannot be serialized;
- a failing command is setup/transport/policy noise rather than the named
  predicate;
- expected values, evaluator or graph schema are changed after failure without
  preserving and independently justifying the original;
- a source RED is inferred from new RXX status or missing test registration;
- a child/agent/loop/result is given governor, mutation, PASS or closure
  authority;
- package/install/host/public proof is promoted across an unproved layer;
- publication, commit, push, merge, release, public mutation or closure lacks
  separate current authorization; or
- independent review returns `GAP-REVISE`, `BLOCKED` or `OWNER DECISION`.

Use the current IMPLEMENTAUDIT Andon schema and class. Preserve distinct
partial/non-verdict results and the original failed witness; do not normalize
them into PASS.

## Terminal acceptance

R0035 is terminal only when all of the following are true on one future exact
candidate and no active Andon/handoff remains:

1. Current repository root, branch, commit, tree, full dirty state, controller,
   issue/body/comment identity and authority are mechanically re-anchored; the
   e60/W04 identities above remain historical only.
2. The current owner/source map is exact, and one semantic writer owns the DAG/
   JOIN contract. Generated/package/public surfaces point back to that owner.
3. Final topology remains exactly four child skills—`audit-state`,
   `audit-assess`, `audit-implement`, `audit-andon`—under the sole
   `/implementaudit` governor; audit-andon uniquely supports direct entry while
   remaining non-authoritative and never becoming a DAG node or peer governor.
4. `SOURCE_RUNTIME_DELTA_REQUIRED` and `ACCEPTANCE_TEST_DELTA_REQUIRED` have
   evidence-backed terminal values. No runtime RED was manufactured from a new
   RXX, missing file or absent registration.
5. The complete R0035 positive, negative, boundary, adjacent and held-out family
   passes, and mutation controls prove required JOIN, graph/result currentness,
   single-writer serialization, normalization, recomputation, bounded dispatch,
   common-dependency and cheap-path predicates.
6. Existing action-selection, fanout, internal topology/routing, currentness,
   authority/effect, nested-loop and closure gates affected by the actual delta
   pass without weakened expectations or erased failures.
7. If packaged runtime bytes changed, exact source→generated→built→packaged→
   isolated-installed parity, version/inventory, route and applicable host
   evidence pass. If they did not change, the package/installed leg is recorded
   as not triggered rather than falsely claimed.
8. One bounded governed live execution corroborates independent dispatch,
   required JOIN, a stale-result or shared-writer boundary, parent normalization
   and post-transition recomputation at the exact candidate identity.
9. Fresh independent exact-tree cold review passes with no authoring-context
   reuse, hosted CI passes where applicable, and every failed/non-verdict
   predecessor remains visible with its correct evidence ceiling.
10. Package, installed, hosted, public and cross-repository claims stop at the
    weakest proved leg; no source or local command receipt is promoted.
11. Any separately authorized R0035 issue body and implementation evidence comment
    are independently read back by exact identity/bytes/state after publication.
12. Manual issue closure occurs only after the evidence comment/readback and all
    accepted-RXX evidence joins before C08. Issue creation, PR merge, auto-close,
    elapsed time or a PASS-like child result is not terminal acceptance.

LAB_GRADE_DRAFT_STATUS=COMPLETE


<!-- implementaudit-v041-current-state-reconciliation -->
## v0.4.1 current-state reconciliation (2026-09-07)

This additive section supersedes stale current-status statements in the historical body; it does not rewrite accepted history or itself grant implementation, qualification, release, publication, tracker-closure, or native AthruK credit.

- Current semantic status: `ENGINEERING_REQUIRED`
- Current statement: Work-conserving transaction-scoped concurrency and partial JOINs must preserve logical-delivery, writer/effect, currentness and context-placement custody.
- Applicable accepted evidence: Narrow transaction/writer/dependency controls and Auto-LOOM schedule are reusable.
- Proof/authority limit: Cross-transaction logical-delivery identity and actual safe child overlap remain nonverdict; prompt-only read-only is not containment and no global mutex is permitted.
- AthruK relationship: `A, C, G, J, K`
- Auto-LOOM relationship: continuous result-to-JOIN-to-prepay-to-refill with context locality, governor/child context cost and return-compression value as placement inputs
- First remaining discriminator/prerequisite: Logical-delivery discriminator/repair, enforceable effect-capability admission, context-aware placement contract and exact final qualification.
- Next consumer/owner: `AUTO_DAG_AUTO_LOOM_OWNER`
- Release accounting: no release cell closes from this reconciliation; required remaining remains 26 plus conditional B-F3.
- Frozen proposal source: `sha256:baf4ab4600363cf3047664fea87971e593a423a55de0a2ab9df8c0d15235770c` (local run evidence; not public authority).


<!-- thread8-triad-integration-f4c2a199743d -->
### Bounded SSS x BWP x AMA integration input

Conceptual relations, co-change and shared eventual products are not hard execution edges. Preserve safe unrelated work while buffering actual dependent acceptance; meaningful JOIN and progress claims need joint state, resources and peer/environment assumptions.

[Reviewed source and issue crosswalk](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/0e175fe64cbd4846fbf8e06c8b2ede12295c514c/docs/research/implementaudit/triad-integration/ISSUE_ADJUDICATION.json); [draft integration PR](https://github.com/theislampill/IMPLEMENTAUDIT.md/pull/223). The isolated canonical package gate remains failed at the frozen identity-convergence gap. This note grants no governor admission, native authority-NONE, runtime/install/release qualification or issue closure. Existing owner and qualification obligations remain in force.
