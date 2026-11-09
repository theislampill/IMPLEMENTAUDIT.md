/* Root-invoked V8 control callback. No global start, tool call or admission.
 * Load the separately received frozen f668 WindowsRoleIO; do not replace it.
 * Actual Root source/config/body/admission/history rights remain external.
 */
const CONTROL_REPO='theislampill/IMPLEMENTAUDIT.md';
const CONTROL_API='https://api.github.com/repos/'+CONTROL_REPO;
const CONTROL_TOOLS=Object.freeze({fetch:'mcp__codex_apps__github_fetch',file:'mcp__codex_apps__github_fetch_file',tree:'mcp__codex_apps__github_create_tree',commit:'mcp__codex_apps__github_create_commit',ref:'mcp__codex_apps__github_update_ref'});
function controlNeed(v,c){if(!v)throw Error(c);}
function exactKeys(v,names){return v&&typeof v==='object'&&!Array.isArray(v)&&Object.keys(v).sort().join(',')===[...names].sort().join(',');}
function hex40(v){return typeof v==='string'&&/^[0-9a-f]{40}$/.test(v);}
function utf8(s){const out=[];for(const ch of s){let c=ch.codePointAt(0);if(c>=0xd800&&c<=0xdfff)c=0xfffd;if(c<128)out.push(c);else if(c<2048)out.push(192|(c>>>6),128|(c&63));else if(c<65536)out.push(224|(c>>>12),128|((c>>>6)&63),128|(c&63));else out.push(240|(c>>>18),128|((c>>>12)&63),128|((c>>>6)&63),128|(c&63));}return out;}
// Git object identity only: pure bytes, no Git process/key/provider boundary.
function sha1(input){let bytes=input.slice(),bits=bytes.length*8;bytes.push(128);while(bytes.length%64!==56)bytes.push(0);for(let i=7;i>=0;i--)bytes.push(i>=4?0:(bits>>>((i%4)*8))&255);let h=[0x67452301,0xefcdab89,0x98badcfe,0x10325476,0xc3d2e1f0];const rol=(x,n)=>((x<<n)|(x>>>(32-n)))>>>0;for(let off=0;off<bytes.length;off+=64){const w=new Array(80);for(let i=0;i<16;i++)w[i]=((bytes[off+4*i]<<24)|(bytes[off+4*i+1]<<16)|(bytes[off+4*i+2]<<8)|bytes[off+4*i+3])>>>0;for(let i=16;i<80;i++)w[i]=rol(w[i-3]^w[i-8]^w[i-14]^w[i-16],1);let[a,b,c,d,e]=h;for(let i=0;i<80;i++){let f,k;if(i<20){f=(b&c)|(~b&d);k=0x5a827999;}else if(i<40){f=b^c^d;k=0x6ed9eba1;}else if(i<60){f=(b&c)|(b&d)|(c&d);k=0x8f1bbcdc;}else{f=b^c^d;k=0xca62c1d6;}const t=(rol(a,5)+f+e+k+w[i])>>>0;e=d;d=c;c=rol(b,30);b=a;a=t;}h=h.map((v,i)=>(v+[a,b,c,d,e][i])>>>0);}return h.map(v=>v.toString(16).padStart(8,'0')).join('');}
function blobId(content){const body=utf8(content);return sha1([...utf8('blob '+body.length+'\0'),...body]);}
function inertOneLeafTree(path,content){const raw=[...utf8('100644 '+path+'\0'),...blobId(content).match(/../g).map(x=>parseInt(x,16))];return sha1([...utf8('tree '+raw.length+'\0'),...raw]);}
function rootResultSha(actual){controlNeed(actual&&actual.isError===false&&actual.structuredContent&&hex40(actual.structuredContent.sha),'ACTUAL_WRITE_SHA_REQUIRED');return actual.structuredContent.sha;}

function makeControlRoleIO(WindowsRoleIO){
  controlNeed(typeof WindowsRoleIO==='function','EXACT_RECEIVED_WINDOWS_ROLE_IO_REQUIRED');
  return class ControlRoleIO extends WindowsRoleIO{
    async nextIntent(){
      await this._until(()=>this.controlPending===''&&
        ((this.echoReady&&this.events.some(e=>e.event==='intent'))||this.events.some(e=>e.event==='complete')),true);
      const i=this.events.findIndex(e=>e.event==='intent'||e.event==='complete');controlNeed(i>=0,'CONTROL_EVENT_REQUIRED');
      const event=this.events[i];if(event.event==='complete')return {complete:true};
      controlNeed(!this.terminal&&this.echoReady,'LIVE_OWNED_ROLE_BEFORE_CONTROL');
      this.events.splice(i,1);return {intent:event.intent};
    }
    async retainReturned(kind,actual){
      // Receipt-only handoff of an ALREADY returned actual outcome. No new
      // provider operation/deadline/grace. Existing Python journal qualifies
      // currentness only after safe retention; descriptor survives refusal.
      controlNeed(this.echoReady&&Number.isSafeInteger(this.session)&&this.session>0&&!this.terminal&&this.controlPending==='','OWNED_RETURNED_OUTCOME_FRAME_UNAVAILABLE');
      const raw=JSON.stringify(actual),length=utf8(raw).length;controlNeed(length>0&&length<=4194304,'FULL_RETURNED_OUTCOME_BOUND');
      this.echoReady=false;
      this._accept(await this.tools.write_stdin({session_id:this.session,chars:String(length)+'\n'+raw,yield_time_ms:1000,max_output_tokens:5000}));
      await this._until(()=>this.events.some(e=>e.event==='retained'),true);
      const i=this.events.findIndex(e=>e.event==='retained');controlNeed(this.events.splice(i,1)[0].kind===kind,'RETURNED_OUTCOME_ORDINAL');
    }
    async receive(){
      await this._until(()=>this.controlPending===''&&this.terminal&&this.last===0&&this.events.some(e=>e.event==='complete'),true);
      return this.events.find(e=>e.event==='complete').receipt;
    }
  };
}

// Trusted plan is separately Root-authenticated raw R.encode bytes, NEVER a TTY event.
function canonical(value){
  if(value===null||typeof value==='boolean')return JSON.stringify(value);
  if(typeof value==='string')return JSON.stringify(value).replace(/[\u0080-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));
  if(typeof value==='number'){controlNeed(Number.isSafeInteger(value),'PLAN_INTEGER');return String(value);}
  if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
  controlNeed(value&&Object.getPrototypeOf(value)===Object.prototype,'PLAN_OBJECT');
  return '{'+Object.keys(value).sort().map(k=>canonical(k)+':'+canonical(value[k])).join(',')+'}';
}
function fixedTree(files){
  const root={};for(const [path,row] of Object.entries(files)){let node=root;const parts=path.split('/');for(const p of parts.slice(0,-1))node=node[p]||(node[p]={});node[parts[parts.length-1]]=row.body_utf8;}
  function digest(node){const rows=Object.keys(node).map(name=>{const dir=typeof node[name]!=='string',h=dir?digest(node[name]):blobId(node[name]);return{key:name+(dir?'/':''),raw:[...utf8((dir?'40000':'100644')+' '+name+'\0'),...h.match(/../g).map(x=>parseInt(x,16))]};}).sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:0);const raw=rows.flatMap(r=>r.raw);return sha1([...utf8('tree '+raw.length+'\0'),...raw]);}return digest(root);
}
function trustedPublicationPlan(raw,pin,sha256){
  controlNeed(typeof raw==='string'&&raw.length>0&&raw.length<=262144&&/^[\x00-\x7f]*$/.test(raw)&&typeof pin==='string'&&/^[0-9a-f]{64}$/.test(pin)&&typeof sha256==='function'&&sha256(raw)===pin,'INDEPENDENT_ROOT_PLAN_BYTES_SHA_REQUIRED');
  let p;try{p=JSON.parse(raw);}catch(_){throw Error('ROOT_PLAN_JSON');}
  controlNeed(canonical(p)+'\n'===raw&&exactKeys(p,['schema','authority','phase','context','branch','parent_sha','files','expected_tree_sha','receiving','root_body_validation_at_unix_ms','root_issuer_authentication_required','authentication_boundary','supported_tool_order','reserve_and_retain_full_actual_result_before_next_call','automatic_retry','effect_grant','original_awards']),'CLOSED_CANONICAL_ROOT_PLAN');
  controlNeed(p.schema==='dg16.root-control-publication-plan.v1'&&p.authority==='NONE'&&['tools','g3_initial','g3_final'].includes(p.phase)&&p.context&&p.context.repository===CONTROL_REPO&&hex40(p.context.workflow_commit)&&typeof p.context.run_id==='string'&&/^[1-9][0-9]{0,19}$/.test(p.context.run_id),'ROOT_PLAN_CONTEXT_PHASE');
  controlNeed(exactKeys(p.context,['repository','branch','workflow_commit','workflow_path','run_id','run_attempt','job_name'])&&typeof p.context.branch==='string'&&p.context.branch.length>0&&typeof p.context.workflow_path==='string'&&p.context.workflow_path.length>0&&typeof p.context.job_name==='string'&&p.context.job_name.length>0&&Number.isSafeInteger(p.context.run_attempt)&&p.context.run_attempt>0,'CLOSED_ROOT_PLAN_CONTEXT');
  controlNeed(typeof p.branch==='string'&&/^pro\/[A-Za-z0-9][A-Za-z0-9/_-]{0,180}$/.test(p.branch)&&!p.branch.includes('..')&&!p.branch.includes('//')&&hex40(p.parent_sha)&&hex40(p.expected_tree_sha),'ROOT_PLAN_TARGET');
  controlNeed(p.root_issuer_authentication_required===true&&typeof p.authentication_boundary==='string'&&p.authentication_boundary.length>0&&p.reserve_and_retain_full_actual_result_before_next_call===true&&p.automatic_retry===false&&p.effect_grant===false&&canonical(p.original_awards)==='[]'&&Number.isSafeInteger(p.root_body_validation_at_unix_ms)&&p.root_body_validation_at_unix_ms>0,'ROOT_PLAN_BOUNDARY');
  controlNeed(exactKeys(p.receiving,['bytes','sha256'])&&Number.isSafeInteger(p.receiving.bytes)&&p.receiving.bytes>0&&/^[0-9a-f]{64}$/.test(p.receiving.sha256)&&canonical(p.supported_tool_order)===canonical([CONTROL_TOOLS.tree,CONTROL_TOOLS.commit,CONTROL_TOOLS.ref]),'ROOT_PLAN_RECEIVING_TOOLS');
  const first='qualification/dg16-r5-g3/ROOT_DECISION.json',last='qualification/dg16-r5-g3/ORIGINAL_DECISION.json',names=p.phase==='tools'?['HOST_TOOL_ADOPTION.json']:p.phase==='g3_initial'?[first]:[last,first];
  controlNeed(exactKeys(p.files,names),'ROOT_PLAN_EXACT_PHASE_FILES');
  for(const r of Object.values(p.files)){
    controlNeed(exactKeys(r,['body_utf8','bytes','sha256','git_blob_sha'])&&typeof r.body_utf8==='string'&&Number.isSafeInteger(r.bytes)&&r.bytes>0&&r.bytes<=65536&&utf8(r.body_utf8).length===r.bytes&&sha256(r.body_utf8)===r.sha256&&blobId(r.body_utf8)===r.git_blob_sha,'ROOT_PLAN_EXACT_BODY');
    // R.body.decode/encode cannot produce isolated surrogate code points.
    for(let i=0;i<r.body_utf8.length;i++){const c=r.body_utf8.charCodeAt(i);if(c>=0xd800&&c<=0xdbff){const d=r.body_utf8.charCodeAt(++i);controlNeed(d>=0xdc00&&d<=0xdfff,'ROOT_PLAN_BODY_UTF8');}else controlNeed(c<0xdc00||c>0xdfff,'ROOT_PLAN_BODY_UTF8');}
  }
  controlNeed(fixedTree(p.files)===p.expected_tree_sha,'ROOT_PLAN_TREE_ID');
  function freeze(v){if(v&&typeof v==='object'){for(const x of Object.values(v))freeze(x);Object.freeze(v);}return v;}return freeze(p);
}
function validateControlIntent(intent,stage,state,deadline){
  const p=state.plan;controlNeed(p&&exactKeys(intent,['schema','authority','kind','ordinal','call','deadline_unix_ms','automatic_retry','actual_native_history_required','frame_deadline_unix_ms'])&&intent.actual_native_history_required===true&&Number.isSafeInteger(intent.frame_deadline_unix_ms)&&intent.frame_deadline_unix_ms<=deadline&&intent.frame_deadline_unix_ms<=Date.now()+45000&&intent.authority==='NONE'&&intent.automatic_retry===false&&intent.deadline_unix_ms===deadline&&Number.isSafeInteger(intent.ordinal)&&intent.call,'EXACT_CONTROL_INTENT_REQUIRED');
  const call=intent.call;let expected;
  if(stage<3){
    controlNeed(exactKeys(call,['authority','tool','arguments','requires_separate_root_effect_authorization','previous_actual_tool_results','no_unknown_effect_replay'])&&intent.schema==='dg16.root-control-exclusive-call-intent.v1'&&intent.kind==='write-'+stage&&intent.ordinal===stage&&call.authority==='NONE'&&call.requires_separate_root_effect_authorization===true&&call.no_unknown_effect_replay===true,'THREE_EXACT_WRITE_ORDER');
    if(stage===0)expected={repository_full_name:CONTROL_REPO,tree_elements:Object.keys(p.files).sort().map(path=>({path,mode:'100644',type:'blob',content:p.files[path].body_utf8}))};
    else if(stage===1){controlNeed(state.tree===p.expected_tree_sha,'ACTUAL_TREE_DIFFERS_FROM_TRUSTED_PLAN');expected={repository_full_name:CONTROL_REPO,tree_sha:p.expected_tree_sha,parent_sha:p.parent_sha,message:'DG16 root control '+p.phase+' run '+p.context.run_id};}
    else{controlNeed(hex40(state.commit),'ACTUAL_COMMIT_REQUIRED');expected={repository_full_name:CONTROL_REPO,branch_name:p.branch,sha:state.commit,expected_sha:p.parent_sha,force:false};}
    controlNeed(call.tool===p.supported_tool_order[stage]&&canonical(call.arguments)===canonical(expected),'CALL_DIFFERS_FROM_INDEPENDENT_ROOT_PLAN');
    controlNeed(canonical(call.previous_actual_tool_results)===canonical(state.results),'ACTUAL_PREVIOUS_RESULT_DESCRIPTORS');
  }else{
    const i=stage-3;controlNeed(exactKeys(call,['kind','tool','arguments'])&&i<state.reads.length&&intent.schema==='dg16.root-control-exclusive-read-intent.v1'&&intent.ordinal===i&&intent.kind===state.reads[i][0]&&call.kind===intent.kind.slice(5)&&call.tool===(typeof state.reads[i][1]==='string'?CONTROL_TOOLS.fetch:CONTROL_TOOLS.file),'EXACT_ROOT_CONTROL_READ_PLAN');
    expected=typeof state.reads[i][1]==='string'?{url:state.reads[i][1]}:state.reads[i][1];controlNeed(canonical(call.arguments)===canonical(expected),'READ_DIFFERS_FROM_INDEPENDENT_ROOT_PLAN');
  }
  // Dispatch independently derived plain arguments, never the caller-owned object.
  return {tool:call.tool,arguments:JSON.parse(canonical(expected))};
}

async function runControl(io,native,deadlineUnixMs,trustedPlanRaw,trustedPlanSha256,receivedSha256){
  const state={results:[]};let stage=0,pending=null,returned=null;
  const preexistingSession=io.session??null,preexistingLaunch=io.launchAttempted===true;
  try{
    controlNeed(Number.isSafeInteger(deadlineUnixMs)&&Date.now()<deadlineUnixMs,'EXISTING_CONTROL_DEADLINE');
    state.plan=trustedPublicationPlan(trustedPlanRaw,trustedPlanSha256,receivedSha256);
    for(const name of Object.values(CONTROL_TOOLS))controlNeed(typeof native[name]==='function','ACTUAL_ROOT_NATIVE_WRITE_READ_SURFACE_REQUIRED');
    await io.assertAdmitted(deadlineUnixMs);
    for(;;){
      const next=await io.nextIntent();
      if(next.complete){controlNeed(Array.isArray(state.reads)&&stage===3+state.reads.length,'PREMATURE_CONTROL_COMPLETION');return {authority:'NONE',actual_receiving:await io.receive(),writes:3,reads:state.reads.length,original_awards:[]};}
      const intent=next.intent;const call=validateControlIntent(intent,stage,state,deadlineUnixMs);pending=intent.kind;
      // Waiting for real durable intent may expire/lose the owned role.
      controlNeed(Date.now()<deadlineUnixMs&&Date.now()<intent.frame_deadline_unix_ms&&Number.isSafeInteger(io.session)&&io.session>0&&!io.terminal&&io.echoReady&&io.controlPending==='','LIVE_ADMITTED_CONTROL_ROLE_BEFORE_MCP');
      const actual=await native[call.tool](call.arguments);
      // Always hand returned outcome to the real role; it records safe late
      // results before qualifying the next call. Root history remains real.
      const outcomeWire=JSON.stringify(actual);
      returned={kind:intent.kind,tool:call.tool,actual_result:{bytes:utf8(outcomeWire).length,sha256:receivedSha256(outcomeWire)},actual_native_history_required:true,local_receiving:'NOT_YET_PROVED'};
      controlNeed(typeof io.retainReturned==='function','EXACT_RECEIPT_ONLY_OUTCOME_ADAPTER_REQUIRED');
      await io.retainReturned(intent.kind,actual);
      returned.local_receiving='RETAINED_ACKNOWLEDGEMENT';
      controlNeed(Date.now()<intent.frame_deadline_unix_ms&&Date.now()<deadlineUnixMs,'RETURNED_OUTCOME_AFTER_FRAME_END');
      if(stage<3){const raw=JSON.stringify(actual);state.results.push({bytes:utf8(raw).length,sha256:receivedSha256(raw)});}
      if(stage===0){state.tree=rootResultSha(actual);controlNeed(state.tree===state.plan.expected_tree_sha,'ACTUAL_TREE_DIFFERS_FROM_TRUSTED_PLAN');}
      else if(stage===1){state.commit=rootResultSha(actual);const p=state.plan;state.reads=[['read-ref',CONTROL_API+'/git/ref/heads/'+p.branch],['read-commit',CONTROL_API+'/git/commits/'+state.commit],['read-tree',CONTROL_API+'/git/trees/'+p.expected_tree_sha+'?recursive=1'],...Object.keys(p.files).sort().map((n,i)=>['read-blob'+i,{repository_full_name:CONTROL_REPO,path:n,ref:state.commit,encoding:'base64'}]),['read-closing_ref',CONTROL_API+'/git/ref/heads/'+p.branch]];}
      stage++;pending=null;returned=null;
    }
  }catch(_error){
    let result=null,cleanupFailed=false;
    if(preexistingSession===null&&!preexistingLaunch){
      try{result=await io.unknown({pending,automatic_retry:false,no_effect_inferred:false});}catch(_ignored){cleanupFailed=true;}
    }
    const failure=Error('ROOT_CONTROL_PUBLICATION_REFUSED_OR_UNKNOWN_NO_REPLAY');
    failure.custody={status:preexistingSession!==null||preexistingLaunch?'PREEXISTING_PROCESS_UNTOUCHED':result?.status??'UNRESOLVED_ROOT_PROCESS_CUSTODY',session_id:io.session??null,terminal:io.terminal===true,exit_code:Number.isSafeInteger(io.last)?io.last:null,cleanup_failed:cleanupFailed,launch_attempted:io.launchAttempted===true,automatic_retry:false};
    if(returned)failure.returned_outcome=returned;
    throw failure;
  }
}

async function runControlWithSelection(tools,native,selection,deadlineUnixMs,receivedWindowsRoleIO,trustedPlanRaw,trustedPlanSha256,receivedSha256){
  const Base=receivedWindowsRoleIO||(typeof WindowsRoleIO!=='undefined'?WindowsRoleIO:
    (typeof require==='function'?require('../../windows_role_io.js').WindowsRoleIO:null));
  const IO=makeControlRoleIO(Base);return runControl(new IO(tools,selection),native,deadlineUnixMs,trustedPlanRaw,trustedPlanSha256,receivedSha256);
}
if(typeof module!=='undefined')module.exports={runControl,runControlWithSelection,makeControlRoleIO,validateControlIntent,trustedPublicationPlan,canonical,fixedTree,blobId,inertOneLeafTree,CONTROL_TOOLS};
