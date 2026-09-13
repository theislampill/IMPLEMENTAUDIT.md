#!/usr/bin/env python3
"""Invalidate one H0-bound controller after a Codex compact SessionStart."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


RESULT_SCHEMA = "implementaudit.codex-compact-interlock-result.v1"
HOST_NAMESPACE = "codex"
STORE_DIRECTORY = "host-session-binding-v1"
MAX_INPUT_BYTES = 65536
MAX_TEXT = 1024
TOKEN_RE = re.compile(
    r"refs/implementaudit/(?P<family>continuity-(?:receipts|invalidations))/"
    r"(?P<controller>[a-z0-9-]{1,48})(?:/[A-Za-z0-9-]+)?@(?P<oid>[0-9a-f]{40})"
)


class InterlockUnavailable(RuntimeError):
    """The event cannot be attributed or invalidated without guessing."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value = dict(pairs)
    if len(value) != len(pairs):
        raise InterlockUnavailable("hook input contains a duplicate JSON member")
    return value


def emit(status: str, *, keep_running: bool, **extra: Any) -> None:
    payload: dict[str, Any] = {
        "schema": RESULT_SCHEMA,
        "status": status,
        "continue": keep_running,
    }
    if not keep_running:
        payload["stopReason"] = (
            "IMPLEMENTAUDIT continuity requires a fresh verified controller receipt."
        )
    payload.update(extra)
    sys.stdout.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")


def exact_text(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > MAX_TEXT
        or any(ord(character) < 32 for character in value)
    ):
        raise InterlockUnavailable(f"invalid {label}")
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


def fixed_bash() -> str:
    candidates = (
        (r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files\Git\usr\bin\bash.exe")
        if os.name == "nt"
        else ("/bin/bash", "/usr/bin/bash", "/usr/local/bin/bash")
    )
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file() and not path.is_symlink():
            return str(path)
    raise InterlockUnavailable("canonical Bash is unavailable")


def claim_environment() -> dict[str, str]:
    """Return a fixed host-substrate environment for claim-run Git reads/writes."""

    python_directory = str(Path(sys.executable).resolve().parent)
    if os.name == "nt":
        git_root = Path(r"C:\Program Files\Git")
        path_entries = (
            python_directory,
            str(git_root / "bin"),
            str(git_root / "usr" / "bin"),
            str(git_root / "mingw64" / "bin"),
            str(git_root / "cmd"),
        )
        system_root = r"C:\Windows"
        environment = {
            "PATH": os.pathsep.join((*path_entries, str(Path(system_root) / "System32"))),
            "SystemRoot": system_root,
            "WINDIR": system_root,
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


def run(
    command: list[str],
    *,
    cwd: str | None = None,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=30,
            env=environment,
        )
    except (OSError, UnicodeError, subprocess.SubprocessError) as error:
        raise InterlockUnavailable("subordinate validation is unavailable") from error


def json_result(result: subprocess.CompletedProcess[str], label: str) -> dict[str, Any]:
    if result.stderr or not result.stdout.endswith("\n") or "\n" in result.stdout[:-1]:
        raise InterlockUnavailable(f"{label} returned an invalid result")
    try:
        value = json.loads(result.stdout)
    except (TypeError, json.JSONDecodeError) as error:
        raise InterlockUnavailable(f"{label} returned malformed JSON") from error
    if not isinstance(value, dict):
        raise InterlockUnavailable(f"{label} returned the wrong shape")
    return value


def same_path(left: str, right: str) -> bool:
    return os.path.normcase(os.path.abspath(left)) == os.path.normcase(os.path.abspath(right))


def event_id(binding: dict[str, Any], session_id: str) -> str:
    identity = {
        "schema": "implementaudit.codex-compact-event.v1",
        "host_namespace": HOST_NAMESPACE,
        "host_session_id": session_id,
        "binding_generation": binding["binding_generation"],
        "continuity_generation": binding["applicable_continuity_generation"],
        "continuity_receipt": binding["applicable_continuity_receipt"],
        "source": "compact",
    }
    digest = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return f"codex-compact-v1-{digest}"


def recovery_capsule(compact_event_id: str) -> dict[str, Any]:
    """Describe the only substantive route admitted after this exact boundary."""
    prefix = "codex-compact-v1-"
    digest = compact_event_id.removeprefix(prefix)
    if not compact_event_id.startswith(prefix) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise InterlockUnavailable("compact event identity is malformed")
    body = {
        "schema": "implementaudit.post-compaction-recovery.v2",
        "event_id": compact_event_id,
        "event_digest": f"sha256:{digest}",
        "required_child": "audit-state",
        "mechanical_governor_actions": [
            "INVALIDATE",
            "MECHANICAL_CURRENTNESS",
            "OPEN_AUDIT_STATE",
        ],
        "governor_substantive_reconstruction": False,
        "return_kind": "MINIMUM_APPLICABLE_FRONTIER",
        "return_requires_governor_reconciliation": True,
        "stale_credit": False,
        "worker_context_disposition": "DISCARD_AFTER_RETURN",
    }
    return {
        **body,
        "capsule_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    }


def require_binding(store: Path, session_id: str, binding_core: Path) -> dict[str, Any] | None:
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


def validate_live_controller(binding: dict[str, Any], claim_helper: Path, bash: str) -> None:
    controller = exact_text(binding["controller_id"], "controller_id")
    repository = exact_text(binding["repository_identity"], "repository_identity")
    result = run(
        [bash, str(claim_helper), "--current-controller", controller],
        cwd=repository,
        environment=claim_environment(),
    )
    if result.returncode != 0 or result.stderr or not result.stdout.endswith("\n"):
        raise InterlockUnavailable("controller currentness is unavailable")
    fields = result.stdout[:-1].split("\t")
    if len(fields) != 4:
        raise InterlockUnavailable("controller currentness has the wrong shape")
    observed_controller, observed_repo, observed_root, observed_claim = fields
    if (
        observed_controller != controller
        or observed_claim != binding["claim_id"]
        or not same_path(observed_repo, repository)
        or not same_path(observed_root, binding["explicit_run_root"])
    ):
        raise InterlockUnavailable("controller currentness is stale or foreign")


def validate_event(
    store: Path,
    session_id: str,
    binding: dict[str, Any],
    binding_core: Path,
    compact_event_id: str,
) -> None:
    command = [
        sys.executable,
        str(binding_core),
        "--store",
        str(store),
        "validate-event",
        "--host-id",
        HOST_NAMESPACE,
        "--host-session-id",
        session_id,
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
        compact_event_id,
    ]
    result = run(command)
    value = json_result(result, "host event validation")
    if result.returncode != 0 or value.get("status") != "ATTRIBUTED":
        raise InterlockUnavailable("host event attribution is unavailable")


def invalidate(binding: dict[str, Any], claim_helper: Path, bash: str, compact_event_id: str) -> str:
    controller = binding["controller_id"]
    receipt = binding["applicable_continuity_receipt"]
    receipt_match = TOKEN_RE.fullmatch(receipt)
    if (
        receipt_match is None
        or receipt_match.group("family") != "continuity-receipts"
        or receipt_match.group("controller") != controller
        or receipt.rsplit("/", 1)[-1].split("@", 1)[0]
        != binding["applicable_continuity_generation"]
    ):
        raise InterlockUnavailable("binding continuity receipt is malformed")
    result = run(
        [
            bash,
            str(claim_helper),
            "--invalidate-continuity",
            controller,
            "--boundary",
            "host-reported-compaction",
            "--event",
            compact_event_id,
            "--expected-current",
            receipt,
        ],
        cwd=binding["repository_identity"],
        environment=claim_environment(),
    )
    if result.returncode != 0 or result.stderr or not result.stdout.endswith("\n"):
        raise InterlockUnavailable("continuity invalidation is unavailable")
    token = result.stdout[:-1]
    match = TOKEN_RE.fullmatch(token)
    if (
        match is None
        or match.group("family") != "continuity-invalidations"
        or match.group("controller") != controller
    ):
        raise InterlockUnavailable("continuity invalidation returned a foreign token")
    return token


def main() -> int:
    audit_pending = None
    try:
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise InterlockUnavailable("hook input is oversized")
        try:
            event = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
        except (UnicodeError, json.JSONDecodeError) as error:
            raise InterlockUnavailable("hook input is malformed") from error
        if not isinstance(event, dict):
            raise InterlockUnavailable("hook input has the wrong shape")
        if event.get("hook_event_name") != "SessionStart":
            raise InterlockUnavailable("hook event is foreign")
        source = event.get("source")
        if source in {"startup", "resume", "clear"}:
            emit("IGNORED", keep_running=True)
            return 0
        if source != "compact":
            raise InterlockUnavailable("SessionStart source is unsupported")
        session_id = exact_text(event.get("session_id"), "session_id")
        store = plugin_store()
        script_dir = Path(__file__).resolve().parent
        binding_core = script_dir / "host-session-binding.py"
        claim_helper = script_dir / "claim-run.sh"
        if not binding_core.is_file() or not claim_helper.is_file():
            raise InterlockUnavailable("installed owner scripts are unavailable")
        binding = require_binding(store, session_id, binding_core)
        if binding is None:
            emit("UNBOUND", keep_running=True)
            return 0
        # Persist the independent cognitive obligation before continuity can fail.
        # The old native capsule/currentness owner remains a separate gate below.
        pending_spec = importlib.util.spec_from_file_location(
            '_compact_audit_pending', script_dir / 'compaction-audit-pending.py')
        pending_owner = importlib.util.module_from_spec(pending_spec)
        pending_spec.loader.exec_module(pending_owner)
        audit_pending = pending_owner.record_signal(store, session_id, event)
        bash = fixed_bash()
        validate_live_controller(binding, claim_helper, bash)
        compact_event_id = event_id(binding, session_id)
        validate_event(store, session_id, binding, binding_core, compact_event_id)
        token = invalidate(binding, claim_helper, bash, compact_event_id)
        emit(
            "INVALIDATED",
            keep_running=False,
            invalidation=token,
            event_id=compact_event_id,
            recovery=recovery_capsule(compact_event_id),
            audit_state_required=audit_pending['audit_state_required'],
            audit_pending=audit_pending,
        )
    except (InterlockUnavailable, KeyError, TypeError, ValueError, OSError):
        emit("BLOCKED", keep_running=False, audit_state_required=True,
             audit_pending=audit_pending,
             pending_custody="RECORDED" if audit_pending is not None else "UNVERIFIED_RECONCILE_SIGNAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
