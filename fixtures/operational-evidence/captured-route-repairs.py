"""Constructed owner-format repair controls; no native or producer proof.

Inputs in preimages are exact copies of the reviewer's constructed JSON. The
optional occurrence consumer is a pure companion, never an original owner.
"""
import argparse
import base64
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
parser.add_argument('--consumer', default=str(HERE / 'consumer.py'))
parser.add_argument('--occurrence', default=str(HERE / 'occurrence-consumer.py'))
options, remainder = parser.parse_known_args()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


subject = load(options.consumer, 'constructed_route_repair_subject')
occurrence = load(options.occurrence, 'constructed_occurrence_repair_subject')
subject.decode_occurrence_capture = occurrence.decode_occurrence_capture


def fixture(name):
    return json.loads((HERE / 'captured-review-preimages' / (name + '.json')).read_text())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(value if type(value) is bytes else canonical(value)).hexdigest()


def reseal(route):
    route['record_identity'] = 'sha256:' + digest({k: v for k, v in route.items() if k != 'record_identity'})


def packet(route, target):
    value = json.loads(base64.b64decode(route['lifecycle']['delivery']['packet']['bytes_b64']))
    value['target_identity'] = target
    raw = canonical(value)
    route['lifecycle']['delivery']['packet'] = {'bytes': len(raw), 'digest': 'sha256:' + digest(raw),
        'bytes_b64': base64.b64encode(raw).decode()}
    reseal(route)


def assignment(state):
    return state['assignments']['constructed-child']


def rebind_result(state):
    a = assignment(state)
    a['return']['return_digest'] = digest(a['return']['identity'])
    a['accepted']['value']['actual_result_digest'] = a['return']['return_digest']
    a['logical_join']['return_digest'] = a['return']['return_digest']
    a['logical_join']['acceptance'] = copy.deepcopy(a['accepted'])


def with_acquisition():
    """Existing owner envelope with constructed pins; no Q/E file was acquired."""
    state = fixture('pending_bound_return_control')
    a = assignment(state)
    descriptor = {'schema': 'implementaudit.compaction-fixed-acquisition-policy.v1',
        'profile_id': 'codex-desktop-0.153.4-collaboration-public-v1',
        'custody_namespace': 'result-observations-v1', 'qualification_key': 'qualification/Q.json',
        'authenticating_source_owner': None}
    policy = {'descriptor': descriptor, 'code_and_skill_pins': a['code']}
    policy['policy_digest'] = digest(policy)
    a['policy'] = policy
    candidate = fixture('candidate_control')
    candidate.update(policy_digest=policy['policy_digest'], observation_id=a['return']['observation_id'],
        covered_boundary_versions=a['return']['identity']['scope'], exact_result_digest=a['return']['return_digest'],
        exact_acceptance_digest=digest(a['accepted']))
    candidate['assignment_identity'] = digest({'child': candidate['actual_child_identity'], 'code': a['code']})
    candidate['O_U_exchange_USE_R_A_identities']['R'] = a['return']['identity']
    candidate['O_U_exchange_USE_R_A_identities']['A'] = a['accepted']
    candidate['physical_source_and_cutoff_identities']['compaction_cutoff'] = a['accepted']['value']['observation_source_cutoff']
    # A pin hashes raw file bytes, not a compact reserialization of its value.
    c_pin = {'path': '/constructed/candidates/c.json', 'bytes': 123,
             'sha256': digest(b'CONSTRUCTED raw candidate wire including whitespace')}
    q_pin = {'path': '/constructed/qualification/Q.json', 'bytes': 123,
             'sha256': digest(b'CONSTRUCTED Q bytes, never acquired')}
    profile = {'status': 'QUALIFICATION_RECORD_BOUND_ORIGIN_UNRESOLVED', 'policy_qualified': None,
        'qualification_record_bound': True, 'policy_digest': policy['policy_digest'], 'Q': q_pin,
        'evidence': c_pin, 'review_pins': [
            {'path': '/constructed/qualification/review.json', 'bytes': 12, 'sha256': digest(b'CONSTRUCTED review')},
            {'path': '/constructed/qualification/selection.json', 'bytes': 12, 'sha256': digest(b'CONSTRUCTED selection')}],
        'unresolved_implementation_edge': 'No independently authenticating producer/custody validator is established'}
    keys = ('policy_digest', 'parent_identity', 'actual_child_identity', 'assignment_identity', 'obligation_digest',
        'observation_id', 'covered_boundary_versions', 'O_U_exchange_USE_R_A_identities',
        'physical_source_and_cutoff_identities', 'exact_result_digest', 'exact_acceptance_digest', 'authority_ceiling')
    episode = {key: candidate[key] for key in keys}
    episode.update(Q_digest=q_pin['sha256'], actual_acquisition_and_custody_validation_evidence={'candidate': c_pin})
    a['logical_join']['profile'] = profile
    a['logical_join']['acquisition'] = {'status': 'QUALIFICATION_BOUND_PENDING_EPISODE_ORIGIN',
        'policy': policy, 'profile': profile, 'candidate': c_pin,
        'lookup': {'Q': '/constructed/qualification/Q.json', 'E': '/constructed/episodes/e.json'},
        'episode_record_bound': False, 'episode': None, 'origin_validated': None,
        'host_producer_authenticated': False, 'authority_ceiling': 'NONE',
        'unresolved_implementation_edge': 'Authenticating producer/custody acquisition validator is not implemented or qualified',
        'episode_candidate': episode}
    return state


class OwnerFormatRepairTests(unittest.TestCase):
    def decode(self, kind, value):
        return subject.decode_route_capture(kind, value)

    def test_reviewer_route_control_passes_and_foreign_target_fails(self):
        self.assertTrue(self.decode('route', fixture('route_control'))['records'])
        with self.assertRaises(ValueError):
            self.decode('route', fixture('packet_child_disagrees_with_action'))

    def test_all_four_exact_action_child_mappings(self):
        for reason, child in (('STALE_CONTEXT_RECONSTRUCTION', 'audit-state'),
            ('IMMUTABLE_INDEPENDENT_REVIEW', 'audit-assess'), ('MAINTAINER_QUALIFICATION', 'audit-implement'),
            ('NONTRIVIAL_ANDON_DIAGNOSIS', 'audit-andon')):
            value = fixture('route_control'); value['action']['argv'] = ['route-trigger', reason]
            packet(value, child)
            self.assertTrue(self.decode('route', value)['records'])
            value['action']['argv'].append('not-the-exact-trigger'); reseal(value)
            with self.assertRaises(ValueError): self.decode('route', value)

    def test_standalone_result_without_action_does_not_infer_child_from_path(self):
        route = fixture('packet_child_disagrees_with_action')
        value = {'schema': 'implementaudit.route-transaction-result.v1', 'status': 'CHILD_OPEN',
            'decision': 'REQUIRED', 'route_state': 'OPEN', 'advance_allowed': False, 'enforcement_available': True,
            'record_oid': '1' * 40, 'record_identity': route['record_identity'],
            'obligation_id': route['obligation_id'], 'route_transaction_id': route['route_transaction_id'],
            'delivery': route['lifecycle']['delivery'], 'history_read_performed': False,
            'holon_lifecycle': {'required_sequence': ['OPEN', 'LOAD', 'USE', 'RETURN', 'DISPOSE', 'RECONCILE'],
                'completed': ['OPEN'], 'selected_child': 'audit-assess', 'obligation_id': route['obligation_id'],
                'route_transaction_id': route['route_transaction_id'], 'identity_bound': True,
                'unverified': ['LOAD', 'USE', 'DISPOSE'], 'child_authority': 'NONE', 'child_can_route': False,
                'governor_reconciliation_required': True, 'canonical_credit': False}}
        self.assertTrue(self.decode('route-result', value)['records'])

    def test_reviewer_logical_task_alias_is_refused(self):
        with self.assertRaises(ValueError):
            self.decode('route', fixture('logical_task_aliases_governed_role'))

    def test_logical_task_exact_regex_reserved_roles_and_identities(self):
        value = fixture('route_control')
        for name in ('reconcile-boundary_2', 'f' * 31, 'f' * 65):
            value['lifecycle']['logical_task'] = name; reseal(value)
            self.assertTrue(self.decode('route', value)['records'])
        for name in ('audit-state', 'audit-assess', 'audit-implement', 'audit-andon', value['host_session_id'],
            value['route_transaction_id'], 'f' * 32, 'f' * 64, '12345678-1234-1234-1234-123456789abc',
            'Uppercase', 'two words', 'a' * 129):
            value['lifecycle']['logical_task'] = name; reseal(value)
            with self.assertRaises(ValueError): self.decode('route', value)

    def test_reviewer_pending_bound_control_and_foreign_acceptance(self):
        result = self.decode('pending', fixture('pending_bound_return_control'))
        self.assertEqual(sum(row['observation']['pending'] for row in result['records']
            if row['record_type'] == 'PendingCompaction'), 2)
        with self.assertRaises(ValueError): self.decode('pending', fixture('pending_foreign_accepted_result'))

    def test_available_acceptance_binding_fields_are_checked(self):
        for field, replacement in (('observation_id', 'f' * 64), ('obligation_digest', 'f' * 64),
            ('child_observation_exchange_identity', 'f' * 64), ('accepted_boundary_versions', []),
            ('observation_source_cutoff', None)):
            value = fixture('pending_bound_return_control')
            assignment(value)['accepted']['value'][field] = replacement
            with self.assertRaises(ValueError): self.decode('pending', value)

    def test_return_digest_and_selected_observation_scope_are_checked(self):
        value = fixture('pending_bound_return_control'); assignment(value)['return']['return_digest'] = 'f' * 64
        with self.assertRaises(ValueError): self.decode('pending', value)
        value = fixture('pending_bound_return_control')
        assignment(value)['return']['identity']['scope'] = []
        rebind_result(value)
        with self.assertRaises(ValueError): self.decode('pending', value)

    def test_join_coverage_return_and_acceptance_are_bound(self):
        for field, replacement in (('return_digest', 'f' * 64), ('child_id', 'foreign-child'),
                                  ('proposed_consumption', []), ('acceptance', {})):
            value = fixture('pending_bound_return_control')
            assignment(value)['logical_join'][field] = replacement
            with self.assertRaises(ValueError): self.decode('pending', value)

    def test_historical_projection_does_not_hide_later_actual_boundary(self):
        value = fixture('pending_bound_return_control')
        assignment(value)['logical_join']['projected_pending'] = []
        result = self.decode('pending', value)
        self.assertEqual(sum(row['observation']['pending'] for row in result['records']
            if row['record_type'] == 'PendingCompaction'), 2)

    def test_incomplete_captured_return_is_explicitly_omitted_not_authenticated(self):
        value = fixture('pending_bound_return_control'); a = assignment(value)
        for key in ('identity', 'return_digest', 'frontier', 'evidence'): del a['return'][key]
        a['accepted'] = {}; a['logical_join']['acceptance'] = {}
        result = self.decode('pending', value)
        self.assertTrue(any('incomplete' in row['reason'].lower() for row in result['omissions']))
        self.assertTrue(any(row['record_type'] == 'ChildReturn' for row in result['records']))

    def test_reviewer_multiline_refusals_are_retained_exactly(self):
        for name, kind in (('route_multiline_refusal', 'route-result'), ('host_multiline_refusal', 'host-binding')):
            value = fixture(name)
            result = self.decode(kind, value)
            self.assertTrue(any(row['record_type'] == 'NativeRefusal' and row['observation']['error'] == value['error']
                                for row in result['records']))

    def test_refusal_text_keeps_utf8_controls_and_remains_bounded(self):
        value = fixture('host_multiline_refusal'); value['error'] = 'constructed\r\n\t\u00e9chec\u0000stderr'
        self.assertTrue(self.decode('host-binding', value)['records'])
        value['error'] = 'x' * (8192 + 1)
        with self.assertRaises(ValueError): self.decode('host-binding', value)

    def test_complete_embedded_episode_projects_existing_occurrences(self):
        value = with_acquisition()
        with mock.patch('builtins.open', side_effect=AssertionError('Captured locator was opened')):
            result = self.decode('pending', value)
        self.assertTrue(any(row['record_type'] == 'SourceOccurrence' for row in result['records']))
        self.assertTrue(any(row['record_type'] == 'Artifact' for row in result['records']))
        self.assertTrue(any('bytes' in row['reason'].lower() for row in result['omissions']))
        self.assertFalse(any('nested native occurrence, hold, return and acceptance semantics require' in row['reason']
                             for row in result['omissions']))

    def test_exact_policy_and_acceptance_hashes_are_local_checks(self):
        for field in ('policy_digest', 'exact_acceptance_digest'):
            value = with_acquisition(); a = assignment(value)
            if field == 'policy_digest': a['logical_join']['acquisition']['policy'][field] = 'f' * 64
            else: a['logical_join']['acquisition']['episode_candidate'][field] = 'f' * 64
            with self.assertRaises(ValueError): self.decode('pending', value)

    def test_embedded_episode_remains_bound_to_adjacent_return(self):
        value = with_acquisition(); a = assignment(value)
        episode = a['logical_join']['acquisition']['episode_candidate']
        episode['observation_id'] = 'f' * 64
        with self.assertRaises(ValueError): self.decode('pending', value)

    def test_raw_file_pins_are_not_compact_json_digests(self):
        value = with_acquisition(); acquisition = assignment(value)['logical_join']['acquisition']
        self.assertNotEqual(acquisition['candidate']['sha256'], digest(acquisition['episode_candidate']))
        self.assertTrue(self.decode('pending', value)['records'])

    def test_standalone_schema_less_episode_is_existing_format_without_producer_fabrication(self):
        value = assignment(with_acquisition())['logical_join']['acquisition']['episode_candidate']
        self.assertNotIn('schema', value)
        self.assertNotIn('producer_environment_identity', value)
        decoded = occurrence.decode_occurrence_capture('result-occurrence', value)
        self.assertTrue(any(row['record_type'] == 'SourceOccurrence' for row in decoded['records']))

    def test_owner_distinguishes_one_mib_result_and_two_mib_custody_bounds(self):
        value = with_acquisition()
        acquisition = assignment(value)['logical_join']['acquisition']
        acquisition['candidate']['bytes'] = 1024 * 1024 + 1
        self.assertTrue(self.decode('pending', value)['records'])
        value = fixture('pending_bound_return_control')
        assignment(value)['return']['identity']['members'][0]['pin']['bytes'] = 1024 * 1024 + 1
        rebind_result(value)
        with self.assertRaises(ValueError): self.decode('pending', value)

    def test_only_original_bind_selector_has_optional_physical_line_compatibility(self):
        value = fixture('pending_bound_return_control')
        assignment(value)['return']['evidence']['bound_exchange']['call']['physical_line'] = None
        self.assertTrue(self.decode('pending', value)['records'])
        assignment(value)['return']['evidence']['use']['call']['physical_line'] = None
        with self.assertRaises(ValueError): self.decode('pending', value)


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]] + remainder)
