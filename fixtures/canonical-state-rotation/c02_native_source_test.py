#!/usr/bin/env python3
"""Portable C02 source controls; constructed native admission is not qualification.

The repository's actual source owner, claim owner, retained files and Git CAS
execute. The initial JOIN and native source fence are explicitly constructed.
No host/model process, issuer grant, production ref or private task artifact is
used. Windows kernel/cancellation qualification belongs to separate controls.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / 'skills/implementaudit/scripts'
SOURCE = ROOT / 'source-peers/native-runtime/skills/implementaudit/scripts/compaction-source-owner-codex-app.py'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class ConstructedLedger:
    """Deterministic source edge, never a native producer capability."""
    def acquire(self, source):
        return types.SimpleNamespace(thread_id='constructed-session', turn_id='constructed-turn',
            verify=lambda: None, checkpoint=lambda: ('CONSTRUCTED_SOURCE_FENCE', 1))


class NativeSourceControls(unittest.TestCase):
    def setUp(self):
        self.source_owner = load(SOURCE, 'c02_source_' + uuid.uuid4().hex)
        self.assertTrue(callable(getattr(self.source_owner.OwnedStdioC02CensusV1, 'census_facts_v1', None)),
                        'existing source fact-only census is missing')
        # Optional test containment directory; no host/profile/config selection.
        chosen = os.environ.get('R0039_C02_TEST_TMPDIR')
        parent = Path(chosen or tempfile.gettempdir()).resolve(strict=True)
        self.temp = tempfile.TemporaryDirectory(prefix='ia-c02-', dir=parent)
        self.repo = Path(self.temp.name).resolve(strict=True)
        def cleanup():
            self.assertEqual(Path(self.temp.name).resolve(strict=True), self.repo)
            self.assertEqual(self.repo.parent, parent)
            self.temp.cleanup()
        self.addCleanup(cleanup)
        self.scripts = self.repo / 'skills/implementaudit/scripts'
        self.scripts.mkdir(parents=True)
        for name in ('claim-run.sh', 'claim-run-rotation.py', 'rotate-canonical-state.py',
                     'canonical_hot_projection.py', 'canonical_custody.py'):
            shutil.copyfile(SCRIPTS / name, self.scripts / name)
            self.assertEqual((self.scripts / name).read_bytes(), (SCRIPTS / name).read_bytes())
        self.owner = load(self.scripts / 'claim-run-rotation.py', 'c02_claim_' + uuid.uuid4().hex)
        self.owner.git(self.repo, 'init', '-q')
        run = self.repo / '.IMPLEMENTAUDIT/runs/controlled-abc123'
        run.mkdir(parents=True)
        (run / '.claimed').write_bytes(b'CONSTRUCTED_CUSTODY_INPUT_NOT_NATIVE_ADMISSION\n')
        self.context = {'repo': self.repo, 'run_root': run, 'controller': 'c02-native-control',
            'claim_id': '1' * 32, 'run_root_identity': '.IMPLEMENTAUDIT/runs/controlled-abc123'}
        for kind, namespace in (('controller', 'controllers'), ('pointer', 'current-generations'),
                ('marker', 'current-generation-migrations'), ('invalidation', 'continuity-invalidations')):
            self.context[kind + '_ref'] = 'refs/implementaudit/' + namespace + '/' + self.context['controller']
        controller = ('implementaudit.controller-current.v1\t' + self.context['controller'] + '\t' +
                      self.context['claim_id'] + '\t' + str(run) + '\n').encode()
        self.context['controller_oid'] = self.blob(controller)
        invalidation = ('\t'.join(('implementaudit.continuity-invalidation.v1', self.context['controller'],
            self.context['controller_oid'], self.context['claim_id'], 'new-session', 'constructed-initial-event')) + '\n').encode()
        initial = {'controller': self.context['controller_oid'],
            'pointer': self.blob(b'CONSTRUCTED_POINTER_BLOB_NOT_A_NATIVE_JOIN\n'),
            'marker': self.blob(b'CONSTRUCTED_MARKER_BLOB_NOT_A_NATIVE_JOIN\n'),
            'invalidation': self.blob(invalidation)}
        for role, oid in initial.items():
            self.owner.git(self.repo, 'update-ref', self.context[role + '_ref'], oid, '0' * 40)
            self.owner.git(self.repo, 'update-ref', self.owner.anchor_ref(self.context, oid), oid, '0' * 40)
        self.initial = self.owner.managed(self.context)
        self.selected = {'profile_id': self.source_owner.OWNED_STDIO_PROFILE,
            'root_thread_id': 'constructed-session',
            'pending_owner': {'owner_id': 'CONSTRUCTED_EXISTING_SOURCE_OWNER', 'session_id': 'constructed-session'}}
        self.source = self.source_owner.OwnedStdioC02CensusV1(
            self.selected, self.owner, self.context, ConstructedLedger())
        joined = {'pointer_oid': initial['pointer'], 'marker_oid': initial['marker'],
                  'pointer': {'invalidation_oid': initial['invalidation']}}
        with mock.patch.object(self.owner, 'require_current_generation_join_v1', return_value=joined):
            self.source.arm({'c02_terminal_fence': {'session_id': 'constructed-session',
                'turn_id': 'constructed-turn', 'source_sha256': '9' * 64, 'source_bytes': 123}})
        # Explicit test admission only. The production injection API, not this
        # fixture, owns _fault_inflight and its accepted event callback.
        self.source._production_binding = self.source_owner._C02_SOURCE_BINDING_SEAL_V1
        self.transactions, self.guard_reads = [], []
        self.invalidation_calls = 0

    def blob(self, raw):
        return self.owner.git(self.repo, 'hash-object', '-w', '--stdin', input_bytes=raw).decode().strip()

    def refs(self):
        return self.owner.git(self.repo, 'for-each-ref', '--format=%(refname) %(objectname)').decode()

    @contextlib.contextmanager
    def instrument(self, *, cancel_after_git=False):
        owner, source = self.owner, self.source
        real_git = owner.git_process
        real_verified = owner._NativePublicationInputs.verified_ref_guards_v1
        real_invalidator = owner.invalidate_current_generation_v1
        def verified(observation):
            self.assertIsInstance(observation, owner._NativePublicationInputs)
            self.assertIsInstance(observation.retained, owner.RetainedInputs)
            self.assertEqual([pin.path for pin, _ in observation.retained.items],
                             owner.retained_owner_paths(self.context))
            value = real_verified(observation)
            self.assertEqual(value, owner.owner_guards(self.context, self.initial, exclude=('invalidation',)))
            self.assertTrue(value)
            self.guard_reads.append(dict(value))
            return value
        def git_process(repo, *args, **kwargs):
            result = real_git(repo, *args, **kwargs)
            if args == ('update-ref', '--stdin', '-z'):
                self.transactions.append((kwargs['input_bytes'], result.returncode))
                if cancel_after_git and result.returncode == 0:
                    source.cancel_now()
            return result
        def invalidate(*args, **kwargs):
            self.invalidation_calls += 1
            return real_invalidator(*args, **kwargs)
        with mock.patch.object(owner._NativePublicationInputs, 'verified_ref_guards_v1', verified), \
             mock.patch.object(owner, 'git_process', git_process), \
             mock.patch.object(owner, 'invalidate_current_generation_v1', invalidate):
            yield

    def test_real_injection_and_fact_only_census_preserve_issuer_boundary(self):
        with self.instrument():
            token = self.source.inject_controlled_fault('constructed-engineered-new-session')
        oid = self.owner.exact_authority_token(self.context, 'invalidation', token)
        self.assertEqual(self.source._original, oid)
        self.assertNotEqual(oid, self.initial['invalidation'])
        self.assertEqual(self.owner.managed(self.context), dict(self.initial, invalidation=oid))
        self.assertEqual(self.invalidation_calls, 1)
        self.assertEqual(len(self.guard_reads), 1)
        self.assertEqual(len(self.transactions), 1)
        transaction, returncode = self.transactions[0]
        self.assertEqual(returncode, 0)
        for ref, old in self.guard_reads[0].items():
            self.assertIn(b'verify ' + ref.encode() + b'\0' + old.encode() + b'\0', transaction)
        self.assertIn(b'update ' + self.context['invalidation_ref'].encode() + b'\0' + oid.encode() +
                      b'\0' + self.initial['invalidation'].encode() + b'\0', transaction)
        interval = self.source.census_facts_v1()
        self.assertEqual(interval['source_owner'], self.selected['pending_owner']['owner_id'])
        self.assertEqual(interval['subject'], {key: self.context[key] for key in
            ('controller', 'claim_id', 'run_root_identity')})
        self.assertEqual(interval['events'], [{'sequence': 1, 'kind': 'native-boundary',
            'event_id': 'constructed-engineered-new-session', 'invalidation_oid': oid, 'boundary': 'new-session'}])
        self.assertEqual(interval['covered_boundary_kinds'], sorted(self.owner.BOUNDARIES))
        self.assertTrue(interval['complete'] and interval['covers_adjudications'])
        self.assertEqual((interval['interval_start'], interval['interval_end']), (1, 1))
        self.assertEqual(interval['source_cutoff'], self.source.source_cutoff)
        self.assertNotIn('grant', interval)
        self.assertNotIn('c02_adjudication', self.selected)
        for configured in (None, {'census_owner': 'CONSTRUCTED_FOREIGN_OWNER'}):
            self.selected['c02_adjudication'] = configured
            with self.subTest(configured=configured), self.assertRaisesRegex(ValueError, 'CONFIGURED_CENSUS_OWNER_MISMATCH'):
                self.source.census({})
        self.selected['c02_adjudication'] = {'census_owner': interval['source_owner']}
        self.assertEqual(self.source.census({}), interval)
        with self.assertRaisesRegex(ValueError, 'OWNER_ROUTE_NOT_SELECTED'):
            self.source_owner.ConfiguredC02IssuerV1(None, interval['subject'])
        self.assertFalse(self.source._cancelled.is_set() or self.source._fault_inflight)

    def test_changed_expected_old_refuses_before_transaction(self):
        replacement = self.blob(b'constructed-preempting-pointer\n')
        self.owner.git(self.repo, 'update-ref', self.context['pointer_ref'], replacement, self.initial['pointer'])
        before = self.refs()
        with self.instrument(), self.assertRaisesRegex(ValueError, 'OUTCOME_UNKNOWN_READBACK_REQUIRED'):
            self.source.inject_controlled_fault('constructed-preempted-injection')
        self.assertEqual(self.refs(), before)
        self.assertEqual(self.invalidation_calls, 1)
        self.assertFalse(self.transactions)
        self.assertTrue(self.source._cancelled.is_set())
        self.assertIsNone(self.source._original)

    def test_cancelled_source_refuses_before_invalidator(self):
        before = self.refs()
        self.source.cancel_now()
        with self.instrument(), self.assertRaisesRegex(ValueError, 'OUTCOME_UNKNOWN_READBACK_REQUIRED'):
            self.source.inject_controlled_fault('constructed-cancelled-injection')
        self.assertEqual(self.refs(), before)
        self.assertEqual(self.invalidation_calls, 0)
        self.assertFalse(self.transactions)
        self.assertIsNone(self.source._original)

    def test_post_commit_cancellation_preserves_unknown_effect(self):
        with self.instrument(cancel_after_git=True), self.assertRaisesRegex(ValueError, 'OUTCOME_UNKNOWN_READBACK_REQUIRED'):
            self.source.inject_controlled_fault('constructed-commit-then-cancel')
        after = self.owner.managed(self.context)
        self.assertNotEqual(after['invalidation'], self.initial['invalidation'])
        self.assertEqual(len(self.guard_reads), 1)
        self.assertEqual(len(self.transactions), 1)
        self.assertTrue(self.source._cancelled.is_set())
        self.assertIsNone(self.source._original)
        self.assertEqual(self.owner.invalidation_record(self.context, after['invalidation'])['event'],
                         'constructed-commit-then-cancel')

    def test_existing_event_cannot_be_reclassified_as_controlled(self):
        before = self.refs()
        event = self.owner.invalidation_record(self.context, self.initial['invalidation'])['event']
        with self.instrument(), \
             mock.patch.object(self.owner, 'write_blob', side_effect=AssertionError('WRITE_BLOCKED')) as writes, \
             mock.patch.object(self.owner, 'update_refs', side_effect=AssertionError('TRANSACTION_BLOCKED')) as updates:
            with self.assertRaisesRegex(ValueError, 'OUTCOME_UNKNOWN_READBACK_REQUIRED'):
                self.source.inject_controlled_fault(event)
            self.assertEqual(writes.call_count, 0)
            self.assertEqual(updates.call_count, 0)
        self.assertEqual(self.refs(), before)
        self.assertEqual(self.invalidation_calls, 1)  # Ordinary exact retry remains legal.
        self.assertFalse(self.guard_reads or self.transactions)
        self.assertTrue(self.source._cancelled.is_set())
        self.assertFalse(self.source._fault_inflight)
        self.assertIsNone(self.source._original)
        self.assertEqual(self.source._events, [])
        with self.assertRaisesRegex(ValueError, 'C02_LIVE_INTERVAL_UNAVAILABLE'):
            self.source.census_facts_v1()

    def test_fact_census_refuses_absent_event_or_source_admission(self):
        before = self.refs()
        with self.assertRaisesRegex(ValueError, 'EXACT_CONTROLLED_EVENT_NOT_OBSERVED'):
            self.source.census_facts_v1()
        self.source._production_binding = None
        with self.assertRaisesRegex(ValueError, 'SELECTED_LIVE_SOURCE_REQUIRED'):
            self.source.census_facts_v1()
        self.assertEqual(self.refs(), before)

    def test_fact_census_refuses_unobserved_adjudication(self):
        with self.instrument():
            self.source.inject_controlled_fault('constructed-census-injection')
        before = self.refs()
        # Failure stimulus only: a newly reported decision outside the source's
        # observed callback history. No grant or correction record is created.
        with mock.patch.object(self.owner, '_c02_retained_decisions_v1', return_value=([({}, '6' * 40)], {})):
            with self.assertRaisesRegex(ValueError, 'UNOBSERVED_OWNER_ADJUDICATION'):
                self.source.census_facts_v1()
        self.assertEqual(self.refs(), before)


class CorrectionScopeControls(unittest.TestCase):
    def setUp(self):
        self.owner = load(SCRIPTS / 'claim-run-rotation.py', 'c02_scope_' + uuid.uuid4().hex)
        self.observed = {'schema': 'implementaudit.c02-observation.v1', 'controller': 'qualification',
            'claim_id': '1' * 32, 'run_root_identity': '.IMPLEMENTAUDIT/runs/test-abc123',
            'pointer_oid': '2' * 40, 'receipt_oid': '3' * 40, 'marker_oid': '4' * 40,
            'invalidation_oid': '5' * 40, 'event_id': 'constructed-erroneous-event',
            'boundary': 'new-session', 'later_boundaries': []}
        self.context = {key: self.observed[key] for key in ('controller', 'claim_id', 'run_root_identity')}
        expected = {key: self.observed[key] for key in ('controller', 'claim_id', 'run_root_identity',
                    'pointer_oid', 'receipt_oid', 'marker_oid', 'invalidation_oid')}
        expected.update(controller_oid='a' * 40, receipt_ref='refs/implementaudit/continuity-receipts/qualification/G0002')
        self.correction = {'expected_old': expected}
        self.predecessor = dict(self.context, controller_oid=expected['controller_oid'],
            pointer_oid=expected['pointer_oid'], receipt_oid=expected['receipt_oid'], receipt_ref=expected['receipt_ref'],
            migration_marker_oid=expected['marker_oid'], receipt_schema=self.owner.RECEIPT_SCHEMA,
            invalidation_oid='8' * 40, projection_generation_id='G0002', continuity_epoch='G0002')

    def test_existing_correction_wire_has_no_authority_and_exact_plus_one_scope(self):
        decision = {'schema': 'implementaudit.c02-decision-proposal.v1', 'issuer': 'CONSTRUCTED_OWNER',
            'grant_sha256': '6' * 64, 'evidence_sha256': '7' * 64, 'kind': 'ERRONEOUS_INVALIDATION',
            'observation_sha256': hashlib.sha256(self.owner.canonical(self.observed)).hexdigest()}
        decision['decision_id'] = hashlib.sha256(self.owner.canonical(decision)).hexdigest()
        proposal = self.owner.propose_c02_correction_v1(self.observed, decision, [])
        self.assertEqual(proposal['status'], 'OWNER_ADMISSION_REQUIRED')
        self.assertEqual(proposal['authority_ceiling'], 'NO_EFFECT_AUTHORITY')
        scope = self.owner._c02_fresh_grant_scope_v1(self.context, self.correction, 'b' * 40,
            self.predecessor, 'CONSTRUCTED_SOURCE_CUTOFF')
        self.assertEqual(scope['projection_generation_id'], 'G0003')
        self.assertEqual(scope['continuity_epoch'], 'G0003')
        self.assertEqual(scope['correction_record_oid'], 'b' * 40)
        self.assertEqual(scope['corrected_invalidation_oid'], self.observed['invalidation_oid'])
        self.assertEqual(scope['source_cutoff'], 'CONSTRUCTED_SOURCE_CUTOFF')

    def test_wrong_predecessor_and_exhausted_generation_refuse(self):
        for change in ({'migration_marker_oid': 'b' * 40}, {'projection_generation_id': 'GFFFF'}):
            predecessor = dict(self.predecessor, **change)
            with self.subTest(change=change), self.assertRaises(self.owner.RotationError):
                self.owner._c02_fresh_grant_scope_v1(self.context, self.correction, 'c' * 40,
                    predecessor, 'CONSTRUCTED_SOURCE_CUTOFF')


if __name__ == '__main__':
    unittest.main(verbosity=2)
