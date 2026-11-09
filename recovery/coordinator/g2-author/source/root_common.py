"""Shared bounded data/held-file helpers. No process, provider or crypto effect."""
from pathlib import Path
import hashlib,json,os,re,stat,sys,types

SOURCE_COMMIT='7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'
SOURCE_TREE='6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e'
BRANCH='pro/dg16-r5-full-g2-current-03-20261107'
COMPONENT_SEAL='e99a60d5790355ae39c0e4bbc4567add87e702775ade8f5655e2f3ef56bd9602'
COMPONENT_INDEX='9d54e10f1c6d056d43801b8457f909030498704a766b17998abbc9c4525c28f3'
ROOT_SESSION=None
# Exact Pro tool identities of the independently/root received R1 maximum.
# This is not a claim about a different hosted build. The host's independent
# maximum-encryption gate has its own current observed tool identities.
QUALIFIED_PRIVATE_TOOL_PINS={
 '/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12':
   {'bytes':30894944,'sha256':'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7'},
 '/usr/bin/env':{'bytes':56144,'sha256':'eb1c64bbc9908afcdf8cb48524f17112d8dd76a249f80dee2f01da14747b3b6e'},
 '/usr/bin/openssl':{'bytes':1103304,'sha256':'acc10176d038aeb7b2a77d9ec972ac2985857a7191f7aecb7c54ef0e2c7e9549'}}
CHUNK=1024**2
ROLE_CAPS={'live':400000,'terminal':400000,'cipher':269574168}
METADATA_MAX=4*1024**2
JOURNAL_MAX=32*1024**2
BODY_TOTAL_MAX=2*1024**3
AUTH='ACTUAL_ROOT_TOOL_HISTORY_AND_INDEPENDENT_RECEIVING_REQUIRED'

class Refusal(ValueError):pass
def need(ok,code):
    if not ok:raise Refusal(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def desc(raw):return dict(bytes=len(raw),sha256=sha(raw))
def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
def parse(raw,maximum=METADATA_MAX):
    need(type(raw) is bytes and 0<len(raw)<=maximum,'JSON_BOUND')
    def pairs(items):
        out={}
        for k,v in items:need(k not in out,'DUPLICATE_JSON_KEY');out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Refusal('NONFINITE_JSON')))
def integer(v,lo=0,hi=2**63-1):return type(v) is int and lo<=v<=hi
def digest(v):return type(v) is str and re.fullmatch('[0-9a-f]{64}',v) is not None
def descriptor(v,maximum):
    need(type(v) is dict and set(v)=={'bytes','sha256'} and integer(v['bytes'],0,maximum) and digest(v['sha256']),'DESCRIPTOR')
    return v
def context(v):
    need(type(v) is dict and set(v)==set('repository branch run_id run_attempt workflow_commit source_commit source_tree workflow_path job_name'.split()),'CONTEXT_FIELDS')
    fixed=dict(repository='theislampill/IMPLEMENTAUDIT.md',branch=BRANCH,run_attempt=1,source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,
      workflow_path='.github/workflows/dg16-r5-full-g2.yml',job_name='full-registry-raw-pair')
    need(all(type(v[k]) is type(x) and v[k]==x for k,x in fixed.items()) and type(v['run_id']) is str
      and re.fullmatch('[1-9][0-9]{0,19}',v['run_id']) and type(v['workflow_commit']) is str
      and re.fullmatch('[0-9a-f]{40}',v['workflow_commit']) and v['workflow_commit']!='0'*40,'CONTEXT_SCOPE')
    return v
def identity(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid)
def stamp(s):return (*identity(s),s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def read(path,maximum=METADATA_MAX,private=False):
    p=Path(path).absolute();need(p.resolve(strict=True)==p,'PHYSICAL_INPUT_PATH');before=p.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=maximum,'INPUT_FILE_BOUND')
    if private:need(before.st_uid==os.geteuid() and stat.S_IMODE(before.st_mode) in (0o400,0o600),'PRIVATE_INPUT_CUSTODY')
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(stamp(os.fstat(fd))==stamp(before),'INPUT_OPEN_CHANGED');parts=[];size=0
        while size<before.st_size:
            raw=os.read(fd,min(CHUNK,before.st_size-size));need(bool(raw),'INPUT_SHORT_READ');parts.append(raw);size+=len(raw)
        need(os.read(fd,1)==b'' and stamp(os.fstat(fd))==stamp(before)==stamp(p.lstat()),'INPUT_CHANGED')
        return b''.join(parts)
    finally:os.close(fd)

def binding(here,expected):
    need(digest(expected),'FINAL_ROOT_BINDING_REQUIRED')
    raw=read(Path(here)/'ROOT_BINDING.json',65536);need(sha(raw)==expected,'ROOT_BINDING_CHANGED');value=parse(raw,65536)
    need(value.get('schema')=='dg16.protected-full-root-receiver-binding.v1' and value.get('source_commit')==SOURCE_COMMIT
      and value.get('source_tree')==SOURCE_TREE and value.get('branch')==BRANCH
      and value.get('repository')=='theislampill/IMPLEMENTAUDIT.md'
      and type(ROOT_SESSION) is str and value.get('session')==ROOT_SESSION
      and value.get('component_seal_sha256')==COMPONENT_SEAL and value.get('component_index_sha256')==COMPONENT_INDEX
      and value.get('actual_component_review_received') is True and value.get('actual_maximum_qualification_received') is True
      and value.get('effect_grant') is False and value.get('original_awards')==[], 'ROOT_BINDING_SCOPE')
    need(type(value.get('final_tree')) is str and re.fullmatch('[0-9a-f]{40}',value['final_tree']),'FINAL_TREE_REQUIRED')
    descriptor(value['recipient'],8192);descriptor(value['public_receiver_binding'],65536)
    descriptor(value['public_recipient_adoption'],16384);need(digest(value['workflow_sha256']),'WORKFLOW_BINDING')
    descriptor(value['successor_runtime_binding'],16384)
    runtime_raw=read(Path(here)/'SUCCESSOR_RUNTIME_BINDING.json',16384)
    need(desc(runtime_raw)==value['successor_runtime_binding'],'SUCCESSOR_RUNTIME_BINDING_CHANGED')
    runtime=parse(runtime_raw,16384)
    need(runtime.get('session')==ROOT_SESSION and runtime.get('effect_grant') is False
      and runtime.get('local_native_currentness') is False and runtime.get('original_awards')==[],
      'SUCCESSOR_RUNTIME_SCOPE')
    return value,raw

def components(here,b):
    root=Path(here)/'component';pins=b['component_members']
    expected={'fs_protocol.py','fs_io.py','fs_command.py','fs_carrier.py','full_g2_hooks.py','fs_runner.py','fs_transport.py','bound_child.py',
      'capture_evidence.py','CAPTURE_DIAGNOSTIC_CATALOG.json'}
    need(type(pins) is dict and set(pins)==expected,'EXACT_COMPONENT_POPULATION')
    raws={name:read(root/name,1024**2) for name in pins};need(all(desc(raw)==pins[n] for n,raw in raws.items()),'COMPONENT_PIN')
    order=('fs_protocol','fs_io','fs_command','fs_carrier','full_g2_hooks','fs_runner','fs_transport')
    previous={n:sys.modules.get(n) for n in order};modules={}
    try:
        for name in order:
            m=types.ModuleType(name);m.__file__=str(root/(name+'.py'));sys.modules[name]=m
            exec(compile(raws[name+'.py'],m.__file__,'exec'),m.__dict__);modules[name]=m
    finally:
        for n,old in previous.items():
            if old is None:sys.modules.pop(n,None)
            else:sys.modules[n]=old
    need(all(read(root/n,1024**2)==raw for n,raw in raws.items()),'COMPONENT_READBACK')
    return modules

def artifact_name(role,ctx):
    context(ctx);need(role in ROLE_CAPS,'ARTIFACT_ROLE')
    return ('dg16-full-correspondence-review-'+ctx['run_id']+'-1' if role=='live' else
      'dg16-full-registry-'+ctx['run_id']+'-1' if role=='terminal' else 'dg16-g2-failed-streams-'+ctx['run_id']+'-a1')

def diagnostic_disposition(*,primary_received,primary_status,public_receipt,cipher_received,private_result):
    need(type(primary_received) is bool and type(cipher_received) is bool and type(primary_status) is str,'DISPOSITION_INPUT')
    ready=type(public_receipt) is dict and public_receipt.get('status')=='ENCRYPTED_LOCAL_NOT_PROVIDER_RECEIVED'
    authenticated=(type(private_result) is dict and private_result.get('status')=='AUTHENTICATED_DIAGNOSTIC_STREAMS_RECEIVED'
      and private_result.get('crypto_child_custody')=='ECHILD')
    return dict(schema='dg16.protected-full-outcome-neutral-receiving.v1',authority='NONE',primary_received=primary_received,
      primary_status=primary_status,encrypted_copy_expected=ready,cipher_received=cipher_received,
      complete_private_diagnostic=primary_received and ready and cipher_received and authenticated,
      diagnostic_status='AUTHENTICATED_PRIVATE_STREAMS_AVAILABLE' if primary_received and ready and cipher_received and authenticated else
        'ENCRYPTED_COPY_UNAVAILABLE' if ready and not cipher_received else 'NOT_COMPLETELY_RECEIVED',
      live_acceptance_custody_transferred=False,automatic_retry=False,original_awards=[])
