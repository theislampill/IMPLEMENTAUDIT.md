"""Inert conditional B: exact initial H0, three config leaves, first-event fence, teardown.

No OPERATION_B_BOUND.json is supplied. No import-side effect. First use requires
successful independently received fresh A and an actual new parent B grant.
"""
import argparse,copy,hashlib,json,os,subprocess,sys,time,types
from pathlib import Path
HERE=Path(__file__).absolute().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,x):
 with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
def get(cfg,keys):
 value=cfg
 for key in keys:
  if not isinstance(value,dict) or key not in value:return dict(present=False,value=None)
  value=value[key]
 return dict(present=True,value=value)
def differences(a,b,prefix=()):
 def leaves(value,path):
  if isinstance(value,dict) and value:
   return [p for key,item in value.items() for p in leaves(item,path+(key,))]
  return [path]
 if isinstance(a,dict) and isinstance(b,dict):
  result=[]
  for key in sorted(set(a)|set(b)):
   if key not in a:result+=leaves(b[key],prefix+(key,))
   elif key not in b:result+=leaves(a[key],prefix+(key,))
   else:result+=differences(a[key],b[key],prefix+(key,))
  return result
 return [] if a==b else [prefix]
def userlayer(config,home):
 rows=[x for x in config.get('layers',[]) if x['name']['type']=='user' and x['name'].get('profile') is None]
 assert len(rows)==1;row=rows[0];assert Path(row['name']['file']).resolve()==(Path(home)/'config.toml').resolve();return row
def load_code(item,name):
 p=Path(item['path']);raw=p.read_bytes();assert len(raw)==item['bytes'] and sha(raw)==item['sha256']
 m=types.ModuleType(name);m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__);return m
def verify_tombstone_postimage(expected,token,looked,reason):
 post=dict(expected,binding_generation='G0002',status='TOMBSTONED',predecessor_generation='G0001',supersession_or_tombstone_reason=reason)
 assert token['status']==looked['status']=='TOMBSTONED' and token['object_closed'] is False
 assert token['binding']==post and looked['binding']==post
 return post

def observe_selected_identity(fence,msg,trusted,session,turn_id):
 # Run IDs are opaque. Only the actual first matching start establishes one.
 method=msg['method'];params=msg['params'];run=params['run']
 assert params['threadId']==session and params['turnId']==turn_id
 for key in ['source','sourcePath','eventName','displayOrder','handlerType','statusMessage']:
  assert run.get(key)==trusted[key],'Selected hook tuple differs: '+key
 assert run.get('executionMode')=='sync' and run.get('scope')=='turn'
 observed=run.get('id');assert isinstance(observed,str) and observed,'Missing actual opaque hook run ID'
 if method=='hook/started':
  assert fence['selected_run_id'] is None and len(fence['started'])==1 and not fence['completed'],'Duplicate or late selected start'
  assert run.get('status')=='running'
  fence['selected_run_id']=observed
  fence['selected_start_thread']=params['threadId'];fence['selected_start_turn']=params['turnId']
 elif method=='hook/completed':
  assert len(fence['started'])==1 and len(fence['completed'])==1 and fence['selected_run_id'] is not None,'Missing or duplicate start/completion'
  assert observed==fence['selected_run_id'] and params['threadId']==fence['selected_start_thread'] and params['turnId']==fence['selected_start_turn'],'Completed hook differs from actual first start'
 else:raise AssertionError('Not a selected start/completion')
 return observed

def qualification_receipt_deadline(turn_end,pass_deadline):
 return min(turn_end,pass_deadline) if pass_deadline is not None else turn_end
def terminal_receipt_on_time(received_at,turn_end,pass_deadline):
 return received_at<=qualification_receipt_deadline(turn_end,pass_deadline)
def qualification_recv_remaining(now,turn_end,pass_deadline,requested):
 remaining=qualification_receipt_deadline(turn_end,pass_deadline)-now
 if remaining<=0:raise RuntimeError('Qualification receipt deadline reached before receive')
 return min(requested,remaining)

def main(args):
 op_raw=Path('C:\\workspace\\ai\\improveimplementaudit\\plans\\astra-r3-execution-20261114-01\\dg17-native-20261114-01\\OPERATION_B_BOUND.json').read_bytes();op=json.loads(op_raw);g=json.loads(args.grant.read_bytes())
 assert g['issuer']==op['issuer'] and g['stage']=='B' and g['operation_sha256']==sha(op_raw)
 assert g['post_A_sha256']==op['post_A']['sha256'] and g['owner_approval_sha256']==op['owner_approval']['sha256']
 gate=Path(g['independent_post_A']['path']).read_bytes();assert sha(gate)==g['independent_post_A']['sha256']==op['independent_post_A']['sha256']
 ar=Path(op['post_A']['path']).read_bytes();assert sha(ar)==op['post_A']['sha256'];a=json.loads(ar)
 assert a['status']=='STAGE_A_BOUND_CONTEXT_READY_FOR_INDEPENDENT_REVIEW' and a['thread_start_calls']==1 and a['model_turns']==1 and a['native_cleanup']['actor_idle'] is True
 assert a['H0_effects']==a['trust_effects']==a['qualifying_events']==0
 start=a['window_start_ns']/1e9;hard=start+900;deadline=start+780
 assert time.perf_counter()<start+570,'At least330s must remain in SAME actual900s window; no reset'
 for item in op['readset']:
  p=Path(item['path']);h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
  assert h.hexdigest()==item['sha256']
 case=Path(op['case']);out=case/'evidence'/'stage-B01';out.mkdir(exist_ok=False)
 rpc=load_code(op['rpc_module'],'qualified_episode_rpc');session=a['session'];repo=Path(a['claim']['repository']);root=Path(a['claim']['run_root'])
 inp=json.loads(Path(op['constructor_inputs']['path']).read_bytes());manifest=json.loads(Path(op['constructor_manifest']['path']).read_bytes())
 ctor=load_code(op['constructor'],'bound_positive_constructor')
 expected=ctor.expected_binding(inp);assert manifest['expected_initial_B_full_binding']==expected
 assert session==inp['host_session_id'] and expected['binding_generation']=='G0001'
 store=Path(inp['binding_store']);assert not store.exists(),'No re-init/rebind of existing or tombstoned store'
 hook=Path(manifest['intended_project_hook_path']);assert sha(hook.read_bytes())==manifest['hook_sha256']
 env=os.environ|{'PATH':op['fixed_path'],'PYTHONDONTWRITEBYTECODE':'1','CODEX_HOME':op['expected_codex_home']}
 result=dict(stage='B',operation_sha256=sha(op_raw),post_A_sha256=op['post_A']['sha256'],status='STARTED',window_start_ns=a['window_start_ns'],thread_start_calls=0,model_turn_requests=0,selected_starts=0,selected_completions=0,host_h0_bound=False,config_write_attempts=0)
 client=None;bound=False;writes=False;qual_id=None;fence=None;cleanup_mode=False
 def command(name,argv,cwd=repo,limit=45):
  if time.perf_counter()>deadline:raise RuntimeError('B work reserve reached')
  values=[str(v) for v in argv]
  if values[0]==op['bash']:values=[values[0],*(v.replace('\\','/') if len(v)>2 and v[1:3]==':\\' else v for v in values[1:])]
  if cleanup_mode:limit=min(limit,8)
  remaining=deadline-time.perf_counter();assert remaining>0,'No subprocess after absolute cutoff'
  r=subprocess.run(values,cwd=cwd,env=env,stdin=subprocess.DEVNULL,capture_output=True,timeout=min(limit,remaining))
  save(out/(name+'.json'),dict(argv=values,exit=r.returncode,stdout=r.stdout.decode('utf-8'),stderr=r.stderr.decode('utf-8')))
  if r.returncode:raise RuntimeError('B fixed owner refused '+name)
  return r.stdout.decode('utf-8').strip()
 def config_snapshot():return client.rpc('config/read',{'cwd':str(repo),'includeLayers':True},10 if cleanup_mode else 30)
 def leaf_write(name,keys,value):
  nonlocal writes
  before=userlayer(config_snapshot(),op['expected_codex_home']);cfg=before['config']
  allowed=[('projects',str(repo),'trust_level'),('hooks','state',result['hook_key'],'trusted_hash'),('hooks','state',result['hook_key'],'enabled')]
  assert tuple(keys) in allowed
  keypath='.'.join(json.dumps(x) if any(c in x for c in '.:\\/"') else x for x in keys)
  result['config_write_attempts']+=1;writes=True
  response=client.rpc('config/value/write',dict(keyPath=keypath,mergeStrategy='replace',value=value,filePath=before['name']['file'],expectedVersion=before['version']),10 if cleanup_mode else 30)
  after=userlayer(config_snapshot(),op['expected_codex_home']);delta=differences(cfg,after['config'])
  assert delta==[tuple(keys)] or (not delta and get(cfg,keys)==dict(present=True,value=value))
  assert get(after['config'],keys)==dict(present=True,value=value)
  save(out/(name+'.json'),dict(operation='config/value/write',keys=keys,value=value,before=get(cfg,keys),before_version=before['version'],response=response,after_version=after['version'],changed_leaves=[list(x) for x in delta],all_other_config_unchanged=True))
 def hook_entries(*, declared=False):
  timeout=10 if cleanup_mode else 30
  rows=client.declared_hooks_for_proposal(repo,timeout) if declared else client.hook_inventory(repo,session,timeout)
  own=[]
  for entry in rows:
   assert not entry['errors']
   for item in entry['hooks']:
    if item['source']=='project' and Path(item['sourcePath'])==hook:own.append(item)
    elif item.get('enabled') is not False:raise RuntimeError('Other enabled/unknown hook')
  assert len(own)==1;h=own[0]
  assert h['handlerType']=='command' and h['eventName']=='stop' and h['isManaged'] is False and h['timeoutSec']==60
  assert h['command']==manifest['commandWindows'] and h['key']==a['hook_key'] and h['currentHash']==a['native_current_hash']
  return h
 def check_context(turnid,witness):
  # Existing exact new journal, only a complete-prefix snapshot while append is active.
  p=Path(result['journal_path']);raw=p.read_bytes();assert len(raw)<=16*1024*1024
  end=len(raw) if raw.endswith(b'\n') else raw.rfind(b'\n')+1;assert end>0
  rows=[json.loads(line) for line in raw[:end].decode('utf-8').splitlines()]
  assert rows[0]['payload']['id']==session
  cs=[x['payload'] for x in rows if x.get('type')=='turn_context' and x.get('payload',{}).get('turn_id')==turnid];assert len(cs)==1;c=cs[0]
  assert c['model']=='gpt-6.1-sol' and c['effort']=='high' and c['approval_policy']=='never'
  assert witness['sandbox']=={'type':'readOnly','networkAccess':False} and c['sandbox_policy'].get('type')=='read-only'
  if 'network_access' in c['sandbox_policy']:assert c['sandbox_policy']['network_access'] is False
  else:assert set(c['sandbox_policy'])=={'type'},'Unknown permission context'
  profile=c.get('permission_profile')
  if profile is not None:
   assert isinstance(profile,dict) and profile.get('type')=='managed' and set(profile)=={'type','file_system','network'}
   fs=profile['file_system'];assert fs.get('type')=='restricted' and set(fs)=={'type','entries'} and all(x.get('access') in ['read','none'] for x in fs['entries']) and profile['network']=='restricted'
  return dict(journal=str(p),complete_prefix_bytes=end,complete_prefix_sha256=sha(raw[:end]),unconsumed_tail_bytes=len(raw)-end,unconsumed_tail_sha256=sha(raw[end:]),turn_context={k:c.get(k) for k in ['turn_id','cwd','approval_policy','sandbox_policy','permission_profile','model','effort']},explicit_native_sandbox=witness['sandbox'])
 try:
  client=rpc.Client(op['appserver_argv'],str(repo),env,case/'native-B',deadline);client.thread_id=session;result['initialize']=client.init();assert Path(result['initialize']['codexHome']).resolve()==Path(op['expected_codex_home']).resolve();client.local_plugin_selection=op['local_plugin_selection']
  resumed=client.rpc('thread/resume',{'threadId':session,'cwd':str(repo),'model':'gpt-6.1-sol','approvalPolicy':'never','sandbox':'read-only','runtimeWorkspaceRoots':[str(repo)],'config':{'model_reasoning_effort':'high'}});rpc.restricted(resumed,repo);assert resumed['thread']['id']==session;client.thread_id=session
  save(out/'ACTUAL_B_RESUME_PRE_EFFECT.json',resumed);result['journal_path']=resumed['thread']['path']
  assert len(resumed['thread'].get('turns',[]))<=1
  config,_,caps=client.capabilities(repo,session);save(out/'ACTUAL_B_CAPABILITIES.json',caps)
  h=hook_entries();assert h['trustStatus']=='untrusted';result['hook_key']=h['key']
  pre=json.loads(Path(op['config_preimages']['path']).read_bytes());u=userlayer(config,op['expected_codex_home'])
  assert u['version']==pre['version'] and sha(rpc.canon(u['config']))==pre['user_config_sha256'],'Post-A config changed; no blind adaptation'
  claim=[op['bash'],repo/'skills/implementaudit/scripts/claim-run.sh']
  assert command('01-currentness',claim+['--require-current-continuity',inp['controller_id']])==inp['applicable_continuity_receipt']
  core=[op['python']['path'],'-I','-S','-B',inp['binding_owner'],'--store',str(store)]
  command('02-owned-init',core+['init','--owner-id',op['new_store_owner']])
  flags={'owner-id':op['new_store_owner'],'host-id':'codex','host-session-id':session,'controller-id':inp['controller_id'],'claim-id':inp['claim_id'],'explicit-run-root':str(root),'repository-identity':str(repo),'git-common-directory-identity':inp['git_common_directory_identity'],'worktree-identity':str(repo),'activation-event-id':inp['activation_event_id'],'activation-receipt':inp['activation_receipt'],'continuity-generation':inp['applicable_continuity_generation'],'continuity-receipt':inp['applicable_continuity_receipt']}
  result['H0_bind_requested']=True
  actual=json.loads(command('03-owned-bind',core+['bind',*[v for k,value in flags.items() for v in ['--'+k,value]]]))
  bound=True;result['host_h0_bound']=True;ctor.verify_bound_result(inp,actual)
  looked=json.loads(command('04-owned-lookup',core+['lookup','--host-id','codex','--host-session-id',session]));ctor.verify_bound_result(inp,looked)
  assert actual==looked
  leaf_write('05-new-project-trust',['projects',str(repo),'trust_level'],'trusted')
  leaf_write('06-new-hook-trust',['hooks','state',h['key'],'trusted_hash'],h['currentHash'])
  # New definition defaults enabled; write only if actual API says it is not.
  if hook_entries(declared=True)['enabled'] is not True:leaf_write('07-new-hook-enable',['hooks','state',h['key'],'enabled'],True)
  trusted=hook_entries(declared=True);assert trusted['enabled'] is True and trusted['trustStatus']=='trusted'
  save(out/'ACTUAL_EXACT_TRUSTED_HOOK.json',trusted)
  effective=client.rpc('thread/resume',{'threadId':session,'cwd':str(repo),'model':'gpt-6.1-sol','approvalPolicy':'never','sandbox':'read-only','runtimeWorkspaceRoots':[str(repo)],'config':{'model_reasoning_effort':'high'}});rpc.restricted(effective,repo);assert effective['thread']['id']==session
  save(out/'ACTUAL_MODEL_PERMISSIONS_BEFORE_QUALIFYING.json',effective)
  _,_,caps=client.capabilities(repo,session);save(out/'ACTUAL_CAPABILITIES_AFTER_TRUST.json',caps);effective_hook=hook_entries();assert effective_hook['trustStatus']=='trusted' and effective_hook['enabled'] is True
  assert command('08-currentness-before-model',claim+['--require-current-continuity',inp['controller_id']])==inp['applicable_continuity_receipt']
  fence=dict(started=[],completed=[],selected_run_id=None,selected_entry_identity={k:trusted[k] for k in ['key','command','currentHash','source','sourcePath','eventName','displayOrder','handlerType','statusMessage']},first_completion=None,interrupt_request_id=None,interrupt_response=None,after_pass_activity=[],permission_snapshots=[],timeline=[])
  original_recv=client.recv;qual_request_sent=False;terminal=None;terminal_received_on_time=False;pass_deadline=None
  def interrupt(reason):
   if fence['interrupt_request_id'] is not None:return
   assert qual_id;client.seq+=1;number=client.seq;client.sent[number]='turn/interrupt';fence['interrupt_request_id']=number
   packet=dict(id=number,method='turn/interrupt',params={'threadId':session,'turnId':qual_id})
   fence['timeline'].append(dict(kind='owned_interrupt_send_before_receipt_IO',at_monotonic_ns=time.perf_counter_ns(),reason=reason))
   client.record(dict(direction='request',value=packet,first_event_containment_reason=reason));client.proc.stdin.write(rpc.canon(packet)+b'\n');client.proc.stdin.flush()
  def receive(seconds=30):
   nonlocal qual_id,pass_deadline,terminal,terminal_received_on_time
   if qual_request_sent and terminal is None and not cleanup_mode:
    try:seconds=qualification_recv_remaining(time.perf_counter(),turn_end,pass_deadline,seconds)
    except Exception:interrupt('qualification absolute receipt deadline before receive');raise
   msg=original_recv(seconds);received_at=time.perf_counter();method=msg.get('method');params=msg.get('params',{})
   if fence['interrupt_request_id'] is not None and msg.get('id')==fence['interrupt_request_id']:fence['interrupt_response']=msg
   if method=='turn/started' and params.get('threadId')==session and qual_request_sent:
    observed_id=params['turn']['id'];assert qual_id in [None,observed_id];qual_id=observed_id;client.turn_id=qual_id;client.active=True
   if method in ['hook/started','hook/completed']:
    run=params.get('run',{})
    selected=run.get('source')=='project' and Path(run.get('sourcePath',''))==hook and str(run.get('eventName','')).lower()=='stop'
    if selected:
     if not qual_request_sent or params.get('threadId')!=session:
      if qual_id is not None:interrupt('selected source unexpected principal/state')
      raise RuntimeError('selected source event not in exact requested principal')
     observed_id=params['turnId']
     if qual_id not in [None,observed_id]:interrupt('selected source wrong owned turn');raise RuntimeError('selected source wrongturn')
     qual_id=observed_id;client.turn_id=qual_id;client.active=True
     target='started' if method=='hook/started' else 'completed';fence[target].append(msg)
     fence['timeline'].append(dict(kind='selected_'+target,at_monotonic_ns=time.perf_counter_ns(),status=run.get('status')))
     if method=='hook/completed' and run.get('status')!='completed':interrupt('first selected nonPASS or unknown before receiptIO')
     try:observe_selected_identity(fence,msg,trusted,session,qual_id)
     except Exception:interrupt('selected-source actual start/completion identity mismatch');raise
     if method=='hook/started':
      try:fence['permission_snapshots'].append(check_context(qual_id,effective))
      except Exception:interrupt('effective permission witness unavailable/mismatch');raise
     else:
      # Critical order: first nonPASS interrupt is sent BEFORE any receipt IO.
      if fence['first_completion'] is None:
       fence['first_completion']=msg
       if run.get('status')!='completed':interrupt('first selected nonPASS '+str(run.get('status')))
       else:pass_deadline=min(deadline,received_at+10)
      else:interrupt('second selected completion')
   if fence['first_completion'] and fence['first_completion']['params']['run'].get('status')=='completed' and (method=='item/started' or str(method).endswith('/delta')):
    fence['after_pass_activity'].append(msg);interrupt('new model activity after firstPASS')
   if method=='turn/completed' and params.get('turn',{}).get('id')==qual_id:
    # Preserve actual terminal even when late; receipt time alone governs qualification.
    terminal=params;client.active=False
    terminal_received_on_time=terminal_receipt_on_time(received_at,turn_end,pass_deadline)
    fence['terminal_receipt']=dict(at_monotonic=received_at,turn_deadline=turn_end,pass_deadline=pass_deadline,accepting_deadline=qualification_receipt_deadline(turn_end,pass_deadline),on_time=terminal_received_on_time,actual_terminal=params)
    if not terminal_received_on_time:interrupt('late actual terminal receipt; not qualifying')
   return msg
  client.recv=receive
  prompt=('This exact new qualification object remains open. Read '+str(root/'STATE.md')+' and '+str(root/'ROADMAP.md')+' in separate bounded read-only actions. Then give one brief truthful nonterminal progress status. Do not write/repair any record, run lifecycle helpers, use network/MCP/apps/plugins/subagents, change bindings/trust/settings, or claim completion/handoff. Emit no completion orhandoff markers. The native owner judges the durable record; do not self-certify Stop success or retry a blocked response.')
  save(out/'QUALIFYING_PROMPT.json',dict(text=prompt,sha256=sha(prompt.encode())))
  qual_request_sent=True;result['model_turn_requests']=1;turn_end=min(deadline,time.perf_counter()+180)
  started=client.rpc('turn/start',{'threadId':session,'input':[{'type':'text','text':prompt}],'model':'gpt-6.1-sol','effort':'high','approvalPolicy':'never','sandboxPolicy':{'type':'readOnly','networkAccess':False}},min(30,turn_end-time.perf_counter()))
  returned=started['turn']['id'];assert qual_id in [None,returned];qual_id=returned;client.turn_id=qual_id;client.active=terminal is None
  while terminal is None and time.perf_counter()<turn_end:
   if time.perf_counter()>=qualification_receipt_deadline(turn_end,pass_deadline):interrupt('qualification absolute receipt deadline');break
   try:msg=client.recv(qualification_recv_remaining(time.perf_counter(),turn_end,pass_deadline,5))
   except Exception as error:
    if isinstance(error,__import__('queue').Empty):continue
    raise
   if msg.get('method')=='turn/completed' and msg.get('params',{}).get('turn',{}).get('id')==qual_id:
    assert terminal is not None;break
  if terminal is None:
   interrupt('qualifying deadline');cleanup_mode=True;finish=min(hard-50,time.perf_counter()+20)
   while time.perf_counter()<finish:
    remaining=finish-time.perf_counter()
    if remaining<=0:break
    msg=client.recv(remaining)
    if msg.get('method')=='turn/completed' and msg.get('params',{}).get('turn',{}).get('id')==qual_id:assert terminal is not None;break
  result.update(selected_starts=len(fence['started']),selected_completions=len(fence['completed']),fence=fence,terminal=terminal,qualifying_turn=qual_id)
  # No filesystem receipt inspection before the first-event containment fence above.
  assert terminal and terminal_received_on_time and terminal['turn']['status']=='completed' and fence['first_completion']['params']['run']['status']=='completed'
  assert len(fence['started'])==len(fence['completed'])==1 and not fence['after_pass_activity'] and fence['interrupt_request_id'] is None
  result['permissions_at_completion']=check_context(qual_id,effective)
  readback=client.rpc('thread/read',{'threadId':session,'includeTurns':True});assert readback['thread']['id']==session and readback['thread']['status']['type']=='idle';save(out/'ACTUAL_QUALIFIED_TURN_READBACK.json',readback)
  receipts=[]
  for p in Path(inp['evidence_directory']).glob('*.json'):
   r=json.loads(p.read_bytes())
   if r.get('event',{}).get('turn_id')==qual_id:receipts.append((p,r))
  assert len(receipts)==1;p,r=receipts[0]
  assert r['policy_sha256']==manifest['policy_sha256'] and r['validator_exit']==0 and r['selected_disposition']=='NONTERMINAL_YIELD'
  assert r['event']['session_id']==session and r['binding']==expected
  assert r['record_disposition']['record_disposition']=='NONTERMINAL_YIELD'
  result.update(status='ONE_ACTUAL_SELECTED_NATIVE_ALLOW_AND_NATURAL_NONTERMINAL_COMPLETION_AWAIT_INDEPENDENT_RECEIVING',native_receipt=dict(path=str(p),sha256=sha(p.read_bytes()),value=r))
 except Exception as error:
  result.update(status='STOPPED_FIRST_FAILURE_OR_UNKNOWN_NO_RETRY',error=repr(error))
  if fence is not None:result['fence']=fence
  raise
 finally:
  cleanup={};cleanup_mode=True
  if client is not None:
   client.deadline=hard-5
   # Contain only the actual known NEW active turn before config/receipt cleanup.
   # The first-event async interrupt is never repeated merely because its reply
   # is not yet observed; later actor-idle readback establishes completion.
   if client.active and client.turn_id:
    try:
     if fence is not None and 'interrupt' in locals():interrupt('teardown containment of known owned turn')
     else:client.rpc('turn/interrupt',{'threadId':session,'turnId':client.turn_id},10)
     cleanup['owned_interrupt_requested']=True
    except Exception as error:cleanup['interrupt_cleanup_error']=repr(error)
    cleanup['active_completion_requires_actual_readback']=True
    client.active=False
   try:
    if 'hook_key' in result and (writes or bound or result.get('H0_bind_requested')):
     leaf_write('TEARDOWN-disable-only-new-hook',['hooks','state',result['hook_key'],'enabled'],False)
     cleanup['new_hook_disabled_in_config']=hook_entries(declared=True)['enabled'] is False
     cleanup['new_hook_disabled']=cleanup['new_hook_disabled_in_config'] and hook_entries()['enabled'] is False
   except Exception as error:cleanup['hook_cleanup_error']=repr(error)
  if bound or result.get('H0_bind_requested'):
   try:
    # Teardown is admitted even after the work cutoff, within reserved global time.
    deadline=hard-5
    prior=json.loads(command('TEARDOWN-read-owned-binding-before-withdraw',core+['lookup','--host-id','codex','--host-session-id',session]))
    ctor.verify_bound_result(inp,prior)
    token=json.loads(command('TEARDOWN-new-binding-tombstone',core+['tombstone','--owner-id',op['new_store_owner'],'--host-id','codex','--host-session-id',session,'--expected-generation','G0001','--reason','Authorized single positive qualification ended; attribution withdrawn only, object remains open']))
    looked=json.loads(command('TEARDOWN-read-only-tombstone',core+['lookup','--host-id','codex','--host-session-id',session]))
    post=verify_tombstone_postimage(expected,token,looked,'Authorized single positive qualification ended; attribution withdrawn only, object remains open')
    cleanup['exact_tombstone_postimage']=post
    cleanup['new_binding_tombstoned_object_open']=True
   except Exception as error:cleanup['H0_cleanup_error']=repr(error)
  if client is not None:
   try:cleanup['native']=client.close(hard-5)
   except Exception as error:cleanup['native_cleanup_error']=repr(error)
  if fence is not None:
   result.update(selected_starts=len(fence['started']),selected_completions=len(fence['completed']))
   if len(fence['started'])!=1 or len(fence['completed'])!=1 or fence['after_pass_activity'] or fence['interrupt_request_id'] is not None:
    result['status']='FIRST_EVENT_OR_LATE_EXTRA_ACTIVITY_NOT_QUALIFYING'
  cleanup['config_residue']='Only approved three newproject/hook leaves retained inert; no null-delete/globalconfig rewrite attempted.'
  cleanup['known']=bool(cleanup.get('native',{}).get('actor_idle') and cleanup.get('native',{}).get('readers_done') and cleanup.get('native',{}).get('server_wait_returned') and not any(k.endswith('_error') for k in cleanup))
  if writes or bound or result.get('H0_bind_requested'):cleanup['known']=cleanup['known'] and cleanup.get('new_hook_disabled') is True and cleanup.get('new_binding_tombstoned_object_open') is True
  if not cleanup['known']:result['status']='STOPPED_TEARDOWN_UNKNOWN_NO_RETRY'
  result['cleanup']=cleanup;result['elapsed_global_seconds']=time.perf_counter()-start;save(out/'POST_B.json',result)
  if result['elapsed_global_seconds']>900:raise RuntimeError('Global window exceeded; no completion claim')
  if not cleanup['known']:raise RuntimeError('Teardown unknown; parent reconciliation required')
 print(json.dumps(dict(status=result['status'],post_B=str(out/'POST_B.json'))))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--grant',type=Path,required=True);main(ap.parse_args())
