#!/usr/bin/env python3
"""Real-shell controls for the shell-to-companion executed-buffer boundary.

The interpreter audit/trace hook observes actual compiled and executing code;
it supplies no continuity, receipt, native, or effect authority.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SOURCE = Path(os.environ.get("SHELL_CUSTODY_SOURCE") or
              Path(__file__).resolve().parents[1] / "skills/implementaudit/scripts")
WORK = Path(os.environ.get("SHELL_CUSTODY_WORK") or tempfile.gettempdir())
EVIDENCE = os.environ.get("SHELL_CUSTODY_EVIDENCE")
MEMBERS = ("claim-run.sh", "claim-run-rotation.py", "canonical_custody.py",
           "canonical_hot_projection.py", "canonical_rotation_inputs.py",
           "rotate-canonical-state.py", "validate-run-root.sh", "read-canonical-pair.py")
MARKER = "EXECUTED_UNSELECTED_COMPANION"

OBSERVER = r'''
import hashlib, json, os, sys
from pathlib import Path
target = os.environ["SHELL_OBSERVER_TARGET"]
log = Path(os.environ["SHELL_OBSERVER_LOG"])
drift = os.environ.get("SHELL_OBSERVER_DRIFT") == "1"
changed = False
def record(value):
    with log.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True) + "\n")
def trace(frame, event, arg):
    if frame.f_code.co_filename == target and frame.f_code.co_name == "<module>" and event == "call":
        record({"event": "module", "file": frame.f_globals.get("__file__"),
                "name": frame.f_globals.get("__name__"), "argv": sys.argv,
                "package": frame.f_globals.get("__package__"),
                "main_identity": sys.modules["__main__"].__dict__ is frame.f_globals,
                "import_path": sys.path[0], "stdin": sys.stdin.read()})
    return trace
def audit(event, args):
    global changed
    if event == "compile" and args[1] == target:
        source = args[0]
        if isinstance(source, str):
            source = source.encode()
        record({"event": "compile", "sha256": hashlib.sha256(source).hexdigest(), "bytes": len(source)})
        if drift and not changed:
            changed = True
            marker = b'print("EXECUTED_UNSELECTED_COMPANION", flush=True)\nraise SystemExit(0)\n'
            Path(target).write_bytes(marker + b"#" * (len(source) - len(marker)))
    elif event == "exec" and args[0].co_filename == target:
        sys.settrace(trace)
sys.addaudithook(audit)
'''


class ShellCompanionSourceCustody(unittest.TestCase):
    def setUp(self):
        WORK.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="shell-custody-", dir=WORK)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).absolute()
        self.cwd = self.root / "caller directory"
        self.cwd.mkdir()
        self.scripts = self.layout("source layout", "skills/implementaudit/scripts")
        self.companion = self.scripts / "claim-run-rotation.py"
        self.original = self.companion.read_bytes()
        self.calls = 0

    def layout(self, label, relative):
        scripts = self.root / label / relative
        scripts.mkdir(parents=True)
        for name in MEMBERS:
            if (SOURCE / name).is_file():
                shutil.copyfile(SOURCE / name, scripts / name)
        return scripts

    def invoke(self, scripts=None, *, args=None, extra_env=None, input_bytes=b""):
        scripts = self.scripts if scripts is None else scripts
        args = ["--resolve-canonical-generation", "invalid?controller"] if args is None else args
        environment = {"PATH": os.environ["PATH"], "LC_ALL": "C.UTF-8",
                       "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1",
                       "GIT_NO_LAZY_FETCH": "1", "GIT_CONFIG_NOSYSTEM": "1",
                       "GIT_CONFIG_GLOBAL": os.devnull}
        environment.update(extra_env or {})
        # Windows CreateProcess searches System32 before PATH for a bare name;
        # resolve the selected shell instead of accidentally starting WSL bash.
        for key in ("SystemRoot", "TEMP", "TMP"):
            if key in os.environ:
                environment[key] = os.environ[key]
        bash = shutil.which("bash")
        if bash is None:
            self.fail("bash is required for shell custody controls")
        command = [bash, (scripts / "claim-run.sh").as_posix(), *args]
        result = subprocess.run(command, cwd=self.cwd, env=environment,
                                input=input_bytes, capture_output=True, timeout=20,
                                check=False)
        self.calls += 1
        if EVIDENCE:
            dest = Path(EVIDENCE) / self._testMethodName / str(self.calls)
            dest.mkdir(parents=True, exist_ok=True)
            (dest / "stdout.bin").write_bytes(result.stdout)
            (dest / "stderr.bin").write_bytes(result.stderr)
            (dest / "receipt.json").write_text(json.dumps({
                "argv": command, "cwd": str(self.cwd), "returncode": result.returncode,
                "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
                "shell_sha256": hashlib.sha256((scripts / "claim-run.sh").read_bytes()).hexdigest(),
            }, indent=2) + "\n")
        return result

    def changed_source(self, length=None):
        length = len(self.original) if length is None else length
        payload = ('print("' + MARKER + '", flush=True)\nraise SystemExit(0)\n').encode()
        self.assertGreater(length, len(payload))
        return payload + b"#" * (length - len(payload))

    def assert_loader_refusal(self, result):
        self.assertEqual(result.returncode, 1, result.stdout.decode() + result.stderr.decode())
        self.assertNotIn(MARKER.encode(), result.stdout + result.stderr)
        self.assertIn(b"claim-run.sh: companion source", result.stderr)

    def assert_actual_companion(self, result):
        self.assertEqual(result.returncode, 1, result.stderr.decode())
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stderr, ("claim-run.sh: controller identity is invalid" + os.linesep).encode())

    def observe(self, *, drift=False):
        observer = self.root / "observer"
        observer.mkdir()
        (observer / "sitecustomize.py").write_text(OBSERVER)
        log = self.root / "interpreter-observations.jsonl"
        env = {"PYTHONPATH": str(observer), "SHELL_OBSERVER_TARGET": str(self.companion),
               "SHELL_OBSERVER_LOG": str(log), "SHELL_OBSERVER_DRIFT": str(int(drift))}
        result = self.invoke(extra_env=env, input_bytes=b"preserved stdin\n")
        records = [json.loads(line) for line in log.read_text().splitlines()]
        if EVIDENCE:
            dest = Path(EVIDENCE) / self._testMethodName
            shutil.copyfile(log, dest / "interpreter-observations.jsonl")
        return result, records

    def test_same_size_unselected_companion_is_not_executed(self):
        # A same-size source substitution must fail before any substituted code.
        self.companion.write_bytes(self.changed_source())
        self.assert_loader_refusal(self.invoke())

    def test_exact_companion_executes_in_both_package_layouts(self):
        # A loader that loses __file__, __name__, or argv cannot reach this error.
        self.assert_actual_companion(self.invoke())
        standalone = self.layout("standalone layout", "scripts")
        self.assert_actual_companion(self.invoke(standalone))

    def test_wrong_lengths_and_missing_source_are_refused(self):
        for length in (len(self.original) - 1, len(self.original) + 1):
            with self.subTest(length=length):
                self.companion.write_bytes(self.changed_source(length))
                self.assert_loader_refusal(self.invoke())
        self.companion.unlink()
        self.assert_loader_refusal(self.invoke())

    def test_hardlinked_companion_is_refused(self):
        os.link(self.companion, self.scripts / "companion.alias")
        self.assert_loader_refusal(self.invoke())

    @unittest.skipUnless(os.name == "posix", "native POSIX alias case")
    def test_symlinked_companion_is_refused(self):
        physical = self.scripts / "companion.physical"
        self.companion.rename(physical)
        self.companion.symlink_to(physical)
        self.assert_loader_refusal(self.invoke())

    @unittest.skipUnless(os.name == "posix", "native POSIX ancestor alias case")
    def test_symlinked_source_directory_is_refused(self):
        alias = self.root / "aliased source directory"
        alias.symlink_to(self.scripts, target_is_directory=True)
        self.assert_loader_refusal(self.invoke(alias))

    def test_caller_directory_cannot_select_companion_or_bootstrap_import(self):
        # Invocation cwd is unrelated to the source-owner sibling selection.
        (self.cwd / "claim-run-rotation.py").write_bytes(self.changed_source())
        (self.cwd / "hashlib.py").write_text('print("' + MARKER + '")\nraise SystemExit(0)\n')
        self.assert_actual_companion(self.invoke())

    def test_real_main_module_args_path_import_path_and_stdin_are_preserved(self):
        result, records = self.observe()
        self.assert_actual_companion(result)
        compiled = [row for row in records if row["event"] == "compile"]
        self.assertGreaterEqual(len(compiled), 1)
        self.assertEqual(compiled[0]["bytes"], len(self.original))
        self.assertEqual(compiled[0]["sha256"], hashlib.sha256(self.original).hexdigest())
        modules = [row for row in records if row["event"] == "module"]
        self.assertEqual(len(modules), 1)
        self.assertEqual(modules[0], {"event": "module", "file": str(self.companion),
                         "name": "__main__", "argv": [self.companion.as_posix(), "resolve", "invalid?controller"],
                         "package": None, "main_identity": True,
                         "import_path": str(self.scripts), "stdin": "preserved stdin\n"})

    def test_capture_to_compile_path_change_never_executes_replacement(self):
        result, records = self.observe(drift=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(MARKER.encode(), result.stdout + result.stderr)
        compiled = [row for row in records if row["event"] == "compile"]
        self.assertEqual(compiled[0]["sha256"], hashlib.sha256(self.original).hexdigest())
        self.assertEqual(len([row for row in records if row["event"] == "module"]), 1)
        self.assertIn(b"executing claim code differs from the physical load snapshot", result.stderr)
        self.assertEqual(self.companion.read_bytes(), self.changed_source())


if __name__ == "__main__":
    unittest.main(verbosity=2)
