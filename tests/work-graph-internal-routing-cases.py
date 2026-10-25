#!/usr/bin/env python3
"""Original78 finite source controls; actual original cases require allocation."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
PROFILE = "CONTROLLED_TASK_INTERNAL_SKILL_ROUTING_V1"
NODE = "COMMAND:tests/internal-skill-routing.test.sh:0"


def load(name):
    path = ROOT / name
    spec = importlib.util.spec_from_file_location("internal78_" + path.stem.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


shared = load("tests/work-graph-audit-spec-cases.py")
Q, P = shared.Q, shared.P


class CatalogCases(unittest.TestCase):
    def test_original78_has_an_explicit_finite_profile(self):
        helper = load("scripts/qualify-work-graph-finite-leaf.py")
        self.assertIn(PROFILE, helper._CONTRACTS,
                      "original78 lacks an explicit complete finite resolver/copy profile")
        contract = helper.contract_for(PROFILE)
        self.assertEqual((contract["label"], contract["index"], contract["program"]),
                         ("internal-skill-routing", 78, "tests/internal-skill-routing.test.sh"))
        graph, scope, node = helper.select_node(Q.WG, H.original("scripts/verify-package.sh"), P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][78]))
        self.assertEqual((node["id"], node["source"]), (NODE, "bash tests/internal-skill-routing.test.sh\n"))
        self.assertEqual((scope["nodes"], len(scope["omitted_nodes"])), ([NODE], 116))
        self.assertEqual(Q._FINITE_MODES["internal-skill-routing"], PROFILE)
        self.assertEqual(len(helper.source_paths(PROFILE)), 10)
        self.assertEqual(len(contract["data"]), 7)
        self.assertEqual(contract["recursive"]["roots"], ("skills", "plugins/implementaudit/skills/implementaudit"))
        for name, pin in contract["programs"].items():
            self.assertEqual(hashlib.sha256(H.input_bytes(name)).hexdigest(), pin)
        self.assertNotIn("complete_git", contract)


class Fixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        shutil.copytree(ROOT / "skills", self.source / "skills", dirs_exist_ok=True)
        for directory in (self.source, *(p for p in self.source.rglob("*") if p.is_dir())):
            directory.chmod(0o755)
        self.restore_historical_inputs()

    def write(self, name, raw, mode=0o644):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        for directory in (path.parent, *path.parent.parents):
            if directory == self.source or self.source in directory.parents:
                directory.chmod(0o755)
        path.write_bytes(raw)
        path.chmod(mode)
        return path


class AdmissionCases(Fixture, unittest.TestCase):
    def test_complete_skills_and_unknown_copy_members_keep_bytes_modes_and_empty_directories(self):
        extra = self.write("skills/implementaudit/extra/nested.bin", b"\x00\xff actual copied data", 0o755)
        empty = self.source / "skills/implementaudit/extra/empty"
        empty.mkdir(mode=0o755)
        state, _, objects = self.snapshot()
        expected = {p.relative_to(self.source).as_posix(): p.read_bytes() for p in (self.source / "skills").rglob("*") if p.is_file()}
        self.assertEqual({name: objects[row["sha256"]] for name, row in state["files"].items()
                          if name.startswith("skills/")}, expected)
        self.assertEqual(state["files"][extra.relative_to(self.source).as_posix()]["mode"], 0o755)
        self.assertEqual(state["directories"][empty.relative_to(self.source).as_posix()], 0o755)
        bound = state["recursive_inputs"]["resources"]
        self.assertIn(extra.relative_to(self.source).as_posix(), bound["copied_paths"])
        self.assertEqual((bound["original_git_commands"], bound["original_child_routes"]), ([], []))

    def test_optional_peer_and_internal_procedures_preserve_actual_absence_file_and_directory(self):
        peer = self.A.INTERNAL_ROUTING_PEER_ROOT + "/SKILL.md"
        internal = "skills/implementaudit/internal-procedures"
        before, _, _ = self.snapshot()
        self.assertEqual(before["recursive_inputs"]["resources"]["peer_kind"], "MISSING")
        self.assertEqual(before["recursive_inputs"]["projection"]["probes"][self.A.INTERNAL_ROUTING_PEER_ROOT]["kind"], "MISSING")
        file = self.write(peer, b"present physical peer is input, not an acceptance decision")
        self.write(internal, b"an ordinary file has a different resolver meaning from absence")
        present, _, objects = self.snapshot()
        self.assertEqual(present["recursive_inputs"]["resources"]["peer_kind"], "FILE")
        self.assertEqual(present["recursive_inputs"]["resources"]["source_internal_procedures_kind"], "FILE")
        self.assertEqual(objects[present["files"][peer]["sha256"]], file.read_bytes())
        for name in (peer, internal):
            path = self.source / name
            path.unlink()
            path.mkdir(mode=0o755)
        self.write(peer + "/retained.bin", b"complete optional subtree")
        directories, _, _ = self.snapshot()
        self.assertEqual(directories["recursive_inputs"]["resources"]["peer_kind"], "DIRECTORY")
        self.assertEqual(directories["recursive_inputs"]["resources"]["source_internal_procedures_kind"], "DIRECTORY")
        self.assertIn(peer + "/retained.bin", directories["files"])
        self.assertIn(internal, directories["directories"])

    def test_original_program_registry_and_required_positive_operands_refuse_drift(self):
        for name in (*self.A.contract_for(PROFILE)["programs"], self.A.REGISTRY):
            path = self.source / name
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            try:
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "executable|registry"):
                    self.snapshot()
            finally:
                path.write_bytes(raw)
        path = self.source / "skills/audit-state/SKILL.md"
        path.unlink()
        session = self.session()
        with self.assertRaises((ValueError, OSError)):
            session._acquire()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))

    def test_unknown_recursive_aliases_and_nonpreserved_modes_refuse(self):
        path = self.write("skills/implementaudit/unknown", b"ordinary")
        outside = self.base / "outside"
        outside.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        path.unlink()
        os.link(outside, path)
        with self.assertRaisesRegex(ValueError, "single-link"):
            self.snapshot()
        path.unlink()
        path.write_bytes(b"ordinary")
        path.chmod(0o600)
        with self.assertRaisesRegex(ValueError, "mode"):
            self.snapshot()

    def test_new_peer_after_observed_absence_refuses_closing_currentness(self):
        read = P.snapshot_tree
        calls = []
        def add_after_absence(*args, **kwargs):
            result = read(*args, **kwargs)
            calls.append(1)
            if len(calls) == 2:
                self.write(self.A.INTERNAL_ROUTING_PEER_ROOT + "/SKILL.md", b"new peer")
            return result
        with mock.patch.object(P, "snapshot_tree", side_effect=add_after_absence):
            with self.assertRaisesRegex(ValueError, "presence|ancestor"):
                self.snapshot()
        self.assertEqual(len(calls), 2)

    def test_extra_canonical_child_bytes_are_admitted_for_original_semantic_refusal(self):
        before, _, _ = self.snapshot()
        name = "skills/extra-owned-control/SKILL.md"
        path = self.write(name, b"# extra ordinary canonical population member\n")
        after, _, objects = self.snapshot()
        self.assertNotEqual(before, after)
        self.assertEqual(objects[after["files"][name]["sha256"]], path.read_bytes())
        self.assertNotIn(name, after["recursive_inputs"]["resources"]["copied_paths"])
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session._acquire()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))
        self.assertFalse((session.output / "objects").exists())

    def test_private_copy_spool_and_diagnostic_lifetimes_preserve_all_default_limits(self):
        state, _, _ = self.snapshot()
        bound = state["recursive_inputs"]["resources"]
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((bound["resolver_invocations"], bound["inline_python_blocks"], bound["standalone_copies"]), (5, 4, 4))
        self.assertEqual((reservation["standalone_source_files"], reservation["generated_private_files"],
                          reservation["wrapper_spools"]), (6, 2, 4))
        self.assertEqual(reservation["files"], bound["copied_source_files"] + 24 + 2 + 4)
        self.assertEqual(reservation["directories"], bound["copied_source_directories"] + 25)
        self.assertGreaterEqual(reservation["content_bytes"], bound["copied_source_bytes"] +
            4 * sum(state["files"][name]["bytes"] for name in bound["standalone_paths"]))
        session = self.session()
        parent = P.bind_session(Q.VerifierTaskSession, Q.WG, Q.ROOT, (ROOT / "scripts/qualify-work-graph-prefix.py").read_bytes())
        self.assertEqual(session.LIMITS, parent.LIMITS)
        self.assertEqual(session.LIMITS["scratch_bytes"], 32 * 1024**2)
        self.A.require_resource_capacity(reservation, session.LIMITS)
        for override in ({"scratch_bytes": reservation["required_bytes"] - 1},
                         {"file_bytes": reservation["largest_file_bytes"] - 1},
                         {"stream_bytes": reservation["max_stderr_bytes"] - 1},
                         {"address_bytes": reservation["original_data_memory_reservation"] * 4 // 3 - 1}):
            with self.subTest(override=override), self.assertRaisesRegex(ValueError, "capacity"):
                self.A.require_resource_capacity(reservation, dict(session.LIMITS, **override))
        files = {"/work/" + self.A.INTERNAL_ROUTING_RESOLVER: (b"captured bytes", 0o644),
                 "/work/skills/implementaudit/exec": (b"other copied bytes", 0o755)}
        image, policy = self.A.finite_image_permissions(files, state, profile=PROFILE)
        self.assertEqual(image, files)
        self.assertEqual(policy, dict(source_modes="PRESERVE_READ_ONLY_MOUNT"))

    def test_complete_copied_population_above32mib_refuses_before_runtime(self):
        for number in range(250):
            self.write("skills/implementaudit/many/f%03d" % number, b"x")
        state, _, _ = self.snapshot()
        bound = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertGreater(bound["required_bytes"], 32 * 1024**2)
        session = self.session()
        with self.assertRaisesRegex(ValueError, "scratch capacity"):
            session._acquire()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))
        self.assertEqual(list(session.output.rglob("dispatch.json")), [])


class LiveCases(unittest.TestCase):
    """Two actual public CLI controls; never enabled by the ordinary bank."""
    @classmethod
    def setUpClass(cls):
        if os.environ.get("R0035_INTERNAL_ROUTING_LIVE") != "1":
            raise unittest.SkipTest("set R0035_INTERNAL_ROUTING_LIVE=1 only under a receiving namespace allocation")
        if not os.environ.get("R0035_INTERNAL_ROUTING_EVIDENCE"):
            raise RuntimeError("actual original78 controls require a fresh evidence destination")

    def setUp(self):
        self.base = Path(os.environ["R0035_INTERNAL_ROUTING_EVIDENCE"]) / self._testMethodName
        self.base.mkdir(parents=True, exist_ok=False)
        self.source = self.base / "source"
        self.A = load("scripts/qualify-work-graph-finite-leaf.py")
        objects = {}
        state, _ = self.A.snapshot_source(P, ROOT, objects, profile=PROFILE)
        for name, mode in sorted(state["directories"].items(), key=lambda row: len(Path(row[0]).parts)):
            path = self.source / name
            path.mkdir(parents=True, exist_ok=True)
            path.chmod(mode)
        for name, row in state["files"].items():
            path = self.source / name
            path.write_bytes(objects[row["sha256"]])
            path.chmod(row["mode"])

    def invoke(self):
        before, before_stamps = self.A.snapshot_source(P, self.source, {}, profile=PROFILE)
        (self.base / "source-before.json").write_bytes(P.encode(dict(state=before, stamps=before_stamps)))
        environment = dict(PATH="/usr/bin:/bin", LANG="C", LC_ALL="C", TZ="UTC",
            PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1", PYTHONSAFEPATH="1", PYTHONHASHSEED="0")
        argv = ["/usr/bin/python3", "-B", str(ROOT / "scripts/qualify-work-graph-verifier.py"),
                "internal-skill-routing", str(self.source), str(self.base / "session")]
        request = b'{"operation":"run"}\n' * 2
        started = time.monotonic()
        process = subprocess.Popen(argv, cwd=ROOT, env=environment, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        timed_out = False
        try:
            stdout, stderr = process.communicate(request, timeout=240)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        (self.base / "cli.stdout").write_bytes(stdout)
        (self.base / "cli.stderr").write_bytes(stderr)
        (self.base / "cli.json").write_text(json.dumps(dict(argv=argv, environment=environment,
            pid=process.pid, exit=process.returncode, timed_out=timed_out, elapsed=time.monotonic() - started,
            request_hex=request.hex(), cli_reaped=True, authority="NONE"), sort_keys=True) + "\n")
        after, after_stamps = self.A.snapshot_source(P, self.source, {}, profile=PROFILE)
        (self.base / "source-after.json").write_bytes(P.encode(dict(state=after, stamps=after_stamps)))
        self.assertFalse(timed_out, "retained timeout is not original success")
        self.assertEqual((before, before_stamps), (after, after_stamps))
        rows = [json.loads(line) for line in stdout.splitlines()]
        self.assertTrue(rows, stderr)
        for row in rows:
            self.assertEqual((row["group"]["nodes"], len(row["group"]["omitted_nodes"])), ([NODE], 116))
            self.assertEqual((row["canonical_acceptance"], row["authority"]), ("UNQUALIFIED", "NONE"))
            directory = Path(row["evidence_directory"])
            receipt = json.loads((directory / "receipt.json").read_bytes())
            self.assertEqual((receipt["node"], receipt["scope"]), (NODE, PROFILE))
            self.assertEqual((directory / "exit-code.txt").read_bytes(), (str(row["exit"]) + "\n").encode())
        return process.returncode, rows, stderr

    def test_actual_original_positive_and_reuse(self):
        code, rows, stderr = self.invoke()
        self.assertEqual((code, stderr, len(rows)), (0, b"", 2))
        first, second = rows
        directory = Path(first["evidence_directory"])
        self.assertEqual((first["exit"], first["complete"], first["disposition"], second["disposition"]),
                         (0, True, "EXECUTED", "REUSED"))
        expected = (b"internal-skill-routing.test: ok\n"
                    b"internal-skill-routing.test: resolver controls ok\n"
                    b"internal-skill-routing.test: routing observability controls ok (10/10)\n"
                    b"internal-skill-routing.test: secondary abnormality controls ok (4/4)\n")
        self.assertEqual((directory / "stdout.log").read_bytes(), expected)
        self.assertEqual((directory / "stderr.log").read_bytes(), b"")
        self.assertEqual((first["key"], first["receipt_digest"]), (second["key"], second["receipt_digest"]))
        self.assertEqual(len(list((self.base / "session").rglob("dispatch.json"))), 1)

    def test_actual_extra_canonical_child_failure_is_retained_without_reuse(self):
        path = self.source / "skills/extra-owned-control/SKILL.md"
        path.parent.mkdir(mode=0o755)
        path.write_bytes(b"# extra ordinary canonical population member\n")
        path.chmod(0o644)
        code, rows, stderr = self.invoke()
        self.assertEqual((code, len(rows)), (2, 1))
        result = rows[0]
        self.assertEqual((result["exit"], result["complete"], result["disposition"]), (1, True, "EXECUTED"))
        directory = Path(result["evidence_directory"])
        self.assertEqual((directory / "stdout.log").read_bytes(), b"internal-skill-routing.test: ok\n")
        self.assertIn(b"canonical child population is not exact", (directory / "stderr.log").read_bytes())
        self.assertIn(b"extra-owned-control", (directory / "stderr.log").read_bytes())
        self.assertIn(b"failed or interrupted", stderr)
        self.assertEqual(len(list((self.base / "session").rglob("dispatch.json"))), 1)


if __name__ == "__main__":
    unittest.main()
