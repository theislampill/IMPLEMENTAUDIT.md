#!/usr/bin/env python3
"""Build and classify immutable, bounded worker-continuation packets."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pathlib
import re
import sys
import unicodedata
from typing import Any


SOURCE_SCHEMA = "implementaudit.bounded-continuation-source.v1"
PACKET_SCHEMA = "implementaudit.bounded-continuation-packet.v1"
BUILD_SCHEMA = "implementaudit.bounded-continuation-build.v1"
OBSERVATION_SCHEMA = "implementaudit.bounded-continuation-observation.v1"
CLASSIFICATION_SCHEMA = "implementaudit.bounded-continuation-classification.v1"
AUTHORITY_CEILING = "PARENT_GOVERNOR_ADJUDICATION_REQUIRED"
MAX_PACKET_BYTES = 32 * 1024

SOURCE_KEYS = {
    "schema", "controller", "target", "graph", "authority", "process",
    "evidence", "continuation",
}
PACKET_KEYS = SOURCE_KEYS | {"packet_digest"}
CONTROLLER_KEYS = {"controller_id", "claim_id", "run_id", "receipt_ref"}
TARGET_KEYS = {
    "repository_id", "git_common_id", "worktree_id", "cell_id",
    "base_commit", "base_tree", "head_commit", "head_tree",
}
GRAPH_KEYS = {
    "digest", "state", "dependencies", "writer_holds", "resource_holds",
}
AUTHORITY_KEYS = {"authorized_files", "authorized_effects"}
PROCESS_KEYS = {
    "context_id", "result_disposition", "active_constraints",
    "instruction_events",
}
EVIDENCE_KEYS = {"pointers", "focused_tests", "unresolved_evidence_id"}
CONTINUATION_KEYS = {"next_action", "stop_conditions", "return_schema"}
EVENT_KEYS = {"event_id", "event_digest", "disposition"}
OBSERVATION_KEYS = {
    "schema", "controller", "target", "graph", "currentness",
    "effect_status", "receiver", "instruction_events", "subagent_observations",
    "activegraph", "query_result",
}
RECEIVER_KEYS = {"context_id", "interrupted_cognition", "headroom_sufficient"}
SUBAGENT_KEYS = {
    "observation_id", "event_kind", "agent_id", "task_id", "lane_id", "status",
}
ACTIVEGRAPH_KEYS = {"state", "digest"}
QUERY_RESULT_KEYS = {
    "schema", "query_contract", "filters", "rows", "row_bytes", "max_rows",
    "max_bytes", "coverage", "requested_position", "next_cursor", "truncated",
    "code", "decision_usable", "authority_ceiling", "establishes",
}
HISTORY_EVENT_KEYS = {
    "schema_version", "run_id", "controller_id", "generation_id", "sequence",
    "record_kind", "subject_id", "source_epoch", "transition", "status",
    "supersedes_event_id", "payload", "source_evidence_id", "source_locator",
    "source_digest", "payload_digest", "event_id",
}
POSITION_KEYS = {"sequence", "event_id"}
SOURCE_LOCATOR_KEYS = {"kind", "root_identity", "path", "host_identity"}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SHA256_ID_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
OID_RE = re.compile(r"^[0-9a-f]{40}$")
EVENT_ID_RE = re.compile(r"^iaevt-v1-[0-9a-f]{64}$")
RECEIPT_RE = re.compile(
    r"^refs/implementaudit/continuity-receipts/[^/]+/G[0-9A-F]+@[0-9a-f]{40}$"
)
TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]*$")
HISTORY_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
HISTORY_CONTROLLER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,47}$")
GENERATION_RE = re.compile(r"^G[0-9A-F]{4}$")
SEQUENCE_RE = re.compile(r"^[0-9]{20}$")
SOURCE_EVIDENCE_RE = re.compile(
    r"^iasrc-v1-(?:r0039-archive|r0038-snapshot)-[A-Za-z0-9._-]{1,96}$"
)
PATH_COMPONENT_RE = re.compile(r"^(?:[A-Za-z0-9._~-]|%[0-9A-F]{2})+$")
HISTORY_RECORD_KINDS = {
    "finding.closed", "andon.closed", "residual.terminal", "epoch.closed",
    "instruction.satisfied", "phase.completed", "transition.closed",
    "recovery.record", "artifact.historical",
}
HISTORY_TRANSITIONS = {"MIGRATED", "APPENDED", "CORRECTED", "SUPERSEDED"}
HISTORY_STATUSES = {"PRESERVED", "CLOSED", "SATISFIED", "EXPIRED", "SUPERSEDED"}
URI_PREFIX = "implementaudit-evidence:v1/"
URI_UNRESERVED = frozenset(
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
)
INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1


class ContinuationError(ValueError):
    """The packet or observation does not satisfy the bounded v1 contract."""

    def __init__(self, code: str, path: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message


def fail(code: str, path: str, message: str) -> None:
    raise ContinuationError(code, path, message)


def reject_float(token: str) -> float:
    fail("CONTINUATION_JSON_INVALID", "$", f"floats are forbidden: {token}")


def reject_constant(token: str) -> None:
    fail("CONTINUATION_JSON_INVALID", "$", f"non-finite value is forbidden: {token}")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("CONTINUATION_JSON_INVALID", "$", f"duplicate key: {key}")
        result[key] = value
    return result


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def load_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        fail("CONTINUATION_INPUT_UNAVAILABLE", str(path), str(exc))
    if raw.startswith(b"\xef\xbb\xbf"):
        fail("CONTINUATION_JSON_INVALID", str(path), "UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8", "strict")
        value = json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_float=reject_float,
            parse_constant=reject_constant,
        )
    except ContinuationError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail("CONTINUATION_JSON_INVALID", str(path), str(exc))
    if type(value) is not dict:
        fail("CONTINUATION_JSON_INVALID", str(path), "root must be an object")
    return value


def exact_object(value: Any, keys: set[str], path: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        fail(
            "CONTINUATION_SCHEMA_INVALID",
            path,
            f"keys must be exactly {sorted(keys)!r}",
        )
    return value


def exact_text(value: Any, path: str, pattern: re.Pattern[str] | None = None) -> str:
    if type(value) is not str or not value:
        fail("CONTINUATION_SCHEMA_INVALID", path, "must be non-empty text")
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        fail("CONTINUATION_SCHEMA_INVALID", path, "surrogates are forbidden")
    if pattern is not None and not pattern.fullmatch(value):
        fail("CONTINUATION_SCHEMA_INVALID", path, "text is not canonical")
    return value


def text_list(value: Any, path: str, *, allow_empty: bool = False) -> list[str]:
    if type(value) is not list or (not value and not allow_empty):
        fail("CONTINUATION_SCHEMA_INVALID", path, "must be a bounded text array")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(exact_text(item, f"{path}[{index}]"))
    if len(result) != len(set(result)):
        fail("CONTINUATION_SCHEMA_INVALID", path, "items must be unique")
    return result


def validate_identity_json(value: Any, path: str) -> None:
    if value is None or type(value) is bool:
        return
    if type(value) is str:
        exact_text(value, path)
        return
    if type(value) is int:
        if not INT64_MIN <= value <= INT64_MAX:
            fail("CONTINUATION_SCHEMA_INVALID", path, "integer exceeds R0038 identity bounds")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            validate_identity_json(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                fail("CONTINUATION_SCHEMA_INVALID", path, "payload keys must be text")
            validate_identity_json(item, f"{path}.{key}")
        return
    fail("CONTINUATION_SCHEMA_INVALID", path, "value has no R0038 identity")


def canonical_path_component(token: str, path: str, *, evidence_uri: bool) -> None:
    if not PATH_COMPONENT_RE.fullmatch(token):
        fail("CONTINUATION_SCHEMA_INVALID", path, "source path component is not canonical")
    raw = bytearray()
    index = 0
    while index < len(token):
        if token[index] == "%":
            raw.append(int(token[index + 1:index + 3], 16))
            index += 3
        else:
            raw.append(ord(token[index]))
            index += 1
    try:
        decoded = bytes(raw).decode("utf-8", "strict")
    except UnicodeDecodeError:
        fail("CONTINUATION_SCHEMA_INVALID", path, "source path component is not UTF-8")
    decoded = unicodedata.normalize("NFC", decoded)
    forbidden = {"\0", "/"} | ({"\\"} if evidence_uri else set())
    if decoded in {"", ".", ".."} or any(char in decoded for char in forbidden):
        fail("CONTINUATION_SCHEMA_INVALID", path, "source path component is unsafe")
    encoded = decoded.encode("utf-8", "strict")
    expected = "".join(
        chr(byte) if byte in URI_UNRESERVED else f"%{byte:02X}"
        for byte in encoded
    )
    if token != expected:
        fail("CONTINUATION_SCHEMA_INVALID", path, "source path component is not normalized")


def validate_source_locator(value: Any, path: str) -> dict[str, Any]:
    locator = exact_object(value, SOURCE_LOCATOR_KEYS, path)
    kind = locator["kind"]
    if kind not in {"repo-relative", "run-root-relative", "evidence-uri", "host-bound"}:
        fail("CONTINUATION_SCHEMA_INVALID", f"{path}.kind", "kind is invalid")
    exact_text(locator["root_identity"], f"{path}.root_identity", SHA256_ID_RE)
    raw_path = exact_text(locator["path"], f"{path}.path")
    if not raw_path.isascii():
        fail("CONTINUATION_SCHEMA_INVALID", f"{path}.path", "source path is not canonical ASCII")
    if kind == "evidence-uri":
        if locator["host_identity"] is not None or not raw_path.startswith(URI_PREFIX):
            fail("CONTINUATION_SCHEMA_INVALID", path, "evidence URI locator is inconsistent")
        components = raw_path[len(URI_PREFIX):].split("/")
        evidence_uri = True
    else:
        if raw_path.startswith("/") or raw_path.endswith("/") or "\\" in raw_path:
            fail("CONTINUATION_SCHEMA_INVALID", f"{path}.path", "relative source path is invalid")
        components = raw_path.split("/")
        evidence_uri = False
        if kind == "host-bound":
            exact_text(locator["host_identity"], f"{path}.host_identity", SHA256_ID_RE)
        elif locator["host_identity"] is not None:
            fail("CONTINUATION_SCHEMA_INVALID", f"{path}.host_identity", "host identity is not allowed")
    if not components or any(not component for component in components):
        fail("CONTINUATION_SCHEMA_INVALID", f"{path}.path", "source path is empty")
    for index, component in enumerate(components):
        canonical_path_component(
            component, f"{path}.path[{index}]", evidence_uri=evidence_uri,
        )
    return locator


def validate_history_event(value: Any, path: str) -> dict[str, Any]:
    event = exact_object(value, HISTORY_EVENT_KEYS, path)
    if event["schema_version"] != "implementaudit.history-event.v1":
        fail("CONTINUATION_SCHEMA_INVALID", f"{path}.schema_version", "event schema is invalid")
    exact_text(event["run_id"], f"{path}.run_id", HISTORY_TOKEN_RE)
    exact_text(event["controller_id"], f"{path}.controller_id", HISTORY_CONTROLLER_RE)
    exact_text(event["generation_id"], f"{path}.generation_id", GENERATION_RE)
    exact_text(event["sequence"], f"{path}.sequence", SEQUENCE_RE)
    exact_text(event["subject_id"], f"{path}.subject_id", HISTORY_TOKEN_RE)
    exact_text(event["source_epoch"], f"{path}.source_epoch", GENERATION_RE)
    exact_text(event["source_evidence_id"], f"{path}.source_evidence_id", SOURCE_EVIDENCE_RE)
    if event["record_kind"] not in HISTORY_RECORD_KINDS:
        fail("CONTINUATION_SCHEMA_INVALID", f"{path}.record_kind", "record kind is invalid")
    if event["transition"] not in HISTORY_TRANSITIONS:
        fail("CONTINUATION_SCHEMA_INVALID", f"{path}.transition", "transition is invalid")
    if event["status"] not in HISTORY_STATUSES:
        fail("CONTINUATION_SCHEMA_INVALID", f"{path}.status", "status is invalid")
    if event["supersedes_event_id"] is not None:
        exact_text(event["supersedes_event_id"], f"{path}.supersedes_event_id", EVENT_ID_RE)
    validate_identity_json(event["payload"], f"{path}.payload")
    validate_source_locator(event["source_locator"], f"{path}.source_locator")
    exact_text(event["source_digest"], f"{path}.source_digest", SHA256_ID_RE)
    exact_text(event["payload_digest"], f"{path}.payload_digest", SHA256_RE)
    exact_text(event["event_id"], f"{path}.event_id", EVENT_ID_RE)
    return event


def history_event_identity_is_valid(event: dict[str, Any]) -> bool:
    expected_payload = hashlib.sha256(canonical_json(event["payload"])).hexdigest()
    if event["payload_digest"] != expected_payload:
        return False
    unsigned = dict(event)
    unsigned.pop("event_id")
    expected_identity = "iaevt-v1-" + hashlib.sha256(canonical_json(unsigned)).hexdigest()
    return event["event_id"] == expected_identity


def validate_controller(value: Any, path: str) -> dict[str, Any]:
    result = exact_object(value, CONTROLLER_KEYS, path)
    exact_text(result["controller_id"], f"{path}.controller_id", TOKEN_RE)
    exact_text(result["claim_id"], f"{path}.claim_id", TOKEN_RE)
    exact_text(result["run_id"], f"{path}.run_id", TOKEN_RE)
    exact_text(result["receipt_ref"], f"{path}.receipt_ref", RECEIPT_RE)
    return result


def validate_target(value: Any, path: str) -> dict[str, Any]:
    result = exact_object(value, TARGET_KEYS, path)
    for key in ("repository_id", "git_common_id", "worktree_id"):
        exact_text(result[key], f"{path}.{key}", SHA256_ID_RE)
    exact_text(result["cell_id"], f"{path}.cell_id", TOKEN_RE)
    for key in ("base_commit", "base_tree", "head_commit", "head_tree"):
        exact_text(result[key], f"{path}.{key}", OID_RE)
    return result


def validate_graph(value: Any, path: str) -> dict[str, Any]:
    result = exact_object(value, GRAPH_KEYS, path)
    exact_text(result["digest"], f"{path}.digest", SHA256_RE)
    if result["state"] not in {"ACTIVE", "READY", "BLOCKED", "DONE"}:
        fail("CONTINUATION_SCHEMA_INVALID", f"{path}.state", "state is invalid")
    text_list(result["dependencies"], f"{path}.dependencies", allow_empty=True)
    text_list(result["writer_holds"], f"{path}.writer_holds", allow_empty=True)
    text_list(result["resource_holds"], f"{path}.resource_holds", allow_empty=True)
    return result


def validate_events(value: Any, path: str) -> list[dict[str, Any]]:
    if type(value) is not list:
        fail("CONTINUATION_SCHEMA_INVALID", path, "must be an event array")
    seen: set[str] = set()
    for index, item in enumerate(value):
        event_path = f"{path}[{index}]"
        event = exact_object(item, EVENT_KEYS, event_path)
        identity = exact_text(event["event_id"], f"{event_path}.event_id", EVENT_ID_RE)
        exact_text(event["event_digest"], f"{event_path}.event_digest", SHA256_RE)
        if event["disposition"] not in {"CONSUMED", "NEW", "PENDING"}:
            fail(
                "CONTINUATION_SCHEMA_INVALID",
                f"{event_path}.disposition",
                "event disposition is invalid",
            )
        if identity in seen:
            fail("CONTINUATION_SCHEMA_INVALID", path, "event identities must be unique")
        seen.add(identity)
    return value


def validate_subagent_observations(value: Any, path: str) -> list[dict[str, Any]]:
    if type(value) is not list:
        fail("CONTINUATION_SCHEMA_INVALID", path, "must be an observation array")
    seen: set[str] = set()
    statuses = {"STARTED", "PARTIAL", "FAILED", "CANCELLED", "SUCCESS_RETURNED"}
    for index, item in enumerate(value):
        row_path = f"{path}[{index}]"
        row = exact_object(item, SUBAGENT_KEYS, row_path)
        identity = exact_text(row["observation_id"], f"{row_path}.observation_id", TOKEN_RE)
        for key in ("agent_id", "task_id", "lane_id"):
            exact_text(row[key], f"{row_path}.{key}", TOKEN_RE)
        if row["event_kind"] not in {"SubagentStart", "SubagentStop"}:
            fail("CONTINUATION_SCHEMA_INVALID", f"{row_path}.event_kind", "event kind is invalid")
        if row["status"] not in statuses:
            fail("CONTINUATION_SCHEMA_INVALID", f"{row_path}.status", "status is invalid")
        if (row["event_kind"] == "SubagentStart") != (row["status"] == "STARTED"):
            fail("CONTINUATION_SCHEMA_INVALID", row_path, "start/stop status is inconsistent")
        if identity in seen:
            fail("CONTINUATION_SCHEMA_INVALID", path, "observation identities must be unique")
        seen.add(identity)
    return value


def validate_position(value: Any, path: str, *, nullable: bool = True) -> dict[str, Any] | None:
    if value is None and nullable:
        return None
    result = exact_object(value, POSITION_KEYS, path)
    exact_text(result["sequence"], f"{path}.sequence", SEQUENCE_RE)
    exact_text(result["event_id"], f"{path}.event_id", EVENT_ID_RE)
    return result


def validate_query_result(value: Any, path: str) -> dict[str, Any]:
    result = exact_object(value, QUERY_RESULT_KEYS, path)
    if result["schema"] != "implementaudit.operational-evidence-query-result.v1":
        fail("CONTINUATION_SCHEMA_INVALID", f"{path}.schema", "query schema is invalid")
    if result["query_contract"] != "implementaudit.history-query.v1":
        fail("CONTINUATION_SCHEMA_INVALID", f"{path}.query_contract", "query contract is invalid")
    filters = exact_object(result["filters"], {"event_ids"}, f"{path}.filters")
    event_ids = text_list(filters["event_ids"], f"{path}.filters.event_ids")
    if len(event_ids) != 1 or not EVENT_ID_RE.fullmatch(event_ids[0]):
        fail("CONTINUATION_SCHEMA_INVALID", f"{path}.filters.event_ids", "one canonical event is required")
    if type(result["rows"]) is not list:
        fail("CONTINUATION_SCHEMA_INVALID", f"{path}.rows", "rows must be an array")
    for index, row in enumerate(result["rows"]):
        row_path = f"{path}.rows[{index}]"
        validate_history_event(row, row_path)
    for key in ("row_bytes", "max_rows", "max_bytes"):
        if type(result[key]) is not int or result[key] < (0 if key == "row_bytes" else 1):
            fail("CONTINUATION_SCHEMA_INVALID", f"{path}.{key}", "bound is invalid")
    coverage = exact_object(result["coverage"], {"start", "end"}, f"{path}.coverage")
    validate_position(coverage["start"], f"{path}.coverage.start")
    validate_position(coverage["end"], f"{path}.coverage.end")
    validate_position(result["requested_position"], f"{path}.requested_position")
    if result["next_cursor"] is not None:
        exact_text(result["next_cursor"], f"{path}.next_cursor")
    if type(result["truncated"]) is not bool or type(result["decision_usable"]) is not bool:
        fail("CONTINUATION_SCHEMA_INVALID", path, "query booleans are invalid")
    exact_text(result["code"], f"{path}.code", TOKEN_RE)
    if result["authority_ceiling"] != "READ_ONLY_OBSERVATION" or result["establishes"] != []:
        fail("CONTINUATION_SCHEMA_INVALID", path, "query crossed its authority ceiling")
    return result


def query_result_is_usable(
        value: dict[str, Any], evidence_id: str, packet: dict[str, Any]) -> bool:
    row = value["rows"][0] if len(value["rows"]) == 1 else None
    if row is None:
        return False
    receipt_generation = packet["controller"]["receipt_ref"].rsplit("/", 1)[1].split("@", 1)[0]
    position = {"sequence": row["sequence"], "event_id": row["event_id"]}
    return (
        value["filters"] == {"event_ids": [evidence_id]}
        and row["event_id"] == evidence_id
        and row["controller_id"] == packet["controller"]["controller_id"]
        and row["run_id"] == packet["controller"]["run_id"]
        and row["generation_id"] == receipt_generation
        and row["source_epoch"] == receipt_generation
        and history_event_identity_is_valid(row)
        and value["row_bytes"] == len(canonical_json(row))
        and value["max_rows"] >= 1
        and value["max_bytes"] >= value["row_bytes"]
        and value["coverage"] == {"start": position, "end": position}
        and value["requested_position"] is None
        and value["next_cursor"] is None
        and value["truncated"] is False
        and value["code"] == "OK"
        and value["decision_usable"] is True
    )


def validate_source(value: Any) -> dict[str, Any]:
    result = exact_object(value, SOURCE_KEYS, "$source")
    if result["schema"] != SOURCE_SCHEMA:
        fail("CONTINUATION_SCHEMA_INVALID", "$.source.schema", "source schema is invalid")
    validate_controller(result["controller"], "$.source.controller")
    validate_target(result["target"], "$.source.target")
    validate_graph(result["graph"], "$.source.graph")
    authority = exact_object(result["authority"], AUTHORITY_KEYS, "$.source.authority")
    text_list(authority["authorized_files"], "$.source.authority.authorized_files")
    text_list(authority["authorized_effects"], "$.source.authority.authorized_effects")
    process = exact_object(result["process"], PROCESS_KEYS, "$.source.process")
    exact_text(process["context_id"], "$.source.process.context_id", TOKEN_RE)
    exact_text(process["result_disposition"], "$.source.process.result_disposition", TOKEN_RE)
    text_list(process["active_constraints"], "$.source.process.active_constraints", allow_empty=True)
    validate_events(process["instruction_events"], "$.source.process.instruction_events")
    evidence = exact_object(result["evidence"], EVIDENCE_KEYS, "$.source.evidence")
    text_list(evidence["pointers"], "$.source.evidence.pointers", allow_empty=True)
    text_list(evidence["focused_tests"], "$.source.evidence.focused_tests")
    unresolved = evidence["unresolved_evidence_id"]
    if unresolved is not None:
        exact_text(unresolved, "$.source.evidence.unresolved_evidence_id", EVENT_ID_RE)
    continuation = exact_object(
        result["continuation"], CONTINUATION_KEYS, "$.source.continuation"
    )
    exact_text(continuation["next_action"], "$.source.continuation.next_action")
    text_list(continuation["stop_conditions"], "$.source.continuation.stop_conditions")
    exact_text(continuation["return_schema"], "$.source.continuation.return_schema", TOKEN_RE)
    return result


def packet_digest(packet: dict[str, Any]) -> str:
    unsigned = dict(packet)
    unsigned.pop("packet_digest", None)
    return hashlib.sha256(canonical_json(unsigned)).hexdigest()


def validate_packet(value: Any) -> dict[str, Any]:
    if len(canonical_json(value)) > MAX_PACKET_BYTES:
        fail(
            "CONTINUATION_BOUND_EXCEEDED",
            "$packet",
            f"canonical packet exceeds {MAX_PACKET_BYTES} bytes",
        )
    result = exact_object(value, PACKET_KEYS, "$packet")
    source = dict(result)
    source.pop("packet_digest")
    source["schema"] = SOURCE_SCHEMA
    validate_source(source)
    if result["schema"] != PACKET_SCHEMA:
        fail("CONTINUATION_SCHEMA_INVALID", "$.packet.schema", "packet schema is invalid")
    exact_text(result["packet_digest"], "$.packet.packet_digest", SHA256_RE)
    if result["packet_digest"] != packet_digest(result):
        fail("CONTINUATION_PACKET_DIGEST_MISMATCH", "$.packet.packet_digest", "digest is stale")
    return result


def validate_observation(value: Any) -> dict[str, Any]:
    result = exact_object(value, OBSERVATION_KEYS, "$observation")
    if result["schema"] != OBSERVATION_SCHEMA:
        fail(
            "CONTINUATION_SCHEMA_INVALID",
            "$.observation.schema",
            "observation schema is invalid",
        )
    validate_controller(result["controller"], "$.observation.controller")
    validate_target(result["target"], "$.observation.target")
    validate_graph(result["graph"], "$.observation.graph")
    if result["currentness"] not in {"CURRENT", "STALE", "UNKNOWN"}:
        fail("CONTINUATION_SCHEMA_INVALID", "$.observation.currentness", "value is invalid")
    if result["effect_status"] not in {"CLEAR", "PENDING", "UNKNOWN"}:
        fail("CONTINUATION_SCHEMA_INVALID", "$.observation.effect_status", "value is invalid")
    receiver = exact_object(result["receiver"], RECEIVER_KEYS, "$.observation.receiver")
    exact_text(receiver["context_id"], "$.observation.receiver.context_id", TOKEN_RE)
    if type(receiver["interrupted_cognition"]) is not bool:
        fail("CONTINUATION_SCHEMA_INVALID", "$.observation.receiver.interrupted_cognition", "must be boolean")
    if type(receiver["headroom_sufficient"]) is not bool:
        fail("CONTINUATION_SCHEMA_INVALID", "$.observation.receiver.headroom_sufficient", "must be boolean")
    validate_events(result["instruction_events"], "$.observation.instruction_events")
    validate_subagent_observations(
        result["subagent_observations"], "$.observation.subagent_observations"
    )
    if result["activegraph"] is not None:
        mirror = exact_object(result["activegraph"], ACTIVEGRAPH_KEYS, "$.observation.activegraph")
        if mirror["state"] not in {"ACTIVE", "READY", "BLOCKED", "DONE"}:
            fail("CONTINUATION_SCHEMA_INVALID", "$.observation.activegraph.state", "state is invalid")
        exact_text(mirror["digest"], "$.observation.activegraph.digest", SHA256_RE)
    if result["query_result"] is not None:
        validate_query_result(result["query_result"], "$.observation.query_result")
    return result


def build_packet(source: dict[str, Any]) -> dict[str, Any]:
    validate_source(source)
    packet = copy.deepcopy(source)
    packet["schema"] = PACKET_SCHEMA
    packet["packet_digest"] = packet_digest(packet)
    raw = canonical_json(packet)
    if len(raw) > MAX_PACKET_BYTES:
        fail(
            "CONTINUATION_BOUND_EXCEEDED",
            "$packet",
            f"canonical packet exceeds {MAX_PACKET_BYTES} bytes",
        )
    text = raw.decode("utf-8")
    return {
        "schema": BUILD_SCHEMA,
        "packet": packet,
        "measurement": {
            "encoding": "UTF-8",
            "bytes": len(raw),
            "characters": len(text),
            "token_estimator": "characters/4-ceiling",
            "estimated_tokens": (len(text) + 3) // 4,
        },
        "authority_ceiling": AUTHORITY_CEILING,
        "establishes": [],
    }


def classify(packet: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    packet = validate_packet(packet)
    observation = validate_observation(observation)
    contradictions: list[str] = []
    if packet["controller"] != observation["controller"]:
        contradictions.append("CONTROLLER_IDENTITY_MISMATCH")
    if packet["target"] != observation["target"]:
        contradictions.append("TARGET_IDENTITY_MISMATCH")
    if packet["graph"] != observation["graph"]:
        contradictions.append("GRAPH_PROJECTION_MISMATCH")
    if observation["currentness"] != "CURRENT":
        contradictions.append("CONTINUITY_NOT_CURRENT")
    if observation["effect_status"] != "CLEAR":
        contradictions.append("EFFECT_NOT_CLEAR")
    mirror = observation["activegraph"]
    if mirror is not None and (
        mirror["state"] != observation["graph"]["state"]
        or mirror["digest"] != observation["graph"]["digest"]
    ):
        contradictions.append("ACTIVEGRAPH_WORK_GRAPH_CONTRADICTION")

    packet_events = {row["event_id"]: row for row in packet["process"]["instruction_events"]}
    observed_events = {row["event_id"]: row for row in observation["instruction_events"]}
    for identity, row in packet_events.items():
        if observed_events.get(identity) != row:
            contradictions.append("INSTRUCTION_EVENT_MISMATCH")
            break
    extra_events = [
        row for identity, row in observed_events.items() if identity not in packet_events
    ]
    if any(row["disposition"] != "NEW" for row in extra_events):
        contradictions.append("INSTRUCTION_EVENT_MISMATCH")
    consumed = sorted(
        identity for identity, row in observed_events.items()
        if identity in packet_events and row["disposition"] == "CONSUMED"
    )
    admitted = sorted(row["event_id"] for row in extra_events if row["disposition"] == "NEW")

    unresolved = packet["evidence"]["unresolved_evidence_id"]
    query_result = observation["query_result"]
    query_needed = unresolved is not None and query_result is None
    if unresolved is None and query_result is not None:
        contradictions.append("UNREQUESTED_HISTORY_RESULT")
    elif unresolved is not None and query_result is not None and not query_result_is_usable(
            query_result, unresolved, packet):
        contradictions.append("HISTORY_QUERY_RESULT_NOT_DECISION_USABLE")

    same_context = observation["receiver"]["context_id"] == packet["process"]["context_id"]
    if same_context and not (
        observation["receiver"]["interrupted_cognition"] is True
        and observation["receiver"]["headroom_sufficient"] is True
    ):
        contradictions.append("SAME_CONTEXT_NOT_RESUMABLE")

    recovered = {
        "controller": copy.deepcopy(packet["controller"]),
        "target": copy.deepcopy(packet["target"]),
        "graph": copy.deepcopy(packet["graph"]),
        "authorized_files": list(packet["authority"]["authorized_files"]),
        "authorized_effects": list(packet["authority"]["authorized_effects"]),
        "result_disposition": packet["process"]["result_disposition"],
        "active_constraints": list(packet["process"]["active_constraints"]),
        "evidence_pointers": list(packet["evidence"]["pointers"]),
        "focused_tests": list(packet["evidence"]["focused_tests"]),
        "next_action": packet["continuation"]["next_action"],
        "stop_conditions": list(packet["continuation"]["stop_conditions"]),
        "return_schema": packet["continuation"]["return_schema"],
    }
    blocking = [
        item for item in contradictions
        if item != "ACTIVEGRAPH_WORK_GRAPH_CONTRADICTION"
    ]
    history_query = None
    if blocking:
        classifier = "REPORT_AND_WAIT"
    elif query_needed:
        classifier = "QUERY_HISTORY_THEN_RESUME"
        history_query = {
            "schema": "implementaudit.history-query-request.v1",
            "route": "QUERY_HISTORY_THEN_RESUME",
            "requirement": "REQUIRED",
            "evidence_ids": [unresolved],
        }
    elif same_context:
        classifier = "SAME_CONTEXT_RESUME"
    else:
        classifier = "FRESH_CONTEXT_RESUME"
    return {
        "schema": CLASSIFICATION_SCHEMA,
        "classifier": classifier,
        "packet_digest": packet["packet_digest"],
        "recovered": recovered,
        "instruction_events": {"consumed": consumed, "admitted": admitted},
        "subagent_observations": copy.deepcopy(observation["subagent_observations"]),
        "history_query": history_query,
        "contradictions": sorted(set(contradictions)),
        "authority_ceiling": AUTHORITY_CEILING,
        "establishes": [],
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="build one immutable bounded packet")
    build.add_argument("--input", required=True, type=pathlib.Path)
    classify_parser = sub.add_parser("classify", help="classify one current observation")
    classify_parser.add_argument("--packet", required=True, type=pathlib.Path)
    classify_parser.add_argument("--observation", required=True, type=pathlib.Path)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "build":
            output = build_packet(load_json(args.input))
        else:
            output = classify(load_json(args.packet), load_json(args.observation))
    except ContinuationError as exc:
        print(
            canonical_json({
                "schema": "implementaudit.bounded-continuation-error.v1",
                "code": exc.code,
                "path": exc.path,
                "message": exc.message,
                "authority_ceiling": AUTHORITY_CEILING,
                "establishes": [],
            }).decode("utf-8"),
            file=sys.stderr,
        )
        return 2
    print(canonical_json(output).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
