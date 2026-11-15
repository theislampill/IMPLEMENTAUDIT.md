#!/usr/bin/env python3
"""One prelaunch host observation. No request, episode, or acceptance authority."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import types

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'engineering/pro-executor-g221-host-inventory-20261115'
BASE_COMMIT = '060902121a45b180853e630891caa5e6c9d2f704'
BASE_TREE = 'f74f43a029cca69dc28af9096e983c9e275f3436'
OWNER = 'qualification/dg16-r5-full-g2/'
WORKFLOW = '.github/workflows/dg16-g221-host-inventory.yml'
PINS = {
    'run.py': '688166071f33d2cb33c48a4136a88b7dccf719267e9fa43db72cffb361fdbd74',
    'host_utility.py': '02a15dc96ecce23e14a3a84bca880aa536d79fffc4f6d6160835cb4ba97a19b5',
    'evidence_io.py': 'c2f8d718c8acd3a223d494239e6bc19d4a90e3d5c66f49cdac8f701ce4807075',
    'native_profile.py': 'c16c75039b938718ab4bfee9e49a6c55322bdfda22f25d0a526cf74f87944c3d',
    'native_admission.py': 'd96262b67a18f62a7fe07264a3b5a08b5a8016a237d9b46ca7c781e234421342',
    'current_host.py': '893ad0f5c8b59d7bff47985cfe94ef8d76d5b1cbb76f4076c1efdf86fe10d3fc',
    'native_prerequisite.py': '594ac753bbfda9cfa3285a7c5a31018fd5384bb3d3f0afcd89bc29cea7749f42',
    'native_integration.py': 'c6f2b17e59369a04db2062b79ea2150c54d978fd1c0f18a9b25e094e303bc266',
}
PROVIDER = {
    'repository': ('GITHUB_REPOSITORY', r'[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}'),
    'ref': ('GITHUB_REF', r'refs/heads/[A-Za-z0-9_./-]{1,200}'),
    'sha': ('GITHUB_SHA', r'[0-9a-f]{40}'),
    'run_id': ('GITHUB_RUN_ID', r'[1-9][0-9]{0,19}'),
    'attempt': ('GITHUB_RUN_ATTEMPT', r'[1-9][0-9]{0,5}'),
    'event': ('GITHUB_EVENT_NAME', r'[a-z_]{1,40}'),
}
PREFIX = 'DG16_G221_HOST_INVENTORY '


class Refusal(Exception):
    pass


def need(value, code):
    if not value:
        raise Refusal(code)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def descriptor(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                git_blob=hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest())


def read_file(path):
    """Bounded ordinary-file read; execute only the bytes checked by the caller."""
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
         and before.st_size <= 256 * 1024, 'SOURCE_FILE_SHAPE_REFUSED')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        stamp = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        need(stamp(os.fstat(fd)) == stamp(before), 'SOURCE_OPEN_CHANGED')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(256 * 1024 + 1)
        need(len(raw) == before.st_size and stamp(os.fstat(fd)) == stamp(before)
             and stamp(path.lstat()) == stamp(before), 'SOURCE_READ_CHANGED')
        return raw
    finally:
        os.close(fd)


def verify_pin(name, raw):
    need(descriptor(raw)['sha256'] == PINS[name], 'OWNER_SOURCE_PIN_REFUSED')


def provider_fields(environment):
    # Invalid/missing values become null; arbitrary environment text is never logged.
    return {key: value if re.fullmatch(pattern, value) else None
            for key, (name, pattern) in PROVIDER.items()
            for value in (environment.get(name, ''),)}


def require_provider(provider, environment):
    need(all(value is not None for value in provider.values())
         and provider['repository'] == REPOSITORY
         and provider['ref'] == 'refs/heads/' + BRANCH
         and provider['event'] == 'push' and provider['attempt'] == '1'
         and environment.get('GITHUB_ACTIONS') == 'true'
         and environment.get('G221_PUSH_CREATED') == 'true'
         and environment.get('G221_PUSH_DELETED') == 'false', 'PROVIDER_CONTEXT_REFUSED')


def effect_denied(event, args):
    if event == 'open':
        mode, flags = args[1:3]
        return bool((isinstance(mode, str) and any(c in mode for c in 'wax+'))
                    or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
    return (event.startswith(('subprocess.', 'socket.', 'os.exec', 'os.spawn', 'os.posix_spawn', 'os.fork'))
            or event in {'os.system', 'os.mkdir', 'os.remove', 'os.rmdir', 'os.rename',
                         'os.link', 'os.symlink', 'os.chmod', 'os.chown', 'os.truncate',
                         'os.utime', 'os.setxattr', 'os.removexattr', 'os.chdir', 'os.putenv', 'os.unsetenv'})


def failure(exc, stage):
    # Owner refusal codes are fixed public tokens. Never print exception messages/paths.
    message = str(exc)
    code = message if re.fullmatch(r'[A-Z][A-Z0-9_]{0,95}', message) else 'OBSERVATION_EXCEPTION_REFUSED'
    return dict(stage=stage, code=code, exception=type(exc).__name__,
                errno=exc.errno if isinstance(exc, OSError) else None)


def observe(local=False):
    root = Path(__file__).absolute().parents[2]
    provider = provider_fields(os.environ)
    result = dict(schema='dg16.g221-prelaunch-host-inventory.v1', authority='NONE',
        scope='PRELAUNCH_OBSERVATION_ONLY', context='LOCAL_UNHOSTED' if local else 'GITHUB_HOSTED',
        status='REFUSED', provider=provider, source_base_commit=BASE_COMMIT, source_base_tree=BASE_TREE,
        sources={}, source_closing_verified=False, host=None, tool_paths=None,
        selected_tuple=None, selected_tuple_sha256=None, selected_candidates_sha256=None,
        selected_match=None, first_refusal=None, closing_refusal=None,
        same_job_earned_qualification=False, currentness=False,
        future_g221_acceptance=False, effect_grant=False)
    held = {}
    active = [False]

    def audit(event, args):
        if active[0] and effect_denied(event, args):
            raise Refusal('OBSERVATION_EFFECT_REFUSED')

    sys.addaudithook(audit)
    stage = 'SOURCE'
    try:
        need(root.resolve(strict=True) == root, 'SOURCE_ROOT_ALIAS_REFUSED')
        need(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,
             'ISOLATED_SYSTEM_PYTHON_REQUIRED')
        for relative in ('qualification/dg16-g221-host-inventory/observe.py', WORKFLOW):
            held[relative] = read_file(root / relative)
            result['sources'][relative] = descriptor(held[relative])
        if not local:
            need(globals().get('_HELD_OBSERVER_BYTES') == held['qualification/dg16-g221-host-inventory/observe.py'],
                 'HELD_OBSERVER_REQUIRED')
            stage = 'PROVIDER'
            require_provider(provider, os.environ)
        stage = 'OWNER_SOURCE'
        for name in PINS:
            relative = OWNER + name
            raw = read_file(root / relative)
            result['sources'][relative] = dict(descriptor(raw), expected_sha256=PINS[name])
            verify_pin(name, raw)
            held[relative] = raw
        # All eight owner modules are pinned before any owner module is executed.
        # Original loaders also hash their held compile bytes and close native reads.
        stage = 'MODULE_LOAD'
        active[0] = True
        adapter = types.ModuleType('g221_observation_adapter')
        adapter.__file__ = str(root / OWNER / 'run.py')
        exec(compile(held[OWNER + 'run.py'], adapter.__file__, 'exec'), adapter.__dict__)
        utility = adapter.load_utility()
        native = adapter.load_native(utility)  # Inert module construction, not admission.
        result['selected_candidates_sha256'] = hashlib.sha256(native.E.encode(list(native.C.SELECTED_HOSTS))).hexdigest()
        stage = 'INVENTORY'
        paths, host = adapter.inventory(utility)
        result['host'], result['tool_paths'] = host, paths
        stage = 'SELECTED_TUPLE'
        selected = native.C.target_host(host)
        selected_raw = native.E.encode(selected)
        result['selected_tuple'] = selected
        result['selected_tuple_sha256'] = hashlib.sha256(selected_raw).hexdigest()
        result['selected_match'] = any(selected_raw == native.E.encode(candidate)
                                       for candidate in native.C.SELECTED_HOSTS)
        need(result['selected_match'], 'G2_CURRENT_HOST_SELECTED_TUPLE_REFUSED')
        need(not local, 'LOCAL_OBSERVATION_HAS_NO_HOSTED_CONTEXT')
        result['status'] = 'SELECTED_TUPLE_MATCH_OBSERVED'
    except Exception as exc:
        result['first_refusal'] = failure(exc, stage)
    finally:
        active[0] = False
        try:
            for relative, raw in held.items():
                need(read_file(root / relative) == raw, 'SOURCE_CLOSING_CHANGED')
            result['source_closing_verified'] = len(held) == len(PINS) + 2
        except Exception as exc:
            result['closing_refusal'] = failure(exc, 'SOURCE_CLOSING')
            if result['first_refusal'] is None:
                result['first_refusal'] = result['closing_refusal']
            result['status'] = 'REFUSED'
    return result


def emit(result, output):
    raw = canonical(result)
    need(len(raw) <= 64 * 1024, 'PUBLIC_OBSERVATION_BOUND')
    digest = hashlib.sha256(raw).hexdigest()
    # This exact canonical body (including final LF) is independently recoverable.
    print(PREFIX + 'sha256=' + digest + ' base64=' + base64.b64encode(raw).decode('ascii'), flush=True)
    output = output.absolute()
    need(output.parent.resolve(strict=True) == output.parent, 'OUTPUT_PARENT_ALIAS_REFUSED')
    output.mkdir(mode=0o700)  # Fresh output only; never overwrite earlier evidence.
    for name, body in (('OBSERVATION.json', raw), ('OBSERVATION.sha256', (digest + '  OBSERVATION.json\n').encode('ascii'))):
        with (output / name).open('xb') as stream:
            stream.write(body)
        need((output / name).read_bytes() == body, 'OUTPUT_READBACK_REFUSED')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--local', action='store_true', help='Unhosted read-only diagnostic; always exits nonzero.')
    args = parser.parse_args()
    result = observe(args.local)
    try:
        emit(result, args.output)
    except Exception as exc:
        print('DG16_G221_HOST_INVENTORY_RETENTION_REFUSED ' + canonical(failure(exc, 'RETENTION')).decode().strip(), flush=True)
        return 1
    return 0 if result['status'] == 'SELECTED_TUPLE_MATCH_OBSERVED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
