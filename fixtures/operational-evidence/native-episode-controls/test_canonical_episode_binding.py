from native_test_support import source_path, source_text, functions as selected_functions, load, source_api, SCRATCH, PUBLIC_OWNERS
from unittest import mock
import os
'Canonical lineage/child selection unit controls; no live episode credit.'
import ast
import base64
import contextlib
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import types
import unittest
HERE = SCRATCH

def fail(reason, **kwargs):
    raise ValueError(reason)

def digest(value):
    return 'sha256:' + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def require(value, reason):
    if not value:
        raise ValueError(reason)

def route_fixture(state='SATISFIED'):
    needed = {'validate_lifecycle_predecessor_chain', 'open_logical_task', 'logical_task_name', 'validate_bytes_identity', 'bytes_identity', 'read_current_episode_binding_v1'}
    tree = ast.parse(source_text('route-transaction.py'))
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in needed]
    env = {'__name__': 'fixture', 'Any': object, 'Path': Path, 'fail': fail, 'json': json, 'base64': base64, 'hashlib': hashlib, 're': re, 'OID_RE': re.compile('[0-9a-f]{40}'), 'HEX_RE': re.compile('sha256:[0-9a-f]{64}'), 'digest_json': digest, 'exact_keys': lambda value, keys, label: value if isinstance(value, dict) and set(value) == keys else fail(label), 'exact_text': lambda value, label: value if isinstance(value, str) and value else fail(label)}
    exec(compile(ast.Module(body=selected, type_ignores=[]), '<existing-route-validators>', 'exec'), env)
    common = {'host_id': 'host', 'host_session_id': 'root', 'host_binding_generation': '0001', 'host_correlation_id': 'correlation', 'continuity_generation': '0001', 'continuity_receipt': 'receipt', 'obligation_id': 'obligation', 'route_transaction_id': 'transaction', 'controller_id': 'controller', 'claim_id': 'claim', 'explicit_run_root': 'run'}
    delivery = {'packet': env['bytes_identity'](b'packet'), 'child': {'identity': 'audit-state', **env['bytes_identity'](b'skill')}}
    lifecycle = {'state': 'OPEN', 'required_record_oid': 'a' * 40, 'delivery': delivery, 'logical_task': 'bounded-task', 'child_return': None, 'governor_decision': None, 'governor_decision_count': 0, 'source_event_status': 'active'}

    def record(status, predecessor, life):
        value = {**common, 'route_state': status, 'predecessor_record_oid': predecessor, 'lifecycle': life}
        return value | {'record_identity': digest(value)}
    opened = record('OPEN', 'a' * 40, lifecycle)
    returned = record('RETURNED', 'b' * 40, lifecycle | {'state': 'RETURNED', 'child_return': {'return': 'exact'}})
    satisfied = record('SATISFIED', 'c' * 40, returned['lifecycle'] | {'state': 'SATISFIED', 'governor_decision': {'accept': 'exact'}, 'governor_decision_count': 1, 'source_event_status': 'satisfied'})
    objects = {'b' * 40: opened, 'c' * 40: returned, 'd' * 40: satisfied}
    current = {'OPEN': ('b' * 40, opened), 'RETURNED': ('c' * 40, returned), 'SATISFIED': ('d' * 40, satisfied)}[state]

    def validate_bytes(repo, oid, value, **kwargs):
        require(value['record_identity'] == digest({k: v for k, v in value.items() if k != 'record_identity'}), 'record bytes changed')
    env.update(RouteObjectReader=lambda repo: contextlib.nullcontext(None), git_blob_bytes=lambda repo, oid, label, **kwargs: json.dumps(objects[oid]).encode(), decoded_artifact=lambda raw, label: json.loads(raw), validate_canonical_route_record_bytes=validate_bytes, mapped_child_route=lambda record: ('audit-state', 'audit-state-target'), current_ref=lambda repo, controller: copy.deepcopy(current), validate_pure_current_route=lambda *args: {'record_oid': current[0], 'record_identity': current[1]['record_identity'], 'controller_record_oid': 'e' * 40}, _pure_route_final_ref_fence=lambda *args: None)
    return (env, objects, current)

class CanonicalRouteControls(unittest.TestCase):

    def test_terminal_binding_preserves_exact_open_identity(self):
        open_env, _, _ = route_fixture('OPEN')
        terminal_env, _, _ = route_fixture('SATISFIED')
        first = open_env['read_current_episode_binding_v1'](Path('.'), 'controller')
        last = terminal_env['read_current_episode_binding_v1'](Path('.'), 'controller')
        self.assertEqual(last['logical_task'], 'bounded-task')
        self.assertEqual(last['selected_child_role'], 'audit-state')
        self.assertEqual(first['opening_digest'], last['opening_digest'])
        self.assertNotEqual(first['binding_digest'], last['binding_digest'])
        self.assertNotIn('actual_child_id', last)

    def test_changed_lineage_or_final_ref_fence_refuses(self):
        env, objects, _ = route_fixture()
        objects['b' * 40]['lifecycle']['logical_task'] = 'foreign'
        with self.assertRaises(ValueError):
            env['read_current_episode_binding_v1'](Path('.'), 'controller')
        env, _, _ = route_fixture()
        env['_pure_route_final_ref_fence'] = lambda *args: fail('fence changed')
        with self.assertRaisesRegex(ValueError, 'fence changed'):
            env['read_current_episode_binding_v1'](Path('.'), 'controller')

class CanonicalNativeSelectionControls(unittest.TestCase):

    def fixture(self, paths):
        root = '11111111-1111-1111-1111-111111111111'
        ids = ['22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333']
        selected = {'root_thread_id': root, 'root_agent_path': '/root', 'root_source': 'parent', 'session_root': 'sessions', 'cli_version': 'v', 'cwd': 'cwd'}
        env = {'require': require, 'Path': Path, 're': re, 'os': __import__('os'), 'hashlib': hashlib, 'HERE': HERE, 'READER': HERE / 'unused'}
        selected_functions('compaction-source-owner-codex-app.py', {'_np_subject'}, env)
        episode = {'logical_task': 'required-task', 'opening_digest': 'selected-open'}

        def header(thread):
            name = thread['path']
            index = ids.index(thread['id']) if thread['id'] in ids else -1
            return {'physical': {'path': name, 'device': 1, 'inode': index + 2}, 'header_prefix': {'sha256': 'header'}, 'cutoff_bytes': 100, 'metadata': {'id': thread['id'], 'parent_thread_id': root, 'agent_path': '/root' if index < 0 else paths[index]}}
        threads = [{'id': ident, 'path': str(Path('sessions') / ('rollout-' + ident + '.jsonl'))} for index, ident in enumerate(ids[:len(paths)])]
        calls = []

        def native(runtime, methods, child_id=None):
            calls.append((methods, child_id))
            if methods[0][0] == 'thread/list':
                return {'responses': [{'threads': threads}]}
            return {'responses': [{'thread': {'id': root, 'path': 'parent'}}, {'thread': next((t for t in threads if t['id'] == child_id))}]}
        helpers = types.SimpleNamespace(header=header, validate_relation=lambda *args: None, canonical_path=lambda p: Path(p))
        runtime = (selected, None, None, helpers, None)
        env['_np_episode'] = lambda runtime: copy.deepcopy(episode)
        env['_np_call'] = native
        return (env, runtime, calls, ids)

    def test_unique_canonical_path_selects_child_not_list_order(self):
        env, runtime, calls, ids = self.fixture(['/root/unrelated', '/root/required-task'])
        result = env['_np_subject'](runtime)
        self.assertEqual(result['actual_child_identity']['thread_id'], ids[1])
        self.assertEqual(calls[-1][1], ids[1])

    def test_duplicate_or_absent_canonical_task_refuses(self):
        for paths in (['/root/required-task', '/root/required-task'], ['/root/unrelated']):
            env, runtime, _, _ = self.fixture(paths)
            with self.subTest(paths=paths), self.assertRaisesRegex(ValueError, 'CANONICAL_CHILD_NOT_UNIQUE'):
                env['_np_subject'](runtime)
if __name__ == '__main__':
    unittest.main(verbosity=2)
