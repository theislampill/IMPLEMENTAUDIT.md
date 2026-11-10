#!/usr/bin/env python3
"""One prospective hosted Linux primitive discrimination; no owner acceptance.

Import is inert. --run is guarded to the single declared hosted push context.
Only --emit-public reads a completed public packet. No install or fallback.
"""
import argparse
import ctypes
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import signal
import socket
import stat
import subprocess
import sys
import time

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg16-r5-linux-host-03-20261105'
SOURCE_COMMIT = 'e61ead4284e8c8a58948fb9c0b128fd933482d69'
SOURCE_TREE = '1df9ff643f5b5564ebb6b17c51254f4e9faf4b7a'
SOURCE_FILE = 'scripts/work-graph-continuity-transport.py'
SOURCE_SHA256 = 'aa98b1a45b9345d3ccf88611a7b90cd2939e04ee3f520b82610546ba96b77d48'
PUBLIC_NAMES = ('RESULT.json', 'HOST.json', 'SOURCE.json', 'PROBE.json',
                'CLEANUP.json', 'FAILURE.json', 'ARTIFACT_MANIFEST.json')
FILE_LIMIT, TOTAL_LIMIT = 65536, 262144
LINE_LIMIT, LOG_LIMIT = 262144, 1048576
PREFIX = 'DG16_LINUX_HOST_JSON '
RUN_SECONDS, PROBE_SECONDS, COMMAND_SECONDS = 45, 15, 4
CANARY = b'DG16 owned read-only image canary v1\n'
OUTSIDE = b'DG16 owned outside sentinel v1\n'
WORK = b'DG16 owned sole work mount v1\n'
CHILD_CHECKS = ('namespaces_distinct', 'image_read', 'image_mount_ro', 'root_mount_ro', 'proc_mount_ro',
                'only_declared_writable_mounts', 'no_inherited_extra_fds',
                'work_mount_rw', 'image_append_denied', 'image_create_denied',
                'image_rename_denied', 'image_unlink_denied', 'sealed_source_read',
                'sealed_source_linked', 'sealed_source_write_denied', 'work_roundtrip',
                'outside_direct_denied', 'outside_symlink_denied', 'outside_proc_denied',
                'caps_dropped', 'no_new_privileges', 'remount_denied',
                'host_loopback_unreachable', 'no_external_route')

# Fixed trusted payload. It never forks or invokes a program/model/owner helper.
CHILD = r'''import errno,fcntl,hashlib,json,os,pathlib,socket,stat,sys
r=json.loads(sys.argv[1]); c={}; e={}
def describe_descriptors(primary, listed_count, inherited, anchors):
    # Metadata only. Identity matches classify owned objects; they grant no exception.
    limit=16
    def number(value):return value if type(value) is int and 0<=value<=4096 else None
    def identity(info):return (info.st_dev,info.st_ino,stat.S_IFMT(info.st_mode))
    references={name:tuple(anchors[name]) for name in ('sealed_memfd','image_root','work_root')}
    source_error=None
    try:references['linked_source']=identity(os.stat('/sealed/probe.py'))
    except OSError as exc:references['linked_source']=None;source_error=number(exc.errno)
    def fact(info, error):
        if info is None:
            return {'live':False,'errno':number(error),'kind':'UNAVAILABLE',
                    'owned_matches':dict.fromkeys(('linked_source','sealed_memfd','image_root','work_root'),None)}
        kinds=((stat.S_ISREG,'REGULAR'),(stat.S_ISDIR,'DIRECTORY'),(stat.S_ISCHR,'CHARACTER'),
               (stat.S_ISBLK,'BLOCK'),(stat.S_ISFIFO,'FIFO'),(stat.S_ISSOCK,'SOCKET'))
        return {'live':True,'errno':None,'kind':next((name for test,name in kinds if test(info.st_mode)),'OTHER'),
                'owned_matches':{name:identity(info)==reference if reference is not None else None
                                 for name,reference in references.items()}}
    rows=[]
    for descriptor,first,first_error in sorted(primary,key=lambda item:item[0]):
        try:later=os.fstat(descriptor);later_error=None
        except OSError as exc:later=None;later_error=number(exc.errno)
        after=fact(later,later_error)
        after['same_as_primary']=identity(first)==identity(later) if first is not None and later is not None else None
        for key,command in (('fd_flags',fcntl.F_GETFD),('status_flags',fcntl.F_GETFL)):
            after[key]=None;after[key+'_errno']=None
            if later is not None:
                try:after[key]=fcntl.fcntl(descriptor,command)
                except OSError as exc:after[key+'_errno']=number(exc.errno)
        rows.append({'fd':descriptor,'primary':fact(first,first_error),'followup':after})
    live=set(inherited)
    return {'schema':'dg16.linux-fd-observation.v1','sample_limit':limit,'non_atomic':True,
            'listed_count':listed_count,'live_count':len(live),'live_sample':sorted(live)[:limit],
            'missing_standard_fds':sorted({0,1,2}-live),'sample_truncated':listed_count>limit,
            'source_reference':{'available':references['linked_source'] is not None,'errno':source_error},'rows':rows}
def deny(name,call,allowed):
    try: call()
    except OSError as x: e[name]=x.errno;c[name]=x.errno in allowed
    else: c[name]=False
def append(path):
    with open(path,'ab') as f:f.write(b'UNEXPECTED_WRITE')
def create(path):
    with open(path,'xb') as f:f.write(b'UNEXPECTED_CREATE')
ns={k:os.stat('/proc/self/ns/'+k).st_ino for k in ('user','mnt','net','pid')}
c['namespaces_distinct']=all(ns[k]!=r['parent_ns'][k] for k in ns)
image=pathlib.Path('/image');work=pathlib.Path('/work')
c['image_read']=hashlib.sha256((image/'canary').read_bytes()).hexdigest()==r['canary_sha256']
mounts={};writable=[]
for line in pathlib.Path('/proc/self/mountinfo').read_text().splitlines():
    fields=line.split()
    if len(fields)>6:
        options=fields[5].split(',')
        if fields[4] in ('/','/image','/work','/proc'):mounts[fields[4]]=options
        if 'rw' in options:writable.append(fields[4])
c['image_mount_ro']='ro' in mounts.get('/image',[])
c['root_mount_ro']='ro' in mounts.get('/',[])
c['proc_mount_ro']='ro' in mounts.get('/proc',[])
c['work_mount_rw']='rw' in mounts.get('/work',[])
c['only_declared_writable_mounts']='/work' in writable and set(writable)<=set(('/work','/dev/null'))
ctypes_import_boundary={'schema':'dg16.linux-ctypes-import-boundary.v1',
                        'absent_before_primary_census':'ctypes' not in sys.modules}
if not ctypes_import_boundary['absent_before_primary_census']:
    raise RuntimeError('CTYPES_PREIMPORTED_BEFORE_PRIMARY_CENSUS')
inherited=[];descriptor_primary=[];descriptor_names=os.listdir('/proc/self/fd')
for descriptor in descriptor_names:
    try:info=os.fstat(int(descriptor))
    except OSError as exc:
        if len(descriptor_primary)<16:descriptor_primary.append((int(descriptor),None,exc.errno))
        continue
    inherited.append(int(descriptor))
    if len(descriptor_primary)<16:descriptor_primary.append((int(descriptor),info,None))
c['no_inherited_extra_fds']=set(inherited)=={0,1,2}
fd_observation=describe_descriptors(descriptor_primary,len(descriptor_names),inherited,r['fd_anchors'])
deny('image_append_denied',lambda:append(image/'canary'),{errno.EROFS})
deny('image_create_denied',lambda:create(image/'new'),{errno.EROFS})
deny('image_rename_denied',lambda:os.rename(image/'canary',image/'renamed'),{errno.EROFS})
deny('image_unlink_denied',lambda:os.unlink(image/'canary'),{errno.EROFS})
sealed=pathlib.Path('/sealed/probe.py')
c['sealed_source_read']=hashlib.sha256(sealed.read_bytes()).hexdigest()==r['child_sha256']
c['sealed_source_linked']=sealed.stat().st_nlink==1
deny('sealed_source_write_denied',lambda:append(sealed),{errno.EROFS})
payload=b'DG16 owned sole work mount v1\n'
(work/'result').write_bytes(payload)
c['work_roundtrip']=(work/'result').read_bytes()==payload
absent={errno.ENOENT,errno.ENOTDIR,errno.EACCES,errno.EPERM,errno.EROFS}
deny('outside_direct_denied',lambda:append(r['outside']),absent)
os.symlink(r['outside'],work/'escape')
deny('outside_symlink_denied',lambda:append(work/'escape'),absent)
deny('outside_proc_denied',lambda:append('/proc/'+str(r['parent_pid'])+'/root'+r['outside']),absent)
status={}
for line in pathlib.Path('/proc/self/status').read_text().splitlines():
    if ':' in line:
        k,v=line.split(':',1)
        if k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs'):status[k]=v.strip()
c['caps_dropped']=all(int(status.get(k,'1'),16)==0 for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb'))
c['no_new_privileges']=status.get('NoNewPrivs')=='1'
ctypes_import_boundary['absent_before_delayed_import']='ctypes' not in sys.modules
if not ctypes_import_boundary['absent_before_delayed_import']:
    raise RuntimeError('CTYPES_PREIMPORTED_BEFORE_DELAYED_IMPORT')
import ctypes
post_ctypes_inherited=[];post_ctypes_descriptor_primary=[];post_ctypes_descriptor_names=os.listdir('/proc/self/fd')
for descriptor in post_ctypes_descriptor_names:
    try:info=os.fstat(int(descriptor))
    except OSError as exc:
        if len(post_ctypes_descriptor_primary)<16:post_ctypes_descriptor_primary.append((int(descriptor),None,exc.errno))
        continue
    post_ctypes_inherited.append(int(descriptor))
    if len(post_ctypes_descriptor_primary)<16:post_ctypes_descriptor_primary.append((int(descriptor),info,None))
fd_observation_after_ctypes_import=describe_descriptors(post_ctypes_descriptor_primary,len(post_ctypes_descriptor_names),post_ctypes_inherited,r['fd_anchors'])
ctypes_import_boundary['present_after_delayed_import']='ctypes' in sys.modules
if not ctypes_import_boundary['present_after_delayed_import']:
    raise RuntimeError('CTYPES_IMPORT_NOT_RECORDED')
libc=ctypes.CDLL(None,use_errno=True)
libc.mount.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_ulong,ctypes.c_void_p]
rc=libc.mount(None,b'/image',None,32|4096,None);e['remount_denied']=ctypes.get_errno()
c['remount_denied']=rc==-1 and e['remount_denied'] in (errno.EPERM,errno.EACCES)
with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.settimeout(0.5)
    try:s.connect(('127.0.0.1',r['port']))
    except OSError as x:
        e['host_loopback_unreachable']=x.errno if x.errno is not None else 0
        c['host_loopback_unreachable']=x.errno in (errno.ECONNREFUSED,errno.ENETUNREACH,errno.ENETDOWN,errno.EHOSTUNREACH,errno.EACCES,errno.EPERM)
    else:c['host_loopback_unreachable']=False
routes=pathlib.Path('/proc/net/route').read_text().splitlines()[1:]
c['no_external_route']=all(line.split()[0]=='lo' for line in routes if line.strip())
out={'schema':'dg16.linux-host-child.v3','checks':c,'errno':e,'namespace_inodes':ns,'capabilities':status,'mount_flags':mounts,'descriptor_observation':fd_observation,'descriptor_observation_after_ctypes_import':fd_observation_after_ctypes_import,'ctypes_import_boundary':ctypes_import_boundary}
print(json.dumps(out,sort_keys=True,separators=(',',':'),ensure_ascii=True))
sys.exit(0 if all(c.values()) else 1)
'''

class Refusal(Exception):
    pass

def require(condition, code):
    if not condition:
        raise Refusal(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False)+'\n').encode('ascii')

def unique_pairs(pairs):
    d = {}
    for k, v in pairs:
        require(k not in d, 'DUPLICATE_JSON_KEY')
        d[k] = v
    return d

def parse_json(raw):
    def reject(_):
        raise Refusal('NONFINITE_JSON')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique_pairs, parse_constant=reject)

def token(value, maximum=80):
    require(type(value) is str and re.fullmatch(r'[A-Za-z0-9_.:+~/=-]{1,'+str(maximum)+'}', value), 'UNSAFE_IDENTITY_TOKEN')
    return value

def checked_file(path, maximum=64*1024*1024, single_link=True):
    path = Path(path)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and (not single_link or before.st_nlink == 1)
            and before.st_size <= maximum, 'FILE_SHAPE_REFUSED')
    with path.open('rb') as stream:
        raw = stream.read(maximum+1)
    after = path.lstat()
    require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==
            (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns) and len(raw)<=maximum, 'FILE_CHANGED')
    return raw

def trusted(name):
    requested = Path('/usr/bin')/name
    try:
        path = requested.resolve(strict=True)
        require(path.is_file() and os.access(path,os.X_OK), 'TOOL_NOT_EXECUTABLE')
        for item in (path,*path.parents):
            info = item.lstat()
            require(info.st_uid==0 and not info.st_mode & 0o022, 'TOOL_CUSTODY_REFUSED')
        info = path.stat()
        require(not info.st_mode & 0o6000, 'PRIVILEGED_TOOL_REFUSED')
        try: cap = os.getxattr(path,'security.capability')
        except OSError as exc:
            require(exc.errno in (errno.ENODATA,errno.ENOTSUP), 'TOOL_CAPABILITY_UNKNOWN')
            cap = b''
        require(not cap, 'PRIVILEGED_TOOL_REFUSED')
        raw = checked_file(path, single_link=False)
        return str(path), {'available':True,'requested':'/usr/bin/'+name,'canonical':str(path),
                           'bytes':len(raw),'sha256':sha(raw),'root_owned_nonwritable_chain':True,
                           'setid_or_file_capabilities':False}
    except (OSError,Refusal) as exc:
        code=str(exc) if isinstance(exc,Refusal) else 'TOOL_OS_REFUSAL'
        return None, {'available':False,'requested':'/usr/bin/'+name,'code':code,
                      'errno':getattr(exc,'errno',None)}

def numeric_file(path):
    try:
        raw = checked_file(path,256).decode('ascii').strip()
        require(re.fullmatch(r'[0-9]{1,16}',raw), 'NUMERIC_FACT_REFUSED')
        return {'readable':True,'value':int(raw)}
    except (OSError,Refusal,UnicodeError):
        return {'readable':False}

def fd_observation_valid(value, predicate):
    keys={'schema','sample_limit','non_atomic','listed_count','live_count','live_sample',
          'missing_standard_fds','sample_truncated','source_reference','rows'}
    require(type(value) is dict and set(value)==keys,'FD_OBSERVATION_SHAPE_REFUSED')
    require(value['schema']=='dg16.linux-fd-observation.v1' and type(value['sample_limit']) is int
            and value['sample_limit']==16 and value['non_atomic'] is True,'FD_OBSERVATION_SCHEMA_REFUSED')
    descriptor_max=2**31-1
    def integer(number,maximum=descriptor_max):return type(number) is int and 0<=number<=maximum
    def error(number):return number is None or integer(number,4096)
    def numbers(items,maximum_count):
        return (type(items) is list and len(items)<=maximum_count and all(integer(number) for number in items)
                and items==sorted(set(items)))
    require(integer(value['listed_count']) and integer(value['live_count'])
            and value['live_count']<=value['listed_count'],'FD_COUNT_REFUSED')
    live=value['live_sample'];missing=value['missing_standard_fds']
    require(numbers(live,16) and len(live)==min(16,value['live_count'])
            and numbers(missing,3) and missing==sorted({0,1,2}-set(live)),'FD_SAMPLE_REFUSED')
    require(type(value['sample_truncated']) is bool
            and value['sample_truncated']==(value['listed_count']>16),'FD_TRUNCATION_REFUSED')
    reference=value['source_reference']
    require(type(reference) is dict and set(reference)=={'available','errno'}
            and type(reference['available']) is bool and error(reference['errno'])
            and (not reference['available'] or reference['errno'] is None),'FD_REFERENCE_REFUSED')
    rows=value['rows'];require(type(rows) is list and len(rows)==min(16,value['listed_count']),'FD_ROWS_REFUSED')
    kinds={'REGULAR','DIRECTORY','CHARACTER','BLOCK','FIFO','SOCKET','OTHER','UNAVAILABLE'}
    anchors={'linked_source','sealed_memfd','image_root','work_root'}
    fact_keys={'live','errno','kind','owned_matches'}
    followup_keys=fact_keys|{'same_as_primary','fd_flags','fd_flags_errno','status_flags','status_flags_errno'}
    def fact(item, followup):
        require(type(item) is dict and set(item)==(followup_keys if followup else fact_keys),'FD_FACT_SHAPE_REFUSED')
        require(type(item['live']) is bool and error(item['errno']) and type(item['kind']) is str
                and item['kind'] in kinds,'FD_FACT_VALUE_REFUSED')
        require((item['kind']!='UNAVAILABLE' and item['errno'] is None) if item['live']
                else item['kind']=='UNAVAILABLE','FD_FACT_STATE_REFUSED')
        matches=item['owned_matches']
        require(type(matches) is dict and set(matches)==anchors,'FD_OWNED_MATCH_SHAPE_REFUSED')
        for name,matched in matches.items():
            if not item['live'] or (name=='linked_source' and not reference['available']):
                require(matched is None,'FD_UNAVAILABLE_MATCH_REFUSED')
            else:require(type(matched) is bool,'FD_OWNED_MATCH_VALUE_REFUSED')
            if matched is True:
                require(item['kind']==('REGULAR' if name in ('linked_source','sealed_memfd') else 'DIRECTORY'),
                        'FD_OWNED_MATCH_KIND_REFUSED')
        if followup:
            for key in ('fd_flags','status_flags'):
                require((item[key] is None or integer(item[key],2**32-1)) and error(item[key+'_errno']),
                        'FD_FLAGS_REFUSED')
                require(item[key] is None or item[key+'_errno'] is None,'FD_FLAG_STATE_REFUSED')
                if not item['live']:require(item[key] is None and item[key+'_errno'] is None,'FD_ABSENT_FLAGS_REFUSED')
    identifiers=[];primary_live=[]
    for row in rows:
        require(type(row) is dict and set(row)=={'fd','primary','followup'} and integer(row['fd']),'FD_ROW_REFUSED')
        identifiers.append(row['fd']);fact(row['primary'],False);fact(row['followup'],True)
        first=row['primary'];later=row['followup']
        if first['live']:primary_live.append(row['fd'])
        if first['live'] and later['live']:
            require(type(later['same_as_primary']) is bool,'FD_IDENTITY_STATE_REFUSED')
            if later['same_as_primary']:
                require(first['kind']==later['kind'] and first['owned_matches']==later['owned_matches'],'FD_IDENTITY_CONTRADICTION')
            if any(first['owned_matches'][name] is True and later['owned_matches'][name] is True for name in anchors):
                require(later['same_as_primary'] is True,'FD_COMMON_ANCHOR_IDENTITY_CONTRADICTION')
        else:require(later['same_as_primary'] is None,'FD_IDENTITY_UNAVAILABLE_REFUSED')
    require(identifiers==sorted(set(identifiers)),'FD_ROW_POPULATION_REFUSED')
    require(len(primary_live)<=value['live_count'] and set(live).intersection(identifiers)<=set(primary_live)
            and all(number in live or (value['live_count']>16 and number>live[-1]) for number in primary_live),
            'FD_SAMPLED_SUMMARY_CONTRADICTION')
    require(len(set(primary_live)|set(live))<=value['live_count']
            <=len(primary_live)+value['listed_count']-len(identifiers),'FD_CENSUS_CARDINALITY_CONTRADICTION')
    if value['live_count']>len(live):
        unavailable_above=sum(row['fd']>live[-1] and not row['primary']['live'] for row in rows)
        require(value['live_count']-len(live)<=descriptor_max-live[-1]-unavailable_above,
                'FD_TAIL_CAPACITY_CONTRADICTION')
    if not value['sample_truncated']:
        require(primary_live==live and len(primary_live)==value['live_count'],'FD_COMPLETE_POPULATION_REFUSED')
    require(predicate is (value['live_count']==3 and live==[0,1,2]),'FD_PREDICATE_CONTRADICTION')
    return value

def child_valid(value):
    require(type(value) is dict and set(value)=={'schema','checks','errno','namespace_inodes','capabilities','mount_flags','descriptor_observation','descriptor_observation_after_ctypes_import','ctypes_import_boundary'}, 'CHILD_SHAPE_REFUSED')
    require(value['schema']=='dg16.linux-host-child.v3', 'CHILD_SCHEMA_REFUSED')
    require(type(value['checks']) is dict and set(value['checks'])==set(CHILD_CHECKS)
            and all(type(x) is bool for x in value['checks'].values()), 'CHILD_CHECK_POPULATION_REFUSED')
    require(type(value['errno']) is dict and set(value['errno'])<=set(CHILD_CHECKS)
            and all(type(x) is int and 0<=x<=4096 for x in value['errno'].values()), 'CHILD_ERRNO_REFUSED')
    require(type(value['namespace_inodes']) is dict and set(value['namespace_inodes'])=={'user','mnt','net','pid'}
            and all(type(x) is int and 0<x<2**64 for x in value['namespace_inodes'].values()), 'CHILD_NAMESPACE_REFUSED')
    require(type(value['capabilities']) is dict and set(value['capabilities'])=={'CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs'}
            and all(type(x) is str and re.fullmatch('[0-9a-f]{1,16}',x) for x in value['capabilities'].values()), 'CHILD_CAPS_REFUSED')
    require(type(value['mount_flags']) is dict and set(value['mount_flags'])=={'/','/image','/work','/proc'}, 'CHILD_MOUNTS_REFUSED')
    for flags in value['mount_flags'].values():
        require(type(flags) is list and 1<=len(flags)<=16 and all(type(x) is str and re.fullmatch('[a-z0-9_=.-]{1,40}',x) for x in flags), 'CHILD_FLAGS_REFUSED')
    fd_observation_valid(value['descriptor_observation'],value['checks']['no_inherited_extra_fds'])
    boundary=value['ctypes_import_boundary']
    require(type(boundary) is dict and set(boundary)=={'schema','absent_before_primary_census',
            'absent_before_delayed_import','present_after_delayed_import'},'CTYPES_IMPORT_BOUNDARY_SHAPE_REFUSED')
    require(boundary['schema']=='dg16.linux-ctypes-import-boundary.v1'
            and boundary['absent_before_primary_census'] is True
            and boundary['absent_before_delayed_import'] is True
            and boundary['present_after_delayed_import'] is True,'CTYPES_IMPORT_BOUNDARY_REFUSED')
    # Reuse the strict schema validator; this derived flag is diagnostic only.
    after=value['descriptor_observation_after_ctypes_import']
    fd_observation_valid(after,type(after) is dict and after.get('live_count')==3 and after.get('live_sample')==[0,1,2])
    return value

def transport_lines(files):
    """Pure, all-or-nothing encoding; same receiving rule as reviewed Windows path."""
    require(set(files)==set(PUBLIC_NAMES), 'PUBLIC_POPULATION_REFUSED')
    rows=[];total=0
    for name in sorted(files):
        raw=files[name];require(type(raw) is bytes and len(raw)<=FILE_LIMIT,'PUBLIC_FILE_BOUND')
        total+=len(raw);require(total<=TOTAL_LIMIT,'PUBLIC_TOTAL_BOUND');parse_json(raw)
        rows.append({'name':name,'bytes':len(raw),'sha256':sha(raw),'utf8_json':raw.decode('utf-8')})
    manifest=parse_json(files['ARTIFACT_MANIFEST.json'])
    require(type(manifest) is dict and set(manifest)=={'schema','members'} and manifest['schema']=='dg16.linux-host-artifacts.v1','PUBLIC_MANIFEST_SHAPE')
    expected={}
    for row in manifest['members']:
        require(type(row) is dict and set(row)=={'name','bytes','sha256'} and row['name'] not in expected,'PUBLIC_MANIFEST_MEMBER')
        require(row['name'] in PUBLIC_NAMES and row['name']!='ARTIFACT_MANIFEST.json'
                and type(row['bytes']) is int and 0<=row['bytes']<=FILE_LIMIT
                and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['sha256']),'PUBLIC_MANIFEST_VALUE')
        expected[row['name']]=(row['bytes'],row['sha256'])
    actual={r['name']:(r['bytes'],r['sha256']) for r in rows if r['name']!='ARTIFACT_MANIFEST.json'}
    require(expected==actual,'PUBLIC_MANIFEST_MISMATCH')
    lines=[PREFIX+json.dumps(row,ensure_ascii=True,separators=(',',':')) for row in rows]
    lengths=[len(line.encode('ascii'))+2 for line in lines]
    require(all(n<=LINE_LIMIT for n in lengths) and sum(lengths)<=LOG_LIMIT,'PUBLIC_ENCODED_BOUND')
    return lines

def emit_public(output):
    public=Path(output)/'public'
    require(public.resolve(strict=True)==public and public.is_dir(),'PUBLIC_DIRECTORY_REFUSED')
    require({p.name for p in public.iterdir()}==set(PUBLIC_NAMES),'PUBLIC_POPULATION_REFUSED')
    files={name:checked_file(public/name,FILE_LIMIT) for name in PUBLIC_NAMES}
    for line in transport_lines(files):
        print(line,flush=True)

def safe_environment():
    return {'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1',
            'GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null','GIT_CONFIG_NOSYSTEM':'1',
            'GIT_TERMINAL_PROMPT':'0','GIT_OPTIONAL_LOCKS':'0','GIT_NO_LAZY_FETCH':'1',
            'GIT_NO_REPLACE_OBJECTS':'1','GIT_CONFIG_COUNT':'3','GIT_CONFIG_KEY_0':'core.hooksPath',
            'GIT_CONFIG_VALUE_0':'/dev/null','GIT_CONFIG_KEY_1':'core.fsmonitor','GIT_CONFIG_VALUE_1':'false',
            'GIT_CONFIG_KEY_2':'protocol.allow','GIT_CONFIG_VALUE_2':'never'}

def context(output, source):
    e=os.environ
    require(e.get('GITHUB_ACTIONS')=='true' and e.get('GITHUB_REPOSITORY')==REPOSITORY
            and e.get('GITHUB_EVENT_NAME')=='push' and e.get('GITHUB_REF')=='refs/heads/'+BRANCH
            and e.get('GITHUB_RUN_ATTEMPT')=='1','EVENT_GUARD_REFUSED')
    run=e.get('GITHUB_RUN_ID','');require(re.fullmatch('[0-9]{1,20}',run),'RUN_ID_REFUSED')
    commit=e.get('GITHUB_SHA','');require(re.fullmatch('[0-9a-f]{40}',commit),'WORKFLOW_COMMIT_REFUSED')
    temp=Path(e.get('RUNNER_TEMP','')).resolve(strict=True)
    workspace=Path(e.get('GITHUB_WORKSPACE','')).resolve(strict=True)
    require(Path(output).absolute()==temp/('dg16-linux-host-'+run+'-1'),'OUTPUT_PATH_REFUSED')
    require(Path(source).absolute()==workspace/'qualified-source','SOURCE_PATH_REFUSED')
    require(Path(source).resolve(strict=True)==Path(source).absolute(),'SOURCE_DIRECTORY_REFUSED')
    require(not Path(output).exists(),'NO_RETRY_OUTPUT_EXISTS')
    return {'repository':REPOSITORY,'branch':BRANCH,'event':'push','run_id':run,'run_attempt':1,'workflow_commit':commit}

def children():
    raw=Path('/proc/self/task/'+str(os.getpid())+'/children').read_text().strip()
    numeric=not raw or re.fullmatch(r'[0-9 ]+',raw) is not None
    census={'captured_bytes':len(raw.encode('ascii','replace')),'captured_sha256':sha(raw.encode('ascii','replace')),
            'numeric_shape':numeric,'observed_tokens':len(raw.split()) if numeric else None,
            'text_bound':160,'live_population_bound':8}
    try:
        require(not raw or re.fullmatch(r'[0-9 ]{1,160}',raw),'CHILD_CUSTODY_REFUSED')
        ids=[int(x) for x in raw.split()];require(len(ids)<=8,'CHILD_POPULATION_BOUND')
        return ids
    except Refusal as exc:
        exc.census=census
        raise

def stop_owned_children():
    """Reap owned terminal children before the unchanged bounded live census.

    The 4096 terminal-status bound and Linux __WALL child-wait scope match the
    maintained whole-capture owner's quiescent discipline. Neither enlarges the
    eight-live-child/160-character census or grants foreign-child authority.
    """
    end=time.monotonic()+4;signals_sent=0;reaped=[]
    def result(echild):
        return {'echild':echild,'pidfd_signals':signals_sent,'reaped_statuses':reaped}
    try:
        while time.monotonic()<end:
            while time.monotonic()<end:
                try:pid,status=os.waitpid(-1,os.WNOHANG|0x40000000)
                except ChildProcessError:return result(True)
                if not pid:break
                require(len(reaped)<4096,'CHILD_REAP_POPULATION_BOUND')
                require(os.WIFEXITED(status) or os.WIFSIGNALED(status),'CHILD_WAIT_STATUS_REFUSED')
                reaped.append({'pid':pid,'returncode':os.waitstatus_to_exitcode(status)})
            if time.monotonic()>=end:break
            for pid in children():
                try:
                    fd=os.pidfd_open(pid)
                    try:
                        # Holding the PID identity never replaces parent custody.
                        require(pid in children(),'CHILD_CUSTODY_CHANGED')
                        signal.pidfd_send_signal(fd,signal.SIGKILL);signals_sent+=1
                    finally:os.close(fd)
                except ProcessLookupError:pass
            time.sleep(0.01)
        return result(False)
    except BaseException as exc:
        exc.cleanup_partial=result(False)
        raise

def public_cleanup(cleanup):
    rows=cleanup['reaped_statuses']
    result={'echild':cleanup['echild'],'pidfd_signals':cleanup.get('pidfd_signals',0),
            'retained_status_count':len(rows),'retained_statuses_sha256':sha(canonical(rows)),
            'reaped_statuses':rows[:8],'reaped_statuses_truncated':len(rows)>8}
    if 'code' in cleanup:result['code']=cleanup['code']
    if 'census' in cleanup:result['census']=cleanup['census']
    return result

def safe_reason(label, returncode, stderr, timed_out=False, overflow=False, start_errno=None):
    """Classify a bounded known diagnostic; never return decoded stderr or values."""
    if start_errno is not None:return {errno.ENOENT:'START_FILE_MISSING',errno.EACCES:'START_PERMISSION_REFUSED',errno.ENOEXEC:'START_FORMAT_REFUSED'}.get(start_errno,'START_OS_REFUSED')
    if timed_out:return 'COMMAND_WATCHDOG_EXPIRED'
    if overflow:return 'COMMAND_OUTPUT_BOUND_EXCEEDED'
    lower=stderr.lower()
    for needle,code in ((b'netlink_route','NETLINK_ROUTE_REFUSED'),
                        (b'no permissions to create new namespace','USER_NAMESPACE_PERMISSION_REFUSED'),
                        (b'creating new namespace failed','NAMESPACE_CREATION_REFUSED'),
                        (b'uid_map','USER_MAPPING_REFUSED'),(b'gid_map','GROUP_MAPPING_REFUSED'),
                        (b'mount proc','PROC_MOUNT_REFUSED'),(b'bind mount','BIND_MOUNT_REFUSED'),
                        (b'unknown option','BWRAP_OPTION_UNAVAILABLE'),
                        (b'no packages found matching','PACKAGE_UNAVAILABLE'),
                        (b'operation not permitted','OS_OPERATION_NOT_PERMITTED'),
                        (b'permission denied','OS_PERMISSION_DENIED'),
                        (b'no such file or directory','OS_REQUIRED_PATH_UNAVAILABLE')):
        if needle in lower:return code
    if label=='source-identity' and stderr:return 'GIT_SOURCE_IDENTITY_REFUSED'
    for name in ('PermissionError','FileNotFoundError','OSError','ValueError','AssertionError','RuntimeError'):
        if re.search(rb'(?:^|\n)'+name.encode('ascii')+rb':',stderr):return 'CHILD_'+name.upper()
    if returncode is None:return 'EXIT_STATUS_UNESTABLISHED'
    if returncode!=0:return 'COMMAND_NONZERO_UNCLASSIFIED'
    return 'STDERR_PRESENT_UNCLASSIFIED' if stderr else 'EXIT_ZERO_NO_STDERR'

def capture(label, argv, records, deadline, seconds=COMMAND_SECONDS, fds=()):
    require(time.monotonic()<deadline,'RUN_WATCHDOG')
    try:
        p=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                           env=safe_environment(),start_new_session=True,pass_fds=tuple(fds))
    except OSError as exc:
        records.append({'name':label,'process_started':False,'returncode':None,'start_errno':exc.errno,
                        'reason_code':safe_reason(label,None,b'',start_errno=exc.errno)})
        raise Refusal('PROCESS_START_REFUSED') from None
    streams=[bytearray(),bytearray()];timed_out=False;overflow=False;complete=False;started=time.monotonic();anchor=None;internal_failure=None
    try:
        try:anchor=os.pidfd_open(p.pid)
        except OSError as exc:
            internal_failure={'code':'PIDFD_ACQUISITION_REFUSED','errno':exc.errno}
            raise Refusal('PIDFD_ACQUISITION_REFUSED') from None
        with selectors.DefaultSelector() as sel:
            for i,s in enumerate((p.stdout,p.stderr)):os.set_blocking(s.fileno(),False);sel.register(s,selectors.EVENT_READ,i)
            while sel.get_map():
                if time.monotonic()>=min(deadline,started+seconds):timed_out=True;break
                for key,_ in sel.select(0.05):
                    chunk=os.read(key.fileobj.fileno(),4096)
                    if not chunk:sel.unregister(key.fileobj);continue
                    remaining=32768-len(streams[key.data]);streams[key.data].extend(chunk[:remaining])
                    if len(chunk)>remaining:overflow=True;break
                if overflow:break
            complete=not sel.get_map()
        if not timed_out and not overflow:
            try:p.wait(timeout=max(0.01,min(1,deadline-time.monotonic())))
            except subprocess.TimeoutExpired:timed_out=True
    finally:
        # Only the one dedicated adapter has children; this also contains orphaned
        # bwrap descendants after subreaper adoption. No process-name/group kill.
        if p.returncode is None:p.poll()
        rc=p.returncode
        try:cleanup=stop_owned_children()
        except BaseException as exc:
            cleanup=getattr(exc,'cleanup_partial',{'echild':False,'pidfd_signals':0,'reaped_statuses':[]})
            known=('CHILD_CUSTODY_REFUSED','CHILD_POPULATION_BOUND','CHILD_CUSTODY_CHANGED',
                   'CHILD_REAP_POPULATION_BOUND','CHILD_WAIT_STATUS_REFUSED')
            cleanup['code']=str(exc) if isinstance(exc,Refusal) and str(exc) in known else 'CHILD_CLEANUP_OBSERVATION_REFUSED'
            if isinstance(exc,Refusal) and hasattr(exc,'census'):cleanup['census']=exc.census
        if rc is None:
            rc=next((row['returncode'] for row in cleanup['reaped_statuses'] if row['pid']==p.pid),None)
            p.returncode=rc
        if anchor is not None:os.close(anchor)
        for s in (p.stdout,p.stderr):s.close()
        records.append({'name':label,'process_started':True,'returncode':rc,'timeout':timed_out,'output_bound_exceeded':overflow,
                        'pidfd_acquired':anchor is not None,'internal_failure':internal_failure,
                        'reason_code':safe_reason(label,rc,bytes(streams[1]),timed_out,overflow),
                        'stream_digest_scope':'CAPTURED_BYTES_ONLY','streams_complete':complete and not timed_out and not overflow,
                        'stdout_bytes':len(streams[0]),'stderr_bytes':len(streams[1]),
                        'stdout_sha256':sha(streams[0]),'stderr_sha256':sha(streams[1]),'cleanup':public_cleanup(cleanup)})
    for accepted,code in ((cleanup['echild'],'CHILD_CLEANUP_UNCERTAIN'),
                          (not timed_out and not overflow,'CAPTURE_BOUND_REFUSED')):
        if not accepted:
            exc=Refusal(code)
            # These exact bounded streams stay private. Callers may validate a
            # closed result separately; cleanup refusal is never suppressed.
            exc.captured={'returncode':rc,'stdout':bytes(streams[0]),'stderr':bytes(streams[1]),
                          'streams_complete':complete and not timed_out and not overflow}
            raise exc
    return rc,bytes(streams[0]),bytes(streams[1])

def write_public(public, documents):
    files={name:canonical(documents[name]) for name in PUBLIC_NAMES if name!='ARTIFACT_MANIFEST.json'}
    files['ARTIFACT_MANIFEST.json']=canonical({'schema':'dg16.linux-host-artifacts.v1','members':[
        {'name':name,'bytes':len(raw),'sha256':sha(raw)} for name,raw in sorted(files.items())]})
    transport_lines(files)  # Validate both original and encoded populations first.
    for name,raw in files.items():
        with (public/name).open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())

def fixture_readback(private):
    """Sanitized retained effects even after the first refusal; never repairs them."""
    result={}
    for relative in ('image/canary','outside/sentinel','work/result','work/escape'):
        p=private/relative
        try:
            info=p.lstat();row={'present':True,'bytes':info.st_size,'mode':stat.S_IMODE(info.st_mode)}
            if stat.S_ISREG(info.st_mode):row.update(kind='file',sha256=sha(checked_file(p,65536)))
            elif stat.S_ISLNK(info.st_mode):row.update(kind='symlink',target_matches_outside=os.readlink(p)==str(private/'outside/sentinel'))
            else:row['kind']='unexpected'
        except FileNotFoundError:row={'present':False}
        except (OSError,Refusal):row={'present':'UNESTABLISHED','readback':'REFUSED'}
        result[relative]=row
    for directory,expected in (('image',{'canary'}),('outside',{'sentinel'}),('work',{'result','escape'})):
        p=private/directory
        if p.is_dir():
            names={f.name for f in p.iterdir()}
            result[directory+'_population']={'count':len(names),'expected_names_exact':names==expected,'unexpected_name_count':len(names-expected)}
    return result

def final_fixtures_ok(value):
    return (all(value.get(name,{}).get('sha256')==sha(raw) for name,raw in
                (('image/canary',CANARY),('outside/sentinel',OUTSIDE),('work/result',WORK)))
            and value.get('work/escape',{}).get('target_matches_outside') is True
            and all(value.get(name+'_population',{}).get('expected_names_exact') is True
                    for name in ('image','outside','work')))

def note_failure(docs, code, operation='ADAPTER', command=None):
    failure=docs['FAILURE.json']
    if failure['present']:failure.setdefault('additional_failures',[]).append({'code':code,'operation_id':operation})
    else:
        failure.update(present=True,code=code,operation_id=operation)
        if command is not None:failure['most_recent_command']=command

def close_listener(listener, listening):
    """One nonblocking adverse observation; always attempt owned socket close."""
    result={'created':listener is not None,'listening_established':listening,
            'readback_attempted':False,'late_connections':0,'close_attempted':False,
            'closed':listener is None,'errors':[]}
    if listener is None:return result
    def failed(operation, exc):
        number=exc.errno if isinstance(exc,OSError) else None
        result['errors'].append({'operation_id':operation,'code':'LISTENER_CLEANUP_ERROR',
            'errno':number if type(number) is int and 0<=number<=4096 else None})
    operation='LISTENER_SET_NONBLOCKING'
    try:
        if listening:
            result['readback_attempted']=True
            listener.setblocking(False);operation='LISTENER_ACCEPT'
            try:connection,_=listener.accept()
            except BlockingIOError:pass
            else:
                # One connection already refutes isolation. No drain retry is needed.
                result['late_connections']=1;operation='LISTENER_CONNECTION_CLOSE'
                connection.close()
    except Exception as exc:failed(operation,exc)
    finally:
        result['close_attempted']=True
        try:listener.close()
        except Exception as exc:failed('LISTENER_CLOSE',exc)
        try:result['closed']=listener.fileno()==-1
        except Exception as exc:failed('LISTENER_CLOSED_READBACK',exc)
    return result

def run(output, source):
    identity=context(output,source);output=Path(output);source=Path(source)
    output.mkdir(mode=0o700);public=output/'public';public.mkdir(mode=0o700)
    private=output/'private';private.mkdir(mode=0o700)
    deadline=time.monotonic()+RUN_SECONDS;records=[];fds=[];listener=None;listener_listening=False;subreaper=False;operation='HOST_INVENTORY'
    docs={'RESULT.json':{'schema':'dg16.linux-host-result.v1','status':'UNQUALIFIED','identity':identity,
          'scope':'HOST_PRIMITIVES_ONLY','C5':False,'full_G2':False,'G3':False,'original_acceptance':False,
          'namespace_attempts':0,'automatic_retry':False},
          'HOST.json':{'schema':'dg16.linux-host-facts.v1','tools':{},'commands':records},
          'SOURCE.json':{'schema':'dg16.linux-host-source.v1','expected_commit':SOURCE_COMMIT,'expected_tree':SOURCE_TREE,'verified':False},
          'PROBE.json':{'schema':'dg16.linux-host-probe.v1','started':False,'child':None},
          'CLEANUP.json':{'schema':'dg16.linux-host-cleanup.v1','private_fixtures_retained':True,'public_evidence_retained':True},
          'FAILURE.json':{'schema':'dg16.linux-host-failure.v1','present':False}}
    def terminated(_signum,_frame):raise Refusal('TERMINATION_REQUESTED')
    signal.signal(signal.SIGTERM,terminated)
    try:
        docs['RESULT.json']['adapter_sha256']=sha(checked_file(Path(__file__).resolve(strict=True)))
        docs['HOST.json']['platform_observation']={'platform':token(sys.platform),'os_name':token(os.name),
            'uid':os.geteuid() if hasattr(os,'geteuid') else None,'architecture':token(os.uname().machine) if hasattr(os,'uname') else 'UNAVAILABLE'}
        require(sys.platform=='linux' and os.name=='posix' and os.geteuid()!=0 and os.uname().machine=='x86_64','HOST_IDENTITY_REFUSED')
        require(hasattr(os,'memfd_create') and hasattr(os,'pidfd_open') and hasattr(signal,'pidfd_send_signal'),'KERNEL_API_UNAVAILABLE')
        release={}
        for line in checked_file(Path('/etc/os-release').resolve(strict=True),16384).decode('utf-8').splitlines():
            if '=' in line:
                k,v=line.split('=',1)
                if k in ('ID','VERSION_ID'):release[k]=token(v.strip('"'),32)
        docs['HOST.json']['os']=release
        require(release=={'ID':'ubuntu','VERSION_ID':'26.04'},'OS_IMAGE_REFUSED')
        docs['HOST.json'].update(architecture='x86_64',kernel=token(os.uname().release),uid=os.geteuid(),
            image_os=token(os.environ.get('ImageOS','')),image_version=token(os.environ.get('ImageVersion','')),
            userns_clone=numeric_file('/proc/sys/kernel/unprivileged_userns_clone'),
            max_user_namespaces=numeric_file('/proc/sys/user/max_user_namespaces'),
            apparmor_userns_restriction=numeric_file('/proc/sys/kernel/apparmor_restrict_unprivileged_userns'))
        operation='TOOL_AND_PROFILE_INVENTORY';tools={}
        for name in ('bwrap','bash','python3','git','dpkg-query'):
            tools[name],docs['HOST.json']['tools'][name]=trusted(name)
        profile=Path('/etc/apparmor.d/bwrap-userns-restrict')
        try:raw=checked_file(profile,65536);profile_fact={'present':True,'sha256':sha(raw),'bytes':len(raw)}
        except (OSError,Refusal):profile_fact={'present':False}
        docs['HOST.json']['apparmor_bwrap_profile']=profile_fact
        for label,path in (('apparmor_enabled','/sys/module/apparmor/parameters/enabled'),
                           ('current_confinement','/proc/self/attr/current')):
            try:
                raw=checked_file(path,65536)
                docs['HOST.json'][label]={'readable':True,'bytes':len(raw),'sha256':sha(raw),
                    'known_value':raw.decode('ascii').strip() if raw.strip() in (b'Y',b'N',b'unconfined') else 'OTHER_RECORDED_BY_DIGEST'}
            except (OSError,Refusal,UnicodeError):docs['HOST.json'][label]={'readable':False}
        try:
            raw=checked_file('/sys/kernel/security/apparmor/profiles',65536)
            docs['HOST.json']['loaded_profile_observation']={'readable':True,'bwrap_profile_listed':any(line.startswith(b'bwrap-userns-restrict ') for line in raw.splitlines())}
        except (OSError,Refusal):docs['HOST.json']['loaded_profile_observation']={'readable':False}
        for name in ('bwrap','bash','python3','git','dpkg-query'):require(tools[name] is not None,'TRUSTED_'+name.upper().replace('-','_')+'_UNAVAILABLE')
        require(Path(sys.executable).resolve()==Path(tools['python3']),'INTERPRETER_IDENTITY_REFUSED')
        require(profile_fact['present'] or docs['HOST.json']['apparmor_userns_restriction'].get('value')==0,
                'BWRAP_PROFILE_OR_UNRESTRICTED_POLICY_UNAVAILABLE')
        operation='SUBREAPER_PREREQUISITE';libc=ctypes.CDLL(None,use_errno=True)
        require(libc.prctl(36,1,0,0,0)==0,'SUBREAPER_UNAVAILABLE');subreaper=True
        actual=ctypes.c_int();require(libc.prctl(37,ctypes.byref(actual),0,0,0)==0 and actual.value==1,'SUBREAPER_READBACK_REFUSED')
        operation='PACKAGE_INVENTORY'
        rc,raw,err=capture('package-versions',[tools['dpkg-query'],'-W','-f=${Package}\t${Version}\n','bubblewrap','apparmor'],records,deadline)
        require(rc==0 and not err,'PACKAGE_INVENTORY_REFUSED')
        packages={}
        for line in raw.decode('ascii').splitlines():
            name,version=line.split('\t');require(name in ('bubblewrap','apparmor') and name not in packages,'PACKAGE_SHAPE_REFUSED');packages[name]=token(version)
        require(set(packages)=={'bubblewrap','apparmor'},'PACKAGE_POPULATION_REFUSED');docs['HOST.json']['packages']=packages
        operation='PUBLIC_SOURCE_IDENTITY'
        rc,raw,err=capture('source-identity',[tools['git'],'-C',str(source),'rev-parse','HEAD','HEAD^{tree}'],records,deadline)
        identities=raw.decode('ascii').splitlines()
        if len(identities)==2 and all(re.fullmatch('[0-9a-f]{40}',value) for value in identities):
            docs['SOURCE.json'].update(observed_commit=identities[0],observed_tree=identities[1])
        require(rc==0 and not err and identities==[SOURCE_COMMIT,SOURCE_TREE],'SOURCE_IDENTITY_REFUSED')
        source_bytes=checked_file(source/SOURCE_FILE,131072);require(sha(source_bytes)==SOURCE_SHA256,'SOURCE_BYTES_REFUSED')
        docs['SOURCE.json'].update(verified=True,member=SOURCE_FILE,member_sha256=SOURCE_SHA256,
            usage='STATIC_LAUNCH_PREDICATE_REFERENCE_ONLY; NO_MAINTAINED_OWNER_IMPORT_OR_CALL')
        operation='OWNED_FIXTURE_PREPARATION';image=private/'image';work=private/'work';outside=private/'outside'
        for p in (image,work,outside):p.mkdir(mode=0o700)
        (image/'canary').write_bytes(CANARY);(outside/'sentinel').write_bytes(OUTSIDE)
        image_fd=os.open(image,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);fds.append(image_fd)
        image_stat=os.fstat(image_fd);work_stat=work.stat()
        payload=CHILD.encode('utf-8');fd=os.memfd_create('dg16-host-probe',os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING);fds.append(fd)
        with os.fdopen(os.dup(fd),'wb') as stream:stream.write(payload);stream.flush()
        os.lseek(fd,0,os.SEEK_SET);fcntl.fcntl(fd,1033,15);require(fcntl.fcntl(fd,1034)==15,'MEMFD_SEAL_REFUSED')
        listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM);listener.bind(('127.0.0.1',0));listener.listen(2)
        listener_listening=True;listener.settimeout(1)
        port=listener.getsockname()[1]
        with socket.create_connection(('127.0.0.1',port),timeout=1):
            connection,_=listener.accept();connection.close()
        listener.setblocking(False)
        parent_ns={k:os.stat('/proc/self/ns/'+k).st_ino for k in ('user','mnt','net','pid')}
        memfd_stat=os.fstat(fd)
        request={'parent_ns':parent_ns,'parent_pid':os.getpid(),'outside':str(outside/'sentinel'),
                 'port':port,'canary_sha256':sha(CANARY),'child_sha256':sha(payload),
                 'fd_anchors':{'sealed_memfd':[memfd_stat.st_dev,memfd_stat.st_ino,stat.S_IFMT(memfd_stat.st_mode)],
                               'image_root':[image_stat.st_dev,image_stat.st_ino,stat.S_IFMT(image_stat.st_mode)],
                               'work_root':[work_stat.st_dev,work_stat.st_ino,stat.S_IFMT(work_stat.st_mode)]}}
        command=[tools['bwrap'],'--unshare-user','--unshare-net','--unshare-pid','--cap-drop','ALL','--die-with-parent','--clearenv']
        for root in ('/usr','/bin','/sbin','/lib','/lib64','/etc'):
            if Path(root).exists():command+=['--ro-bind',root,root]
        command+=['--proc','/proc','--remount-ro','/proc','--dev-bind','/dev/null','/dev/null','--symlink','/proc/self/fd','/dev/fd',
                  '--ro-bind-fd',str(image_fd),'/image','--bind',str(work),'/work','--dir','/sealed',
                  '--perms','0700','--file',str(fd),'/sealed/probe.py','--dir','/implementaudit-python',
                  '--ro-bind',tools['python3'],'/implementaudit-python/cpython','--remount-ro','/',
                  '--chdir','/work','--setenv','PATH','/usr/bin:/bin','--setenv','LC_ALL','C',
                  '/implementaudit-python/cpython','-I','-S','-B','/sealed/probe.py',json.dumps(request,separators=(',',':'))]
        docs['RESULT.json']['namespace_attempts']=1;docs['PROBE.json'].update(launch_requested=True,parent_namespace_inodes=parent_ns,
            maintained_predicates=['MANDATORY_USER_NET','CAP_DROP_ALL','DIE_WITH_PARENT','CLEARENV','TRUSTED_HOST_TOOLS','RO_BIND_FD','SEALED_MEMFD_LINKED_SOURCE','ROOT_REMOUNT_RO','ISOLATED_PYTHON'],
            added_predicates=['PRIVATE_PID_AND_PROC','ONE_WRITABLE_WORK_BIND'],watchdog_seconds=PROBE_SECONDS)
        operation='ONE_NAMESPACE_LAUNCH'
        rc,raw,err=capture('one-bwrap-discrimination',command,records,deadline,PROBE_SECONDS,fds)
        operation='NAMESPACE_RESULT_RECEIVING'
        require(not err,'NAMESPACE_OR_CHILD_STDERR_REFUSED')
        child=child_valid(parse_json(raw));docs['PROBE.json']['child']=child
        require(rc==0 and all(child['checks'].values()),'HOST_PRIMITIVE_DISCRIMINATION_FAILED')
        try:connection,_=listener.accept();connection.close();unexpected=True
        except BlockingIOError:unexpected=False
        require(not unexpected,'HOST_LOOPBACK_REACHED')
        operation='PARENT_EFFECT_READBACK'
        require(checked_file(image/'canary')==CANARY and {p.name for p in image.iterdir()}=={'canary'},'IMAGE_CHANGED')
        require(checked_file(outside/'sentinel')==OUTSIDE and {p.name for p in outside.iterdir()}=={'sentinel'},'OUTSIDE_CHANGED')
        require(checked_file(work/'result')==WORK and {p.name for p in work.iterdir()}=={'result','escape'}
                and (work/'escape').is_symlink() and os.readlink(work/'escape')==str(outside/'sentinel'),'WORK_POPULATION_CHANGED')
        require((image.stat().st_dev,image.stat().st_ino)==(image_stat.st_dev,image_stat.st_ino)
                and (work.stat().st_dev,work.stat().st_ino)==(work_stat.st_dev,work_stat.st_ino),'MOUNT_SOURCE_CHANGED')
        require(fcntl.fcntl(fd,1034)==15,'MEMFD_SEAL_CHANGED')
        docs['PROBE.json']['parent_readback']={'image_unchanged':True,'outside_unchanged':True,'work_exact':True,
            'host_listener_unreached':True,'memfd_seals':15,'image_sha256':sha(CANARY),'outside_sha256':sha(OUTSIDE),'work_sha256':sha(WORK)}
        require(time.monotonic()<deadline,'RUN_WATCHDOG')
        docs['RESULT.json']['status']='HOST_PRIMITIVES_OBSERVED_PENDING_INDEPENDENT_RECEIVING'
    except BaseException as exc:
        code=str(exc) if isinstance(exc,Refusal) else 'UNEXPECTED_'+type(exc).__name__.upper()
        require(re.fullmatch('[A-Z0-9_]{1,100}',code),'FAILURE_CODE_REFUSED')
        note_failure(docs,code,operation,records[-1] if records else None)
        if isinstance(exc,OSError):docs['FAILURE.json']['exception_errno']=exc.errno
    finally:
        if subreaper:
            try:cleanup=stop_owned_children()
            except BaseException:cleanup={'echild':False,'code':'CLEANUP_OBSERVATION_REFUSED'}
        else:cleanup={'echild':True,'note':'NO_PROCESS_LAUNCH_BEFORE_SUBREAPER'}
        docs['CLEANUP.json']['owned_processes']=cleanup
        if not cleanup['echild']:
            docs['RESULT.json']['status']='UNQUALIFIED_CLEANUP_UNCERTAIN'
            note_failure(docs,'CLEANUP_UNCERTAIN','POST_OPERATION_CLEANUP')
        docs['PROBE.json']['started']=any(row['name']=='one-bwrap-discrimination' and row.get('process_started') is True for row in records)
        # Every failed operation still gets post-containment fixture observations.
        try:docs['PROBE.json']['final_fixture_readback']=fixture_readback(private)
        except BaseException:docs['PROBE.json']['final_fixture_readback']={'status':'READBACK_UNESTABLISHED'}
        docs['PROBE.json']['post_shutdown_fixtures_exact']=final_fixtures_ok(docs['PROBE.json']['final_fixture_readback'])
        if docs['RESULT.json']['status']=='HOST_PRIMITIVES_OBSERVED_PENDING_INDEPENDENT_RECEIVING' and not docs['PROBE.json']['post_shutdown_fixtures_exact']:
            docs['RESULT.json']['status']='UNQUALIFIED_FINAL_READBACK';note_failure(docs,'FINAL_FIXTURE_READBACK_REFUSED','POST_SHUTDOWN_FIXTURE_READBACK')
        if docs['SOURCE.json']['verified']:
            try:docs['SOURCE.json']['member_rechecked_unchanged']=sha(checked_file(source/SOURCE_FILE,131072))==SOURCE_SHA256
            except (OSError,Refusal):docs['SOURCE.json']['member_rechecked_unchanged']=False
            if not docs['SOURCE.json']['member_rechecked_unchanged']:
                docs['RESULT.json']['status']='UNQUALIFIED_SOURCE_CHANGED';note_failure(docs,'SOURCE_MEMBER_CHANGED','POST_SHUTDOWN_SOURCE_READBACK')
        listener_cleanup=close_listener(listener,listener_listening)
        docs['CLEANUP.json']['host_listener']=listener_cleanup
        late_connections=listener_cleanup['late_connections']
        docs['CLEANUP.json']['late_host_listener_connections']=late_connections
        if late_connections:
            docs['RESULT.json']['status']='UNQUALIFIED_HOST_LISTENER_REACHED';note_failure(docs,'LATE_HOST_LISTENER_CONNECTION','POST_SHUTDOWN_LISTENER_READBACK')
        if listener_cleanup['errors'] or not listener_cleanup['closed']:
            docs['RESULT.json']['status']='UNQUALIFIED_CLEANUP_UNCERTAIN';note_failure(docs,'LISTENER_CLEANUP_UNCERTAIN','POST_SHUTDOWN_LISTENER_CLEANUP')
        descriptors_closed=True
        for fd in reversed(fds):
            try:os.close(fd)
            except OSError:descriptors_closed=False
        docs['CLEANUP.json'].update(listener_closed=listener_cleanup['closed'],held_descriptors_closed=descriptors_closed)
        if not descriptors_closed:
            docs['RESULT.json']['status']='UNQUALIFIED_CLEANUP_UNCERTAIN';note_failure(docs,'DESCRIPTOR_CLEANUP_UNCERTAIN','HELD_DESCRIPTOR_CLEANUP')
        docs['RESULT.json']['command_count']=len(records)
        write_public(public,docs)
    return 0 if docs['RESULT.json']['status']=='HOST_PRIMITIVES_OBSERVED_PENDING_INDEPENDENT_RECEIVING' else 1

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('--source',type=Path)
    mode=parser.add_mutually_exclusive_group(required=True);mode.add_argument('--run',action='store_true');mode.add_argument('--emit-public',action='store_true')
    args=parser.parse_args()
    try:
        if args.emit_public:emit_public(args.output);return 0
        require(args.source is not None,'SOURCE_ARGUMENT_REQUIRED')
        return run(args.output,args.source)
    except BaseException as exc:
        code=str(exc) if isinstance(exc,Refusal) else 'PACKET_FAILURE_'+type(exc).__name__.upper()
        if not re.fullmatch('[A-Z0-9_]{1,100}',code):code='PACKET_FAILURE'
        print('DG16_LINUX_HOST_TRANSPORT '+json.dumps({'status':'UNQUALIFIED_NO_COMPLETE_PUBLIC_TRANSPORT','code':code},ensure_ascii=True),flush=True)
        return 1

if __name__=='__main__':
    sys.exit(main())
