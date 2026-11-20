#!/usr/bin/env python3
"""Finite prospective A12 capture. Source preparation must not call execute()."""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import stat
import subprocess
import sys
import threading
import time
import traceback
import zipfile
import zlib

SOURCE_COMMIT = '51416b2f156b341c4a5f09029e2c6ceb5b30b1e7'
SOURCE_TREE = '9c3913ceaa95f3f36b0377fe2dba4a302afcba89'
BRANCH = 'pro/dg18-a12-current-51416-20261120-02'
PREFIX = 'handoff/pro-executor-results-20261115/dg18-a12-current-capture/'
WORKFLOW_PATH = '.github/workflows/dg18-a12-current-capture.yml'
PATHS = [WORKFLOW_PATH, PREFIX + 'capture.py', PREFIX + 'episode.py', PREFIX + 'mutations.py']
ORIGINAL_TEST = 'fixtures/canonical-state-rotation/claim_transaction_test.py'
CONTEXT = {'schema': 'dg18.original-a12-capture.v1', 'authority': 'NONE', 'original_criterion': 12,
           'original_denominator': 14, 'product_commit': SOURCE_COMMIT, 'product_tree': SOURCE_TREE,
           'native_OR_C02_G132_Stop_N1_evidence': False, 'award': None, 'automatic_retry': False}
MAX_FILE = 64 * 1024 * 1024
MAX_CASE_BYTES = 512 * 1024 * 1024
MAX_COMMANDS = 50000
CASE_TIMEOUT = 600
CAMPAIGN_TIMEOUT = 5400
RAW_RUN = subprocess.run
RAW_POPEN = subprocess.Popen


class PipeTee:
    """Preserve the original pipe API and record exactly accepted/read bytes."""
    def __init__(self, original, owner, name):
        self.original=original;self.owner=owner;self.name=name;self.closed=False

    def write(self, raw):
        count=self.original.write(raw)
        self.owner.record_pipe(self.name,'write',raw[:count],{'requested_bytes':len(raw),'returned_bytes':count})
        return count

    def read(self, *args):
        raw=self.original.read(*args);self.owner.record_pipe(self.name,'read',raw,{'arguments':list(args)});return raw

    def readline(self, *args):
        raw=self.original.readline(*args);self.owner.record_pipe(self.name,'readline',raw,{'arguments':list(args)});return raw

    def flush(self):
        return self.original.flush()

    def close(self):
        try:return self.original.close()
        finally:self.closed=True;self.owner.maybe_finish()

    def __getattr__(self,name):return getattr(self.original,name)


class ProcessTee:
    def __init__(self, process, recorder, folder, row, stderr_file):
        self.process=process;self.recorder=recorder;self.folder=folder;self.row=row
        self.stderr_file=stderr_file;self.finished=False;self.pipe_lock=threading.Lock();self.frames=[]
        self.stdin=PipeTee(process.stdin,self,'stdin');self.stdout=PipeTee(process.stdout,self,'stdout')
        self.stderr=None
        for name in ('stdin','stdout'):write_new(folder/(name+'.bin'),b'')

    def record_pipe(self,name,operation,raw,extra):
        if not isinstance(raw,bytes):raise TypeError('declared object-reader pipe was not binary')
        with self.pipe_lock:
            path=self.folder/(name+'.bin');offset=path.stat().st_size
            with path.open('ab') as handle:handle.write(raw);handle.flush();os.fsync(handle.fileno())
            row={'index':len(self.frames)+1,'stream':name,'operation':operation,'offset':offset,
                 'time_ns':time.time_ns(),**digest(raw),**extra}
            self.frames.append(row);write_json(self.folder/'pipe-frames'/f'{row["index"]:06d}.json',row)

    def maybe_finish(self):
        if self.finished or not self.stdin.closed or not self.stdout.closed or self.process.poll() is None:return
        self.stderr_file.flush();os.fsync(self.stderr_file.fileno());self.stderr_file.close()
        self.row.update(exit_code=self.process.returncode,ended_ns=time.time_ns(),pipe_frames=len(self.frames),effect='READ_ONLY_PROCESS_COMPLETED')
        for name in ('stdin','stdout','stderr'):self.row[name]=digest((self.folder/(name+'.bin')).read_bytes())
        write_json(self.folder/'RETURN.json',self.row);self.finished=True

    def wait(self,*args,**kwargs):
        result=self.process.wait(*args,**kwargs);self.maybe_finish();return result

    def kill(self):
        self.recorder.event('original-object-reader-kill',command_index=self.row['index']);return self.process.kill()

    def poll(self):return self.process.poll()
    def __getattr__(self,name):return getattr(self.process,name)


def digest(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            'git_blob': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()}


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def write_new(path, raw):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as handle:
        handle.write(raw); handle.flush(); os.fsync(handle.fileno())


def write_json(path, value):
    write_new(path, canonical(value))


def safe_dir(path):
    path = Path(os.path.abspath(path))
    for member in (path, *path.parents):
        info = member.lstat()
        if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
            raise ValueError('nonphysical directory: ' + str(member))
    return path


def load_local(name):
    path = Path(__file__).with_name(name + '.py')
    spec = importlib.util.spec_from_file_location('dg18_a12_' + name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def regular_bytes(path):
    first = path.lstat()
    if not stat.S_ISREG(first.st_mode) or stat.S_ISLNK(first.st_mode) or first.st_size > MAX_FILE:
        raise ValueError('nonregular or oversized retained file: ' + str(path))
    raw = path.read_bytes(); last = path.lstat()
    if (first.st_dev, first.st_ino, first.st_size, first.st_mtime_ns, first.st_mode) != (
            last.st_dev, last.st_ino, last.st_size, last.st_mtime_ns, last.st_mode):
        raise ValueError('file changed across full observation: ' + str(path))
    return raw, first


class Recorder:
    """Evidence transport only. Does not manufacture operation outcomes."""
    def __init__(self, root, original_run=RAW_RUN, original_popen=RAW_POPEN):
        self.root = safe_dir(root); self.original_run = original_run
        self.original_popen=original_popen;self.transport_local=threading.local();self.processes=[]
        self.commands = []; self.events = []; self.snapshots = []
        self.total_bytes = 0; self.scope = 'setup'; self.depth = 0
        for name in ('streams', 'events', 'snapshots', 'bodies'):
            (self.root / name).mkdir(exist_ok=False)

    def body(self, raw):
        if not isinstance(raw, bytes):
            raise TypeError('retained body is not bytes')
        row = digest(raw); path = self.root / 'bodies' / row['sha256']
        if len(raw) > MAX_FILE:
            # Preserve the obtained body before reporting the evidence bound failure.
            write_new(self.root / ('OVERSIZED-' + row['sha256'] + '.bin'), raw)
            raise ValueError('single-body bound exceeded; actual body retained, no verdict')
        if path.exists():
            if path.read_bytes() != raw: raise ValueError('content address collision')
        else:
            write_new(path, raw); self.total_bytes += len(raw)
            if self.total_bytes > MAX_CASE_BYTES:
                raise ValueError('case evidence bound exceeded; obtained bodies retained, no verdict')
        return {'path': path.relative_to(self.root).as_posix(), **row}

    def event(self, kind, **data):
        row = {'index': len(self.events) + 1, 'kind': kind, 'scope': self.scope,
               'time_ns': time.time_ns(), **data}
        self.events.append(row); write_json(self.root / 'events' / f'{row["index"]:06d}.json', row)
        return row

    @staticmethod
    def stream_bytes(raw, kwargs):
        if raw is None: return None
        if isinstance(raw, str): return raw.encode(kwargs.get('encoding') or 'utf-8', kwargs.get('errors') or 'strict')
        if not isinstance(raw, bytes): raise TypeError('unsupported command stream type')
        return raw

    def run(self, *args, **kwargs):
        if len(self.commands) >= MAX_COMMANDS:
            raise ValueError('command count bound reached before another command; no verdict')
        argv = args[0] if args else kwargs.get('args')
        if not isinstance(argv, (list, tuple)) or kwargs.get('shell', False):
            raise ValueError('undeclared shell/string command; original not invoked')
        index = len(self.commands) + 1; folder = self.root / 'streams' / f'{index:06d}'; folder.mkdir()
        env = kwargs.get('env'); inp = self.stream_bytes(kwargs.get('input'), kwargs)
        row = {'index': index, 'scope': self.scope, 'argv': [str(x) for x in argv],
               'cwd': str(kwargs.get('cwd') or Path.cwd()), 'started_ns': time.time_ns(),
               'timeout': kwargs.get('timeout'), 'check': kwargs.get('check', False),
               'text': bool(kwargs.get('text') or kwargs.get('universal_newlines')),
               'encoding': kwargs.get('encoding'), 'errors': kwargs.get('errors'),
               'env_keys': None if env is None else sorted(env),
               'env_sha256': None if env is None else digest(canonical(dict(env)))['sha256'],
               'input': None if inp is None else digest(inp)}
        redirected = {name: folder / (name + '.redirected.bin') for name in ('stdout', 'stderr')
                      if kwargs.get(name) == subprocess.DEVNULL}
        if redirected:
            row['stdio_retention_substitution'] = {name:
                'Original DEVNULL redirected to a regular evidence file; caller-visible stream remains None.'
                for name in redirected}
        self.commands.append(row)
        if inp is not None: write_new(folder / 'stdin.bin', inp)
        write_json(folder / 'INTENT.json', row)
        try:
            with ExitStack() as files:
                retained = {name: files.enter_context(path.open('xb')) for name, path in redirected.items()}
                observed_kwargs = dict(kwargs, **retained)
                self.transport_local.inside_run=True
                try:result = self.original_run(*args, **observed_kwargs)
                finally:
                    self.transport_local.inside_run=False
                    for handle in retained.values():
                        handle.flush(); os.fsync(handle.fileno())
        except BaseException as exc:
            row.update(exception_type=type(exc).__name__, exception_text=str(exc), ended_ns=time.time_ns(),
                       effect='UNKNOWN' if isinstance(exc, (OSError, subprocess.TimeoutExpired)) else 'EXCEPTION_RETAINED')
            if isinstance(exc,subprocess.CalledProcessError):
                row['exit_code']=exc.returncode;row['effect']='PROCESS_COMPLETED_NONZERO'
            for name in ('stdout', 'stderr'):
                if name in redirected and redirected[name].exists():
                    retained_path = folder / (name + '.partial.bin'); redirected[name].rename(retained_path)
                    row[name + '_partial'] = digest(retained_path.read_bytes())
                else:
                    raw = self.stream_bytes(getattr(exc, name, None), kwargs)
                    if raw is not None:
                        write_new(folder / (name + '.partial.bin'), raw); row[name + '_partial'] = digest(raw)
            write_json(folder / 'EXCEPTION.json', row)
            raise
        for name in ('stdout', 'stderr'):
            if name in redirected:
                retained_path = folder / (name + '.bin'); redirected[name].rename(retained_path)
                row[name] = digest(retained_path.read_bytes())
                continue
            raw = self.stream_bytes(getattr(result, name), kwargs)
            if raw is None:
                row[name] = None; row[name + '_availability'] = 'INHERITED_OR_REDIRECTED_NOT_CAPTURED'
            else:
                write_new(folder / (name + '.bin'), raw); row[name] = digest(raw)
        row.update(exit_code=result.returncode, ended_ns=time.time_ns())
        write_json(folder / 'RETURN.json', row)
        return result

    def completeness(self):
        gaps=[]
        for row in self.commands:
            if row.get('effect')=='UNKNOWN':gaps.append({'command':row['index'],'gap':'UNKNOWN_PROCESS_EFFECT'})
            if 'exit_code' not in row:gaps.append({'command':row['index'],'gap':'NO_TERMINAL_PROCESS_RETURN'})
            for name in ('stdout','stderr'):
                if not isinstance(row.get(name),dict) and not isinstance(row.get(name+'_partial'),dict):
                    gaps.append({'command':row['index'],'gap':'UNRETAINED_'+name.upper()})
        for process in self.processes:
            if not process.finished:gaps.append({'command':process.row['index'],'gap':'INCOMPLETE_DIRECT_PIPE_PROCESS'})
        return {'complete':not gaps,'gaps':gaps}

    def popen(self,*args,**kwargs):
        if getattr(self.transport_local,'inside_run',False):return self.original_popen(*args,**kwargs)
        argv=args[0] if args else kwargs.get('args')
        if (not isinstance(argv,(tuple,list)) or list(map(str,argv))[-2:]!=['cat-file','--batch-command']
                or kwargs.get('stdin')!=subprocess.PIPE or kwargs.get('stdout')!=subprocess.PIPE
                or kwargs.get('stderr')!=subprocess.DEVNULL or kwargs.get('shell',False)):
            raise ValueError('unreviewed direct Popen population; no process launched')
        if len(self.commands)>=MAX_COMMANDS:raise ValueError('command count bound reached')
        index=len(self.commands)+1;folder=self.root/'streams'/f'{index:06d}';folder.mkdir()
        env=kwargs.get('env')
        row={'index':index,'scope':self.scope,'transport':'ORIGINAL_DIRECT_OBJECT_READER',
             'argv':list(map(str,argv)),'cwd':str(kwargs.get('cwd') or Path.cwd()),'started_ns':time.time_ns(),
             'env_keys':None if env is None else sorted(env),
             'env_sha256':None if env is None else digest(canonical(dict(env)))['sha256'],
             'stdin':'original binary PIPE, calls/accepted bytes unchanged','stdout':'original binary PIPE, reads/results unchanged',
             'stderr_retention_substitution':'Original DEVNULL is redirected to a regular evidence file; exposed process.stderr remains None.',
             'original_argv_env_timeouts_and_object_exchange_unchanged':True}
        self.commands.append(row);write_json(folder/'INTENT.json',row)
        err=(folder/'stderr.bin').open('xb');selected=dict(kwargs,stderr=err)
        try:process=self.original_popen(*args,**selected)
        except BaseException as exc:
            err.close();row.update(exception_type=type(exc).__name__,exception_text=str(exc),effect='UNKNOWN',ended_ns=time.time_ns())
            write_json(folder/'EXCEPTION.json',row);raise
        proxy=ProcessTee(process,self,folder,row,err);self.processes.append(proxy);return proxy

    def git_read(self, repo, *args):
        env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'GIT_CONFIG_NOSYSTEM': '1',
               'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_NO_LAZY_FETCH': '1', 'GIT_ALLOW_PROTOCOL': ''}
        result = self.run(['/usr/bin/git', '--no-replace-objects', '-C', str(repo),
            '-c', 'core.hooksPath=/dev/null', '-c', 'protocol.allow=never', *args],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
        if result.returncode: raise ValueError('observational Git read failed; raw result retained')
        return result.stdout

    def snapshot(self, repo, run_root, label):
        repo = safe_dir(repo); files = []; objects = {}
        old_scope = self.scope; self.scope = 'observation:' + label
        try:
            refs_raw = self.git_read(repo, 'for-each-ref', '--format=%(refname) %(objectname)')
            refs = dict(line.split(' ', 1) for line in refs_raw.decode().splitlines())
            identity_raw = self.git_read(repo, 'rev-parse', 'HEAD', 'HEAD^{tree}')
            head, tree = identity_raw.decode().splitlines()
            for path in sorted(repo.rglob('*')):
                info = path.lstat()
                if stat.S_ISDIR(info.st_mode): continue
                raw, info = regular_bytes(path); relative = path.relative_to(repo).as_posix()
                row = {'path': relative, 'mode': oct(info.st_mode & 0o7777), 'uid': info.st_uid,
                       'body': self.body(raw)}; files.append(row)
                if re.fullmatch(r'\.git/objects/[0-9a-f]{2}/[0-9a-f]{38}', relative):
                    oid = relative.replace('.git/objects/', '').replace('/', '')
                    try:
                        decoded = zlib.decompress(raw); header, content = decoded.split(b'\0', 1)
                        kind, size = header.decode().split(' ', 1)
                        objects[oid] = {'kind': kind, 'declared_bytes': int(size),
                            'size_matches': int(size) == len(content),
                            'identity_matches': hashlib.sha1(decoded).hexdigest() == oid,
                            'body': self.body(content), 'compressed_body': row['body']}
                    except (ValueError, zlib.error, UnicodeError) as exc:
                        objects[oid] = {'decode_error': type(exc).__name__, 'compressed_body': row['body']}
            row = {'index': len(self.snapshots) + 1, 'label': label, 'time_ns': time.time_ns(),
                   'repository': str(repo), 'run_root': str(run_root),
                   'head': head, 'tree': tree, 'refs': refs, 'refs_raw': self.body(refs_raw),
                   'identity_raw': self.body(identity_raw), 'files': files, 'objects': objects}
            self.snapshots.append(row)
            path = self.root / 'snapshots' / f'{row["index"]:06d}.json'; write_json(path, row)
            self.event('snapshot', snapshot_index=row['index'], label=label, path=path.relative_to(self.root).as_posix(),
                       snapshot=digest(path.read_bytes()))
            return row
        finally:
            self.scope = old_scope

    def finish(self):
        for process in self.processes:
            process.maybe_finish()
            if not process.finished:
                process.stderr_file.flush()
                write_json(process.folder/'UNFINISHED.json',{'effect':'UNKNOWN','pid':process.process.pid,
                    'poll':process.process.poll(),'stdin_closed':process.stdin.closed,'stdout_closed':process.stdout.closed,
                    'no_product_operation_repeated':True})
        write_json(self.root / 'COMMAND_INDEX.json', {'commands': self.commands, 'count': len(self.commands)})
        write_json(self.root / 'EVENT_INDEX.json', {'events': self.events, 'count': len(self.events)})
        write_json(self.root / 'SNAPSHOT_INDEX.json', {'snapshots': [
            {'index': s['index'], 'label': s['label'], 'path': f'snapshots/{s["index"]:06d}.json'} for s in self.snapshots]})


def archive_tree(repo, target):
    repo = safe_dir(repo); target = Path(target); rows = []
    if target.exists() or target.is_relative_to(repo): raise ValueError('invalid or repeated archive target')
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(repo.rglob('*')):
            info = path.lstat()
            if stat.S_ISDIR(info.st_mode): continue
            raw, info = regular_bytes(path); name = path.relative_to(repo).as_posix()
            entry = zipfile.ZipInfo(name); entry.external_attr = (stat.S_IFREG | (info.st_mode & 0o7777)) << 16
            entry.compress_type = zipfile.ZIP_DEFLATED; archive.writestr(entry, raw)
            rows.append({'path': name, 'mode': oct(info.st_mode & 0o7777), **digest(raw)})
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None or len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError('fixture archive did not read back exactly')
        if any(digest(archive.read(row['path'])) != {k: row[k] for k in ('bytes','sha256','git_blob')} for row in rows):
            raise ValueError('fixture archive member readback differs')
    return {'path': target.name, **digest(target.read_bytes()), 'members': rows,
            'member_count': len(rows), 'member_bytes': sum(r['bytes'] for r in rows)}


def git(source, *args):
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'GIT_CONFIG_NOSYSTEM': '1',
           'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_NO_LAZY_FETCH': '1', 'GIT_ALLOW_PROTOCOL': ''}
    return RAW_RUN(['/usr/bin/git', '-c', 'protocol.allow=never', '-c', 'core.hooksPath=/dev/null',
                    '-c', 'core.fsmonitor=false', *args], cwd=source, env=env,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=30).stdout


def provider_binding(output):
    expected = {'GITHUB_ACTIONS': 'true', 'RUNNER_ENVIRONMENT': 'github-hosted',
        'GITHUB_REPOSITORY': 'theislampill/IMPLEMENTAUDIT.md', 'GITHUB_EVENT_NAME': 'push',
        'GITHUB_REF': 'refs/heads/' + BRANCH, 'GITHUB_RUN_ATTEMPT': '1'}
    for key, value in expected.items():
        if os.environ.get(key) != value: raise ValueError('provider binding differs: ' + key)
    run = os.environ.get('GITHUB_RUN_ID', ''); commit = os.environ.get('GITHUB_SHA', '')
    if not run.isdigit() or not re.fullmatch('[0-9a-f]{40}', commit): raise ValueError('invalid provider identity')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_bytes())
    if event.get('before') != '0' * 40 or event.get('after') != commit or event.get('created') is not True or event.get('deleted') is not False:
        raise ValueError('only a genuine new first-push attempt is selected')
    if sys.platform != 'linux' or os.path.abspath(sys.executable) != '/usr/bin/python3.12':
        raise ValueError('declared physical Linux interpreter required')
    target = safe_dir(os.environ['RUNNER_TEMP']) / ('dg18-a12-' + run + '-1')
    if Path(os.path.abspath(output)) != target: raise ValueError('output does not bind this run')
    return run, commit, target, expected


def host_binding(source, output):
    run, commit, target, expected = provider_binding(output)
    source = safe_dir(source)
    if target.is_relative_to(source) or source.is_relative_to(target): raise ValueError('source/output overlap')
    packet = safe_dir(Path(__file__).absolute().parents[len(PurePosixPath(PREFIX + 'capture.py').parts) - 1])
    identity = git(packet, 'show', '-s', '--format=%H%n%T%n%P', 'HEAD').decode().splitlines()
    if identity[0] != commit or identity[2].split() != [SOURCE_COMMIT]: raise ValueError('not the exact sole-parent publication')
    changed = git(packet, 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').decode().splitlines()
    if sorted(changed) != sorted(PATHS) or git(packet, 'status', '--porcelain=v1', '--untracked-files=all'):
        raise ValueError('packet additions or bytes differ')
    return {**CONTEXT, 'run_id': int(run), 'attempt': 1, 'workflow_commit': commit, 'workflow_tree': identity[1],
            'workflow_parent': SOURCE_COMMIT, 'workflow_changed_paths': changed, 'host_predicates': expected,
            'source_path': str(source), 'output_path': str(target),
            'capture_sources': {name: digest((packet / PREFIX / name).read_bytes()) for name in ('capture.py','episode.py','mutations.py')}}


def source_census(source, output):
    identity = git(source, 'show', '-s', '--format=%H%n%T', 'HEAD').decode().splitlines()
    if identity != [SOURCE_COMMIT, SOURCE_TREE]: raise ValueError('product commit/tree differs')
    status = git(source, 'status', '--porcelain=v1', '--untracked-files=all')
    if status: raise ValueError('product checkout is not clean')
    prefixes = ('skills/implementaudit/scripts/', 'skills/implementaudit/templates/')
    exact = {ORIGINAL_TEST, 'fixtures/canonical-state-rotation/protected_projection_v2_test.py',
             'fixtures/canonical-state-rotation/v2/source.json', 'fixtures/controller-initialization/author_checkpoint.py',
             'fixtures/run-root-example/phases/phase-1.md'}
    rows = []
    for line in git(source, 'ls-tree', '-r', 'HEAD').decode().splitlines():
        meta, path = line.split('\t', 1)
        if path not in exact and not path.startswith(prefixes): continue
        mode, kind, oid = meta.split(); raw, info = regular_bytes(source / path)
        if kind != 'blob' or mode not in {'100644','100755'} or digest(raw)['git_blob'] != oid:
            raise ValueError('source member differs from exact original tree: ' + path)
        rows.append({'path': path, 'mode': mode, **digest(raw)})
    paths = {r['path'] for r in rows}
    if not exact.issubset(paths): raise ValueError('source population incomplete')
    actual = {p.relative_to(source).as_posix() for prefix in prefixes for p in (source / prefix).rglob('*') if p.is_file() or p.is_symlink()}
    if actual != {p for p in paths if p.startswith(prefixes)}: raise ValueError('physical runtime population differs')
    tools = []; tool_dir = output / 'runtime-bodies'; tool_dir.mkdir(exist_ok=True)
    for name in ('python3.12', 'git', 'bash'):
        path = Path('/usr/bin') / name; raw, info = regular_bytes(path)
        if info.st_uid != 0 or info.st_mode & 0o022: raise ValueError('unqualified physical runtime: ' + name)
        body = digest(raw); target = tool_dir / (body['sha256'] + '.bin')
        if not target.exists(): write_new(target, raw)
        if target.read_bytes() != raw: raise ValueError('retained physical executable differs')
        version = RAW_RUN([str(path), '--version'], env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
        if version.returncode: raise ValueError('physical tool version failed')
        versions = {}
        for label, data in (('stdout', version.stdout), ('stderr', version.stderr)):
            filename = digest(data)['sha256'] + '.bin'; dest = tool_dir / filename
            if not dest.exists(): write_new(dest, data)
            if dest.read_bytes() != data: raise ValueError('retained tool version bytes differ')
            versions[label] = {'path': 'runtime-bodies/' + filename, **digest(data)}
        tools.append({'path': str(path), 'uid': info.st_uid, 'mode': oct(info.st_mode & 0o7777),
                      **body, 'retained_body': target.relative_to(output).as_posix(), 'version': versions})
    return {**CONTEXT, 'source_members': rows, 'source_member_count': len(rows),
            'source_member_bytes': sum(r['bytes'] for r in rows), 'tools': tools, 'python': sys.version, 'git_status': status.decode()}


def process_survivorship(root):
    records = {}; unavailable = []
    for node in Path('/proc').iterdir():
        if not node.name.isdigit(): continue
        try:
            raw = (node / 'stat').read_text(); parts = raw[raw.rfind(')') + 2:].split()
            pid = int(node.name)
            try: cwd = os.readlink(node / 'cwd')
            except OSError: cwd = None
            try: argv = [v.decode(errors='replace') for v in (node / 'cmdline').read_bytes().split(b'\0') if v]
            except OSError: argv = []
            records[pid] = {'pid': pid, 'ppid': int(parts[1]), 'start_ticks': int(parts[19]),
                            'state': parts[0], 'cwd': cwd, 'argv': argv}
        except (FileNotFoundError, ProcessLookupError): continue
        except (OSError, ValueError, IndexError) as exc: unavailable.append({'pid': int(node.name), 'error': type(exc).__name__})
    descendants = {os.getpid()}
    while True:
        newer = descendants | {pid for pid, row in records.items() if row['ppid'] in descendants}
        if newer == descendants: break
        descendants = newer
    prefix = str(root) + '/'
    selected = [r for pid, r in records.items() if pid != os.getpid() and (pid in descendants
        or (r['cwd'] is not None and r['cwd'].startswith(prefix)) or any(a.startswith(prefix) for a in r['argv']))]
    return {'scope': 'Current descendants and cwd/argv under this exact evidence root; not a transitive process history.',
            'observer_pid': os.getpid(), 'survivors': selected, 'unavailable': unavailable}


def run_child(argv, folder, env, timeout=CASE_TIMEOUT):
    """One child attempt; retain raw streams on timeout and kill its own group."""
    write_json(folder / 'CHILD_INTENT.json', {'argv': argv, 'started_ns': time.time_ns(), 'timeout_seconds': timeout,
                                            'new_process_group': True, 'retry': False})
    with (folder / 'CHILD.stdout').open('xb') as out, (folder / 'CHILD.stderr').open('xb') as err:
        process = subprocess.Popen(argv, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True)
        row = {'pid': process.pid, 'process_group': process.pid, 'started_ns': time.time_ns(), 'retry': False}
        try:
            row['exit_code'] = process.wait(timeout=timeout); row['transport'] = 'COMPLETED'
        except subprocess.TimeoutExpired:
            row['transport'] = 'TIMEOUT_UNKNOWN'; row['effect'] = 'UNKNOWN'
            try:os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:row['termination_race']='process group already absent'
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:row['kill_race']='process group already absent'
                process.wait(timeout=10)
            row['exit_code'] = process.returncode
        row['ended_ns'] = time.time_ns()
    row['stdout'] = digest((folder / 'CHILD.stdout').read_bytes()); row['stderr'] = digest((folder / 'CHILD.stderr').read_bytes())
    write_json(folder / 'CHILD_RETURN.json', row)
    return row


def preflight(source, output):
    binding = host_binding(source, output); output.mkdir(mode=0o700, exist_ok=False)
    write_json(output / 'PREFLIGHT_INTENT.json', binding)
    census = source_census(source, output); write_json(output / 'SOURCE_BEFORE.json', census)
    mutations = load_local('mutations'); owner_raw = (source / 'skills/implementaudit/scripts/claim-run-rotation.py').read_bytes()
    for row in mutations.MUTANTS:
        write_json(output / 'source-variants' / (row[0] + '.json'), mutations.build_variant(owner_raw, row[0]))
    write_json(output / 'PREFLIGHT.json', {**binding, 'cases': list(mutations.CASES), 'case_count': len(mutations.CASES),
        'source_before': digest((output / 'SOURCE_BEFORE.json').read_bytes()), 'case_timeout_seconds': CASE_TIMEOUT,
        'campaign_timeout_seconds': CAMPAIGN_TIMEOUT,
        'selected_original_tests_have_executed': False, 'status': 'PREPARED_FOR_DECLARED_ORIGINAL_CAMPAIGN_ONLY'})


def capture_cases(source, output, cases, env, *, clock=time.monotonic, child_runner=run_child):
    """Keep the full declared population within the outer custody window.

    A case not started before the predeclared deadline remains incomplete. It is
    not omitted from the result population and cannot supply mutation credit.
    """
    cases_root = output / 'cases'; cases_root.mkdir(exist_ok=False); rows = []
    started = clock()
    for case in cases:
        folder = cases_root / case['id']; folder.mkdir(mode=0o700)
        remaining = CAMPAIGN_TIMEOUT - (clock() - started)
        if remaining <= 0:
            transport = {'transport':'NOT_STARTED_CAMPAIGN_DEADLINE','effect':'NO_CHILD_STARTED',
                'exit_code':None,'retry':False,'campaign_timeout_seconds':CAMPAIGN_TIMEOUT}
            result = {'disposition':'INCOMPLETE','original_executed':False,
                'reason':'Declared aggregate execution budget elapsed; case remains required and unobserved.'}
            write_json(folder / 'CHILD_NOT_STARTED.json', {'case':case,'transport':transport,'result':result})
            rows.append({'case':case,'transport':transport,'result':result,'result_body':None})
            continue
        argv = ['/usr/bin/python3.12', '-I', '-B', str(Path(__file__).with_name('episode.py')),
                '--source', str(source), '--output', str(folder), '--case', case['id'],
                '--preflight', str(output / 'PREFLIGHT.json')]
        transport = child_runner(argv, folder, env, timeout=min(CASE_TIMEOUT, remaining))
        result_path = folder / 'CASE_RESULT.json'
        result = json.loads(result_path.read_bytes()) if result_path.exists() else {'disposition': 'INCOMPLETE'}
        rows.append({'case': case, 'transport': transport, 'result': result,
                     'result_body': digest(result_path.read_bytes()) if result_path.exists() else None})
    return rows


def execute(source, output):
    binding = host_binding(source, output); pre = json.loads((output / 'PREFLIGHT.json').read_bytes())
    if any(pre[k] != binding[k] for k in binding): raise ValueError('preflight binding changed')
    if digest((output / 'SOURCE_BEFORE.json').read_bytes()) != pre['source_before']: raise ValueError('preflight source record changed')
    before = json.loads((output / 'SOURCE_BEFORE.json').read_bytes())
    if source_census(source, output) != before: raise ValueError('source/runtime changed before execution')
    write_json(output / 'EXECUTION_INTENT.json', {**binding, 'cases': pre['cases'], 'time_ns': time.time_ns()})
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'LANG': 'C', 'PYTHONDONTWRITEBYTECODE': '1',
           'PYTHONUNBUFFERED': '1'}
    rows = capture_cases(source, output, pre['cases'], env)
    after = source_census(source, output); write_json(output / 'SOURCE_AFTER.json', after)
    survival = process_survivorship(output); write_json(output / 'PROCESS_SURVIVORSHIP.json', survival)
    complete = len(rows) == len(pre['cases']) and after == before and not survival['survivors'] and not survival['unavailable']
    complete = complete and all(r['transport']['transport'] == 'COMPLETED' and r['transport']['exit_code'] == 0
        and r['result'].get('disposition') in {'BASELINE_PASS','KILLED'}
        and r['result'].get('fixture_cleanup_complete') is True for r in rows)
    write_json(output / 'RESULT.json', {**binding, 'cases': rows, 'case_count': len(rows),
        'status': 'CAPTURE_COMPLETE_PENDING_INDEPENDENT_A12_RECEIVING' if complete else 'FAILED_SURVIVED_OR_INCOMPLETE_PRESERVED',
        'source_unchanged': after == before, 'survivorship': survival, 'award': None})
    print(json.dumps({'cases': len(rows), 'capture_complete': complete, 'award': None}))
    return 0 if complete else 1


def finalize(source, output):
    """Observational survivor custody only; no original imports or case execution."""
    provider_binding(output)
    if not output.exists():
        output.mkdir(mode=0o700, exist_ok=False)
        write_json(output / 'NO_PREFLIGHT.json', {**CONTEXT, 'original_execution_established': False})
    safe_dir(output); survivor_rows = []
    process_observation = process_survivorship(output)
    cleanup_admitted = not process_observation['survivors'] and not process_observation['unavailable']
    for fixtures in sorted((output / 'cases').glob('*/fixtures')) if (output / 'cases').exists() else []:
        safe_dir(fixtures)
        for repo in sorted(fixtures.iterdir()):
            safe_dir(repo)
            if not cleanup_admitted:
                survivor_rows.append({'repository':str(repo),'cleanup_complete':False,
                    'disposition':'PROCESS_CUSTODY_UNRESOLVED_ROOT_RETAINED',
                    'original_result':'INCOMPLETE_UNKNOWN_NOT_REPAIRED'})
                continue
            target = fixtures.parent / ('SURVIVING-' + repo.name + '.zip')
            try:
                archive = archive_tree(repo, target)
                shutil.rmtree(repo)
                survivor_rows.append({'repository': str(repo), 'archive': archive,
                    'cleanup_complete': not os.path.lexists(repo), 'original_result': 'INCOMPLETE_UNKNOWN_NOT_REPAIRED'})
            except BaseException as exc:
                survivor_rows.append({'repository': str(repo), 'retention_error': type(exc).__name__,
                                     'message': str(exc), 'cleanup_complete': False})
    write_json(output / 'SURVIVOR_FINALIZATION.json', {**CONTEXT, 'surviving_fixtures': survivor_rows,
        'original_case_calls': 0, 'process_observation': process_observation,
        'fixture_cleanup_admitted':cleanup_admitted})
    rows = []
    for path in sorted(output.rglob('*')):
        info = path.lstat()
        if stat.S_ISDIR(info.st_mode): continue
        raw, info = regular_bytes(path); relative = path.relative_to(output).as_posix()
        if relative == 'FINAL_MANIFEST.json': raise ValueError('already finalized; no retry')
        rows.append({'path': relative, 'mode': oct(info.st_mode & 0o7777), **digest(raw)})
    write_json(output / 'FINAL_MANIFEST.json', {**CONTEXT, 'members': rows, 'member_count': len(rows),
        'member_bytes': sum(r['bytes'] for r in rows), 'original_cases_called_by_finalizer': 0})
    print(json.dumps({'retained_members': len(rows), 'retained_bytes': sum(r['bytes'] for r in rows), 'award': None}))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--step', required=True, choices=['preflight','execute','finalize'])
    parser.add_argument('--source', required=True, type=Path); parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); source = Path(os.path.abspath(args.source)); output = Path(os.path.abspath(args.output))
    if args.step == 'preflight': preflight(source, output); return 0
    if args.step == 'execute': return execute(source, output)
    finalize(source, output); return 0


if __name__ == '__main__':
    raise SystemExit(main())
