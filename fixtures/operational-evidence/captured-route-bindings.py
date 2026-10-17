"""RR01-RR03 constructed owner-format controls, never authentication proofs.

Exact reviewer JSON preimages are retained beside this file. Only the supplied
pure consumer is loaded; native owners and paths carried in data are not opened.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--target', type=Path, default=HERE / 'operational_query_policy.py')
args, remaining = parser.parse_known_args()
spec = importlib.util.spec_from_file_location('remaining_bindings_subject', args.target)
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


def fixture(name):
    return json.loads((HERE / 'captured-review-preimages' / (name + '.json')).read_bytes())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False).encode()).hexdigest()


def assignment(state):
    return state['assignments']['constructed-child']


def reseal(state):
    a = assignment(state)
    a['return']['return_digest'] = digest(a['return']['identity'])
    if a.get('accepted'):
        a['accepted']['value']['actual_result_digest'] = a['return']['return_digest']
    if a.get('logical_join'):
        a['logical_join']['return_digest'] = a['return']['return_digest']
        a['logical_join']['acceptance'] = copy.deepcopy(a['accepted'])


def decode(kind, value):
    decoder = subject.decode_route_capture if kind == 'pending' else subject.decode_occurrence_capture
    with mock.patch('builtins.open', side_effect=AssertionError('No captured path I/O')), \
         mock.patch('pathlib.Path.open', side_effect=AssertionError('No captured path I/O')), \
         mock.patch('os.open', side_effect=AssertionError('No captured path I/O')), \
         mock.patch('pathlib.Path.stat', side_effect=AssertionError('No captured metadata I/O')), \
         mock.patch('pathlib.Path.resolve', side_effect=AssertionError('No captured path resolution')):
        return decoder(kind, value)


class RemainingBindingTests(unittest.TestCase):
    def test_pending_without_q_preserves_available_return_acceptance_and_pending(self):
        value = fixture('pending_bound_return_control')
        original = copy.deepcopy(value)
        out = decode('pending', value)
        self.assertEqual(value, original)
        types = {r['record_type'] for r in out['records']}
        self.assertTrue({'ChildReturn', 'ParentAcceptanceObservation', 'PendingCompaction'} <= types)
        pending = [r['observation'] for r in out['records'] if r['record_type'] == 'PendingCompaction']
        self.assertTrue(pending and all(p['pending'] for p in pending))
        self.assertTrue(out['omissions'])

    def test_complete_return_without_acceptance_does_not_require_c_q_e(self):
        value = fixture('pending_bound_return_control')
        a = assignment(value)
        a.pop('accepted')
        a.pop('logical_join')
        out = decode('pending', value)
        self.assertTrue(any(r['record_type'] == 'ChildReturn' for r in out['records']))

    def test_preacceptance_return_physical_identity_still_checked(self):
        value = fixture('pending_no_q_result_physical_list')
        a = assignment(value)
        a.pop('accepted')
        a.pop('logical_join')
        with self.assertRaises(ValueError):
            decode('pending', value)

    def test_source_context_is_optional_but_existing_child_pin_identity_is_not(self):
        value = fixture('pending_bound_return_control')
        a = assignment(value)
        a['return']['identity']['use']['result']['physical']['inode'] += 1
        reseal(value)
        with self.assertRaises(ValueError):
            decode('pending', value)

    def test_parent_acceptance_pin_cannot_claim_child_role(self):
        value = fixture('pending_bound_return_control')
        assignment(value)['accepted']['record']['role'] = 'child'
        reseal(value)
        with self.assertRaises(ValueError):
            decode('pending', value)

    def test_pending_acceptance_same_file_bytes_cannot_overlap_delivery(self):
        value = fixture('pending_bound_return_control')
        a = assignment(value)
        a['accepted']['record']['locator']['offset'] = a['return']['identity']['parent_delivery']['locator']['offset']
        reseal(value)
        with self.assertRaises(ValueError):
            decode('pending', value)

    def test_member_physical_alias_is_duplicate_even_at_another_path(self):
        value = fixture('pending_bound_return_control')
        members = assignment(value)['return']['identity']['members']
        another = copy.deepcopy(members[0])
        another['pin']['path'] = '/fixture/result/another.json'
        members.append(another)
        reseal(value)
        with self.assertRaises(ValueError):
            decode('pending', value)

    def test_result_and_member_keep_one_mib_each_with_two_mib_total(self):
        value = fixture('pending_bound_return_control')
        r = assignment(value)['return']['identity']
        r['result_pin']['bytes'] = 1048576
        r['members'][0]['pin']['bytes'] = 1048576
        reseal(value)
        decode('pending', value)
        r['result_pin']['bytes'] += 1
        reseal(value)
        with self.assertRaises(ValueError):
            decode('pending', value)

    def test_candidate_and_schema_less_episode_keep_valid_obligation_one_mib(self):
        for name in ('candidate_control', 'schema_less_episode_control'):
            with self.subTest(name=name):
                value = fixture(name)
                value['O_U_exchange_USE_R_A_identities']['O']['bytes'] = 1048576
                decode('result-occurrence', value)

    def test_c_and_e_still_require_acceptance_even_though_preacceptance_pending_does_not(self):
        for name in ('candidate_control', 'schema_less_episode_control'):
            with self.subTest(name=name):
                value = fixture(name)
                value['O_U_exchange_USE_R_A_identities']['A'] = None
                value['exact_acceptance_digest'] = digest(None)
                with self.assertRaises(ValueError):
                    decode('result-occurrence', value)

    def test_qualified_and_bound_envelopes_preserve_raw_pin_hashes(self):
        for name in ('qualified_acquisition_control', 'bound_episode_control'):
            with self.subTest(name=name):
                value = fixture(name)
                acquisition = assignment(value)['logical_join']['acquisition']
                self.assertNotEqual(acquisition['candidate']['sha256'], digest(acquisition['episode_candidate']))
                decode('pending', value)

    def test_qualification_evidence_candidate_may_differ_from_current_episode_candidate(self):
        value = fixture('qualified_acquisition_control')
        a = assignment(value)
        acquisition = a['logical_join']['acquisition']
        acquisition['profile']['evidence'] = {'path': '/constructed/candidates/qualification-only.json',
            'bytes': 137, 'sha256': 'b' * 64}
        a['logical_join']['profile'] = copy.deepcopy(acquisition['profile'])
        self.assertNotEqual(acquisition['candidate'], acquisition['profile']['evidence'])
        decode('pending', value)

    def test_candidate_q_e_and_reviews_keep_two_mib_custody_bound(self):
        value = fixture('bound_episode_control')
        a = assignment(value)
        acquisition = a['logical_join']['acquisition']
        custody = [acquisition['candidate'], acquisition['episode'], acquisition['profile']['Q'],
                   acquisition['profile']['evidence'], *acquisition['profile']['review_pins']]
        for pin in custody:
            pin['bytes'] = 2097152
        acquisition['episode_candidate']['actual_acquisition_and_custody_validation_evidence']['candidate'] = copy.deepcopy(acquisition['candidate'])
        a['logical_join']['profile'] = copy.deepcopy(acquisition['profile'])
        decode('pending', value)
        acquisition['episode']['bytes'] += 1
        with self.assertRaises(ValueError):
            decode('pending', value)


NEGATIVES = {
    'pending_no_q_result_physical_list': 'pending',
    'pending_no_q_member_physical_bool': 'pending',
    'pending_no_q_member_outside_directory': 'pending',
    'pending_no_q_duplicate_member': 'pending',
    'pending_no_q_member_total_over_2m': 'pending',
    'pending_no_q_acceptance_record_list': 'pending',
    'pending_no_q_acceptance_precedes_delivery': 'pending',
    'candidate_obligation_over_1m': 'result-occurrence',
    'schema_less_episode_obligation_over_1m': 'result-occurrence',
    'qualified_q_pin_differs_from_lookup': 'pending',
    'bound_e_pin_differs_from_lookup': 'pending',
}


def exact_negative(name, kind):
    def test(self):
        value = fixture(name)
        with self.assertRaises(ValueError):
            decode(kind, value)
    return test


for name, kind in NEGATIVES.items():
    setattr(RemainingBindingTests, 'test_reviewer_' + name, exact_negative(name, kind))


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0], *remaining])
