"""Actual tiny default-carrier controls; no original verifier or native launch."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run-work-graph-verifier.sh"


class DefaultTransportDescriptorCases(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="default-carrier-fds-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        (self.base / "scripts").mkdir()
        self.runner = self.base / "scripts/run-work-graph-verifier.sh"
        shutil.copyfile(RUNNER, self.runner)
        self.marker = self.base / "inherited.txt"
        self.marker.write_bytes(b"independent caller descriptor")
        self.stdin = b"shared stdin\nsecond line\x00exact bytes"
        python_alias = shutil.which("python")
        self.assertIsNotNone(python_alias, "runner requires its existing python alias")
        self.environment = dict(PATH=os.pathsep.join(dict.fromkeys(
            [str(Path(python_alias).parent), "/usr/bin", "/bin"])),
            LANG="C", LC_ALL="C", PYTHONDONTWRITEBYTECODE="1")
        observer = self.base / "observe.py"
        observer.write_text('''import json,os,sys
try:
    os.fstat(3)
    fd3_open = True
except OSError:
    fd3_open = False
try:
    fd3_content = os.pread(3,128,0).decode()
except OSError:
    fd3_content = None
print(json.dumps(dict(phase=sys.argv[1], shared=sys.argv[2], argc=int(sys.argv[3]),
    fd3_open=fd3_open, fd3_content=fd3_content, inherited=os.pread(7,128,0).decode(),
    stdin=sys.stdin.buffer.read().hex() if sys.argv[1] == "body" else None),sort_keys=True))
''')
        self.observe = " ".join(map(shlex.quote, [sys.executable, "-I", "-S", "-B", str(observer)]))

    def frames(self, failure=None):
        trap = self.observe + ' trap "$shared_state" "$#"'
        if failure == "trap":
            trap += "; exit 14"
        prelude = ('set -euo pipefail\nshared_state=kept\n'
                   'shared_function() { printf "%s" "$shared_state"; }\n'
                   'test "$1" = first\nshift\ntrap ' + shlex.quote(trap) + ' EXIT\n')
        if failure == "prelude":
            prelude += "false\n"
        body = ('shared_state="$(shared_function)-updated"\n' + self.observe +
                ' body "$shared_state" "$#"\n')
        if failure == "body":
            body += "exit 9\n"
        terminal = 'test "$(shared_function)" = kept-updated\ntest "$1" = second\n'
        return [("PRELUDE", prelude), ("BODY", body), ("TERMINAL", terminal)]

    def run_carrier(self, frames, mode, *, caller_fd3=False, relative_trace=False):
        stream = b"".join(name.encode() + b"\0" + source.encode() + b"\0" for name, source in frames)
        path = self.base / (mode + ".bin")
        path.write_bytes(stream)
        trace = self.base / (mode + ".tsv")
        if mode == "legacy":
            script = self.base / "scripts/verify-package.sh"
            script.write_text("".join(source for _, source in frames))
            arguments = [str(script), "first", "second"]
        else:
            arguments = [str(self.runner), str(path), str(trace.relative_to(self.base) if relative_trace else trace), str(len(frames)),
                         hashlib.sha256(stream).hexdigest(), "first", "second"]
        # Both carriers receive identical caller descriptors, including independent FD7.
        fd3 = 'exec 3<"$1"' if caller_fd3 else "exec 3>&-"
        command = ["/usr/bin/bash", "--noprofile", "--norc", "-c",
                   fd3 + '\nexec 7<"$1"\nshift\nexec "$@"', "fd-control",
                   str(self.marker), "/usr/bin/bash", "--noprofile", "--norc", *arguments]
        result = subprocess.run(command, input=self.stdin, capture_output=True,
                                cwd=self.base, env=self.environment, close_fds=True, timeout=15)
        return result, trace.read_bytes() if trace.exists() else None

    def assert_carriers(self, failure, expected_exit, expected_trace):
        frames = self.frames(failure)
        legacy, _ = self.run_carrier(frames, "legacy")
        dag, trace = self.run_carrier(frames, "dag")
        self.assertEqual((legacy.returncode, dag.returncode), (expected_exit, expected_exit))
        self.assertEqual(dag.stderr, legacy.stderr)
        observed = [json.loads(row) for row in dag.stdout.splitlines()]
        self.assertTrue(observed, "the actual child observer must execute")
        for row in observed:
            self.assertFalse(row["fd3_open"], row["phase"] + " inherited the private trace descriptor")
            self.assertEqual(row["inherited"], "independent caller descriptor")
            self.assertEqual(row["argc"], 1)
        self.assertEqual(dag.stdout, legacy.stdout)
        self.assertEqual(trace, expected_trace)
        if failure != "prelude":
            self.assertEqual(observed[0]["stdin"], self.stdin.hex())
            self.assertEqual(observed[0]["shared"], "kept-updated")
        self.assertEqual(observed[-1]["phase"], "trap")

    def test_normal_body_and_exit_trap_do_not_inherit_tracer(self):
        self.assert_carriers(None, 0, b"PRELUDE\tSTART\nPRELUDE\tPASS\nBODY\tSTART\nBODY\tPASS\nTERMINAL\tSTART\nTERMINAL\tPASS\n")

    def test_failed_body_preserves_exit_trap_stdin_and_failed_prefix(self):
        self.assert_carriers("body", 9, b"PRELUDE\tSTART\nPRELUDE\tPASS\nBODY\tSTART\n")

    def test_failed_prelude_does_not_dispatch_body_or_terminal(self):
        self.assert_carriers("prelude", 1, b"PRELUDE\tSTART\n")

    def test_late_exit_trap_failure_keeps_complete_trace_and_nonzero(self):
        self.assert_carriers("trap", 14, b"PRELUDE\tSTART\nPRELUDE\tPASS\nBODY\tSTART\nBODY\tPASS\nTERMINAL\tSTART\nTERMINAL\tPASS\n")

    def test_existing_caller_fd3_is_preserved_instead_of_replaced_by_tracer(self):
        frames = self.frames()
        legacy, _ = self.run_carrier(frames, "legacy", caller_fd3=True)
        dag, trace = self.run_carrier(frames, "dag", caller_fd3=True)
        self.assertEqual((legacy.returncode, dag.returncode), (0, 0))
        self.assertEqual(dag.stdout, legacy.stdout)
        self.assertEqual(dag.stderr, legacy.stderr)
        for row in map(json.loads, dag.stdout.splitlines()):
            self.assertTrue(row["fd3_open"])
            self.assertEqual(row["fd3_content"], "independent caller descriptor")
        self.assertTrue(trace.endswith(b"TERMINAL\tPASS\n"))

    def test_relative_trace_destination_survives_source_directory_change(self):
        changed = self.base / "changed-directory"
        changed.mkdir()
        frames = self.frames()
        frames[0] = ("PRELUDE", frames[0][1] + "cd " + shlex.quote(str(changed)) + "\n")
        legacy, _ = self.run_carrier(frames, "legacy")
        dag, trace = self.run_carrier(frames, "dag", relative_trace=True)
        self.assertEqual((legacy.returncode, dag.returncode), (0, 0))
        self.assertEqual((dag.stdout, dag.stderr), (legacy.stdout, legacy.stderr))
        self.assertEqual(trace, b"PRELUDE\tSTART\nPRELUDE\tPASS\nBODY\tSTART\nBODY\tPASS\nTERMINAL\tSTART\nTERMINAL\tPASS\n")
        self.assertFalse((changed / "dag.tsv").exists())

    def test_explicit_trace_corruption_keeps_exit_and_parser_refuses(self):
        frames = self.frames("body")
        frames[1] = ("BODY", "printf 'FOREIGN\\tPASS\\n' >> " +
                     shlex.quote(str(self.base / "dag.tsv")) + "\n" + frames[1][1])
        result, trace = self.run_carrier(frames, "dag")
        self.assertEqual(result.returncode, 9)
        self.assertIn(b"FOREIGN\tPASS\n", trace)
        path = ROOT / "scripts/qualify-work-graph-verifier.py"
        spec = importlib.util.spec_from_file_location("fd3_trace_consumer", path)
        consumer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(consumer)
        mapping = dict(nodes=[dict(id=name) for name, _ in frames])
        with self.assertRaisesRegex(consumer.WG.WorkGraphError, "invalid ordered verifier node trace"):
            consumer.trace_nodes(mapping, "dag", result.returncode, trace)


if __name__ == "__main__":
    unittest.main()
