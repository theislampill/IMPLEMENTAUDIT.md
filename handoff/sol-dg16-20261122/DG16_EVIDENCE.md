# DG16 source-custody and report-completeness return

## Exact historical source remains incomplete

Results45 retains **11 of 15 bodies (673,870 of 787,231 bytes)**. Recomputed the length and SHA-256 of every retained Git blob and checked its mode and membership against the immutable inventory. The four unavailable originals total 113,361 bytes. Results46 retains **14 checked payloads (127,299 bytes)**, including the bounded Task 1 R2 restoration source and decision. Its same-path test is 23,009 bytes with hash `3f13a9575ec75ee3aad3a9e1f2fa9baf82ff44e96a9f6eab3d86f06c6c5e8457`. The original is 23,375 bytes with the different hash below. The R2 Root decision admits only restoration input receiving and bounded projection source. Full derivation, Task 2, source adoption, protected readiness and original awards remain unissued at that scope. [Results45 custody index](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/6431a1d1e067ab37e4f461caa4a61890d69e7c14/handoff/pro-executor-results-20261115/continuing-execution-20261122-45-recovery3/CUSTODY_INDEX.json), [results46 decision](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/6431a1d1e067ab37e4f461caa4a61890d69e7c14/handoff/pro-executor-results-20261115/continuing-execution-20261122-46-task1-r2/ROOT_TASK1_R2_ADJUDICATION_G0004.json).

| Original body | Bytes | SHA-256 |
| --- | ---: | --- |
| `DERIVATION_MANIFEST.json` | 31,081 | `46b66cfa6e0d90730d11373e767b908ff2676a3e238b61713832f472d9e7edef` |
| `SOURCE_ONLY_CONTENT.json` | 8,613 | `faca08fd01305098c720aec37029abb67b9f8a3c95b75e7808281c11bdcf9504` |
| `owner-sources/generators/rebind_source.py` | 50,292 | `45138b8e537a7a7f24b6b6ce68f0978b42cd5f44d5b3f4bb6e37997f58c2b3f1` |
| `tests/test_joint_source.py` | 23,375 | `a29e590a625333cfcc56f8795381fa2bda1ec7a9b96b29417004768b7915a61b` |

The bounded local scan found zero target basenames among regular files and among members of eight DG16-named ZIPs. Three standalone gzip representations were outside that ZIP member scan. No blob in the shared Git object database had any target length. The documented historical tree `6044873db84b02185e07ec2d712b9aad827888eb` was unavailable locally and its exact GitHub tree lookup returned HTTP 404. These results bound the inspected stores. The next historical custody input would be a legitimate exact object or archive locator. Any recovered candidate would still need independent byte and publication-safety review. [Frozen inventory and locator disposition](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/6431a1d1e067ab37e4f461caa4a61890d69e7c14/handoff/pro-executor-results-20261115/continuing-execution-20261122-45-recovery3/README.md).

## The retained ordinary report exceeded both uncompressed limits

Read the exact 11,775-byte provider ZIP and all 13 members (61,160 uncompressed bytes). Recomputed all 12 manifest payload digests and sizes, checked context bookends and the context/preparation receipts, and refused a same-length corrupted member. The archive binds attempt 1 and operation source `7cbad948f54216617bfa46f3548917104e8f650f`. Each phase returned zero. The substantive receiver refused the `REPORT_BOUND` stub as `REPORT_SCHEMA_OR_INCOMPLETE_STUB` and the artifact remained `UNQUALIFIED`. [Exact archived artifact and receiving](https://github.com/theislampill/IMPLEMENTAUDIT.md/tree/2f920bd7c3b70c78c8c105b486a71c8bc4b5426a/handoff/pro-final-20261122/evidence).

| Quantity | Bytes |
| --- | ---: |
| Producer-reported full legacy canonical JSON | 2,589,544 |
| Inner limit for this operation | 1,823,337 |
| Entire uncompressed delivery limit including manifest | 2,097,152 |
| Excess over the inner limit | 766,207 |
| Excess over the entire delivery limit before overhead | 492,392 |

The exact encoder sizes canonical JSON and the receiver checks that bound before parsing. The outer delivery bound sums uncompressed members plus the manifest. The reported full size therefore rules out a reserve-only repair or ZIP compression as a way to deliver this legacy representation. The report bytes and per-section sizes were withheld, so the size and full-report digest remain producer statements. The archived stub preserves the refusal. [Encoder and receiver](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/7cbad948f54216617bfa46f3548917104e8f650f/engineering/g132-host-runtime-static-operation/runtime_static.py#L1152-L1178), [outer delivery bound](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/7cbad948f54216617bfa46f3548917104e8f650f/engineering/g132-host-runtime-static-operation/run-owned.py#L175-L200), [inner limit calculation](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/7cbad948f54216617bfa46f3548917104e8f650f/engineering/g132-host-runtime-static-operation/run-owned.py#L389-L404).

## Prospective compact representation for Root review

The current receiver already recomputes six canonical values from the observed rows and pinned inputs. A separately versioned compact report could retain the observed rows and their actual closing observations in full, and carry a `{bytes, sha256}` commitment to each of these six canonical derived values. The receiver would validate the compact canonical JSON under the same inner wire limit and preserve the outer aggregate limit. It would reconstruct the six values through the same selected source and unchanged finite observation and resource bounds. It would consume these as logical report fields in memory, applying the same per-field equality, coverage, drift, budget and complete-predicate checks. This design preserves each actual observation and distinguishes the historical serialized form from the prospective wire. [Existing canonical recomputations and terminal checks](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/7cbad948f54216617bfa46f3548917104e8f650f/engineering/g132-host-runtime-static-operation/runtime_static.py#L1249-L1267).

| Derived field | Existing reconstruction dependency |
| --- | --- |
| `expected_provider` | Pinned wheel and observed objects |
| `layout` | Selected rows, topology, and expected provider |
| `cache` | Selected rows and objects, pinned retained cache |
| `graph` | Layout, cache, expected provider, and observed objects |
| `pin_comparisons` | Layout and observed objects, directories, and selections |
| `counters` | Existing observed population and resource counts, plus graph edge count |

For prospective admission, require a strict closed descriptor census, duplicate-key and noncanonical-wire refusal, exact source/context and input pins, unchanged selector/row/edge quotas, and budget checks before any potentially expensive derived computation. Compute digests without accepting an oversized decoded transport or accumulating an unbounded legacy JSON buffer. A missing observation, mismatched bookend or failed recomputation must continue to refuse. Freeze and test the maximum allowed compact record and a one-byte-over record, then test descriptor omission/substitution, incomplete bookends, old/new shape confusion and the actual outer manifest-inclusive total. If the governing source owner requires the limit to apply to the historical serialized form as well, hold this variant and retain the refusal.

A local in-memory fixture exercised the pinned source's pure canonical and strict JSON helpers with stand-in values for the six existing sections. The compact serialization used 3,736 bytes versus 6,681 and reconstructed byte-identical canonical fixture JSON. Duplicate keys, a missing commitment, a changed commitment, and an oversized compact record refused. The exact legacy encoder accepted the fixture at its selected bound and emitted `REPORT_BOUND` one byte over. This checks the representation idea; the production sources, the held report's fit, and the operational receiver remain unqualified. A source-owner review of this representation is the next ordinary gate. It can use retained public fixture data with the actual recomputation functions to find whether the savings cover the wire limit. Even at the historical inner limit the compact wire would need to save at least 766,207 net bytes with framing. Record inability to fit as refusal.

## Original work order and receiving boundary

- Retain M2's exact-source normalized correspondence and its individual node and raw-output limits. [Original M2 decision](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/6431a1d1e067ab37e4f461caa4a61890d69e7c14/handoff/pro-executor-results-20261115/continuing-execution-20261120-19/dg16-m2/ROOT_ADJUDICATION.json).
- Retain M4 at the declared L04 native natural transition, including the consumed decision-changing independent preparation while the dependent effect stayed blocked. [Original M4 decision](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/6431a1d1e067ab37e4f461caa4a61890d69e7c14/handoff/pro-executor-results-20261115/continuing-execution-20261117/original-receiving/M4_ROOT_RECEIVING.json).
- Retain M5's applicable Q04/Q05 package and isolated Linux installed scopes and the correspondence for required exact commands. [Bounded M5 decision](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/6431a1d1e067ab37e4f461caa4a61890d69e7c14/handoff/pro-executor-results-20261115/continuation-recovery/m5/ROOT_ORIGINAL_RECEIVING.md).
- M1/G1 and M3/G3 remain open, as does the complete M6/48-row disposition. Source custody or this ordinary diagnostic is only an input to future receiving. Actual G1 dispatch and G3 consumption, their exact current native and operational inputs, Root decisions and M6 receiving retain their own prerequisites. [Original six-group matrix](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/585012cbc6b47cb332222c2784481567a482c8a5/recovery/contracts/SIX_GROUP_MILESTONES.json), [R0035 original and amendments](https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/209).
- Root receiving of this return is pending. Run `44888568054` remains `SPENT_NO_RETRY`. `301aeecde08ba6f169bc3cd837eae6f6ad068219` and A4-07 remain `UNKNOWN_NO_REPLAY`. Queued `43098152901` remains separate and untouched.
