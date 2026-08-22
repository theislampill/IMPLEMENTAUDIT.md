#!/usr/bin/env python3
"""Strict canonical loader for the R0038 operational-evidence substrate."""
from __future__ import annotations

import argparse
import ast
import datetime
import decimal
import hashlib
import importlib.util
import json
import math
import os
import pathlib
import platform
import re
import stat
import subprocess
import sys
import urllib.error
import urllib.request
from collections import Counter


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


def _string_list(value, path, *, allowed=None, unique=True):
    if type(value) is not list:
        _error("OE_SCHEMA_INVALID", path, "must be an array")
    for index, item in enumerate(value):
        _text(item, f"{path}[{index}]")
        if allowed is not None and item not in allowed:
            _error("OE_SCHEMA_INVALID", f"{path}[{index}]", "unsupported value")
    if unique and len(set(value)) != len(value):
        _error("OE_SCHEMA_INVALID", path, "must not contain duplicates")
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


def _native_graph_projection(raw):
    compiler_path = pathlib.Path(__file__).resolve().with_name("compile-work-graph.py")
    compiler_raw = _native_file(
        compiler_path, "$native.work_graph_compiler", 256 * 1024)
    spec = importlib.util.spec_from_file_location(
        "_implementaudit_native_work_graph_compiler", compiler_path)
    if spec is None or spec.loader is None:
        _error("OE_NATIVE_CURRENT_GRAPH", "$native.WORK_GRAPH",
               "canonical HC-H4 compiler cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        projection = module.compile_frontier_projection(raw)
    except Exception as exc:
        _error("OE_NATIVE_CURRENT_GRAPH", "$native.WORK_GRAPH",
               f"canonical HC-H4 compiler rejected WORK_GRAPH: {exc}")
    if (type(projection) is not dict or not projection.get("active") or
            not projection.get("ready") or not (
                projection.get("writer_holds") or projection.get("resource_holds"))):
        _error("OE_NATIVE_CURRENT_MISSING", "$native.WORK_GRAPH.frontier",
               "WORK_GRAPH omits ACTIVE, READY, or declared hold facts")
    return projection, hashlib.sha256(compiler_raw).hexdigest()


def _native_predecessor(repo, controller, claim, run_id, generation, token):
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
        if fields[1] != controller or fields[3] != claim or fields[10] != expected_generation:
            _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt.predecessor",
                   "v2 predecessor is foreign to current custody")
    elif raw.startswith(b"implementaudit.continuity-receipt.v3\t"):
        fields = _native_exact_tsv(
            raw, "implementaudit.continuity-receipt.v3", 18,
            "$native.receipt.predecessor")
        if (fields[1] != controller or fields[2] != claim or fields[3] != run_id or
                fields[4] != expected_generation):
            _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt.predecessor",
                   "v3 predecessor is foreign to current custody")
    else:
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.receipt.predecessor",
               "receipt predecessor schema is unsupported")


def _native_route(repo, controller, claim, run_root, generation, receipt):
    ref = f"refs/implementaudit/route-decisions/{controller}"
    oid = _native_ref_oid(repo, ref, "$native.route.ref")
    raw = _native_blob(repo, oid, "$native.route")
    if not raw.endswith(b"\n") or b"\n" in raw[:-1] or b"\r" in raw:
        _error("OE_NATIVE_CURRENT_ROUTE", "$native.route",
               "R0033 route record bytes are malformed")
    value = decode_strict_json_bytes(raw[:-1], "R0033 route record")
    validate_identity_json_v1(value)
    base_keys = {
        "schema", "predicate_version", "controller_id", "claim_id",
        "explicit_run_root", "continuity_generation", "continuity_receipt",
        "host_id", "host_session_id", "host_binding_generation",
        "host_correlation_id", "boundary", "scope", "action", "evidence",
        "inputs", "package", "child_source", "decision", "classification",
        "invalidators", "expiry_fingerprint", "expires_on",
        "predecessor_record_oid", "route_transaction_id", "obligation_id",
        "route_state", "child_lifecycle_owned", "consumed_record_oid",
        "record_identity"}
    allowed = [base_keys, base_keys | {"history_query"}, base_keys | {"lifecycle"},
               base_keys | {"history_query", "lifecycle"}]
    if type(value) is not dict or set(value) not in allowed:
        _error("OE_NATIVE_CURRENT_ROUTE", "$native.route",
               "R0033 route record field population is malformed")
    expected_raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False).encode("utf-8") + b"\n"
    if raw != expected_raw:
        _error("OE_NATIVE_CURRENT_BYTES", "$native.route",
               "R0033 route record bytes are not canonical")
    expires = [
        "action-completion", "next-action-change", "scope-change",
        "read-set-change", "host-binding-generation-change",
        "continuity-receipt-change", "package-identity-change",
        "child-source-identity-change", "owner-evidence-change",
        "authority-evidence-change", "dependency-evidence-change",
        "effect-evidence-change", "contradiction-or-invalidation",
        "scope-expansion"]
    if (value.get("schema") != "implementaudit.route-decision.v1" or
            value.get("predicate_version") != "R0033.route-predicate.v1" or
            value.get("controller_id") != controller or value.get("claim_id") != claim or
            _native_resolved_path(value.get("explicit_run_root"),
                                  "$native.route.explicit_run_root") != run_root or
            value.get("continuity_generation") != generation or
            value.get("continuity_receipt") != receipt or
            value.get("decision") not in {"PENDING", "NOT_REQUIRED", "REQUIRED"} or
            value.get("classification") not in {
                "MECHANICALLY_REQUIRED", "MECHANICALLY_NOT_REQUIRED",
                "JUDGEMENT_REQUIRED"} or value.get("expires_on") != expires or
            type(value.get("invalidators")) is not list or
            len(value["invalidators"]) != len(set(value["invalidators"])) or
            not all(type(item) is str and item for item in value["invalidators"]) or
            type(value.get("route_transaction_id")) is not str or
            not re.fullmatch(r"sha256:[0-9a-f]{64}", value["route_transaction_id"])):
        _error("OE_NATIVE_CURRENT_ROUTE", "$native.route",
               "R0033 route record is stale, foreign, or malformed")
    lifecycle = value.get("lifecycle")
    if value["decision"] == "REQUIRED":
        allowed_states = {"UNSATISFIED"} if lifecycle is None else {
            "OPEN", "RETURNED", "SATISFIED"}
        if (value.get("route_state") not in allowed_states or
                type(value.get("obligation_id")) is not str or
                not value["obligation_id"]):
            _error("OE_NATIVE_CURRENT_ROUTE", "$native.route",
                   "required R0033 route has no exact obligation state")
    elif value.get("route_state") is not None or value.get("obligation_id") is not None:
        _error("OE_NATIVE_CURRENT_ROUTE", "$native.route",
               "non-required R0033 route owns an obligation")
    if value.get("child_lifecycle_owned") is not (lifecycle is not None):
        _error("OE_NATIVE_CURRENT_ROUTE", "$native.route.lifecycle",
               "R0033 lifecycle ownership is contradictory")
    if lifecycle is not None and (
            type(lifecycle) is not dict or lifecycle.get("state") != value["route_state"]):
        _error("OE_NATIVE_CURRENT_ROUTE", "$native.route.lifecycle",
               "R0033 lifecycle state is malformed")
    for name in ("predecessor_record_oid", "consumed_record_oid"):
        candidate = value.get(name)
        if candidate is not None and (
                type(candidate) is not str or not re.fullmatch(r"[0-9a-f]{40}", candidate)):
            _error("OE_NATIVE_CURRENT_ROUTE", f"$native.route.{name}",
                   "R0033 route object identity is malformed")
    base = {key: item for key, item in value.items() if key != "record_identity"}
    identity = "sha256:" + hashlib.sha256(canonical_json_v1(base)).hexdigest()
    if value.get("record_identity") != identity:
        _error("OE_NATIVE_CURRENT_ROUTE", "$native.route.record_identity",
               "R0033 route record identity is stale")
    return {
        "ref": ref, "record_oid": oid, "record_identity": identity,
        "decision": value["decision"], "classification": value["classification"],
        "route_transaction_id": value["route_transaction_id"],
        "obligation_id": value["obligation_id"], "route_state": value["route_state"],
    }


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
    projection, compiler_sha256 = _native_graph_projection(graph_raw)
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
    _native_predecessor(
        source_repository, controller, claim, run_id, generation,
        receipt_fields[17])

    marker_ref = f"refs/implementaudit/current-generation-migrations/{controller}"
    marker_oid = _native_ref_oid(
        source_repository, marker_ref, "$native.marker.ref")
    marker = _native_exact_tsv(
        _native_blob(source_repository, marker_oid, "$native.marker"),
        "implementaudit.current-generation-migration.v1", 10, "$native.marker")
    if marker != [
            "implementaudit.current-generation-migration.v1", controller, claim,
            run_id, generation, pointer_ref,
            "implementaudit.state-generation-pointer.v1", receipt_ref,
            receipt_oid, "true"]:
        _error("OE_NATIVE_CURRENT_RECEIPT", "$native.marker",
               "permanent migration marker is stale or foreign")
    route = _native_route(
        source_repository, controller, claim, run_root, generation, receipt)

    ref_fence = {
        controller_ref: controller_oid, invalidation_ref: invalidation_oid,
        pointer_ref: pointer_oid, receipt_ref: receipt_oid, marker_ref: marker_oid,
        route["ref"]: route["record_oid"]}
    file_fence = {
        run_root / ".claimed": claimed_raw, run_root / ".controller": sentinel_raw,
        state_path: state_raw, roadmap_path: roadmap_raw, graph_path: graph_raw}
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
    parser = argparse.ArgumentParser(
        description="validate and canonicalize R0038 operational evidence")
    parser.add_argument("command", choices=("validate", "canonicalize"))
    parser.add_argument("input", type=pathlib.Path)
    args = parser.parse_args()
    try:
        value, schema_sha256 = load_operational_evidence(args.input)
        canonical = canonical_json_v1(value)
        if args.command == "canonicalize":
            sys.stdout.buffer.write(canonical)
        else:
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
    except OperationalEvidenceError as exc:
        sys.stderr.buffer.write(canonical_json_v1(exc.receipt()))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
