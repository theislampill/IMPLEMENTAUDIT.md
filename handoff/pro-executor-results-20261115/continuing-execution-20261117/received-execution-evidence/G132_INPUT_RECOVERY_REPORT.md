# G132 exact input recovery

**Seven of the 11 approved private input bodies were recovered with exact byte-size and SHA-256 matches. Four exact bodies remain missing in this bounded search.** This is newly recovered file custody only. Protected operation status remains `UNKNOWN_NO_REPLAY`; no authority, sender operation, host preparation, live G1/G3 result, or original award follows.

## Exact-byte outcome

| Approved input | Required bytes | Result |
|---|---:|---|
| `COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json` | 425 | Missing exact version; older mismatch found |
| `COMPOSITION_PLACEMENT_EVIDENCE_INDEX.json` | 512 | Exact match recovered |
| `COMPOSITION_PLACEMENT_RECEIVING.json` | 937 | Missing exact version; older mismatch found |
| `COMPOSITION_ROOT_ADMISSION.json` | 800 | Missing exact version; older mismatch found |
| `PACKAGE_BODY_RECEIVING.json` | 9,744 | Exact match recovered |
| `PACKAGE_ROOT_RECEIVING.json` | 928 | Exact match recovered |
| `PACKAGE_TERMINAL_RECEIVING.json` | 4,531 | Exact match recovered |
| `SOURCE_ACQUISITION.json` | 593,285 | Missing exact version; older mismatch found |
| `placement/ACCESS09_DIAGNOSTIC.json` | 29,107 | Exact match recovered |
| `placement/ACCESS09_FINAL.json` | 5,113 | Exact match recovered |
| `placement/ACCESS09_ROOT_RECEIVING.json` | 1,961 | Exact match recovered |

The complete approved SHA-256 values are preserved unchanged in [EXPECTED_INPUT_INDEX.json](EXPECTED_INPUT_INDEX.json); [RESULT.json](RESULT.json) records every match, current path, current file observation, and source archive/member. The approved index body is 1,397 bytes, SHA-256 `d069c3a7c66f54ffe7eae32ca89701743e96bdd2a0e221f52864150887390f15`, returned Git blob `eeceaf0223b28fa78d17a9132d84a34f585e4049`.

All seven matches were present as actual members of `DG16_PRIVATE_CONTINUATION_INPUTS_20261109.zip`, Library ID `libfile_ee3c3406b2b08191b07d22a10740a864`, archive SHA-256 `7572fecaf1f7c0e9015d54b4392ef2349166efb11bcfda95ce2779c7c9808a46`. The same archive also survives inside the separately materialized DG16 successor recovery bundle; the nested path is recorded in the byte scans. Only exact matching bodies were extracted to `recovered_inputs/`; none was reformatted or regenerated.

The four same-name older bodies have these observed byte lengths: native applicability adoption 627 rather than 425; placement receiving 886 rather than 937; Root admission 749 rather than 800; source acquisition 198,602 rather than 593,285. Their SHA-256 values also differ. They were not substituted for the approved inputs.

## Bounded investigation and provenance

The initial four search requests covered the exact input filenames, the known evidence-bundle title, and DG16/G1/G132/ACCESS09 artifact titles. One filtered inventory request was rejected at argument binding; a minimal project inventory request then returned its first 200 items. The broad search's pasted text references were not materialized or treated as recoverable input bodies. The final exact-title query for the four remaining filenames returned no matches. All arguments, returned identities, counts, continuations, exclusions, and the error are retained in [RESULT.json](RESULT.json) and `query_receipts/`.

Five relevant existing DG16 bundles were materialized through the current Library skill's required helper route, using the complete earlier search result and exact selections:

- `DG16_PRIVATE_CONTINUATION_INPUTS_20261109.zip`
- `DG16_PRO_SUCCESSOR_RECOVERY_20261110.zip`
- `DG16_PRIVATE_SUCCESSOR_CHECKPOINT_20261110.zip`
- `DG16_PRIVATE_CURRENT05_RECEIVING_INCREMENT_20261110.zip`
- `DG16_CURRENT05_WAITING_REFS_AND_ROOT_DECISIONS_20261110.zip`

Both materializations completed without partial results. The five selected bundles and their nested ZIPs yielded 23 distinct archive bodies inspected. Inspection read archive metadata and actual members whose basenames matched the approved 11 names. No nested archive was skipped by the bounded scanner. Detailed comparisons are in [BYTE_SCAN_01.json](BYTE_SCAN_01.json), [BYTE_SCAN_02.json](BYTE_SCAN_02.json), and [BYTE_SCAN_03.json](BYTE_SCAN_03.json).

## What changes, and what does not

Root can now receive seven exact existing bodies as newly recovered evidence. This narrows the missing-byte problem from 11 to four. It does not restore the former files' physical identity or custody continuity, satisfy same-live-job receiving, issue a new admission, settle the interrupted provider request, or renew the protected grant. The old no-replay boundary and the sender/currentness/live prerequisites remain unchanged.

The missing result is limited to the named searches and inspected artifacts. The unconsumed inventory continuation and other Library contents were not exhaustively examined; no global absence claim is made. No prior-chat summary, public hash, source program, or older version was used to synthesize a missing body. No remote publication or mutation occurred.

## Final chronology-targeted lookup

The final pass specifically addressed the age gap: the recovered bundles date from November 9/10, while the four missing input versions belong to the later approved G132 composition. The exact project-inventory continuation returned 200 more items, spanning November 13 14:37 through 08:46, with two relevant project notes and no eligible later DG16/G132 archive. Across the two inventory pages, 400 items were returned; a further cursor remains, so this is still not an exhaustive Library census.

A separate title search restricted to creation dates November 11–17 queried `DG16`, `G132`, `continuing execution`, and `successor checkpoint`. It returned five authored project notes/concurrence records and one supplemental retention receipt, with no archive or continuation. Pointer checks in four resolved records found no exact retained GitHub artifact URL/ID or missing-input custody claim. One review names `product-e76.zip` as a product-source copy with an overlay; that is not an identified retained copy of the four approved private bodies. The ten captured approved/source-composition records also contain no exact retained artifact pointer. No later download candidate was established and no additional download occurred.

The exact queries and findings are retained in [CHRONOLOGY_LOOKUP.json](CHRONOLOGY_LOOKUP.json) and `query_receipts/07.json` through `09.json`. The earlier report/result/manifest are preserved as `PRE_CHRONOLOGY_*` files. The creation-date search does not exhaust all version histories or alternative artifact titles. The final result is therefore **7 exact inputs recovered, 4 exact versions not found in this bounded, chronology-targeted investigation**, with no global absence claim.

### Smallest legitimate next action

Obtain these four **existing exact bodies**, or their precise retained archive/file identity, from their actual custodian: `COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json`, `COMPOSITION_PLACEMENT_RECEIVING.json`, `COMPOSITION_ROOT_ADMISSION.json`, and `SOURCE_ACQUISITION.json`. The next action is a narrow evidence-recovery request followed by byte verification against `EXPECTED_INPUT_INDEX.json`; it is not reauthoring an admission, manufacturing replacement inputs, or preparing another launch. No additional broad search campaign is proposed.

Root reports actual local UID/GID 1000. The approved `operation.py::qualify` requires UID/EUID/GID/EGID zero, so the present direct local credentials do not satisfy that source gate. No privileged route was prepared. All protected-effect, old-request, sender, currentness, and original accepting-receiving boundaries remain unchanged.
