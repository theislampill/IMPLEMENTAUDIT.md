#!/usr/bin/env python3
"""Strict canonical loader for the R0038 operational-evidence substrate."""
from __future__ import annotations

import argparse
import ast
import base64
import contextlib
import ctypes
import datetime
import decimal
import hashlib
import io
import json
import math
import os
import pathlib
import platform
import re
import secrets
import stat
import subprocess
import sys
import tempfile
import types
import urllib.error
import urllib.request
from collections import Counter

# The controller's existing source identity transitively binds this new owner.
# Rebind both reviewed files together; missing, aliased or changed bytes fail closed.
_QUERY_POLICY_MODULE_SHA256 = '52d4d1fa89bee7e36eb3bb634051f8ca252a2cb7fa4a64a4b77aae1ef158da66'
_QUERY_POLICY_MODULE_BYTES = 8647
def _load_query_policy_module():
    import hashlib as _hashlib
    import os as _os
    import stat as _stat
    import sys as _sys
    import types as _types
    _path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'operational_query_policy.py')
    _fd = None
    try:
        _before = _os.lstat(_path)
        if (_stat.S_ISLNK(_before.st_mode) or not _stat.S_ISREG(_before.st_mode)
                or getattr(_before, "st_file_attributes", 0) & 0x400):
            raise ImportError("operational_query_policy.py: source is not a non-aliased regular file")
        _flags = _os.O_RDONLY | getattr(_os, "O_BINARY", 0) | getattr(_os, "O_NONBLOCK", 0) | getattr(_os, "O_NOFOLLOW", 0)
        _fd = _os.open(_path, _flags)
        _info = _os.fstat(_fd)
        if (not _stat.S_ISREG(_info.st_mode) or (_before.st_dev, _before.st_ino) != (_info.st_dev, _info.st_ino)):
            raise ImportError("operational_query_policy.py: source identity changed while opening")
        with _os.fdopen(_fd, "rb") as _stream:
            _fd = None
            _source = _stream.read(_QUERY_POLICY_MODULE_BYTES + 1)
    except OSError as _exc:
        raise ImportError("operational_query_policy.py: source unavailable") from _exc
    finally:
        if _fd is not None:
            _os.close(_fd)
    if len(_source) != _QUERY_POLICY_MODULE_BYTES or _hashlib.sha256(_source).hexdigest() != _QUERY_POLICY_MODULE_SHA256:
        raise ImportError("operational_query_policy.py: source identity mismatch")
    _module = _types.ModuleType(__name__ + ".query_policy_module")
    _module.__file__ = _path
    # Register before execution for annotations/introspection; undo a failed load.
    _previous = _sys.modules.get(_module.__name__)
    _sys.modules[_module.__name__] = _module
    try:
        exec(compile(_source, _path, "exec"), _module.__dict__)
    except BaseException:
        if _previous is None:
            _sys.modules.pop(_module.__name__, None)
        else:
            _sys.modules[_module.__name__] = _previous
        raise
    return _module
_query_policy_module = _load_query_policy_module()



RECORD_SCHEMA = "implementaudit-operational-evidence-v1"
VALIDATION_SCHEMA = "implementaudit-operational-evidence-validation-v1"
SCHEMA_DEFINITION = "implementaudit-operational-evidence-schema-v1"
REPOSITORY_COLLECTION_SCHEMA = "implementaudit-repository-collection-v1"
EVIDENCE_FAILURE_COLLECTION_SCHEMA = (
    "implementaudit-evidence-failure-collection-v1")
RELEASE_COLLECTION_SCHEMA = "implementaudit-release-collection-v1"
EXTERNAL_READ_CAPTURE_SCHEMA = "implementaudit-external-read-capture-v1"
STATIC_RECEIPT_SCHEMA = "implementaudit-static-receipt-v1"
STATIC_NORMALIZED_SCHEMA = "implementaudit-static-normalized-v1"
STATIC_NORMALIZED_SET_SCHEMA = "implementaudit-static-normalized-set-v1"
NATIVE_CURRENT_SCHEMA = "implementaudit-native-current-facts-v1"
SNAPSHOT_INPUT_SCHEMA = "implementaudit-operational-snapshot-input.v1"
SNAPSHOT_PAYLOAD_SCHEMA = "implementaudit-operational-snapshot-payload.v1"
SNAPSHOT_MANIFEST_SCHEMA = "IA-OPERATIONAL-SNAPSHOT-v1"
SNAPSHOT_CURRENT_SCHEMA = "implementaudit.operational-snapshot-current.v1"
SNAPSHOT_PUBLICATION_SCHEMA = "implementaudit-operational-snapshot-publication-v1"
SNAPSHOT_DIFF_SCHEMA = "implementaudit-operational-snapshot-diff.v1"
SNAPSHOT_PROJECTION_SCHEMA = "implementaudit-operational-snapshot-projection.v1"
SNAPSHOT_EXPORT_SCHEMA = "implementaudit-operational-snapshot-export.v1"
SNAPSHOT_ID_RE = re.compile(r"^iasnap-v1-[0-9a-f]{64}$")
SNAPSHOT_EVIDENCE_ID_RE = re.compile(
    r"^iasrc-v1-r0038-snapshot-([0-9a-f]{64})"
    r"(?:-([A-Za-z0-9][A-Za-z0-9._-]{0,30}))?$")
SNAPSHOT_CURRENT_KEYS = frozenset({
    "schema_version", "snapshot_id", "manifest_sha256", "source_pointer_oid"})
QUERY_SCHEMA = "implementaudit.operational-evidence-query.v1"
QUERY_STATUS_SCHEMA = "implementaudit.operational-evidence-status.v1"
QUERY_RESULT_SCHEMA = "implementaudit.operational-evidence-query-result.v1"
QUERY_WHY_SCHEMA = "implementaudit.operational-evidence-why.v1"
HISTORY_QUERY_SCHEMA = "implementaudit.history-query.v1"
HISTORY_REQUEST_SCHEMA = "implementaudit.history-query-request.v1"
HISTORY_CURSOR_SCHEMA = "implementaudit.history-query-cursor.v1"
HISTORY_EVENT_SCHEMA = "implementaudit.history-event.v1"
HISTORY_MANIFEST_SCHEMA = "implementaudit.state-generation-manifest.v1"
HISTORY_EVENT_ID_RE = re.compile(r"^iaevt-v1-[0-9a-f]{64}$")
HISTORY_SEQUENCE_RE = re.compile(r"^[0-9]{20}$")
HISTORY_FILTER_KEYS = frozenset({
    "event_ids", "record_kinds", "subject_ids", "source_evidence_ids",
    "statuses", "transitions"})
SNAPSHOT_MANIFEST_KEYS = frozenset({
    "schema_version", "controller_id", "claim_id", "run_id", "source_epoch",
    "source_pointer_oid", "source_evidence_entries"})
SNAPSHOT_OWNER_ENTRY_KEYS = frozenset({
    "source_evidence_id", "sha256", "kind", "root_identity",
    "host_identity", "input_path_flavor", "source_locator"})
SNAPSHOT_PAYLOAD_KEYS = frozenset({
    "schema_version", "snapshot_id", "aggregate", "families",
    "missing_or_omitted_state", "collections", "input_manifest_sha256"})
FAMILIES = (
    "CODE", "OWNERSHIP", "EXECUTION", "EVIDENCE", "FAILURE", "RELEASE")
STATES = (
    "CURRENT", "UNKNOWN", "UNSUPPORTED", "STALE", "UNVERIFIED",
    "CONTRADICTORY", "PARSER_ERROR", "INVALID")
AGGREGATES = ("COMPLETE", "DEGRADED", "STALE", "INVALID", "SUPERSEDED")
LAYERS = (
    "repository", "git", "planning", "controller", "execution",
    "evidence", "failure", "package", "install", "host", "ci",
    "release", "external", "public")
ENTITY_FAMILIES = {
    "Repository": "CODE", "Commit": "CODE", "Tree": "CODE",
    "Worktree": "CODE", "File": "CODE", "Symbol": "CODE",
    "Package": "CODE", "GeneratedArtifact": "CODE",
    "Writer": "OWNERSHIP", "Resource": "OWNERSHIP",
    "Controller": "EXECUTION", "CustodyClaim": "EXECUTION",
    "Receipt": "EXECUTION", "Run": "EXECUTION", "Phase": "EXECUTION",
    "WorkItem": "EXECUTION", "Claim": "EVIDENCE",
    "Criterion": "EVIDENCE", "Evidence": "EVIDENCE", "Check": "EVIDENCE",
    "Review": "EVIDENCE", "Andon": "FAILURE", "Residual": "FAILURE",
    "Countermeasure": "FAILURE", "Issue": "RELEASE",
    "PullRequest": "RELEASE", "WorkflowRun": "RELEASE",
    "Release": "RELEASE", "Tag": "RELEASE", "Asset": "RELEASE",
    "Install": "RELEASE", "PublicSurface": "RELEASE",
}
RELATION_TYPES = (
    "OWNS", "WRITES", "GENERATES", "PACKAGES", "INSTALLS", "CONSUMES",
    "DEPENDS_ON", "BLOCKS", "READY_WHEN", "SERIALISES_WITH", "JOINS",
    "CLAIMS", "EVIDENCES", "CONTRADICTS", "INVALIDATES", "SUPERSEDES",
    "FAILED_AT", "CONTAINED_BY", "REPAIRED_BY", "VERIFIED_BY",
    "RECOVERED_TO", "QUALIFIES", "MERGES_TO", "TAGS", "PUBLISHES",
    "READ_BACK_AS")
TOP_LEVEL_KEYS = {
    "schema", "aggregate", "families", "affected_families",
    "capability_declarations", "currentness_predicates", "entities",
    "relations", "payload_records"}
COMMON_KEYS = {
    "id", "family", "native_owner_identity", "source_identity",
    "evidence_layer", "currentness"}
HEX = frozenset("0123456789abcdef")
STATIC_OUTCOMES = (
    "CURRENT", "STALE", "UNSUPPORTED", "PARTIAL", "PARSER_ERROR",
    "CONTRADICTORY", "VERSION_MISMATCH", "TARGET_CONFIG_UNTRUSTED",
    "NOT_INSTALLED", "UNSUPPORTED_LANGUAGE", "TOOL_TIMEOUT", "TOOL_CRASH")
STATIC_FACT_KINDS = (
    "MODULE_EDGE", "REVERSE_DEPENDENT", "SOURCE_CYCLE", "NO_EDGE", "LEAF",
    "ORPHAN", "UNUSED", "UNREACHABLE", "UNRESOLVED_IMPORT", "FILE")
STATIC_NEGATIVE_KINDS = frozenset(
    {"NO_EDGE", "LEAF", "ORPHAN", "UNUSED", "UNREACHABLE"})


class OperationalEvidenceError(ValueError):
    """A stable typed refusal for unsupported or invalid evidence input."""

    def __init__(self, code: str, path: str, message: str):
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message

    def receipt(self) -> dict[str, str]:
        return {
            "schema": "implementaudit-operational-evidence-error-v1",
            "code": self.code,
            "path": self.path,
            "message": self.message,
        }


def _error(code: str, path: str, message: str) -> None:
    raise OperationalEvidenceError(code, path, message)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _error("OE_JSON_DUPLICATE_KEY", "$", f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(token):
    _error("OE_JSON_NONFINITE", "$", f"non-finite JSON number: {token}")


def _strict_int(token):
    try:
        return int(token)
    except ValueError:
        _error("OE_JSON_NUMBER_LIMIT", "$",
               "JSON integer exceeds the runtime conversion limit")


def _lossless_float(token):
    try:
        source = decimal.Decimal(token)
        value = float(source)
        round_trip = decimal.Decimal(repr(value)) if math.isfinite(value) else None
    except decimal.DecimalException:
        _error("OE_JSON_NUMBER_LOSS", "$", f"invalid JSON number: {token}")
    if round_trip is None:
        _error("OE_JSON_NONFINITE", "$", f"non-finite JSON number: {token}")
    sign_changed = (source.is_zero() and
                    source.is_signed() != (math.copysign(1.0, value) < 0.0))
    if round_trip != source or sign_changed:
        _error("OE_JSON_NUMBER_LOSS", "$", f"lossy JSON number: {token}")
    return value


def decode_strict_json_bytes(data: bytes, owner: str):
    if data.startswith(b"\xef\xbb\xbf"):
        _error("OE_UTF8_BOM", "$", f"{owner} must not contain a UTF-8 BOM")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        _error("OE_UTF8_INVALID", "$", f"{owner} must be valid UTF-8")
    try:
        return json.loads(
            text, object_pairs_hook=_unique_object,
            parse_constant=_nonfinite, parse_float=_lossless_float,
            parse_int=_strict_int)
    except OperationalEvidenceError:
        raise
    except (json.JSONDecodeError, RecursionError):
        _error("OE_JSON_MALFORMED", "$", f"{owner} is malformed JSON")


def validate_identity_json_v1(value, path="$"):
    """Keep canonical identity values portable across governed owners."""
    if value is None or type(value) in (bool, str):
        return
    if type(value) is int:
        if not -(2**63) <= value <= 2**63 - 1:
            _error("OE_JSON_MODEL_INVALID", path,
                   "integer is outside signed 64-bit range")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            validate_identity_json_v1(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                _error("OE_JSON_MODEL_INVALID", path, "object key is not a string")
            validate_identity_json_v1(item, f"{path}.{key}")
        return
    _error("OE_JSON_MODEL_INVALID", path, "floats and non-JSON values are forbidden")


def canonical_json_v1(value) -> bytes:
    """UTF-8 JSON, sorted object keys, declared array order, no whitespace."""
    validate_identity_json_v1(value)
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, RecursionError):
        _error("OE_JSON_MODEL_INVALID", "$", "value is not strict JSON")


def canonical_payload_text(value: str) -> str:
    """Normalize only line endings, then remove all trailing LF characters."""
    if type(value) is not str:
        _error("OE_SCHEMA_INVALID", "$.payload_records[].payload",
               "payload must be a string")
    return value.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


def _object(value, path, *, exact_keys=None, required=()):
    if type(value) is not dict:
        _error("OE_SCHEMA_INVALID", path, "must be an object")
    missing = set(required) - set(value)
    extra = set(value) - set(exact_keys) if exact_keys is not None else set()
    if missing:
        _error("OE_SCHEMA_INVALID", path,
               f"missing keys: {','.join(sorted(missing))}")
    if extra:
        _error("OE_SCHEMA_INVALID", path,
               f"unknown keys: {','.join(sorted(extra))}")
    return value


def _text(value, path):
    if type(value) is not str or not value:
        _error("OE_SCHEMA_INVALID", path, "must be a non-empty string")
    return value


def _string_list_violation_v1(value, *, allowed=None, unique=True):
    """Return the one producer list-grammar violation, if any."""
    if type(value) is not list:
        return None, "must be an array"
    for index, item in enumerate(value):
        if type(item) is not str or not item:
            return index, "must be a non-empty string"
        if allowed is not None and item not in allowed:
            return index, "unsupported value"
    if unique and len(set(value)) != len(value):
        return None, "must not contain duplicates"
    return None, None


def _string_list(value, path, *, allowed=None, unique=True):
    index, violation = _string_list_violation_v1(
        value, allowed=allowed, unique=unique)
    if violation is not None:
        member_path = path if index is None else f"{path}[{index}]"
        _error("OE_SCHEMA_INVALID", member_path, violation)
    return value


def _currentness(value, path):
    _object(value, path, exact_keys={"state", "invalidators"},
            required={"state", "invalidators"})
    state = value["state"]
    if state not in STATES:
        _error("OE_SCHEMA_INVALID", f"{path}.state", "unsupported state")
    invalidators = _string_list(value["invalidators"], f"{path}.invalidators")
    if state == "CURRENT" and invalidators:
        _error("OE_STALE_RECORD", path,
               "CURRENT record cannot retain an invalidator")
    if state == "STALE" and not invalidators:
        _error("OE_STALE_RECORD", path,
               "STALE record must name an invalidator")
    return state


def _common_record(value, path, *, exact_keys, required_extra=()):
    required = COMMON_KEYS | set(required_extra)
    _object(value, path, exact_keys=COMMON_KEYS | set(exact_keys), required=required)
    _text(value["id"], f"{path}.id")
    if value["family"] not in FAMILIES:
        _error("OE_SCHEMA_INVALID", f"{path}.family", "unsupported family")
    _text(value["native_owner_identity"], f"{path}.native_owner_identity")
    source = _object(
        value["source_identity"], f"{path}.source_identity",
        exact_keys={"id", "layer"}, required={"id", "layer"})
    _text(source["id"], f"{path}.source_identity.id")
    if source["layer"] not in LAYERS or value["evidence_layer"] not in LAYERS:
        _error("OE_SCHEMA_INVALID", path, "unsupported evidence layer")
    if source["layer"] != value["evidence_layer"]:
        _error("OE_CROSS_LAYER", path,
               "source layer and evidence layer must identify the same native leg")
    state = _currentness(value["currentness"], f"{path}.currentness")
    return state


def _validate_schema_definition(schema):
    try:
        expected = schema["properties"]["schema"]["const"]
        aggregates = tuple(schema["properties"]["aggregate"]["enum"])
        families = tuple(schema["properties"]["families"]["prefixItems"])
        family_values = tuple(item["const"] for item in families)
        states = tuple(schema["$defs"]["state"]["enum"])
        layers = tuple(schema["$defs"]["layer"]["enum"])
        entity_types = set(schema["$defs"]["entity"]["properties"]
                           ["record_type"]["enum"])
        relation_types = tuple(schema["$defs"]["relation"]["properties"]
                               ["relation_type"]["enum"])
        canonicalisation = schema["x-canonicalisation"]
        payload_normalisation = schema["x-payload-normalisation"]
    except (KeyError, TypeError):
        _error("OE_SCHEMA_DEFINITION_INVALID", "$schema",
               "schema definition is incomplete")
    if (schema.get("x-implementaudit-schema") != SCHEMA_DEFINITION or
            expected != RECORD_SCHEMA or aggregates != AGGREGATES or
            family_values != FAMILIES or states != STATES or layers != LAYERS or
            entity_types != set(ENTITY_FAMILIES) or
            relation_types != RELATION_TYPES or
            canonicalisation != {
                "identity": "canonical_json_v1", "encoding": "UTF-8",
                "bom": False, "object_keys": "recursive_lexicographic",
                "array_order": "declared_semantic_order",
                "insignificant_whitespace": False, "string_rewriting": False,
            } or payload_normalisation != {
                "identity": "canonical_payload_text_v1",
                "line_endings": "CRLF_and_CR_to_LF",
                "trailing_lf": "remove_all",
                "other_whitespace": "preserve", "unicode": "preserve",
            }):
        _error("OE_SCHEMA_DEFINITION_INVALID", "$schema",
               "schema definition does not match the loader contract")


def _digest(value, path):
    if (type(value) is not str or len(value) != 64 or
            any(character not in HEX for character in value)):
        _error("OE_SCHEMA_INVALID", path, "must be 64 lowercase hexadecimal")


def _git_object(value, path):
    if (type(value) is not str or len(value) != 40 or
            any(character not in HEX for character in value)):
        _error("OE_STATIC_RECEIPT_INVALID", path,
               "must be 40 lowercase hexadecimal")


def _boolean(value, path):
    if type(value) is not bool:
        _error("OE_STATIC_RECEIPT_INVALID", path, "must be a boolean")
    return value


def _safe_relative_path(value, path):
    _text(value, path)
    pure = pathlib.PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or value != pure.as_posix():
        _error("OE_REPOSITORY_PATH", path,
               "must be a normalized repository-relative POSIX path")
    return pure


def _run_git(root: pathlib.Path, *args: str, text: bool = True):
    environment = dict(os.environ)
    for name in tuple(environment):
        if name == "GIT_CONFIG_PARAMETERS" or name.startswith("GIT_CONFIG_KEY_"):
            environment.pop(name)
    environment.update({
        "GIT_CONFIG_COUNT": "0",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_OPTIONAL_LOCKS": "0",
    })
    for name in (
            "GIT_ASKPASS", "SSH_ASKPASS", "GIT_SSH", "GIT_SSH_COMMAND",
            "GIT_PROXY_COMMAND", "GIT_EXTERNAL_DIFF", "GIT_PAGER", "PAGER",
            "GIT_EDITOR", "GIT_SEQUENCE_EDITOR", "VISUAL", "EDITOR"):
        environment.pop(name, None)
    isolated_configuration = [
        "-c", "core.fsmonitor=false",
        "-c", f"core.hooksPath={os.devnull}",
        "-c", "credential.helper=",
        "-c", "core.sshCommand=",
        "-c", "diff.external=",
        "-c", "protocol.ext.allow=never",
    ]
    try:
        return subprocess.run(
            ["git", *isolated_configuration, "-C", os.fspath(root), *args],
            check=True,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=text, env=environment)
    except (FileNotFoundError, OSError, subprocess.CalledProcessError):
        _error("OE_REPOSITORY_GIT", "$repository",
               "repository Git facts could not be read")


def _python_module_map(paths):
    modules = {}
    for path in paths:
        if not path.endswith(".py"):
            continue
        parts = list(pathlib.PurePosixPath(path).with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts.pop()
        if parts:
            modules[".".join(parts)] = path
    return modules


def _import_candidates(source_path, node):
    source_parts = list(
        pathlib.PurePosixPath(source_path).with_suffix("").parts)
    if source_parts and source_parts[-1] == "__init__":
        package_parts = source_parts[:-1]
    else:
        package_parts = source_parts[:-1]
    names = []
    if isinstance(node, ast.Import):
        names.extend(alias.name for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        if node.level:
            trim = node.level - 1
            if trim > len(package_parts):
                return []
            base = package_parts[:len(package_parts) - trim]
            if node.module:
                base.extend(node.module.split("."))
            names.append(".".join(base))
        elif node.module:
            names.append(node.module)
    return sorted(set(names))


def _resolve_import(source_path, node, modules):
    return sorted({
        modules[name]
        for name in _import_candidates(source_path, node)
        if name in modules
    })


def _file_language(path):
    suffix = pathlib.PurePosixPath(path).suffix.lower()
    return {
        ".py": "python", ".sh": "shell", ".js": "javascript",
        ".jsx": "javascript", ".ts": "typescript", ".tsx": "typescript",
        ".json": "json",
    }.get(suffix, "unsupported")


def _read_repository_path(path):
    if path.is_symlink():
        return os.readlink(path).encode("utf-8"), "symlink"
    if path.is_file():
        return path.read_bytes(), "file"
    raise OSError("tracked path is not a readable file or symlink")


def _physical_file_row(relative, data=None, file_type=None):
    if data is None:
        return {"path": relative, "readable": False}
    return {
        "path": relative,
        "readable": True,
        "file_type": file_type,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _require_repository_snapshot_stable(
        root, paths, commit, tree, raw_paths, status, physical_file_rows):
    observed_file_rows = []
    for index, relative in enumerate(paths):
        pure = _safe_relative_path(relative, f"$repository.files[{index}]")
        path = root.joinpath(*pure.parts)
        try:
            data, file_type = _read_repository_path(path)
            observed_file_rows.append(
                _physical_file_row(relative, data, file_type))
        except (OSError, UnicodeError):
            observed_file_rows.append(_physical_file_row(relative))
    observed_commit = _run_git(
        root, "rev-parse", "--verify", "HEAD").stdout.strip()
    observed_tree = _run_git(
        root, "rev-parse", "--verify", "HEAD^{tree}").stdout.strip()
    observed_raw_paths = _run_git(root, "ls-files", "-z", text=False).stdout
    observed_status = _run_git(
        root, "status", "--porcelain=v1", "--untracked-files=all").stdout
    if (observed_commit != commit or observed_tree != tree or
            observed_raw_paths != raw_paths or observed_status != status or
            observed_file_rows != physical_file_rows):
        _error("OE_REPOSITORY_CHANGED_DURING_SCAN", "$repository",
               "repository physical snapshot changed during collection")


def _native_file(path, label, maximum=256 * 1024):
    try:
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or path.is_symlink() or
                bool(getattr(before, "st_file_attributes", 0) & 0x400) or
                before.st_size > maximum):
            raise OSError("unsafe native-current file")
        raw = path.read_bytes()
        after = path.lstat()
    except OSError:
        _error("OE_NATIVE_CURRENT_FILE", label,
               "required bounded native-current file is unreadable or unsafe")
    identity = (
        before.st_dev, before.st_ino, before.st_mode, before.st_size,
        before.st_mtime_ns)
    observed = (
        after.st_dev, after.st_ino, after.st_mode, after.st_size,
        after.st_mtime_ns)
    if identity != observed or len(raw) != before.st_size:
        _error("OE_NATIVE_CURRENT_CHANGED", label,
               "native-current file changed during observation")
    return raw


def _native_blob(repo, oid, label, maximum=512 * 1024):
    if type(oid) is not str or not re.fullmatch(r"[0-9a-f]{40}", oid):
        _error("OE_NATIVE_CURRENT_GIT", label, "Git object identity is malformed")
    try:
        object_type = _run_git(repo, "cat-file", "-t", oid).stdout.strip()
        size_text = _run_git(repo, "cat-file", "-s", oid).stdout.strip()
    except OperationalEvidenceError:
        _error("OE_NATIVE_CURRENT_GIT", label,
               "required native-current Git object is missing or unreadable")
    try:
        size = int(size_text)
    except ValueError:
        _error("OE_NATIVE_CURRENT_GIT", label, "Git object size is malformed")
    if object_type != "blob" or not 0 <= size <= maximum:
        _error("OE_NATIVE_CURRENT_GIT", label,
               "required native-current Git blob is absent or outside its bound")
    try:
        raw = _run_git(repo, "cat-file", "blob", oid, text=False).stdout
    except OperationalEvidenceError:
        _error("OE_NATIVE_CURRENT_GIT", label,
               "required native-current Git blob is missing or unreadable")
    if len(raw) != size:
        _error("OE_NATIVE_CURRENT_CHANGED", label,
               "native-current Git blob changed during observation")
    return raw


def _native_ref_oid(repo, ref, label):
    try:
        oid = _run_git(repo, "rev-parse", "--verify", ref).stdout.strip()
    except OperationalEvidenceError:
        _error("OE_NATIVE_CURRENT_GIT", label,
               "required native-current ref is missing or unreadable")
    if not re.fullmatch(r"[0-9a-f]{40}", oid):
        _error("OE_NATIVE_CURRENT_GIT", label, "native-current ref is malformed")
    return oid


def _native_exact_tsv(raw, schema, count, label):
    if (not raw.endswith(b"\n") or b"\n" in raw[:-1] or b"\r" in raw or
            b"\x00" in raw or any(
                byte < 0x20 and byte not in (0x09, 0x0A) or byte == 0x7f
                for byte in raw)):
        _error("OE_NATIVE_CURRENT_BYTES", label,
               "native-current record does not have exact LF-delimited TSV bytes")
    try:
        fields = raw[:-1].decode("utf-8", "strict").split("\t")
    except UnicodeDecodeError:
        _error("OE_NATIVE_CURRENT_BYTES", label,
               "native-current record is not exact UTF-8")
    if len(fields) != count or fields[0] != schema or any(field == "" for field in fields):
        _error("OE_NATIVE_CURRENT_BYTES", label,
               "native-current record schema or field population is malformed")
    return fields


def _native_exact_no_lf_tsv(raw, schema, count, label):
    if (not raw or b"\n" in raw or b"\r" in raw or b"\x00" in raw or any(
            byte < 0x20 and byte != 0x09 or byte == 0x7f for byte in raw)):
        _error("OE_NATIVE_CURRENT_BYTES", label,
               "native-current record does not have exact no-LF TSV bytes")
    try:
        fields = raw.decode("utf-8", "strict").split("\t")
    except UnicodeDecodeError:
        _error("OE_NATIVE_CURRENT_BYTES", label,
               "native-current record is not exact UTF-8")
    if len(fields) != count or fields[0] != schema or any(field == "" for field in fields):
        _error("OE_NATIVE_CURRENT_BYTES", label,
               "native-current record schema or field population is malformed")
    return fields


def _native_resolved_path(value, label):
    if type(value) is not str or not value or "\x00" in value:
        _error("OE_NATIVE_CURRENT_PATH", label, "native path is malformed")
    try:
        supplied = pathlib.Path(value)
        resolved = supplied.resolve(strict=True)
    except OSError:
        _error("OE_NATIVE_CURRENT_PATH", label, "native path cannot be resolved")
    if supplied.absolute() != resolved:
        _error("OE_NATIVE_CURRENT_PATH", label,
               "native path traverses an alias or is not canonical")
    return resolved


def _native_claim(run_root, repository, common, controller, claim, run_id):
    claimed_raw = _native_file(run_root / ".claimed", "$native.claim", 16 * 1024)
    if (not claimed_raw.endswith(b"\n") or b"\r" in claimed_raw or
            b"\n" in claimed_raw[:-1].replace(b"\n", b"", 9)):
        _error("OE_NATIVE_CURRENT_CLAIM", "$native.claim",
               "run claim does not have exact bounded LF records")
    try:
        lines = claimed_raw[:-1].decode("utf-8", "strict").split("\n")
    except UnicodeDecodeError:
        _error("OE_NATIVE_CURRENT_CLAIM", "$native.claim",
               "run claim is not exact UTF-8")
    keys = (
        "schema", "claim_id", "claimed_at_utc", "mode", "templates",
        "repo_root", "git_common_dir", "run_base", "run_root", "run_name")
    if len(lines) != len(keys):
        _error("OE_NATIVE_CURRENT_CLAIM", "$native.claim",
               "run claim field population is malformed")
    values = {}
    for key, line in zip(keys, lines):
        prefix = f"{key}="
        if not line.startswith(prefix) or line == prefix:
            _error("OE_NATIVE_CURRENT_CLAIM", "$native.claim",
                   "run claim field ordering is malformed")
        values[key] = line[len(prefix):]
    relative = pathlib.PurePosixPath(".IMPLEMENTAUDIT", "runs", run_id).as_posix()
    if (values["schema"] != "implementaudit.run-claim.v2" or
            values["claim_id"] != claim or values["run_base"] != ".IMPLEMENTAUDIT/runs" or
            values["run_root"] != relative or values["run_name"] != run_id or
            _native_resolved_path(values["repo_root"], "$native.claim.repo_root") != repository or
            _native_resolved_path(values["git_common_dir"], "$native.claim.git_common_dir") != common):
        _error("OE_NATIVE_CURRENT_CLAIM", "$native.claim",
               "run claim disagrees with native controller custody")
    controller_raw = _native_file(
        run_root / ".controller", "$native.controller_sentinel", 1024)
    if controller_raw != f"controller_id={controller}\n".encode("utf-8"):
        _error("OE_NATIVE_CURRENT_CLAIM", "$native.controller_sentinel",
               "controller sentinel disagrees with controller custody")
    return claimed_raw, controller_raw, relative


def _native_markdown_cells(line, expected, label):
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        _error("OE_NATIVE_CURRENT_STATE", label, "Markdown table row is malformed")
    cells = [cell.strip() for cell in stripped[1:-1].split("|")]
    if len(cells) != expected or any(cell == "" for cell in cells):
        _error("OE_NATIVE_CURRENT_STATE", label, "Markdown table row is malformed")
    return cells


def _native_state_facts(raw):
    if raw.startswith(b"\xef\xbb\xbf"):
        _error("OE_NATIVE_CURRENT_STATE", "$native.STATE",
               "hot STATE must not contain a UTF-8 BOM")
    try:
        lines = raw.decode("utf-8", "strict").splitlines()
    except UnicodeDecodeError:
        _error("OE_NATIVE_CURRENT_STATE", "$native.STATE",
               "hot STATE is not exact UTF-8")
    epochs = [line[len("Current epoch: "):].strip() for line in lines
              if line.startswith("Current epoch: ")]
    if len(epochs) != 1 or not re.fullmatch(r"G[0-9A-F]{4}", epochs[0]):
        _error("OE_NATIVE_CURRENT_STATE", "$native.STATE.current_epoch",
               "hot STATE has no unique canonical current epoch")
    headings = [index for index, line in enumerate(lines) if line == "## Current phase"]
    if len(headings) != 1:
        _error("OE_NATIVE_CURRENT_STATE", "$native.STATE.current_phase",
               "hot STATE has no unique current-phase section")
    start = headings[0] + 1
    end = next((index for index in range(start, len(lines))
                if lines[index].startswith("## ")), len(lines))
    phase_rows = {}
    for index in range(start, end):
        if not lines[index].lstrip().startswith("|"):
            continue
        cells = _native_markdown_cells(
            lines[index], 2, f"$native.STATE.current_phase[{index + 1}]")
        if cells in (["Field", "Value"], ["---", "---"]):
            continue
        if cells[0] in phase_rows:
            _error("OE_NATIVE_CURRENT_STATE", "$native.STATE.current_phase",
                   "hot STATE current-phase field is duplicated")
        phase_rows[cells[0]] = cells[1]
    next_action = phase_rows.get("Next action", "").strip()
    andon_state = phase_rows.get("Andon state", "").strip()
    if not next_action or next_action in {"-", "none", "pending"}:
        _error("OE_NATIVE_CURRENT_MISSING", "$native.STATE.next_action",
               "hot STATE has no exact next action")
    open_andons = sorted(set(re.findall(
        r"(?<![A-Za-z0-9_-])([A-Z][A-Z0-9_-]*)=ACTIVE(?![A-Za-z0-9_-])",
        andon_state)))
    if not open_andons:
        _error("OE_NATIVE_CURRENT_MISSING", "$native.STATE.open_andons",
               "hot STATE has no explicit open Andon")

    instruction_header = [
        "Instr", "Reference", "Kind", "Authority", "Subject", "Issued epoch",
        "Status", "Status evidence", "Supersedes/by", "Scope end"]
    header_rows = []
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        try:
            cells = _native_markdown_cells(
                line, 10, f"$native.STATE.instructions[{index + 1}]")
        except OperationalEvidenceError:
            continue
        if cells == instruction_header:
            header_rows.append(index)
    if len(header_rows) != 1:
        _error("OE_NATIVE_CURRENT_STATE", "$native.STATE.instructions",
               "hot STATE has no unique instruction table")
    mapping = [
        "id", "reference", "kind", "authority", "subject", "issued_epoch",
        "status", "status_evidence", "supersedes_by", "scope_end"]
    active = []
    seen = set()
    index = header_rows[0] + 2
    while index < len(lines) and lines[index].lstrip().startswith("|"):
        cells = _native_markdown_cells(
            lines[index], 10, f"$native.STATE.instructions[{index + 1}]")
        if cells[0] in seen:
            _error("OE_NATIVE_CURRENT_STATE", "$native.STATE.instructions",
                   "instruction identity is duplicated")
        seen.add(cells[0])
        row = dict(zip(mapping, cells))
        if row["status"] == "active":
            active.append(row)
        index += 1
    if not active:
        _error("OE_NATIVE_CURRENT_MISSING", "$native.STATE.active_instructions",
               "hot STATE has no active instruction")
    return {
        "epoch": epochs[0], "next_action": next_action,
        "andon_state": andon_state, "open_andons": open_andons,
        "active_instructions": sorted(active, key=lambda row: row["id"]),
    }


def _native_pointer(raw, controller, claim, run_id):
    value = decode_strict_json_bytes(raw, "current-generation pointer")
    validate_identity_json_v1(value)
    keys = {
        "schema_version", "controller_id", "claim_id", "run_id",
        "generation_id", "predecessor_pointer_oid",
        "predecessor_pointer_digest", "generation_manifest_oid",
        "generation_manifest_digest", "cold_high_water", "hot_state_digest",
        "hot_roadmap_digest", "work_graph_path", "work_graph_digest",
        "query_contract_version", "source_epoch", "degraded_state",
        "pointer_digest"}
    _object(value, "$native.pointer", exact_keys=keys, required=keys)
    if canonical_json_v1(value) != raw:
        _error("OE_NATIVE_CURRENT_BYTES", "$native.pointer",
               "current-generation pointer bytes are not canonical_json_v1")
    patterns = {
        "claim_id": r"[0-9a-f]{32}", "run_id": r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}",
        "generation_id": r"G[0-9A-F]{4}", "source_epoch": r"G[0-9A-F]{4}",
        "generation_manifest_oid": r"[0-9a-f]{40}",
        "generation_manifest_digest": r"[0-9a-f]{64}",
        "cold_high_water": r"[0-9]{20}", "hot_state_digest": r"[0-9a-f]{64}",
        "hot_roadmap_digest": r"[0-9a-f]{64}",
        "work_graph_digest": r"[0-9a-f]{64}", "pointer_digest": r"[0-9a-f]{64}",
    }
    if any(type(value[name]) is not str or not re.fullmatch(pattern, value[name])
           for name, pattern in patterns.items()):
        _error("OE_NATIVE_CURRENT_POINTER", "$native.pointer",
               "current-generation pointer identity is malformed")
    predecessor = (
        value["predecessor_pointer_oid"], value["predecessor_pointer_digest"])
    if (predecessor[0] is None) != (predecessor[1] is None):
        _error("OE_NATIVE_CURRENT_POINTER", "$native.pointer",
               "pointer predecessor identity is incomplete")
    if predecessor[0] is not None and (
            type(predecessor[0]) is not str or
            not re.fullmatch(r"[0-9a-f]{40}", predecessor[0]) or
            type(predecessor[1]) is not str or
            not re.fullmatch(r"[0-9a-f]{64}", predecessor[1])):
        _error("OE_NATIVE_CURRENT_POINTER", "$native.pointer",
               "pointer predecessor identity is malformed")
    if (value["schema_version"] != "implementaudit.state-generation-pointer.v1" or
            value["controller_id"] != controller or value["claim_id"] != claim or
            value["run_id"] != run_id or
            value["generation_id"] != value["source_epoch"] or
            value["query_contract_version"] != "implementaudit.history-query.v1" or
            value["work_graph_path"] != "WORK_GRAPH.json" or
            value["degraded_state"] not in {"NONE", "ACTIVEGRAPH_DOGFOOD_DEGRADED"}):
        _error("OE_NATIVE_CURRENT_POINTER", "$native.pointer",
               "pointer disagrees with native controller/claim/run/epoch custody")
    unsigned = dict(value)
    supplied = unsigned.pop("pointer_digest")
    observed = hashlib.sha256(canonical_json_v1(unsigned)).hexdigest()
    if supplied != observed:
        _error("OE_NATIVE_CURRENT_POINTER", "$native.pointer.pointer_digest",
               "pointer digest is stale")
    return value


def _native_module_from_bytes(raw, path, name, label):
    module = types.ModuleType(name)
    module.__file__ = os.fspath(path)
    module.__package__ = ""
    try:
        exec(compile(raw, os.fspath(path), "exec"), module.__dict__)
    except Exception as exc:
        _error("OE_NATIVE_CURRENT_SOURCE", label,
               f"canonical read-only source cannot be loaded: {exc}")
    return module


def _native_graph_projection(raw):
    compiler_path = pathlib.Path(__file__).resolve().with_name("compile-work-graph.py")
    compiler_raw = _native_file(
        compiler_path, "$native.work_graph_compiler", 256 * 1024)
    module = _native_module_from_bytes(
        compiler_raw, compiler_path,
        "_implementaudit_native_work_graph_compiler",
        "$native.work_graph_compiler")
    try:
        projection = module.compile_frontier_projection(raw)
    except Exception as exc:
        _error("OE_NATIVE_CURRENT_GRAPH", "$native.WORK_GRAPH",
               f"canonical HC-H4 compiler rejected WORK_GRAPH: {exc}")
    if _native_file(
            compiler_path, "$native.work_graph_compiler", 256 * 1024) != compiler_raw:
        _error("OE_NATIVE_CURRENT_CHANGED", "$native.work_graph_compiler",
               "HC-H4 compiler changed during byte-bound execution")
    required_frontier = {
        "population", "counts", "active", "ready", "blocked_summary",
        "writer_holds", "resource_holds", "digest"}
    if type(projection) is not dict or not required_frontier <= set(projection):
        _error("OE_NATIVE_CURRENT_MISSING", "$native.WORK_GRAPH.frontier",
               "WORK_GRAPH frontier facts are missing")
    population = projection["population"]
    counts = projection["counts"]
    if (type(population) is not int or population < 0 or
            type(counts) is not dict or set(counts) != {
                "DONE", "ACTIVE", "READY", "BLOCKED"} or
            any(type(count) is not int or count < 0
                for count in counts.values()) or
            type(projection["digest"]) is not str or
            not re.fullmatch(r"[0-9a-f]{64}", projection["digest"])):
        _error("OE_NATIVE_CURRENT_MISSING", "$native.WORK_GRAPH.frontier",
               "WORK_GRAPH frontier population is malformed")
    active = projection["active"]
    ready = projection["ready"]
    blocked_summary = projection["blocked_summary"]
    writer_holds = projection["writer_holds"]
    resource_holds = projection["resource_holds"]
    if (type(active) is not list or type(ready) is not list or
            type(blocked_summary) is not dict or type(writer_holds) is not dict or
            type(resource_holds) is not dict):
        _error("OE_NATIVE_CURRENT_MISSING", "$native.WORK_GRAPH.frontier",
               "WORK_GRAPH frontier collection types are malformed")
    def valid_members(members):
        return (type(members) is list and
                all(type(member) is str and member for member in members) and
                members == sorted(set(members)))

    if not valid_members(active) or not valid_members(ready):
        _error("OE_NATIVE_CURRENT_MISSING", "$native.WORK_GRAPH.frontier",
               "WORK_GRAPH frontier identities are malformed")
    for mapping in (blocked_summary, writer_holds, resource_holds):
        for identity, members in mapping.items():
            if type(identity) is not str or not identity or not valid_members(members):
                _error("OE_NATIVE_CURRENT_MISSING", "$native.WORK_GRAPH.frontier",
                       "WORK_GRAPH frontier hold maps are malformed")
    if (sum(counts.values()) != population or
            len(active) != counts["ACTIVE"] or
            len(ready) != counts["READY"] or
            len(blocked_summary) != counts["BLOCKED"]):
        _error("OE_NATIVE_CURRENT_MISSING", "$native.WORK_GRAPH.frontier",
               "WORK_GRAPH frontier census is inconsistent")
    return (projection, hashlib.sha256(compiler_raw).hexdigest(),
            compiler_path, compiler_raw)


def _native_predecessor(
        repo, controller, controller_oid, claim, run_id, generation, token):
    if type(token) is not str or token.count("@") != 1:
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt.predecessor",
               "receipt predecessor token is malformed")
    ref, oid = token.split("@")
    ordinal = int(generation[1:], 16)
    if ordinal <= 1:
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt.predecessor",
               "receipt-v3 has no admissible predecessor generation")
    expected_generation = f"G{ordinal - 1:04X}"
    expected_ref = f"refs/implementaudit/continuity-receipts/{controller}/{expected_generation}"
    if ref != expected_ref or _native_ref_oid(
            repo, ref, "$native.receipt.predecessor_ref") != oid:
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt.predecessor",
               "receipt predecessor is stale or foreign")
    raw = _native_blob(repo, oid, "$native.receipt.predecessor")
    if raw.startswith(b"implementaudit.continuity-receipt.v2\t"):
        fields = _native_exact_tsv(
            raw, "implementaudit.continuity-receipt.v2", 12,
            "$native.receipt.predecessor")
        if (fields[1:4] != [controller, controller_oid, claim] or
                not re.fullmatch(r"[0-9a-f]{40}", fields[4]) or
                not re.fullmatch(r"[0-9a-f]{40}", fields[5]) or
                not re.fullmatch(r"[0-9a-f]{64}", fields[6]) or
                not re.fullmatch(r"[0-9a-f]{64}", fields[7]) or
                not (fields[8] == "none" or
                     re.fullmatch(r"[0-9a-f]{40}", fields[8])) or
                fields[9] not in {
                    "host-reported-compaction", "new-session",
                    "handoff-resume", "manual-resume",
                    "inferred-context-gap"} or
                fields[10] != expected_generation or not fields[11]):
            _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt.predecessor",
                   "v2 predecessor is malformed or foreign to current custody")
    elif raw.startswith(b"implementaudit.continuity-receipt.v3\t"):
        fields = _native_exact_tsv(
            raw, "implementaudit.continuity-receipt.v3", 18,
            "$native.receipt.predecessor")
        if (fields[1] != controller or fields[2] != claim or fields[3] != run_id or
                fields[4] != expected_generation or
                not re.fullmatch(r"[0-9a-f]{40}", fields[5]) or
                fields[6] != f"refs/implementaudit/current-generations/{controller}" or
                not re.fullmatch(r"[0-9a-f]{40}", fields[7]) or
                not re.fullmatch(r"[0-9a-f]{64}", fields[8]) or
                not re.fullmatch(r"[0-9a-f]{64}", fields[9]) or
                not re.fullmatch(r"[0-9a-f]{64}", fields[10]) or
                fields[11] != "WORK_GRAPH.json" or
                not re.fullmatch(r"[0-9a-f]{64}", fields[12]) or
                not re.fullmatch(r"[0-9a-f]{40}", fields[13]) or
                not re.fullmatch(r"[0-9a-f]{64}", fields[14]) or
                not re.fullmatch(r"[0-9]{20}", fields[15]) or not fields[16]):
            _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt.predecessor",
                   "v3 predecessor is malformed or foreign to current custody")
        predecessor_ordinal = int(expected_generation[1:], 16)
        if predecessor_ordinal <= 1 or fields[17].count("@") != 1:
            _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt.predecessor",
                   "v3 predecessor own-predecessor token is malformed")
        own_ref, own_oid = fields[17].split("@")
        own_epoch = f"G{predecessor_ordinal - 1:04X}"
        if (own_ref !=
                f"refs/implementaudit/continuity-receipts/{controller}/{own_epoch}" or
                not re.fullmatch(r"[0-9a-f]{40}", own_oid)):
            _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt.predecessor",
                   "v3 predecessor own-predecessor token is not structurally immediate")
    else:
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt.predecessor",
               "receipt predecessor schema is unsupported")
    return ref, oid, raw


def _native_route_module():
    path = pathlib.Path(__file__).resolve().with_name("route-transaction.py")
    raw = _native_file(path, "$native.route_validator", 512 * 1024)
    module = _native_module_from_bytes(
        raw, path, "_implementaudit_native_route_transaction",
        "$native.route_validator")
    required = (
        "validate_pure_current_route", "trusted_host_executable",
        "sanitized_action_environment", "bash_script_path")
    if any(not callable(getattr(module, name, None)) for name in required):
        _error("OE_NATIVE_CURRENT_SOURCE", "$native.route_validator",
               "canonical R0033 read-only predicates are incomplete")
    return module, path, raw


def _native_child_environment(route_module):
    with contextlib.redirect_stdout(io.StringIO()):
        source = route_module.sanitized_action_environment()
    inherited = {
        "comspec", "pathext", "systemdrive", "systemroot", "temp", "tmp",
        "tmpdir", "windir",
    }
    fixed = {
        "GIT_ATTR_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM",
        "GIT_EXTERNAL_DIFF", "GIT_OPTIONAL_LOCKS", "GIT_PAGER", "LC_ALL",
        "PAGER", "PATH",
    }
    environment = {
        key: value for key, value in source.items()
        if key in fixed or key.casefold() in inherited
    }
    if "PATH" not in environment:
        _error("OE_NATIVE_CURRENT_SOURCE", "$native.child_environment",
               "private R0011 child PATH is unavailable")
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONSAFEPATH"] = "1"
    return environment


def _native_private_residue(closure):
    try:
        members = sorted(closure.iterdir(), key=lambda item: os.fspath(item))
    except OSError:
        members = []
    return sorted([os.fspath(closure), *(os.fspath(path) for path in members)])


def _native_cleanup_private_closure(closure, expected):
    try:
        for path, raw in expected:
            if _native_file(path, "$native.private_continuity_closure") != raw:
                raise OSError("private R0011 closure member changed before cleanup")
            os.unlink(path)
        os.rmdir(closure)
    except (OSError, OperationalEvidenceError):
        residue = _native_private_residue(closure)
        _error(
            "OE_NATIVE_CURRENT_CLEANUP",
            "$native.private_continuity_closure",
            "private R0011 closure cleanup refused; residue=" +
            json.dumps(residue, sort_keys=True, separators=(",", ":")) +
            "; manual reconciliation required",
        )


_NATIVE_R0011_CHILD_BOOTSTRAP = r'''set -u
claim_path="$1"
validate_path="$2"
expected_claim="$3"
expected_validate="$4"
shift 4
claim_payload="$(base64 < "$claim_path")" || exit 90
validate_payload="$(base64 < "$validate_path")" || exit 91
claim_text="$(printf '%s' "$claim_payload" | base64 -d; printf 'X')" || exit 92
validate_text="$(printf '%s' "$validate_payload" | base64 -d; printf 'X')" || exit 93
claim_text="${claim_text%X}"
validate_text="${validate_text%X}"
observed_claim="$(printf '%s' "$claim_text" | sha256sum | cut -d' ' -f1)" || exit 94
observed_validate="$(printf '%s' "$validate_text" | sha256sum | cut -d' ' -f1)" || exit 95
[ "$observed_claim" = "$expected_claim" ] || exit 96
[ "$observed_validate" = "$expected_validate" ] || exit 97
bash() {
  if [ "$#" -ge 1 ] && [ "${1##*/}" = "validate-run-root.sh" ]; then
    shift
    ( set -- "$@"; eval "$validate_text" )
  else
    command bash "$@"
  fi
}
( set -- "$@"; eval "$claim_text" )
status=$?
printf 'implementaudit-native-r0011-child-v1\t%s\t%s\n' \
  "$observed_claim" "$observed_validate" >&2
exit "$status"
'''


def _native_require_current_receipt(repo, controller, receipt, route_module):
    claim_path = pathlib.Path(__file__).resolve().with_name("claim-run.sh")
    validate_path = claim_path.with_name("validate-run-root.sh")
    claim_raw = _native_file(claim_path, "$native.continuity_validator", 256 * 1024)
    validate_raw = _native_file(
        validate_path, "$native.continuity_claim_validator", 256 * 1024)
    closure = None
    completed = None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            bash = route_module.trusted_host_executable(repo, "bash")
        environment = _native_child_environment(route_module)
        closure = pathlib.Path(tempfile.mkdtemp(
            prefix="implementaudit-native-current-r0011-"))
        materialized_claim = closure / claim_path.name
        materialized_validate = closure / validate_path.name
        expected = (
            (materialized_claim, claim_raw),
            (materialized_validate, validate_raw),
        )
        for target, raw in expected:
            with target.open("xb") as stream:
                stream.write(raw)
            if _native_file(
                    target, "$native.private_continuity_closure",
                    256 * 1024) != raw:
                _error(
                    "OE_NATIVE_CURRENT_CHANGED",
                    "$native.private_continuity_closure",
                    "private R0011 materialization changed before child launch")
        with contextlib.redirect_stdout(io.StringIO()):
            claim_arg = route_module.bash_script_path(materialized_claim)
            validate_arg = route_module.bash_script_path(materialized_validate)
        completed = subprocess.run(
            [
                os.fspath(bash), "-c", _NATIVE_R0011_CHILD_BOOTSTRAP,
                "implementaudit-native-r0011-child", claim_arg, validate_arg,
                hashlib.sha256(claim_raw).hexdigest(),
                hashlib.sha256(validate_raw).hexdigest(),
                "--require-current-continuity", controller,
            ],
            cwd=repo, env=environment, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            check=False)
    except (OSError, SystemExit):
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt",
               "canonical R0011 currentness validator is unavailable")
    finally:
        if closure is not None:
            _native_cleanup_private_closure(closure, expected)
    child_binding = (
        "implementaudit-native-r0011-child-v1\t" +
        hashlib.sha256(claim_raw).hexdigest() + "\t" +
        hashlib.sha256(validate_raw).hexdigest())
    if completed.returncode or completed.stdout.strip() != receipt:
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt",
               "canonical R0011 currentness validator rejected the receipt chain")
    if completed.stderr.splitlines().count(child_binding) != 1:
        _error("OE_NATIVE_CURRENT_CHANGED", "$native.continuity_child",
               "completed R0011 child did not bind the exact helper identities")
    if _native_file(
            claim_path, "$native.continuity_validator", 256 * 1024) != claim_raw:
        _error("OE_NATIVE_CURRENT_CHANGED", "$native.continuity_validator",
               "R0011 validator changed during currentness validation")
    if _native_file(
            validate_path, "$native.continuity_claim_validator",
            256 * 1024) != validate_raw:
        _error("OE_NATIVE_CURRENT_CHANGED", "$native.continuity_claim_validator",
               "R0011 claim validator changed during currentness validation")
    return claim_path, claim_raw, validate_path, validate_raw


def _native_route(
        repo, controller, controller_oid, claim, run_root, generation, receipt,
        boundary_kind, boundary_event_id, next_action, route_module):
    expected_current = {
        "controller_id": controller,
        "controller_record_oid": controller_oid,
        "claim_id": claim,
        "explicit_run_root": os.fspath(run_root),
        "continuity_generation": generation,
        "continuity_receipt": receipt,
        "boundary_kind": boundary_kind,
        "boundary_event_id": boundary_event_id,
        "next_action": next_action,
    }
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return route_module.validate_pure_current_route(
                repo, controller, expected_current)
    except (Exception, SystemExit):
        _error("OE_NATIVE_CURRENT_ROUTE", "$native.route",
               "canonical R0033 pure current-route validator rejected the route record")

def collect_native_current():
    """Read one exact native hot/current fact set without lifecycle authority."""
    source_repository = pathlib.Path(__file__).resolve().parents[3]
    observed_source = _native_resolved_path(
        _run_git(source_repository, "rev-parse", "--path-format=absolute",
                 "--show-toplevel").stdout.strip(), "$native.source_repository")
    if observed_source != source_repository:
        _error("OE_NATIVE_CURRENT_CUSTODY", "$native.source_repository",
               "carrier source is not in its own repository checkout")
    common = _native_resolved_path(
        _run_git(source_repository, "rev-parse", "--path-format=absolute",
                 "--git-common-dir").stdout.strip(), "$native.git_common_dir")
    controller_refs = _run_git(
        source_repository, "for-each-ref", "--format=%(refname)",
        "refs/implementaudit/controllers/").stdout.splitlines()
    if len(controller_refs) != 1:
        _error("OE_NATIVE_CURRENT_CUSTODY", "$native.controller",
               "native controller population must contain exactly one ref")
    controller_ref = controller_refs[0]
    prefix = "refs/implementaudit/controllers/"
    controller = controller_ref[len(prefix):] if controller_ref.startswith(prefix) else ""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", controller):
        _error("OE_NATIVE_CURRENT_CUSTODY", "$native.controller",
               "native controller identity is malformed")
    controller_oid = _native_ref_oid(
        source_repository, controller_ref, "$native.controller.ref")
    controller_fields = _native_exact_tsv(
        _native_blob(source_repository, controller_oid, "$native.controller"),
        "implementaudit.controller-current.v1", 4, "$native.controller")
    claim = controller_fields[2]
    if (controller_fields[1] != controller or
            not re.fullmatch(r"[0-9a-f]{32}", claim)):
        _error("OE_NATIVE_CURRENT_CUSTODY", "$native.controller",
               "native controller record is foreign or malformed")
    run_root = _native_resolved_path(controller_fields[3], "$native.run_root")
    try:
        repository = run_root.parents[2]
    except (ValueError, IndexError):
        _error("OE_NATIVE_CURRENT_CUSTODY", "$native.run_root",
               "native run root is outside fixed run custody")
    try:
        run_relative = run_root.relative_to(repository)
    except ValueError:
        _error("OE_NATIVE_CURRENT_CUSTODY", "$native.run_root",
               "native run root is outside controller repository")
    if (len(run_relative.parts) != 3 or run_relative.parts[:2] != (
            ".IMPLEMENTAUDIT", "runs") or run_root.is_symlink()):
        _error("OE_NATIVE_CURRENT_CUSTODY", "$native.run_root",
               "native run root is not the fixed bound-run-root location")
    run_id = run_relative.parts[2]
    controller_common = _native_resolved_path(
        _run_git(repository, "rev-parse", "--path-format=absolute",
                 "--git-common-dir").stdout.strip(), "$native.controller_git_common_dir")
    if controller_common != common:
        _error("OE_NATIVE_CURRENT_CUSTODY", "$native.controller",
               "controller repository is foreign to carrier Git custody")
    claimed_raw, sentinel_raw, run_relative_text = _native_claim(
        run_root, repository, common, controller, claim, run_id)

    state_path = run_root / "STATE.md"
    roadmap_path = run_root / "ROADMAP.md"
    graph_path = run_root / "WORK_GRAPH.json"
    state_raw = _native_file(state_path, "$native.STATE")
    roadmap_raw = _native_file(roadmap_path, "$native.ROADMAP")
    graph_raw = _native_file(graph_path, "$native.WORK_GRAPH")
    state = _native_state_facts(state_raw)
    (projection, compiler_sha256, compiler_path,
     compiler_raw) = _native_graph_projection(graph_raw)
    state_sha256 = hashlib.sha256(state_raw).hexdigest()
    roadmap_sha256 = hashlib.sha256(roadmap_raw).hexdigest()
    graph_sha256 = hashlib.sha256(graph_raw).hexdigest()

    invalidation_ref = f"refs/implementaudit/continuity-invalidations/{controller}"
    invalidation_oid = _native_ref_oid(
        source_repository, invalidation_ref, "$native.invalidation.ref")
    invalidation = _native_exact_tsv(
        _native_blob(source_repository, invalidation_oid, "$native.invalidation"),
        "implementaudit.continuity-invalidation.v1", 6, "$native.invalidation")
    if (invalidation[1:4] != [controller, controller_oid, claim] or
            invalidation[4] not in {
                "host-reported-compaction", "new-session", "handoff-resume",
                "manual-resume", "inferred-context-gap"}):
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.invalidation",
               "continuity invalidation is foreign or malformed")

    pointer_ref = f"refs/implementaudit/current-generations/{controller}"
    pointer_oid = _native_ref_oid(
        source_repository, pointer_ref, "$native.pointer.ref")
    pointer_raw = _native_blob(source_repository, pointer_oid, "$native.pointer")
    pointer = _native_pointer(pointer_raw, controller, claim, run_id)
    generation = pointer["source_epoch"]
    if (state["epoch"] != generation or pointer["hot_state_digest"] != state_sha256 or
            pointer["hot_roadmap_digest"] != roadmap_sha256 or
            pointer["work_graph_digest"] != graph_sha256):
        _error("OE_NATIVE_CURRENT_STALE", "$native.hot",
               "hot STATE/ROADMAP/WORK_GRAPH disagree with current pointer")

    receipt_ref = f"refs/implementaudit/continuity-receipts/{controller}/{generation}"
    receipt_oid = _native_ref_oid(
        source_repository, receipt_ref, "$native.receipt.ref")
    receipt_fields = _native_exact_tsv(
        _native_blob(source_repository, receipt_oid, "$native.receipt"),
        "implementaudit.continuity-receipt.v3", 18, "$native.receipt")
    receipt = f"{receipt_ref}@{receipt_oid}"
    expected_receipt = [
        "implementaudit.continuity-receipt.v3", controller, claim, run_id,
        generation, invalidation_oid, pointer_ref, pointer_oid,
        pointer["pointer_digest"], state_sha256, roadmap_sha256,
        "WORK_GRAPH.json", graph_sha256, pointer["generation_manifest_oid"],
        pointer["generation_manifest_digest"], pointer["cold_high_water"],
        state["next_action"], receipt_fields[17]]
    if receipt_fields != expected_receipt:
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt",
               "receipt-v3 disagrees with pointer, hot files, or next action")
    predecessor_ref, predecessor_oid, predecessor_raw = _native_predecessor(
        source_repository, controller, controller_oid, claim, run_id,
        generation, receipt_fields[17])

    marker_ref = f"refs/implementaudit/current-generation-migrations/{controller}"
    marker_oid = _native_ref_oid(
        source_repository, marker_ref, "$native.marker.ref")
    marker = _native_exact_no_lf_tsv(
        _native_blob(source_repository, marker_oid, "$native.marker"),
        "implementaudit.current-generation-migration.v1", 10, "$native.marker")
    if (marker[:4] != [
            "implementaudit.current-generation-migration.v1", controller, claim,
            run_id] or not re.fullmatch(r"G[0-9A-F]{4}", marker[4]) or
            marker[5:7] != [
                pointer_ref, "implementaudit.state-generation-pointer.v1"] or
            marker[9] != "true"):
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.marker",
               "permanent migration marker is malformed or foreign")
    genesis_generation = marker[4]
    genesis_receipt_ref = marker[7]
    genesis_receipt_oid = marker[8]
    if (genesis_receipt_ref !=
            f"refs/implementaudit/continuity-receipts/{controller}/{genesis_generation}" or
            _native_ref_oid(source_repository, genesis_receipt_ref,
                            "$native.marker.receipt_ref") != genesis_receipt_oid):
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.marker",
               "permanent migration marker receipt is stale or foreign")
    genesis_receipt_fields = _native_exact_tsv(
        _native_blob(source_repository, genesis_receipt_oid,
                     "$native.marker.receipt"),
        "implementaudit.continuity-receipt.v3", 18,
        "$native.marker.receipt")
    if (genesis_receipt_fields[:5] != [
            "implementaudit.continuity-receipt.v3", controller, claim, run_id,
            genesis_generation] or genesis_receipt_fields[6] != pointer_ref or
            not re.fullmatch(r"[0-9a-f]{40}", genesis_receipt_fields[7])):
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.marker",
               "permanent migration marker receipt is malformed or foreign")
    genesis_pointer_oid = genesis_receipt_fields[7]
    genesis_pointer = _native_pointer(
        _native_blob(source_repository, genesis_pointer_oid,
                     "$native.marker.pointer"),
        controller, claim, run_id)
    if (genesis_pointer["source_epoch"] != genesis_generation or
            genesis_pointer["generation_id"] != genesis_generation or
            genesis_pointer["predecessor_pointer_oid"] is not None or
            genesis_pointer["predecessor_pointer_digest"] is not None or
            genesis_receipt_fields[8:16] != [
                genesis_pointer["pointer_digest"],
                genesis_pointer["hot_state_digest"],
                genesis_pointer["hot_roadmap_digest"],
                genesis_pointer["work_graph_path"],
                genesis_pointer["work_graph_digest"],
                genesis_pointer["generation_manifest_oid"],
                genesis_pointer["generation_manifest_digest"],
                genesis_pointer["cold_high_water"]]):
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.marker",
               "permanent migration marker does not bind the immutable genesis")
    if genesis_receipt_fields[17].count("@") != 1:
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.marker",
               "permanent genesis predecessor token is malformed")
    genesis_predecessor_ref, genesis_predecessor_oid = (
        genesis_receipt_fields[17].split("@"))
    genesis_ordinal = int(genesis_generation[1:], 16)
    if (genesis_ordinal <= 1 or genesis_predecessor_ref !=
            f"refs/implementaudit/continuity-receipts/{controller}/"
            f"G{genesis_ordinal - 1:04X}" or
            not re.fullmatch(r"[0-9a-f]{40}", genesis_predecessor_oid)):
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.marker",
               "permanent genesis predecessor token is not structurally immediate")
    current_ordinal = int(generation[1:], 16)
    if current_ordinal < genesis_ordinal:
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.marker",
               "current generation predates permanent genesis")
    if current_ordinal == genesis_ordinal:
        if (pointer_oid != genesis_pointer_oid or
                pointer["predecessor_pointer_oid"] is not None or
                pointer["predecessor_pointer_digest"] is not None):
            _error("OE_NATIVE_CURRENT_RECEIPT", "$native.marker",
                   "current genesis disagrees with permanent marker")
    else:
        predecessor_fields = _native_exact_tsv(
            predecessor_raw, "implementaudit.continuity-receipt.v3", 18,
            "$native.receipt.predecessor")
        if (pointer["predecessor_pointer_oid"] != predecessor_fields[7] or
                pointer["predecessor_pointer_digest"] != predecessor_fields[8]):
            _error("OE_NATIVE_CURRENT_RECEIPT", "$native.pointer.predecessor",
                   "current pointer is not joined to its immediate receipt predecessor")
    route_module, route_validator_path, route_validator_raw = _native_route_module()
    (continuity_validator_path, continuity_validator_raw,
     continuity_claim_validator_path, continuity_claim_validator_raw) = (
        _native_require_current_receipt(
            repository, controller, receipt, route_module))
    route = _native_route(
        source_repository, controller, controller_oid, claim, run_root,
        generation, receipt, invalidation[4], invalidation[5],
        state["next_action"], route_module)

    ref_fence = {
        controller_ref: controller_oid, invalidation_ref: invalidation_oid,
        pointer_ref: pointer_oid, receipt_ref: receipt_oid, marker_ref: marker_oid,
        genesis_receipt_ref: genesis_receipt_oid,
        predecessor_ref: predecessor_oid,
        route["ref"]: route["record_oid"]}
    file_fence = {
        run_root / ".claimed": claimed_raw, run_root / ".controller": sentinel_raw,
        state_path: state_raw, roadmap_path: roadmap_raw, graph_path: graph_raw,
        compiler_path: compiler_raw,
        route_validator_path: route_validator_raw,
        continuity_validator_path: continuity_validator_raw,
        continuity_claim_validator_path: continuity_claim_validator_raw}
    if _run_git(
            source_repository, "for-each-ref", "--format=%(refname)",
            "refs/implementaudit/controllers/").stdout.splitlines() != controller_refs:
        _error("OE_NATIVE_CURRENT_CHANGED", "$native.controller",
               "controller population changed during observation")
    if any(_native_ref_oid(
            source_repository, ref, "$native.final_ref_fence") != oid
           for ref, oid in ref_fence.items()):
        _error("OE_NATIVE_CURRENT_CHANGED", "$native.refs",
               "native-current ref changed during observation")
    if any(_native_file(path, "$native.final_file_fence") != raw
           for path, raw in file_fence.items()):
        _error("OE_NATIVE_CURRENT_CHANGED", "$native.hot",
               "native-current file changed during observation")

    result = {
        "schema": NATIVE_CURRENT_SCHEMA,
        "authority_ceiling": "READ_ONLY_NATIVE_CURRENT_FACT",
        "establishes": [],
        "repository": {
            "root": repository.as_posix(), "git_common_dir": common.as_posix()},
        "controller": {
            "id": controller, "ref": controller_ref, "record_oid": controller_oid},
        "claim": {
            "id": claim, "run_id": run_id, "run_root": run_relative_text},
        "continuity": {
            "generation": generation, "source_epoch": pointer["source_epoch"],
            "invalidation_ref": invalidation_ref,
            "invalidation_oid": invalidation_oid,
            "boundary_kind": invalidation[4], "boundary_event_id": invalidation[5],
            "pointer_ref": pointer_ref, "pointer_oid": pointer_oid,
            "pointer_digest": pointer["pointer_digest"],
            "receipt_schema": receipt_fields[0], "receipt_ref": receipt_ref,
            "receipt_oid": receipt_oid, "receipt": receipt,
            "marker_ref": marker_ref, "marker_oid": marker_oid,
            "generation_manifest_oid": pointer["generation_manifest_oid"],
            "generation_manifest_digest": pointer["generation_manifest_digest"],
            "cold_high_water": pointer["cold_high_water"],
            "degraded_state": pointer["degraded_state"]},
        "hot": {
            "state_path": "STATE.md", "state_sha256": state_sha256,
            "roadmap_path": "ROADMAP.md", "roadmap_sha256": roadmap_sha256,
            "work_graph_path": "WORK_GRAPH.json",
            "work_graph_sha256": graph_sha256,
            "work_graph_compiler_sha256": compiler_sha256},
        "frontier": projection,
        "andon_state": state["andon_state"],
        "open_andons": state["open_andons"],
        "active_instructions": state["active_instructions"],
        "next_action": state["next_action"],
        "route": route,
    }
    result["semantic_sha256"] = hashlib.sha256(canonical_json_v1(result)).hexdigest()
    final_route = _native_route(
        source_repository, controller, controller_oid, claim, run_root,
        generation, receipt, invalidation[4], invalidation[5],
        state["next_action"], route_module)
    if final_route != route:
        _error("OE_NATIVE_CURRENT_CHANGED", "$native.route",
               "R0033 route identity changed during final semantic observation")
    return result


def collect_repository(root: pathlib.Path):
    """Collect exact read-only Git/file/package facts and bounded Python AST edges."""
    root = pathlib.Path(root).resolve()
    if not root.is_dir():
        _error("OE_REPOSITORY_UNREADABLE", "$repository",
               "repository root must be a readable directory")
    top = pathlib.Path(
        _run_git(root, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    if top != root:
        _error("OE_REPOSITORY_ROOT", "$repository",
               "root must be the exact Git worktree top level")
    commit = _run_git(root, "rev-parse", "--verify", "HEAD").stdout.strip()
    tree = _run_git(
        root, "rev-parse", "--verify", "HEAD^{tree}").stdout.strip()
    _git_object(commit, "$repository.commit")
    _git_object(tree, "$repository.tree")
    raw_paths = _run_git(root, "ls-files", "-z", text=False).stdout
    try:
        path_values = raw_paths.decode("utf-8").split("\0")
    except UnicodeDecodeError:
        _error("OE_REPOSITORY_PATH", "$repository.files",
               "tracked paths must be valid UTF-8")
    paths = sorted(path for path in path_values if path)
    status = _run_git(
        root, "status", "--porcelain=v1", "--untracked-files=all").stdout
    worktree_state = "CLEAN" if not status else "DIRTY"

    facts = []
    diagnostics = {"warnings": [], "errors": [], "skipped": [], "unknown": []}
    file_rows = []
    physical_file_rows = []
    file_bytes = {}
    file_error = False
    for index, relative in enumerate(paths):
        pure = _safe_relative_path(relative, f"$repository.files[{index}]")
        path = root.joinpath(*pure.parts)
        try:
            data, file_type = _read_repository_path(path)
        except (OSError, UnicodeError):
            file_error = True
            physical_file_rows.append(_physical_file_row(relative))
            diagnostics["errors"].append(f"tracked-path-unreadable:{relative}")
            facts.append({
                "kind": "FILE_UNREADABLE_OBSERVATION", "path": relative,
                "state": "STALE", "provenance": {
                    "method": "git-ls-files+working-tree-read",
                    "commit": commit, "tree": tree,
                },
            })
            continue
        digest = hashlib.sha256(data).hexdigest()
        physical_file_rows.append(
            _physical_file_row(relative, data, file_type))
        file_bytes[relative] = data
        file_rows.append({"path": relative, "bytes": len(data), "sha256": digest})
        facts.append({
            "kind": "FILE", "path": relative, "sha256": digest,
            "bytes": len(data), "file_type": file_type,
            "language": _file_language(relative), "state": "CURRENT",
            "provenance": {
                "method": "git-ls-files+working-tree-sha256",
                "commit": commit, "tree": tree,
            },
        })

    _require_repository_snapshot_stable(
        root, paths, commit, tree, raw_paths, status, physical_file_rows)
    input_file_set_sha256 = hashlib.sha256(
        canonical_json_v1(file_rows)).hexdigest()

    modules = _python_module_map(file_bytes)
    python_paths = sorted(path for path in file_bytes if path.endswith(".py"))
    ast_provenance = None
    if python_paths:
        try:
            ast_package_sha256 = hashlib.sha256(
                pathlib.Path(ast.__file__).read_bytes()).hexdigest()
        except (AttributeError, OSError):
            _error("OE_STATIC_COLLECTOR_IDENTITY", "$repository.python_ast",
                   "Python AST collector bytes could not be identified")
        ast_provenance = {
            "collector_identity": "python-stdlib-ast",
            "collector_version": (
                f"{platform.python_implementation()}-{platform.python_version()}"),
            "collector_package_sha256": ast_package_sha256,
            "invocation_identity": "ast.parse(mode=exec,type_comments=false)",
            "output_schema_identity": REPOSITORY_COLLECTION_SCHEMA,
            "parser": "python-ast-static-imports-v1",
        }
    static_invocations = []
    parser_error = False
    for relative in python_paths:
        digest = hashlib.sha256(file_bytes[relative]).hexdigest()
        static_invocations.append({
            "collector": "python_ast", "input_path": relative,
            "input_sha256": digest, **ast_provenance,
        })
        try:
            source = file_bytes[relative].decode("utf-8")
            parsed = ast.parse(source, filename=relative, mode="exec")
        except (UnicodeDecodeError, SyntaxError) as exc:
            parser_error = True
            diagnostics["errors"].append(
                f"python-parser-error:{relative}:{type(exc).__name__}")
            facts.append({
                "kind": "PARSER_ERROR_OBSERVATION", "path": relative,
                "state": "PARSER_ERROR",
                "provenance": {
                    **ast_provenance,
                    "input_path": relative, "input_sha256": digest,
                },
            })
            continue
        for node in ast.walk(parsed):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                candidates = _import_candidates(relative, node)
                resolved = _resolve_import(relative, node, modules)
                for target in resolved:
                    provenance = {
                        **ast_provenance,
                        "input_path": relative, "input_sha256": digest,
                    }
                    facts.append({
                        "kind": "PYTHON_IMPORT", "source": relative,
                        "target": target, "state": "CURRENT",
                        "provenance": provenance,
                    })
                    facts.append({
                        "kind": "PYTHON_REVERSE_DEPENDENT", "source": target,
                        "target": relative, "state": "CURRENT",
                        "provenance": provenance,
                    })
                for target in sorted(name for name in candidates
                                     if name not in modules):
                    facts.append({
                        "kind": "UNSUPPORTED_IMPORT_OBSERVATION",
                        "source": relative, "target": target,
                        "state": "UNSUPPORTED", "provenance": {
                            **ast_provenance,
                            "input_path": relative, "input_sha256": digest,
                            "reason": "outside-declared-local-module-map",
                        },
                    })
            elif (isinstance(node, ast.Call) and
                  ((isinstance(node.func, ast.Name) and
                    node.func.id == "__import__") or
                   (isinstance(node.func, ast.Attribute) and
                    node.func.attr == "import_module"))):
                diagnostics["unknown"].append(
                    f"computed-import:{relative}:{getattr(node, 'lineno', 0)}")

    package_state = "NOT_APPLICABLE"
    package_path = "package/implementaudit-package.json"
    if package_path in file_bytes:
        package_state = "SUPPORTED"
        try:
            manifest = decode_strict_json_bytes(
                file_bytes[package_path], "package manifest")
            _object(manifest, "$package", required={"package_name"})
            package_name = _text(manifest["package_name"], "$package.package_name")
            facts.append({
                "kind": "PACKAGE_MANIFEST", "path": package_path,
                "package_name": package_name,
                "sha256": hashlib.sha256(file_bytes[package_path]).hexdigest(),
                "state": "CURRENT", "provenance": {
                    "parser": "strict-json-v1", "input_path": package_path,
                },
            })
            roots = manifest.get("shared_resource_roots", [])
            if type(roots) is not list:
                _error("OE_SCHEMA_INVALID", "$package.shared_resource_roots",
                       "must be an array")
            for index, declared in enumerate(roots):
                pure = _safe_relative_path(
                    declared, f"$package.shared_resource_roots[{index}]")
                prefix = pure.as_posix().rstrip("/") + "/"
                if any(path == pure.as_posix() or path.startswith(prefix)
                       for path in file_bytes):
                    facts.append({
                        "kind": "PACKAGE_ROOT", "package_name": package_name,
                        "path": pure.as_posix(), "state": "CURRENT",
                        "provenance": {
                            "parser": "strict-json-v1",
                            "input_path": package_path,
                            "input_sha256": hashlib.sha256(
                                file_bytes[package_path]).hexdigest(),
                        },
                    })
                else:
                    diagnostics["unknown"].append(
                        f"declared-package-root-missing:{pure.as_posix()}")
        except OperationalEvidenceError as exc:
            package_state = "PARSER_ERROR"
            diagnostics["errors"].append(
                f"package-manifest-error:{exc.code}:{exc.path}")
            facts.append({
                "kind": "PACKAGE_MANIFEST_ERROR", "path": package_path,
                "state": "PARSER_ERROR", "provenance": {
                    "parser": "strict-json-v1", "input_path": package_path,
                    "input_sha256": hashlib.sha256(
                        file_bytes[package_path]).hexdigest(),
                },
            })

    registry_path = "scripts/verify-package.sh"
    if registry_path in file_bytes:
        facts.append({
            "kind": "REGISTRY_FILE", "path": registry_path,
            "sha256": hashlib.sha256(file_bytes[registry_path]).hexdigest(),
            "state": "UNSUPPORTED", "provenance": {
                "method": "exact-file-fact-only",
                "reason": "shell-registry-parser-not-admitted",
            },
        })
        registry_state = "UNSUPPORTED"
        registry_reason = "shell_registry_exact_file_fact_only"
    else:
        registry_state = "NOT_APPLICABLE"
        registry_reason = "registry_file_absent"

    if not static_invocations:
        python_state = "NOT_APPLICABLE"
        python_reason = "no_tracked_python_inputs"
    elif parser_error:
        python_state = "PARTIAL"
        python_reason = "parser_error_population_retained"
    else:
        python_state = "SUPPORTED"
        python_reason = "bounded_positive_ast_edges"
    python_capability = {
        "capability": "python_ast", "state": python_state,
        "reason_code": python_reason,
    }
    if ast_provenance is not None:
        python_capability["provenance"] = {
            **ast_provenance,
            "input_file_set_sha256": input_file_set_sha256,
        }
    capabilities = [
        {"capability": "file_facts",
         "state": "PARTIAL" if file_error else "SUPPORTED",
         "reason_code": ("tracked_file_unreadable" if file_error else
                         "tracked_working_tree_bytes_hashed")},
        {"capability": "package_manifest", "state": package_state,
         "reason_code": "strict_json_positive_declarations_only"},
        python_capability,
        {"capability": "validation_registry_entries", "state": registry_state,
         "reason_code": registry_reason},
    ]
    _require_repository_snapshot_stable(
        root, paths, commit, tree, raw_paths, status, physical_file_rows)
    facts.sort(key=lambda row: canonical_json_v1(row))
    static_invocations.sort(key=lambda row: canonical_json_v1(row))
    for values in diagnostics.values():
        values.sort()
    result = {
        "schema": REPOSITORY_COLLECTION_SCHEMA,
        "repository": {
            "commit": commit, "tree": tree,
            "worktree_state": worktree_state,
            "input_file_set_sha256": input_file_set_sha256,
        },
        "capabilities": sorted(capabilities, key=lambda row: row["capability"]),
        "diagnostics": diagnostics,
        "facts": facts,
        "static_collector_invocations": static_invocations,
    }
    immutable_result = decode_strict_json_bytes(
        canonical_json_v1(result), "repository collection result")
    _require_repository_snapshot_stable(
        root, paths, commit, tree, raw_paths, status, physical_file_rows)
    return immutable_result


def collect_evidence_failure(root: pathlib.Path):
    """Collect canonical EVIDENCE/FAILURE run artifacts without promotion."""
    root = pathlib.Path(root).resolve()
    if not root.is_dir():
        _error("OE_RUN_ARTIFACT_MISSING", "$run_artifact",
               "run-artifact root must be a readable directory")
    artifact_path = root / "operational-evidence.json"
    if artifact_path.is_symlink() or not artifact_path.is_file():
        _error("OE_RUN_ARTIFACT_MISSING", "$run_artifact",
               "canonical operational-evidence.json is required")
    try:
        artifact_bytes = artifact_path.read_bytes()
    except OSError:
        _error("OE_RUN_ARTIFACT_MISSING", "$run_artifact",
               "canonical operational-evidence.json is unreadable")
    if len(artifact_bytes) > 1024 * 1024:
        _error("OE_RUN_ARTIFACT_INVALID", "$run_artifact",
               "canonical run artifact exceeds the C04 byte bound")
    artifact = decode_strict_json_bytes(artifact_bytes, "canonical run artifact")
    top_keys = {
        "schema", "run_identity", "artifact_identity", "first_red_id",
        "weakest_leg_id", "residual_ids", "evidence_records",
        "failure_records"}
    _object(artifact, "$run_artifact", exact_keys=top_keys, required=top_keys)
    if artifact["schema"] != "implementaudit-run-evidence-v1":
        _error("OE_RUN_ARTIFACT_INVALID", "$run_artifact.schema",
               "unsupported canonical run-artifact schema")
    run_identity = _text(
        artifact["run_identity"], "$run_artifact.run_identity")
    artifact_identity = _text(
        artifact["artifact_identity"], "$run_artifact.artifact_identity")
    artifact_sha256 = hashlib.sha256(artifact_bytes).hexdigest()

    if type(artifact["evidence_records"]) is not list:
        _error("OE_RUN_ARTIFACT_INVALID", "$run_artifact.evidence_records",
               "must be an array")
    evidence_keys = {
        "id", "sequence", "record_type", "claim_id", "criterion_id", "leg",
        "result_class", "proxy", "source_identity", "native_owner_identity",
        "currentness", "controls", "contrary_evidence"}
    evidence_records = []
    evidence_by_id = {}
    evidence_sequences = []
    for index, source_record in enumerate(artifact["evidence_records"]):
        path = f"$run_artifact.evidence_records[{index}]"
        record = _object(
            source_record, path, exact_keys=evidence_keys,
            required=evidence_keys)
        record_id = _text(record["id"], f"{path}.id")
        if record_id in evidence_by_id:
            _error("OE_RUN_ARTIFACT_INVALID", f"{path}.id",
                   "evidence record id must be unique")
        sequence = record["sequence"]
        if type(sequence) is not int or sequence < 0:
            _error("OE_RUN_ARTIFACT_INVALID", f"{path}.sequence",
                   "sequence must be a non-negative integer")
        if record["record_type"] not in (
                "Claim", "Criterion", "Evidence", "Check", "Review"):
            _error("OE_RUN_ARTIFACT_INVALID", f"{path}.record_type",
                   "unsupported EVIDENCE record type")
        for key in (
                "claim_id", "criterion_id", "source_identity",
                "native_owner_identity"):
            _text(record[key], f"{path}.{key}")
        if record["leg"] not in (
                "ATTEMPT", "RECEIPT", "EFFECT", "RECOVERY", "CLOSURE"):
            _error("OE_RUN_ARTIFACT_INVALID", f"{path}.leg",
                   "unsupported evidence leg")
        if record["result_class"] not in (
                "RED", "GREEN", "NONVERDICT", "UNKNOWN"):
            _error("OE_RUN_ARTIFACT_INVALID", f"{path}.result_class",
                   "unsupported evidence result class")
        proxy = _boolean(record["proxy"], f"{path}.proxy")
        if proxy and record["leg"] not in ("ATTEMPT", "RECEIPT"):
            _error("OE_RUN_EVIDENCE_PROXY", path,
                   "proxy evidence cannot become effect, recovery or closure")
        _currentness(record["currentness"], f"{path}.currentness")
        _string_list(record["controls"], f"{path}.controls")
        _string_list(
            record["contrary_evidence"], f"{path}.contrary_evidence")
        normalized = {
            **record,
            "family": "EVIDENCE",
            "authority_ceiling": "READ_ONLY_NATIVE_ARTIFACT_FACT",
            "artifact_sha256": artifact_sha256,
        }
        evidence_records.append(normalized)
        evidence_by_id[record_id] = normalized
        evidence_sequences.append(sequence)
    if evidence_sequences != sorted(evidence_sequences) or len(set(
            evidence_sequences)) != len(evidence_sequences):
        _error("OE_RUN_ARTIFACT_INVALID", "$run_artifact.evidence_records",
               "evidence sequence must be unique and increasing")
    for record in evidence_records:
        if any(reference not in evidence_by_id
               for reference in record["contrary_evidence"]):
            _error("OE_RUN_EVIDENCE_REFERENCE",
                   f"$run_artifact.evidence_records[{record['id']}].contrary_evidence",
                   "contrary evidence must reference a retained evidence record")

    red_records = [
        record for record in evidence_records
        if record["result_class"] == "RED" and not record["proxy"]]
    if red_records:
        first_red_id = _text(
            artifact["first_red_id"], "$run_artifact.first_red_id")
        if (first_red_id not in evidence_by_id or
                first_red_id != min(
                    red_records, key=lambda row: row["sequence"])["id"]):
            _error("OE_RUN_EVIDENCE_FIRST_RED", "$run_artifact.first_red_id",
                   "first RED must retain the earliest non-proxy RED record")
        first_red_state = "PRESENT"
    else:
        if artifact["first_red_id"] is not None:
            _error("OE_RUN_EVIDENCE_FIRST_RED", "$run_artifact.first_red_id",
                   "no-first-RED population must use JSON null")
        first_red_id = None
        first_red_state = "NOT_APPLICABLE"
    weakest_leg_id = _text(
        artifact["weakest_leg_id"], "$run_artifact.weakest_leg_id")
    weakest = evidence_by_id.get(weakest_leg_id)
    if (weakest is None or weakest["proxy"] or
            (red_records and weakest["result_class"] != "RED")):
        _error("OE_RUN_EVIDENCE_WEAKEST", "$run_artifact.weakest_leg_id",
               "weakest leg must be non-proxy and RED when a RED exists")

    if type(artifact["failure_records"]) is not list:
        _error("OE_RUN_ARTIFACT_INVALID", "$run_artifact.failure_records",
               "must be an array")
    failure_keys = {
        "id", "sequence", "record_type", "andon_id", "abnormality_class",
        "statement", "cause_confidence", "evidence_ids", "recovery_state",
        "source_identity", "native_owner_identity", "currentness"}
    failure_records = []
    failure_by_id = {}
    failure_sequences = []
    for index, source_record in enumerate(artifact["failure_records"]):
        path = f"$run_artifact.failure_records[{index}]"
        record = _object(
            source_record, path, exact_keys=failure_keys, required=failure_keys)
        record_id = _text(record["id"], f"{path}.id")
        if record_id in failure_by_id or record_id in evidence_by_id:
            _error("OE_RUN_FAILURE_INVALID", f"{path}.id",
                   "failure record id must be globally unique")
        sequence = record["sequence"]
        if type(sequence) is not int or sequence < 0:
            _error("OE_RUN_FAILURE_INVALID", f"{path}.sequence",
                   "sequence must be a non-negative integer")
        if record["record_type"] not in (
                "Andon", "Residual", "Containment", "Countermeasure",
                "Rerun", "Recovery"):
            _error("OE_RUN_FAILURE_INVALID", f"{path}.record_type",
                   "unsupported FAILURE record type")
        for key in (
                "andon_id", "abnormality_class", "statement",
                "source_identity", "native_owner_identity"):
            _text(record[key], f"{path}.{key}")
        if record["cause_confidence"] not in (
                "UNKNOWN", "LOW", "MEDIUM", "HIGH"):
            _error("OE_RUN_FAILURE_INVALID", f"{path}.cause_confidence",
                   "unsupported cause confidence")
        if record["recovery_state"] not in (
                "NOT_CLAIMED", "ATTEMPTED", "OBSERVED", "UNVERIFIED"):
            _error("OE_RUN_FAILURE_INVALID", f"{path}.recovery_state",
                   "unsupported recovery state")
        _string_list(record["evidence_ids"], f"{path}.evidence_ids")
        _currentness(record["currentness"], f"{path}.currentness")
        normalized = {
            **record,
            "family": "FAILURE",
            "authority_ceiling": "READ_ONLY_NATIVE_ARTIFACT_FACT",
            "artifact_sha256": artifact_sha256,
        }
        failure_records.append(normalized)
        failure_by_id[record_id] = normalized
        failure_sequences.append(sequence)
    if failure_sequences != sorted(failure_sequences) or len(set(
            failure_sequences)) != len(failure_sequences):
        _error("OE_RUN_FAILURE_INVALID", "$run_artifact.failure_records",
               "failure sequence must be unique and increasing")
    andon_ids = {
        record["id"] for record in failure_records
        if record["record_type"] == "Andon"}
    for record in failure_records:
        if record["andon_id"] not in andon_ids:
            _error("OE_RUN_FAILURE_REFERENCE",
                   f"$run_artifact.failure_records[{record['id']}].andon_id",
                   "failure lineage must reference a retained Andon")
        if any(reference not in evidence_by_id
               for reference in record["evidence_ids"]):
            _error("OE_RUN_FAILURE_REFERENCE",
                   f"$run_artifact.failure_records[{record['id']}].evidence_ids",
                   "failure lineage must reference retained evidence")
        if record["recovery_state"] == "OBSERVED":
            recovery_evidence = [
                evidence_by_id[reference]
                for reference in record["evidence_ids"]]
            if (not recovery_evidence or any(
                    evidence["leg"] != "RECOVERY" or
                    evidence["result_class"] != "GREEN" or
                    evidence["proxy"] or
                    evidence["currentness"]["state"] != "CURRENT"
                    for evidence in recovery_evidence)):
                _error("OE_RUN_RECOVERY_EVIDENCE",
                       f"$run_artifact.failure_records[{record['id']}]",
                       "observed recovery requires current direct recovery evidence")
    residual_ids = _string_list(
        artifact["residual_ids"], "$run_artifact.residual_ids")
    if any(residual_id not in failure_by_id or
           failure_by_id[residual_id]["record_type"] != "Residual"
           for residual_id in residual_ids):
        _error("OE_RUN_FAILURE_REFERENCE", "$run_artifact.residual_ids",
               "declared residual must reference a retained Residual record")

    layer_census = Counter(
        record["leg"] for record in evidence_records)
    layer_census_result = {
        leg: layer_census.get(leg, 0)
        for leg in (
            "ATTEMPT", "RECEIPT", "EFFECT", "RECOVERY", "CLOSURE")
    }
    result = {
        "schema": EVIDENCE_FAILURE_COLLECTION_SCHEMA,
        "families": ["EVIDENCE", "FAILURE"],
        "source": {
            "path": "operational-evidence.json",
            "sha256": artifact_sha256,
            "run_identity": run_identity,
            "artifact_identity": artifact_identity,
        },
        "first_red_id": first_red_id,
        "first_red_state": first_red_state,
        "weakest_leg_id": weakest_leg_id,
        "residual_ids": list(residual_ids),
        "layer_census": layer_census_result,
        "evidence_records": evidence_records,
        "failure_records": failure_records,
        "establishes": [],
    }
    result["semantic_sha256"] = hashlib.sha256(
        canonical_json_v1(result)).hexdigest()
    immutable_result = decode_strict_json_bytes(
        canonical_json_v1(result), "evidence/failure collection")
    if artifact_path.is_symlink():
        _error("OE_RUN_ARTIFACT_CHANGED", "$run_artifact",
               "canonical run artifact changed during collection")
    try:
        final_artifact_bytes = artifact_path.read_bytes()
    except OSError:
        _error("OE_RUN_ARTIFACT_CHANGED", "$run_artifact",
               "canonical run artifact changed during collection")
    if final_artifact_bytes != artifact_bytes:
        _error("OE_RUN_ARTIFACT_CHANGED", "$run_artifact",
               "canonical run artifact changed during collection")
    return immutable_result


def _utc_timestamp(value, path):
    _text(value, path)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value) is None:
        _error("OE_EXTERNAL_CAPTURE_INVALID", path,
               "must be an exact UTC second timestamp")
    try:
        datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        _error("OE_EXTERNAL_CAPTURE_INVALID", path,
               "must be a valid UTC calendar timestamp")
    return value


def _validate_capture_chronology(captured_at, expires_at, evaluated_at, path):
    if captured_at >= expires_at or evaluated_at < captured_at:
        _error("OE_EXTERNAL_CAPTURE_INVALID", path,
               "capture chronology must satisfy captured < expires and "
               "evaluated >= captured")


def _external_boundary_currentness(
        auth_state, rate_state, pagination_state, object_drift,
        expires_at, evaluated_at):
    invalidators = []
    if auth_state == "ABSENT":
        invalidators.append("AUTH_ABSENT")
    elif auth_state == "UNKNOWN":
        invalidators.append("AUTH_UNKNOWN")
    if rate_state == "EXHAUSTED":
        invalidators.append("RATE_LIMITED")
    elif rate_state == "UNKNOWN":
        invalidators.append("RATE_UNKNOWN")
    if pagination_state == "INCOMPLETE":
        invalidators.append("PAGINATION_INCOMPLETE")
    elif pagination_state == "UNKNOWN":
        invalidators.append("PAGINATION_UNKNOWN")
    if object_drift:
        invalidators.append("OBJECT_DRIFT")
    if evaluated_at >= expires_at:
        invalidators.append("CAPTURE_EXPIRED")
    if any(item in invalidators for item in ("OBJECT_DRIFT", "CAPTURE_EXPIRED")):
        state = "STALE"
    elif any(item in invalidators for item in ("AUTH_ABSENT", "AUTH_UNKNOWN")):
        state = "UNVERIFIED"
    elif invalidators:
        state = "UNKNOWN"
    else:
        state = "CURRENT"
    return {"state": state, "invalidators": invalidators}


def _compose_currentness(native, capture):
    """Retain both native and capture invalidators without promotion."""
    state_rank = {
        "CURRENT": 0, "UNSUPPORTED": 1, "UNKNOWN": 2, "UNVERIFIED": 3,
        "STALE": 4, "CONTRADICTORY": 5, "PARSER_ERROR": 6,
        "INVALID": 7,
    }
    state = max(
        (native["state"], capture["state"]), key=state_rank.__getitem__)
    invalidators = []
    for invalidator in [
            *native["invalidators"], *capture["invalidators"]]:
        if invalidator not in invalidators:
            invalidators.append(invalidator)
    return {"state": state, "invalidators": invalidators}


def collect_release(root: pathlib.Path):
    """Collect local and frozen external RELEASE facts without promotion."""
    root = pathlib.Path(root).resolve()
    repository_before = collect_repository(root)
    repository = repository_before["repository"]
    file_facts = {
        row["path"]: row for row in repository_before["facts"]
        if row.get("kind") == "FILE"}

    def read_fixed_json(relative, owner):
        path = root / relative
        if path.is_symlink() or not path.is_file():
            _error("OE_RELEASE_ARTIFACT_MISSING", f"$release.{relative}",
                   f"canonical {relative} is required")
        try:
            data = path.read_bytes()
        except OSError:
            _error("OE_RELEASE_ARTIFACT_MISSING", f"$release.{relative}",
                   f"canonical {relative} is unreadable")
        tracked = file_facts.get(relative)
        digest = hashlib.sha256(data).hexdigest()
        if tracked is None or tracked.get("sha256") != digest:
            _error("OE_RELEASE_CHANGED_DURING_SCAN", f"$release.{relative}",
                   "release owner artifact changed after repository scan")
        return decode_strict_json_bytes(data, owner), digest

    local, local_manifest_sha256 = read_fixed_json(
        "release-local.json", "local release manifest")
    local_top = {"schema", "records"}
    _object(local, "$release.local", exact_keys=local_top, required=local_top)
    if local["schema"] != "implementaudit-local-release-v1":
        _error("OE_RELEASE_LOCAL_INVALID", "$release.local.schema",
               "unsupported local release schema")
    if type(local["records"]) is not list:
        _error("OE_RELEASE_LOCAL_INVALID", "$release.local.records",
               "must be an array")

    nodes = [
        {
            "id": "git-commit", "record_type": "Commit", "layer": "LOCAL",
            "family": "RELEASE", "object_identity": repository["commit"],
            "source_identity": "git:HEAD",
            "native_owner_identity": "git:repository",
            "currentness": {"state": "CURRENT", "invalidators": []},
            "authority_ceiling": "READ_ONLY_NATIVE_OBSERVATION",
        },
        {
            "id": "git-tree", "record_type": "Tree", "layer": "LOCAL",
            "family": "RELEASE", "object_identity": repository["tree"],
            "source_identity": "git:HEAD^{tree}",
            "native_owner_identity": "git:repository",
            "currentness": {"state": "CURRENT", "invalidators": []},
            "authority_ceiling": "READ_ONLY_NATIVE_OBSERVATION",
        },
        {
            "id": "git-worktree", "record_type": "Worktree",
            "layer": "LOCAL", "family": "RELEASE",
            "object_identity": repository["worktree_state"],
            "source_identity": "git:status--porcelain-v1",
            "native_owner_identity": "git:repository",
            "currentness": {"state": "CURRENT", "invalidators": []},
            "authority_ceiling": "READ_ONLY_NATIVE_OBSERVATION",
        },
    ]
    seen_ids = {row["id"] for row in nodes}
    local_keys = {
        "id", "record_type", "path", "sha256", "source_identity",
        "native_owner_identity", "currentness"}
    for index, source_record in enumerate(local["records"]):
        path = f"$release.local.records[{index}]"
        record = _object(
            source_record, path, exact_keys=local_keys, required=local_keys)
        record_id = _text(record["id"], f"{path}.id")
        if record_id in seen_ids:
            _error("OE_RELEASE_LOCAL_INVALID", f"{path}.id",
                   "release node id must be unique")
        if record["record_type"] not in (
                "GeneratedArtifact", "Package", "Install", "Host"):
            _error("OE_RELEASE_LOCAL_INVALID", f"{path}.record_type",
                   "unsupported local RELEASE record type")
        relative = _safe_relative_path(record["path"], f"{path}.path").as_posix()
        _digest(record["sha256"], f"{path}.sha256")
        _text(record["source_identity"], f"{path}.source_identity")
        _text(
            record["native_owner_identity"],
            f"{path}.native_owner_identity")
        _currentness(record["currentness"], f"{path}.currentness")
        observed = file_facts.get(relative)
        if observed is None or observed.get("sha256") != record["sha256"]:
            _error("OE_RELEASE_LOCAL_DIGEST", f"{path}.sha256",
                   "local release fact does not match working-tree bytes")
        nodes.append({
            **record, "layer": "LOCAL", "family": "RELEASE",
            "authority_ceiling": "READ_ONLY_NATIVE_OBSERVATION",
            "manifest_sha256": local_manifest_sha256,
        })
        seen_ids.add(record_id)

    capture, capture_sha256 = read_fixed_json(
        "external-capture.json", "external release capture")
    capture_keys = {
        "schema", "capture_identity", "source_identity", "auth_state",
        "rate", "pagination", "object_drift", "captured_at", "expires_at",
        "evaluated_at", "records"}
    _object(
        capture, "$release.external", exact_keys=capture_keys,
        required=capture_keys)
    if capture["schema"] != "implementaudit-external-release-capture-v1":
        _error("OE_EXTERNAL_CAPTURE_INVALID", "$release.external.schema",
               "unsupported external capture schema")
    capture_identity = _text(
        capture["capture_identity"], "$release.external.capture_identity")
    external_source = _text(
        capture["source_identity"], "$release.external.source_identity")
    auth_state = capture["auth_state"]
    if auth_state not in ("PRESENT", "ABSENT", "UNKNOWN"):
        _error("OE_EXTERNAL_CAPTURE_INVALID", "$release.external.auth_state",
               "unsupported external auth state")
    rate = _object(
        capture["rate"], "$release.external.rate",
        exact_keys={"state", "remaining", "reset_at"},
        required={"state", "remaining", "reset_at"})
    if rate["state"] not in ("AVAILABLE", "EXHAUSTED", "UNKNOWN"):
        _error("OE_EXTERNAL_CAPTURE_INVALID", "$release.external.rate.state",
               "unsupported external rate state")
    if type(rate["remaining"]) is not int or rate["remaining"] < 0:
        _error("OE_EXTERNAL_CAPTURE_INVALID",
               "$release.external.rate.remaining",
               "rate remaining must be a non-negative integer")
    _utc_timestamp(rate["reset_at"], "$release.external.rate.reset_at")
    pagination = _object(
        capture["pagination"], "$release.external.pagination",
        exact_keys={"state", "pages"}, required={"state", "pages"})
    if pagination["state"] not in ("COMPLETE", "INCOMPLETE", "UNKNOWN"):
        _error("OE_EXTERNAL_CAPTURE_INVALID",
               "$release.external.pagination.state",
               "unsupported pagination state")
    if type(pagination["pages"]) is not int or pagination["pages"] < 1:
        _error("OE_EXTERNAL_CAPTURE_INVALID",
               "$release.external.pagination.pages",
               "pagination pages must be a positive integer")
    object_drift = _boolean(
        capture["object_drift"], "$release.external.object_drift")
    captured_at = _utc_timestamp(
        capture["captured_at"], "$release.external.captured_at")
    expires_at = _utc_timestamp(
        capture["expires_at"], "$release.external.expires_at")
    evaluated_at = _utc_timestamp(
        capture["evaluated_at"], "$release.external.evaluated_at")
    _validate_capture_chronology(
        captured_at, expires_at, evaluated_at, "$release.external")
    boundary_currentness = _external_boundary_currentness(
        auth_state, rate["state"], pagination["state"], object_drift,
        expires_at, evaluated_at)
    if type(capture["records"]) is not list:
        _error("OE_EXTERNAL_CAPTURE_INVALID", "$release.external.records",
               "must be an array")
    external_keys = {
        "id", "record_type", "stable_id", "commit_identity",
        "source_identity", "native_owner_identity", "updated_at", "etag",
        "payload_sha256", "currentness"}
    external_types = {
        "PullRequest", "Check", "Merge", "Tag", "Release", "Asset",
        "PublicSurface"}
    for index, source_record in enumerate(capture["records"]):
        path = f"$release.external.records[{index}]"
        record = _object(
            source_record, path, exact_keys=external_keys,
            required=external_keys)
        record_id = _text(record["id"], f"{path}.id")
        if record_id in seen_ids:
            _error("OE_EXTERNAL_CAPTURE_INVALID", f"{path}.id",
                   "release node id must be unique")
        if record["record_type"] not in external_types:
            _error("OE_EXTERNAL_CAPTURE_INVALID", f"{path}.record_type",
                   "unsupported external RELEASE record type")
        _text(record["stable_id"], f"{path}.stable_id")
        _git_object(record["commit_identity"], f"{path}.commit_identity")
        for key in ("source_identity", "native_owner_identity", "etag"):
            _text(record[key], f"{path}.{key}")
        _utc_timestamp(record["updated_at"], f"{path}.updated_at")
        _digest(record["payload_sha256"], f"{path}.payload_sha256")
        _currentness(record["currentness"], f"{path}.currentness")
        native_currentness = {
            "state": record["currentness"]["state"],
            "invalidators": list(record["currentness"]["invalidators"]),
        }
        capture_currentness = {
            "state": boundary_currentness["state"],
            "invalidators": list(boundary_currentness["invalidators"]),
        }
        currentness = _compose_currentness(
            native_currentness, capture_currentness)
        nodes.append({
            **record,
            "native_currentness": native_currentness,
            "capture_currentness": capture_currentness,
            "currentness": currentness, "layer": "EXTERNAL",
            "family": "RELEASE",
            "authority_ceiling": "READ_ONLY_NATIVE_OBSERVATION",
            "capture_identity": capture_identity,
            "capture_sha256": capture_sha256,
        })
        seen_ids.add(record_id)

    public_nodes = [
        row for row in nodes if row["record_type"] == "PublicSurface"]
    candidate_invalidators = list(boundary_currentness["invalidators"])
    for external_node in (
            row for row in nodes if row["layer"] == "EXTERNAL"):
        for invalidator in external_node["currentness"]["invalidators"]:
            if invalidator not in candidate_invalidators:
                candidate_invalidators.append(invalidator)
    required_types = {
        "Commit", "Tree", "Worktree", "GeneratedArtifact", "Package",
        "Install", "Host", "PullRequest", "Check", "Merge", "Tag",
        "Release", "Asset", "PublicSurface"}
    observed_types = {row["record_type"] for row in nodes}
    missing_types = sorted(required_types - observed_types)
    candidate_invalidators.extend(
        f"MISSING_RELEASE_LAYER:{record_type}"
        for record_type in missing_types)
    public_commit = None
    if len(public_nodes) != 1:
        candidate_invalidators.append("PUBLIC_IDENTITY_NOT_EXACTLY_ONE")
    else:
        public_commit = public_nodes[0]["commit_identity"]
        if public_commit != repository["commit"]:
            candidate_invalidators.append(
                "PUBLIC_PREDECESSOR_DIFFERS_FROM_LOCAL_COMMIT")
    if repository["worktree_state"] != "CLEAN":
        candidate_invalidators.append("LOCAL_WORKTREE_DIRTY")
    if not candidate_invalidators:
        candidate_invalidators.append("NATIVE_CANDIDATE_QUALIFICATION_REQUIRED")

    type_census = Counter(row["record_type"] for row in nodes)
    nodes.sort(key=lambda row: (row["layer"], row["record_type"], row["id"]))
    result = {
        "schema": RELEASE_COLLECTION_SCHEMA,
        "families": ["RELEASE"],
        "repository": {
            "commit": repository["commit"], "tree": repository["tree"],
            "worktree_state": repository["worktree_state"],
        },
        "local_manifest_sha256": local_manifest_sha256,
        "external_capture_sha256": capture_sha256,
        "external_boundary": {
            "capture_identity": capture_identity,
            "source_identity": external_source,
            "auth_state": auth_state,
            "rate_state": rate["state"],
            "rate_remaining": rate["remaining"],
            "pagination_state": pagination["state"],
            "pagination_pages": pagination["pages"],
            "object_drift": object_drift,
            "captured_at": captured_at, "expires_at": expires_at,
            "evaluated_at": evaluated_at,
        },
        "omissions": [
            {
                "record_type": record_type,
                "state": "UNKNOWN",
                "invalidator": f"MISSING_RELEASE_LAYER:{record_type}",
            }
            for record_type in missing_types
        ],
        "node_type_census": {
            key: type_census[key] for key in sorted(required_types)},
        "nodes": nodes,
        "candidate": {
            "state": "UNVERIFIED",
            "invalidators": candidate_invalidators,
            "local_commit": repository["commit"],
            "public_commit": public_commit,
        },
        "establishes": [],
    }
    result["semantic_sha256"] = hashlib.sha256(
        canonical_json_v1(result)).hexdigest()
    immutable_result = decode_strict_json_bytes(
        canonical_json_v1(result), "release collection")
    repository_after = collect_repository(root)
    if repository_after != repository_before:
        _error("OE_RELEASE_CHANGED_DURING_SCAN", "$release",
               "repository changed during RELEASE collection")
    return immutable_result


def _snapshot_stage_v1(stage: str) -> None:
    """Internal fault boundary; tests may replace this no-op, callers may not."""
    del stage


def _snapshot_is_link_v1(path: pathlib.Path) -> bool:
    try:
        metadata = os.lstat(path)
    except OSError:
        return False
    return (stat.S_ISLNK(metadata.st_mode) or
            bool(getattr(metadata, "st_file_attributes", 0) &
                 getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)))


def _snapshot_read_regular_v1(
        path: pathlib.Path, root: pathlib.Path, code: str,
        *, maximum: int = 16 * 1024 * 1024) -> bytes:
    try:
        root_absolute = pathlib.Path(os.path.abspath(root))
        path_absolute = pathlib.Path(os.path.abspath(path))
        relative = path_absolute.relative_to(root_absolute)
        cursor = root_absolute
        if _snapshot_is_link_v1(cursor) or not cursor.is_dir():
            _error(code, "$snapshot", "snapshot custody root is not a physical directory")
        for component in relative.parts:
            if component in {"", ".", ".."}:
                _error(code, "$snapshot", "snapshot path is not canonical")
            cursor = cursor / component
            if _snapshot_is_link_v1(cursor):
                _error(code, "$snapshot", "snapshot path crosses a link or reparse point")
        metadata = os.lstat(path_absolute)
        if (not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1 or
                metadata.st_size > maximum):
            _error(code, "$snapshot", "snapshot member is not one bounded physical file")
        raw = path_absolute.read_bytes()
        if len(raw) != metadata.st_size:
            _error(code, "$snapshot", "snapshot member changed during read")
        return raw
    except OperationalEvidenceError:
        raise
    except (OSError, ValueError):
        _error(code, "$snapshot", "snapshot member is unreadable or outside custody")


def _snapshot_decode_canonical_object_v1(raw: bytes, code: str) -> dict:
    value = decode_strict_json_bytes(raw, "operational snapshot")
    if type(value) is not dict or canonical_json_v1(value) != raw:
        _error(code, "$snapshot", "snapshot JSON is not one exact canonical object")
    return value


def _snapshot_write_new_file_v1(path: pathlib.Path, raw: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError:
        _error("OE_SNAPSHOT_WRITE_FAILED", "$snapshot",
               "immutable snapshot member could not be durably created")


def _snapshot_portable_native_v1(native: dict) -> dict:
    """Remove volatile checkout spelling while retaining owner-native identity."""
    repository_root = pathlib.Path(native["repository"]["root"])
    common_root = pathlib.Path(native["repository"]["git_common_dir"])
    run_relative = pathlib.PurePosixPath(native["claim"]["run_root"])
    run_root = repository_root.joinpath(*run_relative.parts)

    def spellings(path):
        return {str(path), os.fspath(path), path.as_posix(),
                str(path.resolve()), path.resolve().as_posix()}

    replacements = {}
    for spelling in spellings(repository_root):
        replacements[spelling] = "$REPOSITORY_ROOT"
    for spelling in spellings(common_root):
        replacements[spelling] = "$GIT_COMMON_DIR"
    for spelling in spellings(run_root):
        replacements[spelling] = "$RUN_ROOT"

    def replace(value):
        if type(value) is dict:
            return {key: replace(item) for key, item in value.items()
                    if key != "semantic_sha256"}
        if type(value) is list:
            return [replace(item) for item in value]
        if type(value) is str:
            return replacements.get(value, value)
        return value

    result = replace(native)
    result["semantic_sha256"] = hashlib.sha256(
        canonical_json_v1(result)).hexdigest()
    return result


def _snapshot_optional_collection_v1(owner: str, action) -> dict:
    try:
        value = action()
    except OperationalEvidenceError as exc:
        if exc.code not in {"OE_RUN_ARTIFACT_MISSING", "OE_RELEASE_ARTIFACT_MISSING"}:
            raise
        value = {"code": exc.code, "path": exc.path}
        return {
            "owner": owner, "state": "UNKNOWN", "value": value,
            "sha256": hashlib.sha256(canonical_json_v1(value)).hexdigest()}
    return {
        "owner": owner, "state": "CURRENT", "value": value,
        "sha256": hashlib.sha256(canonical_json_v1(value)).hexdigest()}


def _collect_snapshot_inputs_v1(native: dict) -> dict:
    repository_root = pathlib.Path(native["repository"]["root"])
    run_relative = pathlib.PurePosixPath(native["claim"]["run_root"])
    run_root = repository_root.joinpath(*run_relative.parts)
    repository = collect_repository(repository_root)
    collections = {
        "native_current": {
            "owner": "R0038-C03", "state": "CURRENT",
            "value": _snapshot_portable_native_v1(native)},
        "repository": {
            "owner": "R0038-C02", "state": "CURRENT", "value": repository},
        "evidence_failure": _snapshot_optional_collection_v1(
            "R0038-C04", lambda: collect_evidence_failure(run_root)),
        "release": _snapshot_optional_collection_v1(
            "R0038-C05", lambda: collect_release(repository_root)),
    }
    for row in collections.values():
        row.setdefault(
            "sha256", hashlib.sha256(canonical_json_v1(row["value"])).hexdigest())
    return collections


def _snapshot_missing_census_v1(collections: dict) -> list[dict]:
    missing = []
    for name in sorted(collections):
        row = collections[name]
        if row["state"] != "CURRENT":
            missing.append({
                "kind": "COLLECTOR_NON_CURRENT", "collector": name,
                "owner": row["owner"], "state": row["state"],
                "code": row["value"].get("code")})
    repository = collections["repository"]["value"]
    for bucket in ("errors", "unknown"):
        for value in repository.get("diagnostics", {}).get(bucket, []):
            missing.append({
                "kind": "REPOSITORY_DIAGNOSTIC", "collector": "repository",
                "owner": collections["repository"]["owner"],
                "state": "UNKNOWN", "code": f"{bucket}:{value}"})

    evidence_failure = collections["evidence_failure"]
    if evidence_failure["state"] == "CURRENT":
        for bucket in ("evidence_records", "failure_records"):
            for record in evidence_failure["value"].get(bucket, []):
                currentness = record["currentness"]
                if currentness["state"] == "CURRENT":
                    continue
                missing.append({
                    "kind": "OWNER_FACT_NON_CURRENT",
                    "collector": "evidence_failure",
                    "owner": evidence_failure["owner"],
                    "family": record["family"],
                    "fact_path": f"{bucket}/{record['id']}",
                    "record_id": record["id"],
                    "record_type": record["record_type"],
                    "native_owner_identity": record["native_owner_identity"],
                    "state": currentness["state"],
                    "invalidators": list(currentness["invalidators"]),
                })

    release = collections["release"]
    if release["state"] == "CURRENT":
        for record in release["value"].get("nodes", []):
            currentness = record["currentness"]
            if currentness["state"] == "CURRENT":
                continue
            missing.append({
                "kind": "OWNER_FACT_NON_CURRENT",
                "collector": "release",
                "owner": release["owner"],
                "family": record["family"],
                "layer": record["layer"],
                "fact_path": f"nodes/{record['id']}",
                "record_id": record["id"],
                "record_type": record["record_type"],
                "native_owner_identity": record["native_owner_identity"],
                "state": currentness["state"],
                "invalidators": list(currentness["invalidators"]),
            })
        for value in release["value"].get("candidate", {}).get("invalidators", []):
            missing.append({
                "kind": "RELEASE_INVALIDATOR", "collector": "release",
                "owner": release["owner"],
                "state": release["value"]["candidate"].get("state", "UNVERIFIED"),
                "code": value})
    return sorted(missing, key=canonical_json_v1)


def _build_snapshot_material_v1(
        native: dict, collections: dict, schema_raw: bytes,
        compiler_raw: bytes) -> dict:
    missing = _snapshot_missing_census_v1(collections)
    aggregate = "DEGRADED" if missing else "COMPLETE"
    portable_native = collections["native_current"]["value"]
    input_manifest = {
        "schema_version": SNAPSHOT_INPUT_SCHEMA,
        "compiler_sha256": hashlib.sha256(compiler_raw).hexdigest(),
        "schema_sha256": hashlib.sha256(schema_raw).hexdigest(),
        "current_tuple": {
            "controller_id": native["controller"]["id"],
            "claim_id": native["claim"]["id"],
            "run_id": native["claim"]["run_id"],
            "source_epoch": native["continuity"]["source_epoch"],
            "source_pointer_oid": native["continuity"]["pointer_oid"],
            "hot_state_sha256": native["hot"]["state_sha256"],
            "hot_roadmap_sha256": native["hot"]["roadmap_sha256"],
            "work_graph_sha256": native["hot"]["work_graph_sha256"],
            "route_identity": native["route"]["record_identity"],
        },
        "collector_inputs": [
            {"name": name, "owner": row["owner"], "state": row["state"],
             "sha256": row["sha256"]}
            for name, row in sorted(collections.items())],
        "native_semantic_sha256": portable_native["semantic_sha256"],
        "missing_or_omitted_state": missing,
    }
    input_raw = canonical_json_v1(input_manifest)
    snapshot_digest = hashlib.sha256(input_raw).hexdigest()
    snapshot_id = "iasnap-v1-" + snapshot_digest
    payload = {
        "schema_version": SNAPSHOT_PAYLOAD_SCHEMA,
        "snapshot_id": snapshot_id, "aggregate": aggregate,
        "families": list(FAMILIES),
        "missing_or_omitted_state": missing,
        "collections": {name: row for name, row in sorted(collections.items())},
        "input_manifest_sha256": snapshot_digest,
    }
    payload_raw = canonical_json_v1(payload)
    root_identity = "sha256:" + hashlib.sha256(canonical_json_v1({
        "controller_id": native["controller"]["id"],
        "claim_id": native["claim"]["id"],
        "run_id": native["claim"]["run_id"],
    })).hexdigest()
    evidence_id = (
        "iasrc-v1-r0038-snapshot-" + snapshot_digest + "-operational-evidence")
    entry = {
        "source_evidence_id": evidence_id,
        "sha256": hashlib.sha256(payload_raw).hexdigest(),
        "kind": "run-root-relative", "root_identity": root_identity,
        "host_identity": None, "input_path_flavor": "posix",
        "source_locator": {
            "kind": "run-root-relative", "root_identity": root_identity,
            "path": (
                f"operational-evidence/snapshots/{snapshot_id}/snapshot.json"),
            "host_identity": None,
        },
    }
    manifest = {
        "schema_version": SNAPSHOT_MANIFEST_SCHEMA,
        "controller_id": native["controller"]["id"],
        "claim_id": native["claim"]["id"],
        "run_id": native["claim"]["run_id"],
        "source_epoch": native["continuity"]["source_epoch"],
        "source_pointer_oid": native["continuity"]["pointer_oid"],
        "source_evidence_entries": [entry],
    }
    manifest_raw = canonical_json_v1(manifest)
    current = {
        "schema_version": SNAPSHOT_CURRENT_SCHEMA,
        "snapshot_id": snapshot_id,
        "manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "source_pointer_oid": native["continuity"]["pointer_oid"],
    }
    return {
        "snapshot_id": snapshot_id, "aggregate": aggregate,
        "evidence_id": evidence_id, "input_raw": input_raw,
        "payload_raw": payload_raw, "manifest_raw": manifest_raw,
        "current_raw": canonical_json_v1(current),
    }


def _snapshot_validate_owner_entry_v1(entry: object, snapshot_digest: str) -> None:
    if (type(entry) is not dict or set(entry) != SNAPSHOT_OWNER_ENTRY_KEYS or
            type(entry.get("source_evidence_id")) is not str or
            type(entry.get("sha256")) is not str or
            not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) or
            entry.get("kind") != "run-root-relative" or
            type(entry.get("root_identity")) is not str or
            not re.fullmatch(r"sha256:[0-9a-f]{64}", entry["root_identity"]) or
            entry.get("host_identity") is not None or
            entry.get("input_path_flavor") != "posix"):
        _error("OE_SNAPSHOT_MANIFEST_INVALID", "$snapshot.manifest",
               "source-evidence entry is malformed")
    match = SNAPSHOT_EVIDENCE_ID_RE.fullmatch(entry["source_evidence_id"])
    locator = entry.get("source_locator")
    if (match is None or match.group(1) != snapshot_digest or
            type(locator) is not dict or set(locator) != {
                "kind", "root_identity", "path", "host_identity"} or
            locator.get("kind") != entry["kind"] or
            locator.get("root_identity") != entry["root_identity"] or
            locator.get("host_identity") is not None or
            locator.get("path") != (
                f"operational-evidence/snapshots/iasnap-v1-{snapshot_digest}/"
                "snapshot.json")):
        _error("OE_SNAPSHOT_MANIFEST_INVALID", "$snapshot.manifest",
               "source-evidence entry does not bind this snapshot")


def _snapshot_validate_manifest_v1(raw: bytes, snapshot_id: str) -> dict:
    value = _snapshot_decode_canonical_object_v1(
        raw, "OE_SNAPSHOT_MANIFEST_INVALID")
    if (set(value) != SNAPSHOT_MANIFEST_KEYS or
            value.get("schema_version") != SNAPSHOT_MANIFEST_SCHEMA or
            not SNAPSHOT_ID_RE.fullmatch(snapshot_id) or
            type(value.get("controller_id")) is not str or
            not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", value["controller_id"]) or
            type(value.get("claim_id")) is not str or
            not re.fullmatch(r"[0-9a-f]{32}", value["claim_id"]) or
            type(value.get("run_id")) is not str or
            not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", value["run_id"]) or
            type(value.get("source_epoch")) is not str or
            not re.fullmatch(r"G[0-9]{4}", value["source_epoch"]) or
            type(value.get("source_pointer_oid")) is not str or
            not re.fullmatch(
                r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value["source_pointer_oid"]) or
            type(value.get("source_evidence_entries")) is not list or
            not value["source_evidence_entries"]):
        _error("OE_SNAPSHOT_MANIFEST_INVALID", "$snapshot.manifest",
               "snapshot owner manifest has the wrong schema or key set")
    identities = set()
    digest = snapshot_id.removeprefix("iasnap-v1-")
    for entry in value["source_evidence_entries"]:
        _snapshot_validate_owner_entry_v1(entry, digest)
        identity = entry["source_evidence_id"]
        if identity in identities:
            _error("OE_SNAPSHOT_MANIFEST_INVALID", "$snapshot.manifest",
                   "source-evidence identities must be unique")
        identities.add(identity)
    return value


def _snapshot_validate_current_v1(
        raw: bytes, snapshots: pathlib.Path) -> dict:
    value = _snapshot_decode_canonical_object_v1(
        raw, "OE_SNAPSHOT_CURRENT_INVALID")
    if (set(value) != SNAPSHOT_CURRENT_KEYS or
            value.get("schema_version") != SNAPSHOT_CURRENT_SCHEMA or
            type(value.get("snapshot_id")) is not str or
            not SNAPSHOT_ID_RE.fullmatch(value["snapshot_id"]) or
            type(value.get("manifest_sha256")) is not str or
            not re.fullmatch(r"[0-9a-f]{64}", value["manifest_sha256"]) or
            type(value.get("source_pointer_oid")) is not str or
            not re.fullmatch(
                r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value["source_pointer_oid"])):
        _error("OE_SNAPSHOT_CURRENT_INVALID", "$snapshot.CURRENT",
               "CURRENT has the wrong schema, key set, or identity")
    manifest_path = snapshots / value["snapshot_id"] / "manifest.json"
    manifest_raw = _snapshot_read_regular_v1(
        manifest_path, snapshots, "OE_SNAPSHOT_CURRENT_INVALID")
    if hashlib.sha256(manifest_raw).hexdigest() != value["manifest_sha256"]:
        _error("OE_SNAPSHOT_CURRENT_INVALID", "$snapshot.CURRENT",
               "CURRENT does not bind its immutable manifest")
    manifest = _snapshot_validate_manifest_v1(manifest_raw, value["snapshot_id"])
    if manifest["source_pointer_oid"] != value["source_pointer_oid"]:
        _error("OE_SNAPSHOT_CURRENT_INVALID", "$snapshot.CURRENT",
               "CURRENT and manifest pointer identities disagree")
    run_root = snapshots.parents[1]
    for entry in manifest["source_evidence_entries"]:
        relative = pathlib.PurePosixPath(entry["source_locator"]["path"])
        source_path = run_root.joinpath(*relative.parts)
        source_raw = _snapshot_read_regular_v1(
            source_path, run_root, "OE_SNAPSHOT_CURRENT_INVALID")
        if hashlib.sha256(source_raw).hexdigest() != entry["sha256"]:
            _error("OE_SNAPSHOT_CURRENT_INVALID", "$snapshot.CURRENT",
                   "CURRENT-selected source evidence does not match its digest")
    return value


def _snapshot_current_raw_v1(snapshots: pathlib.Path) -> bytes | None:
    current = snapshots / "CURRENT"
    if not current.exists() and not current.is_symlink():
        return None
    raw = _snapshot_read_regular_v1(
        current, snapshots, "OE_SNAPSHOT_CURRENT_INVALID", maximum=64 * 1024)
    _snapshot_validate_current_v1(raw, snapshots)
    return raw


def _snapshot_verify_materialization_v1(
        snapshot_dir: pathlib.Path, expected: dict[str, bytes],
        snapshot_id: str) -> None:
    try:
        if (_snapshot_is_link_v1(snapshot_dir) or not snapshot_dir.is_dir() or
                {path.name for path in snapshot_dir.iterdir()} != set(expected)):
            _error("OE_SNAPSHOT_IMMUTABLE_MISMATCH", "$snapshot",
                   "immutable snapshot population differs from the candidate")
    except OSError:
        _error("OE_SNAPSHOT_IMMUTABLE_MISMATCH", "$snapshot",
               "immutable snapshot population cannot be enumerated")
    for name, raw in expected.items():
        if _snapshot_read_regular_v1(
                snapshot_dir / name, snapshot_dir,
                "OE_SNAPSHOT_IMMUTABLE_MISMATCH") != raw:
            _error("OE_SNAPSHOT_IMMUTABLE_MISMATCH", "$snapshot",
                   "immutable snapshot bytes differ from the candidate")
    _snapshot_validate_manifest_v1(expected["manifest.json"], snapshot_id)


def _snapshot_cleanup_pending_v1(path: pathlib.Path | None) -> None:
    if path is None or not path.exists():
        return
    try:
        members = {member.name: member for member in path.iterdir()}
        if set(members) - {"input-manifest.json", "snapshot.json", "manifest.json"}:
            _error("OE_SNAPSHOT_CLEANUP_REFUSED", "$snapshot.pending",
                   "pending directory contains non-task-owned residue")
        for member in members.values():
            if _snapshot_is_link_v1(member) or not member.is_file():
                _error("OE_SNAPSHOT_CLEANUP_REFUSED", "$snapshot.pending",
                       "pending directory contains a non-file member")
            member.unlink()
        path.rmdir()
    except OperationalEvidenceError:
        raise
    except OSError:
        _error("OE_SNAPSHOT_CLEANUP_REFUSED", "$snapshot.pending",
               "pending task-owned snapshot residue needs reconciliation")


def _snapshot_require_input_fence_v1(
        compiler_path: pathlib.Path, schema_path: pathlib.Path,
        snapshots: pathlib.Path, compiler_raw: bytes, schema_raw: bytes,
        native: dict, collections: dict, before_current: bytes | None) -> None:
    final_compiler = _native_file(
        compiler_path, "$snapshot.final_compiler", 2 * 1024 * 1024)
    final_schema = _native_file(
        schema_path, "$snapshot.final_schema", 512 * 1024)
    final_native = collect_native_current()
    final_collections = _collect_snapshot_inputs_v1(final_native)
    if (compiler_raw != final_compiler or schema_raw != final_schema or
            canonical_json_v1(_snapshot_portable_native_v1(native)) !=
            canonical_json_v1(_snapshot_portable_native_v1(final_native)) or
            canonical_json_v1(collections) != canonical_json_v1(final_collections)):
        _error("OE_SNAPSHOT_INPUT_CHANGED", "$snapshot.input_fence",
               "a compiler, schema, native, route, graph, or collector input drifted")
    final_current = (_snapshot_current_raw_v1(snapshots)
                     if snapshots.exists() else None)
    if final_current != before_current:
        _error("OE_SNAPSHOT_CURRENT_CHANGED", "$snapshot.CURRENT",
               "CURRENT changed during the complete input fence")


def publish_current_snapshot():
    """Compile and atomically select one native-custody R0038 snapshot."""
    source_repository = pathlib.Path(__file__).resolve().parents[3]
    common = _native_resolved_path(
        _run_git(source_repository, "rev-parse", "--path-format=absolute",
                 "--git-common-dir").stdout.strip(), "$snapshot.git_common_dir")
    lock = common / "implementaudit-r0038-snapshot-writer.lock"
    pending = None
    current_temp = None
    lock_held = False
    selection_replaced = False
    try:
        try:
            lock.mkdir()
            lock_held = True
        except OSError:
            _error("OE_SNAPSHOT_WRITER_BUSY", "$snapshot.writer",
                   "the single R0038 output-root writer is already held")
        _snapshot_stage_v1("writer-held")

        compiler_path = pathlib.Path(__file__).resolve()
        schema_path = compiler_path.parent.parent / "references" / (
            "operational-evidence-schema.json")
        compiler_raw = _native_file(compiler_path, "$snapshot.compiler", 2 * 1024 * 1024)
        schema_raw = _native_file(schema_path, "$snapshot.schema", 512 * 1024)
        schema_value = decode_strict_json_bytes(schema_raw, "snapshot schema")
        if schema_value.get("x-immutable-snapshot-publication", {}).get(
                "schema") != SNAPSHOT_MANIFEST_SCHEMA:
            _error("OE_SNAPSHOT_SCHEMA_INVALID", "$snapshot.schema",
                   "schema does not admit the immutable snapshot contract")

        native = collect_native_current()
        repository_root = pathlib.Path(native["repository"]["root"])
        run_relative = pathlib.PurePosixPath(native["claim"]["run_root"])
        run_root = repository_root.joinpath(*run_relative.parts)
        snapshots = run_root / "operational-evidence" / "snapshots"
        if snapshots.exists() and (_snapshot_is_link_v1(snapshots) or not snapshots.is_dir()):
            _error("OE_SNAPSHOT_OUTPUT_INVALID", "$snapshot.output_root",
                   "snapshot output root is not one physical directory")
        before_current = (_snapshot_current_raw_v1(snapshots)
                          if snapshots.exists() else None)
        collections = _collect_snapshot_inputs_v1(native)
        _snapshot_stage_v1("after-first-observation")

        _snapshot_require_input_fence_v1(
            compiler_path, schema_path, snapshots, compiler_raw, schema_raw,
            native, collections, before_current)

        material = _build_snapshot_material_v1(
            native, collections, schema_raw, compiler_raw)
        if material["aggregate"] == "INVALID":
            _error("OE_SNAPSHOT_INVALID_AGGREGATE", "$snapshot.aggregate",
                   "INVALID input cannot be published")
        _snapshot_stage_v1("before-temp-creation")
        operational_root = run_root / "operational-evidence"
        operational_root.mkdir(exist_ok=True)
        if _snapshot_is_link_v1(operational_root) or not operational_root.is_dir():
            _error("OE_SNAPSHOT_OUTPUT_INVALID", "$snapshot.output_root",
                   "operational-evidence root is not one physical directory")
        snapshots.mkdir(exist_ok=True)
        if _snapshot_is_link_v1(snapshots) or not snapshots.is_dir():
            _error("OE_SNAPSHOT_OUTPUT_INVALID", "$snapshot.output_root",
                   "snapshot output root is not one physical directory")

        expected = {
            "input-manifest.json": material["input_raw"],
            "snapshot.json": material["payload_raw"],
            "manifest.json": material["manifest_raw"],
        }
        snapshot_dir = snapshots / material["snapshot_id"]
        if snapshot_dir.exists() or snapshot_dir.is_symlink():
            _snapshot_verify_materialization_v1(
                snapshot_dir, expected, material["snapshot_id"])
        else:
            pending = pathlib.Path(tempfile.mkdtemp(
                prefix=".pending-r0038-", dir=snapshots))
            _snapshot_stage_v1("after-temp-creation")
            for name in ("input-manifest.json", "snapshot.json", "manifest.json"):
                _snapshot_stage_v1("before-" + name)
                _snapshot_write_new_file_v1(pending / name, expected[name])
                _snapshot_stage_v1("after-" + name)
            _snapshot_verify_materialization_v1(
                pending, expected, material["snapshot_id"])
            _snapshot_stage_v1("after-manifest-reread")
            try:
                pending.rename(snapshot_dir)
            except OSError:
                _error("OE_SNAPSHOT_IMMUTABLE_MISMATCH", "$snapshot",
                       "immutable snapshot identity already has different custody")
            pending = None
            _snapshot_verify_materialization_v1(
                snapshot_dir, expected, material["snapshot_id"])

        if _snapshot_current_raw_v1(snapshots) != before_current:
            _error("OE_SNAPSHOT_CURRENT_CHANGED", "$snapshot.CURRENT",
                   "CURRENT changed immediately before atomic selection")
        _snapshot_stage_v1("before-current-temp")
        descriptor, current_name = tempfile.mkstemp(
            prefix=".CURRENT-r0038-", dir=snapshots)
        current_temp = pathlib.Path(current_name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(material["current_raw"])
                stream.flush()
                os.fsync(stream.fileno())
        except OSError:
            _error("OE_SNAPSHOT_WRITE_FAILED", "$snapshot.CURRENT",
                   "CURRENT temporary sibling could not be durably written")
        _snapshot_stage_v1("after-current-temp")
        if _snapshot_read_regular_v1(
                current_temp, snapshots, "OE_SNAPSHOT_CURRENT_INVALID",
                maximum=64 * 1024) != material["current_raw"]:
            _error("OE_SNAPSHOT_CURRENT_INVALID", "$snapshot.CURRENT",
                   "CURRENT temporary sibling failed exact reread")
        _snapshot_stage_v1("before-current-replace")
        _snapshot_require_input_fence_v1(
            compiler_path, schema_path, snapshots, compiler_raw, schema_raw,
            native, collections, before_current)
        _snapshot_verify_materialization_v1(
            snapshot_dir, expected, material["snapshot_id"])
        if _snapshot_read_regular_v1(
                current_temp, snapshots, "OE_SNAPSHOT_CURRENT_INVALID",
                maximum=64 * 1024) != material["current_raw"]:
            _error("OE_SNAPSHOT_CURRENT_INVALID", "$snapshot.CURRENT",
                   "CURRENT temporary sibling changed before atomic selection")
        try:
            os.replace(current_temp, snapshots / "CURRENT")
            current_temp = None
            selection_replaced = True
        except OSError:
            _error("OE_SNAPSHOT_WRITE_FAILED", "$snapshot.CURRENT",
                   "CURRENT atomic replacement failed")
        try:
            _snapshot_stage_v1("after-current-replace")
        except Exception:
            _error("OE_SNAPSHOT_PUBLICATION_UNKNOWN_EFFECT", "$snapshot.CURRENT",
                   "CURRENT replaced but post-selection completion is unknown")
        readback = _snapshot_current_raw_v1(snapshots)
        if readback != material["current_raw"]:
            _error("OE_SNAPSHOT_PUBLICATION_UNKNOWN_EFFECT", "$snapshot.CURRENT",
                   "post-selection readback did not match the candidate")
        _snapshot_verify_materialization_v1(
            snapshot_dir, expected, material["snapshot_id"])
        return {
            "schema": SNAPSHOT_PUBLICATION_SCHEMA,
            "snapshot_id": material["snapshot_id"],
            "aggregate": material["aggregate"],
            "manifest_sha256": hashlib.sha256(material["manifest_raw"]).hexdigest(),
            "current_sha256": hashlib.sha256(material["current_raw"]).hexdigest(),
            "source_evidence_ids": [material["evidence_id"]],
            "selection_state": (
                "UNCHANGED" if before_current == material["current_raw"] else "ADVANCED"),
            "authority_ceiling": "R0038_OUTPUT_ROOT_ONLY",
            "establishes": [],
        }
    except OperationalEvidenceError:
        raise
    except Exception:
        if selection_replaced:
            _error("OE_SNAPSHOT_PUBLICATION_UNKNOWN_EFFECT", "$snapshot.CURRENT",
                   "publication failed after atomic selection")
        _error("OE_SNAPSHOT_PUBLICATION_FAILED", "$snapshot",
               "snapshot publication failed before atomic selection")
    finally:
        if current_temp is not None:
            try:
                current_temp.unlink(missing_ok=True)
            except OSError:
                pass
        if pending is not None:
            _snapshot_cleanup_pending_v1(pending)
        if lock_held:
            try:
                lock.rmdir()
            except OSError:
                if sys.exc_info()[0] is None:
                    _error("OE_SNAPSHOT_CLEANUP_REFUSED", "$snapshot.writer",
                           "writer lock residue needs manual reconciliation")


def _native_external_get(url, headers):
    """Perform the runner's concrete GET-only network operation."""
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        response = urllib.request.urlopen(request, timeout=30)
    except urllib.error.HTTPError as exc:
        response = exc
    try:
        raw_headers = {}
        seen_headers = set()
        for key, value in response.headers.raw_items():
            normalized = key.lower()
            if normalized in seen_headers:
                _error("OE_EXTERNAL_RESPONSE", "$external.response.headers",
                       "response headers must not collide case-insensitively")
            seen_headers.add(normalized)
            raw_headers[key] = value
        return {
            "status": response.status,
            "headers": raw_headers,
            "body": response.read(),
        }
    finally:
        response.close()


def run_external_readonly(request, transport=None):
    """Run one fixed allowlisted external GET and return a frozen capture."""
    request_keys = {
        "schema", "source", "operation", "path", "auth_state", "page",
        "per_page", "expected_etag", "captured_at", "expires_at",
        "evaluated_at"}
    if type(request) is not dict or set(request) != request_keys:
        _error("OE_EXTERNAL_REQUEST", "$external.request",
               "external request must use the exact read-only request keys")
    if request["schema"] != "implementaudit-external-read-request-v1":
        _error("OE_EXTERNAL_REQUEST", "$external.request.schema",
               "unsupported external request schema")
    if request["source"] != "GITHUB_API":
        _error("OE_EXTERNAL_REQUEST", "$external.request.source",
               "only the fixed GitHub API read source is supported")
    repository_path = r"/repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
    allowlist = {
        "PULL_REQUEST": repository_path + r"/pulls/[1-9]\d*",
        "CHECK_RUNS": (
            repository_path + r"/commits/[0-9a-f]{40}/check-runs"),
        "TAG": repository_path + r"/git/ref/tags/[A-Za-z0-9._-]+",
        "RELEASE": repository_path + r"/releases/tags/[A-Za-z0-9._-]+",
        "ASSET": repository_path + r"/releases/assets/[1-9]\d*",
        "PUBLIC_READBACK": repository_path + r"/contents/[A-Za-z0-9._/-]+",
    }
    pattern = allowlist.get(request["operation"])
    if (pattern is None or re.fullmatch(pattern, request["path"]) is None or
            ".." in pathlib.PurePosixPath(request["path"]).parts):
        _error("OE_EXTERNAL_REQUEST", "$external.request",
               "external request is outside the fixed read-only allowlist")
    auth_state = request["auth_state"]
    if auth_state not in ("PRESENT", "ABSENT", "UNKNOWN"):
        _error("OE_EXTERNAL_REQUEST", "$external.request.auth_state",
               "unsupported external auth state")
    page = request["page"]
    per_page = request["per_page"]
    if (type(page) is not int or page < 1 or type(per_page) is not int or
            per_page < 1 or per_page > 100):
        _error("OE_EXTERNAL_REQUEST", "$external.request",
               "page must be positive and per_page must be 1..100")
    expected_etag = request["expected_etag"]
    if expected_etag is not None:
        _text(expected_etag, "$external.request.expected_etag")
    captured_at = _utc_timestamp(
        request["captured_at"], "$external.request.captured_at")
    expires_at = _utc_timestamp(
        request["expires_at"], "$external.request.expires_at")
    evaluated_at = _utc_timestamp(
        request["evaluated_at"], "$external.request.evaluated_at")
    _validate_capture_chronology(
        captured_at, expires_at, evaluated_at, "$external.request")
    if transport is not None and not callable(transport):
        _error("OE_EXTERNAL_REQUEST", "$external.transport",
               "transport must be callable when supplied")
    url = (
        f"https://api.github.com{request['path']}?page={page}&per_page={per_page}")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        response = (
            _native_external_get(url, headers) if transport is None else
            transport(url, headers))
    except (OSError, TimeoutError):
        _error("OE_EXTERNAL_TRANSPORT", "$external.response",
               "external read transport failed")
    response = _object(
        response, "$external.response",
        exact_keys={"status", "headers", "body"},
        required={"status", "headers", "body"})
    status = response["status"]
    if type(status) is not int or status < 100 or status > 599:
        _error("OE_EXTERNAL_RESPONSE", "$external.response.status",
               "HTTP status must be an integer from 100 through 599")
    raw_headers = _object(response["headers"], "$external.response.headers")
    normalized_headers = {}
    for key, value in raw_headers.items():
        if type(key) is not str or type(value) is not str:
            _error("OE_EXTERNAL_RESPONSE", "$external.response.headers",
                   "response headers must be strings")
        normalized = key.lower()
        if normalized in normalized_headers:
            _error("OE_EXTERNAL_RESPONSE", "$external.response.headers",
                   "response headers must not collide case-insensitively")
        normalized_headers[normalized] = value
    body = response["body"]
    if type(body) is not bytes:
        _error("OE_EXTERNAL_RESPONSE", "$external.response.body",
               "response body must be bytes")
    payload = decode_strict_json_bytes(body, "external response")
    remaining_text = normalized_headers.get("x-ratelimit-remaining")
    try:
        rate_remaining = (
            int(remaining_text) if remaining_text is not None else None)
    except ValueError:
        _error("OE_EXTERNAL_RESPONSE", "$external.response.headers",
               "rate remaining header must be an integer")
    if rate_remaining is not None and rate_remaining < 0:
        _error("OE_EXTERNAL_RESPONSE", "$external.response.headers",
               "rate remaining header must be non-negative")
    rate_state = (
        "EXHAUSTED" if status == 429 or rate_remaining == 0 else
        "AVAILABLE" if rate_remaining is not None else "UNKNOWN")
    link = normalized_headers.get("link", "")
    pagination_state = (
        "INCOMPLETE" if 'rel="next"' in link else "COMPLETE")
    actual_etag = normalized_headers.get("etag")
    object_drift = (
        expected_etag is not None and actual_etag != expected_etag)
    currentness = _external_boundary_currentness(
        auth_state, rate_state, pagination_state, object_drift,
        expires_at, evaluated_at)
    if status < 200 or status >= 300:
        known = set(currentness["invalidators"])
        if status not in (401, 403, 429) or not known:
            currentness = {
                "state": "UNKNOWN",
                "invalidators": [*currentness["invalidators"],
                                 f"HTTP_STATUS_{status}"],
            }
    injected_transport = transport is not None
    if injected_transport:
        currentness = {
            "state": ("UNVERIFIED" if currentness["state"] == "CURRENT" else
                      currentness["state"]),
            "invalidators": [*currentness["invalidators"],
                             "UNTRUSTED_INJECTED_TRANSPORT"],
        }
    result = {
        "schema": EXTERNAL_READ_CAPTURE_SCHEMA,
        "authority_ceiling": "READ_ONLY_EXTERNAL_CAPTURE",
        "establishes": [],
        "boundary": {
            "method": "UNVERIFIED" if injected_transport else "GET",
            "network_used": True,
            "write_verb_exposed": (
                "UNKNOWN" if injected_transport else False),
            "transport_trust": (
                "UNTRUSTED_INJECTED" if injected_transport else
                "NATIVE_FIXED_GET"),
        },
        "request": {
            "source": request["source"], "operation": request["operation"],
            "path": request["path"], "auth_state": auth_state,
            "page": page, "per_page": per_page,
            "expected_etag": expected_etag,
        },
        "response": {
            "status": status, "etag": actual_etag,
            "rate_remaining": rate_remaining, "pagination": pagination_state,
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "body_bytes": len(body),
        },
        "captured_at": captured_at, "expires_at": expires_at,
        "evaluated_at": evaluated_at, "currentness": currentness,
        "payload": payload,
    }
    result["semantic_sha256"] = hashlib.sha256(
        canonical_json_v1(result)).hexdigest()
    return decode_strict_json_bytes(
        canonical_json_v1(result), "external read capture")


def _validate_static_qualification(value, outcome):
    if outcome == "CURRENT":
        _error("OE_STATIC_QUALIFICATION_REQUIRED", "$static.qualification",
               "C02 has no native qualification owner for external CURRENT")
    if value is not None:
        _error("OE_STATIC_QUALIFICATION_UNTRUSTED", "$static.qualification",
               "caller-issued qualification has no authority in C02")
    return None


def _validate_static_receipt(value):
    _object(
        value, "$static", exact_keys={
            "schema", "outcome", "invalidators", "collector", "target", "scope",
            "diagnostics", "facts", "qualification"},
        required={
            "schema", "outcome", "invalidators", "collector", "target", "scope",
            "diagnostics", "facts"})
    if value["schema"] != STATIC_RECEIPT_SCHEMA:
        _error("OE_STATIC_RECEIPT_INVALID", "$static.schema",
               "unsupported static receipt schema")
    outcome = value["outcome"]
    if outcome not in STATIC_OUTCOMES:
        _error("OE_STATIC_RECEIPT_INVALID", "$static.outcome",
               "unsupported static outcome")
    invalidators = _string_list(
        value["invalidators"], "$static.invalidators", unique=False)
    if outcome == "CURRENT" and invalidators:
        _error("OE_STATIC_CURRENTNESS", "$static.invalidators",
               "CURRENT static receipt cannot retain an invalidator")
    if outcome == "STALE" and not invalidators:
        _error("OE_STATIC_CURRENTNESS", "$static.invalidators",
               "STALE static receipt must name an invalidator")
    collector = _object(
        value["collector"], "$static.collector", exact_keys={
            "identity", "version", "package_sha256", "invocation_identity",
            "output_schema_identity", "parser_mode", "configuration_sha256",
            "trust_mode", "executes_target_code", "auto_installs",
            "network_access"}, required={
            "identity", "version", "package_sha256", "invocation_identity",
            "output_schema_identity", "parser_mode", "configuration_sha256",
            "trust_mode", "executes_target_code", "auto_installs",
            "network_access"})
    for key in ("identity", "version", "invocation_identity",
                "output_schema_identity", "parser_mode", "trust_mode"):
        _text(collector[key], f"$static.collector.{key}")
    _digest(collector["package_sha256"], "$static.collector.package_sha256")
    _digest(
        collector["configuration_sha256"],
        "$static.collector.configuration_sha256")
    trust_effects = (
        _boolean(collector["executes_target_code"],
                 "$static.collector.executes_target_code"),
        _boolean(collector["auto_installs"], "$static.collector.auto_installs"),
        _boolean(collector["network_access"], "$static.collector.network_access"),
    )
    if any(trust_effects):
        _error("OE_STATIC_TRUST", "$static.collector",
               "C02 accepts only data-only, offline, pre-installed collectors")

    target = _object(
        value["target"], "$static.target", exact_keys={
            "repository_identity", "snapshot_identity", "commit", "tree",
            "worktree_state", "input_file_set_sha256", "physical_change"},
        required={
            "repository_identity", "snapshot_identity", "commit", "tree",
            "worktree_state", "input_file_set_sha256", "physical_change"})
    _text(target["repository_identity"], "$static.target.repository_identity")
    _text(target["snapshot_identity"], "$static.target.snapshot_identity")
    _git_object(target["commit"], "$static.target.commit")
    _git_object(target["tree"], "$static.target.tree")
    if target["worktree_state"] not in ("CLEAN", "DIRTY"):
        _error("OE_STATIC_RECEIPT_INVALID", "$static.target.worktree_state",
               "unsupported worktree state")
    _digest(
        target["input_file_set_sha256"],
        "$static.target.input_file_set_sha256")
    physical_change = _boolean(
        target["physical_change"], "$static.target.physical_change")
    if physical_change and outcome == "CURRENT":
        _error("OE_STATIC_STALE", "$static.target.physical_change",
               "physical change invalidates a CURRENT static receipt")

    scope_keys = {
        "applicable", "supported", "unsupported", "input_complete",
        "entrypoints_complete", "workspace_complete",
        "extension_resolution_complete", "dynamic_entrypoints_complete",
        "generated_policy_complete", "parser_complete"}
    scope = _object(
        value["scope"], "$static.scope", exact_keys=scope_keys,
        required=scope_keys)
    supported = _string_list(scope["supported"], "$static.scope.supported")
    unsupported = _string_list(
        scope["unsupported"], "$static.scope.unsupported")
    completeness_keys = (
        "applicable", "input_complete", "entrypoints_complete",
        "workspace_complete", "extension_resolution_complete",
        "dynamic_entrypoints_complete", "generated_policy_complete",
        "parser_complete")
    completeness = {
        key: _boolean(scope[key], f"$static.scope.{key}")
        for key in completeness_keys
    }

    diagnostics = _object(
        value["diagnostics"], "$static.diagnostics", exact_keys={
            "warnings", "errors", "skipped", "unknown"}, required={
            "warnings", "errors", "skipped", "unknown"})
    for key in ("warnings", "errors", "skipped", "unknown"):
        _string_list(
            diagnostics[key], f"$static.diagnostics.{key}", unique=False)
    if (outcome == "CURRENT" and
            (diagnostics["errors"] or diagnostics["skipped"] or
             not completeness["parser_complete"] or
             not completeness["applicable"])):
        _error("OE_STATIC_CURRENTNESS", "$static",
               "CURRENT static receipt cannot hide incomplete parser population")

    if type(value["facts"]) is not list:
        _error("OE_STATIC_RECEIPT_INVALID", "$static.facts",
               "must be an array")
    facts = []
    fact_ids = set()
    for index, source_fact in enumerate(value["facts"]):
        path = f"$static.facts[{index}]"
        fact = _object(
            source_fact, path, exact_keys={
                "id", "kind", "polarity", "source", "target", "resolution",
                "state", "work_consequence", "mapping"}, required={
                "id", "kind", "polarity", "source", "target", "resolution",
                "state", "work_consequence", "mapping"})
        _text(fact["id"], f"{path}.id")
        if fact["id"] in fact_ids:
            _error("OE_STATIC_RECEIPT_INVALID", f"{path}.id",
                   "fact id must be unique")
        fact_ids.add(fact["id"])
        if fact["kind"] not in STATIC_FACT_KINDS:
            _error("OE_STATIC_RECEIPT_INVALID", f"{path}.kind",
                   "unsupported static fact kind")
        if fact["polarity"] not in ("POSITIVE", "NEGATIVE"):
            _error("OE_STATIC_RECEIPT_INVALID", f"{path}.polarity",
                   "unsupported fact polarity")
        _text(fact["source"], f"{path}.source")
        _text(fact["target"], f"{path}.target")
        if fact["resolution"] not in (
                "RESOLVED", "UNRESOLVED", "UNSUPPORTED", "PARTIAL"):
            _error("OE_STATIC_RECEIPT_INVALID", f"{path}.resolution",
                   "unsupported resolution")
        if fact["state"] not in STATIC_OUTCOMES:
            _error("OE_STATIC_RECEIPT_INVALID", f"{path}.state",
                   "unsupported fact state")
        if fact["work_consequence"] != "NONE":
            _error("OE_STATIC_AUTHORITY", f"{path}.work_consequence",
                   "source topology cannot create a work-DAG or lifecycle effect")
        mapping = fact["mapping"]
        if mapping is not None:
            _error("OE_STATIC_MAPPING_FORBIDDEN", f"{path}.mapping",
                   "C02 static facts cannot supply governed work-node mappings")
        if fact["kind"] in STATIC_NEGATIVE_KINDS:
            if (fact["polarity"] != "NEGATIVE" or unsupported or
                    not all(completeness.values())):
                _error("OE_STATIC_NEGATIVE_UNQUALIFIED", path,
                       "absence fact requires complete supported scope")
        if fact["kind"] in ("MODULE_EDGE", "REVERSE_DEPENDENT") and (
                fact["polarity"] != "POSITIVE" or
                fact["resolution"] != "RESOLVED"):
            _error("OE_STATIC_RECEIPT_INVALID", path,
                   "positive structural relation must be resolved")
        provenance = {
            "collector_identity": collector["identity"],
            "collector_version": collector["version"],
            "collector_package_sha256": collector["package_sha256"],
            "invocation_identity": collector["invocation_identity"],
            "output_schema_identity": collector["output_schema_identity"],
            "parser_mode": collector["parser_mode"],
            "configuration_sha256": collector["configuration_sha256"],
            "target_snapshot_identity": target["snapshot_identity"],
            "input_file_set_sha256": target["input_file_set_sha256"],
        }
        facts.append({
            **fact,
            "state": (outcome if outcome != "CURRENT" and
                      fact["state"] == "CURRENT" else fact["state"]),
            "native_owner_identity": target["repository_identity"],
            "authority_ceiling": "READ_ONLY_STRUCTURAL_FACT",
            "provenance": provenance,
        })

    synthetic = {
        "PARSER_ERROR": "PARSER_ERROR_OBSERVATION",
        "UNSUPPORTED": "UNSUPPORTED_OBSERVATION",
        "UNSUPPORTED_LANGUAGE": "UNSUPPORTED_OBSERVATION",
        "NOT_INSTALLED": "TOOL_UNAVAILABLE_OBSERVATION",
        "TOOL_TIMEOUT": "TOOL_FAILURE_OBSERVATION",
        "TOOL_CRASH": "TOOL_FAILURE_OBSERVATION",
        "VERSION_MISMATCH": "TOOL_FAILURE_OBSERVATION",
        "TARGET_CONFIG_UNTRUSTED": "UNSUPPORTED_OBSERVATION",
    }
    if not facts and outcome in synthetic:
        facts.append({
            "id": f"synthetic:{collector['identity']}:{outcome.lower()}",
            "kind": synthetic[outcome], "polarity": "POSITIVE",
            "source": collector["identity"],
            "target": target["snapshot_identity"],
            "resolution": "UNSUPPORTED" if outcome != "PARSER_ERROR" else "PARTIAL",
            "state": outcome, "work_consequence": "NONE", "mapping": None,
            "native_owner_identity": target["repository_identity"],
            "authority_ceiling": "READ_ONLY_STRUCTURAL_FACT",
            "provenance": {
                "collector_identity": collector["identity"],
                "collector_version": collector["version"],
                "collector_package_sha256": collector["package_sha256"],
                "invocation_identity": collector["invocation_identity"],
                "output_schema_identity": collector["output_schema_identity"],
                "parser_mode": collector["parser_mode"],
                "configuration_sha256": collector["configuration_sha256"],
                "target_snapshot_identity": target["snapshot_identity"],
                "input_file_set_sha256": target["input_file_set_sha256"],
            },
        })
    if not facts:
        _error("OE_STATIC_EMPTY", "$static.facts",
               "static receipt must retain a fact or typed degradation")
    qualification = _validate_static_qualification(
        value.get("qualification"), outcome)
    normalized = {
        "schema": STATIC_NORMALIZED_SCHEMA,
        "normalization_identity": "canonical_json_v1",
        "outcome": outcome,
        "invalidators": sorted(invalidators),
        "qualification": {
            "collector": dict(collector), "target": dict(target),
            "scope": {**scope, "supported": list(supported),
                      "unsupported": list(unsupported)},
            "self_probe": qualification,
        },
        "diagnostics": {
            key: sorted(diagnostics[key])
            for key in ("warnings", "errors", "skipped", "unknown")
        },
        "facts": sorted(facts, key=lambda row: canonical_json_v1(row)),
    }
    normalized["semantic_sha256"] = hashlib.sha256(
        canonical_json_v1(normalized)).hexdigest()
    return normalized


def normalize_static_receipt(value):
    """Qualify one external static receipt without executing its collector."""
    if type(value) is not dict:
        _error("OE_STATIC_RECEIPT_INVALID", "$static", "must be an object")
    return _validate_static_receipt(json.loads(
        canonical_json_v1(value).decode("utf-8")))


def normalize_static_receipts(values):
    """Retain distinct provenance and surface opposite edge claims."""
    if type(values) is not list or not values:
        _error("OE_STATIC_RECEIPT_INVALID", "$static_set",
               "must be a non-empty array")
    receipts = [normalize_static_receipt(value) for value in values]
    target_identity = receipts[0]["qualification"]["target"]
    if any(receipt["qualification"]["target"] != target_identity
           for receipt in receipts[1:]):
        _error("OE_STATIC_SET_MISMATCH", "$static_set",
               "collector receipts must bind the same exact target snapshot")
    facts = [fact for receipt in receipts for fact in receipt["facts"]]
    positive_edges = {
        (fact["source"], fact["target"])
        for fact in facts
        if fact["kind"] == "MODULE_EDGE" and fact["polarity"] == "POSITIVE"
    }
    negative_edges = {
        (fact["source"], fact["target"])
        for fact in facts
        if fact["kind"] == "NO_EDGE" and fact["polarity"] == "NEGATIVE"
    }
    contradictions = [
        {"source": source, "target": target}
        for source, target in sorted(positive_edges & negative_edges)
    ]
    if contradictions:
        outcome = "CONTRADICTORY"
    elif len({receipt["outcome"] for receipt in receipts}) == 1:
        outcome = receipts[0]["outcome"]
    else:
        outcome = "PARTIAL"
    result = {
        "schema": STATIC_NORMALIZED_SET_SCHEMA,
        "normalization_identity": "canonical_json_v1", "outcome": outcome,
        "contradictions": contradictions,
        "facts": sorted(facts, key=lambda row: canonical_json_v1(row)),
        "receipt_sha256": sorted(
            receipt["semantic_sha256"] for receipt in receipts),
    }
    result["semantic_sha256"] = hashlib.sha256(
        canonical_json_v1(result)).hexdigest()
    return result


def _snapshot_diff_exact_object_v1(value: object, keys: set[str], path: str) -> dict:
    if type(value) is not dict or set(value) != keys:
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "snapshot member does not match its exact producer schema")
    return value


def _snapshot_diff_text_v1(value: object, path: str) -> str:
    if type(value) is not str or not value:
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "snapshot member text must be non-empty")
    return value


def _snapshot_diff_digest_v1(value: object, path: str) -> str:
    if type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "snapshot member digest must be lowercase SHA-256")
    return value


def _snapshot_diff_unique_string_list_v1(value: object, path: str) -> list[str]:
    index, violation = _string_list_violation_v1(value)
    if violation is not None:
        member_path = path if index is None else f"{path}[{index}]"
        _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
               f"snapshot producer list {violation}")
    return value


def _snapshot_diff_currentness_v1(value: object, path: str) -> None:
    currentness = _snapshot_diff_exact_object_v1(
        value, {"state", "invalidators"}, path)
    state = currentness["state"]
    invalidators = currentness["invalidators"]
    _snapshot_diff_unique_string_list_v1(invalidators, f"{path}.invalidators")
    if (state not in STATES or (state == "CURRENT" and invalidators) or
            (state == "STALE" and not invalidators)):
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "snapshot currentness state and invalidators are inconsistent")


def _snapshot_diff_semantic_v1(value: dict, path: str) -> None:
    digest = _snapshot_diff_digest_v1(
        value.get("semantic_sha256"), f"{path}.semantic_sha256")
    semantic = dict(value)
    semantic.pop("semantic_sha256")
    if hashlib.sha256(canonical_json_v1(semantic)).hexdigest() != digest:
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "snapshot collection semantic digest differs")


def _snapshot_diff_keyset_v1(names: str) -> frozenset[str]:
    return frozenset(names.split())


_SNAPSHOT_DIFF_CLOSED_KEYSETS_V1 = frozenset({
    SNAPSHOT_PAYLOAD_KEYS,
    _snapshot_diff_keyset_v1(
        "native_current repository evidence_failure release"),
    _snapshot_diff_keyset_v1("owner state value sha256"),
    _snapshot_diff_keyset_v1("state invalidators"),
    _snapshot_diff_keyset_v1(
        "schema authority_ceiling establishes repository controller claim "
        "continuity hot frontier andon_state open_andons "
        "active_instructions next_action route semantic_sha256"),
    _snapshot_diff_keyset_v1("root git_common_dir"),
    _snapshot_diff_keyset_v1("id ref record_oid"),
    _snapshot_diff_keyset_v1("id run_id run_root"),
    _snapshot_diff_keyset_v1(
        "generation source_epoch invalidation_ref invalidation_oid "
        "boundary_kind boundary_event_id pointer_ref pointer_oid "
        "pointer_digest receipt_schema receipt_ref receipt_oid receipt "
        "marker_ref marker_oid generation_manifest_oid "
        "generation_manifest_digest cold_high_water degraded_state"),
    _snapshot_diff_keyset_v1(
        "state_path state_sha256 roadmap_path roadmap_sha256 "
        "work_graph_path work_graph_sha256 work_graph_compiler_sha256"),
    _snapshot_diff_keyset_v1(
        "population counts active ready blocked_summary writer_holds "
        "resource_holds digest"),
    _snapshot_diff_keyset_v1("DONE ACTIVE READY BLOCKED"),
    _snapshot_diff_keyset_v1(
        "id reference kind authority subject issued_epoch status "
        "status_evidence supersedes_by scope_end"),
    _snapshot_diff_keyset_v1(
        "controller_id controller_record_oid ref record_oid record_identity "
        "decision classification route_transaction_id obligation_id route_state"),
    _snapshot_diff_keyset_v1(
        "schema repository capabilities diagnostics facts "
        "static_collector_invocations"),
    _snapshot_diff_keyset_v1(
        "commit tree worktree_state input_file_set_sha256"),
    _snapshot_diff_keyset_v1("warnings errors skipped unknown"),
    _snapshot_diff_keyset_v1("capability state reason_code"),
    _snapshot_diff_keyset_v1("capability state reason_code provenance"),
    _snapshot_diff_keyset_v1(
        "collector_identity collector_version collector_package_sha256 "
        "invocation_identity output_schema_identity parser "
        "input_file_set_sha256"),
    _snapshot_diff_keyset_v1(
        "collector input_path input_sha256 collector_identity "
        "collector_version collector_package_sha256 invocation_identity "
        "output_schema_identity parser"),
    _snapshot_diff_keyset_v1(
        "kind path sha256 bytes file_type language state provenance"),
    _snapshot_diff_keyset_v1("kind path state provenance"),
    _snapshot_diff_keyset_v1("kind source target state provenance"),
    _snapshot_diff_keyset_v1(
        "kind path package_name sha256 state provenance"),
    _snapshot_diff_keyset_v1("kind package_name path state provenance"),
    _snapshot_diff_keyset_v1("kind path sha256 state provenance"),
    _snapshot_diff_keyset_v1("method commit tree"),
    _snapshot_diff_keyset_v1(
        "collector_identity collector_version collector_package_sha256 "
        "invocation_identity output_schema_identity parser input_path input_sha256"),
    _snapshot_diff_keyset_v1(
        "collector_identity collector_version collector_package_sha256 "
        "invocation_identity output_schema_identity parser input_path "
        "input_sha256 reason"),
    _snapshot_diff_keyset_v1("parser input_path"),
    _snapshot_diff_keyset_v1("parser input_path input_sha256"),
    _snapshot_diff_keyset_v1("method reason"),
    _snapshot_diff_keyset_v1(
        "schema families source first_red_id first_red_state weakest_leg_id "
        "residual_ids layer_census evidence_records failure_records "
        "establishes semantic_sha256"),
    _snapshot_diff_keyset_v1("path sha256 run_identity artifact_identity"),
    _snapshot_diff_keyset_v1("ATTEMPT RECEIPT EFFECT RECOVERY CLOSURE"),
    _snapshot_diff_keyset_v1(
        "id sequence record_type claim_id criterion_id leg result_class proxy "
        "source_identity native_owner_identity currentness controls "
        "contrary_evidence family authority_ceiling artifact_sha256"),
    _snapshot_diff_keyset_v1(
        "id sequence record_type andon_id abnormality_class statement "
        "cause_confidence evidence_ids recovery_state source_identity "
        "native_owner_identity currentness family authority_ceiling "
        "artifact_sha256"),
    _snapshot_diff_keyset_v1(
        "schema families repository local_manifest_sha256 "
        "external_capture_sha256 external_boundary omissions node_type_census "
        "nodes candidate establishes semantic_sha256"),
    _snapshot_diff_keyset_v1("commit tree worktree_state"),
    _snapshot_diff_keyset_v1(
        "capture_identity source_identity auth_state rate_state rate_remaining "
        "pagination_state pagination_pages object_drift captured_at expires_at "
        "evaluated_at"),
    _snapshot_diff_keyset_v1("record_type state invalidator"),
    _snapshot_diff_keyset_v1(
        "Commit Tree Worktree GeneratedArtifact Package Install Host "
        "PullRequest Check Merge Tag Release Asset PublicSurface"),
    _snapshot_diff_keyset_v1(
        "state invalidators local_commit public_commit"),
    _snapshot_diff_keyset_v1(
        "id record_type family source_identity native_owner_identity "
        "currentness authority_ceiling layer object_identity"),
    _snapshot_diff_keyset_v1(
        "id record_type family source_identity native_owner_identity "
        "currentness authority_ceiling layer path sha256 manifest_sha256"),
    _snapshot_diff_keyset_v1(
        "id record_type family source_identity native_owner_identity "
        "currentness authority_ceiling layer stable_id commit_identity "
        "updated_at etag payload_sha256 native_currentness "
        "capture_currentness capture_identity capture_sha256"),
    _snapshot_diff_keyset_v1("code path"),
    _snapshot_diff_keyset_v1("kind collector owner state code"),
    _snapshot_diff_keyset_v1(
        "kind collector owner family fact_path record_id record_type "
        "native_owner_identity state invalidators"),
    _snapshot_diff_keyset_v1(
        "kind collector owner family layer fact_path record_id record_type "
        "native_owner_identity state invalidators"),
})

_SNAPSHOT_DIFF_DYNAMIC_MAP_SUFFIXES_V1 = (
    ".frontier.blocked_summary", ".frontier.writer_holds",
    ".frontier.resource_holds")


def _snapshot_diff_closed_tree_v1(value: object, path: str) -> None:
    """Consume every JSON branch admitted by the four producer grammars."""
    if type(value) is dict:
        dynamic = path.endswith(_SNAPSHOT_DIFF_DYNAMIC_MAP_SUFFIXES_V1)
        if not dynamic and frozenset(value) not in _SNAPSHOT_DIFF_CLOSED_KEYSETS_V1:
            _error("OE_DIFF_SNAPSHOT_INVALID", path,
                   "snapshot object has an unconsumed producer branch")
        for key, member in value.items():
            if type(key) is not str or not key:
                _error("OE_DIFF_SNAPSHOT_INVALID", path,
                       "snapshot object key must be non-empty text")
            _snapshot_diff_closed_tree_v1(member, f"{path}.{key}")
        return
    if type(value) is list:
        for index, member in enumerate(value):
            _snapshot_diff_closed_tree_v1(member, f"{path}[{index}]")
        return
    key = path.rsplit(".", 1)[-1]
    nullable = {
        "code", "public_commit", "obligation_id", "route_state",
        "first_red_id", "weakest_leg_id"}
    if value is None:
        if key not in nullable:
            _error("OE_DIFF_SNAPSHOT_INVALID", path,
                   "snapshot scalar is not nullable")
        return
    if type(value) is bool:
        if key not in {"proxy", "object_drift"}:
            _error("OE_DIFF_SNAPSHOT_INVALID", path,
                   "snapshot scalar boolean is not admitted here")
        return
    if type(value) is int:
        if value < 0 or key not in {
                "sequence", "bytes", "population", "rate_remaining",
                "pagination_pages", "DONE", "ACTIVE", "READY", "BLOCKED",
                "ATTEMPT", "RECEIPT", "EFFECT", "RECOVERY", "CLOSURE",
                "Commit", "Tree", "Worktree", "GeneratedArtifact", "Package",
                "Install", "Host", "PullRequest", "Check", "Merge", "Tag",
                "Release", "Asset", "PublicSurface"}:
            _error("OE_DIFF_SNAPSHOT_INVALID", path,
                   "snapshot scalar integer is not admitted here")
        return
    if type(value) is not str or not value:
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "snapshot scalar must be non-empty text")
    if ("sha256" in key or key.endswith("_digest") or key == "digest"):
        _snapshot_diff_digest_v1(value, path)
    enum_values = {
        "family": set(FAMILIES),
        "layer": {"LOCAL", "EXTERNAL"},
        "record_type": {
            "Claim", "Criterion", "Evidence", "Check", "Review", "Andon",
            "Residual", "Containment", "Countermeasure", "Rerun", "Recovery",
            "Commit", "Tree", "Worktree", "GeneratedArtifact", "Package",
            "Install", "Host", "PullRequest", "Merge", "Tag", "Release",
            "Asset", "PublicSurface"},
        "leg": {"ATTEMPT", "RECEIPT", "EFFECT", "RECOVERY", "CLOSURE"},
        "result_class": {"RED", "GREEN", "NONVERDICT", "UNKNOWN"},
        "cause_confidence": {"UNKNOWN", "LOW", "MEDIUM", "HIGH"},
        "recovery_state": {"NOT_CLAIMED", "ATTEMPTED", "OBSERVED", "UNVERIFIED"},
        "worktree_state": {"CLEAN", "DIRTY"},
        "file_type": {"file", "symlink"},
        "language": {"python", "shell", "javascript", "typescript", "json", "unsupported"},
        "auth_state": {"PRESENT", "ABSENT", "UNKNOWN"},
        "rate_state": {"AVAILABLE", "EXHAUSTED", "UNKNOWN"},
        "pagination_state": {"COMPLETE", "INCOMPLETE", "UNKNOWN"},
    }
    if key in enum_values and value not in enum_values[key]:
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "snapshot scalar has a foreign enum value")
    if key == "state" and value not in set(STATES) | {
            "SUPPORTED", "PARTIAL", "NOT_APPLICABLE"}:
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "snapshot state has a foreign enum value")


def _snapshot_diff_evidence_record_v1(
        value: object, path: str, identities: set[str]) -> dict:
    keys = {
        "id", "sequence", "record_type", "claim_id", "criterion_id", "leg",
        "result_class", "proxy", "source_identity", "native_owner_identity",
        "currentness", "controls", "contrary_evidence", "family",
        "authority_ceiling", "artifact_sha256"}
    row = _snapshot_diff_exact_object_v1(value, keys, path)
    identity = _snapshot_diff_text_v1(row["id"], f"{path}.id")
    if identity in identities:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.id",
               "snapshot record identity must be globally unique")
    identities.add(identity)
    if type(row["sequence"]) is not int or row["sequence"] < 0:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.sequence",
               "evidence sequence must be non-negative")
    if (row["record_type"] not in {
            "Claim", "Criterion", "Evidence", "Check", "Review"} or
            row["family"] != "EVIDENCE" or
            row["leg"] not in {
                "ATTEMPT", "RECEIPT", "EFFECT", "RECOVERY", "CLOSURE"} or
            row["result_class"] not in {"RED", "GREEN", "NONVERDICT", "UNKNOWN"} or
            type(row["proxy"]) is not bool or
            (row["proxy"] and row["leg"] not in {"ATTEMPT", "RECEIPT"}) or
            row["authority_ceiling"] != "READ_ONLY_NATIVE_ARTIFACT_FACT"):
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "evidence member type, family, leg, or authority differs")
    for key in ("claim_id", "criterion_id", "source_identity",
                "native_owner_identity"):
        _snapshot_diff_text_v1(row[key], f"{path}.{key}")
    for key in ("controls", "contrary_evidence"):
        _snapshot_diff_unique_string_list_v1(row[key], f"{path}.{key}")
    _snapshot_diff_currentness_v1(row["currentness"], f"{path}.currentness")
    _snapshot_diff_digest_v1(row["artifact_sha256"], f"{path}.artifact_sha256")
    return row


def _snapshot_diff_failure_record_v1(
        value: object, path: str, identities: set[str]) -> dict:
    keys = {
        "id", "sequence", "record_type", "andon_id", "abnormality_class",
        "statement", "cause_confidence", "evidence_ids", "recovery_state",
        "source_identity", "native_owner_identity", "currentness", "family",
        "authority_ceiling", "artifact_sha256"}
    row = _snapshot_diff_exact_object_v1(value, keys, path)
    identity = _snapshot_diff_text_v1(row["id"], f"{path}.id")
    if identity in identities:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.id",
               "snapshot record identity must be globally unique")
    identities.add(identity)
    if (type(row["sequence"]) is not int or row["sequence"] < 0 or
            row["record_type"] not in {
                "Andon", "Residual", "Containment", "Countermeasure",
                "Rerun", "Recovery"} or row["family"] != "FAILURE" or
            row["cause_confidence"] not in {"UNKNOWN", "LOW", "MEDIUM", "HIGH"} or
            row["recovery_state"] not in {
                "NOT_CLAIMED", "ATTEMPTED", "OBSERVED", "UNVERIFIED"} or
            row["authority_ceiling"] != "READ_ONLY_NATIVE_ARTIFACT_FACT"):
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "failure member type, family, recovery, or authority differs")
    for key in ("andon_id", "abnormality_class", "statement",
                "source_identity", "native_owner_identity"):
        _snapshot_diff_text_v1(row[key], f"{path}.{key}")
    _snapshot_diff_unique_string_list_v1(
        row["evidence_ids"], f"{path}.evidence_ids")
    _snapshot_diff_currentness_v1(row["currentness"], f"{path}.currentness")
    _snapshot_diff_digest_v1(row["artifact_sha256"], f"{path}.artifact_sha256")
    return row


def _snapshot_diff_release_record_v1(
        value: object, path: str, identities: set[str]) -> dict:
    required = {
        "id", "record_type", "family", "source_identity",
        "native_owner_identity", "currentness", "authority_ceiling", "layer"}
    variants = (
        required | {"object_identity"},
        required | {"path", "sha256", "manifest_sha256"},
        required | {
            "stable_id", "commit_identity", "updated_at", "etag",
            "payload_sha256", "native_currentness", "capture_currentness",
            "capture_identity", "capture_sha256"},
    )
    if type(value) is not dict or set(value) not in variants:
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "release member does not match an exact producer variant")
    identity = _snapshot_diff_text_v1(value["id"], f"{path}.id")
    if identity in identities:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.id",
               "snapshot record identity must be globally unique")
    identities.add(identity)
    if (value["record_type"] not in {
            "Commit", "Tree", "Worktree", "GeneratedArtifact", "Package",
            "Install", "Host", "PullRequest", "Check", "Merge", "Tag",
            "Release", "Asset", "PublicSurface"} or
            value["family"] != "RELEASE" or
            value["authority_ceiling"] != "READ_ONLY_NATIVE_OBSERVATION" or
            value["layer"] not in {"LOCAL", "EXTERNAL"}):
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "release member type, family, layer, or authority differs")
    for key in ("source_identity", "native_owner_identity"):
        _snapshot_diff_text_v1(value[key], f"{path}.{key}")
    _snapshot_diff_currentness_v1(value["currentness"], f"{path}.currentness")
    for key in ("native_currentness", "capture_currentness"):
        if key in value:
            _snapshot_diff_currentness_v1(value[key], f"{path}.{key}")
    if "object_identity" in value:
        object_identity = _snapshot_diff_text_v1(
            value["object_identity"], f"{path}.object_identity")
        if value["record_type"] in {"Commit", "Tree"}:
            if re.fullmatch(r"[0-9a-f]{40}", object_identity) is None:
                _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.object_identity",
                       "release Git object identity is malformed")
        elif value["record_type"] != "Worktree" or object_identity not in {
                "CLEAN", "DIRTY"}:
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.object_identity",
                   "release object identity differs from its local variant")
    if "path" in value:
        _snapshot_diff_text_v1(value["path"], f"{path}.path")
        _snapshot_diff_digest_v1(value["sha256"], f"{path}.sha256")
        _snapshot_diff_digest_v1(
            value["manifest_sha256"], f"{path}.manifest_sha256")
    if "stable_id" in value:
        for key in ("stable_id", "source_identity", "native_owner_identity",
                    "updated_at", "etag", "capture_identity"):
            _snapshot_diff_text_v1(value[key], f"{path}.{key}")
        _snapshot_diff_digest_v1(
            value["payload_sha256"], f"{path}.payload_sha256")
        _snapshot_diff_digest_v1(
            value["capture_sha256"], f"{path}.capture_sha256")
        if re.fullmatch(r"[0-9a-f]{40}", value["commit_identity"]) is None:
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.commit_identity",
                   "external release commit identity is malformed")
    return value


def _snapshot_diff_missing_v1(value: object, path: str) -> None:
    if type(value) is not dict or value.get("kind") not in {
            "COLLECTOR_NON_CURRENT", "REPOSITORY_DIAGNOSTIC",
            "OWNER_FACT_NON_CURRENT", "RELEASE_INVALIDATOR"}:
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "missing-or-omitted entry has a foreign schema")
    kind = value["kind"]
    schemas = {
        "COLLECTOR_NON_CURRENT": {
            "kind", "collector", "owner", "state", "code"},
        "REPOSITORY_DIAGNOSTIC": {
            "kind", "collector", "owner", "state", "code"},
        "RELEASE_INVALIDATOR": {"kind", "collector", "owner", "state", "code"},
    }
    if kind == "OWNER_FACT_NON_CURRENT":
        evidence_keys = {
            "kind", "collector", "owner", "family", "fact_path", "record_id",
            "record_type", "native_owner_identity", "state", "invalidators"}
        release_keys = evidence_keys | {"layer"}
        if set(value) not in (evidence_keys, release_keys):
            _error("OE_DIFF_SNAPSHOT_INVALID", path,
                   "owner-fact omission has a foreign schema")
        if value["family"] not in FAMILIES:
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.family",
                   "omitted owner fact has a foreign family")
        invalidators = value["invalidators"]
        if (type(invalidators) is not list or any(
                type(item) is not str or not item for item in invalidators) or
                (value["state"] == "STALE" and not invalidators)):
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.invalidators",
                   "omitted owner-fact invalidators are inconsistent")
    elif set(value) != schemas[kind]:
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "missing-or-omitted entry has a foreign key set")
    if value["state"] not in STATES or value["state"] == "CURRENT":
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.state",
               "omitted state must be a supported non-current state")
    for key in ("collector", "owner"):
        _snapshot_diff_text_v1(value[key], f"{path}.{key}")
    if kind != "OWNER_FACT_NON_CURRENT" and value["code"] is not None:
        _snapshot_diff_text_v1(value["code"], f"{path}.code")


def _snapshot_diff_repository_v1(value: dict, path: str) -> None:
    repository = _snapshot_diff_exact_object_v1(
        value["repository"],
        {"commit", "tree", "worktree_state", "input_file_set_sha256"},
        f"{path}.repository")
    for key in ("commit", "tree"):
        if re.fullmatch(r"[0-9a-f]{40}", repository[key]) is None:
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.repository.{key}",
                   "repository Git identity is malformed")
    _snapshot_diff_digest_v1(
        repository["input_file_set_sha256"],
        f"{path}.repository.input_file_set_sha256")

    diagnostics = _snapshot_diff_exact_object_v1(
        value["diagnostics"], {"warnings", "errors", "skipped", "unknown"},
        f"{path}.diagnostics")
    for bucket, members in diagnostics.items():
        if (type(members) is not list or any(
                type(member) is not str or not member for member in members) or
                len(set(members)) != len(members)):
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.diagnostics.{bucket}",
                   "repository diagnostic population is malformed")

    invocations = value["static_collector_invocations"]
    if type(invocations) is not list:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.static_collector_invocations",
               "static invocation population must be an array")
    invocation_keys = {
        "collector", "input_path", "input_sha256", "collector_identity",
        "collector_version", "collector_package_sha256", "invocation_identity",
        "output_schema_identity", "parser"}
    for index, invocation in enumerate(invocations):
        _snapshot_diff_exact_object_v1(
            invocation, invocation_keys,
            f"{path}.static_collector_invocations[{index}]")
        if invocation["collector"] != "python_ast":
            _error("OE_DIFF_SNAPSHOT_INVALID",
                   f"{path}.static_collector_invocations[{index}].collector",
                   "static invocation collector is foreign")

    capabilities = value["capabilities"]
    if type(capabilities) is not list:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.capabilities",
               "repository capabilities must be an array")
    seen_capabilities = set()
    for index, capability in enumerate(capabilities):
        capability_path = f"{path}.capabilities[{index}]"
        name = capability.get("capability") if type(capability) is dict else None
        keys = {"capability", "state", "reason_code"}
        if name == "python_ast" and invocations:
            keys.add("provenance")
        row = _snapshot_diff_exact_object_v1(capability, keys, capability_path)
        if (name not in {"file_facts", "package_manifest", "python_ast",
                         "validation_registry_entries"} or
                name in seen_capabilities):
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{capability_path}.capability",
                   "repository capability identity is foreign or duplicated")
        seen_capabilities.add(name)
        if "provenance" in row:
            expected = {
                "collector_identity", "collector_version",
                "collector_package_sha256", "invocation_identity",
                "output_schema_identity", "parser", "input_file_set_sha256"}
            _snapshot_diff_exact_object_v1(
                row["provenance"], expected, f"{capability_path}.provenance")
    if seen_capabilities != {
            "file_facts", "package_manifest", "python_ast",
            "validation_registry_entries"}:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.capabilities",
               "repository capability population is incomplete")

    fact_variants = {
        "FILE": {"kind", "path", "sha256", "bytes", "file_type",
                 "language", "state", "provenance"},
        "FILE_UNREADABLE_OBSERVATION": {"kind", "path", "state", "provenance"},
        "PARSER_ERROR_OBSERVATION": {"kind", "path", "state", "provenance"},
        "PYTHON_IMPORT": {"kind", "source", "target", "state", "provenance"},
        "PYTHON_REVERSE_DEPENDENT": {
            "kind", "source", "target", "state", "provenance"},
        "UNSUPPORTED_IMPORT_OBSERVATION": {
            "kind", "source", "target", "state", "provenance"},
        "PACKAGE_MANIFEST": {
            "kind", "path", "package_name", "sha256", "state", "provenance"},
        "PACKAGE_ROOT": {"kind", "package_name", "path", "state", "provenance"},
        "PACKAGE_MANIFEST_ERROR": {"kind", "path", "state", "provenance"},
        "REGISTRY_FILE": {"kind", "path", "sha256", "state", "provenance"},
    }
    facts = value["facts"]
    if type(facts) is not list:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.facts",
               "repository facts must be an array")
    ast_keys = {
        "collector_identity", "collector_version", "collector_package_sha256",
        "invocation_identity", "output_schema_identity", "parser",
        "input_path", "input_sha256"}
    for index, fact in enumerate(facts):
        fact_path = f"{path}.facts[{index}]"
        kind = fact.get("kind") if type(fact) is dict else None
        if kind not in fact_variants:
            _error("OE_DIFF_SNAPSHOT_INVALID", fact_path,
                   "repository fact kind is foreign")
        row = _snapshot_diff_exact_object_v1(
            fact, fact_variants[kind], fact_path)
        provenance_keys = {
            "FILE": {"method", "commit", "tree"},
            "FILE_UNREADABLE_OBSERVATION": {"method", "commit", "tree"},
            "PARSER_ERROR_OBSERVATION": ast_keys,
            "PYTHON_IMPORT": ast_keys,
            "PYTHON_REVERSE_DEPENDENT": ast_keys,
            "UNSUPPORTED_IMPORT_OBSERVATION": ast_keys | {"reason"},
            "PACKAGE_MANIFEST": {"parser", "input_path"},
            "PACKAGE_ROOT": {"parser", "input_path", "input_sha256"},
            "PACKAGE_MANIFEST_ERROR": {"parser", "input_path", "input_sha256"},
            "REGISTRY_FILE": {"method", "reason"},
        }[kind]
        _snapshot_diff_exact_object_v1(
            row["provenance"], provenance_keys, f"{fact_path}.provenance")


def _snapshot_diff_native_v1(value: dict, path: str) -> None:
    fixed = {
        "repository": {"root", "git_common_dir"},
        "controller": {"id", "ref", "record_oid"},
        "claim": {"id", "run_id", "run_root"},
        "continuity": {
            "generation", "source_epoch", "invalidation_ref", "invalidation_oid",
            "boundary_kind", "boundary_event_id", "pointer_ref", "pointer_oid",
            "pointer_digest", "receipt_schema", "receipt_ref", "receipt_oid",
            "receipt", "marker_ref", "marker_oid", "generation_manifest_oid",
            "generation_manifest_digest", "cold_high_water", "degraded_state"},
        "hot": {
            "state_path", "state_sha256", "roadmap_path", "roadmap_sha256",
            "work_graph_path", "work_graph_sha256", "work_graph_compiler_sha256"},
        "frontier": {
            "population", "counts", "active", "ready", "blocked_summary",
            "writer_holds", "resource_holds", "digest"},
        "route": {
            "controller_id", "controller_record_oid", "ref", "record_oid",
            "record_identity", "decision", "classification",
            "route_transaction_id", "obligation_id", "route_state"},
    }
    for key, keys in fixed.items():
        _snapshot_diff_exact_object_v1(value[key], keys, f"{path}.{key}")
    for key in ("controller", "continuity", "route"):
        for member, item in value[key].items():
            if member.endswith("_oid") and re.fullmatch(r"[0-9a-f]{40}", item) is None:
                _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.{key}.{member}",
                       "native Git object identity is malformed")
    if value["route"]["decision"] not in {"REQUIRED", "NOT_REQUIRED"}:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.route.decision",
               "native route decision is foreign")
    if value["route"]["decision"] == "REQUIRED":
        if (type(value["route"]["obligation_id"]) is not str or
                value["route"]["route_state"] not in {
                    "UNSATISFIED", "OPEN", "RETURNED", "SATISFIED"}):
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.route",
                   "required route obligation state is malformed")
    counts = _snapshot_diff_exact_object_v1(
        value["frontier"]["counts"], {"DONE", "ACTIVE", "READY", "BLOCKED"},
        f"{path}.frontier.counts")
    if (sum(counts.values()) != value["frontier"]["population"] or
            len(value["frontier"]["active"]) != counts["ACTIVE"] or
            len(value["frontier"]["ready"]) != counts["READY"] or
            len(value["frontier"]["blocked_summary"]) != counts["BLOCKED"]):
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.frontier",
               "native frontier census differs from its population")
    for name in ("active", "ready"):
        members = value["frontier"][name]
        if (type(members) is not list or members != sorted(set(members)) or
                any(type(member) is not str or not member for member in members)):
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.frontier.{name}",
                   "native frontier identities are malformed")
    for name in ("blocked_summary", "writer_holds", "resource_holds"):
        mapping = value["frontier"][name]
        if type(mapping) is not dict:
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.frontier.{name}",
                   "native frontier hold map is malformed")
        for identity, members in mapping.items():
            if (not identity or type(members) is not list or
                    members != sorted(set(members)) or
                    any(type(member) is not str or not member for member in members)):
                _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.frontier.{name}",
                       "native frontier hold population is malformed")
    frontier = dict(value["frontier"])
    digest = frontier.pop("digest")
    if hashlib.sha256(canonical_json_v1(frontier)).hexdigest() != digest:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.frontier.digest",
               "native frontier digest differs")
    if (type(value["open_andons"]) is not list or
            value["open_andons"] != sorted(set(value["open_andons"])) or
            not value["open_andons"]):
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.open_andons",
               "native open-Andon population is malformed")
    instructions = value["active_instructions"]
    instruction_keys = {
        "id", "reference", "kind", "authority", "subject", "issued_epoch",
        "status", "status_evidence", "supersedes_by", "scope_end"}
    if type(instructions) is not list or not instructions:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.active_instructions",
               "native active-instruction population is absent")
    seen = set()
    for index, instruction in enumerate(instructions):
        row = _snapshot_diff_exact_object_v1(
            instruction, instruction_keys, f"{path}.active_instructions[{index}]")
        if row["status"] != "active" or row["id"] in seen:
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.active_instructions[{index}]",
                   "native active instruction is foreign or duplicated")
        seen.add(row["id"])


def _snapshot_diff_release_v1(value: dict, path: str) -> None:
    repository = _snapshot_diff_exact_object_v1(
        value["repository"], {"commit", "tree", "worktree_state"},
        f"{path}.repository")
    boundary = _snapshot_diff_exact_object_v1(
        value["external_boundary"], {
            "capture_identity", "source_identity", "auth_state", "rate_state",
            "rate_remaining", "pagination_state", "pagination_pages",
            "object_drift", "captured_at", "expires_at", "evaluated_at"},
        f"{path}.external_boundary")
    candidate = _snapshot_diff_exact_object_v1(
        value["candidate"], {"state", "invalidators", "local_commit", "public_commit"},
        f"{path}.candidate")
    if (candidate["state"] != "UNVERIFIED" or
            candidate["local_commit"] != repository["commit"]):
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.candidate",
               "release candidate state or local identity differs")
    for key in ("captured_at", "expires_at", "evaluated_at"):
        if (type(boundary[key]) is not str or re.fullmatch(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", boundary[key]) is None):
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.external_boundary.{key}",
                   "release boundary timestamp is malformed")
    if (boundary["captured_at"] >= boundary["expires_at"] or
            boundary["evaluated_at"] < boundary["captured_at"]):
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.external_boundary",
               "release boundary chronology differs")
    boundary_currentness = _external_boundary_currentness(
        boundary["auth_state"], boundary["rate_state"],
        boundary["pagination_state"], boundary["object_drift"],
        boundary["expires_at"], boundary["evaluated_at"])
    local_types = {"GeneratedArtifact", "Package", "Install", "Host"}
    external_types = {
        "PullRequest", "Check", "Merge", "Tag", "Release", "Asset",
        "PublicSurface"}
    for index, row in enumerate(value["nodes"]):
        node_path = f"{path}.nodes[{index}]"
        if "object_identity" in row:
            if row["record_type"] not in {"Commit", "Tree", "Worktree"} or row["layer"] != "LOCAL":
                _error("OE_DIFF_SNAPSHOT_INVALID", node_path,
                       "release object node uses a foreign variant")
        elif "path" in row:
            if row["record_type"] not in local_types or row["layer"] != "LOCAL":
                _error("OE_DIFF_SNAPSHOT_INVALID", node_path,
                       "release local-path node uses a foreign variant")
        elif row["record_type"] not in external_types or row["layer"] != "EXTERNAL":
            _error("OE_DIFF_SNAPSHOT_INVALID", node_path,
                   "release external node uses a foreign variant")
        if row["layer"] == "EXTERNAL":
            expected = _compose_currentness(
                row["native_currentness"], row["capture_currentness"])
            if (row["capture_currentness"] != boundary_currentness or
                    row["currentness"] != expected or
                    row["capture_identity"] != boundary["capture_identity"] or
                    row["capture_sha256"] != value["external_capture_sha256"]):
                _error("OE_DIFF_SNAPSHOT_INVALID", node_path,
                       "release external currentness or capture identity differs")
    required_types = {
        "Commit", "Tree", "Worktree", "GeneratedArtifact", "Package",
        "Install", "Host", "PullRequest", "Check", "Merge", "Tag",
        "Release", "Asset", "PublicSurface"}
    observed_types = {row["record_type"] for row in value["nodes"]}
    missing_types = sorted(required_types - observed_types)
    expected_omissions = [{
        "record_type": record_type, "state": "UNKNOWN",
        "invalidator": f"MISSING_RELEASE_LAYER:{record_type}"}
        for record_type in missing_types]
    if value["omissions"] != expected_omissions:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.omissions",
               "release omission census differs from validated nodes")
    public_nodes = [
        row for row in value["nodes"] if row["record_type"] == "PublicSurface"]
    public_commit = (public_nodes[0]["commit_identity"]
                     if len(public_nodes) == 1 else None)
    if candidate["public_commit"] != public_commit:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.candidate.public_commit",
               "release public candidate identity differs")
    expected_invalidators = list(boundary_currentness["invalidators"])
    for row in (item for item in value["nodes"] if item["layer"] == "EXTERNAL"):
        for invalidator in row["currentness"]["invalidators"]:
            if invalidator not in expected_invalidators:
                expected_invalidators.append(invalidator)
    expected_invalidators.extend(
        f"MISSING_RELEASE_LAYER:{record_type}" for record_type in missing_types)
    if len(public_nodes) != 1:
        expected_invalidators.append("PUBLIC_IDENTITY_NOT_EXACTLY_ONE")
    elif public_commit != repository["commit"]:
        expected_invalidators.append("PUBLIC_PREDECESSOR_DIFFERS_FROM_LOCAL_COMMIT")
    if repository["worktree_state"] != "CLEAN":
        expected_invalidators.append("LOCAL_WORKTREE_DIRTY")
    if not expected_invalidators:
        expected_invalidators.append("NATIVE_CANDIDATE_QUALIFICATION_REQUIRED")
    if candidate["invalidators"] != expected_invalidators:
        _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.candidate.invalidators",
               "release candidate invalidators differ from validated nodes")


def _snapshot_diff_collections_v1(
        collections: object, path: str) -> tuple[set[str], list[dict]]:
    owners = {
        "native_current": "R0038-C03", "repository": "R0038-C02",
        "evidence_failure": "R0038-C04", "release": "R0038-C05"}
    if type(collections) is not dict or set(collections) != set(owners):
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "snapshot must retain the complete producer collection population")
    identities: set[str] = set()
    population: list[dict] = []
    for name in sorted(owners):
        member_path = f"{path}.{name}"
        member = _snapshot_diff_exact_object_v1(
            collections[name], {"owner", "state", "value", "sha256"}, member_path)
        if member["owner"] != owners[name] or member["state"] not in {"CURRENT", "UNKNOWN"}:
            _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                   "snapshot collection owner or state differs")
        if name in {"native_current", "repository"} and member["state"] != "CURRENT":
            _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                   "required snapshot collector is not CURRENT")
        value = member["value"]
        digest = _snapshot_diff_digest_v1(member["sha256"], f"{member_path}.sha256")
        if hashlib.sha256(canonical_json_v1(value)).hexdigest() != digest:
            _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                   "snapshot collection digest differs")
        if member["state"] == "UNKNOWN":
            unknown = _snapshot_diff_exact_object_v1(
                value, {"code", "path"}, f"{member_path}.value")
            _snapshot_diff_text_v1(unknown["code"], f"{member_path}.value.code")
            _snapshot_diff_text_v1(unknown["path"], f"{member_path}.value.path")
            continue
        if name == "native_current":
            keys = {
                "schema", "authority_ceiling", "establishes", "repository",
                "controller", "claim", "continuity", "hot", "frontier",
                "andon_state", "open_andons", "active_instructions",
                "next_action", "route", "semantic_sha256"}
            current = _snapshot_diff_exact_object_v1(value, keys, f"{member_path}.value")
            if (current["schema"] != NATIVE_CURRENT_SCHEMA or
                    current["authority_ceiling"] != "READ_ONLY_NATIVE_CURRENT_FACT" or
                    current["establishes"] != [] or any(
                        type(current[key]) is not dict or not current[key]
                        for key in ("repository", "controller", "claim", "continuity",
                                    "hot", "frontier", "route")) or
                    type(current["open_andons"]) is not list or
                    type(current["active_instructions"]) is not list):
                _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                       "native-current collection schema differs")
            _snapshot_diff_text_v1(current["andon_state"], f"{member_path}.andon_state")
            _snapshot_diff_text_v1(current["next_action"], f"{member_path}.next_action")
            _snapshot_diff_native_v1(current, f"{member_path}.value")
            route = current["route"]
            if (route["decision"] != "REQUIRED" and
                    (route["obligation_id"] is not None or
                     route["route_state"] is not None)):
                _error("OE_DIFF_SNAPSHOT_INVALID", f"{member_path}.value.route",
                       "non-required route cannot retain obligation state")
            _snapshot_diff_semantic_v1(current, f"{member_path}.value")
        elif name == "repository":
            keys = {
                "schema", "repository", "capabilities", "diagnostics", "facts",
                "static_collector_invocations"}
            repository = _snapshot_diff_exact_object_v1(
                value, keys, f"{member_path}.value")
            if (repository["schema"] != REPOSITORY_COLLECTION_SCHEMA or
                    type(repository["repository"]) is not dict or
                    type(repository["capabilities"]) is not list or
                    type(repository["facts"]) is not list or
                    type(repository["static_collector_invocations"]) is not list or
                    type(repository["diagnostics"]) is not dict):
                _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                       "repository collection schema differs")
            _snapshot_diff_repository_v1(repository, f"{member_path}.value")
        elif name == "evidence_failure":
            keys = {
                "schema", "families", "source", "first_red_id", "first_red_state",
                "weakest_leg_id", "residual_ids", "layer_census",
                "evidence_records", "failure_records", "establishes",
                "semantic_sha256"}
            evidence = _snapshot_diff_exact_object_v1(
                value, keys, f"{member_path}.value")
            if (evidence["schema"] != EVIDENCE_FAILURE_COLLECTION_SCHEMA or
                    evidence["families"] != ["EVIDENCE", "FAILURE"] or
                    evidence["establishes"] != [] or
                    type(evidence["evidence_records"]) is not list or
                    type(evidence["failure_records"]) is not list or
                    type(evidence["residual_ids"]) is not list):
                _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                       "evidence/failure collection schema differs")
            evidence_sequences = []
            for index, row in enumerate(evidence["evidence_records"]):
                record_path = f"{member_path}.value.evidence_records[{index}]"
                parsed = _snapshot_diff_evidence_record_v1(
                    row, record_path, identities)
                population.append({"path": f"record:{parsed['id']}",
                                   "record": parsed})
                evidence_sequences.append(row["sequence"])
            failure_sequences = []
            for index, row in enumerate(evidence["failure_records"]):
                record_path = f"{member_path}.value.failure_records[{index}]"
                parsed = _snapshot_diff_failure_record_v1(
                    row, record_path, identities)
                population.append({"path": f"record:{parsed['id']}",
                                   "record": parsed})
                failure_sequences.append(row["sequence"])
            if (len(evidence_sequences) != len(set(evidence_sequences)) or
                    len(failure_sequences) != len(set(failure_sequences))):
                _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                       "snapshot evidence/failure sequences are not unique")
            evidence_by_id = {
                row["id"]: row for row in evidence["evidence_records"]}
            failure_by_id = {
                row["id"]: row for row in evidence["failure_records"]}
            red_records = [
                row for row in evidence["evidence_records"]
                if row["result_class"] == "RED" and not row["proxy"]]
            expected_first_red = (min(
                red_records, key=lambda row: row["sequence"])["id"]
                if red_records else None)
            if (evidence["first_red_id"] != expected_first_red or
                    evidence["first_red_state"] != (
                        "PRESENT" if red_records else "NOT_APPLICABLE")):
                _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                       "first RED identity/state differs from validated evidence")
            weakest = evidence_by_id.get(evidence["weakest_leg_id"])
            if (weakest is None or weakest["proxy"] or
                    (red_records and weakest["result_class"] != "RED")):
                _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                       "weakest leg differs from validated evidence")
            for row in evidence["evidence_records"]:
                if any(reference not in evidence_by_id
                       for reference in row["contrary_evidence"]):
                    _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                           "contrary evidence references an absent record")
            andon_ids = {
                row["id"] for row in evidence["failure_records"]
                if row["record_type"] == "Andon"}
            for row in evidence["failure_records"]:
                if (row["andon_id"] not in andon_ids or any(
                        reference not in evidence_by_id
                        for reference in row["evidence_ids"])):
                    _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                           "failure lineage references an absent record")
                if row["recovery_state"] == "OBSERVED":
                    recovery = [evidence_by_id[item] for item in row["evidence_ids"]]
                    if (not recovery or any(
                            item["leg"] != "RECOVERY" or
                            item["result_class"] != "GREEN" or item["proxy"] or
                            item["currentness"]["state"] != "CURRENT"
                            for item in recovery)):
                        _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                               "observed recovery lacks current direct evidence")
            _snapshot_diff_unique_string_list_v1(
                evidence["residual_ids"], f"{member_path}.value.residual_ids")
            if (any(item not in failure_by_id or
                        failure_by_id[item]["record_type"] != "Residual"
                        for item in evidence["residual_ids"])):
                _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                       "residual census differs from validated failure records")
            expected_census = Counter(
                row["leg"] for row in evidence["evidence_records"])
            if evidence["layer_census"] != {
                    leg: expected_census.get(leg, 0)
                    for leg in ("ATTEMPT", "RECEIPT", "EFFECT", "RECOVERY", "CLOSURE")}:
                _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                       "evidence layer census differs from validated records")
            _snapshot_diff_semantic_v1(evidence, f"{member_path}.value")
        else:
            keys = {
                "schema", "families", "repository", "local_manifest_sha256",
                "external_capture_sha256", "external_boundary", "omissions",
                "node_type_census", "nodes", "candidate", "establishes",
                "semantic_sha256"}
            release = _snapshot_diff_exact_object_v1(
                value, keys, f"{member_path}.value")
            if (release["schema"] != RELEASE_COLLECTION_SCHEMA or
                    release["families"] != ["RELEASE"] or
                    release["establishes"] != [] or
                    type(release["nodes"]) is not list or
                    type(release["omissions"]) is not list or
                    type(release["node_type_census"]) is not dict or
                    type(release["candidate"]) is not dict):
                _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                       "release collection schema differs")
            for index, row in enumerate(release["nodes"]):
                record_path = f"{member_path}.value.nodes[{index}]"
                parsed = _snapshot_diff_release_record_v1(
                    row, record_path, identities)
                population.append({"path": f"record:{parsed['id']}",
                                   "record": parsed})
            required_types = {
                "Commit", "Tree", "Worktree", "GeneratedArtifact", "Package",
                "Install", "Host", "PullRequest", "Check", "Merge", "Tag",
                "Release", "Asset", "PublicSurface"}
            type_census = Counter(row["record_type"] for row in release["nodes"])
            if release["node_type_census"] != {
                    key: type_census[key] for key in sorted(required_types)}:
                _error("OE_DIFF_SNAPSHOT_INVALID", member_path,
                       "release node-type census differs from validated records")
            _snapshot_diff_release_v1(release, f"{member_path}.value")
            _snapshot_diff_semantic_v1(release, f"{member_path}.value")
    return identities, population


def _parse_diff_snapshot_v1(snapshot: object, path: str) -> tuple[dict, list[dict]]:
    """Validate one immutable payload without repairing or selecting authority."""
    if (type(snapshot) is not dict or set(snapshot) != SNAPSHOT_PAYLOAD_KEYS or
            snapshot.get("schema_version") != SNAPSHOT_PAYLOAD_SCHEMA or
            type(snapshot.get("snapshot_id")) is not str or
            not SNAPSHOT_ID_RE.fullmatch(snapshot["snapshot_id"]) or
            snapshot.get("aggregate") not in AGGREGATES or
            tuple(snapshot.get("families", ())) != FAMILIES or
            type(snapshot.get("missing_or_omitted_state")) is not list or
            type(snapshot.get("collections")) is not dict or
            type(snapshot.get("input_manifest_sha256")) is not str or
            not re.fullmatch(r"[0-9a-f]{64}", snapshot["input_manifest_sha256"]) or
            snapshot["snapshot_id"] !=
            "iasnap-v1-" + snapshot["input_manifest_sha256"]):
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "snapshot payload schema, identity, families, or manifest differs")
    try:
        validate_identity_json_v1(snapshot, path)
        canonical = json.loads(canonical_json_v1(snapshot).decode("utf-8"))
        _snapshot_diff_closed_tree_v1(canonical, path)
        missing = canonical["missing_or_omitted_state"]
        for index, row in enumerate(missing):
            _snapshot_diff_missing_v1(row, f"{path}.missing_or_omitted_state[{index}]")
        if canonical["aggregate"] not in {"COMPLETE", "DEGRADED"} or (
                canonical["aggregate"] == "COMPLETE") != (not missing):
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.aggregate",
                   "snapshot aggregate and missing-state census differ")
        validated_identities, population = _snapshot_diff_collections_v1(
            canonical["collections"], f"{path}.collections")
        if _snapshot_missing_census_v1(canonical["collections"]) != missing:
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.missing_or_omitted_state",
                   "snapshot missing-state census differs from validated collections")
        if {row["record"]["id"] for row in population} != validated_identities:
            _error("OE_DIFF_SNAPSHOT_INVALID", f"{path}.collections",
                   "snapshot record population differs from validated members")
    except OperationalEvidenceError as exc:
        if exc.code == "OE_DIFF_SNAPSHOT_INVALID":
            raise
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "snapshot payload contains invalid or duplicate records")
    except Exception:
        _error("OE_DIFF_SNAPSHOT_INVALID", path,
               "snapshot payload contains a malformed producer branch")
    return canonical, population


def _validate_diff_snapshot_v1(snapshot: object, path: str) -> dict:
    return _parse_diff_snapshot_v1(snapshot, path)[0]


def _snapshot_diff_items_v1(
        snapshot: dict, population: list[dict]) -> dict[str, object]:
    items = {
        "snapshot:aggregate": snapshot["aggregate"],
        "snapshot:families": snapshot["families"],
        "snapshot:missing_or_omitted_state": sorted(
            snapshot["missing_or_omitted_state"], key=canonical_json_v1),
    }
    for row in population:
        items[row["path"]] = row["record"]
    return items


def diff_snapshots(before: object, after: object) -> dict:
    """Return a deterministic semantic diff between two validated payloads."""
    left, left_population = _parse_diff_snapshot_v1(before, "$.before")
    right, right_population = _parse_diff_snapshot_v1(after, "$.after")
    left_items = _snapshot_diff_items_v1(left, left_population)
    right_items = _snapshot_diff_items_v1(right, right_population)
    left_keys = set(left_items)
    right_keys = set(right_items)
    added = [
        {"identity": identity, "record": right_items[identity]}
        for identity in sorted(right_keys - left_keys)]
    removed = [
        {"identity": identity, "record": left_items[identity]}
        for identity in sorted(left_keys - right_keys)]
    changed = [
        {"identity": identity, "before": left_items[identity],
         "after": right_items[identity]}
        for identity in sorted(left_keys & right_keys)
        if canonical_json_v1(left_items[identity]) !=
        canonical_json_v1(right_items[identity])]
    return {
        "schema": SNAPSHOT_DIFF_SCHEMA,
        "before_snapshot_id": left["snapshot_id"],
        "after_snapshot_id": right["snapshot_id"],
        "before_input_manifest_sha256": left["input_manifest_sha256"],
        "after_input_manifest_sha256": right["input_manifest_sha256"],
        "added": added, "removed": removed, "changed": changed,
        "counts": {"added": len(added), "removed": len(removed),
                   "changed": len(changed)},
        "authority_ceiling": "READ_ONLY_OBSERVATION", "establishes": [],
    }


def render_snapshot_projection_v1(
        snapshot: object, *, output_format: str,
        max_rows: int, max_bytes: int) -> bytes:
    """Render an inert bounded table/graph projection as canonical JSON."""
    value, population = _parse_diff_snapshot_v1(snapshot, "$snapshot")
    return _render_snapshot_projection_parsed_v1(
        value, population, output_format=output_format,
        max_rows=max_rows, max_bytes=max_bytes)


def _render_snapshot_projection_parsed_v1(
        value: dict, population: list[dict], *, output_format: str,
        max_rows: int, max_bytes: int) -> bytes:
    if output_format not in ("table", "graph"):
        _error("OE_EXPORT_FORMAT_INVALID", "$.format",
               "bounded projection format must be table or graph")
    if (type(max_rows) is not int or max_rows <= 0 or
            type(max_bytes) is not int or max_bytes <= 0):
        _error("OE_EXPORT_BOUND_INVALID", "$export",
               "projection bounds must be finite positive integers")
    population.sort(key=lambda row: (
        row["record"]["currentness"]["state"] == "CURRENT",
        row["record"]["currentness"]["state"],
        row["record"]["family"], row["record"]["id"],
        canonical_json_v1(row["record"])))
    state_census = Counter(
        row["record"]["currentness"]["state"] for row in population)
    retained = []
    retained_bytes = 0
    for row in population:
        row_bytes = len(canonical_json_v1(row))
        if len(retained) >= max_rows or retained_bytes + row_bytes > max_bytes:
            break
        retained.append(row)
        retained_bytes += row_bytes
    retained_ids = {row["record"]["id"] for row in retained}
    omitted_state_census = Counter(
        row["record"]["currentness"]["state"] for row in population
        if row["record"]["id"] not in retained_ids)
    omitted_count = len(population) - len(retained)
    result = {
        "schema": SNAPSHOT_PROJECTION_SCHEMA,
        "format": output_format, "snapshot_id": value["snapshot_id"],
        "rows": retained, "row_bytes": retained_bytes,
        "max_rows": max_rows, "max_bytes": max_bytes,
        "population_count": len(population),
        "included_count": len(retained), "omitted_count": omitted_count,
        "state_census": dict(sorted(state_census.items())),
        "omitted_state_census": dict(sorted(omitted_state_census.items())),
        "missing_or_omitted_state": sorted(
            value["missing_or_omitted_state"], key=canonical_json_v1),
        "truncated": omitted_count != 0,
        "code": ("OE_EXPORT_REQUIRES_BOUNDED_REVIEW"
                 if omitted_count else "OK"),
        "decision_usable": omitted_count == 0,
        "authority_ceiling": "READ_ONLY_OBSERVATION", "establishes": [],
    }
    return canonical_json_v1(result)


def _export_destination_v1(
        destination: object, owned_root: object) -> tuple[pathlib.Path, pathlib.Path]:
    if not isinstance(destination, (str, os.PathLike)) or not isinstance(
            owned_root, (str, os.PathLike)):
        _error("OE_EXPORT_DESTINATION_INVALID", "$.destination",
               "destination and owned root must be explicit paths")
    requested_spelling = os.fspath(destination)
    root_spelling = os.fspath(owned_root)
    requested = pathlib.Path(requested_spelling)
    root = pathlib.Path(root_spelling)
    if not requested.is_absolute() or not root.is_absolute():
        _error("OE_EXPORT_DESTINATION_INVALID", "$.destination",
               "destination authority cannot be cwd-relative")
    try:
        if (os.path.normpath(requested_spelling) != requested_spelling or
                os.path.normpath(root_spelling) != root_spelling or
                pathlib.Path(os.path.abspath(requested_spelling)) != requested or
                pathlib.Path(os.path.abspath(root_spelling)) != root):
            raise OSError("destination or owned root spelling is not canonical")
        if _snapshot_is_link_v1(root):
            raise OSError("owned root is a link or reparse point")
        resolved_root = root.resolve(strict=True)
        if (not resolved_root.is_dir() or
                os.fspath(resolved_root) != os.fspath(root)):
            raise OSError("owned root is not a directory")
        resolved_destination = requested.resolve(strict=False)
        if os.fspath(resolved_destination) != os.fspath(requested):
            raise OSError("destination spelling aliases a different path")
        resolved_destination.relative_to(resolved_root)
        relative_parent = resolved_destination.parent.relative_to(resolved_root)
        cursor = resolved_root
        for part in relative_parent.parts:
            cursor = cursor / part
            if (_snapshot_is_link_v1(cursor) or not cursor.is_dir() or
                    os.fspath(cursor.resolve(strict=True)) != os.fspath(cursor)):
                raise OSError("destination parent is not an owned regular directory")
        repository = pathlib.Path(__file__).resolve().parents[3]
        try:
            resolved_root.relative_to(repository)
        except ValueError:
            pass
        else:
            raise OSError("repository and authority roots are not export custody")
    except (OSError, RuntimeError, ValueError):
        _error("OE_EXPORT_DESTINATION_INVALID", "$.destination",
               "destination is outside the explicit isolated owned root")
    if os.path.lexists(resolved_destination):
        _error("OE_EXPORT_DESTINATION_EXISTS", "$.destination",
               "export destination must be new and task-owned")
    return resolved_destination, resolved_root


def _snapshot_same_file_identity_v1(left: os.stat_result, right: os.stat_result) -> bool:
    return (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)


def _snapshot_windows_kernel_v1():
    if os.name != "nt":
        raise OSError("staged export requires Windows no-replace handle rename")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [
        ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    kernel.CreateFileW.restype = ctypes.c_void_p
    kernel.WriteFile.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p]
    kernel.WriteFile.restype = ctypes.c_int
    kernel.ReadFile.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p]
    kernel.ReadFile.restype = ctypes.c_int
    kernel.FlushFileBuffers.argtypes = [ctypes.c_void_p]
    kernel.FlushFileBuffers.restype = ctypes.c_int
    kernel.SetFilePointerEx.argtypes = [
        ctypes.c_void_p, ctypes.c_int64, ctypes.POINTER(ctypes.c_int64),
        ctypes.c_uint32]
    kernel.SetFilePointerEx.restype = ctypes.c_int
    kernel.SetFileInformationByHandle.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    kernel.SetFileInformationByHandle.restype = ctypes.c_int
    kernel.GetFileInformationByHandle.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    kernel.GetFileInformationByHandle.restype = ctypes.c_int
    kernel.GetVolumeInformationByHandleW.argtypes = [
        ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_wchar_p, ctypes.c_uint32]
    kernel.GetVolumeInformationByHandleW.restype = ctypes.c_int
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.CloseHandle.restype = ctypes.c_int
    return kernel


class _SnapshotFileTimeV1(ctypes.Structure):
    _fields_ = [("low", ctypes.c_uint32), ("high", ctypes.c_uint32)]


class _SnapshotHandleInfoV1(ctypes.Structure):
    _fields_ = [
        ("attributes", ctypes.c_uint32),
        ("creation_time", _SnapshotFileTimeV1),
        ("access_time", _SnapshotFileTimeV1),
        ("write_time", _SnapshotFileTimeV1),
        ("volume_serial", ctypes.c_uint32),
        ("size_high", ctypes.c_uint32),
        ("size_low", ctypes.c_uint32),
        ("links", ctypes.c_uint32),
        ("file_index_high", ctypes.c_uint32),
        ("file_index_low", ctypes.c_uint32),
    ]


def _snapshot_handle_info_v1(kernel, handle) -> _SnapshotHandleInfoV1:
    info = _SnapshotHandleInfoV1()
    if not kernel.GetFileInformationByHandle(handle, ctypes.byref(info)):
        raise ctypes.WinError(ctypes.get_last_error())
    return info


def _snapshot_handle_regular_v1(info: _SnapshotHandleInfoV1, size: int) -> bool:
    observed_size = (info.size_high << 32) | info.size_low
    return not (info.attributes & (0x10 | 0x400)) and info.links == 1 and (
        observed_size == size)


def _snapshot_hardlink_publication_capable_v1(kernel, handle) -> bool:
    """Admit publication only when the bound volume cannot add hard links."""
    flags = ctypes.c_uint32()
    if not kernel.GetVolumeInformationByHandleW(
            handle, None, 0, None, None, ctypes.byref(flags), None, 0):
        raise ctypes.WinError(ctypes.get_last_error())
    return not bool(flags.value & 0x00400000)


def _snapshot_delete_stage_v1(kernel, handle) -> None:
    disposition = ctypes.c_ubyte(1)
    if not kernel.SetFileInformationByHandle(
            handle, 4, ctypes.byref(disposition), ctypes.sizeof(disposition)):
        raise ctypes.WinError(ctypes.get_last_error())


def _snapshot_atomic_no_replace_v1(handle, target: pathlib.Path) -> None:
    """Atomically rename the live private stage; replacement is forbidden."""
    kernel = _snapshot_windows_kernel_v1()
    name = os.fspath(target).encode("utf-16-le")
    pointer_size = ctypes.sizeof(ctypes.c_void_p)
    root_offset = (4 + pointer_size - 1) // pointer_size * pointer_size
    length_offset = root_offset + pointer_size
    name_offset = length_offset + 4
    buffer = ctypes.create_string_buffer(name_offset + len(name) + 2)
    ctypes.c_uint32.from_buffer(buffer, 0).value = 0
    ctypes.c_void_p.from_buffer(buffer, root_offset).value = None
    ctypes.c_uint32.from_buffer(buffer, length_offset).value = len(name)
    ctypes.memmove(ctypes.addressof(buffer) + name_offset, name, len(name))
    if not kernel.SetFileInformationByHandle(
            handle, 3, buffer, name_offset + len(name)):
        code = ctypes.get_last_error()
        if code in {80, 183}:
            raise FileExistsError(code, "export destination became occupied")
        raise ctypes.WinError(code)


def _snapshot_stage_export_v1(raw: bytes, target: pathlib.Path) -> None:
    """Publish one exact byte string through a write/delete-excluded stage."""
    kernel = _snapshot_windows_kernel_v1()
    stage = target.with_name(
        f".{target.name}.{secrets.token_hex(16)}.implementaudit-stage")
    handle = kernel.CreateFileW(
        os.fspath(stage), 0x80000000 | 0x40000000 | 0x00010000,
        0x00000001, None, 1, 0x00000100, None)
    if handle == ctypes.c_void_p(-1).value:
        code = ctypes.get_last_error()
        if code in {80, 183}:
            raise OSError(code, "private stage identity collided")
        raise ctypes.WinError(code)
    published = False
    delete_marked = False
    try:
        created = _snapshot_handle_info_v1(kernel, handle)
        if not _snapshot_handle_regular_v1(created, 0):
            raise OSError("private stage is not one regular physical file")
        if not _snapshot_hardlink_publication_capable_v1(kernel, handle):
            raise OSError(
                "volume cannot exclude hard-link topology through publication")
        _snapshot_stage_v1("stage-created")
        offset = 0
        while offset < len(raw):
            chunk = raw[offset:offset + 1024 * 1024]
            buffer = ctypes.create_string_buffer(chunk)
            written = ctypes.c_uint32()
            if (not kernel.WriteFile(handle, buffer, len(chunk),
                                     ctypes.byref(written), None) or
                    written.value != len(chunk)):
                raise ctypes.WinError(ctypes.get_last_error())
            offset += written.value
        _snapshot_stage_v1("write-complete")
        if not kernel.FlushFileBuffers(handle):
            raise ctypes.WinError(ctypes.get_last_error())
        _snapshot_stage_v1("fsync-complete")
        if not kernel.SetFilePointerEx(handle, 0, None, 0):
            raise ctypes.WinError(ctypes.get_last_error())
        _snapshot_stage_v1("readback-start")
        observed = bytearray()
        while len(observed) <= len(raw):
            capacity = min(1024 * 1024, len(raw) + 1 - len(observed))
            buffer = ctypes.create_string_buffer(capacity)
            count = ctypes.c_uint32()
            if not kernel.ReadFile(
                    handle, buffer, capacity, ctypes.byref(count), None):
                raise ctypes.WinError(ctypes.get_last_error())
            if count.value == 0:
                break
            observed.extend(buffer.raw[:count.value])
        _snapshot_stage_v1("readback-eof")
        verified = _snapshot_handle_info_v1(kernel, handle)
        if (bytes(observed) != raw or
                not _snapshot_handle_regular_v1(verified, len(raw)) or
                (created.volume_serial, created.file_index_high,
                 created.file_index_low) !=
                (verified.volume_serial, verified.file_index_high,
                 verified.file_index_low)):
            raise OSError("private stage identity or exact bytes changed")
        _snapshot_stage_v1("before-publish")
        final_stage = _snapshot_handle_info_v1(kernel, handle)
        if (not _snapshot_handle_regular_v1(final_stage, len(raw)) or
                (created.volume_serial, created.file_index_high,
                 created.file_index_low) !=
                (final_stage.volume_serial, final_stage.file_index_high,
                 final_stage.file_index_low)):
            raise OSError("private stage changed immediately before publication")
        _snapshot_atomic_no_replace_v1(handle, target)
        published = True
    finally:
        if not published:
            try:
                _snapshot_delete_stage_v1(kernel, handle)
                delete_marked = True
            except OSError:
                pass
        if not kernel.CloseHandle(handle):
            if published:
                raise ctypes.WinError(ctypes.get_last_error())
        if not published and not delete_marked:
            raise OSError("private stage cleanup could not be identity-bound")


def export_snapshot(
        snapshot: object, destination: object, *, owned_root: object,
        output_format: str = "json", max_rows: int | None = None,
        max_bytes: int | None = None) -> dict:
    """Write one new export below an explicit isolated task-owned root."""
    value, population = _parse_diff_snapshot_v1(snapshot, "$snapshot")
    target, root = _export_destination_v1(destination, owned_root)
    if output_format == "json":
        if max_rows is not None or max_bytes is not None:
            _error("OE_EXPORT_BOUND_INVALID", "$export",
                   "canonical JSON export is complete and cannot be truncated")
        raw = canonical_json_v1(value)
        truncated = False
    elif output_format in ("table", "graph"):
        raw = _render_snapshot_projection_parsed_v1(
            value, population, output_format=output_format,
            max_rows=max_rows, max_bytes=max_bytes)
        truncated = json.loads(raw.decode("utf-8"))["truncated"]
    else:
        _error("OE_EXPORT_FORMAT_INVALID", "$.format",
               "export format must be json, table, or graph")
    try:
        _snapshot_stage_export_v1(raw, target)
    except FileExistsError:
        _error("OE_EXPORT_DESTINATION_EXISTS", "$.destination",
               "export destination became occupied")
    except OSError:
        _error("OE_EXPORT_WRITE_FAILED", "$.destination",
               "export could not be written and verified atomically")
    return {
        "schema": SNAPSHOT_EXPORT_SCHEMA, "snapshot_id": value["snapshot_id"],
        "format": output_format, "output_sha256": hashlib.sha256(raw).hexdigest(),
        "output_bytes": len(raw), "truncated": truncated,
        "decision_usable": not truncated,
        "authority_ceiling": "EXPLICIT_TASK_OWNED_DESTINATION_ONLY",
        "establishes": [],
    }


def _load_diff_snapshot_file_v1(path: pathlib.Path, label: str) -> dict:
    try:
        raw = _native_file(path, label, 16 * 1024 * 1024)
        value = _snapshot_decode_canonical_object_v1(raw, "OE_DIFF_SNAPSHOT_INVALID")
    except OperationalEvidenceError as exc:
        if exc.code == "OE_DIFF_SNAPSHOT_INVALID":
            raise
        _error("OE_DIFF_SNAPSHOT_INVALID", label,
               "snapshot input is unreadable or not a regular canonical file")
    return _validate_diff_snapshot_v1(value, label)


_snapshot_query_policy = _query_policy_module.SnapshotQueryPolicy(
    families=FAMILIES, states=STATES, snapshot_schema=SNAPSHOT_PAYLOAD_SCHEMA,
    status_schema=QUERY_STATUS_SCHEMA, result_schema=QUERY_RESULT_SCHEMA,
    why_schema=QUERY_WHY_SCHEMA, canonical_json=canonical_json_v1, error=_error)

def _snapshot_query_records_v1(snapshot: object) -> list[dict]:
    return _snapshot_query_policy._snapshot_query_records_v1(snapshot)


def evaluate_currentness(snapshot: dict) -> dict:
    return _snapshot_query_policy.evaluate_currentness(snapshot)


def query_family(snapshot: dict, family: str, current_only: bool=False) -> dict:
    return _snapshot_query_policy.query_family(snapshot, family, current_only)


def explain_history_why_v1(snapshot: dict, record_id: str) -> dict:
    return _snapshot_query_policy.explain_history_why_v1(snapshot, record_id)


def normalize_history_filters_v1(filters: object) -> dict:
    """Normalize a direct query filter or the exact HC-H2B one-ID request."""
    if type(filters) is not dict:
        _error("OE_QUERY_FILTER_INVALID", "$.filters", "must be an object")
    if filters.get("schema") == HISTORY_REQUEST_SCHEMA:
        if (set(filters) != {"schema", "route", "requirement", "evidence_ids"} or
                filters.get("route") != "QUERY_HISTORY_THEN_RESUME" or
                filters.get("requirement") != "REQUIRED" or
                type(filters.get("evidence_ids")) is not list or
                len(filters["evidence_ids"]) != 1 or
                type(filters["evidence_ids"][0]) is not str or
                not HISTORY_EVENT_ID_RE.fullmatch(filters["evidence_ids"][0])):
            _error("OE_QUERY_FILTER_INVALID", "$.filters",
                   "HC-H2B request must carry one canonical evidence identity")
        return {"event_ids": list(filters["evidence_ids"])}
    if not filters or not set(filters) <= HISTORY_FILTER_KEYS:
        _error("OE_QUERY_FILTER_INVALID", "$.filters",
               "at least one supported filter is required")
    normalized = {}
    for key in sorted(filters):
        values = filters[key]
        if (type(values) is not list or not values or
                any(type(item) is not str or not item for item in values)):
            _error("OE_QUERY_FILTER_INVALID", f"$.filters.{key}",
                   "filter values must be a non-empty string array")
        unique = sorted(set(values))
        if len(unique) != len(values):
            _error("OE_QUERY_FILTER_INVALID", f"$.filters.{key}",
                   "filter values must be unique")
        if key == "event_ids" and any(
                not HISTORY_EVENT_ID_RE.fullmatch(item) for item in unique):
            _error("OE_QUERY_FILTER_INVALID", f"$.filters.{key}",
                   "event identity is not canonical")
        normalized[key] = unique
    return normalized


def _history_request_v1(request: object) -> tuple[dict, int, int]:
    if (type(request) is not dict or
            set(request) != {"schema", "filters", "max_rows", "max_bytes"} or
            request.get("schema") != QUERY_SCHEMA):
        _error("OE_QUERY_FILTER_INVALID", "$query",
               "query request has the wrong schema or key set")
    filters = normalize_history_filters_v1(request["filters"])
    for key in ("max_rows", "max_bytes"):
        value = request[key]
        if type(value) is not int or value <= 0:
            _error("OE_QUERY_BOUND_INVALID", f"$.{key}",
                   "bound must be a finite positive integer")
    return filters, request["max_rows"], request["max_bytes"]


def _load_r39_query_contract_v1() -> tuple[types.ModuleType, pathlib.Path, bytes]:
    """Execute the exact fixed sibling R0027 verifier bytes as trusted source."""
    path = pathlib.Path(__file__).resolve().with_name("rotate-canonical-state.py")
    raw = _native_file(path, "$query.r39_contract", 512 * 1024)
    name = "_implementaudit_r39_query_contract_v1"
    module = types.ModuleType(name)
    module.__file__ = os.fspath(path)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        exec(compile(raw, os.fspath(path), "exec"), module.__dict__)
    except Exception:
        _error("OE_QUERY_R39_CONTRACT_INVALID", "$query.r39_contract",
               "exact R0027 query contract could not be loaded")
    finally:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
    if not all(hasattr(module, name) for name in (
            "RotationError", "verify_generation_manifest_v1",
            "load_governed_source_custody_v1",
            "load_canonical_generation_pointer_oid_v1",
            "load_canonical_generation_manifest_oid_v1",
            "verify_pointer_manifest_tuple_v1",
            "require_complete_pointer_receipt_marker_route_v1")):
        _error("OE_QUERY_R39_CONTRACT_INVALID", "$query.r39_contract",
               "exact R0027 query contract is incomplete")
    return module, path, raw


def _validate_query_manifest_v1(
        manifest: object, path: str, r39: types.ModuleType | None = None) -> dict:
    contract = r39 or _load_r39_query_contract_v1()[0]
    try:
        contract.verify_generation_manifest_v1(manifest)
    except contract.RotationError:
        _error("OE_QUERY_MANIFEST_INVALID", path,
               "canonical R0027 manifest verification failed")
    return manifest


def _require_r39_current_manifest_v1(
        r39: types.ModuleType, expected: dict) -> dict:
    """Bind one exact manifest to the live no-argument R0027 current selection."""
    try:
        live = r39.load_governed_source_custody_v1()
        pointer_oid = live.get("pointer_oid")
        marker_oid = live.get("marker_oid")
        if pointer_oid is None or marker_oid is None:
            raise r39.RotationError("current R0027 pointer route is incomplete")
        pointer = r39.load_canonical_generation_pointer_oid_v1(
            live["repo_path"], pointer_oid)
        manifest_oid = pointer["generation_manifest_oid"]
        observed = r39.load_canonical_generation_manifest_oid_v1(
            live["repo_path"], manifest_oid)
        r39.verify_pointer_manifest_tuple_v1(
            pointer=pointer, manifest=observed, manifest_oid=manifest_oid)
        r39.require_complete_pointer_receipt_marker_route_v1(
            live=live, receipt=live["receipt"], pointer=pointer,
            pointer_oid=pointer_oid, marker_oid=marker_oid)
    except r39.RotationError:
        _error("OE_QUERY_CURRENT_MANIFEST_INVALID", "$query.current_manifest",
               "live R0027 pointer/receipt/marker selection is not exact")
    if canonical_json_v1(observed) != canonical_json_v1(expected):
        _error("OE_QUERY_CURRENT_MANIFEST_INVALID", "$query.current_manifest",
               "supplied manifest is not the live R0027 current selection")
    return observed


def encode_query_cursor_v1(
        request: dict, manifest: dict, position: dict) -> str:
    filters, _rows, _bytes = _history_request_v1(request)
    _validate_query_manifest_v1(manifest, "$manifest")
    if (type(position) is not dict or set(position) != {"sequence", "event_id"} or
            type(position.get("sequence")) is not str or
            not HISTORY_SEQUENCE_RE.fullmatch(position["sequence"]) or
            type(position.get("event_id")) is not str or
            not HISTORY_EVENT_ID_RE.fullmatch(position["event_id"])):
        _error("OE_QUERY_CURSOR_POSITION_STALE", "$.requested_position",
               "cursor position is not canonical")
    body = {
        "schema": HISTORY_CURSOR_SCHEMA,
        "query_contract": HISTORY_QUERY_SCHEMA,
        "generation_id": manifest["generation_id"],
        "manifest_digest": manifest["manifest_digest"],
        "filters_sha256": hashlib.sha256(canonical_json_v1(filters)).hexdigest(),
        "requested_position": dict(position),
    }
    raw = canonical_json_v1(body)
    payload = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    return f"iaqcur-v1.{payload}.{hashlib.sha256(raw).hexdigest()}"


def decode_query_cursor_v1(
        cursor: str, request: dict, manifest: dict) -> dict:
    filters, _rows, _bytes = _history_request_v1(request)
    _validate_query_manifest_v1(manifest, "$manifest")
    if type(cursor) is not str:
        _error("OE_QUERY_CURSOR_DIGEST_INVALID", "$.cursor",
               "cursor is not text")
    parts = cursor.split(".")
    if len(parts) != 3 or parts[0] != "iaqcur-v1" or not re.fullmatch(
            r"[0-9a-f]{64}", parts[2]):
        _error("OE_QUERY_CURSOR_DIGEST_INVALID", "$.cursor",
               "cursor framing or checksum is malformed")
    try:
        raw = base64.b64decode(
            parts[1] + "=" * (-len(parts[1]) % 4), altchars=b"-_",
            validate=True)
    except (ValueError, TypeError):
        _error("OE_QUERY_CURSOR_DIGEST_INVALID", "$.cursor",
               "cursor payload is malformed")
    if hashlib.sha256(raw).hexdigest() != parts[2]:
        _error("OE_QUERY_CURSOR_DIGEST_INVALID", "$.cursor",
               "cursor checksum does not match its payload")
    body = decode_strict_json_bytes(raw, "history query cursor")
    if (type(body) is not dict or set(body) != {
            "schema", "query_contract", "generation_id", "manifest_digest",
            "filters_sha256", "requested_position"} or
            body.get("schema") != HISTORY_CURSOR_SCHEMA or
            body.get("query_contract") != HISTORY_QUERY_SCHEMA):
        _error("OE_QUERY_CURSOR_VERSION_MISMATCH", "$.cursor",
               "cursor schema or query contract is unsupported")
    if body.get("generation_id") != manifest["generation_id"]:
        _error("OE_QUERY_CURSOR_GENERATION_MISMATCH", "$.cursor",
               "cursor generation is not current")
    if body.get("manifest_digest") != manifest["manifest_digest"]:
        _error("OE_QUERY_CURSOR_MANIFEST_MISMATCH", "$.cursor",
               "cursor manifest is not current")
    if body.get("filters_sha256") != hashlib.sha256(
            canonical_json_v1(filters)).hexdigest():
        _error("OE_QUERY_CURSOR_FILTER_MISMATCH", "$.cursor",
               "cursor filters differ from this request")
    position = body.get("requested_position")
    if (type(position) is not dict or set(position) != {"sequence", "event_id"} or
            type(position.get("sequence")) is not str or
            not HISTORY_SEQUENCE_RE.fullmatch(position["sequence"]) or
            type(position.get("event_id")) is not str or
            not HISTORY_EVENT_ID_RE.fullmatch(position["event_id"])):
        _error("OE_QUERY_CURSOR_POSITION_STALE", "$.cursor.requested_position",
               "cursor position is not canonical")
    return body


def _history_manifests_v1(
        current_manifest: dict, load_predecessor,
        r39: types.ModuleType) -> list[dict]:
    current = _validate_query_manifest_v1(current_manifest, "$manifest", r39)
    manifests = [current]
    seen = {current["manifest_digest"]}
    expected = current.get("predecessor_manifest_digest")
    while expected is not None:
        if type(expected) is not str or not re.fullmatch(r"[0-9a-f]{64}", expected):
            _error("OE_QUERY_MANIFEST_INVALID", "$manifest.predecessor",
                   "predecessor digest is malformed")
        if expected in seen:
            _error("OE_QUERY_MANIFEST_INVALID", "$manifest.predecessor",
                   "predecessor chain contains a cycle")
        try:
            predecessor = load_predecessor(expected)
        except OperationalEvidenceError:
            raise
        except Exception:
            _error("OE_QUERY_MANIFEST_INVALID", "$manifest.predecessor",
                   "verified predecessor could not be loaded")
        predecessor = _validate_query_manifest_v1(
            predecessor, "$manifest.predecessor", r39)
        if predecessor["manifest_digest"] != expected:
            _error("OE_QUERY_MANIFEST_INVALID", "$manifest.predecessor",
                   "loader returned a foreign predecessor")
        if (predecessor.get("controller_id") != current.get("controller_id") or
                predecessor.get("claim_id") != current.get("claim_id") or
                predecessor.get("run_id") != current.get("run_id")):
            _error("OE_QUERY_MANIFEST_INVALID", "$manifest.predecessor",
                   "predecessor crossed controller, claim, or run custody")
        manifests.append(predecessor)
        seen.add(expected)
        expected = predecessor.get("predecessor_manifest_digest")
    return manifests


def _history_event_v1(manifest: dict, row: dict, load_segment) -> tuple[dict, bytes]:
    try:
        raw = load_segment(manifest, row)
    except OperationalEvidenceError:
        raise
    except Exception:
        _error("OE_QUERY_SEGMENT_INVALID", "$.segment",
               "referenced event segment could not be loaded")
    if type(raw) is not bytes or hashlib.sha256(raw).hexdigest() != (
            row["segment_digest"].removeprefix("sha256:")):
        _error("OE_QUERY_SEGMENT_INVALID", "$.segment",
               "referenced event segment digest differs")
    event = decode_strict_json_bytes(raw, "history event segment")
    if canonical_json_v1(event) != raw:
        _error("OE_QUERY_SEGMENT_INVALID", "$.segment",
               "event segment is not canonical")
    candidate = dict(event) if type(event) is dict else {}
    candidate.pop("event_id", None)
    expected_id = "iaevt-v1-" + hashlib.sha256(
        canonical_json_v1(candidate)).hexdigest()
    if (type(event) is not dict or
            event.get("schema_version") != HISTORY_EVENT_SCHEMA or
            event.get("event_id") != row["event_id"] or
            event.get("event_id") != expected_id or
            event.get("sequence") != row["sequence"] or
            event.get("record_kind") != row["record_kind"] or
            event.get("source_evidence_id") != row["source_evidence_id"] or
            event.get("generation_id") != manifest["generation_id"] or
            event.get("controller_id") != manifest.get("controller_id") or
            event.get("run_id") != manifest.get("run_id")):
        _error("OE_QUERY_SEGMENT_INVALID", "$.segment",
               "event segment crossed its verified manifest custody")
    return event, raw


def _history_matches_v1(event: dict, filters: dict) -> bool:
    fields = {
        "event_ids": "event_id", "record_kinds": "record_kind",
        "subject_ids": "subject_id", "source_evidence_ids": "source_evidence_id",
        "statuses": "status", "transitions": "transition"}
    return all(event.get(fields[key]) in values for key, values in filters.items())


def query_history_v1(
        request: dict, current_manifest: dict, cursor: str | None = None,
        *, load_segment, load_predecessor) -> dict:
    """Read only the verified predecessor chain under explicit finite bounds."""
    filters, max_rows, max_bytes = _history_request_v1(request)
    r39, r39_path, r39_raw = _load_r39_query_contract_v1()
    _validate_query_manifest_v1(current_manifest, "$manifest", r39)
    _require_r39_current_manifest_v1(r39, current_manifest)
    manifests = _history_manifests_v1(
        current_manifest, load_predecessor, r39)
    cursor_body = (decode_query_cursor_v1(cursor, request, current_manifest)
                   if cursor is not None else None)
    requested_position = (cursor_body["requested_position"]
                          if cursor_body is not None else None)
    population = []
    identities = set()
    for manifest in manifests:
        for row in manifest["events"]:
            identity = (row["sequence"], row["event_id"])
            if identity in identities:
                _error("OE_QUERY_MANIFEST_INVALID", "$.manifest.events",
                       "predecessor population repeats an event position")
            identities.add(identity)
            population.append((identity, manifest, row))
    population.sort(key=lambda item: item[0])
    if requested_position is not None:
        position_tuple = (
            requested_position["sequence"], requested_position["event_id"])
        if position_tuple not in identities:
            _error("OE_QUERY_CURSOR_POSITION_STALE", "$.cursor.requested_position",
                   "cursor position is absent from verified history")
    else:
        position_tuple = None
    rows = []
    row_bytes = 0
    truncated = False
    observed_start = None
    observed_end = None
    next_position = None
    metadata_fields = {
        "event_ids": "event_id", "record_kinds": "record_kind",
        "source_evidence_ids": "source_evidence_id"}
    for identity, manifest, row in population:
        if position_tuple is not None and identity <= position_tuple:
            continue
        if observed_start is None:
            observed_start = {"sequence": identity[0], "event_id": identity[1]}
        observed_end = {"sequence": identity[0], "event_id": identity[1]}
        if any(row[metadata_fields[key]] not in values
               for key, values in filters.items() if key in metadata_fields):
            continue
        event, raw = _history_event_v1(manifest, row, load_segment)
        if not _history_matches_v1(event, filters):
            continue
        if len(rows) >= max_rows or row_bytes + len(raw) > max_bytes:
            truncated = True
            break
        rows.append(event)
        row_bytes += len(raw)
        next_position = {"sequence": identity[0], "event_id": identity[1]}
    next_cursor = None
    if truncated and next_position is not None:
        next_cursor = encode_query_cursor_v1(
            request, current_manifest, next_position)
    result = {
        "schema": QUERY_RESULT_SCHEMA,
        "query_contract": HISTORY_QUERY_SCHEMA,
        "filters": filters,
        "rows": rows,
        "row_bytes": row_bytes,
        "max_rows": max_rows, "max_bytes": max_bytes,
        "coverage": {"start": observed_start, "end": observed_end},
        "requested_position": requested_position,
        "next_cursor": next_cursor,
        "truncated": truncated,
        "code": ("OE_QUERY_REQUIRES_BOUNDED_REVIEW" if truncated else "OK"),
        "decision_usable": cursor is None and not truncated,
        "authority_ceiling": "READ_ONLY_OBSERVATION",
        "establishes": [],
    }
    if _native_file(r39_path, "$query.r39_contract", 512 * 1024) != r39_raw:
        _error("OE_QUERY_R39_CONTRACT_CHANGED", "$query.r39_contract",
               "R0027 query contract changed during the bounded read")
    _require_r39_current_manifest_v1(r39, current_manifest)
    return result


def _load_selected_snapshot_v1() -> dict:
    native = collect_native_current()
    repository_root = pathlib.Path(native["repository"]["root"])
    run_root = repository_root.joinpath(
        *pathlib.PurePosixPath(native["claim"]["run_root"]).parts)
    snapshots = run_root / "operational-evidence" / "snapshots"
    raw = _snapshot_current_raw_v1(snapshots)
    if raw is None:
        _error("OE_SNAPSHOT_CURRENT_INVALID", "$snapshot.CURRENT",
               "no selected operational snapshot exists")
    current = _snapshot_validate_current_v1(raw, snapshots)
    payload_raw = _snapshot_read_regular_v1(
        snapshots / current["snapshot_id"] / "snapshot.json", snapshots,
        "OE_SNAPSHOT_CURRENT_INVALID")
    payload = _snapshot_decode_canonical_object_v1(
        payload_raw, "OE_SNAPSHOT_CURRENT_INVALID")
    if (payload.get("schema_version") != SNAPSHOT_PAYLOAD_SCHEMA or
            payload.get("snapshot_id") != current["snapshot_id"]):
        _error("OE_SNAPSHOT_CURRENT_INVALID", "$snapshot.snapshot",
               "selected snapshot identity or schema differs")
    return payload


def build_cli_parser_v1() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="validate, query, diff, and export R0038 operational evidence")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "canonicalize"):
        command = commands.add_parser(name)
        command.add_argument("input", type=pathlib.Path)
    commands.add_parser("status")
    query = commands.add_parser("query")
    query.add_argument("--family", required=True, choices=FAMILIES)
    query.add_argument("--current-only", action="store_true")
    query.add_argument("--max-rows", required=True, type=int)
    query.add_argument("--max-bytes", required=True, type=int)
    why = commands.add_parser("why")
    why.add_argument("record_id")
    diff = commands.add_parser("diff")
    diff.add_argument("before", type=pathlib.Path)
    diff.add_argument("after", type=pathlib.Path)
    export = commands.add_parser("export")
    export.add_argument("--destination", required=True, type=pathlib.Path)
    export.add_argument("--owned-root", required=True, type=pathlib.Path)
    export.add_argument("--format", choices=("json", "table", "graph"),
                        default="json")
    export.add_argument("--max-rows", type=int)
    export.add_argument("--max-bytes", type=int)
    return parser


def _validate_record(value):
    if type(value) is not dict:
        _error("OE_SCHEMA_INVALID", "$", "must be an object")
    if value.get("schema") != RECORD_SCHEMA:
        _error("OE_SCHEMA_UNSUPPORTED", "$.schema",
               f"unsupported operational-evidence schema: {value.get('schema')!r}")
    _object(value, "$", exact_keys=TOP_LEVEL_KEYS, required=TOP_LEVEL_KEYS)
    if value["aggregate"] not in AGGREGATES:
        _error("OE_SCHEMA_INVALID", "$.aggregate", "unsupported aggregate")
    if type(value["families"]) is not list or tuple(value["families"]) != FAMILIES:
        _error("OE_SCHEMA_INVALID", "$.families",
               "must preserve the six frozen families in canonical order")
    affected = _string_list(
        value["affected_families"], "$.affected_families", allowed=FAMILIES)
    if value["aggregate"] == "COMPLETE" and affected:
        _error("OE_SCHEMA_INVALID", "$.affected_families",
               "COMPLETE cannot name affected families")
    if value["aggregate"] != "COMPLETE" and not affected:
        _error("OE_SCHEMA_INVALID", "$.affected_families",
               "non-COMPLETE aggregate must name affected families")

    collections = (
        ("capability_declarations", {"supported", "reason_code"},
         {"supported", "reason_code"}),
        ("currentness_predicates", {"predicate", "input_sha256"},
         {"predicate", "input_sha256"}),
        ("entities", {"record_type", "required"},
         {"record_type", "required"}),
        ("relations", {"relation_type", "source_entity_id",
                       "target_entity_id", "confidence", "inference_rule"},
         {"relation_type", "source_entity_id", "target_entity_id",
          "confidence", "inference_rule"}),
        ("payload_records", {"media_type", "payload", "payload_sha256"},
         {"media_type", "payload", "payload_sha256"}),
    )
    all_ids = set()
    entities = set()
    required_current_families = set()
    for name, keys, required in collections:
        rows = value[name]
        if type(rows) is not list:
            _error("OE_SCHEMA_INVALID", f"$.{name}", "must be an array")
        for index, row in enumerate(rows):
            path = f"$.{name}[{index}]"
            state = _common_record(
                row, path, exact_keys=keys, required_extra=required)
            if row["id"] in all_ids:
                _error("OE_SCHEMA_INVALID", path, "record id must be unique")
            all_ids.add(row["id"])
            if name == "capability_declarations":
                if type(row["supported"]) is not bool:
                    _error("OE_SCHEMA_INVALID", f"{path}.supported",
                           "must be a boolean")
                _text(row["reason_code"], f"{path}.reason_code")
            elif name == "currentness_predicates":
                _text(row["predicate"], f"{path}.predicate")
                _digest(row["input_sha256"], f"{path}.input_sha256")
            elif name == "entities":
                record_type = row["record_type"]
                if type(record_type) is not str:
                    _error("OE_SCHEMA_INVALID", f"{path}.record_type",
                           "must be a string")
                expected_family = ENTITY_FAMILIES.get(record_type)
                if expected_family is None:
                    _error("OE_SCHEMA_INVALID", f"{path}.record_type",
                           "unsupported entity type")
                if expected_family != row["family"]:
                    _error("OE_CROSS_LAYER", path,
                           "entity type crossed its frozen projection family")
                if type(row["required"]) is not bool:
                    _error("OE_SCHEMA_INVALID", f"{path}.required",
                           "must be a boolean")
                entities.add(row["id"])
                if row["required"] and state == "CURRENT":
                    required_current_families.add(row["family"])
                if (value["aggregate"] == "COMPLETE" and row["required"] and
                        state != "CURRENT"):
                    _error("OE_STALE_RECORD", path,
                           "COMPLETE requires every required entity CURRENT")
            elif name == "relations":
                if row["relation_type"] not in RELATION_TYPES:
                    _error("OE_SCHEMA_INVALID", f"{path}.relation_type",
                           "unsupported relation type")
                _text(row["source_entity_id"], f"{path}.source_entity_id")
                _text(row["target_entity_id"], f"{path}.target_entity_id")
                if row["confidence"] not in ("mechanical", "declared", "inferred"):
                    _error("OE_SCHEMA_INVALID", f"{path}.confidence",
                           "unsupported confidence")
                if row["confidence"] == "inferred":
                    _text(row["inference_rule"], f"{path}.inference_rule")
                elif row["inference_rule"] is not None:
                    _error("OE_SCHEMA_INVALID", f"{path}.inference_rule",
                           "only inferred relations name an inference rule")
            elif name == "payload_records":
                _text(row["media_type"], f"{path}.media_type")
                normalized = canonical_payload_text(row["payload"])
                digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
                _digest(row["payload_sha256"], f"{path}.payload_sha256")
                if digest != row["payload_sha256"]:
                    _error("OE_PAYLOAD_DIGEST", f"{path}.payload_sha256",
                           "payload digest does not match canonical payload bytes")
                row["payload"] = normalized

    for index, relation in enumerate(value["relations"]):
        if (relation["source_entity_id"] not in entities or
                relation["target_entity_id"] not in entities):
            _error("OE_SCHEMA_INVALID", f"$.relations[{index}]",
                   "relation endpoint is not a retained entity")
    if (value["aggregate"] == "COMPLETE" and
            required_current_families != set(FAMILIES)):
        _error("OE_SCHEMA_INVALID", "$.entities",
               "COMPLETE must retain a required CURRENT entity for every family")
    return value


def load_operational_evidence(path: pathlib.Path):
    script_root = pathlib.Path(__file__).resolve().parent.parent
    schema_path = script_root / "references" / "operational-evidence-schema.json"
    try:
        schema_bytes = schema_path.read_bytes()
        input_bytes = path.read_bytes()
    except OSError:
        _error("OE_INPUT_UNREADABLE", "$", "input or schema cannot be read")
    schema = decode_strict_json_bytes(schema_bytes, "operational-evidence schema")
    _validate_schema_definition(schema)
    value = decode_strict_json_bytes(input_bytes, "operational-evidence input")
    return _validate_record(value), hashlib.sha256(
        canonical_json_v1(schema)).hexdigest()


def main() -> int:
    parser = build_cli_parser_v1()
    args = parser.parse_args()
    try:
        if args.command in ("validate", "canonicalize"):
            value, schema_sha256 = load_operational_evidence(args.input)
            canonical = canonical_json_v1(value)
            if args.command == "canonicalize":
                sys.stdout.buffer.write(canonical)
                return 0
            census = Counter(
                row["currentness"]["state"]
                for name in ("capability_declarations", "currentness_predicates",
                             "entities", "relations", "payload_records")
                for row in value[name])
            receipt = {
                "schema": VALIDATION_SCHEMA,
                "record_schema": RECORD_SCHEMA,
                "aggregate": value["aggregate"],
                "families": list(FAMILIES),
                "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
                "schema_sha256": schema_sha256,
                "fact_state_census": dict(sorted(census.items())),
            }
            sys.stdout.buffer.write(canonical_json_v1(receipt))
            return 0
        if args.command == "diff":
            before = _load_diff_snapshot_file_v1(args.before, "$.before")
            after = _load_diff_snapshot_file_v1(args.after, "$.after")
            sys.stdout.buffer.write(canonical_json_v1(
                diff_snapshots(before, after)))
            return 0
        snapshot = _load_selected_snapshot_v1()
        if args.command == "export":
            receipt = export_snapshot(
                snapshot, args.destination, owned_root=args.owned_root,
                output_format=args.format, max_rows=args.max_rows,
                max_bytes=args.max_bytes)
            sys.stdout.buffer.write(canonical_json_v1(receipt))
            return 0
        if args.command == "status":
            result = evaluate_currentness(snapshot)
        elif args.command == "why":
            result = explain_history_why_v1(snapshot, args.record_id)
        else:
            if (type(args.max_rows) is not int or args.max_rows <= 0 or
                    type(args.max_bytes) is not int or args.max_bytes <= 0):
                _error("OE_QUERY_BOUND_INVALID", "$query",
                       "query bounds must be finite positive integers")
            result = query_family(
                snapshot, args.family, current_only=args.current_only)
            retained = []
            size = 0
            truncated = False
            for row in result["rows"]:
                row_size = len(canonical_json_v1(row))
                if len(retained) >= args.max_rows or size + row_size > args.max_bytes:
                    truncated = True
                    break
                retained.append(row)
                size += row_size
            result.update({
                "rows": retained, "row_bytes": size,
                "max_rows": args.max_rows, "max_bytes": args.max_bytes,
                "truncated": truncated,
                "code": ("OE_QUERY_REQUIRES_BOUNDED_REVIEW"
                         if truncated else "OK"),
                "decision_usable": not truncated,
            })
        sys.stdout.buffer.write(canonical_json_v1(result))
        return 0
    except OperationalEvidenceError as exc:
        sys.stderr.buffer.write(canonical_json_v1(exc.receipt()))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
