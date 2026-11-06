#!/usr/bin/env python3
"""One prospective fresh H0 mechanical episode; execution requires actual GO."""
import argparse
import ast
import contextlib
from datetime import datetime,timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import resource
import sys
import tarfile
import traceback

HERE=Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location('h0_host_io',HERE/'host_io.py');H=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(H)
sys.dont_write_bytecode=True
NEXT_ACTION='Open the exact canonical audit-state route and receive the seven mechanical occurrences through the existing reader while native custody remains live'

def prepared(work):
 request_raw=H.read(work/'HOST_REQUEST.json');request=H.parse(request_raw)
 manifest_raw=H.read(work/'INPUT_MANIFEST.json');manifest=H.parse(manifest_raw)
 seal_raw=H.read(work/'SEALED_PREPARATION.json');seal=H.parse(seal_raw)
 H.need(request['preparation_sha256']==H.sha(seal_raw) and request['input_manifest_sha256']==H.sha(manifest_raw),'PREPARATION_BINDING')
 H.need(request['source_commit']==manifest['source_commit']==H.SOURCE_COMMIT and request['source_tree']==H.SOURCE_TREE and manifest['source_tree']==H.SOURCE_TREE and request['controller']==H.CONTROLLER,'PREPARATION_SCOPE')
 actual=H.census(manifest);state=H.parse(H.read(work/'HOST_STATE.json'))
 H.need(state['input_custody']==actual and H.sha(H.encode(actual))==request['input_custody_sha256'],'PREPARATION_INPUT_CUSTODY')
 H.need(state['request_sha256']==H.sha(request_raw),'PREPARATION_REQUEST_IDENTITY')
 for name,physical in state['identities'].items():H.need(H.pin(work/name,4*1024*1024)[1]==physical,'PREPARATION_PHYSICAL_IDENTITY_CHANGED')
 for row in seal['files']:
  path=work/row['name'];raw=H.read(path)
  H.need(len(raw)==row['bytes'] and H.sha(raw)==row['sha256'],'PREPARATION_FILE_CHANGED')
  if path.suffix=='.py':ast.parse(raw)
 return request,manifest,state

def grant(work,request,go_sha):
 raw=H.read(work/'ROOT_GO.json',65536);go=H.parse(raw);review_raw=H.read(work/'INDEPENDENT_REVIEW.json',65536);review=H.parse(review_raw)
 H.need(type(go_sha) is str and re.fullmatch('[0-9a-f]{64}',go_sha) and H.sha(raw)==go_sha,'EXACT_GO_REQUIRED')
 fixed={'schema':'r5.h0-root-go.v1','author':'/root','decision':'GO','one_shot':True,'host_request_sha256':H.sha(H.read(work/'HOST_REQUEST.json')),'preparation_sha256':request['preparation_sha256'],'input_custody_sha256':request['input_custody_sha256'],'subject':request['subject'],'controller':H.CONTROLLER,'source_commit':request['source_commit'],'source_tree':H.SOURCE_TREE,'review_sha256':H.sha(review_raw),'allocations':request['allocations']}
 H.need(H.matches(go,fixed),'GO_SCOPE')
 H.need(type(review) is dict and review.get('schema')=='r5.h0-independent-host-review.v1' and review.get('decision')=='PASS' and review.get('blocking_findings')==[] and review.get('host_request_sha256')==fixed['host_request_sha256'] and review.get('preparation_sha256')==request['preparation_sha256'] and H.independent_reviewer(review.get('reviewer')),'INDEPENDENT_REVIEW_SCOPE')
 return go

class Subject:
 def __init__(self,work,request,manifest,go_sha):
  self.go_sha=go_sha
  self.work,self.request,self.manifest=work,request,manifest;self.root=work/'private';self.root.mkdir(mode=0o700)
  self.repo=self.root/'subject';self.repo.mkdir(mode=0o700);self.evidence=self.root/'evidence';self.evidence.mkdir(mode=0o700)
  self.scripts=self.repo/'skills/implementaudit/scripts';self.commands=[];self.copied={}
  for item in manifest['members']:
   if 'destination' not in item:continue
   raw=H.read(item['path']);target=self.repo/item['destination'];H.write(target,raw,mode=item['mode']);self.copied[str(target)]=(raw,item['mode'],H.pin(target,4*1024*1024)[1])
  self.python=next(r['path'] for r in manifest['members'] if r['key']=='system/python3')
  self.gitpath=next(r['path'] for r in manifest['members'] if r['key']=='system/git')
  self.bash=next(r['path'] for r in manifest['members'] if r['key']=='system/bash')
  self.env=dict(H.ENV,IMPLEMENTAUDIT_PYTHON=self.python)
  self.git('-c','init.templateDir=','init','-q','-b','qualification','--object-format=sha1')
  H.write(self.repo/'.gitignore',b'.IMPLEMENTAUDIT/\n.task-tmp/\nskills/\nfixtures/\n')
  H.write(self.repo/'TASK.json',{'purpose':'Actual selected-prior original and exact BIND retry through existing H0 reader','source_checkpoint_commit':request['source_commit'],'source_checkpoint_tree':H.SOURCE_TREE,'root_go_sha256':go_sha,'historical_83_44_preserved':True,'old_pending_consumed':False,'model_inference':False,'original_acceptance':False})
  self.git('add','--','.gitignore','TASK.json')
  self.git('-c','user.name=DG18 isolated H0 mechanical fixture','-c','user.email=h0@example.invalid','-c','commit.gpgsign=false','-c','core.hooksPath=/dev/null','commit','-qm','Define one authorized H0 mechanical subject')
  self.head=self.git('rev-parse','HEAD').decode().strip();self.tree=self.git('rev-parse','HEAD^{tree}').decode().strip()
  relative=self.claim('--controller',H.CONTROLLER,'R5 H0 selected prior mechanical episode').decode().strip()
  H.need(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9-]+-[A-Za-z0-9]{6}',relative),'FRESH_RUN_ROOT')
  self.run=self.repo/relative
  purpose='Establish one genuine fresh native boundary needed by the exact same-session pending owner, then observe seven mechanical LOAD DELIVER BIND occurrences including selected prior and exact retry; retain unresolved scope and no RETURN or JOIN.'
  next_action=NEXT_ACTION
  self.call([self.python,'-I','-B',self.repo/'fixtures/controller-initialization/author_checkpoint.py','--repo',self.repo,'--run-root',relative,'--source',self.repo,'--purpose',purpose,'--next-action',next_action])
  inspection=H.parse(self.claim('--inspect-controller-initialization',H.CONTROLLER,'--run-root',relative))
  H.need(inspection['current_controller_oid'] is None and inspection['missing_files']==[],'INITIALIZATION_INCOMPLETE')
  H.write(self.evidence/'INITIALIZATION_INSPECTION.json',inspection)
  active=H.parse(self.claim('--activate-controller',H.CONTROLLER,'--run-root',relative,'--expected-initialization',inspection['initialization_token']))
  H.need(active['status']=='BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS','INITIALIZATION_REFUSED');H.write(self.evidence/'ACTIVATION.json',active)
  current=self.claim('--current-controller',H.CONTROLLER).decode().strip().split('\t')
  H.need(len(current)==4 and current[:3]==[H.CONTROLLER,str(self.repo),str(self.run)],'ACTUAL_CONTROLLER_READBACK');self.claim_id=current[3]
  self.receipt=self.claim('--resume-controller',H.CONTROLLER,'--boundary','new-session','--epoch','G0001').decode().strip()
  self.currentness();H.write(self.evidence/'INITIAL_CURRENTNESS.json',{'receipt':self.receipt,'subject_head':self.head,'subject_tree':self.tree,'runtime_source_commit':request['source_commit'],'runtime_source_tree':H.SOURCE_TREE})
 def copy_fence(self):
  for path,(raw,mode,physical) in self.copied.items():
   pin,now,actual=H.pin(path,4*1024*1024,True);H.need(actual==raw and pin['mode']==mode and now==physical,'EXECUTING_SOURCE_CHANGED')
 def call(self,argv,expected=0):
  exact_receiver=[self.python,'-I','-B',str(HERE/'live_receiver.py'),'--work',str(self.work),'--go-sha256',self.go_sha]
  timeout=80 if list(map(str,argv))==exact_receiver else 45
  self.copy_fence();code,out,err=H.command(argv,self.repo,timeout=timeout,env=self.env);n=len(self.commands)+1
  H.write(self.evidence/('%03d.stdout'%n),out);H.write(self.evidence/('%03d.stderr'%n),err)
  self.commands.append({'argv':list(map(str,argv)),'returncode':code,'stdout_sha256':H.sha(out),'stderr_sha256':H.sha(err)})
  H.write(self.evidence/'COMMANDS.json',self.commands,replace=n>1)
  H.need(code==expected if expected is not None else code!=0,'ACTUAL_COMMAND_STATUS');self.copy_fence();return out
 def git(self,*args):return self.call([self.gitpath,*args])
 def claim(self,*args,expected=0):return self.call([self.bash,self.scripts/'claim-run.sh',*args],expected)
 def currentness(self):
  H.need(self.claim('--verify-resume-receipt',self.receipt).decode().strip()==self.receipt,'VERIFY_CURRENTNESS')
  H.need(self.claim('--require-current-continuity',H.CONTROLLER).decode().strip()==self.receipt,'REQUIRE_CURRENTNESS')
 def binding(self,mode,tid,owner,event,epoch,expected=None):
  argv=[self.python,self.scripts/'host-session-binding.py','--store',self.root/'host-store',mode,'--owner-id',owner,'--host-id','codex','--host-session-id',tid,'--controller-id',H.CONTROLLER,'--claim-id',self.claim_id,'--explicit-run-root',self.run,'--repository-identity',self.repo,'--git-common-directory-identity',self.repo/'.git','--worktree-identity',self.repo,'--activation-event-id',event,'--activation-receipt',self.receipt,'--continuity-generation',epoch,'--continuity-receipt',self.receipt]
  if expected:argv+=['--expected-generation',expected,'--reason','Actual fresh compact resume proof and mechanical currentness']
  value=H.parse(self.call(argv));H.write(self.evidence/('HOST_'+mode.upper()+'.json'),value)
  looked=H.parse(self.call([self.python,self.scripts/'host-session-binding.py','--store',self.root/'host-store','lookup','--host-id','codex','--host-session-id',tid]))
  H.need(looked['status']=='BOUND','HOST_NOT_BOUND');return looked['binding']['binding_generation']

def binary_copy(s):
 archive=next(r for r in s.manifest['members'] if r['key']=='official-binary-archive');directory=s.root/'binary';directory.mkdir(mode=0o700);binary=directory/'codex';seen=0
 state=H.parse(H.read(s.work/'HOST_STATE.json'));original=next(row for row in state['input_custody']['members'] if row['key']=='official-binary-archive')
 with os.fdopen(os.open(archive['path'],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as held:
  H.need(H.identity(os.fstat(held.fileno()))==original['identity'] and H.identity(Path(archive['path']).lstat())==original['identity'] and H.ancestors(Path(archive['path']).parent)==original['ancestors'],'OFFICIAL_ARCHIVE_PHYSICAL_CHANGED')
  with tarfile.open(fileobj=held,mode='r:gz') as tar:
   count=0
   for member in tar:
    count+=1;H.need(count<=256,'ARCHIVE_MEMBER_BOUND')
    if member.name!=H.BINARY_MEMBER:continue
    seen+=1;H.need(seen==1 and member.isfile() and member.size==H.BINARY_BYTES,'OFFICIAL_BINARY_MEMBER')
    with tar.extractfile(member) as source,binary.open('xb') as output:
     size=0
     while block:=source.read(1048576):size+=len(block);H.need(size<=H.BINARY_BYTES,'BINARY_COPY_BOUND');output.write(block)
     output.flush();os.fsync(output.fileno())
  H.need(H.identity(os.fstat(held.fileno()))==original['identity'] and H.identity(Path(archive['path']).lstat())==original['identity'] and H.ancestors(Path(archive['path']).parent)==original['ancestors'],'OFFICIAL_ARCHIVE_CHANGED_DURING_EXTRACTION')
 H.need(seen==1,'OFFICIAL_BINARY_ABSENT');binary.chmod(0o500);pin=H.source_pin(binary)
 H.need(pin['bytes']==H.BINARY_BYTES and pin['sha256']==H.BINARY_SHA,'OWNED_BINARY_PIN')
 H.need(s.call([binary,'--version']).decode().strip()=='codex-cli 0.166.0','NATIVE_VERSION');return binary

def canonical_open(s,pending,tid,owner,scope,binding_generation):
 state=pending.load(s.root/'host-store',tid);proof=state['observations'][scope[0]['id']]['proof'];digest=H.sha(pending.canonical(proof));event='codex-compact-v1-'+digest
 H.need(scope[0]['id']=='boundary-'+digest,'ACTUAL_BOUNDARY_DIGEST')
 invalidation=s.claim('--invalidate-continuity',H.CONTROLLER,'--boundary','host-reported-compaction','--event',event).decode().strip()
 s.claim('--require-current-continuity',H.CONTROLLER,expected=None)
 old_state=H.read(s.run/'STATE.md');old_roadmap=H.read(s.run/'ROADMAP.md')
 H.write(s.evidence/'POST_BOUNDARY_STATE_READ.md',old_state);H.write(s.evidence/'POST_BOUNDARY_ROADMAP_READ.md',old_roadmap)
 H.need(old_state.count(b'Current epoch: G0001')==1,'FRESH_EPOCH_PREIMAGE')
 timestamp=datetime.now(timezone.utc).isoformat()
 # Pure mechanical checkpoint of the real event. No substantive recovery,
 # acceptance or lifecycle completion is authored here.
 new_state=old_state.replace(b'Current epoch: G0001',b'Current epoch: G0002',1)
 anchor=b'| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|'
 H.need(new_state.count(anchor)==1,'EPOCH_TABLE_PREIMAGE')
 row=('\n| G0002 | host-reported-compaction | '+timestamp+' | actual source `'+s.head+'` / `'+s.tree+'` | yes | Mechanical currentness only; actual source proof '+digest+'; audit-state obligation remains pending |').encode()
 new_state=new_state.replace(anchor,anchor+row,1);H.write(s.run/'STATE.md',new_state,replace=True)
 H.need(H.read(s.run/'ROADMAP.md')==old_roadmap,'ROADMAP_CHANGED')
 s.receipt=s.claim('--resume-controller',H.CONTROLLER,'--boundary','host-reported-compaction','--epoch','G0002').decode().strip();s.currentness()
 generation=s.binding('rebind',tid,owner,event,'G0002',binding_generation)
 task=s.repo/'.task-tmp/h0';task.mkdir(parents=True,mode=0o700)
 capsule={'schema':'implementaudit.post-compaction-recovery.v2','event_id':event,'event_digest':'sha256:'+digest,'required_child':'audit-state','mechanical_governor_actions':['INVALIDATE','MECHANICAL_CURRENTNESS','OPEN_AUDIT_STATE'],'governor_substantive_reconstruction':False,'return_kind':'MINIMUM_APPLICABLE_FRONTIER','return_requires_governor_reconciliation':True,'stale_credit':False,'worker_context_disposition':'DISCARD_AFTER_RETURN'}
 capsule['capsule_digest']='sha256:'+H.sha(H.canonical(capsule));H.write(task/'CAPSULE.json',capsule);H.write(task/'ACTUAL_BOUNDARY.json',proof)
 argv=['route-trigger','STALE_CONTEXT_RECONSTRUCTION']
 inputs=[{'identity':'actual-boundary-proof','path':'.task-tmp/h0/ACTUAL_BOUNDARY.json','digest':'sha256:'+H.sha(H.read(task/'ACTUAL_BOUNDARY.json'))},{'identity':'post-compaction-recovery-capsule:'+event,'path':'.task-tmp/h0/CAPSULE.json','digest':'sha256:'+H.sha(H.read(task/'CAPSULE.json'))}]
 boundary={'kind':'host-reported-compaction','event_id':event}
 boundary['digest']='sha256:'+H.sha(H.canonical(boundary))
 current_scope={'identity':NEXT_ACTION}
 current_scope['digest']='sha256:'+H.sha(H.canonical(current_scope))
 action={'identity':'h0-seven-physical-occurrences','class':'REQUIRED_INTERNAL_CHILD','argv':argv}
 action['digest']='sha256:'+H.sha(H.canonical(action))
 request={'schema':'implementaudit.route-decision-request.v1','predicate_version':'R0033.route-predicate.v1','boundary':boundary,'scope':current_scope,'action':action,'inputs':sorted(inputs,key=lambda r:r['identity'])}
 H.write(task/'REQUEST.json',request)
 common=['--controller',H.CONTROLLER,'--store',s.root/'host-store','--host-id','codex','--host-session-id',tid,'--binding-generation',generation,'--request',task/'REQUEST.json','--requester-identity','governor']
 route=s.scripts/'route-transaction.py';decision=H.parse(s.call([s.python,route,'decide',*common,'--expected-record','none']))
 H.need(decision['decision']=='REQUIRED' and decision['route_state']=='UNSATISFIED','CANONICAL_REQUIRED_ABSENT')
 record=H.parse(s.git('cat-file','blob',decision['record_oid']))
 packet={'schema':'implementaudit.route-packet.v1','obligation_id':decision['obligation_id'],'route_transaction_id':decision['route_transaction_id'],'target_identity':'audit-state','source_event':{'schema':'implementaudit.source-event.v1','source_identity':event,'provenance':{'schema':'implementaudit.source-event-provenance.v1','event_id':event,'host_correlation_id':record['host_correlation_id']},'body':'One actual fresh source-bound mechanical qualification. The actual compact/resume proof is '+digest+'. Seven real LOAD/DELIVER/BIND occurrences are required; no RETURN/JOIN, cognition or original award is asserted.','kind':'one-shot-action','reactivation':{'reopen':False,'target_changed':False,'invalidating_evidence':False}}}
 H.write(task/'PACKET.json',packet)
 opened=H.parse(s.call([s.python,route,'open',*common,'--expected-record',decision['record_oid'],'--packet',task/'PACKET.json','--logical-task','h0-mechanical-prior-'+s.request['run_id']]))
 H.need(opened['status']=='CHILD_OPEN' and opened['route_state']=='OPEN','CANONICAL_OPEN_ABSENT')
 H.write(s.evidence/'CANONICAL_OPEN.json',opened);H.write(s.evidence/'BOUNDARY_CURRENTNESS.json',{'invalidation':invalidation,'event':event,'scope':scope,'receipt':s.receipt,'binding_generation':generation})
 return generation

def execute(work,request,manifest,go_sha):
 grant(work,request,go_sha);progress=H.Progress(work,request,go_sha);s=None;native=provider=None;result={'status':'INCOMPLETE','authority':'NONE','original_acceptance':False,'public_return':None,'public_join':None};failure=None
 try:
  s=Subject(work,request,manifest,go_sha);progress.mark('INITIALIZATION',True)
  progress.mark('BINARY_COPY');binary=binary_copy(s);progress.mark('BINARY_COPY',True);source=H.load(s.scripts/'compaction-source-owner-codex-app.py','h0_initial_source');pending=H.load(s.scripts/'compaction-audit-pending.py','h0_pending')
  progress.mark('PROVIDER_START');provider=H.load(HERE/'provider.py','h0_provider').Provider(s.root/'provider');progress.mark('PROVIDER_START',True);home=s.root/'home';home.mkdir(mode=0o700)
  config='model = "dg18-emulated-model"\nmodel_provider = "h0_mechanical"\nmodel_context_window = 258400\n[projects.'+json.dumps(str(s.repo))+']\ntrust_level = "trusted"\n[features]\nhooks = false\napps = false\nmulti_agent = true\n[model_providers.h0_mechanical]\nname = "Explicit deterministic H0 transport, no inference"\nbase_url = '+json.dumps(provider.url)+'\nwire_api = "responses"\nrequires_openai_auth = false\nrequest_max_retries = 0\nstream_max_retries = 0\n[mcp_servers.dg18prior]\ncommand = '+json.dumps(s.python)+'\nargs = ['+json.dumps(str(s.scripts/'compaction-prior-mcp.py'))+', "--source-owner", '+json.dumps(str(s.scripts/'compaction-source-owner-codex-app.py'))+']\n'
  H.write(home/'config.toml',config.encode());progress.mark('NATIVE_START');native=H.load(HERE/'native_transport.py','h0_native').Native(binary,home,s.repo,s.root/'native')
  progress.mark('NATIVE_START',True);progress.mark('NATIVE_INITIALIZE')
  native.rpc('initialize',{'clientInfo':{'name':'h0_prior_mechanical','version':'r5'},'capabilities':{'experimentalApi':True}});native.send({'method':'initialized','params':{}})
  progress.mark('NATIVE_INITIALIZE',True);progress.mark('ROOT_THREAD')
  thread=native.rpc('thread/start',{'cwd':str(s.repo),'model':'dg18-emulated-model','modelProvider':'h0_mechanical','approvalPolicy':'never','sandbox':'read-only','environments':[],'ephemeral':False});tid=thread['thread']['id'];rollout=Path(thread['thread']['path'])
  progress.mark('ROOT_THREAD',True)
  def turn(text):
   provider.arm({'text':text});native.rpc('turn/start',{'threadId':tid,'input':[{'type':'text','text':text}]});terminal,_=native.wait_turn(tid);H.need(terminal['params']['turn']['status']=='completed','ACTUAL_NATIVE_TURN_INCOMPLETE')
  progress.mark('SEED_TURN');turn('Seed the necessary fresh H0 source. All provider text and usage are explicitly emulated.')
  progress.mark('SEED_TURN',True);progress.mark('NECESSARY_COMPACTION')
  provider.arm({'text':'Mechanical summary for this one genuine native compact operation; no prior evidence is replaced.'});native.rpc('thread/compact/start',{'threadId':tid});terminal,_=native.wait_turn(tid);H.need(terminal['params']['turn']['status']=='completed','ACTUAL_COMPACTION_INCOMPLETE')
  progress.mark('NECESSARY_COMPACTION',True);progress.mark('RESUMED_TURN');turn('Resume after the actual fresh boundary; prior archive and old pending facts remain untouched.')
  progress.mark('RESUMED_TURN',True);fence=native.rpc('thread/read',{'threadId':tid,'includeTurns':False});H.write(s.evidence/'NATIVE_THREAD_FENCE.json',fence)
  progress.mark('HOST_BINDING');owner='dg18-isolated-h0-physical-store-20261106-05';store=s.root/'host-store';s.call([s.python,s.scripts/'host-session-binding.py','--store',store,'init','--owner-id',owner])
  generation=s.binding('bind',tid,owner,'dg18-isolated-h0-source-activation-20261106-05','G0001')
  progress.mark('HOST_BINDING',True);progress.mark('MECHANICAL_SELECTION')
  process=source.fresh_canary_process_identity_v1(native.proc);physical=rollout.stat();raw=H.read(rollout,8*1024*1024)
  capture={'schema':'implementaudit.fresh-native-live-canary-capture.v1','thread_id':tid,'native_version':'codex-cli 0.166.0','native_executable_sha256':H.BINARY_SHA,'pid':native.proc.pid,'proc_start_ticks':process['proc_start_ticks'],'proc_host_pid':process['host_pid'],'argv':native.argv,'cwd':str(s.repo),'codex_home':str(home),'source':{'path':str(rollout),'bytes':len(raw),'sha256':H.sha(raw),'physical':{'device':physical.st_dev,'inode':physical.st_ino}},'capture_script_sha256':H.sha(H.read(Path(__file__))), 'usage_origin':'DETERMINISTIC_LOCAL_RESPONSES_EMULATION','authority_ceiling':'NONE'}
  H.write(s.root/'LIVE_CAPTURE.json',capture)
  selected={'schema':'implementaudit.codex0166-mechanical-selection.v1','profile_id':'codex-app-server-0.166.0-linux-prior-mechanical-v1','root_thread_id':tid,'root_agent_path':'/root','root_source':str(rollout),'session_root':str(home/'sessions'),'cwd':str(s.repo),'cli_version':'0.166.0','native_version':'codex-cli 0.166.0','native_executable':H.source_pin(binary),'codex_home':str(home),'runtime_helpers':{name:H.source_pin(s.scripts/name) for name in ('bounded_native_reader.py','bounded_source_owner.py','bounded_file_custody.py')},'episode_owner':{'module_pin':H.source_pin(s.scripts/'route-transaction.py'),'repository':str(s.repo),'controller':H.CONTROLLER},'pending_owner':{'store':str(store),'session_id':tid,'owner_id':owner},'producer_capture_pin':H.source_pin(s.root/'LIVE_CAPTURE.json'),'capture_producer_pin':H.source_pin(Path(__file__)),'tool_evidence_contract':'ACTUAL_NATIVE_MCP_PRIOR_ONLY_EMULATED_PROVIDER_V1','mechanical_tool':{'server_pin':H.source_pin(s.scripts/'compaction-prior-mcp.py'),'protocol_pin':H.source_pin(s.scripts/'compaction-prior-protocol.py'),'config_pin':H.source_pin(home/'config.toml'),'python_pin':H.source_pin(s.python)}}
  H.write(s.root/'SOURCE_SELECTION.json',selected);selection_pin=H.source_pin(s.root/'SOURCE_SELECTION.json');target=s.scripts/'compaction-source-owner-codex-app.py';template=H.read(target)
  H.need(H.sha(template)=='5bb21eed89945a8da97857f980b1f85a06dc07df47b25475b9173f23e82ce8f8' and template.count(b'MECHANICAL_SELECTION_PIN = None')==1,'EXACT_MECHANICAL_TEMPLATE')
  bound=template.replace(b'MECHANICAL_SELECTION_PIN = None',b'MECHANICAL_SELECTION_PIN = '+repr(selection_pin).encode(),1);H.write(target,bound,replace=True,mode=s.copied[str(target)][1]);s.copied[str(target)]=(bound,s.copied[str(target)][1],H.pin(target,4*1024*1024)[1]);source.MECHANICAL_SELECTION_PIN=selection_pin
  progress.mark('MECHANICAL_SELECTION',True);progress.mark('PHYSICAL_REGISTRATION')
  raw=H.read(rollout,8*1024*1024);registered=pending.operate(store,tid,owner,'register-source',{'task_id':tid,'transcript':str(rollout),'expected_bytes':len(raw),'expected_sha256':H.sha(raw)})
  state=pending.load(store,tid);scope=pending.available_scope(state)
  H.need(state['source_problem'] is None and len(scope)==1 and scope[0]['kind']=='COMPLETED_RESUMED_BOUNDARY' and not state['assignments'],'ONE_GENUINE_AVAILABLE_SCOPE_REQUIRED')
  H.write(s.evidence/'REGISTERED.json',registered);progress.mark('PHYSICAL_REGISTRATION',True);progress.mark('CANONICAL_OPEN');generation=canonical_open(s,pending,tid,owner,scope,generation)
  progress.mark('CANONICAL_OPEN',True);H.write(s.evidence/'RUNTIME_CUSTODY.json',{path:physical for path,(_,_,physical) in s.copied.items()})
  s.currentness();prepared(work);s.copy_fence();H.need(native.proc.poll() is None,'NATIVE_NOT_LIVE')
  mechanical=H.load(HERE/'mechanical_driver.py','h0_mechanical_driver');result['mechanical']=mechanical.run_existing(native=native,provider=provider,pending=pending,source=source,scope=scope,evidence_directory=s.evidence,progress=progress.mark,diagnostic=progress.observe_mcp_failure)
  # The original selected-occurrences reader is invoked again in a distinct
  # receiving process while this same native process and source files remain live.
  s.copy_fence();s.currentness();H.need(source.fresh_canary_process_identity_v1(native.proc)==process,'LIVE_NATIVE_IDENTITY_CHANGED')
  progress.mark('LIVE_RECEIVING');s.call([s.python,'-I','-B',HERE/'live_receiver.py','--work',work,'--go-sha256',go_sha])
  received=H.parse(H.read(s.evidence/'MECHANICAL_RECEIVING.json'));H.need(received['status']=='EXISTING_READER_SEVEN_OCCURRENCES_RECEIVED','LIVE_RECEIVING_ABSENT')
  progress.mark('LIVE_RECEIVING',True);progress.mark('FINAL_CURRENTNESS');s.currentness();prepared(work);H.need(native.proc.poll() is None,'NATIVE_ENDED_BEFORE_RECEIVING');progress.mark('FINAL_CURRENTNESS',True);result['receiving']=received;result['status']='MECHANICAL_RECEIVED_PENDING_ROOT_RECONCILIATION'
 except BaseException as exc:
  failure=exc;progress.fail(exc);H.write(work/'PRIVATE_FAILURE.txt',traceback.format_exc().encode());result['failure_type']=type(exc).__name__
 finally:
  if native:
   progress.mark('NATIVE_CLEANUP')
   try:
    result['native_cleanup']=native.close()
    if result['native_cleanup']['direct_child_exited'] and result['native_cleanup']['readers_joined']:progress.mark('NATIVE_CLEANUP',True)
    else:progress.fail(H.Refusal('NATIVE_CLEANUP_REFUSED'))
   except BaseException as exc:result['native_cleanup']={'direct_child_exited':False,'cleanup_error_type':type(exc).__name__};progress.fail(exc,'NATIVE_CLEANUP_REFUSED')
  if provider:
   progress.mark('PROVIDER_CLEANUP')
   try:
    result['provider_cleanup']=provider.close()
    if result['provider_cleanup']['listener_closed'] and result['provider_cleanup']['handlers_joined']:progress.mark('PROVIDER_CLEANUP',True)
    else:progress.fail(H.Refusal('PROVIDER_CLEANUP_REFUSED'))
   except BaseException as exc:result['provider_cleanup']={'listener_closed':False,'cleanup_error_type':type(exc).__name__};progress.fail(exc,'PROVIDER_CLEANUP_REFUSED')
  if s is not None:
   try:
    collection=H.load(HERE/'h0_result_collection.py','h0_result_collection')
    result['owner_observations']=collection.retain_for_subject(s,H)
   except BaseException as exc:
    result['owner_observations']={'status':'COLLECTION_REFUSED','effect':'UNKNOWN','authority':'NONE'}
    progress.fail(H.Refusal('H0_OWNER_OBSERVATION_REFUSED'))
    if failure is None:failure=exc
  H.write(work/'NATIVE_RESULT.json',result)
  if s is not None:H.write(s.evidence/'RESULT.json',result)
 H.need(failure is None,'MECHANICAL_OPERATION_FAILED')
 H.need(result['native_cleanup']['direct_child_exited'] and result['native_cleanup']['readers_joined'] and result['provider_cleanup']['listener_closed'] and result['provider_cleanup']['handlers_joined'],'LOCAL_CLEANUP_UNCERTAIN')
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--prepare-check',action='store_true');p.add_argument('--execute',action='store_true');p.add_argument('--go-sha256');a=p.parse_args()
 H.need(a.prepare_check!=a.execute,'ONE_MODE_REQUIRED');work=a.work;H.need(work.is_absolute() and work.resolve(strict=True)==work,'WORK_PATH')
 request,manifest,state=prepared(work)
 if a.prepare_check:print('{"status":"PURE_PREPARATION_CHECK_PASS","authority":"NONE"}');return
 H.need((work/'DISPATCH_RESERVED.json').is_file(),'ONE_SHOT_DISPATCH_RESERVATION_REQUIRED')
 resource.setrlimit(resource.RLIMIT_FSIZE,(H.BINARY_BYTES,H.BINARY_BYTES));os.umask(0o077)
 execute(work,request,manifest,a.go_sha256);print('{"status":"MECHANICAL_RECEIVED_PENDING_ROOT_RECONCILIATION","authority":"NONE"}')
if __name__=='__main__':
 try:main()
 except BaseException:print('{"status":"H0_NATIVE_DRIVER_REFUSED","authority":"NONE"}');raise SystemExit(1)
