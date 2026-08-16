# Engineering Genealogy

This directory preserves a repository-neutral research corpus covering four engineering trifectas, twelve frozen lineages, and 658 lineage-scoped properties. It retains both the exact delivered packet ZIPs and their exact extracted members.

The corpus is research evidence, not implementation authority. It does not assign properties to a target repository, prescribe a runtime topology, or establish release status. `CORPUS_MANIFEST.json` records file identities; `PROPERTY_MASTER_INDEX.json` provides navigational locators back to the authoritative frozen property ledgers.

This retention layer is included in the v0.4.0.0 repository/source state,
remains excluded from both plugin and standalone runtime payloads, and does not
activate the deferred v0.4.1 reabsorption campaign.

## Trifectas

| Trifecta | Lineages | Properties |
|---|---:|---:|
| [LAW](law/) | 3 | 106 |
| [CSS](css/) | 3 | 195 |
| [SSD](ssd/) | 3 | 198 |
| [DRF](drf/) | 3 | 159 |
| **Total** | **12** | **658** |

## Identity layers

- `packet/` contains exact raw delivered ZIP bytes.
- `corpus/` contains exact member bytes extracted without text normalisation.
- `LINEAGE_MANIFEST.json` records lineage-local packet, member, embedded-manifest and property-ledger identity.
- `CORPUS_SOURCE_LOCK.json` records the selected source occurrences and expected denominator.
- `CORPUS_MANIFEST.json` is a deterministic file-identity projection.
- `PROPERTY_MASTER_INDEX.json` is a deterministic navigation projection; it does not replace source rows.

Some source manifests declare normalised packet or content digests whose scope differs from the raw delivered ZIP. Both identities are preserved and labelled rather than compared as though they were the same claim. Evolved Lean and Evolved Agile contain no embedded packet manifest; that absence is recorded explicitly.

See [RESEARCH_METHOD.md](RESEARCH_METHOD.md) for the retained method and [REPLICATION_GUIDE.md](REPLICATION_GUIDE.md) for deterministic reconstruction.
