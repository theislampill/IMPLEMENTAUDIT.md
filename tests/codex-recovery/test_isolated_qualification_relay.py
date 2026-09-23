"""Synthetic relay controls; no native process, model, job or governor call.

Breaks caught: reserved-route narration for source-only measurement, cross-mode
ACK acceptance, missing custody/parent/prefix checks, and late or duplicate USE.
The marker, parent parser and staged protocol remain real. Only native/proof
boundaries in the provider integration controls are substituted.
"""
import argparse
import copy
import contextlib
import ctypes
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

PURPOSE = 'ISOLATED_QUALIFICATION'
PARENT = '11111111-1111-4111-8111-111111111111'
WORKER = '22222222-2222-4222-8222-222222222222'
LOGICAL = 'synthetic_isolated_qualification'
NORMAL_LOGICAL = 'synthetic_governed_child'
SOURCE = WORK = None
SHARED = NATIVE = PARENT_READER = PROVIDER = ROUTE = INTERLOCK = None


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ready(isolated=True):
    row = {'schema': 'child-load-ready-v1',
        'identity': {'selected_child': None if isolated else 'audit-assess',
            'parent_thread_id': PARENT, 'transaction_ref': 'synthetic_run',
            'reason': 'check the selected source delivery', 'source_sha256': '1' * 64},
        'worker_thread_id': WORKER,
        'process_identity': {'pid': 31337, 'creation_filetime_100ns': 133777777777777777,
            'creation_utc': '2024-11-04T12:29:37.777778+00:00',
            'identity_source': 'SYNTHETIC_ONLY'},
        'load_evidence': {'command_item_id': 'command-1', 'model_ready_item_id': 'ready-1',
            'turn_id': 'turn-1', 'snapshot_sha256': '2' * 64},
        'raw_prefix': [{'path': str(WORK / name), 'bytes': 1, 'sha256': sha(b'x')}
            for name in ('stdout.bin', 'stderr.bin', 'sent.jsonl')],
        'phase_capable_source_adoption': {'path': str(WORK / 'source.json'), 'bytes': 1, 'sha256': '3' * 64},
        'runtime_selection_acceptance': {'path': str(WORK / 'selection.json'), 'bytes': 1, 'sha256': '4' * 64},
        'semantic_verdict': None, 'owner_stage_receipt': None}
    if isolated:
        row['purpose'] = PURPOSE
        row['identity']['logical_task'] = LOGICAL
    else:
        row['identity']['logical_task'] = NORMAL_LOGICAL
    return row


def legacy_normal_marker(row, digest):
    return ('CHILD_SKILL_ROUTE=audit-assess\n'
        "I'm using audit-assess to check the selected source delivery.\n"
        'Child task: ' + WORKER + '; LOAD_READY_SHA256=' + digest)


def normal_marker(row, digest):
    return ('```ini\nCHILD_TASK=' + NORMAL_LOGICAL + '\nCHILD_SKILL_ROUTE=audit-assess\n'
        'LOAD=VERIFIED\nWORKER_TASK=' + WORKER + '\nLOAD_READY_SHA256=' + digest + '\n```\n'
        "I'm using the `" + NORMAL_LOGICAL + '` holon with the `audit-assess` skill '
        'to check the selected source delivery.')


def fixture_parent(directory, marker, *, role='assistant', channel='commentary', duplicate=False,
                   parent=PARENT, partial=False):
    meta = encode({'type': 'session_meta', 'payload': {'id': parent}})
    row = encode({'type': 'response_item', 'payload': {'type': 'message', 'role': role,
        'channel': channel, 'content': [{'type': 'output_text', 'text': marker}]}})
    raw = meta + row + (row if duplicate else b'')
    if partial:
        raw = raw[:-1]
    path = directory / 'parent.jsonl'
    path.write_bytes(raw)
    return path, len(meta), row


class MarkerAndAckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def isolated_marker(self, module, row):
        try:
            return module.marker_for(row, sha(encode(row)))
        except (ValueError, KeyError) as exc:
            self.fail('Truthful isolated presentation is unsupported: ' + str(exc))

    def test_truthful_isolated_marker_has_own_ini_and_named_task(self):
        row = ready()
        for module in (SHARED, NATIVE):
            with self.subTest(module=module.__name__):
                marker = self.isolated_marker(module, row)
                self.assertTrue(marker.startswith('```ini\n'))
                self.assertIn('ISOLATED_QUALIFICATION=LOAD_READY', marker)
                self.assertIn('LOGICAL_TASK=' + LOGICAL, marker)
                self.assertIn('SOURCE_SHA256=' + '1' * 64, marker)
                self.assertIn('WORKER_TASK=' + WORKER, marker)
                self.assertIn('PROCESS_PID=31337', marker)
                self.assertIn('PROCESS_BIRTH_FILETIME_100NS=133777777777777777', marker)
                self.assertIn('LOAD_READY_SHA256=' + sha(encode(row)), marker)
                self.assertIn('\n```\n', marker)
                self.assertIn(LOGICAL, marker.split('\n```\n', 1)[1])
                self.assertNotIn('CHILD_SKILL_ROUTE', marker)
                self.assertNotIn("I'm using", marker)

    def test_normal_marker_behavior_is_retained(self):
        row = ready(False); digest = sha(encode(row))
        for module in (SHARED, NATIVE):
            self.assertEqual(module.marker_for(row, digest), normal_marker(row, digest))

    def test_shared_and_native_isolated_parser_accept_same_actual_row(self):
        row = ready(); digest = sha(encode(row))
        marker = self.isolated_marker(SHARED, row)
        self.assertEqual(marker, self.isolated_marker(NATIVE, row))
        path, offset, raw = fixture_parent(self.directory, marker)
        ack = {'ready_sha256': digest, 'parent_row_offset': offset,
            'parent_row_bytes': len(raw), 'parent_row_sha256': sha(raw)}
        expected = {'path': str(path), 'offset': offset, 'bytes': len(raw), 'sha256': sha(raw)}
        for module in (PARENT_READER, NATIVE):
            self.assertEqual(module.verify_parent_ack(ack, row, digest, path, offset, offset), expected)

    def test_normal_parser_round_trip_is_retained(self):
        row = ready(False); digest = sha(encode(row))
        path, offset, raw = fixture_parent(self.directory, normal_marker(row, digest))
        ack = {'ready_sha256': digest, 'parent_row_offset': offset,
            'parent_row_bytes': len(raw), 'parent_row_sha256': sha(raw)}
        for module in (PARENT_READER, NATIVE):
            try: result = module.verify_parent_ack(ack, row, digest, path, offset, offset)
            except ValueError as exc: self.fail('Grouped normal INI marker refused: ' + str(exc))
            self.assertEqual(result['sha256'], sha(raw))

    def test_isolated_refuses_reserved_governed_marker(self):
        row = ready(); digest = sha(encode(row))
        path, offset, raw = fixture_parent(self.directory, normal_marker(row, digest))
        ack = {'ready_sha256': digest, 'parent_row_offset': offset,
            'parent_row_bytes': len(raw), 'parent_row_sha256': sha(raw)}
        for module in (PARENT_READER, NATIVE):
            with self.assertRaises(ValueError):
                module.verify_parent_ack(ack, row, digest, path, offset, offset)

    def test_governed_refuses_isolated_marker(self):
        isolated = ready(); row = ready(False); digest = sha(encode(row))
        marker = self.isolated_marker(SHARED, isolated)
        path, offset, raw = fixture_parent(self.directory, marker)
        ack = {'ready_sha256': digest, 'parent_row_offset': offset,
            'parent_row_bytes': len(raw), 'parent_row_sha256': sha(raw)}
        for module in (PARENT_READER, NATIVE):
            with self.assertRaises(ValueError):
                module.verify_parent_ack(ack, row, digest, path, offset, offset)

    def test_missing_or_unknown_isolated_mode_refuses(self):
        for mode in ('MISSING', '', 'UNKNOWN', None):
            row = ready()
            if mode == 'MISSING': row.pop('purpose')
            else: row['purpose'] = mode
            for module in (SHARED, NATIVE):
                with self.subTest(mode=mode, module=module.__name__), self.assertRaises(ValueError):
                    module.marker_for(row, sha(encode(row)))

    def test_isolated_rejects_governed_selector_and_malformed_custody(self):
        for case in ('selector', 'missing_selector', 'task', 'source', 'worker', 'pid', 'birth', 'prefix', 'verdict', 'stage'):
            row = ready()
            if case == 'selector': row['identity']['selected_child'] = 'audit-assess'
            elif case == 'missing_selector': row['identity'].pop('selected_child')
            elif case == 'task': row['identity']['logical_task'] = 'bad\nTASK'
            elif case == 'source': row['identity']['source_sha256'] = 'not-a-digest'
            elif case == 'worker': row['worker_thread_id'] = ''
            elif case == 'pid': row['process_identity']['pid'] = True
            elif case == 'birth': row['process_identity']['creation_filetime_100ns'] = 0
            elif case == 'prefix': row['raw_prefix'] = []
            elif case == 'verdict': row['semantic_verdict'] = 'PASS'
            else: row['owner_stage_receipt'] = 'INVENTED'
            for module in (SHARED, NATIVE):
                with self.subTest(case=case, module=module.__name__), self.assertRaises(ValueError):
                    module.marker_for(row, sha(encode(row)))

    def test_foreign_READY_digest_refuses_both_modes(self):
        for isolated in (False, True):
            for module in (SHARED, NATIVE):
                with self.subTest(isolated=isolated), self.assertRaises(ValueError):
                    module.marker_for(ready(isolated), '0' * 64)

    def test_parent_row_identity_order_and_uniqueness_remain_required(self):
        for isolated in (False, True):
            row = ready(isolated); digest = sha(encode(row))
            marker = self.isolated_marker(SHARED, row) if isolated else normal_marker(row, digest)
            for case in ('missing', 'tool', 'analysis', 'wrong_parent', 'duplicate', 'partial', 'retroactive', 'wrong_offset', 'wrong_digest'):
                options = {}
                actual = marker
                if case == 'missing': actual = 'ordinary unrelated commentary'
                elif case == 'tool': options['role'] = 'tool'
                elif case == 'analysis': options['channel'] = 'analysis'
                elif case == 'wrong_parent': options['parent'] = WORKER
                elif case == 'duplicate': options['duplicate'] = True
                elif case == 'partial': options['partial'] = True
                path, offset, raw = fixture_parent(self.directory, actual, **options)
                ack = {'ready_sha256': digest, 'parent_row_offset': offset,
                    'parent_row_bytes': len(raw), 'parent_row_sha256': sha(raw)}
                if case == 'wrong_offset': ack['parent_row_offset'] += 1
                if case == 'wrong_digest': ack['ready_sha256'] = '0' * 64
                floor = offset + 1 if case == 'retroactive' else offset
                for module in (PARENT_READER, NATIVE):
                    with self.subTest(isolated=isolated, case=case, module=module.__name__), self.assertRaises(ValueError):
                        module.verify_parent_ack(ack, row, digest, path, offset, floor)

    def test_wrong_task_worker_or_birth_cannot_reuse_parent_ACK(self):
        old = ready(); marker = self.isolated_marker(SHARED, old)
        path, offset, raw = fixture_parent(self.directory, marker)
        for case in ('task', 'worker', 'birth', 'source'):
            row = copy.deepcopy(old)
            if case == 'task': row['identity']['logical_task'] = 'other_task'
            elif case == 'worker': row['worker_thread_id'] = PARENT
            elif case == 'birth': row['process_identity']['creation_filetime_100ns'] += 1
            else: row['identity']['source_sha256'] = '5' * 64
            digest = sha(encode(row))
            ack = {'ready_sha256': digest, 'parent_row_offset': offset,
                'parent_row_bytes': len(raw), 'parent_row_sha256': sha(raw)}
            for module in (PARENT_READER, NATIVE):
                with self.subTest(case=case), self.assertRaises(ValueError):
                    module.verify_parent_ack(ack, row, digest, path, offset, offset)


class PrefixAndModeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def test_existing_prefix_reader_detects_byte_drift(self):
        row = ready()
        for item in row['raw_prefix']:
            path = self.directory / Path(item['path']).name
            path.write_bytes(b'x'); item['path'] = str(path)
        self.assertEqual(PARENT_READER.read_prefixes(row, self.directory, 1048576),
            {'stdout.bin': b'x', 'stderr.bin': b'x', 'sent.jsonl': b'x'})
        (self.directory / 'stdout.bin').write_bytes(b'y')
        with self.assertRaises(ValueError):
            PARENT_READER.read_prefixes(row, self.directory, 1048576)

    def test_governed_bundle_cannot_consume_isolated_purpose(self):
        plan = {'purpose': PURPOSE, 'visibility': {'identity': ready(False)['identity']},
            'adapter_source': PROVIDER.MEMBERS['capture.py']}
        raw = encode(plan); (self.directory / 'THREAD_METADATA_PLAN.json').write_bytes(raw)
        with self.assertRaises(ValueError):
            PROVIDER.bundle_plan(sha(raw), self.directory)

    def test_valid_normal_bundle_selection_remains_valid(self):
        for purpose in ('OFFLINE_FIXTURE', 'NATURALLY_WARRANTED_WORKER'):
            plan = {'purpose': purpose, 'visibility': {'identity': ready(False)['identity']},
                'adapter_source': PROVIDER.MEMBERS['capture.py']}
            raw = encode(plan); (self.directory / 'THREAD_METADATA_PLAN.json').write_bytes(raw)
            self.assertEqual(PROVIDER.bundle_plan(sha(raw), self.directory), plan)

    def test_isolated_context_has_explicit_source_owned_entrypoint(self):
        method = getattr(PROVIDER, 'verify_isolated_qualification_load_ready', None)
        self.assertTrue(callable(method), 'Existing provider lacks isolated qualification custody verification')
        context = {'path_kind': 'governed', 'purpose': PURPOSE}
        with self.assertRaises(ValueError):
            method(context, ready(), {})


class StagedAckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def exercise(self, *, isolated=True, ack_kind='exact', parent_labels=None):
        expected = ready(isolated)
        parent_path = self.directory / 'parent.jsonl'
        parent_path.write_bytes(encode({'type': 'session_meta', 'payload': {'id': PARENT}}))
        cursor = parent_path.stat().st_size
        run = self.directory / 'run'; run.mkdir()
        prefixes = []
        for name in ('stdout.bin', 'stderr.bin', 'sent.jsonl'):
            path = run / name; path.write_bytes(b'x')
            prefixes.append({'path': str(path), 'bytes': 1, 'sha256': sha(b'x')})
        identity = expected['identity']
        cfg = {'identity': identity, 'parent_rollout': str(parent_path),
            'parent_launch_offset': cursor, 'ack_timeout_seconds': 1,
            'phase_capable_source_adoption': expected['phase_capable_source_adoption'],
            'runtime_selection_acceptance': expected['runtime_selection_acceptance'],
            'load_input': [{'type': 'text', 'text': 'SYNTHETIC_LOAD', 'text_elements': []}],
            'use_input': [{'type': 'text', 'text': 'SYNTHETIC_USE', 'text_elements': []}]}
        plan = {'purpose': PURPOSE if isolated else 'NATURALLY_WARRANTED_WORKER', 'visibility': cfg,
            'binding': {'load_pins': {'child_source': {'sha256': identity['source_sha256']}}},
            'turn_start': {'id': 5, 'method': 'turn/start', 'params': {'threadId': 'FUTURE', 'input': cfg['load_input']}},
            'use_turn_start': {'id': 6, 'method': 'turn/start', 'params': {'threadId': 'FUTURE', 'input': cfg['use_input']}},
            'expected_turn_settings': {'USE': {'activePermissionProfile': {'id': 'worker_use', 'extends': None}}}}
        class Canary:
            thread_id = WORKER
            completed = True
            phase = 'LOAD'
            first_anomaly = None
            def fail(self, reason):
                if self.first_anomaly is None: self.first_anomaly = reason
                raise ValueError(self.first_anomaly)
            def qualify_load(self): return copy.deepcopy(expected['load_evidence'])
            def release(self, digest, settings):
                if self.first_anomaly is not None: raise ValueError(self.first_anomaly)
                if self.phase != 'LOAD': raise ValueError('Duplicate USE release')
                self.phase = 'USE'
            def transport_complete(self): return self.phase == 'USE'
            def snapshot(self): return {'phase': self.phase}
        canary = Canary(); requests = []; clock = [0.0]
        def response(request):
            requests.append(copy.deepcopy(request))
            return {'result': {}}
        def pause(seconds):
            observed = json.loads((run / 'LOAD_READY.json').read_bytes())
            digest = sha(encode(observed))
            if ack_kind == 'none':
                clock[0] += 2
                return
            if ack_kind == 'late': clock[0] += 2
            marker = normal_marker(observed, digest) if ack_kind == 'cross_mode' else SHARED.marker_for(observed, digest)
            message = {'type': 'message', 'role': 'assistant',
                'content': [{'type': 'output_text', 'text': marker}]}
            message.update({'channel': 'commentary'} if parent_labels is None else parent_labels)
            row = encode({'type': 'response_item', 'payload': message})
            offset = parent_path.stat().st_size
            with parent_path.open('ab') as stream:
                stream.write(row)
                if ack_kind == 'duplicate': stream.write(row)
            ack = {'ready_sha256': digest, 'parent_row_offset': offset,
                'parent_row_bytes': len(row), 'parent_row_sha256': sha(row)}
            (run / 'PARENT_VISIBILITY_ACK.json').write_bytes(encode(ack))
        failure = None
        try:
            value = NATIVE.staged_turns(plan=plan, canary=canary, response=response,
                check_deadline=lambda: None, wait_event=lambda: None,
                process_identity=expected['process_identity'], flush_raw=lambda: prefixes,
                run=run, clock=lambda: clock[0], pause=pause, relay=lambda *args, **kwargs: None)
        except (ValueError, KeyError) as exc:
            # staged_turns latches a typed outer error; retain the actual ACK
            # rejection so an earlier fixture error cannot satisfy a negative.
            failure = str(exc.__context__ or exc); value = None
            self.assertEqual(canary.phase, 'LOAD')
            self.assertIsNotNone(canary.first_anomaly)
        return value, failure, requests, run

    def test_isolated_READY_and_actual_parent_ACK_release_one_USE_on_same_worker(self):
        value, failure, requests, run = self.exercise()
        self.assertIsNone(failure, 'Isolated staged relay refused: ' + str(failure))
        row = json.loads((run / 'LOAD_READY.json').read_bytes())
        self.assertEqual(row['purpose'], PURPOSE)
        self.assertIsNone(row['semantic_verdict']); self.assertIsNone(row['owner_stage_receipt'])
        self.assertEqual([(row['id'], row['params']['threadId']) for row in requests], [(5, WORKER), (6, WORKER)])
        release = json.loads((run / 'RELEASE.json').read_bytes())
        self.assertEqual(release['delivery_status'], 'PENDING')
        self.assertEqual(release['worker_thread_id'], WORKER)
        self.assertEqual(value['status'], 'TWO_TURN_TRANSPORT_COMPLETE_NONVERDICT')

    def test_normal_staged_relay_and_READY_remain_unchanged(self):
        value, failure, requests, run = self.exercise(isolated=False)
        self.assertIsNone(failure)
        self.assertNotIn('purpose', json.loads((run / 'LOAD_READY.json').read_bytes()))
        self.assertEqual([row['id'] for row in requests], [5, 6])
        self.assertEqual(value['status'], 'TWO_TURN_TRANSPORT_COMPLETE_NONVERDICT')

    def test_cross_mode_ACK_cannot_release_isolated_USE(self):
        value, failure, requests, run = self.exercise(ack_kind='cross_mode')
        self.assertEqual(failure, 'Missing or duplicate truthful parent marker')
        self.assertEqual([row['id'] for row in requests], [5])
        self.assertFalse((run / 'RELEASE.json').exists())

    def test_late_ACK_cannot_release_USE(self):
        value, failure, requests, run = self.exercise(ack_kind='late')
        self.assertEqual(failure, 'Late or post-USE ACK')
        self.assertEqual([row['id'] for row in requests], [5])
        self.assertFalse((run / 'RELEASE.json').exists())

    def test_duplicate_parent_marker_cannot_release_USE(self):
        value, failure, requests, run = self.exercise(ack_kind='duplicate')
        self.assertEqual(failure, 'Missing or duplicate truthful parent marker')
        self.assertEqual([row['id'] for row in requests], [5])
        self.assertFalse((run / 'RELEASE.json').exists())


class IsolatedParentConsumerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def fixture(self):
        bundle = self.directory / 'bundle'; bundle.mkdir()
        run = bundle / 'runs/synthetic_run'; run.mkdir(parents=True)
        row = ready()
        prefixes = {}
        for item in row['raw_prefix']:
            path = run / Path(item['path']).name
            path.write_bytes(b'x'); item['path'] = str(path)
            prefixes[path.name] = b'x'
        parent_path = self.directory / 'parent.jsonl'
        parent_path.write_bytes(encode({'type': 'session_meta', 'payload': {'id': PARENT}}))
        cursor = parent_path.stat().st_size
        cfg = {'identity': copy.deepcopy(row['identity']), 'parent_rollout': str(parent_path),
            'parent_launch_offset': cursor,
            'phase_capable_source_adoption': row['phase_capable_source_adoption'],
            'runtime_selection_acceptance': row['runtime_selection_acceptance']}
        plan = {'purpose': PURPOSE, 'visibility': cfg, 'server_argv': ['SYNTHETIC_NO_PROCESS'],
            'server_cwd': str(self.directory), 'binding': {'load_pins': {'child_source': {'sha256': '1' * 64}}}}
        plan_raw = encode(plan); plan_path = bundle / 'THREAD_METADATA_PLAN.json'; plan_path.write_bytes(plan_raw)
        context = {'path_kind': 'isolated_qualification', 'purpose': PURPOSE, 'bundle_root': str(bundle),
            'plan_sha256': sha(plan_raw), 'run_name': 'synthetic_run', 'run': str(run),
            'identity': copy.deepcopy(row['identity']), 'parent_rollout': str(parent_path), 'parent_launch_offset': cursor}
        plan_pin = {'path': str(plan_path), 'bytes': len(plan_raw), 'sha256': sha(plan_raw)}
        (run / 'INVOCATION.json').write_bytes(encode({'plan': plan_pin, 'argv': plan['server_argv'], 'cwd': plan['server_cwd']}))
        (run / 'PROCESS_CUSTODY.json').write_bytes(encode({'plan_sha256': sha(plan_raw), 'process_identity': row['process_identity']}))
        ready_path = run / 'LOAD_READY.json'; raw = encode(row); ready_path.write_bytes(raw)
        ready_pin = {'path': str(ready_path), 'bytes': len(raw), 'sha256': sha(raw)}
        helper = load(SOURCE / 'skills/implementaudit/scripts/native-capture-adapter/process_owner.py', 'fixture_file_owner')
        return context, plan, row, prefixes, ready_pin, helper

    def boundaries(self, context, plan, row, prefixes, helper):
        required = ('isolated_qualification_preflight', 'verify_isolated_qualification_load_ready')
        for name in required:
            self.assertTrue(callable(getattr(PROVIDER, name, None)), 'Missing isolated source-owned consumer: ' + name)
        def preflight(digest, *, bundle_root):
            self.assertEqual((digest, str(bundle_root)), (context['plan_sha256'], context['bundle_root']))
            return copy.deepcopy(plan), [], helper
        def replay(actual_plan, actual_ready, actual_prefixes, *, bundle_root):
            self.assertEqual(actual_plan, plan); self.assertEqual(actual_ready, row)
            self.assertEqual(actual_prefixes, prefixes); self.assertEqual(str(bundle_root), context['bundle_root'])
            return copy.deepcopy(row['load_evidence'])
        def liveness(identity):
            self.assertEqual(identity, row['process_identity'])
        return (patch.object(PROVIDER, 'isolated_qualification_preflight', preflight),
                patch.object(PROVIDER, 'replay_load', replay),
                patch.object(PROVIDER, 'require_live_process', liveness))

    def test_c91_06a_one_verified_ready_reaches_owned_custody(self):
        context, plan, row, prefixes, ready_pin, helper = self.fixture()
        a, b, c = self.boundaries(context, plan, row, prefixes, helper)
        with a, b, c:
            with (patch.object(PROVIDER, 'isolated_qualification_preflight', wraps=PROVIDER.isolated_qualification_preflight) as preflight,
                  patch.object(PROVIDER, 'replay_load', wraps=PROVIDER.replay_load) as replay,
                  patch.object(PROVIDER, 'require_live_process', wraps=PROVIDER.require_live_process) as liveness):
                # One direct call measures this edge; the full inspect/ACK test below
                # deliberately performs its own repeated revalidations.
                actual, actual_sha, proof = PARENT_READER.verified_ready(context, ready_pin, PROVIDER)
                preflight.assert_called_once_with(context['plan_sha256'], bundle_root=context['bundle_root'])
                replay.assert_called_once()
                liveness.assert_called_once_with(row['process_identity'])
                self.assertEqual((actual, actual_sha), (row, ready_pin['sha256']))
                self.assertEqual(proof, {'load_evidence': row['load_evidence'],
                    'worker_thread_id': row['worker_thread_id'], 'process_identity': row['process_identity']})
                counts = {'preflight': preflight.call_count, 'replay': replay.call_count, 'liveness': liveness.call_count}
        self.assertTrue(all(not (Path(context['run']) / name).exists()
                            for name in ('PARENT_VISIBILITY_ACK.json', 'RELEASE.json', 'READBACK.json')))
        (WORK / 'C91-06A.json').write_bytes(encode({'control': 'C91-06A', 'guard_reach': counts,
            'verified_ready_calls': 1, 'source_test_only': True, 'native_freshness': 'H84-01_UNQUALIFIED'}))

    def test_c91_06b_same_run_release_presence_reaches_prior_use_guard(self):
        context, plan, row, prefixes, ready_pin, helper = self.fixture()
        # This exact owner checks marker presence, not authenticated prior use.
        marker = Path(context['run']) / 'RELEASE.json'
        marker.write_bytes(encode({'ready_sha256': ready_pin['sha256'],
            'worker_thread_id': row['worker_thread_id'], 'delivery_status': 'PENDING'}))
        a, b, c = self.boundaries(context, plan, row, prefixes, helper)
        with a, b, c:
            with (patch.object(PROVIDER, 'isolated_qualification_preflight', wraps=PROVIDER.isolated_qualification_preflight) as preflight,
                  patch.object(PROVIDER, 'replay_load', wraps=PROVIDER.replay_load) as replay,
                  patch.object(PROVIDER, 'require_live_process', wraps=PROVIDER.require_live_process) as liveness):
                with self.assertRaisesRegex(ValueError, 'Worker already released, disposed or terminal'):
                    PARENT_READER.verified_ready(context, ready_pin, PROVIDER)
                preflight.assert_called_once_with(context['plan_sha256'], bundle_root=context['bundle_root'])
                replay.assert_not_called()
                liveness.assert_not_called()
                counts = {'preflight': preflight.call_count, 'replay': replay.call_count, 'liveness': liveness.call_count}
        self.assertEqual({name: (Path(context['run']) / name).read_bytes() for name in prefixes}, prefixes)
        (WORK / 'C91-06B.json').write_bytes(encode({'control': 'C91-06B', 'guard_reach': counts,
            'refusal': 'Worker already released, disposed or terminal', 'public_prefixes_unchanged': True,
            'scope': 'same-run release marker presence only', 'native_prior_assignment': 'H84-01_UNQUALIFIED'}))

    def test_c91_06c_birth_mismatch_reaches_process_custody_guard(self):
        context, plan, row, prefixes, ready_pin, helper = self.fixture()
        custody_path = Path(context['run']) / 'PROCESS_CUSTODY.json'
        custody = json.loads(custody_path.read_bytes())
        custody['process_identity']['creation_filetime_100ns'] += 1
        custody_path.write_bytes(encode(custody))
        a, b, c = self.boundaries(context, plan, row, prefixes, helper)
        with a, b, c:
            with (patch.object(PROVIDER, 'isolated_qualification_preflight', wraps=PROVIDER.isolated_qualification_preflight) as preflight,
                  patch.object(PROVIDER, 'replay_load', wraps=PROVIDER.replay_load) as replay,
                  patch.object(PROVIDER, 'require_live_process', wraps=PROVIDER.require_live_process) as liveness):
                with self.assertRaisesRegex(ValueError, 'READY process differs from retained launch custody'):
                    PARENT_READER.verified_ready(context, ready_pin, PROVIDER)
                preflight.assert_called_once()
                replay.assert_not_called()
                liveness.assert_not_called()
                counts = {'preflight': preflight.call_count, 'replay': replay.call_count, 'liveness': liveness.call_count}
        self.assertEqual(json.loads(Path(ready_pin['path']).read_bytes()), row)
        (WORK / 'C91-06C.json').write_bytes(encode({'control': 'C91-06C', 'guard_reach': counts,
            'refusal': 'READY process differs from retained launch custody', 'READY_unchanged': True,
            'native_process_birth_observed': False}))

    def test_c91_06d_missing_custody_cannot_be_inferred_fresh(self):
        context, plan, row, prefixes, ready_pin, helper = self.fixture()
        custody_path = Path(context['run']) / 'PROCESS_CUSTODY.json'
        self.assertTrue(custody_path.resolve().is_relative_to(self.directory.resolve()))
        custody_path.unlink()
        a, b, c = self.boundaries(context, plan, row, prefixes, helper)
        with a, b, c:
            with (patch.object(PROVIDER, 'isolated_qualification_preflight', wraps=PROVIDER.isolated_qualification_preflight) as preflight,
                  patch.object(PROVIDER, 'replay_load', wraps=PROVIDER.replay_load) as replay,
                  patch.object(PROVIDER, 'require_live_process', wraps=PROVIDER.require_live_process) as liveness):
                with self.assertRaises(FileNotFoundError) as failure:
                    PARENT_READER.verified_ready(context, ready_pin, PROVIDER)
                self.assertEqual(Path(failure.exception.filename), custody_path)
                preflight.assert_called_once()
                replay.assert_not_called()
                liveness.assert_not_called()
                counts = {'preflight': preflight.call_count, 'replay': replay.call_count, 'liveness': liveness.call_count}
        self.assertTrue(all(not (Path(context['run']) / name).exists()
                            for name in ('PARENT_VISIBILITY_ACK.json', 'RELEASE.json', 'READBACK.json')))
        (WORK / 'C91-06D.json').write_bytes(encode({'control': 'C91-06D', 'guard_reach': counts,
            'missing_input': 'PROCESS_CUSTODY.json', 'native_freshness': 'H84-01_UNQUALIFIED',
            'release_or_ack_created': False}))

    def test_isolated_parent_inspection_and_one_ACK_use_existing_custody_checks(self):
        context, plan, row, prefixes, ready_pin, helper = self.fixture()
        a, b, c = self.boundaries(context, plan, row, prefixes, helper)
        with a, b, c:
            inspection = PARENT_READER.inspect_load(context, ready_pin, PROVIDER)
            self.assertFalse(inspection['narration_performed']); self.assertFalse(inspection['USE_released'])
            text = inspection['expected_announcement_text']
            self.assertTrue(text.startswith('```ini\nISOLATED_QUALIFICATION=LOAD_READY'))
            parent_path = Path(context['parent_rollout']); offset = parent_path.stat().st_size
            parent_row = encode({'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant',
                'channel': 'commentary', 'content': [{'type': 'output_text', 'text': text}]}})
            with parent_path.open('ab') as stream: stream.write(parent_row)
            result = PARENT_READER.acknowledge_load(context, ready_pin, inspection['inspection'], PROVIDER)
            self.assertEqual(result['status'], 'ACTUAL_PARENT_ROW_BOUND_ACK_PUBLISHED')
            ack = json.loads((Path(context['run']) / 'PARENT_VISIBILITY_ACK.json').read_bytes())
            self.assertEqual(ack, {'ready_sha256': ready_pin['sha256'], 'parent_row_offset': offset,
                'parent_row_bytes': len(parent_row), 'parent_row_sha256': sha(parent_row)})
            with self.assertRaises(ValueError):
                PARENT_READER.acknowledge_load(context, ready_pin, inspection['inspection'], PROVIDER)

    def test_isolated_consumer_refuses_prefix_growth_after_READY(self):
        context, plan, row, prefixes, ready_pin, helper = self.fixture()
        with (Path(context['run']) / 'stdout.bin').open('ab') as stream: stream.write(b'y')
        a, b, c = self.boundaries(context, plan, row, prefixes, helper)
        with a, b, c, self.assertRaisesRegex(ValueError, 'Held LOAD stream advanced'):
            PARENT_READER.verified_ready(context, ready_pin, PROVIDER)

    def test_isolated_consumer_refuses_different_process_birth_custody(self):
        context, plan, row, prefixes, ready_pin, helper = self.fixture()
        path = Path(context['run']) / 'PROCESS_CUSTODY.json'
        changed = json.loads(path.read_bytes()); changed['process_identity']['creation_filetime_100ns'] += 1
        path.write_bytes(encode(changed))
        a, b, c = self.boundaries(context, plan, row, prefixes, helper)
        with a, b, c, self.assertRaisesRegex(ValueError, 'READY process differs'):
            PARENT_READER.verified_ready(context, ready_pin, PROVIDER)

    def test_isolated_consumer_refuses_normal_READY(self):
        context, plan, row, prefixes, ready_pin, helper = self.fixture()
        wrong = copy.deepcopy(row); wrong.pop('purpose'); wrong['identity'].pop('logical_task')
        wrong['identity']['selected_child'] = 'audit-assess'
        raw = encode(wrong); Path(ready_pin['path']).write_bytes(raw)
        changed_pin = {**ready_pin, 'bytes': len(raw), 'sha256': sha(raw)}
        a, b, c = self.boundaries(context, plan, row, prefixes, helper)
        with a, b, c, self.assertRaises(ValueError):
            PARENT_READER.verified_ready(context, changed_pin, PROVIDER)

    def test_governed_parent_keeps_required_governor_gate(self):
        context, plan, row, prefixes, ready_pin, helper = self.fixture()
        context['path_kind'] = 'governed'
        with patch.object(PROVIDER, 'preflight', return_value=(plan, [], helper)), \
             patch.object(PROVIDER, 'require_governor_dispatch', side_effect=ValueError('GOVERNED_GATE_HELD')), \
             self.assertRaisesRegex(ValueError, 'GOVERNED_GATE_HELD'):
            PARENT_READER.verified_ready(context, ready_pin, PROVIDER)

    def test_actual_parent_cannot_ACK_other_mode_after_isolated_inspection(self):
        context, plan, row, prefixes, ready_pin, helper = self.fixture()
        a, b, c = self.boundaries(context, plan, row, prefixes, helper)
        with a, b, c:
            inspection = PARENT_READER.inspect_load(context, ready_pin, PROVIDER)
            text = normal_marker(row, ready_pin['sha256'])
            with Path(context['parent_rollout']).open('ab') as stream:
                stream.write(encode({'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant',
                    'channel': 'commentary', 'content': [{'type': 'output_text', 'text': text}]}}))
            with self.assertRaises(ValueError):
                PARENT_READER.acknowledge_load(context, ready_pin, inspection['inspection'], PROVIDER)
            self.assertFalse((Path(context['run']) / 'PARENT_VISIBILITY_ACK.json').exists())




class ParentCommentaryShapeTests(unittest.TestCase):
    # Break caught: admitting the wrong output phase, or rejecting current public
    # host commentary merely because it uses phase instead of legacy channel.
    setUp = IsolatedParentConsumerTests.setUp
    fixture = IsolatedParentConsumerTests.fixture
    boundaries = IsolatedParentConsumerTests.boundaries
    exercise = StagedAckTests.exercise

    def append_row(self, path, marker, labels, *, role='assistant', kind='message',
                   row_type='response_item', content=None):
        payload = {'type': kind, 'role': role,
            'content': [{'type': 'output_text', 'text': marker}] if content is None else content,
            'id': 'SYNTHETIC_MESSAGE', 'internal_chat_message_metadata_passthrough': None}
        payload.update(labels)
        raw = encode({'type': row_type, 'payload': payload})
        offset = path.stat().st_size
        with path.open('ab') as stream: stream.write(raw)
        return offset, raw

    def parser_case(self, labels, *, isolated=True, **kwargs):
        row = ready(isolated); digest = sha(encode(row))
        marker = SHARED.marker_for(row, digest)
        path = self.directory / 'parent-shape.jsonl'
        path.write_bytes(encode({'type': 'session_meta', 'payload': {'id': PARENT}}))
        offset, raw = self.append_row(path, marker, labels, **kwargs)
        ack = {'ready_sha256': digest, 'parent_row_offset': offset,
            'parent_row_bytes': len(raw), 'parent_row_sha256': sha(raw)}
        return row, digest, path, offset, raw, ack

    def test_current_legacy_and_agreeing_labels_reach_both_ACK_readers(self):
        for labels in ({'phase': 'commentary'}, {'channel': 'commentary'},
                       {'phase': 'commentary', 'channel': 'commentary'}):
            for isolated in (False, True):
                row, digest, path, offset, raw, ack = self.parser_case(labels, isolated=isolated)
                expected = {'path': str(path), 'offset': offset, 'bytes': len(raw), 'sha256': sha(raw)}
                for module in (PARENT_READER, NATIVE):
                    with self.subTest(labels=labels, isolated=isolated, consumer=module.__name__):
                        try: actual = module.verify_parent_ack(ack, row, digest, path, offset, offset)
                        except ValueError as exc: self.fail('Supported commentary shape refused: ' + str(exc))
                        self.assertEqual(actual, expected)

    def test_absent_wrong_null_or_conflicting_labels_refuse(self):
        rejected = [{}, {'phase': None}, {'channel': None}, {'phase': 'analysis'},
            {'phase': 'final_answer'}, {'channel': 'analysis'}, {'phase': 'Commentary'},
            {'phase': 'commentary', 'channel': 'analysis'},
            {'phase': 'analysis', 'channel': 'commentary'},
            {'phase': None, 'channel': 'commentary'}, {'phase': 'commentary', 'channel': None},
            {'phase': False, 'channel': 'commentary'}, {'phase': 'commentary', 'channel': 'commentary\n'}]
        for labels in rejected:
            for isolated in (False, True):
                row, digest, path, offset, raw, ack = self.parser_case(labels, isolated=isolated)
                for module in (PARENT_READER, NATIVE):
                    with self.subTest(labels=labels, isolated=isolated, consumer=module.__name__), self.assertRaises(ValueError):
                        module.verify_parent_ack(ack, row, digest, path, offset, offset)

    def test_current_shape_still_requires_assistant_response_message(self):
        for kwargs in ({'role': 'user'}, {'role': 'tool'}, {'role': 'system'},
                       {'kind': 'function_call_output'}, {'kind': 'reasoning'}, {'row_type': 'event_msg'}):
            row, digest, path, offset, raw, ack = self.parser_case({'phase': 'commentary'}, **kwargs)
            for module in (PARENT_READER, NATIVE):
                with self.subTest(kwargs=kwargs, consumer=module.__name__), self.assertRaises(ValueError):
                    module.verify_parent_ack(ack, row, digest, path, offset, offset)

    def test_current_shape_still_requires_exact_output_text_content(self):
        for content in ([], [{'type': 'output_text', 'text': 'not the marker'}],
                        [{'type': 'input_text', 'text': 'not the marker'}]):
            row, digest, path, offset, raw, ack = self.parser_case({'phase': 'commentary'}, content=content)
            for module in (PARENT_READER, NATIVE):
                with self.subTest(content=content, consumer=module.__name__), self.assertRaises(ValueError):
                    module.verify_parent_ack(ack, row, digest, path, offset, offset)

    def test_current_shape_rejects_historical_preinspection_duplicate_and_offset_mismatch(self):
        for case in ('historical', 'preinspection', 'duplicate', 'offset', 'bytes', 'row_digest', 'ready_digest', 'parent'):
            row, digest, path, offset, raw, ack = self.parser_case({'phase': 'commentary'})
            launch, floor = offset, offset
            if case == 'historical': launch = offset + len(raw)
            elif case == 'preinspection': floor = offset + 1
            elif case == 'duplicate':
                with path.open('ab') as stream: stream.write(raw)
            elif case == 'offset': ack['parent_row_offset'] += 1
            elif case == 'bytes': ack['parent_row_bytes'] -= 1
            elif case == 'row_digest': ack['parent_row_sha256'] = '0' * 64
            elif case == 'ready_digest': ack['ready_sha256'] = '0' * 64
            else:
                contents = path.read_bytes().splitlines(keepends=True)
                contents[0] = encode({'type': 'session_meta', 'payload': {'id': WORKER}})
                path.write_bytes(b''.join(contents))
            for module in (PARENT_READER, NATIVE):
                with self.subTest(case=case, consumer=module.__name__), self.assertRaises(ValueError):
                    module.verify_parent_ack(ack, row, digest, path, launch, floor)

    def test_current_shape_rejects_other_task_source_worker_and_READY(self):
        for case in ('task', 'source', 'worker', 'birth'):
            row, digest, path, offset, raw, ack = self.parser_case({'phase': 'commentary'})
            if case == 'task': row['identity']['logical_task'] = 'other_task'
            elif case == 'source': row['identity']['source_sha256'] = '9' * 64
            elif case == 'worker': row['worker_thread_id'] = PARENT
            else: row['process_identity']['creation_filetime_100ns'] += 1
            digest = sha(encode(row)); ack['ready_sha256'] = digest
            for module in (PARENT_READER, NATIVE):
                with self.subTest(case=case, consumer=module.__name__), self.assertRaises(ValueError):
                    module.verify_parent_ack(ack, row, digest, path, offset, offset)

    def test_parent_inspection_to_ACK_accepts_current_phase_only_shape(self):
        context, plan, row, prefixes, ready_pin, helper = self.fixture()
        a, b, c = self.boundaries(context, plan, row, prefixes, helper)
        with a, b, c:
            inspection = PARENT_READER.inspect_load(context, ready_pin, PROVIDER)
            self.append_row(Path(context['parent_rollout']), inspection['expected_announcement_text'], {'phase': 'commentary'})
            try: result = PARENT_READER.acknowledge_load(context, ready_pin, inspection['inspection'], PROVIDER)
            except ValueError as exc: self.fail('Actual host-shaped parent ACK refused: ' + str(exc))
            self.assertEqual(result['status'], 'ACTUAL_PARENT_ROW_BOUND_ACK_PUBLISHED')
            with self.assertRaises(ValueError):
                PARENT_READER.acknowledge_load(context, ready_pin, inspection['inspection'], PROVIDER)

    def test_native_staged_hold_accepts_current_phase_only_ACK(self):
        value, failure, requests, run = self.exercise(parent_labels={'phase': 'commentary'})
        self.assertIsNone(failure, 'Current host-shaped native ACK refused: ' + str(failure))
        self.assertEqual([(request['id'], request['params']['threadId']) for request in requests], [(5, WORKER), (6, WORKER)])
        self.assertEqual(value['status'], 'TWO_TURN_TRANSPORT_COMPLETE_NONVERDICT')

    def test_native_staged_hold_rejects_conflicting_labels(self):
        value, failure, requests, run = self.exercise(parent_labels={'phase': 'analysis', 'channel': 'commentary'})
        self.assertEqual(failure, 'Missing or duplicate truthful parent marker')
        self.assertEqual([request['id'] for request in requests], [5])
        self.assertFalse((run / 'RELEASE.json').exists())


class NormalIniConsumerTests(unittest.TestCase):
    setUp = MarkerAndAckTests.setUp

    def test_missing_or_alias_normal_logical_identity_refuses(self):
        for value in (None, '', 'bad\nTASK', WORKER, PARENT, 'audit-assess', 'audit-state', 'synthetic_run',
                      '1' * 64, '0123456789abcdef0123456789abcdef', '33333333-3333-4333-8333-333333333333'):
            row = ready(False)
            if value is None: row['identity'].pop('logical_task')
            else: row['identity']['logical_task'] = value
            for module in (SHARED, NATIVE):
                with self.subTest(value=value, module=module.__name__), self.assertRaises(ValueError):
                    module.marker_for(row, sha(encode(row)))

    def test_new_ini_marker_is_required_by_both_actual_ack_readers(self):
        row = ready(False); digest = sha(encode(row)); correct = normal_marker(row, digest)
        variants = [legacy_normal_marker(row, digest), correct.replace('```ini\n', '```text\n', 1),
            correct.replace('```ini\n', '```\n', 1), correct.replace('```ini\n', '', 1).replace('\n```\n', '\n', 1),
            correct.replace(NORMAL_LOGICAL, WORKER),
            correct.replace("I'm using the `" + NORMAL_LOGICAL + '` holon', "I'm using this ordinary child"),
            correct + '\n' + correct]
        for text in variants:
            path, offset, raw = fixture_parent(self.directory, text)
            ack = {'ready_sha256': digest, 'parent_row_offset': offset,
                'parent_row_bytes': len(raw), 'parent_row_sha256': sha(raw)}
            for module in (PARENT_READER, NATIVE):
                with self.subTest(module=module.__name__, text=text[:30]), self.assertRaises(ValueError):
                    module.verify_parent_ack(ack, row, digest, path, offset, offset)

    def open_case(self, *, logical=NORMAL_LOGICAL, requester='governor', existing_open=False):
        # Only canonical/Git/host read and write boundaries are substituted. The
        # real command, field binding and visible producer execute on owned data.
        child_path = self.directory / 'synthetic-child.md'; child_raw = b'SYNTHETIC_ONLY_CHILD\n'
        child_path.write_bytes(child_raw)
        source_digests = {}
        for name in ('SKILL.md', 'resolve-internal-skill.py'):
            raw = ('SYNTHETIC_ONLY_PACKAGE ' + name + '\n').encode()
            (self.directory / name).write_bytes(raw)
            source_digests[name] = ROUTE.bytes_identity(raw)['digest']
        old = {'decision': 'REQUIRED', 'route_state': 'UNSATISFIED', 'child_lifecycle_owned': False,
            'route_transaction_id': 'sha256:' + 'a' * 64, 'obligation_id': 'sha256:' + 'b' * 64,
            'host_session_id': PARENT,
            'package': {'source_digests': source_digests},
            'action': {'argv': ['route-trigger', 'IMMUTABLE_INDEPENDENT_REVIEW']},
            'child_source': {'identity': str(child_path), 'digest': ROUTE.bytes_identity(child_raw)['digest']}}
        if existing_open:
            old.update(route_state='OPEN', child_lifecycle_owned=True, lifecycle={'state': 'OPEN'})
        args = argparse.Namespace(recovery_capsule=None, request='SYNTHETIC_REQUEST', packet='SYNTHETIC_PACKET',
            controller='synthetic_controller', expected_record='1' * 40, route_transaction_id=old['route_transaction_id'],
            requester_identity=requester, writer_key=[], dependency_key=[], logical_task=logical)
        saved = []
        def cas(repo, controller, previous, record, *rest, **kwargs):
            saved.append(copy.deepcopy(record))
            return '2' * 40, {**copy.deepcopy(record), 'record_identity': ROUTE.digest_json(record)}
        def child_delivery(child, *, expected_identity_inputs):
            if child != 'audit-assess' or expected_identity_inputs != source_digests:
                raise ValueError('Synthetic delivery received foreign child/package custody')
            return child_raw, child_path
        patches = {
            'repo_context': lambda: (self.directory, 'SYNTHETIC', str(self.directory)),
            'read_request': lambda path: {'SYNTHETIC_ONLY': True},
            'namespace_gate': lambda common: contextlib.nullcontext(),
            'current_ref': lambda *a, **kw: ('1' * 40, old),
            'validate_route_currentness': lambda *a: ({}, {}, 'fingerprint'),
            'read_route_packet': lambda *a, **kw: (b'SYNTHETIC_PACKET', {'source_event': {}}),
            'validate_source_event_binding': lambda *a: None,
            'post_compaction_recovery_capsule': lambda *a: None,
            'child_delivery_bytes': child_delivery,
            'admit_transaction_child': lambda *a: {'admission_identity': 'SYNTHETIC_ADMISSION'},
            'cas_route_record': cas, 'post_route_currentness': lambda *a: None,
        }
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.ExitStack() as stack:
            for name, value in patches.items(): stack.enter_context(patch.object(ROUTE, name, value))
            stack.enter_context(contextlib.redirect_stdout(stdout)); stack.enter_context(contextlib.redirect_stderr(stderr))
            try: ROUTE.command_open(args); failure = None
            except (SystemExit, ValueError) as exc: failure = exc
        return old, saved, stderr.getvalue(), failure

    def test_new_open_binds_chosen_logical_name_and_emits_unverified_selection(self):
        old, saved, text, failure = self.open_case()
        self.assertIsNone(failure)
        self.assertEqual(saved[0]['lifecycle'].get('logical_task'), NORMAL_LOGICAL)
        self.assertNotIn('logical_task', old)
        self.assertEqual(text, '```ini\nCHILD_TASK=' + NORMAL_LOGICAL + '\nCHILD_TASK_KIND=GOVERNED_CHILD_SKILL\n'
            'CHILD_SKILL_SELECTED=audit-assess\nSTATUS=OPEN\nLOAD=UNVERIFIED\n```\n'
            "I'm opening the `" + NORMAL_LOGICAL + '` holon for the `audit-assess` skill '
            'to independently assess the exact immutable review packet.\n')
        self.assertNotIn('CHILD_SKILL_ROUTE=', text)

    def test_missing_name_or_non_governor_stops_before_open_cas(self):
        for kwargs in ({'logical': None}, {'logical': ''}, {'logical': 'audit-assess'}, {'logical': 'audit-state'},
                       {'logical': '1' * 64}, {'logical': '33333333-3333-4333-8333-333333333333'}, {'requester': 'child'}):
            old, saved, text, failure = self.open_case(**kwargs)
            with self.subTest(kwargs=kwargs):
                self.assertIsNotNone(failure); self.assertEqual(saved, [])

    def test_existing_open_without_logical_name_is_not_backfilled(self):
        old, saved, text, failure = self.open_case(existing_open=True)
        self.assertIsNotNone(failure); self.assertEqual(saved, [])
        self.assertNotIn('logical_task', old['lifecycle'])

    def request(self, presentation=True):
        value = {'schema': ROUTE.REQUEST_SCHEMA, 'predicate_version': ROUTE.PREDICATE_VERSION,
            'boundary': {'kind': 'synthetic', 'event_id': 'synthetic-boundary', 'digest': 'sha256:' + '1' * 64},
            'scope': {'identity': 'synthetic-frontier', 'digest': 'sha256:' + '2' * 64},
            'action': {'identity': 'synthetic-action', 'digest': 'sha256:' + '3' * 64,
                       'class': 'PURE_BOUNDED_READ_OR_VALIDATION', 'argv': ['route-read-snapshot']},
            'inputs': [{'identity': 'synthetic-input', 'path': 'synthetic.md', 'digest': 'sha256:' + '4' * 64}]}
        if presentation: value['presentation'] = {'parent_holon': 'synthetic-parent-holon', 'consuming_frontier': 'synthetic consuming frontier'}
        return value

    def test_nochild_presentation_is_validated_in_existing_request_carrier(self):
        value = self.request()
        try: actual = ROUTE.validate_request(value)
        except SystemExit as exc: self.fail('Required bound presentation carrier unsupported: ' + str(exc))
        self.assertEqual(actual['presentation'], value['presentation'])
        # Historical request data stays readable and gains no missing fields.
        legacy = self.request(False); self.assertEqual(ROUTE.validate_request(legacy), legacy)
        self.assertNotIn('presentation', legacy)

    def test_nochild_missing_or_injected_names_refuse(self):
        for presentation in ({}, {'parent_holon': 'x'}, {'parent_holon': 'x\nSTATUS=PASS', 'consuming_frontier': 'f'},
                             {'parent_holon': 'x', 'consuming_frontier': 'f', 'extra': True}):
            value = self.request(); value['presentation'] = presentation
            with self.subTest(presentation=presentation), self.assertRaises(SystemExit): ROUTE.validate_request(value)

    def test_record_request_reconstruction_retains_bound_nochild_presentation(self):
        request = self.request(); record = {**request, 'inputs': [{**request['inputs'][0], 'status': 'CURRENT'}]}
        self.assertEqual(ROUTE.candidate_request_from_record(record, require_current_inputs=True), request)

    def test_actual_nochild_command_returns_canonical_presentation_with_its_ini(self):
        request = self.request()
        record = {**request, 'schema': ROUTE.RECORD_SCHEMA,
            'inputs': [{**request['inputs'][0], 'status': 'CURRENT'}],
            'decision': 'NOT_REQUIRED', 'classification': 'MECHANICALLY_NOT_REQUIRED',
            'record_identity': 'sha256:' + '5' * 64, 'route_state': None}
        validated = {'record': record, 'oid': '1' * 40, 'current': {'explicit_run_root': 'synthetic_run'},
            'current_not_required': True, 'current_satisfied': False, 'obligation_id': None,
            'route_transaction_id': None, 'history_query': None}
        args = argparse.Namespace(controller='synthetic_controller')
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(ROUTE, 'repo_context', return_value=(self.directory, 'SYNTHETIC', str(self.directory))), \
             patch.object(ROUTE, 'namespace_gate', return_value=contextlib.nullcontext()), \
             patch.object(ROUTE, 'current_ref', return_value=('1' * 40, record)), \
             patch.object(ROUTE, 'validate_canonical_route_record_bytes'), \
             patch.object(ROUTE, 'validate_current_result', return_value=validated), \
             patch.object(ROUTE, 'projection_status', return_value='SYNTHETIC_ONLY'), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            ROUTE.command_admit_current(args)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload['presentation'], request['presentation'])
        self.assertEqual(stderr.getvalue(), ROUTE.no_child_notice(record['presentation']) + '\n')
        binding = {'controller_id': 'synthetic_controller', 'host_session_id': PARENT,
            'binding_generation': 'G0001', 'repository_identity': str(self.directory)}
        result = types.SimpleNamespace(returncode=0, stdout=stdout.getvalue(), stderr=stderr.getvalue())
        with patch.object(INTERLOCK, 'run', return_value=result):
            self.assertEqual(INTERLOCK.current_route(self.directory, binding, self.directory / 'route.py'), payload)

    def test_nochild_ini_producer_and_existing_stop_consumer_agree(self):
        presentation = self.request()['presentation']
        expected = ('```ini\nPARENT_HOLON=synthetic-parent-holon\nCONSUMING_FRONTIER=synthetic consuming frontier\n'
            'CHILD_SKILL_ROUTE=NOT_REQUIRED\n```\nThe `synthetic-parent-holon` parent uses no internal child at '
            '`synthetic consuming frontier` because the exact current R0033 route is NOT_REQUIRED.')
        self.assertEqual(ROUTE.no_child_notice(presentation), expected)
        binding = {'controller_id': 'synthetic_controller', 'host_session_id': PARENT,
            'binding_generation': 'G0001', 'repository_identity': str(self.directory)}
        payload = {'status': 'CURRENT', 'decision': 'NOT_REQUIRED', 'presentation': presentation}
        result = types.SimpleNamespace(returncode=0, stdout=json.dumps(payload) + '\n', stderr=expected + '\n')
        with patch.object(INTERLOCK, 'run', return_value=result):
            try: observed = INTERLOCK.current_route(self.directory, binding, self.directory / 'route.py')
            except INTERLOCK.InterlockUnavailable as exc: self.fail('Bound no-child INI refused: ' + str(exc))
        self.assertEqual(observed, payload)
        legacy = 'CHILD_SKILL_ROUTE=NOT_REQUIRED\nNo internal child is used because the exact current R0033 route is NOT_REQUIRED.\n'
        for invalid in (legacy, '', expected.replace('```ini\n', '```text\n') + '\n',
                        expected.replace('```ini\n', '```\n') + '\n', expected.replace('synthetic-parent-holon', 'wrong-parent') + '\n'):
            result.stderr = invalid
            with patch.object(INTERLOCK, 'run', return_value=result), self.subTest(notice=invalid[:25]), self.assertRaises(INTERLOCK.InterlockUnavailable):
                INTERLOCK.current_route(self.directory, binding, self.directory / 'route.py')

    def dispatch_case(self, *, caller_name=NORMAL_LOGICAL, canonical_name=NORMAL_LOGICAL, denied=None):
        child_path = self.directory / 'dispatch-child.md'; child_raw = b'SYNTHETIC_ONLY_CHILD\n'; child_path.write_bytes(child_raw)
        envelope = self.directory / 'dispatch-packet.json'; packet_raw = b'SYNTHETIC_ONLY_PACKET\n'; envelope.write_bytes(packet_raw)
        transcript = SOURCE / 'skills/implementaudit/references/transcript-contract.md'
        record = {'schema': ROUTE.RECORD_SCHEMA, 'decision': 'REQUIRED', 'route_state': 'OPEN',
            'host_session_id': PARENT, 'route_transaction_id': 'sha256:' + 'a' * 64,
            'obligation_id': 'sha256:' + 'b' * 64,
            'action': {'argv': ['route-trigger', 'IMMUTABLE_INDEPENDENT_REVIEW']},
            'lifecycle': {'state': 'OPEN', 'logical_task': canonical_name, 'child_return': None,
                'governor_decision': None, 'execution_evidence': None,
                'delivery': {'packet': ROUTE.bytes_identity(packet_raw),
                             'child': {'identity': str(child_path), **ROUTE.bytes_identity(child_raw)}}}}
        if canonical_name is None: record['lifecycle'].pop('logical_task')
        identity = {'selected_child': 'audit-assess', 'logical_task': caller_name, 'parent_thread_id': PARENT,
            'transaction_ref': record['route_transaction_id'], 'reason': 'check the selected source delivery',
            'source_sha256': sha(child_raw)}
        context = {'identity': identity, 'parent_rollout': str(self.directory / 'parent.jsonl'), 'parent_launch_offset': 0}
        plan = {'visibility': copy.deepcopy(context),
            'governor_dispatch': {'repository': str(self.directory), 'controller': 'synthetic_controller',
                'store': str(self.directory), 'host_id': 'codex', 'host_session_id': PARENT, 'binding_generation': 'G0001',
                'request': 'SYNTHETIC_REQUEST', 'packet': str(envelope), 'route_transaction_id': record['route_transaction_id'],
                'expected_record': '1' * 40},
            'binding': {'load_pins': {'child_source': {'path': str(child_path), 'bytes': len(child_raw), 'sha256': sha(child_raw)},
                'frozen_open_envelope': {'path': str(envelope)},
                'shared_transcript_contract': {'path': str(transcript), 'sha256': sha(transcript.read_bytes())}}}}
        calls = []
        def guard(name, value=None):
            def invoke(*args, **kwargs):
                calls.append(name)
                if denied == name: raise ValueError('SYNTHETIC_' + name)
                return value
            return invoke
        owner = types.SimpleNamespace(RECOVERY_RECORD_SCHEMA=ROUTE.RECOVERY_RECORD_SCHEMA,
            git=guard('git_read', str(self.directory)), current_ref=guard('current_ref', ('1' * 40, record)),
            validate_canonical_route_record_bytes=guard('canonical_record'), mapped_child_route=ROUTE.mapped_child_route,
            open_logical_task=ROUTE.open_logical_task, read_request=guard('request', {}),
            read_route_packet=guard('packet', (packet_raw, {'source_event': {}})), bytes_identity=ROUTE.bytes_identity,
            child_delivery_bytes=guard('resolver', (child_raw, child_path)),
            validate_route_currentness=guard('currentness', ({}, {}, 'fingerprint')),
            validate_source_event_binding=guard('source_event'), post_route_currentness=guard('post_currentness'))
        with patch.object(PROVIDER, 'route_owner', return_value=owner):
            return PROVIDER.require_governor_dispatch(context, plan), calls, record

    def test_native_identity_is_reconstructed_from_canonical_open_not_caller_assertion(self):
        result, calls, record = self.dispatch_case()
        self.assertEqual(result['identity']['logical_task'], NORMAL_LOGICAL)
        self.assertEqual(result['identity']['logical_task'], record['lifecycle']['logical_task'])
        self.assertIn('canonical_record', calls); self.assertIn('currentness', calls); self.assertIn('post_currentness', calls)
        with self.assertRaises((ValueError, SystemExit)):
            self.dispatch_case(caller_name='different_caller_name')
        with self.assertRaises((ValueError, SystemExit)):
            self.dispatch_case(canonical_name=None)

    def test_normal_identity_addition_does_not_bypass_existing_owner_guards(self):
        for guard in ('canonical_record', 'packet', 'resolver', 'currentness', 'source_event', 'post_currentness'):
            with self.subTest(guard=guard), self.assertRaisesRegex(ValueError, 'SYNTHETIC_' + guard):
                self.dispatch_case(denied=guard)

    def test_lifecycle_history_preserves_logical_name_without_backfill(self):
        for legacy, changed in ((False, False), (True, False), (False, True), (True, True)):
            lifecycle = {'state': 'OPEN', 'required_record_oid': '1' * 40, 'child_return': None,
                'governor_decision': None, 'governor_decision_count': 0, 'source_event_status': 'active', 'execution_evidence': None}
            if not legacy: lifecycle['logical_task'] = NORMAL_LOGICAL
            predecessor = {'route_state': 'OPEN', 'predecessor_record_oid': '1' * 40, 'lifecycle': lifecycle}
            predecessor['record_identity'] = ROUTE.digest_json(predecessor)
            current = {'route_state': 'RETURNED', 'predecessor_record_oid': '2' * 40,
                'lifecycle': {**lifecycle, 'state': 'RETURNED', 'child_return': {'SYNTHETIC_ONLY': True}}}
            if changed: current['lifecycle']['logical_task'] = 'changed_or_backfilled_name'
            current['record_identity'] = ROUTE.digest_json(current)
            with patch.object(ROUTE, 'git_blob_bytes', return_value=encode(predecessor)):
                if changed:
                    with self.subTest(legacy=legacy), self.assertRaises(SystemExit):
                        ROUTE.validate_lifecycle_predecessor_chain(self.directory, '3' * 40, current)
                else:
                    ROUTE.validate_lifecycle_predecessor_chain(self.directory, '3' * 40, current)


def main():
    global SOURCE, WORK, SHARED, NATIVE, PARENT_READER, PROVIDER, ROUTE, INTERLOCK
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    args = parser.parse_args()
    SOURCE, WORK = args.source.resolve(), args.work_dir.resolve()
    WORK.mkdir(parents=True, exist_ok=False)
    scripts = SOURCE / 'skills/implementaudit/scripts'
    SHARED = load(scripts / 'child-load-visibility.py', 'tested_shared')
    NATIVE = load(scripts / 'native-capture-adapter/load_visibility.py', 'tested_native')
    PARENT_READER = load(scripts / 'child-parent-visibility.py', 'tested_parent')
    PROVIDER = load(scripts / 'native-worker-capture.py', 'tested_provider')
    ROUTE = load(scripts / 'route-transaction.py', 'tested_route')
    INTERLOCK = load(scripts / 'host-stop-interlock.py', 'tested_interlock')
    def forbid(event, args):
        if event in ('subprocess.Popen', 'os.system', 'os.spawn', 'ctypes.dlopen'):
            raise AssertionError('Native/process/job operation forbidden in relay regressions')
    sys.addaudithook(forbid)
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls)
        for cls in (MarkerAndAckTests, PrefixAndModeTests, StagedAckTests, IsolatedParentConsumerTests, ParentCommentaryShapeTests, NormalIniConsumerTests))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    log = stream.getvalue()
    (WORK / 'TEST.log').write_text(log, encoding='utf8')
    record = {'source': str(SOURCE), 'tests': result.testsRun, 'failures': len(result.failures),
        'errors': len(result.errors), 'successful': result.wasSuccessful(),
        'test_sha256': sha(Path(__file__).read_bytes()), 'native_executed': False,
        'synthetic_only': True, 'source_or_runtime_admission': False}
    (WORK / 'RESULTS.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf8')
    print(json.dumps(record))
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    raise SystemExit(main())
