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
SCHEMA='dg16.synthetic-access-matrix.v2'
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
# Inserted into access_matrix.py; no separate runtime import or native entry point.
FRONTIER_SCHEMA='dg16.access08-precondition-frontier.v1'
FRONTIER_LIMIT=24576
FRONTIER_CODES=('ADMITTED_ROOT_REQUIRED','TOOL_CUSTODY','TOOL_PRECONDITION','OPT_CUSTODY','OPT_ACL','ACL_UNAVAILABLE','ACL_BOUND','WORKSPACE_PRECONDITION','OWNED_CREATION_INCOMPLETE','SENTINEL_WRITE','CLEANUP_SENTINEL_ID','CLEANUP_DIRECTORY_ID','DEADLINE','DIAGNOSTIC_FD_BOUND','PATH_SHAPE','ANCESTRY_BOUND','TARGET_FD_PATH_DRIFT','SENTINEL_DRIFT','FD_ROUTE_DRIFT','CREDENTIALS_BOUND','READ_BOUND','MAP_SHAPE','MAP_RANGE','MAP_COUNT','MAP_OVERLAP','MOUNT_SHAPE','MOUNT_UNAVAILABLE','PRE_INTERVENTION_DRIFT','FRONTIER_BOUND','PRIVATE_MEMBER_BOUND')
FRONTIER_STEPS=('CREDENTIALS','ADMISSION_CHECK','TOOL_RESOLVE','OPT_OPEN','ROOT_LSTAT','ROOT_CUSTODY','OPT_LSTAT','OPT_CUSTODY','OPT_ACL_ABSENCE','OPT_CLOSE','WORKSPACE_LSTAT','WORKSPACE_DIR_TEST','WORKSPACE_SYMLINK_TEST','WORKSPACE_CHECK','FIRST_DEADLINE','FIRST_SNAPSHOT','FIRST_ARGV','FIRST_FD_CENSUS','FIRST_FD_BOUND','READY_FOR_ROWS','TERMINAL_PRECONDITION',
 *tuple(stage+'_'+op for stage in ('INITIAL_TOOL','FIRST_TOOL') for op in ('OPEN','OPENED_STAT','READ','FD_CLOSING_STAT','PATH_CLOSING_STAT','CUSTODY','PRECONDITION','CLOSE')),
 *tuple(role+'_'+op for role in ('ISLAND','WORK') for op in ('PARENT_OPEN','PARENT_STAT','ROOT_MKDIR','ROOT_OPEN','GATE_MKDIR','GATE_OPEN','TARGET_MKDIR','TARGET_OPEN','SENTINEL_OPEN','SENTINEL_WRITE','SENTINEL_STAT','SENTINEL_CLOSE','CLEANUP_RESTORE_OWNER','CLEANUP_RESTORE_MODE','CLEANUP_SENTINEL_CHECK','CLEANUP_SENTINEL_UNLINK','CLEANUP_DIRECTORY_CHECK','CLEANUP_DIRECTORY_REMOVE','CLEANUP_FD_CLOSE','CLEANUP_PARENT_CLOSE')),
 'OPT_ACL_ACCESS','OPT_ACL_DEFAULT','FIRST_ANCESTOR_OPEN','FIRST_ANCESTOR_ACL_ACCESS','FIRST_ANCESTOR_ACL_DEFAULT')
FRONTIER_FACT_ROLES=('ROOT','OPT','WORKSPACE','ISLAND_PARENT','ISLAND_ROOT','ISLAND_GATE','ISLAND_TARGET','WORK_PARENT','WORK_ROOT')
def empty_frontier():
 return dict(schema=FRONTIER_SCHEMA,state='NOT_STARTED',current=None,operations=[],credentials=None,
  facts={role:None for role in FRONTIER_FACT_ROLES},tools={stage:dict(opened=None,fd_closing=None,path_closing=None,content=None,closed=None) for stage in ('INITIAL_TOOL','FIRST_TOOL')},
  workspace=dict(is_dir=None,is_symlink=None,lstat_errno=None),diagnostic_fd_count=None,acl=[],first_ancestors=[],
  creation={role:dict(started=False,complete=False,cleanup_attempted=False,cleanup_result=None,descriptors_closed=None,owned_descriptor_count=0,closed_descriptor_count=0,parent_descriptor_held=False,parent_descriptor_closed=None) for role in ('ISLAND','WORK')},
  first_failure=None,terminal_exception=None,private_record=None)
def generic_fact(f):
 need(type(f) is dict and set(f)=={'device','inode','mode','uid','gid'} and all(integer(v) for v in f.values()) and f['mode']<=65535 and f['uid']<2**32 and f['gid']<2**32,'FRONTIER_FACT')
def frontier_error(e):
 classes=('Refusal','OSError','PermissionError','FileNotFoundError','NotADirectoryError','IsADirectoryError','ValueError')
 kind=type(e).__name__ if type(e).__name__ in classes else 'OTHER'
 number=getattr(e,'errno',None);origin='DIRECT_OSERROR' if isinstance(e,OSError) and type(number) is int else 'NONE'
 if origin=='NONE' and isinstance(getattr(e,'__context__',None),OSError):number=e.__context__.errno;origin='CHAINED_OSERROR'
 if type(number) is not int or not 0<number<=4095:number=None;origin='NONE'
 code=str(e) if isinstance(e,Refusal) and str(e) in FRONTIER_CODES else 'UNCLASSIFIED_REFUSAL' if isinstance(e,Refusal) else 'OS_ERROR' if isinstance(e,OSError) else 'UNCLASSIFIED_EXCEPTION'
 return dict(exception_class=kind,code=code,errno=number,errno_origin=origin)
def check_frontier_error(e):
 need(type(e) is dict and set(e)=={'exception_class','code','errno','errno_origin'},'FRONTIER_ERROR_FIELDS')
 need(e['exception_class'] in ('Refusal','OSError','PermissionError','FileNotFoundError','NotADirectoryError','IsADirectoryError','ValueError','OTHER') and e['code'] in (*FRONTIER_CODES,'UNCLASSIFIED_REFUSAL','OS_ERROR','UNCLASSIFIED_EXCEPTION'),'FRONTIER_ERROR_ENUM')
 need(e['errno'] is None or type(e['errno']) is int and 0<e['errno']<=4095,'FRONTIER_ERRNO')
 need(e['errno_origin'] in ('NONE','DIRECT_OSERROR','CHAINED_OSERROR') and (e['errno'] is None)==(e['errno_origin']=='NONE'),'FRONTIER_ERRNO_ORIGIN')
 os_classes=('OSError','PermissionError','FileNotFoundError','NotADirectoryError','IsADirectoryError')
 kind=e['exception_class'];code=e['code'];origin=e['errno_origin']
 if kind=='Refusal':need(code in (*FRONTIER_CODES,'UNCLASSIFIED_REFUSAL'),'FRONTIER_REFUSAL_CLASS')
 elif kind in os_classes:need(code=='OS_ERROR','FRONTIER_OS_CLASS')
 elif kind=='ValueError':need(code=='UNCLASSIFIED_EXCEPTION','FRONTIER_VALUE_CLASS')
 if code in (*FRONTIER_CODES,'UNCLASSIFIED_REFUSAL'):need(kind in ('Refusal','OTHER'),'FRONTIER_REFUSAL_CODE')
 elif code=='OS_ERROR':need(kind in (*os_classes,'OTHER'),'FRONTIER_OS_CODE')
 else:need(kind in ('ValueError','OTHER'),'FRONTIER_UNCLASSIFIED_CODE')
 if origin=='DIRECT_OSERROR':need(kind in (*os_classes,'OTHER') and code=='OS_ERROR','FRONTIER_DIRECT_OSERROR')

def frontier_binding(value,maximum=114688):
 need(type(value) is dict and set(value)=={'bytes','sha256'} and integer(value['bytes'],maximum) and digest(value['sha256']),'FRONTIER_BINDING')
 need((value['bytes']==0)==(value['sha256']==sha(b'')),'FRONTIER_EMPTY_BINDING')
class Frontier:
 """Observation only. Every guard is still evaluated by the original operation."""
 def __init__(self):self.public=empty_frontier();self.private=dict(errors=[],paths={},acl=[]);self.stack=[]
 def call(self,step,fn,ordinal=None):
  need(step in FRONTIER_STEPS and len(self.public['operations'])<128,'FRONTIER_BOUND')
  row=dict(step=step,ordinal=ordinal,result='STARTED',error=None);index=len(self.public['operations']);self.public['operations'].append(row);self.public['current']=index
  if self.public['state']=='NOT_STARTED':self.public['state']='IN_PROGRESS'
  self.stack.append(index)
  try:
   value=fn();row['result']='PASSED';return value
  except BaseException as e:
   row['result']='FAILED';row['error']=frontier_error(e)
   self.private['errors'].append(dict(operation=index,exception_class=type(e).__name__[:80],message=str(e)[:512],errno=getattr(e,'errno',None)))
   if self.public['first_failure'] is None:self.public['first_failure']=index
   if 'CLEANUP_' not in step:self.public['state']='FAILED'
   raise
  finally:self.stack.pop()
 def observe_fact(self,role,value):self.public['facts'][role]=fact(value)
 def acl_event(self,scope,ordinal,kind,fn):
  step=('OPT' if scope=='OPT' else 'FIRST_ANCESTOR')+'_ACL_'+kind
  record=dict(scope=scope,ordinal=ordinal,kind=kind,result='STARTED',errno=None,content=None)
  self.public['acl'].append(record);absent=[]
  def action():
   try:
    raw=fn();record.update(result='PRESENT',content=binding(raw))
    self.private['acl'].append(dict(scope=scope,ordinal=ordinal,kind=kind,raw_hex=raw.hex() if len(raw)<=4096 else None,content=binding(raw)))
    return raw
   except OSError as e:
    record.update(result='ABSENT' if e.errno==errno.ENODATA else 'UNSUPPORTED' if e.errno in (errno.EOPNOTSUPP,errno.ENOTSUP) else 'OS_ERROR',errno=e.errno)
    # ENODATA is an observed absent ACL, accepted by the unchanged acl() guard.
    if e.errno==errno.ENODATA:absent.append(e);return None
    raise
  result=self.call(step,action,ordinal)
  if record['result']=='ABSENT':raise absent[0]
  return result
 def ready(self):
  self.call('READY_FOR_ROWS',lambda:None);need(self.public['first_failure'] is None,'FRONTIER_BOUND');self.public['state']='READY'
 def terminal(self,e,raw):
  self.public['terminal_exception']=dict(error=frontier_error(e),private_exception=binding(raw))
  if self.public['state']!='READY':self.public['state']='FAILED'
  if self.public['first_failure'] is None and self.public['state']!='READY':
   index=len(self.public['operations']);need(index<128,'FRONTIER_BOUND')
   self.public['operations'].append(dict(step='TERMINAL_PRECONDITION',ordinal=None,result='FAILED',error=frontier_error(e)))
   self.public['current']=self.public['first_failure']=index;self.public['state']='FAILED'

 def retain(self,private):
  raw=canonical(dict(observations=self.public,private=self.private));put(private/'preconditions.private.json',raw);self.public['private_record']=binding(raw)
  return self.public

def validate_frontier(f,matrix):
 need(type(f) is dict and set(f)==set(empty_frontier()) and f['schema']==FRONTIER_SCHEMA,'FRONTIER_SCHEMA')
 need(f['state'] in ('NOT_STARTED','IN_PROGRESS','READY','FAILED'),'FRONTIER_STATE')
 ops=f['operations'];need(type(ops) is list and len(ops)<=128,'FRONTIER_OPERATIONS')
 need(f['current'] is None if not ops else type(f['current']) is int and f['current']==len(ops)-1,'FRONTIER_CURRENT')
 need(f['diagnostic_fd_count'] is None or integer(f['diagnostic_fd_count'],2**31-1),'FRONTIER_FD_COUNT')
 for i,row in enumerate(ops):
  need(type(row) is dict and set(row)=={'step','ordinal','result','error'} and row['step'] in FRONTIER_STEPS and row['result'] in ('STARTED','PASSED','FAILED'),'FRONTIER_OPERATION_FIELDS')
  need(row['ordinal'] is None or integer(row['ordinal'],31),'FRONTIER_OPERATION_ORDINAL')
  need((row['error'] is not None)==(row['result']=='FAILED'),'FRONTIER_OPERATION_ERROR')
  if row['error'] is not None:check_frontier_error(row['error'])
 # Normal precondition operations are a finite one-shot order; closing calls
 # may follow a failed operation, but no further normal work may continue.
 normal=['CREDENTIALS','ADMISSION_CHECK','TOOL_RESOLVE']
 normal += ['INITIAL_TOOL_'+k for k in ('OPEN','OPENED_STAT','READ','FD_CLOSING_STAT','PATH_CLOSING_STAT','CUSTODY','PRECONDITION','CLOSE')]
 normal += ['OPT_OPEN','ROOT_LSTAT','ROOT_CUSTODY','OPT_LSTAT','OPT_CUSTODY','OPT_ACL_ACCESS','OPT_ACL_DEFAULT','OPT_ACL_ABSENCE','OPT_CLOSE','WORKSPACE_LSTAT','WORKSPACE_DIR_TEST','WORKSPACE_SYMLINK_TEST','WORKSPACE_CHECK']
 for role in ('ISLAND','WORK'):
  normal += [role+'_'+k for k in ('PARENT_OPEN','PARENT_STAT','ROOT_MKDIR','ROOT_OPEN')]
  if role=='ISLAND':normal += [role+'_'+k for k in ('GATE_MKDIR','GATE_OPEN','TARGET_MKDIR','TARGET_OPEN')]
  normal += [role+'_'+k for k in ('SENTINEL_OPEN','SENTINEL_WRITE','SENTINEL_STAT','SENTINEL_CLOSE')]
 normal += ['FIRST_DEADLINE','FIRST_SNAPSHOT']
 ranks={(step,None):i for i,step in enumerate(normal)};offset=len(normal)
 for ordinal in range(20):
  for sub,step in enumerate(('FIRST_ANCESTOR_OPEN','FIRST_ANCESTOR_ACL_ACCESS','FIRST_ANCESTOR_ACL_DEFAULT')):ranks[(step,ordinal)]=offset+ordinal*3+sub
 tail=['FIRST_ARGV']+['FIRST_TOOL_'+k for k in ('OPEN','OPENED_STAT','READ','FD_CLOSING_STAT','PATH_CLOSING_STAT','CUSTODY','PRECONDITION','CLOSE')]+['FIRST_FD_CENSUS','FIRST_FD_BOUND','READY_FOR_ROWS']
 for i,step in enumerate(tail):ranks[(step,None)]=offset+60+i
 positions=[];keys=set()
 for index,row in enumerate(ops):
  key=(row['step'],row['ordinal'])
  if 'CLEANUP_' not in row['step'] and row['step']!='TERMINAL_PRECONDITION':
   need(key in ranks and key not in keys,'FRONTIER_OPERATION_POPULATION');keys.add(key);positions.append(ranks[key])
  if f['first_failure'] is not None and index>f['first_failure']:
   need('CLEANUP_' in row['step'] or row['step'].endswith('_CLOSE') or row['step']=='TERMINAL_PRECONDITION','FRONTIER_CONTINUED_AFTER_FAILURE')
 need(positions==sorted(positions),'FRONTIER_OPERATION_ORDER')
 if f['first_failure'] is not None:
  need(type(f['first_failure']) is int and 0<=f['first_failure']<len(ops) and ops[f['first_failure']]['result']=='FAILED','FRONTIER_FAILURE_JOIN')
 else:need(not any(r['result']=='FAILED' for r in ops),'FRONTIER_MISSING_FAILURE')
 if f['state']=='FAILED':need(f['first_failure'] is not None,'FRONTIER_FAILED_STATE')
 if f['credentials'] is not None:need(type(f['credentials']) is dict and set(f['credentials'])=={'uid','euid','gid','egid'} and all(integer(v,2**32-1) for v in f['credentials'].values()),'FRONTIER_CREDENTIALS')
 need(type(f['facts']) is dict and set(f['facts'])==set(FRONTIER_FACT_ROLES),'FRONTIER_FACT_ROLES')
 for value in f['facts'].values():
  if value is not None:generic_fact(value)
 need(type(f['tools']) is dict and set(f['tools'])=={'INITIAL_TOOL','FIRST_TOOL'},'FRONTIER_TOOLS')
 for t in f['tools'].values():
  need(type(t) is dict and set(t)=={'opened','fd_closing','path_closing','content','closed'},'FRONTIER_TOOL_FIELDS')
  for key in ('opened','fd_closing','path_closing'):
   if t[key] is not None:generic_fact(t[key])
  if t['content'] is not None:frontier_binding(t['content'],131073)
  need(t['closed'] is None or type(t['closed']) is bool,'FRONTIER_TOOL_CLOSED')
 w=f['workspace'];need(type(w) is dict and set(w)=={'is_dir','is_symlink','lstat_errno'},'FRONTIER_WORKSPACE')
 for key in ('is_dir','is_symlink'):need(w[key] is None or type(w[key]) is bool,'FRONTIER_WORKSPACE_FLAGS')
 need(w['lstat_errno'] is None or type(w['lstat_errno']) is int and 0<w['lstat_errno']<=4095,'FRONTIER_WORKSPACE_ERRNO')
 need(type(f['acl']) is list and len(f['acl'])<=42,'FRONTIER_ACL_COUNT');seen=set()
 for a in f['acl']:
  need(type(a) is dict and set(a)=={'scope','ordinal','kind','result','errno','content'} and a['scope'] in ('OPT','FIRST_ANCESTOR') and a['kind'] in ('ACCESS','DEFAULT'),'FRONTIER_ACL_FIELDS')
  need(a['ordinal'] is None if a['scope']=='OPT' else integer(a['ordinal'],19),'FRONTIER_ACL_ORDINAL')
  key=(a['scope'],a['ordinal'],a['kind']);need(key not in seen,'FRONTIER_ACL_DUPLICATE');seen.add(key)
  need(a['result'] in ('STARTED','ABSENT','PRESENT','UNSUPPORTED','OS_ERROR'),'FRONTIER_ACL_RESULT')
  if a['result']=='PRESENT':need(a['errno'] is None,'FRONTIER_ACL_PRESENT');frontier_binding(a['content'],65536)
  else:need(a['content'] is None,'FRONTIER_ACL_NO_BYTES')
  if a['result']=='ABSENT':need(a['errno']==errno.ENODATA,'FRONTIER_ACL_ABSENCE')
  elif a['result']=='UNSUPPORTED':need(a['errno'] in (errno.EOPNOTSUPP,errno.ENOTSUP),'FRONTIER_ACL_UNSUPPORTED')
  elif a['result']=='OS_ERROR':need(type(a['errno']) is int and 0<a['errno']<=4095 and a['errno'] not in (errno.ENODATA,errno.EOPNOTSUPP,errno.ENOTSUP),'FRONTIER_ACL_OS_ERROR')
  elif a['result']=='STARTED':need(a['errno'] is None,'FRONTIER_ACL_STARTED')
  opstep=('OPT' if a['scope']=='OPT' else 'FIRST_ANCESTOR')+'_ACL_'+a['kind']
  related=[r for r in ops if r['step']==opstep and r['ordinal']==a['ordinal']];need(len(related)==1,'FRONTIER_ACL_OPERATION')
  need(related[0]['result']==('STARTED' if a['result']=='STARTED' else 'FAILED' if a['result'] in ('UNSUPPORTED','OS_ERROR') else 'PASSED'),'FRONTIER_ACL_OPERATION_RESULT')
  if a['result'] in ('UNSUPPORTED','OS_ERROR'):need(related[0]['error']['errno']==a['errno'],'FRONTIER_ACL_ERROR_JOIN')
 need(type(f['first_ancestors']) is list and len(f['first_ancestors'])<=20,'FRONTIER_ANCESTORS')
 for value in f['first_ancestors']:generic_fact(value)
 need(type(f['creation']) is dict and set(f['creation'])=={'ISLAND','WORK'},'FRONTIER_CREATION')
 for role,c in f['creation'].items():
  need(type(c) is dict and set(c)=={'started','complete','cleanup_attempted','cleanup_result','descriptors_closed','owned_descriptor_count','closed_descriptor_count','parent_descriptor_held','parent_descriptor_closed'},'FRONTIER_CREATION_FIELDS')
  for key in ('started','complete','cleanup_attempted','parent_descriptor_held'):need(type(c[key]) is bool,'FRONTIER_CREATION_BOOL')
  for key in ('cleanup_result','descriptors_closed','parent_descriptor_closed'):need(c[key] is None or type(c[key]) is bool,'FRONTIER_CLEANUP_BOOL')
  need(not c['complete'] or c['started'],'FRONTIER_CREATION_COMPLETE')
  related=[r for r in ops if r['step'].startswith(role+'_')]
  need(c['started']==bool(related),'FRONTIER_CREATION_ATTEMPT_JOIN')
  parent_open=[r for r in related if r['step']==role+'_PARENT_OPEN']
  need(not c['parent_descriptor_held'] or len(parent_open)==1 and parent_open[0]['result']=='PASSED','FRONTIER_PARENT_OPEN_JOIN')
  closing=[r for r in related if 'CLEANUP_' in r['step']]
  need(c['cleanup_attempted']==bool(closing),'FRONTIER_CLEANUP_OPERATION_JOIN')
  closed_fds=[r for r in closing if r['step']==role+'_CLEANUP_FD_CLOSE' and r['result']=='PASSED']
  need(len(closed_fds)==c['closed_descriptor_count'] and [r['ordinal'] for r in closed_fds]==list(range(c['closed_descriptor_count'])),'FRONTIER_FD_CLOSE_OPERATION_JOIN')
  if c['parent_descriptor_closed'] is True:need(any(r['step']==role+'_CLEANUP_PARENT_CLOSE' and r['result']=='PASSED' for r in closing),'FRONTIER_PARENT_CLOSE_OPERATION_JOIN')
  need(c['cleanup_result'] is None or c['cleanup_attempted'],'FRONTIER_CLEANUP_ATTEMPT')
  need(integer(c['owned_descriptor_count'],3) and integer(c['closed_descriptor_count'],3) and c['closed_descriptor_count']<=c['owned_descriptor_count'],'FRONTIER_DESCRIPTOR_COUNTS')
  if c['cleanup_result'] is True:need(c['descriptors_closed'] is True and c['parent_descriptor_closed'] is True and c['closed_descriptor_count']==c['owned_descriptor_count'],'FRONTIER_CLEANUP_CLOSED')
  if c['descriptors_closed'] is True:need(c['closed_descriptor_count']==c['owned_descriptor_count'] and c['parent_descriptor_closed'] is True,'FRONTIER_DESCRIPTOR_CLOSURE')
  if c['parent_descriptor_closed'] is not None:need(c['parent_descriptor_held'] and c['cleanup_attempted'],'FRONTIER_PARENT_CLOSURE')
  if c['complete']:
   required={role+'_'+key for key in ('PARENT_OPEN','PARENT_STAT','ROOT_MKDIR','ROOT_OPEN','SENTINEL_OPEN','SENTINEL_WRITE','SENTINEL_STAT','SENTINEL_CLOSE')}
   if role=='ISLAND':required|={role+'_'+key for key in ('GATE_MKDIR','GATE_OPEN','TARGET_MKDIR','TARGET_OPEN')}
   need(required<={r['step'] for r in ops if r['result']=='PASSED'} and c['owned_descriptor_count']==(3 if role=='ISLAND' else 1),'FRONTIER_CREATION_STEPS')

 if f['terminal_exception'] is not None:
  e=f['terminal_exception'];need(type(e) is dict and set(e)=={'error','private_exception'},'FRONTIER_TERMINAL_ERROR');check_frontier_error(e['error']);frontier_binding(e['private_exception'])
 if f['private_record'] is not None:frontier_binding(f['private_record'])
 if f['state']=='NOT_STARTED':need(f==empty_frontier() and all(r['status']=='SKIPPED' for r in matrix['rows']) and matrix['status']!='COMPLETE','FRONTIER_NOT_STARTED')
 else:need(f['private_record'] is not None and ops,'FRONTIER_RETENTION')
 passed={r['step'] for r in ops if r['result']=='PASSED'}
 if 'ADMISSION_CHECK' in passed:need(f['credentials'] is not None and f['credentials']['euid']==f['credentials']['egid']==0 and digest(matrix['source_admission_sha256']),'FRONTIER_ADMISSION_JOIN')
 for role in ('ROOT','OPT'):
  if role+'_CUSTODY' in passed:
   v=f['facts'][role];need(v is not None and stat.S_ISDIR(v['mode']) and v['uid']==v['gid']==0 and not v['mode']&0o022,'FRONTIER_CUSTODY_JOIN')
 for stage,t in f['tools'].items():
  if stage+'_CUSTODY' in passed:need(t['opened'] is not None and t['opened']==t['fd_closing']==t['path_closing'],'FRONTIER_TOOL_CUSTODY_JOIN')
  if stage+'_PRECONDITION' in passed:
   need(t['content']==dict(bytes=72160,sha256=BWRAP_SHA) and t['opened'] is not None and t['opened']['uid']==0 and not t['opened']['mode']&0o6022,'FRONTIER_TOOL_PRECONDITION_JOIN')
 if 'OPT_ACL_ABSENCE' in passed:need(len([a for a in f['acl'] if a['scope']=='OPT' and a['result']=='ABSENT'])==2,'FRONTIER_OPT_ACL_JOIN')
 if 'FIRST_FD_BOUND' in passed:need(f['diagnostic_fd_count'] is not None and f['diagnostic_fd_count']<=32,'FRONTIER_FD_BOUND_JOIN')
 if 'WORKSPACE_CHECK' in passed:need(w['is_dir'] is True and w['is_symlink'] is False,'FRONTIER_WORKSPACE_JOIN')
 for row in ops:
  if row['result']!='FAILED':continue
  step=row['step'];error=row['error']
  if step in ('ROOT_CUSTODY','OPT_CUSTODY'):
   v=f['facts'][step.split('_')[0]];need(v is not None and error['code']=='OPT_CUSTODY' and not(stat.S_ISDIR(v['mode']) and v['uid']==v['gid']==0 and not v['mode']&0o022),'FRONTIER_FAILED_CUSTODY_JOIN')
  if step in ('INITIAL_TOOL_PRECONDITION','FIRST_TOOL_PRECONDITION'):
   t=f['tools'][step.removesuffix('_PRECONDITION')];need(t['opened'] is not None and t['content'] is not None and error['code']=='TOOL_PRECONDITION','FRONTIER_FAILED_TOOL_FACTS')
   need(not(t['content']==dict(bytes=72160,sha256=BWRAP_SHA) and t['opened']['uid']==0 and not t['opened']['mode']&0o6022),'FRONTIER_FAILED_TOOL_JOIN')
  if step in ('INITIAL_TOOL_CUSTODY','FIRST_TOOL_CUSTODY'):
   t=f['tools'][step.removesuffix('_CUSTODY')];need(all(t[k] is not None for k in ('opened','fd_closing','path_closing')) and error['code']=='TOOL_CUSTODY' and not(t['opened']==t['fd_closing']==t['path_closing']),'FRONTIER_FAILED_TOOL_CUSTODY')
  if step=='ADMISSION_CHECK':need(f['credentials'] is not None and error['code']=='ADMITTED_ROOT_REQUIRED' and not(f['credentials']['euid']==f['credentials']['egid']==0 and digest(matrix['source_admission_sha256'])),'FRONTIER_FAILED_ADMISSION')
  if step=='FIRST_FD_BOUND':need(error['code']=='DIAGNOSTIC_FD_BOUND' and f['diagnostic_fd_count'] is not None and f['diagnostic_fd_count']>32,'FRONTIER_FAILED_FD_BOUND')
  if step=='WORKSPACE_CHECK':need(error['code']=='WORKSPACE_PRECONDITION' and not(w['is_dir'] is True and w['is_symlink'] is False),'FRONTIER_FAILED_WORKSPACE')
  if step=='OPT_ACL_ABSENCE':need(error['code']=='OPT_ACL' and len([a for a in f['acl'] if a['scope']=='OPT' and a['result']=='PRESENT'])>0,'FRONTIER_FAILED_ACL_ABSENCE')
 for i,value in enumerate(f['first_ancestors']):need(any(r['step']=='FIRST_ANCESTOR_OPEN' and r['ordinal']==i and r['result']=='PASSED' for r in ops),'FRONTIER_ANCESTOR_OPEN_JOIN')
 for a in f['acl']:
  if a['scope']=='FIRST_ANCESTOR':need(a['ordinal']<len(f['first_ancestors']),'FRONTIER_ACL_ANCESTOR_JOIN')
 # Join actual operation results to retained operands. Caught WORKSPACE_LSTAT
 # OSError is intentionally a PASSED callback with errno and no fact.
 opmap={(r['step'],r['ordinal']):r for r in ops if 'CLEANUP_' not in r['step']}
 def result(step,ordinal=None):
  row=opmap.get((step,ordinal));return None if row is None else row['result']
 def has(step,ordinal=None):return result(step,ordinal)=='PASSED'
 if has('CREDENTIALS'):need(f['credentials'] is not None,'FRONTIER_CREDENTIAL_OPERAND')
 for role in ('ROOT','OPT'):
  if has(role+'_LSTAT'):need(f['facts'][role] is not None,'FRONTIER_STAT_OPERAND')
 if has('WORKSPACE_LSTAT'):
  need((f['facts']['WORKSPACE'] is None)==(w['lstat_errno'] is not None),'FRONTIER_WORKSPACE_LSTAT_RESULT')
 if has('WORKSPACE_DIR_TEST'):need(type(w['is_dir']) is bool,'FRONTIER_WORKSPACE_DIR_RESULT')
 if has('WORKSPACE_SYMLINK_TEST'):need(w['is_dir'] is True and type(w['is_symlink']) is bool,'FRONTIER_WORKSPACE_SYMLINK_RESULT')
 if w['is_dir'] is False:need(result('WORKSPACE_SYMLINK_TEST') is None and w['is_symlink'] is None,'FRONTIER_WORKSPACE_SHORT_CIRCUIT')
 for stage,t in f['tools'].items():
  if has(stage+'_OPENED_STAT'):need(t['opened'] is not None,'FRONTIER_TOOL_STAT_OPERAND')
  if has(stage+'_READ'):need(t['content'] is not None,'FRONTIER_TOOL_READ_OPERAND')
  # The producer assigns both closing facts after the second stat returns.
  if has(stage+'_PATH_CLOSING_STAT'):need(t['fd_closing'] is not None and t['path_closing'] is not None and has(stage+'_FD_CLOSING_STAT'),'FRONTIER_TOOL_CLOSING_OPERANDS')
  closing=result(stage+'_CLOSE')
  need(t['closed']==(True if closing=='PASSED' else False if closing in ('STARTED','FAILED') else None),'FRONTIER_TOOL_CLOSE_JOIN')
 for role,c in f['creation'].items():
  if has(role+'_PARENT_STAT'):need(f['facts'][role+'_PARENT'] is not None,'FRONTIER_PARENT_STAT_OPERAND')
  if has(role+'_PARENT_OPEN'):need(c['parent_descriptor_held'],'FRONTIER_ACQUIRED_PARENT')
  for part in (('ROOT','GATE','TARGET') if role=='ISLAND' else ('ROOT',)):
   if has(role+'_'+part+'_OPEN'):need(f['facts'][role+'_'+part] is not None,'FRONTIER_OWNED_STAT_OPERAND')
  acquired=c['parent_descriptor_held'] or c['owned_descriptor_count']>0 or c['complete'] or any(has(role+'_'+part+'_MKDIR') for part in ('ROOT','GATE','TARGET'))
  if matrix['cleanup'] and acquired:
   need(c['cleanup_attempted'] and c['cleanup_result'] is True and c['descriptors_closed'] is True and c['parent_descriptor_closed'] is True and c['closed_descriptor_count']==c['owned_descriptor_count'],'FRONTIER_ACQUIRED_CLEANUP')
  if c['cleanup_result'] is True:
   successful={(r['step'],r['ordinal']) for r in ops if r['result']=='PASSED'}
   # add() appends the FD before fstat and nodes.append. A failed OPEN
   # may therefore hold a descriptor without a known removable node.
   # Passed OPEN or its retained node fact proves a known node; complete
   # is not necessary. Directory ordinals index reversed known nodes,
   # while FD-close ordinals independently index reversed held FDs.
   parts=('ROOT','GATE','TARGET') if role=='ISLAND' else ('ROOT',)
   known=[part for part in parts if has(role+'_'+part+'_OPEN') or f['facts'][role+'_'+part] is not None]
   need(len(known)<=c['owned_descriptor_count'],'FRONTIER_KNOWN_NODE_DESCRIPTOR_COUNT')
   required_cleanup=set()
   if c['parent_descriptor_held']:required_cleanup.add((role+'_CLEANUP_PARENT_CLOSE',None))
   for i in range(c['owned_descriptor_count']):required_cleanup.add((role+'_CLEANUP_FD_CLOSE',i))
   for i in range(len(known)):required_cleanup|={(role+'_CLEANUP_DIRECTORY_CHECK',i),(role+'_CLEANUP_DIRECTORY_REMOVE',i)}
   # gate_fd is assigned only after GATE_OPEN returns successfully.
   if role=='ISLAND' and has(role+'_GATE_OPEN'):required_cleanup|={(role+'_CLEANUP_RESTORE_OWNER',None),(role+'_CLEANUP_RESTORE_MODE',None)}
   # self.sentinel is assigned only after successful SENTINEL_STAT; an
   # opened but unobserved sentinel does not establish its cleanup identity.
   if has(role+'_SENTINEL_STAT'):required_cleanup|={(role+'_CLEANUP_SENTINEL_CHECK',None),(role+'_CLEANUP_SENTINEL_UNLINK',None)}
   need(required_cleanup<=successful,'FRONTIER_SUCCESSFUL_CLEANUP_POPULATION')
 if has('FIRST_FD_CENSUS'):need(f['diagnostic_fd_count'] is not None,'FRONTIER_FD_CENSUS_OPERAND')
 if f['diagnostic_fd_count'] is not None:need(has('FIRST_FD_CENSUS'),'FRONTIER_FD_CENSUS_JOIN')
 for row in ops:
  if row['step'].endswith(('_ACL_ACCESS','_ACL_DEFAULT')):
   scope='OPT' if row['step'].startswith('OPT_') else 'FIRST_ANCESTOR';kind=row['step'].rsplit('_',1)[1]
   need(any(a['scope']==scope and a['ordinal']==row['ordinal'] and a['kind']==kind for a in f['acl']),'FRONTIER_ACL_RESULT_PRESENT')
 if f['state']=='READY':
  # Exact applicable population, including both ACL calls for each observed
  # ancestor, every numeric operand producer, and the tool finally closures.
  expected={(step,None) for step in normal+tail}
  expected|={(step,i) for i in range(len(f['first_ancestors'])) for step in ('FIRST_ANCESTOR_OPEN','FIRST_ANCESTOR_ACL_ACCESS','FIRST_ANCESTOR_ACL_DEFAULT')}
  actual={(r['step'],r['ordinal']) for r in ops if 'CLEANUP_' not in r['step'] and r['step']!='TERMINAL_PRECONDITION'}
  need(actual==expected and all(opmap[key]['result']=='PASSED' for key in expected),'FRONTIER_READY_OPERATION_POPULATION')
  for i,a in enumerate(matrix['rows'][0]['before']['ancestors']):
   values=[v for v in f['acl'] if v['scope']=='FIRST_ANCESTOR' and v['ordinal']==i]
   need(len(values)==2 and {v['kind'] for v in values}=={'ACCESS','DEFAULT'} and all(v['result'] in ('ABSENT','PRESENT') for v in values),'FRONTIER_READY_ANCESTOR_ACL')
   need(a['acl_absent']==all(v['result']=='ABSENT' for v in values),'FRONTIER_ANCESTOR_ACL_OPERAND')
 if f['state']=='READY':
  need(not any(r['result']=='STARTED' for r in ops),'FRONTIER_READY_CLOSED_OPERATIONS')
  need(f['first_failure'] is None or all('CLEANUP_' in r['step'] for r in ops if r['result']=='FAILED'),'FRONTIER_READY_FAILURE')
  required={'ADMISSION_CHECK','INITIAL_TOOL_CUSTODY','INITIAL_TOOL_PRECONDITION','ROOT_CUSTODY','OPT_CUSTODY','OPT_ACL_ABSENCE','WORKSPACE_CHECK','FIRST_SNAPSHOT','FIRST_TOOL_CUSTODY','FIRST_TOOL_PRECONDITION','FIRST_FD_BOUND','READY_FOR_ROWS'}
  need(required<=passed and all(c['complete'] for c in f['creation'].values()),'FRONTIER_READY_PREFIX')
  need(matrix['rows'][0]['status']!='SKIPPED','FRONTIER_READY_ROW')
  row=matrix['rows'][0];before=row['before'];need(before is not None,'FRONTIER_READY_SNAPSHOT')
  observed=[{k:a[k] for k in ('device','inode','mode','uid','gid')} for a in before['ancestors']]
  need(f['first_ancestors']==observed,'FRONTIER_FIRST_SNAPSHOT_JOIN')
  t=f['tools']['FIRST_TOOL'];need(row['tool_before']==dict(t['content'],**t['opened']),'FRONTIER_FIRST_TOOL_JOIN')
  need(len(observed)==5 and observed==[f['facts'][key] for key in ('ROOT','OPT','ISLAND_ROOT','ISLAND_GATE','ISLAND_TARGET')],'FRONTIER_ISLAND_FACT_JOIN')

 if matrix['status']=='COMPLETE':need(f['state']=='READY' and all(r['result']=='PASSED' for r in ops),'FRONTIER_COMPLETE_MATRIX')
 if matrix['cleanup']:
  need(all(not c['cleanup_attempted'] or c['cleanup_result'] is True for c in f['creation'].values()),'FRONTIER_MATRIX_CLEANUP')
 need(len(canonical(f))<=FRONTIER_LIMIT,'FRONTIER_PUBLIC_BOUND');return f


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
def acl(fd,observer=None):
 out={}
 for key in ('system.posix_acl_access','system.posix_acl_default'):
  try:
   raw=os.getxattr(fd,key) if observer is None else observer('ACCESS' if key.endswith('_access') else 'DEFAULT',lambda:os.getxattr(fd,key))
   need(len(raw)<=4096,'ACL_BOUND');out[key]=raw.hex()
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

def snapshot(path,target_fd,observer=None):
 path=Path(path);need(path.is_absolute() and str(path)==os.path.normpath(path),'PATH_SHAPE')
 paths=[Path('/')];paths.extend(Path('/').joinpath(*path.parts[1:i+1]) for i in range(1,len(path.parts)))
 need(len(paths)<=20,'ANCESTRY_BOUND');rows=[];fd=None
 try:
  for i,p in enumerate(paths):
   open_ancestor=lambda:os.open('/' if i==0 else p.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,**({} if i==0 else {'dir_fd':fd}))
   opened=open_ancestor() if observer is None else observer.call('FIRST_ANCESTOR_OPEN',open_ancestor,i)
   if fd is not None:os.close(fd)
   fd=opened;s=os.fstat(fd)
   if observer is not None:observer.public['first_ancestors'].append(fact(s))
   a=acl(fd,None if observer is None else lambda kind,fn:observer.acl_event('FIRST_ANCESTOR',i,kind,fn));r=fact(s);r.update(acl_absent=all(v is None for v in a.values()),acl_sha256=sha(canonical(a)));rows.append(r)
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
 failure='NONE',source_admission_sha256=None,preconditions=empty_frontier(),original_awards=[],historical_cause='UNPROVED',final_caps_are_setup_observation=False)
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
 validate_frontier(x['preconditions'],x)
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
 """Exact owned names and held parents; optional bounded observations only."""
 def __init__(self,parent,island,frontier=None,role=None):
  self.frontier=frontier;self.role=role or ('ISLAND' if island else 'WORK')
  if frontier is not None:frontier.public['creation'][self.role]['started']=True
  self.parent=Path(parent);self.parent_fd=self.call('PARENT_OPEN',lambda:physical_open(parent));self.nodes=[];self.fds=[];self.gate_fd=None;self.gate=None;self.sentinel=None;self.target_fd=None
  if frontier is not None:frontier.public['creation'][self.role]['parent_descriptor_held']=True
  self.name='access08-'+os.urandom(12).hex();self.root=self.parent/self.name
  try:
   if frontier is not None:frontier.observe_fact(self.role+'_PARENT',self.call('PARENT_STAT',lambda:os.fstat(self.parent_fd)))
   self.call('ROOT_MKDIR',lambda:os.mkdir(self.name,0o700,dir_fd=self.parent_fd));self.root_fd=self.add(self.parent_fd,self.name,'ROOT')
   if island:
    self.call('GATE_MKDIR',lambda:os.mkdir('gate',0o700,dir_fd=self.root_fd));self.gate_fd=self.add(self.root_fd,'gate','GATE');self.gate=self.root/'gate'
    self.call('TARGET_MKDIR',lambda:os.mkdir('target',0o755,dir_fd=self.gate_fd));self.target_fd=self.add(self.gate_fd,'target','TARGET');self.target=self.gate/'target'
   else:self.target_fd=self.root_fd;self.target=self.root
   fd=self.call('SENTINEL_OPEN',lambda:os.open('sentinel',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644,dir_fd=self.target_fd))
   try:
    self.call('SENTINEL_WRITE',lambda:need(os.write(fd,SENTINEL)==len(SENTINEL),'SENTINEL_WRITE'))
    self.sentinel=fact(self.call('SENTINEL_STAT',lambda:os.fstat(fd)))
   finally:self.call('SENTINEL_CLOSE',lambda:os.close(fd))
   if frontier is not None:frontier.public['creation'][self.role]['complete']=True
  except BaseException:
   self.close();raise Refusal('OWNED_CREATION_INCOMPLETE') from None
 def call(self,operation,fn,ordinal=None):
  return fn() if self.frontier is None else self.frontier.call(self.role+'_'+operation,fn,ordinal)
 def add(self,parent,name,role):
  def action():
   fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
   self.fds.append(fd)
   if self.frontier is not None:self.frontier.public['creation'][self.role]['owned_descriptor_count']=len(self.fds)
   observed=fact(os.fstat(fd));self.nodes.append((parent,name,fd,observed))
   if self.frontier is not None:self.frontier.public['facts'][self.role+'_'+role]=observed
   return fd
  return self.call(role+'_OPEN',action)
 def restore(self):
  if self.gate_fd is not None:
   self.call('CLEANUP_RESTORE_OWNER',lambda:os.fchown(self.gate_fd,0,0));self.call('CLEANUP_RESTORE_MODE',lambda:os.fchmod(self.gate_fd,0o700))
 def close(self):
  success=True;c=None if self.frontier is None else self.frontier.public['creation'][self.role]
  if c is not None:c['cleanup_attempted']=True
  try:
   self.restore()
   if self.sentinel is not None:
    self.call('CLEANUP_SENTINEL_CHECK',lambda:need(fact(os.stat('sentinel',dir_fd=self.target_fd,follow_symlinks=False))==self.sentinel,'CLEANUP_SENTINEL_ID'))
    self.call('CLEANUP_SENTINEL_UNLINK',lambda:os.unlink('sentinel',dir_fd=self.target_fd))
   for index,(parent,name,fd,f) in enumerate(reversed(self.nodes)):
    def check():
     actual=fact(os.stat(name,dir_fd=parent,follow_symlinks=False));need(actual==fact(os.fstat(fd)) and actual==f,'CLEANUP_DIRECTORY_ID')
    self.call('CLEANUP_DIRECTORY_CHECK',check,index);self.call('CLEANUP_DIRECTORY_REMOVE',lambda:os.rmdir(name,dir_fd=parent),index)
  except (OSError,Refusal):success=False
  finally:
   if c is not None:c['descriptors_closed']=False
   for index,fd in enumerate(reversed(self.fds)):
    self.call('CLEANUP_FD_CLOSE',lambda:os.close(fd),index)
    if c is not None:c['closed_descriptor_count']+=1
   if c is not None:c['parent_descriptor_closed']=False
   self.call('CLEANUP_PARENT_CLOSE',lambda:os.close(self.parent_fd))
   if c is not None:c['parent_descriptor_closed']=True
   if c is not None:c['descriptors_closed']=True;c['cleanup_result']=success
  return success

def run(source,private,admission,utility):
 started=time.monotonic();deadline=started+87;x=empty_record();x['source_admission_sha256']=admission;owned=[];frontier=Frontier()
 def check_deadline():need(time.monotonic()<deadline,'DEADLINE')
 try:
  ids=frontier.call('CREDENTIALS',lambda:dict(uid=os.getuid(),euid=os.geteuid(),gid=os.getgid(),egid=os.getegid()));frontier.public['credentials']=ids
  frontier.call('ADMISSION_CHECK',lambda:need(ids['euid']==ids['egid']==0 and digest(admission),'ADMITTED_ROOT_REQUIRED'))
  # Same admitted parent shell and original precondition guards; observations add no authority.
  bwrap=frontier.call('TOOL_RESOLVE',lambda:Path('/usr/bin/bwrap').resolve(strict=True));frontier.private['paths']['TOOL']=str(bwrap)
  def tool(stage=None):
   call=(lambda operation,fn:fn()) if stage is None else lambda operation,fn:frontier.call(stage+'_'+operation,fn)
   record=None if stage is None else frontier.public['tools'][stage]
   fd=call('OPEN',lambda:os.open(bwrap,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC))
   try:
    st=call('OPENED_STAT',lambda:os.fstat(fd))
    if record is not None:record['opened']=fact(st)
    raw=call('READ',lambda:os.read(fd,131073))
    if record is not None:record['content']=binding(raw)
    closing=call('FD_CLOSING_STAT',lambda:os.fstat(fd));path_closing=call('PATH_CLOSING_STAT',lambda:bwrap.stat())
    if record is not None:record['fd_closing']=fact(closing);record['path_closing']=fact(path_closing)
    call('CUSTODY',lambda:need(fact(st)==fact(closing)==fact(path_closing),'TOOL_CUSTODY'))
    call('PRECONDITION',lambda:need(len(raw)==72160 and sha(raw)==BWRAP_SHA and st.st_uid==0 and not st.st_mode&0o6022,'TOOL_PRECONDITION'))
    return dict(binding(raw),**fact(st))
   finally:
    if record is not None:record['closed']=False
    call('CLOSE',lambda:os.close(fd))
    if record is not None:record['closed']=True
  tool('INITIAL_TOOL');opt=Path('/opt');basefd=frontier.call('OPT_OPEN',lambda:os.open(opt,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW))
  try:
   for role,path in (('ROOT',Path('/')),('OPT',opt)):
    st=frontier.call(role+'_LSTAT',lambda:path.lstat());frontier.observe_fact(role,st)
    frontier.call(role+'_CUSTODY',lambda:need(stat.S_ISDIR(st.st_mode) and st.st_uid==st.st_gid==0 and not st.st_mode&0o022,'OPT_CUSTODY'))
   a=acl(basefd,lambda kind,fn:frontier.acl_event('OPT',None,kind,fn))
   frontier.call('OPT_ACL_ABSENCE',lambda:need(all(v is None for v in a.values()),'OPT_ACL'))
  finally:frontier.call('OPT_CLOSE',lambda:os.close(basefd))
  workspace=Path(source)/'fixtures/canonical-state-rotation';frontier.private['paths']['WORKSPACE']=str(workspace)
  def observe_workspace():
   try:frontier.observe_fact('WORKSPACE',workspace.lstat())
   except OSError as e:frontier.public['workspace']['lstat_errno']=e.errno
  frontier.call('WORKSPACE_LSTAT',observe_workspace)
  w=frontier.public['workspace'];w['is_dir']=frontier.call('WORKSPACE_DIR_TEST',workspace.is_dir)
  if w['is_dir']:w['is_symlink']=frontier.call('WORKSPACE_SYMLINK_TEST',workspace.is_symlink)
  frontier.call('WORKSPACE_CHECK',lambda:need(w['is_dir'] and not w['is_symlink'],'WORKSPACE_PRECONDITION'))
  island=OwnedTree(opt,True,frontier,'ISLAND');owned.append(island);work=OwnedTree(workspace,False,frontier,'WORK');owned.append(work)
  # Every ordinary observation contains all ancestors from / and the exact live parent FD.
  for index,name in enumerate(ROWS):
   if index==0:frontier.call('FIRST_DEADLINE',check_deadline)
   else:check_deadline()
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
   before=frontier.call('FIRST_SNAPSHOT',lambda:snapshot(tree.target,tree.target_fd,frontier)) if index==0 else snapshot(tree.target,tree.target_fd)
   route='PATH' if index==2 else 'FD'
   command=frontier.call('FIRST_ARGV',lambda:argv(str(bwrap),str(tree.target),tree.target_fd,route)) if index==0 else argv(str(bwrap),str(tree.target),tree.target_fd,route)
   r=x['rows'][index];r.update(status='INCOMPLETE',skip=None,before=project_snapshot(before),intervention_before=project_snapshot(intervention) if intervention is not None else None,argv_sha256=sha(canonical(command)),
    pass_fds=[tree.target_fd],tool_before=tool('FIRST_TOOL' if index==0 else None),gate=fact(os.fstat(island.gate_fd)) if tree is island else None)
   if index==0:
    count=frontier.call('FIRST_FD_CENSUS',lambda:len(os.listdir('/proc/self/fd')));frontier.public['diagnostic_fd_count']=count
    frontier.call('FIRST_FD_BOUND',lambda:need(count<=32,'DIAGNOSTIC_FD_BOUND'));frontier.ready()
   else:need(len(os.listdir('/proc/self/fd'))<=32,'DIAGNOSTIC_FD_BOUND')
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
  raw_exception=canonical(dict(kind=type(e).__name__,message=str(e)[:512],errno=getattr(e,'errno',getattr(e.__context__,'errno',None))))
  put(private/'exception.private.json',raw_exception);frontier.terminal(e,raw_exception)
  x['status']='INCOMPLETE' if any(r['status']!='SKIPPED' for r in x['rows']) else 'REFUSED'
  x['failure']='DEADLINE' if str(e)=='DEADLINE' else 'OBSERVATION' if x['status']=='INCOMPLETE' else 'PRECONDITION'
  if str(e)=='OWNED_CREATION_INCOMPLETE':x['status']='INCOMPLETE';x['failure']='CLEANUP'
 finally:
  closed=[]
  for tree in reversed(owned):
   try:closed.append(tree.close())
   except (OSError,Refusal):closed.append(False)
  creation=frontier.public['creation']
  x['cleanup']=all(closed) and x['failure']!='CLEANUP' and all(not c['cleanup_attempted'] or c['cleanup_result'] is True for c in creation.values())
  if not x['cleanup']:x['status']='INCOMPLETE';x['failure']='CLEANUP'
  x['phase_elapsed_ns']=int((time.monotonic()-started)*1e9)
  if x['phase_elapsed_ns']>90*10**9:x['status']='INCOMPLETE';x['failure']='DEADLINE'
 if x['status']=='INCOMPLETE':
  for r in x['rows']:
   if r['status']=='SKIPPED':r['skip']='EARLIER_INCOMPLETE'
 x['preconditions']=frontier.retain(private)
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
