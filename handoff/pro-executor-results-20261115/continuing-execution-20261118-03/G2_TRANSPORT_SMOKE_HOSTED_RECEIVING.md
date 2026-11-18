# FINAL — Independent receiving of the hosted G2 transport smoke

**Decision: PASS — TRANSPORT ONLY.**  
**Reviewer:** `/root/g2_smoke_cold_review`  
**Authority:** `NONE`  
**Blocking receiving findings:** none at this scope.  
**Date:** 2026-11-18.

This separate receiving report preserves the earlier source review unchanged. It is an ordinary engineering judgment for root to consume, not an original acceptance decision or formal audit record. No rerun, branch/ref mutation, original control consumption, full pair, controller operation, or acceptance award was performed.

## Independently reacquired evidence

I reacquired provider run metadata, the latest-attempt job/step metadata, artifact metadata, the smoke branch ref, the complete integration commit delta, the job log, and the run collection filtered to the exact integration commit. I separately downloaded the actual artifact through the provider and fetched five source files at the immutable integration SHA. These readbacks are retained in `provider/`; they do not rely on root's receiving summary.

| Binding | Independently verified value |
| --- | --- |
| Repository | `theislampill/IMPLEMENTAUDIT.md` |
| Integration commit | `3fcf7146ec2ff086323d20170f995137ca4be9eb` |
| Sole parent | `9a349423b6ca3dda18115a07ed41b63970bc8b77` |
| Tree | `fd5a2c73cf08f207b27ed2e139708461b57938b9` |
| Smoke branch | `engineering/g2-production-transport-smoke-20261118-01` |
| Run / attempt | `44267730042` / `1` |
| Job | `134676323610`, `transport-only` |
| Artifact | `14410149163`, `g2-production-transport-smoke-44267730042-1` |
| Terminal result | Run, sole job, and every reported step: `completed` / `success` |

The provider reports run number 1, attempt 1, no previous attempt URL, a push event, and no associated PR. The current smoke branch ref still names the exact integration SHA. The run collection for this SHA contains exactly this one workflow run; no full-pair workflow is returned for it. The run's metadata interval from start to last update is 12 seconds, within the reviewed bounds. The job log reports image `ubuntu-26.04` and contents permission `read`.

## Integration matches the frozen review

The remote commit has exactly four changed files: the new smoke workflow, new smoke script, repaired `live_control.py`, and its new transport regression tests. Existing workflows, the unchanged utility, and acceptance pins are outside that delta.

| Remote file | Verified SHA-256 |
| --- | --- |
| `transport_smoke.py` | `baa97ec17871541cafdbf7a0f118d45c3704bf5a9389cc4c86c508dea192471b` |
| `g2-production-transport-smoke.yml` | `7beac6d601cff224540f64b71c72d722cd3ff73e4765fedcec24c85d6966de23` |
| `live_control.py` | `cd8262defc85c2541632fe00e51bc78c804b13a3a8a4501e39300b4269f866ff` |
| `host_utility.py` | `02a15dc96ecce23e14a3a84bca880aa536d79fffc4f6d6160835cb4ba97a19b5` |
| `test_live_control_transport.py` | `963b21c7527e3d163c327dc42c9af35b2f79ff3f5c15737703dac35cb4980e2f` |

I also recomputed each Git blob SHA from the downloaded bytes and joined the four changed blobs to the provider commit delta. The smoke/workflow/dependency hashes exactly match the frozen source review. Every file in the earlier review's evidence manifest was rehashed and remains unchanged.

## Artifact and result integrity

The independently downloaded ZIP is 1,470 bytes and has SHA-256:

`a2def234f35eb93821e541432d234c364df6c50618a975d40775b24c2887a47e`

That matches the fresh provider artifact digest and the upload digest in the independently reacquired job log. The ZIP passes CRC verification and contains exactly `RESULT.json`.

The extracted result is 4,248 bytes and has SHA-256:

`e954aa82bc50f58de306424846f16693051e38e8fe66fe56d2eef26840966f00`

It exactly matches root's retained result bytes. Its parsed value also equals each of the two actual structured records in the job log: the script record and final evidence record. Duplicate JSON keys and nonfinite JSON values are rejected by the independent checker.

## What the actual captures establish

The result names the exact run, attempt, integration SHA, source parent, smoke digest, dependency digests, public repository, fixed control branch, and expected control commit `0fc8b8a0343925e72b24f4f98daad8ba988bd045`. Source hashes were verified, the subreaper was enabled and read back, and the recorded attempted operations are exactly `init`, `ls-remote`, and `fetch`.

| Actual capture | Exit | Streams | pidfd | Cleanup | Retained child statuses |
| --- | --- | --- | --- | --- | --- |
| Bare init | 0 | Complete; stdout/stderr empty | Acquired | ECHILD true | 0 |
| Fixed HTTPS discovery | 0 | Complete; stdout 93 bytes; stderr empty | Acquired | ECHILD true | 0 |
| Exact-commit HTTPS fetch | 0 | Complete; stdout/stderr empty | Acquired | ECHILD true | 1, exit 0 |

All captures report no timeout, output overflow, or internal failure. I recomputed the empty-stream digests and the exact discovery digest. The expected discovery bytes are the fixed commit, a tab, the complete fixed control ref, and a newline; their SHA-256 is `752ebcbe43c43352c2f4545ae9891cb336de78fff7192ae28f22c8c5af5bbfa2`, matching the actual record.

All cleanup-status digests were independently recomputed using the exact production canonical encoding. Fetch cleanup retains one additional child status, PID `2510`, return code `0`, with digest `b719543139cd7df8fe28feb3a313f0d0a5da3c253420bd9305050e4a4111fec8`. The production source waits for its direct subprocess before this cleanup census; the additional terminal child is consistent with subreaper adoption. The record proves the retained additional-child reap and final ECHILD, without asserting an unrecorded descendant identity. No pidfd signal was needed in any capture.

The result is `TRANSPORT_OBSERVED` with code `FETCH_COMPLETED_STOPPED_BEFORE_PARENT`. Given the exact reviewed gate, fetch success raises before returning into the production `hold` function. No parent-reading command, payload validation, final control reread, or original consumption boundary follows. All four forbidden control-output names are recorded absent. All acceptance, full G2, G132, full-pair, replay, original-consumption, branch-writing, and retry flags remain false.

## Verification and remaining boundaries

`verify_received.py` completed with exit 0 and **97 passing assertions**; details are retained in `checks.json`. These checks validate already acquired evidence and perform no hosted operation.

The prospective hosted transport gap is now resolved **for this one run and these exact source bytes**. The original local executor's missing procfs interface remains a historical limitation of that local experiment. This hosted result demonstrates successful completed-command cleanup and one additional terminal-child reap. It does **not** exercise live-child signaling, timeout cleanup, maximum child-population limits, arbitrary process trees, or every production cleanup failure path; all pidfd-signal counts are zero.

Post-fetch branch currentness remains unproved because the reviewed smoke deliberately has no post-fetch control-ref reread. No original private-input liveness, review window, parent/payload validity, full-pair result, original acceptance, full G2, or G132 is established by this artifact. The provider's terminal success does not broaden that boundary.

**Final receiving judgment: PASS at the exact read-only transport-and-successful-cleanup observation scope. Root may consume this judgment within the existing commissioning constraints. No acceptance award or new execution authority is granted.**

Provider references: [run](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/44267730042), [job](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/44267730042/job/134676323610), [integration commit](https://github.com/theislampill/IMPLEMENTAUDIT.md/commit/3fcf7146ec2ff086323d20170f995137ca4be9eb).
