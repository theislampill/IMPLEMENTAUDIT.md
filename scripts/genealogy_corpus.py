#!/usr/bin/env python3
"""Deterministic preservation and validation for the Engineering Genealogy corpus."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any


SOURCE_LOCK = Path("docs/research/genealogy/CORPUS_SOURCE_LOCK.json")
CORPUS_MANIFEST = Path("docs/research/genealogy/CORPUS_MANIFEST.json")
PROPERTY_INDEX = Path("docs/research/genealogy/PROPERTY_MASTER_INDEX.json")
PROMPT_MANIFEST = Path("docs/research/genealogy/method/SOURCE_PROMPT_MANIFEST.json")


class CorpusError(RuntimeError):
    """A deterministic corpus contract failed."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(value))


def load_source_lock(root: Path) -> dict[str, Any]:
    path = root / SOURCE_LOCK
    if not path.is_file():
        raise CorpusError(f"missing source lock: {SOURCE_LOCK.as_posix()}")
    lock = read_json(path)
    if lock.get("schema") != "implementaudit-engineering-genealogy-source-lock-v1":
        raise CorpusError("unsupported corpus source-lock schema")
    return lock


def safe_member_path(name: str) -> PurePosixPath:
    member = PurePosixPath(name)
    if not name or member.is_absolute() or ".." in member.parts or "\\" in name:
        raise CorpusError(f"unsafe ZIP member path: {name!r}")
    return member


def nested_value(value: Any, dotted_path: str) -> Any:
    current = value
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise CorpusError(f"property root not found: {dotted_path}")
        current = current[part]
    return current


def first_present(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in record:
            return record[key]
    return "NOT_PRESENT_IN_SOURCE_SCHEMA"


def parse_json_property_ledger(data: bytes, root_key: str, member_sha256: str) -> list[dict[str, Any]]:
    document = json.loads(data.decode("utf-8"))
    records = nested_value(document, root_key)
    if not isinstance(records, list):
        raise CorpusError(f"JSON property root is not a list: {root_key}")
    rows: list[dict[str, Any]] = []
    pointer_root = "/" + "/".join(root_key.split("."))
    for ordinal, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise CorpusError(f"JSON property row {ordinal} is not an object")
        property_id = first_present(record, "PROPERTY_ID", "property_id")
        property_name = first_present(record, "PROPERTY_NAME", "property_name")
        if not isinstance(property_id, str) or not isinstance(property_name, str):
            raise CorpusError(f"JSON property row {ordinal} lacks string ID/name")
        rows.append(
            {
                "source_property_id": property_id,
                "property_name": property_name,
                "current_status": first_present(record, "CURRENT_STATUS", "current_status"),
                "mature_or_evolved_form": first_present(
                    record, "MATURE_OR_EVOLVED_FORM", "mature_or_evolved_form"
                ),
                "evidence_strength": first_present(record, "EVIDENCE_STRENGTH", "evidence_strength"),
                "source_ordinal": ordinal,
                "source_locator": {
                    "format": "json",
                    "json_pointer": f"{pointer_root}/{ordinal - 1}",
                    "member_sha256": member_sha256,
                },
                "source_row_sha256": sha256_bytes(
                    json.dumps(
                        record,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    ).encode("utf-8")
                ),
            }
        )
    return rows


_YAML_PROPERTY = re.compile(r"^(?P<indent>\s*)-\s+PROPERTY_ID:\s*(?P<value>.+?)\s*$")


def _unquote_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1].replace("''", "'")
    return value


def _yaml_field(lines: list[str], start: int, end: int, key: str) -> Any:
    pattern = re.compile(rf"^(?P<indent>\s*){re.escape(key)}:\s*(?P<value>.*)$")
    for index in range(start, end):
        match = pattern.match(lines[index])
        if not match:
            continue
        indent = len(match.group("indent"))
        parts = [match.group("value").strip()]
        cursor = index + 1
        while cursor < end:
            line = lines[cursor]
            if not line.strip():
                break
            leading = len(line) - len(line.lstrip())
            if leading <= indent:
                break
            stripped = line.strip()
            if re.match(r"^[A-Z][A-Z0-9_]*:\s*", stripped):
                break
            parts.append(stripped)
            cursor += 1
        value = " ".join(part for part in parts if part)
        return _unquote_yaml_scalar(value) if value else "NOT_PRESENT_IN_SOURCE_SCHEMA"
    return "NOT_PRESENT_IN_SOURCE_SCHEMA"


def parse_yaml_property_ledger(data: bytes, root_key: str, member_sha256: str) -> list[dict[str, Any]]:
    text = data.decode("utf-8")
    lines = text.splitlines()
    leaf_key = root_key.split(".")[-1]
    section_match = re.compile(rf"^(?P<indent>\s*){re.escape(leaf_key)}:\s*$")
    section_start = None
    section_indent = None
    for index, line in enumerate(lines):
        match = section_match.match(line)
        if match:
            section_start = index + 1
            section_indent = len(match.group("indent"))
            break
    if section_start is None or section_indent is None:
        raise CorpusError(f"YAML property root not found: {root_key}")

    section_end = len(lines)
    saw_property = False
    property_indent = None
    for index in range(section_start, len(lines)):
        line = lines[index]
        match = _YAML_PROPERTY.match(line)
        if match and property_indent is None:
            property_indent = len(match.group("indent"))
            saw_property = True
            continue
        if saw_property and line.strip():
            leading = len(line) - len(line.lstrip())
            if leading <= section_indent and not line.lstrip().startswith("-"):
                section_end = index
                break

    starts: list[tuple[int, re.Match[str]]] = []
    for index in range(section_start, section_end):
        line = lines[index]
        match = _YAML_PROPERTY.match(line)
        if match and (property_indent is None or len(match.group("indent")) == property_indent):
            starts.append((index, match))
    rows: list[dict[str, Any]] = []
    for position, (start, match) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else section_end
        property_id = _unquote_yaml_scalar(match.group("value"))
        property_name = _yaml_field(lines, start, end, "PROPERTY_NAME")
        if not isinstance(property_name, str) or property_name == "NOT_PRESENT_IN_SOURCE_SCHEMA":
            raise CorpusError(f"YAML property {property_id} lacks PROPERTY_NAME")
        source_segment = "\n".join(lines[start:end]).encode("utf-8")
        rows.append(
            {
                "source_property_id": property_id,
                "property_name": property_name,
                "current_status": _yaml_field(lines, start, end, "CURRENT_STATUS"),
                "mature_or_evolved_form": _yaml_field(lines, start, end, "MATURE_OR_EVOLVED_FORM"),
                "evidence_strength": _yaml_field(lines, start, end, "EVIDENCE_STRENGTH"),
                "source_ordinal": position + 1,
                "source_locator": {
                    "format": "yaml",
                    "line_start": start + 1,
                    "line_end": end,
                    "member_sha256": member_sha256,
                },
                "source_row_sha256": sha256_bytes(source_segment),
            }
        )
    return rows


def _declared_digest_fields(value: Any, prefix: str = "") -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if "sha256" in key.lower() or "digest" in key.lower():
                found.append({"field": path, "value": child})
            found.extend(_declared_digest_fields(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_declared_digest_fields(child, f"{prefix}[{index}]"))
    return found


def _lineage_directory(root: Path, lineage: dict[str, Any]) -> Path:
    return root / "docs" / "research" / "genealogy" / lineage["trifecta"] / lineage["lineage_slug"]


def _validate_packet(root: Path, lineage: dict[str, Any]) -> tuple[bytes, zipfile.ZipFile]:
    packet = root / lineage["packet_path"]
    if not packet.is_file():
        raise CorpusError(f"missing packet: {lineage['packet_path']}")
    data = packet.read_bytes()
    if len(data) != lineage["packet_bytes"]:
        raise CorpusError(f"packet byte-length mismatch: {lineage['packet_path']}")
    if sha256_bytes(data) != lineage["packet_sha256"]:
        raise CorpusError(f"packet SHA-256 mismatch: {lineage['packet_path']}")
    return data, zipfile.ZipFile(packet)


def compute_models(root: Path, require_extracted: bool = True) -> dict[str, Any]:
    lock = load_source_lock(root)
    expected = lock["expected"]
    lineages = lock["lineages"]
    if len(lineages) != expected["lineages"]:
        raise CorpusError("lineage population mismatch in source lock")
    if len({item["trifecta"] for item in lineages}) != expected["trifectas"]:
        raise CorpusError("trifecta population mismatch in source lock")

    corpus_files: list[dict[str, Any]] = []
    lineage_manifests: dict[Path, dict[str, Any]] = {}
    properties: list[dict[str, Any]] = []

    for lineage in lineages:
        packet_data, archive = _validate_packet(root, lineage)
        with archive:
            member_names = [info.filename for info in archive.infolist() if not info.is_dir()]
            for name in member_names:
                safe_member_path(name)
            if lineage["property_ledger_member"] not in member_names:
                raise CorpusError(f"property ledger absent from packet: {lineage['lineage_id']}")
            member_records: list[dict[str, Any]] = []
            lineage_dir = _lineage_directory(root, lineage)
            corpus_dir = lineage_dir / "corpus"
            for name in member_names:
                member_data = archive.read(name)
                member_path = corpus_dir.joinpath(*PurePosixPath(name).parts)
                if require_extracted:
                    if not member_path.is_file():
                        raise CorpusError(f"missing extracted member: {member_path.relative_to(root).as_posix()}")
                    if member_path.read_bytes() != member_data:
                        raise CorpusError(f"extracted member byte mismatch: {member_path.relative_to(root).as_posix()}")
                record = {
                    "member": name,
                    "path": member_path.relative_to(root).as_posix(),
                    "bytes": len(member_data),
                    "sha256": sha256_bytes(member_data),
                }
                member_records.append(record)
                corpus_files.append({"role": "extracted_member", **record})

            ledger_data = archive.read(lineage["property_ledger_member"])
            ledger_sha = sha256_bytes(ledger_data)
            if lineage["property_ledger_member"].lower().endswith(".json"):
                parsed = parse_json_property_ledger(ledger_data, lineage["property_root"], ledger_sha)
            else:
                parsed = parse_yaml_property_ledger(ledger_data, lineage["property_root"], ledger_sha)
            if len(parsed) != lineage["property_count"]:
                raise CorpusError(
                    f"property population mismatch for {lineage['lineage_id']}: "
                    f"expected {lineage['property_count']}, observed {len(parsed)}"
                )
            for row in parsed:
                row["global_property_key"] = f"{lineage['lineage_id']}::{row['source_property_id']}"
                row["trifecta"] = lineage["trifecta"]
                row["lineage_id"] = lineage["lineage_id"]
                row["lineage_name"] = lineage["lineage_name"]
                row["source_locator"]["packet_path"] = lineage["packet_path"]
                row["source_locator"]["member"] = lineage["property_ledger_member"]
                properties.append(row)

            manifest_member = lineage["embedded_manifest_member"]
            if manifest_member is None:
                embedded_manifest: dict[str, Any] = {
                    "status": "NOT_PRESENT_IN_PACKET",
                    "member": None,
                    "declared_digest_fields": [],
                }
            else:
                if manifest_member not in member_names:
                    raise CorpusError(f"declared embedded manifest absent: {manifest_member}")
                manifest_data = archive.read(manifest_member)
                manifest_json = json.loads(manifest_data.decode("utf-8"))
                embedded_manifest = {
                    "status": "PRESENT",
                    "member": manifest_member,
                    "bytes": len(manifest_data),
                    "sha256": sha256_bytes(manifest_data),
                    "declared_digest_fields": _declared_digest_fields(manifest_json),
                    "identity_note": (
                        "Declared packet/content digests retain their source-defined scope and are not treated "
                        "as the raw delivered ZIP SHA-256 unless the source explicitly says so."
                    ),
                }

            lineage_manifest = {
                "schema": "implementaudit-engineering-genealogy-lineage-manifest-v1",
                "trifecta": lineage["trifecta"],
                "lineage_id": lineage["lineage_id"],
                "lineage_name": lineage["lineage_name"],
                "packet": {
                    "path": lineage["packet_path"],
                    "bytes": len(packet_data),
                    "sha256": sha256_bytes(packet_data),
                    "identity_kind": "RAW_DELIVERED_ZIP_BYTES",
                },
                "embedded_manifest": embedded_manifest,
                "property_ledger": {
                    "member": lineage["property_ledger_member"],
                    "root": lineage["property_root"],
                    "properties": len(parsed),
                    "bytes": len(ledger_data),
                    "sha256": ledger_sha,
                },
                "members": member_records,
            }
            lineage_manifests[lineage_dir / "LINEAGE_MANIFEST.json"] = lineage_manifest
            corpus_files.append(
                {
                    "role": "frozen_packet",
                    "path": lineage["packet_path"],
                    "bytes": len(packet_data),
                    "sha256": sha256_bytes(packet_data),
                }
            )

    prompt_files: list[dict[str, Any]] = []
    for prompt in lock["source_prompts"]:
        path = root / prompt["path"]
        if not path.is_file():
            raise CorpusError(f"missing source prompt: {prompt['path']}")
        data = path.read_bytes()
        if len(data) != prompt["bytes"] or sha256_bytes(data) != prompt["sha256"]:
            raise CorpusError(f"source-prompt identity mismatch: {prompt['path']}")
        role = "source_prompt_manifest" if path.name.endswith("MANIFEST.json") else "source_prompt"
        record = {"role": role, "path": prompt["path"], "bytes": len(data), "sha256": sha256_bytes(data)}
        prompt_files.append(record)
        corpus_files.append(record)

    keys = [row["global_property_key"] for row in properties]
    if len(keys) != len(set(keys)):
        raise CorpusError("duplicate global property key in source ledgers")
    if len(properties) != expected["properties"]:
        raise CorpusError(f"property population mismatch: expected {expected['properties']}, observed {len(properties)}")
    bare_counts = Counter(row["source_property_id"] for row in properties)

    source_lock_data = (root / SOURCE_LOCK).read_bytes()
    corpus_manifest = {
        "schema": "implementaudit-engineering-genealogy-corpus-manifest-v1",
        "authority_boundary": "File identity projection; frozen packet members remain research-content authority.",
        "source_lock": {
            "path": SOURCE_LOCK.as_posix(),
            "bytes": len(source_lock_data),
            "sha256": sha256_bytes(source_lock_data),
        },
        "counts": {
            "trifectas": expected["trifectas"],
            "lineages": expected["lineages"],
            "properties": expected["properties"],
            "files": len(corpus_files),
            "bytes": sum(item["bytes"] for item in corpus_files),
        },
        "files": sorted(corpus_files, key=lambda item: (item["path"], item["role"])),
    }
    property_index = {
        "schema": "implementaudit-engineering-genealogy-property-master-index-v1",
        "authority_boundary": "Navigational projection only; exact frozen property ledgers remain research authority.",
        "global_key": "<LINEAGE_ID>::<SOURCE_PROPERTY_ID>",
        "counts": {
            "properties": len(properties),
            "unique_global_keys": len(set(keys)),
            "unique_bare_property_ids": len(bare_counts),
            "bare_property_id_collision_groups": sum(1 for count in bare_counts.values() if count > 1),
        },
        "properties": properties,
    }
    source_prompt_manifest = {
        "schema": "implementaudit-engineering-genealogy-source-prompt-manifest-v1",
        "authority_boundary": "Exact source-prompt identity inventory; generalised templates are separate derived method aids.",
        "files": sorted(prompt_files, key=lambda item: item["path"]),
    }
    return {
        "lock": lock,
        "lineage_manifests": lineage_manifests,
        "corpus_manifest": corpus_manifest,
        "property_index": property_index,
        "source_prompt_manifest": source_prompt_manifest,
    }


def build_corpus(root: Path) -> dict[str, Any]:
    root = root.resolve()
    lock = load_source_lock(root)
    for lineage in lock["lineages"]:
        lineage_dir = _lineage_directory(root, lineage)
        corpus_dir = lineage_dir / "corpus"
        if corpus_dir.exists():
            shutil.rmtree(corpus_dir)
        corpus_dir.mkdir(parents=True)
        _, archive = _validate_packet(root, lineage)
        with archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                member = safe_member_path(info.filename)
                destination = corpus_dir.joinpath(*member.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(info.filename))
    models = compute_models(root, require_extracted=True)
    for path, manifest in models["lineage_manifests"].items():
        write_json(path, manifest)
    write_json(root / CORPUS_MANIFEST, models["corpus_manifest"])
    write_json(root / PROPERTY_INDEX, models["property_index"])
    write_json(root / PROMPT_MANIFEST, models["source_prompt_manifest"])
    return models


def _is_absolute_local_path(value: str) -> bool:
    return bool(re.search(r"(?i)(?:^|[\s\"'])(?:[a-z]:[\\/]|/(?:users|home)/[^\s/]+/)", value))


def _validate_actual_property_index(root: Path, errors: list[str]) -> None:
    path = root / PROPERTY_INDEX
    if not path.is_file():
        errors.append(f"missing generated file: {PROPERTY_INDEX.as_posix()}")
        return
    try:
        index = read_json(path)
    except Exception as exc:  # pragma: no cover - diagnostic boundary
        errors.append(f"invalid property index JSON: {exc}")
        return
    rows = index.get("properties", [])
    keys = [row.get("global_property_key") for row in rows if isinstance(row, dict)]
    if len(keys) != len(set(keys)):
        errors.append("duplicate global property key")
    if len(rows) != 658:
        errors.append(f"property population mismatch: expected 658, observed {len(rows)}")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("property index contains a non-object row")
            continue
        locator = row.get("source_locator", {})
        packet = locator.get("packet_path")
        member = locator.get("member")
        if not isinstance(packet, str) or not isinstance(member, str):
            errors.append(f"dangling source locator: {row.get('global_property_key')}")
            continue
        packet_path = root / packet
        if not packet_path.is_file():
            errors.append(f"dangling source locator: {row.get('global_property_key')}")
            continue
        try:
            with zipfile.ZipFile(packet_path) as archive:
                if member not in archive.namelist():
                    errors.append(f"dangling source locator: {row.get('global_property_key')}")
        except zipfile.BadZipFile:
            errors.append(f"dangling source locator: {row.get('global_property_key')}")


def _validate_public_projection_paths(root: Path, errors: list[str]) -> None:
    candidates = [
        root / SOURCE_LOCK,
        root / CORPUS_MANIFEST,
        root / PROPERTY_INDEX,
        root / PROMPT_MANIFEST,
    ]
    genealogy = root / "docs" / "research" / "genealogy"
    candidates.extend(genealogy.glob("*/*/LINEAGE_MANIFEST.json"))
    candidates.extend(genealogy.glob("README.md"))
    candidates.extend(genealogy.glob("*/README.md"))
    candidates.extend(genealogy.glob("*/*/README.md"))
    for path in candidates:
        if path.is_file() and _is_absolute_local_path(path.read_text(encoding="utf-8")):
            errors.append(f"absolute local path in public projection: {path.relative_to(root).as_posix()}")


def _validate_neutral_readmes(root: Path, errors: list[str]) -> None:
    genealogy = root / "docs" / "research" / "genealogy"
    pattern = re.compile(r"(?i)(?:RXX\s+owner|\b(?:current|final|assigned|native)\b.{0,60}\bR\d{2}\b)")
    for path in genealogy.glob("*/*/README.md"):
        if pattern.search(path.read_text(encoding="utf-8")):
            errors.append(f"IMPLEMENTAUDIT-specific disposition in neutral README: {path.relative_to(root).as_posix()}")


def _validate_package(package: Path, errors: list[str]) -> None:
    if not package.is_file():
        errors.append(f"package not found: {package}")
        return
    try:
        with zipfile.ZipFile(package) as archive:
            if any("docs/research/genealogy" in name.replace("\\", "/").lower() for name in archive.namelist()):
                errors.append("genealogy content entered distributable package")
    except zipfile.BadZipFile:
        errors.append(f"package is not a ZIP archive: {package}")


def check_corpus(root: Path, package: Path | None = None) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    try:
        lock = load_source_lock(root)
        expected_dirs = {_lineage_directory(root, lineage) for lineage in lock["lineages"]}
        if any(not path.is_dir() for path in expected_dirs):
            errors.append("lineage population mismatch")
        required_docs = [
            root / "docs/research/genealogy/README.md",
            root / "docs/research/genealogy/RESEARCH_METHOD.md",
            root / "docs/research/genealogy/REPLICATION_GUIDE.md",
            root / "docs/research/genealogy/method/templates/EVOLVED_LINEAGE_RESEARCH_PROMPT_TEMPLATE.md",
            root / "docs/research/genealogy/method/templates/EVOLVED_LINEAGE_DEPTH_REOPEN_PROMPT_TEMPLATE.md",
            root / "docs/research/genealogy/method/templates/EVOLVED_TRIFECTA_SYNTHESIS_PROMPT_TEMPLATE.md",
        ]
        required_docs.extend(root / f"docs/research/genealogy/{trifecta}/README.md" for trifecta in ("law", "css", "ssd", "drf"))
        required_docs.extend(path / "README.md" for path in expected_dirs)
        for path in required_docs:
            if not path.is_file():
                errors.append(f"missing required genealogy documentation: {path.relative_to(root).as_posix()}")
    except Exception as exc:
        return [str(exc)]

    _validate_actual_property_index(root, errors)
    _validate_public_projection_paths(root, errors)
    _validate_neutral_readmes(root, errors)
    if package is not None:
        _validate_package(package, errors)

    try:
        expected = compute_models(root, require_extracted=True)
    except Exception as exc:
        errors.append(str(exc))
        return sorted(set(errors))

    comparisons = {
        CORPUS_MANIFEST: expected["corpus_manifest"],
        PROPERTY_INDEX: expected["property_index"],
        PROMPT_MANIFEST: expected["source_prompt_manifest"],
    }
    comparisons.update(
        {path.relative_to(root): value for path, value in expected["lineage_manifests"].items()}
    )
    for relative, value in comparisons.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing generated file: {relative.as_posix()}")
        elif path.read_bytes() != json_bytes(value):
            errors.append(f"generated projection is stale or modified: {relative.as_posix()}")
    return sorted(set(errors))
