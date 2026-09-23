#!/usr/bin/env python3
"""Deterministic F2 archive helper plus bounded immutable-lineage publisher.

The publisher can only CAS one already-stored current-generation pointer under
internally derived controller custody.  It never selects a live source owner,
writes R0011/receipts/markers, or advances any lifecycle state. The explicit
recovery re-entry orchestrator separately invokes existing owners only after
fresh terminal recovery validation and owner-realised canonical reconciliation.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import ctypes
import hashlib
import hmac
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import unicodedata
import zlib
from pathlib import Path
from typing import Any, Mapping, NamedTuple, Sequence

# The controller's existing source identity transitively binds this new owner.
# Rebind both reviewed files together; missing, aliased or changed bytes fail closed.
_HOT_PROJECTION_MODULE_SHA256 = '0c5fb125e59b3493c2f3c9baf6a7704ccb2b5fc486f9363a028055f3d6cfad7c'
_HOT_PROJECTION_MODULE_BYTES = 12058
def _load_hot_projection_module():
    import hashlib as _hashlib
    import os as _os
    import stat as _stat
    import sys as _sys
    import types as _types
    _path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'canonical_hot_projection.py')
    _fd = None
    try:
        _before = _os.lstat(_path)
        if (_stat.S_ISLNK(_before.st_mode) or not _stat.S_ISREG(_before.st_mode)
                or getattr(_before, "st_file_attributes", 0) & 0x400):
            raise ImportError("canonical_hot_projection.py: source is not a non-aliased regular file")
        _flags = _os.O_RDONLY | getattr(_os, "O_BINARY", 0) | getattr(_os, "O_NONBLOCK", 0) | getattr(_os, "O_NOFOLLOW", 0)
        _fd = _os.open(_path, _flags)
        _info = _os.fstat(_fd)
        if (not _stat.S_ISREG(_info.st_mode) or (_before.st_dev, _before.st_ino) != (_info.st_dev, _info.st_ino)):
            raise ImportError("canonical_hot_projection.py: source identity changed while opening")
        with _os.fdopen(_fd, "rb") as _stream:
            _fd = None
            _source = _stream.read(_HOT_PROJECTION_MODULE_BYTES + 1)
    except OSError as _exc:
        raise ImportError("canonical_hot_projection.py: source unavailable") from _exc
    finally:
        if _fd is not None:
            _os.close(_fd)
    if len(_source) != _HOT_PROJECTION_MODULE_BYTES or _hashlib.sha256(_source).hexdigest() != _HOT_PROJECTION_MODULE_SHA256:
        raise ImportError("canonical_hot_projection.py: source identity mismatch")
    _module = _types.ModuleType(__name__ + ".hot_projection_module")
    _module.__file__ = _path
    # Register before execution for annotations/introspection; undo a failed load.
    _previous = _sys.modules.get(_module.__name__)
    _sys.modules[_module.__name__] = _module
    try:
        exec(compile(_source, _path, "exec"), _module.__dict__)
    except BaseException:
        if _previous is None:
            _sys.modules.pop(_module.__name__, None)
        else:
            _sys.modules[_module.__name__] = _previous
        raise
    return _module
_hot_projection_module = _load_hot_projection_module()



ZERO_OID = "0" * 40
ARCHIVE_PREFIX = "refs/implementaudit/state-archives"
MIGRATION_CLASSIFICATION_PREFIX = (
    "refs/implementaudit/state-migration-classifications")
FORBIDDEN_TRANSITION_FIELDS = {
    "current_generation",
    "epoch",
    "invalidation_oid",
    "migration_marker",
    "pointer_oid",
    "predecessor_receipt",
    "receipt_oid",
}
FORBIDDEN_SOURCE_COMPONENTS = ["state-generations", "state-archives", "quarantine"]
EXPECTED_RESULTS = {
    "draft_schema": "implementaudit.canonical-state-projection-draft.v1",
    "archive_schema": "implementaudit.canonical-state-archive.v1",
    "archive_ref_update": "EXPECTED_ZERO_CAS",
    "discovery": "EXCLUDED",
    "recursive_population": "EXCLUDED",
    "retrieval": "GIT_BLOB_OID_AND_SHA256",
    "permissions": "SOURCE_MODE_EXACT_READBACK",
}


class RotationError(RuntimeError):
    """A fail-closed draft/archive contract violation."""


CLASSIFICATIONS_V1 = (
    "HOT_CURRENT",
    "HOT_POINTER",
    "COLD_HISTORY",
    "ON_DEMAND_EVIDENCE",
    "DUPLICATE_DERIVABLE",
)
REMOVED_CLASSIFICATIONS_V1 = frozenset({"COLD_HISTORY", "ON_DEMAND_EVIDENCE"})
LEGACY_RECORD_ID = re.compile(r"^ialegacy-v1-[0-9a-f]{64}$")
DERIVATION_SOURCE_ID = re.compile(
    r"^git:[0-9a-f]{40}:skills/implementaudit/templates/(?:STATE|ROADMAP)\.md$")


class DerivationSource(NamedTuple):
    owner: str
    source_id: str
    source_bytes: bytes


class DerivationPointer(NamedTuple):
    schema: str
    owner: str
    source_id: str
    source_digest: str
    operation: str
    selector: str
    derived_digest: str


class MaterializedMigrationInputs(NamedTuple):
    sources: dict[str, bytes]
    population_digest: str
    derivation_operation: str


class ClassificationFixture(NamedTuple):
    sources: dict[str, tuple[dict[str, object], ...]]
    derivation_sources: dict[str, DerivationSource]
    classes: tuple[str, ...] = CLASSIFICATIONS_V1

    @classmethod
    def from_mapping(cls, value: object,
                     derivation_sources: Mapping[str, DerivationSource]) -> "ClassificationFixture":
        if (type(value) is not dict
                or set(value) != {"schema", "classes", "sources"}
                or value.get("schema")
                != "implementaudit.hot-cold-section-classification.v1"
                or value.get("classes") != list(CLASSIFICATIONS_V1)):
            raise RotationError("classification fixture schema is invalid")
        normalized_derivations = _validate_derivation_sources_v1(derivation_sources)
        raw_sources = value.get("sources")
        if type(raw_sources) is not dict or set(raw_sources) != {"STATE.md", "ROADMAP.md"}:
            raise RotationError("classification fixture source population is invalid")
        normalized: dict[str, tuple[dict[str, object], ...]] = {}
        for source_name in ("STATE.md", "ROADMAP.md"):
            source = raw_sources[source_name]
            if type(source) is not dict or set(source) != {"sections"}:
                raise RotationError("classification fixture source schema is invalid")
            sections = source["sections"]
            if type(sections) is not list or not sections:
                raise RotationError("classification fixture section population is empty")
            headings: set[str] = set()
            literal_rows: set[str] = set()
            stored: list[dict[str, object]] = []
            for section in sections:
                if type(section) is not dict:
                    raise RotationError("classification section is malformed")
                allowed = {"heading", "classification", "record_kind",
                           "derivation_pointer", "tables", "records"}
                if not set(section).issubset(allowed) or not {
                        "heading", "classification", "record_kind"}.issubset(section):
                    raise RotationError("classification section keys are invalid")
                heading = section["heading"]
                classification = section["classification"]
                record_kind = section["record_kind"]
                pointer = section.get("derivation_pointer")
                if (type(heading) is not str or not heading.startswith("#")
                        or heading in headings or type(record_kind) is not str
                        or not record_kind or classification not in CLASSIFICATIONS_V1):
                    raise RotationError("classification section identity is invalid")
                _verify_derivation_pointer_v1(
                    classification, pointer, record_kind, normalized_derivations)
                headings.add(heading)
                records = section.get("records", [])
                tables = section.get("tables", [])
                if type(records) is not list or type(tables) is not list:
                    raise RotationError("classification section partitions are invalid")
                for record in records:
                    _validate_explicit_classification_row_v1(record)
                    _verify_derivation_pointer_v1(
                        record["classification"], record.get("derivation_pointer"),
                        record["record_kind"], normalized_derivations)
                    line = record["source_line"]
                    if line in literal_rows:
                        raise RotationError("classification rules overlap")
                    literal_rows.add(line)
                table_headers: set[str] = set()
                for table in tables:
                    if (type(table) is not dict
                            or set(table) != {"header", "delimiter", "rows"}
                            or type(table["header"]) is not str
                            or type(table["delimiter"]) is not str
                            or type(table["rows"]) is not list
                            or not table["rows"]
                            or table["header"] in table_headers):
                        raise RotationError("classification table schema is invalid")
                    table_headers.add(table["header"])
                    for row in table["rows"]:
                        _validate_explicit_classification_row_v1(row)
                        _verify_derivation_pointer_v1(
                            row["classification"], row.get("derivation_pointer"),
                            row["record_kind"], normalized_derivations)
                        line = row["source_line"]
                        if line in literal_rows:
                            raise RotationError("classification rules overlap")
                        literal_rows.add(line)
                stored.append(json.loads(json.dumps(section, ensure_ascii=False)))
            normalized[source_name] = tuple(stored)
        return cls(sources=normalized, derivation_sources=normalized_derivations)


def _validate_derivation_sources_v1(
        sources: Mapping[str, DerivationSource]) -> dict[str, DerivationSource]:
    if type(sources) is not dict:
        raise RotationError("derivation source population is invalid")
    normalized: dict[str, DerivationSource] = {}
    for source_id, source in sources.items():
        if (type(source_id) is not str or not DERIVATION_SOURCE_ID.fullmatch(source_id)
                or type(source) is not DerivationSource or source.source_id != source_id
                or source.owner != "R0039" or type(source.source_bytes) is not bytes
                or not source.source_bytes):
            raise RotationError("derivation source identity is invalid")
        try:
            source.source_bytes.decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise RotationError("derivation source is not UTF-8") from exc
        normalized[source_id] = source
    return normalized


def _extract_markdown_section_v1(source_bytes: bytes, selector: str) -> bytes:
    if type(selector) is not str or not selector.startswith("# "):
        raise RotationError("derivation selector is invalid")
    lines = source_bytes.splitlines(keepends=True)
    matches = [index for index, line in enumerate(lines)
               if line.rstrip(b"\r\n").decode("utf-8", "strict") == selector]
    if len(matches) != 1:
        raise RotationError("derivation selector is unresolved")
    start_index = matches[0]
    end_index = start_index + 1
    while end_index < len(lines):
        line = lines[end_index].rstrip(b"\r\n")
        if line.startswith(b"# ") or line.startswith(b"## "):
            break
        end_index += 1
    return b"".join(lines[start_index:end_index])


def _verify_derivation_pointer_v1(
        classification: object, pointer: object, record_kind: object,
        sources: Mapping[str, DerivationSource]) -> DerivationPointer | None:
    if classification == "DUPLICATE_DERIVABLE":
        raw = pointer._asdict() if type(pointer) is DerivationPointer else pointer
        keys = {"schema", "owner", "source_id", "source_digest", "operation",
                "selector", "derived_digest"}
        if (type(raw) is not dict or set(raw) != keys
                or record_kind != "template.identity"
                or raw["schema"] != "implementaudit.derivation-pointer.v1"
                or raw["owner"] != "R0039"
                or type(raw["source_id"]) is not str
                or not DERIVATION_SOURCE_ID.fullmatch(raw["source_id"])
                or type(raw["source_digest"]) is not str
                or not SHA_ID.fullmatch(raw["source_digest"])
                or raw["operation"] != "markdown-section-v1"
                or type(raw["selector"]) is not str
                or type(raw["derived_digest"]) is not str
                or not SHA_ID.fullmatch(raw["derived_digest"])):
            raise RotationError("duplicate-derivable record lacks exact derivation pointer")
        source = sources.get(raw["source_id"])
        if source is None or source.owner != raw["owner"]:
            raise RotationError("duplicate-derivable source is unresolved or wrong-owner")
        observed_source_digest = "sha256:" + hashlib.sha256(source.source_bytes).hexdigest()
        if not hmac.compare_digest(str(raw["source_digest"]), observed_source_digest):
            raise RotationError("duplicate-derivable source digest disagrees")
        derived = _extract_markdown_section_v1(source.source_bytes, str(raw["selector"]))
        observed_derived_digest = "sha256:" + hashlib.sha256(derived).hexdigest()
        if not hmac.compare_digest(str(raw["derived_digest"]), observed_derived_digest):
            raise RotationError("duplicate-derivable bytes disagree")
        return DerivationPointer(**raw)
    elif pointer is not None:
        raise RotationError("derivation pointer is only valid for duplicate-derivable records")
    return None


def _validate_explicit_classification_row_v1(row: object) -> None:
    if (type(row) is not dict
            or not set(row).issubset({"source_line", "classification", "record_kind",
                                      "derivation_pointer"})
            or set(row) - {"derivation_pointer"}
            != {"source_line", "classification", "record_kind"}
            or type(row["source_line"]) is not str or not row["source_line"]
            or "\n" in row["source_line"] or "\r" in row["source_line"]
            or row["classification"] not in CLASSIFICATIONS_V1
            or type(row["record_kind"]) is not str or not row["record_kind"]):
        raise RotationError("explicit classification row is invalid")


def load_materialized_migration_preimages_v1(
        population: object) -> MaterializedMigrationInputs:
    if type(population) is not dict:
        raise RotationError("materialized migration preimage fixture is invalid")
    fixture = population.get("materialized_migration_preimages")
    if (type(fixture) is not dict
            or set(fixture) != {"derivation_operation", "population_digest", "sources"}
            or fixture["derivation_operation"]
            != "inject-explicit-classification-records-v1"
            or type(fixture["population_digest"]) is not str
            or not HEX_SHA256.fullmatch(fixture["population_digest"])
            or type(fixture["sources"]) is not dict
            or set(fixture["sources"]) != {"STATE.md", "ROADMAP.md"}):
        raise RotationError("materialized migration preimage fixture is invalid")
    sources: dict[str, bytes] = {}
    population_rows: list[list[object]] = []
    for name in ("STATE.md", "ROADMAP.md"):
        encoded = fixture["sources"][name]
        if (type(encoded) is not dict
                or set(encoded) != {"encoding", "byte_count", "sha256", "bytes"}
                or encoded["encoding"] != "zlib+base64"
                or type(encoded["byte_count"]) is not int
                or encoded["byte_count"] < 1
                or type(encoded["sha256"]) is not str
                or not HEX_SHA256.fullmatch(encoded["sha256"])
                or type(encoded["bytes"]) is not str or not encoded["bytes"]):
            raise RotationError("materialized migration preimage source is invalid")
        try:
            compressed = base64.b64decode(encoded["bytes"], validate=True)
            if base64.b64encode(compressed).decode("ascii") != encoded["bytes"]:
                raise ValueError("non-canonical base64")
            decompressor = zlib.decompressobj()
            raw = decompressor.decompress(compressed) + decompressor.flush()
            if not decompressor.eof or decompressor.unused_data:
                raise ValueError("non-canonical zlib stream")
            raw.decode("utf-8", "strict")
        except (ValueError, UnicodeDecodeError, zlib.error) as exc:
            raise RotationError("materialized migration preimage bytes are invalid") from exc
        digest = hashlib.sha256(raw).hexdigest()
        if (len(raw) != encoded["byte_count"]
                or not hmac.compare_digest(digest, str(encoded["sha256"]))):
            raise RotationError("materialized migration preimage identity disagrees")
        sources[name] = raw
        population_rows.append([name, len(raw), digest])
    observed_population = hashlib.sha256(canonical_json_v1(population_rows)).hexdigest()
    if not hmac.compare_digest(observed_population, str(fixture["population_digest"])):
        raise RotationError("materialized migration preimage population disagrees")
    return MaterializedMigrationInputs(
        sources=sources, population_digest=observed_population,
        derivation_operation=str(fixture["derivation_operation"]))


def _materialize_migration_source_v1(
        frozen: bytes, sections: Sequence[Mapping[str, object]]) -> bytes:
    try:
        text = frozen.decode("utf-8", "strict").replace("\r\n", "\n")
    except UnicodeDecodeError as exc:
        raise RotationError("frozen template source is not UTF-8") from exc
    for index in range(len(sections) - 1, -1, -1):
        section = sections[index]
        heading = section["heading"]
        if type(heading) is not str:
            raise RotationError("materialized preimage derivation is invalid")
        try:
            start = text.index(heading + "\n")
            end = (len(text) if index + 1 == len(sections)
                   else text.index(str(sections[index + 1]["heading"]) + "\n", start))
        except ValueError as exc:
            raise RotationError("materialized preimage derivation is unresolved") from exc
        block = text[start:end]
        for table in section.get("tables", []):
            prefix = str(table["header"]) + "\n" + str(table["delimiter"]) + "\n"
            try:
                table_start = block.index(prefix) + len(prefix)
                population_end = table_start
                while block[population_end:].startswith("|"):
                    population_end = block.index("\n", population_end) + 1
            except ValueError as exc:
                raise RotationError("materialized preimage table derivation is unresolved") from exc
            rows = "\n".join(str(row["source_line"]) for row in table["rows"])
            block = (block[:table_start] + rows + "\n\n"
                     + block[population_end:].lstrip("\n"))
        literal_rows = [str(row["source_line"]) for row in section.get("records", [])]
        if literal_rows:
            block = block.rstrip("\n") + "\n\n" + "\n".join(literal_rows) + "\n\n"
        text = text[:start] + block + text[end:]
    return text.encode("utf-8")


def prove_materialized_preimage_derivation_v1(
        frozen_templates: Mapping[str, bytes],
        classification_sources: Mapping[str, Mapping[str, object]],
        materialized: MaterializedMigrationInputs) -> None:
    if (type(frozen_templates) is not dict
            or set(frozen_templates) != {"STATE.md", "ROADMAP.md"}
            or type(classification_sources) is not dict
            or set(classification_sources) != set(frozen_templates)
            or type(materialized) is not MaterializedMigrationInputs):
        raise RotationError("materialized preimage derivation population is invalid")
    for name in ("STATE.md", "ROADMAP.md"):
        source = classification_sources[name]
        if type(source) is not dict or set(source) != {"sections"}:
            raise RotationError("materialized preimage derivation source is invalid")
        observed = _materialize_migration_source_v1(
            frozen_templates[name], source["sections"])
        if observed != materialized.sources[name]:
            raise RotationError("materialized preimage derivation bytes disagree")


class ClassifiedRecord(NamedTuple):
    source_name: str
    heading: str
    record_kind: str
    ordinal: int
    byte_start: int
    byte_end: int
    source_bytes: bytes
    classification: str
    derivation_pointer: DerivationPointer | None = None


class LegacyRecord(NamedTuple):
    source_name: str
    heading: str
    record_kind: str
    ordinal: int
    byte_start: int
    byte_end: int
    source_bytes: bytes
    source_digest: str
    stable_id: str

    @classmethod
    def from_source(cls, *, source_name: str, heading: str, record_kind: str,
                    ordinal: int, byte_start: int, byte_end: int,
                    source_bytes: bytes) -> "LegacyRecord":
        digest = hashlib.sha256(source_bytes).hexdigest()
        body = {
            "schema": "implementaudit.legacy-record-id.v1",
            "source_name": source_name,
            "heading": heading,
            "record_kind": record_kind,
            "ordinal": ordinal,
            "byte_start": byte_start,
            "byte_end": byte_end,
            "source_digest": digest,
        }
        stable_id = "ialegacy-v1-" + hashlib.sha256(canonical_json_v1(body)).hexdigest()
        return cls(source_name, heading, record_kind, ordinal, byte_start, byte_end,
                   source_bytes, digest, stable_id)


class MigrationReceipt(NamedTuple):
    source_count: int
    event_count: int
    population_digest: str


class RuntimeArtifact(NamedTuple):
    path: str
    status: str
    notes: str


class LedgerFinding(NamedTuple):
    number: str
    finding: str
    priority: str
    action: str
    status: str
    evidence: str
    depends_on: str
    follow_up: str


class ResidualRecord(NamedTuple):
    residual: str
    consequential: str
    disposition: str
    owner: str
    evidence: str


class DecisionRecord(NamedTuple):
    status: str
    reason: str
    target: str
    evidence: str


class ScopeCreepRecord(NamedTuple):
    number: str
    issue: str
    location: str
    recommendation: str
    status: str


class AndonRecord(NamedTuple):
    number: str
    occurrence: str
    phase: str
    abnormality_class: str
    abnormality: str
    countermeasure: str
    rerun_evidence: str
    outcome: str


class InstructionRecord(NamedTuple):
    instruction_id: str
    reference: str
    kind: str
    authority: str
    subject: str
    issued_epoch: str
    status: str
    status_evidence: str
    supersedes_by: str
    scope_end: str


class NativeCurrent(NamedTuple):
    controller_id: str
    run_id: str
    phase: str
    status: str
    audit_object_state: str
    next_action: str
    current_epoch: str
    route: str
    owner_source: str
    baseline_ref: str
    last_check: str
    audit_object_source: str
    latest_auditing_operation: str
    terminal_closure_condition: str
    handoff_state: str
    runtime_artifacts: tuple[RuntimeArtifact, ...]
    open_ledger: tuple[LedgerFinding, ...]
    occurrence_resolution: str
    open_residuals: tuple[ResidualRecord, ...]
    execution_identity: str
    agents_update_decision: DecisionRecord
    continuity_decision_record: DecisionRecord
    action_selected: tuple[str, ...]
    action_omitted: tuple[str, ...]
    action_depth_rationale: str
    implementaudit_base: str
    planning_evidence: tuple[str, ...]
    open_scope_creep: tuple[ScopeCreepRecord, ...]
    open_andons: tuple[AndonRecord, ...]
    active_instructions: tuple[InstructionRecord, ...]

    def _as_hot_fields(self) -> dict[str, object]:
        fields = {
            "controller_id": self.controller_id,
            "run_id": self.run_id,
            "phase": self.phase,
            "status": self.status,
            "audit_object_state": self.audit_object_state,
            "next_action": self.next_action,
            "current_epoch": self.current_epoch,
            "route": self.route,
            "owner_source": self.owner_source,
            "baseline_ref": self.baseline_ref,
            "last_check": self.last_check,
            "audit_object_source": self.audit_object_source,
            "latest_auditing_operation": self.latest_auditing_operation,
            "terminal_closure_condition": self.terminal_closure_condition,
            "handoff_state": self.handoff_state,
            "runtime_artifacts": self.runtime_artifacts,
            "open_ledger": self.open_ledger,
            "occurrence_resolution": self.occurrence_resolution,
            "open_residuals": self.open_residuals,
            "execution_identity": self.execution_identity,
            "agents_update_decision": self.agents_update_decision,
            "continuity_decision_record": self.continuity_decision_record,
            "action_selected": self.action_selected,
            "action_omitted": self.action_omitted,
            "action_depth_rationale": self.action_depth_rationale,
            "implementaudit_base": self.implementaudit_base,
            "planning_evidence": self.planning_evidence,
            "open_scope_creep": self.open_scope_creep,
            "open_andons": self.open_andons,
            "active_instructions": self.active_instructions,
        }
        _validate_native_current_fields_v1(fields)
        return fields

    def hot_state_fields(self) -> dict[str, object]:
        return self._as_hot_fields()

    def hot_roadmap_fields(self) -> dict[str, object]:
        return self._as_hot_fields()


class GraphProjection(NamedTuple):
    work_graph_path: str
    work_graph_digest: str
    active_nodes: tuple[str, ...]

class CustodyPointer(NamedTuple):
    current_generation_ref: str
    pointer_oid: str
    manifest_digest: str
    archive_ref: str
    archive_digest: str
    history_query: str

def _line_records_v1(source_bytes: bytes) -> list[tuple[int, int, str]]:
    try:
        source_bytes.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise RotationError("classification source is not UTF-8") from exc
    records: list[tuple[int, int, str]] = []
    cursor = 0
    for raw in source_bytes.splitlines(keepends=True):
        end = cursor + len(raw)
        content = raw.rstrip(b"\r\n").decode("utf-8", "strict")
        records.append((cursor, end, content))
        cursor = end
    if cursor < len(source_bytes):
        records.append((cursor, len(source_bytes),
                        source_bytes[cursor:].decode("utf-8", "strict")))
    return records


def _classified_v1(*, source_name: str, heading: str, record_kind: str,
                   ordinal: int, start: int, end: int, source_bytes: bytes,
                   classification: str,
                   derivation_pointer: object,
                   derivation_sources: Mapping[str, DerivationSource]) -> ClassifiedRecord:
    if end <= start:
        raise RotationError("classification contains an empty byte range")
    resolved = _verify_derivation_pointer_v1(
        classification, derivation_pointer, record_kind, derivation_sources)
    if resolved is not None:
        derived = _extract_markdown_section_v1(
            derivation_sources[resolved.source_id].source_bytes, resolved.selector)
        if derived != source_bytes[start:end]:
            raise RotationError("duplicate-derivable classified bytes disagree")
    return ClassifiedRecord(source_name, heading, record_kind, ordinal, start, end,
                            source_bytes[start:end], classification,
                            resolved)


def _classify_one_source_v1(source_name: str, source_bytes: bytes,
                            sections: Sequence[Mapping[str, object]],
                            derivation_sources: Mapping[str, DerivationSource]
                            ) -> list[ClassifiedRecord]:
    lines = _line_records_v1(source_bytes)
    observed_headings = [(start, text) for start, _, text in lines
                         if text.startswith("# ") or text.startswith("## ")]
    expected_headings = [str(section["heading"]) for section in sections]
    if [heading for _, heading in observed_headings] != expected_headings:
        raise RotationError("classification source headings are unknown, missing, or reordered")
    results: list[ClassifiedRecord] = []
    ordinal = 0
    for index, section in enumerate(sections):
        section_start = observed_headings[index][0]
        section_end = (len(source_bytes) if index + 1 == len(sections)
                       else observed_headings[index + 1][0])
        heading = str(section["heading"])
        line_subset = [row for row in lines
                       if section_start <= row[0] < section_end]
        explicit: list[tuple[int, int, Mapping[str, object]]] = []
        for record in section.get("records", []):
            matches = [(start, end) for start, end, text in line_subset
                       if text == record["source_line"]]
            if len(matches) != 1:
                raise RotationError("explicit classification record is unmatched")
            explicit.append((matches[0][0], matches[0][1], record))
        for table in section.get("tables", []):
            headers = [line_index for line_index, (_, _, text) in enumerate(line_subset)
                       if text == table["header"]]
            if len(headers) != 1:
                raise RotationError("classification table header is unmatched")
            header_index = headers[0]
            if (header_index + 1 >= len(line_subset)
                    or line_subset[header_index + 1][2] != table["delimiter"]):
                raise RotationError("classification table delimiter is unmatched")
            row_index = header_index + 2
            actual_rows: list[tuple[int, int, str]] = []
            while row_index < len(line_subset) and line_subset[row_index][2].startswith("|"):
                actual_rows.append(line_subset[row_index])
                row_index += 1
            expected_rows = [row["source_line"] for row in table["rows"]]
            if [row[2] for row in actual_rows] != expected_rows:
                raise RotationError("classification table row population is unmatched")
            explicit.extend((actual[0], actual[1], rule)
                            for actual, rule in zip(actual_rows, table["rows"], strict=True))
        explicit.sort(key=lambda row: (row[0], row[1]))
        if any(left[1] > right[0] for left, right in zip(explicit, explicit[1:])):
            raise RotationError("classification rules overlap")
        cursor = section_start
        for start, end, rule in explicit:
            if start < cursor:
                raise RotationError("classification rules overlap")
            if start > cursor:
                results.append(_classified_v1(
                    source_name=source_name, heading=heading,
                    record_kind=str(section["record_kind"]), ordinal=ordinal,
                    start=cursor, end=start, source_bytes=source_bytes,
                    classification=str(section["classification"]),
                    derivation_pointer=section.get("derivation_pointer"),
                    derivation_sources=derivation_sources))
                ordinal += 1
            results.append(_classified_v1(
                source_name=source_name, heading=heading,
                record_kind=str(rule["record_kind"]), ordinal=ordinal,
                start=start, end=end, source_bytes=source_bytes,
                classification=str(rule["classification"]),
                derivation_pointer=rule.get("derivation_pointer"),
                derivation_sources=derivation_sources))
            ordinal += 1
            cursor = end
        if cursor < section_end:
            results.append(_classified_v1(
                source_name=source_name, heading=heading,
                record_kind=str(section["record_kind"]), ordinal=ordinal,
                start=cursor, end=section_end, source_bytes=source_bytes,
                classification=str(section["classification"]),
                derivation_pointer=section.get("derivation_pointer"),
                derivation_sources=derivation_sources))
            ordinal += 1
    return results


def classify_all_source_records_v1(
        sources: Mapping[str, bytes],
        classification: ClassificationFixture) -> dict[str, list[ClassifiedRecord]]:
    if (type(classification) is not ClassificationFixture
            or type(sources) is not dict
            or set(sources) != {"STATE.md", "ROADMAP.md"}
            or any(type(value) is not bytes or not value for value in sources.values())):
        raise RotationError("classification source population is invalid")
    coverage = {
        source_name: _classify_one_source_v1(
            source_name, sources[source_name], classification.sources[source_name],
            classification.derivation_sources)
        for source_name in ("STATE.md", "ROADMAP.md")
    }
    verify_classification_coverage_v1(sources, coverage)
    return coverage


def verify_classification_coverage_v1(
        sources: Mapping[str, bytes],
        coverage: Mapping[str, Sequence[ClassifiedRecord]]) -> None:
    if set(sources) != {"STATE.md", "ROADMAP.md"} or set(coverage) != set(sources):
        raise RotationError("classification coverage population is incomplete")
    for source_name in ("STATE.md", "ROADMAP.md"):
        source = sources[source_name]
        rows = coverage[source_name]
        if not rows:
            raise RotationError("classification coverage is empty")
        cursor = 0
        for ordinal, row in enumerate(rows):
            if (type(row) is not ClassifiedRecord or row.source_name != source_name
                    or row.ordinal != ordinal or row.byte_start != cursor
                    or row.byte_end <= row.byte_start or row.byte_end > len(source)
                    or row.source_bytes != source[row.byte_start:row.byte_end]
                    or row.classification not in CLASSIFICATIONS_V1):
                raise RotationError("classification coverage has a gap, overlap, or mismatch")
            if ((row.classification == "DUPLICATE_DERIVABLE"
                 and type(row.derivation_pointer) is not DerivationPointer)
                    or (row.classification != "DUPLICATE_DERIVABLE"
                        and row.derivation_pointer is not None)):
                raise RotationError("classification derivation coverage is invalid")
            cursor = row.byte_end
        if cursor != len(source):
            raise RotationError("classification coverage does not reach end of source")


def enumerate_legacy_history_v1(state_bytes: bytes, roadmap_bytes: bytes,
                                classification: ClassificationFixture) -> list[LegacyRecord]:
    sources = {"STATE.md": state_bytes, "ROADMAP.md": roadmap_bytes}
    coverage = classify_all_source_records_v1(sources, classification)
    verify_classification_coverage_v1(sources, coverage)
    records: list[LegacyRecord] = []
    for source_name in ("STATE.md", "ROADMAP.md"):
        for classified in coverage[source_name]:
            if classified.classification in REMOVED_CLASSIFICATIONS_V1:
                records.append(LegacyRecord.from_source(
                    source_name=source_name, heading=classified.heading,
                    record_kind=classified.record_kind, ordinal=classified.ordinal,
                    byte_start=classified.byte_start, byte_end=classified.byte_end,
                    source_bytes=classified.source_bytes))
    return records


def hash_population_v1(rows: Sequence[tuple[str, str]]) -> str:
    normalized: list[list[str]] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        if (type(row) is not tuple or len(row) != 2
                or type(row[0]) is not str or not LEGACY_RECORD_ID.fullmatch(row[0])
                or type(row[1]) is not str or not HEX_SHA256.fullmatch(row[1])
                or row in seen):
            raise RotationError("legacy history population identity is invalid")
        seen.add(row)
        normalized.append([row[0], row[1]])
    if not normalized:
        raise RotationError("legacy history population is empty")
    normalized.sort()
    return hashlib.sha256(canonical_json_v1(normalized)).hexdigest()


def verify_migration_population_v1(
        records: list[LegacyRecord], segment_bytes: list[bytes],
        manifest: dict[str, object]) -> MigrationReceipt:
    """Prove exact source/event/manifest equality without Git effects."""
    if (type(records) is not list or type(segment_bytes) is not list
            or not records or not segment_bytes
            or any(type(row) is not LegacyRecord for row in records)
            or any(type(raw) is not bytes or not raw for raw in segment_bytes)):
        raise RotationError("legacy history population is not equivalent")
    source = {(row.stable_id, row.source_digest) for row in records}
    if len(source) != len(records):
        raise RotationError("legacy history population is not equivalent")
    source_records = {(row.stable_id, row.source_digest): row for row in records}
    verify_generation_manifest_v1(manifest)
    manifest_rows = {str(row["event_id"]): row for row in manifest["events"]}
    destination: set[tuple[str, str]] = set()
    observed_event_ids: set[str] = set()
    for raw in segment_bytes:
        try:
            event = json.loads(raw.decode("utf-8", "strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RotationError("legacy history population is not equivalent") from exc
        if type(event) is not dict or canonical_json_v1(event) != raw:
            raise RotationError("legacy history population is not equivalent")
        validate_event_output_v1(event)
        without_id = dict(event)
        event_id = str(without_id.pop("event_id"))
        expected_event_id = "iaevt-v1-" + hashlib.sha256(
            canonical_json_v1(without_id)).hexdigest()
        payload = event["payload"]
        if (event_id != expected_event_id or event_id in observed_event_ids
                or type(payload) is not dict
                or set(payload) != {"legacy_record_id", "legacy_source_digest"}
                or type(payload["legacy_record_id"]) is not str
                or not LEGACY_RECORD_ID.fullmatch(payload["legacy_record_id"])
                or type(payload["legacy_source_digest"]) is not str
                or not HEX_SHA256.fullmatch(payload["legacy_source_digest"])
                or event["payload_digest"]
                != hashlib.sha256(canonical_json_v1(payload)).hexdigest()):
            raise RotationError("legacy history population is not equivalent")
        row = manifest_rows.get(event_id)
        if (row is None or row["sequence"] != event["sequence"]
                or row["record_kind"] != event["record_kind"]
                or row["source_evidence_id"] != event["source_evidence_id"]
                or row["segment_digest"]
                != "sha256:" + hashlib.sha256(raw).hexdigest()):
            raise RotationError("legacy history population is not equivalent")
        observed_event_ids.add(event_id)
        pair = (str(payload["legacy_record_id"]),
                str(payload["legacy_source_digest"]))
        legacy = source_records.get(pair)
        if (legacy is None or event["record_kind"] != legacy.record_kind
                or event["subject_id"] != legacy.stable_id
                or event["transition"] != "MIGRATED"):
            raise RotationError("legacy history population is not equivalent")
        destination.add(pair)
    if (source != destination or len(source) != len(records)
            or len(destination) != len(segment_bytes)
            or observed_event_ids != set(manifest_rows)
            or len(segment_bytes) != len(manifest["events"])):
        raise RotationError("legacy history population is not equivalent")
    return MigrationReceipt(source_count=len(records), event_count=len(segment_bytes),
                            population_digest=hash_population_v1(sorted(source)))


def verify_migration_equivalence_v1(
        records: list[LegacyRecord], segment_bytes: list[bytes],
        manifest: dict[str, object], repo: Path) -> MigrationReceipt:
    """Prove pure population equality first, then exact immutable ref bytes."""
    receipt = verify_migration_population_v1(records, segment_bytes, manifest)
    if not isinstance(repo, Path):
        raise RotationError("legacy history population is not equivalent")
    verify_manifest_segments_core_v1(repo, manifest)
    for raw in segment_bytes:
        try:
            event = json.loads(raw.decode("utf-8", "strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RotationError("legacy history population is not equivalent") from exc
        stored = load_exact_segment_bytes_v1(
            repo, str(manifest["run_id"]), str(manifest["generation_id"]),
            str(event["sequence"]), str(event["event_id"]))
        if not hmac.compare_digest(raw, stored):
            raise RotationError("legacy history population is not equivalent")
    return receipt


def _hot_value_v1(value: object) -> str:
    return _hot_projection._hot_value_v1(value)


def _validate_native_current_fields_v1(fields: Mapping[str, object]) -> None:
    expected = set(NativeCurrent._fields)
    if set(fields) != expected:
        raise RotationError("native current fields are not exact")
    tuple_fields = {
        "runtime_artifacts", "open_ledger", "open_residuals", "action_selected",
        "action_omitted", "planning_evidence", "open_scope_creep",
        "open_andons", "active_instructions",
    }
    decision_fields = {"agents_update_decision", "continuity_decision_record"}
    for name in expected - tuple_fields - decision_fields:
        _hot_value_v1(fields[name])
    if (not CONTROLLER_ID.fullmatch(str(fields["controller_id"]))
            or not TOKEN_ID.fullmatch(str(fields["run_id"]))
            or fields["status"] not in {"open", "READY_TO_DISPATCH", "IN_PHASE",
                                        "PAUSED", "BLOCKED", "INTERRUPTED", "DONE"}
            or not GENERATION_ID.fullmatch(str(fields["current_epoch"]))):
        raise RotationError("native current identity is invalid")
    for name in ("action_selected", "action_omitted", "planning_evidence"):
        rows = fields[name]
        if type(rows) is not tuple or len(set(rows)) != len(rows):
            raise RotationError("native current rows are invalid")
        for row in rows:
            _hot_value_v1(row)
    typed_rows = {
        "runtime_artifacts": RuntimeArtifact,
        "open_ledger": LedgerFinding,
        "open_residuals": ResidualRecord,
        "open_scope_creep": ScopeCreepRecord,
        "open_andons": AndonRecord,
        "active_instructions": InstructionRecord,
    }
    for name, row_type in typed_rows.items():
        rows = fields[name]
        if (type(rows) is not tuple or any(type(row) is not row_type for row in rows)
                or len(set(rows)) != len(rows)):
            raise RotationError("native typed current rows are invalid")
        for row in rows:
            for value in row:
                _hot_value_v1(value)
    for name in decision_fields:
        decision = fields[name]
        if type(decision) is not DecisionRecord:
            raise RotationError("native decision record is invalid")
        for value in decision:
            _hot_value_v1(value)


def _validate_hot_dependencies_v1(graph: GraphProjection,
                                  custody: CustodyPointer) -> None:
    if (type(graph) is not GraphProjection
            or graph.work_graph_path != "WORK_GRAPH.json"
            or not HEX_SHA256.fullmatch(graph.work_graph_digest)
            or not graph.active_nodes
            or any(type(row) is not str or not row for row in graph.active_nodes)
            or len(set(graph.active_nodes)) != len(graph.active_nodes)):
        raise RotationError("hot WORK_GRAPH projection is invalid")
    if (type(custody) is not CustodyPointer
            or not custody.current_generation_ref.startswith(
                "refs/implementaudit/current-generations/")
            or not GIT_OID.fullmatch(custody.pointer_oid)
            or not HEX_SHA256.fullmatch(custody.manifest_digest)
            or not custody.archive_ref.startswith("refs/implementaudit/state-archives/")
            or not HEX_SHA256.fullmatch(custody.archive_digest)
            or not custody.history_query):
        raise RotationError("hot custody pointer is invalid")


_hot_projection = _hot_projection_module.HotProjectionRenderer(
    error_type=RotationError, validate_fields=_validate_native_current_fields_v1,
    validate_dependencies=_validate_hot_dependencies_v1)

def _render_lines_v1(lines: Sequence[str]) -> bytes:
    return _hot_projection._render_lines_v1(lines)


STATE_HOT_SECTIONS_V1 = _hot_projection_module.STATE_HOT_SECTIONS_V1
ROADMAP_HOT_SECTIONS_V1 = _hot_projection_module.ROADMAP_HOT_SECTIONS_V1


def _markdown_headings_v1(raw: bytes) -> tuple[str, ...]:
    return _hot_projection._markdown_headings_v1(raw)


def verify_hot_renderer_template_parity_v1(state_template: bytes, roadmap_template: bytes, state_rendered: bytes, roadmap_rendered: bytes) -> None:
    return _hot_projection.verify_hot_renderer_template_parity_v1(state_template, roadmap_template, state_rendered, roadmap_rendered)


def render_state_template_v1(fields: Mapping[str, object], graph: GraphProjection, custody: CustodyPointer) -> bytes:
    return _hot_projection.render_state_template_v1(fields, graph, custody)


def render_roadmap_template_v1(fields: Mapping[str, object], graph: GraphProjection, custody: CustodyPointer) -> bytes:
    return _hot_projection.render_roadmap_template_v1(fields, graph, custody)


def derive_hot_state_v1(native: NativeCurrent, graph: GraphProjection,
                        custody: CustodyPointer) -> bytes:
    if type(native) is not NativeCurrent:
        raise RotationError("native current state is invalid")
    return render_state_template_v1(native.hot_state_fields(), graph, custody)


def derive_hot_roadmap_v1(native: NativeCurrent, graph: GraphProjection,
                          custody: CustodyPointer) -> bytes:
    if type(native) is not NativeCurrent:
        raise RotationError("native current roadmap is invalid")
    return render_roadmap_template_v1(native.hot_roadmap_fields(), graph, custody)


class ExpectedOldCasLost(RotationError):
    """Bounded loser evidence; callers must re-derive custody before any retry."""

    def __init__(self, ref: str, candidate_oid: str, expected_old: str, observed_after_loss: str | None,
                 classification: str):
        self.ref = ref
        self.candidate_oid = candidate_oid
        self.expected_old = expected_old
        self.observed_after_loss = observed_after_loss
        self.classification = classification
        super().__init__(f"expected-old CAS lost: {ref} candidate={candidate_oid} expected={expected_old} observed={observed_after_loss or 'ABSENT'} classification={classification}")


class PublicationObservationV1(NamedTuple):
    semantic_role: str
    canonical_no_follow_path: str
    file_identity: tuple[int, int]
    size: int
    ctime_ns: int
    mtime_ns: int
    sha256: str
    expected_digest: str


class _NativeFileSnapshotV1(NamedTuple):
    canonical_path: str
    file_identity: tuple[int, int]
    size: int
    ctime_ns: int
    mtime_ns: int


WINDOWS_TRUSTED_GIT_PATHS_V1 = (
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Program Files\Git\bin\git.exe",
)
PLATFORM_NULL_SINK_V1 = "NUL" if os.name == "nt" else "/dev/null"
WINDOWS_FILE_ATTRIBUTE_DIRECTORY = 0x10
WINDOWS_FILE_ATTRIBUTE_REPARSE_POINT = 0x400
WINDOWS_GENERIC_READ = 0x80000000
WINDOWS_FILE_SHARE_ALL = 0x1 | 0x2 | 0x4
WINDOWS_OPEN_EXISTING = 3
WINDOWS_FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
WINDOWS_INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
WINDOWS_EPOCH_OFFSET_100NS = 116_444_736_000_000_000


class _WindowsFileTimeV1(ctypes.Structure):
    _fields_ = [("low", ctypes.c_uint32), ("high", ctypes.c_uint32)]


class _WindowsByHandleFileInformationV1(ctypes.Structure):
    _fields_ = [
        ("attributes", ctypes.c_uint32),
        ("creation_time", _WindowsFileTimeV1),
        ("last_access_time", _WindowsFileTimeV1),
        ("last_write_time", _WindowsFileTimeV1),
        ("volume_serial", ctypes.c_uint32),
        ("size_high", ctypes.c_uint32),
        ("size_low", ctypes.c_uint32),
        ("link_count", ctypes.c_uint32),
        ("file_index_high", ctypes.c_uint32),
        ("file_index_low", ctypes.c_uint32),
    ]


INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1
SHA_ID = re.compile(r"^sha256:[0-9a-f]{64}$")
TOKEN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
CONTROLLER_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,47}$")
GENERATION_ID = re.compile(r"^G[0-9A-F]{4}$")
SEQUENCE_ID = re.compile(r"^[0-9]{20}$")
EVENT_ID = re.compile(r"^iaevt-v1-[0-9a-f]{64}$")
SOURCE_EVIDENCE_ID = re.compile(
    r"^iasrc-v1-(r0039-archive|r0038-snapshot)-[A-Za-z0-9._-]{1,96}$"
)
URI_PREFIX = "implementaudit-evidence:v1/"
URI_UNRESERVED = frozenset(
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
)
EVENT_ENUMS_V1 = {
    "record_kind": frozenset({
        "finding.closed", "andon.closed", "residual.terminal", "epoch.closed",
        "instruction.satisfied", "phase.completed", "transition.closed",
        "recovery.record", "artifact.historical",
    }),
    "transition": frozenset({"MIGRATED", "APPENDED", "CORRECTED", "SUPERSEDED"}),
    "status": frozenset({"PRESERVED", "CLOSED", "SATISFIED", "EXPIRED", "SUPERSEDED"}),
}
EVENT_REQUEST_KEYS = frozenset({
    "schema_version", "run_id", "controller_id", "generation_id", "sequence",
    "record_kind", "subject_id", "source_epoch", "transition", "status",
    "supersedes_event_id", "payload",
})
EVENT_OUTPUT_KEYS = EVENT_REQUEST_KEYS | {
    "source_evidence_id", "source_locator", "source_digest",
    "payload_digest", "event_id",
}
CLAIM_ID = re.compile(r"^[0-9a-f]{32}$")
GIT_OID = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
MANIFEST_EVENT_KEYS = frozenset({
    "sequence", "event_id", "segment_digest", "record_kind", "source_evidence_id",
})
MANIFEST_BODY_KEYS = frozenset({
    "schema_version", "query_contract_version", "controller_id", "claim_id",
    "run_id", "generation_id", "source_epoch", "predecessor_manifest_digest",
    "predecessor_high_water", "events", "record_class_counts", "population_digest",
    "high_water",
})
MANIFEST_KEYS = MANIFEST_BODY_KEYS | {"manifest_digest"}
POINTER_BODY_KEYS = frozenset({
    "schema_version", "controller_id", "claim_id", "run_id", "generation_id",
    "predecessor_pointer_oid", "predecessor_pointer_digest", "generation_manifest_oid",
    "generation_manifest_digest", "cold_high_water", "hot_state_digest",
    "hot_roadmap_digest", "work_graph_path", "work_graph_digest",
    "query_contract_version", "source_epoch", "degraded_state",
})
POINTER_KEYS = POINTER_BODY_KEYS | {"pointer_digest"}
EXPECTED_WORK_GRAPH_PATH = "WORK_GRAPH.json"
EVENT_SEGMENT_PREFIX = "refs/implementaudit/state-event-segments"
OWNER_MANIFEST_KEYS = frozenset({"entries"})
OWNER_ENTRY_KEYS = frozenset({
    "source_evidence_id", "sha256", "kind", "root_identity", "host_identity",
    "input_path_flavor", "source_locator",
})
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
SNAPSHOT_ID = re.compile(r"^iasnap-v1-[0-9a-f]{64}$")
SNAPSHOT_EVIDENCE_ID = re.compile(
    r"^iasrc-v1-r0038-snapshot-([0-9a-f]{64})"
    r"(?:-([A-Za-z0-9][A-Za-z0-9._-]{0,30}))?$"
)
SNAPSHOT_CURRENT_KEYS = frozenset({
    "schema_version", "snapshot_id", "manifest_sha256", "source_pointer_oid",
})
SNAPSHOT_MANIFEST_KEYS = frozenset({
    "schema_version", "controller_id", "claim_id", "run_id", "source_epoch",
    "source_pointer_oid", "source_evidence_entries",
})


def validate_identity_json_v1(value: object, path: str = "$") -> None:
    """Reject values that cannot have a portable immutable JSON identity."""
    if value is None or type(value) in (bool, str):
        return
    if type(value) is int:
        if not INT64_MIN <= value <= INT64_MAX:
            raise RotationError("OE_EVENT_PAYLOAD_INVALID")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            validate_identity_json_v1(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise RotationError("OE_EVENT_PAYLOAD_INVALID")
            validate_identity_json_v1(item, f"{path}.{key}")
        return
    raise RotationError("OE_EVENT_PAYLOAD_INVALID")


def canonical_json_v1(value: object) -> bytes:
    """Canonical identity bytes: compact UTF-8 JSON with no terminal LF."""
    validate_identity_json_v1(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def strict_percent_decode_ascii_v1(token: str) -> bytes:
    if not token.isascii():
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    data = bytearray()
    index = 0
    while index < len(token):
        if token[index] == "%":
            if (index + 2 >= len(token)
                    or not re.fullmatch(r"[0-9A-Fa-f]{2}", token[index + 1:index + 3])):
                raise RotationError("OE_SOURCE_LOCATOR_INVALID")
            data.append(int(token[index + 1:index + 3], 16))
            index += 3
        else:
            byte = ord(token[index])
            if byte not in URI_UNRESERVED:
                raise RotationError("OE_SOURCE_LOCATOR_INVALID")
            data.append(byte)
            index += 1
    return bytes(data)


def _encode_component_v1(component: str, *, evidence_uri: bool) -> str:
    normalized = unicodedata.normalize("NFC", component)
    forbidden = {"\0", "/"} | ({"\\"} if evidence_uri else set())
    if normalized in {"", ".", ".."} or any(char in normalized for char in forbidden):
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    try:
        encoded = normalized.encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise RotationError("OE_SOURCE_LOCATOR_INVALID") from exc
    return "".join(
        chr(byte) if byte in URI_UNRESERVED else f"%{byte:02X}"
        for byte in encoded
    )


def canonicalize_evidence_uri_v1(raw: str) -> str:
    if not raw.isascii() or not raw.startswith(URI_PREFIX):
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    tokens = raw[len(URI_PREFIX):].split("/")
    if not tokens or any(not token for token in tokens):
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    try:
        return URI_PREFIX + "/".join(
            _encode_component_v1(
                strict_percent_decode_ascii_v1(token).decode("utf-8", "strict"),
                evidence_uri=True,
            ) for token in tokens
        )
    except UnicodeDecodeError as exc:
        raise RotationError("OE_SOURCE_LOCATOR_INVALID") from exc


def encode_path_component_v1(component: str) -> str:
    return _encode_component_v1(component, evidence_uri=False)


def decode_canonical_path_component_v1(token: str) -> str:
    try:
        component = strict_percent_decode_ascii_v1(token).decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise RotationError("OE_SOURCE_LOCATOR_INVALID") from exc
    if "\0" in component or "/" in component:
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    return component


def canonicalize_portable_path_v1(raw: str, flavor: str) -> str:
    if flavor not in {"windows", "posix", "canonical"} or not raw:
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    if flavor == "windows":
        if (raw.endswith(("/", "\\")) or ("/" in raw and "\\" in raw)
                or raw.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", raw)):
            raise RotationError("OE_SOURCE_LOCATOR_INVALID")
        parts = re.split(r"[\\\\/]", raw)
    elif flavor == "posix":
        if raw.endswith("/") or raw.startswith("/"):
            raise RotationError("OE_SOURCE_LOCATOR_INVALID")
        parts = raw.split("/")
    else:
        if raw.endswith("/") or not raw.isascii() or raw.startswith("/") or "\\" in raw:
            raise RotationError("OE_SOURCE_LOCATOR_INVALID")
        parts = [decode_canonical_path_component_v1(token) for token in raw.split("/")]
    if any(part in {"", ".", ".."} or "\0" in part for part in parts):
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    return "/".join(encode_path_component_v1(part) for part in parts)


def normalize_source_locator_v1(locator: dict[str, object], *,
                                owner_entry: dict[str, object]) -> dict[str, object]:
    if type(locator) is not dict or set(locator) != {
            "kind", "root_identity", "path", "host_identity"}:
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    kind = locator["kind"]
    root_identity = locator["root_identity"]
    raw_path = locator["path"]
    host_identity = locator["host_identity"]
    if (type(kind) is not str
            or kind not in {"repo-relative", "run-root-relative", "evidence-uri", "host-bound"}
            or type(root_identity) is not str or not SHA_ID.fullmatch(root_identity)
            or type(raw_path) is not str or not raw_path):
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    if any(name not in owner_entry for name in ("kind", "root_identity", "host_identity", "input_path_flavor")):
        raise RotationError("OE_SOURCE_EVIDENCE_CONTEXT_MISMATCH")
    if (kind != owner_entry["kind"] or root_identity != owner_entry["root_identity"]
            or host_identity != owner_entry["host_identity"]):
        raise RotationError("OE_SOURCE_EVIDENCE_CONTEXT_MISMATCH")
    flavor = owner_entry["input_path_flavor"]
    if kind == "evidence-uri":
        if host_identity is not None or flavor is not None:
            raise RotationError("OE_SOURCE_LOCATOR_INVALID")
        return {"kind": kind, "root_identity": root_identity,
                "path": canonicalize_evidence_uri_v1(raw_path), "host_identity": None}
    if type(flavor) is not str:
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    if kind == "host-bound":
        if type(host_identity) is not str or not SHA_ID.fullmatch(host_identity):
            raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    elif host_identity is not None:
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    return {"kind": kind, "root_identity": root_identity,
            "path": canonicalize_portable_path_v1(raw_path, flavor),
            "host_identity": host_identity}


def validate_canonical_source_locator_v1(locator: dict[str, object]) -> None:
    if type(locator) is not dict:
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")
    normalized = normalize_source_locator_v1(
        locator, owner_entry={
            "kind": locator.get("kind"), "root_identity": locator.get("root_identity"),
            "host_identity": locator.get("host_identity"), "input_path_flavor": (
                None if locator.get("kind") == "evidence-uri" else "canonical"),
        })
    if normalized != locator:
        raise RotationError("OE_SOURCE_LOCATOR_INVALID")


def validate_event_request_v1(event: dict[str, object]) -> None:
    if type(event) is not dict or set(event) != EVENT_REQUEST_KEYS:
        raise RotationError("OE_EVENT_REQUEST_KEYS_NOT_EXACT")
    if event["schema_version"] != "implementaudit.history-event.v1":
        raise RotationError("OE_EVENT_SCHEMA_INVALID")
    if type(event["run_id"]) is not str or not TOKEN_ID.fullmatch(event["run_id"]):
        raise RotationError("OE_EVENT_RUN_ID_INVALID")
    if type(event["controller_id"]) is not str or not CONTROLLER_ID.fullmatch(event["controller_id"]):
        raise RotationError("OE_EVENT_CONTROLLER_ID_INVALID")
    if type(event["generation_id"]) is not str or not GENERATION_ID.fullmatch(event["generation_id"]):
        raise RotationError("OE_EVENT_GENERATION_ID_INVALID")
    if type(event["sequence"]) is not str or not SEQUENCE_ID.fullmatch(event["sequence"]):
        raise RotationError("OE_EVENT_SEQUENCE_INVALID")
    for name in ("record_kind", "transition", "status"):
        if type(event[name]) is not str or event[name] not in EVENT_ENUMS_V1[name]:
            raise RotationError(f"OE_EVENT_{name.upper()}_INVALID")
    if type(event["subject_id"]) is not str or not TOKEN_ID.fullmatch(event["subject_id"]):
        raise RotationError("OE_EVENT_SUBJECT_ID_INVALID")
    if type(event["source_epoch"]) is not str or not GENERATION_ID.fullmatch(event["source_epoch"]):
        raise RotationError("OE_EVENT_SOURCE_EPOCH_INVALID")
    supersedes = event["supersedes_event_id"]
    if supersedes is not None and (type(supersedes) is not str or not EVENT_ID.fullmatch(supersedes)):
        raise RotationError("OE_EVENT_SUPERSEDES_ID_INVALID")
    validate_identity_json_v1(event["payload"])


def require_exact_owner_manifest_entry_v1(manifest: dict[str, object],
                                          source_evidence_id: str) -> dict[str, object]:
    if (type(source_evidence_id) is not str
            or not SOURCE_EVIDENCE_ID.fullmatch(source_evidence_id)):
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    if type(manifest) is not dict or set(manifest) != OWNER_MANIFEST_KEYS:
        raise RotationError("OE_SOURCE_EVIDENCE_CONTEXT_MISMATCH")
    entries = manifest["entries"]
    if type(entries) is not list:
        raise RotationError("OE_SOURCE_EVIDENCE_CONTEXT_MISMATCH")
    matched = []
    for entry in entries:
        validate_owner_manifest_entry_v1(entry)
        if entry["source_evidence_id"] == source_evidence_id:
            matched.append(entry)
    if len(matched) != 1:
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    return matched[0]


def validate_owner_manifest_entry_v1(entry: object) -> None:
    """Validate every owner entry before selecting the requested identity."""
    if type(entry) is not dict or set(entry) != OWNER_ENTRY_KEYS:
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    if (type(entry["source_evidence_id"]) is not str
            or not SOURCE_EVIDENCE_ID.fullmatch(entry["source_evidence_id"])):
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    if type(entry["sha256"]) is not str or not HEX_SHA256.fullmatch(entry["sha256"]):
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    if type(entry["source_locator"]) is not dict:
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    try:
        normalize_source_locator_v1(entry["source_locator"], owner_entry=entry)
    except RotationError as exc:
        if str(exc) == "OE_SOURCE_EVIDENCE_CONTEXT_MISMATCH":
            raise
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED") from exc


def resolve_owner_source_evidence_in_context_v1(
        context: dict[str, object], source_evidence_id: str) -> tuple[dict[str, object], str]:
    if type(context) is not dict or set(context) != {"owner_manifest"}:
        raise RotationError("OE_SOURCE_EVIDENCE_CONTEXT_MISMATCH")
    entry = require_exact_owner_manifest_entry_v1(context["owner_manifest"], source_evidence_id)
    if type(entry["sha256"]) is not str or not HEX_SHA256.fullmatch(entry["sha256"]):
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    locator = entry["source_locator"]
    if type(locator) is not dict:
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    return normalize_source_locator_v1(locator, owner_entry=entry), "sha256:" + entry["sha256"]


def load_governed_source_context_v1(source_evidence_id: str) -> dict[str, object]:
    """No caller-selected source branch, path, ref, or manifest is accepted."""
    if type(source_evidence_id) is not str or not SOURCE_EVIDENCE_ID.fullmatch(source_evidence_id):
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    custody = load_governed_source_custody_v1()
    pointer_oid = custody["pointer_oid"]
    marker_oid = custody["marker_oid"]
    if pointer_oid is None and marker_oid is None:
        if not source_evidence_id.startswith("iasrc-v1-r0039-archive-"):
            raise RotationError("OE_SOURCE_EVIDENCE_WRONG_BRANCH")
        owner_manifest = load_exact_r0039_f2_archive_manifest_v1(
            repo=Path(custody["repo_path"]),
            run_root=Path(custody["run_root_path"]),
            controller_id=str(custody["controller_id"]),
            claim_id=str(custody["claim_id"]),
            run_id=str(custody["run_id"]),
            source_epoch=str(custody["source_epoch"]),
        )
    else:
        if pointer_oid is None or marker_oid is None:
            raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
        pointer = load_canonical_generation_pointer_oid_v1(
            Path(custody["repo_path"]), str(pointer_oid))
        require_complete_pointer_receipt_marker_route_v1(
            live=custody, receipt=custody["receipt"], pointer=pointer,
            pointer_oid=str(pointer_oid), marker_oid=str(marker_oid))
        if not source_evidence_id.startswith("iasrc-v1-r0038-snapshot-"):
            raise RotationError("OE_SOURCE_EVIDENCE_WRONG_BRANCH")
        owner_manifest = load_exact_r0038_current_snapshot_manifest_v1(
            run_root=Path(custody["run_root_path"]), pointer_oid=str(pointer_oid),
            controller_id=str(custody["controller_id"]),
            claim_id=str(custody["claim_id"]), run_id=str(custody["run_id"]),
            source_epoch=str(custody["source_epoch"]),
        )
    return {**custody, "owner_manifest": owner_manifest}


def resolve_owner_source_evidence_v1(source_evidence_id: str) -> tuple[dict[str, object], str]:
    return resolve_owner_source_evidence_in_context_v1(
        load_governed_source_context_v1(source_evidence_id), source_evidence_id)


def validate_event_output_v1(event: dict[str, object]) -> None:
    if type(event) is not dict or set(event) != EVENT_OUTPUT_KEYS:
        raise RotationError("OE_EVENT_OUTPUT_KEYS_NOT_EXACT")
    request = {name: event[name] for name in EVENT_REQUEST_KEYS}
    validate_event_request_v1(request)
    if (type(event["source_evidence_id"]) is not str
            or not SOURCE_EVIDENCE_ID.fullmatch(event["source_evidence_id"])):
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    validate_canonical_source_locator_v1(event["source_locator"])
    if type(event["source_digest"]) is not str or not SHA_ID.fullmatch(event["source_digest"]):
        raise RotationError("OE_EVENT_DIGEST_INVALID")
    if (type(event["payload_digest"]) is not str
            or not HEX_SHA256.fullmatch(event["payload_digest"])):
        raise RotationError("OE_EVENT_DIGEST_INVALID")
    if type(event["event_id"]) is not str or not EVENT_ID.fullmatch(event["event_id"]):
        raise RotationError("OE_EVENT_ID_INVALID")


def _build_event_segment_in_context_v1(
        event: dict[str, object], *, source_evidence_id: str,
        context: Mapping[str, object]) -> tuple[dict[str, object], bytes]:
    validate_event_request_v1(event)
    if not isinstance(context, Mapping):
        raise RotationError("OE_SOURCE_EVIDENCE_CONTEXT_MISMATCH")
    expected = tuple(context.get(name) for name in (
        "run_id", "controller_id", "generation_id", "source_epoch"))
    if (event["run_id"], event["controller_id"], event["generation_id"],
            event["source_epoch"]) != expected:
        raise RotationError("OE_SOURCE_EVIDENCE_CONTEXT_MISMATCH")
    source_locator, source_digest = resolve_owner_source_evidence_in_context_v1(
        {"owner_manifest": context.get("owner_manifest")}, source_evidence_id)
    envelope = dict(event)
    envelope.update({
        "source_evidence_id": source_evidence_id,
        "source_locator": source_locator,
        "source_digest": source_digest,
        "payload_digest": hashlib.sha256(canonical_json_v1(event["payload"])).hexdigest(),
    })
    envelope["event_id"] = "iaevt-v1-" + hashlib.sha256(
        canonical_json_v1(envelope)).hexdigest()
    validate_event_output_v1(envelope)
    return envelope, canonical_json_v1(envelope)


def build_event_segment_v1(event: dict[str, object], *,
                           source_evidence_id: str) -> tuple[dict[str, object], bytes]:
    return _build_event_segment_in_context_v1(
        event, source_evidence_id=source_evidence_id,
        context=load_governed_source_context_v1(source_evidence_id))


def allocate_candidate_sequences_v1(old_high_water: str, count: int) -> list[str]:
    if (type(old_high_water) is not str or not SEQUENCE_ID.fullmatch(old_high_water)
            or type(count) is not int or count < 1):
        raise RotationError("invalid high-water or allocation count")
    start = int(old_high_water) + 1
    stop = start + count
    if stop - 1 > 99_999_999_999_999_999_999:
        raise RotationError("sequence space exhausted")
    return [f"{value:020d}" for value in range(start, stop)]


def manifest_population_rows_v1(events: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{key: row[key] for key in MANIFEST_EVENT_KEYS} for row in events]


def build_generation_manifest_v1(predecessor_manifest: dict[str, object] | None,
                                 events: list[dict[str, object]]) -> tuple[dict[str, object], bytes]:
    """Build the sole canonical manifest product from stored event envelopes."""
    return _build_generation_manifest_in_context_v1(
        predecessor_manifest, events, context=load_governed_publication_context_v1())


def _build_generation_manifest_in_context_v1(predecessor_manifest, events, *, context):
    if type(events) is not list or (not events and predecessor_manifest is None):
        raise RotationError("manifest requires immutable event population")
    before = "00000000000000000000"
    predecessor_digest = None
    if predecessor_manifest is not None:
        predecessor_digest = verify_generation_manifest_v1(predecessor_manifest)
        before = str(predecessor_manifest["high_water"])
    ordered = sorted(events, key=lambda row: (str(row.get("sequence")), str(row.get("event_id"))))
    for event in ordered:
        validate_event_output_v1(event)
    expected_authority = (context["controller_id"], context["run_id"],
                          context["generation_id"], context["source_epoch"])
    if any((event["controller_id"], event["run_id"], event["generation_id"], event["source_epoch"])
           != expected_authority for event in ordered):
        raise RotationError("candidate events disagree with governed publication context")
    sequences = [str(event["sequence"]) for event in ordered]
    if sequences and sequences != allocate_candidate_sequences_v1(before, len(ordered)):
        raise RotationError("manifest sequence is not the exact contiguous predecessor successor")
    rows = [{"sequence": event["sequence"], "event_id": event["event_id"],
             "segment_digest": "sha256:" + hashlib.sha256(canonical_json_v1(event)).hexdigest(),
             "record_kind": event["record_kind"], "source_evidence_id": event["source_evidence_id"]}
            for event in ordered]
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["record_kind"])] = counts.get(str(row["record_kind"]), 0) + 1
    body: dict[str, object] = {
        "schema_version": "implementaudit.state-generation-manifest.v1",
        "query_contract_version": "implementaudit.history-query.v1",
        "controller_id": context["controller_id"], "claim_id": context["claim_id"],
        "run_id": context["run_id"], "generation_id": context["generation_id"],
        "source_epoch": context["source_epoch"], "predecessor_manifest_digest": predecessor_digest,
        "predecessor_high_water": before, "events": rows,
        "record_class_counts": dict(sorted(counts.items())),
        "population_digest": hashlib.sha256(canonical_json_v1(manifest_population_rows_v1(rows))).hexdigest(),
        "high_water": (rows[-1]["sequence"] if rows else before),
    }
    body["manifest_digest"] = hashlib.sha256(canonical_json_v1(body)).hexdigest()
    verify_generation_manifest_v1(body)
    return body, canonical_json_v1(body)


def verify_generation_manifest_v1(manifest: dict[str, object]) -> str:
    if type(manifest) is not dict or set(manifest) != MANIFEST_KEYS:
        raise RotationError("manifest keys are not exact")
    if (manifest["schema_version"] != "implementaudit.state-generation-manifest.v1"
            or manifest["query_contract_version"] != "implementaudit.history-query.v1"):
        raise RotationError("manifest schema/query contract is invalid")
    for name, pattern in (("controller_id", CONTROLLER_ID), ("claim_id", CLAIM_ID),
                          ("run_id", TOKEN_ID), ("generation_id", GENERATION_ID),
                          ("source_epoch", GENERATION_ID)):
        if type(manifest[name]) is not str or not pattern.fullmatch(manifest[name]):
            raise RotationError("manifest authority identity is invalid")
    body = dict(manifest); supplied = body.pop("manifest_digest")
    observed = hashlib.sha256(canonical_json_v1(body)).hexdigest()
    if type(supplied) is not str or not HEX_SHA256.fullmatch(supplied) or not hmac.compare_digest(supplied, observed):
        raise RotationError("manifest digest mismatch")
    predecessor = manifest["predecessor_manifest_digest"]
    if predecessor is not None and (type(predecessor) is not str or not HEX_SHA256.fullmatch(predecessor)):
        raise RotationError("manifest predecessor digest is invalid")
    before, high = manifest["predecessor_high_water"], manifest["high_water"]
    if type(before) is not str or type(high) is not str or not SEQUENCE_ID.fullmatch(before) or not SEQUENCE_ID.fullmatch(high):
        raise RotationError("manifest high-water is invalid")
    events = manifest["events"]
    if (type(events) is not list or (not events and predecessor is None)
            or (predecessor is None and before != "00000000000000000000")):
        raise RotationError("manifest predecessor/events are invalid")
    for row in events:
        if (type(row) is not dict or set(row) != MANIFEST_EVENT_KEYS
                or type(row["sequence"]) is not str or not SEQUENCE_ID.fullmatch(row["sequence"])
                or type(row["event_id"]) is not str or not EVENT_ID.fullmatch(row["event_id"])
                or type(row["segment_digest"]) is not str or not SHA_ID.fullmatch(row["segment_digest"])
                or type(row["record_kind"]) is not str or row["record_kind"] not in EVENT_ENUMS_V1["record_kind"]
                or type(row["source_evidence_id"]) is not str or not SOURCE_EVIDENCE_ID.fullmatch(row["source_evidence_id"])):
            raise RotationError("manifest event identity is invalid")
    if events != sorted(events, key=lambda row: (row["sequence"], row["event_id"])):
        raise RotationError("manifest events are not in canonical order")
    if len({row["sequence"] for row in events}) != len(events) or len({row["event_id"] for row in events}) != len(events):
        raise RotationError("manifest contains duplicate identity")
    if events:
        if ([row["sequence"] for row in events]
                != allocate_candidate_sequences_v1(before, len(events))
                or high != events[-1]["sequence"]):
            raise RotationError("manifest sequence is not contiguous")
    elif high != before:
        raise RotationError("empty successor manifest changed the predecessor high-water")
    counts: dict[str, int] = {}
    for row in events: counts[row["record_kind"]] = counts.get(row["record_kind"], 0) + 1
    if manifest["record_class_counts"] != dict(sorted(counts.items())):
        raise RotationError("manifest record-class counts disagree")
    if manifest["population_digest"] != hashlib.sha256(canonical_json_v1(manifest_population_rows_v1(events))).hexdigest():
        raise RotationError("manifest population digest disagrees")
    return observed


def verify_generation_pointer_v1(pointer: dict[str, object]) -> str:
    if type(pointer) is not dict or set(pointer) != POINTER_KEYS:
        raise RotationError("generation pointer keys are not exact")
    if pointer["schema_version"] != "implementaudit.state-generation-pointer.v1":
        raise RotationError("generation pointer schema is invalid")
    for name, pattern in (("controller_id", CONTROLLER_ID), ("claim_id", CLAIM_ID),
                          ("run_id", TOKEN_ID), ("generation_id", GENERATION_ID),
                          ("source_epoch", GENERATION_ID)):
        if type(pointer[name]) is not str or not pattern.fullmatch(pointer[name]):
            raise RotationError("generation pointer authority identity is invalid")
    previous_oid, previous_digest = pointer["predecessor_pointer_oid"], pointer["predecessor_pointer_digest"]
    if (previous_oid is None) != (previous_digest is None):
        raise RotationError("generation pointer predecessor identity is partial")
    if previous_oid is not None and (type(previous_oid) is not str or not GIT_OID.fullmatch(previous_oid)
                                     or type(previous_digest) is not str or not HEX_SHA256.fullmatch(previous_digest)):
        raise RotationError("generation pointer predecessor identity is invalid")
    if type(pointer["generation_manifest_oid"]) is not str or not GIT_OID.fullmatch(pointer["generation_manifest_oid"]):
        raise RotationError("generation pointer manifest OID is invalid")
    for name in ("generation_manifest_digest", "hot_state_digest", "hot_roadmap_digest", "work_graph_digest"):
        if type(pointer[name]) is not str or not HEX_SHA256.fullmatch(pointer[name]):
            raise RotationError("generation pointer digest identity is invalid")
    if (type(pointer["cold_high_water"]) is not str or not SEQUENCE_ID.fullmatch(pointer["cold_high_water"])
            or pointer["query_contract_version"] != "implementaudit.history-query.v1"
            or pointer["work_graph_path"] != EXPECTED_WORK_GRAPH_PATH
            or pointer["degraded_state"] not in {"NONE", "ACTIVEGRAPH_DOGFOOD_DEGRADED"}):
        raise RotationError("generation pointer state is invalid")
    body = dict(pointer); supplied = body.pop("pointer_digest")
    observed = hashlib.sha256(canonical_json_v1(body)).hexdigest()
    if type(supplied) is not str or not HEX_SHA256.fullmatch(supplied) or not hmac.compare_digest(supplied, observed):
        raise RotationError("generation pointer digest mismatch")
    return observed


def build_generation_pointer_v1(**values: object) -> tuple[dict[str, object], bytes]:
    allowed = POINTER_BODY_KEYS - {"schema_version", "query_contract_version"}
    if set(values) != allowed:
        raise RotationError("generation pointer build keys are not exact")
    body = {"schema_version": "implementaudit.state-generation-pointer.v1",
            "query_contract_version": "implementaudit.history-query.v1", **values}
    body["pointer_digest"] = hashlib.sha256(canonical_json_v1(body)).hexdigest()
    verify_generation_pointer_v1(body)
    return body, canonical_json_v1(body)


def verify_generation_successor_tuple_v1(*, pointer: dict[str, object], manifest: dict[str, object],
                                         predecessor_oid: str | None,
                                         predecessor_pointer: dict[str, object] | None,
                                         predecessor_manifest: dict[str, object] | None = None) -> None:
    """Bind a candidate pointer/manifest pair to exactly the observed predecessor."""
    if predecessor_oid is None:
        if (predecessor_pointer is not None or predecessor_manifest is not None or pointer["predecessor_pointer_oid"] is not None
                or pointer["predecessor_pointer_digest"] is not None
                or manifest["predecessor_manifest_digest"] is not None
                or manifest["predecessor_high_water"] != "00000000000000000000"):
            raise RotationError("genesis pointer predecessor disagrees")
        return
    if predecessor_pointer is None or predecessor_manifest is None:
        raise RotationError("successor predecessor is unavailable")
    previous_digest = verify_generation_pointer_v1(predecessor_pointer)
    predecessor_digest = verify_generation_manifest_v1(predecessor_manifest)
    predecessor_authority = tuple(predecessor_manifest[key] for key in (
        "controller_id", "claim_id", "run_id", "generation_id", "source_epoch"))
    pointer_authority = tuple(predecessor_pointer[key] for key in (
        "controller_id", "claim_id", "run_id", "generation_id", "source_epoch"))
    candidate_lineage = tuple(pointer[key] for key in ("controller_id", "claim_id", "run_id"))
    predecessor_lineage = tuple(predecessor_manifest[key] for key in ("controller_id", "claim_id", "run_id"))
    if (candidate_lineage != predecessor_lineage
            or pointer["predecessor_pointer_oid"] != predecessor_oid
            or pointer["predecessor_pointer_digest"] != previous_digest
            or predecessor_authority != pointer_authority
            or predecessor_pointer["generation_manifest_digest"] != predecessor_digest
            or predecessor_pointer["cold_high_water"] != predecessor_manifest["high_water"]
            or manifest["predecessor_manifest_digest"] != predecessor_digest
            or manifest["predecessor_high_water"] != predecessor_manifest["high_water"]):
        raise RotationError("successor pointer predecessor disagrees")


def verify_pointer_manifest_tuple_v1(*, pointer: dict[str, object], manifest: dict[str, object],
                                     manifest_oid: str) -> None:
    """Require every candidate pointer/manifest identity field to agree exactly."""
    verify_generation_pointer_v1(pointer)
    manifest_digest = verify_generation_manifest_v1(manifest)
    if (type(manifest_oid) is not str or not GIT_OID.fullmatch(manifest_oid)
            or pointer["generation_manifest_oid"] != manifest_oid
            or pointer["generation_manifest_digest"] != manifest_digest
            or tuple(pointer[key] for key in ("controller_id", "claim_id", "run_id", "generation_id", "source_epoch"))
            != tuple(manifest[key] for key in ("controller_id", "claim_id", "run_id", "generation_id", "source_epoch"))
            or pointer["cold_high_water"] != manifest["high_water"]):
        raise RotationError("pointer and manifest tuple disagrees")


def read_exact_git_blob_oid_v1(repo: Path, oid: str) -> bytes:
    if type(oid) is not str or not GIT_OID.fullmatch(oid):
        raise RotationError("Git object identity is invalid")
    if git(repo, "cat-file", "-t", oid).decode("utf-8").strip() != "blob":
        raise RotationError("Git object is not a blob")
    return git(repo, "cat-file", "blob", oid)


def load_canonical_generation_manifest_oid_v1(repo: Path, oid: str) -> dict[str, object]:
    raw = read_exact_git_blob_oid_v1(repo, oid)
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RotationError("generation manifest JSON is invalid") from exc
    if type(parsed) is not dict or canonical_json_v1(parsed) != raw:
        raise RotationError("generation manifest bytes are not canonical")
    verify_generation_manifest_v1(parsed)
    return parsed


def load_canonical_generation_pointer_oid_v1(repo: Path, oid: str) -> dict[str, object]:
    raw = read_exact_git_blob_oid_v1(repo, oid)
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RotationError("generation pointer JSON is invalid") from exc
    if type(parsed) is not dict or canonical_json_v1(parsed) != raw:
        raise RotationError("generation pointer bytes are not canonical")
    verify_generation_pointer_v1(parsed)
    return parsed


def load_exact_segment_bytes_v1(repo: Path, run_id: str, generation_id: str,
                                sequence: str, event_id: str) -> bytes:
    if (type(run_id) is not str or not TOKEN_ID.fullmatch(run_id)
            or type(generation_id) is not str or not GENERATION_ID.fullmatch(generation_id)
            or type(sequence) is not str or not SEQUENCE_ID.fullmatch(sequence)
            or type(event_id) is not str or not EVENT_ID.fullmatch(event_id)):
        raise RotationError("immutable event segment identity is invalid")
    ref = f"{EVENT_SEGMENT_PREFIX}/{run_id}/{generation_id}/{sequence}/{event_id}"
    oid = read_optional_exact_ref_oid_v1(repo, ref)
    if oid is None:
        raise RotationError("immutable event segment is unavailable")
    return read_exact_git_blob_oid_v1(repo, oid)


def verify_manifest_segments_core_v1(repo: Path, manifest: dict[str, object]) -> None:
    """Verify stored segment bytes only; live source-owner resolution is excluded."""
    verify_generation_manifest_v1(manifest)
    for row in manifest["events"]:
        raw = load_exact_segment_bytes_v1(repo, str(manifest["run_id"]),
                                          str(manifest["generation_id"]),
                                          str(row["sequence"]), str(row["event_id"]))
        try:
            segment = json.loads(raw.decode("utf-8", "strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RotationError("immutable event segment JSON is invalid") from exc
        if type(segment) is not dict or canonical_json_v1(segment) != raw:
            raise RotationError("immutable event segment bytes are not canonical")
        validate_event_output_v1(segment)
        without_id = dict(segment)
        supplied = without_id.pop("event_id")
        expected_id = "iaevt-v1-" + hashlib.sha256(canonical_json_v1(without_id)).hexdigest()
        if supplied != expected_id:
            raise RotationError("immutable event segment identity disagrees")
        if (segment["controller_id"] != manifest["controller_id"]
                or segment["run_id"] != manifest["run_id"]
                or segment["generation_id"] != manifest["generation_id"]
                or segment["source_epoch"] != manifest["source_epoch"]
                or segment["sequence"] != row["sequence"] or segment["event_id"] != row["event_id"]
                or segment["record_kind"] != row["record_kind"]
                or segment["source_evidence_id"] != row["source_evidence_id"]):
            raise RotationError("manifest row and segment semantics disagree")
        if "sha256:" + hashlib.sha256(raw).hexdigest() != row["segment_digest"]:
            raise RotationError("manifest segment digest disagrees")


def resolve_stored_owner_source_evidence_v1(
        *, manifest: dict[str, object], source_evidence_id: str
        ) -> tuple[dict[str, object], str]:
    """Re-resolve an immutable event through its original exact owner branch."""
    custody = load_governed_source_custody_v1()
    if tuple(manifest.get(name) for name in (
            "controller_id", "claim_id", "run_id")) != tuple(
            custody.get(name) for name in ("controller_id", "claim_id", "run_id")):
        raise RotationError("stored manifest authority disagrees with live custody")
    if source_evidence_id.startswith("iasrc-v1-r0039-archive-"):
        owner_manifest = load_exact_r0039_f2_archive_manifest_v1(
            repo=Path(custody["repo_path"]),
            run_root=Path(custody["run_root_path"]),
            controller_id=str(manifest["controller_id"]),
            claim_id=str(manifest["claim_id"]), run_id=str(manifest["run_id"]),
            source_epoch=str(manifest["source_epoch"]),
        )
    elif source_evidence_id.startswith("iasrc-v1-r0038-snapshot-"):
        owner_manifest = load_immutable_r0038_snapshot_for_evidence_id_v1(
            run_root=Path(custody["run_root_path"]),
            controller_id=str(manifest["controller_id"]),
            claim_id=str(manifest["claim_id"]), run_id=str(manifest["run_id"]),
            source_epoch=str(manifest["source_epoch"]),
            source_evidence_id=source_evidence_id,
        )
    else:
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    return resolve_owner_source_evidence_in_context_v1(
        {"owner_manifest": owner_manifest}, source_evidence_id)


def verify_manifest_segments_v1(repo: Path, manifest: dict[str, object]) -> None:
    """Verify immutable bytes and re-resolve each stored owner identity."""
    verify_manifest_segments_core_v1(repo, manifest)
    for row in manifest["events"]:
        raw = load_exact_segment_bytes_v1(
            repo, str(manifest["run_id"]), str(manifest["generation_id"]),
            str(row["sequence"]), str(row["event_id"]))
        segment = _decode_exact_canonical_json_v1(
            raw, "immutable event segment JSON is invalid")
        expected_locator, expected_digest = resolve_stored_owner_source_evidence_v1(
            manifest=manifest,
            source_evidence_id=str(segment["source_evidence_id"]))
        if (segment["source_locator"] != expected_locator
                or segment["source_digest"] != expected_digest):
            raise RotationError(
                "segment source evidence disagrees with exact owner manifest")


def read_exact_ref_state_v1(repo: Path, ref: str) -> tuple[str, str | None]:
    """Distinguish a physically absent ref from unreadable ref custody."""
    rc, output = git_optional(repo, "rev-parse", "--verify", ref)
    if rc == 0:
        try:
            oid = output.decode("ascii", "strict").removesuffix("\n")
        except UnicodeDecodeError:
            return "MALFORMED", None
        if output != (oid + "\n").encode("ascii") or not GIT_OID.fullmatch(oid):
            return "MALFORMED", None
        return "RESOLVED", oid

    loose_raw = git(repo, "rev-parse", "--path-format=absolute", "--git-path", ref)
    try:
        loose_path = Path(loose_raw.decode("utf-8", "strict").rstrip("\n"))
    except UnicodeDecodeError as exc:
        raise RotationError("governed ref custody is unreadable") from exc
    if loose_path.exists() or loose_path.is_symlink():
        return "BROKEN", None

    common_raw = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    try:
        packed_path = Path(common_raw.decode("utf-8", "strict").rstrip("\n")) / "packed-refs"
        if packed_path.is_symlink() or (packed_path.exists() and not packed_path.is_file()):
            raise RotationError("governed packed-ref custody is unreadable")
        packed_raw = packed_path.read_bytes() if packed_path.is_file() else b""
        packed_lines = packed_raw.decode("utf-8", "strict").splitlines()
    except RotationError:
        raise
    except (OSError, UnicodeDecodeError) as exc:
        raise RotationError("governed packed-ref custody is unreadable") from exc
    for line in packed_lines:
        if line.startswith(("#", "^")) or not line:
            continue
        fields = line.split()
        if len(fields) >= 2 and fields[-1] == ref:
            return "BROKEN", None
    return "ABSENT", None


def read_optional_exact_ref_oid_v1(repo: Path, ref: str) -> str | None:
    state, oid = read_exact_ref_state_v1(repo, ref)
    if state == "RESOLVED":
        return oid
    if state == "ABSENT":
        return None
    raise RotationError(f"governed ref exists but is {state.lower()}")


def _is_reparse_or_link_v1(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _read_bounded_regular_bytes_v1(path: Path, root: Path, error: str) -> bytes:
    """Read one exact regular file without accepting a link/reparse escape."""
    try:
        root_absolute = Path(os.path.abspath(root))
        path_absolute = Path(os.path.abspath(path))
        path_absolute.relative_to(root_absolute)
        cursor = root_absolute
        if _is_reparse_or_link_v1(cursor) or not cursor.is_dir():
            raise RotationError(error)
        for component in path_absolute.relative_to(root_absolute).parts:
            if component in {"", ".", ".."}:
                raise RotationError(error)
            cursor = cursor / component
            if _is_reparse_or_link_v1(cursor):
                raise RotationError(error)
        metadata = os.lstat(path_absolute)
        if (not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1
                or bool(getattr(metadata, "st_file_attributes", 0)
                        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))):
            raise RotationError(error)
        return path_absolute.read_bytes()
    except RotationError:
        raise
    except (OSError, ValueError) as exc:
        raise RotationError(error) from exc


def _decode_exact_canonical_json_v1(raw: bytes, error: str) -> dict[str, object]:
    try:
        value = json.loads(raw.decode("utf-8", "strict"))
        if type(value) is not dict or canonical_json_v1(value) != raw:
            raise RotationError(error)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise RotationError(error) from exc
    return value


def _validate_snapshot_owner_manifest_v1(
        manifest: dict[str, object], *, controller_id: str, claim_id: str,
        run_id: str, source_epoch: str, pointer_oid: str, snapshot_id: str
        ) -> dict[str, object]:
    if (set(manifest) != SNAPSHOT_MANIFEST_KEYS
            or manifest.get("schema_version") != "IA-OPERATIONAL-SNAPSHOT-v1"
            or manifest.get("controller_id") != controller_id
            or manifest.get("claim_id") != claim_id
            or manifest.get("run_id") != run_id
            or manifest.get("source_epoch") != source_epoch
            or manifest.get("source_pointer_oid") != pointer_oid):
        raise RotationError("OE_R0038_SNAPSHOT_MANIFEST_INVALID")
    entries = manifest.get("source_evidence_entries")
    if type(entries) is not list or not entries:
        raise RotationError("OE_R0038_SNAPSHOT_MANIFEST_INVALID")
    identities: set[str] = set()
    snapshot_digest = snapshot_id.removeprefix("iasnap-v1-")
    for entry in entries:
        try:
            validate_owner_manifest_entry_v1(entry)
        except RotationError as exc:
            raise RotationError("OE_R0038_SNAPSHOT_MANIFEST_INVALID") from exc
        identity = str(entry["source_evidence_id"])
        identity_match = SNAPSHOT_EVIDENCE_ID.fullmatch(identity)
        if (identity_match is None or identity_match.group(1) != snapshot_digest
                or identity in identities):
            raise RotationError("OE_R0038_SNAPSHOT_MANIFEST_INVALID")
        identities.add(identity)
    return {"entries": entries}


def load_exact_r0038_current_snapshot_manifest_v1(
        *, run_root: Path, pointer_oid: str, controller_id: str, claim_id: str,
        run_id: str, source_epoch: str) -> dict[str, object]:
    """Load only the canonical CURRENT-selected immutable R0038 snapshot."""
    if (not isinstance(run_root, Path) or not GIT_OID.fullmatch(pointer_oid)
            or not CONTROLLER_ID.fullmatch(controller_id)
            or not CLAIM_ID.fullmatch(claim_id) or not TOKEN_ID.fullmatch(run_id)
            or not GENERATION_ID.fullmatch(source_epoch)):
        raise RotationError("OE_R0038_SNAPSHOT_MANIFEST_INVALID")
    snapshots = run_root / "operational-evidence" / "snapshots"
    current_path = snapshots / "CURRENT"
    if not current_path.exists() and not current_path.is_symlink():
        raise RotationError("OE_R0038_SNAPSHOT_NOT_PUBLISHED")
    current_raw = _read_bounded_regular_bytes_v1(
        current_path, run_root, "OE_R0038_SNAPSHOT_CURRENT_INVALID")
    current = _decode_exact_canonical_json_v1(
        current_raw, "OE_R0038_SNAPSHOT_CURRENT_INVALID")
    if (set(current) != SNAPSHOT_CURRENT_KEYS
            or current.get("schema_version")
            != "implementaudit.operational-snapshot-current.v1"
            or type(current.get("snapshot_id")) is not str
            or not SNAPSHOT_ID.fullmatch(str(current["snapshot_id"]))
            or type(current.get("manifest_sha256")) is not str
            or not HEX_SHA256.fullmatch(str(current["manifest_sha256"]))
            or current.get("source_pointer_oid") != pointer_oid):
        raise RotationError("OE_R0038_SNAPSHOT_CURRENT_INVALID")
    snapshot_id = str(current["snapshot_id"])
    manifest_path = snapshots / snapshot_id / "manifest.json"
    manifest_raw = _read_bounded_regular_bytes_v1(
        manifest_path, run_root, "OE_R0038_SNAPSHOT_MANIFEST_INVALID")
    if not hmac.compare_digest(
            hashlib.sha256(manifest_raw).hexdigest(),
            str(current["manifest_sha256"])):
        raise RotationError("OE_R0038_SNAPSHOT_MANIFEST_INVALID")
    manifest = _decode_exact_canonical_json_v1(
        manifest_raw, "OE_R0038_SNAPSHOT_MANIFEST_INVALID")
    owner_manifest = _validate_snapshot_owner_manifest_v1(
        manifest, controller_id=controller_id, claim_id=claim_id,
        run_id=run_id, source_epoch=source_epoch, pointer_oid=pointer_oid,
        snapshot_id=snapshot_id)
    if _read_bounded_regular_bytes_v1(
            current_path, run_root,
            "OE_R0038_SNAPSHOT_CURRENT_INVALID") != current_raw:
        raise RotationError("OE_R0038_SNAPSHOT_CURRENT_CHANGED")
    return owner_manifest


def load_immutable_r0038_snapshot_for_evidence_id_v1(
        *, run_root: Path, controller_id: str, claim_id: str, run_id: str,
        source_epoch: str, source_evidence_id: str) -> dict[str, object]:
    """Reopen the immutable snapshot encoded by a stored evidence identity."""
    match = (SNAPSHOT_EVIDENCE_ID.fullmatch(source_evidence_id)
             if type(source_evidence_id) is str else None)
    if match is None:
        raise RotationError("OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    snapshot_id = "iasnap-v1-" + match.group(1)
    manifest_path = (run_root / "operational-evidence" / "snapshots"
                     / snapshot_id / "manifest.json")
    manifest_raw = _read_bounded_regular_bytes_v1(
        manifest_path, run_root, "OE_R0038_SNAPSHOT_MANIFEST_INVALID")
    manifest = _decode_exact_canonical_json_v1(
        manifest_raw, "OE_R0038_SNAPSHOT_MANIFEST_INVALID")
    pointer_oid = manifest.get("source_pointer_oid")
    if type(pointer_oid) is not str or not GIT_OID.fullmatch(pointer_oid):
        raise RotationError("OE_R0038_SNAPSHOT_MANIFEST_INVALID")
    owner_manifest = _validate_snapshot_owner_manifest_v1(
        manifest, controller_id=controller_id, claim_id=claim_id,
        run_id=run_id, source_epoch=source_epoch, pointer_oid=pointer_oid,
        snapshot_id=snapshot_id)
    require_exact_owner_manifest_entry_v1(owner_manifest, source_evidence_id)
    return owner_manifest


def load_exact_r0039_f2_archive_manifest_v1(
        *, repo: Path, run_root: Path, controller_id: str, claim_id: str,
        run_id: str, source_epoch: str) -> dict[str, object]:
    """Resolve the one exact F2 archive branch into the Task-3 owner shape."""
    if (not isinstance(repo, Path) or not isinstance(run_root, Path)
            or not CONTROLLER_ID.fullmatch(controller_id)
            or not CLAIM_ID.fullmatch(claim_id) or not TOKEN_ID.fullmatch(run_id)
            or not GENERATION_ID.fullmatch(source_epoch)):
        raise RotationError("OE_R0039_ARCHIVE_INVALID")
    try:
        repo = require_repo(str(repo))
        run_root = require_run_root(str(run_root), repo)
    except RotationError as exc:
        raise RotationError("OE_R0039_ARCHIVE_INVALID") from exc
    expected_run_root = repo / ".IMPLEMENTAUDIT" / "runs" / run_id
    if not same_path(run_root, expected_run_root):
        raise RotationError("OE_R0039_ARCHIVE_INVALID")
    prefix = f"{ARCHIVE_PREFIX}/{controller_id}/"
    refs = [line for line in git(
        repo, "for-each-ref", "--format=%(refname)", prefix
    ).decode("utf-8", "strict").splitlines() if line]
    if len(refs) != 1:
        raise RotationError("OE_R0039_ARCHIVE_INVALID")
    archive_ref = refs[0]
    generation = archive_ref.removeprefix(prefix)
    if not re.fullmatch(r"g[0-9a-f]{4}", generation):
        raise RotationError("OE_R0039_ARCHIVE_INVALID")
    verify_archive(repo, controller_id, generation)
    archive_oid = read_optional_exact_ref_oid_v1(repo, archive_ref)
    if archive_oid is None:
        raise RotationError("OE_R0039_ARCHIVE_INVALID")
    archive_raw = read_exact_git_blob_oid_v1(repo, archive_oid)
    try:
        archive = json.loads(archive_raw.decode("utf-8", "strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RotationError("OE_R0039_ARCHIVE_INVALID") from exc
    if type(archive) is not dict or canonical_bytes(archive) != archive_raw:
        raise RotationError("OE_R0039_ARCHIVE_INVALID")
    by_role = {str(entry["role"]): entry for entry in archive["entries"]}
    if set(by_role) != {"STATE", "ROADMAP", "WORK_GRAPH"}:
        raise RotationError("OE_R0039_ARCHIVE_INVALID")
    population_rows = [[
        name, int(by_role[name]["byte_length"]), str(by_role[name]["sha256"])
    ] for name in ("STATE", "ROADMAP")]
    population_digest = hashlib.sha256(canonical_json_v1(population_rows)).hexdigest()
    root_identity = "sha256:" + population_digest
    entry = {
        "source_evidence_id": "iasrc-v1-r0039-archive-task5-migration",
        "sha256": population_digest,
        "kind": "evidence-uri",
        "root_identity": root_identity,
        "host_identity": None,
        "input_path_flavor": None,
        "source_locator": {
            "kind": "evidence-uri", "root_identity": root_identity,
            "path": ("implementaudit-evidence:v1/r0039/f2/"
                     + encode_path_component_v1(generation)),
            "host_identity": None,
        },
    }
    validate_owner_manifest_entry_v1(entry)
    return {"entries": [entry]}


def migration_classification_ref_v1(controller_id: str, archive_oid: str) -> str:
    """Return the sole controller/archive-keyed immutable classification ref."""
    if (type(controller_id) is not str
            or not CONTROLLER_ID.fullmatch(controller_id)
            or type(archive_oid) is not str
            or not GIT_OID.fullmatch(archive_oid)):
        raise RotationError("migration classification identity is invalid")
    return f"{MIGRATION_CLASSIFICATION_PREFIX}/{controller_id}/{archive_oid}"


def _load_live_genesis_archive_sources_v1(
        repo: Path, *, controller_id: str,
        archive_oid: str) -> tuple[str, dict[str, object], dict[str, bytes]]:
    if (not isinstance(repo, Path) or type(controller_id) is not str
            or not CONTROLLER_ID.fullmatch(controller_id)
            or type(archive_oid) is not str or not GIT_OID.fullmatch(archive_oid)):
        raise RotationError("live-genesis archive custody is invalid")
    repo = require_repo(str(repo))
    prefix = f"{ARCHIVE_PREFIX}/{controller_id}/"
    refs = [line for line in git(
        repo, "for-each-ref", "--format=%(refname)", prefix
    ).decode("utf-8", "strict").splitlines() if line]
    if len(refs) != 1:
        raise RotationError("live-genesis archive custody is invalid")
    archive_ref = refs[0]
    generation = archive_ref.removeprefix(prefix)
    if not re.fullmatch(r"g[0-9]{4}", generation):
        raise RotationError("live-genesis archive custody is invalid")
    if read_optional_exact_ref_oid_v1(repo, archive_ref) != archive_oid:
        raise RotationError("live-genesis archive custody is invalid")
    verify_archive(repo, controller_id, generation)
    archive_raw = read_exact_git_blob_oid_v1(repo, archive_oid)
    try:
        archive = json.loads(archive_raw.decode("utf-8", "strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RotationError("live-genesis archive custody is invalid") from exc
    if type(archive) is not dict or canonical_bytes(archive) != archive_raw:
        raise RotationError("live-genesis archive custody is invalid")
    entries = archive.get("entries")
    if type(entries) is not list:
        raise RotationError("live-genesis archive custody is invalid")
    by_role = {entry.get("role"): entry for entry in entries
               if type(entry) is dict}
    if (len(by_role) != len(entries)
            or set(by_role) != {"STATE", "ROADMAP", "WORK_GRAPH"}
            or by_role["STATE"].get("source_path") != "STATE.md"
            or by_role["ROADMAP"].get("source_path") != "ROADMAP.md"
            or by_role["WORK_GRAPH"].get("source_path") != "WORK_GRAPH.json"):
        raise RotationError("live-genesis archive custody is invalid")
    sources = {
        "STATE.md": read_exact_git_blob_oid_v1(
            repo, str(by_role["STATE"].get("blob_oid"))),
        "ROADMAP.md": read_exact_git_blob_oid_v1(
            repo, str(by_role["ROADMAP"].get("blob_oid"))),
    }
    return archive_ref, archive, sources


def _decode_live_genesis_classification_v1(
        raw: bytes, sources: Mapping[str, bytes]
        ) -> ClassificationFixture:
    mapping = _decode_exact_canonical_json_v1(
        raw, "live-genesis classification bytes are invalid")
    try:
        fixture = ClassificationFixture.from_mapping(mapping, {})
        coverage = classify_all_source_records_v1(sources, fixture)
        verify_classification_coverage_v1(sources, coverage)
    except RotationError as exc:
        raise RotationError("live-genesis classification is invalid") from exc
    return fixture


def load_live_genesis_classification_oid_v1(
        repo: Path, *, controller_id: str, archive_oid: str
        ) -> tuple[str, str, ClassificationFixture, bytes]:
    """Load the exact admitted classification and reprove archive coverage."""
    if not isinstance(repo, Path):
        raise RotationError("live-genesis classification custody is invalid")
    repo = require_repo(str(repo))
    classification_ref = migration_classification_ref_v1(
        controller_id, archive_oid)
    _archive_ref, _archive, sources = _load_live_genesis_archive_sources_v1(
        repo, controller_id=controller_id, archive_oid=archive_oid)
    classification_oid = read_optional_exact_ref_oid_v1(repo, classification_ref)
    if classification_oid is None:
        raise RotationError("live-genesis classification is unavailable")
    raw = read_exact_git_blob_oid_v1(repo, classification_oid)
    fixture = _decode_live_genesis_classification_v1(raw, sources)
    if read_exact_git_blob_oid_v1(repo, classification_oid) != raw:
        raise RotationError("live-genesis classification readback changed")
    return classification_ref, classification_oid, fixture, raw


def _classification_admission_transaction_v1(
        *, repo: Path, classification_ref: str, classification_oid: str,
        guards: tuple[tuple[str, str], ...]) -> tuple[list[str], dict[str, str], bytes]:
    if (not isinstance(repo, Path)
            or not classification_ref.startswith(MIGRATION_CLASSIFICATION_PREFIX + "/")
            or not GIT_OID.fullmatch(classification_oid)
            or tuple(sorted(guards)) != guards):
        raise RotationError("classification admission transaction is invalid")
    rows = [b"start\0"]
    for ref, oid in guards:
        if (not ref.startswith("refs/implementaudit/")
                or not GIT_OID.fullmatch(oid)):
            raise RotationError("classification admission guard is invalid")
        rows.append(b"verify " + ref.encode("ascii") + b"\0"
                    + oid.encode("ascii") + b"\0")
    rows.append(b"update " + classification_ref.encode("ascii") + b"\0"
                + classification_oid.encode("ascii") + b"\0"
                + ZERO_OID.encode("ascii") + b"\0prepare\0commit\0")
    executable = git_executable_v1()
    environment = {
        "PATH": os.path.dirname(executable), "LC_ALL": "C", "LANG": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": PLATFORM_NULL_SINK_V1,
        "GIT_TERMINAL_PROMPT": "0",
    }
    return ([executable, "-c", f"core.hooksPath={PLATFORM_NULL_SINK_V1}",
             "update-ref", "--stdin", "-z"], environment, b"".join(rows))


def publish_live_genesis_classification_v1(
        *, candidate_classification_oid: str) -> str:
    """Admit one reviewed classification without accepting caller custody."""
    if (type(candidate_classification_oid) is not str
            or not GIT_OID.fullmatch(candidate_classification_oid)):
        raise RotationError("candidate classification identity is invalid")
    opened_custody = _publication_custody_tuple_v1()
    repo, controller_id, controller_oid, _claim_id, _run_root, _run_id = (
        _publication_custody_fields_v1())
    repo = require_repo(str(repo))
    controller_ref = f"refs/implementaudit/controllers/{controller_id}"
    current_ref = f"refs/implementaudit/current-generations/{controller_id}"
    marker_ref = f"refs/implementaudit/current-generation-migrations/{controller_id}"
    if read_optional_exact_ref_oid_v1(repo, controller_ref) != controller_oid:
        raise RotationError("classification admission custody is stale")
    for ref in (current_ref, marker_ref):
        state, _oid = read_exact_ref_state_v1(repo, ref)
        if state != "ABSENT":
            raise RotationError("classification admission requires genesis custody")
    prefix = f"{ARCHIVE_PREFIX}/{controller_id}/"
    archive_refs = [line for line in git(
        repo, "for-each-ref", "--format=%(refname)", prefix
    ).decode("utf-8", "strict").splitlines() if line]
    if len(archive_refs) != 1:
        raise RotationError("live-genesis archive custody is invalid")
    archive_ref = archive_refs[0]
    archive_oid = read_optional_exact_ref_oid_v1(repo, archive_ref)
    if archive_oid is None:
        raise RotationError("live-genesis archive custody is invalid")
    classification_ref = migration_classification_ref_v1(
        controller_id, archive_oid)
    _exact_archive_ref, _archive, sources = _load_live_genesis_archive_sources_v1(
        repo, controller_id=controller_id, archive_oid=archive_oid)
    candidate_raw = read_exact_git_blob_oid_v1(repo, candidate_classification_oid)
    _decode_live_genesis_classification_v1(candidate_raw, sources)
    existing = read_optional_exact_ref_oid_v1(repo, classification_ref)
    if existing is not None:
        if existing != candidate_classification_oid:
            raise RotationError("migration classification ref is immutable")
        loaded = load_live_genesis_classification_oid_v1(
            repo, controller_id=controller_id, archive_oid=archive_oid)
        if loaded[1] != candidate_classification_oid or loaded[3] != candidate_raw:
            raise RotationError("migration classification idempotent readback disagrees")
        if (read_optional_exact_ref_oid_v1(repo, controller_ref) != controller_oid
                or read_optional_exact_ref_oid_v1(repo, archive_ref) != archive_oid
                or read_optional_exact_ref_oid_v1(repo, current_ref) is not None
                or read_optional_exact_ref_oid_v1(repo, marker_ref) is not None):
            raise RotationError("classification admission custody is stale")
        return candidate_classification_oid
    if read_exact_git_blob_oid_v1(repo, candidate_classification_oid) != candidate_raw:
        raise RotationError("candidate classification bytes changed")
    guards = tuple(sorted((
        (archive_ref, archive_oid), (controller_ref, controller_oid),
        (current_ref, ZERO_OID), (marker_ref, ZERO_OID),
    )))
    argv, environment, stdin_bytes = _classification_admission_transaction_v1(
        repo=repo, classification_ref=classification_ref,
        classification_oid=candidate_classification_oid, guards=guards)
    _require_publication_custody_recheck_v1(opened_custody)
    completed = subprocess.run(
        argv, cwd=str(repo), env=environment, input=stdin_bytes,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0:
        observed = read_optional_exact_ref_oid_v1(repo, classification_ref)
        if observed != candidate_classification_oid:
            raise RotationError("classification admission CAS failed")
        if (read_optional_exact_ref_oid_v1(repo, controller_ref) != controller_oid
                or read_optional_exact_ref_oid_v1(repo, archive_ref) != archive_oid
                or read_optional_exact_ref_oid_v1(repo, current_ref) is not None
                or read_optional_exact_ref_oid_v1(repo, marker_ref) is not None):
            raise RotationError("classification admission custody is stale")
    loaded = load_live_genesis_classification_oid_v1(
        repo, controller_id=controller_id, archive_oid=archive_oid)
    if loaded[1] != candidate_classification_oid or loaded[3] != candidate_raw:
        raise RotationError("classification admission readback disagrees")
    return candidate_classification_oid


def _windows_apis_v1() -> object:
    if os.name != "nt" or not hasattr(ctypes, "WinDLL"):
        raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateFileW.argtypes = [
        ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
    ]
    kernel32.CreateFileW.restype = ctypes.c_void_p
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_int
    kernel32.GetFileInformationByHandle.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(_WindowsByHandleFileInformationV1),
    ]
    kernel32.GetFileInformationByHandle.restype = ctypes.c_int
    kernel32.GetFinalPathNameByHandleW.argtypes = [
        ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
    ]
    kernel32.GetFinalPathNameByHandleW.restype = ctypes.c_uint32
    kernel32.SetFilePointerEx.argtypes = [
        ctypes.c_void_p, ctypes.c_int64, ctypes.c_void_p, ctypes.c_uint32,
    ]
    kernel32.SetFilePointerEx.restype = ctypes.c_int
    kernel32.ReadFile.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p,
    ]
    kernel32.ReadFile.restype = ctypes.c_int
    return kernel32


def _windows_open_regular_no_reparse_v1(path: Path) -> int:
    kernel32 = _windows_apis_v1()
    handle = kernel32.CreateFileW(
        str(path), WINDOWS_GENERIC_READ, WINDOWS_FILE_SHARE_ALL, None,
        WINDOWS_OPEN_EXISTING, WINDOWS_FILE_FLAG_OPEN_REPARSE_POINT, None,
    )
    if handle in (None, WINDOWS_INVALID_HANDLE_VALUE):
        raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
    try:
        information = _WindowsByHandleFileInformationV1()
        if not kernel32.GetFileInformationByHandle(handle, ctypes.byref(information)):
            raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
        if information.attributes & (
                WINDOWS_FILE_ATTRIBUTE_DIRECTORY | WINDOWS_FILE_ATTRIBUTE_REPARSE_POINT):
            raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
    except BaseException:
        kernel32.CloseHandle(handle)
        raise
    return int(handle)


def _windows_close_handle_v1(handle: int) -> None:
    kernel32 = _windows_apis_v1()
    if not kernel32.CloseHandle(ctypes.c_void_p(handle)):
        raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")


def _windows_filetime_ns_v1(value: _WindowsFileTimeV1) -> int:
    ticks = (int(value.high) << 32) | int(value.low)
    return (ticks - WINDOWS_EPOCH_OFFSET_100NS) * 100


def _windows_snapshot_v1(handle: int) -> _NativeFileSnapshotV1:
    kernel32 = _windows_apis_v1()
    information = _WindowsByHandleFileInformationV1()
    if not kernel32.GetFileInformationByHandle(
            ctypes.c_void_p(handle), ctypes.byref(information)):
        raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
    if information.attributes & (
            WINDOWS_FILE_ATTRIBUTE_DIRECTORY | WINDOWS_FILE_ATTRIBUTE_REPARSE_POINT):
        raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
    buffer = ctypes.create_unicode_buffer(32768)
    length = kernel32.GetFinalPathNameByHandleW(
        ctypes.c_void_p(handle), buffer, len(buffer), 0)
    if length == 0 or length >= len(buffer):
        raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
    canonical = buffer.value
    if canonical.startswith("\\\\?\\UNC\\"):
        canonical = "\\\\" + canonical[8:]
    elif canonical.startswith("\\\\?\\"):
        canonical = canonical[4:]
    size = (int(information.size_high) << 32) | int(information.size_low)
    file_index = ((int(information.file_index_high) << 32)
                  | int(information.file_index_low))
    return _NativeFileSnapshotV1(
        os.path.normcase(os.path.abspath(canonical)),
        (int(information.volume_serial), file_index),
        size,
        _windows_filetime_ns_v1(information.creation_time),
        _windows_filetime_ns_v1(information.last_write_time),
    )


def _windows_read_handle_bytes_v1(handle: int) -> bytes:
    kernel32 = _windows_apis_v1()
    if not kernel32.SetFilePointerEx(ctypes.c_void_p(handle), 0, None, 0):
        raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
    chunks: list[bytes] = []
    while True:
        buffer = ctypes.create_string_buffer(65536)
        count = ctypes.c_uint32()
        if not kernel32.ReadFile(
                ctypes.c_void_p(handle), buffer, len(buffer), ctypes.byref(count), None):
            raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
        if count.value == 0:
            return b"".join(chunks)
        chunks.append(buffer.raw[:count.value])


def _read_posix_descriptor_bytes_v1(descriptor: int) -> bytes:
    os.lseek(descriptor, 0, os.SEEK_SET)
    return b"".join(iter(lambda: os.read(descriptor, 65536), b""))


def publication_owner_repo_v1() -> Path:
    """Consume the claim-run physical-owner locator without a caller path."""
    fields = _publication_custody_tuple_v1()
    return require_repo(fields[4])


def _publication_custody_environment_v1() -> dict[str, str]:
    """Carry only the host-supplied session join beyond fixed Git inputs."""
    environment = git_environment()
    session_id = os.environ.get("CODEX_SESSION_ID")
    if session_id is not None:
        environment["CODEX_SESSION_ID"] = session_id
    return environment


def _publication_custody_tuple_v1() -> tuple[str, ...]:
    """Read the unchanged no-argument eight-field custody contract exactly."""
    return _read_owner_custody_tuple_v1(
        "--publication-custody", "implementaudit.publication-custody.v1", 8)


def _read_owner_custody_tuple_v1(command: str, schema: str, width: int) -> tuple[str, ...]:
    """Read an exact, closed, read-only claim-owner locator."""
    if (command, schema, width) not in {
        ("--publication-custody", "implementaudit.publication-custody.v1", 8),
        ("--recovery-custody", "implementaudit.recovery-custody-locator.v1", 12),
    }:
        raise RotationError("custody locator contract is invalid")
    claim_helper = Path(__file__).with_name("claim-run.sh")
    executable_repo = claim_helper.parents[3]
    runner = ([r"C:\Program Files\Git\bin\bash.exe", "--noprofile", "--norc"]
              if os.name == "nt" else ["/bin/bash", "--noprofile", "--norc"])
    completed = subprocess.run(
        [*runner, str(claim_helper), command],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(executable_repo),
        env=_publication_custody_environment_v1(), check=False)
    if completed.returncode != 0:
        raise RotationError("publication custody owner contract is unavailable")
    if (completed.stderr or not completed.stdout.endswith(b"\n")
            or b"\n" in completed.stdout[:-1]):
        raise RotationError("publication custody owner contract is invalid")
    try:
        fields = tuple(completed.stdout[:-1].decode("utf-8", "strict").split("\t"))
    except UnicodeDecodeError as exc:
        raise RotationError("publication custody owner contract is invalid") from exc
    if len(fields) != width or fields[0] != schema:
        raise RotationError("publication custody owner contract is invalid")
    return fields


def _require_publication_custody_recheck_v1(expected: object) -> None:
    try:
        observed = _publication_custody_tuple_v1()
    except RotationError as exc:
        raise RotationError("publication custody changed during the final fence") from exc
    if type(expected) is not tuple or len(expected) != 8 or observed != expected:
        raise RotationError("publication custody changed during the final fence")


def _decode_custody_invalidation_v1(raw: bytes, controller_id: str,
                                     controller_oid: str, claim_id: str) -> list[str]:
    """Shared existing publication invalidation grammar and custody join."""
    fields = raw.decode("utf-8", "strict").rstrip("\n").split("\t")
    if (len(fields) != 6 or fields[:4] != [
            "implementaudit.continuity-invalidation.v1", controller_id,
            controller_oid, claim_id]
            or fields[4] not in {"host-reported-compaction", "new-session",
                                 "handoff-resume", "manual-resume", "inferred-context-gap"}
            or not fields[5]):
        raise RotationError("publication invalidation does not bind current custody")
    return fields


def observe_recovery_subject_v1() -> dict[str, object]:
    """Observe an invalidated unchanged predecessor; grant no recovery admission.

    Opaque boundary identity is a subject, never evidence that an event occurred.
    All authority comes from the installed physical owner and its H0 join. No
    path, controller, receipt or caller assertion is accepted as an argument.
    """
    contract = ("--recovery-custody", "implementaudit.recovery-custody-locator.v1", 12)
    custody = _read_owner_custody_tuple_v1(*contract)
    (_, controller, controller_oid, claim, repo_text, common_text, root_text,
     run_id, epoch, receipt_token, binding_generation, binding_digest) = custody
    if (not CONTROLLER_ID.fullmatch(controller) or not GIT_OID.fullmatch(controller_oid)
            or not CLAIM_ID.fullmatch(claim) or not TOKEN_ID.fullmatch(run_id)
            or not GENERATION_ID.fullmatch(epoch)
            or not GENERATION_ID.fullmatch(binding_generation)
            or re.fullmatch(r"sha256:[0-9a-f]{64}", binding_digest) is None):
        raise RotationError("recovery custody locator is malformed")
    repo = require_repo(repo_text)
    common = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip()).resolve()
    if common != Path(common_text).resolve():
        raise RotationError("recovery custody common directory differs")
    root = require_run_root(root_text, repo)
    if root.name != run_id:
        raise RotationError("recovery custody run identity differs")
    pointer_ref = f"refs/implementaudit/current-generations/{controller}"
    marker_ref = f"refs/implementaudit/current-generation-migrations/{controller}"
    invalidation_ref = f"refs/implementaudit/continuity-invalidations/{controller}"
    receipt_ref = f"refs/implementaudit/continuity-receipts/{controller}/{epoch}"
    refs = [f"refs/implementaudit/controllers/{controller}", pointer_ref,
            marker_ref, invalidation_ref, receipt_ref]
    guards = {ref: read_optional_exact_ref_oid_v1(repo, ref) for ref in refs}
    if any(value is None for value in guards.values()) or guards[refs[0]] != controller_oid:
        raise RotationError("recovery custody route is incomplete")
    if receipt_token != receipt_ref + "@" + str(guards[receipt_ref]):
        raise RotationError("recovery custody H0 predecessor receipt differs")
    pointer_oid = str(guards[pointer_ref])
    pointer = load_canonical_generation_pointer_oid_v1(repo, pointer_oid)
    if tuple(pointer[key] for key in ("controller_id", "claim_id", "run_id", "generation_id", "source_epoch")) != (
            controller, claim, run_id, epoch, epoch):
        raise RotationError("recovery custody pointer identity differs")
    receipt = _receipt_record_v1(repo, receipt_token)
    live = {"repo_path": repo, "controller_id": controller, "controller_oid": controller_oid,
            "claim_id": claim, "run_id": run_id, "source_epoch": epoch, "pointer_ref": pointer_ref}
    require_complete_pointer_receipt_marker_route_v1(
        live=live, receipt=receipt, pointer=pointer, pointer_oid=pointer_oid,
        marker_oid=str(guards[marker_ref]))
    raw_invalidation = read_exact_git_blob_oid_v1(repo, str(guards[invalidation_ref]))
    # Recovery subjects require exact canonical wire bytes. Keep the established
    # publication decoder's compatibility behavior confined to publication.
    if (not raw_invalidation.endswith(b"\n") or b"\n" in raw_invalidation[:-1]
            or b"\r" in raw_invalidation or b"\x00" in raw_invalidation
            or len(raw_invalidation[:-1].split(b"\t")) != 6):
        raise RotationError("recovery subject invalidation bytes are noncanonical")
    try:
        invalidation = _decode_custody_invalidation_v1(
            raw_invalidation, controller, controller_oid, claim)
    except UnicodeError as exc:
        raise RotationError("recovery subject invalidation is malformed") from exc
    if receipt["fields"][5] == guards[invalidation_ref]:
        raise RotationError("recovery subject requires a new invalidation")
    expected = {"STATE": pointer["hot_state_digest"], "ROADMAP": pointer["hot_roadmap_digest"],
                "WORK_GRAPH": pointer["work_graph_digest"]}
    with PublicationObservationSessionV1({"run_root_path": root}, expected) as session:
        initial = session.observe(reopen=True)
        if _read_owner_custody_tuple_v1(*contract) != custody:
            raise RotationError("recovery custody changed during observation")
        # Re-run the bounded immutable join: this also fences predecessor and
        # permanent genesis receipt refs resolved by the existing owner checker.
        require_complete_pointer_receipt_marker_route_v1(
            live=live, receipt=_receipt_record_v1(repo, receipt_token), pointer=pointer,
            pointer_oid=pointer_oid, marker_oid=str(guards[marker_ref]))
        if {ref: read_optional_exact_ref_oid_v1(repo, ref) for ref in refs} != guards:
            raise RotationError("recovery subject refs changed during observation")
        if session.observe(reopen=True) != initial:
            raise RotationError("recovery subject hot inputs changed during observation")
    return {
        "schema": "implementaudit.recovery-subject-observation.v1",
        "controller_id": controller, "controller_oid": controller_oid, "claim_id": claim,
        "repository_identity": str(repo), "explicit_run_root": str(root),
        "predecessor_epoch": epoch, "predecessor_receipt": receipt_token,
        "pointer_oid": pointer_oid, "marker_oid": guards[marker_ref],
        "subject_invalidation_oid": guards[invalidation_ref],
        "subject_boundary_kind": invalidation[4], "subject_boundary_event_id": invalidation[5],
        "host_binding_generation": binding_generation, "host_binding_digest": binding_digest,
        "hot_input_digests": expected, "genuine_host_evidence": "UNVERIFIED",
        "continuity_current": False, "ordinary_effect_authority": "NONE",
        "route_open_authority": "NONE",
    }


def _recovery_owner_module_v1(filename: str):
    """Load only a physical sibling owner; never an executable supplied by a caller."""
    import importlib.util
    if filename not in {"route-transaction.py", "host-session-binding.py"}:
        raise RotationError("recovery owner is outside the closed population")
    path = Path(__file__).with_name(filename)
    _read_bounded_regular_bytes_v1(path, path.parent, "recovery owner source is unsafe")
    spec = importlib.util.spec_from_file_location(
        "implementaudit_reentry_" + filename.replace("-", "_").replace(".", "_"), path)
    if spec is None or spec.loader is None:
        raise RotationError("recovery owner source is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _reconciled_recovery_state_v1(raw: bytes, *, subject: dict[str, object],
                                  proposal: dict[str, object], terminal_oid: str,
                                  head: str, tree: str) -> tuple[bytes, str]:
    """Build only the transition expressly accepted by the recovery governor."""
    if (set(proposal) != {"schema", "predecessor_state_digest", "next_action_policy", "next_action"}
            or proposal["schema"] != "implementaudit.recovery-reconciliation-proposal.v1"
            or proposal["predecessor_state_digest"] != "sha256:" + hashlib.sha256(raw).hexdigest()
            or proposal["predecessor_state_digest"] != "sha256:" + subject["hot_input_digests"]["STATE"]
            or proposal["next_action_policy"] not in {"RETAIN_PREDECESSOR", "REPLACE_NEXT_ACTION"}
            or not all(GIT_OID.fullmatch(value) for value in (terminal_oid, head, tree))):
        raise RotationError("recovery reconciliation proposal does not bind the exact predecessor")
    action = proposal["next_action"]
    if (type(action) is not str or not action or len(action) > 4096
            or len(action.splitlines()) != 1
            or action != action.strip() or action.lower() in {"-", "none", "pending"}
            or action != action.strip("`")
            or any(ord(char) < 32 or char == "|" or ord(char) == 127 for char in action)):
        raise RotationError("recovery reconciliation next action is not one exact table cell")
    try:
        lines = raw.decode("utf-8", "strict").splitlines(keepends=True)
    except UnicodeError as exc:
        raise RotationError("recovery predecessor STATE is not UTF-8") from exc
    epoch = str(subject["predecessor_epoch"])
    if not GENERATION_ID.fullmatch(epoch) or not 0 < int(epoch[1:], 16) < 0xFFFF:
        raise RotationError("recovery predecessor epoch cannot advance")
    successor = f"G{int(epoch[1:], 16) + 1:04X}"
    epoch_lines = [i for i, line in enumerate(lines) if line.startswith("Current epoch: ")]
    actions = [i for i, line in enumerate(lines) if len(line.split("|")) > 3
               and line.split("|")[1].strip() == "Next action"]
    rows = [i for i, line in enumerate(lines) if len(line.split("|")) > 6
            and line.split("|")[1].strip(" \t`") == epoch]
    if (len(epoch_lines) != 1 or lines[epoch_lines[0]].rstrip("\r\n") != "Current epoch: " + epoch
            or len(actions) != 1 or len(rows) != 1
            or any(len(line.split("|")) > 2 and line.split("|")[1].strip(" \t`") == successor
                   for line in lines)):
        raise RotationError("recovery predecessor STATE transition anchors are ambiguous")
    old_action = lines[actions[0]].split("|")[2].strip(" \t`")
    if proposal["next_action_policy"] == "RETAIN_PREDECESSOR" and action != old_action:
        raise RotationError("retained recovery next action differs from the accepted predecessor")
    newline = "\r\n" if lines[epoch_lines[0]].endswith("\r\n") else "\n"
    lines[epoch_lines[0]] = "Current epoch: " + successor + newline
    if proposal["next_action_policy"] == "REPLACE_NEXT_ACTION":
        cells = lines[actions[0]].split("|")
        old_cell = cells[2]
        leading = old_cell[:len(old_cell) - len(old_cell.lstrip(" \t"))]
        trailing = old_cell[len(old_cell.rstrip(" \t")):]
        cells[2] = leading + action + trailing
        lines[actions[0]] = "|".join(cells)
    preimage_oid = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    row = (f"| {successor} | {subject['subject_boundary_kind']} | recovery-owner | "
           f"repo at `{head}` / `{tree}` | yes | Accepted recovery reconciliation `{terminal_oid}` "
           f"state-preimage `{preimage_oid}` |" + newline)
    if not lines[rows[0]].endswith("\n"):
        raise RotationError("recovery predecessor epoch row lacks a line terminator")
    lines.insert(rows[0] + 1, row)
    return "".join(lines).encode("utf-8"), successor


def reconcile_recovery_successor_v1(*, recovery_args: argparse.Namespace,
                                    observer: object) -> dict[str, object]:
    """Realise accepted cognition under R0039 ownership; grant no currentness.

    Arguments locate the terminal owner record/native observation. The route
    owner rederives all authority; no caller-authored STATE or accepted flag is
    an input. Only STATE's epoch, explicitly accepted Next action and one
    provenance row may change. ROADMAP and WORK_GRAPH remain byte-identical.
    """
    route = _recovery_owner_module_v1("route-transaction.py")
    subject = observe_recovery_subject_v1()
    repo = Path(subject["repository_identity"])
    root = Path(subject["explicit_run_root"])
    with _acquire_r0039_publication_file_lease_v1(repo):
        terminal = route.read_terminal_recovery_v1(repo, recovery_args, observer=observer)
        record = terminal["record"]
        if (terminal["schema"] != "implementaudit.terminal-recovery-observation.v1"
                or record["recovery_capsule"]["custody"]["subject"] != subject
                or terminal["continuity_current"] is not False
                or terminal["ordinary_effect_authority"] != "NONE"):
            raise RotationError("terminal recovery owner returned foreign custody")
        with PublicationObservationSessionV1({"run_root_path": root}, subject["hot_input_digests"]) as session:
            original = {role: session.read_role_exact(role, reopen=True)
                        for role in ("STATE", "ROADMAP", "WORK_GRAPH")}
            head = git(repo, "rev-parse", "HEAD").decode("ascii").strip()
            tree = git(repo, "rev-parse", "HEAD^{tree}").decode("ascii").strip()
            updated, successor = _reconciled_recovery_state_v1(
                original["STATE"], subject=subject, proposal=terminal["canonical_reconciliation"],
                terminal_oid=terminal["record_oid"], head=head, tree=tree)
            successor_ref = f"refs/implementaudit/continuity-receipts/{subject['controller_id']}/{successor}"
            if read_optional_exact_ref_oid_v1(repo, successor_ref) is not None:
                raise RotationError("recovery successor receipt already exists")
            # Immutable local custody only: no new ref or registry, and no
            # preimage bytes are copied into the distributed source package.
            preimage_oid = git(repo, "hash-object", "-w", "--stdin", input_bytes=original["STATE"]).decode("ascii").strip()
            if read_exact_git_blob_oid_v1(repo, preimage_oid) != original["STATE"]:
                raise RotationError("recovery STATE preimage readback differs")
            path = root / (".recovery-state-" + terminal["record_oid"] + ".tmp")
            created = False
            try:
                with path.open("xb") as stream:
                    created = True
                    stream.write(updated)
                    stream.flush()
                    os.fsync(stream.fileno())
                if (route.read_terminal_recovery_v1(repo, recovery_args, observer=observer) != terminal
                        or observe_recovery_subject_v1() != subject
                        or git(repo, "rev-parse", "HEAD").decode("ascii").strip() != head
                        or git(repo, "rev-parse", "HEAD^{tree}").decode("ascii").strip() != tree):
                    raise RotationError("recovery reconciliation authority changed before mutation")
                session.observe(reopen=True)
                # Windows replacement refuses an open destination even with
                # delete sharing. Close only its verified retained handle at
                # this last write boundary; the other hot handles stay held.
                next(retained for role, retained in session.opened if role == "STATE").close()
                os.replace(path, root / "STATE.md")
            finally:
                if created and path.exists():
                    path.unlink()
        try:
            with PublicationObservationSessionV1({"run_root_path": root}, {
                    **subject["hot_input_digests"], "STATE": hashlib.sha256(updated).hexdigest()}) as session:
                session.observe(reopen=True)
        except Exception as exc:
            raise RotationError("recovery STATE was replaced but post-write custody is uncertain; owner readback required") from exc
        return {
            "schema": "implementaudit.recovery-reconciliation.v1", "subject": subject,
            "terminal_record_oid": terminal["record_oid"],
            "route_transaction_id": record["route_transaction_id"],
            "accepted_return_digest": record["lifecycle"]["child_return"]["digest"],
            "governor_decision_digest": record["lifecycle"]["governor_decision"]["digest"],
            "successor_epoch": successor, "successor_state_digest": hashlib.sha256(updated).hexdigest(),
            "next_action": terminal["canonical_reconciliation"]["next_action"],
            "continuity_current": False, "ordinary_effect_authority": "NONE",
            "next_owner_action": "prepare_live_successor_v1",
        }


def _read_reconciled_recovery_v1(route: object, binding_owner: object,
                                 recovery_args: argparse.Namespace) -> dict[str, object]:
    """Recognize only an exact owner postimage; never replay recovery cognition.

    The native/H0 predecessor is historical after this boundary. Its accepted
    immutable terminal lifecycle is evidence, not a claim of fresh old custody.
    """
    locator = _read_owner_custody_tuple_v1("--recovery-custody", "implementaudit.recovery-custody-locator.v1", 12)
    repo = require_repo(locator[4])
    oid, record = route.current_ref(repo, recovery_args.controller, route_transaction_id=recovery_args.route_transaction_id)
    if (oid != recovery_args.expected_record or record is None
            or record.get("schema") != route.RECOVERY_RECORD_SCHEMA or record.get("route_state") != "SATISFIED"):
        raise RotationError("partial recovery lacks its exact accepted terminal owner record")
    capsule = record["recovery_capsule"]
    subject = capsule["custody"]["subject"]
    if ((locator[1], locator[2], locator[3], str(repo), str(Path(locator[6]))) != (
            subject["controller_id"], subject["controller_oid"], subject["claim_id"],
            subject["repository_identity"], subject["explicit_run_root"])
            or route.executing_package_evidence(repo, route.recovery_request_v3(capsule), "REQUIRED") != (capsule["package"], capsule["child_source"])):
        raise RotationError("partial recovery physical owner or package changed")
    returned = route.decoded_artifact(route.validate_bytes_identity(record["lifecycle"]["child_return"], "recovery return"), "recovery return")
    proposal = route.recovery_reconciliation_proposal_v1(returned["payload"]["canonical_reconciliation"], capsule)
    root = require_run_root(locator[6], repo)
    with PublicationObservationSessionV1({"run_root_path": root}, None) as session:
        raw = session.read_role_exact("STATE", reopen=True)
        matches = re.findall(rb"Accepted recovery reconciliation `([0-9a-f]{40})` state-preimage `([0-9a-f]{40})`", raw)
        own = [preimage for terminal, preimage in matches if terminal.decode("ascii") == oid]
        if len(own) != 1:
            raise RotationError("partial recovery has no unique owner preimage locator")
        old = read_exact_git_blob_oid_v1(repo, own[0].decode("ascii"))
        expected, successor = _reconciled_recovery_state_v1(old, subject=subject, proposal=proposal, terminal_oid=oid,
            head=git(repo, "rev-parse", "HEAD").decode("ascii").strip(), tree=git(repo, "rev-parse", "HEAD^{tree}").decode("ascii").strip())
        if raw != expected:
            raise RotationError("partial recovery STATE is not the exact accepted owner postimage")
        session.bind_expected_digests({**subject["hot_input_digests"], "STATE": hashlib.sha256(expected).hexdigest()})
        session.observe(reopen=True)
    common = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip()
    for ref, expected_oid in (
        (f"refs/implementaudit/continuity-invalidations/{subject['controller_id']}", subject["subject_invalidation_oid"]),
        (f"refs/implementaudit/current-generation-migrations/{subject['controller_id']}", subject["marker_oid"]),
        tuple(subject["predecessor_receipt"].rsplit("@", 1))):
        if read_optional_exact_ref_oid_v1(repo, ref) != expected_oid:
            raise RotationError("partial recovery historical authority changed")
    use_path = Path(common) / "implementaudit-recovery-capsules" / recovery_args.controller / (
        "native-v3-" + capsule["native_invocation_digest"].removeprefix("sha256:") + ".used")
    if _read_bounded_regular_bytes_v1(use_path, Path(common), "recovery use custody is unsafe") != route.recovery_capsule_use_v3(capsule, record["route_transaction_id"]):
        raise RotationError("partial recovery native use custody changed")
    expected_store = Path(__file__).resolve().parents[3].parents[3] / "data" / Path(__file__).resolve().parents[3].parent.parent.name / Path(__file__).resolve().parents[3].parent.name / "host-session-binding-v1"
    if (Path(recovery_args.store).resolve() != expected_store.resolve()
            or recovery_args.host_id != record["host_id"] or recovery_args.host_session_id != record["host_session_id"]
            or recovery_args.binding_generation != record["host_binding_generation"]):
        raise RotationError("partial recovery H0 locator is foreign")
    execution = route.resolve_execution_evidence(Path(recovery_args.store), returned["payload"]["holon_execution_evidence"],
        record["host_id"], record["host_session_id"], record["host_binding_generation"], "audit-state",
        record["route_transaction_id"], record["obligation_id"], record["lifecycle"]["delivery"]["packet"]["digest"])
    if execution != record["lifecycle"]["execution_evidence"]:
        raise RotationError("partial recovery accepted execution evidence changed")
    terminal = {"schema": "implementaudit.terminal-recovery-observation.v1", "record_oid": oid,
        "record": record, "canonical_reconciliation": proposal, "continuity_current": False,
        "ordinary_effect_authority": "NONE"}
    reconciliation = {"schema": "implementaudit.recovery-reconciliation.v1", "subject": subject,
        "terminal_record_oid": oid, "route_transaction_id": record["route_transaction_id"],
        "accepted_return_digest": record["lifecycle"]["child_return"]["digest"],
        "governor_decision_digest": record["lifecycle"]["governor_decision"]["digest"],
        "successor_epoch": successor, "successor_state_digest": hashlib.sha256(expected).hexdigest(),
        "next_action": proposal["next_action"], "continuity_current": False, "ordinary_effect_authority": "NONE",
        "next_owner_action": "inspect exact existing successor pointer/receipt/H0 boundary"}
    if (route.current_ref(repo, recovery_args.controller, route_transaction_id=recovery_args.route_transaction_id) != (oid, record)
            or _read_owner_custody_tuple_v1("--recovery-custody", "implementaudit.recovery-custody-locator.v1", 12) != locator):
        raise RotationError("partial recovery custody changed during readback")
    return {"terminal": terminal, "reconciliation": reconciliation, "locator": locator}


def _verify_completed_recovery_predecessor_v1(records, expected_digest):
    """Restore only a local copy of the exact original H0 record for hashing.

    command_bind creates G0001 with a null reason. command_rebind places its
    reason on both the superseded record and its new ACTIVE successor. A later
    rebind overwrites the latter reason, leaving the former as exact history.
    """
    if len(records) < 2:
        raise RotationError("completed recovery lacks its retained H0 predecessor")
    original = dict(records[-2])
    if original.get("binding_generation") == "G0001" and original.get("predecessor_generation") is None:
        reason = None
    else:
        older = records[-3] if len(records) > 2 else {}
        if (older.get("binding_generation") != original.get("predecessor_generation")
                or older.get("status") != "SUPERSEDED"
                or not isinstance(older.get("supersession_or_tombstone_reason"), str)
                or not older["supersession_or_tombstone_reason"]):
            raise RotationError("completed recovery lacks exact original H0 transition history")
        reason = older["supersession_or_tombstone_reason"]
    original["status"] = "ACTIVE"
    original["supersession_or_tombstone_reason"] = reason
    observed = "sha256:" + hashlib.sha256(json.dumps(original, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if not hmac.compare_digest(observed, expected_digest):
        raise RotationError("completed recovery predecessor differs from accepted H0 custody")


def complete_recovery_reentry_v1(*, recovery_args: argparse.Namespace,
                                 observer: object) -> dict[str, object]:
    """Use existing publication, receipt and H0 producers after reconciliation.

    This ordered operation is not an atomic transaction across hot files, Git
    and H0. A failed stage stops with its last completed owner boundary; it does
    not roll back published history or pretend that ordinary route admission
    followed. A fresh ordinary route must still pass its unchanged owner gate.
    """
    route = _recovery_owner_module_v1("route-transaction.py")
    binding_owner = _recovery_owner_module_v1("host-session-binding.py")
    partial = None
    try:
        initial_subject = observe_recovery_subject_v1()
    except RotationError:
        partial = _read_reconciled_recovery_v1(route, binding_owner, recovery_args)
        initial_subject = partial["reconciliation"]["subject"]
    repo = Path(initial_subject["repository_identity"])
    initial_custody = _read_owner_custody_tuple_v1(
        "--recovery-custody", "implementaudit.recovery-custody-locator.v1", 12)
    terminal = (route.read_terminal_recovery_v1(repo, recovery_args, observer=observer)
                if partial is None else partial["terminal"])
    capsule = terminal["record"]["recovery_capsule"]
    store = Path(recovery_args.store)
    _, binding_state = binding_owner.load_state(store, recovery_args.host_id, recovery_args.host_session_id)
    binding = dict(binding_owner.current_record(binding_state, require_active=True))
    owner = binding_owner.load_owner(store)
    completed_binding = (partial is not None and binding["binding_generation"] == binding_owner.next_generation(initial_subject["host_binding_generation"]))
    if not completed_binding and "sha256:" + hashlib.sha256(json.dumps(binding, sort_keys=True, separators=(",", ":")).encode()).hexdigest() != initial_subject["host_binding_digest"]:
        raise RotationError("recovery H0 binding differs before reconciliation")
    terminal_ref = route.transaction_route_ref_name(recovery_args.controller, recovery_args.route_transaction_id)
    stable_refs = {
        f"refs/implementaudit/controllers/{initial_subject['controller_id']}": initial_subject["controller_oid"],
        f"refs/implementaudit/current-generation-migrations/{initial_subject['controller_id']}": initial_subject["marker_oid"],
        f"refs/implementaudit/continuity-invalidations/{initial_subject['controller_id']}": initial_subject["subject_invalidation_oid"],
        initial_subject["predecessor_receipt"].rsplit("@", 1)[0]: initial_subject["predecessor_receipt"].rsplit("@", 1)[1],
        terminal_ref: terminal["record_oid"],
    }
    stage = "TERMINAL_RECOVERY_VERIFIED"
    try:
        reconciliation = (reconcile_recovery_successor_v1(recovery_args=recovery_args, observer=observer)
                          if partial is None else partial["reconciliation"])
        stage = "STATE_RECONCILED"
        if reconciliation["subject"] != initial_subject or reconciliation["terminal_record_oid"] != terminal["record_oid"]:
            raise RotationError("recovery reconciliation changed its initial terminal subject")

        def fence() -> None:
            if ({ref: read_optional_exact_ref_oid_v1(repo, ref) for ref in stable_refs} != stable_refs
                    or _read_owner_custody_tuple_v1("--recovery-custody", "implementaudit.recovery-custody-locator.v1", 12) != initial_custody
                    or route.executing_package_evidence(repo, route.recovery_request_v3(capsule), "REQUIRED") != (capsule["package"], capsule["child_source"])):
                raise RotationError("recovery re-entry custody changed between owner boundaries")
            with PublicationObservationSessionV1({"run_root_path": initial_subject["explicit_run_root"]}, {
                    **initial_subject["hot_input_digests"], "STATE": reconciliation["successor_state_digest"]}) as session:
                session.observe(reopen=True)

        fence()
        pointer_ref = f"refs/implementaudit/current-generations/{initial_subject['controller_id']}"
        pointer = read_optional_exact_ref_oid_v1(repo, pointer_ref)
        if pointer == initial_subject["pointer_oid"]:
            if completed_binding:
                raise RotationError("completed H0 has no published successor")
            prepared = prepare_live_successor_v1()
            stage = "SUCCESSOR_PREPARED"
            fence()
            pointer = publish_generation_pointer_v1(candidate_pointer_oid=prepared["candidate_pointer_oid"],
                additional_guard_refs=tuple(sorted(stable_refs.items())))
        else:
            previous = load_canonical_generation_pointer_oid_v1(repo, initial_subject["pointer_oid"])
            previous_manifest = load_canonical_generation_manifest_oid_v1(repo, previous["generation_manifest_oid"])
            # Readback reconstructs already-published bytes from authenticated
            # terminal/postimage custody; the ordinary producer still obtains
            # its context exclusively from its unchanged publication gate.
            expected_manifest, manifest_raw = _build_generation_manifest_in_context_v1(previous_manifest, [], context={
                "controller_id": initial_subject["controller_id"], "claim_id": initial_subject["claim_id"],
                "run_id": previous["run_id"], "generation_id": reconciliation["successor_epoch"],
                "source_epoch": reconciliation["successor_epoch"]})
            manifest_oid = git(repo, "hash-object", "--stdin", input_bytes=manifest_raw).decode("ascii").strip()
            expected_pointer, pointer_raw = build_generation_pointer_v1(
                controller_id=initial_subject["controller_id"], claim_id=initial_subject["claim_id"],
                run_id=previous["run_id"], generation_id=reconciliation["successor_epoch"], source_epoch=reconciliation["successor_epoch"],
                predecessor_pointer_oid=initial_subject["pointer_oid"], predecessor_pointer_digest=previous["pointer_digest"],
                generation_manifest_oid=manifest_oid, generation_manifest_digest=expected_manifest["manifest_digest"],
                cold_high_water=expected_manifest["high_water"], hot_state_digest=reconciliation["successor_state_digest"],
                hot_roadmap_digest=initial_subject["hot_input_digests"]["ROADMAP"], work_graph_path=EXPECTED_WORK_GRAPH_PATH,
                work_graph_digest=initial_subject["hot_input_digests"]["WORK_GRAPH"], degraded_state=previous["degraded_state"])
            if (pointer != git(repo, "hash-object", "--stdin", input_bytes=pointer_raw).decode("ascii").strip()
                    or load_canonical_generation_pointer_oid_v1(repo, str(pointer)) != expected_pointer
                    or load_canonical_generation_manifest_oid_v1(repo, manifest_oid) != expected_manifest):
                raise RotationError("partial recovery pointer is not the exact accepted successor")
        stage = "SUCCESSOR_PUBLISHED"
        fence()
        runner = ([r"C:\Program Files\Git\bin\bash.exe", "--noprofile", "--norc"]
                  if os.name == "nt" else ["/bin/bash", "--noprofile", "--norc"])
        claim = str(Path(__file__).with_name("claim-run.sh"))
        def claim_call(*arguments: str) -> str:
            result = subprocess.run([*runner, claim, *arguments], cwd=repo,
                env=_publication_custody_environment_v1(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if result.returncode != 0 or result.stderr or not result.stdout.endswith(b"\n") or b"\n" in result.stdout[:-1]:
                raise RotationError("R0011 recovery re-entry owner refused or returned uncertain output")
            return result.stdout[:-1].decode("utf-8", "strict")
        expected_ref = f"refs/implementaudit/continuity-receipts/{initial_subject['controller_id']}/{reconciliation['successor_epoch']}"
        existing_receipt = read_optional_exact_ref_oid_v1(repo, expected_ref)
        if existing_receipt is None:
            if completed_binding:
                raise RotationError("completed H0 has no exact successor receipt")
            receipt = claim_call("--resume-controller", initial_subject["controller_id"], "--boundary",
                initial_subject["subject_boundary_kind"], "--epoch", reconciliation["successor_epoch"])
        else:
            receipt = expected_ref + "@" + existing_receipt
        if receipt != expected_ref + "@" + str(read_optional_exact_ref_oid_v1(repo, expected_ref)):
            raise RotationError("R0011 successor receipt readback differs")
        stage = "R0011_RECEIPT_VERIFIED"
        fence()
        if claim_call("--require-current-continuity", initial_subject["controller_id"]) != receipt:
            raise RotationError("R0011 strict currentness differs from successor receipt")
        if completed_binding:
            records = binding_state["records"]
            prior = records[-2] if len(records) > 1 else {}
            _verify_completed_recovery_predecessor_v1(records, initial_subject["host_binding_digest"])
            changed_keys = {"binding_generation", "predecessor_generation", "status", "supersession_or_tombstone_reason",
                            "applicable_continuity_generation", "applicable_continuity_receipt"}
            expected_reason = "accepted-recovery:" + terminal["record_oid"]
            if (prior.get("binding_generation") != initial_subject["host_binding_generation"]
                    or prior.get("status") != "SUPERSEDED"
                    or binding["predecessor_generation"] != initial_subject["host_binding_generation"]
                    or binding["supersession_or_tombstone_reason"] != expected_reason
                    or prior.get("supersession_or_tombstone_reason") != expected_reason
                    or binding["applicable_continuity_generation"] != reconciliation["successor_epoch"]
                    or binding["applicable_continuity_receipt"] != receipt
                    or prior.get("applicable_continuity_receipt") != initial_subject["predecessor_receipt"]
                    or any(prior.get(key) != value for key, value in binding.items() if key not in changed_keys)):
                raise RotationError("completed recovery H0 lineage is not the exact owner successor")
            return {"schema": "implementaudit.recovery-reentry.v1", "stage": "H0_REBOUND", "idempotent": True,
                "reconciliation": reconciliation, "published_pointer_oid": pointer,
                "continuity_receipt": receipt, "host_binding_generation": binding["binding_generation"],
                "continuity_current": True, "ordinary_effect_authority": "NONE",
                "next_owner_action": "fresh ordinary route decision and strict admit-current"}
        rebind = argparse.Namespace(store=str(store), owner_id=owner["owner_id"],
            expected_generation=binding["binding_generation"], reason="accepted-recovery:" + terminal["record_oid"],
            host_id=binding["host_id"], host_session_id=binding["host_session_id"],
            controller_id=binding["controller_id"], claim_id=binding["claim_id"],
            explicit_run_root=binding["explicit_run_root"], repository_identity=binding["repository_identity"],
            git_common_directory_identity=binding["git_common_directory_identity"], worktree_identity=binding["worktree_identity"],
            activation_event_id=binding["activation_event_id"], activation_receipt=binding["activation_receipt"],
            continuity_generation=reconciliation["successor_epoch"], continuity_receipt=receipt)
        # This is the existing H0 writer, including its own expected-generation
        # check, writer lock, immutable predecessor retention and atomic state IO.
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            binding_owner.command_rebind(rebind)
        stage = "H0_REBOUND"
        _, post_state = binding_owner.load_state(store, binding["host_id"], binding["host_session_id"])
        post_binding = binding_owner.current_record(post_state, require_active=True)
        expected_binding = binding_owner.binding_from_args(rebind,
            binding_generation=binding_owner.next_generation(binding["binding_generation"]),
            predecessor_generation=binding["binding_generation"], reason=rebind.reason)
        if (post_binding != expected_binding
                or claim_call("--require-current-continuity", initial_subject["controller_id"]) != receipt
                or {ref: read_optional_exact_ref_oid_v1(repo, ref) for ref in stable_refs} != stable_refs
                or route.executing_package_evidence(repo, route.recovery_request_v3(capsule), "REQUIRED") != (capsule["package"], capsule["child_source"])):
            raise RotationError("recovery re-entry successor readback differs")
        return {"schema": "implementaudit.recovery-reentry.v1", "stage": stage, "idempotent": False,
            "reconciliation": reconciliation, "published_pointer_oid": pointer,
            "continuity_receipt": receipt, "host_binding_generation": post_binding["binding_generation"],
            "continuity_current": True, "ordinary_effect_authority": "NONE",
            "next_owner_action": "fresh ordinary route decision and strict admit-current"}
    except (Exception, SystemExit) as exc:
        next_action = {
            "TERMINAL_RECOVERY_VERIFIED": "read exact STATE preimage/postimage before retrying owner reconciliation",
            "STATE_RECONCILED": "read exact current-generation pointer and successor receipt; prepare_live_successor_v1() only while predecessor pointer remains exact",
            "SUCCESSOR_PREPARED": "publish_generation_pointer_v1(candidate_pointer_oid=prepared.candidate_pointer_oid)",
            "SUCCESSOR_PUBLISHED": "claim-run.sh --resume-controller <controller> --boundary <subject_boundary_kind> --epoch <successor_epoch>",
            "R0011_RECEIPT_VERIFIED": "host-session-binding.py rebind with exact expected predecessor binding generation and successor receipt",
            "H0_REBOUND": "strict claim currentness and exact H0 successor-lineage readback",
        }[stage]
        pending = {"schema": "implementaudit.recovery-reentry-pending.v1", "last_completed_stage": stage,
            "terminal_record_oid": terminal["record_oid"], "route_transaction_id": recovery_args.route_transaction_id,
            "next_owner_action": next_action,
            "retry_entry": "complete_recovery_reentry_v1 with the same exact terminal locators; owner rederives partial state",
            "reconciliation": locals().get("reconciliation"), "prepared": locals().get("prepared"),
            "observed_pointer_oid": locals().get("pointer"), "continuity_receipt": locals().get("receipt"),
            "ordinary_effect_authority": "NONE"}
        error = RotationError(f"recovery re-entry stopped after {stage}; {next_action}; exact owner readback required: {exc}")
        error.recovery_pending = pending
        raise error from exc
def _open_governed_publication_context_v1(
        ) -> tuple[dict[str, object], "PublicationObservationSessionV1"]:
    """Open receipt-bound custody and retain its mutable-file handles."""
    fields = _publication_custody_tuple_v1()
    _, controller_id, controller_oid, claim_id, repo_text, common_text, run_root_text, run_id = fields
    if (not CONTROLLER_ID.fullmatch(controller_id) or not GIT_OID.fullmatch(controller_oid)
            or not CLAIM_ID.fullmatch(claim_id) or not TOKEN_ID.fullmatch(run_id)):
        raise RotationError("publication custody owner contract is invalid")
    controller_repo = require_repo(repo_text)
    controller_common = Path(git(controller_repo, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip()).resolve()
    if controller_common != Path(common_text).resolve():
        raise RotationError("publication custody owner common directory is invalid")
    run_root = require_run_root(run_root_text, controller_repo)
    session = PublicationObservationSessionV1(
        {"run_root_path": run_root}, None).__enter__()
    try:
        state_bytes = session.read_role_exact("STATE", reopen=False)
        roadmap_bytes = session.read_role_exact("ROADMAP", reopen=False)
        generation_id = next(line.split(": ", 1)[1]
                             for line in state_bytes.decode("utf-8", "strict").splitlines()
                             if line.startswith("Current epoch: "))
        if not GENERATION_ID.fullmatch(generation_id):
            raise RotationError("publication generation identity is invalid")
        current_ref = f"refs/implementaudit/current-generations/{controller_id}"
        marker_ref = f"refs/implementaudit/current-generation-migrations/{controller_id}"
        receipt_ref = f"refs/implementaudit/continuity-receipts/{controller_id}/{generation_id}"
        invalidation_ref = f"refs/implementaudit/continuity-invalidations/{controller_id}"
        current_oid = read_optional_exact_ref_oid_v1(controller_repo, current_ref)
        marker_oid = read_optional_exact_ref_oid_v1(controller_repo, marker_ref)
        if current_oid is None and marker_oid is not None:
            raise RotationError("migration marker exists without generation pointer")
        receipt_oid = read_optional_exact_ref_oid_v1(controller_repo, receipt_ref)
        invalidation_oid = read_optional_exact_ref_oid_v1(controller_repo, invalidation_ref)
        invalidation_fields: list[str] | None = None
        if invalidation_oid is not None:
            invalidation_fields = _decode_custody_invalidation_v1(
                read_exact_git_blob_oid_v1(controller_repo, invalidation_oid),
                controller_id, controller_oid, claim_id)
        predecessor_receipt_token: str | None = None
        transition = receipt_oid is None
        if transition:
            if (invalidation_oid is None or invalidation_fields is None
                    or (current_oid is None) != (marker_oid is None)):
                raise RotationError("publication continuity receipt is unavailable")
            ordinal = int(generation_id[1:], 16)
            if ordinal <= 1:
                raise RotationError("publication continuity receipt is unavailable")
            predecessor_epoch = f"G{ordinal - 1:04X}"
            receipt_ref = (
                f"refs/implementaudit/continuity-receipts/{controller_id}/"
                f"{predecessor_epoch}")
            receipt_oid = read_optional_exact_ref_oid_v1(controller_repo, receipt_ref)
            if receipt_oid is None:
                raise RotationError("publication continuity receipt is unavailable")
            predecessor_receipt_token = receipt_ref + "@" + receipt_oid
        receipt = read_exact_git_blob_oid_v1(controller_repo, receipt_oid)
        receipt_fields = _decode_exact_receipt_fields_v1(receipt)
        head = git(controller_repo, "rev-parse", "HEAD").decode("ascii", "strict").strip()
        tree = git(controller_repo, "rev-parse", "HEAD^{tree}").decode("ascii", "strict").strip()
        state_digest = hashlib.sha256(state_bytes).hexdigest()
        roadmap_digest = hashlib.sha256(roadmap_bytes).hexdigest()
        allowed_boundaries = {"host-reported-compaction", "new-session",
                              "handoff-resume", "manual-resume",
                              "inferred-context-gap"}
        predecessor_epoch = (
            f"G{int(generation_id[1:], 16) - 1:04X}"
            if transition else generation_id)
        if current_oid is None:
            receipt_authority = [
                "implementaudit.continuity-receipt.v2", controller_id,
                controller_oid, claim_id, head, tree]
            if (len(receipt_fields) != 12
                    or receipt_fields[:6] != receipt_authority
                    or not all(HEX_SHA256.fullmatch(value)
                               for value in receipt_fields[6:8])
                    or (not transition
                        and receipt_fields[8] != (invalidation_oid or "none"))
                    or (receipt_fields[8] != "none"
                        and not GIT_OID.fullmatch(receipt_fields[8]))
                    or receipt_fields[9] not in allowed_boundaries
                    or receipt_fields[10] != predecessor_epoch
                    or not receipt_fields[11]
                    or (not transition and
                        receipt_fields[6:8] != [state_digest, roadmap_digest])):
                raise RotationError(
                    "publication continuity receipt does not bind current custody")
        else:
            predecessor_pointer = load_canonical_generation_pointer_oid_v1(
                controller_repo, current_oid)
            predecessor_live = {
                "repo_path": controller_repo, "controller_id": controller_id,
                "controller_oid": controller_oid, "claim_id": claim_id,
                "run_id": run_id, "source_epoch": predecessor_epoch,
                "pointer_ref": current_ref,
            }
            predecessor_receipt = {
                "ref": receipt_ref, "oid": receipt_oid,
                "raw": receipt, "fields": receipt_fields,
            }
            require_complete_pointer_receipt_marker_route_v1(
                live=predecessor_live, receipt=predecessor_receipt,
                pointer=predecessor_pointer, pointer_oid=current_oid,
                marker_oid=str(marker_oid))
            if predecessor_pointer["source_epoch"] != predecessor_epoch:
                raise RotationError(
                    "publication continuity receipt does not bind current custody")
            if transition:
                if receipt_fields[5] == invalidation_oid:
                    raise RotationError(
                        "publication continuity receipt does not bind current custody")
            elif (receipt_fields[5] != invalidation_oid
                    or receipt_fields[9:11] != [state_digest, roadmap_digest]
                    or receipt_fields[12] != hashlib.sha256(
                        session.read_role_exact(
                            "WORK_GRAPH", reopen=False)).hexdigest()):
                raise RotationError(
                    "publication continuity receipt does not bind current custody")
        if transition:
            state_lines = state_bytes.decode("utf-8", "strict").splitlines()
            next_actions = []
            epoch_rows = []
            for line in state_lines:
                cells = [cell.strip(" \t`") for cell in line.split("|")]
                if len(cells) > 3 and cells[1] == "Next action":
                    next_actions.append(cells[2])
                if len(cells) > 6 and cells[1] == generation_id:
                    epoch_rows.append(cells)
            expected_repo = f"repo at {head} / {tree}"
            if (len(next_actions) != 1 or not next_actions[0]
                    or next_actions[0].lower() in {"-", "none", "pending"}
                    or len(epoch_rows) != 1
                    or epoch_rows[0][2] != invalidation_fields[4]
                    or epoch_rows[0][4].replace("`", "") != expected_repo
                    or epoch_rows[0][5] != "yes"):
                raise RotationError("publication transition state is not reconciled")
        context = {
            "repo_path": controller_repo, "run_root_path": run_root,
            "controller_id": controller_id, "claim_id": claim_id,
            "run_id": run_id, "generation_id": generation_id,
            "source_epoch": generation_id, "receipt_ref": receipt_ref,
            "receipt_oid": receipt_oid,
            "predecessor_receipt_token": predecessor_receipt_token,
            "receipt_state_digest": state_digest,
            "receipt_roadmap_digest": roadmap_digest,
            "expected_old_pointer_oid": current_oid,
            "migration_marker_oid": marker_oid,
            "publication_custody_tuple": fields,
            "publication_guard_refs": tuple(sorted((
                (f"refs/implementaudit/controllers/{controller_id}", controller_oid),
                (receipt_ref, receipt_oid), (marker_ref, marker_oid or ZERO_OID),
                (invalidation_ref, invalidation_oid or ZERO_OID)))),
        }
        return context, session
    except (UnicodeDecodeError, StopIteration, IndexError) as exc:
        session.__exit__()
        raise RotationError("publication generation or receipt identity is unavailable") from exc
    except BaseException:
        session.__exit__()
        raise


def load_governed_publication_context_v1() -> dict[str, object]:
    """Read bounded controller custody without accepting a caller override."""
    context, session = _open_governed_publication_context_v1()
    session.__exit__()
    return context


def _publication_custody_fields_v1() -> tuple[Path, str, str, str, Path, str]:
    fields = _publication_custody_tuple_v1()
    _, controller_id, controller_oid, claim_id, repo_text, _, run_root_text, run_id = fields
    repo = require_repo(repo_text)
    run_root = require_run_root(run_root_text, repo)
    if (not CONTROLLER_ID.fullmatch(controller_id) or not GIT_OID.fullmatch(controller_oid)
            or not CLAIM_ID.fullmatch(claim_id) or not TOKEN_ID.fullmatch(run_id)):
        raise RotationError("publication custody owner contract is invalid")
    return repo, controller_id, controller_oid, claim_id, run_root, run_id


def _decode_exact_receipt_fields_v1(raw: bytes) -> list[str]:
    """Preserve raw receipts and enforce the one canonical v3 byte form."""
    if raw.startswith(b"implementaudit.continuity-receipt.v3\t"):
        if (not raw.endswith(b"\n") or raw.endswith(b"\n\n")
                or b"\n" in raw[:-1] or b"\r" in raw
                or any(value < 0x20 and value not in (0x09, 0x0A)
                       or value == 0x7F for value in raw)):
            raise RotationError("continuity receipt bytes are not canonical")
        body = raw[:-1]
        expected_fields = 18
    else:
        body = raw
        while body.endswith(b"\n"):
            body = body[:-1]
        if (not body.startswith(b"implementaudit.continuity-receipt.v2\t")
                or b"\n" in body or b"\r" in body):
            raise RotationError("continuity receipt bytes are not canonical")
        expected_fields = 12
    try:
        fields = body.decode("utf-8", "strict").split("\t")
    except UnicodeDecodeError as exc:
        raise RotationError("continuity receipt bytes are not canonical") from exc
    if (len(fields) != expected_fields
            or body.count(b"\t") != expected_fields - 1
            or any(field == "" for field in fields)):
        raise RotationError("continuity receipt bytes are not canonical")
    return fields


def _receipt_record_v1(repo: Path, token: str) -> dict[str, object]:
    if type(token) is not str or "@" not in token:
        raise RotationError("continuity receipt token is invalid")
    receipt_ref, receipt_oid = token.rsplit("@", 1)
    if (not receipt_ref.startswith("refs/implementaudit/continuity-receipts/")
            or not GIT_OID.fullmatch(receipt_oid)
            or read_optional_exact_ref_oid_v1(repo, receipt_ref) != receipt_oid):
        raise RotationError("continuity receipt token is invalid")
    raw = read_exact_git_blob_oid_v1(repo, receipt_oid)
    fields = _decode_exact_receipt_fields_v1(raw)
    return {"ref": receipt_ref, "oid": receipt_oid, "raw": raw, "fields": fields}


def _previous_receipt_token_v1(repo: Path, controller_id: str,
                               source_epoch: str) -> str:
    if not GENERATION_ID.fullmatch(source_epoch):
        raise RotationError("continuity receipt predecessor epoch is invalid")
    ordinal = int(source_epoch[1:], 16)
    if ordinal <= 1:
        raise RotationError("continuity receipt predecessor epoch is invalid")
    previous_epoch = f"G{ordinal - 1:04X}"
    previous_ref = (
        f"refs/implementaudit/continuity-receipts/{controller_id}/{previous_epoch}")
    previous_oid = read_optional_exact_ref_oid_v1(repo, previous_ref)
    if previous_oid is None:
        raise RotationError("continuity receipt predecessor is unavailable")
    return previous_ref + "@" + previous_oid


def _validate_predecessor_receipt_v1(
        repo: Path, token: str, *, controller_id: str, controller_oid: str,
        claim_id: str, run_id: str, expected_epoch: str) -> None:
    receipt = _receipt_record_v1(repo, token)
    fields = receipt["fields"]
    expected_ref = (
        f"refs/implementaudit/continuity-receipts/{controller_id}/{expected_epoch}")
    if receipt["ref"] != expected_ref or not isinstance(fields, list):
        raise RotationError("continuity receipt predecessor is invalid")
    if fields[0] == "implementaudit.continuity-receipt.v2":
        if (fields[:4] != [fields[0], controller_id, controller_oid, claim_id]
                or not all(GIT_OID.fullmatch(value) for value in fields[4:6])
                or not all(HEX_SHA256.fullmatch(value) for value in fields[6:8])
                or (fields[8] != "none" and not GIT_OID.fullmatch(fields[8]))
                or fields[9] not in {
                    "host-reported-compaction", "new-session", "handoff-resume",
                    "manual-resume", "inferred-context-gap"}
                or fields[10] != expected_epoch or not fields[11]):
            raise RotationError("continuity receipt predecessor is invalid")
        return
    pointer_ref = f"refs/implementaudit/current-generations/{controller_id}"
    if (fields[:5] != [fields[0], controller_id, claim_id, run_id, expected_epoch]
            or not GIT_OID.fullmatch(fields[5])
            or fields[6] != pointer_ref
            or not GIT_OID.fullmatch(fields[7])
            or not all(HEX_SHA256.fullmatch(fields[index])
                       for index in (8, 9, 10, 12, 14))
            or fields[11] != "WORK_GRAPH.json"
            or not GIT_OID.fullmatch(fields[13])
            or re.fullmatch(r"[0-9]{20}", fields[15]) is None
            or not fields[16]):
        raise RotationError("continuity receipt predecessor is invalid")
    _require_structural_predecessor_token_v1(
        fields[17], controller_id=controller_id, receipt_epoch=expected_epoch)


def _require_structural_predecessor_token_v1(
        token: str, *, controller_id: str, receipt_epoch: str) -> None:
    """Validate one predecessor token shape without hydrating earlier history."""
    if (type(token) is not str or not CONTROLLER_ID.fullmatch(controller_id)
            or not GENERATION_ID.fullmatch(receipt_epoch) or "@" not in token):
        raise RotationError("continuity receipt predecessor lineage is invalid")
    ordinal = int(receipt_epoch[1:], 16)
    if ordinal <= 1:
        raise RotationError("continuity receipt predecessor lineage is invalid")
    own_ref, own_oid = token.rsplit("@", 1)
    own_epoch = f"G{ordinal - 1:04X}"
    expected_ref = (
        f"refs/implementaudit/continuity-receipts/{controller_id}/{own_epoch}")
    if own_ref != expected_ref or not GIT_OID.fullmatch(own_oid):
        raise RotationError("continuity receipt predecessor lineage is invalid")


def _require_immediate_predecessor_v1(
        repo: Path, fields: list[str], *, controller_id: str,
        controller_oid: str, claim_id: str, run_id: str,
        source_epoch: str) -> None:
    expected_token = _previous_receipt_token_v1(repo, controller_id, source_epoch)
    if fields[17] != expected_token:
        raise RotationError("continuity receipt predecessor is not immediate")
    expected_epoch = expected_token.rsplit("/", 1)[1].split("@", 1)[0]
    _validate_predecessor_receipt_v1(
        repo, expected_token, controller_id=controller_id,
        controller_oid=controller_oid, claim_id=claim_id, run_id=run_id,
        expected_epoch=expected_epoch)


def _require_r0011_v3_verification_v1(repo: Path, token: str) -> None:
    claim_helper = Path(__file__).with_name("claim-run.sh")
    runner = ([r"C:\Program Files\Git\bin\bash.exe"]
              if os.name == "nt" else ["/bin/bash"])
    completed = subprocess.run(
        [*runner, str(claim_helper), "--verify-resume-receipt", token],
        cwd=str(repo), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=git_environment(), check=False)
    if (completed.returncode != 0
            or completed.stdout != (token + "\n").encode("utf-8")):
        raise RotationError("R0011 receipt v3 verification failed")


def load_governed_source_custody_v1() -> dict[str, object]:
    """Derive live source custody mechanically and accept no caller override."""
    repo, controller_id, controller_oid, claim_id, run_root, run_id = (
        _publication_custody_fields_v1())
    pointer_ref = f"refs/implementaudit/current-generations/{controller_id}"
    marker_ref = f"refs/implementaudit/current-generation-migrations/{controller_id}"
    pointer_oid = read_optional_exact_ref_oid_v1(repo, pointer_ref)
    marker_oid = read_optional_exact_ref_oid_v1(repo, marker_ref)
    if pointer_oid is None and marker_oid is None:
        live = load_governed_publication_context_v1()
        receipt_ref = str(live["receipt_ref"])
        receipt = _receipt_record_v1(
            repo, receipt_ref + "@" + str(live["receipt_oid"]))
        return {
            **live, "repo_path": repo, "run_root_path": run_root,
            "controller_oid": controller_oid, "pointer_ref": pointer_ref,
            "marker_ref": marker_ref, "pointer_oid": None, "marker_oid": None,
            "receipt": receipt,
        }
    pointer = (None if pointer_oid is None else
               load_canonical_generation_pointer_oid_v1(repo, pointer_oid))
    if pointer is None:
        raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
    source_epoch = str(pointer["source_epoch"])
    receipt_ref = f"refs/implementaudit/continuity-receipts/{controller_id}/{source_epoch}"
    receipt_oid = read_optional_exact_ref_oid_v1(repo, receipt_ref)
    receipt = (None if receipt_oid is None else
               _receipt_record_v1(repo, receipt_ref + "@" + receipt_oid))
    live = {
        "repo_path": repo, "run_root_path": run_root,
        "controller_id": controller_id, "controller_oid": controller_oid,
        "claim_id": claim_id, "run_id": run_id,
        "generation_id": pointer["generation_id"],
        "source_epoch": source_epoch,
        "pointer_ref": pointer_ref, "marker_ref": marker_ref,
        "pointer_oid": pointer_oid, "marker_oid": marker_oid,
        "receipt": receipt,
    }
    if marker_oid is not None:
        claim_helper = Path(__file__).with_name("claim-run.sh")
        runner = ([r"C:\Program Files\Git\bin\bash.exe"]
                  if os.name == "nt" else ["/bin/bash"])
        current = subprocess.run(
            [*runner, str(claim_helper), "--require-current-continuity", controller_id],
            cwd=str(repo), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=git_environment(), check=False)
        if (current.returncode != 0 or receipt is None
                or current.stdout.decode("utf-8", "strict").strip()
                != receipt_ref + "@" + receipt_oid):
            raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
    return live


def require_complete_pointer_receipt_marker_route_v1(
        *, live: dict[str, object], receipt: object,
        pointer: dict[str, object], pointer_oid: str, marker_oid: str) -> None:
    """Require the exact pointer -> receipt-v3 -> permanent-marker join."""
    verify_generation_pointer_v1(pointer)
    if (type(receipt) is not dict or set(receipt) != {"ref", "oid", "raw", "fields"}
            or not GIT_OID.fullmatch(pointer_oid) or not GIT_OID.fullmatch(marker_oid)):
        raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
    fields = receipt["fields"]
    if type(fields) is not list or len(fields) != 18:
        raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
    controller_id = str(live["controller_id"])
    claim_id = str(live["claim_id"])
    run_id = str(live["run_id"])
    source_epoch = str(live["source_epoch"])
    pointer_ref = str(live["pointer_ref"])
    if (fields[0:5] != ["implementaudit.continuity-receipt.v3", controller_id,
                         claim_id, run_id, source_epoch]
            or fields[6:8] != [pointer_ref, pointer_oid]
            or fields[8:16] != [
                pointer["pointer_digest"], pointer["hot_state_digest"],
                pointer["hot_roadmap_digest"], pointer["work_graph_path"],
                pointer["work_graph_digest"], pointer["generation_manifest_oid"],
                pointer["generation_manifest_digest"], pointer["cold_high_water"]]
            or receipt["ref"] != (
                f"refs/implementaudit/continuity-receipts/{controller_id}/{source_epoch}")):
        raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
    _require_immediate_predecessor_v1(
        Path(live["repo_path"]), fields, controller_id=controller_id,
        controller_oid=str(live["controller_oid"]), claim_id=claim_id,
        run_id=run_id, source_epoch=source_epoch)
    repo = Path(live["repo_path"])
    marker_raw = read_exact_git_blob_oid_v1(repo, marker_oid)
    try:
        marker_fields = marker_raw.decode("utf-8", "strict").split("\t")
    except UnicodeDecodeError as exc:
        raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE") from exc
    if b"\r" in marker_raw or b"\n" in marker_raw:
        raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
    if (len(marker_fields) != 10
            or marker_fields[:4] != [
                "implementaudit.current-generation-migration.v1", controller_id,
                claim_id, run_id]
            or not GENERATION_ID.fullmatch(marker_fields[4])
            or marker_fields[5:7] != [
                pointer_ref, "implementaudit.state-generation-pointer.v1"]
            or marker_fields[9] != "true"):
        raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
    genesis_epoch = marker_fields[4]
    genesis_receipt_ref = marker_fields[7]
    genesis_receipt_oid = marker_fields[8]
    if (genesis_receipt_ref != (
            f"refs/implementaudit/continuity-receipts/{controller_id}/{genesis_epoch}")
            or not GIT_OID.fullmatch(genesis_receipt_oid)):
        raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
    genesis_receipt = _receipt_record_v1(
        repo, genesis_receipt_ref + "@" + genesis_receipt_oid)
    genesis_fields = genesis_receipt["fields"]
    if (type(genesis_fields) is not list or len(genesis_fields) != 18
            or genesis_fields[:5] != [
                "implementaudit.continuity-receipt.v3", controller_id,
                claim_id, run_id, genesis_epoch]
            or genesis_fields[6] != pointer_ref
            or not GIT_OID.fullmatch(genesis_fields[7])):
        raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
    genesis_pointer_oid = genesis_fields[7]
    genesis_pointer = load_canonical_generation_pointer_oid_v1(
        repo, genesis_pointer_oid)
    if (tuple(genesis_pointer[name] for name in (
            "controller_id", "claim_id", "run_id", "source_epoch"))
            != (controller_id, claim_id, run_id, genesis_epoch)
            or genesis_pointer["generation_id"] != genesis_epoch
            or genesis_pointer["predecessor_pointer_oid"] is not None
            or genesis_pointer["predecessor_pointer_digest"] is not None
            or genesis_fields[8:16] != [
                genesis_pointer["pointer_digest"],
                genesis_pointer["hot_state_digest"],
                genesis_pointer["hot_roadmap_digest"],
                genesis_pointer["work_graph_path"],
                genesis_pointer["work_graph_digest"],
                genesis_pointer["generation_manifest_oid"],
                genesis_pointer["generation_manifest_digest"],
                genesis_pointer["cold_high_water"]]):
        raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
    _require_structural_predecessor_token_v1(
        genesis_fields[17], controller_id=controller_id,
        receipt_epoch=genesis_epoch)
    current_ordinal = int(source_epoch[1:], 16)
    genesis_ordinal = int(genesis_epoch[1:], 16)
    if current_ordinal < genesis_ordinal:
        raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
    if current_ordinal == genesis_ordinal:
        if (pointer_oid != genesis_pointer_oid
                or pointer["predecessor_pointer_oid"] is not None
                or pointer["predecessor_pointer_digest"] is not None):
            raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")
    else:
        predecessor_receipt = _receipt_record_v1(repo, fields[17])
        predecessor_fields = predecessor_receipt["fields"]
        if (not isinstance(predecessor_fields, list)
                or len(predecessor_fields) != 18
                or pointer["predecessor_pointer_oid"] != predecessor_fields[7]
                or pointer["predecessor_pointer_digest"] != predecessor_fields[8]):
            raise RotationError("OE_SOURCE_ROUTE_INCOMPLETE")


def r0039_publication_lease_path_v1(repo: Path) -> Path:
    """Resolve the one absolute Git-common lease shared by linked worktrees."""
    common = Path(git(
        repo, "rev-parse", "--path-format=absolute", "--git-common-dir"
    ).decode("utf-8", "strict").strip()).resolve()
    try:
        common_stat = os.lstat(common)
    except OSError as exc:
        raise RotationError("R0039 publication writer lease custody is unavailable") from exc
    if (not common.is_absolute() or not stat.S_ISDIR(common_stat.st_mode)
            or stat.S_ISLNK(common_stat.st_mode)
            or bool(getattr(common_stat, "st_file_attributes", 0) & 0x400)):
        raise RotationError("R0039 publication writer lease custody is unavailable")
    return common / "implementaudit-r0039-publication.lock"


def _r0039_legacy_worktree_lease_path_v1(repo: Path) -> Path:
    return Path(git(
        repo, "rev-parse", "--path-format=absolute", "--git-path",
        "implementaudit-r0039-publication.lock"
    ).decode("utf-8", "strict").strip()).resolve()


@contextlib.contextmanager
def _acquire_r0039_publication_file_lease_v1(repo: Path):
    """Own the Git-common create-exclusive lease, failing closed on skew."""
    gate = r0039_publication_lease_path_v1(repo)
    legacy_gate = _r0039_legacy_worktree_lease_path_v1(repo)
    try:
        descriptor = os.open(gate, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
    except FileExistsError as exc:
        raise RotationError("R0039 publication writer lease is held") from exc
    opened = os.fstat(descriptor)
    try:
        current = os.lstat(gate)
        if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or not stat.S_ISREG(current.st_mode) or current.st_nlink != 1
                or (current.st_dev, current.st_ino) != (opened.st_dev, opened.st_ino)):
            raise RotationError("R0039 publication writer lease custody changed")
        if legacy_gate != gate and os.path.lexists(legacy_gate):
            raise RotationError("R0039 publication writer lease version skew")
        yield gate
    finally:
        os.close(descriptor)
        try:
            current = os.lstat(gate)
        except FileNotFoundError:
            current = None
        if current is not None:
            if (not stat.S_ISREG(current.st_mode) or current.st_nlink != 1
                    or (current.st_dev, current.st_ino) !=
                    (opened.st_dev, opened.st_ino)):
                raise RotationError("R0039 publication writer lease custody changed")
            os.unlink(gate)


@contextlib.contextmanager
def acquire_r0039_publication_writer_lease_v1():
    """Serialize cooperating publishers; caller supplies no route or authority."""
    discovery_repo = publication_owner_repo_v1()
    with _acquire_r0039_publication_file_lease_v1(discovery_repo):
        context, session = _open_governed_publication_context_v1()
        if Path(context["repo_path"]) != discovery_repo:
            session.__exit__()
            raise RotationError("publication custody owner changed under lease")
        try:
            yield context, session
        finally:
            session.__exit__()


def _read_live_genesis_event_population_v1(
        repo: Path, *, run_id: str, generation_id: str) -> dict[str, str]:
    if (not isinstance(repo, Path) or type(run_id) is not str
            or not TOKEN_ID.fullmatch(run_id) or type(generation_id) is not str
            or not GENERATION_ID.fullmatch(generation_id)):
        raise RotationError("live-genesis event population identity is invalid")
    prefix = f"{EVENT_SEGMENT_PREFIX}/{run_id}/{generation_id}/"
    lines = git(
        repo, "for-each-ref", "--format=%(refname)%09%(objectname)", prefix
    ).decode("utf-8", "strict").splitlines()
    observed: dict[str, str] = {}
    for line in lines:
        fields = line.split("\t")
        if (len(fields) != 2 or not fields[0].startswith(prefix)
                or not GIT_OID.fullmatch(fields[1]) or fields[0] in observed):
            raise RotationError("live-genesis event population is malformed")
        observed[fields[0]] = fields[1]
    return dict(sorted(observed.items()))


def _require_live_genesis_guards_v1(
        repo: Path, guards: tuple[tuple[str, str], ...]) -> None:
    if tuple(sorted(guards)) != guards:
        raise RotationError("live-genesis event guard ordering is invalid")
    for ref, expected_oid in guards:
        if (not ref.startswith("refs/implementaudit/")
                or not GIT_OID.fullmatch(expected_oid)):
            raise RotationError("live-genesis event guard identity is invalid")
        state, observed_oid = read_exact_ref_state_v1(repo, ref)
        if ((expected_oid == ZERO_OID and state != "ABSENT")
                or (expected_oid != ZERO_OID
                    and (state != "RESOLVED" or observed_oid != expected_oid))):
            raise RotationError("live-genesis event custody is stale")


def _live_genesis_event_transaction_v1(
        *, repo: Path, event_population: Mapping[str, str],
        guards: tuple[tuple[str, str], ...]
        ) -> tuple[list[str], dict[str, str], bytes]:
    if (not isinstance(repo, Path) or type(event_population) is not dict
            or not event_population or dict(sorted(event_population.items())) != event_population
            or tuple(sorted(guards)) != guards):
        raise RotationError("live-genesis event transaction is invalid")
    rows = [b"start\0"]
    for ref, oid in guards:
        if (not ref.startswith("refs/implementaudit/")
                or not GIT_OID.fullmatch(oid)):
            raise RotationError("live-genesis event guard identity is invalid")
        rows.append(b"verify " + ref.encode("ascii") + b"\0"
                    + oid.encode("ascii") + b"\0")
    for ref, oid in event_population.items():
        if (not ref.startswith(EVENT_SEGMENT_PREFIX + "/")
                or not GIT_OID.fullmatch(oid)):
            raise RotationError("live-genesis event transaction is invalid")
        rows.append(b"update " + ref.encode("ascii") + b"\0"
                    + oid.encode("ascii") + b"\0"
                    + ZERO_OID.encode("ascii") + b"\0")
    rows.extend((b"prepare\0", b"commit\0"))
    executable = git_executable_v1()
    environment = {
        "PATH": os.path.dirname(executable), "LC_ALL": "C", "LANG": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": PLATFORM_NULL_SINK_V1,
        "GIT_TERMINAL_PROMPT": "0",
    }
    return ([executable, "-c", f"core.hooksPath={PLATFORM_NULL_SINK_V1}",
             "update-ref", "--stdin", "-z"], environment, b"".join(rows))


def prepare_live_genesis_v1() -> dict[str, object]:
    """Prepare one fully equivalent genesis candidate from governed custody."""
    with acquire_r0039_publication_writer_lease_v1() as (context, session):
        required = {
            "repo_path", "run_root_path", "controller_id", "claim_id", "run_id",
            "generation_id", "source_epoch", "receipt_ref", "receipt_oid",
            "predecessor_receipt_token", "receipt_state_digest",
            "receipt_roadmap_digest", "expected_old_pointer_oid",
            "migration_marker_oid", "publication_custody_tuple",
            "publication_guard_refs",
        }
        if (type(context) is not dict or not required.issubset(context)
                or context["expected_old_pointer_oid"] is not None
                or context["migration_marker_oid"] is not None
                or context["predecessor_receipt_token"]
                != str(context["receipt_ref"]) + "@" + str(context["receipt_oid"])):
            raise RotationError("live-genesis requires a fresh invalidated successor")
        repo = Path(context["repo_path"])
        run_root = Path(context["run_root_path"])
        controller_id = str(context["controller_id"])
        claim_id = str(context["claim_id"])
        run_id = str(context["run_id"])
        generation_id = str(context["generation_id"])
        source_epoch = str(context["source_epoch"])
        if (not CONTROLLER_ID.fullmatch(controller_id)
                or not CLAIM_ID.fullmatch(claim_id) or not TOKEN_ID.fullmatch(run_id)
                or not GENERATION_ID.fullmatch(generation_id)
                or source_epoch != generation_id
                or not same_path(run_root, repo / ".IMPLEMENTAUDIT" / "runs" / run_id)):
            raise RotationError("live-genesis custody identity is invalid")

        initial_hot = {
            role: session.read_role_exact(role, reopen=False)
            for role in ("STATE", "ROADMAP", "WORK_GRAPH")
        }
        hot_digests = {
            role: hashlib.sha256(raw).hexdigest()
            for role, raw in initial_hot.items()
        }
        if (hot_digests["STATE"] != context["receipt_state_digest"]
                or hot_digests["ROADMAP"] != context["receipt_roadmap_digest"]):
            raise RotationError("live-genesis hot custody disagrees")

        archive_prefix = f"{ARCHIVE_PREFIX}/{controller_id}/"
        archive_refs = [line for line in git(
            repo, "for-each-ref", "--format=%(refname)", archive_prefix
        ).decode("utf-8", "strict").splitlines() if line]
        if len(archive_refs) != 1:
            raise RotationError("live-genesis archive custody is invalid")
        archive_ref = archive_refs[0]
        archive_oid = read_optional_exact_ref_oid_v1(repo, archive_ref)
        if archive_oid is None:
            raise RotationError("live-genesis archive custody is invalid")
        exact_archive_ref, _archive, archive_sources = (
            _load_live_genesis_archive_sources_v1(
                repo, controller_id=controller_id, archive_oid=archive_oid))
        if exact_archive_ref != archive_ref:
            raise RotationError("live-genesis archive custody is invalid")
        classification_ref, classification_oid, classification, _classification_raw = (
            load_live_genesis_classification_oid_v1(
                repo, controller_id=controller_id, archive_oid=archive_oid))
        records = enumerate_legacy_history_v1(
            archive_sources["STATE.md"], archive_sources["ROADMAP.md"],
            classification)
        owner_manifest = load_exact_r0039_f2_archive_manifest_v1(
            repo=repo, run_root=run_root, controller_id=controller_id,
            claim_id=claim_id, run_id=run_id, source_epoch=source_epoch)
        source_context = {**context, "owner_manifest": owner_manifest}
        source_evidence_id = "iasrc-v1-r0039-archive-task5-migration"
        sequences = allocate_candidate_sequences_v1(
            "00000000000000000000", len(records))
        events: list[dict[str, object]] = []
        segment_bytes: list[bytes] = []
        for record, sequence in zip(records, sequences, strict=True):
            request = {
                "schema_version": "implementaudit.history-event.v1",
                "run_id": run_id, "controller_id": controller_id,
                "generation_id": generation_id, "sequence": sequence,
                "record_kind": record.record_kind,
                "subject_id": record.stable_id, "source_epoch": source_epoch,
                "transition": "MIGRATED",
                "status": ("SATISFIED" if record.record_kind
                           == "instruction.satisfied" else "CLOSED"),
                "supersedes_event_id": None,
                "payload": {
                    "legacy_record_id": record.stable_id,
                    "legacy_source_digest": record.source_digest,
                },
            }
            event, raw = _build_event_segment_in_context_v1(
                request, source_evidence_id=source_evidence_id,
                context=source_context)
            events.append(event)
            segment_bytes.append(raw)
        manifest, manifest_raw = build_generation_manifest_v1(None, events)
        pure_receipt = verify_migration_population_v1(
            records, segment_bytes, manifest)

        event_population: dict[str, str] = {}
        for event, raw in zip(events, segment_bytes, strict=True):
            oid = git(repo, "hash-object", "-w", "--stdin",
                      input_bytes=raw).decode("ascii", "strict").strip()
            ref = _segment_ref_v1(
                run_id, generation_id, str(event["sequence"]),
                str(event["event_id"]))
            if ref in event_population:
                raise RotationError("live-genesis event population is not unique")
            event_population[ref] = oid
        event_population = dict(sorted(event_population.items()))

        guard_map: dict[str, str] = {}
        raw_guards = context["publication_guard_refs"]
        if type(raw_guards) is not tuple:
            raise RotationError("live-genesis event guards are invalid")
        additions = (
            *raw_guards,
            (archive_ref, archive_oid),
            (classification_ref, classification_oid),
            (f"refs/implementaudit/current-generations/{controller_id}", ZERO_OID),
            (f"refs/implementaudit/current-generation-migrations/{controller_id}",
             ZERO_OID),
        )
        for row in additions:
            if (type(row) is not tuple or len(row) != 2
                    or row[0] in guard_map and guard_map[row[0]] != row[1]):
                raise RotationError("live-genesis event guards are invalid")
            guard_map[str(row[0])] = str(row[1])
        guards = tuple(sorted(guard_map.items()))
        _require_live_genesis_guards_v1(repo, guards)
        observed = _read_live_genesis_event_population_v1(
            repo, run_id=run_id, generation_id=generation_id)
        if observed and observed != event_population:
            raise RotationError("live-genesis event population is partial or foreign")
        if not observed:
            argv, environment, stdin_bytes = _live_genesis_event_transaction_v1(
                repo=repo, event_population=event_population, guards=guards)
            _require_publication_custody_recheck_v1(
                context["publication_custody_tuple"])
            completed = subprocess.run(
                argv, cwd=str(repo), env=environment, input=stdin_bytes,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            observed = _read_live_genesis_event_population_v1(
                repo, run_id=run_id, generation_id=generation_id)
            if completed.returncode != 0:
                if observed != event_population:
                    raise RotationError("live-genesis event publication failed")
                _require_live_genesis_guards_v1(repo, guards)
        if observed != event_population:
            raise RotationError("live-genesis event population readback disagrees")
        _require_live_genesis_guards_v1(repo, guards)
        stored_receipt = verify_migration_equivalence_v1(
            records, segment_bytes, manifest, repo)
        if stored_receipt != pure_receipt:
            raise RotationError("live-genesis stored equivalence disagrees")

        final_hot = {
            role: session.read_role_exact(role, reopen=True)
            for role in ("STATE", "ROADMAP", "WORK_GRAPH")
        }
        if final_hot != initial_hot:
            raise RotationError("live-genesis hot custody changed")
        manifest_oid = git(
            repo, "hash-object", "-w", "--stdin",
            input_bytes=manifest_raw).decode("ascii", "strict").strip()
        loaded_manifest = load_canonical_generation_manifest_oid_v1(
            repo, manifest_oid)
        pointer, pointer_raw = build_generation_pointer_v1(
            controller_id=controller_id, claim_id=claim_id, run_id=run_id,
            generation_id=generation_id, source_epoch=source_epoch,
            predecessor_pointer_oid=None, predecessor_pointer_digest=None,
            generation_manifest_oid=manifest_oid,
            generation_manifest_digest=str(manifest["manifest_digest"]),
            cold_high_water=str(manifest["high_water"]),
            hot_state_digest=hot_digests["STATE"],
            hot_roadmap_digest=hot_digests["ROADMAP"],
            work_graph_path=EXPECTED_WORK_GRAPH_PATH,
            work_graph_digest=hot_digests["WORK_GRAPH"],
            degraded_state="NONE")
        pointer_oid = git(
            repo, "hash-object", "-w", "--stdin",
            input_bytes=pointer_raw).decode("ascii", "strict").strip()
        loaded_pointer = load_canonical_generation_pointer_oid_v1(
            repo, pointer_oid)
        verify_pointer_manifest_tuple_v1(
            pointer=loaded_pointer, manifest=loaded_manifest,
            manifest_oid=manifest_oid)
        verify_generation_successor_tuple_v1(
            pointer=loaded_pointer, manifest=loaded_manifest,
            predecessor_oid=None, predecessor_pointer=None,
            predecessor_manifest=None)
        return {
            "schema": "implementaudit.live-genesis-preparation.v1",
            "controller_id": controller_id,
            "claim_id": claim_id,
            "run_id": run_id,
            "source_epoch": source_epoch,
            "archive_ref": archive_ref,
            "archive_oid": archive_oid,
            "classification_ref": classification_ref,
            "classification_oid": classification_oid,
            "event_count": stored_receipt.event_count,
            "event_population_digest": stored_receipt.population_digest,
            "generation_manifest_oid": manifest_oid,
            "generation_manifest_digest": str(manifest["manifest_digest"]),
            "candidate_pointer_oid": pointer_oid,
            "authority_ceiling": "R0039_CANDIDATE_ONLY",
        }


def prepare_live_successor_v1() -> dict[str, object]:
    """Prepare a continuity-only successor from exact governed custody."""
    with acquire_r0039_publication_writer_lease_v1() as (context, session):
        predecessor_oid = context.get("expected_old_pointer_oid")
        marker_oid = context.get("migration_marker_oid")
        predecessor_receipt = context.get("predecessor_receipt_token")
        if (type(predecessor_oid) is not str or not GIT_OID.fullmatch(predecessor_oid)
                or type(marker_oid) is not str or not GIT_OID.fullmatch(marker_oid)
                or type(predecessor_receipt) is not str
                or predecessor_receipt != (
                    str(context.get("receipt_ref")) + "@" +
                    str(context.get("receipt_oid")))):
            raise RotationError("live-successor requires an invalidated post-marker predecessor")
        repo = Path(context["repo_path"])
        controller_id = str(context["controller_id"])
        claim_id = str(context["claim_id"])
        run_id = str(context["run_id"])
        generation_id = str(context["generation_id"])
        source_epoch = str(context["source_epoch"])
        predecessor_pointer = load_canonical_generation_pointer_oid_v1(
            repo, predecessor_oid)
        predecessor_manifest = load_canonical_generation_manifest_oid_v1(
            repo, str(predecessor_pointer["generation_manifest_oid"]))
        previous_epoch = str(predecessor_pointer["source_epoch"])
        if (source_epoch != generation_id
                or not GENERATION_ID.fullmatch(generation_id)
                or int(generation_id[1:], 16) != int(previous_epoch[1:], 16) + 1
                or tuple(predecessor_pointer[name] for name in (
                    "controller_id", "claim_id", "run_id"))
                != (controller_id, claim_id, run_id)):
            raise RotationError("live-successor generation is not the exact next epoch")

        initial_hot = {
            role: session.read_role_exact(role, reopen=False)
            for role in ("STATE", "ROADMAP", "WORK_GRAPH")
        }
        hot_digests = {
            role: hashlib.sha256(raw).hexdigest()
            for role, raw in initial_hot.items()
        }
        if (hot_digests["STATE"] != context["receipt_state_digest"]
                or hot_digests["ROADMAP"] != context["receipt_roadmap_digest"]):
            raise RotationError("live-successor hot custody disagrees")

        manifest, manifest_raw = build_generation_manifest_v1(
            predecessor_manifest, [])
        if (manifest["events"] or manifest["high_water"]
                != predecessor_manifest["high_water"]):
            raise RotationError("live-successor changed cold history without evidence")
        manifest_oid = git(
            repo, "hash-object", "-w", "--stdin",
            input_bytes=manifest_raw).decode("ascii", "strict").strip()
        loaded_manifest = load_canonical_generation_manifest_oid_v1(
            repo, manifest_oid)
        pointer, pointer_raw = build_generation_pointer_v1(
            controller_id=controller_id, claim_id=claim_id, run_id=run_id,
            generation_id=generation_id, source_epoch=source_epoch,
            predecessor_pointer_oid=predecessor_oid,
            predecessor_pointer_digest=str(predecessor_pointer["pointer_digest"]),
            generation_manifest_oid=manifest_oid,
            generation_manifest_digest=str(manifest["manifest_digest"]),
            cold_high_water=str(manifest["high_water"]),
            hot_state_digest=hot_digests["STATE"],
            hot_roadmap_digest=hot_digests["ROADMAP"],
            work_graph_path=EXPECTED_WORK_GRAPH_PATH,
            work_graph_digest=hot_digests["WORK_GRAPH"],
            degraded_state=str(predecessor_pointer["degraded_state"]))
        pointer_oid = git(
            repo, "hash-object", "-w", "--stdin",
            input_bytes=pointer_raw).decode("ascii", "strict").strip()
        loaded_pointer = load_canonical_generation_pointer_oid_v1(
            repo, pointer_oid)
        verify_pointer_manifest_tuple_v1(
            pointer=loaded_pointer, manifest=loaded_manifest,
            manifest_oid=manifest_oid)
        verify_generation_successor_tuple_v1(
            pointer=loaded_pointer, manifest=loaded_manifest,
            predecessor_oid=predecessor_oid,
            predecessor_pointer=predecessor_pointer,
            predecessor_manifest=predecessor_manifest)
        final_hot = {
            role: session.read_role_exact(role, reopen=True)
            for role in ("STATE", "ROADMAP", "WORK_GRAPH")
        }
        if final_hot != initial_hot:
            raise RotationError("live-successor hot custody changed")
        return {
            "schema": "implementaudit.live-successor-preparation.v1",
            "controller_id": controller_id,
            "claim_id": claim_id,
            "run_id": run_id,
            "source_epoch": source_epoch,
            "predecessor_pointer_oid": predecessor_oid,
            "permanent_marker_oid": marker_oid,
            "event_count": 0,
            "generation_manifest_oid": manifest_oid,
            "generation_manifest_digest": str(manifest["manifest_digest"]),
            "candidate_pointer_oid": pointer_oid,
            "authority_ceiling": "R0039_CANDIDATE_ONLY",
        }


def prepare_trusted_update_ref_transaction_v1(*, repo: Path, ref: str, new_oid: str,
                                              old_oid: str,
                                              verify_refs: tuple[tuple[str, str], ...]) -> dict[str, object]:
    if (not ref.startswith(("refs/implementaudit/current-generations/",
                            "refs/implementaudit/current-generation-migrations/"))
            or not GIT_OID.fullmatch(new_oid) or not GIT_OID.fullmatch(old_oid)):
        raise RotationError("publication CAS identity is invalid")
    if tuple(sorted(verify_refs)) != verify_refs:
        raise RotationError("publication guard ordering is invalid")
    rows = [b"start\0"]
    for guard_ref, guard_oid in verify_refs:
        if (not guard_ref.startswith("refs/implementaudit/")
                or not GIT_OID.fullmatch(guard_oid)):
            raise RotationError("publication guard identity is invalid")
        rows.append(b"verify " + guard_ref.encode("ascii") + b"\0" + guard_oid.encode("ascii") + b"\0")
    rows.append(b"update " + ref.encode("ascii") + b"\0" + new_oid.encode("ascii")
                + b"\0" + old_oid.encode("ascii") + b"\0prepare\0commit\0")
    executable = git_executable_v1()
    environment = {"PATH": os.path.dirname(executable), "LC_ALL": "C", "LANG": "C",
                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": PLATFORM_NULL_SINK_V1,
                   "GIT_TERMINAL_PROMPT": "0"}
    return {"argv": [executable, "-c", f"core.hooksPath={PLATFORM_NULL_SINK_V1}",
                     "update-ref", "--stdin", "-z"],
            "cwd": str(repo), "env": environment, "stdin_bytes": b"".join(rows), "ref": ref}


def read_back_published_ref_v1(cas: dict[str, object]) -> str:
    verify_trusted_update_ref_transaction_v1(cas)
    completed = subprocess.run([str(cas["argv"][0]), "-C", str(cas["cwd"]), "rev-parse", "--verify", str(cas["ref"])],
                               env=dict(cas["env"]), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0:
        raise RotationError("publication readback has unknown effect")
    try:
        oid = completed.stdout.decode("utf-8", "strict").strip()
    except UnicodeDecodeError as exc:
        raise RotationError("publication readback has unknown effect") from exc
    if not GIT_OID.fullmatch(oid):
        raise RotationError("publication readback has unknown effect")
    return oid


def verify_trusted_update_ref_transaction_v1(cas: dict[str, object]) -> None:
    executable = git_executable_v1()
    expected_environment = {
        "PATH": os.path.dirname(executable), "LC_ALL": "C", "LANG": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": PLATFORM_NULL_SINK_V1,
        "GIT_TERMINAL_PROMPT": "0",
    }
    expected_prefix = [executable, "-c", f"core.hooksPath={PLATFORM_NULL_SINK_V1}",
                       "update-ref", "--stdin", "-z"]
    if (set(cas) != {"argv", "cwd", "env", "stdin_bytes", "ref"}
            or cas["argv"] != expected_prefix or cas["env"] != expected_environment
            or type(cas["cwd"]) is not str or type(cas["stdin_bytes"]) is not bytes
            or type(cas["ref"]) is not str):
        raise RotationError("trusted Git transaction changed")


def quarantine_unreferenced_cas_loser_v1(repo: Path, candidate_oid: str) -> str:
    """Classify only an unreferenced loser; this bounded cell never deletes objects."""
    if type(candidate_oid) is not str or not GIT_OID.fullmatch(candidate_oid):
        raise RotationError("CAS loser identity is invalid")
    refs = git(repo, "for-each-ref", "--format=%(refname)", "--points-at", candidate_oid).decode().splitlines()
    if refs:
        raise RotationError("CAS loser is referenced; effect is unknown")
    return "UNREFERENCED_LOSER_QUARANTINED"


def _freeze_git_blob_v1(repo: Path, role: str, oid: str) -> tuple[str, str, str, int, str]:
    if type(oid) is not str or not GIT_OID.fullmatch(oid):
        raise RotationError("immutable input OID is invalid")
    object_type = git(repo, "cat-file", "-t", oid).decode("ascii", "strict").strip()
    if object_type != "blob":
        raise RotationError("immutable input object is not a blob")
    raw = read_exact_git_blob_oid_v1(repo, oid)
    return role, object_type, oid, hashlib.sha256(raw).hexdigest(), len(raw)


def _segment_ref_v1(run_id: str, generation_id: str, sequence: str, event_id: str) -> str:
    return f"{EVENT_SEGMENT_PREFIX}/{run_id}/{generation_id}/{sequence}/{event_id}"


def _freeze_manifest_segments_v1(repo: Path, role_prefix: str,
                                 manifest: dict[str, object]) -> list[tuple[str, str, str, int, str]]:
    rows = []
    for row in manifest["events"]:
        ref = _segment_ref_v1(str(manifest["run_id"]), str(manifest["generation_id"]),
                              str(row["sequence"]), str(row["event_id"]))
        oid = read_optional_exact_ref_oid_v1(repo, ref)
        if oid is None:
            raise RotationError("immutable event segment is unavailable")
        rows.append(_freeze_git_blob_v1(repo, f"{role_prefix}-segment:{row['sequence']}", oid))
    return rows


def freeze_immutable_publication_inputs_v1(*, repo: Path, candidate_pointer: dict[str, object],
                                           candidate_manifest: dict[str, object],
                                           expected_old_pointer_oid: str | None,
                                           candidate_pointer_oid: str) -> tuple[tuple[object, ...], ...]:
    if (canonical_json_v1(candidate_pointer) != read_exact_git_blob_oid_v1(repo, candidate_pointer_oid)
            or canonical_json_v1(candidate_manifest) != read_exact_git_blob_oid_v1(
                repo, str(candidate_pointer["generation_manifest_oid"]))):
        raise RotationError("candidate immutable object identity disagrees")
    rows: list[tuple[object, ...]] = [
        _freeze_git_blob_v1(repo, "candidate-pointer", candidate_pointer_oid),
        _freeze_git_blob_v1(repo, "candidate-manifest", str(candidate_pointer["generation_manifest_oid"])),
        *_freeze_manifest_segments_v1(repo, "candidate", candidate_manifest),
    ]
    if expected_old_pointer_oid is not None:
        rows.append(_freeze_git_blob_v1(repo, "predecessor-pointer", expected_old_pointer_oid))
        predecessor = load_canonical_generation_pointer_oid_v1(repo, expected_old_pointer_oid)
        predecessor_manifest = load_canonical_generation_manifest_oid_v1(
            repo, str(predecessor["generation_manifest_oid"]))
        rows.append(_freeze_git_blob_v1(repo, "predecessor-manifest",
                                        str(predecessor["generation_manifest_oid"])))
        rows.extend(_freeze_manifest_segments_v1(repo, "predecessor", predecessor_manifest))
    return tuple(sorted(rows))


def verify_frozen_immutable_publication_inputs_v1(*, repo: Path, frozen: tuple[tuple[object, ...], ...],
                                                  candidate_pointer: dict[str, object],
                                                  candidate_manifest: dict[str, object],
                                                  expected_old_pointer_oid: str | None,
                                                  candidate_pointer_oid: str) -> None:
    observed = freeze_immutable_publication_inputs_v1(
        repo=repo, candidate_pointer=candidate_pointer, candidate_manifest=candidate_manifest,
        expected_old_pointer_oid=expected_old_pointer_oid, candidate_pointer_oid=candidate_pointer_oid)
    if observed != frozen:
        raise RotationError("immutable publication input changed")


class _RetainedPublicationFileV1:
    def __init__(self, path: Path):
        self.handle: int | None = None
        self.descriptor: int | None = None
        if os.name == "nt":
            self.handle = _windows_open_regular_no_reparse_v1(path)
            self.initial = _windows_snapshot_v1(self.handle)
        else:
            if not hasattr(os, "O_NOFOLLOW"):
                raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
            flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_BINARY", 0)
            try:
                self.descriptor = os.open(path, flags)
                opened = os.fstat(self.descriptor)
            except OSError as exc:
                raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED") from exc
            if not stat.S_ISREG(opened.st_mode):
                self.close()
                raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
            self.initial = _NativeFileSnapshotV1(
                os.path.normcase(os.path.abspath(path)),
                (opened.st_dev, opened.st_ino), opened.st_size,
                opened.st_ctime_ns, opened.st_mtime_ns)

    def close(self) -> None:
        if self.handle is not None:
            handle, self.handle = self.handle, None
            _windows_close_handle_v1(handle)
        if self.descriptor is not None:
            descriptor, self.descriptor = self.descriptor, None
            os.close(descriptor)

    def read_exact(self) -> bytes:
        if self.handle is not None:
            return _windows_read_handle_bytes_v1(self.handle)
        if self.descriptor is None:
            raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
        return _read_posix_descriptor_bytes_v1(self.descriptor)

    def current_snapshot(self) -> _NativeFileSnapshotV1:
        if self.handle is not None:
            return _windows_snapshot_v1(self.handle)
        if self.descriptor is None:
            raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
        current = os.fstat(self.descriptor)
        return _NativeFileSnapshotV1(
            self.initial.canonical_path, (current.st_dev, current.st_ino),
            current.st_size, current.st_ctime_ns, current.st_mtime_ns)

    def reopened_snapshot(self) -> _NativeFileSnapshotV1:
        path = Path(self.initial.canonical_path)
        if os.name == "nt":
            reopened = _windows_open_regular_no_reparse_v1(path)
            try:
                return _windows_snapshot_v1(reopened)
            finally:
                _windows_close_handle_v1(reopened)
        if not hasattr(os, "O_NOFOLLOW"):
            raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
        try:
            descriptor = os.open(
                path, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_BINARY", 0))
            current = os.fstat(descriptor)
        except OSError as exc:
            raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED") from exc
        finally:
            if "descriptor" in locals():
                os.close(descriptor)
        if not stat.S_ISREG(current.st_mode):
            raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
        return _NativeFileSnapshotV1(
            self.initial.canonical_path, (current.st_dev, current.st_ino),
            current.st_size, current.st_ctime_ns, current.st_mtime_ns)


class PublicationObservationSessionV1:
    def __init__(self, context: dict[str, object], expected_digests: dict[str, str] | None):
        self.root = Path(context["run_root_path"])
        self.expected = expected_digests
        self.opened: list[tuple[str, _RetainedPublicationFileV1]] = []

    def __enter__(self):
        try:
            for role, relative in (("STATE", "STATE.md"), ("ROADMAP", "ROADMAP.md"),
                                   ("WORK_GRAPH", EXPECTED_WORK_GRAPH_PATH)):
                self.opened.append((role, _RetainedPublicationFileV1(self.root / relative)))
        except BaseException:
            self.__exit__()
            raise
        return self

    def __exit__(self, *_):
        for _, retained in reversed(self.opened):
            retained.close()
        self.opened.clear()

    def read_role_exact(self, role: str, *, reopen: bool) -> bytes:
        retained = next((item for name, item in self.opened if name == role), None)
        if retained is None:
            raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
        data = retained.read_exact()
        current = retained.current_snapshot()
        if current != retained.initial or len(data) != retained.initial.size:
            raise RotationError("publication input changed during observation")
        if reopen and retained.reopened_snapshot() != retained.initial:
            raise RotationError("publication input changed during observation")
        return data

    def bind_expected_digests(self, expected_digests: dict[str, str]) -> None:
        if (set(expected_digests) != {"STATE", "ROADMAP", "WORK_GRAPH"}
                or any(type(value) is not str or not HEX_SHA256.fullmatch(value)
                       for value in expected_digests.values())):
            raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
        self.expected = dict(expected_digests)

    def observe(self, *, reopen: bool) -> tuple[PublicationObservationV1, ...]:
        rows: list[PublicationObservationV1] = []
        for role, retained in self.opened:
            data = self.read_role_exact(role, reopen=reopen)
            digest = hashlib.sha256(data).hexdigest()
            expected = digest if self.expected is None else self.expected.get(role)
            if type(expected) is not str or not HEX_SHA256.fullmatch(expected):
                raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
            if expected != digest:
                raise RotationError("publication input digest disagrees with candidate pointer")
            rows.append(PublicationObservationV1(
                role, retained.initial.canonical_path, retained.initial.file_identity,
                retained.initial.size, retained.initial.ctime_ns,
                retained.initial.mtime_ns, digest, expected))
        return tuple(sorted(rows, key=lambda row: row.canonical_no_follow_path))


def observe_publication_vector_v1(*, context: dict[str, object],
                                  expected_digests: dict[str, str] | None = None
                                  ) -> tuple[PublicationObservationV1, ...]:
    with PublicationObservationSessionV1(context, expected_digests) as session:
        return session.observe(reopen=True)


def publish_generation_pointer_v1(*, candidate_pointer_oid: str,
                                  additional_guard_refs: tuple[tuple[str, str], ...] = ()) -> str:
    if type(candidate_pointer_oid) is not str or not GIT_OID.fullmatch(candidate_pointer_oid):
        raise RotationError("candidate pointer identity is invalid")
    with acquire_r0039_publication_writer_lease_v1() as (context, session):
        repo = Path(context["repo_path"])
        pointer = load_canonical_generation_pointer_oid_v1(repo, candidate_pointer_oid)
        expected = (context["controller_id"], context["claim_id"], context["run_id"],
                    context["generation_id"], context["source_epoch"])
        if tuple(pointer[key] for key in ("controller_id", "claim_id", "run_id", "generation_id", "source_epoch")) != expected:
            raise RotationError("generation pointer authority disagrees with live custody")
        manifest = load_canonical_generation_manifest_oid_v1(repo, str(pointer["generation_manifest_oid"]))
        if tuple(manifest[key] for key in ("controller_id", "claim_id", "run_id", "generation_id", "source_epoch")) != expected:
            raise RotationError("generation manifest authority disagrees with live custody")
        verify_pointer_manifest_tuple_v1(
            pointer=pointer, manifest=manifest, manifest_oid=str(pointer["generation_manifest_oid"]))
        predecessor_oid = context["expected_old_pointer_oid"]
        previous = (None if predecessor_oid is None else
                    load_canonical_generation_pointer_oid_v1(repo, str(predecessor_oid)))
        predecessor_manifest = (None if previous is None else
                                load_canonical_generation_manifest_oid_v1(
                                    repo, str(previous["generation_manifest_oid"])))
        verify_manifest_segments_core_v1(repo, manifest)
        if predecessor_manifest is not None:
            verify_manifest_segments_core_v1(repo, predecessor_manifest)
        verify_generation_successor_tuple_v1(
            pointer=pointer, manifest=manifest, predecessor_oid=predecessor_oid,
            predecessor_pointer=previous, predecessor_manifest=predecessor_manifest)
        frozen = freeze_immutable_publication_inputs_v1(
            repo=repo, candidate_pointer=pointer, candidate_manifest=manifest,
            expected_old_pointer_oid=context["expected_old_pointer_oid"],
            candidate_pointer_oid=candidate_pointer_oid)
        verify_frozen_immutable_publication_inputs_v1(
            repo=repo, frozen=frozen, candidate_pointer=pointer, candidate_manifest=manifest,
            expected_old_pointer_oid=context["expected_old_pointer_oid"],
            candidate_pointer_oid=candidate_pointer_oid)
        if (pointer["hot_state_digest"] != context["receipt_state_digest"]
                or pointer["hot_roadmap_digest"] != context["receipt_roadmap_digest"]):
            raise RotationError(
                "candidate hot-state digests disagree with receipt-bound custody")
        expected_digests = {"STATE": str(context["receipt_state_digest"]),
                            "ROADMAP": str(context["receipt_roadmap_digest"]),
                            "WORK_GRAPH": str(pointer["work_graph_digest"])}
        session.bind_expected_digests(expected_digests)
        ref = f"refs/implementaudit/current-generations/{context['controller_id']}"
        # Extra guards can only constrain publication, never replace owner guards.
        guards = dict(context["publication_guard_refs"])
        if type(additional_guard_refs) is not tuple:
            raise RotationError("additional publication guards are malformed")
        for guard_ref, guard_oid in additional_guard_refs:
            if guard_ref in guards and guards[guard_ref] != guard_oid:
                raise RotationError("additional publication guard conflicts with owner custody")
            guards[guard_ref] = guard_oid
        cas = prepare_trusted_update_ref_transaction_v1(
            repo=repo, ref=ref, new_oid=candidate_pointer_oid,
            old_oid=context["expected_old_pointer_oid"] or ZERO_OID,
            verify_refs=tuple(sorted(guards.items())))
        first = session.observe(reopen=False)
        second = session.observe(reopen=True)
        # Revalidate the fixed executable identity and isolated Git inputs
        # immediately before the final equality decision.  Once equality
        # completes, the one prebuilt update-ref process is the only call.
        verify_trusted_update_ref_transaction_v1(cas)
        if first != second or not frozen:
            raise RotationError("publication input changed during the final fence")
        _require_publication_custody_recheck_v1(
            context["publication_custody_tuple"])
        completed = subprocess.run(cas["argv"], cwd=cas["cwd"], env=cas["env"],
                                   input=cas["stdin_bytes"], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, check=False)
        if completed.returncode != 0:
            observed = read_back_published_ref_v1(cas)
            expected_old = context["expected_old_pointer_oid"] or ZERO_OID
            if observed in {candidate_pointer_oid, expected_old}:
                raise RotationError("publication readback has unknown effect")
            classification = quarantine_unreferenced_cas_loser_v1(repo, candidate_pointer_oid)
            raise ExpectedOldCasLost(ref, candidate_pointer_oid,
                                     expected_old, observed, classification)
        observed = read_back_published_ref_v1(cas)
        if observed != candidate_pointer_oid:
            raise RotationError("current-generation pointer readback mismatch")
        return observed


def publish_first_migration_marker_v1() -> str:
    """Publish the permanent marker only after the exact v3 receipt exists."""
    opened_custody = _publication_custody_tuple_v1()
    repo, controller_id, controller_oid, claim_id, run_root, run_id = (
        _publication_custody_fields_v1())
    lease = _acquire_r0039_publication_file_lease_v1(repo)
    lease.__enter__()
    try:
        pointer_ref = f"refs/implementaudit/current-generations/{controller_id}"
        marker_ref = (
            f"refs/implementaudit/current-generation-migrations/{controller_id}")
        pointer_oid = read_optional_exact_ref_oid_v1(repo, pointer_ref)
        if pointer_oid is None or read_optional_exact_ref_oid_v1(repo, marker_ref) is not None:
            raise RotationError("first migration marker precondition is invalid")
        pointer = load_canonical_generation_pointer_oid_v1(repo, pointer_oid)
        if tuple(pointer[name] for name in ("controller_id", "claim_id", "run_id")) != (
                controller_id, claim_id, run_id):
            raise RotationError("first migration marker pointer authority disagrees")
        source_epoch = str(pointer["source_epoch"])
        receipt_ref = (
            f"refs/implementaudit/continuity-receipts/{controller_id}/{source_epoch}")
        receipt_oid = read_optional_exact_ref_oid_v1(repo, receipt_ref)
        if receipt_oid is None:
            raise RotationError("first migration marker requires receipt v3")
        receipt = _receipt_record_v1(repo, receipt_ref + "@" + receipt_oid)
        fields = receipt["fields"]
        if (type(fields) is not list or len(fields) != 18
                or fields[0:5] != [
                    "implementaudit.continuity-receipt.v3", controller_id,
                    claim_id, run_id, source_epoch]
                or fields[6:8] != [pointer_ref, pointer_oid]
                or fields[8:16] != [
                    pointer["pointer_digest"], pointer["hot_state_digest"],
                    pointer["hot_roadmap_digest"], pointer["work_graph_path"],
                    pointer["work_graph_digest"], pointer["generation_manifest_oid"],
                    pointer["generation_manifest_digest"],
                    pointer["cold_high_water"]]):
            raise RotationError("first migration marker requires receipt v3")
        _require_immediate_predecessor_v1(
            repo, fields, controller_id=controller_id,
            controller_oid=controller_oid, claim_id=claim_id,
            run_id=run_id, source_epoch=source_epoch)
        _require_r0011_v3_verification_v1(
            repo, receipt_ref + "@" + receipt_oid)
        marker_raw = "\t".join((
            "implementaudit.current-generation-migration.v1", controller_id,
            claim_id, run_id, source_epoch, pointer_ref,
            "implementaudit.state-generation-pointer.v1", receipt_ref,
            receipt_oid, "true",
        )).encode("utf-8")
        marker_oid = git(
            repo, "hash-object", "-w", "--stdin", input_bytes=marker_raw
        ).decode("ascii", "strict").strip()
        invalidation_ref = f"refs/implementaudit/continuity-invalidations/{controller_id}"
        invalidation_oid = read_optional_exact_ref_oid_v1(repo, invalidation_ref)
        if fields[5] != (invalidation_oid or "none"):
            raise RotationError("first migration marker invalidation disagrees")
        guards = tuple(sorted((
            (f"refs/implementaudit/controllers/{controller_id}", controller_oid),
            (pointer_ref, pointer_oid), (receipt_ref, receipt_oid),
            (invalidation_ref, invalidation_oid or ZERO_OID),
        )))
        cas = prepare_trusted_update_ref_transaction_v1(
            repo=repo, ref=marker_ref, new_oid=marker_oid,
            old_oid=ZERO_OID, verify_refs=guards)
        verify_trusted_update_ref_transaction_v1(cas)
        _require_publication_custody_recheck_v1(opened_custody)
        completed = subprocess.run(
            cas["argv"], cwd=cas["cwd"], env=cas["env"],
            input=cas["stdin_bytes"], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=False)
        if completed.returncode != 0:
            raise RotationError("first migration marker effect is unknown")
        if read_back_published_ref_v1(cas) != marker_oid:
            raise RotationError("first migration marker readback mismatch")
        live = {
            "repo_path": repo, "run_root_path": run_root,
            "controller_id": controller_id, "controller_oid": controller_oid,
            "claim_id": claim_id,
            "run_id": run_id, "source_epoch": source_epoch,
            "pointer_ref": pointer_ref,
        }
        require_complete_pointer_receipt_marker_route_v1(
            live=live, receipt=receipt, pointer=pointer,
            pointer_oid=pointer_oid, marker_oid=marker_oid)
        return marker_oid
    finally:
        lease.__exit__(None, None, None)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_reparse(st: object) -> bool:
    return bool(getattr(st, "st_file_attributes", 0) & 0x400)


def effective_mode(mode: int) -> int:
    if os.name == "nt":
        return 0o666 if mode & stat.S_IWUSR else 0o444
    return mode


def _fixed_git_environment_v1(executable: str,
                              platform_name: str) -> dict[str, str]:
    if platform_name == "nt":
        path_value = ";".join((
            r"C:\Program Files\Git\cmd",
            r"C:\Program Files\Git\bin",
            r"C:\Program Files\Git\usr\bin",
            r"C:\Windows\System32",
            r"C:\Windows",
        ))
        sink = "NUL"
    elif platform_name == "posix":
        path_value = ":".join(dict.fromkeys(
            (str(Path(executable).parent), "/usr/bin", "/bin")))
        sink = "/dev/null"
    else:
        raise RotationError("trusted Git platform is unsupported")
    return {
        "PATH": path_value, "LC_ALL": "C", "LANG": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": sink,
        "GIT_TERMINAL_PROMPT": "0",
    }


def git_environment() -> dict[str, str]:
    return _fixed_git_environment_v1(
        git_executable_v1(), "nt" if os.name == "nt" else "posix")


def git_executable_v1() -> str:
    candidates = (tuple(Path(value) for value in WINDOWS_TRUSTED_GIT_PATHS_V1)
                  if os.name == "nt"
                  else (Path("/usr/bin/git"), Path("/usr/local/bin/git")))
    executable = next((candidate for candidate in candidates
                       if candidate.is_file() and not candidate.is_symlink()), None)
    if executable is None:
        raise RotationError("trusted Git executable is unavailable")
    return str(executable)


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        [git_executable_v1(), "-C", str(repo), *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=git_environment(),
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise RotationError(f"git {' '.join(args)} failed: {detail or result.returncode}")
    return result.stdout


def git_optional(repo: Path, *args: str) -> tuple[int, bytes]:
    result = subprocess.run(
        [git_executable_v1(), "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=git_environment(),
        check=False,
    )
    return result.returncode, result.stdout


def same_path(left: Path, right: Path) -> bool:
    return os.path.normcase(os.path.abspath(left)) == os.path.normcase(
        os.path.abspath(right)
    )


def contained(path: Path, root: Path) -> bool:
    try:
        return os.path.commonpath((os.path.abspath(path), os.path.abspath(root))) == os.path.abspath(root)
    except ValueError:
        return False


def require_safe_directory_chain(path: Path, root: Path) -> None:
    if not contained(path, root):
        raise RotationError(f"path escapes repository custody: {path}")
    relative = path.relative_to(root)
    cursor = root
    for part in (Path("."), *relative.parts):
        if part != Path("."):
            cursor = cursor / part
        try:
            current = os.lstat(cursor)
        except OSError as exc:
            raise RotationError(f"directory custody is unavailable: {cursor}: {exc}") from exc
        if (
            not stat.S_ISDIR(current.st_mode)
            or stat.S_ISLNK(current.st_mode)
            or is_reparse(current)
        ):
            raise RotationError(f"directory custody contains a symlink or reparse point: {cursor}")


def require_repo(raw: str) -> Path:
    repo = Path(os.path.abspath(raw))
    require_safe_directory_chain(repo, repo)
    top = Path(
        git(repo, "rev-parse", "--path-format=absolute", "--show-toplevel")
        .decode("utf-8")
        .strip()
    )
    if not same_path(repo, top):
        raise RotationError("--repo-root is not the exact Git worktree root")
    return repo


def require_run_root(raw: str, repo: Path) -> Path:
    run_root = Path(os.path.abspath(raw))
    require_safe_directory_chain(run_root, repo)
    return run_root


def safe_relative(raw: object, forbidden: set[str]) -> str:
    if (
        not isinstance(raw, str)
        or not raw
        or raw.startswith("/")
        or "\\" in raw
        or re.match(r"^[A-Za-z]:", raw)
    ):
        raise RotationError(f"unsafe protected path: {raw}")
    parts = raw.split("/")
    forbidden_folded = {item.casefold() for item in forbidden}
    if any(part in {"", ".", ".."} for part in parts) or any(
        part.casefold() in forbidden_folded for part in parts
    ):
        raise RotationError(f"unsafe protected path: {raw}")
    return raw


def read_regular(
    path: Path,
    custody_root: Path,
    label: str,
    *,
    require_owner_write: bool,
) -> tuple[bytes, os.stat_result]:
    if not contained(path, custody_root):
        raise RotationError(f"protected path escapes custody: {label}")
    require_safe_directory_chain(path.parent, custody_root)
    try:
        before = os.lstat(path)
    except OSError as exc:
        raise RotationError(f"protected file is unavailable: {label}: {exc}") from exc
    if (
        not stat.S_ISREG(before.st_mode)
        or stat.S_ISLNK(before.st_mode)
        or is_reparse(before)
        or before.st_nlink != 1
    ):
        raise RotationError(f"protected file must be regular, non-linked, and non-reparse: {label}")
    if not (before.st_mode & stat.S_IRUSR) or (
        require_owner_write and not (before.st_mode & stat.S_IWUSR)
    ):
        raise RotationError(f"unsafe permissions for protected file: {label}")

    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or is_reparse(opened)
            or opened.st_nlink != 1
            or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
        ):
            raise RotationError(f"protected file identity changed while opening: {label}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        data = b"".join(chunks)
    finally:
        os.close(descriptor)

    after = os.lstat(path)
    if (
        (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        != (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        or len(data) != before.st_size
    ):
        raise RotationError(f"protected file changed during read: {label}")
    return data, before


def write_new_regular(path: Path, data: bytes, mode: int) -> None:
    mode = effective_mode(mode)
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(path, flags, mode)
    try:
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.chmod(path, mode)
    landed = os.lstat(path)
    if (
        not stat.S_ISREG(landed.st_mode)
        or stat.S_ISLNK(landed.st_mode)
        or is_reparse(landed)
        or landed.st_nlink != 1
        or stat.S_IMODE(landed.st_mode) != mode
    ):
        raise RotationError(f"draft permission or file-kind readback failed: {path.name}")


def validate_identity(controller: str, generation: str) -> str:
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?", controller):
        raise RotationError("invalid controller identity")
    if not re.fullmatch(r"g[0-9]{4}", generation):
        raise RotationError("invalid projection generation identity")
    return f"{ARCHIVE_PREFIX}/{controller}/{generation}"


def load_preimage(
    manifest_path: Path,
    run_root: Path,
    controller: str,
    generation: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_bytes, _ = read_regular(
        manifest_path,
        run_root,
        manifest_path.relative_to(run_root).as_posix(),
        require_owner_write=False,
    )
    try:
        population = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RotationError(f"invalid archive population manifest: {exc}") from exc
    if not isinstance(population, dict) or set(population) != {
        "schema",
        "controller",
        "generation",
        "archive_ref",
        "protected_files",
        "forbidden_source_components",
        "forbidden_transition_fields",
        "expected",
    }:
        raise RotationError("archive population fields drifted")
    archive_ref = validate_identity(controller, generation)
    if population.get("schema") != "implementaudit.canonical-state-rotation-f2-fixture.v1":
        raise RotationError("wrong archive population schema")
    if population.get("controller") != controller or population.get("generation") != generation:
        raise RotationError("archive population owner identity drifted")
    if population.get("archive_ref") != archive_ref:
        raise RotationError("archive population ref identity drifted")
    forbidden_components = population.get("forbidden_source_components")
    if forbidden_components != FORBIDDEN_SOURCE_COMPONENTS:
        raise RotationError("recursive-population exclusions drifted")
    if set(population.get("forbidden_transition_fields", [])) != FORBIDDEN_TRANSITION_FIELDS:
        raise RotationError("transition-envelope exclusions drifted")
    if population.get("expected") != EXPECTED_RESULTS:
        raise RotationError("expected F2 behavior drifted")
    rows = population.get("protected_files")
    if not isinstance(rows, list) or not rows:
        raise RotationError("protected-file population must be nonempty")

    forbidden = set(forbidden_components)
    loaded: list[dict[str, Any]] = []
    seen_roles: set[str] = set()
    seen_paths: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"role", "path"}:
            raise RotationError(f"protected-file row {index} is malformed")
        role = row.get("role")
        if not isinstance(role, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{0,63}", role):
            raise RotationError(f"invalid protected role at row {index}")
        source_path = safe_relative(row.get("path"), forbidden)
        if role in seen_roles or source_path in seen_paths:
            raise RotationError("duplicate protected role or path")
        seen_roles.add(role)
        seen_paths.add(source_path)
        source = run_root.joinpath(*source_path.split("/"))
        data, identity = read_regular(
            source, run_root, source_path, require_owner_write=True
        )
        mode = stat.S_IMODE(identity.st_mode)
        draft_path = f"payload/{index:03d}-{role}.bin"
        predicted_oid = git(run_root, "hash-object", "--stdin", input_bytes=data).decode().strip()
        loaded.append(
            {
                "role": role,
                "source_path": source_path,
                "draft_path": draft_path,
                "sha256": sha256(data),
                "byte_length": len(data),
                "mode": f"{mode:04o}",
                "blob_oid": predicted_oid,
                "_data": data,
            }
        )
    if not {"STATE", "ROADMAP"}.issubset(seen_roles):
        raise RotationError("STATE and ROADMAP roles are required")
    return population, loaded


def classify_protected_state(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {key: value for key, value in entry.items() if key != "_data"}
        for entry in entries
    ]


def quarantine_draft(draft_dir: Path) -> None:
    if not draft_dir.exists():
        return
    quarantine = draft_dir.with_name("quarantine-draft")
    if quarantine.exists() or quarantine.is_symlink():
        raise RotationError("draft failed and fixed quarantine target is unavailable")
    draft_dir.rename(quarantine)


def build_projection_draft(
    repo: Path,
    run_root: Path,
    controller: str,
    generation: str,
    manifest_path: Path,
) -> dict[str, Any]:
    archive_ref = validate_identity(controller, generation)
    if not contained(manifest_path, run_root):
        raise RotationError("archive population manifest escapes run-root custody")
    population, loaded = load_preimage(
        manifest_path, run_root, controller, generation
    )
    entries = classify_protected_state(loaded)
    draft_manifest: dict[str, Any] = {
        "schema": "implementaudit.canonical-state-projection-draft.v1",
        "controller": controller,
        "generation": generation,
        "archive_ref": archive_ref,
        "entries": entries,
        "discovery": "EXCLUDED",
        "recursive_population": "EXCLUDED",
    }
    if FORBIDDEN_TRANSITION_FIELDS.intersection(draft_manifest):
        raise RotationError("projection draft acquired a transition envelope")
    expected = population["expected"]
    if expected["draft_schema"] != draft_manifest["schema"]:
        raise RotationError("draft schema is not admitted by the population")

    generation_root = run_root / "state-generations" / generation
    draft_dir = generation_root / "draft"
    if draft_dir.exists() or draft_dir.is_symlink():
        raise RotationError("projection draft already exists; overwrite refused")
    state_generations = run_root / "state-generations"
    if not state_generations.exists():
        state_generations.mkdir(mode=0o700)
    require_safe_directory_chain(state_generations, repo)
    if not generation_root.exists():
        generation_root.mkdir(mode=0o700)
    require_safe_directory_chain(generation_root, repo)
    draft_dir.mkdir(mode=0o700)
    payload_dir = draft_dir / "payload"
    payload_dir.mkdir(mode=0o700)

    try:
        for entry, loaded_entry in zip(entries, loaded, strict=True):
            mode = int(str(entry["mode"]), 8)
            write_new_regular(
                draft_dir / str(entry["draft_path"]), loaded_entry["_data"], mode
            )
        manifest_bytes = canonical_bytes(draft_manifest)
        write_new_regular(draft_dir / "draft-manifest.json", manifest_bytes, 0o600)
        reread, _ = read_regular(
            draft_dir / "draft-manifest.json",
            draft_dir,
            "draft-manifest.json",
            require_owner_write=True,
        )
        if reread != manifest_bytes:
            raise RotationError("projection draft manifest readback mismatch")
    except BaseException:
        quarantine_draft(draft_dir)
        raise

    return {
        "schema": "implementaudit.canonical-state-projection-draft-receipt.v1",
        "controller": controller,
        "generation": generation,
        "archive_ref": archive_ref,
        "draft_manifest_sha256": sha256(canonical_bytes(draft_manifest)),
        "entries": len(entries),
        "discovery": "EXCLUDED",
        "recursive_population": "EXCLUDED",
    }


def load_draft(
    draft_dir: Path,
    run_root: Path,
    controller: str,
    generation: str,
) -> tuple[dict[str, Any], bytes]:
    expected = run_root / "state-generations" / generation / "draft"
    if not same_path(draft_dir, expected):
        raise RotationError("draft directory is not the canonical undiscoverable location")
    require_safe_directory_chain(draft_dir, run_root)
    raw, _ = read_regular(
        draft_dir / "draft-manifest.json",
        draft_dir,
        "draft-manifest.json",
        require_owner_write=True,
    )
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RotationError(f"invalid projection draft manifest: {exc}") from exc
    if raw != canonical_bytes(manifest):
        raise RotationError("projection draft manifest is not canonical")
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema", "controller", "generation", "archive_ref", "entries",
        "discovery", "recursive_population",
    }:
        raise RotationError("projection draft manifest fields drifted")
    if FORBIDDEN_TRANSITION_FIELDS.intersection(manifest):
        raise RotationError("projection draft contains a transition envelope")
    if manifest.get("schema") != "implementaudit.canonical-state-projection-draft.v1":
        raise RotationError("wrong projection draft schema")
    archive_ref = validate_identity(controller, generation)
    if (
        manifest.get("controller") != controller
        or manifest.get("generation") != generation
        or manifest.get("archive_ref") != archive_ref
    ):
        raise RotationError("projection draft owner identity drifted")
    if manifest.get("discovery") != "EXCLUDED" or manifest.get("recursive_population") != "EXCLUDED":
        raise RotationError("projection draft discovery boundary drifted")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise RotationError("projection draft entry population is empty")
    seen_roles: set[str] = set()
    seen_sources: set[str] = set()
    forbidden_sources = set(FORBIDDEN_SOURCE_COMPONENTS)
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {
            "role", "source_path", "draft_path", "sha256", "byte_length", "mode", "blob_oid"
        }:
            raise RotationError(f"projection draft entry {index} fields drifted")
        role = entry.get("role")
        source_path = safe_relative(entry.get("source_path"), forbidden_sources)
        draft_path = entry.get("draft_path")
        if (
            not isinstance(role, str)
            or not re.fullmatch(r"[A-Z][A-Z0-9_]{0,63}", role)
            or role in seen_roles
        ):
            raise RotationError("duplicate projection draft role")
        source_identity = source_path.casefold()
        if source_identity in seen_sources:
            raise RotationError("duplicate projection draft source path")
        if draft_path != f"payload/{index:03d}-{role}.bin":
            raise RotationError("projection draft payload path drifted")
        seen_roles.add(role)
        seen_sources.add(source_identity)
        mode_text = entry.get("mode")
        if not isinstance(mode_text, str) or not re.fullmatch(r"[0-7]{4}", mode_text):
            raise RotationError("projection draft permission identity is malformed")
        payload_path = draft_dir.joinpath(*str(draft_path).split("/"))
        data, identity = read_regular(
            payload_path, draft_dir, str(draft_path), require_owner_write=False
        )
        if stat.S_IMODE(identity.st_mode) != int(mode_text, 8):
            raise RotationError(f"draft permission readback mismatch: {draft_path}")
        if len(data) != entry.get("byte_length") or sha256(data) != entry.get("sha256"):
            raise RotationError(f"projection draft payload identity mismatch: {draft_path}")
        predicted = git(run_root, "hash-object", "--stdin", input_bytes=data).decode().strip()
        if predicted != entry.get("blob_oid"):
            raise RotationError(f"projection draft blob OID mismatch: {draft_path}")
    return manifest, raw


def receipt_from_archive(archive: dict[str, Any], manifest_oid: str) -> dict[str, Any]:
    return {
        "schema": "implementaudit.canonical-state-archive-receipt.v1",
        "controller": archive["controller"],
        "generation": archive["generation"],
        "archive_ref": archive["archive_ref"],
        "archive_manifest_oid": manifest_oid,
        "archive_manifest_sha256": sha256(canonical_bytes(archive)),
        "draft_manifest_sha256": archive["draft_manifest_sha256"],
        "entries": len(archive["entries"]),
        "retrieval": "GIT_BLOB_OID_AND_SHA256",
        "discovery": "EXCLUDED",
        "recursive_population": "EXCLUDED",
    }


def archive_preimage(
    repo: Path,
    run_root: Path,
    controller: str,
    generation: str,
    draft_dir: Path,
) -> dict[str, Any]:
    archive_ref = validate_identity(controller, generation)
    existing_rc, _ = git_optional(repo, "rev-parse", "--verify", archive_ref)
    if existing_rc == 0:
        raise RotationError("archive ref already exists; expected-zero CAS refused")
    draft, draft_raw = load_draft(
        draft_dir, run_root, controller, generation
    )
    entries = draft["entries"]
    for entry in entries:
        payload_path = draft_dir.joinpath(*str(entry["draft_path"]).split("/"))
        data, _ = read_regular(
            payload_path, draft_dir, str(entry["draft_path"]), require_owner_write=False
        )
        landed_oid = git(repo, "hash-object", "-w", "--stdin", input_bytes=data).decode().strip()
        if landed_oid != entry["blob_oid"]:
            raise RotationError(f"archive blob OID write mismatch: {entry['role']}")
    archive: dict[str, Any] = {
        "schema": "implementaudit.canonical-state-archive.v1",
        "controller": controller,
        "generation": generation,
        "archive_ref": archive_ref,
        "draft_manifest_sha256": sha256(draft_raw),
        "entries": entries,
        "discovery": "EXCLUDED",
        "recursive_population": "EXCLUDED",
    }
    archive_raw = canonical_bytes(archive)
    manifest_oid = git(repo, "hash-object", "-w", "--stdin", input_bytes=archive_raw).decode().strip()
    update = subprocess.run(
        [git_executable_v1(), "-C", str(repo), "update-ref", archive_ref, manifest_oid, ZERO_OID],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=git_environment(),
        check=False,
    )
    if update.returncode != 0:
        raise RotationError("archive ref already exists; expected-zero CAS refused")
    receipt = verify_archive(repo, controller, generation)
    expected_receipt = receipt_from_archive(archive, manifest_oid)
    if receipt != expected_receipt:
        raise RotationError("archive ref or typed readback mismatch")
    return receipt


def verify_archive(repo: Path, controller: str, generation: str) -> dict[str, Any]:
    archive_ref = validate_identity(controller, generation)
    manifest_oid = git(repo, "rev-parse", "--verify", archive_ref).decode().strip()
    if git(repo, "cat-file", "-t", manifest_oid).decode().strip() != "blob":
        raise RotationError("archive manifest object is not a blob")
    raw = git(repo, "cat-file", "blob", manifest_oid)
    try:
        archive = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RotationError(f"invalid archive manifest: {exc}") from exc
    if raw != canonical_bytes(archive):
        raise RotationError("archive manifest is not canonical")
    if not isinstance(archive, dict) or set(archive) != {
        "schema", "controller", "generation", "archive_ref", "draft_manifest_sha256",
        "entries", "discovery", "recursive_population",
    }:
        raise RotationError("archive manifest fields drifted")
    if archive.get("schema") != "implementaudit.canonical-state-archive.v1":
        raise RotationError("wrong archive manifest schema")
    if (
        archive.get("controller") != controller
        or archive.get("generation") != generation
        or archive.get("archive_ref") != archive_ref
    ):
        raise RotationError("archive owner identity drifted")
    if archive.get("discovery") != "EXCLUDED" or archive.get("recursive_population") != "EXCLUDED":
        raise RotationError("archive discovery boundary drifted")
    entries = archive.get("entries")
    if not isinstance(entries, list) or not entries:
        raise RotationError("archive entry population is empty")
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {
            "role", "source_path", "draft_path", "sha256", "byte_length", "mode", "blob_oid"
        }:
            raise RotationError("archive entry fields drifted")
        oid = entry.get("blob_oid")
        if not isinstance(oid, str) or git(repo, "cat-file", "-t", oid).decode().strip() != "blob":
            raise RotationError(f"archive entry is not a blob: {entry.get('role')}")
        data = git(repo, "cat-file", "blob", oid)
        if len(data) != entry.get("byte_length") or sha256(data) != entry.get("sha256"):
            raise RotationError(f"archive entry identity mismatch: {entry.get('role')}")
        computed_oid = git(repo, "hash-object", "--stdin", input_bytes=data).decode().strip()
        if computed_oid != oid:
            raise RotationError(f"archive entry OID mismatch: {entry.get('role')}")
    return receipt_from_archive(archive, manifest_oid)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    draft = commands.add_parser("draft")
    draft.add_argument("--repo-root", required=True)
    draft.add_argument("--run-root", required=True)
    draft.add_argument("--controller", required=True)
    draft.add_argument("--generation", required=True)
    draft.add_argument("--manifest", required=True)
    archive = commands.add_parser("archive")
    archive.add_argument("--repo-root", required=True)
    archive.add_argument("--run-root", required=True)
    archive.add_argument("--controller", required=True)
    archive.add_argument("--generation", required=True)
    archive.add_argument("--draft-dir", required=True)
    verify = commands.add_parser("verify-archive")
    verify.add_argument("--repo-root", required=True)
    verify.add_argument("--controller", required=True)
    verify.add_argument("--generation", required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    repo = require_repo(args.repo_root)
    if args.command == "draft":
        run_root = require_run_root(args.run_root, repo)
        result = build_projection_draft(
            repo,
            run_root,
            args.controller,
            args.generation,
            Path(os.path.abspath(args.manifest)),
        )
    elif args.command == "archive":
        run_root = require_run_root(args.run_root, repo)
        result = archive_preimage(
            repo,
            run_root,
            args.controller,
            args.generation,
            Path(os.path.abspath(args.draft_dir)),
        )
    else:
        result = verify_archive(repo, args.controller, args.generation)
    sys.stdout.buffer.write(canonical_bytes(result))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RotationError as exc:
        print(f"rotate-canonical-state: {exc}", file=sys.stderr)
        raise SystemExit(1)
