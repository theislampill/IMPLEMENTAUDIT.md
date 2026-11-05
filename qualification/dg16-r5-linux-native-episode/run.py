#!/usr/bin/env python3
"""Prospective single-job original14 native bank episode; no formal acceptance.

Reconstructed after loss. Each --step is a distinct completed workflow action.
Only the fixed case bank executes; imported host utility's primitive run is never called.
Private checkpoint, controller documents, receipts, and raw streams are not public outputs.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import sys
import time
import types

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg16-r5-linux-native-episode-01-20261105'
SOURCE_COMMIT = '539aa846e37eab2dd527912d5e5eaa95f69d61cf'
SOURCE_TREE = '6a278e8c95eb1812ce39ca1af288532d4951d860'
UTILITY_SHA = '04e1e49783458e1314734fee8ed87f5179e2860ee9f4eb3dd2445d8a9068d705'
MANIFEST_SHA = '135398e23c7811fd2003ff093f1610f0bb20cc369833b21a0733f217afa67265'
BANK = 'tests/work-graph-original14-receiving-cases.py'
OWNER = 'skills/implementaudit/scripts/claim-run.sh'
AUTHOR = 'fixtures/controller-initialization/author_checkpoint.py'
TESTS = (
 'test_actual_later_invalidation_prevents_return',
 'test_derivative_snapshot_change_after_use_prevents_return',
 'test_native_intake_later_boundary_prevents_return',
 'test_native_intake_rejects_opaque_fixture_work_graph',
 'test_native_intake_rejects_unowned_nested_record',
 'test_native_intake_uses_current_original14_not_retired_root',
 'test_protected_document_change_after_use_prevents_return',
 'test_real_original14_documents_reach_unchanged_graph_parser',
 'test_valid_original14_owner_does_not_supply_missing_graph_document',
)
STEPS = ('preflight','initialize','discover','invalidate','read-state','read-roadmap',
         'resume','verify','require','bank','receive')
NAMES = ('STATE.md','PROTOCOL.md','ROADMAP.md','THINKING.md','sidecars.md','tools.md','context.md')
PUBLIC_NAMES = ('RESULT.json','HOST.json','SOURCE.json','PROBE.json','CLEANUP.json','FAILURE.json','ARTIFACT_MANIFEST.json')
RUN_SECONDS, BANK_SECONDS, FINAL_SECONDS = 900, 600, 30
PURPOSE = 'Run the unchanged public nine-case original14 native receiving bank under fresh hosted custody and retain only its source-host-scoped result before teardown.'
NEXT_ACTION = 'Execute the unchanged nine-case bank and mechanically receive its exact result while this fresh controller is current; no G1, C5, full G2, G3, or original acceptance is asserted.'
KNOWN_CODES = ('CONTINUITY_TRANSPORT_NAMESPACE_REFUSED','CONTINUITY_TRANSPORT_TIMEOUT','CANONICAL_WORK_GRAPH','SOURCE_PROFILE_REFUSED','NATIVE_CHECKPOINT','NETLINK_ROUTE','OS_OPERATION_NOT_PERMITTED','OS_PERMISSION_DENIED','OS_REQUIRED_PATH_UNAVAILABLE')
EXCEPTIONS = ('AssertionError','RuntimeError','ValueError','OSError','TimeoutError','WorkGraphError','ContinuityTransportError','FileNotFoundError','PermissionError','OTHER')

class Refusal(Exception): pass
class Deadline(Exception): pass

def need(value, code):
    if not value: raise Refusal(code)

def digest(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
def token(raw, pattern):
    text=raw.decode('ascii').strip(); need(re.fullmatch(pattern,text) is not None,'OWNER_TOKEN_SHAPE_REFUSED'); return text

def load_utility():
    path=Path(__file__).with_name('host_utility.py')
    raw=path.read_bytes(); need(digest(raw)==UTILITY_SHA,'UTILITY_DIGEST_REFUSED')
    module=types.ModuleType('sealed_host_utility'); module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module

def identities(path):
    p=Path(path); st=p.lstat();need(stat.S_ISDIR(st.st_mode) and not p.is_symlink(),'DIRECTORY_CUSTODY_REFUSED')
    return [st.st_dev,st.st_ino,st.st_uid]

def read_manifest(u):
    raw=u.checked_file(Path(__file__).with_name('SOURCE_MANIFEST.json'),1024*1024)
    need(digest(raw)==MANIFEST_SHA,'SOURCE_MANIFEST_DIGEST_REFUSED'); m=u.parse_json(raw)
    need(set(m)=={'schema','repository','commit','tree','file_count','total_bytes','members'} and
         m['schema']=='dg16.linux-native-source-manifest.v2' and m['repository']==REPOSITORY and
         m['commit']==SOURCE_COMMIT and m['tree']==SOURCE_TREE and m['file_count']==1735 and
         m['total_bytes']==163394357 and len(m['members'])==1735,'SOURCE_MANIFEST_SHAPE_REFUSED')
    result={}
    for row in m['members']:
        need(set(row)=={'path','mode','git_blob','bytes','sha256'} and isinstance(row['path'],str),'SOURCE_MEMBER_REFUSED')
        p=PurePosixPath(row['path']);need(not p.is_absolute() and '..' not in p.parts and str(p)==row['path'] and
             row['path'] not in result and row['mode'] in ('100644','100755') and
             type(row['bytes']) is int and 0<=row['bytes']<=256*1024**2 and
             re.fullmatch('[0-9a-f]{40}',row['git_blob']) and re.fullmatch('[0-9a-f]{64}',row['sha256']), 'SOURCE_MEMBER_REFUSED')
        result[row['path']]=row
    need(sum(row['bytes'] for row in result.values())==m['total_bytes'],'SOURCE_SIZE_REFUSED')
    return result

def verify_source(source,manifest,u,runtime=False):
    observed=set();total=0
    allowed_dirs={str(p) for name in manifest for p in PurePosixPath(name).parents if str(p)!='.'}
    for parent,dirs,files in os.walk(source,followlinks=False):
        here=Path(parent)
        for name in list(dirs):
            p=here/name; rel=p.relative_to(source).as_posix(); st=p.lstat()
            need(stat.S_ISDIR(st.st_mode) and not p.is_symlink(),'SOURCE_DIRECTORY_SHAPE_REFUSED')
            if here==source and name=='.git':dirs.remove(name)
            elif here==source and name=='.IMPLEMENTAUDIT':
                need(runtime,'UNEXPECTED_RUNTIME_BEFORE_CLAIM');dirs.remove(name)
            else:need(rel in allowed_dirs,'UNEXPECTED_SOURCE_DIRECTORY')
        for name in files:
            p=here/name;rel=p.relative_to(source).as_posix()
            need(rel in manifest,'UNEXPECTED_SOURCE_FILE');row=manifest[rel];st=p.lstat()
            need(stat.S_ISREG(st.st_mode) and st.st_nlink==1 and not st.st_mode & 0o6000 and
                 bool(st.st_mode & 0o111)==(row['mode']=='100755'),'SOURCE_FILE_MODE_REFUSED')
            raw=u.checked_file(p,256*1024**2);need(len(raw)==row['bytes'] and digest(raw)==row['sha256'] and
                 hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'SOURCE_BYTES_REFUSED')
            total+=len(raw);observed.add(rel)
    need(observed==set(manifest) and total==163394357,'SOURCE_POPULATION_REFUSED')
    return {'file_count':len(observed),'total_bytes':total,'manifest_sha256':MANIFEST_SHA,'all_members_match':True}

def runtime_snapshot(source,state,u):
    run=state['run_root'];need(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9][a-z0-9-]*-[A-Za-z0-9]{6}',run),'RUN_ROOT_SHAPE_REFUSED')
    base=source/'.IMPLEMENTAUDIT'; expected={'.r36-locks/namespace.gate'}
    prefix=run.removeprefix('.IMPLEMENTAUDIT/')+'/'
    expected.update(prefix+n for n in (*NAMES,'phases/phase-1.md','.claimed','.controller'))
    observed={};directories=set();total=0
    for parent,dirs,files in os.walk(base,followlinks=False):
        here=Path(parent);st=here.lstat();need(stat.S_ISDIR(st.st_mode) and st.st_uid==os.geteuid() and not here.is_symlink(),'RUNTIME_DIRECTORY_REFUSED')
        directories.add(here.relative_to(base).as_posix())
        for name in dirs:need(not (here/name).is_symlink(),'RUNTIME_SYMLINK_REFUSED')
        for name in files:
            p=here/name;rel=p.relative_to(base).as_posix();st=p.lstat();need(rel in expected and st.st_uid==os.geteuid(),'RUNTIME_POPULATION_REFUSED')
            raw=u.checked_file(p,65536);total+=len(raw);need(total<=512*1024,'RUNTIME_AGGREGATE_BOUND')
            observed[rel]={'bytes':len(raw),'sha256':digest(raw),'device':st.st_dev,'inode':st.st_ino}
    expected_dirs={'.','.r36-locks','runs',run.removeprefix('.IMPLEMENTAUDIT/'),run.removeprefix('.IMPLEMENTAUDIT/')+'/phases'}
    need(set(observed)==expected and directories==expected_dirs,'RUNTIME_POPULATION_REFUSED')
    need(observed['.r36-locks/namespace.gate']['bytes']==1,'RUNTIME_GATE_SHAPE_REFUSED')
    return observed

def write_private(path,raw):
    need(not path.exists(),'PRIVATE_MEMBER_ALREADY_EXISTS')
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    os.chmod(path,0o600)

def save_state(path,state):
    tmp=path.with_suffix('.next');need(not tmp.exists(),'STATE_WRITE_INTERRUPTED')
    with tmp.open('xb') as f:f.write(canonical(state));f.flush();os.fsync(f.fileno())
    os.chmod(tmp,0o600);os.replace(tmp,path)

def host_context(output,source,mode):
    e=os.environ;need(e.get('GITHUB_ACTIONS')=='true' and e.get('GITHUB_REPOSITORY')==REPOSITORY and
         e.get('GITHUB_EVENT_NAME')=='push' and e.get('GITHUB_REF')=='refs/heads/'+BRANCH and
         e.get('GITHUB_RUN_ATTEMPT')=='1','EVENT_GUARD_REFUSED')
    run=e.get('GITHUB_RUN_ID','');sha=e.get('GITHUB_SHA','')
    need(re.fullmatch('[0-9]{1,20}',run) and re.fullmatch('[0-9a-f]{40}',sha),'HOSTED_IDENTITY_REFUSED')
    workspace=Path(e['GITHUB_WORKSPACE']).resolve(strict=True);temp=Path(e['RUNNER_TEMP']).resolve(strict=True)
    need(output==temp/('dg16-linux-native-episode-'+run+'-1') and source==workspace/'qualified-source' and
         source.resolve(strict=True)==source,'RESOURCE_SCOPE_REFUSED')
    need(Path(__file__).absolute().parent==workspace/'packet/qualification/dg16-r5-linux-native-episode','PACKET_LOCATION_REFUSED')
    return {'repository':REPOSITORY,'branch':BRANCH,'run_id':run,'run_attempt':1,'workflow_commit':sha}

# The CHILD below is a result-recorder wrapper. It does not replace any test,
# fixture, native owner, assertion, population, or source constant.
CHILD = r'''import hashlib,importlib.util,io,json,os,pathlib,sys,traceback,unittest
sys.dont_write_bytecode=True
root=pathlib.Path(sys.argv[1]); path=root/'tests/work-graph-original14-receiving-cases.py'
os.chdir(root)
spec=importlib.util.spec_from_file_location('hosted_original14',path)
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
expected=json.loads(sys.argv[2]); suite=unittest.defaultTestLoader.loadTestsFromTestCase(module.Original14GraphReceiving)
names=[test._testMethodName for test in suite]
if names!=expected:raise RuntimeError('BANK_POPULATION_REFUSED')
class Record(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.rows=[]
    def record(self,test,outcome,err=None):
        row={'test':test._testMethodName,'outcome':outcome,'exception_type':None,
             'diagnostic_bytes':0,'diagnostic_sha256':hashlib.sha256(b'').hexdigest(),'known_codes':[]}
        if err is not None:
            raw=''.join(traceback.format_exception(*err)).encode('utf-8','replace')
            kind=err[0].__name__
            row.update(exception_type=kind if kind in ('AssertionError','RuntimeError','ValueError','OSError',
                       'TimeoutError','WorkGraphError','ContinuityTransportError','FileNotFoundError','PermissionError') else 'OTHER',
                       diagnostic_bytes=len(raw),diagnostic_sha256=hashlib.sha256(raw).hexdigest())
            needles=(('CONTINUITY_TRANSPORT_NAMESPACE_REFUSED',b'CONTINUITY_TRANSPORT_NAMESPACE_REFUSED'),
                     ('CONTINUITY_TRANSPORT_TIMEOUT',b'CONTINUITY_TRANSPORT_TIMEOUT'),
                     ('CANONICAL_WORK_GRAPH',b'canonical WORK_GRAPH'),
                     ('SOURCE_PROFILE_REFUSED',b'SOURCE_REFUSED'),
                     ('NATIVE_CHECKPOINT',b'native checkpoint'),
                     ('NETLINK_ROUTE',b'NETLINK_ROUTE'),
                     ('OS_OPERATION_NOT_PERMITTED',b'Operation not permitted'),
                     ('OS_PERMISSION_DENIED',b'Permission denied'),
                     ('OS_REQUIRED_PATH_UNAVAILABLE',b'No such file or directory'))
            row['known_codes']=[name for name,needle in needles if needle in raw]
        self.rows.append(row)
    def addSuccess(self,test):super().addSuccess(test);self.record(test,'PASS')
    def addFailure(self,test,err):super().addFailure(test,err);self.record(test,'FAIL',err)
    def addError(self,test,err):super().addError(test,err);self.record(test,'ERROR',err)
    def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,'SKIP')
    def addExpectedFailure(self,test,err):super().addExpectedFailure(test,err);self.record(test,'EXPECTED_FAILURE',err)
    def addUnexpectedSuccess(self,test):super().addUnexpectedSuccess(test);self.record(test,'UNEXPECTED_SUCCESS')
stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Record).run(suite)
raw=stream.getvalue().encode('utf-8','replace')
record={'schema':'dg16.linux-native-bank.v1','test_population':names,'tests_run':result.testsRun,
        'success':result.wasSuccessful(),'rows':result.rows,'runner_text_bytes':len(raw),
        'runner_text_sha256':hashlib.sha256(raw).hexdigest()}
print(json.dumps(record,sort_keys=True,separators=(',',':')),flush=True)
raise SystemExit(0 if result.wasSuccessful() else 1)
'''

def validate_bank(v):
    need(type(v) is dict and set(v)=={'schema','test_population','tests_run','success','rows','runner_text_bytes','runner_text_sha256'} and
         v['schema']=='dg16.linux-native-bank.v1' and v['test_population']==list(TESTS) and
         type(v['tests_run']) is int and v['tests_run']==9 and type(v['success']) is bool and
         type(v['rows']) is list and len(v['rows'])==9 and type(v['runner_text_bytes']) is int and v['runner_text_bytes']>=0 and
         re.fullmatch('[0-9a-f]{64}',v['runner_text_sha256']),'BANK_RESULT_SHAPE_REFUSED')
    seen=[]
    for row in v['rows']:
        need(type(row) is dict and set(row)=={'test','outcome','exception_type','diagnostic_bytes','diagnostic_sha256','known_codes'} and
             row['test'] in TESTS and row['outcome'] in ('PASS','FAIL','ERROR','SKIP','EXPECTED_FAILURE','UNEXPECTED_SUCCESS') and
             (row['exception_type'] is None or row['exception_type'] in EXCEPTIONS) and
             type(row['diagnostic_bytes']) is int and row['diagnostic_bytes']>=0 and
             re.fullmatch('[0-9a-f]{64}',row['diagnostic_sha256']) and type(row['known_codes']) is list and
             len(row['known_codes'])==len(set(row['known_codes'])) and all(x in KNOWN_CODES for x in row['known_codes']),'BANK_ROW_REFUSED')
        seen.append(row['test'])
    need(seen==list(TESTS),'BANK_RESULT_POPULATION_REFUSED')
    return v

def fresh_state(context,source,output):
    start=time.monotonic()
    return {'schema':'dg16.linux-native-private-episode.v1','context':context,
       'controller':'r5-linux-native-'+context['run_id']+'-a1','run_root':None,'receipt':None,
       'completed':[],'failed':False,'started_monotonic':start,'deadline_monotonic':start+RUN_SECONDS,
       'source_directory_identity':identities(source),'git_directory_identity':identities(source/'.git'),
       'output_directory_identity':identities(output),'runtime':None,'reads':{},
       'docs':{
        'RESULT.json':dict(context,schema='dg16.linux-native-episode-result.v1',status='UNQUALIFIED',
          scope='UNCHANGED_NINE_CASE_ORIGINAL14_NATIVE_RECEIVING_BANK_IN_FRESH_HOSTED_CHECKOUT',
          G1=False,C5=False,full_G2=False,G3=False,original_acceptance=False,audit_closure=False,
          independent_assessment=False,automatic_retry=False,adapter_sha256=digest(Path(__file__).read_bytes()),
          utility_sha256=UTILITY_SHA,source_manifest_sha256=MANIFEST_SHA),
        'HOST.json':{'schema':'dg16.linux-native-episode-host.v1','tools':{},'commands':[]},
        'SOURCE.json':{'schema':'dg16.linux-native-episode-source.v1','commit':SOURCE_COMMIT,'tree':SOURCE_TREE,
                       'before':None,'after':None,'tracked_source_mutations':False},
        'PROBE.json':{'schema':'dg16.linux-native-episode-operation.v1','bank':BANK,'expected_tests':list(TESTS),
           'child_sha256':digest(CHILD.encode()),'started':False,'result':None,'phases':[],
           'fresh_controller':False,'separate_state_roadmap_reads':False,'currentness_before_bank':False,
           'receiving':{'status':'NOT_RECEIVED','authority':'NONE','receipt_transfer_authority':False},
           'episode_watchdog_seconds':RUN_SECONDS,'bank_watchdog_seconds':BANK_SECONDS},
        'CLEANUP.json':{'schema':'dg16.linux-native-episode-cleanup.v1','all_step_children_reaped':True,
           'source_unchanged':False,'runtime_unchanged_after_initialization':False,
           'private_outputs_uploaded':False,'private_retention':'LIVE_JOB_ONLY; no universal interrupted-stream retention'},
        'FAILURE.json':{'schema':'dg16.linux-native-episode-failure.v1','present':False,'failures':[]}
       }}

def inventory(u):
    need(sys.platform=='linux' and os.name=='posix' and os.geteuid()!=0 and os.uname().machine=='x86_64','HOST_IDENTITY_REFUSED')
    release={}
    for line in u.checked_file(Path('/etc/os-release').resolve(),16384).decode().splitlines():
        if '=' in line:
            k,v=line.split('=',1)
            if k in ('ID','VERSION_ID'):release[k]=u.token(v.strip('"'),32)
    need(release=={'ID':'ubuntu','VERSION_ID':'26.04'},'OS_IMAGE_REFUSED')
    paths={};facts={}
    for name in ('bwrap','bash','python3','git'):
        paths[name],facts[name]=u.trusted(name);need(paths[name] is not None,'TRUSTED_TOOL_UNAVAILABLE')
    need(Path(sys.executable).resolve()==Path(paths['python3']),'INTERPRETER_IDENTITY_REFUSED')
    host={'os':release,'architecture':'x86_64','kernel':u.token(os.uname().release),'uid':os.geteuid(),
      'python_version':list(sys.version_info[:3]),'image_os':u.token(os.environ.get('ImageOS','')),
      'image_version':u.token(os.environ.get('ImageVersion','')),'tools':facts,
      'boot_identity_sha256':digest(u.checked_file(Path('/proc/sys/kernel/random/boot_id'),128))}
    return paths,host

def enable_subreaper():
    lib=ctypes.CDLL(None,use_errno=True);actual=ctypes.c_int()
    need(lib.prctl(36,1,0,0,0)==0 and lib.prctl(37,ctypes.byref(actual),0,0,0)==0 and actual.value==1,'SUBREAPER_REFUSED')

def check_source_git(command,tools,source,full=False):
    rc,out,err=command('source-identity',[tools['git'],'-C',str(source),'rev-parse','HEAD','HEAD^{tree}'])
    need(rc==0 and not err and out.decode().splitlines()==[SOURCE_COMMIT,SOURCE_TREE],'SOURCE_GIT_IDENTITY_REFUSED')
    if not full:return
    for kind,args in (('index-clean',['diff','--cached','--quiet','--exit-code']),('tracked-clean',['diff','--quiet','--exit-code'])):
        rc,out,err=command(kind,[tools['git'],'-C',str(source),*args]);need(rc==0 and not out and not err,'SOURCE_TRACKED_STATE_CHANGED')

def operation(step,state,source,output,tools,u,manifest,command):
    docs=state['docs'];probe=docs['PROBE.json'];helper=str(source/OWNER);controller=state['controller'];private=output/'private'
    def owner(label,args):
        rc,out,err=command(label,[tools['bash'],helper,*args]);need(rc==0,'MAINTAINED_OWNER_REFUSED')
        write_private(private/(label+'.stdout'),out);write_private(private/(label+'.stderr'),err)
        return out
    def current(label):
        raw=owner(label,['--require-current-continuity',controller]);need(raw.decode().strip()==state['receipt'],'CURRENT_RECEIPT_CHANGED');return digest(raw)
    if step=='preflight':
        docs['SOURCE.json']['before']=verify_source(source,manifest,u,False)
        rc,out,err=command('no-imported-controller-refs',[tools['git'],'for-each-ref','--format=%(refname)','refs/implementaudit'])
        need(rc==0 and not out and not err,'PREEXISTING_CONTROLLER_REFS_REFUSED')
    elif step=='initialize':
        raw=owner('fresh-claim',['--controller',controller,'r5-linux-native-bank'])
        run=token(raw,r'\.IMPLEMENTAUDIT/runs/r5-linux-native-bank-[A-Za-z0-9]{6}');state['run_root']=run
        rc,out,err=command('author-real-task',[tools['python3'],'-I','-S','-B',str(source/AUTHOR),
             '--repo',str(source),'--run-root',run,'--source',str(source),'--purpose',PURPOSE,'--next-action',NEXT_ACTION])
        write_private(private/'author-real-task.stdout',out);write_private(private/'author-real-task.stderr',err)
        need(rc==0,'REAL_TASK_AUTHOR_REFUSED');value=u.parse_json(out)
        need(type(value) is dict and set(value)==set((*NAMES,'phases/phase-1.md')) and all(type(v) is str and re.fullmatch('[0-9a-f]{64}',v) for v in value.values()),'AUTHOR_RESULT_SHAPE_REFUSED')
        for name,sha in value.items():need(digest(u.checked_file(source/run/name,65536))==sha,'AUTHORED_TASK_READBACK_REFUSED')
        inspected=u.parse_json(owner('inspect-initialization',['--inspect-controller-initialization',controller,'--run-root',run]))
        init=inspected['initialization_token'];need(type(init) is str and re.fullmatch('refs/implementaudit/controller-initializations/'+controller+r'/[0-9a-f]{32}@[0-9a-f]{40}',init),'INITIALIZATION_TOKEN_REFUSED')
        activated=u.parse_json(owner('activate-initialization',['--activate-controller',controller,'--run-root',run,'--expected-initialization',init]))
        need(activated.get('status')=='BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS' and
             activated.get('authority_ceiling')=='ELIGIBLE_FOR_NORMAL_CURRENTNESS_ONLY','ACTIVATION_SCOPE_REFUSED')
        state['runtime']=runtime_snapshot(source,state,u);probe['fresh_controller']=True
        probe['fresh_initialization_sha256']=digest(canonical(activated))
    elif step=='discover':
        raw=owner('discover-controller',['--current-controller',controller]);fields=raw.decode().strip().split('\t')
        need(len(fields)==4 and fields[0]==controller and Path(fields[1])==source and
             Path(fields[2])==source/state['run_root'],'CURRENT_CONTROLLER_CONTEXT_REFUSED')
        probe['same_checkout_controller_discovered']=True
    elif step=='invalidate':
        event='github-run-'+state['context']['run_id']+'-attempt-1-fresh-hosted-job'
        raw=owner('invalidate-new-session',['--invalidate-continuity',controller,'--boundary','new-session','--event',event])
        state['invalidation']=token(raw,'refs/implementaudit/continuity-invalidations/'+controller+r'@[0-9a-f]{40}')
        probe['boundary_invalidation_sha256']=digest(raw)
    elif step in ('read-state','read-roadmap'):
        name='STATE.md' if step=='read-state' else 'ROADMAP.md';path=source/state['run_root']/name
        raw=u.checked_file(path,65536);write_private(private/(step+'.read'),raw)
        # These invocations are distinct ordered Actions steps, never a composed read.
        state['reads'][name]={'sha256':digest(raw),'bytes':len(raw),'step_ordinal':len(state['completed'])+1}
        if step=='read-roadmap':
            need(state['reads']['STATE.md']['step_ordinal']<state['reads'][name]['step_ordinal'],'READ_ACTION_ORDER_REFUSED')
            probe['separate_state_roadmap_reads']=True
    elif step=='resume':
        need(set(state['reads'])=={'STATE.md','ROADMAP.md'},'CANONICAL_READS_INCOMPLETE')
        for name,read in state['reads'].items():need(digest(u.checked_file(source/state['run_root']/name,65536))==read['sha256'],'CANONICAL_READ_BYTES_CHANGED')
        raw=owner('resume-new-session',['--resume-controller',controller,'--boundary','new-session','--epoch','G0001'])
        state['receipt']=token(raw,'refs/implementaudit/continuity-receipts/'+controller+r'/G0001@[0-9a-f]{40}')
        probe['normal_resume_receipt_sha256']=digest(raw)
    elif step=='verify':
        raw=owner('verify-resume',['--verify-resume-receipt',state['receipt']]);need(raw.decode().strip()==state['receipt'],'VERIFIED_RECEIPT_MISMATCH')
        probe['normal_receipt_verified']=True
    elif step=='require':
        probe['initial_currentness_sha256']=current('initial-require-currentness')
    elif step=='bank':
        current('before-bank-currentness');probe['currentness_before_bank']=True;probe['started']=True
        rc,out,err=command('unchanged-nine-case-bank',[tools['python3'],'-I','-S','-B','-c',CHILD,str(source),json.dumps(list(TESTS),separators=(',',':'))],seconds=BANK_SECONDS)
        write_private(private/'bank.stdout',out);write_private(private/'bank.stderr',err)
        need(not err,'BANK_STDERR_REFUSED');result=validate_bank(u.parse_json(out));probe['result']=result
        need(rc==0 and result['success'] and all(row['outcome']=='PASS' for row in result['rows']),'BANK_NOT_ALL_PASS')
        current('after-bank-currentness');probe['currentness_after_bank']=True
    elif step=='receive':
        result=validate_bank(probe['result']);need(result['success'] and all(row['outcome']=='PASS' for row in result['rows']),'RECEIVING_BANK_NOT_PASS')
        current('receiving-currentness');probe['receiving']={'status':'RECEIVED_AT_DECLARED_SCOPE','authority':'NONE',
           'receipt_transfer_authority':False,'while_same_checkout_current':True,'bank_result_sha256':digest(canonical(result)),
           'eligible_delta':'ONE_MAINTAINED_NINE_CASE_BANK_OBSERVATION_ONLY','G1':False,'C5':False,'full_G2':False,'G3':False,'original_acceptance':False}
        write_private(private/'live-bank-receiving.json',canonical(probe['receiving']))
    else:raise Refusal('UNKNOWN_STEP')

def record_failure(state,operation,exc):
    state['failed']=True
    code=str(exc) if type(exc).__name__=='Refusal' and re.fullmatch('[A-Z0-9_]{1,90}',str(exc)) else ('STEP_WATCHDOG_OR_TERMINATION' if isinstance(exc,Deadline) else 'SAFE_EXCEPTION_RECORDED')
    record={'operation':operation,'code':code,'exception_type':type(exc).__name__ if type(exc).__name__ in ('Refusal','Deadline','OSError','ValueError','KeyError','TypeError','AssertionError') else 'OTHER',
            'errno':exc.errno if isinstance(exc,OSError) and type(exc.errno) is int and 0<=exc.errno<=4096 else None}
    state['docs']['FAILURE.json']['present']=True;state['docs']['FAILURE.json']['failures'].append(record)

def execute(mode,source,output,u):
    context=host_context(output,source,mode);state_path=output/'private/episode.json'
    if mode=='preflight':
        need(not output.exists(),'NO_RETRY_OUTPUT_EXISTS');output.mkdir(mode=0o700)
        (output/'private').mkdir(mode=0o700);(output/'public').mkdir(mode=0o700)
        state=fresh_state(context,source,output);save_state(state_path,state)
    else:
        need(output.resolve(strict=True)==output,'OUTPUT_DIRECTORY_REFUSED')
        state=u.parse_json(u.checked_file(state_path,1024*1024))
        need(state['schema']=='dg16.linux-native-private-episode.v1' and state['context']==context and
             identities(source)==state['source_directory_identity'] and identities(source/'.git')==state['git_directory_identity'] and
             identities(output)==state['output_directory_identity'],'LIVE_CONTEXT_CHANGED')
    docs=state['docs'];enabled=False;commands=docs['HOST.json']['commands'];stage_success=False
    oldcwd=Path.cwd();os.chdir(source)
    def expired(_a,_b):raise Deadline()
    signal.signal(signal.SIGALRM,expired);signal.signal(signal.SIGTERM,expired)
    budget=FINAL_SECONDS if mode=='finalize' else max(1,min(RUN_SECONDS,int(state['deadline_monotonic']-time.monotonic())))
    signal.alarm(budget)
    deadline=time.monotonic()+FINAL_SECONDS if mode=='finalize' else state['deadline_monotonic']
    def command(label,argv,seconds=90):
        # Labels are fixed by this file; no command line, environment, stdout or stderr becomes public.
        return u.capture(mode+'-'+label,argv,commands,deadline,seconds=seconds)
    try:
        need(mode=='finalize' or not state['failed'],'PRIOR_STEP_FAILED')
        if mode!='finalize':need(STEPS[len(state['completed'])]==mode,'STEP_ORDER_REFUSED')
        tools,host=inventory(u)
        prior={k:v for k,v in docs['HOST.json'].items() if k not in ('schema','commands')}
        need('boot_identity_sha256' not in docs['HOST.json'] or prior==host,'HOST_TOOLCHAIN_CHANGED')
        docs['HOST.json'].update(host);enable_subreaper();enabled=True
        manifest=read_manifest(u);check_source_git(command,tools,source,mode in ('preflight','bank','receive','finalize'))
        source_fact=verify_source(source,manifest,u,state['run_root'] is not None)
        if state['runtime'] is not None:need(runtime_snapshot(source,state,u)==state['runtime'],'CLAIMED_RUNTIME_CHANGED')
        if mode=='finalize':
            docs['SOURCE.json']['after']=source_fact
            docs['CLEANUP.json']['source_unchanged']=docs['SOURCE.json']['before']==source_fact
            docs['CLEANUP.json']['runtime_unchanged_after_initialization']=state['runtime'] is not None and runtime_snapshot(source,state,u)==state['runtime']
            need(state['completed']==list(STEPS) and not state['failed'],'EPISODE_INCOMPLETE')
            rc,out,err=command('live-closing-currentness',[tools['bash'],str(source/OWNER),'--require-current-continuity',state['controller']],seconds=20)
            write_private(output/'private/final-currentness.stdout',out);write_private(output/'private/final-currentness.stderr',err)
            need(rc==0 and out.decode().strip()==state['receipt'],'FINAL_CURRENTNESS_REFUSED')
            need(docs['PROBE.json']['receiving']['status']=='RECEIVED_AT_DECLARED_SCOPE','LIVE_RECEIVING_MISSING')
            docs['PROBE.json']['receiving']['closing_currentness_sha256']=digest(out)
            docs['PROBE.json']['receiving']['verified_before_teardown']=True
            stage_success=True
        else:
            operation(mode,state,source,output,tools,u,manifest,command)
            if mode=='bank':check_source_git(command,tools,source,True)
            verify_source(source,manifest,u,state['run_root'] is not None)
            if state['runtime'] is not None:need(runtime_snapshot(source,state,u)==state['runtime'],'CLAIMED_RUNTIME_CHANGED')
            state['completed'].append(mode)
            docs['PROBE.json']['phases'].append({'name':mode,'status':'COMPLETED','ordinal':len(state['completed'])})
            stage_success=True
    except BaseException as exc:
        record_failure(state,mode,exc)
    finally:
        # This process owns only its own descendants; no name-based or process-group cleanup.
        signal.alarm(10)
        try:
            cleanup=u.stop_owned_children() if enabled else {'echild':not u.children(),'pidfd_signals':0,'reaped_statuses':[]}
            need(cleanup['echild'],'STEP_CHILD_CLEANUP_UNCERTAIN')
        except BaseException as exc:
            docs['CLEANUP.json']['all_step_children_reaped']=False;stage_success=False;record_failure(state,mode+'-cleanup',exc)
        docs['RESULT.json']['elapsed_seconds']=time.monotonic()-state['started_monotonic']
        docs['RESULT.json']['completed_steps']=list(state['completed'])
        if mode=='finalize':
            okay=stage_success and not state['failed'] and docs['CLEANUP.json']['all_step_children_reaped'] and docs['CLEANUP.json']['source_unchanged'] and docs['CLEANUP.json']['runtime_unchanged_after_initialization']
            docs['RESULT.json']['status']='QUALIFIED_AT_DECLARED_SCOPE' if okay else 'UNQUALIFIED'
            docs['RESULT.json']['custody_evidence_scope']='HISTORICAL_THIS_LIVE_JOB_ONLY; exported hashes convey no currentness'
            save_state(state_path,state);u.write_public(output/'public',docs)
        else:save_state(state_path,state)
        signal.alarm(0);os.chdir(oldcwd)
    print(json.dumps({'step':mode,'status':'COMPLETED' if stage_success and not state['failed'] else 'UNQUALIFIED'},sort_keys=True),flush=True)
    return 0 if stage_success and not state['failed'] else 1

def main():
    p=argparse.ArgumentParser();p.add_argument('--step',choices=(*STEPS,'finalize'));p.add_argument('--emit-public',action='store_true')
    p.add_argument('--source',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    need(bool(a.step)!=bool(a.emit_public),'MODE_REFUSED');u=load_utility()
    source=Path(a.source).absolute();output=Path(a.output).absolute()
    if a.emit_public:
        host_context(output,source,'emit-public');u.emit_public(output);return 0
    return execute(a.step,source,output,u)

if __name__=='__main__':
    try:raise SystemExit(main())
    except (Refusal,OSError,ValueError,KeyError,TypeError):
        print('DG16_LINUX_NATIVE_EPISODE {"status":"UNQUALIFIED","code":"PRE_ENTRY_OR_RETENTION_REFUSED"}',flush=True)
        raise SystemExit(1)
