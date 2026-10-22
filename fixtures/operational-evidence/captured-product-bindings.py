"""Bounded source-confirmed RR04/product controls through the captured API."""
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
spec = importlib.util.spec_from_file_location('remaining_bindings_subject', args.target)
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


def fixture(name):
    return json.loads((HERE / 'captured-review-preimages' / (name + '.json')).read_text())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def reseal(graph):
    contract = graph['integration_topology']['product_contract']
    source = graph['authority']['qualified_product_contract']
    document = canonical({k: v for k, v in contract.items() if k != 'authority_sha256'})
    source.update(bytes=len(document), sha256=hashlib.sha256(document).hexdigest())
    contract['authority_sha256'] = hashlib.sha256(canonical(source)).hexdigest()


def proposal_fixture():
    graph = fixture('product_control')
    graph['cells'].append({'id': 'composer', 'state': 'READY', 'deps': ['done-source']})
    graph['population']['total_cells'] += 1
    proposal = {'owner': 'composer', 'products': ['1' * 40, '6' * 40],
                'qualification_review_sha256': '3' * 64,
                'integration_authority': graph['authority']['qualified_product_contract']['receipt']}
    graph['integration_topology']['composition_proposals'] = [proposal]
    graph['integration_topology']['product_contract']['composition_authorizations'] = [copy.deepcopy(proposal)]
    reseal(graph)
    return graph


class RemainingBindingsTests(unittest.TestCase):
    def decode(self, value):
        before = copy.deepcopy(value)
        with patch('builtins.open', side_effect=AssertionError('capture file IO')), \
             patch('pathlib.Path.open', side_effect=AssertionError('capture path IO')):
            result = subject.decode_occurrence_capture('member-coverage', value)
        self.assertEqual(value, before)
        keys = {canonical(row['key']) for row in result['records']}
        self.assertEqual(len(keys), len(result['records']))
        for row in result['records']:
            for field in ('source_key', 'target_key'):
                if field in row:
                    self.assertIn(canonical(row[field]), keys)
            self.assertNotIn('establishes', row)
            self.assertNotIn('currentness', row)
        return result

    def reject(self, value, reason):
        with self.assertRaisesRegex(ValueError, reason):
            self.decode(value)

    def test_exact_multiline_cost_boundary_is_preserved(self):
        graph = fixture('preparation_multiline_cost_boundary')
        result = self.decode(graph)
        self.assertTrue(any(r['record_type'] == 'WorkPreparation' and
                            r['observation'] == graph['cells'][1]['preparation'] for r in result['records']))

    def test_cost_boundary_uses_nonempty_scalar_string_without_identity_text_limits(self):
        for prose in (' \n', 'Résumé\n' * 1000, '\tbounded\r\nprose'):
            graph = fixture('preparation_control')
            graph['cells'][1]['preparation']['record']['cost_boundary'] = prose
            self.decode(graph)
        for value in ('', None, False, []):
            graph = fixture('preparation_control')
            graph['cells'][1]['preparation']['record']['cost_boundary'] = value
            self.reject(graph, 'PREPARATION_RECORD')
        graph = fixture('preparation_control')
        graph['cells'][1]['preparation']['record']['cost_boundary'] = '\ud800'
        self.reject(graph, 'CAPTURE_SCALAR')
        graph = fixture('preparation_control')
        graph['cells'][1]['preparation']['record']['graph_path'] += '\n'
        self.reject(graph, 'PREPARATION_RECORD')

    def test_exact_supplied_product_control_projects_realised_noncell_and_heads(self):
        graph = fixture('product_control'); result = self.decode(graph)
        noncell = graph['integration_topology']['qualified_products'][0]
        self.assertTrue(any(r['record_type'] == 'WorkNonCellProduct' and r['observation'] == noncell for r in result['records']))
        self.assertTrue(any(r['record_type'] == 'IntegrationHeads' for r in result['records']))
        self.assertIn('PRODUCT_AUTHORITY_BYTES_NOT_CAPTURED', {o['reason'] for o in result['omissions']})
        self.assertIn('PRODUCT_QUALIFICATION_NOT_ESTABLISHED', {o['reason'] for o in result['omissions']})

    def test_exact_noncell_identity_contradiction_refuses(self):
        self.reject(fixture('product_noncell_tree_contradiction'), 'WORK_PRODUCT_NONCELL_BINDING')

    def test_exact_foreign_integration_head_refuses(self):
        self.reject(fixture('product_foreign_integration_head'), 'WORK_PRODUCT_INTEGRATION_HEAD')

    def test_exact_unknown_composition_owner_refuses(self):
        self.reject(fixture('product_unknown_composition_owner'), 'WORK_PRODUCT_PROPOSAL_OWNER')

    def test_exact_realised_self_supersession_refuses(self):
        self.reject(fixture('product_self_supersession'), 'WORK_PRODUCT_SELF_SUPERSESSION')

    def test_noncell_disposition_owner_and_population_are_bound(self):
        graph = fixture('product_control')
        graph['integration_topology']['qualified_products'][0]['result']['disposition']['target'] = 'a' * 40
        self.reject(graph, 'WORK_PRODUCT_NONCELL_DISPOSITION')
        graph = fixture('product_control'); graph['integration_topology']['qualified_products'][0]['owner'] = 'absent'
        self.reject(graph, 'WORK_PRODUCT_NONCELL_BINDING')
        graph = fixture('product_control'); graph['integration_topology']['qualified_products'].append(
            copy.deepcopy(graph['integration_topology']['qualified_products'][0]))
        self.reject(graph, 'WORK_PRODUCT_NONCELL_OWNER')
        graph = fixture('product_control'); graph['integration_topology']['qualified_products'] = []
        self.reject(graph, 'WORK_PRODUCT_RUNTIME_CENSUS')

    def test_known_runtime_fields_have_exact_shapes(self):
        for field, value, reason in (('qualified_products', {}, 'WORK_PRODUCT_NONCELL'),
                                     ('integration_heads', [], 'WORK_PRODUCT_INTEGRATION_HEAD'),
                                     ('integration_heads', ['short'], 'WORK_PRODUCT_INTEGRATION_HEAD'),
                                     ('composition_proposals', {}, 'WORK_PRODUCT_PROPOSAL')):
            graph = fixture('product_control'); graph['integration_topology'][field] = value
            self.reject(graph, reason)

    def test_valid_proposal_preserves_data_and_matches_exact_authorization(self):
        graph = proposal_fixture(); result = self.decode(graph)
        proposal = graph['integration_topology']['composition_proposals'][0]
        self.assertTrue(any(r['record_type'] == 'CompositionProposal' and r['observation'] == proposal for r in result['records']))
        self.assertIn('PRODUCT_COMPOSITION_ACTIVATION_NOT_ESTABLISHED', {o['reason'] for o in result['omissions']})
        graph['integration_topology']['product_contract']['composition_authorizations'] = []
        reseal(graph)
        self.reject(graph, 'WORK_PRODUCT_PROPOSAL_AUTHORIZATION')

    def test_proposal_supplied_dependency_and_hold_predicates(self):
        graph = proposal_fixture(); graph['cells'][-1]['state'] = 'BLOCKED'
        self.reject(graph, 'WORK_PRODUCT_PROPOSAL_DEPENDENCIES')
        graph = proposal_fixture(); graph['cells'][-1]['deps'].append('holder')
        self.reject(graph, 'WORK_PRODUCT_PROPOSAL_DEPENDENCIES')
        graph = proposal_fixture(); graph['serialization_groups']['W_owner'].append('composer')
        self.reject(graph, 'WORK_PRODUCT_PROPOSAL_HOLD')

    def test_proposal_duplicate_owner_and_exact_product_order(self):
        graph = proposal_fixture(); graph['integration_topology']['composition_proposals'].append(
            copy.deepcopy(graph['integration_topology']['composition_proposals'][0]))
        self.reject(graph, 'WORK_PRODUCT_PROPOSAL_OWNER')
        graph = proposal_fixture(); graph['integration_topology']['composition_proposals'][0]['products'].reverse()
        self.reject(graph, 'WORK_PRODUCT_PROPOSAL_PRODUCTS')

    def test_missing_operands_are_named_omissions_not_false_consistency(self):
        graph = fixture('product_control'); del graph['integration_topology']['qualified_products']
        result = self.decode(graph)
        self.assertIn('PRODUCT_NONCELL_REALISATIONS_NOT_CAPTURED', {o['reason'] for o in result['omissions']})
        graph = fixture('product_control'); del graph['integration_topology']['integration_heads']
        result = self.decode(graph)
        self.assertIn('PRODUCT_INTEGRATION_HEADS_NOT_CAPTURED', {o['reason'] for o in result['omissions']})
        graph = proposal_fixture(); del graph['integration_topology']['product_contract']; del graph['authority']
        result = self.decode(graph)
        reasons = {o['reason'] for o in result['omissions']}
        self.assertTrue({'NON_CELL_PRODUCT_BINDINGS_NOT_CAPTURED', 'COMPOSITION_AUTHORIZATION_INPUT_NOT_CAPTURED'} <= reasons)
        self.assertTrue(any(r['record_type'] == 'CompositionProposal' for r in result['records']))

    def test_known_intrinsic_shape_and_self_supersession_checked_without_contract(self):
        graph = fixture('product_control'); del graph['integration_topology']['product_contract']; del graph['authority']
        graph['integration_topology']['qualified_products'][0]['result']['product']['tree'] = 'short'
        self.reject(graph, 'WORK_PRODUCT_IDENTITY')
        graph = fixture('product_self_supersession'); del graph['integration_topology']['product_contract']; del graph['authority']
        self.reject(graph, 'WORK_PRODUCT_SELF_SUPERSESSION')


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0], *remaining])
