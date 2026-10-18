"""Source/interface controls only; constructed inputs grant no native credit."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(sys.argv.pop(1)).resolve()
spec = importlib.util.spec_from_file_location('oe_episode_tests', ROOT / 'scripts/operational-evidence.py')
oe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oe)
SEED = json.loads((ROOT / 'fixtures/operational-evidence/review-native-before.json').read_bytes())


def load_fixture(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


load_fixture('native_test_support', ROOT / 'fixtures/operational-evidence/native-episode-controls/native_test_support.py')
owner_fixture = load_fixture('episode_fixture_data', ROOT / 'fixtures/operational-evidence/native-episode-controls/test_episode_export.py')
saved_argv = sys.argv
try:
    sys.argv = ['route_fixture', str(ROOT)]
    route_fixture = load_fixture('episode_route_fixture', ROOT / 'fixtures/operational-evidence/native-route-projection.py')
finally:
    sys.argv = saved_argv


class NativeEpisodeProjectionTests(unittest.TestCase):
    def material(self):
        collections = route_fixture.NativeRouteProjectionTests().material(record_overrides={
            'route_state': 'OPEN', 'host_id': 'codex', 'host_session_id': 'fixture-parent'})
        native = collections['native_current']['value']
        episode = owner_fixture.FrozenExportTests().available()
        scope = native['route_graph']['route_scope']
        episode['owner']['canonical_route'] = copy.deepcopy(native['route'])
        episode['owner']['host_and_scope'] = {**scope['owner'], **scope['host'],
            **{key: native['route'][key] for key in ('obligation_id', 'route_transaction_id')}}
        peers = oe._native_episode_peer_bytes()
        producer_sha, contract_sha = [hashlib.sha256(raw).hexdigest() for path, raw in peers]
        episode['owner']['code_pins'].update({
            'implementaudit/scripts/compaction-audit-pending.py': producer_sha,
            'implementaudit/scripts/compaction-result-observation.py': contract_sha,
            'implementaudit/scripts/route-transaction.py': scope['source']['producer_sha256']})
        owner_fixture.FrozenExportTests().reseal(episode)
        native['native_episode'] = {'producer_sha256': producer_sha, 'contract_sha256': contract_sha, 'value': episode}
        return collections

    def payload(self, collections):
        return route_fixture.NativeRouteProjectionTests().payload(collections)

    def legacy_payload(self):
        collections = copy.deepcopy(SEED['collections'])
        material = oe._build_snapshot_material_v1(collections['native_current']['value'], collections,
            (ROOT / 'docs/operational-evidence-schema.json').read_bytes(),
            (ROOT / 'scripts/operational-evidence.py').read_bytes())
        return json.loads(material['payload_raw'])

    def test_missing_native_episode_stays_explicitly_unverified(self):
        value = self.legacy_payload()
        status = oe.evaluate_currentness(value)
        missing = [row for row in status['missing_or_omitted_state'] if row.get('code') == 'NATIVE_EPISODE_UNAVAILABLE']
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]['state'], 'UNVERIFIED')
        rows = oe.query_family(value, 'EXECUTION')['rows']
        episode = [row['record'] for row in rows if row['record']['record_type'] == 'NativeEpisodeCapability']
        self.assertEqual(len(episode), 1)
        self.assertEqual(episode[0]['currentness']['state'], 'UNVERIFIED')

    def test_no_override_missing_owner_is_nonacquiring(self):
        self.assertTrue(callable(getattr(oe, '_native_episode', None)))
        with patch.object(oe.subprocess, 'Popen', side_effect=AssertionError('unexpected acquisition')):
            self.assertIsNone(oe._native_episode())

    def test_available_episode_keeps_distinct_records_and_h0_gap(self):
        value = self.payload(self.material())
        rows = oe._snapshot_query_records_v1(value)
        kinds = {row['record']['record_type'] for row in rows}
        self.assertTrue({'NativeAcceptedEpisode', 'NativeResult', 'NativeAcceptance', 'NativeJoin',
            'NativePhysicalCustody', 'NativeResultOccurrence', 'NativeSourceTerminalRelease'} <= kinds)
        h0 = next(row['record'] for row in rows if row['record']['record_type'] == 'NativeLifecycleReceipts')
        self.assertEqual(h0['currentness']['state'], 'UNVERIFIED')
        missing = oe.evaluate_currentness(value)['missing_or_omitted_state']
        self.assertTrue(any(row.get('code') == 'NATIVE_H0_LIFECYCLE_UNAVAILABLE' for row in missing))
        joined = next(row['record'] for row in rows if row['record']['record_type'] == 'NativeJoin')
        why = oe.explain_history_why_v1(value, joined['id'])
        self.assertTrue({'NativeAcceptance', 'NativeResult', 'NativePhysicalCustody'} <=
                        {row['record_type'] for row in why['chain']})
        self.assertEqual(oe.diff_snapshots(value, value)['counts']['changed'], 0)

    def test_coherently_foreign_scope_cannot_cross_native_owners(self):
        for field in ('controller', 'transaction', 'producer_code'):
            collections = self.material()
            wrapped = collections['native_current']['value']['native_episode']
            value = wrapped['value']
            owner = value['owner']
            if field == 'controller':
                owner['canonical_route'].update(controller_id='foreign', ref='refs/implementaudit/route-decisions/foreign')
                owner['host_and_scope']['controller_id'] = 'foreign'
                owner['host_and_scope']['continuity_receipt'] = owner['host_and_scope']['continuity_receipt'].replace('/bounded-control/', '/foreign/')
            elif field == 'transaction':
                owner['canonical_route']['route_transaction_id'] = owner['host_and_scope']['route_transaction_id'] = 'sha256:' + '0' * 64
            else:
                owner['code_pins']['implementaudit/scripts/compaction-audit-pending.py'] = '0' * 64
            owner_fixture.FrozenExportTests().reseal(value)
            path, raw = oe._native_episode_peer_bytes()[1]
            contract = oe._native_module_from_bytes(raw, path, 'fixture_frozen_contract', '$fixture')
            contract.validate_frozen_episode_export_v1(value)  # Internally valid, externally foreign.
            with self.subTest(field=field), self.assertRaises(oe.OperationalEvidenceError):
                payload = self.payload(collections)
                oe.diff_snapshots(payload, payload)

    def test_unproved_second_boundary_remains_visible_and_unconsumed(self):
        for kind in ('UNRESOLVED_RESUME_OBSERVATION', 'UNRESOLVED_SIGNAL', 'AMBIGUOUS_MARKER_GROUP'):
            with self.subTest(kind=kind):
                self._unproved_second_boundary(kind)

    def _unproved_second_boundary(self, kind):
        collections = self.material()
        episode = collections['native_current']['value']['native_episode']['value']
        later = {'id': 'later-unresolved-delivery', 'kind': kind, 'version': 1}
        episode['pending']['observations'].append({**later, 'consumed_version': 0, 'assignment_children': []})
        episode['pending']['pending_scope'] = [later]
        episode['pending']['revision'] += 1
        owner_fixture.FrozenExportTests().reseal(episode)
        value = self.payload(collections)
        ordinary = oe.query_family(value, 'EXECUTION')['rows']
        current = oe.query_family(value, 'EXECUTION', current_only=True)['rows']
        row = next(row['record'] for row in ordinary if row['record']['record_type'] == 'NativePendingBoundary'
                   and row['record']['observation']['id'] == later['id'])
        self.assertEqual(row['currentness']['state'], 'UNVERIFIED')
        self.assertEqual(row['observation']['consumed_version'], 0)
        self.assertFalse(any(item['record']['id'] == row['id'] for item in current))
        self.assertEqual(value['aggregate'], 'DEGRADED')
        self.assertTrue(any(item.get('code') == 'NATIVE_PENDING_BOUNDARY_UNVERIFIED'
            and item.get('scope') == later['id'] for item in value['missing_or_omitted_state']))

    def test_covered_kind_and_overlapping_occurrence_never_become_current(self):
        for mutation in ('covered-kind', 'pair-overlap', 'cross-pair-overlap'):
            collections = self.material()
            episode = collections['native_current']['value']['native_episode']['value']
            if mutation == 'covered-kind':
                episode['pending']['observations'][0]['kind'] = 'AMBIGUOUS_MARKER_GROUP'
            else:
                role = 'call' if mutation == 'pair-overlap' else 'result'
                episode['occurrences']['occurrences'][0]['records'][role]['locator']['bytes'] = 6
            owner_fixture.FrozenExportTests().reseal(episode)
            with self.subTest(mutation=mutation), self.assertRaises(oe.OperationalEvidenceError):
                oe.query_family(self.payload(collections), 'EXECUTION', current_only=True)

    def test_frozen_episode_consumers_never_invoke_selected_owner(self):
        value = self.payload(self.material())
        original = oe._native_module_from_bytes
        def guarded(*args):
            module = original(*args)
            if hasattr(module, 'validate_frozen_episode_export_v1'):
                module._nonprotected_source_owner = lambda *a, **k: self.fail('private source lookup')
                module.artifact = lambda *a, **k: self.fail('source-input refresh')
            return module
        with patch.object(oe, '_native_module_from_bytes', side_effect=guarded), \
                patch.object(oe, '_native_episode', side_effect=AssertionError('episode acquisition')), \
                patch.object(oe, 'collect_native_current', side_effect=AssertionError('native acquisition')), \
                patch.object(oe.subprocess, 'Popen', side_effect=AssertionError('subprocess')):
            for family in oe.FAMILIES:
                oe.query_family(value, family)
            oe.diff_snapshots(value, value)


if __name__ == '__main__':
    unittest.main()
