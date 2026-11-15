# DG17 final source CI receiving — run 43686248655

**Disposition: independently received and qualified at source-CI scope. Both jobs succeeded. The actual Windows fixture passed all 14 controls; Linux passed all 29 source methods and all three deterministic modes.** This record confers no native grant, original acceptance or closure authority.

## Exact run and source

[GitHub run 43686248655](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/43686248655) is attempt 1, triggered by a push to `engineering/pro-executor-dg17-source-20261115`, with provider status `completed/success`. It was created at `2026-11-15T06:36:57Z` and updated at `2026-11-15T06:37:33Z`.

The event, both actual checkout log outputs and both generated PINS records identify published commit `a297957be11feb494c0ec467235794a1e0c54751`, tree `b08dc4ecf4028beeedb579a312eccae23cb5d863`. The provider commit has sole parent `c2faca3a5bccf26b4571fddbece4d420385c86b5`. Local immutable `3304d04a43dc64d6cbc2e0ccc45b1503574238a1` has that exact tree; its only additions to reviewed integration `a18b2f2d` are the two previously frozen integration-review files. The six workflow/builder/generator/test/rehearsal owners remain byte-identical to reviewed source `0655cfa8`.

Actual jobs are Windows `132727226807` and Linux `132727227047`. Both checkout, test, artifact-retention and completion steps succeeded. Checkout is branch-based, so this receiving binds its observed `git log -1 --format=%H` output and generated HEAD/tree, not merely the event SHA. Provider logs show Contents/Metadata read permissions. The fixed workflow remains push-only for this branch, with pinned checkout/upload actions and bounded jobs.

## Actual Windows fixture results

The Windows job used the generated `stage_b.py` and the exact frozen fixture source on Windows Server 2022. Its artifact ends `CASES 14 FAILED 0`: three intended positives and eleven intended refusals, with no setup ERROR. Names, expected outcomes and refusal reasons equal all fourteen literal source case declarations.

| Control | Actual result / intended predicate |
| --- | --- |
| Driver creates a new private store | PASS |
| Re-check of driver-created store | PASS |
| Independently constructed protected DACL | PASS |
| Administrators grant | REFUSED: another principal `S-1-5-32-544` |
| Everyone write | REFUSED: another principal `S-1-1-0` |
| Everyone read-only | REFUSED: another principal `S-1-1-0` |
| Inherited Users write | REFUSED: DACL is not protected |
| Inherited Users under otherwise private parent | REFUSED: DACL is not protected |
| Missing directory | REFUSED: open failed, winerror 2 |
| Junction to a private target | REFUSED: junction/link/reparse point |
| Unprotected DACL with user+SYSTEM inheritance | REFUSED: DACL is not protected |
| `create=True` on an existing directory | REFUSED: fresh-create failed, winerror 183 |
| Regular file | REFUSED: not a directory |
| Deliberate different owner | REFUSED: Administrators SID is not current user |

The rows contain **30 independent owner SID observations**: 29 equal the current token user; the final observation independently confirms the deliberate Administrators owner before its intended refusal. All observations equal their stated expected owner. There are **14 successful private user+SYSTEM baseline observations**, including parent/child preconditions before inherited-access mutations and the private target before junction creation. Source sequencing keeps setup failures in ERROR, outside qualifying refusal results.

Each positive returns a protected DACL with exactly two entries: the current user and SYSTEM (`S-1-5-18`), both FullControl mask `0x001f01ff`, flags `3`. This run supplies actual execution evidence for the complete fresh-DACL fixture replacement and its independent module-free owner readback. The fixture's fixed Windows PowerShell executable is distinct from the workflow's `pwsh` wrapper; exact Python/Windows PowerShell/CLR binary-version identities are not printed here and are not promoted into native host admission.

## Linux source and simulated lifecycle

The retained log contains the exact 29 methods declared by the frozen `DriverBundle` class, all `ok`, with `Ran 29 tests in 0.168s` and `OK`. A pre-existing invalid-escape SyntaxWarning is retained without altering the passing outcome.

| Mode | Actual elapsed seconds | Received outcome |
| --- | ---: | --- |
| Native boundary | 5.771470837 | Source steps 01–10 pass; stop before native appserver creation |
| Full | 8.165903833 | Deterministic A/B lifecycle passes with simulated native seams |
| Blocked hook | 8.15491546 | First nonpass contained and cleaned up in simulation |

The boundary result has twelve source receipts because step 06 includes initialization/activation substeps. Full/blocked results have nineteen Stage A source entries and eight Stage B entries. Their native RPC/model traffic, grant/reviewer inputs, selected native events and Linux private-directory substitute are explicitly simulated. Full and blocked record known teardown only in simulation. Logs and retained result objects agree. Zero genuine Codex turns and zero native appservers are recorded in every mode; Linux does not exercise Windows custody. Native-shaped `ONE_ACTUAL_SELECTED_NATIVE_ALLOW...` wording in the reused driver remains inside the explicit simulation notice and earns no native credit.

## Artifact and producer readback

| Retained artifact | ID | ZIP bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Windows source controls | 14150317766 | 3,351 | `14df48f5cd170301efa114f361ebfcf1a1399f91631c418e3fc6852ada77136e` |
| Linux source lifecycle | 14150851650 | 11,013 | `1b9fb65d13a011c64f5fd4c2d2df5316e1a7c4f71b99665ae9d843f911cfac28` |

Both retained ZIPs match fresh public provider digests and acquisition receipts. Reading each compressed member verified CRC and exact equality with all **15 retained members** (three Windows, twelve Linux), including lengths and SHA-256 values. The root catalog equals the fresh raw artifact-catalog object. The dedicated artifact adapter omits `node_id`; this shape difference was resolved against the raw provider metadata, without an archive GET. Acquisition intents/receipts record one body GET per artifact and no automatic retry. This reviewer made **zero archive-body GETs** and performed no test, workflow or native rerun.

Both complete PINS documents contain ten generated-file descriptors, match their rebuild-log summaries, bind the exact published source and retain `limits_unchanged=true`, `native_admission=false`, nine unresolved inputs and all fourteen original UNKNOWN differences. All ten historical input hashes match the frozen source inputs. Windows operation A is 18,437 bytes, SHA-256 `6f242b5ba95270a22ff7d5760fec0cebd30e139868a3e3a593fca36355074a97`; Linux operation A is 18,684 bytes, SHA-256 `987b2e5bb80c887477dab2f0610a66f2de45d4d0b6a64e283c5c2e9330c187f4`.

The unchanged builder verifies generated files through its seven-field file-identity/digest reader before emitting PINS and checks generated command/operation pin closure. The workflow invokes the rebuilt output; historical pre-generated carriers are not substituted for it. The unchanged rehearsal guard restricts inspected direct launches to exact Python/Bash/Git identities, permits only the two specified owner Bash scripts and refuses app-server invocation. This is evidence about these inspected execution paths, not a claim of a universal process sandbox.

**Receiving ceiling:** these artifacts contain PINS, aggregate control/lifecycle outputs and simulation notices. They do not upload the generated carrier bodies, full operation bodies, per-command source receipt bodies or POST_A/POST_B bodies. This receiving verifies the retained descriptors and producer/results boundary; it does not claim independent body receipt of absent files. The nine unresolved host inputs and fresh final native authorization prerequisites remain unresolved.

## Preserved history and authority

This run resolves pending actual Windows execution for this source candidate. Earlier failed runs remain failed and are not regraded: the initial identity refusal remains unexplained; wrong-owner interceptions, Get-Acl module failure, residual Administrators and residual Creator Owner fixtures retain their original dispositions. Prior successful Linux simulations keep their original limits.

No fresh native grant, actual A/B Codex episode, original custody receiving, native acceptance or closure was performed or awarded. All fourteen original custody differences remain UNKNOWN. Public provider records, decoded job logs and the exact retained input identities are frozen beside this report and bound by the accompanying independent receipt.
