"""Exact approved fresh-context Stage A only; no H0/trust/qualifying event. Parent-granted."""
import argparse,datetime,hashlib,json,os,re,stat,subprocess,sys,time,types
from pathlib import Path
HERE=Path(__file__).absolute().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,value):
 with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write('\n')
def pinned_module(item,name):
 p=Path(item['path']);s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not p.is_symlink() and not getattr(s,'st_file_attributes',0)&1024
 with p.open('rb') as f:
  opened=os.fstat(f.fileno());assert (s.st_dev,s.st_ino,s.st_nlink,s.st_size)==(opened.st_dev,opened.st_ino,opened.st_nlink,opened.st_size)
  raw=f.read(item['bytes']+1)
 assert len(raw)==item['bytes'] and sha(raw)==item['sha256']
 m=types.ModuleType(name);m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__);return m
def write_state(root,repo,epoch,approval,context,head,tree):
 prior_rows=[]
 if (root/'STATE.md').exists():prior_rows=[x for x in (root/'STATE.md').read_text(encoding='utf-8').splitlines() if re.match(r'^\| G[0-9A-F]{4} \|',x)]
 rows={'Run root':root.relative_to(repo).as_posix(),'Phase':'1','Status':'READY_TO_DISPATCH','Audit object state':'open','Owner/source':'PrimarySol approved isolated Y04 current-source qualification; parent programme remains open','Baseline ref':head,'Last check':context,'Next action':'Independent receiver checks fresh context; after explicit Stage B admission observe one valid nonterminal project Stop','Authorization state':'Fresh human A+B permission '+approval+'; Stage B conditional, no programme closure','Re-entry condition':'Read current STATE and ROADMAP separately and require exact controller continuity before any further qualified action','Current checkpoint':'Fresh source/principal preparation boundary; native allowance not yet received','Last completed step':context,'Pending decision':'Independent post-Stage-A source/permission/policy review and exact Stage B parent admission'}
 body='# Owned current-source positive qualification\n\n## Current phase\n\n| Field | Value |\n|---|---|\n'+''.join('| '+k+' | '+v+' |\n' for k,v in rows.items())
 body+='\n## Andon log\n\n| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |\n|---|---|---|---|---|---|---|---|\n\n## Context epochs and instruction applicability\n\nCurrent epoch: '+epoch+'\n\n| Epoch | Boundary | Observed at | Reconciled inputs | Reconciled? | Notes |\n|---|---|---|---|---|---|\n'
 body+='\n'.join(prior_rows)+('\n' if prior_rows else '')+'| '+epoch+' | '+('new-session' if epoch!='G0001' else 'manual-resume')+' | '+datetime.datetime.now(datetime.timezone.utc).isoformat()+' | HEAD '+head+' tree '+tree+'; '+context+' | yes | Source/currentness only, not native allowance |\n'
 (root/'STATE.md').write_text(body,encoding='utf-8',newline='\n')
 if not (root/'ROADMAP.md').exists():(root/'ROADMAP.md').write_text('# Qualification frontier\n\nCurrent intake: establish and independently receive one fresh authorized source/principal context; native allowance and parent programme remain open.\n\n| # | Phase | Depends on | Status |\n|---|---|---|---|\n| 1 | Establish and independently receive one fresh authorized source/principal context | none | open |\n\nThinking file: `<run-root>/THINKING.md`\n',encoding='utf-8',newline='\n')
 phase=root/'phases/phase-1.md'
 if not phase.exists():
  phase.parent.mkdir(exist_ok=True);phase.write_text(PHASE_1.format(run=root.relative_to(repo).as_posix(),head=head,tree=tree,helper=(repo/'skills/implementaudit/scripts/claim-run.sh').as_posix(),controller=(root/'.controller').read_text(encoding='utf-8').strip().split('=',1)[1]),encoding='utf-8',newline='\n')
PHASE_1='# Phase 1 — Receive one fresh authorized source/principal context\n\nIMPLEMENTAUDIT_PHASE_START\nTask: Owned current-source positive qualification, Stage A source/principal preparation only\nType: brownfield\nRun root: {run}\nBaseline ref: {head}\nOwner/source: {run}/STATE.md and the actual source at {head}\nAudit object: the owner-authorized bounded initialization and receiving task\nDepends on phases: none\n\n## Work\n\nEstablish verified fresh execution custody, then perform the stated receiving task. Preserve predecessor evidence as history. No completed result is inferred from initialization.\n\n## Implementation steps (ordered)\n\n- Step 1: Receive the initialized root — target: {run}; change: publish only after the initialization validator and expected-old guards pass; verify: run the public activation and normal continuity entry points; expected: exact real receipt verifies against this source and state.\n- Step 2: Perform the authorized next action — target: the bounded task in STATE.md; change: independent receiver checks the fresh context; verify: capture the actual operation and final readback; expected: the specific receiving result is supported without a duplicate predecessor effect.\n\n## Scope boundaries\n\nIn scope: initialization of this fresh run, normal continuity, and the explicitly stated receiving task.\nOut of scope: original incident custody reconstruction, protected bodies, credentials, publication, product commits, installed-home changes, or acceptance awards.\n\n## STOP conditions (plan-specific)\n\n- Stop if the claim, controller token, source HEAD/tree or initializer source of this root differs from the received binding.\n- Stop if an existing partial file conflicts with the real author input; preserve both observations and do not replace the file automatically.\n\n## Current state excerpts\n\n- Actual target HEAD is {head}; tree is {tree}.\n- Actual controller is {controller}.\n- No phase or effect is completed in this authored initial checkpoint.\n\n## Acceptance criteria\n\n- [ ] All seven real task files pass the existing structural validator under the authenticated pending context.\n- [ ] Normal resume, verify and require calls obtain and verify actual fresh continuity.\n- [ ] The declared next action has its own real result and no duplicated predecessor effect.\n\n## Mandatory commands\n\n- bash {helper} --require-current-continuity {controller} > <run-root>/evidence/require-currentness.txt 2>&1 — property: behavioral; scope: this exact fresh controller; coverage: full; capture: <run-root>/evidence/require-currentness.txt; expected: exit 0 only after real receipt verification.\n\n## Evidence required\n\n- Actual CLI command captures, source/claim/ref readback, and the declared receiving result.\n- Markdown fallback: yes; sidecars are not an authorization dependency for this task.\n\n## Rollback / defer path\n\nRetain incomplete custody and fail closed; remove only the explicitly owned disposable fixture after its selected evidence has been retained. Do not roll back an original controller or published effect.\n\n## Maintenance notes\n\n- Keep this phase bound to the actual task and source. It does not substitute for a reviewer or a continuity receipt.\n\nIMPLEMENTAUDIT_PHASE_VERIFY\nNo verification passage is claimed in the initial checkpoint.\n\nAGENTS_UPDATE_DECISION\nNo durable repository instruction change is requested by this receiving task.\n\nCONTINUITY_DECISION\nPreserve the actual fresh receipt only after the normal owner emits it.\n\nIMPLEMENTAUDIT_PHASE_DONE\nStatus: open\n'
def verify_isolated_profile(op):
 home=Path(op['expected_codex_home'])
 assert home.name=='isolated-home-01' and home.parent==Path(op['case']).parent,'Exact isolated task home required'
 guard=pinned_module(op['constructor'],'isolated_profile_physical_guard')
 guard.path(home)
 assert home.is_dir() and home.resolve(strict=True)==home,'Physical isolated home required'
 guard.pinned(home/'config.toml',op['profile_sha256'],65536)

def receive_selected_plugin(client,op,repo,out):
 selection=op['local_plugin_selection']
 verify_isolated_profile(op)
 account=client.rpc('account/read',{'refreshToken':False})
 if not isinstance(account.get('account'),dict):raise RuntimeError('Isolated authenticated provider route unavailable; no principal created')
 save(out/'AUTH_ROUTE_RECEIVING.json',dict(account_response_sha256=sha(rpc_bytes(account)),authenticated_account_present=True,credential_material_retained=False))
 installed=client.rpc('plugin/install',dict(pluginName='implementaudit',marketplacePath=selection['marketplace_file']))
 if installed.get('appsNeedingAuth')!=[]:raise RuntimeError('Unapproved plugin app authentication')
 detail=client.rpc('plugin/read',dict(pluginName='implementaudit',marketplacePath=selection['marketplace_file']))['plugin']
 if detail.get('marketplaceName')!='implementaudit' or detail.get('apps')!=[] or detail.get('mcpServers')!=[] or detail.get('hooks')!=[]:raise RuntimeError('Unexpected canonical plugin effects')
 plugin_id=detail['summary']['id'];listed=client.rpc('skills/list',dict(cwds=[str(repo)],forceReload=True))
 rows=[x for entry in listed['data'] for x in entry['skills'] if x.get('pluginId')==plugin_id]
 if any(entry.get('errors') for entry in listed['data']):raise RuntimeError('Native skill discovery errors')
 if sorted(x['name'] for x in rows)!=sorted(op['native_skill_pins']):raise RuntimeError('Exact five-skill native discovery not established')
 for row in rows:
  path=Path(row['path']);assert path.is_relative_to(Path(op['expected_codex_home'])) and row['enabled'] is True
  expected=op['native_skill_pins'][row['name']];assert path.is_file() and digest(path)==expected
 save(out/'ACTUAL_PLUGIN_SKILL_DISCOVERY.json',dict(plugin=detail,skills=rows,source_package=op['package'],native_activation_or_T12_accepted=False))
def rpc_bytes(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()

def main(args):
 op_raw=(HERE/'OPERATION_A.json').read_bytes();op=json.loads(op_raw);grant=json.loads(args.grant.read_bytes())
 assert grant['issuer']==op['issuer'] and grant['stage']=='A' and grant['operation_sha256']==sha(op_raw)
 assert grant['owner_approval_sha256']==op['owner_approval']['sha256'] and grant['resource_ack_received'] is True
 for item in op['readset']:
  p=Path(item['path']);assert p.is_file() and digest(p)==item['sha256'],str(p)
 assert Path(sys.executable).resolve()==Path(op['python']['path']).resolve()
 start=args.window_start_ns/1e9;deadline=start+810
 assert 0<=time.perf_counter()-start<15,'Clock must start at first parent-admitted effect, before this child.'
 case=Path(op['case']);assert not case.exists();case.mkdir();out=case/'evidence';out.mkdir()
 save(out/'START.json',dict(operation_sha256=sha(op_raw),owner_approval=op['owner_approval'],parent_grant=grant,window_start_ns=args.window_start_ns,window_total_seconds=900,model_turns=0))
 result=dict(stage='A',operation_sha256=sha(op_raw),status='STARTED',window_start_ns=args.window_start_ns,thread_start_calls=0,model_turns=0,H0_effects=0,trust_effects=0,qualifying_events=0)
 rpcmod=pinned_module(op['rpc_module'],'bounded_native_rpc');client=None
 env=os.environ|{'PATH':op['fixed_path'],'PYTHONDONTWRITEBYTECODE':'1','CODEX_HOME':op['expected_codex_home']}
 def command(name,argv,cwd,limit=60):
  if time.perf_counter()>deadline-120:raise RuntimeError('Insufficient global cleanup time')
  values=[str(v) for v in argv]
  if values[0]==op['bash']:values=[values[0],*(v.replace('\\','/') if len(v)>2 and v[1:3]==':\\' else v for v in values[1:])]
  r=subprocess.run(values,cwd=cwd,env=env,stdin=subprocess.DEVNULL,capture_output=True,timeout=min(limit,deadline-time.perf_counter()))
  save(out/(name+'.json'),dict(argv=[str(v) for v in argv],cwd=str(cwd),exit=r.returncode,stdout=r.stdout.decode('utf-8','strict'),stderr=r.stderr.decode('utf-8','strict')))
  if r.returncode:raise RuntimeError('source helper refused '+name)
  return r.stdout.decode('utf-8').strip()
 repo=case/'source';controller=op['controller'];root=None
 try:
  command('01-clone',[op['git'],'-c','core.longpaths=true','clone','--shared','--single-branch','--no-checkout','--branch',op['branch'],op['source_worktree'],repo],op['source_worktree'],120)
  command('02-checkout',[op['git'],'-c','core.autocrlf=false','checkout','--detach',op['source_head']],repo)
  assert command('03-head',[op['git'],'rev-parse','HEAD'],repo)==op['source_head']
  assert command('04-tree',[op['git'],'rev-parse','HEAD^{tree}'],repo)==op['source_tree']
  assert not command('05-controller-ref-absence',[op['git'],'for-each-ref','--format=%(refname)','refs/implementaudit/controllers/','refs/implementaudit/current-generations/','refs/implementaudit/current-generation-migrations/'],repo)
  for rel,expected in op['source_pins'].items():assert digest(repo/rel)==expected
  claim=[op['bash'],repo/'skills/implementaudit/scripts/claim-run.sh']
  rel=command('06-new-claim',claim+['--controller',controller,'dg17-y04-current-positive'],repo);root=repo/rel
  assert root.is_dir() and root.is_relative_to(repo)
  for name in ['PROTOCOL.md','THINKING.md','sidecars.md','tools.md','context.md']:
   assert not (root/name).exists();(root/name).write_bytes((repo/'skills/implementaudit/templates'/name).read_bytes())
  write_state(root,repo,'G0001',op['owner_approval']['sha256'],'Actual exact-source clone, claim and source-only preparation complete',op['source_head'],op['source_tree'])
  rel=root.relative_to(repo).as_posix()
  pending=json.loads(command('06a-inspect-initialization',claim+['--inspect-controller-initialization',controller,'--run-root',rel],repo))
  assert pending['binding_record_oid'] is None and pending['current_controller_oid'] is None and pending['missing_files']==[] and pending['prepared_source_head']==op['source_head']
  bound=json.loads(command('06b-activate-controller',claim+['--activate-controller',controller,'--run-root',rel,'--expected-initialization',pending['initialization_token']],repo))
  assert bound['status']=='BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS' and bound['initialization_token']==pending['initialization_token']
  token=command('07-source-bootstrap',claim+['--resume-controller',controller,'--boundary','manual-resume','--epoch','G0001'],repo)
  assert command('08-source-verify',claim+['--verify-resume-receipt',token],repo)==token
  assert command('09-source-require',claim+['--require-current-continuity',controller],repo)==token
  # Explicit only intake/READY source predicate, never a constructed native event.
  command('10-source-positive',[op['bash'],repo/'skills/implementaudit/scripts/validate-run-root.sh','--nonterminal-yield',root],repo,30)
  assert not (repo/'.codex/hooks.json').exists()
  verify_isolated_profile(op)
  client=rpcmod.Client(op['appserver_argv'],str(repo),env,case/'native-A',deadline)
  client.local_plugin_selection=op['local_plugin_selection']
  result['initialize']=client.init()
  assert Path(result['initialize']['codexHome']).resolve()==Path(op['expected_codex_home']).resolve(),'Unapproved authentication/config home'
  receive_selected_plugin(client,op,repo,out)
  config,hooks,caps=client.capabilities(repo)
  if any(h.get('enabled') is not False for h in hooks):raise RuntimeError('unapproved enabled/unknown other hook')
  save(out/'PRE_MODEL_CAPABILITIES.json',caps)
  result['thread_start_calls']=1
  created=client.rpc('thread/start',{'cwd':str(repo),'model':'gpt-6.1-sol','allowProviderModelFallback':False,'approvalPolicy':'never','sandbox':'read-only','runtimeWorkspaceRoots':[str(repo)],'dynamicTools':[],'ephemeral':False})
  save(out/'ACTUAL_THREAD_START.json',created);session=created.get('thread',{}).get('id')
  if isinstance(session,str) and re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',session):client.thread_id=session;result['actual_principal']=session
  else:raise RuntimeError('native principal creation response unbound/unknown')
  rpcmod.restricted(created,repo)
  readback=client.rpc('thread/read',{'threadId':session,'includeTurns':False});assert readback['thread']['id']==session
  save(out/'ACTUAL_THREAD_READ.json',readback)
  config,hooks,caps=client.capabilities(repo,session)
  if any(h.get('enabled') is not False for h in hooks):raise RuntimeError('unapproved hook before observation')
  save(out/'ACTUAL_THREAD_CAPABILITIES.json',caps)
  prompt=('Approved ONE preliminary read-only source observation, NOT the qualified Stop test. Read '+str(root/'STATE.md')+' and '+str(root/'ROADMAP.md')+' in separate bounded read-only native shell actions. Then use a read-only command to compute SHA256 of these actual source members: '+', '.join(op['observation_members'])+'. Return observed hashes and any inability to read. Do not modify any file, invoke lifecycle helpers, use apps/plugins/MCP/subagents/network, change settings/bindings/trust, or claim Stop/closure/handoff success. Emit no audit completion or handoff markers. If capability is unavailable, report the first failure without retry/fallback.')
  result['model_turns']=1;save(out/'OBSERVATION_PROMPT.json',dict(text=prompt,sha256=sha(prompt.encode())))
  begun,completed=client.turn(session,prompt,180);turnid=begun['turn']['id']
  observed=client.rpc('thread/read',{'threadId':session,'includeTurns':True});save(out/'ACTUAL_OBSERVATION_READ.json',observed)
  assert observed['thread']['id']==session and observed['thread']['status']['type']=='idle'
  turn=next(x for x in observed['thread']['turns'] if x['id']==turnid)
  commands=[x for x in turn['items'] if x.get('type')=='commandExecution']
  assert len(commands)>=2 and all(x.get('status')=='completed' and x.get('exitCode')==0 for x in commands)
  observed_text='\n'.join(str(x.get('aggregatedOutput','')) for x in commands)
  for member in op['observation_members']:
   if op['source_pins'][member] not in observed_text:raise RuntimeError('actual source observation missing hash '+member)
  context=rpcmod.journal_context(observed['thread']['path'],session,turnid,created);save(out/'ACTUAL_PERMISSION_CONTEXT.json',context)
  (out/'STATE_G0001_NATIVE_SCOPE.md').write_bytes((root/'STATE.md').read_bytes());(out/'ROADMAP_G0001_NATIVE_SCOPE.md').write_bytes((root/'ROADMAP.md').read_bytes())
  command('11-invalidate-new-session',claim+['--invalidate-continuity',controller,'--boundary','new-session','--event','native-thread-start-'+session],repo)
  write_state(root,repo,'G0002',op['owner_approval']['sha256'],'Actual new session '+session+' source-observation '+turnid+' completed with effective readOnly/networkoff; independent positive Stop not performed',op['source_head'],op['source_tree'])
  command('12-separate-STATE-read',[op['python']['path'],'-I','-S','-B','-c','from pathlib import Path;print(Path('+repr(str(root/'STATE.md'))+').read_text(encoding="utf-8"))'],repo)
  command('13-separate-ROADMAP-read',[op['python']['path'],'-I','-S','-B','-c','from pathlib import Path;print(Path('+repr(str(root/'ROADMAP.md'))+').read_text(encoding="utf-8"))'],repo)
  token=command('14-native-context-resume',claim+['--resume-controller',controller,'--boundary','new-session','--epoch','G0002'],repo)
  assert command('15-native-context-verify',claim+['--verify-resume-receipt',token],repo)==token
  assert command('16-native-context-require',claim+['--require-current-continuity',controller],repo)==token
  ownerrow=command('17-current-controller',claim+['--current-controller',controller],repo).split('\t');assert len(ownerrow)==4 and Path(ownerrow[2])==root
  seed=dict(actual_thread_start=created,actual_observation_turn=turnid,actual_permission_context=context,controller=controller,claim_id=ownerrow[3],run_root=str(root),repository=str(repo),currentness=token,stage='A_IDENTITY_CLAIM_SUBRECEIPT_ONLY_NOT_B_ADMISSION')
  save(out/'ACTUAL_A_IDENTITY_AND_CLAIM.json',seed)
  ctor_dir=case/'constructor';ctor_dir.mkdir();ctor_path=ctor_dir/'positive_hook_constructor_v2.py';ctor_path.write_bytes(Path(op['constructor']['path']).read_bytes());assert digest(ctor_path)==op['constructor']['sha256']
  ctor=pinned_module(dict(path=str(ctor_path),bytes=op['constructor']['bytes'],sha256=op['constructor']['sha256']),'owned_positive_hook_constructor')
  inputs=dict(host_session_id=session,controller_id=controller,claim_id=ownerrow[3],explicit_run_root=str(root),repository_identity=str(repo),git_common_directory_identity=str(repo/'.git'),worktree_identity=str(repo),applicable_continuity_generation='G0002',applicable_continuity_receipt=token,activation_event_id='native-thread-start-'+session,activation_receipt='sha256:'+sha(rpcmod.canon(created)),binding_store=str(case/'host-store'),evidence_directory=str(out/'native-stop'),binding_owner=op['binding_owner']['path'],handler=str(repo/'skills/implementaudit/scripts/host-stop-interlock.py'),validator=str(repo/'skills/implementaudit/scripts/validate-run-root.sh'),custody=str(repo/'skills/implementaudit/scripts/canonical_custody.py'),python=op['python']['path'],bash=op['bash'],bash_sha256=op['bash_sha256'],fixed_path=op['fixed_path'],actual_stage_a_receipt=dict(path=str(out/'ACTUAL_A_IDENTITY_AND_CLAIM.json'),sha256=digest(out/'ACTUAL_A_IDENTITY_AND_CLAIM.json')),owner_approval_receipt=op['owner_approval'])
  save(out/'CONSTRUCTOR_ACTUAL_INPUTS.json',inputs);manifest=ctor.build(inputs,ctor_dir/'bound-positive');save(out/'CONSTRUCTOR_MANIFEST.json',manifest)
  hook=repo/'.codex/hooks.json';hook.parent.mkdir(exist_ok=True);assert not hook.exists();hook.write_bytes(Path(manifest['hook_proposal_path']).read_bytes());assert digest(hook)==manifest['hook_sha256']
  snapshot=client.declared_hooks_for_proposal(repo);own=[]
  for entry in snapshot:
   if entry.get('errors'):raise RuntimeError('hook discovery errors after proposal')
   for h in entry['hooks']:
    if h.get('source')=='project' and Path(h.get('sourcePath',''))==hook:own.append(h)
    elif h.get('enabled') is not False:raise RuntimeError('other hook enabled/unknown')
  assert len(own)==1 and own[0]['eventName']=='stop' and own[0]['handlerType']=='command' and own[0]['timeoutSec']==60 and own[0].get('isManaged') is False and own[0].get('trustStatus')=='untrusted'
  loaded=[]
  for entry in client.hook_inventory(repo,session):
   for item in entry['hooks']:
    if item.get('source')=='project' and Path(item.get('sourcePath',''))==hook:
     if any(item.get(field)!=own[0].get(field) for field in ('key','currentHash','handlerType','eventName','isManaged','trustStatus','command')):
      raise RuntimeError('loaded proposal differs from declared hook')
     loaded.append(item)
    elif item.get('enabled') is not False:
     raise RuntimeError('other enabled or unknown loaded hook')
  if len(loaded)>1:raise RuntimeError('ambiguous loaded project hook')
  save(out/'POST_PROPOSAL_SCOPE.json',{'declared':True,'loaded_at_observation':bool(loaded),'turn_authority':False})
  save(out/'ACTUAL_UNTRUSTED_HOOK.json',own[0])
  config=client.rpc('config/read',{'cwd':str(repo),'includeLayers':True})
  user=[x for x in config.get('layers',[]) if x['name']['type']=='user' and x['name'].get('profile') is None];assert len(user)==1
  cfg=user[0]['config'];key=own[0]['key'];project=cfg.get('projects',{}).get(str(repo),{});state=cfg.get('hooks',{}).get('state',{}).get(key,{})
  pre=dict(file=user[0]['name']['file'],version=user[0]['version'],user_config_sha256=sha(rpcmod.canon(cfg)),project_trust=dict(present='trust_level' in project,value=project.get('trust_level')),hook_trusted_hash=dict(present='trusted_hash' in state,value=state.get('trusted_hash')),hook_enabled=dict(present='enabled' in state,value=state.get('enabled')))
  assert not any(x['present'] for x in [pre['project_trust'],pre['hook_trusted_hash'],pre['hook_enabled']]),'Fresh context collides with preexisting scoped config'
  save(out/'EXACT_THREE_LEAF_PREIMAGES.json',pre)
  result.update(status='STAGE_A_BOUND_CONTEXT_READY_FOR_INDEPENDENT_REVIEW',session=session,turn=turnid,claim=seed,constructor_manifest=manifest,hook_key=key,native_current_hash=own[0]['currentHash'],post_A_H0_trust_qualifying_effects=0,remaining_global_seconds=900-(time.perf_counter()-start))
 except Exception as error:result.update(status='STAGE_A_STOPPED_FIRST_REFUSAL_OR_UNKNOWN_NO_RETRY',error=repr(error));raise
 finally:
  if client is not None:result['native_cleanup']=client.close(start+895)
  result['elapsed_global_seconds']=time.perf_counter()-start
  save(out/'POST_A.json',result)
 if result.get('native_cleanup',{}).get('actor_idle') is not True:raise RuntimeError('New principal idle state not verified')
 print(json.dumps(dict(status=result['status'],post_A=str(out/'POST_A.json'),remaining_global_seconds=result['remaining_global_seconds'])))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--grant',type=Path,required=True);ap.add_argument('--window-start-ns',type=int,required=True);main(ap.parse_args())
