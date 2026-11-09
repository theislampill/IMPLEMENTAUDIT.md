(() => {
  const op = 'plans/astra-successor-reconciliation-20261108/g1-current04-issuer/original-host-01';
  const issuer = '/mnt/c/workspace/ai/improveimplementaudit/'+op+'/phase.py';
  const quote = value => "'"+String(value).replaceAll("'","''")+"'";
  function moduleFrom(raw) {const m={exports:{}};new Function('module',raw)(m);return m.exports;}
  function checked(result,why) {if(result.exit_code!==0)throw Error(why+': '+result.output.slice(-500));return result.output.trim();}
  async function rawExec(cmd, maximumOutput=2000){
    let r=await tools.exec_command({cmd,login:false,max_output_tokens:maximumOutput,yield_time_ms:1000});let output=r.output;
    while(r.session_id!=null && r.exit_code==null){r=await tools.write_stdin({session_id:r.session_id,chars:'',yield_time_ms:1000,max_output_tokens:maximumOutput});output+=r.output;}
    return {...r,output};
  }
  async function local(script,...args){
    return checked(await rawExec('& python -I -B '+[op+'/'+script,...args].map(quote).join(' ')+'; exit $LASTEXITCODE',3500),'LOCAL_'+script);
  }
  async function linux(script,args,output=10000){
    const argv=['C:\\Windows\\System32\\wsl.exe','-d','Ubuntu','-u','agent','--cd','/','--exec','/usr/bin/python3','-I','-B',script,...args];
    return checked(await rawExec("$PSNativeCommandArgumentPassing='Standard'; & "+argv.map(quote).join(' ')+'; exit $LASTEXITCODE',output),'ROOT_OPERATOR_CLI');
  }
  async function saved(name,obj){
    if(!/^[A-Za-z0-9_.-]+\.json$/.test(name))throw Error('unsafe receipt name');
    // Only public ref/endpoint results and bounded safe outcome summaries enter here.
    const s=JSON.stringify(obj);if(s.length>18500)throw Error('SAFE_WINDOWS_RECEIPT_BOUND');
    const path=op+'/'+name;
    return checked(await rawExec("$p=[IO.Path]::GetFullPath("+quote(path)+");$f=[IO.File]::Open($p,[IO.FileMode]::CreateNew);try{$b=[Text.UTF8Encoding]::new($false).GetBytes("+quote(s)+");$f.Write($b,0,$b.Length);$f.Flush($true)}finally{$f.Dispose()};(Get-FileHash -LiteralPath $p).Hash",60),'SAVE_RECEIPT');
  }
  async function role(phase,sources,shellTitle){
    const snapshot=JSON.parse(await local('observe.py',phase));if(!snapshot.available)return snapshot;
    const issued=JSON.parse(await linux(issuer,['role',phase,shellTitle]));
    const W=moduleFrom(sources.io).WindowsRoleIO, slots=moduleFrom(sources.slots);
    const io=new W(tools,issued.selection);
    try{
      const got=await slots.runSeven(io,tools,issued.deadline);
      const summary={phase,session:issued.session,slots:got.slots,receipt_received:!!got.actual_receiving,process_session:io.session,terminal:io.terminal,exit:io.last};
      await saved('ROLE_'+phase+'.json',summary);return summary;
    }catch(e){const summary={phase,session:issued.session,status:'REFUSED_OR_UNKNOWN_NO_REPLAY',code:e.message,custody:e.custody??null,process_session:io.session,terminal:io.terminal,exit:io.last};await saved('ROLE_'+phase+'_REFUSAL.json',summary);return summary}
  }
  async function publishControl(phase,sources,shellTitle){
    if(!['tools','g3_initial','g3_final'].includes(phase))throw Error('CONTROL_PHASE');
    if(phase==='tools')await linux(issuer,['tools',phase,shellTitle]);
    const branch=phase==='tools'?'pro/dg16-g1-tools-control-04-20261109':'pro/dg16-g1-g3-control-04-20261109';
    const raw=await tools.mcp__codex_apps__github_fetch({url:'https://api.github.com/repos/theislampill/IMPLEMENTAUDIT.md/git/ref/heads/'+branch});
    if(raw.isError)throw Error('PARENT_READBACK_FAILED');
    await saved('PARENT_'+phase+'.json',raw);
    const v=JSON.parse(await linux(issuer,['control',phase,shellTitle]));
    const W=moduleFrom(sources.io).WindowsRoleIO, control=moduleFrom(sources.control);
    const hash=new Function(sources.hash+';return sha256;')();
    try{
      const received=await control.runControlWithSelection(tools,tools,v.selection,v.deadline,W,v.trusted_plan,v.trusted_sha,hash);
      const summary={phase,writes:received.writes,reads:received.reads,actual_receiving:received.actual_receiving};await saved('CONTROL_'+phase+'.json',summary);return summary;
    }catch(e){const summary={phase,status:'REFUSED_OR_UNKNOWN_NO_REPLAY',code:e.message,custody:e.custody??null,returned:e.returned_outcome??null};await saved('CONTROL_'+phase+'_REFUSAL.json',summary);return summary}
  }
  return {rawExec,linux,local,role,publishControl,saved};
})()
