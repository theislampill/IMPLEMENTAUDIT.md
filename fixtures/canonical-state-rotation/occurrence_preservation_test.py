#!/usr/bin/env python3
"""Occurrence preservation controls, with opt-in pinned historical documents.

The normal controls use explicitly constructed protocol subjects. Set
R0039_OCCURRENCE_INPUTS to the existing historical-cold-receiving/inputs
directory to qualify the original documentary records through an isolated real
Git archive and a fresh Python reader. R0039_OCCURRENCE_FRONTIER optionally
selects the pinned later owner frontier; only two selected documentary JOIN
rows are exported after whole-file size/hash verification. The five original
carriers remain unchanged. Native transcripts, private/replacement bodies and
real pending stores are never opened. Documentary acceptance is not native
pending consumption.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


F = load('occurrence_projection_fixture', HERE / 'protected_projection_v2_test.py')
M = F.MODULE

# These are original, bounded documentary carriers, not admitted native inputs.
PINS = {
    'boundary13520': ('post-compaction-audit-state-13520/RECONCILIATION.json', 65516,
                     '0c78e6fd649877673e33006e2e4ed54fa6015e7cb87e188bb7a06b29cb7644ed'),
    'boundary14114': ('post-compaction-audit-state-14114/RECONCILIATION.json', 19373,
                     '0c07c68762045f4f9bf937baa0fd52fb7c0413bbefc945996ca14358238ee26b'),
    'boundary_archive': ('TWO_BOUNDARY_ARCHIVE_READBACK.json', 2244,
                         '5f70f30e96c462070d0c76c21eea83cedd4b9ddb57b8651c745c947001fcde27'),
    'occurrence_source': ('thread9-2-compaction-occurrence-review-05/MANIFEST.json', 4751,
                         'b4d1877a604c10df3fea29e9326305ea496ad8f0e6e153a71d908e3e11d5337a'),
    'occurrence_source_join': ('thread9-2-compaction-occurrence-review-join-05.json', 2484,
                              '547e9d90122a736c77ee2a13ecf49484842c1022459e09d9866f28057ab0cf03'),
}
FRONTIER_PIN = (2038090, '1feebd44cc33a4ca9630bb9f4576fef98546ddd7d9d3ceecea1de09388176ebe')
FRONTIER_SELECTION = ((118, 13520, '2026-09-10T13:26:13.714078+00:00'),
                      (125, 14114, '2026-09-10T14:06:39.334084+00:00'))


def selected_frontier_rows(value):
    """Extract exact documentary successors without exporting the private frontier."""
    rows = {}
    for index, boundary, accepted_at in FRONTIER_SELECTION:
        selected = value['execution_topology']['children'][index]
        original = PINS['boundary' + str(boundary)]
        if (selected['id'] != 'post_compaction_audit_state_' + str(boundary)
                or selected['boundary_id'] != 'root-raw-compaction-' + str(boundary)
                or selected['status'] != 'RETURNED_ACCEPTED_JOINED_POST_COMPACTION_RECONCILIATION'
                or selected['JOINed'] is not True or selected['accepted_utc'] != accepted_at
                or selected['RETURN']['bytes'] != original[1] or selected['RETURN']['sha256'] != original[2]
                or selected['governor_acceptance'] != 'BOUNDED_NONAUTHORITATIVE_PREPARATION_STATE_RECONCILIATION'
                or selected['product_hook_pending_store_credit'] is not False
                or selected['canonical_currentness'] is not False or selected['canonical_effect_authority'] != 'NONE'
                or selected['native_route_receipt_credit'] != 'NONE' or selected['parent_complete'] is not False
                or selected['DISPOSE'] != 'UNVERIFIED_NATIVE_RECEIPT; WORKER_STOPPED'):
            raise ValueError('documentary successor differs from its original return or authority ceiling')
        rows['/execution_topology/children/' + str(index)] = {
            key: selected[key] for key in ('id', 'boundary_id', 'status', 'JOINed', 'accepted_utc',
                'governor_acceptance', 'product_hook_pending_store_credit', 'canonical_currentness',
                'canonical_effect_authority', 'native_route_receipt_credit', 'parent_complete', 'DISPOSE')}
        rows['/execution_topology/children/' + str(index)]['return_pin'] = {
            'bytes': original[1], 'sha256': original[2]}
    return {'source_bytes': FRONTIER_PIN[0], 'source_sha256': FRONTIER_PIN[1], 'selected_rows': rows}


def pinned_frontier_selection(path):
    path = Path(path).absolute()
    before = os.lstat(path)
    size, digest = FRONTIER_PIN
    if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
            or getattr(before, 'st_file_attributes', 0) & 0x400 or before.st_size != size):
        raise ValueError('frontier physical identity/size mismatch')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(size + 1)
        after = os.fstat(stream.fileno())
    identity = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
    if (identity(before) != identity(opened) or identity(opened) != identity(after)
            or identity(after) != identity(os.lstat(path)) or len(raw) != size or F.sha(raw) != digest):
        raise ValueError('frontier exact source pin/custody mismatch')
    # No parser sees unpinned bytes, and no unselected frontier row is returned.
    return selected_frontier_rows(json.loads(raw))


def pinned_documents(base):
    """Bound paths and bytes before reading this selected public document set."""
    base = Path(base).absolute()
    result = {}
    for name, (relative, size, digest) in PINS.items():
        path = base / relative
        for parent in (base, *reversed(path.relative_to(base).parents[:-1])):
            selected = parent if parent.is_absolute() else base / parent
            info = os.lstat(selected)
            if not stat.S_ISDIR(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
                raise ValueError('historical input directory is not physical')
        before = os.lstat(path)
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or getattr(before, 'st_file_attributes', 0) & 0x400 or before.st_size != size):
            raise ValueError('historical document identity/size mismatch: ' + name)
        with path.open('rb') as stream:
            opened = os.fstat(stream.fileno())
            raw = stream.read(size + 1)
            after = os.fstat(stream.fileno())
        identity = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
        if (identity(before) != identity(opened) or identity(opened) != identity(after)
                or identity(after) != identity(os.lstat(path)) or len(raw) != size or F.sha(raw) != digest):
            raise ValueError('historical document pin/custody mismatch: ' + name)
        result[name] = raw
    return result


def historical_facts(documents, frontier=None):
    """Extract only the independently checkable documentary scope, not authority."""
    old, current, archive, reviewed, joined = (json.loads(documents[name]) for name in PINS)
    assert old['boundary']['id'] == 'root-raw-compaction-13520'
    assert old['boundary']['covers_only_boundary'] == 13520
    assert old['boundary']['raw_prefix_last_line_observed'] == 13781
    assert old['boundary']['future_boundary_coverage'] is False
    assert old['lifecycle']['GOVERNOR_ACCEPTANCE'] == old['lifecycle']['JOIN'] == 'PENDING'
    assert current['accepted_ancestry']['previous_audit']['JOINed'] is True
    assert current['accepted_ancestry']['previous_audit']['boundary_id'] == old['boundary']['id']
    assert current['accepted_ancestry']['previous_audit_covers_current_boundary'] is False
    assert current['accepted_ancestry']['previous_reconciliation']['sha256'] == PINS['boundary13520'][2]
    assert current['status'] == 'RETURNED_PENDING_GOVERNOR_ACCEPTANCE'
    assert current['boundary']['id'] == 'root-raw-compaction-14114'
    assert current['boundary']['latest_checked_line'] == 14276
    assert current['boundary']['previous13520_credit_reused'] is False
    assert current['lifecycle']['governor_acceptance'] == current['lifecycle']['JOIN'] == 'PENDING'
    assert reviewed['source_subject'] == joined['source_subject']
    assert reviewed['source_manifest'] == joined['source_manifest']
    assert joined['ACCEPTED'] is True and joined['JOINED'] is True
    assert joined['native_or_package_qualification'] is False and joined['source_adoption'] is False
    assert joined['PARENT_COMPLETE'] is False
    records = archive['records']
    assert [row['line'] for row in records] == [13520, 13533, 14114, 14135]
    for first, second in zip(old['boundary']['records'], records[:2]):
        assert first['physical_line'] == second['line']
        assert first['sha256'] == second['actual_sha256'] == second['expected_sha256']
        assert first['bytes_including_lf'] == second['actual_bytes'] == second['expected_bytes']
    for first, second in zip(current['boundary']['evidence'], records[2:]):
        assert (first['line'], first['offset'], first['bytes'], first['sha256']) == (
            second['line'], second['offset'], second['actual_bytes'], second['actual_sha256'])
    facts = {
        'boundary13520': {'id': old['boundary']['id'], 'cutoff_line': 13781,
                          'seal_acceptance': 'PENDING', 'later_documentary_acceptance': True,
                          'native_consumption': 'UNPROVED', 'covers_14114': False},
        'boundary14114': {'id': current['boundary']['id'], 'cutoff_line': 14276,
                          'seal_acceptance': 'PENDING', 'native_consumption': 'UNPROVED',
                          'later_documentary_acceptance': 'NOT_SUPPLIED_IN_RETURN_PACKET',
                          'reuses_13520': False, 'native_consumption_obligation': True},
        'original_occurrences': [{key: row[key] for key in ('line', 'offset', 'actual_bytes', 'actual_sha256')}
                                 for row in records],
        'h0_identity': 'UNPROVED', 'original_physical_inode': 'NOT_PRESERVED_BY_ARCHIVE',
        'consumer_source_subject': reviewed['source_subject']['sha256'],
        'consumer_source_manifest': reviewed['source_manifest']['sha256'],
        'consumer_adoption': False, 'host_producer_authenticated': False,
        'authority': 'DOCUMENTARY_ONLY_NO_NATIVE_PENDING_CONSUMPTION',
    }
    if frontier is not None:
        for index, boundary, _ in FRONTIER_SELECTION:
            selected = frontier['selected_rows']['/execution_topology/children/' + str(index)]
            facts['boundary' + str(boundary)].update(
                later_documentary_acceptance=selected['JOINed'],
                documentary_accepted_at=selected['accepted_utc'],
                product_hook_pending_store_credit=selected['product_hook_pending_store_credit'],
                canonical_effect_authority=selected['canonical_effect_authority'],
                native_route_receipt_credit=selected['native_route_receipt_credit'],
                native_dispose=selected['DISPOSE'])
    return facts


def parse_pair(bodies):
    state, roadmap, owners, artifacts = F.fixture_pair(bodies)
    return M.parse_canonical_pair_v2(state, roadmap, owner_map=owners, artifacts=artifacts)


def project(preimage):
    return M.derive_hot_pair_v2(preimage, transition=None,
                               archive_pointers=F.archive_pointers(preimage), **F.LIMITS)


def row(record_id, status, description, evidence_refs=None):
    return {'record_id': record_id, 'status': status, 'description': description,
            'scope': 'R0039 original criterion-5 preservation; no authority grant',
            'evidence_refs': evidence_refs or ['evidence']}


class OccurrencePreservation(unittest.TestCase):
    def test_selected_prior_retry_and_physical_identity_are_not_interchangeable(self):
        bodies = F.fixture_bodies()
        pending = bodies['STATE']['payload']['pending_boundaries']['value']
        pending[1]['retry'] = {'state': 'SUPPORTED_RETRY', 'original_occurrence_id': 'boundary-1',
                               'supported_evidence_ref': 'evidence'}
        original = parse_pair(bodies)
        projected = project(original)
        self.assertTrue(M.verify_projection_equivalence_v2(original, projected)['equivalent'])
        # Each mutation is against the selected preimage, not a newly self-authored
        # owner map. Equal bytes/call labels do not license replacing an occurrence.
        changes = [(['selected_occurrence_id'], 'copied-unselected-occurrence'),
                   (['prior_occurrence_ids'], ['foreign-prior']),
                   (['physical_source', 'file_identity'], 'copied/other-file.jsonl'),
                   (['physical_source', 'offset'], 0),
                   (['physical_source', 'ordinal'], 17),
                   (['physical_source', 'source_binding'], '0' * 64),
                   (['physical_source', 'sha256'], '1' * 64),
                   (['retry', 'original_occurrence_id'], 'foreign-original'),
                   (['retry', 'supported_evidence_ref'], 'work_graph')]
        for keys, value in changes:
            changed = copy.deepcopy(projected)
            selected = changed['payload']['STATE']['pending_boundaries']['value'][1]
            for key in keys[:-1]:
                selected = selected[key]
            selected[keys[-1]] = value
            with self.subTest(field=keys), self.assertRaises(M.ProjectionV2Error):
                M.verify_projection_equivalence_v2(original, changed)

    def test_later_correct_response_does_not_rewrite_original_or_consume_pending(self):
        bodies = F.fixture_bodies()
        selected = bodies['STATE']['payload']['pending_boundaries']['value'][0]
        selected['result'] = {'state': 'SUCCEEDED', 'original_response_sha256': F.sha(b'wrong original'),
                              'returned_response_sha256': F.sha(b'later corrected response')}
        original = parse_pair(bodies)
        projected = project(original)
        result = projected['payload']['STATE']['pending_boundaries']['value'][0]
        self.assertNotEqual(result['result']['original_response_sha256'], result['result']['returned_response_sha256'])
        self.assertEqual(result['consumption'], {'state': 'PENDING', 'witness': None, 'covered_boundary_ids': []})
        changed = copy.deepcopy(projected)
        changed['payload']['STATE']['pending_boundaries']['value'][0]['result']['original_response_sha256'] = result['result']['returned_response_sha256']
        with self.assertRaises(M.ProjectionV2Error):
            M.verify_projection_equivalence_v2(original, changed)

    def test_pending_failed_reserved_and_uncovered_are_retained_without_currentness(self):
        for result_state in ('PENDING', 'FAILED'):
            bodies = F.fixture_bodies()
            selected = bodies['STATE']['payload']['pending_boundaries']['value'][0]
            selected['result']['state'] = result_state
            original = parse_pair(bodies)
            projected = project(original)
            pending = projected['payload']['STATE']['pending_boundaries']['value']
            self.assertEqual(pending[0], selected)
            self.assertEqual(pending[0]['uncovered_successors'], ['boundary-2'])
            self.assertEqual(pending[1]['consumption']['state'], 'PENDING')
            for entry in pending:
                self.assertTrue(entry['audit_state_required'])
                self.assertEqual(entry['currentness'], {'state': 'UNRESOLVED', 'epoch': None})
                self.assertEqual(entry['reservation']['state'], 'RESERVED')
            for key, value in (('audit_state_required', False), ('uncovered_successors', [])):
                changed = copy.deepcopy(projected)
                changed['payload']['STATE']['pending_boundaries']['value'][0][key] = value
                with self.subTest(result=result_state, field=key), self.assertRaises(M.ProjectionV2Error):
                    M.verify_projection_equivalence_v2(original, changed)

    def test_tc06_continuing_consumer_duties_survive_disabled_new_rotations(self):
        bodies = F.fixture_bodies()
        grant = bodies['STATE']['payload']['authorisations']['value'][0]
        grant.update(status='REVOKED', applicability='DOES_NOT_APPLY', subject='New rotation admission')
        duties = ['Read permanent migration marker', 'Resolve pointer and matching receipt',
                  'Retrieve retained typed archive', 'Preserve pending acceptance duties']
        bodies['ROADMAP']['payload']['obligations']['value'].extend(
            row('TC06-duty-' + str(index), 'OPEN', duty) for index, duty in enumerate(duties))
        original = parse_pair(bodies)
        projected = project(original)
        self.assertEqual(projected['payload']['STATE']['authorisations']['value'][0], grant)
        self.assertEqual(projected['payload']['ROADMAP']['obligations'], original['payload']['ROADMAP']['obligations'])
        for index in range(len(duties)):
            changed = copy.deepcopy(projected)
            changed['payload']['ROADMAP']['obligations']['value'][index + 1]['status'] = 'DONE'
            with self.subTest(duty=index), self.assertRaises(M.ProjectionV2Error):
                M.verify_projection_equivalence_v2(original, changed)

    def test_tc11_archive_preserves_historical_scope_and_current_use_refusal(self):
        bodies = F.fixture_bodies()
        history = bodies['STATE']['history'][0]
        self.assertEqual(history['record_id'], 'TC11-admission-history')
        original = parse_pair(bodies)
        projected = project(original)
        pointer = next(item for item in projected['archive_pointers'] if item['record_id'] == history['record_id'])
        self.assertEqual(pointer['record_sha256'], F.sha(F.canonical(history)))
        self.assertEqual(pointer['authority'], 'ARCHIVED_ONLY_HISTORY')
        self.assertEqual(history['payload']['current_applicability'], 'INVALIDATED_CURRENT_USE')
        self.assertTrue(history['payload']['original_scope'])
        self.assertTrue(history['payload']['historical_refusal'])

    @unittest.skipUnless(os.environ.get('R0039_OCCURRENCE_FRONTIER'), 'exact later documentary frontier not selected')
    def test_later_documentary_join_retains_return_pins_and_zero_native_credit(self):
        selected = pinned_frontier_selection(os.environ['R0039_OCCURRENCE_FRONTIER'])
        self.assertEqual(len(selected['selected_rows']), 2)
        for index, boundary, accepted_at in FRONTIER_SELECTION:
            entry = selected['selected_rows']['/execution_topology/children/' + str(index)]
            self.assertEqual(entry['return_pin']['sha256'], PINS['boundary' + str(boundary)][2])
            self.assertTrue(entry['JOINed'])
            self.assertEqual(entry['accepted_utc'], accepted_at)
            self.assertFalse(entry['product_hook_pending_store_credit'])
            self.assertEqual(entry['canonical_effect_authority'], 'NONE')
        # Constructed negative controls cannot promote a changed/foreign return,
        # erase a later ordinary JOIN, or turn it into native credit.
        children = [None] * 126
        for index, _, _ in FRONTIER_SELECTION:
            entry = copy.deepcopy(selected['selected_rows']['/execution_topology/children/' + str(index)])
            entry['RETURN'] = entry.pop('return_pin')
            children[index] = entry
        candidate = {'execution_topology': {'children': children}}
        for field, changed_value in (('JOINed', False), ('product_hook_pending_store_credit', True),
                                     ('canonical_effect_authority', 'CURRENT'), ('native_route_receipt_credit', 'PASS'),
                                     ('boundary_id', 'foreign-boundary'), ('accepted_utc', 'later-invented-time')):
            changed = copy.deepcopy(candidate)
            changed['execution_topology']['children'][125][field] = changed_value
            with self.subTest(field=field), self.assertRaises(ValueError):
                selected_frontier_rows(changed)
        changed = copy.deepcopy(candidate)
        changed['execution_topology']['children'][125]['RETURN']['sha256'] = PINS['boundary13520'][2]
        with self.assertRaises(ValueError):
            selected_frontier_rows(changed)

    @unittest.skipUnless(os.environ.get('R0039_OCCURRENCE_INPUTS'), 'exact original documentary input directory not selected')
    def test_original_documents_survive_real_archive_and_fresh_process_readback(self):
        documents = pinned_documents(os.environ['R0039_OCCURRENCE_INPUTS'])
        frontier_path = os.environ.get('R0039_OCCURRENCE_FRONTIER')
        selected = pinned_frontier_selection(frontier_path) if frontier_path else None
        facts = historical_facts(documents, selected)
        if selected is not None:
            documents['ordinary_acceptance_successor'] = F.canonical(selected)
        archive = load('occurrence_archive_fixture', HERE / 'archive_v2_test.py')
        bodies = F.fixture_bodies()
        for name in documents:
            bodies['STATE']['artifact_refs'].append({'artifact_id': name, 'owner': 'R0033/continuity',
                'role': 'EVIDENCE', 'locator': 'historical/' + name + '.json', 'object_format': 'sha1'})
            bodies['STATE']['payload']['runtime_artifacts']['value'].append(name)
        bodies['STATE']['payload']['evidence_ceilings']['value'].append(row(
            'original-occurrence-authority-ceiling', 'UNVERIFIED', F.canonical(facts).decode(), list(documents)))
        bodies['ROADMAP']['payload']['obligations']['value'].append(row(
            'root-raw-compaction-14114-pending', 'BLOCKED',
            'Native consumption of original14114 remains unproved. Preserve its later ordinary acceptance separately; do not replay.',
            ['boundary14114', 'occurrence_source', 'occurrence_source_join']))
        bodies['STATE']['payload']['non_verdicts']['value'].append(row(
            'root-raw-compaction-13520-ordinary-acceptance', 'PRESERVED',
            '13520 was later accepted only as bounded ordinary reconciliation; it covers no14114 native consumption.',
            ['boundary13520', 'boundary14114']))
        texts = json.loads(F.FIXTURE.read_text())['artifact_texts']
        texts.update({key: raw.decode('utf-8') for key, raw in documents.items()})
        original_pair = archive.F.fixture_pair
        with tempfile.TemporaryDirectory(prefix='r0039-occurrence-') as temporary:
            with mock.patch.object(archive.F, 'fixture_bodies', return_value=bodies), mock.patch.object(
                    archive.F, 'fixture_pair', side_effect=lambda value: original_pair(value, texts)):
                subject = archive.make_subject(Path(temporary) / 'repo')
            prepared = archive.prepare(subject)
            final = archive.M.finalize_canonical_projection(subject['repo'], subject['run'], prepared,
                                                             archive.transition(subject, prepared))
            pointer_path = Path(temporary) / 'pointer.json'
            pointer_path.write_bytes(F.canonical(final['pointer']))
            cold = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--cold-read',
                                   str(subject['repo']), str(subject['run']), str(pointer_path)],
                                  capture_output=True, timeout=30, check=False)
            self.assertEqual(cold.returncode, 0, cold.stderr.decode())
            received = json.loads(cold.stdout)
            self.assertEqual(received['payload'], {role: bodies[role]['payload'] for role in ('STATE', 'ROADMAP')})
            self.assertEqual(received['document_hashes'], {name: F.sha(raw) for name, raw in documents.items()})
            if selected is not None:
                received_facts = json.loads(next(entry['description'] for entry in
                    received['payload']['STATE']['evidence_ceilings']['value']
                    if entry['record_id'] == 'original-occurrence-authority-ceiling'))
                for _, boundary, accepted_at in FRONTIER_SELECTION:
                    entry = received_facts['boundary' + str(boundary)]
                    self.assertEqual(entry['seal_acceptance'], 'PENDING')
                    self.assertTrue(entry['later_documentary_acceptance'])
                    self.assertEqual(entry['documentary_accepted_at'], accepted_at)
                    self.assertFalse(entry['product_hook_pending_store_credit'])
                    self.assertEqual(entry['native_consumption'], 'UNPROVED')
            self.assertEqual(received['authority_ceiling'], 'NO_CURRENTNESS_AUTHORITY')
            self.assertEqual(received['history_authority'], ['ARCHIVED_ONLY_HISTORY'] * 2)
            self.assertTrue(received['tc11']['original_scope'])
            self.assertEqual(received['tc11']['current_applicability'], 'INVALIDATED_CURRENT_USE')
            self.assertIn('historical_refusal', received['tc11'])
            self.assertFalse(any('/current-generations/' in ref for ref in archive.git(
                subject['repo'], 'for-each-ref', '--format=%(refname)').decode().splitlines()))


def cold_read(repo, run, pointer_path):
    """Separate-process mechanical receiving, never a native/model canary."""
    archive = load('occurrence_archive_reader', HERE / 'archive_v2_test.py')
    pointer = json.loads(Path(pointer_path).read_bytes())
    received = archive.M.read_canonical_generation(Path(repo), Path(run), pointer)
    manifest = received['archive_manifest']
    documents = {entry['artifact_id']: F.sha(archive.M._blob(Path(repo), entry['blob_oid']))
                 for entry in manifest['entries'] if entry['artifact_id'] in {*PINS, 'ordinary_acceptance_successor'}}
    state = json.loads(received['state_bytes'].split(b'```json\n')[1].split(b'\n```')[0])
    histories = [archive.M.resolve_typed_archive_pointer_v2(Path(repo), item)
                 for item in state['archive_pointers'] if item['role'] == 'HISTORY_RECORD']
    tc11 = next(json.loads(item['bytes'])['payload'] for item in histories
                if json.loads(item['bytes'])['record_id'] == 'TC11-admission-history')
    print(F.canonical({'payload': received['protected_manifest']['PRESERVED_PAYLOAD']['payload'],
        'document_hashes': documents, 'authority_ceiling': 'NO_CURRENTNESS_AUTHORITY',
        'history_authority': [item['authority_ceiling'] for item in histories], 'tc11': tc11}).decode())


if __name__ == '__main__':
    if len(sys.argv) == 5 and sys.argv[1] == '--cold-read':
        cold_read(*sys.argv[2:])
    else:
        unittest.main()
