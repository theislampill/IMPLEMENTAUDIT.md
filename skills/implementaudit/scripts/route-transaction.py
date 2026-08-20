#!/usr/bin/env python3
"""Canonical R0033 route-decision and obligation authority.

This H2A core owns only PENDING/NOT_REQUIRED/REQUIRED classification and the
current immutable Git-ref record. Child opening, result return, and obligation
completion are deliberately outside this module.
"""

from __future__ import annotations

import argparse
import contextlib
import errno
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterator, NoReturn


RESULT_SCHEMA = "implementaudit.route-transaction-result.v1"
REQUEST_SCHEMA = "implementaudit.route-decision-request.v1"
RECORD_SCHEMA = "implementaudit.route-decision.v1"
PREDICATE_VERSION = "R0033.route-predicate.v1"
DECISIONS = {"PENDING", "NOT_REQUIRED", "REQUIRED"}
CLASSIFICATIONS = {
    "MECHANICALLY_REQUIRED",
    "MECHANICALLY_NOT_REQUIRED",
    "JUDGEMENT_REQUIRED",
}
CLOSED_ACTION_CLASSES = {
    "MECHANICAL_CURRENTNESS_ACTION",
    "PURE_BOUNDED_READ_OR_VALIDATION",
    "EXACT_PACKAGE_OR_TOPOLOGY_VERIFICATION",
    "SAFE_STATUS_OR_CONTAINMENT",
    "EXACT_ALREADY_BOUND_DETERMINISTIC_ACTION",
}
REQUIRED_REASONS = {
    "STALE_CONTEXT_RECONSTRUCTION",
    "IMMUTABLE_INDEPENDENT_REVIEW",
    "MAINTAINER_QUALIFICATION",
    "NONTRIVIAL_ANDON_DIAGNOSIS",
}
CONTINUITY_RE = re.compile(r"G[0-9A-F]{4}")
CONTROLLER_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,47}")
OID_RE = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")
HEX_RE = re.compile(r"sha256:[0-9a-f]{64}")
ZERO_OID = "0" * 40
EXPIRES_ON = [
    "action-completion",
    "next-action-change",
    "scope-change",
    "read-set-change",
    "host-binding-generation-change",
    "continuity-receipt-change",
    "package-identity-change",
    "child-source-identity-change",
    "owner-evidence-change",
    "authority-evidence-change",
    "dependency-evidence-change",
    "effect-evidence-change",
    "contradiction-or-invalidation",
    "scope-expansion",
]
RECORD_KEYS = {
    "schema", "predicate_version", "controller_id", "claim_id", "explicit_run_root",
    "continuity_generation", "continuity_receipt", "host_id", "host_session_id",
    "host_binding_generation", "host_correlation_id", "boundary", "scope", "action",
    "evidence", "inputs", "package", "child_source", "decision", "classification",
    "invalidators", "expiry_fingerprint", "expires_on", "predecessor_record_oid",
    "route_transaction_id", "obligation_id", "route_state", "child_lifecycle_owned",
    "consumed_record_oid", "record_identity",
}


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


def fail(message: str, *, decision: str = "PENDING") -> NoReturn:
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "UNAVAILABLE",
            "decision": decision,
            "advance_allowed": False,
            "enforcement_available": False,
            "error": message,
        }
    )
    raise SystemExit(2)


def run(command: list[str], *, cwd: Path, label: str, environment: dict[str, str] | None = None) -> str:
    completed = subprocess.run(command, cwd=cwd, env=environment, text=True, capture_output=True, check=False)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        fail(f"{label} failed: {detail}")
    return completed.stdout.strip()


def git(repo: Path, *args: str, input_text: str | None = None, check: bool = True) -> str:
    executable = trusted_host_executable(repo, "git")
    completed = subprocess.run(
        [str(executable), *args], cwd=repo, env=sanitized_action_environment(), text=True,
        input=input_text, capture_output=True, check=False
    )
    if check and completed.returncode:
        fail(f"git {' '.join(args)} failed: {completed.stderr.strip() or completed.stdout.strip()}")
    return completed.stdout.strip()


def digest_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON member")
    return value


def exact_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 1024 or any(ord(char) < 32 for char in value):
        fail(f"{label} is empty, oversized, or contains a control character")
    return value


def exact_keys(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        fail(f"{label} has the wrong shape")
    return value


def identity_record(value: Any, label: str) -> dict[str, str]:
    record = exact_keys(value, {"identity", "digest"}, label)
    exact_text(record["identity"], f"{label}.identity")
    if not isinstance(record["digest"], str) or not HEX_RE.fullmatch(record["digest"]):
        fail(f"{label}.digest is not a canonical sha256 identity")
    return record


def read_request(path: str) -> dict[str, Any]:
    target = Path(path)
    try:
        if target.absolute() != target.resolve(strict=True):
            fail("request traverses an alias")
        info = os.lstat(target)
        if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or info.st_size > 1_000_000:
            fail("request is not a safe regular file")
        request = json.loads(target.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        fail(f"request is unreadable or malformed: {exc}")
    keys = {
        "schema",
        "predicate_version",
        "boundary",
        "scope",
        "action",
        "inputs",
    }
    exact_keys(request, keys, "request")
    if request["schema"] != REQUEST_SCHEMA or request["predicate_version"] != PREDICATE_VERSION:
        fail("request schema or predicate version is stale")
    boundary = exact_keys(request["boundary"], {"kind", "event_id", "digest"}, "boundary")
    exact_text(boundary["kind"], "boundary.kind")
    exact_text(boundary["event_id"], "boundary.event_id")
    if not HEX_RE.fullmatch(boundary.get("digest", "")):
        fail("boundary identity is malformed")
    identity_record(request["scope"], "scope")
    action = exact_keys(request["action"], {"identity", "digest", "class", "argv"}, "action")
    exact_text(action["identity"], "action.identity")
    exact_text(action["class"], "action.class")
    if not HEX_RE.fullmatch(action.get("digest", "")):
        fail("action identity is malformed")
    if (
        not isinstance(action["argv"], list)
        or not action["argv"]
        or len(action["argv"]) > 64
        or any(not isinstance(item, str) or not item or len(item) > 4096 for item in action["argv"])
    ):
        fail("action argv is empty, oversized, or malformed")
    if not isinstance(request["inputs"], list) or not request["inputs"]:
        fail("inputs must be a non-empty complete identity set")
    identities: list[str] = []
    for index, item in enumerate(request["inputs"]):
        record = exact_keys(item, {"identity", "path", "digest"}, f"inputs[{index}]")
        identities.append(exact_text(record["identity"], f"inputs[{index}].identity"))
        exact_text(record["path"], f"inputs[{index}].path")
        if not isinstance(record["digest"], str) or not HEX_RE.fullmatch(record["digest"]):
            fail(f"inputs[{index}].digest is not canonical")
    if identities != sorted(identities) or len(identities) != len(set(identities)):
        fail("inputs are not uniquely ordered by identity")
    return request


def mechanical_action_class(argv: list[str]) -> str | None:
    executable = argv[0].lower()
    claim = Path(__file__).resolve().with_name("claim-run.sh")
    if Path(argv[0]).name.lower() in {"claim-run.sh", "claim-run"} and Path(argv[0]).resolve() == claim:
        if argv[1:] == ["--current-controller"] or (
            len(argv) == 3 and argv[1] == "--current-controller" and CONTROLLER_RE.fullmatch(argv[2])
        ):
            return "MECHANICAL_CURRENTNESS_ACTION"
        if len(argv) == 3 and argv[1] == "--require-current-continuity" and CONTROLLER_RE.fullmatch(argv[2]):
            return "MECHANICAL_CURRENTNESS_ACTION"
        if len(argv) == 3 and argv[1] == "--verify-resume-receipt" and re.fullmatch(
            r"refs/implementaudit/continuity-receipts/[a-z0-9][a-z0-9-]*/G[0-9A-F]{4}@[0-9a-f]{40}", argv[2]
        ):
            return "MECHANICAL_CURRENTNESS_ACTION"
    if argv == ["route-read-snapshot"]:
        return "PURE_BOUNDED_READ_OR_VALIDATION"
    package_script = Path(argv[2]).resolve() if executable == "bash" and len(argv) == 3 and argv[1] == "-n" else None
    if (
        package_script is not None
        and package_script.parent == Path(__file__).resolve().parent
        and re.fullmatch(r"check-[a-z0-9-]+\.sh", package_script.name)
    ):
        return "EXACT_PACKAGE_OR_TOPOLOGY_VERIFICATION"
    if argv == ["route-safe-status"]:
        return "SAFE_STATUS_OR_CONTAINMENT"
    if executable in {"sha256sum", "shasum"} and len(argv) == 2:
        return "EXACT_ALREADY_BOUND_DETERMINISTIC_ACTION"
    return None


def mechanical_required_reason(argv: list[str]) -> str | None:
    if len(argv) == 2 and argv[0] == "route-trigger" and argv[1] in REQUIRED_REASONS:
        return argv[1]
    return None


def classify(request: dict[str, Any], noncurrent: list[str]) -> tuple[str, str, list[str]]:
    judgement = [item for item in noncurrent if item.endswith(":JUDGEMENT_REQUIRED")]
    if judgement:
        return "REQUIRED", "JUDGEMENT_REQUIRED", judgement
    if noncurrent:
        return "PENDING", "JUDGEMENT_REQUIRED", noncurrent
    required_reason = mechanical_required_reason(request["action"]["argv"])
    if required_reason is not None:
        return "REQUIRED", "MECHANICALLY_REQUIRED", [required_reason]
    derived = mechanical_action_class(request["action"]["argv"])
    if derived is None or request["action"]["class"] != derived or derived not in CLOSED_ACTION_CLASSES:
        return "REQUIRED", "JUDGEMENT_REQUIRED", ["route judgement cannot mint NOT_REQUIRED"]
    return "NOT_REQUIRED", "MECHANICALLY_NOT_REQUIRED", []


def repo_context() -> tuple[Path, str, str]:
    repo = Path(git(Path.cwd(), "rev-parse", "--path-format=absolute", "--show-toplevel")).resolve()
    common = str(Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve())
    return repo, str(repo), common


def ref_name(controller: str) -> str:
    if not CONTROLLER_RE.fullmatch(controller):
        fail("controller identity is not canonical")
    return f"refs/implementaudit/route-decisions/{controller}"


def current_ref(repo: Path, controller: str) -> tuple[str | None, dict[str, Any] | None]:
    ref = ref_name(controller)
    completed = subprocess.run(
        [str(trusted_host_executable(repo, "git")), "rev-parse", "--verify", ref],
        cwd=repo,
        env=sanitized_action_environment(),
        text=True,
        capture_output=True,
    )
    if completed.returncode:
        return None, None
    oid = completed.stdout.strip()
    try:
        record = json.loads(git(repo, "cat-file", "blob", oid), object_pairs_hook=unique_object)
    except (json.JSONDecodeError, ValueError):
        fail("current route record is malformed")
    if not isinstance(record, dict) or set(record) != RECORD_KEYS or record.get("schema") != RECORD_SCHEMA:
        fail("current route record is malformed or mixed-version")
    if (
        record.get("predicate_version") != PREDICATE_VERSION
        or record.get("controller_id") != controller
        or record.get("decision") not in DECISIONS
        or record.get("expires_on") != EXPIRES_ON
        or record.get("child_lifecycle_owned") is not False
    ):
        fail("current route record has foreign identity or invalid decision")
    if record["decision"] == "REQUIRED":
        if record.get("route_state") != "UNSATISFIED" or not isinstance(record.get("obligation_id"), str):
            fail("current required route record has no unsatisfied obligation")
    elif record.get("route_state") is not None or record.get("obligation_id") is not None:
        fail("non-required route record improperly owns an obligation")
    if record.get("classification") not in CLASSIFICATIONS or record.get("record_identity") != digest_json(
        {key: value for key, value in record.items() if key != "record_identity"}
    ):
        fail("current route record identity is invalid")
    return oid, record


def current_controller(repo: Path, controller: str) -> dict[str, str]:
    claim = Path(__file__).with_name("claim-run.sh")
    bash = trusted_host_executable(repo, "bash")
    environment = sanitized_action_environment()
    current = run([str(bash), str(claim), "--current-controller", controller], cwd=repo, label="controller currentness", environment=environment)
    parts = current.split("\t")
    if len(parts) != 4 or parts[0] != controller:
        fail("controller currentness returned a foreign or malformed record")
    receipt = run(
        [str(bash), str(claim), "--require-current-continuity", controller],
        cwd=repo,
        label="continuity currentness",
        environment=environment,
    )
    prefix = f"refs/implementaudit/continuity-receipts/{controller}/"
    if not receipt.startswith(prefix) or "@" not in receipt:
        fail("continuity receipt identity is malformed")
    generation = receipt[len(prefix) :].split("@", 1)[0]
    if not CONTINUITY_RE.fullmatch(generation):
        fail("continuity generation is malformed")
    receipt_oid = receipt.split("@", 1)[1]
    receipt_fields = git(repo, "cat-file", "blob", receipt_oid).split("\t")
    if len(receipt_fields) != 12 or receipt_fields[0] != "implementaudit.continuity-receipt.v2":
        fail("R0033 route authority requires a current v2 continuity receipt")
    invalidation_oid = receipt_fields[8]
    if invalidation_oid == "none":
        fail("route authority requires an exact current boundary invalidation")
    invalidation_fields = git(repo, "cat-file", "blob", invalidation_oid).split("\t")
    if (
        len(invalidation_fields) != 6
        or invalidation_fields[0] != "implementaudit.continuity-invalidation.v1"
        or invalidation_fields[1] != controller
        or invalidation_fields[4] != receipt_fields[9]
    ):
        fail("continuity boundary invalidation is malformed or foreign")
    return {
        "controller_id": parts[0],
        "repository_identity": parts[1],
        "explicit_run_root": parts[2],
        "claim_id": parts[3],
        "continuity_receipt": receipt,
        "continuity_generation": generation,
        "controller_record_oid": git(repo, "rev-parse", "--verify", f"refs/implementaudit/controllers/{controller}"),
        "boundary_kind": receipt_fields[9],
        "boundary_event_id": invalidation_fields[5],
        "next_action": receipt_fields[11],
    }


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        fail(f"cannot hash mechanical evidence {path}: {exc}")
    return f"sha256:{digest.hexdigest()}"


def trusted_host_executable(repo: Path, name: str) -> Path:
    selected = shutil.which(name)
    if selected is None:
        fail(f"trusted host executable is unavailable: {name}")
    resolved = Path(selected).resolve()
    try:
        resolved.relative_to(repo)
    except ValueError:
        pass
    else:
        fail("system action executable resolves inside target-repository custody")
    if os.name == "nt":
        roots = [
            Path(value).resolve()
            for key in ("ProgramFiles", "ProgramFiles(x86)", "SystemRoot")
            if (value := os.environ.get(key))
        ]
        if not any(str(resolved).casefold().startswith(str(root).casefold() + os.sep.casefold()) for root in roots):
            fail("system action executable is outside trusted host custody")
    else:
        cursor = resolved
        while True:
            info = os.lstat(cursor)
            if info.st_uid != 0 or info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                fail("system action executable is outside root-owned host custody")
            if cursor.parent == cursor:
                break
            cursor = cursor.parent
    return resolved


def executable_evidence(repo: Path, argv: list[str]) -> dict[str, str]:
    if mechanical_required_reason(argv) is not None:
        return {"requested": "route-trigger", "resolved": "R0033:built-in", "digest": digest_json(argv)}
    if argv in (["route-read-snapshot"], ["route-safe-status"]):
        return {"requested": argv[0], "resolved": "R0033:built-in", "digest": digest_json(argv)}
    if mechanical_action_class(argv) is None:
        return {"requested": argv[0], "resolved": "R0033:unadmitted", "digest": digest_json(argv)}
    if Path(argv[0]).name.lower() in {"claim-run.sh", "claim-run"}:
        resolved = Path(argv[0]).resolve()
    else:
        if argv[0] not in {"git", "bash", "sha256sum", "shasum"}:
            fail("action executable is not a closed trusted identity")
        resolved = trusted_host_executable(repo, argv[0])
    try:
        info = os.lstat(resolved)
    except OSError as exc:
        fail(f"action executable cannot be inspected: {exc}")
    if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
        fail("action executable is not a safe regular file")
    evidence = {"requested": argv[0], "resolved": str(resolved), "digest": file_digest(resolved)}
    if resolved.suffix.lower() == ".sh":
        interpreter_path = trusted_host_executable(repo, "bash")
        interpreter_info = os.lstat(interpreter_path)
        if not stat.S_ISREG(interpreter_info.st_mode) or stat.S_ISLNK(interpreter_info.st_mode):
            fail("shell action interpreter is not a safe regular file")
        evidence.update(
            {
                "interpreter_resolved": str(interpreter_path),
                "interpreter_digest": file_digest(interpreter_path),
            }
        )
    return evidence


def sanitized_action_environment() -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("GIT_", "LD_", "DYLD_"))
        and key not in {"BASH_ENV", "BASHOPTS", "CDPATH", "ENV", "SHELLOPTS"}
    }
    environment.update(
        {
            "GIT_ATTR_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "NUL" if os.name == "nt" else "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_EXTERNAL_DIFF": "",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_PAGER": "cat",
            "LC_ALL": "C",
            "PAGER": "cat",
        }
    )
    return environment


def worktree_read_set(repo: Path) -> dict[str, Any]:
    git_executable = trusted_host_executable(repo, "git")
    raw_paths = subprocess.run(
        [str(git_executable), "ls-files", "-c", "-o", "--exclude-standard", "-z"],
        cwd=repo,
        env=sanitized_action_environment(),
        capture_output=True,
        check=False,
    )
    if raw_paths.returncode:
        fail("whole-worktree read-set enumeration failed")
    paths = sorted({item.decode("utf-8", "surrogateescape") for item in raw_paths.stdout.split(b"\0") if item})
    if len(paths) > 100_000:
        fail("whole-worktree read set exceeds the bounded population")
    digest = hashlib.sha256()
    for relative in paths:
        encoded = relative.encode("utf-8", "surrogateescape")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        target = repo / relative
        try:
            info = os.lstat(target)
        except OSError:
            digest.update(b"MISSING")
            continue
        if stat.S_ISLNK(info.st_mode):
            payload = os.readlink(target).encode("utf-8", "surrogateescape")
            digest.update(b"SYMLINK")
            digest.update(payload)
        elif stat.S_ISREG(info.st_mode):
            digest.update(file_digest(target).encode("ascii"))
        else:
            digest.update(b"NONREGULAR")
    environment = sanitized_action_environment()
    logical_index = run([str(git_executable), "ls-files", "-s", "-z"], cwd=repo, label="index read-set", environment=environment)
    metadata: dict[str, str] = {}
    for identity, git_path in (
        ("raw_index", "index"),
        ("repository_config", "config"),
        ("worktree_config", "config.worktree"),
        ("sparse_checkout", "info/sparse-checkout"),
    ):
        raw = run([str(git_executable), "rev-parse", "--git-path", git_path], cwd=repo, label=f"{identity} path", environment=environment)
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = repo / candidate
        candidate = candidate.resolve()
        try:
            info = os.lstat(candidate)
        except OSError:
            metadata[identity] = "MISSING"
        else:
            metadata[identity] = file_digest(candidate) if stat.S_ISREG(info.st_mode) and not stat.S_ISLNK(info.st_mode) else "UNSAFE"
    return {
        "population": len(paths),
        "digest": f"sha256:{digest.hexdigest()}",
        "logical_index_digest": digest_json(logical_index),
        "git_metadata": metadata,
        "submodules": "IGNORED_BY_EXACT_ARGV",
    }


def git_environment_requires_judgement(repo: Path) -> bool:
    git_executable = trusted_host_executable(repo, "git")
    completed = subprocess.run(
        [str(git_executable), "config", "--local", "--null", "--list"],
        cwd=repo,
        env=sanitized_action_environment(),
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        return True
    for entry in completed.stdout.split(b"\0"):
        key = entry.split(b"\n", 1)[0].decode("utf-8", "surrogateescape").casefold()
        if key.startswith("filter."):
            return True
    return False


def request_observations(
    repo: Path, current: dict[str, str], request: dict[str, Any]
) -> tuple[list[str], list[dict[str, str]]]:
    invalidators: list[str] = []
    boundary_expected = digest_json({"kind": request["boundary"]["kind"], "event_id": request["boundary"]["event_id"]})
    if request["boundary"]["digest"] != boundary_expected:
        invalidators.append("boundary:CONTRADICTORY")
    if (
        request["boundary"]["kind"] != current["boundary_kind"]
        or request["boundary"]["event_id"] != current["boundary_event_id"]
    ):
        invalidators.append("boundary:STALE")
    scope_expected = digest_json({"identity": request["scope"]["identity"]})
    if request["scope"]["digest"] != scope_expected:
        invalidators.append("scope:CONTRADICTORY")
    if request["scope"]["identity"] != current["next_action"]:
        invalidators.append("scope:STALE")
    action_expected = digest_json(
        {
            "identity": request["action"]["identity"],
            "class": request["action"]["class"],
            "argv": request["action"]["argv"],
        }
    )
    if request["action"]["digest"] != action_expected:
        invalidators.append("action:CONTRADICTORY")
    observed_inputs: list[dict[str, str]] = []
    for item in request["inputs"]:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts or "." in relative.parts:
            invalidators.append(f"{item['identity']}:MISSING")
            continue
        target = repo / relative
        try:
            resolved = target.resolve(strict=True)
            info = os.lstat(target)
            resolved.relative_to(repo)
        except (OSError, RuntimeError, ValueError):
            invalidators.append(f"{item['identity']}:MISSING")
            continue
        if target.absolute() != resolved or not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
            invalidators.append(f"{item['identity']}:MISSING")
            continue
        actual = file_digest(resolved)
        status = "CURRENT" if actual == item["digest"] else "STALE"
        if status != "CURRENT":
            invalidators.append(f"{item['identity']}:{status}")
        observed_inputs.append({"identity": item["identity"], "path": relative.as_posix(), "digest": actual, "status": status})
    current_paths = {item["path"] for item in observed_inputs if item["status"] == "CURRENT"}
    argv = request["action"]["argv"]
    executable = argv[0].lower()
    if executable == "git" and git_environment_requires_judgement(repo):
        invalidators.append("action-environment:JUDGEMENT_REQUIRED")
    if executable in {"sha256sum", "shasum"} and len(argv) == 2 and argv[1] not in current_paths:
        invalidators.append("action-input:MISSING")
    return sorted(invalidators), observed_inputs


def executing_package_evidence(repo: Path, request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    skill_root = Path(__file__).resolve().parent.parent
    source_paths = [
        skill_root / "SKILL.md",
        skill_root / "references" / "route-obligations.md",
        Path(__file__).resolve(),
        Path(__file__).resolve().with_name("claim-run.sh"),
    ]
    if mechanical_action_class(request["action"]["argv"]) == "EXACT_PACKAGE_OR_TOPOLOGY_VERIFICATION":
        source_paths.append(Path(request["action"]["argv"][2]).resolve())
    package = {
        "head": git(repo, "rev-parse", "HEAD"),
        "tree": git(repo, "rev-parse", "HEAD^{tree}"),
        "source_digests": {path.name: file_digest(path) for path in source_paths},
        "action_executable": executable_evidence(repo, request["action"]["argv"]),
    }
    if mechanical_action_class(request["action"]["argv"]) in {
        "PURE_BOUNDED_READ_OR_VALIDATION", "SAFE_STATUS_OR_CONTAINMENT"
    }:
        package["worktree_read_set"] = worktree_read_set(repo)
    candidates = [
        skill_root.parent / "audit-state" / "SKILL.md",
        skill_root / "internal-procedures" / "audit-state.md",
    ]
    child = next((path for path in candidates if path.is_file()), None)
    if child is None:
        fail("exact audit-state child source is absent from the executing package")
    child_source = {"identity": str(child.resolve()), "digest": file_digest(child.resolve())}
    return package, child_source


def evaluate(
    repo: Path,
    common: str,
    args: argparse.Namespace,
    current: dict[str, str],
    request: dict[str, Any],
) -> tuple[str, str, list[str], dict[str, Any], str, str, str | None]:
    noncurrent, observed_inputs = request_observations(repo, current, request)
    decision, classification, invalidators = classify(request, noncurrent)
    package, child_source = executing_package_evidence(repo, request)
    identity_seed = {
        "request": request,
        "controller_record_oid": current["controller_record_oid"],
        "claim_id": current["claim_id"],
        "continuity_receipt": current["continuity_receipt"],
        "host_binding_generation": args.binding_generation,
        "package": package,
        "child_source": child_source,
    }
    transaction_id = digest_json({"kind": "transaction", "seed": identity_seed})
    obligation_id = digest_json({"kind": "obligation", "seed": identity_seed}) if decision == "REQUIRED" else None
    attributed = validate_binding(
        repo,
        common,
        args,
        current,
        request,
        obligation_id,
        transaction_id if obligation_id else None,
    )
    evidence = {
        "owner": {
            "controller_record_oid": current["controller_record_oid"],
            "claim_id": current["claim_id"],
            "run_root": current["explicit_run_root"],
        },
        "authority": {
            "continuity_generation": current["continuity_generation"],
            "continuity_receipt": current["continuity_receipt"],
        },
        "effect": {
            "action_identity": request["action"]["identity"],
            "action_digest": request["action"]["digest"],
            "derived_class": mechanical_action_class(request["action"]["argv"]),
        },
        "dependency": {
            "host_binding_generation": args.binding_generation,
            "host_correlation_id": attributed["correlation_id"],
        },
        "inputs": observed_inputs,
        "package": package,
        "child_source": child_source,
    }
    fingerprint = digest_json({"request": request, "mechanical_evidence": evidence})
    return decision, classification, invalidators, evidence, fingerprint, transaction_id, obligation_id


def validate_binding(
    repo: Path,
    common: str,
    args: argparse.Namespace,
    current: dict[str, str],
    request: dict[str, Any],
    obligation_id: str | None,
    transaction_id: str | None,
) -> dict[str, Any]:
    binding_core = Path(__file__).with_name("host-session-binding.py")
    lookup_raw = run(
        [
            sys.executable,
            str(binding_core),
            "--store",
            args.store,
            "lookup",
            "--host-id",
            args.host_id,
            "--host-session-id",
            args.host_session_id,
        ],
        cwd=repo,
        label="host binding lookup",
    )
    try:
        lookup = json.loads(lookup_raw)
    except json.JSONDecodeError:
        fail("host binding lookup returned malformed output")
    binding = lookup.get("binding") if lookup.get("status") == "BOUND" else None
    if not isinstance(binding, dict):
        fail("host session has no active exact binding")
    expected = {
        "binding_generation": args.binding_generation,
        "controller_id": args.controller,
        "claim_id": current["claim_id"],
        "explicit_run_root": current["explicit_run_root"],
        "repository_identity": str(repo),
        "git_common_directory_identity": common,
        "worktree_identity": str(repo),
        "applicable_continuity_generation": current["continuity_generation"],
        "applicable_continuity_receipt": current["continuity_receipt"],
    }
    for key, value in expected.items():
        if binding.get(key) != value:
            fail(f"host session binding has stale or foreign {key}")
    command = [
        sys.executable,
        str(binding_core),
        "--store",
        args.store,
        "validate-event",
        "--host-id",
        args.host_id,
        "--host-session-id",
        args.host_session_id,
        "--binding-generation",
        args.binding_generation,
        "--controller-id",
        args.controller,
        "--claim-id",
        current["claim_id"],
        "--explicit-run-root",
        current["explicit_run_root"],
        "--repository-identity",
        str(repo),
        "--git-common-directory-identity",
        common,
        "--worktree-identity",
        str(repo),
        "--continuity-generation",
        current["continuity_generation"],
        "--continuity-receipt",
        current["continuity_receipt"],
        "--event-id",
        request["boundary"]["event_id"],
    ]
    if obligation_id is not None and transaction_id is not None:
        command.extend(["--obligation-id", obligation_id, "--route-transaction-id", transaction_id])
    attributed_raw = run(command, cwd=repo, label="host event attribution")
    try:
        attributed = json.loads(attributed_raw)
    except json.JSONDecodeError:
        fail("host event attribution returned malformed output")
    if attributed.get("status") != "ATTRIBUTED":
        fail("host event attribution is unavailable")
    return attributed


@contextlib.contextmanager
def namespace_gate(common: str) -> Iterator[None]:
    common_root = Path(common).resolve()
    directory = common_root / "implementaudit-locks"
    for candidate in (common_root, directory):
        if os.path.lexists(candidate):
            info = os.lstat(candidate)
            if (
                not stat.S_ISDIR(info.st_mode)
                or stat.S_ISLNK(info.st_mode)
                or bool(getattr(info, "st_file_attributes", 0) & 0x400)
            ):
                fail("governed-writer namespace custody is aliased or unsafe")
    directory.mkdir(parents=True, exist_ok=True)
    gate = directory / "route-obligations.gate"
    if not gate.exists():
        try:
            descriptor = os.open(gate, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.write(descriptor, b"\0")
            os.close(descriptor)
        except FileExistsError:
            pass
    flags = os.O_RDWR | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(gate, flags)
    locked = False
    try:
        opened = os.fstat(descriptor)
        current = os.lstat(gate)
        unsafe = lambda item: (
            not stat.S_ISREG(item.st_mode)
            or stat.S_ISLNK(item.st_mode)
            or bool(getattr(item, "st_file_attributes", 0) & 0x400)
            or item.st_nlink != 1
            or item.st_size != 1
        )
        if unsafe(opened) or unsafe(current) or (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
            fail("governed-writer namespace gate is unsafe")
        if os.name == "nt":
            import msvcrt

            while True:
                try:
                    os.lseek(descriptor, 0, os.SEEK_SET)
                    msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                    locked = True
                    break
                except OSError as exc:
                    if exc.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                        raise
                    time.sleep(0.05)
        else:
            import fcntl

            fcntl.flock(descriptor, fcntl.LOCK_EX)
            locked = True
        yield
    finally:
        if locked and os.name == "nt":
            import msvcrt

            os.lseek(descriptor, 0, os.SEEK_SET)
            msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
        elif locked:
            import fcntl

            fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def projection_status(run_root: str, decision: str, oid: str) -> str:
    try:
        text = (Path(run_root) / "STATE.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return "UNAVAILABLE"
    decision_match = re.search(r"^\| Route decision projection \|\s*([^|]+?)\s*\|$", text, re.MULTILINE)
    record_match = re.search(r"^\| Route decision record \|\s*([^|]+?)\s*\|$", text, re.MULTILINE)
    if not decision_match or not record_match:
        return "LEGACY_ABSENT"
    projected_decision = decision_match.group(1).strip()
    projected_record = record_match.group(1).strip()
    return "CURRENT" if (projected_decision, projected_record) == (decision, oid) else "INVALID"


def common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--controller", required=True)
    parser.add_argument("--store", required=True)
    parser.add_argument("--host-id", required=True)
    parser.add_argument("--host-session-id", required=True)
    parser.add_argument("--binding-generation", required=True)
    parser.add_argument("--request", required=True)


def command_check(args: argparse.Namespace) -> None:
    repo, _, common = repo_context()
    request = read_request(args.request)
    with namespace_gate(common):
        oid, record = current_ref(repo, args.controller)
        if oid is None or record is None:
            fail("canonical route decision is absent")
        current = current_controller(repo, args.controller)
        bound_context = {
            "controller_id": args.controller,
            "claim_id": current["claim_id"],
            "explicit_run_root": current["explicit_run_root"],
            "continuity_generation": current["continuity_generation"],
            "continuity_receipt": current["continuity_receipt"],
            "host_id": args.host_id,
            "host_session_id": args.host_session_id,
            "host_binding_generation": args.binding_generation,
        }
        for key, value in bound_context.items():
            if record.get(key) != value:
                fail(f"route decision expired because bound {key} changed", decision=record["decision"])
        decision, classification, invalidators, evidence, fingerprint, transaction_id, obligation_id = evaluate(
            repo, common, args, current, request
        )
        if record.get("expiry_fingerprint") != fingerprint:
            fail("route decision expired because its bound scope or evidence changed", decision=record["decision"])
        if (decision, classification, invalidators, transaction_id, obligation_id) != (
            record.get("decision"),
            record.get("classification"),
            record.get("invalidators"),
            record.get("route_transaction_id"),
            record.get("obligation_id"),
        ):
            fail("route decision no longer agrees with the current predicate", decision=record["decision"])
        final_oid, _ = current_ref(repo, args.controller)
        final_current = current_controller(repo, args.controller)
        final_eval = evaluate(repo, common, args, final_current, request)
        if final_oid != oid or final_current != current or final_eval[4] != fingerprint:
            fail("route decision changed during the currentness check", decision=record["decision"])
        current_not_required = record["decision"] == "NOT_REQUIRED"
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "CURRENT",
            "decision": record["decision"],
            "classification": record["classification"],
            "advance_allowed": False,
            "admission_required": current_not_required,
            "enforcement_available": True,
            "record_oid": oid,
            "record_identity": record["record_identity"],
            "obligation_id": obligation_id,
            "route_state": record.get("route_state"),
            "projection_status": projection_status(current["explicit_run_root"], record["decision"], oid),
            "proof_layers": {
                "source_core": "PRESENT",
                "package": "UNVERIFIED",
                "install": "UNVERIFIED",
                "host_activation": "UNVERIFIED",
            },
            "host_activation_proven": False,
        }
    )
    if not current_not_required:
        raise SystemExit(3)


def command_decide(args: argparse.Namespace) -> None:
    repo, _, common = repo_context()
    request = read_request(args.request)
    with namespace_gate(common):
        current = current_controller(repo, args.controller)
        decision, classification, invalidators, evidence, fingerprint, transaction_id, obligation_id = evaluate(
            repo, common, args, current, request
        )
        old_oid, old = current_ref(repo, args.controller)
        expected = args.expected_record
        if expected == "none":
            if old_oid is not None:
                fail("route decision CAS expected absence but a current record exists", decision=old["decision"] if old else "PENDING")
            expected_oid = ZERO_OID
        elif not OID_RE.fullmatch(expected) or expected != old_oid:
            fail("route decision CAS expected record is stale", decision=old["decision"] if old else "PENDING")
        else:
            expected_oid = expected
        current_context_matches = bool(
            old
            and old.get("claim_id") == current["claim_id"]
            and old.get("explicit_run_root") == current["explicit_run_root"]
            and old.get("continuity_receipt") == current["continuity_receipt"]
            and old.get("host_binding_generation") == args.binding_generation
        )
        if old and current_context_matches and old.get("expiry_fingerprint") == fingerprint and old["decision"] == decision:
            emit(
                {
                    "schema": RESULT_SCHEMA,
                    "status": "DECIDED",
                    "decision": decision,
                    "classification": classification,
                    "advance_allowed": False,
                    "admission_required": decision == "NOT_REQUIRED",
                    "enforcement_available": True,
                    "record_oid": old_oid,
                    "record_identity": old["record_identity"],
                    "obligation_id": old.get("obligation_id"),
                    "route_state": old.get("route_state"),
                    "idempotent": True,
                }
            )
            return
        if (
            old
            and current_context_matches
            and old.get("decision") == "PENDING"
            and old.get("invalidators") in (["action-in-progress"], ["action-completion"])
            and old.get("expiry_fingerprint") == fingerprint
        ):
            fail("the exact action receipt was consumed or has unknown completion; it cannot be re-admitted")
        if old and old.get("decision") == "PENDING" and old.get("invalidators") == ["action-in-progress"]:
            fail("an action-in-progress record has unknown completion and cannot be replaced in H2A")
        if old and old["decision"] == "REQUIRED" and old.get("route_state") == "UNSATISFIED":
            fail("an active same-controller route obligation cannot be downgraded or replaced in H2A", decision="REQUIRED")
        record_base: dict[str, Any] = {
            "schema": RECORD_SCHEMA,
            "predicate_version": PREDICATE_VERSION,
            "controller_id": args.controller,
            "claim_id": current["claim_id"],
            "explicit_run_root": current["explicit_run_root"],
            "continuity_generation": current["continuity_generation"],
            "continuity_receipt": current["continuity_receipt"],
            "host_id": args.host_id,
            "host_session_id": args.host_session_id,
            "host_binding_generation": args.binding_generation,
            "host_correlation_id": evidence["dependency"]["host_correlation_id"],
            "boundary": request["boundary"],
            "scope": request["scope"],
            "action": request["action"],
            "evidence": {key: evidence[key] for key in ("owner", "authority", "effect", "dependency")},
            "inputs": evidence["inputs"],
            "package": evidence["package"],
            "child_source": evidence["child_source"],
            "decision": decision,
            "classification": classification,
            "invalidators": invalidators,
            "expiry_fingerprint": fingerprint,
            "expires_on": EXPIRES_ON,
            "predecessor_record_oid": old_oid,
            "route_transaction_id": transaction_id,
            "obligation_id": obligation_id,
            "route_state": "UNSATISFIED" if decision == "REQUIRED" else None,
            "child_lifecycle_owned": False,
            "consumed_record_oid": None,
        }
        record = {**record_base, "record_identity": digest_json(record_base)}
        raw = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
        new_oid = git(repo, "hash-object", "-w", "--stdin", input_text=raw)
        completed = subprocess.run(
            [str(trusted_host_executable(repo, "git")), "update-ref", ref_name(args.controller), new_oid, expected_oid],
            cwd=repo, env=sanitized_action_environment(), capture_output=True, text=True
        )
        if completed.returncode:
            fail("route decision CAS lost the current-record race", decision=decision)
        try:
            post_current = current_controller(repo, args.controller)
            post_eval = evaluate(repo, common, args, post_current, request)
            post_oid, _ = current_ref(repo, args.controller)
            if post_current != current or post_eval[4] != fingerprint or post_oid != new_oid:
                fail("route decision currentness changed during CAS", decision=decision)
        except SystemExit:
            # Compensate a currentness race only if this exact write is still
            # current. A lost compensation race leaves a stale record that all
            # check paths reject; it never becomes advancement authority.
            subprocess.run(
                [str(trusted_host_executable(repo, "git")), "update-ref", ref_name(args.controller), expected_oid, new_oid],
                cwd=repo,
                env=sanitized_action_environment(),
                capture_output=True,
                text=True,
                check=False,
            )
            raise
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "DECIDED",
            "decision": decision,
            "classification": classification,
            "advance_allowed": False,
            "admission_required": decision == "NOT_REQUIRED",
            "enforcement_available": True,
            "record_oid": new_oid,
            "record_identity": record["record_identity"],
            "predecessor_record_oid": old_oid,
            "obligation_id": obligation_id,
            "route_transaction_id": transaction_id,
            "route_state": record["route_state"],
            "invalidators": invalidators,
            "expires_on": EXPIRES_ON,
            "projection_status": projection_status(current["explicit_run_root"], decision, new_oid),
            "proof_layers": {
                "source_core": "PRESENT",
                "package": "UNVERIFIED",
                "install": "UNVERIFIED",
                "host_activation": "UNVERIFIED",
            },
            "host_activation_proven": False,
        }
    )


def execute_exact_action(
    repo: Path, request: dict[str, Any], executable: dict[str, str]
) -> dict[str, Any]:
    argv = list(request["action"]["argv"])
    if executable["resolved"] == "R0033:built-in":
        payload = json.dumps(worktree_read_set(repo), sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        return {
            "exit_code": 0,
            "stdout_bytes": len(payload),
            "stdout_digest": f"sha256:{hashlib.sha256(payload).hexdigest()}",
            "stderr_bytes": 0,
            "stderr_digest": f"sha256:{hashlib.sha256(b'').hexdigest()}",
        }
    resolved = Path(executable["resolved"])
    if file_digest(resolved) != executable["digest"]:
        fail("exact admitted action executable changed before execution")
    command = [str(resolved), *argv[1:]]
    if "interpreter_resolved" in executable:
        interpreter = Path(executable["interpreter_resolved"])
        if file_digest(interpreter) != executable["interpreter_digest"]:
            fail("exact admitted action interpreter changed before execution")
        command = [str(interpreter), str(resolved), *argv[1:]]
    environment = sanitized_action_environment()
    try:
        completed = subprocess.run(
            command,
            cwd=repo,
            env=environment,
            capture_output=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail(f"exact admitted action could not complete: {type(exc).__name__}")
    if len(completed.stdout) > 1_000_000 or len(completed.stderr) > 1_000_000:
        fail("exact admitted action output exceeded the bounded capture")
    if completed.returncode:
        fail(f"exact admitted action failed with exit {completed.returncode}")
    return {
        "exit_code": completed.returncode,
        "stdout_bytes": len(completed.stdout),
        "stdout_digest": f"sha256:{hashlib.sha256(completed.stdout).hexdigest()}",
        "stderr_bytes": len(completed.stderr),
        "stderr_digest": f"sha256:{hashlib.sha256(completed.stderr).hexdigest()}",
    }


def command_consume(args: argparse.Namespace) -> None:
    repo, _, common = repo_context()
    request = read_request(args.request)
    with namespace_gate(common):
        old_oid, old = current_ref(repo, args.controller)
        if old_oid is None or old is None or args.expected_record != old_oid:
            fail("action-consumption CAS expected record is stale")
        if old["decision"] != "NOT_REQUIRED":
            fail("only a current NOT_REQUIRED action receipt can be consumed", decision=old["decision"])
        current = current_controller(repo, args.controller)
        decision, classification, invalidators, evidence, fingerprint, _, _ = evaluate(
            repo, common, args, current, request
        )
        if (
            decision != "NOT_REQUIRED"
            or classification != "MECHANICALLY_NOT_REQUIRED"
            or invalidators
            or old.get("expiry_fingerprint") != fingerprint
            or old.get("claim_id") != current["claim_id"]
            or old.get("continuity_receipt") != current["continuity_receipt"]
            or old.get("host_binding_generation") != args.binding_generation
        ):
            fail("action receipt is stale and cannot be consumed", decision=old["decision"])
        in_progress_base = {
            **{key: value for key, value in old.items() if key != "record_identity"},
            "decision": "PENDING",
            "classification": "JUDGEMENT_REQUIRED",
            "invalidators": ["action-in-progress"],
            "predecessor_record_oid": old_oid,
            "route_transaction_id": digest_json(
                {
                    "kind": "action-in-progress",
                    "record_oid": old_oid,
                    "fingerprint": fingerprint,
                    "controller_record_oid": current["controller_record_oid"],
                    "continuity_receipt": current["continuity_receipt"],
                    "host_binding_generation": args.binding_generation,
                }
            ),
            "obligation_id": None,
            "route_state": None,
            "consumed_record_oid": old_oid,
            "host_correlation_id": evidence["dependency"]["host_correlation_id"],
        }
        in_progress = {**in_progress_base, "record_identity": digest_json(in_progress_base)}
        in_progress_raw = json.dumps(in_progress, sort_keys=True, separators=(",", ":")) + "\n"
        in_progress_oid = git(repo, "hash-object", "-w", "--stdin", input_text=in_progress_raw)
        admitted = subprocess.run(
            [str(trusted_host_executable(repo, "git")), "update-ref", ref_name(args.controller), in_progress_oid, old_oid],
            cwd=repo,
            env=sanitized_action_environment(),
            capture_output=True,
            text=True,
            check=False,
        )
        if admitted.returncode:
            fail("action-admission CAS lost the current-record race")
        admitted_current = current_controller(repo, args.controller)
        admitted_eval = evaluate(repo, common, args, admitted_current, request)
        admitted_oid, _ = current_ref(repo, args.controller)
        if admitted_current != current or admitted_eval[4] != fingerprint or admitted_oid != in_progress_oid:
            fail("action admission lost currentness before execution", decision="PENDING")

        action_result = execute_exact_action(repo, request, evidence["package"]["action_executable"])
        post_action_current = current_controller(repo, args.controller)
        post_action_eval = evaluate(repo, common, args, post_action_current, request)
        post_action_oid, _ = current_ref(repo, args.controller)
        if post_action_current != current or post_action_eval[4] != fingerprint or post_action_oid != in_progress_oid:
            fail("route authority changed while the exact action executed", decision="PENDING")
        successor_base = {
            **{key: value for key, value in in_progress.items() if key != "record_identity"},
            "decision": "PENDING",
            "classification": "JUDGEMENT_REQUIRED",
            "invalidators": ["action-completion"],
            "predecessor_record_oid": in_progress_oid,
            "route_transaction_id": digest_json(
                {
                    "kind": "action-completion",
                    "record_oid": in_progress_oid,
                    "fingerprint": fingerprint,
                    "controller_record_oid": current["controller_record_oid"],
                    "continuity_receipt": current["continuity_receipt"],
                    "host_binding_generation": args.binding_generation,
                }
            ),
            "obligation_id": None,
            "route_state": None,
            "consumed_record_oid": old_oid,
            "host_correlation_id": evidence["dependency"]["host_correlation_id"],
        }
        successor = {**successor_base, "record_identity": digest_json(successor_base)}
        raw = json.dumps(successor, sort_keys=True, separators=(",", ":")) + "\n"
        new_oid = git(repo, "hash-object", "-w", "--stdin", input_text=raw)
        completed = subprocess.run(
            [str(trusted_host_executable(repo, "git")), "update-ref", ref_name(args.controller), new_oid, in_progress_oid],
            cwd=repo,
            env=sanitized_action_environment(),
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode:
            fail("action-consumption CAS lost the current-record race")
        final_oid, _ = current_ref(repo, args.controller)
        final_current = current_controller(repo, args.controller)
        final_eval = evaluate(repo, common, args, final_current, request)
        if final_oid != new_oid or final_current != current or final_eval[4] != fingerprint:
            fail("completed action record lost currentness", decision="PENDING")
    emit(
        {
            "schema": RESULT_SCHEMA,
            "status": "ACTION_COMPLETE",
            "decision": "PENDING",
            "advance_allowed": False,
            "action_executed": True,
            "action_result": action_result,
            "enforcement_available": True,
            "record_oid": new_oid,
            "record_identity": successor["record_identity"],
            "consumed_record_oid": old_oid,
        }
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    decide = subparsers.add_parser("decide")
    common_args(decide)
    decide.add_argument("--expected-record", required=True)
    decide.set_defaults(run=command_decide)
    check = subparsers.add_parser("check")
    common_args(check)
    check.set_defaults(run=command_check)
    consume = subparsers.add_parser("consume")
    common_args(consume)
    consume.add_argument("--expected-record", required=True)
    consume.set_defaults(run=command_consume)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.run(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
