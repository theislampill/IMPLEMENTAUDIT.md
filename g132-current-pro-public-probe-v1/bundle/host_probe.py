"""Unissued public host probe. Stops before every original protected stage."""
import ast,errno,hashlib,json,os,re,signal,stat,sys,time,types
from pathlib import Path,PurePosixPath
import urllib.request,urllib.error

RUNTIME_SHA256='ca1876e660f6b18b16e5a64edb291bac5e5a083a48e3d8bdc774988fa30820df'
PLACEMENT_SHA256='406fc5e88b1deee8160cfd49363426ca56dbdf1e6f9cae134183a7897fc58034'
HTTP_SHA256='ca5f6cfda9b62aebabe1ed08d82e599f392c3a8581df1232302e5a6774935e32'
FIXTURE_SHA256='8a0279fa1331827e8f26b809a2aa8e34d41196f036449464dd4c86bbb2ba3f55'
INDEX_SHA256='6281cff522f9e13d24992816f9db35c3cff12a45875c9b13bdd6b6d3812ae50a'
BRANCH='engineering/g132-current-pro-public-probe-v1-20261118'
WORKFLOW='.github/workflows/g132-current-pro-public-probe-v1.yml'
REPOSITORY='theislampill/IMPLEMENTAUDIT.md'

def need(v,c):
    if not v:raise ValueError(c)
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return {'bytes':len(b),'sha256':sha(b)}

def owned(path,pin):
    need(path.is_absolute() and path.resolve(strict=True)==path and all(not p.is_symlink() for p in path.parents),'PROBE_SOURCE_PATH')
    before=path.lstat();need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==before.st_gid==0
        and stat.S_IMODE(before.st_mode)==0o400 and 0<before.st_size<=1024**2,'PROBE_SOURCE_CUSTODY')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    try:
        need(mark(os.fstat(fd))==mark(before) and not os.listxattr(fd),'PROBE_SOURCE_OPEN')
        raw=os.pread(fd,1024**2+1,0)
        need(len(raw)==before.st_size and sha(raw)==pin and mark(os.fstat(fd))==mark(before)==mark(path.lstat()),'PROBE_SOURCE_BYTES')
        return raw
    finally:os.close(fd)

def projected(path,pin,namespace):
    raw=owned(path,pin);tree=ast.parse(raw)
    need(all(isinstance(n,(ast.Assign,ast.FunctionDef,ast.ClassDef)) for n in tree.body),'PROBE_PROJECTION_ONLY')
    need(not any(isinstance(n,(ast.Import,ast.ImportFrom)) for n in ast.walk(tree)),'PROBE_NO_ORIGINAL_IMPORT')
    exec(compile(tree,str(path),'exec'),namespace)
    return types.SimpleNamespace(**namespace)

def main():
    # Observations below must come from the actual Root-owned hosted process.
    # Local tests only exercise this refusal; no UID/env/time substitute exists.
    need([os.getuid(),os.geteuid(),os.getgid(),os.getegid()]==[0,0,0,0],'ACTUAL_PUBLIC_PROBE_ROOT_REQUIRED')
    need(sys.platform=='linux' and sys.flags.isolated and sys.dont_write_bytecode,'ACTUAL_ISOLATED_HOST')
    env=os.environ
    need(env.get('GITHUB_ACTIONS')=='true' and env.get('RUNNER_ENVIRONMENT')=='github-hosted'
        and env.get('GITHUB_REPOSITORY')==REPOSITORY and env.get('GITHUB_EVENT_NAME')=='push'
        and env.get('GITHUB_REF')=='refs/heads/'+BRANCH and env.get('GITHUB_RUN_ATTEMPT')=='1'
        and env.get('GITHUB_JOB')=='public-interface-probe','EXACT_PUBLIC_PROBE_CONTEXT')
    need(re.fullmatch('[1-9][0-9]{0,19}',env.get('GITHUB_RUN_ID','')) and re.fullmatch('[0-9a-f]{40}',env.get('GITHUB_SHA',''))
        and env.get('GITHUB_WORKFLOW_SHA')==env['GITHUB_SHA']
        and env.get('GITHUB_WORKFLOW_REF')==REPOSITORY+'/'+WORKFLOW+'@refs/heads/'+BRANCH,'ACTUAL_PUBLIC_PROBE_WORKFLOW')
    root=Path(__file__).resolve().parent
    runtime=owned(root/'current_pro_interfaces.py',RUNTIME_SHA256)
    namespace={'__name__':'current_public_probe_runtime','__file__':str(root/'current_pro_interfaces.py')}
    exec(compile(runtime,str(root/'current_pro_interfaces.py'),'exec'),namespace)
    source=namespace['CurrentSources'](root/'installation')
    need(namespace['INDEX_SHA256']==INDEX_SHA256,'PUBLIC_PROBE_CURRENT_INDEX')
    P=projected(root/'placement_projection.py',PLACEMENT_SHA256,
        {'os':os,'stat':stat,'errno':errno,'json':json,'re':re,'hashlib':hashlib,'PurePosixPath':PurePosixPath})
    identity=P.credentials()
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:custody=P.observe_fd(fd,0o700)
    finally:os.close(fd)
    raw=source.scope_basis_raw
    source.I.validate_scope_basis(source.scope_basis,raw)
    need(P.read_file(root/'installation/phase/tree/qualification/dg16-r5-g1-hosted-episode/ORIGINAL_SCOPE.json',65536)==raw,'EXACT_ORIGINAL_PUBLIC_SCOPE_READ')
    members=P.manifest(source.body(namespace['ENTRY']+'PUBLIC_PACKET_MANIFEST.json'))
    source.G.receive_exact_m4(source.retained_m4_bodies())
    actual_context={'repository':REPOSITORY,'branch':BRANCH,'workflow_path':WORKFLOW,'job_name':env['GITHUB_JOB'],
        'workflow_commit':env['GITHUB_SHA'],'run_id':env['GITHUB_RUN_ID'],'run_attempt':1}
    refused=False
    try:source.context(actual_context)
    except Exception:refused=True
    need(refused,'PUBLIC_PROBE_MUST_NOT_MATCH_PROTECTED_ORIGINAL_CONTEXT')
    fixture=owned(root/'FIXTURE.json',FIXTURE_SHA256)
    def validate_fixture(body,request,request_sha,now_ms,**kwargs):
        need(body==fixture and request is None and request_sha==FIXTURE_SHA256,'EXACT_DISPOSABLE_PUBLIC_FIXTURE')
        need(type(now_ms) is int and abs(now_ms-time.time_ns()//1000000)<1000,'ACTUAL_PUBLIC_FIXTURE_CLOCK')
        return json.loads(body)
    H=projected(root/'http_projection.py',HTTP_SHA256,{
        'urllib':urllib,'signal':signal,'time':time,'re':re,'json':json,'hashlib':hashlib,
        'REPOSITORY':REPOSITORY,'CONTROL_BRANCH':BRANCH,
        'CONTROL_PATH':'g132-current-pro-public-probe-v1/bundle/FIXTURE.json',
        'FINAL_CONTROL_PATH':'g132-current-pro-public-probe-v1/bundle/FIXTURE.json',
        'POLL_COUNT':3,'POLL_SECONDS':.25,'HTTP_SECONDS':5,
        'validate_decision':validate_fixture,'validate_final_decision':validate_fixture})
    began=time.monotonic();body,received,commit=H.read_root_decision(None,FIXTURE_SHA256,began+30)
    need(commit==env['GITHUB_SHA'] and body==fixture,'ACTUAL_PUBLIC_REF_TO_WORKFLOW_JOIN')
    report={'schema':'g132.current-pro-public-host-probe.v1','authority':'NONE',
        'scope':'ACTUAL_PUBLIC_HOST_CUSTODY_SOURCE_AND_PRODUCTION_HTTP_MECHANICS_ONLY',
        'actual_context':actual_context,'actual_uid_euid_gid_egid':identity,'actual_directory_custody':custody,
        'source_index_sha256':INDEX_SHA256,'selected_unissued_host_source':source.identity,
        'original_protected_context':'REFUSED_AS_REQUIRED','public_manifest_members':len(members),
        'exact_original_scope':desc(raw),'retained_m4_members':{n:desc(b) for n,b in source.retained_m4_bodies().items()},
        'actual_http_read':{'commit':commit,'body':desc(body),'elapsed_ms':int((time.monotonic()-began)*1000),
            'source_sha256':HTTP_SHA256,'original_function_bodies_unchanged':True,
            'probe_only_substitutions':['new disposable branch/path','fixture validator','tighter poll/time limits']},
        'full_original_module_imported':False,'original_consumer_invoked':False,'original_sender_started':False,
        'private_inputs_read':False,'reservation_or_original_journal_created':False,'native_model_identity':'NOT_OBSERVED',
        'source_adoption_or_issuer_grant':False,'original_awards':[]}
    print(json.dumps(report,sort_keys=True,separators=(',',':')))

if __name__=='__main__':
    try:main()
    except Exception:
        print(json.dumps({'schema':'g132.current-pro-public-host-probe-refusal.v1','authority':'NONE',
            'status':'PUBLIC_PROBE_REFUSED','original_effects':False},sort_keys=True))
        raise SystemExit(1)
