#!/usr/bin/env python3
"""Original node77 through the existing finite executor; no native authority."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import signal
import stat
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts/qualify-work-graph-finite-leaf.py"
spec = importlib.util.spec_from_file_location("topology_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = "CONTROLLED_TASK_INTERNAL_SKILL_TOPOLOGY_V1"
PROGRAM = "tests/internal-skill-topology.test.sh"
PACKAGE = "package/implementaudit-package.json"
NODE = "COMMAND:" + PROGRAM + ":0"


class CatalogCases(unittest.TestCase):
    def test_original_node77_is_selected_from_unchanged_117_node_registry(self):
        catalog, _ = shared.load("topology_catalog", HELPER)
        registry = (ROOT / "scripts/verify-package.sh").read_bytes()
        try:
            graph, scope, node = catalog.select_node(Q.WG, registry, P.ENVIRONMENT, profile=PROFILE)
        except ValueError as exc:
            self.fail("original node77 finite admission is absent: " + str(exc))
        self.assertEqual(len(graph["nodes"]), 117)
        self.assertEqual(graph["nodes"][77], node)
        self.assertEqual(node["id"], NODE)
        self.assertEqual(node["source"], "bash " + PROGRAM + "\n")
        self.assertEqual(scope["nodes"], [NODE])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        self.assertEqual(set(catalog.source_paths(PROFILE)), {"scripts/verify-package.sh", PROGRAM, PACKAGE})
        with self.assertRaisesRegex(ValueError, "registry"):
            catalog.select_node(Q.WG, registry + b"\n", P.ENVIRONMENT, profile=PROFILE)
        with self.assertRaisesRegex(ValueError, "unsupported"):
            catalog.contract_for(PROFILE.replace("V1", "V2"))


class TopologyFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        # Copy every actual root member through the depth observed by original
        # find. Names are never manufactured from the expected five skills.
        def copy_depth(source, target, depth):
            target.mkdir(parents=True, exist_ok=True)
            for path in sorted(source.iterdir()):
                mode = path.lstat().st_mode
                destination = target / path.name
                if stat.S_ISDIR(mode):
                    destination.mkdir()
                    if depth < 2:
                        copy_depth(path, destination, depth + 1)
                elif stat.S_ISREG(mode):
                    destination.write_bytes(path.read_bytes())
                    destination.chmod(stat.S_IMODE(mode))
                else:
                    raise AssertionError("fixture source has unsupported namespace type")
        copy_depth(ROOT / "skills", self.source / "skills", 1)

    def session(self, name="evidence", **options):
        return Q.create_finite_leaf_session(self.source, self.base / name, profile=PROFILE, **options)

    def skill(self):
        # Find a real ordinary matching member from the acquired source, not a
        # hardcoded expected name. All originals happen to have this pattern.
        return next(path for path in sorted((self.source / "skills").glob("*/SKILL.md"))
                    if path.is_file() and not path.is_symlink())

    def added_skill(self, name=".untracked-skill"):
        directory = self.source / "skills" / name
        directory.mkdir()
        (directory / "SKILL.md").write_bytes(b"not a completion or native grant\n")
        return directory


class AdmissionCases(TopologyFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        # Source admission is a real predicate test with no host execution or
        # observer prerequisite. Actual namespace tests remain separately gated.
        for target, name in ((Q.VerifierTaskSession, "_execute"), (P, "acquire_runtime")):
            guard = mock.patch.object(target, name, side_effect=AssertionError("unit admission cannot launch or acquire host runtime"))
            guard.start()
            self.addCleanup(guard.stop)

    def test_complete_depth_two_names_types_and_dot_members_are_acquired(self):
        self.added_skill()
        (self.source / "skills/.root-data").write_bytes(b"unread root content")
        (self.source / "skills/.empty").mkdir()
        (self.source / "skills/.empty/.nested-empty").mkdir()
        state, stamps, objects = self.snapshot()
        namespace = state["skill_namespace"]["projection"]
        entries = namespace["entries"]
        self.assertEqual(entries["skills/.root-data"], "FILE")
        self.assertEqual(entries["skills/.empty"], "DIRECTORY")
        self.assertEqual(entries["skills/.empty/.nested-empty"], "DIRECTORY")
        self.assertEqual(entries["skills/.untracked-skill/SKILL.md"], "FILE")
        self.assertIn("skill_namespace", stamps)
        self.assertEqual(set(state["files"]), {"scripts/verify-package.sh", PROGRAM, PACKAGE})
        self.assertNotIn(hashlib.sha256(b"unread root content").hexdigest(), objects)
        expected = {}
        for path in (self.source / "skills").iterdir():
            expected[path.relative_to(self.source).as_posix()] = "DIRECTORY" if path.is_dir() else "FILE"
            if path.is_dir():
                for child in path.iterdir():
                    expected[child.relative_to(self.source).as_posix()] = "DIRECTORY" if child.is_dir() else "FILE"
        self.assertEqual(entries, expected)

    def test_skill_contents_are_unread_but_metadata_drift_is_conservative(self):
        original = P.read_regular
        def guarded(path, *args, **kwargs):
            if Path(path).is_relative_to(self.source / "skills"):
                raise AssertionError("typed namespace must not read skill contents")
            return original(path, *args, **kwargs)
        with mock.patch.object(P, "read_regular", side_effect=guarded):
            first, first_stamps, _ = self.snapshot()
            self.skill().write_bytes(b"changed bytes remain unobserved by find\n")
            changed, changed_stamps, _ = self.snapshot()
        self.assertEqual(first["skill_namespace"]["projection"], changed["skill_namespace"]["projection"])
        self.assertNotEqual(first_stamps, changed_stamps)

    def test_added_missing_and_changed_ordinary_types_change_acquisition(self):
        first, _, _ = self.snapshot()
        path = self.skill()
        raw = path.read_bytes()
        path.unlink()
        missing, _, _ = self.snapshot()
        self.assertNotEqual(first, missing)
        self.assertNotIn(path.relative_to(self.source).as_posix(), missing["skill_namespace"]["projection"]["entries"])
        path.mkdir()
        changed, _, _ = self.snapshot()
        self.assertEqual(changed["skill_namespace"]["projection"]["entries"][path.relative_to(self.source).as_posix()], "DIRECTORY")
        self.assertNotEqual(missing, changed)
        path.rmdir()
        path.write_bytes(raw)
        self.added_skill()
        added, _, _ = self.snapshot()
        self.assertNotEqual(first, added)

    def test_nonmatching_alias_hardlink_fifo_and_unreadable_types_refuse(self):
        path = self.source / "skills/.not-a-skill"
        outside = self.base / "outside"
        outside.write_bytes(b"outside")
        for kind in ("symlink", "hardlink", "fifo", "mode"):
            if kind == "symlink": path.symlink_to(outside)
            elif kind == "hardlink": os.link(outside, path)
            elif kind == "fifo": os.mkfifo(path)
            else:
                path.write_bytes(b"unknown mode")
                path.chmod(0o600)
            with self.subTest(kind=kind), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.unlink()
        (self.source / "skills").rename(self.source / "held-skills")
        (self.source / "skills").symlink_to(self.source / "held-skills", target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()

    def test_namespace_addition_during_complete_acquisition_refuses(self):
        target = (self.source / "skills").stat()
        original = os.scandir
        count = 0
        def raced(fd):
            nonlocal count
            info = os.fstat(fd)
            if (info.st_dev, info.st_ino) == (target.st_dev, target.st_ino):
                count += 1
                if count == 2:
                    (self.source / "skills/.arrived-during-census").write_bytes(b"x")
            return original(fd)
        with mock.patch.object(os, "scandir", side_effect=raced), self.assertRaisesRegex(ValueError, "changed"):
            self.snapshot()

    def test_namespace_entry_capacity_refuses_before_dispatch(self):
        for index in range(513):
            (self.source / "skills" / ("empty-%04d" % index)).write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "bound"):
            self.snapshot()

    def test_unknown_program_and_missing_package_refuse_before_dispatch(self):
        program = self.source / PROGRAM
        raw = program.read_bytes()
        program.write_bytes(raw + b"\n")
        with self.assertRaisesRegex(ValueError, "executable"):
            self.snapshot()
        program.write_bytes(raw)
        (self.source / PACKAGE).unlink()
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()

    def test_missing_loader_libc_closure_refuses_without_any_host_read(self):
        def forbidden(*args, **kwargs):
            raise AssertionError("missing closure must refuse before tool reads")
        prefix = SimpleNamespace(read_regular=forbidden, RUNTIME_BOUNDS=P.RUNTIME_BOUNDS)
        runtime = dict(files={}, observations={})
        with self.assertRaisesRegex(ValueError, "closure"):
            self.A._capture_topology_runtime(prefix, runtime, {})

    def test_unknown_paste_bytes_refuse_without_host_execution(self):
        # A deliberate invalid tool capture exercises the production hash gate;
        # it grants no runtime/namespace or successful-execution evidence.
        prefix = SimpleNamespace(read_regular=lambda *args, **kwargs: (dict(mode=0o755), b"unknown executable"),
                                 RUNTIME_BOUNDS=P.RUNTIME_BOUNDS)
        names = ("/lib/x86_64-linux-gnu/libc.so.6", "/lib64/ld-linux-x86-64.so.2")
        runtime = dict(files={name:{} for name in names}, observations={name:{} for name in names})
        with self.assertRaisesRegex(ValueError, "paste"):
            self.A._capture_topology_runtime(prefix, runtime, {})
        self.assertNotIn("/usr/bin/paste", runtime["files"])


class LiveCases(TopologyFixture, shared.RetainedFixture, unittest.TestCase):
    LIVE_ENV = "R0035_TOPOLOGY_LIVE"
    EVIDENCE_ENV = "R0035_TOPOLOGY_EVIDENCE"
    OBJECTS_ENV = "R0035_TOPOLOGY_OBJECTS"
    TEST_SOURCE = "tests/work-graph-topology-cases.py"

    def actual(self, session):
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        self.assertEqual((directory / "exit-code.txt").read_bytes(), (str(result["exit"]) + "\n").encode())
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], NODE)
        self.assertEqual(receipt["scope"], PROFILE)
        self.assertEqual(result["group"]["nodes"], [NODE])
        self.assertEqual(len(result["group"]["omitted_nodes"]), 116)
        self.assertEqual(result["authority"], "NONE")
        self.assertEqual(result["canonical_acceptance"], "UNQUALIFIED")
        return result, stdout, stderr

    def positive(self, session):
        result, stdout, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"]), (0, True), stderr)
        self.assertEqual(stdout, b"internal-skill-topology.test: ok\n")
        self.assertEqual(stderr, b"")
        return result, stdout, stderr

    def negative(self, session, marker):
        result, _, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"]), (1, True), stderr)
        self.assertIn(marker, stderr)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_positive_reuse_complete_typed_image_then_data_refusal(self):
        session = self.session()
        first, _, _ = self.positive(session)
        second, _, _ = self.positive(session)
        self.assertEqual((first["disposition"], second["disposition"]), ("EXECUTED", "REUSED"))
        self.assertEqual(first["receipt_digest"], second["receipt_digest"])
        self.assertEqual(session.dispatch_count, 1)
        image = json.loads((Path(first["evidence_directory"]) / "image.json").read_bytes())
        namespace = image["directory_membership"]
        files = {row["path"]:row for row in image["files"]}
        for name, kind in namespace["entries"].items():
            if kind == "DIRECTORY":
                self.assertIn("/work/" + name, image["directories"])
            else:
                self.assertEqual(files["/work/" + name]["bytes"], 0)
        for name, expected in {
                "/usr/bin/paste": "82077c51bf5add756668fef163556942f01083100d378e3bf860466a83fd6dcb",
                "/lib/x86_64-linux-gnu/libc.so.6": "511f825ee075610ac9c0f7f91e2c13de2000d0f7b859f6461137e809a0a009d0",
                "/lib64/ld-linux-x86-64.so.2": "6222a16be7f2d458d6870efe6e715fc0c8d45766fb79cf7dcc3125538d703e28"}.items():
            self.assertEqual(files[name]["sha256"], expected)
            self.assertEqual(files[name]["mode"], 0o555)
        path = self.source / PACKAGE
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_original_dot_population_failure_is_retained_and_not_reused(self):
        self.added_skill()
        self.negative(self.session(), b"source population mismatch")

    def test_original_omitted_skill_failure_is_retained_and_not_reused(self):
        self.skill().unlink()
        self.negative(self.session(), b"source population mismatch")

    def test_original_package_contract_failure_is_retained_and_not_reused(self):
        path = self.source / PACKAGE
        value = json.loads(path.read_bytes())
        value["public_governor"] = "unadmitted-governor"
        path.write_text(json.dumps(value) + "\n")
        self.negative(self.session(), b"AssertionError: unadmitted-governor")

    def test_added_namespace_refuses_prior_result_without_redispatch(self):
        session = self.session()
        self.positive(session)
        self.added_skill()
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_omitted_namespace_refuses_prior_result_without_redispatch(self):
        session = self.session()
        self.positive(session)
        self.skill().unlink()
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_changed_type_refuses_prior_result_without_redispatch(self):
        session = self.session()
        self.positive(session)
        path = self.skill()
        path.unlink()
        path.mkdir()
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_foreign_process_and_tampered_result_refuse_without_redispatch(self):
        session = self.session()
        result, stdout, _ = self.positive(session)
        read, write = os.pipe()
        child = os.fork()
        if child == 0:
            os.close(read)
            try:
                session.run()
                data = b"WRONGLY_ACCEPTED"
            except (ValueError, OSError) as exc:
                data = str(exc).encode()
            os.write(write, data[:4096])
            os.close(write)
            os._exit(0)
        os.close(write)
        try:
            ready, _, _ = select.select([read], [], [], 5)
            self.assertTrue(ready, "foreign process refusal did not return")
            message = os.read(read, 4096)
            _, status = os.waitpid(child, 0)
            child = None
            self.assertEqual(os.waitstatus_to_exitcode(status), 0)
            self.assertIn(b"producer process changed", message)
            (self.base / "foreign-process-refusal.txt").write_bytes(message + b"\n")
        finally:
            os.close(read)
            if child is not None:
                os.kill(child, signal.SIGKILL)
                os.waitpid(child, 0)
        path = Path(result["evidence_directory"]) / "stdout.log"
        path.chmod(0o600)
        path.write_bytes(stdout + b"altered result\n")
        path.chmod(0o400)
        with self.assertRaisesRegex(ValueError, "evidence refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
