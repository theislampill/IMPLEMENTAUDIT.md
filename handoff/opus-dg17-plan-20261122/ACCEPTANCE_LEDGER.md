# DG16–DG18 acceptance ledger (adviser reconciliation, 2026-11-22)

Prepared by Claude Opus 5.5, read-only.

**Basis:** published Root decision files and commit titles on `engineering/pro-executor-original-completion-20261115` at results46 `6431a1d1e067ab37e4f461caa4a61890d69e7c14`, plus Pro's Nov 17 disposition tables (`continuing-execution-20261117/terminal-reconciliation/`) and Pro's handoff `2f920bd7`.

This ledger **records** decisions; it awards nothing. Astra must verify and adopt it. Each Sol updates only its own cell, with evidence, and Astra is the sole acceptance authority.

**Status words:**
- **ACCEPTED:** Root issued an original acceptance, and the decision body is published.
- **ACCEPTED-BODY-MISSING:** issued, but the original award body is not published.
- **REPORTED:** issuance reported, but no decision body is available.
- **PARTIAL:** an accepted limb or scope that is not the whole requirement.
- **PENDING:** not yet accepted.
- **BLOCKED:** needs a capability, grant or evidence that is not available.
- **UNKNOWN:** could not be settled from the records.

Paths below are under `handoff/pro-executor-results-20261115/`.

---

## DG16 (R0035, #209): run work in the right order, merge only complete and current results

**Milestones: 2 DONE / 6.** **Original 48-row disposition: 0 / 48 final.** The rows can only be dispositioned at M6.

| ID | Plain meaning | Status | Evidence |
|---|---|---|---|
| M1 | Two real cases run in a locked-down sandbox on a real host | BLOCKED | Protected run `44888568054` SPENT_NO_RETRY; host profile (cache, NSS) still failing (results44) |
| M2 | Old and new checkers agree across the whole population | ACCEPTED | Run `44666584405`; commit `703f19ae` (results19) |
| M3 | Real merge of M1 results, two Root decisions, stale refusal | BLOCKED | Same run as M1 |
| M4 | Correct reaction to a real mid-task change | ACCEPTED | Nov 17 DG16_ORIGINAL48 rows L01–L06 (`ORIGINAL_M4_L04_NATIVE_EPISODE_INDEPENDENT…`) |
| M5 | Packages plus four installed routes | PARTIAL | Accepted scopes reused (rows Q04/Q05); occurrence join pending |
| M6 | Final cold review plus the 48-row disposition | PENDING | Needs M1, M3, M5 |

**Additional gate:** a new exact owner grant for a fresh protected G132 operation, after readiness.

**Top three blockers:**
1. GitHub's runner userland drifts (`ld.so.cache`, NSS not files-only). The host route is undecided.
2. Four historical joint-source files are missing (results45).
3. The newest observer report exceeds its size bound (`45049052400`: 2,589,544 bytes against 1,823,337 allowed).

---

## DG17 (R0037, #211): planning, interruptions and final audit behave honestly together

**Cases: 8 DONE / 36. Mutation families: 4 DONE / 14** (plus 1 REPORTED). **Terminal clauses: 0 / 17. Native Stop PASS items: 0 / 15.**

"DONE" means accepted at the source and scope Root recorded. #211 accepts the cell only on **one final candidate**, so every DONE item still needs carry-over proof or a fresh run there.

| ID | Plain meaning | Status | Evidence |
|---|---|---|---|
| P04 | Refuse to act on stale state at resume | ACCEPTED | Commit `47be1143` (results18) |
| B02 | Small obvious problem handled without heavy analysis | ACCEPTED | Commit `703f19ae` (results19) |
| N01 | Never "done" with an open obligation | ACCEPTED | `continuing-execution-20261120-26/DG17_N01_ROOT_ACCEPTANCE.json` |
| N11 | Merge stays the governor's, not a helper's | ACCEPTED | `continuing-execution-20261118-02/ROOT_DG17_N11_B05_H04_ACCEPTANCE.json` (blob `c18e9f5f`) |
| B05 | Fake review gap handled honestly | ACCEPTED | Same file |
| H04 | Unfamiliar lane with missing merge cannot advance | ACCEPTED | Same file |
| N12 | "Green" while a check failed is rejected | ACCEPTED at structural record layer | `…/ROOT_DG17_N12_ACCEPTANCE.json` (blob `f6188a0b`) |
| B03 | Restating the plan causes no replan | ACCEPTED at bounded scope | `…/ROOT_DG17_RETAINED_ELIGIBILITY_ACCEPTANCE.json` (blob `87535c94`) |
| P02, B04, H05 | Selective redo of affected work only | PARTIAL (limb observed; whole case explicitly not awarded) | Same retained-eligibility file; Nov 17 table |
| P03, P07, H07 | Planning failure; governed diagnosis; dual entry | PARTIAL (episodes run; provenance or receiving pending) | Nov 17 table |
| P05, P08, P09, P10, N08, N09, N10, B01, H03, H06 | Various | PARTIAL (source-semantic or operational limb received only) | Nov 17 table |
| P01, P06, N02–N07, B06, H01, H02, H08 | Various | PENDING | Nov 17 table "REQUIRES_…" |
| Family M09 (protect unrelated work) | | ACCEPTED | `…/ROOT_DG17_M09_ACCEPTANCE.json`, commit `04c060ca` |
| Family M12 (helpers get no authority, no chaining) | | ACCEPTED | `…/ROOT_DG17_M12_ACCEPTANCE.json`, commit `e08f8713` |
| Family M04 (final re-audit) | | REPORTED (award body and 2,953-check report lost) | results41 `M04_PUBLICATION_RECOVERY.md` |
| Family M02 (selective redo) | | ACCEPTED at its exact consumer ("does not award P02/B04/H05") | `…/ROOT_DG17_BATCH02_ACCEPTANCE.json` (blob `21e832b2`), source `a297957b` |
| Family M05 (refuse closure with an open obligation) | | ACCEPTED at its exact consumer | Same file |
| Families M04, M12, M14 conjuncts | | Narrower conjuncts accepted only (M12 later became a whole award) | Same file |
| Families M01, M03, M06–M08, M10, M11, M13 | | PENDING | — |
| Terminal clauses 1–17 | Final-version checks | PENDING | — |

**Top three blockers:**
1. Two rules have no checking code: stop-the-line versus raise-the-alarm, and where a diagnosis returns. Drafts exist on `engineering/opus-dg17-plan-20261122`.
2. The model-judgement cases need Codex runs with proven model identity, under an owner grant.
3. Native Stop needs a Codex episode under an owner grant, and must allow a valid handoff that the yield-only policy currently blocks.

---

## DG18 (R0039, #215): archive growing state without losing obligations

**Numbered criteria: 12 decisions issued / 14** (10 with published award bodies). **Binding obligations: 0 / 5.**

| ID | Plain meaning | Status | Evidence |
|---|---|---|---|
| A1, A3 | Identical output; archive never mistaken for current | ACCEPTED | Commit `3a6a0bc5` (results21) |
| A2, A7 | Every field protected; small projects stay simple | ACCEPTED-BODY-MISSING | `continuing-execution-20261120-24/DG18_A2_…`, `DG18_A7_PRIOR_ACCEPTANCE_RECORD.json`; commit `5dcd7d50` |
| A6, A8, A9, A13 | Retrieval, rollback, crash safety, marker safety | ACCEPTED | Commit `3eece0d0` (results20) |
| A10 | Works with all other parts | ACCEPTED | Commit `8807b8e9` |
| A11 | Installed plugin still works | ACCEPTED | Commit `e852e16a` |
| A12 | Skipped or reordered steps are caught | ACCEPTED | `continuing-execution-20261120-23/DG18_A12_ROOT_ACCEPTANCE.json`; commit `a6a4e402` |
| A14 | Steps in the one safe order | ACCEPTED | Commit `703f19ae` |
| A4 | Unsafe writes and paths fail safely, including on Windows | PENDING | Windows matrix memory failures; diagnostic decisions only (`DG18_A4_ROOT_DIAGNOSTIC_DECISION.json`, results41) |
| A5 | A fresh session reconstructs the exact state | PARTIAL | Bounded cold-preservation scope accepted (commit `765090eb`); full criterion withheld |
| OR | Trustworthy host size measurement triggers archiving | BLOCKED (needs a Codex host producer and grant) | Handoff `CUSTODY_AND_GAPS.md` |
| Compaction | Two real compactions survive archiving | BLOCKED (N1 record lost; interpretation open) | `original-acceptance/dg18/N1_HISTORICAL_GAP_AND_CURRENT_OPERATIONS.md` |
| Retry | Retry told apart from the original | PENDING | — |
| Cold receiving | Full fresh-session check | PENDING (depends on the two rows above) | — |
| C02 | Authorized correction of a wrong invalidation | PENDING (needs a real event and an entitled approver) | — |

**Top three blockers:**
1. A4: run the Windows tests one process each, with an equivalence proof, and settle where R01–R09 came from.
2. N1: list what the project state itself records, then answer the interpretation question.
3. The OR producer and C02 need a Codex host session and a disposable real-event trial respectively.

---

## Uncertainties not settled here

- Whether DG17 awards made at source `a297957b` (Nov 18) carry over to the final candidate.
- M04's original body.
- Whether DG18 criterion awards made at `51416b2f` remain valid after future source changes.
