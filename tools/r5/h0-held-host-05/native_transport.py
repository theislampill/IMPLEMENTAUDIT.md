"""One owned official app-server. Captures actual wire; synthesizes no rows."""
import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import threading
import time

class Native:
 def __init__(self,binary,home,cwd,evidence):
  self.evidence=Path(evidence);self.evidence.mkdir(mode=0o700);self.lock=threading.Lock();self.q=queue.Queue(maxsize=8192);self.request_id=0;self.count=0;self.total=0;self.failed=None
  self.capture=(self.evidence/'protocol.jsonl').open('xb');self.err=(self.evidence/'stderr.log').open('xb')
  self.env={'PATH':'/usr/bin:/bin','HOME':str(home),'CODEX_HOME':str(home),'LANG':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1'}
  self.argv=[str(binary),'app-server','--listen','stdio://']
  self.proc=subprocess.Popen(self.argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=cwd,env=self.env,start_new_session=True)
  try:self.pidfd=os.pidfd_open(self.proc.pid)
  except BaseException:
   self.proc.kill();self.proc.wait(timeout=4)
   for stream in (self.proc.stdin,self.proc.stdout,self.proc.stderr,self.capture,self.err):stream.close()
   raise
  self.reader=threading.Thread(target=self._read,daemon=True);self.stderr_reader=threading.Thread(target=self._stderr,daemon=True);self.reader.start();self.stderr_reader.start()
 def record(self,direction,value):
  with self.lock:
   raw=(json.dumps({'sequence':self.count+1,'direction':direction,'value':value},sort_keys=True)+'\n').encode()
   if self.count>=8192 or self.total+len(raw)>32*1024*1024:raise ValueError('NATIVE_CAPTURE_BOUND')
   self.capture.write(raw);self.capture.flush();self.count+=1;self.total+=len(raw)
 def _read(self):
  try:
   while True:
    line=self.proc.stdout.readline(2*1024*1024+1)
    if not line:break
    if len(line)>2*1024*1024 or not line.endswith(b'\n'):raise ValueError('NATIVE_WIRE_BOUND')
    self.record('recv_raw',line.decode());self.q.put(json.loads(line),timeout=2)
  except BaseException as error:self.failed=error
  finally:
   try:self.q.put(EOFError('native stdout closed'),timeout=1)
   except queue.Full:pass
 def _stderr(self):
  total=0
  try:
   while True:
    block=self.proc.stderr.read(65536)
    if not block:break
    total+=len(block)
    if total>8*1024*1024:raise ValueError('NATIVE_STDERR_BOUND')
    self.err.write(block);self.err.flush()
  except BaseException as error:self.failed=error
 def send(self,value):
  if self.failed:raise self.failed
  raw=(json.dumps(value)+'\n').encode()
  if len(raw)>2*1024*1024:raise ValueError('NATIVE_INPUT_BOUND')
  self.record('send',value);self.proc.stdin.write(raw);self.proc.stdin.flush()
 def take(self,timeout):
  if self.failed:raise self.failed
  item=self.q.get(timeout=timeout)
  if isinstance(item,BaseException):raise item
  return item
 def rpc(self,method,params,timeout=30):
  self.request_id+=1;ident=self.request_id;self.send({'id':ident,'method':method,'params':params});deadline=time.monotonic()+timeout
  while time.monotonic()<deadline:
   value=self.take(deadline-time.monotonic())
   if value.get('id')==ident:
    if 'error' in value:raise ValueError('ACTUAL_NATIVE_RPC_REFUSED')
    return value.get('result')
   if 'id' in value and 'method' in value:raise ValueError('UNEXPECTED_NATIVE_SERVER_REQUEST')
  raise TimeoutError('native RPC')
 def wait_turn(self,thread_id,timeout=90):
  deadline=time.monotonic()+timeout;seen=[]
  while time.monotonic()<deadline:
   value=self.take(deadline-time.monotonic());seen.append(value)
   if len(seen)>8192:raise ValueError('NATIVE_TURN_EVENT_BOUND')
   if value.get('method')=='turn/completed' and value.get('params',{}).get('threadId')==thread_id:return value,seen
   if 'id' in value and 'method' in value:raise ValueError('UNEXPECTED_NATIVE_SERVER_REQUEST')
  raise TimeoutError('native turn')
 def close(self):
  if not self.proc.stdin.closed:self.proc.stdin.close()
  killed=False
  try:self.proc.wait(timeout=5)
  except subprocess.TimeoutExpired:signal.pidfd_send_signal(self.pidfd,signal.SIGKILL);killed=True;self.proc.wait(timeout=4)
  self.reader.join(timeout=3);self.stderr_reader.join(timeout=3);os.close(self.pidfd)
  joined=not self.reader.is_alive() and not self.stderr_reader.is_alive()
  if joined:self.capture.close();self.err.close();self.proc.stdout.close();self.proc.stderr.close()
  return {'direct_child_exited':self.proc.returncode is not None,'returncode':self.proc.returncode,'readers_joined':joined,'pidfd_kill_used':killed,'all_descendants_reaped':'OUTER_SUBREAPER_MUST_CHECK'}
