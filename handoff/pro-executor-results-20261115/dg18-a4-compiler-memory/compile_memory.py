#!/usr/bin/env python3
"""Separate compile-only native diagnostic. No original method or award."""
from __future__ import annotations
import argparse
import builtins
import contextlib
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import subprocess
import sys
import time
import zipfile

SOURCE_COMMIT='51416b2f156b341c4a5f09029e2c6ceb5b30b1e7'
SOURCE_TREE='9c3913ceaa95f3f36b0377fe2dba4a302afcba89'
BRANCH='pro/dg18-a4-compiler-memory-51416-20261121-01'
WORKFLOW_PATH='.github/workflows/dg18-a4-compiler-memory.yml'
HELPER_PATH='handoff/pro-executor-results-20261115/dg18-a4-compiler-memory/compile_memory.py'
ADAPTER_PATH='handoff/pro-executor-results-20261115/dg18-a4-compiler-memory/compile_adapter.py'
ADAPTER_PIN={'bytes':6595,'sha256':'4baffb9fdadde5333a1bf535593d4aa794936578be297b1ce723e1f0bd1683b2'}
SOURCE_PINS={
 'skills/implementaudit/scripts/claim-run-rotation.py':{'bytes':291693,'sha256':'9eebc5d5e57b47b0e4b4a2a846de1c0b55407713e14008a6de4d01e7a8c5e19e'},
 'skills/implementaudit/scripts/rotate-canonical-state.py':{'bytes':129959,'sha256':'86a9a2a8501aea60f1e333c421e25b19d4e9758a121296fedfa881185de0a5fd'},
 'scripts/r0039-windows-job.py':{'bytes':25678,'sha256':'0191eb110977e8aad6c615f7130052c08a38b83297c65748768608a2959ecd8b'},
 'fixtures/canonical-state-rotation/windows_custody_test.py':{'bytes':17370,'sha256':'9dd670dc98f55a7527d8202aab306743a6c8b2f15396d83b0c409211e2918f4b'}}
MODES=('native','r2','audit')
REFERENCE_LIMIT=67108864
CONTEXT={'schema':'dg18.a4.separate-compiler-memory.v1','authority':'NONE','award':None,
 'original_method_executions':0,'product_body_executions':0,'automatic_retry':False,
 'original_guard_bytes':REFERENCE_LIMIT,'original_guard_changed':False,'original_guard_invoked':False,
 'original_28_method_order_changed':False,'original_28_methods_invoked':False,
 'baseline_subtracted_bytes':0,'historical_R3_peak':'UNKNOWN','A4_07':'UNKNOWN_NO_REPLAY',
 'frozen_R01_R09_contract_available':False,'source_commit':SOURCE_COMMIT,'source_tree':SOURCE_TREE}

def digest(raw):return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def canonical(row):return (json.dumps(row,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def write_json(path,row):
    raw=canonical(row)
    with path.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
def unsafe(info):return stat.S_ISLNK(info.st_mode) or bool(getattr(info,'st_file_attributes',0)&0x400)
def physical(path,directory=False):
    path=Path(path)
    if not path.is_absolute() or '..' in path.parts:raise ValueError('absolute unaliased path required')
    for item in (path,*path.parents):
        if unsafe(item.lstat()):raise ValueError('link or reparse path refused')
    info=path.lstat()
    if directory:
        if not stat.S_ISDIR(info.st_mode):raise ValueError('physical directory required')
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink!=1:raise ValueError('single-link regular file required')
    return path
def read_pinned(path,pin):
    path=physical(path);before=path.lstat()
    flags=os.O_RDONLY|getattr(os,'O_BINARY',0)|getattr(os,'O_NOFOLLOW',0)
    with os.fdopen(os.open(path,flags),'rb') as stream:
        held=os.fstat(stream.fileno());raw=stream.read(pin['bytes']+1);after=os.fstat(stream.fileno())
    identity=lambda i:(i.st_dev,i.st_ino,i.st_size,i.st_mtime_ns,i.st_nlink)
    if (identity(before)!=identity(held) or identity(held)!=identity(after) or
        identity(after)!=identity(path.lstat()) or digest(raw)!=pin):raise ValueError('physical pinned input changed')
    return raw
def require_windows():
    if os.name!='nt' or sys.platform!='win32':raise ValueError('actual Windows required before output or execution')
    if sys.version_info[:3]!=(3,12,10) or sys.implementation.name!='cpython' or sys.flags.optimize!=0:
        raise ValueError('native CPython 3.12.10 without optimization required')
    if ctypes.sizeof(ctypes.c_void_p)!=8:raise ValueError('native x64 required')
def load_adapter():
    path=Path(__file__).absolute().with_name('compile_adapter.py');raw=read_pinned(path,ADAPTER_PIN)
    spec=importlib.util.spec_from_file_location('exact_r2_compiler',path)
    module=importlib.util.module_from_spec(spec)
    exec(compile(raw,str(path),'exec',dont_inherit=True),module.__dict__)
    read_pinned(path,ADAPTER_PIN)
    return module.ExactSourceCompiler

class NativeMemory:
    def __init__(self,output):
        require_windows()
        class Counters(ctypes.Structure):
            _fields_=[('cb',ctypes.c_uint32),('PageFaultCount',ctypes.c_uint32),
             ('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),
             ('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),
             ('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),
             ('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
        if ctypes.sizeof(Counters)!=72:raise ValueError('PROCESS_MEMORY_COUNTERS72 required')
        kernel=ctypes.WinDLL('kernel32',use_last_error=True);psapi=ctypes.WinDLL('psapi',use_last_error=True)
        kernel.GetCurrentProcess.argtypes=[];kernel.GetCurrentProcess.restype=ctypes.c_void_p
        self.handle=kernel.GetCurrentProcess();self.Counters=Counters
        self.get=psapi.GetProcessMemoryInfo
        self.get.argtypes=[ctypes.c_void_p,ctypes.POINTER(Counters),ctypes.c_uint32];self.get.restype=ctypes.c_int32
        self.output=output;output.mkdir(exist_ok=False);self.pid=os.getpid();self.sequence=0;self.last_peak=0
    def sample(self,label,request=None):
        if self.sequence>=10 or os.getpid()!=self.pid:raise ValueError('native record bound or process identity differs')
        native=self.Counters();native.cb=ctypes.sizeof(native)
        if not self.get(self.handle,ctypes.byref(native),native.cb):raise OSError(ctypes.get_last_error(),'GetProcessMemoryInfo failed')
        peak=int(native.PeakWorkingSetSize);current=int(native.WorkingSetSize)
        if peak<self.last_peak or not 0<current<=peak:raise ValueError('invalid native current/lifetime-peak population')
        self.last_peak=peak;self.sequence+=1
        row={'schema':'dg18.a4.compiler-boundary-memory.v1','pid':self.pid,'sequence':self.sequence,
         'observed_ns':time.time_ns(),'label':label,'request':request,'working_set_bytes':current,
         'lifetime_peak_working_set_bytes':peak,'pagefile_bytes':int(native.PagefileUsage),
         'lifetime_peak_pagefile_bytes':int(native.PeakPagefileUsage),'page_faults':int(native.PageFaultCount),
         'unchanged_reference_limit_bytes':REFERENCE_LIMIT,'scope':'new controlled worker; all observer overhead included',
         'guard_invoked':False,'award':None}
        if len(canonical(row))>2048:raise ValueError('native record byte bound exceeded')
        write_json(self.output/f'{self.sequence:02d}.json',row)

def compile_workload(mode,inputs,observer):
    if mode not in ('native','r2') or not 1<=len(inputs)<=2:raise ValueError('bounded compile mode/population required')
    bodies={name:read_pinned(path,pin) for name,(path,pin) in inputs.items()}
    adapter=load_adapter()(bodies);native=builtins.compile;results=[];request=0;requests=[]
    with adapter if mode=='r2' else contextlib.nullcontext():
        for name,(path,pin) in inputs.items():
            first=None
            for occurrence in (1,2):
                raw=read_pinned(path,pin);request+=1
                observer.sample('before-compile',request)
                code=compile(raw,str(path),'exec',dont_inherit=True,optimize=0)
                results.append(code)
                observer.sample('after-compile',request)
                if code.co_filename!=str(path):raise ValueError('compiler changed exact filename')
                if first is None:first=code
                elif code!=first or ((code is first)!=(mode=='r2')):raise ValueError('exact code/reuse equivalence differs')
                requests.append({'request':request,'source':name,'occurrence':occurrence,'source_pin':pin,
                    'filename_sha256':hashlib.sha256(str(path).encode()).hexdigest()})
    if builtins.compile is not native or adapter.installed:raise ValueError('native compile restoration failed')
    if mode=='r2' and (adapter.requests!=request or adapter.hits!=len(inputs) or adapter.native_compilations!=len(inputs)):
        raise ValueError('exact R2 cache request population differs')
    return results,{'mode':mode,'requests':request,'retained_results':len(results),
     'request_population':requests,'product_body_executions':0,'code_equivalence':True,
     'compile_restored':True,'adapter':adapter.summary()}

def audit_controls():
    Adapter=load_adapter();native=builtins.compile;audit=sys.audit;body=b'CONTROL_ONLY_VALUE = []\n'
    def replacement(*args):return None
    replacement.__name__='audit';replacement.__module__='sys';replacement.__self__=sys
    construction=0
    for value in (replacement,None,sys.getsizeof):
        sys.audit=value
        try:
            try:Adapter({'control.py':body})
            except RuntimeError:construction+=1
            else:raise ValueError('changed audit callable admitted')
        finally:sys.audit=audit
    adapter=Adapter({'control.py':body});sys.audit=replacement;installation=0
    try:
        try:adapter.__enter__()
        except RuntimeError:installation=1
        else:
            adapter.__exit__(None,None,None);raise ValueError('changed installation boundary admitted')
    finally:sys.audit=audit
    state={'active':True,'refuse':False,'events':0};results={}
    class Refusal(RuntimeError):pass
    def hook(event,args):
        if state['active'] and event=='compile' and args[1] in ('A4_DIAGNOSTIC_HIT.py','A4_DIAGNOSTIC_MISS.py'):
            state['events']+=1
            if state['refuse']:raise Refusal('controlled native hook refusal')
    adapter=Adapter({'control.py':body})
    try:
        with adapter:
            first=compile(body,'A4_DIAGNOSTIC_HIT.py','exec',dont_inherit=True)
            sys.addaudithook(hook);sys.audit=replacement
            second=compile(body,'A4_DIAGNOSTIC_HIT.py','exec',dont_inherit=True)
            if second is not first or state['events']!=1:raise ValueError('current native hook not observed on hit')
            state['refuse']=True
            for label,target,filename in (('native',native,'A4_DIAGNOSTIC_HIT.py'),
                 ('hit',builtins.compile,'A4_DIAGNOSTIC_HIT.py'),('miss',builtins.compile,'A4_DIAGNOSTIC_MISS.py')):
                try:target(body,filename,'exec',dont_inherit=True)
                except Refusal:results[label+'_refused']=True
                else:raise ValueError('native audit refusal bypassed')
    finally:state['active']=False;sys.audit=audit
    if (construction!=3 or installation!=1 or state['events']!=4 or
        adapter.audit_refusals!=1 or builtins.compile is not native or adapter.installed):raise ValueError('audit conjunction failed')
    return {'construction_refusals':construction,'installation_refusals':installation,
     'hook_events':state['events'],**results,'compile_restored':True}

def tool_paths():
    require_windows();python=physical(Path(r'C:\hostedtoolcache\windows\Python\3.12.10\x64\python.exe'))
    if physical(Path(sys.executable))!=python:raise ValueError('unexpected physical Python installation')
    candidates=(Path(r'C:\Program Files\Git\ucrt64\bin\git.exe'),Path(r'C:\Program Files\Git\mingw64\bin\git.exe'))
    git=next((physical(p) for p in candidates if p.exists()),None)
    if git is None:raise ValueError('direct physical Git runtime unavailable')
    return {'python':{'path':str(python),**digest(python.read_bytes())},'git':{'path':str(git),**digest(git.read_bytes())}}
def environment(tools):
    values={'SystemRoot':r'C:\Windows','WINDIR':r'C:\Windows',
     'PATH':os.pathsep.join((str(Path(tools['python']['path']).parent),str(Path(tools['git']['path']).parent),r'C:\Windows\System32')),
     'PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1','LC_ALL':'C','LANG':'C',
     'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':os.devnull,'GIT_TERMINAL_PROMPT':'0',
     'GIT_NO_LAZY_FETCH':'1','GIT_ALLOW_PROTOCOL':''}
    for key in ('TEMP','TMP'):
        if key in os.environ:values[key]=os.environ[key]
    return values
def git(source,tools,*args):
    return subprocess.run([tools['git']['path'],'-c','protocol.allow=never','-c','core.hooksPath='+os.devnull,
      '-c','core.autocrlf=false','-c','core.fsmonitor=false',*args],cwd=source,env=environment(tools),
      stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=30).stdout
def provider_binding(output):
    require_windows()
    expected={'GITHUB_ACTIONS':'true','RUNNER_ENVIRONMENT':'github-hosted','GITHUB_REPOSITORY':'theislampill/IMPLEMENTAUDIT.md',
     'GITHUB_EVENT_NAME':'push','GITHUB_REF':'refs/heads/'+BRANCH,'GITHUB_RUN_ATTEMPT':'1','RUNNER_OS':'Windows'}
    if any(os.environ.get(k)!=v for k,v in expected.items()):raise ValueError('provider first-push binding differs')
    run=os.environ.get('GITHUB_RUN_ID','');commit=os.environ.get('GITHUB_SHA','')
    if not re.fullmatch('[0-9]+',run) or not re.fullmatch('[0-9a-f]{40}',commit):raise ValueError('invalid provider identity')
    event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    if event.get('before')!='0'*40 or event.get('after')!=commit or event.get('created') is not True or event.get('deleted') is not False:
        raise ValueError('exclusive fresh branch creation required')
    expected_output=physical(Path(os.environ['RUNNER_TEMP']),True)/('dg18-a4-compiler-memory-'+run+'-1')
    if output!=expected_output:raise ValueError('output is not exact provider-run path')
    return {'run_id':int(run),'attempt':1,'host_commit':commit,'branch':BRANCH}
def source_receiving(source,tools):
    physical(source,True)
    if git(source,tools,'show','-s','--format=%H%n%T','HEAD').decode().splitlines()!=[SOURCE_COMMIT,SOURCE_TREE]:
        raise ValueError('source commit or tree differs')
    if git(source,tools,'status','--porcelain=v1','--untracked-files=all'):raise ValueError('source checkout dirty')
    for relative,pin in SOURCE_PINS.items():read_pinned(source/relative,pin)
    return {'source_commit':SOURCE_COMMIT,'source_tree':SOURCE_TREE,'members':SOURCE_PINS,'tools':tools}
def host_receiving(source,output):
    provider=provider_binding(output);tools=tool_paths()
    helper=physical(Path(__file__).absolute());packet=physical(helper.parents[len(PurePosixPath(HELPER_PATH).parts)-1],True)
    physical(source,True)
    if source==packet or source.is_relative_to(output) or output.is_relative_to(source):raise ValueError('source/output overlap')
    actual=git(packet,tools,'show','-s','--format=%H%n%T%n%P','HEAD').decode().splitlines()
    if actual[0]!=provider['host_commit'] or actual[2].split()!=[SOURCE_COMMIT]:raise ValueError('host sole parent differs')
    changed=git(packet,tools,'diff-tree','--no-commit-id','--name-only','-r','HEAD').decode().splitlines()
    if sorted(changed)!=sorted((HELPER_PATH,ADAPTER_PATH,WORKFLOW_PATH)):raise ValueError('host mutation scope differs')
    if git(packet,tools,'ls-tree',SOURCE_COMMIT,'--',HELPER_PATH,ADAPTER_PATH,WORKFLOW_PATH):raise ValueError('host paths are not all additive')
    if git(packet,tools,'status','--porcelain=v1','--untracked-files=all'):raise ValueError('host checkout dirty')
    read_pinned(helper.with_name('compile_adapter.py'),ADAPTER_PIN)
    return {**CONTEXT,**provider,'host_tree':actual[1],'source_path':str(source),'output_path':str(output),
      'helper':digest(helper.read_bytes()),'adapter':ADAPTER_PIN,'tools':tools,'fixed_modes':list(MODES)}

def worker(source,output,mode):
    require_windows();physical(output,True)
    plan=json.loads((output.parent/'INTENT.json').read_text())
    if (mode not in MODES or output.name!=mode or plan['source_path']!=str(source) or
        plan['helper']!=digest(Path(__file__).read_bytes()) or plan['adapter']!=ADAPTER_PIN):raise ValueError('worker intent differs')
    if digest(physical(Path(sys.executable)).read_bytes())!={k:plan['tools']['python'][k] for k in ('bytes','sha256')}:
        raise ValueError('worker physical Python differs')
    read_pinned(Path(__file__).absolute().with_name('compile_adapter.py'),ADAPTER_PIN)
    started={'pid':os.getpid(),'parent_pid':os.getppid(),'mode':mode,'started_ns':time.time_ns(),**CONTEXT}
    write_json(output/'STARTED.json',started)
    if mode=='audit':summary={'mode':mode,'controls':audit_controls()}
    else:
        memory=NativeMemory(output/'native-memory');memory.sample('worker-before-source')
        inputs={Path(relative).name:(source/relative,pin) for relative,pin in list(SOURCE_PINS.items())[:2]}
        held,summary=compile_workload(mode,inputs,memory)
        for path,pin in inputs.values():read_pinned(path,pin)
        memory.sample('worker-after-source')
        if len(held)!=4 or memory.sequence!=10:raise ValueError('fixed compile/memory population differs')
        summary['native_records']=memory.sequence
        summary['last_lifetime_peak_working_set_bytes']=memory.last_peak
    read_pinned(Path(__file__).absolute().with_name('compile_adapter.py'),ADAPTER_PIN)
    write_json(output/'RESULT.json',{**CONTEXT,**summary,'pid':os.getpid(),'completed_ns':time.time_ns(),
      'status':'CONTROLLED_DIAGNOSTIC_COMPLETE_NO_A4_AWARD'})
    return 0

def qualify_job(row,command,python,mode):
    expected={'status':'COMPLETE_UNADMITTED','exit_code':0,'platform':'win32','started_suspended':True,
     'assigned_before_resume':True,'root_job_membership_confirmed':True,'completion_port_associated_before_assignment':True,
     'complete_memory_scope_valid':True,'cleanup_complete':True,'terminal_active_processes':0,
     'terminal_breakaway_allowed':False,'initial_job_flags':0x2000,'terminal_job_flags':0x2000,
     'kernel_total_processes':1,'creation_event_count':1,'exit_event_count':1,'active_process_zero_count':1,
     'abnormal_exit_event_count':0}
    if any(type(row.get(k))is not type(v) or row[k]!=v for k,v in expected.items()):raise ValueError('native Job conjunction incomplete')
    if row.get('command')!=command or row.get('process_observation_failures')!=[]:raise ValueError('native Job command/image differs')
    observed=row.get('observed_processes');spelling=lambda p:str(PureWindowsPath(p)).casefold()
    if (type(observed)is not list or len(observed)!=1 or observed[0].get('pid')!=row.get('root_pid') or
        observed[0].get('in_job')is not True or observed[0].get('image_sha256')!=python['sha256'] or
        spelling(observed[0].get('image',''))!=spelling(python['path'])):raise ValueError('exact single Python worker image unproven')
    return {'mode':mode,'pid':row['root_pid'],'complete_single_worker_job':True,'award':None}

def execute(source,output):
    binding=host_receiving(source,output);before=source_receiving(source,binding['tools'])
    output.mkdir(mode=0o700,exist_ok=False);write_json(output/'INTENT.json',binding);write_json(output/'SOURCE_BEFORE.json',before)
    jobpath=source/'scripts/r0039-windows-job.py';raw=read_pinned(jobpath,SOURCE_PINS['scripts/r0039-windows-job.py'])
    spec=importlib.util.spec_from_file_location('exact_native_job',jobpath);job=importlib.util.module_from_spec(spec)
    exec(compile(raw,str(jobpath),'exec',dont_inherit=True),job.__dict__)
    received=[]
    try:
        for mode in MODES:
            selected=output/mode;selected.mkdir(mode=0o700,exist_ok=False)
            command=[binding['tools']['python']['path'],'-I','-B',str(Path(__file__).absolute()),
             '--step','worker','--source',str(source),'--output',str(selected),'--mode',mode]
            write_json(selected/'COMMAND_INTENT.json',{'command':command,'mode':mode,'automatic_retry':False})
            row=job.measure(command,source,environment(binding['tools']),selected/'job',diagnostic_timeout_seconds=120)
            job.reconcile_process_events(row.get('process_events'),row.get('kernel_total_processes'),row.get('root_pid'))
            received.append(qualify_job(row,command,binding['tools']['python'],mode))
            result=json.loads((selected/'RESULT.json').read_text())
            if result.get('pid')!=row['root_pid'] or result.get('mode')!=mode or result.get('status')!='CONTROLLED_DIAGNOSTIC_COMPLETE_NO_A4_AWARD':
                raise ValueError('worker result identity differs')
        after=source_receiving(source,tool_paths());write_json(output/'SOURCE_AFTER.json',after)
        if after!=before:raise ValueError('source or physical tools changed')
        if host_receiving(source,output)!=binding:raise ValueError('host or provider binding changed')
        write_json(output/'RESULT.json',{**CONTEXT,'status':'SEPARATE_NATIVE_COMPILER_DIAGNOSTIC_RECORDED','workers':received,
          'interpretation':'Raw controlled native measurements only; no original-suite prediction or threshold acceptance.'})
    except BaseException as exc:
        write_json(output/'ERROR.json',{**CONTEXT,'error_type':type(exc).__name__,'error':str(exc),
          'completed_workers':received,'effects':'RETAIN_ACTUAL_BYTES_NO_RETRY'})
        raise
    return 0

def finalize(source,output):
    provider_binding(output)
    if not output.exists():output.mkdir(mode=0o700,exist_ok=False);write_json(output/'NO_EXECUTION.json',CONTEXT)
    physical(output,True);write_json(output/'FINALIZE_INTENT.json',{**CONTEXT,'started_ns':time.time_ns()})
    rows=[];total=0
    def walk(directory):
        nonlocal total
        for path in sorted(directory.iterdir()):
            info=path.lstat()
            if unsafe(info):raise ValueError('retained diagnostic link/reparse entry refused')
            if stat.S_ISDIR(info.st_mode):walk(path);continue
            physical(path)
            if len(rows)>=128 or info.st_size>2*1024*1024:raise ValueError('retained diagnostic population bound exceeded')
            raw=path.read_bytes();total+=len(raw)
            if total>8*1024*1024:raise ValueError('retained diagnostic byte bound exceeded')
            rows.append({'path':path.relative_to(output).as_posix(),**digest(raw)})
    walk(output)
    write_json(output/'MANIFEST.json',{**CONTEXT,'members':rows,'bytes':total})
    archive=output/'DIAGNOSTIC.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for row in rows:
            path=physical(output/row['path']);raw=path.read_bytes()
            if digest(raw)!={k:row[k] for k in ('bytes','sha256')}:raise ValueError('retained diagnostic bytes changed')
            z.writestr(row['path'],raw)
        z.writestr('MANIFEST.json',(output/'MANIFEST.json').read_bytes())
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None or len(z.namelist())!=len(set(z.namelist())):raise ValueError('ZIP CRC or membership differs')
    write_json(output/'ZIP_RECEIPT.json',{**CONTEXT,'archive':digest(archive.read_bytes()),'members':len(rows)+1})
    return 0

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--step',choices=('execute','worker','finalize'),required=True)
    parser.add_argument('--source',required=True);parser.add_argument('--output',required=True)
    parser.add_argument('--mode',choices=MODES);args=parser.parse_args()
    source=Path(os.path.abspath(args.source));output=Path(os.path.abspath(args.output))
    if args.step=='worker':return worker(source,output,args.mode)
    if args.mode is not None:raise ValueError('mode is only valid for worker')
    return globals()[args.step](source,output)
if __name__=='__main__':raise SystemExit(main())
