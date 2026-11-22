# Adviser DG17 package (Claude Opus 5.5, 2026-11-22). Start here.

Everything here is an adviser draft: **unreviewed, not shipped, no award**. Astra adopts; Sol-DG17 verifies against the source.

Base source is PR #255 head `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7`. Pro handoff: `2f920bd7` on `engineering/pro-final-20261122`.

| File | What it is | Use it for |
|---|---|---|
| `ACCEPTANCE_LEDGER.md` | DG16–DG18 accepted/partial/pending, from Root decision files | Owner dashboard; Astra adopts as the official ledger |
| `DG17_LEDGER_AND_PLAN.md` | All 36 cases, 14 families and 17 clauses with routes; the four-operation plan; specs in sections 7–8e4; preflight in 8f | Sol-DG17's working plan |
| `SUCCESSION_UPDATE_ASTRA_THREE_SOL.md` | Astra plus Sol-DG16, Sol-DG17, Sol-DG18: split, gates, first tasks | Appointing the agents |
| `OP_M_MISSION_DRAFTS.md` | Missions, oracles, distractors and twins for the 15 model cases | Preparing the Codex model batch |
| `draft-andon-return/` | Checker for where a diagnosis returns, with 9 passing tests | N04, N05, H07, M11, terminal clause 4 |
| `draft-jidoka/` | Stop-the-line versus raise-the-alarm checker, with 9 passing tests | N07, M06 |
| `draft-stop-fix/` | Native Stop patch (owner-selected disposition plus activation fallback), 5 passing source tests, probe script, measured package cost | Native Stop amendment PASS items 2–4 and 12 |

**Decisions waiting for Astra:**
1. Where the two missing checkers live: shipped, or repo-only.
2. Which roughly 300 compressed bytes to cut so the Stop patch fits the package reserve.
3. Whether a retired (TOMBSTONED) binding should count as "no active object".
4. Confirming that earlier DG17 awards (made at `a297957b` and `51416b2f`) carry over to the final candidate.

**Not done here:** no native or model run, no hosted run, no change to PR #255 or the results branch.
