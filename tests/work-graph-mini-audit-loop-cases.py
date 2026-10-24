#!/usr/bin/env python3
"""Ten original87 source/boundary controls; no runtime/original qualification.

The complete genuine template corpus is repository test data. Tests validate
and materialize it privately without an environment or host-tree fallback.
Production has no template-root override; no Git/runtime/launcher is called.
"""
import ast
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "CONTROLLED_TASK_MINI_AUDIT_LOOP_V1"
MODE = "mini-audit-loop"
PROGRAM = "tests/e2e-mini-audit-loop.test.sh"
PHASE = "fixtures/e2e-mini-audit-loop/phase-1.md"
TRANSCRIPT = "fixtures/e2e-mini-audit-loop/EXPECTED-TRANSCRIPT.md"
PROTOCOL = "skills/implementaudit/templates/PROTOCOL.md"
PROGRAMS = {
    PROGRAM: "8b4aff39b1da3c36d1ebc9e020923e214dec4926e5426ac4e322d59d444308f3",
    "skills/implementaudit/scripts/validate-phase.sh": "07b2e04ba9aefffc572ac9cf60ecddf88654a26590aaa045dadf464da7bc7dab",
    "skills/implementaudit/scripts/repo-state.sh": "b2220d0627c5e66d106bb3ce8a9daafb5310b87643b9281d63db5a5aa886df3b",
}
INCOMING_CONTRACTS_AST_SHA256 = "117ae99baa7584e7d94552dc6ea4eff5bc170a517131d28ba979708634e32f93"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


B = load("mini_audit_shared_fixtures", ROOT / "tests/work-graph-audit-spec-cases.py")


class MiniFixture(B.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        # Mock only forbidden effects. The production template/source readers,
        # resource derivation, image builder and refusal logic run unchanged.
        guards = (
            mock.patch.object(B.P, "acquire_runtime", side_effect=AssertionError("runtime acquisition forbidden")),
            mock.patch.object(self.A, "finite_runtime", side_effect=AssertionError("runtime acquisition forbidden")),
            mock.patch.object(B.Q.VerifierTaskSession, "_execute", side_effect=AssertionError("original dispatch forbidden")),
            mock.patch("subprocess.Popen", side_effect=AssertionError("external execution forbidden")),
        )
        for guard in guards:
            guard.start()
            self.addCleanup(guard.stop)

    def templates(self):
        # Validate the entire fixed test corpus before writing private fixtures.
        # Production still captures its actual fixed physical template root.
        corpus = json.loads((ROOT / "fixtures/work-graph-mini-audit-loop/git-template-corpus.json").read_bytes())
        self.assertEqual(set(corpus), {"schema", "origin", "directories", "files", "totals"})
        self.assertEqual(corpus["schema"], "implementaudit.test-git-template-corpus.v1")
        self.assertEqual(corpus["origin"], dict(kind="GENUINE_FROZEN_TEMPLATE_BYTES_TEST_DATA_ONLY",
            source_wip_manifest_sha256="5ff119fb9fbd0c89395a7e3cece07f08115a1caa99a80501e7116c2972dc9a42"))
        self.assertEqual(corpus["directories"], self.A._MINI_AUDIT_TEMPLATE_DIRECTORIES)
        self.assertEqual(set(corpus["files"]), set(self.A._MINI_AUDIT_TEMPLATE_FILES))
        decoded = {}
        for name, pin in self.A._MINI_AUDIT_TEMPLATE_FILES.items():
            row = corpus["files"][name]
            self.assertEqual(set(row), {"mode", "bytes", "sha256", "base64"})
            self.assertEqual({key: row[key] for key in ("mode", "bytes", "sha256")}, pin)
            raw = base64.b64decode(row["base64"], validate=True)
            self.assertEqual(len(raw), row["bytes"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
            decoded[name] = (raw, row["mode"])
        self.assertEqual(corpus["totals"], dict(files=len(decoded), directories=len(corpus["directories"]),
            bytes=sum(len(raw) for raw, _ in decoded.values())))
        self.assertEqual(corpus["totals"], dict(files=16, directories=4, bytes=26134))
        target = self.base / "templates"
        for name, mode in sorted(corpus["directories"].items(), key=lambda pair: (pair[0].count("/"), pair[0])):
            directory = target if name == "." else target / name
            directory.mkdir(parents=True, exist_ok=True)
            directory.chmod(mode)
        for name, (raw, mode) in decoded.items():
            path = target / name
            path.write_bytes(raw)
            path.chmod(mode)
        return target

    def assert_no_dispatch(self, session):
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})
        self.assertEqual(list(session.output.rglob("dispatch.json")), [])


class CatalogCases(MiniFixture, unittest.TestCase):
    def test_fixed_profile_source_consumer(self):
        """C01: exact original87 catalog, seven inputs, mode and inherited owners."""
        contract = self.A.contract_for(PROFILE)
        self.assertEqual((contract["index"], contract["program"]), (87, PROGRAM))
        self.assertEqual(contract["programs"], PROGRAMS)
        self.assertEqual(set(contract["data"]), {PHASE, PROTOCOL, TRANSCRIPT})
        self.assertEqual(contract["pinned_data"], {
            PHASE: "44a48a1a22e8bb7a783aa0b4c3608e2d75afe4ad4d74ac720931f759b7cde06b"})
        self.assertEqual(contract["bounds"], dict(file_bytes=131072, total_bytes=524288, files=7))
        self.assertEqual(contract["source_modes"], "PRESERVE_READ_ONLY_MOUNT")
        self.assertEqual(B.Q._FINITE_MODES[MODE], PROFILE)
        entry = ast.parse((ROOT / "tests/work-graph-finite-entry-cases.py").read_bytes())
        modes = next(node.value for node in entry.body if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == "PROFILES" for target in node.targets))
        self.assertEqual(ast.literal_eval(modes)[MODE], PROFILE)
        registry = (ROOT / self.A.REGISTRY).read_bytes()
        graph, scope, node = self.A.select_node(B.Q.WG, registry, B.P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual(len(graph["nodes"]), 117)
        self.assertEqual(node, graph["nodes"][87])
        self.assertEqual(node["source"], "bash " + PROGRAM + "\n")
        self.assertEqual((node["byte_start"], node["byte_end"]), (42194, 42233))
        self.assertEqual(scope["nodes"], ["COMMAND:" + PROGRAM + ":0"])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        self.assertEqual(hashlib.sha256(node["source"].encode()).hexdigest(),
                         "894da2489ef3e7ee99106223882893727292289316d10879d6b84748e2f65b53")
        state, _, objects = self.snapshot()
        self.assertEqual(set(state["files"]), {self.A.REGISTRY, *PROGRAMS, PHASE, PROTOCOL, TRANSCRIPT})
        self.assertNotIn("complete_git_inputs", state)
        for name, row in state["files"].items():
            self.assertEqual(objects[row["sha256"]], (self.source / name).read_bytes())
        incoming = next(node.value for node in ast.parse(self.helper).body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "_CONTRACTS" for target in node.targets))
        retained = [(key, value) for key, value in zip(incoming.keys, incoming.values)
                    if not isinstance(key, ast.Name) or key.id != "MINI_AUDIT_PROFILE"]
        self.assertEqual(len(retained), 33)
        payload = "\n".join(ast.dump(ast.Tuple(elts=[key, value], ctx=ast.Load()), include_attributes=False)
                            for key, value in retained)
        self.assertEqual(hashlib.sha256(payload.encode()).hexdigest(), INCOMING_CONTRACTS_AST_SHA256)
        self.assertEqual(hashlib.sha256((ROOT / self.A.RUNNER).read_bytes()).hexdigest(),
                         "532b06dbe91298bf71d44c88ecf20186adc93b4e3fb16ee2c4d12bc2edee45ff")
        session = self.session()
        self.assertEqual(session.ENVIRONMENT, dict(B.P.ENVIRONMENT, HOME="/nonexistent", GIT_ATTR_NOSYSTEM="1"))
        self.assertEqual(session.SCOPE, PROFILE)
        self.assert_no_dispatch(session)


class DataCases(MiniFixture, unittest.TestCase):
    def test_negative_transcript_is_acquired_as_data(self):
        """C02: the faithful original negative reaches the runtime boundary as data."""
        path = self.source / TRANSCRIPT
        before = path.read_bytes()
        self.assertEqual(before.count(b"IMPLEMENTAUDIT_RUN_COMPLETE\n"), 1)
        changed = before.replace(b"IMPLEMENTAUDIT_RUN_COMPLETE\n", b"")
        path.write_bytes(changed)
        state, _, objects = self.snapshot()
        self.assertEqual(objects[state["files"][TRANSCRIPT]["sha256"]], changed)
        self.assertEqual(state["files"][TRANSCRIPT]["sha256"],
                         "eb7a6bb381a268f258f8d10cbf35cbc71ab945785475119d4c8631001908bb77")
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "source-admission fixture reached runtime acquisition"):
            session.run()
        self.assert_no_dispatch(session)

    def test_unacquired_phase_branch_refuses_before_runtime(self):
        """C03: altered scarce-resource selector cannot load an unacquired validator."""
        path = self.source / PHASE
        path.write_bytes(path.read_bytes() + b"\nScarce resource budget: bounded-review\n")
        session = self.session()
        with self.assertRaisesRegex(ValueError, "pinned branch input"):
            session.run()
        self.assert_no_dispatch(session)


class TemplateCases(MiniFixture, unittest.TestCase):
    def test_complete_templates_and_empty_directory_bind_both_images(self):
        """C04: exact copied data/modes and empty branches enter both image keys."""
        root = self.templates()
        objects = {}
        state, stamps = self.A._mini_audit_template_snapshot(B.P, root, objects)
        self.assertEqual(len(state["files"]), 16)
        self.assertEqual(state["directories"], {".": 0o755, "branches": 0o755, "hooks": 0o755, "info": 0o755})
        self.assertEqual(sum(row["bytes"] for row in state["files"].values()), 26134)
        self.assertEqual({row["mode"] for row in state["files"].values()}, {0o644, 0o755})
        for name, row in state["files"].items():
            self.assertEqual(objects[row["sha256"]], (root / name).read_bytes())
        logical = self.A._MINI_AUDIT_TEMPLATE_ROOT
        templates = dict(root=logical, projection=state, currentness=stamps,
            bounds=dict(self.A._MINI_AUDIT_TEMPLATE_BOUNDS),
            policy="ACTUAL_COMPLETE_DEFAULT_TEMPLATE_TREE_NO_FILTER_NO_OVERRIDE")
        files = {logical + "/" + name: (objects[row["sha256"]], row["mode"])
                 for name, row in state["files"].items()}
        session = self.session()
        for name, members in (("runtime", files), ("original", dict(files, **{"/work/input": (b"data", 0o644)}))):
            with self.subTest(image=name):
                manifest, before = session._image(members, {})
                self.assertNotIn(logical + "/branches", manifest["directories"])
                self.A._mini_audit_template_image(manifest, templates)
                key = session._object(session._encode(manifest))
                self.assertNotEqual(key, before)
                self.assertIn(logical + "/branches", manifest["directories"])
                self.assertFalse(any(row["path"].startswith(logical + "/branches/") for row in manifest["files"]))
                self.assertEqual(manifest["mini_audit_git_templates"], templates)
                self.assertTrue(manifest["root_read_only"])
        self.assert_no_dispatch(session)

    def test_added_active_hook_refuses_complete_population(self):
        """C05: an active hook is rejected by complete census, never filtered."""
        root = self.templates()
        path = root / "hooks/pre-commit"
        raw = b"#!/bin/sh\nexit 0\n"
        path.write_bytes(raw)
        path.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "complete original87 Git template population"):
            self.A._mini_audit_template_snapshot(B.P, root, {})
        self.assertEqual(path.read_bytes(), raw)

    def test_added_template_config_refuses_complete_population(self):
        """C06: a config-bearing initializer cannot select hooks or helpers."""
        root = self.templates()
        path = root / "config"
        raw = b"[core]\n\thooksPath = unexpected-hooks\n"
        path.write_bytes(raw)
        path.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "complete original87 Git template population"):
            self.A._mini_audit_template_snapshot(B.P, root, {})
        self.assertEqual(path.read_bytes(), raw)

    def test_selected_template_symlink_refuses(self):
        """C07: the actual typed reader rejects aliases in selected data."""
        root = self.templates()
        path = root / "info/exclude"
        path.unlink()
        path.symlink_to("../description")
        with self.assertRaisesRegex(ValueError, "ordinary directories and single-link files"):
            self.A._mini_audit_template_snapshot(B.P, root, {})

    def test_closing_template_census_refuses_added_member(self):
        """C08: real closing census catches a change after initial typed capture."""
        root = self.templates()
        original = B.P.snapshot_tree
        calls = 0

        def raced(*args, **kwargs):
            nonlocal calls
            calls += 1
            result = original(*args, **kwargs)
            if calls == 1:
                (root / "hooks/pre-commit").write_bytes(b"late member\n")
            return result

        with mock.patch.object(B.P, "snapshot_tree", side_effect=raced):
            with self.assertRaisesRegex(ValueError, "template namespace changed"):
                self.A._mini_audit_template_snapshot(B.P, root, {})
        self.assertEqual(calls, 2)


class BindingCases(MiniFixture, unittest.TestCase):
    def test_foreign_git_object_refuses_before_physical_reads(self):
        """C09: matching saved metadata cannot bless a different Git object."""
        pins = self.A._MINI_AUDIT_GIT_PINS
        self.assertEqual(pins["/usr/bin/git"]["sha256"],
                         "2a8c18fbf43da9f692d75474c72bea9dfd796c260b0f3dfe456376abc3bbd668")
        runtime = dict(files={name: dict(mode=0o555 if pin["mode"] & 0o111 else 0o444,
            bytes=pin["bytes"], sha256=pin["sha256"]) for name, pin in pins.items()},
            observations={name: dict(pin) for name, pin in pins.items()})
        git_key = pins["/usr/bin/git"]["sha256"]

        class ForeignGitOnly(dict):
            def get(self, key, default=None):
                if key != git_key:
                    raise AssertionError("foreign Git must refuse before dependency object reads")
                return b"foreign Git bytes"

        objects = ForeignGitOnly()
        with mock.patch.object(B.P, "read_regular", side_effect=AssertionError("physical runtime read forbidden")) as reader:
            with self.assertRaisesRegex(ValueError, "captured Git/default linkage"):
                self.A._mini_audit_git_runtime_binding(B.P, runtime, objects)
            reader.assert_not_called()

    def test_fixed_private_write_reservation_and_capacity_boundary(self):
        """C10: fixed source-derived private allocation fits unchanged32MiB only."""
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((reservation["files"], reservation["directories"]), (60, 32))
        self.assertEqual(reservation["required_bytes"], 10027008)
        self.assertEqual(reservation["copies"], 19)
        self.assertEqual(reservation["script_copied_files"] + reservation["script_generated_files"], 5)
        self.assertEqual((reservation["template_copied_files"], reservation["git_generated_file_slots"],
                          reservation["validator_spools"]), (16, 32, 7))
        session = self.session()
        self.assertEqual(session.LIMITS["scratch_bytes"], 32 * 1024**2)
        self.assertEqual({key: session.LIMITS[key] for key in (
            "cpu_seconds", "wall_seconds", "address_bytes", "file_bytes", "stream_bytes", "descriptors",
            "retained_object_bytes", "evidence_bytes")}, dict(cpu_seconds=90, wall_seconds=120,
            address_bytes=1024**3, file_bytes=16 * 1024**2, stream_bytes=16 * 1024**2,
            descriptors=4096, retained_object_bytes=1024**3, evidence_bytes=2 * 1024**3))
        self.A.require_resource_capacity(reservation, session.LIMITS)
        with self.assertRaisesRegex(ValueError, "scratch capacity"):
            self.A.require_resource_capacity(reservation, dict(session.LIMITS, scratch_bytes=10027007))
        self.assert_no_dispatch(session)


if __name__ == "__main__":
    unittest.main()
