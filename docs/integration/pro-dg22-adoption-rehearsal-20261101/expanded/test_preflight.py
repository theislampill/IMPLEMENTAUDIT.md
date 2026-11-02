#!/usr/bin/env python3
"""Finite tests of the new inert packet checker, using actual provisional inputs."""
import copy
import json
from pathlib import Path
import unittest
import preflight

HERE = Path(__file__).resolve().parent


def packet(role='published'):
    return json.loads((HERE / ('PROVISIONAL_INPUTS.' + role + '.json')).read_text())


class InertPreflightTests(unittest.TestCase):
    def test_actual_published_source_and_archives(self):
        report = preflight.check(packet(), final_gate=False)
        self.assertEqual(report['status'], 'PROVISIONAL_INPUTS_VERIFIED')
        self.assertFalse(report['adoption_ready'])
        self.assertEqual(len(report['strict_artifacts']), 2)
        self.assertIn('DG21_COMMON_ADOPTION', report['missing_final_inputs'])

    def test_actual_engineering_source_and_archives(self):
        report = preflight.check(packet('engineering'), final_gate=False)
        self.assertEqual(report['status'], 'PROVISIONAL_INPUTS_VERIFIED')
        self.assertFalse(report['adoption_ready'])
        self.assertEqual(len(report['strict_artifacts']), 2)

    def test_missing_authentic_authorities_refuse_final_gate(self):
        with self.assertRaises(preflight.Refusal) as caught:
            preflight.check(packet(), final_gate=True)
        self.assertIn('CE021', str(caught.exception))
        self.assertIn('DG21_COMMON_ADOPTION', str(caught.exception))
        self.assertIn('human_exact_approval', str(caught.exception))

    def test_changed_artifact_digest_refuses(self):
        p = packet(); p['artifacts'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(preflight.Refusal, 'ARTIFACT_DIGEST'):
            preflight.check(p, final_gate=False)

    def test_changed_source_tree_refuses(self):
        p = packet(); p['subject']['source_tree'] = packet('engineering')['subject']['source_tree']
        with self.assertRaisesRegex(preflight.Refusal, 'SOURCE_TREE'):
            preflight.check(p, final_gate=False)

    def test_changed_expected_parent_refuses(self):
        p = packet(); p['subject']['expected_old'] = p['subject']['source_commit']
        with self.assertRaisesRegex(preflight.Refusal, 'PARENT'):
            preflight.check(p, final_gate=False)

    def test_changed_provisional_authority_bytes_refuse(self):
        p = packet(); p['provisional_authorization']['sha256'] = '0' * 64
        with self.assertRaisesRegex(preflight.Refusal, 'RECEIPT_DIGEST'):
            preflight.check(p, final_gate=False)

    def test_live_mode_cannot_be_requested_in_packet(self):
        p = packet(); p['effects'] = ['update_main']
        with self.assertRaisesRegex(preflight.Refusal, 'NO_LIVE_MUTATION_MODE'):
            preflight.check(p, final_gate=False)

    def test_command_construction_is_data_only_and_non_force(self):
        p = packet()
        recipe = preflight.construct_future_command(p['subject'],
            remote='https://github.com/theislampill/IMPLEMENTAUDIT.md.git',
            checkout='/REQUIRES_AUTHORIZED_PRIVATE_CHECKOUT',
            hook_directory='/REQUIRES_BOUND_PRIVATE_HOOK_DIRECTORY')
        self.assertFalse(recipe['authorized_to_execute'])
        self.assertEqual(recipe['push_argv'][-1], p['subject']['adoption_commit'] + ':refs/heads/main')
        self.assertIn('--atomic', recipe['push_argv'])
        self.assertIn('--no-force', recipe['push_argv'])
        self.assertNotIn('--force-with-lease', recipe['push_argv'])
        self.assertEqual(recipe['guard_values']['old'], p['subject']['expected_old'])
        self.assertEqual(recipe['guard_values']['candidate'], p['subject']['adoption_commit'])
        self.assertEqual(recipe['commit_tree_argv'][-2:], ['-p', p['subject']['expected_old']])

    def test_wrong_repository_in_construction_refuses(self):
        with self.assertRaisesRegex(preflight.Refusal, 'REMOTE'):
            preflight.construct_future_command(packet()['subject'], remote='/tmp/elsewhere',
                checkout='/tmp/checkout', hook_directory='/tmp/hooks')

    def test_reused_message_guard_covers_full_github_issue_urls(self):
        self.assertIsNotNone(preflight.CLOSING.search('Resolves https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/196'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
