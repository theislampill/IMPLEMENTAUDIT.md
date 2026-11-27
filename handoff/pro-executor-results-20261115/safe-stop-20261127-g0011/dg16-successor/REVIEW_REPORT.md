# DG16 successor independent receiving review

## Result and stop boundary

**PASS at exact data, static-delta, and bounded offline scope** for operator `bcd6e8974edd71e214fbacf381dfa1ddab8d96da`. This is a fresh nonauthor receiving review. It grants no Root authority, launch authority, original award, or DG16 completion.

The owner requested **SAFE STOP** after the bounded offline command had completed. No further tests, fetches, branches, runs, native operations, record issuance, or optional follow-up work occurred. Only this report and its seals were completed.

| Identity | Verified value |
|---|---|
| Received successor commit | `bcd6e8974edd71e214fbacf381dfa1ddab8d96da` |
| Successor tree | `ebae278fb84dbe599d16902b77df22fc4a4f3bc2` |
| Exact parent | `2af600fad0e80fa71d9f808741bd74db792308b2` |
| Admitted source commit | `fc2e416c5da38eb370045561f5281a846785ec3e` |
| Admitted source tree | `a9914d446d2a3e0653c972cf50197186e23555d8` |
| Received bundle SHA-256 | `b6d52aee8aea7fc77945dfdde4179de998e52a6556e656f19267cc0c319a99c9` |
| Builder SHA-256 | `79a96e5d12c041de3967645d42d308b864a16987a05314d27c032836ad9fbd0b` |
| New control SHA-256 | `bc90f3d5a4499ca3a91eb239dd712908c68acf9c167cd90d636e2ed3f7e22e36` |

All eight entries in the received `SHA256SUMS` passed. The entire builder and new test were read before any execution. The package's earlier nonauthor “GO” is a claim in its README: its raw reviewer receipt is not among the received files and was not independently verified. The present result rests on fresh receiving evidence.

## Exact source and delta

The admitted source commit and base operator commit were reconstructed from retained provider metadata only when their complete Git object IDs matched. The source was checked out into new isolated verification custody. Four absent immutable source blobs were received through the existing connector, and every received body matched its exact Git blob ID. No network Git, credentials, authentication probing, or remote mutation was used.

All **1,993 admitted source files**, totaling **175,682,079 bytes**, were checked against the source manifest for byte count, SHA-256, Git blob identity, mode, and single-link file state. The source checkout was clean before and after affected validation.

The exact whole-tree delta is **19 files: 18 modifications and one added control**. Every changed or new path is Git mode `100644`; all existing modes remain unchanged. The complete changed-path and byte/hash mapping is in `REVIEW_RESULT.json`.

The workflow bytes equal the base workflow after **only the exact old-main-branch substitution**. There are 22 successor branch literals in 13 files. The new main branch is `engineering/dg16-image23-main-20261128-01`; the control branch adds `-control`. The source branch remains `engineering/pro-dg16-image23-source-20261127-01`.

The create-event trigger, repository/ref/event/ref-type/attempt checks, environment guard, pinned actions, read-only workflow permissions, 330-minute timeout, image-23.1-only selection, and all other steps are preserved. The two in-job receiving boundaries retain their order: first request publication before `g3-consume`, then final request publication before `g3-decide`. Their implementation bodies change only in the reviewed branch/constants/pin substitutions. This establishes preservation; it does not claim that a hosted create event has been run or that event delivery is an exactly-once service.

## Defect repair and pin closure

The pinned V24 loader is **84,755 bytes**, SHA-256 `3d14d02940239c49e590e82cc04c76af14ae958ae3e5ef83b0949b53d7ec7c74`. Its effective executor is the directory-mode source at `test-support/r5-runtime-directory-mode-source/work-graph-c5-executor.py`: **108,100 bytes**, SHA-256 `5c74e75e6a88121918d0c254c5964f6efe950c09fcc5560ef698080254839b20`.

All **15 effective engine members** were derived from actual admitted-source bytes and then corroborated by the loaded engine. Each successor copy matches the full derived map: `operation.EXECUTING_SOURCE_BINDINGS`, `g3_receiving.EXECUTING_SOURCE_BINDINGS`, and `proof_consumer.EXECUTING_SOURCE_PINS`. Each base map differs only in the known stale executor row, which records 83,099 bytes and SHA-256 `d9b9ad23eefaa62bb273970232dc5669ab40d465c6f9d5bf5f83b7048e8df1d8`.

The independent review recomputed the module/data pins, public-input index, composition digest, policy pins, 43-member public packet manifest, bootstrap manifest/admission pins, and entry-point dependencies. It found no stale changed-file digest in the successor scope. Independent static checks totaled 6,143; most are per-file source-manifest checks, not separate behavioral tests.

The base's actual `load_selected` call refused with `SELECTED_ENGINE_BINDINGS_DIFFER_FROM_ASSEMBLY`. Its message SHA-256 is `a53078887f660a89b754edf277c39601f813209febf29773ba8b165a5dd23289`, matching the reported failed run's defect identity.

## Bounded offline validation

The supplied builder was loaded as inspected code and used only through its read-only derivation, in-memory assembly, and verification functions. Neither `cmd_build` nor `cmd_draft` was called. No record was issued, no timestamp was overridden, and no Git commit was authored by the builder. The supplied bodies remained labelled drafts throughout.

The builder's 191 content/consumer checks passed with no warnings. Its in-memory bytes equal every received operator-scope byte. Independently hashing the complete derived tree and commit serialization reproduced the exact received tree and commit above. This is deterministic reproduction of the supplied package, not authority to use its draft records.

The new control ran **once, with five tests, all passing**:

- The source is the exact admitted commit/tree and is clean.
- The pinned `operation.load_selected` accepts the admitted source.
- All three maps equal the actual loaded engine.
- Runtime selector declarations match the engine's base/native/startup declarations.
- Reintroducing the known stale executor row is refused.

The pass used an offline restriction wrapper that rejected writes, network calls, unauthorized subprocesses, and construction of protected sessions. It observed no denied attempt and no protected-session construction. Only allowlisted read-only Git subprocesses were used. No native/runtime qualification, actor, producer, useful-work pair, G1/G3 receiving operation, or old accepted case ran.

## Procedure findings and limits

The package's exclusive-push explanation is incorrect: publication of Git commit/tree objects is separate from branch creation. It does not establish that an API route requires a second review branch, a personal credential, or a user PC. The incumbent Root's separately reviewed object-publication/ref-creation route and its exact grants remain controlling. This review launches neither route.

The package's commit message calls the three records “Root-issued,” while its README and `drafts/` directory identify those same bodies as drafts. They remain **unissued drafts**. Fresh Root issuance and a fresh dependent-pin/record diff are required before any prospective operation.

The seven pre-existing test files are unchanged by this successor. Static inspection shows earlier V21 tuple/branch literals and a fixed selector digest in older tests. The builder's `--tests` comparison permits existing failures and checks for previously passing cases that regress; it is not an all-tests-green gate. No older suite was replayed, no prior reported identical suite result was adopted as new evidence, and no failing suite was repaired or bypassed to obtain this bounded pass.

All admitted-source bytes and all 68 operator-scope files were checked. Some unchanged out-of-scope operator blobs were not imported; the exact whole-tree delta relies on their authenticated tree-entry identities. The new verification custody is not represented as historical local custody. The base operator's unimported parent history is outside this review.

The current result is suitable as bounded receiving evidence for the incumbent Root. Fresh records, concrete prospective grants, actual issued identities, runtime conditions, branch absence/run census, and both in-job receiving stages remain separate work. **Original awards: none. Operational authority: none. Owner safe stop: observed.**
