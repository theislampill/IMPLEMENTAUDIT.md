#!/usr/bin/env python3
"""One full current registry episode; mechanical raw receiving, authority NONE.

Fresh-controller recipe derived from independently reviewed bank03. The retained
pair driver uses the same source checkout and explicitly selects maintained
plan.v2 single-proc custody. Private history and raw captures never become public.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import sys
import time
import types

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg16-r5-full-g2-02-20261105'
SOURCE_COMMIT = '35bf9823856eb4efe254b882954120480632230e'
SOURCE_TREE = 'abe08aabc83de3b27c43e6acf28646fb089f0f34'
UTILITY_SHA = '429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'
MANIFEST_SHA = 'e0d36174d13e60081a87f42e70b6d09179f2441c4e8d3c0c652671e6dd4ead0c'
PAIR_DRIVER_SHA = '8fe702b0ba718242611db3862e9e3ae6fa9dd3e5bf722ffe3239edbb82fddf0f'
PREREQUISITE_SHA = '030f5ef9c5b81394eb1d90e8cfb7c7c95271a66d6a4b8281036b364f323b2ff4'
OWNER = 'skills/implementaudit/scripts/claim-run.sh'
AUTHOR = 'fixtures/controller-initialization/author_checkpoint.py'
STEPS = ('provision','preflight','initialize','discover','invalidate','read-state','read-roadmap',
         'resume','verify','require','pair','receive')
NAMES = ('STATE.md','PROTOCOL.md','ROADMAP.md','THINKING.md','sidecars.md','tools.md','context.md')
PUBLIC_NAMES = ('RESULT.json','HOST.json','SOURCE.json','PROBE.json','CLEANUP.json','FAILURE.json','ARTIFACT_MANIFEST.json')
RUN_SECONDS, BANK_SECONDS, FINAL_SECONDS = 8400, 7200, 90
RECEIVE_SECONDS, SETUP_SECONDS = 300, 600
# Match the maintained initialization owner's 1 MiB canonical-file bound.
# The independent private aggregate and public transport bounds stay unchanged.
PRIVATE_CANONICAL_BYTES = 1024 * 1024
PURPOSE = 'Execute the complete current verifier registry once through legacy then DAG under a fresh current hosted controller, retaining raw sealed evidence and same-job mechanical receiving.'
NEXT_ACTION = 'Derive the actual registry, use explicit maintained single-proc plan.v2, preserve the full raw relation, and independently re-read sealed captures before teardown; no full normalization, original acceptance, G1, C5, G3 or full CI award.'
KNOWN_CODES = ('CONTINUITY_TRANSPORT_NAMESPACE_REFUSED','CONTINUITY_TRANSPORT_TIMEOUT','CANONICAL_WORK_GRAPH','SOURCE_PROFILE_REFUSED','NATIVE_CHECKPOINT','NETLINK_ROUTE','OS_OPERATION_NOT_PERMITTED','OS_PERMISSION_DENIED','OS_REQUIRED_PATH_UNAVAILABLE')
EXCEPTIONS = ('AssertionError','RuntimeError','ValueError','OSError','TimeoutError','WorkGraphError','ContinuityTransportError','FileNotFoundError','PermissionError','OTHER')

class Refusal(Exception): pass
class Deadline(Exception): pass

def need(value, code):
    if not value: raise Refusal(code)

def digest(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
def token(raw, pattern):
    text=raw.decode('ascii').strip(); need(re.fullmatch(pattern,text) is not None,'OWNER_TOKEN_SHAPE_REFUSED'); return text

def load_utility():
    path=Path(__file__).with_name('host_utility.py')
    raw=path.read_bytes(); need(digest(raw)==UTILITY_SHA,'UTILITY_DIGEST_REFUSED')
    module=types.ModuleType('sealed_host_utility'); module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module

def identities(path):
    p=Path(path); st=p.lstat();need(stat.S_ISDIR(st.st_mode) and not p.is_symlink(),'DIRECTORY_CUSTODY_REFUSED')
    return [st.st_dev,st.st_ino,st.st_uid]

def read_manifest(u):
    raw=u.checked_file(Path(__file__).with_name('SOURCE_MANIFEST.json'),1024*1024)
    need(digest(raw)==MANIFEST_SHA,'SOURCE_MANIFEST_DIGEST_REFUSED'); m=u.parse_json(raw)
    need(set(m)=={'schema','repository','commit','tree','file_count','total_bytes','members'} and
         m['schema']=='dg16.linux-native-source-manifest.v2' and m['repository']==REPOSITORY and
         m['commit']==SOURCE_COMMIT and m['tree']==SOURCE_TREE and m['file_count']==1743 and
         m['total_bytes']==164981630 and len(m['members'])==1743,'SOURCE_MANIFEST_SHAPE_REFUSED')
    result={}
    for row in m['members']:
        need(set(row)=={'path','mode','git_blob','bytes','sha256'} and isinstance(row['path'],str),'SOURCE_MEMBER_REFUSED')
        p=PurePosixPath(row['path']);need(not p.is_absolute() and '..' not in p.parts and str(p)==row['path'] and
             row['path'] not in result and row['mode'] in ('100644','100755') and
             type(row['bytes']) is int and 0<=row['bytes']<=256*1024**2 and
             re.fullmatch('[0-9a-f]{40}',row['git_blob']) and re.fullmatch('[0-9a-f]{64}',row['sha256']), 'SOURCE_MEMBER_REFUSED')
        result[row['path']]=row
    need(sum(row['bytes'] for row in result.values())==m['total_bytes'],'SOURCE_SIZE_REFUSED')
    return result

def verify_source(source,manifest,u,runtime=False):
    observed=set();total=0
    allowed_dirs={str(p) for name in manifest for p in PurePosixPath(name).parents if str(p)!='.'}
    for parent,dirs,files in os.walk(source,followlinks=False):
        here=Path(parent)
        for name in list(dirs):
            p=here/name; rel=p.relative_to(source).as_posix(); st=p.lstat()
            need(stat.S_ISDIR(st.st_mode) and not p.is_symlink(),'SOURCE_DIRECTORY_SHAPE_REFUSED')
            if here==source and name=='.git':dirs.remove(name)
            elif here==source and name=='.IMPLEMENTAUDIT':
                need(runtime,'UNEXPECTED_RUNTIME_BEFORE_CLAIM');dirs.remove(name)
            else:need(rel in allowed_dirs,'UNEXPECTED_SOURCE_DIRECTORY')
        for name in files:
            p=here/name;rel=p.relative_to(source).as_posix()
            need(rel in manifest,'UNEXPECTED_SOURCE_FILE');row=manifest[rel];st=p.lstat()
            need(stat.S_ISREG(st.st_mode) and st.st_nlink==1 and not st.st_mode & 0o6000 and
                 bool(st.st_mode & 0o111)==(row['mode']=='100755'),'SOURCE_FILE_MODE_REFUSED')
            raw=u.checked_file(p,256*1024**2);need(len(raw)==row['bytes'] and digest(raw)==row['sha256'] and
                 hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'SOURCE_BYTES_REFUSED')
            total+=len(raw);observed.add(rel)
    need(observed==set(manifest) and total==164981630,'SOURCE_POPULATION_REFUSED')
    return {'file_count':len(observed),'total_bytes':total,'manifest_sha256':MANIFEST_SHA,'all_members_match':True}

def runtime_snapshot(source,state,u):
    run=state['run_root'];need(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9][a-z0-9-]*-[A-Za-z0-9]{6}',run),'RUN_ROOT_SHAPE_REFUSED')
    base=source/'.IMPLEMENTAUDIT'; expected={'.r36-locks/namespace.gate'}
    prefix=run.removeprefix('.IMPLEMENTAUDIT/')+'/'
    expected.update(prefix+n for n in (*NAMES,'phases/phase-1.md','.claimed','.controller'))
    observed={};directories=set();total=0
    for parent,dirs,files in os.walk(base,followlinks=False):
        here=Path(parent);st=here.lstat();need(stat.S_ISDIR(st.st_mode) and st.st_uid==os.geteuid() and not here.is_symlink(),'RUNTIME_DIRECTORY_REFUSED')
        directories.add(here.relative_to(base).as_posix())
        for name in dirs:need(not (here/name).is_symlink(),'RUNTIME_SYMLINK_REFUSED')
        for name in files:
            p=here/name;rel=p.relative_to(base).as_posix();st=p.lstat();need(rel in expected and st.st_uid==os.geteuid(),'RUNTIME_POPULATION_REFUSED')
            canonical_member=rel.startswith(prefix) and rel[len(prefix):] in (*NAMES,'phases/phase-1.md')
            raw=u.checked_file(p,PRIVATE_CANONICAL_BYTES if canonical_member else 65536);total+=len(raw);need(total<=512*1024,'RUNTIME_AGGREGATE_BOUND')
            observed[rel]={'bytes':len(raw),'sha256':digest(raw),'device':st.st_dev,'inode':st.st_ino}
    expected_dirs={'.','.r36-locks','runs',run.removeprefix('.IMPLEMENTAUDIT/'),run.removeprefix('.IMPLEMENTAUDIT/')+'/phases'}
    need(set(observed)==expected and directories==expected_dirs,'RUNTIME_POPULATION_REFUSED')
    need(observed['.r36-locks/namespace.gate']['bytes']==1,'RUNTIME_GATE_SHAPE_REFUSED')
    return observed

def write_private(path,raw):
    need(not path.exists(),'PRIVATE_MEMBER_ALREADY_EXISTS')
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    os.chmod(path,0o600)

def save_state(path,state):
    tmp=path.with_suffix('.next');need(not tmp.exists(),'STATE_WRITE_INTERRUPTED')
    with tmp.open('xb') as f:f.write(canonical(state));f.flush();os.fsync(f.fileno())
    os.chmod(tmp,0o600);os.replace(tmp,path)

def host_context(output,source,mode):
    e=os.environ;need(e.get('GITHUB_ACTIONS')=='true' and e.get('GITHUB_REPOSITORY')==REPOSITORY and
         e.get('GITHUB_EVENT_NAME')=='push' and e.get('GITHUB_REF')=='refs/heads/'+BRANCH and
         e.get('GITHUB_RUN_ATTEMPT')=='1','EVENT_GUARD_REFUSED')
    run=e.get('GITHUB_RUN_ID','');sha=e.get('GITHUB_SHA','')
    need(re.fullmatch('[0-9]{1,20}',run) and re.fullmatch('[0-9a-f]{40}',sha),'HOSTED_IDENTITY_REFUSED')
    workspace=Path(e['GITHUB_WORKSPACE']).resolve(strict=True);temp=Path(e['RUNNER_TEMP']).resolve(strict=True)
    need(output==temp/('dg16-full-g2-episode-'+run+'-1') and source==workspace/'qualified-source' and
         source.resolve(strict=True)==source,'RESOURCE_SCOPE_REFUSED')
    need(Path(__file__).absolute().parent==workspace/'packet/qualification/dg16-r5-full-g2','PACKET_LOCATION_REFUSED')
    return {'repository':REPOSITORY,'branch':BRANCH,'run_id':run,'run_attempt':1,'workflow_commit':sha}

def checked_driver(u):
    path=Path(__file__).with_name('pair_driver.py')
    need(digest(u.checked_file(path,131072))==PAIR_DRIVER_SHA,'PAIR_DRIVER_DIGEST_REFUSED')
    return path

def prerequisite_host(host,u):
    raw=u.checked_file(Path(__file__).with_name('EARNED_PREREQUISITE.json'),16384)
    need(digest(raw)==PREREQUISITE_SHA,'EARNED_PREREQUISITE_DIGEST_REFUSED')
    value=u.parse_json(raw)
    need(value['schema']=='dg16.full-registry-earned-prerequisite.v1' and value['run_id']=='42092153646' and
         value['tests_run']==9 and value['status']=='QUALIFIED_AT_DECLARED_SCOPE' and
         value['receiving_status']=='RECEIVED_AT_DECLARED_SCOPE','EARNED_PREREQUISITE_SHAPE_REFUSED')
    need({key:host[key] for key in ('os','architecture','kernel','python_version','tools')}==value['host_prerequisite'],
         'NATIVE_PREREQUISITE_HOST_PROFILE_CHANGED')

def setup_sudo(u):
    # Administrative provisioning intentionally uses distro sudo. Its expected
    # setuid bit is not allowed into the native transport's non-setid profile.
    pending=['usr','bin','sudo'];path=Path('/');links=0;root=path.lstat()
    need(stat.S_ISDIR(root.st_mode) and root.st_uid==0 and not root.st_mode&0o022,'SETUP_ROOT_CUSTODY_REFUSED')
    observed=[{'path':'/','device':root.st_dev,'inode':root.st_ino,'mode':root.st_mode,
               'uid':root.st_uid,'gid':root.st_gid,'links':root.st_nlink}]
    while pending:
        name=pending.pop(0)
        if name in ('','.'):continue
        if name=='..':path=path.parent;continue
        candidate=path/name;info=candidate.lstat()
        need(info.st_uid==0,'SETUP_SUDO_OWNERSHIP_REFUSED')
        observed.append({'path':str(candidate),'device':info.st_dev,'inode':info.st_ino,
                         'mode':info.st_mode,'uid':info.st_uid,'gid':info.st_gid,'links':info.st_nlink})
        if stat.S_ISLNK(info.st_mode):
            links+=1;target=os.readlink(candidate)
            need(links<=16 and len(target.encode())<=4096,'SETUP_SUDO_ALIAS_BOUND')
            observed[-1]['target_sha256']=digest(os.fsencode(target))
            target_path=Path(target)
            if target_path.is_absolute():path=Path('/');parts=target_path.parts[1:]
            else:parts=target_path.parts
            pending=list(parts)+pending
        else:
            need(not info.st_mode&0o022 and (stat.S_ISDIR(info.st_mode) if pending else stat.S_ISREG(info.st_mode)),
                 'SETUP_SUDO_ANCESTRY_REFUSED')
            path=candidate
    need(path.parent==Path('/usr/bin') and path.name in ('sudo','sudo-rs','sudo.ws'),'SETUP_SUDO_TARGET_REFUSED')
    info=path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_uid==0 and 1<=info.st_nlink<=16 and
         stat.S_IMODE(info.st_mode)==0o4755,'SETUP_SUDO_PROFILE_REFUSED')
    raw=u.checked_file(path,64*1024*1024,single_link=False)
    return {'bytes':len(raw),'sha256':digest(raw),'mode':0o4755,'uid':0,
            'canonical':str(path),'aliases_and_ancestors':observed,
            'scope':'ADMINISTRATIVE_PACKAGE_SETUP_ONLY_NOT_NATIVE_TRANSPORT'}

def hash_record(value):
    need(type(value) is dict and set(value)=={'bytes','sha256'} and
         type(value['bytes']) is int and 0<=value['bytes']<=128*1024*1024 and
         type(value['sha256']) is str and re.fullmatch('[0-9a-f]{64}',value['sha256']), 'PAIR_HASH_RECORD_REFUSED')
    return value

def validate_pair_summary(value):
    literals={
      'schema':'dg16.full-registry-operation.v1','authority':'NONE',
      'source_commit':SOURCE_COMMIT,'source_tree':SOURCE_TREE,
      'capture_plan_schema':'implementaudit.verifier-pair-plan.v2',
      'capture_process_profile':'MAINTAINED_SINGLE_PROC_PIDFD_V2_EXPLICIT_SELECTION',
      'source_checkout':'SAME_CHECKOUT_AS_FRESH_CONTROLLER','source_cloned':False,
      'normalization':'NONE_RAW_BYTES','finite_normalization_unchanged':True,
      'full_population_normalization_adopted':False,'original_acceptance':False,
      'full_G2':False,'C5':False,'G1':False,'G3':False,'full_T14':False,
      'failed_or_unsealed_attempts_are_not_received_as_complete':True,
      'private_raw_captures':'LIVE_JOB_ONLY_RECEIVE_BEFORE_TEARDOWN_NO_CUSTODY_TRANSFER',
      'ordinary_toolchain_scope':'ACTUAL_EXECUTABLE_AND_VENV_BOOKENDS_PARTIAL_NOT_C5',
      'ci_applicability':'CANONICAL_PACKAGE_LEG_ONLY_OTHER_VALIDATE_WORKFLOW_STEPS_UNQUALIFIED'}
    required=set(literals)|{'status','subject_verifier_attempts','receiving_status','records','raw_relation'}
    optional={'mapping','receive_record','same_live_source_current','ordinary_toolchain_unchanged'}
    need(type(value) is dict and required<=set(value)<=required|optional,'PAIR_SUMMARY_KEYS_REFUSED')
    for key,expected in literals.items():need(type(value[key]) is type(expected) and value[key]==expected,'PAIR_SUMMARY_LITERAL_REFUSED')
    need(value['status'] in ('COMPLETE_PAIR_RAW_RELATION_RECORDED','INCOMPLETE_OR_FAILED_OPERATION') and
         type(value['subject_verifier_attempts']) is int and 0<=value['subject_verifier_attempts']<=2 and
         value['receiving_status'] in ('NOT_RECEIVED','RECEIVED_COMPLETE_RAW_PAIR','RECEIVED_PARTIAL_FAILED_OPERATION','NO_SEALED_CAPTURE_RECEIVED'),
         'PAIR_STATUS_REFUSED')
    count=None
    if 'mapping' in value:
        mapping=value['mapping']
        need(type(mapping) is dict and set(mapping)=={'mapped_nodes','registered_tests','mapping','physical_tests','command_stream','exact_registry_reassembly'} and
             all(type(mapping[k]) is int and 0<=mapping[k]<=4096 for k in ('mapped_nodes','registered_tests')) and
             type(mapping['exact_registry_reassembly']) is bool,'PAIR_MAPPING_REFUSED')
        for key in ('mapping','physical_tests','command_stream'):hash_record(mapping[key])
        count=mapping['mapped_nodes']
    records=value['records'];need(type(records) is list and len(records)<=2,'PAIR_RECORDS_REFUSED')
    modes=[]
    for record in records:
        need(type(record) is dict and set(record)=={'mode','exit','elapsed_ms','mapped_nodes','registration_complete',
             'stdout_sha256','stderr_sha256','registry_sha256','graph_digest','nodes','legacy_node_trace','test_level_skip_semantics'} and
             record['mode'] in ('legacy','dag') and type(record['exit']) is int and -255<=record['exit']<=255 and
             type(record['elapsed_ms']) is int and 0<=record['elapsed_ms']<=8400000 and
             type(record['mapped_nodes']) is int and record['mapped_nodes']==count and
             type(record['registration_complete']) is bool,'PAIR_RECORD_REFUSED')
        for key in ('stdout_sha256','stderr_sha256','registry_sha256','graph_digest'):
            need(type(record[key]) is str and re.fullmatch('[0-9a-f]{64}',record[key]),'PAIR_RECORD_HASH_REFUSED')
        need(record['legacy_node_trace']==('UNAVAILABLE_WHOLE_PROCESS_ONLY' if record['mode']=='legacy' else 'NOT_APPLICABLE') and
             record['test_level_skip_semantics']=='RETAINED_IN_PRIVATE_RAW_STREAMS_NO_SYNTHETIC_PASS','PAIR_RECORD_SCOPE_REFUSED')
        nodes=record['nodes'];need(type(nodes) is list and len(nodes)==count,'PAIR_NODE_POPULATION_REFUSED')
        for ordinal,row in enumerate(nodes):
            need(type(row) is dict and set(row)=={'ordinal','status','terminal'} and type(row['ordinal']) is int and
                 row['ordinal']==ordinal and row['status'] in ('PASS','FAIL','INTERRUPTED','UNSETTLED') and
                 type(row['terminal']) is bool and row['terminal']==(row['status']!='UNSETTLED'),'PAIR_NODE_REFUSED')
            if record['mode']=='legacy':need(row['status']=='UNSETTLED','SYNTHETIC_LEGACY_NODE_VERDICT_REFUSED')
        modes.append(record['mode'])
    need(modes in ([],['legacy'],['legacy','dag']),'PAIR_MODE_ORDER_REFUSED')
    relation=value['raw_relation']
    if relation is not None:
        checks=('same_source','same_registry','same_environment','same_record_schema','same_exit','same_stdout','same_stderr',
          'route_pair','same_engine','same_execution_cwd','same_compiled_stream','same_child_environment','same_declared_repro_artifacts',
          'same_stdin','same_dist_namespace','same_portal_events','same_repro_events')
        need(type(relation) is dict and set(relation)=={'checks','raw_observables_equal','normalization','authority',
             'full_population_normalization_adopted','finite_normalization_unchanged'} and
             type(relation['checks']) is dict and set(relation['checks'])==set(checks) and all(type(x) is bool for x in relation['checks'].values()) and
             type(relation['raw_observables_equal']) is bool and relation['raw_observables_equal']==all(relation['checks'].values()) and
             relation['normalization']=='NONE_RAW_BYTES' and relation['authority']=='NONE' and
             relation['full_population_normalization_adopted'] is False and relation['finite_normalization_unchanged'] is True,'RAW_RELATION_REFUSED')
    if value['receiving_status']!='NOT_RECEIVED':
        need({'receive_record','same_live_source_current','ordinary_toolchain_unchanged'}<=set(value) and
             value['same_live_source_current'] is True and value['ordinary_toolchain_unchanged'] is True,'RECEIVE_BINDING_REFUSED')
        hash_record(value['receive_record'])
    else:need(not (set(value)&{'receive_record','same_live_source_current','ordinary_toolchain_unchanged'}),'UNRECEIVED_FIELDS_REFUSED')
    if value['receiving_status']=='RECEIVED_COMPLETE_RAW_PAIR':
        need(modes==['legacy','dag'] and all(r['exit']==0 and r['registration_complete'] for r in records) and
             value['subject_verifier_attempts']==2 and value['status']=='COMPLETE_PAIR_RAW_RELATION_RECORDED' and
             relation is not None and value['mapping']['exact_registry_reassembly'],'COMPLETE_RECEIVING_REFUSED')
    return value

def read_pair_summary(output,received,u):
    path=output/'private/full-pair'/('RECEIVED_PUBLIC.json' if received else 'OPERATION_PUBLIC.json')
    return validate_pair_summary(u.parse_json(u.checked_file(path,49152)))

def emit_bound_public(output,source,u):
    host_context(output,source,'emit-public')
    state=u.parse_json(u.checked_file(output/'private/episode.json',1024*1024))
    need(state['context']==host_context(output,source,'emit-public'),'EMISSION_CONTEXT_CHANGED')
    probe=state['docs']['PROBE.json']
    if probe['result'] is not None:
        validate_pair_summary(probe['result'])
        received=probe['result']['receiving_status']!='NOT_RECEIVED'
        need(read_pair_summary(output,received,u)==probe['result'],'EMISSION_OPERATION_CHANGED')
    if 'unaccepted_receiving_observation' in probe:
        candidate=read_pair_summary(output,True,u)
        expected={'bytes':len(canonical(candidate)),'sha256':digest(canonical(candidate)),
                  'receiving_status':candidate['receiving_status'],'scope':'UNACCEPTED_CALLER_CLEANUP_REFUSED'}
        need(expected==probe['unaccepted_receiving_observation'],'EMISSION_UNACCEPTED_OBSERVATION_CHANGED')
    files={name:u.canonical(state['docs'][name]) for name in PUBLIC_NAMES if name!='ARTIFACT_MANIFEST.json'}
    files['ARTIFACT_MANIFEST.json']=u.canonical({'schema':'dg16.linux-host-artifacts.v1','members':[
        {'name':name,'bytes':len(raw),'sha256':digest(raw)} for name,raw in sorted(files.items())]})
    public=output/'public'
    need(public.resolve(strict=True)==public and {p.name for p in public.iterdir()}==set(PUBLIC_NAMES),'EMISSION_PUBLIC_POPULATION')
    need(all(u.checked_file(public/name,u.FILE_LIMIT)==raw for name,raw in files.items()),'EMISSION_PUBLIC_BYTES_CHANGED')
    lines=u.transport_lines(files)
    for line in lines:print(line,flush=True)

def provision(state,source,output,tools,u,command):
    private=output/'private';started=time.monotonic()
    def setup(label,argv):
        seconds=max(1,int(SETUP_SECONDS-(time.monotonic()-started)))
        need(seconds>1,'SETUP_WATCHDOG')
        rc,out,err=command(label,argv,seconds=seconds)
        write_private(private/(label+'.stdout'),out);write_private(private/(label+'.stderr'),err)
        need(rc==0,'ORDINARY_TOOLCHAIN_SETUP_REFUSED')
        return out
    sudo_fact=setup_sudo(u)
    path,fact=u.trusted('apt-get');need(path is not None,'SETUP_TOOL_UNTRUSTED')
    write_private(private/'administrative-setup-tool.json',canonical(sudo_fact))
    setup('ordinary-apt-index',[sudo_fact['canonical'],'-n','/usr/bin/apt-get','-qq','update'])
    setup('ordinary-apt-prerequisites',[sudo_fact['canonical'],'-n','/usr/bin/apt-get','-qq','install','-y',
         '--no-install-recommends','--no-upgrade','python3-venv','ripgrep','nodejs'])
    venv=private/'ordinary-venv';need(not venv.exists(),'ORDINARY_VENV_ALREADY_EXISTS')
    setup('ordinary-create-venv',[tools['python3'],'-I','-B','-m','venv',str(venv)])
    setup('ordinary-install-release-dependency',[str(venv/'bin/python'),'-I','-B','-m','pip','--isolated',
         '--disable-pip-version-check','--no-input','-q','install','--no-deps','--no-compile','--no-cache-dir',
         '--requirement',str(source/'requirements-release.txt')])
    raw=setup('ordinary-release-dependency-readback',[str(venv/'bin/python'),'-I','-B','-c',
         "import hashlib,importlib.metadata,json,pathlib,zopfli,zopfli.zlib;v=importlib.metadata.version('zopfli');assert v=='0.2.3.post1';p=pathlib.Path(zopfli.__file__);print(json.dumps({'version':v,'module_bytes':p.stat().st_size,'module_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))"])
    value=u.parse_json(raw)
    need(type(value) is dict and set(value)=={'version','module_bytes','module_sha256'} and value['version']=='0.2.3.post1' and
         type(value['module_bytes']) is int and 0<value['module_bytes']<65536 and
         type(value['module_sha256']) is str and re.fullmatch('[0-9a-f]{64}',value['module_sha256']),'ORDINARY_DEPENDENCY_READBACK_REFUSED')
    need(setup_sudo(u)==sudo_fact and u.trusted('apt-get')[1]==fact,'ADMINISTRATIVE_SETUP_TOOL_CHANGED')
    state['docs']['PROBE.json']['ordinary_setup']={'status':'COMPLETED','zopfli_version':'0.2.3.post1',
         'module_bytes':value['module_bytes'],'module_sha256':value['module_sha256'],
         'elapsed_seconds':time.monotonic()-started,'watchdog_seconds':SETUP_SECONDS,'C5':False}


def fresh_state(context,source,output):
    start=time.monotonic()
    return {'schema':'dg16.linux-native-private-episode.v1','context':context,
       'controller':'r5-full-g2-'+context['run_id']+'-a1','run_root':None,'receipt':None,
       'completed':[],'failed':False,'started_monotonic':start,'deadline_monotonic':start+RUN_SECONDS,
       'source_directory_identity':identities(source),'git_directory_identity':identities(source/'.git'),
       'output_directory_identity':identities(output),'runtime':None,'reads':{},
       'docs':{
        'RESULT.json':dict(context,schema='dg16.full-registry-episode-result.v1',status='UNQUALIFIED',
          scope='COMPLETE_CURRENT_REGISTRY_RAW_PAIR_AND_SAME_JOB_MECHANICAL_RECEIVING',
          G1=False,C5=False,full_G2=False,G3=False,full_T14=False,original_acceptance=False,audit_closure=False,
          independent_assessment=False,automatic_retry=False,adapter_sha256=digest(Path(__file__).read_bytes()),
          utility_sha256=UTILITY_SHA,pair_driver_sha256=PAIR_DRIVER_SHA,source_manifest_sha256=MANIFEST_SHA),
        'HOST.json':{'schema':'dg16.full-registry-episode-host.v1','tools':{},'commands':[]},
        'SOURCE.json':{'schema':'dg16.full-registry-episode-source.v1','commit':SOURCE_COMMIT,'tree':SOURCE_TREE,
                       'before':None,'after':None,'tracked_source_mutations':False},
        'PROBE.json':{'schema':'dg16.full-registry-episode-operation.v1','started':False,'result':None,
           'result_disposition':'NOT_OBSERVED','phases':[],'fresh_controller':False,
           'separate_state_roadmap_reads':False,'currentness_before_pair':False,
           'receiving':{'status':'NOT_RECEIVED','authority':'NONE','receipt_transfer_authority':False},
           'episode_watchdog_seconds':RUN_SECONDS,'pair_watchdog_seconds':BANK_SECONDS,
           'receiving_watchdog_seconds':RECEIVE_SECONDS,'setup_watchdog_seconds':SETUP_SECONDS,
           'qualification_threshold_claimed':False,'elapsed_subtraction':0},
        'CLEANUP.json':{'schema':'dg16.full-registry-episode-cleanup.v1','all_step_children_reaped':True,
           'source_unchanged':False,'runtime_unchanged_after_initialization':False,
           'private_outputs_uploaded':False,'private_retention':'LIVE_JOB_ONLY; no universal interrupted-stream retention'},
        'FAILURE.json':{'schema':'dg16.full-registry-episode-failure.v1','present':False,'failures':[]}
       }}

def inventory(u):
    need(sys.platform=='linux' and os.name=='posix' and os.geteuid()!=0 and os.uname().machine=='x86_64','HOST_IDENTITY_REFUSED')
    release={}
    for line in u.checked_file(Path('/etc/os-release').resolve(),16384).decode().splitlines():
        if '=' in line:
            k,v=line.split('=',1)
            if k in ('ID','VERSION_ID'):release[k]=u.token(v.strip('"'),32)
    need(release=={'ID':'ubuntu','VERSION_ID':'26.04'},'OS_IMAGE_REFUSED')
    paths={};facts={}
    for name in ('bwrap','bash','python3','git'):
        paths[name],facts[name]=u.trusted(name);need(paths[name] is not None,'TRUSTED_TOOL_UNAVAILABLE')
    need(Path(sys.executable).resolve()==Path(paths['python3']),'INTERPRETER_IDENTITY_REFUSED')
    host={'os':release,'architecture':'x86_64','kernel':u.token(os.uname().release),'uid':os.geteuid(),
      'python_version':list(sys.version_info[:3]),'image_os':u.token(os.environ.get('ImageOS','')),
      'image_version':u.token(os.environ.get('ImageVersion','')),'tools':facts,
      'boot_identity_sha256':digest(u.checked_file(Path('/proc/sys/kernel/random/boot_id'),128))}
    return paths,host

def enable_subreaper():
    lib=ctypes.CDLL(None,use_errno=True);actual=ctypes.c_int()
    need(lib.prctl(36,1,0,0,0)==0 and lib.prctl(37,ctypes.byref(actual),0,0,0)==0 and actual.value==1,'SUBREAPER_REFUSED')

def check_source_git(command,tools,source,full=False):
    rc,out,err=command('source-identity',[tools['git'],'-C',str(source),'rev-parse','HEAD','HEAD^{tree}'])
    need(rc==0 and not err and out.decode().splitlines()==[SOURCE_COMMIT,SOURCE_TREE],'SOURCE_GIT_IDENTITY_REFUSED')
    if not full:return
    for kind,args in (('index-clean',['diff','--cached','--quiet','--exit-code']),('tracked-clean',['diff','--quiet','--exit-code'])):
        rc,out,err=command(kind,[tools['git'],'-C',str(source),*args]);need(rc==0 and not out and not err,'SOURCE_TRACKED_STATE_CHANGED')

def operation(step,state,source,output,tools,u,manifest,command):
    docs=state['docs'];probe=docs['PROBE.json'];helper=str(source/OWNER);controller=state['controller'];private=output/'private'
    def owner(label,args):
        rc,out,err=command(label,[tools['bash'],helper,*args]);need(rc==0,'MAINTAINED_OWNER_REFUSED')
        write_private(private/(label+'.stdout'),out);write_private(private/(label+'.stderr'),err)
        return out
    def current(label):
        raw=owner(label,['--require-current-continuity',controller]);need(raw.decode().strip()==state['receipt'],'CURRENT_RECEIPT_CHANGED');return digest(raw)
    if step=='provision':
        provision(state,source,output,tools,u,command)
    elif step=='preflight':
        docs['SOURCE.json']['before']=verify_source(source,manifest,u,False)
        rc,out,err=command('no-imported-controller-refs',[tools['git'],'for-each-ref','--format=%(refname)','refs/implementaudit'])
        need(rc==0 and not out and not err,'PREEXISTING_CONTROLLER_REFS_REFUSED')
    elif step=='initialize':
        raw=owner('fresh-claim',['--controller',controller,'r5-full-registry-pair'])
        run=token(raw,r'\.IMPLEMENTAUDIT/runs/r5-full-registry-pair-[A-Za-z0-9]{6}');state['run_root']=run
        rc,out,err=command('author-real-task',[tools['python3'],'-I','-S','-B',str(source/AUTHOR),
             '--repo',str(source),'--run-root',run,'--source',str(source),'--purpose',PURPOSE,'--next-action',NEXT_ACTION])
        write_private(private/'author-real-task.stdout',out);write_private(private/'author-real-task.stderr',err)
        need(rc==0,'REAL_TASK_AUTHOR_REFUSED');value=u.parse_json(out)
        need(type(value) is dict and set(value)==set((*NAMES,'phases/phase-1.md')) and all(type(v) is str and re.fullmatch('[0-9a-f]{64}',v) for v in value.values()),'AUTHOR_RESULT_SHAPE_REFUSED')
        for name,sha in value.items():need(digest(u.checked_file(source/run/name,PRIVATE_CANONICAL_BYTES))==sha,'AUTHORED_TASK_READBACK_REFUSED')
        inspected=u.parse_json(owner('inspect-initialization',['--inspect-controller-initialization',controller,'--run-root',run]))
        init=inspected['initialization_token'];need(type(init) is str and re.fullmatch('refs/implementaudit/controller-initializations/'+controller+r'/[0-9a-f]{32}@[0-9a-f]{40}',init),'INITIALIZATION_TOKEN_REFUSED')
        activated=u.parse_json(owner('activate-initialization',['--activate-controller',controller,'--run-root',run,'--expected-initialization',init]))
        need(activated.get('status')=='BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS' and
             activated.get('authority_ceiling')=='ELIGIBLE_FOR_NORMAL_CURRENTNESS_ONLY','ACTIVATION_SCOPE_REFUSED')
        state['runtime']=runtime_snapshot(source,state,u);probe['fresh_controller']=True
        probe['fresh_initialization_sha256']=digest(canonical(activated))
    elif step=='discover':
        raw=owner('discover-controller',['--current-controller',controller]);fields=raw.decode().strip().split('\t')
        need(len(fields)==4 and fields[0]==controller and Path(fields[1])==source and
             Path(fields[2])==source/state['run_root'],'CURRENT_CONTROLLER_CONTEXT_REFUSED')
        probe['same_checkout_controller_discovered']=True
    elif step=='invalidate':
        event='github-run-'+state['context']['run_id']+'-attempt-1-fresh-hosted-job'
        raw=owner('invalidate-new-session',['--invalidate-continuity',controller,'--boundary','new-session','--event',event])
        state['invalidation']=token(raw,'refs/implementaudit/continuity-invalidations/'+controller+r'@[0-9a-f]{40}')
        probe['boundary_invalidation_sha256']=digest(raw)
    elif step in ('read-state','read-roadmap'):
        name='STATE.md' if step=='read-state' else 'ROADMAP.md';path=source/state['run_root']/name
        raw=u.checked_file(path,PRIVATE_CANONICAL_BYTES);write_private(private/(step+'.read'),raw)
        # These invocations are distinct ordered Actions steps, never a composed read.
        state['reads'][name]={'sha256':digest(raw),'bytes':len(raw),'step_ordinal':len(state['completed'])+1}
        if step=='read-roadmap':
            need(state['reads']['STATE.md']['step_ordinal']<state['reads'][name]['step_ordinal'],'READ_ACTION_ORDER_REFUSED')
            probe['separate_state_roadmap_reads']=True
    elif step=='resume':
        need(set(state['reads'])=={'STATE.md','ROADMAP.md'},'CANONICAL_READS_INCOMPLETE')
        for name,read in state['reads'].items():need(digest(u.checked_file(source/state['run_root']/name,PRIVATE_CANONICAL_BYTES))==read['sha256'],'CANONICAL_READ_BYTES_CHANGED')
        raw=owner('resume-new-session',['--resume-controller',controller,'--boundary','new-session','--epoch','G0001'])
        state['receipt']=token(raw,'refs/implementaudit/continuity-receipts/'+controller+r'/G0001@[0-9a-f]{40}')
        probe['normal_resume_receipt_sha256']=digest(raw)
    elif step=='verify':
        raw=owner('verify-resume',['--verify-resume-receipt',state['receipt']]);need(raw.decode().strip()==state['receipt'],'VERIFIED_RECEIPT_MISMATCH')
        probe['normal_receipt_verified']=True
    elif step=='require':
        probe['initial_currentness_sha256']=current('initial-require-currentness')
    elif step=='pair':
        current('before-pair-currentness');probe['currentness_before_pair']=True;probe['started']=True
        driver=checked_driver(u)
        argv=[tools['python3'],'-I','-S','-B',str(driver),'--source',str(source),'--out',str(private/'full-pair'),
              '--runtime-bin',str(private/'ordinary-venv/bin'),'--capture-plan-profile','single-proc-v2','--execute']
        try:
            rc,out,err=command('complete-current-registry-pair',argv,seconds=BANK_SECONDS)
        except u.Refusal as exc:
            captured=getattr(exc,'captured',None)
            if captured is not None:
                write_private(private/'pair.stdout',captured['stdout']);write_private(private/'pair.stderr',captured['stderr'])
            try:
                probe['result']=read_pair_summary(output,False,u);probe['result_disposition']='VALIDATED_UNRECEIVED'
            except (Refusal,u.Refusal,OSError,ValueError,KeyError,TypeError):pass
            raise
        write_private(private/'pair.stdout',out);write_private(private/'pair.stderr',err)
        probe['result']=read_pair_summary(output,False,u);probe['result_disposition']='VALIDATED_UNRECEIVED'
        current('after-pair-currentness');probe['currentness_after_pair']=True
        need(rc==0 and not err and probe['result']['status']=='COMPLETE_PAIR_RAW_RELATION_RECORDED','FULL_PAIR_INCOMPLETE_OR_FAILED')
    elif step=='receive':
        current('before-receive-currentness')
        driver=checked_driver(u)
        argv=[tools['python3'],'-I','-S','-B',str(driver),'--source',str(source),'--out',str(private/'full-pair'),
              '--runtime-bin',str(private/'ordinary-venv/bin'),'--capture-plan-profile','single-proc-v2','--receive']
        try:
            rc,out,err=command('separate-maintained-sealed-receiving',argv,seconds=RECEIVE_SECONDS)
        except u.Refusal:
            # Even a parse-valid receipt is not accepted after uncertain cleanup.
            try:
                candidate=read_pair_summary(output,True,u)
                probe['unaccepted_receiving_observation']={'bytes':len(canonical(candidate)),'sha256':digest(canonical(candidate)),
                    'receiving_status':candidate['receiving_status'],'scope':'UNACCEPTED_CALLER_CLEANUP_REFUSED'}
            except (Refusal,u.Refusal,OSError,ValueError,KeyError,TypeError):pass
            raise
        write_private(private/'receive.stdout',out);write_private(private/'receive.stderr',err)
        result=read_pair_summary(output,True,u);probe['result']=result
        current('after-receive-currentness')
        probe['receiving']={'status':result['receiving_status'],'authority':'NONE','while_same_checkout_current':True,
           'receipt_transfer_authority':False,'result_sha256':digest(canonical(result)),
           'original_acceptance':False,'full_G2':False,'G1':False,'C5':False,'G3':False,'full_T14':False,
           'eligible_delta':'COMPLETE_OR_ACTUALLY_SEALED_PARTIAL_RAW_OPERATION_ONLY_NO_NORMALIZATION_ADOPTION'}
        probe['result_disposition']=result['receiving_status']
        write_private(private/'live-full-pair-receiving.json',canonical(probe['receiving']))
        need(rc==0 and not err and result['receiving_status']=='RECEIVED_COMPLETE_RAW_PAIR','FULL_PAIR_NOT_COMPLETELY_RECEIVED')

    else:raise Refusal('UNKNOWN_STEP')

def record_failure(state,operation,exc):
    state['failed']=True
    code=str(exc) if type(exc).__name__=='Refusal' and re.fullmatch('[A-Z0-9_]{1,90}',str(exc)) else ('STEP_WATCHDOG_OR_TERMINATION' if isinstance(exc,Deadline) else 'SAFE_EXCEPTION_RECORDED')
    record={'operation':operation,'code':code,'exception_type':type(exc).__name__ if type(exc).__name__ in ('Refusal','Deadline','OSError','ValueError','KeyError','TypeError','AssertionError') else 'OTHER',
            'errno':exc.errno if isinstance(exc,OSError) and type(exc.errno) is int and 0<=exc.errno<=4096 else None}
    state['docs']['FAILURE.json']['present']=True;state['docs']['FAILURE.json']['failures'].append(record)

def execute(mode,source,output,u):
    context=host_context(output,source,mode);state_path=output/'private/episode.json'
    if mode=='provision':
        need(not output.exists(),'NO_RETRY_OUTPUT_EXISTS');output.mkdir(mode=0o700)
        (output/'private').mkdir(mode=0o700);(output/'public').mkdir(mode=0o700)
        state=fresh_state(context,source,output);save_state(state_path,state)
    else:
        need(output.resolve(strict=True)==output,'OUTPUT_DIRECTORY_REFUSED')
        state=u.parse_json(u.checked_file(state_path,1024*1024))
        need(state['schema']=='dg16.linux-native-private-episode.v1' and state['context']==context and
             identities(source)==state['source_directory_identity'] and identities(source/'.git')==state['git_directory_identity'] and
             identities(output)==state['output_directory_identity'],'LIVE_CONTEXT_CHANGED')
    docs=state['docs'];enabled=False;commands=docs['HOST.json']['commands'];stage_success=False
    oldcwd=Path.cwd();os.chdir(source)
    def expired(_a,_b):raise Deadline()
    signal.signal(signal.SIGALRM,expired);signal.signal(signal.SIGTERM,expired)
    budget=FINAL_SECONDS if mode=='finalize' else max(1,min(RUN_SECONDS,int(state['deadline_monotonic']-time.monotonic())))
    signal.alarm(budget)
    deadline=time.monotonic()+FINAL_SECONDS if mode=='finalize' else state['deadline_monotonic']
    def command(label,argv,seconds=90):
        # Labels are fixed by this file; no command line, environment, stdout or stderr becomes public.
        return u.capture(mode+'-'+label,argv,commands,deadline,seconds=seconds)
    try:
        failed_receiving = mode=='receive' and state['docs']['PROBE.json']['started'] and state['docs']['CLEANUP.json']['all_step_children_reaped']
        need(mode=='finalize' or failed_receiving or not state['failed'],'PRIOR_STEP_FAILED')
        if mode!='finalize' and not failed_receiving:need(STEPS[len(state['completed'])]==mode,'STEP_ORDER_REFUSED')
        tools,host=inventory(u)
        prerequisite_host(host,u)
        prior={k:v for k,v in docs['HOST.json'].items() if k not in ('schema','commands')}
        need('boot_identity_sha256' not in docs['HOST.json'] or prior==host,'HOST_TOOLCHAIN_CHANGED')
        docs['HOST.json'].update(host);enable_subreaper();enabled=True
        manifest=read_manifest(u);check_source_git(command,tools,source,mode in ('preflight','pair','receive','finalize'))
        source_fact=verify_source(source,manifest,u,state['run_root'] is not None)
        if state['runtime'] is not None:need(runtime_snapshot(source,state,u)==state['runtime'],'CLAIMED_RUNTIME_CHANGED')
        if mode=='finalize':
            docs['SOURCE.json']['after']=source_fact
            docs['CLEANUP.json']['source_unchanged']=docs['SOURCE.json']['before']==source_fact
            docs['CLEANUP.json']['runtime_unchanged_after_initialization']=state['runtime'] is not None and runtime_snapshot(source,state,u)==state['runtime']
            rc,out,err=command('live-closing-currentness',[tools['bash'],str(source/OWNER),'--require-current-continuity',state['controller']],seconds=20)
            write_private(output/'private/final-currentness.stdout',out);write_private(output/'private/final-currentness.stderr',err)
            need(rc==0 and out.decode().strip()==state['receipt'],'FINAL_CURRENTNESS_REFUSED')
            need(state['completed']==list(STEPS) and not state['failed'],'EPISODE_INCOMPLETE')
            need(docs['PROBE.json']['receiving']['status']=='RECEIVED_COMPLETE_RAW_PAIR','LIVE_RECEIVING_MISSING')
            docs['PROBE.json']['receiving']['closing_currentness_sha256']=digest(out)
            docs['PROBE.json']['receiving']['verified_before_teardown']=True
            stage_success=True
        else:
            operation(mode,state,source,output,tools,u,manifest,command)
            if mode=='provision':docs['HOST.json'].update(inventory(u)[1])
            if mode=='pair':check_source_git(command,tools,source,True)
            verify_source(source,manifest,u,state['run_root'] is not None)
            if state['runtime'] is not None:need(runtime_snapshot(source,state,u)==state['runtime'],'CLAIMED_RUNTIME_CHANGED')
            state['completed'].append(mode)
            docs['PROBE.json']['phases'].append({'name':mode,'status':'COMPLETED','ordinal':len(state['completed'])})
            stage_success=True
    except BaseException as exc:
        record_failure(state,mode,exc)
    finally:
        # This process owns only its own descendants; no name-based or process-group cleanup.
        signal.alarm(10)
        try:
            cleanup=u.stop_owned_children() if enabled else {'echild':not u.children(),'pidfd_signals':0,'reaped_statuses':[]}
            need(cleanup['echild'],'STEP_CHILD_CLEANUP_UNCERTAIN')
        except BaseException as exc:
            docs['CLEANUP.json']['all_step_children_reaped']=False;stage_success=False;record_failure(state,mode+'-cleanup',exc)
        docs['RESULT.json']['elapsed_seconds']=time.monotonic()-state['started_monotonic']
        docs['RESULT.json']['completed_steps']=list(state['completed'])
        if mode=='finalize':
            okay=stage_success and not state['failed'] and docs['CLEANUP.json']['all_step_children_reaped'] and docs['CLEANUP.json']['source_unchanged'] and docs['CLEANUP.json']['runtime_unchanged_after_initialization']
            docs['RESULT.json']['status']='COMPLETE_RAW_PAIR_RECEIVED_NO_FORMAL_ACCEPTANCE' if okay else 'UNQUALIFIED_OR_INCOMPLETE'
            docs['RESULT.json']['custody_evidence_scope']='HISTORICAL_THIS_LIVE_JOB_ONLY; exported hashes convey no currentness'
            save_state(state_path,state);u.write_public(output/'public',docs)
        else:save_state(state_path,state)
        signal.alarm(0);os.chdir(oldcwd)
    print(json.dumps({'step':mode,'status':'COMPLETED' if stage_success and not state['failed'] else 'UNQUALIFIED'},sort_keys=True),flush=True)
    return 0 if stage_success and not state['failed'] else 1

def main():
    p=argparse.ArgumentParser();p.add_argument('--step',choices=(*STEPS,'finalize'));p.add_argument('--emit-public',action='store_true')
    p.add_argument('--source',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    need(bool(a.step)!=bool(a.emit_public),'MODE_REFUSED');u=load_utility()
    source=Path(a.source).absolute();output=Path(a.output).absolute()
    if a.emit_public:
        emit_bound_public(output,source,u);return 0
    return execute(a.step,source,output,u)

if __name__=='__main__':
    try:raise SystemExit(main())
    except (Refusal,OSError,ValueError,KeyError,TypeError):
        print('DG16_LINUX_NATIVE_EPISODE {"status":"UNQUALIFIED","code":"PRE_ENTRY_OR_RETENTION_REFUSED"}',flush=True)
        raise SystemExit(1)
