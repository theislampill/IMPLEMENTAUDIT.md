"""Compile-bound supplementary retention. No effect on import or public receiving."""
import hashlib,json,os,sys,time,types
from pathlib import Path

COMPONENT_PINS = {'CAPTURE_DIAGNOSTIC_CATALOG.json': {'bytes': 670575, 'sha256': 'b5321499719c129b71fb3b0dba82b23582a153f830bce98005b655563894632b'}, 'bound_child.py': {'bytes': 1433, 'sha256': 'fccb0177e87989b7efa728f5d9c5618eddd4261df8015a3b85469be165833915'}, 'capture_evidence.py': {'bytes': 49224, 'sha256': '39d8ea138dedfce118a7b2a8e040c42cec1631e99065a2d0dc855e53bdcbdca2'}, 'fs_carrier.py': {'bytes': 21303, 'sha256': 'a6eeaba52927e084194249feee364e9cad567bff09b2771cbd4da44f8111daf4'}, 'fs_command.py': {'bytes': 5275, 'sha256': '6e9c18cf0635c07ed9530a69a14efe281145ab9aacce61a6bfd68bc5dae08804'}, 'fs_io.py': {'bytes': 8395, 'sha256': '42563b4b9848baf1e68086e3867cbcdcbd26b21bd28509a0b228d39bba6a71d0'}, 'fs_protocol.py': {'bytes': 11796, 'sha256': '7f0ba8b2836f0273d6bde8b5a55aece03e62205aa5ae00d190d863ec7f8ad08e'}, 'fs_runner.py': {'bytes': 12295, 'sha256': '90f17ef142c268199062d44b4ea3b96194ef5ab9c7d7f358a13f0b6c15fba790'}, 'fs_transport.py': {'bytes': 3651, 'sha256': 'ce1e627021e531843d869f35c34001ef7e7f13b4ad09f18d55d58fed13431081'}, 'full_g2_hooks.py': {'bytes': 8458, 'sha256': '7628608fa2e6c083fd26b7c6ec9d588d60959c5baa5100ca34f15be14afe7107'}}
COMPONENT_SEAL = '58f59f2597bd2223c0ecfa8fbbbf2a81e03964d00027c037fde369f685fb570a'
COMPONENT_MANIFEST_SHA = 'fdaee3f0655e41d5bd025cdd36d1d0bd3b183be907769b05c7c541657bb745c6'
PREFLIGHT_SHA = 'ead48287bb511a6d6483946d725f6bc9ec79aac21ce582ac9b14822eff12a359'
SELECTION_SHA = '8a2b932e01672ba15f198ee8b4faf50c8043b97d07bc8efa3037a1450f2a4ed0'
BOUND = True
BRANCH = 'pro/dg16-r5-full-g2-direct-host-03-20261110'
CONTROL_BRANCH = 'pro/dg16-r5-full-g2-direct-control-03-20261110'
HOST_SELECTION_EXPECTED = {'actor': '/root', 'automatic_retry': False, 'branch': 'pro/dg16-r5-full-g2-direct-host-03-20261110', 'component_code_manifest_sha256': 'fdaee3f0655e41d5bd025cdd36d1d0bd3b183be907769b05c7c541657bb745c6', 'component_seal_sha256': '58f59f2597bd2223c0ecfa8fbbbf2a81e03964d00027c037fde369f685fb570a', 'control_branch': 'pro/dg16-r5-full-g2-direct-control-03-20261110', 'effect_grant': False, 'host_gate': 'MAXIMUM_OPAQUE_PLAINTEXT_ENCRYPTION_BEFORE_EITHER_MAINTAINED_LEG', 'host_qualification': {'independent': {'bytes': 4255, 'sha256': '22dbfeadc5b39a2416f3b99eaa94e7e856a114a316bb413c9503471416f9a468'}, 'provider': {'bytes': 5375, 'sha256': '67e88efebe9ca3d00ffc628f72174f5cc94081d1c7456ae8648bf22065230fb7'}, 'public': {'bytes': 8404, 'sha256': 'fcdca4d8152e6a4fc4035de1c00f4e5c892cdf5e7fd9d354278810c198ea969e'}, 'root': {'bytes': 2324, 'sha256': '8e4c0952e031a14d898ee3f94c9a5f5d040870d215ad772938d705f39ffcb31c'}, 'source_root': {'bytes': 1962, 'sha256': 'e017c77887178387ab4af6de49c2f477988c33a5ee92ca7f67770121db7cbd59'}}, 'isolated_maximum_encrypt_capture_received': True, 'issuer_thread': '01a1953f-a15b-7811-aa72-3538ebb03562', 'original_awards': [], 'private_authenticated_interoperability': 'NOT_ESTABLISHED_BY_THIS_ADOPTION', 'private_key_on_host': False, 'recipient': {'bytes': 1411, 'sha256': '3b90dc0a7e3676981f374a079a1cf3d375da3c1217b1ed5bff60b2c79277f5e4'}, 'root_receiving': {'bytes': 2324, 'sha256': '8e4c0952e031a14d898ee3f94c9a5f5d040870d215ad772938d705f39ffcb31c'}, 'schema': 'dg16.protected-full-g2-direct-host-recipient-adoption.v2', 'source_commit': '08e6faa9a71fc09996a32e114346dce6508ef656', 'source_tree': '83165996af29c20f526f53a9dc6c4d8edfec4be5', 'status': 'ACTUAL_RECIPIENT_AND_QUALIFIED_HOST_PROFILE_SELECTED'}
LOAD_ORDER=('fs_protocol','fs_io','fs_command','fs_carrier','full_g2_hooks','fs_runner','fs_transport')

def need(value,code):
    if not value:raise ValueError(code)
def desc(raw):return dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())

def load_preflight(u):
    path=Path(__file__).with_name('protected_preflight.py');raw=u.checked_file(path,32768)
    need(desc(raw)['sha256']==PREFLIGHT_SHA,'PROTECTED_PREFLIGHT_CODE_PIN')
    module=types.ModuleType('protected_host_preflight');module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__);return module

def load_components(u):
    root=Path(__file__).parent;raws={name:u.checked_file(root/name,1024**2) for name in COMPONENT_PINS}
    need(all(desc(raw)==COMPONENT_PINS[name] for name,raw in raws.items()),'PROTECTED_COMPONENT_PIN')
    previous={name:sys.modules.get(name) for name in LOAD_ORDER};modules={}
    try:
        for name in LOAD_ORDER:
            module=types.ModuleType(name);module.__file__=str(root/(name+'.py'))
            sys.modules[name]=module
            exec(compile(raws[name+'.py'],module.__file__,'exec'),module.__dict__);modules[name]=module
    finally:
        for name,old in previous.items():
            if old is None:sys.modules.pop(name,None)
            else:sys.modules[name]=old
    need(all(u.checked_file(root/name,1024**2)==raw for name,raw in raws.items()),'PROTECTED_COMPONENT_CLOSING')
    return modules

def selection(u):
    # Exact Root source adoption is separate from private-role authentication.
    # Byte equality supplies no provenance; Root receives issuer history later.
    need(BOUND is True and type(SELECTION_SHA) is str,'PROTECTED_FINAL_BINDING_REQUIRED')
    raw=u.checked_file(Path(__file__).with_name('PROTECTED_RECIPIENT.json'),16384)
    need(desc(raw)['sha256']==SELECTION_SHA,'PROTECTED_ROOT_SELECTION_CHANGED')
    value=u.parse_json(raw)
    need(type(value) is dict and set(value)==set(HOST_SELECTION_EXPECTED)
      and all(type(value[k]) is type(v) and value[k]==v for k,v in HOST_SELECTION_EXPECTED.items()),
      'PROTECTED_ACTUAL_HOST_ONLY_SELECTION_SCOPE')
    cert=u.checked_file(Path(__file__).with_name('PROTECTED_RECIPIENT.pem'),8192)
    need(desc(cert)==value['recipient'],'PROTECTED_PUBLIC_RECIPIENT_CHANGED')
    return value,raw,cert

def reserve_capacity(value,u):
    selection(u)
    result=load_components(u)['full_g2_hooks'].reserve_public_capacity(value)
    maxima=dict(result['maximum_bytes']);maxima['PROBE.json']+=load_preflight(u).PUBLIC_MAX
    encoded={name:2*size+256 for name,size in maxima.items()}
    need(all(v<=65536-2000 for v in maxima.values()) and sum(maxima.values())<=262144-2000
      and max(encoded.values())<=262144-2000 and sum(encoded.values())<=1048576-2000,
      'PROTECTED_CAPABILITY_PUBLIC_CAPACITY_REFUSED')
    return dict(result,maximum_bytes=maxima,raw_upper=sum(maxima.values()),encoded_upper=sum(encoded.values()))

def preflight(parent,state,source,output,u,tools,manifest):
    return load_preflight(u).observe(parent,types.SimpleNamespace(**globals()),state,source,output,u,tools,manifest)

def validate_public(probe,failure,ctx,u):
    modules=load_components(u);P=modules['fs_protocol'];H=modules['full_g2_hooks'];selected=selection(u)[0]
    need('protected_capability' in probe and 'protected_streams' in failure,'PROTECTED_PUBLIC_FIELDS')
    value=probe['protected_capability']
    if value is not None:
        load_preflight(u).validate_public(value,ctx,P,started=probe['started'])
        if value['recipient_sha256'] is not None:need(value['recipient_sha256']==selected['recipient']['sha256'],'CAPABILITY_RECIPIENT_BINDING')
    else:need(probe['started'] is False,'PAIR_WITHOUT_SAME_HOST_CAPABILITY')
    receipt=failure['protected_streams']
    if receipt is not None:
        need(failure['present'] is True,'PROTECTED_RECEIPT_WITHOUT_FAILURE');H.validate_public_receipt(receipt,ctx)
        if receipt['status']=='ENCRYPTED_LOCAL_NOT_PROVIDER_RECEIVED':
            need(value is not None and value['status']==load_preflight(u).POSITIVE
              and receipt['recipient_sha256']==value['recipient_sha256']==selection(u)[0]['recipient']['sha256'],
              'PROTECTED_READY_CAPABILITY_JOIN')
    return dict(capability=value,retention=receipt)

def failed_finalize(parent,state,source,output,u,tools,manifest,closing_deadline):
    """Original source/runtime/currentness was read immediately before entry.

    The callback repeats source/runtime/policy/host-input reads without creating
    a child while the crypto owner holds its exact primary. No controller call,
    provider fetch or signal/reaper policy is selected inside that callback.
    """
    modules=load_components(u);P=modules['fs_protocol'];F=modules['fs_io'];R=modules['fs_carrier'];H=modules['full_g2_hooks'];E=modules['fs_runner']
    state['protected_closing_deadline_monotonic']=closing_deadline
    outcome=R.neutral('REFUSED','RETENTION_COMPOSITION_UNBOUND');outcome['crypto_child_custody']='NOT_STARTED'
    entered=False;returned=False
    try:
        adopted,adoption_raw,cert=selection(u)
        context=dict(state['context'],source_commit=P.SOURCE_COMMIT,source_tree=P.SOURCE_TREE,
          workflow_path='.github/workflows/dg16-r5-full-g2.yml',job_name='full-registry-raw-pair')
        P.context(context);need(context['branch']==BRANCH,'PROTECTED_ACTUAL_BRANCH')
        need(state['docs']['PROBE.json']['started'] is True,'MAINTAINED_LEG_NOT_STARTED')
        load_preflight(u).validate_public(state['docs']['PROBE.json']['protected_capability'],context,P,started=True)
        capability_root=Path(output)/'private/protected-capability'
        with F.Directory(capability_root) as directory:
            capability_raw=R.small(directory,'STATE.json',16384,lambda:None);capability=P.parse(capability_raw,16384)
        need(capability['public']==state['docs']['PROBE.json']['protected_capability']
          and capability['context']==context and capability['selection']==desc(adoption_raw)
          and capability['tool_pins']==state['protected_host_tool_pins'],'PROTECTED_CAPABILITY_PRIVATE_JOIN')
        def current():
            need(time.monotonic()<state['deadline_monotonic'] and time.monotonic()<closing_deadline,'PROTECTED_ORIGINAL_DEADLINE')
            need(parent.host_context(output,source,'protected-retention')==state['context'],'PROTECTED_HOST_CONTEXT_CHANGED')
            try:
                fact=parent.verify_source(source,manifest,u,state['run_root'] is not None)
                need(fact==state['docs']['SOURCE.json']['after'],'PROTECTED_SOURCE_BOOKEND_CHANGED')
            except BaseException:
                state['docs']['CLEANUP.json']['source_unchanged']=False;raise
            try:need(state['runtime'] is not None and parent.runtime_snapshot(source,state,u)==state['runtime'],'PROTECTED_RUNTIME_CHANGED')
            except BaseException:
                state['docs']['CLEANUP.json']['runtime_unchanged_after_initialization']=False;raise
            need(parent.actual_policy_adoption(u)==state['policy_adoption'],'PROTECTED_POLICY_ADOPTION_CHANGED')
            selected,body,current_cert=selection(u)
            need(body==adoption_raw and selected==adopted and current_cert==cert,'PROTECTED_SELECTION_CLOSING')
            need(time.monotonic()<state['deadline_monotonic'] and time.monotonic()<closing_deadline,'PROTECTED_ORIGINAL_DEADLINE')
        current()
        root=Path(output)/'private/protected-recipient'
        with F.create_directory(root) as directory:
            with F.Output(directory,'recipient.pem',8192) as held:
                held.write(cert);need(held.descriptor(current)==adopted['recipient'],'PROTECTED_STAGED_RECIPIENT')
            observed={};tool_pins={}
            for name in ('openssl','python3'):
                path,fact=u.trusted(name);need(path is not None,'PROTECTED_TRUSTED_TOOL_UNAVAILABLE')
                if name=='openssl':need(path=='/usr/bin/'+name,'PROTECTED_FIXED_TOOL_PATH')
                else:need(path==tools['python3'],'PROTECTED_INTERPRETER_CHANGED')
                observed[name]=fact;tool_pins[path]={k:fact[k] for k in ('bytes','sha256')}
            need(tool_pins==capability['tool_pins'],'ACTUAL_HOST_TOOL_CHANGED_AFTER_CAPABILITY')
            R.store(directory,'STATE.json',dict(schema='dg16.protected-host-actual-tool-observation.v1',authority='NONE',
              context=context,tools=observed,root_selection=desc(adoption_raw),
              same_host_capability=desc(capability_raw),host_crypto_previously_observed=True,original_acceptance=False),16384)
        check=lambda:need(time.monotonic()<min(state['deadline_monotonic'],closing_deadline),'PROTECTED_ORIGINAL_DEADLINE')
        outside=F.usage(capability_root,check);recipient_usage=F.usage(root,check)
        inside=F.usage(Path(output)/'private/full-pair',check)
        projection=parent.read_failed_leg_observation(output,u)
        frame=P.make_manifest(context,projection,adopted['recipient'])
        # The component's full-pair census is supplemented by the already
        # retained same-host records and public certificate outside that tree.
        # Its complete auxiliary reserve remains additional, never shared twice.
        state['protected_shared_allocation']=P.allocation(inside['bytes']+outside['bytes']+recipient_usage['bytes'],
          inside['entries']+outside['entries']+recipient_usage['entries'],P.plain_size(len(P.encode(frame)),frame['streams']))
        executor=E.Executor(source/'scripts/qualify-work-graph-verifier.py',tools['python3'],tool_pins,COMPONENT_PINS,current)
        chosen=dict(schema='dg16.protected-stream-root-selection.v1',context=context,
          recipient=adopted['recipient'],root_receiving=adopted['root_receiving'])
        entered=True
        outcome=H.failed_finalize(state,output,chosen,root/'recipient.pem',executor,
          lambda:parent.read_failed_leg_observation(output,u),closing_deadline,current)
        returned=True
        current();closing=F.usage(Path(output)/'private/full-pair',check)
        need(closing['bytes']+outside['bytes']+recipient_usage['bytes']<=P.TOTAL_MAX,'PROTECTED_SHARED_CLOSING_ALLOCATION')
        return outcome
    except BaseException:
        # An unexpected crossing of the actual command path cannot be relabeled
        # NOT_STARTED. The original failure/public result remains independent.
        custody=outcome.get('crypto_child_custody','UNPROVED') if returned else 'UNPROVED' if entered else 'NOT_STARTED'
        outcome=R.neutral('INCOMPLETE' if custody=='UNPROVED' else 'REFUSED','SUPPLEMENTARY_RETENTION_REFUSED')
        outcome['crypto_child_custody']=custody
        H.add_public_receipt(state,outcome)
        return outcome

def emit_eligibility(parent,state,source,output,u):
    """Read-only exact-path eligibility; never encrypt, retry or claim upload."""
    value=state['docs']['FAILURE.json'].get('protected_streams')
    if value is None or value.get('status')!='ENCRYPTED_LOCAL_NOT_PROVIDER_RECEIVED':return False
    modules=load_components(u);P=modules['fs_protocol'];F=modules['fs_io'];R=modules['fs_carrier'];H=modules['full_g2_hooks']
    adopted,raw,cert=selection(u)
    ctx=dict(state['context'],source_commit=P.SOURCE_COMMIT,source_tree=P.SOURCE_TREE,
      workflow_path='.github/workflows/dg16-r5-full-g2.yml',job_name='full-registry-raw-pair')
    stop=min(state['deadline_monotonic'],state['protected_closing_deadline_monotonic'],time.monotonic()+30)
    def current():
        need(time.monotonic()<stop,'PROTECTED_ELIGIBILITY_DEADLINE')
        need(parent.host_context(output,source,'emit-protected')==state['context'],'PROTECTED_EMISSION_CONTEXT')
        need(selection(u)==(adopted,raw,cert),'PROTECTED_EMISSION_SELECTION')
        need(time.monotonic()<stop,'PROTECTED_ELIGIBILITY_DEADLINE')
    current();H.validate_public_receipt(value,ctx)
    root=Path(output)/'private/full-pair'
    with F.Directory(root/'failure-carrier') as directory:
        outcome=P.parse(R.small(directory,'RETENTION.json',4096,current),4096)
    copy=json.loads(json.dumps(state));need(H.add_public_receipt(copy,outcome)==value,'PROTECTED_PUBLIC_PRIVATE_STATUS_JOIN')
    paths=R.upload_paths(root,outcome,current)
    need(set(paths)==set(P.ARTIFACT_MEMBERS),'PROTECTED_UPLOAD_POPULATION')
    current();return True
