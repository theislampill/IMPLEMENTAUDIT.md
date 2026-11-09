"""Deterministic prospective source/data composition; no operation or decision."""
import argparse,ast,hashlib,json,os,re,stat
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=Path('/workspace/scratch/52e9b813fb80/dg16-work')
INPUT=ROOT/'inputs'
PREFIX='qualification/dg16-r5-full-g2/'
SOURCE_COMMIT='7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'
SOURCE_TREE='6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e'
BRANCH='pro/dg16-r5-full-g2-current-03-20261107'
CONTROL='pro/dg16-r5-full-g2-current-control-03-20261107'
COMPONENT_SEAL='e99a60d5790355ae39c0e4bbc4567add87e702775ade8f5655e2f3ef56bd9602'
COMPONENT_REVIEW='a04b62ff8b2e0e315d0fb7af5ffee37a4d257e9aa507cd628bcd9ccaea3e295d'
COMPONENT_INDEX='9d54e10f1c6d056d43801b8457f909030498704a766b17998abbc9c4525c28f3'
SUCCESSOR_SESSION='52e9b813fb80'
CURRENT_SELECTION={'bytes':2611,'sha256':'b0c465ee54634da10f606febb169a2114a6942aa383d17104bc4ef9c9d4d3a49'}
CURRENT_CUSTODY={'bytes':2442,'sha256':'88a4f0f9cf2df3d65ef2e5121a09a5884ae09d3404c037ba4c944877fd1fb116'}
CURRENT_MAXIMUM_ROOT={'bytes':8230,'sha256':'1b21c5b2631f36f0a009046dafcd9eafe8f12bfb26ec7f79e433d33ba7666c16'}
CURRENT_AUTHOR='/root/g2_cold_review'
CONVENTIONAL_SOURCE_NAMES=('source','source-codex-home','source-3e','source-8ee4','source-ea61','source-current')

def need(ok,code):
    if not ok:raise ValueError(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def desc(raw):return dict(bytes=len(raw),sha256=sha(raw))
def encode(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def digest(value):return type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None
def exact(value,fields):need(type(value) is dict and set(value)==set(fields.split()),'EXACT_INPUT_FIELDS')
def descriptor_part(value):
    need(type(value) is dict and type(value.get('bytes')) is int and value['bytes']>0
      and digest(value.get('sha256')),'ACTUAL_DESCRIPTOR_VALUE')
    return {k:value[k] for k in ('bytes','sha256')}
def public_record(row,maximum):
    exact(row,'path bytes sha256');descriptor_part(row)
    need(type(row['path']) is str and not row['path'].endswith(('.key','.p12','.pfx')),'NO_PRIVATE_KEY_INPUT')
    path=Path(row['path'])
    need(path.is_absolute() and str(path)==os.path.normpath(str(path)) and path.is_relative_to(WORKSPACE),
      'PUBLIC_INPUT_WORKSPACE_REQUIRED')
    # Inspect public lexical parents without following an alias into private storage.
    for parent in path.parents:
        need(stat.S_ISDIR(parent.lstat().st_mode),'PUBLIC_INPUT_PARENT_ALIAS')
    raw=read(path,maximum);need(desc(raw)==descriptor_part(row),'ACTUAL_INPUT_DESCRIPTOR');return raw
def read(path,maximum=1024**2):
    path=Path(path).absolute();info=path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and 0<=info.st_size<=maximum,'INPUT_PHYSICAL_BOUND')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        raw=os.read(fd,maximum+1);end=os.fstat(fd)
        shape=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        need(shape(info)==shape(end)==shape(path.lstat()) and len(raw)==info.st_size,'INPUT_CHANGED')
        return raw
    finally:os.close(fd)
def substitute(raw,before,after,count=1):
    need(raw.count(before)==count,'GENERATOR_EXACT_SOURCE_ANCHOR');return raw.replace(before,after)
def source_inputs():
    bindings=json.loads(read(ROOT/'INPUT_BINDINGS.json'))
    for row in bindings['copies']:need(desc(read(ROOT/row['copy']))=={k:row[k] for k in ('bytes','sha256')},'GENERATOR_INPUT_CHANGED')
    capacity=json.loads(read(ROOT/'CAPACITY_BINDING.json'))
    need(capacity['seal_sha256']==COMPONENT_SEAL,'CAPACITY_INPUT_SCOPE')
    for row in capacity['copies']:need(desc(read(ROOT/row['copy']))=={k:row[k] for k in ('bytes','sha256')},'CAPACITY_INPUT_CHANGED')
    for binding_name in ('ACTUAL_INPUT_BINDINGS.json','SUCCESSOR_INPUT_BINDINGS.json'):
        actual_path=ROOT/binding_name
        if actual_path.is_file():
            for row in json.loads(read(actual_path))['copies']:
                need(desc(read(ROOT/row['copy']))=={k:row[k] for k in ('bytes','sha256')},'ACTUAL_INPUT_COPY_CHANGED')
    return bindings

def qualified_result(raw,case):
    need(type(raw) is bytes and len(raw)<=65536,'ACTUAL_RESULT_BOUND');value=json.loads(raw)
    need(value.get('schema')=='dg16.synthetic-cms-result.v1' and value.get('case')==case
      and value.get('status')=='SYNTHETIC_CRYPTO_CASE_COMPLETE' and value.get('echild_at_terminal') is True
      and value.get('automatic_retry') is False and value.get('original_acceptance') is False,
      'ACTUAL_COMPLETE_QUALIFICATION_REQUIRED')
    expected=[0,0,4,4] if case=='small' else [0,0]
    commands=value.get('crypto_commands');need(type(commands) is list and len(commands)==len(expected),'ACTUAL_COMMAND_POPULATION')
    for command,rc in zip(commands,expected):
        need(type(command.get('returncode')) is int and command['returncode']==rc,'ACTUAL_CRYPTO_DISPOSITION')
        records=command.get('capture');need(type(records) is list and len(records)==1,'ACTUAL_CRYPTO_CAPTURE')
        record=records[0]
        need(type(record.get('returncode')) is int and record['returncode']==rc
          and record.get('process_started') is True and record.get('pidfd_acquired') is True
          and record.get('streams_complete') is True and record.get('timeout') is False
          and record.get('output_bound_exceeded') is False and record.get('internal_failure') is None
          and record.get('cleanup',{}).get('echild') is True and record['cleanup'].get('restoration_complete') is True,
          'ACTUAL_CRYPTO_CUSTODY_REQUIRED')
    if case=='maximum':
        need(value.get('maximum_capacity_qualified') is True and set(value.get('inputs',{}))=={'stdout','stderr'}
          and all(value['inputs'][n].get('bytes')==128*1024**2 for n in ('stdout','stderr')),
          'ACTUAL_MAXIMUM_CAPACITY_REQUIRED')
    return value

def validate_final_input(value):
    """Actual bodies and independent/root receiving are supplied by root later.

    This function does not authenticate a root actor from JSON. Root actual
    tool/lane history is the separate provenance and later effect boundary.
    """
    exact(value,'schema actor session status component_seal_sha256 component_review_seal_sha256 source_commit source_tree branch control_branch public_selection certificate qualifications component_review enrollment_root_receiving effect_grant original_awards')
    need(value['schema']=='dg16.protected-full-g2-final-code-input.v1' and value['actor']=='/root'
      and value['session']==SUCCESSOR_SESSION and value['status']=='ACTUAL_INPUTS_RECEIVED_FOR_CODE_BINDING'
      and value['component_seal_sha256']==COMPONENT_SEAL and value['component_review_seal_sha256']==COMPONENT_REVIEW
      and value['source_commit']==SOURCE_COMMIT and value['source_tree']==SOURCE_TREE
      and value['branch']==BRANCH and value['control_branch']==CONTROL and value['effect_grant'] is False
      and value['original_awards']==[],'ACTUAL_FINAL_INPUT_SCOPE')
    exact(value['qualifications'],'small maximum')
    bodies={};receipts={}
    held=public_record
    accepted={
      'small':dict(result='e62f9127ef6b8c0e8a849a54bb23e98a831a5c2266e070ee2355c75c0275fe20',
        review='cdc597a7c68597f5f8643dec237c00419e06513d7d11ea9a77dd585646e3cb4f',
        root='5609d984bc3a776a9ac1cba6ca3a500ee3a554baf95462ba10ee9bf1d3f32701'),
      'maximum':dict(result='814cd1a0cbb6aa2afdbd90a8cb6ebb4399d4d93bfcaca4c05809b5415b6b6546',
        review='1e6c01bec5398ce960f76a1f20bccd75a99c518b5a6b8d3a0dcf24689eea786f',
        root=CURRENT_MAXIMUM_ROOT['sha256'])}
    for case,record in value['qualifications'].items():
        exact(record,'result independent_seal root_receiving')
        raw=held(record['result'],65536);result=qualified_result(raw,case)
        review_raw=held(record['independent_seal'],131072);review=json.loads(review_raw)
        need(type(review.get('members')) in (list,dict) and type(review.get('member_count')) is int and review['member_count']>0,'ACTUAL_INDEPENDENT_SEAL_REQUIRED')
        receipt_raw=held(record['root_receiving'],16384);receipt=json.loads(receipt_raw)
        need(sha(raw)==accepted[case]['result'] and sha(review_raw)==accepted[case]['review']
          and sha(receipt_raw)==accepted[case]['root'] and receipt.get('actor')=='/root'
          and receipt.get('session')==SUCCESSOR_SESSION and receipt.get('original_awards')==[]
          and receipt.get('native_currentness') is False,'ACTUAL_RECEIVED_QUALIFICATION_PINS')
        disposition='PASS_SCOPED_ACTUAL_'+('SMALL_AUTHENTICATION' if case=='small' else 'MAXIMUM_CAPACITY')+'_RECEIVING'
        final_rows=[r for r in review['members'] if r.get('path')=='FINAL.json']
        need(len(final_rows)==1 and descriptor_part(final_rows[0])==receipt.get('actual_independent_final')
          and review.get('actor')==receipt.get('independent_actor')=='/root/g2_cold_review'
          and review.get('disposition')==receipt.get('received_disposition')==disposition
          and review.get('actual_result')==receipt.get('actual_result')==desc(raw)
          and receipt.get('actual_independent_seal')==desc(review_raw)
          and review.get('effect_grant') is False and review.get('original_awards')==[]
          and receipt.get('actual_returncodes')==[c['returncode'] for c in result['crypto_commands']]
          and receipt.get('actual_tool_provenance',{}).get('one_invocation') is True
          and receipt['actual_tool_provenance'].get('grant_consumed') is True,'ACTUAL_RESULT_REVIEW_ROOT_JOIN')
        if case=='small':
            need(receipt.get('schema')=='dg16.actual-small-root-receiving.v1'
              and receipt.get('state')=='PASS_SCOPED_ACTUAL_SMALL_ROOT_RECEIVING'
              and receipt.get('authenticated_binary_roundtrip_received') is True
              and receipt.get('positive_plaintext_gate_received') is True
              and receipt.get('wrong_key_and_tamper_rejections_received') is True
              and receipt.get('maximum_actual_operation_admitted') is False
              and receipt.get('maximum_capacity_qualified') is False,'ACTUAL_SMALL_ROOT_JOIN')
        else:
            need(receipt.get('schema')=='dg16.actual-maximum-root-receiving.v1'
              and receipt.get('state')=='PASS_SCOPED_ACTUAL_MAXIMUM_ROOT_RECEIVING'
              and receipt.get('source',{}).get('seal')==dict(bytes=3493,sha256=COMPONENT_SEAL)
              and receipt['source'].get('independent_source_review_seal')==dict(bytes=17125,sha256=COMPONENT_REVIEW)
              and receipt['source'].get('manifest')==dict(bytes=2148,sha256=COMPONENT_INDEX)
              and receipt.get('preserved_profile')==dict(address_space_bytes=1024**3,cpu_seconds=60,
                case_seconds=180,cleanup_seconds=3,command_stdout_bytes=32768,command_stderr_bytes=32768,
                crypto_commands_at_most=2,cumulative_private_bytes_at_most=2*1024**3,
                per_command_seconds=60,raw_stream_bytes_each=128*1024**2)
              and receipt.get('capacity_scope')=='PASS_EXACT_PRO_TOOLS_SOURCE_PROFILE_AND_GENERATED_FRAME'
              and receipt.get('maximum_capacity_qualified') is True
              and receipt.get('authenticated_binary_roundtrip_received') is True
              and receipt.get('correct_plaintext_gate_received') is True
              and receipt.get('exact_full_frame_manifest_stream_cipher_receiving') is True
              and receipt.get('complete_captures_installed_limits_and_owned_cleanup') is True
              and receipt.get('new_operation_admitted') is False and receipt.get('full_G2_Q02_acceptance') is False,
              'ACTUAL_MAXIMUM_ROOT_JOIN')
        bodies[case]=dict(result=desc(raw),independent_seal=desc(review_raw),root_receiving=desc(receipt_raw))
        receipts[case]=receipt
    exact(value['component_review'],'independent_seal root_receiving')
    component_review_raw=held(value['component_review']['independent_seal'],131072)
    component_root_raw=held(value['component_review']['root_receiving'],16384)
    need(sha(component_review_raw)==COMPONENT_REVIEW
      and sha(component_root_raw)=='fd2563ada8f1efd3ee189f26295c151e43e3f11393cd81aee5ee0be25df037da','ACTUAL_COMPONENT_REVIEW_PINS')
    component_root=json.loads(component_root_raw)
    need(component_root.get('schema')=='dg16.actual-maximum-bound-source-root-receiving.v1'
      and component_root.get('state')=='PASS_SCOPED_ACTUAL_BOUND_MAXIMUM_SOURCE_ROOT_RECEIVING'
      and component_root.get('actor')=='/root' and component_root.get('genuine_independence_received') is True
      and descriptor_part(component_root['subject'])==dict(bytes=3493,sha256=COMPONENT_SEAL)
      and descriptor_part(component_root['actual_independent_seal'])==desc(component_review_raw)
      and component_root.get('reviewer')==json.loads(component_review_raw).get('actor')=='/root/g1_receiving_review'
      and component_root.get('maximum_effect_admitted_by_this_receipt') is False
      and component_root.get('source_only') is True and component_root.get('original_awards')==[]
      and descriptor_part(component_root['actual_small_root_receiving'])==bodies['small']['root_receiving']
      and receipts['maximum']['source']['root_source_receiving']==desc(component_root_raw),'ACTUAL_COMPONENT_REVIEW_JOIN')
    review_bodies=dict(independent_seal=desc(component_review_raw),root_receiving=desc(component_root_raw))
    enrollment_raw=held(value['enrollment_root_receiving'],16384)
    need(sha(enrollment_raw)=='02bf425912f391bb975adffe13cd3321d5183a53d096ef763c141d27d64a9a6c','ACTUAL_ENROLLMENT_ROOT_PIN')
    enrollment=json.loads(enrollment_raw)
    need(enrollment.get('schema')=='dg16.actual-enrollment-root-receiving.v1'
      and enrollment.get('state')=='PASS_SCOPED_ACTUAL_ENROLLMENT_ROOT_RECEIVING'
      and enrollment.get('actor')=='/root' and enrollment.get('one_actual_invocation') is True
      and enrollment.get('grant_consumed') is True and enrollment.get('future_effect_grant') is False
      and enrollment.get('historical_maximum_award_transferred') is False
      and enrollment.get('original_awards')==[],'ACTUAL_ENROLLMENT_ROOT_JOIN')
    enrollment_predecessors=dict(result=descriptor_part(enrollment['actual_result']),
      independent_final=descriptor_part(enrollment['independent_final']),
      independent_seal=descriptor_part(enrollment['independent_seal']),root_receiving=desc(enrollment_raw))
    need(all(r.get('actual_enrollment_predecessors')==enrollment_predecessors for r in receipts.values())
      and receipts['maximum'].get('actual_small_predecessors')==dict(bodies['small'],
        independent_final=receipts['small']['actual_independent_final'])
      and receipts['small']['actual_recipient_inputs']==receipts['maximum']['actual_recipient_inputs'],
      'ACTUAL_FRESH_QUALIFICATION_LINEAGE_JOIN')
    cert=held(value['certificate'],8192)
    need(cert.startswith(b'-----BEGIN CERTIFICATE-----\n') and cert.rstrip().endswith(b'-----END CERTIFICATE-----')
      and b'PRIVATE KEY' not in cert and cert.count(b'-----BEGIN CERTIFICATE-----')==1,'PUBLIC_CERTIFICATE_ONLY')
    need(desc(cert)==receipts['maximum']['actual_recipient_inputs']['recipient']['certificate'],
      'ACTUAL_QUALIFIED_RECIPIENT_CERTIFICATE_JOIN')
    selected_raw=held(value['public_selection'],16384);selected=json.loads(selected_raw)
    fixed=dict(schema='dg16.protected-full-g2-public-recipient-adoption.v1',actor='/root',session=value['session'],
      status='ACTUAL_RECIPIENT_AND_QUALIFIED_PROFILE_SELECTED',source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,
      branch=BRANCH,control_branch=CONTROL,component_seal_sha256=COMPONENT_SEAL,component_code_manifest_sha256=COMPONENT_INDEX,
      component_review_seal_sha256=COMPONENT_REVIEW,recipient=desc(cert),qualifications=bodies,
      component_review=review_bodies,enrollment_root_receiving=desc(enrollment_raw),
      small_authenticated_qualified=True,maximum_capacity_qualified=True,private_key_on_host=False,
      host_gate='MAXIMUM_OPAQUE_PLAINTEXT_ENCRYPTION_BEFORE_EITHER_MAINTAINED_LEG',
      automatic_retry=False,effect_grant=False,original_awards=[])
    need(set(selected)==set(fixed)|{'root_receiving'} and all(type(selected[k]) is type(v) and selected[k]==v for k,v in fixed.items()),
      'ACTUAL_PUBLIC_ADOPTION_JOIN')
    exact(selected['root_receiving'],'bytes sha256');need(type(selected['root_receiving']['bytes']) is int
      and 0<selected['root_receiving']['bytes']<=65536 and digest(selected['root_receiving']['sha256']),'ACTUAL_ROOT_RECEIVING_DESCRIPTOR')
    need(selected['root_receiving']==bodies['maximum']['root_receiving'],'ACTUAL_ROOT_RECIPIENT_QUALIFICATION_JOIN')
    need(selected_raw==encode(selected),'ACTUAL_PUBLIC_ADOPTION_CANONICAL')
    return dict(selection=selected,selection_raw=selected_raw,certificate=cert)

def validate_runtime_input(value,final=None):
    """Consume actual public root custody testimony for prospective paths only.

    No private path in that data is opened or inspected. Future operations must
    refresh custody. Root lane provenance is external to matching JSON labels.
    """
    exact(value,'schema actor session status workspace_root receiver_output_root maintained_source_root current_public_selection recipient_custody recipient_custody_receiving local_native_currentness effect_grant original_awards')
    need(value['schema']=='dg16.protected-full-g2-current-recipient-runtime-binding.v1'
      and value['actor']=='/root' and value['session']==SUCCESSOR_SESSION
      and value['status']=='PROSPECTIVE_CODE_BINDING_ONLY'
      and value['recipient_custody']=='ACTUAL_ROOT_RECEIVED_REPLACEMENT_RECIPIENT_PRO_SCOPE'
      and value['local_native_currentness'] is False and value['effect_grant'] is False
      and value['original_awards']==[],'SUCCESSOR_RUNTIME_SCOPE')
    for name in ('workspace_root','receiver_output_root','maintained_source_root'):
        text=value[name]
        need(type(text) is str and '\x00' not in text and '\n' not in text
          and Path(text).is_absolute() and str(Path(text))==text
          and '..' not in Path(text).parts,'SUCCESSOR_ABSOLUTE_PHYSICAL_PATH')
    workspace=Path(value['workspace_root']);source=Path(value['maintained_source_root'])
    need(workspace==WORKSPACE and workspace.resolve(strict=True)==workspace and workspace.is_dir()
      and source==workspace.parent/'dg16-execution' and source.resolve(strict=True)==source
      and source.is_dir(),'SUCCESSOR_WORKSPACE_AND_SOURCE_SCOPE')
    output=Path(value['receiver_output_root'])
    need(output==workspace/'g2-protected-full-actual-receiving-current03'
      and (not os.path.lexists(output) or (output.resolve(strict=True)==output and output.is_dir())),
      'SUCCESSOR_RECEIVER_OUTPUT_SCOPE')
    exact(value['current_public_selection'],'bytes sha256')
    need(value['current_public_selection']==CURRENT_SELECTION
      and (final is None or desc(final['selection_raw'])==CURRENT_SELECTION),'CURRENT_PUBLIC_SELECTION_JOIN')
    need(descriptor_part(value['recipient_custody_receiving'])==CURRENT_CUSTODY,'CURRENT_ROOT_CUSTODY_PIN')
    custody=json.loads(public_record(value['recipient_custody_receiving'],16384))
    need(custody.get('schema')=='dg16.current03.recipient-root-custody-selection.v1' and custody.get('actor')=='/root'
      and descriptor_part(custody['selected_public'])==CURRENT_SELECTION
      and descriptor_part(custody['actual_maximum_root_receiving'])==CURRENT_MAXIMUM_ROOT
      and custody.get('future_private_operation_must_refresh_custody') is True
      and custody.get('key_body_opened_read_hashed_or_exported') is False
      and custody.get('historical_key_recreated') is False and custody.get('historical_qualification_transferred') is False
      and custody.get('native_currentness') is False and custody.get('effect_grant') is False
      and custody.get('original_awards')==[],'CURRENT_ROOT_CUSTODY_SCOPE')
    need(custody['private_key_physical_opening']==custody['private_key_physical_closing']
      and custody['directory_physical_opening']==custody['directory_physical_closing']
      and custody['private_key_physical_opening']['mode']=='0600'
      and custody['private_key_physical_opening']['links']==1
      and custody['private_key_physical_opening']['uid']==1000
      and custody['directory_physical_opening']['mode']=='0700'
      and custody['directory_physical_opening']['uid']==1000
      and custody['private_key_physical_opening']['bytes']==custody['selected_key_descriptor']['bytes'],
      'ROOT_METADATA_ONLY_CUSTODY_BOOKENDS')
    return value

def validate_review_selection(value,binding):
    """Pure role/subject join; root separately receives actual commission provenance."""
    exact(value,'schema actor session status author reviewer source_commit source_tree branch control_branch candidate_seal_sha256 composition_seal_sha256 final_tree effect_grant native_currentness original_awards')
    reviewer=binding['composition_review_reviewer']
    need(type(reviewer) is str and re.fullmatch('/root/[a-z0-9_]+',reviewer)
      and reviewer!=CURRENT_AUTHOR,'CURRENT_AUTHOR_CANNOT_REVIEW_FINAL_BINDING')
    expected=dict(schema='dg16.current03.combined-review-root-selection.v1',actor='/root',session=SUCCESSOR_SESSION,
      status='ACTUAL_DISTINCT_REVIEWER_SELECTED_FOR_FINAL_BINDING',author=CURRENT_AUTHOR,reviewer=reviewer,
      source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,branch=BRANCH,control_branch=CONTROL,
      candidate_seal_sha256=binding['candidate_seal_sha256'],composition_seal_sha256=binding['composition_seal_sha256'],
      final_tree=binding['final_tree'],effect_grant=False,native_currentness=False,original_awards=[])
    need(all(type(value[k]) is type(v) and value[k]==v for k,v in expected.items()),
      'ACTUAL_ROOT_DISTINCT_REVIEW_SELECTION_JOIN')
    return value

RUN_HELPERS='''def load_protected(u):
    return load_adapter('protected_bridge.py',PROTECTED_BRIDGE_SHA,u)

def protected_capacity(value,u):
    return load_protected(u).reserve_capacity(value,u)

def protected_preflight(state,source,output,u,tools,manifest):
    parent=types.SimpleNamespace(**globals())
    return load_protected(u).preflight(parent,state,source,output,u,tools,manifest)

def protected_failed_finalize(state,source,output,u,tools,manifest,deadline):
    parent=types.SimpleNamespace(**globals())
    return load_protected(u).failed_finalize(parent,state,source,output,u,tools,manifest,deadline)

def protected_emit(source,output,u):
    # A supplementary eligibility refusal never blocks original public upload.
    eligible=False
    try:
        state=u.parse_json(u.checked_file(output/'private/episode.json',1024**2))
        eligible=load_protected(u).emit_eligibility(types.SimpleNamespace(**globals()),state,source,output,u)
    except BaseException:pass
    print('eligible='+('true' if eligible else 'false'),flush=True)

'''

def prepared_public(final=None):
    source_inputs();files={str(p.relative_to(INPUT/'base_public')):p.read_bytes() for p in (INPUT/'base_public').rglob('*') if p.is_file()}
    need(len(files)==30,'ORIGINAL_PUBLIC_POPULATION')
    index_raw=read(INPUT/'capacity_r1/CODE_MANIFEST.json');need(sha(index_raw)==COMPONENT_INDEX,'COMPONENT_INDEX_PIN')
    pins=json.loads(index_raw)['members']
    for name,pin in pins.items():
        raw=read(INPUT/'capacity_r1'/name);need(desc(raw)==pin,'COMPONENT_MEMBER_PIN')
        if PREFIX+name in files:need(files[PREFIX+name]==raw,'UNCHANGED_COMPONENT_REUSE')
        else:files[PREFIX+name]=raw
    preflight=read(ROOT/'templates/protected_preflight.py.in');ast.parse(preflight)
    files[PREFIX+'protected_preflight.py']=preflight
    bridge=read(ROOT/'templates/protected_bridge.py.in').decode()
    bridge=bridge.replace('__COMPONENT_PINS__',repr(pins)).replace('__PREFLIGHT_SHA__',repr(sha(preflight))).replace('__SELECTION_SHA__',repr(sha(final['selection_raw'])) if final else 'None').replace('__BOUND__','True' if final else 'False')
    files[PREFIX+'protected_bridge.py']=bridge.encode();ast.parse(bridge)
    if final:
        files[PREFIX+'PROTECTED_RECIPIENT.json']=final['selection_raw'];files[PREFIX+'PROTECTED_RECIPIENT.pem']=final['certificate']
    code=files[PREFIX+'run.py'].decode()
    code=substitute(code,"BRANCH = 'pro/dg16-r5-full-g2-current-01-20261106'",'BRANCH = '+repr(BRANCH))
    control=substitute(files[PREFIX+'live_control.py'].decode(),"CONTROL_BRANCH = 'pro/dg16-r5-full-g2-current-control-01-20261106'",'CONTROL_BRANCH = '+repr(CONTROL))
    files[PREFIX+'live_control.py']=control.encode()
    code=re.sub(r"^LIVE_CONTROL_SHA = '[0-9a-f]{64}'$",'LIVE_CONTROL_SHA = '+repr(sha(control.encode())),code,flags=re.M)
    code=substitute(code,'FINAL_COMPOSITION_READY = True','FINAL_COMPOSITION_READY = '+str(final is not None)+'\nPROTECTED_BRIDGE_SHA = '+repr(sha(bridge.encode())))
    code=substitute(code,'def operation(step,state,source,output,tools,u,manifest,command):',RUN_HELPERS+'def operation(step,state,source,output,tools,u,manifest,command):')
    code=substitute(code,"'FAILURE.json':{'schema':'dg16.full-registry-episode-failure.v1','present':False,'failures':[],'capture_observation':None}",
      "'FAILURE.json':{'schema':'dg16.full-registry-episode-failure.v1','present':False,'failures':[],'capture_observation':None,'protected_streams':None}")
    code=substitute(code,"'causal_observations':[],","'causal_observations':[],'protected_capability':None,")
    code=substitute(code,"        require_native_for_pair(state,output,u)\n        state['failed_leg_public_capacity']=failed_leg_public_budget(state,u)",
      "        state['failed_leg_public_capacity']=protected_capacity(failed_leg_public_budget(state,u),u)\n        protected_preflight(state,source,output,u,tools,manifest)\n        require_native_for_pair(state,output,u)")
    code=substitute(code,"            need(state['completed']==list(STEPS) and not state['failed'],'EPISODE_INCOMPLETE')",
      "            if state['failed']:\n                protected_failed_finalize(state,source,output,u,tools,manifest,deadline)\n            need(state['completed']==list(STEPS) and not state['failed'],'EPISODE_INCOMPLETE')")
    code=substitute(code,"p.add_argument('--emit-review',action='store_true')","p.add_argument('--emit-review',action='store_true');p.add_argument('--emit-protected',action='store_true')")
    code=substitute(code,"need(sum((bool(a.step),bool(a.emit_public),bool(a.emit_review)))==1,'MODE_REFUSED')", "need(sum((bool(a.step),bool(a.emit_public),bool(a.emit_review),bool(a.emit_protected)))==1,'MODE_REFUSED')")
    code=substitute(code,'    if a.emit_public:\n',"    if a.emit_protected:\n        protected_emit(source,output,u);return 0\n    if a.emit_public:\n")
    ast.parse(code);files[PREFIX+'run.py']=code.encode()
    workflow=files['.github/workflows/dg16-r5-full-g2.yml'].decode().replace('pro/dg16-r5-full-g2-current-01-20261106',BRANCH)
    workflow=workflow.replace('cc5686eaac81e8c3d21eb965dad4114ee935192e321c672e26d359fd8fadb7d7',sha(code.encode()))
    oldpaths='      - qualification/dg16-r5-full-g2/run.py\n'
    additions=sorted(set(files)-{str(p.relative_to(INPUT/'base_public')) for p in (INPUT/'base_public').rglob('*') if p.is_file()})
    # Actual-input filenames are declared even in the unbound structural stage.
    additions=sorted(set(additions)|{PREFIX+'PROTECTED_RECIPIENT.json',PREFIX+'PROTECTED_RECIPIENT.pem'})
    workflow=substitute(workflow,oldpaths,oldpaths+''.join('      - '+p+'\n' for p in additions))
    workflow+='''
      - name: Read back separate encrypted diagnostic eligibility
        id: protected_emit
        if: always() && steps.emit.outcome == 'success' && steps.emit.outputs.eligible == 'true'
        continue-on-error: true
        shell: bash
        run: |
          set -euo pipefail
          adapter="$GITHUB_WORKSPACE/packet/qualification/dg16-r5-full-g2/run.py"
          actual="$(/usr/bin/sha256sum "$adapter")"
          actual="${actual%% *}"
          if [[ "$actual" != '__ADAPTER_SHA__' ]]; then
            echo 'eligible=false' >> "$GITHUB_OUTPUT"
            exit 1
          fi
          /usr/bin/python3 -I -S -B "$adapter" --emit-protected \\
            --source "$GITHUB_WORKSPACE/qualified-source" \\
            --output "$RUNNER_TEMP/dg16-full-g2-episode-$GITHUB_RUN_ID-$GITHUB_RUN_ATTEMPT" >> "$GITHUB_OUTPUT"

      - name: Upload only the separately eligible encrypted failed-stream role
        if: always() && steps.protected_emit.outcome == 'success' && steps.protected_emit.outputs.eligible == 'true'
        continue-on-error: true
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02
        with:
          name: dg16-g2-failed-streams-${{ github.run_id }}-a1
          path: |
            ${{ runner.temp }}/dg16-full-g2-episode-${{ github.run_id }}-${{ github.run_attempt }}/private/full-pair/failure-carrier/FAILURE_ENVELOPE.json
            ${{ runner.temp }}/dg16-full-g2-episode-${{ github.run_id }}-${{ github.run_attempt }}/private/full-pair/failure-carrier/FAILED_STREAMS.cms
          if-no-files-found: error
          include-hidden-files: false
          retention-days: 7
          compression-level: 0
'''.replace('__ADAPTER_SHA__',sha(code.encode()))
    files['.github/workflows/dg16-r5-full-g2.yml']=workflow.encode()
    return files

PRIVATE_REQUEST_HELPER='''def diagnostic_request(files,result):
    # Public validation runs in this fenced process. Only this data object
    # crosses into a separately admitted private decrypt process later.
    need(result['kind']=='terminal' and type(result['terminal_log_join']) is dict
      and result['terminal_log_join'].get('all_seven_exact') is True,'PRIVATE_REQUEST_REQUIRES_COMPLETE_PUBLIC_LOG_JOIN')
    b,_,_,modules,_,_=verified();docs={name:strict(files[name]) for name in NAMES}
    failure=docs['FAILURE.json'];need(failure['present'] is True,'PRIVATE_REQUEST_REQUIRES_FAILURE')
    ctx={k:docs['RESULT.json'][k] for k in ('repository','branch','run_id','run_attempt','workflow_commit')}
    ctx.update(source_commit=b['source_commit'],source_tree=b['source_tree'],
      workflow_path='.github/workflows/dg16-r5-full-g2.yml',job_name='full-registry-raw-pair')
    parent,u=modules['run.py'],modules['host_utility.py']
    protected=parent.load_protected(u).validate_public(docs['PROBE.json'],failure,ctx,u)
    need(protected['retention'] is not None and protected['retention']['status']=='ENCRYPTED_LOCAL_NOT_PROVIDER_RECEIVED',
      'PRIVATE_REQUEST_ENCRYPTED_COPY_NOT_READY')
    value=dict(schema='dg16.protected-full-private-diagnostic-request.v1',authority='NONE',context=ctx,
      public_receiver_binding_sha256=BINDING_SHA,public_archive=result['metadata']['archive'],
      public_receiving=desc(encode(result)),terminal_log_join=result['terminal_log_join'],
      failure_projection=failure['capture_observation'],protected_receipt=failure['protected_streams'],
      protected_capability=docs['PROBE.json']['protected_capability'],private_key_or_body_present=False,original_acceptance=False)
    need(len(encode(value))<=65536,'PRIVATE_REQUEST_BOUND');return value

'''

def prepared_receiver(final=None,bindings=None,runtime=None):
    """No genuine decision or current tree is created by this generator.

    Once root has a sealed public candidate and actual four decisions, it may
    supply the exact two bindings and actual root review selection. Until then only explicit unbound templates
    are produced; no predecessor decision/path/tree is transplanted.
    """
    public=prepared_public(final);old=json.loads(read(INPUT/'receiver/BINDING.json'))
    runtime=validate_runtime_input(runtime,final) if runtime is not None else None
    runtime_raw=encode(runtime) if runtime is not None else None
    runtime_desc=desc(runtime_raw) if runtime_raw is not None else None
    session=runtime['session'] if runtime is not None else None
    workspace=Path(runtime['workspace_root']) if runtime is not None else None
    receiver_output=Path(runtime['receiver_output_root']) if runtime is not None else None
    historical_workspace=Path('/workspace/scratch/6746ee3422fa')
    excluded=[historical_workspace/n for n in CONVENTIONAL_SOURCE_NAMES]
    if runtime is not None:
        excluded.append(Path(runtime['maintained_source_root']))
        excluded.extend(base/n for base in (workspace,workspace.parent) for n in CONVENTIONAL_SOURCE_NAMES)
    code=read(INPUT/'receiver/receiver.py').decode()
    code=substitute(code,"ROOT=Path('/workspace/scratch/6746ee3422fa')",
      'ROOT='+('Path('+repr(str(workspace))+')' if workspace is not None else 'None')+
      '\nRUNTIME_BINDING_SHA='+repr(runtime_desc['sha256'] if runtime_desc else None)+
      '\nMAINTAINED_SOURCE_ROOTS=tuple(Path(p) for p in '+repr(tuple(str(p) for p in excluded))+')')
    code=substitute(code,"RECEIVER_OUT=ROOT/'successor/g2-current-full-actual-receiving'",
      'RECEIVER_OUT='+('Path('+repr(str(receiver_output))+')' if receiver_output is not None else 'None'))
    code=substitute(code,"args[0].co_filename.startswith(str(ROOT/n)+'/') for n in ('source','source-codex-home','source-3e','source-8ee4','source-ea61','source-current')",
      "args[0].co_filename.startswith(str(root)+'/') for root in MAINTAINED_SOURCE_ROOTS")
    code=substitute(code,'def verified():',"""def verified():
    need(type(RUNTIME_BINDING_SHA) is str,'SUCCESSOR_RUNTIME_BINDING_REQUIRED')
    runtime_raw=acquire(HERE/'SUCCESSOR_RUNTIME_BINDING.json',16384)
    need(sha(runtime_raw)==RUNTIME_BINDING_SHA,'SUCCESSOR_RUNTIME_BINDING_CHANGED')""")
    code=substitute(code,"BINDING_SHA='022cf314b92282ac0aaf959b4ceb6ac9a6aca74059f8d8d3e5dfd1fe294aac57'",'BINDING_SHA=__PUBLIC_BINDING_SHA__')
    code=substitute(code,"{'schema','present','failures','capture_observation'}","{'schema','present','failures','capture_observation','protected_streams'}")
    code=substitute(code,"{'schema':'dg16.full-registry-episode-failure.v1','present':False,'failures':[],'capture_observation':None}",
      "{'schema':'dg16.full-registry-episode-failure.v1','present':False,'failures':[],'capture_observation':None,'protected_streams':None}")
    code=substitute(code,"    native_projection=probe['native_prerequisite']", """    ctx=dict(repository=b['repository'],branch=b['branch'],run_id=run_id,run_attempt=1,workflow_commit=workflow_commit,
      source_commit=b['source_commit'],source_tree=b['source_tree'],workflow_path='.github/workflows/dg16-r5-full-g2.yml',job_name='full-registry-raw-pair')
    need('protected_capability' in probe,'PROTECTED_CAPABILITY_FIELD_REQUIRED')
    protected=parent.load_protected(utility).validate_public(probe,failure,ctx,utility)
    native_projection=probe['native_prerequisite']""")
    code=substitute(code,"'supplement_present':observation is not None,'native':native_observation,'captures':capture_observation}",
      "'supplement_present':observation is not None,'native':native_observation,'captures':capture_observation,'protected':protected}")
    code=substitute(code,'def main():',PRIVATE_REQUEST_HELPER+'def main():')
    code=substitute(code,"parser.add_argument('--terminal-log',type=Path);parser.add_argument('--prepared',type=Path);args=parser.parse_args()",
      "parser.add_argument('--terminal-log',type=Path);parser.add_argument('--prepared',type=Path);parser.add_argument('--private-diagnostic-request',type=Path);args=parser.parse_args()")
    code=substitute(code,"    print(encode(result).decode(),end='')", """    if args.private_diagnostic_request:
        target=args.private_diagnostic_request.absolute()
        need(target.name=='PRIVATE_DIAGNOSTIC_REQUEST.json' and target.parent.resolve(strict=True)==target.parent
          and target.is_relative_to(RECEIVER_OUT) and not os.path.lexists(target),'PRIVATE_REQUEST_OUTPUT_SCOPE')
        body=encode(diagnostic_request(files,result))
        with os.fdopen(os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600),'wb') as stream:
            stream.write(body);stream.flush();os.fsync(stream.fileno())
        need(acquire(target,65536)==body,'PRIVATE_REQUEST_READBACK')
    print(encode(result).decode(),end='')""")
    component_pins=json.loads(read(INPUT/'capacity_r1/CODE_MANIFEST.json'))['members']
    names=set(old['modules'])|set(component_pins)|{'protected_bridge.py','protected_preflight.py'}
    if final:names|={'PROTECTED_RECIPIENT.json','PROTECTED_RECIPIENT.pem'}
    expected_modules={n:desc(public[PREFIX+n]) for n in sorted(names)}
    public_binding=dict(old)
    reset=('candidate_path candidate_seal_sha256 code_review_seal_sha256 composition_path composition_seal_sha256 '
      'composition_sha256 final_tree native_gate_sha256 native_review_seal_sha256 policy_gate_sha256 public_adoption_sha256 '
      'public_native_adoption_sha256 public_native_review_sha256 public_review_sha256').split()
    for name in reset:public_binding[name]=None
    public_binding.update(branch=BRANCH,control_branch=CONTROL,session=session,modules=expected_modules,
      successor_runtime_binding=runtime_desc,composition_review_reviewer=None,composition_review_selection=None)
    root_binding=dict(schema='dg16.protected-full-root-receiver-binding.v1',authority='NONE',repository=old['repository'],
      source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,branch=BRANCH,final_tree=None,session=session,
      successor_runtime_binding=runtime_desc,
      component_seal_sha256=COMPONENT_SEAL,component_index_sha256=COMPONENT_INDEX,component_members=component_pins,
      actual_component_review_received=False,actual_maximum_qualification_received=False,
      recipient=desc(final['certificate']) if final else None,public_recipient_adoption=desc(final['selection_raw']) if final else None,
      public_receiver_binding=None,workflow_sha256=sha(public['.github/workflows/dg16-r5-full-g2.yml']),
      effect_grant=False,original_awards=[])
    review_selection_raw=None
    if bindings is not None:
        need(runtime is not None,'SUCCESSOR_RUNTIME_BEFORE_FINAL_RECEIVER_BINDING')
        need(final is not None,'RECIPIENT_BEFORE_FINAL_RECEIVER_BINDING');exact(bindings,'public root review_selection')
        b=bindings['public'];r=bindings['root'];exact(b,' '.join(public_binding));exact(r,' '.join(root_binding))
        for key,wanted in public_binding.items():
            if key not in reset+['composition_review_reviewer','composition_review_selection']:
                need(type(b[key]) is type(wanted) and b[key]==wanted,'ACTUAL_PUBLIC_BINDING_FIXED_FIELDS')
        for name in reset:
            need(type(b[name]) is str and (Path(b[name]).is_absolute() if name.endswith('_path') else
              re.fullmatch('[0-9a-f]{40}',b[name]) is not None if name=='final_tree' else digest(b[name])),
              'ACTUAL_COMPOSITION_INPUT_REQUIRED')
        need(b['candidate_path']!=old['candidate_path'] and b['composition_path']!=old['composition_path'],
          'OLD_CONSUMED_COMPOSITION_REFUSED')
        selection_path=Path(bindings['review_selection'].get('path',''))
        need(selection_path.is_relative_to(WORKSPACE/'coordinator') and selection_path.suffix=='.json',
          'ACTUAL_ROOT_REVIEW_SELECTION_PATH')
        review_selection_raw=public_record(bindings['review_selection'],16384)
        exact(b['composition_review_selection'],'bytes sha256')
        need(b['composition_review_selection']==desc(review_selection_raw),'ACTUAL_ROOT_REVIEW_SELECTION_DESCRIPTOR')
        validate_review_selection(json.loads(review_selection_raw),b)
        expected=dict(root_binding,final_tree=b['final_tree'],actual_component_review_received=True,
          actual_maximum_qualification_received=True,public_receiver_binding=desc(encode(b)))
        need(r==expected,'ACTUAL_ROOT_PUBLIC_BINDING_JOIN');public_binding=b;root_binding=r
    public_raw=encode(public_binding);root_raw=encode(root_binding)
    code=code.replace('__PUBLIC_BINDING_SHA__',repr(sha(public_raw)) if bindings is not None else 'None');ast.parse(code)
    files={'public_receiver.py':code.encode(),'native_public.py':read(INPUT/'receiver/native_public.py'),
      'admission_gate.py':read(ROOT/'candidate/admission_gate.py')}
    if review_selection_raw is not None:files['FINAL_REVIEW_SELECTION.json']=review_selection_raw
    live=read(INPUT/'receiver/prepare_live_control.py').decode()
    live=substitute(live,"ROOT = Path('/workspace/scratch/6746ee3422fa')",
      'ROOT = '+('Path('+repr(str(workspace))+')' if workspace is not None else 'None'))
    live=substitute(live,"HERE = ROOT/'successor/coordinator'",
      "HERE = ROOT/'coordinator' if ROOT is not None else None")
    live=substitute(live,"RECEIVER = HERE/'g2-current-full-receiver'","RECEIVER = Path(__file__).resolve().parent")
    live=substitute(live,"COMPOSITION = HERE/'g2-current-full-composition'","COMPOSITION = Path("+repr(public_binding['composition_path'])+")" if bindings is not None else 'COMPOSITION = None')
    live=substitute(live,"LIVE = ROOT/'successor/g2-current-full-actual-receiving/live'",
      'LIVE = '+('Path('+repr(str(receiver_output/'live'))+')' if receiver_output is not None else 'None'))
    live=substitute(live,"LIVE/'METADATA.json'","LIVE/'PUBLIC_METADATA.json'")
    live=substitute(live,"OUT = HERE/'g2-current-full-live-control'","OUT = HERE/'g2-protected-full-live-control-current03' if HERE is not None else None")
    live=substitute(live,"RECEIVER/'receiver.py'","RECEIVER/'public_receiver.py'")
    live=substitute(live,"    review_dir = Path(selected['independent_review_directory']).resolve(strict=True)\n    assert review_dir.is_relative_to(ROOT/'successor')",
      "    review_dir = review_directory(selected['independent_review_directory'])")
    live=substitute(live,'def main():',"""def review_directory(path):
    if ROOT is None:raise ValueError('SUCCESSOR_RUNTIME_BINDING_REQUIRED')
    reviewed=Path(path).resolve(strict=True)
    if reviewed==ROOT or not reviewed.is_relative_to(ROOT):raise ValueError('SUCCESSOR_REVIEW_DIRECTORY_SCOPE')
    return reviewed


def main():""")
    if bindings is None:live=substitute(live,'def main():',"def main():\n    raise ValueError('FINAL_RECEIVER_BINDING_REQUIRED')")
    ast.parse(live);files['prepare_live_control.py']=live.encode()
    for name in component_pins:files['component/'+name]=read(INPUT/'capacity_r1'/name)
    common=read(ROOT/'candidate/root_common.py').decode()
    common=substitute(common,'ROOT_SESSION=None','ROOT_SESSION='+repr(session))
    ast.parse(common);files['root_common.py']=common.encode()
    acquire=read(ROOT/'candidate/root_acquire.py').decode().replace('ROOT_BINDING_SHA=None','ROOT_BINDING_SHA='+repr(sha(root_raw)) if bindings is not None else 'ROOT_BINDING_SHA=None')
    acquire=acquire.replace('COMMON_SHA=None','COMMON_SHA='+repr(sha(files['root_common.py'])));ast.parse(acquire);files['root_acquire.py']=acquire.encode()
    helpers={n:desc(files[n]) for n in ('root_common.py','root_acquire.py')}
    for name in ('resolve_body.py','private_receive.py'):
        body=read(ROOT/'candidate'/name).decode().replace('ROOT_BINDING_SHA=None','ROOT_BINDING_SHA='+repr(sha(root_raw)) if bindings is not None else 'ROOT_BINDING_SHA=None')
        if name=='private_receive.py':body=substitute(body,'ROOT_SESSION=None','ROOT_SESSION='+repr(session))
        body=body.replace('HELPER_PINS={}','HELPER_PINS='+repr(helpers));ast.parse(body);files[name]=body.encode()
    if runtime_raw is not None:files['SUCCESSOR_RUNTIME_BINDING.json']=runtime_raw
    files['BINDING.json' if bindings is not None else 'BINDING_TEMPLATE.json']=public_raw
    files['ROOT_BINDING.json' if bindings is not None else 'ROOT_BINDING_TEMPLATE.json']=root_raw
    return files

def prepare(output,actual=None,receiver_bindings=None,runtime=None):
    output=Path(output).absolute()
    need((output.is_relative_to(ROOT) or output.is_relative_to(WORKSPACE/'coordinator'))
      and output.parent.resolve(strict=True)==output.parent and not os.path.lexists(output),'FRESH_OWNED_GENERATOR_OUTPUT')
    final=validate_final_input(actual) if actual is not None else None
    runtime=validate_runtime_input(runtime,final) if runtime is not None else None
    files=prepared_public(final);output.mkdir(mode=0o700)
    for name,raw in files.items():
        path=output/'candidate/public'/name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:stream.write(raw)
    rows=[dict(path=n,mode='100644',git_blob=blob(raw),**desc(raw)) for n,raw in sorted(files.items())]
    manifest=json.loads(files[PREFIX+'SOURCE_MANIFEST.json'])
    need(manifest['commit']==SOURCE_COMMIT and manifest['tree']==SOURCE_TREE and manifest['file_count']==1759
      and manifest['total_bytes']==166407881 and not {r['path'] for r in manifest['members']}.intersection(files),'MAINTAINED_SOURCE_UNCHANGED')
    value=dict(schema='dg16.protected-full-g2-generated-code.v1',authority='NONE',final_binding=final is not None,
      state='FINAL_CODE_BOUND_REQUIRES_ACTUAL_REVIEWS_DECISIONS_AND_ADMISSION' if final else 'STRUCTURAL_TEMPLATE_UNBOUND_NO_OPERATION',
      source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,branch=BRANCH,control_branch=CONTROL,
      source_members_changed=0,source_files=1759,source_bytes=166407881,public_additions=len(rows),members=rows,
      actual_policy_decisions_copied=False,actual_recipient=desc(final['certificate']) if final else None,
      successor_runtime_binding=desc(encode(runtime)) if runtime is not None else None,
      private_custody_ready=False,local_native_currentness=False,actual_operation_admission=False,
      effect_grant=False,original_awards=[])
    (output/'PUBLIC_ADDITION_MANIFEST.json').write_bytes(encode(value))
    receiver=prepared_receiver(final,receiver_bindings,runtime)
    for name,raw in receiver.items():
        path=output/'receiver'/name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:stream.write(raw)
    (output/'RECEIVER_MANIFEST.json').write_bytes(encode(dict(schema='dg16.protected-root-receiver-template.v1',authority='NONE',
      final_composition_binding=receiver_bindings is not None,actual_operation_admission=False,
      successor_runtime_binding=desc(encode(runtime)) if runtime is not None else None,
      private_custody_ready=False,local_native_currentness=False,
      members={n:desc(raw) for n,raw in sorted(receiver.items())})))
    return value

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--actual-input',type=Path)
    p.add_argument('--receiver-bindings',type=Path)
    p.add_argument('--runtime-binding',type=Path)
    args=p.parse_args();actual=json.loads(read(args.actual_input,65536)) if args.actual_input else None
    receiver_bindings=json.loads(read(args.receiver_bindings,131072)) if args.receiver_bindings else None
    runtime=json.loads(read(args.runtime_binding,16384)) if args.runtime_binding else None
    value=prepare(args.out,actual,receiver_bindings,runtime);print(json.dumps({k:value[k] for k in ('state','public_additions','final_binding','effect_grant')},sort_keys=True))
