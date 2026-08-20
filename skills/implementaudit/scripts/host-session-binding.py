#!/usr/bin/env python3
"""Bind one exact host session to one governed IMPLEMENTAUDIT object."""

from __future__ import annotations

import argparse
import contextlib
import errno
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Iterator, NoReturn


STORE_SCHEMA = "implementaudit.host-session-binding-store.v1"
STATE_SCHEMA = "implementaudit.host-session-binding-state.v1"
BINDING_SCHEMA = "implementaudit.host-session-binding.v1"
RESULT_SCHEMA = "implementaudit.host-session-binding-result.v1"
GENERATION_RE = re.compile(r"G([0-9A-F]{4})")
MAX_TEXT = 1024
PROOF_LAYERS = {
    "source_core": "PRESENT",
    "package": "UNVERIFIED",
    "install": "UNVERIFIED",
    "host_activation": "UNVERIFIED",
}
BINDING_KEYS = {
    "schema",
    "host_id",
    "host_session_id",
    "controller_id",
    "claim_id",
    "explicit_run_root",
    "repository_identity",
    "git_common_directory_identity",
    "worktree_identity",
    "binding_generation",
    "activation_event_id",
    "activation_receipt",
    "applicable_continuity_generation",
    "applicable_continuity_receipt",
    "status",
    "predecessor_generation",
    "supersession_or_tombstone_reason",
}


def fail(message: str) -> NoReturn:
    print(
        json.dumps(
            {
                "schema": RESULT_SCHEMA,
                "status": "UNAVAILABLE",
                "enforcement_available": False,
                "error": message,
            },
            sort_keys=True,
        )
    )
    raise SystemExit(2)


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


def exact_text(value: str, label: str) -> str:
    if not value or len(value) > MAX_TEXT or any(ord(char) < 32 for char in value):
        fail(f"{label} is empty, oversized, or contains a control character")
    return value


def generation(value: str, label: str) -> str:
    match = GENERATION_RE.fullmatch(value)
    if not match or int(match.group(1), 16) < 1:
        fail(f"{label} is not a non-zero canonical generation")
    return value


def next_generation(value: str) -> str:
    current = int(generation(value, "binding_generation")[1:], 16)
    if current >= 0xFFFF:
        fail("binding generation is exhausted")
    return f"G{current + 1:04X}"


def has_reparse_flag(info: os.stat_result) -> bool:
    return bool(getattr(info, "st_file_attributes", 0) & 0x400)


def unsafe_file(info: os.stat_result) -> bool:
    return (
        not stat.S_ISREG(info.st_mode)
        or stat.S_ISLNK(info.st_mode)
        or has_reparse_flag(info)
        or info.st_nlink != 1
    )


def safe_existing_directory(value: str, label: str) -> str:
    raw = Path(value)
    try:
        absolute = raw.absolute()
        resolved = raw.resolve(strict=True)
        info = os.lstat(absolute)
    except (OSError, RuntimeError) as exc:
        fail(f"{label} is not a resolvable existing directory: {exc}")
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or has_reparse_flag(info):
        fail(f"{label} is a symlink, reparse point, or non-directory")
    if absolute != resolved:
        fail(f"{label} traverses an alias")
    return str(resolved)


def ensure_safe_directory(path: Path, label: str) -> Path:
    absolute = path.absolute()
    existing = absolute
    while not os.path.lexists(existing):
        parent = existing.parent
        if parent == existing:
            fail(f"{label} has no inspectable existing ancestor")
        existing = parent
    safe_existing_directory(str(existing), f"{label} ancestor")
    try:
        absolute.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        fail(f"{label} cannot be created: {exc}")
    return Path(safe_existing_directory(str(absolute), label))


def is_within(child: str, parent: str) -> bool:
    try:
        Path(child).relative_to(Path(parent))
    except ValueError:
        return False
    return True


def require_run_worktree_custody(run_root: str, worktree: str) -> None:
    if run_root == worktree or not is_within(run_root, worktree):
        fail("explicit_run_root is outside the recorded worktree")


def require_external_store(store: Path, binding: dict[str, Any]) -> Path:
    canonical = Path(safe_existing_directory(str(store), "store"))
    store_text = str(canonical)
    for label in (
        "repository_identity",
        "git_common_directory_identity",
        "worktree_identity",
        "explicit_run_root",
    ):
        target = binding[label]
        if store_text == target or is_within(store_text, target) or is_within(target, store_text):
            fail(f"binding store overlaps target-controlled {label}")
    return canonical


def binding_key(host_id: str, host_session_id: str) -> str:
    return hashlib.sha256(f"{host_id}\0{host_session_id}".encode("utf-8")).hexdigest()


def session_key(host_session_id: str) -> str:
    return hashlib.sha256(host_session_id.encode("utf-8")).hexdigest()


def owner_path(store: Path) -> Path:
    return store / "owner.json"


def state_path(store: Path, host_id: str, host_session_id: str) -> Path:
    key = binding_key(host_id, host_session_id)
    return store / "bindings" / key[:2] / key / "binding.json"


def session_index_path(store: Path, host_session_id: str) -> Path:
    key = session_key(host_session_id)
    return store / "sessions" / key[:2] / f"{key}.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    parent = ensure_safe_directory(path.parent, f"{path.name} parent")
    target = parent / path.name
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        absolute = path.absolute()
        resolved = path.resolve(strict=True)
        if absolute != resolved:
            fail(f"{label} traverses an alias")
        info = os.lstat(path)
        if unsafe_file(info):
            fail(f"{label} is not a safe regular file")
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"{label} is unreadable or malformed: {exc}")
    if not isinstance(payload, dict):
        fail(f"{label} is not an object")
    return payload


def load_owner(store: Path, expected_owner: str | None = None) -> dict[str, Any]:
    marker = read_json(owner_path(store), "store owner state")
    if set(marker) != {"schema", "owner_id", "trusted", "enabled"}:
        fail("store owner state has the wrong shape")
    if marker["schema"] != STORE_SCHEMA or marker["trusted"] is not True or marker["enabled"] is not True:
        fail("store owner state is untrusted, disabled, or mixed-version")
    if not isinstance(marker["owner_id"], str):
        fail("store owner identity is malformed")
    if expected_owner is not None and marker["owner_id"] != expected_owner:
        fail("foreign store owner")
    return marker


@contextlib.contextmanager
def writer_lock(store: Path) -> Iterator[None]:
    lock_path = store / ".writer.lock"
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        fail(f"writer lock cannot be opened safely: {exc}")
    locked = False
    try:
        opened = os.fstat(descriptor)
        current = os.lstat(lock_path)
        if unsafe_file(opened) or unsafe_file(current) or (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
            fail("writer lock is unsafe")
        if opened.st_size == 0:
            os.write(descriptor, b"\0")
            os.fsync(descriptor)
        elif opened.st_size != 1:
            fail("writer lock has an invalid size")
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
        try:
            if locked and os.name == "nt":
                import msvcrt

                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            elif locked:
                import fcntl

                fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def validate_record(record: Any, host_id: str, host_session_id: str) -> dict[str, Any]:
    if not isinstance(record, dict) or set(record) != BINDING_KEYS:
        fail("binding record has the wrong shape")
    if record["schema"] != BINDING_SCHEMA:
        fail("binding record has a mixed-version schema")
    if record["host_id"] != host_id or record["host_session_id"] != host_session_id:
        fail("binding record has foreign host or session identity")
    binding_generation = generation(record["binding_generation"], "binding_generation")
    generation(record["applicable_continuity_generation"], "applicable_continuity_generation")
    if record["status"] not in {"ACTIVE", "SUPERSEDED", "TOMBSTONED"}:
        fail("binding record has an invalid status")
    for key in (
        "controller_id",
        "claim_id",
        "explicit_run_root",
        "repository_identity",
        "git_common_directory_identity",
        "worktree_identity",
        "activation_event_id",
        "activation_receipt",
        "applicable_continuity_receipt",
    ):
        if not isinstance(record[key], str) or not record[key]:
            fail(f"binding record has an invalid {key}")
    for key in (
        "explicit_run_root",
        "repository_identity",
        "git_common_directory_identity",
        "worktree_identity",
    ):
        if safe_existing_directory(record[key], key) != record[key]:
            fail(f"binding record has a non-canonical {key}")
    require_run_worktree_custody(record["explicit_run_root"], record["worktree_identity"])
    predecessor = record["predecessor_generation"]
    ordinal = int(binding_generation[1:], 16)
    expected_predecessor = None if ordinal == 1 else f"G{ordinal - 1:04X}"
    if predecessor != expected_predecessor:
        fail("binding record has a broken predecessor-generation chain")
    reason = record["supersession_or_tombstone_reason"]
    if reason is not None and (not isinstance(reason, str) or not reason):
        fail("binding record has an invalid transition reason")
    return record


def load_state(store: Path, host_id: str, host_session_id: str) -> tuple[Path, dict[str, Any]]:
    target = state_path(store, host_id, host_session_id)
    state = read_json(target, "binding state")
    if set(state) != {"schema", "host_id", "host_session_id", "records"}:
        fail("binding state has the wrong shape")
    if state["schema"] != STATE_SCHEMA or state["host_id"] != host_id or state["host_session_id"] != host_session_id:
        fail("binding state is malformed, foreign, or mixed-version")
    if not isinstance(state["records"], list) or not state["records"]:
        fail("binding state has no records")
    records = [validate_record(record, host_id, host_session_id) for record in state["records"]]
    generations = [record["binding_generation"] for record in records]
    if len(generations) != len(set(generations)) or generations != sorted(generations):
        fail("binding generations are duplicate or out of order")
    active = [record for record in records if record["status"] == "ACTIVE"]
    if len(active) > 1 or (active and active[0] is not records[-1]):
        fail("binding state is ambiguous")
    if not active and records[-1]["status"] != "TOMBSTONED":
        fail("binding state has no current active or tombstoned record")
    for record in records[:-1]:
        if record["status"] != "SUPERSEDED":
            fail("non-current binding record is not superseded")
    return target, state


def current_record(state: dict[str, Any], *, require_active: bool) -> dict[str, Any]:
    current = state["records"][-1]
    if require_active and current["status"] != "ACTIVE":
        fail("host session binding is not active")
    return current


def proof_result(**payload: Any) -> dict[str, Any]:
    return {
        "schema": RESULT_SCHEMA,
        **payload,
        "host_activation_proven": False,
        "proof_layers": dict(PROOF_LAYERS),
    }


def command_init(args: argparse.Namespace) -> None:
    owner = exact_text(args.owner_id, "owner_id")
    store = Path(args.store).absolute()
    if store.exists():
        try:
            info = os.lstat(store)
        except OSError as exc:
            fail(f"store cannot be inspected: {exc}")
        if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or has_reparse_flag(info):
            fail("store is a symlink, reparse point, or non-directory")
        marker = owner_path(store)
        if marker.exists():
            existing = load_owner(store, owner)
            emit({"schema": STORE_SCHEMA, "status": "READY", "owner_id": existing["owner_id"]})
            return
        if any(store.iterdir()):
            fail("non-empty store lacks trusted owner state")
    else:
        store = ensure_safe_directory(store, "store")
    atomic_json(owner_path(store), {"schema": STORE_SCHEMA, "owner_id": owner, "trusted": True, "enabled": True})
    emit({"schema": STORE_SCHEMA, "status": "READY", "owner_id": owner})


def binding_from_args(
    args: argparse.Namespace,
    *,
    binding_generation: str,
    predecessor_generation: str | None,
    reason: str | None,
) -> dict[str, Any]:
    run_root = safe_existing_directory(args.explicit_run_root, "explicit_run_root")
    repository = safe_existing_directory(args.repository_identity, "repository_identity")
    common = safe_existing_directory(args.git_common_directory_identity, "git_common_directory_identity")
    worktree = safe_existing_directory(args.worktree_identity, "worktree_identity")
    require_run_worktree_custody(run_root, worktree)
    return {
        "schema": BINDING_SCHEMA,
        "host_id": exact_text(args.host_id, "host_id"),
        "host_session_id": exact_text(args.host_session_id, "host_session_id"),
        "controller_id": exact_text(args.controller_id, "controller_id"),
        "claim_id": exact_text(args.claim_id, "claim_id"),
        "explicit_run_root": run_root,
        "repository_identity": repository,
        "git_common_directory_identity": common,
        "worktree_identity": worktree,
        "binding_generation": binding_generation,
        "activation_event_id": exact_text(args.activation_event_id, "activation_event_id"),
        "activation_receipt": exact_text(args.activation_receipt, "activation_receipt"),
        "applicable_continuity_generation": generation(args.continuity_generation, "continuity_generation"),
        "applicable_continuity_receipt": exact_text(args.continuity_receipt, "continuity_receipt"),
        "status": "ACTIVE",
        "predecessor_generation": predecessor_generation,
        "supersession_or_tombstone_reason": reason,
    }


def command_bind(args: argparse.Namespace) -> None:
    store = Path(args.store).absolute()
    load_owner(store, exact_text(args.owner_id, "owner_id"))
    binding = binding_from_args(args, binding_generation="G0001", predecessor_generation=None, reason=None)
    store = require_external_store(store, binding)
    target = state_path(store, binding["host_id"], binding["host_session_id"])
    index = session_index_path(store, binding["host_session_id"])
    with writer_lock(store):
        if target.exists():
            fail("binding already exists; expected-generation rebinding is required")
        if index.exists():
            existing = read_json(index, "session host index")
            if existing != {"host_id": binding["host_id"], "host_session_id": binding["host_session_id"]}:
                fail("same session identity is already bound under an incompatible host")
        else:
            atomic_json(index, {"host_id": binding["host_id"], "host_session_id": binding["host_session_id"]})
        atomic_json(
            target,
            {
                "schema": STATE_SCHEMA,
                "host_id": binding["host_id"],
                "host_session_id": binding["host_session_id"],
                "records": [binding],
            },
        )
    emit(proof_result(status="BOUND", binding=binding))


def command_rebind(args: argparse.Namespace) -> None:
    store = Path(args.store).absolute()
    load_owner(store, exact_text(args.owner_id, "owner_id"))
    host_id = exact_text(args.host_id, "host_id")
    session_id = exact_text(args.host_session_id, "host_session_id")
    expected = generation(args.expected_generation, "expected_generation")
    reason = exact_text(args.reason, "reason")
    with writer_lock(store):
        target, state = load_state(store, host_id, session_id)
        current = current_record(state, require_active=True)
        if current["binding_generation"] != expected:
            fail("expected binding generation does not match current generation")
        successor = binding_from_args(
            args,
            binding_generation=next_generation(expected),
            predecessor_generation=expected,
            reason=reason,
        )
        require_external_store(store, current)
        require_external_store(store, successor)
        predecessor = dict(current)
        predecessor["status"] = "SUPERSEDED"
        predecessor["supersession_or_tombstone_reason"] = reason
        state["records"][-1] = predecessor
        state["records"].append(successor)
        atomic_json(target, state)
    emit(proof_result(status="BOUND", binding=successor))


def command_lookup(args: argparse.Namespace) -> None:
    host_id = exact_text(args.host_id, "host_id")
    session_id = exact_text(args.host_session_id, "host_session_id")
    store = Path(args.store).absolute()
    target = state_path(store, host_id, session_id)
    if not target.exists():
        emit({"schema": RESULT_SCHEMA, "status": "UNBOUND", "enforcement_available": False})
        return
    load_owner(store)
    _, state = load_state(store, host_id, session_id)
    current = current_record(state, require_active=False)
    require_external_store(store, current)
    if current["status"] == "TOMBSTONED":
        emit(proof_result(status="TOMBSTONED", enforcement_available=False, binding=current))
        return
    emit(proof_result(status="BOUND", binding=current))


def command_validate_event(args: argparse.Namespace) -> None:
    host_id = exact_text(args.host_id, "host_id")
    session_id = exact_text(args.host_session_id, "host_session_id")
    store = Path(args.store).absolute()
    target = state_path(store, host_id, session_id)
    if not target.exists():
        fail("host session is unbound")
    load_owner(store)
    _, state = load_state(store, host_id, session_id)
    current = current_record(state, require_active=True)
    require_external_store(store, current)
    observed = {
        "binding_generation": generation(args.binding_generation, "binding_generation"),
        "controller_id": exact_text(args.controller_id, "controller_id"),
        "claim_id": exact_text(args.claim_id, "claim_id"),
        "explicit_run_root": safe_existing_directory(args.explicit_run_root, "explicit_run_root"),
        "repository_identity": safe_existing_directory(args.repository_identity, "repository_identity"),
        "git_common_directory_identity": safe_existing_directory(
            args.git_common_directory_identity, "git_common_directory_identity"
        ),
        "worktree_identity": safe_existing_directory(args.worktree_identity, "worktree_identity"),
        "applicable_continuity_generation": generation(args.continuity_generation, "continuity_generation"),
        "applicable_continuity_receipt": exact_text(args.continuity_receipt, "continuity_receipt"),
    }
    for key, value in observed.items():
        if current[key] != value:
            fail(f"event has stale or foreign {key}")
    obligation = args.obligation_id
    transaction = args.route_transaction_id
    if (obligation is None) != (transaction is None):
        fail("route obligation and transaction identities must be supplied together")
    correlation = {
        "host_id": host_id,
        "host_session_id": session_id,
        **observed,
        "event_id": exact_text(args.event_id, "event_id"),
        "turn_id": exact_text(args.turn_id, "turn_id") if args.turn_id else None,
        "tool_use_id": exact_text(args.tool_use_id, "tool_use_id") if args.tool_use_id else None,
        "agent_id": exact_text(args.agent_id, "agent_id") if args.agent_id else None,
        "obligation_id": exact_text(obligation, "obligation_id") if obligation else None,
        "route_transaction_id": exact_text(transaction, "route_transaction_id") if transaction else None,
    }
    digest = hashlib.sha256(json.dumps(correlation, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    result = proof_result(
        status="ATTRIBUTED",
        binding_generation=current["binding_generation"],
        correlation_id=f"sha256:{digest}",
    )
    if obligation is not None:
        result["obligation_id"] = obligation
        result["route_transaction_id"] = transaction
    emit(result)


def command_tombstone(args: argparse.Namespace) -> None:
    store = Path(args.store).absolute()
    load_owner(store, exact_text(args.owner_id, "owner_id"))
    host_id = exact_text(args.host_id, "host_id")
    session_id = exact_text(args.host_session_id, "host_session_id")
    expected = generation(args.expected_generation, "expected_generation")
    reason = exact_text(args.reason, "reason")
    with writer_lock(store):
        target, state = load_state(store, host_id, session_id)
        current = current_record(state, require_active=True)
        require_external_store(store, current)
        if current["binding_generation"] != expected:
            fail("expected binding generation does not match current generation")
        predecessor = dict(current)
        predecessor["status"] = "SUPERSEDED"
        predecessor["supersession_or_tombstone_reason"] = reason
        tombstone = dict(current)
        tombstone["binding_generation"] = next_generation(expected)
        tombstone["status"] = "TOMBSTONED"
        tombstone["predecessor_generation"] = expected
        tombstone["supersession_or_tombstone_reason"] = reason
        state["records"][-1] = predecessor
        state["records"].append(tombstone)
        atomic_json(target, state)
    emit(proof_result(status="TOMBSTONED", binding=tombstone, object_closed=False))


def command_gc(args: argparse.Namespace) -> None:
    store = Path(args.store).absolute()
    load_owner(store, exact_text(args.owner_id, "owner_id"))
    host_id = exact_text(args.host_id, "host_id")
    session_id = exact_text(args.host_session_id, "host_session_id")
    expected = generation(args.expected_generation, "expected_generation")
    if args.retain_generations < 1:
        fail("retain_generations must preserve at least the current generation")
    resolved = {generation(item, "resolved_generation") for item in args.resolved_generation}
    if not resolved or not args.resolution_receipt:
        fail("GC requires closure-owner resolution evidence for every removable generation")
    exact_text(args.resolution_receipt, "resolution_receipt")
    with writer_lock(store):
        target, state = load_state(store, host_id, session_id)
        current = current_record(state, require_active=False)
        require_external_store(store, current)
        if current["binding_generation"] != expected:
            fail("expected binding generation does not match current generation")
        protected = {record["binding_generation"] for record in state["records"][-args.retain_generations :]}
        removed = sorted(
            record["binding_generation"]
            for record in state["records"]
            if record["binding_generation"] in resolved
            and record["binding_generation"] not in protected
            and record["status"] != "ACTIVE"
        )
        if removed:
            state["records"] = [record for record in state["records"] if record["binding_generation"] not in removed]
            atomic_json(target, state)
    emit(
        proof_result(
            status="GC_COMPLETE",
            removed_generations=removed,
            preserved_current_generation=current["binding_generation"],
            governed_state_deleted=False,
        )
    )


def add_binding_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--owner-id", required=True)
    parser.add_argument("--host-id", required=True)
    parser.add_argument("--host-session-id", required=True)
    parser.add_argument("--controller-id", required=True)
    parser.add_argument("--claim-id", required=True)
    parser.add_argument("--explicit-run-root", required=True)
    parser.add_argument("--repository-identity", required=True)
    parser.add_argument("--git-common-directory-identity", required=True)
    parser.add_argument("--worktree-identity", required=True)
    parser.add_argument("--activation-event-id", required=True)
    parser.add_argument("--activation-receipt", required=True)
    parser.add_argument("--continuity-generation", required=True)
    parser.add_argument("--continuity-receipt", required=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init")
    init.add_argument("--owner-id", required=True)
    init.set_defaults(run=command_init)

    bind = subparsers.add_parser("bind")
    add_binding_arguments(bind)
    bind.set_defaults(run=command_bind)

    rebind = subparsers.add_parser("rebind")
    add_binding_arguments(rebind)
    rebind.add_argument("--expected-generation", required=True)
    rebind.add_argument("--reason", required=True)
    rebind.set_defaults(run=command_rebind)

    lookup = subparsers.add_parser("lookup")
    lookup.add_argument("--host-id", required=True)
    lookup.add_argument("--host-session-id", required=True)
    lookup.set_defaults(run=command_lookup)

    event = subparsers.add_parser("validate-event")
    event.add_argument("--host-id", required=True)
    event.add_argument("--host-session-id", required=True)
    event.add_argument("--binding-generation", required=True)
    event.add_argument("--controller-id", required=True)
    event.add_argument("--claim-id", required=True)
    event.add_argument("--explicit-run-root", required=True)
    event.add_argument("--repository-identity", required=True)
    event.add_argument("--git-common-directory-identity", required=True)
    event.add_argument("--worktree-identity", required=True)
    event.add_argument("--continuity-generation", required=True)
    event.add_argument("--continuity-receipt", required=True)
    event.add_argument("--event-id", required=True)
    event.add_argument("--turn-id")
    event.add_argument("--tool-use-id")
    event.add_argument("--agent-id")
    event.add_argument("--obligation-id")
    event.add_argument("--route-transaction-id")
    event.set_defaults(run=command_validate_event)

    tombstone = subparsers.add_parser("tombstone")
    tombstone.add_argument("--owner-id", required=True)
    tombstone.add_argument("--host-id", required=True)
    tombstone.add_argument("--host-session-id", required=True)
    tombstone.add_argument("--expected-generation", required=True)
    tombstone.add_argument("--reason", required=True)
    tombstone.set_defaults(run=command_tombstone)

    gc = subparsers.add_parser("gc")
    gc.add_argument("--owner-id", required=True)
    gc.add_argument("--host-id", required=True)
    gc.add_argument("--host-session-id", required=True)
    gc.add_argument("--expected-generation", required=True)
    gc.add_argument("--retain-generations", type=int, required=True)
    gc.add_argument("--resolved-generation", action="append", default=[])
    gc.add_argument("--resolution-receipt")
    gc.set_defaults(run=command_gc)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.run(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
