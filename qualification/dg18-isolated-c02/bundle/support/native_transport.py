#!/usr/bin/env python3
"""Owned Codex stdio transport. No credential reuse or real-home state."""
from __future__ import annotations
import json,os,queue,signal,subprocess,threading,time
from pathlib import Path

DIAGNOSTIC_SEND_STAGES = ('BEFORE_SEND', 'RECORD', 'WRITE', 'FLUSH')
DIAGNOSTIC_NATIVE_FIELDS = ('first_ingress', 'first_send', 'send_cleanup', 'disconnect')
DIAGNOSTIC_REASONS = (
    'COMPACTION_WITH_OUTSTANDING_WORK',
    'DUPLICATE_ITEM',
    'DUPLICATE_OR_UNKNOWN_REQUEST_ID',
    'EXISTING_OWNER_QUEUE_REQUIRED',
    'FOREIGN_OR_INACTIVE_NATIVE_TURN',
    'FOREIGN_OR_UNKNOWN_NATIVE_SCOPE',
    'FOREIGN_REQUEST_SCOPE',
    'FRESH_CANARY_EARLY_MCP_SCOPE_MISMATCH',
    'FRESH_CANARY_PENDING_HOOK',
    'FRESH_CANARY_RAW_ITEM_STATUS',
    'FRESH_CANARY_TOOL_OR_RESULT_AUTHORITY_NOT_ADMITTED',
    'FRESH_CANARY_UNKNOWN_WIRE_SHAPE',
    'FRESH_CANARY_UNSOLICITED_EARLY_MCP',
    'INITIALIZATION_ORDER',
    'MCP_STARTUP_NOT_SETTLED',
    'MISSING_IMMEDIATE_CANCELLATION',
    'NATIVE_INGRESS_CLOSED_OR_UNKNOWN',
    'NATIVE_RESPONSE_ID_TYPE',
    'NATIVE_SERVER_REQUEST_NOT_ADMITTED',
    'NO_COMPLETE_CURRENT_OWNER_QUIESCENCE_FENCE',
    'OUTGOING_EFFECT_UNKNOWN',
    'OVERLAPPING_TURN_NOT_ADMITTED',
    'OWNED_QUEUE_REJECTED_INGRESS',
    'PINNED_LIFECYCLE_VALIDATOR_REQUIRED',
    'RAW_TOOLS_OR_UNKNOWN_ITEM',
    'READ_FENCE_SCOPE',
    'REQUEST_BEFORE_INITIALIZATION',
    'REQUEST_OUTSIDE_CONSERVATIVE_PROFILE',
    'REQUEST_PARAMS_SHAPE',
    'RESPONSE_SHAPE',
    'SECOND_SESSION_OR_THREAD_NOT_ADMITTED',
    'SELECTED_THREAD_RESPONSE_CHANGED',
    'THREAD_CREATION_SCOPE',
    'TOOLS_OR_UNKNOWN_ITEM_NOT_ADMITTED',
    'TURN_CREATION_SCOPE',
    'TURN_TERMINAL_WITH_PENDING_OR_UNKNOWN_WORK',
    'UNEXPECTED_NATIVE_THREAD',
    'UNKNOWN',
    'UNKNOWN_DELTA_ITEM',
    'UNKNOWN_DUPLICATE_OR_FAILED_RESPONSE',
    'UNKNOWN_ITEM_COMPLETION',
    'UNKNOWN_NATIVE_EVENT_REQUIRES_PROFILE_REVIEW',
    'UNKNOWN_NATIVE_NOTIFICATION_SHAPE',
    'UNKNOWN_NATIVE_RECORD',
    'UNKNOWN_NATIVE_RESPONSE_ENVELOPE',
    'UNKNOWN_OWNER_REQUEST',
    'UNREQUESTED_NATIVE_TURN',
    'UNSELECTED_NATIVE_RESUME',
)

def diagnostic_category(exc):
    category = 'OTHER'
    for exception, code in ((TypeError, 'TYPE_ERROR'), (KeyError, 'KEY_ERROR'),
        (IndexError, 'INDEX_ERROR'), (AttributeError, 'ATTRIBUTE_ERROR'), (ValueError, 'VALUE_ERROR'),
        (RuntimeError, 'RUNTIME_ERROR'), (AssertionError, 'ASSERTION_ERROR'), (TimeoutError, 'TIMEOUT'),
        (subprocess.TimeoutExpired, 'SUBPROCESS_TIMEOUT'), (FileNotFoundError, 'FILE_NOT_FOUND'),
        (PermissionError, 'PERMISSION_ERROR'), (OSError, 'OS_ERROR'), (MemoryError, 'MEMORY_ERROR'),
        (KeyboardInterrupt, 'INTERRUPTED'), (SystemExit, 'SYSTEM_EXIT')):
        if isinstance(exc, exception):
            category = code
            break
    return category


def diagnostic_reason(exc):
    """Only fixed refusal codes; never stringify an exception or inspect its private data."""
    args = BaseException.args.__get__(exc, BaseException)
    if (type(args) is tuple and len(args) == 1 and type(args[0]) is str
            and len(args[0]) <= 64 and args[0] in DIAGNOSTIC_REASONS):
        return args[0]
    return 'UNKNOWN'


class Native:
 def __init__(self,binary,home,cwd,evidence,extra=(),ledger_factory=None):
  self._diagnostic_first={}
  self.evidence=Path(evidence); self.evidence.mkdir(parents=True,exist_ok=True)
  self.events=[];self.lock=threading.Lock();self.q=queue.Queue();self.request_id=0
  self.capture=(self.evidence/'protocol.jsonl').open('x',encoding='utf-8')
  self.stderr=(self.evidence/'stderr.log').open('x',encoding='utf-8')
  self.env={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':str(home),'CODEX_HOME':str(home),'LANG':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1'}
  self.argv=[str(binary),'app-server','--listen','stdio://',*extra]
  self.proc=subprocess.Popen(self.argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,cwd=cwd,env=self.env,text=True,bufsize=1,start_new_session=True)
  self.ledger=ledger_factory(self.q,native_process=self.proc) if ledger_factory else None
  self.record('lifecycle',{'event':'started','pid':self.proc.pid,'argv':self.argv,'cwd':str(cwd),'home':str(home),'environment_keys':sorted(self.env)})
  self.reader=threading.Thread(target=self._read,name='native-stdout',daemon=True);self.reader.start()
 def _observe_failure(self,name,exc,stage=None):
  # Best effort only: diagnostic allocation must not replace an operative refusal.
  try:
   failure={'category':diagnostic_category(exc),'reason':diagnostic_reason(exc)}
   if stage is not None:failure['stage']=stage
   self._diagnostic_first.setdefault(name,failure)
  except BaseException:pass
 def diagnostic_snapshot(self):
  # First records are never mutated; return copies, including for partial init.
  first=getattr(self,'_diagnostic_first',{})
  return {name:dict(first[name]) if name in first else None for name in DIAGNOSTIC_NATIVE_FIELDS}
 def record(self,direction,value):
  with self.lock:
   row={'sequence':len(self.events)+1,'monotonic_ns':time.monotonic_ns(),'direction':direction,'value':value}
   self.events.append(row);self.capture.write(json.dumps(row,sort_keys=True)+'\n');self.capture.flush();os.fsync(self.capture.fileno())
 def _read(self):
  try:
   for line in self.proc.stdout:
    self.record('recv_raw',line)
    try: obj=json.loads(line)
    except Exception as exc: self.q.put(RuntimeError('native non-JSON output'));return
    try:
     if self.ledger:self.ledger.ingest(obj)
     else:self.q.put(obj)
    except Exception as exc:
     self._observe_failure('first_ingress',exc)
     self.record('ledger_refusal',{'reason':str(exc)});self.q.put(exc);return
  finally:
   if self.ledger:
    try:self.ledger.disconnect()
    except Exception as exc:
     self._observe_failure('disconnect',exc)
     pass
   self.q.put(EOFError('native stdout closed'))
 def send(self,value):
  try:
   if self.ledger:self.ledger.before_send(value)
  except BaseException as exc:
   self._observe_failure('first_send',exc,'BEFORE_SEND')
   raise
  try:self.record('send',value)
  except BaseException as exc:
   self._observe_failure('first_send',exc,'RECORD')
   raise
  try:
   try:self.proc.stdin.write(json.dumps(value)+'\n')
   except BaseException as exc:
    self._observe_failure('first_send',exc,'WRITE')
    raise
   try:self.proc.stdin.flush()
   except BaseException as exc:
    self._observe_failure('first_send',exc,'FLUSH')
    raise
  except BaseException:
   if self.ledger:
    try:self.ledger.send_failed()
    except BaseException as exc:
     self._observe_failure('send_cleanup',exc)
     raise
   raise
 def take(self,timeout):
  item=self.q.get(timeout=timeout)
  if isinstance(item,Exception):raise item
  return item
 def rpc(self,method,params,timeout=20):
  self.request_id+=1;ident=self.request_id;self.send({'id':ident,'method':method,'params':params});deadline=time.monotonic()+timeout
  while time.monotonic()<deadline:
   obj=self.take(deadline-time.monotonic())
   if obj.get('id')==ident:
    if 'error' in obj:raise RuntimeError(json.dumps(obj['error']))
    return obj.get('result')
   if 'id' in obj and 'method' in obj:raise RuntimeError('unexpected server request '+obj['method'])
  raise TimeoutError(method)
 def wait_turn(self,thread_id,timeout=30):
  deadline=time.monotonic()+timeout;seen=[]
  while time.monotonic()<deadline:
   obj=self.take(deadline-time.monotonic());seen.append(obj)
   if obj.get('method')=='turn/completed' and obj.get('params',{}).get('threadId')==thread_id:return obj,seen
   if 'id' in obj and 'method' in obj:raise RuntimeError('unexpected native server request '+obj['method'])
  raise TimeoutError('turn completion')
 def close(self):
  if not self.proc.stdin.closed:self.proc.stdin.close()
  escalations=[]
  try:self.proc.wait(timeout=5)
  except subprocess.TimeoutExpired:
   escalations.append('SIGTERM_OWN_PROCESS_GROUP');os.killpg(self.proc.pid,signal.SIGTERM)
   try:self.proc.wait(timeout=3)
   except subprocess.TimeoutExpired:
    escalations.append('SIGKILL_OWN_PROCESS_GROUP');os.killpg(self.proc.pid,signal.SIGKILL);self.proc.wait(timeout=3)
  self.reader.join(timeout=3)
  row={'event':'terminated','pid':self.proc.pid,'returncode':self.proc.returncode,'reader_joined':not self.reader.is_alive(),'escalations':escalations}
  self.record('lifecycle',row);self.capture.close();self.stderr.close();return row
