/* Evaluate these exact reviewed bytes in functions.exec with the real tools
 * capability. admit is the actual controlling capability, never JSON. It binds
 * loaded source, genuine receipt/body provenance and actual agent roles. No
 * record returned here grants acceptance, review, consumption or publication.
 */
(() => {
  'use strict';
  const need=(v,c)=>{if(!v)throw Error(c);};
  const object=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
  const exact=(v,names)=>object(v)&&Object.keys(v).sort().join('|')===names.slice().sort().join('|');
  const hex=v=>typeof v==='string'&&/^[0-9a-f]{64}$/.test(v)&&v!=='0'.repeat(64);
  const path=v=>typeof v==='string'&&v.startsWith('/')&&v.length<=4096&&!/[\x00-\x1f\x7f]/.test(v);
  const descriptor=v=>exact(v,['bytes','sha256'])&&Number.isSafeInteger(v.bytes)&&v.bytes>0&&hex(v.sha256);
  const quote=s=>"'"+s.replace(/'/g,"'\\''")+"'";
  const same=(C,a,b)=>C.canonical(a)===C.canonical(b);
  const CHANNEL='b7c087ce21761b01fa8b5d2e0fd8409f73a402469371511a4df4e92215018e7c';
  const JOURNAL='9cbac140ff23f1df36867a0eca5fe65c94fd3cea27f52292e094f59d9a4e36db';
  const BOOT="import hashlib,sys\nfrom pathlib import Path\np=Path(sys.argv[1]);raw=p.read_bytes()\nassert hashlib.sha256(raw).hexdigest()==sys.argv[2], 'SEMANTIC_SOURCE_PIN'\nsys.argv=[str(p)]+sys.argv[3:]\nexec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})\n";
  function receipt(C,r,independent){
    need(object(r),'RECEIPT_REQUIRED');const value={...r};delete value.receipt_sha256;
    need(hex(r.receipt_sha256)&&C.descriptor(C.canonical(value)).sha256===r.receipt_sha256,'RECEIPT_CHANGED');
    need(r.schema==='dg16.github-public-provider-observation.v1'&&r.operator==='PRO-EXECUTOR-01'
      &&r.successor==='PRO-EXECUTOR-01, designated by owner'&&r.authority==='NONE'
      &&r.original_acceptance===false&&r.private_or_cipher===false&&r.automatic_retry===false
      &&['SOURCE_QUALIFICATION','OWNER_APPROVED_ORIGINAL_ROUTE'].includes(r.purpose),'PUBLIC_RECEIPT_SCOPE');
    need(r.source.channel_sha256===CHANNEL&&r.source.journal_sha256===JOURNAL&&path(r.source.python_path)
      &&same(C,r.public_metadata,r.facts.public_metadata),'REVIEWED_CHANNEL_REQUIRED');
    need(['observed_start_ms','observed_end_ms','expires_ms'].every(k=>Number.isSafeInteger(r[k]))
      &&r.observed_start_ms<=r.observed_end_ms&&r.observed_end_ms<=Date.now()&&Date.now()<r.expires_ms
      &&r.expires_ms<=r.observed_start_ms+300000,'CURRENT_RECEIPT_REQUIRED');
    need(independent?r.status==='INDEPENDENT_PROVIDER_FACTS_MATCH_ONLY'&&/^\/root\/[a-z0-9_]+$/.test(r.actor):
      r.status==='PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING'&&r.actor==='/root','ACTUAL_ROLE_SELECTION');
  }
  function join(C,operator,independent){
    receipt(C,independent,true);
    need(independent.independent_operator_receipt_sha256===operator.receipt_sha256
      &&operator.observed_end_ms<=independent.observed_start_ms
      &&['purpose','role','source','context','facts','public_metadata','control_selection'].every(k=>same(C,operator[k],independent[k])),
      'INDEPENDENT_RECEIVING_CHANGED');
  }
  async function run(C,input,admit,mode){
    let process=null,logInvoked=false,frameSent=false,independent=null,operator=null;
    try{
      need(typeof admit==='function'&&typeof C?.receive==='function'&&typeof C.createActionValidator==='function'
        &&typeof tools!=='undefined'&&typeof tools.exec_command==='function'&&typeof tools.write_stdin==='function',
        'ACTUAL_HOST_CAPABILITIES_REQUIRED');
      const selected=C.strict(C.canonical(input));
      need(exact(selected,mode==='receive'?['driver_source','selection','operator_receipt','body_outcome','receiver','semantic_source']:
        ['driver_source','operator_receipt','independent_receipt','body_outcome','receiver','semantic_source','expires_ms','control']),
        'EXACT_SESSION_SELECTION');
      need(descriptor(selected.driver_source),'ACTUALLY_LOADED_DRIVER_SOURCE_REQUIRED');
      operator=selected.operator_receipt;receipt(C,operator,false);
      need(operator.context.repository==='theislampill/IMPLEMENTAUDIT.md'&&['live','terminal'].includes(operator.role),'G221_ONLY');
      const source=selected.semantic_source,receiver=selected.receiver,body=selected.body_outcome;
      need(exact(source,['path','sha256','journal_parent'])&&path(source.path)&&hex(source.sha256)&&path(source.journal_parent),'EXACT_SEMANTIC_SOURCE');
      need(exact(receiver,['directory','receiver_sha256','seal_sha256','binding_sha256','runtime_sha256'])
        &&path(receiver.directory)&&Object.keys(receiver).filter(k=>k!=='directory').every(k=>hex(receiver[k])),'EXACT_BOUND_RECEIVER');
      const artifact=operator.public_metadata.artifact;
      need(body.status==='EXACT_PUBLIC_BODY_RECEIVED'&&body.authority==='NONE'&&body.operator==='PRO-EXECUTOR-01'
        &&body.provider_receipt_sha256===operator.receipt_sha256&&body.purpose===operator.purpose
        &&same(C,body.archive,{bytes:artifact.size_in_bytes,sha256:artifact.digest.slice(7)})&&path(body.journal_path)
        &&body.body_get_attempts===1&&body.signed_url_retained===false&&body.automatic_retry===false
        &&body.original_acceptance===false,'EXACT_ACQUIRED_PUBLIC_ARCHIVE');
      let deadline,actionCheck=null,control=null,controlFrame=null;
      if(mode==='receive'){
        const spec=selected.selection;actionCheck=C.createActionValidator(spec);
        need(/^\/root\/[a-z0-9_]+$/.test(spec.actor)&&spec.purpose===operator.purpose
          &&same(C,spec.context,operator.context)&&same(C,spec.source,operator.source)&&same(C,spec.control,operator.control_selection)
          &&spec.role===operator.role,'EXACT_DISTINCT_RECEIVER_SELECTION');
        deadline=Math.min(operator.expires_ms,spec.expires_ms);
        if(operator.role==='terminal')need(typeof tools.mcp__codex_apps__github_fetch_workflow_job_logs==='function','ACTUAL_LOG_TOOL_REQUIRED');
      }else{
        independent=selected.independent_receipt;join(C,operator,independent);
        need(operator.role==='live'&&Number.isSafeInteger(selected.expires_ms),'LIVE_CONTROL_ONLY');
        deadline=Math.min(operator.expires_ms,independent.expires_ms,selected.expires_ms);
        need(exact(selected.control,['frame','leaves_path','leaves'])&&path(selected.control.leaves_path)
          &&descriptor(selected.control.leaves),'EXACT_CONTROL_INPUTS');
        const frame=selected.control.frame;
        need(exact(frame,['payload','source_authors','review_seal_sha256','root_decision_input'])&&object(frame.payload)
          &&Object.values(frame.payload).every(v=>typeof v==='string')&&Array.isArray(frame.source_authors),
          'SEPARATELY_AUTHORED_CONTROL_BODIES_REQUIRED');
        controlFrame=C.canonical(frame);need(C.descriptor(controlFrame).bytes<=65536,'BOUNDED_CONTROL_FRAME');
        control={frame_sha256:C.descriptor(controlFrame).sha256,leaves_path:selected.control.leaves_path,leaves:selected.control.leaves};
      }
      need(Date.now()<deadline,'PARENT_DEADLINE_EXPIRED');
      const bound={schema:'dg16.successor-public-semantic-admission.v1',mode,input:selected,
        operation:mode==='receive'?'DISTINCT_PUBLIC_FACTS_AND_ORIGINAL_SEMANTICS':'LOCAL_CONTROL_PREPARATION_FROM_SEPARATELY_AUTHORED_DECISIONS',
        private_or_cipher:false,publication:false,automatic_retry:false,original_acceptance:false};
      const frozen=C.canonical(bound),permit=await admit(bound);
      need(permit&&typeof permit.assertCurrent==='function'&&exact(permit.authorization,['ref','sha256'])
        &&typeof permit.authorization.ref==='string'&&permit.authorization.ref.length>0&&permit.authorization.ref.length<=512
        &&hex(permit.authorization.sha256),'EXTERNAL_CURRENT_AUTHORITY_REQUIRED');
      need(mode==='receive'?typeof permit.assertIndependent==='function':typeof permit.assertControl==='function',
        'ACTUAL_DISTINCT_OR_ROOT_CONTROL_CAPABILITY_REQUIRED');
      const current=async action=>{
        need(Date.now()<deadline&&C.canonical(bound)===frozen,'ADMISSION_CHANGED_OR_EXPIRED');
        await permit.assertCurrent({bound,action});
        need(Date.now()<deadline&&C.canonical(bound)===frozen,'ADMISSION_CHANGED_OR_EXPIRED');
      };
      await current('begin');
      if(mode==='receive'){
        const spec=selected.selection;
        const scope={operator:spec.operator,actor:spec.actor,purpose:spec.purpose,source:spec.source,context:spec.context,
          control:spec.control,role:spec.role,journal_root:spec.journal_root,operation_id:spec.operation_id,expires_ms:spec.expires_ms,
          selection_sha256:C.descriptor(C.canonical(spec)).sha256,previous_receipt_sha256:operator.receipt_sha256};
        independent=await C.receive(operator,spec,{admit:async value=>{
          need(same(C,value,scope),'EXACT_FRESH_RECEIVING_SCOPE');await current('metadata-admission');
          return{authorization:permit.authorization,assertCurrent:async value=>{
            const actual={...value};delete actual.action;need(same(C,actual,scope),'METADATA_SCOPE_CHANGED');
            actionCheck(value.action);await current({metadata_action:value.action});
          },assertIndependent:async value=>{
            need(same(C,value,{operator_receipt:operator,receiver:spec.actor,scope}),'EXACT_INDEPENDENCE_REQUEST');
            await permit.assertIndependent({bound,...value});await current('actual-independence-received');
          }};
        }});
        join(C,operator,independent);deadline=Math.min(deadline,independent.expires_ms);
      }else{
        // This callback authenticates actual live review and separate Root
        // consumption for these exact existing bytes. Labels never create them.
        await permit.assertControl({bound,operator_receipt:operator,independent_receipt:independent});
        await current('actual-root-control-inputs-received');
      }
      await current('semantic-process-start');
      const runtime={mode,actor:mode==='receive'?independent.actor:'/root',source_sha256:source.sha256,
        operator_receipt:operator,independent_receipt:independent,body_outcome:body,receiver,
        journal_parent:source.journal_parent,authorization_sha256:permit.authorization.sha256,expires_ms:deadline,control};
      const rawInput=C.canonical(runtime);need(C.descriptor(rawInput).bytes<=65536,'BOUNDED_SEMANTIC_SELECTION');
      const args=[operator.source.python_path,'-I','-B','-c',BOOT,source.path,source.sha256,rawInput];
      const started=await tools.exec_command({cmd:args.map(quote).join(' '),login:false,shell:'/bin/bash',tty:true,
        yield_time_ms:1000,max_output_tokens:1024});
      process=started.session_id;
      need(Number.isSafeInteger(process)&&started.exit_code===undefined
        &&started.output==='READY_FOR_EPHEMERAL_DOWNLOAD_RESULT_LENGTH_FRAME\r\n','ORIGINAL_GATE_AND_DURABLE_INTENT_NOT_RECEIVED');
      let raw;
      if(mode==='receive'&&operator.role==='terminal'){
        const job=independent.facts.job;
        need(Number.isSafeInteger(job.id)&&job.id>0&&job.run_id===Number(operator.context.run_id)
          &&job.run_attempt===1&&job.head_sha===operator.context.workflow_commit&&job.name==='full-registry-raw-pair'
          &&job.status==='completed','EXACT_TERMINAL_JOB');
        const request={repo_full_name:operator.context.repository,job_id:job.id};
        await current({job_log_request:request});logInvoked=true;
        let actual=await tools.mcp__codex_apps__github_fetch_workflow_job_logs(request);
        await current('actual-job-log-returned');raw=JSON.stringify(actual);actual=null;
      }else raw=mode==='control'?controlFrame:'{}';
      const frame=C.descriptor(raw);need(frame.bytes>0&&frame.bytes<=4*1024*1024,'INHERITED_TOOL_WRAPPER_BOUND');
      await current({ephemeral_frame:frame});frameSent=true;
      let reply=await tools.write_stdin({session_id:process,chars:String(frame.bytes)+'\n'+raw,
        yield_time_ms:1000,max_output_tokens:8192});raw=null;
      let output=reply.output||'';
      while(reply.session_id!==undefined){
        need(reply.session_id===process&&output.length<=65536,'BOUNDED_SAME_PROCESS');
        await current('same-semantic-process-observation');
        reply=await tools.write_stdin({session_id:process,chars:'',yield_time_ms:1000,max_output_tokens:8192});
        output+=reply.output||'';
      }
      process=null;
      need(reply.exit_code===0&&output.length<=65536,'SEMANTIC_PROCESS_REFUSED_OR_UNCERTAIN');
      const outcome=C.strict(output.trim());
      const status=mode==='receive'?'PUBLIC_SEMANTIC_RECEIVING_COMPLETE_DATA_ONLY':'LOCAL_CONTROL_PREPARATION_REQUIRES_SEPARATE_PUBLICATION_AUTHORITY';
      need(outcome.schema==='dg16.successor-public-semantic-outcome.v1'&&outcome.status===status
        &&outcome.authority==='NONE'&&outcome.original_acceptance===false&&outcome.automatic_retry===false
        &&outcome.operator_receipt_sha256===operator.receipt_sha256&&outcome.independent_receipt_sha256===independent.receipt_sha256
        &&outcome.source_sha256===source.sha256&&same(C,outcome.receiver,receiver)&&same(C,outcome.frame,frame)
        &&outcome.external_authority_and_actual_distinct_agent_required===true,'EXACT_DATA_ONLY_SEMANTIC_RESULT');
      // The pinned semantic helper may tighten the parent deadline to the
      // original live REQUEST expiry. Adopt it before any final async callback.
      need(Number.isSafeInteger(outcome.expires_ms)&&outcome.expires_ms<=deadline,'EXACT_SEMANTIC_DEADLINE');
      deadline=outcome.expires_ms;
      await current('semantic-process-completed');
      if(mode==='control')need(outcome.provider_effects===0&&object(outcome.prepared),'NO_CONTROL_PUBLICATION');
      else need(outcome.observation?.authority==='NONE'&&outcome.observation.original_acceptance===false
        &&outcome.observation.review_issued===false&&outcome.observation.root_consumption_issued===false
        &&(operator.role!=='terminal'||outcome.observation.terminal_log_join?.all_seven_exact===true),'ORIGINAL_SEMANTIC_OBSERVATION');
      await current('semantic-outcome-received');
      return{status,authority:'NONE',independent_receipt:independent,semantic_outcome:outcome,
        original_acceptance:false,publication:false,automatic_retry:false,
        external_authority_and_actual_distinct_agent_required:true};
    }catch{
      return{status:'REFUSED_OR_UNCERTAIN_NO_RETRY',authority:'NONE',operator_receipt_sha256:operator?.receipt_sha256||null,
        independent_receipt_sha256:independent?.receipt_sha256||null,pending_process_id:process,
        job_log_tool_invoked:logInvoked,ephemeral_frame_sent:frameSent,original_acceptance:false,publication:false,automatic_retry:false};
    }
  }
  return Object.freeze({receive:(C,input,admit)=>run(C,input,admit,'receive'),
    prepareControl:(C,input,admit)=>run(C,input,admit,'control')});
})()
