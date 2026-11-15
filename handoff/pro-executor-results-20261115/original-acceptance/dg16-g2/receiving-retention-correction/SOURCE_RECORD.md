# G2 nonzero receiving: bounded failure-retention correction

## Original clause and demonstrated defect

Original #209 binding comment 5314412493, Acceptance item 3, requires complete normalized all-settled JOIN to preserve failure, non-verdict, partial and terminal evidence semantics. Its exact retained body is in `585012cbc6b47cb332222c2784481567a482c8a5:recovery/contracts/original/issue-209-comments.json` (SHA256 `98a08af52a729ff27a22a88bcf4500f4aa53206cf16086ba0e60446ee9f5e4dd`). Commission Section D.5 at `e4cba42cb5704f00b78d64e43f5da88501c28229`, `PRO_UNIFIED_COMMISSION.md` line 148, requires identifying the first failing predicate, retaining permitted evidence, reusing unaffected qualification and making only justified corrections. It prohibits automatic protected retries and UNKNOWN replay. These are the correction's scope; no separately worded failed-leg clause is invented.

Actual run 43703658937 completed both full routes with exit 0, then its separate receiver returned 1. The observed outer failure is `FULL_PAIR_NOT_COMPLETELY_RECEIVED`; the actual failing relation and witness are unavailable. The old adapter wrote receiver stdout/stderr privately but refused `rc != 0` before reading the already-existing closed public `RECEIVED_PUBLIC.json`. Its final seven-file public artifact retained only the prior unreceived result. This correction addresses that demonstrated evidence-retention defect only. It neither repairs nor labels the underlying comparison cause, and it cannot recover the missing actual proof body from the completed run.

## Frozen source

- Base and sole parent: `8165a1edbd057aa59faa16e97a61ad1aabbd1e18`.
- Candidate: `5615fbd71268297d95a909446cdd6b05259f4fce`; tree `72a7ef2628180f240fe20a9d2a02016184c52df4`.
- Worktree: `/workspace/scratch/0269e6626329/g2-receive-retention`; tracked clean immediately after the two-file source commit.
- `qualification/dg16-r5-full-g2/run.py`: nine inserted production lines, 84,859 B, SHA256 `e8576425bcbb260e3d2c21c11e510d51f0549756ab0b8dcc14cfdce7a96de15b`.
- `qualification/dg16-g221-production-integration/test_no_supplementary_export.py`: 111 inserted lines in the existing test file, 13,279 B, SHA256 `343a22b49069de77b123fab54ebf09c2b8fa209d9606cea7bba1650bc4d62898`.

On a nonzero receiver return, the adapter attempts its existing bounded typed `read_pair_summary`. A valid summary is placed in the existing `PROBE.result`, with disposition `VALIDATED_UNACCEPTED_NONZERO_RECEIVE`. Missing or malformed summaries leave the prior result intact. The same original `need(rc == 0, 'FULL_PAIR_NOT_COMPLETELY_RECEIVED')` immediately follows; no later currentness, receiving award, live review or acceptance path is reached. The existing schema, public evidence channel, 49,152-byte read bound, equality requirements and receiving guards are unchanged.

## Focused executed controls

Only these two controls ran, once against the old adapter and once against the correction:

1. `DirectPairCallerTests.test_nonzero_receive_retains_valid_false_proof_without_acceptance`
2. `DirectPairCallerTests.test_nonzero_receive_malformed_summary_preserves_original_refusal`

The existing actual public-summary writer and typed reader consume explicitly constructed false-proof shape inputs. All process/effect calls remain stubbed. No synthetic body is represented as historical or accepting evidence. The controls verify no post-receive currentness call or receiving award occurs, and the original refusal remains in both cases.

The RED invocation returned 1 in 0.284374 s: the valid-summary test demonstrated missing `PROBE.result` (KeyError), while the malformed-summary refusal control passed. The GREEN invocation returned 0 in 0.326346 s: two controls passed. Both raw output pairs and exact JSON records are retained beside this record. Syntax compilation of the two changed files passed and `git diff --check` returned 0. Previously qualified full suites were not repeated. No native, model, provider, protected or original accepting run occurred.

## Pin closure and limits

The old exact protected-run workflow still contains 19 old adapter hash guards. Four historical decision/review JSON bodies and the historical source-review/readback documents also name the old hash. They remain unchanged; they truthfully describe the old candidate. The new source does not meet those old pins, and this source-only correction is not a runnable protected admission. A later current-source binding must use the independently reviewed new digest and actual applicable authority; it must not rewrite old approvals or reuse spent grants. `SOURCE_FREEZE.json` lists the exact seven affected dependency paths.

Independent review is pending. The actual failed relation remains UNKNOWN. No G2 or whole-cell acceptance is awarded, and no retry is proposed by this source record.
