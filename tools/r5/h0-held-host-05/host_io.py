"""Bounded preparation/IO helpers. Import has no effects or owner authority."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time

SOURCE_COMMIT='481e529b691ed3d21169b07f376e357ae51f1f03'
SOURCE_PARENT='eb504b84c423ff836e5bc7f8106870f62aea45f5'
SOURCE_TREE='786b4bfaf39b5cc15ce9cf662a51d4518add4645'
AUTHOR='/root/h0_c02_or'
REPOSITORY='theislampill/IMPLEMENTAUDIT.md'
BRANCH='pro/dg18-r5-h0-held-05-20261105'
CONTROL_BRANCH='pro/dg18-r5-h0-control-20261105'
RELATIVE='tools/r5/h0-held-host-05'
WORKFLOW='.github/workflows/r5-h0-held.yml'
ARCHIVE_URL='https://registry.npmjs.org/@openai/codex/-/codex-0.166.0-linux-x64.tgz'
ARCHIVE_BYTES=172325449
ARCHIVE_SHA='cbc00a26d3d0e2ceefc4be8891f8a81ef1e349b3b175bc0ae308762bc001fd93'
BINARY_MEMBER='package/vendor/x86_64-unknown-linux-musl/bin/codex'
BINARY_BYTES=319346888
BINARY_SHA='b8a11fedf24b2dfb59a70c9e52b030f9a508dcd49cd2dd0d41956f4c785156b8'
CONTROLLER='r5-h0-seven-occurrences-20261105-05'
ENV={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1',
 'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null',
 'GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0','GIT_NO_REPLACE_OBJECTS':'1','GIT_NO_LAZY_FETCH':'1'}
class Refusal(Exception):pass
PROGRESS_PHASES=frozenset(('INITIALIZATION','BINARY_COPY','PROVIDER_START','NATIVE_START','NATIVE_INITIALIZE','ROOT_THREAD','SEED_TURN','NECESSARY_COMPACTION','RESUMED_TURN','HOST_BINDING','MECHANICAL_SELECTION','PHYSICAL_REGISTRATION','CANONICAL_OPEN','MECHANICAL_ENTRY','PARENT_OPEN_MESSAGE','NATIVE_CHILD_SPAWN','EXACT_RESERVATION','PRIOR_LOAD','PRIOR_AUTHORIZATION','PRIOR_DELIVER','PRIOR_BIND','PRIOR_EXACT_RETRY','CURRENT_PREPARATION','CURRENT_LOAD','CURRENT_AUTHORIZATION','CURRENT_DELIVER','CURRENT_BIND','SELECTED_OCCURRENCES_EXPORT','CHILD_TERMINAL','LIVE_RECEIVING','FINAL_CURRENTNESS','NATIVE_CLEANUP','PROVIDER_CLEANUP'))
FAILURE_CODES=frozenset(('ACTUAL_COMMAND_STATUS','ACTUAL_NATIVE_RPC_REFUSED','ACTUAL_NATIVE_TURN_INCOMPLETE','ACTUAL_COMPACTION_INCOMPLETE','ONE_GENUINE_AVAILABLE_SCOPE_REQUIRED','NONPROTECTED_SELECTED_ROOT_REQUIRED','SOURCE_SESSION_META','CANONICAL_REQUIRED_ABSENT','CANONICAL_OPEN_ABSENT','MECHANICAL_NATIVE_TOOL_CONFIG_DIFFERS','MECHANICAL_ACTUAL_CHILD_HEADER_BINDING','MECHANICAL_SOURCE_HEADER','MECHANICAL_ROOT_IDENTITY','ACTUAL_MECHANICAL_MCP_TOOL_NOT_ADVERTISED','NATIVE_CHILD_START_UNAVAILABLE','NATIVE_MECHANICAL_CALL_DID_NOT_COMPLETE','ACTUAL_MECHANICAL_COMPLETION_ABSENT','ACTUAL_MECHANICAL_CALL_ABSENT','ACTUAL_SUPPORTED_RETRY_REQUIRED','STRICTLY_LATER_OWNER_REVISION_REQUIRED','EXACT_PRIOR_RETRY_PREDICATE_NOT_ESTABLISHED','EXISTING_READER_EXPORT_DISAGREES','NATIVE_CHILD_TERMINAL_FAILED','MECHANICAL_NATIVE_SPAWN_RESPONSE','ACTUAL_UNIQUE_PARENT_MESSAGE_REQUIRED','MECHANICAL_CANONICAL_OPEN_SPAWN_MESSAGE_REQUIRED','NATIVE_PARENT_TURN_FAILED','NATIVE_SPAWN_TURN_FAILED','EXISTING_READER_REFUSED','LIVE_NATIVE_IDENTITY_CHANGED','PREPARATION_INPUT_CUSTODY','PREPARATION_PHYSICAL_IDENTITY_CHANGED','EXECUTING_SOURCE_CHANGED','FILE_CHANGED_DURING_READ','NATIVE_NOT_LIVE','NATIVE_ENDED_BEFORE_RECEIVING','NATIVE_CAPTURE_BOUND','NATIVE_STDERR_BOUND','NATIVE_WIRE_BOUND','COMMAND_OUTPUT_BOUND','COMMAND_WATCHDOG','NATIVE_TIMEOUT','NATIVE_EOF','LOCAL_OS_REFUSAL','SOURCE_OR_PROTOCOL_REFUSAL','UNCLASSIFIED_REFUSAL','NATIVE_CLEANUP_REFUSED','PROVIDER_CLEANUP_REFUSED','LOCAL_CLEANUP_UNCERTAIN'))
class Progress:
 """Closed observations only, written before and after real milestones."""
 def __init__(self,work,request,go_sha):
  self.path=Path(work)/'PROGRESS.json'
  self.value={'schema':'r5.h0-closed-progress.v1','host_request_sha256':sha(read(Path(work)/'HOST_REQUEST.json')),'go_sha256':go_sha,'source_tree':SOURCE_TREE,'phase':'INITIALIZATION','phase_completed':False,'completed':{},'failure_phase':None,'failure_code':None,'authority':'NONE'}
  write(self.path,self.value)
 def save(self):
  temporary=self.path.with_suffix('.next');write(temporary,self.value);os.replace(temporary,self.path)
  fd=os.open(self.path.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 def mark(self,phase,completed=False):
  need(phase in PROGRESS_PHASES and type(completed) is bool,'PROGRESS_SHAPE')
  self.value['phase']=phase;self.value['phase_completed']=completed
  if completed:self.value['completed'][phase]=True
  self.save()
 def fail(self,error,code=None):
  if self.value['failure_code'] is not None:return
  message=str(error)
  selected=code if code in FAILURE_CODES else message if message in FAILURE_CODES else 'NATIVE_TIMEOUT' if isinstance(error,TimeoutError) or type(error).__name__=='Empty' else 'NATIVE_EOF' if isinstance(error,EOFError) else 'LOCAL_OS_REFUSAL' if isinstance(error,OSError) else 'SOURCE_OR_PROTOCOL_REFUSAL' if isinstance(error,(ValueError,Refusal,KeyError,TypeError)) else 'UNCLASSIFIED_REFUSAL'
  self.value.update(failure_phase=self.value['phase'],failure_code=selected)
  self.save()
def need(ok,code):
 if not ok:raise Refusal(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def matches(value,fixed):return type(value) is dict and all(k in value and type(value[k]) is type(v) and value[k]==v for k,v in fixed.items())
def encode(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def parse(raw):
 def unique(pairs):
  out={}
  for k,v in pairs:need(k not in out,'DUPLICATE_JSON_KEY');out[k]=v
  return out
 return json.loads(raw,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(Refusal('NONFINITE_JSON')))
def identity(s):return [s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_gid]
def ancestors(path):
 path=Path(path);need(path.is_absolute() and '..' not in path.parts,'NONCANONICAL_PATH')
 rows=[]
 for p in (*reversed(path.parents),path):
  s=p.lstat();need(stat.S_ISDIR(s.st_mode),'ANCESTOR_NOT_DIRECTORY')
  rows.append({'path':str(p),'identity':[s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid]})
 return rows
def pin(path,maximum=512*1024*1024,keep=False):
 path=Path(path);parent=ancestors(path.parent);first=path.lstat()
 need(stat.S_ISREG(first.st_mode) and first.st_nlink==1 and 0<=first.st_size<=maximum,'REGULAR_FILE_BOUND')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK);digest=hashlib.sha256();size=0;parts=[]
 with os.fdopen(fd,'rb') as f:
  need(identity(first)==identity(os.fstat(f.fileno())),'FILE_REPLACED_BEFORE_READ')
  while True:
   block=f.read(min(1048576,maximum-size+1))
   if not block:break
   size+=len(block);need(size<=maximum,'FILE_BYTE_BOUND');digest.update(block)
   if keep:parts.append(block)
  last=os.fstat(f.fileno())
 need(identity(first)==identity(last)==identity(path.lstat()) and size==first.st_size and parent==ancestors(path.parent),'FILE_CHANGED_DURING_READ')
 return {'path':str(path),'bytes':size,'sha256':digest.hexdigest(),'mode':stat.S_IMODE(first.st_mode)}, {'identity':identity(first),'ancestors':parent}, b''.join(parts) if keep else None
def read(path,maximum=4*1024*1024):return pin(path,maximum,True)[2]
def source_pin(path):
 p,_,_=pin(path);return {k:p[k] for k in ('path','bytes','sha256')}
def invocation(path):
 original=Path(path);need(original.is_absolute(),'INVOCATION_NOT_ABSOLUTE')
 current=Path('/');pending=list(original.parts[1:]);rows=[];links=0;steps=0
 while pending:
  steps+=1;need(steps<=256,'INVOCATION_HOP_BOUND');part=pending.pop(0)
  if part=='.':continue
  if part=='..':current=current.parent;continue
  node=current/part;s=node.lstat()
  if stat.S_ISLNK(s.st_mode):
   links+=1;target=os.readlink(node);need(links<=40 and len(os.fsencode(target))<=4096 and identity(s)==identity(node.lstat()),'INVOCATION_LINK_CHANGED')
   rows.append({'path':str(node),'identity':identity(s),'target':target});q=Path(target)
   if q.is_absolute():current=Path('/');pending=list(q.parts[1:])+pending
   else:pending=list(q.parts)+pending
  else:
   need(stat.S_ISDIR(s.st_mode) if pending else stat.S_ISREG(s.st_mode) and s.st_nlink==1,'INVOCATION_KIND')
   rows.append({'path':str(node),'identity':[s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid] if pending else identity(s)});current=node
 need(current==original.resolve(strict=True),'INVOCATION_ALIAS_CHANGED')
 return {'invocation':str(original),'resolved':str(current),'nodes':rows}
def census(manifest):
 need(type(manifest) is dict and type(manifest.get('members')) is list and 1<=len(manifest['members'])<=160,'INPUT_POPULATION')
 rows=[];keys=set();paths=set()
 for item in manifest['members']:
  need(type(item) is dict and type(item.get('key')) is str and item['key'] not in keys and item['path'] not in paths,'INPUT_DUPLICATE')
  need(type(item['bytes']) is int and type(item['mode']) is int and type(item['sha256']) is str and re.fullmatch('[0-9a-f]{64}',item['sha256']),'INPUT_SHAPE')
  keys.add(item['key']);paths.add(item['path']);selected=invocation(item['invocation']) if 'invocation' in item else None
  actual,physical,_=pin(item['path']);need(all(actual[k]==item[k] for k in ('path','bytes','sha256','mode')),'INPUT_PIN_CHANGED')
  if selected:need(selected==invocation(item['invocation']) and selected['resolved']==item['path'],'INVOCATION_CHANGED')
  rows.append({'key':item['key'],**actual,**physical,'invocation':selected})
 return {'schema':'r5.h0-held-input-custody.v1','members':rows}
def write(path,value,replace=False,mode=0o600):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 raw=value if isinstance(value,bytes) else encode(value)
 flags=os.O_WRONLY|os.O_CREAT|os.O_NOFOLLOW|(os.O_TRUNC if replace else os.O_EXCL)
 fd=os.open(path,flags,mode)
 with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 os.chmod(path,mode)
def load(path,name):
 p=Path(path);raw=read(p);module=importlib.util.module_from_spec(importlib.util.spec_from_file_location(name,p));sys.modules[name]=module
 exec(compile(raw,str(p),'exec',dont_inherit=True),module.__dict__);need(read(p)==raw,'IMPORTED_CODE_CHANGED');return module
def command(argv,cwd,timeout=40,maximum=4*1024*1024,env=None):
 """One direct child, bounded pipes/time; outer subreaper owns any descendants."""
 import selectors
 proc=subprocess.Popen(list(map(str,argv)),cwd=cwd,env=ENV if env is None else env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:fd=os.pidfd_open(proc.pid)
 except BaseException:
  # This still-unreaped Popen child retains its PID; never signal a process name.
  proc.kill();proc.wait(timeout=4);proc.stdout.close();proc.stderr.close();raise
 streams=[bytearray(),bytearray()];deadline=time.monotonic()+timeout
 try:
  with selectors.DefaultSelector() as selected:
   for n,s in enumerate((proc.stdout,proc.stderr)):os.set_blocking(s.fileno(),False);selected.register(s,selectors.EVENT_READ,n)
   while selected.get_map():
    need(time.monotonic()<deadline,'COMMAND_WATCHDOG')
    for key,_ in selected.select(min(.05,max(0,deadline-time.monotonic()))):
     block=os.read(key.fileobj.fileno(),65536)
     if not block:selected.unregister(key.fileobj);continue
     need(len(streams[key.data])+len(block)<=maximum,'COMMAND_OUTPUT_BOUND');streams[key.data].extend(block)
  code=proc.wait(timeout=max(.01,deadline-time.monotonic()))
  return code,bytes(streams[0]),bytes(streams[1])
 finally:
  if proc.poll() is None:
   signal.pidfd_send_signal(fd,signal.SIGKILL);proc.wait(timeout=4)
  os.close(fd);proc.stdout.close();proc.stderr.close()
