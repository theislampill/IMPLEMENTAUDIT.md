"""Combined portable interfaces only; no authentic admission or native effects."""
import hashlib
import gzip
import ast
import contextlib
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
from argparse import Namespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "skills/implementaudit/scripts"
PEER = ROOT / "source-peers/native-runtime/skills/implementaudit/scripts"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompositeSourceCases(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted prerequisites")
    def test_c5_hosted_current_reader_binds_before_owner_loading(self):
        """Break caught: a changed loader or implicit original profile reads host inputs."""
        observer = load("hosted_current_reader_control", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        receive = getattr(observer, "hosted_current_owner", None)
        self.assertTrue(callable(receive), "bounded hosted current-owner receiving is absent")
        with mock.patch("subprocess.Popen", side_effect=AssertionError("reader dispatched a child")):
            current = receive(ROOT)
            self.assertEqual(current.PROFILE, "FIXED_GENUINE_C5_PRODUCER_EFFECT_CURRENT_COMPOSITE_20261027_V1")
            with tempfile.TemporaryDirectory(prefix="c5-hosted-loader-") as temporary:
                root = Path(temporary)
                (root / "scripts").mkdir()
                (root / "scripts/load-work-graph-c5-executor.py").write_bytes(b"raise AssertionError('must not execute')\n")
                with self.assertRaisesRegex(ValueError, "loader pin"):
                    receive(root)

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted prerequisites")
    def test_c5_hosted_pin_receiving_retains_actual_mismatch(self):
        """Break caught: different host bytes are silently accepted or reprofiled."""
        observer = load("hosted_pin_receiving_control", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        receive = getattr(observer, "hosted_pin_receiving", None)
        self.assertTrue(callable(receive), "literal hosted pin receiving is absent")
        original = load("hosted_pin_owner", ROOT / "scripts/load-work-graph-c5-executor.py")
        base = original._Engine(original.CURRENT_PROFILE).load().B
        with tempfile.TemporaryDirectory(prefix="c5-hosted-pin-") as temporary:
            path = Path(temporary) / "input"
            path.write_bytes(b"abc")
            path.chmod(0o600)
            pin = dict(bytes=3, sha256="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
                       mode=0o600, resolved=str(path), link=None)
            objects = {}
            first = receive(base, str(path), pin, objects)
            self.assertTrue(first["match"])
            self.assertEqual(objects[first["observed"]["sha256"]], b"abc")
            path.write_bytes(b"abd")
            second = receive(base, str(path), pin, objects)
            self.assertFalse(second["match"])
            self.assertEqual(second["expected"], pin)
            self.assertNotEqual(second["observed"]["sha256"], pin["sha256"])

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted prerequisites")
    def test_c5_hosted_nss_receiving_uses_original_refusals(self):
        """Break caught: nonzero identity or a broader NSS provider is called applicable."""
        observer = load("hosted_nss_receiving_control", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        receive = getattr(observer, "hosted_nss_receiving", None)
        self.assertTrue(callable(receive), "literal hosted NSS receiving is absent")
        original = load("hosted_nss_owner", ROOT / "scripts/load-work-graph-c5-executor.py")
        selected = original._Engine(original.CURRENT_PROFILE).load()
        # Explicit source-control data for the unchanged NSS parser, not a host receipt.
        objects = {}
        observed = dict(files={}, nscd={name: {"kind": "MISSING"} for name in selected.B._NSCD})
        for name, raw in [("/etc/passwd", b"root:x:0:0:root:/root:/bin/bash\n"),
                          ("/etc/nsswitch.conf", b"passwd: files\n")]:
            digest = hashlib.sha256(raw).hexdigest()
            objects[digest] = raw
            observed["files"][name] = dict(kind="FILE", resolved=name, mode=0o644, sha256=digest)
        zero = dict(uid=0, euid=0, gid=0, egid=0)
        self.assertTrue(receive(selected.D, observed, objects, zero)["match"])
        self.assertFalse(receive(selected.D, observed, objects, dict(zero, uid=1001))["match"])
        raw = b"passwd: files systemd\n"
        digest = hashlib.sha256(raw).hexdigest()
        objects[digest] = raw
        observed["files"]["/etc/nsswitch.conf"]["sha256"] = digest
        refusal = receive(selected.D, observed, objects, zero)
        self.assertFalse(refusal["match"])
        self.assertIn("files-only", refusal["reason"])

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted prerequisites")
    def test_c5_hosted_git_receiving_bounds_output_and_waits(self):
        """Break caught: output overflow or timeout leaks the owned ordinary Git child."""
        observer = load("hosted_git_receiving_control", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        run = getattr(observer, "hosted_git", None)
        self.assertTrue(callable(run), "bounded hosted Git receiving is absent")
        with tempfile.TemporaryDirectory(prefix="c5-hosted-command-") as temporary:
            records = []
            raw = run(["--version"], Path(temporary), records)
            self.assertTrue(raw.startswith(b"git version "))
            self.assertTrue(records[-1]["wait_reaped"])
            self.assertTrue(records[-1]["owned_group_absent"])
            self.assertTrue(records[-1]["descriptor_restoration"])
            with self.assertRaisesRegex(ValueError, "output bound"):
                run(["--version"], Path(temporary), records, stream_limit=3)
            self.assertTrue(records[-1]["output_overflow"])
            self.assertTrue(records[-1]["wait_reaped"])
            with self.assertRaisesRegex(ValueError, "wall bound"):
                run(["-c", "alias.c5wait=!sleep 2", "c5wait"], Path(temporary), records, wall_seconds=0.03)
            self.assertTrue(records[-1]["timed_out"])
            self.assertTrue(records[-1]["wait_reaped"])

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted prerequisites")
    def test_c5_hosted_deadline_stops_work_and_preserves_terminal_receiving(self):
        """Break caught: the whole-operation deadline becomes an ordinary refusal and starts more work."""
        observer = load("hosted_deadline_control", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        for point in ("host_inputs", "source_preparation", "current_owner"):
            with self.subTest(point=point), contextlib.ExitStack() as stack:
                handlers = {}
                def install(signum, handler):
                    if callable(handler):
                        handlers["deadline"] = handler
                    return "CONTROL_OLD_HANDLER"
                def expire(*args, **kwargs):
                    handlers["deadline"](None, None)
                stack.enter_context(mock.patch.object(observer.resource, "setrlimit"))
                signals = stack.enter_context(mock.patch.object(observer.signal, "signal", side_effect=install))
                alarms = stack.enter_context(mock.patch.object(observer.signal, "alarm"))
                for name in ("getuid", "geteuid", "getgid", "getegid"):
                    stack.enter_context(mock.patch.object(observer.os, name, return_value=0))
                stack.enter_context(mock.patch.object(observer, "fds", return_value={"CONTROL": "UNCHANGED"}))
                owner = stack.enter_context(mock.patch.object(observer, "hosted_current_owner",
                    return_value=Namespace(PROFILE="CONTROL_ONLY")))
                inputs = stack.enter_context(mock.patch.object(observer, "receive_hosted_inputs", return_value={}))
                temporary = stack.enter_context(mock.patch("tempfile.mkdtemp", return_value="/CONTROL_ONLY_NOT_CREATED"))
                prepare = stack.enter_context(mock.patch.object(observer, "prepare_hosted_source",
                    side_effect=ValueError("controlled stop before source effects")))
                {"current_owner": owner, "host_inputs": inputs, "source_preparation": prepare}[point].side_effect = expire
                output = stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                code = observer.receive_hosted_prerequisites("a" * 40)
                if point != "source_preparation":
                    prepare.assert_not_called()
                    temporary.assert_not_called()
                else:
                    prepare.assert_called_once()
                if point == "current_owner":
                    inputs.assert_not_called()
                self.assertEqual(code, 2)
                report = json.loads(output.getvalue())
                self.assertTrue(report["deadline_exceeded"])
                self.assertEqual(report["terminal"]["outcome"], "DEADLINE_EXCEEDED")
                self.assertTrue(report["descriptor_restoration"])
                self.assertEqual(report["overall_admission"], "UNQUALIFIED")
                self.assertFalse(report["original19_started"])
                if point == "source_preparation":
                    self.assertEqual(report["source_preparation"]["commands"], [])
                self.assertEqual(alarms.call_args_list, [mock.call(240), mock.call(0)])
                self.assertEqual(signals.call_args, mock.call(observer.signal.SIGALRM, "CONTROL_OLD_HANDLER"))
        deadline = observer.HostedPrerequisiteDeadline
        self.assertFalse(issubclass(deadline, (OSError, ValueError)))
        base = Namespace(capture_selector=mock.Mock(side_effect=deadline("CONTROL_ONLY")))
        with self.assertRaises(deadline):
            observer.hosted_pin_receiving(base, "/CONTROL_ONLY", {}, {})
        provider = Namespace(_validate_nss=mock.Mock(side_effect=deadline("CONTROL_ONLY")))
        with self.assertRaises(deadline):
            observer.hosted_nss_receiving(provider, {}, {}, dict(uid=0, euid=0, gid=0, egid=0))
        base = Namespace(capture_selector=mock.Mock(return_value={"kind": "MISSING"}),
            SPEC={"python_target": "/CONTROL_ONLY", "runtime_pins": {"/CONTROL_ONLY": {"sha256": "0" * 64}}},
            _PYTHON_ALIASES=(), _NSCD=())
        provider = Namespace(SPEC={"startup_pins": {}, "native_pins": {}}, _ABSENT=(),
            _validate_nss=mock.Mock(), _startup=mock.Mock(side_effect=deadline("CONTROL_ONLY")))
        with self.assertRaises(deadline):
            observer.receive_hosted_inputs(Namespace(B=base, D=provider, CHECK=mock.Mock()))

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted prerequisites")
    def test_c5_hosted_git_setup_failures_retain_attempt_and_close_owned_child(self):
        """Break caught: selector setup fails after spawn with no retained attempt or child cleanup."""
        observer = load("hosted_git_setup_control", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        for point in ("selector", "registration", "spawn", "deadline"):
            with self.subTest(point=point), contextlib.ExitStack() as stack:
                process = Namespace(pid=424242, returncode=None, stdout=mock.Mock(), stderr=mock.Mock())
                def wait(timeout):
                    process.returncode = -9
                    return process.returncode
                process.wait = mock.Mock(side_effect=wait)
                def killpg(pid, signum):
                    self.assertEqual(pid, process.pid)
                    if signum == 0:
                        raise ProcessLookupError("CONTROL_ONLY absent group")
                kills = stack.enter_context(mock.patch.object(observer.os, "killpg", side_effect=killpg))
                stack.enter_context(mock.patch.object(observer.os, "set_blocking"))
                stack.enter_context(mock.patch.object(observer, "fds", return_value={"CONTROL": "UNCHANGED"}))
                spawn = stack.enter_context(mock.patch.object(observer.subprocess, "Popen", return_value=process))
                selector = mock.Mock()
                selector.get_map.return_value = {}
                select = stack.enter_context(mock.patch.object(observer.selectors, "DefaultSelector", return_value=selector))
                error = observer.HostedPrerequisiteDeadline if point == "deadline" else OSError
                failure = error("CONTROL_ONLY setup refusal")
                if point == "registration":
                    selector.register.side_effect = failure
                elif point == "spawn":
                    spawn.side_effect = failure
                else:
                    select.side_effect = failure
                records = []
                with self.assertRaisesRegex(error, "CONTROL_ONLY setup refusal"):
                    observer.hosted_git(["--version"], Path("/CONTROL_ONLY"), records)
                self.assertEqual(len(records), 1)
                record = records[0]
                self.assertEqual(record["exception"]["type"], error.__name__)
                self.assertFalse(record["command_received"])
                self.assertTrue(record["descriptor_restoration"])
                if point == "spawn":
                    self.assertFalse(record["process_handle_returned"])
                    self.assertEqual(record["process_creation_outcome"], "UNOBSERVED_NO_HANDLE_RETURNED")
                    self.assertIsNone(record["pid"])
                    self.assertFalse(record["wait_reaped"])
                    process.wait.assert_not_called()
                    kills.assert_not_called()
                    select.assert_not_called()
                else:
                    self.assertTrue(record["process_handle_returned"])
                    self.assertTrue(record["wait_reaped"])
                    self.assertTrue(record["owned_group_absent"])
                    self.assertEqual(kills.call_args_list,
                        [mock.call(process.pid, observer.signal.SIGKILL), mock.call(process.pid, 0)])
                    process.wait.assert_called_once_with(timeout=5)
                    process.stdout.close.assert_called_once()
                    process.stderr.close.assert_called_once()
                    if point == "registration":
                        selector.close.assert_called_once()

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted prerequisites")
    def test_c5_hosted_source_preparation_uses_genuine_complete_clone(self):
        """Break caught: shallow/shared source or wrong commit is promoted into current inputs."""
        observer = load("hosted_source_preparation_control", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        prepare = getattr(observer, "prepare_hosted_source", None)
        self.assertTrue(callable(prepare), "genuine hosted standalone source preparation is absent")
        with tempfile.TemporaryDirectory(prefix="c5-hosted-clone-") as temporary:
            fixture = Path(temporary) / "fixture"
            output = Path(temporary) / "received"
            fixture.mkdir(mode=0o700)
            output.mkdir(mode=0o700)
            environment = dict(observer.ENV, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
            def git(*arguments):
                return subprocess.run(["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                    "-c", "user.name=C5 source control", "-c", "user.email=c5-source-control@example.invalid",
                    "-C", str(fixture), *arguments], env=environment, check=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
            # A tiny genuine Git fixture; no product repository commit or native claim.
            git("init")
            (fixture / "input.txt").write_bytes(b"source-control\n")
            git("add", "input.txt")
            git("commit", "-m", "Disposable source-control fixture")
            expected = git("rev-parse", "HEAD").decode().strip()
            records = []
            with mock.patch.object(observer, "HOSTED_SOURCE_URL", fixture.as_uri()):
                try:
                    result = prepare(fixture, output, expected, records=records)
                except ValueError as exc:
                    self.fail(str(exc) + "; actual command prefix: " + json.dumps(records[-1:]))
            source = Path(result["path"])
            self.assertEqual(result["source_commit"], expected)
            self.assertFalse((source / ".git/shallow").exists())
            self.assertFalse((source / ".git/objects/info/alternates").exists())
            self.assertTrue(result["clean"])
            self.assertTrue(result["complete_objects"])
            self.assertTrue(all(item["wait_reaped"] and item["owned_group_absent"] for item in result["commands"]))
            original = load("hosted_source_namespace_owner", ROOT / "scripts/load-work-graph-c5-executor.py")
            owner = original._Engine(original.CURRENT_PROFILE).load()
            objects = {}
            captured = owner.B.complete_source(source, objects)
            try:
                owner.P.validate_git_namespace(captured["state"], objects)
            except ValueError as exc:
                import configparser
                config = configparser.RawConfigParser()
                config.read_string(objects[captured["state"]["files"][".git/config"]["sha256"]].decode())
                self.fail(str(exc) + "; fresh config keys: " + json.dumps({s: list(config[s]) for s in config.sections()}))
            self.assertIn(".git/config", captured["state"]["files"])
            self.assertNotIn(b"extraheader", objects[captured["state"]["files"][".git/config"]["sha256"]])

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted prerequisites")
    def test_c5_hosted_source_refuses_alias_and_unbound_expected_identity(self):
        """Break caught: preparation mutates the executing source or accepts an unbound ref."""
        observer = load("hosted_source_guard_control", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        prepare = getattr(observer, "prepare_hosted_source", None)
        self.assertTrue(callable(prepare), "genuine hosted standalone source preparation is absent")
        with mock.patch("subprocess.Popen", side_effect=AssertionError("refusal dispatched Git")):
            with self.assertRaisesRegex(ValueError, "source/output"):
                prepare(ROOT, ROOT / "must-not-be-created", "a" * 40)
            with tempfile.TemporaryDirectory(prefix="c5-hosted-invalid-ref-") as temporary:
                with self.assertRaisesRegex(ValueError, "expected source commit"):
                    prepare(ROOT, Path(temporary), "refs/heads/main")

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted prerequisites")
    def test_c5_hosted_input_report_cannot_promote_a_selected_pin_red(self):
        """Break caught: aggregate receiving hides a literal startup mismatch or grants admission."""
        observer = load("hosted_input_report_control", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        receive = getattr(observer, "receive_hosted_inputs", None)
        self.assertTrue(callable(receive), "hosted selected-input receiving is absent")
        current = observer.hosted_current_owner(ROOT)
        original = current.B.capture_selector
        def changed(name, objects, **kwargs):
            observed = original(name, objects, **kwargs)
            if str(name) == "/etc/ld.so.cache" and observed["kind"] == "FILE":
                observed = dict(observed, sha256="0" * 64)
            return observed
        with mock.patch.object(current.B, "capture_selector", side_effect=changed), \
                mock.patch("subprocess.Popen", side_effect=AssertionError("host input reader dispatched")):
            result = receive(current)
        cache = next(item for item in result["pins"] if item["path"] == "/etc/ld.so.cache")
        self.assertFalse(cache["match"])
        self.assertFalse(result["unchanged_owner_full_startup"]["match"])
        self.assertEqual(result["overall_admission"], "UNQUALIFIED")
        self.assertFalse(result["provider_acquired"])
        self.assertFalse(result["native_admission"])

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted launcher prerequisite")
    def test_c5_hosted_package_pin_refuses_before_archive_parsing(self):
        owner = load("c5_hosted_package_pin", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        decode = getattr(owner, "decode_hosted_launcher", None)
        self.assertTrue(callable(decode), "bounded hosted launcher prerequisite is absent")
        with mock.patch.object(owner, "hosted_archive_data", side_effect=AssertionError("unpinned package parsed")):
            for raw in (b"", b"x" * 50178, b"x" * 50179):
                with self.subTest(size=len(raw)), self.assertRaisesRegex(ValueError, "package pin"):
                    decode(raw)

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted launcher prerequisite")
    def test_c5_hosted_archive_refuses_ambiguous_or_truncated_members(self):
        owner = load("c5_hosted_archive", ROOT / "scripts/qualify-work-graph-c5-setup.py")

        def ar(rows):
            out = bytearray(b"!<arch>\n")
            for name, raw in rows:
                out.extend((name.ljust(16) + "0".ljust(12) + "0".ljust(6)
                            + "0".ljust(6) + "100644".ljust(8) + str(len(raw)).ljust(10) + "`\n").encode())
                out.extend(raw + (b"\n" if len(raw) % 2 else b""))
            return bytes(out)

        rows = [("debian-binary", b"2.0\n"), ("control.tar.zst", b"control"), ("data.tar.zst", b"data")]
        self.assertEqual(owner.hosted_archive_data(ar(rows)), b"data")
        bad = [b"bad", ar(rows)[:-1], ar(rows + [rows[-1]]), ar(rows[::-1]),
               ar([(rows[0][0], b"3.0\n")] + rows[1:]), ar(rows[:2] + [("elsewhere", b"data")])]
        for raw in bad:
            with self.subTest(size=len(raw)), self.assertRaises(ValueError):
                owner.hosted_archive_data(raw)

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted launcher prerequisite")
    def test_c5_hosted_download_is_fixed_bounded_and_refuses_redirects(self):
        owner = load("c5_hosted_download", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.status = 200; response.geturl.return_value = owner.HOSTED_PACKAGE_URL
        response.headers = {"Content-Length": "50178"}; response.read.return_value = b"bounded-response-control"
        opener = mock.MagicMock(); opener.open.return_value = response
        with mock.patch("urllib.request.build_opener", return_value=opener) as build:
            self.assertEqual(owner.hosted_download(), b"bounded-response-control")
            request = opener.open.call_args.args[0]
            self.assertEqual(request.full_url, owner.HOSTED_PACKAGE_URL)
            self.assertEqual(opener.open.call_args.kwargs, {"timeout": 10})
            response.read.assert_called_once_with(50179)
            with self.assertRaisesRegex(ValueError, "redirect"):
                build.call_args.args[0]().redirect_request(None, None, 302, None, {}, "https://elsewhere.invalid/")
            for status, url, size in [(201, owner.HOSTED_PACKAGE_URL, "50178"),
                                      (200, "https://elsewhere.invalid/", "50178"),
                                      (200, owner.HOSTED_PACKAGE_URL, "50179")]:
                response.status = status; response.geturl.return_value = url
                response.headers = {"Content-Length": size}; response.read.reset_mock()
                with self.assertRaises(ValueError):
                    owner.hosted_download()
                response.read.assert_not_called()

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted launcher prerequisite")
    def test_c5_hosted_zstd_refuses_errors_and_output_overflow(self):
        owner = load("c5_hosted_zstd", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        raw = b"constructed compressed-input control"
        package_pin = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        library = mock.MagicMock()
        with mock.patch.object(owner, "HOSTED_PACKAGE_PIN", package_pin), \
                mock.patch.object(owner, "hosted_archive_data", return_value=b"compressed"), \
                mock.patch.object(owner, "hosted_tar_launcher", side_effect=AssertionError("unbounded tar parsed")), \
                mock.patch("ctypes.CDLL", return_value=library) as opened:
            for size, error in [(0, 0), (1048577, 0), (18446744073709551615, 1)]:
                library.ZSTD_decompress.return_value = size; library.ZSTD_isError.return_value = error
                with self.subTest(size=size), self.assertRaisesRegex(ValueError, "zstd"):
                    owner.decode_hosted_launcher(raw)
                self.assertEqual(library.ZSTD_decompress.call_args.args[1], 1048576)
            self.assertEqual(opened.call_args.args, ("/lib/x86_64-linux-gnu/libzstd.so.1",))
            opened.side_effect = OSError("selected installed library unavailable")
            with self.assertRaisesRegex(OSError, "unavailable"):
                owner.decode_hosted_launcher(raw)

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted launcher prerequisite")
    def test_c5_hosted_tar_selects_only_one_exact_regular_launcher(self):
        import tarfile
        owner = load("c5_hosted_tar", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        payload = b"constructed parser control; no original-provider credit"
        pin = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}

        def archive(name="./usr/bin/bwrap", mode=0o755, kind=tarfile.REGTYPE, duplicate=False, data=payload):
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode="w") as tar:
                for _ in range(2 if duplicate else 1):
                    member = tarfile.TarInfo(name); member.mode = mode; member.type = kind
                    member.uid = member.gid = 0; member.size = len(data) if kind == tarfile.REGTYPE else 0
                    member.linkname = "/elsewhere" if kind != tarfile.REGTYPE else ""
                    tar.addfile(member, io.BytesIO(data) if kind == tarfile.REGTYPE else None)
            return buf.getvalue()

        with mock.patch.object(owner, "PIN", pin):
            self.assertEqual(owner.hosted_tar_launcher(archive()), payload)
            for raw in (archive(name="usr/bin/bwrap"), archive(mode=0o4755), archive(kind=tarfile.SYMTYPE),
                        archive(duplicate=True), archive(data=payload + b"x"), archive(data=b"x" * len(payload)),
                        b"x" * (1048576 + 1), b"invalid tar"):
                with self.subTest(size=len(raw)), self.assertRaises(ValueError):
                    owner.hosted_tar_launcher(raw)

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted launcher prerequisite")
    def test_c5_hosted_launcher_write_is_exclusive_and_read_back(self):
        owner = load("c5_hosted_write", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        payload = b"constructed exclusive-write control; no original-provider credit"
        pin = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
        with tempfile.TemporaryDirectory(prefix="c5-launcher-write-") as tmp, mock.patch.object(owner, "PIN", pin):
            parent = os.open(tmp, os.O_RDONLY | os.O_DIRECTORY)
            try:
                result = owner.write_hosted_launcher(parent, payload)
                target = Path(tmp) / "bwrap"
                self.assertEqual(target.read_bytes(), payload)
                self.assertEqual(target.stat().st_mode & 0o7777, 0o755)
                self.assertEqual(result["sha256"], pin["sha256"])
                with self.assertRaises(FileExistsError):
                    owner.write_hosted_launcher(parent, payload)
                self.assertEqual(target.read_bytes(), payload)
                target.unlink(); target.symlink_to(Path(tmp) / "unselected")
                with self.assertRaises(FileExistsError):
                    owner.write_hosted_launcher(parent, payload)
                self.assertFalse((Path(tmp) / "unselected").exists())
                target.unlink()
                with self.assertRaisesRegex(ValueError, "launcher pin"):
                    owner.write_hosted_launcher(parent, payload + b"x")
                self.assertFalse(target.exists())
                os.chmod(tmp, 0o777)
                with self.assertRaisesRegex(ValueError, "parent metadata"):
                    owner.write_hosted_launcher(parent, payload)
                self.assertFalse(target.exists())
                os.chmod(tmp, 0o700)
            finally:
                os.close(parent)

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted launcher prerequisite")
    def test_c5_hosted_launcher_handles_short_write_and_refuses_stalled_write(self):
        owner = load("c5_hosted_short_write", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        payload = b"constructed short-write control"
        pin = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
        real_write = os.write
        with tempfile.TemporaryDirectory(prefix="c5-launcher-short-") as tmp, mock.patch.object(owner, "PIN", pin):
            parent = os.open(tmp, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with mock.patch.object(owner.os, "write", side_effect=lambda fd, raw: real_write(fd, raw[:3])):
                    owner.write_hosted_launcher(parent, payload)
                self.assertEqual((Path(tmp) / "bwrap").read_bytes(), payload)
                (Path(tmp) / "bwrap").unlink()
                with mock.patch.object(owner.os, "write", return_value=0), self.assertRaisesRegex(ValueError, "stalled"):
                    owner.write_hosted_launcher(parent, payload)
                self.assertEqual((Path(tmp) / "bwrap").read_bytes(), b"")
            finally:
                os.close(parent)

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted launcher prerequisite")
    def test_c5_hosted_provision_requires_root_before_fetch_or_target_access(self):
        owner = load("c5_hosted_authority", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        with mock.patch.object(owner.os, "geteuid", return_value=1001), \
                mock.patch.object(owner.os, "getegid", return_value=1001), \
                mock.patch.object(owner, "hosted_download", side_effect=AssertionError("unadmitted network")), \
                mock.patch.object(owner, "hosted_parent", side_effect=AssertionError("unadmitted target")):
            with self.assertRaisesRegex(ValueError, "root"):
                owner.provision_hosted_launcher()

    def test_native_binding_lookup_refuses_ambiguous_json(self):
        owner = load("native_binding_json", PEER / "host-session-binding.py")
        with tempfile.TemporaryDirectory(prefix="native-binding-json-") as temporary:
            root = Path(temporary)
            store, repo = root / "store", root / "repo"
            run, common = repo / "runs" / "fixture", repo / ".git"
            run.mkdir(parents=True)
            common.mkdir()
            key = dict(store=str(store), host_id="codex", host_session_id="fixture-session")

            def invoke(function, **arguments):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    function(Namespace(**arguments))
                return json.loads(output.getvalue())

            invoke(owner.command_init, store=str(store), owner_id="fixture-owner")
            bound = invoke(owner.command_bind, **key, owner_id="fixture-owner",
                           controller_id="fixture-controller", claim_id="1" * 32,
                           explicit_run_root=str(run), repository_identity=str(repo),
                           git_common_directory_identity=str(common), worktree_identity=str(repo),
                           activation_event_id="fixture-event", activation_receipt="fixture-receipt",
                           continuity_generation="G0002", continuity_receipt="fixture-continuity")
            self.assertFalse(bound["host_activation_proven"])
            cases = (
                (owner.owner_path(store), '"trusted": true', '"trusted": false, "trusted": true'),
                (owner.session_index_path(store, key["host_session_id"]),
                 '"host_session_id": "fixture-session"',
                 '"host_session_id": "foreign", "host_session_id": "fixture-session"'),
                (owner.state_path(store, key["host_id"], key["host_session_id"]),
                 '"controller_id": "fixture-controller"',
                 '"controller_id": "foreign", "controller_id": "fixture-controller"'),
            )
            for target, needle, ambiguous in cases:
                with self.subTest(target=target.name):
                    original = target.read_bytes()
                    self.assertEqual(original.count(needle.encode()), 1)
                    target.write_bytes(original.replace(needle.encode(), ambiguous.encode()))
                    output = io.StringIO()
                    try:
                        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as refusal:
                            owner.command_lookup(Namespace(**key))
                        self.assertEqual(refusal.exception.code, 2)
                        result = json.loads(output.getvalue())
                        self.assertEqual(result["status"], "UNAVAILABLE")
                        self.assertIn("duplicate JSON member", result["error"])
                    finally:
                        target.write_bytes(original)
                    self.assertEqual(invoke(owner.command_lookup, **key), bound)

    def test_nonprotected_fixed_policy_does_not_require_owned_stdio_capture(self):
        owner = load("nonprotected_policy_owner", PEER / "compaction-source-owner-codex-app.py")
        observation = load("nonprotected_policy_observation", PEER / "compaction-result-observation.py")
        helpers = load("nonprotected_policy_helpers", PEER / "bounded_source_owner.py")
        names = ("compaction-source-owner-codex-app.py", "codex-recovery-native-reader.py")
        pins = {str(Path("implementaudit/scripts") / name): hashlib.sha256((PEER / name).read_bytes()).hexdigest()
                for name in names}
        fixture_pin = {"path": str(PEER / names[0]), "bytes": (PEER / names[0]).stat().st_size,
                       "sha256": pins[str(Path("implementaudit/scripts") / names[0])]}
        # Only policy construction is under test. No private selection, native
        # process, canonical episode or accepting pending store is admitted.
        selected = dict(profile_id=owner.NONPROTECTED_PROFILE,
                        episode_owner={"module_pin": fixture_pin},
                        native_version="codex-cli 0.164.0-alpha.11.1", cli_version="0.163.0-alpha.10.2",
                        desktop_version="unadmitted-fixture", native_executable=fixture_pin,
                        desktop_executable=fixture_pin, desktop_asar=fixture_pin, config_file=fixture_pin)
        self.assertIsNone(owner.selected_source_pin_v1())
        with mock.patch.object(owner, "_np_runtime", return_value=(selected, None, None, helpers, None)) as runtime, \
                mock.patch.object(owner, "NONPROTECTED_SELECTION_PIN", fixture_pin):
            policy = owner.nonprotected_fixed_policy(observation, pins)
            runtime.assert_called_once_with(observation, pins)
            self.assertEqual(policy["descriptor"]["exact_host_tuple"]["source_header_cli_version"],
                             "0.163.0-alpha.10.2")
            self.assertEqual(policy["descriptor"]["exact_host_tuple"]["child_source_header_cli_version"],
                             "0.164.0-alpha.11.1")
            self.assertEqual(policy["descriptor"]["profile_id"], owner.NONPROTECTED_PROFILE)
            self.assertNotIn("producer_dependencies", policy["descriptor"]["provider_selection"])
            self.assertEqual(policy["policy_digest"], observation.digest(observation.canonical(
                {key: value for key, value in policy.items() if key != "policy_digest"})))
            with mock.patch.object(owner, "capture", {"schema": "implementaudit.owned-stdio-live-acquisition.v1"}, create=True):
                self.assertEqual(owner.nonprotected_fixed_policy(observation, pins), policy)
            changed = dict(pins)
            changed[str(Path("implementaudit/scripts") / names[0])] = "0" * 64
            with self.assertRaisesRegex(ValueError, "NONPROTECTED_PIN_CHANGED"):
                owner.nonprotected_fixed_policy(observation, changed)
        self.assertIsNone(owner.selected_source_pin_v1())

    def test_documented_peer_materialization_supplies_exact_episode_owner_sibling(self):
        with tempfile.TemporaryDirectory(prefix="nonprotected-source-overlay-") as temporary:
            root = Path(temporary)
            scripts = root / "skills/implementaudit/scripts"
            shutil.copytree(CORE, scripts, ignore=shutil.ignore_patterns("__pycache__"))
            for group in ("native-runtime", "route-graph"):
                manifest = json.loads((ROOT / "source-peers" / group / "SOURCE_MANIFEST.json").read_bytes())
                for entry in manifest["files"]:
                    raw = (ROOT / entry["path"]).read_bytes()
                    self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (entry["bytes"], entry["sha256"]))
                    target = root / entry["materialized_path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(raw)
                    target.chmod(int(entry["mode"], 8) & 0o777)
            owner = load("materialized_nonprotected_owner", scripts / "compaction-source-owner-codex-app.py")
            route = scripts / "route-transaction.py"
            raw = route.read_bytes()
            pin = dict(path=str(route), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
            module = owner._np_module(pin, "route-transaction.py")
            self.assertEqual(Path(module.__file__).parent, owner.HERE)
            self.assertTrue(callable(module.read_current_episode_binding_v1))
            self.assertIsNone(owner.selected_source_pin_v1())
            foreign = dict(pin, path=str(ROOT / "source-peers/route-graph/skills/implementaudit/scripts/route-transaction.py"))
            with self.assertRaisesRegex(ValueError, "NONPROTECTED_MODULE_OWNER_PATH"):
                owner._np_module(foreign, "route-transaction.py")
            changed = b"raise AssertionError('UNSELECTED_ROUTE_EXECUTED')\n"
            route.write_bytes(changed + b"#" * (len(raw) - len(changed)))
            with self.assertRaisesRegex(ValueError, "NONPROTECTED_PIN_CHANGED"):
                owner._np_module(pin, "route-transaction.py")
            route.unlink()
            with self.assertRaises(FileNotFoundError):
                owner._np_module(pin, "route-transaction.py")

    @unittest.skipUnless(os.name == "posix", "fixed C5 no-follow source acquisition")
    def test_original_c5_profile_cannot_admit_the_current_composite(self):
        owner = load("strict_original_c5", ROOT / "scripts/load-work-graph-c5-executor.py")
        with tempfile.TemporaryDirectory(prefix="c5-profile-refusal-") as temp:
            output = Path(temp) / "unallocated"
            with mock.patch.object(owner._Engine, "load") as execute:
                with self.assertRaisesRegex(ValueError, "Unsupported fixed C5 execution member: scripts/qualify-work-graph-prefix.py"):
                    owner.create_genuine_c5_session(ROOT, output, expected_source={})
            execute.assert_not_called()
            self.assertFalse(output.exists())

    @unittest.skipUnless(sys.platform == "linux" and hasattr(os, "pidfd_open"), "fixed C5 Linux pidfd constructor")
    def test_current_c5_entry_binds_current_inputs_before_execution(self):
        """Break caught: implicit historical fallback or stale compiler/provider binding."""
        owner = load("explicit_current_c5", ROOT / "scripts/load-work-graph-c5-executor.py")
        create = getattr(owner, "create_current_composite_c5_session_v1", None)
        self.assertTrue(callable(create), "explicit current C5 entry is absent")
        with tempfile.TemporaryDirectory(prefix="c5-current-inputs-") as temporary, \
                mock.patch("subprocess.Popen", side_effect=AssertionError("input selection dispatched a producer")):
            output = Path(temporary) / "evidence"
            # Schema-valid comparison data only; this constructor test never runs
            # source identity acquisition or treats this pair as a real commit.
            session = create(ROOT, output, expected_source={"source_commit": "0" * 40, "source_tree": "1" * 40})
            try:
                selected = type(session).__init__.__globals__
                base, provider = selected["B"], selected["D"]
                self.assertEqual(selected["PROFILE"], "FIXED_GENUINE_C5_PRODUCER_EFFECT_CURRENT_COMPOSITE_20261027_V1")
                self.assertEqual(base.PROFILE, "CURRENT_COMPOSITE_SYSTEM_PYTHON312_DATA_ONLY_20261027_V1")
                self.assertEqual(provider.PROFILE, "CURRENT_COMPOSITE_FIXED_PACKAGE_VENV_PYTHON312_DATA_ONLY_20261027_V1")
                self.assertEqual(str(provider.VENV), "/opt/implementaudit-c5-current-python312-v1")
                self.assertEqual(provider.SITE, "/opt/implementaudit-c5-current-python312-v1/lib/python3.12/site-packages")
                self.assertEqual(provider._ENVIRONMENT["PATH"], "/opt/implementaudit-c5-current-python312-v1/bin:/usr/bin:/bin")
                self.assertEqual(provider._ALIASES[:3], tuple(
                    "/opt/implementaudit-c5-current-python312-v1/bin/" + name for name in ("python", "python3", "python3.12")))
                compiler_sha = hashlib.sha256((ROOT / "skills/implementaudit/scripts/compile-work-graph.py").read_bytes()).hexdigest()
                self.assertEqual(hashlib.sha256(selected["Q"].LOADED_COMPILER).hexdigest(), compiler_sha)
                self.assertEqual(selected["G"].COMPILER_SHA, compiler_sha)
                state = {"files": {name: {"sha256": hashlib.sha256((ROOT / name).read_bytes()).hexdigest()}
                                   for name in set(base.SPEC["programs"]) | set(base.SPEC["payload_sources"])}}
                contract = base._producer_contract(state)
                self.assertEqual(contract["expected_archive_members"], {"canonical_plugin": 75, "standalone_compatibility": 72})
                self.assertEqual(len([name for name in state["files"] if name.startswith("skills/implementaudit/")]), 66)
                self.assertTrue(output.is_dir())
                self.assertEqual(list(output.iterdir()), [])
                self.assertFalse(session.attempted)
            finally:
                session.close()

    @contextlib.contextmanager
    def current_c5_source_copy(self):
        """Real bounded source inputs for refusals; no fabricated Git identity."""
        owner = load("current_c5_copy_owner", ROOT / "scripts/load-work-graph-c5-executor.py")
        self.assertTrue(callable(getattr(owner, "create_current_composite_c5_session_v1", None)),
                        "explicit current C5 entry is absent")
        selection = json.loads((ROOT / "fixtures/work-graph-c5-inputs/execution-current-composite-python312.json").read_bytes())
        members = {owner.LOADER, *owner.CURRENT_PINS, *selection["programs"], *selection["payload_sources"]}
        with tempfile.TemporaryDirectory(prefix="c5-current-source-") as temporary:
            root = Path(temporary) / "source"
            root.mkdir()
            for name in sorted(members):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            yield root, Path(temporary) / "evidence"

    def test_current_c5_unknown_selection_refuses(self):
        """Break caught: a caller can supply an unreviewed source policy."""
        owner = load("unknown_current_c5", ROOT / "scripts/load-work-graph-c5-executor.py")
        self.assertTrue(callable(getattr(owner, "create_current_composite_c5_session_v1", None)),
                        "explicit current C5 entry is absent")
        for value in ("unreviewed", {"pins": {}}, None):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "Unknown fixed C5 execution profile"):
                owner._Engine(value)

    @unittest.skipUnless(os.name == "posix", "fixed C5 source loading")
    def test_current_c5_runtime_layout_refuses_private_mount_shadowing(self):
        """Break caught: a later private mount hides selected runtime bytes/aliases."""
        owner = load("current_c5_layout", ROOT / "scripts/load-work-graph-c5-executor.py")
        selected = owner._Engine(owner.CURRENT_PROFILE).load()
        def layout(logical, resolved=None, links=None):
            resolved = resolved or logical
            # Constructed layout inputs only, never physical custody evidence.
            # Match the selected directory policy so it cannot mask the
            # independent private-mount collision predicate under test.
            modes = {"/": 0o755, **selected.SPEC["directory_mode_policy"]["exceptions"]}
            topology = {"directories": {name: ["0", "0", 0o40000 | mode, 1, 0, 0, 0, 0, 0]
                                        for name, mode in modes.items()},
                        "links": {name: {"target": target} for name, target in (links or {}).items()},
                        "selected": {logical: {"kind": "FILE", "resolved": resolved}}}
            runtime = {"files": {logical: {"resolved": resolved, "bytes": 1,
                                           "sha256": hashlib.sha256(b"x").hexdigest(), "mode": 0o644}}}
            return selected.runtime_layout(runtime, topology)
        for path in ("/opt/c5-provider/file", "/tmp-provider/file"):
            self.assertIn(path, layout(path)["files"])
        for mount in ("/work", "/c5-work", "/tmp"):
            with self.subTest(mount=mount), self.assertRaises(ValueError):
                layout(mount + "/c5-provider/file")
        with self.assertRaises(ValueError):
            layout("/usr/lib/c5-provider/file", "/tmp/c5-provider/file",
                   {"/usr/lib/c5-provider": "/tmp/c5-provider"})
        with self.assertRaises(ValueError):
            layout("/tmp/c5-provider/file", "/opt/c5-provider/file",
                   {"/tmp/c5-provider": "/opt/c5-provider"})

    @unittest.skipUnless(os.name == "posix" and Path("/opt/implementaudit-c5-current-python312-v1").is_dir(),
                         "fixed current provider data input absent; no provider-layout credit")
    def test_current_c5_actual_provider_layout_preserves_bytes_and_ancestry(self):
        """Break caught: the selected real provider is hidden or its alias/modes change."""
        owner = load("current_c5_provider_layout", ROOT / "scripts/load-work-graph-c5-executor.py")
        with mock.patch("subprocess.Popen", side_effect=AssertionError("provider layout dispatched a producer")):
            selected = owner._Engine(owner.CURRENT_PROFILE).load()
            self.assertEqual(selected.D.VENV, Path("/opt/implementaudit-c5-current-python312-v1"))
            objects = {}
            tree = selected.D._capture_tree(selected.D.VENV, objects)
            runtime = {"files": {str(selected.D.VENV / name): row for name, row in tree["files"].items()},
                       "directories": {}, "provider": {"installation": tree}}
            topology = selected.runtime_topology(runtime)
            layout = selected.runtime_layout(runtime, topology)
            self.assertEqual(len(layout["files"]), 22)
            self.assertEqual(layout["directories"]["/opt"], 0o755)
            self.assertEqual(layout["links"]["/opt/implementaudit-c5-current-python312-v1/lib64"], "lib")
            self.assertEqual(layout["files"]["/opt/implementaudit-c5-current-python312-v1/bin/python"]["sha256"],
                             "a92f0f95e883390c7256b2e441484aac06b1002dbe1d924141a77c8d82f96223")
            self.assertEqual(tree, selected.D._capture_tree(selected.D.VENV, {}))
            # Only this actual provider subset is represented; no complete
            # execution image, source stage, bootstrap or session run is made.

    @unittest.skipUnless(os.name == "posix", "fixed C5 no-follow source acquisition")
    def test_current_c5_changed_source_or_selection_refuses_before_output(self):
        """Break caught: current branch omits a code/fixture pin or admits late."""
        cases = ("scripts/qualify-work-graph-prefix.py",
                 "fixtures/work-graph-c5-inputs/execution-current-composite-python312.json",
                 "fixtures/work-graph-c5-inputs/package-current-venv-python312.json",
                 "fixtures/work-graph-c5-inputs/genuine-current-execution-profile.json")
        for member in cases:
            with self.subTest(member=member), self.current_c5_source_copy() as (root, output):
                path = root / member
                path.write_bytes(path.read_bytes() + b"\n")
                owner = load("tampered_current_c5", root / "scripts/load-work-graph-c5-executor.py")
                with mock.patch("subprocess.Popen", side_effect=AssertionError("changed input dispatched a producer")):
                    with self.assertRaisesRegex(ValueError, "Unsupported fixed C5 execution member"):
                        owner.create_current_composite_c5_session_v1(root, output,
                            expected_source={"source_commit": "0" * 40, "source_tree": "1" * 40})
                self.assertFalse(output.exists())

    @unittest.skipUnless(sys.platform == "linux" and hasattr(os, "pidfd_open"), "fixed C5 Linux pidfd constructor")
    def test_current_c5_actual_program_and_payload_drift_refuse_acquisition(self):
        """Break caught: selected producer/payload data bypasses pre-dispatch acquisition."""
        for change, message in (("program", "C5 original producer source differs"),
                                ("payload", "C5 actual package source selector population differs")):
            with self.subTest(change=change), self.current_c5_source_copy() as (root, output):
                if change == "program":
                    path = root / "scripts/package-contract.py"
                    path.write_bytes(path.read_bytes() + b"\n")
                else:
                    (root / "skills/implementaudit/scripts/validate-audit-implement-return.py").unlink()
                owner = load("drifted_current_c5", root / "scripts/load-work-graph-c5-executor.py")
                with mock.patch("subprocess.Popen", side_effect=AssertionError("drifted input dispatched a producer")):
                    session = owner.create_current_composite_c5_session_v1(root, output,
                        expected_source={"source_commit": "0" * 40, "source_tree": "1" * 40})
                    try:
                        with self.assertRaisesRegex(ValueError, message):
                            session._acquire()
                        self.assertTrue(output.is_dir())
                        self.assertFalse(session.attempted)
                    finally:
                        session.close()

    @unittest.skipUnless(sys.platform == "linux" and hasattr(os, "pidfd_open")
                         and Path("/opt/implementaudit-c5-current-python312-v1").is_dir(),
                         "fixed current provider data input absent; no provider-scope credit")
    def test_current_c5_actual_provider_drift_refuses_acquisition(self):
        """Break caught: provider byte substitution reaches producer dispatch."""
        with self.current_c5_source_copy() as (root, output):
            owner = load("provider_drift_current_c5", root / "scripts/load-work-graph-c5-executor.py")
            with mock.patch("subprocess.Popen", side_effect=AssertionError("changed provider dispatched a producer")):
                session = owner.create_current_composite_c5_session_v1(root, output,
                    expected_source={"source_commit": "0" * 40, "source_tree": "1" * 40})
                try:
                    provider = type(session).__init__.__globals__["D"]
                    copied = output.parent / "provider-copy"
                    shutil.copytree(provider.VENV, copied, symlinks=True)
                    changed = copied / "lib/python3.12/site-packages/zopfli/_version.py"
                    changed.write_bytes(changed.read_bytes() + b"\n")
                    capture_tree = provider._capture_tree
                    # Redirect only the filesystem subject to a real disposable
                    # copy; all provider byte/namespace/RECORD predicates stay real.
                    with mock.patch.object(provider, "_capture_tree", side_effect=lambda _root, objects: capture_tree(copied, objects)):
                        with self.assertRaisesRegex(ValueError, "C5 provider file differs from fixed installed bytes"):
                            session._acquire()
                    self.assertTrue(output.is_dir())
                    self.assertFalse(session.attempted)
                finally:
                    session.close()

    def test_retained_native_dependency_and_new_core_profiles_are_distinct(self):
        manifest = json.loads((ROOT / "source-peers/native-runtime/SOURCE_MANIFEST.json").read_bytes())
        retained = next(row for row in manifest["files"]
                        if row["path"].endswith("/claim-run-rotation.py"))
        raw = (ROOT / retained["path"]).read_bytes()
        self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()),
                         (246657, 'bc862f87428e86c608ddc5fe31ad8a3e2c8324b52c09ba379163db160ad70e93'))
        self.assertEqual(retained["materialized_path"], "skills/implementaudit/scripts/claim-run-rotation.py")
        self.assertNotIn(retained["materialized_path"], [row["path"] for row in manifest["frozen_core_dependencies"]])
        transport = load("retained_core_transport", ROOT / "scripts/work-graph-continuity-transport.py")
        profile = transport.SOURCE_PROFILES_V1['composite-20261028-terminal-inventory-v1-core']
        self.assertEqual(transport.SOURCE_PROFILES_V1['composite-20261028-original14-dg17-ledger-v1'][2][1:3],
                         (246657, '908cce5054dc23a9e74b6af695204fc6d9889681611311c7136f087fe0be1663'))
        self.assertEqual(transport.SOURCE_PROFILES_V1['composite-20261028-core-dg17-ledger-v1'][2][1:3],
                         (259408, 'c91e7c3aa243919c4cdb398f999f28734f1a630511a99f6b1aa9dc477b2fae3c'))
        self.assertEqual(transport.SOURCE_PROFILES_V1['composite-20261027-core-dg08-acquisition-v1'][1][1:3],
                         (113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283'))
        self.assertEqual(transport.SOURCE_PROFILES_V1['composite-20261027-original14-dg08-acquisition-v1'][1][1:3],
                         (113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283'))
        self.assertEqual(transport.SOURCE_PROFILES_V1["composite-20261025-original14"][2],
                         ("claim-run-rotation.py", 246657, "4dbbd07b5a792289c13c1225a8099900682b3657396f60f4b74867502cbadf97", None))
        self.assertEqual(transport.SOURCE_PROFILES_V1['composite-20261026-original14-preparation-template-v1'][2][1:3], (246657, '31e30b564e83db80c11c18b3bf83eab9d901bf089af7dd7ebd2e7d823f5105f8'))
        self.assertNotEqual(profile, transport.SOURCE_PROFILES_V1["composite-20261026-core-cas-phases-v1"])
        observed = tuple((name, len((CORE / name).read_bytes()),
                          hashlib.sha256((CORE / name).read_bytes()).hexdigest(), mode)
                         for name, _, _, mode in profile)
        self.assertEqual(observed, profile)
        self.assertNotEqual(profile, transport.SOURCE_PROFILES_V1["composite-20261025-core-posix-reads"])
        self.assertNotEqual(profile, transport.SOURCE_PROFILES_V1["composite-20261025-core-retained-history-v1"])
        self.assertNotEqual(profile, transport.SOURCE_PROFILES_V1["composite-20261026-core-binder-v1"])

    def test_retained_native_profile_refuses_new_history_api_before_dispatch(self):
        peer = ROOT / "source-peers/route-graph/skills/implementaudit/scripts"
        with tempfile.TemporaryDirectory(prefix="history-source-profile-") as temp:
            repo = Path(temp).resolve()
            owner = repo / "owner"
            run = repo / "run"
            owner.mkdir()
            run.mkdir()
            for name in ("route-transaction.py", "route_request_policy.py"):
                shutil.copyfile(peer / name, owner / name)
            for name in ("claim-run.sh", "claim-run-rotation.py"):
                shutil.copyfile(PEER / name, owner / name)
            route = load("retained_history_receiver", owner / "route-transaction.py")
            prefix = "refs/implementaudit/continuity-receipts/fixture/"
            token, current = prefix + "G0002@" + "1" * 40, prefix + "G0003@" + "2" * 40
            fields = ["implementaudit.continuity-receipt.v3", "fixture", "fixture-claim", "run",
                      "G0002", "1" * 40, "refs/implementaudit/current-generations/fixture", "2" * 40,
                      *(["0" * 64] * 4), "retained-marker", prefix + "G0001@" + "3" * 40]
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured), mock.patch.object(
                    subprocess, "run", side_effect=AssertionError("unsupported profile dispatched")) as called:
                with self.assertRaises(SystemExit) as refused:
                    route.original14_retained_predecessor_v1(
                        repo, token, fields, controller="fixture", claim="fixture-claim",
                        run_identity="run", generation="G0002", current_receipt=current,
                        explicit_run_root=str(run))
                self.assertEqual(refused.exception.code, 2)
                called.assert_not_called()
            self.assertIn("exceeds its exact source bound", captured.getvalue())

    @unittest.skipUnless(os.name == "posix", "actual POSIX FIFO replacement")
    def test_route_source_replaced_by_fifo_refuses_before_read(self):
        worker = r'''
import importlib.util, os, pathlib, sys
root = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("fifo_route_loader", root / "compile-work-graph.py")
graph = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graph)
target = root / "route-transaction.py"
original_open = os.open
def replaced_open(path, flags, *args, **kwargs):
    if pathlib.Path(path) == target:
        target.unlink()
        os.mkfifo(target)
        print("FIFO_REPLACEMENT_REACHED", flush=True)
    return original_open(path, flags, *args, **kwargs)
os.open = replaced_open
try:
    graph._native_route_scope_module_v1()
except graph.WorkGraphError as error:
    print(str(error), flush=True)
else:
    raise AssertionError("nonregular route source was accepted")
'''
        peer = ROOT / "source-peers/route-graph/skills/implementaudit/scripts"
        for source in (CORE, peer):
            with self.subTest(source=source), tempfile.TemporaryDirectory(prefix="route-loader-fifo-") as temp:
                target = Path(temp)
                shutil.copyfile(source / "compile-work-graph.py", target / "compile-work-graph.py")
                for name in ("route-transaction.py", "route_request_policy.py"):
                    shutil.copyfile(peer / name, target / name)
                try:
                    result = subprocess.run([sys.executable, "-B", "-c", worker, str(target)],
                                            capture_output=True, timeout=5)
                except subprocess.TimeoutExpired as error:
                    self.fail("route source read blocked; actual stdout=" + repr(error.stdout)
                              + "; actual stderr=" + repr(error.stderr))
                self.assertEqual(result.returncode, 0, result.stderr.decode())
                self.assertIn(b"FIFO_REPLACEMENT_REACHED", result.stdout)
                self.assertIn(b"native route producer source identity changed", result.stdout)

    @unittest.skipUnless(os.name == "posix", "actual POSIX static-owner source replacement")
    def test_static_owner_source_replaced_by_fifo_refuses_before_read(self):
        worker = r'''
import importlib.util, os, pathlib, sys
path = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("static_owner_loader", path)
graph = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graph)
target = path.parents[3] / "scripts/operational-evidence.py"
original_open = os.open
def substituted_open(name, flags, *args, **kwargs):
    if pathlib.Path(name) == target:
        target.rename(target.with_suffix(".retained"))
        os.mkfifo(target)
        print("STATIC_OWNER_FIFO_REPLACEMENT", flush=True)
    return original_open(name, flags, *args, **kwargs)
os.open = substituted_open
try:
    graph._native_static_owner_module_v1()
except graph.WorkGraphError as error:
    print(str(error), flush=True)
else:
    raise AssertionError("nonregular static owner was accepted")
'''
        with tempfile.TemporaryDirectory(prefix="static-owner-fifo-") as temporary:
            target = Path(temporary)
            compiler = target / "skills/implementaudit/scripts/compile-work-graph.py"
            compiler.parent.mkdir(parents=True)
            shutil.copyfile(CORE / compiler.name, compiler)
            owner = target / "scripts/operational-evidence.py"
            owner.parent.mkdir()
            shutil.copyfile(ROOT / "scripts/operational-evidence.py", owner)
            try:
                result = subprocess.run([sys.executable, "-B", "-c", worker, str(compiler)],
                                        capture_output=True, timeout=5)
            except subprocess.TimeoutExpired as error:
                self.fail("static owner source read blocked; owned worker killed/reaped; stdout="
                          + repr(error.stdout))
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertIn(b"STATIC_OWNER_FIFO_REPLACEMENT", result.stdout)
            self.assertIn(b"native static source owner is unavailable or changed", result.stdout)

    def test_lossless_research_observation_retains_complete_original(self):
        """Fixed research snapshot coherence, not native or transitive read credit."""
        stem = "docs/research/implementaudit/r003f-r0041-pending-source-"
        original_name = stem + "qualification.json"
        carrier_name = original_name + ".gz"
        manifest_name = stem + "transport.json"
        manifest = json.loads((ROOT / manifest_name).read_bytes())
        self.assertEqual(manifest["schema"], "implementaudit.research-evidence-transport.v1")
        expected = {
            "original": (original_name, 30022077,
                         "0a35a0e973d5627493928801a3ea82df8e5a82d37fa72d6e3cf795059cb63c57",
                         "707953224788ffe951b50a265fb7c456fda76e36"),
            "carrier": (carrier_name, 5037688,
                        "ed46a9a90918a794beeaa42ceeba0b85bb14f46e72d66101443b857a30cb7941",
                        "f0663d5fbe1e9f429b062001ab6fa025742d1a31"),
        }
        captured = {}
        for role, (name, size, sha256, blob) in expected.items():
            with self.subTest(role=role):
                self.assertEqual({key: manifest[role][key] for key in
                                  ("path", "bytes", "sha256", "git_blob")},
                                 dict(path=name, bytes=size, sha256=sha256, git_blob=blob))
                path = ROOT / name
                self.assertFalse(path.is_symlink())
                self.assertTrue(path.is_file())
                self.assertEqual(path.stat().st_size, size)
                raw = path.read_bytes()
                self.assertEqual(len(raw), size)
                self.assertEqual(hashlib.sha256(raw).hexdigest(), sha256)
                self.assertEqual(hashlib.sha1(b"blob " + str(size).encode() + b"\0" + raw).hexdigest(), blob)
                captured[role] = raw
        self.assertEqual(manifest["carrier"]["format"], "gzip")
        self.assertEqual(manifest["original"]["immutable_commit"],
                         "0049ea15d4e406aa6970ef6c30ea57f58154d757")
        self.assertEqual(manifest["original"]["immutable_tree"],
                         "20d88dc9fe0d27ab364d33e58fd2b80878b38b06")
        with gzip.GzipFile(fileobj=io.BytesIO(captured["carrier"])) as stream:
            decoded = stream.read(expected["original"][1] + 1)
        self.assertEqual(decoded, captured["original"])
        site = json.loads((ROOT / "docs/portal/site.json").read_bytes())
        for names in (site["semantic_sources"], site["pages"]["research-lineage-overview"]["sources"]):
            self.assertEqual(names.count(carrier_name), 1)
            self.assertEqual(names.count(manifest_name), 1)
            self.assertNotIn(original_name, names)

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
        for old, new in (("select_claim_python() {", "unbound_selector() {"),
                         ('rotation_py="$(select_claim_python)" || {', 'rotation_py="$(foreign_selector)" || {')):
            changed = source.replace(old, new)
            self.assertNotEqual(changed, source)
            self.assertFalse(check("claim-run-rotation.py", changed))

    def test_current_pending_fixture_profile_is_exact_and_still_refuses_native_reservation(self):
        fixture = load("composite_pending_fixture", ROOT / "tests/cognition-pending-durability.py")
        pins = fixture.source_pins(ROOT)
        selected = fixture.reservation_refusal_profile(pins)
        self.assertEqual(selected["qualified_checkpoint"], "source-sha256:681b22da6ee2fc5a84cfab7547a9f0551a76c97659e6b5c5b7158ff910117c23")
        self.assertEqual(selected["stored_json_refusal"], "PENDING_STATE_JSON")
        self.assertEqual(selected["nonfinite_counter_refusal"], "PENDING_STATE_JSON_CONSTANT")
        # Historical tuples must not inherit the changed current source owners.
        prior_generic = {
            str(fixture.PEER / 'compaction-audit-pending.py'): '8c16f7f142b67eb4504ae275bf53e8ea104bb75378748402e8a4c0a31efdbc43',
            str(fixture.PEER / 'compaction-result-observation.py'): '9ea603b9d923df5c155c7a5406ee2dac21cbc8fc87ec205f978e3130fbe43345',
            str(fixture.PEER / 'compaction-source-owner-codex-app.py'): '799d468f8a98a6990c798488517ba27f273f4862d6066a9b228ab0d1c7c6a517',
            str(fixture.PEER / 'host-session-binding.py'): '62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890',
        }
        self.assertEqual(fixture.reservation_refusal_profile(prior_generic), {
            **selected,
            "qualified_checkpoint": "source-sha256:799d468f8a98a6990c798488517ba27f273f4862d6066a9b228ab0d1c7c6a517"})
        prior_current = dict(prior_generic)
        prior_current[str(fixture.PEER / "compaction-source-owner-codex-app.py")] = "2fcb390a3e4105adc1178000e736b1a09b3b5a59db03fdd744cda895a1352d04"
        self.assertEqual(fixture.reservation_refusal_profile(prior_current), {
            **selected,
            "qualified_checkpoint": "source-sha256:8c16f7f142b67eb4504ae275bf53e8ea104bb75378748402e8a4c0a31efdbc43"})
        prior_combined = dict(prior_current)
        prior_combined[str(fixture.PEER / "compaction-audit-pending.py")] = "b12a6e385bb911e54c641c8a3c56ba0d0a40819083f4444f2659c6eecd55af8c"
        self.assertEqual(fixture.reservation_refusal_profile(prior_combined), {
            "qualified_checkpoint": "f74a7c6675073af8c78f8a83ef5f3eb1476d2bfb",
            "expected_reason": "NONPROTECTED_PROJECTION_PROFILE_REQUIRED",
            "stored_json_refusal": "PENDING_STATE_JSON",
            "nonfinite_counter_refusal": "PENDING_STATE_JSON_CONSTANT"})
        historical = dict(prior_current)
        historical[str(fixture.PEER / "compaction-audit-pending.py")] = "9b5faf290e08d3df77b15d5e5301a3760c4e599d16719cf8f72e1768522ea691"
        self.assertEqual(fixture.reservation_refusal_profile(historical), {
            "qualified_checkpoint": "5d90c706518cd08f13dfbb2024e806702cae85e9",
            "expected_reason": "NONPROTECTED_PROJECTION_PROFILE_REQUIRED"})
        self.assertEqual(selected["expected_reason"], "NONPROTECTED_PROJECTION_PROFILE_REQUIRED")
        for old_pending in ("b12a6e385bb911e54c641c8a3c56ba0d0a40819083f4444f2659c6eecd55af8c",
                            "9b5faf290e08d3df77b15d5e5301a3760c4e599d16719cf8f72e1768522ea691"):
            mixed = dict(pins)
            mixed[str(fixture.PEER / "compaction-audit-pending.py")] = old_pending
            with self.subTest(mixed_pending=old_pending), self.assertRaises(AssertionError):
                fixture.reservation_refusal_profile(mixed)
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
        peer = ROOT / "source-peers/route-graph/skills/implementaudit/scripts"
        raw = (peer / "route-transaction.py").read_bytes()
        for source in (CORE, peer):
            with self.subTest(source=source), tempfile.TemporaryDirectory(prefix="composite-route-") as temp:
                target = Path(temp)
                shutil.copyfile(source / "compile-work-graph.py", target / "compile-work-graph.py")
                for name in ("route-transaction.py", "route_request_policy.py"):
                    shutil.copyfile(peer / name, target / name)
                graph = load("composite_graph", target / "compile-work-graph.py")
                self.assertEqual(graph._NATIVE_ROUTE_PRODUCER_PROFILES_V1.get(hashlib.sha256(raw).hexdigest()), len(raw))
                module, path, captured = graph._native_route_scope_module_v1()
                self.assertEqual(path, target / "route-transaction.py")
                self.assertEqual(captured, raw)
                self.assertTrue(callable(module.read_current_route_scope_v1))
                (target / "route-transaction.py").write_bytes(raw + b"\n")
                with self.assertRaisesRegex(graph.WorkGraphError, "source identity changed"):
                    graph._native_route_scope_module_v1()
                (target / "route-transaction.py").write_bytes(raw)
                policy = target / "route_request_policy.py"
                policy.write_bytes(policy.read_bytes() + b"\n")
                with self.assertRaisesRegex(graph.WorkGraphError, "dependency is unavailable or mismatched"):
                    graph._native_route_scope_module_v1()

    def test_both_current_compilers_load_exact_transport_and_refuse_substitution(self):
        peer = ROOT / "source-peers/route-graph/skills/implementaudit/scripts"
        transport = (ROOT / "scripts/work-graph-continuity-transport.py").read_bytes()
        for source in (CORE, peer):
            with self.subTest(source=source), tempfile.TemporaryDirectory(prefix="current-transport-loader-") as temporary:
                target = Path(temporary)
                scripts = target / "skills/implementaudit/scripts"
                shutil.copytree(CORE, scripts, ignore=shutil.ignore_patterns("__pycache__"))
                shutil.copy2(source / "compile-work-graph.py", scripts / "compile-work-graph.py")
                (target / "scripts").mkdir()
                for name in ("operational-evidence.py", "operational_query_policy.py", "work-graph-continuity-transport.py"):
                    shutil.copy2(ROOT / "scripts" / name, target / "scripts" / name)
                graph = load("current_transport_graph", scripts / "compile-work-graph.py")
                owner, _, _ = graph._native_static_owner_module_v1()
                claim, validate = [(scripts / name).read_bytes() for name in ("claim-run.sh", "validate-run-root.sh")]
                adapter, sources, _ = graph._native_six_source_transport_v1(owner, claim, validate)
                self.assertEqual(Path(adapter.__file__), target / "scripts/work-graph-continuity-transport.py")
                self.assertEqual(sources[0][1], claim)
                self.assertEqual(len(sources), 8)
                self.assertEqual(graph._NATIVE_CONTINUITY_TRANSPORT_SHA256, hashlib.sha256(transport).hexdigest())
                self.assertEqual(graph._NATIVE_CONTINUITY_TRANSPORT_BYTES, len(transport))
                marker = target / "UNSELECTED_TRANSPORT_EXECUTED"
                changed = transport + ("\nfrom pathlib import Path\nPath(" + repr(str(marker))
                                       + ").write_text('unselected')\n").encode()
                (target / "scripts/work-graph-continuity-transport.py").write_bytes(changed)
                with self.assertRaisesRegex(graph.WorkGraphError, "native continuity transport source identity changed"):
                    graph._native_six_source_transport_v1(owner, claim, validate)
                self.assertFalse(marker.exists())

    def test_overlay_retains_lifecycle_record_interface(self):
        result = subprocess.run([shutil.which("bash"), (PEER / "validate-run-root.sh").as_posix(),
                                 "--turn-disposition", "--help"], capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertIn(b"usage:", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
