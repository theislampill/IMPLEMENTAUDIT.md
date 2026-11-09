(async (action, runtime, sources, shellTitle, helperPin) => {
  const script='/mnt/c/workspace/ai/improveimplementaudit/plans/astra-successor-reconciliation-20261108/g1-current04-issuer/original-host-01/sender.py';
  const exec=async name=>JSON.parse(await runtime.linux(script,[name,helperPin],11000));
  if(action==='assemble')return await exec('assemble');
  if(action==='sender'||action==='start-bound-sender'){
    const ready=await exec(action==='sender'?'admit-dispatch':'check-ready-dispatch'),hash=Function(sources.hash+';return sha256;')();
    if(hash(ready.dispatch)!==ready.dispatch_sha256||Date.now()>=ready.expires_ms)throw Error('DISPATCH_SOURCE_OR_EXPIRY');
    const start=await tools.exec_command({cmd:ready.command,login:false,yield_time_ms:1000,max_output_tokens:4500});let ss=start.session_id??null,tail=start.output||'',status=start.exit_code??null;
    await runtime.saved('SENDER_STARTED.json',{utc:new Date().toISOString(),session:ss,initial_exit:status,expires_ms:ready.expires_ms,dispatch_sha256:ready.dispatch_sha256});
    let done=null,records=[],problem=null;
    if(ss!==null&&status===null){
      try {
        const call=Function('tools','notify','text','setTimeout','return (async()=>{'+ready.dispatch+'\n})()');
        await call(tools,r=>{if(r.dispatcher==='EXACT_FIXED_READ_RETAINED_AND_PUBLISHED')records.push({ordinal:r.ordinal,tool:r.logical_tool_call_ref,descriptor:r.actual_tool_result})},v=>{done=v},setTimeout);
      }catch(e){problem=String(e.message).replace(/[^A-Za-z0-9_]/g,' ').slice(0,130);}
      while(status===null){
        const r=await tools.write_stdin({session_id:ss,chars:'',yield_time_ms:1000,max_output_tokens:4500});
        if(tail.length<100000)tail+=r.output||'';status=r.exit_code??null;
      }
    }
    let terminal=null;try{const t=JSON.parse(tail.trim());if(t.schema==='dg16.root-sender-terminal-export.v1')terminal=t;}catch{}
    const result={terminal,exit:status,session_id:ss,dispatch_finished:done?.status==='DISPATCH_18_COMPLETE_SENDER_TERMINAL_SEPARATE',actual_calls:records.length,dispatch_receiving:done,records,problem,stdout_sha256:hash(tail)};
    await runtime.saved('SENDER_RESULT.json',result);return {status:terminal?.result?.status??'REFUSAL_OR_UNKNOWN',exit:status,ds:result.dispatch_finished,reads:records.length,custody:ss,problem};
  }
  if(action==='prepare-binary'){
    const branch='pro/dg16-g1-carrier-control-04-20261109',v=await tools.mcp__codex_apps__github_fetch({url:'https://api.github.com/repos/theislampill/IMPLEMENTAUDIT.md/git/ref/heads/'+branch});
    if(v.isError)throw Error('FRESH_CIPHER_PARENT_REQUIRED');await runtime.saved('PARENT_cipher.json',v);return await exec(action);
  }
  if(action==='binary'){
    const ready=await exec('admit-binary');
    const decode=src=>{const m={exports:{}};new Function('module',src)(m);return m.exports};
    const selection={distribution:'Ubuntu',user:'agent',python:'/usr/bin/python3',shellTitle,...ready.selection};
    const B=decode(sources.binary),W=decode(sources.io).WindowsRoleIO;
    try{
      const result=await B.runBinaryWithSelection(tools,tools,selection,ready.trustedPlanRaw,ready.plan.sha256,ready.deadline_unix_ms,W,ready.purpose);
      const record={writes:result.writes,reads:result.reads,actual_receiving:result.actual_receiving};
      await runtime.saved('CIPHER_READBACK.json',record);return record;
    }catch(e){const record={status:'UNKNOWN_NO_REPLAY',code:e.message,custody:e.custody??null,returned:e.returned_outcome??null};await runtime.saved('CIPHER_REFUSAL.json',record);return record;}
  }
  throw Error('unsupported Root stage');
})
