#!/usr/bin/env python3
"""Deterministic canonical whole-pair projection and protected-state algebra.

Unknown source grammar, incomplete owners and semantic changes refuse. Native
admission, boundary authenticity and publication remain owned by claim-run.
"""
from __future__ import annotations
from typing import Mapping, Sequence

import copy as _v2_copy_module
import hashlib as _v2_hashlib
import json as _v2_json_module
import re as _v2_re


class ProjectionV2Error(ValueError):
    """A complete source/projection contract could not be established."""


_V2_AUTHORITY = "NO_CURRENTNESS_AUTHORITY"
_V2_BODY_SCHEMA = "implementaudit.canonical-pair.v2"
_V2_TRANSITION_SCHEMA = "implementaudit.canonical-state-transition.v2"
_V2_NATIVE_RESUME_SCHEMA = "implementaudit.native-resume-transition.v1"
_V2_POINTER_SCHEMA = "implementaudit.typed-archive-pointer.v2"
_V2_OWNERS = {"STATE.md", "ROADMAP.md", "claim-run.sh", "WORK_GRAPH.json", "R0033/continuity"}
_V2_GROUP_OWNERS = {
    "STATE": {"identity": "claim-run.sh", "continuation": "STATE.md",
              "instructions": "STATE.md", "authorisations": "STATE.md",
              "terminal": "STATE.md", "andons": "STATE.md", "original_reds": "STATE.md",
              "non_verdicts": "STATE.md", "evidence_ceilings": "STATE.md", "steers": "STATE.md",
              "rollback": "STATE.md", "runtime_artifacts": "STATE.md",
              "pending_boundaries": "R0033/continuity"},
    "ROADMAP": {"frontier": "WORK_GRAPH.json", "obligations": "ROADMAP.md",
                "deferrals": "ROADMAP.md", "dependencies": "ROADMAP.md",
                "compensations": "ROADMAP.md", "planning": "ROADMAP.md"},
}
_V2_BODY_KEYS = {"schema_version", "role", "pair_id", "payload", "continuity", "history",
                 "archive_pointers", "artifact_refs", "transition"}
_V2_CONTINUITY_KEYS = {"projection_generation_id", "continuity_epoch", "invalidation_oid",
                       "predecessor_receipt_ref_oid", "expected_receipt_ref", "expected_receipt_schema",
                       "boundary", "reconciled"}
_V2_TRANSITION_KEYS = _V2_CONTINUITY_KEYS | {
    "schema_version", "boundary", "predecessor_generation_id", "predecessor_epoch",
    "transition_kind", "failed_transition_epoch", "failed_projection_generation_id", "failed_transition_receipt_ref_oid"}
_V2_MAP_KEYS = {"field", "owner", "source_kind", "source_id", "source_pointer", "source_sha256", "value_sha256"}
_V2_DESCRIPTOR_KEYS = {"role", "source_role", "source_pointer", "source_sha256", "source_bytes",
                        "blob_oid", "record_id", "record_sha256", "owner"}
_V2_POINTER_KEYS = _V2_DESCRIPTOR_KEYS | {"schema_version", "archive_ref", "archive_manifest_oid",
                                         "archive_manifest_sha256", "authority", "preparation_generation_id"}
_V2_PREIMAGE_KEYS = {"schema_version", "authority_ceiling", "state_bytes", "roadmap_bytes", "bodies",
                     "payload", "owner_map", "artifacts", "source_hashes", "current_continuity",
                     "current_receipt_ref_oid", "archive_population", "protected_manifest"}
_V2_CANDIDATE_KEYS = {"schema_version", "authority_ceiling", "state_bytes", "roadmap_bytes", "payload",
                      "source_hashes", "owner_map", "artifact_refs", "predecessor_continuity", "transition",
                      "archive_pointers", "protected_manifest", "limits"}
_V2_RECORD_STATES = {"OPEN", "BLOCKED", "DONE", "DEFERRED", "UNVERIFIED", "PRESERVED", "ACTIVE",
                      "SATISFIED", "EXPIRED", "SUPERSEDED", "REVOKED", "UNRESOLVED"}
_V2_BOUNDARIES = {"host-reported-compaction", "new-session", "handoff-resume", "manual-resume",
                   "inferred-context-gap", "canonical-state-rotation"}
_V2_NATIVE_BOUNDARIES = _V2_BOUNDARIES - {"canonical-state-rotation"}
_V2_HISTORY_KINDS = {"finding.closed", "andon.closed", "residual.terminal", "epoch.closed",
                      "instruction.satisfied", "phase.completed", "transition.closed",
                      "recovery.record", "artifact.historical"}


def _v2_require(condition: object, message: str) -> None:
    if not condition:
        raise ProjectionV2Error(message)


def _v2_object(value: object, keys: set[str], label: str) -> Mapping[str, object]:
    _v2_require(isinstance(value, Mapping) and set(value) == keys, label + " has missing or unknown fields")
    return value


def _v2_string(value: object, label: str, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    _v2_require(type(value) is str and bool(value) and "\0" not in value, label + " must be a nonempty string")
    try:
        value.encode("utf-8", "strict")
    except UnicodeError as exc:
        raise ProjectionV2Error(label + " is not valid UTF-8") from exc


def _v2_enum(value: object, choices: set[str], label: str) -> None:
    _v2_require(type(value) is str and value in choices, label + " is outside its closed vocabulary")


def _v2_integer(value: object, label: str, minimum: int = 0) -> None:
    _v2_require(type(value) is int and value >= minimum, label + " must be an integer in range")


def _v2_list(value: object, label: str) -> Sequence[object]:
    _v2_require(type(value) in (list, tuple), label + " must be a sequence")
    return value


def _v2_strings(value: object, label: str) -> None:
    rows = _v2_list(value, label)
    for row in rows:
        _v2_string(row, label)
    _v2_require(len(set(rows)) == len(rows), label + " contains duplicates")


def _v2_digest(value: object, label: str, *, oid: bool = False, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    pattern = r"(?:[0-9a-f]{40}|[0-9a-f]{64})" if oid else r"[0-9a-f]{64}"
    _v2_require(type(value) is str and _v2_re.fullmatch(pattern, value) is not None,
                label + " has an invalid digest")


def _v2_epoch(value: object) -> int:
    _v2_require(type(value) is str and _v2_re.fullmatch(r"G[0-9A-F]{4}", value) is not None,
                "epoch/generation must be exact uppercase Gxxxx")
    number = int(value[1:], 16)
    _v2_require(number > 0, "epoch/generation zero is outside the qualified grammar")
    return number


def _v2_next(value: str, increment: int = 1) -> str:
    number = _v2_epoch(value) + increment
    _v2_require(number <= 65535, "epoch/generation namespace exhausted")
    return "G%04X" % number


def _v2_data(value: object) -> object:
    if value is None or type(value) in (bool, int, str):
        if type(value) is str:
            _v2_require("\0" not in value, "NUL is not admitted in canonical JSON")
        return value
    if isinstance(value, Mapping):
        _v2_require(all(type(key) is str for key in value), "canonical JSON keys must be strings")
        return {key: _v2_data(child) for key, child in value.items()}
    if type(value) in (list, tuple):
        return [_v2_data(child) for child in value]
    raise ProjectionV2Error("canonical JSON excludes floats and unsupported values")


def _v2_canonical(value: object) -> bytes:
    try:
        return _v2_json_module.dumps(_v2_data(value), sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode("utf-8", "strict")
    except (UnicodeError, TypeError, OverflowError, RecursionError) as exc:
        raise ProjectionV2Error("value cannot be encoded as canonical JSON") from exc


def _v2_sha(raw: bytes) -> str:
    return _v2_hashlib.sha256(raw).hexdigest()


def _v2_blob(raw: bytes, algorithm: str = "sha1") -> str:
    return _v2_hashlib.new(algorithm, b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _v2_clone(value: object) -> object:
    return _v2_copy_module.deepcopy(value)


def _v2_same(left: object, right: object) -> bool:
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        return set(left) == set(right) and all(_v2_same(left[key], right[key]) for key in left)
    if type(left) is not type(right):
        return False
    if type(left) in (list, tuple):
        return len(left) == len(right) and all(_v2_same(a, b) for a, b in zip(left, right))
    return left == right


def _v2_pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _v2_leaves(value: object, pointer: str):
    if isinstance(value, Mapping) and value:
        for key in sorted(value):
            yield from _v2_leaves(value[key], pointer + "/" + _v2_pointer_escape(key))
    elif type(value) in (list, tuple) and value:
        for index, child in enumerate(value):
            yield from _v2_leaves(child, pointer + "/" + str(index))
    else:
        yield pointer, value


def _v2_safe_path(value: object) -> None:
    _v2_string(value, "artifact locator")
    _v2_require(not any(char in value for char in "\\:\r\n\t")
                and all(part not in ("", ".", "..") for part in value.split("/")),
                "artifact locator is not a contained relative POSIX path")


def _v2_records(value: object, keys: set[str], label: str) -> Sequence[Mapping[str, object]]:
    rows = _v2_list(value, label)
    seen = set()
    for row in rows:
        _v2_object(row, keys, label)
        _v2_string(row["record_id"], label + " record_id")
        _v2_require(row["record_id"] not in seen, label + " record_id duplicated")
        seen.add(row["record_id"])
        if "evidence_refs" in row:
            _v2_strings(row["evidence_refs"], label + " evidence_refs")
    return rows


def _v2_instruction_rows(value: object) -> None:
    rows = _v2_records(value, {"record_id", "issuer", "subject", "scope", "applicability", "status",
                               "evidence_refs", "issued_epoch", "expires_at", "supersedes"}, "instruction")
    for row in rows:
        for key in ("issuer", "subject", "scope"):
            _v2_string(row[key], "instruction " + key)
        _v2_enum(row["applicability"], {"APPLIES", "DOES_NOT_APPLY", "UNRESOLVED"}, "applicability")
        _v2_enum(row["status"], {"ACTIVE", "SATISFIED", "SUPERSEDED", "REVOKED", "EXPIRED", "AMBIGUOUS"}, "instruction status")
        _v2_epoch(row["issued_epoch"])
        _v2_string(row["expires_at"], "instruction expires_at", nullable=True)
        _v2_strings(row["supersedes"], "instruction supersedes")


def _v2_general_rows(value: object, *, deferred: bool = False) -> None:
    keys = {"record_id", "status", "description", "scope", "evidence_refs"}
    if deferred:
        keys.add("revisit_trigger")
    for row in _v2_records(value, keys, "protected record"):
        _v2_enum(row["status"], {"DEFERRED", "READY", "DONE", "BLOCKED"} if deferred else _V2_RECORD_STATES,
                  "protected status")
        for key in ("description", "scope") + (("revisit_trigger",) if deferred else ()):
            _v2_string(row[key], "protected " + key)


def _v2_acyclic(edges: Mapping[str, Sequence[str]], label: str) -> None:
    """Check a closed relation without imposing a recursive depth/census cap."""
    incoming = {record_id: 0 for record_id in edges}
    for targets in edges.values():
        for target in targets:
            incoming[target] += 1
    ready = [record_id for record_id, count in incoming.items() if count == 0]
    visited = 0
    while ready:
        record_id = ready.pop()
        visited += 1
        for target in edges[record_id]:
            incoming[target] -= 1
            if incoming[target] == 0:
                ready.append(target)
    _v2_require(visited == len(edges), label + " contains a cycle")


def _v2_relations(payload: Mapping[str, object]) -> None:
    """Bind relational fields to the complete typed protected populations."""
    records = {}
    pending = [payload]
    while pending:
        value = pending.pop()
        if isinstance(value, Mapping):
            if "record_id" in value:
                _v2_require(value["record_id"] not in records, "protected record identity is ambiguous")
                records[value["record_id"]] = value
            pending.extend(value.values())
        elif type(value) in (list, tuple):
            pending.extend(value)
    state, roadmap = payload["STATE"], payload["ROADMAP"]
    instruction_rows = list(state["instructions"]["value"]) + list(state["authorisations"]["value"])
    instructions = {row["record_id"]: row for row in instruction_rows}
    supersession = {}
    for record_id, row in instructions.items():
        _v2_require(set(row["supersedes"]) <= set(instructions), "supersession target is not an instruction/authorisation record")
        _v2_require(record_id not in row["supersedes"], "instruction/authorisation supersedes itself")
        supersession[record_id] = row["supersedes"]
    _v2_acyclic(supersession, "supersession")
    compensations = {row["record_id"]: row for row in roadmap["compensations"]["value"]}
    compensation_edges = {}
    for record_id, row in compensations.items():
        subject = row["for_record"]
        _v2_require(subject in records and subject != record_id, "compensation subject is missing or self-referential")
        compensation_edges[record_id] = [subject] if subject in compensations else []
    _v2_acyclic(compensation_edges, "compensation")
    action = roadmap["planning"]["value"]["action_selection"]
    _v2_require(not set(action["selected"]) & set(action["omitted"]), "action is both selected and omitted")


def _v2_pending_rows(value: object) -> None:
    rows = _v2_list(value, "pending boundaries")
    keys = {"boundary_id", "boundary_kind", "owner", "original_evidence_ref", "original_evidence_locator",
            "physical_source", "observation", "reservation", "result", "consumption", "uncovered_successors",
            "historical_refusal", "currentness", "selected_occurrence_id", "prior_occurrence_ids", "retry",
            "completed", "audit_state_required"}
    seen = set()
    for row in rows:
        _v2_object(row, keys, "pending boundary")
        _v2_string(row["boundary_id"], "boundary_id")
        _v2_require(row["boundary_id"] not in seen, "boundary_id duplicated")
        seen.add(row["boundary_id"])
        _v2_enum(row["boundary_kind"], _V2_BOUNDARIES, "boundary kind")
        _v2_require(row["owner"] == "R0033/continuity", "pending boundary owner changed")
        _v2_string(row["original_evidence_ref"], "original evidence ref")
        _v2_safe_path(row["original_evidence_locator"])
        source = _v2_object(row["physical_source"], {"file_identity", "offset", "byte_length", "sha256", "ordinal", "source_binding"}, "physical source")
        _v2_safe_path(source["file_identity"])
        _v2_require(source["file_identity"] == row["original_evidence_locator"], "physical source locator changed")
        for key, minimum in (("offset", 0), ("byte_length", 1), ("ordinal", 1)):
            _v2_integer(source[key], "physical " + key, minimum)
        _v2_digest(source["sha256"], "physical source slice")
        _v2_digest(source["source_binding"], "physical source binding")
        observation = _v2_object(row["observation"], {"scope", "cutoff", "boundary_ids"}, "observation")
        _v2_string(observation["scope"], "observation scope")
        _v2_integer(observation["cutoff"], "observation cutoff")
        _v2_strings(observation["boundary_ids"], "observed boundary ids")
        _v2_require(row["boundary_id"] in observation["boundary_ids"], "boundary missing from its observation")
        reservation = _v2_object(row["reservation"], {"state", "owner_ref"}, "reservation")
        _v2_enum(reservation["state"], {"UNRESERVED", "RESERVED", "RELEASED"}, "reservation state")
        _v2_string(reservation["owner_ref"], "reservation owner", nullable=reservation["state"] != "RESERVED")
        result = _v2_object(row["result"], {"state", "original_response_sha256", "returned_response_sha256"}, "boundary result")
        _v2_enum(result["state"], {"PENDING", "FAILED", "SUCCEEDED"}, "boundary result")
        for key in ("original_response_sha256", "returned_response_sha256"):
            _v2_digest(result[key], key, nullable=True)
        consumption = _v2_object(row["consumption"], {"state", "witness", "covered_boundary_ids"}, "consumption")
        _v2_enum(consumption["state"], {"PENDING", "ACCEPTED", "REFUSED"}, "consumption state")
        _v2_strings(consumption["covered_boundary_ids"], "consumed boundary ids")
        _v2_require(set(consumption["covered_boundary_ids"]) <= set(observation["boundary_ids"]), "consumption exceeds observation")
        if consumption["state"] == "ACCEPTED":
            _v2_require(result["state"] == "SUCCEEDED" and bool(consumption["covered_boundary_ids"]),
                        "reservation or failed result cannot consume a boundary")
            witness = _v2_object(consumption["witness"], {"evidence_ref", "sha256", "observation_scope", "cutoff", "boundary_ids"}, "accepted witness")
            _v2_string(witness["evidence_ref"], "accepted witness evidence")
            _v2_digest(witness["sha256"], "accepted witness digest")
            _v2_integer(witness["cutoff"], "witness cutoff")
            _v2_strings(witness["boundary_ids"], "witness boundary ids")
            _v2_require(witness["observation_scope"] == observation["scope"] and witness["cutoff"] == observation["cutoff"]
                        and witness["boundary_ids"] == consumption["covered_boundary_ids"], "accepted witness scope changed")
        else:
            _v2_require(consumption["witness"] is None and consumption["covered_boundary_ids"] == [],
                        "unaccepted consumption has a witness or covered population")
        _v2_strings(row["uncovered_successors"], "uncovered successors")
        _v2_require(not set(row["uncovered_successors"]) & set(consumption["covered_boundary_ids"]), "covered successor also uncovered")
        refusal = _v2_object(row["historical_refusal"], {"state", "evidence_ref", "original_prefix_cutoff"}, "historical refusal")
        _v2_enum(refusal["state"], {"NONE", "PRESERVED", "ORIGINAL_PREFIX_REQUIRED"}, "historical refusal state")
        _v2_string(refusal["evidence_ref"], "historical refusal evidence", nullable=refusal["state"] == "NONE")
        if refusal["original_prefix_cutoff"] is not None:
            _v2_integer(refusal["original_prefix_cutoff"], "original prefix cutoff")
        _v2_require(refusal["state"] != "ORIGINAL_PREFIX_REQUIRED" or refusal["original_prefix_cutoff"] is not None,
                    "original-prefix refusal lost its cutoff")
        current = _v2_object(row["currentness"], {"state", "epoch"}, "pending currentness")
        _v2_enum(current["state"], {"CURRENT", "UNRESOLVED"}, "pending currentness state")
        if current["epoch"] is not None:
            _v2_epoch(current["epoch"])
        _v2_require(current["state"] != "CURRENT" or current["epoch"] is not None, "currentness lacks a bound epoch")
        _v2_string(row["selected_occurrence_id"], "selected occurrence")
        _v2_strings(row["prior_occurrence_ids"], "prior occurrences")
        retry = _v2_object(row["retry"], {"state", "original_occurrence_id", "supported_evidence_ref"}, "retry")
        _v2_enum(retry["state"], {"NONE", "ORIGINAL_OCCURRENCE", "SUPPORTED_RETRY"}, "retry state")
        _v2_string(retry["original_occurrence_id"], "retry original occurrence", nullable=retry["state"] == "NONE")
        _v2_string(retry["supported_evidence_ref"], "retry evidence", nullable=retry["state"] != "SUPPORTED_RETRY")
        _v2_require(type(row["completed"]) is bool and type(row["audit_state_required"]) is bool, "pending booleans must be exact")
        _v2_require(not (row["completed"] and row["boundary_kind"] == "host-reported-compaction") or row["audit_state_required"],
                    "completed host compaction must retain audit-state requirement, even when epoch/currentness unresolved")
    for row in rows:
        _v2_require(set(row["observation"]["boundary_ids"]) <= seen and set(row["uncovered_successors"]) <= seen,
                    "pending observation names an unmapped boundary")


def _v2_payload_schema(payload: object) -> None:
    _v2_object(payload, {"STATE", "ROADMAP"}, "protected pair payload")
    _v2_canonical(payload)
    native = [isinstance(payload[role], Mapping) and "native_guards" in payload[role] for role in ("STATE", "ROADMAP")]
    _v2_require(native[0] == native[1], "native guard profiles must bind the complete pair")
    for role, groups in _V2_GROUP_OWNERS.items():
        owners = dict(groups, native_guards=role + ".md") if native[0] else groups
        _v2_object(payload[role], set(owners), role + " payload")
        for name, owner in owners.items():
            group = _v2_object(payload[role][name], {"owner", "value"}, name)
            _v2_require(group["owner"] == owner, name + " native owner mismatch")
        if native[0]:
            profile = _v2_object(payload[role]["native_guards"]["value"], {"schema_version", "lines"}, "native guard profile")
            _v2_require(profile["schema_version"] == "implementaudit.native-guard-profile.v1", "native guard schema mismatch")
            lines = _v2_list(profile["lines"], "native guard lines")
            _v2_require(bool(lines) and all(type(line) is str and not any(c in line for c in "\r\n\0")
                        and not any(0xD800 <= ord(c) <= 0xDFFF for c in line) for line in lines),
                        "native guards require exact nonempty line population")
            _v2_require(not any(_v2_re.search(r"current\s+epoch\s*:", line, _v2_re.I) for line in lines),
                        "live native epoch is derived only from effective continuity")
    state = {key: group["value"] for key, group in payload["STATE"].items()}
    roadmap = {key: group["value"] for key, group in payload["ROADMAP"].items()}
    identity = _v2_object(state["identity"], {"controller_id", "claim_id", "run_root_identity", "audit_object", "candidate", "tree", "package", "pull_request", "release"}, "identity")
    for key in identity:
        _v2_string(identity[key], "identity " + key, nullable=key in {"pull_request", "release"})
    _v2_require(_v2_re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", identity["controller_id"]) is not None,
                "controller identity cannot form an exact ref")
    _v2_digest(identity["candidate"], "candidate", oid=True)
    _v2_digest(identity["tree"], "tree", oid=True)
    continuation = _v2_object(state["continuation"], {"phase", "status", "next_action", "route", "last_check"}, "continuation")
    for key in ("phase", "next_action", "last_check"):
        _v2_string(continuation[key], "continuation " + key)
    _v2_require(not any(char in continuation["next_action"] for char in "\r\n\t|"), "next action cannot be represented exactly in the frame/receipt")
    statuses = {"open", "READY_TO_DISPATCH", "IN_PHASE", "PAUSED", "BLOCKED", "INTERRUPTED", "DONE"} if native[0] else {"DONE", "ACTIVE", "READY", "BLOCKED"}
    _v2_enum(continuation["status"], statuses, "continuation status")
    if native[0]:
        lines = state["native_guards"]["lines"]
        for label, value in (("Status", continuation["status"]), ("Next action", continuation["next_action"])):
            near = [line for line in lines if _v2_re.match(r"\s*\|\s*" + label.replace(" ", r"\s+") + r"\s*(?:\||:)", line, _v2_re.I)]
            _v2_require(near == ["| " + label + " | " + value + " |"], "native " + label + " must be one exact protected mirror")
    _v2_enum(continuation["route"], {"ordinary", "recovery", "handoff"}, "continuation route")
    _v2_instruction_rows(state["instructions"])
    _v2_instruction_rows(state["authorisations"])
    terminal = _v2_object(state["terminal"], {"one_shots", "markers", "handoffs", "external_effects"}, "terminal")
    kinds = {"one_shots": "ONE_SHOT", "markers": "MARKER", "handoffs": "HANDOFF", "external_effects": "EXTERNAL_EFFECT"}
    for group, kind in kinds.items():
        for row in _v2_records(terminal[group], {"record_id", "kind", "status", "scope", "evidence_refs"}, "terminal record"):
            _v2_require(row["kind"] == kind, "terminal record kind mismatch")
            _v2_enum(row["status"], {"PLANNED", "PENDING", "ISSUED", "CONSUMED", "BLOCKED", "CANCELLED", "NOT_GRANTED"}, "terminal status")
            _v2_string(row["scope"], "terminal scope")
    for group in ("andons", "original_reds", "non_verdicts", "evidence_ceilings", "steers"):
        _v2_general_rows(state[group])
    rollback = _v2_object(state["rollback"], {"status", "target", "conditions", "evidence_refs"}, "rollback")
    _v2_enum(rollback["status"], {"AVAILABLE", "PENDING", "BLOCKED", "COMPLETED", "UNAVAILABLE"}, "rollback status")
    _v2_string(rollback["target"], "rollback target", nullable=True)
    _v2_strings(rollback["conditions"], "rollback conditions")
    _v2_strings(rollback["evidence_refs"], "rollback evidence")
    _v2_strings(state["runtime_artifacts"], "runtime artifacts")
    _v2_pending_rows(state["pending_boundaries"])
    frontier = _v2_object(roadmap["frontier"], {"DONE", "ACTIVE", "READY", "BLOCKED"}, "frontier")
    nodes = []
    for population in frontier.values():
        _v2_strings(population, "frontier nodes")
        nodes.extend(population)
    _v2_require(len(nodes) == len(set(nodes)), "frontier node occurs in more than one state")
    _v2_general_rows(roadmap["obligations"])
    _v2_general_rows(roadmap["deferrals"], deferred=True)
    for row in _v2_records(roadmap["dependencies"], {"record_id", "source", "target", "status", "evidence_refs"}, "dependency"):
        _v2_string(row["source"], "dependency source")
        _v2_string(row["target"], "dependency target")
        _v2_require(row["source"] in nodes and row["target"] in nodes, "dependency frontier node missing")
        _v2_enum(row["status"], {"OPEN", "SATISFIED", "BLOCKED", "INVALIDATED"}, "dependency status")
    for row in _v2_records(roadmap["compensations"], {"record_id", "for_record", "status", "description", "evidence_refs"}, "compensation"):
        _v2_string(row["for_record"], "compensation subject")
        _v2_string(row["description"], "compensation description")
        _v2_enum(row["status"], {"PENDING", "READY", "DONE", "BLOCKED"}, "compensation status")
    planning = _v2_object(roadmap["planning"], {"goal", "action_selection", "scope_boundaries", "baseline_ref"}, "planning")
    _v2_string(planning["goal"], "planning goal")
    _v2_string(planning["baseline_ref"], "planning baseline")
    _v2_strings(planning["scope_boundaries"], "scope boundaries")
    action = _v2_object(planning["action_selection"], {"selected", "omitted", "rationale"}, "action selection")
    _v2_strings(action["selected"], "selected actions")
    _v2_strings(action["omitted"], "omitted actions")
    _v2_string(action["rationale"], "action rationale")
    _v2_relations(payload)


def validate_protected_payload_v2(payload: Mapping[str, object],
                                  owner_map: Sequence[Mapping[str, object]]) -> dict[str, object]:
    """Validate complete typed groups and one owner/value row for every leaf.

    Whole-file hashes are checked by parse_canonical_pair_v2, which has their
    bytes. This standalone validator grants no source authenticity/currentness.
    """
    _v2_payload_schema(payload)
    expected = {}
    for role in ("STATE", "ROADMAP"):
        for name, group in payload[role].items():
            for pointer, value in _v2_leaves(group, "/payload/" + _v2_pointer_escape(name)):
                expected["/" + role + pointer] = (role, pointer, group["owner"], _v2_sha(_v2_canonical(value)))
    rows = _v2_list(owner_map, "owner map")
    seen = set()
    hashes = {}
    for row in rows:
        _v2_object(row, _V2_MAP_KEYS, "owner map row")
        _v2_string(row["field"], "owner map field")
        _v2_require(row["field"] not in seen and row["field"] in expected, "owner map is duplicate, missing or extra")
        seen.add(row["field"])
        role, pointer, owner, value_hash = expected[row["field"]]
        _v2_require(row["source_kind"] == "PAIR" and row["source_id"] == role and row["source_pointer"] == pointer
                    and row["owner"] == owner and row["value_sha256"] == value_hash, "owner map leaf binding mismatch")
        _v2_digest(row["source_sha256"], "owner source hash")
        _v2_require(role not in hashes or hashes[role] == row["source_sha256"], "one source has conflicting full-file hashes")
        hashes[role] = row["source_sha256"]
    _v2_require(seen == set(expected), "owner map omits a protected leaf")
    return {"schema_version": "implementaudit.protected-payload-validation.v2", "authority_ceiling": _V2_AUTHORITY,
            "payload": _v2_clone(payload), "owner_map": sorted(_v2_clone(list(rows)), key=lambda row: row["field"]),
            "leaf_count": len(expected)}


def _v2_receipt_ref(controller: str, epoch: str) -> str:
    return "refs/implementaudit/continuity-receipts/" + controller + "/" + epoch


def _v2_receipt_token(value: object, controller: str, *, epoch: str | None = None,
                       nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    _v2_require(type(value) is str and value.count("@") == 1, "receipt token must be exact ref@oid")
    ref, oid = value.split("@")
    _v2_digest(oid, "receipt token object", oid=True)
    prefix = "refs/implementaudit/continuity-receipts/" + controller + "/"
    _v2_require(ref.startswith(prefix), "receipt token controller scope mismatch")
    token_epoch = ref[len(prefix):]
    _v2_epoch(token_epoch)
    _v2_require(epoch is None or token_epoch == epoch, "receipt token epoch scope mismatch")
    return token_epoch


def _v2_continuity(value: object, controller: str) -> None:
    _v2_object(value, _V2_CONTINUITY_KEYS, "predecessor continuity")
    _v2_epoch(value["projection_generation_id"])
    number = _v2_epoch(value["continuity_epoch"])
    _v2_digest(value["invalidation_oid"], "predecessor invalidation", oid=True, nullable=number == 1)
    previous = _v2_receipt_token(value["predecessor_receipt_ref_oid"], controller, nullable=number == 1)
    _v2_require(previous is None or _v2_epoch(previous) < number, "predecessor receipt does not precede source epoch")
    _v2_enum(value["boundary"], _V2_BOUNDARIES, "source continuity boundary")
    _v2_require(value["reconciled"] is True, "source reconciliation must be an explicit true fact")
    _v2_enum(value["expected_receipt_schema"], {"implementaudit.continuity-receipt.v2", "implementaudit.continuity-receipt.v3"}, "receipt schema")
    _v2_require(value["expected_receipt_ref"] == _v2_receipt_ref(controller, value["continuity_epoch"]), "receipt ref scope mismatch")


def _v2_transition(value: object, current: Mapping[str, object], controller: str,
                    receipt_oid: str | None = None) -> None:
    _v2_object(value, _V2_TRANSITION_KEYS, "successor transition")
    if value["transition_kind"] == "native-resume":
        _v2_require(value["schema_version"] == _V2_NATIVE_RESUME_SCHEMA
                    and current["expected_receipt_schema"] == "implementaudit.continuity-receipt.v3",
                    "native resume requires the original native boundary and migrated predecessor")
        _v2_enum(value["boundary"], _V2_NATIVE_BOUNDARIES, "native resume boundary")
    else:
        _v2_require(value["schema_version"] == _V2_TRANSITION_SCHEMA and value["boundary"] == "canonical-state-rotation",
                    "successor schema/boundary mismatch")
        _v2_enum(value["transition_kind"], {"rotation", "recovery"}, "transition kind")
    _v2_require(value["reconciled"] is True, "transition reconciliation must be owner-supplied true")
    recovery = value["transition_kind"] == "recovery"
    _v2_require(value["predecessor_generation_id"] == current["projection_generation_id"]
                and value["predecessor_epoch"] == current["continuity_epoch"], "successor predecessor mismatch")
    for field, source in (("projection_generation_id", "projection_generation_id"), ("continuity_epoch", "continuity_epoch")):
        _v2_require(value[field] == _v2_next(current[source], 2 if recovery else 1), "successor skips or reuses a generation/epoch")
    _v2_require(value["failed_transition_epoch"] == (_v2_next(current["continuity_epoch"]) if recovery else None)
                and value["failed_projection_generation_id"] == (_v2_next(current["projection_generation_id"]) if recovery else None),
                "recovery lacks the exact separately recorded failed allocation")
    _v2_digest(value["invalidation_oid"], "successor invalidation", oid=True)
    _v2_require(value["invalidation_oid"] != current["invalidation_oid"], "successor reuses old invalidation")
    failed_receipt = value["failed_transition_receipt_ref_oid"]
    _v2_require(recovery or failed_receipt is None, "non-recovery transition cannot name a failed receipt")
    if failed_receipt is not None:
        _v2_receipt_token(failed_receipt, controller, epoch=value["failed_transition_epoch"])
        _v2_require(value["predecessor_receipt_ref_oid"] == failed_receipt,
                    "recovery predecessor is not the exact actual failed receipt token")
    else:
        _v2_receipt_token(value["predecessor_receipt_ref_oid"], controller, epoch=current["continuity_epoch"])
        if receipt_oid is not None:
            _v2_require(value["predecessor_receipt_ref_oid"] == receipt_oid, "successor fabricates/substitutes predecessor receipt")
    _v2_require(value["expected_receipt_ref"] == _v2_receipt_ref(controller, value["continuity_epoch"])
                and value["expected_receipt_schema"] == "implementaudit.continuity-receipt.v3", "successor receipt expectation mismatch")


def _v2_effective(body: Mapping[str, object]) -> dict[str, object]:
    source = body["transition"] if body["transition"] is not None else body["continuity"]
    return {key: _v2_clone(source[key]) for key in _V2_CONTINUITY_KEYS}


def _v2_render(body: Mapping[str, object], action: str, identity: Mapping[str, object]) -> bytes:
    current = _v2_effective(body)
    text = ("# IMPLEMENTAUDIT " + body["role"].title() + "\n\nCurrent epoch: " + current["continuity_epoch"]
            + "\nCanonical projection generation: " + current["projection_generation_id"]
            + "\n\n| Field | Value |\n|---|---|\n| Next action | " + action + " |\n\n"
            + "## Context epochs and instruction applicability\n\n"
            + "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n"
            + "|---|---|---|---|---|---|\n| " + current["continuity_epoch"] + " | " + current["boundary"]
            + " | not measured | `" + identity["candidate"] + "` / `" + identity["tree"]
            + "` | yes | exact source facts |\n\n```json\n")
    return text.encode("utf-8") + _v2_canonical(body) + b"\n```\n"


def _v2_load_body(raw: object, role: str) -> Mapping[str, object]:
    _v2_require(type(raw) is bytes and b"\r" not in raw and not raw.startswith(b"\xef\xbb\xbf"),
                "canonical source must be BOM-free UTF-8 LF bytes")
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeError as exc:
        raise ProjectionV2Error("canonical source is not UTF-8") from exc
    lines = text.split("\n")
    _v2_require(len(lines) == 19 and lines[15] == "```json" and lines[17:] == ["```", ""],
                "unsupported or incomplete canonical whole-file grammar")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            _v2_require(key not in result, "duplicate canonical JSON key")
            result[key] = value
        return result
    def forbidden(_):
        raise ProjectionV2Error("canonical JSON does not admit floats/constants")
    try:
        body = _v2_json_module.loads(lines[16], object_pairs_hook=unique, parse_float=forbidden, parse_constant=forbidden)
    except (ValueError, RecursionError) as exc:
        raise ProjectionV2Error("canonical JSON body is invalid") from exc
    _v2_object(body, _V2_BODY_KEYS, "canonical body")
    _v2_require(body["schema_version"] == _V2_BODY_SCHEMA and body["role"] == role, "canonical schema/role mismatch")
    _v2_string(body["pair_id"], "pair identity")
    _v2_require(_v2_canonical(body).decode("utf-8") == lines[16], "JSON body is not canonical exact bytes")
    return body


def _v2_history(value: object) -> None:
    for row in _v2_records(value, {"record_id", "record_kind", "owner", "status", "payload"}, "typed history"):
        _v2_enum(row["record_kind"], _V2_HISTORY_KINDS, "history kind")
        _v2_enum(row["owner"], _V2_OWNERS, "history owner")
        _v2_enum(row["status"], {"PRESERVED", "CLOSED", "SATISFIED", "EXPIRED", "SUPERSEDED"}, "history status")
        data = _v2_object(row["payload"], {"text", "evidence_refs", "original_scope", "current_applicability", "historical_refusal"}, "history payload")
        _v2_string(data["text"], "history text")
        _v2_strings(data["evidence_refs"], "history evidence")
        _v2_string(data["original_scope"], "history original scope")
        _v2_enum(data["current_applicability"], {"UNCHANGED", "INVALIDATED_CURRENT_USE"}, "history current applicability")
        _v2_string(data["historical_refusal"], "history refusal", nullable=data["current_applicability"] == "UNCHANGED")


def _v2_archive_pointer(row: object, controller: str) -> None:
    _v2_object(row, _V2_POINTER_KEYS, "typed archive pointer")
    _v2_require(row["schema_version"] == _V2_POINTER_SCHEMA and row["authority"] == "ARCHIVED_ONLY_HISTORY", "archive pointer authority/schema mismatch")
    _v2_enum(row["source_role"], {"STATE", "ROADMAP"}, "archive source role")
    _v2_enum(row["role"], {"STATE_PREIMAGE", "ROADMAP_PREIMAGE", "HISTORY_RECORD"}, "archive record role")
    _v2_enum(row["owner"], _V2_OWNERS, "archive record owner")
    _v2_string(row["record_id"], "archive record identity")
    _v2_epoch(row["preparation_generation_id"])
    _v2_require(row["archive_ref"] == "refs/implementaudit/state-archives/" + controller + "/" + row["preparation_generation_id"],
                "archive ref is not the exact prepared generation scope")
    for key in ("source_sha256", "record_sha256", "archive_manifest_sha256"):
        _v2_digest(row[key], key)
    for key in ("blob_oid", "archive_manifest_oid"):
        _v2_digest(row[key], key, oid=True)
    _v2_integer(row["source_bytes"], "archive source bytes", 1)
    if row["role"] == "HISTORY_RECORD":
        _v2_require(type(row["source_pointer"]) is str and _v2_re.fullmatch(r"/history/(?:0|[1-9][0-9]*)", row["source_pointer"]) is not None,
                    "history source pointer is not exact")
    else:
        _v2_require(row["role"] == row["source_role"] + "_PREIMAGE" and row["source_pointer"] == ""
                    and row["record_id"] == row["source_role"] + ".md" and row["owner"] == row["record_id"]
                    and row["record_sha256"] == row["source_sha256"], "whole-pair archive descriptor mismatch")


def _v2_existing_archives(bodies: Mapping[str, object], controller: str) -> list[dict[str, object]]:
    population = {}
    for role in ("STATE", "ROADMAP"):
        rows = _v2_list(bodies[role]["archive_pointers"], "existing archives")
        seen = set()
        for row in rows:
            _v2_archive_pointer(row, controller)
            identity = _v2_canonical(row)
            _v2_require(identity not in seen, "duplicate existing archive within one source")
            seen.add(identity)
            population[identity] = _v2_clone(row)
    return [population[key] for key in sorted(population)]


def _v2_artifact_refs(bodies: Mapping[str, object], controller: str, current: Mapping[str, object]) -> list[dict[str, object]]:
    refs = {}
    roles = {"CONTINUITY_RECEIPT": [], "WORK_GRAPH": [], "EVIDENCE": []}
    for role in ("STATE", "ROADMAP"):
        for row in _v2_list(bodies[role]["artifact_refs"], "artifact declarations"):
            _v2_object(row, {"artifact_id", "owner", "role", "locator", "object_format"}, "artifact declaration")
            _v2_string(row["artifact_id"], "artifact identity")
            _v2_require(_v2_re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", row["artifact_id"]) is not None,
                        "artifact identity cannot form an exact owner field")
            _v2_require(row["artifact_id"] not in refs, "duplicate artifact declaration")
            _v2_enum(row["owner"], _V2_OWNERS, "artifact owner")
            _v2_enum(row["role"], set(roles), "artifact role")
            _v2_enum(row["object_format"], {"sha1", "sha256"}, "artifact object format")
            if row["role"] == "CONTINUITY_RECEIPT":
                _v2_require(row["owner"] == "claim-run.sh" and row["locator"] == current["expected_receipt_ref"], "receipt artifact owner/ref mismatch")
            else:
                _v2_safe_path(row["locator"])
                if row["role"] == "WORK_GRAPH":
                    _v2_require(row["owner"] == "WORK_GRAPH.json" and row["locator"] == "WORK_GRAPH.json", "WORK_GRAPH owner/locator mismatch")
            refs[row["artifact_id"]] = _v2_clone(row)
            roles[row["role"]].append(row["artifact_id"])
    _v2_require(len(roles["CONTINUITY_RECEIPT"]) == len(roles["WORK_GRAPH"]) == 1, "exactly one receipt and WORK_GRAPH dependency required")
    return [refs[key] for key in sorted(refs)]


def _v2_check_references(value: object, ids: set[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key == "evidence_refs":
                _v2_strings(child, "evidence references")
                _v2_require(set(child) <= ids, "undeclared evidence dependency")
            elif key in {"evidence_ref", "original_evidence_ref", "supported_evidence_ref"} and child is not None:
                _v2_require(type(child) is str and child in ids, "undeclared singular evidence dependency")
            _v2_check_references(child, ids)
    elif type(value) in (list, tuple):
        for child in value:
            _v2_check_references(child, ids)


def _v2_receipt(raw: bytes, current: Mapping[str, object], identity: Mapping[str, object],
                hashes: Mapping[str, str], action: str) -> None:
    _v2_require(type(raw) is bytes and raw.endswith(b"\n") and raw.count(b"\n") == 1 and b"\r" not in raw and b"\0" not in raw,
                "receipt is not exact single-LF native wire bytes")
    try:
        fields = raw[:-1].decode("utf-8", "strict").split("\t")
    except UnicodeError as exc:
        raise ProjectionV2Error("receipt is not UTF-8") from exc
    schema = current["expected_receipt_schema"]
    _v2_require(fields[0] == schema, "receipt schema changed")
    if schema == "implementaudit.continuity-receipt.v2":
        _v2_require(len(fields) == 12, "v2 receipt field population mismatch")
        _v2_digest(fields[2], "controller object", oid=True)
        _v2_require(fields[1] == identity["controller_id"] and fields[3] == identity["claim_id"]
                    and fields[4] == identity["candidate"] and fields[5] == identity["tree"]
                    and fields[6] == hashes["STATE"] and fields[7] == hashes["ROADMAP"]
                    and fields[8] == (current["invalidation_oid"] or "none") and fields[9] == current["boundary"]
                    and fields[10] == current["continuity_epoch"] and fields[11] == action, "v2 receipt source binding mismatch")
    else:
        _v2_require(len(fields) == 14, "v3 receipt field population mismatch")
        _v2_require(fields[1] == identity["controller_id"] and fields[2] == identity["claim_id"]
                    and fields[3] == identity["run_root_identity"] and fields[4] == current["continuity_epoch"]
                    and fields[5] == current["invalidation_oid"] and fields[8] == hashes["STATE"]
                    and fields[9] == hashes["ROADMAP"] and fields[12] == action
                    and fields[13] == current["predecessor_receipt_ref_oid"], "v3 receipt source binding mismatch")
        _v2_require(fields[6] == "refs/implementaudit/current-generations/" + identity["controller_id"],
                    "v3 receipt pointer ref role/controller mismatch")
        _v2_digest(fields[7], "v3 pointer object", oid=True)
        _v2_digest(fields[10], "v3 protected manifest")
        _v2_digest(fields[11], "v3 archive manifest")


def _v2_population(bodies: Mapping[str, object], raw: Mapping[str, bytes]) -> list[dict[str, object]]:
    whole, history = [], []
    for role in ("STATE", "ROADMAP"):
        common = {"source_role": role, "source_sha256": _v2_sha(raw[role]), "source_bytes": len(raw[role]), "blob_oid": _v2_blob(raw[role])}
        whole.append({**common, "role": role + "_PREIMAGE", "source_pointer": "", "record_id": role + ".md",
                      "record_sha256": common["source_sha256"], "owner": role + ".md"})
        for index, row in enumerate(bodies[role]["history"]):
            history.append({**common, "role": "HISTORY_RECORD", "source_pointer": "/history/" + str(index),
                            "record_id": row["record_id"], "record_sha256": _v2_sha(_v2_canonical(row)), "owner": row["owner"]})
    return whole + history


def _v2_manifest(payload, rows, source_hashes, current, receipt_oid, transition, refs, output_hashes, archives):
    return {"PRESERVED_PAYLOAD": {"payload": _v2_clone(payload), "owner_map": _v2_clone(rows), "source_hashes": _v2_clone(source_hashes)},
            "MONOTONIC_TRANSITION": _v2_clone(transition),
            "DERIVED_BINDINGS": {"authority_ceiling": _V2_AUTHORITY, "predecessor_continuity": _v2_clone(current),
                                 "current_receipt_ref_oid": receipt_oid, "artifact_refs": _v2_clone(refs),
                                 "state_sha256": output_hashes["STATE"], "roadmap_sha256": output_hashes["ROADMAP"]},
            "ARCHIVED_ONLY_HISTORY": _v2_clone(archives)}


def parse_canonical_pair_v2(state_bytes: bytes, roadmap_bytes: bytes, *,
                             owner_map: Sequence[Mapping[str, object]], artifacts: Mapping[str, bytes]) -> dict[str, object]:
    """Parse all bytes or refuse; validate external owner/artifact denominator.

    The WORK_GRAPH dependency is preserved as exact owner-bound bytes. Its
    native schema/frontier interpretation remains a separate owner qualification.
    """
    raw = {"STATE": state_bytes, "ROADMAP": roadmap_bytes}
    bodies = {role: _v2_load_body(data, role) for role, data in raw.items()}
    payload = {role: body["payload"] for role, body in bodies.items()}
    _v2_payload_schema(payload)
    identity = payload["STATE"]["identity"]["value"]
    controller = identity["controller_id"]
    action = payload["STATE"]["continuation"]["value"]["next_action"]
    _v2_require(bodies["STATE"]["pair_id"] == bodies["ROADMAP"]["pair_id"]
                and _v2_same(bodies["STATE"]["continuity"], bodies["ROADMAP"]["continuity"])
                and _v2_same(bodies["STATE"]["transition"], bodies["ROADMAP"]["transition"]), "whole-pair identity/continuity mismatch")
    for role, body in bodies.items():
        _v2_continuity(body["continuity"], controller)
        if body["transition"] is not None:
            _v2_transition(body["transition"], body["continuity"], controller)
        _v2_history(body["history"])
        _v2_require(_v2_render(body, action, identity) == raw[role], "canonical frame or identity-bearing mirror changed")
    current = _v2_effective(bodies["STATE"])
    refs = _v2_artifact_refs(bodies, controller, current)
    ids = {row["artifact_id"] for row in refs}
    _v2_require(isinstance(artifacts, Mapping) and set(artifacts) == ids and all(type(value) is bytes for value in artifacts.values()),
                "complete declared artifact byte population required")
    _v2_require(set(payload["STATE"]["runtime_artifacts"]["value"]) == ids, "runtime artifact population omits a declared dependency")
    _v2_check_references(payload, ids)
    for body in bodies.values():
        _v2_check_references(body["history"], ids)
    rows = _v2_list(owner_map, "complete owner map")
    for row in rows:
        _v2_object(row, _V2_MAP_KEYS, "complete owner row")
        _v2_enum(row["source_kind"], {"PAIR", "ARTIFACT"}, "owner source kind")
    pair_rows = [row for row in rows if row["source_kind"] == "PAIR"]
    checked = validate_protected_payload_v2(payload, pair_rows)
    hashes = {role: _v2_sha(data) for role, data in raw.items()}
    _v2_require(all(row["source_sha256"] == hashes[row["source_id"]] for row in pair_rows), "owner rows do not bind complete source bytes")
    expected_artifacts = {}
    for ref in refs:
        artifact_id = ref["artifact_id"]
        digest = _v2_sha(artifacts[artifact_id])
        expected_artifacts[artifact_id] = {"field": "/artifacts/" + artifact_id, "owner": ref["owner"], "source_kind": "ARTIFACT",
                                           "source_id": artifact_id, "source_pointer": "", "source_sha256": digest, "value_sha256": digest}
    artifact_rows = [row for row in rows if row["source_kind"] == "ARTIFACT"]
    _v2_require(len(artifact_rows) == len(expected_artifacts) and all(type(row["source_id"]) is str and row["source_id"] in expected_artifacts
                and _v2_same(row, expected_artifacts[row["source_id"]]) for row in artifact_rows)
                and len({row["source_id"] for row in artifact_rows}) == len(expected_artifacts), "artifact owner denominator/binding mismatch")
    by_id = {row["artifact_id"]: row for row in refs}
    for pending in payload["STATE"]["pending_boundaries"]["value"]:
        artifact_id = pending["original_evidence_ref"]
        evidence = artifacts[artifact_id]
        source = pending["physical_source"]
        _v2_require(by_id[artifact_id]["role"] == "EVIDENCE" and by_id[artifact_id]["locator"] == pending["original_evidence_locator"]
                    and source["source_binding"] == _v2_sha(evidence)
                    and source["offset"] + source["byte_length"] <= len(evidence)
                    and source["sha256"] == _v2_sha(evidence[source["offset"]:source["offset"] + source["byte_length"]]),
                    "pending physical source bytes/locator mismatch")
        witness = pending["consumption"]["witness"]
        if witness is not None:
            _v2_require(witness["sha256"] == _v2_sha(artifacts[witness["evidence_ref"]]), "accepted witness artifact bytes mismatch")
    receipt_ref = next(row for row in refs if row["role"] == "CONTINUITY_RECEIPT")
    receipt_bytes = artifacts[receipt_ref["artifact_id"]]
    _v2_receipt(receipt_bytes, current, identity, hashes, action)
    receipt_oid = receipt_ref["locator"] + "@" + _v2_blob(receipt_bytes, receipt_ref["object_format"])
    sorted_rows = sorted(_v2_clone(list(rows)), key=lambda row: row["field"])
    old_archives = _v2_existing_archives(bodies, controller)
    manifest = _v2_manifest(payload, sorted_rows, hashes, current, receipt_oid, bodies["STATE"]["transition"], refs, hashes, old_archives)
    return {"schema_version": "implementaudit.canonical-pair-preimage.v2", "authority_ceiling": _V2_AUTHORITY,
            "state_bytes": state_bytes, "roadmap_bytes": roadmap_bytes, "bodies": _v2_clone(bodies),
            "payload": checked["payload"], "owner_map": sorted_rows, "artifacts": _v2_clone(dict(artifacts)),
            "source_hashes": hashes, "current_continuity": current, "current_receipt_ref_oid": receipt_oid,
            "archive_population": _v2_population(bodies, raw), "protected_manifest": manifest}


def _v2_revalidate(preimage: object) -> dict[str, object]:
    _v2_object(preimage, _V2_PREIMAGE_KEYS, "preimage")
    expected = parse_canonical_pair_v2(preimage["state_bytes"], preimage["roadmap_bytes"], owner_map=preimage["owner_map"], artifacts=preimage["artifacts"])
    _v2_require(_v2_same(preimage, expected), "preimage metadata was omitted, changed or not derived from exact source bytes")
    return expected


def _v2_derive(preimage, transition, archive_pointers, max_state_bytes, max_roadmap_bytes):
    _v2_integer(max_state_bytes, "STATE output byte limit", 1)
    _v2_integer(max_roadmap_bytes, "ROADMAP output byte limit", 1)
    controller = preimage["payload"]["STATE"]["identity"]["value"]["controller_id"]
    current = preimage["current_continuity"]
    if transition is not None:
        _v2_transition(transition, current, controller, preimage["current_receipt_ref_oid"])
    preparation = _v2_next(current["projection_generation_id"])
    supplied = _v2_list(archive_pointers, "new archive pointer population")
    expected = {(row["source_role"], row["source_pointer"]): row for row in preimage["archive_population"]}
    indexed, anchor = {}, None
    for row in supplied:
        _v2_archive_pointer(row, controller)
        identity = (row["source_role"], row["source_pointer"])
        _v2_require(identity in expected and identity not in indexed
                    and _v2_same({key: row[key] for key in _V2_DESCRIPTOR_KEYS}, expected[identity]), "archive population is not the exact complete source/history denominator")
        _v2_require(row["preparation_generation_id"] == preparation, "archive preparation generation mismatch")
        row_anchor = (row["archive_ref"], row["archive_manifest_oid"], row["archive_manifest_sha256"], row["preparation_generation_id"])
        _v2_require(anchor is None or anchor == row_anchor, "new archive pointers have conflicting anchors")
        anchor = row_anchor
        indexed[identity] = _v2_clone(row)
    _v2_require(set(indexed) == set(expected), "archive pointers omit a whole source or removed typed history item")
    new_pointers = [indexed[(row["source_role"], row["source_pointer"])] for row in preimage["archive_population"]]
    archives = _v2_existing_archives(preimage["bodies"], controller) + new_pointers
    bodies = _v2_clone(preimage["bodies"])
    effective = transition if transition is not None else current
    for body in bodies.values():
        body["history"] = []
        body["archive_pointers"] = _v2_clone(archives)
        body["continuity"] = _v2_clone(current)
        body["transition"] = _v2_clone(transition)
        for ref in body["artifact_refs"]:
            if ref["role"] == "CONTINUITY_RECEIPT":
                ref["locator"] = effective["expected_receipt_ref"]
    action = preimage["payload"]["STATE"]["continuation"]["value"]["next_action"]
    identity = preimage["payload"]["STATE"]["identity"]["value"]
    raw = {role: _v2_render(body, action, identity) for role, body in bodies.items()}
    _v2_require(len(raw["STATE"]) <= max_state_bytes and len(raw["ROADMAP"]) <= max_roadmap_bytes,
                "complete protected projection exceeds caller/calibration byte limits")
    refs = _v2_artifact_refs(bodies, controller, effective)
    output_hashes = {role: _v2_sha(data) for role, data in raw.items()}
    return {"schema_version": "implementaudit.canonical-pair-candidate.v2", "authority_ceiling": _V2_AUTHORITY,
            "state_bytes": raw["STATE"], "roadmap_bytes": raw["ROADMAP"], "payload": _v2_clone(preimage["payload"]),
            "source_hashes": _v2_clone(preimage["source_hashes"]), "owner_map": _v2_clone(preimage["owner_map"]),
            "artifact_refs": refs, "predecessor_continuity": _v2_clone(current), "transition": _v2_clone(transition),
            "archive_pointers": archives,
            "protected_manifest": _v2_manifest(preimage["payload"], preimage["owner_map"], preimage["source_hashes"], current,
                                                preimage["current_receipt_ref_oid"], transition, refs, output_hashes, archives),
            "limits": {"max_state_bytes": max_state_bytes, "max_roadmap_bytes": max_roadmap_bytes}}


def derive_hot_pair_v2(preimage: Mapping[str, object], *, transition: Mapping[str, object] | None,
                        archive_pointers: Sequence[Mapping[str, object]], max_state_bytes: int,
                        max_roadmap_bytes: int) -> dict[str, object]:
    """Deterministically preserve all protected fields; compact only typed history.

    None is an F2 draft with no successor envelope. Non-None transitions must be
    supplied after owner admission and archive anchoring; this pure function
    verifies their algebra, never their native authority or ref currentness.
    """
    return _v2_derive(_v2_revalidate(preimage), transition, archive_pointers, max_state_bytes, max_roadmap_bytes)


def verify_projection_equivalence_v2(preimage: Mapping[str, object], candidate: Mapping[str, object]) -> dict[str, object]:
    """Recompute the full result from exact source bytes; reject every omission.

    Immutable-preimage custody is the caller's responsibility. This checks no
    caller PASS bit, performs no model summary, and creates no authority.
    """
    checked = _v2_revalidate(preimage)
    _v2_object(candidate, _V2_CANDIDATE_KEYS, "candidate")
    limits = _v2_object(candidate["limits"], {"max_state_bytes", "max_roadmap_bytes"}, "candidate limits")
    pointers = _v2_list(candidate["archive_pointers"], "candidate archives")
    count = len(checked["archive_population"])
    _v2_require(len(pointers) >= count, "candidate omits exact retrieval pointers")
    expected = _v2_derive(checked, candidate["transition"], pointers[-count:], limits["max_state_bytes"], limits["max_roadmap_bytes"])
    _v2_require(_v2_same(candidate, expected), "whole-field projection omission, semantic change or derived binding mismatch")
    return {"schema_version": "implementaudit.projection-equivalence.v2", "authority_ceiling": _V2_AUTHORITY,
            "equivalent": True, "protected_leaf_count": len([row for row in checked["owner_map"] if row["source_kind"] == "PAIR"]),
            "source_hashes": _v2_clone(checked["source_hashes"])}
