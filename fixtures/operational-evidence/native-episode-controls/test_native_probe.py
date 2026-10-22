from native_test_support import source_path, source_text, functions as selected_functions, load, source_api, SCRATCH, PUBLIC_OWNERS
from unittest import mock
import os
'Discriminating safety tests for the staged metadata-only probe.'
import importlib.util
from pathlib import Path
import unittest
HERE = SCRATCH
SOURCE = source_path('bounded_native_reader.py')

class ProbeContract(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.module = load('bounded_native_reader.py')

    def api(self):
        self.assertIsNotNone(self.module, 'bounded metadata-only probe is not implemented')
        return self.module

    def test_allows_exact_metadata_read(self):
        self.api().validate_read('thread/read', {'threadId': 'a', 'includeTurns': False})

    def test_refuses_hydration_and_mutation(self):
        mod = self.api()
        for method, params in [('thread/read', {'threadId': 'a', 'includeTurns': True}), ('thread/read', {'threadId': 'a'}), ('turn/start', {'threadId': 'a'}), ('thread/read', {'threadId': 'a', 'includeTurns': False, 'other': 1})]:
            with self.subTest(method=method, params=params), self.assertRaises(ValueError):
                mod.validate_read(method, params)

    def test_metadata_projection_excludes_user_content_and_extra(self):
        row = {'id': 'a', 'path': 'p', 'sessionId': 's', 'parentThreadId': 'r', 'turns': [], 'preview': 'private user content', 'extra': {'opaque': 'private'}, 'source': {'subAgent': {'thread_spawn': {'parent_thread_id': 'r', 'prompt': 'private'}}}}
        projected = self.api().project_thread(row)
        self.assertEqual(projected['parentThreadId'], 'r')
        self.assertNotIn('private', str(projected))
        self.assertNotIn('preview', projected)

    def test_refuses_unexpected_hydrated_response(self):
        with self.assertRaises(ValueError):
            self.api().project_thread({'id': 'a', 'turns': [{'items': []}]})

    def test_bounded_exact_items_and_no_unbounded_list(self):
        mod = self.api()
        mod.validate_read('thread/items/read', {'threadId': 'a', 'turnId': 't', 'itemIds': ['m']})
        for items in ([], ['m'] * 2, [str(n) for n in range(101)]):
            with self.subTest(items=len(items)), self.assertRaises(ValueError):
                mod.validate_read('thread/items/read', {'threadId': 'a', 'turnId': 't', 'itemIds': items})
        with self.assertRaises(ValueError):
            mod.validate_read('thread/items/list', {'threadId': 'a'})

    def test_public_item_projection_refuses_private_and_foreign(self):
        mod = self.api()
        self.assertTrue(hasattr(mod, 'project_items'), 'exact public-item projection is not implemented')
        params = {'threadId': 'a', 'turnId': 't', 'itemIds': ['m']}
        item = {'id': 'm', 'type': 'agentMessage', 'text': 'hello', 'phase': 'commentary'}
        result = mod.project_items({'data': [{'turnId': 't', 'item': item}]}, params)
        self.assertEqual(result[0]['body_sha256'], '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824')
        self.assertNotIn('hello', str(result))
        for patch in ({'type': 'reasoning'}, {'phase': 'analysis'}, {'id': 'foreign'}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                mod.project_items({'data': [{'turnId': 't', 'item': item | patch}]}, params)
if __name__ == '__main__':
    unittest.main(verbosity=2)
