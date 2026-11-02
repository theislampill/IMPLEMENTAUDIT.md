#!/usr/bin/env python3
"""Focused constructed controls for the additive R003F reader; no old campaigns."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import tempfile
import unittest

import bind_final_receipts as b

PARSER = argparse.ArgumentParser()
PARSER.add_argument('retained', type=Path)
PARSER.add_argument('continuation', type=Path)
PARSER.add_argument('repo', type=Path)
ARGS, UNIT_ARGS = PARSER.parse_known_args()
COMMIT = '149e7f9eb12af23ccb55a833ba566d9914f24ace'
TREE = '48fd9b3ce5b2a4bc8c9f7bbd95ed160aade22511'
PARENT = '4af2e43b4047cd577aa6b56eecd5b27c5f0e45e0'
REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'


class ReceiptControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='dg31-constructed-receipts-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.counter = 0
        self.contract = b.read_contract()
        self.source = {'commit': COMMIT, 'tree': TREE}
        self.raw = self.ref({'evidence_kind': 'CONSTRUCTED',
                            'notice': 'Test-only receipt; no real producer, authority, adoption or effect.'})
        self.data = {
            'schema': 'dg31.r003f.final-binding-input.v1',
            'evidence_kind': 'CONSTRUCTED', 'prepared_by': 'constructed-preparer',
            'repository': REPOSITORY, 'issue': 'R003F', 'source': self.source,
            'ce085': {
                'state': 'PASS', 'issue': 'R003F', 'source': self.source,
                'scope': 'DOCUMENTARY_SOURCE_SEMANTIC_RESIDUAL',
                'producer': 'constructed-independent-DG21-producer',
                'receiver': 'constructed-entitled-receiver',
                'environment': 'constructed documentary receiving environment',
                'original_receipt': self.raw, 'current_receiving': self.raw,
                'receiver_authority': self.raw,
                'certificate_sha256': self.contract['retained_files'][0]['sha256'],
                'residual_receipt_hashes': self.contract['residual_receipt_hashes'],
                'conditional_claims': {
                    key: {'state': 'NOT_TRIGGERED_WITH_JUSTIFICATION',
                          'reason': 'Constructed documentary-only scope; no stronger claim selected.',
                          'record': self.raw}
                    for key in self.contract['conditional_claims']},
            },
            'ce086': {
                'state': 'ACTUAL_ADOPTION_READBACK', 'issue': 'R003F',
                'source': self.source, 'expected_old_main': PARENT,
                'ordered_parents': [PARENT], 'target_ref': 'refs/heads/main',
                'owner_approval': {'record': self.raw, 'operation': 'ADOPT_MAIN',
                                   'source': self.source, 'expected_old_main': PARENT,
                                   'ordered_parents': [PARENT]},
                'adoption_result': self.raw,
                'main_readback': self.ref({'ref': 'refs/heads/main',
                    'url': f'https://api.github.com/repos/{REPOSITORY}/git/refs/heads/main',
                    'object': {'type': 'commit', 'sha': COMMIT}}),
                'commit_readback': self.ref({'sha': COMMIT, 'tree': {'sha': TREE},
                                            'parents': [{'sha': PARENT}]}),
                'issue_slice_readback': {'record': self.raw, 'issue': 'R003F',
                    'source': self.source, 'receiver': 'constructed-independent-reader',
                    'independent_of_adoption_writer': True,
                    'certificate_sha256': self.contract['retained_files'][0]['sha256'],
                    'residual_receipt_hashes': self.contract['residual_receipt_hashes']},
            },
        }

    def ref(self, value):
        self.counter += 1
        path = self.root / f'record-{self.counter}.json'
        data = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
        path.write_bytes(data)
        return {'path': path.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                'json_pointer': '', 'selected_value_canonical_sha256': b.canonical_hash(value)}

    def bind(self, data=None, expected_main=COMMIT, acceptance=None, sol_authority=None):
        return b.bind(data or self.data, self.root, ARGS.retained, ARGS.continuation,
                      ARGS.repo, expected_main, acceptance, sol_authority)

    def test_constructed_positive_has_no_effect_readiness(self):
        result = self.bind()
        self.assertEqual(result['result'], 'PASS_CONSTRUCTED_FORM_ONLY')
        self.assertEqual(len(result['core']['source_readback']['consumed_paths']), 29)
        self.assertEqual(len(result['core']['original_predicates']), 14)
        self.assertFalse(result['comment_ready'])
        self.assertFalse(result['closure_ready'])
        self.assertIn('CONSTRUCTED CONTROL', b.evidence_draft(result))

    def test_reference_command_shape_roundtrips_complete_records(self):
        ref = b.make_reference(self.root, self.raw['path'])
        value = b.selected_record(self.root, ref, 'CONSTRUCTED')
        self.assertEqual(value['evidence_kind'], 'CONSTRUCTED')

    def test_missing_ce085_is_pending(self):
        self.data['ce085'] = None
        with self.assertRaises(b.PendingInput): self.bind()

    def test_missing_ce086_is_pending(self):
        self.data['ce086'] = None
        with self.assertRaises(b.PendingInput): self.bind()

    def test_sibling_receipt_is_refused(self):
        self.data['ce085']['issue'] = 'R0041'
        with self.assertRaisesRegex(b.BindingError, 'issue'): self.bind()

    def test_sibling_original_bytes_cannot_hide_behind_r003f_envelope(self):
        self.data['ce085']['original_receipt'] = self.ref({'evidence_kind': 'CONSTRUCTED', 'issue': 'R0041'})
        with self.assertRaisesRegex(b.BindingError, 'issue'): self.bind()

    def test_current_receiving_raw_source_must_match_envelope(self):
        self.data['ce085']['current_receiving'] = self.ref({'evidence_kind': 'CONSTRUCTED',
            'issue': 'R003F', 'source': {'commit': PARENT, 'tree': TREE}})
        with self.assertRaisesRegex(b.BindingError, 'source'): self.bind()

    def test_raw_approval_cannot_disagree_with_normalization(self):
        self.data['ce086']['owner_approval']['record'] = self.ref({'evidence_kind': 'CONSTRUCTED',
            'source': {'commit': PARENT, 'tree': TREE}})
        with self.assertRaisesRegex(b.BindingError, 'approval'): self.bind()

    def test_raw_independent_acceptance_must_bind_same_core(self):
        result = self.bind()
        acceptance = {'core_sha256': result['core_sha256'], 'state': 'ACCEPTED',
            'reviewer': 'constructed-independent-reviewer', 'independent_of_preparer': True,
            'record': self.ref({'evidence_kind': 'CONSTRUCTED', 'core_sha256': '0' * 64}),
            'authority': self.raw}
        with self.assertRaisesRegex(b.BindingError, 'acceptance'): self.bind(acceptance=acceptance)

    def test_rejected_original_acceptance_cannot_be_promoted(self):
        result = self.bind()
        original = {'evidence_kind': 'CONSTRUCTED', 'state': 'REJECTED',
                    'core_sha256': result['core_sha256'], 'reviewer': 'constructed-independent-reviewer',
                    'independent_of_preparer': True}
        acceptance = {**original, 'state': 'ACCEPTED', 'record': self.ref(original), 'authority': self.raw}
        with self.assertRaisesRegex(b.BindingError, 'acceptance.*state'):
            self.bind(acceptance=acceptance)

    def test_failed_current_receiving_cannot_be_promoted(self):
        self.data['ce085']['current_receiving'] = self.ref({'evidence_kind': 'CONSTRUCTED',
            'issue': 'R003F', 'source': self.source, 'state': 'FAIL'})
        with self.assertRaisesRegex(b.BindingError, 'current source receiving.*state'): self.bind()

    def test_failed_native_receipt_cannot_be_promoted(self):
        self.data['ce085']['conditional_claims']['native'] = {
            'state': 'PASS', 'record': self.ref({'evidence_kind': 'CONSTRUCTED', 'state': 'FAIL',
                'issue': 'R003F', 'qualified_source': self.source}),
            'qualified_source': self.source, 'consumer': 'constructed native consumer',
            'environment': 'constructed environment; no native operation'}
        with self.assertRaisesRegex(b.BindingError, 'native qualification.*state'): self.bind()

    def test_failed_artifact_bridge_cannot_be_promoted(self):
        self.data['ce085']['conditional_claims']['package'] = {
            'state': 'PASS', 'record': self.raw, 'consumer': 'constructed consumer',
            'environment': 'constructed environment', 'qualified_source': self.source,
            'artifact_source_commit': PARENT, 'artifact_sha256': '1' * 64,
            'bridge': {'record': self.ref({'evidence_kind': 'CONSTRUCTED', 'result': 'FAIL',
                'from_commit': PARENT, 'to_source': self.source, 'consumer': 'constructed bridge'}),
                'from_commit': PARENT, 'to_source': self.source, 'result': 'PASS',
                'consumer': 'constructed bridge'}}
        with self.assertRaisesRegex(b.BindingError, 'consumer bridge.*result'): self.bind()

    def test_stale_expected_main_is_refused(self):
        with self.assertRaisesRegex(b.BindingError, 'fresh main'): self.bind(expected_main=PARENT)

    def test_wrong_mainline_readback_is_refused(self):
        self.data['ce086']['main_readback'] = self.ref({'ref': 'refs/heads/main',
            'url': f'https://api.github.com/repos/{REPOSITORY}/git/refs/heads/main',
            'object': {'type': 'commit', 'sha': PARENT}})
        with self.assertRaisesRegex(b.BindingError, 'main readback'): self.bind()

    def test_wrong_tree_is_refused(self):
        self.data['source'] = {'commit': COMMIT, 'tree': '0' * 40}
        with self.assertRaises(b.BindingError): self.bind()

    def test_absent_owner_approval_is_refused(self):
        self.data['ce086']['owner_approval'] = None
        with self.assertRaisesRegex(b.BindingError, 'approval'): self.bind()

    def test_approval_for_other_subject_is_refused(self):
        self.data['ce086']['owner_approval']['source'] = {'commit': PARENT, 'tree': TREE}
        with self.assertRaisesRegex(b.BindingError, 'approval'): self.bind()

    def test_wrong_ordered_parents_are_refused(self):
        self.data['ce086']['ordered_parents'] = [PARENT, COMMIT]
        with self.assertRaisesRegex(b.BindingError, 'parent'): self.bind()

    def test_altered_full_record_is_refused(self):
        (self.root / self.raw['path']).write_text('{"changed":true}\n')
        with self.assertRaisesRegex(b.BindingError, 'identity'): self.bind()

    def test_altered_pointer_is_refused(self):
        self.data['ce085']['original_receipt'] = copy.deepcopy(self.raw)
        self.data['ce085']['original_receipt']['json_pointer'] = '/notice'
        with self.assertRaisesRegex(b.BindingError, 'pointer'): self.bind()

    def test_incomplete_residual_receiving_is_refused(self):
        self.data['ce085']['residual_receipt_hashes'] = {'E6': self.contract['residual_receipt_hashes']['E6']}
        with self.assertRaisesRegex(b.BindingError, 'residual'): self.bind()

    def test_unjustified_nontrigger_is_refused(self):
        self.data['ce085']['conditional_claims']['native']['reason'] = ''
        with self.assertRaisesRegex(b.BindingError, 'justification'): self.bind()

    def test_changed_source_package_needs_exact_bridge(self):
        self.data['ce085']['conditional_claims']['package'] = {
            'state': 'PASS', 'record': self.raw, 'consumer': 'constructed consumer',
            'environment': 'constructed environment', 'qualified_source': self.source,
            'artifact_source_commit': PARENT, 'artifact_sha256': '1' * 64}
        with self.assertRaisesRegex(b.BindingError, 'bridge'): self.bind()

    def test_constructed_source_bridge_is_read_only_form(self):
        self.data['ce085']['conditional_claims']['package'] = {
            'state': 'PASS', 'record': self.raw, 'consumer': 'constructed consumer',
            'environment': 'constructed environment', 'qualified_source': self.source,
            'artifact_source_commit': PARENT, 'artifact_sha256': '1' * 64,
            'bridge': {'record': self.raw, 'from_commit': PARENT, 'to_source': self.source,
                       'result': 'PASS', 'consumer': 'constructed source-metadata consumer'}}
        result = self.bind()
        self.assertFalse(result['comment_ready'])

    def test_changed_consumed_path_is_refused(self):
        bad = copy.deepcopy(self.contract['consumed_paths'])
        bad[0]['blob'] = '0' * 40
        with self.assertRaisesRegex(b.BindingError, 'consumed path'):
            b.git_source_readback(ARGS.repo, self.source, bad)

    def test_fixture_cannot_be_relabelled_actual(self):
        self.data['evidence_kind'] = 'ACTUAL'
        with self.assertRaisesRegex(b.BindingError, 'constructed'): self.bind()

    def test_false_final_acceptance_cannot_promote_core(self):
        result = self.bind()
        acceptance = {'core_sha256': '0' * 64, 'state': 'ACCEPTED',
            'reviewer': 'constructed-independent-reviewer', 'independent_of_preparer': True,
            'record': self.raw, 'authority': self.raw}
        with self.assertRaisesRegex(b.BindingError, 'acceptance'): self.bind(acceptance=acceptance)
        self.assertFalse(result['comment_ready'])

    def test_constructed_acceptance_and_sol_grant_never_authorize_effect(self):
        result = self.bind()
        acceptance = {'core_sha256': result['core_sha256'], 'state': 'ACCEPTED',
            'reviewer': 'constructed-independent-reviewer', 'independent_of_preparer': True,
            'record': self.raw, 'authority': self.raw}
        authority = {'core_sha256': result['core_sha256'], 'issue': 225, 'writer': 'Sol',
            'exclusive': True, 'operation': 'post_final_evidence_comment', 'record': self.raw}
        accepted = self.bind(acceptance=acceptance, sol_authority=authority)
        self.assertFalse(accepted['comment_ready'])
        self.assertFalse(accepted['closure_ready'])

    def test_overlapping_issue_writer_is_refused(self):
        authority = {'core_sha256': self.bind()['core_sha256'], 'issue': 225, 'writer': 'Pro',
            'exclusive': True, 'operation': 'post_final_evidence_comment', 'record': self.raw}
        with self.assertRaisesRegex(b.BindingError, 'Sol'): self.bind(sol_authority=authority)


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0], *UNIT_ARGS])
