/* Fixed original control procedure, with actual tools and external original
 * effect authority. This module never issues a grant, review or consumption.
 * publish has three possible writes; receive has none. Unknown is terminal.
 */
(() => {
  'use strict';
  const need=(v,c)=>{if(!v)throw Error(c);};
  const object=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
  const exact=(v,n)=>object(v)&&Object.keys(v).sort().join('|')===n.slice().sort().join('|');
  const hex=(v,n=64)=>typeof v==='string'&&new RegExp('^[0-9a-f]{'+n+'}$').test(v)&&v!=='0'.repeat(n);
  const path=v=>typeof v==='string'&&v.startsWith('/')&&v.length<=4096&&!/[\x00-\x1f\x7f]/.test(v);
  const same=(C,a,b)=>C.canonical(a)===C.canonical(b);
  const quote=s=>"'"+s.replace(/'/g,"'\\''")+"'";
  const descriptor=v=>exact(v,['bytes','sha256'])&&Number.isSafeInteger(v.bytes)&&v.bytes>0&&hex(v.sha256);
  const NAMES=['CONTROL.json','INDEPENDENT_REVIEW.json','ROOT_CONSUMPTION.json'];
  const FETCH='mcp__codex_apps__github_fetch',TREE='mcp__codex_apps__github_create_tree',
    COMMIT='mcp__codex_apps__github_create_commit',BRANCH='mcp__codex_apps__github_create_branch';
  const CHANNEL='b7c087ce21761b01fa8b5d2e0fd8409f73a402469371511a4df4e92215018e7c';
  const JOURNAL='9cbac140ff23f1df36867a0eca5fe65c94fd3cea27f52292e094f59d9a4e36db';
  const BOOT="import hashlib,sys\nfrom pathlib import Path\np=Path(sys.argv[1]);raw=p.read_bytes()\nassert hashlib.sha256(raw).hexdigest()==sys.argv[2], 'EXACT_SELECTED_SOURCE_PIN'\nsys.argv=[str(p)]+sys.argv[3:]\nexec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})\n";
  const originalJSON=(C,v)=>JSON.stringify(C.strict(C.canonical(v)),null,2)+'\n';
  function complete(C,actual){
    need(object(actual)&&Object.keys(actual).every(k=>['content','structuredContent','isError','_meta'].includes(k))
      &&actual.isError===false,'COMPLETE_ACTUAL_TOOL_RESULT');
    const meta=actual._meta||{};need(object(meta)&&Object.keys(meta).every(k=>['truncated','isTruncated','partial','hasMore'].includes(k)&&meta[k]===false),'NO_PARTIAL_RESULT');
    const raw=JSON.stringify(actual);need(C.descriptor(raw).bytes<=4*1024*1024,'ORIGINAL_TOOL_RESULT_BOUND');
    return actual.structuredContent;
  }
  function read(C,actual,url,file=false){
    const s=complete(C,actual);
    need(object(s)&&Object.keys(s).every(k=>['content','title','modified_date','url','display_url','display_title','structuredContent'].includes(k))
      &&s.url===url&&s.display_url===url&&typeof s.content==='string','EXACT_FRESH_READ_ENDPOINT');
    if(s.structuredContent!==undefined){const n=s.structuredContent;
      need(object(n)&&Object.keys(n).every(k=>['content','title','display_url'].includes(k))&&n.content===s.content&&n.display_url===url,'NESTED_RESULT_CHANGED');}
    return file?s.content:C.strict(s.content);
  }
  function selected(C,input,mode){
    const s=C.strict(C.canonical(input));
    need(exact(s,['driver_source','source','journal_root','actor','context','preparation','grant','expires_ms','commit_message','publication_receipt'])
      &&descriptor(s.driver_source)&&path(s.journal_root),'EXACT_PUBLICATION_SELECTION');
    const x=s.source;need(exact(x,['channel_sha256','journal_path','journal_sha256','python_path','semantic_path','semantic_sha256'])
      &&x.channel_sha256===CHANNEL&&x.journal_sha256===JOURNAL&&hex(x.semantic_sha256)
      &&[x.journal_path,x.python_path,x.semantic_path].every(path),'PINNED_EXISTING_SOURCES');
    need(mode==='publish'?s.actor==='/root'&&s.publication_receipt===null&&typeof s.grant==='string'
      &&C.descriptor(s.grant).bytes>0&&C.descriptor(s.grant).bytes<=16384:
      /^\/root\/[a-z0-9_]+$/.test(s.actor)&&s.grant===null&&object(s.publication_receipt),'ACTUAL_ROLE_AND_ORIGINAL_GRANT_SELECTION');
    need(Number.isSafeInteger(s.expires_ms)&&Date.now()<s.expires_ms&&s.expires_ms<=Date.now()+300000
      &&typeof s.commit_message==='string'&&s.commit_message.length>0&&s.commit_message.length<=512,'CURRENT_BOUND_AND_EXACT_MESSAGE');
    const c=s.context,p=s.preparation;
    need(c.repository==='theislampill/IMPLEMENTAUDIT.md'&&/^pro\/dg16-r5-full-g2-direct-host-[0-9]+-[0-9]{8}$/.test(c.branch)
      &&typeof c.run_id==='string'&&/^[1-9][0-9]{0,15}$/.test(c.run_id)&&c.run_attempt===1
      &&['workflow_commit','workflow_tree','source_commit','source_tree'].every(k=>hex(c[k],40)),'EXACT_G221_CONTEXT');
    need(p.schema==='dg16.successor-public-semantic-outcome.v1'&&p.status==='LOCAL_CONTROL_PREPARATION_REQUIRES_SEPARATE_PUBLICATION_AUTHORITY'
      &&p.authority==='NONE'&&p.original_acceptance===false&&p.automatic_retry===false&&p.provider_effects===0
      &&p.source_sha256===x.semantic_sha256&&Number.isSafeInteger(p.expires_ms)&&Date.now()<p.expires_ms,
      'ACTUAL_PREPARATION_SELECTION_REQUIRED');
    const v=p.publication_inputs;need(exact(v,['request_raw','files','create_tree','publication_request','source_authors'])
      &&typeof v.request_raw==='string'&&C.descriptor(v.request_raw).bytes<=4096&&exact(v.files,NAMES)
      &&Array.isArray(v.source_authors)&&['/root','/root/dg16_contract_check'].every(a=>v.source_authors.includes(a)),
      'ORIGINAL_THREE_FILE_CONTROL_AND_SOURCE_AUTHORS');
    const r=C.strict(v.request_raw),q=v.publication_request,t=v.create_tree;
    need(exact(q,['schema','actor','branch','sole_parent','expected_tree','additions','run_id','run_attempt','request_sha256','proof_sha256',
      'independent_review_seal_sha256','expires_utc_epoch','automatic_retry','original_awards','admission'])
      &&q.schema==='dg16.current-g2.actual-live-control-publication-request.v1'&&q.actor==='/root'
      &&q.branch===c.branch.replace('-host-','-control-')&&q.sole_parent===c.workflow_commit&&hex(q.expected_tree,40)
      &&q.run_id===c.run_id&&q.run_attempt===1&&q.request_sha256===C.descriptor(v.request_raw).sha256
      &&q.proof_sha256===r.proof.sha256&&hex(q.independent_review_seal_sha256)&&q.expires_utc_epoch===r.expires_utc_epoch
      &&Number.isSafeInteger(q.expires_utc_epoch)&&q.automatic_retry===false&&same(C,q.original_awards,[])
      &&q.admission==='ROOT_MUST_PERSIST_EXACT_ONE_SHOT_EFFECT_GRANT_BEFORE_PROVIDER_WRITE','UNCHANGED_ORIGINAL_PUBLICATION_REQUEST');
    const checks=p.original_control_checks;
    need(object(checks)&&checks.status==='ORIGINAL_REVIEW_AND_ROOT_INPUT_CHECKS_PASSED_DATA_ONLY'
      &&checks.authority==='NONE'&&checks.original_acceptance===false&&checks.root_consumption_issued===false
      &&descriptor(checks.preparer_source)&&descriptor(checks.root_decision_input)&&descriptor(checks.final)
      &&checks.review_seal_sha256===q.independent_review_seal_sha256&&same(C,checks.review,p.prepared['INDEPENDENT_REVIEW.json'])
      &&checks.receiver_binding_sha256===p.receiver.binding_sha256&&checks.request_sha256===q.request_sha256
      &&checks.proof_sha256===q.proof_sha256,'ORIGINAL_REVIEW_AND_ROOT_INPUT_CHECKS_REQUIRED');
    need(r.hold_seconds===300&&r.expires_utc_epoch===r.created_utc_epoch+300
      &&r.control_branch===q.branch&&r.control_path==='qualification/dg16-full-g2-control/'+c.run_id+'-1'
      &&['repository','branch','run_id','workflow_commit','source_commit','source_tree'].every(k=>r[k]===c[k]),'ORIGINAL_LIVE_SUBJECT');
    need(same(C,p.prepared['PUBLICATION_REQUEST.json'],C.descriptor(originalJSON(C,q)))
      &&same(C,p.prepared['CreateTree.json'],C.descriptor(originalJSON(C,t)))
      &&exact(t,['repository_full_name','base_tree_sha','tree_elements'])&&t.repository_full_name===c.repository
      &&t.base_tree_sha===c.workflow_tree&&Array.isArray(q.additions)&&q.additions.length===3,'EXACT_PREPARED_OBJECTS');
    const elements=[],files={};
    for(const name of NAMES){const raw=v.files[name];need(typeof raw==='string'&&/^[\x00-\x7f]*$/.test(raw),'PUBLIC_ASCII_CONTROL_BODY');
      const d=C.descriptor(raw);need(d.bytes>0&&d.bytes<=4096&&same(C,p.prepared[name],d),'PREPARED_CONTROL_BYTES_CHANGED');
      C.strict(raw);files[name]=d;elements.push({path:r.control_path+'/'+name,mode:'100644',type:'blob',content:raw});
      const a=q.additions.find(a=>a.path===r.control_path+'/'+name);
      need(exact(a,['path','mode','git_blob','bytes','sha256'])&&a.mode==='100644'&&hex(a.git_blob,40)
        &&same(C,{bytes:a.bytes,sha256:a.sha256},d),'EXACT_ONLY_ORIGINAL_ADDITIONS');}
    need(same(C,t.tree_elements,elements),'EXACT_CREATE_TREE_ARGUMENTS');
    return{s,c,p,v,r,q,t,files};
  }
  async function run(C,input,admit,mode){
    let state=null,key=null,initial=null,index=0,started=false,writes=0,commit=null,deadline=null;
    const records=[];
    try{
      need(typeof admit==='function'&&typeof C?.canonical==='function'&&typeof tools!=='undefined'
        &&typeof tools.exec_command==='function'&&typeof tools[FETCH]==='function','REAL_TOOLS_AND_AUTHORITY_REQUIRED');
      state=selected(C,input,mode);const {s,c,p,v,r,q,t,files}=state;
      if(mode==='publish')need([TREE,COMMIT,BRANCH].every(n=>typeof tools[n]==='function'),'EXACT_CREATE_ONLY_TOOLS');
      const preparation=C.descriptor(C.canonical(p)),grant=mode==='publish'?C.descriptor(s.grant):null;
      deadline=Math.min(s.expires_ms,p.expires_ms,q.expires_utc_epoch*1000);
      if(mode==='receive'){
        const old=s.publication_receipt,unsigned={...old};delete unsigned.receipt_sha256;
        need(old.schema==='dg16.successor-control-publication-observation.v1'
          &&old.status==='CONTROL_PUBLISHED_REQUIRES_DISTINCT_RECEIVING_AND_SAME_JOB_CLOSING'&&old.actor==='/root'
          &&old.authority==='NONE'&&old.original_acceptance===false&&old.automatic_retry===false
          &&C.descriptor(C.canonical(unsigned)).sha256===old.receipt_sha256&&same(C,old.context,c)
          &&same(C,old.preparation,preparation)&&same(C,old.source,s.source)&&hex(old.commit,40), 'EXACT_PUBLISHER_RECEIPT');
        deadline=Math.min(deadline,old.expires_ms);commit=old.commit;
      }
      const bound={schema:'dg16.successor-control-operation-admission.v1',mode,input:s,original_effect_grant:grant,
        authority_issued:false,automatic_retry:false,original_acceptance:false};
      const frozen=C.canonical(bound),permit=await admit(bound);
      need(permit&&exact(permit.authorization,['ref','sha256'])&&typeof permit.authorization.ref==='string'
        &&permit.authorization.ref.length>0&&permit.authorization.ref.length<=512&&hex(permit.authorization.sha256)
        &&Number.isSafeInteger(permit.expires_ms)&&typeof permit.assertCurrent==='function'&&typeof permit.assertPrepared==='function',
        'EXTERNAL_ACTUAL_PREPARATION_AND_CURRENT_AUTHORITY');
      need(mode==='publish'?typeof permit.assertEffect==='function'&&same(C,permit.effect_grant,grant):
        typeof permit.assertIndependent==='function','ORIGINAL_EFFECT_OR_ACTUAL_INDEPENDENCE_REQUIRED');
      deadline=Math.min(deadline,permit.expires_ms);
      const current=async action=>{need(Date.now()<deadline&&C.canonical(bound)===frozen,'CONTROL_CHANGED_OR_EXPIRED');
        await permit.assertCurrent({bound,action});need(Date.now()<deadline&&C.canonical(bound)===frozen,'CONTROL_CHANGED_OR_EXPIRED');};
      await current('begin');await permit.assertPrepared({bound,preparation:p});await current('actual-preparation-received');
      if(mode==='receive'){await permit.assertIndependent({bound,publication_receipt:s.publication_receipt,receiver:s.actor});await current('actual-independence-received');}
      key=C.descriptor(C.canonical({repository:c.repository,branch:q.branch,run_id:c.run_id,run_attempt:1,
        workflow_commit:c.workflow_commit,actor:s.actor,mode:'control-'+mode})).sha256;
      const persist=async(action,value)=>{
        const args=[s.source.python_path,'-I','-B','-c',BOOT,s.source.journal_path,s.source.journal_sha256,s.journal_root,action,C.canonical(value)];
        const got=await tools.exec_command({cmd:args.map(quote).join(' '),login:false,shell:'/bin/bash',yield_time_ms:1000,max_output_tokens:1024});
        need(got.exit_code===0&&typeof got.output==='string'&&got.output.length<=8192,'CONTROL_DURABILITY_NOT_RECEIVED');
        const result=C.strict(got.output.trim());need(result.status==='PERSISTED_AND_READ_BACK'&&result.operation_key===key
          &&result.action===action&&descriptor(result.record),'CONTROL_DURABILITY_RECEIPT');return result.record;
      };
      state.persist=persist;
      initial=await persist('begin',{operation_key:key,schema:'dg16.successor-control-one-shot-intent.v1',authority:'NONE',
        actor:s.actor,mode,action_count:mode==='publish'?16:9,preparation,original_effect_grant:grant,
        authorization:permit.authorization,context:c,branch:q.branch,source:s.source,driver_source:s.driver_source,
        expires_ms:deadline,automatic_retry:false});started=true;await current('durable-begin-received');
      const invoke=async(tool,request,decode,effect=false)=>{
        const action={index,tool,request};await current(action);
        const intent=await persist('intent',{operation_key:key,initial,index,tool,request,issued_ms:Date.now(),authority:'NONE',automatic_retry:false});
        await current({...action,intent});
        if(effect){await permit.assertEffect({bound,original_effect_grant:grant,action,intent});await current({...action,effect_admission_received:true});writes++;}
        let actual=await tools[tool](request);await current({index,result_returned:true});
        const raw=JSON.stringify(actual);need(typeof raw==='string'&&C.descriptor(raw).bytes<=4*1024*1024,'BOUNDED_ACTUAL_RESULT');
        const projection=decode(actual);actual=null;
        const result=await persist('result',{operation_key:key,initial,index,intent,whole_actual_wrapper:C.descriptor(raw),
          projection_sha256:C.descriptor(C.canonical(projection)).sha256,observed_ms:Date.now(),authority:'NONE',raw_wrapper_retained:false});
        records.push({intent,result});index++;await current('durable-operation-result-received');return projection;
      };
      const base='https://api.github.com/repos/'+c.repository;
      const fetch=async(url,decode,file=false)=>invoke(FETCH,{url},a=>decode(read(C,a,url,file)));
      const host=()=>fetch(base+'/git/ref/heads/'+c.branch,x=>{need(x.ref==='refs/heads/'+c.branch&&x.object?.type==='commit'&&x.object.sha===c.workflow_commit,'HOST_REF_CHANGED');return{sha:x.object.sha};});
      const live=()=>fetch(base+'/actions/runs/'+c.run_id,x=>{need(x.id===Number(c.run_id)&&x.run_attempt===1&&x.head_sha===c.workflow_commit
        &&x.head_branch===c.branch&&x.event==='push'&&x.status==='in_progress'&&x.repository?.full_name===c.repository,'LIVE_RUN_CHANGED');return{status:x.status,run_id:c.run_id};});
      const absent=()=>fetch(base+'/git/matching-refs/heads/'+q.branch,x=>{need(Array.isArray(x)&&x.length===0,'CONTROL_REF_PRESENT_OR_AMBIGUOUS');return{matching_refs:0};});
      const ref=()=>fetch(base+'/git/ref/heads/'+q.branch,x=>{need(x.ref==='refs/heads/'+q.branch&&x.object?.type==='commit'&&x.object.sha===commit,'CONTROL_REF_CHANGED');return{sha:commit};});
      const commitRead=()=>fetch(base+'/git/commits/'+commit,x=>{need(x.sha===commit&&x.tree?.sha===q.expected_tree
        &&Array.isArray(x.parents)&&x.parents.length===1&&x.parents[0].sha===c.workflow_commit,'CONTROL_TREE_OR_SOLE_PARENT_CHANGED');return{sha:commit,tree:q.expected_tree,parent:c.workflow_commit};});
      if(mode==='publish'){
        await host();await live();await absent();
        await invoke(TREE,t,a=>{const x=complete(C,a);need(exact(x,['sha'])&&x.sha===q.expected_tree,'CREATED_TREE_CHANGED');return{sha:x.sha};},true);
        commit=await invoke(COMMIT,{repository_full_name:c.repository,tree_sha:q.expected_tree,parent_sha:c.workflow_commit,message:s.commit_message},
          a=>{const x=complete(C,a);need(exact(x,['sha'])&&hex(x.sha,40),'ACTUAL_COMMIT_SHA_REQUIRED');return x.sha;},true);
        await commitRead();await host();await live();await absent();
        await invoke(BRANCH,{repository_full_name:c.repository,branch_name:q.branch,sha:commit},
          a=>{const x=complete(C,a);need(exact(x,['branch'])&&x.branch===q.branch,'EXACT_CREATE_BRANCH_RESULT');return{branch:x.branch};},true);
      }
      await ref();await commitRead();const received={};
      for(const name of NAMES)received[name]=await fetch(base+'/contents/'+r.control_path+'/'+name+'?ref='+commit,
        raw=>{need(same(C,C.descriptor(raw),files[name])&&raw===v.files[name],'IMMUTABLE_CONTROL_BYTES_CHANGED');return raw;},true);
      await ref();
      if(mode==='receive'){
        await host();await live();
        const body={receiver:p.receiver,context:c,request_raw:v.request_raw,payload:received,source_authors:v.source_authors,expires_ms:deadline};
        const args=[s.source.python_path,'-I','-B','-c',BOOT,s.source.semantic_path,s.source.semantic_sha256,'--control-readback',C.canonical(body)];
        const sem=await invoke('exec_command',{cmd:args.map(quote).join(' '),login:false,shell:'/bin/bash',yield_time_ms:1000,max_output_tokens:4096},a=>{
          need(a.exit_code===0&&a.session_id===undefined&&typeof a.output==='string'&&a.output.length<=16384,'ORIGINAL_CONTROL_VALIDATOR_REQUIRED');
          const x=C.strict(a.output.trim());need(x.schema==='dg16.successor-public-control-readback.v1'&&x.authority==='NONE'
            &&x.original_acceptance===false&&x.review_issued===false&&x.root_consumption_issued===false&&x.decision==='CONSUME'
            &&same(C,x.request,C.descriptor(v.request_raw))&&same(C,x.files,files),'ORIGINAL_CONTROL_READBACK_CHANGED');return x;
        });need(sem.decision==='CONSUME','ORIGINAL_CONTROL_READBACK_REFUSED');
      }
      const result={schema:'dg16.successor-control-publication-observation.v1',
        status:mode==='publish'?'CONTROL_PUBLISHED_REQUIRES_DISTINCT_RECEIVING_AND_SAME_JOB_CLOSING':'CONTROL_BYTES_INDEPENDENTLY_RECEIVED_REQUIRES_SAME_JOB_CLOSING',
        authority:'NONE',actor:s.actor,context:c,source:s.source,preparation,commit,
        control_selection:{branch:q.branch,commit,tree:q.expected_tree,path:r.control_path,files},
        publisher_receipt_sha256:s.publication_receipt?.receipt_sha256||null,expires_ms:deadline,
        original_effect_grant:grant,provider_writes_invoked:writes,actual_independence_authenticated_externally:mode==='receive',
        same_job_closing_received:false,original_acceptance:false,automatic_retry:false};
      result.receipt_sha256=C.descriptor(C.canonical(result)).sha256;
      await current('finish');await persist('finish',{operation_key:key,initial,records,receipt:result});await current('final-durable-write-received');
      return result;
    }catch{
      const result={status:'REFUSED_OR_UNCERTAIN_NO_RETRY',authority:'NONE',provider_writes_invoked:writes,
        next_action:index,original_acceptance:false,automatic_retry:false};
      if(started&&state?.persist)try{await state.persist('unknown',{operation_key:key,initial,...result,status:'UNKNOWN_NO_RETRY'});}catch{result.journal_completion='UNKNOWN';}
      return result;
    }
  }
  return Object.freeze({publish:(C,input,admit)=>run(C,input,admit,'publish'),receive:(C,input,admit)=>run(C,input,admit,'receive')});
})()
