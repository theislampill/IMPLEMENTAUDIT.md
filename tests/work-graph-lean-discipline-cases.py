#!/usr/bin/env python3
"""Original24 finite source controls; original execution is separately gated."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
PROFILE = "CONTROLLED_TASK_LEAN_DISCIPLINE_V1"
PROGRAM = "tests/lean-discipline.test.sh"
NODE = "COMMAND:" + PROGRAM + ":0"


def load(name):
    path = ROOT / name
    spec = importlib.util.spec_from_file_location("original24_" + path.stem.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


class CatalogCases(unittest.TestCase):
    def test_original24_has_an_explicit_finite_profile(self):
        helper = load("scripts/qualify-work-graph-finite-leaf.py")
        self.assertTrue(PROFILE in helper._CONTRACTS,
                        "original24 has no explicit complete finite source profile")
        contract = helper.contract_for(PROFILE)
        self.assertEqual((contract["label"], contract["index"], contract["program"]),
                         ("lean-discipline", 24, "tests/lean-discipline.test.sh"))
        qualifier = load("scripts/qualify-work-graph-verifier.py")
        prefix = load("scripts/qualify-work-graph-prefix.py")
        graph, scope, node = helper.select_node(qualifier.WG,
            (ROOT / helper.REGISTRY).read_bytes(), prefix.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][24]))
        self.assertEqual((node["id"], node["source"]), (NODE, "bash " + PROGRAM + "\n"))
        self.assertEqual((scope["nodes"], len(scope["omitted_nodes"])), ([NODE], 116))
        self.assertEqual(qualifier._FINITE_MODES["lean-discipline"], PROFILE)
        self.assertEqual(len(helper.source_paths(PROFILE)), 32)
        self.assertEqual(set(contract["programs"]), {PROGRAM, "scripts/check-lean-discipline.sh",
            "fixtures/semantic-preservation/test-cases.sh", "fixtures/semantic-preservation/evaluate.py"})
        for name, pin in contract["programs"].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), pin)
        wrapper = (ROOT / PROGRAM).read_text()
        self.assertEqual(wrapper.count("T=$(make_temp)"), 14)
        self.assertEqual(wrapper.count("scripts/check-lean-discipline.sh\" >/dev/null") +
                         wrapper.count("bash scripts/check-lean-discipline.sh >/dev/null"), 15)
        self.assertIn('cp -r . "$t/" 2>/dev/null || true', wrapper)
        self.assertEqual(contract["whole_copy"], dict(file_bytes=16 * 1024**2,
            total_bytes=192 * 1024**2, entries=4096, depth=40, path_bytes=2048))
        self.assertEqual(contract["source_modes"], "COPY_0666_UMASK_022_READ_ONLY_ROOT")
        self.assertNotIn("complete_git", contract)  # The selected original executes no Git command.


class SourceFixture:
    def setUp(self):
        self.A = load("scripts/qualify-work-graph-finite-leaf.py")
        self.P = load("scripts/qualify-work-graph-prefix.py")
        self.Q = load("scripts/qualify-work-graph-verifier.py")
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        for name in self.A.source_paths(PROFILE):
            self.write(name, (ROOT / name).read_bytes(), (ROOT / name).stat().st_mode & 0o777)

    def write(self, name, raw, mode=0o644):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        for directory in (path.parent, *path.parent.parents):
            if directory == self.source or self.source in directory.parents:
                directory.chmod(0o755)
        path.write_bytes(raw)
        path.chmod(mode)
        return path

    def snapshot(self):
        objects = {}
        state, stamps = self.A.snapshot_source(self.P, self.source, objects, profile=PROFILE)
        return state, stamps, objects

    def session(self):
        raw = (ROOT / "scripts/qualify-work-graph-finite-leaf.py").read_bytes()
        cls = self.A.bind_session(self.Q.VerifierTaskSession, self.Q.WG, ROOT, raw, profile=PROFILE)
        return cls(self.source, self.base / "evidence")

    def assert_refuses_before_runtime(self, session, expected):
        def forbidden(*_args, **_kwargs):
            raise AssertionError("source-only fixture reached runtime acquisition")
        scope = session._acquire.__func__.__globals__
        with mock.patch.object(session, "_observer", return_value=mock.sentinel.source_only), \
                mock.patch.dict(scope, {"finite_runtime": forbidden}), \
                mock.patch.object(self.Q.subprocess, "Popen", side_effect=AssertionError("unexpected launch")):
            with self.assertRaisesRegex(ValueError, expected):
                session._acquire()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))
        self.assertEqual(list(session.output.rglob("dispatch.json")), [])


class AdmissionCases(SourceFixture, unittest.TestCase):
    def test_complete_copy_keeps_unknown_bytes_git_storage_registry_and_empty_directories(self):
        extras = {"unlisted/deep/file.bin": (b"\x00\xff observed bytes", 0o644),
                  ".git/objects/opaque-copy-data": (b"actual fixture bytes, no Git result", 0o444),
                  "extra-executable": (b"unused executable bytes", 0o755)}
        for name, (raw, mode) in extras.items():
            self.write(name, raw, mode)
        (self.source / "empty").mkdir(mode=0o755)
        state, stamps, objects = self.snapshot()
        self.assertEqual(set(state["files"]), {*self.A.source_paths(PROFILE), *extras})
        for name, record in state["files"].items():
            self.assertEqual(objects[record["sha256"]], (self.source / name).read_bytes())
        self.assertEqual(state["directories"]["empty"], 0o755)
        self.assertIn(".git/objects/opaque-copy-data", state["whole_copy_inputs"]["currentness"])
        self.assertEqual(set(self.A.image_subject(state, profile=PROFILE)), set(state["files"]))
        self.assertIn(self.A.REGISTRY, self.A.image_subject(state, profile=PROFILE))
        self.assertEqual(stamps["whole_copy_inputs"]["selectors"]["original_git_commands"], [])

    def test_fixed_worktree_selectors_bind_all_package_members_and_missing_reference_population(self):
        state, _, _ = self.snapshot()
        selected = state["whole_copy_inputs"]["selectors"]
        self.assertEqual((selected["reference_count"], selected["semantic_cases"], selected["semantic_profiles"]), (41, 21, 12))
        self.assertEqual({row["revision"] for row in selected["references"]}, {"WORKTREE"})
        self.assertEqual(len(selected["package_required_skills"]), 5)
        self.assertEqual(len(selected["package_shared_roots"]), 3)
        self.assertEqual(len(selected["repo_only_instrumentation"]), 3)
        self.assertTrue(any(row["kind"] == "MISSING" for row in selected["references"]))
        shared_name = "skills/implementaudit/references/new-ordinary-member.bin"
        self.write(shared_name, b"package enumeration retains the actual member")
        absent_name = "references/definitely-not-shipped.md"
        self.write(absent_name, b"now physically present; semantic disposition belongs to the original")
        changed, _, _ = self.snapshot()
        selected2 = changed["whole_copy_inputs"]["selectors"]
        self.assertEqual(selected2["package_member_mapping"][shared_name], "references/new-ordinary-member.bin")
        matches = [row for row in selected2["references"] if row["path"] == absent_name]
        self.assertTrue(matches)
        self.assertTrue(all(row["kind"] == "FILE" and row["acquired"] == changed["files"][absent_name] for row in matches))
        self.assertIn(absent_name, changed["whole_copy_inputs"]["resources"]["source_read_paths"])
        for name in (self.A.LEAN_DISCIPLINE_CASES, self.A.LEAN_DISCIPLINE_BUILDER):
            path = self.source / name
            original = path.read_bytes()
            modified = original.replace(b"WORKTREE", b"UNOWNED_REVISION", 1) if name.endswith("cases.json") else original + b"\n"
            path.write_bytes(modified)
            try:
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "pinned branch input"):
                    self.snapshot()
            finally:
                path.write_bytes(original)

    def test_original_program_registry_and_copied_runner_changes_refuse_before_runtime(self):
        session = self.session()
        contract = self.A.contract_for(PROFILE)
        for name in (*contract["programs"], self.A.REGISTRY, self.A.RUNNER):
            path = self.source / name
            original = path.read_bytes()
            path.write_bytes(original + b"\n")
            try:
                with self.subTest(name=name):
                    self.assert_refuses_before_runtime(session, "executable|registry|pinned")
            finally:
                path.write_bytes(original)

    def test_unknown_copy_members_refuse_aliases_noncopy_modes_and_oversized_files(self):
        path = self.write("unlisted/member", b"unknown copied member")
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
        with self.assertRaisesRegex(ValueError, "supported source modes"):
            self.snapshot()
        path.chmod(0o644)
        path.parent.chmod(0o700)
        with self.assertRaisesRegex(ValueError, "0755 directories"):
            self.snapshot()
        path.parent.chmod(0o755)
        with path.open("wb") as stream:
            stream.truncate(16 * 1024**2 + 1)
        with self.assertRaisesRegex(ValueError, "byte/entry bound"):
            self.snapshot()

    def test_complete_copy_reacquires_opaque_member_identity_after_capture(self):
        path = self.write(".git/objects/ordinary-opaque", b"same bytes")
        original = self.P.snapshot_tree
        calls = []
        def replace_after_read(*args, **kwargs):
            result = original(*args, **kwargs)
            calls.append(1)
            if len(calls) == 1:
                replacement = path.with_name("replacement")
                replacement.write_bytes(path.read_bytes())
                replacement.chmod(0o644)
                replacement.replace(path)
            return result
        with mock.patch.object(self.P, "snapshot_tree", side_effect=replace_after_read):
            with self.assertRaisesRegex(ValueError, "changed during acquisition"):
                self.snapshot()
        self.assertEqual(len(calls), 2)

    def test_dynamic_lean_negative_is_admitted_as_actual_bytes_without_semantic_answer(self):
        state, _, _ = self.snapshot()
        name = "skills/implementaudit/references/unreviewed-lean-control.md"
        path = self.write(name, b"ordinary added file selected by the original dynamic scan\n")
        changed, _, objects = self.snapshot()
        self.assertNotEqual(state, changed)
        self.assertEqual(objects[changed["files"][name]["sha256"]], path.read_bytes())
        self.assertIn(name, changed["whole_copy_inputs"]["selectors"]["package_member_mapping"])
        session = self.session()
        def forbidden(*_args, **_kwargs):
            raise AssertionError("source-only fixture reached runtime acquisition")
        scope = session._acquire.__func__.__globals__
        with mock.patch.object(session, "_observer", return_value=mock.sentinel.source_only), \
                mock.patch.dict(scope, {"finite_runtime": forbidden}):
            with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
                session._acquire()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))
        self.assertFalse((session.output / "objects").exists())

    def test_copy_growth_and_private_lifetimes_are_bounded_from_the_actual_population(self):
        lean = self.A.LEAN_DISCIPLINE_READS[0]
        original = (self.source / lean).read_bytes()
        added = b"| Jidoka | x\n| Andon | y\n| Poka-yoke | z\n| Standard Work | w\nGraphify terrain leverage\nActiveGraph custody events\n" * 71
        self.write(lean, original + added)
        state, _, _ = self.snapshot()
        resources = state["whole_copy_inputs"]["resources"]
        raw = (self.source / lean).read_bytes()
        text = raw.decode()
        jidoka = re.sub(r"\| Jidoka \|[^\n]+", "| Jidoka | Generic error label for failures. | skills/implementaudit/templates/PROTOCOL.md | check-planner-stages.sh |", text)
        both = re.sub(r"\| Andon \|[^\n]+", "| Andon | Generic error label for failures. | skills/implementaudit/SKILL.md | check-planner-stages.sh |", jidoka)
        self.assertLessEqual(len(both.encode()), len(raw) + resources["copied_file_growth"][lean])
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((reservation["original_copy_incarnations"], reservation["simultaneous_copies"],
            reservation["original_checker_calls"], reservation["semantic_evaluator_calls"],
            reservation["semantic_json_attack_files"], reservation["possible_simultaneous_spools"]), (14, 1, 15, 3, 2, 1))
        self.assertEqual(reservation["files"], len(state["files"]) + 3)
        self.assertEqual(reservation["copied_source_bytes"], sum(value["bytes"] for value in state["files"].values()))
        self.assertGreaterEqual(reservation["content_bytes"], reservation["copied_source_bytes"] +
                                2 * reservation["private_json_file_bound"] + reservation["spool_file_bound"])
        session = self.session()
        self.A.require_resource_capacity(reservation, session.LIMITS)
        for override in ({"scratch_bytes": reservation["required_bytes"] - 1},
                         {"file_bytes": reservation["largest_file_bytes"] - 1},
                         {"stream_bytes": reservation["max_stderr_bytes"] - 1},
                         {"address_bytes": reservation["original_data_memory_reservation"] * 4 // 3 - 1}):
            with self.subTest(override=override), self.assertRaisesRegex(ValueError, "capacity"):
                self.A.require_resource_capacity(reservation, dict(session.LIMITS, **override))

    def test_fixed512mib_refuses_a_complete_admissible_copy_before_runtime(self):
        # Two sparse ordinary16MiB data files plus3900 one-byte files fit the
        # source entry/byte limits but exceed the fixed scratch allocation.
        for index in range(3900):
            self.write("many/f%04d" % index, b"x")
        for index in range(2):
            path = self.write("large-%d" % index, b"")
            with path.open("wb") as stream:
                stream.truncate(16 * 1024**2)
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertGreater(reservation["required_bytes"], 512 * 1024**2)
        session = self.session()
        self.assertEqual(session.LIMITS["scratch_bytes"], 512 * 1024**2)
        self.assertEqual(session.LIMITS["file_bytes"], 16 * 1024**2)
        self.assert_refuses_before_runtime(session, "scratch capacity")

    def test_reviewed_copy_projection_retains_all_bytes_and_copied_runner_mode(self):
        state, _, objects = self.snapshot()
        files = {"/work/" + name: (objects[row["sha256"]], row["mode"]) for name, row in state["files"].items()}
        files["/work/readonly"] = (b"readonly storage", 0o444)
        files["/usr/bin/cp"] = (b"constructed runtime input, not executed", 0o555)
        files["/usr/lib/data"] = (b"constructed runtime data", 0o444)
        image = self.A.copy_readonly_image(files)
        self.assertEqual(set(image), set(files))
        for name, (raw, mode) in files.items():
            self.assertEqual(image[name][0], raw)
            if name.startswith("/work/"):
                self.assertEqual(image[name][1] & ~0o022, mode)
        runner = "/work/" + self.A.RUNNER
        self.assertEqual((state["files"][self.A.RUNNER]["mode"], image[runner][1], image[runner][1] & ~0o022),
                         (0o644, 0o666, 0o644))
        self.assertEqual(image[runner][0], (ROOT / self.A.RUNNER).read_bytes())
        self.assertEqual((image["/usr/bin/cp"][1], image["/usr/lib/data"][1]), (0o555, 0o600))
        self.assertIn("/work/" + self.A.REGISTRY, image)


class LiveCases(unittest.TestCase):
    """Two separately allocated actual public CLI controls; disabled by default."""
    @classmethod
    def setUpClass(cls):
        if os.environ.get("R0035_LEAN_DISCIPLINE_LIVE") != "1":
            raise unittest.SkipTest("set R0035_LEAN_DISCIPLINE_LIVE=1 only under a receiving namespace allocation")
        if not os.environ.get("R0035_LEAN_DISCIPLINE_EVIDENCE"):
            raise RuntimeError("actual original24 controls require a fresh durable-evidence destination")

    def setUp(self):
        self.base = Path(os.environ["R0035_LEAN_DISCIPLINE_EVIDENCE"]) / self._testMethodName
        self.base.mkdir(parents=True, exist_ok=False)
        self.source = self.base / "source"
        shutil.copytree(ROOT, self.source, symlinks=True)
        self.A = load("scripts/qualify-work-graph-finite-leaf.py")
        self.P = load("scripts/qualify-work-graph-prefix.py")

    def invoke(self):
        before, before_stamps = self.A.snapshot_source(self.P, self.source, {}, profile=PROFILE)
        (self.base / "source-before.json").write_bytes(self.P.encode(dict(state=before, stamps=before_stamps)))
        environment = dict(PATH="/usr/bin:/bin", LANG="C", LC_ALL="C", TZ="UTC",
            PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1", PYTHONSAFEPATH="1", PYTHONHASHSEED="0")
        argv = ["/usr/bin/python3", "-B", str(ROOT / "scripts/qualify-work-graph-verifier.py"),
                "lean-discipline", str(self.source), str(self.base / "session")]
        request = b'{"operation":"run"}\n' * 2
        started = time.monotonic()
        process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd=ROOT, env=environment, start_new_session=True)
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
            request_hex=request.hex(), pid=process.pid, exit=process.returncode, timed_out=timed_out,
            elapsed=time.monotonic() - started, cli_reaped=True, authority="NONE"), sort_keys=True) + "\n")
        after, after_stamps = self.A.snapshot_source(self.P, self.source, {}, profile=PROFILE)
        (self.base / "source-after.json").write_bytes(self.P.encode(dict(state=after, stamps=after_stamps)))
        self.assertFalse(timed_out, "actual CLI timeout is retained; it is not an original success")
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
        self.assertEqual((directory / "stdout.log").read_bytes(), b"lean-discipline.test: ok (17/17)\n")
        self.assertEqual((directory / "stderr.log").read_bytes(), b"")
        self.assertEqual((first["key"], first["receipt_digest"]), (second["key"], second["receipt_digest"]))
        self.assertEqual(len(list((self.base / "session").rglob("dispatch.json"))), 1)

    def test_actual_original_dynamic_scan_failure_is_retained_without_reuse(self):
        name = self.source / "skills/implementaudit/references/unreviewed-lean-control.md"
        name.write_bytes(b"actual extra ordinary member for the original dynamic scan\n")
        name.chmod(0o644)
        code, rows, stderr = self.invoke()
        self.assertEqual((code, len(rows)), (2, 1))
        result = rows[0]
        self.assertEqual((result["exit"], result["complete"], result["disposition"]), (1, True, "EXECUTED"))
        directory = Path(result["evidence_directory"])
        self.assertEqual((directory / "stdout.log").read_bytes(), b"")
        self.assertIn(b"FAIL: check-lean-discipline.sh should pass on current repo\n", (directory / "stderr.log").read_bytes())
        self.assertIn(b"failed or interrupted", stderr)
        self.assertEqual(len(list((self.base / "session").rglob("dispatch.json"))), 1)


if __name__ == "__main__":
    unittest.main()
