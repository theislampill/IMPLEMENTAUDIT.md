"""Combined portable interfaces only; no authentic admission or native effects."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
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
    def test_current_pending_fixture_profile_is_exact_and_still_refuses_native_reservation(self):
        fixture = load("composite_pending_fixture", ROOT / "tests/cognition-pending-durability.py")
        pins = fixture.source_pins(ROOT)
        selected = fixture.reservation_refusal_profile(pins)
        self.assertEqual(selected["qualified_checkpoint"], "5d90c706518cd08f13dfbb2024e806702cae85e9")
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
        historical = (ROOT / "fixtures/work-graph-registry/original117.verify-package.sh").read_bytes()
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
