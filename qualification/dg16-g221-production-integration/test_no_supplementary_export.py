"""Focused caller controls; stubbed effects are never accepting evidence."""
import ast
import hashlib
import json
from pathlib import Path
import types
import unittest


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / 'qualification/dg16-r5-full-g2/run.py'


class DirectPairCallerTests(unittest.TestCase):
    def setUp(self):
        self.module = types.ModuleType('subject')
        self.module.__file__ = str(ADAPTER)
        exec(compile(ADAPTER.read_bytes(), str(ADAPTER), 'exec'), self.module.__dict__)
        m = self.module
        self.calls = []
        self.state = {'docs': {'PROBE.json': {}}, 'controller': 'test-only',
                      'receipt': 'test-only-current-receipt', 'policy_adoption': {},
                      'native': {'current_host_request': {'test_only': True}}}
        self.runtime = types.SimpleNamespace(Refusal=m.Refusal)
        m.actual_policy_adoption = lambda _: {}
        m.write_private = lambda path, raw: self.calls.append(('private', path.name))
        m.failed_leg_public_budget = lambda *_: {'original_public_budget': True}
        m.require_native_for_pair = lambda *_: self.calls.append(('native', 'received'))
        m.checked_driver = lambda _: Path('/test-only/pair_driver.py')
        m.read_pair_summary = lambda *_: {'status': 'COMPLETE_PAIR_RAW_RELATION_RECORDED'}
        def forbidden(*_):
            raise AssertionError('SUPPLEMENTARY_CRYPTO_SELECTED')
        for name in ('protected_capacity', 'protected_preflight', 'protected_failed_finalize', 'protected_emit'):
            setattr(m, name, forbidden)

    def command(self, label, argv, **kwargs):
        self.calls.append(('command', label))
        if label.endswith('currentness'):
            return 0, (self.state['receipt'] + '\n').encode(), b''
        return 0, b'{}\n', b''

    def invoke(self, command=None):
        self.module.operation('pair', self.state, Path('/test-only/source'),
                              Path('/test-only/output'), {'bash': '/test-only/bash',
                              'python3': '/test-only/python3'}, self.runtime, {},
                              command or self.command)

    def test_current_host_pair_keeps_native_and_currentness_without_crypto(self):
        self.invoke()
        self.assertEqual(self.state['failed_leg_public_capacity'], {'original_public_budget': True})
        selected = [x for x in self.calls if x[0] != 'private']
        self.assertEqual(selected, [('command', 'before-pair-currentness'),
                                   ('native', 'received'),
                                   ('command', 'complete-current-registry-pair'),
                                   ('command', 'after-pair-currentness')])

    def test_matching_historical_host_still_requires_native_receiving(self):
        self.state['native']['current_host_request'] = None
        self.invoke()
        self.assertEqual(self.calls.count(('native', 'received')), 1)

    def test_missing_native_receiving_blocks_pair(self):
        def refuse(*_):
            raise self.module.Refusal('TEST_ONLY_NATIVE_NOT_RECEIVED')
        self.module.require_native_for_pair = refuse
        with self.assertRaisesRegex(self.module.Refusal, 'TEST_ONLY_NATIVE_NOT_RECEIVED'):
            self.invoke()
        self.assertNotIn(('command', 'complete-current-registry-pair'), self.calls)

    def test_changed_policy_blocks_pair(self):
        self.module.actual_policy_adoption = lambda _: {'changed': True}
        with self.assertRaisesRegex(self.module.Refusal, 'POLICY_ADOPTION_CHANGED_BEFORE_PAIR'):
            self.invoke()
        self.assertEqual(self.calls, [])

    def test_currentness_refusal_blocks_pair(self):
        with self.assertRaisesRegex(self.module.Refusal, 'MAINTAINED_OWNER_REFUSED'):
            self.invoke(lambda *_args, **_kwargs: (1, b'', b''))
        self.assertNotIn(('command', 'complete-current-registry-pair'), self.calls)

    def test_failed_pair_remains_failed_and_retains_output(self):
        def command(label, argv, **kwargs):
            result = self.command(label, argv, **kwargs)
            return (1, b'actual-test-only-failure\n', b'') if label == 'complete-current-registry-pair' else result
        with self.assertRaisesRegex(self.module.Refusal, 'FULL_PAIR_INCOMPLETE_OR_FAILED'):
            self.invoke(command)
        self.assertIn(('private', 'pair.stdout'), self.calls)
        self.assertIn(('private', 'pair.stderr'), self.calls)

    def test_no_entrypoint_invokes_supplementary_crypto(self):
        tree = ast.parse(ADAPTER.read_bytes())
        retired = {'load_protected', 'protected_capacity', 'protected_preflight',
                   'protected_failed_finalize', 'protected_emit'}
        invoked = {n.func.id for n in ast.walk(tree)
                   if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertFalse(retired & invoked)
        workflow = (ROOT / '.github/workflows/dg16-r5-full-g2.yml').read_text()
        self.assertNotIn('--emit-protected', workflow)
        self.assertNotIn('FAILED_STREAMS.cms', workflow)
        self.assertIn('/review/PROOF.json', workflow)
        self.assertIn('/public/ARTIFACT_MANIFEST.json', workflow)
        self.assertEqual(workflow.count(hashlib.sha256(ADAPTER.read_bytes()).hexdigest()),
                         workflow.count('adapter="$GITHUB_WORKSPACE/packet/qualification/dg16-r5-full-g2/run.py"'))


if __name__ == '__main__':
    unittest.main()
