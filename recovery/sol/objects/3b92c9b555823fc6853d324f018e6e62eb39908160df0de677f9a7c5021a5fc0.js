/* Root-invoked G1 seven-slot bridge. No global tool call or automatic start.
 * io is the actual installed receiver/no-echo transport, supplied by Root.
 * native is the real first-party tool surface, never gh/curl/a replacement.
 * Matching a plan is not authentication; Root owns real admission/history.
 */
const ORDER = Object.freeze(['artifacts','run','attempt','jobs','artifact','workflow','download']);
const FETCH = 'mcp__codex_apps__github_fetch';
const DOWNLOAD = 'mcp__codex_apps__github_download_workflow_artifact';
function need(v,c){if(!v)throw Error(c);}
function jsonOnly(v,depth=0){
  need(depth<=100,'TOOL_RESULT_DEPTH');
  if(v===null || ['string','boolean'].includes(typeof v))return;
  if(typeof v==='number'){need(Number.isFinite(v),'TOOL_NONFINITE');return;}
  need(typeof v==='object','TOOL_NON_JSON');
  if(Array.isArray(v)){for(const x of v)jsonOnly(x,depth+1);return;}
  need(Object.getPrototypeOf(v)===Object.prototype || Object.getPrototypeOf(v)===null,'TOOL_NONPLAIN');
  for(const key of Object.keys(v))jsonOnly(v[key],depth+1);
}
function byteLength(text){
  let n=0;for(const ch of text){const c=ch.codePointAt(0);n+=c<128?1:c<2048?2:c<65536?3:4;}return n;
}
function validateIntent(kind,intent){
  need(intent && intent.schema==='dg16.root-receiver-call-intent.v1' && intent.authority==='NONE'
    && intent.kind===kind && intent.automatic_retry===false,'EXACT_RESERVED_INTENT_REQUIRED');
  const a=intent.arguments;
  if(kind==='download'){
    need(intent.tool===DOWNLOAD && a && Object.keys(a).sort().join(',')==='artifact_id,file_name,repo_full_name'
      && a.repo_full_name==='theislampill/IMPLEMENTAUDIT.md' && Number.isSafeInteger(a.artifact_id) && a.artifact_id>0
      && typeof a.file_name==='string' && /^[A-Za-z0-9._-]{1,256}\.zip$/.test(a.file_name),'FIXED_DOWNLOAD_PLAN');
  }else{
    need(intent.tool===FETCH && a && Object.keys(a).join(',')==='url' && typeof a.url==='string'
      && a.url.startsWith('https://api.github.com/repos/theislampill/IMPLEMENTAUDIT.md/')
      && !/[\r\n\u0000]/.test(a.url),'FIXED_METADATA_PLAN');
  }
}
async function runSeven(io,native,deadlineUnixMs){
  need(Number.isSafeInteger(deadlineUnixMs) && Date.now()<deadlineUnixMs,'EXISTING_ROOT_DEADLINE_REQUIRED');
  for(const method of ['assertAdmitted','reserve','retain','receiveEphemeralBody','receive','unknown'])
    need(typeof io[method]==='function','ACTUAL_ROOT_IO_ADAPTER_REQUIRED');
  need(typeof native[FETCH]==='function' && typeof native[DOWNLOAD]==='function','REAL_FIRST_PARTY_SURFACE_REQUIRED');
  // This callback must authenticate the actual Root role/run/journal/installed
  // source and existing deadline. A JSON owner/permission label is insufficient.
  const preexistingSession=io.session??null,preexistingLaunch=io.launchAttempted===true;
  let pending=null,downloadResult=null;
  try{
    await io.assertAdmitted(deadlineUnixMs);
    for(const kind of ORDER){
      need(Date.now()<deadlineUnixMs,'ROOT_DEADLINE_EXPIRED');
      pending=kind;
      const intent=await io.reserve(kind);validateIntent(kind,intent);
      need(Date.now()<deadlineUnixMs,'ROOT_DEADLINE_AFTER_DURABLE_RESERVE_NO_TOOL');
      // One actual call after durable O_EXCL intent. No retry/fallback/race.
      const actual=await native[intent.tool](intent.arguments);
      jsonOnly(actual);need(actual!==null && typeof actual==='object' && !Array.isArray(actual),'COMPLETE_ACTUAL_TOOL_OBJECT');
      need(byteLength(JSON.stringify(actual)+'\n')<=4194304,'COMPLETE_RESULT_BOUND');
      // Actual full wrapper stays in Root memory. retain must use the qualified
      // no-echo stdin/frame route; download_note redacts before any disk write.
      // Never put this value, its duplicate history, or signed URL in argv/log.
      await io.retain(kind,actual,intent);
      if(kind==='download')downloadResult=actual;
      pending=null;
    }
    need(Date.now()<deadlineUnixMs,'ROOT_DEADLINE_BEFORE_BODY');pending='body';
    // Exactly one admitted secure file-ref body GET, using Root's already
    // qualified ephemeral-frame transport. Return metadata, never echo body.
    await io.receiveEphemeralBody(downloadResult,deadlineUnixMs);
    downloadResult=null;pending='receiving';
    need(Date.now()<deadlineUnixMs,'ROOT_DEADLINE_BEFORE_RECEIVING');
    const receipt=await io.receive(deadlineUnixMs);pending=null;
    return {authority:'NONE',slots:7,actual_receiving:receipt,original_awards:[]};
  }catch(_error){
    // Do not echo provider exception text or retain a signed result on failure.
    // An extinct frame/unknown completion remains UNKNOWN, never another GET.
    let result=null,cleanupFailed=false;
    if(preexistingSession===null&&!preexistingLaunch){
      try{result=await io.unknown({authority:'NONE',pending,automatic_retry:false,raw_result_retained:false});}catch(_ignored){cleanupFailed=true;}
    }
    const failure=Error('ROOT_PROVIDER_ROLE_REFUSED_OR_UNKNOWN_NO_REPLAY');
    failure.custody={status:preexistingSession!==null||preexistingLaunch?'PREEXISTING_PROCESS_UNTOUCHED':
      result?.status??'UNRESOLVED_ROOT_PROCESS_CUSTODY',session_id:io.session??null,
      terminal:io.terminal===true,exit_code:Number.isSafeInteger(io.last)?io.last:null,cleanup_failed:cleanupFailed,
      launch_attempted:io.launchAttempted===true,automatic_retry:false};
    throw failure;
  }finally{downloadResult=null;}
}
if(typeof module!=='undefined')module.exports={runSeven,validateIntent};
