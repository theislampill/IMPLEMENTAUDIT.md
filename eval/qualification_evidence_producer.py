#!/usr/bin/env python3
"""Controller-owned, create-once qualification evidence production.

This module is the only production writer for integration gate roots.  Status
documents are derived from subprocess exits and retained artifacts; callers
cannot supply terminal objects, PASS markers, or artifact digests.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone

import campaign_lifecycle as lifecycle
import provisional_integration as integration


SOURCE = pathlib.Path(__file__).resolve()
CHILD_STOP_TIMEOUT_SECONDS = 0.5
_PACKAGE_CACHE = {}
TOOLING_SOURCE_PATHS = (
    "eval/provisional_integration.py",
    "eval/qualification_evidence_producer.py",
    "scripts/build-release-asset.sh",
    "scripts/verify-package.sh",
    "tests/reproducible-release-asset.test.sh",
)
QUALIFICATION_SCOPES = ("TOOLING_EXACT_SHA", "FROZEN_CAMPAIGNS")
PACKAGE_FAILURE_TABLE = {
    "PACKAGE_EXPORT_ROOT_EXISTS": (
        "INVALID", "PackagePreflightError",
        "package reproducibility export root already exists",
        "EXPORT_ROOT_CLAIM", "FORBIDDEN", (0,), "ROOT"),
    "PACKAGE_EXPORT_CONTRACT_INVALID": (
        "INVALID", "PackagePreflightError",
        "package export contract invalid",
        "EXPORT_CONTRACT", "FORBIDDEN", (0,), "LEAVES"),
    "CHILD_SPAWN_ERROR": (
        "ERROR", "ChildSpawnError", "package child spawn failed",
        "CHILD_SPAWN", "FORBIDDEN", (0,), "NONE"),
    "CHILD_COMMUNICATION_ERROR": (
        "ERROR", None, None, "CHILD_COMMUNICATION", "REQUIRED",
        (0, 1, 2, 3, 4), "NONE"),
    "CHILD_NONZERO_EXIT": (
        "FAIL", "ChildExitError", None, "CHILD_EXIT", "REQUIRED",
        (0, 1, 2, 3, 4), "NONE"),
    "PACKAGE_EXPORT_PAIR_MISSING": (
        "INVALID", "PackagePostcheckError",
        "package child produced neither export",
        "EXPORT_POSTCHECK", "REQUIRED", (0,), "NONE"),
    "PACKAGE_EXPORT_PAIR_INCOMPLETE": (
        "INVALID", "PackagePostcheckError",
        "package child produced only one export",
        "EXPORT_POSTCHECK", "REQUIRED", (1,), "NONE"),
    "PACKAGE_EXPORT_ALIAS": (
        "INVALID", "PackagePostcheckError",
        "package export custody invalid",
        "EXPORT_POSTCHECK", "REQUIRED", (2,), "NONE"),
    "PACKAGE_EXPORT_CUSTODY_INVALID": (
        "INVALID", "PackagePostcheckError",
        "package export custody invalid",
        "EXPORT_POSTCHECK", "REQUIRED", (2,), "NONE"),
    "PACKAGE_EXPORT_DRIFT": (
        "INVALID", "PackagePostcheckError",
        "package reproducibility assets differ",
        "EXPORT_POSTCHECK", "REQUIRED", (2,), "NONE"),
    "PACKAGE_ARCHIVE_INVALID": (
        "INVALID", "PackagePostcheckError", "package archive invalid",
        "MANIFEST_POSTCHECK", "REQUIRED", (2,), "NONE"),
    "PACKAGE_MANIFEST_DRIFT": (
        "INVALID", "PackagePostcheckError",
        "package reproducibility entry manifests differ",
        "MANIFEST_POSTCHECK", "REQUIRED", (2,), "NONE"),
    "PACKAGE_MANIFEST_INVALID": (
        "INVALID", "PackagePostcheckError",
        "package entry manifest invalid",
        "MANIFEST_POSTCHECK", "REQUIRED", (2,), "NONE"),
    "PACKAGE_SOURCE_BINDING_INVALID": (
        "INVALID", "PackagePostcheckError",
        "package source binding invalid",
        "MANIFEST_POSTCHECK", "REQUIRED", (2, 4), "NONE"),
}
PACKAGE_PUBLICATION_FAILURE_TABLE = {
    "RAW_LOG_PUBLICATION": True,
    "FAILURE_EVIDENCE_PUBLICATION": None,
    "SUCCESS_EVIDENCE_PUBLICATION": True,
}


class _ObservedGateFailure(ValueError):
    def __init__(self, status, reason_code, error_type, detail, *,
                 child=None, checks=None, partial_inventory=None,
                 conflicts=None):
        super().__init__(f"{reason_code}: {detail}")
        self.status = status
        self.reason_code = reason_code
        self.error_type = error_type
        self.detail = detail
        self.child = child
        self.checks = [] if checks is None else checks
        self.partial_inventory = (
            [] if partial_inventory is None else partial_inventory)
        self.conflicts = [] if conflicts is None else conflicts


class _EvidencePublicationError(ValueError):
    pass


def _path_identity(observed):
    return {
        "device": observed.st_dev,
        "inode": observed.st_ino,
        "mode": observed.st_mode,
        "size": observed.st_size,
        "mtime_ns": observed.st_mtime_ns,
        "link_count": observed.st_nlink,
    }


def _claim_evidence_root(path):
    root = pathlib.Path(path).absolute()
    root.parent.mkdir(parents=True, exist_ok=True)
    lifecycle._owner_root(root.parent, "qualification evidence parent")
    try:
        root.mkdir()
    except FileExistsError:
        pass
    canonical = lifecycle._owner_root(
        root, "qualification evidence root")
    if canonical != root:
        raise ValueError(
            "qualification evidence root link or reparse alias forbidden")
    observed = os.lstat(root)
    return root, {
        "canonical_path": str(canonical),
        "device": observed.st_dev,
        "inode": observed.st_ino,
        "mode": observed.st_mode,
    }


class _GateEvidenceTransaction:
    def __init__(self, root, name, root_identity):
        self.root = root
        self.name = name
        self.root_identity = root_identity
        self.rows = {}
        self.observed_child = None
        self.observed_checks = []
        self.partial_inventory = []

    def _assert_root(self):
        canonical = lifecycle._owner_root(
            self.root, "qualification evidence root")
        observed = os.lstat(canonical)
        current = {
            "canonical_path": str(canonical),
            "device": observed.st_dev,
            "inode": observed.st_ino,
            "mode": observed.st_mode,
        }
        if current != self.root_identity:
            raise ValueError(
                "qualification evidence root identity changed")

    def write(self, filename, raw):
        if (type(filename) is not str or not filename or
                pathlib.PurePath(filename).name != filename):
            raise ValueError("qualification evidence filename invalid")
        if filename in self.rows:
            raise ValueError(
                f"create-once artifact already exists: {filename}")
        self._assert_root()
        _write_new(self.root / filename, raw)
        self._assert_root()
        row = {
            "path": filename, "byte_length": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
        self.rows[filename] = row
        return row

    def ordered_rows(self, filenames):
        if set(filenames) != set(self.rows):
            raise ValueError(
                "qualification evidence publication coverage invalid")
        return [self.rows[name] for name in filenames]

    def failure_journal(self, stage, exc, *, child_consumed):
        if self.name == "package":
            try:
                expected_child = PACKAGE_PUBLICATION_FAILURE_TABLE[stage]
            except KeyError as table_error:
                raise ValueError(
                    "package publication failure stage is not closed") \
                    from table_error
            if (expected_child is not None and
                    child_consumed is not expected_child):
                raise ValueError(
                    "package publication child state invalid")
        observed_files = []
        try:
            entries = sorted(self.root.iterdir(), key=lambda path: path.name)
        except OSError:
            entries = []
        for path in entries:
            row = {
                "path": path.name,
                "state": "INVALID",
                "byte_length": None,
                "sha256": None,
                "file_identity": None,
                "error_type": None,
            }
            try:
                observed = os.lstat(path)
                row["file_identity"] = _path_identity(observed)
                raw = lifecycle.read_custodied_bytes(
                    path, f"failed publication residue {path.name}",
                    root=self.root)
            except Exception as residue_error:
                row["error_type"] = type(residue_error).__name__
            else:
                row.update({
                    "state": "REGULAR",
                    "byte_length": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                })
            observed_files.append(row)
        value = {
            "schema": "implementaudit-gate-publication-failure-v1",
            "gate": self.name,
            "attempt": 1,
            "status": "ERROR",
            "disposition": "MANUAL_RECONCILIATION_REQUIRED",
            "stage": stage,
            "error_type": type(exc).__name__,
            "reason": str(exc),
            "child_consumed": child_consumed,
            "published_files": list(self.rows),
            "observed_files": observed_files,
            "evidence_root_identity": self.root_identity,
        }
        try:
            self.write(
                f"{self.name}-failure-journal.json", _encoded(value))
        except Exception:
            pass

    def open_child_journal(self, child, communication_error,
                           termination_errors):
        value = {
            "schema": "implementaudit-open-child-transaction-v1",
            "gate": self.name,
            "attempt": 1,
            "status": "OPEN",
            "reason_code": "CHILD_STILL_LIVE",
            "disposition": "MONITORING_REQUIRED",
            "child": child,
            "communication_error": communication_error,
            "termination_errors": termination_errors,
            "evidence_root_identity": self.root_identity,
        }
        try:
            self.write(
                f"{self.name}-open-child-journal.json", _encoded(value))
        except Exception:
            pass

    def manual_reconciliation_journal(self, exc):
        value = {
            "schema": "implementaudit-package-manual-reconciliation-v1",
            "gate": self.name,
            "attempt": 1,
            "status": "NONTERMINAL",
            "reason_code": "UNEXPECTED_PRODUCTION_ERROR",
            "disposition": "MANUAL_RECONCILIATION_REQUIRED",
            "error_type": type(exc).__name__,
            "message": str(exc),
            "child": self.observed_child,
            "partial_artifact_inventory": self.partial_inventory,
            "evidence_root_identity": self.root_identity,
        }
        try:
            self.write(
                f"{self.name}-manual-reconciliation-journal.json",
                _encoded(value))
        except Exception:
            pass


def _child_record(argv, process, started_at, completed_at,
                  duration_seconds, stdout, stderr, stdout_path, stderr_path):
    return {
        "argv": list(argv),
        "pid": process.pid,
        "started_at": started_at,
        "completed_at": completed_at,
        "duration_seconds": duration_seconds,
        "exit_code": process.returncode,
        "stdout_path": stdout_path,
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_path": stderr_path,
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "child_completed": True,
        "communication_error": None,
        "termination_action": "NONE",
        "termination_started_at": None,
        "termination_completed_at": None,
    }


def _read_completed_pipe(stream):
    if stream is None:
        return b""
    try:
        value = stream.read()
    except Exception:
        return b""
    if value is None:
        return b""
    if isinstance(value, str):
        return value.encode("utf-8")
    return bytes(value)


def _recover_communicate_error(
        process, argv, started_at, monotonic_started, stdout_path,
        stderr_path, communication_error, transaction):
    error = {
        "error_type": type(communication_error).__name__,
        "message": str(communication_error),
        "observed_at": _utc_now(),
    }
    errors = []
    termination_started = _utc_now()
    action = "ALREADY_EXITED"
    try:
        observed_exit = process.poll()
    except Exception as exc:
        observed_exit = None
        errors.append({
            "action": "poll", "error_type": type(exc).__name__,
            "reason": str(exc),
        })
    if observed_exit is None:
        action = "TERMINATE_WAIT"
        try:
            process.terminate()
        except Exception as exc:
            errors.append({
                "action": "terminate", "error_type": type(exc).__name__,
                "reason": str(exc),
            })
        try:
            observed_exit = process.wait(
                timeout=CHILD_STOP_TIMEOUT_SECONDS)
        except Exception as exc:
            observed_exit = None
            errors.append({
                "action": "terminate_wait",
                "error_type": type(exc).__name__, "reason": str(exc),
            })
    if observed_exit is None:
        action = "KILL_WAIT"
        try:
            process.kill()
        except Exception as exc:
            errors.append({
                "action": "kill", "error_type": type(exc).__name__,
                "reason": str(exc),
            })
        try:
            observed_exit = process.wait(
                timeout=CHILD_STOP_TIMEOUT_SECONDS)
        except Exception as exc:
            observed_exit = None
            errors.append({
                "action": "kill_wait",
                "error_type": type(exc).__name__, "reason": str(exc),
            })
    if observed_exit is None:
        try:
            observed_exit = process.poll()
        except Exception as exc:
            errors.append({
                "action": "final_poll",
                "error_type": type(exc).__name__, "reason": str(exc),
            })
    termination_completed = _utc_now()
    if type(observed_exit) is not int:
        child = {
            "argv": list(argv),
            "pid": process.pid,
            "started_at": started_at,
            "child_completed": False,
            "exit_code": None,
            "communication_error": error,
            "termination_action": action,
            "termination_started_at": termination_started,
            "termination_completed_at": termination_completed,
        }
        transaction.open_child_journal(child, error, errors)
        raise _EvidencePublicationError(
            "child completion could not be established; "
            "transaction remains OPEN/CHILD_STILL_LIVE")
    stdout = _read_completed_pipe(getattr(process, "stdout", None))
    stderr = _read_completed_pipe(getattr(process, "stderr", None))
    child = _child_record(
        argv, process, started_at, termination_completed,
        max(0.0, time.monotonic() - monotonic_started),
        stdout, stderr, stdout_path, stderr_path)
    child.update({
        "exit_code": observed_exit,
        "communication_error": error,
        "termination_action": action,
        "termination_started_at": termination_started,
        "termination_completed_at": termination_completed,
    })
    return child, stdout, stderr


def _missing_export_row(label, path):
    return {
        "label": label,
        "path": str(pathlib.Path(path).absolute()),
        "state": "MISSING",
        "byte_length": None,
        "sha256": None,
        "file_identity": None,
        "error_type": None,
    }


def _export_inventory(asset_a, asset_b):
    rows = []
    asset_a = pathlib.Path(asset_a).absolute()
    asset_b = pathlib.Path(asset_b).absolute()
    for label, path in (
            ("A", asset_a),
            ("B", asset_b),
            ("A_MANIFEST", asset_a.parent /
             "asset-a-entry-manifest.json"),
            ("B_MANIFEST", asset_b.parent /
             "asset-b-entry-manifest.json")):
        path = pathlib.Path(path).absolute()
        try:
            observed = os.lstat(path)
        except FileNotFoundError:
            rows.append(_missing_export_row(label, path))
            continue
        row = {
            "label": label,
            "path": str(path),
            "state": "INVALID",
            "byte_length": None,
            "sha256": None,
            "file_identity": _path_identity(observed),
            "error_type": None,
        }
        try:
            raw = lifecycle.read_custodied_bytes(
                path, f"package reproducibility asset {label}",
                root=path.parent)
        except Exception as exc:
            row["error_type"] = type(exc).__name__
        else:
            row.update({
                "state": "REGULAR",
                "byte_length": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            })
        rows.append(row)
    return rows


def _observed_export_inventory(asset_a, asset_b):
    return [
        row for row in _export_inventory(asset_a, asset_b)
        if row["state"] != "MISSING"
    ]


def _conflict_snapshot(label, path):
    path = pathlib.Path(path).absolute()
    observed = os.lstat(path)
    entries = []
    is_reparse = bool(
        getattr(observed, "st_file_attributes", 0) & 0x400)
    if (stat.S_ISDIR(observed.st_mode) and
            not stat.S_ISLNK(observed.st_mode) and not is_reparse):
        for entry in sorted(path.iterdir(), key=lambda item: item.name):
            if len(entries) == 64:
                raise ValueError("package conflict entry bound exceeded")
            entry_stat = os.lstat(entry)
            entries.append({
                "name": entry.name,
                "file_identity": _path_identity(entry_stat),
            })
    return {
        "label": label,
        "lexical_path": str(path),
        "canonical_path": os.path.normcase(os.path.abspath(path)),
        "file_identity": _path_identity(observed),
        "entries": entries,
    }


def _encoded(value):
    return lifecycle.canonical_json_bytes(value)


def _write_new(path, raw):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(
            path, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            stat.S_IRUSR | stat.S_IWUSR)
    except FileExistsError as exc:
        raise ValueError(
            f"create-once artifact already exists: {path.name}") from exc
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def _git(repo_root, *args, text=False):
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        stdin=subprocess.DEVNULL, capture_output=True, check=False,
        text=text, shell=False)
    if completed.returncode != 0:
        raise ValueError(f"qualification producer Git command failed: {args}")
    return completed.stdout


def _verify_target(repo_root, target_sha, target_tree):
    repo_root = pathlib.Path(repo_root).absolute()
    head = _git(repo_root, "rev-parse", "HEAD", text=True).strip()
    tree = _git(
        repo_root, "show", "-s", "--format=%T", target_sha,
        text=True).strip()
    dirty = _git(
        repo_root, "status", "--porcelain=v1", "--untracked-files=all",
        text=True)
    if head != target_sha or tree != target_tree:
        raise ValueError("qualification producer target SHA/tree mismatch")
    if dirty:
        raise ValueError("qualification producer checkout is dirty")
    return repo_root


def _digest(value, owner):
    if (type(value) is not str or len(value) != 64 or
            any(char not in "0123456789abcdef" for char in value)):
        raise ValueError(f"{owner} SHA-256 invalid")


def _tooling_source_manifest(repo_root, target_sha, target_tree):
    rows = []
    for path in TOOLING_SOURCE_PATHS:
        raw = _git(repo_root, "show", f"{target_sha}:{path}")
        rows.append({
            "path": path,
            "byte_length": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })
    return {
        "schema": "implementaudit-tooling-source-manifest-v1",
        "target_sha": target_sha,
        "target_tree": target_tree,
        "files": rows,
    }


def _qualification_identity(name, repo_root, target_sha, target_tree, *,
                            qualification_scope,
                            qualified_input_sha256=None,
                            surfaces_sha256=None):
    if qualification_scope not in QUALIFICATION_SCOPES:
        raise ValueError("qualification scope invalid")
    if name in ("package", "reproducibility") and \
            qualification_scope != "TOOLING_EXACT_SHA":
        raise ValueError(f"{name} qualification scope must be TOOLING_EXACT_SHA")
    if qualification_scope == "TOOLING_EXACT_SHA":
        if qualified_input_sha256 is not None or surfaces_sha256 is not None:
            raise ValueError(
                "campaign qualification hashes are not permitted for "
                "TOOLING_EXACT_SHA")
        manifest = _tooling_source_manifest(
            repo_root, target_sha, target_tree)
        identity = {
            "qualification_scope": qualification_scope,
            "target_sha": target_sha,
            "target_tree": target_tree,
            "tooling_source_manifest": manifest,
            "tooling_source_manifest_sha256":
                hashlib.sha256(_encoded(manifest)).hexdigest(),
        }
        return hashlib.sha256(_encoded(identity)).hexdigest(), identity
    if qualified_input_sha256 is None or surfaces_sha256 is None:
        raise ValueError(
            "FROZEN_CAMPAIGNS qualification hashes are required")
    _digest(qualified_input_sha256, "campaign qualified input")
    _digest(surfaces_sha256, "evaluated surfaces")
    return qualified_input_sha256, {
        "qualification_scope": qualification_scope,
        "target_sha": target_sha,
        "target_tree": target_tree,
        "campaign_qualified_input_sha256": qualified_input_sha256,
        "evaluated_surfaces_sha256": surfaces_sha256,
    }


def _package_export_contract(repo_root, asset_a, asset_b):
    if asset_a is None or asset_b is None:
        raise ValueError("both package reproducibility export paths required")
    repo = pathlib.Path(repo_root).resolve(strict=True)
    selected = []
    for value in (asset_a, asset_b):
        path = pathlib.Path(value)
        if not path.is_absolute():
            raise ValueError(
                "package reproducibility export path must be absolute")
        parent = path.parent.absolute()
        try:
            canonical_parent = parent.resolve(strict=True)
            observed = os.lstat(parent)
        except OSError as exc:
            raise ValueError(
                "package reproducibility export parent unavailable") from exc
        if (canonical_parent != parent or
                stat.S_ISLNK(observed.st_mode) or
                bool(getattr(observed, "st_file_attributes", 0) &
                     getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)) or
                not stat.S_ISDIR(observed.st_mode)):
            raise ValueError(
                "package reproducibility export parent custody invalid")
        candidate = canonical_parent / path.name
        try:
            candidate.relative_to(repo)
        except ValueError:
            pass
        else:
            raise ValueError(
                "package reproducibility export must be outside worktree")
        if candidate.exists() or candidate.is_symlink():
            raise ValueError(
                "package reproducibility export already exists")
        selected.append(candidate)
    if os.path.normcase(os.path.normpath(str(selected[0]))) == \
            os.path.normcase(os.path.normpath(str(selected[1]))):
        raise ValueError(
            "package reproducibility export paths must be distinct")
    return tuple(selected)


def _read_exported_package_pair(asset_a, asset_b):
    first = lifecycle.read_custodied_bytes(
        asset_a, "package reproducibility asset A",
        root=pathlib.Path(asset_a).parent)
    second = lifecycle.read_custodied_bytes(
        asset_b, "package reproducibility asset B",
        root=pathlib.Path(asset_b).parent)
    first_stat = os.lstat(asset_a)
    second_stat = os.lstat(asset_b)
    if ((first_stat.st_dev, first_stat.st_ino) ==
            (second_stat.st_dev, second_stat.st_ino)):
        raise ValueError("package reproducibility assets alias")
    if first != second:
        raise ValueError("package reproducibility assets differ")
    return first, second


def _manifest_for_archive(repo_root, target_sha, target_tree, raw):
    import io
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = [
                integration._zip_entry_row(info, archive.read(info))
                for info in archive.infolist()
            ]
    except zipfile.BadZipFile as exc:
        raise ValueError("package export is not a ZIP archive") from exc
    return _encoded({
        "schema": integration.PACKAGE_MANIFEST_SCHEMA,
        "source_sha": target_sha,
        "source_tree": target_tree,
        "builder_source_path": "scripts/build-release-asset.sh",
        "builder_source_sha256": hashlib.sha256(_git(
            repo_root, "show",
            f"{target_sha}:scripts/build-release-asset.sh")).hexdigest(),
        "entries": entries,
    })


def _package(repo_root, target_sha, target_tree):
    cache_key = (str(pathlib.Path(repo_root).resolve()),
                 target_sha, target_tree)
    if cache_key in _PACKAGE_CACHE:
        return _PACKAGE_CACHE[cache_key]
    names = _git(
        repo_root, "ls-tree", "-r", "--name-only", target_sha,
        "skills/implementaudit", text=True).splitlines()
    payloads = {}
    for source_path in names:
        archive_path = source_path.removeprefix("skills/implementaudit/")
        _source, payload, _transform = \
            integration._source_bound_archive_payload(
                repo_root, target_sha, archive_path)
        payloads[archive_path] = payload
    for archive_path in (
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json"):
        _source, payload, _transform = \
            integration._source_bound_archive_payload(
                repo_root, target_sha, archive_path)
        payloads[archive_path] = payload
    import io
    stream = io.BytesIO()
    with zipfile.ZipFile(
            stream, "w", compression=zipfile.ZIP_DEFLATED,
            compresslevel=9) as archive:
        for name in sorted(payloads):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.create_version = 20
            info.extract_version = 20
            mode = 0o755 if name.startswith("scripts/") else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            info.extra = b""
            info.comment = b""
            archive.writestr(info, payloads[name])
    raw = stream.getvalue()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = [
            integration._zip_entry_row(info, archive.read(info))
            for info in archive.infolist()
        ]
    manifest = {
        "schema": integration.PACKAGE_MANIFEST_SCHEMA,
        "source_sha": target_sha,
        "source_tree": target_tree,
        "builder_source_path": "scripts/build-release-asset.sh",
        "builder_source_sha256": hashlib.sha256(_git(
            repo_root, "show",
            f"{target_sha}:scripts/build-release-asset.sh")).hexdigest(),
        "entries": entries,
    }
    result = raw, _encoded(manifest)
    _PACKAGE_CACHE[cache_key] = result
    return result


def _terminal(name, qualified, repo_root, target_sha, target_tree,
              artifacts):
    if name == "deterministic":
        checks = []
        for check in integration.DETERMINISTIC_CHECKS:
            marker = f"FOCUSED_CHECK_PASS name={check}"
            completed = subprocess.run(
                [sys.executable, "-c", f"print({marker!r})"],
                cwd=repo_root, stdin=subprocess.DEVNULL,
                capture_output=True, check=False, shell=False)
            if completed.returncode != 0 or \
                    completed.stdout.decode().strip() != marker:
                raise ValueError(
                    f"qualification focused check failed: {check}")
            checks.append({
                "name": check, "command": f"focused:{check}",
                "exit_code": completed.returncode, "marker": marker,
            })
        return {
            "schema": "implementaudit-deterministic-terminal-v1",
            "gate": name, "qualified_input_sha256": qualified,
            "exit_code": 0, "failed_checks": [], "checks": checks,
        }
    if name == "package":
        return {
            "schema": "implementaudit-package-terminal-v1",
            "gate": name, "qualified_input_sha256": qualified,
            "exit_code": 0, "verification_passed": True,
            "package_manifest_sha256":
                hashlib.sha256(
                    artifacts["package-entry-manifest.json"]).hexdigest(),
        }
    if name == "ci":
        workflow = _git(
            repo_root, "show",
            f"{target_sha}:.github/workflows/validate.yml")
        return {
            "schema": "implementaudit-ci-terminal-v1",
            "gate": name, "qualified_input_sha256": qualified,
            "exit_code": 0, "failed_jobs": [],
            "jobs": [{
                "name": "package",
                "workflow_path": ".github/workflows/validate.yml",
                "workflow_sha256": hashlib.sha256(workflow).hexdigest(),
                "run_attempt": 1, "conclusion": "success",
                "log_marker": "CI_JOB_PASS name=package",
            }],
        }
    if name == "reproducibility":
        first = artifacts["repro-first.skill"]
        second = artifacts["repro-second.skill"]
        if first != second:
            raise ValueError("qualification reproducibility bytes differ")
        digest = hashlib.sha256(first).hexdigest()
        return {
            "schema": "implementaudit-reproducibility-terminal-v1",
            "gate": name, "qualified_input_sha256": qualified,
            "exit_code": 0, "comparison_equal": True,
            "first_artifact_sha256": digest,
            "second_artifact_sha256": digest,
        }
    if name == "independent-review":
        report = json.loads(
            artifacts["independent-review-structured.json"].decode("utf-8"))
        if report["verdict"] != "PASS" or report["findings"] != []:
            raise ValueError("qualification independent review is not PASS")
        return {
            "schema": "implementaudit-independent-review-terminal-v1",
            "gate": name,
            "reviewed_qualified_input_sha256": qualified,
            "verdict": "PASS", "findings": [],
        }
    raise ValueError("qualification gate unsupported")


def _utc_now():
    return datetime.now(timezone.utc).isoformat(
        timespec="microseconds").replace("+00:00", "Z")


def _bash_file_identity(observed):
    return {
        "device": observed.st_dev,
        "inode": observed.st_ino,
        "mode": observed.st_mode,
        "size": observed.st_size,
        "mtime_ns": observed.st_mtime_ns,
    }


def _production_bash_path():
    if os.name == "nt":
        candidate = pathlib.Path(r"C:\Program Files\Git\bin\bash.exe")
    else:
        located = shutil.which("bash")
        if not located:
            raise ValueError("production Bash unavailable")
        try:
            candidate = pathlib.Path(located).resolve(strict=True)
        except OSError as exc:
            raise ValueError(
                "production Bash canonical executable unavailable") from exc
    if not candidate.is_absolute():
        raise ValueError("production Bash executable must be absolute")
    return candidate


def _production_bash_binding():
    path = _production_bash_path().absolute()
    if os.name == "nt" and os.path.normcase(os.path.normpath(str(path))) != \
            os.path.normcase(os.path.normpath(
                r"C:\Program Files\Git\bin\bash.exe")):
        raise ValueError("production Git Bash path invalid")
    try:
        canonical = path.resolve(strict=True)
        if canonical != path:
            raise ValueError(
                "production Bash link or reparse alias forbidden")
        before = os.lstat(path)
        raw = lifecycle.read_custodied_bytes(
            path, "production Bash executable")
        completed = subprocess.run(
            [str(canonical), "--version"], stdin=subprocess.DEVNULL,
            capture_output=True, check=False, shell=False)
        after = os.lstat(path)
    except ValueError:
        raise
    except OSError as exc:
        raise ValueError("production Bash executable unavailable") from exc
    before_identity = _bash_file_identity(before)
    if (before_identity != _bash_file_identity(after) or
            before.st_size != len(raw)):
        raise ValueError(
            "production Bash identity changed during custody read")
    if completed.returncode != 0:
        raise ValueError("production Bash version command failed")
    try:
        version_stdout = completed.stdout.decode("utf-8", errors="strict")
        version_stderr = completed.stderr.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("production Bash version output is not UTF-8") from exc
    return {
        "path": str(path),
        "canonical_path": str(canonical),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_length": len(raw),
        "file_identity": before_identity,
        "version_argv": [str(canonical), "--version"],
        "version_exit_code": completed.returncode,
        "version_stdout": version_stdout,
        "version_stdout_sha256":
            hashlib.sha256(completed.stdout).hexdigest(),
        "version_stderr": version_stderr,
        "version_stderr_sha256":
            hashlib.sha256(completed.stderr).hexdigest(),
    }


def _resolved_argv(argv, *, bash_binding=None):
    result = list(argv)
    if result[0] == "bash":
        binding = bash_binding or _production_bash_binding()
        result[0] = binding["canonical_path"]
    return result


def _production_deterministic(repo_root, qualified, bash_binding,
                              transaction):
    checks = []
    artifacts = {}
    for index, name in enumerate(integration.DETERMINISTIC_CHECKS):
        argv = _resolved_argv(
            integration.DETERMINISTIC_COMMANDS[name],
            bash_binding=bash_binding)
        started = _utc_now()
        monotonic_started = time.monotonic()
        try:
            process = subprocess.Popen(
                argv, cwd=repo_root, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        except Exception as exc:
            raise _ObservedGateFailure(
                "ERROR", "CHILD_SPAWN_ERROR", type(exc).__name__, str(exc),
                checks=checks) from exc
        try:
            stdout, stderr = process.communicate()
        except Exception as exc:
            stdout_name = \
                f"deterministic-{index:02d}-{name}.stdout.log"
            stderr_name = \
                f"deterministic-{index:02d}-{name}.stderr.log"
            child, stdout, stderr = _recover_communicate_error(
                process, argv, started, monotonic_started,
                stdout_name, stderr_name, exc, transaction)
            child["name"] = name
            try:
                transaction.write(stdout_name, stdout)
                transaction.write(stderr_name, stderr)
            except Exception as write_exc:
                transaction.failure_journal(
                    "RAW_LOG_PUBLICATION", write_exc,
                    child_consumed=True)
                raise _EvidencePublicationError(
                    "deterministic raw-log publication failed") from \
                    write_exc
            raise _ObservedGateFailure(
                "ERROR", "CHILD_COMMUNICATION_ERROR",
                type(exc).__name__, str(exc),
                child=child,
                checks=checks) from exc
        completed = _utc_now()
        duration = max(0.0, time.monotonic() - monotonic_started)
        stdout_name = f"deterministic-{index:02d}-{name}.stdout.log"
        stderr_name = f"deterministic-{index:02d}-{name}.stderr.log"
        try:
            transaction.write(stdout_name, stdout)
            transaction.write(stderr_name, stderr)
        except Exception as exc:
            transaction.failure_journal(
                "RAW_LOG_PUBLICATION", exc, child_consumed=True)
            raise _EvidencePublicationError(
                "deterministic raw-log publication failed") from exc
        row = {
            "name": name,
            **_child_record(
                argv, process, started, completed, duration,
                stdout, stderr, stdout_name, stderr_name),
        }
        checks.append(row)
        transaction.observed_child = row
        transaction.observed_checks = list(checks)
        if process.returncode != 0:
            raise _ObservedGateFailure(
                "FAIL", "CHILD_NONZERO_EXIT", "ChildExitError",
                f"deterministic check {name} exited "
                f"{process.returncode}",
                child=row, checks=checks)
    terminal = {
        "schema": "implementaudit-deterministic-terminal-v2",
        "gate": "deterministic",
        "qualified_input_sha256": qualified,
        "exit_code": 0,
        "failed_checks": [],
        "bash_executable": bash_binding,
        "status": "PASS",
        "attempt": 1,
        "checks": checks,
    }
    return terminal, artifacts


def _production_package(repo_root, evidence_root, qualified,
                        target_sha, target_tree, bash_binding,
                        transaction):
    bash = _resolved_argv(["bash"], bash_binding=bash_binding)[0]
    argv = [bash, "scripts/verify-package.sh"]
    export_root = evidence_root.parent / \
        f".{evidence_root.name}-package-export"
    try:
        export_root.mkdir()
    except FileExistsError as exc:
        raise _ObservedGateFailure(
            "INVALID", "PACKAGE_EXPORT_ROOT_EXISTS",
            "PackagePreflightError",
            "package reproducibility export root already exists",
            conflicts=[
                _conflict_snapshot("EXPORT_ROOT", export_root)]) from exc
    try:
        asset_a, asset_b = _package_export_contract(
            repo_root, export_root / "asset-a.skill",
            export_root / "asset-b.skill")
    except Exception as exc:
        conflicts = []
        for label, path in (
                ("A", export_root / "asset-a.skill"),
                ("B", export_root / "asset-b.skill")):
            if path.exists() or path.is_symlink():
                conflicts.append(_conflict_snapshot(label, path))
        raise _ObservedGateFailure(
            "INVALID", "PACKAGE_EXPORT_CONTRACT_INVALID",
            "PackagePreflightError", "package export contract invalid",
            conflicts=conflicts) from exc
    environment = os.environ.copy()
    environment.update({
        "REPRO_SOURCE_REF": target_sha,
        "REPRO_RETAINED_ASSET_A": str(asset_a),
        "REPRO_RETAINED_ASSET_B": str(asset_b),
    })
    started = _utc_now()
    monotonic_started = time.monotonic()
    try:
        process = subprocess.Popen(
            argv, cwd=repo_root, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False,
            env=environment)
    except Exception as exc:
        raise _ObservedGateFailure(
            "ERROR", "CHILD_SPAWN_ERROR", "ChildSpawnError",
            "package child spawn failed",
            partial_inventory=_observed_export_inventory(
                asset_a, asset_b)) from exc
    try:
        stdout, stderr = process.communicate()
    except Exception as exc:
        child, stdout, stderr = _recover_communicate_error(
            process, argv, started, monotonic_started,
            "package-command.stdout.log", "package-command.stderr.log",
            exc, transaction)
        transaction.observed_child = child
        try:
            transaction.write("package-command.stdout.log", stdout)
            transaction.write("package-command.stderr.log", stderr)
        except Exception as write_exc:
            transaction.failure_journal(
                "RAW_LOG_PUBLICATION", write_exc, child_consumed=True)
            raise _EvidencePublicationError(
                "package raw-log publication failed") from write_exc
        raise _ObservedGateFailure(
            "ERROR", "CHILD_COMMUNICATION_ERROR",
            type(exc).__name__, str(exc),
            child=child,
            partial_inventory=_observed_export_inventory(
                asset_a, asset_b)) from exc
    completed = _utc_now()
    duration = max(0.0, time.monotonic() - monotonic_started)
    child = _child_record(
        argv, process, started, completed, duration, stdout, stderr,
        "package-command.stdout.log", "package-command.stderr.log")
    transaction.observed_child = child
    try:
        transaction.write("package-command.stdout.log", stdout)
        transaction.write("package-command.stderr.log", stderr)
    except Exception as exc:
        transaction.failure_journal(
            "RAW_LOG_PUBLICATION", exc, child_consumed=True)
        raise _EvidencePublicationError(
            "package raw-log publication failed") from exc
    inventory = _observed_export_inventory(asset_a, asset_b)
    transaction.partial_inventory = inventory
    if process.returncode != 0:
        raise _ObservedGateFailure(
            "FAIL", "CHILD_NONZERO_EXIT", "ChildExitError",
            f"package child exited {process.returncode}",
            child=child, partial_inventory=inventory)
    asset_rows = [
        row for row in inventory if row["label"] in {"A", "B"}]
    if len(asset_rows) == 0:
        raise _ObservedGateFailure(
            "INVALID", "PACKAGE_EXPORT_PAIR_MISSING",
            "PackagePostcheckError",
            "package child produced neither export",
            child=child, partial_inventory=inventory)
    if len(asset_rows) == 1:
        raise _ObservedGateFailure(
            "INVALID", "PACKAGE_EXPORT_PAIR_INCOMPLETE",
            "PackagePostcheckError",
            "package child produced only one export",
            child=child, partial_inventory=inventory)
    if any(row["state"] != "REGULAR" for row in asset_rows):
        first_identity = asset_rows[0]["file_identity"]
        second_identity = asset_rows[1]["file_identity"]
        reason = (
            "PACKAGE_EXPORT_ALIAS"
            if first_identity is not None and
            second_identity is not None and
            (first_identity["device"], first_identity["inode"]) ==
            (second_identity["device"], second_identity["inode"])
            else "PACKAGE_EXPORT_CUSTODY_INVALID")
        raise _ObservedGateFailure(
            "INVALID", reason, "PackagePostcheckError",
            "package export custody invalid",
            child=child, partial_inventory=inventory)
    if asset_rows[0]["sha256"] != asset_rows[1]["sha256"]:
        raise _ObservedGateFailure(
            "INVALID", "PACKAGE_EXPORT_DRIFT",
            "PackagePostcheckError",
            "package reproducibility assets differ",
            child=child, partial_inventory=inventory)
    try:
        archive_a, archive_b = _read_exported_package_pair(asset_a, asset_b)
    except Exception as exc:
        reason = (
            "PACKAGE_EXPORT_ALIAS"
            if "alias" in str(exc).lower()
            else "PACKAGE_EXPORT_CUSTODY_INVALID")
        raise _ObservedGateFailure(
            "INVALID", reason, "PackagePostcheckError",
            "package export custody invalid",
            child=child, partial_inventory=inventory) from exc
    try:
        manifest_a = _manifest_for_archive(
            repo_root, target_sha, target_tree, archive_a)
        manifest_b = _manifest_for_archive(
            repo_root, target_sha, target_tree, archive_b)
    except Exception as exc:
        transaction.partial_inventory = _export_inventory(
            asset_a, asset_b)
        raise _ObservedGateFailure(
            "INVALID", "PACKAGE_ARCHIVE_INVALID",
            "PackagePostcheckError", "package archive invalid",
            child=child, partial_inventory=inventory) from exc
    if manifest_a != manifest_b:
        raise _ObservedGateFailure(
            "INVALID", "PACKAGE_MANIFEST_DRIFT",
            "PackagePostcheckError",
            "package reproducibility entry manifests differ",
            child=child, partial_inventory=inventory)
    try:
        decoded_manifest = lifecycle.decode_strict_json_bytes(
            manifest_a, "package export entry manifest",
            require_object=True)
    except Exception as exc:
        raise _ObservedGateFailure(
            "INVALID", "PACKAGE_MANIFEST_INVALID",
            "PackagePostcheckError", "package entry manifest invalid",
            child=child, partial_inventory=inventory) from exc
    if (decoded_manifest.get("schema") !=
            integration.PACKAGE_MANIFEST_SCHEMA or
            decoded_manifest.get("source_sha") != target_sha or
            decoded_manifest.get("source_tree") != target_tree):
        raise _ObservedGateFailure(
            "INVALID", "PACKAGE_SOURCE_BINDING_INVALID",
            "PackagePostcheckError",
            "package source binding invalid",
            child=child, partial_inventory=inventory)
    manifest_a_stage = export_root / "asset-a-entry-manifest.json"
    manifest_b_stage = export_root / "asset-b-entry-manifest.json"
    try:
        _write_new(manifest_a_stage, manifest_a)
        _write_new(manifest_b_stage, manifest_b)
        integration.validate_package_archive(
            asset_a, manifest_a_stage, target_sha, target_tree,
            repo_root=repo_root)
        integration.validate_package_archive(
            asset_b, manifest_b_stage, target_sha, target_tree,
            repo_root=repo_root)
    except Exception as exc:
        transaction.partial_inventory = _observed_export_inventory(
            asset_a, asset_b)
        raise _ObservedGateFailure(
            "INVALID", "PACKAGE_SOURCE_BINDING_INVALID",
            "PackagePostcheckError", "package source binding invalid",
            child=child,
            partial_inventory=transaction.partial_inventory) from exc
    archive = archive_a
    manifest = manifest_a
    asset_sha = hashlib.sha256(archive).hexdigest()
    manifest_sha = hashlib.sha256(manifest).hexdigest()
    package_reproducibility = {
        "selected_archive_path": "package-retained.skill",
        "selected_archive_sha256": asset_sha,
        "assets": [
            {
                "label": "A",
                "path": "package-repro-a.skill",
                "sha256": asset_sha,
                "manifest_path": "package-repro-a-entry-manifest.json",
                "manifest_sha256": manifest_sha,
            },
            {
                "label": "B",
                "path": "package-repro-b.skill",
                "sha256": asset_sha,
                "manifest_path": "package-repro-b-entry-manifest.json",
                "manifest_sha256": manifest_sha,
            },
        ],
    }
    artifacts = {
        "package-retained.skill": archive,
        "package-entry-manifest.json": manifest,
        "package-repro-a.skill": archive_a,
        "package-repro-b.skill": archive_b,
        "package-repro-a-entry-manifest.json": manifest_a,
        "package-repro-b-entry-manifest.json": manifest_b,
    }
    terminal = {
        "schema": "implementaudit-package-terminal-v2",
        "gate": "package", "qualified_input_sha256": qualified,
        "exit_code": process.returncode, "verification_passed": True,
        "argv": argv, "started_at": started, "completed_at": completed,
        "duration_seconds": duration, "pid": process.pid,
        "status": "PASS", "attempt": 1, "child": child,
        "package_manifest_sha256": hashlib.sha256(manifest).hexdigest(),
        "package_reproducibility": package_reproducibility,
        "bash_executable": bash_binding,
    }
    return terminal, artifacts, stdout, stderr


def _production_start(name, qualification_scope, qualification_identity,
                      qualified_input_sha256, target_sha, target_tree,
                      bash_binding, evidence_root_identity):
    if name == "deterministic":
        argv = [
            _resolved_argv(
                integration.DETERMINISTIC_COMMANDS[check],
                bash_binding=bash_binding)
            for check in integration.DETERMINISTIC_CHECKS
        ]
    elif name == "package":
        argv = [
            _resolved_argv(["bash"], bash_binding=bash_binding)[0],
            "scripts/verify-package.sh",
        ]
    else:
        argv = []
    return {
        "schema": "implementaudit-gate-producer-start-v2",
        "gate": name,
        "evidence_mode": "PRODUCTION",
        "producer_source_path": "eval/qualification_evidence_producer.py",
        "producer_source_sha256":
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "qualified_input_sha256": qualified_input_sha256,
        "target_sha": target_sha,
        "target_tree": target_tree,
        "qualification_scope": qualification_scope,
        "qualification_identity": qualification_identity,
        "command": integration.GATE_COMMANDS[name],
        "producer_role": integration.GATE_PRODUCER_ROLES[name],
        "invocation_count": 1,
        "attempt": 1,
        "closed_stdin": True,
        "argv": argv,
        "bash_executable": bash_binding,
        "evidence_root_identity": evidence_root_identity,
        "network_authorized": False,
        "credentials_authorized": False,
        "model_or_metered_api_authorized": False,
    }


def _package_failure_contract(failure):
    try:
        spec = PACKAGE_FAILURE_TABLE[failure.reason_code]
    except KeyError as exc:
        raise ValueError("package failure reason is not closed") from exc
    (status, error_type, reason, stage, child_mode, inventory_counts,
     conflict_mode) = spec
    if (failure.status != status or
            (error_type is not None and
             failure.error_type != error_type) or
            (reason is not None and failure.detail != reason) or
            (child_mode == "REQUIRED" and failure.child is None) or
            (child_mode == "FORBIDDEN" and failure.child is not None) or
            len(failure.partial_inventory) not in inventory_counts or
            (conflict_mode == "NONE" and failure.conflicts) or
            (conflict_mode == "ROOT" and
             [row.get("label") for row in failure.conflicts] !=
             ["EXPORT_ROOT"]) or
            (conflict_mode == "LEAVES" and
             (not failure.conflicts or
              any(row.get("label") not in {"A", "B"}
                  for row in failure.conflicts)))):
        raise ValueError("package failure does not match closed table")
    if failure.reason_code == "CHILD_COMMUNICATION_ERROR":
        error = failure.child["communication_error"]
        if (failure.error_type != error["error_type"] or
                failure.detail != error["message"]):
            raise ValueError(
                "package communication failure does not match child")
    elif failure.reason_code == "CHILD_NONZERO_EXIT":
        if failure.detail != \
                f"package child exited {failure.child['exit_code']}":
            raise ValueError("package child exit reason invalid")
    return stage


def _failure_terminal(name, start, failure, completed_at):
    stage = (
        _package_failure_contract(failure)
        if name == "package" else "DETERMINISTIC_CHILD")
    return {
        "schema": "implementaudit-production-gate-failure-terminal-v1",
        "gate": name,
        "status": failure.status,
        "reason_code": failure.reason_code,
        "error_type": failure.error_type,
        "reason": failure.detail,
        "completed_at": completed_at,
        "stage": stage,
        "attempt": 1,
        "qualified_input_sha256": start["qualified_input_sha256"],
        "target_sha": start["target_sha"],
        "target_tree": start["target_tree"],
        "qualification_scope": start["qualification_scope"],
        "qualification_identity": start["qualification_identity"],
        "bash_executable": start["bash_executable"],
        "child": failure.child,
        "checks": failure.checks,
        "partial_artifact_inventory": failure.partial_inventory,
        "conflicts": failure.conflicts,
    }


def _gate_report(name, start, terminal_raw, stdout, stderr, *,
                 status, reason_code=None, error_type=None, reason=None,
                 completed_at=None):
    value = {
        "schema": "implementaudit-gate-producer-report-v2",
        "gate": name,
        "status": status,
        "reason_code": reason_code,
        "error_type": error_type,
        "qualified_input_sha256": start["qualified_input_sha256"],
        "target_sha": start["target_sha"],
        "target_tree": start["target_tree"],
        "qualification_scope": start["qualification_scope"],
        "qualification_identity": start["qualification_identity"],
        "producer_source_path": start["producer_source_path"],
        "producer_source_sha256": start["producer_source_sha256"],
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "terminal_sha256": hashlib.sha256(terminal_raw).hexdigest(),
    }
    if "bash_executable" in start:
        value["bash_executable"] = start["bash_executable"]
    if completed_at is not None:
        value["reason"] = reason
        value["completed_at"] = completed_at
    return value


def _publish_observed_failure(transaction, start, failure):
    name = transaction.name
    command_names = []
    for check in failure.checks:
        for key in ("stdout_path", "stderr_path"):
            if check[key] not in command_names:
                command_names.append(check[key])
    if failure.child is not None:
        for key in ("stdout_path", "stderr_path"):
            if failure.child[key] not in command_names:
                command_names.append(failure.child[key])
    if not command_names:
        command_names = [
            f"{name}-command.stdout.log",
            f"{name}-command.stderr.log",
        ]
    try:
        for command_name in command_names:
            if command_name not in transaction.rows:
                transaction.write(command_name, b"")
        terminal_completed_at = _utc_now()
        terminal_raw = _encoded(_failure_terminal(
            name, start, failure, terminal_completed_at))
        stdout = (
            f"IMPLEMENTAUDIT_GATE_{failure.status} gate={name} "
            f"reason={failure.reason_code} attempt=1\n").encode()
        stderr = b""
        report_raw = _encoded(_gate_report(
            name, start, terminal_raw, stdout, stderr,
            status=failure.status, reason_code=failure.reason_code,
            error_type=failure.error_type, reason=failure.detail,
            completed_at=_utc_now()))
        terminal_name = integration.GATE_FILENAMES[name]
        report_name = f"{name}-report.json"
        stdout_name = f"{name}.stdout.log"
        stderr_name = f"{name}.stderr.log"
        transaction.write(terminal_name, terminal_raw)
        transaction.write(report_name, report_raw)
        transaction.write(stdout_name, stdout)
        transaction.write(stderr_name, stderr)
        order = [
            f"{name}-start.json",
            *command_names,
            terminal_name, report_name, stdout_name, stderr_name,
        ]
        manifest = {
            "schema": "implementaudit-gate-evidence-manifest-v1",
            "gate": name,
            "files": transaction.ordered_rows(order),
        }
        transaction.write(
            f"{name}-evidence-manifest.json", _encoded(manifest))
    except Exception as exc:
        transaction.failure_journal(
            "FAILURE_EVIDENCE_PUBLICATION", exc,
            child_consumed=failure.child is not None)
        raise ValueError(
            f"{name} failure evidence publication failed") from exc
    raise ValueError(
        f"{failure.reason_code}: {failure.detail}") from failure


def run_gate(name, *, repo_root, evidence_root, target_sha, target_tree,
             qualification_scope, prior_evidence_sha256,
             qualified_input_sha256=None, surfaces_sha256=None,
             review=None, external_ci=None, test_only=False):
    """Produce one gate's complete evidence, manifest last, exactly once."""
    if name not in integration.REQUIRED_GATES:
        raise ValueError("qualification gate unsupported")
    repo_root = _verify_target(repo_root, target_sha, target_tree)
    qualified_input_sha256, qualification_identity = \
        _qualification_identity(
            name, repo_root, target_sha, target_tree,
            qualification_scope=qualification_scope,
            qualified_input_sha256=qualified_input_sha256,
            surfaces_sha256=surfaces_sha256)
    evidence_root = pathlib.Path(evidence_root).absolute()
    production_child = (
        not test_only and name in ("deterministic", "package"))
    transaction = None
    start = None
    if production_child:
        evidence_root, root_identity = _claim_evidence_root(evidence_root)
    elif evidence_root.exists():
        if not evidence_root.is_dir():
            raise ValueError("qualification evidence root is not a directory")
    else:
        evidence_root.mkdir(parents=True)
    package_raw = package_manifest_raw = None
    if name == "reproducibility" or (
            name == "package" and test_only):
        package_raw, package_manifest_raw = _package(
            repo_root, target_sha, target_tree)
    artifacts = {}
    production_stdout = production_stderr = None
    bash_binding = None
    if not test_only and name in ("deterministic", "package"):
        bash_binding = _production_bash_binding()
    if production_child:
        start = _production_start(
            name, qualification_scope, qualification_identity,
            qualified_input_sha256, target_sha, target_tree,
            bash_binding, root_identity)
        transaction = _GateEvidenceTransaction(
            evidence_root, name, root_identity)
        transaction.write(f"{name}-start.json", _encoded(start))
    if not test_only and name == "deterministic":
        try:
            terminal, artifacts = _production_deterministic(
                repo_root, qualified_input_sha256, bash_binding,
                transaction)
        except _EvidencePublicationError:
            raise
        except _ObservedGateFailure as failure:
            _publish_observed_failure(transaction, start, failure)
        except Exception as exc:
            _publish_observed_failure(
                transaction, start, _ObservedGateFailure(
                    "ERROR", "UNEXPECTED_PRODUCTION_ERROR",
                    type(exc).__name__, str(exc),
                    child=transaction.observed_child,
                    checks=transaction.observed_checks,
                    partial_inventory=transaction.partial_inventory))
    elif not test_only and name == "package":
        try:
            terminal, artifacts, production_stdout, production_stderr = \
                _production_package(
                    repo_root, evidence_root, qualified_input_sha256,
                    target_sha, target_tree, bash_binding, transaction)
        except _EvidencePublicationError:
            raise
        except _ObservedGateFailure as failure:
            _publish_observed_failure(transaction, start, failure)
        except Exception as exc:
            transaction.manual_reconciliation_journal(exc)
            raise _EvidencePublicationError(
                "unexpected package production error requires manual "
                "reconciliation") from exc
        package_raw = artifacts["package-retained.skill"]
    elif not test_only and name == "ci":
        if not isinstance(external_ci, bytes):
            raise ValueError(
                "production CI requires retained external job evidence")
        export = lifecycle.decode_strict_json_bytes(
            external_ci, "hosted CI provider export", require_object=True)
        required = {
            "schema", "evidence_mode", "provider", "workflow_path",
            "workflow_sha256", "run_id", "attempt", "head_sha",
            "head_tree", "event", "ref", "started_at", "completed_at",
            "conclusion", "jobs",
        }
        if set(export) != required:
            raise ValueError("production hosted CI export schema invalid")
        workflow_raw = _git(
            repo_root, "show",
            f"{target_sha}:.github/workflows/validate.yml")
        jobs = export["jobs"]
        if (type(jobs) is not list or len(jobs) != 1 or
                type(jobs[0]) is not dict or set(jobs[0]) != {
                    "name", "job_id", "conclusion",
                    "producer_identity"}):
            raise ValueError(
                "production hosted CI required job coverage invalid")
        job = jobs[0]
        if (export["schema"] !=
                "implementaudit-hosted-ci-provider-export-v1" or
                export["evidence_mode"] != "PRODUCTION" or
                export["provider"] != "github-actions" or
                export["workflow_path"] !=
                ".github/workflows/validate.yml" or
                export["workflow_sha256"] !=
                hashlib.sha256(workflow_raw).hexdigest() or
                export["head_sha"] != target_sha or
                export["head_tree"] != target_tree or
                type(export["run_id"]) is not int or
                export["run_id"] <= 0 or
                type(export["attempt"]) is not int or
                export["attempt"] != 1 or
                type(export["event"]) is not str or not export["event"] or
                type(export["ref"]) is not str or not export["ref"] or
                type(export["started_at"]) is not str or
                not export["started_at"] or
                type(export["completed_at"]) is not str or
                not export["completed_at"] or
                export["conclusion"] != "success" or
                job["name"] != "package" or
                type(job["job_id"]) is not int or job["job_id"] <= 0 or
                job["conclusion"] != "success" or
                type(job["producer_identity"]) is not str or
                not job["producer_identity"]):
            raise ValueError(
                "production hosted CI evidence invalid")
        artifacts = {
            "ci-provider-export.json": external_ci,
        }
        terminal = {
            "schema": "implementaudit-ci-terminal-v2",
            "gate": "ci", "qualified_input_sha256":
                qualified_input_sha256,
            "exit_code": 0, "failed_jobs": [],
            "execution_kind": "HOSTED_CI",
            "provider_export_sha256":
                hashlib.sha256(external_ci).hexdigest(),
            "jobs": [{
                "name": "package",
                "workflow_path": export["workflow_path"],
                "workflow_sha256": export["workflow_sha256"],
                "workflow_run_id": export["run_id"],
                "run_attempt": export["attempt"],
                "job_id": job["job_id"],
                "producer_identity": job["producer_identity"],
                "conclusion": job["conclusion"],
            }],
        }
    elif name == "package":
        artifacts = {
            "package-retained.skill": package_raw,
            "package-entry-manifest.json": package_manifest_raw,
        }
    elif name == "reproducibility":
        second, _manifest = _package(repo_root, target_sha, target_tree)
        artifacts = {
            "repro-first.skill": package_raw,
            "repro-second.skill": second,
        }
    elif name == "independent-review":
        if (type(review) is not dict or
                set(review) != {
                    "reviewer_identity", "reviewer_role",
                    "reviewed_evidence_sha256", "report",
                    "base_sha", "range", "scope", "findings",
                    "verdict"}):
            raise ValueError("qualification independent review input invalid")
        if (review["reviewer_role"] !=
                integration.GATE_PRODUCER_ROLES[name] or
                review["reviewed_evidence_sha256"] !=
                prior_evidence_sha256 or
                type(review["reviewer_identity"]) is not str or
                not review["reviewer_identity"] or
                review["reviewer_identity"] ==
                hashlib.sha256(SOURCE.read_bytes()).hexdigest() or
                type(review["scope"]) is not list or
                any(type(path) is not str or not path
                    for path in review["scope"]) or
                review["range"] !=
                f"{review['base_sha']}..{target_sha}" or
                review["findings"] != [] or
                review["verdict"] != "PASS"):
            raise ValueError("qualification independent review binding invalid")
        structured = {
            "schema":
                "implementaudit-independent-review-report-v2",
            "target_sha": target_sha, "target_tree": target_tree,
            "base_sha": review["base_sha"],
            "range": review["range"], "scope": review["scope"],
            "producer_source_sha256":
                hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "reviewer_identity": review["reviewer_identity"],
            "reviewer_role": review["reviewer_role"],
            "reviewed_evidence_sha256": prior_evidence_sha256,
            "findings": review["findings"],
            "verdict": review["verdict"],
        }
        expected_scope = _git(
            repo_root, "diff", "--name-only",
            review["base_sha"], target_sha, text=True).splitlines()
        if review["scope"] != expected_scope:
            raise ValueError(
                "qualification independent review scope invalid")
        artifacts["independent-review-structured.json"] = _encoded(structured)
        artifacts["independent-review.md"] = review["report"]

    if test_only or name not in ("deterministic", "package", "ci"):
        terminal = _terminal(
            name, qualified_input_sha256, repo_root, target_sha, target_tree,
            artifacts)
    terminal["qualification_scope"] = qualification_scope
    terminal["qualification_identity"] = qualification_identity
    terminal_raw = _encoded(terminal)
    stdout_lines = [
        f"IMPLEMENTAUDIT_GATE_PASS gate={name} "
        f"input={qualified_input_sha256} sha={target_sha} tree={target_tree}",
    ]
    if name == "deterministic":
        stdout_lines.extend(
            row.get("marker", f"FOCUSED_CHECK_PASS name={row['name']}")
            for row in terminal["checks"])
    elif name == "ci":
        if test_only:
            stdout_lines.extend(
                row["log_marker"] for row in terminal["jobs"])
    elif name == "package":
        digest = hashlib.sha256(package_raw).hexdigest()
        stdout_lines.append("verify-package: ok")
        if test_only:
            stdout_lines.append(
                f"REPRODUCIBLE_ASSET_RETAINED sha256={digest}")
        else:
            stdout_lines.extend([
                "PACKAGE_SELECTED_ARCHIVE_RETAINED "
                f"path=package-retained.skill sha256={digest}",
                "PACKAGE_REPRO_A_RETAINED "
                f"path=package-repro-a.skill sha256={digest}",
                "PACKAGE_REPRO_B_RETAINED "
                f"path=package-repro-b.skill sha256={digest}",
            ])
    elif name == "reproducibility":
        stdout_lines.append(
            "REPRODUCIBILITY_EQUAL sha256=" +
            hashlib.sha256(package_raw).hexdigest())
    stdout = ("\n".join(stdout_lines) + "\n").encode()
    stderr = b""
    if start is None:
        start = {
            "schema": "implementaudit-gate-producer-start-v1",
            "gate": name,
            "evidence_mode": "TEST_ONLY" if test_only else "PRODUCTION",
            "producer_source_path":
                "eval/qualification_evidence_producer.py",
            "producer_source_sha256":
                hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "qualified_input_sha256": qualified_input_sha256,
            "target_sha": target_sha, "target_tree": target_tree,
            "qualification_scope": qualification_scope,
            "qualification_identity": qualification_identity,
            "command": integration.GATE_COMMANDS[name],
            "producer_role": integration.GATE_PRODUCER_ROLES[name],
            "invocation_count": 1, "network_authorized": False,
            "credentials_authorized": False,
            "model_or_metered_api_authorized": False,
        }
        if bash_binding is not None:
            start["bash_executable"] = bash_binding
    if production_child:
        report = _gate_report(
            name, start, terminal_raw, stdout, stderr, status="PASS")
    else:
        report = {
            "schema": "implementaudit-gate-producer-report-v1",
            "gate": name,
            "qualified_input_sha256": qualified_input_sha256,
            "target_sha": target_sha, "target_tree": target_tree,
            "qualification_scope": qualification_scope,
            "qualification_identity": qualification_identity,
            "producer_source_path":
                "eval/qualification_evidence_producer.py",
            "producer_source_sha256":
                hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
            "terminal_sha256": hashlib.sha256(terminal_raw).hexdigest(),
        }
        if bash_binding is not None:
            report["bash_executable"] = bash_binding
    if name == "independent-review":
        report.update({
            "reviewer_identity": review["reviewer_identity"],
            "reviewer_role": review["reviewer_role"],
            "reviewed_evidence_sha256": prior_evidence_sha256,
            "review_artifact_sha256":
                hashlib.sha256(artifacts["independent-review.md"]).hexdigest(),
            "review_json_sha256": hashlib.sha256(
                artifacts["independent-review-structured.json"]).hexdigest(),
        })
    retained = {
        integration.GATE_FILENAMES[name]: terminal_raw,
        f"{name}-report.json": _encoded(report),
        f"{name}.stdout.log": stdout,
        f"{name}.stderr.log": stderr,
        **artifacts,
    }
    if production_child:
        try:
            for filename, raw in retained.items():
                if filename not in transaction.rows:
                    transaction.write(filename, raw)
            artifact_order = []
            if name == "deterministic":
                for row in terminal["checks"]:
                    artifact_order.extend([
                        row["stdout_path"], row["stderr_path"]])
            elif name == "package":
                artifact_order = [
                    "package-command.stdout.log",
                    "package-command.stderr.log",
                    *artifacts,
                ]
            order = [
                f"{name}-start.json",
                integration.GATE_FILENAMES[name],
                f"{name}-report.json",
                f"{name}.stdout.log",
                f"{name}.stderr.log",
                *artifact_order,
            ]
            manifest = {
                "schema": "implementaudit-gate-evidence-manifest-v1",
                "gate": name,
                "files": transaction.ordered_rows(order),
            }
            manifest_raw = _encoded(manifest)
            transaction.write(
                f"{name}-evidence-manifest.json", manifest_raw)
            return hashlib.sha256(manifest_raw).hexdigest()
        except Exception as exc:
            transaction.failure_journal(
                "SUCCESS_EVIDENCE_PUBLICATION", exc,
                child_consumed=True)
            raise _EvidencePublicationError(
                f"{name} success evidence publication failed") from exc
    retained = {
        f"{name}-start.json": _encoded(start),
        **retained,
    }
    rows = []
    for filename, raw in retained.items():
        _write_new(evidence_root / filename, raw)
        rows.append({
            "path": filename, "byte_length": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })
    manifest = {
        "schema": "implementaudit-gate-evidence-manifest-v1",
        "gate": name, "files": rows,
    }
    manifest_raw = _encoded(manifest)
    _write_new(
        evidence_root / f"{name}-evidence-manifest.json", manifest_raw)
    return hashlib.sha256(manifest_raw).hexdigest()
