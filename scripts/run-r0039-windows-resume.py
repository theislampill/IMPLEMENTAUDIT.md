#!/usr/bin/env python3
"""Prepare, execute once, and receive an explicitly entitled Windows DG30 operation.

Repo-only qualification tool. It never creates an invalidation, controller,
grant or fixture, and never retries, cleans up or compensates a native effect.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), Path(__file__).with_name(name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


Q = load('check-r0039-windows-resume')


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def physical(path):
    path = Path(path).absolute()
    Q.require('..' not in path.parts, 'parent traversal refused: ' + str(path))
    for part in (path, *path.parents):
        info = part.lstat()
        Q.require(not stat.S_ISLNK(info.st_mode)
                  and not getattr(info, 'st_file_attributes', 0) & 0x400, 'reparse/symlink path refused: ' + str(path))
    # Preserve the reparse/link refusal above before normalizing the physical
    # spelling (including Windows short-path aliases) for containment checks.
    return path.resolve(strict=True)


def separated_output(path, source, subject, *, existing=False):
    path = Path(path).absolute()
    Q.require('..' not in path.parts, 'parent traversal in evidence output refused')
    out = physical(path) if existing else physical(path.parent) / path.name
    Q.require(all(not out.is_relative_to(physical(root)) for root in (source, subject)),
              'evidence output must be separate from source and governed subject')
    return out


def read(path):
    path = physical(path)
    Q.require(path.is_file(), 'regular evidence file required')
    return path.read_bytes()


def ident(path):
    raw = read(path)
    return {'bytes': len(raw), 'sha256': Q.digest(raw)}


def save(path, value):
    raw = value if type(value) is bytes else canonical(value)
    with Path(path).open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def environment(tools):
    # Task-local physical executables. No inherited shell/Python/Git startup
    # overrides, WindowsApps aliases or credentials enter the owner process.
    git = Path(tools['git']['path'])
    Q.direct_git_layout(tools['git']['path'])
    root = git.parents[2]
    system = os.environ.get('SystemRoot', r'C:\Windows')
    env = {'SystemRoot': system, 'WINDIR': system, 'PATHEXT': '.COM;.EXE;.BAT;.CMD',
           'PATH': os.pathsep.join([str(Path(tools['python']['path']).parent),
                    str(git.parent), str(root / 'cmd'), str(root / 'bin'),
                    str(root / 'usr/bin'), str(Path(system) / 'System32')]),
           'IMPLEMENTAUDIT_PYTHON': tools['python']['path'], 'PYTHONDONTWRITEBYTECODE': '1',
           'LC_ALL': 'C', 'MSYS2_ARG_CONV_EXCL': '*'}
    for key in ('TEMP', 'TMP'):
        if key in os.environ:
            env[key] = os.environ[key]
    return env


def command(argv, cwd, env, out, label, *, require_success=True, timeout=180):
    result = subprocess.run([str(x) for x in argv], cwd=cwd, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    save(out / (label + '.stdout'), result.stdout)
    save(out / (label + '.stderr'), result.stderr)
    save(out / (label + '.json'), {'command': [str(x) for x in argv], 'exit_code': result.returncode,
                                 'stdout_sha256': Q.digest(result.stdout), 'stderr_sha256': Q.digest(result.stderr)})
    Q.require(not require_success or result.returncode == 0, 'readback failed: ' + label)
    return result


def git(request, repo, *args):
    env = environment(request['tools'])
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT='0')
    result = subprocess.run([request['tools']['git']['path'], '-C', str(repo), *args],
                            env=env, capture_output=True, timeout=30)
    Q.require(result.returncode == 0, 'Git identity/readback failed: ' + str(args[0]))
    return result.stdout


def claim(request, *args):
    return [request['tools']['bash']['path'], '--noprofile', '--norc',
            str(Path(request['subject_root']) / 'skills/implementaudit/scripts/claim-run.sh'), *args]


def source_snapshot(request):
    source, subject = physical(request['source_root']), physical(request['subject_root'])
    identity = git(request, source, 'rev-parse', 'HEAD', 'HEAD^{tree}').decode().splitlines()
    Q.require(identity == [request['source_head'], request['source_tree']], 'qualified source commit/tree changed')
    Q.require(git(request, source, 'status', '--porcelain=v1', '--untracked-files=normal') == b'',
              'source checkout must be clean; do not stash or repair it in this runner')
    runtime = {}
    names = git(request, source, 'ls-files', '-z', '--', 'skills/implementaudit/scripts',
                'skills/implementaudit/templates').decode().split('\0')
    for name in filter(None, names):
        expected = ident(source / name)
        Q.require(ident(subject / name) == expected, 'subject runtime differs from qualified source: ' + name)
        runtime[name] = expected
    Q.require(len(runtime) > 10, 'runtime source population incomplete')
    tools = {name: {'path': item['path'], 'sha256': ident(item['path'])['sha256']}
             for name, item in request['tools'].items()}
    Q.require(tools == request['tools'], 'native executable identity changed')
    recorder_files = {name: ident(Path(__file__).with_name(name)) for name in
                      ('run-r0039-windows-resume.py', 'check-r0039-windows-resume.py', 'r0039-windows-job.py')}
    for name, expected in recorder_files.items():
        Q.require(ident(source / 'scripts' / name) == expected, 'runner is not the qualified source copy')
    return {'source_head': identity[0], 'source_tree': identity[1], 'runtime': runtime, 'tools': tools,
            'recorders': recorder_files, 'subject_head_tree': git(request, subject, 'rev-parse', 'HEAD', 'HEAD^{tree}').decode().splitlines(),
            'subject_status': git(request, subject, 'status', '--porcelain=v1').decode(),
            'environment_sha256': Q.digest(canonical(environment(tools)))}


def refs(request):
    raw = git(request, request['subject_root'], 'for-each-ref', '--format=%(refname) %(objectname)', 'refs/implementaudit')
    controller = request['controller']
    exact = {'refs/implementaudit/' + family + '/' + controller for family in
             ('controllers', 'continuity-invalidations', 'current-generations', 'current-generation-migrations')}
    prefixes = tuple('refs/implementaudit/' + family + '/' + controller + '/'
                     for family in ('continuity-receipts', 'state-archives'))
    return {ref: oid for ref, oid in (line.split(' ', 1) for line in raw.decode().splitlines())
            if ref in exact or ref.startswith(prefixes)}



def unqualified_readback(request, prepared, out):
    """Retain observations after an attempted effect; never qualify or retry it.

    The recorded failure remains primary. Each query is independently bounded
    and may refuse; neither equal ref scans nor successful queries prove a
    coherent transition, receipt, currentness or native acceptance.
    """
    out.mkdir(exist_ok=False)
    snapshot = prepared['snapshot']
    observation = {'status': 'UNQUALIFIED_POST_ATTEMPT_OBSERVATION',
                   'authority_ceiling': 'NO_CURRENTNESS_TRANSITION_OR_NATIVE_ACCEPTANCE',
                   'automatic_retry': False, 'cleanup_or_compensation': False,
                   'queries': {}, 'errors': {}, 'started_utc': utc()}

    def unchanged(*, owner=False):
        # Check physical bytes without invoking potentially changed tools.
        Q.require(snapshot['tools'] == request['tools'], 'prepared tool identities differ')
        for item in request['tools'].values():
            Q.require(ident(item['path'])['sha256'] == item['sha256'],
                      'tool identity changed; unqualified query refused')
        if owner:
            for name, expected in snapshot['runtime'].items():
                Q.require(ident(Path(request['subject_root']) / name) == expected,
                          'runtime identity changed; unqualified owner query refused: ' + name)
            for name, expected in snapshot['recorders'].items():
                Q.require(ident(Path(__file__).with_name(name)) == expected,
                          'recorder identity changed; unqualified owner query refused: ' + name)

    def observe(label, action):
        try:
            return action()
        except Exception as error:
            observation['errors'][label] = {'exception': type(error).__name__, 'detail': str(error)}
            return None

    def observed_refs():
        unchanged()
        return refs(request)

    observation['refs_before_queries'] = observe('refs_before_queries', observed_refs)
    for flag, label in (('--resolve-canonical-generation', 'resolve-canonical'),
                        ('--resolve-resume-generation', 'resolve-resume'),
                        ('--require-current-continuity', 'require-current')):
        def query():
            unchanged(owner=True)
            result = command(claim(request, flag, request['controller']), request['subject_root'],
                             environment(request['tools']), out, label, require_success=False, timeout=30)
            return {'exit_code': result.returncode, 'stdout_sha256': Q.digest(result.stdout),
                    'stderr_sha256': Q.digest(result.stderr)}
        observation['queries'][label] = observe(label, query)
    observation['refs_after_queries'] = observe('refs_after_queries', observed_refs)

    def retained():
        _, paths = retained_paths(request, prepared['before'])
        return {role: observe('retained-' + role, lambda path=path: ident(path))
                for role, path in paths.items()}
    observation['retained_files'] = observe('retained_files', retained)
    first, last = observation['refs_before_queries'], observation['refs_after_queries']
    observation['ref_scans_equal'] = first == last if first is not None and last is not None else None
    observation['ended_utc'] = utc()
    save(out / 'OBSERVATION.json', observation)


def payload(raw):
    Q.require(raw.count(b'```json\n') == 1, 'exact protected projection JSON body required')
    body = Q.strict_json(raw.split(b'```json\n', 1)[1].split(b'\n```', 1)[0])
    Q.require(type(body) is dict and type(body.get('payload')) is dict, 'protected payload missing')
    return body['payload']


def retained_paths(request, before):
    subject = physical(request['subject_root'])
    run = physical(subject / before['run_root_identity'])
    Q.require(run.is_relative_to(subject / '.IMPLEMENTAUDIT/runs'), 'run escapes its subject')
    paths = {role: physical(before[key]) for role, key in [('STATE', 'state_path'), ('ROADMAP', 'roadmap_path'),
              ('protected', 'protected_manifest_path'), ('archive', 'archive_manifest_path')]}
    paths.update(retired_STATE=physical(run / 'STATE.md'), retired_ROADMAP=physical(run / 'ROADMAP.md'))
    Q.require(all(path.is_relative_to(run) for path in paths.values()), 'canonical evidence escapes run root')
    return run, paths


def preflight(request, out):
    out.mkdir(exist_ok=False)
    snapshot = source_snapshot(request)
    env, repo, ctrl = environment(request['tools']), request['subject_root'], request['controller']
    result = command(claim(request, '--resolve-resume-generation', ctrl), repo, env, out, '01-resolve')
    before = Q.strict_json(result.stdout)
    Q.require(before.get('controller') == ctrl, 'requested controller differs from actual source')
    run, paths = retained_paths(request, before)
    all_refs = refs(request)
    generation, epoch = before['next_projection_generation_id'], before['next_continuity_epoch']
    prefix = 'refs/implementaudit/state-archives/' + ctrl + '/'
    slots = {'generation_path_exists': os.path.lexists(run / 'state-generations' / generation),
             'archive_ref_oid': all_refs.get(prefix + generation),
             'epoch_ref_oid': all_refs.get(prefix + 'epochs/' + epoch),
             'publication_ref_oid': all_refs.get(prefix + 'epochs/' + epoch + '-publication'),
             'receipt_ref_oid': all_refs.get('refs/implementaudit/continuity-receipts/' + ctrl + '/' + epoch)}
    Q.validate_fresh_preflight(before, slots)
    refusal = command(claim(request, '--require-current-continuity', ctrl), repo, env, out, '02-invalidated', require_success=False)
    Q.require(refusal.returncode != 0, 'currentness already satisfied; no fresh operation to measure')
    tokens = ['--expected-pointer', before['pointer_token'], '--expected-invalidation', before['invalidation_token']]
    pair = {}
    # Separate completed subprocesses, STATE before ROADMAP. No effect here.
    for index, role in enumerate(('STATE', 'ROADMAP'), 3):
        raw = command(claim(request, '--read-resume-state', ctrl, '--role', role, *tokens), repo, env, out,
                      '%02d-%s' % (index, role)).stdout
        Q.require(raw == read(paths[role]), 'paired readback differs from canonical bytes')
        pair[role] = payload(raw)
    kept_refs = {ref: oid for ref, oid in all_refs.items() if ref != before['pointer_token'].split('@')[0]}
    retained = {'files': {role: ident(path) for role, path in paths.items()}, 'refs': kept_refs}
    Q.require(source_snapshot(request) == snapshot and refs(request) == all_refs, 'source or authority changed during preflight')
    command_line = claim(request, '--resume-controller', ctrl, '--boundary', before['boundary'],
                         '--epoch', epoch, *tokens)
    return {'snapshot': snapshot, 'before': before, 'fresh_slots': slots, 'payloads': pair,
            'retained': retained, 'command': command_line}


def native_control(request, out):
    """Actual launch-chain/memory control before any owner effect; no authority."""
    out.mkdir(exist_ok=False)
    probe = out / 'probe.py'
    save(probe, b'''import json, os, subprocess, sys, time
allocation = bytearray(32 * 1024 * 1024)
child = subprocess.Popen([sys.executable, '-I', '-c', 'import time; a=bytearray(32*1024*1024); time.sleep(1.0)'])
git = subprocess.Popen([sys.argv[1], 'hash-object', '--stdin'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
time.sleep(0.25)
git.communicate(b'constructed job measurement control')
child.wait()
print(json.dumps({'python_pid':os.getpid(),'child_pid':child.pid,'git_pid':git.pid,'child_exit':child.returncode,'git_exit':git.returncode}))
''')
    argv = [request['tools']['bash']['path'], '--noprofile', '--norc', '-c',
            'exec "$1" -I "$2" "$3"', 'dg30-job-control', request['tools']['python']['path'],
            str(probe), request['tools']['git']['path']]
    measured = load('r0039-windows-job').measure(argv, Path(request['subject_root']), environment(request['tools']), out / 'job')
    Q.validate_measurement(measured, argv, request['tools'])
    body = Q.strict_json(read(out / 'job/stdout.bin'))
    Q.require(body['child_exit'] == body['git_exit'] == 0, 'native launch-chain control failed')
    pids = {row['pid'] for row in measured['process_events'] if row['event'] == 'NEW_PROCESS'}
    Q.require({body['python_pid'], body['child_pid'], body['git_pid']} <= pids,
              'required native control process escaped measured Job')
    Q.require(measured['peak_job_committed_bytes'] >= 64 * 1024 * 1024
              and measured['peak_job_committed_bytes'] > measured['peak_single_process_committed_bytes'],
              'aggregate committed memory control did not discriminate a single-process peak')
    save(out / 'control.json', {'measurement': measured, 'process_readback': body,
                              'scope': 'ACTUAL_NATIVE_MEASUREMENT_CONTROL_ONLY'})
    return ident(out / 'control.json')


def execute(plan_path, expected_sha, entitlement):
    raw = read(plan_path)
    Q.require(Q.digest(raw) == expected_sha, 'prepared operation digest changed')
    plan = Q.strict_json(raw)
    Q.require(plan.get('schema') == 'implementaudit.dg30-windows-operation.v1'
              and type(entitlement) is str and entitlement.strip(), 'explicit external entitlement reference required')
    request = plan['request']
    root = separated_output(plan_path.parent, request['source_root'], request['subject_root'], existing=True)
    out = root / 'execution'
    out.mkdir(exist_ok=False)  # durable one-shot boundary; never overwrite/retry
    save(out / 'ATTEMPT.json', {'status': 'PREFLIGHT_ONLY', 'plan_sha256': expected_sha,
                              'entitlement_reference': entitlement, 'started_utc': utc(),
                              'authority': 'EXTERNAL_ENTITLEMENT_NOT_AUTHENTICATED_BY_THIS_TOOL'})
    launched = False
    try:
        current = preflight(request, out / 'preflight')
        Q.require(Q.same_json(current, plan['prepared']), 'prepared source, exact subject or preimage changed')
        controls = native_control(request, out / 'native-control')
        final = preflight(request, out / 'launch-preflight')
        Q.require(Q.same_json(final, current), 'source/authority changed during native measurement controls')
        save(out / 'LAUNCH_INTENT.json', {'command': current['command'], 'plan_sha256': expected_sha,
                                        'controls': controls, 'at_utc': utc(), 'automatic_retry': False})
        launched = True
        measured = load('r0039-windows-job').measure(current['command'], Path(request['subject_root']),
                                environment(request['tools']), out / 'operation')
        save(out / 'MEASUREMENT.json', measured)
        # Preserve and read state after every returned operation, including
        # numeric qualification failures. Never run another resume.
        env, repo, ctrl = environment(request['tools']), request['subject_root'], request['controller']
        token_raw = read(out / 'operation/stdout.bin')
        token = token_raw.decode('utf-8').strip()
        Q.require(measured['exit_code'] == 0 and token.startswith('refs/implementaudit/continuity-receipts/'),
                  'owner failed or returned no receipt; preserve effect for independent readback')
        verify = command(claim(request, '--verify-resume-receipt', token), repo, env, out, 'verify-receipt').stdout
        required = command(claim(request, '--require-current-continuity', ctrl), repo, env, out, 'require-current').stdout
        after = Q.strict_json(command(claim(request, '--resolve-canonical-generation', ctrl), repo, env, out, 'resolve-current').stdout)
        save(out / 'CURRENT.json', after)
        pair = {}
        for role in ('STATE', 'ROADMAP'):
            data = command(claim(request, '--read-canonical-state', ctrl, '--role', role,
                                '--expected-pointer', after['pointer_token']), repo, env, out, 'current-' + role).stdout
            pair[role] = payload(data)
        receipt_raw = git(request, repo, 'cat-file', 'blob', token.split('@')[1])
        save(out / 'RECEIPT.raw', receipt_raw)
        _, paths = retained_paths(request, current['before'])
        now_refs = refs(request)
        retained_after = {'files': {role: ident(path) for role, path in paths.items()},
                          'refs': {ref: now_refs.get(ref) for ref in current['retained']['refs']}}
        save(out / 'PRESERVED_AFTER.json', retained_after)
        Q.require(source_snapshot(request) == current['snapshot'], 'source/runtime/tool identities changed during operation')
        transition = Q.validate_transition(current['before'], after, receipt_raw, current['payloads'], pair,
                           current['retained'], retained_after, token_raw, verify, required)
        assessment = Q.validate_measurement(measured, current['command'], request['tools'])
        result = {'status': 'RECORDED_OPERATION_READY_FOR_INDEPENDENT_RECEIVING', 'measurement': assessment,
                  'transition': transition, 'source': current['snapshot'], 'controls': controls,
                  'plan_sha256': expected_sha, 'ended_utc': utc(),
                  'authority_ceiling': 'NO_H0_OR_C02_DG30_OR_ISSUE_ACCEPTANCE'}
        save(out / 'RESULT.json', result)
        print(json.dumps({'status': result['status'], 'result_file': str(out / 'RESULT.json'),
                          'authority_ceiling': result['authority_ceiling']}, indent=2))
    except BaseException as exc:
        try:
            save(out / 'FAILURE.json', {'status': 'OWNER_LAUNCH_ATTEMPTED_UNQUALIFIED' if launched else 'NO_OWNER_LAUNCH',
                                       'exception': type(exc).__name__, 'detail': str(exc),
                                       'automatic_retry': False, 'cleanup_or_compensation': False, 'ended_utc': utc()})
        except Exception:
            # Recording the primary failure is best-effort. A failed marker
            # write must neither replace it nor suppress eligible readback.
            pass
        if launched and isinstance(exc, Exception):
            try:
                unqualified_readback(request, current, out / 'unqualified-readback')
            except Exception as readback_error:
                # A diagnostic failure must not replace the owner/measurement
                # failure or turn this consumed attempt into a retry permission.
                try:
                    save(out / 'READBACK_FAILURE.json', {'exception': type(readback_error).__name__,
                         'detail': str(readback_error), 'automatic_retry': False})
                except Exception:
                    pass
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    prepare = subs.add_parser('prepare', help='read-only exact-current preparation; creates no native boundary')
    for name in ('source', 'repo', 'controller', 'source-head', 'source-tree', 'bash', 'python', 'git', 'out'):
        prepare.add_argument('--' + name, required=True)
    run = subs.add_parser('execute', help='one separately entitled operation; no automatic retry')
    run.add_argument('--plan', type=Path, required=True)
    run.add_argument('--plan-sha256', required=True)
    run.add_argument('--entitlement-reference', required=True)
    args = parser.parse_args()
    Q.require(os.name == 'nt' and sys.platform == 'win32', 'authentic Windows execution unavailable; nothing launched')
    if args.action == 'execute':
        execute(args.plan, args.plan_sha256, args.entitlement_reference)
        return
    Q.direct_git_layout(args.git)
    source = physical(args.source)
    subject = physical(args.repo)
    out = separated_output(args.out, source, subject)
    tools = {name: {'path': str(physical(getattr(args, name))), 'sha256': ident(getattr(args, name))['sha256']}
             for name in ('bash', 'python', 'git')}
    Q.require(Path(tools['python']['path']).samefile(sys.executable), 'run using the exact selected physical Python')
    Q.direct_git_layout(tools['git']['path'])
    out.mkdir(exist_ok=False)
    request = {'source_root': str(source), 'subject_root': str(subject), 'controller': args.controller,
               'source_head': args.source_head, 'source_tree': args.source_tree, 'tools': tools}
    prepared = preflight(request, out / 'preflight')
    plan = {'schema': 'implementaudit.dg30-windows-operation.v1', 'request': request, 'prepared': prepared,
            'prepared_utc': utc(), 'host': {'platform': platform.platform(), 'python': sys.version},
            'authority_ceiling': 'READ_ONLY_PREPARATION_NO_NATIVE_OPERATION_GRANT'}
    save(out / 'OPERATION.json', plan)
    print(json.dumps({'plan': str(out / 'OPERATION.json'), 'sha256': ident(out / 'OPERATION.json')['sha256'],
                      'status': 'PREPARED_ONLY_ENTITLED_EXECUTOR_REQUIRED'}, indent=2))


if __name__ == '__main__':
    main()
