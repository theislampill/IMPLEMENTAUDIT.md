from native_test_support import source_path, source_text, functions as selected_functions, load, source_api, SCRATCH, PUBLIC_OWNERS, guard_ast_digest, canonical_unbound_fixture, bounded_bytes
from unittest import mock
import os
import subprocess
import tempfile
'Narrow owner seam controls. Fixtures below confer no native/profile credit.'
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import types
import unittest
HERE = SCRATCH

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def functions(names):
    text = source_text('compaction-result-observation.py')
    tree = ast.parse(text)
    body = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names | {'unique'}]
    env = {'require': require, 'json': json, 're': re, 'Path': Path, 'MAX_TOTAL': 2 * 1024 * 1024, 'canonical': lambda value: json.dumps(value, sort_keys=True, separators=(',', ':')).encode(), 'HoldObservationRefusal': ValueError, 'CURRENT_BOUNDARY_PROFILE': 'old-current', 'NONPROTECTED_PROFILE': 'codex-app-bounded-public-nonprotected-v1'}
    exec(compile(ast.Module(body=body, type_ignores=[]), '<actual-public-owner-functions>', 'exec'), env)
    return env

class ExistingObservationControls(unittest.TestCase):

    def public(self, extensions=False):
        content = {'type': 'output_text', 'text': 'actual public body'}
        if extensions:
            content.update(annotations=[], logprobs=[])
        return {'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant', 'phase': 'commentary', 'id': 'm', 'content': [content]}, 'metadata': {'client_authored': False, 'retained_source': {'complete': True, 'id': {'message_id': 'm', 'role': 'assistant', 'turn_id': '11111111-1111-1111-1111-111111111111'}, 'revision': 'retained_22222222-2222-2222-2222-222222222222'}}}

    def test_current_grammar_is_additive_old_grammar_remains_exact(self):
        env = functions({'public_message', 'current_retained_locator', 'closed'})
        current = {'profile_id': env['NONPROTECTED_PROFILE']}
        old = {'profile_id': 'old-current'}
        self.assertEqual(env['public_message'](self.public(True), context=current), 'actual public body')
        self.assertEqual(env['public_message'](self.public(False), context=old), 'actual public body')
        with self.assertRaises(ValueError):
            env['public_message'](self.public(True), context=old)
        with self.assertRaises(ValueError):
            env['public_message'](self.public(False), context=current)
        altered = self.public(True)
        altered['payload']['content'][0]['annotations'] = [{'unqualified': True}]
        with self.assertRaises(ValueError):
            env['public_message'](altered, context=current)

    def test_return_and_acceptance_checks_are_preserved(self):
        golden = json.loads(Path(__file__).with_name('guard-golden.json').read_text())['return_acceptance_ast_sha256']
        tree = ast.parse(source_text('compaction-result-observation.py'))
        for name in ('actual_result', 'acceptance'):
            node = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name))
            if name == 'actual_result':
                phase = [n for n in node.body if isinstance(n, ast.Assign) and
                    any(isinstance(t, ast.Name) and t.id == 'final_phase' for t in n.targets)]
                self.assertEqual(len(phase), 1)
                self.assertEqual(ast.dump(phase[0].value), ast.dump(ast.parse(
                    "'final' if context['profile_id'] == NONPROTECTED_PROFILE else 'final_answer'", mode='eval').body))
                node.body.remove(phase[0])
                class LegacyFinalPhase(ast.NodeTransformer):
                    def visit_Name(self, value):
                        return ast.Constant(value='final_answer') if value.id == 'final_phase' else value
                node = LegacyFinalPhase().visit(node)
                node.body = [n for n in node.body if not (isinstance(n, ast.Assign) and any((isinstance(t, ast.Name) and t.id == 'selected_occurrences' for t in n.targets))) and (not (isinstance(n, ast.If) and ast.unparse(n.test) == "context['profile_id'] == NONPROTECTED_PROFILE"))]
                for item in ast.walk(node):
                    if isinstance(item, ast.Call) and isinstance(item.func, ast.Name) and (item.func.id == 'hold_history'):
                        item.keywords = [k for k in item.keywords if k.arg != 'occurrence_sink']
            self.assertEqual(guard_ast_digest(node), golden[name], name)

    def retry_fixture(self):
        env = functions({'classify_prior_retry'})
        loc = lambda off: {'offset': off, 'bytes': 5, 'sha256': str(off).zfill(64), 'embedded_ordinal': off, 'physical_line': off}
        pin = lambda off: {'path': 'child.jsonl', 'physical': {'device': 1, 'inode': 2}, 'role': 'child', 'locator': loc(off)}
        call = {'locator': loc(30), 'row': {'payload': {'type': 'custom_tool_call', 'call_id': 'c', 'input': 'owned input'}}}
        response = {'locator': loc(40), 'row': {'payload': {'type': 'custom_tool_call_output', 'call_id': 'c'}}}
        prior = {'bind_request': {'observation_id': 'prior'}, 'bound_response': {'bound': 'prior'}, 'obligation': {'observation_id': 'prior'}}
        pair = {'call': pin(30), 'result': pin(40)}
        env.update(profile_tool_input=lambda context, command: command, delivery_tool_input=lambda *args: 'owned input', command_response=lambda *args: (json.dumps(prior['bound_response']), copy.deepcopy(pair)), before=lambda left, right: require(left['locator']['offset'] < right['locator']['offset'], 'ORDER'))
        context = {'child': {'path': 'child.jsonl', 'physical': {'device': 1, 'inode': 2}}}
        proofs = [{'prior': prior, 'original': {'call': pin(10), 'result': pin(20)}}]
        return (env, context, call, [call, response], proofs, pair)

    def test_retry_export_occurs_only_after_existing_physical_and_response_guards(self):
        env, context, call, records, proofs, pair = self.retry_fixture()
        sink = []
        admitted = set()
        self.assertTrue(env['classify_prior_retry'](context, call, records, {}, 50, proofs, admitted, 's', 'session', 'owner', occurrence_sink=sink))
        self.assertEqual(sink, [{'population': 'PRIOR', 'attempt_class': 'RETRY', 'semantic': 'BIND', 'observation_id': 'prior', 'completion': 'COMPLETED', 'records': pair}])
        self.assertEqual(admitted, {30, 40})
        for failure in ('response', 'copied_offset'):
            env, context, call, records, proofs, pair = self.retry_fixture()
            sink = []
            if failure == 'response':
                env['command_response'] = lambda *args: ('{}', pair)
            else:
                changed = copy.deepcopy(pair)
                changed['call']['locator']['offset'] = 31
                env['command_response'] = lambda *args: (json.dumps({'bound': 'prior'}), changed)
            with self.subTest(failure=failure), self.assertRaises(ValueError):
                env['classify_prior_retry'](context, call, records, {}, 50, proofs, set(), 's', 'session', 'owner', occurrence_sink=sink)
            self.assertEqual(sink, [])

    def test_missing_original_completion_still_refuses_prior_classification(self):
        env = functions({'prior_record_occurrences'})
        prior = {'observation': {'revision': 1}, 'obligation': {'id': 'p'}, 'obligation_pin': {}, 'authorization': {'evidence': {}}, 'exchange': {'evidence': {}}, 'bind_request': {}}
        env.update(artifact=lambda pin: (json.dumps(prior['obligation']).encode(), None), unique=lambda pairs: dict(pairs), authorization=lambda *args: prior['authorization'], completed_exchange=lambda *args: prior['exchange'], original_bind_records=lambda *args: ([], {}, None))
        with self.assertRaisesRegex(ValueError, 'HOLD_PRIOR_ORIGINAL_COMPLETION_UNPROVED'):
            env['prior_record_occurrences']({}, {'authorization': {'value': {'skill_source_pin': {}}}}, {'locator': {'offset': 100}}, [], {}, 'store', 'session', 'owner', {'p': prior}, {})

class FixedSelectionControls(unittest.TestCase):

    def test_unbound_source_owner_cannot_accept_caller_policy(self):
        owner = load('compaction-source-owner-codex-app.py')
        with self.assertRaisesRegex(ValueError, 'NONPROTECTED_FIXED_SELECTION_UNBOUND'):
            owner._np_selection()
        with tempfile.TemporaryDirectory(dir=HERE, prefix='canonical-unbound-') as directory:
            pending, scripts = canonical_unbound_fixture(directory)
            forbidden = AssertionError('subprocess/native acquisition forbidden for unbound fixture')
            with mock.patch.object(subprocess, 'Popen', side_effect=forbidden), mock.patch.object(subprocess, 'run', side_effect=forbidden):
                with self.assertRaises(OSError):
                    pending.read_selected_accepted_episode_v1()
                (scripts / 'route-transaction.py').write_bytes(bounded_bytes(source_path('route-transaction.py')))
                exported = pending.read_selected_accepted_episode_v1()
            self.assertEqual(exported['status'], 'UNAVAILABLE')
            self.assertEqual(exported['reason_code'], 'FIXED_SELECTION_UNBOUND')
            self.assertIsNone(exported['episode'])
if __name__ == '__main__':
    unittest.main(verbosity=2)
