"""TEST_ONLY original-owner controls. Never reads/writes actual /etc or invokes a run.

The adapter maps the owner's fixed /etc selector into a disposable directory and
reports fixture ownership as uid/gid0. Those are test inputs, not host provenance.
All file writes, replacements, descriptors and any exchange syscall are real.
The finite production pins remain untouched; synthetic fixture pins exist only
in the isolated loaded module so these controls qualify custody, not a host image.
"""
import argparse
import ctypes
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import types
import unittest


BEFORE = b'# TEST_ONLY disposable NSS fixture\npasswd:         files systemd\ngroup:          files\nhosts:          files dns\n'
AFTER = b'# TEST_ONLY disposable NSS fixture\npasswd:         files\ngroup:          files\nhosts:          files dns\n'
FOREIGN = b'TEST_ONLY foreign file must remain reachable\n'
RUN = '123456789'
SOURCE = None
FIXTURE_PARENT = None
OBSERVATIONS = []


def load_owner():
    spec = importlib.util.spec_from_file_location('test_only_original_nss', SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Pin the independently hand-written test fixture; no production file edit.
    module.BEFORE_BYTES, module.BEFORE_SHA = len(BEFORE), hashlib.sha256(BEFORE).hexdigest()
    module.AFTER_BYTES, module.AFTER_SHA = len(AFTER), hashlib.sha256(AFTER).hexdigest()
    return module


class FixtureOS:
    def __init__(self, case):
        self.case = case
        self.opened = set()

    def __getattr__(self, name):
        return getattr(os, name)

    def path(self, path, dir_fd=None):
        if isinstance(path, int):
            assert path in self.opened
            return path
        text = os.fspath(path)
        if text == '/':
            return str(self.case.root)
        if text == '/etc':
            return str(self.case.etc)
        if dir_fd is not None:
            assert dir_fd in self.opened and '/' not in text and text not in ('.', '..')
            return text
        actual = Path(text)
        assert actual.is_absolute() and self.case.root in actual.parents
        return str(actual)

    @staticmethod
    def ownership(value):
        fields = {n: getattr(value, n) for n in dir(value) if n.startswith('st_')}
        fields.update(st_uid=0, st_gid=0)
        return types.SimpleNamespace(**fields)

    def getuid(self): return 0
    def geteuid(self): return 0
    def getgid(self): return 0
    def getegid(self): return 0

    def lstat(self, path):
        return self.ownership(os.lstat(self.path(path)))

    def stat(self, path, **kw):
        return self.ownership(os.stat(self.path(path, kw.get('dir_fd')), **kw))

    def fstat(self, fd):
        assert fd in self.opened
        return self.ownership(os.fstat(fd))

    def open(self, path, flags, mode=0o777, **kw):
        fd = os.open(self.path(path, kw.get('dir_fd')), flags, mode, **kw)
        self.opened.add(fd)
        return fd

    def close(self, fd):
        assert fd in self.opened
        os.close(fd)
        self.opened.remove(fd)

    def fdopen(self, fd, mode, **kw):
        assert fd in self.opened
        stream = os.fdopen(fd, mode, **kw)
        if self.case.mode != 'partial_write' or mode != 'wb':
            return stream

        class PartialWrite:
            def __enter__(self): return self
            def __exit__(self, *args): return stream.__exit__(*args)
            def write(self, raw):
                stream.write(raw[:17])
                stream.flush()
                raise OSError('TEST_ONLY partial write')

        return PartialWrite()

    def replace(self, source, target, **kw):
        source = self.path(source, kw.get('src_dir_fd'))
        target = self.path(target, kw.get('dst_dir_fd'))
        is_target = target == 'nsswitch.conf'
        if is_target:
            self.case.boundary()
        os.replace(source, target, **kw)
        if is_target:
            self.case.after_boundary()

    def unlink(self, path, **kw):
        path = self.path(path, kw.get('dir_fd'))
        self.case.unlink_calls += 1
        if self.case.mode == 'unlink_race' and not self.case.injected:
            self.case.injected = True
            temporary = self.case.etc / path
            temporary.rename(self.case.etc / 'owned-before-unlink')
            temporary.write_bytes(FOREIGN)
            self.case.foreign_inode = temporary.stat().st_ino
        return os.unlink(path, **kw)


class Case:
    def __init__(self, mode):
        self.mode = mode
        self.temporary = tempfile.TemporaryDirectory(prefix='TEST_ONLY_nss_', dir=FIXTURE_PARENT)
        self.root = Path(self.temporary.name)
        self.etc = self.root / 'etc'
        self.private = self.root / 'private'
        self.etc.mkdir(mode=0o700)
        self.private.mkdir(mode=0o700)
        self.target = self.etc / 'nsswitch.conf'
        self.target.write_bytes(BEFORE)
        self.target.chmod(0o644)
        self.before_inode = self.target.stat().st_ino
        self.temp = self.etc / ('.implementaudit-r5-g1-nss-' + RUN + '-a1.tmp')
        self.injected = False
        self.failure_injected = False
        self.foreign_inode = None
        self.unlink_calls = 0
        self.boundary_calls = 0
        self.error = None
        self.result = None
        self.module = load_owner()
        self.proxy = FixtureOS(self)
        self.module.os = self.proxy
        if mode in ('missing_exchange_symbol', 'refused_exchange_syscall'):
            library = types.SimpleNamespace()
            if mode == 'refused_exchange_syscall':
                library.renameat2 = lambda *args: -1
            self.module.ctypes = types.SimpleNamespace(
                CDLL=lambda *args, **kw: library, c_int=ctypes.c_int,
                c_char_p=ctypes.c_char_p, c_uint=ctypes.c_uint)
        # The production exchange, when present, uses the real fixture dirfd.
        if hasattr(self.module, 'exchange_entries'):
            actual_exchange = self.module.exchange_entries

            def guarded_exchange(fd, left, right):
                assert fd in self.proxy.opened and right == 'nsswitch.conf'
                assert left == self.temp.name
                self.boundary()
                actual_exchange(fd, left, right)
                self.after_boundary()

            self.module.exchange_entries = guarded_exchange

    def writer(self, path, raw):
        path = Path(path)
        assert self.private in path.parents
        with path.open('xb') as stream:
            stream.write(raw)
        if path.name == 'NSS_CONFIGURATION.next':
            value = json.loads(raw)
            if (self.mode in ('created_failure', 'unlink_race') and
                    value['phase'] == 'TEMPORARY_CREATED' and not self.failure_injected):
                self.failure_injected = True
                # Let checkpoint finish atomically, then fail at the next fsync.
                actual_fsync = self.proxy.fsync

                def fail_once(fd):
                    self.proxy.fsync = actual_fsync
                    raise OSError('TEST_ONLY checkpoint fsync failure')

                self.proxy.fsync = fail_once

    def boundary(self):
        self.boundary_calls += 1
        if self.mode in ('target_race', 'same_bytes_target_race'):
            self.target.rename(self.etc / 'held-original-target')
            self.target.write_bytes(BEFORE if self.mode == 'same_bytes_target_race' else FOREIGN)
            self.target.chmod(0o644)
            self.foreign_inode = self.target.stat().st_ino
            self.injected = True
        elif self.mode == 'source_race':
            self.temp.rename(self.etc / 'held-owned-postimage')
            self.temp.write_bytes(FOREIGN)
            self.temp.chmod(0o644)
            self.foreign_inode = self.temp.stat().st_ino
            self.injected = True
        elif self.mode == 'exchange_refused':
            self.injected = True
            raise OSError('TEST_ONLY exchange unavailable')

    def after_boundary(self):
        if self.mode == 'interrupted_after_exchange':
            self.injected = True
            raise KeyboardInterrupt('TEST_ONLY interruption after namespace effect')

    def run(self):
        try:
            self.result = self.module.prepare(self.private, RUN, self.writer)
        except BaseException as error:
            self.error = type(error).__name__ + ': ' + str(error)
        self.journal = json.loads((self.private / 'NSS_CONFIGURATION.json').read_bytes())
        self.public = self.module.public_state(self.journal)
        self.entries = {p.name: {'inode': p.stat().st_ino,
                        'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': len(p.read_bytes())}
                        for p in self.etc.iterdir() if p.is_file()}
        OBSERVATIONS.append({'case': self.mode, 'TEST_ONLY': True, 'error': self.error,
            'injection_executed': self.injected, 'boundary_calls': self.boundary_calls,
            'unlink_calls': self.unlink_calls, 'before_inode': self.before_inode,
            'foreign_inode': self.foreign_inode, 'entries': self.entries,
            'journal': self.journal, 'public': self.public, 'open_descriptor_count': len(self.proxy.opened)})
        return self

    def close(self):
        # This explicit fixture disposal is test utility ownership, not NSS cleanup.
        assert not self.proxy.opened
        self.temporary.cleanup()


class CustodyTests(unittest.TestCase):
    def episode(self, mode):
        case = Case(mode)
        self.addCleanup(case.close)
        return case.run()

    def test_first_temporary_fstat_failure_closes_fd_and_retains_material(self):
        c = Case('first_temporary_fstat_failure')
        actual_open, actual_fstat = c.proxy.open, c.proxy.fstat
        temporary_fd = None
        observation = None

        def observed_open(path, flags, mode=0o777, **kw):
            nonlocal temporary_fd
            fd = actual_open(path, flags, mode, **kw)
            if path == c.temp.name and flags & os.O_WRONLY:
                temporary_fd = fd
            return fd

        def first_fstat(fd):
            if fd == temporary_fd and not c.injected:
                c.injected = True
                raise OSError(errno.EIO, 'TEST_ONLY first temporary fstat failure')
            return actual_fstat(fd)

        c.proxy.open, c.proxy.fstat = observed_open, first_fstat
        try:
            c.run()
            observation = OBSERVATIONS[-1]
            self.assertTrue(c.injected)
            self.assertIn('OSError: [Errno 5]', c.error)
            self.assertEqual(c.boundary_calls, 0)
            self.assertEqual(c.unlink_calls, 0)
            self.assertEqual(c.target.read_bytes(), BEFORE)
            self.assertEqual(c.target.stat().st_ino, c.before_inode)
            self.assertEqual(c.temp.read_bytes(), b'')
            self.assertEqual(c.journal['replacement'], 'NOT_STARTED')
            self.assertIs(c.journal['configured'], False)
            self.assertFalse(c.journal['temporary_created'])
            self.assertFalse(c.journal['temporary_removed'])
            self.assertEqual(c.public['temporary_false_meaning'],
                             'NO_DURABLE_COMPLETION_OBSERVATION_NOT_PROOF_OF_ABSENCE')
            with self.assertRaises(ValueError):
                c.module.verify_configured(c.journal)
            self.assertFalse(c.proxy.opened, 'owner left the successfully opened temporary fd open')
        finally:
            # Preserve the observed owner failure before test-utility disposal.
            # Closing a leaked fd here cannot turn the preceding assertion green.
            leaked = tuple(c.proxy.opened)
            for fd in leaked:
                c.proxy.close(fd)
            c.close()
            if observation is not None:
                observation['test_utility_cleanup'] = {
                    'authority': 'TEST_FIXTURE_ONLY',
                    'explicitly_closed_owner_left_open_count': len(leaked),
                    'remaining_owner_descriptors': len(c.proxy.opened),
                    'fixture_root_absent': not c.root.exists()}

    def test_pre_effect_failure_retains_allocated_material(self):
        c = self.episode('created_failure')
        self.assertIsNotNone(c.error)
        self.assertTrue(c.temp.exists(), 'allocated temporary material was deleted')
        self.assertFalse(c.journal['temporary_removed'], 'retention was labelled removal')
        self.assertEqual(c.target.read_bytes(), BEFORE)
        self.assertEqual(c.journal['replacement'], 'NOT_STARTED')

    def test_unlink_boundary_cannot_delete_substituted_foreign_name(self):
        c = self.episode('unlink_race')
        self.assertTrue(c.temp.exists(), 'cleanup removed the selected name')
        if c.injected:
            self.assertEqual(c.temp.stat().st_ino, c.foreign_inode, 'foreign inode was deleted')
            self.assertEqual(c.temp.read_bytes(), FOREIGN)
        self.assertFalse(c.journal['temporary_removed'])

    def test_partial_write_material_is_retained_without_removal_claim(self):
        c = self.episode('partial_write')
        self.assertIsNotNone(c.error)
        self.assertTrue(c.temp.exists(), 'partially written evidence was removed')
        self.assertEqual(c.temp.read_bytes(), AFTER[:17])
        self.assertEqual(c.target.read_bytes(), BEFORE)
        self.assertFalse(c.journal['temporary_removed'])
        self.assertEqual(c.journal['replacement'], 'NOT_STARTED')

    def test_late_target_substitution_is_preserved_and_refused(self):
        c = self.episode('target_race')
        self.assertTrue(c.injected)
        self.assertIn(c.foreign_inode, [v['inode'] for v in c.entries.values()], 'displaced foreign target was discarded')
        self.assertIsNotNone(c.error)
        self.assertIsNone(c.journal['configured'])
        self.assertEqual(c.journal['replacement'], 'STARTED_OUTCOME_UNKNOWN')

    def test_same_bytes_new_target_inode_cannot_pass_currentness(self):
        c = self.episode('same_bytes_target_race')
        self.assertTrue(c.injected)
        self.assertIsNotNone(c.error, 'same bytes concealed a substituted target inode')
        self.assertIn(c.foreign_inode, [v['inode'] for v in c.entries.values()])
        self.assertIsNone(c.journal['configured'])

    def test_late_temporary_substitution_retains_original_target(self):
        c = self.episode('source_race')
        self.assertTrue(c.injected)
        self.assertIn(c.before_inode, [v['inode'] for v in c.entries.values()], 'original target inode was discarded')
        self.assertIn(c.foreign_inode, [v['inode'] for v in c.entries.values()])
        self.assertIsNotNone(c.error)
        self.assertIsNone(c.journal['configured'])

    def test_interruption_after_effect_keeps_both_inodes_and_unknown(self):
        c = self.episode('interrupted_after_exchange')
        self.assertTrue(c.injected)
        self.assertEqual(c.target.read_bytes(), AFTER)
        self.assertIn(c.before_inode, [v['inode'] for v in c.entries.values()])
        self.assertIsNone(c.journal['configured'])
        self.assertFalse(c.journal['temporary_removed'])
        with self.assertRaises(ValueError):
            c.module.verify_configured(c.journal)

    def test_refused_exchange_never_falls_back_to_destructive_replace(self):
        c = self.episode('exchange_refused')
        self.assertTrue(c.injected)
        self.assertEqual(c.target.read_bytes(), BEFORE)
        self.assertEqual(c.target.stat().st_ino, c.before_inode)
        self.assertTrue(c.temp.exists())
        self.assertIsNone(c.journal['configured'])

    def test_missing_exchange_symbol_refuses_with_material_retained(self):
        c = self.episode('missing_exchange_symbol')
        self.assertIsNotNone(c.error)
        self.assertEqual(c.journal['failure_code'], 'NSS_CONFIGURATION_EXCHANGE_UNAVAILABLE')
        self.assertEqual(c.target.read_bytes(), BEFORE)
        self.assertTrue(c.temp.exists())
        self.assertIsNone(c.journal['configured'])

    def test_refused_exchange_syscall_refuses_without_destructive_fallback(self):
        c = self.episode('refused_exchange_syscall')
        self.assertIsNotNone(c.error)
        self.assertEqual(c.journal['failure_code'], 'NSS_CONFIGURATION_EXCHANGE_REFUSED')
        self.assertEqual(c.target.read_bytes(), BEFORE)
        self.assertTrue(c.temp.exists())
        self.assertIsNone(c.journal['configured'])

    def test_positive_journal_final_readback_and_no_replay(self):
        c = self.episode('positive')
        self.assertIsNone(c.error)
        self.assertEqual(c.target.read_bytes(), AFTER)
        self.assertTrue(c.module.verify_configured(c.journal)['configured'])
        self.assertEqual(c.public['disposition'], 'RETAIN_CONFIGURED_FILE_UNTIL_VM_DISPOSAL')
        self.assertFalse(c.public['temporary_removal_recorded'])
        with self.assertRaisesRegex(ValueError, 'NSS_CONFIGURATION_NO_REPLAY'):
            c.module.prepare(c.private, RUN, c.writer)

    def test_final_drift_and_forged_success_are_refused(self):
        c = self.episode('positive')
        self.assertIsNone(c.error)
        forged = dict(c.journal, after=None)
        with self.assertRaises(ValueError):
            c.module.public_state(forged)
        c.target.write_bytes(FOREIGN)
        with self.assertRaises(ValueError):
            c.module.verify_configured(c.journal)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--owner', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--fixtures', type=Path, required=True)
    args = parser.parse_args()
    SOURCE = args.owner.resolve(strict=True)
    FIXTURE_PARENT = args.fixtures.resolve(strict=True)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(unittest.defaultTestLoader.loadTestsFromTestCase(CustodyTests))
    payload = {'schema': 'test-only.original-nss-custody-controls.v1', 'authority': 'NONE',
        'source': {'bytes': SOURCE.stat().st_size, 'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest()},
        'fixture_scope': 'DISPOSABLE_FILES_WITH_TEST_ONLY_PATH_UID_AND_FINITE_IMAGE_ADAPTER',
        'system_nss_access': False, 'hosted_or_original_execution': False,
        'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'observations': OBSERVATIONS}
    with args.evidence.open('x') as stream:
        json.dump(payload, stream, indent=2)
        stream.write('\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
