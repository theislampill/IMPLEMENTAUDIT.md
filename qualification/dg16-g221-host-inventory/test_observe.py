#!/usr/bin/env python3
"""Narrow new-wrapper controls. Synthetic inputs are TEST_ONLY, never host evidence."""
import ast
import os
from pathlib import Path
import textwrap
import types
import unittest

ROOT = Path(__file__).absolute().parents[2]
PATH = ROOT / 'qualification/dg16-g221-host-inventory/observe.py'
OBS = types.ModuleType('TEST_ONLY_observer')
OBS.__file__ = str(PATH)
exec(compile(PATH.read_bytes(), str(PATH), 'exec'), OBS.__dict__)


class Controls(unittest.TestCase):
    def test_exact_owner_closure_and_internal_loader_pins(self):
        self.assertEqual(len(OBS.PINS), 8)
        raw = (ROOT / OBS.OWNER / 'run.py').read_bytes()
        constants = {n.targets[0].id: n.value.value for n in ast.parse(raw).body
                     if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                     and isinstance(n.value, ast.Constant)}
        names = {'host_utility.py': 'UTILITY_SHA', 'evidence_io.py': 'NATIVE_EVIDENCE_IO_SHA',
                 'native_profile.py': 'NATIVE_PROFILE_SHA', 'native_admission.py': 'NATIVE_ADMISSION_SHA',
                 'current_host.py': 'CURRENT_HOST_SHA', 'native_prerequisite.py': 'NATIVE_RECEIVER_SHA',
                 'native_integration.py': 'NATIVE_INTEGRATION_SHA'}
        for name, pin in OBS.PINS.items():
            OBS.verify_pin(name, (ROOT / OBS.OWNER / name).read_bytes())
            if name in names:
                self.assertEqual(constants[names[name]], pin)

    def test_owner_imports_are_inert_and_stdlib_only(self):
        allowed_imports = {'argparse', 'ctypes', 'errno', 'fcntl', 'hashlib', 'json', 'os', 'pathlib',
                           're', 'selectors', 'signal', 'socket', 'stat', 'subprocess', 'sys', 'time', 'types'}
        for name in OBS.PINS:
            tree = ast.parse((ROOT / OBS.OWNER / name).read_bytes())
            for node in tree.body:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module]
                    self.assertTrue(set(imports) <= allowed_imports)
                elif isinstance(node, ast.Assign):
                    calls = [ast.unparse(c.func) for c in ast.walk(node.value) if isinstance(c, ast.Call)]
                    self.assertTrue(set(calls) <= {'dict', 'Path'}, (name, calls))
                elif isinstance(node, ast.If):
                    self.assertEqual(ast.unparse(node.test), "__name__ == '__main__'")
                elif isinstance(node, ast.ClassDef):
                    self.assertFalse(node.decorator_list)
                    self.assertTrue(all(isinstance(n, ast.Pass) for n in node.body))
                elif isinstance(node, ast.FunctionDef):
                    self.assertFalse(node.decorator_list)
                    self.assertFalse(any(isinstance(n, ast.Call) for d in (*node.args.defaults, *filter(None, node.args.kw_defaults)) for n in ast.walk(d)))
                else:
                    self.assertIsInstance(node, ast.Expr)
                    self.assertIsInstance(node.value, ast.Constant)

    def test_direct_owner_entry_points_only(self):
        tree = ast.parse(PATH.read_bytes())
        calls = {ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and ast.unparse(n.func).startswith(('adapter.', 'native.', 'utility.'))}
        self.assertEqual(calls, {'adapter.load_utility', 'adapter.load_native', 'adapter.inventory',
                                 'native.E.encode', 'native.C.target_host'})

    def test_TEST_ONLY_changed_source_refuses_without_execution(self):
        raw = (ROOT / OBS.OWNER / 'run.py').read_bytes()
        with self.assertRaisesRegex(OBS.Refusal, '^OWNER_SOURCE_PIN_REFUSED$'):
            OBS.verify_pin('run.py', raw + b'\n# TEST_ONLY mutation; never executed\n')

    def test_TEST_ONLY_provider_shape_and_refusals(self):
        # Pure validator inputs only. These are never installed into os.environ.
        env = dict(GITHUB_REPOSITORY=OBS.REPOSITORY, GITHUB_REF='refs/heads/' + OBS.BRANCH,
                   GITHUB_SHA='1' * 40, GITHUB_RUN_ID='1', GITHUB_RUN_ATTEMPT='1',
                   GITHUB_EVENT_NAME='push', GITHUB_ACTIONS='true',
                   G221_PUSH_CREATED='true', G221_PUSH_DELETED='false')
        OBS.require_provider(OBS.provider_fields(env), env)
        for key, value in [('GITHUB_REPOSITORY', 'TEST_ONLY/other'), ('GITHUB_REF', 'refs/heads/TEST_ONLY'),
                           ('GITHUB_SHA', 'TEST_ONLY'), ('GITHUB_RUN_ID', '0'), ('GITHUB_RUN_ATTEMPT', '2'),
                           ('GITHUB_EVENT_NAME', 'workflow_dispatch'), ('GITHUB_ACTIONS', 'false'),
                           ('G221_PUSH_CREATED', 'false'), ('G221_PUSH_DELETED', 'true')]:
            changed = dict(env, **{key: value})
            with self.assertRaisesRegex(OBS.Refusal, '^PROVIDER_CONTEXT_REFUSED$'):
                OBS.require_provider(OBS.provider_fields(changed), changed)

    def test_TEST_ONLY_environment_allowlist(self):
        value = OBS.provider_fields({'GITHUB_TOKEN': 'TEST_ONLY_UNRELATED_VALUE', 'GITHUB_REF': 'TEST_ONLY\nVALUE'})
        self.assertEqual(set(value), {'repository', 'ref', 'sha', 'run_id', 'attempt', 'event'})
        self.assertTrue(all(v is None for v in value.values()))

    def test_TEST_ONLY_effect_boundary(self):
        for event in ('subprocess.Popen', 'socket.__new__', 'os.system', 'os.exec', 'os.fork',
                      'os.mkdir', 'os.remove', 'os.rename', 'os.chmod', 'os.putenv'):
            self.assertTrue(OBS.effect_denied(event, ()), event)
        self.assertTrue(OBS.effect_denied('open', ('/TEST_ONLY/output', 'w', os.O_WRONLY)))
        self.assertTrue(OBS.effect_denied('open', ('/TEST_ONLY/output', None, os.O_CREAT)))
        self.assertFalse(OBS.effect_denied('open', ('/TEST_ONLY/input', 'r', os.O_RDONLY)))

    def test_TEST_ONLY_exception_text_withheld(self):
        value = OBS.failure(PermissionError(13, 'TEST_ONLY_PRIVATE_VALUE', '/TEST_ONLY/private'), 'TEST_ONLY')
        self.assertEqual(value['code'], 'OBSERVATION_EXCEPTION_REFUSED')
        self.assertEqual(value['errno'], 13)
        self.assertNotIn('PRIVATE_VALUE', OBS.canonical(value).decode())
        self.assertNotIn('/TEST_ONLY/private', OBS.canonical(value).decode())

    def test_workflow_bounds_pin_and_bootstrap_syntax(self):
        workflow = (ROOT / OBS.WORKFLOW).read_text()
        self.assertIn("expected = '" + OBS.descriptor(PATH.read_bytes())['sha256'] + "'", workflow)
        for value in (OBS.BRANCH, "github.event.created == true", "github.event.deleted == false",
                      "github.run_attempt == '1'", 'contents: read', 'runs-on: ubuntu-26.04',
                      'persist-credentials: false', 'if: always()', '/usr/bin/python3 -I -S -B',
                      'actions/checkout@11d5960a326750d5838078e36cf38b85af677262',
                      'actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02'):
            self.assertIn(value, workflow)
        self.assertEqual(workflow.count('uses:'), 2)
        self.assertNotIn('workflow_dispatch:', workflow)
        bootstrap = textwrap.dedent(workflow.split("<<'PY'\n", 1)[1].split('          PY\n', 1)[0])
        compile(bootstrap, '<TEST_ONLY_workflow_bootstrap_syntax>', 'exec')


if __name__ == '__main__':
    unittest.main(verbosity=2)
