/* Evaluates to an inert API. All effects are explicit injected Root callbacks. */
(() => {
 'use strict';
 const THREAD='01a1953f-a15b-7811-aa72-3538ebb03562';
 const HEADER='e6fba7c217f360f6b6f6d3c11f42052131b89cf0042289e07902347ccf8d0389';
 const TOOL='mcp__codex_apps__github_fetch',DOWNLOAD='mcp__codex_apps__github_download_workflow_artifact';
 const READY='READY_FOR_EPHEMERAL_DOWNLOAD_RESULT_LENGTH_FRAME';
 const TERMINAL='PUBLIC_BODY_AND_METADATA_RECEIVED_REQUIRES_INDEPENDENT_RECEIVING';
 const ORDER=['run','attempt','jobs','commit','workflow','artifacts','download','body','closing-run','closing-artifacts'];
 const need=(v,c)=>{if(!v)throw Error(c)};
 const exact=(v,keys)=>v!==null&&typeof v==='object'&&!Array.isArray(v)&&Object.keys(v).sort().join('|')===[...keys].sort().join('|');
 const hex=s=>typeof s==='string'&&/^[0-9a-f]{64}$/.test(s);
 function descriptor(v){return exact(v,['bytes','sha256'])&&Number.isSafeInteger(v.bytes)&&v.bytes>0&&v.bytes<=4*1024**2&&hex(v.sha256)}
 function same(a,b){return JSON.stringify(a)===JSON.stringify(b)}
 function utf8(s){const out=[];for(const ch of s){let n=ch.codePointAt(0);if(n<128)out.push(n);else if(n<2048)out.push(192|n>>6,128|n&63);else if(n<65536)out.push(224|n>>12,128|n>>6&63,128|n&63);else out.push(240|n>>18,128|n>>12&63,128|n>>6&63,128|n&63)}return out}
 function sha256(text){
  const bytes=utf8(text),length=bytes.length,bits=length*8;bytes.push(128);while(bytes.length%64!==56)bytes.push(0);
  const hi=Math.floor(bits/4294967296),lo=bits>>>0;for(const x of [hi,lo])for(let s=24;s>=0;s-=8)bytes.push(x>>>s&255);
  const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  const H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19],rot=(n,s)=>(n>>>s)|(n<<(32-s));
  for(let off=0;off<bytes.length;off+=64){const w=[];for(let i=0;i<16;i++)w[i]=(bytes[off+4*i]<<24|bytes[off+4*i+1]<<16|bytes[off+4*i+2]<<8|bytes[off+4*i+3])>>>0;
   for(let i=16;i<64;i++){const a=w[i-15],b=w[i-2];w[i]=(w[i-16]+(rot(a,7)^rot(a,18)^(a>>>3))+w[i-7]+(rot(b,17)^rot(b,19)^(b>>>10)))>>>0}
   let [a,b,c,d,e,f,g,h]=H;for(let i=0;i<64;i++){const t1=(h+(rot(e,6)^rot(e,11)^rot(e,25))+((e&f)^(~e&g))+K[i]+w[i])>>>0,t2=((rot(a,2)^rot(a,13)^rot(a,22))+((a&b)^(a&c)^(b&c)))>>>0;h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0}
   for(const [i,x] of [a,b,c,d,e,f,g,h].entries())H[i]=(H[i]+x)>>>0;
  }return H.map(x=>x.toString(16).padStart(8,'0')).join('');
 }
 function jsonValue(v,depth=0){need(depth<=100,'JSON_DEPTH');if(v===null||typeof v==='string'||typeof v==='boolean')return;if(typeof v==='number'){need(Number.isFinite(v),'JSON_NONFINITE');return}need(typeof v==='object','JSON_VALUE');if(Array.isArray(v)){for(const x of v)jsonValue(x,depth+1);return}need(Object.getPrototypeOf(v)===Object.prototype||Object.getPrototypeOf(v)===null,'JSON_PROTOTYPE');for(const k of Object.keys(v))jsonValue(v[k],depth+1)}
 function endpoint(c,k){const p='https://api.github.com/repos/'+c.repository,r=c.run_id;return p+({run:'/actions/runs/'+r,attempt:'/actions/runs/'+r+'/attempts/1',jobs:'/actions/runs/'+r+'/attempts/1/jobs?per_page=100&page=1',commit:'/git/commits/'+c.workflow_commit,workflow:'/contents/'+c.workflow_path+'?ref='+c.workflow_commit,artifacts:'/actions/runs/'+r+'/artifacts?per_page=100','closing-run':'/actions/runs/'+r,'closing-artifacts':'/actions/runs/'+r+'/artifacts?per_page=100'})[k]}
 function validateConfig(cfg){
  need(exact(cfg,['context','role','turn_id','configuration_sha256','deadline_ms']),'DRIVER_CONFIG_FIELDS');const c=cfg.context;
  need(exact(c,['repository','branch','run_id','run_attempt','workflow_commit','source_commit','source_tree','workflow_path','job_name']),'CONTEXT_FIELDS');
  need(c.repository==='theislampill/IMPLEMENTAUDIT.md'&&c.branch==='pro/dg16-r5-full-g2-direct-host-01-20261109'&&/^[1-9][0-9]{0,19}$/.test(c.run_id)&&c.run_attempt===1&&c.workflow_commit==='7f618adc702912f760d87f68fe9c94cc419e844c'&&c.source_commit==='7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'&&c.source_tree==='6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e'&&c.workflow_path==='.github/workflows/dg16-r5-full-g2.yml'&&c.job_name==='full-registry-raw-pair','EXACT_EPISODE_SUBJECT');
  need(['live','terminal'].includes(cfg.role)&&/^[0-9a-f-]{36}$/.test(cfg.turn_id)&&hex(cfg.configuration_sha256)&&Number.isSafeInteger(cfg.deadline_ms),'ACTUAL_ROLE_CONFIG_REQUIRED');
 }
 function validateTool(e,cfg,ordinal){
  need(exact(e,['event','tool','native_tool','args','deadline_ms','mark','ordinal','wire'])&&e.ordinal===ordinal&&ordinal!==7&&ORDER[ordinal],'EXACT_ONE_SHOT_ORDINAL');
  need(Number.isSafeInteger(e.deadline_ms)&&e.deadline_ms<=cfg.deadline_ms&&e.wire==='JSON.stringify(actual) UTF8 NO_TRAILING_NEWLINE','EXACT_WIRE_AND_DEADLINE');
  const m=e.mark;need(exact(m,['thread','turn','identity','offset','header'])&&m.thread===THREAD&&m.turn===cfg.turn_id&&m.header===HEADER&&Array.isArray(m.identity)&&m.identity.length===2&&m.identity.every(x=>typeof x==='string'&&/^[0-9]+$/.test(x))&&Number.isSafeInteger(m.offset)&&m.offset>=0,'EXACT_CURRENT_ROOT_CURSOR');
  if(ordinal===6){need(e.tool===DOWNLOAD&&e.native_tool==='github.download_workflow_artifact'&&exact(e.args,['repo_full_name','artifact_id','file_name'])&&e.args.repo_full_name===cfg.context.repository&&Number.isSafeInteger(e.args.artifact_id)&&e.args.artifact_id>0&&e.args.file_name===(cfg.role==='live'?'dg16-full-correspondence-review-':'dg16-full-registry-')+cfg.context.run_id+'-1.zip','EXACT_DOWNLOAD_ONLY')}
  else need(e.tool===TOOL&&e.native_tool==='github.fetch'&&exact(e.args,['url'])&&e.args.url===endpoint(cfg.context,ORDER[ordinal]),'EXACT_METADATA_ENDPOINT');
 }
 async function run(cfg,io){
  let processState=null,ordinal=0,pending=null,body=null,terminal=null,buffer='',total=0,sent=0,invoked=0,started=false;
  let failure='DRIVER_REFUSED_OR_COMPLETION_UNKNOWN';
  try{
   validateConfig(cfg);for(const k of ['now','start','poll','send','call','retain','stop','readback'])need(typeof io[k]==='function','EXPLICIT_CALLBACKS_REQUIRED');
   const began=io.now();need(began<cfg.deadline_ms&&cfg.deadline_ms<=began+300000,'ROLE_TIME_WINDOW');
   await io.retain({event:'driver_start_intent',authority:'NONE',configuration_sha256:cfg.configuration_sha256,role:cfg.role,turn_id:cfg.turn_id,deadline_ms:cfg.deadline_ms,automatic_retry:false});
   started=true;processState=await io.start();
   async function line(text){
    text=text.replace(/\r/g,'').trim();if(!text)return;
    need(text.length<=32768,'PROTOCOL_LINE_BOUND');
    if(text===READY){need(pending!==null,'UNASSOCIATED_FRAME_READINESS');need(io.now()<pending.deadline_ms,'TOOL_START_DEADLINE');
     const event=pending;await io.retain({event:'driver_tool_intent',authority:'NONE',ordinal,tool:event.tool,args:event.args,configuration_sha256:cfg.configuration_sha256,deadline_ms:event.deadline_ms,automatic_retry:false});
     // Await the actual tool exactly once. No Promise.race/cancel fiction or
     // second invocation when completion is late, refused or indeterminate.
     invoked++;let actual=await io.call(event.tool,event.args);jsonValue(actual);need(actual!==null&&typeof actual==='object'&&!Array.isArray(actual),'COMPLETE_TOOL_RESULT_REQUIRED');
     let wire=JSON.stringify(actual);const bytes=utf8(wire).length;need(bytes>0&&bytes<=4194304,'COMPLETE_WIRE_BOUND');
     const ack={wire_sha256:sha256(wire),wire_bytes:bytes};wire=null;actual=null;
     need(io.now()<event.deadline_ms,'TOOL_RETURNED_AFTER_DEADLINE');
     const payload=JSON.stringify(ack);await io.retain({event:'driver_wire_descriptor',authority:'NONE',ordinal,...ack,automatic_retry:false});
     pending=null;ordinal++;sent++;const response=await io.send(String(utf8(payload).length)+'\n'+payload);
     // Process send output is consumed by the same bounded parser below.
     need(response&&typeof response==='object','PROCESS_SEND_RESULT');queued.push(response);return;
    }
    let e;try{e=JSON.parse(text)}catch{throw Error('UNRECOGNIZED_PROCESS_OUTPUT')}
    if(e.event==='tool_request'){need(pending===null&&!terminal,'DUPLICATE_PENDING_REQUEST');validateTool(e,cfg,ordinal);pending=e;return}
    if(e.event==='body_get_intent'){
     need(ordinal===7&&!pending&&body===null&&exact(e,['event','body_operation_ref','artifact_id','expected_archive','deadline_ms'])&&/^root_body_get_[0-9a-f]{64}$/.test(e.body_operation_ref)&&Number.isSafeInteger(e.artifact_id)&&e.artifact_id>0&&descriptor(e.expected_archive)&&e.expected_archive.bytes<=262144&&Number.isSafeInteger(e.deadline_ms)&&io.now()<e.deadline_ms&&e.deadline_ms<=cfg.deadline_ms,'EXACT_BODY_INTENT');
     body={ref:e.body_operation_ref,archive:e.expected_archive};await io.retain({event:'driver_body_intent_observed',authority:'NONE',body_operation_ref:body.ref,expected_archive:body.archive,automatic_retry:false});return;
    }
    if(e.event==='body_get_outcome'){
     const o=e.outcome;need(exact(e,['event','outcome'])&&o&&body&&ordinal===7&&o.body_operation_ref===body.ref&&o.mcp_tool_call_id===null&&o.automatic_retry===false&&o.redirects===false&&o.proxy===false&&o.body_get_attempts===1&&o.status==='RECEIVED'&&descriptor(o.archive)&&same(o.archive,body.archive),'BODY_REFUSED_OR_UNKNOWN');
     // Do not retain the arbitrary outcome object. Only closed descriptors.
     await io.retain({event:'driver_body_received_observed',authority:'NONE',body_operation_ref:body.ref,archive:body.archive,mcp_tool_call_id:null,automatic_retry:false});ordinal++;return;
    }
    need(exact(e,['status','authority','role','archive','automatic_retry'])&&e.status===TERMINAL&&e.authority==='NONE'&&e.role===cfg.role&&e.automatic_retry===false&&descriptor(e.archive)&&body&&same(e.archive,body.archive)&&ordinal===10&&!pending&&!terminal,'EXACT_TERMINAL_REQUIRED');terminal=e;
   }
   const queued=[];
   for(;;){
    need(io.now()<cfg.deadline_ms,'OPERATOR_PROCESS_DEADLINE');
    need(processState&&typeof processState.output==='string','PROCESS_RESULT_REQUIRED');
    total+=utf8(processState.output).length;need(total<=131072,'TOTAL_PROTOCOL_OUTPUT_BOUND');
    // Actual adapter supplies only source/READY-bound regular-file records.
    // Screen output, including any CSI sequence, is never reconstructed here.
    need(!processState.output.includes('\u001b'),'SCREEN_OUTPUT_NOT_A_RECORD_SOURCE');
    buffer+=processState.output;
    while(buffer.includes('\n')){const at=buffer.indexOf('\n'),text=buffer.slice(0,at);buffer=buffer.slice(at+1);await line(text)}
    if(processState.exit_code!==undefined){if(buffer.trim()){await line(buffer);buffer=''}need(processState.exit_code===0&&terminal&&ordinal===10&&sent===9&&!pending,'PROCESS_TERMINAL_NOT_PROVED');break}
    need(Number.isSafeInteger(processState.session_id),'RUNNING_PROCESS_ID_REQUIRED');
    processState=queued.length?queued.shift():await io.poll();
   }
   const readback=await io.readback(terminal);need(readback&&readback.status==='EXACT_TERMINAL_PUBLIC_FILES_READ_BACK'&&readback.role===cfg.role&&descriptor(readback.archive)&&same(readback.archive,terminal.archive),'TERMINAL_READBACK_MISMATCH');
   const result={status:'TERMINAL_READ_BACK',authority:'NONE',role:cfg.role,configuration_sha256:cfg.configuration_sha256,archive:terminal.archive,received_mcp_requests:sent,body_http_separate:true,original_acceptance:false,automatic_retry:false};
   await io.retain(result);return result;
  }catch{
   // No exception text, raw stdout, tool result, file reference or history is
   // returned or persisted. Stop never authorizes a duplicate call or restart.
   let stopped=null;if(started){try{stopped=await io.stop(failure)}catch{}}
   const result={status:'UNKNOWN_NO_RETRY',authority:'NONE',reason:failure,next_ordinal:ordinal,actual_tool_invocations:invoked,configuration_sha256:hex(cfg&&cfg.configuration_sha256)?cfg.configuration_sha256:null,process_exit_code:stopped&&Number.isSafeInteger(stopped.exit_code)?stopped.exit_code:null,process_session_id:stopped&&Number.isSafeInteger(stopped.session_id)?stopped.session_id:null,raw_frames_retained:false,automatic_retry:false};
   try{if(io&&typeof io.retain==='function')await io.retain(result)}catch{}
   return result;
  }
 }
 return {run,utf8,sha256,endpoint,THREAD,HEADER,TOOL,DOWNLOAD,READY,TERMINAL,ORDER};
})()
