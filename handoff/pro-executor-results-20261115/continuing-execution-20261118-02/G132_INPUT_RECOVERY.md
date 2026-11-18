# G132 approved-input recovery — bounded receiving result

**Disposition: bounded census complete; none of the four exact approved bodies was recovered.** This closes the assigned search of three named historical Library transcripts and the declared data decoders. It does not prove that no other copy exists. No original acceptance or replay authority follows from this work.

The governing input index is the exact 1,397-byte `qualification/dg16-r5-g1-hosted-episode/carrier/INPUT_INDEX.json` at approved commit `301aeecde08ba6f169bc3cd837eae6f6ad068219`, SHA-256 `d069c3a7c66f54ffe7eae32ca89701743e96bdd2a0e221f52864150887390f15`. Its recovered bytes are preserved as `EXPECTED_INPUT_INDEX.json`.

## Missing approved bodies

| Body | Required bytes | Required SHA-256 | Result |
|---|---:|---|---|
| `COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json` | 425 | `64a241977c802a500ebd6b35544207d2759d9e0deb7b2a359153aa5a6100985d` | Exact body not recovered |
| `COMPOSITION_PLACEMENT_RECEIVING.json` | 937 | `e8e85c869bfd878f98fb146ffdd01dbef8511f60c58e6db2d5cdfee652e59dd5` | Exact body not recovered |
| `COMPOSITION_ROOT_ADMISSION.json` | 800 | `dd20cb8e155342ed7f09426a1533ac435e2e1e14d917bcd35e31e1b1f1a1e995` | Exact body not recovered |
| `SOURCE_ACQUISITION.json` | 593,285 | `265325e29418163caeb27e13f4a66b32e1e5c0e4f3ad72cbef9bfff72a3b3bbf` | Exact body not recovered |

The earlier seven recovered inputs remain outside this search. No substitute body or grant was created.

## Source custody and search

All three specified transcripts were materialized through the current Library skill helpers. Byte sizes and `user.library-file-id` extended attributes were verified locally, and all bytes were hashed before extraction. The first target used the unchanged exact-title search result with `library_download.py`; the other two used find-resolved native references, `prepare_materialize`, and `library_file_transfer.py`. Transfer instructions were passed unchanged to the helper; signed transfer URLs and headers are not included in this report or the public evidence set.

| Library file | Bytes | Local SHA-256 |
|---|---:|---|
| `libfile_9455641d97788191a57b0a8223f3d1ee` — November 14, 20:57 transcript | 34,388,969 | `87a126d8c901d308c5e831a478839fcc7193b5b34a587c941348a74ff3ff01a9` |
| `libfile_e33fc9d357588191b8d33296ec6f2547` — November 14, 18:17 transcript | 25,450,045 | `69f96cda4ab75645956537e111dfcdf8c98b88ef0c4584d438318bc0368f3881` |
| `libfile_7dffe40432dc8191b0767bbb1e1ff1a9` — November 13, 19:22 transcript | 33,776,590 | `cf75a5d635a120abe6e2e838250907cf38d17b3a40f18c911d82ea30a959a50e` |

The total materialized source was **93,615,604 bytes**. All three contain missing filenames; none contains any of the four approved SHA-256 values as literal text. The initial per-source census is retained unchanged, including its provisional status; this report, `RECOVERY_RESULT.json`, and the two extraction receipts provide the terminal bounded result.

The primary extraction checked 24,448 exact-size candidates and parsed 4,212 complete JSON/Python data objects, comprising 1,186 unique objects. It performed 297 strict base64 decodings. Complete data objects were tested in explicit JSON serialization variants, with every transformation recorded and acceptance contingent on both exact byte size and SHA-256. No transcript code, shell commands, dynamic expressions, or instructions were executed.

Two small nested strings exceeded the initial traversal-depth bound. A focused follow-up recovered those exact strings through the recorded data transformations and checked them independently: neither matched. That follow-up also examined 7,746 standalone JSON-shaped string candidates: 7,193 were complete literal strings, with 148 unique decoded values; 553 were rejected as nonliteral. No standalone candidate exceeded the size bound, no new traversal bound remained, and no approved body matched.

The transcripts contain an explicit **older** same-name index: native 626 bytes / `3cea658c5d33da58f995998207d6bd8accbf8181ea6c7bf2ce454be1a4801db5`; placement 886 bytes / `5ff8a1e82e4e2b6a572f7da89fd199dda5eef5d80a4285293f8316264ac2b8bf`; Root admission 749 bytes / `1aeb53573dbf20f0a44c24b6f0528d1bc7372d3a71c96dfc51a76e005de09c85`. Their provenance is recorded in `EXTRACTION_RECEIPT.json`. They do not satisfy the approved pins.

A separate Library search for the four approved hashes returned ten ranked, mostly unrelated candidates. Exact `find` checks over each candidate's entire reported text range returned zero matches. This was a bounded discovery check, not an exhaustive Library inventory or an exact-match guarantee from semantic search. The search cursor was not followed into an unbounded unrelated corpus.

## Capability and original-scope boundary

At `2026-11-18 05:42:59 UTC`, metadata for all 326 currently exposed tools was inspected without credential probing. No advertised interface matched the required actual usage-window, canonical C02 migration-event, native client-operation history/status, or original G3 custody/Root-admission capabilities. `CAPABILITY_CENSUS.json` records the exact lookup categories and scope. This finding concerns the exposed tool descriptions; it does not assert that another environment cannot provide those capabilities.

Public source recovery, local process execution, Library reads, and connected GitHub capabilities remain available. Root owns the separately scoped connected smoke and its current reconciliation. This lane made no GitHub write and supplies no new evidence about its outcome. The previously delivered exact G3 consumer remains executable source with a genuine `ACTUAL_ROOT_CUSTODY_REQUIRED` refusal on the current nonroot host; generic callback success is not substituted for original consumer acceptance.

For original G132, the four exact input bodies remain missing. Independently, original sender admission/private-input custody, actual native provenance, genuine root-owned live-job G3 custody and same-job component inputs, currentness, remaining lifetime, and authentic reconciliation of the interrupted protected request remain required. Recovery of a historical admission file, even had it succeeded, would not issue current authority or remove `UNKNOWN_NO_REPLAY`.

For DG18, no actual eligible usage-window, occurrence-discrimination, canonical C02 migration, cold receiving, or current custody input emerged. There is therefore **no new READY original DG18 cell** from this recovery. Exact6b, W-FULL, criterion 11 and A7 remain accepted as recorded; N1 remains `LOST/UNKNOWN`. Those accepted tests were not rerun. The existing original-criterion mapping remains `/workspace/scratch/095d3235c921/evidence/dg18-current.md`, 19,756 bytes, SHA-256 `f9089c2a2d907eaa74f56dc46457cf0e623727b01b6f66bd24e46103e5125d6d`.

## Limits and effects

The decoders cover complete raw JSON windows, complete JSON/Python data literals, present string contents, strict maximal base64 tokens, and explicit JSON serialization of complete existing data. Incomplete/nonliteral program expressions were rejected. Unspecified split encodings, arbitrary compression, absent runtime values, and undiscovered files remain outside this bounded search. The absence of a hash match is reported only for these examined sources and transformations.

There were zero protected launches or ref updates, private sender operations, encryption/decryption operations, replay attempts, grant issuances, native-proof claims, or original acceptance awards. The frozen adapter manifest `d2ef2aa1554dfd4535f227fddb08c0df9db5db599b4f875e2ea153d4f7bb07f9` and Root smoke files were untouched. Only this assigned recovery directory received new files.

`RECOVERY_MANIFEST.json` binds the report, approved index, scanner sources, extraction receipts, capability census, terminal result and safe search/find receipts. Full transcripts are retained as local private source material and are not copied into the repository or publication artifacts.
