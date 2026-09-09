# Replication Guide

## Verify the committed corpus

From the repository root:

```bash
python scripts/check-genealogy-corpus.py --root .
```

The checker verifies seven trifectas, twenty-one selected lineage directories, raw ZIP identities, exact extracted-member parity, embedded-manifest identity, 1,405 unique lineage-scoped property locators, source-prompt identities, neutral projection hygiene, all three exact outer packets, 266 recursive member occurrences, 34,052 full relation guards, all 60,679 cross-lineage matrix pairs, and generated-file freshness.

## Rebuild deterministic projections

```bash
python scripts/build-genealogy-corpus.py --root .
python scripts/check-genealogy-corpus.py --root .
```

The builder deletes and recreates only each lineage's generated `corpus/` directory and the declared generated JSON projections. It never changes packet ZIPs or source prompts. A clean rebuild must produce no Git diff.

## Add or replace a frozen packet

This corpus is frozen. A future, separately governed update must:

1. preserve the old packet identity in history;
2. add the new raw occurrence and exact hash to `CORPUS_SOURCE_LOCK.json`;
3. retain the complete new denominator rather than selecting only favourable rows;
4. regenerate projections;
5. run positive and mutation-based negative controls;
6. explain any denominator or source-selection change.

Target-repository crosswalks, implementation conclusions and release decisions do not belong in lineage README files or frozen packet members.

## Bind and resolve exact public content

After generation or a reviewed documentation/script change, rebuild the content lock:

```bash
python scripts/build-public-custody-lock.py --root .
```

Record its printed SHA-256 independently. With that exact digest substituted for `REVIEWED_CUSTODY_LOCK_SHA256`, read complete original records:

```bash
python scripts/resolve-genealogy.py --root . --expected-custody-lock-sha256 REVIEWED_CUSTODY_LOCK_SHA256 --property EVOLVED_SOFTWARE_MAINTENANCE_AND_EVOLUTION::ESME-C001
python scripts/resolve-genealogy.py --root . --expected-custody-lock-sha256 REVIEWED_CUSTODY_LOCK_SHA256 --trifecta ama --relation AMA-R00001
python scripts/resolve-genealogy.py --root . --expected-custody-lock-sha256 REVIEWED_CUSTODY_LOCK_SHA256 --target-property EWM:EWM-048
python scripts/resolve-genealogy.py --root . --expected-custody-lock-sha256 REVIEWED_CUSTODY_LOCK_SHA256 --packet docs/research/genealogy/bwp/packet/EVOLVED_BWP_FROZEN_PACKET.zip --member EVOLVED_BWP_INTRA_CROSSWALK_MATRIX.json --json-pointer /pairs/0
```

For any archived source, select its exact `outer_packet`, ordered `archive_chain` and `member` from `ARCHIVE_OCCURRENCE_INDEX.json`. Repeat `--archive-chain MEMBER.zip` for each nested archive. Use `--output NEW_FILE` without a JSON pointer to extract exact member bytes. Existing outputs are refused. Bundled scripts are source material; the resolver never executes them. Full relation rows retain guard references; use the same member/pointer route to inspect the referenced constituent register and semantic profiles. Presence of guards is a custody check, not adjudication that they apply.

A future publisher must obtain an actual immutable repository commit from authorized publication, verify the full commit/ref identity, and bind it to the reviewed custody-lock SHA-256. Replace `--root .` with `--base-url VERIFIED_IMMUTABLE_HTTP_ROOT` for fresh retrieval. The placeholder is not a public URL or a publication claim. Use a fresh process with only the resolver, origin and expected lock digest; no downloaded packet cache or private run directory is needed. A local HTTP rehearsal proves portability only. Publication closure requires a real remote readback after publication.

## Reconstruct the separate target indexes

Copy the three exact neutral outer packets into a new temporary input directory (preserving names and verifying their source-lock hashes). Then run the existing target builder, without archive code execution:

```bash
python docs/research/implementaudit/triad-integration/build_intake.py --packets TEMPORARY_PACKET_DIRECTORY --output docs/research/implementaudit/triad-integration --check
```

It checks the original four target navigation projections for 747 properties, 34,052 relations and 268 contexts. Those historical target projections retain their original dispositions and proof limits. They do not incorporate or supersede the separately frozen corrective audit or the canonical successor's later decisions. All source-authored originals and bibliography identities remain in neutral custody. Neither normalization nor the count of bibliographic rows creates independent empirical support.

## Concrete reuse limits

`CUSTODY_REUSE_LIMITS.json` records the recursive member scan and concrete flagged passages. No external papers were downloaded or added. The retained bibliography/access limits are authored research metadata, not licenses to redistribute the referenced external works. A concrete restricted member, if later identified, must receive a per-member disposition and a faithful lawful replacement route; blanket withholding of the authored corpus is not the default. Exact frozen bytes must not be silently redacted or overwritten.
