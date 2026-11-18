/* Inert functions.exec factory. Pass the actual tools object explicitly.
 * Transport records never replace native history, owner admission, or G1/G3 proof.
 * No grant, sender, process, GitHub call, or file is created by loading this file.
 */
((injected) => {
  'use strict';
  let {tools, codec, linux} = injected;
  const need = (v, c) => { if (!v) throw Error(c); };
  const same = (a, b) => codec.canonical(a) === codec.canonical(b);
  const clone = v => codec.strict(codec.canonical(v));
  const hex = v => typeof v === 'string' && /^[0-9a-f]{64}$/.test(v);
  const oid = v => typeof v === 'string' && /^[0-9a-f]{40}$/.test(v);
  const integer = v => Number.isSafeInteger(v);
  const MAX = 4 * 1024 * 1024, CHUNK = 8192, FLOOR = 300000;
  const FETCH = 'mcp__codex_apps__github_fetch';
  const FILE = 'mcp__codex_apps__github_fetch_file';
  const CREATE_BRANCH = 'mcp__codex_apps__github_create_branch';
  const WRITES = ['mcp__codex_apps__github_create_blob', 'mcp__codex_apps__github_create_tree',
    'mcp__codex_apps__github_create_commit', 'mcp__codex_apps__github_update_ref'];
  const READY = 'READY_FOR_EPHEMERAL_DOWNLOAD_RESULT_LENGTH_FRAME';
  const HOST_LAUNCH = 'pro/dg16-g1-original-g3-32-20261114';
  const quote = s => "'" + s.replace(/'/g, "'\\''") + "'";
  const utf8 = s => {
    const out=[];
    for (const ch of s) { let n=ch.codePointAt(0);if(n>=0xd800&&n<=0xdfff)n=0xfffd;
      if(n<128)out.push(n); else if(n<2048)out.push(192|n>>6,128|n&63);
      else if(n<65536)out.push(224|n>>12,128|n>>6&63,128|n&63);
      else out.push(240|n>>18,128|n>>12&63,128|n>>6&63,128|n&63);
    } return out;
  };
  const base64 = bytes => { const C='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'; let out='';
    for(let i=0;i<bytes.length;i+=3){const a=bytes[i],b=bytes[i+1],c=bytes[i+2];
      out+=C[a>>2]+C[(a&3)<<4|(b??0)>>4]+(b===undefined?'=':C[(b&15)<<2|(c??0)>>6])+(c===undefined?'=':C[c&63]);
    } return out;
  };
  const decode64 = text => { need(typeof text==='string' && /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(text),'BASE64');
    const C='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/', out=[];
    for(let i=0;i<text.length;i+=4){const a=C.indexOf(text[i]),b=C.indexOf(text[i+1]),c=C.indexOf(text[i+2]),d=C.indexOf(text[i+3]);
      out.push((a<<2)|(b>>4));if(text[i+2]!=='=')out.push(((b&15)<<4)|(c>>2));if(text[i+3]!=='=')out.push(((c&3)<<6)|d);
    } need(base64(out)===text,'CANONICAL_BASE64');return out;
  };
  function textBytes(bytes) {
    // Argument files from the maintained owner are ASCII JSON, including escaped Unicode.
    need(bytes.every(v=>v<128),'OWNER_ARGUMENT_JSON_MUST_BE_ASCII');
    let out='';for(let i=0;i<bytes.length;i+=8192)out+=String.fromCharCode(...bytes.slice(i,i+8192));return out;
  }
  need(tools && typeof tools.exec_command==='function' && typeof tools.write_stdin==='function', 'ACTUAL_PROCESS_TOOLS_REQUIRED');
  for(const k of ['canonical','strict','descriptor'])need(typeof codec?.[k]==='function','RECEIVED_CODEC_REQUIRED');
  need(linux && typeof linux.python_path==='string' && linux.python_path.startsWith('/')
    && typeof linux.helper_path==='string' && linux.helper_path.startsWith('/') && hex(linux.helper_sha256)
    && typeof linux.journal_root==='string' && linux.journal_root.startsWith('/'),'CURRENT_LINUX_PATH_SELECTION');
  linux=clone(linux);
  // Source is read through a no-follow descriptor and executed from the exact received bytes.
  const LOADER="import hashlib,os,pathlib,stat,sys; p=pathlib.Path(sys.argv[1]); mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns); assert p.is_absolute() and p.resolve(strict=True)==p and all(not x.is_symlink() for x in p.parents); s=p.lstat(); assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid() and not s.st_mode&0o022 and 0<s.st_size<=1048576; fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC); assert mark(os.fstat(fd))==mark(s) and not os.listxattr(fd); b=os.pread(fd,1048577,0); assert len(b)==s.st_size and hashlib.sha256(b).hexdigest()==sys.argv[2] and mark(os.fstat(fd))==mark(s)==mark(p.lstat()); os.close(fd); sys.argv=[str(p),*sys.argv[3:]]; exec(compile(b,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})";
  function command(path,pin,args){
    need(typeof path==='string'&&path.startsWith('/')&&hex(pin)&&Array.isArray(args)
      &&args.every(x=>typeof x==='string'&&!x.includes('\0')),'PINNED_COMMAND_ARGUMENTS');
    return [linux.python_path,'-I','-B','-c',LOADER,path,pin,...args].map(quote).join(' ');
  }
  async function host(action,value){
    const encoded=base64(utf8(codec.canonical(value)));need(encoded.length<=256*1024,'HOST_ARGUMENT_BOUND');
    let r=await tools.exec_command({cmd:command(linux.helper_path,linux.helper_sha256,[action,encoded]),
      login:false,shell:'/bin/bash',yield_time_ms:1000,max_output_tokens:6000});
    let out=r.output||'', session=r.session_id, polls=0;
    while(r.exit_code===undefined&&r.session_id!==undefined){
      need(++polls<=48&&integer(session)&&r.session_id===session,'HOST_COMPLETION_UNKNOWN');
      r=await tools.write_stdin({session_id:session,chars:'',yield_time_ms:1000,max_output_tokens:6000});
      out+=r.output||'';need(out.length<=65536,'HOST_RETURN_BOUND');
    }
    need(r.exit_code===0&&r.session_id===undefined,'HOST_REFUSED_OR_UNKNOWN');
    return codec.strict(out.trim());
  }
  function validateSpec(input,role){
    const s=clone(input), c=s.context;
    need(s.schema==='dg16.pro-functions-operator.v1'&&s.role===role,'OPERATOR_SCOPE');
    need(c&&c.repository==='theislampill/IMPLEMENTAUDIT.md'&&typeof c.run_id==='string'
      &&/^[1-9][0-9]{0,15}$/.test(c.run_id)&&c.run_attempt===1&&oid(c.workflow_commit)
      &&oid(c.source_commit)&&oid(c.source_tree),'EXACT_EPISODE_CONTEXT');
    need(s.actor&&s.actor.surface==='ChatGPT-functions'&&typeof s.actor.controller==='string'
      &&s.actor.controller.length>0&&typeof s.actor.continuity_receipt==='string'
      &&s.actor.continuity_receipt.length>0&&typeof s.actor.assignment_ref==='string'
      &&s.actor.assignment_ref.length>0,'CURRENT_ACTOR_CLAIMS_REQUIRED');
    need(integer(s.issued_ms)&&integer(s.expires_ms)&&s.issued_ms<=Date.now()
      &&Date.now()<s.expires_ms&&s.expires_ms<=s.issued_ms+600000,'ORIGINAL_BOUNDED_WINDOW');
    need(oid(s.operator_source?.commit)&&hex(s.operator_source?.index_sha256),'SELECTED_OPERATOR_SOURCE');
    return s;
  }
  async function session(input,role,admit,body){
    let key=null,index=0,started=false,calls=0,scope=null;
    try{
      const spec=validateSpec(input,role);
      need(typeof admit==='function','LIVE_ADMISSION_CAPABILITY_REQUIRED');
      if(role==='sender')need(spec.expires_ms-Date.now()>=FLOOR,'REMAINING_300000MS_REQUIRED');
      const actual=await host('identity',{root:linux.journal_root});
      need(actual.stable?.platform==='linux'&&actual.native_model_identity==='NOT_OBSERVED','ACTUAL_LINUX_OBSERVATION');
      scope=clone({spec,host_identity:actual,transport_source:{path:linux.helper_path,sha256:linux.helper_sha256},
        journal_root:linux.journal_root,automatic_retry:false,original_acceptance:false});
      const frozen=codec.canonical(scope),permit=await admit(scope);
      need(permit&&typeof permit.assertCurrent==='function'&&typeof permit.assertNoReplay==='function'
        &&typeof permit.authorization?.ref==='string'
        &&hex(permit.authorization?.sha256),'LIVE_CURRENT_AUTHORITY_CAPABILITY_REQUIRED');
      async function current(action,allowLate=false){
        need(codec.canonical(scope)===frozen,'ADMISSION_SCOPE_MUTATED');
        if(!allowLate)need(Date.now()<spec.expires_ms,'OPERATOR_EXPIRED');
        need(await permit.assertCurrent({scope,action})!==false,'LIVE_AUTHORITY_REFUSED');
        need(await permit.assertNoReplay({scope,action})!==false,'UNKNOWN_OR_SPENT_SUBJECT_REFUSED');
        need(codec.canonical(scope)===frozen,'ADMISSION_SCOPE_MUTATED');
        if(!allowLate)need(Date.now()<spec.expires_ms,'OPERATOR_EXPIRED');
      }
      await current({kind:'open'});
      const subject={context:spec.context,role,stage:spec.stage||null};
      const subject_json=codec.canonical(subject);key=codec.descriptor(subject_json).sha256;
      await host('open',{root:linux.journal_root,key,subject_json,scope_sha256:codec.descriptor(frozen).sha256,
        authorization:permit.authorization,host_identity:actual.stable,expires_ms:spec.expires_ms,max_steps:128});
      started=true;
      async function once(kind,request,fn,{floor=false,deadline=spec.expires_ms}={}){
        const frozenRequest=clone(request);await current({kind,phase:'before-reserve',request:frozenRequest});
        need(Date.now()<deadline,'ORIGINAL_FRAME_EXPIRED');
        if(floor)need(spec.expires_ms-Date.now()>=FLOOR,'REMAINING_300000MS_REQUIRED');
        const intent=await host('reserve',{root:linux.journal_root,key,index,kind,request:codec.descriptor(codec.canonical(frozenRequest)),deadline_ms:deadline});
        need(intent.status==='RESERVED_ONCE','DURABLE_INTENT_REQUIRED');
        await current({kind,phase:'before-invoke',request:frozenRequest});
        need(Date.now()<deadline,'ORIGINAL_FRAME_EXPIRED');
        if(floor)need(spec.expires_ms-Date.now()>=FLOOR,'REMAINING_300000MS_REQUIRED');
        // No race timeout and no second invocation after late/unknown completion.
        calls++;const actual=await fn();codec.canonical(actual);
        const raw=JSON.stringify(actual);need(typeof raw==='string'&&utf8(raw).length<=MAX,'COMPLETE_RESULT_BOUND');
        codec.strict(raw);
        await host('complete',{root:linux.journal_root,key,index,intent:intent.record,
          result:codec.descriptor(raw),returned_ms:Date.now(),qualification:'NOT_YET_CHECKED'});
        index++;
        await current({kind,phase:'after-return',result:codec.descriptor(raw)});
        need(Date.now()<deadline,'LATE_RETURN_PRESERVED_NO_REPLAY');
        return actual;
      }
      const result=await body({spec,scope,permit,current,once});
      await current({kind:'finish'});
      await host('finish',{root:linux.journal_root,key,index,result:codec.descriptor(codec.canonical(result))});
      need(Date.now()<spec.expires_ms,'TERMINAL_AFTER_DEADLINE');
      return {status:'TRANSPORT_COMPLETE_REQUIRES_ORIGINAL_RECEIVING',authority:'NONE',role,
        subject_key:key,steps:index,actual_callbacks_or_tools:calls,result,original_acceptance:false,
        native_history_authenticated:false,automatic_retry:false};
    }catch{
      if(started){try{await host('unknown',{root:linux.journal_root,key,index,
        status:'UNKNOWN_NO_REPLAY',no_effect_inferred:false,automatic_retry:false});}catch{}}
      return {status:started?'UNKNOWN_NO_REPLAY':'REFUSED_BEFORE_OPERATION',authority:'NONE',
        subject_key:key,steps:index,actual_callbacks_or_tools:calls,original_acceptance:false,
        native_history_authenticated:false,automatic_retry:false,no_effect_inferred:false};
    }
  }
  function wholeResult(actual){
    need(actual&&typeof actual==='object'&&!Array.isArray(actual)&&typeof actual.isError==='boolean','FULL_ACTUAL_TOOL_RESULT');
    need(!Object.keys(actual._meta||{}).some(k=>['truncated','isTruncated','partial','hasMore'].includes(k)&&actual._meta[k]),'TRUNCATED_TOOL_RESULT');
    codec.canonical(actual);const raw=JSON.stringify(actual);codec.strict(raw);need(utf8(raw).length<=MAX,'ACTUAL_RESULT_BOUND');return raw;
  }
  function endpoint(c,i){
    const p='https://api.github.com/repos/'+c.repository,r=c.run_id;
    return p+['/actions/runs/'+r,'/actions/runs/'+r+'/attempts/1',
      '/actions/runs/'+r+'/attempts/1/jobs?per_page=100&page=1','/actions/runs/'+r+'/artifacts?per_page=100',
      '/actions/runs/'+r+'/artifacts?per_page=100','/contents/'+c.workflow_path+'?ref='+c.workflow_commit][i%6];
  }
  async function observePublic(input,admit){
    return session(input,'public-observation',admit,async s=>{
      need(typeof tools[FETCH]==='function','ACTUAL_PUBLIC_TOOL_REQUIRED');
      const arguments_={url:endpoint(s.spec.context,0)};
      const actual=await s.once('public-run-observation',{tool:FETCH,arguments:arguments_},
        ()=>tools[FETCH](clone(arguments_)));
      const raw=wholeResult(actual);need(actual.isError===false,'PUBLIC_TOOL_REFUSED');
      return {tool:FETCH,arguments:arguments_,actual_result:codec.descriptor(raw),
        qualification:'PUBLIC_READ_TRANSPORT_SMOKE_ONLY',sender_invoked:false,g3_invoked:false};
    });
  }
  async function prepareSmokeBranch(input,admit){
    return session(input,'smoke-branch',admit,async s=>{
      const p=s.spec.smoke;
      need(p?.scope==='SYNTHETIC_TRANSPORT_ONLY_NO_ORIGINAL_INPUTS'
        &&typeof p.branch==='string'&&/^engineering\/g132-portability-smoke-[a-z0-9-]{1,80}$/.test(p.branch)
        &&oid(p.parent_sha),'EXACT_FRESH_ENGINEERING_SMOKE');
      for(const name of [WRITES[1],WRITES[2],CREATE_BRANCH,FETCH])need(typeof tools[name]==='function','ACTUAL_SMOKE_TOOL_REQUIRED');
      const content=codec.canonical({schema:'dg16.g132-public-portability-smoke.v1',authority:'NONE',
        original_acceptance:false,private_inputs:false,controller:s.spec.actor.controller,
        run_id:s.spec.context.run_id})+'\n';
      const args={repository_full_name:s.spec.context.repository,tree_elements:[{path:'G132_PORTABILITY_SMOKE.json',mode:'100644',type:'blob',content}]};
      const tree=await s.once('smoke-data-tree',{tool:WRITES[1],arguments:args},()=>tools[WRITES[1]](clone(args)));
      wholeResult(tree);need(tree.isError===false&&oid(tree.structuredContent?.sha),'ACTUAL_SMOKE_TREE');
      const commitArgs={repository_full_name:s.spec.context.repository,tree_sha:tree.structuredContent.sha,
        parent_sha:p.parent_sha,message:'G132 public portability smoke; synthetic data only'};
      const commit=await s.once('smoke-data-commit',{tool:WRITES[2],arguments:commitArgs},()=>tools[WRITES[2]](clone(commitArgs)));
      wholeResult(commit);need(commit.isError===false&&oid(commit.structuredContent?.sha),'ACTUAL_SMOKE_COMMIT');
      const branchArgs={repository_full_name:s.spec.context.repository,branch_name:p.branch,sha:commit.structuredContent.sha};
      const branch=await s.once('smoke-fresh-branch',{tool:CREATE_BRANCH,arguments:branchArgs},()=>tools[CREATE_BRANCH](clone(branchArgs)));
      wholeResult(branch);need(branch.isError===false,'ACTUAL_FRESH_BRANCH_REQUIRED');
      const url='https://api.github.com/repos/'+s.spec.context.repository+'/git/ref/heads/'+p.branch;
      const read=await s.once('smoke-branch-readback',{tool:FETCH,arguments:{url}},()=>tools[FETCH]({url}));
      wholeResult(read);const sc=read.structuredContent;
      need(read.isError===false&&sc?.url===url&&sc.display_url===url&&typeof sc.content==='string','ACTUAL_SMOKE_REF_ENDPOINT');
      const ref=codec.strict(sc.content);need(ref.ref==='refs/heads/'+p.branch&&ref.object?.type==='commit'
        &&ref.object.sha===commit.structuredContent.sha,'ACTUAL_SMOKE_REF_JOIN');
      return {branch:p.branch,parent_sha:commit.structuredContent.sha,base_parent:p.parent_sha,
        data_only_tree:tree.structuredContent.sha,qualification:'PUBLIC_SYNTHETIC_BRANCH_ONLY',original_awards:[]};
    });
  }
  async function sender(input,admit,{dispatcher,startSender,receiveSenderTerminal}){
    return session(input,'sender',admit,async s=>{
      need(typeof startSender==='function'&&typeof receiveSenderTerminal==='function','ACTUAL_SENDER_CAPABILITIES_REQUIRED');
      need(typeof tools[FETCH]==='function'&&dispatcher&&typeof dispatcher.path==='string'
        &&hex(dispatcher.descriptor?.sha256)&&integer(dispatcher.descriptor?.bytes),'PINNED_DISPATCHER_REQUIRED');
      need(s.spec.context.workflow_path==='.github/workflows/dg16-r5-g1-hosted-episode.yml','ORIGINAL_SENDER_WORKFLOW');
      const helper=async(args)=>{
        await s.current({kind:'existing-dispatcher',args_descriptor:codec.descriptor(codec.canonical(args))});
        const r=await host('invoke',{source:dispatcher,args:args.map(String),deadline_ms:s.spec.expires_ms});
        need(r.status==='PINNED_HELPER_RETURNED','EXISTING_HELPER_RETURN_REQUIRED');return r.result;
      };
      const start=await s.once('actual-sender-start',{context:s.spec.context,dispatcher},
        ()=>startSender({scope:s.scope,minimum_remaining_ms:FLOOR}),{floor:true});
      need(start&&start.automatic_retry===false,'SENDER_START_CUSTODY_REQUIRED');
      need((await helper(['initialize'])).status==='INITIALIZED','DISPATCH_JOURNAL_OPEN');
      for(let i=0;i<18;i++){
        let ready=null;
        for(let polls=0;polls<120;polls++){
          ready=await helper(['ready',i]);if(ready.status==='READY')break;
          need(ready.status==='PENDING'&&ready.fetch_permitted===false,'READINESS_REFUSED');
          await new Promise(resolve=>setTimeout(resolve,50));
        }
        need(ready?.status==='READY','READINESS_BOUND');
        const reserved=await helper(['reserve',i]),call=reserved.plan;
        need(reserved.status==='RESERVED_ONCE'&&integer(reserved.remaining_ms)&&reserved.remaining_ms>0
          &&typeof reserved.logical_tool_call_ref==='string'&&reserved.logical_tool_call_ref.length>0
          &&hex(call.intent_sha256)&&call.ordinal===i&&call.tool===FETCH
          &&same(call.arguments,{url:endpoint(s.spec.context,i)}),'EXACT_RESERVED_SENDER_READ');
        const actual=await s.once('sender-read',{ordinal:i,tool:FETCH,arguments:call.arguments,
          original_intent_sha256:call.intent_sha256},()=>tools[FETCH](clone(call.arguments)));
        const raw=wholeResult(actual)+'\n',bytes=utf8(raw);let last;
        for(let offset=0;offset<bytes.length;offset+=CHUNK){
          const part=bytes.slice(offset,offset+CHUNK);last=await helper(['chunk',i,offset,base64(part)]);
          need(last.status==='CHUNK_RETAINED'&&last.bytes===offset+part.length,'SOURCE_RESULT_CHUNK_READBACK');
        }
        const retained=await helper(['complete',i,bytes.length,last.sha256,call.intent_sha256]);
        need(retained.status==='ACTUAL_FULL_RESULT_RETAINED'&&retained.receipt.logical_tool_call_ref===reserved.logical_tool_call_ref,'SOURCE_RESULT_JOIN');
        const published=await helper(['publish',i]);
        need(published.status==='PUBLISHED'&&published.ordinal===i&&published.broker_status==='RECEIVED'
          &&published.fetch_permitted===false,'SOURCE_BROKER_REFUSED');
      }
      const dispatch=await helper(['finish']);
      need(dispatch.status==='DISPATCH_18_COMPLETE_SENDER_TERMINAL_SEPARATE','DISPATCH_CLOSURE');
      const terminal=await s.once('sender-terminal-receiving',{dispatch:codec.descriptor(codec.canonical(dispatch))},
        ()=>receiveSenderTerminal({scope:s.scope,start,dispatch}));
      return {sender_reads:18,dispatch,terminal,source_receiving_separate:true};
    });
  }
  function validateCall(call,spec,created){
    need(call&&[FETCH,FILE,...WRITES].includes(call.tool)&&typeof tools[call.tool]==='function'
      &&call.arguments&&typeof call.arguments==='object','SUPPORTED_ACTUAL_TOOL_REQUIRED');
    const a=call.arguments,p=spec.publication,c=spec.context;
    if(call.tool===FETCH){const prefix='https://api.github.com/repos/'+c.repository;
      need(typeof a.url==='string'&&Object.keys(a).length===1&&[
        prefix+'/git/ref/heads/'+p.branch,prefix+'/git/refs/heads/'+p.branch,
        prefix+'/git/commits/'+created.commit,prefix+'/git/trees/'+created.tree+(p.writes===3?'?recursive=1':'')].includes(a.url),
        'EXACT_PUBLICATION_READBACK_ONLY');return;}
    need(a.repository_full_name===c.repository,'EXACT_REPOSITORY');
    if(call.tool===FILE){need(p.paths.includes(a.path)&&a.ref===created.commit&&a.encoding==='base64','EXACT_PUBLICATION_FILE');return;}
    if(call.tool===WRITES[0]){need(typeof a.content==='string'&&['utf-8','base64'].includes(a.encoding),'BLOB_ENCODING');return;}
    if(call.tool===WRITES[1]){
      need(Array.isArray(a.tree_elements)&&a.tree_elements.length===p.paths.length
        &&same(a.tree_elements.map(x=>x.path).sort(),[...p.paths].sort())
        &&(a.base_tree_sha===undefined||a.base_tree_sha===null)
        &&a.tree_elements.every(x=>x.mode==='100644'&&x.type==='blob'
          &&((oid(x.sha)&&x.content===undefined)||(typeof x.content==='string'&&x.sha===undefined))),
        'EXACT_DATA_TREE');return;
    }
    if(call.tool===WRITES[2]){need(a.parent_sha===p.parent_sha&&a.tree_sha===created.tree
      &&(!a.additional_parent_shas||a.additional_parent_shas.length===0),'ONE_EXPECTED_PARENT');return;}
    need(a.branch_name===p.branch&&p.branch!==HOST_LAUNCH&&a.expected_sha===p.parent_sha
      &&a.force===false&&a.sha===created.commit,'EXPECTED_OLD_NONFORCE_REF_REQUIRED');
  }
  async function publish(input,admit,source){
    return session(input,'publication',admit,async s=>{
      const p=s.spec.publication;
      need(p&&p.kind==='CONTROL_DATA_ONLY'&&typeof p.branch==='string'&&p.branch!==HOST_LAUNCH
        &&/^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$/.test(p.branch)
        &&!p.branch.includes('..')&&!p.branch.endsWith('/')&&!p.branch.endsWith('.lock')
        &&oid(p.parent_sha)&&[3,5].includes(p.writes)&&integer(p.reads)
        &&Array.isArray(p.paths)&&p.paths.length>=1&&p.paths.length<=16
        &&p.reads===p.paths.length+4&&new Set(p.paths).size===p.paths.length
        &&(p.writes===3||same([...p.paths].sort(),['CONTROL.json','INPUTS.cms']))
        &&p.paths.every(x=>typeof x==='string'&&/^[A-Za-z0-9_.-]+(?:\/[A-Za-z0-9_.-]+)*$/.test(x)
          &&!x.split('/').some(v=>v==='.'||v==='..')&&!x.startsWith('.github/')),'BOUNDED_DATA_PUBLICATION_ONLY');
      for(const k of ['start','next','respond'])need(typeof source?.[k]==='function','ACTUAL_LOCAL_PROCESS_CAPABILITY_REQUIRED');
      need(integer(source.selection?.deadline_ms)&&Date.now()<source.selection.deadline_ms
        &&source.selection.deadline_ms<=s.spec.expires_ms,'PROCESS_WITHIN_ORIGINAL_DEADLINE');
      await s.once('publication-process-start',{selection:source.selection},()=>source.start());
      const created={},order=p.writes===5?[WRITES[0],WRITES[0],WRITES[1],WRITES[2],WRITES[3]]:[WRITES[1],WRITES[2],WRITES[3]];
      let n=0,last=null;
      for(;;){
        await s.current({kind:'source-frame',ordinal:n});const event=await source.next();
        if(event.event==='complete'){
          need(n===p.writes+p.reads&&event.receipt&&event.receipt.authority==='NONE','COMPLETE_SOURCE_RECEIVING_REQUIRED');
          return {calls:n,source_receipt:event.receipt,source_acceptance_separate:true};
        }
        need(event.event==='intent'&&event.ready===true&&event.intent,'EXACT_SOURCE_INTENT_AND_FRAME_READINESS');
        const i=event.intent,deadline=i.frame_deadline_unix_ms;
        need(n<p.writes+p.reads&&i.authority==='NONE'&&i.automatic_retry===false,'ORIGINAL_CALL_BOUND');
        need(integer(deadline)&&Date.now()<deadline&&deadline<=Math.min(s.spec.expires_ms,Date.now()+45000),'ORIGINAL_45S_FRAME');
        if(p.writes===5){need(i.schema==='dg16.binary-publication-exclusive-intent.v1'
          &&integer(i.frame_started_unix_ms)&&i.frame_started_unix_ms<=Date.now()
          &&integer(i.expires_unix_ms)&&deadline<=Math.min(i.frame_started_unix_ms+45000,i.expires_unix_ms),'ORIGINAL_BINARY_FRAME_WINDOW');}
        else need(['dg16.root-control-exclusive-call-intent.v1','dg16.root-control-exclusive-read-intent.v1'].includes(i.schema)
          &&integer(i.deadline_unix_ms)&&deadline<=i.deadline_unix_ms,'ORIGINAL_CONTROL_FRAME_WINDOW');
        const call=i.call||await source.readArguments(event);
        validateCall(call,s.spec,created);
        need(n<p.writes?call.tool===order[n]:[FETCH,FILE].includes(call.tool),'ORIGINAL_WRITE_READ_ORDER');
        if(n>=p.writes){
          const api='https://api.github.com/repos/'+s.spec.context.repository,paths=[...p.paths].sort();
          const reads=[{tool:FETCH,arguments:{url:api+'/git/ref/heads/'+p.branch}},
            {tool:FETCH,arguments:{url:api+'/git/commits/'+created.commit}},
            {tool:FETCH,arguments:{url:api+'/git/trees/'+created.tree+(p.writes===3?'?recursive=1':'')}},
            ...paths.map(path=>({tool:FILE,arguments:{repository_full_name:s.spec.context.repository,path,ref:created.commit,encoding:'base64'}})),
            {tool:FETCH,arguments:{url:api+'/git/ref/heads/'+p.branch}}];
          need(same({tool:call.tool,arguments:call.arguments},reads[n-p.writes]),'EXACT_ORIGINAL_READBACK_ORDER');
        }
        const actual=await s.once('publication-tool',{ordinal:n,tool:call.tool,arguments:call.arguments,
          source_intent_sha256:codec.descriptor(codec.canonical(i)).sha256},()=>tools[call.tool](clone(call.arguments)),{deadline});
        const raw=wholeResult(actual);
        last=codec.descriptor(raw);await s.current({kind:'deliver-original-result',ordinal:n,descriptor:last});
        need(Date.now()<deadline,'ORIGINAL_FRAME_EXPIRED');
        await source.respond(raw,last);n++;
        need(actual.isError===false,'ACTUAL_TOOL_REFUSAL_DELIVERED');
        if(call.tool===WRITES[1]){need(oid(actual.structuredContent?.sha),'ACTUAL_TREE_ID_REQUIRED');created.tree=actual.structuredContent.sha;}
        if(call.tool===WRITES[2]){need(oid(actual.structuredContent?.sha),'ACTUAL_COMMIT_ID_REQUIRED');created.commit=actual.structuredContent.sha;}
      }
    });
  }
  async function consumeG3(input,admit,{readRequest,validateRequest,decide,validateDecision,consume}){
    return session(input,'g3',admit,async s=>{
      for(const fn of [readRequest,validateRequest,decide,validateDecision,consume])
        need(typeof fn==='function','ACTUAL_G3_OWNER_AND_ROOT_CALLBACKS_REQUIRED');
      need(['components','original-final'].includes(s.spec.stage),'EXACT_G3_STAGE');
      const request=await s.once('g3-actual-request',{stage:s.spec.stage},()=>readRequest({scope:s.scope}));
      need(typeof request?.raw==='string'&&utf8(request.raw).length>0&&utf8(request.raw).length<=MAX,'ACTUAL_REQUEST_BYTES_REQUIRED');
      await s.current({kind:'validate-original-request'});
      const requestBinding=await validateRequest({scope:s.scope,request});
      need(requestBinding&&requestBinding.request_sha256===codec.descriptor(request.raw).sha256,'ORIGINAL_REQUEST_VALIDATION_REQUIRED');
      await s.current({kind:'validated-original-request'});
      const decision=await s.once('live-root-decision',{requestBinding},()=>decide({scope:s.scope,request,requestBinding}));
      need(typeof decision?.raw==='string'&&utf8(decision.raw).length>0&&utf8(decision.raw).length<=MAX,'ACTUAL_DECISION_BYTES_REQUIRED');
      await s.current({kind:'validate-original-decision'});
      const decisionBinding=await validateDecision({scope:s.scope,request,requestBinding,decision});
      need(decisionBinding&&decisionBinding.request_sha256===requestBinding.request_sha256
        &&decisionBinding.decision_sha256===codec.descriptor(decision.raw).sha256,'ORIGINAL_DECISION_VALIDATION_REQUIRED');
      await s.current({kind:'validated-original-decision'});
      // The separate existing owner must actually consume; a decision JSON is not this effect.
      const consumed=await s.once('actual-g3-consumption',{requestBinding,decisionBinding},
        ()=>consume({scope:s.scope,request,decision,requestBinding,decisionBinding}));
      need(consumed&&typeof consumed==='object','ACTUAL_G3_RETURN_REQUIRED');
      return {requestBinding,decisionBinding,consumer_return:consumed,
        original_scope_adjudication:'SEPARATE_EXISTING_OWNER_REQUIRED'};
    });
  }
  function senderProcess(selection){
    const selected=clone(selection);need(typeof selected.path==='string'&&hex(selected.sha256)
      &&integer(selected.deadline_ms)&&Date.now()<selected.deadline_ms
      &&selected.deadline_ms<=Date.now()+600000,'ACTUAL_SENDER_PROCESS_SELECTION');
    let process=null,exit,output='',started=false,terminalRead=false;
    const update=r=>{need(r&&typeof r.output==='string','SENDER_PROCESS_RESULT');output+=r.output;
      need(utf8(output).length<=32768,'ORIGINAL_SENDER_TERMINAL_BOUND');
      if(r.session_id!==undefined){need(process===null||process===r.session_id,'SENDER_PROCESS_SUBSTITUTED');process=r.session_id;}
      if(r.exit_code!==undefined)exit=r.exit_code;};
    return Object.freeze({
      startSender:async({scope,minimum_remaining_ms})=>{
        need(!started&&minimum_remaining_ms===FLOOR&&scope.spec.expires_ms<=selected.deadline_ms
          &&scope.spec.expires_ms-Date.now()>=FLOOR,'ACTUAL_SENDER_START_FLOOR');started=true;
        update(await tools.exec_command({cmd:command(selected.path,selected.sha256,[]),login:false,
          shell:'/bin/bash',yield_time_ms:1000,max_output_tokens:4000}));
        return {status:'ACTUAL_PINNED_LINUX_SENDER_PROCESS_INVOKED',process_session_id:process,
          returned_exit_code:exit??null,source:clone(selected),automatic_retry:false};
      },
      receiveSenderTerminal:async()=>{
        need(started&&!terminalRead,'ONE_SENDER_TERMINAL_RECEIVING');terminalRead=true;
        for(let polls=0;exit===undefined;polls++){
          need(polls<600&&Date.now()<selected.deadline_ms&&integer(process),'SENDER_TERMINAL_UNKNOWN');
          update(await tools.write_stdin({session_id:process,chars:'',yield_time_ms:1000,max_output_tokens:4000}));
        }
        need(exit===0&&Date.now()<selected.deadline_ms,'ACTUAL_SENDER_TERMINAL_EXIT');
        const value=codec.strict(output.trim());need(value.schema==='dg16.root-sender-terminal-export.v1'
          &&value.authority==='NONE'&&value.result?.status==='PAYLOAD_READY'
          &&value.publication_performed===false&&same(value.original_awards,[]),'ORIGINAL_SENDER_TERMINAL');
        return {raw:output,descriptor:codec.descriptor(output),actual:value,
          physical_process_session_id:process,original_receiving_required:true};
      },
    });
  }
  function framedProcess(selection){
    const selected=clone(selection);need(typeof selected.path==='string'&&hex(selected.sha256)
      &&Array.isArray(selected.args)&&typeof selected.exchange_root==='string'
      &&integer(selected.deadline_ms)&&Date.now()<selected.deadline_ms
      &&selected.deadline_ms<=Date.now()+600000,'PINNED_PROCESS_SELECTION');
    let process=null,exit,buffer='',queue=[],pending=null,last=null,frameKind=null,terminal=null,started=false,total=0;
    async function update(r){
      need(r&&typeof r.output==='string'&&!r.output.includes('\u001b'),'NONSCREEN_PROCESS_OUTPUT_REQUIRED');
      if(r.session_id!==undefined){need(process===null||process===r.session_id,'PROCESS_SUBSTITUTED');process=r.session_id;}
      if(r.exit_code!==undefined)exit=r.exit_code;
      total+=utf8(r.output).length;need(total<=262144,'PROCESS_OUTPUT_BOUND');buffer+=r.output;
      while(buffer.includes('\n')){const at=buffer.indexOf('\n'),line=buffer.slice(0,at).replace(/\r$/,'');buffer=buffer.slice(at+1);if(line)queue.push(line);}
    }
    async function next(){
      for(let polls=0;polls<240;polls++){
        need(Date.now()<selected.deadline_ms,'ORIGINAL_PROCESS_DEADLINE');
        while(queue.length){const line=queue.shift();
          if(line===READY){need(pending&&!last&&!frameKind&&!terminal,'UNBOUND_FRAME_READY');
            const event=pending;pending=null;frameKind=event.intent.kind;need(typeof frameKind==='string'&&frameKind.length>0,'ORIGINAL_FRAME_KIND');return {...event,ready:true};}
          const event=codec.strict(line);
          if(event.event==='intent'){need(!pending&&!last&&!frameKind&&!terminal,'DUPLICATE_OR_UNACKNOWLEDGED_INTENT');pending=event;continue;}
          if(event.event==='retained'){need(last&&event.kind===last.kind&&same(event.actual_result||event.receipt,last.descriptor),'SOURCE_RETURN_DESCRIPTOR_CHANGED');last=null;continue;}
          if(event.event==='complete'){need(!pending&&!last&&!frameKind&&!terminal,'PROCESS_TERMINAL_SEQUENCE');terminal=event;continue;}
          throw Error('SOURCE_REFUSED_OR_UNKNOWN_FRAME');
        }
        if(terminal&&exit!==undefined){need(exit===0&&!buffer,'PROCESS_TERMINAL_EXIT_REQUIRED');return terminal;}
        need(exit===undefined&&integer(process),'PROCESS_COMPLETION_UNKNOWN');
        await update(await tools.write_stdin({session_id:process,chars:'',yield_time_ms:1000,max_output_tokens:4000}));
      }throw Error('PROCESS_POLL_BOUND');
    }
    return Object.freeze({selection:clone(selected),
      start:async()=>{need(!started,'LOCAL_PROCESS_REPLAY');started=true;
        await update(await tools.exec_command({cmd:command(selected.path,selected.sha256,selected.args),
          login:false,shell:'/bin/bash',tty:true,yield_time_ms:1000,max_output_tokens:4000}));
        return {status:'PINNED_PROCESS_STARTED',process_session_id:process,automatic_retry:false};},
      next,
      readArguments:async event=>{
        const i=event.intent;need(i.schema==='dg16.binary-publication-exclusive-intent.v1'
          &&hex(event.intent_sha256)&&typeof event.intent_path==='string','ORIGINAL_BINARY_INTENT');
        need(typeof i.kind==='string'&&/^[A-Za-z0-9_-]+$/.test(i.kind)
          &&event.intent_path.endsWith('/'+i.kind+'.INTENT.json')
          &&i.arguments_path===event.intent_path.slice(0,event.intent_path.lastIndexOf('/')+1)+i.kind+'.ARGUMENTS.json',
          'ORIGINAL_ARGUMENTS_FILE_JOIN');
        const retained=await host('read-intent',{exchange_root:selected.exchange_root,path:event.intent_path,
          sha256:event.intent_sha256,deadline_ms:i.frame_deadline_unix_ms});
        need(same(retained.intent,i),'DURABLE_ORIGINAL_INTENT_CHANGED');
        const desc=i.arguments;need(integer(desc?.bytes)&&desc.bytes>0&&desc.bytes<=MAX&&hex(desc.sha256),'ARGUMENT_DESCRIPTOR');
        const parts=[];let physical=null;
        for(let offset=0;offset<desc.bytes;offset+=CHUNK){
          const row=await host('read-chunk',{exchange_root:selected.exchange_root,path:i.arguments_path,
            descriptor:desc,offset,count:CHUNK,deadline_ms:i.frame_deadline_unix_ms});
          need(row.offset===offset&&row.total_bytes===desc.bytes&&row.whole_file_sha256===desc.sha256,'ARGUMENT_CHUNK_BINDING');
          if(physical)need(same(physical,row.physical),'ARGUMENT_PHYSICAL_CHANGED');else physical=row.physical;
          const bytes=decode64(row.chunk_base64);need(bytes.length===row.count,'ARGUMENT_CHUNK_SIZE');parts.push(...bytes);
        }
        const raw=textBytes(parts);need(same(codec.descriptor(raw),desc),'COMPLETE_ARGUMENT_FILE');
        return {tool:i.tool,arguments:codec.strict(raw)};
      },
      respond:async(raw,descriptor)=>{need(integer(process)&&exit===undefined&&!last&&frameKind,'ONE_EPHEMERAL_RESPONSE_FRAME');
        need(Date.now()<selected.deadline_ms,'ORIGINAL_PROCESS_DEADLINE');
        last={descriptor,kind:frameKind};frameKind=null;await update(await tools.write_stdin({session_id:process,
          chars:String(utf8(raw).length)+'\n'+raw,yield_time_ms:1000,max_output_tokens:4000}));},
      observation:()=>({process_session_id:process,exit_code:exit??null,automatic_retry:false}),
    });
  }
  return Object.freeze({observeHost:()=>host('identity',{root:linux.journal_root}),observePublic,prepareSmokeBranch,
    sender,senderProcess,publish,consumeG3,framedProcess,endpoint,minimumRemainingMs:FLOOR,readyMarker:READY});
})
