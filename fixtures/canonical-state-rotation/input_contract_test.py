#!/usr/bin/env python3
"""Pure proposed-input controls; constructed observations grant no entitlement."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def module(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / 'skills/implementaudit/scripts' / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class InputContract(unittest.TestCase):
    def setUp(self):
        self.rotation = module('rotate-canonical-state')

    def test_independent_or_branches_and_boundary(self):
        for byte_count, tokens, health, expected in (
                (131072, 32767, 2501, ['BYTES']), (131071, 32768, 2501, ['TOKENS']),
                (131071, 32767, 2500, ['CONTEXT_HEALTH']), (131071, 32767, 2501, []),
                (131072, 32768, 2500, ['BYTES', 'TOKENS', 'CONTEXT_HEALTH'])):
            with self.subTest(bytes=byte_count, tokens=tokens, health=health):
                self.assertEqual(self.rotation.rotation_trigger_v1(byte_count, tokens, health), expected)

    def test_unknown_or_invalid_observation_is_not_healthy_or_zero(self):
        for values in ((1, None, 3000), (1, 1, None), (1, True, 3000), (1, 1, -1),
                       (1, 1, 10001), (-1, 1, 3000), (1, 1.2, 3000)):
            with self.subTest(values=values), self.assertRaises(self.rotation.RotationError):
                self.rotation.rotation_trigger_v1(*values)

    def test_both_frozen_payoffs_are_required(self):
        self.assertTrue(self.rotation.rotation_payoff_v1(32768, 8192))
        self.assertFalse(self.rotation.rotation_payoff_v1(32767, 8192))
        self.assertFalse(self.rotation.rotation_payoff_v1(32768, 8191))
        with self.assertRaises(self.rotation.RotationError):
            self.rotation.rotation_payoff_v1(None, 8192)

    def test_observation_identity_and_freshness(self):
        subject = {'controller': 'test', 'claim_id': '1' * 32, 'run_root_identity': '.IMPLEMENTAUDIT/runs/test-abc123',
                   'receipt_token': 'refs/implementaudit/continuity-receipts/test/G0001@' + '2' * 40,
                   'state_sha256': '3' * 64, 'roadmap_sha256': '4' * 64}
        contract = {'schema': 'implementaudit.rotation-input-contract-proposal.v1',
                    'baseline_calibration_id': self.rotation.CALIBRATION_ID, 'baseline_population_sha256': self.rotation.CALIBRATION_SHA256,
                    'issuer': 'test-owner', 'grant_sha256': '5' * 64, 'producer_sha256': '6' * 64,
                    'host': {'name': 'constructed-host', 'version': 'fixture'}, 'subject': subject,
                    'maximum_observation_age_ms': 30000,
                    'tokenizer': {'name': 'cl100k_base', 'implementation': 'tiktoken', 'version': '0.13.0'}}
        observation = {'schema': 'implementaudit.rotation-input-observation.v1',
                       'contract_sha256': self.rotation.sha256(self.rotation.canonical_bytes(contract)),
                       'subject': subject, 'host': contract['host'], 'issuer': 'test-owner',
                       'grant_sha256': '5' * 64, 'producer_sha256': '6' * 64,
                       'observed_at_unix_ms': 100000, 'source_bytes': 100000, 'source_tokens': 33000,
                       'context_health_bp': 9000, 'tokenizer': contract['tokenizer']}
        observation['observation_id'] = self.rotation.sha256(self.rotation.canonical_bytes(observation))
        answer = self.rotation.check_rotation_observation_v1(contract, observation, subject, 100000, 110000)
        self.assertEqual(answer['triggered_by'], ['TOKENS'])
        self.assertEqual(answer['authority_ceiling'], 'PROPOSED_INPUT_ONLY_NO_EFFECT_AUTHORITY')
        for changed, now in (({'source_bytes': 99999}, 110000), ({'source_tokens': None}, 110000),
                             ({'producer_sha256': '7' * 64}, 110000), ({}, 130001), ({}, 99999)):
            broken = copy.deepcopy(observation)
            broken.update(changed)
            with self.subTest(change=changed, now=now), self.assertRaises(self.rotation.RotationError):
                self.rotation.check_rotation_observation_v1(contract, broken, subject, 100000, now)


class CorrectionContract(unittest.TestCase):
    def setUp(self):
        self.owner = module('claim-run-rotation')
        self.observed = {'schema': 'implementaudit.c02-observation.v1', 'controller': 'qualification',
            'claim_id': '1' * 32, 'run_root_identity': '.IMPLEMENTAUDIT/runs/test-abc123',
            'pointer_oid': '2' * 40, 'receipt_oid': '3' * 40, 'marker_oid': '4' * 40,
            'invalidation_oid': '5' * 40, 'event_id': 'constructed-erroneous-event',
            'boundary': 'manual-resume', 'later_boundaries': []}
        self.decision = {'schema': 'implementaudit.c02-decision-proposal.v1', 'issuer': 'constructed-owner',
            'grant_sha256': '6' * 64, 'evidence_sha256': '7' * 64, 'kind': 'ERRONEOUS_INVALIDATION',
            'observation_sha256': self.owner.hashlib.sha256(self.owner.canonical(self.observed)).hexdigest()}
        self.decision['decision_id'] = self.owner.hashlib.sha256(self.owner.canonical(self.decision)).hexdigest()

    def test_proposal_is_bound_and_has_no_effect_authority(self):
        before = copy.deepcopy(self.observed)
        result = self.owner.propose_c02_correction_v1(self.observed, self.decision, [])
        self.assertEqual(result['status'], 'OWNER_ADMISSION_REQUIRED')
        self.assertEqual(result['expected_old']['invalidation_oid'], '5' * 40)
        self.assertEqual(result['authority_ceiling'], 'NO_EFFECT_AUTHORITY')
        self.assertEqual(self.observed, before)

    def test_exact_retry_and_conflicting_kind(self):
        prior = [{'observation': self.observed, 'decision': self.decision}]
        self.assertEqual(self.owner.propose_c02_correction_v1(self.observed, self.decision, prior)['status'],
                         'EXACT_RETRY_NO_EFFECT')
        changed = copy.deepcopy(self.decision)
        changed['kind'] = 'ORDINARY_RESUME'
        with self.assertRaises(self.owner.RotationError):
            self.owner.propose_c02_correction_v1(self.observed, changed, prior)

    def test_newer_boundary_supersedes_correction_without_erasing_history(self):
        observed = copy.deepcopy(self.observed)
        observed['later_boundaries'] = [{'event_id': 'constructed-newer-event',
            'invalidation_oid': '8' * 40, 'boundary': 'new-session'}]
        decision = copy.deepcopy(self.decision)
        decision['observation_sha256'] = self.owner.hashlib.sha256(self.owner.canonical(observed)).hexdigest()
        decision.pop('decision_id')
        decision['decision_id'] = self.owner.hashlib.sha256(self.owner.canonical(decision)).hexdigest()
        result = self.owner.propose_c02_correction_v1(observed, decision, [])
        self.assertEqual(result['status'], 'SUPERSEDED_NEWER_BOUNDARY_NO_EFFECT')
        self.assertEqual(len(observed['later_boundaries']), 1)

    def test_changed_old_identity_and_missing_census_refuse(self):
        for field, value in (('pointer_oid', '9' * 40), ('later_boundaries', None), ('marker_oid', None)):
            changed = copy.deepcopy(self.observed)
            changed[field] = value
            with self.subTest(field=field), self.assertRaises(self.owner.RotationError):
                self.owner.propose_c02_correction_v1(changed, self.decision, [])


if __name__ == '__main__':
    unittest.main()
