#!/usr/bin/env python3
"""One unchanged legacy diagnostic; closed causal observations, authority NONE.

Fresh-controller recipe derived from independently reviewed bank03. The retained
pair helpers preserve the original complete plan.v2 single-proc preflight. A
dedicated driver calls legacy once. Private history and raw captures stay private.
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
BRANCH = 'pro/dg16-r5-g2-capture-diagnostic-01-20261106'
SOURCE_COMMIT = '0d57929be5bd15682b4e9da2c0209d5dff307843'
SOURCE_TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
UTILITY_SHA = '429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'
MANIFEST_SHA = 'a9d6b6ab0a4395e331ecba2499779103ff5bf8ac70d0c9a33a0a85b0d77d789e'
PAIR_DRIVER_SHA = '36ede64b6a6796c1e4e33c2ca624797677dd6e0278f0e6a6e2943346e34537f0'
DIAGNOSTICS_SHA = '74cdc1177d50b2435aef282dd21c6af01d52b0251fc19a1eb4b38151d5b6f150'
FULL_RELATION_SHA = 'd42132b0c84e89c7a767cdd3a5e68afe527907094be9756b613eb35db24492dd'
RELATION_INPUTS_SHA = '26248867833c88ba6fadf27c4b223d00012742ba28839da129680f5cd35b0f35'
POLICY_SHA = '01d93c25522bd15aab81ef681e85be396b772f1da310e3203e7a23fb3c78c9b4'
POLICY_CONTROL_SHA = '35f43dbec610532673143e019c0b6e940941d9c67629bbbef29ba30467adb418'
LIVE_CONTROL_SHA = '00b679c73dc522b33f0ec75cc9a4b8596ec6f9262158f0808efd2d6bdd77bf22'
PREREQUISITE_SHA = '254863d44db06228d13374892ee8161c268b283fab039ccfaafc7e66f0279430'
NATIVE_CLOSURE_SHA = '0e1283bdf245f5db09e33e1addc84f9c2cb7174d51e95aa07d123d986639e9a8'
CHECKOUT_PREPARE_SHA = '2bb9e721c167f9c506480b48cbc1b5eea7de977999bba36b319d0276cce4b577'
CAPTURE_EVIDENCE_SHA = '9addf3d28c7fb87c1cb27d6fe2a294033310e9bf43e14f775c5021b3fd2df00c'
CAPTURE_DIAGNOSTIC_SHA = 'da7653c8de5ad4555831a331e4dfbc20b1a248ad316f0c53e1cce5f68dee5666'
OWNER = 'skills/implementaudit/scripts/claim-run.sh'
AUTHOR = 'fixtures/controller-initialization/author_checkpoint.py'
STEPS = ('provision', 'preflight', 'initialize', 'discover', 'invalidate', 'read-state', 'read-roadmap', 'resume', 'verify', 'require', 'native-bank', 'native-receive', 'diagnose', 'diagnostic-receive')
NAMES = ('STATE.md','PROTOCOL.md','ROADMAP.md','THINKING.md','sidecars.md','tools.md','context.md')
PUBLIC_NAMES = ('RESULT.json','HOST.json','SOURCE.json','PROBE.json','CLEANUP.json','FAILURE.json','ARTIFACT_MANIFEST.json')
RUN_SECONDS, BANK_SECONDS, FINAL_SECONDS = 8400, 7200, 180
RECEIVE_SECONDS, SETUP_SECONDS = 300, 600
HOLD_SECONDS = 300
# Match the maintained initialization owner's 1 MiB canonical-file bound.
# The independent private aggregate and public transport bounds stay unchanged.
PRIVATE_CANONICAL_BYTES = 1024 * 1024
PURPOSE = 'Observe the unchanged complete current legacy verifier exactly once under a fresh current hosted controller, retaining bounded closed failed-capture evidence without DAG, comparison, normalization, live hold or original acceptance.'
NEXT_ACTION = 'Receive the durable primary exit and source-bound namespace, test, code and site observations from the actual maintained operation, distinguish every observation timing, then close source, runtime, cleanup and currentness without awarding G2 or Q02.'
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

def load_diagnostics(u):
    path=Path(__file__).with_name('pair_diagnostics.py')
    raw=u.checked_file(path,16384);need(digest(raw)==DIAGNOSTICS_SHA,'DIAGNOSTICS_CODE_CHANGED')
    module=types.ModuleType('sealed_pair_diagnostics');module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module

def load_adapter(name,expected,u,maximum=65536):
    path=Path(__file__).with_name(name);raw=u.checked_file(path,maximum)
    need(digest(raw)==expected,'BOUND_ADAPTER_MEMBER_CHANGED')
    module=types.ModuleType('sealed_'+name.replace('.','_'));module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__);return module

def actual_policy_adoption(u):
    directory=Path(__file__).parent
    policy_raw=u.checked_file(directory/'POLICY.json',65536);need(digest(policy_raw)==POLICY_SHA,'FULL_POLICY_CHANGED')
    policy=u.parse_json(policy_raw)
    need(policy_raw==canonical(policy) and policy['receiver_inputs_sha256']==RELATION_INPUTS_SHA and
         policy['full_receiver_sha256']==FULL_RELATION_SHA,'FULL_POLICY_BINDING')
    gate=load_adapter('policy_control.py',POLICY_CONTROL_SHA,u)
    decisions=directory.parent/'dg16-r5-full-g2-decisions'
    payload={name:u.checked_file(decisions/name,65536) for name in gate.DECISION_FILES}
    bindings={'source_commit':SOURCE_COMMIT,'source_tree':SOURCE_TREE,'policy_sha256':POLICY_SHA,
              'receiver_inputs_sha256':RELATION_INPUTS_SHA,'adapter_sha256':digest(u.checked_file(Path(__file__),131072)),
              'pair_driver_sha256':PAIR_DRIVER_SHA}
    return gate.validate(payload,bindings,policy)

def checked_full_proof(value,u):
    full=load_adapter('full_relation.py',FULL_RELATION_SHA,u)
    return full.validate_public_proof(value,policy_sha=POLICY_SHA,inputs_sha=RELATION_INPUTS_SHA,
                                      source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE)

def causal_observations(output,u):
    diagnostics=load_diagnostics(u); rows=[]
    for role in ('EXECUTE','RECEIVE'):
        path=output/'private/full-pair/evidence'/(role+'_PROGRESS.json')
        if path.exists():
            value=u.parse_json(u.checked_file(path,4096))
            try:diagnostics.validate(value)
            except (AssertionError,ValueError,KeyError,TypeError):raise Refusal('CAUSAL_OBSERVATION_SHAPE')
            need(value['role']==role.lower(),'CAUSAL_OBSERVATION_ROLE')
            rows.append(value)
    return rows

def identities(path):
    p=Path(path); st=p.lstat();need(stat.S_ISDIR(st.st_mode) and not p.is_symlink(),'DIRECTORY_CUSTODY_REFUSED')
    return [st.st_dev,st.st_ino,st.st_uid]

def read_manifest(u):
    raw=u.checked_file(Path(__file__).with_name('SOURCE_MANIFEST.json'),1024*1024)
    need(digest(raw)==MANIFEST_SHA,'SOURCE_MANIFEST_DIGEST_REFUSED'); m=u.parse_json(raw)
    need(set(m)=={'schema','repository','commit','tree','file_count','total_bytes','members'} and
         m['schema']=='dg16.linux-native-source-manifest.v2' and m['repository']==REPOSITORY and
         m['commit']==SOURCE_COMMIT and m['tree']==SOURCE_TREE and m['file_count']==1755 and
         m['total_bytes']==165855954 and len(m['members'])==1755,'SOURCE_MANIFEST_SHAPE_REFUSED')
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
    need(observed==set(manifest) and total==165855954,'SOURCE_POPULATION_REFUSED')
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
    need(output==temp/('dg16-g2-capture-diagnostic-'+run+'-1') and source==workspace/'qualified-source' and
         source.resolve(strict=True)==source,'RESOURCE_SCOPE_REFUSED')
    need(Path(__file__).absolute().parent==workspace/'packet/qualification/dg16-r5-full-g2','PACKET_LOCATION_REFUSED')
    return {'repository':REPOSITORY,'branch':BRANCH,'run_id':run,'run_attempt':1,'workflow_commit':sha}

def checked_driver(u):
    path=Path(__file__).with_name('pair_driver.py')
    need(digest(u.checked_file(path,131072))==PAIR_DRIVER_SHA,'PAIR_DRIVER_DIGEST_REFUSED')
    return path

def prerequisite_host(host,u):
    raw=u.checked_file(Path(__file__).with_name('EARNED_NATIVE_PREREQUISITE_04.json'),16384)
    need(digest(raw)==PREREQUISITE_SHA,'EARNED_PREREQUISITE_DIGEST_REFUSED')
    value=u.parse_json(raw)
    need(value['schema']=='dg16.native-bank-earned-prerequisite.v2' and value['run_id']=='42123891532' and
         value['tests_run']==9 and value['native_receiving']['status']=='RECEIVED_AT_DECLARED_SCOPE' and
         value['selected_source_commit']==SOURCE_COMMIT and value['selected_source_tree']==SOURCE_TREE and
         value['overall_closing_currentness_verified_before_teardown'] is False and
         value['receipt_transfer_authority'] is False and value['new_controller_required'] is True,
         'EARNED_PREREQUISITE_SHAPE_REFUSED')
    need({key:host[key] for key in ('os','architecture','kernel','python_version','tools')}==value['host_prerequisite'],
         'NATIVE_PREREQUISITE_HOST_PROFILE_CHANGED')

def native_closure_applicability(source,u):
    raw=u.checked_file(Path(__file__).with_name('UNCHANGED_BANK_SOURCE_CLOSURE.json'),65536)
    need(digest(raw)==NATIVE_CLOSURE_SHA,'NATIVE_CLOSURE_MANIFEST_CHANGED')
    value=u.parse_json(raw)
    need(value['schema']=='dg16.native-bank-conservative-source-closure.v1' and
         value['selected_source_commit']==SOURCE_COMMIT and value['selected_source_tree']==SOURCE_TREE and
         value['file_count']==89 and value['total_bytes']==3200361,'NATIVE_CLOSURE_SCOPE_REFUSED')
    rows={row['path']:row for row in value['members']}
    need(len(rows)==value['file_count'],'NATIVE_CLOSURE_POPULATION_REFUSED')
    manifest=read_manifest(u)
    rule=value['population_rule']; observed=set(rule['exact_files'])
    for prefix in rule['whole_subtrees']:
        root=source/prefix
        need(root.resolve(strict=True)==root and root.is_dir(),'NATIVE_CLOSURE_DIRECTORY_REFUSED')
        for parent,dirs,files in os.walk(root,followlinks=False):
            here=Path(parent)
            for name in dirs:
                info=(here/name).lstat()
                need(stat.S_ISDIR(info.st_mode) and not (here/name).is_symlink(),
                     'NATIVE_CLOSURE_DIRECTORY_REFUSED')
            observed.update((here/name).relative_to(source).as_posix() for name in files)
    unchanged=observed==set(rows)
    total=0
    for name in sorted(observed):
        need(name in manifest,'NATIVE_CLOSURE_UNREGISTERED_MEMBER')
        current=manifest[name]; info=(source/name).lstat()
        need(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and not info.st_mode&0o6000 and
             bool(info.st_mode&0o111)==(current['mode']=='100755'),'NATIVE_CLOSURE_MEMBER_SHAPE')
        body=u.checked_file(source/name,256*1024**2); total+=len(body)
        need(len(body)==current['bytes'] and digest(body)==current['sha256'],
             'NATIVE_CLOSURE_SELECTED_SOURCE_CHANGED')
        unchanged=unchanged and name in rows and rows[name]==current
    return {'manifest_sha256':NATIVE_CLOSURE_SHA,'exact_directory_population':observed==set(rows),
            'file_count':len(observed),'total_bytes':total,'unchanged_consumed_closure':unchanged}

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
    # Ubuntu's documented sudo-rs alternative resolves here; this is an exact
    # administrative-setup target, never a non-setid native transport admission.
    need(path in (Path('/usr/bin/sudo'),Path('/usr/bin/sudo-rs'),
                  Path('/usr/bin/sudo.ws'),Path('/usr/lib/cargo/bin/sudo')),
         'SETUP_SUDO_TARGET_REFUSED')
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
      'normalization':'RAW_BYTES_WITH_SEPARATE_PROSPECTIVE_FULL_RELATION','finite_normalization_unchanged':True,
      'policy_sha256':POLICY_SHA,'original_acceptance':False,
      'full_G2':False,'C5':False,'G1':False,'G3':False,'full_T14':False,
      'failed_or_unsealed_attempts_are_not_received_as_complete':True,
      'private_raw_captures':'LIVE_JOB_ONLY_RECEIVE_BEFORE_TEARDOWN_NO_CUSTODY_TRANSFER',
      'ordinary_toolchain_scope':'ACTUAL_EXECUTABLE_AND_VENV_BOOKENDS_PARTIAL_NOT_C5',
      'ci_applicability':'CANONICAL_PACKAGE_LEG_ONLY_OTHER_VALIDATE_WORKFLOW_STEPS_UNQUALIFIED'}
    required=set(literals)|{'status','subject_verifier_attempts','receiving_status','records','raw_relation','causal_observations','full_population_normalization_adopted'}
    optional={'mapping','receive_record','same_live_source_current','ordinary_toolchain_unchanged','runtime_report_source','full_correspondence'}
    need(type(value) is dict and required<=set(value)<=required|optional,'PAIR_SUMMARY_KEYS_REFUSED')
    for key,expected in literals.items():need(type(value[key]) is type(expected) and value[key]==expected,'PAIR_SUMMARY_LITERAL_REFUSED')
    need(type(value['full_population_normalization_adopted']) is bool,'PAIR_POLICY_FLAG')
    if 'runtime_report_source' in value:
        row=value['runtime_report_source']
        need(type(row) is dict and set(row)=={'version','bytes','sha256'} and type(row['version']) is str and
             re.fullmatch(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',row['version']) and
             type(row['bytes']) is int and 0<row['bytes']<=131072 and type(row['sha256']) is str and
             re.fullmatch('[0-9a-f]{64}',row['sha256']),'RUNTIME_REPORT_PUBLIC_SHAPE')
    if 'full_correspondence' in value:
        need(value['full_population_normalization_adopted'],'UNADOPTED_FULL_PROOF')
        checked_full_proof(value['full_correspondence'],load_utility())
    need(type(value['causal_observations']) is list and len(value['causal_observations'])<=2,'CAUSAL_OBSERVATION_POPULATION')
    diagnostics=load_diagnostics(load_utility())
    for observation in value['causal_observations']:
        try:diagnostics.validate(observation)
        except (AssertionError,ValueError,KeyError,TypeError):raise Refusal('CAUSAL_OBSERVATION_SHAPE')
    need(value['status'] in ('COMPLETE_PAIR_RAW_RELATION_RECORDED','INCOMPLETE_OR_FAILED_OPERATION') and
         type(value['subject_verifier_attempts']) is int and 0<=value['subject_verifier_attempts']<=2 and
         value['receiving_status'] in ('NOT_RECEIVED','RECEIVED_COMPLETE_RAW_PAIR','RECEIVED_PARTIAL_FAILED_OPERATION','NO_SEALED_CAPTURE_RECEIVED'),
         'PAIR_STATUS_REFUSED')
    count=None
    if 'mapping' in value:
        mapping=value['mapping']
        need(type(mapping) is dict and set(mapping)=={'mapped_nodes','registered_tests','mapping','physical_tests','command_stream','exact_registry_reassembly'} and
             all(type(mapping[k]) is int and 0<=mapping[k]<=4096 for k in ('mapped_nodes','registered_tests')) and
             (mapping['exact_registry_reassembly'] is None or type(mapping['exact_registry_reassembly']) is bool),'PAIR_MAPPING_REFUSED')
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
    preparation=load_adapter('checkout_prepare.py',CHECKOUT_PREPARE_SHA,u)
    preparation.readback(output,probe['checkout_preparation'],u.checked_file)
    need(probe['causal_observations']==causal_observations(output,u),'EMISSION_CAUSAL_OBSERVATION_CHANGED')
    need(probe.get('native_prerequisite')==native_projection(state,output,u,True),'EMISSION_NATIVE_PROJECTION_CHANGED')
    if probe['result'] is not None:
        validate_pair_summary(probe['result'])
        received=probe['result']['receiving_status']!='NOT_RECEIVED'
        need(read_pair_summary(output,received,u)==probe['result'],'EMISSION_OPERATION_CHANGED')
    if 'unaccepted_receiving_observation' in probe:
        candidate=read_pair_summary(output,True,u)
        expected={'bytes':len(canonical(candidate)),'sha256':digest(canonical(candidate)),
                  'receiving_status':candidate['receiving_status'],'scope':'UNACCEPTED_CALLER_CLEANUP_REFUSED'}
        need(expected==probe['unaccepted_receiving_observation'],'EMISSION_UNACCEPTED_OBSERVATION_CHANGED')
    diagnostic_readback_check(state,output,u)
    files={name:u.canonical(state['docs'][name]) for name in PUBLIC_NAMES if name!='ARTIFACT_MANIFEST.json'}
    files['ARTIFACT_MANIFEST.json']=u.canonical({'schema':'dg16.linux-host-artifacts.v1','members':[
        {'name':name,'bytes':len(raw),'sha256':digest(raw)} for name,raw in sorted(files.items())]})
    public=output/'public'
    need(public.resolve(strict=True)==public and {p.name for p in public.iterdir()}==set(PUBLIC_NAMES),'EMISSION_PUBLIC_POPULATION')
    need(all(u.checked_file(public/name,u.FILE_LIMIT)==raw for name,raw in files.items()),'EMISSION_PUBLIC_BYTES_CHANGED')
    check_cumulative_public(state,output,u,files)
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
    # Closed public observation of the actual successfully guarded setup tool.
    # The complete alias/inode chain stays in the existing private record.
    state['docs']['PROBE.json']['administrative_setup']={
        'schema':'dg16.administrative-setup-tool.v1','status':'GUARDED_BEFORE_EXECUTION',
        'canonical':sudo_fact['canonical'],'bytes':sudo_fact['bytes'],
        'sha256':sudo_fact['sha256'],'mode':sudo_fact['mode'],'uid':sudo_fact['uid'],
        'aliases_and_ancestors_sha256':digest(canonical(sudo_fact['aliases_and_ancestors'])),
        'alias_and_ancestor_count':len(sudo_fact['aliases_and_ancestors']),
        'scope':'ADMINISTRATIVE_PACKAGE_SETUP_ONLY_NOT_NATIVE_TRANSPORT'}
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


TESTS = (
 'test_actual_later_invalidation_prevents_return',
 'test_derivative_snapshot_change_after_use_prevents_return',
 'test_native_intake_later_boundary_prevents_return',
 'test_native_intake_rejects_opaque_fixture_work_graph',
 'test_native_intake_rejects_unowned_nested_record',
 'test_native_intake_uses_current_original14_not_retired_root',
 'test_protected_document_change_after_use_prevents_return',
 'test_real_original14_documents_reach_unchanged_graph_parser',
 'test_valid_original14_owner_does_not_supply_missing_graph_document',
)


CHILD = r'''import hashlib,importlib.util,io,json,os,pathlib,sys,traceback,unittest
sys.dont_write_bytecode=True
root=pathlib.Path(sys.argv[1]); path=root/'tests/work-graph-original14-receiving-cases.py'
os.chdir(root)
spec=importlib.util.spec_from_file_location('hosted_original14',path)
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
expected=json.loads(sys.argv[2]); suite=unittest.defaultTestLoader.loadTestsFromTestCase(module.Original14GraphReceiving)
names=[test._testMethodName for test in suite]
if names!=expected:raise RuntimeError('BANK_POPULATION_REFUSED')
class Record(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.rows=[]
    def record(self,test,outcome,err=None):
        row={'test':test._testMethodName,'outcome':outcome,'exception_type':None,
             'diagnostic_bytes':0,'diagnostic_sha256':hashlib.sha256(b'').hexdigest(),'known_codes':[]}
        if err is not None:
            raw=''.join(traceback.format_exception(*err)).encode('utf-8','replace')
            kind=err[0].__name__
            row.update(exception_type=kind if kind in ('AssertionError','RuntimeError','ValueError','OSError',
                       'TimeoutError','WorkGraphError','ContinuityTransportError','FileNotFoundError','PermissionError') else 'OTHER',
                       diagnostic_bytes=len(raw),diagnostic_sha256=hashlib.sha256(raw).hexdigest())
            needles=(('CONTINUITY_TRANSPORT_NAMESPACE_REFUSED',b'CONTINUITY_TRANSPORT_NAMESPACE_REFUSED'),
                     ('CONTINUITY_TRANSPORT_TIMEOUT',b'CONTINUITY_TRANSPORT_TIMEOUT'),
                     ('CANONICAL_WORK_GRAPH',b'canonical WORK_GRAPH'),
                     ('SOURCE_PROFILE_REFUSED',b'SOURCE_REFUSED'),
                     ('NATIVE_CHECKPOINT',b'native checkpoint'),
                     ('NETLINK_ROUTE',b'NETLINK_ROUTE'),
                     ('OS_OPERATION_NOT_PERMITTED',b'Operation not permitted'),
                     ('OS_PERMISSION_DENIED',b'Permission denied'),
                     ('OS_REQUIRED_PATH_UNAVAILABLE',b'No such file or directory'))
            row['known_codes']=[name for name,needle in needles if needle in raw]
        self.rows.append(row)
    def addSuccess(self,test):super().addSuccess(test);self.record(test,'PASS')
    def addFailure(self,test,err):super().addFailure(test,err);self.record(test,'FAIL',err)
    def addError(self,test,err):super().addError(test,err);self.record(test,'ERROR',err)
    def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,'SKIP')
    def addExpectedFailure(self,test,err):super().addExpectedFailure(test,err);self.record(test,'EXPECTED_FAILURE',err)
    def addUnexpectedSuccess(self,test):super().addUnexpectedSuccess(test);self.record(test,'UNEXPECTED_SUCCESS')
stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Record).run(suite)
raw=stream.getvalue().encode('utf-8','replace')
record={'schema':'dg16.linux-native-bank.v1','test_population':names,'tests_run':result.testsRun,
        'success':result.wasSuccessful(),'rows':result.rows,'runner_text_bytes':len(raw),
        'runner_text_sha256':hashlib.sha256(raw).hexdigest()}
print(json.dumps(record,sort_keys=True,separators=(',',':')),flush=True)
raise SystemExit(0 if result.wasSuccessful() else 1)
'''


def validate_bank(v):
    need(type(v) is dict and set(v)=={'schema','test_population','tests_run','success','rows','runner_text_bytes','runner_text_sha256'} and
         v['schema']=='dg16.linux-native-bank.v1' and v['test_population']==list(TESTS) and
         type(v['tests_run']) is int and v['tests_run']==9 and type(v['success']) is bool and
         type(v['rows']) is list and len(v['rows'])==9 and type(v['runner_text_bytes']) is int and v['runner_text_bytes']>=0 and
         re.fullmatch('[0-9a-f]{64}',v['runner_text_sha256']),'BANK_RESULT_SHAPE_REFUSED')
    seen=[]
    for row in v['rows']:
        need(type(row) is dict and set(row)=={'test','outcome','exception_type','diagnostic_bytes','diagnostic_sha256','known_codes'} and
             row['test'] in TESTS and row['outcome'] in ('PASS','FAIL','ERROR','SKIP','EXPECTED_FAILURE','UNEXPECTED_SUCCESS') and
             (row['exception_type'] is None or row['exception_type'] in EXCEPTIONS) and
             type(row['diagnostic_bytes']) is int and row['diagnostic_bytes']>=0 and
             re.fullmatch('[0-9a-f]{64}',row['diagnostic_sha256']) and type(row['known_codes']) is list and
             len(row['known_codes'])==len(set(row['known_codes'])) and all(x in KNOWN_CODES for x in row['known_codes']),'BANK_ROW_REFUSED')
        seen.append(row['test'])
    need(seen==list(TESTS),'BANK_RESULT_POPULATION_REFUSED')
    return v


def retain_bank_capture(probe,private,rc,out,err,complete,u):
    # Preserve exact bounded bytes privately even when caller cleanup refused.
    write_private(private/'bank.stdout',out);write_private(private/'bank.stderr',err)
    probe['capture_observation']={'primary_returncode':rc,'streams_complete':complete,
        'stdout_bytes':len(out),'stdout_sha256':digest(out),'stderr_bytes':len(err),'stderr_sha256':digest(err)}
    probe['result_disposition']='UNRECEIVED_INVALID_OR_INCOMPLETE'
    if not complete or err:return None
    try:result=validate_bank(u.parse_json(out))
    except (Refusal,u.Refusal,ValueError,TypeError,KeyError,UnicodeError):return None
    probe['result']=result
    probe['result_disposition']='VALIDATED_UNRECEIVED'
    return result


NATIVE_BANK_SECONDS = 600
NATIVE_COMMAND_BYTES = 128 * 1024
NATIVE_COMMAND_COUNT = 32
PAIR_RECEIVING_RESERVE = RECEIVE_SECONDS + HOLD_SECONDS + FINAL_SECONDS


def new_native_state():
    return {'requirement':None,'status':'NOT_ASSESSED','started':False,
        'capture_custody_accepted':False,'currentness_before_bank':False,'currentness_after_bank':False,
        'result':None,'result_disposition':'NOT_OBSERVED','receiving':None,
        'eligible_for_full_pair':False,'closing_currentness_verified_before_teardown':False}


def native_requirement(host,u,source):
    raw=u.checked_file(Path(__file__).with_name('EARNED_NATIVE_PREREQUISITE_04.json'),16384)
    need(digest(raw)==PREREQUISITE_SHA,'EARNED_PREREQUISITE_DIGEST_REFUSED')
    earned=u.parse_json(raw)
    # Preserve the old strict matcher as the historical-match predicate. A
    # changed result is a requirement for a new bank, never a qualification.
    matched=True
    try:prerequisite_host(host,u)
    except Refusal as exc:
        if str(exc)!='NATIVE_PREREQUISITE_HOST_PROFILE_CHANGED':raise
        matched=False
    profile={key:host[key] for key in ('os','architecture','kernel','python_version','tools')}
    expected=earned['host_prerequisite']
    fields={key:profile[key]==expected[key] for key in ('os','architecture','kernel','python_version')}
    fields.update({'tools.'+name:profile['tools'][name]==expected['tools'][name]
                   for name in ('bash','bwrap','git','python3')})
    need(matched==all(fields.values()),'NATIVE_PROFILE_COMPARISON_CHANGED')
    source_match=(SOURCE_COMMIT==earned['historical_source_commit'] and
                  SOURCE_TREE==earned['historical_source_tree'])
    closure=native_closure_applicability(source,u)
    return {'schema':'dg16.full-registry-native-requirement.v1','authority':'NONE',
        'historical_run_id':earned['run_id'],'historical_source_commit':earned['historical_source_commit'],
        'historical_source_tree':earned['historical_source_tree'],'selected_source_commit':SOURCE_COMMIT,
        'selected_source_tree':SOURCE_TREE,'source_exact_match':source_match,'host_exact_match':matched,
        'host_field_matches':fields,'observed_native_profile_sha256':digest(canonical(profile)),
        'historical_native_profile_sha256':digest(canonical(expected)),
        'source_dependency_applicability':closure,
        'historical_overall_closing_currentness':False,
        'requires_fresh_bank':not (matched and closure['unchanged_consumed_closure']),
        'historical_receipt_transfer':False}


def observe_host(state,host,u):
    # Preserve the actual returned facts before either drift or historical
    # prerequisite decisions. The private opening binding is never overwritten.
    prior=state['bound_host']
    state['docs']['HOST.json'].update(host)
    state['docs']['HOST.json']['latest_observed_host_sha256']=digest(canonical(host))
    if prior is None:
        state['bound_host']=u.parse_json(canonical(host))
    state['docs']['HOST.json']['opening_host_sha256']=digest(canonical(state['bound_host']))
    need(prior is None or prior==host,'HOST_TOOLCHAIN_CHANGED')
    requirement=native_requirement(host,u,Path(state['source_path']))
    native=state['native']
    if native['requirement'] is None:
        native['requirement']=requirement
        native['status']='FRESH_NINE_BANK_REQUIRED' if requirement['requires_fresh_bank'] else 'UNCHANGED_BANK_DEPENDENCIES_AND_HOST'
    else:need(native['requirement']==requirement,'NATIVE_REQUIREMENT_CHANGED')


def native_commands_summary(state):
    rows=state['native_commands'];raw=canonical(rows)
    need(type(rows) is list and len(rows)<=NATIVE_COMMAND_COUNT and len(raw)<=NATIVE_COMMAND_BYTES,
         'NATIVE_COMMAND_RECORD_BOUND')
    return {'count':len(rows),'bytes':len(raw),'sha256':digest(raw),
        'all_recorded_cleanup_echild':all(type(row) is dict and type(row.get('cleanup')) is dict
            and row['cleanup'].get('echild') is True for row in rows),
        'scope':'EXACT_COMMAND_RECORDS_RETAINED_JOB_PRIVATE'}


def native_receipt(native,currentness_sha256):
    requirement=native['requirement']
    required=requirement['requires_fresh_bank']
    result=native['result']
    qualified=not required or (native['capture_custody_accepted'] and
        native.get('capture_observation',{}).get('primary_returncode')==0 and
        native.get('capture_observation',{}).get('streams_complete') is True and
        native.get('capture_observation',{}).get('stderr_bytes')==0 and
        result is not None and result['success'] and all(row['outcome']=='PASS' for row in result['rows']) and
        native['currentness_before_bank'] and native['currentness_after_bank'])
    status=('RECEIVED_HISTORICAL_BANK_APPLICABILITY' if not required else
            'RECEIVED_AT_DECLARED_SCOPE' if qualified else 'RECEIVED_FAILED_BANK_AT_DECLARED_SCOPE')
    return {'schema':'dg16.full-registry-native-receiving.v1','status':status,'authority':'NONE',
        'receipt_transfer_authority':False,'while_same_checkout_current':True,
        'source_commit':SOURCE_COMMIT,'source_tree':SOURCE_TREE,
        'requirement_sha256':digest(canonical(requirement)),
        'bank_result_sha256':digest(canonical(result)) if result is not None else None,
        'currentness_sha256':currentness_sha256,'eligible_for_full_pair':qualified,
        'eligible_delta':'EXACT_NATIVE_PREREQUISITE_ONLY_NO_ORIGINAL_AWARD',
        'original_acceptance':False,'G1':False,'C5':False,'full_G2':False,'G3':False,'full_T14':False}


def native_projection(state,output,u,verify_private=False):
    native=state['native']
    base=set(new_native_state())
    need(type(native) is dict and base<=set(native)<=base|{'capture_observation'},'NATIVE_STATE_KEYS_REFUSED')
    need(native['status'] in ('NOT_ASSESSED','FRESH_NINE_BANK_REQUIRED','UNCHANGED_BANK_DEPENDENCIES_AND_HOST',
        'BANK_STARTED','BANK_PASSED_UNRECEIVED','BANK_FAILED_UNRECEIVED','RECEIVED_AT_DECLARED_SCOPE',
        'RECEIVED_FAILED_BANK_AT_DECLARED_SCOPE','RECEIVED_HISTORICAL_BANK_APPLICABILITY'), 'NATIVE_STATUS_REFUSED')
    for name in ('started','capture_custody_accepted','currentness_before_bank','currentness_after_bank',
                 'eligible_for_full_pair','closing_currentness_verified_before_teardown'):
        need(type(native[name]) is bool,'NATIVE_BOOLEAN_REFUSED')
    need(native['result_disposition'] in ('NOT_OBSERVED','UNRECEIVED_INVALID_OR_INCOMPLETE',
        'VALIDATED_UNRECEIVED','RECEIVED_AT_DECLARED_SCOPE','RECEIVED_FAILED_BANK_AT_DECLARED_SCOPE',
        'RECEIVED_HISTORICAL_BANK_APPLICABILITY'),'NATIVE_DISPOSITION_REFUSED')
    requirement=native['requirement']
    if requirement is not None:
        need(state['bound_host'] is not None and requirement==native_requirement(state['bound_host'],u,Path(state['source_path'])),
             'NATIVE_REQUIREMENT_READBACK_CHANGED')
    result=validate_bank(native['result']) if native['result'] is not None else None
    capture=native.get('capture_observation')
    if capture is not None:
        need(type(capture) is dict and set(capture)=={'primary_returncode','streams_complete',
            'stdout_bytes','stdout_sha256','stderr_bytes','stderr_sha256'} and
            (capture['primary_returncode'] is None or type(capture['primary_returncode']) is int) and
            type(capture['streams_complete']) is bool,'NATIVE_CAPTURE_SHAPE_REFUSED')
        for stream in ('stdout','stderr'):
            need(type(capture[stream+'_bytes']) is int and 0<=capture[stream+'_bytes']<=32768 and
                 type(capture[stream+'_sha256']) is str and re.fullmatch('[0-9a-f]{64}',capture[stream+'_sha256']),
                 'NATIVE_CAPTURE_BOUND')
        if verify_private:
            observed={name:u.checked_file(output/'private'/('bank.'+name),32768) for name in ('stdout','stderr')}
            for name,raw in observed.items():
                need(len(raw)==capture[name+'_bytes'] and digest(raw)==capture[name+'_sha256'],'NATIVE_CAPTURE_READBACK_CHANGED')
            if result is not None:
                need(capture['streams_complete'] and not observed['stderr'] and
                     validate_bank(u.parse_json(observed['stdout']))==result,'NATIVE_RESULT_READBACK_CHANGED')
    else:need(result is None and not native['capture_custody_accepted'],'NATIVE_CAPTURE_MISSING')
    receipt=native['receiving']
    if receipt is not None:
        need(requirement is not None and type(receipt) is dict and
             type(receipt.get('currentness_sha256')) is str and re.fullmatch('[0-9a-f]{64}',receipt['currentness_sha256']),
             'NATIVE_RECEIPT_SHAPE_REFUSED')
        need(receipt==native_receipt(native,receipt['currentness_sha256']),'NATIVE_RECEIPT_SCOPE_CHANGED')
        if verify_private:
            raw=u.checked_file(output/'private/live-bank-receiving.json',16384)
            need(u.parse_json(raw)==receipt,'NATIVE_RECEIPT_READBACK_CHANGED')
            current=u.checked_file(output/'private/native-receiving-currentness.stdout',512)
            need(digest(current)==receipt['currentness_sha256'],'NATIVE_RECEIPT_CURRENTNESS_BYTES_CHANGED')
    need(native['eligible_for_full_pair']==(receipt is not None and receipt['eligible_for_full_pair'] is True),
         'NATIVE_ELIGIBILITY_CHANGED')
    return {'schema':'dg16.full-registry-native-prerequisite.v1','authority':'NONE',
        'bank':'tests/work-graph-original14-receiving-cases.py','expected_tests':list(TESTS),
        'status':native['status'],'requirement':requirement,'started':native['started'],
        'capture_custody_accepted':native['capture_custody_accepted'],'capture_observation':capture,
        'result':result,'result_disposition':native['result_disposition'],'receiving':receipt,
        'currentness_before_bank':native['currentness_before_bank'],'currentness_after_bank':native['currentness_after_bank'],
        'qualified_for_pair_at_receiving':native['eligible_for_full_pair'],
        'closing_currentness_verified_before_teardown':native['closing_currentness_verified_before_teardown'],
        'bank_watchdog_seconds':NATIVE_BANK_SECONDS,'elapsed_subtraction':0,
        'command_records':native_commands_summary(state),'original_acceptance':False,'full_G2':False,'C5':False,'G1':False}


def require_native_for_pair(state,output,u):
    value=native_projection(state,output,u,True)
    need(value['qualified_for_pair_at_receiving'] and state['docs']['CLEANUP.json']['all_step_children_reaped'],
         'CURRENT_NATIVE_PREREQUISITE_NOT_RECEIVED')
    need(state['deadline_monotonic']-time.monotonic()>=BANK_SECONDS+PAIR_RECEIVING_RESERVE,
         'FULL_PAIR_RECEIVING_BUDGET_UNAVAILABLE')


def native_operation(step,state,source,output,tools,u,command,current):
    native=state['native'];private=output/'private'
    need(native['requirement'] is not None,'NATIVE_REQUIREMENT_MISSING')
    if step=='native-bank':
        need(not native['started'] and native['receiving'] is None,'NATIVE_NO_REPEAT')
        current('native-before-bank-currentness');native['currentness_before_bank']=True
        if not native['requirement']['requires_fresh_bank']:
            native['status']='UNCHANGED_BANK_DEPENDENCIES_AND_HOST'
            return
        native['started']=True;native['status']='BANK_STARTED'
        try:
            rc,out,err=command('unchanged-nine-case-bank',[tools['python3'],'-I','-S','-B','-c',CHILD,
                str(source),json.dumps(list(TESTS),separators=(',',':'))],seconds=NATIVE_BANK_SECONDS)
        except u.Refusal as exc:
            captured=getattr(exc,'captured',None)
            if captured is not None:
                retain_bank_capture(native,private,captured['returncode'],captured['stdout'],
                    captured['stderr'],captured['streams_complete'],u)
            native['status']='BANK_FAILED_UNRECEIVED'
            raise
        native['capture_custody_accepted']=True
        result=retain_bank_capture(native,private,rc,out,err,True,u)
        native['status']='BANK_FAILED_UNRECEIVED'
        need(not err,'BANK_STDERR_REFUSED');need(result is not None,'BANK_RESULT_SHAPE_REFUSED')
        need(rc==0 and result['success'] and all(row['outcome']=='PASS' for row in result['rows']),'BANK_NOT_ALL_PASS')
        current('native-after-bank-currentness');native['currentness_after_bank']=True
        native['status']='BANK_PASSED_UNRECEIVED'
    elif step=='native-receive':
        need(native['receiving'] is None,'NATIVE_NO_REPEAT_RECEIVING')
        if native['requirement']['requires_fresh_bank']:
            need(native['started'] and native['capture_custody_accepted'] and native['result'] is not None,
                 'NATIVE_CAPTURE_CUSTODY_NOT_ELIGIBLE')
        native_projection(state,output,u,True)
        currentness=current('native-receiving-currentness')
        receipt=native_receipt(native,currentness)
        write_private(private/'live-bank-receiving.json',canonical(receipt))
        native['receiving']=receipt;native['status']=receipt['status']
        native['eligible_for_full_pair']=receipt['eligible_for_full_pair']
        native['result_disposition']=receipt['status']
        need(native['eligible_for_full_pair'],'NATIVE_BANK_NOT_QUALIFIED')
    else:raise Refusal('UNKNOWN_NATIVE_STEP')


def fresh_state(context,source,output):
    start=time.monotonic()
    return {'schema':'dg16.linux-native-private-episode.v1','context':context,
       'source_path':str(source),
       'controller':'r5-g2-capture-diagnostic-'+context['run_id']+'-a1','run_root':None,'receipt':None,
       'completed':[],'failed':False,'diagnostic_reserved':False,'diagnostic_receiving_reserved':False,'started_monotonic':start,'deadline_monotonic':start+RUN_SECONDS,
       'source_directory_identity':identities(source),'git_directory_identity':identities(source/'.git'),
       'output_directory_identity':identities(output),'runtime':None,'reads':{},
       'bound_host':None,'native':new_native_state(),'native_commands':[],
       'docs':{
        'RESULT.json':dict(context,schema='dg16.g2-failed-capture-episode-result.v1',status='UNQUALIFIED',
          scope='ONE_UNCHANGED_LEGACY_DIAGNOSTIC_WITH_CLOSED_CAUSAL_EVIDENCE',
          G1=False,C5=False,full_G2=False,Q02=False,G3=False,full_T14=False,original_acceptance=False,audit_closure=False,
          independent_assessment=False,automatic_retry=False,adapter_sha256=digest(Path(__file__).read_bytes()),
          utility_sha256=UTILITY_SHA,pair_driver_sha256=PAIR_DRIVER_SHA,capture_evidence_sha256=CAPTURE_EVIDENCE_SHA,capture_diagnostic_sha256=CAPTURE_DIAGNOSTIC_SHA,source_manifest_sha256=MANIFEST_SHA,
          policy_sha256=POLICY_SHA,receiver_inputs_sha256=RELATION_INPUTS_SHA),
        'HOST.json':{'schema':'dg16.full-registry-episode-host.v1','tools':{},'commands':[]},
        'SOURCE.json':{'schema':'dg16.full-registry-episode-source.v1','commit':SOURCE_COMMIT,'tree':SOURCE_TREE,
                       'before':None,'after':None,'tracked_source_mutations':False},
        'PROBE.json':{'schema':'dg16.g2-failed-capture-episode-operation.v1','started':False,'result':None,
           'causal_observations':[],'failed_capture_diagnostic':None,'diagnostic_route':None,
           'diagnostic_receiving':None,'diagnostic_capture_custody_established':False,'diagnostic_readback_refused':False,
           'diagnostic_public_budget':None,
           'diagnostic_currentness':dict.fromkeys(('before_operation','after_operation','before_readback','after_readback','closing')),
           'diagnostic_scope':'UNSEALED_DATA_IS_NOT_ORIGINAL_CAPTURE_RECEIVING',
           'result_disposition':'NOT_OBSERVED','phases':[],'fresh_controller':False,
           'separate_state_roadmap_reads':False,'currentness_before_pair':False,
           'receiving':{'status':'NOT_RECEIVED','authority':'NONE','receipt_transfer_authority':False},
           'episode_watchdog_seconds':RUN_SECONDS,'pair_watchdog_seconds':BANK_SECONDS,
           'receiving_watchdog_seconds':RECEIVE_SECONDS,'setup_watchdog_seconds':SETUP_SECONDS,
           'live_review_watchdog_seconds':HOLD_SECONDS,
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
        state['policy_adoption']=actual_policy_adoption(u)
        docs['PROBE.json']['policy_adoption']=state['policy_adoption']
        provision(state,source,output,tools,u,command)
    elif step=='preflight':
        docs['SOURCE.json']['before']=verify_source(source,manifest,u,False)
        rc,out,err=command('no-imported-controller-refs',[tools['git'],'for-each-ref','--format=%(refname)','refs/implementaudit'])
        need(rc==0 and not out and not err,'PREEXISTING_CONTROLLER_REFS_REFUSED')
    elif step=='initialize':
        raw=owner('fresh-claim',['--controller',controller,'r5-g2-capture-diagnostic'])
        run=token(raw,r'\.IMPLEMENTAUDIT/runs/r5-g2-capture-diagnostic-[A-Za-z0-9]{6}');state['run_root']=run
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
    elif step in ('native-bank','native-receive'):
        native_operation(step,state,source,output,tools,u,command,current)
    elif step in ('diagnose','diagnostic-receive'):
        diagnostic_operation(step,state,source,output,tools,u,command,current)
    else:raise Refusal('UNKNOWN_STEP')

def check_review_public(state,output,u):
    root=output/'review';need(root.resolve(strict=True)==root,'REVIEW_DIRECTORY_CHANGED')
    expected=state['review_files']
    need(set(expected)=={'REQUEST.json','PROOF.json',*('public/'+name for name in PUBLIC_NAMES)} and
         {p.name for p in root.iterdir()}=={'REQUEST.json','PROOF.json','public'} and
         {p.name for p in (root/'public').iterdir()}==set(PUBLIC_NAMES),'REVIEW_PUBLIC_POPULATION')
    files={}
    for name,row in expected.items():
        raw=u.checked_file(root/name,4096 if name=='REQUEST.json' else 16384 if name=='PROOF.json' else u.FILE_LIMIT)
        need({'bytes':len(raw),'sha256':digest(raw)}==row,'REVIEW_PUBLIC_BYTES_CHANGED');files[name]=raw
    need(sum(map(len,files.values()))<=u.TOTAL_LIMIT,'REVIEW_PUBLIC_AGGREGATE_BOUND')
    checked_full_proof(u.parse_json(files['PROOF.json']),u)
    u.transport_lines({name:files['public/'+name] for name in PUBLIC_NAMES})
    need(digest(files['REQUEST.json'])==state['review_request_sha256'],'REVIEW_REQUEST_CHANGED')
    return files['REQUEST.json']

def check_cumulative_public(state,output,u,files=None):
    """The original aggregate ceiling covers both exported JSON populations."""
    if files is None:
        files={name:u.canonical(state['docs'][name]) for name in PUBLIC_NAMES if name!='ARTIFACT_MANIFEST.json'}
        files['ARTIFACT_MANIFEST.json']=u.canonical({'schema':'dg16.linux-host-artifacts.v1','members':[
            {'name':name,'bytes':len(raw),'sha256':digest(raw)} for name,raw in sorted(files.items())]})
    u.transport_lines(files)
    previous=0
    if state.get('review_files'):
        check_review_public(state,output,u)
        previous=sum(row['bytes'] for row in state['review_files'].values())
    current=sum(map(len,files.values()))
    need(previous+current<=u.TOTAL_LIMIT,'EPISODE_PUBLIC_AGGREGATE_BOUND')
    return {'review_payload_bytes':previous,'final_payload_bytes':current,'total_bytes':previous+current,
            'maximum_bytes':u.TOTAL_LIMIT}


def closing_control_readback(state,output,u):
    request_raw=check_review_public(state,output,u)
    work=output/'private/live-review'
    control=load_adapter('live_control.py',LIVE_CONTROL_SHA,u)
    reserved=u.parse_json(u.checked_file(work/'CONSUMPTION_RESERVED.json',4096))
    need(reserved==state['live_consumption'] and type(reserved.get('accepted_utc_epoch')) is int,
         'CONSUMPTION_RESERVATION_CHANGED')
    payload={name:u.checked_file(work/name,4096) for name in control.NAMES}
    received=control.validate(payload,request_raw,now=reserved['accepted_utc_epoch'])
    need(all(reserved[key]==value for key,value in received.items()),'CLOSING_CONTROL_DATA_CHANGED')
    return reserved

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
    docs=state['docs'];enabled=False;stage_success=False
    preparation=load_adapter('checkout_prepare.py',CHECKOUT_PREPARE_SHA,u)
    if mode=='provision':docs['PROBE.json']['checkout_preparation']=preparation.initial_record()
    commands=state['native_commands'] if mode in ('native-bank','native-receive') else docs['HOST.json']['commands']
    oldcwd=Path.cwd();os.chdir(source)
    def expired(_a,_b):raise Deadline()
    signal.signal(signal.SIGALRM,expired);signal.signal(signal.SIGTERM,expired)
    remaining=state['deadline_monotonic']-time.monotonic()
    budget=max(1,min(FINAL_SECONDS if mode=='finalize' else RUN_SECONDS,int(remaining)))
    signal.alarm(budget)
    deadline=min(time.monotonic()+FINAL_SECONDS,state['deadline_monotonic']) if mode=='finalize' else state['deadline_monotonic']
    def command(label,argv,seconds=90):
        # Labels are fixed by this file; no command line, environment, stdout or stderr becomes public.
        return u.capture(mode+'-'+label,argv,commands,deadline,seconds=seconds)
    try:
        need(time.monotonic()<state['deadline_monotonic'],'EPISODE_ORCHESTRATION_EXPIRED')
        diagnostic_prior_custody(state,mode)
        failed_receiving = mode=='diagnostic-receive' and state['docs']['PROBE.json']['started'] and state['docs']['CLEANUP.json']['all_step_children_reaped']
        failed_native_receiving = (mode=='native-receive' and state['native']['started'] and
            state['native']['capture_custody_accepted'] and state['native']['result'] is not None and
            state['docs']['CLEANUP.json']['all_step_children_reaped'])
        failed_receiving = failed_receiving or failed_native_receiving
        need(mode=='finalize' or failed_receiving or not state['failed'],'PRIOR_STEP_FAILED')
        if mode!='finalize' and not failed_receiving:need(STEPS[len(state['completed'])]==mode,'STEP_ORDER_REFUSED')
        tools,host=inventory(u)
        observe_host(state,host,u)
        enable_subreaper();enabled=True
        manifest=read_manifest(u)
        if mode=='provision':
            need(state['completed']==[] and state['run_root'] is None and state['receipt'] is None,'CHECKOUT_PREPARATION_AFTER_CUSTODY_REFUSED')
            actual_policy_adoption(u)
            verify_source(source,manifest,u,False)
            preparation.prepare(source,output,docs['PROBE.json']['checkout_preparation'],u.checked_file,write_private)
        check_source_git(command,tools,source,mode in ('preflight','native-bank','native-receive','diagnose','diagnostic-receive','finalize'))
        source_fact=verify_source(source,manifest,u,state['run_root'] is not None)
        if state['runtime'] is not None:need(runtime_snapshot(source,state,u)==state['runtime'],'CLAIMED_RUNTIME_CHANGED')
        if mode=='finalize':
            stage_success=finalize_diagnostic(state,source,output,tools,u,command,source_fact)
        else:
            operation(mode,state,source,output,tools,u,manifest,command)
            if mode=='provision':observe_host(state,inventory(u)[1],u)
            if mode in ('native-bank','diagnose'):check_source_git(command,tools,source,True)
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
        try:
            docs['PROBE.json']['failed_capture_diagnostic']=read_diagnostic_projection(output,u)
            docs['PROBE.json']['diagnostic_route']=read_diagnostic_route(output,u)
        except (Refusal,OSError,ValueError,KeyError,TypeError):
            docs['PROBE.json']['diagnostic_readback_refused']=True
            stage_success=False;record_failure(state,mode,Refusal('DIAGNOSTIC_RETENTION_READBACK_REFUSED'))
        try:docs['PROBE.json']['causal_observations']=causal_observations(output,u)
        except (Refusal,OSError,ValueError,KeyError,TypeError):
            stage_success=False;record_failure(state,mode,Refusal('CAUSAL_OBSERVATION_READBACK_REFUSED'))
        try:
            docs['PROBE.json']['native_prerequisite']=native_projection(state,output,u)
        except BaseException as exc:
            docs['PROBE.json']['native_prerequisite']=None
            stage_success=False;record_failure(state,mode+'-native-projection',exc)
        docs['RESULT.json']['elapsed_seconds']=time.monotonic()-state['started_monotonic']
        docs['RESULT.json']['completed_steps']=list(state['completed'])
        if mode=='finalize':
            if time.monotonic()>=state['deadline_monotonic']:
                stage_success=False;record_failure(state,mode,Refusal('EPISODE_ORCHESTRATION_EXPIRED'))
            okay=stage_success and not state['failed'] and docs['CLEANUP.json']['all_step_children_reaped'] and docs['CLEANUP.json']['source_unchanged'] and docs['CLEANUP.json']['runtime_unchanged_after_initialization']
            docs['RESULT.json']['status']='CLOSED_LEGACY_DIAGNOSTIC_RETAINED_NO_ORIGINAL_ACCEPTANCE' if okay else 'UNQUALIFIED_OR_INCOMPLETE'
            docs['RESULT.json']['custody_evidence_scope']='HISTORICAL_THIS_LIVE_JOB_ONLY; exported hashes convey no currentness'
            save_state(state_path,state)
            preparation.readback(output,docs['PROBE.json']['checkout_preparation'],u.checked_file)
            check_cumulative_public(state,output,u)
            u.write_public(output/'public',docs)
        else:save_state(state_path,state)
        signal.alarm(0);os.chdir(oldcwd)
    print(json.dumps({'step':mode,'status':'COMPLETED' if stage_success and not state['failed'] else 'UNQUALIFIED'},sort_keys=True),flush=True)
    return 0 if stage_success and not state['failed'] else 1

def main():
    p=argparse.ArgumentParser();p.add_argument('--step',choices=(*STEPS,'finalize'));p.add_argument('--emit-public',action='store_true')
    p.add_argument('--source',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    need(sum((bool(a.step),bool(a.emit_public)))==1,'MODE_REFUSED');u=load_utility()
    source=Path(a.source).absolute();output=Path(a.output).absolute()
    if a.emit_public:
        emit_bound_public(output,source,u);return 0
    return execute(a.step,source,output,u)

def capture_evidence_module(u):
    return load_adapter('capture_evidence.py',CAPTURE_EVIDENCE_SHA,u)


def read_diagnostic_projection(output,u):
    evidence=output/'private/full-pair/evidence'
    if not os.path.lexists(evidence/'DIAGNOSTIC.json'):return None
    module=capture_evidence_module(u)
    return module.readback(evidence,module.load_catalog())


def read_diagnostic_route(output,u):
    path=output/'private/full-pair/evidence/DIAGNOSTIC_ROUTE.json'
    if not os.path.lexists(path):return None
    module=capture_evidence_module(u);raw=u.checked_file(path,8192)
    value=module.validate_route(module.strict(raw))
    need(module.canonical(value)==raw,'DIAGNOSTIC_ROUTE_CANONICAL')
    return value


def diagnostic_child_custody(records,index):
    rows=records[index:]
    return (len(rows)==1 and rows[0].get('process_started') is True and rows[0].get('pidfd_acquired') is True
            and rows[0].get('internal_failure') is None and type(rows[0].get('cleanup')) is dict
            and rows[0]['cleanup'].get('echild') is True)


def diagnostic_prior_custody(state,mode):
    if mode in ('diagnostic-receive','finalize'):
        need(state['docs']['CLEANUP.json']['all_step_children_reaped'] and (not state['diagnostic_reserved']
             or state['docs']['PROBE.json']['diagnostic_capture_custody_established']), 'DIAGNOSTIC_PRIOR_CHILD_CUSTODY')


def diagnostic_public_budget(state,u):
    """Reserve all remaining public bytes before consuming the sole owner call.

    Existing public/encoded ceilings are unchanged. The source-bound future
    envelopes include JSON newlines, nesting, failure metadata and manifest.
    A refusal consumes no legacy operation and does not predict its outcome.
    """
    need((u.FILE_LIMIT,u.TOTAL_LIMIT,u.LINE_LIMIT,u.LOG_LIMIT)==(65536,262144,262144,1048576),
         'DIAGNOSTIC_INHERITED_PUBLIC_LIMITS')
    docs=state['docs'];names=set(PUBLIC_NAMES)-{'ARTIFACT_MANIFEST.json'}
    need(set(docs)==names,'DIAGNOSTIC_PRECALL_PUBLIC_POPULATION')
    base={name:len(canonical(docs[name])) for name in names}
    need(base['PROBE.json']<=16384,'DIAGNOSTIC_PRECALL_PROBE_BOUND')
    # Projection 28672 + 2*1024 nested-line bytes; route and receiving
    # 2048 + 2*96 each; causal 4608; phases/currentness 512 each;
    # this reservation record 1536. Every allocation includes its newline.
    future={'PROBE.json':42368,'HOST.json':14*2304,'RESULT.json':2048,
            'SOURCE.json':512,'CLEANUP.json':512,'FAILURE.json':12288}
    maximum={name:base[name]+future[name] for name in names}
    maximum['ARTIFACT_MANIFEST.json']=2048
    reserve=2000
    need(all(size<=u.FILE_LIMIT-reserve for size in maximum.values())
         and sum(maximum.values())<=u.TOTAL_LIMIT-reserve,'DIAGNOSTIC_PUBLIC_CAPACITY_UNAVAILABLE')
    # Every byte is canonical ASCII JSON. Quoting can at most double it;
    # 256 bytes covers the fixed transport envelope, hashes and CRLF.
    encoded={name:2*size+256 for name,size in maximum.items()}
    need(max(encoded.values())<=u.LINE_LIMIT-reserve and sum(encoded.values())<=u.LOG_LIMIT-reserve,
         'DIAGNOSTIC_ENCODED_CAPACITY_UNAVAILABLE')
    record={'schema':'dg16.g2-diagnostic-precall-public-capacity.v1','authority':'NONE',
        'scope':'CAPACITY_RESERVATION_NOT_OPERATION_EVIDENCE','base_bytes':base,'maximum_bytes':maximum,
        'reserved_headroom':reserve,'remaining_host_commands':14,'nested_command_record_bound':2304,
        'raw_aggregate_upper':sum(maximum.values()),'encoded_line_upper':max(encoded.values()),
        'encoded_aggregate_upper':sum(encoded.values()),'original_acceptance':False}
    raw=canonical(record)
    need(len(raw)<=1280 and raw.count(b'\n')<=128,'DIAGNOSTIC_CAPACITY_RECORD_BOUND')
    return record


def diagnostic_operation(step,state,source,output,tools,u,command,current):
    probe=state['docs']['PROBE.json'];private=output/'private'
    need(actual_policy_adoption(u)==state['policy_adoption'],'DIAGNOSTIC_POLICY_INPUT_CHANGED')
    if step=='diagnose':
        probe['diagnostic_currentness']['before_operation']=current('before-diagnostic-currentness')
        require_native_for_pair(state,output,u)
        need(state['diagnostic_reserved'] is False,'DIAGNOSTIC_CALL_ALREADY_RESERVED')
        path=Path(__file__).with_name('capture_diagnostic.py')
        need(digest(u.checked_file(path,65536))==CAPTURE_DIAGNOSTIC_SHA,'DIAGNOSTIC_DRIVER_PIN')
        probe['diagnostic_public_budget']=diagnostic_public_budget(state,u)
        state['diagnostic_reserved']=True;probe['started']=True
        save_state(private/'episode.json',state)
        argv=[tools['python3'],'-I','-S','-B',str(path),'--source',str(source),'--out',str(private/'full-pair'),
              '--runtime-bin',str(private/'ordinary-venv/bin'),'--capture-plan-profile','single-proc-v2','--diagnose']
        index=len(state['docs']['HOST.json']['commands']);error=None;rc=None;out=err=b''
        try:rc,out,err=command('one-maintained-legacy-diagnostic',argv,seconds=BANK_SECONDS)
        except BaseException as exc:
            error=exc;captured=getattr(exc,'captured',{})
            rc=captured.get('returncode');out=captured.get('stdout',b'');err=captured.get('stderr',b'')
        finally:
            write_private(private/'diagnostic.stdout',out);write_private(private/'diagnostic.stderr',err)
            probe['diagnostic_capture_custody_established']=diagnostic_child_custody(state['docs']['HOST.json']['commands'],index)
            try:
                probe['failed_capture_diagnostic']=read_diagnostic_projection(output,u)
                probe['diagnostic_route']=read_diagnostic_route(output,u)
            except (Refusal,u.Refusal,OSError,ValueError,KeyError,TypeError):probe['diagnostic_readback_refused']=True
            save_state(private/'episode.json',state)
        # No subsequent owner command follows an unestablished child cleanup.
        need(probe['diagnostic_capture_custody_established'],'DIAGNOSTIC_CALLER_CUSTODY_UNESTABLISHED')
        probe['diagnostic_currentness']['after_operation']=current('after-diagnostic-currentness')
        if error is not None:raise error
        need(rc==0 and not err and probe['failed_capture_diagnostic'] is not None
             and probe['failed_capture_diagnostic']['diagnostic_complete'] and probe['diagnostic_route'] is not None,
             'DIAGNOSTIC_OBSERVATION_INCOMPLETE')
    elif step=='diagnostic-receive':
        need(state['diagnostic_reserved'] and state['diagnostic_receiving_reserved'] is False,'DIAGNOSTIC_RECEIVING_RESERVATION')
        need(probe['diagnostic_capture_custody_established'],'DIAGNOSTIC_RECEIVING_CALLER_CUSTODY')
        state['diagnostic_receiving_reserved']=True;save_state(private/'episode.json',state)
        before=current('before-diagnostic-readback-currentness')
        projection=read_diagnostic_projection(output,u);route=read_diagnostic_route(output,u)
        need(projection is not None and projection==probe['failed_capture_diagnostic'] and route==probe['diagnostic_route'],
             'DIAGNOSTIC_PRIVATE_READBACK_CHANGED')
        after=current('after-diagnostic-readback-currentness')
        received={'schema':'dg16.g2-diagnostic-data-readback.v1','authority':'NONE','status':'CLOSED_DIAGNOSTIC_READ_BACK',
                  'scope':'UNSEALED_DIAGNOSTIC_DATA_ONLY_NOT_ORIGINAL_CAPTURE_RECEIVING','projection':{'bytes':len(canonical(projection)),'sha256':digest(canonical(projection))},
                  'route':{'bytes':len(canonical(route)),'sha256':digest(canonical(route))} if route is not None else None,
                  'diagnostic_complete':projection['diagnostic_complete'],'before_currentness_sha256':before,'after_currentness_sha256':after,
                  'full_G2':False,'Q02':False,'original_acceptance':False,'receipt_transfer_authority':False}
        need(len(canonical(received))<=2048 and canonical(received).count(b'\n')<=96,'DIAGNOSTIC_RECEIVING_RECORD_BOUND')
        write_private(private/'diagnostic-receiving.json',canonical(received))
        probe['diagnostic_receiving']=received;probe['diagnostic_currentness'].update(before_readback=before,after_readback=after)
    else:raise Refusal('UNKNOWN_DIAGNOSTIC_OPERATION')


def diagnostic_readback_check(state,output,u):
    probe=state['docs']['PROBE.json'];projection=read_diagnostic_projection(output,u)
    need(projection==probe['failed_capture_diagnostic'] and read_diagnostic_route(output,u)==probe['diagnostic_route'],
         'DIAGNOSTIC_CLOSING_BYTES_CHANGED')
    received=probe['diagnostic_receiving']
    if received is not None:
        need(u.parse_json(u.checked_file(output/'private/diagnostic-receiving.json',4096))==received
             and received['projection']=={'bytes':len(canonical(projection)),'sha256':digest(canonical(projection))},
             'DIAGNOSTIC_RECEIVING_READBACK_CHANGED')
    return projection


def finalize_diagnostic(state,source,output,tools,u,command,source_fact):
    docs=state['docs'];probe=docs['PROBE.json']
    docs['SOURCE.json']['after']=source_fact
    docs['CLEANUP.json']['source_unchanged']=docs['SOURCE.json']['before']==source_fact
    docs['CLEANUP.json']['runtime_unchanged_after_initialization']=(state['runtime'] is not None and runtime_snapshot(source,state,u)==state['runtime'])
    need(docs['CLEANUP.json']['all_step_children_reaped'] and state['receipt'] is not None and state['run_root'] is not None,
         'DIAGNOSTIC_FINAL_OWNER_PREREQUISITE')
    rc,out,err=command('diagnostic-closing-currentness',[tools['bash'],str(source/OWNER),'--require-current-continuity',state['controller']],seconds=20)
    write_private(output/'private/final-currentness.stdout',out);write_private(output/'private/final-currentness.stderr',err)
    need(rc==0 and not err and out.decode().strip()==state['receipt'],'DIAGNOSTIC_FINAL_CURRENTNESS')
    probe['diagnostic_currentness']['closing']=digest(out)
    projection=diagnostic_readback_check(state,output,u)
    need(actual_policy_adoption(u)==state['policy_adoption'],'DIAGNOSTIC_CLOSING_POLICY_INPUT_CHANGED')
    need(native_projection(state,output,u,True)['qualified_for_pair_at_receiving'],'DIAGNOSTIC_NATIVE_PREREQUISITE_NOT_RECEIVED')
    state['native']['closing_currentness_verified_before_teardown']=True
    need(state['completed']==list(STEPS) and not state['failed'] and projection is not None and projection['diagnostic_complete']
         and probe['diagnostic_receiving'] is not None and all(probe['diagnostic_currentness'].values()),'DIAGNOSTIC_EPISODE_INCOMPLETE')
    return True


if __name__=='__main__':
    try:raise SystemExit(main())
    except (Refusal,OSError,ValueError,KeyError,TypeError):
        print('DG16_LINUX_NATIVE_EPISODE {"status":"UNQUALIFIED","code":"PRE_ENTRY_OR_RETENTION_REFUSED"}',flush=True)
        raise SystemExit(1)
