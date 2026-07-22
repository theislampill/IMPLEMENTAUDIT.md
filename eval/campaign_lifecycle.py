#!/usr/bin/env python3
"""Data-neutral custody and lifecycle primitives for frozen campaigns.

This module deliberately knows nothing about fixtures, scoring, or campaign
acceptance.  Campaign-specific code supplies expected identities and terminal
states; the helpers enforce only retained-evidence mechanics.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import stat


STAGE_TERMINAL_SCHEMA = "implementaudit-staged-campaign-terminal-v1"


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(value):
    raise ValueError(f"non-finite JSON number: {value}")


def decode_strict_json_bytes(data, owner, *, require_object=False):
    try:
        text = bytes(data).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{owner} must be UTF-8") from exc
    try:
        value = json.loads(
            text, object_pairs_hook=_unique, parse_constant=_nonfinite)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{owner} is malformed JSON") from exc
    if require_object and type(value) is not dict:
        raise ValueError(f"{owner} must be an object")
    return value


def canonical_json_bytes(value):
    return (json.dumps(value, indent=1, sort_keys=True, allow_nan=False) +
            "\n").encode("utf-8")


def _reparse_point(path_stat):
    return bool(getattr(path_stat, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _walk_no_link(path, owner):
    current = pathlib.Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        path_stat = os.lstat(current)
        if stat.S_ISLNK(path_stat.st_mode) or _reparse_point(path_stat):
            raise ValueError(f"{owner} link or reparse alias forbidden")


def _canonical_lexical(path, owner, *, directory=False):
    lexical = pathlib.Path(path).absolute()
    try:
        resolved = lexical.resolve(strict=True)
        if resolved != lexical:
            raise ValueError(f"{owner} link or reparse alias forbidden")
        _walk_no_link(lexical, owner)
        path_stat = os.lstat(lexical)
        expected = stat.S_ISDIR if directory else stat.S_ISREG
        if not expected(path_stat.st_mode):
            kind = "directory" if directory else "regular file"
            raise ValueError(f"{owner} must be a {kind}")
        return lexical
    except ValueError:
        raise
    except OSError as exc:
        raise ValueError(f"{owner} cannot be resolved") from exc


def _owner_root(root, owner="owner root"):
    return _canonical_lexical(root, owner, directory=True)


def read_custodied_bytes(path, owner, *, root=None):
    """Read one regular file through one canonical, single-link identity."""
    lexical = pathlib.Path(path).absolute()
    stop = None
    if root is not None:
        stop = _owner_root(root)
        try:
            lexical.relative_to(stop)
        except ValueError as exc:
            raise ValueError(f"{owner} path escapes owner root") from exc
    try:
        resolved = lexical.resolve(strict=True)
        if resolved != lexical:
            raise ValueError(f"{owner} link or reparse alias forbidden")
        if stop is not None:
            try:
                resolved.relative_to(stop)
            except ValueError as exc:
                raise ValueError(f"{owner} path escapes owner root") from exc
        _walk_no_link(lexical, owner)
        with open(lexical, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode):
                raise ValueError(f"{owner} must be a retained regular file")
            if opened.st_nlink != 1:
                raise ValueError(f"{owner} hardlink identity forbidden")
            return stream.read()
    except ValueError:
        raise
    except OSError as exc:
        raise ValueError(f"{owner} cannot be read as retained evidence") from exc


def read_strict_json_bytes(path, owner, *, root):
    return decode_strict_json_bytes(
        read_custodied_bytes(path, owner, root=root), owner,
        require_object=True)


def write_new_bytes(path, payload):
    """Create one file without following an aliased parent or replacing bytes."""
    if type(payload) is not bytes:
        raise TypeError("create-once payload must be bytes")
    path = pathlib.Path(path).absolute()
    parent = _canonical_lexical(path.parent, "create-once parent", directory=True)
    if path.parent != parent:
        raise ValueError("create-once parent link or reparse alias forbidden")
    try:
        with open(path, "xb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                raise ValueError("create-once target identity invalid")
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise ValueError(
            f"create-once artifact already exists: {path.name}") from exc
    return path


def write_new_json(path, value):
    return write_new_bytes(path, canonical_json_bytes(value))


def _direct_name(value, owner):
    if (type(value) is not str or not value or value in (".", "..") or
            "/" in value or "\\" in value or "\x00" in value):
        raise ValueError(f"{owner} name invalid")
    return value


def _identity(value, expected, owner):
    if type(value) is not dict or type(expected) is not dict:
        raise ValueError(f"{owner} identity must be an object")
    for key, expected_value in expected.items():
        if key not in value or value[key] != expected_value:
            if key == "campaign":
                raise ValueError(f"{owner} campaign identity drift")
            raise ValueError(f"{owner} identity drift")


def _mission_descriptor(value, index):
    if type(value) is not dict:
        raise ValueError(f"mission descriptor {index} must be an object")
    required = {
        "attempt", "status_identity", "terminal_identity",
        "terminal_state_field", "terminal_stop_reason_field",
        "allowed_attempt",
    }
    if set(value) != required:
        raise ValueError(f"mission descriptor {index} key set invalid")
    _direct_name(value["attempt"], f"mission descriptor {index} attempt")
    if not value["attempt"].startswith("attempt-"):
        raise ValueError(f"mission descriptor {index} attempt name invalid")
    if type(value["status_identity"]) is not dict or not value["status_identity"]:
        raise ValueError(f"mission descriptor {index} status identity invalid")
    if type(value["terminal_identity"]) is not dict or not value["terminal_identity"]:
        raise ValueError(f"mission descriptor {index} terminal identity invalid")
    _direct_name(value["terminal_state_field"],
                 f"mission descriptor {index} terminal state field")
    _direct_name(value["terminal_stop_reason_field"],
                 f"mission descriptor {index} stop reason field")
    if type(value["allowed_attempt"]) not in (set, frozenset, list, tuple):
        raise ValueError(f"mission descriptor {index} allowed entries invalid")
    allowed_attempt = {
        _direct_name(name, f"mission descriptor {index} allowed entry")
        for name in value["allowed_attempt"]
    }
    if not {"attempt-status.json", "attempt-terminal.json"} <= allowed_attempt:
        raise ValueError(f"mission descriptor {index} lifecycle entries missing")
    return value


def validate_terminal_prefix(root, missions, *, stop_states, allowed_root):
    """Validate an exact, gap-free prefix of create-once terminal attempts."""
    root = _owner_root(root, "campaign root")
    if type(missions) not in (list, tuple):
        raise ValueError("mission descriptors must be an ordered sequence")
    descriptors = [_mission_descriptor(row, index)
                   for index, row in enumerate(missions)]
    names = [row["attempt"] for row in descriptors]
    if len(names) != len(set(names)):
        raise ValueError("duplicate attempt identity in mission descriptors")
    if type(stop_states) not in (set, frozenset, list, tuple):
        raise ValueError("stop states must be a collection")
    stop_states = set(stop_states)
    if any(type(value) is not str or not value for value in stop_states):
        raise ValueError("stop states contain an invalid value")
    root_identities = {}
    if type(allowed_root) is dict:
        for name, identity in allowed_root.items():
            name = _direct_name(name, "allowed root entry")
            if identity is not None and type(identity) is not dict:
                raise ValueError("allowed root identity must be an object or null")
            root_identities[name] = identity
        allowed = set(root_identities)
    elif type(allowed_root) in (set, frozenset, list, tuple):
        allowed = {_direct_name(value, "allowed root entry")
                   for value in allowed_root}
    else:
        raise ValueError("allowed root entries must be a collection")
    claiming = {name + ".claiming" for name in names}
    entries = list(root.iterdir())
    entry_names = [entry.name for entry in entries]
    if len(entry_names) != len(set(entry_names)):
        raise ValueError("duplicate campaign custody entry")
    unexpected = set(entry_names) - allowed - set(names) - claiming
    if unexpected:
        raise ValueError("unexpected campaign custody entry: " +
                         ", ".join(sorted(unexpected)))
    for name, expected_identity in root_identities.items():
        if expected_identity is None:
            continue
        if name not in entry_names:
            raise ValueError(f"required campaign root artifact missing: {name}")
        value = read_strict_json_bytes(
            root / name, f"campaign root artifact {name}", root=root)
        _identity(value, expected_identity, f"campaign root artifact {name}")
    present_claims = set(entry_names) & claiming
    if present_claims:
        raise ValueError("campaign contains a nonterminal claiming directory")

    actual = set(entry_names) & set(names)
    count = 0
    while count < len(names) and names[count] in actual:
        count += 1
    if actual != set(names[:count]):
        raise ValueError("campaign terminal prefix has a gap")

    rows = []
    stopped_at = None
    for index, descriptor in enumerate(descriptors[:count]):
        attempt = _canonical_lexical(
            root / descriptor["attempt"], "attempt custody", directory=True)
        attempt_entries = {entry.name for entry in attempt.iterdir()}
        required = {"attempt-status.json", "attempt-terminal.json"}
        allowed_attempt = set(descriptor["allowed_attempt"])
        if not attempt_entries <= allowed_attempt:
            raise ValueError("unexpected attempt custody entry")
        if not required <= attempt_entries:
            raise ValueError("campaign terminal prefix is nonterminal")
        status = read_strict_json_bytes(
            attempt / "attempt-status.json", "attempt status", root=root)
        terminal = read_strict_json_bytes(
            attempt / "attempt-terminal.json", "attempt terminal", root=root)
        _identity(status, descriptor["status_identity"], "attempt status")
        _identity(terminal, descriptor["terminal_identity"], "attempt terminal")
        state_field = descriptor["terminal_state_field"]
        reason_field = descriptor["terminal_stop_reason_field"]
        state = terminal.get(state_field)
        if type(state) is not str or not state:
            raise ValueError("attempt terminal state invalid")
        reason = terminal.get(reason_field)
        if reason is not None and (type(reason) is not str or not reason):
            raise ValueError("attempt terminal stop reason invalid")
        if stopped_at is not None:
            raise ValueError("campaign contains attempt after terminal stop")
        if state in stop_states or reason is not None:
            stopped_at = index
        rows.append({"attempt": descriptor["attempt"], "status": status,
                     "terminal": terminal})
    return rows


def _stage_descriptor(value):
    required = {
        "name", "campaign", "schema", "terminal_name", "missions",
        "stop_states", "allowed_root",
    }
    if type(value) is not dict or set(value) != required:
        raise ValueError("stage descriptor key set invalid")
    for key in ("name", "campaign", "schema"):
        if type(value[key]) is not str or not value[key]:
            raise ValueError(f"stage descriptor {key} invalid")
    _direct_name(value["terminal_name"], "stage terminal")
    return value


def _validate_stage_binding(stage, binding):
    if type(binding) is not dict:
        raise ValueError("stage binding must be an object")
    required = {"campaign", "stage", "stage_schema", "mission_count"}
    if not required <= set(binding):
        raise ValueError("stage binding key set invalid")
    if binding["campaign"] != stage["campaign"]:
        raise ValueError("stage binding campaign mismatch")
    if binding["stage"] != stage["name"]:
        raise ValueError("stage binding name mismatch")
    if binding["stage_schema"] != stage["schema"]:
        raise ValueError("stage binding schema mismatch")
    if (type(binding["mission_count"]) is not int or
            binding["mission_count"] != len(stage["missions"])):
        raise ValueError("stage binding prefix length mismatch")


def _stage_prefix(root, stage, *, include_terminal):
    allowed = (dict(stage["allowed_root"])
               if type(stage["allowed_root"]) is dict
               else set(stage["allowed_root"]))
    if include_terminal:
        if type(allowed) is dict:
            allowed[stage["terminal_name"]] = None
        else:
            allowed.add(stage["terminal_name"])
    rows = validate_terminal_prefix(
        root, stage["missions"], stop_states=stage["stop_states"],
        allowed_root=allowed)
    if len(rows) != len(stage["missions"]):
        raise ValueError("stage terminal requires the exact declared prefix")
    stop_states = set(stage["stop_states"])
    for descriptor, row in zip(stage["missions"], rows):
        terminal = row["terminal"]
        if (terminal[descriptor["terminal_state_field"]] in stop_states or
                terminal[descriptor["terminal_stop_reason_field"]] is not None):
            raise ValueError("stopped prefix cannot create a stage terminal")
    return rows


def write_stage_terminal(root, stage, binding):
    stage = _stage_descriptor(stage)
    _validate_stage_binding(stage, binding)
    terminal_path = pathlib.Path(root) / stage["terminal_name"]
    if terminal_path.exists():
        raise ValueError(
            f"create-once artifact already exists: {stage['terminal_name']}")
    _stage_prefix(root, stage, include_terminal=False)
    binding_sha256 = hashlib.sha256(canonical_json_bytes(binding)).hexdigest()
    terminal = {
        "schema": STAGE_TERMINAL_SCHEMA,
        "campaign": stage["campaign"],
        "stage": stage["name"],
        "stage_schema": stage["schema"],
        "mission_count": len(stage["missions"]),
        "binding_sha256": binding_sha256,
    }
    return write_new_json(terminal_path, terminal)


def validate_stage_resume(root, stage, binding):
    stage = _stage_descriptor(stage)
    _validate_stage_binding(stage, binding)
    _stage_prefix(root, stage, include_terminal=True)
    terminal_path = pathlib.Path(root) / stage["terminal_name"]
    if not terminal_path.exists():
        raise ValueError("stage terminal is missing")
    terminal = read_strict_json_bytes(
        terminal_path, "stage terminal", root=root)
    expected = {
        "schema": STAGE_TERMINAL_SCHEMA,
        "campaign": stage["campaign"],
        "stage": stage["name"],
        "stage_schema": stage["schema"],
        "mission_count": len(stage["missions"]),
        "binding_sha256": hashlib.sha256(
            canonical_json_bytes(binding)).hexdigest(),
    }
    if terminal.get("campaign") != expected["campaign"]:
        raise ValueError("stage terminal campaign mismatch")
    identity_fields = {
        "schema", "stage", "stage_schema", "mission_count",
    }
    if any(terminal.get(key) != expected[key] for key in identity_fields):
        raise ValueError("stage terminal identity mismatch")
    if terminal.get("binding_sha256") != expected["binding_sha256"]:
        raise ValueError("stage terminal binding hash mismatch")
    if terminal != expected:
        raise ValueError("stage terminal key set invalid")
    return terminal
