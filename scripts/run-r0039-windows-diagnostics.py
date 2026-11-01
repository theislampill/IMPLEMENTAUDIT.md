#!/usr/bin/env python3
"""Disposable hosted kernel and grouped-ref diagnostics at an exact source.

This never invokes claim-run, provisions a controller, or admits a native resume.
The fixture and recorder bytes are unchanged. The harness retains temporary
evidence before cleanup and captures real Git output before test substitutions.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import traceback
import unittest

QUALIFIED_SOURCE = "4af2e43b4047cd577aa6b56eecd5b27c5f0e45e0"
QUALIFIED_TREE = "8cb97d13e2b4f5e8bf99cc3e6e17e9267cbdef77"
BRANCH = "refs/heads/pro/dg30-r0039-windows-diagnostic-20261101"
DIAGNOSTIC_PATHS = {
    ".github/workflows/dg30-windows-diagnostic.yml",
    "scripts/run-r0039-windows-diagnostics.py",
}
SOURCE_PATHS = [
    "scripts/r0039-windows-job.py",
    "scripts/check-r0039-windows-resume.py",
    "scripts/run-r0039-windows-resume.py",
    "fixtures/canonical-state-rotation/windows_job_test.py",
    "fixtures/canonical-state-rotation/windows_qualification_test.py",
    "tests/canonical-state-rotation.test.sh",
    "docs/integration/dg30-windows-qualification-20261101.md",
    "fixtures/canonical-state-rotation/ref_group_test.py",
    "fixtures/canonical-state-rotation/windows_custody_test.py",
    "skills/implementaudit/scripts/claim-run-rotation.py",
    "skills/implementaudit/scripts/canonical_custody.py",
]


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical(value):
    path = Path(value)
    if not path.is_absolute() or ".." in path.parts:
        raise RuntimeError("tool path is not absolute and unaliased")
    for part in (path, *path.parents):
        row = part.lstat()
        if stat.S_ISLNK(row.st_mode) or getattr(row, "st_file_attributes", 0) & 0x400:
            raise RuntimeError("tool path traverses a symlink or reparse point")
    if not path.is_file():
        raise RuntimeError("tool is not a regular file")
    return path.resolve(strict=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    summary = {"schema": "dg30.hosted-windows-diagnostics.v1", "status": "INCOMPLETE",
               "scope": "three disposable WindowsKernelIntegration and seven RefGroup tests; no controller or original operation",
               "original_resume_performed": False, "native_authority": "NONE",
               "qualified_source": QUALIFIED_SOURCE, "qualified_tree": QUALIFIED_TREE}
    exit_code = 1
    began = time.monotonic()
    cleanup_rows = []
    capture_errors = []
    try:
        if os.name != "nt" or sys.platform != "win32":
            raise RuntimeError("actual Windows is required; no skip-based success")
        if os.environ.get("IMPLEMENTAUDIT_WINDOWS_JOB_CONTROLS") != "1":
            raise RuntimeError("explicit disposable diagnostic opt-in is missing")
        if os.environ.get("GITHUB_REF") != BRANCH or os.environ.get("GITHUB_EVENT_NAME") != "push":
            raise RuntimeError("only the exact authorized diagnostic branch push is admitted")
        if os.environ.get("GITHUB_REPOSITORY") != "theislampill/IMPLEMENTAUDIT.md":
            raise RuntimeError("foreign diagnostic repository")
        source = Path(__file__).resolve().parents[1]
        summary["host"] = {"platform": platform.platform(), "windows_version": list(sys.getwindowsversion()),
                           "python_version": sys.version, "architecture": platform.machine()}
        summary["job"] = {key: os.environ.get(key) for key in (
            "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_REF", "GITHUB_EVENT_NAME", "GITHUB_RUN_ID",
            "GITHUB_RUN_ATTEMPT", "GITHUB_JOB", "GITHUB_WORKFLOW", "RUNNER_OS", "RUNNER_ARCH",
            "RUNNER_ENVIRONMENT", "ImageOS", "ImageVersion")}
        python = physical(sys.executable)
        policy_spec = importlib.util.spec_from_file_location("dg30_direct_git_policy", source / "scripts/check-r0039-windows-resume.py")
        policy = importlib.util.module_from_spec(policy_spec)
        policy_spec.loader.exec_module(policy)
        available = [value for value in policy.DIRECT_GIT_EXECUTABLES if Path(value).is_file()]
        if len(available) != 1:
            raise RuntimeError("exactly one supported direct Git image must be available: " + repr(available))
        policy.direct_git_layout(available[0])
        git = physical(available[0])
        bash = physical(r"C:\Program Files\Git\bin\bash.exe")
        summary["tools"] = {name: {"path": str(path), "sha256": digest(path), "bytes": path.stat().st_size}
                            for name, path in (("python", python), ("git", git), ("bash", bash))}
        # Children receive only the OS/tool startup requirements, never an
        # inherited Actions credential, GitHub token, or Python startup hook.
        allowed = {"SystemRoot", "WINDIR", "COMSPEC", "TEMP", "TMP", "PATH", "PATHEXT",
                   "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE"}
        clean = {key: value for key, value in os.environ.items() if key.upper() in {k.upper() for k in allowed}}
        clean["IMPLEMENTAUDIT_WINDOWS_JOB_CONTROLS"] = "1"
        clean["IMPLEMENTAUDIT_WINDOWS_JOB_GIT"] = str(git)
        os.environ.clear()
        os.environ.update(clean)

        def run_git(*arguments):
            return subprocess.check_output([str(git), "-C", str(source), *arguments], text=True).strip()

        head, tree = run_git("rev-parse", "HEAD"), run_git("rev-parse", "HEAD^{tree}")
        summary["executed_head"], summary["executed_tree"] = head, tree
        if head != summary["job"]["GITHUB_SHA"] or run_git("rev-parse", QUALIFIED_SOURCE + "^{tree}") != QUALIFIED_TREE:
            raise RuntimeError("source/job identity mismatch")
        subprocess.run([str(git), "-C", str(source), "merge-base", "--is-ancestor", QUALIFIED_SOURCE, head], check=True)
        if set(run_git("diff", "--name-only", QUALIFIED_SOURCE, head).splitlines()) != DIAGNOSTIC_PATHS:
            raise RuntimeError("diagnostic branch changed the reviewed source population")
        if run_git("status", "--porcelain", "--untracked-files=no"):
            raise RuntimeError("tracked source is dirty")
        bindings = []
        for relative in [*SOURCE_PATHS, *sorted(DIAGNOSTIC_PATHS)]:
            path = source / relative
            oid = run_git("rev-parse", "HEAD:" + relative)
            if run_git("hash-object", str(path)) != oid:
                raise RuntimeError("working source differs from committed blob: " + relative)
            blob = subprocess.check_output([str(git), "-C", str(source), "cat-file", "blob", oid])
            if hashlib.sha256(blob).hexdigest() != digest(path):
                raise RuntimeError("working source bytes differ from exact committed bytes: " + relative)
            bindings.append({"path": relative, "blob_oid": oid, "sha256": digest(path), "bytes": path.stat().st_size})
        summary["source_files"] = bindings
        summary["git_version"] = run_git("--version")
        dump(out / "source-job-binding.json", summary)

        original_temporary = tempfile.TemporaryDirectory
        original_tempdir = tempfile.tempdir
        temporary_root = out / "temporary"
        temporary_root.mkdir()
        tempfile.tempdir = str(temporary_root)
        active_test = [None]
        ref_tools = []

        class EvidenceResult(unittest.TextTestResult):
            def startTest(self, test):
                active_test[0] = test.id()
                super().startTest(test)

            def stopTest(self, test):
                if hasattr(test, "exe"):
                    try:
                        selected = physical(test.exe)
                        ref_tools.append({"test": test.id(), "path": str(selected),
                                          "sha256": digest(selected), "bytes": selected.stat().st_size})
                    except Exception as exc:
                        capture_errors.append("grouped-ref tool identity: " + str(exc))
                active_test[0] = None
                super().stopTest(test)

        class RetainedTemporaryDirectory(original_temporary):
            def cleanup(self):
                path = Path(self.name)
                if path.exists():
                    row = {"test": active_test[0], "original_path": str(path),
                           "copy": f"operations/{len(cleanup_rows) + 1:02d}-{path.name}"}
                    cleanup_rows.append(row)
                    try:
                        shutil.copytree(path, out / row["copy"])
                        row["evidence_copied"] = True
                    except Exception as exc:
                        row["evidence_copied"] = False
                        capture_errors.append(type(exc).__name__ + ": " + str(exc))
                        # Keep the original inside the artifact root even if
                        # copying fails; neither __exit__ nor GC may erase it.
                        self._finalizer.detach()
                        row["original_retained_after_capture_failure"] = True
                    else:
                        super().cleanup()
                    row["temporary_directory_removed"] = not path.exists()

        tempfile.TemporaryDirectory = RetainedTemporaryDirectory
        try:
            test_path = source / "fixtures/canonical-state-rotation/windows_job_test.py"
            spec = importlib.util.spec_from_file_location("dg30_windows_job_test", test_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.WindowsKernelIntegration)
            with (out / "unittest.log").open("x", encoding="utf-8") as stream:
                result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=EvidenceResult, failfast=True).run(suite)
            print((out / "unittest.log").read_text(encoding="utf-8"), flush=True)
            summary["tests"] = {"run": result.testsRun, "skipped": [(str(t), reason) for t, reason in result.skipped],
                                "failures": [(str(t), error) for t, error in result.failures],
                                "errors": [(str(t), error) for t, error in result.errors],
                                "was_successful": result.wasSuccessful()}
            if not result.wasSuccessful() or result.testsRun != 3 or result.skipped:
                summary["grouped_ref_tests"] = {"status": "NOT_DISPATCHED_KERNEL_CONTROLS_FAILED"}
                raise RuntimeError("kernel controls failed or skipped; no additional diagnostic phase launched")
            # The changed grouped-ref substrate was not executable on Linux.
            # These exact existing controls create empty disposable Git repos,
            # not migrated controllers. Keep their fixed owner-selected Git
            # (which may be cmd/git.exe) distinct from the kernel direct image.
            custody_spec = importlib.util.spec_from_file_location("windows_custody_test", source / "fixtures/canonical-state-rotation/windows_custody_test.py")
            custody_fixture = importlib.util.module_from_spec(custody_spec)
            custody_spec.loader.exec_module(custody_fixture)
            sys.modules["windows_custody_test"] = custody_fixture
            ref_spec = importlib.util.spec_from_file_location("dg30_ref_group_test", source / "fixtures/canonical-state-rotation/ref_group_test.py")
            refs = importlib.util.module_from_spec(ref_spec)
            ref_spec.loader.exec_module(refs)
            ref_suite = unittest.defaultTestLoader.loadTestsFromTestCase(refs.RefGroup)
            command_root = out / "grouped-ref-commands"
            command_root.mkdir()
            original_run = subprocess.run
            command_rows = []

            def recorded_run(*args, **kwargs):
                # Capture the real result before any deliberate test substitute
                # changes CompletedProcess.stdout. Never record environment.
                command_out = command_root / f"{len(command_rows) + 1:04d}"
                row = {"test": active_test[0], "command": [str(v) for v in args[0]],
                       "evidence": str(command_out.relative_to(out))}
                command_rows.append(row)
                started = time.monotonic()

                def retain_stream(key, value):
                    if value is not None:
                        try:
                            (command_out / (key + ".bin")).write_bytes(value.encode() if isinstance(value, str) else value)
                        except Exception as exc:
                            capture_errors.append("grouped-ref " + key + " capture: " + type(exc).__name__ + ": " + str(exc))
                            raise

                try:
                    try:
                        command_out.mkdir()
                    except Exception as exc:
                        capture_errors.append("grouped-ref directory capture: " + type(exc).__name__ + ": " + str(exc))
                        raise
                    retain_stream("stdin", kwargs.get("input"))
                    try:
                        actual = original_run(*args, **kwargs)
                    except BaseException as exc:
                        row["error"] = {"type": type(exc).__name__, "message": str(exc)}
                        if isinstance(exc, subprocess.CalledProcessError):
                            row["exit_code"] = exc.returncode
                        retain_stream("stdout", getattr(exc, "stdout", None))
                        retain_stream("stderr", getattr(exc, "stderr", None))
                        raise
                    else:
                        row["exit_code"] = actual.returncode
                        retain_stream("stdout", actual.stdout)
                        retain_stream("stderr", actual.stderr)
                        return actual
                finally:
                    row["wall_seconds"] = time.monotonic() - started
                    try:
                        dump(command_out / "command.json", row)
                    except Exception as exc:
                        # Negative source controls intentionally accept OSError;
                        # an instrumentation failure must still fail the run.
                        capture_errors.append("grouped-ref metadata capture: " + type(exc).__name__ + ": " + str(exc))
                        raise

            subprocess.run = recorded_run
            try:
                with (out / "grouped-ref-unittest.log").open("x", encoding="utf-8") as stream:
                    ref_result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=EvidenceResult).run(ref_suite)
            finally:
                subprocess.run = original_run
            print((out / "grouped-ref-unittest.log").read_text(encoding="utf-8"), flush=True)
            summary["grouped_ref_tests"] = {"run": ref_result.testsRun,
                "skipped": [(str(t), reason) for t, reason in ref_result.skipped],
                "failures": [(str(t), error) for t, error in ref_result.failures],
                "errors": [(str(t), error) for t, error in ref_result.errors],
                "was_successful": ref_result.wasSuccessful(), "actual_fixed_owner_tools": ref_tools,
                "captured_command_count": len(command_rows), "measurement_scope": "raw command exits and wall times; no Job memory claim"}
        finally:
            tempfile.TemporaryDirectory = original_temporary
            tempfile.tempdir = original_tempdir
        records = []
        for path in sorted(out.glob("operations/*/operation/measurement.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            records.append({"path": str(path.relative_to(out)), "sha256": digest(path),
                            **{key: record.get(key) for key in (
                                "status", "error", "root_pid", "elapsed_ms", "exit_code", "kernel_total_processes",
                                "terminal_active_processes", "peak_job_committed_bytes", "baseline_subtracted_bytes",
                                "complete_memory_scope_valid", "containment_status", "cleanup_complete")}})
        summary["measurements"] = records
        passed = (result.wasSuccessful() and result.testsRun == 3 and not result.skipped
                  and ref_result.wasSuccessful() and ref_result.testsRun == 7 and not ref_result.skipped
                  and len(ref_tools) == 7 and len(records) == 3 and len(cleanup_rows) == 10 and not capture_errors
                  and all(row.get("evidence_copied") and row.get("temporary_directory_removed") for row in cleanup_rows)
                  and all(row["cleanup_complete"] is True and row["terminal_active_processes"] == 0 for row in records))
        summary["status"] = "PASS_DIAGNOSTICS_ONLY" if passed else "FAIL_DIAGNOSTICS"
        exit_code = 0 if passed else 1
    except BaseException as exc:
        summary["failure"] = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        print(summary["failure"]["traceback"], file=sys.stderr, flush=True)
    finally:
        summary.update(exit_code=exit_code, wall_seconds=time.monotonic() - began,
                       temporary_cleanup=cleanup_rows, capture_errors=capture_errors)
        dump(out / "result.json", summary)
        dump(out / "manifest.json", [{"path": str(p.relative_to(out)), "bytes": p.stat().st_size, "sha256": digest(p)}
                                     for p in sorted(out.rglob("*")) if p.is_file() and p.name != "manifest.json"])
        print(json.dumps({"status": summary["status"], "exit_code": exit_code,
                          "scope": summary["scope"]}), flush=True)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
