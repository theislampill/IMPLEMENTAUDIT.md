"""Independent models for one frozen fixture change; no actual Windows calls."""
import ast
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import types
import unittest

ROOT = Path('/workspace/scratch/0269e6626329/dg17')
REVIEW = Path(__file__).absolute().parent
COMMIT = '3bde5a5123d3b1c6cf908b2e263504dce994d4e7'
PARENT = '4db726a4f5c7f6429589a941977e233ece967e91'
REL = 'handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/'
USER, SYSTEM, ADMIN, EVERYONE = 'S-1-5-21-1000', 'S-1-5-18', 'S-1-5-32-544', 'S-1-1-0'


def frozen(path, rev=COMMIT):
    return subprocess.check_output(['git', 'show', rev + ':' + path], cwd=ROOT)


FIXTURE = frozen(REL + 'tools/test_store_custody.py')
OLD = frozen(REL + 'tools/test_store_custody.py', PARENT)


def helpers(work, source=FIXTURE, **overrides):
    tree = ast.parse(source)
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) or (
        isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in
        {'ICACLS', 'POWERSHELL', 'OWNER_QUERY'} for t in n.targets))]
    ns = dict(base64=base64, json=json, os=os, stat=stat, subprocess=None,
              work=work, rows=[], bad=0, preconditions=[], me='SIMULATED\\User')
    exec(compile(ast.Module(body=selected, type_ignores=[]), 'frozen-fixture', 'exec'), ns)
    ns.update(overrides)
    return ns


class DaclModel:
    def __init__(self, grants=(ADMIN,), denies=(), removal='normal'):
        self.grants, self.denies = set(grants), set(denies)
        self.owner = ADMIN
        self.removal = removal
        self.events = []
        self.observations = []

    def owner_facts(self, path):
        self.events.append(('owner', path))
        return {'owner': self.owner, 'user': USER}

    def acl(self, path, *args):
        self.events.append(('icacls', path, args))
        if args[0] == '/setowner':
            self.owner = USER
        elif args[0] == '/inheritance:r':
            self.grants.update({USER, SYSTEM})
        elif args[0] == '/remove:g':
            assert args == ('/remove:g', '*' + ADMIN)
            if isinstance(self.removal, Exception):
                raise self.removal
            if self.removal != 'noop':
                self.grants.discard(ADMIN)
        elif args[0] == '/grant:r':
            self.grants.update(arg.split(':', 1)[0].lstrip('*') for arg in args[1:])
        else:
            raise AssertionError(('unexpected modeled command', args))

    def check(self, path):
        self.events.append(('check', path))
        self.observations.append((set(self.grants), set(self.denies)))
        if self.denies:
            raise RuntimeError('store custody refused: unsupported access entry type 1')
        foreign = self.grants - {USER, SYSTEM}
        if foreign:
            raise RuntimeError('store custody refused: access granted to another principal ' + sorted(foreign)[0])
        return {'owner': self.owner, 'protected': True}

    def namespace(self, work, source=FIXTURE):
        return helpers(work, source, icacls=self.acl, owner_facts=self.owner_facts, check=self.check)


class ResidualAceControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='independent-model-', dir=REVIEW)
        self.work = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_only_one_fixture_command_added_and_all_predicates_unchanged(self):
        tree = ast.parse(FIXTURE)
        private = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'private')
        expected = ast.parse("icacls(p,'/remove:g','*S-1-5-32-544')").body[0]
        matches = [n for n in private.body if ast.dump(n) == ast.dump(expected)]
        self.assertEqual(len(matches), 1)
        index = private.body.index(matches[0])
        self.assertEqual(index, 3)
        private.body.pop(index)
        self.assertEqual(ast.dump(tree), ast.dump(ast.parse(OLD)))
        calls = [n.value for n in tree.body if isinstance(n, ast.Expr) and
            isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'case']
        self.assertEqual(len(calls), 14)
        self.assertEqual(sum(ast.literal_eval(n.args[1]) == 'REFUSED' for n in calls), 11)
        paths = subprocess.check_output(['git', 'diff', '--name-only', PARENT, COMMIT], cwd=ROOT, text=True).splitlines()
        self.assertEqual(paths, [REL + p for p in ['README.md','SOURCE_QUALIFICATION_MANIFEST.json',
            'SOURCE_REHEARSAL_20261115.md','tools/test_driver_bundle.py','tools/test_store_custody.py']])
        self.assertEqual(hashlib.sha256(FIXTURE).hexdigest(),
            '546ead882cdc019298e3b5328dcc100ec8e1059d73fb6eaabe6085c9fbd903a4')

    def test_observed_residual_grant_requires_change_and_clean_preimage_still_passes(self):
        for label, source, grants, expected in [
            ('old-residual', OLD, {ADMIN}, 'ERROR'),
            ('new-residual', FIXTURE, {ADMIN}, 'PASS'),
            ('already-clean', FIXTURE, set(), 'PASS')]:
            model = DaclModel(grants=grants)
            ns = model.namespace(self.work, source)
            ns['case'](label, 'PASS', lambda: model.check(ns['private'](self.work / label)))
            row = ns['rows'][0]
            self.assertEqual(row['got'], expected)
            self.assertEqual(row['ok'], expected == 'PASS')
            if expected == 'PASS':
                self.assertTrue(all(g == {USER, SYSTEM} and not d for g,d in model.observations))
                self.assertEqual([p['check'] for p in row['preconditions']],
                    ['independent owner SID', 'independent owner SID', 'private user+SYSTEM baseline'])
            else:
                self.assertTrue(all(p['check'] != 'private user+SYSTEM baseline' for p in row['preconditions']))

    def test_intended_adverse_grants_follow_complete_baseline_and_remain_refused(self):
        for sid in [ADMIN, EVERYONE]:
            model = DaclModel()
            ns = model.namespace(self.work)
            ns['case']('intentional-' + sid, 'REFUSED',
                lambda: model.check(ns['private'](self.work / sid, ['*' + sid + ':(OI)(CI)F'])),
                'access granted to another principal ' + sid)
            row = ns['rows'][0]
            self.assertTrue(row['ok'], row)
            self.assertEqual(model.observations[0], ({USER, SYSTEM}, set()))
            self.assertIn(sid, model.observations[-1][0])
            removal = next(i for i,e in enumerate(model.events) if e[0] == 'icacls' and e[2][0] == '/remove:g')
            baseline = next(i for i,e in enumerate(model.events) if e[0] == 'check')
            adverse = next(i for i,e in enumerate(model.events) if e[0] == 'icacls' and e[2][0] == '/grant:r')
            self.assertLess(removal, baseline)
            self.assertLess(baseline, adverse)
            self.assertEqual(sum(e[0] == 'icacls' and e[2][0] == '/remove:g' for e in model.events), 1)

    def test_silent_failed_removal_cannot_be_expected_admin_negative(self):
        model = DaclModel(removal='noop')
        ns = model.namespace(self.work)
        ns['case']('noop', 'REFUSED',
            lambda: model.check(ns['private'](self.work/'noop', ['*' + ADMIN + ':(OI)(CI)F'])),
            'access granted to another principal ' + ADMIN)
        row = ns['rows'][0]
        self.assertEqual((row['got'],row['ok']), ('ERROR',False))
        self.assertIn('fixture private baseline refused', row['detail'])
        self.assertFalse(any(e[0] == 'icacls' and e[2][0] == '/grant:r' for e in model.events))

    def test_other_principals_and_deny_entries_survive_targeted_removal_and_fail_baseline(self):
        for label, grants, denies in [('foreign', {ADMIN,EVERYONE}, set()),
                                      ('admin-deny', {ADMIN}, {ADMIN})]:
            model = DaclModel(grants=grants, denies=denies)
            ns = model.namespace(self.work)
            reason = 'access granted to another principal ' + EVERYONE if not denies else 'unsupported access entry type 1'
            ns['case'](label, 'REFUSED',
                lambda: model.check(ns['private'](self.work/label, ['*' + ADMIN + ':(OI)(CI)F'])), reason)
            row = ns['rows'][0]
            self.assertEqual((row['got'],row['ok']), ('ERROR',False))
            self.assertNotIn(ADMIN, model.grants)
            self.assertEqual(model.denies, denies)
            if not denies:self.assertIn(EVERYONE, model.grants)
            self.assertFalse(any(p['check']=='private user+SYSTEM baseline' for p in row['preconditions']))
            self.assertFalse(any(e[0]=='icacls' and e[2][0]=='/grant:r' for e in model.events))

    def test_removal_exception_stops_before_baseline_or_perturbation(self):
        for i,error in enumerate([AssertionError('SIMULATED icacls nonzero'),
                subprocess.TimeoutExpired('SIMULATED icacls',30),PermissionError('SIMULATED denied')]):
            model = DaclModel(removal=error)
            ns = model.namespace(self.work)
            ns['case']('command-error', 'REFUSED',
                lambda: model.check(ns['private'](self.work/str(i), ['*' + ADMIN + ':(OI)(CI)F'])),
                'access granted to another principal ' + ADMIN)
            row = ns['rows'][0]
            self.assertEqual((row['got'],row['ok']), ('ERROR',False))
            self.assertEqual(model.observations, [])
            self.assertFalse(any(e[0]=='icacls' and e[2][0]=='/grant:r' for e in model.events))

    def test_actual_icacls_wrapper_retains_fixed_argv_timeout_and_nonzero_rejection(self):
        captures=[]
        def run(command, **kw):
            captures.append((command,kw))
            return types.SimpleNamespace(returncode=0,stdout='',stderr='')
        ns=helpers(self.work,subprocess=types.SimpleNamespace(run=run))
        path=self.work/"literal-'quote;[wildcard]"
        ns['icacls'](path,'/remove:g','*'+ADMIN)
        command,kw=captures[0]
        self.assertEqual(command,[r'C:\Windows\System32\icacls.exe',str(path),'/remove:g','*'+ADMIN])
        self.assertEqual(kw,{'capture_output':True,'text':True,'timeout':30})
        ns['subprocess']=types.SimpleNamespace(run=lambda *a,**kw:types.SimpleNamespace(returncode=1,stdout='',stderr='SIMULATED failure'))
        with self.assertRaises(AssertionError):ns['icacls'](path,'/remove:g','*'+ADMIN)

    def test_manifest_preserves_received_history_and_all_product_bytes(self):
        name=REL+'SOURCE_QUALIFICATION_MANIFEST.json';raw=frozen(name)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'208a1dfb224fa902b22429ff6161177449b884dddd36c871ed444259d7eb6a49')
        m=json.loads(raw);old=json.loads(frozen(name,PARENT))
        for key in ['second_ci_receiving','third_ci_receiving']:
            self.assertEqual(m[key],old[key])
        packet=(ROOT/'.IMPLEMENTAUDIT/dg17-ci-43679794953/SOURCE_CI_RECEIVING.json').read_bytes()
        self.assertEqual((len(packet),hashlib.sha256(packet).hexdigest()),
            (42735,'b2abc0db85b8c0faa3708b6d9b8e3ef642c42c45468abdf5471c6c03d5fad03c'))
        self.assertEqual(m['fourth_ci_receiving'],json.loads(packet))
        self.assertFalse(m['native_admission']);self.assertEqual(m['original14_custody_unknown_differences'],14)
        for pin in m['changed_file_population_excludes_this_manifest']:
            b=frozen(pin['path']);self.assertEqual((len(b),hashlib.sha256(b).hexdigest()),(pin['bytes'],pin['sha256']))
        for p in ['.github/workflows/dg17-offline-lifecycle.yml',REL+'tools/build_release_acl.py',
                  REL+'tools/make_acl_stage_b.py',REL+'tools/rehearse_lifecycle.py']:
            self.assertEqual(frozen(p),frozen(p,PARENT))


if __name__=='__main__':unittest.main(verbosity=2)
