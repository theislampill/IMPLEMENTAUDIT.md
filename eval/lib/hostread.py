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

SUPPORTED_READERS = ("cat", "grep", "head", "rg", "sed", "tail")
SUPPORTED_CLAUDE = frozenset(
    ("Read", "Write", "Edit", "Bash", "Grep", "Glob", "Skill",
     "Task", "Workflow"))


_PROFILE_CAPABILITY = object()


class _MintedProfile(dict):
    """Process-local capability returned only by mechanical profile minting.

    Persisted JSON is promoted back to this type only after replay verifies the
    pre-spawn and parent custody chain.  A caller-created dictionary therefore
    cannot grant itself formal authority by copying the serialized marker.
    """

    def __init__(self, value, capability=None):
        if capability is not _PROFILE_CAPABILITY:
            raise TypeError("formal profile capability is internal")
        super().__init__(value)


def _mint_profile(value):
    return _MintedProfile(value, _PROFILE_CAPABILITY)


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
    value = json.loads(line, object_pairs_hook=unique)
    if not isinstance(value, dict):
        raise ValueError("host event is not a JSON object")
    return value


def _within(path, root, case_sensitive=True):
    path = str(path or "").replace("\\", "/").rstrip("/")
    root = str(root or "").replace("\\", "/").rstrip("/")
    if not case_sensitive:
        path = path.casefold()
        root = root.casefold()
    return bool(path and root and (path == root or path.startswith(root + "/")))


def _profile_result(ok, reason=None):
    result = {"host_status": "PASS" if ok else "INVALID",
              "property_status": "PASS" if ok else "INCOMPLETE"}
    if reason:
        result["reason"] = reason
    return result


def validate_profile(profile, post_probe=None, formal=True,
                     writable_roots=()):
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
    authority = profile.get("authority")
    if formal and authority != "mechanically-minted":
        return _profile_result(False, "profile authority")
    if not formal and authority not in ("mechanically-minted",
                                        "test-fixture-only"):
        return _profile_result(False, "profile authority")
    repo = profile.get("repo")
    if (profile.get("host") == "claude" and isinstance(repo, dict) and
            isinstance(repo.get("lexical_root"), str) and
            isinstance(repo.get("real_root"), str) and
            type(repo.get("case_sensitive")) is bool):
        native_tools = profile.get("native_tools")
        if (not isinstance(native_tools, dict) or
                not isinstance(native_tools.get("requested"), list) or
                any(not isinstance(tool, str) or not tool
                    for tool in native_tools["requested"]) or
                not re.fullmatch(r"[0-9a-f]{64}",
                                 str(profile.get("probe_sha256", "")))):
            return _profile_result(False, "native profile shape")
        if post_probe is not None and post_probe != {
                "native_tools": native_tools}:
            return _profile_result(False, "native profile drift")
        return _profile_result(True)
    shell = profile.get("shell")
    wrapper = profile.get("outer_wrapper")
    environment = profile.get("environment")
    executables = profile.get("executables")
    if (not isinstance(repo, dict) or
            not isinstance(repo.get("lexical_root"), str) or
            not isinstance(repo.get("real_root"), str) or
            type(repo.get("case_sensitive")) is not bool or
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
        post_shell = post_probe.get("shell") or {}
        for field in ("realpath", "sha256", "stat"):
            if post_shell.get(field) != shell.get(field):
                return _profile_result(False, "shell drift")
        post_exec = post_probe.get("executables")
        if post_exec != executables:
            return _profile_result(False, "executable resolution drift")
    return _profile_result(True)


def _admit_persisted_profile(profile):
    """Restore formal capability after replay has verified parent custody."""
    if not isinstance(profile, dict) or \
            profile.get("authority") != "mechanically-minted":
        raise ValueError("persisted profile authority")
    admitted = _mint_profile(profile)
    if validate_profile(admitted, formal=True)["host_status"] != "PASS":
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
            if (_sha256(data) != entry.get("sha256") or
                    len(data) != entry.get("size") or
                    entry.get("relative_path") != relative or
                    entry.get("symlink_free") is not True or
                    not _within(entry.get("canonical_path"),
                                repo.get("lexical_root"),
                                case_sensitive=repo["case_sensitive"])):
                raise ValueError("preimage mismatch")
    except (ValueError, TypeError, base64.binascii.Error):
        return {"status": "INVALID"}
    return {"status": "PASS"}


def snapshot_digest(preimages):
    return _sha256(_canonical_bytes(preimages))


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
    root = preimages["repo"]["lexical_root"].rstrip("/")
    case_sensitive = preimages["repo"]["case_sensitive"]
    if not _within(candidate, root, case_sensitive=case_sensitive):
        return None
    return candidate


def _path_matches(path, target, preimages):
    entry = (preimages.get("targets") or {}).get(target)
    observed = _normalize_path(path, preimages)
    case_sensitive = (preimages.get("repo") or {}).get(
        "case_sensitive", True)
    return bool(entry and observed and _within(
        observed, entry["canonical_path"], case_sensitive=case_sensitive) and
        _within(entry["canonical_path"], observed,
                case_sensitive=case_sensitive))


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
        return self._append({"id": action_id or f"invalid@{ordinal}",
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

    def finish(self):
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


def _valid_todo_items(items):
    return (isinstance(items, list) and all(
        isinstance(item, dict) and set(item) == {"text", "completed"} and
        isinstance(item.get("text"), str) and
        type(item.get("completed")) is bool
        for item in items))


def _profile_allows_wrapper(profile, formal):
    return validate_profile(profile, formal=formal)["host_status"] == "PASS"


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
    binding = binding or {}
    active_thread = None
    active_turn = None
    turns = 0
    for ordinal, line in enumerate(str(raw_stdout or "").splitlines(), 1):
        try:
            event = _strict_object(line)
        except (ValueError, json.JSONDecodeError, TypeError) as exc:
            machine.invalid_action(ordinal, str(exc))
            continue
        event_type = event.get("type")
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
            if (active_turn is not None or turns != 1 or
                    (binding.get("thread_id") and
                     thread != binding["thread_id"]) or
                    (binding.get("turn_id") and
                     turn != binding["turn_id"])):
                machine.invalid_action(ordinal, "turn binding mismatch")
            else:
                active_turn = turn or binding.get("turn_id") or "<unique-turn>"
            continue
        if event_type == "turn.completed":
            turn = event.get("turn_id", active_turn)
            if active_turn is None or (binding.get("turn_id") and
                                       turn != binding["turn_id"]):
                machine.invalid_action(ordinal, "turn completion mismatch")
            active_turn = None
            continue
        if event_type not in ("item.started", "item.updated",
                              "item.completed"):
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
        if event_type == "item.completed" and item_type == "agent_message":
            if (item.get("status") not in (None, "completed") or
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
            if item_status not in (None, "completed"):
                machine.complete(action_id, ordinal, state="INVALID",
                                 reason="invalid todo completion")
            else:
                machine.complete(action_id, ordinal)
    result = machine.finish()
    result["requested_tools"] = []
    result["observed_tools"] = []
    return result


def _claude_result_metadata(event):
    metadata = event.get("tool_use_result")
    if metadata is None:
        return None
    return metadata if isinstance(metadata, dict) else "<malformed>"


def _result_path(metadata):
    if not isinstance(metadata, dict):
        return None
    if "filePath" in metadata:
        return metadata.get("filePath")
    file_obj = metadata.get("file")
    if file_obj is not None and not isinstance(file_obj, dict):
        return "<malformed>"
    return file_obj.get("filePath") if isinstance(file_obj, dict) else None


def _lexical_path(path):
    if not isinstance(path, str) or not path or "\x00" in path:
        return None
    text = path.replace("\\", "/")
    if any(part == ".." for part in text.split("/")):
        return None
    return str(PurePosixPath(text))


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
    binding = binding or {}
    requested = list(requested_tools or [])
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
            if not isinstance(tools, list) or any(not isinstance(t, str)
                                                 for t in tools):
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
                    invalid_input = _lexical_path(path) is None
                elif effect == "command":
                    invalid_input = not isinstance(command, str) or not command
                elif effect == "search":
                    invalid_input = (_lexical_path(path) is None or
                                     inputs.get("output_mode") not in
                                     ("content", "files_with_matches"))
                if (effect in ("read", "write", "search") and
                        isinstance(path, str) and path.startswith("/") and
                        (not isinstance(profile, dict) or
                         not _within(path, (profile.get("repo") or {}).get(
                             "lexical_root")))):
                    invalid_input = True
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
                result_path = _result_path(metadata)
                if result_path == "<malformed>":
                    malformed = True
                if (result_path is not None and action.get("path") and
                        _lexical_path(result_path) !=
                        _lexical_path(action.get("path"))):
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
    if (_within(observed, canonical, case_sensitive=case_sensitive) and
            _within(canonical, observed, case_sensitive=case_sensitive)):
        return "direct"
    if _within(canonical, observed, case_sensitive=case_sensitive):
        return "scope"
    return "unrelated"


def _finite_shell_tokens(command):
    """Tokenize only the deliberately finite, single-stage POSIX surface."""
    if not isinstance(command, str) or not command or "\x00" in command:
        return None
    # Shell composition, expansion, and alternate dialects are outside this
    # evidence grammar.  Redirection is handled below as a small explicit
    # exception; this is not intended to grow into a shell parser.
    if ("\n" in command or "\r" in command or "$" in command or
            "#" in command or
            "`" in command or any(text in command for text in
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
    if validate_profile(profile, formal=formal)["host_status"] != "PASS":
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
    for name, identity in (profile.get("executables") or {}).items():
        if argv0 == name or argv0 == identity.get("path"):
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
    return bool(left and right and left == right)


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
    if (spec.get("mode") != "formal-v2" or
            spec.get("host") not in ("codex", "claude") or
            not isinstance(spec.get("checks"), list) or
            not spec["checks"] or
            not isinstance(spec.get("requested_tools"), list) or
            any(not isinstance(tool, str) for tool in
                spec["requested_tools"]) or
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
    if replay_spec is None:
        replay_spec = {"schema": REPLAY_SCHEMA,
                       "mode": "custody-only-test"}
    if not _validate_replay_spec(replay_spec, formal):
        raise ValueError("invalid pre-spawn replay recipe")
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
    if not isinstance(trace, dict) or trace.get("schema") != TRACE_SCHEMA:
        raise ValueError("trace schema")
    if not isinstance(matrix, dict) or matrix.get("schema") != MATRIX_SCHEMA:
        raise ValueError("matrix schema")
    stdout_bytes = (raw_stdout if isinstance(raw_stdout, bytes) else
                    str(raw_stdout).encode("utf-8"))
    session_bytes = (raw_session if isinstance(raw_session, bytes) else
                     str(raw_session).encode("utf-8"))
    _write_new(os.path.join(root, "host-stdout.raw"), stdout_bytes)
    _write_new(os.path.join(root, "host-session.raw"), session_bytes)
    _write_new_json(os.path.join(root, "host-tool-trace.json"), trace)
    _write_new_json(os.path.join(root, "host-read-matrix.json"), matrix)
    _write_new_json(os.path.join(root, "host-read-post-probe.json"),
                    post_probe)
    bound = {name: _file_sha256(os.path.join(root, name))
             for name in _CAPTURE_FILES[:-1]}
    terminal = {"schema": TERMINAL_SCHEMA, "hashes": bound,
                "post_probe_sha256": _sha256(_canonical_bytes(post_probe)),
                "profile_post_status": profile_post_status,
                "binding": binding or {},
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
    for line in str(raw_stdout or "").splitlines():
        try:
            event = _strict_object(line)
        except (ValueError, TypeError, json.JSONDecodeError):
            continue
        if event.get("type") == "thread.started" and isinstance(
                event.get("thread_id"), str):
            threads.append(event["thread_id"])
        if event.get("type") == "turn.started":
            turn_id = event.get("turn_id")
            if turn_id is not None and not isinstance(turn_id, str):
                return None
            turns.append((event.get("thread_id"), turn_id))
    if len(threads) != 1 or len(turns) != 1 or \
            turns[0][0] not in (None, threads[0]):
        return None
    result = {"thread_id": threads[0], "stdout_turn_ordinal": 1}
    if turns[0][1] is not None:
        result["turn_id"] = turns[0][1]
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
    if not binding or not raw_session:
        return binding
    try:
        objects = [_strict_object(line) for line in bytes(raw_session).decode(
            "utf-8").splitlines() if line.strip()]
    except (UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        return binding
    turns = [obj.get("payload") or {} for obj in objects
             if obj.get("type") == "turn_context"]
    if len(turns) == 1 and isinstance(turns[0].get("turn_id"), str):
        result = dict(binding)
        result["native_turn_id"] = turns[0]["turn_id"]
        return result
    return binding


def corroborate_session(raw_stdout, raw_session, host, binding, trace,
                        profile=None, process_started=None):
    """Corroborate lineage/action identity from the distinct native stream."""
    if not raw_session:
        return "MISSING"
    stdout_bytes = (raw_stdout.encode("utf-8") if isinstance(raw_stdout, str)
                    else bytes(raw_stdout))
    session_bytes = (raw_session.encode("utf-8")
                     if isinstance(raw_session, str) else bytes(raw_session))
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
    types = {obj.get("type") for obj in objects}
    if host == "codex":
        if not types.intersection({"session_meta", "turn_context",
                                   "event_msg", "response_item"}):
            return "INVALID"
        metas = [obj for obj in objects if obj.get("type") == "session_meta"]
        turns = [obj for obj in objects if obj.get("type") == "turn_context"]
        if len(metas) != 1 or len(turns) != 1:
            return "INVALID"
        meta = metas[0].get("payload") or {}
        turn = turns[0].get("payload") or {}
        repo = (profile or {}).get("repo") or {}
        if (meta.get("id") != binding.get("thread_id") or
                meta.get("session_id") != binding.get("thread_id") or
                binding.get("stdout_turn_ordinal") != 1 or
                turn.get("turn_id") != binding.get("native_turn_id") or
                str(turn.get("cwd", "")).replace("\\", "/") !=
                str(repo.get("lexical_root", "")).replace("\\", "/") or
                str(meta.get("cwd", "")).replace("\\", "/") !=
                str(repo.get("lexical_root", "")).replace("\\", "/")):
            return "INVALID"
        meta_time = _parse_utc(metas[0].get("timestamp") or
                               meta.get("timestamp"))
        turn_time = _parse_utc(turns[0].get("timestamp"))
        process_time = _parse_utc((process_started or {}).get("started_at"))
        if (not meta_time or not turn_time or not process_time or
                meta_time < process_time or turn_time < meta_time):
            return "INVALID"
        return "VALID"
    elif not types.intersection({"system", "assistant", "user", "result"}):
        return "INVALID"
    scalars = set()
    for obj in objects:
        scalars.update(_scalar_strings(obj))
    if not binding or any(value not in scalars for value in binding.values()):
        return "INVALID"
    action_ids = [action.get("id") for action in trace.get("actions", [])
                  if isinstance(action.get("id"), str) and
                  action.get("state") in ("COMPLETED", "INVALID",
                                          "INCOMPLETE")]
    if action_ids and any(action_id not in scalars
                          for action_id in action_ids):
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
        if terminal.get("schema") != TERMINAL_SCHEMA:
            raise ValueError("terminal invalid")
        if not _validate_replay_spec(replay_spec, formal):
            raise ValueError("replay recipe invalid")
        if trace.get("schema") != TRACE_SCHEMA or \
                matrix.get("schema") != MATRIX_SCHEMA:
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
            profile = _admit_persisted_profile(profile)
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
                derived = derive_codex_binding(raw_stdout)
                lineage_valid = bool(derived) and all(
                    binding.get(key) == value for key, value in
                    (derived or {}).items()) and isinstance(
                        binding.get("native_turn_id"), str)
                normalized = normalize_codex(
                    raw_stdout, profile=profile, binding=binding,
                    formal=formal)
            else:
                derived = derive_claude_binding(raw_stdout)
                lineage_valid = derived is not None and binding == derived
                normalized = normalize_claude(
                    raw_stdout,
                    requested_tools=replay_spec["requested_tools"],
                    binding=binding, profile=profile, formal=formal)
            if derived is not None and not lineage_valid:
                raise ValueError("lineage binding mismatch")
            session_status = corroborate_session(
                raw_stdout, raw_session, replay_spec["host"], binding,
                normalized, profile=profile, process_started=process)
            if session_status in ("INVALID", "SUBSTITUTED"):
                raise ValueError("native session stream invalid")
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
    return {"status": "PASS", "matrix": matrix, "trace": trace,
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
