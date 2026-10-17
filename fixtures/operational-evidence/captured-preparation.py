"""Source-bound constructed preparation controls through the real capture API.

No WG owner helper, graph_path, receipt, inspected/proposed path, or authority
source is opened. --target selects the integrated companion without patching it.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--target', type=Path, default=HERE / 'consumer_successor.py')
args, remaining = parser.parse_known_args()
spec = importlib.util.spec_from_file_location('preparation_consumer_subject', args.target)
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


def load_control(name='preparation_control'):
    return json.loads((HERE / 'captured-review-preimages' / (name + '.json')).read_text())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def preparation(graph):
    return next(c for c in graph['cells'] if c['id'] == 'prepared')['preparation']


def blocked_control():
    graph = load_control()
    prepared = graph['cells'][1]
    prepared.update(state='BLOCKED', deps=['holder'])
    prepared['preparation']['execution_unavailable'] = {'kind': 'UNMET_DEPENDENCIES', 'dependencies': ['holder']}
    graph['serialization_groups'] = {}
    return graph


def product_control():
    graph = load_control()
    product = {'commit': '1' * 40, 'tree': '2' * 40, 'review_sha256': '3' * 64}
    result = {'product': product, 'disposition': {'kind': 'INTEGRATED', 'target': '4' * 40}}
    graph['cells'].append({'id': 'done-source', 'state': 'DONE', 'deps': [], 'source_bearing': True, 'result': result})
    graph['population']['total_cells'] = 3
    graph['cells'][1]['deps'] = ['done-source']
    preparation(graph)['record']['predecessors'].append({'cell_id': 'done-source', 'state': 'DONE',
        'identity': {'kind': 'QUALIFIED_PRODUCT', **product}})
    document = {'done_classification': {'done-source': 'SOURCE_PRODUCT'}, 'non_cell_owners': [], 'join_owners': [],
        'product_bindings': [{'owner_kind': 'CELL', 'owner': 'done-source', **product}],
        'disposition_bindings': [{'product_commit': product['commit'], **result['disposition']}],
        'composition_authorizations': [], 'future_consumers': [{'product_commit': product['commit'], 'cell_id': 'prepared'}]}
    source = {'kind': 'GOVERNOR_VERIFIED_PRODUCT_BINDINGS', 'path': '/constructed/product-authority.json',
        'bytes': len(canonical(document)), 'sha256': sha(document),
        'receipt': 'refs/implementaudit/continuity-receipts/constructed/G0001@' + '5' * 40}
    graph['authority'] = {'qualified_product_contract': source}
    graph['integration_topology'] = {'product_contract': {'authority_sha256': sha(source), **document},
        'unrecognized_product_field': {'raw': 'retained'}}
    return graph


class PreparationConsumerTests(unittest.TestCase):
    def decode(self, graph):
        before = copy.deepcopy(graph)
        # A meaningful negative capability assertion: data paths are inert.
        with patch('builtins.open', side_effect=AssertionError('capture attempted file IO')), \
             patch('pathlib.Path.open', side_effect=AssertionError('capture attempted path IO')):
            result = subject.decode_occurrence_capture('member-coverage', graph)
        self.assertEqual(graph, before)
        keys = {canonical(r['key']) for r in result['records']}
        self.assertEqual(len(keys), len(result['records']))
        for row in result['records']:
            for endpoint in ('source_key', 'target_key'):
                if endpoint in row:
                    self.assertIn(canonical(row[endpoint]), keys)
            self.assertNotIn('establishes', row)
            self.assertNotIn('currentness', row)
        return result

    def reject(self, graph, reason):
        with self.assertRaisesRegex(ValueError, reason):
            self.decode(graph)

    def test_reviewer_ready_control_projects_full_preparation_and_hold(self):
        graph = load_control()
        result = self.decode(graph)
        self.assertTrue(any(r['record_type'] == 'WorkPreparation' and r['observation'] == preparation(graph)
                            for r in result['records']))
        relations = {r.get('relation_type') for r in result['records']}
        self.assertTrue({'HAS_PREPARATION', 'HELD_BY_GROUP', 'HELD_BY_MEMBER', 'OBSERVES_PREDECESSOR'} <= relations)
        self.assertIn('PREPARATION_ACTIVATION_NOT_ESTABLISHED', {o['reason'] for o in result['omissions']})

    def test_reviewer_missing_group_refuses(self):
        self.reject(load_control('preparation_missing_group'), 'PREPARATION_HOLD_BINDING')

    def test_reviewer_stale_predecessor_refuses(self):
        self.reject(load_control('preparation_stale_predecessor'), 'PREPARATION_PREDECESSOR_STATE')

    def test_blocked_exact_unmet_dependencies_with_done_predecessor(self):
        graph = blocked_control()
        graph['cells'].append({'id': 'done', 'state': 'DONE', 'deps': []})
        graph['population']['total_cells'] = 3
        graph['cells'][1]['deps'].append('done')
        preparation(graph)['record']['predecessors'].append({'cell_id': 'done', 'state': 'DONE',
            'identity': {'kind': 'UNAVAILABLE', 'reason': 'NON_SOURCE_PRODUCT'}})
        result = self.decode(graph)
        self.assertTrue(any(r.get('relation_type') == 'BLOCKED_BY_DEPENDENCY' for r in result['records']))
        bad = copy.deepcopy(graph)
        preparation(bad)['execution_unavailable']['dependencies'].append('done')
        self.reject(bad, 'PREPARATION_DEPENDENCY_BINDING')
        bad = copy.deepcopy(graph)
        preparation(bad)['record']['predecessors'].pop()
        self.reject(bad, 'PREPARATION_PREDECESSOR_SET')

    def test_ready_requires_exact_group_members_and_active_holders(self):
        graph = load_control(); graph['serialization_groups']['W_owner'].remove('prepared')
        self.reject(graph, 'PREPARATION_HOLD_BINDING')
        graph = load_control(); graph['cells'][0]['state'] = 'DONE'
        self.reject(graph, 'PREPARATION_HOLDER_BINDING')
        graph = load_control(); graph['cells'].append({'id': 'other', 'state': 'ACTIVE', 'deps': []})
        graph['population']['total_cells'] = 3; graph['serialization_groups']['W_owner'].append('other')
        self.reject(graph, 'PREPARATION_HOLDER_BINDING')

    def test_predecessor_population_and_identity_cannot_be_fabricated(self):
        for mode in ('missing', 'duplicate', 'foreign', 'identity'):
            with self.subTest(mode=mode):
                graph = load_control(); predecessors = preparation(graph)['record']['predecessors']
                if mode == 'missing': predecessors.clear()
                if mode == 'duplicate': predecessors.append(copy.deepcopy(predecessors[0]))
                if mode == 'foreign': predecessors[0]['cell_id'] = 'absent'
                if mode == 'identity': predecessors[0]['identity']['reason'] = 'NON_SOURCE_PRODUCT'
                self.reject(graph, 'PREPARATION_PREDECESSOR')

    def test_full_declaration_and_state_are_required(self):
        for state in ('DONE', 'ACTIVE'):
            graph = load_control(); graph['cells'][1]['state'] = state
            self.reject(graph, 'PREPARATION_STATE')
        graph = load_control(); graph['cells'][1]['preparation'] = {'raw_guard': 'preserved'}
        self.reject(graph, 'PREPARATION_DECLARATION')
        graph = load_control(); preparation(graph)['final_composed_only'] = True
        self.reject(graph, 'PREPARATION_EFFECT_BOUNDARY')
        graph = load_control(); preparation(graph)['effect_class'] = 'SOURCE_MUTATION'
        self.reject(graph, 'PREPARATION_EFFECT_BOUNDARY')

    def test_kinds_allowed_forbidden_rank_and_receipt_bindings(self):
        cases = [('kinds', ['SOURCE_MUTATION'], 'PREPARATION_KINDS'),
                 ('allowed_work', ['BRIEF'], 'PREPARATION_ALLOWED_WORK'),
                 ('forbidden_work', ['SOURCE_MUTATION'], 'PREPARATION_FORBIDDEN_WORK'),
                 ('receipt', 'CURRENT', 'PREPARATION_RECEIPT')]
        for field, value, reason in cases:
            with self.subTest(field=field):
                graph = load_control(); target = preparation(graph) if field == 'kinds' else preparation(graph)['record']
                target[field] = value; self.reject(graph, reason)
        for rank in (True, -1, '1'):
            graph = load_control(); preparation(graph)['rank']['cost'] = rank
            self.reject(graph, 'PREPARATION_RANK')

    def test_guard_sets_have_source_order_semantics(self):
        graph = load_control(); record = preparation(graph)['record']
        for name in ('forbidden_work', 'invalidators', 'activation_revalidation'):
            record[name].reverse()
        record['invalidators'].append('OWNER_ADDITIONAL_INVALIDATOR')
        record['receipt'] = record['receipt'].replace('/G0001@', '/G0000@')
        self.decode(graph)  # WG's literal syntax permits this token; no receipt authentication.
        graph = load_control(); preparation(graph)['kinds'] = ['REVIEW_PLAN', 'BRIEF']
        preparation(graph)['record']['allowed_work'] = ['REVIEW_PLAN', 'BRIEF']
        self.reject(graph, 'PREPARATION_KINDS')

    def test_invalidation_revalidation_and_assumption_boundaries(self):
        for name in ('invalidators', 'activation_revalidation', 'inspected_paths', 'proposed_paths'):
            graph = load_control(); preparation(graph)['record'][name] = []
            self.reject(graph, 'PREPARATION_')
        graph = load_control(); preparation(graph)['record']['interface_assumptions'] = {}
        self.reject(graph, 'PREPARATION_INTERFACE_ASSUMPTIONS')
        graph = load_control(); preparation(graph)['record']['interface_assumptions']['constructed-interface'] = 'unknown'
        self.reject(graph, 'PREPARATION_INTERFACE_ASSUMPTIONS')

    def test_done_source_predecessor_uses_local_product_identity_without_authority_credit(self):
        graph = product_control(); result = self.decode(graph)
        self.assertTrue(any(r['record_type'] == 'WorkPreparation' for r in result['records']))
        self.assertIn('PRODUCT_AUTHORITY_BYTES_NOT_CAPTURED', {o['reason'] for o in result['omissions']})
        bad = copy.deepcopy(graph)
        preparation(bad)['record']['predecessors'][-1]['identity']['tree'] = 'f' * 40
        self.reject(bad, 'PREPARATION_PREDECESSOR_IDENTITY')
        bad = copy.deepcopy(graph); bad['cells'][-1]['result']['product']['commit'] = 'short'
        self.reject(bad, 'WORK_PRODUCT_IDENTITY')

    def test_product_authority_pin_binding_is_local_and_paths_remain_inert(self):
        graph = product_control(); graph['authority']['qualified_product_contract']['path'] = '/never/open/authority'
        self.reject(graph, 'WORK_PRODUCT_AUTHORITY_BINDING')
        graph['integration_topology']['product_contract']['authority_sha256'] = sha(graph['authority']['qualified_product_contract'])
        self.decode(graph)

    def test_supplied_product_bindings_must_match_local_products_and_population(self):
        graph = product_control(); graph['integration_topology']['product_contract']['product_bindings'][0]['tree'] = 'f' * 40
        self.reject(graph, 'WORK_PRODUCT_RESULT_BINDING')
        graph = product_control(); graph['integration_topology']['product_contract']['done_classification'] = {}
        self.reject(graph, 'WORK_PRODUCT_CLASSIFICATION')
        graph = product_control(); graph['integration_topology']['product_contract']['future_consumers'][0]['cell_id'] = 'absent'
        self.reject(graph, 'WORK_PRODUCT_FUTURE_CONSUMER')

    def test_product_composition_cycle_and_rejected_target_refuse(self):
        graph = product_control(); contract = graph['integration_topology']['product_contract']
        other = {'owner_kind': 'NON_CELL', 'owner': 'declared-owner', 'commit': '6' * 40,
                 'tree': '7' * 40, 'review_sha256': '8' * 64}
        contract['non_cell_owners'] = ['declared-owner']; contract['product_bindings'].append(other)
        composed = {'kind': 'COMPOSED', 'target': other['commit']}
        graph['cells'][-1]['result']['disposition'] = composed
        contract['disposition_bindings'][0].update(composed)
        contract['disposition_bindings'].append({'product_commit': other['commit'], 'kind': 'INTEGRATED', 'target': '9' * 40})
        self.decode(graph)
        bad = copy.deepcopy(graph)
        bad['integration_topology']['product_contract']['disposition_bindings'][1].update(kind='COMPOSED', target='1' * 40)
        self.reject(bad, 'WORK_PRODUCT_COMPOSITION_CYCLE')
        bad = copy.deepcopy(graph)
        bad['integration_topology']['product_contract']['disposition_bindings'][1].update(kind='REJECTED', target='1' * 40)
        self.reject(bad, 'WORK_PRODUCT_COMPOSITION_CURRENTNESS')

    def test_product_composition_authorization_binds_supplied_owner_review_and_receipt(self):
        graph = product_control(); contract = graph['integration_topology']['product_contract']
        contract['composition_authorizations'] = [{'owner': 'prepared', 'products': ['1' * 40],
            'qualification_review_sha256': '3' * 64,
            'integration_authority': graph['authority']['qualified_product_contract']['receipt']}]
        self.decode(graph)
        for field, changed in (('owner', 'absent'), ('products', ['a' * 40]),
                               ('qualification_review_sha256', 'b' * 64), ('integration_authority', 'CURRENT')):
            with self.subTest(field=field):
                bad = copy.deepcopy(graph)
                bad['integration_topology']['product_contract']['composition_authorizations'][0][field] = changed
                self.reject(bad, 'WORK_PRODUCT_COMPOSITION_AUTHORIZATION')

    def test_product_named_join_and_duplicate_owner_bindings_refuse(self):
        graph = product_control(); contract = graph['integration_topology']['product_contract']
        contract['join_owners'] = ['prepared']
        self.reject(graph, 'WORK_PRODUCT_JOIN_OWNER')
        graph = product_control(); contract = graph['integration_topology']['product_contract']
        contract['product_bindings'].append(copy.deepcopy(contract['product_bindings'][0]))
        self.reject(graph, 'WORK_PRODUCT_BINDING_POPULATION')

    def test_product_missing_exact_authority_input_is_an_omission(self):
        graph = product_control(); del graph['integration_topology']; del graph['authority']
        result = self.decode(graph)
        self.assertIn('PRODUCT_AUTHORITY_INPUTS_NOT_CAPTURED', {o['reason'] for o in result['omissions']})
        self.assertTrue(any(r['record_type'] == 'WorkPreparation' for r in result['records']))

    def test_unknown_optional_product_fields_preserve_raw_with_omission(self):
        graph = load_control(); graph['integration_topology'] = {'future_owner_field': {'raw': 'retained'}}
        result = self.decode(graph)
        self.assertTrue(any(r['record_type'] == 'WorkGraph' and r['observation'] == graph for r in result['records']))
        self.assertIn('OWNER_OPTIONAL_CONTRACT_NOT_VALIDATED', {o['reason'] for o in result['omissions']})


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0], *remaining])
