#!/usr/bin/env python3
"""Exact-event/lease mechanics with explicit test-owner stimuli, not native grants."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import queue
import sys
import threading
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'skills/implementaudit/scripts/canonical_rotation_inputs.py'
MODULE = None
if SOURCE.exists():
    SPEC = importlib.util.spec_from_file_location('native_rotation_input_under_test', SOURCE)
    MODULE = importlib.util.module_from_spec(SPEC)
    sys.modules[SPEC.name] = MODULE
    SPEC.loader.exec_module(MODULE)

THREAD, TURN = 'test-native-thread', 'test-native-turn'
NOW = 1792742165555
SUBJECT = {
    'controller': 'test-input-owner', 'claim_id': '1' * 32,
    'run_root_identity': '.IMPLEMENTAUDIT/runs/input-Ab12Cd',
    'receipt_token': 'refs/implementaudit/continuity-receipts/test-input-owner/G0001@' + '2' * 40,
    'state_sha256': '3' * 64, 'roadmap_sha256': '4' * 64,
}


def binding():
    return {
        'issuer': 'EXPLICIT-TEST-OWNER-NOT-PRODUCTION', 'grant_sha256': '5' * 64,
        'producer_sha256': '6' * 64, 'semantic_contract_sha256': '7' * 64,
        'host': {'name': 'codex', 'version': '0.153.4',
                 'binary_sha256': '444a3f0008050605cae73cd9b7a2dcac61294062dfaab56dd20430fd6498518b',
                 'effective_config_sha256': '8' * 64, 'model': 'gpt-6-astra'},
        'budget_policy': {'id': 'TEST-CONFIGURED-HEADROOM',
                          'configured_usable_tokens': 258400, 'maximum_age_ms': 30000},
        'tokenizer': {'name': 'cl100k_base', 'implementation': 'tiktoken', 'version': '0.13.0',
                      'encoding_sha256': '223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7'},
        'subject': copy.deepcopy(SUBJECT), 'source_bytes': 100000, 'source_tokens': 30000,
        'thread_id': THREAD, 'turn_id': TURN,
    }


def exact(total=17014, response='resp_test_exact'):
    return {'method': 'rawResponse/completed', 'params': {
        'threadId': THREAD, 'turnId': TURN, 'responseId': response,
        'usage': {'inputTokens': total - 11, 'outputTokens': 11, 'totalTokens': total,
                  'cachedInputTokens': 0, 'cacheWriteInputTokens': 0, 'reasoningOutputTokens': 0},
        'usageMetadata': {'metadata': {'PRIVATE_UNRETAINED_BODY': 'must not persist'}},
    }}


def reported_window(window=258400, total=17014, *, thread_id=THREAD, turn_id=TURN):
    """Constructed window event, not measured capacity or authentic host telemetry."""
    usage = exact(total)['params']['usage']
    return {'method': 'thread/tokenUsage/updated', 'params': {
        'threadId': thread_id, 'turnId': turn_id, 'tokenUsage': {
            'last': dict(usage), 'total': dict(usage), 'modelContextWindow': window}}}


def terminal():
    return {'method': 'turn/completed', 'params': {
        'threadId': THREAD, 'turn': {'id': TURN, 'status': 'completed', 'items': []}}}


class Availability(unittest.TestCase):
    def test_source_owned_input_mechanics_exist(self):
        self.assertIsNotNone(MODULE, 'source-owned native input adapter is absent')


@unittest.skipIf(MODULE is None, 'adapter not implemented yet')
class NativeInputMechanics(unittest.TestCase):
    def setUp(self):
        self.clock = mock.patch.object(MODULE.time, 'time_ns', return_value=NOW * 1000000).start()
        self.monotonic = mock.patch.object(MODULE.time, 'monotonic_ns', return_value=5000000000).start()
        self.addCleanup(mock.patch.stopall)

    def state(self, total=17014, complete=True):
        state = MODULE.NativeInputState(binding())
        state.observe(exact(total))
        state.observe(reported_window(total=total))
        if complete:
            state.observe(terminal())
        return state

    def owner(self, state):
        # The absent external owner is replaced only inside this fixture. This
        # is not a supported registration/authorizer API or native qualification.
        return mock.patch.object(MODULE, '_resolve_existing_owner_v1', return_value=state)

    def lease(self, subject=None, source_bytes=100000, source_tokens=30000):
        return MODULE.rotation_input_lease_v1(subject or SUBJECT, source_bytes, source_tokens)

    def test_default_resolver_refuses_caller_supplied_authority(self):
        with self.assertRaisesRegex(MODULE.NativeInputError, 'NATIVE_INPUT_DURABLE_SOURCE_UNAVAILABLE_OR_CONSUMED'):
            with self.lease():
                self.fail('unadmitted source reached accepting body')
        with mock.patch.object(MODULE, '_resolve_existing_owner_v1', return_value=True):
            with self.assertRaises(MODULE.NativeInputError):
                with self.lease():
                    self.fail('boolean authenticator reached accepting body')

    def test_retained_native_probe_is_parser_evidence_only(self):
        path = os.environ.get('R0039_EXACT_USAGE_PROBE')
        if not path:
            self.skipTest('retained real native exact-event probe not selected')
        probe = json.loads(Path(path).read_text(encoding='utf-8'))
        row = probe['exact_usage'][0]
        parsed = MODULE.parse_exact_usage_v1(
            {'method': 'rawResponse/completed', 'params': row['params']},
            probe['thread_id'], probe['turn_id'], row['received_at_unix_ms'], 1)
        self.assertEqual(parsed['usage']['totalTokens'], 17014)
        self.assertEqual(parsed['usage']['inputTokens'], 17003)
        self.assertEqual(parsed['usage']['outputTokens'], 11)
        self.assertNotIn('usageMetadata', parsed)
        self.assertNotIn('grant_sha256', parsed)

    def test_missing_null_estimated_and_inconsistent_usage_refuse(self):
        cases = []
        for usage in (None, {}, {'totalTokens': 1}):
            row = exact(); row['params']['usage'] = usage; cases.append(row)
        row = exact(); row['method'] = 'thread/tokenUsage/updated'; cases.append(row)
        row = exact(); row['params']['usage']['totalTokens'] += 1; cases.append(row)
        row = exact(); row['params']['usage']['inputTokens'] = True; cases.append(row)
        row = exact(); row['params']['usage']['cachedInputTokens'] = 18000; cases.append(row)
        for event in cases:
            with self.subTest(event=event), self.assertRaises(MODULE.NativeInputError):
                MODULE.parse_exact_usage_v1(event, THREAD, TURN, NOW, 1)

    def test_foreign_duplicate_and_replayed_responses_poison_the_candidate(self):
        for field in ('threadId', 'turnId'):
            state = MODULE.NativeInputState(binding())
            event = exact(); event['params'][field] = 'foreign'
            with self.assertRaises(MODULE.NativeInputError):
                state.observe(event)
            with self.owner(state), self.assertRaises(MODULE.NativeInputError):
                with self.lease(): pass
        state = self.state()
        with self.assertRaises(MODULE.NativeInputError):
            state.observe(exact())
        with self.owner(state), self.assertRaises(MODULE.NativeInputError):
            with self.lease(): pass

    def test_incomplete_turn_and_estimate_only_cannot_lease(self):
        estimate_only = MODULE.NativeInputState(binding())
        with self.assertRaisesRegex(MODULE.NativeInputError, 'UNBOUND_WINDOW_EVENT'):
            estimate_only.observe(reported_window())
        for state in (self.state(complete=False), estimate_only):
            with self.owner(state), self.assertRaises(MODULE.NativeInputError):
                with self.lease(): pass

    def test_configured_headroom_rounding_does_not_cross_threshold_early(self):
        for used, expected in ((0, 10000), (17014, 9342), (193799, 2501),
                               (193800, 2500), (193801, 2500), (258400, 0), (258401, 0)):
            with self.subTest(used=used):
                self.assertEqual(MODULE.configured_headroom_bp_v1(used, 258400), expected)
        for used, budget in ((True, 258400), (-1, 258400), (17014, 0), (17014, None)):
            with self.assertRaises(MODULE.NativeInputError):
                MODULE.configured_headroom_bp_v1(used, budget)

    def test_constructed_threshold_inputs_use_existing_trigger_and_payoff_policy(self):
        # These are algebra controls, never a genuine native health-only result.
        path = ROOT / 'skills/implementaudit/scripts/rotate-canonical-state.py'
        spec = importlib.util.spec_from_file_location('native_input_existing_rotation', path)
        rotation = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = rotation
        spec.loader.exec_module(rotation)
        for used, expected in ((17014, []), (193799, []), (193800, ['CONTEXT_HEALTH'])):
            with self.owner(self.state(used)), self.lease() as lease:
                self.assertEqual(rotation.rotation_trigger_v1(
                    100000, 30000, lease.observation['context_health_bp']), expected)
        self.assertEqual(rotation.rotation_trigger_v1(100000, 32768, 9342), ['TOKENS'])
        self.assertFalse(rotation.rotation_payoff_v1(32768, 8191))
        self.assertFalse(rotation.rotation_payoff_v1(32767, 8192))
        self.assertTrue(rotation.rotation_payoff_v1(32768, 8192))

    def test_binding_is_copied_and_caller_trusted_flags_are_not_admission(self):
        original = binding()
        state = MODULE.NativeInputState(original)
        original['budget_policy']['configured_usable_tokens'] = 1
        original['subject']['state_sha256'] = 'f' * 64
        state.observe(exact()); state.observe(reported_window()); state.observe(terminal())
        with self.owner(state), self.lease() as lease:
            self.assertEqual(lease.observation['context_health_bp'], 9342)
            self.assertEqual(lease.observation['subject'], SUBJECT)
        original = binding(); original['trusted'] = True
        with self.assertRaises(MODULE.NativeInputError):
            MODULE.NativeInputState(original)

    def test_source_bindings_and_clock_limits_refuse_before_effect(self):
        for field in SUBJECT:
            wrong = dict(SUBJECT); wrong[field] = 'foreign'
            with self.owner(self.state()), self.assertRaises(MODULE.NativeInputError):
                with self.lease(subject=wrong): pass
        for counts in ((99999, 30000), (100000, 29999)):
            with self.owner(self.state()), self.assertRaises(MODULE.NativeInputError):
                with self.lease(source_bytes=counts[0], source_tokens=counts[1]): pass
        for delta in (-1, 30001):
            state = self.state()
            self.clock.return_value = (NOW + delta) * 1000000
            with self.owner(state), self.assertRaises(MODULE.NativeInputError):
                with self.lease(): pass
            self.clock.return_value = NOW * 1000000
        state = self.state()
        self.monotonic.return_value += 30001000000
        with self.owner(state), self.assertRaises(MODULE.NativeInputError):
            with self.lease(): pass

    def test_later_context_events_disconnect_and_unknown_stream_revoke_lease(self):
        methods = ('item/tool/call', 'item/completed', 'thread/compacted', 'thread/reverted',
                   'model/rerouted', 'config/changed', 'unknown/record')
        for method in methods:
            state = self.state(); effects = []
            with self.owner(state), self.lease() as lease:
                with self.assertRaises(MODULE.NativeInputError):
                    state.observe({'method': method, 'params': {}})
                with self.assertRaises(MODULE.NativeInputError):
                    lease.admit(SUBJECT, 100000, 30000, lambda observation, guard: effects.append(observation))
            self.assertEqual(effects, [])
        for action in ('disconnect', 'withdraw_admission'):
            state = self.state(); effects = []
            with self.owner(state), self.lease() as lease:
                getattr(state, action)()
                with self.assertRaises(MODULE.NativeInputError):
                    lease.admit(SUBJECT, 100000, 30000, lambda observation, guard: effects.append(observation))
            self.assertEqual(effects, [])

    def test_context_mutation_is_denied_while_lease_is_live(self):
        state = self.state(); sent = []; failures = []
        with self.owner(state), self.lease():
            def send():
                try:
                    with state.context_change('tool-result injection'):
                        sent.append(True)
                except MODULE.NativeInputError:
                    failures.append(True)
            worker = threading.Thread(target=send)
            worker.start(); worker.join(timeout=2)
            self.assertFalse(worker.is_alive())
        self.assertEqual(sent, [])
        self.assertEqual(failures, [True])

    def test_final_admission_rechecks_live_owner_and_expiry(self):
        state = self.state(); effects = []
        with self.owner(state) as resolve, self.lease() as lease:
            resolve.return_value = MODULE.NativeInputState(binding())
            with self.assertRaises(MODULE.NativeInputError):
                lease.admit(SUBJECT, 100000, 30000, lambda obs, guard: effects.append(obs))
        self.assertEqual(effects, [])
        with self.owner(self.state()), self.lease() as lease:
            self.clock.return_value = (NOW + 30001) * 1000000
            with self.assertRaises(MODULE.NativeInputError):
                lease.admit(SUBJECT, 100000, 30000, lambda obs, guard: effects.append(obs))
        self.assertEqual(effects, [])

    def test_revision_drift_and_final_pair_drift_refuse_effect(self):
        for drift in ('stream', 'pair'):
            state = self.state(); effects = []
            with self.owner(state), self.lease() as lease:
                subject = dict(SUBJECT)
                if drift == 'stream':
                    with self.assertRaisesRegex(MODULE.NativeInputError, 'WINDOW_EVENT'):
                        state.observe({'method': 'thread/tokenUsage/updated', 'params': {
                            'threadId': THREAD, 'turnId': TURN, 'tokenUsage': {}}})
                else:
                    subject['receipt_token'] = subject['receipt_token'][:-1] + '9'
                with self.assertRaises(MODULE.NativeInputError):
                    lease.admit(subject, 100000, 30000, lambda obs, guard: effects.append(obs))
            self.assertEqual(effects, [])

    def test_missing_foreign_smaller_or_duplicate_window_refuses_lease(self):
        state = MODULE.NativeInputState(binding())
        state.observe(exact()); state.observe(terminal())
        with self.owner(state), self.assertRaisesRegex(MODULE.NativeInputError, 'CURRENT_REPORTED_WINDOW_REQUIRED'):
            with self.lease(): self.fail('windowless candidate reached accepting body')
        events = [reported_window(window=value) for value in (258399, None, True)]
        events += [reported_window(thread_id='foreign'), reported_window(turn_id='foreign')]
        for event in events:
            with self.subTest(event=event):
                state = MODULE.NativeInputState(binding()); state.observe(exact())
                with self.assertRaises(MODULE.NativeInputError): state.observe(event)
                with self.owner(state), self.assertRaises(MODULE.NativeInputError):
                    with self.lease(): self.fail('invalid window reached accepting body')
        state = self.state()
        with self.assertRaisesRegex(MODULE.NativeInputError, 'DUPLICATE_OR_UNBOUND_WINDOW_EVENT'):
            state.observe(reported_window())
        with self.owner(state), self.assertRaises(MODULE.NativeInputError):
            with self.lease(): self.fail('duplicate window reset the candidate')

    def test_larger_reported_window_does_not_replace_usage_policy_or_receipt_clocks(self):
        state = MODULE.NativeInputState(binding())
        state.observe(exact(), received_at_unix_ms=NOW - 10, received_monotonic_ns=4990000000)
        # Different constructed UI counters and a larger report cannot renew
        # the raw numerator, configured denominator or original source cutoff.
        state.observe(reported_window(window=300000, total=90000))
        state.observe(terminal())
        with self.owner(state), self.lease() as lease:
            observed = lease.observation
            self.assertEqual(observed['exact_usage']['usage']['totalTokens'], 17014)
            self.assertEqual(observed['budget_policy']['configured_usable_tokens'], 258400)
            self.assertEqual(observed['context_health_bp'], 9342)
            self.assertEqual(observed['reported_window']['model_context_window'], 300000)
            self.assertEqual(observed['exact_usage']['received_at_unix_ms'], NOW - 10)
        self.clock.return_value += 29991000000
        with self.owner(state), self.assertRaisesRegex(MODULE.NativeInputError, 'STALE_FUTURE_OR_UNCERTAIN_CUTOFF'):
            with self.lease(): self.fail('later window refreshed the old raw cutoff')

    def test_archive_schema_is_bound_to_exact_window_calibration(self):
        path = ROOT / 'skills/implementaudit/scripts/rotate-canonical-state.py'
        spec = importlib.util.spec_from_file_location('constructed_window_archive_rotation', path)
        rotation = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = rotation; spec.loader.exec_module(rotation)
        selected = binding()
        selected['budget_policy']['id'] = 'R0039-CONFIGURED-HEADROOM-v1'
        state = MODULE.NativeInputState(selected)
        state.observe(exact()); state.observe(reported_window()); state.observe(terminal())
        with self.owner(state), self.lease() as lease:
            observation = lease.observation
        receipt_ref, receipt_oid = SUBJECT['receipt_token'].split('@')
        predecessor = dict(SUBJECT, receipt_ref=receipt_ref, receipt_oid=receipt_oid)
        current = rotation.full_or_calibration_contract_v1()
        for calibration in rotation._historical_or_calibrations_v1():
            current_schema = calibration == current
            record = dict(schema='implementaudit.rotation-native-input.v2' if current_schema else
                          'implementaudit.rotation-native-input.v1', observation=copy.deepcopy(observation),
                          prepared_at_unix_ms=NOW, authority_ceiling='HISTORICAL_INPUT_NOT_REAUTHENTICATED')
            if not current_schema: del record['observation']['reported_window']
            rotation._check_native_input_record(record, predecessor, 100000, 30000, calibration)
            # Change the entire member population as well as the version: this
            # catches an actual downgrade, not merely a malformed schema label.
            record['schema'] = ('implementaudit.rotation-native-input.v1' if current_schema else
                                'implementaudit.rotation-native-input.v2')
            if current_schema: del record['observation']['reported_window']
            else: record['observation']['reported_window'] = copy.deepcopy(observation['reported_window'])
            with self.subTest(module=calibration['native_input_module_sha256']), self.assertRaisesRegex(
                    rotation.RotationError, 'schema differs from its exact calibration'):
                rotation._check_native_input_record(record, predecessor, 100000, 30000, calibration)
        record = dict(schema='implementaudit.rotation-native-input.v2', observation=copy.deepcopy(observation),
                      prepared_at_unix_ms=NOW, authority_ceiling='HISTORICAL_INPUT_NOT_REAUTHENTICATED')
        record['observation']['reported_window']['schema'] = 'implementaudit.native-reported-window.v2'
        with self.assertRaises(rotation.RotationError):
            rotation._check_native_input_record(record, predecessor, 100000, 30000, current)

    def test_nested_and_consumed_candidate_leases_refuse(self):
        state = self.state()
        with self.owner(state):
            with self.lease() as lease:
                with self.assertRaises(MODULE.NativeInputError):
                    with self.lease(): self.fail('second writer acquired native input')
                def publish(observation, guard):
                    token = guard.before_effect()
                    guard.after_effect(token)
                lease.admit(SUBJECT, 100000, 30000, publish)
            with self.assertRaises(MODULE.NativeInputError):
                with self.lease(): self.fail('consumed response was replayed')

    def test_atomic_publisher_and_one_shot_do_not_leak_mutable_bindings(self):
        state = self.state(); outputs = []
        with self.owner(state), self.lease() as lease:
            preview = lease.observation
            self.assertEqual(preview['context_health_bp'], 9342)
            self.assertEqual(preview['health_semantics'], 'CONFIGURED_OPERATIONAL_HEADROOM_EXACT_USAGE_AT_CUTOFF')
            preview['subject']['state_sha256'] = 'tampered'
            def publish(observation, guard):
                with self.assertRaises(MODULE.NativeInputError):
                    with state.context_change('turn/start'): self.fail('request sent during publication')
                token = guard.before_effect()
                outputs.append(observation)
                guard.after_effect(token)
                return 'existing-publisher-result'
            self.assertEqual(lease.admit(SUBJECT, 100000, 30000, publish), 'existing-publisher-result')
            with self.assertRaises(MODULE.NativeInputError):
                lease.admit(SUBJECT, 100000, 30000, publish)
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0]['subject'], SUBJECT)
        with self.assertRaises(MODULE.NativeInputError):
            lease.admit(SUBJECT, 100000, 30000, publish)

    def test_callback_failure_cannot_retry_unknown_effect(self):
        state = self.state()
        with self.owner(state), self.lease() as lease:
            def uncertain(observation, guard):
                guard.before_effect()
                raise RuntimeError('publication outcome unknown')
            with self.assertRaises(MODULE.NativeInputOutcomeUnknown):
                lease.admit(SUBJECT, 100000, 30000, uncertain)
            with self.assertRaises(MODULE.NativeInputError):
                lease.admit(SUBJECT, 100000, 30000, lambda obs, guard: self.fail('unknown effect retried'))

    def test_review_counterexamples_do_not_hide_incoming_revocation_behind_publisher(self):
        # Adapted from the sealed independent native_input_concurrency_review.py
        # SHA256 9861530598bd6dcd32e785304d7391f0aad0ea844d79270ad1725035f1797dcb.
        # The publisher holds the outgoing gate while a second owner thread
        # reports loss of validity. Old code returned success before processing it.
        for reason in ('disconnect', 'withdraw_admission', 'unexpected-record'):
            with self.subTest(reason=reason):
                state = self.state(); attempted = threading.Event(); completed = threading.Event()
                effects = []
                def incoming():
                    attempted.set()
                    try:
                        if reason == 'unexpected-record':
                            state.observe({'method': 'config/changed', 'params': {}})
                        else:
                            getattr(state, reason)()
                    except MODULE.NativeInputError:
                        pass
                    finally:
                        completed.set()
                worker = threading.Thread(target=incoming)
                try:
                    with self.owner(state), self.lease() as lease:
                        def publish(observation, guard=None):
                            token = guard.before_effect() if guard else None
                            worker.start()
                            self.assertTrue(attempted.wait(2))
                            completed.wait(0.1)
                            effects.append('SIMULATED_ALREADY_ISSUED_EFFECT')
                            if guard:
                                guard.after_effect(token)
                            return 'UNSAFE_SUCCESS'
                        with self.assertRaises(MODULE.NativeInputError) as caught:
                            lease.admit(SUBJECT, 100000, 30000, publish)
                        self.assertIsInstance(caught.exception, MODULE.NativeInputOutcomeUnknown)
                        self.assertTrue(completed.is_set(), 'invalidation waited behind publication')
                finally:
                    if worker.ident is not None:
                        worker.join(2)
                self.assertFalse(worker.is_alive())
                self.assertEqual(effects, ['SIMULATED_ALREADY_ISSUED_EFFECT'])

    def test_review_expiry_during_publication_cannot_return_success(self):
        with self.owner(self.state()), self.lease() as lease:
            def publish(observation, guard=None):
                token = guard.before_effect() if guard else None
                self.clock.return_value += 30001000000
                self.monotonic.return_value += 30001000000
                # Deliberately omit after_effect: the outer post-publish check
                # must still refuse to certify a stale completed callback.
                return 'UNSAFE_SUCCESS_AFTER_EXPIRY'
            with self.assertRaises(MODULE.NativeInputError):
                lease.admit(SUBJECT, 100000, 30000, publish)

    def test_precommit_checkpoint_sees_revocation_or_expiry_before_effect(self):
        for reason in ('disconnect', 'withdraw_admission', 'unknown', 'expiry'):
            with self.subTest(reason=reason):
                self.clock.return_value = NOW * 1000000
                state = self.state(); effects = []
                with self.owner(state), self.lease() as lease:
                    def publish(observation, guard):
                        if reason == 'expiry':
                            self.clock.return_value += 30001000000
                        elif reason == 'unknown':
                            try:
                                state.observe({'method': 'unknown/record', 'params': {}})
                            except MODULE.NativeInputError:
                                pass
                        else:
                            getattr(state, reason)()
                        token = guard.before_effect()
                        effects.append(True)
                        guard.after_effect(token)
                    with self.assertRaises(MODULE.NativeInputError) as caught:
                        lease.admit(SUBJECT, 100000, 30000, publish)
                    # Callback entry has occurred: even a guard refusal gets the
                    # conservative UNKNOWN disposition, without asserting effect.
                    self.assertIsInstance(caught.exception, MODULE.NativeInputOutcomeUnknown)
                self.assertEqual(effects, [])

    def test_missing_or_swallowed_posteffect_check_never_certifies_success(self):
        for mode in ('no-checkpoints', 'missing-post', 'swallowed-post-error'):
            with self.subTest(mode=mode):
                state = self.state()
                with self.owner(state), self.lease() as lease:
                    def publish(observation, guard):
                        if mode == 'no-checkpoints':
                            return 'UNVERIFIED_EFFECT'
                        token = guard.before_effect()
                        if mode == 'swallowed-post-error':
                            state.disconnect()
                            try:
                                guard.after_effect(token)
                            except MODULE.NativeInputOutcomeUnknown:
                                pass
                        return 'UNVERIFIED_EFFECT'
                    with self.assertRaises(MODULE.NativeInputOutcomeUnknown):
                        lease.admit(SUBJECT, 100000, 30000, publish)

    def test_revision_token_is_paired_and_multiple_effects_recheck_same_source(self):
        state = self.state(); seen = []
        with self.owner(state), self.lease() as lease:
            def publish(observation, guard):
                for ordinal in (1, 2):
                    guard.verify()
                    token = guard.before_effect()
                    self.assertEqual(token.source_revision, observation['cutoff_revision'])
                    self.assertEqual(token.grant_sha256, '5' * 64)
                    self.assertEqual(token.response_id, 'resp_test_exact')
                    self.assertEqual(token.ordinal, ordinal)
                    seen.append(ordinal)
                    guard.after_effect(token)
                return 'VERIFIED_AT_POSTEFFECT_CHECKPOINT'
            self.assertEqual(lease.admit(SUBJECT, 100000, 30000, publish),
                             'VERIFIED_AT_POSTEFFECT_CHECKPOINT')
        self.assertEqual(seen, [1, 2])

    def test_posteffect_check_rejects_a_foreign_checkpoint(self):
        with self.owner(self.state()), self.lease() as lease:
            def publish(observation, guard):
                token = guard.before_effect()
                guard.after_effect(tuple(token))
            with self.assertRaises(MODULE.NativeInputOutcomeUnknown):
                lease.admit(SUBJECT, 100000, 30000, publish)

    def test_review_unknown_cannot_be_repaired_by_restoring_owner_or_checkpoint(self):
        # Preserve the independent native_input_repair_review.py counterexamples:
        # the old guard could report UNKNOWN, then later return SUCCESS.
        for mode in ('foreign-checkpoint', 'changed-owner'):
            with self.subTest(mode=mode):
                state = self.state(); failures = []; later = []
                with self.owner(state) as resolve, self.lease() as lease:
                    def publish(observation, guard):
                        token = guard.before_effect()
                        if mode == 'changed-owner':
                            resolve.return_value = self.state()
                        try:
                            guard.after_effect(tuple(token) if mode == 'foreign-checkpoint' else token)
                        except MODULE.NativeInputOutcomeUnknown:
                            failures.append('UNKNOWN')
                        resolve.return_value = state
                        for operation in (guard.verify, guard.before_effect,
                                          lambda: guard.after_effect(token)):
                            try:
                                operation()
                            except MODULE.NativeInputOutcomeUnknown:
                                later.append('UNKNOWN')
                            except MODULE.NativeInputError:
                                later.append('CLEAN_REFUSAL')
                            else:
                                later.append('ACCEPTED')
                        return 'UNSAFE_SUCCESS_AFTER_UNKNOWN'
                    with self.assertRaises(MODULE.NativeInputOutcomeUnknown):
                        lease.admit(SUBJECT, 100000, 30000, publish)
                self.assertEqual(failures, ['UNKNOWN'])
                self.assertEqual(later, ['UNKNOWN', 'UNKNOWN', 'UNKNOWN'])

    def test_review_arbitrary_callback_error_cannot_prove_no_effect(self):
        effects = []
        with self.owner(self.state()), self.lease() as lease:
            def publish(observation, guard):
                effects.append('SIMULATED_UNINSTRUMENTED_EFFECT')
                raise MODULE.NativeInputError('CALLBACK_ERROR_NOT_A_GUARD_REFUSAL')
            with self.assertRaises(MODULE.NativeInputError) as caught:
                lease.admit(SUBJECT, 100000, 30000, publish)
            self.assertIsInstance(caught.exception, MODULE.NativeInputOutcomeUnknown)
        self.assertEqual(effects, ['SIMULATED_UNINSTRUMENTED_EFFECT'])


class NativeSourceLedgerMechanics(unittest.TestCase):
    """Constructed RPC traffic; no native producer or quiescence admission."""
    @classmethod
    def setUpClass(cls):
        path = ROOT / 'source-peers/native-runtime/skills/implementaudit/scripts/compaction-source-owner-codex-app.py'
        spec = importlib.util.spec_from_file_location('native_source_ledger_under_test', path)
        cls.source = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.source)

    def ready(self, incoming_id=1, outgoing_id=1):
        messages = queue.Queue()
        value = self.source.OwnedStdioQuiescenceV1(messages)
        value.before_send({'id': outgoing_id, 'method': 'initialize', 'params': {}})
        value.ingest({'id': incoming_id, 'result': {}}); messages.get_nowait()
        value.before_send({'method': 'initialized'})
        value.before_send({'id': 2, 'method': 'thread/start', 'params': {}})
        value.ingest({'id': 2, 'result': {'thread': {'id': THREAD}}}); messages.get_nowait()
        value.before_send({'id': 3, 'method': 'turn/start', 'params': {'threadId': THREAD}})
        value.ingest({'id': 3, 'result': {'turn': {'id': TURN}}}); messages.get_nowait()
        value.ingest({'method': 'turn/completed', 'params': {'threadId': THREAD,
            'turn': {'id': TURN, 'status': 'completed'}}}); messages.get_nowait()
        value.before_send({'id': 4, 'method': 'thread/read', 'params': {'threadId': THREAD}})
        value.ingest({'id': 4, 'result': {'thread': {'id': THREAD}}}); messages.get_nowait()
        value.acquire().verify()
        return value

    def test_exact_integer_and_string_ids_are_distinct_valid_requests(self):
        self.ready()
        self.ready(incoming_id='1', outgoing_id='1')

    def test_incoming_id_aliases_and_mismatches_poison_the_fence(self):
        for identity in (True, 1.0, '1', None, [], {}):
            with self.subTest(identity=identity):
                value = self.source.OwnedStdioQuiescenceV1(queue.Queue())
                value.before_send({'id': 1, 'method': 'initialize'})
                with self.assertRaises(ValueError):
                    value.ingest({'id': identity, 'result': {}})
                self.assertEqual(value._pending, {(int, 1): 'initialize'})
                with self.assertRaises(ValueError):
                    value.ingest({'id': 1, 'result': {}})
                with self.assertRaises(ValueError):
                    value.acquire()

    def test_outgoing_id_aliases_and_reused_ids_refuse(self):
        for identity in (True, 1.0, None, [], {}):
            with self.subTest(identity=identity):
                value = self.source.OwnedStdioQuiescenceV1(queue.Queue())
                with self.assertRaises(ValueError):
                    value.before_send({'id': identity, 'method': 'initialize'})
                with self.assertRaises(ValueError):
                    value.acquire()
        value = self.ready()
        with self.assertRaises(ValueError):
            value.before_send({'id': 4, 'method': 'thread/read', 'params': {'threadId': THREAD}})


if __name__ == '__main__':
    unittest.main()
