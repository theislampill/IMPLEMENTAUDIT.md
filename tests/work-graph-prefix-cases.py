#!/usr/bin/env python3
"""Bounded admission/consumer controls for the opt-in composed prefix.

These tiny constructed controls do not execute or qualify the canonical group.
The explicit actual profile remains separately scheduled by its caller.
"""
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


Q = load("prefix_qualifier", ROOT / "scripts/qualify-work-graph-verifier.py")


def stat_record(info, **changes):
    fields = {name: getattr(info, name) for name in
              ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")}
    fields.update(changes)
    return SimpleNamespace(**fields)


class AdmissionCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / "scripts/qualify-work-graph-prefix.py"

    def setUp(self):
        if not all(hasattr(os, name) for name in ("O_NOFOLLOW", "O_DIRECTORY")):
            self.skipTest("finite namespace profile requires no-follow descriptors")
        self.assertTrue(self.path.is_file(), "composed-prefix acquisition profile is absent")
        self.P = load("prefix_profile", self.path)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.source.mkdir()
        (self.source / "nested").mkdir()
        (self.source / "nested/input").write_bytes(b"original\n")
        self.objects = {}

    def snapshot(self, **limits):
        bounds = dict(self.P.SOURCE_BOUNDS, **limits)
        return self.P.snapshot_tree(self.source, self.objects, bounds)

    def test_stat_identifiers_preserve_uint64_domain_in_canonical_json(self):
        original = self.source.stat()
        encodings = set()
        for identifier in (0, 2**63 - 1, 2**63, 2**64 - 2, 2**64 - 1):
            with self.subTest(identifier=identifier):
                value = self.P.identity(stat_record(original, st_dev=identifier, st_ino=identifier))
                encoded = Q.WG.canonical_json_v1(dict(identity=value))
                restored = Q.WG.decode_strict_json_bytes(encoded, "stat identity")
                self.assertEqual(restored["identity"][:2], [str(identifier), str(identifier)])
                self.assertEqual(value[2:], [original.st_mode, original.st_nlink, original.st_size,
                                            original.st_mtime_ns, original.st_ctime_ns])
                encodings.add(encoded)
        self.assertEqual(len(encodings), 5, "adjacent unsigned identities collapsed")
        # Real current interpreter stat is observed without acquiring its bytes
        # or invoking the runtime-image/namespace path.
        actual = self.P.identity(Path(sys.executable).stat())
        self.assertEqual(json.loads(Q.WG.canonical_json_v1(actual)), actual)

    def test_stat_identifiers_refuse_malformed_and_out_of_domain_values(self):
        original = self.source.stat()
        for field in ("st_dev", "st_ino"):
            for invalid in (-1, 2**64, True, 1.0, "1", None):
                with self.subTest(field=field, invalid=invalid), self.assertRaisesRegex(ValueError, "unsigned 64-bit"):
                    self.P.identity(stat_record(original, **{field: invalid}))

    def test_original_group_is_exact_source_prefix_without_successor(self):
        registry = (ROOT / "scripts/verify-package.sh").read_bytes()
        graph, scope, data = self.P.select_prefix(Q.WG, registry, self.P.ENVIRONMENT)
        self.assertEqual(len(scope["nodes"]), 23)
        self.assertEqual(len(graph["nodes"]), 117)
        self.assertEqual(scope["nodes"][0], "PRELUDE")
        self.assertEqual(scope["nodes"][-1], "COMMAND:scripts/check-terminology-integration.sh:0")
        self.assertEqual(scope["stop_before"], "COMMAND:scripts/check-added-lines-clean.sh:0")
        self.assertEqual(data, registry[:39558])
        self.assertNotIn(b"printf 'verify-package: ok", data)
        with self.assertRaisesRegex(ValueError, "registry"):
            self.P.select_prefix(Q.WG, registry + b"\n", self.P.ENVIRONMENT)

    def test_snapshot_binds_bytes_modes_and_negative_namespace(self):
        first, _ = self.snapshot()
        (self.source / "nested/new").write_bytes(b"")
        second, _ = self.snapshot()
        self.assertNotEqual(first, second)
        (self.source / "nested/new").unlink()
        (self.source / "nested/input").chmod(0o600)
        third, _ = self.snapshot()
        self.assertNotEqual(first, third)
        (self.source / "nested/input").write_bytes(b"changed\n")
        fourth, _ = self.snapshot()
        self.assertNotEqual(third, fourth)

    def test_source_symlink_does_not_read_target(self):
        (self.base / "outside").write_bytes(b"must not be acquired")
        (self.source / "alias").symlink_to(self.base / "outside")
        with self.assertRaisesRegex(ValueError, "ordinary|symlink|kind"):
            self.snapshot()
        self.assertNotIn(Q.sha(b"must not be acquired"), self.objects)

    def test_ancestor_symlink_refuses(self):
        alias = self.base / "alias"
        alias.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            self.P.snapshot_tree(alias, self.objects, self.P.SOURCE_BOUNDS)

    def test_hardlink_and_fifo_refuse(self):
        os.link(self.source / "nested/input", self.source / "other")
        with self.assertRaisesRegex(ValueError, "link|ordinary"):
            self.snapshot()
        (self.source / "other").unlink()
        if hasattr(os, "mkfifo"):
            os.mkfifo(self.source / "fifo")
            with self.assertRaisesRegex(ValueError, "ordinary|kind"):
                self.snapshot()

    def test_bounds_apply_before_acquiring_oversized_inputs(self):
        for limits in ({"file_bytes": 2}, {"total_bytes": 2}, {"entries": 1}, {"depth": 1}):
            with self.subTest(limits=limits), self.assertRaisesRegex(ValueError, "bound"):
                self.snapshot(**limits)

    def test_reserved_bootstrap_directory_refuses(self):
        (self.source / ".IMPLEMENTAUDIT").mkdir()
        state, _ = self.snapshot()
        with self.assertRaisesRegex(ValueError, "reserved|collision"):
            self.P.source_archive(state, self.objects)

    def test_archive_roundtrip_preserves_exact_census_modes_and_bytes(self):
        (self.source / "empty").mkdir(mode=0o700)
        (self.source / "nested/input").chmod(0o640)
        state, _ = self.snapshot()
        archive = self.P.source_archive(state, self.objects)
        target = self.base / "materialized"
        target.mkdir()
        self.P.materialize_archive(archive, state, target)
        acquired, _ = self.P.snapshot_tree(target, {}, self.P.SOURCE_BOUNDS)
        self.assertEqual(acquired, state)
        member = target / "nested/input"
        self.assertEqual(member.stat().st_nlink, 1)
        self.assertEqual(member.stat().st_mtime_ns, 0)
        self.assertEqual(member.read_bytes(), b"original\n")

    def test_archive_rejects_duplicate_traversal_and_link(self):
        state, _ = self.snapshot()
        original = self.P.source_archive(state, self.objects)
        for attack in ("duplicate", "traversal", "link", "metadata", "missing"):
            data = io.BytesIO()
            with tarfile.open(fileobj=io.BytesIO(original), mode="r:") as old, tarfile.open(fileobj=data, mode="w:", format=tarfile.PAX_FORMAT) as new:
                members = old.getmembers()
                for item in members[:-1] if attack == "missing" else members:
                    new.addfile(item, old.extractfile(item) if item.isfile() else None)
                if attack != "missing":
                    item = tarfile.TarInfo("nested/input" if attack == "duplicate" else "../escape" if attack == "traversal" else "alien")
                    item.mode = 0o644
                    if attack == "link":
                        item.type, item.linkname = tarfile.SYMTYPE, "nested/input"
                    elif attack == "metadata":
                        item.uid = 1
                    new.addfile(item, io.BytesIO(b""))
            target = self.base / attack
            target.mkdir()
            with self.subTest(attack=attack), self.assertRaises(ValueError):
                self.P.materialize_archive(data.getvalue(), state, target)
            self.assertFalse((self.base / "escape").exists())

    def test_git_external_storage_and_config_refuse(self):
        git = self.source / ".git"
        git.mkdir()
        (git / "objects/info").mkdir(parents=True)
        (git / "config").write_text("[core]\nrepositoryformatversion = 0\nbare = false\n")
        state, _ = self.snapshot()
        self.P.validate_git_namespace(state, self.objects)
        for name in ("commondir", "objects/info/alternates", "shallow", "config.worktree"):
            path = git / name
            path.write_text("../../outside\n")
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Git|git"):
                self.P.validate_git_namespace(self.snapshot()[0], self.objects)
            path.unlink()
        (git / "config").write_text('[include]\npath = /outside\n')
        with self.assertRaisesRegex(ValueError, "config"):
            self.P.validate_git_namespace(self.snapshot()[0], self.objects)

    def test_runtime_budget_counts_aliases_and_unique_objects_separately(self):
        entries = {"/one": dict(sha256=Q.sha(b"data"), bytes=4, mode=0o444),
                   "/two": dict(sha256=Q.sha(b"data"), bytes=4, mode=0o444)}
        self.assertEqual(self.P.runtime_budget(entries, dict(entries=2, mounted_bytes=8, unique_bytes=4)),
                         dict(entries=2, mounted_bytes=8, unique_bytes=4))
        for bounds in (dict(entries=1, mounted_bytes=8, unique_bytes=4), dict(entries=2, mounted_bytes=7, unique_bytes=4), dict(entries=2, mounted_bytes=8, unique_bytes=3)):
            with self.subTest(bounds=bounds), self.assertRaisesRegex(ValueError, "bound"):
                self.P.runtime_budget(entries, bounds)

    def test_qualifier_exposes_only_explicit_prefix_route(self):
        self.assertTrue(callable(getattr(Q, "create_composed_prefix_session", None)))
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/qualify-work-graph-verifier.py"), "--help"], capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"prefix", result.stdout)
        self.assertIn(b"scoped", result.stdout)

    def test_changed_executable_requires_a_reviewed_prefix_contract(self):
        self.assertTrue(callable(getattr(self.P, "validate_programs", None)), "finite executable admission is absent")
        state = dict(files={n: dict(sha256=Q.sha((ROOT / n).read_bytes())) for n in self.P.PROGRAM_PINS})
        self.P.validate_programs(state)
        state["files"]["scripts/check-readme-toc.sh"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "executable"):
            self.P.validate_programs(state)

    def test_prefix24_selects_only_the_next_original_command(self):
        registry = (ROOT / "scripts/verify-package.sh").read_bytes()
        try:
            graph, scope, data = self.P.select_prefix(Q.WG, registry, self.P.ENVIRONMENT,
                profile="COMPOSED_SOURCE_PREFIX_24_V1")
        except TypeError as exc:
            self.fail("explicit original prefix24 selection is unavailable: " + str(exc))
        self.assertEqual(len(graph["nodes"]), 117)
        self.assertEqual(len(scope["nodes"]), 24)
        self.assertEqual(scope["profile"], "COMPOSED_SOURCE_PREFIX_24_V1")
        self.assertEqual(scope["nodes"][-1], "COMMAND:scripts/check-added-lines-clean.sh:0")
        self.assertEqual(scope["stop_before"], "COMMAND:tests/lean-discipline.test.sh:0")
        self.assertEqual(data, registry[:39603])
        self.assertEqual(Q.sha(data), "98246f2b17a7c0c1f1d443e587b0eec9ac2240ecc1a4edda7c46ecefdc81e8a4")
        self.assertTrue(data.endswith(b"bash scripts/check-added-lines-clean.sh HEAD\n"))
        self.assertNotIn(b"bash tests/lean-discipline.test.sh\n", data)
        self.assertNotIn(b"printf 'verify-package: ok", data)

    def test_prefix24_pins_both_new_transitive_programs(self):
        paths = set(self.P.PROGRAM_PINS) | {"scripts/check-added-lines-clean.sh",
            "skills/implementaudit/scripts/repo-state.sh"}
        state = dict(files={n: dict(sha256=Q.sha((ROOT / n).read_bytes())) for n in paths})
        self.P.validate_programs(state, profile="COMPOSED_SOURCE_PREFIX_24_V1")
        for path in ("scripts/check-added-lines-clean.sh", "skills/implementaudit/scripts/repo-state.sh"):
            original = state["files"].pop(path)
            with self.subTest(path=path, change="missing"), self.assertRaisesRegex(ValueError, "executable"):
                self.P.validate_programs(state, profile="COMPOSED_SOURCE_PREFIX_24_V1")
            state["files"][path] = dict(sha256="0" * 64)
            with self.subTest(path=path, change="changed"), self.assertRaisesRegex(ValueError, "executable"):
                self.P.validate_programs(state, profile="COMPOSED_SOURCE_PREFIX_24_V1")
            # Neither new pin changes the historical prefix23 admission scope.
            self.P.validate_programs(state)
            state["files"][path] = original

    def test_unknown_profile_refuses_before_evidence_creation(self):
        for profile in ("prefix24", "COMPOSED_SOURCE_PREFIX_25_V1", "", None, [], {}):
            destination = self.base / "refused-evidence"
            with self.subTest(profile=profile), self.assertRaisesRegex(ValueError, "profile"):
                Q.create_composed_prefix_session(self.source, destination, profile=profile)
            self.assertFalse(destination.exists())

    def test_prefix24_cli_without_requests_does_not_execute(self):
        destination = self.base / "cli-evidence"
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/qualify-work-graph-verifier.py"),
            "prefix24", str(self.source), str(destination)], input=b"", capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads((destination / "session.json").read_bytes())
        self.assertEqual(record["scope"], "COMPOSED_SOURCE_PREFIX_24_V1")
        self.assertEqual(result.stdout, b"")
        self.assertEqual(sorted(p.name for p in destination.iterdir()), ["session.json"])

    def test_prefix_routes_refuse_imported_receipts_and_oversized_requests(self):
        requests = (b'{"operation":"run","receipt":{"exit":0}}\n',
                    b'{"operation":"run","scope":"COMPOSED_SOURCE_PREFIX_23_V1"}\n',
                    b" " * 4097 + b'\n')
        for mode in ("prefix", "prefix24"):
            for index, request in enumerate(requests):
                destination = self.base / (mode + "-request-" + str(index))
                result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/qualify-work-graph-verifier.py"),
                    mode, str(self.source), str(destination)], input=request, capture_output=True)
                with self.subTest(mode=mode, request=index):
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertEqual(result.stdout, b"")
                    self.assertEqual(sorted(p.name for p in destination.iterdir()), ["session.json"])
                    self.assertIn(b"byte bound" if index == 2 else b"only a current-source run request", result.stderr)


class NamespaceCases(unittest.TestCase):
    """Opt-in tiny actual launch controls, never canonical prefix qualification."""

    @classmethod
    def setUpClass(cls):
        if os.environ.get("R0035_PREFIX24_LIVE") != "1":
            raise unittest.SkipTest("set R0035_PREFIX24_LIVE=1 for tiny actual namespace controls")
        if sys.platform != "linux" or not Path("/usr/bin/bwrap").is_file():
            raise unittest.SkipTest("actual prefix image requires Linux bubblewrap")
        cls.P = load("namespace_prefix", ROOT / "scripts/qualify-work-graph-prefix.py")
        cls.objects = {}
        cls.runtime = cls.P.acquire_runtime(cls.objects)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.source.mkdir()

    def launch(self, script, *, profile=None):
        output = self.base / ("default" if profile is None else profile)
        options = {} if profile is None else dict(profile=profile)
        session = Q.create_composed_prefix_session(self.source, output, **options)
        state = dict(files={}, directories={".": 0o755})
        image = dict(runtime=self.runtime, objects=self.objects,
            archive=self.P.source_archive(state, {}), source=state, prefix=script,
            key="0" * 64, acquired=dict(scope=dict(nodes=["constructed-process-substitution"])),
            required_objects=[])
        directory = output / "execution"
        receipt, _ = session._execute_group(image, directory)
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        if os.environ.get("R0035_PREFIX24_EVIDENCE"):
            retained = Path(os.environ["R0035_PREFIX24_EVIDENCE"]) / self._testMethodName
            retained.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(output, retained)
            (retained / "control.sh").write_bytes(script)
            (retained / "runtime.json").write_bytes(self.P.encode(self.runtime))
            (retained / "control.json").write_bytes(self.P.encode(dict(
                evidence="CONSTRUCTED_LAUNCH_CONTROL_NOT_CANONICAL_PREFIX_QUALIFICATION",
                source=state, source_archive_sha256=Q.sha(image["archive"]),
                helper_sha256=Q.sha((ROOT / "scripts/qualify-work-graph-prefix.py").read_bytes()),
                qualifier_sha256=Q.sha((ROOT / "scripts/qualify-work-graph-verifier.py").read_bytes()),
                test_sha256=Q.sha(Path(__file__).read_bytes()), authority="NONE")))
        unavailable = (b"Creating new namespace failed: Operation not permitted",
                       b"No permissions to create new namespace",
                       b"setting up uid map: Permission denied")
        if receipt["exit"] != 0 and not stdout and any(message in stderr for message in unavailable):
            self.skipTest("host namespace capability refused before subject execution: " + stderr.decode(errors="replace").strip())
        self.assertEqual((directory / "exit-code.txt").read_bytes(), (str(receipt["exit"]) + "\n").encode())
        return session, receipt, stdout, stderr

    def test_default_no_proc_image_retains_process_substitution_failure(self):
        script = b"set -euo pipefail\nwhile IFS= read -r value; do printf '%s\\n' \"$value\"; done < <(printf 'descriptor-input\\n')\n"
        session, receipt, stdout, stderr = self.launch(script)
        self.assertNotEqual(receipt["exit"], 0)
        self.assertEqual(stdout, b"")
        self.assertIn(b"/dev/fd/", stderr)
        self.assertEqual(session._issued, {})

    def test_prefix24_process_substitution_uses_private_proc(self):
        script = b"set -euo pipefail\nwhile IFS= read -r value; do printf '%s\\n' \"$value\"; done < <(printf 'descriptor-input\\n')\n"
        session, receipt, stdout, stderr = self.launch(script, profile="COMPOSED_SOURCE_PREFIX_24_V1")
        self.assertEqual(receipt["exit"], 0, stderr)
        self.assertEqual(stdout, b"descriptor-input\n")
        self.assertEqual(stderr, b"")
        self.assertEqual(receipt["scope"], "COMPOSED_SOURCE_PREFIX_24_V1")
        self.assertEqual(session._issued, {}, "direct launch is not a successful consumption")

    def test_prefix24_proc_does_not_expose_host_process_or_input_descriptors(self):
        program = '''import ctypes, errno, json, os
from pathlib import Path
assert Path('/proc/self/stat').is_file()
assert os.readlink('/dev/fd') == '/proc/self/fd'
assert not Path('/proc/%d/stat').exists()
assert not Path('/proc/1/root%s').exists()
assert not Path('/proc/self/fd/3').exists()
assert os.read(0, 1) == b''
libc = ctypes.CDLL(None, use_errno=True)
assert libc.unshare(0x10000000) == -1 and ctypes.get_errno() == errno.EPERM
assert libc.setns(-1, 0) == -1 and ctypes.get_errno() == errno.EPERM
try:
    os.open('/proc/sys/kernel/randomize_va_space', os.O_WRONLY)
except OSError as exc:
    assert exc.errno in (errno.EROFS, errno.EACCES, errno.ENOENT)
else:
    raise AssertionError('proc kernel control is writable')
print('private-proc-custody: ok')
''' % (os.getpid(), str(self.source))
        script = b"set -euo pipefail\npython - <<'PY'\n" + program.encode() + b"PY\n"
        _, receipt, stdout, stderr = self.launch(script, profile="COMPOSED_SOURCE_PREFIX_24_V1")
        self.assertEqual(receipt["exit"], 0, stderr)
        self.assertEqual(stdout, b"private-proc-custody: ok\n")
        self.assertEqual(stderr, b"")


class CustodyCases(unittest.TestCase):
    """Constructed tiny producer records exercise the real live consumer.

    Input acquisition and subprocess dispatch are replaced only in tests that
    isolate the consumer state machine; these do not claim canonical execution.
    Byte/mode/object checks and source/engine/private-directory custody stay real.
    """
    def setUp(self):
        if Q.fcntl is None or not hasattr(Q.fcntl, "F_GET_SEALS"):
            self.skipTest("finite execution needs observable Linux memfd seals")
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.source.mkdir()
        self.source_file = self.source / "input"
        self.source_file.write_bytes(b"input\n")
        self.S = Q.create_composed_prefix_session(self.source, self.base / "evidence")
        self.P = load("custody_prefix", ROOT / "scripts/qualify-work-graph-prefix.py")

    def seed(self, *, code=0, complete=True):
        """Tiny constructed record, not a supplied API receipt/exit authority."""
        directory = self.S.output / "constructed-producer"
        directory.mkdir(mode=0o700)
        key = Q.sha(self.source_file.read_bytes())
        required = [self.S._object(b"archive"), self.S._object(b"runtime"), self.S._object(b"prefix"), self.S._object(b"seccomp")]
        receipt = dict(key=key, exit=code, complete=complete, scope=self.S.SCOPE)
        raw = {"stdout.log": b"tiny\n", "stderr.log": b"", "exit-code.txt": (str(code) + "\n").encode(), "receipt.json": Q.WG.canonical_json_v1(receipt)}
        for name, data in raw.items():
            self.S._write(directory / name, data)
            (directory / name).chmod(0o400)
        retained = dict(key=key, directory=directory, retained=raw, required_objects=required, observed_at=time.monotonic())
        return receipt, retained

    def input(self):
        return dict(key=Q.sha(self.source_file.read_bytes()), stamps={"file": self.source_file.stat().st_ctime_ns},
                    acquired=dict(scope=dict(nodes=["constructed-group"], omitted_nodes=[])), graph={})

    def test_unchanged_live_consumption_keeps_original_receipt_and_dispatch(self):
        receipt, retained = self.seed()
        with mock.patch.object(self.S, "_acquire", side_effect=self.input), mock.patch.object(self.S, "_execute_group", return_value=(receipt, retained)) as dispatch:
            first = self.S.run()
            second = self.S.run()
        self.assertEqual((first["disposition"], second["disposition"]), ("EXECUTED", "REUSED"))
        self.assertEqual(first["receipt_digest"], second["receipt_digest"])
        self.assertEqual(dispatch.call_count, 1)

    def test_profiles_keep_distinct_live_results_and_original_default(self):
        sessions = [self.S, Q.create_composed_prefix_session(self.source, self.base / "prefix24-evidence",
            profile="COMPOSED_SOURCE_PREFIX_24_V1")]
        expected = ["COMPOSED_SOURCE_PREFIX_23_V1", "COMPOSED_SOURCE_PREFIX_24_V1"]
        for session, scope in zip(sessions, expected):
            self.S = session
            receipt, retained = self.seed()
            with mock.patch.object(self.S, "_acquire", side_effect=self.input), mock.patch.object(self.S, "_execute_group", return_value=(receipt, retained)) as dispatch:
                first = self.S.run()
                second = self.S.run()
            with self.subTest(scope=scope):
                self.assertEqual((first["disposition"], second["disposition"]), ("EXECUTED", "REUSED"))
                self.assertEqual((first["scope"], second["scope"]), (scope, scope))
                self.assertEqual(set(self.S._issued), {scope})
                self.assertEqual(dispatch.call_count, 1)
                with self.assertRaises(TypeError):
                    self.S.run(receipt=receipt)
        self.assertIsNot(type(sessions[0]), type(sessions[1]))
        self.assertNotEqual(sessions[0].producer, sessions[1].producer)
        default = Q.create_composed_prefix_session(self.source, self.base / "later-default")
        self.assertEqual(default.SCOPE, expected[0])

    def test_prefix24_failed_or_changed_results_refuse_reuse(self):
        for case in ("failed", "incomplete", "changed-output", "changed-source"):
            self.source_file.write_bytes(b"input\n")
            self.S = Q.create_composed_prefix_session(self.source, self.base / ("prefix24-" + case),
                profile="COMPOSED_SOURCE_PREFIX_24_V1")
            receipt, retained = self.seed(code=7 if case == "failed" else 0, complete=case != "incomplete")
            with mock.patch.object(self.S, "_acquire", side_effect=self.input), mock.patch.object(self.S, "_execute_group", return_value=(receipt, retained)) as dispatch:
                self.S.run()
                if case == "changed-output":
                    target = retained["directory"] / "stdout.log"
                    target.chmod(0o600)
                    target.write_bytes(b"rewritten output\n")
                    target.chmod(0o400)
                elif case == "changed-source":
                    self.source_file.write_bytes(b"different\n")
                with self.subTest(case=case), self.assertRaises(ValueError):
                    self.S.run()
                self.assertEqual(dispatch.call_count, 1)

    def test_changed_current_input_refuses_before_dispatch(self):
        receipt, retained = self.seed()
        with mock.patch.object(self.S, "_acquire", side_effect=self.input), mock.patch.object(self.S, "_execute_group", return_value=(receipt, retained)) as dispatch:
            self.S.run()
            self.source_file.write_bytes(b"different\n")
            with self.assertRaisesRegex(ValueError, "prior receipt refused"):
                self.S.run()
            self.assertEqual(dispatch.call_count, 1)
            self.source_file.write_bytes(b"input\n")
            self.assertEqual(self.S.run()["disposition"], "REUSED")

    def test_failed_or_incomplete_results_never_issue_reuse(self):
        for code, complete in ((7, True), (0, False)):
            with self.subTest(code=code, complete=complete):
                # Separate live producer per real consumer case.
                self.S = Q.create_composed_prefix_session(self.source, self.base / ("failure-%s-%s" % (code, complete)))
                receipt, retained = self.seed(code=code, complete=complete)
                with mock.patch.object(self.S, "_acquire", side_effect=self.input), mock.patch.object(self.S, "_execute_group", return_value=(receipt, retained)) as dispatch:
                    self.S.run()
                    with self.assertRaisesRegex(ValueError, "failed or interrupted"):
                        self.S.run()
                    self.assertEqual(dispatch.call_count, 1)

    def test_raw_receipt_output_and_required_objects_cannot_be_resealed(self):
        receipt, retained = self.seed()
        self.S._issued[self.P.PROFILE] = retained
        targets = [retained["directory"] / n for n in retained["retained"]]
        targets += [self.S.output / "objects" / n for n in retained["required_objects"]]
        for target in targets:
            original = target.read_bytes()
            target.chmod(0o600)
            target.write_bytes(b"forged same-success declaration\n")
            target.chmod(0o400)
            with self.subTest(target=target.name):
                keys, refused = self.S._issued_keys()
                self.assertNotIn(self.P.PROFILE, keys)
                self.assertIn(self.P.PROFILE, refused)
            target.chmod(0o600)
            target.write_bytes(original)
            target.chmod(0o400)
        self.assertIn(self.P.PROFILE, self.S._issued_keys()[0])

    def test_missing_object_is_not_silently_reconstructed(self):
        key = self.S._object(b"required input")
        (self.S.output / "objects" / key).unlink()
        with self.assertRaisesRegex(ValueError, "missing|changed"):
            self.S._object(b"required input")

    def test_expiry_process_environment_and_private_custody_refuse(self):
        _, retained = self.seed()
        self.S._issued[self.P.PROFILE] = retained
        retained["observed_at"] -= self.S.max_age + 1
        self.assertIn(self.P.PROFILE, self.S._issued_keys()[1])
        retained["observed_at"] = time.monotonic()
        with mock.patch.object(os, "getpid", return_value=self.S.producer_pid + 1), self.assertRaisesRegex(ValueError, "process changed"):
            self.S.run()
        self.S.environment["BASH_ENV"] = "/unacquired"
        with self.assertRaisesRegex(ValueError, "environment changed"):
            self.S.run()
        self.S.environment.pop("BASH_ENV")
        self.S.output.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "custody changed"):
            self.S.run()

    def test_adjacent_uint64_custody_identity_refuses_before_acquisition(self):
        current = self.S.output.lstat()
        observed = [2**63]
        original_lstat = Path.lstat
        def lstat(path, *args, **kwargs):
            if path == self.S.output:
                return stat_record(current, st_dev=2**64 - 1, st_ino=observed[0])
            return original_lstat(path, *args, **kwargs)
        self.S._output_identity = self.P.identity(stat_record(current, st_dev=2**64 - 1, st_ino=observed[0]))[:2]
        with mock.patch.object(Path, "lstat", lstat), mock.patch.object(self.S, "_acquire") as acquire:
            self.S._custody()
            observed[0] += 1
            with self.assertRaisesRegex(ValueError, "custody changed"):
                self.S.run()
            acquire.assert_not_called()
        self.assertEqual(self.S.dispatch_count, 0)

    def test_no_imported_receipt_entrypoint(self):
        _, retained = self.seed()
        with self.assertRaises(TypeError):
            self.S.run(receipt=json.loads(retained["retained"]["receipt.json"]))
        self.assertEqual(self.S.dispatch_count, 0)

    def test_source_change_during_consumption_does_not_issue_result(self):
        receipt, retained = self.seed()
        before = self.input()
        self.source_file.write_bytes(b"different\n")
        after = self.input()
        with mock.patch.object(self.S, "_acquire", side_effect=[before, after]), mock.patch.object(self.S, "_execute_group", return_value=(receipt, retained)):
            with self.assertRaisesRegex(ValueError, "during-consumption"):
                self.S.run()
        self.assertEqual(self.S._issued, {})

    def test_new_result_is_rechecked_after_post_execution_acquisition(self):
        receipt, retained = self.seed()
        calls = [0]
        def acquire():
            calls[0] += 1
            if calls[0] == 2:
                path = retained["directory"] / "stdout.log"
                path.chmod(0o600)
                path.write_bytes(b"changed after actual exit\n")
                path.chmod(0o400)
            return self.input()
        with mock.patch.object(self.S, "_acquire", side_effect=acquire), mock.patch.object(self.S, "_execute_group", return_value=(receipt, retained)):
            with self.assertRaisesRegex(ValueError, "issued.*changed"):
                self.S.run()
        self.assertEqual(self.S._issued, {})

    def tiny_image(self):
        return dict(runtime=dict(directories=[], files={}), objects={}, archive=b"constructed archive",
                    source=dict(files={}, directories={".": 0o755}), prefix=b"constructed prefix\n",
                    key="0" * 64, acquired=dict(scope=dict(nodes=["constructed-group"])), required_objects=[])

    def test_prelaunch_error_closes_every_sealed_descriptor(self):
        descriptors = []
        original = self.S._sealed
        def seal(data):
            fd = original(data)
            descriptors.append(fd)
            return fd
        directory = self.S.output / "launch-failure"
        with mock.patch.object(self.S, "_sealed", side_effect=seal), mock.patch.object(subprocess, "Popen", side_effect=OSError("constructed launch refusal")):
            with self.assertRaisesRegex(OSError, "launch refusal"):
                self.S._execute_group(self.tiny_image(), directory)
        for fd in descriptors:
            with self.assertRaises(OSError):
                os.fstat(fd)
        record = json.loads((directory / "launch-error.json").read_bytes())
        self.assertEqual(record["actual_exit"], "UNOBSERVED")
        self.assertFalse((directory / "exit-code.txt").exists())

    def test_proc_profile_has_no_host_proc_or_launch_fallback(self):
        for profile in ("COMPOSED_SOURCE_PREFIX_23_V1", "COMPOSED_SOURCE_PREFIX_24_V1"):
            self.S = Q.create_composed_prefix_session(self.source, self.base / profile, profile=profile)
            launches = []
            def refuse(argv, **kwargs):
                self.assertEqual(argv[:2], ["/usr/bin/bwrap", "--args"])
                raw = os.pread(int(argv[2]), 256 * 1024, 0)
                self.assertTrue(raw.endswith(b"\0"))
                launches.append(raw[:-1].decode().split("\0"))
                raise OSError("constructed namespace launch refusal")
            directory = self.S.output / "launch"
            with mock.patch.object(subprocess, "Popen", side_effect=refuse):
                with self.assertRaisesRegex(OSError, "namespace launch refusal"):
                    self.S._execute_group(self.tiny_image(), directory)
            with self.subTest(profile=profile):
                self.assertEqual(len(launches), 1, "namespace refusal must not retry with a weaker image")
                args = launches[0]
                self.assertIn("--unshare-all", args)
                self.assertNotIn("--bind", args)
                self.assertNotIn("--ro-bind", args)
                if profile.endswith("24_V1"):
                    pos = args.index("--proc")
                    self.assertEqual(args[pos:pos + 7], ["--proc", "/proc", "--remount-ro", "/proc",
                                                       "--symlink", "/proc/self/fd", "/dev/fd"])
                else:
                    self.assertNotIn("--proc", args)
                    self.assertNotIn("/dev/fd", args)
                self.assertFalse((directory / "receipt.json").exists())
                self.assertEqual(self.S._issued, {})

    def tiny_process(self, program, **kwargs):
        # Replace only the external namespace launcher in constructed observer
        # controls. This is explicitly not a sandbox/canonical execution proof.
        return self.real_popen([sys.executable, "-B", "-c", program], **kwargs)

    def test_actual_child_exit_survives_later_receipt_error(self):
        self.real_popen = subprocess.Popen
        write = self.S._write
        def record(path, value):
            if path.name == "receipt.json":
                raise ValueError("constructed later receipt error")
            return write(path, value)
        directory = self.S.output / "durability"
        with mock.patch.object(subprocess, "Popen", side_effect=lambda argv, **kwargs: self.tiny_process("print('actual tiny stdout'); raise SystemExit(7)", **kwargs)), mock.patch.object(self.S, "_write", side_effect=record):
            with self.assertRaisesRegex(ValueError, "later receipt error"):
                self.S._execute_group(self.tiny_image(), directory)
        self.assertEqual((directory / "exit-code.txt").read_bytes(), b"7\n")
        self.assertEqual((directory / "stdout.log").read_bytes(), b"actual tiny stdout\n")
        self.assertEqual(self.S._issued, {})

    def test_timeout_and_interruption_keep_actual_owned_child_exit(self):
        self.real_popen = subprocess.Popen
        for operation in ("timeout", "interrupt"):
            directory = self.S.output / operation
            self.S.LIMITS = dict(self.S.LIMITS, wall_seconds=0.05)
            def launch(argv, **kwargs):
                child = self.tiny_process("import time; time.sleep(5)", **kwargs)
                if operation == "interrupt":
                    wait = child.wait
                    once = [True]
                    def interrupted(*args, **kw):
                        if once[0]:
                            once[0] = False
                            raise KeyboardInterrupt()
                        return wait(*args, **kw)
                    child.wait = interrupted
                return child
            with mock.patch.object(subprocess, "Popen", side_effect=launch):
                if operation == "interrupt":
                    with self.assertRaises(KeyboardInterrupt):
                        self.S._execute_group(self.tiny_image(), directory)
                else:
                    receipt, _ = self.S._execute_group(self.tiny_image(), directory)
                    self.assertFalse(receipt["complete"])
            self.assertEqual((directory / "exit-code.txt").read_bytes(), b"-9\n")
            self.assertEqual(self.S._issued, {})

    def test_prefix_cli_does_not_report_signalled_or_incomplete_success(self):
        class Input:
            buffer = io.BytesIO(b'{"operation":"run"}\n')
        for mode in ("prefix", "prefix24"):
            for code, complete in ((-9, False), (0, False)):
                Input.buffer = io.BytesIO(b'{"operation":"run"}\n')
                session = mock.Mock()
                session.run.return_value = dict(exit=code, complete=complete)
                with mock.patch.object(sys, "argv", ["qualifier", mode, str(self.source), str(self.base / "unused")]), mock.patch.object(sys, "stdin", Input), mock.patch.object(sys, "stdout", io.StringIO()), mock.patch.object(Q, "create_composed_prefix_session", return_value=session):
                    self.assertNotEqual(Q.main(), 0)

    def exit_before_kill(self, operation, code):
        """Real child and killpg; a pipe fixes the exit-before-signal ordering.

        Only the external launcher and acquisition are substituted. This is a
        termination/custody control, not a namespace or prefix execution proof.
        """
        self.S = Q.create_composed_prefix_session(self.source, self.base / ("race-%s-%s" % (operation, code)))
        self.S.LIMITS = dict(self.S.LIMITS, wall_seconds=0.01)
        real_popen, real_killpg = subprocess.Popen, os.killpg
        readfd, writefd = os.pipe()
        child, observed = {}, {}
        interruption = KeyboardInterrupt("controlled wait interruption")
        def launch(argv, **kwargs):
            kwargs["pass_fds"] = (*kwargs["pass_fds"], readfd)
            process = real_popen([sys.executable, "-B", "-c",
                "import os,sys; os.read(int(sys.argv[1]),1); print('actual exit race'); raise SystemExit(int(sys.argv[2]))",
                str(readfd), str(code)], **kwargs)
            child["process"], child["wait"] = process, process.wait
            if operation == "interrupt":
                first = [True]
                def interrupted(*args, **kw):
                    if first[0]:
                        first[0] = False
                        raise interruption
                    return child["wait"](*args, **kw)
                process.wait = interrupted
            return process
        def kill_after_exit(pgid, signum):
            self.assertEqual(pgid, child["process"].pid)
            self.assertEqual(signum, signal.SIGKILL)
            # The child cannot exit before this gate, so the interruption's
            # poll sees a live child. The real group then disappears before
            # the real signal call, without relying on scheduler sleeps.
            os.write(writefd, b"x")
            observed["exit"] = child["wait"](timeout=2)
            self.assertEqual(observed["exit"], code)
            try:
                return real_killpg(pgid, signum)
            except ProcessLookupError:
                observed["group_absent"] = True
                raise
        acquired = dict(self.tiny_image(), stamps={}, graph={})
        directory = self.S.output / "generation-000001" / "execution"
        try:
            with mock.patch.object(subprocess, "Popen", side_effect=launch), mock.patch.object(os, "killpg", side_effect=kill_after_exit), mock.patch.object(self.S, "_acquire", return_value=acquired):
                if operation == "interrupt":
                    with self.assertRaises(KeyboardInterrupt) as raised:
                        self.S.run()
                    self.assertIs(raised.exception, interruption)
                    self.assertFalse((directory / "receipt.json").exists())
                else:
                    result = self.S.run()
                    self.assertEqual(result["exit"], code)
                    self.assertFalse(result["complete"])
                    self.assertFalse(json.loads((directory / "receipt.json").read_bytes())["complete"])
                self.assertEqual(observed, dict(exit=code, group_absent=True))
                self.assertEqual((directory / "exit-code.txt").read_bytes(), (str(code) + "\n").encode())
                self.assertEqual((directory / "stdout.log").read_bytes(), b"actual exit race\n")
                self.assertEqual((directory / "stderr.log").read_bytes(), b"")
                self.assertEqual(self.S._issued, {})
                with self.assertRaisesRegex(ValueError, "failed or interrupted"):
                    self.S.run()
                self.assertEqual(self.S.dispatch_count, 1)
        finally:
            if "process" in child and child["process"].poll() is None:
                try:
                    real_killpg(child["process"].pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                child["wait"](timeout=2)
            os.close(readfd)
            os.close(writefd)

    def test_timeout_exit_before_kill_preserves_actual_exit_without_success(self):
        for code in (0, 7):
            with self.subTest(code=code):
                self.exit_before_kill("timeout", code)

    def test_interruption_exit_before_kill_preserves_actual_exit_and_exception(self):
        for code in (0, 7):
            with self.subTest(code=code):
                self.exit_before_kill("interrupt", code)

    def test_concurrent_consumption_refuses_without_second_acquisition(self):
        entered, release = threading.Event(), threading.Event()
        errors = []
        calls = [0]
        def acquire():
            calls[0] += 1
            if calls[0] != 1:
                raise AssertionError("second acquisition entered concurrent consumer")
            entered.set()
            release.wait(timeout=2)
            raise ValueError("constructed stopped first acquisition")
        def first():
            try:
                self.S.run()
            except BaseException as exc:
                errors.append(exc)
        with mock.patch.object(self.S, "_acquire", side_effect=acquire):
            thread = threading.Thread(target=first)
            thread.start()
            self.assertTrue(entered.wait(timeout=2))
            try:
                with self.assertRaisesRegex(ValueError, "concurrent"):
                    self.S.run()
            finally:
                release.set()
                thread.join(timeout=2)
        self.assertEqual(calls[0], 1)
        self.assertEqual(len(errors), 1)


if __name__ == "__main__":
    unittest.main()
