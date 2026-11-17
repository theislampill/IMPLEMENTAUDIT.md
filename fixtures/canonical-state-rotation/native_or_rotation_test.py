#!/usr/bin/env python3
"""Constructed owner-lease OR mechanics, with real offline source token counts.

These fixtures grant no genuine native health-only qualification or authority.
"""
import copy
from contextlib import contextmanager
import unittest
from unittest import mock

import token_admission_test as token_fixture
from archive_v2_test import M, git, transition
from native_input_adapter_test import binding, exact, reported_window, terminal


class NativeOrRotation(unittest.TestCase):
    def setUp(self):
        self.assertTrue(callable(getattr(M, 'full_or_calibration_contract_v1', None)),
                        'complete OR helper selection is absent')
        self.fixture = token_fixture.TokenAdmission('runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.encoding = self.fixture.encoding
        self.native = M.native_inputs_module_v1()
        self.now = 1792742165555
        self.clock = mock.patch.object(self.native.time, 'time_ns', return_value=self.now * 1000000).start()
        self.addCleanup(mock.patch.stopall)

    def subject(self, text='q ' * 22000):
        return self.fixture.subject(text)

    @contextmanager
    def observation(self, subject, used=193800, alter=None):
        predecessor = subject['predecessor']
        selected = binding()
        selected['subject'] = {key: predecessor[key] for key in
            ('controller', 'claim_id', 'run_root_identity', 'state_sha256', 'roadmap_sha256')}
        selected['subject']['receipt_token'] = predecessor['receipt_ref'] + '@' + predecessor['receipt_oid']
        selected['source_bytes'] = sum(map(len, subject['source']))
        selected['source_tokens'] = sum(M.count_rotation_tokens_v1(self.encoding, subject['source']))
        selected['budget_policy']['id'] = 'R0039-CONFIGURED-HEADROOM-v1'
        if alter:
            alter(selected)
        owner = self.native.NativeInputState(selected)
        owner.observe(exact(used)); owner.observe(reported_window(total=used)); owner.observe(terminal())
        with mock.patch.object(self.native, '_resolve_existing_owner_v1', return_value=owner):
            with self.native.rotation_input_lease_v1(selected['subject'], selected['source_bytes'],
                                                   selected['source_tokens']) as lease:
                yield lease, owner

    def prepare(self, subject, lease=None, calibration=None):
        return M.prepare_canonical_draft(subject['repo'], subject['run'],
            subject['predecessor']['controller'], 'G0002', subject['owner_map'], subject['predecessor'],
            calibration or M.full_or_calibration_contract_v1(), tokenizer_bytes=self.encoding,
            native_observation=lease)

    def test_constructed_health_only_archives_exact_input_and_keeps_historical_readable(self):
        subject = self.subject()
        with self.observation(subject) as (lease, owner):
            result = self.prepare(subject, lease)
            self.assertLess(result['measurement']['live_bytes_before'], 131072)
            self.assertLess(result['measurement']['live_tokens_before'], 32768)
            self.assertEqual(result['measurement']['triggered_by'], ['CONTEXT_HEALTH'])
            self.assertEqual(result['measurement']['context_health_bp'], 2500)
            self.assertGreaterEqual(result['measurement']['live_byte_reduction'], 32768)
            self.assertGreaterEqual(result['measurement']['live_token_reduction'], 8192)
            manifest, _, _ = M._checked_prepared(subject['repo'], subject['run'], result)
            self.assertEqual(manifest['native_input'], result['native_input'])
        # Historical verification has no freshness/admission authority. It must
        # still reconstruct old exact bytes after the current native lease ends.
        self.clock.return_value += 60000000000
        M._checked_prepared(subject['repo'], subject['run'], result)
        finalized = M.finalize_canonical_projection(subject['repo'], subject['run'], result,
                                                   transition(subject, result))
        M.read_canonical_generation(subject['repo'], subject['run'], finalized['pointer'])

    def test_one_token_above_headroom_boundary_has_no_archive_or_owner_map_read(self):
        subject = self.subject()
        subject['owner_map'].unlink()
        with self.observation(subject, used=193799) as (lease, owner):
            before = git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)')
            result = self.prepare(subject, lease)
            self.assertFalse(result['triggered'])
            self.assertEqual(result['context_health_bp'], 2501)
            self.assertEqual(result['archive_writes'], 0)
            self.assertEqual(before, git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)'))

    def test_missing_json_or_closed_unadmitted_lease_refuses_without_archive(self):
        subject = self.subject()
        with self.observation(subject) as (lease, owner):
            copied_json = lease.observation
            with mock.patch.object(self.native, '_resolve_existing_owner_v1',
                                   side_effect=self.native.NativeInputError('OWNER_UNAVAILABLE')):
                with self.assertRaises(M.RotationError):
                    self.prepare(subject, lease)
        before = git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)')
        for proposed in (None, copied_json, lease):
            with self.subTest(kind=type(proposed).__name__), self.assertRaises(M.RotationError):
                self.prepare(subject, proposed)
        self.assertEqual(before, git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)'))

    def test_opaque_lease_cannot_substitute_its_source_owner_binding(self):
        subject = self.subject()
        with self.observation(subject) as (lease, owner):
            lease._observation['host']['effective_config_sha256'] = 'f' * 64
            before = git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)')
            with self.assertRaises(M.RotationError):
                self.prepare(subject, lease)
            self.assertEqual(before, git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)'))

    def test_foreign_source_receipt_and_policy_refuse_before_archive(self):
        subject = self.subject()
        changes = [
            lambda value: value.__setitem__('source_bytes', value['source_bytes'] + 1),
            lambda value: value.__setitem__('source_tokens', value['source_tokens'] + 1),
            lambda value: value['subject'].__setitem__('state_sha256', 'a' * 64),
            lambda value: value['subject'].__setitem__('roadmap_sha256', 'b' * 64),
            lambda value: value['subject'].__setitem__('receipt_token', 'foreign-receipt'),
            lambda value: value['budget_policy'].__setitem__('configured_usable_tokens', 20000),
            lambda value: value['host'].__setitem__('model', 'foreign-model'),
        ]
        before = git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)')
        for index, alter in enumerate(changes):
            with self.subTest(index=index), self.observation(subject, alter=alter) as (lease, owner):
                with self.assertRaises(M.RotationError):
                    self.prepare(subject, lease)
        self.assertEqual(before, git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)'))

    def test_stale_future_withdrawn_or_revised_input_refuses_before_archive(self):
        subject = self.subject()
        before = git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)')
        for fault in ('stale', 'future', 'withdrawn', 'revised'):
            self.clock.return_value = self.now * 1000000
            with self.subTest(fault=fault), self.observation(subject) as (lease, owner):
                if fault == 'stale': self.clock.return_value += 30001000000
                elif fault == 'future': self.clock.return_value -= 1000000
                elif fault == 'withdrawn': owner.withdraw_admission()
                else: owner.invalidate('context append')
                with self.assertRaises(M.RotationError):
                    self.prepare(subject, lease)
        self.assertEqual(before, git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)'))

    def test_health_trigger_does_not_waive_either_payoff_minimum(self):
        # Whitespace has ample removable bytes but too few actual tokens.
        subject = self.subject(' ' * 50000)
        with self.observation(subject) as (lease, owner), self.assertRaisesRegex(M.RotationError, 'payoff'):
            self.prepare(subject, lease)

    def test_health_trigger_does_not_waive_minimum_byte_payoff(self):
        subject = self.subject('q ' * 10000)
        self.assertLess(sum(map(len, subject['source'])), 32768)
        self.assertGreater(sum(M.count_rotation_tokens_v1(self.encoding, subject['source'])), 8192)
        with self.observation(subject) as (lease, owner), self.assertRaisesRegex(M.RotationError, 'payoff'):
            self.prepare(subject, lease)

    def test_native_input_cannot_be_attached_to_byte_token_or_correction_policy(self):
        subject = self.subject()
        for policy in (M.calibration_contract_v1(), M.token_calibration_contract_v1(),
                       M.c02_preparation_policy_v1()):
            with self.subTest(route=policy['admission_route']), self.observation(subject) as (lease, owner):
                with self.assertRaises(M.RotationError):
                    self.prepare(subject, lease, policy)

    def test_prepared_input_and_native_policy_substitution_are_detected(self):
        subject = self.subject()
        with self.observation(subject) as (lease, owner):
            result = self.prepare(subject, lease)
        for fault in ('input', 'policy'):
            changed = copy.deepcopy(result)
            if fault == 'input':
                changed['native_input']['observation']['context_health_bp'] = 0
            else:
                changed['calibration'] = M.token_calibration_contract_v1()
                del changed['native_input']
            with self.subTest(fault=fault), self.assertRaises(M.RotationError):
                M._checked_prepared(subject['repo'], subject['run'], changed)

    def test_rehashed_archived_input_still_must_match_actual_source_population(self):
        subject = self.subject()
        with self.observation(subject) as (lease, owner):
            result = self.prepare(subject, lease)
        manifest = M.verify_canonical_archive(subject['repo'], result['controller'],
                                              result['archive_ref'], result['archive_manifest_sha256'])
        manifest['native_input']['observation']['source_tokens'] += 1
        raw = M.canonical_bytes(manifest)
        oid = git(subject['repo'], 'hash-object', '-w', '--stdin', data=raw).decode().strip()
        git(subject['repo'], 'update-ref', result['archive_ref'], oid, result['archive_manifest_oid'])
        with self.assertRaises(M.RotationError):
            M.verify_canonical_archive(subject['repo'], result['controller'], result['archive_ref'], M.sha256(raw))


if __name__ == '__main__':
    unittest.main()
