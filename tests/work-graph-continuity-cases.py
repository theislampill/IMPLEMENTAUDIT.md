#!/usr/bin/env python3
"""Finite repository-only transport controls on disposable Git/run fixtures.

Current engine code runs with exact historical six-source inputs.
These are constructed source/interface observations, not host continuity credit.
The existing claim/rotation owners create fixture receipts; no live controller is
inspected. Run from the repository root with PYTHONDONTWRITEBYTECODE=1.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).absolute().parents[1]
SCRIPTS = ROOT / "skills/implementaudit/scripts"
TRANSPORT = ROOT / "scripts/work-graph-continuity-transport.py"
NAMES = ("claim-run.sh", "validate-run-root.sh", "claim-run-rotation.py",
         "rotate-canonical-state.py", "canonical_hot_projection.py", "canonical_custody.py")
EVIDENCE = Path(os.environ.get("R0035_TRANSPORT_EVIDENCE") or
                tempfile.mkdtemp(prefix="r0035-transport-evidence-")).absolute()
EVIDENCE.mkdir(parents=True, exist_ok=True)
os.environ["R0039_CLAIM_EVIDENCE_DIR"] = str(EVIDENCE / "constructed")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


HISTORICAL = load("transport_historical_inputs", ROOT / "tests/work-graph-historical-fixture.py")
_ENGINE = tempfile.TemporaryDirectory(prefix="transport-historical-engine-")
SOURCE_ROOT = HISTORICAL.copy_continuity_engine(Path(_ENGINE.name))
SCRIPTS = SOURCE_ROOT / "skills/implementaudit/scripts"
TRANSPORT = SOURCE_ROOT / "scripts/work-graph-continuity-transport.py"
OWNER = load("r0035_transport_source_owner", SOURCE_ROOT / "scripts/operational-evidence.py")
FIXTURES = load("r0035_transport_constructed_fixture",
                ROOT / "fixtures/canonical-state-rotation/claim_transaction_test.py")
FIXTURES.POST = SCRIPTS
ADAPTER = load("r0035_transport_host_probe", TRANSPORT) if TRANSPORT.exists() else None
REQUIRE_SUPPORTED_HOST = "--require-supported-host" in sys.argv
if REQUIRE_SUPPORTED_HOST:
    sys.argv.remove("--require-supported-host")
_HOST_STATUS = None


def snapshot(root):
    """Byte and mode census includes objects, refs, run state, and lease files."""
    return {str(path.relative_to(root)): (path.stat().st_mode & 0o7777,
                                         hashlib.sha256(path.read_bytes()).hexdigest())
            for path in sorted(root.rglob("*")) if path.is_file()}


def save_result(name, result):
    value = {key: (value.decode("utf-8", "backslashreplace") if isinstance(value, bytes) else value)
             for key, value in result.items()}
    (EVIDENCE / (name + ".json")).write_text(json.dumps(value, indent=2) + "\n")


def require_host():
    """Probe a disposable empty repository, never the local active controller."""
    global _HOST_STATUS
    if _HOST_STATUS is None:
        if ADAPTER is None:
            raise AssertionError("sealed six-source transport is not implemented")
        with tempfile.TemporaryDirectory(prefix="r0035-transport-host-") as directory:
            repository = Path(directory)
            if sys.platform == "linux" and Path("/usr/bin/git").exists():
                created = subprocess.run(["/usr/bin/git", "init", "-q", str(repository)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env={"PATH": "/usr/bin:/bin", "GIT_CONFIG_GLOBAL": os.devnull,
                                 "GIT_CONFIG_NOSYSTEM": "1"}, timeout=15, check=False)
                if created.returncode:
                    raise AssertionError(created.stderr.decode())
            sources = tuple((str(SCRIPTS / name), (SCRIPTS / name).read_bytes()) for name in NAMES)
            try:
                observed = ADAPTER.call_readonly_v1(OWNER, repository=str(repository),
                            sources=sources, arguments=("--current-controller",))
                # Empty controller population is the intended owner refusal;
                # mounted-source acquisition alone qualifies this host probe.
                if observed["returncode"] == 0 or not observed["closure"]:
                    raise AssertionError("empty fixture unexpectedly admitted a controller")
                _HOST_STATUS = dict(status="SUPPORTED_CONSTRUCTED_TRANSPORT", owner_exit=observed["returncode"])
            except ADAPTER.ContinuityTransportError as exc:
                if exc.code not in {"CONTINUITY_TRANSPORT_UNSUPPORTED_HOST", "CONTINUITY_TRANSPORT_UNAVAILABLE",
                                    "CONTINUITY_TRANSPORT_NAMESPACE_REFUSED", "CONTINUITY_TRANSPORT_TIMEOUT"}:
                    raise
                _HOST_STATUS = dict(status="UNSUPPORTED", refusal_code=exc.code,
                                    returncode=exc.returncode, stderr=exc.stderr.decode("utf-8", "replace"))
        save_result("host-capability", _HOST_STATUS)
        print("continuity transport host disposition: " + _HOST_STATUS["status"], file=sys.stderr)
    if _HOST_STATUS["status"] == "UNSUPPORTED":
        message = "UNSUPPORTED: " + _HOST_STATUS["refusal_code"]
        if REQUIRE_SUPPORTED_HOST:
            raise AssertionError(message)
        raise unittest.SkipTest(message + "; positive kernel/owner controls not qualified")


def exercise_python_startup(case, label, receipt):
    """An unchanged nested owner must not import Python source from repo cwd."""
    commands = (("--current-controller",),
                ("--require-current-continuity", FIXTURES.CONTROLLER),
                ("--verify-resume-receipt", receipt))
    expected = [case.fixture.claim(*arguments) for arguments in commands]
    for baseline in expected:
        case.assertEqual(baseline.returncode, 0, baseline.stderr)
    poison = case.fixture.repo / "datetime.py"
    case.assertFalse(poison.exists())
    poison.write_text("import os\nos.write(2,b'OUTSIDE_SIX_SOURCE_EXECUTED\\n')\n"
                      "raise RuntimeError('OUTSIDE_SIX_SOURCE_EXECUTED')\n")
    before = snapshot(case.fixture.repo)
    original = subprocess.Popen
    tracing = os.environ.get("R0035_TRANSPORT_TRACE") == "1"
    try:
        for arguments, baseline in zip(commands, expected):
            with case.subTest(command=arguments[0], fixture=label):
                trace = EVIDENCE / (label + "-startup-" + arguments[0][2:] + ".trace")
                def traced(command, **kwargs):
                    if tracing and Path(command[0]).name == "bwrap":
                        command = ["/usr/bin/strace", "-f", "-v", "-yy", "-s", "2048", "-o", str(trace),
                                   "-e", "trace=openat,execve,write", *command]
                    return original(command, **kwargs)
                with mock.patch.object(subprocess, "Popen", side_effect=traced):
                    observed = case.call(*arguments)
                save_result(label + "-cwd-module-" + arguments[0][2:], observed)
                case.assertEqual((observed["returncode"], observed["stdout"], observed["stderr"]),
                                 (baseline.returncode, baseline.stdout, baseline.stderr))
                if tracing:
                    lines = trace.read_text().splitlines()
                    case.assertFalse(any("openat(" in line and '<' + str(poison) + '>' in line for line in lines),
                                     "nested Python opened the repository marker module")
                    case.assertFalse(any("write(" in line and "OUTSIDE_SIX_SOURCE_EXECUTED" in line for line in lines))
                    binaries, wrappers = [], []
                    for line in lines:
                        match = re.search(r'\bexecve\("([^"]+)", \[', line)
                        if not match or not re.fullmatch(r"(?:cpython|python(?:3(?:\.\d+)?)?)", Path(match[1]).name):
                            continue
                        case.assertIn(match[1], ("/implementaudit-python/cpython", "/implementaudit-python/python",
                                                "/implementaudit-python/python3"), "unisolated host Python executed")
                        if match[1].endswith("/cpython"):
                            case.assertIn('["/implementaudit-python/cpython", "-I", "-S", "-B", ', line)
                            binaries.append(line)
                        else:
                            wrappers.append(line)
                    case.assertGreaterEqual(len(binaries), 2, "bootstrap and actual owner Python were not traced")
                    case.assertTrue(wrappers, "owner did not execute a private Python wrapper")
                    case.assertTrue({line.split()[0] for line in wrappers}.issubset(
                                    {line.split()[0] for line in binaries}), "wrapper did not exec the isolated alias")
                    if arguments[0] != "--current-controller":
                        narrowed = [line for line in binaries if '", "-", ' in line and '"PYTHON' not in line]
                        case.assertTrue(narrowed, "no actual nested validator Python after owner environment narrowing")
                        case.assertTrue(all('"PATH=/implementaudit-python:' in line for line in narrowed))
                    save_result(label + "-startup-executions-" + arguments[0][2:],
                                dict(python_execve=binaries, wrapper_execve=wrappers, poison_module_reads=0))
        case.assertEqual(snapshot(case.fixture.repo), before,
                         "startup read wrote bytecode, objects, refs, or run state")
    finally:
        poison.unlink()


class HostIndependentControls(unittest.TestCase):
    def test_command_allowlist_refuses_writers_without_host_execution(self):
        self.assertIsNotNone(ADAPTER)
        for command in ("--rotate-canonical-state", "--recover-canonical-state", "--resume-controller",
                        "--invalidate-continuity", "--read-resume-state", "--observe-current-continuity"):
            with self.subTest(command=command):
                with self.assertRaises(ADAPTER.ContinuityTransportError) as caught:
                    ADAPTER.call_readonly_v1(OWNER, repository="unused", sources=(), arguments=(command, "fixture"))
                self.assertEqual(caught.exception.code, "CONTINUITY_TRANSPORT_COMMAND_REFUSED")
                self.assertIsNone(caught.exception.returncode)

    def test_exact_source_population_rejects_omissions_extras_and_foreign_paths(self):
        self.assertIsNotNone(ADAPTER)
        sources = tuple((str(SCRIPTS / name), (SCRIPTS / name).read_bytes()) for name in NAMES)
        for bad in ((), sources[:-1], sources + sources[:1], list(sources),
                    ((str(ROOT / NAMES[0]), sources[0][1]),) + sources[1:]):
            with self.subTest(population=len(bad)):
                with self.assertRaises(ADAPTER.ContinuityTransportError):
                    ADAPTER._sources(OWNER, bad, SCRIPTS)

    def test_windows_and_missing_host_tool_are_typed_refusals(self):
        self.assertIsNotNone(ADAPTER)
        with mock.patch.object(sys, "platform", "win32"):
            with self.assertRaises(ADAPTER.ContinuityTransportError) as caught:
                ADAPTER.call_readonly_v1(OWNER, repository="unused", sources=(), arguments=("--current-controller",))
        self.assertEqual(caught.exception.code, "CONTINUITY_TRANSPORT_UNSUPPORTED_HOST")
        with mock.patch.object(Path, "resolve", side_effect=FileNotFoundError("constructed absent tool")):
            with self.assertRaises(ADAPTER.ContinuityTransportError) as caught:
                ADAPTER._trusted("bwrap")
        self.assertEqual(caught.exception.code, "CONTINUITY_TRANSPORT_UNAVAILABLE")


class TransportControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_host()
        # Execution fixtures stay outside workspace synchronisation. A source
        # synchronizer replacing an inode is correctly a custody refusal, not a
        # transport regression. Durable observations still use EVIDENCE.
        cls.temp = tempfile.TemporaryDirectory(prefix="r0035-transport-controls-", dir="/tmp")
        cls.base = Path(cls.temp.name)
        cls.fixture = FIXTURES.Fixture(persistent_repo=cls.base / "legacy")
        cls.checkout = cls.base / "source-checkout"
        cls.source_dir = cls.checkout / "skills/implementaudit/scripts"
        cls.source_dir.mkdir(parents=True)
        for name in NAMES:
            shutil.copy2(SCRIPTS / name, cls.source_dir / name)
        cls.adapter_path = cls.checkout / "scripts/work-graph-continuity-transport.py"
        cls.adapter_path.parent.mkdir()
        if TRANSPORT.exists():
            shutil.copy2(TRANSPORT, cls.adapter_path)
            cls.transport = load("r0035_transport_under_test", cls.adapter_path)
        else:
            cls.transport = None
        cls.sources = tuple((str(cls.source_dir / name), (cls.source_dir / name).read_bytes())
                            for name in NAMES)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.close()
        cls.temp.cleanup()

    def call(self, *arguments, sources=None, repository=None):
        self.assertIsNotNone(self.transport, "sealed six-source continuity transport is not implemented")
        return self.transport.call_readonly_v1(OWNER, repository=str(repository or self.fixture.repo),
                  sources=self.sources if sources is None else sources, arguments=tuple(arguments))

    def test_01_old_transport_reopens_the_wrong_companion_path(self):
        # Catch accidental claims that the old two-source transport was already
        # compatible: its actual historical six-source invocation retains this failure.
        with tempfile.TemporaryDirectory(dir=self.base) as temporary:
            root = Path(temporary)
            claim, validate = ((SCRIPTS / name).read_bytes() for name in NAMES[:2])
            (root / NAMES[0]).write_bytes(claim)
            (root / NAMES[1]).write_bytes(validate)
            command = ["/usr/bin/bash", "-c", OWNER._NATIVE_R0011_CHILD_BOOTSTRAP,
                       "implementaudit-r0035-current", str(root / NAMES[0]), str(root / NAMES[1]),
                       hashlib.sha256(claim).hexdigest(), hashlib.sha256(validate).hexdigest(),
                       "--require-current-continuity", FIXTURES.CONTROLLER]
            run = subprocess.run(command, cwd=self.fixture.repo, env={"PATH": "/usr/bin:/bin",
                                  "PYTHONDONTWRITEBYTECODE": "1"}, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, timeout=30, check=False)
            self.assertEqual(run.returncode, 2)
            self.assertIn(b"./claim-run-rotation.py", run.stderr)
            save_result("old-transport-preimage", dict(argv=command, returncode=run.returncode,
                                                       stdout=run.stdout, stderr=run.stderr))

    def test_02_legacy_owner_outputs_and_repository_bytes_are_preserved(self):
        before = snapshot(self.fixture.repo)
        prior_closure = None
        for arguments in (("--current-controller",),
                          ("--require-current-continuity", FIXTURES.CONTROLLER),
                          ("--verify-resume-receipt", self.fixture.receipt)):
            with self.subTest(command=arguments[0]):
                expected = self.fixture.claim(*arguments)
                observed = self.call(*arguments)
                save_result("legacy-" + arguments[0][2:], observed)
                self.assertEqual(observed["returncode"], expected.returncode, observed["stderr"].decode())
                self.assertEqual(observed["stdout"], expected.stdout)
                self.assertEqual(observed["stderr"], expected.stderr)
                self.assertEqual(observed["returncode"], 0)
                closure = observed["closure"]
                self.assertEqual(closure["schema"], "implementaudit.continuity-source-closure.v2")
                self.assertEqual(closure["repository"], str(self.fixture.repo))
                self.assertEqual(tuple(row["name"] for row in closure["members"]), NAMES)
                self.assertTrue(all(row["readonly"] and row["links"] == 1
                                    and row["seals"] == 15 for row in closure["members"]))
                self.assertEqual(closure["startup"], dict(profile="ISOLATED_CPYTHON_V1", isolated=True,
                                                        no_site=True, dont_write_bytecode=True))
                if prior_closure is not None:
                    self.assertEqual(closure, prior_closure, "closure identity includes ephemeral process state")
                prior_closure = closure
        self.assertEqual(snapshot(self.fixture.repo), before,
                         "readonly transport changed refs, objects, leases, or run/source state")

    def test_03_exact_readonly_command_domain(self):
        # A future broad pass-through must not expose any writer or extra argv.
        bad = [(), ("--current-controller", FIXTURES.CONTROLLER),
               ("--current-controller", "extra", "extra"),
               ("--require-current-continuity",), ("--verify-resume-receipt",),
               ("--require-current-continuity", FIXTURES.CONTROLLER, "extra"),
               ("--verify-resume-receipt", self.fixture.receipt, "extra"),
               ("--require-current-continuity", "--rotate-canonical-state"),
               ("--verify-resume-receipt", "not-a-receipt")]
        bad += [(command, FIXTURES.CONTROLLER) for command in
                ("--rotate-canonical-state", "--recover-canonical-state", "--resume-controller",
                 "--invalidate-continuity", "--read-resume-state", "--read-current-state",
                 "--observe-current-continuity", "--controller")]
        before = snapshot(self.fixture.repo)
        for arguments in bad:
            with self.subTest(arguments=arguments):
                with self.assertRaises(self.transport.ContinuityTransportError) as caught:
                    self.call(*arguments)
                self.assertEqual(caught.exception.code, "CONTINUITY_TRANSPORT_COMMAND_REFUSED")
        self.assertEqual(snapshot(self.fixture.repo), before)

    def test_04_population_aliases_and_unqualified_bytes_refuse(self):
        foreign = self.base / "foreign.py"
        foreign.write_bytes(self.sources[2][1])
        bad = [self.sources[:-1], self.sources + (self.sources[0],),
               self.sources[:2] + ((str(foreign), self.sources[2][1]),) + self.sources[3:],
               self.sources[:2] + ((self.sources[2][0], self.sources[2][1] + b"\n"),) + self.sources[3:],
               list(self.sources)]
        for sources in bad:
            with self.subTest(population=repr(sources)[:120]):
                with self.assertRaises(self.transport.ContinuityTransportError):
                    self.call("--current-controller", sources=sources)
        for name in ("claim-run-rotation.py", "canonical_custody.py"):
            path = self.source_dir / name
            original = path.read_bytes()
            mode = path.stat().st_mode & 0o7777
            for kind in ("symlink", "hardlink", "mode"):
                with self.subTest(name=name, alias=kind):
                    try:
                        if kind == "symlink":
                            path.unlink(); path.symlink_to(foreign)
                        elif kind == "hardlink":
                            path.unlink(); os.link(foreign, path)
                        else:
                            path.chmod(mode ^ 0o111)
                        with self.assertRaises(self.transport.ContinuityTransportError):
                            self.call("--current-controller")
                    finally:
                        path.unlink()
                        path.write_bytes(original)
                        path.chmod(mode)

    def test_05_kernel_seals_are_enforced_and_descriptors_close(self):
        # Omitting WRITE/GROW/SHRINK/SEAL must allow one of these real kernel
        # mutations, even if the parent keeps reporting the expected digest.
        import fcntl
        original = subprocess.Popen
        seen = []
        def inspect(command, **kwargs):
            if Path(command[0]).name == "bwrap":
                for index, item in enumerate(command):
                    if item != "--file":
                        continue
                    fd = int(command[index + 1])
                    self.assertEqual(fcntl.fcntl(fd, 1034), 15)
                    for action in (lambda: os.pwrite(fd, b"x", 0),
                                   lambda: os.ftruncate(fd, 0),
                                   lambda: os.ftruncate(fd, os.fstat(fd).st_size + 1),
                                   lambda: fcntl.fcntl(fd, 1033, 0)):
                        with self.assertRaises(OSError) as caught:
                            action()
                        self.assertEqual(caught.exception.errno, errno.EPERM)
                    seen.append(fd)
            return original(command, **kwargs)
        with mock.patch.object(subprocess, "Popen", side_effect=inspect):
            result = self.call("--current-controller")
        self.assertEqual(result["returncode"], 0, result["stderr"])
        self.assertEqual(len(seen), 8, "six owner sources and two isolated-startup wrappers must be sealed")
        observation = json.loads(result["transport_stderr"].split(b"\t", 1)[1])
        self.assertEqual(tuple(row["name"] for row in observation["startup_members"]), ("python", "python3"))
        self.assertTrue(all(row["readonly"] and row["links"] == 1 and row["mode"] == 0o755
                            for row in observation["startup_members"]))
        save_result("kernel-source-and-startup-seals", result)
        for fd in seen:
            with self.assertRaises(OSError) as caught:
                os.fstat(fd)
            self.assertEqual(caught.exception.errno, errno.EBADF)

    def test_06_source_parent_replacement_does_not_redirect_nested_reads(self):
        original = subprocess.Popen
        parent = self.source_dir.parents[1]
        retained = parent.with_name("skills-retained")
        fired = []
        def replace(command, **kwargs):
            if Path(command[0]).name == "bwrap":
                parent.rename(retained)
                self.source_dir.mkdir(parents=True)
                for name in NAMES:
                    (self.source_dir / name).write_text("SOURCE_REPLACEMENT_EXECUTED\n")
                fired.append(True)
            return original(command, **kwargs)
        try:
            with mock.patch.object(subprocess, "Popen", side_effect=replace):
                with self.assertRaises(self.transport.ContinuityTransportError) as caught:
                    self.call("--require-current-continuity", FIXTURES.CONTROLLER)
            self.assertEqual(fired, [True])
            self.assertEqual(caught.exception.returncode, 0, caught.exception.stderr)
            self.assertEqual(caught.exception.stdout.decode().strip(), self.fixture.receipt)
            self.assertNotIn(b"SOURCE_REPLACEMENT_EXECUTED", caught.exception.stderr)
        finally:
            if fired:
                shutil.rmtree(parent)
                retained.rename(parent)

    def test_07_repository_replacement_refuses_after_held_cwd_execution(self):
        original = subprocess.Popen
        repo = self.fixture.repo
        retained = repo.with_name("legacy-retained")
        fired = []
        def replace(command, **kwargs):
            if Path(command[0]).name == "bwrap":
                repo.rename(retained)
                repo.mkdir()
                fired.append(True)
            return original(command, **kwargs)
        try:
            with mock.patch.object(subprocess, "Popen", side_effect=replace):
                with self.assertRaises(self.transport.ContinuityTransportError) as caught:
                    self.call("--require-current-continuity", FIXTURES.CONTROLLER)
            self.assertEqual(fired, [True])
            self.assertEqual(caught.exception.returncode, 0, caught.exception.stderr)
            self.assertEqual(caught.exception.code, "CONTINUITY_TRANSPORT_SOURCE_CHANGED")
        finally:
            if fired:
                repo.rmdir()
                retained.rename(repo)

    def test_08_unsupported_host_and_missing_bwrap_refuse_before_execution(self):
        with mock.patch.object(sys, "platform", "win32"):
            with self.assertRaises(self.transport.ContinuityTransportError) as caught:
                self.call("--current-controller")
        self.assertEqual(caught.exception.code, "CONTINUITY_TRANSPORT_UNSUPPORTED_HOST")
        original = Path.resolve
        def absent(path, *args, **kwargs):
            if str(path) == "/usr/bin/bwrap":
                raise FileNotFoundError("constructed missing host bwrap")
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, "resolve", new=absent):
            with self.assertRaises(self.transport.ContinuityTransportError) as caught:
                self.call("--current-controller")
        self.assertEqual(caught.exception.code, "CONTINUITY_TRANSPORT_UNAVAILABLE")
        self.assertIsNone(caught.exception.returncode)

    def test_09_currentness_drift_and_owner_stderr_are_preserved(self):
        state = self.fixture.run_root / "STATE.md"
        raw = state.read_bytes()
        try:
            state.write_bytes(raw + b"\nchanged after receipt\n")
            result = self.call("--require-current-continuity", FIXTURES.CONTROLLER)
            self.assertNotEqual(result["returncode"], 0)
            self.assertEqual(result["stdout"], b"")
        finally:
            state.write_bytes(raw)
        marker_ref = "refs/implementaudit/current-generation-migrations/" + FIXTURES.CONTROLLER
        try:
            self.fixture.malformed_marker()
            expected = self.fixture.claim("--require-current-continuity", FIXTURES.CONTROLLER)
            observed = self.call("--require-current-continuity", FIXTURES.CONTROLLER)
            self.assertNotEqual(observed["returncode"], 0)
            self.assertTrue(observed["stderr"])
            self.assertEqual((observed["returncode"], observed["stdout"], observed["stderr"]),
                             (expected.returncode, expected.stdout, expected.stderr))
            save_result("owner-refusal-with-stderr", observed)
        finally:
            self.fixture.git("update-ref", "-d", marker_ref)

    def test_10_cwd_alias_and_foreign_repository_refuse(self):
        link = self.base / "repository-alias"
        link.symlink_to(self.fixture.repo, target_is_directory=True)
        for repository in (link, self.fixture.run_root):
            with self.subTest(repository=repository):
                with self.assertRaises(self.transport.ContinuityTransportError):
                    self.call("--current-controller", repository=repository)

    def test_11_nested_python_ignores_repository_cwd_modules(self):
        exercise_python_startup(self, "legacy", self.fixture.receipt)


class MigratedControls(unittest.TestCase):
    call = TransportControls.call

    @classmethod
    def setUpClass(cls):
        require_host()
        cls.temp = tempfile.TemporaryDirectory(prefix="r0035-transport-migrated-", dir="/tmp")
        cls.addClassCleanup(cls.temp.cleanup)
        # Keep fixture construction in its own ordinary process: the unchanged
        # rotation owner enforces a 64-MiB peak budget, while this test runner has
        # already imported the large operational reader. Do not weaken that gate.
        construction = r'''
import sys
sys.dont_write_bytecode=True
import importlib.util,json,pathlib
spec=importlib.util.spec_from_file_location("constructed_owner_fixture",sys.argv[1])
fixture=importlib.util.module_from_spec(spec); sys.modules[spec.name]=fixture; spec.loader.exec_module(fixture)
fixture.POST=pathlib.Path(sys.argv[3])
subject=fixture.RealHelperIntegration(); subject.persistent_repo=pathlib.Path(sys.argv[2])
try:
    subject.setUp(); rotated=subject.rotate()
    if rotated["status"]!="ROTATED": raise RuntimeError("fixture did not migrate")
    print(json.dumps(dict(repo=str(subject.fixture.repo),run_root=str(subject.fixture.run_root),receipt=rotated["receipt_token"])))
finally:
    subject.doCleanups()
'''
        built = subprocess.run([sys.executable, "-B", "-c", construction,
                  str(ROOT / "fixtures/canonical-state-rotation/claim_transaction_test.py"),
                  str(Path(cls.temp.name) / "repo"), str(SCRIPTS)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                  env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), timeout=45, check=False)
        if built.returncode:
            raise AssertionError(built.stderr.decode())
        data = json.loads(built.stdout)
        cls.fixture = FIXTURES.Fixture.__new__(FIXTURES.Fixture)
        cls.fixture.directory = None
        cls.fixture.repo = Path(data["repo"])
        cls.fixture.scripts = cls.fixture.repo / "skills/implementaudit/scripts"
        cls.fixture.run_root = Path(data["run_root"])
        cls.receipt = data["receipt"]
        cls.source_dir = cls.fixture.scripts
        # The owner's fixture uses copyfile; restore canonical Git source modes
        # in this disposable checkout before the transport's observation starts.
        for name in NAMES:
            shutil.copystat(SCRIPTS / name, cls.source_dir / name)
        adapter = cls.fixture.repo / "scripts/work-graph-continuity-transport.py"
        adapter.parent.mkdir()
        shutil.copy2(TRANSPORT, adapter)
        cls.transport = load("r0035_transport_migrated_under_test", adapter)
        cls.sources = tuple((str(cls.source_dir / name), (cls.source_dir / name).read_bytes())
                            for name in NAMES)

    def test_11_actual_migrated_owners_use_the_closed_readonly_siblings(self):
        before = snapshot(self.fixture.repo)
        original = subprocess.Popen
        trace = EVIDENCE / "migrated-require.trace"
        tracing = os.environ.get("R0035_TRANSPORT_TRACE") == "1"
        def traced(command, **kwargs):
            if tracing and Path(command[0]).name == "bwrap":
                command = ["/usr/bin/strace", "-f", "-yy", "-s", "1024", "-o", str(trace),
                           "-e", "trace=openat,execve", *command]
            return original(command, **kwargs)
        for arguments in (("--current-controller",),
                          ("--require-current-continuity", FIXTURES.CONTROLLER),
                          ("--verify-resume-receipt", self.receipt)):
            expected = self.fixture.claim(*arguments)
            with mock.patch.object(subprocess, "Popen", side_effect=traced):
                result = self.call(*arguments)
            self.assertEqual((result["returncode"], result["stdout"], result["stderr"]),
                             (expected.returncode, expected.stdout, expected.stderr), result["stderr"])
            self.assertEqual(result["returncode"], 0)
            save_result("migrated-" + arguments[0][2:], result)
        # The last trace is verify: it traverses the same complete migrated
        # generation/archive source closure as require. Count actual open calls,
        # excluding paths merely mentioned in process argv or metadata JSON.
        if tracing:
            lines = trace.read_text().splitlines()
            for name in NAMES:
                count = sum("openat(" in line and '<' + str(self.source_dir / name) + '>' in line
                            for line in lines)
                self.assertGreaterEqual(count, 2, "no nested source read after bootstrap: " + name)
        self.assertEqual(snapshot(self.fixture.repo), before,
                         "migrated readonly reads changed Git, leases, or protected run bytes")

    def test_12_each_source_replaced_after_sealing_never_executes_changed_bytes(self):
        original = subprocess.Popen
        for index, name in enumerate(NAMES):
            with self.subTest(source=name):
                path, raw = self.sources[index]
                path = Path(path)
                mode = path.stat().st_mode & 0o7777
                fired = []
                def changed(command, **kwargs):
                    if Path(command[0]).name == "bwrap":
                        path.write_text("echo SOURCE_CHANGED_EXECUTED >&2; exit 93\n" if name.endswith(".sh")
                                        else "import sys; sys.stderr.write('SOURCE_CHANGED_EXECUTED'); sys.exit(93)\n")
                        fired.append(True)
                    return original(command, **kwargs)
                try:
                    with mock.patch.object(subprocess, "Popen", side_effect=changed):
                        with self.assertRaises(self.transport.ContinuityTransportError) as caught:
                            self.call("--require-current-continuity", FIXTURES.CONTROLLER)
                    self.assertEqual(fired, [True])
                    self.assertEqual(caught.exception.returncode, 0, caught.exception.stderr)
                    self.assertEqual(caught.exception.stdout.decode().strip(), self.receipt)
                    self.assertNotIn(b"SOURCE_CHANGED_EXECUTED", caught.exception.stderr)
                    save_result("changed-before-exec-" + name, dict(returncode=caught.exception.returncode,
                                stdout=caught.exception.stdout, stderr=caught.exception.stderr,
                                refusal_code=caught.exception.code))
                finally:
                    path.write_bytes(raw)
                    path.chmod(mode)

    def test_13_nested_python_ignores_repository_cwd_modules(self):
        exercise_python_startup(self, "migrated", self.receipt)


if __name__ == "__main__":
    unittest.main(verbosity=2)
