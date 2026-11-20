#!/usr/bin/env python3
"""Retain one prospective complete original A3 discriminator; confer no acceptance authority.

The product and original fixture factory are unchanged; episode.py is a new prospective full-predicate discriminator.
This recorder confers no acceptance or native-host authority.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import time
import traceback
import unittest
import zipfile

SOURCE_COMMIT = '51416b2f156b341c4a5f09029e2c6ceb5b30b1e7'
SOURCE_TREE = '9c3913ceaa95f3f36b0377fe2dba4a302afcba89'
BRANCH = 'pro/dg18-a3-current-51416-20261120-02'
WORKFLOW_PATH = '.github/workflows/dg18-a3-current-capture.yml'
HELPER_PATH = 'handoff/pro-executor-results-20261115/dg18-a3-current-capture/capture.py'
EPISODE_PATH = 'handoff/pro-executor-results-20261115/dg18-a3-current-capture/episode.py'
ORIGINAL_TEST = 'fixtures/canonical-state-rotation/canonical_reader_test.py'
STAGES = ('original-a3-full-conjunction',)
METHODS = ('test_complete_archive_isolation',)
CONTEXT = {'schema': 'dg18.original-a3-capture.v1', 'authority': 'NONE',
           'source_commit': SOURCE_COMMIT, 'source_tree': SOURCE_TREE,
           'original_criterion': 3, 'original_denominator': 14,
           'native_Stop_OR_C02_or_N1_evidence': False, 'automatic_retry': False}


def digest(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            'git_blob': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()}


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def write_new(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def write_json(path, value):
    write_new(path, canonical(value))


def safe_dir(path):
    path = Path(os.path.abspath(path))
    for node in (path, *path.parents):
        info = node.lstat()
        if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
            raise ValueError('nonphysical directory: ' + str(node))
    return path


def git(source, *arguments):
    env = dict(os.environ)
    for key in list(env):
        if key.startswith('GIT_'):
            env.pop(key)
    env.update(PATH='/usr/bin:/bin', LC_ALL='C', GIT_CONFIG_NOSYSTEM='1',
               GIT_CONFIG_GLOBAL='/dev/null', GIT_NO_LAZY_FETCH='1', GIT_ALLOW_PROTOCOL='')
    return subprocess.run(['/usr/bin/git', '-c', 'protocol.allow=never',
        '-c', 'core.hooksPath=/dev/null', '-c', 'core.fsmonitor=false', *arguments],
        cwd=source, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=True, timeout=30).stdout


def provider_binding(output):
    expected = {'GITHUB_ACTIONS': 'true', 'RUNNER_ENVIRONMENT': 'github-hosted',
        'GITHUB_REPOSITORY': 'theislampill/IMPLEMENTAUDIT.md', 'GITHUB_EVENT_NAME': 'push',
        'GITHUB_REF': 'refs/heads/' + BRANCH, 'GITHUB_RUN_ATTEMPT': '1'}
    for key, value in expected.items():
        if os.environ.get(key) != value:
            raise ValueError('host/event binding mismatch: ' + key)
    run = os.environ.get('GITHUB_RUN_ID', '')
    workflow_commit = os.environ.get('GITHUB_SHA', '')
    if not re.fullmatch(r'[0-9]+', run) or not re.fullmatch(r'[0-9a-f]{40}', workflow_commit):
        raise ValueError('invalid provider run/commit')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    if event.get('before') != '0' * 40 or event.get('after') != workflow_commit:
        raise ValueError('not the exact first branch-creation push')
    if event.get('deleted') is not False or event.get('created') is not True:
        raise ValueError('event is not a new live branch')
    if sys.platform != 'linux' or os.path.abspath(sys.executable) != '/usr/bin/python3.12':
        raise ValueError('existing qualified Linux physical interpreter required')
    selected_output = safe_dir(os.environ['RUNNER_TEMP']) / ('dg18-a3-' + run + '-1')
    if Path(os.path.abspath(output)) != selected_output:
        raise ValueError('output does not bind exact provider run')
    return expected,run,workflow_commit,selected_output


def host_binding(source, output):
    expected,run,workflow_commit,selected_output=provider_binding(output)
    source = safe_dir(source)
    if selected_output.is_relative_to(source) or source.is_relative_to(selected_output):
        raise ValueError('output and product source overlap')
    packet = Path(__file__).absolute().parents[len(PurePosixPath(HELPER_PATH).parts)-1]
    packet = safe_dir(packet)
    actual = git(packet, 'show', '-s', '--format=%H%n%T%n%P', 'HEAD').decode().splitlines()
    if actual[0] != workflow_commit or actual[2].split() != [SOURCE_COMMIT]:
        raise ValueError('workflow commit does not have exact sole source parent')
    changed = git(packet, 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').decode().splitlines()
    if sorted(changed) != sorted([WORKFLOW_PATH, HELPER_PATH, EPISODE_PATH]):
        raise ValueError('publication contains unreviewed paths')
    if git(packet, 'status', '--porcelain=v1', '--untracked-files=all'):
        raise ValueError('workflow checkout changed')
    return {**CONTEXT, 'run_id': int(run), 'attempt': 1,
            'workflow_commit': workflow_commit, 'workflow_tree': actual[1],
            'workflow_parent': SOURCE_COMMIT, 'workflow_changed_paths': changed,
            'source_path': str(source), 'output_path': str(selected_output),
            'helper': digest(Path(__file__).read_bytes()), 'episode': digest((packet/EPISODE_PATH).read_bytes()), 'host_predicates': expected}


def source_census(source):
    actual = git(source, 'show', '-s', '--format=%H%n%T', 'HEAD').decode().splitlines()
    if actual != [SOURCE_COMMIT, SOURCE_TREE]:
        raise ValueError('product source commit/tree differs')
    status = git(source, 'status', '--porcelain=v1', '--untracked-files=all')
    if status:
        raise ValueError('product source not clean: ' + status.decode(errors='replace'))
    prefixes = ('skills/implementaudit/scripts/', 'skills/implementaudit/templates/')
    exact = {ORIGINAL_TEST, 'fixtures/canonical-state-rotation/protected_projection_v2_test.py',
             'fixtures/canonical-state-rotation/v2/source.json',
             'fixtures/controller-initialization/author_checkpoint.py',
             'fixtures/run-root-example/phases/phase-1.md'}
    rows = []
    for line in git(source, 'ls-tree', '-r', 'HEAD').decode().splitlines():
        metadata, path = line.split('\t', 1)
        if path not in exact and not path.startswith(prefixes):
            continue
        mode, kind, oid = metadata.split()
        p = source / path
        info = p.lstat()
        if kind != 'blob' or mode not in {'100644','100755'} or not stat.S_ISREG(info.st_mode):
            raise ValueError('nonregular selected runtime member: ' + path)
        safe_dir(p.parent)
        raw = p.read_bytes()
        if digest(raw)['git_blob'] != oid:
            raise ValueError('runtime source differs from immutable Git tree: ' + path)
        rows.append({'path':path,'mode':mode,**digest(raw)})
    if not exact.issubset({row['path'] for row in rows}):
        raise ValueError('selected source population incomplete')
    physical = {p.relative_to(source).as_posix() for prefix in prefixes
                for p in (source/prefix).rglob('*') if p.is_file() or p.is_symlink()}
    selected_runtime = {row['path'] for row in rows if row['path'].startswith(prefixes)}
    if physical != selected_runtime:
        raise ValueError('physical copied runtime population differs from Git tree')
    tools = []
    for path in ('/usr/bin/python3.12','/usr/bin/git','/usr/bin/bash'):
        p = Path(path); info = p.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('unqualified physical executable: ' + path)
        tools.append({'path':path,'uid':info.st_uid,'mode':oct(info.st_mode & 0o7777),**digest(p.read_bytes())})
    return {**CONTEXT, 'source_members':rows, 'source_member_count':len(rows),
            'tools':tools, 'git_status':status.decode(), 'python':sys.version,
            'git_version':git(source,'--version').decode().strip()}


def process_survivorship(evidence_root):
    """Observe current descendants and processes holding this isolated fixture path."""
    records, unavailable = {}, []
    for node in Path('/proc').iterdir():
        if not node.name.isdigit():
            continue
        try:
            raw = (node/'stat').read_text(); rest = raw[raw.rfind(')')+2:].split()
            pid = int(node.name); ppid = int(rest[1]); birth = int(rest[19])
            try: cwd = os.readlink(node/'cwd')
            except OSError: cwd = None
            try: argv = (node/'cmdline').read_bytes().split(b'\0'); argv = [a.decode(errors='replace') for a in argv if a]
            except OSError: argv = []
            records[pid] = {'pid':pid,'ppid':ppid,'start_ticks':birth,'state':rest[0], 'cwd':cwd,'argv':argv}
        except (FileNotFoundError,ProcessLookupError):
            continue
        except (PermissionError,ValueError,IndexError) as exc:
            unavailable.append({'pid':int(node.name),'error':type(exc).__name__})
    descendants = {os.getpid()}
    while True:
        larger = descendants | {pid for pid,r in records.items() if r['ppid'] in descendants}
        if larger == descendants:break
        descendants = larger
    prefix = str(evidence_root) + '/'
    survivors = [r for pid,r in records.items() if pid != os.getpid() and (
        pid in descendants or (r['cwd'] is not None and r['cwd'].startswith(prefix)) or
        any(arg.startswith(prefix) for arg in r['argv']))]
    return {'observer_pid':os.getpid(),'scope':'Current descendants plus process cwd/argv under exact isolated fixture directory; not a native host event or Windows aggregate performance census.',
            'fixture_root':str(evidence_root),'survivors':survivors,'unavailable_process_rows':unavailable,
            'all_selected_process_rows_observable':not unavailable}


def preflight(source, output):
    binding = host_binding(source,output)
    output.mkdir(mode=0o700,exist_ok=False)
    write_json(output/'PREFLIGHT_INTENT.json',binding)
    census = source_census(source)
    write_json(output/'SOURCE_BEFORE.json',census)
    write_json(output/'PREFLIGHT.json',{**binding,'status':'QUALIFIED_FOR_DECLARED_ORDINARY_A3_FIXTURES',
       'source_before':digest((output/'SOURCE_BEFORE.json').read_bytes()),
       'stages':list(STAGES),'methods':list(METHODS),
       'retention':'New prospective episode retains content-addressed per-phase snapshots and final actual fixture ZIP before original fixture cleanup.',
       'fresh_original_execution_reason':'Checked existing source and retained current evidence do not establish complete A3 archive-as-live, recursive-validator and simultaneous-current discrimination. One new prospective fixture uses the unchanged product. No historical replay or authenticated native event.',
       'award':None})
    print('A3 exact source/preflight received; original cases have not executed.')


def artifact_record(output, stage):
    if stage != STAGES[0]:raise ValueError('undeclared A3 episode')
    folder=output/'stage-records';record_path=folder/(stage+'.json')
    record=json.loads(record_path.read_bytes())
    if (record.get('schema')!='dg18.prospective-original-a3-full-discriminator.v1' or
        record.get('method_completed') is not True or record.get('authority')!='NONE' or
        record.get('original_criterion')!=3 or record.get('original_denominator')!=14 or
        record.get('native_host_occurrence') is not False or record.get('award') is not None):
        raise ValueError('A3 episode incomplete or scope changed')
    expected_snapshots={'G0002-archive-canary-excluded','identical-canary-in-current-phase-population',
        'current-phase-adversary-removed','pending-boundary-no-current-generation',
        'G0003-only-current','old-and-archive-tokens-refused','live-pointer-absent-archive-not-current','retired-root-pair-poisoned',
        'G0003-despite-retired-root-poison','final-retained-fixture'}
    snapshots=record['snapshots']
    if len(snapshots)!=len(expected_snapshots) or {r['label'] for r in snapshots}!=expected_snapshots:
        raise ValueError('A3 full snapshot population missing or duplicated')
    for row in snapshots:
        p=PurePosixPath(row['path'])
        if p.is_absolute() or '..' in p.parts:raise ValueError('unsafe snapshot locator')
        got=digest((folder/row['path']).read_bytes())
        if any(got[k]!=row[k] for k in ('bytes','sha256','git_blob')):raise ValueError('snapshot bytes differ')
    if len(record['archives'])!=2 or [a['label'] for a in record['archives']]!=['G0002','G0003']:
        raise ValueError('both actual archive populations required')
    if not record['source_identity'] or not record['checks'] or not record['commands']:
        raise ValueError('A3 source, actual checks or commands absent')
    archive_path=folder/(stage+'.fixture.zip');raw=archive_path.read_bytes();declared=record['retained_fixture']
    if declared['name']!=archive_path.name or any(digest(raw)[k]!=declared[k] for k in ('bytes','sha256','git_blob')):
        raise ValueError('actual retained fixture archive differs')
    index=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if archive.testzip() is not None:raise ValueError('corrupt retained A3 fixture')
        names=set()
        for member in archive.infolist():
            p=PurePosixPath(member.filename)
            if member.filename in names or p.is_absolute() or '..' in p.parts or member.is_dir() or stat.S_ISLNK(member.external_attr>>16):
                raise ValueError('unsafe retained A3 fixture member')
            names.add(member.filename);index.append({'path':member.filename,**digest(archive.read(member))})
    return {'stage':stage,'record':digest(record_path.read_bytes()),'archive':digest(raw),
            'snapshot_count':len(snapshots),'archive_members':index,'archive_member_count':len(index),
            'archive_member_bytes':sum(r['bytes'] for r in index),'original_check_count':len(record['checks']),
            'terminal_result':'PROSPECTIVE_COMPLETE_A3_EPISODE_RETAINED_PENDING_INDEPENDENT_RECEIVING'}


def capture_original_command(original_run,streams,calls,active):
    """Pass exact arguments/result through; retain original full command streams."""
    def captured_run(argv,cwd,data=None):
        input_bytes=data
        index=len(calls)+1;folder=streams/f'{index:04d}';folder.mkdir(mode=0o700)
        argv_strings=[str(x) for x in argv]
        item={'index':index,'stage':active['stage'],'phase':active.get('phase'),'argv':argv_strings,'cwd':str(cwd),
              'input':None if input_bytes is None else digest(input_bytes),'started_ns':time.time_ns()}
        calls.append(item)
        if input_bytes is not None:write_new(folder/'stdin.bin',input_bytes)
        write_json(folder/'INTENT.json',item)
        try:
            result=original_run(argv,cwd,data)
        except BaseException as exc:
            item.update(exception_type=type(exc).__name__,exception_text=str(exc),ended_ns=time.time_ns())
            for name in ('stdout','stderr'):
                raw=getattr(exc,name,None)
                if raw is not None:
                    if isinstance(raw,str):raw=raw.encode()
                    write_new(folder/(name+'.partial.bin'),raw)
                    item[name+'_partial']=digest(raw)
            write_json(folder/'EXCEPTION.json',item)
            raise
        write_new(folder/'stdout.bin',result.stdout);write_new(folder/'stderr.bin',result.stderr)
        item.update(exit_code=result.returncode,stdout=digest(result.stdout),stderr=digest(result.stderr),ended_ns=time.time_ns())
        write_json(folder/'RETURN.json',item)
        return result
    return captured_run


def execute(source, output):
    binding=host_binding(source,output)
    pre=json.loads((output/'PREFLIGHT.json').read_text())
    if any(pre[k]!=binding[k] for k in ('run_id','workflow_commit','source_commit','source_tree','helper','episode')):
        raise ValueError('execution substituted the preflight binding')
    if digest((output/'SOURCE_BEFORE.json').read_bytes())!=pre['source_before']:
        raise ValueError('preflight source receipt changed')
    if source_census(source)!=json.loads((output/'SOURCE_BEFORE.json').read_text()):
        raise ValueError('source/tool selection changed before actual execution')
    write_json(output/'EXECUTION_INTENT.json',{**binding,'methods':list(METHODS),'stages':list(STAGES),
       'source_preflight':digest((output/'PREFLIGHT.json').read_bytes()),'time_ns':time.time_ns()})
    evidence=output/'stage-records';evidence.mkdir(mode=0o700,exist_ok=False)
    streams=output/'command-streams';streams.mkdir(mode=0o700,exist_ok=False)
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    os.environ['PATH']='/usr/bin:/bin'
    os.environ['LC_ALL']='C'
    sys.dont_write_bytecode=True
    active={'stage':None,'case':None,'phase':None}; calls=[]; case_results=[]
    original_run=None; module=None; suite_result=None; failure=None
    out=(output/'SUITE.stdout').open('xb');err=(output/'SUITE.stderr').open('xb')
    old_stdout,old_stderr=sys.stdout,sys.stderr
    out_text=io.TextIOWrapper(out,encoding='utf-8',write_through=True)
    err_text=io.TextIOWrapper(err,encoding='utf-8',write_through=True)
    try:
        sys.stdout,sys.stderr=out_text,err_text
        spec=importlib.util.spec_from_file_location('dg18_original_a3_reader_factory',source/ORIGINAL_TEST)
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        original_run=module.command
        module.command=capture_original_command(original_run,streams,calls,active)
        episode_spec=importlib.util.spec_from_file_location('dg18_prospective_a3_episode',Path(__file__).with_name('episode.py'))
        episode=importlib.util.module_from_spec(episode_spec);episode_spec.loader.exec_module(episode)
        case_class=episode.build_case(module,evidence,lambda phase:active.update(phase=phase))
        class CaptureResult(unittest.TextTestResult):
            def startTest(self,test):
                stage=STAGES[METHODS.index(test._testMethodName)]
                active.update(stage=stage,case=test)
                case_results.append({'stage':stage,'method':test._testMethodName,'test_id':test.id(),'started_ns':time.time_ns()})
                super().startTest(test)
            def addSuccess(self,test):
                case_results[-1]['unittest_outcome']='success';super().addSuccess(test)
            def addFailure(self,test,err):
                case_results[-1]['unittest_outcome']='failure';super().addFailure(test,err)
            def addError(self,test,err):
                case_results[-1]['unittest_outcome']='error';super().addError(test,err)
            def addSkip(self,test,reason):
                case_results[-1]['unittest_outcome']='skipped';case_results[-1]['skip_reason']=reason;super().addSkip(test,reason)
            def stopTest(self,test):
                row=case_results[-1];row['ended_ns']=time.time_ns()
                repo=getattr(test,'repo',None)
                row['fixture_repository']=None if repo is None else str(repo)
                row['original_fixture_cleanup_complete']=repo is not None and not os.path.lexists(repo)
                write_json(output/'case-completions'/(row['stage']+'.json'),row)
                active.update(stage=None,case=None);super().stopTest(test)
        suite=unittest.TestSuite(case_class(method) for method in METHODS)
        suite_result=unittest.TextTestRunner(stream=err_text,verbosity=2,resultclass=CaptureResult,failfast=False).run(suite)
    except BaseException as exc:
        failure={'type':type(exc).__name__,'message':str(exc)};traceback.print_exc(file=err_text)
    finally:
        if module is not None and original_run is not None:module.command=original_run
        sys.stdout,sys.stderr=old_stdout,old_stderr
        out_text.flush();err_text.flush();out_text.close();err_text.close()
        write_json(output/'COMMAND_INDEX.json',{'commands':calls,'count':len(calls)})
        survival=process_survivorship(source/'fixtures/canonical-state-rotation');write_json(output/'FINAL_PROCESS_SURVIVORSHIP.json',survival)
        try:
            after=source_census(source);write_json(output/'SOURCE_AFTER.json',after)
            source_unchanged=after==json.loads((output/'SOURCE_BEFORE.json').read_text())
        except BaseException as exc:
            source_unchanged=False;write_json(output/'SOURCE_AFTER_ERROR.json',{'type':type(exc).__name__,'message':str(exc)})
        artifacts=[];artifact_errors=[]
        for stage in STAGES:
            try:artifacts.append(artifact_record(output,stage))
            except BaseException as exc:artifact_errors.append({'stage':stage,'type':type(exc).__name__,'message':str(exc)})
        write_json(output/'ORIGINAL_EPISODE_ARTIFACT_INDEX.json',{'stages':artifacts,'errors':artifact_errors})
        qualified=(failure is None and suite_result is not None and suite_result.wasSuccessful()
            and suite_result.testsRun==len(STAGES) and not suite_result.skipped
            and len(case_results)==len(STAGES) and all(r.get('unittest_outcome')=='success' and r['original_fixture_cleanup_complete'] for r in case_results)
            and [x['stage'] for x in case_results]==list(STAGES) and len(calls)>0 and not artifact_errors
            and source_unchanged and not survival['survivors'] and survival['all_selected_process_rows_observable'])
        result={**binding,'status':'ORIGINAL_A3_CAPTURE_COMPLETE_PENDING_INDEPENDENT_RECEIVING' if qualified else 'FAILED_OR_INCOMPLETE_PRESERVED_NO_RETRY',
            'original_case_count':len(case_results),'cases':case_results,'prospective_full_predicate_discriminator':True,
            'command_count':len(calls),'source_unchanged':source_unchanged,'artifact_errors':artifact_errors,
            'suite_exception':failure,'suite_stdout':digest((output/'SUITE.stdout').read_bytes()),
            'suite_stderr':digest((output/'SUITE.stderr').read_bytes()),'survivorship':survival,
            'award':None,'no_native_Stop_or_original_host_occurrence_claim':True}
        write_json(output/'RESULT.json',result)
    print(json.dumps({'status':result['status'],'cases':len(case_results),'commands':len(calls),'award':None},sort_keys=True))
    return 0 if qualified else 1


def finalize(source,output):
    """Retain success/failure files only; never launch or repeat an original case."""
    provider_binding(output)
    if not output.exists():
        output.mkdir(mode=0o700,exist_ok=False)
        write_json(output/'NO_PREFLIGHT_OUTPUT.json',{**CONTEXT,'status':'PREFLIGHT_DID_NOT_PRODUCE_OUTPUT','original_execution_established':False})
    safe_dir(output)
    rows=[]
    for path in sorted(output.rglob('*')):
        info=path.lstat()
        if stat.S_ISLNK(info.st_mode):raise ValueError('linked evidence output')
        if not stat.S_ISREG(info.st_mode):continue
        relative=path.relative_to(output).as_posix()
        if relative=='FINAL_MANIFEST.json':raise ValueError('finalization already occurred; no replay')
        rows.append({'path':relative,**digest(path.read_bytes())})
    write_json(output/'FINAL_MANIFEST.json',{**CONTEXT,'selection':'Complete retained output regular-file population before final manifest; contains the new full-predicate episode evidence, exact archived canary and before/after snapshots, full command/suite streams, and final cleanup/survivorship facts.',
        'members':rows,'member_count':len(rows),'member_bytes':sum(r['bytes'] for r in rows),
        'original_execution_rerun_by_finalizer':False,'award':None})
    print(json.dumps({'retained_files':len(rows),'retained_bytes':sum(r['bytes'] for r in rows),'award':None},sort_keys=True))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--step',choices=['preflight','execute','finalize'],required=True)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();source=Path(os.path.abspath(args.source));output=Path(os.path.abspath(args.output))
    if args.step=='preflight':preflight(source,output);return 0
    if args.step=='execute':return execute(source,output)
    finalize(source,output);return 0


if __name__=='__main__':
    raise SystemExit(main())
