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


def attachment_dfa_tables(first=ord('/')):
    """Hand-built two-default chain; state 4 accepts a first-byte prefix."""
    tables = {1: [0, 0, 0, 0, 1], 7: [0] * 5,
              2: [0, 0x80000100, 0x80000200, 768, 1024],
              4: [0, 2, 3, 0, 0], 3: [0] * 1280, 8: [0] * 1280}
    tables[3][768 + first] = 3
    tables[8][768 + first] = 4
    tables[3][1024:1280] = [4] * 256
    tables[8][1024:1280] = [4] * 256
    return tables


def attachment_dfa_bytes(tables, flags=1):
    """Serialize only the documented table framing, without a matching oracle."""
    import struct
    widths = {1: 4, 2: 4, 3: 2, 4: 2, 5: 1, 7: 4, 8: 2}
    data = bytearray(24)
    for ident, values in sorted(tables.items()):
        width = widths[ident]
        data.extend(struct.pack('>HHII', ident, width, 0, len(values)))
        data.extend(b''.join(value.to_bytes(width, 'big') for value in values))
        data.extend(bytes((-len(data)) % 8))
    struct.pack_into('>IIIH', data, 0, 0x1b5e783d, 24, len(data), flags)
    return bytes(data)


def large_policy_export(size, *, name='ci-large'):
    """ABI5 fixture: fixed attachment DFA plus an opaque permission blob."""
    def named(value):
        return b'\x04' + (len(value) + 1).to_bytes(2, 'little') + value + b'\0'
    dfa = attachment_dfa_bytes(attachment_dfa_tables(ord('a')))
    version = named(b'version') + b'\x02\x05\0\0\0'
    head = (named(b'profile') + b'\x07\x05' + (len(name.encode()) + 1).to_bytes(2, 'little') +
            name.encode() + b'\0' + named(b'aadfa') + b'\x06' + len(dfa).to_bytes(4, 'little') + dfa +
            b'\x02\0\0\0\0' + named(b'flags') + b'\x07\x08' + named(b'filedfa') + b'\x06')
    padding = size - len(version) - len(head) - 5
    assert padding >= 0
    profile = head + padding.to_bytes(4, 'little') + bytes(padding) + b'\x08'
    return version + profile, hashlib.sha256(b'\x05\0\0\0' + profile).hexdigest()


def kernel_export_fixture(root, name, raw, ident='1'):
    """Task-owned physical files; never a live kernel policy or admission."""
    entry = root / 'profiles' / (name + '.' + ident)
    rawdir = root / 'raw_data' / ident
    entry.mkdir(parents=True)
    rawdir.mkdir(parents=True)
    (entry / 'name').write_text(name + '\n')
    for key, value in [('raw_data', raw), ('sha256', hashlib.sha256(raw).hexdigest().encode() + b'\n'),
                       ('abi', b'v5\n')]:
        (rawdir / key).write_bytes(value)
    for key, target in [('raw_data', 'raw_data'), ('raw_sha256', 'sha256'), ('raw_abi', 'abi')]:
        (entry / key).symlink_to('../../raw_data/' + ident + '/' + target)
    return entry


def apparmor_abi5_compiler():
    """Host-only check: AppArmor parser exists and emits Ubuntu ABI5 wire bytes."""
    parser = Path('/usr/sbin/apparmor_parser')
    if sys.platform != 'linux' or not parser.is_file():
        return False
    env = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC'}
    try:
        version = subprocess.run([str(parser), '--version'], env=env, cwd='/',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=False)
        if version.returncode != 0 or not version.stdout:
            return False
        match = re.fullmatch(rb'AppArmor parser version ([0-9]+)(?:\.[0-9]+){1,2}(?:-[A-Za-z0-9.+-]+)?',
            version.stdout.splitlines()[0])
        if match is None:
            return False
        argv = [str(parser), '--config-file=/dev/null', '--skip-cache',
            '--skip-read-cache', '--jobs=0', '--skip-kernel-load', '--stdout']
        if int(match.group(1)) >= 5:
            argv.append('--zstd-compress-level=0')
        probe = subprocess.run(argv, input=b'abi <abi/4.0>,\nprofile abi5-probe /nonexistent flags=(unconfined) { userns, }\n',
            env=env, cwd='/', stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        return False
    return probe.returncode == 0 and probe.stdout.startswith(b'\x04\x08\x00version\x00\x02\x05\x00\x00\x00')


APPARMOR_ABI5_COMPILER = apparmor_abi5_compiler()


class CompositeSourceCases(unittest.TestCase):
    def c5_selected_source_fixture(self, mode):
        """Explicit historical/current source data; no host or native receipt."""
        temporary = tempfile.TemporaryDirectory(prefix="c5-selected-source-")
        self.addCleanup(temporary.cleanup)
        source = Path(temporary.name) / "source"
        fixture = load("composite_c5_selected_source_fixture", ROOT / "tests/c5-selected-source-fixture.py")
        fixture.materialize(ROOT, source, mode)
        return source

    def test_c5_raw_export_oversize_refuses_before_kernel_open_work(self):
        """AppArmor raw_data open decompresses; advertised overflow must stop first."""
        owner = load('c5_export_preopen_bound', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        with tempfile.TemporaryDirectory(prefix='policy-preopen-bound-') as temporary:
            root = Path(temporary)
            entry = kernel_export_fixture(root, 'ci-large', b'x' * 17)
            with mock.patch.object(owner.os, 'open', side_effect=AssertionError('oversized export opened')), \
                 self.assertRaisesRegex(ValueError, 'advertised.*bound'):
                owner._bwrap_selected_export(entry, root, 16)

    def test_c5_raw_export_readback_rechecks_advertised_bound_before_open(self):
        """A larger replacement between reads must not trigger a second raw open."""
        owner = load('c5_export_readback_preopen', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        actual_read, actual_open = owner._bwrap_read, os.open
        with tempfile.TemporaryDirectory(prefix='policy-readback-preopen-') as temporary:
            root = Path(temporary)
            entry = kernel_export_fixture(root, 'ci-large', b'x' * 17)
            raw_path = root / 'raw_data/1/raw_data'
            raw_opens = []
            def open_counted(path, *args, **kwargs):
                if Path(path) == raw_path:
                    raw_opens.append(str(path))
                return actual_open(path, *args, **kwargs)
            def read_then_replace(path, maximum=4096):
                raw = actual_read(path, maximum)
                if Path(path) == raw_path:
                    raw_path.write_bytes(b'x' * 18)
                return raw
            with mock.patch.object(owner, '_bwrap_read', side_effect=read_then_replace), \
                 mock.patch.object(owner.os, 'open', side_effect=open_counted), \
                 self.assertRaisesRegex(ValueError, 'advertised.*bound'):
                owner._bwrap_selected_export(entry, root, 17)
            self.assertEqual(len(raw_opens), 1)

    def test_c5_tcpdump_diagnostic_retains_actual_export_without_loading_policy(self):
        """The selected refusal can be inspected without changing kernel policy."""
        owner = load('c5_tcpdump_diagnostic', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        actual_iterdir = Path.iterdir
        actual_receive = owner._bwrap_selected_export
        raw, digest = large_policy_export(70000, name='tcpdump')
        inventory = {'tcpdump': dict(attach='<unknown>', mode='enforce', sha256=digest)}
        context = dict(global_state={}, files={'/usr/sbin/apparmor_parser': {'sha256': '1' * 64}})
        with tempfile.TemporaryDirectory(prefix='tcpdump-diagnostic-') as temporary:
            root = Path(temporary)
            entry = kernel_export_fixture(root, 'tcpdump', raw)
            def entries_at(path):
                return iter([entry]) if str(path) == '/sys/kernel/security/apparmor/policy/profiles' else actual_iterdir(path)
            def receive_at(selected, kernel_root):
                self.assertEqual(str(kernel_root), '/sys/kernel/security/apparmor/policy')
                return actual_receive(selected, root)
            output = io.StringIO()
            with mock.patch.object(owner, '_bwrap_root'), \
                 mock.patch.object(owner, 'hosted_bwrap_policy_context', return_value=context), \
                 mock.patch.object(owner, 'hosted_bwrap_policy_inventory', return_value=inventory), \
                 mock.patch.object(Path, 'iterdir', entries_at), \
                 mock.patch.object(owner, '_bwrap_selected_export', side_effect=receive_at), \
                 mock.patch.object(owner, '_bwrap_regular', side_effect=FileNotFoundError), \
                 mock.patch.object(owner, 'hosted_bwrap_policy_parser', side_effect=AssertionError('policy effect')), \
                 contextlib.redirect_stdout(output):
                self.assertEqual(owner.diagnose_hosted_bwrap_policy('tcpdump'), 0)
            record = json.loads(output.getvalue())
            self.assertEqual((record['authority'], record['policy_operations'], record['selected_name']),
                             ('NONE', 0, 'tcpdump'))
            self.assertEqual(record['exported']['bytes'], 70000)
            self.assertEqual(__import__('base64').b64decode(record['exported']['base64']), raw)
            self.assertEqual(record['attachment_observation']['status'], 'PROVED_NOMATCH')
            self.assertEqual(record['attachment_observation']['proof']['profile_sha256'], digest)
            self.assertEqual(set(record['source_files']), {'/etc/apparmor.d/usr.bin.tcpdump',
                                                          '/etc/apparmor.d/local/usr.bin.tcpdump'})
        with mock.patch.object(owner, '_bwrap_root', side_effect=AssertionError('invalid selection reached host')), \
             self.assertRaisesRegex(ValueError, 'selection'):
            owner.diagnose_hosted_bwrap_policy('../other')

    def test_c5_policy_reader_completes_short_reads_and_refuses_hidden_overflow(self):
        """One short read must neither truncate a valid export nor hide overflow."""
        owner = load('c5_incremental_export', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        actual_read = os.read
        with tempfile.TemporaryDirectory(prefix='policy-short-read-') as temporary:
            path = Path(temporary) / 'raw'
            path.write_bytes(b'0123456789')
            with mock.patch.object(owner.os, 'read', side_effect=lambda fd, count: actual_read(fd, min(count, 3))):
                self.assertEqual(owner._bwrap_read(path, 10), b'0123456789')
                with self.assertRaisesRegex(ValueError, 'bound'):
                    owner._bwrap_read(path, 9)

    def test_c5_policy_reader_refuses_same_bytes_physical_replacement(self):
        """Matching content does not authorize switching the captured file object."""
        owner = load('c5_export_replacement', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        actual_read = os.read
        with tempfile.TemporaryDirectory(prefix='policy-replace-') as temporary:
            path = Path(temporary) / 'raw'
            path.write_bytes(b'original bytes')
            changed = False
            def replace_on_read(fd, count):
                nonlocal changed
                if not changed:
                    changed = True
                    path.rename(path.with_name('old'))
                    path.write_bytes(b'original bytes')
                return actual_read(fd, count)
            with mock.patch.object(owner.os, 'read', side_effect=replace_on_read), \
                 self.assertRaisesRegex(ValueError, 'changed'):
                owner._bwrap_read(path, 100)

    def test_c5_selected_export_refuses_replacement_between_complete_reads(self):
        """Full-export bookends bind the object, not just identical second bytes."""
        owner = load('c5_export_bookend_identity', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        with tempfile.TemporaryDirectory(prefix='policy-readback-replace-') as temporary:
            root = Path(temporary)
            entry = kernel_export_fixture(root, 'ci-selected', b'same bytes')
            actual_read = owner._bwrap_read
            changed = False
            def replace_after_read(path, maximum=4096):
                nonlocal changed
                raw = actual_read(path, maximum)
                if Path(path).name == 'raw_data' and not changed:
                    changed = True
                    Path(path).rename(Path(path).with_name('old'))
                    Path(path).write_bytes(raw)
                return raw
            with mock.patch.object(owner, '_bwrap_read', side_effect=replace_after_read), \
                 self.assertRaisesRegex(ValueError, 'changed'):
                owner._bwrap_selected_export(entry, root)

    def test_c5_large_policy_export_reaches_bound_nonmatch_consumer(self):
        """A large permission blob must not force a small, safe attachment UNKNOWN."""
        owner = load('c5_large_export', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        raw, digest = large_policy_export(70000)
        row = dict(attach='<unknown>', mode='enforce', sha256=digest)
        with tempfile.TemporaryDirectory(prefix='policy-large-export-') as temporary:
            root = Path(temporary)
            entry = kernel_export_fixture(root, 'ci-large', raw)
            with self.assertRaisesRegex(ValueError, 'bound'):
                owner._bwrap_selected_export(entry, root, 65536)
            received = owner._bwrap_selected_export(entry, root)
            self.assertEqual(received['bytes'], 70000)
            decoded = __import__('base64').b64decode(received['base64'], validate=True)
            proof = owner._bwrap_prove_nonmatch(decoded, 'ci-large', row)
            owner.hosted_bwrap_policy_delta({'ci-large': row}, opaque_proofs={'ci-large': proof})
            self.assertEqual(proof['result'], 'PROVED_DFA_NOMATCH_BOTH_FIXED_PATHS')
            self.assertEqual(proof['raw_sha256'], hashlib.sha256(raw).hexdigest())

    def test_c5_raw_policy_bound_preserves_smaller_dfa_and_structural_limits(self):
        """The new raw-export budget does not enlarge attachment or parser work."""
        owner = load('c5_large_export_limits', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        raw, digest = large_policy_export(4 * 1024**2)
        row = dict(attach='<unknown>', mode='enforce', sha256=digest)
        with tempfile.TemporaryDirectory(prefix='policy-exact-bound-') as temporary:
            root = Path(temporary)
            entry = kernel_export_fixture(root, 'ci-large', raw)
            self.assertEqual(owner._bwrap_selected_export(entry, root)['bytes'], 4194304)
            self.assertEqual(owner._bwrap_prove_nonmatch(raw, 'ci-large', row)['profile_sha256'], digest)
            (root / 'raw_data/1/raw_data').write_bytes(raw + b'x')
            with self.assertRaisesRegex(ValueError, 'bound'):
                owner._bwrap_selected_export(entry, root)
        for value in (raw + b'x', raw[:-1], b'x' * 65537):
            with self.subTest(bytes=len(value)), self.assertRaises(ValueError):
                owner._bwrap_v5_profiles(value)
        with self.assertRaisesRegex(ValueError, 'DFA bound'):
            owner._bwrap_dfa_nonmatch(bytes(65537), '/usr/bin/bwrap')

    def test_c5_opaque_resolver_debits_actual_exports_against_same_aggregate(self):
        """Two individually bounded exports must not exceed the four-MiB batch."""
        owner = load('c5_export_aggregate', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        actual_iterdir = Path.iterdir
        actual_receive = owner._bwrap_selected_export
        for excess in (0, 1):
            with self.subTest(excess=excess), tempfile.TemporaryDirectory(prefix='policy-aggregate-') as temporary:
                root = Path(temporary)
                first, digest1 = large_policy_export(3 * 1024**2, name='first')
                second, digest2 = large_policy_export(1024**2 + excess, name='second')
                entries = [kernel_export_fixture(root, 'first', first),
                           kernel_export_fixture(root, 'second', second, '2')]
                inventory = {name: dict(attach='<unknown>', mode='enforce', sha256=digest)
                             for name, digest in [('first', digest1), ('second', digest2)]}
                def entries_at(path):
                    return iter(entries) if str(path) == '/sys/kernel/security/apparmor/policy/profiles' else actual_iterdir(path)
                def receive_at(entry, kernel_root, maximum):
                    self.assertEqual(str(kernel_root), '/sys/kernel/security/apparmor/policy')
                    return actual_receive(entry, root, maximum)
                with mock.patch.object(Path, 'iterdir', entries_at), \
                     mock.patch.object(owner, '_bwrap_selected_export', side_effect=receive_at), \
                     mock.patch.object(owner, 'hosted_bwrap_policy_inventory', return_value=inventory):
                    if excess:
                        with self.assertRaisesRegex(ValueError, 'advertised size exceeds bound'):
                            owner._bwrap_resolve_opaque(inventory)
                    else:
                        self.assertEqual(set(owner._bwrap_resolve_opaque(inventory)), {'first', 'second'})

    @unittest.skipUnless(sys.platform == "linux", "fixed Linux hosted prerequisites")
    def test_c5_hosted_current_reader_binds_before_owner_loading(self):
        """Break caught: a changed loader or implicit original profile reads host inputs."""
        observer = load("hosted_current_reader_control", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        receive = getattr(observer, "hosted_current_owner", None)
        self.assertTrue(callable(receive), "bounded hosted current-owner receiving is absent")
        historical_source = self.c5_selected_source_fixture("HISTORICAL_HOSTED_READER")
        with mock.patch("subprocess.Popen", side_effect=AssertionError("reader dispatched a child")):
            current = receive(historical_source)
            self.assertEqual(current.PROFILE, "FIXED_GENUINE_C5_SHARED_IMAGE_CORRESPONDENCE_R4_BUILD_LOCAL_COMPRESSION_20261104_V1")
            self.assertEqual(hashlib.sha256(current.Q.LOADED_DRIVER).hexdigest(),
                             '8cc8342f025866ffaf8c98cc1dd33d7576416c2de39e9d444b9acfd546685a0b')
            self.assertEqual(hashlib.sha256(current.SOURCES['skills/implementaudit/scripts/compile-work-graph.py'][0]).hexdigest(),
                             '62c3b0fb95bbf006ef81e981a16325395e6165ae65c901f667de0e60bf74de3c')
            loader = load("hosted_retained_r4_source", historical_source / "scripts/load-work-graph-c5-executor.py")
            initialized = loader._Engine(loader.R4_BUILD_CACHE_PROFILE,
                                        source_revision=loader.R4_INITIALIZATION_SOURCE_REVISION).load()
            self.assertEqual(hashlib.sha256(initialized.SOURCES['skills/implementaudit/scripts/compile-work-graph.py'][0]).hexdigest(),
                             '1e33ab31553903ca64f58b64673371e0ec4efdf3208031db79f50898744ca033')
            retained = loader._Engine(loader.R4_BUILD_CACHE_PROFILE,
                                     source_revision=loader.R4_BUILD_CACHE_SOURCE_REVISION).load()
            self.assertEqual(hashlib.sha256(retained.SOURCES['skills/implementaudit/scripts/compile-work-graph.py'][0]).hexdigest(),
                             'addcae949fdab009f7f0b4a9f023392309841c1798357ca89f9ec2b84d4c8ba9')
            self.assertEqual(observer.HOSTED_CURRENT105_LOADER_PIN,
                             {'bytes': 20466, 'sha256': 'cc2b2306e05d0845a0dcc809aaa886427009633a7390d7cdb664fbb9884aced9'})
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
        original = load("hosted_pin_owner", self.c5_selected_source_fixture("R4_CURRENT") / "scripts/load-work-graph-c5-executor.py")
        base = original._Engine(original.CURRENT_PROFILE, source_revision=original.R4_COMPOSED_SOURCE_REVISION).load().B
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
        original = load("hosted_nss_owner", self.c5_selected_source_fixture("R4_CURRENT") / "scripts/load-work-graph-c5-executor.py")
        selected = original._Engine(original.CURRENT_PROFILE, source_revision=original.R4_COMPOSED_SOURCE_REVISION).load()
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
        loader_raw = (ROOT / "scripts/load-work-graph-c5-executor.py").read_bytes()
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
                    return_value=Namespace(PROFILE="CONTROL_ONLY", SOURCES={
                        "scripts/load-work-graph-c5-executor.py": (loader_raw, None)})))
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
                if point != "current_owner":
                    self.assertEqual(report["loader"], dict(bytes=len(loader_raw),
                        sha256=hashlib.sha256(loader_raw).hexdigest()))
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
            original = load("hosted_source_namespace_owner", self.c5_selected_source_fixture("R4_CURRENT") / "scripts/load-work-graph-c5-executor.py")
            owner = original._Engine(original.CURRENT_PROFILE, source_revision=original.R4_COMPOSED_SOURCE_REVISION).load()
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
        historical_source = self.c5_selected_source_fixture("HISTORICAL_HOSTED_READER")
        current = observer.hosted_current_owner(historical_source)
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

    def test_c5_bwrap_policy_definition_and_child_boundary_are_exact(self):
        owner = load("c5_bwrap_policy_definition", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        policy = owner.HOSTED_BWRAP_POLICY
        self.assertEqual(hashlib.sha256(policy).hexdigest(), owner.HOSTED_BWRAP_POLICY_SHA256)
        self.assertIn(b"abi <abi/4.0>,", policy)
        self.assertIn(b" /usr/bin/bwrap flags=(attach_disconnected)", policy)
        self.assertIn(b"audit deny capability,", policy)
        self.assertNotIn(b"unconfined", policy)
        self.assertNotIn(b"include", policy)

    def test_c5_bwrap_policy_refuses_competing_or_unrelated_kernel_changes(self):
        owner = load("c5_bwrap_policy_delta", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        before = {"unprivileged_userns": dict(attach="unprivileged_userns", mode="enforce", sha256="a" * 64)}
        after = dict(before, **{owner.HOSTED_BWRAP_NAMES[0]: dict(attach="/usr/bin/bwrap", mode="enforce", sha256="b" * 64),
                               owner.HOSTED_BWRAP_NAMES[1]: dict(attach=owner.HOSTED_BWRAP_NAMES[1], mode="enforce", sha256="c" * 64)})
        owner.hosted_bwrap_policy_delta(before, after)
        for attach in ("/usr/bin/bwrap", "/bin/bwrap", "/usr/bin/*", "<unknown>"):
            with self.subTest(attach=attach), self.assertRaises(ValueError):
                owner.hosted_bwrap_policy_delta(dict(before, foreign=dict(attach=attach, mode="enforce", sha256="d" * 64)))
        with self.assertRaises(ValueError):
            owner.hosted_bwrap_policy_delta(after)
        changed = dict(after, unrelated=dict(attach="/bin/unrelated", mode="enforce", sha256="e" * 64))
        with self.assertRaises(ValueError):
            owner.hosted_bwrap_policy_delta(before, changed)
        changed = dict(after)
        changed[owner.HOSTED_BWRAP_NAMES[0]] = dict(after[owner.HOSTED_BWRAP_NAMES[0]], mode="complain")
        with self.assertRaises(ValueError):
            owner.hosted_bwrap_policy_delta(before, changed)

    def test_c5_bwrap_policy_requires_root_before_reads_or_effects(self):
        owner = load("c5_bwrap_policy_authority", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        with mock.patch.object(owner.os, "geteuid", return_value=1001), \
             mock.patch.object(owner.os, "getegid", return_value=1001), \
             mock.patch.object(owner, "hosted_bwrap_policy_context", side_effect=AssertionError("unadmitted read")), \
             mock.patch.object(owner, "hosted_bwrap_policy_parser", side_effect=AssertionError("unadmitted policy effect")):
            for method in (owner.provision_hosted_bwrap_policy, owner.finalize_hosted_bwrap_policy):
                with self.assertRaisesRegex(ValueError, "root"):
                    method()

        with mock.patch.object(owner.os, "geteuid", return_value=0), \
             mock.patch.object(owner.os, "getegid", return_value=0), \
             mock.patch.dict(owner.os.environ, {}, clear=True), \
             mock.patch.object(owner, "hosted_bwrap_policy_context", side_effect=AssertionError("non-hosted read")):
            for method in (owner.provision_hosted_bwrap_policy, owner.finalize_hosted_bwrap_policy):
                with self.assertRaisesRegex(ValueError, "GitHub-hosted"):
                    method()

    def test_c5_bwrap_policy_parser_cannot_replace_or_write_cache(self):
        owner = load("c5_bwrap_policy_parser", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        with mock.patch.object(owner.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, b"", b"")) as run:
            owner.hosted_bwrap_policy_parser("--skip-kernel-load")
            command = run.call_args.args[0]
            self.assertIn("--config-file=/dev/null", command)
            self.assertIn("--skip-cache", command)
            self.assertIn("--skip-read-cache", command)
            self.assertIn("--jobs=0", command)
            self.assertEqual(run.call_args.kwargs["input"], owner.HOSTED_BWRAP_POLICY)
            self.assertEqual(run.call_args.kwargs["env"], owner.ENV)
            for operation in ("--replace", "--remove"):
                with self.assertRaises(ValueError):
                    owner.hosted_bwrap_policy_parser(operation)
            self.assertEqual(run.call_count, 1)

    @unittest.skipUnless(sys.platform == "linux", "ordinary exclusive receipt controls")
    def test_c5_bwrap_policy_receipt_is_exclusive_and_never_follows_links(self):
        owner = load("c5_bwrap_policy_receipt", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        with tempfile.TemporaryDirectory(prefix="c5-policy-receipt-") as temporary:
            parent = os.open(temporary, os.O_RDONLY | os.O_DIRECTORY)
            try:
                descriptor = owner.create_hosted_bwrap_receipt(parent)
                os.close(descriptor)
                path = Path(temporary) / owner.HOSTED_BWRAP_RECEIPT
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                with self.assertRaises(FileExistsError):
                    owner.create_hosted_bwrap_receipt(parent)
                path.unlink()
                sentinel = Path(temporary) / "sentinel"
                sentinel.write_bytes(b"unchanged")
                path.symlink_to(sentinel)
                with self.assertRaises(FileExistsError):
                    owner.create_hosted_bwrap_receipt(parent)
                self.assertEqual(sentinel.read_bytes(), b"unchanged")
            finally:
                os.close(parent)

    def test_c5_bwrap_policy_changed_launcher_refuses_before_any_parser(self):
        owner = load("c5_bwrap_policy_changed_binary", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        states = {'/sys/module/apparmor/parameters/enabled': b'Y\n',
                  '/proc/sys/kernel/apparmor_restrict_unprivileged_userns': b'1\n',
                  '/proc/sys/kernel/unprivileged_userns_clone': b'1\n'}
        def regular(path, maximum):
            return b'changed binary', [1, 2, 0o100755, 1, 14, 5, 6, 0, 0]
        with mock.patch.object(owner, '_bwrap_disk_policies', return_value=[]), \
             mock.patch.object(owner, '_bwrap_read', side_effect=lambda path, maximum: states[path]), \
             mock.patch.object(owner, '_bwrap_regular', side_effect=regular), \
             mock.patch.object(owner.subprocess, 'run', side_effect=AssertionError('changed binary reached parser')) as run:
            with self.assertRaisesRegex(ValueError, 'launcher pin'):
                owner.hosted_bwrap_policy_context()
            run.assert_not_called()

    def test_c5_bwrap_policy_observation_refuses_pending_or_replaced_policy(self):
        owner = load("c5_bwrap_policy_rollback", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        current = dict(global_state={'restricted': '1'}, files={})
        loaded = {owner.HOSTED_BWRAP_NAMES[0]: dict(attach='/usr/bin/bwrap', mode='enforce', sha256='a'*64),
                  owner.HOSTED_BWRAP_NAMES[1]: dict(attach=owner.HOSTED_BWRAP_NAMES[1], mode='enforce', sha256='b'*64)}
        record = dict(schema='implementaudit.hosted-bwrap-policy.v1', state='ACTIVE',
                      profile_sha256=owner.HOSTED_BWRAP_POLICY_SHA256, context=current, loaded=loaded)
        owner.hosted_bwrap_policy_observation(record, current, loaded)
        for changed in (dict(record, state='PENDING'), dict(record, profile_sha256='0'*64),
                        dict(record, unknown=True), dict(record, context=dict(global_state={'restricted': '0'}, files={}))):
            with self.assertRaises(ValueError):
                owner.hosted_bwrap_policy_observation(changed, current, loaded)
        changed = dict(loaded)
        changed[owner.HOSTED_BWRAP_NAMES[0]] = dict(loaded[owner.HOSTED_BWRAP_NAMES[0]], sha256='c'*64)
        with self.assertRaises(ValueError):
            owner.hosted_bwrap_policy_observation(record, current, changed)

    def test_c5_bwrap_policy_existing_disk_definition_refuses_without_effect(self):
        owner = load("c5_bwrap_policy_existing_disk", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        with mock.patch.object(owner, '_bwrap_disk_policies', return_value=['/etc/apparmor.d/bwrap']), \
             mock.patch.object(owner.subprocess, 'run', side_effect=AssertionError('existing policy reached parser')) as run:
            with self.assertRaisesRegex(ValueError, 'existing bwrap policy file'):
                owner.hosted_bwrap_policy_context()
            run.assert_not_called()

    def test_c5_bwrap_policy_finalization_retains_live_labels_and_receipt(self):
        owner = load("c5_bwrap_policy_nonremoving_finalization", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        current = dict(global_state={'restricted': '1'}, files={})
        loaded = {owner.HOSTED_BWRAP_NAMES[0]: dict(attach='/usr/bin/bwrap', mode='enforce', sha256='a'*64),
                  owner.HOSTED_BWRAP_NAMES[1]: dict(attach=owner.HOSTED_BWRAP_NAMES[1], mode='enforce', sha256='b'*64)}
        record = dict(schema='implementaudit.hosted-bwrap-policy.v1', state='ACTIVE',
                      profile_sha256=owner.HOSTED_BWRAP_POLICY_SHA256, context=current, loaded=loaded)
        live = []
        def after_inventory():
            live.append(424242)  # New managed execution after the observed inventory.
            return current
        with tempfile.TemporaryDirectory(prefix='c5-retained-policy-') as temporary:
            path = Path(temporary) / 'owned.json'
            raw = (json.dumps(record) + '\n').encode()
            path.write_bytes(raw);path.chmod(0o600)
            observed = owner.identity(path.stat())
            with mock.patch.object(owner, '_bwrap_root'), \
                 mock.patch.object(owner, 'HOSTED_BWRAP_RECEIPT', str(path)), \
                 mock.patch.object(owner, 'hosted_bwrap_policy_inventory', return_value=loaded), \
                 mock.patch.object(owner, 'hosted_bwrap_policy_context', side_effect=after_inventory), \
                 mock.patch.object(owner, '_bwrap_regular', return_value=(raw, observed)), \
                 mock.patch.object(owner, 'hosted_bwrap_policy_parser', side_effect=AssertionError('finalizer changed kernel policy')) as parser, \
                 mock.patch.object(owner.os, 'unlink', side_effect=AssertionError('finalizer deleted retained receipt')), \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(owner.finalize_hosted_bwrap_policy(), 0)
            self.assertEqual(live, [424242])
            parser.assert_not_called()
            self.assertEqual(path.read_bytes(), raw)
            result = json.loads(output.getvalue())
            self.assertFalse(result['kernel_policy_unloaded'])
            self.assertFalse(result['receipt_unlinked'])
            self.assertEqual(result['retained_until'], 'EPHEMERAL_VM_DISPOSAL')

    def test_c5_bwrap_policy_finalization_requires_root_inventory_readback(self):
        owner = load("c5_bwrap_policy_mandatory_inventory", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        with mock.patch.object(owner, '_bwrap_root'), \
             mock.patch.object(owner, 'hosted_bwrap_policy_inventory', side_effect=PermissionError('not readable')) as inventory, \
             mock.patch.object(owner, '_bwrap_regular', side_effect=AssertionError('inventory was bypassed')) as receipt, \
             mock.patch.object(owner, 'hosted_bwrap_policy_parser', side_effect=AssertionError('unqualified kernel change')) as parser:
            with self.assertRaises(PermissionError):
                owner.finalize_hosted_bwrap_policy()
            inventory.assert_called_once()
            receipt.assert_not_called()
            parser.assert_not_called()

    def test_c5_bwrap_policy_refusal_reports_bounded_exact_kernel_record(self):
        owner = load("c5_bwrap_policy_refusal_record", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        cases = [('opaque-foreign', '<unknown>', 'name_or_opaque'),
                 ('unpriv_bwrap', 'unpriv_bwrap', 'name_or_opaque'),
                 ('foreign-target', '/usr/bin/bwrap', 'target_attachment'),
                 ('foreign-pattern', '/usr/bin/*', 'target_attachment')]
        with mock.patch.object(owner, 'hosted_bwrap_policy_parser', side_effect=AssertionError('refusal dispatched policy')) as parser:
            for name, attachment, guard in cases:
                row = dict(attach=attachment, mode='enforce', sha256='a'*64)
                with self.subTest(name=name), self.assertRaises(ValueError) as refused:
                    owner.hosted_bwrap_policy_delta({name: row})
                message = str(refused.exception)
                self.assertIn('; kernel_record=', message)
                record = json.loads(message.split('; kernel_record=', 1)[1])
                self.assertEqual(record['name'], name)
                self.assertEqual(record['record'], row)
                self.assertEqual(record['guard'], guard)
                self.assertFalse(record['truncated'])
                self.assertLessEqual(len(message.encode()), 16480)
            name = 'bwrap-' + '\x01'*4090
            row = dict(attach='<unknown>', mode='enforce', sha256='a'*64)
            with self.assertRaises(ValueError) as refused:
                owner.hosted_bwrap_policy_delta({name: row})
            message = str(refused.exception)
            record = json.loads(message.split('; kernel_record=', 1)[1])
            self.assertTrue(record['truncated'])
            self.assertEqual(len(record['complete_record_sha256']), 64)
            self.assertLessEqual(len(message.encode()), 16480)
            parser.assert_not_called()

    def test_c5_selected_policy_export_binds_kernel_bytes_and_refuses_escape(self):
        owner = load("c5_policy_export", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        receive = getattr(owner, '_bwrap_selected_export', None)
        self.assertTrue(callable(receive), 'selected kernel policy export receiving is absent')
        with tempfile.TemporaryDirectory(prefix='apparmor-export-') as temporary:
            root = Path(temporary) / 'policy'
            entry = root / 'profiles' / '1password.1'
            rawdir = root / 'raw_data' / '1'
            entry.mkdir(parents=True)
            rawdir.mkdir(parents=True)
            raw = b'bounded kernel-exported policy bytes\x00'
            for name, value in [('raw_data', raw), ('sha256', hashlib.sha256(raw).hexdigest().encode() + b'\n'), ('abi', b'v9\n')]:
                (rawdir / name).write_bytes(value)
            for name, target in [('raw_data', 'raw_data'), ('raw_sha256', 'sha256'), ('raw_abi', 'abi')]:
                (entry / name).symlink_to('../../raw_data/1/' + target)
            with mock.patch.object(owner, 'hosted_bwrap_policy_parser', side_effect=AssertionError('policy effect')), \
                 mock.patch.object(Path, 'resolve', side_effect=AssertionError('kernel policy root is a magic link')):
                result = receive(entry, root)
                self.assertEqual(result['bytes'], len(raw))
                self.assertEqual(result['sha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(__import__('base64').b64decode(result['base64']), raw)
                (rawdir / 'sha256').write_text('0' * 64 + '\n')
                with self.assertRaisesRegex(ValueError, 'hash'):
                    receive(entry, root)
                (entry / 'raw_data').unlink()
                (entry / 'raw_data').symlink_to(Path(temporary) / 'foreign')
                (Path(temporary) / 'foreign').write_bytes(raw)
                with self.assertRaisesRegex(ValueError, 'export path'):
                    receive(entry, root)

    def test_c5_selected_policy_export_refuses_oversized_or_mixed_exports(self):
        owner = load("c5_policy_export_bounds", ROOT / "scripts/qualify-work-graph-c5-setup.py")
        receive = getattr(owner, '_bwrap_selected_export', None)
        self.assertTrue(callable(receive), 'selected kernel policy export receiving is absent')
        with tempfile.TemporaryDirectory(prefix='apparmor-export-bound-') as temporary:
            root = Path(temporary)
            entry = root / 'profiles' / '1password.1'
            rawdir = root / 'raw_data' / '1'
            other = root / 'raw_data' / '2'
            entry.mkdir(parents=True)
            rawdir.mkdir(parents=True)
            other.mkdir()
            for directory in (rawdir, other):
                (directory / 'raw_data').write_bytes(b'x' * (4 * 1024**2 + 1))
                (directory / 'sha256').write_text('0' * 64 + '\n')
                (directory / 'abi').write_text('v9\n')
            for name, target in [('raw_data', 'raw_data'), ('raw_sha256', 'sha256'), ('raw_abi', 'abi')]:
                (entry / name).symlink_to('../../raw_data/1/' + target)
            with self.assertRaisesRegex(ValueError, 'bound'):
                receive(entry, root)
            (entry / 'raw_abi').unlink()
            (entry / 'raw_abi').symlink_to('../../raw_data/2/abi')
            with self.assertRaisesRegex(ValueError, 'export path'):
                receive(entry, root)

    def test_c5_differential_attachment_retries_the_same_character(self):
        """Clearing flags or consuming a byte at a differential default is unsafe."""
        owner = load('c5_diff_attachment', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        for first, expected in [(ord('/'), False), (ord('a'), True)]:
            raw = attachment_dfa_bytes(attachment_dfa_tables(first))
            for target in ('/usr/bin/bwrap', '/bin/bwrap'):
                with self.subTest(first=first, target=target):
                    self.assertIs(owner._bwrap_dfa_nonmatch(raw, target), expected)
        # An ordinary default consumes the byte even in a flagged DFA.
        tables = attachment_dfa_tables()
        tables[2][1] &= 0x00ffffff
        for target in ('/usr/bin/bwrap', '/bin/bwrap'):
            self.assertTrue(owner._bwrap_dfa_nonmatch(attachment_dfa_bytes(tables), target))

    def test_c5_differential_attachment_preserves_equivalence_classes(self):
        """Retry must use the same mapped byte, not remap it or use raw ASCII."""
        owner = load('c5_diff_equivalence', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        tables = attachment_dfa_tables(1)
        tables[5] = [0] * 256
        tables[5][ord('/')] = 1
        raw = attachment_dfa_bytes(tables)
        self.assertFalse(owner._bwrap_dfa_nonmatch(raw, '/usr/bin/bwrap'))
        self.assertFalse(owner._bwrap_dfa_nonmatch(raw, '/bin/bwrap'))
        self.assertTrue(owner._bwrap_dfa_nonmatch(raw, 'another-program'))

    def test_c5_differential_attachment_covers_direct_attachment_defaults(self):
        """Attachment leftmatch may consume a byte before differential fallback."""
        owner = load('c5_diff_leftmatch', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        tables = {1: [0, 0, 0, 1], 7: [0] * 4,
                  2: [0, 0x80000100, 512, 768], 4: [0, 2, 0, 0],
                  3: [0] * 1024, 8: [0] * 1024}
        for character in (ord('u'), ord('b')):
            tables[3][512 + character] = 2
            tables[8][512 + character] = 3
        tables[3][768:1024] = [3] * 256
        tables[8][768:1024] = [3] * 256
        # Retrying '/' reaches zero; consuming it at 1->2 instead allows
        # the next 'u' or 'b' to reach the accepting self-loop at state 3.
        for target in ('/usr/bin/bwrap', '/bin/bwrap'):
            with self.subTest(target=target):
                self.assertFalse(owner._bwrap_dfa_nonmatch(attachment_dfa_bytes(tables), target))

    def test_c5_differential_attachment_covers_a_midpath_matcher_switch(self):
        """Checking only two complete deterministic traversals is insufficient."""
        owner = load('c5_diff_switch', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        tables = attachment_dfa_tables(ord('a'))
        for character in (ord('u'), ord('b')):
            tables[3][768 + character] = 3
            tables[8][768 + character] = 4
        # All-retry rejects '/' and all-direct rejects the third byte.
        # A direct first default followed by retry reaches accepting state 4.
        for target in ('/usr/bin/bwrap', '/bin/bwrap'):
            with self.subTest(target=target):
                self.assertFalse(owner._bwrap_dfa_nonmatch(attachment_dfa_bytes(tables), target))

    def test_c5_differential_attachment_refuses_unknown_flags_and_cycles(self):
        """New encoding support must retain closed flags and terminate on corrupt defaults."""
        owner = load('c5_diff_refusal', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        for flags in (0, 2, 3, 65535):
            with self.subTest(flags=flags), self.assertRaises(ValueError):
                owner._bwrap_dfa_nonmatch(attachment_dfa_bytes(attachment_dfa_tables(), flags), '/bin/bwrap')
        for bit in (0x01000000, 0x20000000, 0x40000000):
            tables = attachment_dfa_tables()
            tables[2][1] |= bit
            with self.subTest(bit=bit), self.assertRaises(ValueError):
                owner._bwrap_dfa_nonmatch(attachment_dfa_bytes(tables), '/bin/bwrap')
        for defaults in ([0, 1, 3, 0, 0], [0, 2, 1, 0, 0]):
            tables = attachment_dfa_tables()
            tables[4] = defaults
            with self.subTest(defaults=defaults), self.assertRaises(ValueError):
                owner._bwrap_dfa_nonmatch(attachment_dfa_bytes(tables), '/bin/bwrap')

    def test_c5_differential_attachment_refuses_invalid_state_references(self):
        """Malformed default/next/check indices cannot establish a nonmatch proof."""
        owner = load('c5_diff_state_bounds', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        for ident, index in ((4, 1), (8, 0), (3, 0)):
            tables = attachment_dfa_tables()
            tables[ident][index] = 5
            with self.subTest(table=ident), self.assertRaises(ValueError):
                owner._bwrap_dfa_nonmatch(attachment_dfa_bytes(tables), '/bin/bwrap')
        tables = attachment_dfa_tables()
        tables[2][1] = 0x80ffffff
        with self.assertRaises(ValueError):
            owner._bwrap_dfa_nonmatch(attachment_dfa_bytes(tables), '/bin/bwrap')

    def test_c5_compiled_opaque_network_array_counts_typed_triples(self):
        """Legacy network arrays count allow/audit/quiet records, not scalars."""
        owner = load('c5_network_array', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        def named(name):
            return b'\x04' + (len(name) + 1).to_bytes(2, 'little') + name + b'\0'
        def policy(count, values, name=b'net_allowed_af', nested=False, end=b'\x0c'):
            array = named(name) + b'\x0b' + count.to_bytes(2, 'little') + values + end
            if nested:
                array = named(b'nested') + b'\x07' + array + b'\x08'
            profile = (named(b'profile') + b'\x07\x05\x03\x00ci\x00' +
                       named(b'flags') + b'\x07\x08' + array + b'\x08')
            return named(b'version') + b'\x02\x05\x00\x00\x00' + profile, profile
        scalar = b'\x01\x00\x00'
        for count in (0, 1, 46):
            raw, profile = policy(count, scalar * (3 * count))
            with self.subTest(valid_count=count):
                result = owner._bwrap_v5_profiles(raw)
                self.assertEqual(set(result), {'ci'})
                self.assertEqual(result['ci']['sha256'], hashlib.sha256(b'\x05\x00\x00\x00' + profile).hexdigest())
                self.assertIsNone(result['ci']['xmatch'])
        ordinary, _ = policy(1, scalar, name=b'ordinary')
        self.assertEqual(set(owner._bwrap_v5_profiles(ordinary)), {'ci'})
        adverse = [policy(1, scalar * 2), policy(1, scalar * 4), policy(46, scalar * 46),
                   policy(1, scalar * 2 + b'\x02\x00\x00\x00\x00'),
                   policy(1, scalar * 2 + named(b'named') + scalar),
                   policy(1, scalar * 3, name=b'ordinary'),
                   policy(1, scalar * 3, nested=True),
                   policy(1, scalar * 3, end=b'\x0a'), policy(4097, b'')]
        for index, (raw, _) in enumerate(adverse):
            with self.subTest(adverse=index), self.assertRaises(ValueError):
                owner._bwrap_v5_profiles(raw)

        def permission_table_records_are_closed_typed_and_context_bound():
            owner = load('c5_permission_records', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
            def named(name):
                return b'\x04' + (len(name)+1).to_bytes(2, 'little') + name + b'\0'
            def u32(value):
                return b'\x02' + value.to_bytes(4, 'little')
            def policy(count=1, records=None, version=1, parent=b'policydb', extra=b''):
                if records is None:
                    records = (u32(0) + u32(1)*13) * count
                table = named(b'perms') + b'\x07' + named(b'version') + u32(version)
                table += b'\x0b' + count.to_bytes(2, 'little') + records + b'\x0c' + extra + b'\x08'
                body = named(b'profile') + b'\x07\x05\x03\x00ci\x00'
                body += named(b'flags') + b'\x07\x08' + named(parent) + b'\x07' + table + b'\x08\x08'
                return named(b'version') + u32(5) + body, body
            for count in (1, 2, 23):
                raw, body = policy(count)
                result = owner._bwrap_v5_profiles(raw)
                self.assertEqual(result['ci']['sha256'], hashlib.sha256((5).to_bytes(4, 'little') + body).hexdigest())
                self.assertEqual(result['ci']['abi'], 5)
                self.assertIsNone(result['ci']['xmatch'])
            invalid = [policy(version=2)[0], policy(parent=b'unrelated')[0], policy(extra=u32(0))[0],
                       policy(records=u32(1)*14)[0], policy(records=u32(0)+u32(1)*12)[0],
                       policy(records=u32(0)+u32(1)*14)[0],
                       policy(records=u32(0)+u32(1)*12+b'\x01\0\0')[0],
                       policy(records=u32(0)+u32(1)*12+named(b'foreign')+u32(1))[0]]
            valid, _ = policy()
            invalid += [valid[:12]+(7).to_bytes(4, 'little')+valid[16:],
                        valid[:16]+named(b'namespace')+b'\x05\x02\0x\0'+valid[16:], valid[:-1]]
            for raw in invalid:
                with self.subTest(raw_sha=hashlib.sha256(raw).hexdigest()), self.assertRaises(ValueError):
                    owner._bwrap_v5_profiles(raw)
        def no_load_userspace_transport_keeps_original_budget_and_kernel_route():
            owner = load('c5_userspace_transport', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
            fixed = ['/usr/sbin/apparmor_parser', '--config-file=/dev/null', '--skip-cache',
                     '--skip-read-cache', '--jobs=0', '--skip-kernel-load', '--stdout']
            for version in (b'4.0.1', b'5.0.2'):
                query = Namespace(returncode=0, stdout=b'AppArmor parser version '+version+b'\n', stderr=b'')
                result = Namespace(returncode=0, stdout=b'SYNTHETIC_WIRE_ONLY', stderr=b'')
                with mock.patch.object(owner.subprocess, 'run', side_effect=[query, result]) as run:
                    self.assertEqual(owner._bwrap_compile_userspace(b'SYNTHETIC_POLICY'), result.stdout)
                self.assertEqual(run.call_args_list[0].args[0], ['/usr/sbin/apparmor_parser', '--version'])
                expected = fixed + (['--zstd-compress-level=0'] if version.startswith(b'5') else [])
                self.assertEqual(run.call_args_list[1].args[0], expected)
                self.assertLessEqual(run.call_args_list[1].kwargs['timeout'], 20)
                self.assertEqual(run.call_args_list[1].kwargs['input'], b'SYNTHETIC_POLICY')
            bad = Namespace(returncode=0, stdout=b'unknown compiler\n', stderr=b'')
            with mock.patch.object(owner.subprocess, 'run', return_value=bad) as run, self.assertRaises(ValueError):
                owner._bwrap_compile_userspace(b'SYNTHETIC_POLICY')
            self.assertEqual(run.call_count, 1)
            query = Namespace(returncode=0, stdout=b'AppArmor parser version 5.0.2\n', stderr=b'')
            overflow = Namespace(returncode=0, stdout=b'x'*65536, stderr=b'')
            with mock.patch.object(owner.subprocess, 'run', side_effect=[query, overflow]), self.assertRaises(ValueError):
                owner._bwrap_compile_userspace(b'SYNTHETIC_POLICY')
            with mock.patch.object(owner.subprocess, 'run', return_value=query) as run:
                with mock.patch.object(owner.time, 'monotonic', side_effect=[0, 0, 21]), self.assertRaises(ValueError):
                    owner._bwrap_compile_userspace(b'SYNTHETIC_POLICY')
            self.assertEqual(run.call_count, 1)

        permission_table_records_are_closed_typed_and_context_bound()
        no_load_userspace_transport_keeps_original_budget_and_kernel_route()




    @unittest.skipUnless(APPARMOR_ABI5_COMPILER, 'AppArmor ABI5 no-load compiler')
    def test_c5_compiled_opaque_attachment_is_bound_and_conservative(self):
        owner = load('c5_opaque_semantics', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        receive = getattr(owner, '_bwrap_v5_profiles', None)
        prove = getattr(owner, '_bwrap_prove_nonmatch', None)
        self.assertTrue(callable(receive) and callable(prove), 'bound compiled attachment receiving is absent')
        def compile_policy(attachment):
            source = ('abi <abi/4.0>,\nprofile ci-selected ' + attachment +
                      ' flags=(unconfined) { userns, }\n').encode()
            return owner._bwrap_compile_userspace(source)
        raw = compile_policy('/opt/selected/program')
        profiles = receive(raw)
        self.assertEqual(set(profiles), {'ci-selected'})
        row = dict(attach='<unknown>', mode='unconfined', sha256=profiles['ci-selected']['sha256'])
        proof = prove(raw, 'ci-selected', row)
        self.assertEqual(proof['targets'], ['/usr/bin/bwrap', '/bin/bwrap'])
        with self.assertRaises(ValueError):
            owner.hosted_bwrap_policy_delta({'ci-selected': row})
        owner.hosted_bwrap_policy_delta({'ci-selected': row}, opaque_proofs={'ci-selected': proof})
        for changed in (dict(proof, name='foreign'), dict(proof, profile_sha256='0' * 64),
                        dict(proof, targets=['/usr/bin/bwrap']), dict(proof, result=True)):
            with self.assertRaises(ValueError):
                owner.hosted_bwrap_policy_delta({'ci-selected': row}, opaque_proofs={'ci-selected': changed})
        with self.assertRaises(ValueError):
            prove(raw, 'foreign-name', row)
        with self.assertRaises(ValueError):
            prove(raw, 'ci-selected', dict(row, sha256='0' * 64))
        for changed in (raw[:-1], raw + b'\x00', b'x' * 65537):
            with self.assertRaises(ValueError):
                receive(changed)
        for attachment in ('/usr/bin/bwrap', '/bin/bwrap', '/usr/bin/*', '/**'):
            with self.subTest(attachment=attachment):
                competing = compile_policy(attachment)
                bound = receive(competing)['ci-selected']
                with self.assertRaisesRegex(ValueError, 'attachment'):
                    prove(competing, 'ci-selected', dict(row, sha256=bound['sha256']))

    @unittest.skipUnless(APPARMOR_ABI5_COMPILER, 'AppArmor ABI5 no-load compiler')
    def test_c5_approved_compilation_binds_both_exact_profiles_without_loading(self):
        owner = load('c5_approved_compiled', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        receive = getattr(owner, '_bwrap_v5_profiles', None)
        self.assertTrue(callable(receive), 'compiled profile binding is absent')
        compiled = owner._bwrap_compile_userspace(owner.HOSTED_BWRAP_POLICY)
        profiles = receive(compiled)
        self.assertEqual(set(profiles), set(owner.HOSTED_BWRAP_NAMES))
        self.assertTrue(profiles[owner.HOSTED_BWRAP_NAMES[0]]['xmatch'])
        self.assertIsNone(profiles[owner.HOSTED_BWRAP_NAMES[1]]['xmatch'])
        self.assertEqual(len({row['sha256'] for row in profiles.values()}), 2)
        expected = {name: row['sha256'] for name, row in profiles.items()}
        loaded = {name: dict(attach='<unknown>' if row['xmatch'] else name,
                            mode='enforce', sha256=row['sha256']) for name, row in profiles.items()}
        owner.hosted_bwrap_policy_delta({}, loaded, expected_owned=expected)
        wrong = {name: dict(row) for name, row in loaded.items()}
        wrong[owner.HOSTED_BWRAP_NAMES[0]]['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            owner.hosted_bwrap_policy_delta({}, wrong, expected_owned=expected)
        context = dict(global_state={'restricted': '1'}, files={})
        record = dict(schema='implementaudit.hosted-bwrap-policy.v2', state='ACTIVE',
            profile_sha256=owner.HOSTED_BWRAP_POLICY_SHA256, context=context,
            loaded=loaded, compiled_profiles=expected)
        owner.hosted_bwrap_policy_observation(record, context, loaded)
        with self.assertRaises(ValueError):
            owner.hosted_bwrap_policy_observation(dict(record, compiled_profiles=dict(expected,
                **{owner.HOSTED_BWRAP_NAMES[0]: '0' * 64})), context, loaded)
        legacy = dict(record, schema='implementaudit.hosted-bwrap-policy.v1')
        del legacy['compiled_profiles']
        with self.assertRaises(ValueError):
            owner.hosted_bwrap_policy_observation(legacy, context, loaded)

    @unittest.skipUnless(APPARMOR_ABI5_COMPILER, 'AppArmor ABI5 no-load compiler')
    def test_c5_provision_consumes_fresh_proofs_and_retains_pending_on_wrong_loaded_hash(self):
        """Actual installer/receipt flow with constructed kernel observations; no policy load."""
        owner = load('c5_provision_compiled_flow', ROOT / 'scripts/qualify-work-graph-c5-setup.py')
        expected = owner._bwrap_expected_compilation()
        compiled = owner._bwrap_compile_userspace(b'abi <abi/4.0>,\nprofile ci-foreign /opt/other flags=(unconfined) { userns, }\n')
        foreign = dict(attach='<unknown>', mode='unconfined', sha256=owner._bwrap_v5_profiles(compiled)['ci-foreign']['sha256'])
        before = {'ci-foreign': foreign}
        proof = {'ci-foreign': owner._bwrap_prove_nonmatch(compiled, 'ci-foreign', foreign)}
        context = dict(global_state={'restricted': '1'}, files={})
        actual_open = os.open
        for corrupt in (False, True):
            with self.subTest(corrupt=corrupt), tempfile.TemporaryDirectory(prefix='ci-policy-receipt-') as temporary:
                receipt = Path(temporary) / owner.HOSTED_BWRAP_RECEIPT
                after = dict(before, **{name: dict(attach='<unknown>' if i == 0 else name,
                    mode='enforce', sha256=expected[name]) for i, name in enumerate(owner.HOSTED_BWRAP_NAMES)})
                if corrupt:
                    after[owner.HOSTED_BWRAP_NAMES[0]]['sha256'] = '0' * 64
                def open_private(path, *args, **kwargs):
                    return actual_open(temporary if os.fspath(path) == '/run' else path, *args, **kwargs)
                def simulated_add(mode):
                    self.assertEqual(mode, '--add')
                    pending = json.loads(receipt.read_bytes())
                    self.assertEqual(pending['state'], 'PENDING')
                    self.assertEqual(pending['compiled_profiles'], expected)
                    return dict(exit_code=0, stdout='', stderr='')
                with mock.patch.object(owner, '_bwrap_root'), \
                     mock.patch.object(owner, 'hosted_bwrap_policy_context', return_value=context), \
                     mock.patch.object(owner, 'hosted_bwrap_policy_inventory', side_effect=[before, before, after]), \
                     mock.patch.object(owner, '_bwrap_resolve_opaque', return_value=proof) as resolve, \
                     mock.patch.object(owner, '_bwrap_expected_compilation', return_value=expected), \
                     mock.patch.object(owner, 'hosted_bwrap_policy_parser', side_effect=simulated_add) as parser, \
                     mock.patch.object(owner.os, 'open', side_effect=open_private), contextlib.redirect_stdout(io.StringIO()):
                    if corrupt:
                        with self.assertRaisesRegex(ValueError, 'approved compilation'):
                            owner.provision_hosted_bwrap_policy()
                    else:
                        self.assertEqual(owner.provision_hosted_bwrap_policy(), 0)
                    self.assertEqual(parser.call_count, 1)
                    self.assertEqual(resolve.call_args_list, [mock.call(before), mock.call(after)])
                observed = json.loads(receipt.read_bytes())
                self.assertEqual(observed['state'], 'PENDING' if corrupt else 'ACTIVE')
                self.assertEqual(observed['schema'], 'implementaudit.hosted-bwrap-policy.v2')

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
        with self.current_c5_source_copy() as (legacy_root, _), \
                tempfile.TemporaryDirectory(prefix="c5-current-inputs-") as temporary, \
                mock.patch("subprocess.Popen", side_effect=AssertionError("input selection dispatched a producer")):
            legacy = load("historical_current_c5", legacy_root / "scripts/load-work-graph-c5-executor.py")
            create = getattr(legacy, "create_current_composite_c5_session_v1", None)
            self.assertTrue(callable(create), "explicit current C5 entry is absent")
            output = Path(temporary) / "evidence"
            # Schema-valid comparison data only; this constructor test never runs
            # source identity acquisition or treats this pair as a real commit.
            session = create(legacy_root, output, expected_source={"source_commit": "0" * 40, "source_tree": "1" * 40})
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
                compiler_sha = hashlib.sha256((legacy_root / "skills/implementaudit/scripts/compile-work-graph.py").read_bytes()).hexdigest()
                self.assertEqual(compiler_sha, "25f2c24645cc65ed4b9bfbd70bb2d0ce26eb6accc51de0af0df06b3bdff5b627")
                self.assertNotEqual(compiler_sha, hashlib.sha256((ROOT / "skills/implementaudit/scripts/compile-work-graph.py").read_bytes()).hexdigest())
                self.assertEqual(hashlib.sha256(selected["Q"].LOADED_COMPILER).hexdigest(), compiler_sha)
                self.assertEqual(selected["G"].COMPILER_SHA, compiler_sha)
                state = {"files": {name: {"sha256": hashlib.sha256((legacy_root / name).read_bytes()).hexdigest()}
                                   for name in set(base.SPEC["programs"]) | set(base.SPEC["payload_sources"])}}
                # CURRENT retains its historical producer selection. Its
                # constructor wiring is valid, but today's producer bytes must
                # not silently replace that selection.
                program = "scripts/repro-event-capture.py"
                self.assertNotEqual(state["files"][program]["sha256"], base.SPEC["programs"][program])
                with self.assertRaisesRegex(ValueError,
                        r"^C5 original producer source differs: scripts/repro-event-capture\.py$"):
                    base._producer_contract(state)
                self.assertEqual(len([name for name in state["files"] if name.startswith("skills/implementaudit/")]), 66)
                self.assertTrue(output.is_dir())
                self.assertEqual(list(output.iterdir()), [])
                self.assertFalse(session.attempted)
            finally:
                session.close()
            # The explicit current R5 tuple selects all six current producers.
            # Its owner executes its own disposable source. The state below
            # still compares actual ROOT producer/payload data; this is a
            # source-contract positive only, not a native image qualification.
            current_output = Path(temporary) / "correspondence-evidence"
            current_source = self.c5_selected_source_fixture("R5_CURRENT_V4")
            current_owner = load("current_c5_selected_r5_builder", current_source / "scripts/load-work-graph-c5-executor.py")
            current = current_owner.create_r5_hosted_ubuntu24_inner_capture_c5_session_v4(
                current_source, current_output, expected_source={"source_commit": "0" * 40, "source_tree": "1" * 40})
            try:
                base = type(current).__init__.__globals__["B"]
                state = {"files": {name: {"sha256": hashlib.sha256((ROOT / name).read_bytes()).hexdigest()}
                                   for name in set(base.SPEC["programs"]) | set(base.SPEC["payload_sources"])}}
                contract = base._producer_contract(state)
                self.assertEqual(contract["expected_archive_members"], {"canonical_plugin": 75, "standalone_compatibility": 72})
                self.assertEqual(len(contract["selected_programs"]), 6)
                self.assertEqual(len(contract["roles"]), 19)
                self.assertEqual(list(current_output.iterdir()), [])
                self.assertFalse(current.attempted)
            finally:
                current.close()

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
                selected = ROOT / name
                if name in (owner.LOADER, owner.EXECUTOR):
                    selected = ROOT / "test-support/work-graph-c5-profile-history/pro-dg16-public-cost-20261101" / name
                elif name in (owner.BASE, owner.PROVIDER, owner.GATE):
                    selected = ROOT / "test-support/work-graph-c5-profile-history/pre-r4-fresh-canary-20261104" / name
                elif name == "scripts/package-contract.py":
                    selected = ROOT / "fixtures/work-graph-c5-inputs/r4-package-contract-before-build-cache.py"
                elif name == owner.QUALIFIER:
                    selected = ROOT / "test-support/work-graph-c5-profile-history/pre-current105-qualifier-20261104" / name
                elif name == owner.COMPILER:
                    selected = ROOT / "test-support/work-graph-c5-profile-history/pre-composed-compiler-20261104" / name
                shutil.copyfile(selected, target)
            yield root, Path(temporary) / "evidence"

    @contextlib.contextmanager
    def correspondence_c5_source_copy(self):
        """Current producer inputs under the separately explicit current R5 tuple."""
        root = self.c5_selected_source_fixture("R5_CURRENT_V4")
        yield root, root.parent / "evidence"


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
        owner = load("current_c5_layout", self.c5_selected_source_fixture("R4_CURRENT") / "scripts/load-work-graph-c5-executor.py")
        selected = owner._Engine(owner.CURRENT_PROFILE, source_revision=owner.R4_COMPOSED_SOURCE_REVISION).load()
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
        owner = load("current_c5_provider_layout", self.c5_selected_source_fixture("R4_CURRENT") / "scripts/load-work-graph-c5-executor.py")
        with mock.patch("subprocess.Popen", side_effect=AssertionError("provider layout dispatched a producer")):
            selected = owner._Engine(owner.CURRENT_PROFILE, source_revision=owner.R4_COMPOSED_SOURCE_REVISION).load()
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
        for change, message in (("program", r"^C5 original producer source differs: scripts/package-contract\.py$"),
                                ("payload", r"^C5 actual package source selector population differs$")):
            with self.subTest(change=change), self.correspondence_c5_source_copy() as (root, output):
                owner = load("drifted_current_c5", root / "scripts/load-work-graph-c5-executor.py")
                with mock.patch("subprocess.Popen", side_effect=AssertionError("drifted input dispatched a producer")):
                    self.assertEqual(dict(owner.R5_QUALIFIER_REPAIR_PINS),
                                     dict(owner.R5_HOSTED_PINS, **{owner.QUALIFIER:
                                         "cff5376a90dbffdd18e762234c59b62285d8a26d35a916243a085bcf99c48b4c"}))
                    self.assertEqual(owner.R5_HOSTED_PINS[owner.QUALIFIER],
                                     "8cc8342f025866ffaf8c98cc1dd33d7576416c2de39e9d444b9acfd546685a0b")
                    self.assertEqual(dict(owner.R5_CONTINUITY_RECEIVER_PINS),
                                     dict(owner.R5_QUALIFIER_REPAIR_PINS, **{owner.COMPILER:
                                         hashlib.sha256((root / owner.COMPILER).read_bytes()).hexdigest()}))
                    self.assertEqual(dict(owner.R5_INNER_CAPTURE_PINS),
                                     dict(owner.R5_CONTINUITY_RECEIVER_PINS, **{owner.QUALIFIER:
                                         "79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b"}))
                    session = owner.create_r5_hosted_ubuntu24_inner_capture_c5_session_v4(root, output,
                        expected_source={"source_commit": "0" * 40, "source_tree": "1" * 40})
                    try:
                        base = type(session).__init__.__globals__["B"]
                        state = {"files": {name: {"sha256": hashlib.sha256((root / name).read_bytes()).hexdigest()}
                                           for name in set(base.SPEC["programs"]) | set(base.SPEC["payload_sources"])}}
                        contract = base._producer_contract(state)
                        self.assertEqual(contract["expected_archive_members"], {"canonical_plugin": 75, "standalone_compatibility": 72})
                        if change == "program":
                            path = root / "scripts/package-contract.py"
                            path.write_bytes(path.read_bytes() + b"\n")
                        else:
                            (root / "skills/implementaudit/scripts/validate-audit-implement-return.py").unlink()
                        with self.assertRaisesRegex(ValueError, message):
                            session._acquire()
                        self.assertTrue(output.is_dir())
                        self.assertEqual(list(output.iterdir()), [])
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

    def test_prior_windows_load_binding_profile_has_exact_physical_members(self):
        """Preserve the actual previous files; no native qualification transfer."""
        import ast
        nodes = ast.parse((ROOT / "scripts/work-graph-continuity-transport.py").read_bytes()).body
        selected = [node for node in nodes if isinstance(node, ast.Assign)
                    and len(node.targets) == 1 and isinstance(node.targets[0], ast.Subscript)
                    and isinstance(node.targets[0].value, ast.Name)
                    and node.targets[0].value.id == "SOURCE_PROFILES_V1"
                    and ast.literal_eval(node.targets[0].slice) == "composite-20261105-r5-windows-load-binding-v1-core"]
        self.assertEqual(len(selected), 1)
        profile = ast.literal_eval(selected[0].value)
        history = ROOT / "test-support/r5-h0-template-history/eb504b84-source/skills/implementaudit/scripts"
        overrides = {"claim-run.sh", "claim-run-rotation.py"}
        self.assertEqual({path.name for path in history.iterdir()}, overrides)
        for name, size, digest, mode in profile:
            path = (history if name in overrides else CORE) / name
            raw = path.read_bytes()
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (size, digest))
        for name in overrides:
            self.assertNotEqual((history / name).read_bytes(), (CORE / name).read_bytes())

    def test_prior_windows_capture_profile_has_exact_physical_members(self):
        """Actual copied file bytes; profile selection only, no native qualification."""
        import ast
        transport_source = ROOT / "scripts/work-graph-continuity-transport.py"
        profile_name = "composite-20261105-r5-windows-companion-capture-v1-core"
        declarations = [node for node in ast.parse(transport_source.read_bytes()).body
                        if isinstance(node, ast.Assign) and len(node.targets) == 1
                        and isinstance(node.targets[0], ast.Subscript)
                        and isinstance(node.targets[0].value, ast.Name)
                        and node.targets[0].value.id == "SOURCE_PROFILES_V1"
                        and ast.literal_eval(node.targets[0].slice) == profile_name]
        self.assertEqual(len(declarations), 1)
        profile = ast.literal_eval(declarations[0].value)
        history = ROOT / "test-support/r5-windows-load-binding-history/35bf982-source/skills/implementaudit/scripts"
        overrides = {"claim-run.sh", "claim-run-rotation.py"}
        self.assertEqual({path.name for path in history.iterdir()}, overrides)
        self.assertEqual(profile[0][1:3],
                         (32290, "dce0e6af8ce69e63283d0ed5ad1496779d5f2c1b90024c79228af5e22df75d4c"))
        self.assertEqual(profile[2][1:3],
                         (288439, "ce40c4410011e46b209df718207b58c15d18e60db1379e7b66b24f04616637f9"))
        with tempfile.TemporaryDirectory(prefix="prior-windows-capture-source-") as temporary:
            destination = Path(temporary)
            for name, size, digest, mode in profile:
                selected = (history if name in overrides else CORE) / name
                raw = selected.read_bytes()
                self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (size, digest))
                target = destination / name
                shutil.copyfile(selected, target)
                target.chmod(mode)
                self.assertEqual(target.read_bytes(), raw)
            observed = tuple((name, len((destination / name).read_bytes()),
                              hashlib.sha256((destination / name).read_bytes()).hexdigest(), mode)
                             for name, _, _, mode in profile)
            self.assertEqual(observed, profile)
            self.assertEqual(len(observed), 8)
        for name in overrides:
            self.assertNotEqual((history / name).read_bytes(), (CORE / name).read_bytes())

    def test_retained_native_dependency_and_new_core_profiles_are_distinct(self):
        manifest = json.loads((ROOT / "source-peers/native-runtime/SOURCE_MANIFEST.json").read_bytes())
        retained = next(row for row in manifest["files"]
                        if row["path"].endswith("/claim-run-rotation.py"))
        raw = (ROOT / retained["path"]).read_bytes()
        self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()),
                         (247069, '60b96654209ffa21091ce0bdcda1135d73ff0c116750842277019a1b26787a4f'))
        self.assertEqual(retained["materialized_path"], "skills/implementaudit/scripts/claim-run-rotation.py")
        self.assertNotIn(retained["materialized_path"], [row["path"] for row in manifest["frozen_core_dependencies"]])
        transport = load("retained_core_transport", ROOT / "scripts/work-graph-continuity-transport.py")
        historical = transport.SOURCE_PROFILES_V1['composite-20261028-dg10-native-stop-v1-core']
        self.assertEqual(historical[2][1:3],
                         (259408, '1c70c0612bad4b2311bb89ddad60484937b5d195bf98380c3ef3e0d30d6cd94b'))
        self.assertEqual(transport.SOURCE_PROFILES_V1['composite-20261028-dg10-native-stop-v1-original14'][2][1:3],
                         (246657, 'bc862f87428e86c608ddc5fe31ad8a3e2c8324b52c09ba379163db160ad70e93'))
        previous = transport.SOURCE_PROFILES_V1['composite-20261029-dg18-native-resume-v1-core']
        self.assertEqual(transport.SOURCE_PROFILES_V1['composite-20261029-dg18-native-resume-v1-original14'][2][1:3],
                         (246657, '82ddcbb3cf476098fbcac57c0550d4240457688df2c4504c8ab8caea2c3367b1'))
        profile = transport.SOURCE_PROFILES_V1['composite-20261105-r5-h0-mechanical-template-v1-core']
        self.assertTrue(transport._windows_core_profile_v1(historical))
        self.assertTrue(transport._windows_core_profile_v1(previous))
        self.assertTrue(transport._windows_core_profile_v1(profile))
        self.assertNotEqual(previous, profile)
        self.assertFalse(transport._windows_core_profile_v1(((*profile[0][:2], '0' * 64, profile[0][3]), *profile[1:])))
        self.assertEqual(transport.SOURCE_PROFILES_V1['composite-20261028-terminal-inventory-v1-core'][1][1:3],
                         (114294, 'e7a20d7d5eab497338327814367fe8c7221a35cfe61bdfaadd91d84101f0d250'))
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

    def test_engineered_profiles_select_current_bytes_and_preserve_every_historical_domain(self):
        """Break caught: repaired helper bytes cannot reach a fixed accepting consumer."""
        transport = load("engineered_continuity_transport", ROOT / "scripts/work-graph-continuity-transport.py")
        owner = load("engineered_continuity_receiver", ROOT / "scripts/operational-evidence.py")
        prefix = "composite-20261105-r5-h0-mechanical-template-v1-"
        previous = {name: rows for name, rows in transport.SOURCE_PROFILES_V1.items()
                    if not name.startswith(prefix)}
        self.assertEqual(len(previous), 42)
        self.assertEqual(hashlib.sha256(json.dumps(previous, sort_keys=True,
                         separators=(",", ":")).encode()).hexdigest(),
                         '130fe36bc1780d48a422d331e592fd4051e1994ce9849368fffdc74458d7cd94')
        previous = {name: rows for name, rows in previous.items()
                    if not name.startswith("composite-20261105-r5-windows-load-binding-v1-")}
        self.assertEqual(len(previous), 41)
        self.assertEqual(hashlib.sha256(json.dumps(previous, sort_keys=True,
                         separators=(",", ":")).encode()).hexdigest(),
                         'e2b85eb225fcaf5845711833b48ae39afa850ded317dff86f6ae756294662c4d')
        previous = {name: rows for name, rows in previous.items()
                    if not name.startswith("composite-20261105-r5-windows-companion-capture-v1-")}
        self.assertEqual(len(previous), 40)
        self.assertEqual(hashlib.sha256(json.dumps(previous, sort_keys=True,
                         separators=(",", ":")).encode()).hexdigest(),
                         'df36e93324b15e6aecd3701e059cfd426714a25ddf8c8d6997018a959b2996a1')
        previous = {name: rows for name, rows in previous.items()
                    if not name.startswith("composite-20261105-r5-windows-initialization-v1-")}
        self.assertEqual(len(previous), 39)
        self.assertEqual(hashlib.sha256(json.dumps(previous, sort_keys=True,
                         separators=(",", ":")).encode()).hexdigest(),
                         'c70eff98c71f83219fc1776b77081942672dc12d463df2469db29b678a640348')
        previous = {name: rows for name, rows in previous.items()
                    if not name.startswith("composite-20261104-r4-controller-initialization-v1-")}
        self.assertEqual(len(previous), 38)
        self.assertEqual(hashlib.sha256(json.dumps(previous, sort_keys=True,
                         separators=(",", ":")).encode()).hexdigest(),
                         "b7e885d4bc1bddad04b5d43e2ca2ef3dca96bc46c79a916961373e154b68ffcd")
        previous = {name: rows for name, rows in previous.items()
                    if not name.startswith("composite-20261104-r4-native-canary-v4-")}
        self.assertEqual(len(previous), 37)
        self.assertEqual(hashlib.sha256(json.dumps(previous, sort_keys=True,
                         separators=(",", ":")).encode()).hexdigest(), '8ce4b8d78c7ce1257231650f9c49b4df4a3d23a709df102ac24beb457ef0759c')
        historical = {name: rows for name, rows in previous.items()
                      if not name.startswith("composite-20261104-dg17-dg18-custody-v1-")}
        self.assertEqual(len(historical), 35)
        self.assertEqual(hashlib.sha256(json.dumps(historical, sort_keys=True,
                         separators=(",", ":")).encode()).hexdigest(),
                         "50c356cb09ebd3bf3b5be64bab44ba966f758e0abe7f24b8d87c17ef2978dda6")
        self.assertEqual(len(transport.SOURCE_PROFILES_V1), 43)
        for kind, directory in (("core", CORE), ("original14", PEER)):
            with self.subTest(kind=kind):
                selected_name = prefix + kind if kind == "core" else "composite-20261104-dg17-dg18-custody-v1-original14"
                profile = transport.SOURCE_PROFILES_V1[selected_name]
                self.assertIn(profile, owner._NATIVE_CONTINUITY_SOURCE_PROFILES_V1)
                sources = tuple((str(directory / name if (directory / name).is_file() else CORE / name),
                                 (directory / name if (directory / name).is_file() else CORE / name).read_bytes())
                                for name, _, _, _ in profile)
                selected = transport.source_profiles_for_helpers_v1(sources[0][1], sources[1][1])
                self.assertIn(transport._platform_source_profile_v1(profile), selected)
                self.assertEqual(transport._source_profile(sources), transport._platform_source_profile_v1(profile))
                changed = ((sources[0][0], b"!" + sources[0][1][1:]), *sources[1:])
                self.assertEqual(transport.source_profiles_for_helpers_v1(changed[0][1], changed[1][1]), ())
                with self.assertRaisesRegex(transport.ContinuityTransportError, "SOURCE_REFUSED"):
                    transport._source_profile(changed)
                if kind == "original14" and os.name != "nt":
                    with mock.patch.object(subprocess, "run", side_effect=AssertionError("unsupported host dispatched")), \
                            self.assertRaisesRegex(transport.ContinuityTransportError, "UNSUPPORTED_HOST"):
                        transport._original14_call(None, None, ROOT, sources, ("--current-controller",))

    def test_windows_capture_receiver_platform_shapes_and_refusals(self):
        """Constructed platform rows exercise the real receiver; no native Windows credit."""
        import copy
        import stat
        import types
        owner = load("capture_receiver_shapes", ROOT / "scripts/operational-evidence.py")
        transport = load("capture_transport_shapes", ROOT / "scripts/work-graph-continuity-transport.py")
        profile = transport.SOURCE_PROFILES_V1['composite-20261105-r5-h0-mechanical-template-v1-core']
        pair = dict(claim_sha256=profile[0][2], validate_sha256=profile[1][2])
        source = ROOT / "scripts/work-graph-continuity-transport.py"
        raw = source.read_bytes()
        transport_row = dict(path=str(source), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                             mode=stat.S_IMODE(source.stat().st_mode))
        def value(platform):
            rows = []
            for name, size, digest, _mode in profile:
                path = CORE / name
                row = dict(name=name, path=str(path), bytes=size, sha256=digest,
                           mode=stat.S_IMODE(path.stat().st_mode), links=1)
                row.update(dict(held=True) if platform == 'nt' else dict(readonly=True, seals=15))
                rows.append(row)
            if platform == 'nt':
                execution = dict(schema='implementaudit.continuity-windows-source-closure.v1',
                                 repository=str(ROOT), members=rows, custody='WINDOWS_HELD_FILES_V1')
            else:
                execution = dict(schema='implementaudit.continuity-source-closure.v2',
                                 repository=str(ROOT), members=rows,
                                 startup=dict(profile='ISOLATED_CPYTHON_V1', isolated=True,
                                              no_site=True, dont_write_bytecode=True))
            return dict(schema='implementaudit.native-continuity-closure.v1', execution=execution,
                        transport=transport_row)
        def read(path, _label, maximum):
            data = path.read_bytes()
            self.assertLessEqual(len(data), maximum)
            return data
        for platform in ('posix', 'nt'):
            with self.subTest(platform=platform), mock.patch.object(owner, 'os', types.SimpleNamespace(name=platform)), \
                    mock.patch.object(owner, '_native_file', side_effect=read):
                owner._native_check_continuity_closure_v1(value(platform), ROOT, CORE / 'compile-work-graph.py', pair)
                with self.assertRaisesRegex(ValueError, 'executed closure differs'):
                    owner._native_check_continuity_closure_v1(value('nt' if platform == 'posix' else 'posix'),
                                                             ROOT, CORE / 'compile-work-graph.py', pair)
                for mutation in ('digest', 'mode', 'member', 'path', 'custody'):
                    damaged = copy.deepcopy(value(platform))
                    rows = damaged['execution']['members']
                    if mutation == 'digest': rows[0]['sha256'] = '0' * 64
                    elif mutation == 'mode': rows[0]['mode'] ^= 0o100
                    elif mutation == 'member': rows.append(copy.deepcopy(rows[0]))
                    elif mutation == 'path': rows[0]['path'] += '-foreign'
                    else: rows[0]['held' if platform == 'nt' else 'seals'] = False
                    with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'executed closure differs'):
                        owner._native_check_continuity_closure_v1(damaged, ROOT, CORE / 'compile-work-graph.py', pair)
                foreign = dict(pair, claim_sha256='0' * 64)
                with self.assertRaisesRegex(ValueError, 'unknown or incomplete source closure'):
                    owner._native_check_continuity_closure_v1(value(platform), ROOT, CORE / 'compile-work-graph.py', foreign)
        # A POSIX registry mode mismatch remains a strict source refusal.
        damaged_profile = ((*profile[0][:3], profile[0][3] ^ 0o100), *profile[1:])
        with mock.patch.object(owner, '_NATIVE_CONTINUITY_SOURCE_PROFILES_V1', (damaged_profile,)), \
                mock.patch.object(owner, 'os', types.SimpleNamespace(name='posix')), \
                mock.patch.object(owner, '_native_file', side_effect=read), \
                self.assertRaisesRegex(ValueError, 'source differs from the qualified closure'):
            owner._native_check_continuity_closure_v1(value('posix'), ROOT, CORE / 'compile-work-graph.py', pair)

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
        self.assertEqual(selected["qualified_checkpoint"], 'source-sha256:5bb21eed89945a8da97857f980b1f85a06dc07df47b25475b9173f23e82ce8f8')
        self.assertEqual(selected["stored_json_refusal"], "PENDING_STATE_JSON")
        self.assertEqual(selected["nonfinite_counter_refusal"], "PENDING_STATE_JSON_CONSTANT")
        r3 = dict(pins)
        r3[str(fixture.PEER / "compaction-result-observation.py")] = "15de2cb86378960163be08876876ff2473dc034704f6dad014d90a9bb7dc7156"
        r3[str(fixture.PEER / "compaction-audit-pending.py")] = "44f37242fed8e136b548172fdd8d95de270552d8c176e8563b5b4075ac059198"
        r3[str(fixture.PEER / "compaction-source-owner-codex-app.py")] = "8d6e51fcd82ab3d236c5b6707129228a73483fcb7700825c42b0fb797cef9ebf"
        self.assertEqual(fixture.reservation_refusal_profile(r3), {**selected,
            "qualified_checkpoint": "source-sha256:8d6e51fcd82ab3d236c5b6707129228a73483fcb7700825c42b0fb797cef9ebf"})
        before_issuer_repair = dict(r3)
        before_issuer_repair[str(fixture.PEER / "compaction-source-owner-codex-app.py")] = "681b22da6ee2fc5a84cfab7547a9f0551a76c97659e6b5c5b7158ff910117c23"
        self.assertEqual(fixture.reservation_refusal_profile(before_issuer_repair), {
            **selected,
            "qualified_checkpoint": "source-sha256:44f37242fed8e136b548172fdd8d95de270552d8c176e8563b5b4075ac059198"})
        before_pending_repair = dict(before_issuer_repair)
        before_pending_repair[str(fixture.PEER / "compaction-audit-pending.py")] = "e9e8b5f9246f288ceade888c44ad4f1445033f4d944eabf3d8e4da391891a682"
        self.assertEqual(fixture.reservation_refusal_profile(before_pending_repair), {
            **selected,
            "qualified_checkpoint": "source-sha256:681b22da6ee2fc5a84cfab7547a9f0551a76c97659e6b5c5b7158ff910117c23"})
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
        # This closed historical C4 profile still binds its original
        # package owner. The new builder is deliberately refused.
        with self.assertRaisesRegex(ValueError, "executable"):
            prefix.validate_programs({"files": programs}, profile="COMPOSED_COMPOSITE_PREFIX_23_V1")
        retained = ROOT / "fixtures/work-graph-c5-inputs/r4-package-contract-before-build-cache.py"
        programs["scripts/package-contract.py"]["sha256"] = hashlib.sha256(retained.read_bytes()).hexdigest()
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
            owner = load("retained_overlay_lazy_native_input", target / "rotate-canonical-state.py")
            native = owner.native_inputs_module_v1()
            raw = Path(native.__file__).read_bytes()
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()),
                             (27154, "96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489"))
            # The new core dependency remains invalid for the retained peer.
            shutil.copyfile(CORE / "canonical_rotation_inputs.py", target / "canonical_rotation_inputs.py")
            with self.assertRaisesRegex(owner.RotationError, "native input source identity mismatch"):
                owner.native_inputs_module_v1()

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

    def test_windows_full_snapshot_budget_is_separate_from_thin_reads(self):
        from types import SimpleNamespace
        transport = load("snapshot_budget_transport", ROOT / "scripts/work-graph-continuity-transport.py")
        self.assertEqual(transport._TIMEOUT, 30)
        owner = SimpleNamespace(_native_module_from_bytes=lambda *a: None,
                                _native_child_environment=lambda route: {})
        class ObservedCall(Exception):
            pass
        with tempfile.TemporaryDirectory(prefix="snapshot-budget-dispatch-") as temporary:
            root = Path(temporary).resolve()
            session = dict(root=root, view=root / "view", scratch=root / "scratch",
                           expected=[], reads=0)
            fake_os = SimpleNamespace(name="nt", pathsep=os.pathsep, devnull=os.devnull)
            for closing in (False, True):
                session["reads"] = int(closing)
                with self.subTest(closing=closing), mock.patch.object(transport, "os", fake_os), \
                        mock.patch.object(transport, "_windows_parent_python_v1", return_value="pinned-python"), \
                        mock.patch.object(transport.subprocess, "run", side_effect=ObservedCall) as dispatch:
                    with self.assertRaises(ObservedCall):
                        transport._call_windows_canonical_snapshot_v1(owner, object(), root, root / "run",
                            ((str(root / "canonical_custody.py"), b"constructed source selector"),), session=session)
                    self.assertEqual(dispatch.call_args.kwargs["timeout"], 60)
                    self.assertEqual(transport._TIMEOUT, 30)
                    request = json.loads(dispatch.call_args.args[0][-1])
                    self.assertEqual(request["verify_only"], closing)

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
                # Constructed comparison metadata only: exercise the independent
                # receiver's actual source reads without dispatch/currentness.
                closure = dict(schema="implementaudit.native-continuity-closure.v1",
                    execution=dict(schema="implementaudit.continuity-source-closure.v2",
                        repository=str(target), members=[dict(name=Path(path).name,
                            path=path, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                            mode=Path(path).stat().st_mode & 0o777, links=1, readonly=True, seals=15)
                            for path, raw in sources],
                        startup=dict(profile="ISOLATED_CPYTHON_V1", isolated=True,
                            no_site=True, dont_write_bytecode=True)),
                    transport=dict(path=str(target / "scripts/work-graph-continuity-transport.py"),
                        bytes=len(transport), sha256=hashlib.sha256(transport).hexdigest(),
                        mode=(target / "scripts/work-graph-continuity-transport.py").stat().st_mode & 0o777))
                pair = dict(claim_sha256=hashlib.sha256(claim).hexdigest(),
                            validate_sha256=hashlib.sha256(validate).hexdigest())
                owner._native_check_continuity_closure_v1(closure, target,
                    scripts / "compile-work-graph.py", pair)
                changed_closure = json.loads(json.dumps(closure))
                changed_closure["execution"]["members"][0]["sha256"] = "0" * 64
                with self.assertRaisesRegex(owner.OperationalEvidenceError, "executed closure differs"):
                    owner._native_check_continuity_closure_v1(changed_closure, target,
                        scripts / "compile-work-graph.py", pair)
                marker = target / "UNSELECTED_TRANSPORT_EXECUTED"
                # Keep the selected byte length so this exercises the digest
                # refusal rather than the earlier exact acquisition bound.
                changed = ("from pathlib import Path\nPath(" + repr(str(marker))
                           + ").write_text('unselected')\n").encode()
                changed += b"#" + b" " * (len(transport) - len(changed) - 2) + b"\n"
                self.assertEqual(len(changed), len(transport))
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
