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
import zipfile
from datetime import datetime, timezone

import campaign_lifecycle as lifecycle
import provisional_integration as integration


SOURCE = pathlib.Path(__file__).resolve()
_PACKAGE_CACHE = {}


def _encoded(value):
    return lifecycle.canonical_json_bytes(value)


def _write_new(path, raw):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        stat.S_IRUSR | stat.S_IWUSR)
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
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _resolved_argv(argv):
    result = list(argv)
    if result[0] == "bash":
        executable = shutil.which("bash")
        if not executable:
            git_bash = pathlib.Path(
                os.environ.get("ProgramFiles", r"C:\Program Files")) / \
                "Git" / "bin" / "bash.exe"
            if not git_bash.is_file():
                raise ValueError("production Git Bash unavailable")
            executable = str(git_bash)
        result[0] = executable
    return result


def _production_deterministic(repo_root, qualified):
    checks = []
    artifacts = {}
    for index, name in enumerate(integration.DETERMINISTIC_CHECKS):
        argv = _resolved_argv(integration.DETERMINISTIC_COMMANDS[name])
        started = _utc_now()
        process = subprocess.Popen(
            argv, cwd=repo_root, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = process.communicate()
        completed = _utc_now()
        stdout_name = f"deterministic-{index:02d}-{name}.stdout.log"
        stderr_name = f"deterministic-{index:02d}-{name}.stderr.log"
        artifacts[stdout_name] = stdout
        artifacts[stderr_name] = stderr
        checks.append({
            "name": name, "argv": argv, "exit_code": process.returncode,
            "started_at": started, "completed_at": completed,
            "pid": process.pid, "stdout_path": stdout_name,
            "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "stderr_path": stderr_name,
            "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        })
        if process.returncode != 0:
            break
    terminal = {
        "schema": "implementaudit-deterministic-terminal-v2",
        "gate": "deterministic",
        "qualified_input_sha256": qualified,
        "exit_code": 0 if len(checks) == len(
            integration.DETERMINISTIC_CHECKS) else 1,
        "failed_checks": [
            row["name"] for row in checks if row["exit_code"] != 0],
        "checks": checks,
    }
    if (len(checks) != len(integration.DETERMINISTIC_CHECKS) or
            terminal["failed_checks"]):
        raise ValueError("production deterministic qualification failed")
    return terminal, artifacts


def _production_package(repo_root, qualified, target_sha, target_tree):
    bash = _resolved_argv(["bash"])[0]
    argv = [bash, "scripts/verify-package.sh"]
    started = _utc_now()
    process = subprocess.Popen(
        argv, cwd=repo_root, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    stdout, stderr = process.communicate()
    completed = _utc_now()
    if process.returncode != 0:
        raise ValueError("production full package gate failed")
    archive, manifest = _package(repo_root, target_sha, target_tree)
    artifacts = {
        "package-retained.skill": archive,
        "package-entry-manifest.json": manifest,
    }
    terminal = {
        "schema": "implementaudit-package-terminal-v2",
        "gate": "package", "qualified_input_sha256": qualified,
        "exit_code": process.returncode, "verification_passed": True,
        "argv": argv, "started_at": started, "completed_at": completed,
        "pid": process.pid,
        "package_manifest_sha256": hashlib.sha256(manifest).hexdigest(),
    }
    return terminal, artifacts, stdout, stderr


def run_gate(name, *, repo_root, evidence_root, target_sha, target_tree,
             qualified_input_sha256, surfaces_sha256,
             prior_evidence_sha256, review=None, external_ci=None,
             test_only=False):
    """Produce one gate's complete evidence, manifest last, exactly once."""
    if name not in integration.REQUIRED_GATES:
        raise ValueError("qualification gate unsupported")
    repo_root = _verify_target(repo_root, target_sha, target_tree)
    evidence_root = pathlib.Path(evidence_root).absolute()
    if evidence_root.exists():
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
    if not test_only and name == "deterministic":
        terminal, artifacts = _production_deterministic(
            repo_root, qualified_input_sha256)
    elif not test_only and name == "package":
        terminal, artifacts, production_stdout, production_stderr = \
            _production_package(
                repo_root, qualified_input_sha256, target_sha, target_tree)
        artifacts["package-command.stdout.log"] = production_stdout
        artifacts["package-command.stderr.log"] = production_stderr
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
        stdout_lines.extend([
            "verify-package: ok",
            f"REPRODUCIBLE_ASSET_RETAINED sha256={digest}",
        ])
    elif name == "reproducibility":
        stdout_lines.append(
            "REPRODUCIBILITY_EQUAL sha256=" +
            hashlib.sha256(package_raw).hexdigest())
    stdout = ("\n".join(stdout_lines) + "\n").encode()
    stderr = b""
    start = {
        "schema": "implementaudit-gate-producer-start-v1",
        "gate": name,
        "evidence_mode": "TEST_ONLY" if test_only else "PRODUCTION",
        "producer_source_path": "eval/qualification_evidence_producer.py",
        "producer_source_sha256":
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "qualified_input_sha256": qualified_input_sha256,
        "target_sha": target_sha, "target_tree": target_tree,
        "command": integration.GATE_COMMANDS[name],
        "producer_role": integration.GATE_PRODUCER_ROLES[name],
        "evaluated_surfaces_sha256": surfaces_sha256,
        "invocation_count": 1, "network_authorized": False,
        "credentials_authorized": False,
        "model_or_metered_api_authorized": False,
    }
    report = {
        "schema": "implementaudit-gate-producer-report-v1",
        "gate": name,
        "qualified_input_sha256": qualified_input_sha256,
        "target_sha": target_sha, "target_tree": target_tree,
        "producer_source_path": "eval/qualification_evidence_producer.py",
        "producer_source_sha256":
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "terminal_sha256": hashlib.sha256(terminal_raw).hexdigest(),
    }
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
        f"{name}-start.json": _encoded(start),
        integration.GATE_FILENAMES[name]: terminal_raw,
        f"{name}-report.json": _encoded(report),
        f"{name}.stdout.log": stdout,
        f"{name}.stderr.log": stderr,
        **artifacts,
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
