"""Small fixed-episode JSONL client, adapted from the retained DG17 native drivers."""
import copy,datetime,hashlib,json,os,queue,subprocess,threading,time
from pathlib import Path
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
class Stop(RuntimeError):pass

def hook_projection(h):
 # Preserve omitted-versus-null optional metadata. Never retain raw commands.
 fields=['key','source','sourcePath','eventName','handlerType','enabled','isManaged','currentHash','trustStatus','timeoutSec','matcher','environmentId','pluginId','async']
 result={k:h[k] for k in fields if k in h}
 if isinstance(h.get('command'),str):result['commandSha256']=sha(h['command'].encode('utf-8'))
 return result
class Client:
 def __init__(self,argv,cwd,env,out,deadline):
  self.out=Path(out);self.out.mkdir();self.deadline=deadline;self.q=queue.Queue();self.seq=0;self.events=[];self.sent={};self.thread_id=None;self.turn_id=None
  self.active=False;self.log=(self.out/'safe-wire.jsonl').open('x',encoding='utf-8');launch_before=datetime.datetime.now(datetime.timezone.utc).isoformat();self.proc=subprocess.Popen(argv,cwd=cwd,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
  self.identity=dict(pid=self.proc.pid,parent_pid=os.getpid(),argv=argv,cwd=cwd,launch_before_utc=launch_before,launch_after_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
  self.record(dict(kind='actual_owned_appserver_identity',value=self.identity))
  def reader(stream,kind):
   while True:
    raw=stream.readline(4*1024*1024+1)
    if not raw:break
    if len(raw)>4*1024*1024:self.q.put(('error','wire frame bound'));break
    if kind=='stderr':self.q.put(('stderr',dict(bytes=len(raw),sha256=sha(raw))));continue
    try:self.q.put(('frame',(json.loads(raw),dict(bytes=len(raw),sha256=sha(raw)))))
    except Exception:self.q.put(('error','nonJSON native frame'));break
   self.q.put((kind+'-eof',None))
  self.readers=[threading.Thread(target=reader,args=(self.proc.stdout,'stdout'),daemon=True),threading.Thread(target=reader,args=(self.proc.stderr,'stderr'),daemon=True)]
  for t in self.readers:t.start()
 def record(self,x):self.log.write(json.dumps(x,ensure_ascii=False)+'\n');self.log.flush()
 def recv(self,seconds=30):
  end=min(self.deadline,time.perf_counter()+seconds)
  while True:
   remain=end-time.perf_counter()
   if remain<=0:raise Stop('absolute RPC/global deadline reached')
   kind,value=self.q.get(timeout=remain)
   if kind=='stderr':self.record(dict(direction=kind,**value));continue
   break
  if kind!='frame':raise Stop(kind+':'+str(value))
  msg,wire=value;method=self.sent.get(msg.get('id'))
  safe=dict(direction='response',wire=wire)
  if method=='config/read':safe.update(method=method,raw_config_not_retained=True)
  elif method=='hooks/list':safe.update(method=method,projection=[dict(cwd=e.get('cwd'),errors=bool(e.get('errors')),warnings_count=len(e.get('warnings',[])),hooks=[hook_projection(h) for h in e.get('hooks',[])]) for e in msg.get('result',{}).get('data',[])])
  elif method=='mcpServerStatus/list':safe.update(method=method,projection=[dict(name=r.get('name'),tools_count=len(r.get('tools',{})),resources_count=len(r.get('resources',[])),templates_count=len(r.get('resourceTemplates',[])),has_server_info=r.get('serverInfo') is not None,has_server_capabilities=r.get('serverCapabilities') is not None) for r in msg.get('result',{}).get('data',[])])
  elif str(method).startswith('account/'):safe.update(method=method,account_body_not_retained=True)
  elif 'error' in msg:safe.update(method=method,error_code=msg['error'].get('code'),error_message_hash=sha(str(msg['error'].get('message','')).encode()))
  elif str(msg.get('method','')).startswith(('mcp','account/','config/')):safe['notification_method']=msg.get('method')
  else:safe['message']=msg
  self.record(safe)
  if 'method' in msg and 'id' in msg:raise Stop('unexpected native request '+msg['method'])
  return msg
 def rpc(self,method,params,seconds=30):
  self.seq+=1;number=self.seq;self.sent[number]=method
  self.record(dict(direction='request',id=number,method=method,params=params))
  self.proc.stdin.write(canon(dict(id=number,method=method,params=params))+b'\n');self.proc.stdin.flush()
  end=min(self.deadline,time.perf_counter()+seconds)
  while time.perf_counter()<end:
   msg=self.recv(max(.1,end-time.perf_counter()))
   if msg.get('id')==number:
    if 'error' in msg:raise Stop('native RPC refused '+method+' code='+str(msg['error'].get('code')))
    return msg['result']
   self.events.append(msg)
  raise Stop('RPC deadline '+method)
 def init(self):
  r=self.rpc('initialize',{'clientInfo':{'name':'dg17-fresh-positive-qualification','version':'1'},'capabilities':{'experimentalApi':True}})
  self.proc.stdin.write(canon({'method':'initialized','params':{}})+b'\n');self.proc.stdin.flush();return r
 def paged(self,method,params):
  rows=[];cursor=None
  for _ in range(8):
   r=self.rpc(method,dict(params,**({'cursor':cursor} if cursor else {})));data=r.get('data');assert isinstance(data,list);rows+=data
   cursor=r.get('nextCursor')
   if not cursor:return rows
  raise Stop('metadata pagination bound')
 def hook_inventory(self, cwd, thread_id=None, seconds=30):
  if thread_id is not None:
   if not thread_id or thread_id != self.thread_id:
    raise Stop('hook inventory requires the bound loaded principal')
   params = {'threadId': thread_id}
  else:
   if self.thread_id is not None:
    raise Stop('cwd-only hook inventory is restricted to pre-creation')
   params = {'cwds': [str(cwd)]}
  return self._inventory_reply(cwd, params, seconds)
 def declared_hooks_for_proposal(self, cwd, seconds=30):
  # A declaration readback cannot establish which hooks the loaded principal will run.
  return self._inventory_reply(cwd, {'cwds': [str(cwd)]}, seconds)
 def _inventory_reply(self, cwd, params, seconds):
  data = self.rpc('hooks/list', params, seconds).get('data')
  if not isinstance(data, list) or len(data) != 1:
   raise Stop('hook inventory requires exactly one result for this query')
  entry = data[0]
  if (not isinstance(entry, dict) or not isinstance(entry.get('cwd'), str)
      or Path(entry['cwd']) != Path(cwd) or entry.get('errors') != []
      or entry.get('warnings') != [] or not isinstance(entry.get('hooks'), list)):
   raise Stop('hook inventory missing the bound scope or its complete diagnostics')
  return data
 def capabilities(self,cwd,thread_id=None):
  config=self.rpc('config/read',{'cwd':str(cwd),'includeLayers':True})
  web_search=config.get('config',{}).get('web_search')
  if web_search!='disabled':raise Stop('effective provider web_search disabled not established')
  features=self.paged('experimentalFeature/list',{'limit':100,**({'threadId':thread_id} if thread_id else {})})
  flags={r['name']:r['enabled'] for r in features}
  for key in ['apps','multi_agent','memories']:
   if flags.get(key) is not False:raise Stop('effective disabled feature not established: '+key)
  if 'multi_agent_v2' in flags and flags['multi_agent_v2'] is not False:raise Stop('advertised multi_agent_v2 not disabled')
  if flags.get('hooks') is not True:raise Stop('hook support not enabled')
  if flags.get('plugins') is not True:raise Stop('selected local plugin feature unavailable')
  selected=getattr(self,'local_plugin_selection',None)
  if not isinstance(selected,dict):raise Stop('exact local plugin source unbound')
  plugin_config=config.get('config',{}).get('plugins')
  if not isinstance(plugin_config,dict) or set(plugin_config)!={selected['key']} or plugin_config[selected['key']].get('enabled') is not True:raise Stop('unselected plugin configuration')
  effective=config.get('config')
  if not isinstance(effective,dict):raise Stop('effective configuration unavailable')
  # This selected isolated profile declares no MCP servers. Absence of its
  # optional table is accepted only together with a complete EMPTY native
  # inventory below, again on the loaded principal before a model turn.
  servers=effective.get('mcp_servers',{})
  if not isinstance(servers,dict) or servers:raise Stop('effective MCP configuration is not empty')
  enabled={}
  mcp=self.paged('mcpServerStatus/list',{'limit':100,**({'threadId':thread_id} if thread_id else {})})
  if mcp:raise Stop('effective MCP runtime inventory is not empty')
  flat=[hook for entry in self.hook_inventory(cwd,thread_id) for hook in entry['hooks']]
  safe=dict(features=flags,effective_web_search=web_search,effective_MCP_enabled=enabled,mcp=[dict(name=r['name'],zero_capabilities=True) for r in mcp],hooks=[hook_projection(h) for h in flat],layers=[dict(name=x['name'],version=x['version'],disabledReason=x.get('disabledReason')) for x in config.get('layers',[])])
  self.record(dict(kind='safe_effective_capabilities',value=safe));return config,flat,safe
 def turn(self,thread_id,prompt,seconds=180):
  end=min(self.deadline,time.perf_counter()+seconds)
  r=self.rpc('turn/start',{'threadId':thread_id,'input':[{'type':'text','text':prompt}],'model':'gpt-6.1-sol','effort':'high','approvalPolicy':'never','sandboxPolicy':{'type':'readOnly','networkAccess':False}},min(30,end-time.perf_counter()))
  self.turn_id=r['turn']['id'];self.active=True
  while time.perf_counter()<end:
   msg=self.recv(max(.1,end-time.perf_counter()));self.events.append(msg)
   if msg.get('method')=='turn/completed' and msg.get('params',{}).get('turn',{}).get('id')==self.turn_id:
    if msg['params']['turn']['status']!='completed':raise Stop('source observation turn noncomplete')
    self.active=False;return r,msg['params']
  raise Stop('model turn deadline')
 def close(self,cleanup_deadline=None):
  # Every wait shares one absolute cutoff. Expiry is UNKNOWN, never terminal credit.
  if cleanup_deadline is not None:self.deadline=cleanup_deadline
  cutoff=self.deadline;result={}
  def remaining(cap):return max(0,min(cap,cutoff-time.perf_counter()))
  if self.thread_id and self.turn_id and self.active:
   try:
    assert remaining(10)>0
    self.rpc('turn/interrupt',{'threadId':self.thread_id,'turnId':self.turn_id},remaining(10));result['interrupt_requested']=True
   except Exception:result['interrupt_not_required_or_unproved']=True
  if self.thread_id:
   try:
    assert remaining(10)>0
    r=self.rpc('thread/read',{'threadId':self.thread_id,'includeTurns':False},remaining(10));result['thread_read']=r
    result['actor_idle']=r['thread']['id']==self.thread_id and r['thread']['status']['type'] in ['idle','notLoaded']
   except Exception:result['actor_idle']=False
  else:result['actor_idle']=False
  waited=False
  try:
   self.proc.stdin.close();self.proc.wait(timeout=remaining(10));waited=True
  except Exception:
   try:self.proc.terminate()
   except Exception:result['terminate_unproved']=True
   try:self.proc.wait(timeout=remaining(5));waited=True
   except Exception:
    try:self.proc.kill()
    except Exception:result['kill_unproved']=True
    try:self.proc.wait(timeout=remaining(5));waited=True
    except Exception:result['server_terminal_unproved']=True
  result.update(server_exit=self.proc.returncode,server_wait_returned=waited,owned_appserver=self.identity)
  for t in self.readers:t.join(timeout=remaining(2))
  result['readers_done']=all(not t.is_alive() for t in self.readers)
  result['cleanup_cutoff_reached']=time.perf_counter()>=cutoff
  self.log.close();return result

def restricted(reply,cwd):
 if reply.get('cwd')!=str(cwd) or reply.get('model')!='gpt-6.1-sol' or reply.get('approvalPolicy')!='never' or reply.get('sandbox')!={'type':'readOnly','networkAccess':False}:raise Stop('native effective model/source/permission mismatch')
def journal_context(path,thread_id,turn_id,native_permission_witness):
 p=Path(path);st=p.lstat();assert st.st_size<=16*1024*1024 and not p.is_symlink() and not getattr(st,'st_file_attributes',0)&1024
 raw=p.read_bytes();rows=[json.loads(x) for x in raw.decode('utf-8').splitlines()]
 assert rows[0]['payload']['id']==thread_id
 contexts=[r['payload'] for r in rows if r.get('type')=='turn_context' and r.get('payload',{}).get('turn_id')==turn_id]
 assert len(contexts)==1;c=contexts[0]
 assert c['model']=='gpt-6.1-sol' and c['effort']=='high' and c['approval_policy']=='never'
 closed=c.get('sandbox_policy');assert isinstance(closed,dict) and closed.get('type')=='read-only'
 assert native_permission_witness['sandbox']=={'type':'readOnly','networkAccess':False} and native_permission_witness['approvalPolicy']=='never'
 if 'network_access' in closed:assert closed['network_access'] is False;network_basis='explicit native context false plus exact native response'
 else:
  assert set(closed)=={'type'},'unknown context permission fields'
  network_basis='actual native response explicit readOnly/networkAccessfalse + matching closed readonly context variant (schema ReadOnly defaultfalse), not absence alone'
 profile=c.get('permission_profile')
 if profile is not None:
  # Recognize only the actual historical qualified readOnly representation.
  # Any unknown/broader profile layout is stopped; disabled semantics are not inferred from a single correlation.
  assert isinstance(profile,dict) and profile.get('type')=='managed','unknown/broader actual permission profile'
  assert set(profile)=={'type','file_system','network'} and profile['network']=='restricted'
  fs=profile['file_system'];assert isinstance(fs,dict) and fs.get('type')=='restricted' and set(fs)=={'type','entries'}
  assert isinstance(fs['entries'],list) and all(isinstance(x,dict) and x.get('access') in ['read','none'] for x in fs['entries'])
 return dict(path=str(p),bytes=len(raw),sha256=sha(raw),network_basis=network_basis,native_permission_response_sha256=sha(canon(native_permission_witness)),turn_context={k:c.get(k) for k in ['turn_id','cwd','approval_policy','sandbox_policy','permission_profile','model','effort']})
