#!/usr/bin/env python3
"""Original75 source/boundary controls; no original execution or authority."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
spec = importlib.util.spec_from_file_location("package_shape_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = "CONTROLLED_TASK_PACKAGE_SHAPE_CLAIMS_V1"
MODE = "package-shape-claims"
PROGRAM = "tests/package-shape-claims.test.sh"
CHECKER = "scripts/check-package-shape-claims.sh"
DATA = (
    "package/implementaudit-package.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json",
    "AGENTS.md", "README.md", "CONTRIBUTING.md", "docs/portal/site.json",
)
TREE_FILES = (
    *("skills/" + name + "/SKILL.md" for name in
      ("implementaudit", "audit-state", "audit-assess", "audit-implement", "audit-andon")),
    "docs/portal/pages/package-contents.html", "docs/portal/pages/what-it-is.html",
)


class CatalogCases(unittest.TestCase):
    def test_original75_profile_and_exact_consumers(self):
        A, _ = shared.load("package_shape_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        try:
            contract = A.contract_for(PROFILE)
        except ValueError as error:
            self.fail("missing exact original75 profile/source consumer: " + str(error))
        registry = H.original("scripts/verify-package.sh")
        graph, scope, node = A.select_node(Q.WG, registry, P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][75]))
        self.assertEqual(node["source"], "bash tests/package-shape-claims.test.sh\n")
        self.assertEqual(scope["nodes"], ["COMMAND:tests/package-shape-claims.test.sh:0"])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        self.assertEqual(contract["programs"], {
            PROGRAM: "62423be42e48121a3af91e962cf523248fbeea5c31d666a89f831a651ba947ad",
            CHECKER: "8cf31dfa733650ad2359121036d640bb35486d79736dbea965315def6c8a3136",
        })
        self.assertEqual(set(A.source_paths(PROFILE)), {"scripts/verify-package.sh", PROGRAM, CHECKER, *DATA})
        self.assertEqual(contract["recursive"]["roots"], ("skills", "docs/portal/pages"))
        self.assertFalse(contract["recursive"]["optional"])
        self.assertEqual(contract["source_modes"], "PRESERVE_READ_ONLY_MOUNT")
        self.assertEqual(contract["scratch_bytes"], 64 * 1024**2)
        self.assertEqual(Q._FINITE_MODES[MODE], PROFILE)
        entry, _ = shared.load("package_shape_entry", ROOT / "tests/work-graph-finite-entry-cases.py")
        self.assertEqual(entry.PROFILES[MODE], PROFILE)
        with self.assertRaisesRegex(ValueError, "registry"):
            A.select_node(Q.WG, registry + b"\n", P.ENVIRONMENT, profile=PROFILE)


class PackageShapeFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        for name in TREE_FILES:
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / name).read_bytes())
            path.chmod(0o644)

    def session(self, name="evidence"):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=PROFILE))

    def no_execution(self, session):
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})
        self.assertFalse((session.output / "objects").exists())
        self.assertEqual(list(session.output.rglob("receipt.json")), [])
        self.assertEqual(list(session.output.rglob("dispatch.json")), [])


class AdmissionCases(PackageShapeFixture, unittest.TestCase):
    def test_complete_names_types_empty_directories_and_bytes_are_retained(self):
        extra = self.source / "docs/portal/pages/.nonmatching-data"
        extra.write_bytes(b"non-HTML bytes\x00\xff")
        empty = self.source / "skills/empty-child"
        empty.mkdir()
        state, stamps, objects = self.snapshot()
        self.assertEqual(set(state["files"]), {
            "scripts/verify-package.sh", PROGRAM, CHECKER, *DATA, *TREE_FILES,
            "docs/portal/pages/.nonmatching-data",
        })
        self.assertIn("skills/empty-child", state["directories"])
        self.assertIn("recursive_inputs", stamps)
        self.assertEqual(state["recursive_inputs"]["projection"]["probes"], {
            "skills": {"kind": "DIRECTORY"}, "docs/portal/pages": {"kind": "DIRECTORY"},
        })
        for name, record in state["files"].items():
            self.assertEqual(objects[record["sha256"]], (self.source / name).read_bytes())
        self.assertNotIn("scripts/verify-package.sh", self.A.image_subject(state, profile=PROFILE))
        self.assertFalse((self.source / ".git").exists())

    def test_extra_skill_population_reaches_original_oracle_as_data(self):
        before, _, _ = self.snapshot()
        path = self.source / "skills/unexpected-child/SKILL.md"
        path.parent.mkdir()
        path.write_bytes(b"---\nname: unexpected-child\n---\n")
        after, _, objects = self.snapshot()
        self.assertNotEqual(before, after)
        self.assertEqual(objects[after["files"]["skills/unexpected-child/SKILL.md"]["sha256"]], path.read_bytes())
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.no_execution(session)

    def test_new_portal_page_claim_reaches_original_oracle_as_data(self):
        path = self.source / "docs/portal/pages/new-current-page.html"
        path.write_bytes(b"Codex natively discovers the plugin.\n")
        state, _, objects = self.snapshot()
        subject = self.A.image_subject(state, profile=PROFILE)
        self.assertIn("docs/portal/pages/new-current-page.html", subject)
        self.assertEqual(objects[subject["docs/portal/pages/new-current-page.html"]["sha256"]], path.read_bytes())
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.no_execution(session)

    def test_malformed_manifest_is_retained_without_semantic_substitution(self):
        path = self.source / DATA[0]
        path.write_bytes(b"{malformed package contract\n")
        state, _, objects = self.snapshot()
        self.assertEqual(objects[state["files"][DATA[0]]["sha256"]], path.read_bytes())
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.no_execution(session)

    def test_missing_literal_or_required_page_refuses_before_runtime(self):
        for index, name in enumerate((DATA[0], TREE_FILES[-1])):
            path = self.source / name
            original = path.read_bytes()
            path.unlink()
            session = self.session("missing-" + str(index))
            with self.subTest(path=name), self.assertRaises((ValueError, OSError)):
                session.run()
            self.no_execution(session)
            path.write_bytes(original)

    def test_aliased_glob_member_refuses_before_runtime(self):
        path = self.source / "docs/portal/pages/aliased.html"
        path.symlink_to(self.source / TREE_FILES[-1])
        session = self.session()
        with self.assertRaises((ValueError, OSError)):
            session.run()
        self.no_execution(session)

    def test_new_member_during_closing_census_refuses(self):
        original = P.snapshot_tree
        changed = False

        def racing_snapshot(root, *args, **kwargs):
            nonlocal changed
            result = original(root, *args, **kwargs)
            if Path(root) == self.source / "docs/portal/pages" and not changed:
                changed = True
                (Path(root) / "late-page.html").write_bytes(b"late current surface\n")
            return result

        with mock.patch.object(P, "snapshot_tree", racing_snapshot):
            with self.assertRaisesRegex(ValueError, "changed"):
                self.snapshot()
        self.assertTrue(changed)

    def test_changed_checker_refuses_before_runtime_or_dispatch(self):
        path = self.source / CHECKER
        path.write_bytes(path.read_bytes() + b"\n")
        session = self.session()
        with self.assertRaisesRegex(ValueError, "executable"):
            session.run()
        self.no_execution(session)

    def test_fixed_private_write_census_and_resource_refusals(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((reservation["copies"], reservation["files"], reservation["directories"]), (15, 239, 199))
        self.assertEqual((reservation["fixture_trees"], reservation["fixture_files"],
                          reservation["extra_generated_files"]), (15, 210, 2))
        self.assertEqual((reservation["checker_spools"], reservation["wrapper_spools"]), (17, 10))
        self.assertEqual(reservation["required_bytes"], 44367872)
        self.assertEqual(reservation["fixture_json_file_bounds"], [
            6 * state["files"][name]["bytes"] + 256 for name in DATA[:3]])
        session = self.session()
        self.assertEqual(session.LIMITS["scratch_bytes"], 64 * 1024**2)
        self.A.require_resource_capacity(reservation, session.LIMITS)
        for field, value in (("scratch_bytes", reservation["required_bytes"] - 1),
                             ("file_bytes", reservation["largest_file_bytes"] - 1),
                             ("stream_bytes", reservation["max_stderr_bytes"] - 1),
                             ("address_bytes", reservation["original_data_memory_reservation"])):
            with self.subTest(limit=field), self.assertRaisesRegex(ValueError, "capacity"):
                self.A.require_resource_capacity(reservation, dict(session.LIMITS, **{field: value}))
        with self.assertRaisesRegex(ValueError, "scratch capacity"):
            self.A.require_resource_capacity(reservation, dict(session.LIMITS, scratch_bytes=32 * 1024**2))
        path = self.source / DATA[0]
        path.write_bytes(path.read_bytes() + b" " * 16384)
        larger, _, _ = self.snapshot()
        increased = self.A.temporary_requirements(larger, profile=PROFILE)
        self.assertGreater(increased["required_bytes"], reservation["required_bytes"])
        self.assertGreater(increased["original_data_memory_reservation"], reservation["original_data_memory_reservation"])

    def test_public_custody_and_runtime_tripwire_grant_no_execution_credit(self):
        session = self.session()
        record = json.loads((session.output / "session.json").read_bytes())
        self.assertEqual(record["scope"], PROFILE)
        self.assertEqual(record["receipt_custody"], "LIVE_PRODUCER_ONLY_NO_IMPORT")
        self.assertEqual(session.environment, P.ENVIRONMENT)
        with self.assertRaises(TypeError):
            session.run(receipt={"exit": 0})
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.no_execution(session)


class IntegrationCases(unittest.TestCase):
    def test_new_bank_reaches_capture_environment_boundary(self):
        # The existing probe records argv/environment, never executes the old banks.
        verifier, _ = shared.load("package_shape_capture", ROOT / "tests/work-graph-verifier-cases.py")
        with tempfile.TemporaryDirectory() as temporary:
            verifier.fixture_capture_environment_cases(Path(temporary) / "capture")


if __name__ == "__main__":
    unittest.main()
