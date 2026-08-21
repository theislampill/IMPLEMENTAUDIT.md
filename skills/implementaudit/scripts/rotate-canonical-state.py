#!/usr/bin/env python3
"""Deterministic F2 archive helper plus bounded immutable-lineage publisher.

The publisher can only CAS one already-stored current-generation pointer under
internally derived controller custody.  It never selects a live source owner,
writes R0011/receipts/markers, or advances any lifecycle state.
"""

from __future__ import annotations

import argparse
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
from pathlib import Path
from typing import Any, NamedTuple


ZERO_OID = "0" * 40
ARCHIVE_PREFIX = "refs/implementaudit/state-archives"
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


class TrustedExecutableIdentityV1(NamedTuple):
    canonical_path: str
    file_identity: tuple[int, int]
    size: int
    ctime_ns: int
    mtime_ns: int
    sha256: str
    owner_identity: str


class _NativeFileSnapshotV1(NamedTuple):
    canonical_path: str
    file_identity: tuple[int, int]
    size: int
    ctime_ns: int
    mtime_ns: int
    owner_identity: str | None


WINDOWS_TRUSTED_GIT_PATHS_V1 = (
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Program Files\Git\bin\git.exe",
)
# These are the only Windows security principals accepted as owners of the
# fixed Program Files Git executable: LocalSystem, BUILTIN\Administrators, and
# NT SERVICE\TrustedInstaller.  Caller/user/service SIDs are never accepted.
WINDOWS_TRUSTED_OWNER_SIDS_V1 = frozenset({
    "S-1-5-18",
    "S-1-5-32-544",
    "S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464",
})
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
    raise RotationError("OE_SOURCE_CONTEXT_NOT_AVAILABLE")


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


def build_event_segment_v1(event: dict[str, object], *,
                           source_evidence_id: str) -> tuple[dict[str, object], bytes]:
    validate_event_request_v1(event)
    context = load_governed_source_context_v1(source_evidence_id)
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
    context = load_governed_publication_context_v1()
    if type(events) is not list or not events:
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
    if sequences != allocate_candidate_sequences_v1(before, len(ordered)):
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
        "high_water": rows[-1]["sequence"],
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
    if type(events) is not list or not events or (predecessor is None and before != "00000000000000000000"):
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
    if [row["sequence"] for row in events] != allocate_candidate_sequences_v1(before, len(events)) or high != events[-1]["sequence"]:
        raise RotationError("manifest sequence is not contiguous")
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


def read_optional_exact_ref_oid_v1(repo: Path, ref: str) -> str | None:
    rc, output = git_optional(repo, "rev-parse", "--verify", ref)
    if rc == 0:
        oid = output.decode("utf-8").strip()
        if not GIT_OID.fullmatch(oid):
            raise RotationError("governed ref identity is invalid")
        return oid
    return None


def _windows_apis_v1() -> tuple[object, object]:
    if os.name != "nt" or not hasattr(ctypes, "WinDLL"):
        raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
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
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    advapi32.GetSecurityInfo.argtypes = [
        ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p),
    ]
    advapi32.GetSecurityInfo.restype = ctypes.c_uint32
    advapi32.ConvertSidToStringSidW.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p),
    ]
    advapi32.ConvertSidToStringSidW.restype = ctypes.c_int
    return kernel32, advapi32


def _windows_open_regular_no_reparse_v1(path: Path) -> int:
    kernel32, _ = _windows_apis_v1()
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
    kernel32, _ = _windows_apis_v1()
    if not kernel32.CloseHandle(ctypes.c_void_p(handle)):
        raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")


def _windows_filetime_ns_v1(value: _WindowsFileTimeV1) -> int:
    ticks = (int(value.high) << 32) | int(value.low)
    return (ticks - WINDOWS_EPOCH_OFFSET_100NS) * 100


def _windows_owner_sid_v1(handle: int) -> str:
    kernel32, advapi32 = _windows_apis_v1()
    owner = ctypes.c_void_p()
    security_descriptor = ctypes.c_void_p()
    result = advapi32.GetSecurityInfo(
        ctypes.c_void_p(handle), 1, 1, ctypes.byref(owner), None, None, None,
        ctypes.byref(security_descriptor),
    )
    if result != 0 or not owner.value or not security_descriptor.value:
        if security_descriptor.value:
            kernel32.LocalFree(security_descriptor)
        raise RotationError("trusted Windows file ownership is unavailable")
    sid_text = ctypes.c_void_p()
    try:
        if not advapi32.ConvertSidToStringSidW(owner, ctypes.byref(sid_text)):
            raise RotationError("trusted Windows file ownership is unavailable")
        return ctypes.wstring_at(sid_text.value)
    finally:
        if sid_text.value:
            kernel32.LocalFree(sid_text)
        kernel32.LocalFree(security_descriptor)


def _windows_snapshot_v1(handle: int, *, include_owner: bool) -> _NativeFileSnapshotV1:
    kernel32, _ = _windows_apis_v1()
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
        _windows_owner_sid_v1(handle) if include_owner else None,
    )


def _windows_read_handle_bytes_v1(handle: int) -> bytes:
    kernel32, _ = _windows_apis_v1()
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


def freeze_trusted_executable_v1(path: Path) -> TrustedExecutableIdentityV1:
    if os.name == "nt":
        handle = _windows_open_regular_no_reparse_v1(path)
        try:
            snapshot = _windows_snapshot_v1(handle, include_owner=True)
            if snapshot.owner_identity not in WINDOWS_TRUSTED_OWNER_SIDS_V1:
                raise RotationError("trusted Windows file ownership is invalid")
            data = _windows_read_handle_bytes_v1(handle)
            after = _windows_snapshot_v1(handle, include_owner=True)
            if after != snapshot or len(data) != snapshot.size:
                raise RotationError("trusted Git executable changed")
        finally:
            _windows_close_handle_v1(handle)
    else:
        if not hasattr(os, "O_NOFOLLOW"):
            raise RotationError("trusted Git executable identity is unsupported")
        try:
            descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        except OSError as exc:
            raise RotationError("trusted Git executable identity is unsupported") from exc
        try:
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode) or before.st_uid != 0:
                raise RotationError("trusted Git executable ownership is invalid")
            data = _read_posix_descriptor_bytes_v1(descriptor)
            after = os.fstat(descriptor)
            if ((before.st_dev, before.st_ino, before.st_size, before.st_ctime_ns,
                 before.st_mtime_ns) !=
                    (after.st_dev, after.st_ino, after.st_size, after.st_ctime_ns,
                     after.st_mtime_ns) or len(data) != before.st_size):
                raise RotationError("trusted Git executable changed")
            snapshot = _NativeFileSnapshotV1(
                os.path.normcase(os.path.abspath(path)),
                (before.st_dev, before.st_ino), before.st_size,
                before.st_ctime_ns, before.st_mtime_ns, "uid:0")
        finally:
            os.close(descriptor)
    return TrustedExecutableIdentityV1(
        snapshot.canonical_path, snapshot.file_identity, snapshot.size,
        snapshot.ctime_ns, snapshot.mtime_ns, hashlib.sha256(data).hexdigest(),
        str(snapshot.owner_identity),
    )


def observe_trusted_executable_v1(
        expected: TrustedExecutableIdentityV1) -> TrustedExecutableIdentityV1:
    observed = freeze_trusted_executable_v1(Path(expected.canonical_path))
    if observed != expected:
        raise RotationError("trusted Git executable changed")
    return observed


def publication_owner_repo_v1() -> Path:
    """Consume the claim-run physical-owner locator without a caller path."""
    claim_helper = Path(__file__).with_name("claim-run.sh")
    runner = ([r"C:\Program Files\Git\bin\bash.exe"]
              if os.name == "nt" else ["/bin/bash"])
    completed = subprocess.run([*runner, str(claim_helper), "--publication-custody"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env=git_environment(), check=False)
    if completed.returncode != 0:
        raise RotationError("publication custody owner contract is unavailable")
    fields = completed.stdout.decode("utf-8", "strict").rstrip("\n").split("\t")
    if len(fields) != 8 or fields[0] != "implementaudit.publication-custody.v1":
        raise RotationError("publication custody owner contract is invalid")
    return require_repo(fields[4])


def load_governed_publication_context_v1() -> dict[str, object]:
    """Read bounded controller custody without accepting a caller override."""
    claim_helper = Path(__file__).with_name("claim-run.sh")
    runner = ([r"C:\Program Files\Git\bin\bash.exe"]
              if os.name == "nt" else ["/bin/bash"])
    completed = subprocess.run([*runner, str(claim_helper), "--publication-custody"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env=git_environment(), check=False)
    if completed.returncode != 0:
        raise RotationError("publication custody owner contract is unavailable")
    try:
        fields = completed.stdout.decode("utf-8", "strict").rstrip("\n").split("\t")
    except UnicodeDecodeError as exc:
        raise RotationError("publication custody owner contract is invalid") from exc
    if len(fields) != 8 or fields[0] != "implementaudit.publication-custody.v1":
        raise RotationError("publication custody owner contract is invalid")
    _, controller_id, controller_oid, claim_id, repo_text, common_text, run_root_text, run_id = fields
    if (not CONTROLLER_ID.fullmatch(controller_id) or not GIT_OID.fullmatch(controller_oid)
            or not CLAIM_ID.fullmatch(claim_id) or not TOKEN_ID.fullmatch(run_id)):
        raise RotationError("publication custody owner contract is invalid")
    controller_repo = require_repo(repo_text)
    controller_common = Path(git(controller_repo, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip()).resolve()
    if controller_common != Path(common_text).resolve():
        raise RotationError("publication custody owner common directory is invalid")
    run_root = require_run_root(run_root_text, controller_repo)
    discovery_repo = controller_repo
    state = run_root / "STATE.md"
    try:
        generation_id = next(line.split(": ", 1)[1] for line in state.read_text("utf-8").splitlines()
                             if line.startswith("Current epoch: "))
    except (OSError, StopIteration, IndexError) as exc:
        raise RotationError("publication generation identity is unavailable") from exc
    if not GENERATION_ID.fullmatch(generation_id):
        raise RotationError("publication generation identity is invalid")
    current_ref = f"refs/implementaudit/current-generations/{controller_id}"
    marker_ref = f"refs/implementaudit/current-generation-migrations/{controller_id}"
    receipt_ref = f"refs/implementaudit/continuity-receipts/{controller_id}/{generation_id}"
    invalidation_ref = f"refs/implementaudit/continuity-invalidations/{controller_id}"
    receipt_oid = read_optional_exact_ref_oid_v1(discovery_repo, receipt_ref)
    if receipt_oid is None:
        raise RotationError("publication continuity receipt is unavailable")
    invalidation_oid = read_optional_exact_ref_oid_v1(discovery_repo, invalidation_ref)
    receipt = read_exact_git_blob_oid_v1(discovery_repo, receipt_oid)
    try:
        receipt_fields = receipt.decode("utf-8", "strict").rstrip("\n").split("\t")
    except UnicodeDecodeError as exc:
        raise RotationError("publication continuity receipt is invalid") from exc
    head = git(controller_repo, "rev-parse", "HEAD").decode("ascii", "strict").strip()
    tree = git(controller_repo, "rev-parse", "HEAD^{tree}").decode("ascii", "strict").strip()
    state_digest = hashlib.sha256(state.read_bytes()).hexdigest()
    roadmap = run_root / "ROADMAP.md"
    roadmap_digest = hashlib.sha256(roadmap.read_bytes()).hexdigest()
    expected_receipt = ["implementaudit.continuity-receipt.v2", controller_id, controller_oid,
                        claim_id, head, tree, state_digest, roadmap_digest,
                        invalidation_oid or "none"]
    if (len(receipt_fields) != 12 or receipt_fields[:9] != expected_receipt
            or receipt_fields[9] not in {"host-reported-compaction", "new-session", "handoff-resume", "manual-resume", "inferred-context-gap"}
            or receipt_fields[10] != generation_id or not receipt_fields[11]):
        raise RotationError("publication continuity receipt does not bind current custody")
    current_oid = read_optional_exact_ref_oid_v1(discovery_repo, current_ref)
    marker_oid = read_optional_exact_ref_oid_v1(discovery_repo, marker_ref)
    if current_oid is None and marker_oid is not None:
        raise RotationError("migration marker exists without generation pointer")
    return {"repo_path": controller_repo, "run_root_path": run_root, "controller_id": controller_id,
            "claim_id": claim_id, "run_id": run_id, "generation_id": generation_id,
            "source_epoch": generation_id, "receipt_oid": receipt_oid,
            "expected_old_pointer_oid": current_oid, "migration_marker_oid": marker_oid,
            "publication_guard_refs": tuple(sorted(((f"refs/implementaudit/controllers/{controller_id}", controller_oid),
                (receipt_ref, receipt_oid), (marker_ref, marker_oid or ZERO_OID),
                (invalidation_ref, invalidation_oid or ZERO_OID))))}


@contextlib.contextmanager
def acquire_r0039_publication_writer_lease_v1():
    """Serialize cooperating publishers; caller supplies no route or authority."""
    discovery_repo = publication_owner_repo_v1()
    gate = Path(git(discovery_repo, "rev-parse", "--path-format=absolute", "--git-path",
                    "implementaudit-r0039-publication.lock").decode().strip())
    gate.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(gate, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
    except FileExistsError as exc:
        raise RotationError("R0039 publication writer lease is held") from exc
    try:
        context = load_governed_publication_context_v1()
        yield context
    finally:
        os.close(descriptor)
        try: os.unlink(gate)
        except OSError: pass


def prepare_trusted_update_ref_transaction_v1(*, repo: Path, ref: str, new_oid: str,
                                              old_oid: str,
                                              verify_refs: tuple[tuple[str, str], ...]) -> dict[str, object]:
    if (not ref.startswith("refs/implementaudit/current-generations/")
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
    if os.name == "nt":
        # Platform fixed trust roots: never derive a final transaction binary
        # from caller environment (including ProgramFiles or PATH).
        candidates = [Path(value) for value in WINDOWS_TRUSTED_GIT_PATHS_V1]
    else:
        candidates = [Path("/usr/bin/git"), Path("/usr/local/bin/git")]
    executable_path = next((candidate for candidate in candidates
                            if candidate.is_file() and not candidate.is_symlink()), None)
    if executable_path is None:
        raise RotationError("trusted Git executable is unavailable")
    trusted_executable = freeze_trusted_executable_v1(executable_path)
    executable = trusted_executable.canonical_path
    git_dir = Path(git(repo, "rev-parse", "--git-dir").decode("utf-8", "strict").strip())
    if not git_dir.is_absolute():
        git_dir = repo / git_dir
    hooks = git_dir / "implementaudit-r0039-empty-hooks"
    global_config = git_dir / "implementaudit-r0039-empty-global-config"
    try:
        hooks.mkdir(mode=0o700, exist_ok=True)
        mode = stat.S_IMODE(os.lstat(hooks).st_mode)
    except OSError as exc:
        raise RotationError("trusted Git hook isolation is unavailable") from exc
    if (not hooks.is_dir() or is_reparse(os.lstat(hooks)) or any(hooks.iterdir())
            or (os.name != "nt" and mode & 0o077)):
        raise RotationError("trusted Git hook isolation is invalid")
    try:
        descriptor = os.open(global_config, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        descriptor = None
    except OSError as exc:
        raise RotationError("trusted Git global configuration is unavailable") from exc
    if descriptor is not None:
        os.close(descriptor)
    try:
        config_stat = os.lstat(global_config)
    except OSError as exc:
        raise RotationError("trusted Git global configuration is unavailable") from exc
    if (not stat.S_ISREG(config_stat.st_mode) or stat.S_ISLNK(config_stat.st_mode)
            or is_reparse(config_stat) or config_stat.st_size != 0):
        raise RotationError("trusted Git global configuration is invalid")
    environment = {"PATH": os.path.dirname(executable), "LC_ALL": "C", "LANG": "C",
                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(global_config),
                   "GIT_TERMINAL_PROMPT": "0"}
    return {"argv": [executable, "-c", f"core.hooksPath={hooks}", "update-ref", "--stdin", "-z"],
            "cwd": str(repo), "env": environment, "stdin_bytes": b"".join(rows), "ref": ref,
            "trusted_executable_identity": trusted_executable,
            "trusted_hooks": str(hooks), "trusted_global_config": str(global_config)}


def read_back_published_ref_v1(cas: dict[str, object]) -> str:
    verify_trusted_update_ref_transaction_v1(cas)
    completed = subprocess.run([str(cas["argv"][0]), "-C", str(cas["cwd"]), "rev-parse", "--verify", str(cas["ref"])],
                               env=dict(cas["env"]), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0:
        raise RotationError("publication readback has unknown effect")
    oid = completed.stdout.decode("utf-8", "strict").strip()
    if not GIT_OID.fullmatch(oid):
        raise RotationError("publication readback identity is invalid")
    return oid


def verify_trusted_update_ref_transaction_v1(cas: dict[str, object]) -> None:
    expected = cas["trusted_executable_identity"]
    if not isinstance(expected, TrustedExecutableIdentityV1):
        raise RotationError("trusted Git executable identity is invalid")
    observe_trusted_executable_v1(expected)
    for value, directory in ((cas["trusted_hooks"], True), (cas["trusted_global_config"], False)):
        path = Path(str(value)); current = os.lstat(path)
        if (is_reparse(current) or (directory and (not path.is_dir() or any(path.iterdir())))
                or (not directory and (not stat.S_ISREG(current.st_mode) or current.st_size != 0))):
            raise RotationError("trusted Git isolation changed")


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
            self.initial = _windows_snapshot_v1(self.handle, include_owner=False)
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
                opened.st_ctime_ns, opened.st_mtime_ns, None)

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
            return _windows_snapshot_v1(self.handle, include_owner=False)
        if self.descriptor is None:
            raise RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED")
        current = os.fstat(self.descriptor)
        return _NativeFileSnapshotV1(
            self.initial.canonical_path, (current.st_dev, current.st_ino),
            current.st_size, current.st_ctime_ns, current.st_mtime_ns, None)

    def reopened_snapshot(self) -> _NativeFileSnapshotV1:
        path = Path(self.initial.canonical_path)
        if os.name == "nt":
            reopened = _windows_open_regular_no_reparse_v1(path)
            try:
                return _windows_snapshot_v1(reopened, include_owner=False)
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
            current.st_size, current.st_ctime_ns, current.st_mtime_ns, None)


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

    def observe(self, *, reopen: bool) -> tuple[PublicationObservationV1, ...]:
        rows: list[PublicationObservationV1] = []
        for role, retained in self.opened:
            data = retained.read_exact()
            current = retained.current_snapshot()
            if current != retained.initial or len(data) != retained.initial.size:
                raise RotationError("publication input changed during observation")
            if reopen and retained.reopened_snapshot() != retained.initial:
                raise RotationError("publication input changed during observation")
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
        return tuple(rows)


def observe_publication_vector_v1(*, context: dict[str, object],
                                  expected_digests: dict[str, str] | None = None
                                  ) -> tuple[PublicationObservationV1, ...]:
    with PublicationObservationSessionV1(context, expected_digests) as session:
        return session.observe(reopen=True)


def publish_generation_pointer_v1(*, candidate_pointer_oid: str) -> str:
    if type(candidate_pointer_oid) is not str or not GIT_OID.fullmatch(candidate_pointer_oid):
        raise RotationError("candidate pointer identity is invalid")
    with acquire_r0039_publication_writer_lease_v1() as context:
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
        expected_digests = {"STATE": str(pointer["hot_state_digest"]),
                            "ROADMAP": str(pointer["hot_roadmap_digest"]),
                            "WORK_GRAPH": str(pointer["work_graph_digest"])}
        ref = f"refs/implementaudit/current-generations/{context['controller_id']}"
        cas = prepare_trusted_update_ref_transaction_v1(
            repo=repo, ref=ref, new_oid=candidate_pointer_oid,
            old_oid=context["expected_old_pointer_oid"] or ZERO_OID,
            verify_refs=context["publication_guard_refs"])
        with PublicationObservationSessionV1(context, expected_digests) as session:
            first = session.observe(reopen=False)
            second = session.observe(reopen=True)
            # Revalidate the fixed executable identity and isolated Git inputs
            # immediately before the final equality decision.  Once equality
            # completes, the one prebuilt update-ref process is the only call.
            verify_trusted_update_ref_transaction_v1(cas)
            if first != second or not frozen:
                raise RotationError("publication input changed during the final fence")
            completed = subprocess.run(cas["argv"], cwd=cas["cwd"], env=cas["env"],
                                       input=cas["stdin_bytes"], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, check=False)
        if completed.returncode != 0:
            observed = read_optional_exact_ref_oid_v1(repo, ref)
            classification = quarantine_unreferenced_cas_loser_v1(repo, candidate_pointer_oid)
            raise ExpectedOldCasLost(ref, candidate_pointer_oid,
                                     context["expected_old_pointer_oid"] or ZERO_OID, observed, classification)
        observed = read_back_published_ref_v1(cas)
        if observed != candidate_pointer_oid:
            raise RotationError("current-generation pointer readback mismatch")
        return observed


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


def git_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for name in (
        "BASH_ENV",
        "CDPATH",
        "DYLD_INSERT_LIBRARIES",
        "ENV",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_GLOBAL",
        "GIT_CONFIG_NOSYSTEM",
        "GIT_CONFIG_SYSTEM",
        "GIT_DIR",
        "GIT_EXEC_PATH",
        "GIT_INDEX_FILE",
        "GIT_NAMESPACE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_SSH",
        "GIT_SSH_COMMAND",
        "GIT_WORK_TREE",
        "LD_PRELOAD",
    ):
        environment.pop(name, None)
    for name in tuple(environment):
        if (name.startswith("BASH_FUNC_")
                or name.startswith("GIT_CONFIG_KEY_")
                or name.startswith("GIT_CONFIG_VALUE_")):
            environment.pop(name, None)
    if os.name == "nt":
        environment["PATH"] = ";".join((
            r"C:\Program Files\Git\cmd",
            r"C:\Program Files\Git\bin",
            r"C:\Program Files\Git\usr\bin",
            r"C:\Windows\System32",
            r"C:\Windows",
        ))
    return environment


def git_executable_v1() -> str:
    if os.name != "nt":
        return "git"
    executable = next((Path(value) for value in WINDOWS_TRUSTED_GIT_PATHS_V1
                       if Path(value).is_file() and not Path(value).is_symlink()), None)
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
