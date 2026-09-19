#!/usr/bin/env python3
"""Canonical R0033 route-decision and obligation authority.

The H2A core owns PENDING/NOT_REQUIRED/REQUIRED classification and the current
immutable Git-ref record. H2B extends that same authority with bounded child
open, return, completion, and source-identity replay checks.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
from datetime import datetime
import errno
import hashlib
import json
import math
import os
import queue
import re
import shutil
import stat
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Iterator, NoReturn

# The controller's existing source identity transitively binds this new owner.
# Rebind both reviewed files together; missing, aliased or changed bytes fail closed.
_ROUTE_REQUEST_POLICY_SHA256 = 'ea69123930803e428630b51565b6c7f58d079262f3feda34d95c31f0fdd6375f'
_ROUTE_REQUEST_POLICY_BYTES = 5191
def _load_route_request_policy():
    import hashlib as _hashlib
    import os as _os
    import stat as _stat
    import sys as _sys
    import types as _types
    _path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'route_request_policy.py')
    _fd = None
    try:
        _before = _os.lstat(_path)
        if (_stat.S_ISLNK(_before.st_mode) or not _stat.S_ISREG(_before.st_mode)
                or getattr(_before, "st_file_attributes", 0) & 0x400):
            raise ImportError("route_request_policy.py: source is not a non-aliased regular file")
        _flags = _os.O_RDONLY | getattr(_os, "O_BINARY", 0) | getattr(_os, "O_NONBLOCK", 0) | getattr(_os, "O_NOFOLLOW", 0)
        _fd = _os.open(_path, _flags)
        _info = _os.fstat(_fd)
        if (not _stat.S_ISREG(_info.st_mode) or (_before.st_dev, _before.st_ino) != (_info.st_dev, _info.st_ino)):
            raise ImportError("route_request_policy.py: source identity changed while opening")
        with _os.fdopen(_fd, "rb") as _stream:
            _fd = None
            _source = _stream.read(_ROUTE_REQUEST_POLICY_BYTES + 1)
    except OSError as _exc:
        raise ImportError("route_request_policy.py: source unavailable") from _exc
    finally:
        if _fd is not None:
            _os.close(_fd)
    if len(_source) != _ROUTE_REQUEST_POLICY_BYTES or _hashlib.sha256(_source).hexdigest() != _ROUTE_REQUEST_POLICY_SHA256:
        raise ImportError("route_request_policy.py: source identity mismatch")
    _module = _types.ModuleType(__name__ + ".route_request_policy")
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
_route_request_policy = _load_route_request_policy()



RESULT_SCHEMA = "implementaudit.route-transaction-result.v1"
REQUEST_SCHEMA = _route_request_policy.REQUEST_SCHEMA
RECORD_SCHEMA = "implementaudit.route-decision.v1"
PREDICATE_VERSION = _route_request_policy.PREDICATE_VERSION
PACKET_SCHEMA = "implementaudit.route-packet.v1"
SOURCE_EVENT_SCHEMA = "implementaudit.source-event.v1"
SOURCE_EVENT_PROVENANCE_SCHEMA = "implementaudit.source-event-provenance.v1"
CHILD_RETURN_SCHEMA = "implementaudit.child-return.v1"
GOVERNOR_DECISION_SCHEMA = "implementaudit.governor-route-decision.v1"
DECISIONS = {"PENDING", "NOT_REQUIRED", "REQUIRED"}
CLASSIFICATIONS = {
    "MECHANICALLY_REQUIRED",
    "MECHANICALLY_NOT_REQUIRED",
    "JUDGEMENT_REQUIRED",
}
CLOSED_ACTION_CLASSES = {
    "MECHANICAL_CURRENTNESS_ACTION",
    "PURE_BOUNDED_READ_OR_VALIDATION",
    "EXACT_PACKAGE_OR_TOPOLOGY_VERIFICATION",
    "SAFE_STATUS_OR_CONTAINMENT",
    "EXACT_ALREADY_BOUND_DETERMINISTIC_ACTION",
}
REQUIRED_REASONS = {
    "STALE_CONTEXT_RECONSTRUCTION",
    "IMMUTABLE_INDEPENDENT_REVIEW",
    "MAINTAINER_QUALIFICATION",
    "NONTRIVIAL_ANDON_DIAGNOSIS",
}
CHILD_ROUTE_MAP = {
    "STALE_CONTEXT_RECONSTRUCTION": (
        "audit-state",
        "rehydrate bounded current state after the exact stale-context boundary",
    ),
    "IMMUTABLE_INDEPENDENT_REVIEW": (
        "audit-assess",
        "independently assess the exact immutable review packet",
    ),
    "MAINTAINER_QUALIFICATION": (
        "audit-implement",
        "qualify the exact maintainer candidate after verified release currentness",
    ),
    "NONTRIVIAL_ANDON_DIAGNOSIS": (
        "audit-andon",
        "diagnose the established nontrivial Andon within its authority ceiling",
    ),
}
PRESERVED_UNOPENABLE_REQUIRED_RECORDS = {
    "ccf169415933de3f98fd75c54a2711ba1c060174": {
        "record_identity": "sha256:77e05b3db3afa24d979592e8aeecb83ce6fc56ab8499409834bd8e858b4320e7",
        "action": {
            "identity": "g0253-hbase-b2-independent-assessment",
            "class": "PURE_BOUNDED_READ_OR_VALIDATION",
            "argv": ["route-trigger", "IMMUTABLE_INDEPENDENT_REVIEW", "B2"],
            "digest": "sha256:81799f3bdfdda82923d13bac09dda630e49b703d25460815cec3da3f8ab71877",
        },
        "package": {
            "head": "57b48140f1266cbd3f6316718463409a134f1969",
            "tree": "4e5f6ce2467c7c0535408a5c3745a0365b94f5c3",
            "source_digests": {
                "SKILL.md": "sha256:766cae1fc8693367a2b81b63e9c28e00e3deab588e723d9570267dadbab4e238",
                "claim-run.sh": "sha256:b75d14e633c16f81c23d7a7e61f6715010a810424b885c7e688e5c88411847f6",
                "route-obligations.md": "sha256:9424cbe4d07fba5f579331f4ec32f22707c8d0b13c0a32f8204f4995037266fc",
                "route-transaction.py": "sha256:6c6e64100c75d57eb03f0391a280abf4133f4683ed58c5bfa9d3c73e7da88cd0",
            },
            "action_executable": {
                "requested": "route-trigger",
                "resolved": "R0033:unadmitted",
                "digest": "sha256:bd1ee9a50d3314a7eee4e592b272700fa05e264ac3ba858398bb6985c433e11d",
            },
        },
    },
    "0b2929335e450d18260221243c394b8afceb7666": {
        "record_identity": "sha256:cfbbd8086bd71963da58bdaf9c74b766d829971a123892bafabeef118fea7e57",
        "action": {
            "identity": "action:g027f-native-s2-d01-fixture-review",
            "class": "REQUIRED_INTERNAL_CHILD",
            "argv": ["route-trigger", "INDEPENDENT_ASSESSMENT_REQUIRED"],
            "digest": "sha256:05c223ed8112aa3ca07b9fea9c36af8eb207f72132960af5f08a24b14028254c",
        },
        "package": {
            "head": "57b48140f1266cbd3f6316718463409a134f1969",
            "tree": "4e5f6ce2467c7c0535408a5c3745a0365b94f5c3",
            "source_digests": {
                "SKILL.md": "sha256:45f8f76064f360bb1741f4e8be8474f543f2d0fb6fb63c0f5165b72cd03c0e9c",
                "claim-run.sh": "sha256:b75d14e633c16f81c23d7a7e61f6715010a810424b885c7e688e5c88411847f6",
                "route-obligations.md": "sha256:c998a8a50559e41e350cb525d00c9589366f041db4c63a2bc9e4ffd49faf30b8",
                "route-transaction.py": "sha256:5cf343a61d732afd029f04b710fbc5cccfa8223223990b2559341bb2ed5abc86",
            },
            "action_executable": {
                "requested": "route-trigger",
                "resolved": "R0033:unadmitted",
                "digest": "sha256:75f4b9c84c8416823f904ba933c2e2ab3de5bcfe6c2df33aa73a2d988838de2b",
            },
        },
    },
}
HOLON_LIFECYCLE_SEQUENCE = ("OPEN", "LOAD", "USE", "RETURN", "DISPOSE", "RECONCILE")
CONTINUITY_RE = re.compile(r"G[0-9A-F]{4}")
CONTROLLER_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,47}")
OID_RE = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")
HEX_RE = _route_request_policy.HEX_RE
EVENT_ID_RE = re.compile(r"iaevt-v1-[0-9a-f]{64}")
ZERO_OID = "0" * 40
EXPIRES_ON = [
    "action-completion",
    "next-action-change",
    "scope-change",
    "read-set-change",
    "host-binding-generation-change",
    "continuity-receipt-change",
    "package-identity-change",
    "child-source-identity-change",
    "owner-evidence-change",
    "authority-evidence-change",
    "dependency-evidence-change",
    "effect-evidence-change",
    "contradiction-or-invalidation",
    "scope-expansion",
]
# Route history is semantically unbounded; these limits constrain one validation
# attempt's resources without treating healthy predecessor depth as corruption.
MAX_ROUTE_LINEAGE_RECORDS = 4096
MAX_ROUTE_RECORD_BYTES = 1 * 1024 * 1024
MAX_ROUTE_LINEAGE_BYTES = 64 * 1024 * 1024
MAX_ROUTE_LINEAGE_ELAPSED_SECONDS = 30.0
MAX_CAT_FILE_HEADER_BYTES = 256
RECORD_KEYS = {
    "schema", "predicate_version", "controller_id", "claim_id", "explicit_run_root",
    "continuity_generation", "continuity_receipt", "host_id", "host_session_id",
    "host_binding_generation", "host_correlation_id", "boundary", "scope", "action",
    "evidence", "inputs", "package", "child_source", "decision", "classification",
    "invalidators", "expiry_fingerprint", "expires_on", "predecessor_record_oid",
    "route_transaction_id", "obligation_id", "route_state", "child_lifecycle_owned",
    "consumed_record_oid", "record_identity",
}
HISTORY_RECORD_KEYS = RECORD_KEYS | {"history_query"}
LIFECYCLE_RECORD_KEYS = RECORD_KEYS | {"lifecycle"}
HISTORY_LIFECYCLE_RECORD_KEYS = HISTORY_RECORD_KEYS | {"lifecycle"}
EXECUTION_EVIDENCE_SCHEMA = "implementaudit.holon-execution-evidence.v1"
RESOLVED_EXECUTION_EVIDENCE_SCHEMA = "implementaudit.resolved-holon-execution-evidence.v1"
HOST_STAGE_RECEIPT_SCHEMA = "implementaudit.host-holon-stage-receipt.v1"
AUDIT_STATE_FRONTIER_RETURN_SCHEMA = "implementaudit.audit-state-minimum-frontier-return.v1"
RECOVERY_CAPSULE_SCHEMA = "implementaudit.post-compaction-recovery.v2"
TRANSACTION_ADMISSION_SCHEMA = "implementaudit.route-transaction-admission.v1"
RECOVERY_CUSTODY_SCHEMA = "implementaudit.route-recovery-custody.v1"
RECOVERY_INPUT_ADAPTER_DIGEST = "sha256:ab5782898381268f6149359dc8be0fb05e3938d465275ce962448aa9da0d7754"
RETAINED_RECOVERY_INPUT_SCHEMA = "implementaudit.retained-recovery-input-candidate.v1"
RETAINED_NATIVE_VERSION = "0.153.4"
MAX_RETAINED_NATIVE_ROW_BYTES = 131072
MAX_RETAINED_NATIVE_SLICE_BYTES = 1048576


class RouteUnavailable(RuntimeError):
    """A fail-closed native dispatch/admission refusal."""


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


def fail(message: str, *, decision: str = "PENDING") -> NoReturn:
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "UNAVAILABLE",
            "decision": decision,
            "advance_allowed": False,
            "enforcement_available": False,
            "error": message,
        }
    )
    raise SystemExit(2)


def run(command: list[str], *, cwd: Path, label: str, environment: dict[str, str] | None = None) -> str:
    completed = subprocess.run(command, cwd=cwd, env=environment, text=True, capture_output=True, check=False)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        fail(f"{label} failed: {detail}")
    return completed.stdout.strip()


def git(repo: Path, *args: str, input_text: str | None = None, check: bool = True) -> str:
    executable = trusted_host_executable(repo, "git")
    completed = subprocess.run(
        [str(executable), *args], cwd=repo, env=sanitized_action_environment(), text=True,
        input=input_text, capture_output=True, check=False
    )
    if check and completed.returncode:
        fail(f"git {' '.join(args)} failed: {completed.stderr.strip() or completed.stdout.strip()}")
    return completed.stdout.strip()


def write_route_record_blob(repo: Path, raw: str) -> str:
    """Write canonical route-record bytes without host newline translation."""
    executable = trusted_host_executable(repo, "git")
    completed = subprocess.run(
        [str(executable), "hash-object", "-w", "--stdin"],
        cwd=repo,
        env=sanitized_action_environment(),
        input=raw.encode("utf-8"),
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        detail = (completed.stderr or completed.stdout).decode("utf-8", errors="replace").strip()
        fail(f"git hash-object -w --stdin failed: {detail or f'exit {completed.returncode}'}")
    try:
        oid = completed.stdout.decode("ascii").strip()
    except UnicodeDecodeError:
        fail("git hash-object -w --stdin returned a non-ASCII object identity")
    if not OID_RE.fullmatch(oid):
        fail("git hash-object -w --stdin returned a malformed object identity")
    return oid


def digest_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    return _route_request_policy.unique_object(pairs)


def exact_text(value: Any, label: str) -> str:
    try:
        return _route_request_policy.exact_text(value, label)
    except _route_request_policy.RequestRefusal as exc:
        fail(exc.message, decision=exc.decision)


def exact_keys(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    try:
        return _route_request_policy.exact_keys(value, keys, label)
    except _route_request_policy.RequestRefusal as exc:
        fail(exc.message, decision=exc.decision)


def identity_record(value: Any, label: str) -> dict[str, str]:
    try:
        return _route_request_policy.identity_record(value, label)
    except _route_request_policy.RequestRefusal as exc:
        fail(exc.message, decision=exc.decision)


def logical_task_name(value: Any, *reserved: str) -> str:
    if (not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,127}", value)
            or value in reserved or value in {"audit-state", "audit-assess", "audit-andon", "audit-implement"}
            or re.fullmatch(r"[0-9a-f]{32,64}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", value)):
        fail("governor-chosen logical task is missing, malformed or aliases another identity", decision="REQUIRED")
    return value


def open_logical_task(record: dict[str, Any]) -> str:
    """Read the name bound at canonical OPEN; never backfill old records."""
    lifecycle = record.get("lifecycle")
    if (record.get("route_state") != "OPEN" or not isinstance(lifecycle, dict)
            or lifecycle.get("state") != "OPEN"):
        fail("logical task requires the existing exact OPEN record", decision="REQUIRED")
    child, _ = mapped_child_route(record)
    return logical_task_name(lifecycle.get("logical_task"), child,
                             record.get("route_transaction_id"), record.get("host_session_id"))


def validate_presentation(value: Any) -> dict[str, str]:
    try:
        return _route_request_policy.validate_presentation(value)
    except _route_request_policy.RequestRefusal as exc:
        fail(exc.message, decision=exc.decision)


def no_child_notice(presentation: Any) -> str:
    bound = validate_presentation(presentation)
    parent, frontier = bound["parent_holon"], bound["consuming_frontier"]
    return ("```ini\nPARENT_HOLON=" + parent + "\nCONSUMING_FRONTIER=" + frontier +
            "\nCHILD_SKILL_ROUTE=NOT_REQUIRED\n```\nThe `" + parent + "` parent uses no internal child at `" +
            frontier + "` because the exact current R0033 route is NOT_REQUIRED.")


def read_request(path: str) -> dict[str, Any]:
    target = Path(path)
    try:
        if target.absolute() != target.resolve(strict=True):
            fail("request traverses an alias")
        info = os.lstat(target)
        if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or info.st_size > 1_000_000:
            fail("request is not a safe regular file")
        request = json.loads(target.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        fail(f"request is unreadable or malformed: {exc}")
    validated = validate_request(request)
    argv = validated["action"]["argv"]
    if argv and argv[0] == "route-trigger":
        if len(argv) == 2 and argv[1] in REQUIRED_REASONS:
            pass
        elif len(argv) >= 2 and argv[1] == "QUERY_HISTORY_THEN_RESUME":
            normalized_history_query(validated)
        else:
            fail("reserved route-trigger namespace requires one exact canonical reason pair or history query")
    return validated


def validate_request(request: Any) -> dict[str, Any]:
    try:
        return _route_request_policy.validate_request(request)
    except _route_request_policy.RequestRefusal as exc:
        fail(exc.message, decision=exc.decision)


def read_exact_artifact(path: str, label: str) -> tuple[bytes, dict[str, Any]]:
    target = Path(path)
    try:
        if target.absolute() != target.resolve(strict=True):
            fail(f"{label} traverses an alias")
        info = os.lstat(target)
        if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or info.st_size > 1_000_000:
            fail(f"{label} is not a safe bounded regular file")
        raw = target.read_bytes()
        value = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        fail(f"{label} is unreadable or malformed: {exc}")
    if not isinstance(value, dict):
        fail(f"{label} is not a JSON object")
    return raw, value


def bytes_identity(raw: bytes) -> dict[str, Any]:
    return {
        "bytes": len(raw),
        "digest": f"sha256:{hashlib.sha256(raw).hexdigest()}",
        "bytes_b64": base64.b64encode(raw).decode("ascii"),
    }


def validate_bytes_identity(value: Any, label: str, *, with_identity: bool = False) -> bytes:
    keys = {"bytes", "digest", "bytes_b64"} | ({"identity"} if with_identity else set())
    record = exact_keys(value, keys, label)
    if with_identity:
        exact_text(record["identity"], f"{label}.identity")
    if type(record["bytes"]) is not int or record["bytes"] < 0 or record["bytes"] > 1_000_000:
        fail(f"{label}.bytes is not a bounded byte count")
    if not isinstance(record["digest"], str) or not HEX_RE.fullmatch(record["digest"]):
        fail(f"{label}.digest is not a canonical sha256 identity")
    try:
        raw = base64.b64decode(record["bytes_b64"], validate=True)
    except (TypeError, ValueError):
        fail(f"{label}.bytes_b64 is malformed")
    if bytes_identity(raw) != {key: item for key, item in record.items() if key != "identity"}:
        fail(f"{label} bytes do not match their count and digest")
    return raw


def source_event_problem(value: Any, label: str = "source_event") -> str | None:
    keys = {"schema", "source_identity", "provenance", "body", "kind", "reactivation"}
    if not isinstance(value, dict) or set(value) != keys:
        return f"{label} has the wrong shape"
    if value["schema"] != SOURCE_EVENT_SCHEMA:
        return f"{label} schema is stale"
    identity = value["source_identity"]
    if not isinstance(identity, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,255}", identity):
        return f"{label} source identity is not canonical"
    provenance = value["provenance"]
    provenance_keys = {"schema", "event_id", "host_correlation_id"}
    if not isinstance(provenance, dict) or set(provenance) != provenance_keys:
        return f"{label} provenance is missing or ambiguous"
    if provenance["schema"] != SOURCE_EVENT_PROVENANCE_SCHEMA:
        return f"{label} provenance schema is stale"
    if provenance["event_id"] != identity:
        return f"{label} provenance names a different source identity"
    if not isinstance(provenance["host_correlation_id"], str) or not HEX_RE.fullmatch(
        provenance["host_correlation_id"]
    ):
        return f"{label} provenance correlation is not canonical"
    body = value["body"]
    if not isinstance(body, str) or not body or len(body.encode("utf-8")) > 100_000 or "\x00" in body:
        return f"{label} body is empty, oversized, or malformed"
    if value["kind"] not in {"one-shot-action", "standing-constraint"}:
        return f"{label} kind is unsupported"
    reactivation = value["reactivation"]
    reactivation_keys = {"reopen", "target_changed", "invalidating_evidence"}
    if not isinstance(reactivation, dict) or set(reactivation) != reactivation_keys:
        return f"{label} reactivation has the wrong shape"
    if any(type(reactivation[key]) is not bool for key in reactivation):
        return f"{label} reactivation flags are malformed"
    return None


def source_event_record(value: Any, label: str = "source_event") -> dict[str, Any]:
    problem = source_event_problem(value, label)
    if problem is not None:
        fail(problem)
    return value


def read_replay_source_event(path: str) -> dict[str, Any]:
    target = Path(path)
    try:
        if target.absolute() != target.resolve(strict=True):
            ambiguous_replay_stop("reconstructed source event traverses an alias")
        info = os.lstat(target)
        if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or info.st_size > 1_000_000:
            ambiguous_replay_stop("reconstructed source event is not a safe bounded regular file")
        raw = target.read_bytes()
        value = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=unique_object)
    except SystemExit:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        ambiguous_replay_stop(f"reconstructed source event is unreadable or malformed: {exc}")
    problem = source_event_problem(value, "reconstructed source event")
    if problem is not None:
        ambiguous_replay_stop(problem)
    return value


def decoded_artifact(raw: bytes, label: str) -> dict[str, Any]:
    try:
        return _route_request_policy.decoded_artifact(raw, label)
    except _route_request_policy.RequestRefusal as exc:
        fail(exc.message, decision=exc.decision)


def route_packet_record(
    packet: Any,
    obligation_id: str,
    transaction_id: str,
    label: str = "route packet",
    *,
    expected_target: str | None = None,
) -> dict[str, Any]:
    packet = exact_keys(
        packet,
        {"schema", "obligation_id", "route_transaction_id", "source_event", "target_identity"},
        label,
    )
    if packet["schema"] != PACKET_SCHEMA:
        fail(f"{label} schema is stale")
    if packet["obligation_id"] != obligation_id or packet["route_transaction_id"] != transaction_id:
        fail(f"{label} names a foreign obligation or transaction")
    source_event_record(packet["source_event"], f"{label} source_event")
    exact_text(packet["target_identity"], f"{label} target_identity")
    if expected_target is not None and packet["target_identity"] != expected_target:
        fail(f"{label} target does not match the sole mapped governed child")
    return packet


def child_return_record(
    returned: Any,
    obligation_id: str,
    transaction_id: str,
    packet_digest: str,
    label: str = "child return",
    *,
    expected_child: str | None = None,
    expected_capsule: dict[str, Any] | None = None,
) -> dict[str, Any]:
    returned = exact_keys(
        returned,
        {"schema", "obligation_id", "route_transaction_id", "packet_digest", "status", "payload"},
        label,
    )
    if returned["schema"] != CHILD_RETURN_SCHEMA or returned["status"] != "RETURNED":
        fail(f"{label} schema or status is stale")
    if (
        returned["obligation_id"] != obligation_id
        or returned["route_transaction_id"] != transaction_id
        or returned["packet_digest"] != packet_digest
    ):
        fail(f"{label} names a foreign delivery")
    if not isinstance(returned["payload"], dict):
        fail(f"{label} payload is malformed")
    execution = returned["payload"].get("holon_execution_evidence")
    if execution is not None:
        if expected_child is None:
            fail(f"{label} execution evidence has no exact selected-child binding", decision="REQUIRED")
        execution_evidence_record(
            execution,
            expected_child,
            transaction_id,
            obligation_id,
            packet_digest,
            f"{label} execution evidence",
        )
    if expected_child == "audit-state" and expected_capsule is not None:
        audit_state_frontier_return_record(
            returned["payload"],
            expected_capsule,
            packet_digest,
            obligation_id,
            transaction_id,
        )
    return returned


def governor_decision_record(
    decision: Any, obligation_id: str, transaction_id: str, return_digest: str,
    label: str = "governor decision",
) -> dict[str, Any]:
    decision = exact_keys(
        decision,
        {"schema", "obligation_id", "route_transaction_id", "return_digest", "outcome", "reason"},
        label,
    )
    if decision["schema"] != GOVERNOR_DECISION_SCHEMA or decision["outcome"] != "SATISFIED":
        fail(f"{label} schema or outcome is not admissible")
    if (
        decision["obligation_id"] != obligation_id
        or decision["route_transaction_id"] != transaction_id
        or decision["return_digest"] != return_digest
    ):
        fail(f"{label} names a foreign return")
    exact_text(decision["reason"], f"{label} reason")
    return decision


def read_route_packet(
    path: str, obligation_id: str, transaction_id: str, *, expected_target: str | None = None
) -> tuple[bytes, dict[str, Any]]:
    raw, packet = read_exact_artifact(path, "route packet")
    return raw, route_packet_record(
        packet, obligation_id, transaction_id, expected_target=expected_target
    )


def read_child_return(
    path: str,
    obligation_id: str,
    transaction_id: str,
    packet_digest: str,
    *,
    expected_child: str | None = None,
    expected_capsule: dict[str, Any] | None = None,
) -> tuple[bytes, dict[str, Any]]:
    raw, returned = read_exact_artifact(path, "child return")
    return raw, child_return_record(
        returned,
        obligation_id,
        transaction_id,
        packet_digest,
        expected_child=expected_child,
        expected_capsule=expected_capsule,
    )


def read_governor_decision(
    path: str, obligation_id: str, transaction_id: str, return_digest: str
) -> tuple[bytes, dict[str, Any]]:
    raw, decision = read_exact_artifact(path, "governor decision")
    return raw, governor_decision_record(decision, obligation_id, transaction_id, return_digest)


def mechanical_action_class(argv: list[str]) -> str | None:
    executable = argv[0].lower()
    claim = Path(__file__).resolve().with_name("claim-run.sh")
    if Path(argv[0]).name.lower() in {"claim-run.sh", "claim-run"} and Path(argv[0]).resolve() == claim:
        if argv[1:] == ["--current-controller"] or (
            len(argv) == 3 and argv[1] == "--current-controller" and CONTROLLER_RE.fullmatch(argv[2])
        ):
            return "MECHANICAL_CURRENTNESS_ACTION"
        if len(argv) == 3 and argv[1] == "--require-current-continuity" and CONTROLLER_RE.fullmatch(argv[2]):
            return "MECHANICAL_CURRENTNESS_ACTION"
        if len(argv) == 3 and argv[1] == "--verify-resume-receipt":
            receipt = re.fullmatch(
                r"refs/implementaudit/continuity-receipts/([^/]+)/G[0-9A-F]{4}@[0-9a-f]{40}", argv[2]
            )
            if receipt and CONTROLLER_RE.fullmatch(receipt.group(1)):
                return "MECHANICAL_CURRENTNESS_ACTION"
    if argv == ["route-read-snapshot"]:
        return "PURE_BOUNDED_READ_OR_VALIDATION"
    package_script = Path(argv[2]).resolve() if executable == "bash" and len(argv) == 3 and argv[1] == "-n" else None
    if (
        package_script is not None
        and package_script.parent == Path(__file__).resolve().parent
        and re.fullmatch(r"check-[a-z0-9-]+\.sh", package_script.name)
    ):
        return "EXACT_PACKAGE_OR_TOPOLOGY_VERIFICATION"
    if argv == ["route-safe-status"]:
        return "SAFE_STATUS_OR_CONTAINMENT"
    if executable in {"sha256sum", "shasum"} and len(argv) == 2:
        return "EXACT_ALREADY_BOUND_DETERMINISTIC_ACTION"
    return None


def mechanical_required_reason(argv: list[str]) -> str | None:
    if len(argv) == 2 and argv[0] == "route-trigger" and argv[1] in REQUIRED_REASONS:
        return argv[1]
    return None


def mapped_child_route(record: dict[str, Any]) -> tuple[str, str]:
    action = record.get("action")
    reason = mechanical_required_reason(action.get("argv", []) if isinstance(action, dict) else [])
    if record.get("decision") != "REQUIRED" or reason not in CHILD_ROUTE_MAP:
        fail(
            "required route does not establish exactly one canonical governed child",
            decision=record.get("decision", "PENDING"),
        )
    return CHILD_ROUTE_MAP[reason]


def transaction_child_admission(
    active_transaction_ids: list[str], requested_transaction_id: str
) -> dict[str, Any]:
    """Apply the one-child ceiling to one transaction, never to the controller."""
    if (
        not isinstance(active_transaction_ids, list)
        or any(not isinstance(item, str) or not item for item in active_transaction_ids)
        or not isinstance(requested_transaction_id, str)
        or not requested_transaction_id
    ):
        fail("route transaction child admission identity is malformed")
    if requested_transaction_id in active_transaction_ids:
        return {
            "decision": "REJECTED",
            "requested_transaction_id": requested_transaction_id,
            "reason": "MAX_CHILD_PER_ROUTE_TRANSACTION_1",
        }
    return {
        "decision": "READY",
        "requested_transaction_id": requested_transaction_id,
        "controller_wide_child_max_one": False,
    }


def _typed_keys(values: list[str], label: str) -> list[str]:
    if (
        not isinstance(values, list)
        or values != sorted(set(values))
        or any(not isinstance(value, str) or not value or len(value) > 512 for value in values)
    ):
        raise RouteUnavailable(f"{label} identities are malformed")
    return values


def admit_transaction_child(
    common: Path,
    controller: str,
    route_transaction_id: str,
    selected_child: str,
    writer_keys: list[str],
    dependency_keys: list[str],
) -> dict[str, Any]:
    """Persist one native child admission per transaction under the Git common dir."""
    if not CONTROLLER_RE.fullmatch(controller) or not HEX_RE.fullmatch(route_transaction_id):
        raise RouteUnavailable("route transaction admission identity is malformed")
    if selected_child not in {child for child, _ in CHILD_ROUTE_MAP.values()}:
        raise RouteUnavailable("route transaction selected child is not canonical")
    writers = _typed_keys(writer_keys, "writer")
    dependencies = _typed_keys(dependency_keys, "dependency")
    directory = Path(common).resolve() / "implementaudit-route-transactions" / controller
    directory.mkdir(parents=True, exist_ok=True)
    transaction_hex = route_transaction_id.removeprefix("sha256:")
    target = directory / f"{transaction_hex}.json"
    records: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            raise RouteUnavailable(f"route transaction admission ledger is malformed: {exc}") from exc
        if not isinstance(record, dict) or set(record) != {
            "schema", "controller_id", "route_transaction_id", "selected_child",
            "writer_keys", "dependency_keys", "status", "admission_identity",
        } or record.get("schema") != TRANSACTION_ADMISSION_SCHEMA:
            raise RouteUnavailable("route transaction admission ledger has a foreign record")
        identity_body = {key: value for key, value in record.items() if key not in {"status", "admission_identity"}}
        if (
            record.get("status") not in {"ACTIVE", "TERMINAL"}
            or record.get("admission_identity") != digest_json(identity_body)
        ):
            raise RouteUnavailable("route transaction admission ledger has an invalid identity")
        records.append(record)
    if target.exists() or any(record["route_transaction_id"] == route_transaction_id for record in records):
        raise RouteUnavailable("MAX_CHILD_PER_ROUTE_TRANSACTION_1")
    for record in records:
        if record["status"] != "ACTIVE":
            continue
        if set(writers) & set(record["writer_keys"]):
            raise RouteUnavailable("WRITER_CONFLICT")
        if set(dependencies) & set(record["dependency_keys"]):
            raise RouteUnavailable("DEPENDENCY_CONFLICT")
    identity_body = {
        "schema": TRANSACTION_ADMISSION_SCHEMA,
        "controller_id": controller,
        "route_transaction_id": route_transaction_id,
        "selected_child": selected_child,
        "writer_keys": writers,
        "dependency_keys": dependencies,
    }
    admission = {
        **identity_body,
        "status": "ACTIVE",
        "admission_identity": digest_json(identity_body),
    }
    try:
        with target.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(admission, sort_keys=True, separators=(",", ":")) + "\n")
    except FileExistsError as exc:
        raise RouteUnavailable("MAX_CHILD_PER_ROUTE_TRANSACTION_1") from exc
    return {"decision": "ADMITTED", **admission}


def release_transaction_admission(
    common: Path,
    controller: str,
    route_transaction_id: str,
    selected_child: str,
    *,
    terminal: bool,
    expected_admission_identity: str | None = None,
) -> None:
    """Identity-fenced cleanup for a failed OPEN or terminal lifecycle."""
    if not CONTROLLER_RE.fullmatch(controller) or not HEX_RE.fullmatch(route_transaction_id):
        raise RouteUnavailable("route transaction admission cleanup identity is malformed")
    target = (
        Path(common).resolve()
        / "implementaudit-route-transactions"
        / controller
        / f"{route_transaction_id.removeprefix('sha256:')}.json"
    )
    if not target.is_file():
        raise RouteUnavailable("route transaction admission cleanup target is absent")
    try:
        record = json.loads(target.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise RouteUnavailable(f"route transaction admission cleanup target is malformed: {exc}") from exc
    if (
        not isinstance(record, dict)
        or record.get("controller_id") != controller
        or record.get("route_transaction_id") != route_transaction_id
        or record.get("selected_child") != selected_child
        or record.get("status") not in {"ACTIVE", "TERMINAL"}
        or (
            expected_admission_identity is not None
            and record.get("admission_identity") != expected_admission_identity
        )
    ):
        raise RouteUnavailable("route transaction admission cleanup fence does not match")
    if record["status"] == "TERMINAL":
        if terminal:
            return
        raise RouteUnavailable("terminal route transaction admission cannot be reopened")
    if terminal:
        successor = {**record, "status": "TERMINAL"}
        temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
        try:
            with temporary.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(successor, sort_keys=True, separators=(",", ":")) + "\n")
            os.replace(temporary, target)
        except BaseException:
            try:
                temporary.unlink()
            except OSError:
                pass
            raise
    else:
        target.unlink()


def transaction_route_ref_name(controller: str, route_transaction_id: str) -> str:
    if not CONTROLLER_RE.fullmatch(controller) or not HEX_RE.fullmatch(route_transaction_id):
        raise RouteUnavailable("canonical transaction route identity is malformed")
    return (
        f"refs/implementaudit/route-transactions/{controller}/"
        f"{route_transaction_id.removeprefix('sha256:')}"
    )


def transaction_route_ref_oid(repo: Path, controller: str, route_transaction_id: str) -> str | None:
    ref = transaction_route_ref_name(controller, route_transaction_id)
    completed = subprocess.run(
        [str(trusted_host_executable(repo, "git")), "rev-parse", "--verify", ref],
        cwd=repo,
        env=sanitized_action_environment(),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        return None
    oid = completed.stdout.strip()
    if not OID_RE.fullmatch(oid):
        raise RouteUnavailable("canonical transaction route ref is malformed")
    return oid


def transaction_route_ref_cas(
    repo: Path,
    controller: str,
    route_transaction_id: str,
    expected_oid: str | None,
    new_oid: str,
) -> None:
    if not OID_RE.fullmatch(new_oid) or (expected_oid is not None and not OID_RE.fullmatch(expected_oid)):
        raise RouteUnavailable("canonical transaction route CAS identity is malformed")
    ref = transaction_route_ref_name(controller, route_transaction_id)
    completed = subprocess.run(
        [
            str(trusted_host_executable(repo, "git")),
            "update-ref",
            ref,
            new_oid,
            expected_oid or ZERO_OID,
        ],
        cwd=repo,
        env=sanitized_action_environment(),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        raise RouteUnavailable("canonical transaction route CAS lost its identity fence")


def execution_evidence_record(
    value: Any,
    selected_child: str,
    route_transaction_id: str,
    obligation_id: str,
    packet_digest: str,
    label: str = "holon execution evidence",
) -> dict[str, Any]:
    evidence = exact_keys(
        value,
        {"schema", "selected_child", "route_transaction_id", "obligation_id", "packet_digest", "stages"},
        label,
    )
    if evidence["schema"] != EXECUTION_EVIDENCE_SCHEMA or (
        evidence["selected_child"], evidence["route_transaction_id"], evidence["obligation_id"], evidence["packet_digest"]
    ) != (selected_child, route_transaction_id, obligation_id, packet_digest):
        fail(f"{label} is foreign to the exact child delivery", decision="REQUIRED")
    if not isinstance(evidence["stages"], list) or len(evidence["stages"]) != 3:
        fail(f"{label} does not contain the exact LOAD/USE/DISPOSE receipt set", decision="REQUIRED")
    observed: list[str] = []
    receipts: set[str] = set()
    for index, item in enumerate(evidence["stages"]):
        stage = exact_keys(item, {"stage", "receipt_identity"}, f"{label}.stages[{index}]")
        if stage["stage"] not in {"LOAD", "USE", "DISPOSE"} or not HEX_RE.fullmatch(stage["receipt_identity"]):
            fail(f"{label} contains a malformed stage receipt", decision="REQUIRED")
        observed.append(stage["stage"])
        receipts.add(stage["receipt_identity"])
    if observed != ["LOAD", "USE", "DISPOSE"] or len(receipts) != 3:
        fail(f"{label} does not discriminate LOAD/USE/DISPOSE", decision="REQUIRED")
    return evidence


def _host_stage_receipt_path(store: Path, receipt_identity: str) -> Path:
    if not HEX_RE.fullmatch(receipt_identity):
        fail("host holon stage receipt identity is malformed", decision="REQUIRED")
    digest = receipt_identity.removeprefix("sha256:")
    return Path(store).resolve() / "holon-stage-receipts" / digest[:2] / f"{digest}.json"


def _host_stage_receipt_record(
    value: Any,
    owner_id: str,
    host_id: str,
    host_session_id: str,
    binding_generation: str,
    selected_child: str,
    route_transaction_id: str,
    obligation_id: str,
    packet_digest: str,
    stage: str,
) -> dict[str, Any]:
    receipt = exact_keys(
        value,
        {
            "schema", "owner_id", "host_id", "host_session_id", "binding_generation",
            "selected_child", "packet_digest", "obligation_id", "route_transaction_id",
            "stage", "event_id", "receipt_identity",
        },
        "host holon stage receipt",
    )
    body = {key: item for key, item in receipt.items() if key != "receipt_identity"}
    if (
        receipt["schema"] != HOST_STAGE_RECEIPT_SCHEMA
        or (
            receipt["owner_id"], receipt["host_id"], receipt["host_session_id"],
            receipt["binding_generation"], receipt["selected_child"],
            receipt["route_transaction_id"], receipt["obligation_id"],
            receipt["packet_digest"], receipt["stage"],
        ) != (
            owner_id, host_id, host_session_id, binding_generation, selected_child,
            route_transaction_id, obligation_id, packet_digest, stage,
        )
        or not isinstance(receipt["event_id"], str)
        or not receipt["event_id"]
        or receipt["receipt_identity"] != digest_json(body)
    ):
        fail("host holon stage receipt is absent, foreign, reused, or malformed", decision="REQUIRED")
    return receipt


def resolved_execution_evidence_record(
    value: Any,
    selected_child: str,
    route_transaction_id: str,
    obligation_id: str,
    packet_digest: str,
) -> dict[str, Any]:
    resolved = exact_keys(
        value,
        {
            "schema", "owner_id", "host_id", "host_session_id", "binding_generation",
            "selected_child", "route_transaction_id", "obligation_id", "packet_digest", "stages",
        },
        "resolved holon execution evidence",
    )
    if resolved["schema"] != RESOLVED_EXECUTION_EVIDENCE_SCHEMA:
        fail("resolved holon execution evidence schema is stale", decision="REQUIRED")
    if not isinstance(resolved["stages"], list) or len(resolved["stages"]) != 3:
        fail("resolved holon execution evidence is incomplete", decision="REQUIRED")
    expected_stages = ["LOAD", "USE", "DISPOSE"]
    receipts: set[str] = set()
    for stage, receipt in zip(expected_stages, resolved["stages"], strict=True):
        valid = _host_stage_receipt_record(
            receipt,
            resolved["owner_id"],
            resolved["host_id"],
            resolved["host_session_id"],
            resolved["binding_generation"],
            selected_child,
            route_transaction_id,
            obligation_id,
            packet_digest,
            stage,
        )
        receipts.add(valid["receipt_identity"])
    if len(receipts) != 3 or (
        resolved["selected_child"], resolved["route_transaction_id"],
        resolved["obligation_id"], resolved["packet_digest"]
    ) != (selected_child, route_transaction_id, obligation_id, packet_digest):
        fail("resolved holon execution evidence is foreign or reused", decision="REQUIRED")
    return resolved


def resolve_execution_evidence(
    store: Path,
    value: Any,
    host_id: str,
    host_session_id: str,
    binding_generation: str,
    selected_child: str,
    route_transaction_id: str,
    obligation_id: str,
    packet_digest: str,
) -> dict[str, Any]:
    """Resolve child receipt identities through the trusted host-owned store."""
    evidence = execution_evidence_record(
        value, selected_child, route_transaction_id, obligation_id, packet_digest
    )
    store = Path(store).resolve()
    try:
        owner = json.loads((store / "owner.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        fail(f"host holon receipt owner is unavailable: {exc}", decision="REQUIRED")
    if not isinstance(owner, dict) or owner != {
        "schema": "implementaudit.host-session-binding-store.v1",
        "owner_id": owner.get("owner_id") if isinstance(owner, dict) else None,
        "trusted": True,
        "enabled": True,
    } or not isinstance(owner.get("owner_id"), str) or not owner["owner_id"]:
        fail("host holon receipt owner is foreign or disabled", decision="REQUIRED")
    receipts: list[dict[str, Any]] = []
    for item in evidence["stages"]:
        target = _host_stage_receipt_path(store, item["receipt_identity"])
        try:
            if target.absolute() != target.resolve(strict=True):
                raise OSError("receipt traverses an alias")
            receipt = json.loads(target.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            fail(f"host holon stage receipt is unresolvable: {exc}", decision="REQUIRED")
        valid = _host_stage_receipt_record(
            receipt,
            owner["owner_id"],
            host_id,
            host_session_id,
            binding_generation,
            selected_child,
            route_transaction_id,
            obligation_id,
            packet_digest,
            item["stage"],
        )
        if valid["receipt_identity"] != item["receipt_identity"]:
            fail("host holon stage receipt identity differs from the child return", decision="REQUIRED")
        receipts.append(valid)
    resolved = {
        "schema": RESOLVED_EXECUTION_EVIDENCE_SCHEMA,
        "owner_id": owner["owner_id"],
        "host_id": host_id,
        "host_session_id": host_session_id,
        "binding_generation": binding_generation,
        "selected_child": selected_child,
        "route_transaction_id": route_transaction_id,
        "obligation_id": obligation_id,
        "packet_digest": packet_digest,
        "stages": receipts,
    }
    return resolved_execution_evidence_record(
        resolved, selected_child, route_transaction_id, obligation_id, packet_digest
    )


def audit_state_frontier_return_record(
    value: Any,
    capsule: dict[str, Any],
    packet_digest: str,
    obligation_id: str,
    route_transaction_id: str,
) -> dict[str, Any]:
    if capsule.get("schema") == RECOVERY_ATTEMPT_CAPSULE_SCHEMA:
        if not isinstance(value, dict):
            fail("recovery v4 return lacks explicit attempt admission", decision="REQUIRED")
        recovery_attempt_admission_record_v1(value.get("attempt_admission"))
        value = {key:item for key,item in value.items() if key != "attempt_admission"}
    if capsule.get("schema") in {RECOVERY_V3_SCHEMA, RECOVERY_ATTEMPT_CAPSULE_SCHEMA}:
        if not isinstance(value, dict) or "canonical_reconciliation" not in value:
            fail("recovery return requires its explicit canonical reconciliation proposal", decision="REQUIRED")
        recovery_reconciliation_proposal_v1(value["canonical_reconciliation"], capsule)
        # Preserve the unchanged v1 frontier checker for all existing fields.
        value = {key: item for key, item in value.items() if key != "canonical_reconciliation"}
    returned = exact_keys(
        value,
        {
            "schema", "event_id", "capsule_digest", "selected_child", "packet_digest",
            "obligation_id", "route_transaction_id", "frontier", "context_disposition",
            "holon_execution_evidence",
        },
        "audit-state minimum-frontier return",
    )
    if (
        returned["schema"] != (AUDIT_STATE_FRONTIER_RETURN_V2_SCHEMA if capsule.get("schema") == RECOVERY_ATTEMPT_CAPSULE_SCHEMA else AUDIT_STATE_FRONTIER_RETURN_SCHEMA)
        or (
            returned["event_id"], returned["capsule_digest"], returned["selected_child"],
            returned["packet_digest"], returned["obligation_id"],
            returned["route_transaction_id"], returned["context_disposition"],
        ) != (
            capsule["event_id"], capsule["capsule_digest"], "audit-state",
            packet_digest, obligation_id, route_transaction_id, "DISCARD_AFTER_RETURN",
        )
    ):
        fail("audit-state minimum-frontier return is foreign or stale", decision="REQUIRED")
    frontier = exact_keys(
        returned["frontier"],
        {"bound_identities", "unresolved_obligations", "contradictions", "next_typed_edge"},
        "audit-state minimum frontier",
    )
    expected_bound_identities = [
        {"kind": "EVENT", "identity": capsule["event_digest"]},
        {"kind": "CAPSULE", "identity": capsule["capsule_digest"]},
        {"kind": "PACKET", "identity": packet_digest},
        {"kind": "OBLIGATION", "identity": obligation_id},
        {"kind": "ROUTE_TRANSACTION", "identity": route_transaction_id},
    ]
    if frontier["bound_identities"] != expected_bound_identities:
        fail("audit-state frontier bound identities are absent, foreign, or replayed", decision="REQUIRED")

    unresolved = frontier["unresolved_obligations"]
    if not isinstance(unresolved, list) or len(unresolved) > 256:
        fail("audit-state unresolved-obligation frontier is malformed or oversized", decision="REQUIRED")
    unresolved_keys: set[tuple[str, str]] = set()
    for index, item in enumerate(unresolved):
        reference = exact_keys(
            item,
            {"obligation_id", "route_transaction_id", "state"},
            f"audit-state unresolved obligation[{index}]",
        )
        if (
            not isinstance(reference["obligation_id"], str)
            or not HEX_RE.fullmatch(reference["obligation_id"])
            or not isinstance(reference["route_transaction_id"], str)
            or not HEX_RE.fullmatch(reference["route_transaction_id"])
            or not isinstance(reference["state"], str)
            or reference["state"] not in {"UNSATISFIED", "OPEN", "RETURNED"}
        ):
            fail("audit-state unresolved-obligation reference is malformed", decision="REQUIRED")
        key = (reference["obligation_id"], reference["route_transaction_id"])
        if key in unresolved_keys:
            fail("audit-state unresolved-obligation reference is replayed", decision="REQUIRED")
        unresolved_keys.add(key)

    contradictions = frontier["contradictions"]
    if not isinstance(contradictions, list) or len(contradictions) > 256:
        fail("audit-state contradiction frontier is malformed or oversized", decision="REQUIRED")
    contradiction_keys: set[tuple[str, str, str]] = set()
    for index, item in enumerate(contradictions):
        reference = exact_keys(
            item,
            {"kind", "left_ref", "right_ref"},
            f"audit-state contradiction[{index}]",
        )
        if (
            not isinstance(reference["kind"], str)
            or reference["kind"] not in {"IDENTITY", "CURRENTNESS", "AUTHORITY", "STATE"}
            or not isinstance(reference["left_ref"], str)
            or not HEX_RE.fullmatch(reference["left_ref"])
            or not isinstance(reference["right_ref"], str)
            or not HEX_RE.fullmatch(reference["right_ref"])
            or reference["left_ref"] == reference["right_ref"]
        ):
            fail("audit-state contradiction reference is malformed", decision="REQUIRED")
        key = (reference["kind"], reference["left_ref"], reference["right_ref"])
        if key in contradiction_keys:
            fail("audit-state contradiction reference is replayed", decision="REQUIRED")
        contradiction_keys.add(key)

    edge = exact_keys(
        frontier["next_typed_edge"],
        {"kind", "target_kind", "target_ref"},
        "audit-state next typed edge",
    )
    if (
        not isinstance(edge["kind"], str)
        or edge["kind"] not in {"READY", "BLOCKED", "ACTIVE"}
        or not isinstance(edge["target_kind"], str)
        or edge["target_kind"] not in {
            "GOVERNOR_ACTION", "ROUTE_OBLIGATION", "EVIDENCE_REQUEST", "STOP"
        }
        or not isinstance(edge["target_ref"], str)
        or not HEX_RE.fullmatch(edge["target_ref"])
    ):
        fail("audit-state next typed edge is malformed", decision="REQUIRED")
    execution_evidence_record(
        returned["holon_execution_evidence"],
        "audit-state",
        route_transaction_id,
        obligation_id,
        packet_digest,
    )
    return returned


def recovery_capsule_record(value: Any, event_id: str) -> dict[str, Any]:
    capsule = exact_keys(
        value,
        {
            "schema", "event_id", "event_digest", "required_child", "mechanical_governor_actions",
            "governor_substantive_reconstruction", "return_kind",
            "return_requires_governor_reconciliation", "stale_credit",
            "worker_context_disposition", "capsule_digest",
        },
        "post-compaction recovery capsule",
    )
    event_match = re.fullmatch(r"codex-compact-v1-([0-9a-f]{64})", event_id)
    body = {key: item for key, item in capsule.items() if key != "capsule_digest"}
    if (
        capsule["schema"] != RECOVERY_CAPSULE_SCHEMA
        or event_match is None
        or capsule["event_id"] != event_id
        or capsule["event_digest"] != f"sha256:{event_match.group(1)}"
        or capsule["required_child"] != "audit-state"
        or capsule["mechanical_governor_actions"] != ["INVALIDATE", "MECHANICAL_CURRENTNESS", "OPEN_AUDIT_STATE"]
        or capsule["governor_substantive_reconstruction"] is not False
        or capsule["return_kind"] != "MINIMUM_APPLICABLE_FRONTIER"
        or capsule["return_requires_governor_reconciliation"] is not True
        or capsule["stale_credit"] is not False
        or capsule["worker_context_disposition"] != "DISCARD_AFTER_RETURN"
        or capsule["capsule_digest"] != digest_json(body)
    ):
        fail("post-compaction recovery capsule is absent, stale, foreign, or mismatched", decision="REQUIRED")
    return capsule


def post_compaction_recovery_capsule(repo: Path, request: dict[str, Any]) -> dict[str, Any] | None:
    """Load the exact capsule that a canonical compact-bound audit-state request cites."""
    event_id = request["boundary"]["event_id"]
    if mechanical_required_reason(request["action"]["argv"]) != "STALE_CONTEXT_RECONSTRUCTION" or not event_id.startswith(
        "codex-compact-v1-"
    ):
        return None
    identity = f"post-compaction-recovery-capsule:{event_id}"
    matches = [item for item in request["inputs"] if item["identity"] == identity]
    if len(matches) != 1:
        fail("canonical audit-state routing requires one exact post-compaction capsule", decision="REQUIRED")
    target = (repo / matches[0]["path"]).resolve()
    try:
        target.relative_to(repo.resolve())
        raw = target.read_bytes()
        if target.absolute() != target.resolve(strict=True) or len(raw) > 100_000:
            raise OSError("unsafe recovery capsule")
        value = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        fail(f"post-compaction recovery capsule is unreadable: {exc}", decision="REQUIRED")
    if bytes_identity(raw)["digest"] != matches[0]["digest"]:
        fail("post-compaction recovery capsule bytes differ from the canonical request", decision="REQUIRED")
    return recovery_capsule_record(value, event_id)


def consume_recovery_capsule(common: Path, controller: str, capsule: dict[str, Any]) -> None:
    """Make one exact compact event single-use at the live OPEN boundary."""
    directory = Path(common).resolve() / "implementaudit-recovery-capsules" / controller
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{capsule['capsule_digest'].removeprefix('sha256:')}.used"
    try:
        with target.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(capsule["event_id"] + "\n")
    except FileExistsError as exc:
        raise RouteUnavailable("post-compaction recovery capsule was reused") from exc


def release_recovery_capsule(common: Path, controller: str, capsule: dict[str, Any]) -> None:
    """Release only this exact capsule after a pre-CAS OPEN failure."""
    target = (
        Path(common).resolve()
        / "implementaudit-recovery-capsules"
        / controller
        / f"{capsule['capsule_digest'].removeprefix('sha256:')}.used"
    )
    try:
        observed = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise RouteUnavailable(f"post-compaction capsule cleanup target is unavailable: {exc}") from exc
    if observed != capsule["event_id"] + "\n":
        raise RouteUnavailable("post-compaction capsule cleanup fence does not match")
    target.unlink()


def holon_lifecycle_projection(
    route_state: str,
    selected_child: str,
    route_transaction_id: str,
    obligation_id: str,
    *,
    execution_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project the identity-bound governed lifecycle without granting child authority."""
    completed_by_state = {
        "UNSATISFIED": (),
        "OPEN": ("OPEN",),
        "RETURNED": ("OPEN", "RETURN"),
        "SATISFIED": ("OPEN", "RETURN", "RECONCILE"),
    }
    children = {child for child, _ in CHILD_ROUTE_MAP.values()}
    if route_state not in completed_by_state:
        fail("holon lifecycle state is not canonical", decision="REQUIRED")
    if selected_child not in children:
        fail("holon lifecycle child identity is not canonical", decision="REQUIRED")
    if not HEX_RE.fullmatch(route_transaction_id) or not HEX_RE.fullmatch(obligation_id):
        fail("holon lifecycle route identity is malformed", decision="REQUIRED")
    completed = set(completed_by_state[route_state])
    if execution_evidence is not None:
        evidence = resolved_execution_evidence_record(
            execution_evidence,
            selected_child,
            route_transaction_id,
            obligation_id,
            execution_evidence.get("packet_digest", "") if isinstance(execution_evidence, dict) else "",
        )
        completed.update(stage["stage"] for stage in evidence["stages"])
    ordered_completed = [stage for stage in HOLON_LIFECYCLE_SEQUENCE if stage in completed]
    unverified = [stage for stage in ("LOAD", "USE", "DISPOSE") if stage not in completed]
    reconciled = route_state == "SATISFIED"
    return {
        "required_sequence": list(HOLON_LIFECYCLE_SEQUENCE),
        "completed": ordered_completed,
        "selected_child": selected_child,
        "route_transaction_id": route_transaction_id,
        "obligation_id": obligation_id,
        "identity_bound": True,
        "unverified": unverified,
        "child_authority": "NONE",
        "child_can_route": False,
        "governor_reconciliation_required": not reconciled,
        "canonical_credit": reconciled and not unverified,
    }


def abnormality_route(
    abnormality: str,
    *,
    deterministic_mechanical_resolution: bool,
    known_countermeasure_falsified: bool = False,
    new_causal_mechanism_required: bool = False,
    requester: str = "governor",
) -> dict[str, Any]:
    """Separate governor mechanics from governed abnormality cognition."""
    if not isinstance(abnormality, str) or not abnormality:
        fail("abnormality identity is malformed")
    if requester != "governor":
        return {
            "decision": "STOP_CHILD_TO_CHILD_DISPATCH",
            "return_to_governor": True,
            "authority_ceiling": "NONE",
        }
    substantive = (
        not deterministic_mechanical_resolution
        or known_countermeasure_falsified
        or new_causal_mechanism_required
    )
    if substantive:
        return {
            "route": "audit-andon",
            "owner": "GOVERNED_CHILD_COGNITION",
            "governor_diagnosis": False,
            "authority_ceiling": "NONE",
        }
    return {
        "route": "NONE",
        "owner": "GOVERNOR_MECHANICAL",
        "governor_diagnosis": False,
        "authority_ceiling": "NONE",
    }


def require_governor_dispatch_requester(requester: str) -> None:
    """Enforce that governed children return; they never become dispatchers."""
    if requester == "governor":
        return
    if requester in {child for child, _ in CHILD_ROUTE_MAP.values()}:
        raise RouteUnavailable("STOP_CHILD_TO_CHILD_DISPATCH")
    raise RouteUnavailable("dispatch requester identity is not canonical")


def normalized_history_query(request: dict[str, Any]) -> dict[str, Any] | None:
    argv = request["action"]["argv"]
    if len(argv) < 2 or argv[:2] != ["route-trigger", "QUERY_HISTORY_THEN_RESUME"]:
        return None
    if len(argv) != 3 or not EVENT_ID_RE.fullmatch(argv[2]):
        fail("history query requires one exact immutable evidence identity")
    return {
        "schema": "implementaudit.history-query-request.v1",
        "route": "QUERY_HISTORY_THEN_RESUME",
        "requirement": "REQUIRED",
        "evidence_ids": [argv[2]],
    }


def classify(request: dict[str, Any], noncurrent: list[str]) -> tuple[str, str, list[str]]:
    judgement = [item for item in noncurrent if item.endswith(":JUDGEMENT_REQUIRED")]
    if judgement:
        return "REQUIRED", "JUDGEMENT_REQUIRED", judgement
    if noncurrent:
        return "PENDING", "JUDGEMENT_REQUIRED", noncurrent
    required_reason = mechanical_required_reason(request["action"]["argv"])
    if required_reason is not None:
        return "REQUIRED", "MECHANICALLY_REQUIRED", [required_reason]
    history_query = normalized_history_query(request)
    if history_query is not None:
        return "REQUIRED", "JUDGEMENT_REQUIRED", [f"history-evidence:{history_query['evidence_ids'][0]}"]
    derived = mechanical_action_class(request["action"]["argv"])
    if derived is None or request["action"]["class"] != derived or derived not in CLOSED_ACTION_CLASSES:
        return "REQUIRED", "JUDGEMENT_REQUIRED", ["route judgement cannot mint NOT_REQUIRED"]
    return "NOT_REQUIRED", "MECHANICALLY_NOT_REQUIRED", []


def repo_context() -> tuple[Path, str, str]:
    repo = Path(git(Path.cwd(), "rev-parse", "--path-format=absolute", "--show-toplevel")).resolve()
    common = str(Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve())
    return repo, str(repo), common


def ref_name(controller: str) -> str:
    if not CONTROLLER_RE.fullmatch(controller):
        fail("controller identity is not canonical")
    return f"refs/implementaudit/route-decisions/{controller}"


class RouteObjectReader:
    """One bounded, cached Git batch reader for a route-history validation."""

    def __init__(self, repo: Path) -> None:
        self.repo = repo
        self.started = time.monotonic()
        self.cache: dict[str, bytes] = {}
        self.total_bytes = 0
        self.process: subprocess.Popen[bytes] | None = None
        self.io_requests: queue.Queue[Any] = queue.Queue()
        self.io_worker: threading.Thread | None = None

    def __enter__(self) -> "RouteObjectReader":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def check_elapsed(self) -> None:
        if time.monotonic() - self.started > MAX_ROUTE_LINEAGE_ELAPSED_SECONDS:
            fail("route history resource budget exceeded: elapsed-work")

    def remaining_elapsed(self) -> float:
        remaining = MAX_ROUTE_LINEAGE_ELAPSED_SECONDS - (time.monotonic() - self.started)
        if remaining <= 0:
            fail("route history resource budget exceeded: elapsed-work")
        return remaining

    def start(self) -> None:
        if self.process is not None:
            return
        self.process = subprocess.Popen(
            [str(trusted_host_executable(self.repo, "git")), "cat-file", "--batch"],
            cwd=self.repo,
            env=sanitized_action_environment(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        if self.process.stdin is None or self.process.stdout is None:
            fail("route history batch reader has no exact input/output stream")

        self.io_worker = threading.Thread(
            target=self.io_loop,
            name="implementaudit-route-object-reader",
            daemon=True,
        )
        self.io_worker.start()

    def io_loop(self) -> None:
        while True:
            request = self.io_requests.get()
            if request is None:
                return
            operation, result = request
            try:
                result.put((True, operation()))
            except BaseException as exc:
                result.put((False, exc))

    def deadline_io(self, operation: Any, label: str) -> Any:
        self.check_elapsed()
        timeout = self.remaining_elapsed()
        result: queue.Queue[Any] = queue.Queue(maxsize=1)
        self.io_requests.put_nowait((operation, result))
        try:
            succeeded, payload = result.get(timeout=timeout)
        except queue.Empty:
            self.abort()
            fail("route history resource budget exceeded: elapsed-work")
        if not succeeded:
            self.abort()
            if isinstance(payload, (OSError, ValueError)):
                fail(f"{label} blob is unreadable")
            raise payload
        self.check_elapsed()
        return payload

    @staticmethod
    def close_streams(process: Any) -> None:
        for stream in (process.stdin, process.stdout):
            if stream is not None:
                with contextlib.suppress(OSError, ValueError):
                    stream.close()

    def shutdown(self, *, force: bool) -> None:
        process = self.process
        worker = self.io_worker
        self.process = None
        self.io_worker = None
        if process is None:
            return
        if force:
            with contextlib.suppress(OSError):
                if process.poll() is None:
                    process.kill()
        self.io_requests.put_nowait(None)
        if worker is not None:
            worker.join(timeout=2)
        if process.stdin is not None:
            with contextlib.suppress(OSError, ValueError):
                process.stdin.close()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(OSError):
                process.kill()
            with contextlib.suppress(OSError, subprocess.TimeoutExpired):
                process.wait(timeout=2)
        self.close_streams(process)

    def abort(self) -> None:
        self.shutdown(force=True)

    def close(self) -> None:
        self.shutdown(force=False)

    def read_exact(self, stream: Any, size: int, label: str) -> bytes:
        parts: list[bytes] = []
        remaining = size
        while remaining:
            part = self.deadline_io(lambda: stream.read(remaining), label)
            if not part:
                self.abort()
                fail(f"{label} blob is unreadable")
            parts.append(part)
            remaining -= len(part)
        return b"".join(parts)

    def read(self, oid: str, label: str) -> bytes:
        self.check_elapsed()
        if oid in self.cache:
            return self.cache[oid]
        if len(self.cache) >= MAX_ROUTE_LINEAGE_RECORDS:
            fail("route history resource budget exceeded: record-count")
        if not OID_RE.fullmatch(oid):
            fail(f"{label} identity is malformed")
        self.start()
        assert self.process is not None and self.process.stdin is not None and self.process.stdout is not None

        def send_request() -> None:
            self.process.stdin.write(oid.encode("ascii") + b"\n")
            self.process.stdin.flush()
        self.deadline_io(send_request, label)
        header = self.deadline_io(
            lambda: self.process.stdout.readline(MAX_CAT_FILE_HEADER_BYTES + 1),
            label,
        )
        if not header.endswith(b"\n") or len(header) > MAX_CAT_FILE_HEADER_BYTES:
            self.abort()
            fail(f"{label} blob is unreadable")
        fields = header[:-1].split(b" ")
        if len(fields) != 3 or fields[0] != oid.encode("ascii") or fields[1] != b"blob":
            self.abort()
            fail(f"{label} blob is unreadable")
        try:
            size = int(fields[2])
        except ValueError:
            self.abort()
            fail(f"{label} blob is unreadable")
        if size < 0 or size > MAX_ROUTE_RECORD_BYTES:
            self.abort()
            fail("route history resource budget exceeded: per-record-bytes")
        if self.total_bytes + size > MAX_ROUTE_LINEAGE_BYTES:
            self.abort()
            fail("route history resource budget exceeded: cumulative-bytes")
        raw = self.read_exact(self.process.stdout, size, label)
        trailer = self.read_exact(self.process.stdout, 1, label)
        if trailer != b"\n":
            self.abort()
            fail(f"{label} blob is unreadable")
        self.cache[oid] = raw
        self.total_bytes += size
        self.check_elapsed()
        return raw


def current_ref(
    repo: Path,
    controller: str,
    *,
    allow_immutable_terminal_child: bool = False,
    allow_immutable_active_child: bool = False,
    route_transaction_id: str | None = None,
) -> tuple[str | None, dict[str, Any] | None]:
    ref = (
        transaction_route_ref_name(controller, route_transaction_id)
        if route_transaction_id is not None
        else ref_name(controller)
    )
    completed = subprocess.run(
        [str(trusted_host_executable(repo, "git")), "rev-parse", "--verify", ref],
        cwd=repo,
        env=sanitized_action_environment(),
        text=True,
        capture_output=True,
    )
    if completed.returncode:
        return None, None
    oid = completed.stdout.strip()
    with RouteObjectReader(repo) as object_reader:
        record = decoded_artifact(
            object_reader.read(oid, "current route record"), "current route record"
        )
        if route_transaction_id is None and record.get("schema") == RECOVERY_RECORD_SCHEMA:
            fail("recovery record cannot occupy ordinary route custody", decision="REQUIRED")
        if route_transaction_id is not None and record.get("route_transaction_id") != route_transaction_id:
            fail("canonical transaction route ref names a foreign record", decision="REQUIRED")
        validate_route_record_semantics(
            repo,
            controller,
            oid,
            record,
            allow_immutable_terminal_child=allow_immutable_terminal_child,
            allow_immutable_active_child=allow_immutable_active_child,
            object_reader=object_reader,
        )
    return oid, record


def git_blob_bytes(
    repo: Path, oid: str, label: str, *, object_reader: Any | None = None
) -> bytes:
    if object_reader is not None:
        return object_reader.read(oid, label)
    completed = subprocess.run(
        [str(trusted_host_executable(repo, "git")), "cat-file", "blob", oid],
        cwd=repo,
        env=sanitized_action_environment(),
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        fail(f"{label} blob is unreadable")
    return completed.stdout


def validate_canonical_route_record_bytes(
    repo: Path, oid: str, record: dict[str, Any], *, object_reader: Any | None = None
) -> None:
    route_raw = git_blob_bytes(
        repo, oid, "route record", object_reader=object_reader
    )
    try:
        canonical_route_raw = json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8") + b"\n"
    except (TypeError, ValueError):
        fail("route record cannot be encoded as canonical JSON")
    if route_raw != canonical_route_raw:
        fail("route record bytes are not exact canonical JSON")


def validate_route_record_semantics(
    repo: Path,
    controller: str,
    oid: str,
    record: dict[str, Any],
    *,
    allow_immutable_terminal_child: bool = False,
    allow_immutable_active_child: bool = False,
    predecessor_seen: frozenset[str] = frozenset(),
    predecessor_depth: int = 0,
    object_reader: Any | None = None,
) -> None:
    """Validate one canonical record and all historical authority iteratively."""
    del predecessor_depth
    if object_reader is None:
        with RouteObjectReader(repo) as owned_reader:
            validate_route_record_worklist(
                repo,
                controller,
                oid,
                record,
                allow_immutable_terminal_child=allow_immutable_terminal_child,
                allow_immutable_active_child=allow_immutable_active_child,
                predecessor_seen=predecessor_seen,
                object_reader=owned_reader,
            )
        return
    validate_route_record_worklist(
        repo,
        controller,
        oid,
        record,
        allow_immutable_terminal_child=allow_immutable_terminal_child,
        allow_immutable_active_child=allow_immutable_active_child,
        predecessor_seen=predecessor_seen,
        object_reader=object_reader,
    )


def validate_route_record_worklist(
    repo: Path,
    controller: str,
    oid: str,
    record: dict[str, Any],
    *,
    allow_immutable_terminal_child: bool,
    allow_immutable_active_child: bool,
    predecessor_seen: frozenset[str],
    object_reader: Any,
) -> None:
    worklist = [
        (
            oid,
            record,
            allow_immutable_terminal_child,
            allow_immutable_active_child,
        )
    ]
    seen = set(predecessor_seen)
    while worklist:
        if hasattr(object_reader, "check_elapsed"):
            object_reader.check_elapsed()
        current_oid, current, allow_terminal, allow_active = worklist.pop()
        if current_oid in seen:
            fail("route record predecessor chain contains a cycle")
        seen.add(current_oid)
        dependency = validate_route_record_local(
            repo,
            controller,
            current_oid,
            current,
            allow_immutable_terminal_child=allow_terminal,
            allow_immutable_active_child=allow_active,
            predecessor_seen=frozenset(seen),
            object_reader=object_reader,
        )
        if dependency is not None:
            worklist.append(dependency)


def validate_route_record_local(
    repo: Path,
    controller: str,
    oid: str,
    record: dict[str, Any],
    *,
    allow_immutable_terminal_child: bool,
    allow_immutable_active_child: bool,
    predecessor_seen: frozenset[str],
    object_reader: Any,
) -> tuple[str, dict[str, Any], bool, bool] | None:
    if (isinstance(record, dict) and record.get("schema") == RECOVERY_RECORD_SCHEMA
            and record.get("route_state") == "ABANDONED"):
        validate_canonical_route_record_bytes(repo, oid, record, object_reader=object_reader)
        predecessor_oid = record.get("predecessor_record_oid")
        if not isinstance(predecessor_oid, str) or not OID_RE.fullmatch(predecessor_oid):
            fail("abandonment predecessor identity is malformed", decision="REQUIRED")
        predecessor = decoded_artifact(git_blob_bytes(repo, predecessor_oid,
            "abandoned recovery predecessor", object_reader=object_reader), "abandoned recovery predecessor")
        validate_recovery_abandonment_v1(record, predecessor_oid, predecessor)
        return predecessor_oid, predecessor, True, True
    if isinstance(record, dict) and record.get("schema") == RECOVERY_RECORD_SCHEMA:
        recovery_record_header_v1(record, controller)
        lifecycle_present = "lifecycle" in record
        lifecycle = record.get("lifecycle")
        validate_canonical_route_record_bytes(repo, oid, record, object_reader=object_reader)
    else:
        if (
            not isinstance(record, dict)
            or frozenset(record) - {"presentation"} not in {
                frozenset(RECORD_KEYS),
                frozenset(HISTORY_RECORD_KEYS),
                frozenset(LIFECYCLE_RECORD_KEYS),
                frozenset(HISTORY_LIFECYCLE_RECORD_KEYS),
            }
            or record.get("schema") != RECORD_SCHEMA
        ):
            fail("current route record is malformed or mixed-version")
        if "presentation" in record:
            validate_presentation(record["presentation"])
        if "history_query" in record and record["history_query"] != normalized_history_query(record):
            fail("current route record has a malformed history-query request")
        lifecycle_present = "lifecycle" in record
        lifecycle = record.get("lifecycle")
        if (
            record.get("predicate_version") != PREDICATE_VERSION
            or record.get("controller_id") != controller
            or record.get("decision") not in DECISIONS
            or record.get("expires_on") != EXPIRES_ON
            or record.get("child_lifecycle_owned") is not lifecycle_present
        ):
            fail("current route record has foreign identity or invalid decision")
        if record["decision"] == "REQUIRED":
            allowed_states = {"UNSATISFIED"} if not lifecycle_present else {"OPEN", "RETURNED", "SATISFIED"}
            if record.get("route_state") not in allowed_states or not isinstance(record.get("obligation_id"), str):
                fail("current required route record has no unsatisfied obligation")
        elif record.get("route_state") is not None or record.get("obligation_id") is not None:
            fail("non-required route record improperly owns an obligation")
        if record.get("classification") not in CLASSIFICATIONS or record.get("record_identity") != digest_json(
            {key: value for key, value in record.items() if key != "record_identity"}
        ):
            fail("current route record identity is invalid")
        validate_canonical_route_record_bytes(
            repo, oid, record, object_reader=object_reader
        )
    if lifecycle_present:
        lifecycle_keys = {
            "state", "required_record_oid", "delivery", "child_return", "governor_decision",
            "governor_decision_count", "source_event_status",
        }
        attempt_variant = (record.get("schema") == RECOVERY_RECORD_SCHEMA
            and record["recovery_capsule"]["schema"] == RECOVERY_ATTEMPT_CAPSULE_SCHEMA)
        if attempt_variant:
            lifecycle_keys.add("attempt_evidence")
        if not isinstance(lifecycle, dict) or set(lifecycle) not in {
            frozenset(lifecycle_keys | extra) for extra in
            (set(), {"execution_evidence"}, {"logical_task"}, {"execution_evidence", "logical_task"})
        }:
            fail("route lifecycle has the wrong shape")
        if "logical_task" in lifecycle:
            logical_task_name(lifecycle["logical_task"], mapped_child_route(record)[0],
                              record.get("route_transaction_id"), record.get("host_session_id"))
        if attempt_variant:
            recovery_attempt_evidence_record_v1(lifecycle["attempt_evidence"], record["recovery_capsule"])
        delivery = exact_keys(lifecycle["delivery"], {"child", "packet"}, "route lifecycle delivery")
        child_raw = validate_bytes_identity(delivery["child"], "route lifecycle child", with_identity=True)
        packet_raw = validate_bytes_identity(delivery["packet"], "route lifecycle packet")
        mapped_child, _ = mapped_child_route(record)
        immutable_terminal_child = (
            allow_immutable_terminal_child
            and record.get("decision") == "REQUIRED"
            and record.get("route_state") == "SATISFIED"
            and lifecycle.get("state") == "SATISFIED"
            and lifecycle.get("source_event_status") == "satisfied"
        )
        immutable_active_child = (
            allow_immutable_active_child
            and record.get("decision") == "REQUIRED"
            and record.get("route_state") in {"OPEN", "RETURNED"}
            and lifecycle.get("state") == record.get("route_state")
            and lifecycle.get("source_event_status") == "active"
        )
        if immutable_terminal_child or immutable_active_child:
            bound_child = exact_keys(
                record.get("child_source"), {"identity", "digest"}, "bound route child source"
            )
            if delivery["child"].get("identity") != bound_child["identity"] or (
                delivery["child"].get("digest") != bound_child["digest"]
            ):
                fail("route lifecycle child is foreign to the bound route decision")
        else:
            exact_child_raw, exact_child_path = child_delivery_bytes(mapped_child, expected_identity_inputs=record.get("package", {}).get("source_digests", {}))
            exact_child = {"identity": str(exact_child_path), **bytes_identity(exact_child_raw)}
            if delivery["child"] != exact_child or child_raw != exact_child_raw:
                fail("route lifecycle child is not the exact mapped current child source")
            if record.get("child_source") != {
                "identity": exact_child["identity"], "digest": exact_child["digest"]
            }:
                fail("route lifecycle child is foreign to the bound route decision")
        packet = route_packet_record(
            decoded_artifact(packet_raw, "route lifecycle packet"),
            record["obligation_id"],
            record["route_transaction_id"],
            "route lifecycle packet",
            expected_target=mapped_child,
        )
        if record.get("schema") == RECOVERY_RECORD_SCHEMA:
            validate_recovery_packet_v3(packet, record["recovery_capsule"], record["host_correlation_id"])
        returned_raw = None
        if lifecycle["child_return"] is not None:
            returned_raw = validate_bytes_identity(lifecycle["child_return"], "route lifecycle child return")
            returned = child_return_record(
                decoded_artifact(returned_raw, "route lifecycle child return"),
                record["obligation_id"],
                record["route_transaction_id"],
                delivery["packet"]["digest"],
                "route lifecycle child return",
                expected_child=mapped_child,
                expected_capsule=record.get("recovery_capsule"),
            )
            if attempt_variant:
                recovery_attempt_admission_record_v1(returned["payload"].get("attempt_admission"),
                    lifecycle["attempt_evidence"]["evidence_digest"])
            raw_execution = returned["payload"].get("holon_execution_evidence")
            resolved_execution = lifecycle.get("execution_evidence")
            if (raw_execution is None) != (resolved_execution is None):
                fail("route lifecycle execution evidence differs from the exact child return")
            if raw_execution is not None:
                shaped = execution_evidence_record(
                    raw_execution,
                    mapped_child,
                    record["route_transaction_id"],
                    record["obligation_id"],
                    delivery["packet"]["digest"],
                )
                resolved = resolved_execution_evidence_record(
                    resolved_execution,
                    mapped_child,
                    record["route_transaction_id"],
                    record["obligation_id"],
                    delivery["packet"]["digest"],
                )
                if [item["receipt_identity"] for item in shaped["stages"]] != [
                    item["receipt_identity"] for item in resolved["stages"]
                ]:
                    fail("route lifecycle host receipts differ from the child return identities")
        elif lifecycle.get("execution_evidence") is not None:
            fail("route lifecycle execution evidence exists before the exact child return")
        if lifecycle["governor_decision"] is not None:
            decision_raw = validate_bytes_identity(
                lifecycle["governor_decision"], "route lifecycle governor decision"
            )
            if returned_raw is None:
                fail("route lifecycle governor decision has no exact child return")
            governor_decision_record(
                decoded_artifact(decision_raw, "route lifecycle governor decision"),
                record["obligation_id"],
                record["route_transaction_id"],
                bytes_identity(returned_raw)["digest"],
                "route lifecycle governor decision",
            )
        if lifecycle["source_event_status"] not in {"active", "satisfied"}:
            fail("route lifecycle source-event status is malformed")
        if lifecycle["state"] != record["route_state"] or not OID_RE.fullmatch(lifecycle["required_record_oid"]):
            fail("route lifecycle state or required-record identity is malformed")
        expected_source_status = (
            "satisfied"
            if lifecycle["state"] == "SATISFIED" and packet["source_event"]["kind"] == "one-shot-action"
            else "active"
        )
        if lifecycle["source_event_status"] != expected_source_status:
            fail("route lifecycle source-event status contradicts its exact packet and state")
        if lifecycle["state"] == "OPEN" and (
            lifecycle["child_return"] is not None
            or lifecycle["governor_decision"] is not None
            or lifecycle["governor_decision_count"] != 0
        ):
            fail("open route lifecycle contains return or decision evidence")
        if lifecycle["state"] == "RETURNED" and (
            not isinstance(lifecycle["child_return"], dict)
            or lifecycle["governor_decision"] is not None
            or lifecycle["governor_decision_count"] != 0
        ):
            fail("returned route lifecycle has malformed return or decision evidence")
        if lifecycle["state"] == "SATISFIED" and (
            not isinstance(lifecycle["child_return"], dict)
            or not isinstance(lifecycle["governor_decision"], dict)
            or lifecycle["governor_decision_count"] != 1
        ):
            fail("satisfied route lifecycle does not contain exactly one governor decision")
        required_oid = lifecycle["required_record_oid"]
        required = decoded_artifact(
            git_blob_bytes(
                repo,
                required_oid,
                "required route record",
                object_reader=object_reader,
            ),
            "required route record",
        )
        validate_required_route_record_relation(required, record)
        validate_lifecycle_predecessor_chain(
            repo,
            oid,
            record,
            predecessor_seen=predecessor_seen,
            object_reader=object_reader,
        )
        return required_oid, required, True, True

    predecessor_oid = record.get("predecessor_record_oid")
    if predecessor_oid is None:
        return None
    if not isinstance(predecessor_oid, str) or not OID_RE.fullmatch(predecessor_oid):
        fail("route record predecessor identity is malformed")
    predecessor = decoded_artifact(
        git_blob_bytes(
            repo,
            predecessor_oid,
            "route record predecessor",
            object_reader=object_reader,
        ),
        "route record predecessor",
    )
    return predecessor_oid, predecessor, True, True


def validate_required_route_record_relation(
    required: dict[str, Any],
    lifecycle_record: dict[str, Any],
) -> None:
    if (
        required.get("decision") != "REQUIRED"
        or required.get("route_state") != "UNSATISFIED"
        or required.get("child_lifecycle_owned") is not False
    ):
        fail("required route record is not an exact unsatisfied authority record")
    inherited = set(RECOVERY_RECORD_KEYS if lifecycle_record.get("schema") == RECOVERY_RECORD_SCHEMA else RECORD_KEYS) - {
        "record_identity", "predecessor_record_oid", "route_state", "child_lifecycle_owned"
    }
    if any(required.get(key) != lifecycle_record.get(key) for key in inherited):
        fail("route lifecycle is foreign to its required authority record")
    if required.get("history_query") != lifecycle_record.get("history_query"):
        fail("route lifecycle changed its required history-query authority")
    if required.get("presentation") != lifecycle_record.get("presentation"):
        fail("route lifecycle changed its bound presentation custody")


def validate_lifecycle_predecessor_chain(
    repo: Path,
    record_oid: str,
    record: dict[str, Any],
    *,
    predecessor_seen: frozenset[str] = frozenset(),
    object_reader: Any | None = None,
) -> None:
    del record_oid
    seen = set(predecessor_seen)
    current = record
    while True:
        lifecycle = current["lifecycle"]
        state = lifecycle["state"]
        if state == "OPEN":
            if current.get("predecessor_record_oid") != lifecycle["required_record_oid"]:
                fail("open route lifecycle does not directly succeed its required authority")
            return
        predecessor_oid = current.get("predecessor_record_oid")
        if not isinstance(predecessor_oid, str) or not OID_RE.fullmatch(predecessor_oid):
            fail("route lifecycle predecessor identity is malformed")
        if predecessor_oid in seen:
            fail("route lifecycle predecessor chain contains a cycle")
        seen.add(predecessor_oid)
        predecessor = decoded_artifact(
            git_blob_bytes(
                repo,
                predecessor_oid,
                "route lifecycle predecessor",
                object_reader=object_reader,
            ),
            "route lifecycle predecessor",
        )
        if set(predecessor) != set(current) or predecessor.get("record_identity") != digest_json(
            {key: value for key, value in predecessor.items() if key != "record_identity"}
        ):
            fail("route lifecycle predecessor is not an exact canonical record")
        invariant_keys = set(current) - {
            "record_identity", "predecessor_record_oid", "route_state", "lifecycle"
        }
        if any(predecessor.get(key) != current.get(key) for key in invariant_keys):
            fail("route lifecycle predecessor changed immutable route authority")
        predecessor_lifecycle = predecessor.get("lifecycle")
        if not isinstance(predecessor_lifecycle, dict):
            fail("route lifecycle predecessor has no lifecycle authority")
        expected_state = (
            "OPEN" if state == "RETURNED" else "RETURNED" if state == "SATISFIED" else None
        )
        if expected_state is None or predecessor.get("route_state") != expected_state:
            fail("route lifecycle predecessor skips a canonical state transition")
        expected_lifecycle = {
            **lifecycle,
            "state": expected_state,
            "governor_decision": None,
            "governor_decision_count": 0,
            "source_event_status": "active",
        }
        if expected_state == "OPEN":
            expected_lifecycle["child_return"] = None
            if "execution_evidence" in predecessor_lifecycle:
                expected_lifecycle["execution_evidence"] = None
            else:
                expected_lifecycle.pop("execution_evidence", None)
        if predecessor_lifecycle != expected_lifecycle:
            fail("route lifecycle predecessor evidence does not match its successor")
        validate_canonical_route_record_bytes(
            repo, predecessor_oid, predecessor, object_reader=object_reader
        )
        current = predecessor


def bash_script_path(path: Path) -> str:
    resolved = str(path.resolve())
    if os.name != "nt":
        return resolved
    drive, tail = os.path.splitdrive(resolved)
    if len(drive) != 2 or drive[1] != ":":
        fail("shell action path is not on an exact local drive")
    return f"/{drive[0].lower()}{tail.replace(os.sep, '/')}"


def recovery_custody_record_v1(value: Any) -> dict[str, Any]:
    """Validate observation bytes as data, never as route/currentness authority."""
    record = exact_keys(value, {
        "schema", "subject", "subject_digest", "input_adapter_digest",
        "genuine_host_evidence", "continuity_current", "ordinary_effect_authority",
        "route_open_authority", "record_identity",
    }, "recovery custody record")
    subject = exact_keys(record["subject"], {
        "schema", "controller_id", "controller_oid", "claim_id", "repository_identity",
        "explicit_run_root", "predecessor_epoch", "predecessor_receipt", "pointer_oid",
        "marker_oid", "subject_invalidation_oid", "subject_boundary_kind",
        "subject_boundary_event_id", "host_binding_generation", "host_binding_digest",
        "hot_input_digests", "genuine_host_evidence", "continuity_current",
        "ordinary_effect_authority", "route_open_authority",
    }, "recovery custody subject")
    if (record["schema"] != RECOVERY_CUSTODY_SCHEMA
            or subject["schema"] != "implementaudit.recovery-subject-observation.v1"
            or record["input_adapter_digest"] != RECOVERY_INPUT_ADAPTER_DIGEST):
        fail("recovery custody schema or owner source is foreign", decision="REQUIRED")
    for item in (record, subject):
        if (item["genuine_host_evidence"] != "UNVERIFIED"
                or item["continuity_current"] is not False
                or item["ordinary_effect_authority"] != "NONE"
                or item["route_open_authority"] != "NONE"):
            fail("recovery custody cannot claim native proof or authority", decision="REQUIRED")
    for key, pattern in (
        ("controller_id", CONTROLLER_RE), ("claim_id", re.compile(r"[0-9a-f]{32}")),
        ("controller_oid", OID_RE), ("pointer_oid", OID_RE), ("marker_oid", OID_RE),
        ("subject_invalidation_oid", OID_RE), ("predecessor_epoch", CONTINUITY_RE),
        ("host_binding_generation", CONTINUITY_RE), ("host_binding_digest", HEX_RE),
    ):
        if not isinstance(subject[key], str) or not pattern.fullmatch(subject[key]):
            fail(f"recovery custody {key} is malformed", decision="REQUIRED")
    if subject["predecessor_epoch"] == "G0000" or subject["host_binding_generation"] == "G0000":
        fail("recovery custody has no predecessor or active binding", decision="REQUIRED")
    prefix = (f"refs/implementaudit/continuity-receipts/{subject['controller_id']}/"
              f"{subject['predecessor_epoch']}@")
    receipt = exact_text(subject["predecessor_receipt"], "recovery predecessor receipt")
    if not receipt.startswith(prefix) or not OID_RE.fullmatch(receipt[len(prefix):]):
        fail("recovery custody predecessor receipt is foreign", decision="REQUIRED")
    for key in ("repository_identity", "explicit_run_root"):
        if not Path(exact_text(subject[key], "recovery " + key)).is_absolute():
            fail("recovery custody path is not absolute", decision="REQUIRED")
    exact_text(subject["subject_boundary_event_id"], "recovery subject boundary event")
    if not isinstance(subject["subject_boundary_kind"], str) or subject["subject_boundary_kind"] not in {
        "host-reported-compaction", "new-session", "handoff-resume", "manual-resume",
        "inferred-context-gap",
    }:
        fail("recovery custody boundary kind is foreign", decision="REQUIRED")
    hot = exact_keys(subject["hot_input_digests"], {"STATE", "ROADMAP", "WORK_GRAPH"}, "recovery hot identities")
    if any(not isinstance(item, str) or not re.fullmatch(r"[0-9a-f]{64}", item) for item in hot.values()):
        fail("recovery custody hot identity is malformed", decision="REQUIRED")
    if (record["subject_digest"] != digest_json(subject)
            or record["record_identity"] != digest_json({
                key: item for key, item in record.items() if key != "record_identity"})):
        fail("recovery custody record identity differs", decision="REQUIRED")
    return record


def observe_recovery_custody_v1(repo: Path) -> dict[str, Any]:
    """Read the exact adjacent owner; grant no recovery admission or native proof."""
    adapter = Path(__file__).with_name("codex-recovery-prompt-input.py").absolute()
    # Reuse the frozen input adapter's physical-owner loader without supplying a
    # synthetic hook envelope. Its four owner-source pins remain unchanged.
    script = """import hashlib,json,os,pathlib,sys,types
path = pathlib.Path(sys.argv[1])
raw = path.read_bytes()
if 'sha256:' + hashlib.sha256(raw).hexdigest() != sys.argv[2]:
    raise RuntimeError('recovery input adapter source differs')
module = types.ModuleType('_route_recovery_owner_loader')
module.__file__ = str(path)
sys.modules[module.__name__] = module
exec(compile(raw, str(path), 'exec'), module.__dict__)
# Derive the physical owner layout from the verified adjacent adapter.
# The host session remains unchanged; the existing owner/H0 join validates it.
root = path.parents[3]
os.environ['PLUGIN_ROOT'] = str(root)
os.environ['PLUGIN_DATA'] = str(root.parents[3]/'data'/root.parent.parent.name/root.parent.name)
owner, _, _ = module.load_owner()
subject = owner.observe_recovery_subject_v1()
module.load_owner()
if path.read_bytes() != raw:
    raise RuntimeError('recovery input adapter changed during observation')
sys.stdout.buffer.write(json.dumps(subject,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('utf-8') + b'\\n')
"""
    try:
        completed = subprocess.run(
            [sys.executable, "-I", "-S", "-B", "-c", script,
             str(adapter), RECOVERY_INPUT_ADAPTER_DIGEST],
            cwd=repo, env=sanitized_action_environment(), capture_output=True,
            timeout=60, check=False,
        )
        raw = completed.stdout
        if completed.returncode != 0:
            fail("recovery owner observation is unavailable: CHILD_EXIT", decision="REQUIRED")
        if completed.stderr:
            fail("recovery owner observation is unavailable: CHILD_STDERR", decision="REQUIRED")
        if (len(raw) > 32768 or not raw.endswith(b"\n") or b"\n" in raw[:-1]
                or b"\r" in raw or b"\x00" in raw):
            fail("recovery owner observation is unavailable: OUTPUT_FRAME", decision="REQUIRED")
        decoded = raw.decode("utf-8", "strict")
        subject = json.loads(decoded, object_pairs_hook=unique_object)
    except subprocess.TimeoutExpired:
        fail("recovery owner observation is unavailable: CHILD_TIMEOUT", decision="REQUIRED")
    except OSError:
        fail("recovery owner observation is unavailable: CHILD_OS", decision="REQUIRED")
    except UnicodeError:
        fail("recovery owner observation is unavailable: OUTPUT_ENCODING", decision="REQUIRED")
    except (ValueError, RecursionError):
        fail("recovery owner observation is unavailable: OUTPUT_JSON", decision="REQUIRED")
    except subprocess.SubprocessError:
        fail("recovery owner observation is unavailable: CHILD_PROCESS", decision="REQUIRED")
    body = {
        "schema": RECOVERY_CUSTODY_SCHEMA, "subject": subject,
        "subject_digest": digest_json(subject),
        "input_adapter_digest": RECOVERY_INPUT_ADAPTER_DIGEST,
        "genuine_host_evidence": "UNVERIFIED", "continuity_current": False,
        "ordinary_effect_authority": "NONE", "route_open_authority": "NONE",
    }
    record = recovery_custody_record_v1({**body, "record_identity": digest_json(body)})
    if Path(record["subject"]["repository_identity"]).resolve() != repo.resolve():
        fail("recovery custody belongs to another repository", decision="REQUIRED")
    return record


def revalidate_recovery_custody_v1(repo: Path, expected: Any) -> dict[str, Any]:
    """Compare a retained record with a fresh physical-owner observation."""
    retained = recovery_custody_record_v1(expected)
    observed = observe_recovery_custody_v1(repo)
    if observed != retained:
        fail("recovery predecessor custody changed", decision="REQUIRED")
    return observed


def require_recovery_native_proof_v1(custody: Any) -> NoReturn:
    """No native invocation resolver is qualified; caller data cannot grant it."""
    recovery_custody_record_v1(custody)
    fail("NATIVE_RECOVERY_PROOF_UNQUALIFIED", decision="REQUIRED")


def command_observe_recovery_custody(args: argparse.Namespace) -> None:
    repo, _, _ = repo_context()
    emit(observe_recovery_custody_v1(repo))


def _retained_native_json_v1(raw: bytes, label: str) -> dict[str, Any]:
    """Decode one bounded native LF row, preserving its outer envelope."""
    if (not isinstance(raw, bytes) or not raw or len(raw) > MAX_RETAINED_NATIVE_ROW_BYTES
            or not raw.endswith(b"\n") or b"\n" in raw[:-1]
            or b"\r" in raw or b"\x00" in raw):
        fail(f"{label} bytes are malformed or oversized", decision="REQUIRED")
    def reject_constant(value: str) -> NoReturn:
        fail(f"{label} contains nonfinite JSON", decision="REQUIRED")
    try:
        value = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=unique_object,
                           parse_constant=reject_constant)
    except (UnicodeError, ValueError, RecursionError):
        fail(f"{label} is not bounded strict JSON", decision="REQUIRED")
    if not isinstance(value, dict):
        fail(f"{label} is not an object", decision="REQUIRED")
    return value


def _retained_recovery_input_v1(value: Any, session_id: str, turn_id: str) -> dict[str, Any]:
    """Validate input semantics as data; flags and matching digests prove no origin."""
    value = exact_keys(value, {
        "schema", "source_event", "source_event_digest", "subject", "subject_digest",
        "subject_cause_attested", "genuine_host_evidence", "continuity_current",
        "ordinary_effect_authority", "route_open_authority", "input_digest",
    }, "retained recovery input")
    try:
        json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8", "strict")
    except (UnicodeError, ValueError):
        fail("retained recovery input contains invalid Unicode or JSON", decision="REQUIRED")
    def producer_digest(item: Any) -> str:
        # Match the frozen adapter's canonicalization, not the route record's
        # general digest_json Unicode policy.
        return "sha256:" + hashlib.sha256(json.dumps(item, sort_keys=True,
            separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")).hexdigest()
    if (value["schema"] != "implementaudit.recovery-host-input.v1"
            or value["subject_cause_attested"] is not False
            or value["genuine_host_evidence"] != "UNVERIFIED"
            or value["continuity_current"] is not False
            or value["ordinary_effect_authority"] != "NONE"
            or value["route_open_authority"] != "NONE"):
        fail("retained recovery input schema or authority ceiling differs", decision="REQUIRED")
    source = exact_keys(value["source_event"], {
        "schema", "host_id", "kind", "host_session_id", "turn_id",
        "host_binding_generation", "host_binding_digest",
    }, "retained recovery source input")
    if (source["schema"] != "implementaudit.user-prompt-source-input.v1"
            or source["host_id"] != "codex" or source["kind"] != "UserPromptSubmit"
            or source["host_session_id"] != session_id or source["turn_id"] != turn_id):
        fail("retained recovery source session, turn or kind differs", decision="REQUIRED")
    custody_body = {
        "schema": RECOVERY_CUSTODY_SCHEMA, "subject": value["subject"],
        "subject_digest": digest_json(value["subject"]), "input_adapter_digest": RECOVERY_INPUT_ADAPTER_DIGEST,
        "genuine_host_evidence": "UNVERIFIED", "continuity_current": False,
        "ordinary_effect_authority": "NONE", "route_open_authority": "NONE",
    }
    # This calls only the data parser. Physical-owner revalidation is separate.
    custody = recovery_custody_record_v1({**custody_body, "record_identity": digest_json(custody_body)})
    if (source["host_binding_generation"] != custody["subject"]["host_binding_generation"]
            or source["host_binding_digest"] != custody["subject"]["host_binding_digest"]
            or value["source_event_digest"] != producer_digest(source)
            or value["subject_digest"] != producer_digest(value["subject"])
            or value["input_digest"] != producer_digest({key: item for key, item in value.items() if key != "input_digest"})):
        fail("retained recovery input H0 join or digest differs", decision="REQUIRED")
    return value


def parse_retained_recovery_row_v1(
    raw: bytes, *, expected_session_id: str, expected_turn_id: str, after_ordinal: int,
) -> dict[str, Any]:
    """Parse the qualified 0.153.4 row shape, without claiming producer provenance."""
    session_id = exact_text(expected_session_id, "compared native session")
    turn_id = exact_text(expected_turn_id, "compared native turn")
    if type(after_ordinal) is not int or after_ordinal < 0:
        fail("retained native frontier is malformed", decision="REQUIRED")
    row = exact_keys(_retained_native_json_v1(raw, "retained native row"),
                     {"timestamp", "ordinal", "type", "payload"}, "retained native hook envelope")
    # Any outer metadata, including false/null/unknown shapes, is ineligible.
    if (row["type"] != "response_item" or type(row["ordinal"]) is not int
            or row["ordinal"] <= after_ordinal):
        fail("retained native row is stale or foreign", decision="REQUIRED")
    timestamp = exact_text(row["timestamp"], "retained native timestamp")
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z", timestamp):
            raise ValueError("nonexact native timestamp")
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        fail("retained native timestamp is malformed", decision="REQUIRED")
    message = exact_keys(row["payload"], {
        "type", "id", "role", "content", "internal_chat_message_metadata_passthrough",
    }, "retained native developer message")
    if message["type"] != "message" or message["role"] != "developer":
        fail("retained native item is not an exact developer message", decision="REQUIRED")
    exact_text(message["id"], "retained native message identity")
    content = message["content"]
    if not isinstance(content, list) or len(content) != 1:
        fail("retained native message has ambiguous content", decision="REQUIRED")
    item = exact_keys(content[0], {"type", "text"}, "retained native content")
    if item["type"] != "input_text" or not isinstance(item["text"], str):
        fail("retained native content is not input_text", decision="REQUIRED")
    metadata = exact_keys(message["internal_chat_message_metadata_passthrough"],
        {"turn_id", "create_time", "content_item_kinds"}, "retained native hook metadata")
    if (metadata["turn_id"] != turn_id
            or metadata["content_item_kinds"] != ["hooks.additional_context"]
            or type(metadata["create_time"]) not in {int, float}):
        fail("retained native hook metadata is malformed or misaligned", decision="REQUIRED")
    try:
        if not math.isfinite(metadata["create_time"]) or metadata["create_time"] < 0:
            raise ValueError("invalid native creation time")
    except (ValueError, OverflowError):
        fail("retained native creation time is malformed", decision="REQUIRED")
    try:
        text_bytes = item["text"].encode("utf-8", "strict")
    except UnicodeError:
        fail("retained recovery input text is not UTF-8", decision="REQUIRED")
    value = _retained_native_json_v1(text_bytes + b"\n", "retained recovery input text")
    value = _retained_recovery_input_v1(value, session_id, turn_id)
    if json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) != item["text"]:
        fail("retained recovery input text is not exact producer JSON", decision="REQUIRED")
    return {
        "schema": RETAINED_RECOVERY_INPUT_SCHEMA, "ordinal": row["ordinal"],
        "row_digest": "sha256:" + hashlib.sha256(raw).hexdigest(), "input": value,
        "native_attribution": "UNQUALIFIED", "genuine_host_evidence": "UNVERIFIED",
        "continuity_current": False, "ordinary_effect_authority": "NONE", "route_open_authority": "NONE",
    }


def select_retained_recovery_input_v1(
    raw: bytes, *, expected_thread_id: str, expected_session_id: str,
    expected_turn_id: str, after_ordinal: int,
) -> dict[str, Any]:
    """Parse retained session-meta plus a bounded row slice, never a caller path.

    These supplied bytes need not contain the conversation prefix. A future
    qualified native reader must independently stream-verify its saved prefix
    and obtain the bounded current-turn suffix before invoking this parser.
    """
    for value in (expected_thread_id, expected_session_id, expected_turn_id):
        exact_text(value, "compared native identity")
    if (type(after_ordinal) is not int or after_ordinal < 0 or not isinstance(raw, bytes)
            or not raw or len(raw) > MAX_RETAINED_NATIVE_SLICE_BYTES):
        fail("retained native slice or frontier is malformed or oversized", decision="REQUIRED")
    lines = raw.splitlines(keepends=True)
    if len(lines) > 4096:
        fail("retained native slice exceeds its row bound", decision="REQUIRED")
    first = exact_keys(_retained_native_json_v1(lines[0], "native session metadata"),
        {"timestamp", "ordinal", "type", "payload"}, "native session envelope")
    session = first["payload"]
    if (first["type"] != "session_meta" or type(first["ordinal"]) is not int or first["ordinal"] != 0
            or not isinstance(session, dict) or session.get("id") != expected_thread_id
            or session.get("session_id") != expected_session_id or session.get("cli_version") != RETAINED_NATIVE_VERSION):
        fail("native session metadata disagrees with the compared task/session/version", decision="REQUIRED")
    candidates = []
    rejected_client_rows = 0
    previous_ordinal = -1
    for line in lines:
        row = _retained_native_json_v1(line, "native retained row")
        if (set(row) not in ({"timestamp", "ordinal", "type", "payload"},
                            {"timestamp", "ordinal", "type", "payload", "metadata"})
                or type(row["ordinal"]) is not int or row["ordinal"] <= previous_ordinal):
            fail("native retained row envelope or ordinal order differs", decision="REQUIRED")
        previous_ordinal = row["ordinal"]
        message = row["payload"]
        if (row["ordinal"] <= after_ordinal or row["type"] != "response_item"
                or not isinstance(message, dict) or message.get("role") != "developer"):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        recovery_text = False
        for item in content:
            if not isinstance(item, dict) or not isinstance(item.get("text"), str):
                continue
            text = item["text"]
            if "implementaudit.recovery-host-input.v1" in text:
                recovery_text = True
                break
            try:
                decoded = json.loads(text, object_pairs_hook=unique_object)
            except json.JSONDecodeError:
                continue
            except (ValueError, RecursionError):
                fail("native developer JSON is ambiguous or exceeds parser limits", decision="REQUIRED")
            if isinstance(decoded, dict) and decoded.get("schema") == "implementaudit.recovery-host-input.v1":
                recovery_text = True
                break
        if not recovery_text:
            continue
        envelope = row.get("metadata")
        if (isinstance(envelope, dict) and set(envelope) == {"client_authored"}
                and envelope["client_authored"] is True):
            rejected_client_rows += 1
            continue
        candidates.append(parse_retained_recovery_row_v1(line, expected_session_id=expected_session_id,
            expected_turn_id=expected_turn_id, after_ordinal=after_ordinal))
    if len(candidates) != 1:
        fail("retained recovery input is absent or ambiguous", decision="REQUIRED")
    return {**candidates[0], "rejected_client_rows": rejected_client_rows,
            "retained_slice_digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
            "session_meta_digest": "sha256:" + hashlib.sha256(lines[0]).hexdigest(),
            "compared_after_ordinal": after_ordinal}


def reconcile_retained_recovery_input_v1(
    repo: Path, raw: bytes, *, expected_thread_id: str, expected_session_id: str,
    expected_turn_id: str, after_ordinal: int,
) -> dict[str, Any]:
    """Join candidate bytes to current physical custody; native provenance stays closed."""
    custody = observe_recovery_custody_v1(repo)
    candidate = select_retained_recovery_input_v1(raw, expected_thread_id=expected_thread_id,
        expected_session_id=expected_session_id, expected_turn_id=expected_turn_id, after_ordinal=after_ordinal)
    if candidate["input"]["subject"] != custody["subject"]:
        fail("retained recovery input differs from the current physical subject", decision="REQUIRED")
    revalidate_recovery_custody_v1(repo, custody)
    return {**candidate, "custody_revalidated": True, "custody_record_identity": custody["record_identity"]}


RECOVERY_NATIVE_READER_DIGEST = 'sha256:2ddbeb9efc6f957b3cad0aca34723e74703b427485af112facc616b30f8f5cff'


def recovery_native_observer_module_v1() -> Any:
    """Load only the exact adjacent observer, preserving its source identity."""
    import types
    path = Path(__file__).with_name("codex-recovery-native-reader.py").resolve()
    raw = path.read_bytes()
    if "sha256:" + hashlib.sha256(raw).hexdigest() != RECOVERY_NATIVE_READER_DIGEST:
        fail("native observer source differs", decision="REQUIRED")
    name = "_route_native_observer_" + hashlib.sha256(str(path).encode()).hexdigest()
    if name not in sys.modules:
        module = types.ModuleType(name)
        module.__file__ = str(path)
        sys.modules[name] = module
        exec(compile(raw, str(path), "exec"), module.__dict__)
    return sys.modules[name]


def create_recovery_native_observer_v1(**parameters: Any) -> Any:
    return recovery_native_observer_module_v1().NativeRecoveryObserver(**parameters)


def native_session_custody_v1(repo: Path, session: str) -> dict[str, Any]:
    """Resolve actual native session through the existing physical H0 owner."""
    adapter = Path(__file__).with_name("codex-recovery-prompt-input.py").resolve()
    script = """import hashlib,json,os,pathlib,sys,types
path=pathlib.Path(sys.argv[1]);raw=path.read_bytes()
if 'sha256:'+hashlib.sha256(raw).hexdigest()!=sys.argv[2]:raise RuntimeError('adapter changed')
module=types.ModuleType('_native_session_owner');module.__file__=str(path)
exec(compile(raw,str(path),'exec'),module.__dict__)
os.environ['CODEX_SESSION_ID']=sys.argv[3]
root=path.parents[3]
os.environ['PLUGIN_ROOT']=str(root)
os.environ['PLUGIN_DATA']=str(root.parents[3]/'data'/root.parent.parent.name/root.parent.name)
owner,scripts,store=module.load_owner()
binding=module.lookup_binding(owner,scripts,store,sys.argv[3])
subject=owner.observe_recovery_subject_v1()
if module.lookup_binding(owner,scripts,store,sys.argv[3])!=binding:raise RuntimeError('H0 changed')
module.load_owner()
if path.read_bytes()!=raw:raise RuntimeError('adapter changed')
sys.stdout.buffer.write(json.dumps({'binding':binding,'binding_digest':module.digest(binding),'subject':subject},sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()+b'\\n')
"""
    completed = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", script,
        str(adapter), RECOVERY_INPUT_ADAPTER_DIGEST, exact_text(session, "native session")],
        cwd=repo, env=sanitized_action_environment(), capture_output=True, timeout=60, check=False)
    if completed.returncode or completed.stderr or len(completed.stdout) > 65536:
        fail("native-session physical H0 observation failed", decision="REQUIRED")
    value = _retained_native_json_v1(completed.stdout, "native-session custody")
    body = {"schema": RECOVERY_CUSTODY_SCHEMA, "subject": value["subject"],
        "subject_digest": digest_json(value["subject"]), "input_adapter_digest": RECOVERY_INPUT_ADAPTER_DIGEST,
        "genuine_host_evidence": "UNVERIFIED", "continuity_current": False,
        "ordinary_effect_authority": "NONE", "route_open_authority": "NONE"}
    custody = recovery_custody_record_v1({**body, "record_identity": digest_json(body)})
    binding = value["binding"]
    if (binding["host_session_id"] != session
            or binding["binding_generation"] != custody["subject"]["host_binding_generation"]
            or value["binding_digest"] != custody["subject"]["host_binding_digest"]
            or Path(custody["subject"]["repository_identity"]).resolve() != repo.resolve()):
        fail("native session does not own this physical recovery subject", decision="REQUIRED")
    return custody


def read_retained_recovery_input_v1(repo: Path, *, observer: Any = None) -> dict[str, Any]:
    """Reread actual native evidence and physical custody; grant no route authority."""
    if observer is None:
        require_recovery_native_proof_v1(observe_recovery_custody_v1(repo))
    module = recovery_native_observer_module_v1()
    if type(observer) is not module.NativeRecoveryObserver:
        fail("native observer must be the exact source-owned implementation", decision="REQUIRED")
    if (observer.repo != repo.resolve() or observer.plugin_root != Path(__file__).resolve().parents[3]):
        fail("native observer source/repository locator is foreign", decision="REQUIRED")
    try:
        observed = observer.read_input()
        custody = native_session_custody_v1(repo, observed["native_session_id"])
        candidate = select_retained_recovery_input_v1(observed["raw"],
            expected_thread_id=observed["native_thread_id"], expected_session_id=observed["native_session_id"],
            expected_turn_id=observed["native_turn_id"], after_ordinal=observed["after_ordinal"])
        if candidate["input"]["subject"] != custody["subject"]:
            fail("native input no longer matches physical custody", decision="REQUIRED")
        repeated = observer.read_input()
        again = select_retained_recovery_input_v1(repeated["raw"],
            expected_thread_id=repeated["native_thread_id"], expected_session_id=repeated["native_session_id"],
            expected_turn_id=repeated["native_turn_id"], after_ordinal=repeated["after_ordinal"])
        if (candidate["row_digest"] != again["row_digest"] or observed["epoch_identity"] != repeated["epoch_identity"]
                or observed.get("observation_successor_identity") != repeated.get("observation_successor_identity")
                or observed.get("observation_successor_spec_sha256") != repeated.get("observation_successor_spec_sha256")
                or native_session_custody_v1(repo, observed["native_session_id"]) != custody):
            fail("native recovery input or physical custody changed during readback", decision="REQUIRED")
    except (module.Refusal, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        fail("actual native recovery observation is unavailable", decision="REQUIRED")
    body = {"schema": "implementaudit.native-recovery-input-observation.v1", "input": candidate["input"],
        "native_thread_id": observed["native_thread_id"], "native_session_id": observed["native_session_id"],
        "native_turn_id": observed["native_turn_id"], "row_ordinal": candidate["ordinal"],
        "row_digest": candidate["row_digest"], "epoch_identity": observed["epoch_identity"],
        "custody_record_identity": custody["record_identity"],
        "native_attribution": "QUALIFIED_BOUNDED_READBACK", "continuity_current": False,
        "ordinary_effect_authority": "NONE", "route_open_authority": "NONE"}
    return {**body, "observation_identity": digest_json(body)}



# Explicit stale-context cognition variant. Historical cause remains unverified;
# native occurrence is supplied only by the separately qualified owner reader.
RECOVERY_RECORD_SCHEMA = "implementaudit.route-recovery-decision.v1"
RECOVERY_V3_SCHEMA = "implementaudit.post-compaction-recovery.v3"
RECOVERY_SCOPE_KIND = "MINIMUM_APPLICABLE_FRONTIER"
RECOVERY_RECORD_KEYS = {
    "schema", "predicate_version", "controller_id", "claim_id", "explicit_run_root",
    "host_id", "host_session_id", "host_binding_generation", "host_correlation_id",
    "recovery_capsule", "scope", "action", "package", "child_source", "decision",
    "classification", "predecessor_record_oid", "route_transaction_id", "obligation_id",
    "route_state", "child_lifecycle_owned", "continuity_current", "ordinary_effect_authority",
    "record_identity",
}


def recovery_observer_args_v1(parser: argparse.ArgumentParser) -> None:
    for name in ("binary", "home", "controller-cwd", "plugin-id", "task", "epoch-directory"):
        parser.add_argument("--native-" + name)
    parser.add_argument("--native-observation-successor-spec")
    parser.add_argument("--native-observation-successor-sha256")


def recovery_observer_from_args_v1(repo: Path, args: argparse.Namespace) -> Any:
    observer = getattr(args, "native_recovery_observer", None)
    if observer is not None:
        return observer
    names = ("binary", "home", "controller_cwd", "plugin_id", "task", "epoch_directory")
    parameters = {name: getattr(args, "native_" + name, None) for name in names}
    if any(value is None for value in parameters.values()):
        fail("NATIVE_RECOVERY_PROOF_UNQUALIFIED: exact native owner locators are required", decision="REQUIRED")
    parameters.update(repo=repo, plugin_root=Path(__file__).resolve().parents[3])
    for name in ("observation_successor_spec", "observation_successor_sha256"):
        parameters[name] = getattr(args, "native_" + name, None)
    try:
        return create_recovery_native_observer_v1(**parameters)
    except (OSError, ValueError, TypeError, recovery_native_observer_module_v1().Refusal):
        fail("native recovery observer preparation is unavailable", decision="REQUIRED")


def command_prepare_recovery_capsule_v3(args: argparse.Namespace) -> None:
    repo, _, _ = repo_context()
    emit(prepare_recovery_capsule_v3(repo, observer=recovery_observer_from_args_v1(repo, args)))


def recovery_request_v3(capsule: dict[str, Any]) -> dict[str, Any]:
    argv = ["route-trigger", "STALE_CONTEXT_RECONSTRUCTION"]
    return {"schema": REQUEST_SCHEMA, "predicate_version": PREDICATE_VERSION,
            "boundary": {"kind": "recovery-request", "event_id": capsule["event_id"],
                         "digest": capsule["event_digest"]},
            "scope": {"identity": RECOVERY_SCOPE_KIND, "digest": capsule["scope_digest"]},
            "action": {"identity": "recovery-cognition", "digest": digest_json(argv),
                       "class": "REQUIRED_INTERNAL_CHILD", "argv": argv},
            "inputs": [{"identity": "recovery-subject", "path": "recovery-capsule.json",
                        "digest": capsule["custody"]["subject_digest"]}]}


def recovery_capsule_v3_record(value: Any) -> dict[str, Any]:
    value = exact_keys(value, {"schema", "custody", "native_observation", "native_invocation_digest",
        "event_id", "event_digest", "scope_digest", "selected_child", "return_contract",
        "package", "child_source", "continuity_current", "ordinary_effect_authority",
        "subject_cause_attested", "capsule_digest"} | ({"attempt_boundary"} if isinstance(value, dict) and value.get("schema") == RECOVERY_ATTEMPT_CAPSULE_SCHEMA else set()), "recovery custody capsule")
    custody = recovery_custody_record_v1(value["custody"])
    native = exact_keys(value["native_observation"], {"schema", "input", "native_thread_id", "native_session_id",
        "native_turn_id", "row_ordinal", "row_digest", "epoch_identity", "custody_record_identity",
        "observation_identity", "native_attribution", "continuity_current", "ordinary_effect_authority",
        "route_open_authority"}, "recovery native observation")
    if (not isinstance(native["input"], dict) or native["input"].get("subject") != custody["subject"]
            or native["schema"] != "implementaudit.native-recovery-input-observation.v1"
            or native["native_attribution"] != "QUALIFIED_BOUNDED_READBACK"
            or native["custody_record_identity"] != custody["record_identity"]
            or native["continuity_current"] is not False or native["ordinary_effect_authority"] != "NONE"
            or native["route_open_authority"] != "NONE" or type(native["row_ordinal"]) is not int
            or native["row_ordinal"] < 1):
        fail("recovery capsule native input names a foreign subject", decision="REQUIRED")
    for key in ("row_digest", "epoch_identity", "observation_identity"):
        if not isinstance(native[key], str) or not HEX_RE.fullmatch(native[key]):
            fail("recovery native observation digest is malformed", decision="REQUIRED")
    _retained_recovery_input_v1(native["input"], native["native_session_id"], native["native_turn_id"])
    if native["observation_identity"] != digest_json({k: v for k, v in native.items() if k != "observation_identity"}):
        fail("recovery native observation identity differs", decision="REQUIRED")
    invocation = digest_json({key: native.get(key) for key in
        ("native_thread_id", "native_session_id", "native_turn_id")})
    if (value["schema"] not in {RECOVERY_V3_SCHEMA, RECOVERY_ATTEMPT_CAPSULE_SCHEMA} or value["selected_child"] != "audit-state"
            or value["return_contract"] != (AUDIT_STATE_FRONTIER_RETURN_V2_SCHEMA if value["schema"] == RECOVERY_ATTEMPT_CAPSULE_SCHEMA else AUDIT_STATE_FRONTIER_RETURN_SCHEMA)
            or value["continuity_current"] is not False or value["ordinary_effect_authority"] != "NONE"
            or value["subject_cause_attested"] is not False
            or value["native_invocation_digest"] != invocation
            or value["event_id"] != "recovery-native-v1-" + invocation.removeprefix("sha256:")
            or value["event_digest"] != native.get("input", {}).get("source_event_digest")
            or value["scope_digest"] != digest_json({"kind": RECOVERY_SCOPE_KIND,
                                                    "subject_digest": custody["subject_digest"]})
            or value["capsule_digest"] != digest_json({k: v for k, v in value.items() if k != "capsule_digest"})):
        fail("recovery v3 capsule identity or authority ceiling differs", decision="REQUIRED")
    for key in ("native_thread_id", "native_session_id", "native_turn_id"):
        exact_text(native.get(key), "native recovery " + key)
    if value["schema"] == RECOVERY_ATTEMPT_CAPSULE_SCHEMA and value["attempt_boundary"] != recovery_attempt_boundary_v1(value):
        fail("recovery attempt boundary differs from native occurrence", decision="REQUIRED")
    return value


def read_recovery_capsule_v3(path: str) -> tuple[bytes, dict[str, Any]]:
    try:
        raw, value = read_exact_artifact(path, "recovery capsule")
        return raw, recovery_capsule_v3_record(value)
    except (RecursionError, UnicodeError):
        fail("recovery capsule exceeds bounded JSON encoding limits", decision="REQUIRED")


def prepare_recovery_capsule_v3(repo: Path, *, observer: Any) -> dict[str, Any]:
    """Read-only preparation. Never accept a serialized proof as native occurrence."""
    native = read_retained_recovery_input_v1(repo, observer=observer)
    custody = observe_recovery_custody_v1(repo)
    invocation = digest_json({key: native[key] for key in
        ("native_thread_id", "native_session_id", "native_turn_id")})
    capsule = {"schema": RECOVERY_ATTEMPT_CAPSULE_SCHEMA, "custody": custody, "native_observation": native,
        "native_invocation_digest": invocation,
        "event_id": "recovery-native-v1-" + invocation.removeprefix("sha256:"),
        "event_digest": native["input"]["source_event_digest"],
        "scope_digest": digest_json({"kind": RECOVERY_SCOPE_KIND, "subject_digest": custody["subject_digest"]}),
        "selected_child": "audit-state", "return_contract": AUDIT_STATE_FRONTIER_RETURN_V2_SCHEMA,
        "continuity_current": False, "ordinary_effect_authority": "NONE", "subject_cause_attested": False}
    capsule["attempt_boundary"] = recovery_attempt_boundary_v1(capsule)
    capsule["package"], capsule["child_source"] = executing_package_evidence(repo, recovery_request_v3(capsule), "REQUIRED")
    capsule["capsule_digest"] = digest_json(capsule)
    revalidate_recovery_custody_v1(repo, custody)
    if read_retained_recovery_input_v1(repo, observer=observer) != native:
        fail("native recovery observation changed during capsule preparation", decision="REQUIRED")
    return recovery_capsule_v3_record(capsule)


def recovery_binding_v3(repo: Path, common: str, args: argparse.Namespace,
                        capsule: dict[str, Any], obligation: str, transaction: str) -> dict[str, Any]:
    """Attribute the new event against exact physical H0 predecessor custody.

    This H0 correlation never authenticates native occurrence and never denotes
    a current continuity receipt. The qualified native reader is mandatory too.
    """
    subject = capsule["custody"]["subject"]
    native = capsule["native_observation"]
    root = Path(__file__).resolve().parents[3]
    # Physical layout is .../plugins/cache/marketplace/plugin/version.
    expected_store = root.parents[3] / "data" / root.parent.parent.name / root.parent.name / "host-session-binding-v1"
    if (Path(args.store).resolve() != expected_store.resolve()
            or str(repo) != subject["repository_identity"] or args.controller != subject["controller_id"]
            or args.host_id != "codex" or args.host_session_id != native["native_session_id"]
            or args.binding_generation != subject["host_binding_generation"]):
        fail("recovery route H0/controller identity differs", decision="REQUIRED")
    fields = {"host-id": args.host_id, "host-session-id": args.host_session_id,
        "binding-generation": args.binding_generation, "controller-id": args.controller,
        "claim-id": subject["claim_id"], "explicit-run-root": subject["explicit_run_root"],
        "repository-identity": str(repo), "git-common-directory-identity": common,
        "worktree-identity": str(repo), "continuity-generation": subject["predecessor_epoch"],
        "continuity-receipt": subject["predecessor_receipt"], "event-id": capsule["event_id"],
        "obligation-id": obligation, "route-transaction-id": transaction}
    command = [sys.executable, str(Path(__file__).with_name("host-session-binding.py")),
               "--store", args.store, "validate-event"]
    for key, item in fields.items():
        command.extend(["--" + key, item])
    result = subprocess.run(command, cwd=repo, env=sanitized_action_environment(),
                            capture_output=True, check=False)
    if result.returncode:
        fail("recovery predecessor H0 attribution failed", decision="REQUIRED")
    attributed = decoded_artifact(result.stdout, "recovery predecessor H0 attribution")
    if attributed.get("status") != "ATTRIBUTED":
        fail("recovery predecessor H0 attribution is unavailable", decision="REQUIRED")
    return attributed


def recovery_record_header_v1(record: dict[str, Any], controller: str) -> None:
    keys = RECOVERY_RECORD_KEYS | ({"lifecycle"} if "lifecycle" in record else set())
    exact_keys(record, keys, "recovery route record")
    capsule = recovery_capsule_v3_record(record["recovery_capsule"])
    subject = capsule["custody"]["subject"]
    transaction = digest_json({"schema": RECOVERY_RECORD_SCHEMA, "capsule_digest": capsule["capsule_digest"]})
    if (record["schema"] != RECOVERY_RECORD_SCHEMA or record["controller_id"] != controller
            or controller != subject["controller_id"] or record["claim_id"] != subject["claim_id"]
            or record["explicit_run_root"] != subject["explicit_run_root"]
            or record["scope"] != recovery_request_v3(capsule)["scope"]
            or record["action"] != recovery_request_v3(capsule)["action"]
            or record["package"] != capsule["package"] or record["child_source"] != capsule["child_source"]
            or record["host_id"] != "codex"
            or record["host_session_id"] != capsule["native_observation"]["native_session_id"]
            or record["host_binding_generation"] != subject["host_binding_generation"]
            or record["predicate_version"] != ("R0033.recovery-cognition.v2" if capsule["schema"] == RECOVERY_ATTEMPT_CAPSULE_SCHEMA else "R0033.recovery-cognition.v1")
            or record["route_transaction_id"] != transaction
            or record["obligation_id"] != digest_json({"recovery_transaction": transaction, "child": "audit-state"})
            or record["decision"] != "REQUIRED" or record["classification"] != "MECHANICALLY_REQUIRED"
            or record["continuity_current"] is not False or record["ordinary_effect_authority"] != "NONE"
            or record["child_lifecycle_owned"] is not ("lifecycle" in record)
            or record["route_state"] not in ({"OPEN", "RETURNED", "SATISFIED"} if "lifecycle" in record else {"UNSATISFIED"})
            or record["record_identity"] != digest_json({k: v for k, v in record.items() if k != "record_identity"})):
        fail("recovery route identity or authority ceiling differs", decision="REQUIRED")
    if not isinstance(record["host_correlation_id"], str) or not HEX_RE.fullmatch(record["host_correlation_id"]):
        fail("recovery H0 correlation is malformed", decision="REQUIRED")
    if "lifecycle" not in record and record["predecessor_record_oid"] is not None:
        fail("recovery REQUIRED has a foreign predecessor", decision="REQUIRED")


def recovery_capsule_use_v3(capsule: dict[str, Any], transaction: str) -> bytes:
    return (json.dumps({"schema": "implementaudit.recovery-capsule-use.v3",
        "native_invocation_digest": capsule["native_invocation_digest"],
        "subject_digest": capsule["custody"]["subject_digest"], "capsule_digest": capsule["capsule_digest"],
        "route_transaction_id": transaction}, sort_keys=True, separators=(",", ":")) + "\n").encode()


def recovery_reconciliation_proposal_v1(value: Any, capsule: dict[str, Any]) -> dict[str, Any]:
    """Validate the child's bounded proposal; only the later state owner applies it."""
    proposal = exact_keys(value, {"schema", "predecessor_state_digest", "next_action_policy", "next_action"},
                          "recovery canonical reconciliation")
    action = proposal["next_action"]
    if (proposal["schema"] != "implementaudit.recovery-reconciliation-proposal.v1"
            or proposal["predecessor_state_digest"] != "sha256:" + capsule["custody"]["subject"]["hot_input_digests"]["STATE"]
            or proposal["next_action_policy"] not in {"RETAIN_PREDECESSOR", "REPLACE_NEXT_ACTION"}
            or not isinstance(action, str) or not 0 < len(action) <= 4096
            or action != action.strip() or any(ord(char) < 32 or ord(char) == 127 for char in action)):
        fail("recovery canonical reconciliation proposal is absent or foreign", decision="REQUIRED")
    return proposal


def validate_recovery_packet_v3(packet: dict[str, Any], capsule: dict[str, Any], correlation: str) -> None:
    source = packet["source_event"]
    if (source["source_identity"] != capsule["event_id"] or source["kind"] != "one-shot-action"
            or source["body"] != RECOVERY_SCOPE_KIND + ":" + capsule["custody"]["subject_digest"]
            or any(source["reactivation"].values())
            or source["provenance"]["host_correlation_id"] != correlation):
        fail("recovery packet source or scope is foreign", decision="REQUIRED")


def read_terminal_recovery_v1(repo: Path, args: argparse.Namespace, *, observer: Any) -> dict[str, Any]:
    """Fresh terminal evidence for the separate R0039 reconciliation owner.

    This read-only seam neither reconciles hot state nor publishes a receipt.
    The consumer must hold/recheck its own lock and exact pre/post fences.
    """
    if observer is None or not args.route_transaction_id:
        fail("terminal recovery requires exact native observer and transaction", decision="REQUIRED")
    common = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    oid, record = current_ref(repo, args.controller, route_transaction_id=args.route_transaction_id)
    if (oid != args.expected_record or record is None or record.get("schema") != RECOVERY_RECORD_SCHEMA
            or record["route_state"] != "SATISFIED"):
        fail("terminal recovery evidence is absent, stale, or incomplete", decision="REQUIRED")
    capsule = prepare_recovery_capsule_v3(repo, observer=observer)
    if capsule != record["recovery_capsule"]:
        fail("terminal recovery lost exact native/custody/package evidence", decision="REQUIRED")
    attributed = recovery_binding_v3(repo, common, args, capsule, record["obligation_id"], args.route_transaction_id)
    if attributed["correlation_id"] != record["host_correlation_id"]:
        fail("terminal recovery H0 attribution changed", decision="REQUIRED")
    lifecycle = record["lifecycle"]
    if capsule["schema"] == RECOVERY_ATTEMPT_CAPSULE_SCHEMA:
        observe_recovery_attempt_v1(repo, observer, capsule, lifecycle["attempt_evidence"])
    returned = decoded_artifact(validate_bytes_identity(lifecycle["child_return"], "terminal recovery return"), "terminal recovery return")
    resolved = resolve_execution_evidence(Path(args.store), returned["payload"]["holon_execution_evidence"],
        args.host_id, args.host_session_id, args.binding_generation, "audit-state", args.route_transaction_id,
        record["obligation_id"], lifecycle["delivery"]["packet"]["digest"])
    use_path = Path(common) / "implementaudit-recovery-capsules" / args.controller / (
        "native-v3-" + capsule["native_invocation_digest"].removeprefix("sha256:") + ".used")
    if (resolved != lifecycle["execution_evidence"] or not use_path.is_file()
            or use_path.read_bytes() != recovery_capsule_use_v3(capsule, args.route_transaction_id)):
        fail("terminal recovery execution or one-use custody changed", decision="REQUIRED")
    if (prepare_recovery_capsule_v3(repo, observer=observer) != capsule
            or current_ref(repo, args.controller, route_transaction_id=args.route_transaction_id) != (oid, record)):
        fail("terminal recovery readback changed", decision="REQUIRED")
    proposal = recovery_reconciliation_proposal_v1(returned["payload"]["canonical_reconciliation"], capsule)
    return {"schema": "implementaudit.terminal-recovery-observation.v1", "record_oid": oid,
            "record": record, "canonical_reconciliation": proposal,
            "continuity_current": False, "ordinary_effect_authority": "NONE"}


def command_recovery_transaction_v1(args: argparse.Namespace, phase: str) -> None:
    """Existing transaction lifecycle, explicitly limited to recovery cognition."""
    repo, _, common = repo_context()
    observer = recovery_observer_from_args_v1(repo, args)
    if phase not in {"decide-transaction", "open", "return", "complete"}:
        fail("unsupported recovery lifecycle phase", decision="REQUIRED")
    capsule_raw, capsule = read_recovery_capsule_v3(args.recovery_capsule)
    request = read_request(args.request)
    if request != recovery_request_v3(capsule):
        fail("recovery request expands its capsule minimum-frontier scope", decision="REQUIRED")
    transaction = digest_json({"schema": RECOVERY_RECORD_SCHEMA, "capsule_digest": capsule["capsule_digest"]})
    obligation = digest_json({"recovery_transaction": transaction, "child": "audit-state"})
    if phase != "decide-transaction" and args.route_transaction_id != transaction:
        fail("recovery transaction custody is foreign", decision="REQUIRED")
    attempt_evidence = None
    with namespace_gate(common):
        def recheck() -> dict[str, Any]:
            if attempt_evidence is not None:
                observe_recovery_attempt_v1(repo, observer, capsule, attempt_evidence)
            if prepare_recovery_capsule_v3(repo, observer=observer) != capsule:
                fail("recovery native/custody/package observation changed", decision="REQUIRED")
            if read_recovery_capsule_v3(args.recovery_capsule)[0] != capsule_raw or read_request(args.request) != request:
                fail("recovery capsule/request bytes changed", decision="REQUIRED")
            return recovery_binding_v3(repo, common, args, capsule, obligation, transaction)

        attributed = recheck()
        old_oid, old = current_ref(repo, args.controller, route_transaction_id=transaction)
        expected = ZERO_OID if args.expected_record == "none" else args.expected_record
        if (old_oid or ZERO_OID) != expected:
            fail("recovery lifecycle CAS expected record is stale", decision="REQUIRED")
        if old is not None and (old.get("schema") != RECOVERY_RECORD_SCHEMA
                or old["recovery_capsule"] != capsule or old["host_correlation_id"] != attributed["correlation_id"]):
            fail("recovery transaction has foreign authority", decision="REQUIRED")
        use_path = Path(common) / "implementaudit-recovery-capsules" / args.controller / (
            "native-v3-" + capsule["native_invocation_digest"].removeprefix("sha256:") + ".used")
        use_bytes = recovery_capsule_use_v3(capsule, transaction)
        if phase == "decide-transaction":
            if old is not None:
                fail("recovery decision already exists; continue its exact lifecycle", decision="REQUIRED")
            subject = capsule["custody"]["subject"]
            base = {"schema": RECOVERY_RECORD_SCHEMA, "predicate_version": ("R0033.recovery-cognition.v2" if capsule["schema"] == RECOVERY_ATTEMPT_CAPSULE_SCHEMA else "R0033.recovery-cognition.v1"),
                "controller_id": args.controller, "claim_id": subject["claim_id"],
                "explicit_run_root": subject["explicit_run_root"], "host_id": args.host_id,
                "host_session_id": args.host_session_id, "host_binding_generation": args.binding_generation,
                "host_correlation_id": attributed["correlation_id"], "recovery_capsule": capsule,
                "scope": request["scope"], "action": request["action"], "package": capsule["package"],
                "child_source": capsule["child_source"], "decision": "REQUIRED", "classification": "MECHANICALLY_REQUIRED",
                "predecessor_record_oid": None, "route_transaction_id": transaction, "obligation_id": obligation,
                "route_state": "UNSATISFIED", "child_lifecycle_owned": False,
                "continuity_current": False, "ordinary_effect_authority": "NONE"}
        else:
            if old is None:
                fail("recovery lifecycle has no REQUIRED record", decision="REQUIRED")
            base = {k: v for k, v in old.items() if k != "record_identity"}
            base["predecessor_record_oid"] = old_oid
            lifecycle = old.get("lifecycle")
            if phase == "open":
                if old["route_state"] != "UNSATISFIED" or lifecycle is not None:
                    fail("recovery child may OPEN exactly once", decision="REQUIRED")
                require_governor_dispatch_requester(args.requester_identity)
                logical_task = logical_task_name(getattr(args, "logical_task", None), "audit-state",
                                                 transaction, old["host_session_id"])
                packet_raw, packet = read_route_packet(args.packet, obligation, transaction, expected_target="audit-state")
                validate_recovery_packet_v3(packet, capsule, attributed["correlation_id"])
                child_raw, child_path = child_delivery_bytes("audit-state", expected_identity_inputs=old["package"]["source_digests"])
                lifecycle = {"state": "OPEN", "logical_task": logical_task, "required_record_oid": old_oid,
                    "delivery": {"child": {"identity": str(child_path), **bytes_identity(child_raw)}, "packet": bytes_identity(packet_raw)},
                    "child_return": None, "governor_decision": None, "governor_decision_count": 0,
                    "source_event_status": "active", "execution_evidence": None}
                if capsule["schema"] == RECOVERY_ATTEMPT_CAPSULE_SCHEMA:
                    attempt_evidence = observe_recovery_attempt_v1(repo, observer, capsule)
                    lifecycle["attempt_evidence"] = attempt_evidence
                base.update(route_state="OPEN", child_lifecycle_owned=True, lifecycle=lifecycle)
            else:
                if capsule["schema"] == RECOVERY_ATTEMPT_CAPSULE_SCHEMA:
                    attempt_evidence = lifecycle.get("attempt_evidence") if isinstance(lifecycle, dict) else None
                    if attempt_evidence is None:
                        fail("recovery v4 OPEN lacks its native attempt evidence", decision="REQUIRED")
                    observe_recovery_attempt_v1(repo, observer, capsule, attempt_evidence)
                if not isinstance(lifecycle, dict) or lifecycle["state"] not in ({"OPEN"} if phase == "return" else {"RETURNED", "SATISFIED"}):
                    fail("recovery lifecycle phase skips its required predecessor", decision="REQUIRED")
                if not use_path.is_file() or use_path.read_bytes() != use_bytes:
                    fail("recovery invocation one-use custody differs", decision="REQUIRED")
                return_raw, returned = read_child_return(args.return_path, obligation, transaction,
                    lifecycle["delivery"]["packet"]["digest"], expected_child="audit-state", expected_capsule=capsule)
                if capsule["schema"] == RECOVERY_ATTEMPT_CAPSULE_SCHEMA:
                    recovery_attempt_admission_record_v1(returned["payload"].get("attempt_admission"),
                        attempt_evidence["evidence_digest"])
                resolved = resolve_execution_evidence(Path(args.store), returned["payload"]["holon_execution_evidence"],
                    args.host_id, args.host_session_id, args.binding_generation, "audit-state", transaction, obligation,
                    lifecycle["delivery"]["packet"]["digest"])
                if phase == "return":
                    lifecycle = {**lifecycle, "state": "RETURNED", "child_return": bytes_identity(return_raw), "execution_evidence": resolved}
                else:
                    packet_raw, _ = read_route_packet(args.packet, obligation, transaction, expected_target="audit-state")
                    decision_raw, _ = read_governor_decision(args.decision, obligation, transaction, bytes_identity(return_raw)["digest"])
                    if (bytes_identity(packet_raw) != lifecycle["delivery"]["packet"]
                            or bytes_identity(return_raw) != lifecycle["child_return"] or resolved != lifecycle["execution_evidence"]):
                        fail("recovery reconciliation differs from accepted delivery/return/receipts", decision="REQUIRED")
                    if lifecycle["state"] == "SATISFIED" and bytes_identity(decision_raw) != lifecycle["governor_decision"]:
                        fail("recovery reconciliation may not replace its one decision", decision="REQUIRED")
                    lifecycle = {**lifecycle, "state": "SATISFIED", "governor_decision": bytes_identity(decision_raw),
                                 "governor_decision_count": 1, "source_event_status": "satisfied"}
                base.update(route_state=lifecycle["state"], lifecycle=lifecycle)
        admission = None
        if phase == "open":
            admission = admit_transaction_child(Path(common), args.controller, transaction, "audit-state",
                sorted(set(args.writer_key)), sorted(set(args.dependency_key)))
            try:
                use_path.parent.mkdir(parents=True, exist_ok=True)
                with use_path.open("xb") as stream:
                    stream.write(use_bytes)
            except OSError:
                release_transaction_admission(Path(common), args.controller, transaction, "audit-state", terminal=False,
                    expected_admission_identity=admission["admission_identity"])
                fail("native recovery invocation already used or unavailable", decision="REQUIRED")
        idempotent = phase == "complete" and old["route_state"] == "SATISFIED"
        try:
            recheck()
            if idempotent:
                new_oid, record = old_oid, old
            else:
                new_oid, record = cas_route_record(repo, args.controller, expected, base,
                    "recovery-" + phase, route_transaction_id=transaction)
            if recheck() != attributed or current_ref(repo, args.controller, route_transaction_id=transaction) != (new_oid, record):
                fail("recovery lifecycle post-CAS readback changed", decision="REQUIRED")
            if phase in {"open", "complete"} and read_route_packet(args.packet, obligation, transaction, expected_target="audit-state")[0] != packet_raw:
                fail("recovery packet changed during delivery", decision="REQUIRED")
            if phase in {"return", "complete"}:
                if read_child_return(args.return_path, obligation, transaction, lifecycle["delivery"]["packet"]["digest"],
                        expected_child="audit-state", expected_capsule=capsule)[0] != return_raw:
                    fail("recovery return changed during readback", decision="REQUIRED")
            if phase == "complete":
                if read_governor_decision(args.decision, obligation, transaction, bytes_identity(return_raw)["digest"])[0] != decision_raw:
                    fail("recovery governor decision changed during readback", decision="REQUIRED")
        except SystemExit:
            if admission is not None:
                try:
                    if current_ref(repo, args.controller, route_transaction_id=transaction) == (old_oid, old):
                        if use_path.read_bytes() == use_bytes:
                            release_transaction_admission(Path(common), args.controller, transaction, "audit-state", terminal=False,
                                expected_admission_identity=admission["admission_identity"])
                            use_path.unlink()
                except (OSError, RouteUnavailable, SystemExit):
                    pass
            raise
        if phase == "complete":
            release_transaction_admission(Path(common), args.controller, transaction, "audit-state", terminal=True)
        if phase == "open":
            selected, reason = mapped_child_route(record)
            emit_visible_child_route(selected, reason, logical_task=open_logical_task(record))
    emit({"schema": RESULT_SCHEMA, "status": "RECOVERY_" + record["route_state"], "decision": "REQUIRED",
        "record_oid": new_oid, "record_identity": record["record_identity"], "route_transaction_id": transaction,
        "obligation_id": obligation, "route_state": record["route_state"], "advance_allowed": False,
        "continuity_current": False, "ordinary_effect_authority": "NONE", "subject_cause_attested": False,
        "recovery_cognition_accepted": phase == "complete", "owner_reconciliation_required": True,
        "idempotent": idempotent})

# Prospective R0033/R0037 refusal/disposition kernel. This is inserted into
# route-transaction.py; it creates no controller, registry or ref namespace.
RECOVERY_REFUSAL_SCHEMA = "implementaudit.audit-state-recovery-refusal.v1"
RECOVERY_ABANDONMENT_SCHEMA = "implementaudit.recovery-abandonment.v1"
RECOVERY_ATTEMPT_CAPSULE_SCHEMA = "implementaudit.post-compaction-recovery.v4"
AUDIT_STATE_FRONTIER_RETURN_V2_SCHEMA = "implementaudit.audit-state-minimum-frontier-return.v2"


def recovery_attempt_boundary_v1(capsule: dict[str, Any]) -> dict[str, Any]:
    """Project a qualified capsule's entire native turn, never a later row reset.

    Projection is not native qualification or proof of no reconstruction. The
    caller first uses the exact native/custody owner and separately evaluates
    governor conduct over this interval; serialized input cannot qualify itself.
    """
    if capsule.get("schema") not in {RECOVERY_V3_SCHEMA, RECOVERY_ATTEMPT_CAPSULE_SCHEMA}:
        fail("attempt boundary requires explicit recovery custody", decision="REQUIRED")
    native = capsule["native_observation"]
    identity = {key: exact_text(native.get(key), "attempt " + key) for key in
                ("native_thread_id", "native_session_id", "native_turn_id")}
    if digest_json(identity) != capsule.get("native_invocation_digest"):
        fail("attempt native invocation differs", decision="REQUIRED")
    return {"schema": "implementaudit.recovery-attempt-boundary.v1", **identity,
            "attempt_identity": capsule["native_invocation_digest"],
            "scope": "ENTIRE_QUALIFIED_NATIVE_TURN_THROUGH_OPEN",
            "input_occurrence_digest": native["row_digest"],
            "input_occurrence_ordinal": native["row_ordinal"],
            "subject_digest": capsule["custody"]["subject_digest"],
            "native_observation_identity": native["observation_identity"],
            "historical_misses_disposition": "PRESERVE_WITHOUT_RETROACTIVE_CREDIT"}


def recovery_refusal_record_v1(value: Any, capsule: dict[str, Any], packet: str,
                               obligation: str, transaction: str) -> dict[str, Any]:
    """Evidence-only refusal, deliberately outside successful frontier RETURN."""
    value = exact_keys(value, {"schema", "capsule_digest", "event_digest", "packet_digest",
        "obligation_id", "route_transaction_id", "reason", "evidence_digests",
        "context_disposition", "continuity_current", "ordinary_effect_authority",
        "recovery_cognition_accepted"}, "recovery refusal")
    if (capsule.get("schema") not in {RECOVERY_V3_SCHEMA, RECOVERY_ATTEMPT_CAPSULE_SCHEMA}
            or value["schema"] != RECOVERY_REFUSAL_SCHEMA
            or value["capsule_digest"] != capsule["capsule_digest"]
            or value["event_digest"] != capsule["event_digest"] or value["packet_digest"] != packet
            or value["obligation_id"] != obligation or value["route_transaction_id"] != transaction
            or value["reason"] not in {"GOVERNOR_RECONSTRUCTION_WITHIN_ATTEMPT",
                "ATTEMPT_ADMISSION_UNPROVED", "CUSTODY_OR_SOURCE_CHANGED", "INTERVENING_BOUNDARY_UNRESOLVED"}
            or value["context_disposition"] != "DISCARD_AFTER_RETURN"
            or value["continuity_current"] is not False
            or value["ordinary_effect_authority"] != "NONE"
            or value["recovery_cognition_accepted"] is not False):
        fail("recovery refusal identity or authority differs", decision="REQUIRED")
    evidence = value["evidence_digests"]
    if (not isinstance(evidence, list) or not 1 <= len(evidence) <= 16
            or any(not isinstance(item, str) or not HEX_RE.fullmatch(item) for item in evidence)
            or len(set(evidence)) != len(evidence)):
        fail("recovery refusal requires bounded existing evidence identities", decision="REQUIRED")
    return value


def recovery_abandon_base_v1(old_oid: str, old: dict[str, Any], disposition: Any) -> dict[str, Any]:
    """Build a terminal successor retaining exact old source, capsule and lifecycle.

    The production caller must already validate the old canonical record with
    immutable-child custody. This pure relation adds no native or source trust.
    """
    d = exact_keys(disposition, {"schema", "old_record_oid", "old_record_identity",
        "route_transaction_id", "capsule_digest", "admission_identity", "reason",
        "evidence_digest", "source_transition_digest", "successor_package",
        "successor_child_source", "continuity_current", "ordinary_effect_authority",
        "recovery_cognition_accepted"} | ({"preserved_source_root"} if isinstance(disposition, dict)
            and "preserved_source_root" in disposition else set()), "recovery abandonment")
    lifecycle = old.get("lifecycle")
    if (not isinstance(old_oid, str) or not OID_RE.fullmatch(old_oid)
            or old.get("schema") != RECOVERY_RECORD_SCHEMA or old.get("route_state") not in {"OPEN", "RETURNED"}
            or not isinstance(lifecycle, dict) or lifecycle.get("state") != old["route_state"]
            or lifecycle.get("governor_decision") is not None or lifecycle.get("governor_decision_count") != 0
            or old.get("continuity_current") is not False or old.get("ordinary_effect_authority") != "NONE"
            or old.get("record_identity") != digest_json({k:v for k,v in old.items() if k != "record_identity"})
            or d["schema"] != RECOVERY_ABANDONMENT_SCHEMA or d["old_record_oid"] != old_oid
            or d["old_record_identity"] != old["record_identity"]
            or d["route_transaction_id"] != old["route_transaction_id"]
            or d["capsule_digest"] != old["recovery_capsule"]["capsule_digest"]
            or d["reason"] not in {"ADMISSION_REJECTED", "CHILD_REFUSED"}
            or d["continuity_current"] is not False or d["ordinary_effect_authority"] != "NONE"
            or d["recovery_cognition_accepted"] is not False):
        fail("abandonment requires exact consumed unaccepted recovery", decision="REQUIRED")
    for key in ("admission_identity", "evidence_digest", "source_transition_digest"):
        if not isinstance(d[key], str) or not HEX_RE.fullmatch(d[key]):
            fail("abandonment evidence or source transition digest is malformed", decision="REQUIRED")
    if "preserved_source_root" in d:
        root = d["preserved_source_root"]
        if (not isinstance(root, str) or not Path(root).is_absolute() or ".." in Path(root).parts):
            fail("preserved source root is not an exact absolute custody locator", decision="REQUIRED")
    if (not isinstance(d["successor_package"], dict) or not isinstance(d["successor_child_source"], dict)
            or (d["successor_package"] == old["package"] and d["successor_child_source"] == old["child_source"])):
        fail("prospective abandonment requires an explicit successor source", decision="REQUIRED")
    return {**{k:v for k,v in old.items() if k != "record_identity"},
            "predecessor_record_oid": old_oid, "route_state": "ABANDONED", "disposition": d}


def validate_recovery_abandonment_v1(record: dict[str, Any], predecessor_oid: str,
                                    predecessor: dict[str, Any]) -> None:
    expected = recovery_abandon_base_v1(predecessor_oid, predecessor, record.get("disposition"))
    if record != {**expected, "record_identity": digest_json(expected)}:
        fail("abandonment changed preserved predecessor evidence", decision="REQUIRED")


def apply_recovery_abandonment_v1(old_oid: str, old: dict[str, Any], disposition: dict[str, Any],
                                *, read: Any, recheck: Any, cas: Any, release: Any) -> tuple[str, dict[str, Any]]:
    """Internal sequence under the existing namespace gate; no public callbacks.

    `recheck` is the production owner's native/custody/source/one-use/disposal
    readback, not a caller JSON proof. An uncertain CAS is never retried here.
    Exact terminal readback permits only idempotent completion of cleanup.
    """
    base = recovery_abandon_base_v1(old_oid, old, disposition)
    candidate = {**base, "record_identity": digest_json(base)}
    proof = recheck()
    current_oid, current = read()
    if current_oid == old_oid and current == old:
        if recheck() != proof or read() != (old_oid, old):
            fail("abandonment pre-CAS proof changed", decision="REQUIRED")
        new_oid, result = cas(old_oid, base)
    elif current == candidate and current_oid != old_oid:
        new_oid, result = current_oid, current
    else:
        fail("abandonment expected-old or exact terminal readback is stale", decision="REQUIRED")
    if (not isinstance(new_oid, str) or not OID_RE.fullmatch(new_oid)
            or result != candidate or read() != (new_oid, candidate) or recheck() != proof):
        fail("abandonment post-CAS state is unknown or foreign", decision="REQUIRED")
    release(disposition["admission_identity"])
    if read() != (new_oid, candidate) or recheck() != proof:
        fail("abandonment cleanup readback changed; no completion credit", decision="REQUIRED")
    return new_oid, candidate


def revalidate_preserved_recovery_sources_v1(old: dict[str, Any], preserved_root: str | None = None) -> None:
    """Hash retained old source files without executing them or treating them as current."""
    child = Path(old["child_source"]["identity"])
    if not child.is_absolute() or child.name != "SKILL.md" or child.parent.name != "audit-state":
        fail("preserved recovery child source path differs", decision="REQUIRED")
    governor = child.parent.parent / "implementaudit"
    if preserved_root is not None:
        # The separately reviewed plan binds relocation; original identity fields
        # remain untouched. Rehash all exact old bytes, never execute the copy.
        root = Path(preserved_root)
        if not root.is_absolute() or ".." in root.parts:
            fail("preserved source custody root differs", decision="REQUIRED")
        governor = root / "skills" / "implementaudit"
        child = root / "skills" / "audit-state" / "SKILL.md"
    paths = {"SKILL.md": governor / "SKILL.md",
        "route-obligations.md": governor / "references" / "route-obligations.md",
        **{name: governor / "scripts" / name for name in
           ("route-transaction.py", "claim-run.sh", "resolve-internal-skill.py")}}
    pins = old["package"].get("source_digests")
    if not isinstance(pins, dict) or set(pins) != set(paths):
        fail("preserved recovery package source population differs", decision="REQUIRED")
    if file_digest(child) != old["child_source"]["digest"] or any(file_digest(path) != pins[name] for name,path in paths.items()):
        fail("preserved old source bytes are unavailable or changed", decision="REQUIRED")


def retained_disposition_locator_v1(old: dict[str, Any], used_raw: bytes) -> dict[str, Any]:
    """Address derived by abandonment from a validated immutable old record.

    This relation is not independent native authentication or permission to
    select arbitrary history. The owner obtains old and .used itself.
    """
    if (not isinstance(old, dict) or old.get("schema") != RECOVERY_RECORD_SCHEMA
            or old.get("route_state") not in {"OPEN", "RETURNED"}
            or old.get("record_identity") != digest_json({k:v for k,v in old.items() if k != "record_identity"})
            or not isinstance(old.get("lifecycle"), dict)
            or old["lifecycle"].get("state") != old["route_state"]
            or old["lifecycle"].get("governor_decision") is not None
            or old["lifecycle"].get("governor_decision_count") != 0):
        fail("retained disposition requires exact unaccepted old recovery", decision="REQUIRED")
    capsule = recovery_capsule_v3_record(old["recovery_capsule"])
    if not isinstance(used_raw, bytes) or used_raw != recovery_capsule_use_v3(capsule, old["route_transaction_id"]):
        fail("retained disposition consumed marker differs", decision="REQUIRED")
    native = capsule["native_observation"]
    return {"schema": "implementaudit.retained-disposition-locator.v1",
        "old_record_identity": old["record_identity"], "capsule_digest": capsule["capsule_digest"],
        "used_digest": "sha256:" + hashlib.sha256(used_raw).hexdigest(),
        **{key:native[key] for key in ("native_thread_id", "native_session_id", "native_turn_id",
                                      "row_ordinal", "row_digest", "epoch_identity")}}


def read_abandonment_recovery_input_v1(repo: Path, old: dict[str, Any], used_raw: bytes,
                                     *, observer: Any) -> dict[str, Any]:
    """Historical occurrence plus current authentication, only for abandonment."""
    locator = retained_disposition_locator_v1(old, used_raw)
    capsule = old["recovery_capsule"]
    module = recovery_native_observer_module_v1()
    if type(observer) is not module.NativeRecoveryObserver:
        fail("disposition observer must be the exact source-owned implementation", decision="REQUIRED")
    if observer.repo != repo.resolve() or observer.plugin_root != Path(__file__).resolve().parents[3]:
        fail("disposition observer source/repository locator is foreign", decision="REQUIRED")
    committed_prefix = None
    committed_epoch = None
    if capsule["schema"] == RECOVERY_ATTEMPT_CAPSULE_SCHEMA:
        frozen = recovery_attempt_evidence_record_v1(old["lifecycle"].get("attempt_evidence"), capsule)
        committed_prefix = frozen["evidence"]["readback_prefix"]
        committed_epoch = frozen["evidence"]["native_epoch_frontier"]
    try:
        observed = observer.read_disposition_input(locator, committed_prefix=committed_prefix)
        if committed_epoch is not None and observed["native_epoch_frontier"] != committed_epoch:
            fail("retained disposition existing frozen epoch differs", decision="REQUIRED")
        custody = native_session_custody_v1(repo, observed["native_session_id"])
        candidate = select_retained_recovery_input_v1(observed["raw"],
            expected_thread_id=observed["native_thread_id"], expected_session_id=observed["native_session_id"],
            expected_turn_id=observed["native_turn_id"], after_ordinal=observed["after_ordinal"])
        if (candidate["input"]["subject"] != custody["subject"]
                or candidate["row_digest"] != locator["row_digest"] or candidate["ordinal"] != locator["row_ordinal"]
                or any(observed[key] != locator[key] for key in
                    ("native_thread_id", "native_session_id", "native_turn_id", "epoch_identity"))):
            fail("retained disposition native occurrence or physical custody differs", decision="REQUIRED")
        repeated = observer.read_disposition_input(locator, committed_prefix=committed_prefix)
        again = select_retained_recovery_input_v1(repeated["raw"],
            expected_thread_id=repeated["native_thread_id"], expected_session_id=repeated["native_session_id"],
            expected_turn_id=repeated["native_turn_id"], after_ordinal=repeated["after_ordinal"])
        if (candidate != again or any(observed.get(key) != repeated.get(key) for key in
                ("native_thread_id", "native_session_id", "native_turn_id", "epoch_identity",
                 "native_epoch_frontier", "disposition_locator_identity",
                 "observation_successor_identity", "observation_successor_spec_sha256"))
                or native_session_custody_v1(repo, observed["native_session_id"]) != custody):
            fail("retained disposition occurrence or authentication changed during readback", decision="REQUIRED")
    except (module.Refusal, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        fail("retained disposition native authentication is unavailable", decision="REQUIRED")
    body = {"schema": "implementaudit.native-recovery-input-observation.v1", "input": candidate["input"],
        "native_thread_id": observed["native_thread_id"], "native_session_id": observed["native_session_id"],
        "native_turn_id": observed["native_turn_id"], "row_ordinal": candidate["ordinal"],
        "row_digest": candidate["row_digest"], "epoch_identity": observed["epoch_identity"],
        "custody_record_identity": custody["record_identity"],
        "native_attribution": "QUALIFIED_BOUNDED_READBACK", "continuity_current": False,
        "ordinary_effect_authority": "NONE", "route_open_authority": "NONE"}
    result = {**body, "observation_identity": digest_json(body)}
    if result != capsule["native_observation"]:
        fail("retained disposition observation does not equal immutable original", decision="REQUIRED")
    return result


def command_abandon_recovery_v1(args: argparse.Namespace) -> None:
    """Prospective owner disposition, never successful RETURN or ordinary COMPLETE."""
    if (not OID_RE.fullmatch(args.expected_record) or not HEX_RE.fullmatch(args.route_transaction_id)
            or not CONTROLLER_RE.fullmatch(args.controller)):
        fail("abandonment exact controller/record/transaction locator is malformed", decision="REQUIRED")
    repo, _, common = repo_context()
    observer = recovery_observer_from_args_v1(repo, args)
    raw, plan = read_exact_artifact(args.disposition, "reviewed abandonment plan")
    if "sha256:" + hashlib.sha256(raw).hexdigest() != args.disposition_digest:
        fail("review-bound abandonment plan digest differs", decision="REQUIRED")
    exact_keys(plan, {"disposition", "execution_evidence", "evidence"}, "abandonment plan")
    d = plan["disposition"]
    if d.get("old_record_oid") != args.expected_record or d.get("route_transaction_id") != args.route_transaction_id:
        fail("abandonment plan expected record or transaction differs", decision="REQUIRED")
    with namespace_gate(common):
        old_raw = git_blob_bytes(repo, args.expected_record, "preserved recovery OPEN")
        old = decoded_artifact(old_raw, "preserved recovery OPEN")
        validate_route_record_semantics(repo, args.controller, args.expected_record, old,
                                       allow_immutable_active_child=True)
        recovery_abandon_base_v1(args.expected_record, old, d)
        evidence_raw = validate_bytes_identity(plan["evidence"], "abandonment factual evidence")
        if bytes_identity(evidence_raw)["digest"] != d["evidence_digest"]:
            fail("abandonment evidence differs", decision="REQUIRED")
        capsule = old["recovery_capsule"]
        if d["reason"] == "CHILD_REFUSED":
            recovery_refusal_record_v1(decoded_artifact(evidence_raw, "child refusal"), capsule,
                old["lifecycle"]["delivery"]["packet"]["digest"], old["obligation_id"], args.route_transaction_id)
        def admission() -> dict[str, Any]:
            target = Path(common) / "implementaudit-route-transactions" / args.controller / (
                args.route_transaction_id.removeprefix("sha256:") + ".json")
            _, value = read_exact_artifact(str(target), "owned recovery admission")
            exact_keys(value, {"schema", "controller_id", "route_transaction_id", "selected_child",
                "writer_keys", "dependency_keys", "status", "admission_identity"}, "owned recovery admission")
            identity = {k:v for k,v in value.items() if k not in {"status", "admission_identity"}}
            if (value["schema"] != TRANSACTION_ADMISSION_SCHEMA or value["controller_id"] != args.controller
                    or value["route_transaction_id"] != args.route_transaction_id or value["selected_child"] != "audit-state"
                    or value["status"] not in {"ACTIVE", "TERMINAL"}
                    or value["admission_identity"] != digest_json(identity)
                    or value["admission_identity"] != d["admission_identity"]):
                fail("abandonment admission ownership changed", decision="REQUIRED")
            return value
        def read() -> tuple[str | None, dict[str, Any] | None]:
            return current_ref(repo, args.controller, route_transaction_id=args.route_transaction_id,
                               allow_immutable_active_child=True)
        def recheck() -> dict[str, Any]:
            if "preserved_source_root" in d:
                revalidate_preserved_recovery_sources_v1(old, d["preserved_source_root"])
            else:
                revalidate_preserved_recovery_sources_v1(old)
            revalidate_recovery_custody_v1(repo, capsule["custody"])
            use = Path(common) / "implementaudit-recovery-capsules" / args.controller / (
                "native-v3-" + capsule["native_invocation_digest"].removeprefix("sha256:") + ".used")
            used_raw = use.read_bytes() if use.is_file() else None
            if used_raw != recovery_capsule_use_v3(capsule, args.route_transaction_id):
                fail("abandonment consumed native identity differs", decision="REQUIRED")
            native = read_abandonment_recovery_input_v1(repo, old, used_raw, observer=observer)
            if native != capsule["native_observation"]:
                fail("abandonment old native occurrence changed", decision="REQUIRED")
            # The observer freshly validates the independently review-bound source
            # transition and physical epoch/current inventories on every read.
            spec = observer.successor_spec()
            if (spec is None or d["source_transition_digest"] != "sha256:" + observer.observation_successor_sha256):
                fail("abandonment requires qualified successor source comparison", decision="REQUIRED")
            package, child = executing_package_evidence(repo, recovery_request_v3(capsule), "REQUIRED")
            if (package != d["successor_package"] or child != d["successor_child_source"]
                    or any(package[key] != old["package"][key] for key in ("head", "tree", "action_executable"))):
                fail("abandonment successor package or repository identity differs", decision="REQUIRED")
            attributed = recovery_binding_v3(repo, common, args, capsule, old["obligation_id"], args.route_transaction_id)
            if attributed["correlation_id"] != old["host_correlation_id"]:
                fail("abandonment physical H0 attribution differs", decision="REQUIRED")
            stages = resolve_execution_evidence(Path(args.store), plan["execution_evidence"], args.host_id,
                args.host_session_id, args.binding_generation, "audit-state", args.route_transaction_id,
                old["obligation_id"], old["lifecycle"]["delivery"]["packet"]["digest"])
            if read_exact_artifact(args.disposition, "reviewed abandonment plan")[0] != raw:
                fail("abandonment reviewed bytes changed", decision="REQUIRED")
            a = admission()
            if a["status"] == "TERMINAL" and read()[1].get("route_state") != "ABANDONED":
                fail("terminal admission has no exact abandonment", decision="REQUIRED")
            return {"native": native, "source_spec": spec, "package": package, "child": child,
                    "attributed": attributed, "stages": stages, "admission_identity": a["admission_identity"]}
        def cas(expected: str, base: dict[str, Any]) -> tuple[str, dict[str, Any]]:
            return cas_route_record(repo, args.controller, expected, base, "recovery-abandon",
                                    route_transaction_id=args.route_transaction_id)
        def release(identity: str) -> None:
            release_transaction_admission(Path(common), args.controller, args.route_transaction_id,
                "audit-state", terminal=True, expected_admission_identity=identity)
            if admission()["status"] != "TERMINAL":
                fail("abandonment admission release is unverified", decision="REQUIRED")
        oid, record = apply_recovery_abandonment_v1(args.expected_record, old, d,
            read=read, recheck=recheck, cas=cas, release=release)
    emit({"schema": RESULT_SCHEMA, "status": "RECOVERY_ABANDONED", "record_oid": oid,
        "record_identity": record["record_identity"], "route_transaction_id": args.route_transaction_id,
        "route_state": "ABANDONED", "advance_allowed": False, "continuity_current": False,
        "ordinary_effect_authority": "NONE", "recovery_cognition_accepted": False,
        "native_invocation_remains_consumed": True, "historical_source_retained": True})


def recovery_attempt_admission_record_v1(value: Any, expected_evidence: str | None = None) -> dict[str, Any]:
    """An explicit isolated-child verdict, not a mechanical claim of semantic truth."""
    value = exact_keys(value, {"schema", "evidence_digest", "outcome"}, "recovery attempt admission")
    if (value["schema"] != "implementaudit.recovery-attempt-admission.v1"
            or value["outcome"] != "ADMITTED" or not isinstance(value["evidence_digest"], str)
            or not HEX_RE.fullmatch(value["evidence_digest"])
            or (expected_evidence is not None and value["evidence_digest"] != expected_evidence)):
        fail("recovery attempt has no exact explicit admission verdict", decision="REQUIRED")
    return value


def recovery_attempt_evidence_record_v1(value: Any, capsule: dict[str, Any]) -> dict[str, Any]:
    """Historical shape only. Only the authenticated observer can mint evidence."""
    value = exact_keys(value, {"schema", "capsule_digest", "native_observation_identity",
        "source_reader_digest", "evidence", "evidence_digest"}, "qualified recovery attempt evidence")
    if (capsule["schema"] != RECOVERY_ATTEMPT_CAPSULE_SCHEMA
            or value["schema"] != "implementaudit.qualified-recovery-attempt-evidence.v1"
            or value["capsule_digest"] != capsule["capsule_digest"]
            or value["native_observation_identity"] != capsule["native_observation"]["observation_identity"]
            or not isinstance(value["source_reader_digest"], str) or not HEX_RE.fullmatch(value["source_reader_digest"])
            or value["evidence_digest"] != digest_json({k:v for k,v in value.items() if k != "evidence_digest"})):
        fail("recovery attempt evidence envelope differs", decision="REQUIRED")
    module = recovery_native_observer_module_v1()
    try:
        module.validate_attempt_evidence_shape(value["evidence"])
    except (module.Refusal, ValueError, TypeError, KeyError):
        fail("recovery attempt native evidence shape differs", decision="REQUIRED")
    evidence = value["evidence"]
    native = capsule["native_observation"]
    if (any(evidence[key] != native[key] for key in ("native_thread_id", "native_session_id", "native_turn_id", "epoch_identity"))
            or evidence["input_row_digest"] != native["row_digest"]):
        fail("recovery attempt evidence names another native occurrence", decision="REQUIRED")
    return value


def observe_recovery_attempt_v1(repo: Path, observer: Any, capsule: dict[str, Any],
                                frozen: dict[str, Any] | None = None) -> dict[str, Any]:
    """Existing authenticated native ingress; never accept a caller's clean flag."""
    if read_retained_recovery_input_v1(repo, observer=observer) != capsule["native_observation"]:
        fail("recovery attempt native/custody observation changed", decision="REQUIRED")
    module = recovery_native_observer_module_v1()
    try:
        if frozen is None:
            evidence = observer.read_attempt_evidence()
        else:
            recovery_attempt_evidence_record_v1(frozen, capsule)
            if frozen["source_reader_digest"] != RECOVERY_NATIVE_READER_DIGEST:
                fail("recovery attempt evidence executing reader changed", decision="REQUIRED")
            observer.revalidate_attempt_evidence(frozen["evidence"])
            return frozen
    except (module.Refusal, OSError, ValueError, KeyError, TypeError):
        fail("recovery attempt interval is incomplete, changed, or has an intervening boundary", decision="REQUIRED")
    # The source-owned scanner reports boundaries with their exact native row
    # digests. They invalidate only this attempt, not unrelated holons.
    if evidence["compaction_markers"]:
        fail("recovery attempt contains an intervening parent boundary", decision="REQUIRED")
    body = {"schema": "implementaudit.qualified-recovery-attempt-evidence.v1",
        "capsule_digest": capsule["capsule_digest"],
        "native_observation_identity": capsule["native_observation"]["observation_identity"],
        "source_reader_digest": RECOVERY_NATIVE_READER_DIGEST, "evidence": evidence}
    return recovery_attempt_evidence_record_v1({**body, "evidence_digest": digest_json(body)}, capsule)


def current_controller(
    repo: Path,
    controller: str,
    *,
    environment: dict[str, str] | None = None,
) -> dict[str, str]:
    claim = Path(__file__).with_name("claim-run.sh")
    bash = trusted_host_executable(repo, "bash")
    if environment is None:
        environment = sanitized_action_environment()
    claim_arg = bash_script_path(claim)
    current = run([str(bash), claim_arg, "--current-controller", controller], cwd=repo, label="controller currentness", environment=environment)
    parts = current.split("\t")
    if len(parts) != 4 or parts[0] != controller:
        fail("controller currentness returned a foreign or malformed record")
    try:
        explicit_run_root = str(Path(parts[2]).resolve(strict=True))
    except OSError as exc:
        fail(f"controller currentness returned an unreadable run root: {exc}")
    receipt = run(
        [str(bash), claim_arg, "--require-current-continuity", controller],
        cwd=repo,
        label="continuity currentness",
        environment=environment,
    )
    prefix = f"refs/implementaudit/continuity-receipts/{controller}/"
    if not receipt.startswith(prefix) or "@" not in receipt:
        fail("continuity receipt identity is malformed")
    generation = receipt[len(prefix) :].split("@", 1)[0]
    if not CONTINUITY_RE.fullmatch(generation):
        fail("continuity generation is malformed")
    receipt_oid = receipt.split("@", 1)[1]
    receipt_raw = git_blob_bytes(repo, receipt_oid, "continuity receipt")
    try:
        receipt_text = receipt_raw.decode("utf-8", "strict")
    except UnicodeError:
        fail("continuity receipt is not UTF-8")
    if "\r" in receipt_text or "\x00" in receipt_text:
        fail("continuity receipt has forbidden bytes")
    receipt_fields = receipt_text.rstrip("\n").split("\t")
    schema = receipt_fields[0] if receipt_fields else ""
    if schema == "implementaudit.continuity-receipt.v2":
        if (
            len(receipt_fields) != 12
            or receipt_fields[1] != controller
            or receipt_fields[3] != parts[3]
            or receipt_fields[10] != generation
        ):
            fail("current v2 continuity receipt is malformed or foreign")
        invalidation_oid = receipt_fields[8]
        boundary_kind = receipt_fields[9]
        next_action = receipt_fields[11]
    elif schema == "implementaudit.continuity-receipt.v3":
        if (
            len(receipt_fields) != 18
            or not receipt_raw.endswith(b"\n")
            or receipt_raw.endswith(b"\n\n")
            or b"\n" in receipt_raw[:-1]
            or receipt_fields[1] != controller
            or receipt_fields[2] != parts[3]
            or receipt_fields[3] != Path(parts[2]).name
            or receipt_fields[4] != generation
            or receipt_fields[6] != f"refs/implementaudit/current-generations/{controller}"
        ):
            fail("current v3 continuity receipt is malformed or foreign")
        invalidation_oid = receipt_fields[5]
        boundary_kind = ""
        next_action = receipt_fields[16]
    else:
        fail("R0033 route authority requires a current v2 or v3 continuity receipt")
    if invalidation_oid == "none":
        fail("route authority requires an exact current boundary invalidation")
    try:
        invalidation_fields = git_blob_bytes(repo, invalidation_oid, "continuity invalidation").decode(
            "utf-8", "strict"
        ).rstrip("\n").split("\t")
    except UnicodeError:
        fail("continuity boundary invalidation is not UTF-8")
    if (
        len(invalidation_fields) != 6
        or invalidation_fields[0] != "implementaudit.continuity-invalidation.v1"
        or invalidation_fields[1] != controller
        or (boundary_kind and invalidation_fields[4] != boundary_kind)
    ):
        fail("continuity boundary invalidation is malformed or foreign")
    boundary_kind = invalidation_fields[4]
    return {
        "controller_id": parts[0],
        "repository_identity": parts[1],
        "explicit_run_root": explicit_run_root,
        "claim_id": parts[3],
        "continuity_receipt": receipt,
        "continuity_generation": generation,
        "controller_record_oid": git(repo, "rev-parse", "--verify", f"refs/implementaudit/controllers/{controller}"),
        "boundary_kind": boundary_kind,
        "boundary_event_id": invalidation_fields[5],
        "next_action": next_action,
    }


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        fail(f"cannot hash mechanical evidence {path}: {exc}")
    return f"sha256:{digest.hexdigest()}"


def trusted_host_executable(repo: Path, name: str) -> Path:
    selected: str | None = None
    if os.name == "nt" and name == "bash":
        for key in ("ProgramFiles", "ProgramFiles(x86)"):
            if root := os.environ.get(key):
                candidate = Path(root) / "Git" / "bin" / "bash.exe"
                if candidate.is_file():
                    selected = str(candidate)
                    break
    if selected is None:
        selected = shutil.which(name)
    if selected is None:
        fail(f"trusted host executable is unavailable: {name}")
    resolved = Path(selected).resolve()
    try:
        resolved.relative_to(repo)
    except ValueError:
        pass
    else:
        fail("system action executable resolves inside target-repository custody")
    if os.name == "nt":
        roots = [
            Path(value).resolve()
            for key in ("ProgramFiles", "ProgramFiles(x86)", "SystemRoot")
            if (value := os.environ.get(key))
        ]
        if not any(str(resolved).casefold().startswith(str(root).casefold() + os.sep.casefold()) for root in roots):
            fail("system action executable is outside trusted host custody")
    else:
        cursor = resolved
        while True:
            info = os.lstat(cursor)
            if info.st_uid != 0 or info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                fail("system action executable is outside root-owned host custody")
            if cursor.parent == cursor:
                break
            cursor = cursor.parent
    return resolved


def executable_evidence(repo: Path, argv: list[str]) -> dict[str, str]:
    if mechanical_required_reason(argv) is not None:
        return {"requested": "route-trigger", "resolved": "R0033:built-in", "digest": digest_json(argv)}
    if argv in (["route-read-snapshot"], ["route-safe-status"]):
        return {"requested": argv[0], "resolved": "R0033:built-in", "digest": digest_json(argv)}
    if mechanical_action_class(argv) is None:
        return {"requested": argv[0], "resolved": "R0033:unadmitted", "digest": digest_json(argv)}
    if Path(argv[0]).name.lower() in {"claim-run.sh", "claim-run"}:
        resolved = Path(argv[0]).resolve()
    else:
        if argv[0] not in {"git", "bash", "sha256sum", "shasum"}:
            fail("action executable is not a closed trusted identity")
        resolved = trusted_host_executable(repo, argv[0])
    try:
        info = os.lstat(resolved)
    except OSError as exc:
        fail(f"action executable cannot be inspected: {exc}")
    if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
        fail("action executable is not a safe regular file")
    evidence = {"requested": argv[0], "resolved": str(resolved), "digest": file_digest(resolved)}
    if resolved.suffix.lower() == ".sh":
        interpreter_path = trusted_host_executable(repo, "bash")
        interpreter_info = os.lstat(interpreter_path)
        if not stat.S_ISREG(interpreter_info.st_mode) or stat.S_ISLNK(interpreter_info.st_mode):
            fail("shell action interpreter is not a safe regular file")
        evidence.update(
            {
                "interpreter_resolved": str(interpreter_path),
                "interpreter_digest": file_digest(interpreter_path),
            }
        )
    return evidence


def sanitized_action_environment() -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("GIT_", "LD_", "DYLD_"))
        and not key.startswith("BASH_FUNC_")
        and key not in {"BASH_ENV", "BASHOPTS", "CDPATH", "ENV", "SHELLOPTS"}
    }
    if os.name == "nt":
        candidates: list[Path] = []
        if program_files := os.environ.get("ProgramFiles"):
            git_root = Path(program_files) / "Git"
            candidates.extend((git_root / "cmd", git_root / "bin", git_root / "usr" / "bin"))
        if system_root := os.environ.get("SystemRoot"):
            candidates.extend((Path(system_root) / "System32", Path(system_root)))
        environment["PATH"] = os.pathsep.join(str(path.resolve()) for path in candidates if path.is_dir())
    else:
        environment["PATH"] = "/usr/bin:/bin"
    environment.update(
        {
            "GIT_ATTR_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "NUL" if os.name == "nt" else "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_EXTERNAL_DIFF": "",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_PAGER": "cat",
            "LC_ALL": "C",
            "PAGER": "cat",
        }
    )
    return environment


def pure_route_environment() -> dict[str, str]:
    """Return the exact host allowlist for the no-effect R0033 reader."""
    source = sanitized_action_environment()
    inherited = {
        "comspec", "pathext", "systemdrive", "systemroot", "temp", "tmp",
        "tmpdir", "windir",
    }
    fixed = {
        "GIT_ATTR_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM",
        "GIT_EXTERNAL_DIFF", "GIT_OPTIONAL_LOCKS", "GIT_PAGER", "LC_ALL",
        "PAGER", "PATH",
    }
    environment = {
        key: value for key, value in source.items()
        if key in fixed or key.casefold() in inherited
    }
    if "PATH" not in environment:
        fail("pure R0033 reader PATH is unavailable")
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONSAFEPATH"] = "1"
    return environment


def worktree_read_set(repo: Path) -> dict[str, Any]:
    git_executable = trusted_host_executable(repo, "git")
    git_read = [str(git_executable), "-c", "core.fsmonitor=false", "-c", "core.hooksPath="]
    raw_paths = subprocess.run(
        [*git_read, "ls-files", "-c", "-o", "--exclude-standard", "-z"],
        cwd=repo,
        env=sanitized_action_environment(),
        capture_output=True,
        check=False,
    )
    if raw_paths.returncode:
        fail("whole-worktree read-set enumeration failed")
    paths = sorted({item.decode("utf-8", "surrogateescape") for item in raw_paths.stdout.split(b"\0") if item})
    if len(paths) > 100_000:
        fail("whole-worktree read set exceeds the bounded population")
    digest = hashlib.sha256()
    for relative in paths:
        encoded = relative.encode("utf-8", "surrogateescape")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        target = repo / relative
        try:
            info = os.lstat(target)
        except OSError:
            digest.update(b"MISSING")
            continue
        if stat.S_ISLNK(info.st_mode):
            payload = os.readlink(target).encode("utf-8", "surrogateescape")
            digest.update(b"SYMLINK")
            digest.update(payload)
        elif stat.S_ISREG(info.st_mode):
            digest.update(file_digest(target).encode("ascii"))
        else:
            digest.update(b"NONREGULAR")
    environment = sanitized_action_environment()
    logical_index = run([*git_read, "ls-files", "-s", "-z"], cwd=repo, label="index read-set", environment=environment)
    metadata: dict[str, str] = {}
    for identity, git_path in (
        ("raw_index", "index"),
        ("repository_config", "config"),
        ("worktree_config", "config.worktree"),
        ("sparse_checkout", "info/sparse-checkout"),
    ):
        raw = run([*git_read, "rev-parse", "--git-path", git_path], cwd=repo, label=f"{identity} path", environment=environment)
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = repo / candidate
        candidate = candidate.resolve()
        try:
            info = os.lstat(candidate)
        except OSError:
            metadata[identity] = "MISSING"
        else:
            metadata[identity] = file_digest(candidate) if stat.S_ISREG(info.st_mode) and not stat.S_ISLNK(info.st_mode) else "UNSAFE"
    return {
        "population": len(paths),
        "digest": f"sha256:{digest.hexdigest()}",
        "logical_index_digest": digest_json(logical_index),
        "git_metadata": metadata,
        "submodules": "IGNORED_BY_EXACT_ARGV",
    }


def git_environment_requires_judgement(repo: Path) -> bool:
    git_executable = trusted_host_executable(repo, "git")
    completed = subprocess.run(
        [str(git_executable), "-c", "core.fsmonitor=false", "-c", "core.hooksPath=", "config", "--local", "--null", "--list"],
        cwd=repo,
        env=sanitized_action_environment(),
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        return True
    for entry in completed.stdout.split(b"\0"):
        key = entry.split(b"\n", 1)[0].decode("utf-8", "surrogateescape").casefold()
        if key.startswith("filter."):
            return True
    return False


def request_observations(
    repo: Path, current: dict[str, str], request: dict[str, Any]
) -> tuple[list[str], list[dict[str, str]]]:
    invalidators: list[str] = []
    boundary_expected = digest_json({"kind": request["boundary"]["kind"], "event_id": request["boundary"]["event_id"]})
    if request["boundary"]["digest"] != boundary_expected:
        invalidators.append("boundary:CONTRADICTORY")
    if (
        request["boundary"]["kind"] != current["boundary_kind"]
        or request["boundary"]["event_id"] != current["boundary_event_id"]
    ):
        invalidators.append("boundary:STALE")
    scope_expected = digest_json({"identity": request["scope"]["identity"]})
    if request["scope"]["digest"] != scope_expected:
        invalidators.append("scope:CONTRADICTORY")
    if request["scope"]["identity"] != current["next_action"]:
        invalidators.append("scope:STALE")
    action_expected = digest_json(
        {
            "identity": request["action"]["identity"],
            "class": request["action"]["class"],
            "argv": request["action"]["argv"],
        }
    )
    if request["action"]["digest"] != action_expected:
        invalidators.append("action:CONTRADICTORY")
    observed_inputs: list[dict[str, str]] = []
    for item in request["inputs"]:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts or "." in relative.parts:
            invalidators.append(f"{item['identity']}:MISSING")
            continue
        target = repo / relative
        try:
            resolved = target.resolve(strict=True)
            info = os.lstat(target)
            resolved.relative_to(repo)
        except (OSError, RuntimeError, ValueError):
            invalidators.append(f"{item['identity']}:MISSING")
            continue
        if target.absolute() != resolved or not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
            invalidators.append(f"{item['identity']}:MISSING")
            continue
        actual = file_digest(resolved)
        status = "CURRENT" if actual == item["digest"] else "STALE"
        if status != "CURRENT":
            invalidators.append(f"{item['identity']}:{status}")
        observed_inputs.append({"identity": item["identity"], "path": relative.as_posix(), "digest": actual, "status": status})
    current_paths = {item["path"] for item in observed_inputs if item["status"] == "CURRENT"}
    argv = request["action"]["argv"]
    executable = argv[0].lower()
    if executable == "git" and git_environment_requires_judgement(repo):
        invalidators.append("action-environment:JUDGEMENT_REQUIRED")
    if executable in {"sha256sum", "shasum"} and len(argv) == 2 and argv[1] not in current_paths:
        invalidators.append("action-input:MISSING")
    return sorted(invalidators), observed_inputs


def executing_package_evidence(
    repo: Path, request: dict[str, Any], decision: str | None = None
) -> tuple[dict[str, Any], dict[str, str]]:
    if decision is None:
        decision = (
            "NOT_REQUIRED"
            if mechanical_action_class(request["action"]["argv"]) in CLOSED_ACTION_CLASSES
            else "REQUIRED"
        )
    skill_root = Path(__file__).resolve().parent.parent
    source_paths = [
        skill_root / "SKILL.md",
        skill_root / "references" / "route-obligations.md",
        Path(__file__).resolve(),
        Path(__file__).resolve().with_name("claim-run.sh"),
    ]
    reason = mechanical_required_reason(request["action"]["argv"])
    if decision == "REQUIRED" and reason in CHILD_ROUTE_MAP:
        source_paths.append(Path(__file__).resolve().with_name("resolve-internal-skill.py"))
    if mechanical_action_class(request["action"]["argv"]) == "EXACT_PACKAGE_OR_TOPOLOGY_VERIFICATION":
        source_paths.append(Path(request["action"]["argv"][2]).resolve())
    package = {
        "head": git(repo, "rev-parse", "HEAD"),
        "tree": git(repo, "rev-parse", "HEAD^{tree}"),
        "source_digests": {path.name: file_digest(path) for path in source_paths},
        "action_executable": executable_evidence(repo, request["action"]["argv"]),
    }
    if mechanical_action_class(request["action"]["argv"]) in {
        "PURE_BOUNDED_READ_OR_VALIDATION", "SAFE_STATUS_OR_CONTAINMENT"
    }:
        package["worktree_read_set"] = worktree_read_set(repo)
    if decision == "REQUIRED" and reason in CHILD_ROUTE_MAP:
        identity_inputs: dict[str, str] = {}
        child_raw, child = child_delivery_bytes(CHILD_ROUTE_MAP[reason][0], identity_inputs=identity_inputs)
        for name, digest in identity_inputs.items():
            if name in package["source_digests"] and package["source_digests"][name] != digest:
                fail("executing package source changed during child identity binding")
            package["source_digests"][name] = digest
        child_source = {"identity": str(child), "digest": bytes_identity(child_raw)["digest"]}
    else:
        state = "UNMAPPED_REQUIRED" if decision == "REQUIRED" else decision
        identity = f"R0033:{state}:NO_CHILD"
        child_source = {"identity": identity, "digest": digest_json({"identity": identity})}
    if decision == "REQUIRED" and reason in CHILD_ROUTE_MAP:
        # The immediate binding consumer rechecks actual delivery, including
        # namespace facts; equal material hashes alone cannot bind a changed layout.
        final_inputs: dict[str, str] = {}
        final_raw, final_child = child_delivery_bytes(
            CHILD_ROUTE_MAP[reason][0], identity_inputs=final_inputs,
            expected_identity_inputs=identity_inputs,
        )
        if (final_raw != child_raw or final_child != child or final_inputs != identity_inputs):
            fail("child delivery inputs changed during executing package binding")
    return package, child_source


def route_semantic_basis(
    repo: Path,
    current: dict[str, str],
    request: dict[str, Any],
    host_binding_generation: str,
) -> dict[str, Any]:
    """Compute the R0033 route predicate without host-event attribution."""
    recovery_capsule = post_compaction_recovery_capsule(repo, request)
    noncurrent, observed_inputs = request_observations(repo, current, request)
    decision, classification, invalidators = classify(request, noncurrent)
    package, child_source = executing_package_evidence(repo, request, decision)
    identity_seed = {
        "request": request,
        "controller_record_oid": current["controller_record_oid"],
        "claim_id": current["claim_id"],
        "continuity_receipt": current["continuity_receipt"],
        "host_binding_generation": host_binding_generation,
        "package": package,
        "child_source": child_source,
        "recovery_capsule_digest": recovery_capsule["capsule_digest"] if recovery_capsule else None,
    }
    transaction_id = digest_json({"kind": "transaction", "seed": identity_seed})
    obligation_id = digest_json({"kind": "obligation", "seed": identity_seed}) if decision == "REQUIRED" else None
    return {
        "decision": decision,
        "classification": classification,
        "invalidators": invalidators,
        "observed_inputs": observed_inputs,
        "package": package,
        "child_source": child_source,
        "transaction_id": transaction_id,
        "obligation_id": obligation_id,
        "recovery_capsule": recovery_capsule,
    }


def route_semantics_from_basis(
    current: dict[str, str],
    request: dict[str, Any],
    host_binding_generation: str,
    host_correlation_id: str,
    basis: dict[str, Any],
) -> tuple[str, str, list[str], dict[str, Any], str, str, str | None]:
    """Finish the pure R0033 semantics with one retained dependency identity."""
    evidence = {
        "owner": {
            "controller_record_oid": current["controller_record_oid"],
            "claim_id": current["claim_id"],
            "run_root": current["explicit_run_root"],
        },
        "authority": {
            "continuity_generation": current["continuity_generation"],
            "continuity_receipt": current["continuity_receipt"],
        },
        "effect": {
            "action_identity": request["action"]["identity"],
            "action_digest": request["action"]["digest"],
            "derived_class": mechanical_action_class(request["action"]["argv"]),
        },
        "dependency": {
            "host_binding_generation": host_binding_generation,
            "host_correlation_id": host_correlation_id,
        },
        "inputs": basis["observed_inputs"],
        "package": basis["package"],
        "child_source": basis["child_source"],
    }
    fingerprint = digest_json({"request": request, "mechanical_evidence": evidence})
    return (
        basis["decision"],
        basis["classification"],
        basis["invalidators"],
        evidence,
        fingerprint,
        basis["transaction_id"],
        basis["obligation_id"],
    )


def validate_binding(
    repo: Path,
    common: str,
    args: argparse.Namespace,
    current: dict[str, str],
    request: dict[str, Any],
    obligation_id: str | None,
    transaction_id: str | None,
    *,
    event_id: str | None = None,
    replay: bool = False,
    expected_lineage: list[tuple[str, str, str]] | None = None,
) -> dict[str, Any]:
    def binding_failure(message: str) -> NoReturn:
        if replay:
            ambiguous_replay_stop(message)
        fail(message)

    def binding_run(command: list[str], label: str) -> str:
        completed = subprocess.run(command, cwd=repo, text=True, capture_output=True, check=False)
        if completed.returncode:
            detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
            binding_failure(f"{label} failed: {detail}")
        return completed.stdout.strip()

    binding_core = Path(__file__).with_name("host-session-binding.py")
    lookup_raw = binding_run(
        [
            sys.executable,
            str(binding_core),
            "--store",
            args.store,
            "lookup",
            "--host-id",
            args.host_id,
            "--host-session-id",
            args.host_session_id,
        ],
        "host binding lookup",
    )
    try:
        lookup = json.loads(lookup_raw)
    except json.JSONDecodeError:
        binding_failure("host binding lookup returned malformed output")
    binding = lookup.get("binding") if lookup.get("status") == "BOUND" else None
    if not isinstance(binding, dict):
        binding_failure("host session has no active exact binding")
    expected = {
        "binding_generation": args.binding_generation,
        "controller_id": args.controller,
        "claim_id": current["claim_id"],
        "explicit_run_root": current["explicit_run_root"],
        "repository_identity": str(repo),
        "git_common_directory_identity": common,
        "worktree_identity": str(repo),
        "applicable_continuity_generation": current["continuity_generation"],
        "applicable_continuity_receipt": current["continuity_receipt"],
    }
    for key, value in expected.items():
        if binding.get(key) != value:
            binding_failure(f"host session binding has stale or foreign {key}")
    command = [
        sys.executable,
        str(binding_core),
        "--store",
        args.store,
        "validate-event",
        "--host-id",
        args.host_id,
        "--host-session-id",
        args.host_session_id,
        "--binding-generation",
        args.binding_generation,
        "--controller-id",
        args.controller,
        "--claim-id",
        current["claim_id"],
        "--explicit-run-root",
        current["explicit_run_root"],
        "--repository-identity",
        str(repo),
        "--git-common-directory-identity",
        common,
        "--worktree-identity",
        str(repo),
        "--continuity-generation",
        current["continuity_generation"],
        "--continuity-receipt",
        current["continuity_receipt"],
        "--event-id",
        event_id or request["boundary"]["event_id"],
    ]
    if obligation_id is not None and transaction_id is not None:
        command.extend(["--obligation-id", obligation_id, "--route-transaction-id", transaction_id])
    for binding_generation, continuity_generation, continuity_receipt in expected_lineage or []:
        command.extend(
            [
                "--expected-lineage-link",
                binding_generation,
                continuity_generation,
                continuity_receipt,
            ]
        )
    attributed_raw = binding_run(command, "host event attribution")
    try:
        attributed = json.loads(attributed_raw)
    except json.JSONDecodeError:
        binding_failure("host event attribution returned malformed output")
    if attributed.get("status") != "ATTRIBUTED":
        binding_failure("host event attribution is unavailable")
    return attributed


def evaluate(
    repo: Path,
    common: str,
    args: argparse.Namespace,
    current: dict[str, str],
    request: dict[str, Any],
) -> tuple[str, str, list[str], dict[str, Any], str, str, str | None]:
    """Evaluate one effect path with mandatory exact R003A attribution."""
    basis = route_semantic_basis(
        repo, current, request, args.binding_generation)
    attributed = validate_binding(
        repo,
        common,
        args,
        current,
        request,
        basis["obligation_id"],
        basis["transaction_id"] if basis["obligation_id"] else None,
    )
    return route_semantics_from_basis(
        current,
        request,
        args.binding_generation,
        attributed["correlation_id"],
        basis,
    )


def validate_source_event_binding(
    repo: Path,
    common: str,
    args: argparse.Namespace,
    current: dict[str, str],
    request: dict[str, Any],
    event: dict[str, Any],
    obligation_id: str,
    transaction_id: str,
    *,
    replay: bool = False,
) -> None:
    attributed = validate_binding(
        repo,
        common,
        args,
        current,
        request,
        obligation_id,
        transaction_id,
        event_id=event["source_identity"],
        replay=replay,
    )
    provenance = event["provenance"]
    if provenance["event_id"] != event["source_identity"] or provenance["host_correlation_id"] != attributed.get(
        "correlation_id"
    ):
        if replay:
            ambiguous_replay_stop("reconstructed source provenance is unbound or conflicting")
        fail("source event provenance is unbound or conflicting", decision="REQUIRED")


@contextlib.contextmanager
def namespace_gate(common: str) -> Iterator[None]:
    common_root = Path(common).resolve()
    directory = common_root / "implementaudit-locks"
    for candidate in (common_root, directory):
        if os.path.lexists(candidate):
            info = os.lstat(candidate)
            if (
                not stat.S_ISDIR(info.st_mode)
                or stat.S_ISLNK(info.st_mode)
                or bool(getattr(info, "st_file_attributes", 0) & 0x400)
            ):
                fail("governed-writer namespace custody is aliased or unsafe")
    directory.mkdir(parents=True, exist_ok=True)
    gate = directory / "route-obligations.gate"
    if not gate.exists():
        try:
            descriptor = os.open(gate, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.write(descriptor, b"\0")
            os.close(descriptor)
        except FileExistsError:
            pass
    flags = os.O_RDWR | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(gate, flags)
    locked = False
    try:
        opened = os.fstat(descriptor)
        current = os.lstat(gate)
        unsafe = lambda item: (
            not stat.S_ISREG(item.st_mode)
            or stat.S_ISLNK(item.st_mode)
            or bool(getattr(item, "st_file_attributes", 0) & 0x400)
            or item.st_nlink != 1
            or item.st_size != 1
        )
        if unsafe(opened) or unsafe(current) or (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
            fail("governed-writer namespace gate is unsafe")
        if os.name == "nt":
            import msvcrt

            while True:
                try:
                    os.lseek(descriptor, 0, os.SEEK_SET)
                    msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                    locked = True
                    break
                except OSError as exc:
                    if exc.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                        raise
                    time.sleep(0.05)
        else:
            import fcntl

            fcntl.flock(descriptor, fcntl.LOCK_EX)
            locked = True
        yield
    finally:
        if locked and os.name == "nt":
            import msvcrt

            os.lseek(descriptor, 0, os.SEEK_SET)
            msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
        elif locked:
            import fcntl

            fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def projection_status(run_root: str, decision: str, oid: str) -> str:
    try:
        text = (Path(run_root) / "STATE.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return "UNAVAILABLE"
    decision_match = re.search(r"^\| Route decision projection \|\s*([^|]+?)\s*\|$", text, re.MULTILINE)
    record_match = re.search(r"^\| Route decision record \|\s*([^|]+?)\s*\|$", text, re.MULTILINE)
    if not decision_match or not record_match:
        return "LEGACY_ABSENT"
    projected_decision = decision_match.group(1).strip()
    projected_record = record_match.group(1).strip()
    return "CURRENT" if (projected_decision, projected_record) == (decision, oid) else "INVALID"


def mirror_observation(decision: str, route_state: str | None, claim: str) -> str:
    if claim == "ABSENT":
        return "IGNORED_ABSENT"
    canonical = route_state if route_state is not None else decision
    return "IGNORED_CORROBORATION" if claim == canonical else "IGNORED_CONTRADICTION"


def _pure_route_final_ref_fence(
    repo: Path, controller: str, controller_oid: str, route_oid: str
) -> None:
    controller_ref = f"refs/implementaudit/controllers/{controller}"
    route_ref = ref_name(controller)
    raw = git(
        repo,
        "for-each-ref",
        "--format=%(refname)%09%(objectname)",
        controller_ref,
        route_ref,
    )
    rows = raw.splitlines()
    observed: dict[str, str] = {}
    for row in rows:
        parts = row.split("\t")
        if len(parts) != 2 or parts[0] in observed or not OID_RE.fullmatch(parts[1]):
            fail("final R0033 route/controller ref fence is malformed")
        observed[parts[0]] = parts[1]
    if observed != {controller_ref: controller_oid, route_ref: route_oid}:
        fail("R0033 route or current-controller identity changed during pure validation")


def candidate_request_from_record(
    record: dict[str, Any], *, require_current_inputs: bool
) -> dict[str, Any]:
    retained_inputs = record.get("inputs")
    if not isinstance(retained_inputs, list) or not retained_inputs:
        fail("current route record has no exact observed input set")
    request_inputs: list[dict[str, str]] = []
    for index, item in enumerate(retained_inputs):
        observed = exact_keys(
            item,
            {"identity", "path", "digest", "status"},
            f"route inputs[{index}]",
        )
        if observed["status"] not in {"CURRENT", "STALE"}:
            fail("current route record has a malformed observed input status")
        if require_current_inputs and observed["status"] != "CURRENT":
            fail("pure route validation cannot reconstruct a noncurrent request input")
        request_inputs.append(
            {
                "identity": observed["identity"],
                "path": observed["path"],
                "digest": observed["digest"],
            }
        )
    return validate_request(
        {
            "schema": REQUEST_SCHEMA,
            "predicate_version": PREDICATE_VERSION,
            "boundary": record["boundary"],
            "scope": record["scope"],
            "action": record["action"],
            "inputs": request_inputs,
            **({"presentation": record["presentation"]} if "presentation" in record else {}),
        }
    )


def validate_pure_current_route(
    repo: Path,
    controller: str,
    expected_current: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Validate current route semantics without attributing a host event/effect."""
    environment = pure_route_environment()
    oid, record = current_ref(repo, controller)
    if oid is None or record is None:
        fail("canonical route decision is absent")
    validate_canonical_route_record_bytes(repo, oid, record)
    current = current_controller(repo, controller, environment=environment)
    if expected_current is not None:
        allowed = {
            "controller_id",
            "controller_record_oid",
            "claim_id",
            "explicit_run_root",
            "continuity_generation",
            "continuity_receipt",
            "boundary_kind",
            "boundary_event_id",
            "next_action",
        }
        if set(expected_current) != allowed or any(
            current.get(key) != value for key, value in expected_current.items()
        ):
            fail("current controller disagrees with the bounded C03 observation")
    bound_context = {
        "controller_id": current["controller_id"],
        "claim_id": current["claim_id"],
        "explicit_run_root": current["explicit_run_root"],
        "continuity_generation": current["continuity_generation"],
        "continuity_receipt": current["continuity_receipt"],
    }
    for key, value in bound_context.items():
        if record.get(key) != value:
            fail(f"route decision expired because bound {key} changed")
    exact_text(record.get("host_id"), "route host_id")
    exact_text(record.get("host_session_id"), "route host_session_id")
    binding_generation = record.get("host_binding_generation")
    correlation_id = record.get("host_correlation_id")
    if (
        not isinstance(binding_generation, str)
        or not CONTINUITY_RE.fullmatch(binding_generation)
        or not isinstance(correlation_id, str)
        or not HEX_RE.fullmatch(correlation_id)
    ):
        fail("route retained host dependency identity is malformed")
    request = candidate_request_from_record(record, require_current_inputs=True)
    basis = route_semantic_basis(
        repo, current, request, binding_generation)
    (
        decision,
        classification,
        invalidators,
        evidence,
        fingerprint,
        transaction_id,
        obligation_id,
    ) = route_semantics_from_basis(
        current, request, binding_generation, correlation_id, basis)
    retained_evidence = {
        key: evidence[key] for key in (
            "owner", "authority", "effect", "dependency")
    }
    if (
        record.get("evidence") != retained_evidence
        or record.get("inputs") != basis["observed_inputs"]
        or record.get("package") != basis["package"]
        or record.get("child_source") != basis["child_source"]
        or record.get("expiry_fingerprint") != fingerprint
        or record.get("decision") != decision
        or record.get("classification") != classification
        or record.get("invalidators") != invalidators
        or record.get("route_transaction_id") != transaction_id
        or record.get("obligation_id") != obligation_id
        or record.get("history_query") != normalized_history_query(request)
    ):
        fail("route decision no longer agrees with its exact live predicate")
    post_current = current_controller(repo, controller, environment=environment)
    post_oid, post_record = current_ref(repo, controller)
    if post_current != current or post_oid != oid or post_record != record:
        fail("R0033 route/controller semantics changed during pure validation")
    _pure_route_final_ref_fence(
        repo, controller, current["controller_record_oid"], oid)
    return {
        "controller_id": controller,
        "controller_record_oid": current["controller_record_oid"],
        "ref": ref_name(controller),
        "record_oid": oid,
        "record_identity": record["record_identity"],
        "decision": decision,
        "classification": classification,
        "route_transaction_id": transaction_id,
        "obligation_id": obligation_id,
        "route_state": record["route_state"],
    }


def binding_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--controller", required=True)
    parser.add_argument("--store", required=True)
    parser.add_argument("--host-id", required=True)
    parser.add_argument("--host-session-id", required=True)
    parser.add_argument("--binding-generation", required=True)


def common_args(parser: argparse.ArgumentParser) -> None:
    binding_args(parser)
    parser.add_argument("--request", required=True)
    parser.add_argument("--mirror-claim", choices=("ABSENT", "PENDING", "SATISFIED"), default="ABSENT")
    parser.add_argument("--requester-identity", default="governor")
    parser.add_argument("--writer-key", action="append", default=[])
    parser.add_argument("--dependency-key", action="append", default=[])


def validate_route_currentness(
    repo: Path,
    common: str,
    args: argparse.Namespace,
    request: dict[str, Any],
    record: dict[str, Any],
) -> tuple[dict[str, str], dict[str, Any], str]:
    if record.get("schema") == RECOVERY_RECORD_SCHEMA:
        fail("recovery cognition cannot enter ordinary route currentness", decision="REQUIRED")
    current = current_controller(repo, args.controller)
    bound_context = {
        "controller_id": args.controller,
        "claim_id": current["claim_id"],
        "explicit_run_root": current["explicit_run_root"],
        "continuity_generation": current["continuity_generation"],
        "continuity_receipt": current["continuity_receipt"],
        "host_id": args.host_id,
        "host_session_id": args.host_session_id,
        "host_binding_generation": args.binding_generation,
    }
    for key, value in bound_context.items():
        if record.get(key) != value:
            fail(f"route decision expired because bound {key} changed", decision=record["decision"])
    decision, classification, invalidators, evidence, fingerprint, transaction_id, obligation_id = evaluate(
        repo, common, args, current, request
    )
    if (
        record.get("expiry_fingerprint") != fingerprint
        or record.get("decision") != decision
        or record.get("classification") != classification
        or record.get("invalidators") != invalidators
        or record.get("route_transaction_id") != transaction_id
        or record.get("obligation_id") != obligation_id
        or record.get("history_query") != normalized_history_query(request)
    ):
        fail("route decision no longer agrees with its exact live predicate", decision=record["decision"])
    return current, evidence, fingerprint


def post_route_currentness(
    repo: Path,
    common: str,
    args: argparse.Namespace,
    request: dict[str, Any],
    expected_current: dict[str, str],
    expected_fingerprint: str,
    expected_oid: str,
) -> None:
    post_current = current_controller(repo, args.controller)
    post_eval = evaluate(repo, common, args, post_current, request)
    transaction_id = getattr(args, "route_transaction_id", None)
    post_oid, _ = current_ref(
        repo, args.controller, route_transaction_id=transaction_id
    )
    if post_current != expected_current or post_eval[4] != expected_fingerprint or post_oid != expected_oid:
        fail("route lifecycle lost currentness during its canonical transition", decision="REQUIRED")


def cas_route_record(
    repo: Path,
    controller: str,
    expected_oid: str,
    record_base: dict[str, Any],
    label: str,
    *,
    route_transaction_id: str | None = None,
) -> tuple[str, dict[str, Any]]:
    record = {**record_base, "record_identity": digest_json(record_base)}
    raw = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
    new_oid = write_route_record_blob(repo, raw)
    try:
        if route_transaction_id is None:
            completed = subprocess.run(
                [str(trusted_host_executable(repo, "git")), "update-ref", ref_name(controller), new_oid, expected_oid],
                cwd=repo,
                env=sanitized_action_environment(),
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode:
                fail(f"{label} CAS lost the current-record race", decision="REQUIRED")
        else:
            transaction_route_ref_cas(
                repo, controller, route_transaction_id, expected_oid, new_oid
            )
    except RouteUnavailable as exc:
        fail(str(exc), decision="REQUIRED")
    reread_oid, reread = current_ref(
        repo, controller, route_transaction_id=route_transaction_id
    )
    if reread_oid != new_oid or reread != record:
        fail(f"{label} canonical record reread failed", decision="REQUIRED")
    return new_oid, record


def skill_frontmatter_identity(raw: bytes, label: str) -> tuple[str, str]:
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeError as exc:
        fail(f"{label} bytes are not exact UTF-8: {exc}")
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if frontmatter is None:
        fail(f"{label} has no exact YAML frontmatter")
    name = re.search(r"^name:\s*([^\s\"]+)\s*$", frontmatter.group(1), re.MULTILINE)
    version = re.search(r'^\s+version:\s*"([^"]+)"\s*$', frontmatter.group(1), re.MULTILINE)
    if name is None or version is None:
        fail(f"{label} frontmatter has no exact name/version identity")
    return name.group(1), version.group(1)


def child_delivery_snapshot(path: Path, label: str) -> tuple[bytes, tuple[int, ...]]:
    """Read one exact delivery input and retain its physical identity for reread."""
    def identity(info: os.stat_result) -> tuple[int, ...]:
        if (not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode)
                or getattr(info, "st_file_attributes", 0) & 0x400 or info.st_nlink != 1):
            fail(f"{label} is not an unaliased regular delivery input")
        return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
    try:
        if path.absolute() != path.resolve(strict=True):
            fail(f"{label} traverses a delivery input alias")
        before = identity(os.lstat(path))
        with path.open("rb") as stream:
            opened = identity(os.fstat(stream.fileno()))
            raw = stream.read()
            finished = identity(os.fstat(stream.fileno()))
        if before != opened or opened != finished or finished != identity(os.lstat(path)) or len(raw) != before[2]:
            fail(f"{label} changed while its delivery bytes were read")
        return raw, before
    except OSError as exc:
        fail(f"{label} cannot be read as an exact delivery input: {exc}")


def standalone_child_delivery_namespace(skill_root: Path) -> dict[str, Any]:
    """Observe the finite existing standalone namespace; not a filesystem lock."""
    children = ("audit-state", "audit-assess", "audit-implement", "audit-andon")
    forbidden = {name: (skill_root / name).exists() or (skill_root / name).is_symlink()
                 for name in ("skills", "hooks", ".codex-plugin", ".claude-plugin")}
    peers = {name: (skill_root.parent / name / "SKILL.md").exists()
             or (skill_root.parent / name / "SKILL.md").is_symlink() for name in children}
    if any(forbidden.values()):
        fail("standalone delivery contains canonical discovery or hook topology")
    if any(peers.values()):
        fail("standalone delivery has an ambiguous canonical child peer")
    directory = skill_root / "internal-procedures"
    try:
        info = os.lstat(directory)
        if (directory.absolute() != directory.resolve(strict=True) or not stat.S_ISDIR(info.st_mode)
                or stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400):
            fail("standalone procedure namespace traverses an alias")
        names = sorted(p.name for p in directory.iterdir())
        if set(names) != {name + ".md" for name in children}:
            fail("standalone delivery procedure population is not exact")
    except OSError as exc:
        fail(f"standalone procedure population cannot be read: {exc}")
    return {"procedures": names, "forbidden_paths": forbidden, "canonical_peers": peers}


def standalone_child_delivery_identity(
    skill_root: Path, governor_version: str, material: dict[Path, tuple[bytes, tuple[int, ...]]]
) -> None:
    """Validate existing projection identity only; metadata grants no authority."""
    children = ("audit-state", "audit-assess", "audit-implement", "audit-andon")
    required = ["implementaudit", *children]
    internal = [
        {"name": name, "maintainer_only": name == "audit-implement", "directly_invocable": name == "audit-andon"}
        for name in children
    ]
    procedure_names = {f"internal-procedures/{name}.md" for name in children}
    def read(name: str) -> bytes:
        path = skill_root / name
        if path not in material:
            material[path] = child_delivery_snapshot(path, name)
        return material[path][0]
    def metadata(name: str) -> dict[str, Any]:
        def nonfinite(value: str) -> NoReturn:
            raise ValueError("nonfinite metadata number")
        try:
            value = json.loads(read(name).decode("utf-8", "strict"), object_pairs_hook=unique_object, parse_constant=nonfinite)
        except (ValueError, UnicodeError) as exc:
            fail(f"standalone {name} is malformed identity metadata: {exc}")
        if not isinstance(value, dict):
            fail(f"standalone {name} identity metadata is not an object")
        return value
    package = metadata("IMPLEMENTAUDIT_PACKAGE.json")
    inventory = metadata("IMPLEMENTAUDIT_INVENTORY.json")
    package_keys = {"schema_version", "logical_package", "package_name", "description", "publisher",
                    "marketplace", "runtime_version", "release_family", "public_governor", "public_entrypoint",
                    "required_skills", "internal_skills", "shared_resource_roots", "host_manifests",
                    "generated_projections", "inventory_contract", "budgets", "generic_activegraph_dependency"}
    inventory_keys = {"schema", "artifact_role", "package_name", "runtime_version", "release_family",
                      "public_governor", "required_skills", "internal_skills", "source", "members"}
    if (set(package) != package_keys or type(package.get("schema_version")) is not int
            or package["schema_version"] != 1 or package.get("logical_package") != "IMPLEMENTAUDIT_PLUGIN"
            or package.get("public_entrypoint") != "/implementaudit" or set(inventory) != inventory_keys
            or inventory.get("schema") != "implementaudit.package-inventory.v1"
            or inventory.get("artifact_role") != "standalone_compatibility"):
        fail("standalone package/inventory schema or role is not exact")
    if (package.get("generated_projections") != {
            "canonical_plugin": {"artifact": "IMPLEMENTAUDIT.plugin.zip", "layout": "plugin-root"},
            "standalone_compatibility": {"artifact": "IMPLEMENTAUDIT.skill", "layout": "flattened-skill"}}
            or package.get("inventory_contract") != {"format": "implementaudit.package-inventory.v1",
                "sort": "utf8-posix-path", "fields": ["path", "bytes", "sha256"],
                "source_binding": ["commit", "tree", "worktree_state"]}):
        fail("standalone package projection/inventory identity contract differs")
    for data in (package, inventory):
        if (data.get("package_name") != "implementaudit" or data.get("public_governor") != "implementaudit"
                or data.get("runtime_version") != governor_version or data.get("release_family") != "v" + governor_version + ".0"
                or data.get("required_skills") != required or data.get("internal_skills") != internal
                or any(type(row.get(key)) is not bool for row in data.get("internal_skills", [])
                       for key in ("maintainer_only", "directly_invocable"))):
            fail("standalone package/child identity disagrees with the executing governor")
    source = inventory.get("source")
    if (not isinstance(source, dict) or set(source) != {"commit", "tree", "worktree_state"}
            or any(not isinstance(source.get(k), str) or not re.fullmatch(r"[0-9a-f]{40}", source[k]) for k in ("commit", "tree"))
            or not isinstance(source.get("worktree_state"), str)
            or source["worktree_state"] not in {"clean", "dirty"}):
        fail("standalone inventory source identity is malformed")
    rows = inventory.get("members")
    if not isinstance(rows, list) or not rows:
        fail("standalone inventory member identities are missing")
    members: dict[str, dict[str, Any]] = {}
    folded: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            fail("standalone inventory member identity is malformed")
        name = row["path"]
        if (not isinstance(name, str) or not name or "\\" in name or ":" in name
                or any(ord(c) < 32 for c in name) or any(p in {"", ".", ".."} for p in name.split("/"))
                or name.casefold() in folded or type(row["bytes"]) is not int or row["bytes"] < 0
                or not isinstance(row["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])):
            fail("standalone inventory member path/bytes/digest is not exact")
        members[name] = row; folded.add(name.casefold())
    if ({name for name in members if name.startswith("internal-procedures/")} != procedure_names
            or any(name == "IMPLEMENTAUDIT_INVENTORY.json" or name.startswith(("skills/", "hooks/", ".codex-plugin/", ".claude-plugin/")) for name in members)):
        fail("standalone inventory exposes an ambiguous projection population")
    for name in ("SKILL.md", "IMPLEMENTAUDIT_PACKAGE.json", *sorted(procedure_names)):
        raw = read(name)
        if members.get(name) != {"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}:
            fail(f"standalone {name} disagrees with its unique inventory identity")
        if name in procedure_names:
            try:
                raw.decode("utf-8", "strict")
            except UnicodeError:
                fail("standalone procedure bytes are not exact UTF-8")
            if raw.startswith(b"---\n") or raw.startswith(b"---\r\n"):
                fail("standalone procedure retains discoverable YAML frontmatter")

def resolved_child_delivery_path(mapped_child: str, governor: Path, resolver: Path) -> Path:
    completed = subprocess.run(
        [sys.executable, str(resolver), "--governor", str(governor), "--child", mapped_child],
        cwd=governor.parent, env=pure_route_environment(), text=True, capture_output=True, check=False,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        fail(f"internal-child resolver refused {mapped_child}: {detail}")
    rows = completed.stdout.splitlines()
    if len(rows) != 1 or completed.stderr:
        fail("internal-child resolver returned a noncanonical result stream")
    return Path(rows[0])


def child_delivery_bytes(
    mapped_child: str, *, identity_inputs: dict[str, str] | None = None,
    expected_identity_inputs: dict[str, str] | None = None,
) -> tuple[bytes, Path]:
    if mapped_child not in {child for child, _ in CHILD_ROUTE_MAP.values()}:
        fail("governed child route is outside the closed population")
    skill_root = Path(__file__).resolve().parent.parent
    governor = skill_root / "SKILL.md"
    resolver = Path(__file__).resolve().with_name("resolve-internal-skill.py")
    material = {
        governor: child_delivery_snapshot(governor, "governor"),
        resolver: child_delivery_snapshot(resolver, "internal-child resolver"),
    }
    child = resolved_child_delivery_path(mapped_child, governor, resolver)
    canonical = (skill_root.parent / mapped_child / "SKILL.md").absolute()
    standalone = (skill_root / "internal-procedures" / f"{mapped_child}.md").absolute()
    if child not in {canonical, standalone}:
        fail(f"resolved {mapped_child} child is outside the executing package layout")
    material[child] = child_delivery_snapshot(child, "governed child")
    child_raw, governor_raw = material[child][0], material[governor][0]
    governor_name, governor_version = skill_frontmatter_identity(governor_raw, "governor")
    if governor_name != "implementaudit":
        fail("executing governor identity is not implementaudit")
    if child == canonical:
        child_name, child_version = skill_frontmatter_identity(child_raw, "governed child")
        if child_name != mapped_child or child_version != governor_version:
            fail("resolved child frontmatter identity/version disagrees with the executing governor")
    else:
        namespace_before = standalone_child_delivery_namespace(skill_root)
        standalone_child_delivery_identity(skill_root, governor_version, material)
    for path, before in material.items():
        if child_delivery_snapshot(path, path.name) != before:
            fail("child delivery identity input changed before delivery")
    # Bind representation inputs through the existing package evidence owner.
    observed_inputs = {path.name: bytes_identity(material[path][0])["digest"] for path in
        (governor, resolver, *(skill_root / name for name in
            ("IMPLEMENTAUDIT_PACKAGE.json", "IMPLEMENTAUDIT_INVENTORY.json") if child == standalone))}
    if expected_identity_inputs is not None and child == standalone:
        if (not isinstance(expected_identity_inputs, dict) or any(
                expected_identity_inputs.get(name) != observed_inputs[name]
                for name in ("IMPLEMENTAUDIT_PACKAGE.json", "IMPLEMENTAUDIT_INVENTORY.json"))):
            fail("standalone delivery identity metadata differs from the bound route package")
    if identity_inputs is not None:
        identity_inputs.update(observed_inputs)
    # Reobserve the full existing resolver contract and standalone namespace
    # after material rereads and output construction. These are finite checks,
    # not atomicity or detection of every intervening change-and-restore.
    if resolved_child_delivery_path(mapped_child, governor, resolver) != child:
        fail("child delivery namespace selected a different role or path")
    if child == standalone and standalone_child_delivery_namespace(skill_root) != namespace_before:
        fail("standalone delivery namespace changed before delivery")
    return child_raw, child

def emit_visible_child_route(mapped_child: str, reason: str, *, logical_task: str) -> None:
    """OPEN is prospective selection, never verified native worker LOAD."""
    logical_task_name(logical_task, mapped_child)
    print("```ini\nCHILD_TASK=" + logical_task + "\nCHILD_TASK_KIND=GOVERNED_CHILD_SKILL\n"
          "CHILD_SKILL_SELECTED=" + mapped_child + "\nSTATUS=OPEN\nLOAD=UNVERIFIED\n```\n"
          "I'm opening the `" + logical_task + "` holon for the `" + mapped_child +
          "` skill to " + reason + ".", file=sys.stderr)


def command_open(args: argparse.Namespace) -> None:
    if getattr(args, "recovery_capsule", None) is not None:
        return command_recovery_transaction_v1(args, "open")
    repo, _, common = repo_context()
    request = read_request(args.request)
    with namespace_gate(common):
        old_oid, old = current_ref(
            repo, args.controller, route_transaction_id=args.route_transaction_id
        )
        if old_oid is None or old is None or args.expected_record != old_oid:
            fail("child-open CAS expected record is stale", decision="REQUIRED")
        if old["decision"] != "REQUIRED" or old.get("route_state") != "UNSATISFIED" or "lifecycle" in old:
            fail("only an exact unsatisfied REQUIRED obligation can open a child", decision=old["decision"])
        mapped_child, visible_reason = mapped_child_route(old)
        if args.route_transaction_id is not None and old["route_transaction_id"] != args.route_transaction_id:
            fail("child-open transaction custody is foreign", decision="REQUIRED")
        try:
            require_governor_dispatch_requester(args.requester_identity)
        except RouteUnavailable as exc:
            fail(str(exc), decision="REQUIRED")
        logical_task = logical_task_name(getattr(args, "logical_task", None), mapped_child,
                                         old["route_transaction_id"], old.get("host_session_id"))
        current, _, fingerprint = validate_route_currentness(repo, common, args, request, old)
        packet_raw, packet = read_route_packet(
            args.packet,
            old["obligation_id"],
            old["route_transaction_id"],
            expected_target=mapped_child,
        )
        validate_source_event_binding(
            repo,
            common,
            args,
            current,
            request,
            packet["source_event"],
            old["obligation_id"],
            old["route_transaction_id"],
        )
        capsule = post_compaction_recovery_capsule(repo, request)
        child_raw, child_path = child_delivery_bytes(mapped_child, expected_identity_inputs=old["package"]["source_digests"])
        delivery = {
            "child": {"identity": str(child_path), **bytes_identity(child_raw)},
            "packet": bytes_identity(packet_raw),
        }
        if old.get("child_source") != {
            "identity": str(child_path),
            "digest": delivery["child"]["digest"],
        }:
            fail("mapped child delivery disagrees with the bound route decision", decision="REQUIRED")
        lifecycle = {
            "state": "OPEN",
            "logical_task": logical_task,
            "required_record_oid": old_oid,
            "delivery": delivery,
            "child_return": None,
            "governor_decision": None,
            "governor_decision_count": 0,
            "source_event_status": "active",
            "execution_evidence": None,
        }
        record_base = {
            **{key: value for key, value in old.items() if key != "record_identity"},
            "predecessor_record_oid": old_oid,
            "route_state": "OPEN",
            "child_lifecycle_owned": True,
            "lifecycle": lifecycle,
        }
        try:
            admission = admit_transaction_child(
                Path(common),
                args.controller,
                old["route_transaction_id"],
                mapped_child,
                sorted(set(args.writer_key)),
                sorted(set(args.dependency_key)),
            )
            if capsule is not None:
                try:
                    consume_recovery_capsule(Path(common), args.controller, capsule)
                except RouteUnavailable:
                    release_transaction_admission(
                        Path(common),
                        args.controller,
                        old["route_transaction_id"],
                        mapped_child,
                        terminal=False,
                        expected_admission_identity=admission["admission_identity"],
                    )
                    raise
        except RouteUnavailable as exc:
            fail(str(exc), decision="REQUIRED")
        try:
            new_oid, record = cas_route_record(
                repo,
                args.controller,
                old_oid,
                record_base,
                "child-open",
                route_transaction_id=args.route_transaction_id,
            )
        except SystemExit:
            try:
                # CAS may have committed before its canonical reread failed.
                # Release custody only while the exact pre-OPEN record remains.
                cleanup_oid, cleanup_record = current_ref(
                    repo, args.controller, route_transaction_id=args.route_transaction_id
                )
                if cleanup_oid == old_oid and cleanup_record == old:
                    release_transaction_admission(
                        Path(common),
                        args.controller,
                        old["route_transaction_id"],
                        mapped_child,
                        terminal=False,
                        expected_admission_identity=admission["admission_identity"],
                    )
                    if capsule is not None:
                        release_recovery_capsule(Path(common), args.controller, capsule)
            except (OSError, RouteUnavailable, SystemExit):
                pass
            raise
        post_route_currentness(repo, common, args, request, current, fingerprint, new_oid)
        packet_after, _ = read_route_packet(
            args.packet,
            old["obligation_id"],
            old["route_transaction_id"],
            expected_target=mapped_child,
        )
        child_after, _ = child_delivery_bytes(mapped_child, expected_identity_inputs=old["package"]["source_digests"])
        if bytes_identity(packet_after) != delivery["packet"] or bytes_identity(child_after) != {
            key: value for key, value in delivery["child"].items() if key != "identity"
        }:
            fail("child or packet bytes changed during delivery", decision="REQUIRED")
        emit_visible_child_route(mapped_child, visible_reason, logical_task=open_logical_task(record))
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "CHILD_OPEN",
            "decision": "REQUIRED",
            "route_state": "OPEN",
            "advance_allowed": False,
            "enforcement_available": True,
            "record_oid": new_oid,
            "record_identity": record["record_identity"],
            "obligation_id": old["obligation_id"],
            "route_transaction_id": old["route_transaction_id"],
            "delivery": delivery,
            "holon_lifecycle": holon_lifecycle_projection(
                "OPEN",
                mapped_child,
                old["route_transaction_id"],
                old["obligation_id"],
            ),
            "history_read_performed": False,
        }
    )


def command_return(args: argparse.Namespace) -> None:
    if getattr(args, "recovery_capsule", None) is not None:
        return command_recovery_transaction_v1(args, "return")
    repo, _, common = repo_context()
    request = read_request(args.request)
    with namespace_gate(common):
        old_oid, old = current_ref(
            repo, args.controller, route_transaction_id=args.route_transaction_id
        )
        if old_oid is None or old is None or args.expected_record != old_oid:
            fail("child-return CAS expected record is stale", decision="REQUIRED")
        lifecycle = old.get("lifecycle")
        if old["decision"] != "REQUIRED" or not isinstance(lifecycle, dict) or lifecycle.get("state") != "OPEN":
            fail("only an exact OPEN route can accept a child return", decision=old["decision"])
        mapped_child, _ = mapped_child_route(old)
        current, _, fingerprint = validate_route_currentness(repo, common, args, request, old)
        capsule = post_compaction_recovery_capsule(repo, request)
        return_raw, returned = read_child_return(
            args.return_path,
            old["obligation_id"],
            old["route_transaction_id"],
            lifecycle["delivery"]["packet"]["digest"],
            expected_child=mapped_child,
            expected_capsule=capsule,
        )
        raw_execution = returned["payload"].get("holon_execution_evidence")
        resolved_execution = None
        if raw_execution is not None:
            resolved_execution = resolve_execution_evidence(
                Path(args.store),
                raw_execution,
                args.host_id,
                args.host_session_id,
                args.binding_generation,
                mapped_child,
                old["route_transaction_id"],
                old["obligation_id"],
                lifecycle["delivery"]["packet"]["digest"],
            )
        returned_identity = bytes_identity(return_raw)
        next_lifecycle = {
            **lifecycle,
            "state": "RETURNED",
            "child_return": returned_identity,
            "execution_evidence": resolved_execution,
        }
        record_base = {
            **{key: value for key, value in old.items() if key != "record_identity"},
            "predecessor_record_oid": old_oid,
            "route_state": "RETURNED",
            "lifecycle": next_lifecycle,
        }
        new_oid, record = cas_route_record(
            repo,
            args.controller,
            old_oid,
            record_base,
            "child-return",
            route_transaction_id=args.route_transaction_id,
        )
        post_route_currentness(repo, common, args, request, current, fingerprint, new_oid)
        return_after, _ = read_child_return(
            args.return_path,
            old["obligation_id"],
            old["route_transaction_id"],
            lifecycle["delivery"]["packet"]["digest"],
            expected_child=mapped_child,
            expected_capsule=capsule,
        )
        if bytes_identity(return_after) != returned_identity:
            fail("child return bytes changed during canonical return", decision="REQUIRED")
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "CHILD_RETURNED",
            "decision": "REQUIRED",
            "route_state": "RETURNED",
            "advance_allowed": False,
            "enforcement_available": True,
            "record_oid": new_oid,
            "record_identity": record["record_identity"],
            "child_return": returned_identity,
            "holon_lifecycle": holon_lifecycle_projection(
                "RETURNED",
                mapped_child,
                old["route_transaction_id"],
                old["obligation_id"],
                execution_evidence=next_lifecycle["execution_evidence"],
            ),
            "history_read_performed": False,
        }
    )


def completion_payload(oid: str, record: dict[str, Any], *, idempotent: bool) -> dict[str, Any]:
    mapped_child, _ = mapped_child_route(record)
    return {
        "schema": RESULT_SCHEMA,
        "status": "ROUTE_COMPLETE",
        "decision": "REQUIRED",
        "route_state": "SATISFIED",
        "advance_allowed": True,
        "enforcement_available": True,
        "record_oid": oid,
        "record_identity": record["record_identity"],
        "governor_decision_count": 1,
        "post_return_currentness": "VERIFIED",
        "holon_lifecycle": holon_lifecycle_projection(
            "SATISFIED",
            mapped_child,
            record["route_transaction_id"],
            record["obligation_id"],
            execution_evidence=record.get("lifecycle", {}).get("execution_evidence"),
        ),
        "history_read_performed": False,
        "idempotent": idempotent,
    }


def command_complete(args: argparse.Namespace) -> None:
    if getattr(args, "recovery_capsule", None) is not None:
        return command_recovery_transaction_v1(args, "complete")
    repo, _, common = repo_context()
    request = read_request(args.request)
    with namespace_gate(common):
        old_oid, old = current_ref(
            repo, args.controller, route_transaction_id=args.route_transaction_id
        )
        if old_oid is None or old is None or args.expected_record != old_oid:
            fail("route-completion CAS expected record is stale", decision="REQUIRED")
        lifecycle = old.get("lifecycle")
        if old["decision"] != "REQUIRED" or not isinstance(lifecycle, dict):
            fail("only an exact REQUIRED lifecycle can complete", decision=old["decision"])
        mapped_child, _ = mapped_child_route(old)
        current, _, fingerprint = validate_route_currentness(repo, common, args, request, old)
        capsule = post_compaction_recovery_capsule(repo, request)
        packet_raw, packet = read_route_packet(
            args.packet,
            old["obligation_id"],
            old["route_transaction_id"],
            expected_target=mapped_child,
        )
        validate_source_event_binding(
            repo,
            common,
            args,
            current,
            request,
            packet["source_event"],
            old["obligation_id"],
            old["route_transaction_id"],
        )
        return_raw, _ = read_child_return(
            args.return_path,
            old["obligation_id"],
            old["route_transaction_id"],
            lifecycle["delivery"]["packet"]["digest"],
            expected_child=mapped_child,
            expected_capsule=capsule,
        )
        returned_value = decoded_artifact(return_raw, "child return")
        raw_execution = returned_value["payload"].get("holon_execution_evidence")
        resolved_execution = None
        if raw_execution is not None:
            resolved_execution = resolve_execution_evidence(
                Path(args.store),
                raw_execution,
                args.host_id,
                args.host_session_id,
                args.binding_generation,
                mapped_child,
                old["route_transaction_id"],
                old["obligation_id"],
                lifecycle["delivery"]["packet"]["digest"],
            )
        if lifecycle.get("execution_evidence") != resolved_execution:
            fail("governor completion did not resolve the same host execution receipts", decision="REQUIRED")
        decision_raw, _ = read_governor_decision(
            args.decision,
            old["obligation_id"],
            old["route_transaction_id"],
            bytes_identity(return_raw)["digest"],
        )
        child_raw, child_path = child_delivery_bytes(mapped_child, expected_identity_inputs=old["package"]["source_digests"])
        live_delivery = {
            "child": {"identity": str(child_path), **bytes_identity(child_raw)},
            "packet": bytes_identity(packet_raw),
        }
        live_return = bytes_identity(return_raw)
        live_decision = bytes_identity(decision_raw)
        if lifecycle.get("state") == "SATISFIED":
            if (
                lifecycle.get("delivery") != live_delivery
                or lifecycle.get("child_return") != live_return
                or lifecycle.get("governor_decision") != live_decision
                or lifecycle.get("governor_decision_count") != 1
            ):
                fail("terminal route completion does not match the exact prior governor decision", decision="REQUIRED")
            post_route_currentness(repo, common, args, request, current, fingerprint, old_oid)
            try:
                release_transaction_admission(
                    Path(common),
                    args.controller,
                    old["route_transaction_id"],
                    mapped_child,
                    terminal=True,
                )
            except RouteUnavailable as exc:
                fail(str(exc), decision="REQUIRED")
            emit(completion_payload(old_oid, old, idempotent=True))
            return
        if lifecycle.get("state") != "RETURNED" or lifecycle.get("child_return") != live_return:
            fail("governor completion did not receive the same canonical live return", decision="REQUIRED")
        if lifecycle.get("delivery") != live_delivery:
            fail("governor completion did not receive the original full child and packet bytes", decision="REQUIRED")
        source_event = source_event_record(packet["source_event"])
        source_status = "satisfied" if source_event["kind"] == "one-shot-action" else "active"
        next_lifecycle = {
            **lifecycle,
            "state": "SATISFIED",
            "governor_decision": live_decision,
            "governor_decision_count": 1,
            "source_event_status": source_status,
        }
        record_base = {
            **{key: value for key, value in old.items() if key != "record_identity"},
            "predecessor_record_oid": old_oid,
            "route_state": "SATISFIED",
            "lifecycle": next_lifecycle,
        }
        new_oid, record = cas_route_record(
            repo,
            args.controller,
            old_oid,
            record_base,
            "route-completion",
            route_transaction_id=args.route_transaction_id,
        )
        try:
            post_route_currentness(repo, common, args, request, current, fingerprint, new_oid)
            packet_after, _ = read_route_packet(
                args.packet,
                old["obligation_id"],
                old["route_transaction_id"],
                expected_target=mapped_child,
            )
            return_after, _ = read_child_return(
                args.return_path,
                old["obligation_id"],
                old["route_transaction_id"],
                lifecycle["delivery"]["packet"]["digest"],
                expected_child=mapped_child,
                expected_capsule=capsule,
            )
            decision_after, _ = read_governor_decision(
                args.decision,
                old["obligation_id"],
                old["route_transaction_id"],
                bytes_identity(return_after)["digest"],
            )
            if (
                bytes_identity(packet_after) != lifecycle["delivery"]["packet"]
                or bytes_identity(return_after) != live_return
                or bytes_identity(decision_after) != live_decision
            ):
                fail("route completion bytes changed during post-return currentness reread", decision="REQUIRED")
        except SystemExit:
            target_ref = (
                transaction_route_ref_name(args.controller, args.route_transaction_id)
                if args.route_transaction_id is not None
                else ref_name(args.controller)
            )
            compensated = subprocess.run(
                [str(trusted_host_executable(repo, "git")), "update-ref", target_ref, old_oid, new_oid],
                cwd=repo,
                env=sanitized_action_environment(),
                capture_output=True,
                text=True,
                check=False,
            )
            if compensated.returncode or current_ref(
                repo, args.controller, route_transaction_id=args.route_transaction_id
            )[0] != old_oid:
                fail("route completion post-reread failed and exact compensation is unavailable", decision="REQUIRED")
            raise
        try:
            release_transaction_admission(
                Path(common),
                args.controller,
                old["route_transaction_id"],
                mapped_child,
                terminal=True,
            )
        except RouteUnavailable as exc:
            fail(str(exc), decision="REQUIRED")
    emit(completion_payload(new_oid, record, idempotent=False))


def zero_replay_effects() -> dict[str, int]:
    return {
        "instruction_rows": 0,
        "route_transactions": 0,
        "lifecycle_transitions": 0,
        "mutation_authorizations": 0,
        "task_dispatches": 0,
        "external_effects": 0,
    }


def instruction_replay_status(
    stored: dict[str, Any], incoming: dict[str, Any], *, target_terminal: bool
) -> dict[str, Any]:
    same_source = stored.get("source_identity") == incoming.get("source_identity")
    same_body = stored.get("body") == incoming.get("body")
    same_semantics = all(
        stored.get(key) == incoming.get(key) for key in ("body", "kind", "reactivation", "provenance")
    )
    if same_source and not same_semantics:
        return {
            "status": "ambiguous",
            "source_event_relation": "SOURCE_IDENTITY_SEMANTICS_CONFLICT",
            "new_instruction_rows": 0,
        }
    if stored.get("kind") == "standing-constraint" and stored.get("status") == "active" and same_source:
        return {"status": "STANDING_APPLIES", "source_event_relation": "SAME_SOURCE", "new_instruction_rows": 0}
    if same_source:
        return {"status": "REPLAY_NO_OP", "source_event_relation": "SAME_SOURCE", "new_instruction_rows": 0}
    relation = "DISTINCT_SOURCE_SAME_BODY" if same_body else "DISTINCT_SOURCE_DISTINCT_BODY"
    reactivation = incoming.get("reactivation")
    expressly_reactivated = isinstance(reactivation, dict) and any(
        reactivation.get(key) is True for key in ("reopen", "target_changed", "invalidating_evidence")
    )
    if target_terminal and not expressly_reactivated:
        return {"status": "TERMINAL_NO_OP", "source_event_relation": relation, "new_instruction_rows": 0}
    return {"status": "NEW_SOURCE_REVIEW_REQUIRED", "source_event_relation": relation, "new_instruction_rows": 0}


def ambiguous_replay_stop(message: str) -> NoReturn:
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "ambiguous",
            "stop": True,
            "decision": "REQUIRED",
            "advance_allowed": False,
            "effects": zero_replay_effects(),
            "error": message,
        }
    )
    raise SystemExit(2)


def command_replay(args: argparse.Namespace) -> None:
    repo, _, common = repo_context()
    request = read_request(args.request)
    with namespace_gate(common):
        oid, record = current_ref(repo, args.controller)
        if oid is None or record is None or args.expected_record != oid:
            ambiguous_replay_stop("replay target identity is missing or stale")
        lifecycle = record.get("lifecycle")
        if record.get("decision") != "REQUIRED" or not isinstance(lifecycle, dict) or lifecycle.get("state") != "SATISFIED":
            ambiguous_replay_stop("replay target is not an exact terminal route")
        current, _, fingerprint = validate_route_currentness(repo, common, args, request, record)
        mapped_child, _ = mapped_child_route(record)
        try:
            packet_raw = base64.b64decode(lifecycle["delivery"]["packet"]["bytes_b64"], validate=True)
            packet = route_packet_record(
                decoded_artifact(packet_raw, "stored route packet"),
                record["obligation_id"],
                record["route_transaction_id"],
                "stored route packet",
                expected_target=mapped_child,
            )
            stored_event = source_event_record(packet["source_event"], "stored source_event")
        except (KeyError, TypeError, ValueError, UnicodeError, json.JSONDecodeError, SystemExit):
            ambiguous_replay_stop("stored source provenance is ambiguous")
        validate_source_event_binding(
            repo,
            common,
            args,
            current,
            request,
            stored_event,
            record["obligation_id"],
            record["route_transaction_id"],
            replay=True,
        )
        incoming_event = read_replay_source_event(args.event)
        validate_source_event_binding(
            repo,
            common,
            args,
            current,
            request,
            incoming_event,
            record["obligation_id"],
            record["route_transaction_id"],
            replay=True,
        )
        stored = {**stored_event, "status": lifecycle["source_event_status"]}
        replay = instruction_replay_status(stored, incoming_event, target_terminal=True)
        if replay["status"] == "ambiguous":
            ambiguous_replay_stop("one source identity was reconstructed with conflicting semantic bytes")
        post_route_currentness(repo, common, args, request, current, fingerprint, oid)
        review_required = replay["status"] == "NEW_SOURCE_REVIEW_REQUIRED"
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": replay["status"],
            "decision": "REQUIRED",
            "route_state": "SATISFIED",
            "target_state": "SATISFIED",
            "advance_allowed": not review_required,
            "record_oid": oid,
            "record_identity": record["record_identity"],
            "source_identity": incoming_event["source_identity"],
            "source_event_relation": replay["source_event_relation"],
            "effects": zero_replay_effects(),
            "history_read_performed": False,
        }
    )
    if review_required:
        raise SystemExit(3)


def validate_current_result(
    repo: Path,
    common: str,
    args: argparse.Namespace,
    request: dict[str, Any],
    *,
    expected_oid: str | None = None,
    expected_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    history_query = normalized_history_query(request)
    oid, record = current_ref(repo, args.controller)
    if oid is None or record is None:
        fail("canonical route decision is absent")
    validate_canonical_route_record_bytes(repo, oid, record)
    if expected_oid is not None and oid != expected_oid:
        fail("route decision changed after request-free candidate derivation", decision=record["decision"])
    if expected_record is not None and record != expected_record:
        fail("route record changed after request-free candidate derivation", decision=record["decision"])
    current = current_controller(repo, args.controller)
    bound_context = {
        "controller_id": args.controller,
        "claim_id": current["claim_id"],
        "explicit_run_root": current["explicit_run_root"],
        "continuity_generation": current["continuity_generation"],
        "continuity_receipt": current["continuity_receipt"],
        "host_id": args.host_id,
        "host_session_id": args.host_session_id,
        "host_binding_generation": args.binding_generation,
    }
    for key, value in bound_context.items():
        if record.get(key) != value:
            fail(f"route decision expired because bound {key} changed", decision=record["decision"])
    decision, classification, invalidators, evidence, fingerprint, transaction_id, obligation_id = evaluate(
        repo, common, args, current, request
    )
    if record.get("expiry_fingerprint") != fingerprint:
        fail("route decision expired because its bound scope or evidence changed", decision=record["decision"])
    if record.get("history_query") != history_query:
        fail("route decision history-query request changed", decision=record["decision"])
    if (decision, classification, invalidators, transaction_id, obligation_id) != (
        record.get("decision"),
        record.get("classification"),
        record.get("invalidators"),
        record.get("route_transaction_id"),
        record.get("obligation_id"),
    ):
        fail("route decision no longer agrees with the current predicate", decision=record["decision"])
    lifecycle = record.get("lifecycle")
    if record["decision"] == "REQUIRED" and isinstance(lifecycle, dict):
        mapped_child, _ = mapped_child_route(record)
        packet_raw = validate_bytes_identity(lifecycle["delivery"]["packet"], "lifecycle.delivery.packet")
        packet = route_packet_record(
            decoded_artifact(packet_raw, "lifecycle route packet"),
            record["obligation_id"],
            record["route_transaction_id"],
            "lifecycle route packet",
            expected_target=mapped_child,
        )
        validate_source_event_binding(
            repo,
            common,
            args,
            current,
            request,
            packet["source_event"],
            record["obligation_id"],
            record["route_transaction_id"],
        )
    final_oid, _ = current_ref(repo, args.controller)
    final_current = current_controller(repo, args.controller)
    final_eval = evaluate(repo, common, args, final_current, request)
    if final_oid != oid or final_current != current or final_eval[4] != fingerprint:
        fail("route decision changed during the currentness check", decision=record["decision"])
    return {
        "oid": oid,
        "record": record,
        "current": current,
        "history_query": history_query,
        "obligation_id": obligation_id,
        "route_transaction_id": transaction_id if obligation_id is not None else None,
        "current_not_required": record["decision"] == "NOT_REQUIRED",
        "current_satisfied": record["decision"] == "REQUIRED" and record.get("route_state") == "SATISFIED",
    }


def current_result_payload(
    validated: dict[str, Any], *, mirror_claim: str
) -> dict[str, Any]:
    oid = validated["oid"]
    record = validated["record"]
    current = validated["current"]
    selected_child = mapped_child_route(record)[0] if record["decision"] == "REQUIRED" else None
    return {
        "schema": RESULT_SCHEMA,
        "status": "CURRENT",
        "decision": record["decision"],
        "classification": record["classification"],
        "advance_allowed": validated["current_satisfied"],
        "admission_required": validated["current_not_required"],
        "enforcement_available": True,
        "record_oid": oid,
        "record_identity": record["record_identity"],
        "obligation_id": validated["obligation_id"],
        "route_transaction_id": validated["route_transaction_id"],
        "route_state": record.get("route_state"),
        "selected_child": selected_child,
        "governor_decision_count": record.get("lifecycle", {}).get("governor_decision_count", 0),
        "history_query": validated["history_query"],
        "history_read_performed": False,
        "mirror_claim": mirror_claim,
        "mirror_status": mirror_observation(record["decision"], record.get("route_state"), mirror_claim),
        "projection_status": projection_status(current["explicit_run_root"], record["decision"], oid),
        "proof_layers": {
            "source_core": "PRESENT",
            "package": "UNVERIFIED",
            "install": "UNVERIFIED",
            "host_activation": "UNVERIFIED",
        },
        "host_activation_proven": False,
        **({"presentation": record["presentation"]} if "presentation" in record else {}),
    }


def emit_current_result(validated: dict[str, Any], *, mirror_claim: str) -> None:
    emit(current_result_payload(validated, mirror_claim=mirror_claim))
    if not (validated["current_not_required"] or validated["current_satisfied"]):
        raise SystemExit(3)


def exact_generation_successor(predecessor: Any, successor: Any) -> bool:
    return bool(
        isinstance(predecessor, str)
        and isinstance(successor, str)
        and CONTINUITY_RE.fullmatch(predecessor)
        and CONTINUITY_RE.fullmatch(successor)
        and int(successor[1:], 16) == int(predecessor[1:], 16) + 1
    )


def continuity_receipt_ref(controller: str, generation: str) -> str:
    return f"refs/implementaudit/continuity-receipts/{controller}/{generation}"


def canonical_ref_oid(repo: Path, ref: str, label: str) -> str:
    """Resolve one exact ref without allowing decode failures to escape as tracebacks."""
    completed = subprocess.run(
        [str(trusted_host_executable(repo, "git")), "rev-parse", "--verify", ref],
        cwd=repo,
        env=sanitized_action_environment(),
        capture_output=True,
        check=False,
    )
    try:
        oid = completed.stdout.rstrip(b"\n").decode("ascii", "strict")
    except UnicodeDecodeError:
        fail(f"{label} ref has non-ASCII output", decision="REQUIRED")
    if completed.returncode or not OID_RE.fullmatch(oid):
        fail(f"{label} ref is missing or unreadable", decision="REQUIRED")
    return oid


def split_continuity_token(
    token: Any, controller: str, generation: str, label: str
) -> tuple[str, str]:
    expected_ref = continuity_receipt_ref(controller, generation)
    if not isinstance(token, str) or token.count("@") != 1:
        fail(f"{label} token is malformed", decision="REQUIRED")
    ref, oid = token.split("@")
    if ref != expected_ref or not OID_RE.fullmatch(oid):
        fail(f"{label} token is foreign or noncanonical", decision="REQUIRED")
    return ref, oid


def validated_v3_predecessor(
    repo: Path,
    token: str,
    *,
    controller: str,
    claim: str,
    run_identity: str,
    generation: str,
) -> str:
    """Validate one canonical immutable v3 receipt and return its exact predecessor token."""
    ref, oid = split_continuity_token(token, controller, generation, "continuity receipt")
    if canonical_ref_oid(repo, ref, "continuity receipt") != oid:
        fail("continuity receipt token does not match its canonical ref", decision="REQUIRED")
    raw = git_blob_bytes(repo, oid, "continuity receipt")
    if (
        not raw.endswith(b"\n")
        or b"\n" in raw[:-1]
        or b"\r" in raw
        or any((value < 0x20 and value not in (0x09, 0x0A)) or value == 0x7F for value in raw)
    ):
        fail("continuity receipt bytes are not canonical", decision="REQUIRED")
    fields_raw = raw[:-1].split(b"\t")
    if len(fields_raw) != 18 or any(field == b"" for field in fields_raw):
        fail("continuity receipt has a malformed field layout", decision="REQUIRED")
    try:
        fields = [field.decode("utf-8", "strict") for field in fields_raw]
    except UnicodeDecodeError:
        fail("continuity receipt is not strict UTF-8", decision="REQUIRED")
    (
        schema,
        receipt_controller,
        receipt_claim,
        receipt_run,
        receipt_generation,
        invalidation_oid,
        pointer_ref,
        pointer_oid,
        pointer_digest,
        state_digest,
        roadmap_digest,
        graph_path,
        graph_digest,
        manifest_oid,
        manifest_digest,
        high_water,
        next_action,
        predecessor,
    ) = fields
    if schema != "implementaudit.continuity-receipt.v3":
        fail("successor continuity receipt is not v3", decision="REQUIRED")
    if (receipt_controller, receipt_claim, receipt_run, receipt_generation) != (
        controller,
        claim,
        run_identity,
        generation,
    ):
        fail("successor continuity receipt changed controller, claim, run, or generation", decision="REQUIRED")
    if pointer_ref != f"refs/implementaudit/current-generations/{controller}":
        fail("successor continuity receipt has a foreign generation pointer ref", decision="REQUIRED")
    if not all(OID_RE.fullmatch(value) for value in (invalidation_oid, pointer_oid, manifest_oid)):
        fail("successor continuity receipt has a malformed object identity", decision="REQUIRED")
    if not all(
        re.fullmatch(r"[0-9a-f]{64}", value)
        for value in (
            pointer_digest,
            state_digest,
            roadmap_digest,
            graph_digest,
            manifest_digest,
        )
    ):
        fail("successor continuity receipt has a malformed digest", decision="REQUIRED")
    if graph_path != "WORK_GRAPH.json" or not re.fullmatch(r"[0-9]{20}", high_water):
        fail("successor continuity receipt has malformed graph or high-water metadata", decision="REQUIRED")
    if not next_action:
        fail("successor continuity receipt has no next action", decision="REQUIRED")
    predecessor_generation = f"G{int(generation[1:], 16) - 1:04X}"
    split_continuity_token(predecessor, controller, predecessor_generation, "continuity predecessor")
    return predecessor


def validate_terminal_continuity_chain(
    repo: Path,
    *,
    controller: str,
    claim: str,
    run_identity: str,
    terminal_generation: Any,
    terminal_receipt: Any,
    current_generation: Any,
    current_receipt: Any,
    require_current_v3: bool = False,
) -> list[tuple[str, str]]:
    """Require a bounded contiguous canonical v3 chain back to the terminal receipt."""
    if (
        not isinstance(terminal_generation, str)
        or not isinstance(current_generation, str)
        or not CONTINUITY_RE.fullmatch(terminal_generation)
        or not CONTINUITY_RE.fullmatch(current_generation)
    ):
        fail("terminal route re-entry has a malformed continuity generation", decision="REQUIRED")
    terminal_ordinal = int(terminal_generation[1:], 16)
    current_ordinal = int(current_generation[1:], 16)
    distance = current_ordinal - terminal_ordinal
    if distance <= 0:
        fail("terminal route re-entry requires a strictly later continuity generation", decision="REQUIRED")
    if distance > 64:
        fail("terminal route re-entry continuity traversal exceeds its bound", decision="REQUIRED")
    terminal_ref, terminal_oid = split_continuity_token(
        terminal_receipt, controller, terminal_generation, "terminal continuity receipt"
    )
    candidate_generation = current_generation
    candidate_receipt = current_receipt
    reverse_links = [(candidate_generation, candidate_receipt)]
    if distance == 1 and not require_current_v3:
        current_ref, current_oid = split_continuity_token(
            current_receipt, controller, current_generation, "current continuity receipt"
        )
        if current_receipt == terminal_receipt:
            fail("terminal route re-entry requires a distinct continuity receipt", decision="REQUIRED")
        if canonical_ref_oid(repo, current_ref, "current continuity receipt") != current_oid:
            fail("current continuity receipt token does not match its canonical ref", decision="REQUIRED")
        git_blob_bytes(repo, current_oid, "current continuity receipt")
        reverse_links.append((terminal_generation, terminal_receipt))
    else:
        for _ in range(distance):
            candidate_receipt = validated_v3_predecessor(
                repo,
                candidate_receipt,
                controller=controller,
                claim=claim,
                run_identity=run_identity,
                generation=candidate_generation,
            )
            candidate_generation = f"G{int(candidate_generation[1:], 16) - 1:04X}"
            reverse_links.append((candidate_generation, candidate_receipt))
        if candidate_generation != terminal_generation or candidate_receipt != terminal_receipt:
            fail("continuity receipt chain does not reach the terminal route receipt", decision="REQUIRED")
    if canonical_ref_oid(repo, terminal_ref, "terminal continuity receipt") != terminal_oid:
        fail("terminal continuity receipt token does not match its canonical ref", decision="REQUIRED")
    git_blob_bytes(repo, terminal_oid, "terminal continuity receipt")
    return list(reversed(reverse_links))


def is_exact_preserved_unopenable_required_record(record_oid: str, record: dict[str, Any]) -> bool:
    """Recognize only explicitly allowlisted immutable lifecycle-free route objects."""
    descriptor = PRESERVED_UNOPENABLE_REQUIRED_RECORDS.get(record_oid)
    no_child_identity = "R0033:UNMAPPED_REQUIRED:NO_CHILD"
    return bool(
        descriptor is not None
        and record.get("record_identity") == descriptor["record_identity"]
        and record.get("decision") == "REQUIRED"
        and record.get("route_state") == "UNSATISFIED"
        and record.get("child_lifecycle_owned") is False
        and "lifecycle" not in record
        and record.get("classification") == "JUDGEMENT_REQUIRED"
        and record.get("invalidators") == ["route judgement cannot mint NOT_REQUIRED"]
        and record.get("action") == descriptor["action"]
        and record.get("package") == descriptor["package"]
        and record.get("child_source") == {
            "identity": no_child_identity,
            "digest": digest_json({"identity": no_child_identity}),
        }
    )


def validate_stale_unsatisfied_custody(
    repo: Path,
    common: str,
    record_oid: str,
    record: dict[str, Any],
    retained_request: dict[str, Any],
) -> None:
    """Authenticate one lifecycle-free required record from retained exact semantics."""
    preserved_unopenable = is_exact_preserved_unopenable_required_record(record_oid, record)
    predecessor_oid = record.get("predecessor_record_oid")
    if predecessor_oid is not None:
        if not isinstance(predecessor_oid, str) or not OID_RE.fullmatch(predecessor_oid):
            fail("stale unsatisfied route predecessor identity is malformed", decision="REQUIRED")
        predecessor = decoded_artifact(
            git_blob_bytes(repo, predecessor_oid, "stale unsatisfied route predecessor"),
            "stale unsatisfied route predecessor",
        )
        validate_route_record_semantics(
            repo,
            record["controller_id"],
            predecessor_oid,
            predecessor,
            allow_immutable_terminal_child=True,
            allow_immutable_active_child=True,
            predecessor_seen=frozenset({record_oid}),
            predecessor_depth=1,
        )
        lifecycle_present = "lifecycle" in predecessor
        lifecycle = predecessor.get("lifecycle")

        same_context = all(
            predecessor.get(key) == record.get(key)
            for key in (
                "claim_id",
                "explicit_run_root",
                "continuity_generation",
                "continuity_receipt",
                "host_binding_generation",
            )
        )
        if predecessor["decision"] != "REQUIRED":
            if predecessor.get("decision") == "PENDING" and predecessor.get("invalidators") == [
                "action-in-progress"
            ]:
                fail("stale unsatisfied route predecessor has unknown action completion", decision="REQUIRED")
            if same_context and predecessor.get("expiry_fingerprint") == record.get("expiry_fingerprint"):
                fail("stale unsatisfied route predecessor is an idempotent predicate alias", decision="REQUIRED")
        else:
            unchanged_owner = (
                "controller_id",
                "claim_id",
                "explicit_run_root",
                "host_id",
            )
            if any(predecessor.get(key) != record.get(key) for key in unchanged_owner):
                fail("stale unsatisfied route predecessor changed route ownership", decision="REQUIRED")
            if (
                predecessor.get("obligation_id") == record.get("obligation_id")
                or predecessor.get("route_transaction_id") == record.get("route_transaction_id")
            ):
                fail("stale unsatisfied route predecessor did not yield a fresh obligation", decision="REQUIRED")
            predecessor_boundary = predecessor.get("boundary")
            record_boundary = record.get("boundary")
            if (
                not isinstance(predecessor_boundary, dict)
                or not isinstance(record_boundary, dict)
                or predecessor_boundary.get("event_id") == record_boundary.get("event_id")
                or predecessor_boundary.get("digest") == record_boundary.get("digest")
            ):
                fail("stale unsatisfied route predecessor did not cross a distinct boundary", decision="REQUIRED")
            predecessor_state = predecessor.get("route_state")
            continuity_links = validate_terminal_continuity_chain(
                repo,
                controller=record["controller_id"],
                claim=record["claim_id"],
                run_identity=Path(record["explicit_run_root"]).name,
                terminal_generation=predecessor.get("continuity_generation"),
                terminal_receipt=predecessor.get("continuity_receipt"),
                current_generation=record.get("continuity_generation"),
                current_receipt=record.get("continuity_receipt"),
                require_current_v3=predecessor_state in {"UNSATISFIED", "OPEN", "RETURNED"},
            )
            predecessor_binding = predecessor.get("host_binding_generation")
            record_binding = record.get("host_binding_generation")
            if (
                not isinstance(predecessor_binding, str)
                or not isinstance(record_binding, str)
                or not CONTINUITY_RE.fullmatch(predecessor_binding)
                or not CONTINUITY_RE.fullmatch(record_binding)
            ):
                fail("stale unsatisfied route predecessor has malformed binding context", decision="REQUIRED")
            binding_distance = int(record_binding[1:], 16) - int(predecessor_binding[1:], 16)
            if predecessor_state in {"UNSATISFIED", "OPEN", "RETURNED"}:
                if (
                    predecessor.get("host_session_id") != record.get("host_session_id")
                    or
                    mechanical_required_reason(record["action"]["argv"])
                    != "STALE_CONTEXT_RECONSTRUCTION"
                    or mapped_child_route(record)[0] != "audit-state"
                    or binding_distance != len(continuity_links) - 1
                ):
                    fail("stale unsatisfied route predecessor is not an exact active recovery", decision="REQUIRED")
            elif predecessor_state == "SATISFIED":
                predecessor_lifecycle = predecessor.get("lifecycle")
                if (
                    not isinstance(predecessor_lifecycle, dict)
                    or predecessor_lifecycle.get("state") != "SATISFIED"
                    or predecessor_lifecycle.get("source_event_status") != "satisfied"
                ):
                    fail("stale unsatisfied route predecessor is not an exact terminal re-entry", decision="REQUIRED")
                validate_terminal_owner_transition(predecessor, record)
            else:
                fail("stale unsatisfied route predecessor has no allowed direct transition", decision="REQUIRED")

    package = exact_keys(
        record.get("package"),
        {"head", "tree", "source_digests", "action_executable"},
        "stale unsatisfied route package",
    )
    if package["head"] != git(repo, "rev-parse", "HEAD") or package["tree"] != git(
        repo, "rev-parse", "HEAD^{tree}"
    ):
        fail("stale unsatisfied route package has foreign repository identity", decision="REQUIRED")
    source_digest_keys = {
        "SKILL.md", "route-obligations.md", "route-transaction.py", "claim-run.sh"
    }
    if not preserved_unopenable:
        source_digest_keys.add("resolve-internal-skill.py")
    source_digests = exact_keys(
        package["source_digests"],
        source_digest_keys,
        "stale unsatisfied route package source digests",
    )
    if any(not isinstance(value, str) or not HEX_RE.fullmatch(value) for value in source_digests.values()):
        fail("stale unsatisfied route package source digest is malformed", decision="REQUIRED")
    expected_executable = {
        "requested": "route-trigger",
        "resolved": "R0033:unadmitted" if preserved_unopenable else "R0033:built-in",
        "digest": digest_json(retained_request["action"]["argv"]),
    }
    if package["action_executable"] != expected_executable:
        fail("stale unsatisfied route package action identity is foreign", decision="REQUIRED")

    child_source = identity_record(record.get("child_source"), "stale unsatisfied route child source")
    if preserved_unopenable:
        legacy_identity = "R0033:UNMAPPED_REQUIRED:NO_CHILD"
        if child_source != {
            "identity": legacy_identity,
            "digest": digest_json({"identity": legacy_identity}),
        }:
            fail("legacy unopenable route lost its exact no-child custody", decision="REQUIRED")
    else:
        mapped_child, _ = mapped_child_route(record)
        historical_child = Path(child_source["identity"])
        current_child_raw, _ = child_delivery_bytes(mapped_child)
        if (
            not historical_child.is_absolute()
            or historical_child.name != "SKILL.md"
            or historical_child.parent.name != mapped_child
            or child_source["digest"] != bytes_identity(current_child_raw)["digest"]
        ):
            fail("stale unsatisfied route child source has no exact historical custody", decision="REQUIRED")

    evidence = exact_keys(
        record.get("evidence"),
        {"owner", "authority", "effect", "dependency"},
        "stale unsatisfied route evidence",
    )
    owner = exact_keys(
        evidence["owner"], {"controller_record_oid", "claim_id", "run_root"}, "stale route owner evidence"
    )
    authority = exact_keys(
        evidence["authority"], {"continuity_generation", "continuity_receipt"}, "stale route authority evidence"
    )
    dependency = exact_keys(
        evidence["dependency"], {"host_binding_generation", "host_correlation_id"}, "stale route dependency evidence"
    )
    expected_evidence = {
        "owner": {
            "controller_record_oid": owner["controller_record_oid"],
            "claim_id": record.get("claim_id"),
            "run_root": record.get("explicit_run_root"),
        },
        "authority": {
            "continuity_generation": record.get("continuity_generation"),
            "continuity_receipt": record.get("continuity_receipt"),
        },
        "effect": {
            "action_identity": retained_request["action"]["identity"],
            "action_digest": retained_request["action"]["digest"],
            "derived_class": mechanical_action_class(retained_request["action"]["argv"]),
        },
        "dependency": {
            "host_binding_generation": record.get("host_binding_generation"),
            "host_correlation_id": record.get("host_correlation_id"),
        },
    }
    if (
        not isinstance(owner["controller_record_oid"], str)
        or not OID_RE.fullmatch(owner["controller_record_oid"])
        or evidence != expected_evidence
        or authority != expected_evidence["authority"]
        or dependency != expected_evidence["dependency"]
    ):
        fail("stale unsatisfied route retained evidence is foreign", decision="REQUIRED")

    if any(item.get("status") != "CURRENT" for item in record["inputs"]):
        fail("stale unsatisfied route did not retain a current input set", decision="REQUIRED")
    identity_seed = {
        "request": retained_request,
        "controller_record_oid": owner["controller_record_oid"],
        "claim_id": record["claim_id"],
        "continuity_receipt": record["continuity_receipt"],
        "host_binding_generation": record["host_binding_generation"],
        "package": package,
        "child_source": child_source,
    }
    expected_transaction = digest_json({"kind": "transaction", "seed": identity_seed})
    expected_obligation = digest_json({"kind": "obligation", "seed": identity_seed})
    mechanical_evidence = {
        **expected_evidence,
        "inputs": record["inputs"],
        "package": package,
        "child_source": child_source,
    }
    expected_fingerprint = digest_json({"request": retained_request, "mechanical_evidence": mechanical_evidence})
    reason = mechanical_required_reason(retained_request["action"]["argv"])
    expected_classification = "JUDGEMENT_REQUIRED" if preserved_unopenable else "MECHANICALLY_REQUIRED"
    expected_invalidators = (
        ["route judgement cannot mint NOT_REQUIRED"] if preserved_unopenable else [reason]
    )
    if (
        record.get("route_transaction_id") != expected_transaction
        or record.get("obligation_id") != expected_obligation
        or record.get("expiry_fingerprint") != expected_fingerprint
        or record.get("decision") != "REQUIRED"
        or record.get("classification") != expected_classification
        or record.get("invalidators") != expected_invalidators
        or (not preserved_unopenable and reason not in CHILD_ROUTE_MAP)
        or record.get("consumed_record_oid") is not None
        or record.get("history_query") is not None
    ):
        fail("stale unsatisfied route no longer matches its retained predicate", decision="REQUIRED")

    correlation = {
        "host_id": record["host_id"],
        "host_session_id": record["host_session_id"],
        "binding_generation": record["host_binding_generation"],
        "controller_id": record["controller_id"],
        "claim_id": record["claim_id"],
        "explicit_run_root": record["explicit_run_root"],
        "repository_identity": str(repo),
        "git_common_directory_identity": common,
        "worktree_identity": str(repo),
        "applicable_continuity_generation": record["continuity_generation"],
        "applicable_continuity_receipt": record["continuity_receipt"],
        "event_id": retained_request["boundary"]["event_id"],
        "turn_id": None,
        "tool_use_id": None,
        "agent_id": None,
        "obligation_id": expected_obligation,
        "route_transaction_id": expected_transaction,
    }
    correlation_raw = json.dumps(correlation, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if record.get("host_correlation_id") != f"sha256:{hashlib.sha256(correlation_raw).hexdigest()}":
        fail("stale unsatisfied route lost its exact host-event custody", decision="REQUIRED")


def validate_terminal_owner_transition(
    predecessor: dict[str, Any],
    successor: dict[str, Any],
) -> None:
    """Validate one terminal route owner across same- or fresh-session custody."""
    unchanged_owner = (
        "controller_id",
        "claim_id",
        "explicit_run_root",
        "host_id",
    )
    if any(predecessor.get(key) != successor.get(key) for key in unchanged_owner):
        fail("terminal route re-entry changed controller, claim, run, or host identity", decision="REQUIRED")
    predecessor_session = exact_text(
        predecessor.get("host_session_id"), "terminal route predecessor host session"
    )
    successor_session = exact_text(
        successor.get("host_session_id"), "terminal route successor host session"
    )
    predecessor_binding = predecessor.get("host_binding_generation")
    successor_binding = successor.get("host_binding_generation")
    if (
        not isinstance(predecessor_binding, str)
        or not CONTINUITY_RE.fullmatch(predecessor_binding)
        or not isinstance(successor_binding, str)
        or not CONTINUITY_RE.fullmatch(successor_binding)
    ):
        fail("terminal route re-entry has malformed host-binding custody", decision="REQUIRED")
    if predecessor_session == successor_session:
        if int(successor_binding[1:], 16) <= int(predecessor_binding[1:], 16):
            fail("terminal route re-entry requires a strictly later same-session host binding", decision="REQUIRED")
    elif int(successor_binding[1:], 16) == 0:
        fail("terminal route re-entry requires an active fresh-session host binding", decision="REQUIRED")


def require_terminal_route_reentry(
    repo: Path,
    args: argparse.Namespace,
    current: dict[str, str],
    request: dict[str, Any],
    old_oid: str,
    old: dict[str, Any],
    decision: str,
    *,
    candidate_transaction_id: str | None = None,
    candidate_obligation_id: str | None = None,
) -> None:
    """Admit only a verified later-boundary successor to a terminal one-shot route."""
    validate_canonical_route_record_bytes(repo, old_oid, old)
    candidate_request_from_record(old, require_current_inputs=False)
    lifecycle = old.get("lifecycle")
    if (
        old.get("decision") != "REQUIRED"
        or old.get("route_state") != "SATISFIED"
        or not isinstance(lifecycle, dict)
        or lifecycle.get("state") != "SATISFIED"
        or lifecycle.get("source_event_status") != "satisfied"
    ):
        fail("only an exact terminal one-shot route lifecycle can yield to a fresh boundary", decision="REQUIRED")
    historical_child = validate_bytes_identity(
        lifecycle.get("delivery", {}).get("child"),
        "terminal route lifecycle child",
        with_identity=True,
    )
    mapped_child, _ = mapped_child_route(old)
    current_child, _ = child_delivery_bytes(mapped_child)
    if current_child != historical_child:
        # Historical delivery remains exact evidence, never current child credit.
        # Only a fresh REQUIRED lifecycle for the same canonical child can
        # succeed this source change; all ordinary currentness fences still run.
        candidate_reason = mechanical_required_reason(request["action"]["argv"])
        candidate_child = CHILD_ROUTE_MAP.get(candidate_reason, (None, None))[0]
        if (
            decision != "REQUIRED"
            or candidate_child != mapped_child
            or not isinstance(candidate_transaction_id, str)
            or not HEX_RE.fullmatch(candidate_transaction_id)
            or candidate_transaction_id == old.get("route_transaction_id")
            or not isinstance(candidate_obligation_id, str)
            or not HEX_RE.fullmatch(candidate_obligation_id)
            or candidate_obligation_id == old.get("obligation_id")
        ):
            fail("changed terminal child requires a fresh same-child REQUIRED obligation", decision="REQUIRED")
    successor_owner = {
        "controller_id": args.controller,
        "claim_id": current["claim_id"],
        "explicit_run_root": current["explicit_run_root"],
        "host_id": args.host_id,
        "host_session_id": args.host_session_id,
        "host_binding_generation": args.binding_generation,
    }
    validate_terminal_owner_transition(old, successor_owner)
    validate_terminal_continuity_chain(
        repo,
        controller=args.controller,
        claim=current["claim_id"],
        run_identity=Path(current["explicit_run_root"]).name,
        terminal_generation=old.get("continuity_generation"),
        terminal_receipt=old.get("continuity_receipt"),
        current_generation=current["continuity_generation"],
        current_receipt=current["continuity_receipt"],
    )
    old_boundary = old.get("boundary")
    new_boundary = request["boundary"]
    if (
        not isinstance(old_boundary, dict)
        or old_boundary.get("event_id") == new_boundary["event_id"]
        or old_boundary.get("digest") == new_boundary["digest"]
    ):
        fail("terminal route re-entry requires a distinct canonical boundary event and digest", decision="REQUIRED")
    noncurrent, _ = request_observations(repo, current, request)
    if noncurrent or decision not in {"NOT_REQUIRED", "REQUIRED"}:
        fail("terminal route re-entry predicate is incomplete or noncurrent", decision="REQUIRED")


def require_active_route_recovery(
    repo: Path,
    common: str,
    args: argparse.Namespace,
    current: dict[str, str],
    request: dict[str, Any],
    old_oid: str,
    old: dict[str, Any],
    decision: str,
    classification: str,
    obligation_id: str | None,
    transaction_id: str | None,
) -> None:
    """Admit one exact contiguous stale-context successor to an incomplete route."""
    validate_canonical_route_record_bytes(repo, old_oid, old)
    retained_request = candidate_request_from_record(old, require_current_inputs=False)
    lifecycle = old.get("lifecycle")
    route_state = old.get("route_state")
    unsatisfied = (
        route_state == "UNSATISFIED"
        and "lifecycle" not in old
        and lifecycle is None
        and old.get("child_lifecycle_owned") is False
    )
    active_lifecycle = (
        route_state in {"OPEN", "RETURNED"}
        and isinstance(lifecycle, dict)
        and lifecycle.get("state") == route_state
        and lifecycle.get("source_event_status") == "active"
    )
    if old.get("decision") != "REQUIRED" or not (unsatisfied or active_lifecycle):
        fail("only an exact incomplete REQUIRED route can enter stale-context recovery", decision="REQUIRED")
    unchanged_owner = {
        "controller_id": args.controller,
        "claim_id": current["claim_id"],
        "explicit_run_root": current["explicit_run_root"],
        "host_id": args.host_id,
        "host_session_id": args.host_session_id,
    }
    if any(old.get(key) != value for key, value in unchanged_owner.items()):
        fail("active route recovery changed controller, claim, run, host, or session identity", decision="REQUIRED")
    if unsatisfied:
        validate_stale_unsatisfied_custody(repo, common, old_oid, old, retained_request)
    continuity_links = validate_terminal_continuity_chain(
        repo,
        controller=args.controller,
        claim=current["claim_id"],
        run_identity=Path(current["explicit_run_root"]).name,
        terminal_generation=old.get("continuity_generation"),
        terminal_receipt=old.get("continuity_receipt"),
        current_generation=current["continuity_generation"],
        current_receipt=current["continuity_receipt"],
        require_current_v3=True,
    )
    old_binding = old.get("host_binding_generation")
    if (
        not isinstance(old_binding, str)
        or not CONTINUITY_RE.fullmatch(old_binding)
        or not CONTINUITY_RE.fullmatch(args.binding_generation)
        or int(args.binding_generation[1:], 16) - int(old_binding[1:], 16) != len(continuity_links) - 1
    ):
        fail("active route recovery requires an exact matching host-binding generation chain", decision="REQUIRED")
    binding_start = int(old_binding[1:], 16)
    expected_lineage = [
        (f"G{binding_start + index:04X}", continuity_generation, continuity_receipt)
        for index, (continuity_generation, continuity_receipt) in enumerate(continuity_links)
    ]
    validate_binding(
        repo,
        common,
        args,
        current,
        request,
        obligation_id,
        transaction_id,
        expected_lineage=expected_lineage,
    )
    old_boundary = old.get("boundary")
    new_boundary = request["boundary"]
    if (
        not isinstance(old_boundary, dict)
        or old_boundary.get("event_id") == new_boundary["event_id"]
        or old_boundary.get("digest") == new_boundary["digest"]
    ):
        fail("active route recovery requires a distinct canonical boundary event and digest", decision="REQUIRED")
    if mechanical_required_reason(request["action"]["argv"]) != "STALE_CONTEXT_RECONSTRUCTION":
        fail("active route recovery requires STALE_CONTEXT_RECONSTRUCTION", decision="REQUIRED")
    mapped_child, _ = CHILD_ROUTE_MAP["STALE_CONTEXT_RECONSTRUCTION"]
    if mapped_child != "audit-state":
        fail("active route recovery has no canonical audit-state mapping", decision="REQUIRED")
    noncurrent, _ = request_observations(repo, current, request)
    if noncurrent or decision != "REQUIRED" or classification != "MECHANICALLY_REQUIRED":
        fail("active route recovery predicate is incomplete or noncurrent", decision="REQUIRED")


def command_check(args: argparse.Namespace) -> None:
    repo, _, common = repo_context()
    request = read_request(args.request)
    with namespace_gate(common):
        validated = validate_current_result(repo, common, args, request)
    emit_current_result(validated, mirror_claim=args.mirror_claim)


def command_observe_current(args: argparse.Namespace) -> None:
    repo, _, common = repo_context()
    with namespace_gate(common):
        oid, record = current_ref(repo, args.controller)
        if oid is None or record is None:
            fail("canonical route decision is absent")
        validate_canonical_route_record_bytes(repo, oid, record)
        request = candidate_request_from_record(record, require_current_inputs=False)
        validated = validate_current_result(
            repo,
            common,
            args,
            request,
            expected_oid=oid,
            expected_record=record,
        )
    emit_current_result(validated, mirror_claim="ABSENT")


def command_admit_current(args: argparse.Namespace) -> None:
    """Request-free effect gate over one exact current route result."""
    repo, _, common = repo_context()
    with namespace_gate(common):
        oid, record = current_ref(repo, args.controller)
        if oid is None or record is None:
            fail("canonical route decision is absent")
        validate_canonical_route_record_bytes(repo, oid, record)
        request = candidate_request_from_record(record, require_current_inputs=False)
        validated = validate_current_result(
            repo,
            common,
            args,
            request,
            expected_oid=oid,
            expected_record=record,
        )
        payload = current_result_payload(validated, mirror_claim="ABSENT")
        if not (validated["current_not_required"] or validated["current_satisfied"]):
            emit(payload)
            raise SystemExit(3)
        if validated["current_not_required"]:
            print(no_child_notice(record.get("presentation")), file=sys.stderr)
    emit(payload)


def command_admit_transaction(args: argparse.Namespace) -> None:
    """Native transaction-keyed child admission used by OPEN and schedulers."""
    common = Path(args.common_directory).resolve()
    with namespace_gate(str(common)):
        try:
            admission = admit_transaction_child(
                common,
                args.controller,
                args.route_transaction_id,
                args.selected_child,
                sorted(set(args.writer_key)),
                sorted(set(args.dependency_key)),
            )
        except RouteUnavailable as exc:
            fail(str(exc), decision="REQUIRED")
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "TRANSACTION_CHILD_ADMITTED",
            "decision": "REQUIRED",
            "advance_allowed": False,
            "enforcement_available": True,
            "controller_id": args.controller,
            "route_transaction_id": args.route_transaction_id,
            "selected_child": args.selected_child,
            "writer_keys": admission["writer_keys"],
            "dependency_keys": admission["dependency_keys"],
        }
    )


def command_decide_transaction(args: argparse.Namespace) -> None:
    if getattr(args, "recovery_capsule", None) is not None:
        return command_recovery_transaction_v1(args, "decide-transaction")
    """Create one canonical REQUIRED route under transaction-keyed custody."""
    repo, _, common = repo_context()
    request = read_request(args.request)
    history_query = normalized_history_query(request)
    with namespace_gate(common):
        current = current_controller(repo, args.controller)
        decision, classification, invalidators, evidence, fingerprint, transaction_id, obligation_id = evaluate(
            repo, common, args, current, request
        )
        if decision != "REQUIRED" or obligation_id is None:
            fail("transaction-keyed decide requires one exact REQUIRED obligation", decision=decision)
        old_oid, old = current_ref(
            repo,
            args.controller,
            allow_immutable_terminal_child=True,
            allow_immutable_active_child=True,
            route_transaction_id=transaction_id,
        )
        expected = args.expected_record
        if expected == "none":
            if old_oid is not None:
                fail("transaction-keyed decide expected absence but the route exists", decision="REQUIRED")
            expected_oid = ZERO_OID
        elif not OID_RE.fullmatch(expected) or expected != old_oid:
            fail("transaction-keyed decide CAS expected record is stale", decision="REQUIRED")
        else:
            expected_oid = expected
        if old is not None:
            if old.get("expiry_fingerprint") == fingerprint and old.get("route_transaction_id") == transaction_id:
                emit(
                    {
                        "schema": RESULT_SCHEMA,
                        "status": "DECIDED",
                        "decision": "REQUIRED",
                        "classification": old["classification"],
                        "advance_allowed": old.get("route_state") == "SATISFIED",
                        "enforcement_available": True,
                        "record_oid": old_oid,
                        "record_identity": old["record_identity"],
                        "obligation_id": old["obligation_id"],
                        "route_transaction_id": transaction_id,
                        "route_state": old["route_state"],
                        "transaction_custody": transaction_route_ref_name(args.controller, transaction_id),
                        "idempotent": True,
                    }
                )
                return
            fail("transaction-keyed route identity already owns a different predicate", decision="REQUIRED")
        record_base: dict[str, Any] = {
            "schema": RECORD_SCHEMA,
            "predicate_version": PREDICATE_VERSION,
            "controller_id": args.controller,
            "claim_id": current["claim_id"],
            "explicit_run_root": current["explicit_run_root"],
            "continuity_generation": current["continuity_generation"],
            "continuity_receipt": current["continuity_receipt"],
            "host_id": args.host_id,
            "host_session_id": args.host_session_id,
            "host_binding_generation": args.binding_generation,
            "host_correlation_id": evidence["dependency"]["host_correlation_id"],
            "boundary": request["boundary"],
            "scope": request["scope"],
            "action": request["action"],
            "evidence": {key: evidence[key] for key in ("owner", "authority", "effect", "dependency")},
            "inputs": evidence["inputs"],
            "package": evidence["package"],
            "child_source": evidence["child_source"],
            "decision": decision,
            "classification": classification,
            "invalidators": invalidators,
            "expiry_fingerprint": fingerprint,
            "expires_on": EXPIRES_ON,
            "predecessor_record_oid": None,
            "route_transaction_id": transaction_id,
            "obligation_id": obligation_id,
            "route_state": "UNSATISFIED",
            "child_lifecycle_owned": False,
            "consumed_record_oid": None,
        }
        if "presentation" in request:
            record_base["presentation"] = request["presentation"]
        if history_query is not None:
            record_base["history_query"] = history_query
        new_oid, record = cas_route_record(
            repo,
            args.controller,
            expected_oid,
            record_base,
            "transaction-keyed decide",
            route_transaction_id=transaction_id,
        )
        post_current = current_controller(repo, args.controller)
        post_eval = evaluate(repo, common, args, post_current, request)
        post_oid, _ = current_ref(repo, args.controller, route_transaction_id=transaction_id)
        if post_current != current or post_eval[4] != fingerprint or post_oid != new_oid:
            fail("transaction-keyed decision lost currentness", decision="REQUIRED")
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "DECIDED",
            "decision": "REQUIRED",
            "classification": classification,
            "advance_allowed": False,
            "enforcement_available": True,
            "record_oid": new_oid,
            "record_identity": record["record_identity"],
            "obligation_id": obligation_id,
            "route_transaction_id": transaction_id,
            "route_state": "UNSATISFIED",
            "transaction_custody": transaction_route_ref_name(args.controller, transaction_id),
            "history_query": history_query,
            "history_read_performed": False,
        }
    )


def command_decide(args: argparse.Namespace) -> None:
    repo, _, common = repo_context()
    request = read_request(args.request)
    history_query = normalized_history_query(request)
    with namespace_gate(common):
        current = current_controller(repo, args.controller)
        decision, classification, invalidators, evidence, fingerprint, transaction_id, obligation_id = evaluate(
            repo, common, args, current, request
        )
        if mechanical_required_reason(request["action"]["argv"]) == "NONTRIVIAL_ANDON_DIAGNOSIS":
            try:
                require_governor_dispatch_requester(args.requester_identity)
            except RouteUnavailable as exc:
                fail(str(exc), decision="REQUIRED")
        old_oid, old = current_ref(
            repo,
            args.controller,
            allow_immutable_terminal_child=True,
            allow_immutable_active_child=True,
        )
        expected = args.expected_record
        if expected == "none":
            if old_oid is not None:
                fail("route decision CAS expected absence but a current record exists", decision=old["decision"] if old else "PENDING")
            expected_oid = ZERO_OID
        elif not OID_RE.fullmatch(expected) or expected != old_oid:
            fail("route decision CAS expected record is stale", decision=old["decision"] if old else "PENDING")
        else:
            expected_oid = expected
        current_context_matches = bool(
            old
            and old.get("claim_id") == current["claim_id"]
            and old.get("explicit_run_root") == current["explicit_run_root"]
            and old.get("continuity_receipt") == current["continuity_receipt"]
            and old.get("host_binding_generation") == args.binding_generation
        )
        active_recovery = bool(
            old
            and old["decision"] == "REQUIRED"
            and old.get("route_state") in {"UNSATISFIED", "OPEN", "RETURNED"}
            and (old.get("route_state") != "UNSATISFIED" or not current_context_matches)
        )
        if active_recovery:
            require_active_route_recovery(
                repo,
                common,
                args,
                current,
                request,
                old_oid,
                old,
                decision,
                classification,
                obligation_id,
                transaction_id,
            )
        if old and current_context_matches and old.get("expiry_fingerprint") == fingerprint and old["decision"] == decision:
            satisfied = old.get("route_state") == "SATISFIED"
            emit(
                {
                    "schema": RESULT_SCHEMA,
                    "status": "DECIDED",
                    "decision": decision,
                    "classification": classification,
                    "advance_allowed": satisfied,
                    "admission_required": decision == "NOT_REQUIRED",
                    "enforcement_available": True,
                    "record_oid": old_oid,
                    "record_identity": old["record_identity"],
                    "obligation_id": old.get("obligation_id"),
                    "route_state": old.get("route_state"),
                    "history_query": history_query,
                    "history_read_performed": False,
                    "governor_decision_count": old.get("lifecycle", {}).get("governor_decision_count", 0),
                    "idempotent": True,
                }
            )
            return
        if (
            old
            and current_context_matches
            and old.get("decision") == "PENDING"
            and old.get("invalidators") in (["action-in-progress"], ["action-completion"])
            and old.get("expiry_fingerprint") == fingerprint
        ):
            fail("the exact action receipt was consumed or has unknown completion; it cannot be re-admitted")
        if old and old.get("decision") == "PENDING" and old.get("invalidators") == ["action-in-progress"]:
            fail("an action-in-progress record has unknown completion and cannot be replaced in H2A")
        if (
            old
            and old["decision"] == "REQUIRED"
            and old.get("route_state") == "UNSATISFIED"
            and not active_recovery
        ):
            fail("an active same-controller route obligation cannot be downgraded or replaced in H2A", decision="REQUIRED")
        terminal_reentry = bool(
            old and old["decision"] == "REQUIRED" and old.get("route_state") == "SATISFIED"
        )
        if terminal_reentry:
            require_terminal_route_reentry(
                repo, args, current, request, old_oid, old, decision,
                candidate_transaction_id=transaction_id,
                candidate_obligation_id=obligation_id,
            )
        record_base: dict[str, Any] = {
            "schema": RECORD_SCHEMA,
            "predicate_version": PREDICATE_VERSION,
            "controller_id": args.controller,
            "claim_id": current["claim_id"],
            "explicit_run_root": current["explicit_run_root"],
            "continuity_generation": current["continuity_generation"],
            "continuity_receipt": current["continuity_receipt"],
            "host_id": args.host_id,
            "host_session_id": args.host_session_id,
            "host_binding_generation": args.binding_generation,
            "host_correlation_id": evidence["dependency"]["host_correlation_id"],
            "boundary": request["boundary"],
            "scope": request["scope"],
            "action": request["action"],
            "evidence": {key: evidence[key] for key in ("owner", "authority", "effect", "dependency")},
            "inputs": evidence["inputs"],
            "package": evidence["package"],
            "child_source": evidence["child_source"],
            "decision": decision,
            "classification": classification,
            "invalidators": invalidators,
            "expiry_fingerprint": fingerprint,
            "expires_on": EXPIRES_ON,
            "predecessor_record_oid": old_oid,
            "route_transaction_id": transaction_id,
            "obligation_id": obligation_id,
            "route_state": "UNSATISFIED" if decision == "REQUIRED" else None,
            "child_lifecycle_owned": False,
            "consumed_record_oid": None,
        }
        if "presentation" in request:
            record_base["presentation"] = request["presentation"]
        if history_query is not None:
            record_base["history_query"] = history_query
        record = {**record_base, "record_identity": digest_json(record_base)}
        raw = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
        new_oid = write_route_record_blob(repo, raw)
        completed = subprocess.run(
            [str(trusted_host_executable(repo, "git")), "update-ref", ref_name(args.controller), new_oid, expected_oid],
            cwd=repo, env=sanitized_action_environment(), capture_output=True, text=True
        )
        if completed.returncode:
            fail("route decision CAS lost the current-record race", decision=decision)
        try:
            post_current = current_controller(repo, args.controller)
            post_eval = evaluate(repo, common, args, post_current, request)
            post_oid, _ = current_ref(repo, args.controller)
            if terminal_reentry:
                validate_terminal_continuity_chain(
                    repo,
                    controller=args.controller,
                    claim=current["claim_id"],
                    run_identity=Path(current["explicit_run_root"]).name,
                    terminal_generation=old.get("continuity_generation"),
                    terminal_receipt=old.get("continuity_receipt"),
                    current_generation=current["continuity_generation"],
                    current_receipt=current["continuity_receipt"],
                )
            if active_recovery:
                require_active_route_recovery(
                    repo,
                    common,
                    args,
                    current,
                    request,
                    old_oid,
                    old,
                    decision,
                    classification,
                    obligation_id,
                    transaction_id,
                )
            if post_current != current or post_eval[4] != fingerprint or post_oid != new_oid:
                fail("route decision currentness changed during CAS", decision=decision)
        except SystemExit:
            # Compensate a currentness race only if this exact write is still
            # current. A lost compensation race leaves a stale record that all
            # check paths reject; it never becomes advancement authority.
            subprocess.run(
                [str(trusted_host_executable(repo, "git")), "update-ref", ref_name(args.controller), expected_oid, new_oid],
                cwd=repo,
                env=sanitized_action_environment(),
                capture_output=True,
                text=True,
                check=False,
            )
            raise
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "DECIDED",
            "decision": decision,
            "classification": classification,
            "advance_allowed": False,
            "admission_required": decision == "NOT_REQUIRED",
            "enforcement_available": True,
            "record_oid": new_oid,
            "record_identity": record["record_identity"],
            "predecessor_record_oid": old_oid,
            "obligation_id": obligation_id,
            "route_transaction_id": transaction_id,
            "route_state": record["route_state"],
            "invalidators": invalidators,
            "expires_on": EXPIRES_ON,
            "history_query": history_query,
            "history_read_performed": False,
            "projection_status": projection_status(current["explicit_run_root"], decision, new_oid),
            "proof_layers": {
                "source_core": "PRESENT",
                "package": "UNVERIFIED",
                "install": "UNVERIFIED",
                "host_activation": "UNVERIFIED",
            },
            "host_activation_proven": False,
        }
    )


def execute_exact_action(
    repo: Path, request: dict[str, Any], executable: dict[str, str]
) -> dict[str, Any]:
    argv = list(request["action"]["argv"])
    if executable["resolved"] == "R0033:built-in":
        payload = json.dumps(worktree_read_set(repo), sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        return {
            "exit_code": 0,
            "stdout_bytes": len(payload),
            "stdout_digest": f"sha256:{hashlib.sha256(payload).hexdigest()}",
            "stderr_bytes": 0,
            "stderr_digest": f"sha256:{hashlib.sha256(b'').hexdigest()}",
        }
    resolved = Path(executable["resolved"])
    if file_digest(resolved) != executable["digest"]:
        fail("exact admitted action executable changed before execution")
    command = [str(resolved), *argv[1:]]
    if "interpreter_resolved" in executable:
        interpreter = Path(executable["interpreter_resolved"])
        if file_digest(interpreter) != executable["interpreter_digest"]:
            fail("exact admitted action interpreter changed before execution")
        command = [str(interpreter), bash_script_path(resolved), *argv[1:]]
    environment = sanitized_action_environment()
    try:
        completed = subprocess.run(
            command,
            cwd=repo,
            env=environment,
            capture_output=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail(f"exact admitted action could not complete: {type(exc).__name__}")
    if len(completed.stdout) > 1_000_000 or len(completed.stderr) > 1_000_000:
        fail("exact admitted action output exceeded the bounded capture")
    if completed.returncode:
        fail(f"exact admitted action failed with exit {completed.returncode}")
    return {
        "exit_code": completed.returncode,
        "stdout_bytes": len(completed.stdout),
        "stdout_digest": f"sha256:{hashlib.sha256(completed.stdout).hexdigest()}",
        "stderr_bytes": len(completed.stderr),
        "stderr_digest": f"sha256:{hashlib.sha256(completed.stderr).hexdigest()}",
    }


def command_consume(args: argparse.Namespace) -> None:
    repo, _, common = repo_context()
    request = read_request(args.request)
    with namespace_gate(common):
        old_oid, old = current_ref(repo, args.controller)
        if old_oid is None or old is None or args.expected_record != old_oid:
            fail("action-consumption CAS expected record is stale")
        if old["decision"] != "NOT_REQUIRED":
            fail("only a current NOT_REQUIRED action receipt can be consumed", decision=old["decision"])
        current = current_controller(repo, args.controller)
        decision, classification, invalidators, evidence, fingerprint, _, _ = evaluate(
            repo, common, args, current, request
        )
        if (
            decision != "NOT_REQUIRED"
            or classification != "MECHANICALLY_NOT_REQUIRED"
            or invalidators
            or old.get("expiry_fingerprint") != fingerprint
            or old.get("claim_id") != current["claim_id"]
            or old.get("continuity_receipt") != current["continuity_receipt"]
            or old.get("host_binding_generation") != args.binding_generation
        ):
            fail("action receipt is stale and cannot be consumed", decision=old["decision"])
        in_progress_base = {
            **{key: value for key, value in old.items() if key != "record_identity"},
            "decision": "PENDING",
            "classification": "JUDGEMENT_REQUIRED",
            "invalidators": ["action-in-progress"],
            "predecessor_record_oid": old_oid,
            "route_transaction_id": digest_json(
                {
                    "kind": "action-in-progress",
                    "record_oid": old_oid,
                    "fingerprint": fingerprint,
                    "controller_record_oid": current["controller_record_oid"],
                    "continuity_receipt": current["continuity_receipt"],
                    "host_binding_generation": args.binding_generation,
                }
            ),
            "obligation_id": None,
            "route_state": None,
            "consumed_record_oid": old_oid,
            "host_correlation_id": evidence["dependency"]["host_correlation_id"],
        }
        in_progress = {**in_progress_base, "record_identity": digest_json(in_progress_base)}
        in_progress_raw = json.dumps(in_progress, sort_keys=True, separators=(",", ":")) + "\n"
        in_progress_oid = write_route_record_blob(repo, in_progress_raw)
        admitted = subprocess.run(
            [str(trusted_host_executable(repo, "git")), "update-ref", ref_name(args.controller), in_progress_oid, old_oid],
            cwd=repo,
            env=sanitized_action_environment(),
            capture_output=True,
            text=True,
            check=False,
        )
        if admitted.returncode:
            fail("action-admission CAS lost the current-record race")
        admitted_current = current_controller(repo, args.controller)
        admitted_eval = evaluate(repo, common, args, admitted_current, request)
        admitted_oid, _ = current_ref(repo, args.controller)
        if admitted_current != current or admitted_eval[4] != fingerprint or admitted_oid != in_progress_oid:
            fail("action admission lost currentness before execution", decision="PENDING")

        action_result = execute_exact_action(repo, request, evidence["package"]["action_executable"])
        post_action_current = current_controller(repo, args.controller)
        post_action_eval = evaluate(repo, common, args, post_action_current, request)
        post_action_oid, _ = current_ref(repo, args.controller)
        if post_action_current != current or post_action_eval[4] != fingerprint or post_action_oid != in_progress_oid:
            fail("route authority changed while the exact action executed", decision="PENDING")
        successor_base = {
            **{key: value for key, value in in_progress.items() if key != "record_identity"},
            "decision": "PENDING",
            "classification": "JUDGEMENT_REQUIRED",
            "invalidators": ["action-completion"],
            "predecessor_record_oid": in_progress_oid,
            "route_transaction_id": digest_json(
                {
                    "kind": "action-completion",
                    "record_oid": in_progress_oid,
                    "fingerprint": fingerprint,
                    "controller_record_oid": current["controller_record_oid"],
                    "continuity_receipt": current["continuity_receipt"],
                    "host_binding_generation": args.binding_generation,
                }
            ),
            "obligation_id": None,
            "route_state": None,
            "consumed_record_oid": old_oid,
            "host_correlation_id": evidence["dependency"]["host_correlation_id"],
        }
        successor = {**successor_base, "record_identity": digest_json(successor_base)}
        raw = json.dumps(successor, sort_keys=True, separators=(",", ":")) + "\n"
        new_oid = write_route_record_blob(repo, raw)
        completed = subprocess.run(
            [str(trusted_host_executable(repo, "git")), "update-ref", ref_name(args.controller), new_oid, in_progress_oid],
            cwd=repo,
            env=sanitized_action_environment(),
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode:
            fail("action-consumption CAS lost the current-record race")
        final_oid, _ = current_ref(repo, args.controller)
        final_current = current_controller(repo, args.controller)
        final_eval = evaluate(repo, common, args, final_current, request)
        if final_oid != new_oid or final_current != current or final_eval[4] != fingerprint:
            fail("completed action record lost currentness", decision="PENDING")
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "ACTION_COMPLETE",
            "decision": "PENDING",
            "advance_allowed": False,
            "action_executed": True,
            "action_result": action_result,
            "enforcement_available": True,
            "record_oid": new_oid,
            "record_identity": successor["record_identity"],
            "consumed_record_oid": old_oid,
        }
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    recovery_prepare = subparsers.add_parser("prepare-recovery-capsule")
    recovery_observer_args_v1(recovery_prepare)
    recovery_prepare.set_defaults(run=command_prepare_recovery_capsule_v3)
    abandon = subparsers.add_parser("abandon-recovery")
    binding_args(abandon)
    recovery_observer_args_v1(abandon)
    for name in ("expected-record", "route-transaction-id", "disposition", "disposition-digest"):
        abandon.add_argument("--" + name, required=True)
    abandon.set_defaults(run=command_abandon_recovery_v1)
    recovery_custody = subparsers.add_parser("observe-recovery-custody")
    recovery_custody.set_defaults(run=command_observe_recovery_custody)
    admit_transaction = subparsers.add_parser("admit-transaction")
    admit_transaction.add_argument("--common-directory", required=True)
    admit_transaction.add_argument("--controller", required=True)
    admit_transaction.add_argument("--route-transaction-id", required=True)
    admit_transaction.add_argument("--selected-child", required=True)
    admit_transaction.add_argument("--writer-key", action="append", default=[])
    admit_transaction.add_argument("--dependency-key", action="append", default=[])
    admit_transaction.set_defaults(run=command_admit_transaction)
    decide_transaction = subparsers.add_parser("decide-transaction")
    common_args(decide_transaction)
    decide_transaction.add_argument("--recovery-capsule")
    recovery_observer_args_v1(decide_transaction)
    decide_transaction.add_argument("--expected-record", required=True)
    decide_transaction.set_defaults(run=command_decide_transaction)
    decide = subparsers.add_parser("decide")
    common_args(decide)
    decide.add_argument("--expected-record", required=True)
    decide.set_defaults(run=command_decide)
    check = subparsers.add_parser("check")
    common_args(check)
    check.set_defaults(run=command_check)
    observe_current = subparsers.add_parser("observe-current")
    binding_args(observe_current)
    observe_current.set_defaults(run=command_observe_current)
    admit_current = subparsers.add_parser("admit-current")
    binding_args(admit_current)
    admit_current.set_defaults(run=command_admit_current)
    consume = subparsers.add_parser("consume")
    common_args(consume)
    consume.add_argument("--expected-record", required=True)
    consume.set_defaults(run=command_consume)
    open_child = subparsers.add_parser("open")
    common_args(open_child)
    open_child.add_argument("--recovery-capsule")
    recovery_observer_args_v1(open_child)
    open_child.add_argument("--expected-record", required=True)
    open_child.add_argument("--packet", required=True)
    open_child.add_argument("--logical-task", required=True)
    open_child.add_argument("--route-transaction-id")
    open_child.set_defaults(run=command_open)
    return_child = subparsers.add_parser("return")
    common_args(return_child)
    return_child.add_argument("--recovery-capsule")
    recovery_observer_args_v1(return_child)
    return_child.add_argument("--expected-record", required=True)
    return_child.add_argument("--return", dest="return_path", required=True)
    return_child.add_argument("--route-transaction-id")
    return_child.set_defaults(run=command_return)
    complete = subparsers.add_parser("complete")
    common_args(complete)
    complete.add_argument("--recovery-capsule")
    recovery_observer_args_v1(complete)
    complete.add_argument("--expected-record", required=True)
    complete.add_argument("--packet", required=True)
    complete.add_argument("--return", dest="return_path", required=True)
    complete.add_argument("--decision", required=True)
    complete.add_argument("--route-transaction-id")
    complete.set_defaults(run=command_complete)
    replay = subparsers.add_parser("replay")
    common_args(replay)
    replay.add_argument("--expected-record", required=True)
    replay.add_argument("--event", required=True)
    replay.set_defaults(run=command_replay)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.run(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
