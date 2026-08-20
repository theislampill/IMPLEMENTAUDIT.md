#!/usr/bin/env python3
"""Canonical R0033 route-decision and obligation authority.

This H2A core owns only PENDING/NOT_REQUIRED/REQUIRED classification and the
current immutable Git-ref record. Child opening, result return, and obligation
completion are deliberately outside this module.
"""

from __future__ import annotations

import argparse
import contextlib
import errno
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterator, NoReturn


RESULT_SCHEMA = "implementaudit.route-transaction-result.v1"
REQUEST_SCHEMA = "implementaudit.route-decision-request.v1"
RECORD_SCHEMA = "implementaudit.route-decision.v1"
PREDICATE_VERSION = "R0033.route-predicate.v1"
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
STATUS_VALUES = {"CURRENT", "MISSING", "STALE", "CONTRADICTORY"}
CONTINUITY_RE = re.compile(r"G[0-9A-F]{4}")
CONTROLLER_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,47}")
OID_RE = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")
HEX_RE = re.compile(r"sha256:[0-9a-f]{64}")
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
RECORD_KEYS = {
    "schema", "predicate_version", "controller_id", "claim_id", "explicit_run_root",
    "continuity_generation", "continuity_receipt", "host_id", "host_session_id",
    "host_binding_generation", "host_correlation_id", "boundary", "scope", "action",
    "evidence", "inputs", "package", "child_source", "decision", "classification",
    "invalidators", "expiry_fingerprint", "expires_on", "predecessor_record_oid",
    "route_transaction_id", "obligation_id", "route_state", "child_lifecycle_owned",
    "record_identity",
}


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


def run(command: list[str], *, cwd: Path, label: str) -> str:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        fail(f"{label} failed: {detail}")
    return completed.stdout.strip()


def git(repo: Path, *args: str, input_text: str | None = None, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=repo, text=True, input=input_text, capture_output=True, check=False
    )
    if check and completed.returncode:
        fail(f"git {' '.join(args)} failed: {completed.stderr.strip() or completed.stdout.strip()}")
    return completed.stdout.strip()


def digest_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON member")
    return value


def exact_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 1024 or any(ord(char) < 32 for char in value):
        fail(f"{label} is empty, oversized, or contains a control character")
    return value


def exact_keys(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        fail(f"{label} has the wrong shape")
    return value


def identity_record(value: Any, label: str, *, status: bool = True) -> dict[str, str]:
    keys = {"identity", "digest", "status"} if status else {"identity", "digest"}
    record = exact_keys(value, keys, label)
    exact_text(record["identity"], f"{label}.identity")
    if not isinstance(record["digest"], str) or not HEX_RE.fullmatch(record["digest"]):
        fail(f"{label}.digest is not a canonical sha256 identity")
    if status and record["status"] not in STATUS_VALUES:
        fail(f"{label}.status is invalid")
    return record


def read_request(path: str) -> dict[str, Any]:
    target = Path(path)
    try:
        if target.absolute() != target.resolve(strict=True):
            fail("request traverses an alias")
        info = os.lstat(target)
        if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or info.st_size > 1_000_000:
            fail("request is not a safe regular file")
        request = json.loads(target.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        fail(f"request is unreadable or malformed: {exc}")
    keys = {
        "schema",
        "predicate_version",
        "boundary",
        "scope",
        "action",
        "evidence",
        "inputs",
        "package",
        "child_source",
        "required_reasons",
        "judgement_required",
    }
    exact_keys(request, keys, "request")
    if request["schema"] != REQUEST_SCHEMA or request["predicate_version"] != PREDICATE_VERSION:
        fail("request schema or predicate version is stale")
    boundary = exact_keys(request["boundary"], {"kind", "event_id", "digest", "status"}, "boundary")
    exact_text(boundary["kind"], "boundary.kind")
    exact_text(boundary["event_id"], "boundary.event_id")
    if not HEX_RE.fullmatch(boundary.get("digest", "")) or boundary.get("status") not in STATUS_VALUES:
        fail("boundary identity is malformed")
    identity_record(request["scope"], "scope")
    action = exact_keys(request["action"], {"identity", "digest", "status", "class"}, "action")
    exact_text(action["identity"], "action.identity")
    exact_text(action["class"], "action.class")
    if not HEX_RE.fullmatch(action.get("digest", "")) or action.get("status") not in STATUS_VALUES:
        fail("action identity is malformed")
    evidence = exact_keys(request["evidence"], {"owner", "authority", "effect", "dependency"}, "evidence")
    for name in sorted(evidence):
        identity_record(evidence[name], f"evidence.{name}")
    identity_record(request["package"], "package")
    identity_record(request["child_source"], "child_source")
    if not isinstance(request["inputs"], list) or not request["inputs"]:
        fail("inputs must be a non-empty complete identity set")
    identities: list[str] = []
    for index, item in enumerate(request["inputs"]):
        identities.append(identity_record(item, f"inputs[{index}]")["identity"])
    if identities != sorted(identities) or len(identities) != len(set(identities)):
        fail("inputs are not uniquely ordered by identity")
    reasons = request["required_reasons"]
    if not isinstance(reasons, list) or reasons != sorted(set(reasons)) or any(x not in REQUIRED_REASONS for x in reasons):
        fail("required_reasons are unknown, duplicate, or non-canonical")
    if not isinstance(request["judgement_required"], bool):
        fail("judgement_required is not boolean")
    return request


def classify(request: dict[str, Any]) -> tuple[str, str, list[str]]:
    observed = [request["boundary"], request["scope"], request["action"], request["package"], request["child_source"]]
    observed.extend(request["evidence"].values())
    observed.extend(request["inputs"])
    noncurrent = sorted(
        f"{item['identity']}:{item['status']}" for item in observed if item["status"] != "CURRENT"
    )
    if noncurrent:
        return "PENDING", "JUDGEMENT_REQUIRED", noncurrent
    if request["required_reasons"]:
        return "REQUIRED", "MECHANICALLY_REQUIRED", list(request["required_reasons"])
    if request["judgement_required"] or request["action"]["class"] not in CLOSED_ACTION_CLASSES:
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


def current_ref(repo: Path, controller: str) -> tuple[str | None, dict[str, Any] | None]:
    ref = ref_name(controller)
    completed = subprocess.run(["git", "rev-parse", "--verify", ref], cwd=repo, text=True, capture_output=True)
    if completed.returncode:
        return None, None
    oid = completed.stdout.strip()
    try:
        record = json.loads(git(repo, "cat-file", "blob", oid), object_pairs_hook=unique_object)
    except (json.JSONDecodeError, ValueError):
        fail("current route record is malformed")
    if not isinstance(record, dict) or set(record) != RECORD_KEYS or record.get("schema") != RECORD_SCHEMA:
        fail("current route record is malformed or mixed-version")
    if (
        record.get("predicate_version") != PREDICATE_VERSION
        or record.get("controller_id") != controller
        or record.get("decision") not in DECISIONS
        or record.get("expires_on") != EXPIRES_ON
        or record.get("child_lifecycle_owned") is not False
    ):
        fail("current route record has foreign identity or invalid decision")
    if record["decision"] == "REQUIRED":
        if record.get("route_state") != "UNSATISFIED" or not isinstance(record.get("obligation_id"), str):
            fail("current required route record has no unsatisfied obligation")
    elif record.get("route_state") is not None or record.get("obligation_id") is not None:
        fail("non-required route record improperly owns an obligation")
    if record.get("classification") not in CLASSIFICATIONS or record.get("record_identity") != digest_json(
        {key: value for key, value in record.items() if key != "record_identity"}
    ):
        fail("current route record identity is invalid")
    return oid, record


def current_controller(repo: Path, controller: str) -> dict[str, str]:
    claim = Path(__file__).with_name("claim-run.sh")
    current = run(["bash", str(claim), "--current-controller", controller], cwd=repo, label="controller currentness")
    parts = current.split("\t")
    if len(parts) != 4 or parts[0] != controller:
        fail("controller currentness returned a foreign or malformed record")
    receipt = run(
        ["bash", str(claim), "--require-current-continuity", controller],
        cwd=repo,
        label="continuity currentness",
    )
    prefix = f"refs/implementaudit/continuity-receipts/{controller}/"
    if not receipt.startswith(prefix) or "@" not in receipt:
        fail("continuity receipt identity is malformed")
    generation = receipt[len(prefix) :].split("@", 1)[0]
    if not CONTINUITY_RE.fullmatch(generation):
        fail("continuity generation is malformed")
    return {
        "controller_id": parts[0],
        "repository_identity": parts[1],
        "explicit_run_root": parts[2],
        "claim_id": parts[3],
        "continuity_receipt": receipt,
        "continuity_generation": generation,
    }


def validate_binding(
    repo: Path,
    common: str,
    args: argparse.Namespace,
    current: dict[str, str],
    request: dict[str, Any],
    obligation_id: str | None,
    transaction_id: str | None,
) -> dict[str, Any]:
    binding_core = Path(__file__).with_name("host-session-binding.py")
    lookup_raw = run(
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
        cwd=repo,
        label="host binding lookup",
    )
    try:
        lookup = json.loads(lookup_raw)
    except json.JSONDecodeError:
        fail("host binding lookup returned malformed output")
    binding = lookup.get("binding") if lookup.get("status") == "BOUND" else None
    if not isinstance(binding, dict):
        fail("host session has no active exact binding")
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
            fail(f"host session binding has stale or foreign {key}")
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
        request["boundary"]["event_id"],
    ]
    if obligation_id is not None and transaction_id is not None:
        command.extend(["--obligation-id", obligation_id, "--route-transaction-id", transaction_id])
    attributed_raw = run(command, cwd=repo, label="host event attribution")
    try:
        attributed = json.loads(attributed_raw)
    except json.JSONDecodeError:
        fail("host event attribution returned malformed output")
    if attributed.get("status") != "ATTRIBUTED":
        fail("host event attribution is unavailable")
    return attributed


@contextlib.contextmanager
def namespace_gate(repo: Path) -> Iterator[None]:
    directory = repo / ".IMPLEMENTAUDIT" / ".r36-locks"
    for candidate in (directory.parent, directory):
        if os.path.lexists(candidate):
            info = os.lstat(candidate)
            if (
                not stat.S_ISDIR(info.st_mode)
                or stat.S_ISLNK(info.st_mode)
                or bool(getattr(info, "st_file_attributes", 0) & 0x400)
            ):
                fail("governed-writer namespace custody is aliased or unsafe")
    directory.mkdir(parents=True, exist_ok=True)
    gate = directory / "namespace.gate"
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


def common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--controller", required=True)
    parser.add_argument("--store", required=True)
    parser.add_argument("--host-id", required=True)
    parser.add_argument("--host-session-id", required=True)
    parser.add_argument("--binding-generation", required=True)
    parser.add_argument("--request", required=True)


def command_check(args: argparse.Namespace) -> None:
    repo, _, common = repo_context()
    oid, record = current_ref(repo, args.controller)
    if oid is None or record is None:
        fail("canonical route decision is absent")
    if args.action_completed:
        fail("route decision expired on action completion")
    request = read_request(args.request)
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
    decision, classification, invalidators = classify(request)
    fingerprint = digest_json(request)
    if record.get("expiry_fingerprint") != fingerprint:
        fail("route decision expired because its bound scope or evidence changed", decision=record["decision"])
    if (decision, classification, invalidators) != (
        record.get("decision"),
        record.get("classification"),
        record.get("invalidators"),
    ):
        fail("route decision no longer agrees with the current predicate", decision=record["decision"])
    obligation_id = record.get("obligation_id")
    transaction_id = record.get("route_transaction_id")
    validate_binding(repo, common, args, current, request, obligation_id, transaction_id)
    advance = record["decision"] == "NOT_REQUIRED"
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "CURRENT",
            "decision": record["decision"],
            "classification": record["classification"],
            "advance_allowed": advance,
            "enforcement_available": True,
            "record_oid": oid,
            "record_identity": record["record_identity"],
            "obligation_id": obligation_id,
            "route_state": record.get("route_state"),
            "projection_status": projection_status(current["explicit_run_root"], record["decision"], oid),
            "proof_layers": {
                "source_core": "PRESENT",
                "package": "UNVERIFIED",
                "install": "UNVERIFIED",
                "host_activation": "UNVERIFIED",
            },
            "host_activation_proven": False,
        }
    )
    if not advance:
        raise SystemExit(3)


def command_decide(args: argparse.Namespace) -> None:
    repo, _, common = repo_context()
    request = read_request(args.request)
    decision, classification, invalidators = classify(request)
    fingerprint = digest_json(request)
    transaction_id = digest_json({"controller": args.controller, "fingerprint": fingerprint, "kind": "transaction"})
    obligation_id = (
        digest_json({"controller": args.controller, "fingerprint": fingerprint, "kind": "obligation"})
        if decision == "REQUIRED"
        else None
    )
    current = current_controller(repo, args.controller)
    attributed = validate_binding(repo, common, args, current, request, obligation_id, transaction_id if obligation_id else None)
    with namespace_gate(repo):
        # Recheck both owners while holding the cooperating target-writer gate.
        current = current_controller(repo, args.controller)
        validate_binding(repo, common, args, current, request, obligation_id, transaction_id if obligation_id else None)
        old_oid, old = current_ref(repo, args.controller)
        expected = args.expected_record
        if expected == "none":
            if old_oid is not None:
                fail("route decision CAS expected absence but a current record exists", decision=old["decision"] if old else "PENDING")
            expected_oid = ZERO_OID
        elif not OID_RE.fullmatch(expected) or expected != old_oid:
            fail("route decision CAS expected record is stale", decision=old["decision"] if old else "PENDING")
        else:
            expected_oid = expected
        if old and old.get("expiry_fingerprint") == fingerprint and old["decision"] == decision:
            emit(
                {
                    "schema": RESULT_SCHEMA,
                    "status": "DECIDED",
                    "decision": decision,
                    "classification": classification,
                    "advance_allowed": decision == "NOT_REQUIRED",
                    "enforcement_available": True,
                    "record_oid": old_oid,
                    "record_identity": old["record_identity"],
                    "obligation_id": old.get("obligation_id"),
                    "route_state": old.get("route_state"),
                    "idempotent": True,
                }
            )
            return
        if old and old["decision"] == "REQUIRED" and old.get("route_state") == "UNSATISFIED":
            fail("an active same-controller route obligation cannot be downgraded or replaced in H2A", decision="REQUIRED")
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
            "host_correlation_id": attributed["correlation_id"],
            "boundary": request["boundary"],
            "scope": request["scope"],
            "action": request["action"],
            "evidence": request["evidence"],
            "inputs": request["inputs"],
            "package": request["package"],
            "child_source": request["child_source"],
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
        }
        record = {**record_base, "record_identity": digest_json(record_base)}
        raw = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
        new_oid = git(repo, "hash-object", "-w", "--stdin", input_text=raw)
        completed = subprocess.run(
            ["git", "update-ref", ref_name(args.controller), new_oid, expected_oid], cwd=repo, capture_output=True, text=True
        )
        if completed.returncode:
            fail("route decision CAS lost the current-record race", decision=decision)
        try:
            post_current = current_controller(repo, args.controller)
            validate_binding(
                repo,
                common,
                args,
                post_current,
                request,
                obligation_id,
                transaction_id if obligation_id else None,
            )
        except SystemExit:
            # Compensate a currentness race only if this exact write is still
            # current. A lost compensation race leaves a stale record that all
            # check paths reject; it never becomes advancement authority.
            subprocess.run(
                ["git", "update-ref", ref_name(args.controller), expected_oid, new_oid],
                cwd=repo,
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
            "advance_allowed": decision == "NOT_REQUIRED",
            "enforcement_available": True,
            "record_oid": new_oid,
            "record_identity": record["record_identity"],
            "predecessor_record_oid": old_oid,
            "obligation_id": obligation_id,
            "route_transaction_id": transaction_id,
            "route_state": record["route_state"],
            "invalidators": invalidators,
            "expires_on": EXPIRES_ON,
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    decide = subparsers.add_parser("decide")
    common_args(decide)
    decide.add_argument("--expected-record", required=True)
    decide.set_defaults(run=command_decide)
    check = subparsers.add_parser("check")
    common_args(check)
    check.add_argument("--action-completed", action="store_true")
    check.set_defaults(run=command_check)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.run(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
