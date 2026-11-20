#!/usr/bin/env python3
"""Exact-current full original A2 recorder. No acceptance or provider authority.
Original product/fixture imports occur only inside execute after exact hosted
first-push, source-tree, source-byte and physical-tool preflight checks.
"""
from __future__ import annotations
import argparse, ast, base64, copy, hashlib, importlib.util, io, json, os, re, stat
import subprocess, sys, time, traceback, unittest, zipfile
from pathlib import Path, PurePosixPath
SOURCE_COMMIT = '51416b2f156b341c4a5f09029e2c6ceb5b30b1e7'
SOURCE_TREE = '9c3913ceaa95f3f36b0377fe2dba4a302afcba89'
BRANCH = 'pro/dg18-a2-current-51416-20261120-02'
WORKFLOW_PATH = '.github/workflows/dg18-a2-current-capture.yml'
HELPER_PATH = 'handoff/pro-executor-results-20261115/dg18-a2-current-capture/capture.py'
ORACLE_PATH = 'handoff/pro-executor-results-20261115/dg18-a2-current-capture/a2_oracle.py'
ORIGINAL_TEST = 'fixtures/canonical-state-rotation/archive_v2_test.py'
PROJECTION_TEST = 'fixtures/canonical-state-rotation/protected_projection_v2_test.py'
NATIVE_METHOD = 'test_immutable_reader_rejects_every_changed_pointer_binding'
CONTEXT = {'schema':'dg18.original-a2-capture.v1','authority':'NONE',
           'source_commit':SOURCE_COMMIT,'source_tree':SOURCE_TREE,
           'original_criterion':2,'original_denominator':14,
           'native_Stop_OR_C02_or_N1_evidence':False,'automatic_retry':False}
ORIGINAL_METHODS = ['test_paired_native_guard_lines_preserve_exact_native_status_and_action', 'test_native_guard_profile_schema_and_mirrors_refuse_ambiguity', 'test_every_native_guard_leaf_is_in_complete_owner_and_equivalence_population', 'test_complete_pair_preservation_and_draft_without_successor', 'test_each_protected_leaf_requires_exact_owner_and_value_evidence', 'test_source_pair_and_owner_map_denominator_are_not_caller_assertions', 'test_legacy_extra_unknown_noncanonical_and_duplicate_json_fail_closed', 'test_closed_state_vocabularies_and_frontier_population', 'test_every_protected_leaf_change_is_detected_against_immutable_preimage', 'test_changed_whole_pair_with_self_consistent_metadata_is_not_equivalent', 'test_typed_history_has_complete_exact_retrieval_pointers', 'test_tc06_existing_archive_remains_when_followup_rotation_is_unavailable', 'test_rotation_transition_and_recovery_skip_only_exact_failed_allocation', 'test_native_epoch_bridge_and_recovery_with_actual_failed_receipt_token', 'test_receipt_is_external_exact_byte_bound_and_preserves_identity', 'test_safe_artifact_dependencies_are_derived_from_complete_pair', 'test_pending_boundaries_keep_unresolved_epoch_and_required_rehydration', 'test_reservation_failed_result_and_later_correct_response_do_not_consume', 'test_accepted_witness_covers_only_exact_observation_and_occurrence_scope', 'test_physical_source_selected_occurrence_prior_retry_and_refusal_are_protected', 'test_explicit_bounds_and_pure_inputs', 'test_large_typed_history_reduces_with_complete_source_retrieval', 'test_all_pending_state_vocabulary_is_closed', 'test_epoch_table_mirror_mismatch_refuses_even_with_refreshed_receipt_and_owner_hashes', 'test_api_invocations_do_not_read_write_or_spawn', 'test_review_v3_pointer_ref_binds_exact_role_and_source_controller', 'test_review_supersession_targets_are_present_and_not_self', 'test_review_supersession_cycles_refuse_after_valid_closed_targets', 'test_review_planning_actions_cannot_be_selected_and_omitted', 'test_review_compensation_subject_requires_one_existing_protected_record', 'test_review_compensation_cycles_refuse_with_existing_targets', 'test_valid_closed_relation_chains_preserve_exact_source_bound_values']


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
    selected_output = safe_dir(os.environ['RUNNER_TEMP']) / ('dg18-a2-' + run + '-1')
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
    if sorted(changed) != sorted([WORKFLOW_PATH, HELPER_PATH, ORACLE_PATH]):
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
    write_json(output/'FINAL_MANIFEST.json',{**CONTEXT,'selection':'Complete retained A2 source, original and prospective full-population observations, reversible API transcripts and deduplicated byte objects, actual native generation snapshots and command streams, original cleanup and bounded survivorship. No acceptance award.',
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
    if not re.fullmatch(r'[a-z][a-z0-9-]*', name):
        raise ValueError('unexpected original clean-root name')
    archive = destination / (name + '-' + moment + '.zip')
    rows, directories = [], []
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        for path in sorted(repo.rglob('*')):
            info = path.lstat()
            relative = path.relative_to(repo).as_posix()
            if stat.S_ISLNK(info.st_mode):
                raise ValueError('linked original A2 subject member: ' + relative)
            if stat.S_ISDIR(info.st_mode):
                directories.append({'path': relative, 'mode': oct(info.st_mode & 0o7777)})
                continue
            if not stat.S_ISREG(info.st_mode):
                raise ValueError('nonregular original A2 subject member: ' + relative)
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

# These codecs are recorder infrastructure only. They never call a product API.
def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def exact_equal(a,b):
    if type(a) is not type(b):return False
    if type(a) is dict:return set(a)==set(b) and all(exact_equal(a[k],b[k]) for k in a)
    if type(a) is list:return len(a)==len(b) and all(exact_equal(x,y) for x,y in zip(a,b))
    return a==b and (type(a) is not float or a.hex()==b.hex())


def delta(before, after, path=()):
    """Reversible exact JSON edits, with a single splice for changed list length."""
    if type(before) not in (dict,list) and exact_equal(before,after):
        return []
    if type(before) is dict and type(after) is dict:
        edits = []
        for key in sorted(set(before) - set(after)):
            edits.append({'op':'delete','path':list(path+(key,))})
        for key in sorted(set(after) - set(before)):
            edits.append({'op':'set','path':list(path+(key,)),'value':after[key]})
        for key in sorted(set(before) & set(after)):
            edits.extend(delta(before[key], after[key], path+(key,)))
        return edits
    if type(before) is list and type(after) is list:
        if len(before) == len(after):
            edits=[]
            for i,(a,b) in enumerate(zip(before,after)):
                edits.extend(delta(a,b,path+(i,)))
            return edits
        prefix=0
        while prefix < min(len(before),len(after)) and exact_equal(before[prefix],after[prefix]):
            prefix+=1
        suffix=0
        while suffix < min(len(before),len(after))-prefix and exact_equal(before[-1-suffix],after[-1-suffix]):
            suffix+=1
        return [{'op':'splice','path':list(path),'index':prefix,
                 'delete':len(before)-prefix-suffix,
                 'values':after[prefix:len(after)-suffix if suffix else len(after)]}]
    return [{'op':'set','path':list(path),'value':after}]


def apply_delta(before, edits):
    value=copy.deepcopy(before)
    for edit in edits:
        path=edit['path']
        if not path and edit['op']=='set':
            value=copy.deepcopy(edit['value']);continue
        target=value
        if edit['op']=='splice':
            for part in path:target=target[part]
            target[edit['index']:edit['index']+edit['delete']]=copy.deepcopy(edit['values'])
        else:
            for part in path[:-1]:target=target[part]
            if edit['op']=='delete':del target[path[-1]]
            elif edit['op']=='set':target[path[-1]]=copy.deepcopy(edit['value'])
            else:raise ValueError('unknown exact recorder edit')
    return value


class ApiRecorder:
    """Buffer actual outer API calls in memory; no I/O inside the pure APIs.

    JSON baselines plus reversible patches retain every exact value. Large strings
    and bytes are deduplicated as SHA-256-addressed raw objects, never discarded.
    Every input/output is frozen before returning to its original caller.
    """
    def __init__(self, active):
        self.active=active; self.depth=0; self.rows=[]; self.objects={}; self.baselines={}
        self.baseline_ids={}; self.patches=[]; self.restores=[]

    def freeze(self,value):
        if type(value) is bytes or (type(value) is str and len(value.encode('utf-8'))>1024):
            raw=value if type(value) is bytes else value.encode('utf-8')
            h=hashlib.sha256(raw).hexdigest()
            prior=self.objects.setdefault(h,raw)
            if prior!=raw:raise ValueError('content object collision')
            return {'$a2_object':h,'kind':'bytes' if type(value) is bytes else 'utf8','bytes':len(raw)}
        if value is None or type(value) in (str,bool,int,float):return value
        if isinstance(value,os.PathLike):return {'$a2_path':os.fspath(value)}
        if type(value) is tuple:return {'$a2_tuple':[self.freeze(v) for v in value]}
        if type(value) is list:return [self.freeze(v) for v in value]
        if isinstance(value,dict):
            if not all(type(k) is str for k in value):raise TypeError('nonstring API mapping key')
            return {k:self.freeze(v) for k,v in value.items()}
        raise TypeError('unsupported exact API value '+type(value).__name__)

    def encode(self, slot, value):
        frozen=self.freeze(value); raw=compact(frozen)
        if slot not in self.baselines:
            key=f'B{len(self.baselines)+1:05d}'
            self.baselines[slot]=frozen;self.baseline_ids[slot]=key
            return {'baseline':key,'initial':frozen,'json_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        base=self.baselines[slot]; edits=delta(base,frozen)
        # Codec round trips are source-qualified separately; each actual transcript
        # retains its reconstructed digest for an independent receiver to recompute.
        return {'baseline':self.baseline_ids[slot],'edits':edits,
                'json_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}

    def wrap(self, module, name, prefix):
        original=getattr(module,name); recorder=self
        def observed(*args,**kwargs):
            if recorder.depth:
                return original(*args,**kwargs)
            recorder.depth+=1
            try:
                case=recorder.active.get('case'); label=recorder.active.get('label')
                test=recorder.active.get('test');subtest=getattr(test,'_subtest',None)
                caller=sys._getframe(1)
                api=prefix+'.'+name
                bucket=recorder.active.get('bucket')
                row={'index':len(recorder.rows)+1,'case':case,'label':label,'baseline_bucket':bucket,'api':api,
                     'subtest':str(subtest) if subtest is not None else None,
                     'caller':{'file':caller.f_code.co_filename,'function':caller.f_code.co_name,'line':caller.f_lineno},
                     'started_ns':time.time_ns()}
                row['input']=recorder.encode((case,api,bucket,'input'),{'args':list(args),'kwargs':kwargs})
                recorder.rows.append(row)
                try:
                    result=original(*args,**kwargs)
                except BaseException as exc:
                    row.update(outcome='exception',exception={'module':type(exc).__module__,
                        'type':type(exc).__name__,'text':str(exc)},ended_ns=time.time_ns())
                    raise
                row.update(outcome='return',output=recorder.encode((case,api,bucket,'output'),result),ended_ns=time.time_ns())
                return result
            finally:
                recorder.depth-=1
        self.restores.append((module,name,original));setattr(module,name,observed)

    def restore(self):
        for module,name,original in reversed(self.restores):setattr(module,name,original)
        self.restores=[]

    def flush(self, output):
        if self.depth:raise ValueError('recorder must flush outside product calls')
        object_dir=output/'api-objects';object_dir.mkdir(mode=0o700,exist_ok=False)
        objects=[]
        for h,raw in sorted(self.objects.items()):
            write_new(object_dir/h,raw);objects.append({'path':'api-objects/'+h,**digest(raw)})
        write_json(output/'API_OBJECTS.json',{'objects':objects,'count':len(objects),'bytes':sum(r['bytes'] for r in objects)})
        # One JSON line per call permits bounded independent sequential receiving.
        with (output/'API_CALLS.jsonl').open('xb') as f:
            for row in self.rows:f.write(compact(row)+b'\n')
        write_json(output/'API_CODEC.json',{'schema':'dg18.a2.exact-api-transcript.v1',
            'calls':len(self.rows),'baselines':len(self.baselines),'objects':len(objects),
            'encoding':'A baseline initial value occurs in the first record for each case/API/declared baseline bucket/side. Later records contain set/delete/splice edits against that immutable baseline, not against the previous record. Each decoded JSON value has its full canonical byte length and SHA-256. $a2_object is a retained raw object; kind=utf8 decodes as UTF-8, kind=bytes retains bytes. $a2_path records an original Path argument. $a2_tuple preserves a tuple separately from a JSON list; primitive types remain exact. No environment or credentials are captured.',
            'api_depth':'Only the original outermost selected API call is recorded; recursive implementation calls are not separate test observations.',
            'writes_inside_selected_API_calls':False,'authority':'NONE','award':None})


def load_selected(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module


def preflight(source, output):
    binding=host_binding(source,output)
    output.mkdir(mode=0o700,exist_ok=False)
    write_json(output/'PREFLIGHT_INTENT.json',binding)
    census=source_census(source);write_json(output/'SOURCE_BEFORE.json',census)
    original=ast.parse((source/PROJECTION_TEST).read_text())
    klass=next(n for n in original.body if isinstance(n,ast.ClassDef) and n.name=='ProjectionV2Qualification')
    methods=[n.name for n in klass.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    if methods!=ORIGINAL_METHODS or len(methods)!=32:raise ValueError('complete original method census differs')
    write_json(output/'PREFLIGHT.json',{**binding,'status':'SOURCE_AND_HOST_QUALIFIED_ORIGINAL_EXECUTION_NOT_YET_OBSERVED',
        'source_before':digest((output/'SOURCE_BEFORE.json').read_bytes()),
        'oracle':digest(Path(__file__).with_name('a2_oracle.py').read_bytes()),
        'original_projection_methods':methods,'original_native_method':NATIVE_METHOD,
        'prospective_supplement':'Full baseline plus six-disposition extension; exact owner/payload/four-manifest-part mutations, unknown vocabulary and immutable native pointer omissions/changes. Original source and acceptance contract unchanged.',
        'reason':'Checked current CI contains successful original method logs but no retained per-mutation artifacts. Original source lacks the complete six-disposition and explicit full unknown-continuity/terminal census. This new bounded operation retains missing actual observations rather than reconstructing old execution.',
        'award':None})
    print('A2 exact source and hosted first-push preflight received; no original method executed.')


def execute(source,output):
    binding=host_binding(source,output)
    pre=json.loads((output/'PREFLIGHT.json').read_text())
    if any(pre[k]!=binding[k] for k in ('run_id','workflow_commit','source_commit','source_tree','helper')):
        raise ValueError('execution substituted preflight binding')
    if digest((output/'SOURCE_BEFORE.json').read_bytes())!=pre['source_before']:
        raise ValueError('preflight source receipt changed')
    if source_census(source)!=json.loads((output/'SOURCE_BEFORE.json').read_text()):
        raise ValueError('source or physical tool changed before execution')
    if digest(Path(__file__).with_name('a2_oracle.py').read_bytes())!=pre['oracle']:
        raise ValueError('prospective oracle changed after preflight')
    write_json(output/'EXECUTION_INTENT.json',{**binding,'source_preflight':digest((output/'PREFLIGHT.json').read_bytes()),
        'original_methods':ORIGINAL_METHODS,'original_native_method':NATIVE_METHOD,'time_ns':time.time_ns()})
    fixture_root=output/'disposable-fixtures';fixture_root.mkdir(mode=0o700,exist_ok=False)
    streams=output/'command-streams';streams.mkdir(mode=0o700,exist_ok=False)
    snapshots=output/'subject-snapshots';snapshots.mkdir(mode=0o700,exist_ok=False)
    for key in list(os.environ):
        if key.startswith('GIT_'):os.environ.pop(key)
    os.environ.update(PATH='/usr/bin:/bin',LC_ALL='C',PYTHONDONTWRITEBYTECODE='1',
        GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_NO_LAZY_FETCH='1',GIT_ALLOW_PROTOCOL='')
    sys.dont_write_bytecode=True
    active={'case':None,'test':None,'label':None,'bucket':None}; recorder=ApiRecorder(active)
    calls=[];completions=[];subjects={};live_subjects={};capture_errors=[];failure=None;results=[]
    old_run=subprocess.run;old_make=None;old_tempdir=None;A=None;oracle=None;F=None
    out=(output/'SUITE.stdout').open('x',encoding='utf-8',buffering=1)
    err=(output/'SUITE.stderr').open('x',encoding='utf-8',buffering=1)
    old_stdout,old_stderr=sys.stdout,sys.stderr
    try:
        sys.stdout,sys.stderr=out,err
        # Product/original fixture imports are confined below all above gates.
        oracle=load_selected('dg18_a2_prospective_oracle',Path(__file__).with_name('a2_oracle.py'))
        F=load_selected('dg18_a2_original_projection_tests',source/PROJECTION_TEST)
        A=load_selected('dg18_a2_original_archive_tests',source/ORIGINAL_TEST)
        old_tempdir=A.tempfile.tempdir;A.tempfile.tempdir=str(fixture_root)
        for name in ('parse_canonical_pair_v2','validate_protected_payload_v2','derive_hot_pair_v2','verify_projection_equivalence_v2'):
            recorder.wrap(F.MODULE,name,'projection')
        for name in ('prepare_canonical_draft','finalize_canonical_projection','read_canonical_generation'):
            recorder.wrap(A.M,name,'native-generation')
        old_make=A.make_subject
        def observed_subject(*args,**kwargs):
            value=old_make(*args,**kwargs);key=active['case']+'/'+value['repo'].name
            if key in subjects:raise ValueError('original subject identity repeated')
            folder=snapshots/f'{len(subjects)+1:03d}';folder.mkdir(mode=0o700)
            initial=retain_subject(value,folder,fixture_root,'initial')
            subjects[key]={'initial':initial,'folder':folder.relative_to(output).as_posix()}
            live_subjects[key]=(value,folder)
            write_json(folder/'INITIAL.json',initial);return value
        A.make_subject=observed_subject
        subprocess.run=capture_run(old_run,streams,calls,active)
        class CaptureResult(unittest.TextTestResult):
            def startTest(self,test):
                active.update(case=test.id(),test=test,label=None,bucket=None)
                row={'test_id':test.id(),'method':test._testMethodName,'started_ns':time.time_ns(),
                     'api_first':len(recorder.rows)+1}
                completions.append(row)
                if isinstance(test,A.ArchiveQualification):
                    teardown=test.tearDown
                    def observed_teardown():
                        try:
                            for key,(subject,folder) in list(live_subjects.items()):
                                if key.startswith(test.id()+'/'):
                                    terminal=retain_subject(subject,folder,fixture_root,'terminal')
                                    subjects[key]['terminal']=terminal;write_json(folder/'TERMINAL.json',terminal)
                        except BaseException as exc:
                            capture_errors.append({'type':type(exc).__name__,'text':str(exc)})
                            traceback.print_exc(file=err)
                        finally:teardown()
                    test.tearDown=observed_teardown
                super().startTest(test)
            def addSuccess(self,test):completions[-1]['outcome']='success';super().addSuccess(test)
            def addFailure(self,test,info):completions[-1]['outcome']='failure';super().addFailure(test,info)
            def addError(self,test,info):completions[-1]['outcome']='error';super().addError(test,info)
            def addSkip(self,test,reason):
                completions[-1].update(outcome='skipped',reason=reason);super().addSkip(test,reason)
            def addSubTest(self,test,subtest,info):
                if info is not None:completions[-1].setdefault('failed_subtests',[]).append(str(subtest))
                super().addSubTest(test,subtest,info)
            def stopTest(self,test):
                row=completions[-1];row.update(ended_ns=time.time_ns(),api_last=len(recorder.rows))
                if isinstance(test,A.ArchiveQualification):
                    row.update(original_base=str(test.base),original_cleanup_complete=not os.path.lexists(test.base))
                active.update(case=None,test=None,label=None,bucket=None);super().stopTest(test)
        # Native preparation enforces process-lifetime peak memory; run it before
        # retaining the much larger pure-API observation population.
        native_case=oracle.native_case(A,active,recorder)
        suite=unittest.TestSuite([A.ArchiveQualification(NATIVE_METHOD),native_case('test_complete_immutable_pointer_binding_omission_and_change')])
        results.append(unittest.TextTestRunner(stream=err,verbosity=2,resultclass=CaptureResult,failfast=False).run(suite))
        write_json(output/'NATIVE_SUPPLEMENT_OBSERVATIONS.json',oracle.NATIVE_STATE)
        suite=unittest.TestSuite([F.ProjectionV2Qualification(n) for n in ORIGINAL_METHODS])
        results.append(unittest.TextTestRunner(stream=err,verbosity=2,resultclass=CaptureResult,failfast=False).run(suite))
        active.update(case='prospective-full-A2-supplement',test=None,label=None)
        try:
            oracle.run(F,active,recorder)
        finally:
            write_json(output/'SUPPLEMENT_OBSERVATIONS.json',oracle.STATE)
            active.update(case=None,test=None,label=None,bucket=None)
    except BaseException as exc:
        failure={'type':type(exc).__name__,'text':str(exc)};traceback.print_exc(file=err)
    finally:
        subprocess.run=old_run;recorder.restore()
        if A is not None and old_make is not None:A.make_subject=old_make;A.tempfile.tempdir=old_tempdir
        sys.stdout,sys.stderr=old_stdout,old_stderr
        out.flush();err.flush();out.close();err.close()
        recorder.flush(output)
        write_json(output/'COMMAND_INDEX.json',{'count':len(calls),'commands':calls,
            'scope':'All actual delegated outer subprocess.run calls with exact arguments/stdin/full observed streams. Internal direct Popen Git-object protocol is not an extra claimed command census; complete retained Git objects and original reader results remain available.'})
        write_json(output/'ORIGINAL_METHOD_COMPLETIONS.json',{'count':len(completions),'methods':completions})
        write_json(output/'SUBJECT_OBSERVATIONS.json',{'subjects':subjects,'capture_errors':capture_errors})
        survival=process_survivorship(fixture_root);write_json(output/'FINAL_PROCESS_SURVIVORSHIP.json',survival)
        try:
            after=source_census(source);write_json(output/'SOURCE_AFTER.json',after)
            source_unchanged=after==json.loads((output/'SOURCE_BEFORE.json').read_text())
        except BaseException as exc:
            source_unchanged=False;write_json(output/'SOURCE_AFTER_ERROR.json',{'type':type(exc).__name__,'text':str(exc)})
        projection_rows=[r for r in completions if r['method'] in ORIGINAL_METHODS]
        native_rows=[r for r in completions if r['method'] not in ORIGINAL_METHODS]
        shape=(len(projection_rows)==32 and [r['method'] for r in projection_rows]==ORIGINAL_METHODS
            and len(native_rows)==2 and len(subjects)==2 and all(set(v)=={'initial','terminal','folder'} for v in subjects.values())
            and all(r.get('original_cleanup_complete') is True for r in native_rows))
        supplement_ok=oracle is not None and oracle.STATE.get('status')=='ALL_DECLARED_A2_OBSERVATIONS_RETAINED'
        native_ok=oracle is not None and oracle.NATIVE_STATE.get('status')=='ALL_NATIVE_POINTER_OBSERVATIONS_RETAINED'
        qualified=(failure is None and not capture_errors and len(results)==2 and all(r.wasSuccessful() and not r.skipped for r in results)
            and all(r.get('outcome')=='success' and not r.get('failed_subtests') for r in completions)
            and shape and supplement_ok and native_ok and source_unchanged and calls
            and all(type(r.get('exit_code')) is int for r in calls) and not survival['survivors'] and survival['all_selected_process_rows_observable'])
        result={**binding,'status':'ORIGINAL_A2_CAPTURE_COMPLETE_PENDING_INDEPENDENT_RECEIVING' if qualified else 'FAILED_OR_INCOMPLETE_PRESERVED_NO_RETRY',
            'original_methods_observed':len(projection_rows),'native_methods_observed':len(native_rows),
            'whole_population_shape':shape,'supplement_observations_complete':supplement_ok,'native_pointer_observations_complete':native_ok,
            'api_calls':len(recorder.rows),'outer_commands':len(calls),'source_unchanged':source_unchanged,
            'suite_exception':failure,'capture_errors':capture_errors,'survivorship':survival,'award':None}
        write_json(output/'RESULT.json',result)
    print(json.dumps({'status':result['status'],'API_calls':len(recorder.rows),'commands':len(calls),'award':None},sort_keys=True))
    return 0 if qualified else 1


if __name__=='__main__':
    raise SystemExit(main())
