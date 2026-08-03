#!/usr/bin/env python3
"""Finite, replayable host content-read evidence boundary.

The supported surface is intentionally small: mechanically profiled POSIX
commands for Codex plus native Claude Read/Write/Edit/Grep/Glob/Skill actions.
Unsupported syntax and incomplete provenance fail closed.  Process access and
model-visible full-preimage delivery are recorded separately.
"""
from __future__ import annotations

import base64
import hashlib
import json
import math
import os
import re
import shlex
import stat
import subprocess
from pathlib import PurePosixPath


PROFILE_SCHEMA = "implementaudit-host-read-profile-v2"
PREIMAGE_SCHEMA = "implementaudit-host-read-preimages-v1"
TRACE_SCHEMA = "implementaudit-host-tool-trace-v2"
MATRIX_SCHEMA = "implementaudit-host-read-matrix-v1"
PRESPAWN_SCHEMA = "implementaudit-host-read-pre-spawn-v1"
TERMINAL_SCHEMA = "implementaudit-host-read-terminal-v1"
MANIFEST_SCHEMA = "implementaudit-host-read-manifest-v1"
REPLAY_SCHEMA = "implementaudit-host-read-replay-spec-v1"
# Twelve hash-deduplicated retained native sessions have a maximum observed
# turn offset of 9.242 seconds from the whole-second process-start receipt.
# The declared whole-second ceiling is therefore ceil(9.242) == 10 seconds.
CODEX_SESSION_START_WINDOW_SECONDS = 10
# Formal process custody always binds these nonempty identities. Native-session
# corroboration therefore requires both sources instead of inferring optional
# mode from whichever fields happen to be present.
CODEX_REQUIRED_PROCESS_IDENTITY_FIELDS = frozenset(("cwd", "requested_model"))
CODEX_REQUIRED_TURN_IDENTITY_FIELDS = frozenset(("cwd", "model", "turn_id"))
CODEX_NATIVE_REPO_FIELDS = frozenset(
    ("lexical_root", "real_root", "case_sensitive"))
CODEX_NATIVE_PAYLOAD_FIELDS = {
    "session_meta": (
        frozenset(("id", "session_id", "cwd")),
        frozenset((
            "originator", "cli_version", "source", "thread_source",
            "model_provider", "git", "base_instructions",
            "developer_instructions", "dynamic_tools", "reasoning_effort",
            "history_mode", "context_window", "timestamp",
        )),
    ),
    "turn_context": (
        frozenset(("turn_id", "cwd")),
        frozenset((
            "workspace_roots", "current_date", "timezone", "approval_policy",
            "approvals_reviewer", "sandbox_policy", "permission_profile",
            "file_system_sandbox_policy", "model", "comp_hash",
            "personality", "collaboration_mode", "multi_agent_version",
            "realtime_active", "effort", "summary", "service_tier",
        )),
    ),
    "response_item": (
        frozenset(),
        frozenset((
            "type", "action_ids", "role", "content", "id", "status", "name",
            "arguments", "call_id", "summary", "message", "phase", "text",
            "images", "encrypted_content", "input", "output",
            "internal_chat_message_metadata_passthrough",
        )),
    ),
    "event_msg": (
        frozenset(),
        frozenset((
            "type", "action_ids", "role", "content", "id", "status", "name",
            "arguments", "call_id", "summary", "message", "phase", "text",
            "images", "encrypted_content", "changes",
            "collaboration_mode_kind", "completed_at", "duration_ms", "info",
            "last_agent_message", "local_images", "memory_citation",
            "model_context_window", "rate_limits", "started_at", "stderr",
            "stdout", "success", "text_elements", "time_to_first_token_ms",
            "turn_id",
        )),
    ),
    "world_state": (
        frozenset(("state", "full")),
        frozenset(),
    ),
}
CODEX_COLLAB_NATIVE_TOOL_NAMES = frozenset((
    "spawn_agent", "wait_agent", "send_input", "close_agent",
    "send_message", "resume_agent", "followup_task", "interrupt_agent",
    "list_agents",
))
CODEX_COLLAB_NATIVE_CHILD_ID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE)

SUPPORTED_READERS = ("cat", "grep", "head", "rg", "sed", "tail")
SUPPORTED_CLAUDE = frozenset(
    ("Read", "Write", "Edit", "Bash", "Grep", "Glob", "Skill",
     "Task", "Workflow"))
MAX_JSON_DEPTH = 512


_PROFILE_CAPABILITY = object()


def _immutable_profile_value(*_args, **_kwargs):
    raise TypeError("formal profile is immutable")


class _FrozenList(list):
    def __init__(self, *_args, **_kwargs):
        raise TypeError("formal profile is immutable")

    @classmethod
    def _create(cls, value):
        result = list.__new__(cls)
        list.__init__(result, (_freeze_profile_value(item) for item in value))
        return result

    __setitem__ = _immutable_profile_value
    __delitem__ = _immutable_profile_value
    __iadd__ = _immutable_profile_value
    __imul__ = _immutable_profile_value
    append = _immutable_profile_value
    clear = _immutable_profile_value
    extend = _immutable_profile_value
    insert = _immutable_profile_value
    pop = _immutable_profile_value
    remove = _immutable_profile_value
    reverse = _immutable_profile_value
    sort = _immutable_profile_value


class _FrozenDict(dict):
    def __init__(self, *_args, **_kwargs):
        raise TypeError("formal profile is immutable")

    @classmethod
    def _create(cls, value):
        result = dict.__new__(cls)
        dict.__init__(result)
        for key, item in value.items():
            dict.__setitem__(result, key, _freeze_profile_value(item))
        return result

    __setitem__ = _immutable_profile_value
    __delitem__ = _immutable_profile_value
    __ior__ = _immutable_profile_value
    clear = _immutable_profile_value
    pop = _immutable_profile_value
    popitem = _immutable_profile_value
    setdefault = _immutable_profile_value
    update = _immutable_profile_value


def _freeze_profile_value(value):
    if isinstance(value, dict):
        return _FrozenDict._create(value)
    if isinstance(value, list):
        return _FrozenList._create(value)
    return value


class _MintedProfile(_FrozenDict):
    """Process-local capability returned only by mechanical profile minting.

    Persisted JSON is promoted back to this type only after replay verifies the
    pre-spawn and parent custody chain.  A caller-created dictionary therefore
    cannot grant itself formal authority by copying the serialized marker.
    """

    @classmethod
    def _create(cls, value, capability=None):
        if capability is not _PROFILE_CAPABILITY:
            raise TypeError("formal profile capability is internal")
        result = dict.__new__(cls)
        dict.__init__(result)
        for key, item in value.items():
            dict.__setitem__(result, key, _freeze_profile_value(item))
        return result


def _mint_profile(value):
    return _MintedProfile._create(value, _PROFILE_CAPABILITY)


def _canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _strict_object(line):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError(f"non-finite JSON number {value}")

    try:
        value = json.loads(
            line, object_pairs_hook=unique, parse_constant=nonfinite)
    except (RecursionError, MemoryError) as exc:
        raise ValueError("host event exceeds JSON resource limits") from exc
    if not isinstance(value, dict):
        raise ValueError("host event is not a JSON object")
    pending = [(value, 0)]
    while pending:
        current, depth = pending.pop()
        if isinstance(current, dict):
            if depth >= MAX_JSON_DEPTH:
                raise ValueError("host event exceeds JSON depth limit")
            pending.extend((child, depth + 1)
                           for child in current.values())
        elif isinstance(current, list):
            if depth >= MAX_JSON_DEPTH:
                raise ValueError("host event exceeds JSON depth limit")
            pending.extend((child, depth + 1) for child in current)
        elif current is None or type(current) in (str, bool, int):
            continue
        elif type(current) is float and math.isfinite(current):
            continue
        else:
            raise ValueError("host event contains invalid JSON scalar")
    return value


def _valid_codex_lifecycle_shape(event):
    event_type = event.get("type")
    if event_type == "thread.started":
        return (
            set(event) == {"type", "thread_id"} and
            type(event["thread_id"]) is str and bool(event["thread_id"]))
    if event_type in ("turn.started", "turn.completed"):
        optional = {"thread_id", "turn_id"}
        if event_type == "turn.completed":
            optional.add("usage")
        if (not {"type"} <= set(event) or
                not set(event) <= {"type"} | optional):
            return False
        identities_valid = all(
            type(event[field]) is str and bool(event[field])
            for field in ("thread_id", "turn_id") if field in event)
        if not identities_valid:
            return False
        if "usage" in event:
            usage = event["usage"]
            fields = {
                "input_tokens", "cached_input_tokens", "output_tokens",
                "reasoning_output_tokens"}
            return (
                type(usage) is dict and set(usage) == fields and
                all(type(usage[field]) is int and usage[field] >= 0
                    for field in fields))
        return True
    return True


def _valid_codex_item_event_shape(event):
    event_type = event.get("type")
    if event_type not in ("item.started", "item.updated", "item.completed"):
        return False
    keys = set(event)
    if (not {"type", "item"} <= keys or
            not keys <= {
                "type", "item", "status", "thread_id", "turn_id"}):
        return False
    if not isinstance(event["item"], dict):
        return False
    if any(
            type(event[field]) is not str or not event[field]
            for field in ("thread_id", "turn_id") if field in event):
        return False
    if "status" in event:
        allowed_status = (
            {"in_progress"} if event_type in
            ("item.started", "item.updated")
            else {"completed", "failed", "error"})
        if (type(event["status"]) is not str or
                event["status"] not in allowed_status):
            return False
    return True


def _path_identity_text(value):
    text = str(value or "").replace("\\", "/")
    if text == "/" or re.fullmatch(r"[A-Za-z]:/", text):
        return text
    return text.rstrip("/")


def _drive_relative(value):
    return bool(re.match(r"^[A-Za-z]:(?:$|[^/])", value))


def _within(path, root, case_sensitive=True):
    path = _path_identity_text(path)
    root = _path_identity_text(root)
    if _drive_relative(path) or _drive_relative(root):
        return False
    if not case_sensitive:
        path = path.lower()
        root = root.lower()
    prefix = root if root.endswith("/") else root + "/"
    return bool(path and root and (
        path == root or path.startswith(prefix)))


def _same_path(first, second, case_sensitive=True):
    first = _path_identity_text(first)
    second = _path_identity_text(second)
    if _drive_relative(first) or _drive_relative(second):
        return False
    if not case_sensitive:
        first = first.lower()
        second = second.lower()
    return bool(first and second and first == second)


def _codex_native_repo_policy(profile):
    """Return the closed native repo policy or None for any schema drift."""
    if not isinstance(profile, dict):
        return None
    repo = profile.get("repo")
    if (not isinstance(repo, dict) or
            set(repo) != CODEX_NATIVE_REPO_FIELDS or
            type(repo.get("lexical_root")) is not str or
            not repo["lexical_root"] or
            type(repo.get("real_root")) is not str or
            not repo["real_root"] or
            type(repo.get("case_sensitive")) is not bool):
        return None
    return repo


def _mapping(value):
    """Return mapping-shaped input or an empty mapping for fail-closed use."""
    return value if isinstance(value, dict) else {}


def _valid_tool_list(value):
    return (isinstance(value, list) and
            all(isinstance(tool, str) and tool for tool in value))


def _valid_binding_shape(value):
    return (isinstance(value, dict) and all(
        isinstance(key, str) and key and (
            (isinstance(item, str) and item) or type(item) is int)
        for key, item in value.items()))


def _valid_codex_binding(value, require_native=False, allow_empty=False):
    if not isinstance(value, dict):
        return False
    if not value:
        return allow_empty
    allowed = {"thread_id", "stdout_turn_ordinal", "turn_id",
               "native_turn_id"}
    required = {"thread_id", "stdout_turn_ordinal"}
    if not required.issubset(value) or not set(value).issubset(allowed):
        return False
    if (not isinstance(value.get("thread_id"), str) or
            not value["thread_id"] or
            type(value.get("stdout_turn_ordinal")) is not int or
            value["stdout_turn_ordinal"] != 1):
        return False
    for key in ("turn_id", "native_turn_id"):
        if key in value and (not isinstance(value[key], str) or
                             not value[key]):
            return False
    return not require_native or "native_turn_id" in value


def _valid_claude_binding(value, allow_empty=False):
    if not isinstance(value, dict):
        return False
    if not value:
        return allow_empty
    return (set(value) == {"session_id"} and
            isinstance(value.get("session_id"), str) and
            bool(value["session_id"]))


def _profile_result(ok, reason=None):
    result = {"host_status": "PASS" if ok else "INVALID",
              "property_status": "PASS" if ok else "INCOMPLETE"}
    if reason:
        result["reason"] = reason
    return result


def validate_profile(profile, post_probe=None, formal=True,
                     writable_roots=(), expected_host=None):
    """Validate an internally minted profile and optional post-mission probe.

    Caller dictionaries are never accepted as formal authority.  Test fixtures
    may exercise downstream pure functions with ``formal=False``.
    """
    if not isinstance(profile, dict):
        return _profile_result(False, "missing profile")
    if formal and not isinstance(profile, _MintedProfile):
        return _profile_result(False, "profile provenance")
    if profile.get("schema") != PROFILE_SCHEMA:
        return _profile_result(False, "profile schema")
    host = profile.get("host")
    if host not in ("codex", "claude"):
        return _profile_result(False, "profile host")
    if expected_host is not None and host != expected_host:
        return _profile_result(False, "profile host mismatch")
    authority = profile.get("authority")
    if formal and authority != "mechanically-minted":
        return _profile_result(False, "profile authority")
    if not formal and authority not in ("mechanically-minted",
                                        "test-fixture-only"):
        return _profile_result(False, "profile authority")
    repo = _codex_native_repo_policy(profile)
    if host == "claude" and repo is not None:
        native_tools = profile.get("native_tools")
        if (not isinstance(native_tools, dict) or
                not _valid_tool_list(native_tools.get("requested")) or
                not re.fullmatch(r"[0-9a-f]{64}",
                                 str(profile.get("probe_sha256", "")))):
            return _profile_result(False, "native profile shape")
        expected_probe = {
            "repo": repo["lexical_root"], "native_tools": native_tools}
        if (formal and profile.get("probe_sha256") !=
                _sha256(_canonical_bytes(expected_probe))):
            return _profile_result(False, "native profile probe digest")
        if post_probe is not None and post_probe != {
                "native_tools": native_tools}:
            return _profile_result(False, "native profile drift")
        return _profile_result(True)
    shell = profile.get("shell")
    wrapper = profile.get("outer_wrapper")
    environment = profile.get("environment")
    executables = profile.get("executables")
    if (repo is None or
            not isinstance(shell, dict) or
            not isinstance(shell.get("logical_path"), str) or
            not isinstance(shell.get("realpath"), str) or
            not re.fullmatch(r"[0-9a-f]{64}", str(shell.get("sha256", ""))) or
            not isinstance(shell.get("stat"), str) or
            not isinstance(wrapper, dict) or
            wrapper.get("argv_prefix") != ["/bin/bash", "-lc"] or
            wrapper.get("max_unwrap_layers") != 1 or
            not isinstance(environment, dict) or
            not isinstance(executables, dict) or not executables or
            not re.fullmatch(r"[0-9a-f]{64}",
                             str(profile.get("probe_sha256", "")))):
        return _profile_result(False, "profile shape")
    for name, identity in executables.items():
        if (name not in SUPPORTED_READERS or
                not isinstance(identity, dict) or
                identity.get("kind") != "file" or
                not isinstance(identity.get("path"), str) or
                not re.fullmatch(r"[0-9a-f]{64}",
                                 str(identity.get("sha256", ""))) or
                not isinstance(identity.get("stat"), str)):
            return _profile_result(False, "executable identity")
    expected_probe = {"environment": environment, "shell": shell,
                      "executables": executables}
    if (formal and profile.get("probe_sha256") !=
            _sha256(_canonical_bytes(expected_probe))):
        return _profile_result(False, "profile probe digest")
    protected = [shell["realpath"]] + [entry["path"]
                                       for entry in executables.values()]
    for path in protected:
        if any(_within(path, root) or _within(os.path.dirname(path), root)
               for root in writable_roots):
            return _profile_result(False, "profile executable writable")
    if post_probe is not None:
        if not isinstance(post_probe, dict):
            return _profile_result(False, "post probe shape")
        if post_probe.get("environment") != environment:
            return _profile_result(False, "environment drift")
        post_shell = post_probe.get("shell")
        if not isinstance(post_shell, dict):
            return _profile_result(False, "post shell shape")
        for field in ("realpath", "sha256", "stat"):
            if post_shell.get(field) != shell.get(field):
                return _profile_result(False, "shell drift")
        post_exec = post_probe.get("executables")
        if post_exec != executables:
            return _profile_result(False, "executable resolution drift")
    return _profile_result(True)


def _admit_persisted_profile(profile, expected_host=None):
    """Restore formal capability after replay has verified parent custody."""
    if not isinstance(profile, dict) or \
            profile.get("authority") != "mechanically-minted":
        raise ValueError("persisted profile authority")
    admitted = _mint_profile(profile)
    if validate_profile(
            admitted, formal=True,
            expected_host=expected_host)["host_status"] != "PASS":
        raise ValueError("persisted profile invalid")
    return admitted


def _stat_identity(path):
    info = os.stat(path)
    return (f"dev={info.st_dev};ino={info.st_ino};mode={info.st_mode:o};"
            f"size={info.st_size}")


def _run_probe(shell, command, env=None):
    proc = subprocess.run([shell, "-lc", command], capture_output=True,
                          text=True, env=env, timeout=60)
    if proc.returncode != 0:
        raise ValueError(f"profile probe failed: {proc.stderr[:160]}")
    return proc.stdout


def probe_posix(shell_executable, env=None):
    """Probe one exact login-shell environment and supported readers."""
    shell_real = os.path.realpath(shell_executable)
    environment = {}
    for name in ("PATH", "LANG", "LC_ALL", "BASH_ENV", "ENV", "SHELL"):
        output = _run_probe(
            shell_executable,
            f"if [ -n \"${{{name}+x}}\" ]; then printf '%s' \"${name}\"; "
            "else printf '__UNSET__'; fi", env=env)
        environment[name] = None if output == "__UNSET__" else output
    executables = {}
    for name in SUPPORTED_READERS:
        kind = _run_probe(
            shell_executable, f"command -V -- {shlex.quote(name)}", env=env)
        lowered = kind.lower()
        if "alias" in lowered or "function" in lowered or "builtin" in lowered:
            raise ValueError(f"unsupported reader resolution for {name}")
        path = _run_probe(
            shell_executable, f"command -v -- {shlex.quote(name)}", env=env)
        path = path.strip()
        if not path.startswith("/"):
            raise ValueError(f"missing reader resolution for {name}")
        digest = _run_probe(
            shell_executable,
            f"sha256sum -- {shlex.quote(path)} | cut -d' ' -f1", env=env).strip()
        stat_text = _run_probe(
            shell_executable,
            f"stat -c 'dev=%d;ino=%i;mode=%f;size=%s' -- {shlex.quote(path)}",
            env=env).strip()
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"invalid reader digest for {name}")
        executables[name] = {"kind": "file", "path": path,
                             "sha256": digest, "stat": stat_text}
    shell = {"logical_path": "/bin/bash", "realpath": shell_real,
             "sha256": _file_sha256(shell_real),
             "stat": _stat_identity(shell_real)}
    probe = {"environment": environment, "shell": shell,
             "executables": executables}
    probe["probe_sha256"] = _sha256(_canonical_bytes(probe))
    return probe


def mint_codex_profile(repo_root, shell_executable, env=None,
                       writable_roots=()):
    probe = probe_posix(shell_executable, env=env)
    profile = _mint_profile({
        "schema": PROFILE_SCHEMA, "authority": "mechanically-minted",
        "host": "codex",
        "repo": {"lexical_root": os.path.abspath(repo_root).replace("\\", "/"),
                 "real_root": os.path.realpath(repo_root).replace("\\", "/"),
                 "case_sensitive": os.path.normcase("A") != os.path.normcase("a")},
        "shell": probe["shell"],
        "outer_wrapper": {"argv_prefix": ["/bin/bash", "-lc"],
                          "max_unwrap_layers": 1},
        "environment": probe["environment"],
        "executables": probe["executables"],
        "probe_sha256": probe["probe_sha256"]})
    result = validate_profile(profile, formal=False,
                              writable_roots=writable_roots)
    if result["host_status"] != "PASS":
        raise ValueError(result.get("reason", "profile invalid"))
    return profile


def mint_claude_profile(repo_root, requested_tools):
    """Mint the pre-spawn native-tool boundary for a Claude host run."""
    repo_abs = os.path.abspath(repo_root).replace("\\", "/")
    if not _valid_tool_list(requested_tools):
        raise ValueError("invalid requested tool list")
    native_tools = {"requested": list(requested_tools)}
    probe = {"repo": repo_abs, "native_tools": native_tools}
    return _mint_profile({
        "schema": PROFILE_SCHEMA, "authority": "mechanically-minted",
        "host": "claude",
        "repo": {"lexical_root": repo_abs,
                 "real_root": os.path.realpath(repo_root).replace("\\", "/"),
                 "case_sensitive": os.path.normcase("A") != os.path.normcase("a")},
        "native_tools": native_tools,
        "probe_sha256": _sha256(_canonical_bytes(probe))})


def post_probe(profile, shell_executable, env=None):
    probe = probe_posix(shell_executable, env=env)
    return {"environment": probe["environment"], "shell": probe["shell"],
            "executables": probe["executables"]}


def _safe_relative(relative):
    if not isinstance(relative, str) or not relative or "\x00" in relative:
        return False
    text = relative.replace("\\", "/")
    return (not text.startswith("/") and not re.match(r"^[A-Za-z]:/", text)
            and all(part not in ("", ".", "..")
                    for part in text.split("/")))


def capture_preimages(repo_root, targets):
    repo_abs = os.path.abspath(repo_root)
    repo_real = os.path.realpath(repo_root)
    case_sensitive = os.path.normcase("A") != os.path.normcase("a")
    captured = {}
    for relative in targets:
        if not _safe_relative(relative):
            raise ValueError(f"unsafe target {relative!r}")
        path = os.path.abspath(os.path.join(repo_abs, *relative.split("/")))
        if os.path.commonpath((repo_abs, path)) != repo_abs:
            raise ValueError(f"external target {relative!r}")
        current = repo_abs
        symlink_free = True
        for part in relative.split("/"):
            current = os.path.join(current, part)
            if os.path.islink(current):
                symlink_free = False
                break
        if not symlink_free or os.path.realpath(path) != path:
            raise ValueError(f"symlink target {relative!r}")
        data = open(path, "rb").read()
        info = os.stat(path)
        captured[relative] = {
            "canonical_path": path.replace("\\", "/"),
            "relative_path": relative, "content_base64":
            base64.b64encode(data).decode("ascii"),
            "sha256": _sha256(data), "size": len(data),
            "mode": stat.S_IMODE(info.st_mode) | stat.S_IFREG,
            "symlink_free": True}
    return {"schema": PREIMAGE_SCHEMA,
            "repo": {"lexical_root": repo_abs.replace("\\", "/"),
                     "real_root": repo_real.replace("\\", "/"),
                     "case_sensitive": case_sensitive},
            "targets": captured}


def validate_preimages(preimages):
    try:
        if (not isinstance(preimages, dict) or
                preimages.get("schema") != PREIMAGE_SCHEMA or
                not isinstance(preimages.get("repo"), dict) or
                not isinstance(preimages.get("targets"), dict) or
                not preimages["targets"]):
            raise ValueError("preimage shape")
        repo = preimages["repo"]
        for required in ("lexical_root", "real_root"):
            if not isinstance(repo.get(required), str):
                raise ValueError("preimage root")
        if type(repo.get("case_sensitive")) is not bool:
            raise ValueError("filesystem semantics")
        for relative, entry in preimages["targets"].items():
            if not _safe_relative(relative) or not isinstance(entry, dict):
                raise ValueError("target identity")
            data = base64.b64decode(entry.get("content_base64", ""),
                                    validate=True)
            expected_path = str(PurePosixPath(repo["lexical_root"],
                                              relative))
            if (_sha256(data) != entry.get("sha256") or
                    len(data) != entry.get("size") or
                    entry.get("relative_path") != relative or
                    entry.get("symlink_free") is not True or
                    not _same_path(entry.get("canonical_path"),
                                   expected_path,
                                   case_sensitive=repo["case_sensitive"]) or
                    not _within(entry.get("canonical_path"),
                                repo.get("lexical_root"),
                                case_sensitive=repo["case_sensitive"])):
                raise ValueError("preimage mismatch")
    except (ValueError, TypeError, base64.binascii.Error):
        return {"status": "INVALID"}
    return {"status": "PASS"}


def snapshot_digest(preimages):
    return _sha256(_canonical_bytes(preimages))


def _profile_matches_preimages(profile, preimages):
    profile_repo = _mapping(_mapping(profile).get("repo"))
    snapshot_repo = _mapping(_mapping(preimages).get("repo"))
    case_sensitive = profile_repo.get("case_sensitive")
    snapshot_case_sensitive = snapshot_repo.get("case_sensitive")
    if (type(case_sensitive) is not bool or
            type(snapshot_case_sensitive) is not bool or
            snapshot_case_sensitive != case_sensitive):
        return False
    return (_same_path(profile_repo.get("lexical_root"),
                       snapshot_repo.get("lexical_root"),
                       case_sensitive=case_sensitive) and
            _same_path(profile_repo.get("real_root"),
                       snapshot_repo.get("real_root"),
                       case_sensitive=case_sensitive))


def _profile_matches_replay_spec(profile, replay_spec):
    profile = _mapping(profile)
    replay_spec = _mapping(replay_spec)
    host = profile.get("host")
    if host != replay_spec.get("host"):
        return False
    if host == "claude":
        profile_requested = _mapping(profile.get("native_tools")).get(
            "requested")
        replay_requested = replay_spec.get("requested_tools")
        return (_valid_tool_list(profile_requested) and
                _valid_tool_list(replay_requested) and
                profile_requested == replay_requested)
    return host == "codex" and replay_spec.get("requested_tools") == []


def _preimage_bytes(preimages, target):
    if validate_preimages(preimages)["status"] != "PASS":
        return None
    entry = preimages["targets"].get(target)
    if not entry:
        return None
    return base64.b64decode(entry["content_base64"])


def _normalize_path(path, preimages):
    if not isinstance(path, str) or not path or "\x00" in path:
        return None
    text = path.replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", text) or text.startswith("/"):
        candidate = str(PurePosixPath(text))
    else:
        parts = text.split("/")
        if any(part == ".." for part in parts):
            return None
        parts = [part for part in parts if part not in ("", ".")]
        candidate = str(PurePosixPath(
            preimages["repo"]["lexical_root"], *parts))
    root = preimages["repo"]["lexical_root"]
    case_sensitive = preimages["repo"]["case_sensitive"]
    if not _within(candidate, root, case_sensitive=case_sensitive):
        return None
    return candidate


def _path_matches(path, target, preimages):
    entry = (preimages.get("targets") or {}).get(target)
    observed = _normalize_path(path, preimages)
    case_sensitive = (preimages.get("repo") or {}).get(
        "case_sensitive", True)
    return bool(entry and observed and _same_path(
        observed, entry["canonical_path"], case_sensitive=case_sensitive))


class _ActionMachine:
    def __init__(self):
        self.actions = []
        self.pending = {}
        self.reserved = set()
        self.invalid = False
        self.findings = []

    def _append(self, action):
        self.actions.append(action)
        if action.get("state") == "INVALID":
            self.invalid = True
        return action

    def invalid_action(self, ordinal, reason, action_id=None,
                       effect="unknown"):
        self.findings.append({"code": "invalid-host-event",
                              "reason": reason, "ordinal": ordinal,
                              "classification": "fail-closed"})
        diagnostic_id = f"invalid@{ordinal}:{len(self.actions) + 1}"
        return self._append({"id": diagnostic_id,
                             "state": "INVALID", "effect": effect,
                             "classification": "fail-closed",
                             "invocation_invented": False,
                             "invocation_ordinal": None,
                             "completion_ordinal": ordinal,
                             "reason": reason})

    def start(self, action_id, ordinal, effect, payload, **fields):
        if (not isinstance(action_id, str) or not action_id or
                action_id in self.reserved):
            return self.invalid_action(ordinal, "duplicate or missing action id",
                                       action_id)
        self.reserved.add(action_id)
        action = {"id": action_id, "state": "PENDING", "effect": effect,
                  "classification": fields.pop("classification", None),
                  "invocation_invented": False,
                  "invocation_ordinal": ordinal,
                  "completion_ordinal": None, "payload": payload}
        action.update(fields)
        self.pending[action_id] = action
        return self._append(action)

    def update(self, action_id, ordinal, payload):
        if not isinstance(action_id, str) or not action_id:
            return self.invalid_action(ordinal, "invalid action update",
                                       action_id)
        action = self.pending.get(action_id)
        if not action or action.get("effect") != "safe-other" or \
                action.get("action_type") != "todo_list":
            return self.invalid_action(ordinal, "invalid action update",
                                       action_id)
        action.setdefault("updates", []).append(
            {"ordinal": ordinal, "payload": payload})
        return action

    def complete(self, action_id, ordinal, payload=None, state="COMPLETED",
                 **fields):
        if not isinstance(action_id, str) or not action_id:
            return self.invalid_action(ordinal, "completion without invocation",
                                       action_id)
        action = self.pending.pop(action_id, None)
        if action is None:
            return self.invalid_action(ordinal, "completion without invocation",
                                       action_id)
        if payload is not None and action.get("payload") != payload:
            action.update({"state": "INVALID", "completion_ordinal": ordinal,
                           "reason": "start/completion payload conflict"})
            self.invalid = True
            return action
        action.update(fields)
        action["state"] = state
        action["completion_ordinal"] = ordinal
        if state == "INVALID":
            self.invalid = True
        return action

    def terminal_message(self, action_id, ordinal, payload):
        if (not isinstance(action_id, str) or not action_id or
                action_id in self.reserved):
            return self.invalid_action(ordinal, "terminal message id reuse",
                                       action_id, effect="safe-other")
        self.reserved.add(action_id)
        return self._append({"id": action_id,
                             "state": "TERMINAL_SAFE_MESSAGE",
                             "effect": "safe-other",
                             "classification": "not-content-read",
                             "payload": payload,
                             "invocation_invented": False,
                             "invocation_ordinal": None,
                             "completion_ordinal": ordinal})

    def finish(self, pending_invalid=False):
        if pending_invalid and self.pending:
            self.invalid = True
            self.findings.append({
                "code": "incomplete-host-action",
                "classification": "fail-closed",
                "action_ids": sorted(self.pending),
            })
        for action in list(self.pending.values()):
            action["state"] = "INCOMPLETE"
            action["classification"] = action.get("classification") or \
                "fail-closed"
        self.pending.clear()
        return {"schema": TRACE_SCHEMA, "actions": self.actions,
                "invalid": self.invalid, "host_findings": self.findings,
                "ids_reserved": len(self.reserved) == len(set(self.reserved)),
                "action_states": [a["state"] for a in self.actions
                                  if not a["id"].startswith("invalid@")],
                "action_effects": [a["effect"] for a in self.actions
                                   if not a["id"].startswith("invalid@")],
                "host_status": "INVALID" if self.invalid else "PASS"}


def _codex_payload(item):
    item_type = item.get("type")
    if item_type == "command_execution":
        command = item.get("command")
        return ("command", command) if isinstance(command, str) else None
    if item_type == "file_change":
        changes = item.get("changes")
        if not isinstance(changes, list):
            return None
        normalized = []
        for change in changes:
            if (not isinstance(change, dict) or
                    not isinstance(change.get("path"), str) or
                    not change.get("path") or
                    ("kind" in change and
                     not isinstance(change.get("kind"), str))):
                return None
            normalized.append((change["path"], change.get("kind")))
        return ("changes", tuple(normalized))
    if item_type == "todo_list":
        return ("todo_list",) if _valid_todo_items(item.get("items")) else None
    return None


def _valid_codex_collaboration_item(item, event_type):
    fields = {
        "id", "type", "tool", "sender_thread_id", "receiver_thread_ids",
        "prompt", "status", "agents_states",
    }
    if (set(item) != fields or event_type not in
            ("item.started", "item.completed") or
            item.get("type") != "collab_tool_call" or
            not isinstance(item.get("id"), str) or not item["id"] or
            not isinstance(item.get("sender_thread_id"), str) or
            not item["sender_thread_id"] or
            not isinstance(item.get("receiver_thread_ids"), list) or
            not isinstance(item.get("agents_states"), dict)):
        return False
    receivers = item["receiver_thread_ids"]
    if (not all(isinstance(receiver, str) and receiver
                for receiver in receivers) or
            len(receivers) != len(set(receivers)) or
            item["sender_thread_id"] in receivers):
        return False
    tool = item.get("tool")
    if tool not in ("spawn_agent", "wait"):
        return False
    if event_type == "item.started":
        if item.get("status") != "in_progress" or item["agents_states"]:
            return False
        return ((tool == "spawn_agent" and not receivers and
                 isinstance(item.get("prompt"), str) and bool(item["prompt"])) or
                (tool == "wait" and len(receivers) == 1 and
                 item.get("prompt") is None))
    if item.get("status") != "completed" or len(receivers) != 1:
        return False
    child = receivers[0]
    if set(item["agents_states"]) != {child}:
        return False
    state = item["agents_states"].get(child)
    if not isinstance(state, dict) or set(state) != {"message", "status"}:
        return False
    if tool == "spawn_agent":
        return (isinstance(item.get("prompt"), str) and bool(item["prompt"]) and
                state["message"] is None and state["status"] == "pending_init")
    return (item.get("prompt") is None and
            isinstance(state["message"], str) and bool(state["message"]) and
            state["status"] == "completed")


def _valid_todo_items(items):
    return (isinstance(items, list) and all(
        isinstance(item, dict) and set(item) == {"text", "completed"} and
        isinstance(item.get("text"), str) and
        type(item.get("completed")) is bool
        for item in items))


def _profile_allows_wrapper(profile, formal):
    return validate_profile(
        profile, formal=formal,
        expected_host="codex")["host_status"] == "PASS"


def _wrapper_layers(command, profile, formal):
    if not isinstance(command, str) or not _profile_allows_wrapper(profile,
                                                                   formal):
        return 0
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return 0
    prefix = profile["outer_wrapper"]["argv_prefix"]
    return 1 if len(tokens) == 3 and tokens[:2] == prefix else 0


def normalize_codex(raw_stdout, profile=None, binding=None, formal=True):
    machine = _ActionMachine()
    collaboration_children = {}
    if formal and validate_profile(
            profile, formal=True,
            expected_host="codex")["host_status"] != "PASS":
        machine.invalid_action(0, "invalid formal Codex profile")
    if binding is None:
        binding = {}
    if ((formal and not _valid_codex_binding(binding)) or
            (not formal and not _valid_binding_shape(binding))):
        machine.invalid_action(0, "invalid Codex binding")
        binding = {}
    active_thread = None
    active_turn = None
    active_turn_explicit = False
    turns = 0
    last_ordinal = 0
    for ordinal, line in enumerate(str(raw_stdout or "").splitlines(), 1):
        last_ordinal = ordinal
        try:
            event = _strict_object(line)
        except (ValueError, json.JSONDecodeError, TypeError) as exc:
            machine.invalid_action(ordinal, str(exc))
            continue
        event_type = event.get("type")
        if (event_type in ("thread.started", "turn.started",
                           "turn.completed") and
                not _valid_codex_lifecycle_shape(event)):
            machine.invalid_action(
                ordinal, "invalid Codex lifecycle event shape")
            continue
        if event_type == "thread.started":
            thread = event.get("thread_id")
            if (not isinstance(thread, str) or active_thread is not None or
                    (binding.get("thread_id") and
                     thread != binding["thread_id"])):
                machine.invalid_action(ordinal, "thread binding mismatch")
            else:
                active_thread = thread
            continue
        if event_type == "turn.started":
            turns += 1
            turn = event.get("turn_id")
            thread = event.get("thread_id", active_thread)
            if (active_thread is None or active_turn is not None or
                    turns != 1 or thread != active_thread or
                    (binding.get("thread_id") and
                     thread != binding["thread_id"]) or
                    (binding.get("turn_id") and
                     turn != binding["turn_id"])):
                machine.invalid_action(ordinal, "turn binding mismatch")
            else:
                active_turn = turn or binding.get("turn_id") or "<unique-turn>"
                active_turn_explicit = "turn_id" in event
            continue
        if event_type == "turn.completed":
            turn_explicit = "turn_id" in event
            turn = event.get("turn_id")
            thread = event.get("thread_id", active_thread)
            if (active_turn is None or thread != active_thread or
                    turn_explicit != active_turn_explicit or
                    (turn_explicit and turn != active_turn) or
                    (binding.get("turn_id") and
                     turn != binding["turn_id"])):
                machine.invalid_action(ordinal, "turn completion mismatch")
            else:
                active_turn = None
                active_turn_explicit = False
            continue
        if event_type not in ("item.started", "item.updated",
                              "item.completed"):
            machine.invalid_action(
                ordinal, "unsupported Codex event type")
            continue
        if not _valid_codex_item_event_shape(event):
            machine.invalid_action(
                ordinal, "invalid Codex item event root shape")
            continue
        if (event.get("thread_id", active_thread) != active_thread or
                ("turn_id" in event and
                 (not active_turn_explicit or
                  event["turn_id"] != active_turn))):
            machine.invalid_action(
                ordinal, "Codex item event identity mismatch")
            continue
        if active_turn is None:
            machine.invalid_action(ordinal, "action outside bound turn")
            continue
        item = event.get("item")
        if not isinstance(item, dict):
            machine.invalid_action(ordinal, "Codex item is not an object")
            continue
        action_id = item.get("id")
        item_type = item.get("type")
        if item_type == "collab_tool_call":
            if (set(event) != {"type", "item"} or
                    not _valid_codex_collaboration_item(item, event_type) or
                    item.get("sender_thread_id") != active_thread):
                machine.invalid_action(
                    ordinal, "invalid Codex collaboration item", action_id,
                    effect="safe-other")
                continue
            tool = item["tool"]
            sender = item["sender_thread_id"]
            prompt = item["prompt"]
            receivers = item["receiver_thread_ids"]
            payload = (tool, sender, prompt)
            if event_type == "item.started":
                child = receivers[0] if tool == "wait" else None
                if (tool == "wait" and
                        collaboration_children.get(child) != "spawned"):
                    machine.invalid_action(
                        ordinal, "orphan or duplicate collaboration wait",
                        action_id, effect="safe-other")
                    continue
                action = machine.start(
                    action_id, ordinal, "safe-other", payload,
                    classification="not-content-read",
                    action_type="collab_tool_call", tool=tool,
                    sender_thread_id=sender, prompt=prompt,
                    receiver_thread_ids=list(receivers))
                if tool == "wait" and action.get("state") == "PENDING":
                    collaboration_children[child] = "wait_pending"
                continue
            action = machine.pending.get(action_id)
            if (action is None or
                    action.get("action_type") != "collab_tool_call" or
                    action.get("tool") != tool or
                    action.get("sender_thread_id") != sender or
                    action.get("prompt") != prompt):
                machine.complete(
                    action_id, ordinal, state="INVALID",
                    reason="collaboration start/completion conflict")
                continue
            child = receivers[0]
            if tool == "spawn_agent":
                valid_transition = (
                    action.get("receiver_thread_ids") == [] and
                    child not in collaboration_children)
            else:
                valid_transition = (
                    action.get("receiver_thread_ids") == [child] and
                    collaboration_children.get(child) == "wait_pending")
            if not valid_transition:
                machine.complete(
                    action_id, ordinal, state="INVALID",
                    reason="invalid collaboration state transition")
                continue
            completed = machine.complete(
                action_id, ordinal, payload=payload,
                receiver_thread_ids=list(receivers))
            if completed.get("state") == "COMPLETED":
                collaboration_children[child] = (
                    "spawned" if tool == "spawn_agent" else "completed")
            continue
        if item_type == "command_execution":
            base = {"id", "type", "status", "command"}
            keys = set(item)
            if event_type == "item.started":
                metadata = {"aggregated_output", "exit_code"} & keys
                valid_command_shape = (
                    base <= keys and keys <= base | {
                        "aggregated_output", "exit_code"} and
                    (not metadata or
                     (metadata == {"aggregated_output", "exit_code"} and
                      item["aggregated_output"] == "" and
                      item["exit_code"] is None)))
            elif event_type == "item.completed":
                valid_command_shape = keys == base | {
                    "aggregated_output", "exit_code"}
            else:
                valid_command_shape = keys == base
            if not valid_command_shape:
                machine.invalid_action(
                    ordinal, "invalid Codex command item shape", action_id)
                continue
        if event_type == "item.completed" and item_type == "agent_message":
            if (item.get("status") not in (None, "completed") or
                    event.get("status") in ("failed", "error") or
                    not isinstance(item.get("text"), str)):
                machine.invalid_action(ordinal, "invalid terminal message",
                                       action_id)
            else:
                machine.terminal_message(action_id, ordinal,
                                         ("agent_message", item["text"]))
            continue
        if item_type not in ("command_execution", "file_change", "todo_list"):
            machine.invalid_action(ordinal, "unsupported Codex action",
                                   action_id)
            continue
        if item_type == "todo_list" and not _valid_todo_items(
                item.get("items")):
            machine.invalid_action(ordinal, "invalid todo items", action_id,
                                   effect="safe-other")
            continue
        payload = _codex_payload(item)
        if event_type == "item.started":
            valid_start_status = (
                item.get("status") in (None, "in_progress")
                if item_type == "todo_list" else
                item.get("status") == "in_progress")
            if not valid_start_status or payload is None:
                machine.invalid_action(ordinal, "invalid action start",
                                       action_id)
                continue
            effect = ("command" if item_type == "command_execution" else
                      "write" if item_type == "file_change" else "safe-other")
            fields = {"action_type": item_type}
            if item_type == "command_execution":
                wrapper_layers = _wrapper_layers(
                    item.get("command"), profile, formal)
                fields.update({"command": item.get("command"),
                               "wrapper_layers": wrapper_layers,
                               "protocol_wrapper_valid":
                               not formal or wrapper_layers == 1})
            elif item_type == "file_change":
                fields["paths"] = [change["path"]
                                   for change in item["changes"]]
            machine.start(action_id, ordinal, effect, payload, **fields)
            continue
        if event_type == "item.updated":
            if (item.get("status") not in (None, "in_progress") or
                    item_type != "todo_list"):
                machine.invalid_action(ordinal, "invalid action update",
                                       action_id)
            else:
                machine.update(action_id, ordinal, item.get("items"))
            continue
        if not isinstance(action_id, str) or not action_id:
            machine.invalid_action(ordinal, "completion without invocation",
                                   action_id)
            continue
        action = machine.pending.get(action_id)
        if action is None:
            machine.invalid_action(ordinal, "completion without invocation",
                                   action_id)
            continue
        outer_status = event.get("status")
        item_status = item.get("status")
        if item_type == "command_execution":
            exit_code = item.get("exit_code")
            output = item.get("aggregated_output")
            valid_status = (item_status == ("completed" if exit_code == 0
                                             else "failed"))
            if (type(exit_code) is not int or not isinstance(output, str) or
                    outer_status in ("failed", "error") or not valid_status):
                machine.complete(action_id, ordinal, state="INVALID",
                                 reason="contradictory command completion")
                continue
            if action.get("protocol_wrapper_valid") is not True:
                machine.complete(
                    action_id, ordinal, payload=payload, state="INVALID",
                    reason="unbound Codex protocol wrapper")
                continue
            machine.complete(action_id, ordinal, payload=payload,
                             exit_code=exit_code, output=output)
        elif item_type == "file_change":
            if item_status != "completed" or outer_status in ("failed", "error"):
                machine.complete(action_id, ordinal, state="INVALID",
                                 reason="invalid write completion")
            else:
                machine.complete(action_id, ordinal, payload=payload)
        else:
            if (item_status not in (None, "completed") or
                    outer_status in ("failed", "error")):
                machine.complete(action_id, ordinal, state="INVALID",
                                 reason="invalid todo completion")
            else:
                machine.complete(action_id, ordinal)
    if active_thread is None or turns != 1 or active_turn is not None:
        machine.invalid_action(
            last_ordinal + 1, "incomplete or ambiguous Codex lifecycle")
    if any(state != "completed" for state in collaboration_children.values()):
        machine.invalid_action(
            last_ordinal + 1, "incomplete collaboration lifecycle",
            effect="safe-other")
    if formal and collaboration_children:
        machine.invalid_action(
            last_ordinal + 1,
            "unbound collaboration descendant evidence",
            effect="safe-other")
    result = machine.finish(pending_invalid=True)
    result["requested_tools"] = []
    result["observed_tools"] = []
    return result


def _claude_result_metadata(event):
    metadata = event.get("tool_use_result")
    if metadata is None:
        return None
    return metadata if isinstance(metadata, dict) else "<malformed>"


def _result_paths(metadata):
    if not isinstance(metadata, dict):
        return []
    paths = []
    if "filePath" in metadata:
        paths.append(metadata.get("filePath"))
    file_obj = metadata.get("file")
    if file_obj is not None and not isinstance(file_obj, dict):
        return "<malformed>"
    if isinstance(file_obj, dict) and "filePath" in file_obj:
        paths.append(file_obj.get("filePath"))
    return paths


def _lexical_path(path):
    if not isinstance(path, str) or not path or "\x00" in path:
        return None
    text = path.replace("\\", "/")
    if any(part == ".." for part in text.split("/")):
        return None
    return str(PurePosixPath(text))


def _profile_path(path, profile, formal=True):
    """Resolve one lexical tool path inside the profiled repository root."""
    observed = _lexical_path(path)
    if observed is None:
        return None
    absolute = observed.startswith("/") or bool(
        re.match(r"^[A-Za-z]:/", observed))
    repo = _mapping(_mapping(profile).get("repo"))
    root = _lexical_path(repo.get("lexical_root"))
    case_sensitive = repo.get("case_sensitive")
    # Non-formal fixture calls historically omit a profile. Keep their
    # lexical-only behavior while formal normalization requires a root-bound
    # host-specific profile before any result can become evidence.
    if root is None or type(case_sensitive) is not bool:
        return None if formal else observed
    if not absolute:
        observed = str(PurePosixPath(root, observed))
    if not _within(observed, root, case_sensitive=case_sensitive):
        return None
    return observed


def _claude_read_transport(visible, metadata):
    """Validate Claude's narrow native Read rendering contract.

    A metadata-free minimal result remains eligible only through exact visible
    preimage equality at classification time.  When structured file content
    is present, both the structured bytes and the model-visible renderer must
    agree losslessly before that structured content can be used.
    """
    if metadata is None:
        return {"status": "minimal-visible", "structured_content": None}
    if (not isinstance(metadata, dict) or metadata.get("type") != "text" or
            not isinstance(metadata.get("file"), dict)):
        return {"status": "incomplete", "structured_content": None}
    file_record = metadata["file"]
    structured = file_record.get("content")
    if not isinstance(structured, str):
        return {"status": "incomplete", "structured_content": None}
    line_keys = ("startLine", "numLines", "totalLines")
    present = [key in file_record for key in line_keys]
    if any(present):
        if not all(present):
            return {"status": "incomplete",
                    "structured_content": structured}
        start, count, total = (file_record[key] for key in line_keys)
        if (any(type(value) is not int for value in (start, count, total)) or
                start != 1 or count != total or count < 1):
            return {"status": "incomplete",
                    "structured_content": structured}
        raw_lines = structured.split("\n")
        visible_lines = visible.split("\n")
        if count != len(raw_lines) or len(visible_lines) != len(raw_lines):
            return {"status": "incomplete",
                    "structured_content": structured}
        for index, (rendered, original) in enumerate(
                zip(visible_lines, raw_lines), start=1):
            match = re.fullmatch(r"\s*(\d+)\t(.*)", rendered)
            if (not match or int(match.group(1)) != index or
                    match.group(2) != original):
                return {"status": "incomplete",
                        "structured_content": structured}
        return {"status": "full-line-renderer",
                "structured_content": structured}
    if visible != structured:
        return {"status": "incomplete", "structured_content": structured}
    return {"status": "full-exact", "structured_content": structured}


def normalize_claude(raw_stdout, requested_tools, binding=None, profile=None,
                     formal=True):
    machine = _ActionMachine()
    if formal and validate_profile(
            profile, formal=True,
            expected_host="claude")["host_status"] != "PASS":
        machine.invalid_action(0, "invalid formal Claude profile")
    if binding is None:
        binding = {}
    if ((formal and not _valid_claude_binding(binding)) or
            (not formal and not _valid_binding_shape(binding))):
        machine.invalid_action(0, "invalid Claude binding")
        binding = {}
    requested_shape_valid = _valid_tool_list(requested_tools)
    if formal and not requested_shape_valid:
        machine.invalid_action(0, "invalid requested tool list")
    if requested_shape_valid:
        requested = list(requested_tools)
    elif not formal and isinstance(requested_tools, tuple) and all(
            isinstance(tool, str) for tool in requested_tools):
        requested = list(requested_tools)
    else:
        requested = []
    profile_requested = _mapping(
        _mapping(profile).get("native_tools")).get("requested")
    if (formal and
            (not _valid_tool_list(profile_requested) or
             profile_requested != requested)):
        machine.invalid = True
        machine.findings.append({
            "code": "profile-requested-tools-mismatch",
            "classification": "fail-closed"})
    observed = None
    session = binding.get("session_id")
    for ordinal, line in enumerate(str(raw_stdout or "").splitlines(), 1):
        try:
            event = _strict_object(line)
        except (ValueError, json.JSONDecodeError, TypeError) as exc:
            machine.invalid_action(ordinal, str(exc))
            continue
        event_session = event.get("session_id")
        if session and event_session and event_session != session:
            machine.invalid_action(ordinal, "Claude session mismatch")
            continue
        event_type = event.get("type")
        if event_type == "system" and event.get("subtype") == "init":
            tools = event.get("tools")
            if not _valid_tool_list(tools):
                machine.invalid_action(ordinal, "invalid tool inventory")
            elif observed is not None:
                machine.invalid_action(ordinal, "duplicate tool inventory")
            else:
                observed = list(tools)
            continue
        if event_type not in ("assistant", "user"):
            continue
        message = event.get("message")
        if not isinstance(message, dict) or not isinstance(
                message.get("content"), list):
            machine.invalid_action(ordinal, "invalid Claude message")
            continue
        for block in message["content"]:
            if not isinstance(block, dict):
                machine.invalid_action(ordinal, "invalid Claude block")
                continue
            block_type = block.get("type")
            if event_type == "user" and block_type == "tool_use":
                machine.invalid_action(ordinal, "tool use in wrong role",
                                       block.get("id"))
                continue
            if event_type == "assistant" and block_type == "tool_use":
                action_id = block.get("id")
                tool = block.get("name")
                inputs = block.get("input")
                if not isinstance(tool, str) or not isinstance(inputs, dict):
                    machine.invalid_action(ordinal, "invalid Claude tool use",
                                           action_id)
                    continue
                effect = ("read" if tool == "Read" else
                          "write" if tool in ("Write", "Edit") else
                          "command" if tool == "Bash" else
                          "search" if tool == "Grep" else
                          "safe-other" if tool in ("Glob", "Skill") else
                          "descendant" if tool in ("Task", "Workflow") else
                          "unknown")
                path = inputs.get("file_path") if effect in ("read", "write") \
                    else inputs.get("path") if effect == "search" else None
                command = inputs.get("command") if effect == "command" else None
                invalid_input = False
                if effect in ("read", "write"):
                    invalid_input = _profile_path(
                        path, profile, formal=formal) is None
                elif effect == "command":
                    invalid_input = not isinstance(command, str) or not command
                elif effect == "search":
                    invalid_input = (_profile_path(
                        path, profile, formal=formal) is None or
                                     inputs.get("output_mode") not in
                                     ("content", "files_with_matches"))
                if invalid_input:
                    machine.invalid_action(ordinal, "invalid Claude tool input",
                                           action_id, effect=effect)
                    continue
                payload = (tool, _canonical_bytes(inputs).decode("utf-8"))
                action = machine.start(
                    action_id, ordinal, effect, payload, action_type=tool,
                    path=path, command=command, inputs=inputs,
                    classification=("not-content-read" if effect ==
                                    "safe-other" else "fail-closed"))
                if effect == "descendant":
                    action["descendant_complete"] = False
                if effect == "unknown":
                    action["classification"] = "fail-closed"
                continue
            if event_type == "user" and block_type == "tool_result":
                action_id = block.get("tool_use_id")
                if not isinstance(action_id, str) or not action_id:
                    machine.invalid_action(ordinal, "unmatched Claude result",
                                           action_id)
                    continue
                action = machine.pending.get(action_id)
                if action is None:
                    machine.invalid_action(ordinal, "unmatched Claude result",
                                           action_id)
                    continue
                metadata = _claude_result_metadata(event)
                content = block.get("content")
                status = block.get("status")
                is_error = block.get("is_error")
                interrupted = block.get("interrupted")
                failure = (status in ("failed", "error", "cancelled",
                                      "interrupted") or is_error is True or
                           interrupted is True or
                           ("is_error" in block and type(is_error) is not bool))
                malformed = not isinstance(content, str)
                if metadata == "<malformed>":
                    malformed = True
                result_paths = _result_paths(metadata)
                if result_paths == "<malformed>":
                    malformed = True
                    result_paths = []
                action_lexical = _lexical_path(action.get("path"))
                profile_repo = _mapping(_mapping(profile).get("repo"))
                profile_root = _lexical_path(profile_repo.get("lexical_root"))
                if (not formal and profile_root is None and
                        isinstance(action_lexical, str) and
                        (action_lexical.startswith("/") or re.match(
                            r"^[A-Za-z]:/", action_lexical)) and
                        not result_paths):
                    # A profileless non-formal absolute path remains lexical
                    # only when the result independently repeats that exact
                    # identity. It never becomes formal/root-bound evidence.
                    malformed = True
                if result_paths and action.get("path"):
                    action_path = _profile_path(
                        action.get("path"), profile, formal=formal)
                    case_sensitive = profile_repo.get("case_sensitive", True)
                    if (action_path is None or any(
                            not _same_path(
                                _profile_path(path, profile, formal=formal),
                                action_path,
                                case_sensitive=case_sensitive)
                            for path in result_paths)):
                        malformed = True
                if action["effect"] == "command" and isinstance(metadata, dict):
                    if metadata.get("interrupted") is True:
                        failure = True
                    stdout = metadata.get("stdout")
                    if stdout is not None and (not isinstance(stdout, str) or
                                               stdout != content):
                        malformed = True
                    if metadata.get("noOutputExpected") is True and content:
                        malformed = True
                if action["effect"] == "search" and isinstance(metadata, dict):
                    stdout = metadata.get("stdout")
                    if stdout is not None and (not isinstance(stdout, str) or
                                               stdout != content):
                        malformed = True
                if action["effect"] == "write" and isinstance(metadata, dict):
                    if ("userModified" in metadata and
                            metadata.get("userModified") is not False):
                        action["classification"] = "fail-closed"
                        machine.complete(action_id, ordinal, state="INCOMPLETE",
                                         output=content, metadata=metadata)
                        continue
                if action["effect"] in ("search", "safe-other") and \
                        isinstance(metadata, dict) and \
                        metadata.get("truncated") is True:
                    machine.complete(action_id, ordinal, state="INCOMPLETE",
                                     output=content, metadata=metadata)
                    continue
                if action["effect"] == "descendant":
                    machine.complete(action_id, ordinal, state="INCOMPLETE",
                                     output=content, metadata=metadata)
                    continue
                if action["effect"] == "unknown":
                    machine.complete(action_id, ordinal, state="INVALID",
                                     output=content, metadata=metadata)
                    continue
                if action["effect"] == "read" and any(
                        name in action.get("inputs", {})
                        for name in ("offset", "limit")):
                    machine.complete(action_id, ordinal, state="INCOMPLETE",
                                     output=content, metadata=metadata)
                    continue
                read_transport = None
                if action["effect"] == "read" and not malformed:
                    read_transport = _claude_read_transport(content, metadata)
                    if read_transport["status"] == "incomplete":
                        action["classification"] = "fail-closed"
                        machine.complete(
                            action_id, ordinal, state="INCOMPLETE",
                            output=content, metadata=metadata,
                            read_transport=read_transport["status"],
                            structured_content=read_transport[
                                "structured_content"])
                        continue
                if failure or malformed:
                    machine.complete(action_id, ordinal, state="INVALID",
                                     output=content, metadata=metadata)
                else:
                    fields = {"output": content, "metadata": metadata}
                    if read_transport is not None:
                        fields.update({
                            "read_transport": read_transport["status"],
                            "structured_content": read_transport[
                                "structured_content"]})
                    machine.complete(action_id, ordinal, **fields)
    result = machine.finish()
    result["crashed"] = False
    result["requested_tools"] = requested
    result["observed_tools"] = observed or []
    if observed is None:
        result["invalid"] = True
        result["host_status"] = "INVALID"
        result["host_findings"].append(
            {"code": "missing-tool-inventory",
             "classification": "fail-closed"})
    missing_requested = [tool for tool in requested
                         if observed is not None and tool not in observed]
    if missing_requested:
        result["invalid"] = True
        result["host_status"] = "INVALID"
        result["host_findings"].append(
            {"code": "requested-tool-unavailable",
             "tools": missing_requested, "classification": "fail-closed"})
    invoked_unavailable = sorted({
        action.get("action_type") for action in result["actions"]
        if isinstance(action.get("action_type"), str) and
        observed is not None and action.get("action_type") not in observed})
    if invoked_unavailable:
        result["invalid"] = True
        result["host_status"] = "INVALID"
        result["host_findings"].append(
            {"code": "invoked-tool-unavailable",
             "tools": invoked_unavailable, "classification": "fail-closed"})
    unknown_invoked = sorted({
        action.get("action_type") for action in result["actions"]
        if action.get("effect") == "unknown" and
        isinstance(action.get("action_type"), str)})
    if unknown_invoked:
        result["invalid"] = True
        result["host_status"] = "INVALID"
        result["host_findings"].append(
            {"code": "unsupported-invoked-tool", "tools": unknown_invoked,
             "classification": "fail-closed"})
    return result


def _classification(classification="fail-closed", process_access=False,
                    **fields):
    result = {"classification": classification,
              "process_access": bool(process_access)}
    result.update(fields)
    return result


def _target_relationship(path, target, preimages):
    """Return direct, scope, invalid, or unrelated for a captured target.

    This is snapshot-relative lexical identity only.  It deliberately does not
    consult the ambient filesystem during replay.
    """
    if not isinstance(path, str):
        return "invalid"
    if "\x00" in path or any(part == ".." for part in
                              path.replace("\\", "/").split("/")):
        return "invalid"
    observed = _normalize_path(path, preimages)
    entry = (preimages.get("targets") or {}).get(target)
    if not observed or not entry:
        return "invalid"
    canonical = entry["canonical_path"]
    case_sensitive = preimages["repo"]["case_sensitive"]
    if _same_path(observed, canonical, case_sensitive=case_sensitive):
        return "direct"
    if _within(canonical, observed, case_sensitive=case_sensitive):
        return "scope"
    return "unrelated"


def _unquoted_ampersand_free(command):
    """Reject shell background/control ampersands without losing quote origin."""
    if not isinstance(command, str):
        return False
    state = "plain"
    index = 0
    while index < len(command):
        character = command[index]
        if state == "plain":
            if character == "\\":
                if index + 1 >= len(command):
                    return False
                index += 2
                continue
            if character == "'":
                state = "single"
            elif character == '"':
                state = "double"
            elif character == "&":
                return False
        elif state == "single":
            if character == "'":
                state = "plain"
        else:
            if character == "\\":
                if index + 1 >= len(command):
                    return False
                index += 2
                continue
            if character == '"':
                state = "plain"
        index += 1
    return state == "plain"


def _finite_shell_tokens(command):
    """Tokenize only the deliberately finite, single-stage POSIX surface."""
    if not isinstance(command, str) or not command or "\x00" in command:
        return None
    # Shell composition, expansion, and alternate dialects are outside this
    # evidence grammar.  Redirection is handled below as a small explicit
    # exception; this is not intended to grow into a shell parser.
    if ("\n" in command or "\r" in command or "$" in command or
            "#" in command or
            "`" in command or not _unquoted_ampersand_free(command) or
            any(text in command for text in
                                   (";", "&&", "||", "|", "(", ")",
                                    "{", "}"))):
        return None
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars="<>")
        lexer.whitespace_split = True
        lexer.commenters = ""
        return list(lexer)
    except (ValueError, TypeError):
        return None


def _unwrap_profiled_command(command, profile, formal):
    if validate_profile(
            profile, formal=formal,
            expected_host="codex")["host_status"] != "PASS":
        return None
    try:
        tokens = shlex.split(command, posix=True)
    except (ValueError, TypeError):
        return None
    prefix = profile["outer_wrapper"]["argv_prefix"]
    if len(tokens) == 3 and tokens[:2] == prefix:
        return tokens[2]
    return None if formal else command


def _split_redirections(tokens):
    """Split a tiny fd0/input and stdout-redirection subset.

    The last fd0 assignment wins.  Descriptor duplication, attached numeric
    descriptors, here-documents, and missing operands are rejected.
    """
    argv = []
    stdin_paths = []
    output_paths = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in ("<", ">", ">>"):
            if index + 1 >= len(tokens):
                return None
            path = tokens[index + 1]
            if (not path or path in ("<", ">", ">>") or
                    re.fullmatch(r"\d+", argv[-1] if argv else "")):
                return None
            if token == "<":
                stdin_paths.append(path)
            else:
                output_paths.append(path)
            index += 2
            continue
        if token.startswith(("<&", ">&")) or re.match(r"^\d+[<>]", token):
            return None
        argv.append(token)
        index += 1
    return {"argv": argv, "stdin_paths": stdin_paths,
            "output_paths": output_paths}


def _reader_identity(argv0, profile):
    if not argv0 or not isinstance(profile, dict):
        return None
    for name, identity in _mapping(profile.get("executables")).items():
        if (isinstance(identity, dict) and
                (argv0 == name or argv0 == identity.get("path"))):
            return name
    return None


def _paths_access(paths, target, preimages):
    relationships = [_target_relationship(path, target, preimages)
                     for path in paths]
    return ("direct" in relationships, "scope" in relationships,
            "invalid" in relationships)


def _cat_plan(args, stdin_paths):
    paths = []
    end_options = False
    for arg in args:
        if not end_options and arg == "--":
            end_options = True
        elif not end_options and arg.startswith("-"):
            return None
        else:
            paths.append(arg)
    if stdin_paths:
        if paths:
            return None
        paths = [stdin_paths[-1]]
    if not paths:
        return None
    return {"paths": paths, "config_paths": [], "zero": False,
            "terminal": False, "unsafe": False}


def _sed_plan(args, stdin_paths):
    paths = []
    configs = []
    programs = []
    index = 0
    end_options = False
    while index < len(args):
        arg = args[index]
        if not end_options and arg == "--":
            end_options = True
            index += 1
            continue
        if not end_options and arg == "-n":
            index += 1
            continue
        if not end_options and arg in ("-e", "--expression"):
            if index + 1 >= len(args):
                return None
            programs.append(args[index + 1])
            index += 2
            continue
        if not end_options and (arg.startswith("--expression=") or
                                (arg.startswith("-e") and len(arg) > 2)):
            programs.append(arg.split("=", 1)[1] if "=" in arg else arg[2:])
            index += 1
            continue
        if not end_options and arg in ("-f", "--file"):
            if index + 1 >= len(args):
                return None
            configs.append(args[index + 1])
            index += 2
            continue
        if not end_options and arg.startswith("--file="):
            configs.append(arg.split("=", 1)[1])
            index += 1
            continue
        if not end_options and (arg == "-i" or arg.startswith("-i") or
                                arg.startswith("--in-place")):
            return {"paths": paths, "config_paths": configs, "zero": False,
                    "terminal": False, "unsafe": True}
        if not end_options and arg.startswith("-"):
            return None
        if not programs and not configs:
            programs.append(arg)
        else:
            paths.append(arg)
        index += 1
    if stdin_paths:
        if paths:
            return None
        paths = [stdin_paths[-1]]
    if not programs and not configs:
        return None
    return {"paths": paths, "config_paths": configs, "zero": False,
            "terminal": False, "unsafe": False}


def _head_tail_plan(args, stdin_paths):
    paths = []
    zero = False
    index = 0
    end_options = False
    while index < len(args):
        arg = args[index]
        if not end_options and arg == "--":
            end_options = True
            index += 1
            continue
        value = None
        if not end_options and arg in ("-n", "-c", "--lines", "--bytes"):
            if index + 1 >= len(args):
                return None
            value = args[index + 1]
            index += 2
        elif not end_options and re.fullmatch(r"-[nc]\d+", arg):
            value = arg[2:]
            index += 1
        elif not end_options and (arg.startswith("--lines=") or
                                  arg.startswith("--bytes=")):
            value = arg.split("=", 1)[1]
            index += 1
        elif not end_options and arg.startswith("-"):
            return None
        else:
            paths.append(arg)
            index += 1
        if value is not None:
            if not re.fullmatch(r"\d+", value):
                return None
            zero = zero or int(value) == 0
    if stdin_paths:
        if paths:
            return None
        paths = [stdin_paths[-1]]
    if not paths:
        return None
    return {"paths": paths, "config_paths": [], "zero": zero,
            "terminal": False, "unsafe": False}


def _grep_plan(reader, args, stdin_paths):
    paths = []
    configs = []
    patterns = []
    zero = False
    unsafe = False
    terminal = False
    index = 0
    end_options = False
    while index < len(args):
        arg = args[index]
        if not end_options and arg == "--":
            end_options = True
            index += 1
            continue
        if not end_options and ((reader == "rg" and arg in ("-h", "-V")) or
                                (reader == "grep" and arg == "-V")):
            terminal = True
            index += 1
            continue
        if not end_options and arg in ("-e", "--regexp"):
            if index + 1 >= len(args):
                return None
            patterns.append(args[index + 1])
            index += 2
            continue
        if not end_options and arg.startswith("--regexp="):
            patterns.append(arg.split("=", 1)[1])
            index += 1
            continue
        if not end_options and arg in ("-f", "--file"):
            if index + 1 >= len(args):
                return None
            configs.append(args[index + 1])
            index += 2
            continue
        if not end_options and arg.startswith("--file="):
            configs.append(arg.split("=", 1)[1])
            index += 1
            continue
        if not end_options and arg in ("-m", "--max-count"):
            if index + 1 >= len(args):
                return None
            value = args[index + 1]
            if not re.fullmatch(r"\d+", value):
                return None
            zero = zero or int(value) == 0
            index += 2
            continue
        if not end_options and (re.fullmatch(r"-m\d+", arg) or
                                arg.startswith("--max-count=")):
            value = arg[2:] if arg.startswith("-m") else arg.split("=", 1)[1]
            if not re.fullmatch(r"\d+", value):
                return None
            zero = zero or int(value) == 0
            index += 1
            continue
        if not end_options and (arg in ("-R", "-r", "-h", "-l") or
                arg.startswith(("--replace", "--ignore-file",
                                "--exclude-from", "--no-filename",
                                "--files-with-matches", "--files", "--glob"))):
            unsafe = True
            # Options that consume a following value must consume it so a
            # target used as configuration is still recorded as process access.
            if ("=" in arg and arg.startswith(("--replace=",
                                               "--ignore-file=",
                                               "--exclude-from=",
                                               "--glob="))):
                configs.append(arg.split("=", 1)[1])
                index += 1
            elif arg in ("-r", "--replace", "--ignore-file",
                         "--exclude-from", "--glob") and index + 1 < len(args):
                configs.append(args[index + 1])
                index += 2
            else:
                index += 1
            continue
        if not end_options and arg.startswith("-"):
            return None
        if not patterns:
            patterns.append(arg)
        else:
            paths.append(arg)
        index += 1
    if stdin_paths:
        if paths:
            return None
        paths = [stdin_paths[-1]]
    if not terminal and not patterns:
        return None
    return {"paths": paths, "config_paths": configs, "zero": zero,
            "terminal": terminal, "unsafe": unsafe}


def classify_shell(record, target, preimages, profile=None, formal=True,
                   dialect_hint=None):
    """Classify one profiled, single-stage command for one captured target."""
    if (validate_preimages(preimages)["status"] != "PASS" or
            dialect_hint not in (None, "posix") or
            not isinstance(record, dict) or
            not isinstance(record.get("command"), str) or
            not isinstance(record.get("output"), str) or
            type(record.get("exit_code")) is not int):
        return _classification()
    command = _unwrap_profiled_command(record["command"], profile, formal)
    if command is None:
        return _classification()
    tokens = _finite_shell_tokens(command)
    if not tokens:
        return _classification()
    split = _split_redirections(tokens)
    if split is None or not split["argv"]:
        return _classification()
    reader = _reader_identity(split["argv"][0], profile)
    if reader is None:
        return _classification()
    planners = {"cat": _cat_plan, "sed": _sed_plan,
                "head": _head_tail_plan, "tail": _head_tail_plan}
    if reader in planners:
        plan = planners[reader](split["argv"][1:], split["stdin_paths"])
    else:
        plan = _grep_plan(reader, split["argv"][1:], split["stdin_paths"])
    if plan is None:
        # Exact target text under an unsupported option is still process
        # access, but can never become product evidence.
        access = any(_target_relationship(token, target, preimages) in
                     ("direct", "scope") for token in split["argv"][1:])
        return _classification(process_access=access)
    direct, scope, invalid = _paths_access(plan["paths"], target, preimages)
    config_direct, config_scope, config_invalid = _paths_access(
        plan["config_paths"], target, preimages)
    process_access = direct or scope or config_direct or config_scope
    if split["output_paths"] or plan["unsafe"] or invalid or config_invalid or \
            scope or config_direct or config_scope:
        return _classification(process_access=process_access)
    if not direct:
        preimage = _preimage_bytes(preimages, target)
        if preimage is not None and record["output"].encode("utf-8") == preimage:
            return _classification(process_access=False)
        return _classification("not-content-read", process_access=False)
    if plan["terminal"] or plan["zero"]:
        return _classification("not-content-read", process_access=True)
    if record["exit_code"] != 0:
        return _classification(process_access=True)
    preimage = _preimage_bytes(preimages, target)
    if (preimage is not None and
            record["output"].encode("utf-8") == preimage):
        return _classification("content-read", process_access=True,
                               evidence="full-bound-preimage")
    return _classification(process_access=True)


def classify_actions(actions, targets, preimages, profile=None, formal=True):
    """Build a per-target property matrix from persisted normalized actions."""
    result = {}
    for target in targets:
        observed = []
        for action in actions:
            classification = _classification()
            effect = action.get("effect")
            if action.get("state") not in ("COMPLETED",):
                observed.append(classification)
                continue
            if effect == "command":
                classification = classify_shell(
                    {"command": action.get("command"),
                     "output": action.get("output"),
                     "exit_code": action.get("exit_code")},
                    target, preimages, profile=profile, formal=formal)
            elif effect == "read":
                relationship = _target_relationship(action.get("path"), target,
                                                    preimages)
                process = relationship in ("direct", "scope")
                delivered = (action.get("structured_content")
                             if action.get("read_transport") in
                             ("full-line-renderer", "full-exact") else
                             action.get("output"))
                if (relationship == "direct" and
                        not any(name in action.get("inputs", {})
                                for name in ("offset", "limit")) and
                        isinstance(delivered, str) and
                        delivered.encode("utf-8") ==
                        (_preimage_bytes(preimages, target) or b"<missing>")):
                    classification = _classification(
                        "content-read", True, evidence="full-bound-preimage")
                elif relationship == "unrelated":
                    classification = _classification("not-content-read")
                else:
                    classification = _classification(process_access=process)
            elif effect == "search":
                relationship = _target_relationship(action.get("path"), target,
                                                    preimages)
                process = relationship in ("direct", "scope")
                if (relationship == "direct" and
                        action.get("inputs", {}).get("output_mode") ==
                        "content" and
                        action.get("output", "").encode("utf-8") ==
                        (_preimage_bytes(preimages, target) or b"<missing>")):
                    classification = _classification(
                        "content-read", True, evidence="full-bound-preimage")
                elif relationship == "unrelated":
                    classification = _classification("not-content-read")
                else:
                    classification = _classification(process_access=process)
            elif effect == "safe-other":
                classification = _classification("not-content-read")
            observed.append(classification)
        reads = [entry for entry in observed
                 if entry["classification"] == "content-read"]
        access = any(entry["process_access"] for entry in observed)
        result[target] = (reads[0] if reads else
                          _classification("fail-closed" if access else
                                          "fail-closed", access))
    return result


def _equivalent_path(first, second, preimages):
    left = _normalize_path(first, preimages)
    right = _normalize_path(second, preimages)
    case_sensitive = preimages["repo"]["case_sensitive"]
    return bool(left and right and _same_path(
        left, right, case_sensitive=case_sensitive))


def classify_shell_write(record, write, preimages, profile=None, formal=True):
    """Recognize only a direct, single-stage stdout redirection write.

    A successful shell process is still not interchangeable with a native host
    write completion in the product-property adjudicator.
    """
    base = {"classification": "fail-closed", "write_state": "INCOMPLETE",
            "process_access": False}
    if (validate_preimages(preimages)["status"] != "PASS" or
            not isinstance(record, dict) or
            not isinstance(record.get("command"), str) or
            not isinstance(record.get("output"), str) or
            type(record.get("exit_code")) is not int):
        return base
    command = _unwrap_profiled_command(record["command"], profile, formal)
    tokens = _finite_shell_tokens(command) if command is not None else None
    split = _split_redirections(tokens) if tokens else None
    if split is None or len(split["output_paths"]) != 1:
        return base
    output_path = split["output_paths"][0]
    if not _equivalent_path(output_path, write, preimages):
        return base
    state = "COMPLETED" if record["exit_code"] == 0 else "INCOMPLETE"
    return {"classification": ("write-observed" if state == "COMPLETED"
                                else "fail-closed"),
            "write_state": state, "process_access": True,
            "path": output_path}


def _action_classification(action, target, preimages, profile, formal):
    return classify_actions([action], [target], preimages, profile=profile,
                            formal=formal)[target]


def _native_write_paths(action):
    if action.get("effect") != "write":
        return []
    if isinstance(action.get("path"), str):
        return [action["path"]]
    return [path for path in action.get("paths", [])
            if isinstance(path, str)]


def _shell_record(action):
    if action.get("effect") != "command":
        return None
    return {"command": action.get("command"),
            "output": action.get("output"),
            "exit_code": action.get("exit_code")}


def adjudicate_path_order(normalized, reads, write, preimages, profile=None,
                          formal=True):
    """Adjudicate product properties separately from host validity.

    Every required read must deliver the full captured preimage and complete
    before the native write invocation.  A later host failure never erases
    those property measurements.
    """
    actions = list((normalized or {}).get("actions") or [])
    host_findings = list((normalized or {}).get("host_findings") or [])
    read_completions = {}
    read_results = {}
    for target in reads:
        candidates = []
        for action in actions:
            classified = _action_classification(
                action, target, preimages, profile, formal)
            if (classified["classification"] == "content-read" and
                    action.get("state") == "COMPLETED"):
                candidates.append(action.get("completion_ordinal"))
            elif (action.get("effect") == "command" and
                  classified["classification"] == "fail-closed" and
                  (classified.get("process_access") or
                   target in str(action.get("command") or ""))):
                host_findings.append(
                    {"code": "fail-closed-command", "target": target,
                     "action_id": action.get("id")})
        valid = [ordinal for ordinal in candidates if type(ordinal) is int]
        read_completions[target] = min(valid) if valid else None
        read_results[target] = {
            "classification": "content-read" if valid else "fail-closed",
            "completion_ordinal": read_completions[target]}

    native_writes = []
    shell_writes = []
    for action in actions:
        if any(_equivalent_path(path, write, preimages)
               for path in _native_write_paths(action)):
            native_writes.append(action)
        record = _shell_record(action)
        if record is not None:
            shell = classify_shell_write(record, write, preimages,
                                         profile=profile, formal=formal)
            if shell.get("process_access"):
                shell_writes.append((action, shell))
    completed_native = [action for action in native_writes
                        if action.get("state") == "COMPLETED" and
                        type(action.get("invocation_ordinal")) is int and
                        type(action.get("completion_ordinal")) is int]
    write_action = (min(completed_native,
                        key=lambda action: action["invocation_ordinal"])
                    if completed_native else None)
    write_invocation = (write_action.get("invocation_ordinal")
                        if write_action else None)
    write_completed = write_action is not None
    ordered = (write_completed and
               all(type(ordinal) is int and ordinal < write_invocation
                   for ordinal in read_completions.values()))

    live_preimage = True
    for target, completion in read_completions.items():
        for action in actions:
            invocation = action.get("invocation_ordinal")
            if type(invocation) is not int or (type(completion) is int and
                                               invocation >= completion):
                continue
            if any(_equivalent_path(path, target, preimages)
                   for path in _native_write_paths(action)):
                live_preimage = False
            record = _shell_record(action)
            if record is not None and classify_shell_write(
                    record, target, preimages, profile=profile,
                    formal=formal).get("process_access"):
                live_preimage = False

    property_pass = (all(read_completions[target] is not None
                         for target in reads) and write_completed and ordered
                     and live_preimage)
    property_status = "PASS" if property_pass else "INCOMPLETE"
    host_status = (normalized or {}).get("host_status", "INVALID")
    overall = (host_status if host_status in ("INVALID", "ERROR")
               else property_status)
    return {"schema": MATRIX_SCHEMA, "property_status": property_status,
            "host_status": host_status, "overall_status": overall,
            "ordered": ordered, "ordering_source": "persisted-ordinal",
            "write_completed": write_completed,
            "write_invocation_ordinal": write_invocation,
            "borrowed_completion": False, "live_preimage": live_preimage,
            "reads": read_results, "host_findings": host_findings,
            "shell_write_observations": len(shell_writes)}


_CAPTURE_FILES = (
    "host-read-profile.json", "host-read-preimages.json",
    "host-read-fixture.raw", "host-read-replay-spec.json",
    "host-read-pre-spawn.json",
    "host-stdout.raw", "host-session.raw", "host-tool-trace.json",
    "host-read-matrix.json", "host-read-post-probe.json",
    "host-read-terminal.json")


def _write_new(path, data):
    mode = "xb"
    with open(path, mode) as fh:
        fh.write(data)


def _write_new_json(path, value):
    _write_new(path, _canonical_bytes(value) + b"\n")


def _read_json_file(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    return json.loads(text, object_pairs_hook=lambda pairs: _unique_pairs(pairs))


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _raw_capture_bytes(value):
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    raise ValueError("raw capture value must be text or bytes")


def _valid_terminal_trace(trace, formal):
    if not isinstance(trace, dict) or trace.get("schema") != TRACE_SCHEMA:
        return False
    if (not isinstance(trace.get("actions"), list) or
            any(not isinstance(action, dict)
                for action in trace["actions"]) or
            ("observed_tools" in trace and
             not _valid_tool_list(trace["observed_tools"]))):
        return False
    if not formal:
        return True
    return (type(trace.get("invalid")) is bool and
            type(trace.get("ids_reserved")) is bool and
            isinstance(trace.get("action_states"), list) and
            isinstance(trace.get("action_effects"), list) and
            isinstance(trace.get("host_findings"), list) and
            all(isinstance(finding, dict)
                for finding in trace["host_findings"]) and
            trace.get("host_status") in ("PASS", "INVALID", "ERROR") and
            "observed_tools" in trace)


def _valid_terminal_matrix(matrix, formal):
    if not isinstance(matrix, dict) or matrix.get("schema") != MATRIX_SCHEMA:
        return False
    if not formal:
        return True
    return (isinstance(matrix.get("raw_transforms"), dict) and
            isinstance(matrix.get("specs"), dict) and
            all(isinstance(value, dict)
                for value in matrix["specs"].values()))


def _valid_terminal_record(terminal):
    """Admit the sealed terminal only through its complete finite schema."""
    keys = {"schema", "hashes", "post_probe_sha256",
            "profile_post_status", "binding", "actual_tools",
            "normalized_host_status", "host_terminal_kind",
            "session_bound", "session_status"}
    if not isinstance(terminal, dict) or set(terminal) != keys:
        return False
    hashes = terminal.get("hashes")
    return (
        terminal.get("schema") == TERMINAL_SCHEMA and
        isinstance(hashes, dict) and
        set(hashes) == set(_CAPTURE_FILES[:-1]) and
        all(isinstance(value, str) and
            re.fullmatch(r"[0-9a-f]{64}", value)
            for value in hashes.values()) and
        isinstance(terminal.get("post_probe_sha256"), str) and
        bool(re.fullmatch(r"[0-9a-f]{64}",
                          terminal["post_probe_sha256"])) and
        terminal.get("profile_post_status") in ("PASS", "INVALID") and
        isinstance(terminal.get("binding"), dict) and
        _valid_tool_list(terminal.get("actual_tools")) and
        terminal.get("normalized_host_status") in (
            "PASS", "INVALID", "ERROR") and
        terminal.get("host_terminal_kind") in ("ok", "error", "invalid") and
        type(terminal.get("session_bound")) is bool and
        terminal.get("session_status") in (
            "VALID", "MISSING", "INVALID", "SUBSTITUTED") and
        terminal["session_bound"] ==
        (terminal["session_status"] == "VALID"))


def make_replay_spec(host, checks, requested_tools=(), fixture_sha256=None,
                     run_intent_sha256=None):
    """Freeze the production replay recipe before a model process starts."""
    return {"schema": REPLAY_SCHEMA, "mode": "formal-v2", "host": host,
            "checks": checks, "requested_tools": list(requested_tools),
            "fixture_sha256": fixture_sha256,
            "run_intent_sha256": run_intent_sha256,
            "parser_sha256": _file_sha256(os.path.abspath(__file__))}


def _validate_replay_spec(spec, formal):
    if not isinstance(spec, dict) or spec.get("schema") != REPLAY_SCHEMA:
        return False
    if not formal and spec.get("mode") == "custody-only-test":
        return True
    host = spec.get("host")
    requested_tools = spec.get("requested_tools")
    if (spec.get("mode") != "formal-v2" or
            host not in ("codex", "claude") or
            not isinstance(spec.get("checks"), list) or
            not spec["checks"] or
            (host == "codex" and requested_tools != []) or
            (host == "claude" and not _valid_tool_list(requested_tools)) or
            not re.fullmatch(r"[0-9a-f]{64}",
                             str(spec.get("fixture_sha256", ""))) or
            not re.fullmatch(r"[0-9a-f]{64}",
                             str(spec.get("run_intent_sha256", ""))) or
            spec.get("parser_sha256") !=
            _file_sha256(os.path.abspath(__file__))):
        return False
    for check in spec["checks"]:
        if (not isinstance(check, dict) or
                not isinstance(check.get("key"), str) or
                not isinstance(check.get("reads"), list) or
                not check["reads"] or
                not isinstance(check.get("write"), str)):
            return False
    return True


def begin_capture(root, profile, preimages, replay_spec=None,
                  fixture_bytes=None, formal=True):
    """Create immutable pre-spawn custody without any terminal facts."""
    os.makedirs(root, exist_ok=True)
    if any(os.path.lexists(os.path.join(root, name))
           for name in _CAPTURE_FILES + ("host-read-manifest.json",)):
        raise FileExistsError("host-read capture already exists")
    if validate_profile(profile, formal=formal)["host_status"] != "PASS":
        raise ValueError("invalid pre-spawn profile")
    if validate_preimages(preimages)["status"] != "PASS":
        raise ValueError("invalid pre-spawn snapshot")
    if formal and not _profile_matches_preimages(profile, preimages):
        raise ValueError("profile/preimage repository mismatch")
    if replay_spec is None:
        replay_spec = {"schema": REPLAY_SCHEMA,
                       "mode": "custody-only-test"}
    if not _validate_replay_spec(replay_spec, formal):
        raise ValueError("invalid pre-spawn replay recipe")
    if (formal and validate_profile(
            profile, formal=True,
            expected_host=replay_spec["host"])["host_status"] != "PASS"):
        raise ValueError("pre-spawn profile host mismatch")
    if formal and not _profile_matches_replay_spec(profile, replay_spec):
        raise ValueError("profile/replay boundary mismatch")
    if fixture_bytes is None:
        fixture_bytes = b"{}"
    if not isinstance(fixture_bytes, bytes):
        raise ValueError("fixture bytes are not immutable bytes")
    if (formal and _sha256(fixture_bytes) !=
            replay_spec.get("fixture_sha256")):
        raise ValueError("fixture identity mismatch")
    profile_path = os.path.join(root, "host-read-profile.json")
    preimages_path = os.path.join(root, "host-read-preimages.json")
    replay_path = os.path.join(root, "host-read-replay-spec.json")
    fixture_path = os.path.join(root, "host-read-fixture.raw")
    _write_new_json(profile_path, profile)
    _write_new_json(preimages_path, preimages)
    _write_new(fixture_path, fixture_bytes)
    _write_new_json(replay_path, replay_spec)
    pre_spawn = {
        "schema": PRESPAWN_SCHEMA, "created_before_spawn": True,
        "profile_sha256": _file_sha256(profile_path),
        "preimages_sha256": _file_sha256(preimages_path),
        "fixture_sha256": _file_sha256(fixture_path),
        "replay_spec_sha256": _file_sha256(replay_path)}
    _write_new_json(os.path.join(root, "host-read-pre-spawn.json"),
                    pre_spawn)
    return pre_spawn


def finish_capture(root, raw_stdout, raw_session, trace, matrix, post_probe,
                   binding=None, host_terminal_kind="ok",
                   session_status="VALID", formal=True,
                   minted_profile=None):
    """Seal terminal custody after a matching post-mission profile probe."""
    profile = _read_json_file(os.path.join(root, "host-read-profile.json"))
    preimages = _read_json_file(os.path.join(root,
                                              "host-read-preimages.json"))
    if formal:
        if (not isinstance(minted_profile, _MintedProfile) or
                _canonical_bytes(minted_profile) !=
                _canonical_bytes(profile)):
            raise ValueError("formal profile capability mismatch")
        profile = minted_profile
    profile_post_status = validate_profile(
        profile, post_probe=post_probe, formal=formal)["host_status"]
    if validate_preimages(preimages)["status"] != "PASS":
        raise ValueError("preimage custody mismatch")
    if formal and not _profile_matches_preimages(profile, preimages):
        raise ValueError("profile/preimage custody mismatch")
    if not _valid_terminal_trace(trace, formal):
        raise ValueError("trace schema")
    if not _valid_terminal_matrix(matrix, formal):
        raise ValueError("matrix schema")
    if not isinstance(post_probe, dict):
        raise ValueError("post-probe schema")
    if host_terminal_kind not in ("ok", "error", "invalid"):
        raise ValueError("host terminal kind")
    if session_status not in ("VALID", "MISSING", "INVALID",
                              "SUBSTITUTED"):
        raise ValueError("session status")
    if binding is None:
        binding = {}
    host = _mapping(profile).get("host")
    if formal and host == "codex":
        binding_valid = _valid_codex_binding(
            binding, require_native=bool(binding), allow_empty=True)
    elif formal and host == "claude":
        binding_valid = _valid_claude_binding(binding, allow_empty=True)
    else:
        binding_valid = _valid_binding_shape(binding)
    if not binding_valid:
        raise ValueError("binding shape")
    stdout_bytes = _raw_capture_bytes(raw_stdout)
    session_bytes = _raw_capture_bytes(raw_session)
    try:
        trace_bytes = _canonical_bytes(trace) + b"\n"
        matrix_bytes = _canonical_bytes(matrix) + b"\n"
        post_probe_bytes = _canonical_bytes(post_probe) + b"\n"
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("terminal capture is not canonical JSON") from exc
    _write_new(os.path.join(root, "host-stdout.raw"), stdout_bytes)
    _write_new(os.path.join(root, "host-session.raw"), session_bytes)
    _write_new(os.path.join(root, "host-tool-trace.json"), trace_bytes)
    _write_new(os.path.join(root, "host-read-matrix.json"), matrix_bytes)
    _write_new(os.path.join(root, "host-read-post-probe.json"),
               post_probe_bytes)
    bound = {name: _file_sha256(os.path.join(root, name))
             for name in _CAPTURE_FILES[:-1]}
    terminal = {"schema": TERMINAL_SCHEMA, "hashes": bound,
                "post_probe_sha256": _sha256(_canonical_bytes(post_probe)),
                "profile_post_status": profile_post_status,
                "binding": binding,
                "actual_tools": list(trace.get("observed_tools") or []),
                "normalized_host_status": trace.get("host_status"),
                "host_terminal_kind": host_terminal_kind,
                "session_bound": session_status == "VALID",
                "session_status": session_status}
    _write_new_json(os.path.join(root, "host-read-terminal.json"), terminal)
    manifest = {"schema": MANIFEST_SCHEMA,
                "files": {name: _file_sha256(os.path.join(root, name))
                          for name in _CAPTURE_FILES}}
    _write_new_json(os.path.join(root, "host-read-manifest.json"), manifest)
    return {"status": "PASS", "terminal": terminal,
            "manifest": manifest}


def seal_capture(root, profile, preimages, raw_stdout, raw_session, trace,
                 matrix, post_probe, formal=True):
    begin_capture(root, profile, preimages, formal=formal)
    return finish_capture(root, raw_stdout, raw_session, trace, matrix,
                          post_probe, formal=formal,
                          minted_profile=profile if formal else None)


def derive_codex_binding(raw_stdout):
    threads = []
    turns = []
    completions = []
    items = []
    for ordinal, line in enumerate(str(raw_stdout or "").splitlines(), 1):
        try:
            event = _strict_object(line)
        except (ValueError, TypeError, json.JSONDecodeError):
            return None
        event_type = event.get("type")
        if (event_type in ("thread.started", "turn.started",
                           "turn.completed") and
                not _valid_codex_lifecycle_shape(event)):
            return None
        if event_type == "thread.started":
            threads.append((ordinal, event["thread_id"]))
        elif event_type == "turn.started":
            turns.append((
                ordinal, event.get("thread_id"), event.get("turn_id"),
                "turn_id" in event))
        elif event_type == "turn.completed":
            completions.append((
                ordinal, event.get("thread_id"), event.get("turn_id"),
                "turn_id" in event))
        elif event_type in ("item.started", "item.updated", "item.completed"):
            if (not _valid_codex_item_event_shape(event) or
                    event.get("status") in ("failed", "error")):
                return None
            items.append((
                ordinal, event.get("thread_id"), event.get("turn_id"),
                "turn_id" in event))
        else:
            return None
    if len(threads) != 1 or len(turns) != 1 or len(completions) != 1:
        return None
    thread_ordinal, thread_id = threads[0]
    turn_ordinal, turn_thread, turn_id, turn_explicit = turns[0]
    completion_ordinal, completion_thread, completion_turn, \
        completion_explicit = completions[0]
    if (not thread_ordinal < turn_ordinal < completion_ordinal or
            turn_thread not in (None, thread_id) or
            completion_thread not in (None, thread_id) or
            turn_explicit != completion_explicit or
            (turn_explicit and completion_turn != turn_id)):
        return None
    if any(
            not turn_ordinal < ordinal < completion_ordinal or
            item_thread not in (None, thread_id) or
            (item_turn_explicit and
             (not turn_explicit or item_turn != turn_id))
            for ordinal, item_thread, item_turn, item_turn_explicit in items):
        return None
    result = {"thread_id": thread_id, "stdout_turn_ordinal": 1}
    if turn_explicit:
        result["turn_id"] = turn_id
    return result


def derive_claude_binding(raw_stdout):
    sessions = set()
    for line in str(raw_stdout or "").splitlines():
        try:
            event = _strict_object(line)
        except (ValueError, TypeError, json.JSONDecodeError):
            continue
        if isinstance(event.get("session_id"), str):
            sessions.add(event["session_id"])
    return {"session_id": next(iter(sessions))} if len(sessions) == 1 else None


def _scalar_strings(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _scalar_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _scalar_strings(item)
    elif isinstance(value, str):
        yield value


def _parse_utc(value):
    if not isinstance(value, str):
        return None
    try:
        from datetime import datetime
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def augment_codex_binding(binding, raw_session):
    """Bind the one native turn_context ID omitted by exec stdout."""
    if binding is not None and not _valid_codex_binding(binding):
        return None
    if not binding or not raw_session:
        return binding
    try:
        session_bytes = _raw_capture_bytes(raw_session)
        objects = [_strict_object(line) for line in session_bytes.decode(
            "utf-8").splitlines() if line.strip()]
    except (UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        return binding
    turns = [obj.get("payload") for obj in objects
             if obj.get("type") == "turn_context"]
    if (len(turns) == 1 and isinstance(turns[0], dict) and
            isinstance(turns[0].get("turn_id"), str)):
        result = dict(binding)
        result["native_turn_id"] = turns[0]["turn_id"]
        return result
    return binding


def _codex_startup_timestamps_valid(objects, meta_record, turn_record,
                                    process_started):
    """Bind native startup records by file order and one process-time window."""
    try:
        meta_index = objects.index(meta_record)
        turn_index = objects.index(turn_record)
    except ValueError:
        return False
    if meta_index >= turn_index:
        return False
    meta = _mapping(meta_record.get("payload"))
    stamps = (
        _parse_utc((process_started or {}).get("started_at")),
        _parse_utc(meta_record.get("timestamp")),
        _parse_utc(meta.get("timestamp")),
        _parse_utc(turn_record.get("timestamp")),
    )
    if any(value is None or value.utcoffset() is None for value in stamps):
        return False
    process_time, meta_time, meta_payload_time, turn_time = stamps
    from datetime import timedelta
    window_end = process_time + timedelta(
        seconds=CODEX_SESSION_START_WINDOW_SECONDS)
    return (
        process_time <= meta_payload_time <= meta_time <= window_end and
        process_time <= turn_time <= window_end
    )


def _codex_native_rows_valid(objects):
    """Apply the closed native row contract observed in retained sessions."""
    for record in objects:
        if set(record) != {"type", "timestamp", "payload"}:
            return False
        row_type = record.get("type")
        if type(row_type) is not str:
            return False
        contract = CODEX_NATIVE_PAYLOAD_FIELDS.get(row_type)
        payload = record.get("payload")
        if contract is None or not isinstance(payload, dict):
            return False
        required, optional = contract
        if not required <= set(payload) <= required | optional:
            return False
        parsed = _parse_utc(record.get("timestamp"))
        if parsed is None or parsed.utcoffset() is None:
            return False
    return True


def _codex_native_collaboration_name(name):
    if type(name) is not str:
        return False
    folded = name.casefold()
    return (
        folded in CODEX_COLLAB_NATIVE_TOOL_NAMES or
        folded.startswith("multi_agent_v1__") or
        folded.startswith("collaboration.") or
        folded.startswith("collaboration__")
    )


def _codex_native_exec_has_collaboration(value):
    if type(value) is not str:
        return False

    def marker(text):
        folded = text.casefold()
        return ("multi_agent_v1__" in folded or
                "collaboration." in folded or
                "collaboration__" in folded or
                any(name in folded for name in CODEX_COLLAB_NATIVE_TOOL_NAMES))

    def escape(index):
        if index + 1 >= len(value):
            return "", len(value), False
        char = value[index + 1]
        simple = {"n": "\n", "r": "\r", "t": "\t", "b": "\b",
                  "f": "\f", "v": "\v", "0": "\0"}
        if char in simple:
            return simple[char], index + 2, True
        if char in "\r\n":
            end = index + 2
            if char == "\r" and end < len(value) and value[end] == "\n":
                end += 1
            return "", end, True
        if char == "x":
            digits = value[index + 2:index + 4]
            if len(digits) == 2 and all(c in "0123456789abcdefABCDEF"
                                        for c in digits):
                return chr(int(digits, 16)), index + 4, True
            return "", len(value), False
        if char == "u":
            if index + 2 < len(value) and value[index + 2] == "{":
                close = value.find("}", index + 3)
                digits = value[index + 3:close] if close >= 0 else ""
                if (digits and len(digits) <= 6 and
                        all(c in "0123456789abcdefABCDEF" for c in digits)):
                    point = int(digits, 16)
                    if point <= 0x10ffff:
                        return chr(point), close + 1, True
                return "", len(value), False
            digits = value[index + 2:index + 6]
            if len(digits) == 4 and all(c in "0123456789abcdefABCDEF"
                                        for c in digits):
                return chr(int(digits, 16)), index + 6, True
            return "", len(value), False
        return char, index + 2, True

    def identifier_start(char):
        return char in "_$" or char.isidentifier()

    def identifier_part(char):
        return (char in "_$\u200c\u200d" or
                ("a" + char).isidentifier())

    def identifier_escape(index):
        if not value.startswith("\\u", index):
            return "", index + 1, False
        cursor = index + 2
        if cursor < len(value) and value[cursor] == "{":
            close = value.find("}", cursor + 1)
            if close < 0:
                return "", cursor + 1, False
            digits = value[cursor + 1:close]
            if (not digits or len(digits) > 6 or
                    not all(c in "0123456789abcdefABCDEF" for c in digits)):
                return "", close + 1, False
            point = int(digits, 16)
            if point > 0x10ffff:
                return "", close + 1, False
            return chr(point), close + 1, True
        digits = value[cursor:cursor + 4]
        if (len(digits) != 4 or
                not all(c in "0123456789abcdefABCDEF" for c in digits)):
            return "", min(len(value), cursor + max(1, len(digits))), False
        return chr(int(digits, 16)), cursor + 4, True

    def quoted(index, quote):
        decoded = []
        cursor = index + 1
        while cursor < len(value):
            char = value[cursor]
            if char == quote:
                return "".join(decoded), cursor + 1, False
            if char == "\\":
                part, cursor, valid = escape(cursor)
                if not valid:
                    return "", cursor, marker(value[index:])
                decoded.append(part)
                continue
            if char in "\r\n":
                return "", cursor, marker(value[index:cursor])
            decoded.append(char)
            cursor += 1
        return "", cursor, marker(value[index:])

    def regex_allowed(tokens):
        if not tokens:
            return True
        kind, token = tokens[-1]
        if kind == "id" and token.casefold() in {
                "return", "throw", "case", "delete", "void", "typeof",
                "instanceof", "in", "of", "yield", "await"}:
            return True
        return kind == "punct" and token in {
            "(", "[", "{", ",", ";", "=", ":", "!", "?", "+", "-",
            "*", "%", "&", "|", "^", "~", "<", ">"}

    def scan(start=0, stop_brace=False):
        tokens = []
        cursor = start
        brace_depth = 0
        ambiguous = False
        while cursor < len(value):
            char = value[cursor]
            if char.isspace():
                cursor += 1
                continue
            if stop_brace and char == "}" and brace_depth == 0:
                return tokens, cursor + 1, ambiguous, True
            if char in "'\"":
                decoded, cursor, bad = quoted(cursor, char)
                tokens.append(("str", decoded))
                ambiguous = ambiguous or bad
                continue
            if char == "`":
                template_start = cursor
                cursor += 1
                literal = []
                expressions = False
                closed = False
                while cursor < len(value):
                    char = value[cursor]
                    if char == "\\":
                        part, cursor, valid = escape(cursor)
                        if not valid:
                            ambiguous = ambiguous or marker(
                                value[template_start:])
                            cursor = len(value)
                            break
                        literal.append(part)
                    elif char == "`":
                        cursor += 1
                        closed = True
                        break
                    elif char == "$" and cursor + 1 < len(value) and \
                            value[cursor + 1] == "{":
                        expressions = True
                        tokens.append(("barrier", ""))
                        nested, cursor, bad, nested_closed = scan(
                            cursor + 2, True)
                        tokens.extend(nested)
                        tokens.append(("barrier", ""))
                        ambiguous = ambiguous or bad
                        if not nested_closed:
                            ambiguous = ambiguous or marker(
                                value[template_start:])
                            break
                    else:
                        literal.append(char)
                        cursor += 1
                if not closed:
                    ambiguous = ambiguous or marker(value[template_start:])
                elif not expressions:
                    tokens.append(("str", "".join(literal)))
                continue
            if value.startswith("//", cursor):
                end = value.find("\n", cursor + 2)
                cursor = len(value) if end < 0 else end + 1
                continue
            if value.startswith("/*", cursor):
                end = value.find("*/", cursor + 2)
                if end < 0:
                    ambiguous = ambiguous or marker(value[cursor:])
                    cursor = len(value)
                else:
                    cursor = end + 2
                continue
            if char == "/" and regex_allowed(tokens):
                regex_start = cursor
                cursor += 1
                escaped = False
                in_class = False
                closed = False
                while cursor < len(value):
                    current = value[cursor]
                    if escaped:
                        escaped = False
                    elif current == "\\":
                        escaped = True
                    elif current == "[":
                        in_class = True
                    elif current == "]" and in_class:
                        in_class = False
                    elif current == "/" and not in_class:
                        cursor += 1
                        while cursor < len(value) and value[cursor].isalpha():
                            cursor += 1
                        closed = True
                        break
                    elif current in "\r\n":
                        break
                    cursor += 1
                if not closed:
                    ambiguous = ambiguous or marker(value[regex_start:cursor])
                tokens.append(("barrier", ""))
                continue
            if identifier_start(char) or value.startswith("\\u", cursor):
                decoded = []
                malformed = False
                first = True
                while cursor < len(value):
                    current = value[cursor]
                    if current == "\\":
                        part, following, valid = identifier_escape(cursor)
                        allowed = (identifier_start(part) if first else
                                   identifier_part(part)) if valid else False
                        if not valid or not allowed:
                            malformed = True
                            cursor = max(cursor + 1, following)
                            break
                    else:
                        allowed = (identifier_start(current) if first else
                                   identifier_part(current))
                        if not allowed:
                            break
                        part = current
                        following = cursor + 1
                    decoded.append(part)
                    cursor = following
                    first = False
                tokens.append(("bad_id" if malformed else "id",
                               "".join(decoded)))
                continue
            if stop_brace and char == "{":
                brace_depth += 1
            elif stop_brace and char == "}":
                brace_depth -= 1
            tokens.append(("punct", char))
            cursor += 1
        return tokens, cursor, ambiguous, not stop_brace

    tokens, _cursor, ambiguous, _closed = scan()
    if ambiguous:
        return True

    def static_bracket(index):
        if index >= len(tokens) or tokens[index] != ("punct", "["):
            return None, index, False
        cursor = index + 1
        if cursor >= len(tokens) or tokens[cursor][0] != "str":
            return None, index, False
        result = tokens[cursor][1]
        cursor += 1
        while (cursor + 1 < len(tokens) and
               tokens[cursor] == ("punct", "+") and
               tokens[cursor + 1][0] == "str"):
            result += tokens[cursor + 1][1]
            cursor += 2
        if cursor >= len(tokens):
            return result, cursor, True
        if tokens[cursor] != ("punct", "]"):
            return None, index, False
        return result, cursor + 1, False

    def path_state(parts):
        if not parts:
            return None
        first = parts[0].casefold()
        if first in CODEX_COLLAB_NATIVE_TOOL_NAMES:
            return "known"
        for prefix in ("multi_agent_v1__", "collaboration__"):
            if first.startswith(prefix):
                return ("known" if first[len(prefix):] in
                        CODEX_COLLAB_NATIVE_TOOL_NAMES else "unknown")
        if first == "collaboration":
            if len(parts) == 1:
                return "namespace"
            return ("known" if parts[1].casefold() in
                    CODEX_COLLAB_NATIVE_TOOL_NAMES else "unknown")
        return None

    def direct_invocation(index):
        if (index and tokens[index - 1][0] == "id" and
                tokens[index - 1][1].casefold() == "function"):
            return False
        cursor = index + 1
        if (cursor + 2 < len(tokens) and
                tokens[cursor:cursor + 3] == [
                    ("punct", "?"), ("punct", "."), ("punct", "(")]):
            cursor += 2
        if cursor >= len(tokens) or tokens[cursor] != ("punct", "("):
            return False
        depth = 0
        while cursor < len(tokens):
            if tokens[cursor] == ("punct", "("):
                depth += 1
            elif tokens[cursor] == ("punct", ")"):
                depth -= 1
                if depth == 0:
                    cursor += 1
                    return (cursor >= len(tokens) or
                            tokens[cursor] != ("punct", "{"))
            cursor += 1
        return True

    def optional_operator(index, following):
        return (index + 2 < len(tokens) and
                tokens[index] == ("punct", "?") and
                tokens[index + 1] == ("punct", ".") and
                tokens[index + 2] == ("punct", following))

    def call_at(index):
        return (index < len(tokens) and
                (tokens[index] == ("punct", "(") or
                 optional_operator(index, "(")))

    def tools_path(index):
        if (index >= len(tokens) or tokens[index][0] != "id" or
                tokens[index][1].casefold() != "tools"):
            return False, [], None, index, False
        cursor = index + 1
        parts = []
        incomplete = False
        while cursor < len(tokens):
            optional = (cursor + 1 < len(tokens) and
                        tokens[cursor:cursor + 2] == [
                            ("punct", "?"), ("punct", ".")])
            if tokens[cursor] == ("punct", ".") or optional:
                following = cursor + (2 if optional else 1)
                if (following < len(tokens) and
                        tokens[following] == ("punct", "[")):
                    part, following, truncated = static_bracket(following)
                    if part is None:
                        incomplete = True
                        break
                    parts.append(part)
                    cursor = following
                    incomplete = incomplete or truncated
                    if truncated:
                        break
                    continue
                if (following >= len(tokens) or
                        tokens[following][0] not in {"id", "bad_id"}):
                    incomplete = True
                    break
                parts.append(tokens[following][1])
                incomplete = incomplete or tokens[following][0] == "bad_id"
                cursor = following + 1
                if incomplete:
                    break
                continue
            part, following, truncated = static_bracket(cursor)
            if part is None:
                break
            parts.append(part)
            cursor = following
            incomplete = incomplete or truncated
            if truncated:
                break
        return True, parts, path_state(parts), cursor, incomplete

    scopes = [{}]
    function_scopes = [True]

    def bind(name, collaboration, declaration="let"):
        target = len(scopes) - 1
        if declaration == "var":
            for candidate in range(len(scopes) - 1, -1, -1):
                if function_scopes[candidate]:
                    target = candidate
                    break
        scopes[target][name.casefold()] = bool(collaboration)

    def assign(name, collaboration):
        folded = name.casefold()
        for scope in reversed(scopes):
            if folded in scope:
                scope[folded] = bool(collaboration)
                return
        scopes[-1][folded] = bool(collaboration)

    def binding_state(name):
        folded = name.casefold()
        for scope in reversed(scopes):
            if folded in scope:
                return scope[folded]
        return None

    def assignment_operator(index):
        if index >= len(tokens) or tokens[index] != ("punct", "="):
            return False
        before = tokens[index - 1] if index else None
        after = tokens[index + 1] if index + 1 < len(tokens) else None
        return (before != ("punct", "=") and
                after not in {("punct", "="), ("punct", ">")})

    def source_state(index):
        found, _parts, state, _cursor, incomplete = tools_path(index)
        if not found:
            return False, False
        if state == "unknown" or (state and incomplete):
            return False, True
        return state == "known", False

    def destructuring(index):
        opening = index + 1
        if (opening >= len(tokens) or
                tokens[opening] != ("punct", "{")):
            return None
        cursor = opening + 1
        entries = []
        while cursor < len(tokens) and tokens[cursor] != ("punct", "}"):
            if tokens[cursor] == ("punct", ","):
                cursor += 1
                continue
            if tokens[cursor][0] != "id":
                return None
            key = tokens[cursor][1]
            alias = key
            cursor += 1
            if cursor < len(tokens) and tokens[cursor] == ("punct", ":"):
                cursor += 1
                if cursor >= len(tokens) or tokens[cursor][0] != "id":
                    return None
                alias = tokens[cursor][1]
                cursor += 1
            entries.append((key, alias))
            if (cursor < len(tokens) and
                    tokens[cursor] not in {
                        ("punct", ","), ("punct", "}")}):
                return None
        if cursor >= len(tokens):
            return None
        closing = cursor
        equals = closing + 1
        if not assignment_operator(equals):
            return entries, None, False
        found, parts, state, _end, incomplete = tools_path(equals + 1)
        if not found:
            return entries, None, False
        if state == "unknown" or (state and incomplete):
            return entries, None, True
        return entries, parts, False

    def function_parameters(brace):
        arrow = False
        close = brace - 1
        if (brace >= 3 and tokens[brace - 2:brace] == [
                ("punct", "="), ("punct", ">")]):
            arrow = True
            close = brace - 3
            if close >= 0 and tokens[close][0] == "id":
                return [tokens[close][1]]
        if close < 0 or tokens[close] != ("punct", ")"):
            return None
        depth = 1
        opening = close - 1
        while opening >= 0:
            if tokens[opening] == ("punct", ")"):
                depth += 1
            elif tokens[opening] == ("punct", "("):
                depth -= 1
                if depth == 0:
                    break
            opening -= 1
        if opening < 0:
            return None
        function = (
            opening >= 1 and tokens[opening - 1][0] == "id" and
            tokens[opening - 1][1].casefold() == "function") or (
            opening >= 2 and tokens[opening - 2][0] == "id" and
            tokens[opening - 2][1].casefold() == "function")
        catch = (opening >= 1 and tokens[opening - 1][0] == "id" and
                 tokens[opening - 1][1].casefold() == "catch")
        if catch:
            if (close == opening + 2 and
                    tokens[opening + 1][0] == "id"):
                return [tokens[opening + 1][1]]
            return None
        if not arrow and not function and not catch:
            return None
        parameters = []
        cursor = opening + 1
        while cursor < close:
            if tokens[cursor][0] == "id":
                parameters.append(tokens[cursor][1])
            cursor += 1
        return parameters

    def expression_arrow_scopes():
        starts = {}
        for equals in range(len(tokens) - 1):
            if tokens[equals:equals + 2] != [
                    ("punct", "="), ("punct", ">")]:
                continue
            before = equals - 1
            parameters = None
            if before >= 0 and tokens[before][0] == "id":
                parameters = [tokens[before][1]]
            elif before >= 0 and tokens[before] == ("punct", ")"):
                depth = 1
                opening = before - 1
                while opening >= 0:
                    if tokens[opening] == ("punct", ")"):
                        depth += 1
                    elif tokens[opening] == ("punct", "("):
                        depth -= 1
                        if depth == 0:
                            break
                    opening -= 1
                if opening >= 0:
                    parameters = []
                    expect_identifier = True
                    for cursor in range(opening + 1, before):
                        token = tokens[cursor]
                        if expect_identifier and token[0] == "id":
                            parameters.append(token[1])
                            expect_identifier = False
                        elif (not expect_identifier and
                              token == ("punct", ",")):
                            expect_identifier = True
                        else:
                            parameters = None
                            break
                    if expect_identifier and parameters:
                        parameters = None
            body = equals + 2
            if (parameters is None or body >= len(tokens) or
                    tokens[body] == ("punct", "{")):
                continue
            delimiters = []
            cursor = body
            valid = True
            pairs = {"(": ")", "[": "]", "{": "}"}
            while cursor < len(tokens):
                token = tokens[cursor]
                if token[0] == "punct" and token[1] in pairs:
                    delimiters.append(pairs[token[1]])
                elif token[0] == "punct" and token[1] in ")]}":
                    if delimiters and delimiters[-1] == token[1]:
                        delimiters.pop()
                    elif not delimiters:
                        break
                    else:
                        valid = False
                        break
                elif (not delimiters and token in {
                        ("punct", ";"), ("punct", ",")}):
                    break
                cursor += 1
            if delimiters:
                valid = False
            if valid:
                starts.setdefault(body, []).append((cursor, parameters))
        return starts

    arrow_starts = expression_arrow_scopes()
    arrow_ends = []

    index = 0
    while index < len(tokens):
        while arrow_ends and arrow_ends[-1] == index:
            scopes.pop()
            function_scopes.pop()
            arrow_ends.pop()
        for end, parameters in arrow_starts.get(index, []):
            scopes.append({})
            function_scopes.append(True)
            arrow_ends.append(end)
            for parameter in parameters:
                bind(parameter, False)
        token = tokens[index]
        if token == ("punct", "{"):
            parameters = function_parameters(index)
            scopes.append({})
            function_scopes.append(parameters is not None)
            for parameter in parameters or []:
                bind(parameter, False)
            index += 1
            continue
        if token == ("punct", "}"):
            if len(scopes) > 1:
                scopes.pop()
                function_scopes.pop()
            index += 1
            continue
        if (token[0] == "id" and
                token[1].casefold() in {"function", "class"} and
                index + 1 < len(tokens) and tokens[index + 1][0] == "id"):
            bind(tokens[index + 1][1], False)
        if token[0] == "id" and token[1].casefold() in {
                "const", "let", "var"}:
            observed = destructuring(index)
            if observed is not None:
                entries, base_parts, uncertain = observed
                if uncertain:
                    return True
                for key, alias in entries:
                    state = (path_state(base_parts + [key])
                             if base_parts is not None else None)
                    if state == "unknown":
                        return True
                    bind(alias, state == "known", token[1].casefold())
            elif index + 1 < len(tokens) and tokens[index + 1][0] == "id":
                name = tokens[index + 1][1]
                collaboration = False
                uncertain = False
                if assignment_operator(index + 2):
                    collaboration, uncertain = source_state(index + 3)
                if uncertain:
                    return True
                bind(name, collaboration, token[1].casefold())
        if (token[0] == "id" and index + 1 < len(tokens) and
                assignment_operator(index + 1) and
                not (index and tokens[index - 1] in {
                    ("punct", "."), ("punct", "]")})):
            collaboration, uncertain = source_state(index + 2)
            if uncertain:
                return True
            assign(token[1], collaboration)
        found, _parts, state, cursor, incomplete = tools_path(index)
        if found:
            if state and call_at(cursor):
                return True
            if state == "unknown" or (state and incomplete):
                return True
        if token[0] == "bad_id":
            if (path_state([token[1]]) is not None or
                    any(item[0] == "id" and path_state([item[1]]) is not None
                        for item in tokens[index + 1:index + 5])):
                return True
            index += 1
            continue
        if token[0] == "id":
            name = token[1].casefold()
            if not (index and tokens[index - 1] in {
                    ("punct", "."), ("punct", "]")}):
                direct_state = path_state([name])
                called = direct_invocation(index)
                binding = binding_state(name)
                if called and binding is not None:
                    if binding:
                        return True
                elif direct_state and called:
                    return True
                if direct_state == "unknown" and binding is not False:
                    return True
        index += 1
    return False


def _codex_native_output_objects(value):
    texts = []
    if type(value) is str:
        texts.append(value)
    elif isinstance(value, list):
        for item in value:
            if (isinstance(item, dict) and
                    item.get("type") in ("input_text", "output_text") and
                    type(item.get("text")) is str):
                texts.append(item["text"])
    for text in texts:
        candidate = text.strip()
        if (not candidate.startswith("{") or
                not candidate.endswith("}") or
                len(candidate.encode("utf-8")) > 1024 * 1024):
            continue
        try:
            yield _strict_object(candidate)
        except (ValueError, TypeError, json.JSONDecodeError):
            continue


def _codex_native_output_has_collaboration(value):
    for candidate in _codex_native_output_objects(value):
        keys = set(candidate)
        if (type(candidate.get("agent_id")) is str and
                candidate["agent_id"] and
                keys <= {"agent_id", "nickname"}):
            return True
        statuses = candidate.get("status")
        if (isinstance(statuses, dict) and
                keys <= {"status", "timed_out"} and
                any(type(child) is str and
                    CODEX_COLLAB_NATIVE_CHILD_ID_PATTERN.fullmatch(child)
                    for child in statuses)):
            return True
    return False


def _codex_native_message_has_collaboration(payload):
    if payload.get("role") != "user" or not isinstance(
            payload.get("content"), list):
        return False
    return any(
        isinstance(item, dict) and
        item.get("type") in ("input_text", "output_text") and
        type(item.get("text")) is str and
        "<subagent_notification>" in item["text"].casefold()
        for item in payload["content"])


def _codex_native_collaboration_present(objects):
    """Detect executed collaboration from structural native action records."""
    for record in objects:
        if record.get("type") != "response_item":
            continue
        payload = record.get("payload")
        if not isinstance(payload, dict):
            continue
        kind = payload.get("type")
        folded_kind = kind.casefold() if type(kind) is str else ""
        if folded_kind in ("custom_tool_call", "function_call"):
            name = payload.get("name")
            if _codex_native_collaboration_name(name):
                return True
            if (type(name) is str and name.casefold() in ("exec", "functions.exec")
                    and (_codex_native_exec_has_collaboration(
                        payload.get("input")) or
                         _codex_native_exec_has_collaboration(
                             payload.get("arguments")))):
                return True
        elif folded_kind in (
                "custom_tool_call_output", "function_call_output"):
            if _codex_native_output_has_collaboration(payload.get("output")):
                return True
        elif folded_kind == "message":
            if _codex_native_message_has_collaboration(payload):
                return True
    return False


def codex_native_collaboration_status(raw_session):
    """Return PRESENT, ABSENT, or INVALID for a closed Codex native stream."""
    try:
        session_bytes = _raw_capture_bytes(raw_session)
        text = session_bytes.decode("utf-8")
        objects = [_strict_object(line) for line in text.splitlines()
                   if line.strip()]
    except (UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        return "INVALID"
    if not objects or not _codex_native_rows_valid(objects):
        return "INVALID"
    return ("PRESENT" if _codex_native_collaboration_present(objects)
            else "ABSENT")


def corroborate_session(raw_stdout, raw_session, host, binding, trace,
                        profile=None, process_started=None):
    """Corroborate lineage/action identity from the distinct native stream."""
    if host not in ("codex", "claude"):
        return "INVALID"
    if raw_session is None or raw_session == "" or raw_session == b"":
        return "MISSING"
    if process_started is None:
        process_started = {}
    binding_valid = (_valid_codex_binding(binding, require_native=True)
                     if host == "codex" else
                     _valid_claude_binding(binding))
    if (not binding_valid or not isinstance(trace, dict) or
            not isinstance(trace.get("actions"), list) or
            any(not isinstance(action, dict) or
                type(action.get("id")) is not str or not action["id"]
                for action in trace["actions"]) or
            not isinstance(process_started, dict)):
        return "INVALID"
    action_ids = [action["id"] for action in trace["actions"]]
    if len(action_ids) != len(set(action_ids)):
        return "INVALID"
    try:
        stdout_bytes = _raw_capture_bytes(raw_stdout)
        session_bytes = _raw_capture_bytes(raw_session)
    except ValueError:
        return "INVALID"
    if session_bytes == stdout_bytes:
        return "SUBSTITUTED"
    try:
        text = session_bytes.decode("utf-8")
        objects = [_strict_object(line) for line in text.splitlines()
                   if line.strip()]
    except (UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        return "INVALID"
    if not objects:
        return "INVALID"
    if host == "codex":
        if not _codex_native_rows_valid(objects):
            return "INVALID"
        if _codex_native_collaboration_present(objects):
            return "INVALID"
        metas = [obj for obj in objects if obj.get("type") == "session_meta"]
        turns = [obj for obj in objects if obj.get("type") == "turn_context"]
        if len(metas) != 1 or len(turns) != 1:
            return "INVALID"
        meta = metas[0].get("payload")
        turn = turns[0].get("payload")
        if not isinstance(meta, dict) or not isinstance(turn, dict):
            return "INVALID"
        repo = _codex_native_repo_policy(profile)
        if repo is None:
            return "INVALID"
        case_sensitive = repo["case_sensitive"]
        process_cwd = process_started.get("cwd")
        requested_model = process_started.get("requested_model")
        observed_model = turn.get("model")
        if type(case_sensitive) is not bool:
            return "INVALID"
        if (meta.get("id") != binding.get("thread_id") or
                meta.get("session_id") != binding.get("thread_id") or
                binding.get("stdout_turn_ordinal") != 1 or
                turn.get("turn_id") != binding.get("native_turn_id") or
                not _same_path(turn.get("cwd"), repo.get("lexical_root"),
                               case_sensitive=case_sensitive) or
                not _same_path(meta.get("cwd"), repo.get("lexical_root"),
                               case_sensitive=case_sensitive) or
                type(process_cwd) is not str or not process_cwd or
                not _same_path(process_cwd, repo.get("lexical_root"),
                               case_sensitive=case_sensitive) or
                type(requested_model) is not str or not requested_model or
                type(observed_model) is not str or not observed_model or
                observed_model != requested_model):
            return "INVALID"
        meta_time = _parse_utc(metas[0].get("timestamp") or
                               meta.get("timestamp"))
        turn_time = _parse_utc(turns[0].get("timestamp"))
        process_time = _parse_utc((process_started or {}).get("started_at"))
        if (not meta_time or not turn_time or not process_time or
                not _codex_startup_timestamps_valid(
                    objects, metas[0], turns[0], process_started)):
            return "INVALID"
        return "VALID"
    types = [obj.get("type") for obj in objects]
    if (any(type(value) is not str for value in types) or
            not set(types).intersection(
                {"system", "assistant", "user", "result"})):
        return "INVALID"
    scalars = set()
    for obj in objects:
        scalars.update(_scalar_strings(obj))
    if not binding or any(value not in scalars for value in binding.values()):
        return "INVALID"
    if any(action["id"] not in scalars for action in trace["actions"]):
        return "INVALID"
    return "VALID"


def add_host_finding(normalized, code, host_status="INVALID"):
    normalized.setdefault("host_findings", []).append(
        {"code": code, "classification": "fail-closed"})
    normalized["invalid"] = True
    normalized["host_status"] = host_status
    return normalized


def build_matrix(normalized, replay_spec, preimages, profile,
                 profile_post_status="PASS", formal=True):
    classifier_profile = profile if profile_post_status == "PASS" else None
    adjudications = {}
    for spec in replay_spec["checks"]:
        adjudications[spec["key"]] = adjudicate_path_order(
            normalized, spec["reads"], spec["write"], preimages,
            profile=classifier_profile, formal=formal)
    return {"schema": MATRIX_SCHEMA,
            "raw_transforms": {
                "host-stdout.raw": (replay_spec["host"] +
                                    "-typed-action-normalizer-v2"),
                "host-session.raw": "lineage-corroboration-only"},
            "specs": adjudications}


def replay_capture(root, formal=True):
    """Verify all custody hashes without consulting ambient repository state."""
    try:
        required = _CAPTURE_FILES + ("host-read-manifest.json",)
        if any(not os.path.isfile(os.path.join(root, name))
               for name in required):
            raise ValueError("missing capture file")
        profile = _read_json_file(os.path.join(root,
                                               "host-read-profile.json"))
        preimages = _read_json_file(os.path.join(root,
                                                 "host-read-preimages.json"))
        replay_spec = _read_json_file(os.path.join(
            root, "host-read-replay-spec.json"))
        pre_spawn = _read_json_file(os.path.join(root,
                                                  "host-read-pre-spawn.json"))
        terminal = _read_json_file(os.path.join(root,
                                                 "host-read-terminal.json"))
        manifest = _read_json_file(os.path.join(root,
                                                 "host-read-manifest.json"))
        trace = _read_json_file(os.path.join(root, "host-tool-trace.json"))
        matrix = _read_json_file(os.path.join(root, "host-read-matrix.json"))
        post_probe = _read_json_file(os.path.join(
            root, "host-read-post-probe.json"))
        if (not isinstance(pre_spawn, dict) or
                not isinstance(manifest, dict) or
                not isinstance(replay_spec, dict) or
                not isinstance(post_probe, dict) or
                not _valid_terminal_record(terminal)):
            raise ValueError("capture object schema invalid")
        if (validate_profile(profile, formal=False)["host_status"] != "PASS" or
                (formal and profile.get("authority") !=
                 "mechanically-minted")):
            raise ValueError("profile invalid")
        if validate_preimages(preimages)["status"] != "PASS":
            raise ValueError("preimages invalid")
        if set(pre_spawn) != {"schema", "created_before_spawn",
                             "profile_sha256", "preimages_sha256",
                             "fixture_sha256",
                             "replay_spec_sha256"}:
            raise ValueError("pre-spawn binds post-spawn facts")
        if (pre_spawn.get("schema") != PRESPAWN_SCHEMA or
                pre_spawn.get("created_before_spawn") is not True):
            raise ValueError("pre-spawn invalid")
        if not _validate_replay_spec(replay_spec, formal):
            raise ValueError("replay recipe invalid")
        if (not _valid_terminal_trace(trace, formal) or
                not _valid_terminal_matrix(matrix, formal)):
            raise ValueError("derivative schema invalid")
        if manifest.get("schema") != MANIFEST_SCHEMA or \
                set(manifest.get("files", {})) != set(_CAPTURE_FILES):
            raise ValueError("manifest invalid")
        actual = {name: _file_sha256(os.path.join(root, name))
                  for name in _CAPTURE_FILES}
        if manifest["files"] != actual:
            raise ValueError("manifest hash mismatch")
        if terminal.get("hashes") != {
                name: actual[name] for name in _CAPTURE_FILES[:-1]}:
            raise ValueError("terminal hash mismatch")
        if (pre_spawn.get("profile_sha256") !=
                actual["host-read-profile.json"] or
                pre_spawn.get("preimages_sha256") !=
                actual["host-read-preimages.json"] or
                pre_spawn.get("fixture_sha256") !=
                actual["host-read-fixture.raw"] or
                pre_spawn.get("replay_spec_sha256") !=
                actual["host-read-replay-spec.json"]):
            raise ValueError("pre-spawn hash mismatch")
        if replay_spec.get("mode") == "formal-v2":
            intent_path = os.path.join(root, "run-intent.json")
            process_path = os.path.join(root, "process-started.json")
            if not os.path.isfile(intent_path) or not os.path.isfile(
                    process_path):
                raise ValueError("parent custody record missing")
            intent = _read_json_file(intent_path)
            process = _read_json_file(process_path)
            fixture_bytes = open(os.path.join(
                root, "host-read-fixture.raw"), "rb").read()
            fixture = json.loads(fixture_bytes.decode("utf-8"),
                                 object_pairs_hook=_unique_pairs)
            fixture_checks = [
                {"key": spec["key"],
                 "reads": list(spec.get("reads") or []),
                 "write": spec.get("write")}
                for spec in (fixture.get("host_checks") or {}).get(
                    "specs", [])
                if spec.get("kind") == "path_access_order"]
            if (_file_sha256(intent_path) !=
                    replay_spec["run_intent_sha256"] or
                    intent.get("fixture_sha256") !=
                    replay_spec["fixture_sha256"] or
                    _sha256(fixture_bytes) !=
                    replay_spec["fixture_sha256"] or
                    fixture_checks != replay_spec["checks"] or
                    process.get("host_read_pre_spawn_sha256") !=
                    actual["host-read-pre-spawn.json"]):
                raise ValueError("parent custody chain mismatch")
            profile = _admit_persisted_profile(
                profile, expected_host=replay_spec["host"])
            if (not _profile_matches_preimages(profile, preimages) or
                    not _profile_matches_replay_spec(profile, replay_spec)):
                raise ValueError("profile replay boundary mismatch")
            recomputed_post_status = validate_profile(
                profile, post_probe=post_probe, formal=True)["host_status"]
            if (terminal.get("post_probe_sha256") !=
                    _sha256(_canonical_bytes(post_probe)) or
                    terminal.get("profile_post_status") !=
                    recomputed_post_status):
                raise ValueError("post-probe adjudication mismatch")
            raw_stdout = open(os.path.join(root, "host-stdout.raw"),
                              "rb").read().decode("utf-8")
            raw_session = open(os.path.join(root, "host-session.raw"),
                               "rb").read()
            binding = terminal.get("binding")
            if replay_spec["host"] == "codex":
                if not _valid_codex_binding(
                        binding, require_native=bool(binding),
                        allow_empty=True):
                    raise ValueError("terminal binding invalid")
                derived = derive_codex_binding(raw_stdout)
                lineage_valid = bool(derived) and all(
                    binding.get(key) == value for key, value in
                    (derived or {}).items()) and isinstance(
                        binding.get("native_turn_id"), str)
                normalized = normalize_codex(
                    raw_stdout, profile=profile, binding=binding,
                    formal=formal)
            else:
                if not _valid_claude_binding(binding, allow_empty=True):
                    raise ValueError("terminal binding invalid")
                derived = derive_claude_binding(raw_stdout)
                lineage_valid = derived is not None and binding == derived
                normalized = normalize_claude(
                    raw_stdout,
                    requested_tools=replay_spec["requested_tools"],
                    binding=binding, profile=profile, formal=formal)
            session_status = corroborate_session(
                raw_stdout, raw_session, replay_spec["host"], binding,
                normalized, profile=profile, process_started=process)
            if not lineage_valid:
                add_host_finding(normalized, "lineage-binding-invalid")
            if recomputed_post_status != "PASS":
                add_host_finding(normalized, "profile-post-probe-invalid")
            if session_status != "VALID":
                add_host_finding(normalized, "native-session-unbound")
            terminal_kind = terminal.get("host_terminal_kind")
            if terminal_kind == "error":
                add_host_finding(normalized, "host-terminal-error",
                                 host_status="ERROR")
            elif terminal_kind == "invalid":
                add_host_finding(normalized, "host-terminal-invalid")
            regenerated = build_matrix(
                normalized, replay_spec, preimages, profile,
                profile_post_status=terminal.get("profile_post_status"),
                formal=formal)
            if _canonical_bytes(normalized) != _canonical_bytes(trace):
                raise ValueError("trace does not regenerate")
            if _canonical_bytes(regenerated) != _canonical_bytes(matrix):
                raise ValueError("matrix does not regenerate")
            if terminal.get("actual_tools") != \
                    list(normalized.get("observed_tools") or []):
                raise ValueError("actual tool inventory mismatch")
            if terminal.get("normalized_host_status") != \
                    normalized.get("host_status"):
                raise ValueError("normalized host status mismatch")
            if (terminal.get("session_status") != session_status or
                    terminal.get("session_bound") !=
                     (session_status == "VALID")):
                raise ValueError("native session status mismatch")
        else:
            recomputed_post_status = validate_profile(
                profile, post_probe=post_probe, formal=False)["host_status"]
            if (terminal.get("post_probe_sha256") !=
                    _sha256(_canonical_bytes(post_probe)) or
                    terminal.get("profile_post_status") !=
                    recomputed_post_status):
                raise ValueError("post-probe adjudication mismatch")
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return {"status": "INVALID"}
    return {"status": "PASS", "custody_status": "PASS",
            "host_status": trace.get("host_status", "INVALID"),
            "matrix": matrix, "trace": trace,
            "snapshot_sha256": snapshot_digest(preimages)}


def verify_projection(value):
    """Validate and count an immutable rejected-policy diagnostic projection."""
    if not isinstance(value, dict) or not isinstance(value.get("rows"), list):
        return {"status": "INVALID", "counts": {}}
    allowed = {"PASS", "INVALID_OR_INCOMPLETE"}
    seen = set()
    counts = {name: 0 for name in allowed}
    for row in value["rows"]:
        if (not isinstance(row, dict) or
                not isinstance(row.get("run"), str) or row["run"] in seen or
                not re.fullmatch(r"[0-9a-f]{64}",
                                 str(row.get("raw_sha256", ""))) or
                row.get("disposition") not in allowed):
            return {"status": "INVALID", "counts": {}}
        seen.add(row["run"])
        counts[row["disposition"]] += 1
    return {"status": "PASS", "counts": counts}
