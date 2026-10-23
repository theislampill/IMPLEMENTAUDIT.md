#!/usr/bin/env python3
"""Read Stop attribution; refuse unsupported host-effect acceptance."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import types
from pathlib import Path
from typing import Any



RESULT_SCHEMA = "implementaudit.host-stop-interlock-result.v1"


HOST_NAMESPACE = "codex"


STORE_DIRECTORY = "host-session-binding-v1"


MAX_INPUT_BYTES = 65536


MAX_PROXIMAL_SELECTION_BYTES = 131072


MAX_IDENTIFIER_BYTES = 1024


MAX_IGNORED_TEXT = 4096


REQUIRED_EVENT_KEYS = {
    "session_id",
    "turn_id",
    "hook_event_name",
    "stop_hook_active",
    "last_assistant_message",
}


OPTIONAL_EVENT_KEYS = {"cwd", "transcript_path", "model", "permission_mode", "abnormality_cognition"}


IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:@+\-]{0,1023}")


class InterlockUnavailable(RuntimeError):
    """The Stop event cannot be safely translated into an owner result."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value = dict(pairs)
    if len(value) != len(pairs):
        raise InterlockUnavailable("hook input contains a duplicate JSON member")
    return value


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
    if value["last_assistant_message"] is not None:
        assistant_message(value["last_assistant_message"])
    for key in {"cwd", "transcript_path", "model", "permission_mode"} & set(value):
        if key == "transcript_path" and value[key] is None:
            continue
        ignored_text(value[key], key)
    return value


def exact_installed_path(raw: str, *, directory: bool) -> Path:
    """Use the recovery input adapter's physical, non-aliased path contract."""
    if (not isinstance(raw, str) or not raw or len(raw) > 4096
            or any(ord(character) < 32 for character in raw)):
        raise InterlockUnavailable("installed path is unavailable")
    path = Path(raw)
    if not path.is_absolute():
        raise InterlockUnavailable("installed path is not absolute")
    try:
        resolved = path.resolve(strict=True)
        info = path.stat()
    except (OSError, RuntimeError) as error:
        raise InterlockUnavailable("installed path is unavailable") from error
    if (os.path.normcase(str(path)) != os.path.normcase(str(resolved))
            or path.is_symlink()
            or getattr(info, "st_file_attributes", 0) & 0x400
            or (not stat.S_ISDIR(info.st_mode) if directory
                else not stat.S_ISREG(info.st_mode))):
        raise InterlockUnavailable("installed path is aliased or unsafe")
    return path


def plugin_store() -> Path:
    """Bind H0 to both physical owner components, never a flattened name."""
    if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
        raise InterlockUnavailable("isolated fixed hook invocation required")
    script = exact_installed_path(str(Path(__file__).absolute()), directory=False)
    root = exact_installed_path(os.environ.get("PLUGIN_ROOT"), directory=True)
    if root != script.parents[3]:
        raise InterlockUnavailable("PLUGIN_ROOT differs from executing handler")
    plugin, marketplace, cache, plugins = (
        root.parent, root.parent.parent, root.parent.parent.parent,
        root.parent.parent.parent.parent,
    )
    if cache.name != "cache" or plugins.name != "plugins":
        raise InterlockUnavailable("installed cache identity is invalid")
    if not all(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name)
               for name in (marketplace.name, plugin.name)):
        raise InterlockUnavailable("installed owner component is invalid")
    # Same owner mapping as codex-recovery-prompt-input.py. Native scratch
    # names may collide; the physical marketplace/plugin pair cannot be
    # inferred from that flattened string and remains the H0 authority key.
    owner_data = plugins / "data" / marketplace.name / plugin.name
    native_data = plugins / "data" / (plugin.name + "-" + marketplace.name)
    raw_data = os.environ.get("PLUGIN_DATA")
    if raw_data not in (str(owner_data), str(native_data)):
        raise InterlockUnavailable("PLUGIN_DATA differs from physical owner")
    def optional_directory(path: Path) -> Path:
        # An ordinary session need not have created plugin data. Validate the
        # physical existing ancestor without creating or enumerating anything.
        ancestor = path
        while not os.path.lexists(ancestor):
            parent = ancestor.parent
            if parent == ancestor:
                raise InterlockUnavailable("installed data ancestor is unavailable")
            ancestor = parent
        exact_installed_path(str(ancestor), directory=True)
        try:
            resolved = path.resolve(strict=False)
        except (OSError, RuntimeError) as error:
            raise InterlockUnavailable("installed data path is unavailable") from error
        if os.path.normcase(str(path)) != os.path.normcase(str(resolved)):
            raise InterlockUnavailable("installed data path is aliased")
        return path

    optional_directory(Path(raw_data))
    return optional_directory(owner_data / STORE_DIRECTORY)


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


def consume_proximal_selection(
    store: Path,
    event: dict[str, Any],
    binding: dict[str, Any],
    binding_core: Path,
    selection: dict[str, Any],
) -> dict[str, Any]:
    """Mechanical custody API only; native Stop never calls this operation."""
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
    ]
    canonical = json.dumps(
        selection, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    if len(canonical.encode("utf-8")) > MAX_PROXIMAL_SELECTION_BYTES:
        raise InterlockUnavailable("proximal action selection transport is oversized")
    result = run_binding_core(binding_core, command[2:], input_text=canonical)
    value = json_result(result, "proximal action consumption")
    if result.returncode != 0 or value.get("status") != "PROXIMAL_ACTION_CONSUMED":
        raise InterlockUnavailable("proximal action selection was not consumed")
    return value


BINDING_CORE_SHA256 = '8b4f91a51e2e2d45c4bd72b58fb1e115981903f8a752f95eb71cda64b106b6ef'
MAX_CORE_BYTES = 131072


def emit(payload: dict[str, Any]) -> None:
    value = {"schema": RESULT_SCHEMA, **payload, "host_activation_proven": False,
             "enforcement_available": False, "effect_accepted": False}
    print(json.dumps(value, sort_keys=True, separators=(",", ":")))


def load_binding_core(path: Path):
    """Compile exactly one buffer selected by this owner's fixed source pin."""
    expected_path = Path(__file__).absolute().parent / "host-session-binding.py"
    if path != expected_path:
        raise InterlockUnavailable("foreign binding source member")
    for node in (path, *path.parents):
        info = node.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise InterlockUnavailable("aliased binding source")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0))
    with os.fdopen(fd, "rb") as handle:
        before = os.fstat(handle.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > MAX_CORE_BYTES:
            raise InterlockUnavailable("unsafe binding source")
        raw = handle.read(MAX_CORE_BYTES + 1)
        after = os.fstat(handle.fileno())
    if (len(raw) > MAX_CORE_BYTES or before.st_size != len(raw)
            or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
               (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            or hashlib.sha256(raw).hexdigest() != BINDING_CORE_SHA256):
        raise InterlockUnavailable("binding source differs from selected owner")
    module = types.ModuleType("r003a_stop_binding_core")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec", dont_inherit=True), module.__dict__)
    return module


def run_binding_core(path: Path, arguments: list[str], *, input_text: str = ""):
    module = load_binding_core(path)
    output = io.StringIO()
    old_argv, old_stdin = sys.argv, sys.stdin
    try:
        sys.argv = [str(path), *arguments]
        sys.stdin = io.TextIOWrapper(io.BytesIO(input_text.encode("utf-8")), encoding="utf-8")
        with contextlib.redirect_stdout(output):
            try:
                code = module.main()
            except SystemExit as error:
                code = error.code
    finally:
        sys.argv, sys.stdin = old_argv, old_stdin
    return subprocess.CompletedProcess(arguments, code, output.getvalue(), "")


def main() -> int:
    try:
        event = read_event()
        store = plugin_store()
        if not os.path.lexists(store):
            emit({"status": "UNBOUND", "disposition": "NO_ACTIVE_AUDIT_OBJECT",
                  "active_audit_object": False})
            return 0
        result = run_binding_core(Path(__file__).absolute().parent / "host-session-binding.py",
            ["--store", str(store), "lookup", "--host-id", HOST_NAMESPACE,
             "--host-session-id", event["session_id"]])
        value = json_result(result, "host binding lookup")
        if result.returncode == 0 and value.get("status") == "UNBOUND":
            emit({"status": "UNBOUND", "disposition": "NO_ACTIVE_AUDIT_OBJECT",
                  "active_audit_object": False})
            return 0
        # No supported issuer/grant verifier is selected for this host. Readable
        # attribution, purpose labels, reentry flags and historical receipts
        # cannot authorize a current dependent effect. Do not call route,
        # compiler, disposition, consumption or lifecycle owners here.
        raise InterlockUnavailable("UNSUPPORTED_HOST_EFFECT_AUTHENTICATION")
    except (InterlockUnavailable, OSError, RuntimeError, KeyError, TypeError, ValueError) as error:
        emit({"status": "UNAVAILABLE", "decision": "block", "disposition": "BLOCK",
              "active_audit_object": None, "reason": str(error)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

