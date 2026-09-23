# Engineering Genealogy

This directory preserves a repository-neutral research corpus covering seven engineering trifectas, twenty-one selected frozen lineages, and 1,405 lineage-scoped properties. It retains exact delivered lineage ZIPs and extracted members, plus the exact compressed SSS/BWP/AMA synthesis packets and every recursively nested ancestry occurrence.

The corpus is research evidence, not implementation authority. It does not assign properties to a target repository, prescribe a runtime topology, or establish release status. `CORPUS_MANIFEST.json` records file identities; `PROPERTY_MASTER_INDEX.json` provides navigational locators back to the authoritative frozen property ledgers.

The earlier four-trifecta retention layer is historical source evidence. The additional SSS/BWP/AMA custody is a proposed repository-only expansion until separately published. Research remains excluded from plugin and standalone runtime payloads; custody does not activate or qualify a target reabsorption campaign.

## Trifectas

| Trifecta | Lineages | Properties |
|---|---:|---:|
| [LAW](law/) | 3 | 106 |
| [CSS](css/) | 3 | 195 |
| [SSD](ssd/) | 3 | 198 |
| [DRF](drf/) | 3 | 159 |
| [05 SSS](sss/) | 3 | 235 |
| [06 BWP](bwp/) | 3 | 234 |
| [07 AMA](ama/) | 3 | 278 |
| **Total** | **21** | **1,405** |

## Identity layers

- `packet/` contains exact raw delivered ZIP bytes.
- `corpus/` contains exact member bytes extracted without text normalisation.
- `LINEAGE_MANIFEST.json` records lineage-local packet, member, embedded-manifest and property-ledger identity.
- `CORPUS_SOURCE_LOCK.json` records the selected source occurrences and expected denominator.
- `CORPUS_MANIFEST.json` is a deterministic file-identity projection.
- `PROPERTY_MASTER_INDEX.json` is a deterministic navigation projection; it does not replace source rows.

Some source manifests declare normalised packet or content digests whose scope differs from the raw delivered ZIP. Both identities are preserved and labelled rather than compared as though they were the same claim. Evolved Lean and Evolved Agile contain no embedded packet manifest; that absence is recorded explicitly.

See [RESEARCH_METHOD.md](RESEARCH_METHOD.md) for the retained method and [REPLICATION_GUIDE.md](REPLICATION_GUIDE.md) for deterministic reconstruction.

## Complete source retrieval

The earlier 658 selected properties remain unchanged; the nine newly selected lineages add 747. Earlier A/B occurrences and duplicate embeddings remain in the exact archives and do not increase the selected denominator or evidence independence. `ARCHIVE_OCCURRENCE_INDEX.json` inventories all 266 new recursive member occurrences; each new family’s `TRIFECTA_MANIFEST.json` binds its complete compressed synthesis contents, full guarded relations and complete Cartesian pair matrix, including negative/unresolved rows. Reports, tensions, configurations, rejected novelty, source/access records and reconstruction code remain retrievable without executing archive code.

The master property index resolves to each full original lineage record, including canonical ESME/EAOSE records and their antecedent links. `scripts/resolve-genealogy.py` also reads complete relation records, arbitrary exact nested members, and JSON pointers. It verifies a separately supplied custody-lock digest and all retrieved file bytes. It uses one local root or one HTTP origin with no disk cache; see the replication guide. `../PUBLIC_CUSTODY_LOCK.json` binds neutral custody and the separate historical target projection without merging their semantic authority. Publication and fresh remote retrieval must be evidenced separately.
