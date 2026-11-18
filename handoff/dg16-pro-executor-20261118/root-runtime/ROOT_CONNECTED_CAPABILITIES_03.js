/* Actual Root-issued, single-smoke capabilities. Evaluate only in functions.exec
 * with the real tools object after verifying this file and the Root policy.
 * This is not a reusable admission for the original protected G132 operation.
 */
(({tools, codec, setup, policy, policyPin}) => {
  const need=(v,c)=>{if(!v)throw Error(c);};
  const same=(a,b)=>codec.canonical(a)===codec.canonical(b);
  const quote=s=>"'"+s.replace(/'/g,"'\\''")+"'";
  const cfg=codec.strict(setup.configuration.raw);
  const SCOPE='SYNTHETIC_TRANSPORT_ONLY_NO_ORIGINAL_INPUTS';
  const roles=new Set(), permits=new Map(); let decisionIssued=false;
  const hostReceipts=[];
  need(policy.decision==='AUTHORIZE_ONE_CURRENT_NONPROTECTED_G132_TRANSPORT_SMOKE'
    &&policy.root===cfg.root&&policy.branch===cfg.branch&&policy.parent_sha===cfg.parent_sha
    &&policy.controller===cfg.spec.actor.controller&&policy.continuity_receipt===cfg.spec.actor.continuity_receipt
    &&cfg.spec.actor.assignment_ref===policyPin.path
    &&policy.fixture_scope===SCOPE&&policy.protected_operation==='UNCHANGED_UNKNOWN_NO_REPLAY'
    &&policy.original_effect_grant===false&&cfg.fixture_scope===SCOPE,'EXACT_ACTUAL_ROOT_ASSIGNMENT');
  const writeSource=`import hashlib,json,os,pathlib,sys
p=pathlib.Path(sys.argv[1]); b=sys.argv[2].encode('utf-8')
assert p.is_absolute() and p.parent.resolve(strict=True)==p.parent and not os.path.lexists(p)
fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
with os.fdopen(fd,'wb') as f: f.write(b); f.flush(); os.fsync(f.fileno())
assert p.read_bytes()==b
print(json.dumps({'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()},sort_keys=True))`;
  const checkSource=`import hashlib,json,os,pathlib,stat,subprocess,sys,time
v=json.loads(sys.argv[1]); root=pathlib.Path(v['root']); folder=root/'operator-journal'/v['key']
assert root.resolve(strict=True)==root and root.stat().st_uid==os.geteuid()==1000 and stat.S_IMODE(root.stat().st_mode)==0o700
for name,pin in [('SMOKE_CONFIGURATION.json',v['configuration_sha256'])]:
 p=root/name; assert p.resolve(strict=True)==p and p.is_file() and p.stat().st_uid==1000 and p.stat().st_nlink==1
 assert hashlib.sha256(p.read_bytes()).hexdigest()==pin
p=pathlib.Path(v['policy_path']); assert p.resolve(strict=True)==p and p.stat().st_uid==1000 and p.stat().st_nlink==1
assert hashlib.sha256(p.read_bytes()).hexdigest()==v['policy_sha256']
r=subprocess.run(['bash','/home/agent/.codex/skills/remote-skills/skill-6a85962852788191bb717a1a61592b58/scripts/claim-run.sh','--require-current-continuity',v['controller']],cwd=v['repo'],capture_output=True,text=True,timeout=10)
assert r.returncode==0 and r.stdout.strip()==v['continuity_receipt'] and not r.stderr
if v['action']['kind']=='open': assert not os.path.lexists(folder)
else:
 assert folder.resolve(strict=True)==folder and folder.stat().st_uid==1000 and stat.S_IMODE(folder.stat().st_mode)==0o700
 assert not os.path.lexists(folder/'UNKNOWN.json') and not os.path.lexists(folder/'FINISH.json')
 start=json.loads((folder/'START.json').read_bytes()); assert start['key']==v['key'] and start['scope_sha256']==v['scope_sha256']
 assert start['authorization']=={'ref':v['policy_path'],'sha256':v['policy_sha256']}
now=time.time_ns()//1000000; assert now<v['expires_ms']
record={'schema':'dg16.actual-root-currentness-and-no-replay-observation.v1','observed_ms':now,'role':v['role'],'key':v['key'],'scope_sha256':v['scope_sha256'],'action_sha256':v['action_sha256'],'continuity_receipt':r.stdout.strip(),'journal_subject':'ABSENT_BEFORE_OPEN' if v['action']['kind']=='open' else 'ACTIVE_NOT_TERMINAL_NOT_UNKNOWN','original_effect_grant':False}
raw=(json.dumps(record,sort_keys=True,separators=(',',':'))+'\\n').encode()
p=root/'ROOT_CURRENTNESS_OBSERVATIONS.jsonl'; fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
with os.fdopen(fd,'ab') as f: assert f.tell()<1048576; f.write(raw); f.flush(); os.fsync(f.fileno())
print(json.dumps(record,sort_keys=True,separators=(',',':')))`;
  async function runPython(source,args){
    const cmd=['/usr/bin/python3','-I','-B','-c',source,...args].map(quote).join(' ');
    const receipt={sequence:hostReceipts.length,command_sha256:codec.descriptor(cmd).sha256,
      started_ms:Date.now(),returns:[],command_reinvoked:false};
    hostReceipts.push(receipt);
    const deadline=Math.min(cfg.spec.expires_ms,Date.now()+15000);
    try{
      need(Date.now()<deadline,'ACTUAL_ROOT_HOST_DEADLINE');
      let r=await tools.exec_command({cmd,workdir:policy.repo,login:false,shell:'/bin/bash',yield_time_ms:1000,max_output_tokens:1500});
      let output='',session=r.session_id;
      for(;;){
        receipt.returns.push({observed_ms:Date.now(),actual:r});
        need(typeof r.output==='string','ACTUAL_ROOT_HOST_OUTPUT_REQUIRED');
        output+=r.output;need(output.length<=16384&&!output.includes('Warning: truncated output'),'ACTUAL_ROOT_HOST_OUTPUT_BOUND');
        need(r.session_id===undefined||r.session_id===session,'ACTUAL_ROOT_HOST_SESSION_CHANGED');
        if(r.exit_code!==undefined)break;
        need(Number.isSafeInteger(session)&&Date.now()<deadline,'ACTUAL_ROOT_HOST_WAIT_REFUSED');
        r=await tools.write_stdin({session_id:session,chars:'',yield_time_ms:1000,max_output_tokens:1500});
      }
      need(r.exit_code===0&&Date.now()<deadline,'ACTUAL_ROOT_HOST_CHECK_OR_RECORD_REFUSED');
      const value=codec.strict(output.trim());receipt.terminal_received_ms=Date.now();return value;
    }catch(error){receipt.refusal=String(error).slice(0,500);throw error;}
  }
  async function save(name,value){
    need(/^[A-Z0-9_.-]+\.json$/.test(name),'ROOT_RECORD_NAME');
    const raw=typeof value==='string'?value:codec.canonical(value)+'\n';
    const d=await runPython(writeSource,[cfg.root+'/'+name,raw]);
    need(same(d,codec.descriptor(raw)),'ROOT_RECORD_ACTUAL_READBACK'); return d;
  }
  async function admit(scope){
    const s=scope.spec, role=s.role;
    need(['public-observation','sender','smoke-branch','publication','g3'].includes(role)
      &&!roles.has(role)&&scope.automatic_retry===false&&scope.original_acceptance===false
      &&scope.journal_root===cfg.root+'/operator-journal'
      &&same(scope.transport_source,{path:setup.linux.helper_path,sha256:setup.linux.helper_sha256})
      &&scope.host_identity.native_model_identity==='NOT_OBSERVED','ONE_ACTUAL_SMOKE_ROLE');
    const h=scope.host_identity.stable;
    need(h.platform==='linux'&&h.uid===1000&&h.euid===1000&&h.gid===1000&&h.egid===1000
      &&h.journal_root===scope.journal_root,'OBSERVED_NONROOT_PHYSICAL_IDENTITY');
    const common={...cfg.spec,role};
    if(role==='sender')common.fixture_scope=SCOPE;
    if(role==='smoke-branch')common.smoke={scope:SCOPE,branch:cfg.branch,parent_sha:cfg.parent_sha};
    if(role==='publication'){
      need(/^[0-9a-f]{40}$/.test(s.publication?.parent_sha),'ACTUAL_PREPARED_SMOKE_PARENT');
      common.publication={kind:'CONTROL_DATA_ONLY',branch:cfg.branch,parent_sha:s.publication.parent_sha,
        writes:5,reads:6,paths:['CONTROL.json','INPUTS.cms']};
    }
    if(role==='g3')common.stage='components';
    need(same(s,common)&&Date.now()<s.expires_ms,'EXACT_REVIEWED_ROLE_SCOPE');
    const frozen=codec.canonical(scope),scopeHash=codec.descriptor(frozen).sha256;
    const key=codec.descriptor(codec.canonical({context:s.context,role,stage:s.stage||null})).sha256;
    roles.add(role); let observation=null;
    const permit={authorization:{ref:policyPin.path,sha256:policyPin.sha256},
      assertCurrent:async({scope:actual,action})=>{
        need(codec.canonical(actual)===frozen,'ROOT_SCOPE_CHANGED');
        const actionHash=codec.descriptor(codec.canonical(action)).sha256;
        observation=await runPython(checkSource,[codec.canonical({root:cfg.root,repo:policy.repo,key,role,
          controller:policy.controller,continuity_receipt:policy.continuity_receipt,
          configuration_sha256:setup.configuration.sha256,policy_path:policyPin.path,policy_sha256:policyPin.sha256,
          scope_sha256:scopeHash,action,action_sha256:actionHash,expires_ms:s.expires_ms})]);
        need(observation.continuity_receipt===policy.continuity_receipt&&observation.action_sha256===actionHash
          &&observation.scope_sha256===scopeHash&&observation.original_effect_grant===false,'ACTUAL_CURRENTNESS_RECEIVING');
        return true;
      },
      assertNoReplay:async({scope:actual,action})=>{
        need(codec.canonical(actual)===frozen&&observation
          &&observation.action_sha256===codec.descriptor(codec.canonical(action)).sha256
          &&Date.now()-observation.observed_ms>=0&&Date.now()-observation.observed_ms<2000
          &&['ABSENT_BEFORE_OPEN','ACTIVE_NOT_TERMINAL_NOT_UNKNOWN'].includes(observation.journal_subject)
          &&observation.original_effect_grant===false,'ACTUAL_NO_REPLAY_OBSERVATION_REQUIRED');
        return true;
      }};
    await save('ROOT_ADMISSION_'+role.toUpperCase()+'.json',{schema:'dg16.actual-root-smoke-role-admission.v1',
      issuer:'/root',issued_ms:Date.now(),authorization:permit.authorization,scope,scope_sha256:scopeHash,
      authority_scope:SCOPE,native_issuer_authentication:false,protected_operation:'UNCHANGED_UNKNOWN_NO_REPLAY'});
    permits.set(role,permit); return permit;
  }
  async function decide(value){
    need(!decisionIssued&&value.fixture_scope===SCOPE&&value.original_effect_grant===false
      &&value.request.fixture_scope===SCOPE&&value.request.proposal_is_issued_decision===false,'ACTUAL_SYNTHETIC_ROOT_DECISION_ONLY');
    const req=codec.strict(value.request.raw),digest=codec.descriptor('G132 SYNTHETIC: NO NATIVE OBSERVATION').sha256;
    need(value.requestBinding.request_sha256===codec.descriptor(value.request.raw).sha256
      &&value.request.source.sha256==='b85cca1550ff8e7c1c89778180e53a5c70f306f0c8725ba60ef3ccd4bbc3a6ad'
      &&req.schema==='dg16.g3-root-consumption-request.v2'&&req.authority==='NONE'
      &&req.source_commit==='e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'
      &&req.source_tree==='ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7'
      &&req.source_parent==='8c393aa0d415e3bb4f25d333316b3abaf498e5af'
      &&req.run_id===cfg.spec.context.run_id&&req.attempt===1&&req.nonce===digest.slice(0,32)
      &&req.control_branch==='pro/dg16-g1-g3-control-32-20261114'
      &&req.control_path==='qualification/dg16-r5-g3/ROOT_DECISION.json'
      &&req.root==='R5_ROOT'&&req.join==='DG16_COMPONENT_JOIN'
      &&req.original_scope_sha256==='8c08f2aecd34f582f3662b5bc83b3d3a27cee33d2f17711ced868a1d7b11c96a'
      &&req.original_total===157&&req.original_awards===0
      &&same(req.returned_nodes,['G1_ORIGINAL_PAIR','HOST_SCOPE_RECEIVING'])
      &&req.decision_before==='WAITING_FOR_G1_AND_HOST_SCOPE'
      &&req.decision_after==='SCOPED_RETURNS_RETAINED_ORIGINAL_CELL_OPEN'
      &&req.full_g2==='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST'
      &&req.status==='ROOT_REQUEST_READY'&&Date.now()<req.expires_unix_ms
      &&req.shared_expires_unix_ms<=cfg.spec.expires_ms,'ROOT_INSPECTED_EXACT_SYNTHETIC_REQUEST');
    for(const k of ['graph_sha256','dispatch_sha256','transition_sha256','join_sha256','scope_return_sha256','g1_return_sha256','complete_input_key'])
      need(req[k]===digest,'NO_SYNTHETIC_TO_NATIVE_DIGEST_SUBSTITUTION');
    const action={kind:'actual-root-one-time-fixture-decision'},permit=permits.get('g3');
    need(permit,'ACTUAL_G3_ROLE_ADMISSION');
    await permit.assertCurrent({scope:value.scope,action});
    await permit.assertNoReplay({scope:value.scope,action});
    decisionIssued=true;
    const decision={schema:'dg16.g3-root-consumption-decision.v2',issuer:'R5_ROOT_GOVERNOR',
      successor:'PRO-EXECUTOR-01, designated by owner',action:'CONSUME_COMPONENT_RETURNS_ONLY',
      request_sha256:value.requestBinding.request_sha256,
      outputs:{G1_ORIGINAL_PAIR:digest,HOST_SCOPE_RECEIVING:digest},
      consumed_nodes:['G1_ORIGINAL_PAIR','HOST_SCOPE_RECEIVING'],
      owner_arrangement:'SELECTIVE_PARALLEL_EXISTING_OWNERS_DG16_SOLE_SHARED_WRITER',
      original_awards:0,issued_unix_ms:Date.now()};
    for(const k of ['run_id','attempt','nonce','source_commit','source_tree','graph_sha256','dispatch_sha256','join_sha256',
      'decision_before','decision_after','full_g2','expires_unix_ms'])decision[k]=req[k];
    const raw=codec.canonical(decision)+'\n';
    await save('ROOT_ACTUAL_REQUEST.json',value.request.raw);
    const desc=await save('ROOT_ACTUAL_DECISION.json',raw);
    await save('ROOT_ACTUAL_DECISION_ISSUANCE.json',{schema:'dg16.actual-root-synthetic-decision-issuance.v1',
      issuer:'/root',issued_ms:Date.now(),continuity_receipt:policy.continuity_receipt,authorization:permit.authorization,
      request_sha256:value.requestBinding.request_sha256,decision:desc,scope_sha256:codec.descriptor(codec.canonical(value.scope)).sha256,
      decision_proposal_adopted:false,decision_constructed_from_independently_inspected_request:true,
      fixture_scope:SCOPE,original_effect_grant:false,native_history_authenticated:false,
      schema_issuer_label_is_not_native_identity:true,protected_operation:'UNCHANGED_UNKNOWN_NO_REPLAY'});
    return {raw};
  }
  return Object.freeze({admit,decide,hostDiagnostics:()=>codec.strict(codec.canonical(hostReceipts))});
})
