# Replication Guide

## Verify the committed corpus

From the repository root:

```bash
python scripts/check-genealogy-corpus.py --root .
```

The checker verifies four trifectas, twelve lineage directories, raw ZIP identities, exact extracted-member parity, embedded-manifest identity, 658 unique lineage-scoped property locators, source-prompt identities, neutral projection hygiene and generated-file freshness.

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
