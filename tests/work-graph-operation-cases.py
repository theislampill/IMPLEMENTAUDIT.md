#!/usr/bin/env python3
"""Real constructed-source operation windows; no native successful-route claim."""
from __future__ import annotations

import errno
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "skills/implementaudit/scripts/compile-work-graph.py"
SPEC = importlib.util.spec_from_file_location("operation_fixture", ROOT / "tests/native-work-graph-cases.py")
FIXTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURE)
WG = FIXTURE.wg
RETAIN = None


def save(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def constructed_worker(operation, root, operands):
    """Call the same private operation as main, with explicit constructed None.

    This is a Python operation control, not a native CLI success. Public CLI
    REPO_ROOT parsing and genuine native refusal are exercised separately.
    """
    try:
        output = WG._native_operation_output_v1(operation, Path(root), None, operands)
    except (OSError, WG.WorkGraphError) as exc:
        print(f"constructed operation: {exc}", file=sys.stderr)
        return 2
    sys.stdout.buffer.write(output)
    return 0


class OperationWindowControls(unittest.TestCase):
    def setUp(self):
        if RETAIN is None:
            owner = tempfile.TemporaryDirectory(prefix="native-operation-")
            self.addCleanup(owner.cleanup)
            self.root = Path(owner.name)
        else:
            self.root = Path(tempfile.mkdtemp(prefix=self._testMethodName + "-", dir=RETAIN))
        self.run = self.root / "run"
        self.run.mkdir()
        self.args = self.root / "args"
        self.args.mkdir()
        state, nodes = FIXTURE.fixture()
        next(n for n in nodes if n["id"] == "QUALIFY")["requires"] = ["PREP", "SIB"]
        FIXTURE.write_run(self.run, state, nodes)
        self.graph = WG.read_native_run_v1(self.run)
        self.dispatch = WG.select_native_frontier_v1(self.graph)
        self.results = [FIXTURE.packet(self.graph, self.dispatch, n) for n in self.dispatch["selected"]]
        self.graph_path = self.args / "graph.json"
        self.dispatch_path = self.args / "dispatch.json"
        self.results_path = self.args / "results.json"
        self.history_path = self.args / "history.json"
        for path, value in ((self.graph_path, self.graph), (self.dispatch_path, self.dispatch),
                            (self.results_path, self.results), (self.history_path, [])):
            save(path, value)
        self.counter = 0

    def operands(self, operation, held=None):
        if operation == "--select-native":
            return []
        if operation == "--recursive-native":
            return [str(held or self.history_path)]
        return [str(self.graph_path), str(self.dispatch_path), str(held or self.results_path), "QUALIFY"]

    def invoke(self, operation, *, drift=None, native=False):
        """A successful nonblocking FIFO writer open proves the real read began."""
        self.counter += 1
        evidence = self.root / f"call-{self.counter:02}"
        evidence.mkdir()
        gate = self.args / f"gate-{self.counter}.fifo" if drift else None
        if gate is not None:
            os.mkfifo(gate, 0o600)
        operands = self.operands(operation, gate)
        if native:
            empty = self.root / "empty-no-native-continuity"
            empty.mkdir()
            argv = [sys.executable, "-I", "-S", "-B", str(COMPILER), operation,
                    str(self.run), str(empty), *operands]
        else:
            argv = [sys.executable, "-I", "-S", "-B", str(Path(__file__).resolve()),
                    "--constructed-operation", operation, str(self.run), *operands]
        save(evidence / "command.json", dict(argv=argv, cwd=str(self.root), stdin="DEVNULL",
                                            native_success_claim=False, authority="NONE"))
        process = None
        writer = None
        action = "WAIT"
        failure = None
        with (evidence / "stdout.log").open("wb") as out, (evidence / "stderr.log").open("wb") as err:
            try:
                process = subprocess.Popen(argv, cwd=self.root, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
                if gate is not None:
                    deadline = time.monotonic() + 8
                    while writer is None:
                        if process.poll() is not None:
                            raise AssertionError("operation exited before the FIFO result read")
                        try:
                            writer = os.open(gate, os.O_WRONLY | os.O_NONBLOCK)
                        except OSError as exc:
                            if exc.errno != errno.ENXIO or time.monotonic() > deadline:
                                raise
                            time.sleep(0.01)
                    target = self.run / drift
                    target.write_bytes(target.read_bytes() + b"\nchanged while consuming operation input\n")
                    payload = FIXTURE.raw([] if operation == "--recursive-native" else self.results)
                    self.assertLessEqual(len(payload), os.fpathconf(writer, "PC_PIPE_BUF"))
                    self.assertEqual(os.write(writer, payload), len(payload))
                    os.close(writer)
                    writer = None
                process.wait(timeout=8)
            except BaseException as exc:
                failure = exc
            finally:
                if writer is not None:
                    os.close(writer)
                if process is not None and process.poll() is None:
                    action = "TERMINATE_OWNED_TEST_PROCESS"
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        action = "KILL_OWNED_TEST_PROCESS"
                        process.kill()
                        process.wait(timeout=2)
                if gate is not None:
                    gate.unlink()
        code = None if process is None else process.returncode
        (evidence / "exit-code.txt").write_text(str(code) + "\n")
        save(evidence / "cleanup.json", dict(action=action, actual_exit=code, actual_L4=False))
        stdout, stderr = (evidence / "stdout.log").read_bytes(), (evidence / "stderr.log").read_bytes()
        if failure is not None:
            raise AssertionError(f"operation lifecycle failure: {failure}; stderr={stderr!r}") from failure
        return code, stdout, stderr

    def test_stable_operation_bytes_match_existing_readonly_results(self):
        expected = {
            "--select-native": WG.select_native_frontier_v1(self.graph),
            "--recursive-native": WG.compile_recursive_transition_v1(self.graph, []),
            "--reconcile-native": WG.reconcile_native_results_v1(
                self.graph, self.graph, self.dispatch, self.results, "QUALIFY"),
        }
        self.assertEqual(expected["--reconcile-native"]["status"], "SATISFIED_AT_DECLARED_RESULT_CONTRACT")
        for operation, prior in expected.items():
            with self.subTest(operation=operation):
                code, stdout, stderr = self.invoke(operation)
                self.assertEqual((code, stderr), (0, b""))
                self.assertEqual(stdout, WG.canonical_json_v1(prior))
                self.assertEqual(json.loads(stdout)["authority"], "NONE")

    def test_result_fifo_input_drift_refuses_before_any_success_output(self):
        code, stdout, stderr = self.invoke("--reconcile-native", drift="inputs/a.txt")
        self.assertEqual(code, 2)
        self.assertEqual(stdout, b"")
        self.assertIn(b"native inputs changed during intake", stderr)

    def test_history_fifo_source_drift_refuses_before_any_success_output(self):
        code, stdout, stderr = self.invoke("--recursive-native", drift="STATE.md")
        self.assertEqual(code, 2)
        self.assertEqual(stdout, b"")
        self.assertIn(b"native source changed during intake", stderr)

    def test_changed_input_before_acquisition_returns_recompute(self):
        path = self.run / "inputs/a.txt"
        path.write_bytes(path.read_bytes() + b"changed before acquisition\n")
        code, stdout, stderr = self.invoke("--reconcile-native")
        self.assertEqual((code, stderr), (0, b""))
        result = json.loads(stdout)
        self.assertEqual(result["status"], "RECOMPUTE_REQUIRED")
        self.assertIn("PREP", result["invalidated"])
        self.assertIn("SIB", result["preserved"])
        self.assertEqual(result["authority"], "NONE")

    def test_real_native_cli_requires_continuity_without_constructed_fallback(self):
        code, stdout, stderr = self.invoke("--reconcile-native", native=True)
        self.assertEqual(code, 2)
        self.assertEqual(stdout, b"")
        self.assertIn(b"compile-work-graph:", stderr)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--constructed-operation":
        raise SystemExit(constructed_worker(sys.argv[2], sys.argv[3], sys.argv[4:]))
    if "--retain-fixtures" in sys.argv:
        index = sys.argv.index("--retain-fixtures")
        RETAIN = Path(sys.argv[index + 1]).resolve()
        RETAIN.mkdir(parents=True, exist_ok=False)
        del sys.argv[index:index + 2]
    unittest.main(verbosity=2)
