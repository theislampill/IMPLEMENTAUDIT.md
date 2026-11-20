# Original A3 first attempt — failed scope and root cause

## Independent disposition

**FAILED_INCOMPLETE_NO_A3_AWARD. Authority: NONE.**

Receiving of this failed first attempt is complete. All **231 local receiving checks passed**, actual `14a891/0`; these checks establish the accuracy and custody of a failed episode, not original A3 acceptance. No original runtime was imported or executed, no original command was replayed, and no provider/controller/source action was performed by this reviewer.

The failure is in the newly authored prospective episode, immediately after genuine G0002 construction. The actual executed source matches the source I previously reviewed. My earlier source READY missed a deterministic closed-schema mismatch and is **superseded for any further execution of that v1 source**. The prior sealed report, source, controls and receiving requirements remain unchanged as history. A repair and later distinct execution are not pre-approved.

## Exact original occurrence and custody

| Binding | Actual retained identity |
| --- | --- |
| Product | `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7` |
| Capture commit | `2504fb661e9ed8e14c74c3c88ba7ec7740225cc5` |
| Capture tree | `3f7f9b3402ac0a090e7170aebe03219d474be837` |
| Run / attempt / job | `44697958629` / `1` / `136159149912` |
| Artifact | `14611367579` |
| Raw ZIP | 418,689 bytes; SHA-256 `e7f1c33c5d25dbee54cae22e9b9728a84a758a133fab9f52f5d1404cc9c00e9f` |

Root's genuine source adoption binds the exact previous review seal and thirteen receiving requirements. The actual remote three-file bodies match the reviewed author packet; the actual commit has sole parent 51416. Reconstructing the Git tree from all 1,785 immutable original leaves plus the three additions reproduces the actual published tree. There is no observed publication/source substitution behind this failure.

Actual provider metadata reports terminal run/job failure. The execution step failed at 07:51:09 UTC; the other nine recorded steps succeeded, including failure finalization and artifact upload. The exact original archive was downloaded once, actual `ddc504/0`, with HTTP 200 and no retry. Its 99 members total 1,403,460 bytes, comprising 98 manifest payloads / 1,379,251 bytes plus the 24,209-byte final manifest. Every ZIP member, extraction body, manifest digest/blob identity and receiver index entry was independently checked. The full 26,813-byte job log matches its retained provider body.

The original ZIP remains externally bound at `dg18-a3-original-actual/final/ARTIFACT.zip`; it and the complete extraction are not duplicated in this review.

## Initial root cause

The exact 1,224-byte `SUITE.stderr` records one unittest ERROR after 7.855 seconds:

```text
episode.py line 184: archive2=self.actual_archive('G0002',first)
episode.py line 142: pointer=resolved['pointer'];ref=pointer['archive_ref']
KeyError: 'archive_ref'
```

The unchanged original `claim-run-rotation.py::validate_pointer` requires the live pointer's keys to equal its exact `POINTER_KEYS` set. That schema deliberately does **not** contain `archive_ref`. The retained actual G0002 pointer equals the original closed schema and lacks that field. A data-only lookup against the retained JSON reproduces the same KeyError without importing or running the original episode.

The original `resolve_generation` instead returns `archive_manifest_path`, pointing to the actual immutable generation's `archive-manifest.json`. The actual generation manifest's `prepared` record contains the archive ref/OID/hash. Those are distinct from the live pointer object; typed historical archive pointers also have their own `archive_ref` field. The new episode conflated those records.

The retained G0002 evidence independently joins:

- Current pointer `ec252abc412797cfb125f84613b2fe04aa82a5b5`.
- Receipt `9972d15ca4056f653119bf02ef9a22178c4e05b9` and permanent marker `40dd072a33de79d58e68f44dab9dff24cc28a01e`.
- Actual archive authority `refs/implementaudit/state-archives/canonical-reader-test/G0002` at `928213659b4740288a545e342e099585cfc08026`.
- Exact resolved archive body SHA-256 `db6e533feaa7ad1fd4bfc27439d97d3bbab2f293389c2f13a7f05ddf4812a444`.

All 13 actual G0002 archive entries, including the exact 298-byte EVIDENCE canary, are retained and received. The observed failure therefore does not establish a missing archive or an original owner failure. It occurs before the new adapter issues its first archive-read command.

The prior source review checked the intended predicates and recorder integrity but failed to join this field access to the original pointer's closed schema. Its 137 source checks and five TEST_ONLY controls did not exercise a real returned resolution through this adapter. This is a concrete missed source blocker, not an original A3 success later invalidated by publication drift.

## Precise completed and unperformed scope

The original fixture genuinely created its disposable subject and claim, initialized/activated the checkpoint, established G0001, rotated through the unchanged owner into G0002, and resolved the G0002 pair/receipt/marker. All 15 outer command returns are 0. Commands 1–13 are setup/construction; commands 14–15 are final-retention ref reads after the Python exception.

Only two method checks completed: actual G0002 was published, and the declared missing historical capture was absent. The episode record has `archives=[]`, `commands=[]`, `method_completed=false`, and only the `final-retained-fixture` snapshot. Its semantic command list is distinct from the complete 15-entry outer command index.

**No G0002 `current_views` reader/run-root/phase validation baseline ran.** No same-byte live-phase negative/removal/positive sequence ran. No pending manual-resume boundary or G0003 was created. No stale/archive-token or old-receipt discrimination ran. No live-pointer removal/restoration or retired-root poison/restoration ran. The expected thirteen negative calls and nine discriminator snapshots are absent. Thus none of the three complete original A3 predicate conjunctions is established by this attempt.

`CONJUNCTION_DISPOSITION.json` preserves the exact R01–R13 distinction between received custody, partial setup and unperformed acceptance. The recorder correctly returns `FAILED_OR_INCOMPLETE_PRESERVED_NO_RETRY`; its original artifact index has no complete stage and reports `A3 episode incomplete or scope changed`. A null top-level `suite_exception` does not cancel the unittest case ERROR.

## Surviving evidence and cleanup

The original final-retention cleanup ran before temporary-repository cleanup. Its retained fixture ZIP has 84 members / 1,103,198 bytes, with 26 verified loose Git objects, 33 refs, a closed commit/tree graph and 23 snapshot files. All snapshot bodies and both raw retention ref reads agree. No G0003 ref or generation exists.

Actual case completion records original fixture cleanup complete. The bounded survivor observation reports no selected survivor and no unavailable process row. Source-before and source-after are byte-identical; all 49 original inputs and final copied-runtime identities match the earlier immutable source binding. These are accurate failure-finalization and cleanup facts, not substitutes for the unperformed A3 controls.

## Corrective boundary and preserved authority

The separate repair author must reconcile the new archive adapter with the actual original resolution, generation/archive authority and closed schemas, preserve exact ref/object/hash/type bindings, and freeze its own source/delta and meaningful retained-real-data controls. That packet requires subsequent independent review before Root selects any new distinct ordinary episode. This review neither edits that source nor approves a retry, repair implementation or new original execution.

Root's existing failure receipt SHA-256 `9d32986ff54f3430c0d001288d2c9006cf363d78ffcb4183b5a750dfce112013` is consistent with these independent findings. Original 14 and all amendments, accepted unrelated scopes, OR/C02/native/N1 prerequisites, historical failures/losses/pending and UNKNOWN_NO_REPLAY effects remain unchanged. No original A3 or other acceptance credit is awarded.
