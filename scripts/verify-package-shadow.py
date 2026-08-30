#!/usr/bin/env python3
"""Non-authoritative package-verification shadow orchestrator."""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import signal
import shlex
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any


PASS = "PASS"
FAIL = "FAIL"
BLOCKED = "BLOCKED_BY_FAILED_DEPENDENCY"
NOT_APPLICABLE = "SKIPPED_NOT_APPLICABLE"
INFRASTRUCTURE_ERROR = "INFRASTRUCTURE_ERROR"
CHECKPOINT_SCHEMA = "implementaudit.verify-package-shadow.checkpoint.v2"
ENGINE_SEMANTICS = "implementaudit.verify-package-shadow.keep-going.v2"


class RunOptions:
    def __init__(
        self,
        repo_root: Path,
        output_dir: Path,
        timeout_seconds: float,
        mode: str,
        checkpoint_dir: Path | None = None,
        environment: dict[str, str] | None = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.output_dir = Path(output_dir)
        self.timeout_seconds = timeout_seconds
        self.mode = mode
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir is not None else None
        self.environment = dict(environment or {})


class CheckRecord:
    def __init__(
        self,
        *,
        check_id: str,
        order: int,
        status: str,
        duration_seconds: float = 0.0,
        exit_code: int | None = None,
        blocked_by: list[str] | None = None,
        detail: str = "",
        stdout_path: str = "",
        stderr_path: str = "",
        execution_source: str = "EXECUTED",
        result_fingerprint: str = "",
    ) -> None:
        self.check_id = check_id
        self.order = order
        self.status = status
        self.duration_seconds = duration_seconds
        self.exit_code = exit_code
        self.blocked_by = blocked_by or []
        self.detail = detail
        self.stdout_path = stdout_path
        self.stderr_path = stderr_path
        self.execution_source = execution_source
        self.result_fingerprint = result_fingerprint

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "blocked_by": list(self.blocked_by),
            "check_id": self.check_id,
            "detail": self.detail,
            "duration_seconds": round(self.duration_seconds, 6),
            "execution_source": self.execution_source,
            "exit_code": self.exit_code,
            "order": self.order,
            "result_fingerprint": self.result_fingerprint,
            "status": self.status,
            "stderr_path": self.stderr_path,
            "stdout_path": self.stdout_path,
        }


class RunReport:
    def __init__(
        self,
        *,
        mode: str,
        checks: list[CheckRecord],
        run_id: str,
        checkpoints_reused: list[str] | None = None,
        invalidation_reasons: dict[str, list[str]] | None = None,
        checkpoint_validation_seconds: float = 0.0,
        registry_sha256: str = "",
        canonical_verifier_sha256: str | None = None,
    ) -> None:
        self.mode = mode
        self.checks = sorted(checks, key=lambda item: item.order)
        self.run_id = run_id
        self.authority = "NONE"
        self.checkpoints_reused = list(checkpoints_reused or [])
        self.invalidation_reasons = dict(invalidation_reasons or {})
        self.checkpoints_invalidated = list(self.invalidation_reasons)
        self.checks_executed = [
            c.check_id for c in self.checks if c.execution_source == "EXECUTED"
        ]
        self.checkpoint_validation_seconds = checkpoint_validation_seconds
        self.registry_sha256 = registry_sha256
        self.canonical_verifier_sha256 = canonical_verifier_sha256
        self.pass_checks = [c.check_id for c in self.checks if c.status == PASS]
        self.primary_failures = [c.check_id for c in self.checks if c.status == FAIL]
        self.blocked_checks = [c.check_id for c in self.checks if c.status == BLOCKED]
        self.blocked_dependency_map = {
            c.check_id: list(c.blocked_by) for c in self.checks if c.status == BLOCKED
        }
        self.skipped_not_applicable = [
            c.check_id for c in self.checks if c.status == NOT_APPLICABLE
        ]
        self.infrastructure_errors = [
            c.check_id for c in self.checks if c.status == INFRASTRUCTURE_ERROR
        ]
        self.earliest_failure = next(
            (c.check_id for c in self.checks if c.status == FAIL), None
        )
        self.complete_safe_failure_frontier = not self.infrastructure_errors

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "authority": self.authority,
            "blocked_checks": list(self.blocked_checks),
            "blocked_dependency_map": dict(self.blocked_dependency_map),
            "checks": [check.to_json_dict() for check in self.checks],
            "checks_executed": list(self.checks_executed),
            "checkpoint_validation_seconds": round(
                self.checkpoint_validation_seconds, 6
            ),
            "checkpoints_invalidated": list(self.checkpoints_invalidated),
            "checkpoints_reused": list(self.checkpoints_reused),
            "complete_safe_failure_frontier": self.complete_safe_failure_frontier,
            "canonical_verifier_sha256": self.canonical_verifier_sha256,
            "engine_semantics": ENGINE_SEMANTICS,
            "earliest_failure": self.earliest_failure,
            "infrastructure_errors": list(self.infrastructure_errors),
            "invalidation_reasons": dict(self.invalidation_reasons),
            "mode": self.mode,
            "pass_checks": list(self.pass_checks),
            "primary_failures": list(self.primary_failures),
            "registry_sha256": self.registry_sha256,
            "run_id": self.run_id,
            "schema": "implementaudit.verify-package-shadow.report.v1",
            "skipped_not_applicable": list(self.skipped_not_applicable),
        }


def extract_canonical_commands(
    text: str, *, first_command: str
) -> list[tuple[int, tuple[str, ...]]]:
    """Return canonical top-level Bash invocations from the registry boundary."""
    commands: list[tuple[int, tuple[str, ...]]] = []
    logical = ""
    logical_start = 0
    started = False
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        stripped = raw_line.strip()
        if not logical:
            logical_start = line_number
        logical += stripped[:-1].rstrip() + " " if stripped.endswith("\\") else stripped
        if stripped.endswith("\\"):
            continue
        if logical.startswith("bash "):
            argv = tuple(shlex.split(logical, posix=True))
            if len(argv) >= 2 and argv[1] == first_command:
                started = True
            if started:
                commands.append((logical_start, argv))
        logical = ""
    return commands


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _derive_check_id(argv: list[str]) -> str:
    path = Path(argv[1]).as_posix()
    if path.startswith("tests/") and path.endswith(".test.sh"):
        prefix = "test"
        name = Path(path).name[: -len(".test.sh")]
    elif path.startswith("scripts/") and path.endswith(".sh"):
        prefix = "script"
        name = Path(path).stem
    else:
        prefix = "command"
        name = Path(path).name
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{prefix}.{slug}"


def materialize_registry(config: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Expand a digest-bound compact config into the exact check population."""
    canonical = config.get("canonical", {})
    canonical_path = repo_root / str(canonical.get("path", ""))
    text = canonical_path.read_text(encoding="utf-8")
    commands = [
        list(argv)
        for _, argv in extract_canonical_commands(
            text, first_command=str(canonical.get("first_command", ""))
        )
    ]
    population_digest = hashlib.sha256(_canonical_json_bytes(commands)).hexdigest()
    if canonical.get("command_population_sha256") != population_digest:
        raise ValueError("canonical command population digest mismatch")

    composite = dict(config.get("composite", {}))
    composite_check = {
        "id": composite.get("id", "canonical.inline-preflight"),
        "kind": "canonical_prefix",
        "order": 0,
        "argv": [],
        "dependencies": [],
        "implementation_sources": [str(canonical.get("path", ""))],
        "input_contract": composite.get(
            "input_contract", {"mode": "tracked_tree"}
        ),
        "output_contract": composite.get(
            "output_contract", {"mode": "explicit", "paths": []}
        ),
        "material_tools": composite.get("material_tools", ["bash"]),
        "environment": composite.get("environment", []),
        "checkpoint_policy": composite.get(
            "checkpoint_policy", {"mode": "disabled"}
        ),
    }
    checks: list[dict[str, Any]] = [composite_check]
    overrides = config.get("overrides", {})
    seen: set[str] = {str(composite_check["id"])}
    for order, argv in enumerate(commands, 1):
        check_id = _derive_check_id(argv)
        if check_id in seen:
            raise ValueError(f"derived duplicate check id: {check_id}")
        seen.add(check_id)
        override = dict(overrides.get(check_id, {}))
        check = {
            "id": check_id,
            "kind": "command",
            "order": order,
            "argv": argv,
            "dependencies": override.pop("dependencies", []),
            "implementation_sources": override.pop(
                "implementation_sources", [argv[1]]
            ),
            "input_contract": override.pop(
                "input_contract", {"mode": "tracked_tree"}
            ),
            "output_contract": override.pop(
                "output_contract", {"mode": "explicit", "paths": []}
            ),
            "material_tools": override.pop("material_tools", [argv[0]]),
            "environment": override.pop("environment", []),
            "checkpoint_policy": override.pop(
                "checkpoint_policy", {"mode": "disabled"}
            ),
        }
        check.update(override)
        checks.append(check)

    return {
        "schema": config.get("schema"),
        "authority": config.get("authority"),
        "canonical": canonical,
        "execution_environment": config.get("execution_environment", {}),
        "checks": checks,
    }


def validate_registry(registry: dict[str, Any], repo_root: Path) -> list[str]:
    """Return deterministic fail-closed registry diagnostics."""
    errors: list[str] = []
    if registry.get("schema") != "implementaudit.verify-package-shadow.registry.v1":
        errors.append("unsupported registry schema")
    if registry.get("authority") != "NONE":
        errors.append("registry authority must be NONE")

    canonical = registry.get("canonical")
    checks = registry.get("checks")
    if not isinstance(canonical, dict):
        return errors + ["canonical registry object is required"]
    if not isinstance(checks, list) or not checks:
        return errors + ["non-empty checks array is required"]

    canonical_rel = canonical.get("path")
    first_command = canonical.get("first_command")
    if not isinstance(canonical_rel, str) or not canonical_rel:
        errors.append("canonical path is required")
        canonical_path = repo_root / "__missing_canonical__"
    else:
        canonical_path = repo_root / canonical_rel
    if not isinstance(first_command, str) or not first_command:
        errors.append("canonical first_command is required")

    canonical_text = ""
    if not canonical_path.is_file():
        errors.append("canonical verifier is missing")
    else:
        canonical_bytes = canonical_path.read_bytes()
        actual_digest = hashlib.sha256(canonical_bytes).hexdigest()
        if canonical.get("sha256") != actual_digest:
            errors.append("canonical verifier digest mismatch")
        try:
            canonical_text = canonical_bytes.decode("utf-8")
        except UnicodeDecodeError:
            errors.append("canonical verifier is not UTF-8")

    ids: list[str] = []
    id_set: set[str] = set()
    evidence_names: dict[str, str] = {}
    for check in checks:
        if not isinstance(check, dict):
            errors.append("every check must be an object")
            continue
        check_id = check.get("id")
        if not isinstance(check_id, str) or not check_id:
            errors.append("every check requires a non-empty id")
            continue
        if check_id in id_set:
            errors.append(f"duplicate check id: {check_id}")
        ids.append(check_id)
        id_set.add(check_id)
        evidence_name = _evidence_name(check_id)
        if evidence_name in evidence_names and evidence_names[evidence_name] != check_id:
            errors.append(f"checkpoint filename collision: {evidence_name}")
        else:
            evidence_names[evidence_name] = check_id

    orders = [check.get("order") for check in checks if isinstance(check, dict)]
    if orders != list(range(len(checks))):
        errors.append("check orders must be contiguous from zero")

    for check in checks:
        if not isinstance(check, dict) or not isinstance(check.get("id"), str):
            continue
        dependencies = check.get("dependencies", [])
        if not isinstance(dependencies, list) or not all(
            isinstance(item, str) for item in dependencies
        ):
            errors.append(f"{check['id']} dependencies must be a string array")
            continue
        for dependency in dependencies:
            if dependency not in id_set:
                errors.append(f"{check['id']} has unknown dependency: {dependency}")

    graph = {
        check["id"]: tuple(check.get("dependencies", []))
        for check in checks
        if isinstance(check, dict)
        and isinstance(check.get("id"), str)
        and isinstance(check.get("dependencies", []), list)
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for dependency in graph.get(node, ()):
            if dependency in graph and visit(dependency):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    if any(visit(node) for node in graph if node not in visited):
        errors.append("dependency graph contains a cycle")

    if canonical_text and isinstance(first_command, str) and first_command:
        extracted = [
            list(argv)
            for _, argv in extract_canonical_commands(
                canonical_text, first_command=first_command
            )
        ]
        registered = [
            check.get("argv")
            for check in checks
            if isinstance(check, dict) and check.get("kind") == "command"
        ]
        if registered != extracted:
            errors.append("canonical command population mismatch")
        first_line = next(
            (
                line
                for line, argv in extract_canonical_commands(
                    canonical_text, first_command=first_command
                )
                if len(argv) >= 2 and argv[1] == first_command
            ),
            len(canonical_text.splitlines()) + 1,
        )
        static_exports: dict[str, str] = {}
        for line in canonical_text.splitlines()[: first_line - 1]:
            match = re.fullmatch(r"export ([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)", line)
            if match:
                static_exports[match.group(1)] = match.group(2)
        if registry.get("execution_environment", {}) != static_exports:
            errors.append("canonical execution environment mismatch")

    return errors


def _tool_available(tool: str, repo_root: Path) -> bool:
    candidate = Path(tool)
    if candidate.is_absolute():
        return candidate.is_file()
    if "/" in tool or "\\" in tool:
        return (repo_root / candidate).is_file()
    return resolve_tool(tool) is not None


def resolve_tool(tool: str) -> str | None:
    """Resolve material tools without accidentally selecting Windows WSL bash."""
    candidate = Path(tool)
    if candidate.is_absolute():
        return str(candidate) if candidate.is_file() else None
    if tool == "bash" and os.name == "nt":
        configured = os.environ.get("IMPLEMENTAUDIT_GIT_BASH", "")
        candidates = [
            configured,
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files\Git\usr\bin\bash.exe",
        ]
        for value in candidates:
            if value and Path(value).is_file():
                return value
        return None
    return shutil.which(tool)


def build_canonical_prefix(text: str, *, first_command: str) -> str:
    """Extract the exact approved inline prefix with only cwd binding replaced."""
    commands = extract_canonical_commands(text, first_command=first_command)
    if not commands:
        raise ValueError("canonical first command boundary was not found")
    boundary_line = commands[0][0]
    lines = text.splitlines()[: boundary_line - 1]
    root_bindings = [index for index, line in enumerate(lines) if line.startswith("repo_root=")]
    if len(root_bindings) != 1:
        raise ValueError("canonical prefix must contain exactly one repo_root binding")
    lines[root_bindings[0]] = 'repo_root="$(pwd -P)"'
    lines.append("printf 'verify-package-shadow: composite preflight ok\\n'")
    return "\n".join(lines) + "\n"


def _evidence_name(check_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", check_id)


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _path_entry(path: Path, repo_root: Path) -> dict[str, Any]:
    try:
        display = path.relative_to(repo_root).as_posix()
    except ValueError:
        display = str(path.resolve())
    try:
        if path.is_symlink():
            stat = path.lstat()
            return {
                "kind": "symlink",
                "mode": stat.st_mode & 0o777,
                "path": display,
                "target": os.readlink(path),
            }
        if path.is_file():
            data = path.read_bytes()
            stat = path.stat()
            return {
                "bytes": len(data),
                "kind": "file",
                "mode": stat.st_mode & 0o777,
                "path": display,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        if path.is_dir():
            return {"kind": "directory", "path": display}
        return {"kind": "missing", "path": display}
    except OSError as exc:
        return {"detail": str(exc), "kind": "unreadable", "path": display}


def _manifest_entries_reusable(entries: list[dict[str, Any]]) -> bool:
    return not any(
        entry.get("kind") in {"invalid-pattern", "symlink", "unreadable"}
        for entry in entries
    )


def _explicit_manifest(paths: list[Any], repo_root: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for raw in paths:
        if not isinstance(raw, str) or not raw:
            entries.append({"kind": "invalid-pattern", "pattern": repr(raw)})
            continue
        candidate = Path(raw)
        pattern = str(candidate if candidate.is_absolute() else repo_root / candidate)
        has_magic = glob.has_magic(pattern)
        matches = sorted(Path(item) for item in glob.glob(pattern, recursive=True))
        if not matches and not has_magic:
            matches = [Path(pattern)]
        if not matches:
            entries.append({"kind": "zero-match", "pattern": raw})
            continue
        for path in matches:
            entries.append(_path_entry(path, repo_root))
            if path.is_dir() and not path.is_symlink():
                try:
                    descendants = sorted(path.rglob("*"))
                except OSError as exc:
                    entries.append(
                        {
                            "detail": str(exc),
                            "kind": "unreadable",
                            "path": str(path),
                        }
                    )
                else:
                    entries.extend(
                        _path_entry(descendant, repo_root)
                        for descendant in descendants
                    )
    return {"mode": "explicit", "entries": entries}


def _tracked_tree_manifest(repo_root: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=repo_root,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return {
            "mode": "tracked_tree",
            "error": str(exc),
            "reusable": False,
        }
    if completed.returncode != 0:
        return {
            "mode": "tracked_tree",
            "error": "git ls-files failed",
            "reusable": False,
        }
    paths = [
        repo_root / raw.decode("utf-8", "surrogateescape")
        for raw in completed.stdout.split(b"\0")
        if raw
    ]
    entries = [_path_entry(path, repo_root) for path in paths]
    return {
        "mode": "tracked_tree",
        "entries": entries,
        "reusable": _manifest_entries_reusable(entries),
    }


def _input_manifest(contract: Any, repo_root: Path) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {"mode": "invalid", "reusable": False}
    mode = contract.get("mode")
    if mode == "explicit" and isinstance(contract.get("paths", []), list):
        manifest = _explicit_manifest(contract.get("paths", []), repo_root)
        manifest["reusable"] = _manifest_entries_reusable(manifest["entries"])
        return manifest
    if mode == "tracked_tree":
        return _tracked_tree_manifest(repo_root)
    return {"mode": str(mode), "reusable": False}


def _tool_identity(tool: str, repo_root: Path) -> dict[str, Any]:
    resolved = resolve_tool(tool)
    if resolved is None and ("/" in tool or "\\" in tool):
        candidate = Path(tool)
        resolved = str(candidate if candidate.is_absolute() else repo_root / candidate)
    if resolved is None or not Path(resolved).is_file():
        return {"requested": tool, "reusable": False, "status": "missing"}
    try:
        completed = subprocess.run(
            [resolved, "--version"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {
            "path": str(Path(resolved).resolve()),
            "requested": tool,
            "reusable": False,
            "status": "version-unavailable",
        }
    version_text = (completed.stdout + completed.stderr).strip()
    if completed.returncode != 0 or not version_text:
        return {
            "path": str(Path(resolved).resolve()),
            "requested": tool,
            "reusable": False,
            "status": "version-unavailable",
        }
    return {
        "path": str(Path(resolved).resolve()),
        "requested": tool,
        "reusable": True,
        "version": version_text,
    }


def _checkpoint_path(checkpoint_dir: Path, check_id: str) -> Path:
    return checkpoint_dir / f"{_evidence_name(check_id)}.json"


def _checkpoint_sidecar_path(checkpoint_path: Path, stream: str) -> Path:
    return checkpoint_path.with_name(f"{checkpoint_path.stem}.{stream}.txt")


def _load_checkpoint(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.is_file():
        return None, ["checkpoint_missing"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None, ["checkpoint_corrupt"]
    if not isinstance(payload, dict):
        return None, ["checkpoint_incomplete"]
    if payload.get("schema") != CHECKPOINT_SCHEMA:
        return None, ["checkpoint_schema_invalid"]
    required = {
        "check_id",
        "check_definition",
        "checkpoint_policy",
        "implementation_manifest",
        "input_manifest",
        "output_manifest",
        "dependency_fingerprints",
        "environment",
        "tools",
        "applicability",
        "engine_semantics",
        "evidence",
        "result",
        "result_fingerprint",
    }
    if not required.issubset(payload):
        return None, ["checkpoint_incomplete"]
    result = payload.get("result")
    if not isinstance(result, dict) or not isinstance(result.get("status"), str):
        return None, ["checkpoint_incomplete"]
    if not isinstance(payload.get("result_fingerprint"), str):
        return None, ["checkpoint_incomplete"]
    evidence = payload.get("evidence")
    if not isinstance(evidence, dict):
        return None, ["checkpoint_incomplete"]
    evidence_paths: dict[str, str] = {}
    for stream in ("stdout", "stderr"):
        metadata = evidence.get(stream)
        sidecar = _checkpoint_sidecar_path(path, stream)
        if (
            not isinstance(metadata, dict)
            or metadata.get("file") != sidecar.name
            or not isinstance(metadata.get("bytes"), int)
            or not isinstance(metadata.get("sha256"), str)
        ):
            return None, ["checkpoint_evidence_invalid"]
        try:
            data = sidecar.read_bytes()
        except OSError:
            return None, ["checkpoint_evidence_invalid"]
        if (
            len(data) != metadata["bytes"]
            or hashlib.sha256(data).hexdigest() != metadata["sha256"]
        ):
            return None, ["checkpoint_evidence_invalid"]
        evidence_paths[stream] = str(sidecar)
    payload["_evidence_paths"] = evidence_paths
    return payload, []


def _current_checkpoint_identity(
    check: dict[str, Any],
    options: RunOptions,
    dependency_fingerprints: dict[str, str],
    manifest_cache: dict[str, dict[str, Any]],
    tool_cache: dict[str, dict[str, Any]],
    execution_environment: dict[str, str],
) -> dict[str, Any]:
    input_contract = check.get("input_contract", {"mode": "tracked_tree"})
    input_key = json.dumps(input_contract, sort_keys=True)
    if input_key not in manifest_cache:
        manifest_cache[input_key] = _input_manifest(input_contract, options.repo_root)
    implementation_contract = {
        "mode": "explicit",
        "paths": check.get("implementation_sources", []),
    }
    implementation_key = "implementation:" + json.dumps(
        implementation_contract, sort_keys=True
    )
    if implementation_key not in manifest_cache:
        manifest_cache[implementation_key] = _input_manifest(
            implementation_contract, options.repo_root
        )
    tools: list[dict[str, Any]] = []
    for raw_tool in check.get("material_tools", []):
        tool = str(raw_tool)
        if tool not in tool_cache:
            tool_cache[tool] = _tool_identity(tool, options.repo_root)
        tools.append(tool_cache[tool])
    process_environment = os.environ.copy()
    process_environment.update(execution_environment)
    process_environment.update(options.environment)
    environment = {
        "canonical": dict(sorted(execution_environment.items())),
        "check_allowlist": {
            str(name): process_environment.get(str(name), "__UNSET__")
            for name in check.get("environment", [])
        },
    }
    applicability = check.get("applicability", {"mode": "always"})
    checkpoint_policy = check.get("checkpoint_policy", {"mode": "disabled"})
    definition = {
        "argv": check.get("argv", []),
        "dependencies": check.get("dependencies", []),
        "id": check.get("id"),
        "kind": check.get("kind"),
        "not_applicable_output": check.get("not_applicable_output"),
        "order": check.get("order"),
    }
    return {
        "applicability": applicability,
        "check_definition": definition,
        "check_id": str(check.get("id")),
        "checkpoint_policy": checkpoint_policy,
        "dependency_fingerprints": dependency_fingerprints,
        "engine_semantics": ENGINE_SEMANTICS,
        "environment": environment,
        "implementation_manifest": manifest_cache[implementation_key],
        "input_manifest": manifest_cache[input_key],
        "output_manifest": _input_manifest(
            check.get("output_contract", {"mode": "explicit", "paths": []}),
            options.repo_root,
        ),
        "tools": tools,
    }


def _checkpoint_reuse_decision(
    stored: dict[str, Any] | None,
    current: dict[str, Any],
    load_reasons: list[str],
) -> tuple[bool, list[str]]:
    if stored is None:
        return False, load_reasons
    reasons: list[str] = []
    comparisons = (
        ("check_id", "check_identity_changed"),
        ("check_definition", "check_definition_changed"),
        ("checkpoint_policy", "checkpoint_policy_changed"),
        ("implementation_manifest", "implementation_manifest_changed"),
        ("input_manifest", "input_manifest_changed"),
        ("output_manifest", "generated_artifacts_changed"),
        ("dependency_fingerprints", "dependency_fingerprints_changed"),
        ("environment", "environment_changed"),
        ("tools", "tool_identity_changed"),
        ("applicability", "applicability_changed"),
        ("engine_semantics", "engine_semantics_changed"),
    )
    for key, reason in comparisons:
        if stored.get(key) != current.get(key):
            reasons.append(reason)
    if stored.get("result", {}).get("status") != PASS:
        reasons.append("stored_result_not_pass")
    if stored.get("result", {}).get("status") == PASS and stored.get("result", {}).get(
        "exit_code"
    ) != 0:
        reasons.append("stored_pass_exit_code_invalid")
    if stored.get("result_fingerprint") != _result_fingerprint(current, PASS):
        reasons.append("checkpoint_result_fingerprint_invalid")
    if current.get("checkpoint_policy") != {"mode": "exact_declared_inputs"}:
        reasons.append("checkpoint_reuse_not_admitted")
    if current.get("applicability") != {"mode": "always"}:
        reasons.append("applicability_not_proven")
    if not current.get("input_manifest", {}).get("reusable", False):
        reasons.append("input_applicability_not_proven")
    if not current.get("implementation_manifest", {}).get("reusable", False):
        reasons.append("implementation_applicability_not_proven")
    if not current.get("output_manifest", {}).get("reusable", False):
        reasons.append("output_applicability_not_proven")
    if any(not item.get("reusable", False) for item in current.get("tools", [])):
        reasons.append("tool_applicability_not_proven")
    return not reasons, list(dict.fromkeys(reasons))


def _result_fingerprint(current: dict[str, Any], status: str) -> str:
    return _sha256_json({"identity": current, "status": status})


def _runtime_result_fingerprint(
    current: dict[str, Any] | None, check_id: str, status: str
) -> str:
    if current is not None:
        return _result_fingerprint(current, status)
    return _sha256_json(
        {
            "authority": "NONE",
            "check_id": check_id,
            "engine_semantics": ENGINE_SEMANTICS,
            "status": status,
        }
    )


def _store_checkpoint(
    checkpoint_dir: Path,
    current: dict[str, Any],
    record: CheckRecord,
) -> None:
    checkpoint_path = _checkpoint_path(checkpoint_dir, record.check_id)
    evidence: dict[str, dict[str, Any]] = {}
    for stream, raw_path in (
        ("stdout", record.stdout_path),
        ("stderr", record.stderr_path),
    ):
        try:
            data = Path(raw_path).read_bytes() if raw_path else b""
        except OSError:
            data = b""
        sidecar = _checkpoint_sidecar_path(checkpoint_path, stream)
        _write_bytes_atomic(sidecar, data)
        evidence[stream] = {
            "bytes": len(data),
            "file": sidecar.name,
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    payload = {
        "schema": CHECKPOINT_SCHEMA,
        **current,
        "evidence": evidence,
        "result": {
            "exit_code": record.exit_code,
            "status": record.status,
        },
        "result_fingerprint": record.result_fingerprint,
    }
    _write_json_atomic(checkpoint_path, payload)


def _terminate_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        completed = subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if completed.returncode != 0 and process.poll() is None:
            process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def _run_with_tree_timeout(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: float,
) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        argv,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=(
            subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        ),
        start_new_session=os.name != "nt",
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        _terminate_process_tree(process)
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        raise subprocess.TimeoutExpired(
            argv,
            timeout,
            output=stdout or exc.output,
            stderr=stderr or exc.stderr,
        ) from None
    return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)


def run_shadow(registry: dict[str, Any], options: RunOptions) -> RunReport:
    """Execute a validated check population without fail-fast serial discovery."""
    options.output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_enabled_ids = {
        str(check["id"])
        for check in registry["checks"]
        if check.get("checkpoint_policy")
        == {"mode": "exact_declared_inputs"}
    }
    checkpointing_active = (
        options.checkpoint_dir is not None and bool(checkpoint_enabled_ids)
    )
    execution_environment = registry.get("execution_environment", {})
    if not isinstance(execution_environment, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in execution_environment.items()
    ):
        execution_environment = {}
    if checkpointing_active and options.checkpoint_dir is not None:
        options.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    records: list[CheckRecord] = []
    by_id: dict[str, CheckRecord] = {}
    checkpoints_reused: list[str] = []
    invalidation_reasons: dict[str, list[str]] = {}
    checkpoint_validation_seconds = 0.0
    manifest_cache: dict[str, dict[str, Any]] = {}
    tool_cache: dict[str, dict[str, Any]] = {}
    for check in sorted(registry["checks"], key=lambda item: item["order"]):
        check_id = str(check["id"])
        order = int(check["order"])
        blocked_by = [
            dependency
            for dependency in check.get("dependencies", [])
            if dependency in by_id and by_id[dependency].status != PASS
        ]
        if blocked_by:
            record = CheckRecord(
                check_id=check_id,
                order=order,
                status=BLOCKED,
                blocked_by=blocked_by,
                detail="declared prerequisite did not PASS",
                execution_source="NOT_EXECUTED",
            )
            records.append(record)
            by_id[check_id] = record
            continue

        dependency_fingerprints = {
            dependency: by_id[dependency].result_fingerprint
            for dependency in check.get("dependencies", [])
        }
        current_checkpoint: dict[str, Any] | None = None
        if checkpointing_active:
            checkpoint_started = time.monotonic()
            current_checkpoint = _current_checkpoint_identity(
                check,
                options,
                dependency_fingerprints,
                manifest_cache,
                tool_cache,
                execution_environment,
            )
            checkpoint_validation_seconds += time.monotonic() - checkpoint_started
        if options.mode == "RESUME" and check_id not in checkpoint_enabled_ids:
            invalidation_reasons[check_id] = ["checkpoint_reuse_not_admitted"]
        elif (
            options.mode == "RESUME"
            and options.checkpoint_dir is not None
            and current_checkpoint is not None
        ):
            stored, load_reasons = _load_checkpoint(
                _checkpoint_path(options.checkpoint_dir, check_id)
            )
            reusable, reasons = _checkpoint_reuse_decision(
                stored, current_checkpoint, load_reasons
            )
            if reusable and stored is not None:
                record = CheckRecord(
                    check_id=check_id,
                    order=order,
                    status=PASS,
                    exit_code=stored["result"].get("exit_code"),
                    detail="exact applicable PASS checkpoint reused",
                    execution_source="CHECKPOINT_REUSED",
                    result_fingerprint=str(stored["result_fingerprint"]),
                    stdout_path=str(stored["_evidence_paths"]["stdout"]),
                    stderr_path=str(stored["_evidence_paths"]["stderr"]),
                )
                records.append(record)
                by_id[check_id] = record
                checkpoints_reused.append(check_id)
                continue
            invalidation_reasons[check_id] = reasons

        missing_tools = [
            str(tool)
            for tool in check.get("material_tools", [])
            if not _tool_available(str(tool), options.repo_root)
        ]
        if missing_tools:
            record = CheckRecord(
                check_id=check_id,
                order=order,
                status=INFRASTRUCTURE_ERROR,
                detail="missing material tool(s): " + ", ".join(missing_tools),
                execution_source="NOT_EXECUTED",
                result_fingerprint=_runtime_result_fingerprint(
                    current_checkpoint, check_id, INFRASTRUCTURE_ERROR
                ),
            )
            records.append(record)
            by_id[check_id] = record
            continue

        temporary: tempfile.TemporaryDirectory[str] | None = None
        if check.get("kind") == "canonical_prefix":
            canonical = registry.get("canonical", {})
            canonical_path = options.repo_root / str(canonical.get("path", ""))
            try:
                prefix = build_canonical_prefix(
                    canonical_path.read_text(encoding="utf-8"),
                    first_command=str(canonical.get("first_command", "")),
                )
            except (OSError, UnicodeError, ValueError) as exc:
                record = CheckRecord(
                    check_id=check_id,
                    order=order,
                    status=INFRASTRUCTURE_ERROR,
                    detail=f"canonical prefix extraction failed: {exc}",
                    execution_source="NOT_EXECUTED",
                    result_fingerprint=_runtime_result_fingerprint(
                        current_checkpoint, check_id, INFRASTRUCTURE_ERROR
                    ),
                )
                records.append(record)
                by_id[check_id] = record
                continue
            bash = resolve_tool("bash")
            if bash is None:
                record = CheckRecord(
                    check_id=check_id,
                    order=order,
                    status=INFRASTRUCTURE_ERROR,
                    detail="missing material tool(s): bash",
                    execution_source="NOT_EXECUTED",
                    result_fingerprint=_runtime_result_fingerprint(
                        current_checkpoint, check_id, INFRASTRUCTURE_ERROR
                    ),
                )
                records.append(record)
                by_id[check_id] = record
                continue
            temporary = tempfile.TemporaryDirectory(
                prefix="inline-prefix-", dir=options.output_dir
            )
            prefix_path = Path(temporary.name) / "verify-package-inline.sh"
            prefix_path.write_text(prefix, encoding="utf-8", newline="\n")
            argv = [bash, str(prefix_path)]
        else:
            argv = [str(item) for item in check.get("argv", [])]
            if argv and argv[0] == "bash":
                bash = resolve_tool("bash")
                if bash is not None:
                    argv[0] = bash
        if not argv:
            record = CheckRecord(
                check_id=check_id,
                order=order,
                status=INFRASTRUCTURE_ERROR,
                detail="check has no executable argv",
                execution_source="NOT_EXECUTED",
                result_fingerprint=_runtime_result_fingerprint(
                    current_checkpoint, check_id, INFRASTRUCTURE_ERROR
                ),
            )
            records.append(record)
            by_id[check_id] = record
            continue

        base = options.output_dir / f"{order:03d}-{_evidence_name(check_id)}"
        stdout_path = base.with_suffix(".stdout.txt")
        stderr_path = base.with_suffix(".stderr.txt")
        started = time.monotonic()
        try:
            process_environment = os.environ.copy()
            process_environment.update(execution_environment)
            process_environment.update(options.environment)
            completed = _run_with_tree_timeout(
                argv,
                cwd=options.repo_root,
                env=process_environment,
                timeout=options.timeout_seconds,
            )
            duration = time.monotonic() - started
            stdout_path.write_text(completed.stdout, encoding="utf-8", newline="\n")
            stderr_path.write_text(completed.stderr, encoding="utf-8", newline="\n")
            not_applicable_token = check.get("not_applicable_output")
            if (
                completed.returncode == 0
                and isinstance(not_applicable_token, str)
                and not_applicable_token in completed.stdout.splitlines()
            ):
                status = NOT_APPLICABLE
            else:
                status = PASS if completed.returncode == 0 else FAIL
            record = CheckRecord(
                check_id=check_id,
                order=order,
                status=status,
                duration_seconds=duration,
                exit_code=completed.returncode,
                stdout_path=str(stdout_path),
                stderr_path=str(stderr_path),
                result_fingerprint=_runtime_result_fingerprint(
                    current_checkpoint, check_id, status
                ),
            )
        except subprocess.TimeoutExpired as exc:
            duration = time.monotonic() - started
            stdout = (
                exc.stdout.decode("utf-8", "replace")
                if isinstance(exc.stdout, bytes)
                else (exc.stdout or "")
            )
            stderr = (
                exc.stderr.decode("utf-8", "replace")
                if isinstance(exc.stderr, bytes)
                else (exc.stderr or "")
            )
            stdout_path.write_text(stdout, encoding="utf-8", newline="\n")
            stderr_path.write_text(stderr, encoding="utf-8", newline="\n")
            record = CheckRecord(
                check_id=check_id,
                order=order,
                status=INFRASTRUCTURE_ERROR,
                duration_seconds=duration,
                detail=f"timeout after {options.timeout_seconds} seconds",
                stdout_path=str(stdout_path),
                stderr_path=str(stderr_path),
                result_fingerprint=_runtime_result_fingerprint(
                    current_checkpoint, check_id, INFRASTRUCTURE_ERROR
                ),
            )
        except OSError as exc:
            record = CheckRecord(
                check_id=check_id,
                order=order,
                status=INFRASTRUCTURE_ERROR,
                duration_seconds=time.monotonic() - started,
                detail=f"process start failed: {exc}",
                result_fingerprint=_runtime_result_fingerprint(
                    current_checkpoint, check_id, INFRASTRUCTURE_ERROR
                ),
            )
        finally:
            if temporary is not None:
                temporary.cleanup()
        records.append(record)
        by_id[check_id] = record
        if (
            options.checkpoint_dir is not None
            and current_checkpoint is not None
            and check_id in checkpoint_enabled_ids
        ):
            current_checkpoint["output_manifest"] = _input_manifest(
                check.get(
                    "output_contract", {"mode": "explicit", "paths": []}
                ),
                options.repo_root,
            )
            record.result_fingerprint = _runtime_result_fingerprint(
                current_checkpoint, check_id, record.status
            )
            _store_checkpoint(options.checkpoint_dir, current_checkpoint, record)
    return RunReport(
        mode=options.mode,
        checks=records,
        run_id=uuid.uuid4().hex,
        checkpoints_reused=checkpoints_reused,
        invalidation_reasons=invalidation_reasons,
        checkpoint_validation_seconds=checkpoint_validation_seconds,
        registry_sha256=_sha256_json(registry),
        canonical_verifier_sha256=registry.get("canonical", {}).get("sha256"),
    )


def semantic_oracle_comparison(
    canonical_failures: list[str], shadow_report: RunReport
) -> dict[str, Any]:
    """Compare demonstrated oracle failures without penalising extra discovery."""
    canonical = list(dict.fromkeys(canonical_failures))
    shadow = list(shadow_report.primary_failures)
    suppressed = [check_id for check_id in canonical if check_id not in shadow]
    additional = [check_id for check_id in shadow if check_id not in canonical]
    return {
        "additional_shadow_failures": additional,
        "canonical_demonstrated_failures": canonical,
        "result": "PASS" if not suppressed else "FAIL",
        "shadow_primary_failures": shadow,
        "suppressed_failures": suppressed,
    }


def _load_compact_registry(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("registry root must be an object")
    return payload


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _write_bytes_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_bytes(data)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser(
        "validate-registry", help="validate shadow registry against canonical bytes"
    )
    validate.add_argument("--repo-root", type=Path, required=True)
    validate.add_argument("--registry", type=Path, required=True)
    run = subparsers.add_parser(
        "run", help="run the non-authoritative dependency-aware shadow verifier"
    )
    run.add_argument("--repo-root", type=Path, required=True)
    run.add_argument("--registry", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, required=True)
    run.add_argument("--checkpoint-dir", type=Path)
    run.add_argument(
        "--resume",
        action="store_true",
        help="reuse only exact, mechanically applicable PASS checkpoints",
    )
    run.add_argument("--timeout-seconds", type=float, default=900.0)
    args = parser.parse_args(argv)

    if args.command == "validate-registry":
        try:
            compact = _load_compact_registry(args.registry)
            registry = materialize_registry(compact, args.repo_root)
            errors = validate_registry(registry, args.repo_root)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors = [str(exc)]
            registry = {"checks": []}
            compact = {}
        payload = {
            "authority": "NONE",
            "canonical_sha256": compact.get("canonical", {}).get("sha256"),
            "check_count": len(registry.get("checks", [])),
            "checkpoint_enabled_count": sum(
                1
                for check in registry.get("checks", [])
                if check.get("checkpoint_policy")
                == {"mode": "exact_declared_inputs"}
            ),
            "command_check_count": sum(
                1
                for check in registry.get("checks", [])
                if check.get("kind") == "command"
            ),
            "errors": errors,
            "status": "PASS" if not errors else "FAIL",
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if not errors else 2
    if args.command == "run":
        if args.resume and args.checkpoint_dir is None:
            print(
                json.dumps(
                    {
                        "authority": "NONE",
                        "errors": ["--resume requires --checkpoint-dir"],
                        "status": "INFRASTRUCTURE_ERROR",
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2
        try:
            compact = _load_compact_registry(args.registry)
            registry = materialize_registry(compact, args.repo_root)
            errors = validate_registry(registry, args.repo_root)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors = [str(exc)]
            registry = {"checks": []}
        if errors:
            print(
                json.dumps(
                    {"authority": "NONE", "errors": errors, "status": "INFRASTRUCTURE_ERROR"},
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2
        report = run_shadow(
            registry,
            RunOptions(
                repo_root=args.repo_root,
                output_dir=args.output_dir,
                timeout_seconds=args.timeout_seconds,
                mode="RESUME" if args.resume else "KEEP_GOING",
                checkpoint_dir=args.checkpoint_dir,
            ),
        )
        report_path = args.output_dir / "report.json"
        _write_json_atomic(report_path, report.to_json_dict())
        print(
            json.dumps(
                {
                    "authority": "NONE",
                    "blocked": len(report.blocked_checks),
                    "complete_safe_failure_frontier": report.complete_safe_failure_frontier,
                    "checkpoints_invalidated": len(report.checkpoints_invalidated),
                    "checkpoints_reused": len(report.checkpoints_reused),
                    "checks_executed": len(report.checks_executed),
                    "infrastructure_errors": len(report.infrastructure_errors),
                    "passes": len(report.pass_checks),
                    "primary_failures": len(report.primary_failures),
                    "report": str(report_path),
                    "run_id": report.run_id,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1 if report.primary_failures or report.infrastructure_errors else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
