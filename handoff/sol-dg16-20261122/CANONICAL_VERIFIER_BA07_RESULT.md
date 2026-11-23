# DG16 canonical verifier task on `ba07a21d`

The real DAG child reached the eval harness, exited 1, and left NEXT blocked. This occurrence binds `ba07a21d904f0b0a10f7b7b957ccf9c10a76cd13`, tree `f73966558734868bb0de27a4a8d250529afeea11`. It precedes both the awarded M5 freeze and the retained property comparison fix.

| Observed field | Value |
| --- | --- |
| Issued dispatch | `06d95532a2df42e3a0e74ac9040f5cd72932ec39cbedd52fcdad8ec9ff3b0950` |
| Issued graph digest | `20fbca47e761bd836cefc4a6943874d52c74e4cdff90a0362d8ec492806fdf9a` |
| Issued task input digest | `05413b027bdd7ef98e5f35cd5d178bb27f9d78a88d5b95a8bf95678d19865b2c` |
| Received capture digest | `1191f37aca1de2b464ff36be16a44d53dbe720b7498c881922a83c8b64b714fc` |
| Raw stdout SHA-256 | `18653013d2b2c31899e759924e684947ea09b961c518bf000b58a471315e1f6b` |
| Raw stderr SHA-256 | `86af2c47500f919e2f9a29b44a4765379a946b899022f021d58820da0ef466ee` |
| Node results | 119 mapped, 91 registered tests, 100 PASS, one FAIL, 18 UNSETTLED |
| Terminal result | Exit 1, JOIN FAIL, NEXT BLOCKED, authority NONE |

Source and environment bookends compared equal. The private mount namespace left the outer Git directory unchanged. The first failed node was `COMMAND:tests/eval-harness.test.sh:0`. The capture shows `eval/test_provisional_integration.py` attempting to resolve the candidate's first parent to scope a review. The shallow checkout had depth one. The later registry checker did not run, so all five property rows remain `UNVERIFIED` in this occurrence.

The existing named `tests/eval-harness.test.sh` passed separately in a clean depth-two checkout of the same commit and tree. It resolved parent `e830a81a9c50d3958343b9e4c0218d85008ae83e`, reached `PROVISIONAL-INTEGRATION-PASS` and `HISTORICAL-READJUDICATE-PASS`, printed `eval-harness.test: ok`, and exited 0 with an empty post-test Git status. Its stdout SHA-256 is `fd686b8e494ba0570aff5d65a618fba34a728addc09c08efda27632ef0eb176a` and stderr SHA-256 is `62a4b34785b7ffffda71e176701c6dde40908956e2401fe9d20f4fd313e33304`. This resolves the observed checkout-depth failure for that named control. The original run's 18 unsettled nodes and failed JOIN retain their own dispositions. A later full canonical candidate requires depth two and fresh evidence for the nodes it actually executes.

The named portable property and interruption controls passed on `85eab42c0b0abfd8a551ffaa46901ba64e1f4403`. The preceding comparator accepted a missing property. The successor refused missing, duplicate, unknown, reordered, stale and falsely settled rows before creating comparison output, and the restored exact record passed. Its legacy and DAG interruption controls retained matching stdout, stderr and signed exit −15, a NONVERDICT JOIN and a blocked successor. These results exercise the registry-checker slice and the portable task. Whole V02, V04 and M6 are still open. [Original criteria](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/585012cbc6b47cb332222c2784481567a482c8a5/recovery/contracts/original/R0035_209_CRITERIA_INDEX.md)

## Successor setup refusal

On `75ebe0ac5ae8ea3c20e81b581cbc12c2fa5983be`, tree `d37522964f2cebb94822d790825c06f1c4c1ee0a`, a separate depth-two task first failed at `COMMAND:tests/continuity-contract.test.sh:0`. Its temporary private mount had mode 0700 and the ordinary user received permission denied for `.git`. The named continuity control passed on the same source after making only that temporary mount traversable. The failed capture retains exit 1 and stdout/stderr hashes `0768c320f3eb438faaac781c39239e22194c844782d53582f1aeb23a8264dded` and `7babf797bee05112a5a5067bf1caf080627b3b80f65ece6ef5cc535499748aa4`. The running `f88a53d5` occurrence uses the corrected mount and its own capture directory.

## Depth-two terminal result

The `f88a53d5a0223a2784f1cf248500c435b5d1b695` task on tree `df333ba80b68d221045f1355d0907b372bd33884` finished with 64 PASS, one FAIL and 54 UNSETTLED among 119 mapped nodes and 91 registered tests. Rotation passed. The first failure was `COMMAND:tests/composite-source.test.sh:0`. Its C5 current-source receiving rejected the changed `scripts/work-graph-completion.py` body. The task closed with exit 1, JOIN FAIL, NEXT BLOCKED, all five property rows unverified and equal source and environment bookends. Capture digest `91bca800a218daa16dd937e5316459da282469dff121dced26233dcd250c839d`.

The repair restores completion blob `be996a63c82e97325b25f07315b852fe7f7e5d48`, byte-exact to the selected C5 preimage. The verifier task retains its read-only journal validation. On the actual shared verifier composition with the scan repair, the named task check passed and composite receiving advanced to a new fixed-member refusal at `scripts/qualify-work-graph-prefix.py`. The composite suite retained ten errors, two historical-profile failures and two skips. The historical profile failures compare the live DG18 A5 hot projection to older Windows bodies. These two prerequisites need a shared-candidate decision. No C5 tuple was edited or selected by this work.

## C5 source selection after the scan fix

The maintained hosted source reader now selects a distinct V13 tuple for the repaired registry. The captured tuple binds the candidate compiler `d9fb8b1f`, maintained qualifier, exact repaired prefix and finite-leaf source, and its v4 producer program selection. V12 still resolves its physical compiler, prefix and qualifier preimages under `test-support/r5-verifier-scan-history/v12-source`. Earlier source tuples, limits and the completion blob remain exact. The qualifier exposes separate repaired prefix and custody-append selectors.

On the published `2059984e` base with the exact owner-local DG16 repair, the maintained source reader loaded V13 without dispatch, V12 loaded its retained members, and a mixed prefix refused before dispatch. Independent mixed-registry controls refused for both prefix and finite-leaf profiles. The 83-test composite suite had two skips and only the two DG17-owned Windows history failures. The canonical task check, four current custody controls, 11 historical fixture checks and 11 property checks passed. The ordinary canonical no-match route passed PRELUDE and reached the controlled downstream stale diagram. These results supply source compatibility and leave C5 effect dispatch and original qualification open.

The exact repaired shell also reached the scan output descriptor acquisition with an ordinary-process descriptor ceiling of ten. It exited 1 with the expected output-open diagnostic, and the separately owned temporary directory was empty afterward. The earlier actual read-error and match controls remain retained.

DG17's immutable local composition `f894aa80311a7591f00d4b41f0e5f9e1347b9d7e` passed its first 84-test composite suite with two skips. Its second suite exposed incomplete V13 test fixtures. The repaired `tests/c5-current-source-receiving.py` now acquires the exact current tuple, materializes V10/V12 from their retained compiler and builder inputs, compares the released V12 declarations, and preserves mixed compiler, profile and base refusals. In the verified `2059984e` base with the exact DG16 deltas, all 18 exercised source-only tests passed. The two existing optional stale-loader cases remained skipped. The paired composite gate on DG17's next shared commit remains pending.

## Authorized successor dispatch

DG17's complete composite passed 106 tests with four skips on `de4b0d2059ba9faca814d7df89f6e1a9a6567582`, tree `798680769d2e42ec60a5410ee43f53e4a2fc4615`. Root authorized one ordinary canonical verifier run on that subject. A clean detached depth-two checkout verified the candidate, tree and first parent. The task issued dispatch `00cb508b897ea7146e0eb1a1d31f4273a59d19e70eb72f7b56de94156c522edd`, graph `6d0232346f46c9424c0f0c795c5cf2417633c5350f130dfb1028f16de8e7334c`, and input `faa49a22bfc33aeebf592b496ebd489836bcc063dfaf91aaa3c24c394a1eb92b`. The DAG is executing with the v3 required-file and version-property scope, under the ordinary user in a private mount namespace. Terminal settlement remains pending for this single occurrence. [Published composite](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/a5075ea4fdb0ff6a203f510f91a1858ae5d18815/handoff/sol-dg17-20261122/CONTINUATION.md#shared-verifier-composition-de4b0d20)

The single occurrence finished exit 1 after 96 PASS, one FAIL and 22 UNSETTLED. The source and environment bookends compared equal. All 394 version and required-file properties passed and five downstream registry properties remained unverified. JOIN failed and NEXT stayed blocked. The first failed node was `COMMAND:tests/work-graph-verifier.test.sh:0`. The fixture's original scan-argument extraction searched for the pre-repair conditional and raised StopIteration before its benign and matching controls. The retained capture digest is `907bacb08fbbad351e198d1acd4ec8c0f89e535ca2e8ed74ff88c925cd80d553`. The corrected named DIST consumer check passed using the actual repaired registry and both original control inputs. The terminal failure stands for this occurrence.

## N07 C5 source selection

The maintained reader on exact `bf8b986e7d686a79aff555d18324490f74db668a` initially refused the changed compiler. The V14 source selection binds its 261,923-byte compiler, SHA-256 `0176a773fc35bdd674646f667a373c7295d8c6fe29867d0aa675adc9c5366a14`. The V13 tuple and its 261,843-byte compiler, SHA-256 `d9fb8b1f2fb706afd688e59f1d186ee26aa75e1bef396d071e9b0ce4c700c576`, remain bound to the retained physical source. The previous loader was retained and its declarations and selected V13 tuple compared equal.

On exact `bf8b986e` with the owner-local delta, the maintained reader loaded the current compiler, the historical reader received the retained compiler, and mixed source refused before dispatch. The named composite reader, all 18 exercised C5 receiving cases, and 11 verifier-property tests passed. The two existing optional C5 cases skipped. The tests performed source receiving only.
