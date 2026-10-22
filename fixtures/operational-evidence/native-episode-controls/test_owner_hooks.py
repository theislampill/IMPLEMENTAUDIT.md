from native_test_support import source_path, source_text, functions as selected_functions, load, source_api, SCRATCH, PUBLIC_OWNERS
from unittest import mock
import os
import importlib.util
from pathlib import Path
import unittest
import os
import shutil
import subprocess
import tempfile
from unittest import mock
HERE = SCRATCH

class CatalogControls(unittest.TestCase):

    def test_catalog_is_one_parent_filtered_state_db_page(self):
        reader = load('bounded_native_reader.py')
        params = {'parentThreadId': 'root', 'sourceKinds': ['subAgent'], 'limit': 100, 'cursor': None, 'archived': False, 'useStateDbOnly': True}
        try:
            reader.validate_read('thread/list', params)
        except ValueError as error:
            self.fail('bounded parent catalog not implemented: ' + str(error))
        for patch in ({'limit': 101}, {'cursor': 'next'}, {'useStateDbOnly': False}, {'sourceKinds': []}, {'ancestorThreadId': 'root'}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                reader.validate_read('thread/list', params | patch)

    def test_catalog_refuses_partial_duplicate_or_foreign_results(self):
        reader = load('bounded_native_reader.py')
        self.assertTrue(hasattr(reader, 'project_catalog'), 'catalog projection missing')
        params = {'parentThreadId': 'root', 'limit': 100}
        thread = {'id': 'child', 'parentThreadId': 'root', 'source': {'subAgent': {}}, 'threadSource': 'subagent', 'turns': [], 'preview': 'private'}
        self.assertEqual(len(reader.project_catalog({'data': [thread], 'nextCursor': None}, params)), 1)
        self.assertIsNone(reader.project_catalog({'data': [thread | {'threadSource': None}], 'nextCursor': None}, params)[0]['threadSource'])
        self.assertIsNone(reader.project_catalog({'data': [thread | {'parentThreadId': None}], 'nextCursor': None}, params)[0]['parentThreadId'])
        for result in ({'data': [thread], 'nextCursor': 'next'}, {'data': [thread, thread], 'nextCursor': None}, {'data': [thread | {'parentThreadId': 'foreign'}], 'nextCursor': None}):
            with self.subTest(result=result), self.assertRaises(ValueError):
                reader.project_catalog(result, params)

class LaunchControls(unittest.TestCase):

    @unittest.skipUnless(os.name == 'nt', 'Windows handle/launch control; no native credit on other platforms')
    def test_system_tool_selection_ignores_cwd_and_path(self):
        custody = load('bounded_file_custody.py')
        with tempfile.TemporaryDirectory(dir=HERE, prefix='tool-selector-') as directory:
            for name in ('powershell.exe', 'taskkill.exe'):
                (Path(directory) / name).write_bytes(b'not a trusted executable')
            old = os.getcwd()
            try:
                os.chdir(directory)
                with mock.patch.dict(os.environ, {'PATH': directory}):
                    ps = custody.trusted_system_tool('powershell.exe')
                    kill = custody.trusted_system_tool('taskkill.exe')
                    self.assertTrue(ps.is_absolute())
                    self.assertTrue(kill.is_absolute())
                    self.assertFalse(ps.is_relative_to(directory))
                    self.assertFalse(kill.is_relative_to(directory))
                    run = subprocess.run([str(ps), '-NoProfile', '-NonInteractive', '-Command', 'exit 0'], capture_output=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
                    self.assertEqual(run.returncode, 0)
            finally:
                os.chdir(old)

    @unittest.skipUnless(os.name == 'nt', 'Windows handle/launch control; no native credit on other platforms')
    def test_owned_executable_is_immutable_through_launch(self):
        custody = load('bounded_file_custody.py')
        with tempfile.TemporaryDirectory(dir=HERE, prefix='launch-custody-') as directory:
            path = Path(directory) / 'harmless.exe'
            shutil.copyfile(custody.trusted_system_tool('taskkill.exe').parent / 'whoami.exe', path)
            with custody.held_file(path, allow_append=False):
                with self.assertRaises(OSError):
                    path.rename(Path(directory) / 'renamed.exe')
                with self.assertRaises(OSError):
                    with path.open('wb') as stream:
                        stream.write(b'changed')
                run = subprocess.run([str(path)], capture_output=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
                self.assertEqual(run.returncode, 0)
            path.write_bytes(b'guard released')
            self.assertEqual(path.read_bytes(), b'guard released')

    @unittest.skipUnless(os.name == 'nt', 'Windows handle/launch control; no native credit on other platforms')
    def test_native_probe_holds_image_around_complete_transport(self):
        reader = load('bounded_native_reader.py')
        reader.custody = load('bounded_file_custody.py')
        with tempfile.TemporaryDirectory(dir=HERE, prefix='probe-custody-') as directory:
            path = Path(directory) / 'image.bin'
            path.write_bytes(b'owned fixture')

            def transport(*args, **kwargs):
                with self.assertRaises(OSError):
                    path.write_bytes(b'replacement')
                with self.assertRaises(OSError):
                    path.rename(Path(directory) / 'moved.bin')
                return {'transport_returned': True}
            with mock.patch.object(reader, '_probe_held', side_effect=transport):
                self.assertEqual(reader.probe({'native_executable': {'path': str(path)}}), {'transport_returned': True})
if __name__ == '__main__':
    unittest.main(verbosity=2)
