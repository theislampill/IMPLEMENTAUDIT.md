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
