#!/usr/bin/env python3
"""Finite synthetic access discriminator; no original acceptance or receipt authority.

All native entry points require the admitted parent shell. The pure planner,
validators and observations of ordinary owned files are usable as inert controls.
Raw argv, paths, ACLs, mount lines and streams remain private.
"""
import argparse, ctypes, errno, fcntl, hashlib, importlib.util, json, os, re
import resource, selectors, signal, stat, subprocess, sys, tempfile, time
from pathlib import Path
ROWS=('I0','Wf','Wp','I1','I2','I3','I4')
SCHEMA='dg16.synthetic-access-matrix.v1'
BWRAP_SHA='52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712'
SENTINEL=b'DG16_ACCESS08_FIXED_NONSECRET_SENTINEL\n'
HOST_ROOTS=('/usr','/bin','/sbin','/lib','/lib64','/etc','/proc')
LIMITS={'rows':7,'row_wall_seconds':10,'row_cpu_seconds':5,'phase_seconds':90,
 'stream_bytes':8192,'public_bytes':65536,'synthetic_bytes':1048576,'additional_fds':32,
 'per_process_address_space_bytes':268435456,'observed_descendant_ceiling':16,
 'process_accounting':'PIDFD_SUBREAPER_POLL_50MS_NOT_ATOMIC_PIDS_CGROUP',
 'memory_accounting':'RLIMIT_AS_EACH_DESCENDANT_16_TIMES_256MIB_MAX_AT_OBSERVATIONS'}
class Refusal(Exception):pass
def need(x,code):
 if not x:raise Refusal(code)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()+b'\n'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def integer(x,limit=2**64-1):return type(x) is int and 0<=x<=limit
def digest(x):return type(x) is str and re.fullmatch('[0-9a-f]{64}',x) is not None
def binding(raw):return {'bytes':len(raw),'sha256':sha(raw)}
def read(path,limit):
 with open(path,'rb') as f:raw=f.read(limit+1)
 need(len(raw)<=limit,'READ_BOUND');return raw
def put(path,raw):
 need(len(raw)<=114688,'PRIVATE_MEMBER_BOUND')
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 try:
  with os.fdopen(fd,'wb',closefd=False) as f:f.write(raw);f.flush();os.fsync(fd)
 finally:os.close(fd)
def maps(raw):
 rows=[]
 for line in raw.splitlines():
  bits=line.split();need(len(bits)==3 and all(re.fullmatch('[0-9]+',v) for v in bits),'MAP_SHAPE')
  a,b,c=map(int,bits);need(c>0 and a+c<=2**32 and b+c<=2**32,'MAP_RANGE');rows.append([a,b,c])
 need(1<=len(rows)<=16,'MAP_COUNT')
 for idx,r in enumerate(rows):
  for s in rows[:idx]:
   need(r[0]+r[2]<=s[0] or s[0]+s[2]<=r[0],'MAP_OVERLAP')
   need(r[1]+r[2]<=s[1] or s[1]+s[2]<=r[1],'MAP_OVERLAP')
 return rows
def valid_maps(rows):
 need(type(rows) is list and all(type(r) is list and len(r)==3 and all(integer(v,2**32) for v in r) for r in rows),'MAP_TYPE')
 need(maps('\n'.join(' '.join(map(str,r)) for r in rows))==rows,'MAP_CANONICAL');return rows
def mapped(owner,rows):return any(b<=owner<b+n for a,b,n in rows)
def candidate(ancestors,uid_map,gid_map):
 valid_maps(uid_map);valid_maps(gid_map)
 # Only a unique no-ACL 0700 owner+group absent from ACTUAL child maps.
 selected=[dict(ordinal=i,uid=a['uid'],gid=a['gid']) for i,a in enumerate(ancestors)
  if a['mode']&0o7777==0o700 and a['acl_absent'] and not mapped(a['uid'],uid_map) and not mapped(a['gid'],gid_map)]
 return selected[0] if len(selected)==1 else None
def fact(s):return dict(device=s.st_dev,inode=s.st_ino,mode=s.st_mode,uid=s.st_uid,gid=s.st_gid)
def check_fact(f):
 need(type(f) is dict and set(f)=={'device','inode','mode','uid','gid'} and all(integer(v) for v in f.values()),'FACT_FIELDS')
 need(f['mode']&0o170000==0o040000 and f['uid']<2**32 and f['gid']<2**32,'FACT_TYPE')
def acl(fd):
 out={}
 for key in ('system.posix_acl_access','system.posix_acl_default'):
  try:raw=os.getxattr(fd,key);need(len(raw)<=4096,'ACL_BOUND');out[key]=raw.hex()
  except OSError as e:
   need(e.errno==errno.ENODATA,'ACL_UNAVAILABLE');out[key]=None
 return out
def proc_observation():
 fields={}
 for line in read('/proc/self/status',16384).decode().splitlines():
  key,_,value=line.partition(':')
  if key in ('Uid','Gid','Groups'):fields[key]=[int(x) for x in value.split()]
  if key in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs','Seccomp'):fields[key]=int(value.strip(),16 if key.startswith('Cap') else 10)
 need(len(fields['Uid'])==len(fields['Gid'])==4 and len(fields['Groups'])<=256,'CREDENTIALS_BOUND')
 return dict(fields=fields,uid_map=maps(read('/proc/self/uid_map',4096).decode()),gid_map=maps(read('/proc/self/gid_map',4096).decode()),user_namespace=os.stat('/proc/self/ns/user').st_ino)
def mount_facts(paths):
 # Only the longest containing mount for each exact selected ancestry member.
 raw=read('/proc/self/mountinfo',262144);lines=raw.decode().splitlines();selected=[]
 for path in paths:
  hits=[]
  for line in lines:
   parts=line.split();need(len(parts)>=10 and ' - ' in line,'MOUNT_SHAPE')
   mount=parts[4];mount=re.sub(r'\\([0-7]{3})',lambda m:chr(int(m[1],8)),mount)
   if str(path)==mount or str(path).startswith(mount.rstrip('/')+'/'):hits.append((len(mount),line))
  need(hits,'MOUNT_UNAVAILABLE');selected.append(max(hits)[1])
 return selected

def snapshot(path,target_fd):
 path=Path(path);need(path.is_absolute() and str(path)==os.path.normpath(path),'PATH_SHAPE')
 paths=[Path('/')];paths.extend(Path('/').joinpath(*path.parts[1:i+1]) for i in range(1,len(path.parts)))
 need(len(paths)<=20,'ANCESTRY_BOUND');rows=[];fd=None
 try:
  for i,p in enumerate(paths):
   opened=os.open('/' if i==0 else p.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,**({} if i==0 else {'dir_fd':fd}))
   if fd is not None:os.close(fd)
   fd=opened;s=os.fstat(fd);a=acl(fd);r=fact(s);r.update(acl_absent=all(v is None for v in a.values()),acl_sha256=sha(canonical(a)));rows.append(r)
   rows[-1]['raw_acl']=a
  held=fact(os.fstat(target_fd));need(held=={k:rows[-1][k] for k in held},'TARGET_FD_PATH_DRIFT')
  sentinel_fd=os.open('sentinel',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=target_fd)
  try:
   s=os.fstat(sentinel_fd);raw=os.read(sentinel_fd,1024)
   need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and raw==SENTINEL,'SENTINEL_DRIFT')
   sentinel=dict(device=s.st_dev,inode=s.st_ino,mode=s.st_mode,uid=s.st_uid,gid=s.st_gid,bytes=len(raw),sha256=sha(raw))
  finally:os.close(sentinel_fd)
  link=os.readlink('/proc/self/fd/'+str(target_fd));need(link==str(path),'FD_ROUTE_DRIFT')
  return dict(target=held,target_fd=target_fd,fd_flags=fcntl.fcntl(target_fd,fcntl.F_GETFD),sentinel=sentinel,
   ancestors=rows,paths=list(map(str,paths)),mounts=mount_facts(paths),credentials=proc_observation(),fd_link=link)
 finally:
  if fd is not None:os.close(fd)
def project_snapshot(s):
 return dict(target=s['target'],target_fd=s['target_fd'],fd_flags=s['fd_flags'],sentinel=s['sentinel'],
  ancestors=[{k:v for k,v in r.items() if k!='raw_acl'} for r in s['ancestors']],
  mounts_sha256=sha(canonical(s['mounts'])),credentials=s['credentials'],private_sha256=sha(canonical(s)))
def check_snapshot(s):
 need(type(s) is dict and set(s)=={'target','target_fd','fd_flags','sentinel','ancestors','mounts_sha256','credentials','private_sha256'},'SNAPSHOT_FIELDS')
 check_fact(s['target']);need(integer(s['target_fd'],4095) and integer(s['fd_flags'],1),'FD_RANGE')
 need(type(s['ancestors']) is list and 1<=len(s['ancestors'])<=20,'ANCESTOR_COUNT')
 for a in s['ancestors']:
  need(type(a) is dict and set(a)=={'device','inode','mode','uid','gid','acl_absent','acl_sha256'},'ANCESTOR_FIELDS')
  check_fact({k:a[k] for k in ('device','inode','mode','uid','gid')});need(type(a['acl_absent']) is bool and digest(a['acl_sha256']),'ACL_FIELDS')
 need(s['target']=={k:s['ancestors'][-1][k] for k in s['target']},'TARGET_ANCESTOR_JOIN')
 q=s['sentinel'];need(type(q) is dict and set(q)=={'device','inode','mode','uid','gid','bytes','sha256'},'SENTINEL_FIELDS')
 need(all(integer(q[k]) for k in ('device','inode','mode','uid','gid','bytes')) and q['mode']&0o170000==0o100000 and q['bytes']==len(SENTINEL) and q['sha256']==sha(SENTINEL),'SENTINEL_FIELDS')
 need(digest(s['mounts_sha256']) and digest(s['private_sha256']),'SNAPSHOT_HASH')
 check_credentials(s['credentials'])
def check_credentials(c):
 need(type(c) is dict and set(c)=={'fields','uid_map','gid_map','user_namespace'},'CREDENTIAL_FIELDS')
 valid_maps(c['uid_map']);valid_maps(c['gid_map']);need(integer(c['user_namespace']),'USER_NAMESPACE')
 f=c['fields'];need(type(f) is dict and set(f)=={'Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs','Seccomp'},'STATUS_FIELDS')
 for k in ('Uid','Gid','Groups'):need(type(f[k]) is list and len(f[k])<257 and all(integer(v,2**32-1) for v in f[k]),'IDS_RANGE')
 need(len(f['Uid'])==len(f['Gid'])==4,'IDS_COUNT')
 for k in set(f)-{'Uid','Gid','Groups'}:need(integer(f[k]),'STATUS_RANGE')
PAYLOAD=r'''import errno,hashlib,json,os,sys
p=sys.argv[1];expected=bytes.fromhex(sys.argv[2]);route=sys.argv[3]
fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
s=os.fstat(fd);f=os.open('sentinel',os.O_RDONLY|os.O_NOFOLLOW,dir_fd=fd)
raw=os.read(f,1024);os.close(f);assert raw==expected
write_errno=None
try:
 f=os.open('sentinel',os.O_WRONLY|os.O_NOFOLLOW,dir_fd=fd);os.close(f)
except OSError as e:write_errno=e.errno
assert write_errno==errno.EROFS
fields={}
for line in open('/proc/self/status'):
 k,_,v=line.partition(':')
 if k in ('Uid','Gid','Groups'):fields[k]=list(map(int,v.split()))
 if k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs','Seccomp'):fields[k]=int(v.strip(),16 if k.startswith('Cap') else 10)
def maps(p):return [list(map(int,line.split())) for line in open(p)]
print(json.dumps(dict(schema='dg16.access08-payload.v1',route=route,sentinel_hex=raw.hex(),target=dict(device=s.st_dev,inode=s.st_ino,mode=s.st_mode,uid=s.st_uid,gid=s.st_gid),readonly_errno=write_errno,credentials=dict(fields=fields,uid_map=maps('/proc/self/uid_map'),gid_map=maps('/proc/self/gid_map'),user_namespace=os.stat('/proc/self/ns/user').st_ino)),sort_keys=True,separators=(',',':')))
os.close(fd)
'''
PAYLOAD_SHA=sha(PAYLOAD.encode())
def environment():
    result = dict(PATH="/implementaudit-python" + ":/usr/bin:/bin", LC_ALL="C", PYTHONDONTWRITEBYTECODE="1",
                  PYTHONNOUSERSITE="1", PYTHONSAFEPATH="1", GIT_ATTR_NOSYSTEM="1",
                  GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null",
                  GIT_CONFIG_NOSYSTEM="1", GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1",
                  GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0", GIT_EXTERNAL_DIFF="",
                  GIT_PAGER="cat", PAGER="cat")
    config = {"core.fsmonitor": "false", "core.hooksPath": "/dev/null", "protocol.allow": "never",
              "protocol.ext.allow": "never", "credential.helper": "", "core.sshCommand": "",
              "submodule.recurse": "false"}
    result["GIT_CONFIG_COUNT"] = str(len(config))
    for index, (key, value) in enumerate(config.items()):
        result["GIT_CONFIG_KEY_" + str(index)] = key
        result["GIT_CONFIG_VALUE_" + str(index)] = value
    return result

def argv(bwrap,path,fd,route):
 need(route in ('FD','PATH'),'ROUTE')
 command=[bwrap,'--unshare-user','--unshare-net','--cap-drop','ALL','--die-with-parent','--clearenv']
 for root in HOST_ROOTS:
  if Path(root).exists():command+=['--ro-bind',root,root]
 command+=['--dev-bind','/dev/null','/dev/null','--symlink','/proc/self/fd','/dev/fd']
 command+=['--ro-bind-fd',str(fd),path] if route=='FD' else ['--ro-bind',path,path]
 command+=['--dir','/implementaudit-python','--ro-bind','/usr/bin/python3.12','/implementaudit-python/cpython',
  '--remount-ro','/','--chdir',path]
 for key,value in sorted(environment().items()):command+=['--setenv',key,value]
 command+=['/implementaudit-python/cpython','-I','-S','-B','-c',PAYLOAD,path,SENTINEL.hex(),route]
 return command

def empty_row(name):return dict(id=name,route='PATH' if name=='Wp' else 'FD',status='SKIPPED',skip='NO_BASELINE',
 before=None,after=None,intervention_before=None,argv_sha256=None,pass_fds=None,tool_before=None,tool_after=None,capture=None,payload=None,gate=None)
def empty_record():return dict(schema=SCHEMA,authority='NONE',scope='SEVEN_SYNTHETIC_ACCESS_ROWS_ONLY',status='REFUSED',
 rows=[empty_row(n) for n in ROWS],candidate=None,cleanup=False,phase_elapsed_ns=0,limits=LIMITS,
 failure='NONE',source_admission_sha256=None,original_awards=[],historical_cause='UNPROVED',final_caps_are_setup_observation=False)
def validate_payload(p,row):
 need(type(p) is dict and set(p)=={'schema','route','sentinel_hex','target','readonly_errno','credentials'},'PAYLOAD_FIELDS')
 need(p['schema']=='dg16.access08-payload.v1' and p['route']==row['route'] and p['sentinel_hex']==SENTINEL.hex() and p['readonly_errno']==errno.EROFS,'PAYLOAD_READ_PROOF')
 check_fact(p['target']);check_credentials(p['credentials'])
 # UID/GID on mounted inode may overflow for unmapped host owners; fixed target is root.
 need(p['target']==row['before']['target'],'MOUNTED_INODE_JOIN')
 need(p['credentials']['fields']['CapEff']==0,'PAYLOAD_CAPS')
 need(p['credentials']['user_namespace']!=row['before']['credentials']['user_namespace'],'PAYLOAD_NAMESPACE')
def validate_capture(c):
 need(type(c) is dict and set(c)=={'started','returncode','timeout','overflow','streams_complete','cleanup','stdout','stderr','elapsed_ns','cpu_ns','peak_descendants','permission_formatter'},'CAPTURE_FIELDS')
 for k in ('started','timeout','overflow','streams_complete','cleanup','permission_formatter'):need(type(c[k]) is bool,'CAPTURE_BOOL')
 need(c['returncode'] is None or type(c['returncode']) is int and -255<=c['returncode']<=255,'CAPTURE_RC')
 for k in ('stdout','stderr'):need(type(c[k]) is dict and set(c[k])=={'bytes','sha256'} and integer(c[k]['bytes'],8192) and digest(c[k]['sha256']),'CAPTURE_STREAM')
 # Exact empty bytes have a known digest; a retained literal needs room to exist.
 for key in ('stdout','stderr'):
  stream=c[key];need((stream['bytes']==0)==(stream['sha256']==sha(b'')),'STREAM_EMPTY_BINDING')
 need(not c['permission_formatter'] or c['stderr']['bytes']>=len(b'Permission denied'),'FORMATTER_CAPTURE_REQUIRED')
 need(integer(c['elapsed_ns']) and integer(c['cpu_ns']) and integer(c['peak_descendants'],4096),'CAPTURE_MEASURE')
 need(not c['streams_complete'] or c['started'] and not c['timeout'] and not c['overflow'],'CAPTURE_CONTRADICTION')
def validate(x):
 need(type(x) is dict and set(x)==set(empty_record()),'MATRIX_FIELDS')
 need(x['schema']==SCHEMA and x['authority']=='NONE' and x['scope']=='SEVEN_SYNTHETIC_ACCESS_ROWS_ONLY' and x['limits']==LIMITS,'MATRIX_SCOPE')
 need(x['status'] in ('COMPLETE','REFUSED','INCOMPLETE') and x['original_awards']==[] and x['historical_cause']=='UNPROVED' and x['final_caps_are_setup_observation'] is False,'MATRIX_CLAIM')
 need(type(x['cleanup']) is bool and integer(x['phase_elapsed_ns']) and x['failure'] in ('NONE','PRECONDITION','OBSERVATION','CAPTURE','CLEANUP','DEADLINE'),'MATRIX_FLAGS')
 need(x['source_admission_sha256'] is None or digest(x['source_admission_sha256']),'ADMISSION_HASH')
 need(type(x['rows']) is list and len(x['rows'])==7,'MATRIX_ROWS');baseline=False;stopped=False
 for i,r in enumerate(x['rows']):
  need(type(r) is dict and set(r)==set(empty_row(ROWS[i])) and r['id']==ROWS[i] and r['route']==('PATH' if i==2 else 'FD'),'ROW_ORDER_FIELDS')
  need(r['status'] in ('SKIPPED','PASS','PERMISSION_FORMATTER','OTHER_FAILURE','INCOMPLETE'),'ROW_STATUS')
  if r['status']=='SKIPPED':
   need(r==dict(empty_row(ROWS[i]),skip=r['skip']) and r['skip'] in ('NO_BASELINE','NO_UNIQUE_CANDIDATE','EARLIER_INCOMPLETE'),'SKIP_FIELDS')
   need(r['skip']!='NO_UNIQUE_CANDIDATE' or i>=3 and baseline and x['candidate'] is None,'SKIP_CANDIDATE')
   stopped=True;continue
  need(not stopped and (i==0 or baseline),'ROW_AFTER_STOP')
  need(r['skip'] is None and digest(r['argv_sha256']) and type(r['pass_fds']) is list and len(r['pass_fds'])==1 and integer(r['pass_fds'][0],4095),'ROW_INVOCATION')
  for k in ('before','after','intervention_before'):
   if r[k] is not None:check_snapshot(r[k])
  need(r['before'] is not None and r['pass_fds']==[r['before']['target_fd']],'ROW_FD_JOIN')
  for k in ('tool_before','tool_after'):
   if r[k] is not None:
    t=r[k];need(type(t) is dict and set(t)=={'bytes','sha256','device','inode','mode','uid','gid'} and t['bytes']==72160 and t['sha256']==BWRAP_SHA and all(integer(t[v]) for v in ('device','inode','mode','uid','gid')) and t['mode']&0o170000==0o100000 and t['uid']==0 and not t['mode']&0o6022,'TOOL_JOIN')
  if i:need(r['tool_before']==x['rows'][0]['tool_before'],'TOOL_SERIES_DRIFT')
  need(r['tool_before'] is not None,'TOOL_BEFORE')
  if i in (0,3,4,5,6):
   need(type(r['gate']) is dict and set(r['gate'])=={'device','inode','mode','uid','gid'},'GATE_FIELDS');check_fact(r['gate'])
   need(r['gate'] in [{k:a[k] for k in r['gate']} for a in r['before']['ancestors']],'GATE_ANCESTRY')
   if i==0:need(r['intervention_before'] is None and r['gate']['uid']==r['gate']['gid']==0 and r['gate']['mode']&0o7777==0o700,'GATE_BASELINE')
   else:
    previous=x['rows'][0 if i==3 else i-1]
    need(r['intervention_before']==previous['after'],'PRE_INTERVENTION_DRIFT')
    b=x['rows'][0];need(x['candidate'] is not None,'CROSSOVER_NO_CANDIDATE')
    need((r['gate']['device'],r['gate']['inode'])==(b['gate']['device'],b['gate']['inode']),'GATE_IDENTITY')
    need((r['gate']['uid'],r['gate']['gid'])==((0,0) if i==6 else (x['candidate']['uid'],x['candidate']['gid'])) and r['gate']['mode']&0o7777==(0o711 if i==4 else 0o700),'GATE_INTERVENTION')
    for k in ('target','target_fd','fd_flags','sentinel','credentials','mounts_sha256'):need(r['before'][k]==b['before'][k],'CROSSOVER_DRIFT')
    need(r['argv_sha256']==b['argv_sha256'] and r['pass_fds']==b['pass_fds'],'CROSSOVER_ARGV')
    old=b['before']['ancestors'];new=r['before']['ancestors'];need(len(old)==len(new),'ANCESTOR_DRIFT')
    for aa,bb in zip(old,new):
     if (aa['device'],aa['inode'])==(b['gate']['device'],b['gate']['inode']):
      need(all(aa[k]==bb[k] for k in ('device','inode','acl_absent','acl_sha256')),'GATE_ACL_DRIFT')
     else:need(aa==bb,'ANCESTOR_DRIFT')
  else:need(r['gate'] is None and r['intervention_before'] is None,'WORKSPACE_GATE')
  if i==2:
   b=x['rows'][1];need(r['before']==b['before'] and r['pass_fds']==b['pass_fds'],'WORKSPACE_SAME_OBJECT')
  # Even interrupted/no-capture rows must validate every retained observation.
  if r['status']=='INCOMPLETE' and r['capture'] is None:
   need(r['payload'] is None,'UNOBSERVED_PAYLOAD');stopped=True;continue
  validate_capture(r['capture']);c=r['capture']
  closed=c['started'] and c['streams_complete'] and c['cleanup'] and c['returncode'] is not None and c['elapsed_ns']<=10*10**9 and c['cpu_ns']<=5*10**9 and c['peak_descendants']<=16 and r['after']==r['before'] and r['tool_after']==r['tool_before']
  if r['status']!='INCOMPLETE':need(closed,'ROW_CLOSURE')
  else:stopped=True
  if r['status']=='PASS':
   need(c['returncode']==0 and c['stderr']['bytes']==0 and not c['permission_formatter'] and r['payload'] is not None,'PASS_CAPTURE');validate_payload(r['payload'],r)
   need(c['stdout']==binding(canonical(r['payload'])),'PAYLOAD_STREAM_JOIN')
   if i:
    for key in ('fields','uid_map','gid_map'):need(r['payload']['credentials'][key]==x['rows'][0]['payload']['credentials'][key],'CHILD_CREDENTIAL_DRIFT')
  else:
   need(r['payload'] is None,'FAILED_PAYLOAD')
   if r['status'] in ('PERMISSION_FORMATTER','OTHER_FAILURE'):need(c['returncode']!=0 and (r['status']=='PERMISSION_FORMATTER')==c['permission_formatter'],'FAILURE_CAPTURE')
  if i==0:baseline=r['status']=='PASS'
 if x['candidate'] is not None:
  need(baseline and x['rows'][1]['before'] is not None,'CANDIDATE_BASELINE')
  p=x['rows'][0]['payload']['credentials'];expected=candidate(x['rows'][1]['before']['ancestors'],p['uid_map'],p['gid_map'])
  need(expected is not None and x['candidate']==expected,'ACTUAL_MAPPING_CANDIDATE')
 if x['status']=='COMPLETE':
  need(x['cleanup'] and x['failure']=='NONE' and digest(x['source_admission_sha256']) and x['phase_elapsed_ns']<=90*10**9,'COMPLETE_CLOSURE')
  need(x['rows'][0]['status'] not in ('SKIPPED','INCOMPLETE') and all(r['status']!='INCOMPLETE' for r in x['rows']),'COMPLETE_ROWS')
  if baseline:
   pc=x['rows'][0]['payload']['credentials']
   need(x['candidate']==candidate(x['rows'][1]['before']['ancestors'],pc['uid_map'],pc['gid_map']),'CANDIDATE_NOT_OMITTED')
   need(all(r['status']!='SKIPPED' for r in x['rows'][:3]),'WORKSPACE_BASELINES')
   need(all(r['status']!='SKIPPED' for r in x['rows'][3:]) if x['candidate'] is not None else all(r['skip']=='NO_UNIQUE_CANDIDATE' for r in x['rows'][3:]),'CROSSOVER_POPULATION')
  else:need(all(r['skip']=='NO_BASELINE' for r in x['rows'][1:]),'NO_BASELINE_POPULATION')
 need(len(canonical(x))<=65536,'PUBLIC_BOUND');return x

def disposition(x):
 validate(x)
 if x['status']!='COMPLETE':return x['status']
 status=[r['status'] for r in x['rows']]
 if status[0]!='PASS':return 'NO_POSITIVE_BASELINE'
 if status[1:3]==['PERMISSION_FORMATTER','PASS']:return 'FD_PATH_DIFFERENCE'
 if status[1:3]==['PASS','PASS']:return 'WORKSPACE_FAILURE_NOT_REPRODUCED'
 if status==['PASS','PERMISSION_FORMATTER','PERMISSION_FORMATTER','PERMISSION_FORMATTER','PASS','PERMISSION_FORMATTER','PASS']:return 'CONTROLLED_ACCESS_DEPENDENCY_NOT_HISTORICAL_CAUSE'
 return 'UNRESOLVED_COMBINATION'

# Native operations below are never called by local author controls.
def descendants(root):
 result=[];pending=[root]
 while pending:
  pid=pending.pop()
  try:raw=read('/proc/'+str(pid)+'/task/'+str(pid)+'/children',16384)
  except FileNotFoundError:continue
  for token in raw.split():
   child=int(token)
   if child not in result:result.append(child);pending.append(child)
   need(len(result)<=4096,'DESCENDANT_CENSUS')
 return result

def capture(command,fds,deadline,utility):
 start=time.monotonic();cpu_before=resource.getrusage(resource.RUSAGE_CHILDREN);out=bytearray();err=bytearray();p=None;anchor=None;streams_complete=False;timeout=False;overflow=False;peak=0;cleanup=False;rc=None
 def limits():
  resource.setrlimit(resource.RLIMIT_CPU,(5,5));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 try:
  p=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,pass_fds=tuple(fds),
   env=environment(),start_new_session=True,preexec_fn=limits)
  anchor=os.pidfd_open(p.pid)
  with selectors.DefaultSelector() as selector:
   for s,b in ((p.stdout,out),(p.stderr,err)):os.set_blocking(s.fileno(),False);selector.register(s,selectors.EVENT_READ,b)
   while selector.get_map():
    peak=max(peak,len(descendants(os.getpid())))
    cpu_ticks=0
    for pid in descendants(os.getpid()):
     try:
      fields=read('/proc/'+str(pid)+'/stat',4096).rsplit(b')',1)[1].split();cpu_ticks+=int(fields[11])+int(fields[12])+int(fields[13])+int(fields[14])
     except FileNotFoundError:pass
    if peak>16 or cpu_ticks/os.sysconf('SC_CLK_TCK')>=4.5:break
    if time.monotonic()>=min(start+9.5,deadline):timeout=True;break
    for key,_ in selector.select(.05):
     chunk=os.read(key.fileobj.fileno(),4096)
     if not chunk:selector.unregister(key.fileobj);continue
     left=8192-len(key.data);key.data.extend(chunk[:left])
     if len(chunk)>left:overflow=True;break
    if overflow:break
   streams_complete=not selector.get_map() and not timeout and not overflow and peak<=16
  if streams_complete:
   try:rc=p.wait(timeout=max(.001,min(start+9.5,deadline)-time.monotonic()))
   except subprocess.TimeoutExpired:timeout=True;streams_complete=False
 except (OSError,Refusal):streams_complete=False
 finally:
  if p is not None:
   if p.poll() is not None:rc=p.returncode
   closure=utility.stop_owned_children();cleanup=closure['echild']
   if rc is None:rc=next((r['returncode'] for r in closure['reaped_statuses'] if r['pid']==p.pid),None)
   for s in (p.stdout,p.stderr):s.close()
  else:cleanup=not utility.children()
  if anchor is not None:os.close(anchor)
 cpu_after=resource.getrusage(resource.RUSAGE_CHILDREN);cpu_ns=int(max(0,cpu_after.ru_utime+cpu_after.ru_stime-cpu_before.ru_utime-cpu_before.ru_stime)*1e9)
 c=dict(started=p is not None,returncode=rc,timeout=timeout,overflow=overflow,streams_complete=streams_complete,
  cleanup=cleanup,stdout=binding(out),stderr=binding(err),elapsed_ns=int((time.monotonic()-start)*1e9),cpu_ns=cpu_ns,peak_descendants=peak,
  permission_formatter=b'Permission denied' in err)
 return c,bytes(out),bytes(err)

def physical_open(path):
 fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
 try:
  for name in Path(path).parts[1:]:
   child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);os.close(fd);fd=child
  return fd
 except BaseException:
  os.close(fd);raise

class OwnedTree:
 """Exact owned names, held parents; cleanup never recursively follows names."""
 def __init__(self,parent,island):
  self.parent=Path(parent);self.parent_fd=physical_open(parent);self.nodes=[];self.fds=[];self.gate_fd=None;self.gate=None;self.sentinel=None;self.target_fd=None
  self.name='access08-'+os.urandom(12).hex();self.root=self.parent/self.name
  try:
   os.mkdir(self.name,0o700,dir_fd=self.parent_fd);self.root_fd=self.add(self.parent_fd,self.name)
   if island:
    os.mkdir('gate',0o700,dir_fd=self.root_fd);self.gate_fd=self.add(self.root_fd,'gate');self.gate=self.root/'gate'
    os.mkdir('target',0o755,dir_fd=self.gate_fd);self.target_fd=self.add(self.gate_fd,'target');self.target=self.gate/'target'
   else:self.target_fd=self.root_fd;self.target=self.root
   fd=os.open('sentinel',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644,dir_fd=self.target_fd)
   try:
    need(os.write(fd,SENTINEL)==len(SENTINEL),'SENTINEL_WRITE');self.sentinel=fact(os.fstat(fd))
   finally:os.close(fd)
  except BaseException:
   self.close();raise Refusal('OWNED_CREATION_INCOMPLETE') from None
 def add(self,parent,name):
  fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
  self.fds.append(fd);self.nodes.append((parent,name,fd,fact(os.fstat(fd))));return fd
 def restore(self):
  if self.gate_fd is not None:os.fchown(self.gate_fd,0,0);os.fchmod(self.gate_fd,0o700)
 def close(self):
  success=True
  try:
   self.restore()
   if self.sentinel is not None:
    need(fact(os.stat('sentinel',dir_fd=self.target_fd,follow_symlinks=False))==self.sentinel,'CLEANUP_SENTINEL_ID')
    os.unlink('sentinel',dir_fd=self.target_fd)
   for parent,name,fd,f in reversed(self.nodes):
    actual=fact(os.stat(name,dir_fd=parent,follow_symlinks=False));need(actual==fact(os.fstat(fd)) and actual==f,'CLEANUP_DIRECTORY_ID')
    os.rmdir(name,dir_fd=parent)
  except (OSError,Refusal):success=False
  finally:
   for fd in reversed(self.fds):os.close(fd)
   os.close(self.parent_fd)
  return success

def run(source,private,admission,utility):
 started=time.monotonic();deadline=started+87;x=empty_record();x['source_admission_sha256']=admission;owned=[]
 def check_deadline():need(time.monotonic()<deadline,'DEADLINE')
 try:
  need(os.geteuid()==os.getegid()==0 and digest(admission),'ADMITTED_ROOT_REQUIRED')
  # Parent requires currentness, exact packet, source admission and host inventory first.
  bwrap=Path('/usr/bin/bwrap').resolve(strict=True)
  def tool():
   fd=os.open(bwrap,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
   try:
    s=os.fstat(fd);raw=os.read(fd,131073);need(fact(s)==fact(os.fstat(fd))==fact(bwrap.stat()),'TOOL_CUSTODY')
    need(len(raw)==72160 and sha(raw)==BWRAP_SHA and s.st_uid==0 and not s.st_mode&0o6022,'TOOL_PRECONDITION');return dict(binding(raw),**fact(s))
   finally:os.close(fd)
  tool();opt=Path('/opt');basefd=os.open(opt,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:
   for p in (Path('/'),opt):
    s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and not s.st_mode&0o022,'OPT_CUSTODY')
   need(all(v is None for v in acl(basefd).values()),'OPT_ACL')
  finally:os.close(basefd)
  workspace=Path(source)/'fixtures/canonical-state-rotation';need(workspace.is_dir() and not workspace.is_symlink(),'WORKSPACE_PRECONDITION')
  island=OwnedTree(opt,True);owned.append(island);work=OwnedTree(workspace,False);owned.append(work)
  # Every ordinary observation contains all ancestors from / and the exact live parent FD.
  for index,name in enumerate(ROWS):
   check_deadline()
   if index and x['rows'][0]['status']!='PASS':break
   if index>=3 and x['candidate'] is None:
    for r in x['rows'][3:]:r['skip']='NO_UNIQUE_CANDIDATE'
    break
   tree=work if index in (1,2) else island
   intervention=snapshot(island.target,island.target_fd) if index>=3 else None
   if intervention is not None:
    need(project_snapshot(intervention)==x['rows'][0 if index==3 else index-1]['after'],'PRE_INTERVENTION_DRIFT')
   if index==3:os.fchown(island.gate_fd,x['candidate']['uid'],x['candidate']['gid'])
   elif index in (4,5):os.fchmod(island.gate_fd,0o711 if index==4 else 0o700)
   elif index==6:os.fchown(island.gate_fd,0,0)
   before=snapshot(tree.target,tree.target_fd);route='PATH' if index==2 else 'FD';command=argv(str(bwrap),str(tree.target),tree.target_fd,route)
   r=x['rows'][index];r.update(status='INCOMPLETE',skip=None,before=project_snapshot(before),intervention_before=project_snapshot(intervention) if intervention is not None else None,argv_sha256=sha(canonical(command)),
    pass_fds=[tree.target_fd],tool_before=tool(),gate=fact(os.fstat(island.gate_fd)) if tree is island else None)
   need(len(os.listdir('/proc/self/fd'))<=32,'DIAGNOSTIC_FD_BOUND')
   c,out,err=capture(command,[tree.target_fd],deadline,utility);r['capture']=c
   put(private/(name+'.stdout'),out);put(private/(name+'.stderr'),err)
   after=snapshot(tree.target,tree.target_fd);r['after']=project_snapshot(after);r['tool_after']=tool()
   put(private/(name+'.private.json'),canonical(dict(before=before,after=after,intervention_before=intervention,argv=command,pass_fds=[tree.target_fd],capture=c)))
   closed=c['started'] and c['streams_complete'] and c['cleanup'] and c['elapsed_ns']<=10*10**9 and c['cpu_ns']<=5*10**9 and c['peak_descendants']<=16 and c['returncode'] is not None and r['before']==r['after'] and r['tool_before']==r['tool_after']
   if not closed:
    for rest in x['rows'][index+1:]:rest['skip']='EARLIER_INCOMPLETE'
    x['status']='INCOMPLETE';x['failure']='CAPTURE';break
   if c['returncode']==0 and not err:
    try:
     payload=json.loads(out);validate_payload(payload,r);need(out==canonical(payload),'PAYLOAD_ENCODING');r['payload']=payload;r['status']='PASS'
    except (ValueError,Refusal):r['status']='INCOMPLETE';x['failure']='OBSERVATION';break
   elif c['returncode']!=0:r['status']='PERMISSION_FORMATTER' if c['permission_formatter'] else 'OTHER_FAILURE'
   else:
    r['status']='INCOMPLETE';x['failure']='OBSERVATION';break
   if index==2:
    credentials=x['rows'][0]['payload']['credentials'];x['candidate']=candidate(r['before']['ancestors'],credentials['uid_map'],credentials['gid_map'])
  else:pass
  if x['failure']=='NONE':x['status']='COMPLETE'
 except (OSError,Refusal,ValueError) as e:
  put(private/'exception.private.json',canonical(dict(kind=type(e).__name__,message=str(e)[:512],errno=getattr(e,'errno',getattr(e.__context__,'errno',None)))))
  x['status']='INCOMPLETE' if any(r['status']!='SKIPPED' for r in x['rows']) else 'REFUSED'
  x['failure']='DEADLINE' if str(e)=='DEADLINE' else 'OBSERVATION' if x['status']=='INCOMPLETE' else 'PRECONDITION'
  if str(e)=='OWNED_CREATION_INCOMPLETE':x['status']='INCOMPLETE';x['failure']='CLEANUP'
 finally:
  closed=[tree.close() for tree in reversed(owned)];x['cleanup']=all(closed) and x['failure']!='CLEANUP'
  if not x['cleanup']:x['status']='INCOMPLETE';x['failure']='CLEANUP'
  x['phase_elapsed_ns']=int((time.monotonic()-started)*1e9)
  if x['phase_elapsed_ns']>90*10**9:x['status']='INCOMPLETE';x['failure']='DEADLINE'
 if x['status']=='INCOMPLETE':
  for r in x['rows']:
   if r['status']=='SKIPPED':r['skip']='EARLIER_INCOMPLETE'
 return validate(x)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--private',required=True);parser.add_argument('--admission',required=True);args=parser.parse_args()
 # Hosted origin is necessary, never sufficient authority; caller is separately admitted.
 need(os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_ENVIRONMENT')=='github-hosted','HOSTED_REQUIRED')
 from_path=Path(__file__).with_name('host_utility.py');raw=read(from_path,1048576)
 need(sha(raw)=='429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c','UTILITY_PIN')
 import types
 utility=types.ModuleType('matrix_utility');exec(compile(raw,str(from_path),'exec'),utility.__dict__)
 libc=ctypes.CDLL(None,use_errno=True);value=ctypes.c_int();need(libc.prctl(36,1,0,0,0)==0 and libc.prctl(37,ctypes.byref(value),0,0,0)==0 and value.value==1,'SUBREAPER')
 private=Path(args.private);private.mkdir(mode=0o700)
 x=run(Path(args.source),private,args.admission,utility);raw=canonical(x);put(private/'result.json',raw);sys.stdout.buffer.write(canonical(dict(matrix=binding(raw))));return 0
if __name__=='__main__':raise SystemExit(main())
