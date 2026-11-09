"""Concrete Root native-history/no-echo bridge. No live calls in source controls.

The actual Root driver invokes only the requested MCP tools, then sends the V8
JSON.stringify(result) UTF8 SHA256/count (NO newline in that wire value). Real
completed native history is read through Root's exact selected, pinned module.
"""
import ast,copy,hashlib,json,os,re,ssl,signal,sys,time,types,urllib.request,urllib.error,urllib.parse,select
from pathlib import Path
from contextlib import contextmanager
HISTORY_SHA='71b4538d41501c017d2282f799dfbd3ad8e3435c9409c40633ed156d18529bd1'
RESOLVER_SHA='b2ac1130149d9878a3a00c7d8ba214743920a1aede38cb6b75699e14a2d03530'
PREPARATION_SHA='6c7a67e3bf5ee1375e221ab68162da463be2fe63788d850e88ecc4a0ca6eebcd'
WORKFLOW_SHA='4e8a9e196f3c057dcd0d2ad782dba4395cc5f890a06a568c2478194a5a1b8368'
THREAD='01a1953f-a15b-7811-aa72-3538ebb03562'
HEADER='e6fba7c217f360f6b6f6d3c11f42052131b89cf0042289e07902347ccf8d0389'
TOOLS={'mcp__codex_apps__github_fetch':'github.fetch','mcp__codex_apps__github_download_workflow_artifact':'github.download_workflow_artifact'}
def need(ok,code):
 if not ok:raise ValueError(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def desc(raw):return dict(bytes=len(raw),sha256=sha(raw))
def encode(value):return json.dumps(value,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')
def read_source(path,expected=None,maximum=4*1024**2,private=False):
 p=Path(path);need(p.is_absolute() and p.resolve(strict=True)==p,'FIXED_PHYSICAL_SOURCE_PATH')
 before=p.lstat();need(__import__('stat').S_ISREG(before.st_mode) and before.st_nlink==1 and 0<before.st_size<=maximum,'SOURCE_SHAPE')
 if private:need(before.st_uid==os.geteuid() and __import__('stat').S_IMODE(before.st_mode)==0o600,'FRESH_ROOT_PRIVATE_CONFIGURATION')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 try:
  need(mark(os.fstat(fd))==mark(before),'SOURCE_OPEN_CHANGED');chunks=[];count=0
  while True:
   b=os.read(fd,min(65536,maximum-count+1))
   if not b:break
   chunks.append(b);count+=len(b);need(count<=maximum,'SOURCE_BOUND')
  raw=b''.join(chunks);need(len(raw)==before.st_size and mark(os.fstat(fd))==mark(before)==mark(p.lstat()),'SOURCE_CLOSING_CHANGED')
 finally:os.close(fd)
 if expected:need(sha(raw)==expected,'EXACT_ROOT_SOURCE_PIN')
 return raw
def history_module(raw,path):
 need(sha(raw)==HISTORY_SHA,'ROOT_NATIVE_HISTORY_SOURCE_PIN');m=types.ModuleType('actual_selected_root_history');m.__file__=str(path)
 exec(compile(raw,str(path),'exec'),m.__dict__);need(m.THREAD==THREAD and m.HEADER_SHA==HEADER and m.NAMES==TOOLS,'ROOT_HISTORY_SELECTION')
 return m
def resolver_helpers(raw):
 need(sha(raw)==RESOLVER_SHA,'QUALIFIED_ROOT_BODY_RESOLVER_PIN')
 names={'Refusal','WatchdogExpired','need','NoRedirect','request_watchdog','fetch_once','read_ephemeral_frame'}
 nodes=[n for n in ast.parse(raw).body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names]
 # No receiver(), resolve(), main(), filesystem Session, or G1 data surface.
 env={'hashlib':hashlib,'json':json,'os':os,'re':re,'select':select,'signal':signal,'ssl':ssl,'sys':sys,
  'time':time,'types':types,'urllib':urllib,'contextmanager':contextmanager,'WATCHDOG_SECONDS':45}
 if os.name=='posix':env['termios']=__import__('termios')
 exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<exact-qualified-root-transport-helpers>','exec'),env)
 return types.SimpleNamespace(**env)

def make_bridge_class(RootBridge,NativeReply):
 class ConcreteRootBridge(RootBridge):
  def __init__(self,cfg,configuration_raw,H,resolver,core,emit=None,frame=None,fetch=None):
   self.cfg=copy.deepcopy(cfg);self.configuration_raw=configuration_raw;self.H=H;self.resolver=resolver;self.core=core
   self.turn=cfg['turn_id'];need(type(self.turn) is str and re.fullmatch('[0-9a-f-]{36}',self.turn),'ACTUAL_CURRENT_ROOT_TURN_REQUIRED')
   self.emit=emit or self._emit;self.frame=frame or resolver.read_ephemeral_frame;self.fetch=fetch or resolver.fetch_once
   self.active=None;self.expires=0;self.context=None;self.role=None;self.download=None;self.artifacts=None;self.ordinals=set()
  @staticmethod
  def _emit(value):print(encode(value).decode('utf8'),flush=True)
  def now_ms(self):return time.time_ns()//1000000
  def admit(self,admission_raw,preparation,context,role):
   # Authority is the actual external native Root invocation, not JSON labels.
   # This checks its fresh protected configuration/source/history bindings only.
   grant=json.loads(admission_raw);now=self.now_ms()
   need(self.active is None and grant.get('configuration_sha256')==sha(self.configuration_raw)
    and grant.get('issued_ms',now+1)<=now<grant.get('expires_ms',0)<=grant.get('issued_ms',0)+300000,
    'CURRENT_NATIVE_ROOT_CONFIGURATION_ADMISSION_REQUIRED')
   mark=self.H.cursor(self.turn);need(mark['thread']==THREAD and mark['header']==HEADER,'SELECTED_ROOT_HEADER')
   self.active=object();self.expires=grant['expires_ms'];self.context=copy.deepcopy(context);self.role=role
   return self.active
  def _current(self,capability):need(capability is self.active and self.active is not None and self.now_ms()<self.expires,'ROOT_ROLE_EXPIRED_OR_FRAME_EXTINCT')
  def supported(self,capability,tool,arguments,intent):
   self._current(capability);need(tool in TOOLS,'FIRST_PARTY_TOOL_ONLY');deadline=min(self.expires,intent['expires_ms'])
   if tool=='mcp__codex_apps__github_fetch':
    allowed={self.core.A.endpoint(self.context,k) for k in ('run','attempt','jobs','commit','workflow','artifacts','closing-run','closing-artifacts')}
    need(type(arguments) is dict and set(arguments)=={'url'} and arguments['url'] in allowed,'FIXED_PUBLIC_METADATA_ENDPOINT_ONLY')
   else:
    need(type(arguments) is dict and set(arguments)=={'repo_full_name','artifact_id','file_name'} and arguments['repo_full_name']==self.context['repository']
     and type(arguments['artifact_id']) is int and arguments['artifact_id']>0
     and arguments['file_name']==self.core.K.artifact_name(self.role,self.context)+'.zip','FIXED_PUBLIC_DOWNLOAD_ARGUMENTS')
   need(intent['ordinal'] not in self.ordinals,'UNKNOWN_ORDINAL_ALREADY_RESERVED_NO_REPLAY');self.ordinals.add(intent['ordinal'])
   mark=self.H.cursor(self.turn) # Fresh before the actual Root tool request.
   self.emit(dict(event='tool_request',tool=tool,native_tool=TOOLS[tool],args=arguments,deadline_ms=deadline,mark=mark,
    ordinal=intent['ordinal'],wire='JSON.stringify(actual) UTF8 NO_TRAILING_NEWLINE'))
   ack_raw=self.frame(4096,min(45,max(0.001,(deadline-self.now_ms())/1000)))
   ack=json.loads(ack_raw);need(type(ack) is dict and set(ack)=={'wire_sha256','wire_bytes'}
    and type(ack['wire_sha256']) is str and re.fullmatch('[0-9a-f]{64}',ack['wire_sha256'])
    and type(ack['wire_bytes']) is int and 0<ack['wire_bytes']<=4*1024**2,'WIRE_DESCRIPTOR_FRAME_ONLY')
   raw,history,proof=self.H.receive(mark,tool,arguments,ack['wire_sha256'],ack['wire_bytes'],deadline)
   self._current(capability)
   if tool=='mcp__codex_apps__github_download_workflow_artifact':self.download=(raw,history,copy.deepcopy(proof))
   elif arguments.get('url')==self.core.A.endpoint(self.context,'artifacts'):self.artifacts=(raw,history)
   return NativeReply(raw,history,proof)
  def body(self,capability,download_result,download_history,arguments,intent):
   self._current(capability);need(self.download is not None and self.artifacts is not None
    and download_result==self.download[0] and download_history==self.download[1],'ACTUAL_VOLATILE_DOWNLOAD_FRAME_REQUIRED')
   need(intent['ordinal'] not in self.ordinals,'UNKNOWN_BODY_ALREADY_RESERVED_NO_REPLAY');self.ordinals.add(intent['ordinal'])
   _,listing=self.core.U.unwrap_tool_result(self.artifacts[0],self.core.A.endpoint(self.context,'artifacts'),kind='artifacts',context=self.context,workflow_sha256=self.core.binding['workflow_sha256'])
   item=self.core.A.artifacts(listing,self.context,self.core.b)[self.role]
   need(arguments['artifact_id']==item['id'] and arguments['file_name']==self.core.K.artifact_name(self.role,self.context)+'.zip','EXACT_ROOT_SELECTED_BODY')
   # Retain qualified G1 fetch_once's original262144 cap. Larger G2 public ZIPs
   # need a separately qualified Root route; never silently widen the helper.
   need(type(item['size_in_bytes']) is int and 0<item['size_in_bytes']<=262144,'ROOT_QUALIFIED_BODY_CAP_262144')
   _,url=self.core.A.download_reference(download_result,arguments['artifact_id'],arguments['file_name'])
   deadline=min(self.expires,intent['expires_ms']);seconds=min(45,(deadline-self.now_ms())/1000);need(seconds>0,'BODY_WINDOW_EXPIRED')
   operation_ref='root_body_get_'+sha(encode(dict(intent=intent,download_call=self.download[2]['tool_call_ref'])))
   started=self.now_ms();outcome=dict(schema='dg16.root-owned-bounded-http-outcome.v1',authority='NONE',body_operation_ref=operation_ref,
    mcp_tool_call_id=None,download_native_call_ref=self.download[2]['tool_call_ref'],download_result=desc(download_result),
    download_native_history=desc(download_history),expected_archive=dict(bytes=item['size_in_bytes'],sha256=item['digest'][7:]),
    started_ms=started,deadline_ms=deadline,redirects=False,proxy=False,automatic_retry=False,body_get_attempts=0)
   self.emit(dict(event='body_get_intent',body_operation_ref=operation_ref,artifact_id=item['id'],expected_archive=outcome['expected_archive'],deadline_ms=deadline))
   try:
    outcome['body_get_attempts']=1;body=self.fetch(url,item['size_in_bytes'],seconds);self._current(capability)
    need(desc(body)==outcome['expected_archive'],'EXACT_ACTUAL_ARCHIVE_REQUIRED');outcome.update(status='RECEIVED',archive=desc(body),ending_ms=self.now_ms())
   except BaseException:
    outcome.update(status='REFUSED_OR_UNCERTAIN',ending_ms=self.now_ms());self.emit(dict(event='body_get_outcome',outcome=outcome))
    raise ValueError('ROOT_BODY_GET_UNCERTAIN_NO_REPLAY') from None
   finally:url=None
   self.emit(dict(event='body_get_outcome',outcome=outcome));history=encode(outcome)
   # This is actual owned HTTP boundary evidence, explicitly NOT a fabricated
   # MCP event. The core's generic call-ref slot carries its named operation ref.
   proof=dict(tool=None,arguments=arguments,tool_call_ref=operation_ref,body_operation_ref=operation_ref,mcp_tool_call_id=None,
    transport='ROOT_QUALIFIED_FETCH_ONCE_NO_REDIRECT_NO_PROXY',tool_result_sha256=sha(body),history_sha256=sha(history))
   return NativeReply(body,history,proof)
  def release(self,capability):
   if capability is self.active:self.active=None;self.download=None;self.artifacts=None;self.context=None
 return ConcreteRootBridge

def create_received_root_bridge(cfg,exactcore,RootBridge,NativeReply):
 """Actual executable factory. Reads only declared public source/config inputs.

 It neither starts a Session nor invokes cursor/receive/HTTP here. Root's live
 invocation and later admit/callback methods own those bounded effects.
 """
 need(os.name=='posix' and os.getuid()==os.geteuid()>0,'NATIVE_ROOT_NONROOT_POSIX_FACTORY')
 raw_cfg=read_source(cfg['configuration_path'],private=True);need(json.loads(raw_cfg)==cfg,'EXACT_FRESH_ROOT_CONFIGURATION')
 H=history_module(read_source(cfg['native_history_module'],HISTORY_SHA),cfg['native_history_module'])
 resolver=resolver_helpers(read_source(cfg['body_resolver_module'],RESOLVER_SHA))
 sources={name:read_source(path,exactcore.PINS[name]) for name,path in cfg['core_sources'].items()}
 need(set(sources)==set(exactcore.PINS),'EXACT_ROOT_PUBLIC_CORE_SOURCES')
 installation=read_source(cfg['installation_receipt'],exactcore.INSTALLATION_PIN)
 seal=read_source(cfg['receiver_seal'],exactcore.RECEIVER_SEAL_PIN)
 binding_raw=read_source(cfg['public_binding']);runtime_raw=read_source(cfg['runtime'])
 b=json.loads(binding_raw);frame=dict(public_binding=b,workflow_sha256=WORKFLOW_SHA,issuer_thread=THREAD,
  provider_actor='theislampill',provider_actor_id='266501826',source_author=cfg['source_author'])
 core=exactcore.PublicOperator.from_received_installation(sources,frame,installation,seal,binding_raw,runtime_raw)
 core.K.context(cfg['context']);need(cfg['role'] in ('live','terminal'),'PUBLIC_ROLE_ONLY')
 bridge=make_bridge_class(RootBridge,NativeReply)(cfg,raw_cfg,H,resolver,core)
 return bridge,core,cfg['context'],cfg['role']
