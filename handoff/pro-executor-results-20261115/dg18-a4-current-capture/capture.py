#!/usr/bin/env python3
"""Original A4 current Windows capture supplement; no acceptance authority.

Original product and test modules are imported only inside one Root-selected
actual Windows worker after source/host/first-push/exclusive-attempt receiving.
"""
from __future__ import annotations
import argparse
import ast
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import platform
import re
import stat
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import unittest
import zipfile

SOURCE_COMMIT='51416b2f156b341c4a5f09029e2c6ceb5b30b1e7'
SOURCE_TREE='9c3913ceaa95f3f36b0377fe2dba4a302afcba89'
BRANCH='pro/dg18-a4-current-51416-20261120-03'
WORKFLOW_PATH='.github/workflows/dg18-a4-current-capture.yml'
HELPER_PATH='handoff/pro-executor-results-20261115/dg18-a4-current-capture/capture.py'
CONTEXT={'schema':'dg18.original-a4-windows-capture.v1','authority':'NONE',
 'source_commit':SOURCE_COMMIT,'source_tree':SOURCE_TREE,'original_criterion':4,
 'original_denominator':14,'award':None,'automatic_retry':False,
 'native_Stop_OR_C02_N1_evidence':False,'performance_award':False}
ORIGINAL_METHODS=[['windows_custody_test.py', 'WindowsCustody', 'test_all_three_owners_accept_real_directory'], ['windows_custody_test.py', 'WindowsCustody', 'test_retained_binary_file_and_hardlink_refusal'], ['windows_custody_test.py', 'WindowsCustody', 'test_projection_output_is_exclusive_readonly_and_exact'], ['windows_custody_test.py', 'WindowsCustody', 'test_junction_ancestor_is_never_followed'], ['windows_custody_test.py', 'WindowsCustody', 'test_lock_is_exclusive_and_released'], ['windows_custody_test.py', 'WindowsCustody', 'test_windows_process_death_releases_lease_without_deleting_gate'], ['windows_custody_test.py', 'WindowsCustody', 'test_native_memory_observation'], ['windows_custody_test.py', 'WindowsCustody', 'test_retained_directory_name_cannot_be_replaced_before_release'], ['windows_custody_test.py', 'WindowsCustody', 'test_actual_short_directory_alias_is_refused'], ['windows_custody_test.py', 'WindowsCustody', 'test_native_preparation_reuse_enumerates_handles_before_owner_check'], ['windows_custody_test.py', 'WindowsCustody', 'test_snapshot_roundtrip_and_alias_refusal'], ['windows_custody_test.py', 'GitObjectCustody', 'test_exact_blob_reads_and_process_cleanup'], ['windows_custody_test.py', 'GitObjectCustody', 'test_long_authority_paths_use_owned_git_configuration'], ['windows_custody_test.py', 'GitObjectCustody', 'test_wrong_type_and_size_are_refused'], ['windows_custody_test.py', 'GitObjectCustody', 'test_changed_physical_object_cannot_be_served_from_a_value_cache'], ['windows_custody_test.py', 'GitObjectCustody', 'test_packed_delta_base_is_not_served_after_physical_corruption'], ['windows_custody_test.py', 'GitObjectCustody', 'test_live_loose_packed_and_symbolic_ref_discrimination'], ['windows_custody_test.py', 'GitObjectCustody', 'test_dangling_refs_and_noncanonical_packed_grammar_refuse'], ['ref_group_test.py', 'RefGroup', 'test_present_population_has_one_git_verification_and_no_value_cache'], ['ref_group_test.py', 'RefGroup', 'test_packed_loose_override_and_exact_absence'], ['ref_group_test.py', 'RefGroup', 'test_large_population_uses_bounded_fresh_groups'], ['ref_group_test.py', 'RefGroup', 'test_loose_change_after_git_observation_refuses'], ['ref_group_test.py', 'RefGroup', 'test_packed_change_after_git_observation_refuses'], ['ref_group_test.py', 'RefGroup', 'test_symbolic_dangling_and_duplicate_packed_are_not_admitted'], ['ref_group_test.py', 'RefGroup', 'test_partial_duplicate_or_foreign_git_output_refuses'], ['archive_v2_test.py', 'ArchiveQualification', 'test_draft_corruption_and_future_receipt_are_not_finalized'], ['archive_v2_test.py', 'ArchiveQualification', 'test_rebound_archive_metadata_must_match_complete_source_population'], ['claim_transaction_test.py', 'CompleteOwnerDiscriminators', 'test_wrong_candidate_and_component_readback_refuse_without_ref_changes']]
SHORT_ALIAS='windows_custody_test.WindowsCustody.test_actual_short_directory_alias_is_refused'


def digest(raw):
    return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
      'git_blob':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()}


def canonical(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()


def write_new(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())


def write_json(path,value):write_new(path,canonical(value))


def unsafe(info):return stat.S_ISLNK(info.st_mode) or bool(getattr(info,'st_file_attributes',0)&0x400)


def physical(path, *, directory=None):
    path=Path(path)
    if not path.is_absolute() or '..' in path.parts:raise ValueError('absolute unaliased path required')
    for part in (path,*path.parents):
        if unsafe(part.lstat()):raise ValueError('link/reparse path refused: '+str(path))
    info=path.lstat()
    if directory is True and not stat.S_ISDIR(info.st_mode):raise ValueError('physical directory required')
    if directory is False and not stat.S_ISREG(info.st_mode):raise ValueError('physical regular file required')
    return path.resolve(strict=True)


def require_windows():
    if os.name!='nt' or sys.platform!='win32':raise ValueError('actual Windows kernel required before output or original import')
    if sys.version_info[:3]!=(3,12,10):raise ValueError('selected physical Python 3.12.10 required')


def tools_census():
    require_windows()
    python=physical(Path(sys.executable),directory=False)
    expected=Path(r'C:\hostedtoolcache\windows\Python\3.12.10\x64\python.exe')
    if python!=physical(expected,directory=False):raise ValueError('unexpected Python installation')
    git=None
    for name in (r'C:\Program Files\Git\ucrt64\bin\git.exe',r'C:\Program Files\Git\mingw64\bin\git.exe'):
        if Path(name).exists():git=physical(Path(name),directory=False);break
    if git is None:raise ValueError('direct physical Git runtime unavailable')
    paths={'python':python,'git':git,'bash':Path(r'C:\Program Files\Git\usr\bin\bash.exe'),
      'bash_launcher':Path(r'C:\Program Files\Git\bin\bash.exe'),'cmd':Path(r'C:\Windows\System32\cmd.exe')}
    return {name:{'path':str(physical(path,directory=False)),**digest(path.read_bytes())} for name,path in paths.items()}


def environment(tools,fixtures=None):
    git=Path(tools['git']['path']);root=git.parents[2]
    values={'SystemRoot':r'C:\Windows','WINDIR':r'C:\Windows','COMSPEC':tools['cmd']['path'],
      'PATHEXT':'.COM;.EXE;.BAT;.CMD','PATH':os.pathsep.join([str(Path(tools['python']['path']).parent),
      str(git.parent),str(root/'cmd'),str(root/'bin'),str(root/'usr/bin'),r'C:\Windows\System32']),
      'PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1','LC_ALL':'C','LANG':'C',
      'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':os.devnull,'GIT_TERMINAL_PROMPT':'0',
      'GIT_NO_LAZY_FETCH':'1','GIT_ALLOW_PROTOCOL':'','MSYS2_ARG_CONV_EXCL':'*'}
    for key in ('TEMP','TMP'):
        if key in os.environ:values[key]=os.environ[key]
    if fixtures is not None:
        values.update(TEMP=str(fixtures),TMP=str(fixtures),
          R0039_CLAIM_EVIDENCE_DIR=str(fixtures/'claim-evidence'),R0039_CLAIM_RETAIN_ARTIFACTS='1')
    return values


def git(source,*args):
    tools=tools_census()
    return subprocess.run([tools['git']['path'],'-c','protocol.allow=never','-c','core.hooksPath='+os.devnull,
      '-c','core.autocrlf=false','-c','core.fsmonitor=false',*args],cwd=source,env=environment(tools),
      stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=30).stdout


def provider_binding(output):
    require_windows()
    expected={'GITHUB_ACTIONS':'true','RUNNER_ENVIRONMENT':'github-hosted',
      'GITHUB_REPOSITORY':'theislampill/IMPLEMENTAUDIT.md','GITHUB_EVENT_NAME':'push',
      'GITHUB_REF':'refs/heads/'+BRANCH,'GITHUB_RUN_ATTEMPT':'1','RUNNER_OS':'Windows'}
    for key,value in expected.items():
        if os.environ.get(key)!=value:raise ValueError('host/event mismatch: '+key)
    run=os.environ.get('GITHUB_RUN_ID','');commit=os.environ.get('GITHUB_SHA','')
    if not re.fullmatch('[0-9]+',run) or not re.fullmatch('[0-9a-f]{40}',commit):raise ValueError('invalid provider run/commit')
    event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    if (event.get('before')!='0'*40 or event.get('after')!=commit or
        event.get('created') is not True or event.get('deleted') is not False):raise ValueError('not exact branch-creation first push')
    selected=physical(Path(os.environ['RUNNER_TEMP']),directory=True)/('dg18-a4-'+run+'-1')
    if Path(os.path.abspath(output))!=selected:raise ValueError('output is not bound to exact provider run')
    return expected,run,commit,selected


def host_binding(source,output):
    expected,run,commit,selected=provider_binding(output)
    source=physical(source,directory=True)
    packet=physical(Path(__file__).absolute().parents[len(PurePosixPath(HELPER_PATH).parts)-1],directory=True)
    if source.is_relative_to(selected) or selected.is_relative_to(source):raise ValueError('source/output overlap')
    actual=git(packet,'show','-s','--format=%H%n%T%n%P','HEAD').decode().splitlines()
    if actual[0]!=commit or actual[2].split()!=[SOURCE_COMMIT]:raise ValueError('wrong publication sole parent')
    changed=git(packet,'diff-tree','--no-commit-id','--name-only','-r','HEAD').decode().splitlines()
    if sorted(changed)!=sorted([HELPER_PATH,WORKFLOW_PATH]):raise ValueError('unreviewed publication paths')
    if git(packet,'status','--porcelain=v1','--untracked-files=all'):raise ValueError('publication checkout dirty')
    return {**CONTEXT,'run_id':int(run),'attempt':1,'workflow_commit':commit,'workflow_tree':actual[1],
      'workflow_parent':SOURCE_COMMIT,'workflow_changed_paths':changed,'host_predicates':expected,
      'source_path':str(source),'output_path':str(selected),'helper':digest(Path(__file__).read_bytes())}


def source_census(source):
    if git(source,'show','-s','--format=%H%n%T','HEAD').decode().splitlines()!=[SOURCE_COMMIT,SOURCE_TREE]:
        raise ValueError('exact product commit/tree differs')
    status=git(source,'status','--porcelain=v1','--untracked-files=all')
    if status:raise ValueError('product source dirty')
    prefixes=('skills/implementaudit/scripts/','skills/implementaudit/templates/')
    exact={'fixtures/canonical-state-rotation/'+row[0] for row in ORIGINAL_METHODS}|{
      'fixtures/canonical-state-rotation/protected_projection_v2_test.py',
      'fixtures/canonical-state-rotation/v2/source.json','fixtures/controller-initialization/author_checkpoint.py',
      'scripts/r0039-windows-job.py'}
    rows=[]
    for line in git(source,'ls-tree','-r','HEAD').decode().splitlines():
        meta,path=line.split('\t',1)
        if path not in exact and not path.startswith(prefixes):continue
        mode,kind,oid=meta.split();p=physical(source/path,directory=False);raw=p.read_bytes()
        if kind!='blob' or mode not in {'100644','100755'} or digest(raw)['git_blob']!=oid:
            raise ValueError('immutable source member differs: '+path)
        rows.append({'path':path,'mode':mode,**digest(raw)})
    if not exact.issubset({x['path'] for x in rows}):raise ValueError('source population incomplete')
    selected={x['path'] for x in rows if x['path'].startswith(prefixes)}
    actual={p.relative_to(source).as_posix() for prefix in prefixes for p in (source/prefix).rglob('*') if p.is_file() or p.is_symlink()}
    if selected!=actual:raise ValueError('physical runtime population differs')
    return {**CONTEXT,'source_members':rows,'source_member_count':len(rows),'git_status':status.decode(),
      'tools':tools_census(),'python':sys.version,'platform':platform.platform(),'win32_ver':list(platform.win32_ver())}


def expected_ids():return ['.'.join((file[:-3],cls,method)) for file,cls,method in ORIGINAL_METHODS]


def preflight(source,output):
    binding=host_binding(source,output)
    output.mkdir(mode=0o700,exist_ok=False)
    write_json(output/'PREFLIGHT_INTENT.json',binding)
    census=source_census(source);write_json(output/'SOURCE_BEFORE.json',census)
    write_json(output/'PREFLIGHT.json',{**binding,'status':'PROSPECTIVE_WINDOWS_SOURCE_RECEIVED_NO_EPISODE_YET',
      'source_before':digest((output/'SOURCE_BEFORE.json').read_bytes()),'original_methods':ORIGINAL_METHODS,
      'expected_tests':expected_ids(),'optional_exact_short_alias_skip':SHORT_ALIAS,
      'limitations':['No short-alias credit if actual volume supplies no distinct alias.','Independent complete A4 conjunction still required.']})
    print('Exact A4 Windows source and first-push binding received; no original method executed.')


class Recorder:
    """Observe, delegate unchanged and retain exact bytes; never synthesize success."""
    def __init__(self,output,fixtures):
        self.output=output;self.fixtures=fixtures;self.case=None
        # Full records are already retained on disk; only their numbering stays in memory.
        self.command_count=0;self.event_count=0;self.snapshot_count=0;self.processes=[];self.lock=threading.RLock()
        for name in ('blobs','snapshots','events','commands','processes'):(output/name).mkdir(exist_ok=False)
    def content(self,raw):
        ident=digest(raw);path=self.output/'blobs'/ident['sha256']
        with self.lock:
            if path.exists():
                if path.read_bytes()!=raw:raise ValueError('content-addressed byte collision')
            else:write_new(path,raw)
        return {'path':path.relative_to(self.output).as_posix(),**ident}
    def value(self,value):
        if type(value) in (str,int,float,bool) or value is None:return value
        if isinstance(value,bytes):return {'type':'bytes','content':self.content(value)}
        if isinstance(value,os.PathLike):return {'type':'path','value':str(value)}
        if isinstance(value,(tuple,list)):return [self.value(x) for x in value]
        if isinstance(value,dict):return {str(k):self.value(v) for k,v in value.items()}
        if isinstance(value,type):return {'type':'class','name':value.__module__+'.'+value.__qualname__}
        return {'type':type(value).__module__+'.'+type(value).__qualname__}
    def event(self,kind,**fields):
        with self.lock:
            row={'index':self.event_count+1,'kind':kind,'case':self.case,'observed_ns':time.time_ns(),**fields}
            self.event_count+=1;write_json(self.output/'events'/f"{row['index']:06d}.json",row)
            return row
    def snapshot(self,label):
        rows=[];errors=[]
        def walk(directory):
            try:entries=sorted(os.scandir(directory),key=lambda x:x.name)
            except OSError as exc:
                errors.append({'path':str(directory.relative_to(self.fixtures)),'error':type(exc).__name__,'detail':str(exc)});return
            for entry in entries:
                path=Path(entry.path);relative=path.relative_to(self.fixtures).as_posix()
                try:
                    info=path.lstat()  # DirEntry.stat() omits Windows identity fields.
                    row={'path':relative,'mode':info.st_mode,'size':info.st_size,'device':info.st_dev,'inode':info.st_ino,
                      'nlink':info.st_nlink,'mtime_ns':info.st_mtime_ns,'file_attributes':getattr(info,'st_file_attributes',None)}
                    if unsafe(info):
                        row['kind']='LINK_OR_REPARSE_NOT_FOLLOWED'
                        try:row['link_target']=os.readlink(path)
                        except OSError as exc:row['link_read_error']=str(exc)
                    elif stat.S_ISDIR(info.st_mode):row['kind']='DIRECTORY'
                    elif stat.S_ISREG(info.st_mode):
                        row['kind']='REGULAR'
                        if info.st_size>32*1024*1024:raise ValueError('observer file bound exceeded')
                        physical(path.parent,directory=True)
                        descriptor=os.open(path,os.O_RDONLY|getattr(os,'O_BINARY',0)|getattr(os,'O_NOFOLLOW',0))
                        with os.fdopen(descriptor,'rb') as stream:
                            held=os.fstat(stream.fileno());raw=stream.read();after=os.fstat(stream.fileno())
                        key=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns)
                        if key(info)!=key(held) or key(held)!=key(after) or key(after)!=key(path.lstat()) or len(raw)!=info.st_size:
                            raise ValueError('observed file changed during read')
                        row['content']=self.content(raw)
                    else:row['kind']='OTHER_NOT_READ'
                    rows.append(row)
                    if row['kind']=='DIRECTORY':walk(path)
                except OSError as exc:
                    rows.append({'path':relative,'kind':'OBSERVATION_UNAVAILABLE','error':type(exc).__name__,'detail':str(exc)})
                if len(rows)>20000:raise ValueError('observer member bound exceeded')
        walk(self.fixtures)
        with self.lock:
            result={'index':self.snapshot_count+1,'case':self.case,'label':label,'observed_ns':time.time_ns(),
              'root':str(self.fixtures),'members':rows,'enumeration_errors':errors,
              'scope':'Actual current fixture metadata and readable regular bytes; unavailable locked files and reparse entries remain explicit.'}
            self.snapshot_count+=1
            write_json(self.output/'snapshots'/f"{result['index']:05d}.json",result)
        return result
    def record_run(self,original):
        def recorded(*args,**kwargs):
            with self.lock:
                index=self.command_count+1;folder=self.output/'commands'/f'{index:05d}';folder.mkdir()
                row={'index':index,'case':self.case,'args':self.value(args),
                  'kwargs':{k:self.value(v) for k,v in kwargs.items() if k!='env'},'environment_values_recorded':False,
                  'started_ns':time.time_ns()};self.command_count+=1
            argv=args[0] if args else kwargs.get('args',[])
            observe=bool(self.case and self.case.endswith('test_wrong_candidate_and_component_readback_refuse_without_ref_changes') and
              isinstance(argv,(list,tuple)) and any(str(a) in {'--require-current-continuity','--read-current-state','--read-canonical-state'} for a in argv))
            if observe:row['before_snapshot']=self.snapshot('before-owner-command')['index']
            data=kwargs.get('input')
            if isinstance(data,(bytes,str)):
                raw=data if isinstance(data,bytes) else data.encode();write_new(folder/'stdin.bin',raw);row['stdin']=digest(raw)
            write_json(folder/'INTENT.json',row)
            try:result=original(*args,**kwargs)
            except BaseException as exc:
                row.update(exception_type=type(exc).__name__,exception_text=str(exc),ended_ns=time.time_ns())
                for name in ('stdout','stderr'):
                    raw=getattr(exc,name,None)
                    if isinstance(raw,str):raw=raw.encode()
                    if isinstance(raw,bytes):write_new(folder/(name+'.partial.bin'),raw);row[name+'_partial']=digest(raw)
                if observe:row['after_snapshot']=self.snapshot('after-exception-owner-command')['index']
                write_json(folder/'EXCEPTION.json',row);raise
            for name in ('stdout','stderr'):
                raw=getattr(result,name,None)
                if isinstance(raw,str):raw=raw.encode()
                if isinstance(raw,bytes):write_new(folder/(name+'.bin'),raw);row[name]=digest(raw)
                else:row[name]=None
            row.update(exit_code=result.returncode,ended_ns=time.time_ns())
            if observe:row['after_snapshot']=self.snapshot('after-owner-command')['index']
            write_json(folder/'RETURN.json',row);return result
        return recorded
    @contextlib.contextmanager
    def observe(self):
        originals=[];rec=self
        def patch(owner,name,value):originals.append((owner,name,getattr(owner,name)));setattr(owner,name,value)
        old_popen=subprocess.Popen
        def popen(*args,**kwargs):
            with rec.lock:
                index=len(rec.processes)+1
                row={'index':index,'case':rec.case,'args':rec.value(args),
                  'kwargs':{k:rec.value(v) for k,v in kwargs.items() if k!='env'},'environment_values_recorded':False,
                  'started_ns':time.time_ns()};item={'record':row,'process':None};rec.processes.append(item)
            write_json(rec.output/'processes'/f'{index:05d}.intent.json',row)
            try:p=old_popen(*args,**kwargs)
            except BaseException as exc:
                row.update(exception_type=type(exc).__name__,exception_text=str(exc));write_json(rec.output/'processes'/f'{index:05d}.exception.json',row);raise
            item['process']=p;row.update(pid=p.pid);write_json(rec.output/'processes'/f'{index:05d}.started.json',row);return p
        patch(subprocess,'Popen',popen);patch(subprocess,'run',self.record_run(subprocess.run))
        old_enter=unittest.case._AssertRaisesContext.__enter__;old_exit=unittest.case._AssertRaisesContext.__exit__
        def entering(ctx):
            ctx._a4_before=rec.snapshot('before-expected-exception')['index']
            rec.event('EXPECTED_EXCEPTION_ENTER',expected=rec.value(ctx.expected),before_snapshot=ctx._a4_before)
            return old_enter(ctx)
        def exiting(ctx,kind,value,tb):
            row={'expected':rec.value(ctx.expected),'before_snapshot':getattr(ctx,'_a4_before',None),
              'exception':None if kind is None else {'type':kind.__name__,'module':kind.__module__,'text':str(value)}}
            try:
                returned=old_exit(ctx,kind,value,tb);row['delegated_return']=returned;return returned
            except BaseException as exc:
                row.update(delegated_exception={'type':type(exc).__name__,'text':str(exc)});raise
            finally:
                row['after_snapshot']=rec.snapshot('after-expected-exception')['index'];rec.event('EXPECTED_EXCEPTION_EXIT',**row)
        patch(unittest.case._AssertRaisesContext,'__enter__',entering);patch(unittest.case._AssertRaisesContext,'__exit__',exiting)
        for name in ('assertEqual','assertNotEqual','assertTrue','assertFalse','assertIn','assertNotIn','assertIsNone','assertIsNotNone','assertGreater','assertLess'):
            original=getattr(unittest.TestCase,name)
            def assertion(test,*args,_original=original,_name=name,**kwargs):
                row={'name':_name,'arguments':rec.value(args),'kwargs':rec.value(kwargs),'outcome':'RETURNED'}
                try:return _original(test,*args,**kwargs)
                except BaseException as exc:row.update(outcome='RAISED',exception={'type':type(exc).__name__,'text':str(exc)});raise
                finally:rec.event('ASSERTION',**row)
            patch(unittest.TestCase,name,assertion)
        for name in ('_callSetUp','_callTestMethod','_callTearDown','doCleanups'):
            original=getattr(unittest.TestCase,name)
            def lifecycle(test,*args,_original=original,_name=name,**kwargs):
                rec.case=test.id();rec.snapshot('before-'+_name)
                try:return _original(test,*args,**kwargs)
                finally:rec.snapshot('after-'+_name)
            patch(unittest.TestCase,name,lifecycle)
        try:yield self
        finally:
            for owner,name,original in reversed(originals):setattr(owner,name,original)
    def process_terminal(self):
        rows=[]
        for item in self.processes:
            row=dict(item['record']);p=item['process']
            if p is not None:row['terminal_returncode']=p.poll();row['still_running']=row['terminal_returncode'] is None
            else:row['not_created']=True
            rows.append(row)
        write_json(self.output/'PROCESS_TERMINAL.json',{'processes':rows,'survivors':[x for x in rows if x.get('still_running')]})
        return rows


def receive_outcomes(rows,expected,optional):
    if len(rows)!=len(expected) or sorted(x['id'] for x in rows)!=sorted(expected) or len(set(expected))!=len(expected):
        raise ValueError('original method population incomplete or duplicated')
    alias='OBSERVED_SUCCESS' if optional is not None else 'NOT_SELECTED'
    for row in rows:
        if row['outcome']=='SUCCESS':continue
        if row['id']==optional and row['outcome']=='SKIP' and row.get('reason')=='this volume did not provide a distinct 8.3 alias':
            alias='UNAVAILABLE_ON_ACTUAL_VOLUME_NO_ATTACK_CREDIT';continue
        raise ValueError('original method did not pass: '+row['id']+': '+row['outcome'])
    return {'selected':len(expected),'successful':sum(x['outcome']=='SUCCESS' for x in rows),
      'short_alias_observation':alias,'award':None,'scope':'Recorded selected controls; complete original A4 adjudication remains independent.'}


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module


def outcomes_document(result,rows):
    return {'rows':rows,'tests_run':result.testsRun,'success':result.wasSuccessful(),
      'failures':[(test.id(),detail) for test,detail in result.failures],
      'errors':[(test.id(),detail) for test,detail in result.errors],
      'skipped':[(test.id(),why) for test,why in result.skipped]}


def worker(source,output):
    require_windows();physical(output,directory=True)
    plan=json.loads((output/'EXECUTE_INTENT.json').read_text())
    if plan['source_path']!=str(source) or plan['helper']!=digest(Path(__file__).read_bytes()):raise ValueError('worker plan/source mismatch')
    before=source_census(source)
    if before!=json.loads((output/'SOURCE_BEFORE.json').read_text()):raise ValueError('worker source/tools changed')
    write_json(output/'WORKER_ATTEMPT.json',{**CONTEXT,'pid':os.getpid(),'parent_pid':os.getppid(),'plan':digest((output/'EXECUTE_INTENT.json').read_bytes()),'started_ns':time.time_ns()})
    fixtures=physical(output/'fixtures',directory=True);tempfile.tempdir=str(fixtures)
    captured=output/'capture';captured.mkdir(mode=0o700,exist_ok=False);rec=Recorder(captured,fixtures)
    rows=[];error=None;result=None
    class Result(unittest.TextTestResult):
        def startTest(self,test):rec.case=test.id();super().startTest(test)
        def addSuccess(self,test):rows.append({'id':test.id(),'outcome':'SUCCESS'});super().addSuccess(test)
        def addFailure(self,test,err):rows.append({'id':test.id(),'outcome':'FAILURE','detail':self._exc_info_to_string(err,test)});super().addFailure(test,err)
        def addError(self,test,err):rows.append({'id':test.id(),'outcome':'ERROR','detail':self._exc_info_to_string(err,test)});super().addError(test,err)
        def addSkip(self,test,reason):rows.append({'id':test.id(),'outcome':'SKIP','reason':reason});super().addSkip(test,reason)
        def addSubTest(self,test,subtest,err):
            rec.event('SUBTEST',id=subtest.id(),error=None if err is None else self._exc_info_to_string(err,test))
            super().addSubTest(test,subtest,err)
    try:
        sys.path.insert(0,str(source/'fixtures/canonical-state-rotation'))
        modules={file:load_module(file[:-3],source/'fixtures/canonical-state-rotation'/file) for file in dict.fromkeys(x[0] for x in ORIGINAL_METHODS)}
        suite=unittest.TestSuite(getattr(modules[file],cls)(method) for file,cls,method in ORIGINAL_METHODS)
        with (captured/'UNITTEST.log').open('x',encoding='utf-8',newline='\n') as stream:
            with rec.observe():result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
        write_json(captured/'OUTCOMES.json',outcomes_document(result,rows))
        if not result.wasSuccessful():raise ValueError('original control failures/subtest errors retained')
        summary=receive_outcomes(rows,expected_ids(),SHORT_ALIAS)
        write_json(captured/'CONTROL_RECEIVING.json',summary)
    except BaseException as exc:
        error=exc;write_json(captured/'WORKER_ERROR.json',{'type':type(exc).__name__,'text':str(exc),'traceback':traceback.format_exc(),'recorded_outcomes':rows})
    finally:
        terminal=rec.process_terminal();rec.snapshot('terminal-after-original-cleanup')
        unexpected=[str(p.relative_to(fixtures)) for p in fixtures.iterdir() if p.name!='claim-evidence']
        claim=fixtures/'claim-evidence'
        if claim.exists():unexpected.extend(str(p.relative_to(fixtures)) for p in claim.iterdir() if p.is_dir() or not p.name.endswith(('.json','.fixture.zip')))
        write_json(captured/'CLEANUP.json',{'unexpected_remaining_fixture_paths':unexpected,'original_cleanup_delegated_unchanged':True})
        after=source_census(source);write_json(output/'SOURCE_AFTER_WORKER.json',after)
        write_json(captured/'INDEX.json',{'commands':rec.command_count,'processes':len(rec.processes),'events':rec.event_count,'snapshots':rec.snapshot_count,
          'outcomes':rows,'direct_Popen_protocol_streams':'Not universally intercepted. Actual assertion values, original evidence and snapshots are retained; subprocess.run streams are complete.',
          'source_unchanged':after==before})
        if any(x.get('still_running') for x in terminal) or unexpected or after!=before:
            error=error or ValueError('terminal source/cleanup/survivorship conjunction failed')
    if error is not None:raise error
    print('Selected current Windows original controls completed; independent A4 receiving remains required.')
    return 0


def qualify_job(row,command,tools):
    predicates={'status':'COMPLETE_UNADMITTED','exit_code':0,'platform':'win32','started_suspended':True,
      'assigned_before_resume':True,'root_job_membership_confirmed':True,'completion_port_associated_before_assignment':True,
      'complete_memory_scope_valid':True,'cleanup_complete':True,'terminal_active_processes':0,
      'terminal_breakaway_allowed':False,'initial_job_flags':0x2000,'terminal_job_flags':0x2000}
    for key,value in predicates.items():
        if type(row.get(key)) is not type(value) or row[key]!=value:raise ValueError('Windows Job conjunction absent: '+key)
    if row.get('command')!=command:raise ValueError('observed worker command differs')
    total=row.get('kernel_total_processes')
    if type(total)is not int or total<1 or row.get('creation_event_count')!=total or row.get('exit_event_count')!=total:
        raise ValueError('Windows process census unreconciled')
    observed=row.get('observed_processes')
    if type(observed) is not list or not observed:raise ValueError('actual executable observations absent')
    pids={x['pid'] for x in row.get('process_events',[]) if x.get('event')=='NEW_PROCESS'}
    if any(x.get('in_job') is not True or type(x.get('pid')) is not int or x['pid'] not in pids for x in observed):
        raise ValueError('observed process outside containing Job or absent from actual creation census')
    spelling=lambda value:str(PureWindowsPath(value)).casefold()
    for name in ('python','git','bash','cmd'):
        expected=tools[name]
        if not any(spelling(x.get('image',''))==spelling(expected['path']) and
          x.get('image_sha256')==expected['sha256'] and (name!='python' or x['pid']==row.get('root_pid')) for x in observed):
            raise ValueError('selected executable identity not observed in Job: '+name)
    if spelling(command[0])!=spelling(tools['python']['path']):raise ValueError('Job root command differs from selected physical Python')
    return {'scope':'Actual Windows Job containment and terminal cleanup; diagnostic measurement only. No new W-FULL performance award.',
      'kernel_total_processes':total,'award':None}


def execute(source,output):
    binding=host_binding(source,output);physical(output,directory=True)
    preflight=json.loads((output/'PREFLIGHT.json').read_text());before=source_census(source)
    if any(preflight.get(key)!=value for key,value in binding.items()):raise ValueError('preflight binding differs')
    if preflight['source_before']!=digest((output/'SOURCE_BEFORE.json').read_bytes()) or before!=json.loads((output/'SOURCE_BEFORE.json').read_text()):
        raise ValueError('preflight source/tools changed')
    fixtures=output/'fixtures';fixtures.mkdir(mode=0o700,exist_ok=False)
    command=[before['tools']['python']['path'],'-I','-B',str(Path(__file__).absolute()),'--step','worker','--source',str(source),'--output',str(output)]
    write_json(output/'EXECUTE_INTENT.json',{**binding,'started_ns':time.time_ns(),'command':command,'source_before':digest((output/'SOURCE_BEFORE.json').read_bytes()),'one_worker_only':True})
    try:
        measured=load_module('a4_actual_current_job',source/'scripts/r0039-windows-job.py')
        result=measured.measure(command,source,environment(before['tools'],fixtures),output/'windows-job',diagnostic_timeout_seconds=600)
        measured.reconcile_process_events(result.get('process_events'),result.get('kernel_total_processes'),result.get('root_pid'))
        received=qualify_job(result,command,before['tools'])
        after=source_census(source);write_json(output/'SOURCE_AFTER.json',after)
        if after!=before:raise ValueError('source/tools changed after contained operation')
        if not (output/'capture/CONTROL_RECEIVING.json').is_file():raise ValueError('worker control receiving absent')
        write_json(output/'RESULT.json',{**binding,'status':'RECORDED_WINDOWS_CONTROLS_READY_FOR_INDEPENDENT_A4_RECEIVING',
          'job':received,'control_receiving':json.loads((output/'capture/CONTROL_RECEIVING.json').read_text()),
          'source_before':digest((output/'SOURCE_BEFORE.json').read_bytes()),'source_after':digest((output/'SOURCE_AFTER.json').read_bytes())})
        return 0
    except BaseException as exc:
        write_json(output/'EXECUTION_ERROR.json',{**CONTEXT,'type':type(exc).__name__,'text':str(exc),'traceback':traceback.format_exc(),'effects':'ACTUAL_RETAINED_EVIDENCE_ONLY_NO_RETRY'})
        raise


def seal_retained_output(output):
    physical(output,directory=True)
    with (output/'FINALIZE_INTENT.json').open('xb') as stream:
        stream.write(canonical({**CONTEXT,'started_ns':time.time_ns(),'no_original_replay':True}))
    rows=[];not_followed=[];errors=[]
    def walk(directory):
        try:entries=sorted(os.scandir(directory),key=lambda x:x.name)
        except OSError as exc:
            errors.append({'path':directory.relative_to(output).as_posix(),'error':type(exc).__name__,'detail':str(exc)});return
        for entry in entries:
            path=Path(entry.path);rel=path.relative_to(output).as_posix()
            if rel=='FINALIZE_INTENT.json':continue
            try:
                info=entry.stat(follow_symlinks=False)
                if unsafe(info):
                    not_followed.append({'path':rel,'mode':info.st_mode,'file_attributes':getattr(info,'st_file_attributes',None),
                      'reason':'LINK_OR_REPARSE_NOT_FOLLOWED'});continue
                if stat.S_ISDIR(info.st_mode):walk(path);continue
                if not stat.S_ISREG(info.st_mode):
                    not_followed.append({'path':rel,'mode':info.st_mode,'reason':'NONREGULAR_NOT_READ'});continue
                physical(path,directory=False);raw=path.read_bytes()
                rows.append({'path':rel,**digest(raw)})
            except OSError as exc:errors.append({'path':rel,'error':type(exc).__name__,'detail':str(exc)})
    walk(output)
    intent=output/'FINALIZE_INTENT.json';rows.append({'path':intent.name,**digest(intent.read_bytes())})
    rows.sort(key=lambda x:x['path'])
    write_json(output/'FINAL_MANIFEST.json',{**CONTEXT,'members':rows,'member_count':len(rows),'member_bytes':sum(x['bytes'] for x in rows),
      'not_followed_entries':not_followed,'observation_errors':errors,
      'selection':'Complete accessible regular-file output before final manifest, including any unfinished fixture. Links and unavailable entries are enumerated, never followed or invented. Original case snapshots use one exact content-addressed store.'})
    archive=output/'RETAINED_EVIDENCE.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as zipper:
        for row in rows:
            path=physical(output/row['path'],directory=False);raw=path.read_bytes()
            if digest(raw)!={key:row[key] for key in ('bytes','sha256','git_blob')}:raise ValueError('retained evidence changed during sealing')
            zipper.writestr(row['path'],raw)
        zipper.writestr('FINAL_MANIFEST.json',(output/'FINAL_MANIFEST.json').read_bytes())
    with zipfile.ZipFile(archive) as zipper:
        if zipper.testzip() is not None or len(zipper.namelist())!=len(set(zipper.namelist())):raise ValueError('sealed ZIP identity/CRC failure')
    write_json(output/'FINAL_ZIP_RECEIPT.json',{**CONTEXT,'archive':digest(archive.read_bytes()),'archive_name':archive.name,
      'members_including_manifest':len(rows)+1,'manifest':digest((output/'FINAL_MANIFEST.json').read_bytes()),
      'not_followed_count':len(not_followed),'observation_error_count':len(errors)})


def finalize(source,output):
    provider_binding(output)
    if not output.exists():
        output.mkdir(mode=0o700,exist_ok=False);write_json(output/'NO_PREFLIGHT_OUTPUT.json',{**CONTEXT,'original_execution_established':False})
    seal_retained_output(output)
    print('Complete existing Windows capture output sealed without replay.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--step',choices=['preflight','execute','worker','finalize'],required=True)
    parser.add_argument('--source',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    source=Path(os.path.abspath(args.source));output=Path(os.path.abspath(args.output))
    return globals()[args.step](source,output) or 0

if __name__=='__main__':raise SystemExit(main())
