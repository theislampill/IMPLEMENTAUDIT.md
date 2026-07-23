#!/usr/bin/env python3
"""Data-neutral custody and lifecycle primitives for frozen campaigns.

This module deliberately knows nothing about fixtures, scoring, or campaign
acceptance.  Campaign-specific code supplies expected identities and terminal
states; the helpers enforce only retained-evidence mechanics.
"""
from __future__ import annotations

import decimal
import hashlib
import json
import math
import os
import pathlib
import stat


STAGE_TERMINAL_SCHEMA = "implementaudit-staged-campaign-terminal-v1"
MAX_JSON_DEPTH = 512


class TerminalPrefix(list):
    """Validated attempt rows plus the exact root bytes read in the same pass."""

    def __init__(self, rows, root_artifacts):
        super().__init__(rows)
        self.root_artifacts = root_artifacts


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(value):
    raise ValueError(f"non-finite JSON number: {value}")


def _lossless_float(token):
    try:
        source = decimal.Decimal(token)
        value = float(source)
        round_trip = (decimal.Decimal(repr(value))
                      if math.isfinite(value) else None)
        numerically_equal = (round_trip == source
                             if round_trip is not None else False)
    except decimal.DecimalException as exc:
        raise ValueError(f"JSON number domain error: {token}") from exc
    if not math.isfinite(value):
        raise ValueError(f"non-finite JSON number: {token}")
    sign_changed = (source.is_zero() and
                    source.is_signed() != (math.copysign(1.0, value) < 0.0))
    if not numerically_equal or sign_changed:
        raise ValueError(f"lossy JSON number: {token}")
    return value


def decode_strict_json_bytes(data, owner, *, require_object=False):
    try:
        text = bytes(data).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{owner} must be UTF-8") from exc
    try:
        value = json.loads(
            text, object_pairs_hook=_unique, parse_constant=_nonfinite,
            parse_float=_lossless_float)
        _validate_strict_json_model(value, owner)
    except RecursionError as exc:
        raise ValueError(f"{owner} exceeds JSON depth limit") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{owner} is malformed JSON") from exc
    if require_object and type(value) is not dict:
        raise ValueError(f"{owner} must be an object")
    return value


def _validate_strict_json_model(value, owner="JSON value"):
    active = set()
    stack = [("visit", value, owner, 0)]
    while stack:
        action, current, current_owner, depth = stack.pop()
        if action == "leave":
            active.remove(id(current))
            continue
        if type(current) is dict:
            if depth >= MAX_JSON_DEPTH:
                raise ValueError(f"{current_owner} exceeds JSON depth limit")
            identity = id(current)
            if identity in active:
                raise ValueError(
                    f"{current_owner} contains a cyclic JSON container")
            active.add(identity)
            stack.append(("leave", current, current_owner, depth))
            children = []
            for key, child in current.items():
                if type(key) is not str:
                    raise ValueError(
                        f"{current_owner} object key must be an exact string")
                children.append((
                    "visit", child, f"{current_owner}.{key}", depth + 1))
            stack.extend(reversed(children))
            continue
        if isinstance(current, dict):
            raise ValueError(f"{current_owner} object type must be exact dict")
        if type(current) is list:
            if depth >= MAX_JSON_DEPTH:
                raise ValueError(f"{current_owner} exceeds JSON depth limit")
            identity = id(current)
            if identity in active:
                raise ValueError(
                    f"{current_owner} contains a cyclic JSON container")
            active.add(identity)
            stack.append(("leave", current, current_owner, depth))
            stack.extend(
                ("visit", child, f"{current_owner}[{index}]", depth + 1)
                for index, child in reversed(list(enumerate(current))))
            continue
        if isinstance(current, (list, tuple)):
            raise ValueError(f"{current_owner} array type must be exact list")
        if current is None or type(current) in (str, bool, int):
            continue
        if type(current) is float:
            if not math.isfinite(current):
                raise ValueError(
                    f"{current_owner} contains a non-finite number")
            continue
        raise ValueError(f"{current_owner} scalar type is not strict JSON")


def canonical_json_bytes(value):
    try:
        _validate_strict_json_model(value)
        text = json.dumps(value, indent=1, sort_keys=True, allow_nan=False)
    except RecursionError as exc:
        raise ValueError("JSON value exceeds JSON depth limit") from exc
    return (text + "\n").encode("utf-8")


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


def _read_directory_leaf(path, owner, *, expected_stat):
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = None
    try:
        descriptor = os.open(path, flags)
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError(f"{owner} must be a retained regular file")
        if opened.st_nlink != 1:
            raise ValueError(f"{owner} hardlink identity forbidden")
        if ((opened.st_dev, opened.st_ino) !=
                (expected_stat.st_dev, expected_stat.st_ino)):
            raise ValueError(f"{owner} identity changed during custody read")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = None
            return stream.read()
    except ValueError:
        raise
    except OSError as exc:
        raise ValueError(f"{owner} cannot be read as retained evidence") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def read_custodied_directory_manifest(path, owner, *, root):
    """Return canonical bytes binding one recursive no-link directory tree."""
    stop = _owner_root(root)
    directory = pathlib.Path(path).absolute()
    try:
        directory.relative_to(stop)
    except ValueError as exc:
        raise ValueError(f"{owner} path escapes owner root") from exc
    entries = []
    seen_directories = set()
    pending = [(directory, pathlib.PurePosixPath("."))]
    try:
        while pending:
            current, relative = pending.pop()
            _walk_no_link(current, owner)
            current_stat = os.lstat(current)
            if (stat.S_ISLNK(current_stat.st_mode) or
                    _reparse_point(current_stat)):
                raise ValueError(f"{owner} link or reparse alias forbidden")
            if not stat.S_ISDIR(current_stat.st_mode):
                raise ValueError(f"{owner} must be a retained directory")
            identity = (current_stat.st_dev, current_stat.st_ino)
            if identity in seen_directories:
                raise ValueError(f"{owner} repeated directory identity forbidden")
            seen_directories.add(identity)
            entries.append({
                "path": relative.as_posix(), "kind": "directory"})
            with os.scandir(current) as scanned:
                children = list(scanned)
            for child in reversed(sorted(children, key=lambda row: row.name)):
                name = _direct_name(child.name, f"{owner} entry")
                child_path = current / name
                child_relative = (pathlib.PurePosixPath(name)
                                  if relative == pathlib.PurePosixPath(".")
                                  else relative / name)
                child_stat = os.lstat(child_path)
                if (stat.S_ISLNK(child_stat.st_mode) or
                        _reparse_point(child_stat)):
                    raise ValueError(
                        f"{owner} link or reparse alias forbidden")
                if stat.S_ISDIR(child_stat.st_mode):
                    pending.append((child_path, child_relative))
                    continue
                if not stat.S_ISREG(child_stat.st_mode):
                    raise ValueError(f"{owner} special file kind forbidden")
                if child_stat.st_nlink != 1:
                    raise ValueError(f"{owner} hardlink identity forbidden")
                _walk_no_link(child_path, owner)
                payload = _read_directory_leaf(
                    child_path, owner, expected_stat=child_stat)
                entries.append({
                    "path": child_relative.as_posix(), "kind": "file",
                    "byte_length": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                })
    except ValueError:
        raise
    except OSError as exc:
        raise ValueError(f"{owner} cannot be read as retained evidence") from exc
    entries.sort(key=lambda row: row["path"])
    return canonical_json_bytes({
        "schema": "implementaudit-custodied-directory-manifest-v1",
        "entries": entries,
    })


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


def _exact_json_equal(left, right):
    active_left = set()
    active_right = set()
    stack = [("compare", left, right, 0)]
    while stack:
        action, current_left, current_right, depth = stack.pop()
        if action == "leave":
            active_left.remove(id(current_left))
            active_right.remove(id(current_right))
            continue
        if type(current_left) is not type(current_right):
            return False
        if type(current_left) is dict:
            if depth >= MAX_JSON_DEPTH:
                return False
            if set(current_left) != set(current_right):
                return False
            left_identity = id(current_left)
            right_identity = id(current_right)
            if (left_identity in active_left or
                    right_identity in active_right):
                return False
            active_left.add(left_identity)
            active_right.add(right_identity)
            stack.append(("leave", current_left, current_right, depth))
            stack.extend(
                ("compare", current_left[key], current_right[key], depth + 1)
                for key in reversed(list(current_left)))
            continue
        if type(current_left) is list:
            if depth >= MAX_JSON_DEPTH:
                return False
            if len(current_left) != len(current_right):
                return False
            left_identity = id(current_left)
            right_identity = id(current_right)
            if (left_identity in active_left or
                    right_identity in active_right):
                return False
            active_left.add(left_identity)
            active_right.add(right_identity)
            stack.append(("leave", current_left, current_right, depth))
            stack.extend(
                ("compare", left_child, right_child, depth + 1)
                for left_child, right_child in reversed(
                    list(zip(current_left, current_right))))
            continue
        if type(current_left) is float:
            if (current_left != current_right or
                    (current_left == 0.0 and
                     math.copysign(1.0, current_left) !=
                     math.copysign(1.0, current_right))):
                return False
            continue
        if (type(current_left) in (str, bool, int) or
                current_left is None):
            if current_left != current_right:
                return False
            continue
        return False
    return True


def _identity(value, expected, owner):
    if type(value) is not dict or type(expected) is not dict:
        raise ValueError(f"{owner} identity must be an object")
    for key, expected_value in expected.items():
        if key not in value or not _exact_json_equal(
                value[key], expected_value):
            if key == "campaign":
                raise ValueError(f"{owner} campaign identity drift")
            raise ValueError(f"{owner} identity drift")


def _artifact_policy(value, owner, *, allowed_kinds):
    if type(value) is not dict or "kind" not in value:
        raise ValueError(f"{owner} policy invalid")
    kind = value["kind"]
    if kind == "json_identity":
        if (set(value) != {"kind", "identity"} or
                type(value["identity"]) is not dict or
                not value["identity"]):
            raise ValueError(f"{owner} JSON identity policy invalid")
    elif kind == "custodied_file":
        if set(value) != {"kind"}:
            raise ValueError(f"{owner} custody policy invalid")
    elif kind == "custodied_directory":
        if set(value) != {"kind"}:
            raise ValueError(f"{owner} directory custody policy invalid")
    elif kind == "exact_bytes":
        if set(value) != {"kind", "byte_length", "sha256"}:
            raise ValueError(f"{owner} exact-bytes policy invalid")
        digest = value["sha256"]
        if (type(value["byte_length"]) is not int or
                value["byte_length"] < 0 or type(digest) is not str or
                len(digest) != 64 or
                any(character not in "0123456789abcdef" for character in digest)):
            raise ValueError(f"{owner} exact-bytes policy invalid")
    else:
        raise ValueError(f"{owner} policy kind invalid")
    if kind not in allowed_kinds:
        raise ValueError(f"{owner} policy kind forbidden in this scope")
    return value


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
    if type(value["allowed_attempt"]) is not dict:
        raise ValueError(
            f"mission descriptor {index} allowed policy must be explicit")
    allowed_attempt = {}
    for name, policy in value["allowed_attempt"].items():
        name = _direct_name(name, f"mission descriptor {index} allowed entry")
        allowed_attempt[name] = _artifact_policy(
            policy, f"mission descriptor {index} artifact {name}",
            allowed_kinds={
                "json_identity", "custodied_file", "custodied_directory",
                "exact_bytes",
            })
    if not {"attempt-status.json", "attempt-terminal.json"} <= set(allowed_attempt):
        raise ValueError(f"mission descriptor {index} lifecycle entries missing")
    required_policies = {
        "attempt-status.json": value["status_identity"],
        "attempt-terminal.json": value["terminal_identity"],
    }
    for name, identity in required_policies.items():
        policy = allowed_attempt[name]
        if (policy["kind"] != "json_identity" or
                not _exact_json_equal(policy["identity"], identity)):
            raise ValueError(
                f"mission descriptor {index} {name} identity policy drift")
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
    status_identities = [canonical_json_bytes(row["status_identity"])
                         for row in descriptors]
    terminal_identities = [canonical_json_bytes(row["terminal_identity"])
                           for row in descriptors]
    if (len(status_identities) != len(set(status_identities)) or
            len(terminal_identities) != len(set(terminal_identities))):
        raise ValueError("duplicate semantic mission identity")
    if type(stop_states) not in (set, frozenset, list, tuple):
        raise ValueError("stop states must be a collection")
    if any(type(value) is not str or not value for value in stop_states):
        raise ValueError("stop states contain an invalid value")
    stop_states = set(stop_states)
    if type(allowed_root) is not dict:
        raise ValueError(
            "allowed root policy must explicitly cover every artifact")
    root_policies = {}
    for name, policy in allowed_root.items():
        name = _direct_name(name, "allowed root entry")
        root_policies[name] = _artifact_policy(
            policy, "allowed root",
            allowed_kinds={"json_identity", "exact_bytes"})
    allowed = set(root_policies)
    claiming = {name + ".claiming" for name in names}
    entries = list(root.iterdir())
    entry_names = [entry.name for entry in entries]
    if len(entry_names) != len(set(entry_names)):
        raise ValueError("duplicate campaign custody entry")
    unexpected = set(entry_names) - allowed - set(names) - claiming
    if unexpected:
        raise ValueError("unexpected campaign custody entry: " +
                         ", ".join(sorted(unexpected)))
    root_artifacts = {}
    for name in sorted(root_policies):
        policy = root_policies[name]
        if name not in entry_names:
            raise ValueError(f"required campaign root artifact missing: {name}")
        owner = f"campaign root artifact {name}"
        if policy["kind"] == "json_identity":
            raw = read_custodied_bytes(root / name, owner, root=root)
            value = decode_strict_json_bytes(
                raw, owner, require_object=True)
            _identity(value, policy["identity"], owner)
        else:
            raw = read_custodied_bytes(root / name, owner, root=root)
            if policy["kind"] == "exact_bytes" and (
                    len(raw) != policy["byte_length"] or
                    hashlib.sha256(raw).hexdigest() != policy["sha256"]):
                raise ValueError(f"{owner} exact bytes or hash drift")
        root_artifacts[name] = raw
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
        allowed_attempt = descriptor["allowed_attempt"]
        if not attempt_entries <= set(allowed_attempt):
            raise ValueError("unexpected attempt custody entry")
        if not required <= attempt_entries:
            raise ValueError("campaign terminal prefix is nonterminal")
        decoded = {}
        retained_bytes = {}
        for name in sorted(attempt_entries):
            policy = allowed_attempt[name]
            owner = f"attempt artifact {name}"
            if policy["kind"] == "custodied_directory":
                raw = read_custodied_directory_manifest(
                    attempt / name, owner, root=root)
            elif policy["kind"] == "json_identity":
                raw = read_custodied_bytes(attempt / name, owner, root=root)
                value = decode_strict_json_bytes(
                    raw, owner, require_object=True)
                _identity(value, policy["identity"], owner)
                decoded[name] = value
            else:
                raw = read_custodied_bytes(attempt / name, owner, root=root)
                if policy["kind"] == "exact_bytes" and (
                        len(raw) != policy["byte_length"] or
                        hashlib.sha256(raw).hexdigest() != policy["sha256"]):
                    raise ValueError(f"{owner} exact bytes or hash drift")
            retained_bytes[name] = raw
        status = decoded["attempt-status.json"]
        terminal = decoded["attempt-terminal.json"]
        _identity(status, descriptor["status_identity"], "attempt status")
        _identity(terminal, descriptor["terminal_identity"], "attempt terminal")
        state_field = descriptor["terminal_state_field"]
        reason_field = descriptor["terminal_stop_reason_field"]
        if state_field not in terminal or reason_field not in terminal:
            raise ValueError("attempt terminal control field missing")
        state = terminal[state_field]
        if type(state) is not str or not state:
            raise ValueError("attempt terminal state invalid")
        reason = terminal[reason_field]
        if reason is not None and (type(reason) is not str or not reason):
            raise ValueError("attempt terminal stop reason invalid")
        if stopped_at is not None:
            raise ValueError("campaign contains attempt after terminal stop")
        if state in stop_states or reason is not None:
            stopped_at = index
        rows.append({"attempt": descriptor["attempt"], "status": status,
                     "terminal": terminal,
                     "status_bytes": retained_bytes["attempt-status.json"],
                     "terminal_bytes": retained_bytes["attempt-terminal.json"],
                     "artifact_bytes": retained_bytes})
    return TerminalPrefix(rows, root_artifacts)


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
    if type(value["missions"]) is not list:
        raise ValueError("stage descriptor missions must be an exact list")
    if type(value["stop_states"]) is not list:
        raise ValueError("stage descriptor stop_states must be an exact list")
    if type(value["allowed_root"]) is not dict:
        raise ValueError("stage descriptor allowed_root must be an exact object")
    _validate_strict_json_model(value, "stage descriptor")
    for index, mission in enumerate(value["missions"]):
        if type(mission) is not dict:
            raise ValueError(f"stage mission {index} must be an object")
        for identity_name in ("status_identity", "terminal_identity"):
            identity = mission.get(identity_name)
            if (type(identity) is not dict or
                    identity.get("campaign") != value["campaign"]):
                raise ValueError(
                    f"stage mission campaign identity mismatch at {index}")
    matching_campaign_roots = 0
    for name, policy in value["allowed_root"].items():
        if type(policy) is not dict or policy.get("kind") != "json_identity":
            continue
        identity = policy.get("identity")
        if type(identity) is not dict or "campaign" not in identity:
            continue
        if identity["campaign"] != value["campaign"]:
            raise ValueError(
                f"stage root campaign identity mismatch for {name}")
        matching_campaign_roots += 1
    if matching_campaign_roots == 0:
        raise ValueError("stage root campaign identity missing")
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


def _stage_snapshot_sha256(stage, rows):
    root_artifacts = []
    for name in sorted(stage["allowed_root"]):
        raw = rows.root_artifacts[name]
        root_artifacts.append({
            "name": name,
            "byte_length": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })
    entries = []
    for descriptor, row in zip(stage["missions"], rows):
        artifacts = []
        for name in sorted(row["artifact_bytes"]):
            raw = row["artifact_bytes"][name]
            artifacts.append({
                "name": name,
                "byte_length": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            })
        entries.append({
            "mission_descriptor": descriptor,
            "attempt": row["attempt"],
            "artifacts": artifacts,
        })
    snapshot = {
        "schema": "implementaudit-closed-stage-snapshot-v1",
        "stage_descriptor": stage,
        "root_artifacts": root_artifacts,
        "attempts": entries,
    }
    return hashlib.sha256(canonical_json_bytes(snapshot)).hexdigest()


def _validate_caller_snapshot(binding, stage_snapshot_sha256):
    for key in ("prefix_sha256", "stage_snapshot_sha256"):
        if key in binding and binding[key] != stage_snapshot_sha256:
            raise ValueError(
                "caller stage snapshot hash disagrees with internal derivation")


def _stage_terminal_value(stage, binding, stage_snapshot_sha256):
    return {
        "schema": STAGE_TERMINAL_SCHEMA,
        "campaign": stage["campaign"],
        "stage": stage["name"],
        "stage_schema": stage["schema"],
        "mission_count": len(stage["missions"]),
        "binding_sha256": hashlib.sha256(
            canonical_json_bytes(binding)).hexdigest(),
        "stage_snapshot_sha256": stage_snapshot_sha256,
    }


def _stage_prefix(root, stage, *, stage_terminal_bytes=None):
    allowed = dict(stage["allowed_root"])
    if stage_terminal_bytes is not None:
        allowed[stage["terminal_name"]] = {
            "kind": "exact_bytes", "byte_length": len(stage_terminal_bytes),
            "sha256": hashlib.sha256(stage_terminal_bytes).hexdigest(),
        }
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
    rows = _stage_prefix(root, stage)
    stage_snapshot_sha256 = _stage_snapshot_sha256(stage, rows)
    _validate_caller_snapshot(binding, stage_snapshot_sha256)
    terminal = _stage_terminal_value(stage, binding, stage_snapshot_sha256)
    return write_new_json(terminal_path, terminal)


def validate_stage_resume(root, stage, binding):
    stage = _stage_descriptor(stage)
    _validate_stage_binding(stage, binding)
    terminal_path = pathlib.Path(root) / stage["terminal_name"]
    if not terminal_path.exists():
        raise ValueError("stage terminal is missing")
    terminal_bytes = read_custodied_bytes(
        terminal_path, "stage terminal", root=root)
    terminal = decode_strict_json_bytes(
        terminal_bytes, "stage terminal", require_object=True)
    rows = _stage_prefix(
        root, stage, stage_terminal_bytes=terminal_bytes)
    stage_snapshot_sha256 = _stage_snapshot_sha256(stage, rows)
    _validate_caller_snapshot(binding, stage_snapshot_sha256)
    expected = _stage_terminal_value(stage, binding, stage_snapshot_sha256)
    if not _exact_json_equal(
            terminal.get("campaign"), expected["campaign"]):
        raise ValueError("stage terminal campaign mismatch")
    identity_fields = {
        "schema", "stage", "stage_schema", "mission_count",
    }
    if any(not _exact_json_equal(terminal.get(key), expected[key])
           for key in identity_fields):
        raise ValueError("stage terminal identity mismatch")
    if not _exact_json_equal(
            terminal.get("binding_sha256"), expected["binding_sha256"]):
        raise ValueError("stage terminal binding hash mismatch")
    if not _exact_json_equal(
            terminal.get("stage_snapshot_sha256"),
            expected["stage_snapshot_sha256"]):
        raise ValueError("stage snapshot hash mismatch")
    if not _exact_json_equal(terminal, expected):
        raise ValueError("stage terminal key set invalid")
    return terminal
