#!/usr/bin/env python3
"""Later exact byte acquisition for A1/A3; no original case or award authority."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time

PARENT = '51416b2f156b341c4a5f09029e2c6ceb5b30b1e7'
BRANCH = 'pro/dg18-exact-tool-bodies-20261120-01'
HELPER = 'handoff/pro-executor-results-20261115/dg18-exact-tool-bodies/capture.py'
WORKFLOW = '.github/workflows/dg18-exact-tool-bodies.yml'
EXPECTED = [
    {'path': '/usr/bin/python3.12', 'name': 'python3.12.bin', 'bytes': 8020928,
     'sha256': 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f',
     'git_blob': '6d235376c83abecfebea20ec46b105c0d21c086c'},
    {'path': '/usr/bin/git', 'name': 'git.bin', 'bytes': 4640384,
     'sha256': '08ca4d2ee4d8915e86f1faaa52603752507c57af1d16d451dec9992bc9b6d801',
     'git_blob': '2ead47b68ed7b31526a837f186d5d3a4c5579820'},
    {'path': '/usr/bin/bash', 'name': 'bash.bin', 'bytes': 1446024,
     'sha256': 'bc5945feb8bd26203ebfafea5ce1878bb2e32cb8fb50ab7ae395cfb1e1aaaef1',
     'git_blob': '161fddc2f2bdede1fb24ba7739a79c16c9ed6523'},
]


def digest(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            'git_blob': hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()}


def write_new(path, raw):
    with path.open('xb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def write_json(path, value):
    write_new(path, (json.dumps(value, indent=2, sort_keys=True)+'\n').encode())


def stable_body(path, *, expected_uid=0, limit=9000000):
    path = Path(path)
    for parent in path.parents:
        row = parent.lstat()
        if not stat.S_ISDIR(row.st_mode) or stat.S_ISLNK(row.st_mode):
            raise ValueError('nonphysical parent')
    first = path.lstat()
    if (not stat.S_ISREG(first.st_mode) or first.st_uid != expected_uid
            or first.st_mode & 0o022 or first.st_size > limit):
        raise ValueError('unqualified physical executable')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(fd)
        fields = ('st_dev', 'st_ino', 'st_mode', 'st_uid', 'st_gid', 'st_nlink',
                  'st_size', 'st_mtime_ns', 'st_ctime_ns')
        if any(getattr(first, k) != getattr(opened, k) for k in fields):
            raise ValueError('source changed before read')
        with os.fdopen(fd, 'rb', closefd=False) as handle:
            raw = handle.read(limit+1)
        after_fd, after_path = os.fstat(fd), path.lstat()
        if (len(raw) != opened.st_size or len(raw) > limit
                or any(getattr(opened, k) != getattr(after_fd, k)
                       or getattr(opened, k) != getattr(after_path, k) for k in fields)):
            raise ValueError('source changed during read')
        return raw, {'path': str(path), 'uid': opened.st_uid,
                     'mode': oct(stat.S_IMODE(opened.st_mode)), **digest(raw)}
    finally:
        os.close(fd)


def require_expected(row, expected):
    if any(row[k] != expected[k] for k in ('bytes', 'sha256', 'git_blob')):
        raise ValueError('body differs from the original episode census')
    if row['uid'] != 0 or row['mode'] != '0o755' or row['path'] != expected['path']:
        raise ValueError('physical path/owner/mode differs')


def provider_binding(output):
    required = {'GITHUB_ACTIONS': 'true', 'RUNNER_ENVIRONMENT': 'github-hosted',
                'GITHUB_REPOSITORY': 'theislampill/IMPLEMENTAUDIT.md',
                'GITHUB_EVENT_NAME': 'push', 'GITHUB_REF': 'refs/heads/'+BRANCH,
                'GITHUB_RUN_ATTEMPT': '1'}
    if any(os.environ.get(k) != v for k, v in required.items()):
        raise ValueError('provider selection mismatch')
    run, sha = os.environ.get('GITHUB_RUN_ID', ''), os.environ.get('GITHUB_SHA', '')
    if not re.fullmatch(r'[0-9]+', run) or not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('invalid run/commit')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    if (event.get('before') != '0'*40 or event.get('after') != sha
            or event.get('created') is not True or event.get('deleted') is not False):
        raise ValueError('not first live branch creation')
    if sys.platform != 'linux' or os.path.abspath(sys.executable) != '/usr/bin/python3.12':
        raise ValueError('wrong physical interpreter')
    wanted = Path(os.path.abspath(os.environ['RUNNER_TEMP']))/('dg18-tool-bodies-'+run+'-1')
    if output != wanted or not wanted.parent.is_dir() or wanted.parent.is_symlink():
        raise ValueError('output path mismatch')
    return {'schema': 'dg18.exact-tool-body-later-acquisition.v1', 'authority': 'NONE',
            'run_id': int(run), 'attempt': 1, 'workflow_commit': sha,
            'branch': BRANCH, 'provider_predicates': required,
            'original_runs': [{'id': 44703838739, 'attempt': 1, 'criterion': 1},
                              {'id': 44702285737, 'attempt': 1, 'criterion': 3}],
            'temporal_scope': 'Later exact body acquisition only. Original before/pre-execution/after observations are unchanged and are joined separately.',
            'original_case_replayed': False, 'original_awards': [], 'automatic_retry': False}


def clean_environment():
    env = dict(os.environ)
    for key in list(env):
        if key.startswith('GIT_') or key in ('PYTHONPATH', 'PYTHONHOME'):
            env.pop(key)
    env.update(PATH='/usr/bin:/bin', LC_ALL='C', GIT_CONFIG_NOSYSTEM='1',
               GIT_CONFIG_GLOBAL='/dev/null', GIT_ALLOW_PROTOCOL='', GIT_NO_LAZY_FETCH='1')
    return env


def capture(output):
    binding = provider_binding(output)
    output.mkdir(mode=0o700, exist_ok=False)
    write_json(output/'ACQUISITION_INTENT.json', {**binding, 'expected': EXPECTED,
                                               'started_ns': time.time_ns()})
    failure = None
    rows, versions = [], []
    try:
        bodies = []
        for expected in EXPECTED:
            raw, row = stable_body(expected['path'])
            rows.append(row)
            require_expected(row, expected)
            bodies.append(raw)
        packet = Path(__file__).absolute().parents[len(Path(HELPER).parts)-1]
        env = clean_environment()
        def git(*args):
            return subprocess.run(['/usr/bin/git', '-c', 'core.hooksPath=/dev/null',
                '-c', 'core.fsmonitor=false', '-c', 'protocol.allow=never', *args],
                cwd=packet, env=env, check=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=20).stdout
        identity = git('show', '-s', '--format=%H%n%T%n%P', 'HEAD').decode().splitlines()
        if identity[0] != binding['workflow_commit'] or identity[2].split() != [PARENT]:
            raise ValueError('wrong sole-parent publication')
        changed = git('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').decode().splitlines()
        if sorted(changed) != sorted([HELPER, WORKFLOW]) or git('status', '--porcelain=v1', '--untracked-files=all'):
            raise ValueError('unreviewed publication paths or modified checkout')
        binding.update(workflow_tree=identity[1], sole_parent=PARENT,
                       changed_paths=changed, helper=digest(Path(__file__).read_bytes()))
        (output/'bodies').mkdir(mode=0o700)
        for expected, raw in zip(EXPECTED, bodies):
            write_new(output/'bodies'/expected['name'], raw)
        for index, argv in enumerate((['/usr/bin/python3.12', '--version'],
                                      ['/usr/bin/git', '--version'],
                                      ['/usr/bin/bash', '--noprofile', '--norc', '--version'])):
            started = time.time_ns()
            returned = subprocess.run(argv, env=env, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, timeout=20, check=False)
            write_new(output/('version-%d.stdout'%index), returned.stdout)
            write_new(output/('version-%d.stderr'%index), returned.stderr)
            versions.append({'argv': argv, 'exit_code': returned.returncode,
                             'started_ns': started, 'ended_ns': time.time_ns(),
                             'stdout': digest(returned.stdout), 'stderr': digest(returned.stderr)})
            if returned.returncode != 0:
                raise ValueError('version command failed')
        after = []
        for expected, original in zip(EXPECTED, bodies):
            raw, row = stable_body(expected['path'])
            require_expected(row, expected)
            if raw != original or (output/'bodies'/expected['name']).read_bytes() != original:
                raise ValueError('physical or retained body changed')
            after.append(row)
        if after != rows:
            raise ValueError('physical identity census changed')
        write_json(output/'SOURCE_AFTER.json', {'tools': after})
    except BaseException as exc:
        failure = {'type': type(exc).__name__, 'message': str(exc)}
    finally:
        write_json(output/'SOURCE_BEFORE.json', {'tools': rows})
        write_json(output/'VERSION_COMMANDS.json', {'commands': versions,
            'scope': 'Actual version queries during later acquisition; not invented original version streams.'})
        result = {**binding, 'status': 'COMPLETE_EXACT_BODIES_PENDING_INDEPENDENT_JOIN' if failure is None else 'FAILED_OR_INCOMPLETE_NO_RETRY',
                  'tools': rows, 'expected': EXPECTED, 'failure': failure,
                  'python_runtime': sys.version, 'ended_ns': time.time_ns()}
        write_json(output/'RESULT.json', result)
    print(json.dumps({'status': result['status'], 'bodies': len(rows), 'award': None}))
    return 0 if failure is None else 1


def finalize(output):
    binding = provider_binding(output)
    if not output.exists():
        output.mkdir(mode=0o700, exist_ok=False)
        write_json(output/'NO_CAPTURE_OUTPUT.json', {**binding, 'status': 'NO_CAPTURE_OUTPUT'})
    members = []
    for path in sorted(output.rglob('*')):
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
            raise ValueError('unsafe evidence member')
        if not stat.S_ISREG(info.st_mode):
            continue
        if path.name == 'FINAL_MANIFEST.json':
            raise ValueError('finalization already completed')
        members.append({'path': path.relative_to(output).as_posix(), **digest(path.read_bytes())})
    write_json(output/'FINAL_MANIFEST.json', {**binding, 'members': members,
               'member_count': len(members), 'member_bytes': sum(x['bytes'] for x in members),
               'selection': 'Complete retained successful or failed acquisition; no original replay.'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--step', choices=['capture', 'finalize'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = Path(os.path.abspath(args.output))
    if args.step == 'capture':
        return capture(output)
    finalize(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
