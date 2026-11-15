/* Evaluate only after independent source/pin receiving. The caller is the actual
 * entitled controller; `admit` is its live authority capability, never JSON.
 * This acquisition session is read-only at GitHub. It grants no acceptance,
 * publication, private operation, recipient use, proof review or Root consumption.
 */
(() => {
  'use strict';
  const need=(v,c)=>{if(!v)throw Error(c);};
  const quote=s=>"'"+s.replace(/'/g,"'\\''")+"'";
  const same=(C,a,b)=>C.canonical(a)===C.canonical(b);
  const BOOT="import hashlib,sys\nfrom pathlib import Path\np=Path(sys.argv[1]);raw=p.read_bytes()\nassert hashlib.sha256(raw).hexdigest()==sys.argv[2], 'BODY_SOURCE_PIN'\nsys.argv=[str(p)]+sys.argv[3:]\nexec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})\n";
  return async function acquire(C, selection, bodySource, admit) {
    let process=null,downloadStarted=false,frameSent=false,operator=null;
    try {
      need(typeof admit==='function'&&typeof C?.collect==='function'
        &&typeof C.createActionValidator==='function','ACTUAL_ADMISSION_AND_REVIEWED_CHANNEL_REQUIRED');
      need(selection.actor==='/root'&&selection.operator==='PRO-EXECUTOR-01','SUCCESSOR_ROOT_ONLY');
      need(Object.keys(bodySource).sort().join('|')==='journal_parent|path|sha256'
        &&typeof bodySource.path==='string'&&bodySource.path.startsWith('/')
        &&typeof bodySource.journal_parent==='string'&&bodySource.journal_parent.startsWith('/')
        &&/^[0-9a-f]{64}$/.test(bodySource.sha256),'EXACT_BODY_SOURCE');
      const bound={schema:'dg16.successor-acquisition-admission.v1',selection,body_source:bodySource,
        operation:'READ_ONLY_PUBLIC_METADATA_AND_ONE_PUBLIC_ARCHIVE',private_or_cipher:false,
        automatic_retry:false,publication:false,original_acceptance:false};
      // The actual owner/controller must bind this complete selected operation.
      // Receipt fields, caller labels and matching bytes do not create the grant.
      const permit=await admit(bound);
      need(permit&&typeof permit.assertCurrent==='function'
        &&typeof permit.authorization?.ref==='string'
        &&/^[0-9a-f]{64}$/.test(permit.authorization?.sha256),'EXTERNAL_CURRENT_AUTHORITY_REQUIRED');
      const selected=C.canonical(bound);
      const current=async action=>{
        need(Date.now()<selection.expires_ms,'ACQUISITION_EXPIRED');
        await permit.assertCurrent({bound,action});
        need(C.canonical(bound)===selected&&Date.now()<selection.expires_ms,'ADMISSION_CHANGED_OR_EXPIRED');
      };
      const expectedScope={operator:selection.operator,actor:selection.actor,purpose:selection.purpose,
        source:selection.source,context:selection.context,control:selection.control,role:selection.role,
        journal_root:selection.journal_root,operation_id:selection.operation_id,expires_ms:selection.expires_ms,
        selection_sha256:C.descriptor(C.canonical(selection)).sha256,previous_receipt_sha256:null};
      const actionCheck=C.createActionValidator(selection);
      operator=await C.collect(selection,{admit:async scope=>{
        need(same(C,scope,expectedScope),'EXACT_METADATA_SCOPE');await current('metadata-admission');
        return {authorization:permit.authorization,assertCurrent:async value=>{
          const copy={...value};delete copy.action;need(same(C,copy,expectedScope),'METADATA_SCOPE_CHANGED');
          actionCheck(value.action);await current({metadata_action:value.action});
        }};
      }});
      need(operator.status==='PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING',
        'METADATA_NOT_RECEIVED_NO_BODY');
      await current('body-process-start');
      const input={receipt:operator,journal_parent:bodySource.journal_parent,
        authorization_sha256:permit.authorization.sha256};
      const args=[selection.source.python_path,'-I','-B','-c',BOOT,bodySource.path,
        bodySource.sha256,C.canonical(input)];
      const started=await tools.exec_command({cmd:args.map(quote).join(' '),login:false,
        shell:'/bin/bash',tty:true,yield_time_ms:1000,max_output_tokens:1024});
      process=started.session_id;
      need(Number.isSafeInteger(process)&&started.exit_code===undefined
        &&started.output==='READY_FOR_EPHEMERAL_DOWNLOAD_RESULT_LENGTH_FRAME\r\n',
        'DURABLE_DOWNLOAD_INTENT_NOT_RECEIVED');
      const artifact=operator.public_metadata.artifact;
      const request={repo_full_name:selection.context.repository,artifact_id:artifact.id,
        file_name:artifact.name+'.zip'};
      await current({download_request:request});
      downloadStarted=true;
      let actual=await tools.mcp__codex_apps__github_download_workflow_artifact(request);
      await current({download_returned:true});
      let raw=JSON.stringify(actual);actual=null;
      const descriptor=C.descriptor(raw);
      need(descriptor.bytes>0&&descriptor.bytes<=4*1024*1024,'ACTUAL_DOWNLOAD_WRAPPER_BOUND');
      await current({ephemeral_frame:descriptor});
      frameSent=true;
      let reply=await tools.write_stdin({session_id:process,
        chars:String(descriptor.bytes)+'\n'+raw,yield_time_ms:1000,max_output_tokens:8192});
      raw=null;
      // Poll only this same process. No repeated provider call or repeated frame.
      let safeOutput=reply.output||'';
      while(reply.session_id!==undefined){
        await current('same-body-process-observation');
        reply=await tools.write_stdin({session_id:process,chars:'',yield_time_ms:1000,max_output_tokens:8192});
        safeOutput+=reply.output||'';need(safeOutput.length<=65536,'BOUNDED_SAFE_BODY_OUTPUT');
      }
      process=null;
      await current('body-process-completed');
      need(reply.exit_code===0,'BODY_REFUSED_OR_UNCERTAIN');
      const outcome=C.strict(safeOutput.trim());
      need(outcome.status==='EXACT_PUBLIC_BODY_RECEIVED'&&outcome.original_acceptance===false
        &&outcome.body_get_attempts===1&&outcome.signed_url_retained===false
        &&outcome.provider_receipt_sha256===operator.receipt_sha256
        &&same(C,outcome.archive,{bytes:artifact.size_in_bytes,sha256:artifact.digest.slice(7)}),
        'EXACT_PUBLIC_BODY_OUTCOME_REQUIRED');
      return {status:'PUBLIC_ACQUISITION_REQUIRES_DISTINCT_AND_SEMANTIC_RECEIVING',authority:'NONE',
        operator_receipt:operator,body_outcome:outcome,original_acceptance:false,
        independent_receiving:'DISTINCT_ACTUAL_AGENT_REQUIRED',
        semantic_receiving:'UNCHANGED_BOUND_PUBLIC_RECEIVER_INSPECT_REQUIRED',
        protected_effects:false,automatic_retry:false};
    } catch {
      // No arbitrary exception text, result wrapper or URL may escape. An open
      // process has its own <=45s watchdog; observing it is not permission to retry.
      return {status:'REFUSED_OR_UNCERTAIN_NO_RETRY',authority:'NONE',
        operator_receipt_sha256:operator?.receipt_sha256||null,
        pending_process_id:process,download_tool_invoked:downloadStarted,
        ephemeral_frame_sent:frameSent,signed_url_retained:false,
        original_acceptance:false,automatic_retry:false};
    }
  };
})()
