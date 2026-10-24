"""Real runner acquisition controls; fixtures and effects stay under /tmp."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "work_graph_stream", ROOT / "skills/implementaudit/scripts/compile-work-graph.py")
WG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WG)
EVIDENCE = None


class StreamCases(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="r0035-stream-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.root = self.directory / "repo"
        (self.root / "scripts").mkdir(parents=True)
        (self.root / "tests").mkdir()
        shutil.copyfile(ROOT / "scripts/run-work-graph-verifier.sh",
                        self.root / "scripts/run-work-graph-verifier.sh")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "scripts/generate-readme-diagrams.sh").write_text(
            '#!/bin/bash\nprintf "first\\n"\n')
        self.environment = dict(os.environ)
        self.environment.pop("BASH_ENV", None)
        self.environment.pop("ENV", None)
        self.sequence = 0
        self.configure()

    def configure(self, *, code=0, trap_code=None, padding=0):
        prelude = ('#!/usr/bin/env bash\nset -euo pipefail\n'
                   'repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"\n'
                   'cd "$repo_root"\n'
                   '[ "$#" -eq 1 ] && [ "$1" = "argument with spaces" ] || exit 73\n'
                   'shift\nshared_state="retained shell state"\n'
                   'trap \'printf "cleanup=%s\\n" "$shared_state" >&2' +
                   ('' if trap_code is None else '; exit ' + str(trap_code)) + "' EXIT\n")
        registry = (prelude + "#" + "x" * padding + '\n\n'
                    'bash scripts/generate-readme-diagrams.sh --check\n'
                    'bash tests/sample.test.sh "$shared_state"\n'
                    'git diff --check\n\n'
                    "printf 'verify-package: ok\\n'\n").encode()
        (self.root / "scripts/verify-package.sh").write_bytes(registry)
        (self.root / "tests/sample.test.sh").write_text(
            '#!/bin/bash\nIFS= read -r value\n'
            'printf "state=%s; stdin=%s\\n" "$1" "$value"\nexit ' + str(code) + '\n')
        self.mapping = WG.compile_verifier_graph_v1(registry, ["tests/sample.test.sh"], {})
        self.data = WG.verifier_command_stream_v1(self.mapping, registry)
        self.stream = self.directory / "commands.bin"
        self.stream.write_bytes(self.data)

    def run_process(self, argv, *, environment=None, swap=None, timeout=10):
        self.sequence += 1
        trace = self.directory / ("trace-%03d.log" % self.sequence)
        argv = [str(trace) if arg == "TRACE_PATH" else str(arg) for arg in argv]
        selected_environment = self.environment if environment is None else environment
        retained = None
        if EVIDENCE is not None:
            retained = EVIDENCE / self._testMethodName / ("%03d" % self.sequence)
            retained.mkdir(parents=True)
            shutil.copytree(self.root / "scripts", retained / "scripts")
            shutil.copytree(self.root / "tests", retained / "tests")
            for name in ("commands.bin", "bash-env.sh", "replacement.bin"):
                path = self.directory / name
                if path.is_file():
                    shutil.copyfile(path, retained / name)
            if (self.directory / "bin").exists():
                shutil.copytree(self.directory / "bin", retained / "bin")
        process = subprocess.Popen(argv, cwd=self.root, env=selected_environment,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        intercepted = False
        if swap is not None:
            ready, release, operation = swap
            deadline = time.monotonic() + 3
            while process.poll() is None and not ready.exists() and time.monotonic() < deadline:
                time.sleep(.01)
            intercepted = ready.exists()
            if intercepted:
                operation()
            release.touch()
        timed_out = False
        try:
            stdout, stderr = process.communicate(input=b"USER_INPUT\n", timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        events = trace.read_bytes() if trace.exists() else b""
        record = dict(argv=argv, cwd=str(self.root), exit=process.returncode,
                      timed_out=timed_out, intercepted=intercepted,
                      environment_sha256=hashlib.sha256(b"\0".join(
                          os.fsencode(k) + b"=" + os.fsencode(v)
                          for k, v in sorted(selected_environment.items()))).hexdigest())
        if retained is not None:
            (retained / "command.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
            (retained / "stdout.log").write_bytes(stdout)
            (retained / "stderr.log").write_bytes(stderr)
            (retained / "trace.log").write_bytes(events)
            (retained / "exit-code.txt").write_text(str(process.returncode) + "\n")
            (retained / "stdin.bin").write_bytes(b"USER_INPUT\n")
        return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr), events, record

    def run_runner(self, **options):
        return self.run_process([
            "bash", "scripts/run-work-graph-verifier.sh", self.stream, "TRACE_PATH",
            str(len(self.mapping["nodes"])), hashlib.sha256(self.data).hexdigest(),
            "argument with spaces"], **options)

    def swap_before_acquisition(self, kind):
        ready, release = self.directory / "ready", self.directory / "release"
        hook = self.directory / "bash-env.sh"
        # The hook only synchronizes the actual external path replacement. It
        # does not replace the filesystem calls or supply any verifier result.
        hook.write_text(
            'r0035_stream_test_hook() {\n'
            '  if [[ "$BASH_COMMAND" == \'exec {r0035_verifier_frame_fd}\'* ]]; then\n'
            '    trap - DEBUG\n    : > ' + shlex.quote(str(ready)) + '\n'
            '    while [[ ! -e ' + shlex.quote(str(release)) + ' ]]; do sleep 0.01; done\n'
            '  fi\n}\ntrap r0035_stream_test_hook DEBUG\n')
        original = self.directory / "original.bin"
        original.write_bytes(self.data)

        def operation():
            if kind == "unchanged":
                return
            self.stream.unlink()
            if kind == "symlink":
                self.stream.symlink_to(original)
            elif kind == "fifo":
                os.mkfifo(self.stream)
            else:
                self.stream.mkdir()

        result, trace, record = self.run_runner(
            environment=dict(self.environment, BASH_ENV=str(hook)),
            swap=(ready, release, operation), timeout=2)
        self.assertTrue(record["intercepted"], record)
        return result, trace, record

    def assert_refused(self, result, trace, record):
        self.assertFalse(record["timed_out"], record)
        self.assertEqual(result.returncode, 2, (result, record))
        self.assertEqual(result.stdout, b"", result)
        self.assertEqual(trace, b"", result)

    def test_legacy_argv_stdin_state_fail_fast_and_exit_trap(self):
        for code, trap_code, expected in ((0, None, 0), (9, None, 9), (0, 7, 7)):
            with self.subTest(code=code, trap_code=trap_code):
                self.configure(code=code, trap_code=trap_code)
                legacy, _, _ = self.run_process(
                    ["bash", "scripts/verify-package.sh", "argument with spaces"])
                actual, trace, record = self.run_runner()
                self.assertFalse(record["timed_out"])
                self.assertEqual((actual.stdout, actual.stderr, actual.returncode),
                                 (legacy.stdout, legacy.stderr, legacy.returncode))
                self.assertEqual(actual.returncode, expected)
                self.assertIn(b"state=retained shell state; stdin=USER_INPUT\n", actual.stdout)
                self.assertEqual(b"verify-package: ok\n" in actual.stdout, code == 0)
                self.assertEqual(trace.count(b"\tPASS\n"), 2 if code else 5)

    def test_acquisition_hook_preserves_unchanged_execution(self):
        actual, trace, record = self.swap_before_acquisition("unchanged")
        self.assertFalse(record["timed_out"])
        self.assertEqual(actual.returncode, 0, actual)
        self.assertEqual(trace.count(b"\tPASS\n"), 5)
        self.assertIn(b"state=retained shell state; stdin=USER_INPUT\n", actual.stdout)

    def test_symlink_replacement_before_open_refuses(self):
        self.assert_refused(*self.swap_before_acquisition("symlink"))

    def test_fifo_replacement_before_open_refuses_without_blocking(self):
        self.assert_refused(*self.swap_before_acquisition("fifo"))

    def test_directory_replacement_before_open_refuses(self):
        self.assert_refused(*self.swap_before_acquisition("directory"))

    def python_proxy(self, suffix):
        directory = self.directory / "bin"
        directory.mkdir()
        proxy = directory / "python"
        proxy.write_text("#!/bin/bash\nset -e\n" + shlex.quote(sys.executable) +
                         ' "$@"\n' + suffix + "\n")
        proxy.chmod(0o755)
        return dict(self.environment, PATH=str(directory) + os.pathsep + self.environment.get("PATH", ""))

    def test_complete_output_from_failed_acquirer_never_executes(self):
        # A complete pipe is insufficient when the producing process failed.
        marker = self.directory / "first-python-completed"
        environment = self.python_proxy(
            'if [ ! -e ' + shlex.quote(str(marker)) + ' ]; then\n  : > ' +
            shlex.quote(str(marker)) + '\n  exit 9\nfi')
        self.assert_refused(*self.run_runner(environment=environment))

    def test_replacement_after_acquisition_uses_retained_stream(self):
        replacement = self.directory / "replacement.bin"
        replacement.write_bytes(self.data.replace(b"verify-package: ok", b"REPLACED_FRAME_EXECUTED"))
        environment = self.python_proxy(shlex.join(["cp", str(replacement), str(self.stream)]))
        actual, trace, record = self.run_runner(environment=environment)
        self.assertFalse(record["timed_out"])
        self.assertEqual(actual.returncode, 0, actual)
        self.assertIn(b"verify-package: ok\n", actual.stdout)
        self.assertNotIn(b"REPLACED_FRAME_EXECUTED", actual.stdout)
        self.assertEqual(trace.count(b"\tPASS\n"), 5)
        self.assertEqual(self.stream.read_bytes(), replacement.read_bytes())

    def test_malformed_and_incomplete_streams_never_execute(self):
        original = self.data
        for changed in (original[:-1], original + b"EXTRA_UNTERMINATED", b"",
                        b"\0" + original, original + b"EXTRA\0"):
            with self.subTest(bytes=len(changed)):
                self.data = changed
                self.stream.write_bytes(changed)
                self.assert_refused(*self.run_runner())
        self.data = original
        self.stream.write_bytes(original.replace(b"verify-package: ok", b"WRONG_DIGEST"))
        self.assert_refused(*self.run_runner())

    def test_complete_oversized_compiler_stream_refuses(self):
        self.configure(padding=16 * 1024 * 1024)
        self.assert_refused(*self.run_runner())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--retain-evidence", type=Path)
    options, remaining = parser.parse_known_args()
    if options.retain_evidence is not None:
        EVIDENCE = options.retain_evidence.resolve()
        EVIDENCE.mkdir(parents=True, exist_ok=False)
        shutil.copyfile(__file__, EVIDENCE / "harness-source.py")
    unittest.main(argv=[sys.argv[0], *remaining])
