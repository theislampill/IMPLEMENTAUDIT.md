"""Current7e2/R1 failed-finalize hooks; no controller, workflow or grant API."""
from pathlib import Path
import fs_protocol as P
import fs_carrier as R

PUBLIC_NAMES={'RESULT.json','HOST.json','SOURCE.json','PROBE.json','CLEANUP.json','FAILURE.json'}
PUBLIC_ADDITIONAL_BYTES={'FAILURE.json':1045,'CLEANUP.json':512}

def reserve_public_capacity(value):
    """Call on the original capacity result before either canonical leg.

    Charge supplementary fields explicitly. Preserve the original per-file,
    aggregate, encoded-line, log and 2,000-byte headroom limits.
    """
    P.exact(value,'schema authority base_bytes maximum_bytes raw_upper encoded_upper headroom remaining_failed_path_host_commands scope original_acceptance')
    P.need(value['schema']=='dg16.full-pair-failure-capacity.v1' and value['authority']=='NONE'
      and value['headroom']==2000 and value['remaining_failed_path_host_commands']==14
      and value['scope']=='CAPACITY_ONLY_NOT_OPERATION_EVIDENCE' and value['original_acceptance'] is False,
      'ORIGINAL_PUBLIC_CAPACITY_SCOPE')
    old=value['maximum_bytes']
    P.need(type(old) is dict and set(old)==PUBLIC_NAMES|{'ARTIFACT_MANIFEST.json'}
      and all(P.integer(v,0,65536) for v in old.values())
      and value['raw_upper']==sum(old.values()) and value['encoded_upper']==sum(2*v+256 for v in old.values()),
      'ORIGINAL_PUBLIC_CAPACITY_JOIN')
    maxima={name:size+PUBLIC_ADDITIONAL_BYTES.get(name,0) for name,size in old.items()}
    encoded={name:2*size+256 for name,size in maxima.items()}
    P.need(all(v<=65536-2000 for v in maxima.values()) and sum(maxima.values())<=262144-2000
      and max(encoded.values())<=262144-2000 and sum(encoded.values())<=1048576-2000,
      'PROTECTED_PUBLIC_CAPACITY_REFUSED')
    return dict(value,maximum_bytes=maxima,raw_upper=sum(maxima.values()),encoded_upper=sum(encoded.values()))

def validate_public_receipt(value,ctx):
    """Receive one bounded public status; it supplies no provider receipt."""
    P.context(ctx)
    base='schema authority status reason custody_scope provider_upload_confirmed original_acceptance crypto_child_custody'
    ready=type(value) is dict and value.get('status')=='ENCRYPTED_LOCAL_NOT_PROVIDER_RECEIVED'
    P.exact(value,base+(' artifact_role envelope ciphertext recipient_sha256 outcome' if ready else ''))
    P.need(len(P.encode(value))<=1024 and value['schema']=='dg16.protected-stream-public-status.v1'
      and value['authority']=='NONE' and value['custody_scope']==P.COPY_SCOPE
      and value['provider_upload_confirmed'] is False and value['original_acceptance'] is False,
      'PUBLIC_RETENTION_SCOPE')
    P.need(value['crypto_child_custody'] in ('NOT_STARTED','ECHILD','UNPROVED'),'PUBLIC_RETENTION_CUSTODY')
    if ready:
        P.descriptor(value['envelope'],P.ENVELOPE_MAX);P.descriptor(value['ciphertext'],P.CIPHER_MAX)
        P.need(value['reason'] is None and value['crypto_child_custody']=='ECHILD'
          and value['artifact_role']==P.artifact_name(ctx) and value['envelope']['bytes']>0
          and value['ciphertext']['bytes']>0 and P.digest(value['recipient_sha256'])
          and value['outcome'] in ('RETURNED_NONZERO','OWNER_RAISED','UNKNOWN'),'PUBLIC_RETENTION_READY_JOIN')
    else:
        P.need(value['status'] in ('REFUSED','INCOMPLETE','ENCRYPTION_FAILED')
          and type(value['reason']) is str and value['reason'] in R.PUBLIC_REASONS,'PUBLIC_RETENTION_DISPOSITION')
        if value['status']=='REFUSED':P.need(value['crypto_child_custody']!='UNPROVED','PUBLIC_RETENTION_UNKNOWN_CUSTODY')
        elif value['status']=='ENCRYPTION_FAILED':P.need(value['crypto_child_custody']=='ECHILD'
          and value['reason']=='CMS_ENCRYPTION_NONZERO','PUBLIC_RETENTION_ENCRYPTION_FAILURE')
        else:P.need(value['crypto_child_custody'] in ('ECHILD','UNPROVED'),'PUBLIC_RETENTION_INCOMPLETE_CUSTODY')
    return value

def add_public_receipt(state,result):
    docs=state['docs'];P.need(set(docs)==PUBLIC_NAMES and state['failed'] is True,'FAILED_PUBLIC_SCOPE')
    before={name:len(P.encode(docs[name])) for name in PUBLIC_ADDITIONAL_BYTES}
    # The artifact manifest is still synthesized by the unchanged public
    # emission owner. This never appends an eighth public summary body.
    receipt={k:result[k] for k in ('status','reason','artifact_role','envelope','ciphertext','recipient_sha256','outcome','crypto_child_custody') if k in result}
    receipt.update(schema='dg16.protected-stream-public-status.v1',authority='NONE',
      custody_scope=P.COPY_SCOPE,provider_upload_confirmed=False,original_acceptance=False)
    receipt.setdefault('crypto_child_custody','UNPROVED' if result['status']=='INCOMPLETE' else 'NOT_STARTED')
    receipt['reason']=None if result['status']=='ENCRYPTED_LOCAL_NOT_PROVIDER_RECEIVED' else R.reason(P.Refusal(result.get('reason')))
    # The existing R1 state deliberately has exactly these five hosted fields.
    # Source/workflow scope comes from this pinned component, never added to
    # or substituted into the original state context.
    P.exact(state['context'],'repository branch run_id run_attempt workflow_commit')
    ctx=dict(state['context'],source_commit=P.SOURCE_COMMIT,source_tree=P.SOURCE_TREE,
      workflow_path='.github/workflows/dg16-r5-full-g2.yml',job_name='full-registry-raw-pair')
    validate_public_receipt(receipt,ctx)
    docs['FAILURE.json']['protected_streams']=receipt
    cleanup=docs['CLEANUP.json']
    cleanup['private_outputs_uploaded_scope']='PLAINTEXT_PRIVATE_CAPTURE_BYTES'
    cleanup['private_outputs_uploaded']=False
    if result.get('crypto_child_custody','UNPROVED' if result['status']=='INCOMPLETE' else 'NOT_STARTED')=='UNPROVED':
        cleanup['all_step_children_reaped']=False
    cleanup['encrypted_diagnostic_copy']=result['status']
    cleanup['private_retention']='ORIGINAL_RAW_LIVE_JOB_ONLY; separate encrypted diagnostic copy requires provider receiving; no acceptance custody transfer'
    P.need(all(len(P.encode(docs[name]))-size<=PUBLIC_ADDITIONAL_BYTES[name] for name,size in before.items()),
      'PROTECTED_PUBLIC_CAPACITY_CHANGED')
    return receipt

def failed_finalize(state,output,selection,certificate_path,execute,read_projection,closing_deadline,current):
    """Call inside the existing failed finalize180s, before its finally/alarm10.

    Root's compile-bound loader supplies selection, executor, currentness and
    the existing read_failed_leg_observation callback. No runtime user policy
    or callback is selected from an archive, manifest or private stream.
    """
    original=P.encode({k:state['docs'][k] for k in ('RESULT.json','HOST.json','SOURCE.json','PROBE.json')})
    original_failures=P.encode(state['docs']['FAILURE.json']['failures'])
    result=R.neutral('REFUSED','RETENTION_COMPOSITION_UNBOUND')
    try:
        P.need(state['failed'] is True and type(selection) is dict,'FAILED_ROOT_SELECTION_REQUIRED')
        P.exact(selection,'schema context recipient root_receiving')
        P.need(selection['schema']=='dg16.protected-stream-root-selection.v1','ROOT_SELECTION_SCHEMA')
        P.descriptor(selection['root_receiving'],65536);P.need(selection['root_receiving']['bytes']>0,'ROOT_RECEIVING_REQUIRED')
        ctx=selection['context'];P.context(ctx)
        P.need(all(ctx[k]==state['context'][k] for k in ('repository','branch','run_id','run_attempt','workflow_commit')),'ACTUAL_STATE_CONTEXT_JOIN')
        P.need(state['docs']['CLEANUP.json']['all_step_children_reaped'] is True,'FAILED_PARENT_CUSTODY_REQUIRED')
        current();deadline=P.Deadline(state['deadline_monotonic'],closing_deadline)
        projection=read_projection();P.need(projection==state['docs']['FAILURE.json']['capture_observation'],'CURRENT_FAILED_PROJECTION_REQUIRED')
        result=R.protect(Path(output)/'private/full-pair',ctx,projection,certificate_path,selection['recipient'],execute,deadline,read_projection)
        current();deadline.check()
    except BaseException as exc:
        custody=result.get('crypto_child_custody','NOT_STARTED')
        result=R.neutral('INCOMPLETE' if custody=='UNPROVED' else 'REFUSED',R.reason(exc))
        result['crypto_child_custody']=custody
    P.need(P.encode({k:state['docs'][k] for k in ('RESULT.json','HOST.json','SOURCE.json','PROBE.json')})==original
      and P.encode(state['docs']['FAILURE.json']['failures'])==original_failures,'PRIMARY_OUTCOME_CHANGED')
    add_public_receipt(state,result)
    return result
