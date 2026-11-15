"""Independent source-only controls for frozen DG17 owner-query correction.

No Windows command, native episode, artifact body fetch, or source mutation.
"""
import ast
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import types
import unittest

ROOT = Path('/workspace/scratch/0269e6626329/dg17')
COMMIT = '82af8ccb20222ee9e667bb97494818d1b8853fb7'
PARENT = 'c430ef8e5759bfd4eddff4c10b7ab2e442b6d60c'
REL = 'handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/'
WORK = Path(__file__).absolute().parent
FIXTURE_PATH = REL + 'tools/test_store_custody.py'


def frozen(path, rev=COMMIT):
    return subprocess.check_output(['git', 'show', rev + ':' + path], cwd=ROOT)


FIXTURE = frozen(FIXTURE_PATH)
TREE = ast.parse(FIXTURE)
USER = 'S-1-5-21-1000-2000-3000-1001'
ADMIN = 'S-1-5-32-544'


def helpers(run=None, **overrides):
    selected = [node for node in TREE.body if isinstance(node, ast.FunctionDef) or (
        isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and
        t.id in {'POWERSHELL', 'OWNER_QUERY'} for t in node.targets))]
    ns = dict(base64=base64, json=json, os=os, stat=stat,
              subprocess=types.SimpleNamespace(run=run), rows=[], bad=0,
              preconditions=[], work=WORK, me='SIMULATED\\User')
    exec(compile(ast.Module(body=selected, type_ignores=[]),
                 'frozen-fixture-helpers', 'exec'), ns)
    ns.update(overrides)
    return ns


def reply(output=None, code=0, error=''):
    return types.SimpleNamespace(returncode=code,
        stdout=(USER + '\r\n' + USER + '\r\n') if output is None else output,
        stderr=error)


class OwnerQueryControls(unittest.TestCase):
    def test_exact_source_population_and_product_bytes_unchanged(self):
        self.assertEqual(subprocess.check_output(['git', 'rev-parse', COMMIT + '^{tree}'],
            cwd=ROOT, text=True).strip(), '7e084c97e6198856a055434221563ea8412e673a')
        changed = subprocess.check_output(['git', 'diff', '--name-only', PARENT, COMMIT],
            cwd=ROOT, text=True).splitlines()
        expected = [REL + name for name in ['README.md', 'SOURCE_QUALIFICATION_MANIFEST.json',
            'SOURCE_REHEARSAL_20261115.md', 'tools/test_driver_bundle.py', 'tools/test_store_custody.py']]
        self.assertEqual(changed, expected)
        self.assertEqual(hashlib.sha256(FIXTURE).hexdigest(),
            'de7e800bdc99a6e130cff94f1d60585f6f829d77ea601e4460ec90793a5efe5f')
        for path in ['.github/workflows/dg17-offline-lifecycle.yml',
                     REL + 'tools/build_release_acl.py', REL + 'tools/make_acl_stage_b.py',
                     REL + 'tools/rehearse_lifecycle.py']:
            self.assertEqual(frozen(path), frozen(path, PARENT))

    def test_every_case_preimage_and_refusal_reason_is_ast_identical(self):
        def normalized(source):
            tree = ast.parse(source)
            return [ast.dump(node, include_attributes=False) for node in tree.body
                if not (isinstance(node, ast.FunctionDef) and node.name == 'owner_facts')
                and not (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name)
                    and t.id == 'OWNER_QUERY' for t in node.targets))]
        self.assertEqual(normalized(FIXTURE), normalized(frozen(FIXTURE_PATH, PARENT)))
        cases = [n.value for n in TREE.body if isinstance(n, ast.Expr) and
                 isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)
                 and n.value.func.id == 'case']
        self.assertEqual(len(cases), 14)
        negatives = [n for n in cases if ast.literal_eval(n.args[1]) == 'REFUSED']
        self.assertEqual(len(negatives), 11)
        self.assertTrue(all(len(n.args) == 4 and ast.literal_eval(n.args[3]) for n in negatives))

    def test_literal_metacharacter_paths_cannot_change_fixed_command(self):
        captured = []
        original_env = {'SIMULATED': 'unchanged', 'DG17_FIXTURE_OWNER_PATH': 'old-value'}
        def run(argv, **kwargs):
            captured.append((argv, kwargs))
            return reply()
        ns = helpers(run, os=types.SimpleNamespace(environ=original_env))
        paths = [Path("relative-'quote;$(Get-Item*)`n[?]"),
                 WORK / 'spaces and [wildcards]*', WORK / 'unicode-\u03a9-newline\ntext']
        for path in paths:
            self.assertEqual(ns['owner_facts'](path), {'owner': USER, 'user': USER})
        expected = [r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe',
                    '-NoProfile', '-NonInteractive', '-EncodedCommand', ns['OWNER_QUERY']]
        for path, (argv, kw) in zip(paths, captured):
            self.assertEqual(argv, expected)
            self.assertEqual(kw['env']['DG17_FIXTURE_OWNER_PATH'], str(path.absolute()))
            self.assertEqual(kw['env']['SIMULATED'], 'unchanged')
            self.assertIsNot(kw['env'], original_env)
            self.assertEqual(kw['timeout'], 30)
            self.assertTrue(kw['capture_output'] and kw['text'])
            self.assertFalse(kw.get('shell', False))
        self.assertEqual(original_env['DG17_FIXTURE_OWNER_PATH'], 'old-value')
        query = base64.b64decode(ns['OWNER_QUERY'], validate=True).decode('utf-16le')
        self.assertLess(query.index("$PSModuleAutoLoadingPreference = 'None'"),
                        query.index('[System.IO.File]::GetAttributes'))
        self.assertEqual(query.count('[Console]::WriteLine('), 2)
        self.assertLess(query.index('finally { $identity.Dispose() }'),
                        query.index('[Console]::WriteLine($owner)'))
        for forbidden in ['Get-Acl', 'ConvertTo-Json', 'Import-Module', 'Invoke-Expression']:
            self.assertNotIn(forbidden, query)
        for path in paths:
            self.assertNotIn(str(path), query)

    def test_parser_rejects_contamination_and_non_ascii_components(self):
        malformed = ['', 'S-1-', 's-1-5-18', 'S-2-5-18', 'S-1-5--18',
            'S-1-5-18-', 'S-1-+5-18', 'S-1-5-1.8', 'S-1-\u0665-18',
            'S-1-5-\uff11\uff18', 'S-1-5-\u00b2', ' S-1-5-18', 'S-1-5-18 ',
            '\ufeffS-1-5-18', 'S-1-5-18\0', 'S-1-5-18\t', 'S-1-5-0x12',
            'S-1-5-18;exit 0', 'S-1-5-18\r\nnoise']
        for value in malformed:
            for output in [value + '\n' + USER + '\n', USER + '\n' + value + '\n']:
                with self.subTest(output=output):
                    ns = helpers(lambda *a, **kw: reply(output))
                    with self.assertRaises(AssertionError):
                        ns['owner_facts'](WORK)
                    self.assertEqual(ns['preconditions'], [])
        for output in ['', USER, USER + '\n', '\n' + USER + '\n' + USER,
                       USER + '\n' + USER + '\n\n',
                       '#< CLIXML\n' + USER + '\n' + USER + '\n',
                       USER + '\n' + USER + '\n' + USER + '\n']:
            with self.subTest(output=output), self.assertRaises(AssertionError):
                helpers(lambda *a, **kw: reply(output))['owner_facts'](WORK)
        for separator in ['\n', '\r\n']:
            ns = helpers(lambda *a, **kw: reply(USER + separator + USER + separator))
            self.assertEqual(ns['require_owner'](WORK), {'owner': USER, 'user': USER})
            self.assertEqual(len(ns['preconditions']), 1)

    def test_query_failure_or_timeout_never_becomes_negative_credit(self):
        def thrown(error):
            def run(*args, **kwargs):
                raise error
            return run
        runs = [lambda *a, code=code, **kw: reply(code=code, error='SIMULATED process failure')
                for code in [1, 2, -9]]
        runs += [thrown(subprocess.TimeoutExpired('SIMULATED powershell', 30)),
                 thrown(FileNotFoundError('SIMULATED fixed executable absent')),
                 thrown(PermissionError('SIMULATED denied'))]
        for run in runs:
            checked = []
            ns = helpers(run, check=lambda p: checked.append(p))
            ns['case']('SIMULATED negative', 'REFUSED',
                lambda: ns['private_baseline'](WORK), 'SIMULATED process failure')
            row = ns['rows'][0]
            self.assertEqual((row['got'], row['ok'], row['preconditions']), ('ERROR', False, []))
            self.assertEqual(checked, [])
            self.assertEqual(ns['bad'], 1)

    def test_different_owner_never_satisfies_current_user_precondition(self):
        output = ADMIN + '\r\n' + USER + '\r\n'
        ns = helpers(lambda *a, **kw: reply(output))
        self.assertEqual(ns['owner_facts'](WORK), {'owner': ADMIN, 'user': USER})
        with self.assertRaises(AssertionError):
            ns['require_owner'](WORK)
        self.assertEqual(ns['preconditions'], [])
        self.assertEqual(ns['require_owner'](WORK, ADMIN), {'owner': ADMIN, 'user': USER})
        self.assertEqual(len(ns['preconditions']), 1)
        cases = [n.value for n in TREE.body if isinstance(n, ast.Expr) and
                 isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)
                 and n.value.func.id == 'case' and ast.literal_eval(n.value.args[1]) == 'REFUSED']
        for case in cases:
            reason = ast.literal_eval(case.args[3])
            ns['case'](ast.literal_eval(case.args[0]), 'REFUSED',
                       lambda: ns['require_owner'](WORK), reason)
            self.assertEqual((ns['rows'][-1]['got'], ns['rows'][-1]['ok']), ('ERROR', False))
            self.assertEqual(ns['rows'][-1]['preconditions'], [])

    def test_receiving_and_prior_failure_evidence_remain_exact(self):
        path = REL + 'SOURCE_QUALIFICATION_MANIFEST.json'
        raw = frozen(path)
        self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()),
            (105703, 'e96074d2f5598208c63b0d437d73feedd6c48de16dc51c9d546ee0754b75c993'))
        manifest = json.loads(raw)
        old = json.loads(frozen(path, PARENT))
        self.assertEqual(manifest['second_ci_receiving'], old['second_ci_receiving'])
        received = (ROOT / '.IMPLEMENTAUDIT/dg17-ci-43678583519/SOURCE_CI_RECEIVING.json').read_bytes()
        self.assertEqual((len(received), hashlib.sha256(received).hexdigest()),
            (43050, 'c7b2ef7e4bd10232e73f8c59ae5e956a86a5efd838b4fe038bdd943e517dc2e4'))
        self.assertEqual(manifest['third_ci_receiving'], json.loads(received))
        self.assertEqual(manifest['original14_custody_unknown_differences'], 14)
        self.assertFalse(manifest['native_admission'])
        self.assertEqual(manifest['genuine_codex_turns'], 0)
        for item in manifest['changed_file_population_excludes_this_manifest']:
            data = frozen(item['path'])
            self.assertEqual((len(data), hashlib.sha256(data).hexdigest()),
                             (item['bytes'], item['sha256']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
