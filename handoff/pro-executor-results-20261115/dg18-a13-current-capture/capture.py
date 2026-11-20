#!/usr/bin/env python3
"""Retain exactly two original A13 fixture methods; confer no acceptance authority.

The immutable product, original worker, selected methods and assertions are unchanged.
Only transport capture and existing fixture-retention switches are added.
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
BRANCH = 'pro/dg18-a13-current-51416-20261120-01'
WORKFLOW_PATH = '.github/workflows/dg18-a13-current-capture.yml'
HELPER_PATH = 'handoff/pro-executor-results-20261115/dg18-a13-current-capture/capture.py'
ORIGINAL_TEST = 'fixtures/canonical-state-rotation/claim_transaction_test.py'
CASES = (
    ('CompleteOwnerDiscriminators',
     'test_complete_marker_pointer_receipt_currentness_table',
     'complete-reader-matrix'),
    ('NativeResumeDiscriminators',
     'test_native_ancestor_archive_ref_drift_is_fenced_by_real_pointer_cas',
     'native-ancestor-archive-cas-drift'),
)
STAGES = tuple(case[2] for case in CASES)
METHODS = tuple(case[1] for case in CASES)
CONTEXT = {'schema': 'dg18.original-a13-capture.v1', 'authority': 'NONE',
           'source_commit': SOURCE_COMMIT, 'source_tree': SOURCE_TREE,
           'original_criterion': 13, 'original_denominator': 14,
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
    selected_output = safe_dir(os.environ['RUNNER_TEMP']) / ('dg18-a13-' + run + '-1')
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
    if sorted(changed) != sorted([WORKFLOW_PATH, HELPER_PATH]):
        raise ValueError('publication contains unreviewed paths')
    if git(packet, 'status', '--porcelain=v1', '--untracked-files=all'):
        raise ValueError('workflow checkout changed')
    return {**CONTEXT, 'run_id': int(run), 'attempt': 1,
            'workflow_commit': workflow_commit, 'workflow_tree': actual[1],
            'workflow_parent': SOURCE_COMMIT, 'workflow_changed_paths': changed,
            'source_path': str(source), 'output_path': str(selected_output),
            'helper': digest(Path(__file__).read_bytes()), 'host_predicates': expected}


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
             'fixtures/controller-initialization/author_checkpoint.py'}
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
    write_json(output/'PREFLIGHT.json',{**binding,'status':'QUALIFIED_FOR_DECLARED_ORDINARY_A13_FIXTURES',
       'source_before':digest((output/'SOURCE_BEFORE.json').read_bytes()),
       'cases':list(CASES),'methods':list(METHODS),
       'retention_switches':{'R0039_CLAIM_EVIDENCE_DIR':'stage-records','R0039_CLAIM_RETAIN_ARTIFACTS':'1'},
       'fresh_original_execution_reason':'Required 80-row matrix and ancestor-drift fixture records unavailable in the checked sources; currentCI44655969487 artifact census total_count0. This is a fresh disposable control execution, not historical replay or a genuine native event.',
       'award':None})
    print('A13 exact source/preflight received; original cases have not executed.')


def matrix_shape(record):
    """Receive all original rows without changing their source-defined oracle."""
    expected_population = {
        (marker, pointer, receipt)
        for marker in ('absent', 'valid', 'malformed', 'wrong-controller')
        for pointer in ('absent', 'valid', 'malformed', 'wrong-schema')
        for receipt in ('absent', 'exact-v2', 'exact-v3', 'stale', 'mismatched')}
    rows = record['cases']
    labels = [(r['marker'], r['pointer'], r['receipt']) for r in rows]
    if record['case_count'] != 80 or len(rows) != 80 or set(labels) != expected_population:
        raise ValueError('original matrix population incomplete, duplicated or substituted')
    positives = []
    for row, label in zip(rows, labels):
        marker, pointer, receipt = label
        legacy = marker == pointer == 'absent'
        expected = ((legacy and receipt == 'exact-v2') or
                    (marker == pointer == 'valid' and receipt == 'exact-v3'))
        if row['expected_current'] is not expected or type(row['exit_code']) is not int:
            raise ValueError('original matrix expectation or exit substituted')
        if (row['exit_code'] == 0) != expected or row['refs_before'] != row['refs_after']:
            raise ValueError('original matrix outcome or read-only authority invariant failed')
        if not isinstance(row['stdout'], str) or not isinstance(row['stderr'], str):
            raise ValueError('original matrix full text streams missing')
        if expected:
            positives.append(label)
    return {'status': 'COMPLETE_ORIGINAL_80_ROW_MATRIX', 'row_count': 80,
            'positive_rows': positives, 'negative_rows': 78,
            'legacy_positive_scope': 'Both marker and pointer absent with original exact-v2 receipt; preserves the original pre-migration compatibility oracle, not migrated-root fallback authority.'}


def ancestor_shape(record):
    """Index the original real-CAS refusal; confer no native occurrence authority."""
    ancestor = 'refs/implementaudit/state-archives/transaction-test/G0002'
    if record['deleted_ancestor'] != ancestor:
        raise ValueError('original deleted ancestor substituted')
    old = record['old_oid']
    if not isinstance(old, str) or not re.fullmatch('[0-9a-f]{40}', old):
        raise ValueError('original ancestor object identity missing')
    if record['publication_guards'].get(ancestor) != old:
        raise ValueError('real owner CAS did not retain exact ancestor guard')
    rows = record['after']['refs']
    pairs = [row.split() for row in rows]
    if any(len(pair) != 2 for pair in pairs):
        raise ValueError('malformed original after-ref snapshot')
    refs = dict(pairs)
    if len(refs) != len(rows) or ancestor in refs:
        raise ValueError('ancestor not actually absent or duplicate original ref')
    for field in ('pointer_token', 'invalidation_token'):
        token = record['source'][field]
        if not isinstance(token, str) or token.count('@') != 1:
            raise ValueError('original source token malformed')
        ref, oid = token.split('@')
        if not ref.startswith('refs/implementaudit/') or not re.fullmatch('[0-9a-f]{40}', oid) or refs.get(ref) != oid:
            raise ValueError('original prior pointer/invalidation was not preserved')
    forbidden = 'refs/implementaudit/continuity-receipts/transaction-test/G0003'
    if forbidden in refs:
        raise ValueError('failed ancestor guard nevertheless minted successor receipt')
    return {'status': 'ORIGINAL_REAL_CAS_REFUSED_ANCESTOR_DRIFT',
            'deleted_ancestor': ancestor, 'old_oid': old,
            'prior_pointer_and_invalidation_preserved': True,
            'successor_receipt_absent': True,
            'terminal_scope': 'STOP with missing retained ancestor; not currentness, native-boundary authentication or C02 adjudication.'}


def artifact_record(output, stage):
    folder = output/'stage-records'
    record_path = folder/(stage+'.json')
    record = json.loads(record_path.read_text())
    archive_path = folder/(stage+'.fixture.zip')
    raw = archive_path.read_bytes()
    declared = record['retained_fixture']
    if declared['name'] != archive_path.name or declared['bytes'] != len(raw) or declared['sha256'] != digest(raw)['sha256']:
        raise ValueError('original retained fixture descriptor differs: '+stage)
    if not record.get('source_identity'):
        raise ValueError('original fixture source record absent: '+stage)
    if stage == 'complete-reader-matrix':
        terminal = matrix_shape(record)
    elif stage == 'native-ancestor-archive-cas-drift':
        terminal = ancestor_shape(record)
    else:
        raise ValueError('undeclared original case')
    index=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if archive.testzip() is not None:
            raise ValueError('corrupt original fixture archive: '+stage)
        names=set()
        for item in archive.infolist():
            path=PurePosixPath(item.filename)
            if item.filename in names or path.is_absolute() or '..' in path.parts or item.is_dir():
                raise ValueError('invalid original fixture archive member')
            names.add(item.filename)
            mode=(item.external_attr>>16)&0xffff
            if stat.S_ISLNK(mode):raise ValueError('linked fixture archive member')
            index.append({'path':item.filename,**digest(archive.read(item))})
    return {'stage':stage,'record':digest(record_path.read_bytes()),'archive':digest(raw),
            'archive_members':index,'archive_member_count':len(index),
            'archive_member_bytes':sum(x['bytes'] for x in index),
            'terminal_result':terminal}


def capture_original_run(original_run,streams,calls,active):
    """Pass exact arguments/result through; retain original full command streams."""
    def captured_run(argv,*,cwd,input_bytes=None):
        index=len(calls)+1;folder=streams/f'{index:04d}';folder.mkdir(mode=0o700)
        argv_strings=[str(x) for x in argv]
        item={'index':index,'stage':active['stage'],'argv':argv_strings,'cwd':str(cwd),
              'input':None if input_bytes is None else digest(input_bytes),'started_ns':time.time_ns()}
        calls.append(item)
        if input_bytes is not None:write_new(folder/'stdin.bin',input_bytes)
        write_json(folder/'INTENT.json',item)
        try:
            result=original_run(argv,cwd=cwd,input_bytes=input_bytes)
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
    if any(pre[k]!=binding[k] for k in ('run_id','workflow_commit','source_commit','source_tree','helper')):
        raise ValueError('execution substituted the preflight binding')
    if digest((output/'SOURCE_BEFORE.json').read_bytes())!=pre['source_before']:
        raise ValueError('preflight source receipt changed')
    if source_census(source)!=json.loads((output/'SOURCE_BEFORE.json').read_text()):
        raise ValueError('source/tool selection changed before actual execution')
    write_json(output/'EXECUTION_INTENT.json',{**binding,'cases':list(CASES),'methods':list(METHODS),
       'source_preflight':digest((output/'PREFLIGHT.json').read_bytes()),'time_ns':time.time_ns()})
    evidence=output/'stage-records';evidence.mkdir(mode=0o700,exist_ok=False)
    streams=output/'command-streams';streams.mkdir(mode=0o700,exist_ok=False)
    os.environ['R0039_CLAIM_EVIDENCE_DIR']=str(evidence)
    os.environ['R0039_CLAIM_RETAIN_ARTIFACTS']='1'
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    os.environ['PATH']='/usr/bin:/bin'
    os.environ['LC_ALL']='C'
    sys.dont_write_bytecode=True
    active={'stage':None,'case':None}; calls=[]; case_results=[]
    original_run=None; module=None; suite_result=None; failure=None
    out=(output/'SUITE.stdout').open('xb');err=(output/'SUITE.stderr').open('xb')
    old_stdout,old_stderr=sys.stdout,sys.stderr
    out_text=io.TextIOWrapper(out,encoding='utf-8',write_through=True)
    err_text=io.TextIOWrapper(err,encoding='utf-8',write_through=True)
    try:
        sys.stdout,sys.stderr=out_text,err_text
        spec=importlib.util.spec_from_file_location('dg18_original_a13_claim_tests',source/ORIGINAL_TEST)
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        original_run=module.run
        module.run=capture_original_run(original_run,streams,calls,active)
        class CaptureResult(unittest.TextTestResult):
            def startTest(self,test):
                stage=STAGES[METHODS.index(test._testMethodName)]
                expected_class=CASES[METHODS.index(test._testMethodName)][0]
                if type(test).__name__ != expected_class:
                    raise ValueError('selected original class substituted')
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
                fixture=getattr(test,'fixture',None)
                row['fixture_repository']=None if fixture is None else str(fixture.repo)
                row['original_fixture_cleanup_complete']=fixture is not None and not os.path.lexists(fixture.repo)
                write_json(output/'case-completions'/(row['stage']+'.json'),row)
                active.update(stage=None,case=None);super().stopTest(test)
        suite=unittest.TestSuite(getattr(module,class_name)(method) for class_name,method,_ in CASES)
        suite_result=unittest.TextTestRunner(stream=err_text,verbosity=2,resultclass=CaptureResult,failfast=False).run(suite)
    except BaseException as exc:
        failure={'type':type(exc).__name__,'message':str(exc)};traceback.print_exc(file=err_text)
    finally:
        if module is not None and original_run is not None:module.run=original_run
        sys.stdout,sys.stderr=old_stdout,old_stderr
        out_text.flush();err_text.flush();out_text.close();err_text.close()
        write_json(output/'COMMAND_INDEX.json',{'commands':calls,'count':len(calls)})
        survival=process_survivorship(evidence);write_json(output/'FINAL_PROCESS_SURVIVORSHIP.json',survival)
        try:
            after=source_census(source);write_json(output/'SOURCE_AFTER.json',after)
            source_unchanged=after==json.loads((output/'SOURCE_BEFORE.json').read_text())
        except BaseException as exc:
            source_unchanged=False;write_json(output/'SOURCE_AFTER_ERROR.json',{'type':type(exc).__name__,'message':str(exc)})
        artifacts=[];artifact_errors=[]
        for stage in STAGES:
            try:artifacts.append(artifact_record(output,stage))
            except BaseException as exc:artifact_errors.append({'stage':stage,'type':type(exc).__name__,'message':str(exc)})
        write_json(output/'ORIGINAL_CASE_ARTIFACT_INDEX.json',{'stages':artifacts,'errors':artifact_errors})
        qualified=(failure is None and suite_result is not None and suite_result.wasSuccessful()
            and suite_result.testsRun==len(STAGES) and not suite_result.skipped
            and len(case_results)==len(STAGES) and all(r.get('unittest_outcome')=='success' and r['original_fixture_cleanup_complete'] for r in case_results)
            and [x['stage'] for x in case_results]==list(STAGES)
            and all(any(c['stage']==stage for c in calls) for stage in STAGES) and not artifact_errors
            and source_unchanged and not survival['survivors'] and survival['all_selected_process_rows_observable'])
        result={**binding,'status':'ORIGINAL_A13_CAPTURE_COMPLETE_PENDING_INDEPENDENT_RECEIVING' if qualified else 'FAILED_OR_INCOMPLETE_PRESERVED_NO_RETRY',
            'original_case_count':len(case_results),'cases':case_results,
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
    write_json(output/'FINAL_MANIFEST.json',{**CONTEXT,'selection':'Complete retained output regular-file population before final manifest; contains original 80-row matrix, real ancestor-drift fixture, full command/suite streams, and final cleanup/survivorship facts.',
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
