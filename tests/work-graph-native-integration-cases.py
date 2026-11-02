#!/usr/bin/env python3
"""Original74 finite source contract; no native-host acceptance claim."""
import importlib.util
import os
from pathlib import Path
import re
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
spec = importlib.util.spec_from_file_location("native_integration_recursive", ROOT / "tests/work-graph-recursive-cases.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
PROFILE = "CONTROLLED_TASK_NATIVE_INTEGRATION_V1"
PROGRAM = "tests/native-integration.test.sh"
R.MAPPING[PROFILE] = (74, PROGRAM)


class CatalogCases(unittest.TestCase):
    def test_original74_mapping_is_explicit_and_registry_bound(self):
        catalog, _ = R.shared.load("native_integration_catalog", R.HELPER)
        registry = H.original("scripts/verify-package.sh")
        graph, scope, node = catalog.select_node(R.Q.WG, registry, R.P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual(len(graph["nodes"]), 117)
        self.assertEqual(node, graph["nodes"][74])
        self.assertEqual(node["source"], "bash " + PROGRAM + "\n")
        self.assertEqual(scope["nodes"], ["COMMAND:" + PROGRAM + ":0"])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        with self.assertRaisesRegex(ValueError, "registry"):
            catalog.select_node(R.Q.WG, registry + b"\n", R.P.ENVIRONMENT, profile=PROFILE)


class Fixture(R.RecursiveFixture):
    PROFILE = PROFILE

    def session(self, name="evidence", **options):
        return self.source_admission_session(super().session(name, **options))


class AdmissionCases(Fixture, unittest.TestCase):
    def test_complete_all_fixtures_skills_portal_optional_files_and_modes(self):
        for tree in ("fixtures", "skills", "docs/portal"):
            added = self.source / tree / ".hidden/.binary"
            added.parent.mkdir(parents=True)
            added.write_bytes(b"\x00\xff\r\nopaque complete input\n")
            (added.parent / ".empty").mkdir()
        state, _, objects = self.snapshot()
        expected = set(self.A.source_paths(PROFILE)) | {"README.md", "AGENTS.md"}
        for tree in ("fixtures", "skills", "docs/portal"):
            expected.update(p.relative_to(self.source).as_posix() for p in (self.source / tree).rglob("*") if p.is_file())
            self.assertIn(tree + "/.hidden/.empty", state["directories"])
        self.assertEqual(set(state["files"]), expected)
        self.assertIn("fixtures/authorization-binding/auth.txt", state["files"])
        self.assertIn("fixtures/audit-object-routing/category-matrix.md", state["files"])
        for name, entry in state["files"].items():
            self.assertEqual(objects[entry["sha256"]], (self.source / name).read_bytes())
            self.assertEqual(entry["mode"], (self.source / name).stat().st_mode & 0o777)
        self.assertEqual(self.A.contract_for(PROFILE)["source_modes"], "PRESERVE_READ_ONLY_MOUNT")

    def test_optional_root_file_portal_and_audit_routing_absences_are_observed(self):
        before, _, _ = self.snapshot()
        for name in ("README.md", "AGENTS.md"):
            (self.source / name).unlink()
        shutil.rmtree(self.source / "docs/portal")
        shutil.rmtree(self.source / "fixtures/audit-object-routing")
        after, _, _ = self.snapshot()
        self.assertNotEqual(before, after)
        probes = after["recursive_inputs"]["projection"]["probes"]
        for name in ("README.md", "AGENTS.md", "docs/portal"):
            self.assertEqual(probes[name]["kind"], "MISSING")
        self.assertFalse(any(name.startswith("fixtures/audit-object-routing/") for name in after["files"]))
        self.assertNotIn("fixtures/audit-object-routing", after["directories"])

    def test_all_seventeen_required_original_operands_refuse_absence(self):
        required = self.A.contract_for(PROFILE)["recursive"]["required_members"]
        self.assertEqual(len(required), 17)
        for name in required:
            path = self.source / name
            raw, mode = path.read_bytes(), path.stat().st_mode & 0o777
            path.unlink()
            with self.subTest(path=name), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.write_bytes(raw)
            path.chmod(mode)

    def test_complete_fixture_population_rejects_alias_nonregular_and_unsupported_mode(self):
        outside = self.base / "outside"
        outside.write_bytes(b"not owned source\n")
        path = self.source / "fixtures/.added"
        for kind in ("symlink", "hardlink", "fifo", "mode"):
            if kind == "symlink": path.symlink_to(outside)
            elif kind == "hardlink": os.link(outside, path)
            elif kind == "fifo": os.mkfifo(path)
            else: path.write_bytes(b"unreadable\n"); path.chmod(0)
            with self.subTest(kind=kind), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.unlink()

    def test_changed_program_or_registry_refuses_before_runtime_or_dispatch(self):
        for index, name in enumerate((*self.A.contract_for(PROFILE)["programs"], self.A.REGISTRY)):
            session = self.session("program-" + str(index))
            path = self.source / name
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "source|registry|executable"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            self.assertEqual(list(session.output.rglob("dispatch.json")), [])
            path.write_bytes(raw)

    def test_semantic_invalidity_in_unrelated_fixture_is_retained_and_reaches_runtime(self):
        path = self.source / "fixtures/.outside-native-hygiene"
        path.write_bytes(b"password is abcdefghi\n")  # Deliberately invalid synthetic test data.
        state, _, objects = self.snapshot()
        name = path.relative_to(self.source).as_posix()
        self.assertEqual(objects[state["files"][name]["sha256"]], path.read_bytes())
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "reached runtime acquisition"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(list(session.output.rglob("dispatch.json")), [])

    def test_report_bounds_preserve_raw_lf_and_unicode_case_insensitive_matches(self):
        before, _ = self.requirements()
        path = self.source / "skills/.line-bound"
        raw = b"x" * 10000 + b"\r\v\fnon-native slash mode\n"
        path.write_bytes(raw)
        changed, _ = self.requirements()
        first = before["recursive_inputs"]["resources"]
        second = changed["recursive_inputs"]["resources"]
        self.assertGreaterEqual(second["default_first_grep_bytes"] - first["default_first_grep_bytes"], len(raw))
        samples = ("paſſword is abcdefghi", "apİkey = abcdefghijklmnop",
                   "apıkey = abcdefghijklmnop", "apiKey = abcdefghijklmnop")
        for line in samples:
            self.assertIsNotNone(re.search(r"password|api[_-]?key", line, re.I))
        path = self.source / "fixtures/.unicode-hygiene"
        path.write_text("\u2028".join(samples) + "\nEXAMPLE password is abcdefghi\n", encoding="utf-8")
        final, _ = self.requirements()
        self.assertGreaterEqual(final["recursive_inputs"]["resources"]["default_hygiene_bytes"] - second["default_hygiene_bytes"], 5 * 6 * 128)

    def test_deleted_invalid_utf8_line_cannot_hide_private_hygiene_allocation(self):
        _, baseline = self.requirements()
        self.A.require_resource_capacity(baseline, self.session("baseline").LIMITS)
        cases = (("transcripts/audit-object-route-canary-transcript.md", b"AUDIT_VERIFY"),
                 ("negative-generic-roadmap.md", b"DMADV direction/design"))
        for index, (relative, marker) in enumerate(cases):
            name = "fixtures/native-integration/" + relative
            path = self.source / name
            original = path.read_bytes()
            try:
                # Both pinned original sed expressions delete complete LF
                # records. Removing the only invalid record exposes these
                # otherwise skipped, unexempted synthetic diagnostic lines.
                raw = original + b"\xff " + marker + b"\n" + b"hunter2\n" * 130000
                with self.assertRaises(UnicodeDecodeError):
                    raw.decode("utf-8", "strict")
                after = b"\n".join(line for line in raw.split(b"\n") if marker not in line)
                lines = after.decode("utf-8", "strict").splitlines()
                numbers = [n for n, line in enumerate(lines, 1) if line == "hunter2"]
                self.assertEqual(len(numbers), 130000)
                label = "toy password that normalizes secret copying"
                lower_bound = sum(len((name + ":" + str(n) + ": " + label + "\n").encode())
                                  for n in numbers)
                path.write_bytes(raw)
                _, reservation = self.requirements()
                session = self.session("repaired-utf8-" + str(index))
                with self.subTest(path=name):
                    if index == 0:
                        self.assertGreater(lower_bound, session.LIMITS["stream_bytes"])
                    self.assertGreaterEqual(reservation["max_stderr_bytes"], lower_bound)
                    with self.assertRaisesRegex(ValueError, "capacity"):
                        session.run()
                    self.assertEqual(session.dispatch_count, 0)
                    self.assertEqual(list(session.output.rglob("dispatch.json")), [])
            finally:
                path.write_bytes(original)

    def test_all_seven_retained_trees_and_every_private_effect_are_reserved(self):
        state, reservation = self.requirements()
        trees = [self.source / "skills", self.source / "fixtures/native-integration"]
        copied_files = [p for tree in trees for p in tree.rglob("*") if p.is_file()]
        copied_dirs = sum(1 + sum(p.is_dir() for p in tree.rglob("*")) for tree in trees)
        self.assertEqual(reservation["copies"], 7)
        self.assertEqual(reservation["copied_files"], 7 * len(copied_files))
        self.assertEqual(reservation["directories"], 1 + 7 * (copied_dirs + 2))
        self.assertEqual(reservation["files"], 7 * len(copied_files) + 7 + 2 + 3 + 8)
        self.assertEqual((reservation["diagnostic_files"], reservation["grep_report_files"],
                          reservation["sed_temporary_files"], reservation["checker_spools"]), (7, 2, 3, 8))
        self.assertEqual(reservation["checker_spool_bytes"], 8 * state["files"]["scripts/check-native-integration.sh"]["bytes"])
        self.assertGreater(reservation["required_bytes"], 32 * 1024**2)
        self.A.require_resource_capacity(reservation, self.session().LIMITS)
        path = self.source / "skills/.extra-copy"
        path.write_bytes(b"x\n")
        (self.source / "skills/.empty-extra").mkdir()
        _, more = self.requirements()
        self.assertEqual(more["copied_files"] - reservation["copied_files"], 7)
        self.assertEqual(more["directories"] - reservation["directories"], 7)
        self.assertGreater(more["required_bytes"], reservation["required_bytes"])

    def test_128mib_is_fixed_to_original74_and_every_existing_limit_is_unchanged(self):
        session = self.session()
        self.assertEqual(session.LIMITS["scratch_bytes"], 128 * 1024**2)
        old_limits = dict(session.LIMITS, scratch_bytes=32 * 1024**2)
        # The eighteen contracts inherited by this increment. Later separately
        # reviewed profiles can have their own explicit resource contract.
        labels = ("audit-spec", "andon-class", "registry-wrapper", "marker-order", "commit-message",
                  "agents-bootstrap", "andon-escalation", "internal-skill-topology", "capability-ledger",
                  "issues-deferred", "no-terminal-cap", "background-chain", "plan-lifecycle", "plan-quality",
                  "authorization-binding", "read-only-plans", "routing", "audit-object-routing")
        profiles = {R.Q._FINITE_MODES[label] for label in labels}
        self.assertEqual(len(profiles), 18)
        for profile in profiles:
            cls = self.A.bind_session(R.Q.VerifierTaskSession, R.Q.WG, R.Q.ROOT, self.helper, profile=profile)
            self.assertEqual(cls.LIMITS, old_limits)
        _, reservation = self.requirements()
        with self.assertRaisesRegex(ValueError, "scratch capacity"):
            self.A.require_resource_capacity(reservation, old_limits)
        with self.assertRaises(TypeError):
            R.Q.create_finite_leaf_session(self.source, self.base / "knob", profile=PROFILE, scratch_bytes=256 * 1024**2)

    def test_scratch_file_and_stream_insufficiency_refuse_independently(self):
        _, reservation = self.requirements()
        limits = self.session().LIMITS
        for field, value, diagnostic in (("scratch_bytes", reservation["required_bytes"] - 1, "scratch capacity"),
                                        ("file_bytes", reservation["largest_file_bytes"] - 1, "file/stream capacity"),
                                        ("stream_bytes", reservation["max_stderr_bytes"] - 1, "file/stream capacity")):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, diagnostic):
                self.A.require_resource_capacity(reservation, dict(limits, **{field: value}))

    def test_dense_hygiene_output_refuses_before_runtime_or_dispatch(self):
        path = self.source / "fixtures/.dense-hygiene"
        path.write_bytes(b"password\n" * 80000)
        _, reservation = self.requirements()
        session = self.session()
        self.assertGreater(reservation["max_stderr_bytes"], session.LIMITS["stream_bytes"])
        with self.assertRaisesRegex(ValueError, "file/stream capacity"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(list(session.output.rglob("dispatch.json")), [])

    def test_source_file_and_complete_combined_byte_bounds_refuse(self):
        bounds = self.A.contract_for(PROFILE)["recursive"]["bounds"]
        path = self.source / "fixtures/.large"
        path.write_bytes(b"x" * (bounds["file_bytes"] + 1))
        with self.assertRaisesRegex(ValueError, "bound"):
            self.snapshot()
        path.unlink()
        for index in range(3):
            (self.source / "fixtures" / (".total-" + str(index))).write_bytes(b"x" * bounds["file_bytes"])
        with self.assertRaisesRegex(ValueError, "bound"):
            self.snapshot()


class LiveCases(Fixture, R.RecursiveLiveFixture, unittest.TestCase):
    SOURCE_ADMISSION_ONLY = False

    @classmethod
    def setUpClass(cls):
        if os.environ.get("R0035_NATIVE_INTEGRATION_LIVE") != "1":
            raise unittest.SkipTest("set R0035_NATIVE_INTEGRATION_LIVE=1 under a receiving namespace allocation")

    def test_original_success_consumes_actual_receipt_without_redispatch(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        self.assertEqual((first["exit"], first["complete"]), (0, True), stderr)
        self.assertEqual(stdout, b"check-native-integration: ok\nnative-integration.test: ok\n")
        self.assertEqual(stderr, b"")
        second, _, _ = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"]), ("EXECUTED", "REUSED"))
        for field in ("key", "receipt_digest", "producer"):
            self.assertEqual(first[field], second[field])
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_original_semantic_failure_retained_and_not_reused(self):
        (self.source / "fixtures/.outside-native-hygiene").write_bytes(b"password is abcdefghi\n")
        session = self.session()
        result, stdout, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"]), (1, True), stderr)
        self.assertEqual(stdout, b"")
        self.assertIn(b"fixtures/.outside-native-hygiene:1: realistic password value", stderr)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
