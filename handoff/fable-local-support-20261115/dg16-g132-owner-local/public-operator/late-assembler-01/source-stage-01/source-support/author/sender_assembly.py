"""Late, separate Pro sender assembly. Pure bytes and ordinary files only.

Root supplies actual future recipient archive, operation, admission and its
exact host-publication receiving selection. The existing immutable host tree
and manifest never change. Actual sender execution/provider custody is separate.
"""
import io,json,re,zipfile
from pathlib import Path
import compose as C

def unpack(raw):
 C.need(type(raw) is bytes and 0<len(raw)<=65536,'SENDER_ARTIFACT_BOUND')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  infos=z.infolist();C.need(len(infos)==2 and {i.filename for i in infos}=={'REQUEST.json','RECIPIENT.pem'},'SENDER_ARTIFACT_POPULATION');out={}
  for row in infos:
   mode=(row.external_attr>>16)&0o170000
   C.need(not row.is_dir() and 0<row.file_size<=8192 and mode in (0,0o100000) and not row.flag_bits&1 and row.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED),'SENDER_ARTIFACT_MEMBER')
   raw=z.read(row);C.need(len(raw)==row.file_size,'SENDER_ARTIFACT_CRC');out[row.filename]=raw
  return out

def assemble(host,inputs):
 names={'ROOT_SENDER_ASSEMBLY_SELECTION.json','PRO_SENDER_OPERATION.json','PRO_SENDER_ADMISSION.json','ROOT_REQUEST_ARTIFACT.zip','HOST_PUBLICATION_ROOT_RECEIVING.json'}
 C.need(set(inputs)==names|{'private-inputs/'+n for n in C.RETAINED|C.PLACEMENT}|{'private-inputs/'+n for n in C.ROLES.values()},'SENDER_ACTUAL_INPUT_POPULATION')
 selected=C.parse(inputs['ROOT_SENDER_ASSEMBLY_SELECTION.json']);prefix='tree/'+C.W.CORE+'/';packet={n[len(prefix):]:b for n,b in host.items() if n.startswith(prefix)}
 binding=C.parse(packet['carrier/CARRIER_COMPOSITION.json']);index=C.parse(packet['carrier/INPUT_INDEX.json']);operation_raw=inputs['PRO_SENDER_OPERATION.json'];op=C.parse(operation_raw);archive=inputs['ROOT_REQUEST_ARTIFACT.zip'];files=unpack(archive);q=C.parse(files['REQUEST.json'])
 C.need(type(selected) is dict and set(selected)=={'schema','issuer','fixed_packet_directory','source_commit','source_tree','workflow_commit','workflow_branch','workflow_path','workflow_sha256','public_manifest_sha256','bootstrap_admission_sha256','carrier_binding_sha256','input_index_sha256','artifact_id','artifact','request_sha256','actual_host_receiving_sha256','original_awards'},'SENDER_ROOT_SELECTION_FIELDS')
 C.need(selected['schema']=='dg16.late-root-sender-assembly-selection.v1' and selected['issuer']=='R5_ROOT_GOVERNOR' and selected['original_awards']==[],'SENDER_ROOT_SELECTION_SCOPE')
 path=selected['fixed_packet_directory'];C.need(type(path) is str and Path(path).is_absolute() and str(Path(path))==path and '..' not in Path(path).parts and Path(path).name=='packet','SENDER_FIXED_PACKET_DIRECTORY')
 C.need(type(selected['actual_host_receiving_sha256']) is str and re.fullmatch('[0-9a-f]{64}',selected['actual_host_receiving_sha256']),'ACTUAL_HOST_RECEIVING_REQUIRED')
 C.need(C.sha(inputs['HOST_PUBLICATION_ROOT_RECEIVING.json'])==selected['actual_host_receiving_sha256'],'ACTUAL_HOST_RECEIVING_BODY_PIN')
 C.need(type(selected['workflow_commit']) is str and re.fullmatch('[0-9a-f]{40}',selected['workflow_commit']),'SENDER_ACTUAL_WORKFLOW_COMMIT')
 C.need(selected['source_commit']==C.SOURCE and selected['source_tree']==C.TREE and selected['workflow_branch']==binding['branch'] and selected['workflow_path']==binding['workflow_path'] and selected['workflow_sha256']==C.sha(host['tree/'+C.W.WORKFLOW])==binding['workflow_sha256'] and selected['public_manifest_sha256']==C.sha(host['PUBLIC_PACKET_MANIFEST.json']) and selected['bootstrap_admission_sha256']==C.sha(host['tree/'+C.W.ENTRY+'/BOOTSTRAP_ADMISSION.json']) and selected['carrier_binding_sha256']==C.sha(packet['carrier/CARRIER_COMPOSITION.json']) and selected['input_index_sha256']==C.sha(packet['carrier/INPUT_INDEX.json']) and selected['artifact']==C.desc(archive) and selected['request_sha256']==C.sha(files['REQUEST.json']),'SENDER_EXACT_HOST_ARTIFACT_JOIN')
 C.need(type(selected['artifact_id']) is int and 0<selected['artifact_id']<=10**20,'SENDER_ARTIFACT_ID')
 context=dict(repository=binding['repository'],branch=binding['branch'],workflow_commit=selected['workflow_commit'],workflow_path=binding['workflow_path'],run_id=q.get('run_id'),run_attempt=1,job_name=binding['job_name'])
 C.need(type(context['run_id']) is str and re.fullmatch('[1-9][0-9]{0,19}',context['run_id']),'SENDER_RUN_ID')
 for key in ('issued_unix_ms','expires_unix_ms'):C.need(type(q.get(key)) is int,'SENDER_REQUEST_TIME')
 C.need(0<=q['issued_unix_ms']<q['expires_unix_ms']<=q['issued_unix_ms']+600000 and type(q.get('nonce')) is str and re.fullmatch('[0-9a-f]{64}',q['nonce']),'SENDER_REQUEST_TIME_NONCE')
 expected=dict(schema='dg16.core-private-recipient-request.v1',authority='NONE',component_scope=binding['component_scope'],source_commit=C.SOURCE,source_tree=C.TREE,**context,input_index_sha256=selected['input_index_sha256'],input_count=len(index),input_bytes=sum(r['bytes'] for r in index.values()),recipient_sha256=C.sha(files['RECIPIENT.pem']),nonce=q['nonce'],issued_unix_ms=q['issued_unix_ms'],expires_unix_ms=q['expires_unix_ms'],automatic_retry=False,original_awards=[])
 C.need(files['REQUEST.json']==C.encode(expected),'SENDER_EXACT_REQUEST')
 C.need(type(op) is dict and set(op)=={'schema','context','source_commit','source_tree','carrier_binding_sha256','input_index_sha256','artifact_id','artifact','nonce','issued_unix_ms','expires_unix_ms','sender_uid','sender_gid','original_awards'},'SENDER_OPERATION_FIELDS')
 C.need(op['schema']=='dg16.pro-private-sender-operation.v1' and op['context']==context and type(op['context']['run_attempt']) is int and op['source_commit']==C.SOURCE and op['source_tree']==C.TREE and op['carrier_binding_sha256']==selected['carrier_binding_sha256'] and op['input_index_sha256']==selected['input_index_sha256'] and type(op['artifact_id']) is int and op['artifact_id']==selected['artifact_id'] and op['artifact']==selected['artifact'] and op['original_awards']==[],'SENDER_ACTUAL_OPERATION_JOIN')
 C.need(type(op['nonce']) is str and re.fullmatch('[0-9a-f]{64}',op['nonce']) and type(op['sender_uid']) is int and op['sender_uid']>0 and type(op['sender_gid']) is int and op['sender_gid']>=0,'SENDER_OPERATION_IDENTITY')
 C.need(type(op['issued_unix_ms']) is int and type(op['expires_unix_ms']) is int and q['issued_unix_ms']<=op['issued_unix_ms']<op['expires_unix_ms']<=min(q['expires_unix_ms'],op['issued_unix_ms']+binding['limits']['acquisition_seconds']*1000),'SENDER_OPERATION_INTERVAL')
 sender=C.parse(packet['carrier/PRO_SENDER_COMPOSITION.json']);admission_raw=inputs['PRO_SENDER_ADMISSION.json']
 expected=dict(schema='dg16.pro-private-sender-root-admission.v1',issuer='R5_ROOT_GOVERNOR',operation_sha256=C.sha(operation_raw),capture_profile=sender['capture_profile'],provider_profile=sender['provider_profile'],source_commit=C.SOURCE,source_tree=C.TREE,carrier_binding_sha256=selected['carrier_binding_sha256'],limits=binding['limits'],one_encryption=True,metadata_reads=18,automatic_retry=False,host_or_native_effect_grant=False,original_awards=[])
 C.need(admission_raw==C.encode(expected) and operation_raw==C.encode(op),'SENDER_EXACT_ACTUAL_ADMISSION')
 private={n[len('private-inputs/'):]:b for n,b in inputs.items() if n.startswith('private-inputs/')};C.need({n:C.desc(b) for n,b in private.items()}==index,'SENDER_PRIVATE_INDEX_CHANGED')
 # Reuse all exact host code/core/index/control subjects. Only three sender
 # binding bodies and root-only operation/admission/entry are different.
 sender.update(state='REVIEWED_EXACT_PRO_SENDER',source_commit=C.SOURCE,source_tree=C.TREE,operation=C.desc(operation_raw),admission=C.desc(admission_raw));packet['carrier/PRO_SENDER_COMPOSITION.json']=C.encode(sender)
 packet['carrier/sender_policy.py']=C.assignments(packet['carrier/sender_policy.py'],{'BINDING_SHA256':C.sha(packet['carrier/PRO_SENDER_COMPOSITION.json'])})
 carrier={n[8:]:b for n,b in packet.items() if n.startswith('carrier/')};C.loader_bind(carrier);packet['carrier/carrier_loader.py']=carrier['carrier_loader.py']
 packet['carrier/PRO_SENDER_OPERATION.json']=operation_raw;packet['carrier/PRO_SENDER_ADMISSION.json']=admission_raw
 packet.update({'private-inputs/'+n:b for n,b in private.items()})
 entry=C.assignments(C.templates()['adapter/integration/root_sender_entry.py'],{'ENTRY_STATE':'REVIEWED_EXACT_ROOT_SENDER_ENTRY','FIXED_PACKET_DIRECTORY':path,'LOADER_DESCRIPTOR':C.desc(packet['carrier/carrier_loader.py'])})
 out={'packet/'+n:b for n,b in packet.items()};out.update({'root_sender_entry.py':entry,'ROOT_REQUEST_ARTIFACT.zip':archive,'ROOT_SENDER_ASSEMBLY_SELECTION.json':inputs['ROOT_SENDER_ASSEMBLY_SELECTION.json'],'HOST_PUBLICATION_ROOT_RECEIVING.json':inputs['HOST_PUBLICATION_ROOT_RECEIVING.json']})
 out['ROOT_SENDER_INSTALL_MANIFEST.json']=C.encode(dict(schema='dg16.late-root-sender-install-manifest.v1',authority='NONE',fixed_packet_directory=path,sender_uid=op['sender_uid'],sender_gid=op['sender_gid'],directories_mode=0o700,public_file_mode=0o400,private_file_mode=0o600,host_manifest_sha256=selected['public_manifest_sha256'],host_manifest_unchanged=True,late_currentness='ACTUAL_SENDER_POLICY_PROVIDER_REQUEST_AND_TOOLS_REQUIRED',members={n:C.desc(b) for n,b in out.items()},original_awards=[]))
 return out
