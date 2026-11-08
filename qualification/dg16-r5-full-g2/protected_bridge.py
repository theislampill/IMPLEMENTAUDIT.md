"""Compile-bound supplementary retention. No effect on import or public receiving."""
import hashlib,json,os,sys,time,types
from pathlib import Path

COMPONENT_PINS = {'CAPTURE_DIAGNOSTIC_CATALOG.json': {'bytes': 670575, 'sha256': '76382066ebf8077f04b47c0f1912527d7e92568845bc87855ab61006e5e52cdd'}, 'bound_child.py': {'bytes': 1433, 'sha256': 'df154b3cf1b8e70485ebf3900dbc7d1955b893765e4dc7ab0ef8d27fd7a38c0f'}, 'capture_evidence.py': {'bytes': 49224, 'sha256': '6171dce59df2dac0ab1618352cd9dffb6a9a071497c690bbc40d5c1097635aee'}, 'fs_carrier.py': {'bytes': 21303, 'sha256': 'a6eeaba52927e084194249feee364e9cad567bff09b2771cbd4da44f8111daf4'}, 'fs_command.py': {'bytes': 6160, 'sha256': 'cd6aae49b89fc3bc0da0a4c95bf903255f801eb2d8c811e5aaa52acd7299929c'}, 'fs_io.py': {'bytes': 8395, 'sha256': '42563b4b9848baf1e68086e3867cbcdcbd26b21bd28509a0b228d39bba6a71d0'}, 'fs_protocol.py': {'bytes': 11788, 'sha256': 'b44eedcc53a94fae84370241b6c5928b3bf34821e9e05ce8fb8dc516c800d541'}, 'fs_runner.py': {'bytes': 12305, 'sha256': 'b51f231146372c6e6fb9552fc29e71e4e951ab5561cf7632b95856c17e89ff97'}, 'fs_transport.py': {'bytes': 3651, 'sha256': 'ce1e627021e531843d869f35c34001ef7e7f13b4ad09f18d55d58fed13431081'}, 'full_g2_hooks.py': {'bytes': 8458, 'sha256': '7628608fa2e6c083fd26b7c6ec9d588d60959c5baa5100ca34f15be14afe7107'}}
COMPONENT_SEAL = 'e99a60d5790355ae39c0e4bbc4567add87e702775ade8f5655e2f3ef56bd9602'
COMPONENT_MANIFEST_SHA = '9d54e10f1c6d056d43801b8457f909030498704a766b17998abbc9c4525c28f3'
PREFLIGHT_SHA = '91773a1fc701b1ceb8be3e2ebe1ad89279bd9fa553a5ac12b831641540e854b9'
SELECTION_SHA = 'b0c465ee54634da10f606febb169a2114a6942aa383d17104bc4ef9c9d4d3a49'
BOUND = True
BRANCH = 'pro/dg16-r5-full-g2-current-03-20261107'
CONTROL_BRANCH = 'pro/dg16-r5-full-g2-current-control-03-20261107'
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
    need(BOUND is True and type(SELECTION_SHA) is str,'PROTECTED_FINAL_BINDING_REQUIRED')
    raw=u.checked_file(Path(__file__).with_name('PROTECTED_RECIPIENT.json'),16384)
    need(desc(raw)['sha256']==SELECTION_SHA,'PROTECTED_ROOT_SELECTION_CHANGED')
    value=u.parse_json(raw)
    need(value['schema']=='dg16.protected-full-g2-public-recipient-adoption.v1'
      and value['actor']=='/root' and value['status']=='ACTUAL_RECIPIENT_AND_QUALIFIED_PROFILE_SELECTED'
      and value['session']=='52e9b813fb80'
      and value['branch']==BRANCH and value['control_branch']==CONTROL_BRANCH
      and value['component_seal_sha256']==COMPONENT_SEAL
      and value['component_code_manifest_sha256']==COMPONENT_MANIFEST_SHA
      and value['source_commit']=='7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'
      and value['source_tree']=='6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e'
      and value['small_authenticated_qualified'] is True and value['maximum_capacity_qualified'] is True
      and value['host_gate']=='MAXIMUM_OPAQUE_PLAINTEXT_ENCRYPTION_BEFORE_EITHER_MAINTAINED_LEG'
      and value['private_key_on_host'] is False and value['effect_grant'] is False
      and value['automatic_retry'] is False and value['original_awards']==[],
      'PROTECTED_ACTUAL_SELECTION_SCOPE')
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
            for name in ('env','openssl','python3'):
                path,fact=u.trusted(name);need(path is not None,'PROTECTED_TRUSTED_TOOL_UNAVAILABLE')
                if name in ('env','openssl'):need(path=='/usr/bin/'+name,'PROTECTED_FIXED_TOOL_PATH')
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
