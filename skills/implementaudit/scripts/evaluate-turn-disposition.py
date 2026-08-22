#!/usr/bin/env python3
"""Classify one governed host-turn disposition without creating lifecycle state."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, NoReturn


REQUEST_SCHEMA = "implementaudit.turn-disposition-request.v1"
RESULT_SCHEMA = "implementaudit.turn-disposition-result.v1"
BINDING_RESULT_SCHEMA = "implementaudit.host-session-binding-result.v1"
ROUTE_RESULT_SCHEMA = "implementaudit.route-transaction-result.v1"
CLAIMS = {
    "NO_ACTIVE_AUDIT_OBJECT",
    "TERMINAL_CLOSURE",
    "AUDITED_HANDOFF",
    "NONTERMINAL_YIELD",
}
PROOF_LAYERS = {
    "source_core": "PRESENT",
    "package": "UNVERIFIED",
    "install": "UNVERIFIED",
    "host_activation": "UNVERIFIED",
}
HEX_OID = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")
SHA256_ID = re.compile(r"sha256:[0-9a-f]{64}")
GENERATION = re.compile(r"G[0-9A-F]{4}")
CONTINUITY_RECEIPT = re.compile(
    r"refs/implementaudit/continuity-receipts/[a-z0-9][a-z0-9-]{0,47}/G[0-9A-F]{4}@[0-9a-f]{40}(?:[0-9a-f]{24})?"
)
REQUEST_KEYS = {"schema", "claim", "run_root", "binding", "route"}
CORRELATION_KEYS = {
    "host_id",
    "host_session_id",
    "binding_generation",
    "controller_id",
    "claim_id",
    "explicit_run_root",
    "repository_identity",
    "git_common_directory_identity",
    "worktree_identity",
    "applicable_continuity_generation",
    "applicable_continuity_receipt",
    "event_id",
    "turn_id",
    "tool_use_id",
    "agent_id",
    "obligation_id",
    "route_transaction_id",
}
BINDING_RESULT_KEYS = {
    "schema",
    "status",
    "binding_generation",
    "correlation_id",
    "host_activation_proven",
    "proof_layers",
}
ROUTE_RESULT_KEYS = {
    "schema",
    "status",
    "decision",
    "classification",
    "advance_allowed",
    "admission_required",
    "enforcement_available",
    "record_oid",
    "record_identity",
    "obligation_id",
    "route_state",
    "governor_decision_count",
    "history_query",
    "history_read_performed",
    "mirror_claim",
    "mirror_status",
    "projection_status",
    "proof_layers",
    "host_activation_proven",
}
TERMINAL_MARKERS = {
    "AUDIT_COMPLETE",
    "IMPLEMENTAUDIT_RUN_COMPLETE",
    "AUDIT_HANDOFF",
    "ANDON_HANDOFF",
}


class InputError(ValueError):
    """The request is malformed or cannot be decoded strictly."""


class DecisionBlocked(RuntimeError):
    """The request is well formed but cannot permit this turn to stop."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value = dict(pairs)
    if len(value) != len(pairs):
        raise InputError("duplicate JSON member")
    return value


def exact_object(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise InputError(f"{label} has the wrong shape")
    return value


def exact_text(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 4096
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        raise InputError(f"{label} is empty, oversized, or contains a control character")
    return value


def same_path(left: str, right: str) -> bool:
    return os.path.normcase(os.path.abspath(left)) == os.path.normcase(os.path.abspath(right))


def safe_regular_file(path: Path, label: str) -> None:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise InputError(f"{label} cannot be inspected: {exc}") from exc
    if (
        not stat.S_ISREG(info.st_mode)
        or stat.S_ISLNK(info.st_mode)
        or bool(getattr(info, "st_file_attributes", 0) & 0x400)
        or info.st_size > 1_000_000
    ):
        raise InputError(f"{label} is not a bounded regular file")


def read_request(path: str) -> dict[str, Any]:
    target = Path(path)
    safe_regular_file(target, "request")
    try:
        payload = json.loads(target.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, InputError) as exc:
        raise InputError(f"request is unreadable or malformed: {exc}") from exc
    return exact_object(payload, REQUEST_KEYS, "request")


def classify_claim(request: dict[str, Any]) -> str:
    if request["schema"] != REQUEST_SCHEMA:
        raise InputError("request schema is stale or unknown")
    claim = request["claim"]
    if claim not in CLAIMS:
        raise InputError("claim is not a canonical turn disposition")
    if claim == "NO_ACTIVE_AUDIT_OBJECT":
        if any(request[key] is not None for key in ("run_root", "binding", "route")):
            raise DecisionBlocked("no-active-object is the only zero-object path and carries no active-object inputs")
        return claim
    exact_text(request["run_root"], "run_root")
    if request["binding"] is None or request["route"] is None:
        raise DecisionBlocked("an active audit object requires binding and route evidence")
    return claim


def validate_binding(binding: Any, run_root: str) -> dict[str, Any]:
    envelope = exact_object(binding, {"correlation", "result"}, "binding")
    correlation = exact_object(envelope["correlation"], CORRELATION_KEYS, "binding.correlation")
    obligation = correlation["obligation_id"]
    transaction = correlation["route_transaction_id"]
    if (obligation is None) != (transaction is None):
        raise DecisionBlocked("route obligation and transaction identities are incomplete")
    for key in (
        "host_id",
        "host_session_id",
        "controller_id",
        "claim_id",
        "explicit_run_root",
        "repository_identity",
        "git_common_directory_identity",
        "worktree_identity",
        "event_id",
    ):
        exact_text(correlation[key], f"binding.correlation.{key}")
    for key in ("turn_id", "tool_use_id", "agent_id", "obligation_id", "route_transaction_id"):
        exact_text(correlation[key], f"binding.correlation.{key}", nullable=True)
    for key in ("binding_generation", "applicable_continuity_generation"):
        if not isinstance(correlation[key], str) or not GENERATION.fullmatch(correlation[key]):
            raise InputError(f"binding.correlation.{key} is not canonical")
    if not isinstance(correlation["applicable_continuity_receipt"], str) or not CONTINUITY_RECEIPT.fullmatch(
        correlation["applicable_continuity_receipt"]
    ):
        raise InputError("binding.correlation.applicable_continuity_receipt is not canonical")
    if not same_path(correlation["explicit_run_root"], run_root):
        raise DecisionBlocked("binding is foreign to the claimed run root")

    result_keys = set(BINDING_RESULT_KEYS)
    if obligation is not None:
        result_keys.update({"obligation_id", "route_transaction_id"})
    result = exact_object(envelope["result"], result_keys, "binding.result")
    if result["schema"] != BINDING_RESULT_SCHEMA or result["status"] != "ATTRIBUTED":
        raise DecisionBlocked("binding is unavailable or ambiguous")
    if result["binding_generation"] != correlation["binding_generation"]:
        raise DecisionBlocked("binding generation is stale")
    if result["host_activation_proven"] is not False or result["proof_layers"] != PROOF_LAYERS:
        raise DecisionBlocked("binding result overclaims its proof layer")
    expected_correlation = "sha256:" + hashlib.sha256(
        json.dumps(correlation, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if result["correlation_id"] != expected_correlation:
        raise DecisionBlocked("binding correlation identity does not match its exact inputs")
    if obligation is not None and (
        result["obligation_id"] != obligation or result["route_transaction_id"] != transaction
    ):
        raise DecisionBlocked("binding is foreign to the route obligation")
    return correlation


def validate_history_query(value: Any) -> None:
    if value is None:
        return
    query = exact_object(
        value,
        {"schema", "route", "requirement", "evidence_ids"},
        "route.history_query",
    )
    if (
        query["schema"] != "implementaudit.history-query-request.v1"
        or query["route"] != "QUERY_HISTORY_THEN_RESUME"
        or query["requirement"] != "REQUIRED"
        or not isinstance(query["evidence_ids"], list)
        or len(query["evidence_ids"]) != 1
        or not isinstance(query["evidence_ids"][0], str)
        or not re.fullmatch(r"iaevt-v1-[0-9a-f]{64}", query["evidence_ids"][0])
    ):
        raise InputError("route.history_query is malformed")


def validate_route(route: Any, binding: dict[str, Any]) -> dict[str, Any]:
    result = exact_object(route, ROUTE_RESULT_KEYS, "route")
    if result["schema"] != ROUTE_RESULT_SCHEMA or result["status"] != "CURRENT":
        raise DecisionBlocked("route result is absent, stale, or unavailable")
    if result["enforcement_available"] is not True or result["history_read_performed"] is not False:
        raise DecisionBlocked("route result is not the bounded current owner result")
    if result["host_activation_proven"] is not False or result["proof_layers"] != PROOF_LAYERS:
        raise DecisionBlocked("route result overclaims its proof layer")
    if not isinstance(result["record_oid"], str) or not HEX_OID.fullmatch(result["record_oid"]):
        raise InputError("route.record_oid is not canonical")
    if not isinstance(result["record_identity"], str) or not SHA256_ID.fullmatch(result["record_identity"]):
        raise InputError("route.record_identity is not canonical")
    if type(result["governor_decision_count"]) is not int or result["governor_decision_count"] < 0:
        raise InputError("route.governor_decision_count is not a nonnegative integer")
    if result["projection_status"] != "CURRENT":
        raise DecisionBlocked("route result does not match the STATE projection")
    if result["mirror_status"] not in {
        "IGNORED_ABSENT",
        "IGNORED_CORROBORATION",
        "IGNORED_CONTRADICTION",
    }:
        raise InputError("route.mirror_status is not canonical")
    exact_text(result["mirror_claim"], "route.mirror_claim", nullable=True)
    validate_history_query(result["history_query"])

    decision = result["decision"]
    if decision == "NOT_REQUIRED":
        if not (
            result["classification"] == "MECHANICALLY_NOT_REQUIRED"
            and result["advance_allowed"] is False
            and result["admission_required"] is True
            and result["obligation_id"] is None
            and result["route_state"] is None
            and result["governor_decision_count"] == 0
            and binding["obligation_id"] is None
            and binding["route_transaction_id"] is None
        ):
            raise DecisionBlocked("NOT_REQUIRED route result is internally inconsistent")
    elif decision == "REQUIRED":
        if not (
            result["classification"] in {"MECHANICALLY_REQUIRED", "JUDGEMENT_REQUIRED"}
            and result["advance_allowed"] is True
            and result["admission_required"] is False
            and result["route_state"] == "SATISFIED"
            and isinstance(result["obligation_id"], str)
            and result["obligation_id"]
            and result["governor_decision_count"] == 1
            and binding["obligation_id"] == result["obligation_id"]
            and isinstance(binding["route_transaction_id"], str)
            and binding["route_transaction_id"]
        ):
            raise DecisionBlocked("in-scope R0033 obligation is not satisfied")
    else:
        raise DecisionBlocked("route decision is PENDING or unknown")
    return result


def run_root_validator(run_root: str, *, nonterminal_yield: bool = False) -> None:
    root = Path(run_root)
    if not root.is_dir() or root.is_symlink():
        raise DecisionBlocked("claimed run root is absent, aliased, or not a directory")
    validator = Path(__file__).with_name("validate-run-root.sh")
    bash_executable = "bash"
    validator_arg = str(validator)
    root_arg = str(root)
    if os.name == "nt":
        git_executable = shutil.which("git")
        candidates: list[Path] = []
        if git_executable:
            git_path = Path(git_executable).resolve()
            candidates.extend(parent / "bin" / "bash.exe" for parent in git_path.parents)
        bash_path = next(
            (candidate for candidate in candidates if candidate.is_file() and not candidate.is_symlink()),
            None,
        )
        if bash_path is None:
            raise DecisionBlocked("Git-for-Windows Bash is unavailable")
        bash_executable = str(bash_path)
        converted: list[str] = []
        for value in (validator_arg, root_arg):
            result = subprocess.run(["cygpath", "-u", value], text=True, capture_output=True, check=False)
            if result.returncode or not result.stdout.strip():
                raise DecisionBlocked("Git-for-Windows path translation is unavailable")
            converted.append(result.stdout.strip())
        validator_arg, root_arg = converted
    command = [bash_executable, validator_arg]
    if nonterminal_yield:
        command.append("--nonterminal-yield")
    command.append(root_arg)
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        raise DecisionBlocked(f"run-root validation failed: {detail}")


def state_lines(run_root: str) -> list[str]:
    state = Path(run_root) / "STATE.md"
    safe_regular_file(state, "STATE.md")
    try:
        return state.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise InputError(f"STATE.md is unreadable: {exc}") from exc


def state_fields(lines: list[str]) -> dict[str, str]:
    wanted = {
        "Status",
        "Audit object state",
        "Route decision projection",
        "Route decision record",
    }
    values: dict[str, str] = {}
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [cell.strip(" \t`") for cell in line.split("|")]
        if len(cells) > 2 and cells[1] in wanted:
            if cells[1] in values:
                raise DecisionBlocked(f"STATE.md has duplicate {cells[1]} rows")
            values[cells[1]] = cells[2]
    if set(values) != wanted:
        raise DecisionBlocked("STATE.md lacks one canonical current-phase field")
    return values


def validate_projection(fields: dict[str, str], route: dict[str, Any]) -> None:
    if fields["Route decision projection"] != route["decision"]:
        raise DecisionBlocked("STATE route projection disagrees with the canonical route result")
    if fields["Route decision record"] != route["record_oid"]:
        raise DecisionBlocked("STATE route record disagrees with the canonical route result")


def exact_markers(lines: list[str]) -> list[str]:
    return [line for line in lines if line in TERMINAL_MARKERS]


def validate_closure(run_root: str, route: dict[str, Any]) -> None:
    run_root_validator(run_root)
    lines = state_lines(run_root)
    fields = state_fields(lines)
    validate_projection(fields, route)
    markers = exact_markers(lines)
    nonblank = [line for line in lines if line.strip()]
    if fields["Status"] != "DONE" or fields["Audit object state"] != "terminal verified closure":
        raise DecisionBlocked("terminal closure claim does not match lifecycle state")
    if markers != ["AUDIT_COMPLETE", "IMPLEMENTAUDIT_RUN_COMPLETE"] or nonblank[-2:] != markers:
        raise DecisionBlocked("terminal closure markers are missing, reordered, duplicated, or mixed with handoff")


def validate_handoff(run_root: str, route: dict[str, Any]) -> None:
    run_root_validator(run_root)
    lines = state_lines(run_root)
    fields = state_fields(lines)
    validate_projection(fields, route)
    markers = exact_markers(lines)
    nonblank = [line for line in lines if line.strip()]
    handoff_rows = [line for line in lines if line.startswith("Handoff state, if any:")]
    if fields["Status"] != "BLOCKED":
        raise DecisionBlocked("audited handoff requires BLOCKED lifecycle state")
    if len(handoff_rows) != 1 or not handoff_rows[0].split(":", 1)[1].strip():
        raise DecisionBlocked("audited handoff lacks durable handoff evidence")
    if markers != ["AUDIT_HANDOFF"] or nonblank[-1] != "AUDIT_HANDOFF":
        raise DecisionBlocked("handoff marker is missing, nonterminal, duplicated, or mixed with closure")


def validate_yield(run_root: str, route: dict[str, Any]) -> None:
    run_root_validator(run_root, nonterminal_yield=True)
    lines = state_lines(run_root)
    fields = state_fields(lines)
    validate_projection(fields, route)
    if exact_markers(lines):
        raise DecisionBlocked("nonterminal yield emitted a terminal or handoff marker")


def decision(request: dict[str, Any], claim: str) -> dict[str, Any]:
    if claim == "NO_ACTIVE_AUDIT_OBJECT":
        return {
            "schema": RESULT_SCHEMA,
            "status": "ALLOW",
            "disposition": claim,
            "stop_allowed": True,
            "active_audit_object": False,
            "object_closed": False,
            "audited_handoff": False,
            "nonterminal_yield": False,
            "host_activation_proven": False,
        }
    run_root = request["run_root"]
    assert isinstance(run_root, str)
    binding = validate_binding(request["binding"], run_root)
    route = validate_route(request["route"], binding)
    if claim == "TERMINAL_CLOSURE":
        validate_closure(run_root, route)
    elif claim == "AUDITED_HANDOFF":
        validate_handoff(run_root, route)
    else:
        validate_yield(run_root, route)
    return {
        "schema": RESULT_SCHEMA,
        "status": "ALLOW",
        "disposition": claim,
        "stop_allowed": True,
        "active_audit_object": True,
        "object_closed": claim == "TERMINAL_CLOSURE",
        "audited_handoff": claim == "AUDITED_HANDOFF",
        "nonterminal_yield": claim == "NONTERMINAL_YIELD",
        "host_activation_proven": False,
    }


def block_payload(reason: str, *, status: str = "BLOCK") -> dict[str, Any]:
    return {
        "schema": RESULT_SCHEMA,
        "status": status,
        "disposition": "BLOCK",
        "stop_allowed": False,
        "active_audit_object": None,
        "object_closed": False,
        "audited_handoff": False,
        "nonterminal_yield": False,
        "host_activation_proven": False,
        "reason": reason,
    }


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        request = read_request(args.request)
        claim = classify_claim(request)
        emit(decision(request, claim))
        return 0
    except DecisionBlocked as exc:
        emit(block_payload(str(exc)))
        return 3
    except InputError as exc:
        emit(block_payload(str(exc), status="UNAVAILABLE"))
        return 2


if __name__ == "__main__":
    sys.exit(main())
