#!/usr/bin/env python3
"""Owned Codex stdio transport. No credential reuse or real-home state."""
from __future__ import annotations
import hashlib,json,os,queue,signal,shutil,subprocess,threading,time
from pathlib import Path
from owned_resources import bookend,processes,digest,inventory
from namespace_process_custody import PidfdCustody, CustodyError, observe

class Native:
 def __init__(self,binary,home,cwd,evidence,extra=(),server_handler=None):
  self.evidence=Path(evidence); self.evidence.mkdir(parents=True,exist_ok=True)
  self.server_handler=server_handler
  self.custody=PidfdCustody()
  self.home=Path(home);self.owned_tmp=self.evidence/'owned-tmp';self.owned_tmp.mkdir(exist_ok=False)
  self.before=bookend([self.home,self.owned_tmp])
  (self.evidence/'RESOURCE_BEFORE.json').write_text(json.dumps(self.before,indent=2)+'\n')
  self.launch_dir=self.evidence/'owned-binary';self.launch_dir.mkdir(exist_ok=False)
  self.original_binary=Path(binary).resolve(strict=True);self.launch_binary=self.launch_dir/'codex'
  shutil.copyfile(self.original_binary,self.launch_binary);self.launch_binary.chmod(0o755)
  self.binary_sha256=digest(self.launch_binary)
  self.events=[];self.lock=threading.Lock();self.q=queue.Queue();self.request_id=0
  self.capture=(self.evidence/'protocol.jsonl').open('x',encoding='utf-8')
  self.stderr=(self.evidence/'stderr.log').open('x',encoding='utf-8')
  self.env={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':str(home),'CODEX_HOME':str(home),'LANG':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1','TMPDIR':str(self.owned_tmp)}
  self.argv=[str(self.launch_binary),'app-server','--listen','stdio://',*extra]
  self.proc=subprocess.Popen(self.argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,cwd=cwd,env=self.env,text=True,bufsize=1,start_new_session=True)
  self.process_identity=self.custody.local_snapshot(self.proc.pid)
  self.session_prefix=self.process_identity['namespace_sessions'][:self.custody.depth]
  self.record('lifecycle',{'namespace_identity':self.process_identity,'event':'started','pid':self.proc.pid,'argv':self.argv,'cwd':str(cwd),'home':str(home),'environment_keys':sorted(self.env),'original_binary':str(self.original_binary),'binary_sha256':self.binary_sha256,'launch_copy_is_hardlink':self.original_binary.stat().st_ino==self.launch_binary.stat().st_ino})
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
    self.q.put(obj)
  finally:self.q.put(EOFError('native stdout closed'))
 def send(self,value):
  self.record('send',value);self.proc.stdin.write(json.dumps(value)+'\n');self.proc.stdin.flush()
 def take(self,timeout):
  item=self.q.get(timeout=timeout)
  if isinstance(item,Exception):raise item
  return item
 def rpc(self,method,params,timeout=20):
  self.request_id+=1;ident=self.request_id;self.send({'id':ident,'method':method,'params':params});deadline=time.monotonic()+timeout
  while time.monotonic()<deadline:
   obj=self.take(deadline-time.monotonic())
   if 'id' in obj and 'method' in obj:
    self.handle_server_request(obj);continue
   if obj.get('id')==ident:
    if 'error' in obj:raise RuntimeError(json.dumps(obj['error']))
    return obj.get('result')

  raise TimeoutError(method)
 def wait_turn(self,thread_id,timeout=30):
  deadline=time.monotonic()+timeout;seen=[]
  while time.monotonic()<deadline:
   obj=self.take(deadline-time.monotonic());seen.append(obj)
   if obj.get('method')=='turn/completed' and obj.get('params',{}).get('threadId')==thread_id:return obj,seen
   if 'id' in obj and 'method' in obj:self.handle_server_request(obj)
  raise TimeoutError('turn completion')
 def handle_server_request(self,obj):
  if self.server_handler is None:raise RuntimeError('unexpected native server request '+obj['method'])
  result=self.server_handler(obj)
  self.send({'id':obj['id'],'result':result})
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
  def ownership(snapshot):
   own_executable=snapshot.get('exe','').startswith(str(self.launch_dir)+'/')
   own_session=(len(snapshot['namespace_sessions'])>=self.custody.depth and snapshot['namespace_sessions'][:self.custody.depth]==self.session_prefix and snapshot['start_ticks']>=self.process_identity['start_ticks'])
   return own_executable or own_session
  def remaining():
   rows=[]
   for row in processes():
    if row['state']=='Z':continue
    try:
     observed=observe('/proc/'+str(row['pid']))
     if observed['start_ticks']==row['start_ticks'] and ownership(observed):rows.append({**row,'namespace_identity':observed})
    except (FileNotFoundError,ProcessLookupError):continue
    except (OSError,CustodyError) as exc:
     if row.get('exe','') and row['exe'].startswith(str(self.launch_dir)+'/'):rows.append({**row,'custody_refusal':str(exc)})
   return rows
  residual=remaining();signal_attempts=[]
  for sig,label in [(signal.SIGTERM,'SIGTERM_OWN_RESIDUALS_PIDFD'),(signal.SIGKILL,'SIGKILL_OWN_RESIDUALS_PIDFD')]:
   if not residual:break
   for row in residual:
    try:
     if 'namespace_identity' not in row:raise CustodyError(row.get('custody_refusal','unbound candidate'))
     action=self.custody.signal_observed(row['namespace_identity'],sig,ownership)
     signal_attempts.append(action)
     if label not in escalations:escalations.append(label)
    except (FileNotFoundError,ProcessLookupError):signal_attempts.append({'status':'ALREADY_EXITED','visible_pid':row['pid'],'signal':int(sig)})
    except (OSError,CustodyError) as exc:signal_attempts.append({'status':'REFUSED_NO_SIGNAL','visible_pid':row['pid'],'signal':int(sig),'reason':str(exc)})
   deadline=time.monotonic()+3
   while time.monotonic()<deadline and remaining():time.sleep(0.05)
   residual=remaining()
  after=bookend([self.home,self.owned_tmp,self.launch_dir])
  (self.evidence/'RESOURCE_AFTER_PROCESS_EXIT.json').write_text(json.dumps(after,indent=2)+'\n')
  artifacts=inventory(self.launch_dir)
  deleted=[]
  if not residual:
   for file in self.launch_dir.iterdir():
    if file.is_file() and not file.is_symlink():file.unlink();deleted.append(file.name)
  (self.evidence/'NATIVE_EXECUTABLE_EFFECTS.json').write_text(json.dumps({'original_binary':str(self.original_binary),'original_sha256':self.binary_sha256,'launch_root':str(self.launch_dir),'files_after_process_exit':artifacts,'remaining_owned_processes':residual,'deleted_regular_files':deleted,'files_after_cleanup':inventory(self.launch_dir),'cleanup_scope':'only regular non-symlink files in exclusive launch directory after native parent and observed session/executable descendants exited; owned HOME/TMPDIR evidence retained'},indent=2)+'\n')
  row={'event':'terminated','pid':self.proc.pid,'returncode':self.proc.returncode,'reader_joined':not self.reader.is_alive(),'escalations':escalations,'residual_signal_attempts':signal_attempts,'remaining_owned_processes':residual,'launch_directory_empty':not list(self.launch_dir.iterdir())}
  self.record('lifecycle',row);self.capture.close();self.stderr.close();return row
