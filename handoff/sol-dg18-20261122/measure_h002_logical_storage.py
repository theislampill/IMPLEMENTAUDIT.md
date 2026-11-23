"""Measure the exact raw H002 archive and ref-bound object population as logical bytes."""
import argparse
import io
from pathlib import Path, PurePosixPath
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from receive_sealed_a5_cost import (RESULTS, PUBLISHED, git, need, oid, pin, read_pinned, sha, strict, zip_members)

SCOPE = "historical/h002/operation/receiver-packet/"
CARRIER = {
    "bytes": 4177344,
    "sha256": "cd1288b2d6d6f8172bf0e2a265aee8aa9d2b4648fe3ef8bb43d09d838968eae2",
}
CUSTODY_FILES = (
    "operation-evidence/INPUT_CUSTODY_BEFORE.json", "operation-evidence/INPUT_CUSTODY_AFTER.json",
)


def measurement(args):
    index = strict(git("cat-file", "blob", RESULTS + ":" + PUBLISHED))
    execution_pin = index["durable_exact_evidence"][0]
    execution_raw = read_pinned(args.execution, execution_pin)
    e, artifact = zip_members(execution_raw, 127)
    record = strict(e["original/stage2/CANONICAL_ALGEBRA.json"])
    prep = strict(e["FULL_PACKET_RECEIVING.json"])
    need({k: artifact["historical_carrier_not_duplicated"][k] for k in CARRIER}
         == {k: prep["archive"][k] for k in CARRIER} == CARRIER, "original carrier binding differs")
    raw = read_pinned(args.historical_carrier, CARRIER)
    refs = {row["ref"]: row for row in record["object_bindings"]}
    distinct = {}
    for row in refs.values():
        body_pin = {k: row[k] for k in ("bytes", "sha256")}
        existing = distinct.setdefault(row["oid"], body_pin)
        need(existing == body_pin, "ref aliases disagree on body identity")
    need(len(refs) == len(record["object_bindings"]) == 95 and len(distinct) == 86, "exact object/ref census differs")
    selected = {"CANDIDATE_MANIFEST.json": prep["exact_manifest"], "CANDIDATE_SEAL.json": prep["exact_seal"]}
    selected.update({SCOPE + "cold-readback/objects/" + o: p for o, p in distinct.items()})
    selected.update({SCOPE + "cold-readback/RESULT.json": None, SCOPE + "operation-evidence/COLD.json": None})
    selected.update({SCOPE + name: None for name in CUSTODY_FILES})
    actual = {}
    seen, expanded = set(), 0
    limit = prep["payload_bytes"] + prep["exact_manifest"]["bytes"] + prep["exact_seal"]["bytes"]
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r|gz") as h:
        for item in h:
            name = PurePosixPath(item.name)
            expanded += item.size
            need(item.isfile() and 0 <= item.size <= limit and expanded <= limit and len(seen) < 784
                 and not name.is_absolute() and item.name == name.as_posix() and ".." not in name.parts
                 and "\\" not in item.name and item.name not in seen, "unsafe or duplicate carrier member")
            seen.add(item.name)
            if item.name not in selected:
                continue
            expected = selected[item.name]
            need(item.size <= (expected["bytes"] if expected else 100_000), "selected body exceeded bound")
            with h.extractfile(item) as stream:
                body = stream.read(item.size + 1)
            need(len(body) == item.size and (not expected or pin(body) == expected), "selected body mismatch")
            actual[item.name] = body
    need(set(actual) == set(selected) and len(seen) == 784 and expanded == limit, "carrier census mismatch")
    manifest_bytes = actual["CANDIDATE_MANIFEST.json"]
    manifest = strict(manifest_bytes)
    need(strict(actual["CANDIDATE_SEAL.json"])["manifest_sha256"] == sha(manifest_bytes), "manifest seal mismatch")
    manifest_rows = {item["path"]: item for item in manifest["files"]}
    need(len(manifest_rows) == len(manifest["files"]) == 782
         and set(manifest_rows) | {"CANDIDATE_MANIFEST.json", "CANDIDATE_SEAL.json"} == seen, "manifest membership")
    for name, body in actual.items():
        if name in manifest_rows:
            need(pin(body) == {k: manifest_rows[name][k] for k in ("bytes", "sha256")}, "carrier manifest alias differs")

    readback = strict(actual[SCOPE + "cold-readback/RESULT.json"])
    need({x["ref"] + " " + x["oid"] for x in refs.values()} == set(readback["refs"])
         and len(readback["refs"]) == len(readback["objects"]) == 95, "actual raw ref readback differs")
    for ref, row in refs.items():
        need({k: row[k] for k in ("oid", "bytes", "sha256")} == {k: readback["objects"][ref][k] for k in ("oid", "bytes", "sha256")},
             "actual raw object descriptor differs")
    for expected_oid in distinct:
        data = actual[SCOPE + "cold-readback/objects/" + expected_oid]
        need(oid(data) == expected_oid, "actual retained blob differs")

    cold = strict(actual[SCOPE + "operation-evidence/COLD.json"])["resolved"]
    need(cold["pointer"] == record["pointer"] and cold["pointer_token"] == record["pointer_token"]
         and cold["receipt_token"] == record["receipt_token"], "wrong frozen H002 generation readback")
    manifests = [o for o, data_pin in distinct.items() if data_pin["sha256"] == cold["pointer"]["archive_manifest_sha256"]]
    need(len(manifests) == 1, "archive manifest blob is not unique")
    archive = strict(actual[SCOPE + "cold-readback/objects/" + manifests[0]])
    entries = archive["entries"]
    need(entries == record["archive_entries"] and len(entries) == 83, "actual archive manifest entries differ")
    archive_oids = {r["blob_oid"] for r in entries}
    need(archive_oids <= set(distinct) and len(archive_oids) == 76, "archive distinct OID census")
    for row in entries:
        need(pin(actual[SCOPE + "cold-readback/objects/" + row["blob_oid"]])
             == {"bytes": row["byte_length"], "sha256": row["sha256"]}, "archive entry actual body differs")
    opening, closing = [strict(actual[SCOPE + n]) for n in CUSTODY_FILES]
    need(len(opening["identities"]) == len(closing["identities"]) == 145
         and opening["identities"] == closing["identities"]
         and closing["all_bound_inputs_unchanged"], "operation input custody records differ")
    need(read_pinned(args.historical_carrier, CARRIER) == raw
         and read_pinned(args.execution, execution_pin) == execution_raw, "source archive changed")
    archive_gross = sum(r["byte_length"] for r in entries)
    archive_dedup = sum(distinct[o]["bytes"] for o in archive_oids)
    ref_gross = sum(r["bytes"] for r in refs.values())
    ref_dedup = sum(r["bytes"] for r in distinct.values())
    return {
        "schema": "dg18.a5.h002.logical-retained-objects.v1",
        "execution_zip": pin(execution_raw), "historical_carrier": pin(raw),
        "archive_manifest_sha256": cold["pointer"]["archive_manifest_sha256"],
        "archive_manifest_git_blob": manifests[0], "archive_manifest_body_bytes": distinct[manifests[0]]["bytes"],
        "archive_entries": len(entries), "archive_distinct_blobs": len(archive_oids),
        "archive_gross_body_bytes": archive_gross, "archive_deduplicated_body_bytes": archive_dedup,
        "archive_body_alias_bytes": archive_gross - archive_dedup,
        "ref_bindings": len(refs), "ref_distinct_blobs": len(distinct),
        "ref_gross_body_bytes": ref_gross, "ref_deduplicated_body_bytes": ref_dedup,
        "ref_body_alias_bytes": ref_gross - ref_dedup,
        "additional_distinct_ref_blobs": len(set(distinct) - archive_oids),
        "additional_distinct_ref_body_bytes": ref_dedup - archive_dedup,
        "raw_objects_verified_by_sha256_and_git_oid": len(distinct), "retained_input_identities_unchanged": 145,
        "physical_git_store_bytes_established": False, "causal_whole_store_baseline_established": False,
        "whole_store_cumulative_storage_established": False, "native_whole_operation_cost_established": False,
        "historical_work_replayed": False, "new_award": False,
    }


if __name__ == "__main__":
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execution", type=Path, required=True)
    parser.add_argument("--historical-carrier", type=Path, required=True)
    print(json.dumps(measurement(parser.parse_args()), indent=2))
