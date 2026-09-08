#!/usr/bin/env python3
"""Reproduce bounded navigation indexes from the three exact frozen archives."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath


PACKETS = {
    "SSS": (11344299, "920a87ca2a24a792d419ae30a70ced530377e73911f910f06b992c87d8765f31", 235),
    "BWP": (5322062, "6e3c95f7c81e5bbac67880f6ff58d360112e706d3469edbd8da425cb61233214", 234),
    "AMA": (10534831, "1c9654ab3017ecccdd3b24810b20ac23a5b51a5c19c1a488b64a2684dade026f", 278),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def build(packets: Path) -> dict[str, bytes]:
    locks, properties, relations, contexts = [], [], [], []
    for group, (size, sha256, population) in PACKETS.items():
        archive = packets / f"EVOLVED_{group}_FROZEN_PACKET.zip"
        data = archive.read_bytes()
        require(len(data) == size and digest(data) == sha256, f"archive identity mismatch: {archive.name}")
        with zipfile.ZipFile(io.BytesIO(data)) as source:
            names = source.namelist()
            require(len(names) == len(set(names)), f"duplicate members: {group}")
            for name in names:
                path = PurePosixPath(name)
                require(not path.is_absolute() and ".." not in path.parts and "\\" not in name,
                        f"unsafe member: {name}")
            members = {name: source.read(name) for name in names}
        manifest_name = f"EVOLVED_{group}_FROZEN_MANIFEST.json"
        manifest = json.loads(members[manifest_name])
        inventory = manifest["payload_inventory"]
        declared = set()
        for row in inventory:
            name = row.get("filename") or row["path"]
            require(name not in declared, f"duplicate inventory member: {name}")
            declared.add(name)
            payload = members[name]
            require(len(payload) == row["bytes"] and digest(payload) == row["sha256"],
                    f"embedded identity mismatch: {name}")
        require(declared | {manifest_name} == set(names), f"inventory coverage mismatch: {group}")
        locks.append({"trifecta": group, "archive": archive.name, "bytes": size, "sha256": sha256,
                      "inherited_properties": population,
                      "members": [{"path": name, "bytes": len(payload), "sha256": digest(payload)}
                                  for name, payload in sorted(members.items())]})
        intake_name = f"EVOLVED_{group}_INTER_CROSSWALK_INTAKE.json"
        intake = json.loads(members[intake_name])["rows"]
        items = enumerate(intake) if isinstance(intake, list) else intake.items()
        start = len(properties)
        for ordinal, row in items:
            key = row.get("global_qualified_key") or row["key"]
            pointer_key = str(ordinal).replace("~", "~0").replace("/", "~1")
            properties.append({
                "key": key, "trifecta": group, "lineage": row["lineage"],
                "name": row.get("property_name") or row["name"],
                "inherited_disposition": row["disposition"],
                "bearer": row["bearer"], "criterion": row["criterion"], "trigger": row["trigger"],
                "non_trigger": row.get("non_trigger_cheap_path", row.get("non_trigger")),
                "source_ids": row["source_ids"],
                "source_pointer": intake_name + "#/rows/" + pointer_key,
                "source_row_sha256": digest(canonical(row)),
                "source_member_sha256": digest(members[intake_name]),
                "adoption_decision": "NOT_DERIVED_BY_INTAKE_BUILDER",
            })
        require(len(properties) - start == population, f"property population mismatch: {group}")
        relation_name = f"EVOLVED_{group}_DIRECTIONAL_RELATION_LEDGER.json"
        for ordinal, row in enumerate(json.loads(members[relation_name])["relations"]):
            relations.append({
                "id": row.get("relation_id") or row["id"], "trifecta": group,
                "source": row["source_property"], "target": row["target_property"],
                "type": row.get("relation_type") or row["type"],
                "clusters": row.get("cluster_ids", []), "tensions": row.get("tension_ids", []),
                "source_pointer": relation_name + "#/relations/" + str(ordinal),
                "source_row_sha256": digest(canonical(row)),
            })
        for suffix, keys in [
            ("CONVERGENCE_AND_COMPOSITION_CLUSTERS", ["clusters", "one_to_many_composition_bundles"]),
            ("TENSION_LEDGER", ["tensions"]),
            ("ALTERNATIVE_CONFIGURATIONS", ["configurations"]),
            ("COMPOSITION_INDUCED_PROPERTY_LEDGER", ["rejected_candidates"]),
        ]:
            name = f"EVOLVED_{group}_{suffix}.json"
            document = json.loads(members[name])
            for key in keys:
                for ordinal, row in enumerate(document.get(key, [])):
                    contexts.append({"trifecta": group, "kind": key,
                                     "id": row.get("id") or row.get("cluster_id") or row.get("candidate_id")
                                     or row.get("configuration_id") or row.get("tension_id") or row.get("bundle_id"),
                                     "name": row.get("name") or row.get("title") or row.get("proposed_name")
                                     or row.get("originating_criterion"),
                                     "source_pointer": name + "#/" + key + "/" + str(ordinal),
                                     "source_row_sha256": digest(canonical(row))})
    known = {row["key"] for row in properties}
    require(len(properties) == len(known) == 747, "property identity loss or collision")
    require(len(relations) == len({row["id"] for row in relations}) == 34052, "relation identity loss or collision")
    require(all(row["source"] in known and row["target"] in known for row in relations), "unknown endpoint")
    require(len(contexts) == 268, "composition-context population mismatch")
    require(all(isinstance(row["id"], str) and isinstance(row["name"], str) for row in contexts),
            "composition context lacks identity or description")
    pretty = lambda value: (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    return {
        "SOURCE_LOCK.json": pretty({"schema": "implementaudit.triad-source-lock.v1", "packets": locks}),
        "PROPERTY_INDEX.json": pretty(properties),
        "RELATION_INDEX.jsonl": b"".join(canonical(row) + b"\n" for row in relations),
        "CONTEXT_INDEX.json": pretty(contexts),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="compare existing outputs without writing")
    args = parser.parse_args()
    outputs = build(args.packets)
    if args.check:
        for name, data in outputs.items():
            require((args.output / name).read_bytes() == data, f"generated output mismatch: {name}")
    else:
        args.output.mkdir(parents=True, exist_ok=True)
        for name, data in outputs.items():
            (args.output / name).write_bytes(data)
    sys.stdout.write("INTAKE_IDENTITY_VERIFIED properties=747 relations=34052 contexts=268 adoption=NOT_DERIVED\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
