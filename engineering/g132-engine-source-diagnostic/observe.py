#!/usr/bin/python3.12
"""One ordinary fixed-source observation. Never construct an original session."""
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import stat
import sys
import tempfile
import time
import types

SOURCE_COMMIT='f75533f95f0d099c87e7a04beb11b0a25628acdc'
SOURCE_TREE='9b9c2b3f1453b83b87b628b665fceff492bf5b1e'
SOURCE_PARENT='e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'
BRANCH='pro/dg16-g132-engine-source-observe-20261121-02'
WORKFLOW='.github/workflows/dg16-g132-engine-source-observe.yml'
PROFILE='FIXED_GENUINE_C5_SHARED_IMAGE_R5_HOSTED_UBUNTU24_SINGLE_COPY_20261105_V1'
REVISION='R5_HOSTED_UBUNTU24_GIT_08CA_SOURCE_20261121_V1'
SETUP_PIN=dict(bytes=83152,sha256='2dd699956d7b59eacd4a3f092e526047f0f4d89d0f7420edc9e8de093f5bd92c')
GIT_PIN=dict(bytes=4640384,sha256='08ca4d2ee4d8915e86f1faaa52603752507c57af1d16d451dec9992bc9b6d801',mode=493)
MAP_SHA256='5d4e482896bd812dadbc49acd3d61daa3bd2ce774c650c967a86cab02d6235bf'
CONTEXT_KEYS=('GITHUB_ACTIONS','RUNNER_ENVIRONMENT','GITHUB_REPOSITORY','GITHUB_EVENT_NAME',
              'GITHUB_REF','GITHUB_RUN_ATTEMPT','GITHUB_RUN_ID','GITHUB_SHA','GITHUB_JOB',
              'GITHUB_WORKFLOW_SHA','GITHUB_WORKFLOW_REF','ImageOS','ImageVersion')
CAPS=dict(address_bytes=1610612736,cpu_seconds=120,file_bytes=268435456,
          descriptors=256,wall_seconds=240,report_bytes=2097152)

def need(value,message):
    if not value:raise ValueError(message)

def validate_context(context,identity):
    need(identity==(0,0,0,0),'actual UID/GID zero is required')
    exact=dict(GITHUB_ACTIONS='true',RUNNER_ENVIRONMENT='github-hosted',
        GITHUB_REPOSITORY='theislampill/IMPLEMENTAUDIT.md',GITHUB_EVENT_NAME='push',
        GITHUB_REF='refs/heads/'+BRANCH,GITHUB_RUN_ATTEMPT='1',GITHUB_JOB='observe',
        GITHUB_WORKFLOW_REF='theislampill/IMPLEMENTAUDIT.md/'+WORKFLOW+'@refs/heads/'+BRANCH,
        ImageOS='ubuntu24',ImageVersion='20261116.376.1')
    need(all(context.get(k)==v for k,v in exact.items()),'fixed ordinary context or host differs; no retry')
    need(re.fullmatch('[1-9][0-9]{0,19}',context.get('GITHUB_RUN_ID','')) is not None,'run identity differs')
    need(re.fullmatch('[0-9a-f]{40}',context.get('GITHUB_SHA','')) is not None,'diagnostic source identity differs')
    need(context.get('GITHUB_WORKFLOW_SHA')==context['GITHUB_SHA'],'workflow/source identity differs')

def validate_git_pin(row):
    need(row.get('kind')=='FILE' and all(row.get(k)==v for k,v in GIT_PIN.items()),
         'prospective Git08ca body differs; old and other pins are not accepted')

def validate_source(row):
    need(row.get('source_commit')==SOURCE_COMMIT and row.get('source_tree')==SOURCE_TREE
         and row.get('ordered_parents')==[SOURCE_PARENT] and row.get('clean') is True
         and row.get('complete_objects') is True,'exact standalone complete source tuple differs')

def base_result():
    return dict(schema='g132.ordinary-hosted-engine-source-observation.v1',authority='NONE',
        source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,source_parent=SOURCE_PARENT,
        original_execution=False,session_constructed=False,provider_acquired=False,
        provider_imports=0,native_admission=False,original_awards=[],overall_admission='UNQUALIFIED',
        private_inputs_selected=False,launcher_provisioned=False,policy_changed=False,
        no_automatic_retry=True,source_guards_unchanged=True,resource_caps=dict(CAPS),gates={})

def physical(path,maximum):
    path=Path(path)
    before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_size<=maximum,'ordinary physical file bound/type differs')
    def identity(info):
        return (info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,
                info.st_mtime_ns,info.st_ctime_ns,info.st_uid,info.st_gid)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(identity(os.fstat(fd))==identity(before),'physical file identity changed at open')
        raw=os.pread(fd,maximum+1,0)
        need(len(raw)==before.st_size and identity(os.fstat(fd))==identity(before) and identity(path.lstat())==identity(before),
             'physical file changed during bounded read')
        return raw,dict(kind='FILE',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
            mode=stat.S_IMODE(before.st_mode),uid=before.st_uid,gid=before.st_gid,
            identity=[str(before.st_dev),str(before.st_ino),before.st_mode,before.st_nlink,
                      before.st_size,before.st_mtime_ns,before.st_ctime_ns])
    finally:os.close(fd)

def pinned(path,pin):
    raw,row=physical(path,pin['bytes'])
    need(all(row[k]==v for k,v in pin.items()),'fixed source body differs: '+str(path))
    return raw

def engine_map(current,expected):
    result={name:dict(bytes=len(value[0]),sha256=hashlib.sha256(value[0]).hexdigest())
            for name,value in current.SOURCES.items()}
    need(result==expected,'actual thirteen-member Engine map differs')
    need(current.PROFILE==PROFILE and current.SPEC['profile']==PROFILE,'actual Engine profile differs')
    current.CHECK()
    return result

def gate(result,name,operation):
    try:
        value=operation()
        result['gates'][name]=dict(status='PASS',value=value)
        return value
    except (OSError,ValueError,KeyError) as exc:
        result['gates'][name]=dict(status='REFUSED',type=type(exc).__name__,reason=str(exc)[:512])
        return None

def observe():
    result=base_result()
    result['started_time_ns']=time.time_ns()
    result['context']={k:os.environ.get(k,'') for k in CONTEXT_KEYS}
    result['process']=dict(pid=os.getpid(),ppid=os.getppid(),uid=os.getuid(),euid=os.geteuid(),
        gid=os.getgid(),egid=os.getegid(),executable=str(Path('/proc/self/exe').resolve()),
        proc_starttime_ticks=Path('/proc/self/stat').read_text().split()[21],python=sys.version)
    phase='context'
    setup=None
    old_alarm=None
    baseline=None
    allow_git=False
    subprocess_calls=[]
    active=True
    git_prefix=['/usr/bin/git','-c','credential.helper=','-c','core.askPass=/bin/false',
        '-c','core.hooksPath=/dev/null','-c','gc.auto=0','-c','maintenance.auto=false']

    def audit(event,args):
        if not active:return
        if event=='subprocess.Popen':
            executable,argv,cwd,environment=args
            need(allow_git and executable=='/usr/bin/git' and list(argv[:len(git_prefix)])==git_prefix,
                 'only the fixed ordinary source-preparation Git child is permitted')
            need(len(subprocess_calls)<11,'ordinary source-preparation child population exceeded')
            subprocess_calls.append(list(argv))
        elif event in ('os.system','os.fork','os.forkpty','os.exec','os.posix_spawn',
                       'socket.__new__','socket.connect','socket.bind'):
            raise ValueError('ordinary observer refused process/network operation: '+event)

    try:
        validate_context(result['context'],(os.getuid(),os.geteuid(),os.getgid(),os.getegid()))
        root=Path(__file__).resolve().parents[2]
        own=Path(__file__).resolve()
        own_raw,own_row=physical(own,131072)
        need(own_row['sha256']==os.environ.get('EXPECTED_OBSERVER_SHA256'),'diagnostic owner body differs')
        result['diagnostic_owner']=own_row
        map_raw=pinned(own.parent/'ENGINE_MAP.json',dict(bytes=int(os.environ['EXPECTED_MAP_BYTES']),sha256=MAP_SHA256))
        expected_map=json.loads(map_raw)
        need(len(expected_map)==13,'expected Engine population differs')
        path=root/'scripts/qualify-work-graph-c5-setup.py'
        raw=pinned(path,SETUP_PIN)
        setup=types.ModuleType('g132_fixed_ordinary_setup')
        setup.__file__=str(path)
        sys.addaudithook(audit)
        exec(compile(raw,str(path),'exec'),setup.__dict__)
        baseline=setup.fds()
        for which,value in [(resource.RLIMIT_AS,CAPS['address_bytes']),(resource.RLIMIT_CPU,CAPS['cpu_seconds']),
                            (resource.RLIMIT_FSIZE,CAPS['file_bytes']),(resource.RLIMIT_NOFILE,CAPS['descriptors'])]:
            resource.setrlimit(which,(value,value))
        def deadline(signum,frame):raise setup.HostedPrerequisiteDeadline('ordinary source observation wall bound')
        old_alarm=signal.signal(signal.SIGALRM,deadline)
        signal.alarm(CAPS['wall_seconds'])
        phase='exact_engine_loading'
        current=setup.hosted_current_owner(root)
        result['engine_map']=engine_map(current,expected_map)
        result['engine_loading_origin']='DIAGNOSTIC_CHECKOUT_EXACT_R2_MEMBERS'
        result['profile']=PROFILE
        result['source_revision']=REVISION
        result['engine_loaded']=True
        phase='prospective_git_receiving'
        _,before_git=physical('/usr/bin/git',GIT_PIN['bytes'])
        result['git_before']=before_git
        validate_git_pin(before_git)
        phase='selected_host_inputs'
        try:
            host_inputs=setup.receive_hosted_inputs(current)
            result['selected_host_input_observation']=host_inputs
            result['selected_host_input_matches']=bool(
                all(row['match'] for row in host_inputs['pins']+host_inputs['system_aliases'])
                and host_inputs['nss']['result']['match'] and host_inputs['selected_bookends_equal']
                and host_inputs['unchanged_owner_full_startup']['match'])
        except (OSError,ValueError,KeyError) as exc:
            result['selected_host_input_observation']=dict(status='REFUSED',type=type(exc).__name__,reason=str(exc)[:512])
            result['selected_host_input_matches']=False
        rows=[setup.hosted_pin_receiving(current.B,name,pin,{}) for name,pin in current.SPEC['git_files'].items()]
        result['selected_git_file_rows']=rows
        gate(result,'unchanged_git_input_validator',lambda:current.git_inputs({}))
        launcher=dict(current.SPEC['launcher'],mode=493)
        result['launcher_observation']=setup.hosted_pin_receiving(current.B,'/usr/bin/bwrap',launcher,{})
        phase='standalone_source_preparation'
        output=Path(tempfile.mkdtemp(prefix='g132-engine-source-'))
        result['disposable_source_root']=str(output)
        commands=[]
        result['source_preparation']=dict(commands=commands,expected_commit=SOURCE_COMMIT)
        allow_git=True
        try:source=setup.prepare_hosted_source(root,output,SOURCE_COMMIT,records=commands)
        finally:allow_git=False
        result['source_preparation']=source
        validate_source(source)
        actual_source=Path(source['path'])
        phase='actual_checkout_engine_loading'
        need(pinned(actual_source/'scripts/qualify-work-graph-c5-setup.py',SETUP_PIN)==raw,
             'actual source observer differs')
        actual=setup.hosted_current_owner(actual_source)
        result['actual_checkout_engine_map']=engine_map(actual,expected_map)
        phase='complete_actual_source_capture'
        objects={}
        captured=actual.B.complete_source(actual_source,objects)
        result['source_capture']=dict(projection=captured['projection'],files=len(captured['state']['files']),
            directories=len(captured['state']['directories']),objects=len(objects),
            object_bytes=sum(map(len,objects.values())),
            actual_file_bytes=sum(x['bytes'] for x in captured['state']['files'].values()),
            state_sha256=hashlib.sha256(json.dumps(captured['state'],sort_keys=True,separators=(',',':')).encode()).hexdigest())
        gate(result,'git_namespace',lambda:actual.P.validate_git_namespace(captured['state'],objects))
        gate(result,'producer_contract',lambda:actual.B._producer_contract(captured['state']))
        gate(result,'captured_head_identity',lambda:actual.captured_source_identity(captured,objects,
             dict(source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE)))
        actual.CHECK()
        current.CHECK()
        _,after_git=physical('/usr/bin/git',GIT_PIN['bytes'])
        result['git_after']=after_git
        result['git_bookends_equal']=before_git==after_git
        need(result['git_bookends_equal'],'selected Git changed across source observation')
        result['source_loading_bookends_current']=True
        result['status']='OBSERVATION_COMPLETE_WITH_RECORDED_GATE_DISPOSITIONS'
    except BaseException as exc:
        result.update(status='REFUSED',failed_phase=phase,exception_type=type(exc).__name__,reason=str(exc)[:512])
    finally:
        active=False
        if old_alarm is not None:
            signal.alarm(0)
            signal.signal(signal.SIGALRM,old_alarm)
        result['ordinary_git_children']=subprocess_calls
        result['descriptor_restoration']=setup.fds()==baseline if setup is not None and baseline is not None else None
        result['finished_time_ns']=time.time_ns()
        raw=json.dumps(result,sort_keys=True,separators=(',',':')).encode()+b'\n'
        need(len(raw)<=CAPS['report_bytes'],'bounded observation report exceeded')
        sys.stdout.buffer.write(raw)
    source_gates=('git_namespace','producer_contract','captured_head_identity')
    return 0 if result.get('status')=='OBSERVATION_COMPLETE_WITH_RECORDED_GATE_DISPOSITIONS' and result['descriptor_restoration'] is True and all(
        result['gates'].get(name,{}).get('status')=='PASS' for name in source_gates) else 2

def seal_return(directory):
    directory=Path(directory)
    members={}
    for name in ('OBSERVATION.json','STDERR.raw','NATIVE_EXIT_STATUS.raw'):
        raw,row=physical(directory/name,CAPS['report_bytes'])
        members[name]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    value=(directory/'NATIVE_EXIT_STATUS.raw').read_bytes()
    need(re.fullmatch(b'[0-9]{1,3}\n',value) is not None and 0<=int(value)<=255,'native return status differs')
    result=dict(schema='g132.ordinary-hosted-engine-source-native-return.v1',authority='NONE',
        native_exit_status=int(value),members=members,native_admission=False,original_awards=[])
    with (directory/'RETURN.json').open('xb') as stream:
        stream.write(json.dumps(result,sort_keys=True,indent=2).encode()+b'\n')
    return result

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--seal-return':
        seal_return(sys.argv[2])
    elif len(sys.argv)==1:
        raise SystemExit(observe())
    else:
        raise SystemExit('unsupported ordinary diagnostic arguments')
