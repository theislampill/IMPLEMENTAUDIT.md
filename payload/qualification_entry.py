"""Prospective one-shot maximum encrypt/capture qualification; no production leg.

No operation is admitted by these bytes. A separately approved Root dispatch
must bind ADMISSION_JSON to this source manifest before this entry can proceed.
The original production preflight remains unbound and its same-host gate is not
discharged by a qualification on another job. No private-key API is imported.
"""
import hashlib,json,os,re,signal,stat,sys,time,types
from pathlib import Path

HERE=Path(__file__).resolve().parent
SEAL='9401f5b38a105b459301105b1f9dccb4badb908f5f92c30a35f7a551a5ef0786'
CERT={'bytes':1464,'sha256':'5adbbeaf63e38116dcba9eb58af76b0fa056808649f9aa144e3f14dee838f4b8'}
OWNER='79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b'
ORDER=('fs_protocol','fs_io','fs_command','fs_carrier','full_g2_hooks','fs_runner','fs_transport')
class Refusal(ValueError):pass
class Deadline(Exception):pass
def need(ok,code):
    if not ok:raise Refusal(code)
def enc(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('ascii')
def sha(b):return hashlib.sha256(b).hexdigest()
def stamp(s):return dict(zip('dev ino mode nlink size mtime_ns ctime_ns uid gid'.split(),
    (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid)))
def read(path,maximum,expected=None):
    path=Path(path).absolute();need(path.resolve(strict=True)==path,'PHYSICAL_PATH')
    before=path.lstat();need(stat.S_ISREG(before.st_mode) and before.st_nlink==1
        and not before.st_mode&0o022 and 0<=before.st_size<=maximum,'PHYSICAL_FILE')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(stamp(os.fstat(fd))==stamp(before),'OPEN_CHANGED')
        with os.fdopen(fd,'rb',closefd=False) as f:body=f.read(maximum+1)
        need(len(body)==before.st_size and stamp(os.fstat(fd))==stamp(before)
            and stamp(path.lstat())==stamp(before),'READ_CHANGED')
        if expected is not None:need(expected=={'bytes':len(body),'sha256':sha(body)},'INPUT_PIN')
        return body
    finally:os.close(fd)
def module(name,body,path):
    m=types.ModuleType(name);m.__file__=str(path);exec(compile(body,str(path),'exec'),m.__dict__);return m
def load_components(root,members,read_file):
    mods={}
    for name in ORDER:
        body=read_file(root/'components'/(name+'.py'),1024**2,members['components/'+name+'.py'])
        m=types.ModuleType(name);m.__file__=str(root/'components'/(name+'.py'));sys.modules[name]=m
        exec(compile(body,m.__file__,'exec'),m.__dict__);mods[name]=m
    return mods
def context():
    c=dict(repository=os.environ.get('GITHUB_REPOSITORY'),ref=os.environ.get('GITHUB_REF'),
        run_id=os.environ.get('GITHUB_RUN_ID'),attempt=os.environ.get('GITHUB_RUN_ATTEMPT'),head=os.environ.get('GITHUB_SHA'))
    need(c['repository']=='theislampill/IMPLEMENTAUDIT.md' and os.environ.get('GITHUB_EVENT_NAME')=='workflow_dispatch'
        and os.environ.get('RUNNER_ENVIRONMENT')=='github-hosted' and c['attempt']=='1'
        and type(c['ref']) is str and c['ref'].startswith('refs/heads/pro/dg16-direct-encrypt-qualification-')
        and '..' not in c['ref'] and re.fullmatch('[1-9][0-9]{0,19}',c['run_id'] or '')
        and re.fullmatch('[0-9a-f]{40}',c['head'] or '') and c['head']!='0'*40,'DISPATCH_CONTEXT')
    return dict(c,attempt=1)
def admission(raw,c,manifest_hash):
    need(type(raw) is str and len(raw.encode())<=8192,'ADMISSION_BOUND')
    def pairs(items):
        out={}
        for k,v in items:need(k not in out,'ADMISSION_DUPLICATE');out[k]=v
        return out
    a=json.loads(raw,object_pairs_hook=pairs)
    need(type(a) is dict and set(a)=={'schema','purpose','source_manifest','expected_ref','expected_head',
        'owner_approval_sha256','effect_grant','maximum_plaintext','maximum_ciphertext','maximum_gate_seconds',
        'maximum_commands','private_key_on_host','maintained_verifiers'},'ADMISSION_FIELDS')
    need(a['schema']=='dg16.direct-encrypt-qualification-admission.v1'
        and a['purpose']=='ONE_MAXIMUM_ENCRYPT_CAPTURE_ONLY' and a['source_manifest']==manifest_hash
        and a['expected_ref']==c['ref'] and a['expected_head']==c['head']
        and type(a['owner_approval_sha256']) is str and re.fullmatch('[0-9a-f]{64}',a['owner_approval_sha256'])
        and a['owner_approval_sha256']!='0'*64 and a['effect_grant'] is True
        and type(a['maximum_plaintext']) is int and a['maximum_plaintext']==268501016
        and type(a['maximum_ciphertext']) is int and a['maximum_ciphertext']==268517400
        and type(a['maximum_gate_seconds']) is int and a['maximum_gate_seconds']==60
        and type(a['maximum_commands']) is int and a['maximum_commands']==1
        and a['private_key_on_host'] is False and a['maintained_verifiers']==[], 'EXACT_OWNER_ADMISSION_REQUIRED')
    # Matching data is never authentication of the owner approval. The publisher
    # and independent actual receiver must bind the real grant and provider run.
    return a

def main():
    result={'schema':'dg16.direct-qualification-result.v1','status':'NOT_ADMITTED','stage':'ADMISSION',
        'original_acceptance':False,'authenticated_private_receiving':False,'production_gate_received':False}
    raw_admission=os.environ.get('ADMISSION_JSON','')
    if not raw_admission:return 5
    c=context();manifest_raw=read(HERE/'SOURCE_MANIFEST.json',65536);manifest=json.loads(manifest_raw)
    admission(raw_admission,c,sha(manifest_raw));result['context']=c
    need(manifest['component_seal']==SEAL and manifest['native_qualification'] is False
        and manifest['effect_grant'] is False,'SOURCE_SCOPE')
    members=manifest['members'];host_anchor=None
    def current():
        need(context()==c and os.environ.get('ADMISSION_JSON')==raw_admission,'CONTEXT_CHANGED')
        need(read(HERE/'SOURCE_MANIFEST.json',65536)==manifest_raw,'MANIFEST_CHANGED')
        for name,pin in members.items():
            need(not Path(name).is_absolute() and '..' not in Path(name).parts,'SOURCE_MEMBER_PATH')
            read(HERE/name,1024**2,pin)
        if host_anchor is not None:
            need(sha(utility.checked_file(Path('/proc/sys/kernel/random/boot_id'),128))==host_anchor['boot']
                and sha(enc(profile.credentials()))==host_anchor['credentials'],'ACTUAL_HOST_IDENTITY_CHANGED')
    started=time.monotonic();stop=started+60
    class Gate:
        def __init__(self):self.stop=stop
        def check(self):need(time.monotonic()<stop,'QUALIFICATION_DEADLINE')
    gate=Gate();directory=None;executor=None;attempted=False
    facts=command=owner=stdout=None
    old_handlers={n:signal.getsignal(n) for n in (signal.SIGALRM,signal.SIGTERM)}
    def interrupted(*_):raise Deadline()
    signal.signal(signal.SIGALRM,interrupted);signal.signal(signal.SIGTERM,interrupted);signal.alarm(70)
    previous={name:sys.modules.get(name) for name in ORDER};mods={}
    try:
        current();gate.check()
        receiver=module('qualification_receiver',read(HERE/'capture_receiver.py',65536,members['capture_receiver.py']),HERE/'capture_receiver.py')
        host_api=module('qualification_host_api',read(HERE/'host_api.py',65536,members['host_api.py']),HERE/'host_api.py')
        utility=host_api.utility_api();profile=host_api.profile_api(host_api.evidence_api());inventory=host_api.inventory_api(profile)
        result['stage']='PROFILE';tools,host=inventory.inventory(utility)
        matches=profile.compare_historical(host,host_api.HISTORICAL_PROFILE);need(set(matches)==set(receiver.PROFILE) and all(matches.values()),'HOST_PROFILE_DIFFERS')
        host_anchor={'boot':host['boot_identity_sha256'],'credentials':sha(enc(host['credentials']))}
        mods=load_components(HERE,members,read)
        P,F,C,R,E=(mods[n] for n in ('fs_protocol','fs_io','fs_command','fs_carrier','fs_runner'))
        component_manifest=json.loads(read(HERE/'components/CODE_MANIFEST.json',65536,members['components/CODE_MANIFEST.json']))
        seal_raw=read(HERE/'components/HOST_COMPONENT_SEAL.json',65536,members['components/HOST_COMPONENT_SEAL.json'])
        need(sha(seal_raw)==SEAL and component_manifest['members']==json.loads(seal_raw)['members'],'COMPONENT_JOIN')
        observer=module('qualification_tool_observer',read(HERE/'components/protected_preflight.py',32768,members['components/protected_preflight.py']),HERE/'components/protected_preflight.py')
        result['stage']='TOOLS';tool_check=observer.neutral_tool_check();result['tool_check']=tool_check
        observed,pins=observer.observe_tools(utility,tools,tool_check,Deadline);observer.validate_tool_check(tool_check,P)
        opening={path:stamp(Path(path).lstat()) for path in pins}
        certificate=read(HERE/'recipient.pem',8192,CERT)
        read(HERE/'ordinary_owner.py',1024**2,{'bytes':members['ordinary_owner.py']['bytes'],'sha256':OWNER})
        output=HERE/'qualification-output';need(not os.path.lexists(output),'NO_RETRY_OUTPUT_EXISTS')
        gate.check();result['stage']='CAPACITY'
        disk=os.statvfs(HERE);capacity=P.allocation(0,0,P.PLAIN_MAX)
        need(disk.f_bavail*disk.f_frsize>=capacity['total_bytes'],'DISK_CAPACITY')
        with F.create_directory(output) as directory:
            with F.Output(directory,'recipient.pem',8192) as cert,F.Output(directory,'FRAME.bin',P.PLAIN_MAX) as plain,F.Output(directory,'FAILED_STREAMS.cms',P.CIPHER_MAX) as cipher:
                removed={'FRAME.bin':False,'FAILED_STREAMS.cms':False,'recipient.pem':False}
                try:
                    cert.write(certificate);need(cert.descriptor(gate.check)==CERT,'RECIPIENT_CLOSING')
                    left=P.PLAIN_MAX;chunk=b'\0'*P.CHUNK
                    while left:
                        gate.check();part=chunk[:min(left,P.CHUNK)];plain.write(part);left-=len(part)
                    plain_before=plain.descriptor(gate.check)
                    executor=E.Executor(HERE/'ordinary_owner.py',tools['python3'],pins,component_manifest['members'],current,witness_key_generation=False)
                    result['stage']='ENCRYPT';attempted=True
                    actual=executor('encrypt',{'plain':plain,'certificate':cert,'cipher':cipher},P.CIPHER_MAX,gate)
                    need(R.command_record(directory,'encrypt',{'plain':plain,'certificate':cert,'cipher':cipher},P.CIPHER_MAX,gate,actual)==0,'ENCRYPT_NONZERO')
                    command=P.parse(R.small(directory,'COMMAND.json',65536,gate.check),65536)
                    owner=P.parse(R.small(directory,'CAPTURE_OWNER.json',262144,gate.check),262144)
                    stdout,stderr=actual[2],actual[3];receiver.limits_from_stdout(stdout)
                    cipher_desc=cipher.descriptor(gate.check);cipher.rewind();C.auth_enveloped(cipher,cipher_desc['bytes'])
                    plain_after=plain.descriptor(gate.check);current();gate.check()
                    closing={path:stamp(Path(path).lstat()) for path in pins}
                    facts=dict(schema='dg16.direct-encrypt-capture-qualification.v1',scope='MAXIMUM_ENCRYPT_CAPTURE_ONLY_NOT_A_PRODUCTION_GATE',
                        context=c,component_seal=SEAL,source_manifest=sha(manifest_raw),recipient=CERT,profile_matches=matches,
                        host_bookends={'boot_opening':host_anchor['boot'],'boot_closing':None,
                            'credentials_opening':host_anchor['credentials'],'credentials_closing':None},
                        tool_pins=pins,tool_bookends={p:{'opening':opening[p],'closing':closing[p]} for p in pins},
                        plain_before=plain_before,plain_after=plain_after,cipher=cipher_desc,cipher_type_checked=True,
                        files_removed=removed,currentness_bookends=True,gate_clock={'started':started,'stop':stop,'ending':None},
                        authenticated_private_receiving=False,original_acceptance=False)
                finally:
                    # Only held fresh outputs may be removed. Failure is retained;
                    # cleanup never retries a command or clears an old resource.
                    for name,f in [('FAILED_STREAMS.cms',cipher),('FRAME.bin',plain),('recipient.pem',cert)]:
                        if f.fd is not None:
                            try:f.unlink_owned();removed[name]=True
                            except (OSError,P.Refusal):result['cleanup_unknown']=True
            current();gate.check()
            if facts is not None:
                facts['gate_clock']['ending']=time.monotonic()
                _,final_host=inventory.inventory(utility)
                need(profile.compare_historical(final_host,host_api.HISTORICAL_PROFILE)==matches,'CLOSING_PROFILE_CHANGED')
                facts['host_bookends'].update(boot_closing=final_host['boot_identity_sha256'],
                    credentials_closing=sha(enc(final_host['credentials'])))
                current();gate.check();facts['gate_clock']['ending']=time.monotonic()
                received=receiver.receive(facts,command,owner,stdout,stderr);gate.check()
                result.update(status='OBSERVED_ENCRYPT_CAPTURE_REQUIRES_INDEPENDENT_RECEIVING',stage='COMPLETE',
                    facts=facts,command=command,owner=owner,stdout_limits_hex=stdout.hex(),stderr_descriptor=P.desc(stderr),receiving=received)
    except Deadline:result.update(status='INTERRUPTED_OR_DEADLINE',stage=result['stage'])
    except BaseException:result.update(status='REFUSED_OR_EXCEPTION',stage=result['stage'])
    finally:
        signal.alarm(0)
        for n,h in old_handlers.items():signal.signal(n,h)
        for name,old in previous.items():
            if old is None:sys.modules.pop(name,None)
            else:sys.modules[name]=old
        result['command_attempted']=attempted;result['elapsed_seconds']=time.monotonic()-started
        if result['elapsed_seconds']>60 and result['status']=='OBSERVED_ENCRYPT_CAPTURE_REQUIRES_INDEPENDENT_RECEIVING':
            result.update(status='REFUSED_OR_EXCEPTION',stage='FINAL_DEADLINE')
        if executor is not None and executor.last is not None:
            r=executor.last['record'];o=executor.last['owner']
            result['last_capture']={k:r[k] for k in ('process_started','pidfd_acquired','returncode','cleanup','internal_failure')}
            result['last_capture']['owner_descriptor']={'bytes':len(enc(o)),'sha256':sha(enc(o))}
        # Compact, closed evidence only. Actual stdout is retained publicly only
        # after the strict one-line limits parser accepted it; no stderr/cipher.
        body=enc(result)
        if len(body)>65536:
            result=dict(schema='dg16.direct-qualification-result.v1',status='PUBLIC_RECEIPT_BOUND_REFUSED',
                context=c,stage='PUBLIC_RECEIPT',original_acceptance=False,authenticated_private_receiving=False,
                production_gate_received=False,command_attempted=attempted,
                retained_result_descriptor={'bytes':len(body),'sha256':sha(body)})
            body=enc(result)
        need(len(body)<=65536,'COMPACT_RESULT_BOUND')
        target=HERE/'QUALIFICATION_RESULT.json'
        with target.open('xb') as f:f.write(body);f.flush();os.fsync(f.fileno())
    return 0 if result['status']=='OBSERVED_ENCRYPT_CAPTURE_REQUIRES_INDEPENDENT_RECEIVING' else 2

if __name__=='__main__':sys.exit(main())
