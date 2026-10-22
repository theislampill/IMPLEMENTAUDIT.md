"""Unauthenticated owner-format fixtures through the real R0038 pure decoder.

Run with --target /absolute/path/to/operational_query_policy.py after integration.
No native owner helper, source file named in data, or host is opened.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--target', type=Path, default=HERE / 'consumer.py')
args, remaining = parser.parse_known_args()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


subject = load(args.target, 'occurrence_consumer_subject')
fixtures = load(HERE / 'fixture-snippets.py', 'occurrence_source_fixtures')


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False).encode()).hexdigest()


def candidate():
    """Closed constructor-shaped C; fake pins intentionally confer no provenance."""
    contexts = {}
    for index, role in enumerate(('parent', 'child'), 1):
        contexts[role] = {'path': '/fixture/' + role + '.jsonl',
            'physical': {'device': 1, 'inode': index},
            'metadata': {'offset': 0, 'bytes': 10, 'sha256': sha(role + '-metadata'),
                         'embedded_ordinal': 0, 'physical_line': 1},
            'allowed_ranges': [{'offset': 0, 'bytes': 20000}],
            'metadata_payload_digest': sha(role), 'history_start_ordinal': 1}
    pins = []
    def record(role, number, label, call_id=None):
        result = {'path': contexts[role]['path'], 'physical': contexts[role]['physical'],
            'role': role, 'locator': {'offset': number * 100, 'bytes': 10,
            'sha256': sha(label), 'embedded_ordinal': number, 'physical_line': number + 1},
            'timestamp': '2026-01-01T00:00:%02dZ' % number,
            'message_or_call_id': call_id or 'fixture-' + label}
        pins.append(result)
        return result
    for n, label in enumerate(('open', 'spawn', 'spawn-output'), 1):
        record('parent', n, label)
    authorization = record('parent', 4, 'authorization')
    exchange = {'call': record('child', 5, 'delivery', 'reused-call-id'),
                'result': record('child', 6, 'delivery-output', 'reused-call-id')}
    original = {'call': record('child', 7, 'original', 'reused-call-id'),
                'result': record('child', 8, 'original-output', 'reused-call-id')}
    use = {'call': record('child', 9, 'use', 'use-id'),
           'result': record('child', 10, 'use-output', 'use-id')}
    final = record('child', 11, 'final')
    delivered = record('parent', 12, 'parent-delivery')
    accepting = record('parent', 13, 'acceptance')
    scope = [{'id': 'fixture-boundary-1', 'version': 1, 'kind': 'completed-compaction'}]
    obligation, observation, ex = sha('obligation'), sha('observation'), sha('exchange')
    parent = {'thread_id': 'fixture-parent', 'agent_path': '/root'}
    child = {'thread_id': 'fixture-child', 'parent_thread_id': 'fixture-parent',
             'agent_path': '/root/reconcile'}
    cutoff = {'fixture_cutoff': 'source-owned-opaque-cutoff', 'bytes': 810}
    r = {'obligation_digest': obligation, 'observation_id': observation,
         'child_observation_exchange_identity': ex, 'scope': scope,
         'result_pin': {'path': '/fixture/result/result.json', 'bytes': 100, 'sha256': sha('result')},
         'result_physical': {'device': 2, 'inode': 10},
         'members': [{'pin': {'path': '/fixture/result/member.json', 'bytes': 20,
                              'sha256': sha('member')}, 'physical': {'device': 2, 'inode': 11}}],
         'child_final': final, 'parent_delivery': delivered, 'bound_exchange': original,
         'use': use, 'authorization_record': authorization,
         'hold_history': {'path': contexts['child']['path'], 'physical': contexts['child']['physical'],
                          'prefix_bytes': 810, 'prefix_sha256': sha('held-original-prefix'),
                          'physical_records': 9, 'history_start_ordinal': 1,
                          'host_producer_authenticated': False, 'original_bind': original}}
    a = {'record': accepting, 'value': {'schema': 'implementaudit.compaction-reconciliation-acceptance.v1',
         'action': 'ACCEPT_BOUNDED_RECONCILIATION', 'parent_identity': parent,
         'actual_child_identity': child, 'obligation_digest': obligation, 'observation_id': observation,
         'child_observation_exchange_identity': ex, 'actual_result_digest': sha(r),
         'accepted_boundary_versions': scope, 'observation_source_cutoff': cutoff,
         'authority_ceiling': 'NONE'}}
    return {'schema': 'implementaudit.compaction-unconsumed-acquisition.v1',
        'policy_digest': sha('policy'),
        'producer_environment_identity': {'profile_id': 'codex-desktop-0.153.4-collaboration-public-v1',
            'parent_metadata': contexts['parent']['metadata_payload_digest'],
            'child_metadata': contexts['child']['metadata_payload_digest']},
        'parent_identity': parent, 'actual_child_identity': child,
        'assignment_identity': sha('assignment'), 'obligation_digest': obligation,
        'observation_id': observation, 'covered_boundary_versions': scope,
        'O_U_exchange_USE_R_A_identities': {'O': {'path': '/fixture/obligation.json', 'bytes': 80,
                                               'sha256': obligation},
            'U': authorization, 'exchange': exchange, 'USE': use, 'R': r, 'A': a},
        'physical_source_and_cutoff_identities': {**contexts, 'compaction_cutoff': cutoff, 'records': pins},
        'exact_result_digest': sha(r), 'exact_acceptance_digest': sha(a),
        'source_origin_validation': 'UNESTABLISHED', 'host_producer_authenticated': False,
        'authority_ceiling': 'NONE'}


def stage_evidence():
    base = {'owner_id': 'fixture-owner', 'host_id': 'fixture-host', 'host_session_id': 'fixture-session',
            'binding_generation': 'G0001', 'selected_child': 'audit-state',
            'route_transaction_id': 'sha256:' + sha('transaction'),
            'obligation_id': 'sha256:' + sha('obligation'), 'packet_digest': 'sha256:' + sha('packet')}
    stages = []
    for stage in ('LOAD', 'USE', 'DISPOSE'):
        receipt = {'schema': 'implementaudit.host-holon-stage-receipt.v1', **base,
                   'stage': stage, 'event_id': 'fixture-event-' + stage}
        receipt['receipt_identity'] = 'sha256:' + sha(receipt)
        stages.append(receipt)
    return {'schema': 'implementaudit.resolved-holon-execution-evidence.v1', **base, 'stages': stages}


class OccurrenceConsumerTests(unittest.TestCase):
    def decode(self, kind, value):
        self.assertTrue(hasattr(subject, 'decode_occurrence_capture'), 'actual pure consumer interface is absent')
        before = copy.deepcopy(value)
        result = subject.decode_occurrence_capture(kind, value)
        self.assertEqual(value, before, 'decoder mutated captured input')
        keys = {json.dumps(row['key'], sort_keys=True) for row in result['records']}
        self.assertEqual(len(keys), len(result['records']))
        for row in result['records']:
            if 'source_key' in row:
                self.assertIn(json.dumps(row['source_key'], sort_keys=True), keys)
                self.assertIn(json.dumps(row['target_key'], sort_keys=True), keys)
            self.assertNotIn('establishes', row)
            self.assertNotIn('currentness', row)
        return result

    def reject(self, kind, value, reason):
        with self.assertRaisesRegex(ValueError, reason):
            self.decode(kind, value)

    def test_candidate_keeps_exact_original_scope_and_member(self):
        c = candidate()
        result = self.decode('result-occurrence', c)
        self.assertTrue(any(row['observation'] == c for row in result['records']))
        self.assertTrue(any(row['record_type'] == 'SourceOccurrence' for row in result['records']))
        self.assertTrue(any(row['record_type'] == 'Artifact' for row in result['records']))
        self.assertIn('PRIOR_RETRY_CLASSIFICATION_NOT_EXPORTED', {x['reason'] for x in result['omissions']})

    def test_changed_selection_cannot_substitute_original_even_with_same_call_id(self):
        c = candidate()
        c['O_U_exchange_USE_R_A_identities']['R']['bound_exchange'] = copy.deepcopy(c['O_U_exchange_USE_R_A_identities']['USE'])
        self.reject('result-occurrence', c, 'BOUND_EXCHANGE_NOT_ORIGINAL')

    def test_changed_physical_pin_refused_even_with_same_bytes(self):
        for field, new_value in [('path', '/fixture/copied-child.jsonl'),
                                 ('physical', {'device': 1, 'inode': 999})]:
            with self.subTest(field=field):
                c = candidate()
                c['physical_source_and_cutoff_identities']['records'][4][field] = new_value
                self.reject('result-occurrence', c, 'SOURCE_OCCURRENCE_BINDING')

    def test_offset_hash_and_cutoff_are_identity_critical(self):
        for field, value in [('offset', 501), ('sha256', 'f' * 64), ('embedded_ordinal', 77)]:
            with self.subTest(field=field):
                c = candidate()
                c['physical_source_and_cutoff_identities']['records'][4] = copy.deepcopy(c['physical_source_and_cutoff_identities']['records'][4])
                c['physical_source_and_cutoff_identities']['records'][4]['locator'][field] = value
                self.reject('result-occurrence', c, 'REFERENCED_OCCURRENCE_OMITTED')
        c = candidate()
        c['O_U_exchange_USE_R_A_identities']['R']['hold_history']['prefix_bytes'] = 805
        self.reject('result-occurrence', c, 'ORIGINAL_COMPLETION_OUTSIDE_CUTOFF')

    def test_missing_member_or_uncovered_acceptance_does_not_pass(self):
        c = candidate()
        c['O_U_exchange_USE_R_A_identities']['R']['members'] = []
        self.reject('result-occurrence', c, 'RESULT_MEMBER_CLOSURE')
        c = candidate()
        c['covered_boundary_versions'] = copy.deepcopy(c['covered_boundary_versions'])
        c['covered_boundary_versions'].append({'id': 'fixture-boundary-2', 'version': 1, 'kind': 'completed-compaction'})
        self.reject('result-occurrence', c, 'RESULT_OR_ACCEPTANCE_SCOPE')

    def test_result_members_stay_inside_captured_result_directory(self):
        def changed(result_path, member_path):
            c = candidate()
            r = c['O_U_exchange_USE_R_A_identities']['R']
            a = c['O_U_exchange_USE_R_A_identities']['A']
            r['result_pin']['path'] = result_path
            r['members'][0]['pin']['path'] = member_path
            c['exact_result_digest'] = a['value']['actual_result_digest'] = sha(r)
            c['exact_acceptance_digest'] = sha(a)
            return c
        for result_path, member_path in (
                ('/fixture/result/result.json', '/fixture/result/nested/member.json'),
                ('C:\\fixture\\result\\result.json', 'C:\\fixture\\result\\nested\\member.json'),
                ('\\\\server\\share\\result\\result.json', '\\\\server\\share\\result\\member.json')):
            with self.subTest(result=result_path, member=member_path):
                self.decode('result-occurrence', changed(result_path, member_path))
        for result_path, member_path in (
                ('/fixture/result/result.json', '/outside/member.json'),
                ('/fixture/result/result.json', '/fixture/result-other/member.json'),
                ('/fixture/result/result.json', '/fixture/result/../member.json'),
                ('/fixture/result/result.json', 'relative/member.json'),
                ('C:\\fixture\\result\\result.json', 'D:\\fixture\\result\\member.json'),
                ('\\\\server\\share\\result\\result.json', '\\\\other\\share\\result\\member.json')):
            with self.subTest(result=result_path, member=member_path):
                self.reject('result-occurrence', changed(result_path, member_path), 'FOREIGN_RESULT_MEMBER')

    def test_result_artifact_member_ceiling_is_distinct_from_total_custody(self):
        for bucket in ('result_pin', 'member'):
            for amount, allowed in ((1048576, True), (1048577, False)):
                with self.subTest(bucket=bucket, amount=amount):
                    c = candidate()
                    r = c['O_U_exchange_USE_R_A_identities']['R']
                    a = c['O_U_exchange_USE_R_A_identities']['A']
                    pin = r['result_pin'] if bucket == 'result_pin' else r['members'][0]['pin']
                    pin['bytes'] = amount
                    c['exact_result_digest'] = a['value']['actual_result_digest'] = sha(r)
                    c['exact_acceptance_digest'] = sha(a)
                    if allowed:
                        self.decode('result-occurrence', c)
                    else:
                        self.reject('result-occurrence', c, 'RESULT_ARTIFACT_BYTE_BOUND')
        c = candidate()
        r = c['O_U_exchange_USE_R_A_identities']['R']
        result = {'schema': 'implementaudit.compaction-reconciliation-result.v1',
                  **{key: r[key] for key in ('obligation_digest', 'observation_id', 'child_observation_exchange_identity')},
                  'exact_observed_boundary_versions': r['scope'], 'code_and_skill_pins': {},
                  'status': 'SUCCEEDED', 'currentness': 'UNRESOLVED', 'measured_epoch': 'UNRESOLVED',
                  'frontier': 'constructed frontier', 'members': [copy.deepcopy(r['members'][0]['pin'])],
                  'authority_ceiling': 'NONE'}
        result['members'][0]['bytes'] = 1048576
        self.decode('result-occurrence', result)
        result['members'][0]['bytes'] += 1
        self.reject('result-occurrence', result, 'RESULT_ARTIFACT_BYTE_BOUND')

    def test_duplicate_physical_observation_is_not_independent_evidence(self):
        c = candidate()
        c['physical_source_and_cutoff_identities']['records'].append(copy.deepcopy(c['physical_source_and_cutoff_identities']['records'][0]))
        self.reject('result-occurrence', c, 'DUPLICATE_PHYSICAL_OCCURRENCE')

    def test_correlated_physical_line_labels_preserve_one_physical_occurrence(self):
        # CRO actual_result permits physical_line=None; acquire_candidate dedups
        # the full pin, so both labels can occur in its actual records array.
        c = candidate()
        pins = c['physical_source_and_cutoff_identities']['records']
        count = len(pins)
        original = c['O_U_exchange_USE_R_A_identities']['R']['bound_exchange']['call']
        correlated = copy.deepcopy(original)
        correlated['locator']['physical_line'] = None
        pins.append(correlated)
        result = self.decode('result-occurrence', c)
        physical = [r for r in result['records'] if r['record_type'] == 'SourceOccurrence']
        self.assertEqual(len(physical), count)
        grouped = [r for r in physical if original in r['observation']['captured_pins']]
        self.assertEqual(len(grouped), 1)
        self.assertEqual(grouped[0]['observation']['captured_pins'], [original, correlated])
        self.assertIn('CORRELATED_SOURCE_PIN_LABELS_NOT_INDEPENDENT', {x['reason'] for x in result['omissions']})
        self.assertEqual(sum(r.get('relation_type') == 'SELECTS_ORIGINAL_OCCURRENCE' for r in result['records']), 2)

    def test_correlated_labels_cannot_hide_conflicting_physical_facts(self):
        for field, changed in [('sha256', 'f' * 64), ('bytes', 11), ('embedded_ordinal', 99)]:
            with self.subTest(field=field):
                c = candidate()
                pins = c['physical_source_and_cutoff_identities']['records']
                contradictory = copy.deepcopy(pins[6])
                contradictory['locator']['physical_line'] = None
                contradictory['locator'][field] = changed
                pins.append(contradictory)
                self.reject('result-occurrence', c, 'CONFLICTING_PHYSICAL_OCCURRENCE')

    def test_equal_bytes_at_another_offset_are_separate_occurrences(self):
        c = candidate()
        pins = c['physical_source_and_cutoff_identities']['records']
        repeated = copy.deepcopy(pins[6])
        repeated['locator'].update(offset=1400, embedded_ordinal=14, physical_line=15)
        repeated['timestamp'] = '2026-01-01T00:00:14Z'
        pins.append(repeated)
        result = self.decode('result-occurrence', c)
        self.assertEqual(sum(r['record_type'] == 'SourceOccurrence' for r in result['records']), len(pins))
        self.assertEqual(sum(r.get('relation_type') == 'SELECTS_ORIGINAL_OCCURRENCE' for r in result['records']), 2)

    def test_full_graph_preserves_unknown_guard_fields_and_relations(self):
        graph = {'schema': 'implementaudit.work-graph.v1', 'population': {'total_cells': 3},
                 'cells': [{'id': 'source', 'state': 'DONE', 'deps': [], 'full_guard': {'named': 'retained'}},
                           {'id': 'test', 'state': 'READY', 'deps': ['source']},
                           {'id': 'future', 'state': 'BLOCKED', 'deps': ['test']}],
                 'serialization_groups': {'W_owner': ['source', 'test'], 'R_resource': ['future']}}
        result = self.decode('member-coverage', graph)
        self.assertTrue(any(row['observation'] == graph for row in result['records']))
        self.assertEqual(sum(row.get('relation_type') == 'DEPENDS_ON' for row in result['records']), 2)
        self.assertEqual(sum(row['record_type'] == 'Group' for row in result['records']), 2)
        bad = copy.deepcopy(graph); bad['cells'].pop()
        self.reject('member-coverage', bad, 'frontier count')
        bad = copy.deepcopy(graph); bad['serialization_groups']['W_owner'].append('missing')
        self.reject('member-coverage', bad, 'unknown group member')
        bad = copy.deepcopy(graph); bad['cells'][0]['deps'] = ['future']
        self.reject('member-coverage', bad, 'dependency cycle')

    def test_optional_product_contract_is_preserved_but_not_qualified(self):
        graph = {'schema': 'implementaudit.work-graph.v1', 'population': {'total_cells': 1},
                 'cells': [{'id': 'prepared', 'state': 'BLOCKED', 'deps': [], 'preparation': {'raw_guard': 'preserved'}}],
                 'serialization_groups': {}}
        self.reject('member-coverage', graph, 'PREPARATION_DECLARATION')
        del graph['cells'][0]['preparation']
        graph['integration_topology'] = {'future_product_field': {'raw_guard': 'preserved'}}
        result = self.decode('member-coverage', graph)
        self.assertTrue(any(row['record_type'] == 'WorkGraph' and row['observation'] == graph for row in result['records']))
        self.assertIn('OWNER_OPTIONAL_CONTRACT_NOT_VALIDATED', {x['reason'] for x in result['omissions']})

    def test_graph_explicit_null_optional_metadata_matches_owner_contract(self):
        # WG _validate_graph checks frontier/digest only when each is not None.
        graph = {'schema': 'implementaudit.work-graph.v1', 'population': {'total_cells': 1},
                 'cells': [{'id': 'one', 'state': 'READY', 'deps': []}],
                 'serialization_groups': {}, 'digest': None, 'frontier': None}
        result = self.decode('member-coverage', graph)
        self.assertTrue(any(r['record_type'] == 'WorkGraph' and r['observation'] == graph for r in result['records']))
        bad = copy.deepcopy(graph); bad['frontier'] = {}
        self.reject('member-coverage', bad, 'stale frontier')
        bad = copy.deepcopy(graph); bad['digest'] = 'f' * 64
        self.reject('member-coverage', bad, 'WORK_GRAPH_DIGEST')

    def test_actual_coverage_fixture_retains_blocked_recovery_and_sibling(self):
        facts, projection = fixtures.coverage_case()
        result = self.decode('member-coverage', {'facts': facts, 'projection': projection})
        edges = [row['observation'] for row in result['records'] if row['record_type'] == 'CoverageEdge']
        self.assertEqual({edge['id'] for edge in edges}, {edge['id'] for edge in facts['edges']})
        self.assertTrue(any(edge['id'] == 'native-recovery' and edge['gates']['native_currentness'] == 'MISSING' for edge in edges))

    def test_done_custody_may_be_absent_but_pending_custody_remains_required(self):
        # ALC violations compares .get() for custody; nonempty is state != DONE.
        facts, projection = fixtures.coverage_case()
        done = next(e for e in facts['edges'] if e['state'] == 'DONE')
        shown = next(e for e in projection['edges'] if e['id'] == done['id'])
        custody = ('owner', 'consumer', 'reconsider', 'next_action')
        for field in custody:
            done.pop(field)
            shown.pop(field)
        result = self.decode('member-coverage', {'facts': facts, 'projection': projection})
        omissions = [o for o in result['omissions'] if o['reason'] == 'DONE_CUSTODY_FIELDS_ABSENT']
        self.assertEqual(len(omissions), 1)
        self.assertEqual(omissions[0]['member'], done['id'])
        self.assertEqual(omissions[0]['fields'], list(custody))
        self.assertTrue(any(r['record_type'] == 'CoverageEdge' and r['observation'] == done for r in result['records']))
        facts, projection = fixtures.coverage_case()
        pending = next(e for e in facts['edges'] if e['state'] == 'PENDING')
        pending.pop('owner')
        self.reject('member-coverage', {'facts': facts, 'projection': projection}, 'pending-custody')

    def test_historical_view_uses_exact_retained_dictionary(self):
        facts, projection = fixtures.coverage_case()
        projection['views'][-1].update(status='HISTORICAL', **copy.deepcopy(facts['history'][0]))
        facts['history'].append({**copy.deepcopy(facts['history'][0]), 'unreferenced_label': 'retained'})
        self.decode('member-coverage', {'facts': facts, 'projection': projection})
        facts['history'].pop(0)
        self.reject('member-coverage', {'facts': facts, 'projection': projection}, 'historical-scope')

    def test_stale_latest_and_missing_ancestor_sibling_group_are_refused(self):
        facts, projection = fixtures.coverage_case()
        bad = copy.deepcopy(projection); bad['views'][0]['binding']['event'] = 'material-join-1'
        self.reject('member-coverage', {'facts': facts, 'projection': bad}, 'projection-freshness')
        bad = copy.deepcopy(projection); bad['ancestors'] = ['recovery']
        self.reject('member-coverage', {'facts': facts, 'projection': bad}, 'ancestor-coverage')
        bad = copy.deepcopy(projection); bad['edges'] = [r for r in bad['edges'] if r['id'] != 'rlgwo-prep']
        self.reject('member-coverage', {'facts': facts, 'projection': bad}, 'edge-population')

    def test_return_is_not_join_and_source_scope_is_not_native(self):
        facts, projection = fixtures.coverage_case()
        bad = copy.deepcopy(projection); bad['backward_joins'].append('returned-source')
        self.reject('member-coverage', {'facts': facts, 'projection': bad}, 'accepted-backward-joins')
        bad = copy.deepcopy(projection); bad['evidence_scope'] = 'NATIVE'
        self.reject('member-coverage', {'facts': facts, 'projection': bad}, 'evidence-scope')

    def test_stages_preserve_exact_receipts_without_return_or_join(self):
        value = stage_evidence()
        result = self.decode('child-visibility', value)
        stages = [row['observation']['stage'] for row in result['records'] if row['record_type'] == 'LifecycleEvent']
        self.assertEqual(stages, ['LOAD', 'USE', 'DISPOSE'])
        self.assertIn('ACCEPTANCE_JOIN_PARENT_COMPLETION_NOT_ESTABLISHED', {x['reason'] for x in result['omissions']})
        bad = copy.deepcopy(value); bad['stages'][1] = copy.deepcopy(bad['stages'][0])
        self.reject('child-visibility', bad, 'STAGE_SEQUENCE')
        bad = copy.deepcopy(value); bad['stages'][1]['packet_digest'] = 'sha256:' + 'a' * 64
        self.reject('child-visibility', bad, 'STAGE_CONTEXT')

    def test_standalone_host_receipt_retains_ascii_escaped_digest_contract(self):
        # H0 command_record_holon_stage uses json.dumps default ensure_ascii=True.
        receipt = copy.deepcopy(stage_evidence()['stages'][0])
        receipt['binding_generation'] = 'G0001'
        receipt['event_id'] = 'fixture-événement'
        body = {k: v for k, v in receipt.items() if k != 'receipt_identity'}
        receipt['receipt_identity'] = 'sha256:' + hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
        result = self.decode('child-visibility', receipt)
        self.assertTrue(any(r['record_type'] == 'LifecycleEvent' and r['observation'] == receipt for r in result['records']))
        self.assertIn('CROSS_OWNER_RECEIPT_ENCODING_DIFFERS', {o['reason'] for o in result['omissions']})
        self.assertTrue(any(s['path'].endswith('/host-session-binding.py')
                            for s in subject.OCCURRENCE_FORMAT_SOURCES['child-visibility']))
        wrong = copy.deepcopy(receipt); wrong['receipt_identity'] = 'sha256:' + sha(body)
        self.reject('child-visibility', wrong, 'STAGE_RECEIPT_DIGEST')

    def test_resolved_route_receipt_retains_utf8_digest_contract(self):
        # RT digest_json intentionally differs from H0 for non-ASCII body text.
        value = stage_evidence()
        receipt = value['stages'][0]
        receipt['event_id'] = 'fixture-événement'
        body = {k: v for k, v in receipt.items() if k != 'receipt_identity'}
        receipt['receipt_identity'] = 'sha256:' + sha(body)
        result = self.decode('child-visibility', value)
        self.assertIn('CROSS_OWNER_RECEIPT_ENCODING_DIFFERS', {o['reason'] for o in result['omissions']})
        receipt['receipt_identity'] = 'sha256:' + hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
        self.reject('child-visibility', value, 'STAGE_RECEIPT_DIGEST')

    def test_procedure_and_ini_cannot_become_governed_receipt(self):
        self.reject('child-visibility', {'SKILL_SELECTED': 'verification', 'LOAD': 'VERIFIED'}, 'KNOWN_CHILD_VISIBILITY_FORMAT')
        self.reject('child-visibility', '```ini\nLOAD=VERIFIED\n```', 'CAPTURE_OBJECT_REQUIRED')
        value = {'schema': 'implementaudit.child-return.v1', 'obligation_id': 'sha256:' + sha('o'),
                 'route_transaction_id': 'sha256:' + sha('t'), 'packet_digest': 'sha256:' + sha('p'),
                 'status': 'RETURNED', 'payload': {'SKILL_SELECTED': 'verification', 'LOAD': 'VERIFIED'}}
        result = self.decode('child-visibility', value)
        stages = [row['observation'].get('stage') for row in result['records'] if row['record_type'] == 'LifecycleEvent']
        self.assertEqual(stages, ['RETURN'])
        self.assertFalse(any(row['record_type'] == 'ChildRole' for row in result['records']))

    def test_satified_projection_keeps_unverified_native_stages(self):
        value = {'required_sequence': ['OPEN', 'LOAD', 'USE', 'RETURN', 'DISPOSE', 'RECONCILE'],
                 'completed': ['OPEN', 'RETURN', 'RECONCILE'], 'selected_child': 'audit-state',
                 'route_transaction_id': 'sha256:' + sha('t'), 'obligation_id': 'sha256:' + sha('o'),
                 'identity_bound': True, 'unverified': ['LOAD', 'USE', 'DISPOSE'],
                 'child_authority': 'NONE', 'child_can_route': False,
                 'governor_reconciliation_required': False, 'canonical_credit': False}
        result = self.decode('child-visibility', value)
        self.assertEqual([r['observation']['stage'] for r in result['records'] if r['record_type'] == 'LifecycleEvent'],
                         ['OPEN', 'RETURN', 'RECONCILE'])
        bad = copy.deepcopy(value); bad['canonical_credit'] = True
        self.reject('child-visibility', bad, 'LIFECYCLE_CREDIT')

    def test_invalid_scalars_cycles_and_boolean_offsets_refuse(self):
        c = candidate(); c['physical_source_and_cutoff_identities']['records'][0]['locator']['offset'] = True
        self.reject('result-occurrence', c, 'RECORD_LOCATOR')
        c = candidate(); c['extra'] = float('nan')
        self.reject('result-occurrence', c, 'CAPTURE_SCALAR')
        cycle = {}; cycle['loop'] = cycle
        self.reject('member-coverage', cycle, 'CAPTURE_CYCLE')
        facts, projection = fixtures.coverage_case()
        facts['edges'][0]['direction'] = ['INWARD']
        self.reject('member-coverage', {'facts': facts, 'projection': projection}, 'COVERAGE_EDGE')
        acceptance = candidate()['O_U_exchange_USE_R_A_identities']['A']['value']
        acceptance['parent_identity'] = None
        self.reject('result-occurrence', acceptance, 'PARENT_IDENTITY')


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0], *remaining])
