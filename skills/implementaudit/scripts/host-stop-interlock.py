#!/usr/bin/env python3
"""Translate one Codex Stop event into the governed H7A disposition check."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


RESULT_SCHEMA = "implementaudit.host-stop-interlock-result.v1"
HOST_NAMESPACE = "codex"
STORE_DIRECTORY = "host-session-binding-v1"
MAX_INPUT_BYTES = 65536
MAX_IDENTIFIER_BYTES = 1024
MAX_IGNORED_TEXT = 4096
REQUIRED_EVENT_KEYS = {
    "session_id",
    "turn_id",
    "hook_event_name",
    "stop_hook_active",
    "last_assistant_message",
}
OPTIONAL_EVENT_KEYS = {"cwd", "transcript_path", "permission_mode"}
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:@+\-]{0,1023}")
CLOSURE_MARKERS = {"AUDIT_COMPLETE", "IMPLEMENTAUDIT_RUN_COMPLETE"}
HANDOFF_MARKERS = {"AUDIT_HANDOFF", "ANDON_HANDOFF"}
PROOF_LAYERS = {
    "source_core": "PRESENT",
    "package": "UNVERIFIED",
    "install": "UNVERIFIED",
    "host_activation": "UNVERIFIED",
}
PROXIMAL_ARTIFACTS = {
    "context": "R0035_ACTION_CONTEXT.json",
    "request": "R0035_PROXIMAL_REQUEST.json",
    "projection": "R0035_PROXIMAL_PROJECTION.json",
    "token": "R0035_PROXIMAL_ADVANCE_TOKEN.json",
}


class InterlockUnavailable(RuntimeError):
    """The Stop event cannot be safely translated into an owner result."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value = dict(pairs)
    if len(value) != len(pairs):
        raise InterlockUnavailable("hook input contains a duplicate JSON member")
    return value


def emit(payload: dict[str, Any]) -> None:
    value = {
        "schema": RESULT_SCHEMA,
        "host_activation_proven": False,
        **payload,
    }
    sys.stdout.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def block(reason: str) -> None:
    emit(
        {
            "status": "BLOCK",
            "decision": "block",
            "disposition": "BLOCK",
            "active_audit_object": None,
            "reason": reason,
        }
    )


def exact_identifier(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value.encode("utf-8")) > MAX_IDENTIFIER_BYTES
        or IDENTIFIER.fullmatch(value) is None
    ):
        raise InterlockUnavailable(f"invalid {label}")
    return value


def ignored_text(value: Any, label: str) -> None:
    if (
        not isinstance(value, str)
        or len(value.encode("utf-8")) > MAX_IGNORED_TEXT
        or any(ord(character) < 32 for character in value)
    ):
        raise InterlockUnavailable(f"invalid {label}")


def assistant_message(value: Any) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value.encode("utf-8")) > MAX_INPUT_BYTES
        or any(ord(character) < 32 and character not in "\t\r\n" for character in value)
    ):
        raise InterlockUnavailable("invalid last_assistant_message")
    return value


def read_event() -> dict[str, Any]:
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise InterlockUnavailable("hook input is oversized")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise InterlockUnavailable("hook input is malformed") from error
    if (
        not isinstance(value, dict)
        or not REQUIRED_EVENT_KEYS.issubset(value)
        or not set(value).issubset(REQUIRED_EVENT_KEYS | OPTIONAL_EVENT_KEYS)
    ):
        raise InterlockUnavailable("hook input has the wrong shape")
    if value["hook_event_name"] != "Stop":
        raise InterlockUnavailable("hook event is foreign")
    exact_identifier(value["session_id"], "session_id")
    exact_identifier(value["turn_id"], "turn_id")
    if type(value["stop_hook_active"]) is not bool:
        raise InterlockUnavailable("invalid stop_hook_active")
    assistant_message(value["last_assistant_message"])
    for key in OPTIONAL_EVENT_KEYS & set(value):
        ignored_text(value[key], key)
    return value


def plugin_store() -> Path:
    raw = os.environ.get("PLUGIN_DATA")
    if (
        not raw
        or len(raw) > 4096
        or any(ord(character) < 32 for character in raw)
        or not Path(raw).is_absolute()
    ):
        raise InterlockUnavailable("PLUGIN_DATA is unavailable")
    return Path(raw) / STORE_DIRECTORY


def owner_environment() -> dict[str, str]:
    """Use only fixed host-substrate executables for owner validation."""

    python_directory = str(Path(sys.executable).resolve().parent)
    if os.name == "nt":
        git_root = Path(r"C:\Program Files\Git")
        entries = (
            python_directory,
            str(git_root / "bin"),
            str(git_root / "usr" / "bin"),
            str(git_root / "mingw64" / "bin"),
            str(git_root / "cmd"),
            r"C:\Windows\System32",
        )
        environment = {
            "PATH": os.pathsep.join(entries),
            "ProgramFiles": r"C:\Program Files",
            "ProgramFiles(x86)": r"C:\Program Files (x86)",
            "SystemRoot": r"C:\Windows",
            "WINDIR": r"C:\Windows",
        }
    else:
        environment = {
            "PATH": os.pathsep.join((python_directory, "/usr/local/bin", "/usr/bin", "/bin"))
        }
    environment.update(
        {
            "LC_ALL": "C",
            "LANG": "C",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    return environment


def run(command: list[str], *, cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            env=owner_environment(),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=30,
        )
    except (OSError, UnicodeError, subprocess.SubprocessError) as error:
        raise InterlockUnavailable("subordinate validation is unavailable") from error


def json_result(
    result: subprocess.CompletedProcess[str], label: str, *, permit_stderr: bool = False
) -> dict[str, Any]:
    if (
        (result.stderr and not permit_stderr)
        or not result.stdout.endswith("\n")
        or "\n" in result.stdout[:-1]
    ):
        raise InterlockUnavailable(f"{label} returned an invalid result")
    try:
        value = json.loads(result.stdout, object_pairs_hook=unique_object)
    except (TypeError, json.JSONDecodeError) as error:
        raise InterlockUnavailable(f"{label} returned malformed JSON") from error
    if not isinstance(value, dict):
        raise InterlockUnavailable(f"{label} returned the wrong shape")
    return value


def canonical_compiler_result(
    result: subprocess.CompletedProcess[str], label: str,
) -> dict[str, Any]:
    """Parse the compiler's established canonical no-LF JSON transport."""
    if result.stderr or not result.stdout or "\n" in result.stdout or "\r" in result.stdout:
        raise InterlockUnavailable(f"{label} returned an invalid result")
    try:
        value = json.loads(result.stdout, object_pairs_hook=unique_object)
    except (TypeError, json.JSONDecodeError) as error:
        raise InterlockUnavailable(f"{label} returned malformed JSON") from error
    if not isinstance(value, dict):
        raise InterlockUnavailable(f"{label} returned the wrong shape")
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    if result.stdout != canonical:
        raise InterlockUnavailable(f"{label} returned noncanonical JSON")
    return value


def owner_scripts() -> tuple[Path, Path, Path, Path]:
    script_directory = Path(__file__).resolve().parent
    binding = script_directory / "host-session-binding.py"
    route = script_directory / "route-transaction.py"
    evaluator = script_directory / "evaluate-turn-disposition.py"
    compiler = script_directory / "compile-work-graph.py"
    if not all(path.is_file() and not path.is_symlink() for path in (
            binding, route, evaluator, compiler)):
        raise InterlockUnavailable("installed owner scripts are unavailable")
    return binding, route, evaluator, compiler


def lookup_binding(store: Path, session_id: str, binding_core: Path) -> dict[str, Any] | None:
    result = run(
        [
            sys.executable,
            str(binding_core),
            "--store",
            str(store),
            "lookup",
            "--host-id",
            HOST_NAMESPACE,
            "--host-session-id",
            session_id,
        ]
    )
    value = json_result(result, "host binding lookup")
    if result.returncode == 0 and value.get("status") == "UNBOUND":
        return None
    if result.returncode != 0 or value.get("status") != "BOUND":
        raise InterlockUnavailable("host binding is unavailable")
    binding = value.get("binding")
    required = {
        "host_id",
        "host_session_id",
        "controller_id",
        "claim_id",
        "explicit_run_root",
        "repository_identity",
        "git_common_directory_identity",
        "worktree_identity",
        "binding_generation",
        "applicable_continuity_generation",
        "applicable_continuity_receipt",
    }
    if not isinstance(binding, dict) or not required.issubset(binding):
        raise InterlockUnavailable("host binding is incomplete")
    if binding["host_id"] != HOST_NAMESPACE or binding["host_session_id"] != session_id:
        raise InterlockUnavailable("host binding identity is foreign")
    return binding


def current_route(
    store: Path, binding: dict[str, Any], route_core: Path
) -> dict[str, Any]:
    result = run(
        [
            sys.executable,
            str(route_core),
            "admit-current",
            "--controller",
            binding["controller_id"],
            "--store",
            str(store),
            "--host-id",
            HOST_NAMESPACE,
            "--host-session-id",
            binding["host_session_id"],
            "--binding-generation",
            binding["binding_generation"],
        ],
        cwd=binding["repository_identity"],
    )
    value = json_result(result, "current route admission", permit_stderr=True)
    if result.returncode not in {0, 3} or value.get("status") != "CURRENT":
        raise InterlockUnavailable("current route admission is unavailable")
    expected_notice = (
        "CHILD_SKILL_ROUTE=NOT_REQUIRED\n"
        "No internal child is used because the exact current R0033 route is NOT_REQUIRED.\n"
    )
    if result.stderr not in {"", expected_notice}:
        raise InterlockUnavailable("current route admission returned foreign diagnostics")
    return value


def stop_event_id(event: dict[str, Any], binding: dict[str, Any]) -> str:
    identity = {
        "schema": "implementaudit.codex-stop-event.v1",
        "host_id": HOST_NAMESPACE,
        "host_session_id": event["session_id"],
        "turn_id": event["turn_id"],
        "binding_generation": binding["binding_generation"],
        "continuity_generation": binding["applicable_continuity_generation"],
        "continuity_receipt": binding["applicable_continuity_receipt"],
        "last_assistant_message_digest": "sha256:"
        + hashlib.sha256(event["last_assistant_message"].encode("utf-8")).hexdigest(),
    }
    digest = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return f"codex-stop-v1-{digest}"


def validate_event(
    store: Path,
    event: dict[str, Any],
    binding: dict[str, Any],
    route: dict[str, Any],
    binding_core: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    obligation = route.get("obligation_id")
    transaction = route.get("route_transaction_id")
    if (obligation is None) != (transaction is None):
        raise InterlockUnavailable("current route identities are incomplete")
    event_identity = stop_event_id(event, binding)
    command = [
        sys.executable,
        str(binding_core),
        "--store",
        str(store),
        "validate-event",
        "--host-id",
        HOST_NAMESPACE,
        "--host-session-id",
        event["session_id"],
        "--binding-generation",
        binding["binding_generation"],
        "--controller-id",
        binding["controller_id"],
        "--claim-id",
        binding["claim_id"],
        "--explicit-run-root",
        binding["explicit_run_root"],
        "--repository-identity",
        binding["repository_identity"],
        "--git-common-directory-identity",
        binding["git_common_directory_identity"],
        "--worktree-identity",
        binding["worktree_identity"],
        "--continuity-generation",
        binding["applicable_continuity_generation"],
        "--continuity-receipt",
        binding["applicable_continuity_receipt"],
        "--event-id",
        event_identity,
        "--turn-id",
        event["turn_id"],
    ]
    if obligation is not None:
        command.extend(["--obligation-id", obligation, "--route-transaction-id", transaction])
    result = run(command)
    value = json_result(result, "host event validation")
    if result.returncode != 0 or value.get("status") != "ATTRIBUTED":
        raise InterlockUnavailable("host event attribution is unavailable")
    correlation = {
        "host_id": HOST_NAMESPACE,
        "host_session_id": event["session_id"],
        "binding_generation": binding["binding_generation"],
        "controller_id": binding["controller_id"],
        "claim_id": binding["claim_id"],
        "explicit_run_root": binding["explicit_run_root"],
        "repository_identity": binding["repository_identity"],
        "git_common_directory_identity": binding["git_common_directory_identity"],
        "worktree_identity": binding["worktree_identity"],
        "applicable_continuity_generation": binding["applicable_continuity_generation"],
        "applicable_continuity_receipt": binding["applicable_continuity_receipt"],
        "event_id": event_identity,
        "turn_id": event["turn_id"],
        "tool_use_id": None,
        "agent_id": None,
        "obligation_id": obligation,
        "route_transaction_id": transaction,
    }
    return correlation, value


def _fixed_run_artifact(run_root: str, name: str) -> Path:
    root = Path(run_root)
    candidate = root / name
    try:
        absolute = candidate.absolute()
        resolved = candidate.resolve(strict=True)
        info = os.lstat(absolute)
    except (OSError, RuntimeError) as error:
        raise InterlockUnavailable(
            f"proximal action selection artifact {name} is unavailable"
        ) from error
    if (absolute != resolved or not stat.S_ISREG(info.st_mode)
            or stat.S_ISLNK(info.st_mode)
            or bool(getattr(info, "st_file_attributes", 0) & 0x400)
            or info.st_nlink != 1 or info.st_size > MAX_INPUT_BYTES):
        raise InterlockUnavailable(
            f"proximal action selection artifact {name} is unsafe"
        )
    return resolved


def current_proximal_selection(
    binding: dict[str, Any], compiler: Path,
) -> dict[str, Any]:
    root = Path(binding["explicit_run_root"])
    context = _fixed_run_artifact(
        binding["explicit_run_root"], PROXIMAL_ARTIFACTS["context"]
    )
    companion_names = [
        PROXIMAL_ARTIFACTS["request"], PROXIMAL_ARTIFACTS["projection"],
        PROXIMAL_ARTIFACTS["token"],
    ]
    present = [os.path.lexists(root / name) for name in companion_names]
    if any(present) and not all(present):
        raise InterlockUnavailable("proximal action selection artifacts are a partial set")
    command = [sys.executable, str(compiler), "--proximal-action-selection", str(context)]
    if all(present):
        command.extend(str(_fixed_run_artifact(binding["explicit_run_root"], name))
                       for name in companion_names)
    result = run(command, cwd=binding["repository_identity"])
    value = canonical_compiler_result(result, "proximal action selection")
    if result.returncode != 0 or value.get("schema") != "implementaudit.proximal-action-selection.v1":
        raise InterlockUnavailable("proximal action selection is unavailable")
    currentness = value.get("currentness")
    if (not isinstance(currentness, dict)
            or currentness.get("current") is not True
            or currentness.get("receipt") != binding["applicable_continuity_receipt"]):
        raise InterlockUnavailable("proximal action selection is stale or foreign")
    reason = value.get("applicability_reason")
    if not isinstance(reason, str) or not reason:
        raise InterlockUnavailable("proximal action selection has no derived reason")
    return value


def consume_proximal_selection(
    store: Path,
    event: dict[str, Any],
    binding: dict[str, Any],
    binding_core: Path,
    selection: dict[str, Any],
) -> dict[str, Any]:
    command = [
        sys.executable, str(binding_core), "--store", str(store),
        "consume-proximal-action", "--host-id", HOST_NAMESPACE,
        "--host-session-id", event["session_id"],
        "--binding-generation", binding["binding_generation"],
        "--controller-id", binding["controller_id"],
        "--claim-id", binding["claim_id"],
        "--explicit-run-root", binding["explicit_run_root"],
        "--repository-identity", binding["repository_identity"],
        "--git-common-directory-identity", binding["git_common_directory_identity"],
        "--worktree-identity", binding["worktree_identity"],
        "--continuity-generation", binding["applicable_continuity_generation"],
        "--continuity-receipt", binding["applicable_continuity_receipt"],
        "--event-id", stop_event_id(event, binding),
        "--turn-id", event["turn_id"],
        "--selection-json", json.dumps(
            selection, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ),
    ]
    result = run(command)
    value = json_result(result, "proximal action consumption")
    if result.returncode != 0 or value.get("status") != "PROXIMAL_ACTION_CONSUMED":
        raise InterlockUnavailable("proximal action selection was not consumed")
    return value


def classify_claim(message: str) -> str:
    lines = set(message.splitlines())
    has_closure = bool(lines & CLOSURE_MARKERS)
    has_handoff = bool(lines & HANDOFF_MARKERS)
    if has_closure and has_handoff:
        raise InterlockUnavailable("assistant output mixes terminal closure and handoff claims")
    if has_closure:
        return "TERMINAL_CLOSURE"
    if has_handoff:
        return "AUDITED_HANDOFF"
    return "NONTERMINAL_YIELD"


def evaluate(
    evaluator: Path,
    claim: str,
    binding: dict[str, Any],
    binding_result: dict[str, Any],
    route: dict[str, Any],
) -> dict[str, Any]:
    request = {
        "schema": "implementaudit.turn-disposition-request.v1",
        "claim": claim,
        "run_root": binding["explicit_run_root"],
        "binding": {"correlation": binding, "result": binding_result},
        "route": route,
    }
    with tempfile.TemporaryDirectory(prefix="implementaudit-stop-") as temporary:
        request_path = Path(temporary) / "request.json"
        request_path.write_text(
            json.dumps(request, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        result = run([sys.executable, str(evaluator), "--request", str(request_path)])
    value = json_result(result, "turn disposition")
    if result.returncode not in {0, 2, 3}:
        raise InterlockUnavailable("turn disposition is unavailable")
    return value


def translate(
    disposition: dict[str, Any],
    binding_result: dict[str, Any],
    route: dict[str, Any],
    proximal_result: dict[str, Any] | None,
) -> dict[str, Any]:
    if disposition.get("status") != "ALLOW":
        reason = disposition.get("reason")
        if not isinstance(reason, str) or not reason:
            raise InterlockUnavailable("turn disposition blocked without a reason")
        return {
            "status": "BLOCK",
            "decision": "block",
            "disposition": "BLOCK",
            "active_audit_object": disposition.get("active_audit_object"),
            "reason": reason,
        }
    if proximal_result is None:
        raise InterlockUnavailable(
            "proximal action selection is unavailable for an allowed turn"
        )
    return {
        "status": "ALLOW",
        "disposition": disposition["disposition"],
        "active_audit_object": disposition["active_audit_object"],
        "object_closed": disposition["object_closed"],
        "audited_handoff": disposition["audited_handoff"],
        "nonterminal_yield": disposition["nonterminal_yield"],
        "binding_generation": binding_result["binding_generation"],
        "correlation_id": binding_result["correlation_id"],
        "route_decision": route["decision"],
        "route_record_oid": route["record_oid"],
        "obligation_id": route["obligation_id"],
        "route_transaction_id": route["route_transaction_id"],
        "proximal_action_decision": proximal_result["decision"],
        "proximal_action_reason": proximal_result["applicability_reason"],
        "proximal_action_selection_digest": proximal_result["selection_digest"],
        "proof_layers": dict(PROOF_LAYERS),
    }


def main() -> int:
    try:
        event = read_event()
        if event["stop_hook_active"]:
            emit(
                {
                    "status": "REENTRY",
                    "disposition": "NONTERMINAL_YIELD",
                    "forced_exit_evidence": False,
                }
            )
            return 0
        store = plugin_store()
        binding_core, route_core, evaluator, compiler = owner_scripts()
        binding = lookup_binding(store, event["session_id"], binding_core)
        if binding is None:
            emit(
                {
                    "status": "UNBOUND",
                    "disposition": "NO_ACTIVE_AUDIT_OBJECT",
                    "active_audit_object": False,
                }
            )
            return 0
        route = current_route(store, binding, route_core)
        correlation, binding_result = validate_event(store, event, binding, route, binding_core)
        claim = classify_claim(event["last_assistant_message"])
        disposition = evaluate(evaluator, claim, correlation, binding_result, route)
        proximal_result = None
        if disposition.get("status") == "ALLOW":
            selection = current_proximal_selection(binding, compiler)
            proximal_result = consume_proximal_selection(
                store, event, binding, binding_core, selection
            )
        emit(translate(disposition, binding_result, route, proximal_result))
    except (InterlockUnavailable, KeyError, TypeError, ValueError) as error:
        block(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
