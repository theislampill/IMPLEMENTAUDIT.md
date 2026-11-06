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

SOURCE_COMMIT='3e0f4b6d05eb086017ce721d40459fdbd68714dd'
SOURCE_PARENT='5c7e04401b3303d585e2c936208bfffb03df2d18'
SOURCE_TREE='f8741d0293ce2fd1b4b2b2e9dfa1e28d153cd81a'
AUTHOR='/root/windows_continuation_author'
REVIEWER='/root/h0_continuation_review'
REVIEW_EXCLUDED_AUTHORS=(AUTHOR,'/root/h0_followthrough','/root/h0_c02_diagnosis','/root/h0_c02_or')
REPOSITORY='theislampill/IMPLEMENTAUDIT.md'
BRANCH='pro/dg18-isolated-h0-20261106-04'
CONTROL_BRANCH='pro/dg18-isolated-h0-control-20261106-04'
RELATIVE='tools/dg18/isolated-h0-20261106-04'
WORKFLOW='.github/workflows/dg18-isolated-h0-20261106-04.yml'
ARCHIVE_URL='https://registry.npmjs.org/@openai/codex/-/codex-0.166.0-linux-x64.tgz'
ARCHIVE_BYTES=172325449
ARCHIVE_SHA='cbc00a26d3d0e2ceefc4be8891f8a81ef1e349b3b175bc0ae308762bc001fd93'
BINARY_MEMBER='package/vendor/x86_64-unknown-linux-musl/bin/codex'
BINARY_BYTES=319346888
BINARY_SHA='b8a11fedf24b2dfb59a70c9e52b030f9a508dcd49cd2dd0d41956f4c785156b8'
CONTROLLER='dg18-isolated-h0-20261106-04'
ENV={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1',
 'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null',
 'GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0','GIT_NO_REPLACE_OBJECTS':'1','GIT_NO_LAZY_FETCH':'1'}
class Refusal(Exception):pass
PROGRESS_PHASES=frozenset(('INITIALIZATION','BINARY_COPY','PROVIDER_START','NATIVE_START','NATIVE_INITIALIZE','ROOT_THREAD','SEED_TURN','NECESSARY_COMPACTION','RESUMED_TURN','HOST_BINDING','MECHANICAL_SELECTION','PHYSICAL_REGISTRATION','CANONICAL_OPEN','MECHANICAL_ENTRY','PARENT_OPEN_MESSAGE','NATIVE_CHILD_SPAWN','EXACT_RESERVATION','PRIOR_LOAD','PRIOR_AUTHORIZATION','PRIOR_DELIVER','PRIOR_BIND','PRIOR_EXACT_RETRY','CURRENT_PREPARATION','CURRENT_LOAD','CURRENT_AUTHORIZATION','CURRENT_DELIVER','CURRENT_BIND','SELECTED_OCCURRENCES_EXPORT','CHILD_TERMINAL','LIVE_RECEIVING','FINAL_CURRENTNESS','NATIVE_CLEANUP','PROVIDER_CLEANUP'))
FAILURE_CODES=frozenset(('H0_OWNER_OBSERVATION_REFUSED','ACTUAL_COMMAND_STATUS','ACTUAL_NATIVE_RPC_REFUSED','ACTUAL_NATIVE_TURN_INCOMPLETE','ACTUAL_COMPACTION_INCOMPLETE','ONE_GENUINE_AVAILABLE_SCOPE_REQUIRED','NONPROTECTED_SELECTED_ROOT_REQUIRED','SOURCE_SESSION_META','CANONICAL_REQUIRED_ABSENT','CANONICAL_OPEN_ABSENT','MECHANICAL_NATIVE_TOOL_CONFIG_DIFFERS','MECHANICAL_ACTUAL_CHILD_HEADER_BINDING','MECHANICAL_SOURCE_HEADER','MECHANICAL_ROOT_IDENTITY','ACTUAL_MECHANICAL_MCP_TOOL_NOT_ADVERTISED','NATIVE_CHILD_START_UNAVAILABLE','NATIVE_MECHANICAL_CALL_DID_NOT_COMPLETE','ACTUAL_MECHANICAL_COMPLETION_ABSENT','ACTUAL_MECHANICAL_CALL_ABSENT','ACTUAL_SUPPORTED_RETRY_REQUIRED','STRICTLY_LATER_OWNER_REVISION_REQUIRED','EXACT_PRIOR_RETRY_PREDICATE_NOT_ESTABLISHED','EXISTING_READER_EXPORT_DISAGREES','NATIVE_CHILD_TERMINAL_FAILED','MECHANICAL_NATIVE_SPAWN_RESPONSE','ACTUAL_UNIQUE_PARENT_MESSAGE_REQUIRED','MECHANICAL_CANONICAL_OPEN_SPAWN_MESSAGE_REQUIRED','NATIVE_PARENT_TURN_FAILED','NATIVE_SPAWN_TURN_FAILED','EXISTING_READER_REFUSED','LIVE_NATIVE_IDENTITY_CHANGED','PREPARATION_INPUT_CUSTODY','PREPARATION_PHYSICAL_IDENTITY_CHANGED','EXECUTING_SOURCE_CHANGED','FILE_CHANGED_DURING_READ','NATIVE_NOT_LIVE','NATIVE_ENDED_BEFORE_RECEIVING','NATIVE_CAPTURE_BOUND','NATIVE_STDERR_BOUND','NATIVE_WIRE_BOUND','COMMAND_OUTPUT_BOUND','COMMAND_WATCHDOG','NATIVE_TIMEOUT','NATIVE_EOF','LOCAL_OS_REFUSAL','SOURCE_OR_PROTOCOL_REFUSAL','UNCLASSIFIED_REFUSAL','NATIVE_CLEANUP_REFUSED','PROVIDER_CLEANUP_REFUSED','LOCAL_CLEANUP_UNCERTAIN'))
class Progress:
 """Closed observations only, written before and after real milestones."""
 def __init__(self,work,request,go_sha):
  self.path=Path(work)/'PROGRESS.json'
  self.value={'schema':'r5.h0-closed-progress.v1','host_request_sha256':sha(read(Path(work)/'HOST_REQUEST.json')),'go_sha256':go_sha,'source_tree':SOURCE_TREE,'phase':'INITIALIZATION','phase_completed':False,'completed':{},'failure_phase':None,'failure_code':None,'mcp_failure':None,'authority':'NONE'}
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
 def observe_mcp_failure(self,**observed):
  if self.value['failure_code'] is None and self.value['mcp_failure'] is None:
   self.value['mcp_failure']=mcp_failure_projection(phase=self.value['phase'],**observed)
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

MCP_SOURCE_REASON_CODES=frozenset(('ACCEPT_BOUNDED_RECONCILIATION', 'ACQUIRED_RECORD_IDENTITY_CHANGED', 'ACQUISITION_FIXED_POLICY_CHANGED', 'ACTUAL_ASSISTANT_ROLE_OR_PHASE', 'ACTUAL_CHILD_OBSERVATION_MISSING', 'ACTUAL_FINAL_RETURN_DELIVERY_ASSOCIATION', 'ACTUAL_FULL_OBLIGATION_AUTHORIZATION_RESPONSE_DIFFERS', 'ACTUAL_FULL_SKILL_LOAD_DIFFERS', 'ACTUAL_HOST_CALL_RESULT_ASSOCIATION', 'ACTUAL_OBLIGATION_EVIDENCE_REQUIRED', 'ACTUAL_PUBLIC_TEXT_SHAPE', 'ACTUAL_RESULT_ARTIFACT_BINDING', 'ACTUAL_RESULT_ARTIFACT_FIELDS', 'ACTUAL_RESULT_EVIDENCE_SHAPE', 'ACTUAL_RETURN_OBLIGATION_OR_SCOPE_DIFFERS', 'ACTUAL_SPAWN_CALL_OUTPUT_ASSOCIATION', 'ACTUAL_SPAWN_CHILD_IDENTITY', 'ACTUAL_USE_EVIDENCE_SHAPE', 'ACTUAL_USE_EXCHANGE_BINDING', 'ADMITTED_EPISODE_RETRY_DIFFERS', 'ADMITTED_JOIN_ABSENT', 'ALLOWED_RANGE_BOUND', 'ALLOWED_RANGE_SHAPE', 'ARTIFACT_ADMISSION_CHANGED', 'ARTIFACT_BYTE_COUNT', 'ARTIFACT_PHYSICAL_CHANGED', 'ARTIFACT_PIN_BOUND', 'ARTIFACT_PIN_CHANGED', 'ARTIFACT_PIN_SHAPE', 'ASSIGNMENT_POLICY_CHANGED', 'AUTHORIZATION_EVIDENCE_SHAPE', 'AUTHORIZATION_EXACT_OBLIGATION_OR_LOAD_IDENTITY', 'AUTHORIZE_BOUNDED_POST_COMPACTION_RECONCILIATION', 'BOUNDARY_CHILD_NOT_FRESH_FOR_SCOPE', 'BOUNDARY_HISTORICAL_MIGRATION_NOT_SELECTED', 'BOUNDARY_RELEASE_ACCEPTANCE_CHANGED', 'BOUNDARY_RELEASE_CANDIDATE_CHANGED', 'BOUNDARY_RELEASE_CANDIDATE_NOT_ACQUIRED', 'BOUNDARY_RELEASE_FRESH_ASSIGNMENT_REQUIRED', 'BOUNDARY_RELEASE_HOLD_REFUSED', 'BOUNDARY_RELEASE_OWNER_FUNCTIONS_ABSENT', 'BOUNDARY_RELEASE_POLICY_CHANGED_DURING_READ', 'BOUNDARY_RELEASE_QUALIFICATION_CHANGED_DURING_READ', 'BOUNDARY_RELEASE_Q_ABSENT', 'BOUNDARY_RELEASE_RESULT_ABSENT', 'BOUNDARY_RELEASE_RESULT_CHANGED', 'BOUNDARY_RELEASE_SOURCE_CHANGED', 'BOUNDARY_RELEASE_STATE_CHANGED_DURING_READ', 'BOUNDARY_RELEASE_SUBJECT_SHAPE', 'BOUNDARY_SOURCE_ASSOCIATION_CHANGED', 'BOUND_EXCHANGE_NOT_ORIGINAL', 'BOUND_EXCHANGE_SHAPE', 'C02_EXISTING_SOURCE_OWNER_NOT_SELECTED', 'C02_FOREIGN_SOURCE_INTERVAL', 'C02_POSITIVE_CURRENT_TERMINAL_SOURCE_FENCE_REQUIRED', 'CANONICAL_EPISODE_ABSENT', 'CHILD_ACTIVATION_BOUNDARY', 'CHILD_EXCHANGE_LOCATOR_SHAPE', 'CHILD_OR_SOURCE_CHANGED', 'CLIENT_AUTHORED_COMPACT_MARKER', 'CONFLICTING_ACQUISITION_OR_ADMISSION', 'CONFLICTING_CHILD_OBSERVATION_EXCHANGE', 'CONFLICTING_IMMUTABLE_ACQUISITION', 'CONFLICTING_ORIGINAL_BIND_REQUEST', 'CONFLICTING_PUBLIC_AUTHORIZATION', 'CONFLICTING_RESERVATION', 'CONFLICTING_RETURN', 'CONFLICTING_ROOT_ACCEPTANCE', 'CONFLICTING_SCOPE_OWNERS', 'CURRENT_CHILD_HISTORY_METADATA_UNSUPPORTED', 'CURRENT_FRESH_PROFILE_REQUIRED', 'CURRENT_FRESH_SOURCE_BOUNDARY_CHANGED', 'CURRENT_FRESH_SPAWN_REQUIRED', 'CURRENT_PUBLIC_BINDING_SHAPE', 'CURRENT_PUBLIC_METADATA_SHAPE', 'CURRENT_PUBLIC_PROFILE_REQUIRED', 'CURRENT_PUBLIC_RETAINED_ID_OR_COMPLETENESS', 'CURRENT_PUBLIC_RETAINED_ID_SHAPE', 'CURRENT_PUBLIC_RETAINED_SHAPE', 'CURRENT_TERMINAL_EFFECT_RELEASE_REQUIRED', 'CUSTODY_RECORD_BYTE_BOUND', 'CUSTODY_RECORD_CHANGED', 'DELIVERY_SHAPE', 'DUPLICATE_JSON_KEY', 'EMPTY_RETURN_COVERAGE', 'EPISODE_EXPORT_ABSENCE_SHAPE', 'EPISODE_EXPORT_ASSIGNED_OBSERVATION_BINDING', 'EPISODE_EXPORT_BOUND', 'EPISODE_EXPORT_CANONICAL_OPENING_DIGEST', 'EPISODE_EXPORT_CANONICAL_ROUTE_BINDING', 'EPISODE_EXPORT_CANONICAL_ROUTE_SHAPE', 'EPISODE_EXPORT_CHILD_SHAPE', 'EPISODE_EXPORT_CODE_PIN_POPULATION', 'EPISODE_EXPORT_CODE_PIN_SHAPE', 'EPISODE_EXPORT_COMPACTION_CUTOFF_BINDING', 'EPISODE_EXPORT_COMPACTION_CUTOFF_SHAPE', 'EPISODE_EXPORT_CONSUMPTION_BINDING', 'EPISODE_EXPORT_CONTINUITY_RECEIPT_BINDING', 'EPISODE_EXPORT_COVERAGE_BINDING', 'EPISODE_EXPORT_CURRENT_OCCURRENCES', 'EPISODE_EXPORT_CUSTODY_BINDING', 'EPISODE_EXPORT_CUSTODY_SHAPE', 'EPISODE_EXPORT_CUTOFF_SHAPE', 'EPISODE_EXPORT_DIGEST', 'EPISODE_EXPORT_DIGEST_SHAPE', 'EPISODE_EXPORT_EPISODE_SHAPE', 'EPISODE_EXPORT_FIXED_CUTOFF_BINDING', 'EPISODE_EXPORT_H0_BINDING', 'EPISODE_EXPORT_H0_SHAPE', 'EPISODE_EXPORT_HOLD_CUTOFF_SHAPE', 'EPISODE_EXPORT_HOST_SCOPE_SHAPE', 'EPISODE_EXPORT_LIFECYCLE_SHAPE', 'EPISODE_EXPORT_OCCURRENCES_BINDING', 'EPISODE_EXPORT_OCCURRENCES_SHAPE', 'EPISODE_EXPORT_OCCURRENCE_CLASSIFICATION', 'EPISODE_EXPORT_OCCURRENCE_COMPLETION', 'EPISODE_EXPORT_OCCURRENCE_PAIR', 'EPISODE_EXPORT_OCCURRENCE_SHAPE', 'EPISODE_EXPORT_OCCURRENCE_SOURCE_RANGE_OR_IDENTITY', 'EPISODE_EXPORT_ORIGINAL_BIND_CUTOFF', 'EPISODE_EXPORT_OWNER_BINDING', 'EPISODE_EXPORT_OWNER_SHAPE', 'EPISODE_EXPORT_PARENT_CHILD_BINDING', 'EPISODE_EXPORT_PARENT_SHAPE', 'EPISODE_EXPORT_PENDING_BOUND', 'EPISODE_EXPORT_PENDING_ROW_BINDING', 'EPISODE_EXPORT_PENDING_ROW_SHAPE', 'EPISODE_EXPORT_PENDING_SHAPE', 'EPISODE_EXPORT_PIN_BINDING', 'EPISODE_EXPORT_PIN_SHAPE', 'EPISODE_EXPORT_PRESENT_REASON', 'EPISODE_EXPORT_REAL_BOUNDARY_REQUIRED', 'EPISODE_EXPORT_RECORD_LOCATOR_SHAPE', 'EPISODE_EXPORT_RECORD_ORDINAL_ORDER', 'EPISODE_EXPORT_RECORD_PHYSICAL_SHAPE', 'EPISODE_EXPORT_RECORD_PIN_BINDING', 'EPISODE_EXPORT_RECORD_PIN_SHAPE', 'EPISODE_EXPORT_RELEASE_BINDING', 'EPISODE_EXPORT_RELEASE_SHAPE', 'EPISODE_EXPORT_RESULT_ACCEPTANCE_JOIN_BINDING', 'EPISODE_EXPORT_ROUTE_DIGEST_SHAPE', 'EPISODE_EXPORT_ROUTE_SCOPE_BINDING', 'EPISODE_EXPORT_SCOPE_BINDING', 'EPISODE_EXPORT_SCOPE_BOUND', 'EPISODE_EXPORT_SCOPE_SHAPE', 'EPISODE_EXPORT_SHAPE', 'EPISODE_EXPORT_SOURCE_IDENTITY_BINDING', 'EPISODE_EXPORT_SOURCE_LOCATOR_BINDING', 'EPISODE_EXPORT_SOURCE_LOCATOR_SHAPE', 'EPISODE_EXPORT_SOURCE_PATH', 'EPISODE_EXPORT_SOURCE_PHYSICAL_ALIAS', 'EPISODE_EXPORT_SOURCE_PHYSICAL_BINDING', 'EPISODE_EXPORT_SOURCE_PHYSICAL_SHAPE', 'EPISODE_EXPORT_SOURCE_RANGE_BINDING', 'EPISODE_EXPORT_SOURCE_RANGE_BOUND', 'EPISODE_EXPORT_SOURCE_RANGE_SHAPE', 'EPISODE_EXPORT_SOURCE_SHAPE', 'EPISODE_WITHOUT_EXACT_Q', 'EXACT_AUTHENTICATED_EPISODE_REQUIRED', 'EXACT_BOUNDARY_SCOPE_REQUIRED', 'EXACT_EPISODE_BINDING_DIFFERS', 'EXACT_SUCCESSFUL_RETURN_REQUIRED', 'FIXED_SELECTED_PROFILE_DIFFERS', 'FIXED_SELECTION_UNBOUND', 'FOREIGN_CHILD', 'FOREIGN_CUSTODY_RECORD', 'FOREIGN_OR_DUPLICATE_RESULT_MEMBER', 'FOREIGN_RETURN_COVERAGE', 'FRESH_CANARY_PROFILE', 'FULL_HOST_OUTPUT_SHAPE', 'FULL_LOAD_CONTENT_SHAPE', 'FULL_MECHANICAL_BIND_RESPONSE_REQUIRED', 'FULL_SUCCESSFUL_HOST_RESPONSE_REQUIRED', 'HOLD_ACTIVATION_COVERAGE_MISSING', 'HOLD_ALLOWED_RANGE_BOUND', 'HOLD_ALLOWED_RANGE_SHAPE', 'HOLD_ANCHOR_COVERAGE_DIFFERS', 'HOLD_BIND_PREFIX_ABSENT', 'HOLD_BIND_PREFIX_ALREADY_SEALED', 'HOLD_COMPLETION_DISCOVERY_SHAPE', 'HOLD_CONTIGUOUS_RANGE_REQUIRED', 'HOLD_EARLY_SAME_EPISODE_USE', 'HOLD_EPISODE_PREVIOUSLY_DISQUALIFIED', 'HOLD_EPISODE_PREVIOUSLY_REFUSED', 'HOLD_EVENT_GAP_OR_DUPLICATE', 'HOLD_EVENT_ORDER', 'HOLD_EVENT_TIMESTAMP', 'HOLD_HISTORY_PREFIX_CHANGED', 'HOLD_HISTORY_PREFIX_OUTSIDE_CUTOFF', 'HOLD_HISTORY_PREFIX_TRUNCATED', 'HOLD_INITIAL_SETTINGS_COUNT', 'HOLD_METADATA_CHANGED', 'HOLD_ORIGINAL_BIND_CALL_UNPROVED', 'HOLD_ORIGINAL_BIND_COMPLETION_UNPROVED', 'HOLD_ORIGINAL_BIND_NOT_PENDING_AT_ENTRY', 'HOLD_ORIGINAL_CALL_DIFFERS', 'HOLD_ORIGINAL_CALL_LOCATOR_SHAPE', 'HOLD_ORIGINAL_CALL_NOT_COVERED', 'HOLD_ORIGINAL_CALL_OUTSIDE_ENTRY', 'HOLD_ORIGINAL_CALL_SHAPE', 'HOLD_ORIGINAL_ENTRY_COVERAGE', 'HOLD_PARTIAL_OR_OVERFLOW_FRAME', 'HOLD_PREFIX_BYTE_BOUND', 'HOLD_PRIOR_ACTIVATION_BINDING', 'HOLD_PRIOR_AUTHORIZATION_SHAPE', 'HOLD_PRIOR_BIND_SHAPE', 'HOLD_PRIOR_BOUND_RESPONSE_FIELDS', 'HOLD_PRIOR_COMPLETED_EXCHANGE_CHANGED', 'HOLD_PRIOR_CONTEXT_BOUND', 'HOLD_PRIOR_DELIVERY_SHAPE', 'HOLD_PRIOR_ENTRY_SHAPE', 'HOLD_PRIOR_EPISODE_PREVIOUSLY_DISQUALIFIED', 'HOLD_PRIOR_EPISODE_PREVIOUSLY_REFUSED', 'HOLD_PRIOR_EXCHANGE_SHAPE', 'HOLD_PRIOR_IMMUTABLE_OBLIGATION_CHANGED', 'HOLD_PRIOR_OBLIGATION_BINDING', 'HOLD_PRIOR_OBLIGATION_NAMESPACE', 'HOLD_PRIOR_OBLIGATION_PIN', 'HOLD_PRIOR_OBLIGATION_SHAPE', 'HOLD_PRIOR_OBSERVATION_ID', 'HOLD_PRIOR_OBSERVATION_ORDER', 'HOLD_PRIOR_OBSERVATION_SHAPE', 'HOLD_PRIOR_OCCURRENCE_BINDING', 'HOLD_PRIOR_ORIGINAL_COMPLETION_CHANGED', 'HOLD_PRIOR_ORIGINAL_COMPLETION_UNPROVED', 'HOLD_PRIOR_PHYSICAL_ORDER', 'HOLD_PRIOR_PREFIX_BOUND', 'HOLD_PRIOR_PREFIX_CHANGED', 'HOLD_PRIOR_PREFIX_TRUNCATED', 'HOLD_PRIOR_PREPARED_SHAPE', 'HOLD_PRIOR_PUBLIC_AUTHORIZATION_CHANGED', 'HOLD_PRIOR_REFUSAL_SCOPE_UNKNOWN', 'HOLD_PRIOR_REQUEST_BINDING', 'HOLD_PRIOR_RETRY_COMPLETION_UNPROVED', 'HOLD_PRIOR_RETRY_OCCURRENCE_BINDING', 'HOLD_PRIOR_RETRY_RESPONSE_DIFFERS', 'HOLD_PRIOR_SCOPE_BOUND', 'HOLD_PRIOR_SCOPE_DUPLICATE', 'HOLD_PRIOR_SCOPE_SHAPE', 'HOLD_PRIOR_SOURCE_CONTEXT_CHANGED', 'HOLD_PRIOR_UNBOUND_OBSERVATION', 'HOLD_RECORD_COUNT_BOUND', 'HOLD_RECORD_SHAPE', 'HOLD_SOURCE_CHANGED_BEFORE_READ', 'HOLD_SOURCE_CHANGED_DURING_READ', 'HOLD_SOURCE_PHYSICAL_CHANGED', 'HOLD_UNCLASSIFIED_EVENT', 'HOLD_UNCLASSIFIED_TOOL_CALL', 'HOLD_UNPAIRED_TOOL_OUTPUT', 'HOLD_UNQUALIFIED_TOOL_DECLARATION', 'HOLD_UNSETTLED_TOOL_CALL', 'IMMUTABLE_ACQUISITION_WRITE_DIFFERS', 'IMMUTABLE_ACTUAL_RESULT_CHANGED', 'IMMUTABLE_OBLIGATION_CHANGED', 'INHERITED_CHILD_RECORD', 'INVALID_TEXT', 'JOIN_SHAPE', 'LOAD', 'MECHANICAL_ACTUAL_CHILD_HEADER_BINDING', 'MECHANICAL_ARGUMENT_SHAPE', 'MECHANICAL_CANONICAL_OPEN_REQUIRED', 'MECHANICAL_CANONICAL_OPEN_SPAWN_MESSAGE_REQUIRED', 'MECHANICAL_CHILD_CHANGED', 'MECHANICAL_CHILD_TOOL_REQUIRED', 'MECHANICAL_EXACT_ARGUMENT_WIRE_REQUIRED', 'MECHANICAL_FIXED_PENDING_OWNER_DIFFERS', 'MECHANICAL_FRESH_CHILD_REQUIRED', 'MECHANICAL_JSON_BOUND', 'MECHANICAL_NATIVE_ROOT_BINDING', 'MECHANICAL_NATIVE_SPAWN_RESPONSE', 'MECHANICAL_NATIVE_TOOL_METADATA', 'MECHANICAL_NATIVE_TURN_METADATA', 'MECHANICAL_OPERATION_UNSUPPORTED', 'MECHANICAL_PROFILE', 'MECHANICAL_PROFILE_RETURN_JOIN_NOT_ADMITTED', 'MECHANICAL_PROTOCOL_CODE_PIN_ABSENT', 'MECHANICAL_PROTOCOL_PROFILE', 'NONFINITE_JSON', 'NONPROTECTED_CODE_BOUND', 'NONPROTECTED_CODE_CHANGED', 'NONPROTECTED_OWNER_CODE_PIN_ABSENT', 'NONPROTECTED_PRIOR_CANONICAL_OPEN_CHANGED', 'NONPROTECTED_PROJECTION_OPERATION_UNSUPPORTED', 'NONPROTECTED_PROJECTION_PROFILE_REQUIRED', 'NONPROTECTED_PROJECTION_REQUIRES_SELECTED_SOURCE', 'NONPROTECTED_PUBLIC_BINDING_SHAPE', 'NONPROTECTED_PUBLIC_CANONICAL_BINDING', 'NONPROTECTED_REGISTRATION_PARENT_CHANGED', 'NONPROTECTED_RELEASE_CANONICAL_OPEN_CHANGED', 'NONPROTECTED_RESERVED_ACTUAL_CHILD_DIFFERS', 'NONPROTECTED_SELECTED_ROOT_REQUIRED', 'NONPROTECTED_SOURCE_REGISTRATION_PIN', 'NONPROTECTED_SOURCE_REGISTRATION_SHAPE', 'NO_OBSERVABLE_OWNED_SCOPE', 'OBLIGATION_CONFLICT', 'OBLIGATION_NOT_DELIVERED', 'OBSERVATION_AFTER_RETURN_OR_SHAPE', 'OBSERVATION_BIND_SHAPE', 'OBSERVATION_ORDER', 'OBSERVATION_SOURCE_UNBOUND_OR_AFTER_RETURN', 'OBSERVED_EXCHANGE_CHANGED', 'OBSERVED_RECORD_SHAPE_OR_ORDINAL', 'OCCURRENCE_EXPORT_BOUND', 'ORDINARY_ABSENCE', 'ORDINARY_ACCEPTANCE', 'ORDINARY_ACCEPTANCE_BINDING', 'ORDINARY_ACTIVATION', 'ORDINARY_ARTIFACT_BOUND', 'ORDINARY_ARTIFACT_PIN', 'ORDINARY_CAPACITY', 'ORDINARY_CHILD', 'ORDINARY_CHILD_PARENT', 'ORDINARY_CODE_PIN_POPULATION', 'ORDINARY_CUSTODY', 'ORDINARY_DECISION', 'ORDINARY_DIGEST', 'ORDINARY_DISPATCH', 'ORDINARY_DISPATCH_EVENT', 'ORDINARY_DISPATCH_IDENTITY', 'ORDINARY_EXECUTION_ACCEPTED_CUSTODY', 'ORDINARY_EXECUTION_OBJECT', 'ORDINARY_EXECUTION_RECEIPT', 'ORDINARY_EXECUTION_RECORD', 'ORDINARY_EXECUTION_REF', 'ORDINARY_EXPORT_BOUND', 'ORDINARY_EXPORT_FIELDS', 'ORDINARY_EXPORT_IDENTITY', 'ORDINARY_EXPORT_STATUS', 'ORDINARY_FRESH_CHILD', 'ORDINARY_HISTORY_PROMOTION', 'ORDINARY_JOIN', 'ORDINARY_JOIN_RESULT_BINDING', 'ORDINARY_LOCATOR', 'ORDINARY_MEMBER', 'ORDINARY_MEMBER_CUSTODY', 'ORDINARY_MEMBER_POPULATION', 'ORDINARY_MEMBER_TOTAL', 'ORDINARY_MISSION', 'ORDINARY_MISSION_BOUND', 'ORDINARY_OCCURRENCES', 'ORDINARY_OPENING', 'ORDINARY_OPENING_BINDING', 'ORDINARY_OPENING_DIGEST', 'ORDINARY_OPEN_OID', 'ORDINARY_OWNER', 'ORDINARY_OWNER_PROFILE', 'ORDINARY_PACKET', 'ORDINARY_PACKET_PIN', 'ORDINARY_PAYLOAD', 'ORDINARY_PAYLOAD_BINDING', 'ORDINARY_POLICY', 'ORDINARY_POLICY_BINDING', 'ORDINARY_PROCESS', 'ORDINARY_PROCESS_CALL_PAIR', 'ORDINARY_PROCESS_CARRIER', 'ORDINARY_PROCESS_NOT_SUCCEEDED', 'ORDINARY_PROCESS_OUTPUT_BOUND', 'ORDINARY_PROCESS_OUTPUT_CARRIER', 'ORDINARY_PROCESS_RESULT_FIELDS', 'ORDINARY_PROSPECTIVE_POLICY_BINDING', 'ORDINARY_PROVIDER', 'ORDINARY_PROVIDER_BOUND', 'ORDINARY_PROVIDER_PIN', 'ORDINARY_PUBLIC_BINDING', 'ORDINARY_PUBLIC_BODY', 'ORDINARY_PUBLIC_OPEN', 'ORDINARY_PUBLIC_OPEN_BINDING', 'ORDINARY_PUBLIC_POPULATION', 'ORDINARY_PUBLIC_RECORD', 'ORDINARY_PUBLIC_RETAINED_ID', 'ORDINARY_REACTIVATION', 'ORDINARY_RECEIVER_ARGV', 'ORDINARY_RECEIVER_DISPATCH', 'ORDINARY_RECEIVER_PROCESS_BINDING', 'ORDINARY_RECEIVING', 'ORDINARY_RECORD_PIN', 'ORDINARY_RECORD_RANGE', 'ORDINARY_RECORD_ROLE', 'ORDINARY_RECORD_SOURCE', 'ORDINARY_RESULT', 'ORDINARY_RETURN', 'ORDINARY_RETURN_BINDING', 'ORDINARY_REVIEW_PUBLIC_POPULATION', 'ORDINARY_ROUTE_NOT_ACCEPTED', 'ORDINARY_SCOPE', 'ORDINARY_SCOPE_DIGEST', 'ORDINARY_SKILL_PIN', 'ORDINARY_SKILL_SOURCE', 'ORDINARY_SOURCE', 'ORDINARY_SOURCES', 'ORDINARY_SOURCE_ALIAS', 'ORDINARY_SOURCE_BINDING', 'ORDINARY_SOURCE_EVENT', 'ORDINARY_SOURCE_EVENT_BINDING', 'ORDINARY_SOURCE_PROVENANCE', 'ORDINARY_SPAWN', 'ORDINARY_STAGE_PROMOTION', 'ORDINARY_TEXT', 'ORDINARY_WIRE_BOUND', 'ORDINARY_WIRE_DIGEST', 'ORDINARY_WIRE_FIELDS', 'ORDINARY_WIRE_OBJECT', 'ORDINARY_WORK_RESULT', 'OUTSIDE_ALLOWED_READ_RANGE', 'OVERLAPPING_RECORD_LOCATORS', 'OWNED_STDIO_HOST_BINDING_CHANGED', 'OWNED_STDIO_HOST_BINDING_SHAPE', 'O_BINARY', 'O_NOFOLLOW', 'O_NONBLOCK', 'PENDING_OBSERVATION_COUNTERS', 'PENDING_STATE_ABSENT', 'PENDING_STATE_BYTE_BOUND', 'PENDING_STATE_CHANGED_DURING_READ', 'PENDING_STATE_COUNTERS', 'PENDING_STATE_FILE_KIND', 'PENDING_STATE_JSON', 'PENDING_STATE_JSON_CONSTANT', 'PENDING_STATE_JSON_NUMBER', 'PENDING_STATE_PATH', 'PENDING_STATE_SHAPE', 'PENDING_STATE_UNREADABLE', 'POLICY_QUALIFICATION_BINDING', 'POLICY_QUALIFICATION_FIELDS', 'PREPARE_OBLIGATION_SHAPE', 'PUBLIC_AUTHORIZATION_CHANGED', 'QUALIFICATION_ACQUISITION_PIN', 'QUALIFICATION_ACTUAL_CANDIDATE_BINDING', 'QUALIFICATION_CANDIDATE_NAMESPACE', 'QUALIFICATION_REVIEW_BINDING', 'QUALIFICATION_REVIEW_FIELDS', 'QUALIFICATION_REVIEW_NAMESPACE', 'QUALIFICATION_REVIEW_PIN', 'QUALIFICATION_REVIEW_PIN_CHANGED', 'RECORD_BYTE_BOUND', 'RECORD_COUNT_BOUND', 'RECORD_IDENTITY_SHAPE', 'RECORD_LOCATOR_SHAPE', 'RECORD_PARTIAL_OR_MULTIPLE_WIRE', 'RECORD_PIN_CHANGED', 'RECORD_RANGE_PAST_END', 'REGISTERED_SOURCE_REPLACEMENT_REFUSED', 'REQUEST_BYTE_BOUND', 'REQUEST_SHAPE', 'RESERVATION_SHAPE', 'RESULT_CLOSURE_BYTE_BOUND', 'RESULT_MEMBER_CLOSURE', 'RESUME_IDENTITY_UNAVAILABLE', 'RESUME_OBSERVATION_SHAPE', 'RETURN_SHAPE_OR_AUTHORITY_CLAIM', 'RETURN_SOURCE_CUTOFF_ABSENT', 'ROOT_ACCEPTANCE_EXACT_RESULT_OR_SCOPE_DIFFERS', 'SELECTED_ASSIGNMENT_ABSENT', 'SELECTED_EPISODE_ADMISSION_CHANGED', 'SELECTED_EPISODE_ASSIGNMENT_AMBIGUOUS', 'SELECTED_EPISODE_ASSIGNMENT_OR_CODE_CHANGED', 'SELECTED_EPISODE_CHANGED_DURING_READ', 'SELECTED_EPISODE_CUSTODY_CHANGED', 'SELECTED_EPISODE_CUSTODY_NAMESPACE', 'SELECTED_EPISODE_H0_BINDING_CHANGED', 'SELECTED_EPISODE_H0_STAGE_CHANGED', 'SELECTED_EPISODE_IMMUTABLE_CLOSURE_CHANGED', 'SELECTED_EPISODE_OBLIGATION_CHANGED', 'SELECTED_EPISODE_OBSERVATION_CHANGED', 'SELECTED_EPISODE_POLICY_CHANGED', 'SELECTED_EPISODE_PREFIX_CHANGED', 'SELECTED_EPISODE_PREFIX_HEADER_CHANGED', 'SELECTED_EPISODE_PREFIX_PHYSICAL_CHANGED', 'SELECTED_EPISODE_PREFIX_TRUNCATED', 'SELECTED_EPISODE_QUALIFICATION_REMOVED', 'SELECTED_EPISODE_RECORD_CHANGED', 'SELECTED_EPISODE_RETURN_JOIN_CHANGED', 'SOURCE_BOUNDARY_SUMMARY_BOUND', 'SOURCE_CHANGED_BEFORE_READ', 'SOURCE_CHANGED_DURING_READ', 'SOURCE_FILE_KIND', 'SOURCE_JSON_DEPTH_BOUND', 'SOURCE_METADATA_CHANGED', 'SOURCE_OWNER_ATTESTATION_OR_RELEASE_DIFFERS', 'SOURCE_OWNER_ATTESTATION_SHAPE', 'SOURCE_OWNER_BOUNDARY_CONTEXT_REQUIRED', 'SOURCE_OWNER_HOST_BINDING_CHANGED', 'SOURCE_OWNER_HOST_BINDING_SHAPE', 'SOURCE_OWNER_MODULE_PIN_CHANGED', 'SOURCE_OWNER_POLICY_CHANGED_DURING_READ', 'SOURCE_OWNER_QUALIFICATION_CHANGED_DURING_READ', 'SOURCE_OWNER_QUALIFICATION_REQUIRED', 'SOURCE_OWNER_VALIDATOR_ABSENT', 'SOURCE_PARTIAL_OR_UNSUPPORTED_WIRE', 'SOURCE_PATH_ALIAS', 'SOURCE_PHYSICAL_ID_CHANGED', 'SOURCE_PREFIX_OR_PHYSICAL_ID_CHANGED', 'SOURCE_RECORD_BYTE_BOUND', 'SOURCE_RECORD_ORDER', 'SOURCE_REGISTRATION_SHAPE', 'SOURCE_REPARSE', 'SOURCE_ROW_SHAPE', 'SOURCE_SESSION_CHANGED', 'SOURCE_SESSION_META', 'SOURCE_TOTAL_BYTE_BOUND', 'STATUS_IS_NONOBSERVING', 'TOOL_INPUT_BASE_SHAPE', 'TOTAL_RECORD_BYTE_BOUND', 'TYPED_PUBLIC_RECORD_BLOCK', 'TYPED_PUBLIC_RECORD_FIELDS', 'TYPED_PUBLIC_RECORD_MEANING', 'UNOBSERVED_RETURN_SCOPE', 'UNPREPARED_OBSERVATION', 'UNRESOLVED_RESUME_OBSERVATION', 'UNRESOLVED_SIGNAL', 'UNSUPPORTED_PENDING_OPERATION', 'USED_CHILD_CONTEXT_REFUSED', 'VISIBLE_PRE_USE_BLOCK_ABSENT', 'VISIBLE_PRE_USE_FIELD_SHAPE', 'VISIBLE_PRE_USE_MEANING'))

# Closed observation only. This code never returns an owner result or authorizes
# an effect. The source reason codebook below is generated once from the three
# exact frozen source modules, then sealed with this reviewed harness.
MCP_DIAGNOSTIC_SCHEMA='dg18.h0-mcp-failure.v2'
MCP_DIAGNOSTIC_STAGES=frozenset(('ARGUMENTS','WAIT_COMPLETION','SOURCE_ROWS','CALL_SELECTION','OUTPUT_SELECTION','CONTEXT','COMMAND_RESPONSE','RESPONSE_JSON'))
MCP_DIAGNOSTIC_CLASSES=frozenset(('UNQUALIFIED_RECEIPT','OWNER_REFUSAL','NONZERO_RECEIPT','ZERO_EXIT_VALIDATION_FAILURE','MCP_SERVER_REFUSAL'))
MCP_DIAGNOSTIC_SOURCE_SITES=frozenset(('UNKNOWN','PROTOCOL_PARSE','PROTOCOL_ARGUMENTS','PROTOCOL_CALL','PROTOCOL_FRAMING','PROTOCOL_RESPONSE','OBSERVATION_COMMAND','OBSERVATION_MECHANICAL','OBSERVATION_RESOLVE','OBSERVATION_ORDER'))
MCP_DIAGNOSTIC_CEILING={'authority':'NONE','canonical_currentness':False,'recovery_authority':False,'epoch_authority':False,'effect_authority':False,'independent_children':'UNCHANGED','actual_child_result_consumer':'UNQUALIFIED','same_failed_scope_retry':'CONDITIONAL_UNQUALIFIED'}

def independent_reviewer(value):
 return type(value) is str and value==REVIEWER and value.startswith('/root/') and all(value!=author and not value.startswith(author+'/') for author in REVIEW_EXCLUDED_AUTHORS)

def mcp_source_site(error,protocol,observation):
 # Compare the actual selected source filenames, then emit only fixed names.
 # The protocol can be compiled anew by the source owner for each response.
 sites={}
 for module,names in ((protocol,{'parse':'PROTOCOL_PARSE','parsed_arguments':'PROTOCOL_ARGUMENTS','call_input':'PROTOCOL_CALL','framing_text':'PROTOCOL_FRAMING','response_text':'PROTOCOL_RESPONSE'}),(observation,{'command_response':'OBSERVATION_COMMAND','mechanical_command_response':'OBSERVATION_MECHANICAL','resolve_record':'OBSERVATION_RESOLVE','before':'OBSERVATION_ORDER'})):
  for name,label in names.items():
   function=getattr(module,name,None);code=getattr(function,'__code__',None)
   if code is not None:sites[(code.co_filename,name)]=label
 result='UNKNOWN';frame=error.__traceback__
 for _ in range(64):
  if frame is None:break
  code=frame.tb_frame.f_code;label=sites.get((code.co_filename,code.co_name))
  if label is not None:result=label
  frame=frame.tb_next
 return result


MCP_DIAGNOSTIC_QUALIFICATION_STAGES=frozenset(('SELECTED_ROWS','ARGUMENTS','SELECTED_CALL','CALL_OUTPUT_ASSOCIATION','UNIQUE_OCCURRENCE','METADATA','LOCATOR_SHAPE','PHYSICAL_ORDER','TIMESTAMP_ORDER','FRAMING','SERVER_REFUSAL_GRAMMAR','RECEIPT_JSON','RECEIPT_BINDING','RECEIPT_FIELDS','COMPLETE'))
MCP_SERVER_EXCEPTION_CODES={'ValueError':'VALUE_ERROR','TypeError':'TYPE_ERROR','KeyError':'KEY_ERROR','OSError':'OS_ERROR','FileNotFoundError':'FILE_NOT_FOUND','PermissionError':'PERMISSION_ERROR','TimeoutExpired':'SUBPROCESS_TIMEOUT','CalledProcessError':'SUBPROCESS_FAILURE','SubprocessError':'SUBPROCESS_ERROR','JSONDecodeError':'JSON_DECODE','UnicodeDecodeError':'UNICODE_DECODE','UnicodeEncodeError':'UNICODE_ENCODE','Refusal':'SOURCE_REFUSAL','HoldObservationRefusal':'SOURCE_HOLD_REFUSAL','QuiescenceRefusal':'SOURCE_QUIESCENCE_REFUSAL'}
MCP_SERVER_REASON_CODES=MCP_SOURCE_REASON_CODES|frozenset(('H0_OWNER_OBSERVATION_REFUSED','CLOSED_LOAD_PIN_SHAPE', 'CLOSED_MCP_ARGUMENTS', 'CLOSED_MCP_TOOL_REQUIRED', 'CLOSED_MECHANICAL_CHILD_CHANGED', 'CLOSED_MECHANICAL_SELECTION_CHANGED', 'CLOSED_MECHANICAL_SEQUENCE', 'CLOSED_PENDING_OPERATION', 'CURRENT_OBSERVATION_CHANGED', 'EXACT_BIND_RETRY_REQUIRED', 'EXACT_MECHANICAL_ASSIGNMENT_REQUIRED', 'EXACT_SELECTED_SKILL_REQUIRED', 'FIXED_SOURCE_OWNER_REQUIRED', 'LATER_OBSERVATION_REQUIRED', 'LOAD_WORKER_SCOPE', 'MCP_REQUEST_BOUND', 'MECHANICAL_ACTUAL_PENDING_NATIVE_CALL_REQUIRED', 'MECHANICAL_CHILD_OUTPUT_BOUND', 'MECHANICAL_CODE_CHANGED_DURING_CALL', 'MECHANICAL_CODE_OR_LIFECYCLE_CHANGED', 'MECHANICAL_NATIVE_TOOL_METADATA', 'MECHANICAL_PYTHON_SELECTION_CHANGED', 'MECHANICAL_SELECTION_CHANGED', 'MECHANICAL_SERVER_CODE_CHANGED', 'MECHANICAL_SOURCE_NOT_SELECTED', 'PRIOR_OBSERVATION_CHANGED', 'SOURCE_OWNER_BOUND', 'TOOL_PIN_BYTE_BOUND', 'TOOL_PIN_CHANGED', 'TOOL_PIN_PATH_ALIAS'))

def mcp_server_refusal_text(text):
 """Recognize only the pinned server's bounded alternative text grammar.

 This is evidence of matching refusal text, not a child exit/owner receipt.
 The exception name and message themselves are never returned or published.
 """
 if type(text) is not str:return None
 parts=text.split(':',2)
 if len(parts)!=3 or parts[0]!='MECHANICAL_REFUSED' or re.fullmatch('[A-Za-z_][A-Za-z0-9_]{0,63}',parts[1]) is None or len(parts[2])>256:return None
 return {'server_exception':MCP_SERVER_EXCEPTION_CODES.get(parts[1],'UNKNOWN'),
         'server_reason':parts[2] if parts[2] in MCP_SERVER_REASON_CODES else 'UNKNOWN',
         'server_text_sha256':sha(text.encode('utf-8'))}

def mcp_failure_projection(*,phase,protocol,observation,operation,arguments,records,call,outputs,stage,error):
 """Project an exact selected envelope without accepting or repeating its use.

 Only cached rows from the driver's original bounded source read are examined.
 Full source custody and all accepting predicates still belong exclusively to
 the unchanged command_response and existing owner/reader path.
 """
 reason=error.args[0] if len(error.args)==1 and type(error.args[0]) is str else None
 result={'schema':MCP_DIAGNOSTIC_SCHEMA,'phase':phase,'operation':operation,'site':stage,
  'source_error':reason if reason in MCP_SOURCE_REASON_CODES else 'UNKNOWN',
  'source_site':mcp_source_site(error,protocol,observation),'classification':'UNQUALIFIED_RECEIPT',
  'qualification_stage':'SELECTED_ROWS','receipt_binding':'UNQUALIFIED','exit_code':None,'owner_reason':'NOT_APPLICABLE',
  'call_sha256':None,'output_sha256':None,'stdout_sha256':None,'stderr_sha256':None,
  'server_exception':None,'server_reason':None,'server_text_sha256':None,
  'effect_status':'UNCONFIRMED','authority':'NONE'}
 try:
  need(type(records) is list and type(call) is dict and type(outputs) is list and len(outputs)==1,'DIAGNOSTIC_ENVELOPE_UNQUALIFIED')
  result['qualification_stage']='ARGUMENTS'
  wire=protocol.arguments_wire(arguments);parsed,_=protocol.parsed_arguments(wire)
  need(parsed==arguments and parsed['operation']==operation,'DIAGNOSTIC_ENVELOPE_UNQUALIFIED')
  result['qualification_stage']='SELECTED_CALL'
  candidates=[row for row in records if protocol.is_call(row['row']['payload']) and row['row']['payload'].get('arguments')==wire]
  need(candidates and candidates[-1]==call,'DIAGNOSTIC_ENVELOPE_UNQUALIFIED')
  result['qualification_stage']='CALL_OUTPUT_ASSOCIATION'
  call_row=call['row'];output=outputs[0];output_row=output['row'];payload=call_row['payload'];answer=output_row['payload']
  need(protocol.call_input(payload)==wire and protocol.is_output(answer) and answer.get('call_id')==payload['call_id'],'DIAGNOSTIC_ENVELOPE_UNQUALIFIED')
  # Repeated argument wire is legitimate for the distinct exact retry. A reused
  # call ID or another output is not. Never search for an alternative result.
  result['qualification_stage']='UNIQUE_OCCURRENCE'
  matching_calls=[row for row in records if row['row']['payload'].get('type')=='function_call' and row['row']['payload'].get('call_id')==payload['call_id']]
  matching_outputs=[row for row in records if protocol.is_output(row['row']['payload']) and row['row']['payload'].get('call_id')==payload['call_id']]
  need(matching_calls==[call] and matching_outputs==[output],'DIAGNOSTIC_ENVELOPE_UNQUALIFIED')
  result['qualification_stage']='METADATA'
  turn=payload.get('internal_chat_message_metadata_passthrough',{}).get('turn_id')
  need(call_row['type']==output_row['type']=='response_item' and protocol.metadata_ok(call_row,turn) and protocol.metadata_ok(output_row,turn),'DIAGNOSTIC_ENVELOPE_UNQUALIFIED')
  result['qualification_stage']='LOCATOR_SHAPE'
  for record in (call,output):
   locator=record['locator'];need(type(locator) is dict and set(locator)=={'offset','bytes','sha256','embedded_ordinal','physical_line'},'DIAGNOSTIC_ENVELOPE_UNQUALIFIED')
   need(all(type(locator[k]) is int for k in ('offset','bytes','embedded_ordinal','physical_line')) and 0<=locator['offset']<2*1024*1024 and 0<locator['bytes']<=2*1024*1024 and 0<=locator['embedded_ordinal'] and 0<locator['physical_line'] and locator['embedded_ordinal']==record['row']['ordinal'] and type(locator['sha256']) is str and re.fullmatch('[0-9a-f]{64}',locator['sha256']),'DIAGNOSTIC_ENVELOPE_UNQUALIFIED')
  result['qualification_stage']='PHYSICAL_ORDER'
  need(call['locator']['offset']+call['locator']['bytes']<=output['locator']['offset'] and call['locator']['embedded_ordinal']<output['locator']['embedded_ordinal'] and call['locator']['physical_line']<output['locator']['physical_line'],'DIAGNOSTIC_ENVELOPE_UNQUALIFIED')
  result['qualification_stage']='TIMESTAMP_ORDER'
  observation.before({'path':'SAME_ORIGINAL_SNAPSHOT','timestamp':call_row['timestamp'],'locator':call['locator']},{'path':'SAME_ORIGINAL_SNAPSHOT','timestamp':output_row['timestamp'],'locator':output['locator']})
  result['qualification_stage']='FRAMING'
  framed=protocol.framing_text(answer)
  if framed.startswith('MECHANICAL_REFUSED:'):
   result['qualification_stage']='SERVER_REFUSAL_GRAMMAR'
   refusal=mcp_server_refusal_text(framed)
   need(refusal is not None,'DIAGNOSTIC_ENVELOPE_UNQUALIFIED')
   result.update(classification='MCP_SERVER_REFUSAL',qualification_stage='COMPLETE',receipt_binding='ENVELOPE_ONLY',call_sha256=call['locator']['sha256'],output_sha256=output['locator']['sha256'],**refusal)
   validate_mcp_failure(result)
   return result
  result['qualification_stage']='RECEIPT_JSON'
  receipt=protocol.parse(framed)
  result['qualification_stage']='RECEIPT_BINDING'
  keys={'schema','selection_sha256','operation','request_sha256','exit_code','stdout','stdout_sha256','stderr_sha256'}
  need(type(receipt) is dict and set(receipt)==keys and receipt['schema']==protocol.RESPONSE and receipt['selection_sha256']==parsed['selection_sha256'] and receipt['operation']==operation and receipt['request_sha256']==sha(parsed['request_json'].encode('utf-8')),'DIAGNOSTIC_ENVELOPE_UNQUALIFIED')
  result['qualification_stage']='RECEIPT_FIELDS'
  need(type(receipt['exit_code']) is int and -65536<=receipt['exit_code']<=65536 and type(receipt['stdout']) is str and len(receipt['stdout'].encode('utf-8'))<=128*1024 and receipt['stdout_sha256']==sha(receipt['stdout'].encode('utf-8')) and type(receipt['stderr_sha256']) is str and re.fullmatch('[0-9a-f]{64}',receipt['stderr_sha256']),'DIAGNOSTIC_ENVELOPE_UNQUALIFIED')
  classification='ZERO_EXIT_VALIDATION_FAILURE' if receipt['exit_code']==0 else 'NONZERO_RECEIPT';owner_reason='NOT_APPLICABLE'
  if receipt['exit_code']==2:
   try:
    body=protocol.parse(receipt['stdout'])
    if type(body) is dict and set(body)==set(MCP_DIAGNOSTIC_CEILING)|{'status','reason'} and matches(body,MCP_DIAGNOSTIC_CEILING) and body['status']=='PENDING_OPERATION_REFUSED' and type(body['reason']) is str:
     classification='OWNER_REFUSAL';owner_reason=body['reason'] if body['reason'] in MCP_SOURCE_REASON_CODES else 'UNKNOWN'
   except (ValueError,TypeError,KeyError):pass
  result.update(classification=classification,qualification_stage='COMPLETE',receipt_binding='ENVELOPE_ONLY',exit_code=receipt['exit_code'],owner_reason=owner_reason,call_sha256=call['locator']['sha256'],output_sha256=output['locator']['sha256'],stdout_sha256=receipt['stdout_sha256'],stderr_sha256=receipt['stderr_sha256'])
 except (OSError,ValueError,TypeError,KeyError,AttributeError,IndexError,Refusal):pass
 validate_mcp_failure(result)
 return result

def validate_mcp_failure(value):
 keys={'schema','phase','operation','site','source_error','source_site','classification','qualification_stage','receipt_binding','exit_code','owner_reason','call_sha256','output_sha256','stdout_sha256','stderr_sha256','server_exception','server_reason','server_text_sha256','effect_status','authority'}
 need(type(value) is dict and set(value)==keys and value['schema']==MCP_DIAGNOSTIC_SCHEMA and value['effect_status']=='UNCONFIRMED' and value['authority']=='NONE','DIAGNOSTIC_SHAPE')
 for key,allowed in (('phase',PROGRESS_PHASES),('operation',{'LOAD','DELIVER','BIND'}),('site',MCP_DIAGNOSTIC_STAGES),('source_error',MCP_SOURCE_REASON_CODES|{'UNKNOWN'}),('source_site',MCP_DIAGNOSTIC_SOURCE_SITES),('classification',MCP_DIAGNOSTIC_CLASSES),('qualification_stage',MCP_DIAGNOSTIC_QUALIFICATION_STAGES)):
  need(type(value[key]) is str and value[key] in allowed,'DIAGNOSTIC_ENUM')
 hashes=('call_sha256','output_sha256','stdout_sha256','stderr_sha256')
 server_fields=('server_exception','server_reason','server_text_sha256')
 if value['classification']=='UNQUALIFIED_RECEIPT':
  need(value['qualification_stage']!='COMPLETE' and value['receipt_binding']=='UNQUALIFIED' and value['exit_code'] is None and value['owner_reason']=='NOT_APPLICABLE' and all(value[k] is None for k in hashes+server_fields),'DIAGNOSTIC_UNQUALIFIED_FIELDS')
 elif value['classification']=='MCP_SERVER_REFUSAL':
  need(value['qualification_stage']=='COMPLETE' and value['receipt_binding']=='ENVELOPE_ONLY' and value['exit_code'] is None and value['owner_reason']=='NOT_APPLICABLE' and value['stdout_sha256'] is None and value['stderr_sha256'] is None,'DIAGNOSTIC_SERVER_NOT_OWNER_RECEIPT')
  need(all(type(value[k]) is str and re.fullmatch('[0-9a-f]{64}',value[k]) for k in ('call_sha256','output_sha256','server_text_sha256')) and type(value['server_exception']) is str and value['server_exception'] in set(MCP_SERVER_EXCEPTION_CODES.values())|{'UNKNOWN'} and type(value['server_reason']) is str and value['server_reason'] in MCP_SERVER_REASON_CODES|{'UNKNOWN'},'DIAGNOSTIC_SERVER_REFUSAL_FIELDS')
 else:
  need(value['qualification_stage']=='COMPLETE' and value['receipt_binding']=='ENVELOPE_ONLY' and type(value['exit_code']) is int and -65536<=value['exit_code']<=65536 and all(type(value[k]) is str and re.fullmatch('[0-9a-f]{64}',value[k]) for k in hashes) and all(value[k] is None for k in server_fields),'DIAGNOSTIC_RECEIPT_FIELDS')
  if value['classification']=='OWNER_REFUSAL':need(value['exit_code']==2 and type(value['owner_reason']) is str and value['owner_reason'] in MCP_SOURCE_REASON_CODES|{'UNKNOWN'},'DIAGNOSTIC_OWNER_REASON')
  else:need(value['owner_reason']=='NOT_APPLICABLE' and ((value['classification']=='ZERO_EXIT_VALIDATION_FAILURE' and value['exit_code']==0) or (value['classification']=='NONZERO_RECEIPT' and value['exit_code']!=0)),'DIAGNOSTIC_RECEIPT_STATUS')
 return value
