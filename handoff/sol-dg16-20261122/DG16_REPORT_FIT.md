# DG16 follow-up on the six-field compact report

**Decision.** Keep the current encoder, receiver and delivery contract. The retained evidence establishes that the reported v1 observation could not fit either uncompressed boundary. The proposed compact format's fit and reconstruction fidelity remain unmeasured. This follow-up adds no competing receiver and makes no original DG16 acceptance claim.

## Authenticated result and fixture search

The live GitHub provider metadata binds run `45049052400`, attempt 1 and source `7cbad948f54216617bfa46f3548917104e8f650f` to artifact `14764523685`. The archived carrier matched the provider's SHA-256 `2f013bf1d30ef521c5955b6b0e1068d72b99f551f68577c23a1bfe8ec2bbdc11` and size of 11,775 bytes. All 12 payload lengths and hashes matched its manifest. The 13 uncompressed members total 61,160 bytes. The archived input includes a refusal descriptor for the 2,589,544-byte full report, with SHA-256 `9c2bf817bf78a1074f56b8abd23c0c8e2e9237547914690064c73ee0ad5a548b`. Those full-report descriptors are producer statements. [Provider run](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/45049052400), [provider artifact](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/45049052400/artifacts/14764523685), [archived independent readback](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/2f920bd7c3b70c78c8c105b486a71c8bc4b5426a/handoff/pro-final-20261122/evidence/RUN45049052400_INDEPENDENT_RECEIVING.json).

The complete pinned source tree lists the selected observer, contract, wheel and cache, plus nearby host-profile and boot qualification tests. The tests are for separate predecessors and contain no selected-public static report fixture. The exact ordinary-operation ref has one observed run and one artifact. The results baseline search found no occurrence of the full-observation schema or matching test class in archived source, and the bounded workspace search found no corresponding report or source-test basename. These are limits on available fixtures in the inspected scopes. [Exact source tree](https://github.com/theislampill/IMPLEMENTAUDIT.md/tree/7cbad948f54216617bfa46f3548917104e8f650f/engineering/g132-host-runtime-static-operation), [nearest predecessor tests](https://github.com/theislampill/IMPLEMENTAUDIT.md/tree/7cbad948f54216617bfa46f3548917104e8f650f/test-support/g132-host-profile-successor).

## Fixed caps and necessary savings

The selected inner cap is 1,823,337 bytes. The receiver's fixed cap is 2,097,152 bytes, equal to the entire delivery limit including manifest. The v1 report's stated length exceeds those limits by 766,207 and 492,392 bytes respectively. Removing the wrapper reserve alone cannot fit the unchanged representation. ZIP compression leaves the checks on uncompressed bytes unchanged. [Encoder and receiver](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/7cbad948f54216617bfa46f3548917104e8f650f/engineering/g132-host-runtime-static-operation/runtime_static.py#L1152-L1178), [delivery cap and exact payload descriptors](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/7cbad948f54216617bfa46f3548917104e8f650f/engineering/g132-host-runtime-static-operation/run-owned.py#L175-L200).

For the specific prospective representation from the first return, let `S` be the sum of the six canonical section value byte lengths, each including its canonical terminal LF. Replacing their fields with a single `derived` object of six `{bytes, sha256}` commitments removes `S + 74` bytes and adds a commitment member of size `D`. The proposed v2 schema name has the same byte length as v1. The exact fit equation is:

```text
compact_wire_bytes = 2,589,544 - S - 74 + D
inner_fit requires S >= 766,207 + D - 74
```

At any possible fit, some section length must have at least six decimal digits, since six lengths of at most 99,999 bytes could not provide the required net savings. The pinned canonical encoder yields `D >= 619` at that minimum width. Therefore the six canonical values must total **at least 766,752 bytes** for this particular wire to fit the old selected inner cap. The exact threshold depends on all six length widths. The equation was checked on two canonical maps, including escaped and non-ASCII text. These are accounting controls. The withheld report exposes none of the six section lengths, so even this necessary condition is unresolved. [Pinned canonical encoder](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/7cbad948f54216617bfa46f3548917104e8f650f/engineering/g132-host-runtime-static-operation/runtime_static.py#L49-L64), [six actual recomputations](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/7cbad948f54216617bfa46f3548917104e8f650f/engineering/g132-host-runtime-static-operation/runtime_static.py#L1249-L1267).

## Evidence and consumption boundaries

The exact pinned receiver's early data-only functions refused four inputs without reaching host work or the report's semantic recomputations:

| Control | Actual refusal |
| --- | --- |
| Authentic archived refusal stub | `REPORT_SCHEMA_OR_INCOMPLETE_STUB` |
| Hypothetical v2 schema at the v1 entry point | `REPORT_SCHEMA_OR_INCOMPLETE_STUB` |
| Archived stub relabelled with the v1 schema | `UNEXPECTED_REPORT_FIELD` |
| Raw input one byte above the fixed receiver cap | `REPORT_BOUND` |

The v1 shape requires the six concrete section fields. The adapter requires exact bytes and hashes of every present source receipt file and enforces the manifest-inclusive cap. A prospective v2 would need a separately reviewed encoder, consumer and report identity. The v1 full report cannot receive custody credit from six commitments, even if a prospective consumer reconstructs their logical values. The original G1 and G3 contracts continue to require genuine bound dispatch and consumption and exact applicable evidence packets. This operation was an ordinary `UNQUALIFIED` diagnostic. [v1 required fields](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/7cbad948f54216617bfa46f3548917104e8f650f/engineering/g132-host-runtime-static-operation/runtime_static.py#L969-L976), [original milestone matrix](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/585012cbc6b47cb332222c2784481567a482c8a5/recovery/contracts/SIX_GROUP_MILESTONES.json).

The smallest decisive input for historical size and fidelity is the exact complete report with the stated size and SHA-256 and its pinned contract, wheel and cache. Authentic per-section lengths would settle the size equation alone. A separate retained complete public fixture would permit an equivalence test at its own scope. That test would run the actual six recomputations, compare full canonical bytes and verify the outer delivery total. It would also refuse a discarded observed or closing field, wrong derived commitment, excessive expansion and a one-byte-over wire or delivery. No such complete fixture entered this work, so actual six-field reconstruction and historical fit remain open.
