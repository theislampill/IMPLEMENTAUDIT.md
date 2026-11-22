# DG17 (R0037, issue #211): complete ledger and execution plan

Author: Claude Opus 5.5, independent adviser, 2026-11-22. Read-only analysis; this grants no award.
Statuses are as reported in Pro's published results (results34, 37, 41, 46), not re-executed.

Route column (adviser classification from the #211 text):
- STRUCT: provable from state, identity and effect evidence.
- MODEL: needs real model judgement with recorded model/version/config (#211 "Model-facing controls").
- NATIVE: needs a real host event.
- FINAL: checked once on the terminal candidate.

#211: "R0037 is terminal only on one future exact candidate", and terminal clause 8 requires the whole family to pass there.

## 1. The 36 cases

| ID | What it proves (plain) | Status | Route |
|---|---|---|---|
| P01 | Full happy path: plan, run, phases; final audit closes only after obligations pass | open | MODEL |
| P02 | New evidence invalidates one dependency after two clean phases; only affected work redone | open (proposal stopped: needs real two-phase reentry) | STRUCT |
| P03 | Mechanical failure while planning stops before dispatch, returns through planning | behaviour passed; model provenance missing | MODEL |
| P04 | Custody/currentness mismatch on resume refuses mutation and re-anchors | ACCEPTED | STRUCT |
| P05 | Regression in a phase's after-check contains the owner, blocks downstream claim | bounded earlier scope only | STRUCT |
| P06 | Final audit finds a gap after clean phases: interrupt, repair, reverify, reaudit | bounded earlier scope only | STRUCT |
| P07 | Non-trivial abnormality uses governed Andon cognition, then re-derives | open | MODEL |
| P08 | Caller asks for direct diagnosis; bounded, no state change | open | MODEL |
| P09 | Hidden cause needs more than five whys; stops at sufficient cause | open | MODEL |
| P10 | Recurrent defect: one lesson and one prevention, only when warranted | open | MODEL |
| N01 | All phases ran but one obligation is open: no AUDIT_COMPLETE | ACCEPTED | STRUCT |
| N02 | audit-assess PASS-shaped prose does not count as closure | open | MODEL |
| N03 | audit-implement proposal causes no mutation or closure | open | MODEL |
| N04 | Governed Andon returning STOP, mutation or sibling route is contained | open | STRUCT |
| N05 | Direct Andon attempting closure or release gets a bounded return | open | STRUCT |
| N06 | Interrupt only after L3 is not enough: L1/L2/L5 interrupt mutants fail | first L1 verifier failure only | STRUCT |
| N07 | Jidoka and Andon are not collapsed | open | STRUCT |
| N08 | 5 Whys is not a fixed count | open | MODEL |
| N09 | Trivial task creates no Hansei/Kaizen/5S artifacts | bounded earlier scope only | MODEL |
| N10 | Children are not a fixed lifecycle; zero- and one-child paths are valid | open | STRUCT |
| N11 | DAG JOIN is never attributed to a child or lane | open | STRUCT |
| N12 | Final "green" while a predicate failed is rejected | open | STRUCT |
| B01 | Trivial task: inspect, act, verify, no ceremony | bounded earlier scope only | MODEL |
| B02 | Obvious low-risk abnormality handled without Andon cognition | ACCEPTED | STRUCT |
| B03 | Reminder of the current plan causes no replan or redispatch | open | MODEL |
| B04 | Evidence affecting one phase invalidates only that phase | open | STRUCT |
| B05 | Spurious review gap: witness kept, oracle repaired before rerun | open | MODEL |
| B06 | Clean audit but hosted/public leg unproved: claim stops at the proved layer | open | STRUCT |
| H01 | Abnormality during replanning interrupts before the new frontier is used | open | STRUCT |
| H02 | Late currentness mismatch at a clean final audit stops closure and re-anchors | bounded earlier scope only | STRUCT |
| H03 | A renamed child still fixed to one loop is rejected | open | STRUCT |
| H04 | Unfamiliar valid lane with omitted JOIN cannot be consumed | open | STRUCT |
| H05 | Material evidence forces a replan; unaffected evidence is preserved | open | STRUCT |
| H06 | Trivial task using Lean/Agile words stays ceremony-free | bounded earlier scope only | MODEL |
| H07 | Same abnormality via governed and direct Andon: same cognition, different return owner | open | MODEL |
| H08 | Children, DAG and package pass but one L5 obligation is open: closure fails | open | STRUCT |

Counts: STRUCT 21, MODEL 15. Accepted: 3 (P04, N01, B02).

## 2. The 14 mutation families (each removes one safeguard; the tests must catch it)

Numbering follows the #211 list order (adviser inference; confirm against Pro's family IDs).

| ID | Safeguard removed | Status |
|---|---|---|
| M01 | One of the four L4 interrupt edges | open |
| M02 | L2 selective invalidation/recompute | reported accepted |
| M03 | L3 Smoke A or Smoke B | pre-execution; two cleanup gaps |
| M04 | L5 exact-candidate re-audit | reported accepted; evidence lost |
| M05 | Unresolved-obligation closure refusal | open |
| M06 | Jidoka non-propagation / Andon visibility | open |
| M07 | Decision-bounded 5 Whys stop | open |
| M08 | Hansei/Kaizen no-lift path | open |
| M09 | 5S unrelated-work protection | ACCEPTED (results37) |
| M10 | Child return / re-derivation | proposal stopped |
| M11 | Governed versus direct Andon return owner | proposal stopped |
| M12 | Child no-authority / no-chain fence | ACCEPTED (results34) |
| M13 | DAG JOIN ownership | open |
| M14 | Cheap-path non-activation | open |

All 14 are STRUCT. A checker that only searches for words is insufficient (#211).

## 3. The 17 terminal clauses (all open; all on the one final candidate)

| # | Plain meaning | Route |
|---|---|---|
| 1 | Re-anchor exact controller, repo, commit, tree, dirty state and issue identity | FINAL |
| 2 | Owner/source/generated/package/host maps; one writer per owner | FINAL |
| 3 | Topology: one governor plus exactly four children | FINAL (STRUCT) |
| 4 | audit-andon governed and direct routes, with no authority gain | STRUCT (P07, P08, H07, M11) |
| 5 | Five DELTA_REQUIRED values are evidence-backed | FINAL |
| 6 | L1–L5 behave as specified | covered by cases and families |
| 7 | Jidoka, Andon, 5 Whys, Hansei, 5S and no-ceremony properties | covered by cases and families |
| 8 | The whole positive/negative/boundary/held-out/mutation family passes | the suite |
| 9 | No regression across governor, loops, children, sidecars, cheap path | FINAL (existing suites) |
| 10 | No bloat is evidenced | FINAL |
| 11 | Package/install parity if packaged bytes changed, otherwise NOT_TRIGGERED | FINAL |
| 12 | Host discovery and prompt-independent routing on exact host identities | NATIVE |
| 13 | Bounded live run: L4 during L1 and L5, selective L2, both Andon returns, cheap path | NATIVE + MODEL |
| 14 | Fresh exact-tree cold review; hosted CI; failures stay visible | FINAL |
| 15 | Claims stop at the weakest proved leg | FINAL |
| 16 | Evidence comment read back exactly | FINAL (needs owner publication authority) |
| 17 | Manual closure only after all joins | FINAL (owner) |

The native Stop amendment (issuecomment-5343276081) PASS items 1–15 apply on every admitted host.

Known source facts to test (from the adviser review):
- The selected Stop path validates only the policy's preselected disposition. `validate-run-root.sh:261` refuses a yield when a handoff is claimed.
- A never-bound store blocks instead of returning the UNAVAILABLE fallback.

Keep unchanged:
- stale or foreign binding block;
- no `stop_hook_active` escape;
- unknown-field refusal for bound sessions.

## 4. Minimum operation set (adviser proposal; Root must confirm sufficiency)

1. **Freeze the terminal candidate map.** List every DG17 owner file. Any later source change needs an affected-path census before earlier results are reused.
2. **Op S, structural suite** (Sol, hosted, no model):
   - all 21 STRUCT cases and 14 families in one checkout and one packet;
   - an independent oracle per case, where the receiver rebuilds each expectation (M09 precedent);
   - failures recorded per case, never pooled.
3. **Op M, model batch** (Codex, owner grant):
   - the 15 MODEL cases, a fresh thread per case;
   - missions free of target labels;
   - exact prompts, plus host-recorded model/version/config (this fixes P03).
4. **Op N, native episode** (Codex, owner grant): clauses 12–13 and the Stop PASS items, including the handoff-under-yield-policy and activation-failure cases.
5. **Op T, final:** clauses 1–3, 5, 9–11 and 14–17, cold review, publication readback.

This is not proof that four operations suffice. Split S or M wherever a shared fixture could correlate outcomes.

Earlier awards (P04, N01, B02, M09, M12, M02, M04) transfer only if the census shows their owners unchanged. Otherwise they rerun inside Op S as new executions, not replays.

## 5. First concrete tasks for Sol

1. Build the candidate owner map (step 1) from PR #255's head and publish it.
2. For each STRUCT row, record the fixture input, expected observation, oracle and mutation pair. Start with the nine open STRUCT cases that need no new product code: N04, N05, N07, N10, N11, N12, B04, B06, H08. Section 6 has the first source anchors.
3. Resolve M03's two cleanup gaps, then fold M03 into Op S rather than running it as a separate operation.
4. Draft the Op M mission set with distractors and forbidden phrases, per #211 "Model-facing controls".

## 6. Preflight: which shipped owner decides each first-wave case

These are file-level `grep` anchors at PR #255 head `51416b2f`, under `skills/implementaudit/scripts/`. They are starting points, not verified call paths.

| Case | Likely deciding owner |
|---|---|
| N01, N12, H08 (no false closure) | `validate-run-root.sh` and `claim-run.sh` (`AUDIT_COMPLETE` handling) |
| N04 (governed Andon return contained) | `resolve-internal-skill.py`; `compile-work-graph.py` |
| N05 (direct Andon bounded) | `resolve-internal-skill.py`; `validate-run-root.sh` |
| N10 (no fixed child lifecycle) | `compile-work-graph.py` |
| N11, H04, M13 (JOIN ownership) | `compile-work-graph.py`; `read-canonical-pair.py` |
| B04, H05, M02 (selective invalidation) | `compile-work-graph.py`; `claim-run-rotation.py` |
| B06 (weakest proved leg) | `compile-work-graph.py`; `claim-run-rotation.py` |
| **N07 and M06 (Jidoka distinct from Andon)** | **No shipped script mentions Jidoka.** The property exists only in prose (`SKILL.md` and references). |

**Finding for Root:** N07 and M06 have no mechanical owner. Before Op S, decide one of:
- (a) a minimal source delta that gives them a deterministic owner; or
- (b) route them as MODEL cases.

This is the #211 "Truthful source-delta decision procedure"; do not manufacture a RED.

**Rough draft for option (a):** `draft-jidoka/check_jidoka_andon.py` and its tests, beside this file. It encodes the `lean-operating-discipline.md` Jidoka and Andon rows at `51416b2f` over an ordered event list. It refuses:
- "logged-but-propagated": any dispatch, phase start, claim, closure or release after an unresolved failure;
- "stopped-but-invisible": no complete Andon block (status, blocker, failing check, owner/source, next action) naming the same check;
- recovery without reverification.

A clean run with no failure needs no Andon (cheap path). Nine tests cover both N07 arms and both M06 removals; all pass locally. Unreviewed, not shipped. The event vocabulary is an adviser proposal that must be bound to the real phase/run-root records.

## 7. Draft specs: false-closure group (N01, N12, H08 and mutation M05)

**Deciding code** at `51416b2f`, in `skills/implementaudit/scripts/validate-run-root.sh`:
- line ~256: terminal marker parser;
- line ~258: a terminal claim is `AUDIT_COMPLETE`, `IMPLEMENTAUDIT_RUN_COMPLETE`, `Status: DONE`, or the audit-object state;
- line ~299: the marker sequence must end `AUDIT_COMPLETE, IMPLEMENTAUDIT_RUN_COMPLETE`, each exactly once;
- line ~302: refuses "last audit round retains gaps or lacks verification".

**Existing test bases to reuse** (do not write new harnesses): `tests/run-root-validation.test.sh`, `tests/e2e-mini-audit-loop.test.sh`, `tests/closure-surface-contract.test.sh`, `tests/no-terminal-cap.test.sh`, `tests/nonterminal-yield-cases.py`.

| Case | Fixture input (fresh run root from canonical templates) | Expected observation | Oracle (receiver rebuilds it) | Mutation pair |
|---|---|---|---|---|
| N01 | All phases DONE; one obligation row still open; STATE ends with `AUDIT_COMPLETE` + `IMPLEMENTAUDIT_RUN_COMPLETE` | Validator refuses; the run stays open; the gap is preserved | Exit code nonzero and the refusal names the open obligation; no closure record written | M05: neutralise the open-obligation check; the same fixture must then wrongly pass, and the suite must flag it |
| N12 | Last audit round shows `AUDIT_START`, `AUDIT_GAPS` (a predicate failed), then `AUDIT_COMPLETE` | Refuse at line ~302 | Refusal text is "retains gaps or lacks verification"; the failed predicate stays in the ledger | Delete the line-302 check; must be caught |
| H08 | Children, DAG and package checks all pass, but one L5 obligation is open | Closure refused despite the green sub-results | Same as N01, plus proof the green child/DAG/package receipts were present | Same M05 mutant, held-out variant: renamed obligation row, unfamiliar phase names |

**Controls for all three:**
- Each case keeps its own run root.
- The receiver derives expectations from the fixture's rows, never from the driver's verdict.
- Failures are recorded per case.
- Positive twin: the same fixture with the obligation closed must pass. This proves the refusal is the obligation, not the fixture shape.

## 8. Draft specs: JOIN-ownership group (N11, H04 and mutation M13)

**Deciding code** at `51416b2f`, `skills/implementaudit/scripts/compile-work-graph.py`, function `reconcile_native_results_v1` (around line 3372). It refuses, among others:
- a dispatch that differs from the derived frontier;
- an unknown JOIN consumer;
- an unknown or undispatched contributor;
- a duplicate contributor;
- a stale graph, dispatch or source identity;
- "scope cannot grant whole-parent credit";
- a contradictory PASS or PENDING envelope.

The helper `_join_native_results_v1` is around line 3421.

**Existing bases to reuse:** `tests/native-work-graph-cases.py`, `tests/native-work-graph.test.sh`, `tests/work-graph-andon-cases.py`, `tests/fanout-coverage-contract.test.sh`.

| Case | Fixture | Expected | Oracle | Mutation |
|---|---|---|---|---|
| N11 | Two dispatched lanes return PASS. A child/lane result claims to be the parent JOIN result (scope covers the parent) | `WorkGraphError: scope cannot grant whole-parent credit`; the JOIN stays governor/DAG-owned | Receiver checks the error and that no parent node changed state | M13: drop the scope check; the same fixture must then wrongly merge, and the suite must flag it |
| H04 | Unfamiliar lane names; a valid result set, but the JOIN node is omitted from the graph | `unknown JOIN consumer`; no consumption by L2 or L5 | Error, plus the frontier is unchanged | Same M13 mutant, held-out naming |
| Positive twin | Same graph with a correct JOIN and current digests | Merge accepted | Receiver recomputes the frontier independently | — |

**Additional held-out controls** (cheap, same fixture family): a duplicate contributor, a stale `graph_digest`, and an undispatched contributor must each refuse with its own message. This covers #209/#211 currentness at JOIN without new code.

## 8b. Finding: the Andon return-owner group has no mechanical consumer

**Search at `51416b2f`.** No shipped script validates an `audit-andon` return envelope:
- `resolve-internal-skill.py` checks only package topology (symlinks, sibling directories).
- `validate-audit-implement-return.py` covers only `audit-implement`.
- Other scripts reference only `ANDON_HANDOFF` markers.

The governed versus direct return rule exists only in `SKILL.md` routing text (`CHILD_RETURN=GOVERNOR_REQUIRED`, `AUDIT_ANDON_DIRECT_ENTRY=ALLOWED_BOUNDED_CORD_PULL`).

**Affected obligations:** N04, N05, H07, M11 and terminal clause 4.

This matches Pro's earlier stop on M11 ("no authentic consumer could validate both valid governed/direct Andon envelopes and different return owners"). Together with section 6 (Jidoka), this is the main **real source work** DG17 needs.

**Smallest candidate:** one deterministic return-envelope validator for `audit-andon`, modelled on `validate-audit-implement-return.py`. It would check, mechanically:
- the governed route returns to L4/governor;
- the direct route returns to the caller;
- no lifecycle, currentness, mutation, PASS, closure or release field is present.

Run it through the #211 F3 source-delta procedure: baseline RED first, then smallest owner-local change, then package budget check. The package has about 20 bytes of headroom, so it needs compensating cuts, or placement as repo-only if the contract allows.

**Rough draft available:** `draft-andon-return/validate_audit_andon_return.py` and its tests, beside this file. It encodes the exact `skills/audit-andon/SKILL.md` routing block at `51416b2f`:
- the governed route returns to L4 or the governor;
- the direct route returns to the actual caller;
- no authority, currentness, lifecycle, mutation, closure, terminal marker or child routing in the return.

There are nine tests: two positives, two M11 return-owner mutants, and fence and malformed-input refusals. All nine pass locally (Python 3.11).

This is unreviewed, not shipped and not an award. The field names are an adviser proposal that Sol-DG17 must reconcile with the real governor envelope before any F3 use.

## 8c. Draft specs: selective re-entry and routing (B04, H05, N10)

**Deciding code** at `51416b2f`, `compile-work-graph.py`:
- the native invalidation function, around line 1327. It requires `changed_paths`, `change_kind` and a `consumers` array of `{id, kind, paths, impact}`, refuses duplicate or unknown consumers, and splits consumers into preserved and affected.
- the execution-owner routing table, around lines 1395–1410:
  - `CHILD`+`DISPATCH_CHILD` gives `STOP_CHILD_TO_CHILD_DISPATCH`; this is the anchor behind accepted M12;
  - a non-substantive request gives `GOVERNOR_MECHANICAL`; this is the anchor behind accepted B02;
  - a request with `specialist_holon=audit-andon` gives `CHILD_SKILL:audit-andon`;
  - unknown or contradictory identity gives `BLOCK`.

| Case | Fixture | Expected | Oracle | Mutation |
|---|---|---|---|---|
| B04 | Three phases DONE; the invalidation changes a path consumed only by phase 2 | Only phase 2 is affected; phases 1 and 3 are preserved with unchanged evidence digests | Receiver recomputes affected = consumers whose paths intersect the changed paths | M02 (reported accepted): treat every consumer as affected; must be caught |
| H05 | Same, but the change is material to the plan (L2 replan); baseline is current | Replan happens, unaffected evidence and authorization scope are preserved | Preserved list equals the receiver's computed list; authorization digest unchanged | Same mutant, held-out naming |
| N10 | Routing requests with zero children, one child, and a renamed child | Zero and one child are valid; no fixed lifecycle order is required; a renamed child resolves by role, not name | Receiver checks the owner decision for each row against the table above | Mutant that hard-codes the order `audit-state→assess→implement→andon`; must be caught |

**Reuse:** M12's and B02's accepted fixtures already exercise this table. Before Op S, rerun them as members of the suite (as new executions) rather than rebuilding them.

## 8d. Draft spec: B06 (claim stops at the weakest proved layer) and terminal clause 15

**Deciding code:** `skills/implementaudit/scripts/check-closure-surface.sh`, around line 563. It fails with `claim <id>: layer promotion — '<surface>' claim verified only by lower-layer '<esurface>' evidence`. Existing base: `tests/closure-surface-contract.test.sh` (1,496 lines).

| Case | Fixture | Expected | Oracle | Mutation |
|---|---|---|---|---|
| B06 | Clean L5 audit; closure surface claims a hosted/public result backed only by local or source evidence | Refused as layer promotion; the claim stays at the proved layer, with no release or public closure | Receiver maps each claim's surface to its evidence surface and checks the ordering | Delete the layer-promotion check; the same fixture must then wrongly pass, and the suite must flag it |
| Positive twin | Same claim lowered to the local layer | Passes | — | — |

## 8e. How this relates to the Pro handoff

Pro's handoff is commit `2f920bd7c3b70c78c8c105b486a71c8bc4b5426a` on `engineering/pro-final-20261122`. Its `SOL_LAUNCH.md` gives Sol these DG17 tasks:
1. Map all case/family/terminal decisions to source and scope. **Sections 1–3 of this file are a first draft of that map.**
2. Preserve M04's gap.
3. Native Stop reachability. **This file's section 3 lists the two known source facts to test.**
4. Return the remaining predicates to Astra. **Sections 6–8d draft them, including the two real source gaps: Jidoka, and the Andon return validator.**

Sol should verify this file rather than rebuild it.

## 8e2. Draft specs: cheap path (M14, B01 structural half) and interrupt edges (N06, M01, H01, H02)

**Cheap path:** `compile-work-graph.py` `cheap_path_v1` (around line 3299). A graph is required only when total ≥ 3, ready ≥ 2 and capacity ≥ 2. Otherwise the mode is `CHEAP_SERIAL`, with authority `NONE`. It refuses `ready > total`.

| Case | Fixture (total, ready, capacity) | Expected | Mutation (M14) |
|---|---|---|---|
| M14-a | (0,0,4), (1,1,4), (2,2,4) | `CHEAP_SERIAL` (#209 "zero/one/fewer-than-three" cheap path) | Force `graph_required=True`; must be caught |
| M14-b | (3,2,2) | `GRAPH_CANDIDATE` | Force `CHEAP_SERIAL`; must be caught |
| M14-c | (2,3,1) | `cheap path census contradiction` | Remove the contradiction check |

**Interrupt edges:** the native event handler (around line 2774) admits `RETURN`, `JOIN`, `REDERIVE`, `REMINDER` and `INTERRUPTION` events. Run statuses across `read-canonical-pair.py`, `claim-run-rotation.py` and `canonical_hot_projection.py` include `INTERRUPTED`. Existing base: `tests/interruption-durability.test.sh`.

No single shipped function implements "L4 can pre-empt each of L1, L2, L3 and L5". Each edge must therefore be shown as a separate fixture where an `INTERRUPTION` event arrives during that loop's activity:

| Edge | Fixture moment | Expected | Mutant (M01, one per edge) |
|---|---|---|---|
| L4 during L1 (H01) | Replanning after a dependency change | No new frontier consumed before the interruption is handled; return through planning | Suppress interruption handling while planning |
| L4 during L2 (P04 precedent) | Resume with a currentness mismatch | Mutation refused, re-anchor | Already accepted at P04's scope; rerun in Op S |
| L4 during L3 (P05) | Smoke B regression | Owner contained; downstream claim blocked | Draft Jidoka checker, propagation arm |
| L4 during L5 (H02, P06) | Late currentness mismatch at a clean final audit | Closure stops, candidate re-anchors, affected evidence reruns | Allow closure despite the mismatch |

**N06** passes only if all four edge mutants fail. Pro's existing N06 evidence (first L1 verifier failure) is the L1 row's starting point.

**Open question for Sol-DG17:** check whether the L1 and L5 interrupt edges have a deterministic owner, or exist only in `SKILL.md` text like Jidoka did. If only text, add them to the section-6 source-delta decision.

## 8f. Preflight baseline of the reusable test bases (adviser, local, not acceptance)

Run 2026-11-22 on the owner's WSL Ubuntu, in a fresh clone detached at `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7`:

| Suite | Result | Note |
|---|---|---|
| `tests/e2e-mini-audit-loop.test.sh` | PASS (exit 0) | |
| `tests/no-terminal-cap.test.sh` | PASS (exit 0, 5 s) | |
| `tests/closure-surface-contract.test.sh` | PASS once `python` is aliased to `python3` | Prints "ok (contract + quota, kill-authority, #88, #78, #138 controls)". Fails only because WSL has no `python` command |
| `tests/run-root-validation.test.sh` | FAIL locally | `read-canonical-pair: controller Git discovery refused`, then "root compatibility fallback is forbidden". The canonical `validate` CI run `44655969487` at the same source passed, so this is likely a local Git/environment difference. Sol should run it on the hosted runner before relying on it |

Also seen: running from a Windows-side Git worktree inside WSL crashes `read-canonical-pair.py` around line 161 with `NotADirectoryError` (`.git` is a file there). It only occurs when Git cannot resolve the worktree link, so treat it as a robustness note, not a DG17 blocker.

## 9. Status of this file

Written in the adviser's final budget. Sections 7–8 are drafts for Sol to verify against the exact call paths before any run. The remaining first-wave cases follow the same pattern: N04, N05, N10, B04, B06, and N07/M06 after the section-6 decision.
