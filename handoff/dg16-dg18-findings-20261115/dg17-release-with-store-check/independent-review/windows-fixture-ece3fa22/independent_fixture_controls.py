"""Independent bounded source controls; never imports or executes Win32 APIs."""
import ast
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import types
import unittest

ROOT = Path('/workspace/scratch/0269e6626329/dg17')
WORK = ROOT.parent / 'dg17-review/windows-fixture-ece3fa22'
PREFIX = 'handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/'
BASE = '06b22dcfa07cbfed8fc69d922530d05d544d0aef'
HEAD = 'ece3fa22e605fb891e6f2995baf886b220113d14'
SOURCE = subprocess.check_output(['git','-C',str(ROOT),'show',HEAD+':'+PREFIX+'tools/test_store_custody.py'])
TREE = ast.parse(SOURCE)
CASES = [n.value for n in TREE.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
         and isinstance(n.value.func,ast.Name) and n.value.func.id=='case']
NEGATIVES = [(ast.literal_eval(c.args[0]),ast.literal_eval(c.args[3])) for c in CASES
             if ast.literal_eval(c.args[1])=='REFUSED']


def helpers(**overrides):
    selected = [n for n in TREE.body if isinstance(n,ast.FunctionDef) or (
        isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'POWERSHELL','OWNER_QUERY'} for t in n.targets))]
    ns = dict(base64=base64,json=json,os=os,stat=stat,Path=Path,subprocess=None,
              me='SIMULATED\\User',work=WORK,rows=[],bad=0,preconditions=[])
    exec(compile(ast.Module(body=selected,type_ignores=[]),'frozen-fixture-helpers','exec'),ns)
    ns.update(overrides)
    return ns


def refused(message):
    def call(*args,**kwargs): raise RuntimeError(message)
    return call


class IndependentFixtureControls(unittest.TestCase):
    def test_all_eleven_controls_reject_wrong_predicate_returns(self):
        self.assertEqual(len(NEGATIVES),11)
        ns=helpers()
        for name,reason in NEGATIVES:
            ns['case'](name,'REFUSED',refused('store custody refused: '+reason),reason)
            self.assertTrue(ns['rows'][-1]['ok'])
            for wrong in set(r for _,r in NEGATIVES)-{reason}:
                ns['case'](name,'REFUSED',refused('store custody refused: '+wrong),reason)
                self.assertFalse(ns['rows'][-1]['ok'],(name,wrong))
        old_seven=[pair for pair in NEGATIVES if any(x in pair[0] for x in
                   ['Administrators outside','Everyone','inherited Users','junction to','unprotected DACL'])]
        self.assertEqual(len(old_seven),7)
        for name,reason in old_seven:
            ns['case'](name,'REFUSED',refused('store custody refused: owner S-1-5-32-544 is not the current user S-1-5-21-1000'),reason)
            self.assertFalse(ns['rows'][-1]['ok'])

    def test_owner_query_failures_and_baseline_refusals_are_errors(self):
        def timeout(*args,**kwargs): raise subprocess.TimeoutExpired(args[0],30)
        responses=[lambda *a,**kw:types.SimpleNamespace(returncode=1,stdout='',stderr='SIMULATED denied'),
                   lambda *a,**kw:types.SimpleNamespace(returncode=0,stdout='not json',stderr=''),
                   lambda *a,**kw:types.SimpleNamespace(returncode=0,stdout='{"owner":"S-1-5-1"}',stderr=''),
                   lambda *a,**kw:types.SimpleNamespace(returncode=0,stdout='{"owner":null,"user":"S-1-5-1"}',stderr=''),timeout]
        for run in responses:
            ns=helpers(subprocess=types.SimpleNamespace(run=run))
            ns['case']('invalid independent query','REFUSED',lambda:ns['require_owner'](WORK),'is not the current user')
            self.assertEqual(ns['rows'][-1]['got'],'ERROR')
            self.assertFalse(ns['rows'][-1]['ok'])
        for _,reason in NEGATIVES:
            ns=helpers(owner_facts=lambda p:{'owner':'S-1-5-21-1000','user':'S-1-5-21-1000'},
                       check=refused('store custody refused: '+reason))
            ns['case']('failed baseline','REFUSED',lambda:ns['private_baseline'](WORK),reason)
            self.assertEqual(ns['rows'][-1]['got'],'ERROR')
            self.assertFalse(ns['rows'][-1]['ok'])

    def test_literal_path_query_and_icacls_are_fixed_bounded_argv(self):
        captured=[]
        def run(command,**kwargs):
            captured.append((command,kwargs))
            return types.SimpleNamespace(returncode=0,stdout='{"owner":"S-1-5-21-1000","user":"S-1-5-21-1000"}',stderr='')
        ns=helpers(subprocess=types.SimpleNamespace(run=run),ICACLS=r'C:\Windows\System32\icacls.exe')
        path=r"C:\SIMULATED\a'\$([Console]::WriteLine('never'));&literal"
        ns['owner_facts'](path)
        command,kwargs=captured[-1]
        self.assertEqual(command[0],r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe')
        self.assertEqual(command[1:4],['-NoProfile','-NonInteractive','-EncodedCommand'])
        query=base64.b64decode(command[4],validate=True).decode('utf-16le')
        self.assertNotIn(path,query)
        self.assertIn('Get-Acl -LiteralPath $env:DG17_FIXTURE_OWNER_PATH',query)
        self.assertNotIn('Invoke-Expression',query)
        self.assertEqual(kwargs['env']['DG17_FIXTURE_OWNER_PATH'],path)
        self.assertEqual(kwargs['timeout'],30)
        self.assertNotIn('shell',kwargs)
        ns['icacls'](path,'/setowner',ns['me'])
        command,kwargs=captured[-1]
        self.assertEqual(command,[r'C:\Windows\System32\icacls.exe',path,'/setowner','SIMULATED\\User'])
        self.assertEqual(kwargs['timeout'],30)
        self.assertNotIn('shell',kwargs)

    def test_wrong_owner_and_junction_preconditions_cannot_false_pass(self):
        calls=[]
        ns=helpers(private=lambda p:calls.append('positive baseline') or p,
                   icacls=lambda *a:calls.append('owner mutation'),
                   owner_facts=lambda p:{'owner':'S-1-5-21-1000','user':'S-1-5-21-1000'},
                   check=lambda p:calls.append('product check') or {})
        ns['case']('owner mutation did not take','REFUSED',ns['wrong_owner'],'owner S-1-5-32-544 is not the current user')
        self.assertEqual(ns['rows'][-1]['got'],'ERROR')
        self.assertEqual(calls,['positive baseline','owner mutation'])
        calls.clear()
        ns=helpers(private=lambda p:calls.append('positive target') or p,
                   _winapi=types.SimpleNamespace(CreateJunction=lambda *a:calls.append('junction request')),
                   os=types.SimpleNamespace(lstat=lambda p:types.SimpleNamespace(st_file_attributes=0)),
                   check=lambda p:calls.append('product check') or {})
        ns['case']('link not actually a reparse point','REFUSED',ns['junction'],'junction, link or other reparse point')
        self.assertEqual(ns['rows'][-1]['got'],'ERROR')
        self.assertEqual(calls,['positive target','junction request'])

    def test_exact_five_file_population_and_unchanged_guards(self):
        manifest_path=ROOT/PREFIX/'SOURCE_QUALIFICATION_MANIFEST.json'
        raw=manifest_path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'63c4f757c5aa00eff2b711f527cb8ec3f6970eaf4938618de3460ecbe610fb5d')
        manifest=json.loads(raw);correction=manifest['fixture_correction']
        changed=set(subprocess.check_output(['git','-C',str(ROOT),'diff','--name-only',BASE,HEAD],text=True).splitlines())
        records=correction['changed_file_population_excludes_this_manifest']
        self.assertEqual(changed,{r['path'] for r in records}|{manifest_path.relative_to(ROOT).as_posix()})
        self.assertEqual(len(changed),5)
        for record in records:
            body=subprocess.check_output(['git','-C',str(ROOT),'show',HEAD+':'+record['path']])
            self.assertEqual((len(body),hashlib.sha256(body).hexdigest()),(record['bytes'],record['sha256']))
        preserved=['.github/workflows/dg17-offline-lifecycle.yml',PREFIX+'tools/build_release_acl.py',
                   PREFIX+'tools/make_acl_stage_b.py',PREFIX+'tools/rehearse_lifecycle.py']
        for path in preserved:
            before=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+path])
            after=subprocess.check_output(['git','-C',str(ROOT),'show',HEAD+':'+path])
            self.assertEqual(before,after)
        receiving=ROOT/'.IMPLEMENTAUDIT/dg17-ci-43677179224/SOURCE_CI_RECEIVING.json'
        self.assertEqual(hashlib.sha256(receiving.read_bytes()).hexdigest(),'97fe609807cd2a665c09a88c3f676f5e124ee7270bf78d5b061f0395e98de6cd')
        self.assertEqual(json.loads(receiving.read_bytes()),manifest['second_ci_receiving'])
        self.assertFalse(manifest['native_admission'])
        self.assertEqual(manifest['original14_custody_unknown_differences'],14)


if __name__=='__main__':
    with (WORK/'independent-5-controls.log').open('w') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IndependentFixtureControls))
    print((WORK/'independent-5-controls.log').read_text())
    raise SystemExit(not result.wasSuccessful())
