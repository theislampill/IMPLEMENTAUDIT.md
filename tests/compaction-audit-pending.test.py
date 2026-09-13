#!/usr/bin/env python3
"""Actual isolated hook/pending-owner behavior; no live host or campaign custody."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(os.environ.get('IMPLEMENTAUDIT_F01_SOURCE_ROOT', Path(__file__).resolve().parents[1])).resolve()
SCRIPTS = ROOT / 'skills/implementaudit/scripts'


class PendingAuditTests(unittest.TestCase):
    def setUp(self):
        parent = Path(os.environ['IMPLEMENTAUDIT_TEST_ROOT']).resolve(strict=True)
        self.root = Path(tempfile.mkdtemp(prefix='pending-', dir=parent))
        self.assertTrue(self.root.is_relative_to(parent))
        self.data = self.root / 'plugin-data'
        self.store = self.data / 'host-session-binding-v1'
        self.repo = self.root / 'target'
        self.repo.mkdir()
        self.runroot = self.repo / 'run'; self.runroot.mkdir()
        self.common = self.repo / '.git'; self.common.mkdir()
        self.env = dict(os.environ, PLUGIN_DATA=str(self.data), PLUGIN_ROOT=str(ROOT),
                        PYTHONDONTWRITEBYTECODE='1')
        self.session = 'source-session-a'
        self.home = self.root / 'codex-home'; (self.home / 'sessions').mkdir(parents=True)
        self.env['CODEX_HOME'] = str(self.home)
        self.task = 'source-task-a'
        self.transcript = self.home / 'sessions/rollout-source-task-a.jsonl'
        self.ordinal = 0
        self.append('session_meta', {'id': self.task, 'session_id': self.session, 'cli_version': '0.153.4'})
        self.core('init', '--owner-id', 'host-owner')
        self.core('bind', '--owner-id', 'host-owner', '--host-id', 'codex',
                  '--host-session-id', self.session, '--controller-id', 'fixture-controller',
                  '--claim-id', 'fixture-claim', '--explicit-run-root', str(self.runroot),
                  '--repository-identity', str(self.repo), '--git-common-directory-identity', str(self.common),
                  '--worktree-identity', str(self.repo), '--activation-event-id', 'activation-a',
                  '--activation-receipt', 'activation-receipt-a', '--continuity-generation', 'G0001',
                  '--continuity-receipt', 'refs/implementaudit/continuity-receipts/fixture-controller/G0001@' + '1'*40)

    def execute(self, script, *args, payload=None, ok=True):
        completed = subprocess.run([sys.executable, '-I', '-S', '-B', str(SCRIPTS / script), *args],
            input=json.dumps(payload) if payload is not None else None, text=True,
            capture_output=True, cwd=self.repo, env=self.env, timeout=20)
        if ok:
            self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
            self.assertEqual(completed.stderr, '')
        return completed

    def core(self, *args):
        return json.loads(self.execute('host-session-binding.py', '--store', str(self.store), *args).stdout)

    def hook(self, **extra):
        # Execute the real compact main and real H0/pending owner, stopping at
        # the downstream currentness seam before any Git/native process.
        spec = importlib.util.spec_from_file_location('cold_compact_hook', SCRIPTS / 'codex-compact-interlock.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        payload = {
            'hook_event_name': 'SessionStart', 'source': 'compact', 'session_id': self.session,
            'cwd': 'C:/ignored/foreign', 'transcript_path': 'C:/ignored/foreign.jsonl', **extra}
        stdin = io.TextIOWrapper(io.BytesIO(json.dumps(payload).encode()), encoding='utf-8')
        stdout = io.StringIO()
        with mock.patch.dict(os.environ, self.env, clear=True), mock.patch.object(sys, 'stdin', stdin), \
             mock.patch.object(sys, 'stdout', stdout), mock.patch.object(module, 'validate_live_controller',
                 side_effect=module.InterlockUnavailable('Cold fixture downstream currentness refusal')), \
             mock.patch.object(module, 'validate_event', side_effect=AssertionError('Unexpected downstream native action')), \
             mock.patch.object(module, 'invalidate', side_effect=AssertionError('Unexpected downstream invalidation')):
            self.assertEqual(module.main(), 0)
        return json.loads(stdout.getvalue())

    def append(self, kind, payload):
        row = {'timestamp': '2026-09-10T00:00:00Z', 'ordinal': self.ordinal, 'type': kind, 'payload': payload}
        self.ordinal += 1
        with self.transcript.open('ab') as stream:
            stream.write((json.dumps(row, separators=(',', ':')) + '\n').encode())

    def compact(self, turn='turn-a'):
        self.append('compacted', {'message': 'fixture summary excluded from receipts'})
        self.append('turn_context', {'turn_id': turn})

    def pending(self, action, request=None, ok=True):
        completed = self.execute('compaction-audit-pending.py', '--store', str(self.store),
            '--session', self.session, '--owner-id', 'host-owner', action, payload=request, ok=ok)
        if not ok:
            self.assertNotEqual(completed.returncode, 0, completed.stdout)
            return completed
        return json.loads(completed.stdout)

    def register(self, **changes):
        raw = self.transcript.read_bytes()
        request = {'task_id': self.task, 'transcript': str(self.transcript),
                   'expected_bytes': len(raw), 'expected_sha256': hashlib.sha256(raw).hexdigest()}
        request.update(changes)
        return self.pending('register-source', request)

    def reserve(self, child='child-a'):
        return self.pending('reserve', {'child_id': child})

    def observe(self, child='child-a'):
        return self.pending('observe-child', {'child_id': child})

    def returned(self, observation, child='child-a', status='SUCCEEDED', **changes):
        value = {'child_id': child, 'observation_id': observation['observation_id'],
                 'status': status, 'currentness': 'UNRESOLVED', 'measured_epoch': 'UNRESOLVED',
                 'frontier': 'Bounded fixture reconciliation; no canonical authority.'}
        value.update(changes)
        return self.pending('return', value)

    def join(self, result, child='child-a', ok=True):
        return self.pending('join', {'child_id': child, 'return_digest': result['return_digest']}, ok=ok)

    def of_kind(self, scope, kind):
        return [item for item in scope if item['kind'] == kind]

    def test_currentness_failure_cannot_discard_pending_hook_signal(self):
        # Removing the pre-currentness durable observation must fail this test.
        result = self.hook()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIs(result.get('audit_state_required'), True)
        self.assertTrue(any(self.store.rglob('pending.json')), 'No durable pending audit receipt')
        self.assertFalse(any(self.common.rglob('*.used')), 'Native OPEN replay fence unexpectedly touched')



    def test_source_descriptor_dedup_does_not_correlate_repeated_hook_deliveries(self):
        self.compact(); self.register(); self.hook()
        first = self.pending('status'); self.register()
        self.assertEqual(first['pending'], self.pending('status')['pending'])
        self.hook(); second = self.pending('status')
        proved = self.of_kind(first['pending'], 'COMPLETED_RESUMED_BOUNDARY')
        self.assertEqual(len(proved), 1)
        self.assertEqual(proved, self.of_kind(second['pending'], 'COMPLETED_RESUMED_BOUNDARY'))
        unknown = self.of_kind(second['pending'], 'UNRESOLVED_SIGNAL')
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0]['version'], 2)
        one = self.reserve(); retry = self.reserve()
        self.assertEqual(one['assignment'], retry['assignment'])
        self.pending('reserve', {'child_id': 'competing'}, ok=False)




    def test_no_hook_fallback_still_requires_audit(self):
        self.compact(); self.register()
        decision = self.pending('resume')
        self.assertEqual(decision['decision'], 'AUDIT_STATE_REQUIRED')
        self.assertEqual(len(self.of_kind(decision['pending'], 'COMPLETED_RESUMED_BOUNDARY')), 1)
        self.assertEqual(len(self.of_kind(decision['pending'], 'UNRESOLVED_RESUME_OBSERVATION')), 1)
        self.assertEqual(decision['signal_observations'], 0)





    def test_observation_expansion_races_new_reservation_for_exact_b(self):
        self.compact(); self.register(); self.hook(); self.reserve(); self.observe()
        self.compact('turn-b'); self.hook()
        boundary_b = self.pending('status')['available_scope'][0]['id']
        base = [sys.executable, '-I', '-S', '-B', str(SCRIPTS / 'compaction-audit-pending.py'),
                '--store', str(self.store), '--session', self.session, '--owner-id', 'host-owner']
        procs = [subprocess.Popen(base + [action], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE, text=True, cwd=self.repo, env=self.env)
                 for action in ('observe-child', 'reserve')]
        for proc, child in zip(procs, ('child-a', 'child-b')):
            proc.stdin.write(json.dumps({'child_id': child})); proc.stdin.close(); proc.stdin = None
        output = [proc.communicate(timeout=20) for proc in procs]
        self.assertEqual(procs[0].returncode, 0, output)
        state = json.loads(next(self.store.rglob('pending.json')).read_bytes())
        owners = [name for name, item in state['assignments'].items()
                  if boundary_b in [scope['id'] for scope in item['scope']]]
        self.assertEqual(len(owners), 1, output)



    def test_status_or_boolean_cannot_be_verified_compaction_proof(self):
        self.pending('status', {'compacted': True}, ok=False)
        self.pending('resume', {'compacted': True}, ok=False)
        observation = self.pending('resume')
        state = json.loads(next(self.store.rglob('pending.json')).read_bytes())
        proof = state['observations'][observation['pending'][0]['id']]['proof']
        self.assertEqual(proof['occurrence_proof'], 'UNRESOLVED')
        self.assertIsNone(proof['logical_occurrence_count'])
        self.assertFalse(observation['canonical_currentness'])


    def test_duplicate_marker_representations_do_not_invent_two_occurrences(self):
        self.append('compacted', {'message': 'opaque'})
        self.append('response_item', {'type': 'context_compaction'})
        self.append('turn_context', {'turn_id': 'turn-a'})
        self.register(); self.hook()
        pending = self.pending('status')['pending']
        self.assertEqual(len(self.of_kind(pending, 'COMPLETED_RESUMED_BOUNDARY')), 1)
        self.assertEqual(len(self.of_kind(pending, 'UNRESOLVED_SIGNAL')), 1)
        self.assertEqual(len(pending), 2)

    def test_two_canonical_markers_without_separate_resumes_stay_ambiguous(self):
        self.append('compacted', {'message': 'opaque'})
        self.append('event_msg', {'type': 'context_compacted'})
        self.append('turn_context', {'turn_id': 'turn-a'})
        self.register()
        pending = self.pending('status')['pending']
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]['kind'], 'AMBIGUOUS_MARKER_GROUP')

    def test_source_hardlink_and_foreign_session_meta_are_refused(self):
        self.compact()
        raw = self.transcript.read_bytes()
        link = self.home / 'sessions/hardlink-copy.jsonl'
        os.link(self.transcript, link)
        request = {'task_id': self.task, 'transcript': str(self.transcript),
                   'expected_bytes': len(raw), 'expected_sha256': hashlib.sha256(raw).hexdigest()}
        refused = self.pending('register-source', request, ok=False)
        self.assertIn('SOURCE_FILE_KIND', refused.stdout)
        other = self.home / 'sessions/rollout-foreign-source-task-a.jsonl'
        foreign = raw.replace(b'source-session-a', b'source-session-b')
        other.write_bytes(foreign)
        request.update(transcript=str(other), expected_bytes=len(foreign),
                       expected_sha256=hashlib.sha256(foreign).hexdigest())
        refused = self.pending('register-source', request, ok=False)
        self.assertIn('SOURCE_SESSION_META', refused.stdout)

    def test_return_cannot_invent_observation_or_add_authority(self):
        self.compact(); self.register(); self.hook(); self.reserve(); self.observe()
        before = self.pending('status')['pending']
        request = {'child_id': 'child-a', 'observation_id': '0'*64, 'status': 'SUCCEEDED',
                   'currentness': 'UNRESOLVED', 'measured_epoch': 'UNRESOLVED', 'frontier': 'x'}
        refused = self.pending('return', request, ok=False)
        self.assertIn('RETURN_SHAPE_OR_AUTHORITY_CLAIM', refused.stdout)
        request['observation_id'] = self.observe()['observation_id']
        request['trusted'] = True
        refused = self.pending('return', request, ok=False)
        self.assertIn('RETURN_SHAPE_OR_AUTHORITY_CLAIM', refused.stdout)
        self.assertEqual(self.pending('status')['pending'], before)

    def test_provenance_refusals_keep_hook_obligation(self):
        self.compact(); raw = self.transcript.read_bytes()
        self.pending('register-source', {'task_id': self.task, 'transcript': str(self.transcript),
            'expected_bytes': len(raw), 'expected_sha256': '0'*64}, ok=False)
        forged = self.repo / self.transcript.name; forged.write_bytes(raw)
        self.pending('register-source', {'task_id': self.task, 'transcript': str(forged),
            'expected_bytes': len(raw), 'expected_sha256': hashlib.sha256(raw).hexdigest()}, ok=False)
        self.hook(); self.assertEqual(self.pending('status')['decision'], 'AUDIT_STATE_REQUIRED')
        self.register()
        self.transcript.write_bytes(raw.replace(b'source-session-a', b'source-session-b'))
        result = self.hook()
        self.assertTrue(result['audit_state_required'])
        self.assertTrue(self.pending('status')['source_problem'])

    def test_rewritten_prefix_partial_row_and_claimed_trust_are_refused(self):
        self.compact(); self.register(); self.hook()
        self.transcript.write_bytes(self.transcript.read_bytes() + b'{')
        self.assertTrue(self.pending('resume')['source_problem'])
        self.pending('register-source', {'trusted': True}, ok=False)
        self.reserve(); snapshot = self.observe()
        self.assertTrue(snapshot['source_problem'])




    def test_signal_completion_and_resume_remain_separate(self):
        self.register(); self.hook()
        self.assertEqual(self.pending('status')['pending'][0]['kind'], 'UNRESOLVED_SIGNAL')
        self.append('compacted', {'message': 'opaque'})
        self.assertNotIn('COMPLETED_RESUMED_BOUNDARY', [r['kind'] for r in self.pending('resume')['pending']])
        self.append('turn_context', {'turn_id': 'turn-a'})
        self.assertIn('COMPLETED_RESUMED_BOUNDARY', [r['kind'] for r in self.pending('resume')['pending']])







if __name__ == '__main__':
    # This existing package entrypoint runs the retained hook controls and the
    # actual-result replacements for obsolete caller-status success fixtures.
    spec = importlib.util.spec_from_file_location('actual_result_consumer_controls',
        Path(__file__).with_name('compaction-result-consumer.test.py'))
    actual = importlib.util.module_from_spec(spec); spec.loader.exec_module(actual)
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(PendingAuditTests),
        unittest.defaultTestLoader.loadTestsFromModule(actual)])
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if outcome.wasSuccessful() else 1)
