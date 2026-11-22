#!/usr/bin/env python3
"""Four installed-file metadata profiles only; no tool execution or admission."""
from __future__ import annotations
import argparse
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
import zipfile

SOURCE_COMMIT='51416b2f156b341c4a5f09029e2c6ceb5b30b1e7'
SOURCE_TREE='9c3913ceaa95f3f36b0377fe2dba4a302afcba89'
BRANCH='pro/dg18-a4-tool-profile-20261121-01'
HELPER_PATH='handoff/pro-executor-results-20261115/dg18-a4-tool-profile/tool_profile.py'
WORKFLOW_PATH='.github/workflows/dg18-a4-tool-profile.yml'
PYTHON_PATH=r'C:\hostedtoolcache\windows\Python\3.12.10\x64\python.exe'
TARGETS=(r'C:\Program Files\Git\ucrt64\bin\git.exe',r'C:\Program Files\Git\mingw64\bin\git.exe',
         r'C:\Program Files\Git\bin\git.exe',PYTHON_PATH)
FILE_LIMIT=16*1024*1024
READ_CHUNK=64*1024
NAME_CAP=4096
ALIAS_CAP=32
SECONDS=45
JSON_LIMIT=1024*1024
OUTPUT_LIMIT=8*1024*1024
CONTEXT={'schema':'dg18.a4.installed-tool-metadata.v1','authority':'NONE','award':None,
 'source_revision':'R2',
 'operation':'METADATA_ONLY_NO_TOOL_ADMISSION','source_parent':SOURCE_COMMIT,'source_tree':SOURCE_TREE,
 'source_binding':'Root sole-parent/full-additive-tree receiving; helper executes no Git',
 'original_memory_guard_bytes':67108864,'original_memory_guard_changed':False,
 'original_method_order_changed':False,'original_method_executions':0,
 'Git_product_Job_executions':0,'alias_admissions':0,'A4_07':'UNKNOWN_NO_REPLAY',
 'frozen_R01_R09_contract_available':False,'historical_selected_Git_spelling':'UNRECORDED',
 'prior_failure_cause':'COMBINED_TYPE_OR_LINK_COUNT_REFUSAL_NOT_INDIVIDUALLY_ATTRIBUTED',
 'automatic_retry':False}

def canonical(row):return (json.dumps(row,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode()
def digest(raw):return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def error(exc):
    return {'type':type(exc).__name__,'message':str(exc)[:512],
            'errno':getattr(exc,'errno',None),'winerror':getattr(exc,'winerror',None)}
def stat_record(info):
    fields={name:getattr(info,name) for name in ('st_mode','st_ino','st_dev','st_nlink','st_size',
     'st_atime_ns','st_mtime_ns','st_ctime_ns','st_birthtime_ns','st_file_attributes','st_reparse_tag') if hasattr(info,name)}
    return {'status':'OBSERVED','fields':fields,'regular':stat.S_ISREG(info.st_mode),
     'directory':stat.S_ISDIR(info.st_mode),'symlink':stat.S_ISLNK(info.st_mode),
     'reparse':bool(getattr(info,'st_file_attributes',0)&0x400),'mode_octal':oct(info.st_mode)}
def stat_snapshot(path):
    try:return {'path':str(path),**stat_record(os.lstat(path))}
    except OSError as exc:return {'path':str(path),'status':'ERROR','error':error(exc)}
def identity(row):
    if row.get('status')!='OBSERVED':return None
    return {k:v for k,v in row['fields'].items() if k!='st_atime_ns'}

# CPython v3.12.10 only: raw fields remain unchanged. Path stat applies the
# .exe execute-bit heuristic and maps ctime to birthtime; fstat does neither.
# Exact same-API comparisons below still retain full mode and change time.
CROSS_FIELDS=('st_ino','st_dev','st_nlink','st_size','st_mtime_ns','st_birthtime_ns',
              'st_file_attributes','st_reparse_tag')
STAT_FIELDS=(*CROSS_FIELDS,'st_mode','st_ctime_ns','st_atime_ns')
def comparison(equal,**detail):
    return {'status':'INCOMPLETE' if equal is None else ('MATCH' if equal else 'MISMATCH'),
            'equal':equal,**detail}
def observed_stat(row):
    return (type(row)is dict and row.get('status')=='OBSERVED' and type(row.get('fields'))is dict
        and all(type(row['fields'].get(k))is int for k in STAT_FIELDS))
def same_api_comparison(first,last):
    if not observed_stat(first) or not observed_stat(last):return comparison(None,reason='complete same-API stat fields unavailable')
    return comparison(identity(first)==identity(last),scope='exact same API; full mode and ctime retained; access time excluded')
def cross_api_identity(path_row,fd_row):
    if not observed_stat(path_row) or not observed_stat(fd_row):return comparison(None,reason='complete cross-API fields unavailable')
    p=path_row['fields'];f=fd_row['fields']
    if path_row.get('path') not in TARGETS:return comparison(False,reason='outside four fixed executable spellings')
    ordinary=all(r.get('regular')is True and r.get('directory')is False and
        r.get('symlink')is False and r.get('reparse')is False for r in (path_row,fd_row))
    ordinary=ordinary and all(not v['st_file_attributes']&0x410 and v['st_reparse_tag']==0 for v in (p,f))
    expected_fd_mode=stat.S_IFREG | (0o444 if f['st_file_attributes']&1 else 0o666)
    expected_path_mode=stat.S_IFREG | (0o444 if p['st_file_attributes']&1 else 0o666) | 0o111
    fields_equal=all(p[k]==f[k] for k in CROSS_FIELDS)
    modes=p['st_mode']==expected_path_mode and f['st_mode']==expected_fd_mode
    path_ctime=p['st_ctime_ns']==p['st_birthtime_ns']
    return comparison(bool(ordinary and fields_equal and modes and path_ctime),
        semantic_contract='CPython-v3.12.10-fixed-exe-stat-fstat',exact_fields=list(CROSS_FIELDS),
        fields_equal=fields_equal,mode_mapping_matches=modes,path_ctime_is_birthtime=path_ctime,
        descriptor_ctime='native ChangeTime; compared exactly only within fstat before/after',
        raw_metadata_modified=False,identifier_widths_truncated=False)
def complete_profile(row):
    """Derive only comparisons whose inputs exist; never erase partial errors."""
    comparisons={
      'path':same_api_comparison(row.get('path_before'),row.get('path_final')),
      'descriptor':same_api_comparison(row.get('held_before'),row.get('held_after')),
      'cross_before':cross_api_identity(row.get('path_before'),row.get('held_before')),
      'cross_after':cross_api_identity(row.get('path_final'),row.get('held_after'))}
    before=row.get('ancestors_before');after=row.get('ancestors_final')
    if type(before)is not list or type(after)is not list or not before or not after:
        comparisons['ancestors']=comparison(None,reason='ancestor snapshots unavailable')
    elif len(before)!=len(after):comparisons['ancestors']=comparison(False,reason='ancestor populations differ')
    else:
        pairs=[same_api_comparison(a,b) for a,b in zip(before,after)]
        if any(p['equal']is None for p in pairs):comparisons['ancestors']=comparison(None,reason='ancestor metadata incomplete')
        else:comparisons['ancestors']=comparison(all(p['equal'] and a.get('path')==b.get('path') for p,a,b in zip(pairs,before,after)))
    native_keys=('file_attributes','reparse','volume_serial','file_index','file_bytes','number_of_links',
                 'creation_filetime','access_filetime','write_filetime')
    first=row.get('native_before');last=row.get('native_after')
    if any(type(value)is not dict or any(k not in value for k in native_keys) for value in (first,last)):
        comparisons['native_handle']=comparison(None,reason='native before/after metadata unavailable')
    else:
        clean=lambda value:{k:v for k,v in value.items() if k!='access_filetime'}
        comparisons['native_handle']=comparison(clean(first)==clean(last))
    first=row.get('native_final_path_before');last=row.get('native_final_path_after')
    if any(type(value)is not dict or value.get('status')!='OBSERVED' or type(value.get('value'))is not str for value in (first,last)):
        comparisons['native_path']=comparison(None,reason='native final-path observations unavailable')
    else:comparisons['native_path']=comparison(first['value']==last['value'])
    row['comparisons']=comparisons
    row['path_to_held_identity_equal']=comparisons['cross_before']['equal']
    hashed=row.get('hash',{});links=row.get('hardlinks',{})
    if type(hashed)is not dict:hashed={}
    if type(links)is not dict:links={}
    last=row.get('native_after',{})
    row['hardlink_count_matches_native']=(links.get('recorded_names')==last.get('number_of_links')
        if type(last)is dict and type(links.get('recorded_names'))is int and type(last.get('number_of_links'))is int else None)
    all_comparisons=all(value['equal']is True for value in comparisons.values())
    row['stable_read_observed']=bool(all_comparisons and hashed.get('status')=='EOF_OBSERVED' and hashed.get('matches_held_size')is True)
    row['stable_read_status']='INCOMPLETE' if any(value['equal']is None for value in comparisons.values()) else ('OBSERVED_STABLE' if row['stable_read_observed'] else 'NOT_ESTABLISHED')
    row['status']='PARTIAL_METADATA_REFUSAL'
    if (row['stable_read_observed'] and links.get('status')=='COMPLETE' and links.get('close_succeeded')is True
        and row['hardlink_count_matches_native']is True and row.get('handle_closed')is True and row.get('errors')==[]):
        row['status']='FACTUAL_PROFILE_OBSERVED_NO_ADMISSION'
    return row
def ancestors(path):
    if len(path.parents)>12:raise ValueError('ancestor population exceeds fixed bound')
    return [stat_snapshot(p) for p in path.parents]
def safe_ancestors(rows):
    return all(r.get('status')=='OBSERVED' and r['directory'] and not r['symlink'] and not r['reparse'] for r in rows)
def require_windows():
    if os.name!='nt' or sys.platform!='win32':raise ValueError('actual Windows required before output or native calls')
    if sys.implementation.name!='cpython' or sys.version_info[:3]!=(3,12,10) or C.sizeof(C.c_void_p)!=8:
        raise ValueError('exact CPython 3.12.10 x64 required')
    if os.path.normcase(os.path.abspath(sys.executable))!=os.path.normcase(PYTHON_PATH):
        raise ValueError('exact selected Python spelling required')
def bounded_read(path,limit):
    with path.open('rb') as stream:raw=stream.read(limit+1)
    if len(raw)>limit:raise ValueError('bounded control-input read refused')
    return raw
def write_new(output,name,row):
    raw=canonical(row)
    if len(raw)>JSON_LIMIT:raise ValueError('JSON record exceeds one MiB')
    with (output/name).open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
def check_time(deadline):
    if time.monotonic()>deadline:raise TimeoutError('fixed metadata diagnostic deadline elapsed')

class FILETIME(C.Structure):
    _fields_=[('low',C.c_uint32),('high',C.c_uint32)]
class INFO(C.Structure):
    _fields_=[('attributes',C.c_uint32),('creation',FILETIME),('access',FILETIME),('write',FILETIME),
      ('volume_serial',C.c_uint32),('size_high',C.c_uint32),('size_low',C.c_uint32),
      ('links',C.c_uint32),('index_high',C.c_uint32),('index_low',C.c_uint32)]

class Native:
    def __init__(self):
        require_windows()
        if C.sizeof(INFO)!=52 or C.sizeof(C.c_wchar)!=2:raise ValueError('native structure widths differ')
        k=C.WinDLL('kernel32',use_last_error=True)
        def bind(name,result,*args):
            f=getattr(k,name);f.restype=result;f.argtypes=list(args);return f
        H=C.c_void_p;D=C.c_uint32;B=C.c_int32;S=C.c_wchar_p
        self.open=bind('CreateFileW',H,S,D,D,H,D,D,H)
        self.close=bind('CloseHandle',B,H)
        self.info=bind('GetFileInformationByHandle',B,H,C.POINTER(INFO))
        self.file_type=bind('GetFileType',D,H)
        self.final=bind('GetFinalPathNameByHandleW',D,H,S,D,D)
        self.first=bind('FindFirstFileNameW',H,S,D,C.POINTER(D),S)
        self.next=bind('FindNextFileNameW',B,H,C.POINTER(D),S)
        self.find_close=bind('FindClose',B,H)
        self.invalid=C.c_void_p(-1).value
    def win_error(self,operation):
        exc=C.WinError(C.get_last_error());exc.args=(*exc.args,operation);return exc
    def held_info(self,handle):
        row=INFO()
        if not self.info(handle,C.byref(row)):raise self.win_error('GetFileInformationByHandle')
        ft=lambda v:(int(v.high)<<32)|int(v.low)
        return {'file_attributes':int(row.attributes),'reparse':bool(row.attributes&0x400),
         'volume_serial':int(row.volume_serial),'file_index':(int(row.index_high)<<32)|int(row.index_low),
         'file_bytes':(int(row.size_high)<<32)|int(row.size_low),'number_of_links':int(row.links),
         'creation_filetime':ft(row.creation),'access_filetime':ft(row.access),'write_filetime':ft(row.write)}
    def final_path(self,handle):
        buffer=C.create_unicode_buffer(NAME_CAP);count=int(self.final(handle,buffer,NAME_CAP,0))
        if not count:return {'status':'ERROR','error':error(self.win_error('GetFinalPathNameByHandleW'))}
        if count>=NAME_CAP:return {'status':'BUFFER_BOUND_REFUSAL','required_characters':count,'capacity':NAME_CAP}
        return {'status':'OBSERVED','value':buffer.value,'characters':count}
    def aliases(self,path,deadline):
        result={'status':'INCOMPLETE','names':[],'aliases_opened':0,'aliases_admitted':0,
          'name_capacity_characters':NAME_CAP,'record_limit':ALIAS_CAP,'close_succeeded':None}
        handle=None;buffer=C.create_unicode_buffer(NAME_CAP);length=C.c_uint32(NAME_CAP)
        try:
            check_time(deadline)
            handle=self.first(str(path),0,C.byref(length),buffer)
            if handle==self.invalid:
                handle=None;code=C.get_last_error()
                result.update(status='NATIVE_ERROR',winerror=code,reported_characters=int(length.value));return result
            if not handle:handle=None;raise ValueError('null native enumeration handle')
            result['names'].append(buffer.value)
            while True:
                check_time(deadline);length.value=NAME_CAP
                if not self.next(handle,C.byref(length),buffer):
                    code=C.get_last_error()
                    result.update(status='COMPLETE' if code==38 else 'NATIVE_ERROR',winerror=code,
                        reported_characters=int(length.value));break
                if len(result['names'])==ALIAS_CAP:
                    result.update(status='COUNT_BOUND_REFUSAL',at_least_one_more_name=True);break
                result['names'].append(buffer.value)
                if len(result['names'])!=len(set(result['names'])):
                    result['status']='DUPLICATE_NAME_OBSERVED';break
        except Exception as exc:result.update(status='ERROR',error=error(exc))
        finally:
            if handle is not None:
                result['close_succeeded']=bool(self.find_close(handle))
                if not result['close_succeeded']:
                    result['close_error']=error(self.win_error('FindClose'));result['status']='CLOSE_ERROR'
            result['recorded_names']=len(result['names'])
        return result

def streamed_hash(fd,expected_size,deadline):
    if not 0<=expected_size<=FILE_LIMIT:return {'status':'SIZE_BOUND_REFUSAL','expected_bytes':expected_size,'bytes_read':0}
    hashed=hashlib.sha256();count=0
    try:
        while True:
            check_time(deadline);raw=os.read(fd,min(READ_CHUNK,FILE_LIMIT+1-count))
            if not raw:break
            count+=len(raw);hashed.update(raw)
            if count>FILE_LIMIT:return {'status':'READ_BOUND_REFUSAL','bytes_read':count,'partial_sha256':hashed.hexdigest()}
        return {'status':'EOF_OBSERVED','bytes_read':count,'sha256':hashed.hexdigest(),'matches_held_size':count==expected_size}
    except Exception as exc:return {'status':'ERROR','bytes_read':count,'partial_sha256':hashed.hexdigest(),'error':error(exc)}

def profile_one(index,path,native,deadline):
    import msvcrt
    row={**CONTEXT,'index':index,'path':str(path),'started_ns':time.time_ns(),
      'status':'PARTIAL_METADATA_REFUSAL','errors':[],'handle_closed':None,
      'read_access':{'desired_access':'GENERIC_READ','share_mode':'FILE_SHARE_READ',
      'creation':'OPEN_EXISTING','flags':'FILE_FLAG_OPEN_REPARSE_POINT','handle_inheritance':False}}
    handle=None;fd=None
    try:
        check_time(deadline);row['path_before']=stat_snapshot(path);row['ancestors_before']=ancestors(path)
        first=row['path_before']
        if first['status']!='OBSERVED':raise ValueError('input lstat unavailable; metadata retained')
        if not first['regular'] or first['symlink'] or first['reparse']:
            raise ValueError('non-regular or reparse input retained without read')
        if not safe_ancestors(row['ancestors_before']):raise ValueError('unsafe/unavailable ancestor retained without read')
        check_time(deadline)
        handle=native.open(str(path),0x80000000,1,None,3,0x00200000,None)
        if handle==native.invalid:handle=None;raise native.win_error('CreateFileW')
        if not handle:handle=None;raise ValueError('null native file handle')
        row['native_before']=native.held_info(handle)
        C.set_last_error(0);row['native_file_type']=int(native.file_type(handle))
        row['native_file_type_last_error']=C.get_last_error()
        row['native_final_path_before']=native.final_path(handle)
        if row['native_file_type']!=1 or row['native_before']['reparse']:
            raise ValueError('held input not an ordinary disk file; metadata retained')
        fd=msvcrt.open_osfhandle(handle,os.O_RDONLY)
        msvcrt.setmode(fd,os.O_BINARY)
        row['held_before']=stat_record(os.fstat(fd))
        row['cross_api_before']=cross_api_identity(first,row['held_before'])
        if row['cross_api_before']['equal']is True:
            row['hash']=streamed_hash(fd,row['held_before']['fields']['st_size'],deadline)
        else:row['hash']={'status':'PATH_HELD_IDENTITY_REFUSAL','bytes_read':0}
        row['hardlinks']=native.aliases(path,deadline)
        row['active_operation']='held_after';row['held_after']=stat_record(os.fstat(fd))
        row['active_operation']='native_after';row['native_after']=native.held_info(handle)
        row['active_operation']='native_final_path_after'
        row['native_final_path_after']=native.final_path(handle)
    except Exception as exc:row['errors'].append({'operation':row.get('active_operation','profile_observation'),**error(exc)})
    finally:
        row['path_final']=stat_snapshot(path);row['ancestors_final']=ancestors(path)
        if fd is not None:
            try:os.close(fd);row['handle_closed']=True
            except OSError as exc:row['handle_closed']=False;row['errors'].append(error(exc))
        elif handle is not None:
            row['handle_closed']=bool(native.close(handle))
            if not row['handle_closed']:row['errors'].append(error(native.win_error('CloseHandle')))
        row['completed_ns']=time.time_ns()
    return complete_profile(row)

def provider_binding(output):
    require_windows()
    expected={'GITHUB_ACTIONS':'true','RUNNER_ENVIRONMENT':'github-hosted','GITHUB_REPOSITORY':'theislampill/IMPLEMENTAUDIT.md',
      'GITHUB_EVENT_NAME':'push','GITHUB_REF':'refs/heads/'+BRANCH,'GITHUB_RUN_ATTEMPT':'1','RUNNER_OS':'Windows'}
    if any(os.environ.get(k)!=v for k,v in expected.items()):raise ValueError('first-push provider binding differs')
    run=os.environ.get('GITHUB_RUN_ID','');sha=os.environ.get('GITHUB_SHA','')
    if not re.fullmatch('[0-9]+',run) or not re.fullmatch('[0-9a-f]{40}',sha):raise ValueError('invalid run/commit identity')
    event=json.loads(bounded_read(Path(os.environ['GITHUB_EVENT_PATH']),JSON_LIMIT))
    if (event.get('before')!='0'*40 or event.get('after')!=sha or event.get('created')is not True
        or event.get('deleted')is not False):raise ValueError('fresh exclusive branch creation required')
    if output!=Path(os.environ['RUNNER_TEMP'])/('dg18-a4-tool-profile-'+run+'-1'):raise ValueError('exact provider output required')
    helper=Path(os.path.abspath(__file__))
    if helper!=Path(os.environ['GITHUB_WORKSPACE'])/'packet'/HELPER_PATH:raise ValueError('exact reviewed helper path required')
    if not safe_ancestors(ancestors(output)):raise ValueError('output ancestor chain unsafe')
    return {'run_id':int(run),'attempt':1,'host_commit':sha,'branch':BRANCH,'helper':digest(bounded_read(helper,JSON_LIMIT))}

def capture_status(output,names,expected_binding=None):
    """Report retained protocol completeness, never infer native success."""
    if 'RESULT.json' not in names:
        return {'status':'INCOMPLETE_FATAL' if 'FATAL.json' in names else 'INCOMPLETE_NO_TERMINAL_RESULT',
                'complete_profile_population':False,'cleanup_inferred':False}
    if 'FATAL.json' in names:return {'status':'INCOMPLETE_CONFLICTING_TERMINALS','complete_profile_population':False,'cleanup_inferred':False}
    required={'INTENT.json'}|{f'PROFILE-{i:02d}{suffix}.json' for i in range(1,5) for suffix in ('','-INTENT')}
    if not required.issubset(names):return {'status':'INCOMPLETE_MISSING_RECORDS','missing':sorted(required-names),
                                         'complete_profile_population':False,'cleanup_inferred':False}
    try:
        result=json.loads(bounded_read(output/'RESULT.json',JSON_LIMIT))
        intent=json.loads(bounded_read(output/'INTENT.json',JSON_LIMIT))
        if type(result)is not dict or type(intent)is not dict:raise ValueError('terminal or intent schema differs')
        if expected_binding is not None and any(intent.get(k)!=v for k,v in expected_binding.items()):
            raise ValueError('profile/finalizer provider or helper binding differs')
        if (result.get('status')!='METADATA_RECORDED_WITH_EXPLICIT_PARTIALS_NO_ADMISSION' or result.get('profile_count')!=4
            or type(result.get('profiles'))is not list or len(result['profiles'])!=4):raise ValueError('terminal population differs')
        partial=[]
        for i,(target,summary) in enumerate(zip(TARGETS,result['profiles']),1):
            profile=json.loads(bounded_read(output/f'PROFILE-{i:02d}.json',JSON_LIMIT))
            started=json.loads(bounded_read(output/f'PROFILE-{i:02d}-INTENT.json',JSON_LIMIT))
            if (type(profile)is not dict or type(started)is not dict or type(summary)is not dict or
                profile.get('index')!=i or profile.get('path')!=target or started.get('index')!=i or started.get('path')!=target
                or summary.get('index')!=i or summary.get('status')!=profile.get('status')):
                raise ValueError('profile/intent/terminal identities differ')
            if profile.get('status')!='FACTUAL_PROFILE_OBSERVED_NO_ADMISSION':partial.append(i)
        return {'status':'PROFILE_POPULATION_RECORDED_WITH_PARTIALS' if partial else 'PROFILE_POPULATION_RECORDED',
                'complete_profile_population':True,'partial_profiles':partial,'native_success_inferred':False,'cleanup_inferred':False}
    except (OSError,ValueError,TypeError,KeyError) as exc:
        return {'status':'INCOMPLETE_INVALID_TERMINAL_OR_RECORDS','complete_profile_population':False,
                'cleanup_inferred':False,'error':error(exc)}

def seal(output,expected_binding=None,deadline=None):
    deadline=time.monotonic()+20 if deadline is None else deadline
    rows=[];refusals=[];total=0
    paths=list(output.iterdir())
    if len(paths)>16:raise ValueError('output file count exceeds fixed bound')
    allowed={'INTENT.json','RESULT.json','FATAL.json','FINALIZATION_INTENT.json','NO_PROFILE_OUTPUT.json'}|{
             f'PROFILE-{i:02d}{suffix}.json' for i in range(1,5) for suffix in ('','-INTENT')}
    for path in sorted(paths):
        check_time(deadline)
        if path.name not in allowed:
            refusals.append({'name':path.name,'reason':'OUTSIDE_FINITE_OUTPUT_NAMES_NOT_READ'});continue
        before=stat_snapshot(path)
        if (before['status']!='OBSERVED' or not before['regular'] or before['symlink'] or before['reparse']
            or before['fields']['st_nlink']!=1 or not path.name.endswith('.json') or before['fields']['st_size']>JSON_LIMIT):
            refusals.append({'name':path.name,'reason':'UNSAFE_OR_UNBOUNDED_OUTPUT_NOT_READ'});continue
        raw=bounded_read(path,JSON_LIMIT);after=stat_snapshot(path)
        if identity(before)!=identity(after):raise ValueError('output changed while sealing')
        total+=len(raw)
        if total>OUTPUT_LIMIT:raise ValueError('output total byte bound exceeded')
        rows.append({'path':path.name,**digest(raw)})
    capture=capture_status(output,{r['path'] for r in rows},expected_binding)
    manifest={**CONTEXT,'members':rows,'payload_bytes':total,'refusals':refusals,'capture_completeness':capture,
              'finalization_scope':'existing bounded bytes only; no profile replay or completion invention'}
    write_new(output,'MANIFEST.json',manifest)
    with zipfile.ZipFile(output/'PROFILE_EVIDENCE.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
        for row in rows:
            check_time(deadline)
            path=output/row['path'];before=stat_snapshot(path)
            if before['status']!='OBSERVED' or not before['regular'] or before['reparse'] or before['symlink']:
                raise ValueError('output type changed before archive')
            raw=bounded_read(path,JSON_LIMIT)
            if digest(raw)!={k:row[k] for k in ('bytes','sha256')} or identity(before)!=identity(stat_snapshot(path)):
                raise ValueError('retained output identity changed')
            z.writestr(row['path'],raw)
        z.writestr('MANIFEST.json',canonical(manifest))
    archive=output/'PROFILE_EVIDENCE.zip'
    with zipfile.ZipFile(archive) as z:
        if z.testzip()is not None or len(z.namelist())!=len(set(z.namelist())):raise ValueError('archive integrity differs')
    write_new(output,'ZIP_RECEIPT.json',{**CONTEXT,'archive':digest(bounded_read(archive,OUTPUT_LIMIT+JSON_LIMIT)),
       'member_count':len(rows)+1,'refusal_count':len(refusals),'capture_completeness':capture})

def finalize(output):
    binding=provider_binding(output);observed=stat_snapshot(output)
    if observed['status']=='ERROR':
        if observed['error']['type']!='FileNotFoundError':raise ValueError('profile output unavailable for safe finalization')
        output.mkdir(mode=0o700,exist_ok=False)
        write_new(output,'NO_PROFILE_OUTPUT.json',{**CONTEXT,'observation':'exact run output absent before finalization',
            'profile_execution_established':False,'at_ns':time.time_ns()})
    elif not observed['directory'] or observed['symlink'] or observed['reparse']:
        raise ValueError('profile output is not an ordinary directory')
    write_new(output,'FINALIZATION_INTENT.json',{**CONTEXT,**binding,'at_ns':time.time_ns(),
        'profile_replayed':False,'profile_completion_inferred':False,'cooperative_seconds':20})
    seal(output,expected_binding=binding,deadline=time.monotonic()+20)
    return 0

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True)
    parser.add_argument('--step',choices=('profile','finalize'),default='profile');args=parser.parse_args()
    output=Path(os.path.abspath(args.output))
    if args.step=='finalize':return finalize(output)
    binding=provider_binding(output)
    output.mkdir(mode=0o700,exist_ok=False)
    version=sys.getwindowsversion();deadline=time.monotonic()+SECONDS
    write_new(output,'INTENT.json',{**CONTEXT,**binding,'pid':os.getpid(),'started_ns':time.time_ns(),
      'targets':list(TARGETS),'python':sys.version,'windows':{'major':version.major,'minor':version.minor,
       'build':version.build,'platform':version.platform,'product_type':version.product_type},
      'bounds':{'files':4,'file_read_bytes':FILE_LIMIT+1,'all_installed_file_read_bytes':4*(FILE_LIMIT+1),'read_chunk':READ_CHUNK,
       'alias_records_per_file':ALIAS_CAP,'native_name_buffer_characters':NAME_CAP,'cooperative_seconds':SECONDS,
       'output_files':16,'output_file_bytes':JSON_LIMIT,'output_total_bytes':OUTPUT_LIMIT}})
    rows=[];fatal=None
    try:
        if version.major!=10 or version.build!=20348 or version.product_type!=3:
            raise ValueError('Windows Server 2022 kernel identity differs; no profile attempted')
        native=Native()
        for index,name in enumerate(TARGETS,1):
            write_new(output,f'PROFILE-{index:02d}-INTENT.json',{'index':index,'path':name,'started_ns':time.time_ns(),
                'operation':'FIXED_INSTALLED_FILE_METADATA_ONLY','tool_execution_authorized':False})
            row=profile_one(index,Path(name),native,deadline);write_new(output,f'PROFILE-{index:02d}.json',row)
            rows.append({'index':index,'status':row['status'],'handle_closed':row['handle_closed'],
             'error_count':len(row['errors']),'hardlink_status':row.get('hardlinks',{}).get('status')})
        if any(r['handle_closed']is False or r['hardlink_status']=='CLOSE_ERROR' for r in rows):
            raise ValueError('native handle cleanup did not complete')
        write_new(output,'RESULT.json',{**CONTEXT,'status':'METADATA_RECORDED_WITH_EXPLICIT_PARTIALS_NO_ADMISSION',
          'profiles':rows,'profile_count':len(rows),'completed_ns':time.time_ns()})
    except Exception as exc:
        fatal=exc;write_new(output,'FATAL.json',{**CONTEXT,'error':error(exc),'retained_profiles':rows})
    return 2 if fatal is not None else 0
if __name__=='__main__':raise SystemExit(main())
