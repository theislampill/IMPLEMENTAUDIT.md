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
import math
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
BRANCH='pro/dg18-a4-compiler-memory-51416-20261122-03'
WORKFLOW_PATH='.github/workflows/dg18-a4-compiler-memory-r3.yml'
HELPER_PATH='handoff/pro-executor-results-20261115/dg18-a4-compiler-memory-r3/compile_memory.py'
ADAPTER_PATH='handoff/pro-executor-results-20261115/dg18-a4-compiler-memory-r3/compile_adapter.py'
PROFILE_PATH='handoff/pro-executor-results-20261115/dg18-a4-compiler-memory-r3/observed_tool_profile.py'
CONHOST_PATH='handoff/pro-executor-results-20261115/dg18-a4-compiler-memory-r3/conhost_custody.py'
CONHOST_PIN={'bytes':14586,'sha256':'3f6f724f87fa2b09d081ba4ce3ed3c8600cebf39de6443b2958eee8c1a8aa67d'}
CONHOST_IMAGE={'path':r'C:\Windows\System32\conhost.exe',
 'sha256':'4670e2d339001988eace0219462dfaa750418fddf09c004adb28f13aa8a4df2e'}
PROFILE_PIN={'bytes':28985,'sha256':'aa61123993614898f8d731352d04862a5a8fe9b77d1811f640e40870e8bf09b5'}
GIT_PATH=r'C:\Program Files\Git\ucrt64\bin\git.exe'
GIT_PIN={'bytes':4414792,'sha256':'9bf8ee81d79f38a11eaf7799499a634c46a718e009a4a9b2b20b115804643302'}
GIT_ALIASES=frozenset((
 r'\Program Files\Git\ucrt64\bin\git.exe',r'\Program Files\Git\ucrt64\bin\git-upload-pack.exe',
 r'\Program Files\Git\ucrt64\bin\git-receive-pack.exe',r'\Program Files\Git\ucrt64\bin\git-upload-archive.exe'))
PROFILE_EVIDENCE={'run_id':44960177535,'attempt':1,'host_commit':'53733a8081d518fdc58df9bfff0cefad618aea5c',
 'receiving_seal_sha256':'23fd3d64e5bd32f272c0e4c2b24a5171817636f0b13019d3f12cdd4c68b2e4c8',
 'raw_seal_sha256':'b25353cc50a485f449a455121bca39de456f30d73faeac5a445617c28f7a1011',
 'root_adjudication_sha256':'bf11280969ee08eac284a1d14c10f27fa82f7f3128339655bf81b1f4d757d725',
 'scope':'historical authentic constraints only; not current executable admission'}
ADAPTER_PIN={'bytes':6595,'sha256':'4baffb9fdadde5333a1bf535593d4aa794936578be297b1ce723e1f0bd1683b2'}
SOURCE_PINS={
 'skills/implementaudit/scripts/claim-run-rotation.py':{'bytes':291693,'sha256':'9eebc5d5e57b47b0e4b4a2a846de1c0b55407713e14008a6de4d01e7a8c5e19e'},
 'skills/implementaudit/scripts/rotate-canonical-state.py':{'bytes':129959,'sha256':'86a9a2a8501aea60f1e333c421e25b19d4e9758a121296fedfa881185de0a5fd'},
 'scripts/r0039-windows-job.py':{'bytes':25678,'sha256':'0191eb110977e8aad6c615f7130052c08a38b83297c65748768608a2959ecd8b'},
 'fixtures/canonical-state-rotation/windows_custody_test.py':{'bytes':17370,'sha256':'9dd670dc98f55a7527d8202aab306743a6c8b2f15396d83b0c409211e2918f4b'}}
MODES=('native','r2','audit')
REFERENCE_LIMIT=67108864
CONTEXT={'schema':'dg18.a4.separate-compiler-memory.v1','authority':'NONE','award':None,
 'source_revision':'R3','tool_admission':'fresh held exact Git identity and four-name set only',
 'worker_population':'one exact Python root; zero or one separately held exact conhost; complete Job census',
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

def load_observed_profile():
    path=Path(__file__).absolute().with_name('observed_tool_profile.py');raw=read_pinned(path,PROFILE_PIN)
    spec=importlib.util.spec_from_file_location('exact_observed_tool_profile',path)
    module=importlib.util.module_from_spec(spec)
    exec(compile(raw,str(path),'exec',dont_inherit=True),module.__dict__)
    read_pinned(path,PROFILE_PIN)
    return module

def load_conhost_custody():
    path=Path(__file__).absolute().with_name('conhost_custody.py');raw=read_pinned(path,CONHOST_PIN)
    spec=importlib.util.spec_from_file_location('exact_conhost_custody',path)
    module=importlib.util.module_from_spec(spec)
    exec(compile(raw,str(path),'exec',dont_inherit=True),module.__dict__)
    read_pinned(path,CONHOST_PIN)
    if module.CONHOST!=CONHOST_IMAGE:raise ValueError('fixed console-host image binding differs')
    return module.HeldConhost

def native_identity(row):
    return {k:v for k,v in row.items() if k!='access_filetime'}

def validate_git_metadata(profile,row,baseline=None,hash_required=False):
    """Pure data predicate; calling it does not produce native evidence."""
    derived=profile.complete_profile(dict(row))
    if any(value['equal']is not True for value in derived['comparisons'].values()):
        raise ValueError('Git same-API or reviewed cross-API identity incomplete/different')
    if row.get('path')!=GIT_PATH or row.get('errors')!=[] or row.get('native_file_type')!=1:
        raise ValueError('exact ordinary Git path or error-free metadata required')
    for key in ('path_before','path_final','held_before','held_after'):
        fields=row[key]['fields']
        if fields['st_nlink']!=4 or fields['st_size']!=GIT_PIN['bytes']:
            raise ValueError('Git exact size/link population differs')
    for key in ('native_before','native_after'):
        value=row[key]
        if (value['number_of_links']!=4 or value['file_bytes']!=GIT_PIN['bytes'] or
            value['reparse']is not False or value['file_attributes']&0x410):
            raise ValueError('native Git type/size/link population differs')
    for key in ('native_final_path_before','native_final_path_after'):
        if row[key].get('value')!='\\\\?\\'+GIT_PATH:raise ValueError('native final Git spelling differs')
    if not profile.safe_ancestors(row['ancestors_before']) or not profile.safe_ancestors(row['ancestors_final']):
        raise ValueError('Git ancestor chain unsafe')
    aliases=row.get('hardlinks',{});names=aliases.get('names')
    if (aliases.get('status')!='COMPLETE' or aliases.get('winerror')!=38 or aliases.get('close_succeeded')is not True
        or aliases.get('recorded_names')!=4 or type(names)is not list or len(names)!=4
        or any(type(name)is not str for name in names) or frozenset(names)!=GIT_ALIASES
        or aliases.get('aliases_opened')!=0 or aliases.get('aliases_admitted')!=0):
        raise ValueError('complete exact four-name native alias set required')
    if hash_required:
        hashed=row.get('hash',{})
        if (hashed.get('status')!='EOF_OBSERVED' or hashed.get('matches_held_size')is not True
            or hashed.get('bytes_read')!=GIT_PIN['bytes'] or hashed.get('sha256')!=GIT_PIN['sha256']):
            raise ValueError('fresh held Git byte identity differs/incomplete')
    if baseline is not None:
        pairs=[(baseline['path_final'],row['path_before']),(baseline['held_after'],row['held_before'])]
        first=baseline['ancestors_final'];last=row['ancestors_before']
        if len(first)!=len(last) or [v['path'] for v in first]!=[v['path'] for v in last]:
            raise ValueError('Git ancestor population changed while held')
        pairs.extend(zip(first,last))
        if (any(profile.same_api_comparison(a,b)['equal']is not True for a,b in pairs)
            or native_identity(baseline['native_after'])!=native_identity(row['native_before'])):
            raise ValueError('Git or ancestors differ from live held admission')
    return derived['comparisons']

class HeldGit:
    """One live-process receiver, never a cache or generic hardlink allowance."""
    def __init__(self,output,provider):
        require_windows();self.profile=load_observed_profile();self.native=self.profile.Native()
        self.output=output;self.provider=provider;self.pid=os.getpid();self.path=Path(GIT_PATH)
        self.handle=None;self.fd=None;self.directories=[];self.initial=None;self.sequence=0;self.git_calls=0
        self.deadline=time.monotonic()+420;self.last_tick=0;self.finished=False
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        self.tick=kernel.GetTickCount64;self.tick.argtypes=[];self.tick.restype=ctypes.c_uint64
        version=sys.getwindowsversion()
        if (version.major,version.minor,version.build,version.product_type)!=(10,0,20348,3):
            raise ValueError('actual Windows Server 2022 runtime required')
    def clock(self):
        self.profile.check_time(self.deadline)
        tick=int(self.tick())
        if os.getpid()!=self.pid or tick<self.last_tick:raise ValueError('live receiver PID/uptime continuity differs')
        self.last_tick=tick;return tick
    def record(self,name,row):
        row={**CONTEXT,**self.provider,'receiver_pid':self.pid,**row}
        if len(canonical(row))>1024*1024:raise ValueError('held-tool observation exceeds fixed record bound')
        write_json(self.output/name,row)
    def directory_state(self,path,handle,row):
        row['path']=str(path);row['stat']=self.profile.stat_snapshot(path)
        row['native']=self.native.held_info(handle);row['final_path']=self.native.final_path(handle)
        row['native_file_type']=int(self.native.file_type(handle))
        return row
    def check_directory(self,row,baseline=None):
        if (not self.profile.safe_ancestors([row['stat']]) or not row['native']['file_attributes']&0x10
            or row['native']['reparse']is not False or row['native_file_type']!=1
            or row['final_path'].get('status')!='OBSERVED'
            or row['final_path'].get('value')!='\\\\?\\'+row['path']):
            raise ValueError('held ancestor directory type/final spelling differs')
        if baseline is not None and (row['path']!=baseline['path']
            or self.profile.same_api_comparison(baseline['stat'],row['stat'])['equal']is not True
            or native_identity(baseline['native'])!=native_identity(row['native'])):
            raise ValueError('held ancestor same-API identity changed')
    def directory_snapshots(self,row,key):
        row[key]=[]
        for entry in self.directories:
            current={};row[key].append(current)
            self.directory_state(entry['path'],entry['handle'],current)
            self.check_directory(current,entry['baseline'])
    def __enter__(self):
        row={'status':'ACQUIRING','historical_constraints':PROFILE_EVIDENCE,'git_path':GIT_PATH,
             'expected_pin':GIT_PIN,'expected_aliases':sorted(GIT_ALIASES),'directories':[],
             'file_share_mode':'READ_ONLY_NO_WRITE_OR_DELETE','directory_share_mode':'READ_WRITE_NO_DELETE',
             'directory_access':'FILE_LIST_DIRECTORY|FILE_READ_ATTRIBUTES (0x81)',
             'handles_inheritable':False,'aliases_opened':0,'aliases_executed':0,'errors':[]}
        try:
            row['uptime_start_ms']=self.clock()
            parents=list(reversed(self.path.parents))
            if len(parents)!=5:raise ValueError('exact five-ancestor population required')
            for path in parents:
                item={'path':str(path)};row['directories'].append(item)
                item['before']=self.profile.stat_snapshot(path)
                if not self.profile.safe_ancestors([item['before']]):raise ValueError('unsafe ancestor before open')
                # LIST_DIRECTORY participates in delete-sharing checks; attributes alone do not.
                handle=self.native.open(str(path),0x81,3,None,3,0x02200000,None)
                if handle==self.native.invalid:raise self.native.win_error('CreateFileW ancestor')
                if not handle:raise ValueError('null ancestor handle')
                entry={'path':path,'handle':handle};self.directories.append(entry)
                item['held']={};self.directory_state(path,handle,item['held']);self.check_directory(item['held'])
                if self.profile.same_api_comparison(item['before'],item['held']['stat'])['equal']is not True:
                    raise ValueError('ancestor changed while opening')
                entry['baseline']=item['held']
            row['target_before_open']=self.profile.stat_snapshot(self.path)
            self.handle=self.native.open(GIT_PATH,0x80000000,1,None,3,0x00200000,None)
            if self.handle==self.native.invalid:self.handle=None;raise self.native.win_error('CreateFileW Git')
            if not self.handle:self.handle=None;raise ValueError('null Git handle')
            import msvcrt
            self.fd=msvcrt.open_osfhandle(self.handle,os.O_RDONLY);msvcrt.setmode(self.fd,os.O_BINARY)
            self.initial=self.observe('initial-admission',hash_required=True)
            if self.profile.same_api_comparison(row['target_before_open'],self.initial['path_before'])['equal']is not True:
                raise ValueError('Git path changed while opening')
            row['status']='EXACT_GIT_HELD_FOR_THIS_OPERATION';row['uptime_end_ms']=self.clock()
            self.record('GIT_ACQUIRE.json',row)
            return self
        except BaseException as exc:
            row['status']='GIT_ADMISSION_REFUSED';row['errors'].append(self.profile.error(exc))
            try:self.record('GIT_ACQUIRE.json',row)
            finally:self.close()
            raise
    def observe(self,label,hash_required=False):
        if self.sequence>=26 or self.fd is None or self.handle is None:raise ValueError('live receiver/observation bound differs')
        self.sequence+=1
        row={'sequence':self.sequence,'label':label,'path':GIT_PATH,'status':'PARTIAL_HELD_OBSERVATION',
             'errors':[],'hash_required':hash_required,'handle_closed':False,'same_boot_binding':'same live PID and retained handles'}
        try:
            row['uptime_start_ms']=self.clock();deadline=min(self.deadline,time.monotonic()+45)
            row['path_before']=self.profile.stat_snapshot(self.path);row['ancestors_before']=self.profile.ancestors(self.path)
            self.directory_snapshots(row,'ancestor_handles_before')
            row['held_before']=self.profile.stat_record(os.fstat(self.fd));row['native_before']=self.native.held_info(self.handle)
            ctypes.set_last_error(0);row['native_file_type']=int(self.native.file_type(self.handle))
            row['native_file_type_last_error']=ctypes.get_last_error()
            row['native_final_path_before']=self.native.final_path(self.handle)
            if (self.profile.cross_api_identity(row['path_before'],row['held_before'])['equal']is not True
                or row['native_file_type']!=1 or row['native_before']['reparse']is not False
                or row['native_before']['file_attributes']&0x410
                or row['held_before']['fields']['st_size']!=GIT_PIN['bytes']
                or row['held_before']['fields']['st_nlink']!=4
                or row['native_before']['file_bytes']!=GIT_PIN['bytes'] or row['native_before']['number_of_links']!=4
                or row['native_final_path_before'].get('status')!='OBSERVED'
                or row['native_final_path_before'].get('value')!='\\\\?\\'+GIT_PATH):
                raise ValueError('ordinary exact Git identity required before byte read or enumeration')
            if hash_required:
                os.lseek(self.fd,0,os.SEEK_SET)
                row['hash']=self.profile.streamed_hash(self.fd,GIT_PIN['bytes'],deadline)
            row['hardlinks']=self.native.aliases(self.path,deadline)
            row['held_after']=self.profile.stat_record(os.fstat(self.fd));row['native_after']=self.native.held_info(self.handle)
            row['native_final_path_after']=self.native.final_path(self.handle)
            row['path_final']=self.profile.stat_snapshot(self.path);row['ancestors_final']=self.profile.ancestors(self.path)
            self.directory_snapshots(row,'ancestor_handles_after')
            self.profile.check_time(deadline)
            row['comparisons']=validate_git_metadata(self.profile,row,self.initial,hash_required)
            row['uptime_end_ms']=self.clock();row['status']='EXACT_HELD_GIT_METADATA_MATCH'
            return row
        except BaseException as exc:
            row['errors'].append(self.profile.error(exc));raise
        finally:self.record(f'GIT_OBSERVATION-{self.sequence:02d}.json',row)
    def before_command(self):
        if self.git_calls>=12 or self.initial is None or self.finished:raise ValueError('fixed twelve-Git-command population exceeded')
        self.git_calls+=1;self.observe(f'command-{self.git_calls:02d}-before')
    def after_command(self):self.observe(f'command-{self.git_calls:02d}-after')
    def finish(self):
        if self.git_calls!=12:raise ValueError('fixed twelve-Git-command population incomplete')
        self.observe('terminal-held-rehash',hash_required=True);self.finished=True
    def close(self):
        row={'status':'CLOSING','git_calls':self.git_calls,'observations':self.sequence,'terminal_rehash_complete':self.finished,
             'file_handle_closed':None,'directory_handles':[],'errors':[]}
        if self.fd is not None:
            try:os.close(self.fd);row['file_handle_closed']=True
            except OSError as exc:row['file_handle_closed']=False;row['errors'].append(self.profile.error(exc))
            self.fd=None;self.handle=None
        elif self.handle is not None:
            row['file_handle_closed']=bool(self.native.close(self.handle))
            if not row['file_handle_closed']:row['errors'].append(self.profile.error(self.native.win_error('CloseHandle Git')))
            self.handle=None
        for entry in reversed(self.directories):
            closed=bool(self.native.close(entry['handle']));row['directory_handles'].append({'path':str(entry['path']),'closed':closed})
            if not closed:row['errors'].append(self.profile.error(self.native.win_error('CloseHandle ancestor')))
        self.directories=[];row['status']='ACQUIRED_HANDLES_CLOSED' if not row['errors'] else 'HANDLE_CLEANUP_REFUSAL'
        self.record('GIT_CLOSED.json',row)
        return not row['errors']
    def __exit__(self,kind,value,traceback):
        closed=self.close()
        if not closed and kind is None:raise ValueError('held Git/ancestor handle cleanup incomplete')
        return False

def tool_paths(custody):
    require_windows();python=physical(Path(r'C:\hostedtoolcache\windows\Python\3.12.10\x64\python.exe'))
    if physical(Path(sys.executable))!=python:raise ValueError('unexpected physical Python installation')
    if custody.initial is None or custody.fd is None or custody.pid!=os.getpid():raise ValueError('fresh live held Git admission required')
    return {'python':{'path':str(python),**digest(python.read_bytes())},'git':{'path':GIT_PATH,**GIT_PIN}}
def environment(tools):
    values={'SystemRoot':r'C:\Windows','WINDIR':r'C:\Windows',
     'PATH':os.pathsep.join((str(Path(tools['python']['path']).parent),str(Path(tools['git']['path']).parent),r'C:\Windows\System32')),
     'PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1','LC_ALL':'C','LANG':'C',
     'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':os.devnull,'GIT_TERMINAL_PROMPT':'0',
     'GIT_NO_LAZY_FETCH':'1','GIT_ALLOW_PROTOCOL':''}
    for key in ('TEMP','TMP'):
        if key in os.environ:values[key]=os.environ[key]
    return values
def git(source,tools,custody,*args):
    if tools['git']!={'path':GIT_PATH,**GIT_PIN}:raise ValueError('command Git differs from narrow receiver')
    custody.before_command()
    try:
        return subprocess.run([tools['git']['path'],'-c','protocol.allow=never','-c','core.hooksPath='+os.devnull,
          '-c','core.autocrlf=false','-c','core.fsmonitor=false',*args],cwd=source,env=environment(tools),
          stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=30).stdout
    finally:custody.after_command()
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
    expected_output=physical(Path(os.environ['RUNNER_TEMP']),True)/('dg18-a4-compiler-memory-r3-'+run+'-1')
    if output!=expected_output:raise ValueError('output is not exact provider-run path')
    return {'run_id':int(run),'attempt':1,'host_commit':commit,'branch':BRANCH}
def source_receiving(source,tools,custody):
    physical(source,True)
    if git(source,tools,custody,'show','-s','--format=%H%n%T','HEAD').decode().splitlines()!=[SOURCE_COMMIT,SOURCE_TREE]:
        raise ValueError('source commit or tree differs')
    if git(source,tools,custody,'status','--porcelain=v1','--untracked-files=all'):raise ValueError('source checkout dirty')
    for relative,pin in SOURCE_PINS.items():read_pinned(source/relative,pin)
    return {'source_commit':SOURCE_COMMIT,'source_tree':SOURCE_TREE,'members':SOURCE_PINS,'tools':tools}
def host_receiving(source,output,custody):
    provider=provider_binding(output);tools=tool_paths(custody)
    helper=physical(Path(__file__).absolute());packet=physical(helper.parents[len(PurePosixPath(HELPER_PATH).parts)-1],True)
    physical(source,True)
    if source==packet or source.is_relative_to(output) or output.is_relative_to(source):raise ValueError('source/output overlap')
    actual=git(packet,tools,custody,'show','-s','--format=%H%n%T%n%P','HEAD').decode().splitlines()
    if actual[0]!=provider['host_commit'] or actual[2].split()!=[SOURCE_COMMIT]:raise ValueError('host sole parent differs')
    changed=git(packet,tools,custody,'diff-tree','--no-commit-id','--name-only','-r','HEAD').decode().splitlines()
    if sorted(changed)!=sorted((HELPER_PATH,ADAPTER_PATH,PROFILE_PATH,CONHOST_PATH,WORKFLOW_PATH)):raise ValueError('host mutation scope differs')
    if git(packet,tools,custody,'ls-tree',SOURCE_COMMIT,'--',HELPER_PATH,ADAPTER_PATH,PROFILE_PATH,CONHOST_PATH,WORKFLOW_PATH):raise ValueError('host paths are not all additive')
    if git(packet,tools,custody,'status','--porcelain=v1','--untracked-files=all'):raise ValueError('host checkout dirty')
    read_pinned(helper.with_name('compile_adapter.py'),ADAPTER_PIN)
    read_pinned(helper.with_name('observed_tool_profile.py'),PROFILE_PIN)
    read_pinned(helper.with_name('conhost_custody.py'),CONHOST_PIN)
    return {**CONTEXT,**provider,'host_tree':actual[1],'source_path':str(source),'output_path':str(output),
      'helper':digest(helper.read_bytes()),'adapter':ADAPTER_PIN,'observed_profile_helper':PROFILE_PIN,
      'conhost_custody_helper':CONHOST_PIN,'conhost_image':CONHOST_IMAGE,'tools':tools,'fixed_modes':list(MODES)}

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

def qualify_job(row,command,python,mode,conhost,reconcile):
    expected={'status':'COMPLETE_UNADMITTED','exit_code':0,'platform':'win32','started_suspended':True,
     'assigned_before_resume':True,'root_job_membership_confirmed':True,'completion_port_associated_before_assignment':True,
     'complete_memory_scope_valid':True,'cleanup_complete':True,'terminal_active_processes':0,
     'terminal_breakaway_allowed':False,'initial_job_flags':0x2000,'terminal_job_flags':0x2000,
     'active_process_zero_count':1,'abnormal_exit_event_count':0,'root_prior_suspend_count':1,
     'kernel_terminated_processes':0,'containment_status':'ROOT_EXITED_AND_JOB_EMPTY',
     'baseline_subtracted_bytes':0,'harness_included':False,'diagnostic_timeout_seconds':120,
     'metric_admission':'UNADMITTED_DIAGNOSTIC'}
    if any(type(row.get(k))is not type(v) or row[k]!=v for k,v in expected.items()):raise ValueError('native Job conjunction incomplete')
    if row.get('command')!=command or row.get('process_observation_failures')!=[]:raise ValueError('native Job command/image differs')
    if conhost!=CONHOST_IMAGE:raise ValueError('fresh exact console-host image descriptor required')
    total=row.get('kernel_total_processes')
    if type(total)is not int or total not in (1,2):raise ValueError('only root and at most one console-host lifetime admitted')
    counts=reconcile(row.get('process_events'),total,row.get('root_pid'))
    if any(type(row.get(k))is not type(v) or row[k]!=v for k,v in counts.items()):raise ValueError('stored and derived Job accounting differ')
    observed=row.get('observed_processes');created=[r['pid'] for r in row['process_events'] if r['event']=='NEW_PROCESS']
    if (type(observed)is not list or len(observed)!=total or len(set(created))!=total
        or any(type(r)is not dict or set(r)!={'pid','image','image_sha256','in_job'}
               or type(r['pid'])is not int or not 0<r['pid']<=0xffffffff or r['in_job']is not True
               or type(r['image'])is not str or type(r['image_sha256'])is not str for r in observed)
        or len({r['pid'] for r in observed})!=total or {r['pid'] for r in observed}!=set(created)):
        raise ValueError('complete unique observed process-image census unproven')
    root=[r for r in observed if r['pid']==row['root_pid']];companions=[r for r in observed if r['pid']!=row['root_pid']]
    spelling=lambda p:str(PureWindowsPath(p)).casefold()
    if (len(root)!=1 or root[0]['image_sha256']!=python['sha256'] or spelling(root[0]['image'])!=spelling(python['path'])
        or len(companions)>1 or any(r['image_sha256']!=conhost['sha256'] or spelling(r['image'])!=spelling(conhost['path']) for r in companions)):
        raise ValueError('exact Python root/held console-host image population unproven')
    elapsed=row.get('elapsed_ms');root_exit=row.get('root_exit_observed_ms')
    job_peak=row.get('peak_job_committed_bytes');single_peak=row.get('peak_single_process_committed_bytes')
    if (type(elapsed) not in (int,float) or type(root_exit) not in (int,float)
        or not math.isfinite(elapsed) or not math.isfinite(root_exit) or not 0<=root_exit<=elapsed
        or type(job_peak)is not int or type(single_peak)is not int or not 0<single_peak<=job_peak):
        raise ValueError('raw Job timing/memory metadata invalid')
    return {'mode':mode,'pid':row['root_pid'],'complete_supported_worker_job':True,'process_count':total,
      'conhost_pid':companions[0]['pid'] if companions else None,'aggregate_job_committed_bytes':job_peak,
      'elapsed_ms':elapsed,'numeric_performance_admission':False,'award':None}

def execute(source,output):
    provider=provider_binding(output);output.mkdir(mode=0o700,exist_ok=False)
    write_json(output/'ADMISSION_INTENT.json',{**CONTEXT,**provider,'receiver_pid':os.getpid(),
      'historical_constraints':PROFILE_EVIDENCE,'git_path':GIT_PATH,'expected_pin':GIT_PIN,
      'expected_aliases':sorted(GIT_ALIASES),'prior_operation_replayed':False})
    received=[]
    try:
        with HeldGit(output,provider) as custody:
            binding=host_receiving(source,output,custody);before=source_receiving(source,binding['tools'],custody)
            write_json(output/'INTENT.json',binding);write_json(output/'SOURCE_BEFORE.json',before)
            jobpath=source/'scripts/r0039-windows-job.py';raw=read_pinned(jobpath,SOURCE_PINS['scripts/r0039-windows-job.py'])
            spec=importlib.util.spec_from_file_location('exact_native_job',jobpath);job=importlib.util.module_from_spec(spec)
            exec(compile(raw,str(jobpath),'exec',dont_inherit=True),job.__dict__)
            with load_conhost_custody()(custody) as console:
                for mode in MODES:
                    custody.clock();console.before_worker(mode)
                    selected=output/mode;selected.mkdir(mode=0o700,exist_ok=False)
                    command=[binding['tools']['python']['path'],'-I','-B',str(Path(__file__).absolute()),
                     '--step','worker','--source',str(source),'--output',str(selected),'--mode',mode]
                    write_json(selected/'COMMAND_INTENT.json',{'command':command,'mode':mode,'automatic_retry':False})
                    try:row=job.measure(command,source,environment(binding['tools']),selected/'job',diagnostic_timeout_seconds=120)
                    except BaseException:
                        try:console.after_worker(mode)
                        except BaseException as post_error:
                            write_json(selected/'POST_JOB_IMAGE_ERROR.json',{'scope':'image observation after failed Job; original Job error retained',
                              'error':custody.profile.error(post_error)})
                        raise
                    else:console.after_worker(mode)
                    received.append(qualify_job(row,command,binding['tools']['python'],mode,console.image(),job.reconcile_process_events))
                    result=json.loads((selected/'RESULT.json').read_text())
                    if result.get('pid')!=row['root_pid'] or result.get('mode')!=mode or result.get('status')!='CONTROLLED_DIAGNOSTIC_COMPLETE_NO_A4_AWARD':
                        raise ValueError('worker result identity differs')
                    custody.clock()
                after=source_receiving(source,tool_paths(custody),custody);write_json(output/'SOURCE_AFTER.json',after)
                if after!=before:raise ValueError('source or physical tools changed')
                if host_receiving(source,output,custody)!=binding:raise ValueError('host or provider binding changed')
                console.finish();custody.finish()
        write_json(output/'RESULT.json',{**CONTEXT,'status':'SEPARATE_NATIVE_COMPILER_DIAGNOSTIC_RECORDED','workers':received,
          'held_Git_admission_closed':True,'Git_command_count':custody.git_calls,'Git_observation_count':custody.sequence,
          'held_conhost_admission_closed':True,'conhost_observation_count':console.sequence,
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
