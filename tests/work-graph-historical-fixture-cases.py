#!/usr/bin/env python3
"""Historical fixture integrity and explicit current-source refusal controls.

These checks qualify source admission only. They execute no original live leaf,
import no receipt, and do not replace current composite-prefix qualification.
"""
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


H = load("historical_test_inputs", ROOT / "tests/work-graph-historical-fixture.py")
A = load("current_finite_owner", ROOT / "scripts/qualify-work-graph-finite-leaf.py")


class HistoricalInputCases(unittest.TestCase):
    def test_exact_specimens_and_original_registry_are_retained(self):
        for name, row in {**H.MANIFEST["files"], **H.SUPPLEMENTAL}.items():
            with self.subTest(path=name):
                raw = H.original(name)
                self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()),
                                 (row["bytes"], row["sha256"]))
                self.assertIn(row["mode"], (0o644, 0o755))
        self.assertEqual(hashlib.sha256(H.original(A.REGISTRY)).hexdigest(), A.REGISTRY_SHA256)
        self.assertEqual(hashlib.sha256(H.original(A.PREFIX_HELPER)).hexdigest(), A.PREFIX_HELPER_SHA256)
        for profile in A._CONTRACTS:
            contract = A.contract_for(profile)
            for name, expected in {**contract["programs"], **contract.get("pinned_data", {})}.items():
                with self.subTest(profile=profile, pin=name):
                    self.assertEqual(hashlib.sha256(H.selected_input_bytes(name, expected)).hexdigest(), expected,
                                     "each fixture must use its exact selected source profile")
        # Reference specimens do not recursively enter the acquired tests/fixtures subjects.
        self.assertEqual(H.COLLECTION, ROOT / "test-support/work-graph-registry")

    def test_runner_successor_selection_preserves_historical_default(self):
        name = "scripts/run-work-graph-verifier.sh"
        old = H.original(name)
        current_pin = "6f6d2bdbcf8350d6b370d37a5e15f4ddb73d336b5bc42d941540f3269613150f"
        self.assertEqual(H.input_bytes(name), old)
        self.assertEqual(H.selected_input_bytes(name, current_pin), (ROOT / name).read_bytes())
        with self.assertRaisesRegex(ValueError, "selected source pin"):
            H.selected_input_bytes(name, "0" * 64)
        with tempfile.TemporaryDirectory() as temporary:
            changed_root = Path(temporary)
            path = changed_root / name
            path.parent.mkdir(parents=True)
            path.write_bytes((ROOT / name).read_bytes() + b"\n")
            with mock.patch.object(H, "ROOT", changed_root):
                with self.assertRaisesRegex(ValueError, "selected source pin"):
                    H.selected_input_bytes(name, current_pin)
                self.assertEqual(H.input_bytes(name), old)

    def test_changed_specimen_refuses_without_repairing_it(self):
        name = A.REGISTRY
        with tempfile.TemporaryDirectory() as temporary:
            collection = Path(temporary)
            path = collection / H.MANIFEST["files"][name]["specimen"]
            path.parent.mkdir(parents=True)
            changed = H.original(name) + b"\n"
            path.write_bytes(changed)
            with mock.patch.object(H, "COLLECTION", collection):
                with self.assertRaisesRegex(ValueError, "historical specimen changed"):
                    H.original(name)
            self.assertEqual(path.read_bytes(), changed)

    def test_physical_finite_engine_uses_current_code_and_exact_old_dependency(self):
        self.assertEqual(H.Q.ROOT, H.ENGINE_ROOT)
        self.assertEqual(H.Q.LOADED_DRIVER_PATH, H.ENGINE_ROOT / H.ENGINE_NAMES[0])
        for name in H.ENGINE_NAMES:
            expected = H.original(name) if name == A.PREFIX_HELPER else (ROOT / name).read_bytes()
            self.assertEqual((H.ENGINE_ROOT / name).read_bytes(), expected)

    def test_all_historical_selectors_refuse_current_registry(self):
        old, current = H.original(A.REGISTRY), (ROOT / A.REGISTRY).read_bytes()
        self.assertNotEqual(old, current)
        for profile in A._CONTRACTS:
            with self.subTest(profile=profile):
                graph, scope, node = A.select_node(H.Q.WG, old, H.P.ENVIRONMENT, profile=profile)
                self.assertEqual(len(graph["nodes"]), 117)
                self.assertEqual(scope["profile"], profile)
                with self.assertRaisesRegex(ValueError, "registry"):
                    A.select_node(H.Q.WG, current, H.P.ENVIRONMENT, profile=profile)
                with self.assertRaisesRegex(ValueError, "registry"):
                    A.select_node(H.Q.WG, old + b"\n", H.P.ENVIRONMENT, profile=profile)

    def test_current_factory_cannot_use_old_profile_or_create_evidence(self):
        current = load("actual_current_factory", ROOT / "scripts/qualify-work-graph-verifier.py")
        with tempfile.TemporaryDirectory() as temporary:
            for number, profile in enumerate(A._CONTRACTS):
                output = Path(temporary) / str(number)
                with self.subTest(profile=profile), self.assertRaisesRegex(ValueError, "captured prefix helper"):
                    current.create_finite_leaf_session(ROOT, output, profile=profile)
                self.assertFalse(output.exists())

    @unittest.skipUnless(sys.platform == "linux", "physical source descriptors require Linux")
    def test_current_readme_closure_refuses_before_dependent_execution(self):
        current = load("actual_current_readme_loader", ROOT / "scripts/load-work-graph-readme-effect.py")
        with mock.patch.object(current._Engine, "execute") as executed:
            with self.assertRaisesRegex(ValueError, "unsupported fixed engine source"):
                current._load_owner()
        executed.assert_not_called()


@unittest.skipUnless(sys.platform == "linux", "finite source admission requires Linux")
class ChangedCurrentInputCases(unittest.TestCase):
    def test_all_eight_changed_populations_refuse_before_runtime_or_receipt(self):
        cases = {
            A.ACTION_SELECTION_PROFILE: ("action-selection", "SourceCases"),
            A.INTERNAL_ROUTING_PROFILE: ("internal-routing", "AdmissionCases"),
            A.AUDIT_OBJECT_CONTRACT_PROFILE: ("audit-object-contract", "AdmissionCases"),
            A.MARKER_PROFILE: ("finite-batch", "MarkerAdmissionCases"),
            A.TERMINAL_PROFILE: ("recursive", "TerminalAdmission"),
            A.AUTHORIZATION_PROFILE: ("planning", "AuthorizationAdmission"),
            A.BOOTSTRAP_BUDGET_PROFILE: ("bootstrap-budget", "AdmissionCases"),
            A.LEAN_DISCIPLINE_PROFILE: ("lean-discipline", "AdmissionCases"),
        }
        changed = {}
        for profile, contract in A._CONTRACTS.items():
            for name, pin in dict(contract["programs"], **contract.get("pinned_data", {})).items():
                if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != pin:
                    changed.setdefault(profile, []).append(name)
        self.assertEqual(set(changed), set(cases))
        for profile, names in changed.items():
            stem, class_name = cases[profile]
            module = load("selected_" + stem.replace("-", "_"),
                          ROOT / ("tests/work-graph-" + stem + "-cases.py"))
            for name in names:
                fixture = getattr(module, class_name)()
                try:
                    fixture.setUp()
                    fixture.snapshot()  # Prove the selected positive is admissible first.
                    path = fixture.source / name
                    original = path.read_bytes()
                    current = (ROOT / name).read_bytes()
                    self.assertNotEqual(original, current)
                    path.write_bytes(current)
                    session = fixture.session()
                    scope = session._acquire.__func__.__globals__
                    with mock.patch.object(session, "_observer", return_value=mock.sentinel.source_only), \
                         mock.patch.dict(scope, {"finite_runtime": mock.Mock(side_effect=AssertionError("runtime reached"))}), \
                         mock.patch.object(session, "_execute", side_effect=AssertionError("dispatch reached")):
                        with self.subTest(profile=profile, path=name), self.assertRaisesRegex(ValueError, "source|executable|pinned branch"):
                            session.run()
                    self.assertEqual(session.dispatch_count, 0)
                    self.assertEqual(session._issued, {})
                    self.assertFalse(list(session.output.rglob("receipt.json")))
                    self.assertEqual(path.read_bytes(), current)  # Acquisition did not restore old input.
                finally:
                    fixture.doCleanups()


if __name__ == "__main__":
    unittest.main(verbosity=2)
