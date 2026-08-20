#!/usr/bin/env python3
"""Strict canonical loader for the R0038 operational-evidence substrate."""
from __future__ import annotations

import argparse
import ast
import decimal
import hashlib
import json
import math
import os
import pathlib
import platform
import subprocess
import sys
from collections import Counter


RECORD_SCHEMA = "implementaudit-operational-evidence-v1"
VALIDATION_SCHEMA = "implementaudit-operational-evidence-validation-v1"
SCHEMA_DEFINITION = "implementaudit-operational-evidence-schema-v1"
REPOSITORY_COLLECTION_SCHEMA = "implementaudit-repository-collection-v1"
STATIC_RECEIPT_SCHEMA = "implementaudit-static-receipt-v1"
STATIC_NORMALIZED_SCHEMA = "implementaudit-static-normalized-v1"
STATIC_NORMALIZED_SET_SCHEMA = "implementaudit-static-normalized-set-v1"
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


def canonical_json_v1(value) -> bytes:
    """UTF-8 JSON, sorted object keys, declared array order, no whitespace."""
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
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    try:
        return subprocess.run(
            ["git", "-C", os.fspath(root), *args], check=True,
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
    file_bytes = {}
    file_error = False
    for index, relative in enumerate(paths):
        pure = _safe_relative_path(relative, f"$repository.files[{index}]")
        path = root.joinpath(*pure.parts)
        try:
            if path.is_symlink():
                data = os.readlink(path).encode("utf-8")
                file_type = "symlink"
            elif path.is_file():
                data = path.read_bytes()
                file_type = "file"
            else:
                file_error = True
                diagnostics["errors"].append(f"tracked-path-unreadable:{relative}")
                facts.append({
                    "kind": "FILE_UNREADABLE_OBSERVATION", "path": relative,
                    "state": "STALE", "provenance": {
                        "method": "git-ls-files+working-tree-read",
                        "commit": commit, "tree": tree,
                    },
                })
                continue
        except (OSError, UnicodeError):
            file_error = True
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
    facts.sort(key=lambda row: canonical_json_v1(row))
    static_invocations.sort(key=lambda row: canonical_json_v1(row))
    for values in diagnostics.values():
        values.sort()
    return {
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


def _validate_static_receipt(value):
    _object(
        value, "$static", exact_keys={
            "schema", "outcome", "invalidators", "collector", "target", "scope",
            "diagnostics", "facts"},
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
            _object(
                mapping, f"{path}.mapping", exact_keys={
                    "work_node_id", "relation_type", "effect"}, required={
                    "work_node_id", "relation_type", "effect"})
            _text(mapping["work_node_id"], f"{path}.mapping.work_node_id")
            if mapping["relation_type"] not in (
                    "RESOURCE", "READ", "TARGET", "EVIDENCE"):
                _error("OE_STATIC_AUTHORITY", f"{path}.mapping.relation_type",
                       "mapping must be an explicit governed relation")
            if mapping["effect"] not in ("NONE", "INVALIDATE_EVIDENCE"):
                _error("OE_STATIC_AUTHORITY", f"{path}.mapping.effect",
                       "mapping effect exceeds selective invalidation")
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
    normalized = {
        "schema": STATIC_NORMALIZED_SCHEMA,
        "normalization_identity": "canonical_json_v1",
        "outcome": outcome,
        "invalidators": sorted(invalidators),
        "qualification": {
            "collector": dict(collector), "target": dict(target),
            "scope": {**scope, "supported": list(supported),
                      "unsupported": list(unsupported)},
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
