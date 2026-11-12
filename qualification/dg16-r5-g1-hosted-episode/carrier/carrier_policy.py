"""Closed fixed-core carrier contracts. No transport, command or authority API."""
import json
import re
from pathlib import Path
import bundle_codec as C

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
SOURCE_COMMIT = '5f899a653df20073ed6691f898d9c9f630f0c100'
SOURCE_TREE = 'e7af9906e32eea314e33bddb7aeaf6bcff9242b0'
SCOPE = 'CORE_G1_Q06_NATURAL_L04_SEPARATE'
BINDING_SHA256 = '4e15e6f969835badb8adae4fa1a52c455d6836306601ce4bd797a801c3b7484c'
MAX_CIPHERTEXT = C.MAX_PLAINTEXT_BYTES + 16384
MAX_REQUEST = 8192
MAX_CERTIFICATE = 8192
MAX_CONTROL = 8192
MAX_ARTIFACT = 65536
MAX_INDEX = 65536
MAX_METADATA = 1024 * 1024
MAX_PRIVATE_BYTES = 80 * 1024**2
MAX_PRIVATE_ENTRIES = 1600
MAX_ACQUISITION_SECONDS = 600  # Prospective ceiling, not a selected hold.
MAX_COMMAND_SECONDS = 60
MAX_COMMAND_CPU_SECONDS = 60
MEMORY_BYTES = 512 * 1024**2
CONTEXT_KEYS = ('repository','branch','workflow_commit','workflow_path','run_id','run_attempt','job_name')
ROLES = {'root_admission':'COMPOSITION_ROOT_ADMISSION.json',
         'placement_receiving':'COMPOSITION_PLACEMENT_RECEIVING.json',
         'placement_evidence_index':'COMPOSITION_PLACEMENT_EVIDENCE_INDEX.json',
         'native_applicability_adoption':'COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json'}
RETAINED = {'SOURCE_ACQUISITION.json': {'bytes': 644544, 'sha256': '2cfc227c7bf69434e7ae040cd4e9084441b4fe47676af9bef8f8ebe4e0e1b462'}, 'PACKAGE_ROOT_RECEIVING.json': {'bytes': 928, 'sha256': '0edff0f3d8bd6f5520ef72d4e91daba54a6b0033e85b94f041f448c2951d6691'}, 'PACKAGE_BODY_RECEIVING.json': {'bytes': 9744, 'sha256': '8c592c76967ae2d95101af86ca25ab3bd4d09acdad486afbb976d61e7e5a7811'}, 'PACKAGE_TERMINAL_RECEIVING.json': {'bytes': 4531, 'sha256': 'e213b8843f03741c48776277f9e1db8c78ea1d3f7609875ce32bcd94e5ed5b89'}}
BODY_NAMES = ('HOST_COMPOSITION.json','host_composition.py','run.py','NATIVE_SOURCE_APPLICABILITY.json','host_utility.py')
LIMIT_KEYS = ('acquisition_seconds','command_seconds','command_cpu_seconds','poll_seconds')
need, sha, encode = C.need, C.sha, C.encode

def descriptor(raw): return dict(bytes=len(raw),sha256=sha(raw))

def parse(raw, maximum, canonical=True):
    need(type(raw) is bytes and 0 < len(raw) <= maximum,'CARRIER_JSON_BOUND')
    def pairs(rows):
        result={}
        for key,value in rows:
            need(key not in result,'CARRIER_DUPLICATE_KEY');result[key]=value
        return result
    try:
        value=json.loads(raw,object_pairs_hook=pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError('CARRIER_NONFINITE_JSON')))
    except (UnicodeError,json.JSONDecodeError,RecursionError) as exc:
        raise ValueError('CARRIER_JSON_REFUSED') from exc
    if canonical:need(encode(value)==raw,'CARRIER_NONCANONICAL_JSON')
    return value

def exact(value, keys, code='CARRIER_FIELDS'):
    need(type(value) is dict and set(value)==set(keys),code)

def digest(value): need(type(value) is str and re.fullmatch('[0-9a-f]{64}',value),'CARRIER_DIGEST')
def integer(value, low, high, code='CARRIER_INTEGER'):
    need(type(value) is int and low<=value<=high,code)

def context(value):
    exact(value,CONTEXT_KEYS)
    need(value['repository']==REPOSITORY and value['run_attempt']==1 and type(value['run_attempt']) is int,'CARRIER_CONTEXT')
    need(re.fullmatch('[1-9][0-9]{0,19}',value['run_id']) and re.fullmatch('[0-9a-f]{40}',value['workflow_commit']),'CARRIER_RUN')
    need(re.fullmatch(r'pro/[A-Za-z0-9][A-Za-z0-9/_-]{0,180}',value['branch'])
         and '..' not in value['branch'] and '//' not in value['branch'],'CARRIER_BRANCH')
    need(re.fullmatch(r'\.github/workflows/[A-Za-z0-9][A-Za-z0-9_-]{0,100}\.ya?ml',value['workflow_path'])
         and re.fullmatch('[A-Za-z0-9][A-Za-z0-9_-]{0,79}',value['job_name']),'CARRIER_WORKFLOW')
    return value

def fixed_host_paths(ctx):
    context(ctx)
    island=Path('/dg16-g1-'+ctx['run_id'])
    return dict(island=island,packet=island/'packet',source=island/'source',output=island/'output',
      receipt=island/'ROOT_PLACEMENT_RECEIPT.json')

def check_inputs(index, bodies, core):
    pin=C.check_index(index)
    need(type(bodies) is dict and set(bodies)==set(index),'ACTUAL_INPUT_POPULATION')
    for name,row in RETAINED.items(): need(index.get(name)==row,'RETAINED_INPUT_PIN')
    need(core.get('schema')=='dg16.current-g1-g3-fixed-root-core-composition.v2'
         and core.get('state')=='REVIEWED_EXACT_COMPOSITION' and core.get('component_scope')==SCOPE
         and core.get('source_commit')==SOURCE_COMMIT and core.get('source_tree')==SOURCE_TREE,'CARRIER_CORE_SCOPE')
    for role,name in ROLES.items():
        expected=core.get(role)
        need(type(expected) is dict and expected==dict(path='private-inputs/'+name,**index.get(name,{})),
             'CARRIER_COMPOSITION_BODY_BINDING')
    for name,row in index.items():
        need(type(bodies[name]) is bytes and descriptor(bodies[name])==row,'ACTUAL_INPUT_BODY_CHANGED')
    # The placement index may use the core's pretty canonical form; its exact
    # admitted body digest, rather than a reserialization, is the binding.
    try: placement=parse(bodies[ROLES['placement_evidence_index']],C.MAX_FILE_BYTES,canonical=False)
    except (ValueError,UnicodeError,RecursionError) as exc:raise ValueError('PLACEMENT_INDEX_JSON') from exc
    need(type(placement) is dict and set(placement)=={'schema','scope','members'}
         and placement['schema']=='dg16.received-placement-evidence-index.v1','PLACEMENT_INDEX_FIELDS')
    members=placement['members'];C.check_index(members)
    need(all(name.startswith('placement/') for name in members),'PLACEMENT_INDEX_PREFIX')
    need(set(index)==set(RETAINED)|set(ROLES.values())|set(members),'CARRIER_EXACT_INPUT_POPULATION')
    need(all(index[name]==row for name,row in members.items()),'PLACEMENT_ACTUAL_BODY_BINDING')
    return pin

def make_request(ctx,index,cert,nonce,issued_ms,expires_ms):
    context(ctx);digest(nonce)
    need(type(cert) is bytes and 0<len(cert)<=MAX_CERTIFICATE,'RECIPIENT_CERTIFICATE_BOUND')
    integer(issued_ms,0,10**16);integer(expires_ms,issued_ms+1,issued_ms+MAX_ACQUISITION_SECONDS*1000)
    value=dict(schema='dg16.core-private-recipient-request.v1',authority='NONE',component_scope=SCOPE,
      source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,**ctx,input_index_sha256=C.check_index(index),
      input_count=len(index),input_bytes=sum(row['bytes'] for row in index.values()),recipient_sha256=sha(cert),
      nonce=nonce,issued_unix_ms=issued_ms,expires_unix_ms=expires_ms,automatic_retry=False,original_awards=[])
    raw=encode(value);need(len(raw)<=MAX_REQUEST,'REQUEST_BOUND');return raw

def validate_request(raw,cert,ctx,index,now_ms):
    value=parse(raw,MAX_REQUEST)
    expected=make_request(ctx,index,cert,value.get('nonce'),value.get('issued_unix_ms'),value.get('expires_unix_ms'))
    need(raw==expected,'REQUEST_EXACT_CONTEXT')
    integer(now_ms,value['issued_unix_ms'],value['expires_unix_ms'],'REQUEST_EXPIRED_OR_FUTURE')
    return value

def make_control(request_raw,cipher,provider_receipt_sha256,issued_ms):
    q=parse(request_raw,MAX_REQUEST);digest(provider_receipt_sha256)
    need(type(cipher) is bytes and 0<len(cipher)<=MAX_CIPHERTEXT,'CIPHERTEXT_BOUND')
    integer(issued_ms,q['issued_unix_ms'],q['expires_unix_ms'],'CONTROL_TIME')
    value=dict(schema='dg16.core-private-ciphertext-control.v1',authority='NONE',component_scope=SCOPE,
       **{k:q[k] for k in CONTEXT_KEYS},source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,
       request_sha256=sha(request_raw),recipient_sha256=q['recipient_sha256'],nonce=q['nonce'],
       input_index_sha256=q['input_index_sha256'],ciphertext=descriptor(cipher),
       provider_receipt_sha256=provider_receipt_sha256,issued_unix_ms=issued_ms,original_awards=[])
    raw=encode(value);need(len(raw)<=MAX_CONTROL,'CONTROL_BOUND');return raw

def validate_control(raw,cipher,request_raw,now_ms):
    v=parse(raw,MAX_CONTROL);q=parse(request_raw,MAX_REQUEST)
    expected=make_control(request_raw,cipher,v.get('provider_receipt_sha256'),v.get('issued_unix_ms'))
    need(raw==expected,'CONTROL_EXACT_FRESH_BINDING')
    integer(now_ms,v['issued_unix_ms'],q['expires_unix_ms'],'CONTROL_EXPIRED_OR_FUTURE')
    return v

def public_result(status,code,request_sha256,authenticated,staged,cleanup_complete,elapsed_ns):
    need(status in ('REQUEST_READY','PAYLOAD_READY','INPUTS_READY','REFUSED'),'PUBLIC_STATUS')
    need(code in ('ACQUIRED','PRE_ENTRY_REFUSED','CMS_AUTHENTICATION_REFUSED','INPUT_RECEIVING_REFUSED',
         'CONTROL_REFUSED','CURRENTNESS_REFUSED','CLEANUP_REFUSED','INTERRUPTED','TOOL_OR_CAPTURE_REFUSED',
         'DEADLINE_EXPIRED','RESERVATION_REFUSED'),'PUBLIC_CODE')
    if request_sha256 is None:need(status=='REFUSED','PUBLIC_MISSING_REQUEST')
    else:digest(request_sha256)
    integer(elapsed_ns,0,10**16)
    need(all(type(v) is bool for v in (authenticated,staged,cleanup_complete)),'PUBLIC_BOOLEAN')
    return dict(schema='dg16.core-private-carrier-result.v1',authority='NONE',status=status,code=code,
       request_sha256=request_sha256,authenticated=authenticated,staged=staged,cleanup_complete=cleanup_complete,
       elapsed_ns=elapsed_ns,original_awards=[])

def load():
    import carrier_io as F
    base=Path(__file__).absolute().parent
    raw,binding_record=F.read_file(base/'CARRIER_COMPOSITION.json',MAX_INDEX)
    need(sha(raw)==BINDING_SHA256,'CARRIER_BINDING_PIN')
    v=parse(raw,MAX_INDEX)
    need(v.get('state')=='REVIEWED_EXACT_CARRIER_COMPOSITION','CARRIER_COMPOSITION_UNRESOLVED')
    exact(v,('schema','state','repository','source_commit','source_tree','component_scope','branch',
      'workflow_path','workflow_sha256','job_name','control_branch','control_parent','core_bodies',
      'input_index','carrier_admission','placement_body','host_tools','root_tools','limits','original_awards'))
    need(v['schema']=='dg16.core-private-carrier-composition.v2' and v['repository']==REPOSITORY
      and v['source_commit']==SOURCE_COMMIT and v['source_tree']==SOURCE_TREE and v['component_scope']==SCOPE
      and v['original_awards']==[],'CARRIER_COMPOSITION_SCOPE')
    context(dict(repository=REPOSITORY,branch=v['branch'],workflow_commit='0'*40,workflow_path=v['workflow_path'],
       run_id='1',run_attempt=1,job_name=v['job_name']))
    digest(v['workflow_sha256']);need(re.fullmatch('[0-9a-f]{40}',v['control_parent']),'CONTROL_INITIAL_COMMIT')
    need(re.fullmatch(r'pro/[A-Za-z0-9][A-Za-z0-9/_-]{0,180}',v['control_branch']) and '..' not in v['control_branch']
         and '//' not in v['control_branch'] and v['control_branch']!=v['branch'],'CONTROL_BRANCH')
    exact(v['limits'],LIMIT_KEYS)
    integer(v['limits']['acquisition_seconds'],1,MAX_ACQUISITION_SECONDS)
    integer(v['limits']['command_seconds'],1,MAX_COMMAND_SECONDS)
    integer(v['limits']['command_cpu_seconds'],1,MAX_COMMAND_CPU_SECONDS)
    integer(v['limits']['poll_seconds'],1,15)
    need(v['limits']['command_seconds']<=v['limits']['acquisition_seconds'],'CARRIER_TIME_RELATION')
    packet=base.parent
    exact(v['core_bodies'],BODY_NAMES)
    records={}
    for name,row in v['core_bodies'].items():
        body,record=F.read_file(packet/name,1024*1024)
        need(descriptor(body)==row,'CARRIER_CURRENT_CORE_BODY');records[name]=record
    exact(v['placement_body'],('path','bytes','sha256'))
    need(v['placement_body']['path']=='root_placement.py','CARRIER_FIXED_PLACEMENT_MODULE')
    placement_raw,placement_record=F.read_file(packet/'root_placement.py',1024*1024)
    need(dict(path='root_placement.py',**descriptor(placement_raw))==v['placement_body'],'CARRIER_PLACEMENT_BODY_PIN')
    index_raw,index_record=F.read_file(base/'INPUT_INDEX.json',MAX_INDEX)
    need(descriptor(index_raw)==v['input_index'],'CARRIER_INDEX_PIN')
    index=parse(index_raw,MAX_INDEX);C.check_index(index)
    for name,row in RETAINED.items():need(index.get(name)==row,'RETAINED_INPUT_PIN')
    need(set(RETAINED)|set(ROLES.values())<=set(index),'CARRIER_ALL_ROLE_BODIES_REQUIRED')
    admission_raw,admission_record=F.read_file(base/'CARRIER_ADMISSION.json',MAX_INDEX)
    need(descriptor(admission_raw)==v['carrier_admission'],'CARRIER_ADMISSION_BODY_PIN')
    admission=parse(admission_raw,MAX_INDEX)
    expected=dict(schema='dg16.core-private-carrier-root-admission.v2',issuer='R5_ROOT_GOVERNOR',
        operation='ONE_FIXED_TOOL_BOOTSTRAP_ONE_FRESH_RECIPIENT_ONE_PRIVATE_TRANSFER',source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,
        workflow_branch=v['branch'],workflow_path=v['workflow_path'],workflow_sha256=v['workflow_sha256'],
        control_branch=v['control_branch'],control_parent=v['control_parent'],input_index_sha256=sha(index_raw),
        limits=v['limits'],host_tool_bootstrap=v['host_tools'],run_attempt=1,automatic_retry=False,core_or_native_effect_grant=False,original_awards=[])
    need(admission==expected,'CARRIER_SEPARATE_ADMISSION_SCOPE')
    import host_tools
    host_tools.declaration(v)
    for role in ('root_tools',):
        exact(v[role],('openssl','env'))
        for name,row in v[role].items():
            exact(row,('bytes','sha256'));integer(row['bytes'],1,32*1024**2);digest(row['sha256'])
    v['_packet']=packet;v['_base']=base;v['_index']=index;v['_opening_core']=records
    v['_binding_raw']=raw;v['_admission_raw']=admission_raw
    v['_opening_contract']=dict(binding=binding_record,index=index_record,admission=admission_record)
    v['_opening_placement']=placement_record
    return v
