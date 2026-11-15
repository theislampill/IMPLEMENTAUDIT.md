# DG17 independent Linux source receiving — run 43677179224

## Disposition

**LINUX_DETERMINISTIC_LIFECYCLE_RECEIVED_AT_SOURCE_ONLY_SCOPE.** The actual
Linux hosted job succeeded, and its three retained results support the intended
native-boundary, full deterministic lifecycle, and first-non-PASS containment
claims with the explicitly simulated native seams. The overall workflow run
remains FAILED because its Windows job failed. This receipt grants no native
admission, original acceptance, release, or closure.

Reviewer: `/root/dg17_independent_review`; root controller: `pro-executor-01`,
G0003. The reviewer independently read provider metadata and decoded job logs,
then hashed the already-received artifact members. No artifact body was
reacquired, no source or test was run, and no native or remote mutation occurred.
Source inspection used the frozen Git object rather than the changing worktree.

## Exact provider and source binding

| Item | Identity/result |
|---|---|
| Workflow | [DG17 offline source lifecycle](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/43677179224), run 43677179224, attempt 1, push event |
| Branch | engineering/pro-executor-dg17-source-20261115 |
| Published commit | `0d262630b826ecf634a44e3b8b9535b46a6dc14c` |
| Local frozen commit with the same tree | `06b22dcfa07cbfed8fc69d922530d05d544d0aef` |
| Tree | `b81b8b30065b6620a5eaff9a21bb087825b217fa` |
| Linux job | 132699780574, completed/success |
| Windows job | 132699780775, completed/failure |
| Overall run | completed/failure |
| Linux artifact | 14147060553, dg17-linux-source-only, 10711 bytes |
| Linux archive SHA-256 | `1be8f2027ede5fbe02c54b53e09fd4b6082d6c5e8f955a02df1a859eb95a8195` |

The provider's commit object gives the expected tree. The Linux checkout log
prints the exact published commit, and its generated PINS names that same
commit/tree. Provider artifact metadata, the upload log's size/digest/ID, and
the original receiving receipt agree. All twelve retained Linux members match
their recorded lengths and SHA-256 hashes. The source-control log records all
18 focused methods passing on the runner.

## Independently received results

| Fixture | Actual retained result | Elapsed seconds |
|---|---|---:|
| native-boundary | SOURCE_STEPS_01_TO_10_PASS_NATIVE_BOUNDARY_NOT_CROSSED | 5.888422223 |
| full | DETERMINISTIC_LIFECYCLE_PASS_WITH_SIMULATED_NATIVE_SEAMS | 9.442584381 |
| blocked-hook | FIRST_NONPASS_CONTAINED_AND_CLEANED_UP | 9.428914913 |

The boundary fixture records clone, checkout, HEAD/tree and controller-absence
checks, claim/initialization/activation, resume/verification/currentness, and the
positive validator through A10. Its driver's STOPPED status represents the
intentional fixture exception before native process creation, not a failed
deterministic predicate.

The full fixture records A through current-controller readback and B through
currentness, initialization, binding, lookup, scoped trust/enable, and final
currentness. The frozen harness requires successful known cleanup, binding
tombstoning with the object still open, and hook disabling before emitting its
success summary. The blocked-hook fixture additionally requires a nonqualifying
Stage B status, a recorded interruption request, and an actual raised error
before emitting containment success. Its retained simulated call list includes
the interrupt-wire action. These are assertions made by the reviewed source
executed in the successful hosted job; the artifact contains summaries/logs,
not every internal per-command or POST_B file.

All three results and their markers retain authority NONE, zero genuine Codex
turns, zero native appservers, and fourteen UNKNOWN differences. The full and
blocked results explicitly deny actual native acceptance. Native-shaped stage
status strings remain fixture outputs and do not establish authentic host
receiving. Windows custody is explicitly not exercised by these Linux fixtures.

| Retained Linux member | SHA-256 |
|---|---|
| native-boundary/REHEARSAL_RESULT.json | `c4d631d4ecfa6a0e29fd65e05306b833c2807976ac306844946f11dadac43060` |
| full/REHEARSAL_RESULT.json | `bea8729a35e1b6b7cebe03a6707d9c7c6fb6617c3deb78e04863116902d028d8` |
| blocked-hook/REHEARSAL_RESULT.json | `5d281fc5259e8987eb1ddcdf11095439dcac9f7924b4d969b603196fe975edc8` |
| rebuilt/PINS.json | `c8f18b44f59794e391b7d6f9cb15504d0422aa0857bda20a4b95ef64651651a0` |
| source-controls.log | `bf8c4096edfdc6c1e2a09ebf9a0ea6d18f69cdcf47fb8e1c0b486915656f8531` |

PINS records the generated operation as 18684 bytes, SHA-256
`415c81735f9e143f72510b622fb6a5c17e5f4ea98baa87428276da63c62e2f39`,
unchanged limits, native_admission false, and nine unobserved inputs. Generated
Stage A/B hashes remain `683c1e0693eeebfd94b39239baa8896b045aeb2e57663876b8e349efe6d5978b`
and `590a92cc09b835a4a50af8e40364cd6337fecc7d0fbbb08b956fdd4c335e0dd1`.
These generated-carrier identities are recorded by the verified PINS artifact;
their raw bodies were not separately included in the received archive.

## Windows observations preserved separately

The second Windows job did generate PINS and reached the real Windows controls.
The unchanged seven-field builder comparison therefore passed on this execution.
That observation does not explain or erase the first run's identity mismatch.

The actual driver-created user/SYSTEM store and its recheck passed. The manual
icacls positive failed because its owner was Administrators rather than the
current user. Seven negative rows returned the expected generic REFUSED value
for that same wrong-owner condition instead of reaching their intended ACL or
junction predicate; those seven rows receive no credit for the intended control.
The log's CASES 14 FAILED 1 count must not be promoted to thirteen independently
qualified custody predicates. The separate fixture correction remains a source
review and future Windows execution task.

The Windows artifact is 14147315042, 2906 bytes, archive SHA-256
`7d56e96fd6d46dd0224dd95e4e1f46b612a75982d5566c37131b7c6834e3fc29`.
All three retained members were independently hashed. Store-custody log SHA-256:
`669574b9d62dbca1f017e7d47f390bce9fc1a0becc110c90766f87819920661d`.
Both Windows failure facts and the earlier Linux failure remain preserved.

## Receipt and remaining authority

`INDEPENDENT_LINUX_RECEIPT.json` carries the provider binding, all fifteen
verified artifact-member identities, frozen source hashes, complete source
result summaries, PINS, and the seven unqualified Windows negative cases.
Its SHA-256 is
`ab52f0740fad0a38a76e12cbe9c90785328643e552c46c919f912b7d64bcf2d2`.
The independently retrieved provider observation SHA-256 is
`179edf82f96afad6dc70dc1c3e054693fbd0b79ab49806b8c510a6609ed22b9b`.

This Linux source result is reusable at its exact unchanged scope. Final Windows
qualification, actual final-location operation and host inputs, fresh written
owner grant, two authentic Codex model turns, independent post-A receiving,
POST_B, T12, original14 receiving, and custodian certification remain required.
No grant is issued or consumed; all fourteen custody differences remain UNKNOWN.
