"""Push delivery for the frozen v2 qualification; no authority from a job alone.

The operator must bind the actual human approval and this exact parentless
payload commit before creating the ref. The program verifies that supplied tuple
and records the honest push context. A hash-shaped ref is not approval evidence.
"""
import base64,hashlib,json,os,re,stat,sys
from pathlib import Path

PREFIX='refs/heads/pro/dg16-direct-encrypt-qualification-'
ACTOR='theislampill'
ACTOR_ID='266501826'
MANIFEST = '60684bc0aefadd772dcfd74a763643bc16bfb4de88b407856f2aff7e932e6973'
class Refusal(ValueError):pass
def need(ok,code):
    if not ok:raise Refusal(code)
def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('ascii')
def sha(b):return hashlib.sha256(b).hexdigest()
def parse(raw,maximum):
    need(type(raw) is bytes and 0<len(raw)<=maximum,'JSON_BOUND')
    def pairs(items):
        out={}
        for k,v in items:need(k not in out,'DUPLICATE_KEY');out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Refusal('NONFINITE')))

def validate_push(env,event):
    need(env.get('GITHUB_ACTIONS')=='true' and env.get('RUNNER_ENVIRONMENT')=='github-hosted'
        and env.get('GITHUB_EVENT_NAME')=='push' and env.get('GITHUB_REPOSITORY')=='theislampill/IMPLEMENTAUDIT.md'
        and env.get('GITHUB_ACTOR')==ACTOR and env.get('GITHUB_ACTOR_ID')==ACTOR_ID
        and env.get('GITHUB_RUN_ATTEMPT')=='1','PROVIDER_CONTEXT')
    ref=env.get('GITHUB_REF','');head=env.get('GITHUB_SHA','');run=env.get('GITHUB_RUN_ID','')
    match=re.fullmatch(re.escape(PREFIX)+'([0-9a-f]{40})-([0-9a-f]{64})',ref)
    need(match is not None and match[1]==head and head!='0'*40 and match[2]!='0'*64
        and re.fullmatch('[1-9][0-9]{0,19}',run) is not None,'APPROVED_TUPLE_BINDING')
    need(type(event) is dict and event.get('created') is True and event.get('deleted') is False
        and event.get('ref')==ref and event.get('after')==head and event.get('before')=='0'*40
        and event.get('repository',{}).get('full_name')=='theislampill/IMPLEMENTAUDIT.md'
        and event.get('sender',{}).get('login')==ACTOR and str(event.get('sender',{}).get('id'))==ACTOR_ID,
        'ACTUAL_BRANCH_CREATION_PUSH')
    if event.get('head_commit') is not None:
        need(type(event['head_commit']) is dict and event['head_commit'].get('id')==head,'PUSH_HEAD_COMMIT')
    return dict(repository=env['GITHUB_REPOSITORY'],ref=ref,head=head,actor=ACTOR,actor_id=ACTOR_ID,
        event='push',created=True,deleted=False,run_id=run,attempt=1,payload_commit=match[1],
        human_approval_sha256=match[2],approval_authenticated_by_job=False)

def projection(bound):
    # Context supplied by the external admission tuple, NOT a grant inferred
    # because GitHub executed something. Root must receive the real approval.
    return dict(schema='dg16.direct-encrypt-qualification-admission.v1',purpose='ONE_MAXIMUM_ENCRYPT_CAPTURE_ONLY',
        source_manifest=MANIFEST,expected_ref=bound['ref'],expected_head=bound['head'],
        owner_approval_sha256=bound['human_approval_sha256'],effect_grant=True,
        maximum_plaintext=268501016,maximum_ciphertext=268517400,maximum_gate_seconds=60,
        maximum_commands=1,private_key_on_host=False,maintained_verifiers=[])

def physical_read(path,maximum,expected=None):
    path=Path(path).absolute();need(path.resolve(strict=True)==path,'PHYSICAL_PATH')
    before=path.lstat();need(stat.S_ISREG(before.st_mode) and before.st_nlink==1
        and not before.st_mode&0o022 and 0<=before.st_size<=maximum,'PHYSICAL_FILE')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        snap=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        need(snap(os.fstat(fd))==snap(before),'OPEN_CHANGED')
        with os.fdopen(fd,'rb',closefd=False) as f:body=f.read(maximum+1)
        need(len(body)==before.st_size and snap(os.fstat(fd))==snap(before)
            and snap(path.lstat())==snap(before),'READ_CHANGED')
        if expected is not None:need(expected=={'bytes':len(body),'sha256':sha(body)},'PAYLOAD_PIN')
        return body
    finally:os.close(fd)

def receive_delivery(result,expected,legacy_receiver):
    need(type(result) is dict and set(result)=={'schema','authority','delivery','manifest_sha256','qualification'},'DELIVERY_FIELDS')
    need(result['schema']=='dg16.push-delivered-qualification.v1' and result['authority']=='NONE'
        and result['manifest_sha256']==MANIFEST,'DELIVERY_SCOPE')
    d=result['delivery'];need(type(d) is dict and set(d)=={'repository','ref','head','actor','actor_id','event','created','deleted',
        'run_id','attempt','payload_commit','human_approval_sha256','approval_authenticated_by_job'},'DELIVERY_CONTEXT_FIELDS')
    need(d['event']=='push' and d['created'] is True and d['deleted'] is False and d['attempt']==1
        and type(d['attempt']) is int and d['approval_authenticated_by_job'] is False
        and d['repository']=='theislampill/IMPLEMENTAUDIT.md' and d['actor']==ACTOR and d['actor_id']==ACTOR_ID,
        'DELIVERY_ACTUAL_CONTEXT')
    need(type(d['head']) is str and re.fullmatch('[0-9a-f]{40}',d['head']) and d['head']!='0'*40
        and type(d['human_approval_sha256']) is str and re.fullmatch('[0-9a-f]{64}',d['human_approval_sha256'])
        and d['human_approval_sha256']!='0'*64 and type(d['run_id']) is str
        and re.fullmatch('[1-9][0-9]{0,19}',d['run_id']),'DELIVERY_IDENTITY_SHAPE')
    need(type(expected) is dict and set(expected)=={'payload_commit','human_approval_sha256','actor'}
        and expected['payload_commit']==d['head']==d['payload_commit']
        and expected['human_approval_sha256']==d['human_approval_sha256'] and expected['actor']==d['actor']
        and d['ref']==PREFIX+d['payload_commit']+'-'+d['human_approval_sha256'],'EXTERNAL_ADMISSION_TUPLE')
    core={k:d[k] for k in ('repository','ref','run_id','attempt','head')}
    need(result['qualification']['context']==core and len(encode(result))<=65536,'QUALIFICATION_PUSH_JOIN')
    return dict(legacy_receiver.receive_public_result(result['qualification'],MANIFEST),
        actual_delivery=d,approval_authenticity='REQUIRES_EXTERNAL_OWNER_RECORD_AND_ACTUAL_PROVIDER_RECEIVING')

def run_payload(root,bound,current,execute):
    payload=root/'payload';raw=physical_read(payload/'SOURCE_MANIFEST.json',65536)
    need(sha(raw)==MANIFEST,'FROZEN_MANIFEST');manifest=parse(raw,65536)
    for name,pin in manifest['members'].items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts and '\\' not in name,'PAYLOAD_MEMBER_PATH')
        physical_read(payload/name,1024**2,pin)
    need(Path.cwd().resolve()==root.resolve(),'CHECKOUT_WORKING_DIRECTORY')
    ns={'__file__':str(payload/'qualification_entry.py'),'__name__':'push_bound_qualification'}
    # The reviewed producer's bytecode and crypto/receiver code stay unchanged.
    # Its entry-context function is the explicit delivery adapter boundary.
    execute(compile(physical_read(payload/'qualification_entry.py',65536,manifest['members']['qualification_entry.py']),
        str(payload/'qualification_entry.py'),'exec'),ns)
    def producer_context():
        actual=current()
        return {k:actual[k] for k in ('repository','ref','run_id','attempt','head')}
    ns['context']=producer_context
    previous=os.environ.get('ADMISSION_JSON');os.environ['ADMISSION_JSON']=encode(projection(bound)).decode().rstrip('\n')
    previous_umask=os.umask(0o077)
    try:
        status=ns['main']()
    finally:
        os.umask(previous_umask)
        if previous is None:os.environ.pop('ADMISSION_JSON',None)
        else:os.environ['ADMISSION_JSON']=previous
    result=parse(physical_read(payload/'QUALIFICATION_RESULT.json',65536),65536)
    return status,dict(schema='dg16.push-delivered-qualification.v1',authority='NONE',delivery=current(),
        manifest_sha256=MANIFEST,qualification=result)

def main():
    event_path=Path(os.environ.get('GITHUB_EVENT_PATH',''))
    event_raw=physical_read(event_path,2*1024**2);event=parse(event_raw,2*1024**2)
    bound=validate_push(os.environ,event)
    root=Path(__file__).absolute().parent;workspace=Path(os.environ['GITHUB_WORKSPACE']).resolve(strict=True)
    need(root==workspace/'qualifier' and root.resolve(strict=True)==root,'FIXED_CHECKOUT_PATH')
    def current():
        need(physical_read(event_path,2*1024**2)==event_raw,'PUSH_EVENT_CHANGED')
        actual=validate_push(os.environ,event);need(actual==bound,'PUSH_CONTEXT_CHANGED');return actual
    status,result=run_payload(root,bound,current,exec)
    body=encode(result)
    if len(body)>65536:
        print('DG16_PUSH_DELIVERY_PUBLIC_BOUND_REFUSED',flush=True);return 4
    line='DG16_DIRECT_ENCRYPT_QUALIFICATION_DELIVERY '+base64.b64encode(body).decode('ascii')
    need(len((line+'\n').encode())<=262144,'ENCODED_LINE_BOUND')
    print(line,flush=True);return status

if __name__=='__main__':
    try:code=main()
    except BaseException:
        print('DG16_PUSH_DELIVERY_REFUSED_OR_INTERRUPTED; no retry or acceptance',flush=True);code=4
    sys.exit(code)
