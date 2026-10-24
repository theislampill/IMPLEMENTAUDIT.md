#!/usr/bin/env python3
"""Real optional tokenizer admission; no host context-health claim."""
import copy
import hashlib
import importlib.metadata
import os
from pathlib import Path
import tempfile
import unittest

from archive_v2_test import M, F, make_subject, git, transition
import claim_transaction_test as C


class TokenAdmission(unittest.TestCase):
    def setUp(self):
        encoding = os.environ.get('R0039_TOKENIZER_ENCODING')
        if not encoding:
            self.skipTest('real pinned encoding not supplied; token execution unqualified')
        try:
            version = importlib.metadata.version('tiktoken')
        except importlib.metadata.PackageNotFoundError:
            self.skipTest('optional tiktoken is absent; no download is performed')
        self.assertEqual(version, '0.13.0')
        self.encoding = Path(encoding).read_bytes()
        self.assertEqual(hashlib.sha256(self.encoding).hexdigest(),
                         '223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7')
        self.tmp = tempfile.TemporaryDirectory(prefix='r0039-token-')
        self.addCleanup(self.tmp.cleanup)

    def subject(self, text):
        subject = make_subject(Path(self.tmp.name) / 'repo', large=False)
        bodies = F.fixture_bodies()
        bodies['STATE']['history'][0]['payload']['text'] = text
        state, roadmap, owners, artifacts = F.fixture_pair(bodies)
        for role, raw in (('state', state), ('roadmap', roadmap)):
            (subject['run'] / (role.upper() + '.md')).write_bytes(raw)
            subject['predecessor'][role + '_sha256'] = M.sha256(raw)
        subject['source'] = (state, roadmap)
        receipt_oid = git(subject['repo'], 'hash-object', '-w', '--stdin',
                          data=artifacts['receipt']).decode().strip()
        git(subject['repo'], 'update-ref', subject['predecessor']['receipt_ref'], receipt_oid)
        subject['predecessor']['receipt_oid'] = receipt_oid
        subject['owner_map'].write_bytes(M.canonical_bytes(
            {'schema': 'implementaudit.rotation-owner-map.v2', 'owner_map': owners}))
        return subject

    def prepare(self, subject):
        self.assertTrue(callable(getattr(M, 'token_calibration_contract_v1', None)),
                        'accepting token route is missing')
        return M.prepare_canonical_draft(subject['repo'], subject['run'],
            subject['predecessor']['controller'], 'G0002', subject['owner_map'],
            subject['predecessor'], M.token_calibration_contract_v1(), tokenizer_bytes=self.encoding)

    def test_real_token_only_arm_archives_and_revalidates_exact_pair(self):
        subject = self.subject('q ' * 38000)
        self.assertLess(sum(map(len, subject['source'])), 131072)
        result = self.prepare(subject)
        self.assertTrue(result['triggered'])
        self.assertEqual(result['measurement']['triggered_by'], ['TOKENS'])
        self.assertEqual(result['measurement']['context_health'], 'UNAVAILABLE')
        self.assertGreaterEqual(result['measurement']['live_tokens_before'], 32768)
        self.assertGreaterEqual(result['measurement']['live_token_reduction'], 8192)
        M._checked_prepared(subject['repo'], subject['run'], result)
        broken = copy.deepcopy(result)
        broken['measurement']['live_tokens_before'] += 1
        with self.assertRaises(M.RotationError):
            M._checked_prepared(subject['repo'], subject['run'], broken)
        git(subject['repo'], 'gc', '--prune=now')
        M._checked_prepared(subject['repo'], subject['run'], result)

    def test_below_both_arms_writes_no_archive_and_does_not_claim_context_health(self):
        subject = self.subject('short history')
        subject['owner_map'].unlink()
        before = git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)')
        result = self.prepare(subject)
        self.assertFalse(result['triggered'])
        self.assertEqual(result['context_health'], 'UNAVAILABLE')
        self.assertEqual(before, git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)'))
        self.assertFalse((subject['run'] / 'state-generations').exists())

    def test_changed_encoding_refuses_before_archive(self):
        subject = self.subject('q ' * 38000)
        self.encoding = self.encoding[:-1] + b'x'
        before = git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)')
        with self.assertRaises(M.RotationError):
            self.prepare(subject)
        self.assertEqual(before, git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)'))

    def test_real_byte_only_arm_with_measured_token_payoff(self):
        subject = self.subject('a' * 140000)
        self.assertTrue(callable(getattr(M, 'count_rotation_tokens_v1', None)),
                        'real token counting is missing')
        before = M.count_rotation_tokens_v1(self.encoding, subject['source'])
        self.assertLess(sum(before), 32768)
        result = self.prepare(subject)
        self.assertEqual(result['measurement']['triggered_by'], ['BYTES'])

    def test_byte_trigger_does_not_waive_minimum_token_payoff(self):
        subject = self.subject(' ' * 140000)
        with self.assertRaisesRegex(M.RotationError, 'payoff'):
            self.prepare(subject)
        self.assertEqual(git(subject['repo'], 'for-each-ref', '--format=%(refname)',
                             'refs/implementaudit/current-generations/'), b'')


class TokenClaimAdmission(unittest.TestCase):
    history_text = 'q ' * 38000

    def setUp(self):
        self.encoding_path = os.environ.get('R0039_TOKENIZER_ENCODING')
        if not self.encoding_path:
            self.skipTest('real pinned encoding not supplied; accepting token path unqualified')
        C.RealHelperIntegration.setUp(self)

    def test_claim_cli_publishes_token_only_rotation_and_keeps_fourteen_field_receipt(self):
        self.assertLess(sum(len(raw) for raw in self.original_pair.values()), 131072)
        result = self.fixture.claim('--rotate-canonical-state', C.CONTROLLER,
            '--owner-map', str(self.owner_map), '--tokenizer-encoding', self.encoding_path)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        published = C.json.loads(result.stdout)
        self.assertEqual(published['status'], 'ROTATED')
        joined = self.owner.require_current_generation_join_v1(self.context)
        self.assertEqual(joined['receipt_token'], published['receipt_token'])
        record, _ = self.owner.read_epoch(self.context, 'G0002')
        self.assertEqual(record['prepared']['measurement']['triggered_by'], ['TOKENS'])
        receipt = self.owner.read_blob(self.fixture.repo, published['receipt_token'].split('@')[1])
        self.assertEqual(len(receipt.decode().strip().split('\t')), 14)
        self.assertEqual(self.owner.read_component(self.context, 'STATE'), joined['state_bytes'])
        self.assertEqual(self.owner.read_component(self.context, 'ROADMAP'), joined['roadmap_bytes'])
        for role, raw in self.original_pair.items():
            self.assertEqual((self.fixture.run_root / (role + '.md')).read_bytes(), raw)


if __name__ == '__main__':
    unittest.main()
