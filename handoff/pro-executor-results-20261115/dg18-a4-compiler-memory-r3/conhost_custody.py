#!/usr/bin/env python3
"""Supervisor-only held custody of the one observed console-host image."""
from __future__ import annotations
import ctypes
import os
from pathlib import Path, PureWindowsPath
import stat
import time

CONHOST={'path':r'C:\Windows\System32\conhost.exe',
         'sha256':'4670e2d339001988eace0219462dfaa750418fddf09c004adb28f13aa8a4df2e'}
TARGET_ALIAS=r'\Windows\System32\conhost.exe'
MODES=('native','r2','audit')

def native_identity(row):return {k:v for k,v in row.items() if k!='access_filetime'}

def cross_identity(profile,path_row,fd_row):
    """Same reviewed CPython 3.12.10 semantics, only this new fixed .exe path.

    No raw field, original helper target list, or generic file guard is changed.
    """
    if not profile.observed_stat(path_row) or not profile.observed_stat(fd_row):return profile.comparison(None)
    p=path_row['fields'];f=fd_row['fields']
    ordinary=all(r.get('regular')is True and r.get('directory')is False and
        r.get('symlink')is False and r.get('reparse')is False for r in (path_row,fd_row))
    ordinary=ordinary and all(not v['st_file_attributes']&0x410 and v['st_reparse_tag']==0 for v in (p,f))
    mapped=(p['st_mode']==(stat.S_IFREG|(0o444 if p['st_file_attributes']&1 else 0o666)|0o111)
            and f['st_mode']==(stat.S_IFREG|(0o444 if f['st_file_attributes']&1 else 0o666))
            and p['st_ctime_ns']==p['st_birthtime_ns'])
    return profile.comparison(path_row.get('path')==CONHOST['path'] and ordinary and mapped
        and all(p[k]==f[k] for k in profile.CROSS_FIELDS),
        semantic_contract='CPython-v3.12.10-fixed-conhost-exe-stat-fstat',
        raw_metadata_modified=False,identifier_widths_truncated=False)

def initial_identity(profile,row):
    if cross_identity(profile,row.get('path_before'),row.get('held_before'))['equal']is not True:
        raise ValueError('conhost path/descriptor identity incomplete or different')
    native=row.get('native_before',{});held=row['held_before']['fields'];size=held['st_size'];links=held['st_nlink']
    if (row.get('path')!=CONHOST['path'] or row.get('native_file_type')!=1
        or not 0<size<=profile.FILE_LIMIT or not 1<=links<=profile.ALIAS_CAP
        or native.get('reparse')is not False or type(native.get('file_attributes'))is not int
        or native['file_attributes']&0x410 or type(native.get('file_bytes'))is not int
        or type(native.get('number_of_links'))is not int or native['file_bytes']!=size or native['number_of_links']!=links
        or row.get('native_final_path_before',{}).get('status')!='OBSERVED'
        or row['native_final_path_before'].get('value')!='\\\\?\\'+CONHOST['path']):
        raise ValueError('ordinary bounded exact conhost identity required before read/enumeration')
    return size,links

def validate_observation(profile,row,baseline=None,hash_required=False):
    """Data predicate only; live custody and native observations belong to the caller."""
    derived=profile.complete_profile(dict(row))
    comparisons={key:value for key,value in derived['comparisons'].items() if key not in ('cross_before','cross_after')}
    comparisons['cross_before']=cross_identity(profile,row.get('path_before'),row.get('held_before'))
    comparisons['cross_after']=cross_identity(profile,row.get('path_final'),row.get('held_after'))
    if any(value['equal']is not True for value in comparisons.values()):raise ValueError('conhost metadata incomplete/unstable')
    size,links=initial_identity(profile,row)
    expected_ancestors=[str(path) for path in PureWindowsPath(CONHOST['path']).parents]
    if (row.get('errors')!=[] or row['native_final_path_after'].get('value')!='\\\\?\\'+CONHOST['path']
        or not profile.safe_ancestors(row['ancestors_before']) or not profile.safe_ancestors(row['ancestors_final'])
        or [r.get('path') for r in row['ancestors_before']]!=expected_ancestors
        or [r.get('path') for r in row['ancestors_final']]!=expected_ancestors):
        raise ValueError('conhost errors, final spelling or ancestor refusal')
    inventory=row.get('hardlinks',{});names=inventory.get('names')
    if (inventory.get('status')!='COMPLETE' or inventory.get('winerror')!=38
        or inventory.get('close_succeeded')is not True or type(inventory.get('recorded_names'))is not int
        or inventory['recorded_names']!=links or type(names)is not list or len(names)!=links
        or any(type(name)is not str for name in names) or len(set(names))!=links
        or inventory.get('aliases_opened')!=0 or inventory.get('aliases_admitted')!=0):
        raise ValueError('complete bounded conhost link inventory required')
    for name in names:
        if (not name.startswith('\\') or name.startswith('\\\\') or ':' in name or '\0' in name
            or any(part in ('','.','..') for part in name[1:].split('\\'))
            or len(name.encode('utf-16-le','surrogatepass'))//2>=profile.NAME_CAP):
            raise ValueError('conhost alias is not a bounded volume-relative name')
    folded={name.casefold() for name in names}
    if len(folded)!=links or TARGET_ALIAS.casefold() not in folded:raise ValueError('target absent or ambiguous in conhost aliases')
    if hash_required:
        hashed=row.get('hash',{})
        if (hashed.get('status')!='EOF_OBSERVED' or hashed.get('matches_held_size')is not True
            or hashed.get('bytes_read')!=size or hashed.get('sha256')!=CONHOST['sha256']):
            raise ValueError('held conhost hash differs from authentic observed image')
    if baseline is not None:
        pairs=[(baseline['path_final'],row['path_before']),(baseline['held_after'],row['held_before'])]
        first=baseline['ancestors_final'];last=row['ancestors_before']
        if len(first)!=len(last) or [r['path'] for r in first]!=[r['path'] for r in last]:raise ValueError('conhost ancestor population changed')
        pairs.extend(zip(first,last))
        if (any(profile.same_api_comparison(a,b)['equal']is not True for a,b in pairs)
            or native_identity(baseline['native_after'])!=native_identity(row['native_before'])
            or set(baseline['hardlinks']['names'])!=set(names)):
            raise ValueError('conhost differs from its fresh live held receiving')
    return comparisons

class HeldConhost:
    def __init__(self,owner):
        owner.profile.require_windows()
        if owner.pid!=os.getpid() or owner.fd is None or owner.initial is None:raise ValueError('live supervisor custody required')
        self.owner=owner;self.profile=owner.profile;self.native=owner.native;self.path=Path(CONHOST['path'])
        self.directories=[];self.handle=None;self.fd=None;self.initial=None
        self.sequence=0;self.workers=0;self.pending=None;self.finished=False
    def record(self,name,row):
        self.owner.record(name,{'conhost_image':CONHOST,'alias_policy':'fresh held inventory only; no returned-alias admission/execution',**row})
    def directory_snapshots(self,row,key):
        row[key]=[]
        for entry in self.directories:
            current={};row[key].append(current)
            self.owner.directory_state(entry['path'],entry['handle'],current)
            self.owner.check_directory(current,entry['baseline'])
    def __enter__(self):
        self.record('CONHOST_INTENT.json',{'status':'BEFORE_CONHOST_ACQUISITION','pid':os.getpid(),
            'expected_sha256':CONHOST['sha256'],'initial_size_links_aliases':'UNOBSERVED',
            'directory_access':0x81,'directory_share':3,'file_access':0x80000000,'file_share':1,
            'handles_inheritable':False,'observation_limit':8,'alias_limit':32,'read_limit_bytes':self.profile.FILE_LIMIT})
        row={'status':'ACQUIRING','directories':[],'errors':[]}
        try:
            row['uptime_start_ms']=self.owner.clock();parents=list(reversed(self.path.parents))
            if len(parents)!=3:raise ValueError('exact three conhost ancestors required')
            for path in parents:
                item={'path':str(path)};row['directories'].append(item);item['before']=self.profile.stat_snapshot(path)
                if not self.profile.safe_ancestors([item['before']]):raise ValueError('unsafe conhost ancestor before open')
                handle=self.native.open(str(path),0x81,3,None,3,0x02200000,None)
                if handle==self.native.invalid:raise self.native.win_error('CreateFileW conhost ancestor')
                if not handle:raise ValueError('null conhost ancestor handle')
                entry={'path':path,'handle':handle};self.directories.append(entry)
                item['held']={};self.owner.directory_state(path,handle,item['held']);self.owner.check_directory(item['held'])
                if self.profile.same_api_comparison(item['before'],item['held']['stat'])['equal']is not True:
                    raise ValueError('conhost ancestor changed while opening')
                entry['baseline']=item['held']
            row['target_before_open']=self.profile.stat_snapshot(self.path)
            self.handle=self.native.open(str(self.path),0x80000000,1,None,3,0x00200000,None)
            if self.handle==self.native.invalid:self.handle=None;raise self.native.win_error('CreateFileW conhost')
            if not self.handle:self.handle=None;raise ValueError('null conhost file handle')
            import msvcrt
            self.fd=msvcrt.open_osfhandle(self.handle,os.O_RDONLY);msvcrt.setmode(self.fd,os.O_BINARY)
            self.initial=self.observe('initial-held-image',True)
            if self.profile.same_api_comparison(row['target_before_open'],self.initial['path_before'])['equal']is not True:
                raise ValueError('conhost target changed while opening')
            row['status']='EXACT_CONHOST_IMAGE_HELD';row['uptime_end_ms']=self.owner.clock()
            self.record('CONHOST_ACQUIRE.json',row);return self
        except BaseException as exc:
            row['status']='CONHOST_ADMISSION_REFUSED';row['errors'].append(self.profile.error(exc))
            try:self.record('CONHOST_ACQUIRE.json',row)
            finally:self.close()
            raise
    def observe(self,label,hash_required=False):
        if self.sequence>=8 or self.fd is None or self.handle is None:raise ValueError('conhost observation bound/live handle differs')
        self.sequence+=1
        row={'sequence':self.sequence,'label':label,'path':str(self.path),'errors':[],
             'status':'PARTIAL_CONHOST_OBSERVATION','hash_required':hash_required,'handle_closed':False}
        try:
            row['uptime_start_ms']=self.owner.clock();deadline=min(self.owner.deadline,time.monotonic()+45)
            row['path_before']=self.profile.stat_snapshot(self.path);row['ancestors_before']=self.profile.ancestors(self.path)
            self.directory_snapshots(row,'ancestor_handles_before')
            row['held_before']=self.profile.stat_record(os.fstat(self.fd));row['native_before']=self.native.held_info(self.handle)
            ctypes.set_last_error(0);row['native_file_type']=int(self.native.file_type(self.handle))
            row['native_file_type_last_error']=ctypes.get_last_error();row['native_final_path_before']=self.native.final_path(self.handle)
            size,_=initial_identity(self.profile,row)
            if hash_required:
                os.lseek(self.fd,0,os.SEEK_SET);row['hash']=self.profile.streamed_hash(self.fd,size,deadline)
            row['hardlinks']=self.native.aliases(self.path,deadline)
            row['held_after']=self.profile.stat_record(os.fstat(self.fd));row['native_after']=self.native.held_info(self.handle)
            row['native_final_path_after']=self.native.final_path(self.handle)
            row['path_final']=self.profile.stat_snapshot(self.path);row['ancestors_final']=self.profile.ancestors(self.path)
            self.directory_snapshots(row,'ancestor_handles_after');self.profile.check_time(deadline)
            row['comparisons']=validate_observation(self.profile,row,self.initial,hash_required)
            row['uptime_end_ms']=self.owner.clock();row['status']='HELD_CONHOST_IMAGE_METADATA_MATCH';return row
        except BaseException as exc:row['errors'].append(self.profile.error(exc));raise
        finally:self.record(f'CONHOST_OBSERVATION-{self.sequence:02d}.json',row)
    def image(self):
        if self.initial is None or self.fd is None or self.owner.pid!=os.getpid():raise ValueError('fresh live conhost custody absent')
        return dict(CONHOST)
    def before_worker(self,mode):
        if self.workers>=3 or self.pending is not None or mode!=MODES[self.workers]:raise ValueError('fixed worker order/population differs')
        self.workers+=1;self.pending=mode;self.observe(mode+'-before')
    def after_worker(self,mode):
        if self.pending!=mode:raise ValueError('conhost worker boundary differs')
        self.observe(mode+'-after');self.pending=None
    def finish(self):
        if self.workers!=3 or self.pending is not None:raise ValueError('conhost worker-boundary population incomplete')
        self.observe('terminal-held-image-rehash',True);self.finished=True
    def close(self):
        row={'status':'CLOSING','worker_boundaries_started':self.workers,'pending_worker':self.pending,
            'observations':self.sequence,'terminal_rehash_complete':self.finished,
            'file_handle_closed':None,'directory_handles':[],'errors':[]}
        if self.fd is not None:
            try:os.close(self.fd);row['file_handle_closed']=True
            except OSError as exc:row['file_handle_closed']=False;row['errors'].append(self.profile.error(exc))
            self.fd=None;self.handle=None
        elif self.handle is not None:
            row['file_handle_closed']=bool(self.native.close(self.handle))
            if not row['file_handle_closed']:row['errors'].append(self.profile.error(self.native.win_error('CloseHandle conhost')))
            self.handle=None
        for entry in reversed(self.directories):
            closed=bool(self.native.close(entry['handle']));row['directory_handles'].append({'path':str(entry['path']),'closed':closed})
            if not closed:row['errors'].append(self.profile.error(self.native.win_error('CloseHandle conhost ancestor')))
        self.directories=[];row['status']='ACQUIRED_CONHOST_HANDLES_CLOSED' if not row['errors'] else 'CONHOST_CLEANUP_REFUSAL'
        self.record('CONHOST_CLOSED.json',row);return not row['errors']
    def __exit__(self,kind,value,traceback):
        closed=self.close()
        if kind is None and (not closed or not self.finished):raise ValueError('complete conhost lifetime/cleanup not established')
        return False
