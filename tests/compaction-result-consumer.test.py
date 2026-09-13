#!/usr/bin/env python3
"""Cold RETURN/JOIN consumer controls; no actual host/profile qualification."""
import importlib.util
import hashlib
import io
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(os.environ.get('IMPLEMENTAUDIT_F01_SOURCE_ROOT', Path(__file__).resolve().parents[1]))
spec = importlib.util.spec_from_file_location('pending_fixture_support', ROOT / 'tests/compaction-audit-pending.test.py')
legacy = importlib.util.module_from_spec(spec); spec.loader.exec_module(legacy)


class ResultConsumerTests(unittest.TestCase):
    def setUp(self):
        self.fx = legacy.PendingAuditTests()
        self.fx.setUp()
        self.fx.pending('resume')
        self.fx.reserve()
        self.observation = self.fx.observe()

    def caller_result(self):
        return {'child_id': 'child-a', 'observation_id': self.observation['observation_id'],
                'status': 'SUCCEEDED', 'currentness': 'UNRESOLVED', 'measured_epoch': 'UNRESOLVED',
                'frontier': 'Caller fields alone do not prove actual result or parent acceptance.'}

    def test_rc05_caller_status_cannot_be_actual_return(self):
        self.fx.pending('return', self.caller_result(), ok=False)
        self.assertTrue(self.fx.pending('status')['pending'])

    def test_rc09_six_field_path_cannot_consume_without_root_acceptance(self):
        before = self.fx.pending('status')['pending']
        result = self.fx.execute('compaction-audit-pending.py', '--store', str(self.fx.store),
            '--session', self.fx.session, '--owner-id', 'host-owner', 'return', payload=self.caller_result(), ok=False)
        if result.returncode == 0:
            self.fx.join(json.loads(result.stdout), ok=False)
        self.assertEqual(self.fx.pending('status')['pending'], before)


class BoundedExtractorTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / 'skills/implementaudit/scripts/compaction-result-observation.py'
        self.assertTrue(path.exists(), 'Source-owned bounded extractor is absent')
        spec = importlib.util.spec_from_file_location('result_observation', path)
        self.module = importlib.util.module_from_spec(spec); spec.loader.exec_module(self.module)

    def record_fixture(self):
        root = Path(tempfile.mkdtemp(prefix='bounded-record-', dir=os.environ['IMPLEMENTAUDIT_TEST_ROOT']))
        path = root / 'public.jsonl'
        raw = (json.dumps({'timestamp': '2026-09-10T15:11:08.860Z', 'ordinal': 7,
                'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant',
                'phase': 'commentary', 'content': [{'type': 'output_text', 'text': 'Public fixture record'}]}}) + '\n').encode()
        path.write_bytes(raw)
        selector = {'offset': 0, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                    'embedded_ordinal': 7, 'physical_line': 9}
        return path, raw, selector, [{'offset': 0, 'bytes': len(raw)}]

    def test_rc13_copied_physical_identity_and_changed_wire_are_refused(self):
        path, raw, selector, windows = self.record_fixture()
        observed = self.module.read_records(path.resolve(), [selector], windows)
        copied = path.with_name('copy.jsonl'); copied.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'SOURCE_PHYSICAL_ID_CHANGED'):
            self.module.read_records(copied.resolve(), [selector], windows, observed['physical'])
        path.write_bytes(raw.replace(b'Public fixture record', b'Forged fixture record'))
        with self.assertRaisesRegex(ValueError, 'RECORD_PIN_CHANGED'):
            self.module.read_records(path.resolve(), [selector], windows, observed['physical'])

    def test_rc13_hardlink_alias_and_partial_record_are_refused(self):
        path, raw, selector, windows = self.record_fixture()
        partial = {**selector, 'bytes': len(raw) - 1, 'sha256': hashlib.sha256(raw[:-1]).hexdigest()}
        with self.assertRaisesRegex(ValueError, 'RECORD_PARTIAL_OR_MULTIPLE_WIRE'):
            self.module.read_records(path.resolve(), [partial], windows)
        os.link(path, path.with_name('hardlink.jsonl'))
        with self.assertRaisesRegex(ValueError, 'SOURCE_FILE_KIND'):
            self.module.read_records(path.resolve(), [selector], windows)

    def test_rc21_mismatched_embedded_ordinal_is_not_normalized_to_physical_label(self):
        path, raw, selector, windows = self.record_fixture()
        with self.assertRaisesRegex(ValueError, 'OBSERVED_RECORD_SHAPE_OR_ORDINAL'):
            self.module.read_records(path.resolve(), [{**selector, 'embedded_ordinal': 9}], windows)

    def test_rc22_disallowed_range_is_refused_before_open(self):
        selector = {'offset': 20, 'bytes': 30, 'sha256': '0'*64,
                    'embedded_ordinal': 7, 'physical_line': 9}
        with mock.patch('builtins.open', side_effect=AssertionError('Read outside accepted range')):
            with self.assertRaisesRegex(ValueError, 'OUTSIDE_ALLOWED_READ_RANGE'):
                self.module.read_records(Path(__file__).resolve(), [selector], [{'offset': 25, 'bytes': 25}])

    def test_rc21_rc22_exact_seek_keeps_physical_label_distinct(self):
        parent = Path(os.environ['IMPLEMENTAUDIT_TEST_ROOT'])
        path = parent / 'bounded-extractor-source.jsonl'
        raw = (json.dumps({'timestamp': '2026-09-10T15:11:08.860Z', 'ordinal': 7,
                'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant',
                'phase': 'commentary', 'content': [{'type': 'output_text', 'text': 'Public fixture record'}]}}) + '\n').encode()
        prefix = b'INHERITED PREFIX MUST NOT BE READ\n'
        path.write_bytes(prefix + raw + b'PRIVATE SUFFIX MUST NOT BE READ\n')
        selector = {'offset': len(prefix), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                    'embedded_ordinal': 7, 'physical_line': 9}
        original = open
        class Guarded:
            def __init__(self, stream): self.stream = stream
            def __enter__(self): return self
            def __exit__(self, *args): self.stream.close()
            def fileno(self): return self.stream.fileno()
            def seek(self, offset):
                if offset != len(prefix): raise AssertionError('Unbounded seek')
                return self.stream.seek(offset)
            def read(self, count):
                if self.stream.tell() != len(prefix) or count != len(raw):
                    raise AssertionError('Read outside exact public range')
                return self.stream.read(count)
        with mock.patch('builtins.open', side_effect=lambda *args, **kwargs: Guarded(original(*args, **kwargs))):
            observed = self.module.read_records(path.resolve(), [selector], [{'offset': len(prefix), 'bytes': len(raw)}])
        self.assertEqual(observed['records'][0]['locator'], selector)
        self.assertEqual(observed['records'][0]['row']['ordinal'], 7)
        self.assertEqual(observed['records'][0]['locator']['physical_line'], 9)
        self.assertFalse(observed['host_producer_authenticated'])


class ProspectiveChainTests(unittest.TestCase):
    def setUp(self):
        self.fx = legacy.PendingAuditTests(); self.fx.setUp()
        self.fx.pending('resume')
        self.child = 'child-a'
        self.tick = 0
        self.logs = {role: self.fx.home / 'sessions' / ('rollout-' + identifier + '.jsonl')
                     for role, identifier in [('parent', self.fx.session), ('child', 'child-a')]}
        self.ordinals = {'parent': 0, 'child': 0}
        self.lines = {'parent': 0, 'child': 0}
        parent_meta = self.row('parent', 'session_meta', {'id': self.fx.session, 'session_id': self.fx.session,
            'originator': 'Codex Desktop', 'cli_version': '0.153.4', 'source': 'vscode', 'thread_source': 'user'})
        child_meta = self.row('child', 'session_meta', {'id': 'child-a', 'session_id': self.fx.session,
            'parent_thread_id': self.fx.session, 'forked_from_id': self.fx.session,
            'originator': 'Codex Desktop', 'cli_version': '0.153.4', 'thread_source': 'subagent',
            'agent_path': '/root/child-a', 'subagent_history_start_ordinal': 76,
            'source': {'subagent': {'thread_spawn': {'parent_thread_id': self.fx.session, 'agent_path': '/root/child-a'}}}})
        self.ordinals['child'] = 76
        opened = self.message('parent', '```ini\nCHILD_TASK=child-a\nCHILD_TASK_KIND=GOVERNED_CHILD_SKILL\nCHILD_SKILL_SELECTED=audit-state\nSTATUS=OPEN\nLOAD=UNVERIFIED\n```')
        spawn = self.row('parent', 'response_item', {'type': 'function_call', 'name': 'spawn_agent',
            'namespace': 'collaboration', 'call_id': 'spawn-a', 'arguments': json.dumps({'task_name': 'child-a', 'message': 'Opaque notification'})})
        spawned = self.row('parent', 'response_item', {'type': 'function_call_output', 'call_id': 'spawn-a',
            'output': json.dumps({'task_name': '/root/child-a'})})
        self.context = {role: {'path': str(self.logs[role]), 'metadata': meta,
            'allowed_ranges': [{'offset': 0, 'bytes': 2 * 1024 * 1024}]}
            for role, meta in [('parent', parent_meta), ('child', child_meta)]}
        self.context.update(open=opened, spawn_call=spawn, spawn_output=spawned)

    def row(self, role, kind, payload):
        self.tick += 1
        raw = (json.dumps({'timestamp': (datetime(2026, 9, 10, tzinfo=timezone.utc) + timedelta(seconds=self.tick)).isoformat(),
            'ordinal': self.ordinals[role], 'type': kind, 'payload': payload}, separators=(',', ':')) + '\n').encode()
        path = self.logs[role]; offset = path.stat().st_size if path.exists() else 0
        with path.open('ab') as stream: stream.write(raw)
        self.lines[role] += 1
        locator = {'offset': offset, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                   'embedded_ordinal': self.ordinals[role], 'physical_line': self.lines[role]}
        self.ordinals[role] += 1
        return locator

    def message(self, role, content, phase='commentary'):
        return self.row(role, 'response_item', {'type': 'message', 'id': 'message-' + str(self.tick),
            'role': 'assistant', 'phase': phase, 'content': [{'type': 'output_text', 'text': content}]})

    def reserve(self):
        return self.fx.pending('reserve', {'child_id': self.child, 'bounded_purpose': 'Reconcile only the exact owned compaction scope.',
                                          'observation_source': self.context})

    def adapter(self):
        path = ROOT / 'skills/implementaudit/scripts/compaction-result-observation.py'
        spec = importlib.util.spec_from_file_location('prospective_adapter', path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module

    def exchange(self, role, call_id, tool_input, output):
        call = self.row(role, 'response_item', {'type': 'custom_tool_call', 'name': 'exec',
            'call_id': call_id, 'status': 'completed', 'input': tool_input})
        result = self.row(role, 'response_item', {'type': 'custom_tool_call_output', 'call_id': call_id,
            'output': [{'type': 'input_text', 'text': 'Script completed\nOutput:\n'},
                       {'type': 'input_text', 'text': json.dumps({'chunk_id': call_id, 'wall_time_seconds': 0.1,
                        'exit_code': 0, 'original_token_count': 100, 'output': output})}]})
        return call, result

    def authorization(self, reserved):
        adapter = self.adapter()
        self.assertTrue(callable(getattr(adapter, 'load_tool_input', None)), 'Source-defined full LOAD exchange is absent')
        skill = ROOT / 'skills/audit-state/SKILL.md'; raw = skill.read_bytes()
        skill_pin = {'path': str(skill), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        load, loaded = self.exchange('child', 'load-a', adapter.load_tool_input(skill_pin),
            json.dumps({**skill_pin, 'utf8': raw.decode()}))
        route = self.message('parent', '```ini\nCHILD_TASK=' + self.child + '\nCHILD_SKILL_ROUTE=audit-state\nLOAD=VERIFIED\n```')
        def record_identity(role, locator, call_id):
            info = self.logs[role].stat()
            with self.logs[role].open('rb') as stream:
                stream.seek(locator['offset']); row = json.loads(stream.read(locator['bytes']))
            return {'path': str(self.logs[role]), 'physical': {'device': info.st_dev, 'inode': info.st_ino},
                'role': role, 'locator': locator, 'timestamp': row['timestamp'], 'message_or_call_id': call_id}
        load_identity = adapter.digest(adapter.canonical({'call': record_identity('child', load, 'load-a'),
                                                          'result': record_identity('child', loaded, 'load-a')}))
        o = reserved['obligation']
        value = {'schema': 'implementaudit.compaction-use-authorization.v1',
            'action': 'AUTHORIZE_BOUNDED_POST_COMPACTION_RECONCILIATION', 'parent_identity': o['parent_identity'],
            'actual_child_identity': o['actual_child_identity'], 'obligation_digest': reserved['obligation_digest'],
            'observation_id': o['observation_id'], 'load_observation_identity': load_identity,
            'selected_child': 'audit-state', 'skill_source_pin': skill_pin, 'authority_ceiling': 'NONE'}
        u = self.message('parent', '```json\n' + json.dumps(value, sort_keys=True) + '\n```')
        return {'load_call': load, 'load_output': loaded, 'route': route, 'authorization': u}

    def test_rc07_actual_full_delivery_must_precede_observation_binding(self):
        reserved = self.reserve()
        evidence = self.authorization(reserved)
        request = {'child_id': self.child, 'phase': 'deliver', 'observation_id': reserved['obligation']['observation_id'],
                   'authorization_evidence': evidence}
        packet = self.fx.pending('observe-child', request)
        self.assertEqual(packet['obligation_utf8'], Path(reserved['obligation_pin']['path']).read_text())
        self.assertFalse(packet['host_producer_authenticated'])
        state = json.loads(next(self.fx.store.rglob('pending.json')).read_bytes())
        self.assertFalse(state['assignments']['child-a']['observations'], 'The helper credited its own future response')
        adapter = self.adapter()
        call, result = self.exchange('child', 'observe-a',
            adapter.delivery_tool_input(self.fx.store, self.fx.session, 'host-owner', request), json.dumps(packet))
        bind = {'child_id': self.child, 'phase': 'bind',
            'observation_id': request['observation_id'], 'exchange': {'call': call, 'result': result}}
        self.row('child', 'response_item', {'type': 'custom_tool_call', 'name': 'exec',
            'call_id': 'bind-a', 'status': 'completed',
            'input': adapter.delivery_tool_input(self.fx.store, self.fx.session, 'host-owner', bind)})
        bound = self.fx.pending('observe-child', bind)
        self.row('child', 'response_item', {'type': 'custom_tool_call_output', 'call_id': 'bind-a',
            'output': [{'type': 'input_text', 'text': 'Script completed\nOutput:\n'},
                       {'type': 'input_text', 'text': json.dumps({'chunk_id': 'bind-a', 'wall_time_seconds': 0.1,
                        'exit_code': 0, 'original_token_count': 100, 'output': json.dumps(bound)})}]})
        self.assertEqual(bound['observation_id'], request['observation_id'])
        self.assertTrue(bound['child_observation_exchange_identity'])
        self.assertTrue(self.fx.pending('status')['pending'])

    def bound_observation(self, reserved=None):
        reserved = reserved or self.reserve(); evidence = self.authorization(reserved); adapter = self.adapter()
        identifier = reserved['obligation']['observation_id']
        deliver = {'child_id': self.child, 'phase': 'deliver', 'observation_id': identifier, 'authorization_evidence': evidence}
        packet = self.fx.pending('observe-child', deliver)
        call, result = self.exchange('child', 'observe-a',
            adapter.delivery_tool_input(self.fx.store, self.fx.session, 'host-owner', deliver), json.dumps(packet))
        bind = {'child_id': self.child, 'phase': 'bind', 'observation_id': identifier, 'exchange': {'call': call, 'result': result}}
        # The composed F02 owner must observe the real attempted bind before
        # handling it. Keep its response after the operation, as in the held
        # interval fixture; a retrospective synthetic pair is insufficient.
        call = self.row('child', 'response_item', {'type': 'custom_tool_call', 'name': 'exec',
            'call_id': 'bind-a', 'status': 'completed',
            'input': adapter.delivery_tool_input(self.fx.store, self.fx.session, 'host-owner', bind)})
        observed = self.fx.pending('observe-child', bind)
        result = self.row('child', 'response_item', {'type': 'custom_tool_call_output', 'call_id': 'bind-a',
            'output': [{'type': 'input_text', 'text': 'Script completed\nOutput:\n'},
                       {'type': 'input_text', 'text': json.dumps({'chunk_id': 'bind-a', 'wall_time_seconds': 0.1,
                        'exit_code': 0, 'original_token_count': 100, 'output': json.dumps(observed)})}]})
        return reserved, observed, {'call': call, 'result': result}

    def actual_result(self, reserved, observed, bound_exchange, status='SUCCEEDED'):
        exchange_id = observed['child_observation_exchange_identity']
        use_call, use_output = self.exchange('child', 'use-a', '// COMPACTION_OBSERVATION_EXCHANGE=' + exchange_id + '\ntext("bounded fixture work");', 'bounded fixture work')
        root = self.fx.root / ('actual-result-' + observed['observation_id']); root.mkdir()
        member = root / 'finding.txt'; member.write_text('Bounded fixture findings; no actual producer qualification.', encoding='utf-8')
        def pin(path):
            raw = path.read_bytes()
            return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        o = reserved['obligation']
        result_body = {'schema': 'implementaudit.compaction-reconciliation-result.v1',
            'obligation_digest': reserved['obligation_digest'], 'observation_id': o['observation_id'],
            'child_observation_exchange_identity': exchange_id,
            'exact_observed_boundary_versions': o['covered_boundary_versions'], 'code_and_skill_pins': o['code_and_skill_pins'],
            'status': status, 'currentness': 'UNRESOLVED', 'measured_epoch': 'UNRESOLVED', 'frontier': 'Bounded fixture finding.',
            'members': [pin(member)], 'authority_ceiling': 'NONE'}
        path = root / 'RESULT.json'; path.write_text(json.dumps(result_body), encoding='utf-8')
        r = {'schema': 'implementaudit.compaction-result-return.v1', 'obligation_digest': reserved['obligation_digest'],
            'observation_id': o['observation_id'], 'child_observation_exchange_identity': exchange_id,
            'exact_observed_boundary_versions': o['covered_boundary_versions'], 'result_bytes_identity': pin(path),
            'authority_ceiling': 'NONE'}
        text = '```json\n' + json.dumps(r, sort_keys=True) + '\n```'
        final = self.message('child', text, 'final_answer')
        delivery = self.row('parent', 'response_item', {'type': 'agent_message', 'id': 'returned-a',
            'author': '/root/' + self.child, 'recipient': '/root', 'content': [{'type': 'input_text',
            'text': 'Message Type: FINAL_ANSWER\nTask name: /root\nSender: /root/' + self.child + '\nPayload:\n' + text}]})
        return {'bound_exchange': bound_exchange, 'use': {'call': use_call, 'result': use_output},
                'child_final': final, 'parent_delivery': delivery}

    def test_rc01_complete_cold_chain_reaches_profile_gate_without_consuming(self):
        reserved, observed, bound_exchange = self.bound_observation()
        evidence = self.actual_result(reserved, observed, bound_exchange)
        result = self.fx.pending('return', {'child_id': self.child, 'observation_id': observed['observation_id'], 'result_evidence': evidence})
        before = self.fx.pending('status')['pending']
        o = reserved['obligation']
        acceptance = {'schema': 'implementaudit.compaction-reconciliation-acceptance.v1', 'action': 'ACCEPT_BOUNDED_RECONCILIATION',
            'parent_identity': o['parent_identity'], 'actual_child_identity': o['actual_child_identity'],
            'obligation_digest': reserved['obligation_digest'], 'observation_id': observed['observation_id'],
            'child_observation_exchange_identity': observed['child_observation_exchange_identity'],
            'actual_result_digest': result['return_digest'], 'accepted_boundary_versions': o['covered_boundary_versions'],
            'observation_source_cutoff': o['observation_source_cutoff'], 'authority_ceiling': 'NONE'}
        accepted = self.message('parent', '```json\n' + json.dumps(acceptance, sort_keys=True) + '\n```')
        joined = self.fx.pending('join', {'child_id': self.child, 'return_digest': result['return_digest'], 'acceptance': accepted})
        self.assertEqual(joined['status'], 'VERIFIED_LOGICAL_JOIN_PENDING_PROFILE')
        self.assertEqual(joined['proposed_consumption'], before)
        self.assertFalse(joined['pending_consumed'])
        self.assertFalse(joined['host_producer_authenticated'])
        self.assertEqual(self.fx.pending('status')['pending'], before)
        self.assertEqual(joined['projected_pending'], [])

    def test_rc01_obligation_is_materialized_by_real_reserve(self):
        before = self.fx.pending('status')['pending']
        reserved = self.reserve()
        obligation = reserved['obligation']
        self.assertEqual(obligation['schema'], 'implementaudit.compaction-obligation.v1')
        self.assertEqual(obligation['covered_boundary_versions'], before)
        self.assertEqual(obligation['actual_child_identity']['thread_id'], 'child-a')
        self.assertNotEqual(obligation['parent_identity']['thread_id'], obligation['actual_child_identity']['thread_id'])
        self.assertEqual(obligation['authority_ceiling'], 'NONE')
        self.assertEqual(json.loads(Path(reserved['obligation_pin']['path']).read_bytes()), obligation)
        self.assertEqual(self.fx.pending('status')['pending'], before)


    def state_bytes(self):
        return next(self.fx.store.rglob('pending.json')).read_bytes()

    def copy_record(self, role, locator, mutate):
        with self.logs[role].open('rb') as stream:
            stream.seek(locator['offset']); row = json.loads(stream.read(locator['bytes']))
        mutate(row)
        return self.row(role, row['type'], row['payload'])

    def typed_value(self, role, locator):
        with self.logs[role].open('rb') as stream:
            stream.seek(locator['offset']); row = json.loads(stream.read(locator['bytes']))
        return json.loads(row['payload']['content'][0]['text'][8:-4])

    def refused(self, action, request, reason=None):
        before = self.state_bytes()
        result = self.fx.pending(action, request, ok=False)
        value = json.loads(result.stdout)
        self.assertEqual(value['status'], 'PENDING_OPERATION_REFUSED')
        if reason:
            self.assertIn(reason, value['reason'])
        self.assertEqual(self.state_bytes(), before, 'A refused operation mutated pending state')
        return value

    def acceptance_value(self, reserved, observed, result):
        o = reserved['obligation']
        return {'schema': 'implementaudit.compaction-reconciliation-acceptance.v1', 'action': 'ACCEPT_BOUNDED_RECONCILIATION',
            'parent_identity': o['parent_identity'], 'actual_child_identity': o['actual_child_identity'],
            'obligation_digest': reserved['obligation_digest'], 'observation_id': observed['observation_id'],
            'child_observation_exchange_identity': observed['child_observation_exchange_identity'],
            'actual_result_digest': result['return_digest'], 'accepted_boundary_versions': o['covered_boundary_versions'],
            'observation_source_cutoff': o['observation_source_cutoff'], 'authority_ceiling': 'NONE'}

    def returned_chain(self, reserved=None, status='SUCCEEDED'):
        reserved, observed, bound = self.bound_observation(reserved)
        evidence = self.actual_result(reserved, observed, bound, status)
        request = {'child_id': self.child, 'observation_id': observed['observation_id'], 'result_evidence': evidence}
        result = self.fx.pending('return', request)
        return reserved, observed, result, request

    def accepted_chain(self, reserved=None):
        reserved, observed, result, request = self.returned_chain(reserved)
        value = self.acceptance_value(reserved, observed, result)
        accepted = self.message('parent', '```json\n' + json.dumps(value, sort_keys=True) + '\n```')
        join = {'child_id': self.child, 'return_digest': result['return_digest'], 'acceptance': accepted}
        return self.fx.pending('join', join), join

    def test_rc06_rc07_public_authorization_rejects_wrong_identity_role_and_quotation(self):
        reserved = self.reserve(); evidence = self.authorization(reserved)
        value = self.typed_value('parent', evidence['authorization'])
        request = {'child_id': self.child, 'phase': 'deliver', 'observation_id': reserved['obligation']['observation_id'],
                   'authorization_evidence': evidence}
        for field in ('parent_identity', 'actual_child_identity', 'obligation_digest', 'observation_id',
                      'load_observation_identity', 'selected_child', 'skill_source_pin', 'authority_ceiling'):
            with self.subTest(field=field):
                changed = {**value, field: 'foreign'}
                pin = self.message('parent', '```json\n' + json.dumps(changed) + '\n```')
                self.refused('observe-child', {**request, 'authorization_evidence': {**evidence, 'authorization': pin}})
        pin = self.message('parent', '> ```json\n' + json.dumps(value) + '\n```')
        self.refused('observe-child', {**request, 'authorization_evidence': {**evidence, 'authorization': pin}}, 'TYPED_PUBLIC')
        pin = self.message('parent', '```json\n' + json.dumps(value) + '\n```', 'final_answer')
        self.refused('observe-child', {**request, 'authorization_evidence': {**evidence, 'authorization': pin}}, 'ROLE_OR_PHASE')
        pin = self.copy_record('parent', evidence['authorization'], lambda row: row['payload'].update(role='user'))
        self.refused('observe-child', {**request, 'authorization_evidence': {**evidence, 'authorization': pin}}, 'ROLE_OR_PHASE')
        pin = self.message('child', '```json\n' + json.dumps(value) + '\n```')
        self.refused('observe-child', {**request, 'authorization_evidence': {**evidence, 'authorization': pin}})

    def test_rc07_load_truncation_late_route_and_opaque_ack_are_refused(self):
        reserved = self.reserve(); evidence = self.authorization(reserved)
        request = {'child_id': self.child, 'phase': 'deliver', 'observation_id': reserved['obligation']['observation_id'],
                   'authorization_evidence': evidence}
        def truncate(row):
            data = json.loads(row['payload']['output'][1]['text'])
            body = json.loads(data['output']); body['utf8'] = body['utf8'][:100]
            data['output'] = json.dumps(body); row['payload']['output'][1]['text'] = json.dumps(data)
        changed = self.copy_record('child', evidence['load_output'], truncate)
        self.refused('observe-child', {**request, 'authorization_evidence': {**evidence, 'load_output': changed}}, 'FULL_SKILL_LOAD_DIFFERS')
        late = self.copy_record('parent', evidence['route'], lambda row: None)
        self.refused('observe-child', {**request, 'authorization_evidence': {**evidence, 'route': late}}, 'OBSERVATION_ORDER')
        opaque = self.row('parent', 'response_item', {'type': 'agent_message', 'encrypted_content': 'matching-ciphertext'})
        self.refused('observe-child', {**request, 'authorization_evidence': {**evidence, 'authorization': opaque}}, 'ROLE_OR_PHASE')

    def test_rc10_full_same_child_exchange_is_required_before_binding(self):
        reserved = self.reserve(); evidence = self.authorization(reserved); adapter = self.adapter()
        deliver = {'child_id': self.child, 'phase': 'deliver', 'observation_id': reserved['obligation']['observation_id'],
                   'authorization_evidence': evidence}
        packet = self.fx.pending('observe-child', deliver)
        call, result = self.exchange('child', 'short-delivery', adapter.delivery_tool_input(self.fx.store, self.fx.session, 'host-owner', deliver),
                                     json.dumps({**packet, 'obligation_utf8': packet['obligation_utf8'][:100]}))
        bind = {'child_id': self.child, 'phase': 'bind', 'observation_id': deliver['observation_id'], 'exchange': {'call': call, 'result': result}}
        self.refused('observe-child', bind, 'FULL_OBLIGATION_AUTHORIZATION_RESPONSE_DIFFERS')
        call, result = self.exchange('parent', 'foreign-delivery', adapter.delivery_tool_input(self.fx.store, self.fx.session, 'host-owner', deliver), json.dumps(packet))
        self.refused('observe-child', {**bind, 'exchange': {'call': call, 'result': result}})
        self.assertFalse(json.loads(self.state_bytes())['assignments'][self.child]['observations'])

    def test_rc08_result_artifact_member_copy_and_changed_source_are_refused(self):
        reserved, observed, result, request = self.returned_chain()
        member = Path(result['identity']['members'][0]['pin']['path'])
        original = member.read_bytes()
        member.write_bytes(b'Changed bounded finding')
        self.refused('return', request, 'ARTIFACT_BYTE_COUNT')
        member.write_bytes(original)
        replacement = member.with_name('replacement.txt'); replacement.write_bytes(original)
        os.replace(replacement, member)
        self.refused('return', request, 'CONFLICTING_RETURN')

    def test_rc08_foreign_scope_in_actual_final_is_refused(self):
        reserved, observed, bound = self.bound_observation()
        evidence = self.actual_result(reserved, observed, bound)
        value = self.typed_value('child', evidence['child_final'])
        value['exact_observed_boundary_versions'] = []
        text = '```json\n' + json.dumps(value, sort_keys=True) + '\n```'
        final = self.message('child', text, 'final_answer')
        delivery = self.row('parent', 'response_item', {'type': 'agent_message', 'id': 'changed-return',
            'author': '/root/' + self.child, 'recipient': '/root', 'content': [{'type': 'input_text',
            'text': 'Message Type: FINAL_ANSWER\nTask name: /root\nSender: /root/' + self.child + '\nPayload:\n' + text}]})
        self.refused('return', {'child_id': self.child, 'observation_id': observed['observation_id'],
            'result_evidence': {**evidence, 'child_final': final, 'parent_delivery': delivery}}, 'ACTUAL_RETURN_OBLIGATION_OR_SCOPE_DIFFERS')

    def test_rc07_use_before_bound_host_response_is_refused(self):
        reserved, observed, bound = self.bound_observation()
        # Keep the original bind selectors. Give USE an earlier claimed time
        # to reach temporal-order validation after original-bind validation.
        self.tick -= 2
        evidence = self.actual_result(reserved, observed, bound)
        self.refused('return', {'child_id': self.child, 'observation_id': observed['observation_id'],
            'result_evidence': evidence}, 'OBSERVATION_ORDER')

    def test_rc09_wrong_root_acceptance_tuple_role_and_hold_cannot_consume(self):
        reserved, observed, result, request = self.returned_chain()
        value = self.acceptance_value(reserved, observed, result)
        for field in ('parent_identity', 'actual_child_identity', 'obligation_digest', 'observation_id',
                      'child_observation_exchange_identity', 'actual_result_digest', 'accepted_boundary_versions',
                      'observation_source_cutoff', 'authority_ceiling', 'action'):
            with self.subTest(field=field):
                changed = {**value, field: 'HOLD'}
                pin = self.message('parent', '```json\n' + json.dumps(changed) + '\n```')
                self.refused('join', {'child_id': self.child, 'return_digest': result['return_digest'], 'acceptance': pin})
        for text in ('I accepted it.', '> quoted acceptance', '```json\n' + json.dumps(value) + '\n```'):
            pin = self.message('child', text)
            self.refused('join', {'child_id': self.child, 'return_digest': result['return_digest'], 'acceptance': pin})

    def test_rc04_exact_logical_retry_is_byte_idempotent_conflicting_record_refused(self):
        joined, request = self.accepted_chain()
        before = self.state_bytes()
        self.assertEqual(self.fx.pending('join', request), joined)
        self.assertEqual(before, self.state_bytes())
        duplicate = self.copy_record('parent', request['acceptance'], lambda row: None)
        self.refused('join', {**request, 'acceptance': duplicate}, 'CONFLICTING_ROOT_ACCEPTANCE')

    def test_rc04_same_acceptance_retry_after_later_boundary_is_still_idempotent(self):
        joined, request = self.accepted_chain()
        self.fx.pending('resume')
        before = self.state_bytes()
        self.assertEqual(self.fx.pending('join', request), joined)
        self.assertEqual(self.state_bytes(), before)
        self.assertEqual(self.fx.pending('status')['pending'][0]['version'], 2)

    def test_rc06_reservation_retry_cannot_rebind_purpose_or_source(self):
        self.reserve()
        self.refused('reserve', {'child_id': self.child, 'bounded_purpose': 'Foreign purpose',
            'observation_source': self.context}, 'CONFLICTING_RESERVATION')

    def test_rc11_later_unresolved_resume_stays_outside_actual_result_scope(self):
        reserved, observed, result, request = self.returned_chain()
        self.fx.pending('resume')
        value = self.acceptance_value(reserved, observed, result)
        accepted = self.message('parent', '```json\n' + json.dumps(value) + '\n```')
        joined = self.fx.pending('join', {'child_id': self.child, 'return_digest': result['return_digest'], 'acceptance': accepted})
        self.assertEqual(joined['projected_pending'][0]['version'], 2)
        self.assertEqual(joined['proposed_consumption'][0]['version'], 1)
        self.assertFalse(joined['pending_consumed'])
        self.assertEqual(self.fx.pending('status')['decision'], 'WAIT_EXISTING_AUDIT')

    def test_rc16_failed_actual_return_and_caller_terminal_never_release_assignment(self):
        reserved, observed, result, request = self.returned_chain(status='FAILED')
        self.assertEqual(result['status'], 'FAILED')
        self.refused('join', {'child_id': self.child, 'return_digest': result['return_digest'], 'acceptance': {}}, 'EXACT_SUCCESSFUL_RETURN_REQUIRED')
        self.refused('reserve', {'child_id': 'retry', 'terminal': True}, 'RESERVATION_SHAPE')
        self.fx.pending('reserve', {'child_id': 'retry'}, ok=False)
        self.assertTrue(self.fx.pending('status')['pending'])

    def test_rc15_interrupted_actual_return_retains_pending_and_assignment(self):
        reserved, observed, bound = self.bound_observation()
        evidence = self.actual_result(reserved, observed, bound)
        path = ROOT / 'skills/implementaudit/scripts/compaction-audit-pending.py'
        spec = importlib.util.spec_from_file_location('interrupted_actual_owner', path)
        owner = importlib.util.module_from_spec(spec); spec.loader.exec_module(owner)
        before = self.state_bytes()
        with mock.patch.dict(os.environ, self.fx.env, clear=True), mock.patch.object(owner.CORE.os, 'replace', side_effect=OSError('interrupted atomic write')):
            with self.assertRaisesRegex(OSError, 'interrupted'):
                owner.operate(self.fx.store, self.fx.session, 'host-owner', 'return',
                    {'child_id': self.child, 'observation_id': observed['observation_id'], 'result_evidence': evidence})
        self.assertEqual(before, self.state_bytes())
        self.fx.pending('reserve', {'child_id': 'competing'}, ok=False)

    def start_other_child(self, child):
        self.child = child
        self.logs['child'] = self.fx.home / 'sessions' / ('rollout-' + child + '.jsonl')
        self.ordinals['child'] = self.lines['child'] = 0
        meta = self.row('child', 'session_meta', {'id': child, 'session_id': self.fx.session,
            'parent_thread_id': self.fx.session, 'forked_from_id': self.fx.session, 'originator': 'Codex Desktop',
            'cli_version': '0.153.4', 'thread_source': 'subagent', 'agent_path': '/root/' + child,
            'subagent_history_start_ordinal': 76, 'source': {'subagent': {'thread_spawn': {
                'parent_thread_id': self.fx.session, 'agent_path': '/root/' + child}}}})
        self.ordinals['child'] = 76
        opened = self.message('parent', '```ini\nCHILD_TASK=' + child + '\nCHILD_TASK_KIND=GOVERNED_CHILD_SKILL\nCHILD_SKILL_SELECTED=audit-state\nSTATUS=OPEN\nLOAD=UNVERIFIED\n```')
        spawn = self.row('parent', 'response_item', {'type': 'function_call', 'namespace': 'collaboration', 'name': 'spawn_agent',
            'call_id': 'spawn-' + child, 'arguments': json.dumps({'task_name': child, 'message': 'Fixture notification'})})
        spawned = self.row('parent', 'response_item', {'type': 'function_call_output', 'call_id': 'spawn-' + child,
            'output': json.dumps({'task_name': '/root/' + child})})
        self.context = {**self.context, 'child': {'path': str(self.logs['child']), 'metadata': meta,
            'allowed_ranges': [{'offset': 0, 'bytes': 2 * 1024 * 1024}]}, 'open': opened, 'spawn_call': spawn, 'spawn_output': spawned}

    def test_rc02_currentness_epoch_and_independent_children_do_not_gain_authority(self):
        for currentness, epoch in [('VERIFIED', 'VERIFIED'), ('UNRESOLVED', 'VERIFIED'), ('UNRESOLVED', 'UNRESOLVED')]:
            status = self.fx.pending('resume', {'currentness': currentness, 'measured_epoch': epoch})
            self.assertEqual(status['decision'], 'AUDIT_STATE_REQUIRED')
        reserved, observed, result, request = self.returned_chain()
        self.assertEqual(result['currentness'], 'UNRESOLVED')
        self.assertEqual(result['measured_epoch'], 'UNRESOLVED')
        for value in (status, reserved, observed, result):
            self.assertEqual(value['authority'], 'NONE')
            for flag in ('canonical_currentness', 'recovery_authority', 'epoch_authority', 'effect_authority'):
                self.assertFalse(value[flag])
            self.assertEqual(value['independent_children'], 'UNCHANGED')

    def test_rc12_failed_a_allows_proved_b_logical_join_and_retains_failed_a(self):
        self.returned_chain(status='FAILED')
        old = json.loads(self.state_bytes())['assignments']['child-a']
        self.fx.compact('independent-b'); self.fx.register(); self.fx.hook()
        self.assertEqual(self.fx.pending('status')['decision'], 'AUDIT_STATE_REQUIRED')
        self.start_other_child('child-b')
        joined, _ = self.accepted_chain()
        self.assertEqual([v['kind'] for v in joined['proposed_consumption']], ['COMPLETED_RESUMED_BOUNDARY'])
        self.assertTrue(joined['projected_pending'])
        self.assertNotIn('COMPLETED_RESUMED_BOUNDARY', [v['kind'] for v in joined['projected_pending']])
        self.assertEqual(json.loads(self.state_bytes())['assignments']['child-a'], old)
        self.assertTrue(self.fx.pending('status')['state_dependent_decisions_held'])

    def test_rc03_active_child_expands_only_with_new_completed_observation(self):
        self.fx.compact(); self.fx.register(); self.fx.hook()
        first, observed, bound = self.bound_observation()
        self.fx.compact('next-b'); self.fx.hook()
        prepared = self.fx.pending('observe-child', {'child_id': self.child, 'phase': 'prepare'})
        state = json.loads(self.state_bytes())
        self.assertNotIn(prepared['obligation']['observation_id'], state['assignments'][self.child]['observations'])
        self.assertNotEqual(first['obligation']['observation_id'], prepared['obligation']['observation_id'])
        joined, _ = self.accepted_chain(prepared)
        self.assertEqual(len([v for v in joined['proposed_consumption'] if v['kind'] == 'COMPLETED_RESUMED_BOUNDARY']), 2)
        self.assertEqual(joined['projected_pending'], [])

    def test_rc11_insufficient_old_result_cannot_cover_later_prepared_scope(self):
        self.fx.compact(); self.fx.register(); self.fx.hook()
        first, observed, bound = self.bound_observation()
        self.fx.compact('next-b'); self.fx.hook()
        second = self.fx.pending('observe-child', {'child_id': self.child, 'phase': 'prepare'})
        evidence = self.actual_result(first, observed, bound)
        result = self.fx.pending('return', {'child_id': self.child, 'observation_id': observed['observation_id'], 'result_evidence': evidence})
        value = self.acceptance_value(first, observed, result)
        a = self.message('parent', '```json\n' + json.dumps(value) + '\n```')
        joined = self.fx.pending('join', {'child_id': self.child, 'return_digest': result['return_digest'], 'acceptance': a})
        self.assertEqual(len(joined['projected_pending']), 2)
        self.assertEqual(self.fx.pending('status')['decision'], 'WAIT_EXISTING_AUDIT')
        self.fx.pending('reserve', {'child_id': 'insufficient-retry'}, ok=False)
        self.assertNotIn(second['obligation']['observation_id'], json.loads(self.state_bytes())['assignments'][self.child]['observations'])

    def f01_projection(self, action):
        self.fx.compact(); self.fx.register()
        reserved, observed, bound = self.bound_observation()
        self.fx.hook() if action == 'hook' else self.fx.pending('resume')
        evidence = self.actual_result(reserved, observed, bound)
        result = self.fx.pending('return', {'child_id': self.child, 'observation_id': observed['observation_id'], 'result_evidence': evidence})
        a = self.message('parent', '```json\n' + json.dumps(self.acceptance_value(reserved, observed, result)) + '\n```')
        joined = self.fx.pending('join', {'child_id': self.child, 'return_digest': result['return_digest'], 'acceptance': a})
        kind = 'UNRESOLVED_SIGNAL' if action == 'hook' else 'UNRESOLVED_RESUME_OBSERVATION'
        self.assertEqual([v['kind'] for v in joined['projected_pending']], [kind])
        state = json.loads(self.state_bytes())
        self.assertIsNone(state['observations'][joined['projected_pending'][0]['id']]['proof']['logical_occurrence_count'])
        self.assertFalse(joined['host_producer_authenticated'])
        self.fx.pending('reserve', {'child_id': 'uncorrelated-competing-child'}, ok=False)

    def test_f01_old_proof_cannot_swallow_later_hook_actual_chain(self):
        self.f01_projection('hook')

    def test_f01_old_proof_cannot_swallow_later_resume_actual_chain(self):
        self.f01_projection('resume')

    def test_rc08_rewritten_compaction_source_after_observation_refuses_join(self):
        self.fx.compact(); self.fx.register()
        reserved, observed, result, request = self.returned_chain()
        a = self.message('parent', '```json\n' + json.dumps(self.acceptance_value(reserved, observed, result)) + '\n```')
        raw = self.fx.transcript.read_bytes()
        self.fx.transcript.write_bytes(raw.replace(b'fixture summary', b'changed summary'))
        self.refused('join', {'child_id': self.child, 'return_digest': result['return_digest'], 'acceptance': a}, 'RETURN_SOURCE_CUTOFF_CHANGED')

    def test_rc13_rc20_wrong_actual_child_metadata_and_source_profile_refuse(self):
        # Shared parent session_id is present in both records and cannot replace child id.
        raw = self.logs['child'].read_bytes()
        for prior, replacement in [(b'"id":"child-a"', b'"id":"foreign"'),
                                   (b'"parent_thread_id":"source-session-a"', b'"parent_thread_id":"foreign-parent"'),
                                   (b'"cli_version":"0.153.4"', b'"cli_version":"unqualified"')]:
            with self.subTest(replacement=replacement):
                changed = raw.replace(prior, replacement)
                self.logs['child'].write_bytes(changed)
                row = json.loads(changed)
                locator = {**self.context['child']['metadata'], 'bytes':len(changed), 'sha256':hashlib.sha256(changed).hexdigest()}
                context = {**self.context, 'child': {**self.context['child'], 'metadata':locator}}
                self.refused('reserve', {'child_id':self.child, 'bounded_purpose':'Bounded finding.', 'observation_source':context})
        self.logs['child'].write_bytes(raw)

    def test_rc11_successive_compaction_old_actual_result_leaves_new_boundary(self):
        self.fx.compact(); self.fx.register(); self.fx.hook()
        reserved, observed, result, request = self.returned_chain()
        self.fx.compact('later-b'); self.fx.hook()
        a = self.message('parent', '```json\n' + json.dumps(self.acceptance_value(reserved, observed, result)) + '\n```')
        joined = self.fx.pending('join', {'child_id': self.child, 'return_digest': result['return_digest'], 'acceptance': a})
        self.assertEqual(len(joined['projected_pending']), 2)
        self.assertEqual(len([v for v in joined['projected_pending'] if v['kind'] == 'COMPLETED_RESUMED_BOUNDARY']), 1)
        self.assertEqual([v['version'] for v in joined['projected_pending'] if v['kind'] == 'UNRESOLVED_SIGNAL'], [2])

    def test_rc06_active_a_cannot_extend_into_scope_reserved_by_b(self):
        self.fx.compact(); self.fx.register()
        reserved, observed, bound = self.bound_observation()
        self.fx.compact('later-b'); self.fx.hook()
        b = self.fx.pending('reserve', {'child_id': 'child-b'})['assignment']['scope'][0]['id']
        prepared = self.fx.pending('observe-child', {'child_id': self.child, 'phase': 'prepare'})
        self.assertNotIn(b, [v['id'] for v in prepared['obligation']['covered_boundary_versions']])
        joined, request = self.accepted_chain(prepared)
        self.assertIn(b, [v['id'] for v in joined['projected_pending']])

    def test_rc12_later_proof_relates_uncertainty_without_mutating_failed_a(self):
        reserved, observed, result, request = self.returned_chain(status='FAILED')
        old = json.loads(self.state_bytes())
        self.fx.compact(); self.fx.register(); self.fx.pending('resume')
        current = json.loads(self.state_bytes())
        self.assertEqual(current['assignments'][self.child], old['assignments'][self.child])
        identifier = observed['scope'][0]['id']
        self.assertEqual(current['observations'][identifier]['consumed_version'], old['observations'][identifier]['consumed_version'])
        relation = current['source']['resume_observation_relations'][identifier]
        self.assertFalse(relation['retroactive_child_credit'])
        self.assertTrue(relation['later_proved_scope'])

    def test_rc15_status_and_concurrent_exact_logical_retry_are_nonmutating(self):
        joined, request = self.accepted_chain()
        before = self.state_bytes()
        self.fx.pending('status'); self.assertEqual(before, self.state_bytes())
        command = [sys.executable, '-I', '-S', '-B', str(ROOT / 'skills/implementaudit/scripts/compaction-audit-pending.py'),
            '--store', str(self.fx.store), '--session', self.fx.session, '--owner-id', 'host-owner', 'join']
        procs = [subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, cwd=self.fx.repo, env=self.fx.env) for _ in range(2)]
        for proc in procs:
            proc.stdin.write(json.dumps(request)); proc.stdin.close(); proc.stdin = None
        outputs = [proc.communicate(timeout=20) for proc in procs]
        self.assertEqual([p.returncode for p in procs], [0,0], outputs)
        self.assertEqual([json.loads(output[0]) for output in outputs], [joined,joined])
        self.assertEqual(before, self.state_bytes())

    def test_rc14_native_receipt_and_status_cannot_replace_actual_result(self):
        reserved, observed, bound = self.bound_observation()
        for witness in ({'native_receipt': 'fixture-native', 'status': 'SUCCEEDED'},
                        {'trusted': True}, {'epoch': 'VERIFIED'}, {'host_producer_authenticated': True}):
            self.refused('return', {'child_id': self.child, 'observation_id': observed['observation_id'],
                'result_evidence': witness}, 'ACTUAL_RESULT_EVIDENCE_SHAPE')


class PSCPolicyTests(unittest.TestCase):
    def setUp(self):
        self.chain = ProspectiveChainTests(); self.chain.setUp()

    def test_psc04_unconsumed_candidate_is_acquired_before_q_or_e(self):
        joined, request = self.chain.accepted_chain()
        acquisition = joined['acquisition']
        candidate = json.loads(Path(acquisition['candidate']['path']).read_bytes())
        self.assertEqual(candidate['exact_result_digest'], joined['return_digest'])
        self.assertFalse(candidate['host_producer_authenticated'])
        self.assertEqual(acquisition['status'], 'CANDIDATE_ACQUIRED_PENDING_QUALIFICATION')
        self.assertFalse(Path(acquisition['lookup']['Q']).exists())
        self.assertFalse(Path(acquisition['lookup']['E']).exists())
        self.assertFalse(joined['pending_consumed'])
        self.assertTrue(self.chain.fx.pending('status')['pending'])

    def put_json(self, path, value):
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        raw = (json.dumps(value, sort_keys=True) + '\n').encode()
        path.write_bytes(raw)
        return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

    def fixture_q(self, joined):
        acquisition = joined['acquisition']; candidate_pin = acquisition['candidate']
        candidate = json.loads(Path(candidate_pin['path']).read_bytes())
        q = {'policy_digest': acquisition['policy']['policy_digest'],
            'producer_environment_identity': candidate['producer_environment_identity'],
            'qualification_scope': {'profile_id': self.chain.adapter().PROFILE, 'candidate_consumption_required': False},
            'actual_acquisition_evidence': candidate_pin, 'authority_ceiling': 'NONE'}
        subject = {key: q[key] for key in ('policy_digest', 'producer_environment_identity',
                   'qualification_scope', 'actual_acquisition_evidence')}
        directory = Path(acquisition['lookup']['Q']).parent
        q['independent_review'] = self.put_json(directory / 'review.json',
            {'subject': subject, 'disposition': 'PASS', 'authority_ceiling': 'NONE'})
        q['ROOT_qualification_selection'] = self.put_json(directory / 'selection.json',
            {'subject': subject, 'disposition': 'SELECTED', 'authority_ceiling': 'NONE'})
        self.put_json(acquisition['lookup']['Q'], q)
        return q

    def fixture_e(self, joined):
        acquisition = joined['acquisition']
        self.put_json(acquisition['lookup']['E'], acquisition['episode_candidate'])

    def data_arrival(self):
        first, request = self.chain.accepted_chain()
        self.fixture_q(first)
        second = self.chain.fx.pending('join', request)
        self.fixture_e(second)
        third = self.chain.fx.pending('join', request)
        return first, second, third, request

    def test_psc02_q_e_arrival_preserves_policy_assignment_o_r_a_and_promotes_data_stage(self):
        first, request = self.chain.accepted_chain()
        before = json.loads(self.chain.state_bytes())['assignments'][self.chain.child]
        self.fixture_q(first)
        second = self.chain.fx.pending('join', request)
        self.assertTrue(second['profile']['qualification_record_bound'])
        self.assertFalse(Path(second['acquisition']['lookup']['E']).exists(), 'Q improperly depends on prior E/JOIN')
        self.fixture_e(second)
        third = self.chain.fx.pending('join', request)
        after = json.loads(self.chain.state_bytes())['assignments'][self.chain.child]
        for key in ('code', 'policy', 'prepared', 'return', 'accepted', 'logical_join'):
            self.assertEqual(before[key], after[key], key)
        self.assertEqual(len(after['admission_history']), 3)
        self.assertTrue(third['acquisition']['episode_record_bound'])
        self.assertIsNone(third['acquisition']['origin_validated'])
        self.assertEqual(third['status'], 'VERIFIED_LOGICAL_JOIN_PENDING_PROFILE')
        self.assertFalse(third['pending_consumed'])

    def test_psc01_global_q_and_same_format_foreign_episode_do_not_authenticate_b(self):
        first, second, third, request = self.data_arrival()
        old_episode = json.loads(Path(third['acquisition']['lookup']['E']).read_bytes())
        self.chain.fx.compact('new-b'); self.chain.fx.register()
        self.chain.start_other_child('child-b')
        b, b_request = self.chain.accepted_chain()
        self.assertTrue(b['profile']['qualification_record_bound'])
        self.assertFalse(b['host_producer_authenticated'])
        self.assertNotEqual(b['acquisition']['candidate'], third['acquisition']['candidate'])
        self.put_json(b['acquisition']['lookup']['E'], old_episode)
        self.chain.refused('join', b_request, 'EXACT_EPISODE_BINDING_DIFFERS')

    def test_psc03_changed_selector_still_fails_assignment_code_guard(self):
        first, request = self.chain.accepted_chain()
        state = json.loads(self.chain.state_bytes()); assignment = state['assignments'][self.chain.child]
        self.assertTrue(any(key.replace('\\', '/').endswith('/compaction-result-profile.py') for key in assignment['code']))
        mini = self.chain.fx.root / 'changed-source'
        for relative in [Path('skills') / key for key in assignment['code']] + [Path('skills/implementaudit/scripts/host-session-binding.py')]:
            destination = mini / relative; destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / relative).read_bytes())
        selector = mini / 'skills/implementaudit/scripts/compaction-result-profile.py'
        selector.write_bytes(selector.read_bytes() + b'\n# different executable policy selection\n')
        command = [sys.executable, '-I', '-S', '-B', str(mini/'skills/implementaudit/scripts/compaction-audit-pending.py'),
            '--store', str(self.chain.fx.store), '--session', self.chain.fx.session, '--owner-id', 'host-owner', 'join']
        before = self.chain.state_bytes()
        result = subprocess.run(command, input=json.dumps(request), text=True, capture_output=True,
            cwd=self.chain.fx.repo, env=self.chain.fx.env, timeout=20)
        self.assertEqual(result.returncode, 2, result.stdout+result.stderr)
        self.assertIn('CHILD_OR_SOURCE_CHANGED', result.stdout)
        self.assertEqual(before, self.chain.state_bytes())

    def test_psc05_pass_labels_caller_owner_flags_and_arbitrary_paths_never_authenticate(self):
        joined, request = self.chain.accepted_chain()
        q = self.fixture_q(joined)
        bound = self.chain.fx.pending('join', request)
        self.assertTrue(bound['profile']['qualification_record_bound'])
        self.assertIsNone(bound['profile']['policy_qualified'])
        self.assertFalse(bound['host_producer_authenticated'])
        self.put_json(joined['acquisition']['lookup']['Q'], {**q, 'owner': True})
        self.chain.refused('join', request, 'POLICY_QUALIFICATION_FIELDS')
        self.chain.refused('join', {**request, 'Q_path': 'foreign'}, 'JOIN_SHAPE')
        self.chain.refused('join', {**request, 'native_receipt': 'fixture'}, 'JOIN_SHAPE')

    def test_psc06_exact_episode_all_tuple_substitutions_refused(self):
        first, request = self.chain.accepted_chain(); self.fixture_q(first)
        second = self.chain.fx.pending('join', request)
        original = second['acquisition']['episode_candidate']
        for field in original:
            with self.subTest(field=field):
                self.put_json(second['acquisition']['lookup']['E'], {**original, field: 'foreign'})
                self.chain.refused('join', request, 'EXACT_EPISODE_BINDING_DIFFERS')

    def test_psc07_data_retry_idempotent_and_interrupted_arrival_cannot_partly_consume(self):
        first, request = self.chain.accepted_chain(); self.fixture_q(first)
        path = ROOT / 'skills/implementaudit/scripts/compaction-audit-pending.py'
        spec = importlib.util.spec_from_file_location('psc_interrupted_owner', path)
        owner = importlib.util.module_from_spec(spec); spec.loader.exec_module(owner)
        before = self.chain.state_bytes()
        with mock.patch.dict(os.environ, self.chain.fx.env, clear=True), mock.patch.object(owner.CORE.os, 'replace', side_effect=OSError('PSC interrupted arrival')):
            with self.assertRaisesRegex(OSError, 'PSC interrupted'):
                owner.operate(self.chain.fx.store, self.chain.fx.session, 'host-owner', 'join', request)
        self.assertEqual(before, self.chain.state_bytes())
        second = self.chain.fx.pending('join', request); self.fixture_e(second)
        third = self.chain.fx.pending('join', request); before = self.chain.state_bytes()
        self.assertEqual(self.chain.fx.pending('join', request), third)
        self.assertEqual(before, self.chain.state_bytes())
        changed = {**third['acquisition']['episode_candidate'], 'exact_result_digest': '0'*64}
        self.put_json(third['acquisition']['lookup']['E'], changed)
        self.chain.refused('join', request, 'EXACT_EPISODE_BINDING_DIFFERS')

    def test_psc08_failed_a_and_later_uncovered_version_survive_b_data_promotion(self):
        self.chain.returned_chain(status='FAILED')
        old_a = json.loads(self.chain.state_bytes())['assignments']['child-a']
        self.chain.fx.compact('b'); self.chain.fx.register()
        self.chain.start_other_child('child-b')
        first, request = self.chain.accepted_chain(); self.fixture_q(first)
        second = self.chain.fx.pending('join', request)
        self.chain.fx.pending('resume')
        self.fixture_e(second)
        third = self.chain.fx.pending('join', request)
        self.assertTrue(third['projected_pending'])
        self.assertEqual([v['version'] for v in third['projected_pending'] if v['kind']=='UNRESOLVED_RESUME_OBSERVATION'], [2])
        self.assertEqual(json.loads(self.chain.state_bytes())['assignments']['child-a'], old_a)
        self.assertTrue(self.chain.fx.pending('status')['state_dependent_decisions_held'])

    def test_psc09_missing_qualification_epoch_and_currentness_do_not_suppress_audit(self):
        decision = self.chain.fx.pending('resume', {'currentness': 'UNRESOLVED', 'measured_epoch': 'UNRESOLVED'})
        self.assertEqual(decision['decision'], 'AUDIT_STATE_REQUIRED')
        first, request = self.chain.accepted_chain()
        self.assertEqual(first['authority'], 'NONE')
        self.assertFalse(first['canonical_currentness'])
        self.assertFalse(first['pending_consumed'])
        self.assertTrue(self.chain.fx.pending('status')['audit_state_required'])

    def test_psc10_real_entrypoint_cold_evidence_cannot_select_absent_origin_validator(self):
        first, second, third, request = self.data_arrival()
        self.assertEqual(third['acquisition']['status'], 'EPISODE_BOUND_PENDING_ORIGIN_VALIDATOR')
        self.assertIsNone(third['acquisition']['origin_validated'])
        self.assertIn('not implemented or qualified', third['acquisition']['unresolved_implementation_edge'])
        self.assertFalse(third['host_producer_authenticated'])
        self.assertFalse(third['pending_consumed'])
        self.assertTrue(self.chain.fx.pending('status')['pending'])


class PriorObservationHistoryTests(unittest.TestCase):
    def setUp(self):
        self.chain = ProspectiveChainTests(); self.chain.setUp()

    def state(self):
        return json.loads(self.chain.state_bytes())

    def assignment(self):
        return self.state()['assignments'][self.chain.child]

    def clone(self, value):
        return json.loads(json.dumps(value))

    def save_assignment(self, change):
        path = next(self.chain.fx.store.rglob('pending.json'))
        state = json.loads(path.read_bytes())
        change(state['assignments'][self.chain.child])
        path.write_text(json.dumps(state), encoding='utf-8')

    def next_reserved(self):
        self.chain.fx.pending('resume')
        return self.chain.fx.pending('observe-child', {'child_id': self.chain.child, 'phase': 'prepare'})

    def pending_bind(self, reserved, preface=None):
        evidence = self.chain.authorization(reserved); adapter = self.chain.adapter()
        identifier = reserved['obligation']['observation_id']
        deliver = {'child_id': self.chain.child, 'phase': 'deliver', 'observation_id': identifier,
                   'authorization_evidence': evidence}
        packet = self.chain.fx.pending('observe-child', deliver)
        call, result = self.chain.exchange('child', 'pending-delivery',
            adapter.delivery_tool_input(self.chain.fx.store, self.chain.fx.session, 'host-owner', deliver), json.dumps(packet))
        bind = {'child_id': self.chain.child, 'phase': 'bind', 'observation_id': identifier,
                'exchange': {'call': call, 'result': result}}
        if preface:
            preface(bind)
        original = self.chain.row('child', 'response_item', {'type': 'custom_tool_call', 'name': 'exec',
            'call_id': 'pending-bind', 'status': 'completed',
            'input': adapter.delivery_tool_input(self.chain.fx.store, self.chain.fx.session, 'host-owner', bind)})
        return {'reserved': reserved, 'bind': bind, 'original': original}

    def direct(self, pending, candidates, context_change=None):
        assignment = self.assignment(); prepared = assignment['prepared'][pending['bind']['observation_id']]
        context = assignment['observation_source']
        if context_change:
            context_change(context)
        adapter = self.chain.adapter()
        with mock.patch.dict(os.environ, self.chain.fx.env, clear=True):
            exchange = adapter.completed_exchange(context, prepared, pending['bind']['exchange'],
                self.chain.fx.store, self.chain.fx.session, 'host-owner', prepared['authorization']['value']['skill_source_pin'])
            return adapter.hold_history(context, prepared, exchange, pending['bind'], self.chain.fx.store,
                                        self.chain.fx.session, 'host-owner', prior_context=candidates)

    def prior_and_pending(self):
        first = self.chain.bound_observation()
        pending = self.pending_bind(self.next_reserved())
        prior_id = first[0]['obligation']['observation_id']
        return first, pending, {prior_id: self.assignment()['prepared'][prior_id]}

    def finish_pending(self, pending):
        observed = self.chain.fx.pending('observe-child', pending['bind'])
        result = self.chain.row('child', 'response_item', {'type': 'custom_tool_call_output', 'call_id': 'pending-bind',
            'output': [{'type': 'input_text', 'text': 'Script completed\nOutput:\n'},
                       {'type': 'input_text', 'text': json.dumps({'chunk_id': 'pending-bind', 'wall_time_seconds': 0.1,
                        'exit_code': 0, 'original_token_count': 100, 'output': json.dumps(observed)})}]})
        return observed, {'call': pending['original'], 'result': result}

    def return_join(self, reserved, observed, bound):
        evidence = self.chain.actual_result(reserved, observed, bound)
        result = self.chain.fx.pending('return', {'child_id': self.chain.child,
            'observation_id': observed['observation_id'], 'result_evidence': evidence})
        acceptance = self.chain.message('parent', '```json\n' + json.dumps(self.chain.acceptance_value(reserved, observed, result)) + '\n```')
        request = {'child_id': self.chain.child, 'return_digest': result['return_digest'], 'acceptance': acceptance}
        joined = self.chain.fx.pending('join', request)
        self.assertEqual(joined['authority'], 'NONE'); self.assertFalse(joined['canonical_currentness'])
        self.assertFalse(joined['host_producer_authenticated']); self.assertFalse(joined['pending_consumed'])
        return result, request

    def test_ph01_zero_prior_current_exchange_keeps_original_cutoff(self):
        reserved, observed, bound = self.chain.bound_observation()
        prepared = self.assignment()['prepared'][observed['observation_id']]
        original_entry = self.clone(prepared['hold_prefix'])
        reply = self.chain.fx.pending('observe-child', prepared['bind_request'])
        self.assertEqual(reply, observed)
        self.assertEqual(self.assignment()['prepared'][observed['observation_id']]['hold_prefix'], original_entry)
        result, _ = self.return_join(reserved, observed, bound)
        self.assertEqual(result['identity']['hold_history']['prefix_bytes'], bound['result']['offset'] + bound['result']['bytes'])

    def test_ph02_one_prior_completes_bind_retry_return_and_join(self):
        first, pending, candidates = self.prior_and_pending()
        self.assertIsNone(self.assignment()['return'])
        old_entry = self.clone(next(iter(candidates.values()))['hold_prefix'])
        observed, bound = self.finish_pending(pending)
        self.assertEqual(self.chain.fx.pending('observe-child', pending['bind']), observed)
        result, request = self.return_join(pending['reserved'], observed, bound)
        self.assertEqual(result['identity']['hold_history']['original_bind']['call']['locator'], bound['call'])
        self.assertEqual(self.assignment()['prepared'][first[0]['obligation']['observation_id']]['hold_prefix'], old_entry)
        self.chain.fx.pending('join', request)

    def test_ph03_two_prior_observations_validate_transitively(self):
        first = self.chain.bound_observation()
        second = self.chain.bound_observation(self.next_reserved())
        third = self.chain.bound_observation(self.next_reserved())
        result, _ = self.return_join(*third)
        self.assertEqual(len(self.assignment()['observations']), 3)
        self.assertEqual(result['observation_id'], third[1]['observation_id'])
        self.assertNotEqual(first[1]['observation_id'], second[1]['observation_id'])
        self.assertGreater(result['identity']['hold_history']['physical_records'], 12)

    def test_ph04_prior_shape_scope_identity_and_authority_mutations_refuse(self):
        first, pending, good = self.prior_and_pending(); key = next(iter(good))
        self.direct(pending, good)
        def child(value): value[key]['obligation']['actual_child_identity']['thread_id'] = 'foreign-child'
        def parent(value): value[key]['obligation']['parent_identity']['thread_id'] = 'foreign-parent'
        def code(value): value[key]['observation']['code'] = {'foreign': 'f' * 64}
        def scope(value): value[key]['obligation']['covered_boundary_versions'] = []
        def selected(value): value[key]['obligation']['selected_child'] = 'audit-assess'
        def authority(value): value[key]['obligation']['authority_ceiling'] = 'ROOT'
        def response(value): value[key]['bound_response']['authority'] = 'ROOT'
        def flags(value): value[key].clear(); value[key]['completed'] = True
        def namespace(value): value[key]['obligation_pin']['path'] = str(self.chain.fx.root / 'foreign.json')
        def role(value): value[key]['authorization']['load_identity']['call']['role'] = 'parent'
        for label, change, reason in (
            ('foreign-child', child, 'HOLD_PRIOR_OBLIGATION_BINDING'), ('foreign-parent', parent, 'HOLD_PRIOR_OBLIGATION_BINDING'),
            ('foreign-code', code, 'HOLD_PRIOR_OBLIGATION_BINDING'), ('foreign-scope', scope, 'HOLD_PRIOR_OBLIGATION_BINDING'),
            ('wrong-selected', selected, 'HOLD_PRIOR_OBLIGATION_BINDING'), ('authority', authority, 'HOLD_PRIOR_OBLIGATION_BINDING'),
            ('saved-response', response, 'HOLD_PRIOR_BOUND_RESPONSE_FIELDS'), ('flag-only', flags, 'HOLD_PRIOR_PREPARED_SHAPE'),
            ('namespace', namespace, 'HOLD_PRIOR_OBLIGATION_NAMESPACE'), ('role', role, 'HOLD_PRIOR_PUBLIC_AUTHORIZATION_CHANGED')):
            with self.subTest(label=label):
                bad = self.clone(good); change(bad)
                with self.assertRaisesRegex(ValueError, reason): self.direct(pending, bad)

    def test_ph05_self_cycle_duplicate_and_bound_context_refuse(self):
        _, pending, good = self.prior_and_pending(); key = next(iter(good))
        current_id = pending['bind']['observation_id']
        bad = self.clone(good); bad[current_id] = self.assignment()['prepared'][current_id]
        with self.assertRaisesRegex(ValueError, 'HOLD_PRIOR_OBSERVATION_ID'): self.direct(pending, bad)
        bad = self.clone(good); bad['f' * 64] = bad[key]
        with self.assertRaisesRegex(ValueError, 'HOLD_PRIOR_OBLIGATION_BINDING'): self.direct(pending, bad)
        bad = self.clone(good); bad[key]['cycle'] = bad
        with self.assertRaises(ValueError): self.direct(pending, bad)
        bad = {f'{index:064x}': good[key] for index in range(65)}
        with self.assertRaisesRegex(ValueError, 'HOLD_PRIOR_CONTEXT_BOUND'): self.direct(pending, bad)
        bad = self.clone(good); bad[key]['observation']['source_problem'] = 'x' * (2 * 1024 * 1024)
        with self.assertRaisesRegex(ValueError, 'HOLD_PRIOR_CONTEXT_BOUND'): self.direct(pending, bad)

    def test_ph06_real_future_observation_cannot_classify_an_earlier_hold(self):
        first = self.chain.bound_observation(); second = self.chain.bound_observation(self.next_reserved())
        state = self.assignment(); a = state['prepared'][first[1]['observation_id']]; b = state['prepared'][second[1]['observation_id']]
        adapter = self.chain.adapter()
        with mock.patch.dict(os.environ, self.chain.fx.env, clear=True), self.assertRaisesRegex(ValueError, 'HOLD_PRIOR_OBSERVATION_ORDER'):
            adapter.hold_history(state['observation_source'], a, a['exchange'], a['bind_request'], self.chain.fx.store,
                self.chain.fx.session, 'host-owner', prior_context={second[1]['observation_id']: b})

    def test_ph07_same_child_history_activation_and_range_are_not_advanced(self):
        _, pending, good = self.prior_and_pending()
        with self.assertRaises(ValueError):
            self.direct(pending, good, lambda ctx: ctx['child'].update(history_start_ordinal=ctx['child']['history_start_ordinal'] + 1))
        with self.assertRaises(ValueError):
            self.direct(pending, good, lambda ctx: ctx['child'].update(allowed_ranges=[{'offset': 1, 'bytes': 2097151}]))
        with self.assertRaises(ValueError):
            self.direct(pending, good, lambda ctx: ctx['child']['physical'].update(inode=ctx['child']['physical']['inode'] + 1))

    def test_ph08_prior_saved_reply_without_first_host_completion_refuses(self):
        first = self.chain.bound_observation(); path = self.chain.logs['child']
        path.write_bytes(path.read_bytes()[:first[2]['result']['offset']])
        self.chain.lines['child'] -= 1; self.chain.ordinals['child'] -= 1
        pending = self.pending_bind(self.next_reserved())
        prior_id = first[1]['observation_id']; good = {prior_id: self.assignment()['prepared'][prior_id]}
        self.assertIsNotNone(good[prior_id]['bound_response'])
        with self.assertRaisesRegex(ValueError, 'HOLD_PRIOR_ORIGINAL_COMPLETION_UNPROVED'):
            self.direct(pending, good)

    def test_ph09_changed_original_response_is_not_repaired_by_saved_reply(self):
        first = self.chain.bound_observation(); path = self.chain.logs['child']; locator = first[2]['result']
        raw = path.read_bytes(); record = json.loads(raw[locator['offset']:locator['offset'] + locator['bytes']])
        nested = json.loads(record['payload']['output'][1]['text']); nested['exit_code'] = 1
        record['payload']['output'][1]['text'] = json.dumps(nested)
        wire = (json.dumps(record, separators=(',', ':')) + '\n').encode()
        path.write_bytes(raw[:locator['offset']] + wire)
        pending = self.pending_bind(self.next_reserved()); key = first[1]['observation_id']
        with self.assertRaisesRegex(ValueError, 'HOLD_PRIOR_OBSERVATION_REFUSED:FULL_SUCCESSFUL_HOST_RESPONSE_REQUIRED'):
            self.direct(pending, {key: self.assignment()['prepared'][key]})

    def test_ph10_later_duplicate_original_cannot_move_the_entry(self):
        first = self.chain.bound_observation(); key = first[1]['observation_id']; prior = self.assignment()['prepared'][key]
        adapter = self.chain.adapter()
        self.chain.row('child', 'response_item', {'type': 'custom_tool_call', 'name': 'exec', 'status': 'completed', 'call_id': 'duplicate-original',
            'input': adapter.delivery_tool_input(self.chain.fx.store, self.chain.fx.session, 'host-owner', prior['bind_request'])})
        raw = self.chain.logs['child'].read_bytes(); prior['hold_prefix'].update(prefix_bytes=len(raw), prefix_sha256=hashlib.sha256(raw).hexdigest(), physical_records=len(raw.splitlines()))
        pending = self.pending_bind(self.next_reserved())
        with self.assertRaisesRegex(ValueError, 'HOLD_ORIGINAL_BIND_CALL_UNPROVED'):
            self.direct(pending, {key: prior})

    def test_ph11_exact_historical_retry_has_its_own_pair_and_unchanged_original(self):
        first = self.chain.bound_observation(); key = first[1]['observation_id']; prior = self.assignment()['prepared'][key]
        adapter = self.chain.adapter(); request = prior['bind_request']
        call = self.chain.row('child', 'response_item', {'type': 'custom_tool_call', 'name': 'exec', 'status': 'completed', 'call_id': 'historical-retry',
            'input': adapter.delivery_tool_input(self.chain.fx.store, self.chain.fx.session, 'host-owner', request)})
        reply = self.chain.fx.pending('observe-child', request)
        self.assertEqual(reply, first[1])
        self.chain.row('child', 'response_item', {'type': 'custom_tool_call_output', 'call_id': 'historical-retry', 'output': [
            {'type': 'input_text', 'text': 'Script completed\nOutput:\n'}, {'type': 'input_text', 'text': json.dumps({
                'chunk_id': 'historical-retry', 'wall_time_seconds': .1, 'exit_code': 0, 'original_token_count': 100, 'output': json.dumps(reply)})}]})
        second = self.chain.bound_observation(self.next_reserved())
        self.return_join(*second)
        self.assertEqual(self.assignment()['prepared'][key]['hold_prefix'], prior['hold_prefix'])

    def test_ph12_unproved_extra_occurrence_and_unknown_traffic_refuse(self):
        first = self.chain.bound_observation(); prior = self.assignment()['prepared'][first[1]['observation_id']]
        adapter = self.chain.adapter()
        self.chain.exchange('child', 'copied-unproved-delivery', adapter.delivery_tool_input(
            self.chain.fx.store, self.chain.fx.session, 'host-owner', prior['delivery_request']), '{}')
        pending = self.pending_bind(self.next_reserved())
        refused = self.chain.fx.pending('observe-child', pending['bind'], ok=False)
        self.assertIn('HOLD_UNCLASSIFIED_TOOL_CALL', refused.stdout)
        self.assertTrue(self.assignment()['hold_refusals'])

    def test_ph13_incomplete_historical_retry_cannot_borrow_original_reply(self):
        first = self.chain.bound_observation(); prior = self.assignment()['prepared'][first[1]['observation_id']]
        adapter = self.chain.adapter()
        self.chain.row('child', 'response_item', {'type': 'custom_tool_call', 'name': 'exec', 'status': 'completed', 'call_id': 'unfinished-retry',
            'input': adapter.delivery_tool_input(self.chain.fx.store, self.chain.fx.session, 'host-owner', prior['bind_request'])})
        pending = self.pending_bind(self.next_reserved())
        with self.assertRaisesRegex(ValueError, 'HOLD_PRIOR_RETRY_COMPLETION_UNPROVED'):
            self.direct(pending, {first[1]['observation_id']: prior})

    def test_ph14_saved_prior_failure_and_refusal_veto_bind_retry_and_return(self):
        first, pending, candidates = self.prior_and_pending(); old_id = first[1]['observation_id']
        observed, bound = self.finish_pending(pending)
        evidence = self.chain.actual_result(pending['reserved'], observed, bound)
        for bucket, reason in (('hold_failures', 'HOLD_PRIOR_EPISODE_PREVIOUSLY_DISQUALIFIED'),
                               ('hold_refusals', 'HOLD_PRIOR_EPISODE_PREVIOUSLY_REFUSED')):
            with self.subTest(bucket=bucket):
                saved = self.state()
                self.save_assignment(lambda a: a.setdefault(bucket, {}).update({old_id: {'reason': 'retained original failure'}}))
                before = self.chain.state_bytes()
                for action, request in (('observe-child', pending['bind']), ('return', {'child_id': self.chain.child,
                    'observation_id': observed['observation_id'], 'result_evidence': evidence})):
                    result = self.chain.fx.pending(action, request, ok=False)
                    self.assertIn(reason, result.stdout); self.assertEqual(self.chain.state_bytes(), before)
                next(self.chain.fx.store.rglob('pending.json')).write_text(json.dumps(saved), encoding='utf-8')

    def test_ph15_saved_prior_failure_vetoes_join_without_consumption(self):
        first = self.chain.bound_observation(); second = self.chain.bound_observation(self.next_reserved())
        result, request = self.return_join(*second); old_id = first[1]['observation_id']
        self.save_assignment(lambda a: a.setdefault('hold_refusals', {}).update({old_id: {'reason': 'retained refusal'}}))
        before = self.chain.state_bytes()
        rejected = self.chain.fx.pending('join', request, ok=False)
        self.assertIn('HOLD_PRIOR_EPISODE_PREVIOUSLY_REFUSED', rejected.stdout)
        self.assertEqual(before, self.chain.state_bytes())
        self.assertFalse(self.chain.fx.pending('status')['canonical_currentness'])

    def test_ph16_prior_completion_does_not_supply_current_completion(self):
        first, pending, candidates = self.prior_and_pending()
        observed = self.chain.fx.pending('observe-child', pending['bind'])
        prepared = self.assignment()['prepared'][observed['observation_id']]
        adapter = self.chain.adapter()
        with mock.patch.dict(os.environ, self.chain.fx.env, clear=True), self.assertRaises(ValueError):
            adapter.hold_history(self.assignment()['observation_source'], prepared, prepared['exchange'], pending['bind'],
                self.chain.fx.store, self.chain.fx.session, 'host-owner', prior_context=candidates)

    def neutralize(self, locator):
        path = self.chain.logs['child']; raw = path.read_bytes()
        record = json.loads(raw[locator['offset']:locator['offset'] + locator['bytes']])
        record['payload'] = {'type': 'message'}
        wire = json.dumps(record, separators=(',', ':')).encode()
        self.assertLess(len(wire), locator['bytes'])
        wire += b' ' * (locator['bytes'] - len(wire) - 1) + b'\n'
        path.write_bytes(raw[:locator['offset']] + wire + raw[locator['offset'] + locator['bytes']:])

    def bound_with_gap(self, kind):
        original = self.chain.row; inserted = []; done = [False]
        def row(role, outer, payload):
            if role == 'child' and payload.get('type') == 'custom_tool_call_output' and payload.get('call_id') == 'bind-a' and not done[0]:
                done[0] = True
                observed = json.loads(json.loads(payload['output'][1]['text'])['output'])
                command = ('// COMPACTION_OBSERVATION_EXCHANGE=' + observed['child_observation_exchange_identity'] + '\ntext("Early prior work");'
                           if kind == 'early' else 'text("Unclassified prior work");')
                inserted.extend(self.chain.exchange('child', 'prior-gap', command, 'Synthetic gap output'))
            return original(role, outer, payload)
        self.chain.row = row
        try:
            first = self.chain.bound_observation()
        finally:
            self.chain.row = original
        self.assertEqual(len(inserted), 2)
        return first, inserted

    def test_ph17_current_early_use_precedes_exemptions_and_stays_latched(self):
        first, pending, candidates = self.prior_and_pending()
        observed = self.chain.fx.pending('observe-child', pending['bind'])
        early = self.chain.exchange('child', 'current-early', '// COMPACTION_OBSERVATION_EXCHANGE=' +
            observed['child_observation_exchange_identity'] + '\ntext("Early current work");', 'Early output')
        result = self.chain.row('child', 'response_item', {'type': 'custom_tool_call_output', 'call_id': 'pending-bind', 'output': [
            {'type': 'input_text', 'text': 'Script completed\nOutput:\n'}, {'type': 'input_text', 'text': json.dumps({
                'chunk_id': 'pending-bind', 'wall_time_seconds': .1, 'exit_code': 0, 'original_token_count': 100, 'output': json.dumps(observed)})}]})
        refused = self.chain.fx.pending('observe-child', pending['bind'], ok=False)
        self.assertIn('HOLD_EARLY_SAME_EPISODE_USE', refused.stdout)
        saved = self.clone(self.assignment()['hold_failures'])
        for locator in early: self.neutralize(locator)
        retry = self.chain.fx.pending('observe-child', pending['bind'], ok=False)
        self.assertIn('HOLD_EPISODE_PREVIOUSLY_DISQUALIFIED', retry.stdout)
        evidence = self.chain.actual_result(pending['reserved'], observed, {'call': pending['original'], 'result': result})
        returned = self.chain.fx.pending('return', {'child_id': self.chain.child, 'observation_id': observed['observation_id'], 'result_evidence': evidence}, ok=False)
        self.assertIn('HOLD_EPISODE_PREVIOUSLY_DISQUALIFIED', returned.stdout)
        self.assertEqual(self.assignment()['hold_failures'], saved)

    def test_ph18_prior_early_use_is_revalidated_under_its_own_identity(self):
        first, gap = self.bound_with_gap('early')
        pending = self.pending_bind(self.next_reserved())
        refused = self.chain.fx.pending('observe-child', pending['bind'], ok=False)
        self.assertIn('HOLD_PRIOR_OBSERVATION_REFUSED:HOLD_EARLY_SAME_EPISODE_USE', refused.stdout)
        saved = self.clone(self.assignment()['hold_refusals'])
        for locator in gap: self.neutralize(locator)
        retry = self.chain.fx.pending('observe-child', pending['bind'], ok=False)
        self.assertIn('HOLD_EPISODE_PREVIOUSLY_REFUSED', retry.stdout)
        self.assertEqual(self.assignment()['hold_refusals'], saved)

    def test_ph19_unclassified_prior_gap_is_not_covered_by_a_valid_original(self):
        first, gap = self.bound_with_gap('unknown')
        pending = self.pending_bind(self.next_reserved())
        refused = self.chain.fx.pending('observe-child', pending['bind'], ok=False)
        self.assertIn('HOLD_PRIOR_OBSERVATION_REFUSED:HOLD_UNCLASSIFIED_TOOL_CALL', refused.stdout)
        saved = self.clone(self.assignment()['hold_refusals'])
        for locator in gap: self.neutralize(locator)
        retry = self.chain.fx.pending('observe-child', pending['bind'], ok=False)
        self.assertIn('HOLD_EPISODE_PREVIOUSLY_REFUSED', retry.stdout)
        self.assertEqual(self.assignment()['hold_refusals'], saved)

    def test_ph20_unpaired_output_and_time_disorder_remain_visible(self):
        self.chain.bound_observation()
        self.chain.row('child', 'response_item', {'type': 'custom_tool_call_output', 'call_id': 'unpaired-extra', 'output': []})
        pending = self.pending_bind(self.next_reserved())
        result = self.chain.fx.pending('observe-child', pending['bind'], ok=False)
        self.assertIn('HOLD_UNPAIRED_TOOL_OUTPUT', result.stdout)
        self.assertTrue(self.assignment()['hold_refusals'])

    def test_ph21_full_history_time_order_is_not_skipped_for_prior_context(self):
        self.chain.bound_observation()
        clock = self.chain.tick; self.chain.tick -= 10
        self.chain.message('child', 'A backwards-timestamp boundary')
        self.chain.tick = clock + 1
        pending = self.pending_bind(self.next_reserved())
        result = self.chain.fx.pending('observe-child', pending['bind'], ok=False)
        self.assertIn('HOLD_EVENT_ORDER', result.stdout)
        self.assertTrue(self.assignment()['hold_refusals'])

    def test_ph22_prior_obligation_bytes_skill_and_activation_claims_refuse(self):
        first, pending, good = self.prior_and_pending(); key = next(iter(good))
        bad = self.clone(good); bad[key]['authorization']['value']['skill_source_pin']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'HOLD_PRIOR_PUBLIC_AUTHORIZATION_CHANGED'):
            self.direct(pending, bad)
        bad = self.clone(good)
        bad[key]['authorization']['evidence']['load_call'] = self.assignment()['observation_source']['child']['metadata']
        bad[key]['delivery_request']['authorization_evidence'] = bad[key]['authorization']['evidence']
        with self.assertRaises(ValueError): self.direct(pending, bad)
        path = Path(good[key]['obligation_pin']['path']); raw = path.read_bytes()
        path.write_bytes(raw + b' ')
        with self.assertRaisesRegex(ValueError, 'ARTIFACT_BYTE_COUNT'):
            self.direct(pending, good)

    def test_ph23_saved_failed_prior_without_completed_flag_still_vetoes(self):
        first, pending, good = self.prior_and_pending(); old_id = first[1]['observation_id']
        path = ROOT / 'skills/implementaudit/scripts/compaction-audit-pending.py'
        spec = importlib.util.spec_from_file_location('prior_context_owner', path)
        owner = importlib.util.module_from_spec(spec); spec.loader.exec_module(owner)
        for bucket, reason in (('hold_failures', 'HOLD_PRIOR_EPISODE_PREVIOUSLY_DISQUALIFIED'),
                               ('hold_refusals', 'HOLD_PRIOR_EPISODE_PREVIOUSLY_REFUSED')):
            with self.subTest(bucket=bucket):
                assignment = self.assignment(); assignment['observations'].pop(old_id)
                assignment.setdefault(bucket, {})[old_id] = {'reason': 'retained failed initial observation'}
                with self.assertRaisesRegex(ValueError, reason):
                    owner.prior_history_context(assignment, pending['bind']['observation_id'])

    def bad_prior_retry_preface(self, prior, include_early, emitted):
        def preface(bind):
            adapter = self.chain.adapter()
            if include_early:
                assignment = self.assignment(); prepared = assignment['prepared'][bind['observation_id']]
                exchange = adapter.completed_exchange(assignment['observation_source'], prepared, bind['exchange'],
                    self.chain.fx.store, self.chain.fx.session, 'host-owner', prepared['authorization']['value']['skill_source_pin'])
                self.chain.exchange('child', 'early-before-prior-retry', '// COMPACTION_OBSERVATION_EXCHANGE=' +
                    exchange['identity'] + '\ntext("Current early USE");', 'Early output')
            reply = self.clone(prior['bound_response']); reply['authority'] = 'ROOT'
            emitted.extend(self.chain.exchange('child', 'bad-prior-retry', adapter.delivery_tool_input(
                self.chain.fx.store, self.chain.fx.session, 'host-owner', prior['bind_request']), json.dumps(reply)))
        return preface

    def test_ph24_current_early_use_is_detected_before_later_prior_retry_classification(self):
        first = self.chain.bound_observation(); prior = self.assignment()['prepared'][first[1]['observation_id']]
        pending = self.pending_bind(self.next_reserved(), self.bad_prior_retry_preface(prior, True, []))
        result = self.chain.fx.pending('observe-child', pending['bind'], ok=False)
        self.assertIn('HOLD_EARLY_SAME_EPISODE_USE', result.stdout)
        self.assertTrue(self.assignment()['hold_failures'])

    def test_ph25_bad_successful_prior_retry_is_a_persistent_material_refusal(self):
        first = self.chain.bound_observation(); prior = self.assignment()['prepared'][first[1]['observation_id']]
        emitted = []; pending = self.pending_bind(self.next_reserved(), self.bad_prior_retry_preface(prior, False, emitted))
        result = self.chain.fx.pending('observe-child', pending['bind'], ok=False)
        self.assertIn('HOLD_PRIOR_RETRY_RESPONSE_DIFFERS', result.stdout)
        saved = self.clone(self.assignment().get('hold_refusals', {})); self.assertTrue(saved)
        for locator in emitted: self.neutralize(locator)
        retry = self.chain.fx.pending('observe-child', pending['bind'], ok=False)
        self.assertIn('HOLD_EPISODE_PREVIOUSLY_REFUSED', retry.stdout)
        self.assertEqual(self.assignment()['hold_refusals'], saved)

    def test_ph26_entry_cannot_be_resealed_after_original_response(self):
        first = self.chain.bound_observation(); key = first[1]['observation_id']; prior = self.assignment()['prepared'][key]
        raw = self.chain.logs['child'].read_bytes()
        prior['hold_prefix'].update(prefix_bytes=len(raw), prefix_sha256=hashlib.sha256(raw).hexdigest(), physical_records=len(raw.splitlines()))
        pending = self.pending_bind(self.next_reserved())
        with self.assertRaisesRegex(ValueError, 'HOLD_ORIGINAL_BIND_NOT_PENDING_AT_ENTRY'):
            self.direct(pending, {key: prior})

    def test_ph27_saved_refusal_cannot_be_relabelled_as_future_by_revision_only(self):
        first, pending, good = self.prior_and_pending(); old_id = first[1]['observation_id']
        path = ROOT / 'skills/implementaudit/scripts/compaction-audit-pending.py'
        spec = importlib.util.spec_from_file_location('refusal_scope_owner', path)
        owner = importlib.util.module_from_spec(spec); spec.loader.exec_module(owner)
        assignment = self.assignment(); assignment['observations'].pop(old_id)
        assignment.setdefault('hold_failures', {})[old_id] = {'reason': 'retained old refusal'}
        assignment['prepared'][old_id]['observation']['revision'] = assignment['prepared'][pending['bind']['observation_id']]['observation']['revision'] + 1
        with self.assertRaisesRegex(ValueError, 'HOLD_PRIOR_REFUSAL_SCOPE_UNKNOWN'):
            owner.prior_history_context(assignment, pending['bind']['observation_id'])


class CurrentMechanicalOccurrenceTests(unittest.TestCase):
    """Same command/body at another physical occurrence is not selected proof."""
    def fixture(self):
        fixture = PriorObservationHistoryTests(); fixture.setUp()
        return fixture

    def payload(self, fixture, locator):
        raw = fixture.chain.logs['child'].read_bytes()
        return json.loads(raw[locator['offset']:locator['offset'] + locator['bytes']])['payload']

    def copied_pair(self, fixture, pair, identifier, shape):
        chain = fixture.chain
        call = self.payload(fixture, pair['call']); output = self.payload(fixture, pair['result'])
        call['call_id'] = identifier; output['call_id'] = identifier
        if shape == 'invalid-body':
            host = json.loads(output['output'][1]['text']); host['output'] = '{"unproved":true}'
            output['output'][1]['text'] = json.dumps(host)
        copied = [chain.row('child', 'response_item', call)]
        if shape != 'unpaired-call':
            copied.append(chain.row('child', 'response_item', output))
        if shape == 'duplicate-output':
            copied.append(chain.row('child', 'response_item', output))
        return copied

    def refused_hold(self, fixture, action, request, offending):
        result = fixture.chain.fx.pending(action, request, ok=False)
        self.assertIn('HOLD_UNCLASSIFIED_TOOL_CALL', result.stdout)
        identifier = request.get('observation_id') or fixture.assignment()['return']['observation_id']
        saved = fixture.assignment()['hold_refusals'][identifier]
        self.assertEqual(saved['reason'], 'HOLD_UNCLASSIFIED_TOOL_CALL')
        self.assertEqual(saved['evidence']['record'], offending)
        raw = fixture.chain.logs['child'].read_bytes(); prefix = saved['evidence']['prefix']
        self.assertEqual(prefix['path'], str(fixture.chain.logs['child']))
        self.assertEqual(prefix['physical'], fixture.assignment()['observation_source']['child']['physical'])
        self.assertEqual(prefix['prefix_sha256'], hashlib.sha256(raw[:prefix['prefix_bytes']]).hexdigest())
        self.assertGreaterEqual(prefix['prefix_bytes'], offending['offset'] + offending['bytes'])
        self.assertTrue(all(row['consumed_version'] == 0 for row in fixture.state()['observations'].values()))
        return saved

    def test_oc01_retained_invalid_load_copy_is_not_selected_by_either_observation(self):
        fixture = self.fixture(); first = fixture.chain.bound_observation()
        prior = fixture.assignment()['prepared'][first[1]['observation_id']]
        pair = {key: pin['locator'] for key, pin in prior['authorization']['load_identity'].items()}
        extra = self.copied_pair(fixture, pair, 'independent-unproved-occurrence', 'invalid-body')
        pending = fixture.pending_bind(fixture.next_reserved())
        current = fixture.assignment()['prepared'][pending['bind']['observation_id']]
        for selected in (prior, current):
            self.assertNotEqual(extra[0], selected['authorization']['evidence']['load_call'])
            self.assertNotEqual(extra[1], selected['authorization']['evidence']['load_output'])
        self.refused_hold(fixture, 'observe-child', pending['bind'], extra[0])
        self.assertIsNone(fixture.assignment()['return']); self.assertIsNone(fixture.assignment()['join'])

    def test_oc02_valid_full_load_body_does_not_select_a_copied_occurrence(self):
        fixture = self.fixture(); first = fixture.chain.bound_observation()
        prior = fixture.assignment()['prepared'][first[1]['observation_id']]
        pair = {key: pin['locator'] for key, pin in prior['authorization']['load_identity'].items()}
        extra = self.copied_pair(fixture, pair, 'independent-valid-looking-load', 'valid-body')
        self.assertEqual(self.payload(fixture, extra[1])['output'], self.payload(fixture, pair['result'])['output'])
        pending = fixture.pending_bind(fixture.next_reserved())
        self.refused_hold(fixture, 'observe-child', pending['bind'], extra[0])

    def test_oc03_current_load_and_delivery_copies_are_not_current_mechanics(self):
        # Changing output syntax alone cannot fix an unselected physical call.
        for member in ('load', 'delivery'):
            for shape in ('invalid-body', 'valid-body', 'unpaired-call', 'duplicate-output'):
                with self.subTest(member=member, shape=shape):
                    fixture = self.fixture(); reserved = fixture.chain.reserve(); extra = []
                    def preface(bind):
                        prepared = fixture.assignment()['prepared'][bind['observation_id']]
                        pair = (prepared['authorization']['evidence'] if member == 'load' else bind['exchange'])
                        if member == 'load': pair = {'call': pair['load_call'], 'result': pair['load_output']}
                        extra.extend(self.copied_pair(fixture, pair, 'unselected-current-' + member, shape))
                    pending = fixture.pending_bind(reserved, preface)
                    self.refused_hold(fixture, 'observe-child', pending['bind'], extra[0])

    def test_oc04_duplicate_selected_outputs_cannot_borrow_call_association(self):
        for member in ('load', 'delivery'):
            with self.subTest(member=member):
                fixture = self.fixture(); reserved = fixture.chain.reserve(); extra = []
                def preface(bind):
                    prepared = fixture.assignment()['prepared'][bind['observation_id']]
                    locator = (prepared['authorization']['evidence']['load_output'] if member == 'load' else bind['exchange']['result'])
                    extra.append(fixture.chain.row('child', 'response_item', self.payload(fixture, locator)))
                pending = fixture.pending_bind(reserved, preface)
                result = fixture.chain.fx.pending('observe-child', pending['bind'], ok=False)
                self.assertIn('HOLD_UNPAIRED_TOOL_OUTPUT', result.stdout)
                self.assertEqual(fixture.assignment()['hold_refusals'][pending['bind']['observation_id']]['evidence']['record'], extra[0])

    def gap(self, member='load'):
        fixture = self.fixture(); pending = fixture.pending_bind(fixture.chain.reserve())
        observed = fixture.chain.fx.pending('observe-child', pending['bind'])
        prepared = fixture.assignment()['prepared'][observed['observation_id']]
        pair = (prepared['authorization']['load_identity'] if member == 'load' else prepared['exchange']['records'])
        pair = {key: pin['locator'] for key, pin in pair.items()}
        extra = self.copied_pair(fixture, pair, 'unselected-before-original-completion', 'invalid-body')
        completion = fixture.chain.row('child', 'response_item', {'type': 'custom_tool_call_output', 'call_id': 'pending-bind',
            'output': [{'type': 'input_text', 'text': 'Script completed\nOutput:\n'}, {'type': 'input_text', 'text': json.dumps({
                'chunk_id': 'pending-bind', 'wall_time_seconds': .1, 'exit_code': 0, 'original_token_count': 100, 'output': json.dumps(observed)})}]})
        bound = {'call': pending['original'], 'result': completion}
        return fixture, pending, observed, bound, extra

    def saved_return(self, fixture, observed, evidence):
        # JOIN must revalidate history even when stored status claims success.
        # This is deliberately unproved saved state, not a successful RETURN.
        fixture.save_assignment(lambda assignment: assignment.update({'return': {
            'status': 'SUCCEEDED', 'return_digest': 'f' * 64, 'observation_id': observed['observation_id'], 'evidence': evidence}}))
        return {'child_id': fixture.chain.child, 'return_digest': 'f' * 64, 'acceptance': {}}

    def test_oc05_original_completion_gap_is_revalidated_by_retry_return_and_join(self):
        for action in ('observe-child', 'return', 'join'):
            with self.subTest(action=action):
                fixture, pending, observed, bound, extra = self.gap()
                evidence = fixture.chain.actual_result(pending['reserved'], observed, bound)
                request = (pending['bind'] if action == 'observe-child' else
                    {'child_id': fixture.chain.child, 'observation_id': observed['observation_id'], 'result_evidence': evidence}
                    if action == 'return' else self.saved_return(fixture, observed, evidence))
                saved = self.refused_hold(fixture, action, request, extra[0])
                self.assertEqual(saved['evidence']['prefix']['prefix_bytes'], bound['result']['offset'] + bound['result']['bytes'])
                self.assertIsNone(fixture.assignment()['join'])

    def test_oc06_material_refusal_survives_restored_bytes_at_retry_return_and_join(self):
        fixture, pending, observed, bound, extra = self.gap('delivery')
        saved = self.refused_hold(fixture, 'observe-child', pending['bind'], extra[0])
        for locator in extra: fixture.neutralize(locator)
        evidence = fixture.chain.actual_result(pending['reserved'], observed, bound)
        for action, request in (
            ('observe-child', pending['bind']),
            ('return', {'child_id': fixture.chain.child, 'observation_id': observed['observation_id'], 'result_evidence': evidence})):
            result = fixture.chain.fx.pending(action, request, ok=False)
            self.assertIn('HOLD_EPISODE_PREVIOUSLY_REFUSED', result.stdout)
        request = self.saved_return(fixture, observed, evidence)
        result = fixture.chain.fx.pending('join', request, ok=False)
        self.assertIn('HOLD_EPISODE_PREVIOUSLY_REFUSED', result.stdout)
        self.assertEqual(fixture.assignment()['hold_refusals'][observed['observation_id']], saved)
        self.assertTrue(all(row['consumed_version'] == 0 for row in fixture.state()['observations'].values()))

    def test_oc07_same_text_bind_copy_before_original_cannot_be_a_retry(self):
        for shape in ('unpaired-call', 'changed-output', 'duplicate-association'):
            with self.subTest(shape=shape):
                fixture = self.fixture(); reserved = fixture.chain.reserve()
                def preface(bind):
                    command = fixture.chain.adapter().delivery_tool_input(fixture.chain.fx.store, fixture.chain.fx.session, 'host-owner', bind)
                    if shape == 'unpaired-call':
                        fixture.chain.row('child', 'response_item', {'type': 'custom_tool_call', 'name': 'exec',
                            'call_id': 'copied-bind', 'status': 'completed', 'input': command})
                    else:
                        pair = fixture.chain.exchange('child', 'copied-bind', command, '{"unproved":true}')
                        if shape == 'duplicate-association':
                            fixture.chain.row('child', 'response_item', self.payload(fixture, pair[1]))
                pending = fixture.pending_bind(reserved, preface)
                result = fixture.chain.fx.pending('observe-child', pending['bind'], ok=False)
                self.assertIn('HOLD_ORIGINAL_BIND_CALL_UNPROVED', result.stdout)
                self.assertIsNone(fixture.assignment()['return']); self.assertIsNone(fixture.assignment()['join'])

    def test_oc08_same_id_copies_of_selected_current_calls_remain_unproved(self):
        for member in ('load', 'delivery'):
            with self.subTest(member=member):
                fixture = self.fixture(); reserved = fixture.chain.reserve(); extra = []
                def preface(bind):
                    prepared = fixture.assignment()['prepared'][bind['observation_id']]
                    pair = (prepared['authorization']['evidence'] if member == 'load' else bind['exchange'])
                    if member == 'load': pair = {'call': pair['load_call'], 'result': pair['load_output']}
                    identifier = self.payload(fixture, pair['call'])['call_id']
                    extra.extend(self.copied_pair(fixture, pair, identifier, 'valid-body'))
                pending = fixture.pending_bind(reserved, preface)
                self.refused_hold(fixture, 'observe-child', pending['bind'], extra[0])

    def test_oc09_bind_copy_inside_original_completion_gap_is_not_a_retry(self):
        for shape in ('invalid-body', 'valid-body', 'unpaired-call', 'duplicate-output'):
            with self.subTest(shape=shape):
                fixture = self.fixture(); pending = fixture.pending_bind(fixture.chain.reserve())
                observed = fixture.chain.fx.pending('observe-child', pending['bind'])
                copied = self.payload(fixture, pending['original']); copied['call_id'] = 'unselected-bind-before-original-completion'
                extra = fixture.chain.row('child', 'response_item', copied)
                original_output = {'type': 'custom_tool_call_output', 'call_id': 'pending-bind', 'output': [
                    {'type': 'input_text', 'text': 'Script completed\nOutput:\n'}, {'type': 'input_text', 'text': json.dumps({
                        'chunk_id': 'pending-bind', 'wall_time_seconds': .1, 'exit_code': 0,
                        'original_token_count': 100, 'output': json.dumps(observed)})}]}
                output = fixture.clone(original_output); output['call_id'] = copied['call_id']
                if shape == 'invalid-body':
                    host = json.loads(output['output'][1]['text']); host['output'] = '{"unproved":true}'
                    output['output'][1]['text'] = json.dumps(host)
                if shape != 'unpaired-call': fixture.chain.row('child', 'response_item', output)
                if shape == 'duplicate-output': fixture.chain.row('child', 'response_item', output)
                completion = fixture.chain.row('child', 'response_item', original_output)
                saved = self.refused_hold(fixture, 'observe-child', pending['bind'], extra)
                self.assertEqual(saved['evidence']['prefix']['prefix_bytes'], completion['offset'] + completion['bytes'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
