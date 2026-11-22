#!/usr/bin/python3.12
"""Inert source for one prospective ordinary hosted observation, never admission.

The namespace owner has irreversible small hard limits. Run its step in a
separate process before the input step; no NSS lease spans that process. The
input step joins the retained receipt by exact source/provider/boot identity.
No provider acquisition, private input, original execution or session is used.
"""
import argparse
from contextlib import contextmanager, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import re
import resource
import signal
import stat
import types

ROOT = Path(__file__).resolve().parents[2]
BASE_COMMIT = '760aaff5c478ff7354d36da186d62daba983aa49'
OPERATION = 'G132_HOST_PROFILE_SUCCESSOR_20261122_01'
REF = 'refs/heads/pro/dg16-g132-host-profile-successor-20261122-01'
SETUP_PIN = {'bytes': 91535, 'sha256': '37c14d5c8ff0f6f3f8d252049be4fa0d90b4217861c3fb4dd0a740cc9248f592'}
NSS_PIN = {'bytes': 16301, 'sha256': '5552e26ab04987cfe288533e973697776b1c5b7df18e521bb6c27e9c0c2316ab'}
LAUNCHER_PIN = {'bytes': 72160, 'sha256': '52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712'}
LIMITS = dict(address_bytes=1610612736, cpu_seconds=120, file_bytes=268435456,
              descriptors=256, wall_seconds=240, report_bytes=2097152)


def need(value, message):
    if not value:
        raise ValueError(message)


def namespace_join(row, context, source_commit, source_tree):
    """Pure receipt discriminator; rc=0 alone also permits proc-mount refusal."""
    need(row.get('schema') == 'g132.host-profile-namespace.v1'
         and row.get('authority') == 'NONE' and row.get('context') == context
         and row.get('source_commit') == source_commit and row.get('source_tree') == source_tree
         and row.get('setup_pin') == SETUP_PIN and row.get('namespace_return_code') == 0,
         'namespace receipt identity differs')
    ns = row.get('namespace', {})
    need(ns.get('schema') == 'dg16.ordinary-setup-capability.v1' and ns.get('authority') == 'NONE'
         and all(ns.get(k) is False for k in ('original19_started', 'provider_acquired', 'native_admission', 'timed_out', 'overflow'))
         and all(ns.get(k) is True for k in ('complete_custody', 'descriptor_restoration', 'owned_group_absent'))
         and ns.get('classification') == 'SETUP_REACHED_ABSENT_TARGET' and ns.get('exit_code') == 1
         and ns.get('eof') == {'stdout': True, 'stderr': True}
         and ns.get('launcher', {}).get('current') is True
         and all(ns['launcher'].get(k) == v for k, v in LAUNCHER_PIN.items()),
         'namespace owner did not receive the absent-target boundary with complete custody')
    return True


def nss_cleanup_complete(record):
    """Retention is not complete cleanup, even when original NSS was restored."""
    return (type(record) is dict and record.get('schema') == 'g132.hosted-files-only-nss.v2'
            and record.get('state') == 'UNCHANGED_FILES_ONLY_CLOSED'
            and record.get('restoration_verified') is True and record.get('cleanup_complete') is True
            and record.get('replacement_deletion_attempted') is False and record.get('backup_removed') is False
            and record.get('replacement_cleanup', {}).get('disposition') == 'NONE_ALLOCATED')


def identity(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_uid, value.st_gid, value.st_mtime_ns, value.st_ctime_ns)


@contextmanager
def held_bytes(path, maximum, expected=None):
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
             and 0 < before.st_size <= maximum, 'unsupported bounded ordinary input file')
        opening = identity(before)
        raw = os.pread(fd, maximum + 1, 0)
        need(len(raw) == before.st_size, 'ordinary input size differs')
        if expected is not None:
            need(dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()) == expected,
                 'exact ordinary source pin differs')
        need(identity(os.lstat(path)) == opening == identity(os.fstat(fd)), 'ordinary opening custody differs')
        yield raw
        need(identity(os.lstat(path)) == opening == identity(os.fstat(fd))
             and os.pread(fd, maximum + 1, 0) == raw, 'ordinary closing custody differs')
    finally:
        os.close(fd)


@contextmanager
def owner(name, pin):
    path = ROOT / 'scripts' / name
    with held_bytes(path, pin['bytes'], pin) as raw:
        module = types.ModuleType('g132_ordinary_' + name.replace('-', '_'))
        module.__file__ = str(path)
        exec(compile(raw, str(path), 'exec'), module.__dict__)
        yield module


def hosted_context():
    expected = dict(GITHUB_ACTIONS='true', RUNNER_ENVIRONMENT='github-hosted',
                    GITHUB_REPOSITORY='theislampill/IMPLEMENTAUDIT.md', GITHUB_RUN_ATTEMPT='1',
                    GITHUB_EVENT_NAME='push', GITHUB_JOB='qualify', GITHUB_REF=REF,
                    ImageOS='ubuntu24', ImageVersion='20261116.376.1')
    need(all(os.environ.get(k) == v for k, v in expected.items()), 'prospective ordinary provider context differs')
    need((os.getuid(), os.geteuid(), os.getgid(), os.getegid()) == (0, 0, 0, 0), 'ordinary observer requires UID/GID zero')
    host_commit = os.environ.get('GITHUB_SHA', '')
    need(re.fullmatch('[0-9a-f]{40}', host_commit) and os.environ.get('GITHUB_WORKFLOW_SHA') == host_commit,
         'ordinary host workflow identity differs')
    workflow_ref = 'theislampill/IMPLEMENTAUDIT.md/.github/workflows/dg16-g132-host-profile-successor.yml@' + REF
    need(os.environ.get('GITHUB_WORKFLOW_REF') == workflow_ref, 'ordinary workflow reference differs')
    run_id = os.environ.get('GITHUB_RUN_ID', '')
    need(re.fullmatch('[1-9][0-9]*', run_id), 'ordinary run identity absent')
    # boot_id is a kernel pseudo-file with st_size zero, so use an explicit bound.
    with open('/proc/sys/kernel/random/boot_id', 'rb') as stream:
        boot = stream.read(65).decode('ascii').strip()
    need(re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', boot), 'ordinary boot identity absent')
    return dict(expected, boot_id=boot, run_id=run_id, host_commit=host_commit, workflow_ref=workflow_ref)


def source_identity(setup, commit, tree, commands):
    need(re.fullmatch('[0-9a-f]{40}', commit) and re.fullmatch('[0-9a-f]{40}', tree), 'exact source arguments required')
    raw = setup.hosted_git(['rev-parse', 'HEAD', 'HEAD^{tree}', 'HEAD^'], ROOT, commands)
    need(raw.decode('ascii').splitlines() == [commit, tree, BASE_COMMIT], 'ordinary source commit/tree/sole baseline differs')
    parents = setup.hosted_git(['show', '-s', '--format=%P', 'HEAD'], ROOT, commands)
    need(parents == (BASE_COMMIT + '\n').encode(), 'ordinary successor must have the single retained R3 parent')
    shallow = setup.hosted_git(['rev-parse', '--is-shallow-repository'], ROOT, commands)
    need(shallow == b'false\n', 'ordinary source ancestry is shallow')
    status = setup.hosted_git(['--no-optional-locks', 'status', '--porcelain=v1', '--untracked-files=all'], ROOT, commands)
    need(status == b'', 'ordinary selected source worktree is not exact and clean')


def output_directory(context, create):
    root = Path(os.environ['RUNNER_TEMP'])
    need(root.is_absolute() and root.resolve() == root, 'ordinary output parent alias refused')
    path = root / ('g132-host-profile-successor-' + context['run_id'] + '-1')
    if create:
        path.mkdir(mode=0o700)  # Exclusive: a prior attempt is never resumed.
    current = path.lstat()
    need(stat.S_ISDIR(current.st_mode) and stat.S_IMODE(current.st_mode) == 0o700
         and current.st_uid == 0 and current.st_gid == 0, 'ordinary output custody differs')
    return path


def write_receipt(path, row, maximum):
    raw = (json.dumps(row, sort_keys=True, separators=(',', ':')) + '\n').encode()
    need(len(raw) <= maximum, 'ordinary report exceeds bound')
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            count = os.write(fd, raw[offset:])
            need(count > 0, 'ordinary report write stalled')
            offset += count
        os.fsync(fd)
        need(os.pread(fd, len(raw) + 1, 0) == raw and identity(os.fstat(fd)) == identity(os.lstat(path)),
             'ordinary report closing readback differs')
    finally:
        os.close(fd)


class OrdinaryDeadline(BaseException):
    pass


def interrupted(signum, frame):
    raise OrdinaryDeadline('ordinary observation interrupted by bounded wall/signal')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--step', choices=('namespace', 'inputs'), required=True)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--source-tree', required=True)
    args = parser.parse_args(argv)
    context = hosted_context()  # Refuse non-hosted invocation before effects.
    for which, value in ((resource.RLIMIT_AS, LIMITS['address_bytes']), (resource.RLIMIT_CPU, LIMITS['cpu_seconds']),
                         (resource.RLIMIT_FSIZE, LIMITS['file_bytes']), (resource.RLIMIT_NOFILE, LIMITS['descriptors'])):
        resource.setrlimit(which, (value, value))
    signal.signal(signal.SIGALRM, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    signal.alarm(LIMITS['wall_seconds'])
    result = dict(schema='g132.host-profile-' + args.step + '.v1', operation=OPERATION, authority='NONE',
                  source_commit=args.source_commit, source_tree=args.source_tree, context=context,
                  setup_pin=SETUP_PIN, nss_pin=NSS_PIN, limits=LIMITS, source_commands=[],
                  original_execution=False, private_inputs_selected=False, provider_acquired=False,
                  session_constructed=False, native_admission=False, overall_admission='UNQUALIFIED',
                  selected_gate_observation='REFUSED')
    output = None
    success = False
    try:
        with owner('qualify-work-graph-c5-setup.py', SETUP_PIN) as setup:
            source_identity(setup, args.source_commit, args.source_tree, result['source_commands'])
            output = output_directory(context, create=args.step == 'namespace')
            baseline = setup.fds()
            if args.step == 'namespace':
                # No active NSS lease. setup.main lowers hard limits permanently.
                capture = io.StringIO()
                try:
                    with redirect_stdout(capture):
                        result['namespace_return_code'] = setup.main()
                finally:
                    setup.emergency_cleanup()
                need(len(capture.getvalue().encode()) <= 32768, 'namespace owner report exceeds bound')
                result['namespace'] = json.loads(capture.getvalue())
                success = namespace_join(result, context, args.source_commit, args.source_tree)
            else:
                with held_bytes(output / 'namespace.json', 65536) as raw:
                    prior = json.loads(raw)
                    namespace_join(prior, context, args.source_commit, args.source_tree)
                    result['namespace_receipt'] = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                    with owner('hosted-files-only-nss.py', NSS_PIN) as nss:
                        current = setup.hosted_current_owner(ROOT)
                        with nss.hosted_files_only_nss(output / 'nss.json') as lease:
                            result['host_inputs'] = setup.receive_hosted_inputs(current)
                            current.CHECK()
                        result['nss_cleanup'] = lease.record
                        with held_bytes(output / 'nss.json', 16384) as closed:
                            need(json.loads(closed) == lease.record, 'NSS closing receipt differs')
                        result['nss_cleanup_admission'] = ('COMPLETE' if nss_cleanup_complete(lease.record)
                                                           else 'UNQUALIFIED_RETAINED_RESIDUAL')
                        host = result['host_inputs']
                        # Full startup remains the unchanged owner's separate result.
                        # Passing these selected gates cannot create runtime admission.
                        success = (len(host['pins']) == 12 and all(x['match'] is True for x in host['pins'])
                                   and len(host['system_aliases']) == 4 and all(x['match'] is True for x in host['system_aliases'])
                                   and host['nss']['result']['match'] is True and host['selected_bookends_equal'] is True
                                   and nss_cleanup_complete(lease.record))
                source_identity(setup, args.source_commit, args.source_tree, result['source_commands'])
            result['descriptor_restoration'] = setup.fds() == baseline
            need(result['descriptor_restoration'], 'ordinary descriptor restoration differs')
            need(hosted_context() == context, 'ordinary context closing bookend differs')
        result['selected_gate_observation'] = 'OBSERVED_SELECTED_GATE_PASS' if success else 'REFUSED'
    except BaseException as error:
        success = False
        result['failure'] = dict(type=type(error).__name__, reason=str(error)[:512])
    finally:
        signal.alarm(0)
    if output is not None:
        write_receipt(output / (args.step + '.json'), result, 65536 if args.step == 'namespace' else LIMITS['report_bytes'])
    print(json.dumps(dict(operation=OPERATION, step=args.step, success=success,
                          output=str(output) if output else None, overall_admission='UNQUALIFIED'), sort_keys=True))
    return 0 if success else 2


if __name__ == '__main__':
    raise SystemExit(main())
