#!/usr/bin/env python3
"""Deterministic F2 projection-draft and preimage-archive writer.

This helper deliberately has no current-generation, invalidation, epoch,
receipt, migration-marker, or pointer writer.  Those transaction stages remain
owned by later R0039 cells.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any


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
    return "".join(
        chr(byte) if byte in URI_UNRESERVED else f"%{byte:02X}"
        for byte in normalized.encode("utf-8")
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
    if (kind not in {"repo-relative", "run-root-relative", "evidence-uri", "host-bound"}
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
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_DIR",
        "GIT_INDEX_FILE",
        "GIT_NAMESPACE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_WORK_TREE",
    ):
        environment.pop(name, None)
    return environment


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
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
        ["git", "-C", str(repo), *args],
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
        ["git", "-C", str(repo), "update-ref", archive_ref, manifest_oid, ZERO_OID],
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
