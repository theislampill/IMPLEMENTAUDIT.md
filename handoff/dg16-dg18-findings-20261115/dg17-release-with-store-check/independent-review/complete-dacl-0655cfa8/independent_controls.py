"""Independent frozen-source controls; no PowerShell, Win32 or native episode."""
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

ROOT=Path('/workspace/scratch/0269e6626329/dg17')
REVIEW=Path(__file__).absolute().parent
COMMIT='0655cfa87cc3b81ed59ffa046d07b1ba616d631e'
PARENT='c2faca3a5bccf26b4571fddbece4d420385c86b5'
REL='handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/'
USER,SYSTEM,ADMIN,CREATOR='S-1-5-21-1000','S-1-5-18','S-1-5-32-544','S-1-3-0'
def frozen(path,rev=COMMIT):return subprocess.check_output(['git','show',rev+':'+path],cwd=ROOT)
RAW=frozen(REL+'tools/test_store_custody.py');TREE=ast.parse(RAW)
CASES=[n.value for n in TREE.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
       and isinstance(n.value.func,ast.Name) and n.value.func.id=='case']
REASONS=[ast.literal_eval(c.args[3]) for c in CASES if ast.literal_eval(c.args[1])=='REFUSED']
def helpers(work,**overrides):
    selected=[n for n in TREE.body if isinstance(n,ast.FunctionDef) or (isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Name) and t.id in {'ICACLS','POWERSHELL','OWNER_QUERY','DACL_SETUP'} for t in n.targets))]
    ns=dict(base64=base64,json=json,os=os,stat=stat,subprocess=None,rows=[],bad=0,
        preconditions=[],work=work,me='SIMULATED\\User')
    exec(compile(ast.Module(body=selected,type_ignores=[]),'frozen-fixture','exec'),ns)
    ns.update(overrides);return ns
def response(code=0,stderr=''):return types.SimpleNamespace(returncode=code,stdout='',stderr=stderr)


class CompleteDaclControls(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='independent-',dir=REVIEW);self.work=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()

    def test_exact_existing_owner_functions_cases_and_reasons_preserved(self):
        old=ast.parse(frozen(REL+'tools/test_store_custody.py',PARENT))
        oldf={n.name:ast.dump(n) for n in old.body if isinstance(n,ast.FunctionDef)}
        newf={n.name:ast.dump(n) for n in TREE.body if isinstance(n,ast.FunctionDef)}
        self.assertEqual(set(newf)-set(oldf),{'set_private_dacl'})
        self.assertEqual([n for n in oldf if oldf[n]!=newf[n]],['private'])
        def assigns(tree):return {ast.dump(n.targets[0]):ast.dump(n) for n in tree.body if isinstance(n,ast.Assign)}
        a,b=assigns(old),assigns(TREE)
        self.assertTrue(all(b[k]==v for k,v in a.items()))
        oldcases=[n.value for n in old.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
            and isinstance(n.value.func,ast.Name) and n.value.func.id=='case']
        self.assertEqual(len(CASES),14);self.assertEqual(len(REASONS),11)
        normalized=copy.deepcopy(CASES)
        self.assertEqual(ast.literal_eval(normalized[2].args[0]),'positive: independent protected DACL, user+SYSTEM only')
        normalized[2].args[0]=oldcases[2].args[0]
        self.assertEqual([ast.dump(n) for n in normalized],[ast.dump(n) for n in oldcases])
        self.assertEqual(hashlib.sha256(RAW).hexdigest(),'32614b757717b7dc0aa2234683b45117242d6ef105855759acfb29dfd0beebeb')

    def test_writer_is_static_literal_and_parent_environment_unchanged(self):
        calls=[];env={'SIMULATED':'yes','DG17_FIXTURE_DACL_PATH':'old'}
        def run(argv,**kw):calls.append((argv,kw));return response()
        ns=helpers(self.work,subprocess=types.SimpleNamespace(run=run),os=types.SimpleNamespace(environ=env))
        paths=[Path("relative-'quote;$(expr)`x[?]"),self.work/'unicode-\u03a9\nnewline']
        for p in paths:ns['set_private_dacl'](p)
        for p,(argv,kw) in zip(paths,calls):
            self.assertEqual(argv,[r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',ns['DACL_SETUP']])
            self.assertEqual(kw['env']['DG17_FIXTURE_DACL_PATH'],str(p.absolute()))
            self.assertIsNot(kw['env'],env);self.assertEqual(kw['timeout'],30);self.assertNotIn('shell',kw)
        self.assertEqual(env['DG17_FIXTURE_DACL_PATH'],'old')
        script=base64.b64decode(ns['DACL_SETUP'],validate=True).decode('utf-16le')
        self.assertEqual(script.count('[System.IO.Directory]::SetAccessControl($path, $acl)'),1)
        self.assertIn('[System.Security.AccessControl.DirectorySecurity]::new()',script)
        self.assertIn('$acl.SetAccessRuleProtection($true, $false)',script)
        self.assertIn('foreach ($sid in @($identity.User, $system))',script)
        self.assertIn('finally { $identity.Dispose() }',script)
        for term in ['GetAccessControl','SetOwner','Get-Acl','Set-Acl','New-Object','Import-Module',ADMIN,CREATOR,'private_store_directory']:
            self.assertNotIn(term,script)
        for p in paths:self.assertNotIn(str(p),script)

    def test_existing_directory_file_or_symlink_stops_before_mutations(self):
        directory=self.work/'directory';directory.mkdir()
        file=self.work/'file';file.write_text('SIMULATED')
        link=self.work/'link';link.symlink_to(directory,target_is_directory=True)
        for p in [directory,file,link]:
            effects=[];ns=helpers(self.work,icacls=lambda *a:effects.append('icacls'),
                subprocess=types.SimpleNamespace(run=lambda *a,**k:effects.append('writer')))
            ns['case']('existing','REFUSED',lambda:ns['private'](p),REASONS[0])
            row=ns['rows'][0];self.assertEqual((row['got'],row['ok'],row['preconditions']),('ERROR',False,[]))
            self.assertEqual(effects,[])

    def test_writer_failures_cannot_match_any_intended_negative_reason(self):
        for i,reason in enumerate(REASONS):
            for j,kind in enumerate(['nonzero','timeout','denied']):
                effects=[]
                def run(*args,**kw):
                    effects.append('writer')
                    if kind=='timeout':raise subprocess.TimeoutExpired('SIMULATED',30)
                    if kind=='denied':raise PermissionError(reason)
                    return response(1,reason)
                ns=helpers(self.work,icacls=lambda *a:effects.append('owner-or-extra'),
                    owner_facts=lambda p:{'owner':USER,'user':USER},
                    subprocess=types.SimpleNamespace(run=run),check=lambda *a:effects.append('baseline'))
                ns['case']('writer failure','REFUSED',lambda:ns['private'](self.work/(str(i)+'-'+str(j)),['*'+ADMIN+':F']),reason)
                row=ns['rows'][0]
                self.assertEqual((row['got'],row['ok']),('ERROR',False))
                self.assertEqual(effects,['owner-or-extra','writer']);self.assertEqual(len(row['preconditions']),1)

    def test_zero_exit_does_not_bypass_owner_or_full_baseline(self):
        for i,reason in enumerate(REASONS):
            calls=[]
            def refused(path):calls.append('baseline');raise RuntimeError(reason)
            ns=helpers(self.work,icacls=lambda *a:calls.append('owner-or-extra'),
                owner_facts=lambda p:{'owner':USER,'user':USER},
                subprocess=types.SimpleNamespace(run=lambda *a,**kw:response()),check=refused)
            ns['case']('ineffective','REFUSED',lambda:ns['private'](self.work/str(i),['*'+ADMIN+':F']),reason)
            row=ns['rows'][0];self.assertEqual((row['got'],row['ok']),('ERROR',False))
            self.assertEqual(calls,['owner-or-extra','baseline'])
            self.assertTrue(all(p['check']!='private user+SYSTEM baseline' for p in row['preconditions']))
        count=[0];calls=[]
        def facts(path):
            count[0]+=1;return {'owner':USER if count[0]==1 else ADMIN,'user':USER}
        ns=helpers(self.work,icacls=lambda *a:calls.append('owner-or-extra'),owner_facts=facts,
            subprocess=types.SimpleNamespace(run=lambda *a,**kw:response()),check=lambda p:calls.append('baseline'))
        ns['case']('changed owner','REFUSED',lambda:ns['private'](self.work/'changed-owner',['*'+ADMIN+':F']),REASONS[-1])
        self.assertEqual((ns['rows'][0]['got'],ns['rows'][0]['ok']),('ERROR',False));self.assertEqual(calls,['owner-or-extra'])

    def test_complete_baseline_precedes_intended_grant_and_is_not_reapplied(self):
        grants={ADMIN,CREATOR,'S-1-5-21-2000'};events=[]
        def acl(path,*args):
            events.append(('icacls',args[0]))
            if args[0]=='/grant:r':grants.add(ADMIN)
        def run(*args,**kwargs):
            events.append(('replace',));grants.clear();grants.update({USER,SYSTEM});return response()
        def check(path):
            events.append(('check',set(grants)))
            if grants!={USER,SYSTEM}:raise RuntimeError('access granted to another principal '+ADMIN)
            return {'protected':True,'owner':USER}
        ns=helpers(self.work,icacls=acl,owner_facts=lambda p:{'owner':USER,'user':USER},
            subprocess=types.SimpleNamespace(run=run),check=check)
        ns['case']('intended admin','REFUSED',lambda:check(ns['private'](self.work/'fresh',['*'+ADMIN+':F'])),
                   'access granted to another principal '+ADMIN)
        self.assertTrue(ns['rows'][0]['ok']);self.assertEqual(events,[('icacls','/setowner'),('replace',),
            ('check',{USER,SYSTEM}),('icacls','/grant:r'),('check',{USER,SYSTEM,ADMIN})])
        self.assertEqual(ns['rows'][0]['preconditions'][-1]['check'],'private user+SYSTEM baseline')

    def test_exact_five_files_and_preserved_history_product_owners(self):
        paths=subprocess.check_output(['git','diff','--name-only',PARENT,COMMIT],cwd=ROOT,text=True).splitlines()
        self.assertEqual(paths,[REL+p for p in ['README.md','SOURCE_QUALIFICATION_MANIFEST.json','SOURCE_REHEARSAL_20261115.md','tools/test_driver_bundle.py','tools/test_store_custody.py']])
        p=REL+'SOURCE_QUALIFICATION_MANIFEST.json';raw=frozen(p);m=json.loads(raw);old=json.loads(frozen(p,PARENT))
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'8701fd7d74921917dfd70bd48e9565b35ba66412cb6bdb3946b59f1fed24878f')
        for k in ['second_ci_receiving','third_ci_receiving','fourth_ci_receiving']:self.assertEqual(m[k],old[k])
        self.assertFalse(m['native_admission']);self.assertEqual(m['original14_custody_unknown_differences'],14)
        for pin in m['changed_file_population_excludes_this_manifest']:
            b=frozen(pin['path']);self.assertEqual((len(b),hashlib.sha256(b).hexdigest()),(pin['bytes'],pin['sha256']))
        for p in ['.github/workflows/dg17-offline-lifecycle.yml',REL+'tools/build_release_acl.py',REL+'tools/make_acl_stage_b.py',REL+'tools/rehearse_lifecycle.py']:
            self.assertEqual(frozen(p),frozen(p,PARENT))
        self.assertFalse(m['complete_fixture_dacl_replacement']['reconstruction']['old_control_log_bodies_recovered'])
        self.assertIsNone(m['complete_fixture_dacl_replacement']['reconstruction']['old_unpublished_post_edit_source_hash'])

if __name__=='__main__':unittest.main(verbosity=2)
