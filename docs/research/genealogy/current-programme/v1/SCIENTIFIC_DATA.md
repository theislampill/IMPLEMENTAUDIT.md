# Scientific JSON storage

The human-readable research and its scientific interpretations are unchanged.
Four logical JSON datasets use lossless gzip storage to keep each stored file
small enough for the publication transport. Each original `.json` location is
now an explicit `scientific-json-storage-index/1` index linking to a sibling
`.json.gz` payload. The index is storage metadata; the complete scientific JSON
is inside the payload. These payloads contain only the already reviewed public
derived JSON datasets, not original private source archives.

## Datasets

Paths below are relative to this directory. Counts are measured from the original
JSON arrays, whose locations are also recorded in each index.

| Logical dataset and storage index | Gzip payload | Records | Array in original JSON |
| --- | --- | ---: | --- |
| [AMA EAOSE directions](families/ama/current/AMA-S-DIRECTIONS-EAOSE.json) | [JSON.gz](families/ama/current/AMA-S-DIRECTIONS-EAOSE.json.gz) | 8,492 | `/relations` |
| [BWP directions](families/bwp/current/data/relationships/directions.json) | [JSON.gz](families/bwp/current/data/relationships/directions.json.gz) | 15,841 | `/body/relations` |
| [BWP pairs](families/bwp/current/data/relationships/pairs.json) | [JSON.gz](families/bwp/current/data/relationships/pairs.json.gz) | 18,221 | `/body/pairs` |
| [DRF directions](families/drf/current/DRF-S-DIRECTIONS.json) | [JSON.gz](families/drf/current/DRF-S-DIRECTIONS.json.gz) | 16,840 | `/directions` |

## Read and verify

Use any standard gzip reader. For example, from this directory:

```sh
gzip -dc families/ama/current/AMA-S-DIRECTIONS-EAOSE.json.gz > /tmp/AMA-S-DIRECTIONS-EAOSE.original.json
```

The following Python standard-library example verifies both stored and original
bytes, checks the original Git blob identifier, and loads the complete JSON.
Change `index_path` to any of the four logical paths above.

```python
import gzip
import hashlib
import json
from pathlib import Path

index_path = Path("families/ama/current/AMA-S-DIRECTIONS-EAOSE.json")
index = json.loads(index_path.read_bytes())
assert index["schema"] == "scientific-json-storage-index/1"
payload = index["payload"]
stored = (index_path.parent / payload["href"]).read_bytes()
assert len(stored) == payload["bytes"]
assert hashlib.sha256(stored).hexdigest() == payload["sha256"]
original = gzip.decompress(stored)
expected = payload["uncompressed"]
assert len(original) == expected["bytes"]
assert hashlib.sha256(original).hexdigest() == expected["sha256"]
blob = b"blob " + str(len(original)).encode("ascii") + b"\0" + original
assert hashlib.sha1(blob).hexdigest() == expected["git_blob_sha1"]
data = json.loads(original)
```

Decompression restores every original byte, including every machine-readable
field, value, record, list order, source identifier, and interpretation boundary.
The index's `original_metadata` copies the original non-row metadata; its
`records` gives the original array pointer and measured row count. DRF's
`scientific_source_ids` lists the exact factored-evidence identifiers in its rows.
These summaries do not replace the full dataset or qualify its sources anew.

All relative references inside a payload remain relative to its original logical
file location, even if the bytes are read in memory or decompressed elsewhere.
In particular, BWP's `$scientific_ref` references still use the adjacent
`shared-records.json`; AMA context and interface references and DRF evidence
references retain their original meanings. Existing source currentness,
historical-state interpretation, and scientific reading rules continue to apply.
Consumers that previously parsed a logical `.json` file directly should recognize
the storage-index schema, follow `payload.href`, decompress, and then apply the
original scientific schema.

The gzip streams have zero modification time, no embedded filename, and
compression level 9. Recompression is unnecessary for reading or verification;
the SHA-256 values identify the exact stored and decompressed bytes.
