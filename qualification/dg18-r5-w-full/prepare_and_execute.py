#!/usr/bin/env python3
"""One new Windows subject and one maintained W-FULL attempt, after external approval.

This adapter does not authenticate entitlement, award acceptance, retry, install
tools, fetch private evidence, or run a model. No Windows operation is simulated.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import time

SOURCE_HEAD='539aa846e37eab2dd527912d5e5eaa95f69d61cf'
SOURCE_TREE='6a278e8c95eb1812ce39ca1af288532d4951d860'
REPOSITORY='theislampill/IMPLEMENTAUDIT.md'
BRANCH='pro/dg18-r5-w-full-20261105'
BASH=Path(r'C:\Program Files\Git\bin\bash.exe')
DIRECT_GIT_PATHS=(r'C:\Program Files\Git\mingw64\bin\git.exe',
                  r'C:\Program Files\Git\ucrt64\bin\git.exe')
GIT=None
PUBLIC_FILES=('RESULT.json','SOURCE.json','TOOLS.json','CONTROL.json','MEASUREMENT.json',
              'TRANSITION.json','RECEIVING.json','FAILURE.json','ARTIFACT_MANIFEST.json')

def require(ok,reason):
    if not ok: raise RuntimeError(reason)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    raw=value if isinstance(value,bytes) else canonical(value)
    with path.open('xb') as stream: stream.write(raw);stream.flush();os.fsync(stream.fileno())
def physical(path):
    path=Path(path).absolute()
    require('..' not in path.parts,'parent traversal refused')
    for node in (path,*path.parents):
        info=node.lstat()
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info,'st_file_attributes',0)&0x400,'reparse/symlink path refused')
    return path.resolve(strict=True)
def identity(path):
    path=physical(path);require(path.is_file(),'regular file required')
    raw=path.read_bytes();return {'bytes':len(raw),'sha256':sha(raw)}
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module);return module
def clean_environment(python,tmp):
    root=GIT.parents[2];system=Path(os.environ.get('SystemRoot',r'C:\Windows'))
    return {'SystemRoot':str(system),'WINDIR':str(system),'PATHEXT':'.COM;.EXE;.BAT;.CMD',
       'PATH':os.pathsep.join([str(python.parent),str(GIT.parent),str(root/'cmd'),str(root/'bin'),str(root/'usr/bin'),str(system/'System32')]),
       'IMPLEMENTAUDIT_PYTHON':str(python),'PYTHONDONTWRITEBYTECODE':'1','LC_ALL':'C','LANG':'C',
       'MSYS2_ARG_CONV_EXCL':'*','TEMP':str(tmp),'TMP':str(tmp),
       'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':os.devnull,'GIT_CONFIG_SYSTEM':os.devnull,
       'GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0'}

def verify_source(source,manifest,env):
    def git(*args): return subprocess.check_output([str(GIT),'-C',str(source),*args],env=env,timeout=30)
    require(git('rev-parse','HEAD','HEAD^{tree}').decode().splitlines()==[SOURCE_HEAD,SOURCE_TREE],'source commit/tree differs')
    require(git('status','--porcelain=v1','--untracked-files=normal')==b'','qualified source is dirty')
    require(manifest['source_commit']==SOURCE_HEAD and manifest['source_tree']==SOURCE_TREE,'source manifest ancestry differs')
    source_paths={row['path'] for row in manifest['members']}
    skills={p for p in git('ls-files','-z','--','skills').decode().split('\0') if p}
    require(skills=={p for p in source_paths if p.startswith('skills/')},'runtime population differs')
    for row in manifest['members']:
        relative=Path(row['path']);require(not relative.is_absolute() and '..' not in relative.parts,'unsafe manifest path')
        raw=physical(source/relative).read_bytes()
        require(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'source member differs: '+row['path'])
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob_oid'],'source blob differs')
        stage=git('ls-files','--stage','--',row['path']).decode().strip().split()
        require(len(stage)==4 and stage[:3]==[row['git_mode'],row['git_blob_oid'],'0'],'source index member differs')
    return {'source_commit':SOURCE_HEAD,'source_tree':SOURCE_TREE,'member_count':len(manifest['members']),
            'manifest_sha256':sha(canonical(manifest)),'source_status':'CLEAN'}


def read_json_file(path):
    raw=physical(path).read_bytes()
    text=raw.decode('utf-8'); json.loads(text)
    return raw

def export_available_evidence(campaign):
    """Read existing owned output only; preserve failed native measurements without retry."""
    public=campaign.public;operation=campaign.out/'operation'
    errors={}
    def keep(name,body):
        target=public/name;raw=body if isinstance(body,bytes) else canonical(body)
        if target.exists(): require(target.read_bytes()==raw,'public evidence collision: '+name)
        else: save(target,raw)
    def capture(name,paths):
        for relative in paths:
            source=operation/relative
            if not source.exists():continue
            try:
                raw=read_json_file(source)
                # A failed attempt never acquires a PASS by choosing a fallback file.
                keep(name,{'status':'UNQUALIFIED_RECORDED_EVIDENCE','origin':relative,
                    'original_bytes':len(raw),'original_sha256':sha(raw),'original_utf8_json':raw.decode('utf-8')})
            except Exception as error: errors[name]=type(error).__name__
            return
    for name,value in [('SOURCE.json',campaign.source_before),('TOOLS.json',campaign.tools)]:
        try:
            if not (public/name).exists():keep(name,value)
        except Exception as error:errors[name]=type(error).__name__
    if not (public/'CONTROL.json').exists():
        capture('CONTROL.json',('execution/native-control/control.json','execution/native-control/job/measurement.json'))
    if not (public/'MEASUREMENT.json').exists():
        capture('MEASUREMENT.json',('execution/MEASUREMENT.json','execution/operation/measurement.json'))
    observations={}
    for label,relative in [('maintained_failure','execution/FAILURE.json'),
                           ('unqualified_readback','execution/unqualified-readback/OBSERVATION.json'),
                           ('readback_failure','execution/READBACK_FAILURE.json')]:
        source=operation/relative
        if not source.exists():continue
        try:
            raw=read_json_file(source);data=json.loads(raw)
            # Free-form error details and ATTEMPT entitlement are not public data.
            if label=='unqualified_readback':
                if isinstance(data.get('errors'),dict):
                    data['errors']={key:{'exception':value.get('exception')} for key,value in data['errors'].items()}
            else:data={key:data[key] for key in ('status','exception','automatic_retry','cleanup_or_compensation','ended_utc') if key in data}
            observations[label]={'origin':relative,'source_bytes':len(raw),'source_sha256':sha(raw),'observation':data}
        except Exception as error:errors[label]=type(error).__name__
    if observations and not (public/'RECEIVING.json').exists():
        keep('RECEIVING.json',{'status':'UNQUALIFIED_POST_ATTEMPT_OBSERVATIONS','observations':observations,
            'authority_ceiling':'NO_CURRENTNESS_TRANSITION_OR_NATIVE_ACCEPTANCE','automatic_retry':False})
    transition={}
    for key,relative in [('current','execution/CURRENT.json'),('preserved_after','execution/PRESERVED_AFTER.json')]:
        source=operation/relative
        if source.exists():
            try:transition[key]=json.loads(read_json_file(source))
            except Exception as error:errors[key]=type(error).__name__
    receipt=operation/'execution/RECEIPT.raw'
    if receipt.exists():
        try:
            raw=physical(receipt).read_bytes();transition['receipt_raw']=raw.decode('utf-8');transition['receipt_sha256']=sha(raw)
        except Exception as error:errors['receipt']=type(error).__name__
    if transition and not (public/'TRANSITION.json').exists():
        keep('TRANSITION.json',{'status':'UNQUALIFIED_RECORDED_TRANSITION','scope':'THIS_FRESH_SUBJECT_ONLY',**transition})
    return errors

def emit_public(output):
    """Read-only ASCII log transport of the exact reviewed public artifact population."""
    public=physical(Path(output)/'public')
    names={p.name for p in public.iterdir()}
    require(names<=set(PUBLIC_FILES) and 'ARTIFACT_MANIFEST.json' in names,'public population or manifest differs')
    rows=[];total=0
    for name in sorted(names):
        raw=read_json_file(public/name);total+=len(raw)
        require(len(raw)<=1048576 and total<=4194304,'public log transport size limit exceeded; artifacts retained, no truncation')
        rows.append({'name':name,'bytes':len(raw),'sha256':sha(raw),'utf8_json':raw.decode('utf-8')})
    manifest=json.loads(next(row['utf8_json'] for row in rows if row['name']=='ARTIFACT_MANIFEST.json'))
    expected={row['name']:(row['bytes'],row['sha256']) for row in manifest['members']}
    actual={row['name']:(row['bytes'],row['sha256']) for row in rows if row['name']!='ARTIFACT_MANIFEST.json'}
    require(expected==actual,'public manifest differs; no log evidence emitted')
    lines=['DG18_PUBLIC_JSON '+json.dumps(row,ensure_ascii=True,separators=(',',':')) for row in rows]
    # Bound actual ASCII transport too; allow two bytes per native line ending.
    lengths=[len(line.encode('ascii'))+2 for line in lines]
    require(all(length<=1048576 for length in lengths) and sum(lengths)<=4194304,
        'encoded public log transport size limit exceeded; artifacts retained, no truncation')
    for line in lines: print(line)

def preflight_failure(args,exc):
    """Only metadata at this exact owned Actions output; no subject/owner operation."""
    require(os.name=='nt' and os.environ.get('GITHUB_ACTIONS')=='true','no Windows preflight output on another host')
    require(os.environ.get('GITHUB_REPOSITORY')==REPOSITORY and os.environ.get('GITHUB_REF')=='refs/heads/'+BRANCH
        and os.environ.get('GITHUB_EVENT_NAME')=='push' and os.environ.get('GITHUB_RUN_ATTEMPT')=='1','preflight context differs')
    run_id=os.environ.get('GITHUB_RUN_ID','');require(re.fullmatch('[0-9]{1,20}',run_id),'run identity absent')
    parent=physical(os.environ['RUNNER_TEMP']);out=parent/('dg18-w-full-'+run_id+'-1')
    require(Path(args.output).absolute()==out,'preflight output differs')
    if out.exists():
        physical(out);require((out/'ALLOCATION_INTENT.json').is_file(),'preexisting unowned output refused')
    else:out.mkdir(exist_ok=False)
    public=out/'public';public.mkdir(exist_ok=True);physical(public)
    require(not any(public.iterdir()),'preexisting public output refused')
    save(public/'FAILURE.json',{'status':'PREFLIGHT_FAILED_NO_OWNER_LAUNCH','stage':'CONSTRUCTOR_PREFLIGHT',
        'exception_type':type(exc).__name__,'source_commit':SOURCE_HEAD,'source_tree':SOURCE_TREE,
        'subject_directory_allocated':(out/'subject with space').exists(),'owner_execution_started':False,
        'automatic_retry':False,'original_acceptance_delta':0,'raw_console_uploaded':False})
    raw=(public/'FAILURE.json').read_bytes()
    save(public/'ARTIFACT_MANIFEST.json',{'schema':'r5.windows-fresh-public-artifact-selection.v1',
        'members':[{'name':'FAILURE.json','bytes':len(raw),'sha256':sha(raw)}],
        'selection':'SANITIZED_PREFLIGHT_METADATA_ONLY; NO_SUBJECT_OR_OWNER_LAUNCH'})

def task_bodies(meta,authored,owner_source_text):
    """Author only actual new-task facts; do not import fixture receipt/history values."""
    def group(owner,value): return {'owner':owner,'value':value}
    def record(identifier,description,status='ACTIVE'):
        return {'record_id':identifier,'status':status,'description':description,
                'scope':'this newly created Windows qualification subject only','evidence_refs':['authorization']}
    instruction={'record_id':'external-new-task-authorization','issuer':'external owner approval reference',
        'subject':'Perform one fresh Windows resume receiving campaign using the pinned public source',
        'scope':'this disposable subject only; the adapter does not authenticate entitlement',
        'applicability':'APPLIES','status':'ACTIVE','evidence_refs':['authorization'],
        'issued_epoch':'G0001','expires_at':None,'supersedes':[]}
    frontier={'DONE':['actual-initialization'],'ACTIVE':['new-windows-campaign'],
              'READY':[],'BLOCKED':['independent-original-receiving']}
    state={
        'identity':group('claim-run.sh',{'controller_id':meta['controller'],'claim_id':meta['claim_id'],
            'run_root_identity':meta['run_relative'],'audit_object':'Fresh Windows whole-owner resume receiving task',
            'candidate':meta['head'],'tree':meta['tree'],'package':'Exact copied runtime at '+SOURCE_HEAD,
            'pull_request':None,'release':None}),
        'continuation':group('STATE.md',{'phase':'1','status':'open','next_action':meta['next_action'],
            'route':'ordinary','last_check':'Actual pending initialization activated; no acceptance awarded'}),
        'instructions':group('STATE.md',[dict(instruction,record_id='new-task-scope-instruction')]),
        'authorisations':group('STATE.md',[instruction]),
        'terminal':group('STATE.md',{'one_shots':[],'markers':[],'handoffs':[],'external_effects':[]}),
        'andons':group('STATE.md',[]),'original_reds':group('STATE.md',[]),
        'pending_boundaries':group('R0033/continuity',[]),
        'non_verdicts':group('STATE.md',[record('no-acceptance','New task measurements do not award original acceptance')]),
        'evidence_ceilings':group('STATE.md',[record('no-native-history','No historic H0, model session, C02 adjudication or original controller custody is asserted')]),
        'steers':group('STATE.md',[record('one-fresh-attempt','No old effect replay, automatic retry, cleanup or compensation')]),
        'rollback':group('STATE.md',{'status':'AVAILABLE','target':None,
            'conditions':['Stop and retain this newly owned subject after any uncertain effect; no automatic compensation'],
            'evidence_refs':['authorization']}),
        'runtime_artifacts':group('STATE.md',['receipt','authorization','initialization','public_owner_source','work_graph'])}
    roadmap={
        'frontier':group('WORK_GRAPH.json',frontier),
        'obligations':group('ROADMAP.md',[record('receive-fresh-operation','Retain actual whole-Job measurement and independent receiving evidence','OPEN')]),
        'deferrals':group('ROADMAP.md',[]),
        'dependencies':group('ROADMAP.md',[{'record_id':'receiving-dependency','source':'independent-original-receiving',
            'target':'new-windows-campaign','status':'BLOCKED','evidence_refs':['authorization']}]),
        'compensations':group('ROADMAP.md',[]),
        'planning':group('ROADMAP.md',{'goal':'Measure one actual fresh Windows owner resume within the maintained whole-Job contract',
            'action_selection':{'selected':['truthful new subject','actual first rotation','fresh manual invalidation','one maintained prepare/execute'],
                'omitted':['model session','historic H0','C02 adjudication','protected historical operations'],
                'rationale':'Only a fresh isolated Windows qualification episode is selected'},
            'scope_boundaries':['New disposable subject only','No retry','No original acceptance grant'],
            'baseline_ref':meta['head']})}
    bodies={}
    for role,payload in [('STATE',state),('ROADMAP',roadmap)]:
        lines=authored[role].decode().splitlines()
        require([line for line in lines if re.search(r'current\s+epoch\s*:',line,re.I)]==(['Current epoch: G0001'] if role=='STATE' else []),'ordinary author epoch shape differs')
        payload['native_guards']=group(role+'.md',{'schema_version':'implementaudit.native-guard-profile.v1',
            'lines':[line for line in lines if line!='Current epoch: G0001']})
        bodies[role]={'schema_version':'implementaudit.canonical-pair.v2','role':role,
            'pair_id':'actual-windows-'+meta['controller'],'payload':payload,'transition':None,'history':[],
            'archive_pointers':[],'artifact_refs':[],
            'continuity':{'projection_generation_id':'G0001','continuity_epoch':'G0001','invalidation_oid':None,
                'predecessor_receipt_ref_oid':None,'expected_receipt_ref':'refs/implementaudit/continuity-receipts/'+meta['controller']+'/G0001',
                'expected_receipt_schema':'implementaudit.continuity-receipt.v2','boundary':'new-session','reconciled':True}}
    bodies['STATE']['artifact_refs']=[{'artifact_id':'receipt','owner':'claim-run.sh','role':'CONTINUITY_RECEIPT',
        'locator':'refs/implementaudit/continuity-receipts/'+meta['controller']+'/G0001','object_format':'sha1'}]
    for name in ('authorization','initialization','public_owner_source'):
        bodies['STATE']['artifact_refs'].append({'artifact_id':name,'owner':'STATE.md','role':'EVIDENCE',
            'locator':'evidence/'+name+'.txt','object_format':'sha1'})
    bodies['ROADMAP']['artifact_refs']=[{'artifact_id':'work_graph','owner':'WORK_GRAPH.json','role':'WORK_GRAPH',
        'locator':'WORK_GRAPH.json','object_format':'sha1'}]
    bodies['STATE']['history']=[{'record_id':'source-captured-in-this-new-task','record_kind':'artifact.historical',
        'owner':'STATE.md','status':'PRESERVED','payload':{'text':owner_source_text,'evidence_refs':['public_owner_source'],
        'original_scope':'Exact reviewed source of claim-run-rotation.py captured earlier during this new task preparation',
        'current_applicability':'UNCHANGED','historical_refusal':None}}]
    return bodies,frontier

class Campaign:
    def __init__(self,args):
        global GIT
        require(os.name=='nt' and sys.platform=='win32','authentic Windows required; no subject allocated')
        require(sys.version_info[:2]==(3,12),'physical Python 3.12 required')
        require(os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('GITHUB_REPOSITORY')==REPOSITORY,
                'exact approved repository Actions host required')
        require(os.environ.get('GITHUB_EVENT_NAME')=='push' and os.environ.get('GITHUB_REF')=='refs/heads/'+BRANCH,
                'exact isolated push branch required')
        require(os.environ.get('GITHUB_RUN_ATTEMPT')=='1','workflow reruns refused; no old attempt replay')
        run_id=os.environ.get('GITHUB_RUN_ID','');require(re.fullmatch('[0-9]{1,20}',run_id),'actual workflow run identity missing')
        self.packet=physical(Path(__file__).parent);self.source=physical(args.source)
        self.python=physical(args.python);require(self.python.samefile(sys.executable),'selected Python differs from running physical interpreter')
        require(physical(BASH).is_file(),'fixed physical Bash required')
        available=[physical(path) for path in DIRECT_GIT_PATHS if Path(path).is_file()]
        require(available,'one maintained allowlisted direct mingw64/ucrt64 Git image required')
        GIT=available[0]
        self.entitlement=(self.packet/'entitlement-reference.txt').read_text().strip()
        require(self.entitlement and self.entitlement!='UNGRANTED' and len(self.entitlement)<=2048
                and '\n' not in self.entitlement and '\r' not in self.entitlement,
                'external owner entitlement reference has not been supplied')
        self.out=physical(Path(args.output).absolute().parent)/Path(args.output).name
        require(not self.out.exists() and not any(self.out.is_relative_to(root) for root in (self.source,self.packet)),
                'unused separated output required; no retry')
        self.repo=self.out/'subject with space';self.raw=self.out/'raw';self.public=self.out/'public';self.tmp=self.repo/'task-tmp'
        self.controller='r5-winfull-'+run_id
        require(len(self.controller)<=48,'controller namespace limit exceeded')
        self.env=clean_environment(self.python,self.tmp)
        self.manifest=json.loads((self.packet/'SOURCE_MANIFEST.json').read_text())
        self.source_before=verify_source(self.source,self.manifest,self.env)
        checker=load(self.source/'scripts/check-r0039-windows-resume.py','selected_direct_git_contract')
        require(tuple(checker.DIRECT_GIT_EXECUTABLES)==DIRECT_GIT_PATHS,'maintained direct Git allowlist differs')
        checker.direct_git_layout(str(GIT))
        self.out.mkdir(exist_ok=False)
        save(self.out/'ALLOCATION_INTENT.json',{'subject':str(self.repo),'raw_evidence':str(self.raw),'public_evidence':str(self.public),
            'controller':self.controller,'source_commit':SOURCE_HEAD,'source_tree':SOURCE_TREE,'github_run_id':run_id,
            'scope':'ONE_NEW_DISPOSABLE_WINDOWS_SUBJECT','automatic_retry':False,'original_acceptance_delta':0,
            'external_entitlement_reference_sha256':sha(self.entitlement.encode())})
        self.repo.mkdir();self.raw.mkdir();self.public.mkdir();self.tmp.mkdir()
        self.commands=[];self.stage='ALLOCATED';self.plan=None;self.initializer_controls=[]
        self.tools={name:{'path':str(physical(path)),'sha256':identity(path)['sha256']}
                    for name,path in [('bash',BASH),('python',self.python),('git',GIT)]}
        self.runner=self.source/'scripts/run-r0039-windows-resume.py'

    def command(self,argv,label,expected=0,cwd=None,timeout=240):
        argv=list(map(str,argv));began=time.time_ns()
        result=subprocess.run(argv,cwd=cwd or self.repo,env=self.env,stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
        prefix=f'{len(self.commands)+1:03d}-{label}'
        save(self.raw/(prefix+'.stdout'),result.stdout);save(self.raw/(prefix+'.stderr'),result.stderr)
        self.commands.append({'command':argv,'cwd':str(cwd or self.repo),'exit':result.returncode,
            'label':label,'elapsed_ms':(time.time_ns()-began)/1e6,'stdout_sha256':sha(result.stdout),'stderr_sha256':sha(result.stderr)})
        save(self.raw/(prefix+'.json'),self.commands[-1])
        require(result.returncode==expected,'command failed at '+label+'; evidence retained; no retry')
        return result.stdout
    def git(self,*args,label='git'): return self.command([GIT,'-C',self.repo,*args],label)
    def claim(self,*args,label='claim'): return self.command([BASH,'--noprofile','--norc',self.repo/'skills/implementaudit/scripts/claim-run.sh',*args],label)
    def refuse_activation(self,relative,token,label,reason):
        before=self.git('for-each-ref','--format=%(refname) %(objectname)','refs/implementaudit',label=label+'-refs-before')
        self.command([BASH,'--noprofile','--norc',self.repo/'skills/implementaudit/scripts/claim-run.sh',
            '--activate-controller',self.controller,'--run-root',relative,'--expected-initialization',token],label,expected=1)
        captured=self.raw/(f'{len(self.commands):03d}-'+label+'.stderr')
        require(reason in captured.read_text(encoding='utf-8'),'refusal reason differs at '+label)
        stderr_sha=identity(captured)['sha256']
        after=self.git('for-each-ref','--format=%(refname) %(objectname)','refs/implementaudit',label=label+'-refs-after')
        require(before==after,'refused activation changed an authority ref')
        self.initializer_controls.append({'case':label,'status':'EXPECTED_REFUSAL_NO_AUTHORITY_REF_CHANGE',
            'refs_before_sha256':sha(before),'refs_after_sha256':sha(after),'stderr_sha256':stderr_sha,
            'scope':'THIS_FRESH_SUBJECT_ONLY; UNUSED_GIT_BLOBS_ARE_NOT_AUTHORITY'})

    def run(self):
        self.stage='NEW_SUBJECT_INITIALIZATION'
        shutil.copytree(self.source/'skills',self.repo/'skills')
        for row in self.manifest['members']:
            if row['path'].startswith('skills/'):
                require(identity(self.repo/row['path'])=={'bytes':row['bytes'],'sha256':row['sha256']},'copied runtime differs')
        self.git('-c','init.templateDir=','init','-q','-b','qualification',label='init')
        save(self.repo/'.gitignore',b'.IMPLEMENTAUDIT/\ntask-tmp/\nskills/\n')
        save(self.repo/'TASK.md',('# Actual fresh Windows receiving task\n\nRuntime source '+SOURCE_HEAD+' / '+SOURCE_TREE+
            '\nOne new manual-resume campaign; no old history, native H0, model session, protected retry or acceptance award.\n').encode())
        self.git('add','--','TASK.md','.gitignore',label='add')
        self.git('-c','user.name=R5 Windows receiving','-c','user.email=r5-windows@example.invalid',
            '-c','commit.gpgsign=false','-c','core.hooksPath=NUL','commit','-qm','Define actual fresh Windows receiving task',label='baseline')
        head=self.git('rev-parse','HEAD',label='head').decode().strip();tree=self.git('rev-parse','HEAD^{tree}',label='tree').decode().strip()
        relative=self.claim('--controller',self.controller,'Fresh Windows W-FULL receiving',label='claim-pending').decode().strip()
        require(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9-]+-[A-Za-z0-9]{6}',relative),'unexpected claimed root')
        run=self.repo/relative;next_action='Receive the actual fresh Windows whole-owner resume and retain its measured transition'
        self.command([self.python,'-I','-X','utf8','-B',self.source/'fixtures/controller-initialization/author_checkpoint.py',
            '--repo',self.repo,'--run-root',relative,'--source',self.repo,
            '--purpose','Execute one externally authorized fresh Windows receiving campaign; no historical native occurrence or original acceptance is asserted.',
            '--next-action',next_action],'author-real-task')
        inspect=json.loads(self.claim('--inspect-controller-initialization',self.controller,'--run-root',relative,label='inspect-initialization'))
        require(not inspect['missing_files'] and inspect['current_controller_oid'] is None and inspect['binding_record_oid'] is None,'new pending initialization differs')
        invalid_token=inspect['initialization_token'].rsplit('@',1)[0]+'@'+'0'*40
        self.refuse_activation(relative,invalid_token,'invalid-initialization-token',
            'initialization token is absent, stale, copied or belongs to another claim')
        activation=json.loads(self.claim('--activate-controller',self.controller,'--run-root',relative,
            '--expected-initialization',inspect['initialization_token'],label='activate-exact'))
        require(activation['status']=='BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS','activation failed')
        claim=dict(line.split('=',1) for line in (run/'.claimed').read_text().splitlines())
        authored={role:(run/(role+'.md')).read_bytes() for role in ('STATE','ROADMAP')}
        meta={'controller':self.controller,'claim_id':claim['claim_id'],'run_relative':relative,
              'head':head,'tree':tree,'next_action':next_action}
        owner_source=(self.source/'skills/implementaudit/scripts/claim-run-rotation.py').read_bytes()
        bodies,frontier=task_bodies(meta,authored,owner_source.decode())
        factory=load(self.source/'fixtures/canonical-state-rotation/protected_projection_v2_test.py','actual_task_format_helpers')
        artifacts={'authorization':canonical({'reference':self.entitlement,'scope':'this new Windows subject only',
            'authentication':'EXTERNAL_OWNER_REQUIRED; NOT_AUTHENTICATED_BY_ADAPTER'}),
            'initialization':canonical(activation),'public_owner_source':owner_source,
            'work_graph':canonical({'schema':'r5.new-task-frontier.v1','frontier':frontier,'authority':'TASK_FACTS_ONLY'})}
        for name in ('authorization','initialization','public_owner_source'): save(run/'evidence'/(name+'.txt'),artifacts[name])
        save(run/'WORK_GRAPH.json',artifacts['work_graph'])
        pair=factory.render_pair(bodies)
        require(sum(map(len,pair.values()))>131072,'actual captured public source workload does not trigger byte policy')
        for role in ('STATE','ROADMAP'):
            (run/(role+'.md')).write_bytes(pair[role])
            self.command([self.python,'-I','-X','utf8','-B','-c','from pathlib import Path;import sys;sys.stdout.buffer.write(Path(sys.argv[1]).read_bytes())',run/(role+'.md')],'read-'+role)
        legacy=self.claim('--resume-controller',self.controller,'--boundary','new-session','--epoch','G0001',label='normal-first-resume').decode().strip()
        require(self.claim('--verify-resume-receipt',legacy,label='verify-first').decode().strip()==legacy,'first receipt differs')
        require(self.claim('--require-current-continuity',self.controller,label='require-first').decode().strip()==legacy,'first currentness differs')
        # One pending successor proves the corrected controller wire is consumed by
        # the existing predecessor owner. It is never activated or resumed.
        controller_before=self.git('rev-parse','refs/implementaudit/controllers/'+self.controller,label='predecessor-controller-oid').decode().strip()
        successor_relative=self.claim('--controller',self.controller,'--supersede-claim',claim['claim_id'],
            'Inspect actual Windows initialization predecessor',label='prepare-pending-successor').decode().strip()
        self.command([self.python,'-I','-X','utf8','-B',self.source/'fixtures/controller-initialization/author_checkpoint.py',
            '--repo',self.repo,'--run-root',successor_relative,'--source',self.repo,
            '--purpose','Qualify exact initialized Windows predecessor parsing and stale expected-old refusal; no activation or new resume is intended.',
            '--next-action','After the measured owner transition, require this pending activation to refuse its stale expected-old guards'],
            'author-pending-successor-control')
        successor_inspect=json.loads(self.claim('--inspect-controller-initialization',self.controller,
            '--run-root',successor_relative,label='inspect-actual-predecessor'))
        require(successor_inspect['predecessor_kind']=='INITIALIZED_PREDECESSOR'
            and successor_inspect['current_controller_oid']==controller_before
            and successor_inspect['binding_record_oid'] is None and not successor_inspect['missing_files'],
            'exact initialized predecessor was not received')
        self.refuse_activation(successor_relative,inspect['initialization_token'],'foreign-claim-initialization-token',
            'initialization token is absent, stale, copied or belongs to another claim')
        require(self.claim('--require-current-continuity',self.controller,label='require-after-predecessor-inspection').decode().strip()==legacy,
            'pending predecessor inspection changed currentness')
        self.initializer_controls.append({'case':'actual-initialized-predecessor','status':'PASS_READ_EXISTING_PREDECESSOR_NO_ACTIVATION',
            'current_controller_oid':controller_before,'pending_run':successor_relative,
            'predecessor_kind':successor_inspect['predecessor_kind'],'binding_record_oid':None})
        artifacts['receipt']=self.git('cat-file','blob',legacy.split('@')[1],label='actual-first-receipt-blob')
        save(run/'owner-map.json',{'schema':'implementaudit.rotation-owner-map.v2','owner_map':factory.build_owner_map(bodies,pair,artifacts)})
        self.stage='ACTUAL_PREDECESSOR_ROTATION'
        rotation=json.loads(self.claim('--rotate-canonical-state',self.controller,'--owner-map','owner-map.json',label='first-rotation'))
        require(rotation['status']=='ROTATED','real byte-triggered predecessor rotation failed')
        self.claim('--require-current-continuity',self.controller,label='require-migrated-predecessor')
        self.stage='FRESH_MANUAL_BOUNDARY'
        self.claim('--invalidate-continuity',self.controller,'--boundary','manual-resume',
            '--event','new-windows-campaign-'+os.environ['GITHUB_RUN_ID']+'-manual-resume',label='fresh-manual-invalidation')
        self.stage='MAINTAINED_PREPARE'
        operation=self.out/'operation'
        prepared=json.loads(self.command([self.python,'-I','-X','utf8','-B',self.runner,'prepare','--source',self.source,
            '--repo',self.repo,'--controller',self.controller,'--source-head',SOURCE_HEAD,'--source-tree',SOURCE_TREE,
            '--bash',BASH,'--python',self.python,'--git',GIT,'--out',operation],'maintained-prepare'))
        self.plan=Path(prepared['plan']);plan_hash=identity(self.plan)['sha256']
        require(prepared['sha256']==plan_hash,'prepared plan digest differs')
        self.stage='MAINTAINED_SINGLE_EXECUTE'
        self.command([self.python,'-I','-X','utf8','-B',self.runner,'execute','--plan',self.plan,'--plan-sha256',plan_hash,
            '--entitlement-reference',self.entitlement],'maintained-execute',timeout=600)
        result=json.loads((operation/'execution/RESULT.json').read_bytes())
        require(result['status']=='RECORDED_OPERATION_READY_FOR_INDEPENDENT_RECEIVING','maintained operation not qualified for receiving')
        require(verify_source(self.source,self.manifest,self.env)==self.source_before,'source changed after operation')
        self.stage='STALE_INITIALIZATION_GUARD_RECEIVING'
        self.refuse_activation(successor_relative,successor_inspect['initialization_token'],'stale-expected-old-initialization',
            'initialization expected-old source/controller/boundary changed')
        current=json.loads((operation/'execution/CURRENT.json').read_bytes())
        require(self.claim('--require-current-continuity',self.controller,label='require-after-stale-initialization-refusal').decode().strip()==current['receipt_token'],
            'stale initialization refusal changed currentness')
        self.stage='PUBLISH_SELECTED_NEW_SUBJECT_EVIDENCE'
        for name,relative_path in [('CONTROL.json','execution/native-control/control.json'),
                                  ('MEASUREMENT.json','execution/MEASUREMENT.json')]:
            save(self.public/name,(operation/relative_path).read_bytes())
        current=json.loads((operation/'execution/CURRENT.json').read_bytes())
        save(self.public/'TRANSITION.json',{'assessment':result['transition'],'current':current,
              'receipt_raw':(operation/'execution/RECEIPT.raw').read_text(),'scope':'THIS_FRESH_SUBJECT_ONLY'})
        save(self.public/'RECEIVING.json',{'status':result['status'],'authority_ceiling':result['authority_ceiling'],
            'plan_sha256':plan_hash,'verify_stdout_sha256':identity(operation/'execution/verify-receipt.stdout')['sha256'],
            'require_stdout_sha256':identity(operation/'execution/require-current.stdout')['sha256'],
            'original_acceptance_delta':0,'initializer_controls':self.initializer_controls,
            'scope':'MAINTAINED_SEPARATE_PROCESS_RECEIVING; EXTERNAL_INDEPENDENT_REVIEW_PENDING'})
        save(self.public/'SOURCE.json',self.source_before);save(self.public/'TOOLS.json',self.tools)
        save(self.public/'RESULT.json',{'status':result['status'],'measurement':result['measurement'],
            'source_commit':SOURCE_HEAD,'source_tree':SOURCE_TREE,'controller':self.controller,
            'subject_head':head,'subject_tree':tree,'first_receipt':legacy,'final_receipt':current['receipt_token'],
            'source_manifest_sha256':self.source_before['manifest_sha256'],'plan_sha256':plan_hash,
            'authority_ceiling':result['authority_ceiling'],'original_acceptance_delta':0,
            'measurement_scope':'WHOLE_RESUME_OWNER_JOB; PREPARATION_CONTROL_HARNESS_AND_INDEPENDENT_RECEIVING_OUTSIDE_JOB',
            'maximum_ms':60000,'maximum_aggregate_job_committed_bytes':201326592,'baseline_subtracted_bytes':0})
        self.publish_manifest()
        print(json.dumps({'status':result['status'],'public_manifest_sha256':identity(self.public/'ARTIFACT_MANIFEST.json')['sha256'],
                          'original_acceptance_delta':0},sort_keys=True))

    def publish_manifest(self):
        present={path.name for path in self.public.iterdir()}
        require(present<=set(PUBLIC_FILES)-{'ARTIFACT_MANIFEST.json'},'unexpected public artifact')
        rows=[{'name':name,**identity(self.public/name)} for name in sorted(present)]
        save(self.public/'ARTIFACT_MANIFEST.json',{'schema':'r5.windows-fresh-public-artifact-selection.v1','members':rows,
            'selection':'EXPLICIT_NEW_SUBJECT_DATA_ONLY; NO_CONSOLE_HIDDEN_FILES_PRIVATE_ARCHIVE_OR_SEALED_ANSWERS'})
    def failure(self,exc):
        # The maintained runner owns post-attempt reconciliation. Never launch another resume here.
        final_refs={'status':'NOT_APPLICABLE_NO_SUBJECT_GIT'}
        if (self.repo/'.git').exists():
            try:
                raw=self.git('for-each-ref','--format=%(refname) %(objectname)','refs/implementaudit',label='failure-readback-refs')
                pairs=[line.split(' ',1) for line in raw.decode('utf-8').splitlines()]
                require(all(len(row)==2 and row[0].startswith('refs/implementaudit/')
                    and re.fullmatch('[0-9a-f]{40}',row[1]) for row in pairs),'final ref readback shape differs')
                final_refs={'status':'UNQUALIFIED_FINAL_REFS_OBSERVED','stdout_sha256':sha(raw),
                    'refs':dict(pairs),'scope':'AFTER_THE_ADAPTER_FAILURE; NOT_A_CURRENTNESS_OR_TRANSITION_VERDICT'}
            except Exception as error:
                final_refs={'status':'FINAL_REFS_QUERY_FAILED','exception_type':type(error).__name__}
                if self.commands and self.commands[-1]['label']=='failure-readback-refs':
                    final_refs.update({key:self.commands[-1][key] for key in ('exit','stdout_sha256','stderr_sha256')})
        export_errors=export_available_evidence(self)
        if not (self.public/'FAILURE.json').exists():
            save(self.public/'FAILURE.json',{'status':'FAILED_RETAINED_NO_RETRY','stage':self.stage,
                'exception_type':type(exc).__name__,'source_commit':SOURCE_HEAD,'controller':self.controller,
                'raw_evidence_uploaded':False,'authority':'NONE','original_acceptance_delta':0,
                'available_evidence_export_errors':export_errors,'initializer_controls':self.initializer_controls,
                'adapter_final_refs':final_refs})
        if not (self.public/'ARTIFACT_MANIFEST.json').exists(): self.publish_manifest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path);parser.add_argument('--python',type=Path)
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('--emit-public',action='store_true')
    args=parser.parse_args()
    if args.emit_public:
        emit_public(args.output);return
    require(args.source is not None and args.python is not None,'source and physical Python are required')
    campaign=None
    try:
        campaign=Campaign(args)
        campaign.run()
    except BaseException as exc:
        try:
            if campaign is None:preflight_failure(args,exc)
            else:campaign.failure(exc)
        except Exception as evidence_error:
            # Preserve the primary exception; no retry or alternate operation follows.
            print(json.dumps({'status':'FAILURE_EXPORT_INCOMPLETE','exception_type':type(evidence_error).__name__,
                'original_acceptance_delta':0},sort_keys=True))
        raise

if __name__=='__main__': main()
