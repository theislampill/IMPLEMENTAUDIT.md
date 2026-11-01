#!/usr/bin/env python3
"""Disposable hosted diagnostics for the exact three reviewed Windows controls.

This never invokes claim-run, provisions a controller, or admits a native resume.
The fixture and recorder bytes are unchanged. The only test adaptation copies
each completed TemporaryDirectory to evidence before its normal cleanup.
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

QUALIFIED_SOURCE = "a5b6d250249869853c807b4c917ab5de0134e78b"
QUALIFIED_TREE = "6727518ea8d44a00ffa986146469d4d40d1e7063"
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
               "scope": "three disposable WindowsKernelIntegration tests only",
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
        python = physical(sys.executable)
        git = physical(r"C:\Program Files\Git\mingw64\bin\git.exe")
        bash = physical(r"C:\Program Files\Git\bin\bash.exe")
        summary["host"] = {"platform": platform.platform(), "windows_version": list(sys.getwindowsversion()),
                           "python_version": sys.version, "architecture": platform.machine()}
        summary["job"] = {key: os.environ.get(key) for key in (
            "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_REF", "GITHUB_EVENT_NAME", "GITHUB_RUN_ID",
            "GITHUB_RUN_ATTEMPT", "GITHUB_JOB", "GITHUB_WORKFLOW", "RUNNER_OS", "RUNNER_ARCH",
            "RUNNER_ENVIRONMENT", "ImageOS", "ImageVersion")}
        summary["tools"] = {name: {"path": str(path), "sha256": digest(path), "bytes": path.stat().st_size}
                            for name, path in (("python", python), ("git", git), ("bash", bash))}
        # Children receive only the OS/tool startup requirements, never an
        # inherited Actions credential, GitHub token, or Python startup hook.
        allowed = {"SystemRoot", "WINDIR", "COMSPEC", "TEMP", "TMP", "PATH", "PATHEXT",
                   "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE"}
        clean = {key: value for key, value in os.environ.items() if key.upper() in {k.upper() for k in allowed}}
        clean["IMPLEMENTAUDIT_WINDOWS_JOB_CONTROLS"] = "1"
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
            bindings.append({"path": relative, "blob_oid": oid, "sha256": digest(path), "bytes": path.stat().st_size})
        summary["source_files"] = bindings
        summary["git_version"] = run_git("--version")
        dump(out / "source-job-binding.json", summary)

        original_temporary = tempfile.TemporaryDirectory
        original_tempdir = tempfile.tempdir
        temporary_root = out / "temporary"
        temporary_root.mkdir()
        tempfile.tempdir = str(temporary_root)

        class RetainedTemporaryDirectory(original_temporary):
            def cleanup(self):
                path = Path(self.name)
                if path.exists():
                    row = {"original_path": str(path), "copy": f"operations/{len(cleanup_rows) + 1:02d}-{path.name}"}
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
                result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
            print((out / "unittest.log").read_text(encoding="utf-8"), flush=True)
            summary["tests"] = {"run": result.testsRun, "skipped": [(str(t), reason) for t, reason in result.skipped],
                                "failures": [(str(t), error) for t, error in result.failures],
                                "errors": [(str(t), error) for t, error in result.errors],
                                "was_successful": result.wasSuccessful()}
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
                  and len(records) == 3 and len(cleanup_rows) == 3 and not capture_errors
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
