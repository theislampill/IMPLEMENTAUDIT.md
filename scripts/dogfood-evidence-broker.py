#!/usr/bin/env python3
"""Closed RC self-dogfood read broker and runner-owned evidence emitter."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import subprocess
import sys
from pathlib import Path


SCHEMA = "implementaudit.dogfood-event.v1"
ZERO_ID = "0" * 64
HEX40 = re.compile(r"^[a-f0-9]{40}$")
HEX64 = re.compile(r"^[a-f0-9]{64}$")


def fail(message: str) -> "NoReturn":
    raise SystemExit(f"dogfood-evidence-broker: {message}")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: dict[str, object]) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def strict_json_loads(raw: str) -> dict[str, object]:
    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        value: dict[str, object] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def emit_text(value: str) -> None:
    if value:
        sys.stdout.buffer.write(value.encode("utf-8"))
        if not value.endswith("\n"):
            sys.stdout.buffer.write(b"\n")


def require_hex(value: str, pattern: re.Pattern[str], name: str) -> str:
    if not pattern.fullmatch(value):
        fail(f"{name} has invalid identity syntax")
    return value


def exclusive_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        os.write(descriptor, data)
    finally:
        os.close(descriptor)


def load_context(path: Path) -> dict[str, object]:
    try:
        context = strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        fail(f"cannot read context {path}: {exc}")
    if context.get("schema") != "implementaudit.dogfood-broker-context.v1":
        fail("context schema mismatch")
    return context


def load_key(context: dict[str, object]) -> bytes:
    key_path = Path(str(context["key_file"]))
    try:
        key = bytes.fromhex(key_path.read_text(encoding="ascii").strip())
    except (OSError, ValueError) as exc:
        fail(f"cannot read runner key: {exc}")
    if len(key) != 32:
        fail("runner key must be 32 bytes")
    return key


def existing_events(context: dict[str, object], key: bytes) -> list[dict[str, object]]:
    journal = Path(str(context["journal"]))
    if not journal.is_file():
        fail("runner journal is missing")
    events: list[dict[str, object]] = []
    previous = ZERO_ID
    for line_number, raw in enumerate(journal.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            event = strict_json_loads(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            fail(f"journal line {line_number} is invalid JSON: {exc}")
        signature = event.pop("hmac_sha256", None)
        expected = hmac.new(key, canonical(event), hashlib.sha256).hexdigest()
        event["hmac_sha256"] = signature
        if not isinstance(signature, str) or not hmac.compare_digest(signature, expected):
            fail(f"journal line {line_number} has invalid HMAC")
        if event.get("sequence") != len(events) + 1:
            fail(f"journal line {line_number} is out of sequence")
        if event.get("previous_event_id") != previous:
            fail(f"journal line {line_number} breaks the event chain")
        previous = str(event.get("event_id"))
        events.append(event)
    return events


def append_event(
    context: dict[str, object],
    *,
    actor: str,
    action: str,
    target_role: str,
    phase: str,
    result: str,
    correlation_id: str,
    target_identity: str,
    target_path: str | None = None,
    content_sha256: str | None = None,
) -> dict[str, object]:
    key = load_key(context)
    events = existing_events(context, key)
    sequence = len(events) + 1
    previous = str(events[-1]["event_id"]) if events else ZERO_ID
    base: dict[str, object] = {
        "schema": SCHEMA,
        "session_id": context["session_id"],
        "sequence": sequence,
        "previous_event_id": previous,
        "correlation_id": correlation_id,
        "actor": actor,
        "action": action,
        "target_role": target_role,
        "phase": phase,
        "result": result,
        "candidate_commit": context["candidate_commit"],
        "candidate_tree": context["candidate_tree"],
        "package_sha256": context["package_sha256"],
        "runtime_sha256": context["runtime_sha256"],
        "target_identity": target_identity,
    }
    if target_path is not None:
        base["target_path"] = target_path
    if content_sha256 is not None:
        base["content_sha256"] = content_sha256
    base["event_id"] = hashlib.sha256(
        canonical(base) + secrets.token_bytes(16)
    ).hexdigest()
    base["hmac_sha256"] = hmac.new(key, canonical(base), hashlib.sha256).hexdigest()
    journal = Path(str(context["journal"]))
    with journal.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(base, ensure_ascii=True, separators=(",", ":"), sort_keys=True))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    return base


def completed_actions(context: dict[str, object]) -> set[str]:
    events = existing_events(context, load_key(context))
    return {
        str(event["action"])
        for event in events
        if event.get("result") == "completed"
    }


def phase(context: dict[str, object]) -> str:
    actions = completed_actions(context)
    return (
        "post-baseline"
        if {"baseline-status", "baseline-head"}.issubset(actions)
        else "pre-baseline"
    )


def is_real_home_runtime(path: Path) -> bool:
    parts = tuple(part.casefold() for part in path.resolve(strict=False).parts)
    real_home_root = (".codex", "skills", "implementaudit")
    return any(
        parts[index : index + len(real_home_root)] == real_home_root
        for index in range(len(parts) - len(real_home_root) + 1)
    )


def path_role(context: dict[str, object], path: Path) -> str:
    resolved = path.resolve(strict=False)
    source_root = Path(str(context["source_root"])).resolve()
    runtime_root = Path(str(context["runtime_root"])).resolve()
    if is_real_home_runtime(resolved):
        return "real-home-runtime"
    try:
        resolved.relative_to(runtime_root)
        return "temp-installed-runtime"
    except ValueError:
        pass
    try:
        resolved.relative_to(source_root)
        return "source"
    except ValueError:
        pass
    return "other"


def cmd_init(args: argparse.Namespace) -> None:
    if args.audit_object != "implementaudit-rc-self-release":
        fail("SELF_DOGFOOD_TRIGGER requires exact implementaudit-rc-self-release object")
    candidate = require_hex(args.candidate_commit, HEX40, "candidate commit")
    tree = require_hex(args.candidate_tree, HEX40, "candidate tree")
    package = require_hex(args.package_sha256, HEX64, "package SHA-256")
    runtime = require_hex(args.runtime_sha256, HEX64, "runtime SHA-256")
    context_path = Path(args.context).resolve()
    journal_path = Path(args.journal).resolve()
    key_path = Path(args.key_file).resolve()
    source_root = Path(args.source_root).resolve(strict=True)
    runtime_root = Path(args.runtime_root).resolve(strict=True)
    if is_real_home_runtime(runtime_root):
        fail("installed runtime root must not be a real-home runtime")
    if source_root == runtime_root:
        fail("source and installed runtime roots must be disjoint")
    for candidate_root, containing_root in (
        (source_root, runtime_root),
        (runtime_root, source_root),
    ):
        try:
            candidate_root.relative_to(containing_root)
        except ValueError:
            continue
        fail("source and installed runtime roots must be disjoint")
    custody_paths = (context_path, journal_path, key_path)
    if len(set(custody_paths)) != len(custody_paths):
        fail("context, journal, and key paths must be distinct")
    for custody_path in custody_paths:
        for readable_root in (source_root, runtime_root):
            try:
                custody_path.relative_to(readable_root)
            except ValueError:
                continue
            fail("runner custody must remain outside model-readable source/runtime roots")
    reference = runtime_root / "references" / "transcript-contract.md"
    runtime_carrier = runtime_root / "SKILL.md"
    broker = Path(__file__).resolve()
    event_schema = source_root / "fixtures" / "dogfood-bootstrap" / "typed-event.schema.json"
    for name, path in (
        ("installed runtime carrier", runtime_carrier),
        ("dogfood reference", reference),
        ("broker", broker),
        ("event schema", event_schema),
    ):
        if not path.is_file():
            fail(f"{name} is missing: {path}")
    if sha256_file(runtime_carrier) != runtime:
        fail("installed runtime carrier identity mismatch")
    if context_path.exists() or journal_path.exists() or key_path.exists():
        fail("context, journal, and key are create-once runner custody")
    key = secrets.token_bytes(32)
    exclusive_write(key_path, key.hex().encode("ascii") + b"\n")
    exclusive_write(journal_path, b"")
    context = {
        "schema": "implementaudit.dogfood-broker-context.v1",
        "session_id": args.session_id,
        "audit_object": args.audit_object,
        "candidate_commit": candidate,
        "candidate_tree": tree,
        "package_sha256": package,
        "runtime_sha256": runtime,
        "source_root": str(source_root),
        "runtime_root": str(runtime_root),
        "runtime_carrier": str(runtime_carrier),
        "journal": str(journal_path),
        "key_file": str(key_path),
    }
    exclusive_write(context_path, canonical(context) + b"\n")
    append_event(
        context,
        actor="runner",
        action="self-dogfood-trigger",
        target_role="self-release-audit-object",
        phase="pre-baseline",
        result="completed",
        correlation_id="self-dogfood-trigger",
        target_identity=f"{candidate}:{tree}",
    )
    for action, role, path in (
        ("load-reference", "dogfood-reference", reference),
        ("load-broker", "dogfood-broker", broker),
        ("load-event-schema", "dogfood-event-schema", event_schema),
    ):
        append_event(
            context,
            actor="runner",
            action=action,
            target_role=role,
            phase="pre-baseline",
            result="completed",
            correlation_id=action,
            target_identity=sha256_file(path),
            target_path=str(path),
            content_sha256=sha256_file(path),
        )


def run_git(context: dict[str, object], action: str, command: list[str]) -> None:
    source_root = Path(str(context["source_root"]))
    completed = subprocess.run(
        command,
        cwd=source_root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = completed.stdout.rstrip("\n")
    result = "completed" if completed.returncode == 0 else "blocked"
    if action == "baseline-head" and output != context["candidate_commit"]:
        result = "blocked"
    append_event(
        context,
        actor="runner",
        action=action,
        target_role="source",
        phase="pre-baseline",
        result=result,
        correlation_id=action,
        target_identity=hashlib.sha256(output.encode("utf-8")).hexdigest(),
        target_path=str(source_root),
        content_sha256=hashlib.sha256(output.encode("utf-8")).hexdigest(),
    )
    if output:
        emit_text(output)
    if result != "completed":
        fail(f"{action} did not complete against the externally bound candidate")


def cmd_activate(args: argparse.Namespace) -> None:
    context = load_context(Path(args.context))
    actions = completed_actions(context)
    if not {"baseline-status", "baseline-head"}.issubset(actions):
        fail("temp runtime activation is not permitted before both baseline events")
    path = Path(args.path).resolve(strict=True)
    runtime_carrier = Path(str(context["runtime_carrier"])).resolve(strict=True)
    role = path_role(context, path)
    digest = sha256_file(path)
    result = (
        "completed"
        if (
            role == "temp-installed-runtime"
            and path == runtime_carrier
            and digest == context["runtime_sha256"]
        )
        else "blocked"
    )
    append_event(
        context,
        actor="host",
        action="activate-runtime",
        target_role=role,
        phase="post-baseline",
        result=result,
        correlation_id="activate-runtime",
        target_identity=digest,
        target_path=str(path),
        content_sha256=digest,
    )
    if result != "completed":
        fail("runtime activation identity or target role mismatch")


def read_target(args: argparse.Namespace, action: str) -> None:
    context = load_context(Path(args.context))
    requested = Path(args.path)
    path = requested if requested.is_absolute() else Path(str(context["source_root"])) / requested
    resolved_for_gate = path.resolve(strict=False)
    actions = completed_actions(context)
    current_phase = phase(context)
    if not {"baseline-status", "baseline-head", "activate-runtime"}.issubset(actions):
        append_event(
            context,
            actor="model",
            action=action,
            target_role=path_role(context, resolved_for_gate),
            phase=current_phase,
            result="blocked",
            correlation_id=args.correlation_id,
            target_identity="precondition-denied",
            target_path=str(resolved_for_gate),
        )
        fail("model read/search is not permitted before baseline and temp-runtime activation")
    try:
        resolved = path.resolve(strict=True)
    except OSError:
        resolved = path.resolve(strict=False)
        append_event(
            context,
            actor="model",
            action=action,
            target_role=path_role(context, resolved),
            phase="post-baseline",
            result="blocked",
            correlation_id=args.correlation_id,
            target_identity="missing",
            target_path=str(resolved),
        )
        fail("target is missing")
    role = path_role(context, resolved)
    if role not in {"source", "temp-installed-runtime"} or not resolved.is_file():
        append_event(
            context,
            actor="model",
            action=action,
            target_role=role,
            phase="post-baseline",
            result="blocked",
            correlation_id=args.correlation_id,
            target_identity="rejected-target",
            target_path=str(resolved),
        )
        fail("target is outside the bounded source/temp-runtime roots")
    digest = sha256_file(resolved)
    text = resolved.read_text(encoding="utf-8")
    if action == "search":
        matches = [
            f"{index}:{line}"
            for index, line in enumerate(text.splitlines(), 1)
            if args.fixed_string in line
        ]
        output = "\n".join(matches)
    else:
        output = text
    append_event(
        context,
        actor="model",
        action=action,
        target_role=role,
        phase="post-baseline",
        result="completed",
        correlation_id=args.correlation_id,
        target_identity=digest,
        target_path=str(resolved),
        content_sha256=digest,
    )
    if output:
        emit_text(output)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    for name in (
        "context",
        "journal",
        "key-file",
        "session-id",
        "audit-object",
        "candidate-commit",
        "candidate-tree",
        "package-sha256",
        "runtime-sha256",
        "source-root",
        "runtime-root",
    ):
        init.add_argument(f"--{name}", required=True)
    init.set_defaults(handler=cmd_init)
    for name, command in (
        ("baseline-status", ["git", "status", "--short", "--branch", "--untracked-files=all"]),
        ("baseline-head", ["git", "rev-parse", "HEAD"]),
    ):
        sub = commands.add_parser(name)
        sub.add_argument("--context", required=True)
        sub.set_defaults(handler=lambda args, n=name, c=command: run_git(load_context(Path(args.context)), n, c))
    activate = commands.add_parser("activate")
    activate.add_argument("--context", required=True)
    activate.add_argument("--path", required=True)
    activate.set_defaults(handler=cmd_activate)
    read = commands.add_parser("read")
    read.add_argument("--context", required=True)
    read.add_argument("--path", required=True)
    read.add_argument("--correlation-id", required=True)
    read.set_defaults(handler=lambda args: read_target(args, "read"))
    search = commands.add_parser("search")
    search.add_argument("--context", required=True)
    search.add_argument("--path", required=True)
    search.add_argument("--fixed-string", required=True)
    search.add_argument("--correlation-id", required=True)
    search.set_defaults(handler=lambda args: read_target(args, "search"))
    return root


def main() -> None:
    args = parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
