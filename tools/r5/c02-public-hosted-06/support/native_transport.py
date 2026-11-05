#!/usr/bin/env python3
"""Owned Codex stdio transport. No credential reuse or real-home state."""
from __future__ import annotations
import json,os,queue,signal,subprocess,threading,time
from pathlib import Path

class Native:
 def __init__(self,binary,home,cwd,evidence,extra=(),ledger_factory=None):
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
     self.record('ledger_refusal',{'reason':str(exc)});self.q.put(exc);return
  finally:
   if self.ledger:
    try:self.ledger.disconnect()
    except Exception:pass
   self.q.put(EOFError('native stdout closed'))
 def send(self,value):
  if self.ledger:self.ledger.before_send(value)
  self.record('send',value)
  try:self.proc.stdin.write(json.dumps(value)+'\n');self.proc.stdin.flush()
  except BaseException:
   if self.ledger:self.ledger.send_failed()
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
