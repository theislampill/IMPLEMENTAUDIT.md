"""Fixed root-side dispatcher helper. No tool, subprocess or network API.

The external driver pins this body. Root fills BINDING_SHA256 only after exact
late sender assembly/admission; no runtime path/URL/credential overrides exist.
"""
import base64,hashlib,json,os,re,stat,sys,time,types
from pathlib import Path
BINDING_SHA256=None
MAX_BYTES=8*1024**2
MAX_ENTRIES=128
RESULT_MAX=4*1024**2
CHUNK_MAX=49152
META_MAX=16384
KINDS=('run','attempt','jobs','artifact','artifacts','workflow')
PHASES=('OPENING','PRE_ENCRYPTION','CLOSING')
TOOL='mcp__codex_apps__github_fetch'

def need(v,c):
 if not v:raise ValueError(c)
def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return dict(bytes=len(b),sha256=sha(b))
def parse(raw):
 def pairs(rows):
  v={}
  for k,x in rows:need(k not in v,'DUPLICATE_KEY');v[k]=x
  return v
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE'))
def stamp(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def read(path,maximum):
 before=path.lstat();need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=maximum,'ORDINARY_BOUNDED_FILE')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  need(stamp(os.fstat(fd))==stamp(before) and not os.listxattr(fd),'INPUT_OPEN_CHANGED');raw=os.pread(fd,maximum+1,0)
  need(len(raw)==before.st_size and stamp(os.fstat(fd))==stamp(before) and stamp(path.lstat())==stamp(before),'INPUT_CLOSING_CHANGED');return raw
 finally:os.close(fd)
def integer(v,low,high):need(type(v) is int and low<=v<=high,'INTEGER')
def digest(v):need(type(v) is str and re.fullmatch('[0-9a-f]{64}',v),'DIGEST')
def path_exact(v):
 need(type(v) is str and v.startswith('/') and str(Path(v))==v and '..' not in Path(v).parts,'FIXED_PATH');return Path(v)
def binding():
 base=Path(__file__).absolute().parent;raw=read(base/'DISPATCHER_BINDING.json',META_MAX);need(sha(raw)==BINDING_SHA256,'DISPATCHER_UNRESOLVED_OR_CHANGED');b=parse(raw)
 need(set(b)=={'schema','state','entry_path','entry','operation_path','operation','context','source_commit','source_tree','carrier_binding_sha256','input_index_sha256','nonce','sender_uid','sender_gid','journal_path','admission','limits','original_awards'},'BINDING_FIELDS')
 need(b['schema']=='dg16.fixed-root-supported-tool-dispatcher.v2' and b['state']=='ACTUAL_ROOT_ADMITTED_LATE_SENDER_DISPATCH' and b['original_awards']==[],'BINDING_SCOPE')
 need(sys.flags.isolated==1 and sys.dont_write_bytecode and os.getuid()==os.geteuid()==b['sender_uid']>0 and os.getgid()==os.getegid()==b['sender_gid'],'ACTUAL_ADMITTED_NONROOT_IDENTITY')
 entry=path_exact(b['entry_path']);operation=path_exact(b['operation_path']);journal=path_exact(b['journal_path']);run=b['context']['run_id']
 need(operation.name=='PRO_SENDER_OPERATION.json' and operation.parent.name=='carrier' and operation.parent.parent.name=='packet','FIXED_OPERATION_PATH')
 packet=operation.parent.parent;need(entry==packet.parent/'root_sender_entry.py' and journal==packet.parent/('dg16-root-tool-dispatch-'+run+'-a1'),'FIXED_ENTRY_JOURNAL_SIBLINGS')
 opraw=read(operation,65536);need(desc(opraw)==b['operation'],'ACTUAL_OPERATION_BODY');op=parse(opraw)
 need(type(op) is dict and set(op)=={'schema','context','source_commit','source_tree','carrier_binding_sha256','input_index_sha256','artifact_id','artifact','nonce','issued_unix_ms','expires_unix_ms','sender_uid','sender_gid','original_awards'} and op['schema']=='dg16.pro-private-sender-operation.v1' and encode(op)==opraw and op['original_awards']==[],'ACTUAL_OPERATION_SCOPE')
 need(type(op['issued_unix_ms']) is int and type(op['expires_unix_ms']) is int and 0<=op['issued_unix_ms']<op['expires_unix_ms']<=op['issued_unix_ms']+600000,'BOUNDED_OPERATION_INTERVAL')
 need(b['source_commit']=='7e2b00b3a2a16fc6033a5eabe4fc795f6249366f' and b['source_tree']=='6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e','CURRENT_SOURCE_BINDING')
 need(op['context']==b['context'] and op['source_commit']==b['source_commit'] and op['source_tree']==b['source_tree'] and op['carrier_binding_sha256']==b['carrier_binding_sha256'] and op['input_index_sha256']==b['input_index_sha256'] and op['nonce']==b['nonce'] and op['sender_uid']==b['sender_uid'] and op['sender_gid']==b['sender_gid'],'OPERATION_BINDING')
 need(b['limits']==dict(journal_bytes=MAX_BYTES,journal_entries=MAX_ENTRIES,tool_result_bytes=RESULT_MAX,chunk_bytes=CHUNK_MAX,metadata_reads=18),'FIXED_RESOURCE_ALLOCATION')
 admission_raw=read(base/'DISPATCHER_ADMISSION.json',META_MAX);need(desc(admission_raw)==b['admission'],'ACTUAL_DISPATCH_ADMISSION_BODY')
 expected=dict(schema='dg16.root-supported-tool-dispatch-admission.v1',issuer='R5_ROOT_GOVERNOR',operation='ONE_SEQUENTIAL_18_FIXED_READ_DISPATCH_ARTIFACT_LIST_V2',entry_path=b['entry_path'],entry=b['entry'],operation_body=b['operation'],context=b['context'],source_commit=b['source_commit'],source_tree=b['source_tree'],carrier_binding_sha256=b['carrier_binding_sha256'],input_index_sha256=b['input_index_sha256'],nonce=b['nonce'],sender_uid=b['sender_uid'],sender_gid=b['sender_gid'],journal_path=b['journal_path'],limits=b['limits'],automatic_retry=False,crypto_or_native_effect_grant=False,original_awards=[])
 need(parse(admission_raw)==expected,'ACTUAL_DISPATCH_ADMISSION_SCOPE')
 return b,op

def entry(b):
 path=Path(b['entry_path']);raw=read(path,1024**2);need(desc(raw)==b['entry'],'EXACT_ROOT_ENTRY_BODY')
 m=types.ModuleType('exact_root_dispatch_entry');m.__file__=str(path);exec(compile(raw,str(path),'exec'),m.__dict__)
 return m

def endpoint(b,op,i):
 integer(i,0,17);ctx=b['context'];prefix='https://api.github.com/repos/theislampill/IMPLEMENTAUDIT.md';run=ctx['run_id']
 tails=('/actions/runs/'+run,'/actions/runs/'+run+'/attempts/1','/actions/runs/'+run+'/attempts/1/jobs?per_page=100&page=1','/actions/runs/'+run+'/artifacts?per_page=100','/actions/runs/'+run+'/artifacts?per_page=100','/contents/'+ctx['workflow_path']+'?ref='+ctx['workflow_commit'])
 return prefix+tails[i%6]
def name(i,part):integer(i,0,17);return '%02d_%s'%(i,part)
def allowed():
 out={'START.json':META_MAX,'END.json':META_MAX}
 for i in range(18):
  for part,limit in (('INTENT.json',META_MAX),('RESULT.raw',RESULT_MAX),('RESULT_READY.json',META_MAX),('PUBLISH_INTENT.json',META_MAX),('PUBLISHED.json',META_MAX)):
   out[name(i,part)]=limit
 return out

class Journal:
 def __init__(self,b,*,create=False):
  self.b=b;self.path=Path(b['journal_path']);self.fd=None
  if create:self.path.mkdir(mode=0o700,exist_ok=False)
  s=self.path.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==b['sender_uid'] and s.st_gid==b['sender_gid'] and stat.S_IMODE(s.st_mode)==0o700 and not self.path.is_symlink(),'JOURNAL_CUSTODY')
  self.fd=os.open(self.path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);self.identity=(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode);self.current()
  if create:self.write('START.json',encode(dict(schema='dg16.root-dispatch-journal-start.v1',authority='NONE',binding_sha256=BINDING_SHA256,operation=b['operation'],context=b['context'],nonce=b['nonce'],limits=b['limits'],original_awards=[])))
  expected=dict(schema='dg16.root-dispatch-journal-start.v1',authority='NONE',binding_sha256=BINDING_SHA256,operation=b['operation'],context=b['context'],nonce=b['nonce'],limits=b['limits'],original_awards=[])
  need(parse(self.read('START.json'))==expected,'JOURNAL_START_BINDING')
 def __enter__(self):return self
 def __exit__(self,*_):
  if self.fd is not None:os.close(self.fd);self.fd=None
 def current(self):
  for s in (os.fstat(self.fd),self.path.lstat()):need((s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode)==self.identity,'JOURNAL_CHANGED')
  need(not os.listxattr(self.fd),'JOURNAL_ATTRIBUTES')
 def census(self):
  self.current();limits=allowed();out={}
  for p in sorted(self.path.iterdir()):
   need(p.name in limits,'JOURNAL_UNKNOWN_FILE');raw=read(p,limits[p.name]);s=p.lstat();need(s.st_uid==self.b['sender_uid'] and s.st_gid==self.b['sender_gid'] and stat.S_IMODE(s.st_mode)==0o600,'JOURNAL_FILE_CUSTODY');out[p.name]=desc(raw)
  need(len(out)<=MAX_ENTRIES and sum(r['bytes'] for r in out.values())<=MAX_BYTES,'JOURNAL_BOUND');self.current();return out
 def capacity(self,bytes_,entries=1):
  rows=self.census();need('END.json' not in rows,'JOURNAL_TERMINAL');need(sum(r['bytes'] for r in rows.values())+bytes_+META_MAX<=MAX_BYTES and len(rows)+entries+1<=MAX_ENTRIES,'JOURNAL_CAPACITY');return rows
 def read(self,n):need(n in allowed(),'FIXED_JOURNAL_MEMBER');self.current();raw=read(self.path/n,allowed()[n]);self.current();return raw
 def write(self,n,raw):
  need(n in allowed() and type(raw) is bytes and len(raw)<=allowed()[n],'JOURNAL_WRITE_SCOPE')
  rows=self.capacity(len(raw));need(n not in rows,'JOURNAL_WRITE_ONCE')
  fd=os.open(n,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
  try:
   os.fchmod(fd,0o600);offset=0
   while offset<len(raw):nbytes=os.write(fd,raw[offset:]);need(nbytes>0,'JOURNAL_WRITE_PROGRESS');offset+=nbytes
   os.fsync(fd)
  finally:os.close(fd)
  os.fsync(self.fd);need(self.read(n)==raw,'JOURNAL_WRITE_READBACK');return desc(raw)
 def append_result(self,i,offset,chunk):
  integer(offset,0,RESULT_MAX);need(type(chunk) is bytes and 0<len(chunk)<=CHUNK_MAX and offset+len(chunk)<=RESULT_MAX,'RESULT_CHUNK_BOUND');rows=self.capacity(len(chunk))
  need(name(i,'INTENT.json') in rows and name(i,'RESULT_READY.json') not in rows and name(i,'PUBLISH_INTENT.json') not in rows,'RESULT_INGRESS_STATE')
  n=name(i,'RESULT.raw');need((offset==0 and n not in rows) or (offset>0 and rows.get(n,{}).get('bytes')==offset),'RESULT_UNCERTAIN_OR_OFFSET')
  flags=os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC|(os.O_CREAT|os.O_EXCL if offset==0 else os.O_APPEND)
  fd=os.open(n,flags,0o600,dir_fd=self.fd)
  try:
   before=os.fstat(fd);need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==self.b['sender_uid'] and stat.S_IMODE(before.st_mode)==0o600 and before.st_size==offset and not os.listxattr(fd),'RESULT_APPEND_CUSTODY');done=0
   while done<len(chunk):nbytes=os.write(fd,chunk[done:]);need(nbytes>0,'RESULT_WRITE_PROGRESS');done+=nbytes
   os.fsync(fd);need(os.fstat(fd).st_size==offset+len(chunk),'RESULT_APPEND_SIZE')
  finally:os.close(fd)
  os.fsync(self.fd);raw=self.read(n);need(len(raw)==offset+len(chunk) and raw[offset:]==chunk,'RESULT_CHUNK_READBACK');return dict(bytes=len(raw),sha256=sha(raw))

def marker_ready(b,op,i):
 integer(i,0,17);need(int(time.time()*1000)<op['expires_unix_ms'],'OPERATION_EXPIRED')
 packet=Path(b['operation_path']).parent.parent;directory=packet.parent/('dg16-private-sender-'+b['context']['run_id']+'-a1');marker=directory/('BROKER_%02d_REQUEST_READY'%i)
 # Do not inspect BROKER_START/REQUEST/results while this fixed commitment
 # marker is absent. Readiness never creates or modifies the sender directory.
 try:s=marker.lstat()
 except FileNotFoundError:return False
 need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size==0 and s.st_uid==b['sender_uid'] and s.st_gid==b['sender_gid'] and stat.S_IMODE(s.st_mode)==0o600,'REQUEST_READY_CUSTODY')
 need(read(marker,0)==b'','REQUEST_READY_BODY');return True

def reserve(b,op,j,i,m):
 need(marker_ready(b,op,i),'REQUEST_NOT_READY');rows=j.capacity(RESULT_MAX+4*META_MAX,5)
 need(name(i,'INTENT.json') not in rows,'UNCERTAIN_INTENT_NO_SECOND_GET')
 for prior in range(i):
  receipt=parse(j.read(name(prior,'PUBLISHED.json')));need(receipt['status']=='PUBLISHED' and receipt['broker_status']=='RECEIVED','PRIOR_PUBLISH_REQUIRED')
 need(not any(name(later,'INTENT.json') in rows for later in range(i+1,18)),'SEQUENTIAL_READS_ONLY')
 # External O_EXCL reservation precedes broker reservation and any actual GET.
 # Failure at either boundary leaves a blocking exact prefix, never retry credit.
 call_ref='dg16_fetch_'+b['nonce']+'_%02d'%i
 opening=dict(schema='dg16.root-dispatch-intent.v1',ordinal=i,phase=PHASES[i//6],kind=KINDS[i%6],nonce=b['nonce'],operation=b['operation'],logical_tool_call_ref=call_ref,tool=TOOL,arguments={'url':endpoint(b,op,i)},automatic_retry=False,actual_tool_history_required=True)
 j.write(name(i,'INTENT.json'),encode(opening))
 inspected=m.inspect(i);request=inspected['request']
 need(request['ordinal']==i and request['phase']==PHASES[i//6] and request['kind']==KINDS[i%6] and request['context']==b['context'] and request['nonce']==b['nonce'] and request['operation_sha256']==b['operation']['sha256'] and request['source_commit']==b['source_commit'] and request['source_tree']==b['source_tree'] and request['carrier_binding_sha256']==b['carrier_binding_sha256'] and request['artifact_id']==op['artifact_id'] and request['tool']==TOOL and request['method']=='GET' and request['arguments']==opening['arguments'] and inspected['fetch_permitted'] is False,'EXACT_INSPECTED_REQUEST')
 plan=m.reserve(i)
 need(type(plan) is dict and set(plan)=={'tool','arguments','ordinal','nonce','intent_sha256','request_sha256','deadline_monotonic'} and plan['tool']==TOOL and plan['arguments']==opening['arguments'] and plan['ordinal']==i and plan['nonce']==b['nonce'] and plan['request_sha256']==inspected['request_sha256'],'EXACT_RESERVED_PLAN')
 digest(plan['intent_sha256']);digest(plan['request_sha256']);need(type(plan['deadline_monotonic']) in (int,float) and time.monotonic()<plan['deadline_monotonic'],'PLAN_DEADLINE')
 # Bind the broker plan in the already held intent file's paired empty result
 # commitment: no new network permission can be inferred by rereading it.
 return dict(status='RESERVED_ONCE',plan=plan,logical_tool_call_ref=call_ref,remaining_ms=max(0,int((plan['deadline_monotonic']-time.monotonic())*1000)),external_intent_sha256=sha(j.read(name(i,'INTENT.json'))))

def complete_result(b,j,i,expected_bytes,expected_sha,broker_intent_sha):
 integer(expected_bytes,1,RESULT_MAX);digest(expected_sha);digest(broker_intent_sha);intent=parse(j.read(name(i,'INTENT.json')));raw=j.read(name(i,'RESULT.raw'));need(desc(raw)==dict(bytes=expected_bytes,sha256=expected_sha),'FULL_ACTUAL_RESULT_READBACK')
 value=parse(raw);need(type(value) is dict,'FULL_CALL_TOOL_RESULT_REQUIRED')
 receipt=dict(schema='dg16.root-dispatch-result-retained.v1',ordinal=i,nonce=b['nonce'],operation=b['operation'],external_intent_sha256=sha(j.read(name(i,'INTENT.json'))),broker_intent_sha256=broker_intent_sha,logical_tool_call_ref=intent['logical_tool_call_ref'],tool_result=desc(raw),serialization='COMPLETE_RETURNED_CALL_TOOL_RESULT_JSON_UTF8',native_tool_call_id_available=False,actual_tool_history_required=True)
 j.write(name(i,'RESULT_READY.json'),encode(receipt));return dict(status='ACTUAL_FULL_RESULT_RETAINED',receipt=receipt)

def publish(b,j,i,m):
 ready=parse(j.read(name(i,'RESULT_READY.json')));raw=j.read(name(i,'RESULT.raw'));need(ready['ordinal']==i and ready['nonce']==b['nonce'] and ready['operation']==b['operation'] and ready['tool_result']==desc(raw) and ready['external_intent_sha256']==sha(j.read(name(i,'INTENT.json'))),'RESULT_READY_JOIN')
 j.write(name(i,'PUBLISH_INTENT.json'),encode(dict(schema='dg16.root-dispatch-publish-intent.v1',ordinal=i,result_ready_sha256=sha(j.read(name(i,'RESULT_READY.json'))),actual_tool_history_required=True)))
 result=m.publish(i,ready['broker_intent_sha256'],raw,ready['logical_tool_call_ref'])
 need(type(result) is dict and result.get('status')=='COMMITTED_REPLY' and result.get('fetch_permitted') is False,'BROKER_PUBLISH_OUTCOME')
 reply=result['reply'];need(reply['tool_result']==desc(raw) and reply['tool_call_ref']==ready['logical_tool_call_ref'] and reply['intent_sha256']==ready['broker_intent_sha256'] and reply['ordinal']==i and reply['nonce']==b['nonce'],'BROKER_PUBLISH_JOIN')
 record=dict(schema='dg16.root-dispatch-published.v1',status='PUBLISHED',ordinal=i,broker_status=reply['status'],broker_result=result,result_ready_sha256=sha(j.read(name(i,'RESULT_READY.json'))),authority='NONE')
 j.write(name(i,'PUBLISHED.json'),encode(record));return dict(status='PUBLISHED',ordinal=i,broker_status=reply['status'],fetch_permitted=False)

def main():
 need(len(sys.argv)>=2,'FIXED_ACTION');action=sys.argv[1];b,op=binding()
 if action=='initialize':
  need(len(sys.argv)==2,'FIXED_ACTION_ARGUMENTS')
  with Journal(b,create=True):pass
  return dict(status='INITIALIZED',fetch_permitted=False)
 need(action in ('ready','reserve','chunk','complete','publish','finish'),'FIXED_ACTION')
 with Journal(b) as j:
  if action=='finish':
   need(len(sys.argv)==2,'FIXED_ACTION_ARGUMENTS');rows=j.census()
   for i in range(18):need(parse(j.read(name(i,'PUBLISHED.json')))['broker_status']=='RECEIVED','ALL_18_RECEIVED_REQUIRED')
   # This closes the dispatcher journal only. Broker/client terminal and sender
   # cleanup remain independently required and are never awarded here.
   j.write('END.json',encode(dict(schema='dg16.root-dispatch-journal-end.v1',authority='NONE',reads=18,prefix=rows,original_awards=[])))
   return dict(status='DISPATCH_18_COMPLETE_SENDER_TERMINAL_SEPARATE',fetch_permitted=False)
  need(len(sys.argv)>=3,'ORDINAL_REQUIRED');i=int(sys.argv[2]);integer(i,0,17)
  if action=='ready':
   need(len(sys.argv)==3,'FIXED_ACTION_ARGUMENTS');rows=j.census();need(name(i,'INTENT.json') not in rows,'EXISTING_INTENT_NO_REPLAY')
   return dict(status='READY' if marker_ready(b,op,i) else 'PENDING',fetch_permitted=False)
  if action=='reserve':need(len(sys.argv)==3,'FIXED_ACTION_ARGUMENTS');return reserve(b,op,j,i,entry(b))
  if action=='chunk':
   need(len(sys.argv)==5,'FIXED_ACTION_ARGUMENTS');chunk=base64.b64decode(sys.argv[4],validate=True);return dict(status='CHUNK_RETAINED',**j.append_result(i,int(sys.argv[3]),chunk))
  if action=='complete':
   need(len(sys.argv)==6,'FIXED_ACTION_ARGUMENTS');return complete_result(b,j,i,int(sys.argv[3]),sys.argv[4],sys.argv[5])
  need(action=='publish' and len(sys.argv)==3,'FIXED_ACTION_ARGUMENTS');return publish(b,j,i,entry(b))
if __name__=='__main__':
 try:print(json.dumps(main(),sort_keys=True,separators=(',',':')),flush=True)
 except Exception:
  print('{"authority":"NONE","status":"REFUSED_OR_UNCERTAIN","automatic_retry":false}',flush=True);raise SystemExit(1)
