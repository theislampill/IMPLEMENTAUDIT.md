# R53-DAG acceptance family mapped onto frozen 2450417a

**Authority: NONE.** This is a working map for the DG16 executor. It awards nothing.

* **Subject:** `2450417a3d442e189e20ba261120aff3ed7444c6`, tree `b14577983c5e0ab05225250491efe7363945742c`. The tree was asserted in the probe clone.
* **Source of the cases:** the "Discriminating acceptance family" table in `585012cb:recovery/contracts/original/issue-209.md`, plus its derivation rule and terminal criterion 5.
* **Machine-readable copy:** `R53_DAG_MAP.json`, in the same directory.

## Result

| Verdict | Count | Cases |
|---|---|---|
| COVERED | 13 | P01, P02, N01, N02, N04, N07, N08, B01, A03, H01, H02, H03, H04 |
| PARTIAL | 7 | N03, N05, N06, B02, B03, A01, A02 |
| MISSING | 0 | none |

**Model-facing or installed cells:** none. All 20 cases map to deterministic, constructed tests, so the mission-omission rule is NOT_TRIGGERED.

The absence of `R53-DAG-*` identifiers in 2450417a is not treated as a gap. Each PARTIAL below names a behaviour or discriminator that no test checks. Four of the seven are backed by a surviving in-memory mutant.

**Registration:**

* `tests/native-work-graph-cases.py`, `work-graph-completion-cases.py`, `work-graph-completion-transition-cases.py`, `work-graph-pending-settlement-cases.py` and `work-graph-operation-cases.py` all run from `tests/native-work-graph.test.sh`. That script is called at `scripts/verify-package.sh` L768.
* `tests/work-graph-compiler.test.sh` is called at L767.
* `tests/fanout-coverage-contract.test.sh` is called at L766.
* `tests/repo-state.test.sh` is in the same list.
* `tests/audit-andon-return-cases.py` and `tests/jidoka-andon-cases.py` are **not registered**. Their only references are in `handoff/` and `docs/`.

## Derivation check

The native route derives state from observation. It does not trust labels:

* Source documents may declare only `OPEN`, `ACTIVE` or `DONE` (`_native_validate_node`).
* `READY` and `BLOCKED`, the blocked reasons, `input_digest` and the population are computed by `_compile_native_documents_v1` from enumerated source bytes and re-read input files.
* Every consumer reseals and replays the graph (`_check_graph_seal` → `_replay_native_graph_v1`). Any relabel therefore fails with "source-derived" (`native-work-graph-cases.py` L479-484).
* Result evidence in the completion family is the hash of real subprocess output over the node's input files.
* `slot_capacity_controls` writes an `expected_selected` label into `observed.json`, but its assertions compare against the selection the compiler derives, so the label is not trusted.

Exceptions:

* The historical v1 projection (`compile_frontier_projection`) and the A/G route (`compile_native_a_g_v1`) take caller-declared states. The test keeps this deliberately: L416-420 asserts the historical v1 projection's limit instead of changing the oracle.
* `cheap_path_v1` is tested only on caller-supplied scalar counts (see B02).

## Per-case map

Line numbers refer to files at 2450417a. Abbreviations:

* **NWG** = `tests/native-work-graph-cases.py`
* **CMP** = `tests/work-graph-completion-cases.py`
* **TRN** = `tests/work-graph-completion-transition-cases.py`
* **PND** = `tests/work-graph-pending-settlement-cases.py`
* **OPS** = `tests/work-graph-operation-cases.py`
* **WGC** = `tests/work-graph-compiler.test.sh`

| Case | Verdict | Discriminating evidence | Mutation / negative control |
|---|---|---|---|
| P01 closed, joined, commit | COVERED | NWG L428-434 and L486-496 (closed population, derived READY); NWG L526-541 (bounded dispatch); NWG L606-615 (named JOIN satisfied, authority NONE); CMP L321-331 (one dispatch, two returns, JOIN); CMP L99-120 (JOIN, then the new frontier is NEXT); CMP L195-201 and L343-382 (single journal writer, one commit wins); TRN L69-89 | L615 (one result gives PENDING); L490 (omitted node refused); probe K6 KILLED |
| P02 disjoint concurrent | COVERED | NWG L433-434 and L526-530 (PREP and SIB co-selected, QUALIFY BLOCKED); NWG L543-556; CMP L99-109 (consumer held until the JOIN); TRN L157-173; WGC L2416-2473 | L545-549 (shared semantic write gives CONFLICT); L555-556 (path-prefix write) |
| N01 omitted required JOIN | COVERED | NWG L615, L721, L732, L746; CMP L101-105; PND L307-318 | L613 vs L615 pair; K6 KILLED in NWG, CMP and PND |
| N02 stale after drift | COVERED | NWG L620-622; NWG L671-676 (RECOMPUTE_REQUIRED, PREP invalidated, SIB preserved); NWG L742-745; CMP L135-142; PND L281-289 (pending history retained); TRN L227-233; OPS L175-184 | The same results are accepted at L613 and fenced at L674; K2 KILLED |
| N03 duplicate semantic writer | **PARTIAL** | NWG L543-563 (cross-file semantic owner serialized; an ACTIVE holder blocks); TRN L186-195; CMP L343-382; PND L431-445 (one arrival appends); WGC L2437-2473 (A/G blanket acceptance/authority block) | Writes arm is controlled. **M3 SURVIVED** (acceptance and authority dropped from the native overlap check) |
| N04 no post-JOIN recompute | COVERED | NWG L671-676; NWG L757-759; OPS L175-184 (CLI); CMP L195-199; CMP L107-109 | K2 KILLED |
| N05 success envelope, non-verdict | **PARTIAL** | NWG L623-629; CMP L166-177 (includes TRANSPORT_FAILURE, evidence digest present); PND L352-366 | K5 KILLED. **M2 SURVIVED** (exit 0 promotes any status to PASS) |
| N06 correlated count inflation | **PARTIAL** | NWG L630-664 (duplicate key, common read, transitive dependency, transitive read, optional source, plus a disjoint positive); CMP L253-261; CMP L307-319 | K3 and K4 KILLED. **M1 SURVIVED** (duplicate-evidence-digest arm dropped) |
| N07 unbounded fanout | COVERED | NWG L112-150 (12 slot cases); NWG L531-541; TRN L197-212 (deferred CAPACITY and CONTEXT_COST); CMP L281-305; WGC L2540-2546 | The slot grid; K1 KILLED |
| N08 UNKNOWN laundered as BLOCKED | COVERED | NWG L479-484 (relabel refused); NWG L447-458 and L486-496; PND L352-366 and L368-382; CMP L203-213 (PRODUCER_REOBSERVATION_REQUIRED); WGC L186-192 and L2350-2395 | Whole-graph replay makes the refusal direction-independent. Laundering is detectable on the native route only |
| B01 zero ceiling | COVERED | NWG L117 and L128-150; NWG L531-537; WGC L2420-2435 | K1 KILLED at the `zero-ceiling` case |
| B02 one-cell cheap path | **PARTIAL** | NWG L786-789 (`cheap_path_v1` scalars only); NWG L529 (GOVERNOR placement) | **M4 SURVIVED** (derived mode forced to GRAPH_CANDIDATE) |
| B03 L4 interrupt | **PARTIAL** | NWG L623-626; NWG L179-187; CMP L166-177; `tests/repo-state.test.sh` L292-306; `tests/audit-andon-return-cases.py` L37-82 (**unregistered**) | No test composes this case |
| A01 agent correct, DAG wrong | **PARTIAL** | NWG L611-615 and L746; NWG L713-721; `tests/fanout-coverage-contract.test.sh` L17-36 (R0036, separate fixtures) | R0035 arm: K6 KILLED |
| A02 DAG correct, agent wrong | **PARTIAL** | NWG L746 (silent drop refused); NWG L615; CMP L101-105; `tests/fanout-coverage-contract.test.sh` L87-90 (checks only that the fixture exists) | **M5 SURVIVED** (the no-decision-change refusal removed) |
| A03 internal child PASS-like | COVERED | NWG L613-615 and L665-667; CMP L307-319 (forged child PASS for the JOIN refused); CMP L154-164; TRN L69-89; PND L168-180; WGC L2367-2414 | L666 whole-parent scope refused; L317 forged JOIN refused |
| H01 same label, different digest | COVERED | NWG L303-319, L479-484, L733-745, L761-775; TRN L214-225; WGC L233-243 | Labels kept, bytes changed: all refused |
| H02 completion preserves ACTIVE | COVERED | NWG L179-187 and L121-126; PND L384-394; TRN L186-195 | Slot pair `active-zero-full` vs `active-zero-free` |
| H03 reminder, no redispatch | COVERED | NWG L284-339 and L757-759; CMP L272-279; TRN L265-277 | L321-337: changed input, context or event kind each reconsider |
| H04 final composed partial | COVERED | TRN L157-173, L299-310, L91-122; CMP L114-120; NWG L665-667 and L730-732 | Changed contributor keeps B retained and the JOIN BLOCKED |

## The seven genuine gaps

1. **N03, acceptance and authority overlap on the native route.**
   * No test gives two READY native nodes that overlap on `acceptance` (or `authority`) while their writes are disjoint.
   * Mutant M3 replaces `resources()` in `_bounded_selection_v1` so it returns only `cell['resources']`. It survives the native, completion, transition and pending families.
   * The A/G route only blocks any acceptance boundary that is not `NONE`, using caller-supplied facts. That is not overlap serialization.

2. **N05, transport-success envelope.**
   * Every non-PASS fixture carries `exit_code=None` (NWG `packet()` L201, CMP `result()` L87).
   * No case pairs `exit_code=0` with a PARTIAL, NONVERDICT, UNKNOWN, INTERRUPTED or error status.
   * Mutant M2 lets `exit_code==0` promote any status to PASS. It survives all four families.

3. **N06, duplicate evidence bytes.**
   * No case presents identical `evidence_digest` values under distinct independence keys with disjoint sources.
   * The reducer arm `None not in evidence and len(set(evidence)) != len(evidence)` is never exercised.
   * Mutant M1 survives all four families.

4. **B02, derived cheap path.**
   * `select_native_frontier_v1(...)['mode']` and `graph_required` are never asserted on an observed graph.
   * The case needs CHEAP_SERIAL on a one-READY graph, with GRAPH_CANDIDATE on the two-READY fixture as the control.
   * Only the scalar helper `cheap_path_v1` is tested.
   * Mutant M4 survives all four families.

5. **B03, L4 interrupt while a lane is ACTIVE.**
   * Native event kind `INTERRUPTION` (`compile-work-graph.py` L2776) appears in no test.
   * No test applies an L4 Andon while a lane is ACTIVE and then observes three things together: the affected late result fenced, a recomputed governor frontier, and no child authority.
   * Only separate pieces exist. The audit-andon return validator that covers the "no child authority" piece is unregistered.

6. **A01, adjacency pairing.**
   * No case records an R0036 PASS for a lane whose parent DAG omits the required JOIN.
   * The R0035 failing arm is exact. The claim "R0036 can pass while R0035 fails" is inferred from two disjoint tests.

7. **A02, the generic-prose or no-decision-change arm.**
   * The `consumer has no decision-changing return` refusal in `check_recursive_execution_v1` is never exercised.
   * Mutant M5 survives.
   * The R0036 negative fixtures `negative-silent-lane-drop.md` and `negative-generic-single-pass.md` are only checked for presence. They are never fed to the DAG.
   * The silent-drop arm is covered.

Terminal criterion 5 requires mutation controls for "normalization", "common-dependency" and "cheap-path predicates". These are not fully met:

* Normalization lacks the exit-0 envelope arm (gap 2).
* Common-dependency lacks the duplicate-evidence arm (gap 3).
* The cheap path lacks the derived mode (gap 4).
* Single-writer serialization is controlled only for writes (gap 1).

Required JOIN, currentness, recomputation and bounded dispatch each have a killed mutant.

## Commands and results (read-only)

All runs used a fresh WSL clone at `/home/agent/opus-tmp/r53map/run-20261125T022546/src`:

* The branch `engineering/sol-dg17-20261122` was cloned at depth 2, then the subject commit was fetched and checked out detached.
* The tree was asserted equal to `b14577983c5e0ab05225250491efe7363945742c`.
* Porcelain output was 0 lines before the runs and 0 lines after.
* Environment: `env -i HOME=/home/agent PATH=/home/agent/.venv-ia-release/bin:/usr/local/bin:/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1`, Python 3.12.3.

Scripts, all in `C:\Users\theis\AppData\Local\Temp\claude\444e85c66277a305\f388a28a-ca5c-4c89-be28-32fc8ef43b71\scratchpad\r53-map\probe\`:

* `r53map.sh`: clone, baseline tests, native mutants.
* `r53map2.sh`: completion-family mutants.
* `r53map3.sh`: K6 sensitivity control.
* `nwg_mutant_harness.py` and `completion_mutant_harness.py`: the two harnesses.

Each was launched as `MSYS_NO_PATHCONV=1 wsl -d Ubuntu -- bash /mnt/c/.../r53-map/probe/<script>.sh`.

**Mapping confirmation.** Each existing test was run once:

| Test | Exit | Last line |
|---|---|---|
| `tests/native-work-graph-cases.py` | 0 | `native-work-graph.test: ok` |
| `tests/work-graph-completion-cases.py` | 0 | `OK` (26 tests) |
| `tests/work-graph-completion-transition-cases.py` | 0 | `OK` (20 tests) |
| `tests/work-graph-pending-settlement-cases.py` | 0 | `OK` (22 tests) |
| `tests/work-graph-operation-cases.py` | 0 | `OK` |

**Mutation probes.** No file in the checkout was modified:

* The harnesses load the unchanged registered test module.
* They swap one compiler function in memory by string substitution on its source.
* For the completion family, they patch the compiler module that `scripts/work-graph-completion.py` execs.

| Mutant | NWG | CMP | TRN | PND |
|---|---|---|---|---|
| M0 control | green | green | green | green |
| M1 drop duplicate-evidence arm | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| M2 exit 0 counts as PASS | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| M3 acceptance/authority not conflicts | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| M4 derived cheap-path mode constant | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| M5 drop decision-change check | SURVIVED | n/a | n/a | n/a |
| K1 zero ceiling treated as absent | KILLED | not run | not run | not run |
| K2 suppress RECOMPUTE_REQUIRED | KILLED | not run | not run | not run |
| K3 drop duplicate-key arm | KILLED | survived | survived | survived |
| K4 drop common-source arm | KILLED | not run | not run | not run |
| K5 non-PASS terminal counts as PASS | KILLED | survived | survived | survived |
| K6 missing required counts as satisfied | KILLED | KILLED | survived | KILLED |

How to read the table:

* The K rows are sensitivity controls. They show that both harnesses can kill a mutant. In the completion family, K3 and K5 survive because its fixtures use distinct keys and never reach an all-settled non-PASS JOIN. The native family covers those arms.
* M5 is "n/a" in the completion family because only NWG calls `check_recursive_execution_v1`.
* A survivor is a missing discriminator, not a runtime RED. Nothing was rerun to obtain green.
