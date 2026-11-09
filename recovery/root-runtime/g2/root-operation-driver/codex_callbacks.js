/* Evaluates to a factory. Loading it performs no tool, process or file action. */
((D,tools,selection) => {
 'use strict';
 const need=(v,c)=>{if(!v)throw Error(c)};
 need(selection&&selection.wslExe==='C:\\WINDOWS\\system32\\wsl.exe'&&selection.distribution==='Ubuntu'&&selection.user==='agent'&&selection.installationRoot==='/home/agent/dg16-g2-current04-public-20261109/root-operation-driver-01','EXACT_RECEIVED_WSL_SELECTION');
 const root=selection.installationRoot;
 need(['live','terminal'].includes(selection.role)&&selection.configuration===root+'/'+selection.role+'.configuration.json'&&selection.admission.startsWith(root+'/')&&/^[A-Za-z0-9_./-]+$/.test(selection.admission)&&!selection.admission.split('/').includes('..'),'EXACT_CONFIGURATION_ADMISSION_PATHS');
 const quote=s=>"'"+s.replaceAll("'","''")+"'";
 function command(action,...args){return ['&',quote(selection.wslExe),...['--distribution',selection.distribution,'--user',selection.user,'--exec','/usr/bin/python3','-I','-B',root+'/operator_setup.py',action,...args].map(quote)].join(' ')}
 function base64(bytes){const C='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';let out='';for(let i=0;i<bytes.length;i+=3){const a=bytes[i],b=bytes[i+1],c=bytes[i+2];out+=C[a>>2]+C[(a&3)<<4|(b??0)>>4]+(b===undefined?'=':C[(b&15)<<2|(c??0)>>6])+(c===undefined?'=':C[c&63])}return out}
 let processId=null,processExit=undefined,cursor=0,pendingSequence=null;
 const update=result=>{if(result.session_id!==undefined)processId=result.session_id;if(result.exit_code!==undefined)processExit=result.exit_code;return result};
 async function helper(action,...args){const r=await tools.exec_command({cmd:command(action,...args),yield_time_ms:1000,max_output_tokens:12000});need(r.exit_code===0&&r.session_id===undefined,'HELPER_COMPLETION_UNKNOWN_NO_REPLAY');return JSON.parse(r.output.trim())}
 async function publicRecords(){
  const r=await helper('drain',selection.configuration,String(cursor));need(Array.isArray(r.records)&&Number.isSafeInteger(r.next_cursor)&&r.next_cursor>=cursor,'BOUNDED_RECORD_CURSOR');let output='';
  for(const record of r.records){need(record.sequence===cursor&&record.value&&record.request&&record.request.sha256,'EXACT_PUBLIC_RECORD_SEQUENCE');output+=JSON.stringify(record.value)+'\n';
   if(record.value.event==='tool_request'){need(record.ready&&record.ready.sequence===cursor&&record.ready.request.sha256===record.request.sha256&&record.ready.request.bytes===record.request.bytes,'EXACT_PUBLIC_READY_BINDING');pendingSequence=cursor;output+=D.READY+'\n'}cursor++;
  }need(cursor===r.next_cursor,'EXACT_RECORD_CLOSING_CURSOR');return processExit===undefined?{output,session_id:processId}:{output,exit_code:processExit};
 }
 async function pollProcess(){if(processExit===undefined){need(Number.isSafeInteger(processId),'NO_PROCESS_TO_POLL');update(await tools.write_stdin({session_id:processId,chars:'',yield_time_ms:1000,max_output_tokens:1000}))}return publicRecords()}
 return {
  now:()=>Date.now(),
  // Never interpret these process stdout chunks or ConPTY screen redraws.
  start:async()=>{update(await tools.exec_command({cmd:command('run',selection.configuration,selection.admission),tty:false,yield_time_ms:1000,max_output_tokens:1000}));return publicRecords()},
  poll:pollProcess,
  send:async frame=>{need(Number.isSafeInteger(pendingSequence)&&typeof frame==='string'&&frame.length<=4096,'EXACT_DESCRIPTOR_FRAME');const at=frame.indexOf('\n'),raw=frame.slice(at+1);need(at>0&&Number(frame.slice(0,at))===D.utf8(raw).length,'DESCRIPTOR_LENGTH');
   const seq=pendingSequence;pendingSequence=null;const r=await helper('respond',selection.configuration,String(seq),base64(D.utf8(raw)));need(r.status==='EXACT_DESCRIPTOR_RESPONSE_WRITTEN'&&r.sequence===seq,'EXACT_RESPONSE_READBACK');return pollProcess()},
  call:async(name,args)=>{if(name===D.TOOL)return await tools.mcp__codex_apps__github_fetch(args);if(name===D.DOWNLOAD)return await tools.mcp__codex_apps__github_download_workflow_artifact(args);throw Error('UNSUPPORTED_TOOL')},
  retain:async note=>{const r=await helper('note',selection.configuration,base64(D.utf8(JSON.stringify(note))));need(r.status==='SAFE_DRIVER_NOTE_RETAINED','NOTE_NOT_RETAINED')},
  // A pipe is not a terminal: a Ctrl-C byte would not prove process cleanup.
  // Backend frame/role watchdogs remain bounded; preserve actual exit or UNKNOWN.
  stop:async()=>{if(processExit===undefined&&Number.isSafeInteger(processId))update(await tools.write_stdin({session_id:processId,chars:'',yield_time_ms:1000,max_output_tokens:1000}));return {exit_code:processExit??null,session_id:processId}},
  readback:async()=>await helper('readback',selection.configuration)
 };
})
