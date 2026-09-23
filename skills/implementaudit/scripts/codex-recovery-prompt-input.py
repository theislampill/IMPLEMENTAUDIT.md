#!/usr/bin/env python3
"""Read-only native UserPromptSubmit input adapter; no route or event credit."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import types

MAX_INPUT = 65536
MAX_OUTPUT = 32768
FROZEN_OWNER_DIGESTS = {'claim-run.sh': '07e09843b2831149dc43e5f0dc458e82ae5cf9614b116393ac774ddea19390c7', 'host-session-binding.py': '62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890', 'rotate-canonical-state.py': 'd0a1ce2889e98afa37637777a9cc624ff931700dab8b1468b34e5c201cf46460', 'validate-run-root.sh': 'fe005aea40d8eb2ea860c62f0caf1fb78ba678381ab6444e4f7b8202e82b77e5'}


class InputUnavailable(RuntimeError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def digest(value):
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise InputUnavailable("duplicate input field")
        value[key] = item
    return value


def text(value, label):
    if (not isinstance(value, str) or not 0 < len(value) <= 1024
            or any(ord(char) < 32 or ord(char) == 127 for char in value)):
        raise InputUnavailable("invalid " + label)
    return value


def exact_path(raw, *, directory):
    if not isinstance(raw, str) or not raw or len(raw) > 4096:
        raise InputUnavailable("missing installed path")
    path = Path(raw)
    if not path.is_absolute() or any(ord(char) < 32 for char in raw):
        raise InputUnavailable("invalid installed path")
    resolved = path.resolve(strict=True)
    if os.path.normcase(str(path)) != os.path.normcase(str(resolved)):
        raise InputUnavailable("installed path alias")
    info = path.stat()
    if (path.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400
            or (not stat.S_ISDIR(info.st_mode) if directory else not stat.S_ISREG(info.st_mode))):
        raise InputUnavailable("unsafe installed path")
    return path


def load_owner():
    if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
        raise InputUnavailable("isolated fixed hook invocation required")
    script = exact_path(str(Path(__file__).absolute()), directory=False)
    script_dir = script.parent
    root = exact_path(os.environ.get("PLUGIN_ROOT"), directory=True)
    if root != script.parents[3]:
        raise InputUnavailable("PLUGIN_ROOT differs from executing adapter")
    plugin, marketplace, cache, plugins = root.parent, root.parent.parent, root.parent.parent.parent, root.parent.parent.parent.parent
    if cache.name != "cache" or plugins.name != "plugins":
        raise InputUnavailable("installed cache identity is invalid")
    # Native plugin scratch data and the H0 owner store have distinct layouts.
    # Never use the flattened native name to select an H0 owner: hyphen joins
    # can collide across marketplace/plugin pairs. H0 stays keyed by both
    # physical cache components, matching the unchanged claim-run.sh owner.
    if not all(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name)
               for name in (marketplace.name, plugin.name)):
        raise InputUnavailable("installed owner component is invalid")
    owner_data = plugins / "data" / marketplace.name / plugin.name
    native_data = plugins / "data" / (plugin.name + "-" + marketplace.name)
    raw_data = os.environ.get("PLUGIN_DATA")
    if raw_data not in (str(owner_data), str(native_data)):
        raise InputUnavailable("PLUGIN_DATA differs from physical owner")
    # A fresh native scratch directory need not exist; validate its existing
    # parent and reject aliases/reparse points when the directory does exist.
    data = Path(raw_data)
    exact_path(str(data.parent), directory=True)
    if os.path.lexists(data):
        exact_path(str(data), directory=True)
    store = exact_path(str(owner_data / "host-session-binding-v1"), directory=True)
    source_bytes = {}
    for name, expected in FROZEN_OWNER_DIGESTS.items():
        path = exact_path(str(script_dir / name), directory=False)
        raw = path.read_bytes()
        if len(raw) > 2_000_000 or hashlib.sha256(raw).hexdigest() != expected:
            raise InputUnavailable("frozen owner source digest differs")
        source_bytes[name] = raw
    if set(source_bytes) != {"rotate-canonical-state.py", "claim-run.sh",
                             "host-session-binding.py", "validate-run-root.sh"}:
        raise InputUnavailable("frozen owner source population differs")
    module = types.ModuleType("_recovery_prompt_owner")
    module.__file__ = str(script_dir / "rotate-canonical-state.py")
    sys.modules[module.__name__] = module
    exec(compile(source_bytes["rotate-canonical-state.py"], module.__file__, "exec"), module.__dict__)
    return module, script_dir, store


def lookup_binding(owner, script_dir, store, session_id):
    completed = subprocess.run(
        [sys.executable, "-I", "-S", "-B", str(script_dir / "host-session-binding.py"),
         "--store", str(store), "lookup", "--host-id", "codex", "--host-session-id", session_id],
        cwd=str(script_dir), env=owner._publication_custody_environment_v1(),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
    if (completed.returncode != 0 or completed.stderr or len(completed.stdout) > MAX_INPUT
            or not completed.stdout.endswith(b"\n") or b"\n" in completed.stdout[:-1]):
        raise InputUnavailable("H0 lookup unavailable")
    value = json.loads(completed.stdout.decode("utf-8", "strict"), object_pairs_hook=unique_object)
    if not isinstance(value, dict) or value.get("schema") != "implementaudit.host-session-binding-result.v1":
        raise InputUnavailable("H0 lookup shape differs")
    if value.get("status") == "UNBOUND":
        return None
    binding = value.get("binding")
    if (value.get("status") != "BOUND" or not isinstance(binding, dict)
            or binding.get("host_id") != "codex" or binding.get("host_session_id") != session_id
            or binding.get("status") != "ACTIVE"):
        raise InputUnavailable("H0 session binding differs")
    return binding


def recovery_input(event):
    if not isinstance(event, dict) or event.get("hook_event_name") != "UserPromptSubmit":
        raise InputUnavailable("foreign hook event")
    session_id = text(event.get("session_id"), "session_id")
    turn_id = text(event.get("turn_id"), "turn_id")
    if not isinstance(event.get("prompt"), str):
        raise InputUnavailable("invalid prompt field")
    supplied_session = os.environ.get("CODEX_SESSION_ID")
    if supplied_session is not None and supplied_session != session_id:
        raise InputUnavailable("hook session differs from native environment")
    # This only passes the hook envelope's session to the unchanged locator.
    # It does not authenticate stdin, mint an event, or write an H0 binding.
    os.environ["CODEX_SESSION_ID"] = session_id
    owner, script_dir, store = load_owner()
    binding = lookup_binding(owner, script_dir, store, session_id)
    if binding is None:
        return None
    try:
        custody = owner._read_owner_custody_tuple_v1(
            "--recovery-custody", "implementaudit.recovery-custody-locator.v1", 12)
        repository = owner.require_repo(custody[4])
        invalidation_ref = "refs/implementaudit/continuity-invalidations/" + custody[1]
        if owner.read_optional_exact_ref_oid_v1(repository, invalidation_ref) is None:
            return None
        subject = owner.observe_recovery_subject_v1()
    except owner.RotationError as exc:
        if str(exc) == "recovery subject requires a new invalidation":
            return None
        raise InputUnavailable("recovery subject unavailable") from exc
    if (subject.get("schema") != "implementaudit.recovery-subject-observation.v1"
            or subject.get("host_binding_digest") != digest(binding)
            or subject.get("host_binding_generation") != binding.get("binding_generation")
            or subject.get("controller_id") != binding.get("controller_id")
            or subject.get("claim_id") != binding.get("claim_id")
            or subject.get("predecessor_receipt") != binding.get("applicable_continuity_receipt")
            or subject.get("genuine_host_evidence") != "UNVERIFIED"
            or subject.get("continuity_current") is not False
            or subject.get("ordinary_effect_authority") != "NONE"
            or subject.get("route_open_authority") != "NONE"):
        raise InputUnavailable("recovery subject binding differs")
    text(subject.get("subject_boundary_event_id"), "subject event identity")
    source_event = {
        "schema": "implementaudit.user-prompt-source-input.v1",
        "host_id": "codex", "kind": "UserPromptSubmit",
        "host_session_id": session_id, "turn_id": turn_id,
        "host_binding_generation": subject["host_binding_generation"],
        "host_binding_digest": subject["host_binding_digest"],
    }
    result = {
        "schema": "implementaudit.recovery-host-input.v1",
        "source_event": source_event, "source_event_digest": digest(source_event),
        "subject": subject, "subject_digest": digest(subject),
        "subject_cause_attested": False, "genuine_host_evidence": "UNVERIFIED",
        "continuity_current": False, "ordinary_effect_authority": "NONE",
        "route_open_authority": "NONE",
    }
    result["input_digest"] = digest(result)
    # Re-read H0 and source files after observation before producing its input.
    if lookup_binding(owner, script_dir, store, session_id) != binding:
        raise InputUnavailable("H0 binding changed during input assembly")
    for name, expected in FROZEN_OWNER_DIGESTS.items():
        if hashlib.sha256(exact_path(str(script_dir / name), directory=False).read_bytes()).hexdigest() != expected:
            raise InputUnavailable("owner source changed during input assembly")
    return result


def main():
    try:
        raw = sys.stdin.buffer.read(MAX_INPUT + 1)
        if len(raw) > MAX_INPUT:
            raise InputUnavailable("hook input oversized")
        event = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=unique_object)
        value = recovery_input(event)
        output = {"continue": True, "suppressOutput": True} if value is None else {
            "continue": True,
            "hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                   "additionalContext": canonical(value).decode("utf-8")},
        }
        encoded = canonical(output)
        if len(encoded) > MAX_OUTPUT:
            raise InputUnavailable("recovery input output oversized")
    except (InputUnavailable, OSError, ValueError, TypeError, KeyError, RecursionError, subprocess.SubprocessError):
        encoded = canonical({"continue": False,
            "stopReason": "IMPLEMENTAUDIT recovery input is unavailable; no recovery or execution authority was granted."})
    sys.stdout.buffer.write(encoded + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
