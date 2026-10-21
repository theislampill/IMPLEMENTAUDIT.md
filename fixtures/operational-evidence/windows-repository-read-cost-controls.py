"""Actual Windows held-directory controls on disposable roots only.

No native-current acquisition, publication, source adoption or budget credit.
"""
import argparse
import contextlib
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument('source_root', type=Path)
parser.add_argument('--report', type=Path)
parser.add_argument('--test', action='append')
args = parser.parse_args()
ROOT = args.source_root.resolve()
spec = importlib.util.spec_from_file_location('windows_repository_cost', ROOT / 'scripts/operational-evidence.py')
oe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oe)
METRICS = {}


def git(root, *arguments):
    environment = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    environment.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
    return subprocess.run(['git', '-C', str(root), *arguments], env=environment,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


@unittest.skipUnless(os.name == 'nt', 'actual Windows handles are required')
class WindowsRepositoryReadCostTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='oe-windows-directory-cost-')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.root = self.base / 'repository'
        self.root.mkdir()
        self.shared = self.root / 'scope-cost-shared'
        self.shared.mkdir()
        self.first = self.shared / 'first.txt'
        self.first.write_bytes(b'first exact bytes\n')
        self.second = self.shared / 'second.txt'
        self.second.write_bytes(b'second exact bytes\n')

    def test_public_collection_reuses_parent_handles_and_keeps_three_fences(self):
        for index in range(22):
            (self.shared / ('member-%02d.txt' % index)).write_bytes(('row %d\n' % index).encode())
        git(self.root, 'init', '-q')
        git(self.root, 'add', '--all')
        git(self.root, '-c', 'user.name=Constructed Windows control',
            '-c', 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false',
            'commit', '-qm', 'Constructed held-directory fixture')
        opened, fences = [], []
        original_open = oe._windows_open_child_v1
        original_fence = oe._require_repository_snapshot_stable
        def child(parent, name, directory, **kwargs):
            if directory and name == self.shared.name:
                opened.append(name)
            return original_open(parent, name, directory, **kwargs)
        def fence(*a, **kw):
            result = original_fence(*a, **kw)
            fences.append(True)
            return result
        started = time.perf_counter()
        with patch.object(oe, '_windows_open_child_v1', side_effect=child), \
                patch.object(oe, '_require_repository_snapshot_stable', side_effect=fence):
            collection = oe.collect_repository(self.root)
        METRICS['constructed_collection'] = {
            'seconds': time.perf_counter() - started, 'shared_directory_opens': len(opened),
            'stability_fences': len(fences), 'facts': len(collection['facts'])}
        self.assertEqual(collection['repository']['worktree_state'], 'CLEAN')
        self.assertEqual(len(collection['facts']), 24)
        self.assertEqual(len(fences), 3)
        self.assertEqual(len(opened), 1, 'same physical parent reopened for every leaf/fence')

    @contextlib.contextmanager
    def tracked_kernel(self):
        kernel = oe._snapshot_windows_kernel_v1()
        create, close, child = kernel.CreateFileW, kernel.CloseHandle, oe._windows_open_child_v1
        live, peak = set(), [0]
        def acquired(handle):
            if handle != ctypes.c_void_p(-1).value:
                self.assertNotIn(handle, live)
                live.add(handle)
                peak[0] = max(peak[0], len(live))
            return handle
        def create_file(*a):
            return acquired(create(*a))
        def child_file(*a, **kw):
            return acquired(child(*a, **kw))
        def close_file(handle):
            result = close(handle)
            self.assertTrue(result, 'actual CloseHandle failed')
            self.assertIn(handle, live)
            live.remove(handle)
            return result
        kernel.CreateFileW, kernel.CloseHandle = create_file, close_file
        with patch.object(oe, '_snapshot_windows_kernel_v1', return_value=kernel), \
                patch.object(oe, '_windows_open_child_v1', side_effect=child_file):
            yield kernel, live, peak
        self.assertEqual(live, set(), 'scope leaked an actual file/directory handle')

    @contextlib.contextmanager
    def attributes_only_directory_access(self, weak_name=None):
        # Inject a stronger-access denial only. The fallback opens and all
        # substitution/read/refusal behavior still use actual Windows handles.
        original = oe._windows_open_child_v1
        denied = []
        def child(parent, name, directory, **kwargs):
            if directory and kwargs.get('hold_directory') and (weak_name is None or name == weak_name):
                denied.append(name)
                raise PermissionError('constructed read/list access denial')
            return original(parent, name, directory, **kwargs)
        with patch.object(oe, '_windows_open_child_v1', side_effect=child):
            yield denied

    def test_cached_parent_replacement_is_refused_and_scope_releases_handles(self):
        moved = self.shared.with_name('moved')
        with self.tracked_kernel(), self.attributes_only_directory_access() as denied:
            with oe._repository_read_scope_v1(self.root) as read:
                self.assertEqual(read(self.first)[0], b'first exact bytes\n')
                # Existing READ_ATTRIBUTES access does not promise rename denial
                # after the leaf closes. Canonical-name reuse checks must detect it.
                self.shared.rename(moved)
                self.shared.mkdir()
                self.second.write_bytes(b'replacement bytes must not be returned\n')
                with self.assertRaises(OSError):
                    read(self.second)
            with self.assertRaises(OSError):
                read(self.first)
        self.assertTrue(denied)
        self.second.unlink()
        self.shared.rmdir()
        moved.rename(self.shared)

    def test_strong_ancestry_reuses_names_but_keeps_fresh_metadata(self):
        original_name, original_info = oe._windows_handle_name_v1, oe._snapshot_handle_info_v1
        names, metadata = [], []
        identity = self.shared.stat().st_ino
        def name(kernel, handle):
            value = original_name(kernel, handle)
            if value == self.shared:
                names.append(True)
            return value
        def info(kernel, handle):
            value = original_info(kernel, handle)
            if (value.file_index_high << 32) | value.file_index_low == identity:
                metadata.append(True)
            return value
        with patch.object(oe, '_windows_handle_name_v1', side_effect=name), \
                patch.object(oe, '_snapshot_handle_info_v1', side_effect=info):
            with oe._repository_read_scope_v1(self.root) as read:
                self.assertEqual(read(self.first)[0], b'first exact bytes\n')
                self.assertEqual(read(self.second)[0], b'second exact bytes\n')
                self.assertEqual(len(names), 1, 'strongly held ancestry repeated canonical-name work')
                self.assertGreaterEqual(len(metadata), 4)
                with self.assertRaises(OSError):
                    self.shared.rename(self.shared.with_name('strong-rename-attempt'))

    def test_weak_ancestor_retains_descendant_name_rechecks(self):
        original = oe._windows_handle_name_v1
        names = []
        def name(kernel, handle):
            value = original(kernel, handle)
            if value == self.shared:
                names.append(True)
            return value
        with self.attributes_only_directory_access(self.root.name) as denied, \
                patch.object(oe, '_windows_handle_name_v1', side_effect=name):
            with oe._repository_read_scope_v1(self.root) as read:
                self.assertEqual(read(self.first)[0], b'first exact bytes\n')
                self.assertEqual(read(self.second)[0], b'second exact bytes\n')
        self.assertEqual(denied, [self.root.name])
        self.assertEqual(len(names), 2)

    def test_handles_are_bounded_reopened_on_eviction_and_released_on_error(self):
        paths = []
        for index in range(160):
            folder = self.root / ('dir-%03d' % index)
            folder.mkdir()
            target = folder / 'data.txt'
            target.write_bytes(str(index).encode())
            paths.append(target)
        with self.tracked_kernel() as (kernel, live, peak):
            with oe._repository_read_scope_v1(self.root) as read:
                for index, target in enumerate(paths):
                    self.assertEqual(read(target)[0], str(index).encode())
                self.assertEqual(read(paths[0])[0], b'0')
            self.assertEqual(live, set())
            self.assertLessEqual(peak[0], 129)
            with self.assertRaisesRegex(OSError, 'injected bounded read failure'):
                with oe._repository_read_scope_v1(self.root) as read:
                    with patch.object(kernel, 'ReadFile', side_effect=OSError('injected bounded read failure')):
                        read(self.first)
            self.assertEqual(live, set())
        METRICS['handle_bound'] = {'peak_actual_handles': peak[0], 'released': not live}

    def test_parent_name_change_after_cached_validation_is_refused_before_read(self):
        moved = self.shared.with_name('renamed-after-validation')
        changed, reads = [], []
        with self.tracked_kernel() as (kernel, live, peak), self.attributes_only_directory_access() as denied:
            original_read = kernel.ReadFile
            # Retain the tracked opener, then inject exactly after every cached
            # parent was checked and immediately before the leaf is acquired.
            tracked_child = oe._windows_open_child_v1
            def child(parent, name, directory, **kw):
                if not directory and name == self.second.name and not changed:
                    self.shared.rename(moved)
                    self.shared.mkdir()
                    self.second.write_bytes(b'outside replacement must not be read\n')
                    changed.append(True)
                return tracked_child(parent, name, directory, **kw)
            def read_file(*a):
                if changed:
                    reads.append(True)
                return original_read(*a)
            with oe._repository_read_scope_v1(self.root) as read:
                self.assertEqual(read(self.first)[0], b'first exact bytes\n')
                with patch.object(oe, '_windows_open_child_v1', side_effect=child), \
                        patch.object(kernel, 'ReadFile', side_effect=read_file):
                    with self.assertRaises(OSError):
                        read(self.second)
            self.assertEqual(changed, [True])
            self.assertEqual(reads, [])
            self.assertEqual(live, set())
        self.assertTrue(denied)

    def test_cached_long_name_does_not_admit_a_short_alias(self):
        kernel = oe._snapshot_windows_kernel_v1()
        kernel.GetShortPathNameW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
        kernel.GetShortPathNameW.restype = ctypes.c_uint32
        buffer = ctypes.create_unicode_buffer(32768)
        self.assertGreater(kernel.GetShortPathNameW(str(self.shared), buffer, len(buffer)), 0)
        alias_parent = self.shared.parent / Path(buffer.value).name
        if str(alias_parent).casefold() == str(self.shared).casefold():
            self.skipTest('volume assigned no short alias to this disposable directory')
        with oe._repository_read_scope_v1(self.root) as read:
            self.assertEqual(read(self.first)[0], b'first exact bytes\n')
            for _ in range(2):
                with self.assertRaises(OSError):
                    read(alias_parent / self.first.name)

    def test_deep_path_fallback_preserves_uncached_bytes_and_cleanup(self):
        folder = self.root
        for _ in range(130):
            folder /= 'p'
            folder.mkdir()
        target = folder / 'data.txt'
        target.write_bytes(b'deep path bytes\n')
        expected = oe._read_repository_path(target, root=self.root)
        with self.tracked_kernel() as (kernel, live, peak):
            with oe._repository_read_scope_v1(self.root) as read:
                self.assertEqual(read(target), expected)
                self.assertEqual(live, set(), 'deep fallback retained uncached handles')
            self.assertEqual(live, set())
        METRICS['deep_fallback'] = {'parent_depth': len(target.parts) - 1,
                                    'peak_actual_handles': peak[0], 'released': not live}

    def junction(self, kernel, parent, outside):
        kernel.DeviceIoControl.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p,
            ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p]
        kernel.DeviceIoControl.restype = ctypes.c_int
        substitute, printed = ('\\??\\' + str(outside)).encode('utf-16-le'), str(outside).encode('utf-16-le')
        names = substitute + b'\0\0' + printed + b'\0\0'
        raw = struct.pack('<IHHHHHH', 0xA0000003, 8 + len(names), 0,
                          0, len(substitute), len(substitute) + 2, len(printed)) + names
        writer = kernel.CreateFileW(str(parent), 0x100, 7, None, 3, 0x02200000, None)
        self.assertNotEqual(writer, ctypes.c_void_p(-1).value)
        try:
            data, count = ctypes.create_string_buffer(raw), ctypes.c_uint32()
            self.assertTrue(kernel.DeviceIoControl(writer, 0x900A4, data, len(raw), None, 0,
                                                  ctypes.byref(count), None))
        finally:
            kernel.CloseHandle(writer)

    def test_cached_parent_metadata_substitution_never_reads_outside_bytes(self):
        for during_validation in (False, True):
            with self.subTest(during_validation=during_validation):
                parent = self.root / ('empty-' + str(during_validation))
                outside = self.base / ('outside-' + str(during_validation))
                parent.mkdir()
                outside.mkdir()
                (outside / 'sentinel.txt').write_bytes(b'outside sentinel\n')
                identity = parent.stat().st_ino
                changed, outside_reads = [], []
                original_info = oe._snapshot_handle_info_v1
                with self.tracked_kernel() as (kernel, live, peak):
                    original_read = kernel.ReadFile
                    def read_file(handle, *a):
                        if oe._windows_handle_name_v1(kernel, handle) == Path(outside / 'sentinel.txt'):
                            outside_reads.append(True)
                        return original_read(handle, *a)
                    def info(api, handle):
                        value = original_info(api, handle)
                        if not changed and (value.file_index_high << 32) | value.file_index_low == identity:
                            self.junction(kernel, parent, outside)
                            changed.append(True)
                        return value
                    try:
                        with oe._repository_read_scope_v1(self.root) as read:
                            with self.assertRaises(OSError):
                                read(parent / 'missing.txt')
                            if not during_validation:
                                self.junction(kernel, parent, outside)
                                changed.append(True)
                            with patch.object(kernel, 'ReadFile', side_effect=read_file), \
                                    patch.object(oe, '_snapshot_handle_info_v1', side_effect=info if during_validation else original_info):
                                with self.assertRaises(OSError):
                                    read(parent / 'sentinel.txt')
                        self.assertEqual(changed, [True])
                        self.assertEqual(outside_reads, [])
                        self.assertEqual(live, set())
                    finally:
                        if parent.lstat().st_file_attributes & 0x400:
                            parent.rmdir()  # Exact disposable junction, never its target.

    def test_cached_reader_keeps_hardlink_alias_bounds_and_new_transaction_bytes(self):
        with self.attributes_only_directory_access(), oe._repository_read_scope_v1(self.root) as read:
            self.assertEqual(read(self.first, maximum=len(self.first.read_bytes()))[0], self.first.read_bytes())
            for target in (self.shared, Path(str(self.first) + '.'), Path(str(self.first) + ':stream'),
                           self.root / 'NUL', self.base / 'outside.txt'):
                with self.subTest(path=target), self.assertRaises((OSError, ValueError)):
                    read(target)
            with self.assertRaises(OSError):
                read(self.first, maximum=1)
            os.link(self.first, self.root / 'hardlink.txt')
            with self.assertRaises(OSError):
                read(self.first)
        (self.root / 'hardlink.txt').unlink()
        self.first.write_bytes(b'new transaction bytes\n')
        with oe._repository_read_scope_v1(self.root) as read:
            self.assertEqual(read(self.first)[0], b'new transaction bytes\n')

    def test_strong_reader_refuses_a_preexisting_hardlink(self):
        os.link(self.first, self.root / 'hardlink.txt')
        with oe._repository_read_scope_v1(self.root) as read:
            with self.assertRaises(OSError):
                read(self.first)
            with self.assertRaises(OSError):
                read(self.root / 'hardlink.txt')


if __name__ == '__main__':
    suite = (unittest.TestSuite(WindowsRepositoryReadCostTests(name) for name in args.test)
             if args.test else unittest.defaultTestLoader.loadTestsFromTestCase(WindowsRepositoryReadCostTests))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {'scope': 'ACTUAL_WINDOWS_DISPOSABLE_ROOT_CONTROLS_NOT_NATIVE_ACCEPTANCE',
              'source_sha256': hashlib.sha256((ROOT / 'scripts/operational-evidence.py').read_bytes()).hexdigest(),
              'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
              'skipped': len(result.skipped), 'metrics': METRICS}
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, sort_keys=True))
    raise SystemExit(not result.wasSuccessful())
