#!/usr/bin/env python3
"""Capture the unchanged original A1 two-clean-root oracle; authority NONE.

No product or original fixture import occurs until the exclusive execute step
has received the exact source, tool and hosted first-push binding.
"""
from __future__ import annotations
import argparse
import ast
import copy
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
BRANCH = 'pro/dg18-a1-current-51416-20261120-01'
WORKFLOW_PATH = '.github/workflows/dg18-a1-current-capture.yml'
HELPER_PATH = 'handoff/pro-executor-results-20261115/dg18-a1-current-capture/capture.py'
ORIGINAL_TEST = 'fixtures/canonical-state-rotation/archive_v2_test.py'
ORIGINAL_CLASS = 'ArchiveQualification'
ORIGINAL_METHOD = 'test_two_clean_roots_produce_byte_identical_draft_and_final_files'
CONTEXT = {'schema': 'dg18.original-a1-capture.v1', 'authority': 'NONE',
           'source_commit': SOURCE_COMMIT, 'source_tree': SOURCE_TREE,
           'original_criterion': 1, 'original_denominator': 14,
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
    selected_output = safe_dir(os.environ['RUNNER_TEMP']) / ('dg18-a1-' + run + '-1')
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
             'fixtures/canonical-state-rotation/cases.json'}
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
    write_json(output/'FINAL_MANIFEST.json',{**CONTEXT,'selection':'Complete retained output before final manifest: both original clean roots, full pinned large population, all generation files/manifests, actual command streams, original cleanup and bounded survivorship. No original replay or acceptance award.',
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



PINNED_POPULATION = {'source_fixture': {'path': 'fixtures/canonical-state-rotation/v2/source.json', 'bytes': 17400, 'sha256': 'd8d07242e5052693d9da07ae1b9f88cc0cf8fbb46e19b71099e10bfd640ea266', 'git_blob': '573b4b8640eef49571cbcf7b0cd99e4ca7733fea'}, 'source_method': 'ArchiveQualification.test_two_clean_roots_produce_byte_identical_draft_and_final_files', 'original_history_repetition': 5000, 'original_history_line': 'Exact retained historical narrative.\n', 'run_root_identity': '.IMPLEMENTAUDIT/runs/r0039-fixture', 'source_pair': {'STATE': {'bytes': 197555, 'sha256': '9ab0c8d2d19b363a042c10d8fa31c51d8b2aeb4b0e98d35c040bcea2986c7be5', 'git_blob': '5e2ccc496e77729c25bb3adabf3665dff3da9e0c'}, 'ROADMAP': {'bytes': 3001, 'sha256': '7d46caa78372fba5bb9e04f03c4e3fefae43ae8885a942c8b8c6304c9a3fef35', 'git_blob': 'd9d1b657a8f439cd6706a10527b50bf691dff334'}}, 'live_bytes': 200556, 'calibration_sha256': 'b3df1ff07d18f8f5de145cf6d10f48a15f0a0416b392d0ca84567dce6d23e497', 'threshold_bytes': 131072, 'owner_rows': 222, 'scope': 'Pure data derivation from unchanged original JSON and render formula. No original runtime import or episode.'}

def preflight(source, output):
    binding = host_binding(source, output)
    output.mkdir(mode=0o700, exist_ok=False)
    write_json(output / 'PREFLIGHT_INTENT.json', binding)
    census = source_census(source)
    write_json(output / 'SOURCE_BEFORE.json', census)
    write_json(output / 'PREFLIGHT.json', {**binding,
        'status': 'QUALIFIED_FOR_DECLARED_ORIGINAL_A1_METHOD',
        'source_before': digest((output / 'SOURCE_BEFORE.json').read_bytes()),
        'original_class': ORIGINAL_CLASS, 'original_method': ORIGINAL_METHOD,
        'source_population': PINNED_POPULATION,
        'fresh_execution_reason': 'Existing retained first-migration and WFULL artifacts contain one subject each. The original complete two-clean-root generated-file populations were unavailable in checked sources; current CI retains a successful method line but no artifact. This ordinary prospective run captures the unchanged original oracle once.',
        'award': None})
    print('A1 exact source and first-push preflight received; original method not executed.')


def serialize_argument(value):
    """Record command metadata without recording inherited credentials/environment."""
    if value is None or type(value) in (bool, int, float, str):
        return value
    if isinstance(value, os.PathLike):
        return os.fspath(value)
    if isinstance(value, bytes):
        return {'type': 'bytes', **digest(value)}
    if isinstance(value, (list, tuple)):
        return [serialize_argument(v) for v in value]
    return {'type': type(value).__name__}


def capture_run(original, streams, calls, active):
    """Delegate exact subprocess.run arguments; preserve every observed full stream.

    The immutable Git-object reader also uses its own direct Popen protocol.
    Those internal streams are not relabeled as this run-command census.
    Complete retained objects/refs plus unchanged original readback cover them.
    """
    def recorded(*args, **kwargs):
        index = len(calls) + 1
        folder = streams / f'{index:05d}'
        folder.mkdir(mode=0o700)
        item = {'index': index, 'case': active['case'],
                'args': serialize_argument(args),
                'kwargs': {k: serialize_argument(v) for k, v in kwargs.items() if k != 'env'},
                'environment_values_recorded': False, 'started_ns': time.time_ns()}
        caller = sys._getframe(1)
        item['caller'] = {'file': caller.f_code.co_filename, 'function': caller.f_code.co_name, 'line': caller.f_lineno}
        calls.append(item)
        stdin = kwargs.get('input')
        if isinstance(stdin, (bytes, str)):
            raw = stdin if isinstance(stdin, bytes) else stdin.encode()
            write_new(folder / 'stdin.bin', raw)
            item['stdin'] = digest(raw)
        write_json(folder / 'INTENT.json', item)
        try:
            result = original(*args, **kwargs)
        except BaseException as exc:
            item.update(exception_type=type(exc).__name__, exception_text=str(exc), ended_ns=time.time_ns())
            for name in ('stdout', 'stderr'):
                raw = getattr(exc, name, None)
                if isinstance(raw, str):
                    raw = raw.encode()
                if isinstance(raw, bytes):
                    write_new(folder / (name + '.partial.bin'), raw)
                    item[name + '_partial'] = digest(raw)
            write_json(folder / 'EXCEPTION.json', item)
            raise
        for name in ('stdout', 'stderr'):
            raw = getattr(result, name, None)
            if isinstance(raw, str):
                raw = raw.encode()
            if isinstance(raw, bytes):
                write_new(folder / (name + '.bin'), raw)
                item[name] = digest(raw)
            else:
                item[name] = None
        item.update(exit_code=result.returncode, ended_ns=time.time_ns())
        write_json(folder / 'RETURN.json', item)
        return result
    return recorded


def retain_subject(subject, destination, fixture_root, moment):
    repo = safe_dir(subject['repo'])
    run = safe_dir(subject['run'])
    if not repo.is_relative_to(fixture_root) or not run.is_relative_to(repo):
        raise ValueError('original subject escaped exact isolated fixture root')
    name = repo.name
    if name not in {'first', 'second'}:
        raise ValueError('unexpected original clean-root name')
    archive = destination / (name + '-' + moment + '.zip')
    rows, directories = [], []
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        for path in sorted(repo.rglob('*')):
            info = path.lstat()
            relative = path.relative_to(repo).as_posix()
            if stat.S_ISLNK(info.st_mode):
                raise ValueError('linked original A1 subject member: ' + relative)
            if stat.S_ISDIR(info.st_mode):
                directories.append({'path': relative, 'mode': oct(info.st_mode & 0o7777)})
                continue
            if not stat.S_ISREG(info.st_mode):
                raise ValueError('nonregular original A1 subject member: ' + relative)
            raw = path.read_bytes()
            after = path.lstat()
            stable_fields = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
            if any(getattr(after, key) != getattr(info, key) for key in stable_fields):
                raise ValueError('original subject member changed during capture')
            target.writestr(relative, raw)
            rows.append({'path': relative, 'mode': oct(info.st_mode & 0o7777), **digest(raw)})
    return {'name': name, 'moment': moment, 'repository': str(repo),
            'run_root_identity': run.relative_to(repo).as_posix(),
            'archive': {'path': archive.name, **digest(archive.read_bytes())},
            'members': rows, 'member_count': len(rows), 'member_bytes': sum(r['bytes'] for r in rows),
            'directories': directories,
            'original_predecessor': copy.deepcopy(subject['predecessor']),
            'source': {r: digest(subject['source'][i]) for i, r in enumerate(('STATE', 'ROADMAP'))}}


def qualify_two_roots(subjects, prepared, finalized, reads):
    """Check retained A1 shape and whole-file populations; grant no award."""
    if set(subjects) != {'first', 'second'} or set(prepared) != {'first', 'second'}:
        raise ValueError('A1 must retain exactly the two original roots and preparations')
    if set(finalized) != {'first', 'second'}:
        raise ValueError('A1 must retain both original finalizations')
    populations = {}
    for name in ('first', 'second'):
        states = subjects[name]
        if set(states) != {'initial', 'terminal'}:
            raise ValueError('both complete initial and terminal subject snapshots are required')
        initial, terminal = states['initial'], states['terminal']
        if initial['source'] != PINNED_POPULATION['source_pair'] or terminal['source'] != initial['source']:
            raise ValueError('source population differs from the pinned original large input')
        if initial['run_root_identity'] != PINNED_POPULATION['run_root_identity'] or terminal['run_root_identity'] != initial['run_root_identity']:
            raise ValueError('original fixture run identity differs')
        if initial['repository'] == subjects['second' if name == 'first' else 'first']['initial']['repository']:
            raise ValueError('two clean roots alias the same repository')
        prefix = initial['run_root_identity'] + '/state-generations/'
        if any(r['path'].startswith(prefix) for r in initial['members']):
            raise ValueError('initial original root already contained a generation')
        population = {r['path'][len(prefix):]: {k: r[k] for k in ('bytes', 'sha256', 'git_blob')}
                      for r in terminal['members'] if r['path'].startswith(prefix)}
        expected = {'G0002/' + n for n in ('STATE.md', 'ROADMAP.md', 'protected-state.json', 'archive-manifest.json', 'generation-manifest.json')}
        expected |= {'G0002/draft/' + n for n in ('STATE.md', 'ROADMAP.md', 'protected-state.json', 'draft-manifest.json')}
        if set(population) != expected:
            raise ValueError('complete original draft/final file population differs')
        original = prepared[name]
        if original['triggered'] is not True or original['generation_id'] != 'G0002':
            raise ValueError('original large population did not prepare G0002')
        if (original['source_state_sha256'] != PINNED_POPULATION['source_pair']['STATE']['sha256']
                or original['source_roadmap_sha256'] != PINNED_POPULATION['source_pair']['ROADMAP']['sha256']
                or original['calibration']['population_sha256'] != PINNED_POPULATION['calibration_sha256']
                or original['measurement']['live_bytes_before'] != PINNED_POPULATION['live_bytes']):
            raise ValueError('actual prepared source/calibration differs')
        pointer = finalized[name]['pointer']
        if pointer['projection_generation_id'] != 'G0002':
            raise ValueError('final generation substituted')
        for component, key in (('STATE.md', 'state_sha256'), ('ROADMAP.md', 'roadmap_sha256'),
                               ('protected-state.json', 'protected_manifest_sha256'), ('archive-manifest.json', 'archive_manifest_sha256')):
            if pointer[key] != population['G0002/' + component]['sha256']:
                raise ValueError('original pointer body binding differs: ' + component)
        root_reads = [r for r in reads if r['root'] == name]
        if len(root_reads) != 2 or any(r['pointer'] != pointer or r['state']['sha256'] != pointer['state_sha256']
                or r['roadmap']['sha256'] != pointer['roadmap_sha256'] for r in root_reads):
            raise ValueError('both original finalizer/readback calls must be exact')
        if any(r['protected_owner_rows'] != 222 or r['archive_entries'] != 6 for r in root_reads):
            raise ValueError('complete manifest owner/archive population differs')
        populations[name] = population
    if populations['first'] != populations['second']:
        raise ValueError('the complete original two-root output populations differ')
    return {'status': 'COMPLETE_ORIGINAL_TWO_ROOT_BYTES_RETAINED_PENDING_INDEPENDENT_RECEIVING',
            'clean_roots': 2, 'generated_files_per_root': 9, 'complete_populations': populations,
            'pinned_source_population': PINNED_POPULATION, 'original_reads': reads,
            'authority': 'NONE', 'award': None}


def execute(source, output):
    binding = host_binding(source, output)
    pre = json.loads((output / 'PREFLIGHT.json').read_text())
    if any(pre[k] != binding[k] for k in ('run_id', 'workflow_commit', 'source_commit', 'source_tree', 'helper')):
        raise ValueError('execution substituted its preflight binding')
    if digest((output / 'SOURCE_BEFORE.json').read_bytes()) != pre['source_before']:
        raise ValueError('preflight source receipt changed')
    if source_census(source) != json.loads((output / 'SOURCE_BEFORE.json').read_text()):
        raise ValueError('source or physical tool population changed before execution')
    write_json(output / 'EXECUTION_INTENT.json', {**binding,
        'original_class': ORIGINAL_CLASS, 'original_method': ORIGINAL_METHOD,
        'source_preflight': digest((output / 'PREFLIGHT.json').read_bytes()), 'time_ns': time.time_ns()})
    fixture_root = output / 'disposable-fixtures'
    fixture_root.mkdir(mode=0o700, exist_ok=False)
    streams = output / 'command-streams'
    streams.mkdir(mode=0o700, exist_ok=False)
    evidence = output / 'subject-snapshots'
    evidence.mkdir(mode=0o700, exist_ok=False)
    for key in list(os.environ):
        if key.startswith('GIT_'):
            os.environ.pop(key)
    os.environ.update(PATH='/usr/bin:/bin', LC_ALL='C', PYTHONDONTWRITEBYTECODE='1',
                      GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null')
    sys.dont_write_bytecode = True
    active = {'case': None}
    calls, reads, completions, capture_errors = [], [], [], []
    subjects, prepared, finalized, live_subjects = {}, {}, {}, {}
    module = None
    old_run = subprocess.run
    old_methods = {}
    old_tempdir = None
    failure = None
    suite_result = None
    out = io.TextIOWrapper((output / 'SUITE.stdout').open('xb'), encoding='utf-8', write_through=True)
    err = io.TextIOWrapper((output / 'SUITE.stderr').open('xb'), encoding='utf-8', write_through=True)
    old_stdout, old_stderr = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = out, err
        spec = importlib.util.spec_from_file_location('dg18_original_a1_archive_tests', source / ORIGINAL_TEST)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        old_tempdir = module.tempfile.tempdir
        module.tempfile.tempdir = str(fixture_root)
        old_methods = {'make_subject': module.make_subject,
                       'prepare': module.M.prepare_canonical_draft,
                       'finalize': module.M.finalize_canonical_projection,
                       'read': module.M.read_canonical_generation}
        def observe_subject(*args, **kwargs):
            result = old_methods['make_subject'](*args, **kwargs)
            name = result['repo'].name
            if name in subjects:
                raise ValueError('original root repeated')
            subjects[name] = {'initial': retain_subject(result, evidence, fixture_root, 'initial')}
            live_subjects[name] = result
            write_json(evidence / (name + '-initial.json'), subjects[name]['initial'])
            return result
        def observe_prepare(*args, **kwargs):
            result = old_methods['prepare'](*args, **kwargs)
            name = Path(args[0]).name
            if name in prepared:
                raise ValueError('original preparation repeated')
            prepared[name] = copy.deepcopy(result)
            write_json(evidence / (name + '-prepared.json'), result)
            return result
        def observe_finalize(*args, **kwargs):
            result = old_methods['finalize'](*args, **kwargs)
            name = Path(args[0]).name
            if name in finalized:
                raise ValueError('original finalization repeated')
            finalized[name] = {'pointer': copy.deepcopy(result['pointer']),
                               'generation_dir': str(result['generation_dir']),
                               'transition': copy.deepcopy(args[3])}
            write_json(evidence / (name + '-finalized.json'), finalized[name])
            return result
        def observe_read(*args, **kwargs):
            result = old_methods['read'](*args, **kwargs)
            item = {'index': len(reads) + 1, 'root': Path(args[0]).name,
                    'pointer': copy.deepcopy(args[2]),
                    'state': digest(result['state_bytes']), 'roadmap': digest(result['roadmap_bytes']),
                    'state_path': str(result['state_path']), 'roadmap_path': str(result['roadmap_path']),
                    'protected_owner_rows': len(result['protected_manifest']['PRESERVED_PAYLOAD']['owner_map']),
                    'archive_entries': len(result['archive_manifest']['entries'])}
            reads.append(item)
            write_json(evidence / f'read-{len(reads):02d}.json', item)
            return result
        module.make_subject = observe_subject
        module.M.prepare_canonical_draft = observe_prepare
        module.M.finalize_canonical_projection = observe_finalize
        module.M.read_canonical_generation = observe_read
        subprocess.run = capture_run(old_run, streams, calls, active)
        class CaptureResult(unittest.TextTestResult):
            def startTest(self, test):
                if type(test).__name__ != ORIGINAL_CLASS or test._testMethodName != ORIGINAL_METHOD:
                    raise ValueError('original method selection substituted')
                active['case'] = test.id()
                completions.append({'test_id': test.id(), 'method': test._testMethodName, 'started_ns': time.time_ns()})
                original_teardown = test.tearDown
                def observed_teardown():
                    try:
                        for name, subject in live_subjects.items():
                            terminal = retain_subject(subject, evidence, fixture_root, 'terminal')
                            subjects[name]['terminal'] = terminal
                            write_json(evidence / (name + '-terminal.json'), terminal)
                    except BaseException as exc:
                        capture_errors.append({'type': type(exc).__name__, 'message': str(exc)})
                        traceback.print_exc(file=err)
                    finally:
                        original_teardown()
                test.tearDown = observed_teardown
                super().startTest(test)
            def addSuccess(self, test):
                completions[-1]['unittest_outcome'] = 'success'
                super().addSuccess(test)
            def addFailure(self, test, info):
                completions[-1]['unittest_outcome'] = 'failure'
                super().addFailure(test, info)
            def addError(self, test, info):
                completions[-1]['unittest_outcome'] = 'error'
                super().addError(test, info)
            def addSkip(self, test, reason):
                completions[-1].update(unittest_outcome='skipped', skip_reason=reason)
                super().addSkip(test, reason)
            def stopTest(self, test):
                row = completions[-1]
                row['ended_ns'] = time.time_ns()
                row['original_base'] = str(getattr(test, 'base', ''))
                row['original_cleanup_complete'] = hasattr(test, 'base') and not os.path.lexists(test.base)
                write_json(output / 'ORIGINAL_METHOD_COMPLETION.json', row)
                active['case'] = None
                super().stopTest(test)
        suite = unittest.TestSuite([getattr(module, ORIGINAL_CLASS)(ORIGINAL_METHOD)])
        suite_result = unittest.TextTestRunner(stream=err, verbosity=2, resultclass=CaptureResult, failfast=False).run(suite)
    except BaseException as exc:
        failure = {'type': type(exc).__name__, 'message': str(exc)}
        traceback.print_exc(file=err)
    finally:
        subprocess.run = old_run
        if module is not None and old_methods:
            module.make_subject = old_methods['make_subject']
            module.M.prepare_canonical_draft = old_methods['prepare']
            module.M.finalize_canonical_projection = old_methods['finalize']
            module.M.read_canonical_generation = old_methods['read']
            module.tempfile.tempdir = old_tempdir
        sys.stdout, sys.stderr = old_stdout, old_stderr
        out.flush(); err.flush(); out.close(); err.close()
        write_json(output / 'COMMAND_INDEX.json', {'count': len(calls), 'commands': calls,
            'scope': 'Actual subprocess.run calls with exact delegated arguments and observed full streams. Direct internal Popen Git-object-reader protocol is not claimed as captured.'})
        write_json(output / 'SUBJECT_OBSERVATIONS.json', {'subjects': subjects, 'prepared': prepared,
                   'finalized': finalized, 'reads': reads, 'capture_errors': capture_errors})
        try:
            result_shape = qualify_two_roots(subjects, prepared, finalized, reads)
            write_json(output / 'COMPLETE_TWO_ROOT_COMPARISON.json', result_shape)
            shape_ok = True
        except BaseException as exc:
            shape_ok = False
            write_json(output / 'TWO_ROOT_COMPARISON_FAILURE.json', {'type': type(exc).__name__, 'message': str(exc)})
        survival = process_survivorship(fixture_root)
        write_json(output / 'FINAL_PROCESS_SURVIVORSHIP.json', survival)
        try:
            after = source_census(source)
            write_json(output / 'SOURCE_AFTER.json', after)
            source_unchanged = after == json.loads((output / 'SOURCE_BEFORE.json').read_text())
        except BaseException as exc:
            source_unchanged = False
            write_json(output / 'SOURCE_AFTER_ERROR.json', {'type': type(exc).__name__, 'message': str(exc)})
        qualified = (failure is None and not capture_errors and suite_result is not None and suite_result.wasSuccessful()
                     and suite_result.testsRun == 1 and not suite_result.skipped and shape_ok and len(completions) == 1
                     and completions[0].get('unittest_outcome') == 'success' and completions[0]['original_cleanup_complete']
                     and calls and all(type(c.get('exit_code')) is int for c in calls)
                     and source_unchanged and not survival['survivors'] and survival['all_selected_process_rows_observable'])
        result = {**binding, 'status': 'ORIGINAL_A1_CAPTURE_COMPLETE_PENDING_INDEPENDENT_RECEIVING' if qualified else 'FAILED_OR_INCOMPLETE_PRESERVED_NO_RETRY',
                  'original_method': ORIGINAL_METHOD, 'original_method_completions': completions,
                  'original_clean_roots': len(subjects), 'original_readbacks': len(reads), 'command_count': len(calls),
                  'source_unchanged': source_unchanged, 'complete_two_root_shape': shape_ok,
                  'capture_errors': capture_errors, 'suite_exception': failure, 'survivorship': survival,
                  'suite_stdout': digest((output / 'SUITE.stdout').read_bytes()),
                  'suite_stderr': digest((output / 'SUITE.stderr').read_bytes()), 'award': None}
        write_json(output / 'RESULT.json', result)
    print(json.dumps({'status': result['status'], 'roots': len(subjects), 'commands': len(calls), 'award': None}, sort_keys=True))
    return 0 if qualified else 1


if __name__ == "__main__":
    raise SystemExit(main())
