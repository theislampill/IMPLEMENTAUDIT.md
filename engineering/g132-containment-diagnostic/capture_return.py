#!/usr/bin/env python3
"""Unprivileged intent/return retention and ordinary setup classification only."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import time

REPOSITORY='theislampill/IMPLEMENTAUDIT.md'
BRANCH='pro/dg16-g132-containment-observe-20261121-01'
WORKFLOW='.github/workflows/dg16-g132-containment-observe.yml'
SELF='engineering/g132-containment-diagnostic/capture_return.py'
GUARD='engineering/g132-containment-diagnostic/run_stage.py'
GUARD_SHA256='b693564ea1d7955e4d54bed1b1c9ae0a9c121a6328647c7353fbd5fda00f3caa'
OWNER='scripts/qualify-work-graph-c5-setup.py'
OWNER_SHA256='3b3078e9c86d73c1789f102fcfbf2a4eaa9a835ba58ac9885c770dfbdaa50368'
STAGES=('launcher','policy','witness','finalize')
PREVIOUS={'policy':'launcher','witness':'policy'}
STREAM_LIMIT=131072
PIN={'bytes':72160,'sha256':'52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712'}
POLICY_SHA='b3f303f76b8f2c097f92ca5e41b6e0126cd34a10df1d5d0e67b9e86e92e322af'
POLICY_NAMES=('implementaudit-c5-bwrap-v1','implementaudit-c5-unpriv-bwrap-v1')
TARGET='/__c5_proc_setup_intentionally_absent_target__'
FILTER_SHA='df124088b9f6eabc9d06654bae67a6b8a09706936ccab78d358d0165a98fe4da'
ENV={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','TZ':'UTC'}
ARGUMENT_TEMPLATE=['--unshare-all','--unshare-user','--die-with-parent','--new-session','--clearenv',
    '--cap-drop','ALL','--perms','0755','--dir','/proc','--perms','0755','--dir','/dev',
    '--proc','/proc','--remount-ro','/proc','--symlink','/proc/self/fd','/dev/fd',
    '--dev-bind','/dev/null','/dev/null','--remount-ro','/','--chdir','/','--seccomp','OWNED_SEALED_SECCOMP_FD']

def need(value,code):
    if not value:raise ValueError(code)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def encode(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()

def parse(raw):
    def pairs(rows):
        result={}
        for key,value in rows:
            need(key not in result,'DUPLICATE_KEY');result[key]=value
        return result
    def constant(_):raise ValueError('NONFINITE')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)

def receive(stage,code,stdout,stderr):
    need(stage in STAGES and type(code) is int and 0<=code<=255,'NATIVE_RETURN_SHAPE')
    need(type(stdout) is bytes and type(stderr) is bytes
         and len(stdout)<=STREAM_LIMIT and len(stderr)<=STREAM_LIMIT,'NATIVE_STREAM_BOUND')
    record={'schema':'g132.ordinary-containment-native-return.v1','authority':'NONE','stage':stage,
            'observed_exit_code':code,'received':False,'owner_result':None,
            'streams':{name:{'bytes':len(raw),'sha256':sha(raw)} for name,raw in [('stdout',stdout),('stderr',stderr)]},
            'native_admission':False,'original_acceptance':False,'original_awards':[]}
    try:
        value=parse(stdout);need(type(value) is dict,'OWNER_RESULT_SHAPE');record['owner_result']=value
        need(code==0 and not stderr,'ACTUAL_NATIVE_RETURN_REFUSED')
        if stage=='launcher':
            need(value['scope']=='LINUX_LAUNCHER_PROVISION_ONLY_NO_C5_OR_NATIVE_ACCEPTANCE'
                 and value['target']=='/usr/bin/bwrap','LAUNCHER_SCOPE')
            launcher=value['launcher']
            need(all(launcher[k]==v for k,v in PIN.items()) and launcher['mode']=='0755'
                 and launcher['exclusive_creation'] is True
                 and launcher['opening']==launcher['closing'],'LAUNCHER_RESULT')
        elif stage=='policy':
            need(value['scope']=='EPHEMERAL_CI_BWRAP_POLICY_ONLY_NO_NATIVE_ACCEPTANCE'
                 and value['profile_sha256']==POLICY_SHA and value['global_state_unchanged'] is True
                 and value['receipt']=='/run/implementaudit-c5-bwrap-v1.json'
                 and value['parser']['exit_code']==0,'POLICY_SCOPE')
            need(set(value['loaded'])==set(value['compiled_profiles'])==set(POLICY_NAMES),'POLICY_POPULATION')
            for name in POLICY_NAMES:
                row=value['loaded'][name];digest=value['compiled_profiles'][name]
                need(type(digest) is str and re.fullmatch('[0-9a-f]{64}',digest)
                     and row['sha256']==digest and row['mode']=='enforce','POLICY_COMPILATION_JOIN')
        elif stage=='witness':
            need(value['schema']=='dg16.ordinary-setup-capability.v1' and value['authority']=='NONE'
                 and all(value[k] is False for k in ('original19_started','provider_acquired','native_admission')),
                 'ORDINARY_SCOPE')
            need(value['classification']=='SETUP_REACHED_ABSENT_TARGET' and value['complete_custody'] is True,
                 'ABSENT_TARGET_WITNESS_NOT_ESTABLISHED')
            need(all(value[k] is True for k in ('wait4_reaped','owned_group_absent','descriptor_restoration'))
                 and all(value[k] is False for k in ('timed_out','overflow','pidfd_kill'))
                 and value['eof']=={'stdout':True,'stderr':True}
                 and value['parent_opening']==value['parent_closing'],'WITNESS_CUSTODY')
            expected='bwrap: execvp '+TARGET+': No such file or directory\n'
            need(type(value['exit_code']) is int and value['exit_code']==1 and value['stdout']==''
                 and value['stderr']==expected and value['stream_bytes']=={'stdout':0,'stderr':len(expected)},
                 'WITNESS_NATIVE_OUTCOME')
            launcher=value['launcher'];mark=launcher['opening']
            need(all(launcher[k]==v for k,v in PIN.items()) and launcher['current'] is True
                 and mark==launcher['closing'] and type(mark) is list and len(mark)==9
                 and all(type(x) is int for x in mark) and stat.S_ISREG(mark[2])
                 and stat.S_IMODE(mark[2])==0o755 and mark[3]==1 and mark[4]==PIN['bytes']
                 and mark[7:]==[0,0],'WITNESS_LAUNCHER')
            args=value['arguments'];argv=value['argv']
            need(type(args) is list and len(args)==len(ARGUMENT_TEMPLATE)
                 and args[:-1]==ARGUMENT_TEMPLATE[:-1] and type(args[-1]) is str
                 and re.fullmatch('[0-9]{1,6}',args[-1])
                 and type(argv) is list and len(argv)==4 and argv[:2]==['/usr/bin/bwrap','--args']
                 and type(argv[2]) is str and re.fullmatch('[0-9]{1,6}',argv[2]) and argv[3]==TARGET
                 and value['environment']==ENV and value['cwd']=='/'
                 and value['seccomp_sha256']==FILTER_SHA
                 and value['argument_sha256']==sha(b'\0'.join(x.encode() for x in args)+b'\0'),
                 'WITNESS_FIXED_ARGUMENTS')
        else:
            need(value['scope']=='EPHEMERAL_CI_BWRAP_POLICY_OBSERVATION_ONLY'
                 and value['status'] in ('NO_OWNED_POLICY_OBSERVED','ACTIVE_POLICY_AND_RECEIPT_RETAINED')
                 and value['kernel_policy_unloaded'] is False and value['receipt_unlinked'] is False
                 and value['retained_until']=='EPHEMERAL_VM_DISPOSAL'
                 and value['observation_limit']=='SNAPSHOT_ONLY_NOT_LAUNCH_EXCLUSION','FINALIZATION_SCOPE')
            if value['status']=='ACTIVE_POLICY_AND_RECEIPT_RETAINED':
                need(value['profile_sha256']==POLICY_SHA and set(value['loaded'])==set(POLICY_NAMES),'FINALIZATION_POLICY')
        record.update(received=True,status='RECEIVED_AT_ORDINARY_STAGE_SCOPE',reason=None)
    except (ValueError,KeyError,TypeError,UnicodeError) as exc:
        reason=str(exc) if type(exc) is ValueError and re.fullmatch('[A-Z_]{1,80}',str(exc)) else 'OWNER_RESULT_SHAPE'
        record.update(status='ACTUAL_RETURN_RETAINED_NOT_QUALIFIED',reason=reason)
    return record

def read_fixed(path,maximum):
    path=Path(path).absolute();need(path.resolve(strict=True)==path,'FILE_ALIAS')
    before=path.lstat();mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=maximum,'FILE_BOUND')
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        need(mark(os.fstat(fd))==mark(before),'FILE_CHANGED');raw=os.pread(fd,maximum+1,0)
        need(len(raw)==before.st_size and mark(os.fstat(fd))==mark(before)==mark(path.lstat()),'FILE_CHANGED')
        return raw
    finally:os.close(fd)

def context(env):
    fixed={'GITHUB_ACTIONS':'true','RUNNER_ENVIRONMENT':'github-hosted','GITHUB_REPOSITORY':REPOSITORY,
           'GITHUB_REF':'refs/heads/'+BRANCH,'GITHUB_EVENT_NAME':'push','GITHUB_RUN_ATTEMPT':'1','GITHUB_JOB':'observe',
           'GITHUB_WORKFLOW_REF':REPOSITORY+'/'+WORKFLOW+'@refs/heads/'+BRANCH}
    need(all(env.get(k)==v for k,v in fixed.items()),'DIAGNOSTIC_CONTEXT')
    head=env.get('GITHUB_SHA','');run=env.get('GITHUB_RUN_ID','');pin=env.get('EXPECTED_CAPTURE_SHA256','')
    need(re.fullmatch('[0-9a-f]{40}',head) and env.get('GITHUB_WORKFLOW_SHA')==head
         and re.fullmatch('[1-9][0-9]{0,19}',run) and re.fullmatch('[0-9a-f]{64}',pin),'DIAGNOSTIC_CONTEXT')
    need(re.fullmatch('ubuntu[0-9]{2}',env.get('ImageOS',''))
         and re.fullmatch('[0-9]{8}\\.[0-9]{1,8}\\.[0-9]{1,4}',env.get('ImageVersion','')),'IMAGE_OBSERVATION')
    return {'repository':REPOSITORY,'ref':fixed['GITHUB_REF'],'run_id':run,'run_attempt':1,'job':'observe',
            'head_sha':head,'workflow_sha':head,'workflow_ref':fixed['GITHUB_WORKFLOW_REF'],
            'image_os':env['ImageOS'],'image_version':env['ImageVersion'],'capture_sha256':pin}

def current():
    ctx=context(os.environ);workspace=Path(os.environ['GITHUB_WORKSPACE']).absolute()
    need(workspace.resolve(strict=True)==workspace and Path(__file__).absolute()==workspace/SELF,'SOURCE_LOCATION')
    sources={}
    for name,pin,maximum in [(SELF,ctx['capture_sha256'],65536),(GUARD,GUARD_SHA256,16384),
                             (OWNER,OWNER_SHA256,131072),(WORKFLOW,None,65536)]:
        raw=read_fixed(workspace/name,maximum);digest=sha(raw)
        need(pin is None or digest==pin,'SOURCE_PIN');sources[name]={'bytes':len(raw),'sha256':digest}
    raw_head=read_fixed(workspace/'.git/HEAD',128)
    need(raw_head==(ctx['head_sha']+'\n').encode(),'CHECKOUT_HEAD')
    with open('/proc/sys/kernel/random/boot_id','rb') as stream:boot=stream.read(129)
    need(re.fullmatch(b'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\n',boot),'BOOT_ID')
    ctx['boot_identity_sha256']=sha(boot)
    return ctx,sources

def output_root(ctx):
    root=Path(os.environ['RUNNER_TEMP'])/('g132-containment-'+ctx['run_id']+'-a1')
    need(root.is_absolute() and root.resolve(strict=True)==root,'OUTPUT_LOCATION')
    info=root.lstat();need(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode)==0o700
                          and info.st_uid==os.geteuid() and info.st_gid==os.getegid(),'OUTPUT_CUSTODY')
    return root

def actual_argv(stage):
    keys=('GITHUB_REPOSITORY','GITHUB_EVENT_NAME','GITHUB_REF','GITHUB_RUN_ATTEMPT','GITHUB_RUN_ID',
          'GITHUB_SHA','GITHUB_JOB','GITHUB_WORKFLOW_SHA','GITHUB_WORKFLOW_REF','GITHUB_WORKSPACE',
          'RUNNER_TEMP','ImageOS','ImageVersion')
    return ['sudo','-n','/usr/bin/env','-i','PATH=/usr/bin:/bin','LANG=C.UTF-8','LC_ALL=C.UTF-8','TZ=UTC',
            'GITHUB_ACTIONS=true','RUNNER_ENVIRONMENT=github-hosted']+[k+'='+os.environ[k] for k in keys]+[
            '/usr/bin/python3.12','-I','-S','-B',os.environ['GITHUB_WORKSPACE']+'/'+GUARD,stage]

def main():
    need(sys.flags.isolated==1 and sys.dont_write_bytecode is True,'ISOLATED_CAPTURE_REQUIRED')
    args=sys.argv[1:];need(len(args) in (2,3) and args[0] in ('intent','capture') and args[1] in STAGES,'CAPTURE_MODE')
    mode,stage=args[:2];need(len(args)==(2 if mode=='intent' else 3),'CAPTURE_MODE')
    ctx,sources=current();root=output_root(ctx)
    if mode=='intent':
        if stage in PREVIOUS:
            previous=parse(read_fixed(root/(PREVIOUS[stage]+'.RETURN.json'),262144))
            need(previous['received'] is True and previous['stage']==PREVIOUS[stage]
                 and previous['context']==ctx and previous['sources']==sources,'PREVIOUS_STAGE_NOT_RECEIVED')
        result={'schema':'g132.ordinary-containment-intent.v1','authority':'NONE','stage':stage,'context':ctx,
                'sources':sources,'argv':actual_argv(stage),'started_unix_ns':time.time_ns(),
                'started_monotonic_ns':time.monotonic_ns(),'original_awards':[]}
        status=0
    else:
        code=int(args[2]);exit_raw=read_fixed(root/(stage+'.NATIVE_EXIT_STATUS.raw'),8)
        need(exit_raw==(str(code)+'\n').encode('ascii'),'NATIVE_EXIT_STATUS_JOIN')
        stdout=read_fixed(root/(stage+'.STDOUT.raw'),STREAM_LIMIT)
        stderr=read_fixed(root/(stage+'.STDERR.raw'),STREAM_LIMIT)
        intent_raw=read_fixed(root/(stage+'.INTENT.json'),16384);intent=parse(intent_raw)
        ended=time.monotonic_ns()
        need(intent['schema']=='g132.ordinary-containment-intent.v1' and intent['stage']==stage
             and intent['context']==ctx and intent['sources']==sources and intent['argv']==actual_argv(stage)
             and type(intent['started_monotonic_ns']) is int and 0<=intent['started_monotonic_ns']<=ended,'INTENT_JOIN')
        result=receive(stage,code,stdout,stderr)
        if stage=='finalize' and result['received'] and (root/'policy.RETURN.json').exists():
            prior=parse(read_fixed(root/'policy.RETURN.json',262144))
            need(prior['context']==ctx and prior['sources']==sources,'POLICY_CONTEXT_JOIN')
            if prior['received']:
                value=result['owner_result'];expected=prior['owner_result']['loaded']
                if value.get('status')!='ACTIVE_POLICY_AND_RECEIPT_RETAINED' or value.get('loaded')!=expected:
                    result.update(received=False,status='ACTUAL_RETURN_RETAINED_NOT_QUALIFIED',reason='POLICY_RETENTION_JOIN')
        result.update(context=ctx,sources=sources,argv=intent['argv'],started_unix_ns=intent['started_unix_ns'],
                      observed_after_return_unix_ns=time.time_ns(),elapsed_monotonic_ns=ended-intent['started_monotonic_ns'],
                      intent={'bytes':len(intent_raw),'sha256':sha(intent_raw)},
                      native_exit_status={'bytes':len(exit_raw),'sha256':sha(exit_raw)})
        status=0 if result['received'] else 3
    raw=encode(result);need(len(raw)<=262144,'CAPTURE_OUTPUT_BOUND')
    sys.stdout.buffer.write(raw);sys.stdout.buffer.flush()
    return status

if __name__=='__main__':raise SystemExit(main())
