"""Explicit root-only Pro sender selection; absent admissions stay refused.

These pinned records are the root's assembly seam, not actor authentication.
The separately reviewed root dispatcher and actual tool history supply that
boundary. No environment value selects an alternative capture or provider.
"""
import os
from pathlib import Path
import time
import carrier_policy as P
import carrier_io as F

BINDING_SHA256 = '40a03483d59d30335b0531e9d4a152bf88b37c0f54e03417e9ce94b891c6a500'
CAPTURE_PROFILE='MAINTAINED_OWNER_THREE_FD_ENCRYPTION_V1'
PROVIDER_PROFILE='ROOT_SUPPORTED_GITHUB_FETCH_FILE_BROKER_V1'
HOST_CAPTURE_SHA256='429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'

def load(binding,context,artifact_id,archive):
    base=Path(__file__).absolute().parent
    raw,row=F.read_file(base/'PRO_SENDER_COMPOSITION.json',P.MAX_INDEX)
    P.need(type(BINDING_SHA256) is str and P.sha(raw)==BINDING_SHA256,'PRO_SENDER_BINDING_REQUIRED')
    v=P.parse(raw,P.MAX_INDEX)
    P.need(v.get('state')=='REVIEWED_EXACT_PRO_SENDER','PRO_SENDER_UNRESOLVED')
    P.exact(v,('schema','state','source_commit','source_tree','capture_profile','provider_profile',
      'host_capture_sha256','operation','admission','original_awards'))
    P.need(v['schema']=='dg16.pro-private-sender-composition.v1' and v['source_commit']==binding['source_commit']
      and v['source_tree']==binding['source_tree'] and v['capture_profile']==CAPTURE_PROFILE
      and v['provider_profile']==PROVIDER_PROFILE and v['host_capture_sha256']==HOST_CAPTURE_SHA256
      and v['original_awards']==[],'PRO_SENDER_EXACT_ROLE_SCOPE')
    P.integer(binding['limits']['command_seconds'],4,P.MAX_COMMAND_SECONDS,'PRO_SENDER_CLOSING_INTERVAL_REQUIRED')
    bodies={};records={'composition':row}
    for name,file in (('operation','PRO_SENDER_OPERATION.json'),('admission','PRO_SENDER_ADMISSION.json')):
        body,physical=F.read_file(base/file,P.MAX_INDEX)
        P.need(P.descriptor(body)==v[name],'PRO_SENDER_ACTUAL_BODY_PIN')
        bodies[name]=body;records[name]=physical
    op=P.parse(bodies['operation'],P.MAX_INDEX)
    P.exact(op,('schema','context','source_commit','source_tree','carrier_binding_sha256','input_index_sha256',
      'artifact_id','artifact','nonce','issued_unix_ms','expires_unix_ms','sender_uid','sender_gid','original_awards'))
    P.context(context);P.digest(op['nonce']);P.integer(artifact_id,1,10**20)
    P.need(op['schema']=='dg16.pro-private-sender-operation.v1' and op['context']==context
      and op['source_commit']==binding['source_commit'] and op['source_tree']==binding['source_tree']
      and op['carrier_binding_sha256']==P.sha(binding['_binding_raw'])
      and op['input_index_sha256']==P.C.check_index(binding['_index']) and op['artifact_id']==artifact_id
      and op['artifact']==P.descriptor(archive) and op['original_awards']==[],'PRO_SENDER_OPERATION_BINDING')
    P.integer(op['issued_unix_ms'],0,10**16);P.integer(op['expires_unix_ms'],op['issued_unix_ms']+1,
      op['issued_unix_ms']+binding['limits']['acquisition_seconds']*1000)
    P.need(op['issued_unix_ms']<=int(time.time()*1000)<op['expires_unix_ms'],'PRO_SENDER_OPERATION_EXPIRED')
    P.need(type(op['sender_uid']) is int and op['sender_uid']>0 and os.getuid()==os.geteuid()==op['sender_uid']
      and type(op['sender_gid']) is int and os.getgid()==os.getegid()==op['sender_gid'],'PRO_SENDER_ACTUAL_NONROOT_IDENTITY')
    expected=dict(schema='dg16.pro-private-sender-root-admission.v1',issuer='R5_ROOT_GOVERNOR',
      operation_sha256=P.sha(bodies['operation']),capture_profile=CAPTURE_PROFILE,provider_profile=PROVIDER_PROFILE,
      source_commit=binding['source_commit'],source_tree=binding['source_tree'],
      carrier_binding_sha256=P.sha(binding['_binding_raw']),limits=binding['limits'],
      one_encryption=True,metadata_reads=18,automatic_retry=False,host_or_native_effect_grant=False,original_awards=[])
    P.need(P.parse(bodies['admission'],P.MAX_INDEX)==expected,'PRO_SENDER_ROOT_ADMISSION_SCOPE')
    return dict(value=v,operation=op,records=records,base=base,raw=raw)

def current(selection):
    for name,file in (('composition','PRO_SENDER_COMPOSITION.json'),('operation','PRO_SENDER_OPERATION.json'),
                      ('admission','PRO_SENDER_ADMISSION.json')):
        _,row=F.read_file(selection['base']/file,P.MAX_INDEX)
        P.need(row==selection['records'][name],'PRO_SENDER_CURRENT_BODY_CHANGED')
    op=selection['operation']
    P.need(op['issued_unix_ms']<=int(time.time()*1000)<op['expires_unix_ms']
      and os.getuid()==os.geteuid()==op['sender_uid'] and os.getgid()==os.getegid()==op['sender_gid'],
      'PRO_SENDER_CURRENT_OPERATION_CHANGED')
    return True
