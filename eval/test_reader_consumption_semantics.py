#!/usr/bin/env python3
"""Exact-input consumption versus full-preimage delivery; local fixtures only.

These tests distinguish the small command adapter from the stricter full-output
formal evaluators. They never turn a synthetic profile into native authority.
"""
from pathlib import Path
import copy
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'lib'))
import hostread
import b3v4_rederive
import hosts


class ReaderConsumptionSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='reader-consumption-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        support = HERE / 'testdata' / 'host-read-trust' / 'support'
        self.profile = json.loads((support / 'test-profile.json').read_text())
        self.preimages = json.loads((support / 'test-preimages.json').read_text())
        self.target = '.IMPLEMENTAUDIT/runs/run-1/STATE.md'
        for doc in (self.profile, self.preimages):
            doc['repo'].update(lexical_root=str(self.root), real_root=str(self.root))
        for target, entry in self.preimages['targets'].items():
            entry['canonical_path'] = str(self.root / target)
        target = self.root / self.target
        target.parent.mkdir(parents=True)
        target.write_text('STATE\n')
        (self.root / 'decoy.md').write_text('STATE\n')
        (self.root / 'empty.md').write_text('')

    def execute(self, command):
        p = subprocess.run(['/usr/bin/bash', '--noprofile', '--norc', '-c', command],
                           cwd=self.root, capture_output=True, timeout=5,
                           env={**os.environ, 'LC_ALL':'C.UTF-8'})
        self.assertEqual(p.returncode, 0, p.stderr.decode())
        return {'command': command, 'output': p.stdout.decode(), 'exit_code':p.returncode}

    def outcomes(self, record):
        official = hostread.classify_shell(record, self.target, self.preimages,
                                           self.profile, formal=False)
        wrapped = dict(record, command='/bin/bash -lc ' + shlex.quote(record['command']),
                       effect='command', state='COMPLETED')
        independent = b3v4_rederive._command_read_classification(
            wrapped, self.target, self.preimages, self.profile)
        return [official['classification'], independent['classification']]

    def test_equal_decoy_quit_does_not_prove_later_target_read(self):
        record = self.execute('sed q decoy.md ' + self.target)
        self.assertEqual(record['output'], 'STATE\n')
        for outcome in self.outcomes(record):
            self.assertNotEqual(outcome, 'content-read')

    def test_missing_later_target_still_does_not_acquire_read_credit(self):
        (self.root / self.target).unlink()
        record = self.execute('sed q decoy.md ' + self.target)
        self.assertEqual(record['output'], 'STATE\n')
        for outcome in self.outcomes(record):
            self.assertNotEqual(outcome, 'content-read')

    def test_quit_with_target_first_and_full_output_is_valid(self):
        record = self.execute('sed q ' + self.target + ' decoy.md')
        self.assertEqual(self.outcomes(record), ['content-read', 'content-read'])

    def test_draining_sed_reaches_later_target(self):
        record = self.execute("sed -n p empty.md " + self.target)
        self.assertEqual(self.outcomes(record), ['content-read', 'content-read'])

    def test_external_quit_program_does_not_prove_later_target(self):
        (self.root / 'program.sed').write_text('q\n')
        record = self.execute('sed -f program.sed decoy.md ' + self.target)
        for outcome in self.outcomes(record):
            self.assertNotEqual(outcome, 'content-read')

    def test_unmodelled_inline_program_does_not_borrow_equal_output(self):
        record = self.execute("sed '1q' decoy.md " + self.target)
        for outcome in self.outcomes(record):
            self.assertNotEqual(outcome, 'content-read')

    def test_unknown_program_can_write_before_read_and_is_refused(self):
        (self.root / 'program.sed').write_text('w ' + self.target + '\n')
        record = self.execute('sed -f program.sed ' + self.target)
        self.assertEqual((self.root / self.target).read_bytes(), b'')
        for outcome in self.outcomes(record):
            self.assertNotEqual(outcome, 'content-read')

    def test_partial_output_is_not_full_preimage_delivery(self):
        record = {'command':'sed -n p ' + self.target,'output':'STA','exit_code':0}
        self.assertEqual(self.outcomes(record), ['fail-closed', 'fail-closed'])

    def test_cat_full_output_neighbour_is_preserved(self):
        self.assertEqual(self.outcomes(self.execute('cat ' + self.target)),
                         ['content-read', 'content-read'])

    def test_valid_external_grep_is_not_mislabelled_as_actual_nonreading(self):
        # Stronger formal delivery evidence can accept this real read; the
        # adapter still refuses an unbound external-pattern input grammar.
        (self.root / 'patterns.txt').write_text('STATE\n')
        record = self.execute('grep -e STATE -f patterns.txt ' + self.target)
        self.assertEqual(self.outcomes(record), ['content-read', 'content-read'])
        from host_command_policy import HostCommandPolicy
        profile = {'host':'codex', 'attestation_id':'fixture-only',
                   'shell_dialect':'posix',
                   'executables':{'grep':'/usr/bin/grep'}}
        record.update(source='codex-command-completed', shell_dialect='posix',
                      host_read_attestation_id='fixture-only', wrapper_host_owned=False)
        self.assertEqual(HostCommandPolicy.classify_command_target(
            record, self.target, str(self.root), profile), 'fail-closed')

    def test_static_powershell_scope_is_not_native_execution_evidence(self):
        from host_command_policy import HostCommandPolicy
        profile = {'host':'codex', 'attestation_id':'fixture-only',
                   'shell_dialect':'powershell',
                   'executables':{'get-content':'powershell:Get-Content'}}
        for operand, expected in [(self.target, 'content-read'),
                                  ('decoy.md,' + self.target, 'fail-closed')]:
            record = {'command':'Get-Content -LiteralPath ' + operand,
                      'output':'STATE\n', 'exit_code':0,
                      'source':'codex-command-completed', 'shell_dialect':'powershell',
                      'host_read_attestation_id':'fixture-only', 'wrapper_host_owned':False}
            self.assertEqual(HostCommandPolicy.classify_command_target(
                record, self.target, str(self.root), profile), expected)

    def test_configuration_role_cannot_be_target_product_evidence(self):
        record = {'command':'grep -f ' + self.target + ' decoy.md',
                  'output':'STATE\n', 'exit_code':0}
        self.assertEqual(self.outcomes(record), ['fail-closed','fail-closed'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
