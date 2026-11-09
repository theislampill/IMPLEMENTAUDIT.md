"""Separate admitted private decrypt process; no public-receiver import.

Import and authorize are inert. Only main's actual root admission can enter
the pinned nearest-owner crypto executor. Plaintext is never printed.
"""
from pathlib import Path
import hashlib,json,os,signal,sys,time
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import root_common as K
import root_acquire as A

ROOT_BINDING_SHA=None
ROOT_SESSION=None
HELPER_PINS={'root_common.py': {'bytes': 8494, 'sha256': 'f4e2f07b78d4f9acd13f75882ee5faea411a904485a5fbb1c103b49c063615b8'}, 'root_acquire.py': {'bytes': 20704, 'sha256': 'c4eca6f66708215aac994faa9fef1e253466f8898f17a4a612b4e0ec0d1d5c23'}}
PRIVATE_SECONDS=180
need=K.need

def authorize(grant,expected_sha256,raw=None):
    need(K.digest(expected_sha256) and type(raw) is bytes and K.sha(raw)==expected_sha256,'ACTUAL_PRIVATE_ADMISSION_REQUIRED')
    fields='schema actor session disposition context root_binding_sha256 program source_owner tool_pins request cipher_session recipient_certificate recipient_private_key shared_root operation_directory issued_unix_ms expires_unix_ms maximum_seconds component_seal_sha256 effect_grant automatic_retry original_awards'
    need(type(grant) is dict and set(grant)==set(fields.split()),'PRIVATE_ADMISSION_FIELDS')
    K.context(grant['context'])
    need(grant['schema']=='dg16.protected-stream-private-decrypt-admission.v1' and grant['actor']=='/root'
      and type(ROOT_SESSION) is str and grant['session']==ROOT_SESSION and grant['disposition']=='EXECUTE_ONCE_PRIVATE_RECEIVING'
      and grant['root_binding_sha256']==ROOT_BINDING_SHA and K.digest(ROOT_BINDING_SHA)
      and grant['component_seal_sha256']==K.COMPONENT_SEAL and grant['effect_grant'] is True
      and grant['automatic_retry'] is False and grant['original_awards']==[] and grant['maximum_seconds']==PRIVATE_SECONDS,
      'PRIVATE_ADMISSION_SCOPE')
    need(K.integer(grant['issued_unix_ms']) and K.integer(grant['expires_unix_ms'])
      and 0<grant['expires_unix_ms']-grant['issued_unix_ms']<=900000,'PRIVATE_ADMISSION_WINDOW')
    for name in ('program','source_owner','request','recipient_certificate','recipient_private_key'):
        value=grant[name];need(type(value) is dict and set(value)=={'path','bytes','sha256'}
          and type(value['path']) is str and Path(value['path']).is_absolute(),'PRIVATE_ADMISSION_FILE')
        K.descriptor({k:value[k] for k in ('bytes','sha256')},1024**2)
    need(grant['program']['path']==str(HERE/'private_receive.py')
      and grant['source_owner']['sha256']=='79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b',
      'EXACT_PRIVATE_PROGRAM_AND_OWNER')
    pins=grant['tool_pins'];need(type(pins) is dict and len(pins)==3 and '/usr/bin/env' in pins and '/usr/bin/openssl' in pins,
      'PRIVATE_TOOL_POPULATION')
    python=[p for p in pins if p not in ('/usr/bin/env','/usr/bin/openssl')]
    need(len(python)==1 and Path(python[0]).is_absolute(),'PRIVATE_PYTHON_TOOL')
    for pin in pins.values():K.descriptor(pin,32*1024**2)
    need(pins==K.QUALIFIED_PRIVATE_TOOL_PINS,'PRIVATE_TOOL_PROFILE_NOT_ACTUALLY_QUALIFIED')
    for name in ('shared_root','operation_directory','cipher_session'):
        need(type(grant[name]) is str and Path(grant[name]).is_absolute(),'PRIVATE_ROOT_PATH')
    shared=Path(grant['shared_root']);operation=Path(grant['operation_directory']);session=Path(grant['cipher_session'])
    need(operation==shared/'private-diagnostic' and session.is_relative_to(shared) and session!=shared
      and not session.is_relative_to(operation) and Path(grant['request']['path']).is_relative_to(shared),
      'PRIVATE_SHARED_CUSTODY_ROOT')
    return grant

def request_data(raw,binding,context):
    value=K.parse(raw,65536)
    need(type(value) is dict and set(value)==set('schema authority context public_receiver_binding_sha256 public_archive public_receiving terminal_log_join failure_projection protected_receipt protected_capability private_key_or_body_present original_acceptance'.split()),
      'PRIVATE_REQUEST_FIELDS')
    need(value['schema']=='dg16.protected-full-private-diagnostic-request.v1' and value['authority']=='NONE'
      and value['context']==context and value['public_receiver_binding_sha256']==binding['public_receiver_binding']['sha256']
      and value['terminal_log_join'].get('all_seven_exact') is True
      and value['private_key_or_body_present'] is False and value['original_acceptance'] is False,
      'ACTUAL_PUBLIC_RECEIVING_JOIN')
    K.descriptor(value['public_archive'],400000);K.descriptor(value['public_receiving'],65536)
    receipt=value['protected_receipt']
    need(type(receipt) is dict and receipt.get('status')=='ENCRYPTED_LOCAL_NOT_PROVIDER_RECEIVED'
      and receipt.get('recipient_sha256')==binding['recipient']['sha256'],'PUBLIC_ENCRYPTED_DIAGNOSTIC_REQUIRED')
    return value

def write_record(directory,name,value):
    need(name in ('ROOT_INTENT.json','ROOT_RECEIVING.json'),'PRIVATE_ROOT_RECORD_NAME');raw=K.encode(value)
    need(0<len(raw)<=65536,'PRIVATE_ROOT_RECORD_BOUND')
    with os.fdopen(os.open(Path(directory)/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600),'wb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    A.Session.sync(directory);need(K.read(Path(directory)/name,65536,True)==raw,'PRIVATE_ROOT_RECORD_READBACK')
    return K.desc(raw)

def execute_admitted(grant,grant_path,grant_raw,binding,modules,*,clock=time.monotonic):
    """Actual-only path. No caller callback may select a different executor."""
    P=modules['fs_protocol'];F=modules['fs_io'];R=modules['fs_carrier'];H=modules['full_g2_hooks'];E=modules['fs_runner']
    context=grant['context'];root=Path(grant['operation_directory']);shared=Path(grant['shared_root'])
    need(not os.path.lexists(root),'NO_PRIVATE_RECEIVE_REPLAY')
    started=clock();stop=min(started+PRIVATE_SECONDS,started+(grant['expires_unix_ms']-time.time_ns()//1000000)/1000)
    def current():
        need(clock()<stop and grant['issued_unix_ms']<=time.time_ns()//1000000<grant['expires_unix_ms'],'PRIVATE_RECEIVE_DEADLINE')
        need(K.binding(HERE,ROOT_BINDING_SHA)[0]==binding,'PRIVATE_ROOT_BINDING_CHANGED')
        need(K.read(grant_path,65536,True)==grant_raw,'PRIVATE_ADMISSION_CHANGED')
        for name,pin in HELPER_PINS.items():need(K.desc(K.read(HERE/name,65536))==pin,'PRIVATE_HELPER_CHANGED')
        need(K.desc(K.read(HERE/'private_receive.py',65536))=={k:grant['program'][k] for k in ('bytes','sha256')},'PRIVATE_PROGRAM_CHANGED')
        need(clock()<stop,'PRIVATE_RECEIVE_DEADLINE')
    current()
    req=grant['request'];request_raw=K.read(Path(req['path']),65536,True)
    need(K.desc(request_raw)=={k:req[k] for k in ('bytes','sha256')},'EXACT_PUBLIC_REQUEST')
    request=request_data(request_raw,binding,context);projection=request['failure_projection']
    P.validate_failed(projection);H.validate_public_receipt(request['protected_receipt'],context)
    session=A.Session(Path(grant['cipher_session']),binding,components=modules)
    need(session.role=='cipher' and session.context==context,'PRIVATE_CIPHER_SESSION_SCOPE')
    provider_receipt=session.receive(save=False);provider=provider_receipt['provider']
    retained=K.parse(K.read(session.path/'PROVIDER_RECEIVING.json',65536,True))
    # Time is an observation field; all actual bodies and semantic joins agree.
    need({k:v for k,v in retained.items() if k!='observed_unix_ms'}==
      {k:v for k,v in provider_receipt.items() if k!='observed_unix_ms'},'ACTUAL_PROVIDER_RECEIPT_CHANGED')
    cert=grant['recipient_certificate'];key=grant['recipient_private_key'];recipient=binding['recipient']
    need({k:cert[k] for k in ('bytes','sha256')}==recipient,'PRIVATE_RECIPIENT_PIN')
    # Private key body access occurs only after the actual grant, public and
    # provider joins. No key or plaintext bytes enter a public record.
    for row in (cert,key):
        with F.Directory(Path(row['path']).parent) as d,F.Input(d,Path(row['path']).name,8192,
          {k:row[k] for k in ('bytes','sha256')},private=True) as held:held.descriptor(current)
    owner=grant['source_owner'];need(K.desc(K.read(Path(owner['path']),1024**2))=={k:owner[k] for k in ('bytes','sha256')},'PRIVATE_OWNER_SOURCE')
    expected=P.make_manifest(context,projection,recipient);plain=P.plain_size(len(P.encode(expected)),expected['streams'])
    usage=F.usage(shared,current);future=P.CIPHER_MAX+P.ENVELOPE_MAX+plain+sum(x['bytes'] for x in expected['streams'].values())+P.AUX_BYTES+16384
    need(usage['bytes']+future<=P.TOTAL_MAX and usage['entries']+64<=P.ENTRY_MAX,'PRIVATE_SHARED_ALLOCATION_REFUSED')
    with F.create_directory(root):pass
    write_record(root,'ROOT_INTENT.json',dict(schema='dg16.protected-private-root-intent.v1',authority='NONE',context=context,
      actual_admission=K.desc(grant_raw),public_request=K.desc(request_raw),actual_provider_receipt=K.desc(K.encode(retained)),
      shared_usage=usage,future_reserved_bytes=future,total_limit=P.TOTAL_MAX,deadline_monotonic=stop,
      child_max_seconds=60,child_cleanup_seconds=3,private_plaintext_publication=False,automatic_retry=False,original_awards=[]))
    outcome=None;entered=False
    try:
        current();staged=root/'ciphertext';target=root/'authenticated'
        acquired=R.acquire_artifact(session.path/'ARTIFACT.zip',provider,context,provider['artifact_id'],provider['archive'],staged,current)
        need(acquired['members']=={'FAILURE_ENVELOPE.json':request['protected_receipt']['envelope'],
          'FAILED_STREAMS.cms':request['protected_receipt']['ciphertext']},'PUBLIC_PRIVATE_CIPHERTEXT_JOIN')
        current();deadline=P.Deadline(stop,stop,clock=clock)
        python=next(p for p in grant['tool_pins'] if p not in ('/usr/bin/env','/usr/bin/openssl'))
        executor=E.Executor(Path(owner['path']),python,grant['tool_pins'],binding['component_members'],current)
        entered=True
        outcome=R.receive_private(staged,target,context,projection,Path(cert['path']),Path(key['path']),recipient,executor,deadline,provider)
        current();closing=F.usage(shared,current);need(closing['bytes']<=P.TOTAL_MAX,'PRIVATE_CLOSING_ALLOCATION')
    except BaseException:
        if outcome is None:
            outcome=R.neutral('INCOMPLETE' if entered else 'REFUSED','SUPPLEMENTARY_RETENTION_REFUSED')
            outcome['crypto_child_custody']='UNPROVED' if entered else 'NOT_STARTED'
        else:
            outcome=dict(outcome,status='INCOMPLETE',reason='SUPPLEMENTARY_RETENTION_REFUSED')
    complete=(outcome.get('status')=='AUTHENTICATED_DIAGNOSTIC_STREAMS_RECEIVED' and outcome.get('crypto_child_custody')=='ECHILD')
    value=dict(schema='dg16.protected-private-root-receiving.v1',authority='NONE',context=context,
      actual_admission=K.desc(grant_raw),public_request=K.desc(request_raw),provider_receipt=K.desc(K.encode(retained)),
      supplementary=outcome,complete_private_unknown_streams_available=complete,
      plaintext_scope='PRIVATE_ONLY_DIAGNOSTIC_COPY_NOT_LIVE_ACCEPTANCE_CUSTODY',
      primary_result_replaced=False,automatic_retry=False,original_awards=[])
    write_record(root,'ROOT_RECEIVING.json',value)
    return dict(status=outcome['status'],crypto_child_custody=outcome.get('crypto_child_custody'),
      complete_private_unknown_streams_available=complete,result=K.desc(K.encode(value)),
      authority='NONE',original_awards=[],primary_result_replaced=False)

def main():
    need(len(sys.argv)==3 and sys.flags.isolated and sys.dont_write_bytecode,'FIXED_PRIVATE_ENTRY')
    need(set(HELPER_PINS)=={'root_common.py','root_acquire.py'} and
      all(K.desc(K.read(HERE/n,65536))==pin for n,pin in HELPER_PINS.items()),'PRIVATE_HELPER_PINS')
    grant_path=Path(sys.argv[1]).absolute();raw=K.read(grant_path,65536,True);grant=authorize(K.parse(raw,65536),sys.argv[2],raw)
    b,_=K.binding(HERE,ROOT_BINDING_SHA);modules=K.components(HERE,b)
    need(signal.getitimer(signal.ITIMER_REAL)==(0.0,0.0),'PRIVATE_DEDICATED_WATCHDOG')
    old=signal.getsignal(signal.SIGALRM)
    def expired(*_):raise TimeoutError('PRIVATE_OPERATION_DEADLINE')
    signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,PRIVATE_SECONDS)
    try:result=execute_admitted(grant,grant_path,raw,b,modules)
    finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old)
    print(json.dumps(result,sort_keys=True),flush=True);return 0 if result['complete_private_unknown_streams_available'] else 1

if __name__=='__main__':
    try:code=main()
    except BaseException:
        print('{"status":"REFUSED_OR_INCOMPLETE","private_body_printed":false,"automatic_retry":false,"authority":"NONE"}',flush=True);code=1
    raise SystemExit(code)
