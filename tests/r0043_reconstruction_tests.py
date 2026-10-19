"""Behavioral integrity tests for the R0043 repository-only reader (unallocated).

These are artifact/source tests, not evidence that a native owner accepted AMA.
Set the canonically unallocated R0043_PACKET for complete frozen-input integration.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(sys.argv.pop(1)).resolve()
READER = ROOT / 'scripts/r0043-reconstruct.py'
PACKET_VARIABLE = 'R0043_PACKET'  # canonically unallocated test input


def reseal(value):
    value.pop('projection_sha256', None)
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(',', ':')).encode()
    value['projection_sha256'] = hashlib.sha256(encoded).hexdigest()
    return value


class ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not READER.is_file():
            return
        spec = importlib.util.spec_from_file_location('r0043_reader', READER)
        cls.reader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.reader)
        cls.index = cls.reader.read_index(ROOT / 'docs/research/implementaudit/r0043-member-dispositions.json')

    def setUp(self):
        self.assertTrue(READER.is_file(), 'new repository reader is absent; this is not a runtime RED')

    def test_complete_unique_originals_keep_unknown_preparation(self):
        result = self.reader.check_index(self.index)
        self.assertEqual(result['originals'], 278)
        self.assertEqual(result['eaose'], 132)
        self.assertEqual(result['groups'], 32)
        self.assertEqual(result['scope'], 'DOCUMENTARY_INDEX_INTEGRITY_ONLY')
        row = next(r for r in self.index['rows'] if r['key'] == 'EAOSE:EAOSE-C026')
        self.assertEqual(row['source_status'], 'DOMAIN_SPECIFIC')
        self.assertEqual(row['historical_target']['disposition'], 'DEFERRED')
        self.assertIsNone(row['later_prepared_target'])
        self.assertIn('Flat roles, modules or services', row['source_obligation']['cheap_path'])

    def test_missing_nonprimary_original_is_not_replaced_by_memberships(self):
        changed = copy.deepcopy(self.index)
        changed['rows'] = [r for r in changed['rows'] if r['key'] != 'EAOSE:EAOSE-C132']
        changed['population']['originals'] = 1245
        with self.assertRaisesRegex(ValueError, 'population|original'):
            self.reader.check_index(reseal(changed))

    def test_invented_later_target_cannot_be_hidden_by_a_new_digest(self):
        changed = copy.deepcopy(self.index)
        next(r for r in changed['rows'] if r['key'] == 'EAOSE:EAOSE-C026')['later_prepared_target'] = 'FULLY_ABSORBED'
        with self.assertRaisesRegex(ValueError, 'unavailable|prepared'):
            self.reader.check_index(reseal(changed))

    def test_group_membership_cannot_be_promoted_to_receiving(self):
        changed = copy.deepcopy(self.index)
        changed['acceptance']['ama_278_32'] = 'ACCEPTED'
        with self.assertRaisesRegex(ValueError, 'acceptance|authority'):
            self.reader.check_index(reseal(changed))

    def test_dropped_negative_pair_is_detected_independently_of_digest(self):
        changed = copy.deepcopy(self.index)
        changed['relations']['no_material_pairs'] -= 1
        with self.assertRaisesRegex(ValueError, 'pair|relation'):
            self.reader.check_index(reseal(changed))

    def test_tc_parent_substitution_does_not_become_comparison_evidence(self):
        changed = copy.deepcopy(self.index)
        tc = next(r for r in changed['tc_findings'] if r['id'] == 'TC10')
        tc['parents'] = [p.replace('EMAS:EMAS-072', 'EMAS:EMAS-001') for p in tc['parents']]
        with self.assertRaisesRegex(ValueError, 'TC10|TC parent'):
            self.reader.check_index(reseal(changed))

    def test_unsafe_archive_names_are_refused_before_reading_members(self):
        for name in ['../escape', '/absolute', 'C:/host', 'a\\b', 'a/../escape', 'a//b']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.reader.safe_member(name)
        self.reader.safe_member('constituents/EAOSE.zip')

    def test_unknown_member_and_ambiguous_json_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'unknown member'):
            self.reader.index_row(self.index, 'EAOSE:EAOSE-C133')
        with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
            self.reader.core.parse('{"key":1,"key":2}')

    def test_accepted_eaa_qualified_identity_resolves_without_recounting(self):
        source = ROOT / 'docs/research/implementaudit/r0045-member-dispositions.json'
        if not source.is_file():
            self.skipTest('accepted EAA bytes absent in this authoring-only checkout')
        value = self.reader.accepted_member(ROOT, 'EAA', 'EAA-001')
        self.assertEqual(value['availability'], 'EXACT_ACCEPTED_MEMBER_BYTES')
        self.assertEqual(value['record']['id'], 'EAA:EAA-001')
        self.assertEqual(value['route']['issue'], 233)

    def test_missing_or_changed_projection_part_cannot_load_as_complete(self):
        self.assertTrue(hasattr(self.reader, 'write_index'), 'size-bounded content transport is unavailable')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'index.json'
            self.reader.write_index(path, self.index)
            self.assertEqual(self.reader.read_index(path), self.index)
            manifest = json.loads(path.read_bytes())
            first = path.parent / manifest['parts'][0]['file']
            original = first.read_bytes()
            first.write_bytes(original + b' ')
            with self.assertRaisesRegex(ValueError, 'part'):
                self.reader.read_index(path)
            first.unlink()
            with self.assertRaises((OSError, ValueError)):
                self.reader.read_index(path)

    @unittest.skipUnless(os.environ.get(PACKET_VARIABLE), 'full pinned packet is supplied only for custody integration')
    def test_full_source_reader_preserves_action_and_opposite_direction(self):
        corpus = self.reader.Corpus(Path(os.environ[PACKET_VARIABLE]), self.reader.read_lock(ROOT))
        result = self.reader.member_view(corpus, self.index, 'EAOSE:EAOSE-C026', ROOT)
        self.assertEqual(result['original']['CURRENT_STATUS'], 'DOMAIN_SPECIFIC')
        self.assertEqual(result['original']['CRITERION'], 'Cross-level responsibilities remain explicit rather than hidden by nesting.')
        self.assertIsNone(result['later_prepared_target'])
        self.assertEqual(result['source_intake']['global_qualified_key'], 'EAOSE:EAOSE-C026')
        self.assertEqual({g['cluster_id'] for g in result['groups']}, {'AMA-K001', 'AMA-K010'})
        self.assertTrue(result['explicit_pairs'])
        self.assertTrue(any(p['relation_status'] == 'NO_MATERIAL_RELATION' for p in result['explicit_pairs']))
        for relation in result['incident_relations']:
            if relation['reverse_relation_id']:
                reverse = result['independent_reverse_records'][relation['reverse_relation_id']]
                self.assertEqual(reverse['source_property'], relation['target_property'])
                self.assertEqual(reverse['target_property'], relation['source_property'])
        direct = self.reader.member_view(corpus, self.index, 'EAOSE:EAOSE-C120', ROOT)
        self.assertEqual(direct['original']['CURRENT_STATUS'], 'UNRESOLVED')
        self.assertNotEqual(direct['continuation']['if_selected'], result['continuation']['if_selected'])
        with self.assertRaisesRegex(ValueError, 'later|prepared'):
            self.reader.require_prepared(result)

    @unittest.skipUnless(os.environ.get(PACKET_VARIABLE), 'full pinned packet is supplied only for custody integration')
    def test_changed_packet_bytes_are_not_an_accepted_source(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'changed.zip'
            data = bytearray(Path(os.environ[PACKET_VARIABLE]).read_bytes())
            data[-1] ^= 1
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, 'packet identity'):
                self.reader.Corpus(path, self.reader.read_lock(ROOT))

    @unittest.skipUnless(os.environ.get(PACKET_VARIABLE), 'full pinned packet is supplied only for custody integration')
    def test_source_correspondence_rejects_laundered_authority_and_locator(self):
        changed = copy.deepcopy(self.index)
        row = next(r for r in changed['rows'] if r['key'] == 'EAOSE:EAOSE-C001')
        row['source_obligation']['authority'] = 'The sponsor represents every affected party.'
        row['continuation']['if_selected']['actual_owner_and_rights'] = row['source_obligation']['authority']
        row['original']['json_pointer'] = '/properties/1'
        self.reader.check_index(reseal(changed))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'changed.json'
            path.write_text(json.dumps(changed))
            result = subprocess.run([sys.executable, str(READER), 'check', '--index', str(path),
                '--packet', os.environ[PACKET_VARIABLE]], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0, 'altered authority and original locator passed source correspondence')
            self.assertRegex(result.stderr, 'source|original|authority')


if __name__ == '__main__':
    unittest.main(verbosity=2)
