#!/usr/bin/env python3
"""Owned-stdio source grammar and HOLD regression controls.

All source records, native RPC responses and H0/provider edges are constructed.
Physical file reading, original HOLD/bind and pending file operations are real.
No private retained transcript, selected native session, runtime store, model,
Q, grant, accepting JOIN or native qualification is used.
"""
import argparse
import contextlib
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
HERE = SUPPORT = H = O = OBS = P = None
PARENT = '11111111-2222-4333-8444-555555555555'
CHILD = '66666666-7777-4888-8999-aaaaaaaaaaaa'
TASK = 'constructed_owned_stdio_boundary'

def turn_id(index):
    return '00000000-0000-4000-8000-%012x'%index


def rows(turns=1, frames=10, *, role='parent'):
    values = []
    for index in range(1, turns+1):
        identity = turn_id(index)
        portion = [('event_msg', {'type': 'task_started', 'turn_id': identity}),
                   ('turn_context', {'turn_id': identity, 'root_turn_id': identity if role == 'parent' else turn_id(99)})]
        terminal = index < turns
        portion += [('token_usage_record', {'turn_id': identity}) for _ in range(frames-3-int(terminal))]
        portion += [('response_item', {'type': 'message', 'id': 'public-'+str(index), 'role': 'assistant',
                    'phase': 'commentary', 'content': [{'type': 'output_text', 'text': 'public '+str(index)}]})]
        if terminal:
            portion += [('event_msg', {'type': 'task_complete', 'turn_id': identity})]
        values += portion
    return [{'timestamp': '2026-10-23T00:00:00.%06dZ'%index, 'ordinal': index+1, 'type': kind, 'payload': payload}
            for index, (kind, payload) in enumerate(values)]


def wire(row):
    return json.dumps(row, sort_keys=True, separators=(',', ':')).encode()+b'\n'


def fixture(directory, values, role='parent'):
    path = directory/'source.jsonl'
    raw, locators = b'', []
    for index, row in enumerate(values):
        chunk = wire(row)
        locators.append({'offset': len(raw), 'bytes': len(chunk), 'sha256': hashlib.sha256(chunk).hexdigest(),
                         'embedded_ordinal': row['ordinal'], 'physical_line': index+1})
        raw += chunk
    path.write_bytes(raw)
    info = path.stat()
    context = {'profile_id': 'codex-app-server-0.153.4-owned-stdio-candidate-v1',
               role: {'path': str(path), 'physical': {'device': info.st_dev, 'inode': info.st_ino}},
               'parent_turn_start' if role == 'parent' else 'child_activation': {'locator': locators[0]}}
    return path, context, {'locator': locators[-1]}


def read(context, role, pin):
    entry = getattr(H, 'owned_stdio_public_turn_v2', None)
    return entry(OBS, context, role, pin) if entry else O._as_public_turn_v1(OBS, context, role, pin)


def block(value):
    return '```json\n'+json.dumps(value, sort_keys=True, separators=(',', ':'))+'\n```'


class Sources:
    def __init__(self, root):
        self.root = root
        self.paths = {role: root/('rollout-'+identity+'.jsonl') for role, identity in (('parent', PARENT), ('child', CHILD))}
        self.ordinals = {'parent': 0, 'child': 0}
        self.clock = 0

    def append(self, role, kind, payload):
        path = self.paths[role]
        self.clock += 1
        row = {'timestamp': '2026-10-23T00:00:00.%06dZ'%self.clock, 'ordinal': self.ordinals[role], 'type': kind, 'payload': payload}
        self.ordinals[role] += 1
        raw = OBS.canonical(row)+b'\n'
        offset = path.stat().st_size if path.exists() else 0
        with path.open('ab') as stream:
            stream.write(raw)
        return {'path': str(path), 'physical': OBS.identity(path.stat()), 'role': role,
            'locator': {'offset': offset, 'bytes': len(raw), 'sha256': OBS.digest(raw),
                        'embedded_ordinal': row['ordinal'], 'physical_line': row['ordinal']+1},
            'timestamp': row['timestamp'], 'message_or_call_id': payload.get('id', payload.get('call_id'))}

    def message(self, role, text, phase='commentary'):
        return self.append(role, 'response_item', {'type': 'message', 'id': 'fixture-message-'+str(self.clock+1),
            'role': 'assistant', 'phase': phase, 'content': [{'type': 'output_text', 'text': text}]})

    def call(self, text, identity):
        return self.append('child', 'response_item', {'type': 'custom_tool_call', 'name': 'exec', 'input': text,
                                                     'call_id': identity, 'status': 'completed'})

    def output(self, identity, value):
        nested = {'chunk_id': 'CONSTRUCTED', 'wall_time_seconds': .01, 'exit_code': 0,
                  'original_token_count': 1, 'output': json.dumps(value)}
        return self.append('child', 'response_item', {'type': 'custom_tool_call_output', 'call_id': identity,
            'output': [{'type': 'input_text', 'text': 'CONSTRUCTED TOOL RESPONSE'},
                       {'type': 'input_text', 'text': json.dumps(nested)}]})


@contextlib.contextmanager
def constructed(original_bind_output=True, tied_prelude=False, *, prelude_order=None,
                profile_id=None, child_version='0.153.4'):
    global P, OBS
    with tempfile.TemporaryDirectory(dir=HERE) as directory:
        root = Path(directory)
        P, scripts = SUPPORT.canonical_unbound_fixture(root/'public-code')
        (scripts/'route-transaction.py').write_bytes(SUPPORT.bounded_bytes(SUPPORT.ROUTE))
        OBS = P.OBSERVATION
        store = root/'constructed-store'
        source = Sources(root)
        pm = source.append('parent', 'session_meta', {'id': PARENT, 'session_id': PARENT, 'cli_version': '0.153.4'})
        for label in ('C', 'D'):
            source.append('parent', 'compacted', {'constructed_boundary': label})
            source.append('parent', 'event_msg', {'type': 'task_started', 'turn_id': 'constructed-resume-'+label})
        pt = source.append('parent', 'event_msg', {'type': 'task_started', 'turn_id': 'constructed-parent-dispatch'})
        opened = source.message('parent', '```ini\nCHILD_TASK='+TASK+'\nCHILD_SKILL_SELECTED=audit-state\nSTATUS=OPEN\nLOAD=UNVERIFIED\n```')
        spawn = source.append('parent', 'response_item', {'type': 'function_call', 'namespace': 'collaboration', 'name': 'spawn_agent',
            'call_id': 'constructed-spawn', 'arguments': json.dumps({'task_name': TASK, 'fork_turns': 'none'})})
        spawned = source.append('parent', 'response_item', {'type': 'function_call_output', 'call_id': 'constructed-spawn',
                                                         'output': json.dumps({'task_name': '/root/'+TASK})})
        cm = source.append('child', 'session_meta', {'id': CHILD, 'session_id': PARENT, 'parent_thread_id': PARENT,
            'agent_path': '/root/'+TASK, 'cli_version': child_version})
        activation = source.append('child', 'event_msg', {'type': 'task_started', 'turn_id': 'constructed-original-child-turn'})
        if tied_prelude or prelude_order is not None:
            source.append('child', 'response_item', {'type': 'message', 'role': 'developer',
                'content': [{'type': 'input_text', 'text': 'CONSTRUCTED initial context A'}]})
            source.clock -= 2 if prelude_order == 'reversed' else 1
            if prelude_order == 'duplicate':
                source.ordinals['child'] -= 1
            source.append('child', 'response_item', {'type': 'message', 'role': 'developer',
                'content': [{'type': 'input_text', 'text': 'CONSTRUCTED initial context B'}]})
        source.append('child', 'turn_context', {'turn_id': 'constructed-original-child-turn'})
        code = P.nonprotected_code_identity()
        context = {'profile_id': profile_id or OBS.OWNED_STDIO_PROFILE, 'source_association': 'PUBLIC_BOUNDARY_CHILD_STRUCTURAL_UNQUALIFIED',
            'parent_identity': {'thread_id': PARENT, 'agent_path': '/root'},
            'actual_child_identity': {'thread_id': CHILD, 'parent_thread_id': PARENT, 'agent_path': '/root/'+TASK},
            '_source_profile_code_pins': code, 'open': opened, 'spawn_call': spawn, 'spawn_output': spawned,
            'parent_turn_start': pt, 'child_activation': activation}
        for role, metadata in (('parent', pm), ('child', cm)):
            raw = source.paths[role].read_bytes()[:metadata['locator']['bytes']]
            payload = json.loads(raw)['payload']
            context[role] = {'path': str(source.paths[role]), 'physical': metadata['physical'], 'metadata': metadata['locator'],
                'metadata_payload_digest': OBS.digest(OBS.canonical(payload)), 'allowed_ranges': [{'offset': 0, 'bytes': OBS.MAX_TOTAL}],
                'history_start_ordinal': 1 if role == 'child' else 0}
        def local_records(ctx, role, selectors):
            value = ctx[role]
            return OBS.read_records(value['path'], selectors, value['allowed_ranges'], value['physical'])
        guard_owner = types.SimpleNamespace(nonprotected_sources_guard=lambda *a: contextlib.nullcontext())
        with patch.object(OBS, '_nonprotected_read_records', local_records), \
             patch.object(OBS, '_nonprotected_source_owner', lambda *a: guard_owner), \
             patch.object(P, 'attribution', lambda *a: {'CONSTRUCTED_H0_NOT_NATIVE': True}), \
             patch.object(P, 'scan_source', P._scan_source_unheld):
            context['fresh_child_boundary'] = OBS.fresh_child_boundary(context)
            scan = P.scan_source(source.paths['parent'])
            state = P.blank(PARENT)
            state['source'] = {'path': str(source.paths['parent']), 'task_id': PARENT, 'session_id': PARENT,
                'sessions_root': str(root), 'physical': scan['physical'], 'session_meta_sha256': scan['metadata_sha256'],
                'prefix_bytes': scan['bytes'], 'prefix_sha256': scan['sha256'], 'provenance': 'CONSTRUCTED_SOURCE_NOT_NATIVE',
                'native_producer_runtime_equivalence': 'UNVERIFIED'}
            P.refresh(state)
            scope = next(row for row in P.outstanding(state) if state['observations'][row['id']]['proof']['resume_turn'] == 'constructed-resume-C')
            uncovered = next(row for row in P.outstanding(state) if state['observations'][row['id']]['proof']['resume_turn'] == 'constructed-resume-D')
            nominations = {key: value['locator'] for key, value in (('open', opened), ('spawn_call', spawn), ('spawn_output', spawned),
                                                                   ('child_activation', activation), ('parent_turn_start', pt))}
            assignment = {'child_id': CHILD, 'scope': [scope], 'code': code, 'observations': {}, 'return': None, 'join': None,
                'native_lifecycle': 'NOT_CLAIMED', 'reservation_request': {'child_id': CHILD, 'bounded_purpose': 'CONSTRUCTED C only',
                    'observation_source': nominations, 'scope': [scope]}, 'policy': {'CONSTRUCTED_NOT_ADMITTED': True},
                'observation_source': context, 'bounded_purpose': 'CONSTRUCTED C only'}
            state['assignments'][CHILD] = assignment
            original = P.prepare_obligation(store, state, assignment)
            observation = original['obligation']['observation_id']
            P.save(store, state)
            skill = P.selected_audit_state_pin()
            load_input = OBS.profile_tool_input(context, OBS.load_tool_input(skill))
            load_call = source.call(load_input, 'constructed-load')
            load_output = source.output('constructed-load', {**skill, 'utf8': Path(skill['path']).read_text(encoding='utf-8')})
            _, loaded = OBS.command_response(context, 'child', load_call['locator'], load_output['locator'], load_input)
            route = source.message('parent', '```ini\nCHILD_TASK='+TASK+'\nCHILD_SKILL_ROUTE=audit-state\nLOAD=VERIFIED\n```')
            auth_value = {'schema': 'implementaudit.compaction-use-authorization.v1', 'action': 'AUTHORIZE_BOUNDED_POST_COMPACTION_RECONCILIATION',
                'parent_identity': original['obligation']['parent_identity'], 'actual_child_identity': original['obligation']['actual_child_identity'],
                'obligation_digest': original['obligation_pin']['sha256'], 'observation_id': observation,
                'load_observation_identity': OBS.digest(OBS.canonical(loaded)), 'selected_child': 'audit-state',
                'skill_source_pin': skill, 'authority_ceiling': 'NONE'}
            auth = source.message('parent', block(auth_value))
            delivery = {'child_id': CHILD, 'phase': 'deliver', 'observation_id': observation,
                'authorization_evidence': {'load_call': load_call['locator'], 'load_output': load_output['locator'],
                                           'route': route['locator'], 'authorization': auth['locator']}}
            delivery_input = OBS.profile_tool_input(context, OBS.delivery_tool_input(store, PARENT, 'CONSTRUCTED_OWNER', delivery))
            delivery_call = source.call(delivery_input, 'constructed-deliver')
            packet = P.operate(store, PARENT, 'CONSTRUCTED_OWNER', 'observe-child', delivery)
            delivery_output = source.output('constructed-deliver', packet)
            exchange_pair = {'call': delivery_call['locator'], 'result': delivery_output['locator']}
            prepared = P.load(store, PARENT)['assignments'][CHILD]['prepared'][observation]
            exchange = OBS.completed_exchange(context, prepared, exchange_pair, store, PARENT, 'CONSTRUCTED_OWNER', skill)
            bind = {'child_id': CHILD, 'phase': 'bind', 'observation_id': observation, 'exchange': exchange_pair}
            bind_input = OBS.profile_tool_input(context, OBS.delivery_tool_input(store, PARENT, 'CONSTRUCTED_OWNER', bind))
            bind_call = source.call(bind_input, 'constructed-bind')
            bound = P.operate(store, PARENT, 'CONSTRUCTED_OWNER', 'observe-child', bind)
            if original_bind_output:
                bind_output = source.output('constructed-bind', bound)
            else:
                source.call(bind_input, 'constructed-retry')
                bind_output = source.output('constructed-retry', bound)
            yield types.SimpleNamespace(store=store, source=source, observation=observation,
                scope=scope, uncovered=uncovered, context=context, exchange=exchange, bind=bind)


class PublicTurnControls(unittest.TestCase):
    def run_rows(self, values, role='parent'):
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            _, context, selected = fixture(Path(directory), values, role)
            return read(context, role, selected)

    def test_single_turn64_remains_pass65_remains_refusal(self):
        self.assertEqual(self.run_rows(rows(frames=64)), turn_id(1))
        with self.assertRaises(ValueError):
            self.run_rows(rows(frames=65))

    def test_seven_complete_turn_prefixes_use_every_frame(self):
        self.assertEqual(self.run_rows(rows(turns=7, frames=20)), turn_id(7))

    def test_eighth_parent_turn_and_second_child_turn_refuse(self):
        with self.assertRaises(ValueError):
            self.run_rows(rows(turns=8, frames=5))
        with self.assertRaises(ValueError):
            self.run_rows(rows(turns=2, frames=5, role='child'), 'child')

    def test_absent_initial_marker_refuses(self):
        values = rows()[1:]
        with self.assertRaises(ValueError):
            self.run_rows(values)

    def test_missing_or_duplicate_context_refuses(self):
        values = rows()
        values[1] = {**values[1], 'type': 'world_state', 'payload': {}}
        with self.assertRaises(ValueError):
            self.run_rows(values)
        values = rows()
        values[2] = {**values[2], 'type': 'turn_context', 'payload': dict(values[1]['payload'])}
        with self.assertRaises(ValueError):
            self.run_rows(values)

    def test_foreign_context_or_terminal_refuses(self):
        values = rows()
        values[1]['payload']['turn_id'] = turn_id(9)
        with self.assertRaises(ValueError):
            self.run_rows(values)
        values = rows(turns=2)
        values[9]['payload']['turn_id'] = turn_id(9)
        with self.assertRaises(ValueError):
            self.run_rows(values)

    def test_duplicate_or_overlapping_start_refuses(self):
        values = rows(turns=2)
        for item in values[10:]:
            if item['payload'].get('turn_id') == turn_id(2):
                item['payload']['turn_id'] = turn_id(1)
            if item['type'] == 'turn_context':
                item['payload']['root_turn_id'] = turn_id(1)
        with self.assertRaises(ValueError):
            self.run_rows(values)
        values = rows(turns=2)
        values[9] = {**values[9], 'type': 'world_state', 'payload': {}}
        with self.assertRaises(ValueError):
            self.run_rows(values)

    def test_foreign_turn_label_on_nonmarker_refuses(self):
        values = rows()
        values[2]['payload']['turn_id'] = turn_id(4)
        with self.assertRaises(ValueError):
            self.run_rows(values)

    def test_unknown_or_between_turn_frame_refuses(self):
        values = rows()
        values[3]['type'] = 'unknown-future-turn-event'
        with self.assertRaises(ValueError):
            self.run_rows(values)
        values = rows(turns=2)
        values.insert(10, {'timestamp': '2026-10-23T00:00:00.000010Z', 'ordinal': 11,
                          'type': 'world_state', 'payload': {}})
        for index, item in enumerate(values):
            item['ordinal'] = index+1
        with self.assertRaises(ValueError):
            self.run_rows(values)

    def test_skipped_ordinal_partial_frame_or_changed_anchor_refuses(self):
        values = rows()
        values[3]['ordinal'] += 1
        with self.assertRaises(ValueError):
            self.run_rows(values)
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            path, context, selected = fixture(Path(directory), rows())
            context['parent_turn_start']['locator']['sha256'] = '0'*64
            with self.assertRaises(ValueError):
                read(context, 'parent', selected)

    def test_total_byte_bound_is_unchanged(self):
        values = rows(frames=12)
        for item in values[2:-1]:
            item['type'] = 'response_item'
            item['payload'] = {'type': 'message', 'role': 'user', 'content': [{'type': 'input_text', 'text': ''}]}
        remaining = OBS.MAX_TOTAL-sum(len(wire(item)) for item in values)
        for item in values[2:-1]:
            count = min(remaining, OBS.MAX_RECORD-len(wire(item)))
            item['payload']['content'][0]['text'] = 'x'*count
            remaining -= count
        self.assertEqual(remaining, 0)
        self.assertEqual(self.run_rows(values), turn_id(1))
        values[-2]['payload']['content'][0]['text'] += 'x'
        with self.assertRaises(ValueError):
            self.run_rows(values)

    def test_other_profile_is_not_broadened(self):
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            _, context, selected = fixture(Path(directory), rows())
            context['profile_id'] = 'codex-app-bounded-public-nonprotected-v1'
            with self.assertRaises(ValueError):
                read(context, 'parent', selected)

    def test_copied_physical_source_and_changed_prefix_refuse(self):
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            path, context, selected = fixture(Path(directory), rows())
            copied = Path(directory)/'copy.jsonl'
            copied.write_bytes(path.read_bytes())
            context['parent']['path'] = str(copied)
            with self.assertRaises(ValueError):
                read(context, 'parent', selected)
            context['parent']['path'] = str(path)
            original = OBS.physical
            calls = []
            def changed(value):
                calls.append(value)
                if len(calls) == 2:
                    path.write_bytes(path.read_bytes().replace(b'public 1', b'public X'))
                return original(value)
            with patch.object(OBS, 'physical', changed), self.assertRaises(ValueError):
                read(context, 'parent', selected)


    def test_original_native_public_confirmation_stays_mandatory(self):
        # Actual physical source/turn parser and actual public consumer; only
        # native provider acquisition and native RPC responses are constructed.
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            values = rows(turns=2, frames=35)
            values.insert(0, {'timestamp': '2026-10-22T23:59:59Z', 'ordinal': 0, 'type': 'session_meta', 'payload': {'id': 'constructed-root'}})
            path, _, selected = fixture(Path(directory), values)
            all_raw = path.read_bytes()
            first = wire(values[0])
            start = wire(values[1])
            metadata = {'offset': 0, 'bytes': len(first), 'sha256': hashlib.sha256(first).hexdigest(), 'embedded_ordinal': 0, 'physical_line': 1}
            anchor = {'offset': len(first), 'bytes': len(start), 'sha256': hashlib.sha256(start).hexdigest(), 'embedded_ordinal': 1, 'physical_line': 2}
            source = {'path': str(path), 'physical': OBS.identity(path.stat()), 'metadata': metadata,
                      'metadata_payload_digest': OBS.digest(OBS.canonical(values[0]['payload'])),
                      'allowed_ranges': [{'offset': 0, 'bytes': OBS.MAX_TOTAL}]}
            context = {'profile_id': O.OWNED_STDIO_PROFILE, 'parent': source, 'parent_turn_start': {'locator': anchor},
                       'parent_identity': {'thread_id': 'constructed-root'}, 'actual_child_identity': {'thread_id': 'constructed-child'},
                       'canonical_episode_binding': {'opening_digest': 'actual-opening-fixture'}, '_source_profile_code_pins': {}}
            def local_records(ctx, role, selectors):
                owner_source = ctx[role]
                return OBS.read_records(owner_source['path'], selectors, owner_source['allowed_ranges'], owner_source['physical'])
            with patch.object(OBS, '_nonprotected_read_records', local_records):
                row, target = OBS.resolve_record(context, 'parent', selected['locator'])
            body = OBS.public_message(row, context=context).encode()
            expected = {'id': row['payload']['id'], 'turn_id': turn_id(2), 'phase': 'commentary',
                        'body_bytes': len(body), 'body_sha256': OBS.digest(body)}
            custody = type('Custody', (), {'held_file': staticmethod(lambda path, **kwargs: Path(path).open('rb'))})()
            runtime = ({'profile_id': O.OWNED_STDIO_PROFILE}, custody, None, H, None)
            episode = {'opening_digest': 'actual-opening-fixture'}
            for altered in (False, True):
                response = dict(expected)
                if altered:
                    response['body_sha256'] = '0'*64
                def native(rt, methods, child):
                    self.assertEqual(methods[0][1]['turnId'], turn_id(2))
                    return {'responses': [{'page_complete': True, 'items': [response], 'response_sha256': 'e'*64}]}
                with patch.object(O, '_np_runtime', lambda *a: runtime), patch.object(O, '_np_provider_guard', lambda *a: contextlib.nullcontext()), \
                     patch.object(O, '_np_episode', lambda *a: episode), patch.object(O, '_np_call', native), \
                     patch.object(OBS, '_nonprotected_read_records', local_records):
                    if altered:
                        with self.assertRaisesRegex(ValueError, 'OWNED_STDIO_NATIVE_PUBLIC_DIFFERS'):
                            O._as_public_binding_v1(OBS, context, {}, [target], runtime)
                    else:
                        value = O._as_public_binding_v1(OBS, context, {}, [target], runtime)
                        self.assertEqual(value['records'][0]['body_sha256'], expected['body_sha256'])


    def test_partial_physical_frame_refuses(self):
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            path, context, selected = fixture(Path(directory), rows())
            path.write_bytes(path.read_bytes()[:-1])
            with self.assertRaises(ValueError):
                read(context, 'parent', selected)


class HoldOrderControls(unittest.TestCase):
    def completed_hold(self, value):
        prepared = P.load(value.store, PARENT)['assignments'][CHILD]['prepared'][value.observation]
        return OBS.hold_history(value.context, prepared, value.exchange, value.bind,
            value.store, PARENT, 'CONSTRUCTED_OWNER', prior_context={})

    def test_tied_owned_child_binds_original_completion_and_preserves_D(self):
        with constructed(tied_prelude=True) as value:
            held = self.completed_hold(value)
            self.assertEqual(held['original_bind']['call']['message_or_call_id'], 'constructed-bind')
            state = P.load(value.store, PARENT)
            self.assertEqual(state['observations'][value.uncovered['id']]['consumed_version'], 0)
            self.assertIsNone(state['assignments'][CHILD]['return'])
            self.assertIsNone(state['assignments'][CHILD]['join'])

    def test_reversed_timestamps_refuse(self):
        with self.assertRaisesRegex(ValueError, 'HOLD_EVENT_ORDER'):
            with constructed(prelude_order='reversed'):
                self.fail('reversed timestamp accepted')

    def test_duplicate_ordinal_refuses(self):
        with self.assertRaisesRegex(ValueError, 'HOLD_EVENT_GAP_OR_DUPLICATE'):
            with constructed(prelude_order='duplicate'):
                self.fail('duplicate ordinal accepted')

    def test_foreign_profile_and_version_remain_strict(self):
        with self.assertRaisesRegex(ValueError, 'CURRENT_PUBLIC_METADATA_SHAPE'):
            with constructed(tied_prelude=True, profile_id=SUPPORT.load('compaction-result-observation.py').NONPROTECTED_PROFILE):
                self.fail('foreign profile accepted')
        with self.assertRaisesRegex(ValueError, 'HOLD_EVENT_ORDER'):
            with constructed(tied_prelude=True, child_version='0.155.0-alpha.16'):
                self.fail('foreign version inherited tied timestamp exception')

    def test_later_retry_cannot_replace_original_bind_completion(self):
        with constructed(tied_prelude=True, original_bind_output=False) as value:
            with self.assertRaisesRegex(ValueError, 'HOLD_'):
                self.completed_hold(value)
            self.assertIsNone(P.load(value.store, PARENT)['assignments'][CHILD]['return'])

    def test_consequential_order_still_rejects_same_tick(self):
        obs = SUPPORT.load('compaction-result-observation.py')
        first = {'path': 'source-a', 'timestamp': '2026-10-23T00:00:00Z',
                 'locator': {'offset': 0, 'bytes': 1}}
        for path in ('source-a', 'source-b'):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'OBSERVATION_ORDER'):
                obs.before(first, {**first, 'path': path, 'locator': {'offset': 1, 'bytes': 1}})

    def test_child_hold64_passes65_refuses(self):
        obs = SUPPORT.load('compaction-result-observation.py')
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            path = Path(directory)/'hold.jsonl'
            header = {'timestamp': '2026-10-23T00:00:00Z', 'ordinal': 0,
                      'type': 'session_meta', 'payload': {'id': 'constructed-child'}}
            meta = obs.canonical(header)+b'\n'
            def write(count):
                path.write_bytes(meta+b''.join(obs.canonical({'timestamp': '2026-10-23T00:00:01Z',
                    'ordinal': index, 'type': 'event_msg', 'payload': {'type': 'token_count'}})+b'\n'
                    for index in range(1, count)))
            write(64)
            source = {'path': str(path), 'physical': obs.identity(path.stat()), 'history_start_ordinal': 1,
                'metadata': {'offset': 0, 'bytes': len(meta), 'sha256': obs.digest(meta),
                             'embedded_ordinal': 0, 'physical_line': 1},
                'metadata_payload_digest': obs.digest(obs.canonical(header['payload'])),
                'allowed_ranges': [{'offset': 0, 'bytes': obs.MAX_TOTAL}]}
            self.assertEqual(len(obs.hold_records({'child': source})[0]), 64)
            write(65)
            with self.assertRaisesRegex(ValueError, 'HOLD_RECORD_COUNT_BOUND'):
                obs.hold_records({'child': source})


def main():
    global ROOT, HERE, SUPPORT, H, O, OBS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=ROOT)
    parser.add_argument('--scratch-parent', type=Path)
    args = parser.parse_args()
    ROOT = args.repo_root.resolve(strict=True)
    support_path = ROOT/'fixtures/operational-evidence/native-episode-controls/native_test_support.py'
    spec = importlib.util.spec_from_file_location('native_test_support', support_path)
    SUPPORT = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = SUPPORT
    spec.loader.exec_module(SUPPORT)
    with tempfile.TemporaryDirectory(prefix='owned-stdio-source-', dir=args.scratch_parent) as directory:
        HERE = Path(directory).resolve(strict=True)
        SUPPORT.configure(ROOT, HERE)
        H, O, OBS = (SUPPORT.load(name) for name in ('bounded_source_owner.py',
            'compaction-source-owner-codex-app.py', 'compaction-result-observation.py'))
        if O.OWNED_STDIO_SELECTION_PIN is not None:
            raise ValueError('PRIVATE_SELECTION_FORBIDDEN_IN_PORTABLE_SOURCE_CONTROL')
        before = SUPPORT.source_pins()
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(kind)
            for kind in (PublicTurnControls, HoldOrderControls))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if SUPPORT.source_pins() != before:
            raise ValueError('PUBLIC_SOURCE_CHANGED_DURING_CONTROL')
        print(json.dumps({'scope': 'CONSTRUCTED_SOURCE_CONTROLS_NO_NATIVE_CREDIT',
            'executed': result.testsRun, 'success': result.wasSuccessful(), 'source_sha256': before}, sort_keys=True))
        return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
