#!/usr/bin/env python3
"""Standalone command-policy contract; no adapter, host, Git or model import."""
from __future__ import annotations
import ast
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parent / 'lib' / 'host_command_policy.py'

class HostCommandPolicyTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MODULE.is_file(),
                        'command classification still requires the adapter compilation unit')
        spec = importlib.util.spec_from_file_location('isolated_host_command_policy', MODULE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.policy = module.HostCommandPolicy
        self.tmp = tempfile.TemporaryDirectory(prefix='command-policy-')
        self.addCleanup(self.tmp.cleanup)
        self.repo = self.tmp.name
        Path(self.repo, 'STATE.md').write_text('epoch\n', encoding='utf-8')
        self.profile = {'host': 'codex', 'attestation_id': 'local-test-profile',
                        'shell_dialect': 'posix',
                        'executables': {'cat': '/usr/bin/cat', 'echo': 'builtin:echo',
                                        'true': 'builtin:true', 'false': 'builtin:false',
                                        'rg': '/usr/bin/rg', 'bash': '/usr/bin/bash'}}

    def record(self, command, **changes):
        value = {'command': command, 'output': 'epoch\n', 'exit_code': 0,
                 'source': 'codex-command-completed', 'shell_dialect': 'posix',
                 'host_read_attestation_id': 'local-test-profile',
                 'wrapper_host_owned': False}
        value.update(changes)
        return value

    def classify(self, command, **changes):
        return self.policy.classify_command_target(
            self.record(command, **changes), 'STATE.md', self.repo, self.profile)

    def test_no_inward_infrastructure_imports(self):
        tree = ast.parse(MODULE.read_text())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add((node.module or '').split('.')[0])
        self.assertLessEqual(imports, {'__future__', 'os', 're', 'shlex'})
        self.assertNotIn('hosts', MODULE.read_text().split('class HostCommandPolicy')[1])

    def test_direct_read_is_positive(self):
        self.assertEqual(self.classify('cat STATE.md'), 'content-read')

    def test_mention_is_not_read(self):
        self.assertEqual(self.classify('echo STATE.md'), 'not-content-read')

    def test_unattested_command_fails_closed(self):
        self.assertEqual(self.classify('cat STATE.md', host_read_attestation_id=None), 'fail-closed')

    def test_foreign_host_cannot_supply_read_evidence(self):
        self.assertEqual(self.classify('cat STATE.md', source='claude-tool'), 'fail-closed')

    def test_dynamic_target_fails_closed(self):
        self.assertEqual(self.classify('cat "$TARGET"'), 'fail-closed')

    def test_false_branch_is_not_executed(self):
        self.assertEqual(self.classify('false && cat STATE.md', exit_code=1), 'not-content-read')

    def test_ambiguous_status_cannot_become_positive(self):
        self.assertEqual(self.classify('cat STATE.md; echo done'), 'fail-closed')

    def test_non_integer_exit_fails_closed(self):
        self.assertEqual(self.classify('cat STATE.md', exit_code=True), 'fail-closed')

    def test_read_inputs_are_not_mutated(self):
        record = self.record('cat STATE.md')
        original = copy.deepcopy((record, self.profile))
        self.policy.classify_command_target(record, 'STATE.md', self.repo, self.profile)
        self.assertEqual((record, self.profile), original)

    def test_alias_path_does_not_establish_identity(self):
        Path(self.repo, 'alias.md').symlink_to(Path(self.repo, 'STATE.md'))
        self.assertIsNone(self.policy._canonical_trace_path('alias.md', self.repo))

    def test_write_path_enumeration_has_no_write_effect(self):
        self.assertEqual(self.policy._command_write_paths(self.record('echo epoch > output.md')), ['output.md'])
        self.assertFalse(Path(self.repo, 'output.md').exists())

if __name__ == '__main__':
    unittest.main(verbosity=2)
