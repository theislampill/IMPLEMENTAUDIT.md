#!/usr/bin/env python3
"""Original outer capture custody; inner PASS is private until outer receiving."""
import argparse
import contextlib
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import sys
import time

HERE=Path(__file__).absolute().parent
INNER_SHA='adec516f04aad099029c7bb65de3074c29ed021d499adf24a9e29bb0216c9527'
BANK_SECONDS=14400
RUN_SECONDS=15600


def need(value,code):
    if not value:raise ValueError(code)


def load_inner():
    # Fixed source-owned loader; no process or grant is produced by import.
    fd=os.open(HERE/'inner.py',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        info=os.fstat(fd)
        need(__import__('stat').S_ISREG(info.st_mode) and info.st_size<=65536,'INNER_SOURCE_FILE')
        raw=os.read(fd,65537)
        need(len(raw)==info.st_size and hashlib.sha256(raw).hexdigest()==INNER_SHA,'INNER_SOURCE_PIN')
    finally:os.close(fd)
    spec=importlib.util.spec_from_file_location('canary_inner',HERE/'inner.py')
    module=importlib.util.module_from_spec(spec)
    exec(compile(raw,str(HERE/'inner.py'),'exec'),module.__dict__)
    return module


def enable_subreaper():
    lib=ctypes.CDLL(None,use_errno=True);actual=ctypes.c_int()
    need(lib.prctl(36,1,0,0,0)==0 and lib.prctl(37,ctypes.byref(actual),0,0,0)==0 and actual.value==1,'SUBREAPER_REFUSED')


class EpisodeDeadline(RuntimeError):
    pass


@contextlib.contextmanager
def episode_guard(deadline):
    # Original run.py outer alarm/SIGTERM pattern, outside the maintained sigwait owner.
    previous_handler=signal.getsignal(signal.SIGALRM)
    previous_term=signal.getsignal(signal.SIGTERM)
    need(signal.getitimer(signal.ITIMER_REAL)==(0.0,0.0),'PREEXISTING_ALARM_REFUSED')
    remaining=int(deadline-time.monotonic())
    need(0<remaining<=RUN_SECONDS,'EPISODE_EXPIRED')
    def expired(_a,_b):raise EpisodeDeadline('OUTER_EPISODE_DEADLINE')
    signal.signal(signal.SIGALRM,expired);signal.signal(signal.SIGTERM,expired)
    try:
        signal.alarm(remaining)
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM,previous_handler);signal.signal(signal.SIGTERM,previous_term)


def public_context(I,environment):
    episode=I.context(environment)
    need(re.fullmatch('[0-9a-f]{40}',episode['GITHUB_SHA']) is not None and
         0<len(episode['GITHUB_RUN_ID'])<=20,'PUBLIC_JOB_IDENTITY')
    image={k:environment.get(k) for k in ('ImageOS','ImageVersion')}
    need(all(type(v) is str and re.fullmatch('[A-Za-z0-9._-]{1,128}',v) for v in image.values()),'PUBLIC_IMAGE_FIELDS')
    return dict(schema='dg16.canary.public-job-context.v1',source_commit=I.COMMIT,source_tree=I.TREE,
                job=dict(episode,**image))


def join_result(I,E,episode,inner_path,rc,records,error):
    result=dict(schema='dg16.hosted-wrapper-canary.outer.v1',authority='NONE',original_awards=[],
        source_commit=I.COMMIT,source_tree=I.TREE,episode=episode,status='UNQUALIFIED',
        scope='ONE_UNCHANGED_WRAPPER_CANARY_NOT_FULL_G2_OR_ORIGINAL_ACCEPTANCE',
        ordinary_workload_wall_seconds=BANK_SECONDS,episode_wall_seconds=RUN_SECONDS,
        raw_retention='PRIVATE_RUNNER_ONLY_NO_RAW_UPLOAD_NO_CRYPTO',inner_receiving='NOT_CONSUMED')
    if len(records)==1:
        row=records[0]
        result['outer_capture']={k:row.get(k) for k in ('process_started','returncode','timeout','output_bound_exceeded',
            'pidfd_acquired','internal_failure','streams_complete','stdout_bytes','stderr_bytes','stdout_sha256','stderr_sha256','reason_code')}
        result['outer_capture']['cleanup']=row.get('cleanup')
    try:
        need(error is None and len(records)==1,'OUTER_CAPTURE_REFUSED')
        row=records[0]
        need(rc==0 and row.get('returncode')==0 and row.get('process_started') is True and
             row.get('pidfd_acquired') is True and row.get('internal_failure') is None and
             row.get('timeout') is False and row.get('output_bound_exceeded') is False and
             row.get('streams_complete') is True,'OUTER_EXIT_OR_DEADLINE_REFUSED')
        need(type(row.get('cleanup')) is dict and row['cleanup'].get('echild') is True,'OUTER_CLEANUP_UNQUALIFIED')
        raw=I.read(inner_path,65536)
        inner=E.parse(raw)
        need(type(inner) is dict and inner.get('schema')=='dg16.hosted-wrapper-canary.v1' and
             inner.get('authority')=='NONE' and inner.get('original_awards')==[] and
             inner.get('source_commit')==I.COMMIT and inner.get('source_tree')==I.TREE and
             inner.get('episode')==episode and inner.get('phase')=='REPORT_RECEIVING_COMPLETE' and
             inner.get('dependency_manifest_sha256')==I.sha(I.read(HERE/'DEPENDENCIES.json',32768)) and
             inner.get('host_before')==inner.get('host_after') and
             inner.get('status')=='CANARY_REPORT_RELATION_PASS_ONLY' and
             inner.get('exit_code')==0 and inner.get('cleanup_qualified') is True and
             inner.get('cleanup',{}).get('quiescence')=='ECHILD_ALL_CHILDREN' and
             inner.get('cleanup',{}).get('flag_restored') is True and
             inner.get('child_umask')=='022' and inner.get('private_parent_umask')=='077','INNER_RESULT_REFUSED')
        need([r['legacy_ordinal'] for r in inner['reports']]==list(range(34,42)) and
             [r['declared'] for r in inner['reports']]==[5,15,24,9,26,22,7,20],'INNER_REPORT_POPULATION')
        result['inner_receiving']='OUTER_QUALIFIED_EXACT_INNER_RESULT_RECEIVED'
        result['inner_result_sha256']=hashlib.sha256(raw).hexdigest()
        result['received_inner']=inner
        result['status']='CANARY_REPORT_RELATION_PASS_ONLY'
    except BaseException:
        # Never copy or publish a private inner PASS when outer custody/exit/cleanup is unqualified.
        result['status']='UNQUALIFIED'
    return result


def execute(source,output):
    started=time.monotonic();deadline=started+RUN_SECONDS
    I=load_inner();packet=public_context(I,os.environ);episode=I.context(packet['job'])
    deps=json.loads(I.read(HERE/'DEPENDENCIES.json',32768));pins=deps['files']
    for name,row in pins.items():
        raw=I.read(HERE/name,2*1024**2)
        need(dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())==row,'DEPENDENCY_PIN')
    U=I.load('host_utility',pins);E=I.load('evidence_io',pins)
    need(source.is_absolute() and output.is_absolute() and not output.exists() and
         source!=output and source not in output.parents,'FRESH_OUTPUT_REQUIRED')
    output.mkdir(mode=0o700);private=output/'private';private.mkdir(mode=0o700)
    public=output/'public';public.mkdir(mode=0o700)
    context_path=private/'public-job-context.json'
    context_raw=(json.dumps(packet,sort_keys=True)+'\n').encode()
    I.write_private(context_path,context_raw)
    # Original outer owner is a dedicated process. Never take custody of preexisting children.
    need(U.children()==[],'PREEXISTING_CHILDREN_REFUSED')
    enable_subreaper()
    rc=None;records=[];error=None;stdout=stderr=b''
    with episode_guard(deadline):
        try:
            rc,stdout,stderr=U.capture('canary-inner',[
                '/usr/bin/python3','-I','-S','-B',str(HERE/'inner.py'),
                '--source',str(source),'--output',str(private/'inner'),
                '--job-context',str(context_path)],records,deadline,seconds=BANK_SECONDS)
        except BaseException as exc:
            error=exc
            captured=getattr(exc,'captured',None)
            if captured is not None:stdout,stderr=captured['stdout'],captured['stderr']
        # Outer stream copies are private diagnostics only, never workflow log lines.
        I.write_private(private/'outer.stdout',stdout);I.write_private(private/'outer.stderr',stderr)
        need(I.sha(I.read(HERE/'inner.py',65536))==INNER_SHA,'INNER_SOURCE_CLOSING')
        need(I.read(context_path,4096)==context_raw,'PUBLIC_CONTEXT_CLOSING')
        for name,row in pins.items():
            raw=I.read(HERE/name,2*1024**2)
            need(dict(bytes=len(raw),sha256=I.sha(raw))==row,'DEPENDENCY_CLOSING')
        result=join_result(I,E,episode,private/'inner/public/RESULT.json',rc,records,error)
        I.write(public/'RESULT.json',result)
    return 0 if result['status']=='CANARY_REPORT_RELATION_PASS_ONLY' else 1


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    try:return execute(args.source,args.output)
    except BaseException:
        print('DG16_CANARY {"status":"UNQUALIFIED","phase":"OUTER_PREFLIGHT_OR_EPISODE"}')
        return 1


if __name__=='__main__':raise SystemExit(main())
