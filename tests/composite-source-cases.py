"""Combined portable interfaces only; no authentic admission or native effects."""
import hashlib
import ast
import io
import importlib.util
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tokenize
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "skills/implementaudit/scripts"
PEER = ROOT / "source-peers/native-runtime/skills/implementaudit/scripts"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompositeSourceCases(unittest.TestCase):
    @unittest.skipUnless(os.name == "posix", "POSIX descriptor admission controls")
    def test_status_read_guard_admits_only_the_recorded_readonly_descriptor(self):
        fixture = load("status_descriptor_fixture", ROOT / "tests/cognition-pending-durability.py")
        with tempfile.TemporaryDirectory(prefix="status-descriptor-") as temporary:
            path, foreign = Path(temporary) / "allowed", Path(temporary) / "foreign"
            path.write_bytes(b"original")
            foreign.write_bytes(b"unrelated")
            guard = fixture.StatusReadAudit({path})
            descriptor = os.open(path, os.O_RDONLY)
            other = os.open(foreign, os.O_RDONLY)
            try:
                with self.assertRaisesRegex(AssertionError, "no admitted pathname"):
                    guard.record_open(descriptor, path, os.O_RDONLY)
                guard("open", (str(path), "r", os.O_RDONLY))
                guard.record_open(descriptor, path, os.O_RDONLY)
                for candidate in (other, True, str(descriptor), str(foreign)):
                    with self.subTest(candidate=candidate), self.assertRaises(AssertionError):
                        guard("open", (candidate, "r", os.O_RDONLY))
                for candidate in (str(path), descriptor):
                    with self.subTest(writable=candidate), self.assertRaisesRegex(AssertionError, "writable"):
                        guard("open", (candidate, "r+", os.O_RDWR))
                guard("open", (descriptor, "r", os.O_RDONLY))
                self.assertEqual(guard.opened, [str(path)])
                self.assertEqual(guard.wrapped, {descriptor})
                with self.assertRaisesRegex(AssertionError, "repeated"):
                    guard("open", (descriptor, "r", os.O_RDONLY))
                for event in ("os.listdir", "os.scandir", "os.rename", "os.remove", "os.rmdir",
                              "os.mkdir", "subprocess.Popen", "os.system", "socket.connect"):
                    with self.subTest(event=event), self.assertRaisesRegex(AssertionError, "forbidden"):
                        guard(event, ())
                changed = fixture.StatusReadAudit({path})
                changed("open", (str(path), "r", os.O_RDONLY))
                changed.record_open(descriptor, path, os.O_RDONLY)
                path.write_bytes(b"changed size")
                with self.assertRaisesRegex(AssertionError, "identity changed"):
                    changed("open", (descriptor, "r", os.O_RDONLY))
            finally:
                os.close(descriptor)
                os.close(other)

    def test_shell_scanner_retains_logical_statement_boundaries(self):
        checker = (ROOT / "scripts/check-helper-reachability.sh").read_text(encoding="utf-8")
        python = checker.split("<<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
        function = next(node for node in ast.parse(python).body
                        if isinstance(node, ast.FunctionDef) and node.name == "captured_shell_companion")
        namespace = dict(ast=ast, io=io, json=json, hashlib=hashlib, re=re, tokenize=tokenize,
                         projection_payloads={"standalone_compatibility": {
                             "scripts/claim-run-rotation.py": (CORE / "claim-run-rotation.py").read_bytes()}})
        exec(compile(ast.Module(body=[function], type_ignores=[]), "source_scanner", "exec"), namespace)
        source = (CORE / "claim-run.sh").read_text(encoding="utf-8")
        check = namespace["captured_shell_companion"]
        self.assertTrue(check("claim-run-rotation.py", source))
        changed = source.replace('exec(compile(raw, str(path), "exec",', 'exec\n(compile(raw, str(path), "exec",')
        self.assertNotEqual(changed, source)
        self.assertFalse(check("claim-run-rotation.py", changed))

    def test_current_pending_fixture_profile_is_exact_and_still_refuses_native_reservation(self):
        fixture = load("composite_pending_fixture", ROOT / "tests/cognition-pending-durability.py")
        pins = fixture.source_pins(ROOT)
        selected = fixture.reservation_refusal_profile(pins)
        self.assertEqual(selected["qualified_checkpoint"], "f74a7c6675073af8c78f8a83ef5f3eb1476d2bfb")
        self.assertEqual(selected["stored_json_refusal"], "PENDING_STATE_JSON")
        self.assertEqual(selected["nonfinite_counter_refusal"], "PENDING_STATE_JSON_CONSTANT")
        historical = dict(pins)
        historical[str(fixture.PEER / "compaction-audit-pending.py")] = "9b5faf290e08d3df77b15d5e5301a3760c4e599d16719cf8f72e1768522ea691"
        self.assertEqual(fixture.reservation_refusal_profile(historical), {
            "qualified_checkpoint": "5d90c706518cd08f13dfbb2024e806702cae85e9",
            "expected_reason": "NONPROTECTED_PROJECTION_PROFILE_REQUIRED"})
        self.assertEqual(selected["expected_reason"], "NONPROTECTED_PROJECTION_PROFILE_REQUIRED")
        for name in pins:
            for missing in (False, True):
                changed = dict(pins)
                if missing:
                    del changed[name]
                else:
                    changed[name] = "0" * 64
                with self.subTest(name=name, missing=missing), self.assertRaises(AssertionError):
                    fixture.reservation_refusal_profile(changed)

    def test_explicit_current_prefix_preserves_historical_gate(self):
        prefix = load("composite_prefix", ROOT / "scripts/qualify-work-graph-prefix.py")
        compiler = load("composite_prefix_compiler", CORE / "compile-work-graph.py")
        registry = (ROOT / "scripts/verify-package.sh").read_bytes()
        historical = (ROOT / "test-support/work-graph-registry/original117/verify-package.sh").read_bytes()
        self.assertEqual(hashlib.sha256(historical).hexdigest(), prefix.REGISTRY_SHA256)
        old_graph, old_scope, old_data = prefix.select_prefix(compiler, historical, prefix.ENVIRONMENT)
        self.assertEqual(len(old_graph["nodes"]), 117)
        with self.assertRaisesRegex(ValueError, "registry"):
            prefix.select_prefix(compiler, registry, prefix.ENVIRONMENT)
        graph, scope, data = prefix.select_prefix(
            compiler, registry, prefix.ENVIRONMENT, profile="COMPOSED_COMPOSITE_PREFIX_23_V1")
        self.assertEqual(scope["nodes"], [node["id"] for node in graph["nodes"][:23]])
        self.assertEqual(data, b"".join(node["source"].encode() for node in graph["nodes"][:23]))
        self.assertEqual(scope["stop_before"], "COMMAND:scripts/check-added-lines-clean.sh:0")
        self.assertEqual(scope["registry_sha256"], hashlib.sha256(registry).hexdigest())
        self.assertEqual(scope["canonical_node_count"], len(graph["nodes"]))
        self.assertEqual(scope["composition"], "ONE_COMPOSITE_SHELL_GROUP_NO_HISTORICAL_RECEIPT_REUSE")
        self.assertNotEqual(scope["graph_digest"], old_scope["graph_digest"])
        self.assertNotEqual(data, old_data)
        self.assertEqual(scope["historical_receipt_reuse"], "FORBIDDEN")
        programs = {name: {"sha256": hashlib.sha256((ROOT / name).read_bytes()).hexdigest()}
                    for name in prefix.PROGRAM_PINS}
        prefix.validate_programs({"files": programs}, profile="COMPOSED_COMPOSITE_PREFIX_23_V1")
        with self.assertRaisesRegex(ValueError, "executable"):
            prefix.validate_programs({"files": programs})
        programs["scripts/package-contract.py"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "executable"):
            prefix.validate_programs({"files": programs}, profile="COMPOSED_COMPOSITE_PREFIX_23_V1")
        with self.assertRaisesRegex(ValueError, "registry"):
            prefix.select_prefix(compiler, historical, prefix.ENVIRONMENT,
                                 profile="COMPOSED_COMPOSITE_PREFIX_23_V1")
        for changed in (registry + b"\n", registry.replace(b"tests/composite-source.test.sh", b"tests/omitted-source.test.sh")):
            with self.assertRaisesRegex(ValueError, "registry"):
                prefix.select_prefix(compiler, changed, prefix.ENVIRONMENT,
                                     profile="COMPOSED_COMPOSITE_PREFIX_23_V1")

    def test_pending_corruption_cannot_erase_obligations(self):
        owner = load("composite_pending", PEER / "compaction-audit-pending.py")
        with tempfile.TemporaryDirectory(prefix="composite-pending-") as temp:
            store = Path(temp)
            state = owner.blank("composite-fixture")
            owner.add_observation(state, "observed-boundary", "COMPLETED_RESUMED_BOUNDARY", {})
            path = owner.state_path(store, state["session_id"])
            path.parent.mkdir(parents=True)
            original = json.dumps(state).encode()
            path.write_bytes(original)
            self.assertEqual(owner.decision(owner.load(store, state["session_id"]))["decision"], "AUDIT_STATE_REQUIRED")
            bad = original[:-1] + b', "observations": {}}'
            path.write_bytes(bad)
            with self.assertRaisesRegex(owner.Refusal, "DUPLICATE_JSON_KEY"):
                owner.load(store, state["session_id"])
            self.assertEqual(path.read_bytes(), bad)
            state["observations"]["observed-boundary"]["consumed_version"] = True
            path.write_bytes(json.dumps(state).encode())
            with self.assertRaisesRegex(owner.Refusal, "PENDING_OBSERVATION_COUNTERS"):
                owner.load(store, state["session_id"])
            path.write_bytes(original)
            self.assertTrue(owner.decision(owner.load(store, state["session_id"]))["state_dependent_decisions_held"])

    def test_dangling_pending_is_refused(self):
        owner = load("composite_pending_alias", PEER / "compaction-audit-pending.py")
        with tempfile.TemporaryDirectory(prefix="composite-pending-alias-") as temp:
            store = Path(temp)
            path = owner.state_path(store, "composite-fixture")
            path.parent.mkdir(parents=True)
            try:
                path.symlink_to(path.parent / "missing")
            except OSError as exc:
                if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
                    self.skipTest("Windows symlink privilege unavailable")
                raise
            with self.assertRaises(owner.Refusal):
                owner.load(store, "composite-fixture")
            self.assertTrue(path.is_symlink())

    def test_declared_overlay_rotator_imports_selected_dependency(self):
        with tempfile.TemporaryDirectory(prefix="composite-overlay-") as temp:
            target = Path(temp)
            for name in ("rotate-canonical-state.py", "canonical_hot_projection.py", "canonical_custody.py", "canonical_rotation_inputs.py"):
                source = PEER / name if (PEER / name).is_file() else CORE / name
                shutil.copyfile(source, target / name)
            result = subprocess.run([sys.executable, "-B", str(target / "rotate-canonical-state.py"), "--help"], capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertIn(b"usage:", result.stdout)

    def test_combined_read_closure_is_selected_and_changed_member_refuses(self):
        transport = load("composite_transport", ROOT / "scripts/work-graph-continuity-transport.py")
        names = ("claim-run.sh", "validate-run-root.sh", "claim-run-rotation.py", "rotate-canonical-state.py", "canonical_hot_projection.py", "canonical_custody.py", "canonical_rotation_inputs.py", "read-canonical-pair.py")
        rows = tuple((str(PEER / name), (PEER / name if (PEER / name).is_file() else CORE / name).read_bytes()) for name in names)
        profile = transport._source_profile(rows)
        self.assertEqual(len(profile), 8)
        self.assertIn(profile, transport.ORIGINAL14_SOURCE_PROFILES_V1)
        changed = (*rows[:-1], (rows[-1][0], rows[-1][1] + b"\n"))
        with self.assertRaises(transport.ContinuityTransportError):
            transport._source_profile(changed)

    def test_combined_route_producer_is_source_selected(self):
        graph = load("composite_graph", ROOT / "source-peers/route-graph/skills/implementaudit/scripts/compile-work-graph.py")
        raw = (ROOT / "source-peers/route-graph/skills/implementaudit/scripts/route-transaction.py").read_bytes()
        self.assertEqual(graph._NATIVE_ROUTE_PRODUCER_PROFILES_V1.get(hashlib.sha256(raw).hexdigest()), len(raw))
        self.assertNotIn(hashlib.sha256(raw + b"\n").hexdigest(), graph._NATIVE_ROUTE_PRODUCER_PROFILES_V1)

    def test_overlay_retains_lifecycle_record_interface(self):
        result = subprocess.run([shutil.which("bash"), (PEER / "validate-run-root.sh").as_posix(),
                                 "--turn-disposition", "--help"], capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertIn(b"usage:", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
