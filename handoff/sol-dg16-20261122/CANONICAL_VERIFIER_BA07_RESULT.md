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
