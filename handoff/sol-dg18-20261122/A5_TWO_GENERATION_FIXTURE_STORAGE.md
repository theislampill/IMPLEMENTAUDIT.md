# DG18 A5 cumulative Git storage in a two-generation fixture

The exact-source two-generation archive fixture retained **593,082 unique logical archive-entry bytes** across ten Git blobs. The measured ext4 allocation for the disposable repository's Git object database, refs and reflogs grew from **49,152 to 245,760 bytes** before packing. It fell to **73,728 bytes** after packing. The object count, aggregate logical object bytes and exact ref population digest matched across GC. This is an observed storage-cost constituent for the constructed fixture. The exact H002 historical logical footprint and current A5 pair payoff have their own records. [Historical H002 logical footprint](A5_H002_LOGICAL_STORAGE.md) · [Exact A5 payoff](A5_COMPLETE_PAIR_COST.md)

## Subject and measured population

Candidate `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7`, tree `9c3913ceaa95f3f36b0377fe2dba4a302afcba89`. The harness verified 75 archived source file identities and executable bits. It observed the exact existing `test_real_retained_archive_chain_survives_gc_and_missing_ancestor_refuses` and collected storage around the two archive preparations, the fixture's Git packing and the restored ancestor. The fixture constructs its predecessor receipts and does not publish live controller currentness. It uses actual Git objects, refs, archive anchors and typed archive readback. [Pinned fixture](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/51416b2f156b341c4a5f09029e2c6ceb5b30b1e7/fixtures/canonical-state-rotation/archive_v2_test.py#L318) · [Exact harness](measure_a5_fixture_storage.py) · [Case results](A5_TWO_GENERATION_FIXTURE_STORAGE.json)

| Stage | Logical object bytes, all OIDs | Encoded regular-file bytes | Allocated bytes, files and directories |
|---|---:|---:|---:|
| Before first preparation | 427 | 266 | 49,152 |
| After first preparation | 283,917 | 17,425 | 151,552 |
| Before second preparation | 284,344 | 17,691 | 163,840 |
| After second preparation | 600,634 | 36,214 | 229,376 |
| After second finalization, before GC | 600,679 | 36,311 | 245,760 |
| After GC | 600,679 | 25,432 | 73,728 |
| After expected-old archive-anchor restoration | 600,679 | 25,377 | 86,016 |

Logical object sizes are Git `cat-file` body lengths by unique OID. Regular-file bytes are `st_size` for `.git/objects`, loose/packed refs and reflogs. Allocation sums `st_blocks × 512` across those files and directories. This excludes other repository files and filesystem overhead outside those paths. Linux WSL used ext4, CPython 3.12.3 and Git 2.43.0. No reflogs existed in the measured population.

Each archive had six entries. G0002's six distinct entry blobs total 280,141 bytes and G0003's total 313,149 bytes. Two blobs, totaling 208 bytes, are identical and shared across the generations. Their deduplicated union excludes archive manifest bodies. The broader Git object census includes both manifests and the finalization object.

The original missing-ancestor case refused both archive verification and current-generation readback, restored the exact fixture anchor, and again obtained its typed historical STATE. The first measurement wrapper incorrectly expected the post-restore physical layout to equal the post-GC layout. That check failed after the existing fixture's assertions. The restored exact ref population digest and aggregate object-storage census match their post-GC values. The physical ref layout changed. Restoring a formerly packed ref created a loose ref and increased allocation by 12,288 bytes. Both disposable roots were removed.

## Acceptance boundary

Receive this as a physical growth and deduplication measurement for two retained generations on the recorded fixture backend. It establishes no historical H002 disk footprint, production storage budget or authentic OR operation cost. The observed distinction between exact ref state and physical packed/loose representation is relevant to storage receiving. Any future historical or applicable-host measurement needs its original pre/post store and backend observations. Sol-DG16 independently received the bounded fixture evidence at 1a55b3aa. The reviewer matched the pinned source and 75-member population, summed all seven snapshots and verified the inclusion-exclusion calculation and post-restore ref census. The review flagged the original object-population wording. The retained snapshots compare object counts and byte totals and carry no digest of the complete OID set. Disposition RECEIVE_BOUNDED_CONSTRUCTED_FIXTURE_STORAGE. The wording correction used the retained snapshots.
