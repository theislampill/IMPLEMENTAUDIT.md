#!/usr/bin/env python3
"""Reviewed capture04 setup functions; main/host-discovery/capture banks omitted.
Only the fixed fresh provider05 selector differs; callers own phase/currentness.
"""
import argparse
import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import subprocess
import sys
import time
import types
import urllib.request
import zipfile
import zlib

UTILITY_SHA256 = '497dc064daa5499b9f14a36b416e4928b2f57639f4a73bde2f9b1f129297c796'
_UTILITY = None
_COMMAND_DEADLINE = None
PROVIDER_ROOT = '/usr/lib/implementaudit-c5-r5-hosted-python312-05-v1'
ANCESTRY_PATHS = {'/usr/bin/python3.12':'HOST_PYTHON','/usr/bin/git':'HOST_GIT','/usr/lib':'PROVIDER_PARENT',PROVIDER_ROOT+'/lib/python3.12/site-packages':'PROVIDER_SITE'}
ANCESTRY_LIMITS = {'checks':4,'components_per_check':16,'encoded_bytes':16384}
_ANCESTRY_CHECKS = []

def need(value, code):
    if not value: raise ValueError(code)

def sha(raw): return hashlib.sha256(raw).hexdigest()

def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()

def selected_wheel(raw, spec):
    need(len(raw)==spec['bytes'] and sha(raw)==spec['sha256'],'WHEEL_BYTES_DIFFER')
    expected={row['name']:row for row in spec['members']}
    need(len(expected)==len(spec['members'])==12,'WHEEL_SELECTION_POPULATION')
    for name in expected:
        path=PurePosixPath(name)
        need(not path.is_absolute() and '..' not in path.parts and '\\' not in name
             and str(path)==name and len(path.parts)==2,'WHEEL_MEMBER_PATH')
    files={}; names=set()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for info in archive.infolist():
            need(info.filename not in names,'WHEEL_DUPLICATE_MEMBER');names.add(info.filename)
            mode=info.external_attr>>16
            if info.is_dir():
                need(info.filename in {'zopfli/','zopfli-0.2.3.post1.dist-info/'}
                     and stat.S_ISDIR(mode),'WHEEL_DIRECTORY_SHAPE')
                continue
            need(info.filename in expected and stat.S_ISREG(mode),'WHEEL_FILE_POPULATION')
            row=expected[info.filename]
            need(info.file_size==row['bytes'] and stat.S_IMODE(mode)==row['mode']
                 and info.file_size<=4*1024**2 and not info.flag_bits&1,'WHEEL_MEMBER_METADATA')
            with archive.open(info) as stream: data=stream.read(row['bytes']+1)
            need(len(data)==row['bytes'] and sha(data)==row['sha256'],'WHEEL_MEMBER_BYTES')
            files[info.filename]=data
    need(set(files)==set(expected),'WHEEL_MEMBER_POPULATION')
    record='zopfli-0.2.3.post1.dist-info/RECORD';seen=set()
    for row in csv.reader(io.StringIO(files[record].decode('utf-8','strict'))):
        need(len(row)==3,'WHEEL_RECORD_SYNTAX');name,digest,size=row
        need(name in files and name not in seen,'WHEEL_RECORD_POPULATION');seen.add(name)
        if name==record: need(digest==size=='','WHEEL_RECORD_SELF')
        else:
            expected_digest='sha256='+base64.urlsafe_b64encode(hashlib.sha256(files[name]).digest()).decode().rstrip('=')
            need(digest==expected_digest and size==str(len(files[name])),'WHEEL_RECORD_DIGEST')
    need(seen==set(files),'WHEEL_RECORD_OMISSION')
    return files

def identity(info):
    return (info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,
            info.st_mtime_ns,info.st_ctime_ns,info.st_uid,info.st_gid)

def read_regular(path,maximum):
    before=os.lstat(path)
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1
         and before.st_size<=maximum,'ORDINARY_BOUNDED_FILE_REQUIRED')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(identity(os.fstat(fd))==identity(before),'FILE_OPEN_CHANGED')
        raw=b''
        while len(raw)<=maximum:
            part=os.read(fd,min(1024**2,maximum+1-len(raw)))
            if not part: break
            raw+=part
        need(len(raw)==before.st_size and identity(os.fstat(fd))==identity(before)
             and identity(os.lstat(path))==identity(before),'FILE_CAPTURE_CHANGED')
        return raw
    finally: os.close(fd)

def retain_ancestry_component(check, component, status):
    need(_ANCESTRY_CHECKS and _ANCESTRY_CHECKS[-1] is check,'ANCESTRY_DIAGNOSTIC_STATE')
    candidate=dict(check,components=check['components']+[component],status=status)
    need(len(candidate['components'])<=ANCESTRY_LIMITS['components_per_check']
         and len(encoded(_ANCESTRY_CHECKS[:-1]+[candidate]))<=ANCESTRY_LIMITS['encoded_bytes'],
         'ANCESTRY_DIAGNOSTIC_BOUND')
    check.update(candidate)

def root_ancestry(path):
    path=Path(path);need(path.is_absolute(),'ABSOLUTE_PATH_REQUIRED')
    role=ANCESTRY_PATHS.get(str(path));need(role is not None,'ANCESTRY_SELECTION_REFUSED')
    parts=tuple(reversed((path,*path.parents)))
    need(len(_ANCESTRY_CHECKS)<ANCESTRY_LIMITS['checks']
         and len(parts)<=ANCESTRY_LIMITS['components_per_check'],'ANCESTRY_DIAGNOSTIC_BOUND')
    check={'role':role,'target':str(path),'status':'CHECKING','components':[]}
    need(len(encoded(_ANCESTRY_CHECKS+[check]))<=ANCESTRY_LIMITS['encoded_bytes'],'ANCESTRY_DIAGNOSTIC_BOUND')
    _ANCESTRY_CHECKS.append(check)
    for index,part in enumerate(parts):
        try: info=part.lstat()
        except OSError as exc:
            number=exc.errno if type(exc.errno) is int and 0<=exc.errno<=4095 else None
            retain_ancestry_component(check,{'path':str(part),'status':'LSTAT_UNAVAILABLE','errno':number},'UNAVAILABLE')
            raise
        # The eligibility predicate is unchanged. Diagnostics retain only the
        # actual fixed-path lstat fields and closed, mechanically derived facts.
        trusted=(info.st_uid==info.st_gid==0 and not info.st_mode&0o022
                 and not stat.S_ISLNK(info.st_mode))
        kind=('DIRECTORY' if stat.S_ISDIR(info.st_mode) else 'REGULAR' if stat.S_ISREG(info.st_mode)
              else 'SYMLINK' if stat.S_ISLNK(info.st_mode) else 'OTHER')
        component={'path':str(part),'status':'OBSERVED','identity':list(identity(info)),
            'uid':info.st_uid,'gid':info.st_gid,'mode':stat.S_IMODE(info.st_mode),'kind':kind,
            'predicates':{'uid_zero':info.st_uid==0,'gid_zero':info.st_gid==0,
                'group_other_not_writable':not bool(info.st_mode&0o022),'not_symlink':not stat.S_ISLNK(info.st_mode)},
            'trusted':trusted}
        status='REFUSED' if not trusted else 'TRUSTED' if index==len(parts)-1 else 'CHECKING'
        retain_ancestry_component(check,component,status)
        need(trusted,'TRUSTED_ROOT_ANCESTRY_REQUIRED')

def load_utility():
    global _UTILITY
    if _UTILITY is None:
        path=Path(__file__).with_name('host_utility.py')
        raw=read_regular(path,65536);need(sha(raw)==UTILITY_SHA256,'UTILITY_PIN_DIFFERS')
        module=types.ModuleType('selected_owned_child_utility');module.__file__=str(path)
        exec(compile(raw,str(path),'exec'),module.__dict__)
        _UTILITY=module
    return _UTILITY

def enable_subreaper():
    u=load_utility();lib=u.ctypes.CDLL(None,use_errno=True);actual=u.ctypes.c_int()
    need(lib.prctl(36,1,0,0,0)==0
         and lib.prctl(37,u.ctypes.byref(actual),0,0,0)==0
         and actual.value==1,'SUBREAPER_REFUSED')

def command(argv, *, cwd='/', seconds=60, maximum=32768):
    # This is the sole child-owning adapter. Reuse the exact bank03 capture and
    # terminal-first pidfd/ECHILD cleanup; never call its context or probe bank.
    need(cwd=='/' and type(maximum) is int and maximum>0,'COMMAND_SELECTION')
    u=load_utility();records=[];began=time.monotonic();error=None;stdout=stderr=b'';rc=None
    previous=os.getcwd();deadline=_COMMAND_DEADLINE or began+seconds+1
    try:
        os.chdir(cwd)
        try: rc,stdout,stderr=u.capture('input-capture',argv,records,deadline,seconds=seconds)
        except BaseException as exc:
            error=type(exc).__name__
            captured=getattr(exc,'captured',{})
            stdout=captured.get('stdout',b'');stderr=captured.get('stderr',b'')
            rc=captured.get('returncode')
    finally: os.chdir(previous)
    record=records[-1] if records else {}
    rc=record.get('returncode',rc)
    overflow=record.get('output_bound_exceeded',False) or len(stdout)>maximum or len(stderr)>maximum
    cleanup=record.get('cleanup',{})
    row={'exit_code':rc,'elapsed_seconds':time.monotonic()-began,
         'timed_out':record.get('timeout',False),'overflow':overflow,
         'primary_reaped':record.get('process_started',False) and rc is not None,
         'all_owned_children_reaped':cleanup.get('echild',False),
         'stream_bytes':{'stdout':record.get('stdout_bytes',len(stdout)),
                         'stderr':record.get('stderr_bytes',len(stderr))},
         'stream_sha256':{'stdout':record.get('stdout_sha256',sha(stdout)),
                          'stderr':record.get('stderr_sha256',sha(stderr))},
         'exception_type':error,'capture':record,'utility_sha256':UTILITY_SHA256}
    row['complete']=(error is None and not overflow and not row['timed_out']
        and row['primary_reaped'] and row['all_owned_children_reaped']
        and record.get('streams_complete',False) and record.get('internal_failure') is None)
    return row,stdout[:maximum],stderr[:maximum]

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): raise ValueError('WHEEL_REDIRECT_REFUSED')

def fetch_wheel(spec):
    opener=urllib.request.build_opener(NoRedirect())
    with opener.open(spec['url'],timeout=30) as response:
        need(response.status==200 and response.geturl()==spec['url'],'WHEEL_HTTP_REFUSED')
        raw=response.read(spec['bytes']+1)
    return selected_wheel(raw,spec)

def allocate_provider(spec,commands):
    root=Path(spec['new_provider_root']);root_ancestry(root.parent)
    need(not root.exists() and not root.is_symlink(),'PROVIDER_ALREADY_EXISTS')
    root.mkdir(mode=0o755,exist_ok=False)
    row,_,_=command(['/usr/bin/python3.12','-I','-S','-B','-m','venv','--without-pip','--copies',str(root)],seconds=60)
    commands.append(dict(operation='VENV_WITHOUT_PIP',**row));need(row['complete'] and row['exit_code']==0,'VENV_CREATION_REFUSED')
    files=fetch_wheel(spec['wheel']);site=root/'lib/python3.12/site-packages'
    root_ancestry(site)
    need(list(site.iterdir())==[],'FRESH_SITE_NOT_EMPTY')
    for name in ('zopfli','zopfli-0.2.3.post1.dist-info'): (site/name).mkdir(mode=0o755,exist_ok=False)
    record='zopfli-0.2.3.post1.dist-info/RECORD'
    files['zopfli-0.2.3.post1.dist-info/INSTALLER']=b'implementaudit-r5-hosted-fixed-wheel-v1\n'
    files['zopfli-0.2.3.post1.dist-info/REQUESTED']=b''
    stream=io.StringIO(newline='');writer=csv.writer(stream,lineterminator='\n')
    for name in sorted(files):
        raw=files[name]
        writer.writerow((name,'','') if name==record else
            (name,'sha256='+base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode().rstrip('='),str(len(raw))))
    files[record]=stream.getvalue().encode()
    selected_modes={row['name']:row['mode'] for row in spec['wheel']['members']}
    for name,raw in sorted(files.items()):
        # The downloaded wheel's RECORD has group-write permissions. New
        # installed data uses the explicit ordinary 0644 policy instead.
        mode=0o755 if selected_modes.get(name)==0o755 else 0o644
        fd=os.open(site/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
        with os.fdopen(fd,'wb') as out: out.write(raw)
        need(read_regular(site/name,len(raw))==raw,'PROVIDER_WRITE_READBACK')
    return root
