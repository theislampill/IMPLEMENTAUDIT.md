#!/usr/bin/env python3
"""C02 mechanics only: constructed owner evidence is not authentic entitlement.

The production resolver is deliberately unavailable. Only this isolated fixture
substitutes its source locator; real claim-run refs and Git CAS remain in use.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import unittest
from unittest import mock

import claim_transaction_test as transaction_tests

CONTROLLER = transaction_tests.CONTROLLER


class CorrectionPublication(unittest.TestCase):
    rotate = transaction_tests.TransactionControls.rotate

    def setUp(self):
        transaction_tests.TransactionControls.setUp(self)
        self.seed_correction()

    def seed_correction(self):
        self.rotate()
        self.joined = self.owner.require_current_generation_join_v1(self.context)
        event = self.fixture.claim('--invalidate-continuity', CONTROLLER,
                                   '--boundary', 'inferred-context-gap', '--event', 'fixture-erroneous-event')
        self.assertEqual(event.returncode, 0, event.stderr.decode())
        self.event_token = event.stdout.decode().strip()
        self.observed = {
            'schema': 'implementaudit.c02-observation.v1',
            **{key: self.context[key] for key in ('controller', 'claim_id', 'run_root_identity')},
            'pointer_oid': self.joined['pointer_oid'], 'marker_oid': self.joined['marker_oid'],
            'receipt_oid': self.joined['receipt_token'].split('@')[1],
            'invalidation_oid': self.event_token.split('@')[1],
            'event_id': 'fixture-erroneous-event', 'boundary': 'inferred-context-gap',
            'later_boundaries': []}
        self.grant = {
            'schema': 'implementaudit.c02-issuer-grant.v1', 'issuer': 'fixture-only-issuer',
            'scope': {key: self.observed[key] for key in ('controller', 'claim_id', 'run_root_identity',
                     'pointer_oid', 'receipt_oid', 'marker_oid', 'invalidation_oid', 'event_id')},
            'kind': 'ERRONEOUS_INVALIDATION', 'effect': 'APPEND_ONLY_NO_CURRENTNESS',
            'code_sha256': hashlib.sha256(self.fixture.scripts.joinpath('claim-run-rotation.py').read_bytes()).hexdigest(),
            'revoked': False}
        self.decision = {'schema': 'implementaudit.c02-decision-proposal.v1',
            'issuer': self.grant['issuer'], 'grant_sha256': self.digest(self.grant),
            'evidence_sha256': '7' * 64, 'kind': 'ERRONEOUS_INVALIDATION',
            'observation_sha256': self.digest(self.observed)}
        self.decision['decision_id'] = self.digest(self.decision)
        self.source = {'schema': 'implementaudit.c02-owner-snapshot.v1',
            'source_owner': 'fixture-only-source-owner', 'source_cutoff': 'fixture-source-cutoff-1',
            'ordering': 'SOURCE_OWNER_COMPLETE_SEQUENCE', 'census_complete': True,
            'erroneous_event': {key: self.observed[key] for key in ('event_id', 'invalidation_oid', 'boundary')},
            'later_boundaries': [], 'prior_decisions': [], 'grant': self.grant}
        # This locator is fixture custody, never a new production source owner.
        self.source_ref = f'refs/implementaudit/state-archives/{CONTROLLER}/c02-fixture-source'
        self.grant_ref = f'refs/implementaudit/state-archives/{CONTROLLER}/c02-fixture-grant'
        self.write_source()

    def digest(self, value):
        return hashlib.sha256(self.owner.canonical(value)).hexdigest()

    def write_source(self):
        self.write_grant(self.source['grant'])
        oid = self.fixture.blob(self.owner.canonical(self.source))
        old = self.owner.read_ref(self.fixture.repo, self.source_ref)
        self.fixture.git('update-ref', self.source_ref, oid, old or '0' * 40)
        return oid

    def write_grant(self, grant):
        oid = self.fixture.blob(self.owner.canonical(grant))
        old = self.owner.read_ref(self.fixture.repo, self.grant_ref)
        self.fixture.git('update-ref', self.grant_ref, oid, old or '0' * 40)
        return oid

    def resolver(self, context, request):
        self.assertEqual(request['invalidation_token'], self.event_token)
        self.assertEqual(request['decision_id'], self.decision['decision_id'])
        return {'ref': self.source_ref, 'oid': self.owner.read_ref(self.fixture.repo, self.source_ref),
                'grant_ref': self.grant_ref, 'grant_oid': self.owner.read_ref(self.fixture.repo, self.grant_ref)}

    def required(self):
        for name in ('prepare_c02_correction_v1', 'publish_c02_correction_v1'):
            self.assertTrue(callable(getattr(self.owner, name, None)), 'missing bounded C02 mechanic: ' + name)

    def prepare(self):
        self.required()
        return self.owner.prepare_c02_correction_v1(self.context, self.event_token, self.decision)

    def publish(self, prepared=None):
        self.required()
        return self.owner.publish_c02_correction_v1(self.context, prepared or self.prepare())

    def fixture_owner(self):
        return mock.patch.object(self.owner, '_resolve_c02_source_owner_v1', side_effect=self.resolver, create=True)

    def refs(self):
        return self.fixture.git('for-each-ref', '--format=%(refname) %(objectname)')

    def test_first_append_retains_original_and_record_without_currentness(self):
        before = self.owner.authorities(self.context)
        with self.fixture_owner():
            refs = self.refs()
            prepared = self.prepare()
            self.assertEqual(prepared['authority_ceiling'], 'INERT_PREPARATION_NO_EFFECT_AUTHORITY')
            self.assertEqual(self.refs(), refs)
            result = self.publish(prepared)
        self.assertEqual(result['status'], 'APPENDED_NO_CURRENTNESS')
        record = self.owner.decode_json(self.owner.read_blob(self.fixture.repo, result['record_oid']))
        self.assertEqual(record['observation'], self.observed)
        self.assertEqual(record['decision'], self.decision)
        for oid in (result['record_oid'], self.observed['invalidation_oid']):
            self.owner.require_anchor(self.context, oid)
        self.assertEqual(self.owner.authorities(self.context), before)
        with self.assertRaisesRegex(self.owner.RotationError, 'stale'):
            self.owner.require_current_generation_join_v1(self.context)

    def test_exact_retry_is_no_effect_and_conflicting_replay_refuses(self):
        with self.fixture_owner():
            first = self.publish()
            before = self.refs()
            retry = self.publish()
            self.assertEqual(retry['record_oid'], first['record_oid'])
            self.assertEqual(retry['status'], 'EXACT_RETRY_NO_EFFECT')
            self.assertEqual(self.refs(), before)
            self.decision['evidence_sha256'] = '8' * 64
            self.decision.pop('decision_id')
            self.decision['decision_id'] = self.digest(self.decision)
            with self.assertRaisesRegex(self.owner.RotationError, 'conflicting|replay'):
                self.publish()
            self.assertEqual(self.refs(), before)

    def test_conflicting_decision_kind_cannot_relabel_native_resume(self):
        self.decision['kind'] = 'ORDINARY_RESUME'
        self.decision.pop('decision_id')
        self.decision['decision_id'] = self.digest(self.decision)
        before = self.refs()
        with self.fixture_owner(), self.assertRaises(self.owner.RotationError):
            self.publish()
        self.assertEqual(self.refs(), before)

    def test_production_has_no_resolver_and_caller_hash_is_not_entitlement(self):
        self.required()
        before = self.refs()
        with self.assertRaisesRegex(self.owner.RotationError, 'source.owner.*unavailable'):
            self.prepare()
        self.assertEqual(self.refs(), before)

    def test_missing_revoked_wrong_scope_code_and_hash_grants_refuse(self):
        original = copy.deepcopy(self.source)
        changes = [('missing', None), ('revoked', {'revoked': True}),
                   ('scope', {'scope': dict(self.grant['scope'], event_id='another-event')}),
                   ('code', {'code_sha256': '9' * 64}), ('issuer', {'issuer': 'another-issuer'})]
        with self.fixture_owner():
            for name, change in changes:
                with self.subTest(name=name):
                    self.source = copy.deepcopy(original)
                    self.source['grant'] = None if change is None else dict(self.source['grant'], **change)
                    # Keep the caller's grant hash and proposal self-consistent:
                    # rejecting this must test entitlement, not merely hashing.
                    self.decision['grant_sha256'] = self.digest(self.source['grant'])
                    self.decision.pop('decision_id')
                    self.decision['decision_id'] = self.digest(self.decision)
                    self.write_source()
                    before = self.refs()
                    with self.assertRaises(self.owner.RotationError):
                        self.publish()
                    self.assertEqual(self.refs(), before)

    def test_unknown_or_incomplete_source_census_is_never_empty_absence(self):
        original = copy.deepcopy(self.source)
        with self.fixture_owner():
            for change in ({'census_complete': False}, {'ordering': 'UNKNOWN'}, {'source_cutoff': ''},
                           {'later_boundaries': None}, {'prior_decisions': None}):
                with self.subTest(change=change):
                    self.source = dict(copy.deepcopy(original), **change)
                    self.write_source()
                    before = self.refs()
                    with self.assertRaises(self.owner.RotationError):
                        self.publish()
                    self.assertEqual(self.refs(), before)

    def newer(self, event):
        result = self.fixture.claim('--invalidate-continuity', CONTROLLER,
                                    '--boundary', 'new-session', '--event', event)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        return result.stdout.decode().strip().split('@')[1]

    def test_newer_boundary_before_publication_preempts_without_lost_event(self):
        with self.fixture_owner():
            prepared = self.prepare()
            newer = self.newer('genuine-newer-before-correction')
            with self.assertRaises(self.owner.RotationError):
                self.publish(prepared)
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context['invalidation_ref']), newer)
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.anchor_ref(self.context, prepared['record_oid'])))

    def test_newer_boundary_during_cas_is_admitted_and_preempts_correction(self):
        original = self.owner.update_refs
        seen = []
        def preempt(context, updates, guards, **kwargs):
            seen.append(self.newer('genuine-newer-at-correction-cas'))
            return original(context, updates, guards, **kwargs)
        with self.fixture_owner():
            prepared = self.prepare()
            with mock.patch.object(self.owner, 'update_refs', side_effect=preempt):
                with self.assertRaises(self.owner.CASFailure):
                    self.publish(prepared)
        self.assertEqual(len(seen), 1)
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context['invalidation_ref']), seen[0])
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.anchor_ref(self.context, prepared['record_oid'])))

    def test_census_revision_alone_at_cas_is_fenced(self):
        original = self.owner.update_refs
        grant_oid = self.owner.read_ref(self.fixture.repo, self.grant_ref)
        def advance_census(context, updates, guards, **kwargs):
            self.source['source_cutoff'] = 'fixture-source-cutoff-advanced-at-cas'
            self.write_source()
            return original(context, updates, guards, **kwargs)
        with self.fixture_owner():
            prepared = self.prepare()
            with mock.patch.object(self.owner, 'update_refs', side_effect=advance_census):
                with self.assertRaises(self.owner.CASFailure):
                    self.publish(prepared)
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.grant_ref), grant_oid)
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.anchor_ref(self.context, prepared['record_oid'])))

    def test_independent_issuer_revocation_at_cas_is_fenced(self):
        original = self.owner.update_refs
        source_oid = self.owner.read_ref(self.fixture.repo, self.source_ref)
        def revoke(context, updates, guards, **kwargs):
            self.write_grant(dict(self.source['grant'], revoked=True))
            return original(context, updates, guards, **kwargs)
        with self.fixture_owner():
            prepared = self.prepare()
            with mock.patch.object(self.owner, 'update_refs', side_effect=revoke):
                with self.assertRaises(self.owner.CASFailure):
                    self.publish(prepared)
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.source_ref), source_oid)
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.anchor_ref(self.context, prepared['record_oid'])))

    def test_changed_expected_old_and_tampered_preparation_refuse(self):
        with self.fixture_owner():
            prepared = self.prepare()
            tampered = copy.deepcopy(prepared)
            tampered['record']['expected_old']['receipt_oid'] = '9' * 40
            before = self.refs()
            with self.assertRaises(self.owner.CASFailure):
                self.publish(tampered)
            self.assertEqual(self.refs(), before)
            tuples = [(role, self.context[role + '_ref']) for role in ('controller', 'pointer', 'marker')]
            tuples.append(('receipt', self.joined['receipt_token'].split('@')[0]))
            for role, ref in tuples:
                with self.subTest(role=role):
                    old = self.owner.read_ref(self.fixture.repo, ref)
                    replacement = self.fixture.blob(b'fixture wrong expected-old')
                    self.fixture.git('update-ref', ref, replacement, old)
                    try:
                        with self.assertRaises(self.owner.RotationError):
                            self.publish(prepared)
                    finally:
                        self.fixture.git('update-ref', ref, old, replacement)
            self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.anchor_ref(self.context, prepared['record_oid'])))

    def test_append_unknown_result_is_resolved_by_exact_readback(self):
        original = self.owner.git_process
        injected = []
        def unknown(repo, *args, **kwargs):
            result = original(repo, *args, **kwargs)
            if args[:3] == ('update-ref', '--stdin', '-z'):
                injected.append(True)
                raise self.owner.RotationError('fixture transport lost after Git commit')
            return result
        with self.fixture_owner(), mock.patch.object(self.owner, 'git_process', side_effect=unknown):
            result = self.publish()
        self.assertEqual(injected, [True])
        self.assertEqual(result['status'], 'APPENDED_NO_CURRENTNESS')
        self.owner.require_anchor(self.context, result['record_oid'])

    def test_unknown_nonlanded_append_refuses_until_explicit_retry(self):
        original = self.owner.git_process
        def unknown(repo, *args, **kwargs):
            if args[:3] == ('update-ref', '--stdin', '-z'):
                raise self.owner.RotationError('fixture transport lost before Git commit')
            return original(repo, *args, **kwargs)
        with self.fixture_owner():
            prepared = self.prepare()
            with mock.patch.object(self.owner, 'git_process', side_effect=unknown):
                with self.assertRaises(self.owner.CASFailure):
                    self.publish(prepared)
            self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.anchor_ref(self.context, prepared['record_oid'])))
            self.assertEqual(self.publish(prepared)['status'], 'APPENDED_NO_CURRENTNESS')

    def test_crash_before_or_after_append_reconciles_without_duplicate(self):
        original = self.owner.update_refs
        with self.fixture_owner():
            prepared = self.prepare()
            with mock.patch.object(self.owner, 'update_refs', side_effect=KeyboardInterrupt('fixture before append')):
                with self.assertRaises(KeyboardInterrupt):
                    self.publish(prepared)
            self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.anchor_ref(self.context, prepared['record_oid'])))
            def crash(context, updates, guards, **kwargs):
                original(context, updates, guards, **kwargs)
                raise KeyboardInterrupt('fixture after append')
            with mock.patch.object(self.owner, 'update_refs', side_effect=crash):
                with self.assertRaises(KeyboardInterrupt):
                    self.publish(prepared)
            before = self.refs()
            self.assertEqual(self.publish()['status'], 'EXACT_RETRY_NO_EFFECT')
            self.assertEqual(self.refs(), before)


class FreshCorrection(unittest.TestCase):
    """Explicit fresh-transition stimuli; the real production issuer is absent."""
    rotate = transaction_tests.RealHelperIntegration.rotate
    digest = CorrectionPublication.digest
    write_source = CorrectionPublication.write_source
    write_grant = CorrectionPublication.write_grant
    resolver = CorrectionPublication.resolver
    fixture_owner = CorrectionPublication.fixture_owner
    refs = CorrectionPublication.refs
    newer = CorrectionPublication.newer
    prepare = CorrectionPublication.prepare
    publish = CorrectionPublication.publish
    required = CorrectionPublication.required

    def setUp(self):
        path = transaction_tests.POST / 'claim-run-rotation.py'
        spec = importlib.util.spec_from_file_location('c02_api_red_probe', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(callable(getattr(module, 'run_c02_correction_v1', None)),
                        'missing distinct C02 fresh-transition mechanic')
        transaction_tests.RealHelperIntegration.setUp(self)
        CorrectionPublication.seed_correction(self)
        with self.fixture_owner():
            self.appended = self.publish()
        self.correction_oid = self.appended['record_oid']
        self.correction = self.owner.decode_json(self.owner.read_blob(self.fixture.repo, self.correction_oid))

    def fresh_grant(self):
        scope = {key: self.correction['expected_old'][key] for key in
                 ('controller', 'claim_id', 'run_root_identity', 'controller_oid', 'pointer_oid', 'receipt_oid', 'marker_oid')}
        scope.update(correction_record_oid=self.correction_oid,
                     corrected_invalidation_oid=self.observed['invalidation_oid'],
                     projection_generation_id='G0003', continuity_epoch='G0003',
                     source_cutoff='fixture-source-cutoff-2')
        self.source.update(source_cutoff=scope['source_cutoff'],
            prior_decisions=[{'observation': self.observed, 'decision': self.decision}],
            grant={'schema': 'implementaudit.c02-fresh-transition-grant.v1',
                'issuer': 'fixture-only-issuer', 'scope': scope, 'effect': 'C02_FRESH_TRANSITION',
                'code_sha256': hashlib.sha256(self.fixture.scripts.joinpath('claim-run-rotation.py').read_bytes()).hexdigest(),
                'projection_code_sha256': hashlib.sha256(self.fixture.scripts.joinpath('rotate-canonical-state.py').read_bytes()).hexdigest(),
                'revoked': False})
        self.write_source()

    def transition(self):
        return self.owner.run_c02_correction_v1(self.context, self.correction_oid)

    def test_append_only_grant_cannot_restore_currentness(self):
        before = self.refs()
        with self.fixture_owner(), self.assertRaises(self.owner.RotationError):
            self.transition()
        self.assertEqual(self.refs(), before)
        with self.assertRaises(self.owner.RotationError):
            self.owner.require_current_generation_join_v1(self.context)

    def test_distinct_fresh_transition_preserves_payload_and_original_receipt_shape(self):
        self.fresh_grant()
        with self.fixture_owner():
            result = self.transition()
            before = self.refs()
            retry = self.transition()
        self.assertEqual(result['status'], 'CORRECTED_FRESH')
        self.assertEqual(retry['status'], 'ALREADY_CORRECTED')
        self.assertEqual(self.refs(), before)
        joined = self.owner.require_current_generation_join_v1(self.context)
        self.assertEqual(joined['receipt_token'], result['receipt_token'])
        self.assertEqual(joined['pointer']['continuity_epoch'], 'G0003')
        self.assertEqual(joined['pointer']['projection_schema'], 'implementaudit.protected-projection.v2')
        self.assertEqual(joined['pointer']['predecessor_receipt_ref_oid'], self.joined['receipt_token'])
        self.assertEqual(joined['marker_oid'], self.joined['marker_oid'])
        self.assertNotEqual(joined['pointer']['invalidation_oid'], self.observed['invalidation_oid'])
        self.assertEqual(joined['protected_manifest']['PRESERVED_PAYLOAD']['payload'],
                         self.joined['protected_manifest']['PRESERVED_PAYLOAD']['payload'])
        raw = self.owner.read_blob(self.fixture.repo, result['receipt_token'].split('@')[1])
        self.assertEqual(len(raw.rstrip(b'\n').split(b'\t')), 14)
        epoch, _ = self.owner.read_epoch(self.context, 'G0003')
        self.assertEqual(epoch['schema'], 'implementaudit.c02-correction-epoch.v1')
        self.assertEqual(epoch['transition']['transition_kind'], 'c02-correction')
        self.assertEqual(epoch['transition']['boundary'], 'erroneous-invalidation-correction')
        self.assertEqual(epoch['c02_admission']['correction_record_oid'], self.correction_oid)
        self.owner.require_anchor(self.context, self.observed['invalidation_oid'])
        self.owner.require_anchor(self.context, self.correction_oid)
        native = self.fixture.claim('--invalidate-continuity', CONTROLLER,
                                    '--boundary', 'erroneous-invalidation-correction', '--event', 'forged-c02')
        self.assertNotEqual(native.returncode, 0)

    def test_fresh_grant_revocation_scope_code_and_missing_prior_census_refuse(self):
        self.fresh_grant()
        original = copy.deepcopy(self.source)
        changes = [('revoked', {'revoked': True}), ('scope', {'scope': dict(original['grant']['scope'], continuity_epoch='G0004')}),
                   ('code', {'projection_code_sha256': '9' * 64}), ('missing', None)]
        with self.fixture_owner():
            for name, change in changes:
                with self.subTest(name=name):
                    self.source = copy.deepcopy(original)
                    self.source['grant'] = None if change is None else dict(self.source['grant'], **change)
                    self.write_source()
                    before = self.refs()
                    with self.assertRaises(self.owner.RotationError):
                        self.transition()
                    self.assertEqual(self.refs(), before)
            self.source = dict(copy.deepcopy(original), prior_decisions=[])
            self.write_source()
            before = self.refs()
            with self.assertRaises(self.owner.RotationError):
                self.transition()
            self.assertEqual(self.refs(), before)

    def test_newer_boundary_during_retry_grant_resolution_refuses_stale_result(self):
        self.fresh_grant()
        with self.fixture_owner():
            completed = self.transition()
        seen = []
        def preempt(context, request):
            if not seen:
                seen.append(self.newer('genuine-newer-during-c02-exact-retry'))
            return self.resolver(context, request)
        with mock.patch.object(self.owner, '_resolve_c02_source_owner_v1', side_effect=preempt):
            with self.assertRaises(self.owner.RotationError):
                self.transition()
        self.assertEqual(len(seen), 1)
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context['invalidation_ref']), seen[0])
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context['pointer_ref']), completed['pointer_token'].split('@')[1])
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.epoch_ref(self.context, 'G0004')))

    def test_newer_boundary_at_allocation_preempts_without_relabeling(self):
        self.fresh_grant()
        original = self.owner.update_refs
        seen = []
        def preempt(context, updates, guards, **kwargs):
            if self.owner.epoch_ref(context, 'G0003') in updates:
                seen.append(self.newer('genuine-newer-before-c02-allocation'))
            return original(context, updates, guards, **kwargs)
        with self.fixture_owner(), mock.patch.object(self.owner, 'update_refs', side_effect=preempt):
            with self.assertRaises(self.owner.RotationError):
                self.transition()
        self.assertEqual(len(seen), 1)
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context['invalidation_ref']), seen[0])
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.epoch_ref(self.context, 'G0003')))

    def test_newer_boundary_at_pointer_cas_preempts_without_compensation(self):
        self.fresh_grant()
        original = self.owner.update_refs
        seen = []
        def preempt(context, updates, guards, **kwargs):
            if context['pointer_ref'] in updates:
                seen.append(self.newer('genuine-newer-during-c02-pointer-cas'))
            return original(context, updates, guards, **kwargs)
        with self.fixture_owner(), mock.patch.object(self.owner, 'update_refs', side_effect=preempt):
            with self.assertRaises(self.owner.RotationError):
                self.transition()
        self.assertEqual(len(seen), 1)
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context['invalidation_ref']), seen[0])
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context['pointer_ref']), self.observed['pointer_oid'])
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.receipt_ref(self.context, 'G0003')))
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.epoch_ref(self.context, 'G0004')))

    def test_live_grant_revision_is_fenced_again_at_pointer_publication(self):
        self.fresh_grant()
        original = self.owner.update_refs
        seen = []
        def revoke(context, updates, guards, **kwargs):
            if context['pointer_ref'] in updates:
                seen.append(self.write_grant(dict(self.source['grant'], revoked=True)))
            return original(context, updates, guards, **kwargs)
        with self.fixture_owner(), mock.patch.object(self.owner, 'update_refs', side_effect=revoke):
            with self.assertRaises(self.owner.RotationError):
                self.transition()
        self.assertEqual(len(seen), 1)
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context['pointer_ref']), self.observed['pointer_oid'])
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.receipt_ref(self.context, 'G0003')))


if __name__ == '__main__':
    unittest.main()
