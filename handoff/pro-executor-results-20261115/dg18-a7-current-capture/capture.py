#!/usr/bin/env python3
"""One original current ordinary A7 campaign. Original actors run only after exact hosted/source gates."""
from __future__ import annotations
import argparse,ast,copy,hashlib,importlib.util,io,json,os,re,stat,subprocess,sys,time,traceback,unittest,zipfile
from pathlib import Path,PurePosixPath
SOURCE_COMMIT='51416b2f156b341c4a5f09029e2c6ceb5b30b1e7'
SOURCE_TREE='9c3913ceaa95f3f36b0377fe2dba4a302afcba89'
BRANCH='pro/dg18-a7-current-51416-20261120-01'
WORKFLOW_PATH='.github/workflows/dg18-a7-current-capture.yml'
HELPER_PATH='handoff/pro-executor-results-20261115/dg18-a7-current-capture/capture.py'
ORIGINAL_TEST='fixtures/canonical-state-rotation/claim_transaction_test.py'
CONTEXT={'schema':'dg18.original-a7-current-capture.v1','authority':'NONE','source_commit':SOURCE_COMMIT,
    'source_tree':SOURCE_TREE,'original_criterion':7,'original_denominator':14,
    'native_Stop_OR_C02_or_N1_evidence':False,'automatic_retry':False}
PINNED_TOOLS=[{'bytes': 8020928, 'git_blob': '6d235376c83abecfebea20ec46b105c0d21c086c', 'mode': '0o755', 'path': '/usr/bin/python3.12', 'sha256': 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f', 'uid': 0}, {'bytes': 4640384, 'git_blob': '2ead47b68ed7b31526a837f186d5d3a4c5579820', 'mode': '0o755', 'path': '/usr/bin/git', 'sha256': '08ca4d2ee4d8915e86f1faaa52603752507c57af1d16d451dec9992bc9b6d801', 'uid': 0}, {'bytes': 1446024, 'git_blob': '161fddc2f2bdede1fb24ba7739a79c16c9ed6523', 'mode': '0o755', 'path': '/usr/bin/bash', 'sha256': 'bc5945feb8bd26203ebfafea5ce1878bb2e32cb8fb50ab7ae395cfb1e1aaaef1', 'uid': 0}]

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
    selected_output = safe_dir(os.environ['RUNNER_TEMP']) / ('dg18-a7-' + run + '-1')
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
    exact = {ORIGINAL_TEST, 'fixtures/controller-initialization/author_checkpoint.py'}
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
    if len(rows) != 46 or not exact.issubset({row['path'] for row in rows}):
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
    if tools != PINNED_TOOLS:
        raise ValueError('physical executable differs from externally retained exact body')
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
    write_json(output/'FINAL_MANIFEST.json',{**CONTEXT,'selection':'Complete retained output before final manifest: one genuine current small-root campaign, actual predecessor/receipt and paired readbacks, full raw before/after refs/objects/files, actual command streams, original cleanup and bounded survivorship. No original replay or acceptance award.',
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


def qualify_no_trigger(o):
    checks=[]
    def check(name,value):checks.append({'id':name,'passed':bool(value)})
    before=o.get('before',{});after=o.get('after',{})
    pair=o.get('pair_before',{});prepared=o.get('prepared',{})
    total=sum(v.get('bytes',0) for v in pair.values())
    check('one-complete-current-campaign',all(type(o.get(k)) is int and o[k]==1 for k in ('campaigns','prepare_calls','owner_cli_calls')))
    check('exact-source-copy-and-tool-bodies',o.get('source_unchanged') is True and o.get('copied_runtime_exact') is True and o.get('tools_match_external_bodies') is True)
    check('ordinary-byte-route-only',o.get('native_input') is False and o.get('tokenizer_input') is False)
    check('both-ordinary-files-below-threshold',set(pair)=={'STATE','ROADMAP'} and 0<total<131072)
    check('exact-helper-no-trigger',canonical(prepared)==canonical({'triggered':False,'reason':'BELOW_FROZEN_BYTE_THRESHOLD',
        'live_bytes':total,'archive_writes':0,'model_calls':0,'authority_ceiling':'NO_CURRENTNESS_AUTHORITY'}))
    receipt=o.get('receipt_before')
    check('same-real-receipt-returned',isinstance(receipt,str) and bool(receipt) and o.get('receipt_after')==receipt
        and o.get('owner_result')=={'status':'NOT_TRIGGERED','receipt_token':receipt})
    check('unchanged-full-pair-and-four-readbacks',pair==o.get('pair_after')==o.get('read_before')==o.get('read_after'))
    check('same-head-tree-and-all-refs',all(before.get(k) is not None and before.get(k)==after.get(k) for k in ('head','tree','refs')))
    check('same-directory-population',before.get('directories') is not None and before.get('directories')==after.get('directories'))
    oldfiles=before.get('files',{});newfiles=after.get('files',{})
    gate='.git/implementaudit-r0039-rotation.gate'
    added=set(newfiles)-set(oldfiles)
    delta_ok=bool(oldfiles) and set(oldfiles)<=set(newfiles) and all(oldfiles[p]==newfiles[p] for p in oldfiles)
    if added:
        actual=newfiles.get(gate,{})
        delta_ok=delta_ok and added=={gate} and all(actual.get(k)==v for k,v in digest(b'\0').items()) and actual.get('mode')=='0o600'
    check('full-files-objects-preserved-only-existing-coordination-gate-allowed',delta_ok)
    check('no-owner-map-created',o.get('owner_map_before') is False and o.get('owner_map_after') is False)
    check('no-archive-generation-or-migration',o.get('canonical_paths_before')==[] and o.get('canonical_paths_after')==[])
    check('actual-currentness-and-validation',o.get('currentness_and_validation') is True)
    check('complete-raw-command-streams',o.get('all_command_streams_retained') is True)
    check('original-cleanup-complete',o.get('cleanup_complete') is True)
    survival=o.get('survivorship',{})
    check('no-selected-process-survivors-or-unavailable-rows',survival.get('survivors')==[] and survival.get('all_selected_process_rows_observable') is True)
    return {'qualified':all(r['passed'] for r in checks),'checks':checks,'authority':'NONE','award':None,
        'scope':'Current ordinary bytes-only non-trigger; authentic OR producer qualification is separate and not inferred.'}


def load_selected(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module


def preflight(source,output):
    binding=host_binding(source,output)
    output.mkdir(mode=0o700,exist_ok=False)
    write_json(output/'PREFLIGHT_INTENT.json',binding)
    census=source_census(source);write_json(output/'SOURCE_BEFORE.json',census)
    write_json(output/'PREFLIGHT.json',{**binding,'source_before':digest((output/'SOURCE_BEFORE.json').read_bytes()),
        'status':'EXACT_SOURCE_AND_HOST_RECEIVED_ORIGINAL_CAMPAIGN_NOT_YET_EXECUTED',
        'original_predicate':'Below-threshold/non-trigger campaigns retain ordinary cheap STATE/ROADMAP with no archive, model call or extra ceremony.',
        'campaign_count':1,'prepare_calls':1,'owner_cli_calls':1,'native_or_tokenizer_input':False,
        'actual_predecessor_required':True,'owner_map_created':False,'authentic_OR_requirement_supplied':False,
        'qualification_instrumentation_is_not_new_ordinary_product_ceremony':True,'award':None})
    print('A7 exact source and first-push preflight received; original campaign not executed.')


def retain_tree(root,destination,label):
    root=safe_dir(root);destination.mkdir(mode=0o700,parents=True,exist_ok=True)
    target=destination/(label+'.zip');files={};directories=[]
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(root.rglob('*')):
            info=path.lstat();relative=path.relative_to(root).as_posix()
            if stat.S_ISLNK(info.st_mode):raise ValueError('linked captured member: '+relative)
            if stat.S_ISDIR(info.st_mode):
                directories.append({'path':relative,'mode':oct(info.st_mode&0o7777)});continue
            if not stat.S_ISREG(info.st_mode):raise ValueError('nonregular captured member: '+relative)
            raw=path.read_bytes();after=path.lstat()
            fields=('st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns')
            if any(getattr(info,k)!=getattr(after,k) for k in fields):raise ValueError('captured member changed: '+relative)
            archive.writestr(relative,raw)
            files[relative]={'mode':oct(info.st_mode&0o7777),'physical':[getattr(info,k) for k in fields],**digest(raw)}
    return {'files':files,'directories':directories,'archive':{'path':str(target),**digest(target.read_bytes())}}


def refs_and_tree(repo):
    refs={}
    for row in git(repo,'for-each-ref','--format=%(refname) %(objectname)').decode().splitlines():
        name,oid=row.split();refs[name]=oid
    return {'refs':refs,'head':git(repo,'rev-parse','HEAD').decode().strip(),
        'tree':git(repo,'rev-parse','HEAD^{tree}').decode().strip()}


def snapshot(repo,destination,label):
    recorded=retain_tree(repo,destination,label)
    summary={k:v for k,v in recorded.items() if k!='archive'}
    summary.update(refs_and_tree(repo))
    write_json(destination/(label+'.json'),{**summary,'archive':recorded['archive']})
    return summary


def canonical_paths(observation):
    parts=('state-generations','state-archives')
    refs=('refs/implementaudit/state-archives/','refs/implementaudit/current-generations/',
        'refs/implementaudit/current-generation-migrations/','refs/implementaudit/generation-epochs/')
    return sorted([p for p in observation['files'] if any(part in p.split('/') for part in parts)]
        +[name for name in observation['refs'] if name.startswith(refs)])


def copied_runtime_census(fixture,expected):
    selected=[r for r in expected['source_members'] if r['path'].startswith(('skills/implementaudit/scripts/','skills/implementaudit/templates/'))]
    rows=[]
    for row in selected:
        path=fixture.repo/row['path'];safe_dir(path.parent);info=path.lstat()
        if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):raise ValueError('copied source not physical')
        item={'path':row['path'],'mode':format(stat.S_IMODE(info.st_mode)|stat.S_IFREG,'o'),**digest(path.read_bytes())}
        if item!={k:row[k] for k in ('path','mode','bytes','sha256','git_blob')}:raise ValueError('copied source mismatch: '+row['path'])
        rows.append(item)
    actual={p.relative_to(fixture.repo).as_posix() for prefix in ('skills/implementaudit/scripts','skills/implementaudit/templates')
        for p in (fixture.repo/prefix).rglob('*') if p.is_file() or p.is_symlink()}
    if actual!={r['path'] for r in rows}:raise ValueError('copied source population differs')
    return rows


def command_streams_exact(streams,calls):
    for item in calls:
        if type(item.get('exit_code')) is not int:return False
        for name in ('stdout','stderr'):
            expected=item.get(name)
            if not isinstance(expected,dict):return False
            if digest((streams/f"{item['index']:05d}"/(name+'.bin')).read_bytes())!=expected:return False
        if 'stdin' in item and digest((streams/f"{item['index']:05d}"/'stdin.bin').read_bytes())!=item['stdin']:return False
    return bool(calls)


def execute(source,output):
    binding=host_binding(source,output);pre=json.loads((output/'PREFLIGHT.json').read_text())
    if any(pre[k]!=binding[k] for k in ('run_id','workflow_commit','source_commit','source_tree','helper')):
        raise ValueError('execution substituted preflight binding')
    if digest((output/'SOURCE_BEFORE.json').read_bytes())!=pre['source_before']:raise ValueError('preflight source receipt changed')
    expected=json.loads((output/'SOURCE_BEFORE.json').read_bytes())
    if source_census(source)!=expected:raise ValueError('source/tool changed before execution')
    write_json(output/'EXECUTION_INTENT.json',{**binding,'preflight':digest((output/'PREFLIGHT.json').read_bytes()),
        'one_fresh_fixture':True,'no_historical_run_replay':True,'prepare_calls':1,'public_owner_calls':1})
    fixture_root=output/'disposable-fixtures';fixture_root.mkdir(mode=0o700,exist_ok=False)
    streams=output/'command-streams';streams.mkdir(mode=0o700,exist_ok=False)
    snapshots=output/'snapshots';snapshots.mkdir(mode=0o700,exist_ok=False)
    for key in list(os.environ):
        if key.startswith(('GIT_','IMPLEMENTAUDIT_')):os.environ.pop(key)
    os.environ.update(PATH='/usr/bin:/bin',LC_ALL='C',PYTHONDONTWRITEBYTECODE='1',
        R0039_CLAIM_EVIDENCE_DIR=str(fixture_root),GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',
        GIT_NO_LAZY_FETCH='1',GIT_ALLOW_PROTOCOL='')
    sys.dont_write_bytecode=True
    observed={'campaigns':0,'prepare_calls':0,'owner_cli_calls':0,'native_input':False,'tokenizer_input':False}
    active={'case':'INITIALIZATION'};calls=[];failure=None;fixture=None;F=None;copy_before=None
    old_run=subprocess.run;old_cwd=Path.cwd();out=(output/'CAPTURE.stdout').open('x');err=(output/'CAPTURE.stderr').open('x')
    old_stdout,old_stderr=sys.stdout,sys.stderr
    try:
        sys.stdout,sys.stderr=out,err;subprocess.run=capture_run(old_run,streams,calls,active)
        # Every original import and owner operation is below all hosted/source guards.
        F=load_selected('dg18_a7_original_claim_fixture',source/ORIGINAL_TEST)
        fixture=F.Fixture();observed['campaigns']=1
        repo=safe_dir(fixture.repo);run=safe_dir(fixture.run_root)
        if not repo.is_relative_to(fixture_root) or not run.is_relative_to(repo) or fixture.legacy_initialization:
            raise ValueError('not the exact current disposable initialization')
        os.chdir(repo)
        copy_before=copied_runtime_census(fixture,expected);write_json(output/'COPIED_RUNTIME_BEFORE.json',{'members':copy_before})
        receipt=fixture.receipt;observed['receipt_before']=receipt
        write_json(output/'GENUINE_INITIALIZATION.json',{'repo':str(repo),'run':str(run),'controller':F.CONTROLLER,
            'receipt':receipt,'claim_raw':(run/'.claimed').read_text(),'controller_raw':(run/'.controller').read_text(),
            'scope':'Actual normal fixture initialization and receipt; no live Root or native host authority.'})
        def command(label,*args):
            active['case']=label;result=fixture.claim(*args)
            if result.returncode:raise ValueError('original owner readback failed: '+label)
            return result.stdout
        def receive(label):
            checked=command(label+'-verify','--verify-resume-receipt',receipt).decode().strip()
            required=command(label+'-require','--require-current-continuity',F.CONTROLLER).decode().strip()
            if checked!=receipt or required!=receipt:raise ValueError('actual predecessor receipt changed')
            pair={}
            for role in ('STATE','ROADMAP'):
                raw=command(label+'-read-'+role,'--read-current-state',F.CONTROLLER,role,'--expected-pointer','none')
                write_new(output/(label+'-'+role+'.md'),raw);pair[role]=digest(raw)
            active['case']=label+'-validate'
            validated=F.run(['/usr/bin/bash',fixture.scripts/'validate-run-root.sh',run],cwd=repo)
            if validated.returncode:raise ValueError('original root validator refused')
            return pair,required
        observed['read_before'],_=receive('BEFORE')
        active['case']='GENUINE_PREDECESSOR_READ'
        owner=load_selected('dg18_a7_original_claim_owner',fixture.scripts/'claim-run-rotation.py')
        context=owner.discover(F.CONTROLLER);predecessor=owner.resolve_predecessor(context)
        if predecessor['receipt_ref']+'@'+predecessor['receipt_oid']!=receipt:raise ValueError('predecessor does not bind actual receipt')
        if predecessor['continuity_epoch']!='G0001' or predecessor['projection_generation_id']!='G0001':raise ValueError('unexpected initial epoch')
        write_json(output/'ACTUAL_PREDECESSOR.json',predecessor)
        absent_map=run/'a7-absent-owner-map.json';observed['owner_map_before']=os.path.lexists(absent_map)
        observed['pair_before']={role:digest((run/(role+'.md')).read_bytes()) for role in ('STATE','ROADMAP')}
        observed['before']=snapshot(repo,snapshots,'BEFORE')
        observed['canonical_paths_before']=canonical_paths(observed['before'])
        active['case']='UNCHANGED_PREPARE_CHEAP_BRANCH'
        helper=owner.projection_helper();calibration=helper.calibration_contract_v1()
        write_json(output/'PREPARE_INTENT.json',{'repo':str(repo),'run':str(run),'controller':F.CONTROLLER,
            'candidate_generation':'G0002','owner_map':str(absent_map),'predecessor':predecessor,'calibration':calibration,
            'candidate_is_not_an_allocated_epoch':True})
        observed['prepare_calls']+=1
        prepared=helper.prepare_canonical_draft(repo,run,F.CONTROLLER,'G0002',absent_map,predecessor,calibration)
        observed['prepared']=prepared;write_json(output/'PREPARE_RETURN.json',prepared)
        active['case']='ORIGINAL_CURRENT_PUBLIC_OWNER_CLI';observed['owner_cli_calls']+=1
        started=time.time_ns()
        result=fixture.claim('--rotate-canonical-state',F.CONTROLLER,'--owner-map',str(absent_map))
        observed['owner_interval']={'started_ns':started,'ended_ns':time.time_ns(),'exit_code':result.returncode}
        if result.returncode:raise ValueError('original no-trigger owner CLI refused')
        observed['owner_result']=json.loads(result.stdout);write_json(output/'OWNER_RETURN.json',observed['owner_result'])
        observed['read_after'],observed['receipt_after']=receive('AFTER')
        observed['currentness_and_validation']=True
        observed['owner_map_after']=os.path.lexists(absent_map)
        observed['pair_after']={role:digest((run/(role+'.md')).read_bytes()) for role in ('STATE','ROADMAP')}
        observed['after']=snapshot(repo,snapshots,'AFTER')
        observed['canonical_paths_after']=canonical_paths(observed['after'])
        copy_after=copied_runtime_census(fixture,expected);write_json(output/'COPIED_RUNTIME_AFTER.json',{'members':copy_after})
        observed['copied_runtime_exact']=copy_before==copy_after
    except BaseException as exc:
        failure={'type':type(exc).__name__,'text':str(exc)};traceback.print_exc(file=err)
        try:write_json(output/'FAILED_TREE_RECEIVING.json',retain_tree(fixture_root,snapshots,'FAILED_TREE'))
        except BaseException as retained:observed['failed_tree_capture_error']={'type':type(retained).__name__,'text':str(retained)}
    finally:
        os.chdir(old_cwd)
        try:
            if fixture is not None:
                active['case']='ORIGINAL_FIXTURE_CLEANUP';fixture.close()
                observed['cleanup_complete']=not os.path.lexists(fixture.repo) and not any(fixture_root.iterdir())
            else:observed['cleanup_complete']=False
        except BaseException as exc:
            observed['cleanup_complete']=False;observed['cleanup_error']={'type':type(exc).__name__,'text':str(exc)}
        subprocess.run=old_run;sys.stdout,sys.stderr=old_stdout,old_stderr
        out.flush();err.flush();out.close();err.close()
        observed['survivorship']=process_survivorship(fixture_root)
        write_json(output/'FINAL_PROCESS_SURVIVORSHIP.json',observed['survivorship'])
        observed['all_command_streams_retained']=command_streams_exact(streams,calls)
        write_json(output/'COMMAND_INDEX.json',{'count':len(calls),'commands':calls,
            'scope':'All delegated outer subprocess.run invocations in the capture process. Nested initializer subprocess calls remain bound by exact source and its actual outer command/activation output; no nested raw stream is fabricated.'})
        try:
            after_source=source_census(source);write_json(output/'SOURCE_AFTER.json',after_source)
            observed['source_unchanged']=after_source==expected
            observed['tools_match_external_bodies']=after_source['tools']==expected['tools']
        except BaseException as exc:
            observed['source_unchanged']=False;observed['source_after_error']={'type':type(exc).__name__,'text':str(exc)}
        qualification=qualify_no_trigger(observed)
        qualified=failure is None and qualification['qualified'] and 'failed_tree_capture_error' not in observed
        write_json(output/'OBSERVATIONS.json',observed)
        write_json(output/'RESULT.json',{**binding,'status':'COMPLETE_ORDINARY_A7_OBSERVATIONS_PENDING_INDEPENDENT_RECEIVING' if qualified else 'FAILED_OR_INCOMPLETE_PRESERVED_NO_RETRY',
            'failure':failure,'qualification':qualification,'authentic_OR_qualification':False,'award':None})
    print(json.dumps({'qualified_observation':qualified,'commands':len(calls),'award':None},sort_keys=True))
    return 0 if qualified else 1


if __name__=='__main__':
    raise SystemExit(main())
