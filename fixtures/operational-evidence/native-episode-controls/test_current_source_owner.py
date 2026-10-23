from native_test_support import source_path, source_text, functions as selected_functions, load, source_api, SCRATCH, PUBLIC_OWNERS
from unittest import mock
import os
'Owner-side controls: wrong relation, physical substitution, and private records.'
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
HERE = SCRATCH

class CurrentSourceContract(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = source_api()

    def api(self):
        self.assertIsNotNone(self.mod, 'current source owner path is not implemented')
        return self.mod

    def public_row(self):
        return {'type': 'response_item', 'ordinal': 17, 'metadata': {'client_authored': False, 'retained_source': {'id': {'message_id': 'm', 'turn_id': 't', 'role': 'assistant'}, 'revision': 'retained_r', 'complete': True}}, 'payload': {'type': 'message', 'id': 'm', 'role': 'assistant', 'phase': 'commentary', 'content': [{'type': 'output_text', 'text': 'hello', 'annotations': [], 'logprobs': []}]}}

    def test_public_record_identity_and_private_refusal(self):
        mod = self.api()
        got = mod.public_record(self.public_row())
        self.assertEqual(got['body_sha256'], '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824')
        self.assertEqual(got['revision'], 'retained_r')
        self.assertNotIn('hello', str(got))
        for change in ('analysis', 'reasoning', 'wrong_id', 'client_authored', 'incomplete', 'annotations', 'logprobs', 'unknown_extension'):
            row = self.public_row()
            if change == 'analysis':
                row['payload']['phase'] = 'analysis'
            if change == 'reasoning':
                row['payload']['type'] = 'reasoning'
            if change == 'wrong_id':
                row['payload']['id'] = 'other'
            if change == 'client_authored':
                row['metadata']['client_authored'] = True
            if change == 'incomplete':
                row['metadata']['retained_source']['complete'] = False
            if change == 'annotations':
                row['payload']['content'][0]['annotations'] = [{'unqualified': True}]
            if change == 'logprobs':
                row['payload']['content'][0]['logprobs'] = [1]
            if change == 'unknown_extension':
                row['payload']['content'][0]['unknown'] = 'x'
            with self.subTest(change=change), self.assertRaises(ValueError):
                mod.public_record(row)

    def pair(self):
        mod = self.api()
        root = {'id': mod.ROOT_ID, 'sessionId': mod.ROOT_ID, 'parentThreadId': None, 'cliVersion': mod.CLI_VERSION, 'cwd': str(mod.CWD), 'source_kind': 'vscode', 'threadSource': 'user', 'path': str(mod.ROOT_SOURCE), 'ephemeral': False, 'historyMode': 'paginated'}
        child = root | {'id': 'child', 'sessionId': 'child', 'parentThreadId': mod.ROOT_ID, 'source_kind': 'subAgent', 'threadSource': 'subagent'}
        root_header = {'id': mod.ROOT_ID, 'session_id': mod.ROOT_ID, 'cli_version': mod.CLI_VERSION, 'cwd': str(mod.CWD), 'thread_source': 'user'}
        child_header = root_header | {'id': 'child', 'parent_thread_id': mod.ROOT_ID, 'agent_path': '/root/child', 'thread_source': 'subagent'}
        return (root, child, root_header, child_header)

    def test_current_version_relation_handles_native_session_difference(self):
        mod = self.api()
        self.assertEqual(mod.validate_relation(*self.pair()), 'child')
        for part, key, value in [(1, 'parentThreadId', 'foreign'), (1, 'sessionId', mod.ROOT_ID), (3, 'session_id', 'child'), (3, 'parent_thread_id', 'foreign'), (1, 'cliVersion', 'old')]:
            pair = list(self.pair())
            pair[part] = pair[part] | {key: value}
            with self.subTest(part=part, key=key), self.assertRaises(ValueError):
                mod.validate_relation(*pair)

    @unittest.skipUnless(os.name == 'nt', 'Windows handle/launch control; no native credit on other platforms')
    def test_exact_physical_range_refuses_changed_bytes_offset_and_identity(self):
        mod = self.api()
        with tempfile.TemporaryDirectory(dir=HERE, prefix='owner-control-') as directory:
            path = Path(directory) / 'source.jsonl'
            prefix = b'{"type":"unselected"}\n'
            raw = json.dumps(self.public_row()).encode() + b'\n'
            path.write_bytes(prefix + raw)
            physical = mod.physical(path)
            locator = {'offset': len(prefix), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'ordinal': 17}
            good = mod.read_public(path, physical, locator, path.stat().st_size)
            self.assertEqual(good['revision'], 'retained_r')
            for changed in (locator | {'offset': len(prefix) + 1}, locator | {'sha256': '0' * 64}, locator | {'ordinal': 18}):
                with self.subTest(changed=changed), self.assertRaises(ValueError):
                    mod.read_public(path, physical, changed, path.stat().st_size)
            with self.assertRaises(ValueError):
                mod.read_public(path, physical | {'inode': physical['inode'] + 1}, locator, path.stat().st_size)
            path.write_bytes(prefix + raw.replace(b'hello', b'jello'))
            with self.assertRaises(ValueError):
                mod.read_public(path, physical, locator, path.stat().st_size)

    def test_changed_revision_and_native_body_cannot_bind(self):
        mod = self.api()
        source = mod.public_record(self.public_row())
        native = {key: source[key] for key in ('id', 'turn_id', 'phase', 'body_bytes', 'body_sha256')}
        mod.bind_public(source, native)
        for key, value in (('id', 'other'), ('turn_id', 'foreign'), ('body_sha256', '0' * 64)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                mod.bind_public(source, native | {key: value})
        with self.assertRaises(ValueError):
            mod.same_selection(source, source | {'revision': 'replaced'})

    def test_private_owner_selection_alone_chooses_child(self):
        mod = self.api()
        self.assertTrue(hasattr(mod.owner, 'selected_child'), 'fixed child selection is not implemented')
        selected = {'root_thread_id': 'root', 'selected_child_thread_id': 'child', '_selection_sha256': 'pin'}
        self.assertEqual(mod.owner.selected_child(selected, 'root', None), 'child')
        self.assertEqual(mod.owner.selected_child(selected, 'child', None), 'child')
        with self.assertRaises(ValueError):
            mod.owner.selected_child(selected, 'other', None)
        old = {'schema': 'implementaudit.codex-current-public-source-observation.v1', 'root_thread_id': 'root', 'child_thread_id': 'foreign', 'selection_sha256': 'pin'}
        with self.assertRaises(ValueError):
            mod.owner.selected_child(selected, 'root', old)

    @unittest.skipUnless(os.name == 'nt', 'Windows handle/launch control; no native credit on other platforms')
    def test_changed_binary_refuses_before_launch(self):
        mod = self.api()
        with tempfile.TemporaryDirectory(dir=HERE, prefix='binary-control-') as directory:
            binary = Path(directory) / 'not-executable.bin'
            binary.write_bytes(b'not an executable')
            selected = {'native_executable': {'path': str(binary), 'sha256': '0' * 64}, 'cwd': directory, 'root_thread_id': 'root'}
            with mock.patch.object(mod.reader.subprocess, 'Popen', side_effect=AssertionError('native launch forbidden in source control')), self.assertRaisesRegex(ValueError, 'SELECTED_EXECUTABLE_CHANGED'):
                mod.reader.probe(selected, child_id='11111111-1111-1111-1111-111111111111')
if __name__ == '__main__':
    unittest.main(verbosity=2)
