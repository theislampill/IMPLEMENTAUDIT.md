"""Same-host maximum encryption capability; never a maintained failed leg.

The opaque synthetic plaintext has exactly the protocol byte ceiling. It is
deliberately not a valid frame or producer projection and is never uploaded.
"""
import hashlib,os,time
from pathlib import Path

PUBLIC_MAX=2048
SCOPE='SAME_HOST_DIRECT_OPENSSL_MAXIMUM_OPAQUE_PLAINTEXT_ENCRYPTION_ONLY'
POSITIVE='OBSERVED_MAXIMUM_ENCRYPTION_WITH_COMPLETE_CUSTODY'

def need(ok,code):
    if not ok:raise ValueError(code)
def deadline_stop(started,overall,now):
    need(type(started) in (int,float) and type(overall) in (int,float) and type(now) in (int,float)
      and overall==started+8400 and started<=now<overall-7980,'PROTECTED_PREPAIR_BUDGET_UNAVAILABLE')
    # SETUP_SECONDS600 belongs only to the existing provisioning watchdog.
    return min(now+60,overall-7980)

class GateDeadline:
    def __init__(self,started,overall,clock=time.monotonic):
        self.clock=clock;self.stop=deadline_stop(started,overall,clock());self.check()
    def check(self):need(self.clock()<self.stop,'PROTECTED_HOST_CAPABILITY_DEADLINE')

TOOL_NAMES=('openssl','python3')
TOOL_REFUSALS=('TOOL_NOT_EXECUTABLE','TOOL_CUSTODY_REFUSED','PRIVILEGED_TOOL_REFUSED',
    'TOOL_CAPABILITY_UNKNOWN','FILE_SHAPE_REFUSED','FILE_CHANGED','TOOL_OS_REFUSAL','UNKNOWN_UTILITY_REFUSAL')
TOOL_CHECKS=('NOT_ENTERED','TRUSTED_LOOKUP','CANONICAL_PATH','DESCRIPTOR','COMPLETE')
TOOL_RESULTS=('NOT_ENTERED','IN_PROGRESS','PASSED','TRUST_REFUSED','PATH_REFUSED',
    'UNEXPECTED_EXCEPTION','UNEXPECTED_INTERRUPT')


def neutral_tool_check():
    return dict(tool=None,check='NOT_ENTERED',result='NOT_ENTERED',refusal=None,errno=None,canonical_equal=None)


def validate_tool_check(value,P):
    P.exact(value,'tool check result refusal errno canonical_equal')
    need(value['tool'] is None or value['tool'] in TOOL_NAMES,'TOOL_DIAGNOSTIC_TOOL')
    need(value['check'] in TOOL_CHECKS and value['result'] in TOOL_RESULTS,'TOOL_DIAGNOSTIC_STATE')
    need(value['errno'] is None or P.integer(value['errno'],0,4096),'TOOL_DIAGNOSTIC_ERRNO')
    need(value['canonical_equal'] is None or type(value['canonical_equal']) is bool,'TOOL_DIAGNOSTIC_EQUALITY')
    result=value['result'];check=value['check']
    if result=='NOT_ENTERED':
        need(value==neutral_tool_check(),'TOOL_DIAGNOSTIC_NOT_ENTERED')
    else:
        need(value['tool'] in TOOL_NAMES and check!='NOT_ENTERED','TOOL_DIAGNOSTIC_TOOL_JOIN')
        if result=='TRUST_REFUSED':
            need(check=='TRUSTED_LOOKUP' and value['refusal'] in TOOL_REFUSALS
              and value['canonical_equal'] is None,'TOOL_DIAGNOSTIC_TRUST_JOIN')
        elif result=='PATH_REFUSED':
            need(check=='CANONICAL_PATH' and value['refusal']=='PROTECTED_HOST_TOOL_PATH'
              and value['canonical_equal'] is False and value['errno'] is None,'TOOL_DIAGNOSTIC_PATH_JOIN')
        else:
            need(value['refusal'] is None and value['errno'] is None,'TOOL_DIAGNOSTIC_NO_UNBOUNDED_REASON')
            if result=='PASSED':
                need(check=='COMPLETE' and value['tool']=='python3' and value['canonical_equal'] is True,
                  'TOOL_DIAGNOSTIC_COMPLETE_JOIN')
            else:
                need(check in ('TRUSTED_LOOKUP','CANONICAL_PATH','DESCRIPTOR'),'TOOL_DIAGNOSTIC_EXCEPTION_JOIN')


def observe_tools(u,tools,diagnostic,deadline_type):
    observed={};pins={}
    for name in TOOL_NAMES:
        diagnostic.update(tool=name,check='TRUSTED_LOOKUP',result='IN_PROGRESS',refusal=None,errno=None,canonical_equal=None)
        try:
            path,fact=u.trusted(name)
            if path is None:
                code=fact.get('code') if type(fact) is dict else None
                number=fact.get('errno') if type(fact) is dict else None
                diagnostic.update(result='TRUST_REFUSED',refusal=code if code in TOOL_REFUSALS else 'UNKNOWN_UTILITY_REFUSAL',
                    errno=number if type(number) is int and 0<=number<=4096 else None)
            need(path is not None,'PROTECTED_HOST_TOOL_UNAVAILABLE')
            diagnostic['check']='CANONICAL_PATH'
            diagnostic['canonical_equal']=path==('/usr/bin/'+name if name!='python3' else tools['python3'])
            if not diagnostic['canonical_equal']:
                diagnostic.update(result='PATH_REFUSED',refusal='PROTECTED_HOST_TOOL_PATH')
            need(diagnostic['canonical_equal'],'PROTECTED_HOST_TOOL_PATH')
            diagnostic['check']='DESCRIPTOR'
            observed[name]=fact;pins[path]={k:fact[k] for k in ('bytes','sha256')}
        except BaseException as exc:
            if diagnostic['result']=='IN_PROGRESS':
                interrupted=isinstance(exc,(KeyboardInterrupt,SystemExit)) or (
                    isinstance(deadline_type,type) and issubclass(deadline_type,BaseException) and isinstance(exc,deadline_type))
                diagnostic['result']='UNEXPECTED_INTERRUPT' if interrupted else 'UNEXPECTED_EXCEPTION'
            raise
    diagnostic.update(check='COMPLETE',result='PASSED')
    return observed,pins


def validate_public(value,ctx,P,*,started=False):
    fields='schema authority status scope context_sha256 component_seal_sha256 recipient_sha256 tools opaque_plaintext ciphertext command_capture owner_record memory_bytes maximum_plaintext_bytes crypto_child_custody synthetic_files_removed remaining_pair_budget_ms original_acceptance tool_check'
    P.exact(value,fields)
    need(len(P.encode(value))<=PUBLIC_MAX and value['schema']=='dg16.protected-host-capability.direct-openssl.v1'
      and value['authority']=='NONE' and value['scope']==SCOPE and value['context_sha256']==P.sha(P.encode(ctx))
      and value['component_seal_sha256']=='7d87b1228e973c303a6c145bc4e014762a7876485a7aefde0e56d3842fbcbe55'
      and value['memory_bytes']==1024**3 and value['maximum_plaintext_bytes']==P.PLAIN_MAX
      and value['status'] in (POSITIVE,'REFUSED_OR_INCOMPLETE')
      and value['crypto_child_custody'] in ('NOT_STARTED','ECHILD','UNPROVED')
      and type(value['synthetic_files_removed']) is bool and value['original_acceptance'] is False,
      'PROTECTED_HOST_CAPABILITY_SCOPE')
    validate_tool_check(value['tool_check'],P)
    need(value['recipient_sha256'] is None or P.digest(value['recipient_sha256']),'PROTECTED_CAPABILITY_RECIPIENT')
    if value['tools'] is not None:
        P.exact(value['tools'],'openssl python3')
        for row in value['tools'].values():P.descriptor(row,32*1024**2)
    for name,maximum in (('opaque_plaintext',P.PLAIN_MAX),('ciphertext',P.CIPHER_MAX),('command_capture',65536),('owner_record',262144)):
        if value[name] is not None:P.descriptor(value[name],maximum)
    need(value['remaining_pair_budget_ms'] is None or P.integer(value['remaining_pair_budget_ms'],0,8400000),'PROTECTED_CAPABILITY_TIME')
    if value['status']==POSITIVE:
        need(value['tool_check']['result']=='PASSED' and value['crypto_child_custody']=='ECHILD' and value['synthetic_files_removed'] is True
          and value['tools'] is not None and value['recipient_sha256'] is not None
          and value['opaque_plaintext'] is not None and value['opaque_plaintext']['bytes']==P.PLAIN_MAX
          and value['ciphertext'] is not None and 0<value['ciphertext']['bytes']<=P.CIPHER_MAX
          and value['command_capture'] is not None and value['owner_record'] is not None
          and value['remaining_pair_budget_ms'] is not None and value['remaining_pair_budget_ms']>=7980000,
          'PROTECTED_CAPABILITY_POSITIVE_JOIN')
    if started:need(value['status']==POSITIVE,'PAIR_WITHOUT_SAME_HOST_CAPABILITY')
    return value

def observe(parent,bridge,state,source,output,u,tools,manifest):
    modules=bridge.load_components(u);P=modules['fs_protocol'];F=modules['fs_io'];C=modules['fs_command'];R=modules['fs_carrier'];E=modules['fs_runner']
    ctx=dict(state['context'],source_commit=P.SOURCE_COMMIT,source_tree=P.SOURCE_TREE,
      workflow_path='.github/workflows/dg16-r5-full-g2.yml',job_name='full-registry-raw-pair');P.context(ctx)
    value=dict(schema='dg16.protected-host-capability.direct-openssl.v1',authority='NONE',status='REFUSED_OR_INCOMPLETE',scope=SCOPE,
      context_sha256=P.sha(P.encode(ctx)),component_seal_sha256=bridge.COMPONENT_SEAL,recipient_sha256=None,tools=None,
      opaque_plaintext=None,ciphertext=None,command_capture=None,owner_record=None,memory_bytes=C.MEMORY_BYTES,
      maximum_plaintext_bytes=P.PLAIN_MAX,crypto_child_custody='NOT_STARTED',synthetic_files_removed=False,
      remaining_pair_budget_ms=None,original_acceptance=False,tool_check=neutral_tool_check())
    state['docs']['PROBE.json']['protected_capability']=value
    command=None;attempted=False;destination=Path(output)/'private/protected-capability';selected_raw=None;deadline=None
    try:
        deadline=GateDeadline(state['started_monotonic'],state['deadline_monotonic'])
        adopted,selected_raw,cert=bridge.selection(u)
        need(adopted['host_gate']=='MAXIMUM_OPAQUE_PLAINTEXT_ENCRYPTION_BEFORE_EITHER_MAINTAINED_LEG','ACTUAL_HOST_GATE_SELECTION_REQUIRED')
        value['recipient_sha256']=adopted['recipient']['sha256']
        observed,pins=observe_tools(u,tools,value['tool_check'],getattr(parent,'Deadline',None))
        value['tools']={n:{k:fact[k] for k in ('bytes','sha256')} for n,fact in observed.items()}
        def current():
            deadline.check()
            need(parent.host_context(output,source,'protected-preflight')==state['context'],'PROTECTED_PREFLIGHT_HOST_CHANGED')
            need(parent.actual_policy_adoption(u)==state['policy_adoption'],'PROTECTED_PREFLIGHT_POLICY_CHANGED')
            need(bridge.selection(u)==(adopted,selected_raw,cert),'PROTECTED_PREFLIGHT_SELECTION_CHANGED')
            deadline.check()
        current();need(not os.path.lexists(destination),'PROTECTED_PREFLIGHT_ONE_SHOT')
        # Any existing protected copy data is charged. A fresh pair has not
        # started, but an unexpected existing tree cannot be treated as empty.
        existing=dict(bytes=0,entries=0)
        for root in (Path(output)/'private/full-pair',Path(output)/'private/protected-recipient'):
            if os.path.lexists(root):
                usage=F.usage(root,deadline.check)
                existing={k:existing[k]+usage[k] for k in existing}
        capacity=P.allocation(existing['bytes'],existing['entries'],P.PLAIN_MAX)
        disk=os.statvfs(destination.parent)
        need(disk.f_bavail*disk.f_frsize>=capacity['total_bytes']-existing['bytes'],'PROTECTED_PREFLIGHT_DISK_CAPACITY')
        with F.create_directory(destination) as directory:
            R.store(directory,'INTENT.json',dict(schema='dg16.protected-host-capability-intent.v1',authority='NONE',context=ctx,
              scope=SCOPE,valid_failed_leg_frame=False,maintained_producer_evidence=False,
              plaintext_recipe='EXACT_PLAIN_MAX_ZERO_BYTES_WRITTEN_IN_AT_MOST_ONE_MIB_CHUNKS',
              capacity=capacity,tools=observed,component_seal_sha256=bridge.COMPONENT_SEAL,
              public_adoption=P.desc(selected_raw),recipient=adopted['recipient'],deadline_monotonic=deadline.stop,
              effective_prework_seconds=420,provisioning_watchdog_seconds=600,maximum_gate_seconds=60,
              cleanup_seconds=3,crypto_memory_bytes=C.MEMORY_BYTES,original_acceptance=False),16384)
            with F.Output(directory,'recipient.pem',8192) as certificate:
                certificate.write(cert);need(certificate.descriptor(deadline.check)==adopted['recipient'],'CAPABILITY_CERTIFICATE')
                with F.Output(directory,'FRAME.bin',P.PLAIN_MAX) as plain,F.Output(directory,'FAILED_STREAMS.cms',P.CIPHER_MAX) as cipher:
                    chunk=b'\0'*P.CHUNK;left=P.PLAIN_MAX;h=hashlib.sha256()
                    while left:
                        deadline.check();piece=chunk[:min(left,P.CHUNK)];plain.write(piece);h.update(piece);left-=len(piece);deadline.check()
                    value['opaque_plaintext']=dict(bytes=P.PLAIN_MAX,sha256=h.hexdigest())
                    need(plain.descriptor(deadline.check)==value['opaque_plaintext'],'CAPABILITY_PLAINTEXT_READBACK')
                    current();executor=E.Executor(source/'scripts/qualify-work-graph-verifier.py',tools['python3'],pins,bridge.COMPONENT_PINS,current)
                    files=dict(plain=plain,certificate=certificate,cipher=cipher)
                    attempted=True;command=executor('encrypt',files,P.CIPHER_MAX,deadline)
                    rc=R.command_record(directory,'encrypt',files,P.CIPHER_MAX,deadline,command)
                    value['crypto_child_custody']=R.child_custody(attempted,command)
                    need(rc==0,'PROTECTED_CAPABILITY_ENCRYPTION_NONZERO');deadline.check()
                    value['ciphertext']=cipher.descriptor(deadline.check)
                    need(0<value['ciphertext']['bytes']<=value['opaque_plaintext']['bytes']+P.CIPHER_OVERHEAD,'CAPABILITY_CIPHER_OVERHEAD')
                    cipher.rewind();C.auth_enveloped(cipher,value['ciphertext']['bytes']);deadline.check()
                    need(plain.descriptor(deadline.check)==value['opaque_plaintext'],'CAPABILITY_PLAINTEXT_CLOSING')
                    value['command_capture']=P.desc(R.small(directory,'COMMAND.json',65536,deadline.check))
                    value['owner_record']=command[0][0]['owner_evidence']
                    current();plain.unlink_owned();cipher.unlink_owned();deadline.check();value['synthetic_files_removed']=True
            # Exact complete source and runtime bookends occur after closure,
            # with no crypto child competing for process statuses.
            need(parent.verify_source(source,manifest,u,state['run_root'] is not None)==state['docs']['SOURCE.json']['before'],
              'PROTECTED_PREFLIGHT_SOURCE_CLOSING')
            need(parent.runtime_snapshot(source,state,u)==state['runtime'],'PROTECTED_PREFLIGHT_RUNTIME_CLOSING')
            current();usage=F.usage(destination,deadline.check)
            need(usage['bytes']+16384<=P.AUX_BYTES and usage['entries']+1<=32,'CAPABILITY_COMPACT_RETENTION_BOUND')
            value['remaining_pair_budget_ms']=int((state['deadline_monotonic']-time.monotonic())*1000)
            value['status']=POSITIVE;validate_public(value,ctx,P,started=True);deadline.check()
            R.store(directory,'STATE.json',dict(schema='dg16.protected-host-capability-private.v1',authority='NONE',context=ctx,
              public=value,tools=observed,tool_pins=pins,selection=P.desc(selected_raw),
              source_before=state['docs']['SOURCE.json']['before'],runtime=state['runtime'],
              compact_usage_before_record=usage,original_acceptance=False),16384)
            state['protected_host_tool_pins']=pins;state['protected_host_capability_path']=str(destination)
        deadline.check();return value
    except BaseException:
        value['status']='REFUSED_OR_INCOMPLETE';value['crypto_child_custody']=R.child_custody(attempted,command)
        if value['crypto_child_custody']=='UNPROVED':state['docs']['CLEANUP.json']['all_step_children_reaped']=False
        if destination.is_dir() and not (destination/'STATE.json').exists():
            try:
                with F.Directory(destination) as directory:R.store(directory,'STATE.json',dict(schema='dg16.protected-host-capability-private.v1',
                  authority='NONE',context=ctx,public=value,original_acceptance=False),16384)
            except BaseException:pass
        validate_public(value,ctx,P)
        raise ValueError('PROTECTED_HOST_CAPABILITY_NOT_COMPLETE') from None
