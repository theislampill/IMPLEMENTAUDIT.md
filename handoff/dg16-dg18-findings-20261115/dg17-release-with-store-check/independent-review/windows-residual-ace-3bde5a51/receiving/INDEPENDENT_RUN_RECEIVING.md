# DG17 independent receiving — source run 43679794953

## Disposition and scope

**LINUX_SOURCE_RESULTS_AND_WINDOWS_OWNER_READBACK_RECEIVED; TEN_WINDOWS_BASELINE_ERRORS_PRESERVED.** The overall provider run failed. Linux's three deterministic modes and 24 focused methods succeeded at the exact run source. Windows demonstrated the direct .NET owner query on 23 recorded readbacks and four intended case outcomes, then retained ten setup ERROR outcomes. The complete fourteen-case Windows population is not qualified.

Reviewer: `/root/dg17_independent_review`, distinct from the author, delegated by root controller `pro-executor-01`, root-reported verified generation G0005. This is source-only receiving, not a formal audit-assess transition or native receiving/acceptance. No artifact body was reacquired and no lifecycle was rerun for this receiving. The separate one-command fixture correction is reviewed in the parent directory and receives no retroactive credit from this run.

## Provider and source binding

| Binding | Independently verified value |
|---|---|
| Provider run | [43679794953](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/43679794953), attempt 1 |
| Event / branch | push / `engineering/pro-executor-dg17-source-20261115` |
| Status / conclusion | completed / failure |
| Created / updated | `2026-11-15T05:08:44Z` / `2026-11-15T05:09:19Z` |
| Published source commit | `50c7fd7e279cd1f97345941d1ef13d6d76412cd8` |
| Published source tree | `df9b72c932a0b60dca918232567e725fa0585771` |
| Local commit with the same tree | `4db726a4f5c7f6429589a941977e233ece967e91` |
| Linux job | `132707719487`, success |
| Windows job | `132707719628`, failure |

Actual GitHub run, commit, job and artifact metadata and decoded logs were read independently. The checkout log in each job names the exact published commit, and both retained PINS records bind that commit and tree. This resolves the workflow's branch-checkout source binding for this run; event SHA alone was not used as proof of checkout identity.

| Artifact | Bytes | Provider/archive receipt SHA-256 |
|---|---:|---|
| Linux `14148315355`, `dg17-linux-source-only` | 10890 | `3d14e32df915506fe50516088566b49ecbcbb6dc7dd561347fdc6bf4186a4a32` |
| Windows `14148045576`, `dg17-windows-store-source-only` | 3314 | `69abaf53d164e88ca49c10f5c846cb887f01d9b0a77abdf08aedb295dfb729fc` |

Both upload logs confirm those exact artifact IDs, byte counts and archive digests. The retained metadata objects equal actual provider metadata, and the retained one-shot receipts equal their embedded packet objects. All fifteen retained member byte counts and SHA-256 values were independently recomputed and matched. The archive bodies were not reacquired; archive digest agreement is supported by provider metadata, upload logs and the already retained one-shot receipts.

The author's receiving packet is 42,735 bytes and retains SHA-256 `b2abc0db85b8c0faa3708b6d9b8e3ef642c42c45468abdf5471c6c03d5fad03c`. Its Windows rows, Linux results and PINS records agree with the retained member bytes. Exact member identities and provider observation hashes are in the companion machine receipt.

## Linux result received

| Mode | Actual recorded result | Seconds | Result JSON SHA-256 |
|---|---|---:|---|
| native-boundary | SOURCE_STEPS_01_TO_10_PASS_NATIVE_BOUNDARY_NOT_CROSSED | 5.298220503 | `9eb97621d7d23091343a34e0ff1ad4104866b51a411611a51dfc347b7085519d` |
| full | DETERMINISTIC_LIFECYCLE_PASS_WITH_SIMULATED_NATIVE_SEAMS | 8.153142539 | `4258704e15b5e6c24e3f0963cef2518aaeb28f69b3661fb4571a4a2058875986` |
| blocked-hook | FIRST_NONPASS_CONTAINED_AND_CLEANED_UP | 8.082771011 | `e46b133bf341499ed5a6af0a13f4684be81511b55da1467345d3051e4554586b` |

The hosted focused suite log shows 24 methods, 0.146 seconds, OK. The native-boundary stop is its deliberate synthetic boundary sentinel after source steps 01–10. Full and blocked-hook records retain known cleanup in simulation. Native-shaped status labels in the full transcript are simulated results; each summary records authority NONE, zero genuine Codex turns, zero native appservers, no actual native acceptance, no Windows custody, and fourteen original UNKNOWN differences.

Linux PINS.json is 3935 bytes, SHA-256 `0c297f0084e25275a195c6d4de33554ee24804e5408bcdcbbcd77770770bfdb8`. It reports operation A 18684 bytes, SHA-256 `9db06e300dbbb86d8fefe0aad4f3216c33b4dc5cfedfc7ab5dccf7b86079768d`, nine unverified inputs, unchanged limits and no native admission.

The received population contains summaries, logs, simulated markers and generated pin records. It does not separately contain every generated carrier or per-command POST_A/POST_B body. This receiving does not promote pin records into independent receipt of absent bodies.

## Windows result received

Windows rebuilt and generated PINS under the unchanged seven-field identity guard. PINS.json is 3851 bytes, SHA-256 `ee440d0526b4e26eca88852f89186d69c35eb2b31c2ab23500cc3935922d155e`, with operation A 18437 bytes, SHA-256 `4ce157d8a2366cd5f98bc8f8bcbecc81c86f0f9e275f21bd166cd76e434a62f7`, nine unverified inputs and unchanged limits. This successful build does not explain the earlier identity refusal.

The actual store-custody log is 12700 bytes, SHA-256 `c78eee46c626be1f4f6700c488d304edb685f5eeab21026597eaf823e8395fbe`. Its footer is CASES 14 FAILED 10. The direct .NET query generated 23 recorded owner-SID preconditions; every owner equals the expected current user SID. These are 23 readback observations, not 23 distinct fixtures. There is one recorded complete private-baseline precondition.

| Actual case population | Outcome and credit |
|---|---|
| Driver-created store creation | PASS, intended positive |
| Recheck of driver-created store | PASS, intended positive and complete private baseline |
| Missing directory | REFUSED for `open directory failed (winerror 2)`, intended negative |
| Regular file | REFUSED for `not a directory`, intended negative after owner readback |
| Manual protected-DACL positive | ERROR at private baseline; no positive credit |
| Administrators, Everyone write/read, both inherited Users, junction, unprotected DACL, existing-path create, wrong-owner cases | Nine ERROR outcomes at private baseline; no intended negative credit |

The first failing baseline reports an Administrators allow ACE for `S-1-5-32-544`, mask `0x001f01ff`, after current-user ownership was verified. Source inspection at the frozen run commit shows that unsupported ACE type and inherited-entry checks precede the foreign-SID branch. The non-inherited allow characterization is therefore a source-based inference from the reached branch. No detailed origin of that residual ACE is inferred.

Ten cases stop before their intended positive or adverse perturbation. The Administrators negative's baseline error cannot count as its intended refusal even though the same SID appears in both messages. All ten remain unqualified setup errors. Only two of eleven intended negative predicates were reached.

## Preserved history and authority ceiling

The earlier file-identity refusal remains unexplained. The earlier seven negatives intercepted by wrong-owner checks remain unqualified for their intended predicates. Run 43678583519 retains thirteen Get-Acl module-load setup errors and zero verified preconditions; its underlying module-load cause remains unknown. The current direct .NET observations do not regrade that failed run.

The next fixture correction requires its own actual Windows execution and receiving. This run creates no native episode grant, original14 receiving, DG17/R0037 acceptance, or closure. Original fourteen custody differences remain UNKNOWN. Final location/tool/package identities, exact operation receiving, fresh owner grant, authentic A/B turns, independent post-A receiving, POST_B, T12 and custodian requirements remain in force.

Actual Windows/model/lifecycle invocations by this receiver: zero. Remote mutations, source edits and artifact-body reacquisitions: zero.
