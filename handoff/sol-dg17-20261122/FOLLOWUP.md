# DG17 repo-only checker corrections and optional routing

The five reproduced false acceptances now refuse in the repo-only checkers. The shipped compiler and resolver also passed six focused optional-routing controls on PR #255 source `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7`, tree `9c3913ceaa95f3f36b0377fe2dba4a302afcba89`. [Original #211](https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/211), [immutable adviser source](https://github.com/theislampill/IMPLEMENTAUDIT.md/tree/3507812efa63fd3463d8adaee0d2ca39bd762820/handoff/opus-dg17-plan-20261122).

## Checker evidence

| Candidate | Observation |
|---|---|
| Exact adviser scripts, with five regression tests added | 23 tests. All 18 original tests passed and all five regression tests failed because the originals returned accept. |
| Corrected repo-only checkers | 32 of 32 passed. The earlier positive routes and Jidoka/Andon distinctions remain covered. Malformed, wrong-owner, duplicate, and stale-input controls also discriminate. |

Jidoka tracks each unresolved check separately. An Andon marks that same check visible. Recovery needs a named open check, visibility, and an explicit Boolean reverification for that check. A second failure survives the first recovery and stops propagation. The positive control recovers both checks separately. Ambiguous duplicate open identities refuse.

The Andon checker requires a direct return record's observed recipient to match the supplied caller. For a governed return, it recomputes the SHA-256 of the supplied frozen envelope's deterministic UTF-8 JSON and requires the returned digest to match. A changed envelope, changed returned digest, or placeholder refuses. These are data bindings in fixture records. They convey no authority and do not authenticate a producer, delivery, or actual governor consumption. The diagnostics retain the original return authority and terminal-marker fences. [Exact test census and draft blobs](REPO_ONLY_CHECKER_RESULTS.json).

## N10 structural increment

The unchanged shipped `--native-a-g` CLI gave zero selected children for the mechanical request and exactly one `audit-andon` selection for a standalone substantive request with no predecessor child stages. Swapping the order of two independent requests preserved their per-request dispositions. A single supplied fixed four-child itinerary produced `BLOCK`. All five compiler requests stayed byte-identical and retained `SOLE_GOVERNOR` authority. The unchanged resolver resolved exactly the selected child's package-local file. [Command, inputs, outputs, and product blobs](N10_OBSERVATIONS.jsonl).

The existing routing test hit Windows executable-mode and shebang launch errors. On WSL, an archive of the exact source projected the executable at 0755. Its 24 evidential-support tests and 154 subprocess cases passed, the exact resolver reported 20 controls with zero failures, and the adjacent cognition obligation helper reported 16 passing source-value controls. The narrow archive omitted the remaining cognition-pending fixtures, and the encompassing command ended on the first missing fixture. These are completed component observations with a partial existing suite. See [source test entry](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/51416b2f156b341c4a5f09029e2c6ceb5b30b1e7/tests/internal-skill-routing.test.sh).

The structural increment proves behavior at the preparation and resolver interfaces on supplied facts. Original N10 still needs applicable actual governor behavior rejecting a hidden fixed lifecycle while retaining lawful zero- and one-child work. The adviser fixtures still need an actual canonical consuming relation for N07 and the Andon return cases. These layers stay at their observed scope. No already-awarded case was rerun as a qualification, and no Stop patch, model run, native episode, source-owner replacement, or integration action occurred.

## Independent receiving

Rehash the four adviser source/test blobs from the pinned commit, compare the named five preimage expectations, and run the corrected suite and N10 instrument. Compare precise outputs, original positives, and claim limits before any Root decision. The handoff directory stays outside shipping and validation registration. The evidence commit can be reverted atomically on the Sol branch. No original or final-candidate award is issued.
