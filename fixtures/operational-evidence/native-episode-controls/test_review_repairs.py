from native_test_support import source_path, source_text, functions as selected_functions, load, source_api, SCRATCH, PUBLIC_OWNERS
from unittest import mock
import os
import contextlib
import ctypes
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest import mock
HERE = SCRATCH

class ReviewRepairs(unittest.TestCase):

    def test_loader_executes_verified_bytes_without_reopening_code(self):
        owner = load('compaction-source-owner-codex-app.py')
        with tempfile.TemporaryDirectory(dir=HERE, prefix='loader-control-') as directory:
            path = Path(directory) / 'sample.py'
            path.write_text('raise RuntimeError("unverified path executed")')
            with mock.patch.object(owner, 'HERE', Path(directory)), mock.patch.object(owner, '_np_read_pin', return_value=b'VALUE = 17\n'):
                result = owner._np_module({'path': str(path)}, 'sample.py')
            self.assertEqual(result.VALUE, 17)

    @unittest.skipUnless(os.name == 'nt', 'Windows handle/launch control; no native credit on other platforms')
    def test_hardlink_refused(self):
        wrapper = source_api()
        with tempfile.TemporaryDirectory(dir=HERE, prefix='physical-control-') as directory:
            path = Path(directory) / 'a long source name.jsonl'
            path.write_bytes(b'hello\n')
            link = Path(directory) / 'copy.jsonl'
            os.link(path, link)
            with self.assertRaises((ValueError, OSError)):
                wrapper.physical(path)

    @unittest.skipUnless(os.name == 'nt', 'Windows handle/launch control; no native credit on other platforms')
    def test_real_short_alias_refused(self):
        wrapper = source_api()
        with tempfile.TemporaryDirectory(dir=HERE, prefix='short-alias-control-') as directory:
            path = Path(directory) / 'a long native source file.jsonl'
            path.write_bytes(b'hello\n')
            k = ctypes.WinDLL('kernel32', use_last_error=True)
            k.GetShortPathNameW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
            k.GetShortPathNameW.restype = ctypes.c_uint32
            buffer = ctypes.create_unicode_buffer(32768)
            size = k.GetShortPathNameW(str(path), buffer, len(buffer))
            self.assertGreater(size, 0)
            if buffer.value.casefold() == str(path).casefold():
                self.skipTest('volume supplies no distinct short alias')
            with self.assertRaises((ValueError, OSError)):
                wrapper.physical(Path(buffer.value))

    @unittest.skipUnless(os.name == 'nt', 'Windows handle/launch control; no native credit on other platforms')
    def test_growth_is_rejected_without_reading_surplus(self):
        wrapper = source_api()
        with tempfile.TemporaryDirectory(dir=HERE, prefix='growth-control-') as directory:
            path = Path(directory) / 'binary.bin'
            initial = 2 * 1024 * 1024
            path.write_bytes(b'x' * initial)
            normal = wrapper.reader.custody.held_file
            observed = {'bytes': 0, 'grew': False}

            @contextlib.contextmanager
            def growing(selected):
                with normal(selected) as stream:

                    class Proxy:

                        def fileno(self):
                            return stream.fileno()

                        def read(self, n):
                            block = stream.read(n)
                            observed['bytes'] += len(block)
                            if not observed['grew']:
                                with path.open('ab') as out:
                                    out.write(b'surplus')
                                observed['grew'] = True
                            return block
                    yield Proxy()
            with mock.patch.object(wrapper.reader.custody, 'held_file', growing), self.assertRaises(ValueError):
                wrapper.reader.file_pin(path)
            self.assertTrue(observed['grew'])
            self.assertLessEqual(observed['bytes'], initial)

    @unittest.skipUnless(os.name == 'nt', 'Windows handle/launch control; no native credit on other platforms')
    def test_parent_cannot_be_replaced_while_source_is_held_and_append_remains_usable(self):
        wrapper = source_api()
        self.assertTrue(hasattr(wrapper.owner, 'custody'), 'held parent custody is missing')
        with tempfile.TemporaryDirectory(dir=HERE, prefix='parent-control-') as directory:
            parent = Path(directory) / 'parent'
            parent.mkdir()
            path = parent / 'live.jsonl'
            path.write_bytes(b'first\n')
            with wrapper.owner.custody.held_file(path) as stream:
                with self.assertRaises(OSError):
                    parent.rename(Path(directory) / 'moved')
                with path.open('ab') as writer:
                    writer.write(b'second\n')
                self.assertEqual(stream.read(6), b'first\n')
            self.assertEqual(path.read_bytes(), b'first\nsecond\n')

    def test_selected_package_ancestors_hold_without_directory_synchronize_right(self):
        custody = load('bounded_file_custody.py')
        observed = {}

        class NativeCall:

            def __call__(self, *args):
                observed['args'] = args
                ctypes.cast(args[0], ctypes.POINTER(ctypes.c_void_p))[0] = ctypes.c_void_p(7)
                return 0
        nt = types.SimpleNamespace(NtCreateFile=NativeCall(), RtlNtStatusToDosError=NativeCall())
        with mock.patch.object(custody.ctypes, 'WinDLL', return_value=nt, create=True):
            self.assertEqual(custody.open_child(123, 'owned-directory', True), 7)
        args = observed['args']
        attributes = ctypes.cast(args[2], ctypes.POINTER(custody.ObjectAttributes)).contents
        self.assertEqual(args[1], 128)
        self.assertEqual(args[6], 1)
        self.assertEqual(args[8] & 32, 0)
        self.assertTrue(args[8] & 2097152)
        self.assertEqual(attributes.root, 123)
        self.assertTrue(attributes.attributes & 4096)

    def test_cleanup_attempts_remaining_steps_after_each_failure(self):
        reader = load('bounded_native_reader.py')
        self.assertTrue(hasattr(reader, 'cleanup_probe'), 'failure-complete cleanup is missing')
        calls = []

        class Stream:

            def __init__(self, name):
                self.name = name

            def close(self):
                calls.append('close_' + self.name)
                if self.name == 'stdin':
                    raise RuntimeError('close injection')

        class Process:
            pid = 12345
            stdin = Stream('stdin')
            stdout = Stream('stdout')
            stderr = Stream('stderr')

            def wait(self, timeout):
                calls.append('wait')
                if calls.count('wait') == 1:
                    raise subprocess.TimeoutExpired('probe', timeout)
                return 0

            def kill(self):
                calls.append('kill')

            def poll(self):
                calls.append('poll')
                return 0 if calls.count('wait') > 1 else None

        class Thread:

            def join(self, timeout):
                calls.append('join')
                raise RuntimeError('join injection')

            def is_alive(self):
                return False
        state = {name: {'done': True, 'eof': True, 'failure': None} for name in ('stdout', 'stderr')}
        with mock.patch.object(reader.subprocess, 'run', side_effect=subprocess.TimeoutExpired('taskkill', 5)), mock.patch.object(reader.custody, 'trusted_system_tool', return_value=HERE / 'fixture-taskkill.exe'), mock.patch.object(reader.subprocess, 'CREATE_NO_WINDOW', 0, create=True):
            result = reader.cleanup_probe(Process(), [Thread()], state)
        self.assertIn('close_stdout', calls)
        self.assertIn('close_stderr', calls)
        self.assertIn('kill', calls)
        self.assertGreaterEqual(len(result['cleanup_failures']), 3)
        self.assertTrue(result['process_terminated'])
if __name__ == '__main__':
    unittest.main(verbosity=2)
