#!/usr/bin/env python3
"""One held GitHub job for the unchanged C02-06 preparation and native driver.

This adapter creates no review or GO. Only the fixed public control branch can
supply those data after this job's public preparation has been reviewed. Raw
native/canonical evidence stays outside both public artifact directories.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import signal
import stat
import subprocess
import sys
import time
import urllib.request

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
REMOTE = 'https://github.com/' + REPOSITORY + '.git'
WORKFLOW_BRANCH = 'pro/dg18-isolated-c02-20261106'
CONTROL_BRANCH = 'pro/dg18-isolated-c02-control-20261106'
SOURCE_COMMIT = '35bf9823856eb4efe254b882954120480632230e'
SOURCE_TREE = 'abe08aabc83de3b27c43e6acf28646fb089f0f34'
BUNDLE_SHA = '8eaac37fa830514e455e394c3777083e35be300589d4d764830a3dcb1114e94e'
ARCHIVE_URL = 'https://registry.npmjs.org/@openai/codex/-/codex-0.166.0-linux-x64.tgz'
ARCHIVE_BYTES = 172325449
ARCHIVE_SHA = 'cbc00a26d3d0e2ceefc4be8891f8a81ef1e349b3b175bc0ae308762bc001fd93'
ADAPTER_RELATIVE = 'qualification/dg18-isolated-c02/held'
BUNDLE_RELATIVE = 'qualification/dg18-isolated-c02/bundle'
WORKFLOW_RELATIVE = '.github/workflows/dg18-isolated-c02.yml'
PREPARED_NAMES = frozenset(('AUTHORIZATION_FORMATS.json', 'DESIGN.md', 'INPUT_MANIFEST.json',
    'PROTOCOL_PLAN.json', 'PROSPECTIVE_INPUT_DELTA.json', 'PUBLIC_SCOPE.md',
    'REVIEW_REQUEST.json', 'VERIFICATION.json', 'c02_native_tail.py', 'receive_tail.py'))
REVIEW_NAME = 'INDEPENDENT_TECHNICAL_REVIEW.json'
GO_NAME = 'ROOT_GO.json'
CONTROL_NAMES = frozenset(('CONTROL.json', REVIEW_NAME, GO_NAME))
AUTH_ALLOCATIONS = ['fresh-subject', 'fresh-controller', 'owned-binary-copy',
    'one-native-app-server', 'one-loopback-emulated-provider', 'local-emulated-MCP',
    'existing-host-store', 'controlled-C02', 'one-later-native-compaction-resume',
    'independent-readback']
SUBJECT = '/tmp/dg18-isolated-c02-20261106-01'
CONTROLLER = 'dg18-isolated-c02-20261106-01'
BINARY = '/tmp/dg18-isolated-c02-bin-20261106-01/codex'
HOLD_SECONDS = 1500
POLL_SECONDS = 30
DRIVER_SECONDS = 960  # Original driver: 900 seconds, then bounded 40-second cleanup.
INTERRUPT_GRACE_SECONDS = 60
INPUT_FILE_BYTES = 512 * 1024 * 1024  # Existing host builder ceiling; reads stay streaming.
PUBLIC_RESULT_BYTES = 4096
CLEAN_ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC',
    'PYTHONDONTWRITEBYTECODE': '1', 'GIT_CONFIG_NOSYSTEM': '1',
    'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_SYSTEM': '/dev/null',
    'GIT_TERMINAL_PROMPT': '0', 'GIT_OPTIONAL_LOCKS': '0'}

PUBLIC_REASON_CODES = frozenset(('ADAPTER_CODE_CHANGED', 'ADAPTER_LOCATION', 'ADAPTER_SEAL_NAME', 'ADAPTER_SEAL_POPULATION', 'ADAPTER_SEAL_SCHEMA', 'ARCHIVE_BYTE_BOUND', 'ARCHIVE_DOWNLOAD_DEADLINE', 'ARCHIVE_REDIRECT_NOT_ADMITTED', 'BUNDLE_SEAL_NAME', 'C02_06_BUNDLE_MEMBER_CHANGED', 'C02_06_BUNDLE_POPULATION', 'C02_06_BUNDLE_SEAL_CHANGED', 'CONTROL_AUTHORIZATION_PIN', 'CONTROL_BINDING_MISMATCH', 'CONTROL_BRANCH_MOVED_NO_DISPATCH', 'CONTROL_DECISION', 'CONTROL_ENTRY_MUST_BE_REGULAR_BLOB', 'CONTROL_FILE_BYTE_BOUND', 'CONTROL_FILE_POPULATION', 'CONTROL_FILE_SIZE_CHANGED', 'CONTROL_OBJECT_REQUIRED', 'CONTROL_REF_FORMAT', 'CONTROL_REF_POPULATION', 'DRIVER_FAILED_PRESERVED_NO_RETRY', 'DRIVER_OUTER_INTERRUPTION_NO_RETRY', 'DUPLICATE_JSON_KEY', 'FILE_CHANGED_DURING_READ', 'FIRST_RUN_ATTEMPT_ONLY', 'GIT_METADATA_BYTE_BOUND', 'GO_CONTROL_POPULATION', 'HELD_FILE_IDENTITY_CHANGED', 'HELD_REQUEST_CHANGED', 'HELD_SEAL_CHANGED', 'HOLD_EXPIRED_NO_DISPATCH', 'HOST_PREPARE_FAILED', 'INDEPENDENT_REVIEW_SCOPE', 'INPUT_CENSUS_OR_SOURCE', 'MANIFEST_SEAL_MISMATCH', 'NONCANONICAL_PATH', 'NONFINITE_JSON', 'OFFICIAL_ARCHIVE_PIN', 'PREDISPATCH_CHECK_FAILED', 'PREPARATION_CHECK_FAILED', 'PREPARATION_CHECK_SCOPE', 'PREPARATION_MEMBER_CHANGED', 'PREPARATION_POPULATION', 'PREPARATION_SEAL_POPULATION', 'PREPARATION_SEAL_SCHEMA', 'PRIVATE_WORK_DIRECTORY_REQUIRED', 'PUBLIC_GIT_READ_FAILED', 'PUBLIC_PACKET_CHANGED', 'PUBLIC_PACKET_DIFFERS_FROM_HELD_INPUT', 'PUBLIC_PREPARATION_POPULATION', 'ROOT_GO_SCOPE', 'ROOT_STOP_NO_DISPATCH', 'STOP_CONTROL_POPULATION', 'SYMLINK_PATH', 'UNEXPECTED_ORCHESTRATION_FAILURE', 'UNSUPPORTED_FILE', 'WORKFLOW_CHECKOUT_CHANGED', 'WORKFLOW_COMMIT', 'WORKFLOW_TRACKED_FILES_CHANGED', 'WORK_DIRECTORY'))
PUBLIC_REASON_CODES |= frozenset(('INPUT_ANCESTOR_CUSTODY', 'INPUT_MANIFEST_SCOPE',
    'INPUT_MEMBER_SHAPE', 'INPUT_MEMBER_POPULATION', 'INPUT_STREAM_CHANGED',
    'INPUT_STREAM_PIN', 'INPUT_INVOCATION_CUSTODY', 'INPUT_INVOCATION_BOUND',
    'HELD_INPUT_CUSTODY_BINDING', 'HELD_INPUT_CUSTODY_CHANGED',
    'PUBLIC_REQUEST_BINDING_REFUSED', 'PUBLIC_SUMMARY_BYTE_BOUND'))


class Refusal(Exception):
    """Only fixed adapter reason codes, never raw provider or exception text."""


def need(condition, code):
    if not condition:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, 'DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(Refusal('NONFINITE_JSON')))


def identity(s):
    return [s.st_dev, s.st_ino, s.st_mode, s.st_uid, s.st_nlink,
            s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def regular(path, maximum=4 * 1024 * 1024):
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts, 'NONCANONICAL_PATH')
    for p in (path, *path.parents):
        need(not stat.S_ISLNK(p.lstat().st_mode), 'SYMLINK_PATH')
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= maximum,
         'UNSUPPORTED_FILE')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        raw = stream.read(maximum + 1)
        opened = os.fstat(stream.fileno())
    need(len(raw) <= maximum and identity(before) == identity(opened) == identity(path.lstat()),
         'FILE_CHANGED_DURING_READ')
    return raw, identity(before)


def write_new(path, raw, mode=0o600):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.chmod(path, mode)


def git(args, timeout=30, allow_missing=False, *, file_creation_mask=-1):
    done = subprocess.run(['/usr/bin/git', *args], env=CLEAN_ENV, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=timeout,
                          umask=file_creation_mask)
    need(len(done.stdout) <= 65536, 'GIT_METADATA_BYTE_BOUND')
    if allow_missing and done.returncode != 0:
        return None
    need(done.returncode == 0, 'PUBLIC_GIT_READ_FAILED')
    return done.stdout


def code_pins(work):
    worker = work / 'worker'
    adapter = worker / ADAPTER_RELATIVE
    need(Path(__file__).resolve(strict=True) == adapter / 'held_control.py', 'ADAPTER_LOCATION')
    seal_raw, seal_id = regular(adapter / 'ADAPTER_SEAL.json')
    seal = parse(seal_raw)
    need(seal.get('schema') == 'r5.c02-held-adapter-code.v1', 'ADAPTER_SEAL_SCHEMA')
    identities = {str(adapter / 'ADAPTER_SEAL.json'): seal_id}
    names = set()
    for entry in seal['files']:
        name = entry['name']
        need(isinstance(name, str) and '/' not in name and name not in names, 'ADAPTER_SEAL_NAME')
        names.add(name)
        path = worker / WORKFLOW_RELATIVE if name == 'dg18-isolated-c02.yml' else adapter / name
        raw, stamp = regular(path)
        need(sha(raw) == entry['sha256'] and len(raw) == entry['bytes']
             and stat.S_IMODE(stamp[2]) == entry['mode'], 'ADAPTER_CODE_CHANGED')
        identities[str(path)] = stamp
    need(names == {'held_control.py', 'dg18-isolated-c02.yml', 'README.md', 'CONTROL_FORMAT.md', 'STATIC_CHECK.json'},
         'ADAPTER_SEAL_POPULATION')
    bundle = worker / BUNDLE_RELATIVE
    bundle_raw, bundle_id = regular(bundle / 'BUNDLE_SEAL.json')
    need(sha(bundle_raw) == BUNDLE_SHA, 'C02_06_BUNDLE_SEAL_CHANGED')
    identities[str(bundle / 'BUNDLE_SEAL.json')] = bundle_id
    bnames = set()
    for entry in parse(bundle_raw)['files']:
        name = entry['name']
        need(isinstance(name, str) and not Path(name).is_absolute()
             and '..' not in Path(name).parts and name not in bnames, 'BUNDLE_SEAL_NAME')
        bnames.add(name)
        raw, stamp = regular(bundle / name)
        need(sha(raw) == entry['sha256'] and len(raw) == entry['bytes']
             and stat.S_IMODE(stamp[2]) == entry['mode'], 'C02_06_BUNDLE_MEMBER_CHANGED')
        identities[str(bundle / name)] = stamp
    need(len(bnames) == 18, 'C02_06_BUNDLE_POPULATION')
    return sha(seal_raw), identities


def prepared_pins(work):
    packet = work / 'dg18-c02-iso'
    need(set(p.name for p in packet.iterdir()) == PREPARED_NAMES | {'SEALED_PREPARATION.json'},
         'PREPARATION_POPULATION')
    seal_raw, seal_id = regular(packet / 'SEALED_PREPARATION.json')
    seal = parse(seal_raw)
    need(seal.get('schema') == 'implementaudit.r5.c02-native-tail-sealed-preparation.v1'
         and seal.get('authority') == 'PREPARATION_ONLY', 'PREPARATION_SEAL_SCHEMA')
    names = [entry['name'] for entry in seal['files']]
    need(len(names) == 10 and set(names) == PREPARED_NAMES, 'PREPARATION_SEAL_POPULATION')
    identities = {str(packet / 'SEALED_PREPARATION.json'): seal_id}
    for entry in seal['files']:
        path = packet / entry['name']
        raw, stamp = regular(path)
        need(len(raw) == entry['bytes'] and sha(raw) == entry['sha256']
             and stat.S_IMODE(stamp[2]) == entry['mode'] == 0o644, 'PREPARATION_MEMBER_CHANGED')
        identities[str(path)] = stamp
    manifest_raw, _ = regular(packet / 'INPUT_MANIFEST.json')
    need(sha(manifest_raw) == seal['input_manifest_sha256'], 'MANIFEST_SEAL_MISMATCH')
    manifest = parse(manifest_raw)
    need(len(manifest['members']) == 92 and manifest['source_commit'] == SOURCE_COMMIT
         and manifest['source_tree'] == SOURCE_TREE, 'INPUT_CENSUS_OR_SOURCE')
    return sha(seal_raw), seal['input_manifest_sha256'], identities


def directory_custody(path):
    """Stable ancestor identity; directory entry/timestamp changes are not custody."""
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts, 'INPUT_ANCESTOR_CUSTODY')
    result = []
    for node in (*reversed(path.parents), path):
        info = node.lstat()
        need(stat.S_ISDIR(info.st_mode), 'INPUT_ANCESTOR_CUSTODY')
        result.append({'path': str(node), 'identity':
            [info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid]})
    return result


def invocation_custody(invocation, expected):
    """Bind every actual system invocation hop, including same-target symlinks."""
    need(type(invocation) is str and 0 < len(os.fsencode(invocation)) <= 4096,
         'INPUT_INVOCATION_BOUND')
    path = Path(invocation)
    need(path.is_absolute() and str(path) == invocation and '..' not in path.parts,
         'INPUT_INVOCATION_CUSTODY')
    current, pending = Path('/'), list(path.parts[1:])
    nodes = directory_custody(current)
    steps = links = 0
    while pending:
        steps += 1
        need(steps <= 256, 'INPUT_INVOCATION_BOUND')
        part = pending.pop(0)
        if part == '.':
            continue
        if part == '..':
            current = current.parent
            continue
        node = current / part
        before = node.lstat()
        if stat.S_ISLNK(before.st_mode):
            links += 1
            target = os.readlink(node)
            after = node.lstat()
            need(links <= 40 and len(os.fsencode(target)) <= 4096,
                 'INPUT_INVOCATION_BOUND')
            need(identity(before) == identity(after) and before.st_gid == after.st_gid,
                 'INPUT_INVOCATION_CUSTODY')
            nodes.append({'path': str(node), 'identity': identity(before),
                          'gid': before.st_gid, 'target': target})
            target_path = Path(target)
            if target_path.is_absolute():
                current = Path('/')
                pending = list(target_path.parts[1:]) + pending
            else:
                pending = list(target_path.parts) + pending
        else:
            if pending:
                need(stat.S_ISDIR(before.st_mode), 'INPUT_INVOCATION_CUSTODY')
                stamp = [before.st_dev, before.st_ino, before.st_mode, before.st_uid, before.st_gid]
            else:
                need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                     'INPUT_INVOCATION_CUSTODY')
                stamp = identity(before) + [before.st_gid]
            nodes.append({'path': str(node), 'identity': stamp})
            current = node
    need(str(current) == expected and str(path.resolve(strict=True)) == expected,
         'INPUT_INVOCATION_CUSTODY')
    return {'invocation': invocation, 'resolved': expected, 'nodes': nodes}


def streamed_input_custody(item, deadline_ns=None):
    path = Path(item['path'])
    ancestors = directory_custody(path.parent)
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
         and before.st_size == item['bytes']
         and stat.S_IMODE(before.st_mode) == item['mode'], 'INPUT_STREAM_PIN')
    digest, size = hashlib.sha256(), 0
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        need(identity(before) == identity(opened) and before.st_gid == opened.st_gid,
             'INPUT_STREAM_CHANGED')
        while True:
            if deadline_ns is not None:
                need(time.monotonic_ns() < deadline_ns, 'HOLD_EXPIRED_NO_DISPATCH')
            block = stream.read(min(1024 * 1024, item['bytes'] - size + 1))
            if not block:
                break
            size += len(block)
            need(size <= item['bytes'], 'INPUT_STREAM_PIN')
            digest.update(block)
        opened = os.fstat(stream.fileno())
    after = path.lstat()
    need(identity(before) == identity(opened) == identity(after)
         and before.st_gid == opened.st_gid == after.st_gid
         and ancestors == directory_custody(path.parent), 'INPUT_STREAM_CHANGED')
    need(size == item['bytes'] and digest.hexdigest() == item['sha256'], 'INPUT_STREAM_PIN')
    return {'key': item['key'], 'path': str(path), 'identity': identity(before),
            'gid': before.st_gid, 'mode': item['mode'], 'bytes': size,
            'sha256': digest.hexdigest(), 'ancestors': ancestors}


def input_custody(work, manifest_sha, deadline_ns=None):
    """Read-only census of the exact 92 existing inputs; no fresh native allocation."""
    raw, _ = regular(work / 'dg18-c02-iso/INPUT_MANIFEST.json')
    need(sha(raw) == manifest_sha, 'MANIFEST_SEAL_MISMATCH')
    manifest = parse(raw)
    need(type(manifest) is dict and manifest.get('source_root') == str(work / 'source')
         and manifest.get('source_commit') == SOURCE_COMMIT and manifest.get('source_tree') == SOURCE_TREE
         and manifest.get('prospective_subject') == SUBJECT and manifest.get('prospective_controller') == CONTROLLER
         and type(manifest.get('members')) is list and len(manifest['members']) == 92,
         'INPUT_MANIFEST_SCOPE')
    rows, keys, paths = [], set(), set()
    for item in manifest['members']:
        need(type(item) is dict and type(item.get('key')) is str and 0 < len(item['key']) <= 512
             and type(item.get('path')) is str and 0 < len(os.fsencode(item['path'])) <= 4096
             and type(item.get('bytes')) is int and 0 <= item['bytes'] <= INPUT_FILE_BYTES
             and type(item.get('mode')) is int and 0 <= item['mode'] <= 0o7777
             and type(item.get('sha256')) is str and re.fullmatch('[0-9a-f]{64}', item['sha256'])
             and type(item.get('category')) is str, 'INPUT_MEMBER_SHAPE')
        path = Path(item['path'])
        need(path.is_absolute() and str(path) == item['path'] and '..' not in path.parts
             and item['key'] not in keys and item['path'] not in paths, 'INPUT_MEMBER_POPULATION')
        keys.add(item['key'])
        paths.add(item['path'])
        invocation = invocation_custody(item.get('invocation'), item['path']) if item['category'] == 'system-runtime' else None
        row = streamed_input_custody(item, deadline_ns)
        if invocation is not None:
            need(invocation == invocation_custody(item['invocation'], item['path']),
                 'INPUT_INVOCATION_CUSTODY')
            row['system_invocation'] = invocation
        rows.append(row)
    return {'schema': 'implementaudit.r5.c02-held-input-custody.v1',
            'input_manifest_sha256': manifest_sha, 'members': rows}


def private_command(command, work, label, timeout):
    # Never inherit Actions runtime tokens, personal auth or ambient provider configuration.
    with (work / (label + '.stdout')).open('xb') as out, (work / (label + '.stderr')).open('xb') as err:
        done = subprocess.run(command, env=CLEAN_ENV, stdin=subprocess.DEVNULL,
                              stdout=out, stderr=err, timeout=timeout)
    need(done.returncode == 0, label.upper() + '_FAILED')
    return regular(work / (label + '.stdout'))[0]


def download_archive(work):
    path = work / 'codex-0.166.0-linux-x64.tgz'
    deadline = time.monotonic() + 240
    digest = hashlib.sha256()
    size = 0
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(ARCHIVE_URL, timeout=30) as response, path.open('xb') as output:
        need(response.geturl() == ARCHIVE_URL, 'ARCHIVE_REDIRECT_NOT_ADMITTED')
        while True:
            need(time.monotonic() < deadline, 'ARCHIVE_DOWNLOAD_DEADLINE')
            block = response.read(1024 * 1024)
            if not block:
                break
            size += len(block)
            need(size <= ARCHIVE_BYTES, 'ARCHIVE_BYTE_BOUND')
            digest.update(block)
            output.write(block)
    need(size == ARCHIVE_BYTES and digest.hexdigest() == ARCHIVE_SHA, 'OFFICIAL_ARCHIVE_PIN')
    os.chmod(path, 0o644)
    return path


def prepare(work, run_id, run_attempt, workflow_commit):
    need(bool(re.fullmatch('[1-9][0-9]{0,23}', run_id)) and run_attempt == '1', 'FIRST_RUN_ATTEMPT_ONLY')
    need(bool(re.fullmatch('[0-9a-f]{40}', workflow_commit)), 'WORKFLOW_COMMIT')
    adapter_seal, code_ids = code_pins(work)
    worker = work / 'worker'
    need(git(['-C', str(worker), 'rev-parse', 'HEAD']).decode().strip() == workflow_commit,
         'WORKFLOW_CHECKOUT_CHANGED')
    need(not git(['-C', str(worker), 'status', '--porcelain=v1', '--untracked-files=no']),
         'WORKFLOW_TRACKED_FILES_CHANGED')
    git(['-C', str(worker), 'fetch', '--quiet', '--no-tags', '--depth=1', REMOTE, SOURCE_COMMIT], timeout=120)
    git(['-C', str(worker), 'worktree', 'add', '--quiet', '--detach', str(work / 'source'), SOURCE_COMMIT], timeout=60,
        file_creation_mask=0o022)
    archive = download_archive(work)
    bundle = worker / BUNDLE_RELATIVE
    private_command(['/usr/bin/python3', '-I', '-B', str(bundle / 'prepare_on_host.py'),
        '--source', str(work / 'source'), '--archive', str(archive), '--output-parent', str(work),
        '--output', str(work / 'dg18-c02-iso')], work, 'host_prepare', 180)
    check_raw = private_command(['/usr/bin/python3', '-I', '-B', str(work / 'dg18-c02-iso/c02_native_tail.py'),
        '--prepare-check'], work, 'preparation_check', 120)
    check = parse(check_raw)
    need(check.get('status') == 'PREPARATION_CHECK_PASS' and check.get('pinned_input_count') == 92
         and check.get('authority') == 'NONE' and check.get('owner_imported_or_invoked') is False
         and check.get('actual_transaction_or_tail_proved') is False, 'PREPARATION_CHECK_SCOPE')
    prep_sha, input_sha, prep_ids = prepared_pins(work)
    custody = input_custody(work, input_sha)
    now = time.monotonic_ns()
    request = {'schema': 'implementaudit.r5.c02-held-request.v1', 'authority': 'PREPARATION_ONLY',
        'repository': REPOSITORY, 'workflow_branch': WORKFLOW_BRANCH, 'workflow_commit': workflow_commit,
        'run_id': run_id, 'run_attempt': run_attempt, 'job': 'c02', 'nonce': os.urandom(16).hex(),
        'preparation_sha256': prep_sha, 'input_manifest_sha256': input_sha,
        'input_custody_sha256': sha(encode(custody)), 'input_custody_count': 92,
        'code_bundle_sha256': BUNDLE_SHA, 'held_adapter_seal_sha256': adapter_seal,
        'adapter_sha256': sha(regular(Path(__file__).resolve())[0]),
        'workflow_sha256': sha(regular(worker / WORKFLOW_RELATIVE)[0]),
        'source_commit': SOURCE_COMMIT, 'source_tree': SOURCE_TREE,
        'preparation_check_status': check['status'], 'preparation_check_sha256': sha(check_raw),
        'control_branch': CONTROL_BRANCH, 'control_path': 'dg18-c02-iso/' + run_id + '/1',
        'created_unix_seconds': int(time.time()), 'hold_seconds': HOLD_SECONDS,
        'execution_authorized': False, 'original_acceptance': False, 'authentic_OR': False}
    request_raw = encode(request)
    write_new(work / 'HOST_REQUEST.json', request_raw, 0o644)
    ids = dict(code_ids, **prep_ids)
    ids[str(work / 'HOST_REQUEST.json')] = regular(work / 'HOST_REQUEST.json')[1]
    state = {'schema': 'implementaudit.r5.c02-held-private-state.v1', 'request_sha256': sha(request_raw),
             'deadline_monotonic_ns': now + HOLD_SECONDS * 1000000000, 'identities': ids,
             'input_custody': custody}
    write_new(work / 'HOST_STATE.json', encode(state), 0o400)
    public = work / 'public-preparation'
    public.mkdir(mode=0o700)
    for name in sorted(PREPARED_NAMES | {'SEALED_PREPARATION.json'}):
        write_new(public / name, regular(work / 'dg18-c02-iso' / name)[0], 0o644)
    write_new(public / 'HOST_REQUEST.json', request_raw, 0o644)
    need(set(p.name for p in public.iterdir()) == PREPARED_NAMES | {'SEALED_PREPARATION.json', 'HOST_REQUEST.json'},
         'PUBLIC_PREPARATION_POPULATION')
    print(json.dumps({'status': 'PREPARED_AWAITING_ACTUAL_REVIEW_AND_ROOT_GO',
        'request_sha256': sha(request_raw), 'preparation_sha256': prep_sha, 'public_file_count': 12,
        'hold_seconds': HOLD_SECONDS, 'execution_authorized': False}, sort_keys=True), flush=True)


def current_control_head():
    try:
        raw = git(['ls-remote', '--exit-code', '--refs', REMOTE, 'refs/heads/' + CONTROL_BRANCH],
                  timeout=20, allow_missing=True)
    except subprocess.TimeoutExpired:
        return None
    if raw is None:
        return None
    lines = raw.decode('ascii').splitlines()
    need(len(lines) == 1, 'CONTROL_REF_POPULATION')
    parts = lines[0].split('\t')
    need(len(parts) == 2 and bool(re.fullmatch('[0-9a-f]{40}', parts[0]))
         and parts[1] == 'refs/heads/' + CONTROL_BRANCH, 'CONTROL_REF_FORMAT')
    return parts[0]


def read_control_commit(work, commit, prefix):
    cache = work / 'control-cache.git'
    git(['--git-dir', str(cache), 'fetch', '--quiet', '--no-tags', '--depth=1', REMOTE, commit], timeout=30)
    raw = git(['--git-dir', str(cache), 'ls-tree', commit + ':' + prefix], allow_missing=True)
    if raw is None:
        return None
    names = []
    for row in raw.decode('ascii').splitlines():
        fields = row.split('\t')
        need(len(fields) == 2 and bool(re.fullmatch('100644 blob [0-9a-f]{40}', fields[0])),
             'CONTROL_ENTRY_MUST_BE_REGULAR_BLOB')
        names.append(fields[1])
    need(len(names) == len(set(names)) and set(names) in ({'CONTROL.json'}, CONTROL_NAMES),
         'CONTROL_FILE_POPULATION')
    payload = {}
    for name in names:
        ref = commit + ':' + prefix + '/' + name
        size_raw = git(['--git-dir', str(cache), 'cat-file', '-s', ref])
        need(bool(re.fullmatch(b'[0-9]+\n', size_raw)) and 0 < int(size_raw) <= 65536, 'CONTROL_FILE_BYTE_BOUND')
        content = git(['--git-dir', str(cache), 'show', ref])
        need(len(content) == int(size_raw), 'CONTROL_FILE_SIZE_CHANGED')
        payload[name] = content
    return payload


def validate_control(payload, request_raw):
    request = parse(request_raw)
    control = parse(payload['CONTROL.json'])
    need(isinstance(control, dict), 'CONTROL_OBJECT_REQUIRED')
    fixed = {'schema': 'implementaudit.r5.c02-held-control.v1', 'publisher': '/root',
        'repository': REPOSITORY, 'run_id': request['run_id'], 'run_attempt': '1',
        'workflow_commit': request['workflow_commit'], 'request_sha256': sha(request_raw),
        'preparation_sha256': request['preparation_sha256'], 'input_manifest_sha256': request['input_manifest_sha256'],
        'code_bundle_sha256': BUNDLE_SHA, 'held_adapter_seal_sha256': request['held_adapter_seal_sha256']}
    need(set(control) == set(fixed) | {'decision', 'files'}
         and all(control.get(k) == v for k, v in fixed.items()), 'CONTROL_BINDING_MISMATCH')
    need(control['decision'] in ('GO', 'STOP'), 'CONTROL_DECISION')
    if control['decision'] == 'STOP':
        need(set(payload) == {'CONTROL.json'} and control['files'] == {}, 'STOP_CONTROL_POPULATION')
        return 'STOP', None
    need(set(payload) == CONTROL_NAMES and isinstance(control['files'], dict)
         and set(control['files']) == {REVIEW_NAME, GO_NAME}, 'GO_CONTROL_POPULATION')
    for name in (REVIEW_NAME, GO_NAME):
        need(control['files'][name] == {'sha256': sha(payload[name]), 'bytes': len(payload[name])},
             'CONTROL_AUTHORIZATION_PIN')
    review, go = parse(payload[REVIEW_NAME]), parse(payload[GO_NAME])
    review_fixed = {'schema': 'implementaudit.r5.c02-native-tail-independent-review.v1',
        'decision': 'PASS', 'blocking_findings': [], 'preparation_sha256': request['preparation_sha256'],
        'host_request_sha256': sha(request_raw)}
    need(isinstance(review, dict) and all(review.get(k) == v for k, v in review_fixed.items())
         and isinstance(review.get('reviewer'), str) and review['reviewer'].startswith('/root/')
         and review['reviewer'] not in ('/root/r5_c02_successor_prepare', '/root/h0_c02_or') and review['reviewer'] == '/root/c02_cold_review',
         'INDEPENDENT_REVIEW_SCOPE')
    go_fixed = {'schema': 'implementaudit.r5.c02-native-tail-root-go.v1', 'author': '/root', 'decision': 'GO',
        'subject': SUBJECT, 'controller': CONTROLLER, 'owned_binary': BINARY,
        'preparation_sha256': request['preparation_sha256'], 'source_commit': SOURCE_COMMIT,
        'source_tree': SOURCE_TREE, 'one_shot': True, 'allocation_authorized': AUTH_ALLOCATIONS,
        'independent_review_sha256': sha(payload[REVIEW_NAME]), 'host_request_sha256': sha(request_raw),
        'isolated_fixture_git_commit_authorized': True}
    need(isinstance(go, dict) and all(go.get(k) == v for k, v in go_fixed.items())
         and go.get('one_shot') is True and go.get('isolated_fixture_git_commit_authorized') is True,
         'ROOT_GO_SCOPE')
    return 'GO', sha(payload[GO_NAME])


def verify_held(work, state, request):
    need(time.monotonic_ns() < state['deadline_monotonic_ns'], 'HOLD_EXPIRED_NO_DISPATCH')
    adapter_sha, code_ids = code_pins(work)
    prep_sha, manifest_sha, prep_ids = prepared_pins(work)
    need(adapter_sha == request['held_adapter_seal_sha256'] and prep_sha == request['preparation_sha256']
         and manifest_sha == request['input_manifest_sha256'], 'HELD_SEAL_CHANGED')
    observed = dict(code_ids, **prep_ids)
    observed[str(work / 'HOST_REQUEST.json')] = regular(work / 'HOST_REQUEST.json')[1]
    need(observed == state['identities'], 'HELD_FILE_IDENTITY_CHANGED')
    public = work / 'public-preparation'
    need(set(p.name for p in public.iterdir()) == PREPARED_NAMES | {'SEALED_PREPARATION.json', 'HOST_REQUEST.json'},
         'PUBLIC_PACKET_CHANGED')
    for name in sorted(PREPARED_NAMES | {'SEALED_PREPARATION.json', 'HOST_REQUEST.json'}):
        origin = work / name if name == 'HOST_REQUEST.json' else work / 'dg18-c02-iso' / name
        need(regular(public / name)[0] == regular(origin)[0], 'PUBLIC_PACKET_DIFFERS_FROM_HELD_INPUT')
    request_raw, _ = regular(work / 'HOST_REQUEST.json')
    need(sha(request_raw) == state['request_sha256'] and parse(request_raw) == request,
         'HELD_REQUEST_CHANGED')
    original = state.get('input_custody')
    need(type(original) is dict and type(request.get('input_custody_sha256')) is str
         and re.fullmatch('[0-9a-f]{64}', request['input_custody_sha256'])
         and request.get('input_custody_count') == 92
         and sha(encode(original)) == request['input_custody_sha256'], 'HELD_INPUT_CUSTODY_BINDING')
    need(input_custody(work, manifest_sha, state['deadline_monotonic_ns']) == original,
         'HELD_INPUT_CUSTODY_CHANGED')
    need(time.monotonic_ns() < state['deadline_monotonic_ns'], 'HOLD_EXPIRED_NO_DISPATCH')


def execute_once(work, payload, go_sha, control_commit, state, request):
    # This function has no invocation until validate_control, whole-file custody,
    # the second pure preparation check, deadline and control-head checks succeed.
    verify_held(work, state, request)  # Final unchanged input census before exclusive reservation.
    write_new(work / 'DISPATCH_RESERVED.json', encode({'one_shot': True, 'control_commit': control_commit,
              'root_go_sha256': go_sha, 'automatic_retry': False}), 0o400)
    packet = work / 'dg18-c02-iso'
    write_new(packet / REVIEW_NAME, payload[REVIEW_NAME], 0o644)
    write_new(packet / GO_NAME, payload[GO_NAME], 0o644)
    command = ['/usr/bin/python3', '-I', '-B', str(packet / 'c02_native_tail.py'),
               '--execute', '--go-sha256', go_sha]
    with (work / 'native-driver.stdout').open('xb') as out, (work / 'native-driver.stderr').open('xb') as err:
        proc = subprocess.Popen(command, env=CLEAN_ENV, stdin=subprocess.DEVNULL, stdout=out,
                                stderr=err, start_new_session=True)
        write_new(work / 'DISPATCH_STARTED.json', encode({'pid': proc.pid, 'root_go_sha256': go_sha}), 0o400)
        try:
            returncode = proc.wait(timeout=DRIVER_SECONDS)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            # SIGINT lets the original driver enter its own bounded finally.
            # A forced kill never asserts that its separately owned native group
            # has been cleaned up; the disposable runner must then be torn down.
            os.killpg(proc.pid, signal.SIGINT)
            try:
                proc.wait(timeout=INTERRUPT_GRACE_SECONDS)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=10)
            raise Refusal('DRIVER_OUTER_INTERRUPTION_NO_RETRY')
    write_new(work / 'DISPATCH_FINISHED.json', encode({'returncode': returncode,
              'control_commit': control_commit, 'automatic_retry': False}), 0o400)
    need(returncode == 0, 'DRIVER_FAILED_PRESERVED_NO_RETRY')
    return 0


def hold(work):
    request_raw, _ = regular(work / 'HOST_REQUEST.json')
    state = parse(regular(work / 'HOST_STATE.json')[0])
    request = parse(request_raw)
    need(state.get('schema') == 'implementaudit.r5.c02-held-private-state.v1'
         and state['request_sha256'] == sha(request_raw), 'HELD_REQUEST_CHANGED')
    need(request['run_attempt'] == '1', 'FIRST_RUN_ATTEMPT_ONLY')
    verify_held(work, state, request)
    git(['init', '--bare', '--quiet', str(work / 'control-cache.git')])
    seen = set()
    next_notice = 0
    while time.monotonic_ns() < state['deadline_monotonic_ns']:
        commit = current_control_head()
        if commit is not None and commit not in seen:
            payload = read_control_commit(work, commit, request['control_path'])
            seen.add(commit)
            if payload is not None:
                decision, go_sha = validate_control(payload, request_raw)
                need(decision == 'GO', 'ROOT_STOP_NO_DISPATCH')
                verify_held(work, state, request)
                private_command(['/usr/bin/python3', '-I', '-B', str(work / 'dg18-c02-iso/c02_native_tail.py'),
                    '--prepare-check'], work, 'predispatch_check', 120)
                verify_held(work, state, request)
                need(current_control_head() == commit, 'CONTROL_BRANCH_MOVED_NO_DISPATCH')
                return execute_once(work, payload, go_sha, commit, state, request)
        if time.monotonic() >= next_notice:
            print('{"status":"WAITING_FOR_ACTUAL_REVIEW_AND_ROOT_GO","execution_authorized":false}', flush=True)
            next_notice = time.monotonic() + 120
        remaining = (state['deadline_monotonic_ns'] - time.monotonic_ns()) / 1000000000
        if remaining > 0:
            time.sleep(min(POLL_SECONDS, remaining))
    raise Refusal('HOLD_EXPIRED_NO_DISPATCH')


def public_summary(work):
    output = work / 'public-result'
    output.mkdir(mode=0o700)
    record = {'schema': 'implementaudit.r5.c02-held-public-result.v1', 'authority': 'OBSERVATION_ONLY',
        'original_acceptance': False, 'authentic_OR': False, 'child_JOIN': False, 'closure': False,
        'automatic_retry': False, 'raw_evidence_published': False,
        'dispatch_reserved': (work / 'DISPATCH_RESERVED.json').is_file(),
        'dispatch_started': (work / 'DISPATCH_STARTED.json').is_file(),
        'native_result': {'status': 'NOT_OBSERVED'}}
    try:
        request_raw, request_id = regular(work / 'HOST_REQUEST.json')
        request = parse(request_raw)
        need(type(request) is dict and type(request.get('preparation_sha256')) is str
             and re.fullmatch('[0-9a-f]{64}', request['preparation_sha256']),
             'PUBLIC_REQUEST_BINDING_REFUSED')
        # Only attribute a preparation when its original private held binding is
        # available. Missing/malformed/replaced state or request is omitted.
        state_raw, state_id = regular(work / 'HOST_STATE.json')
        state = parse(state_raw)
        need(type(state) is dict and state.get('schema') == 'implementaudit.r5.c02-held-private-state.v1'
             and state.get('request_sha256') == sha(request_raw)
             and type(state.get('identities')) is dict
             and state['identities'].get(str(work / 'HOST_REQUEST.json')) == request_id
             and state_id[3] == os.getuid() and stat.S_IMODE(state_id[2]) == 0o400,
             'PUBLIC_REQUEST_BINDING_REFUSED')
        record.update(request_sha256=sha(request_raw), preparation_sha256=request['preparation_sha256'])
    except (OSError, Refusal, KeyError, ValueError, TypeError):
        pass
    result = work / 'dg18-c02-iso/operation/RESULT.json'
    try:
        # Only the already sealed, separately tested C02-06 allowlist formatter
        # handles raw evidence. No arbitrary error or native output is forwarded.
        code_pins(work)
        formatter = work / 'worker' / BUNDLE_RELATIVE / 'summarize_public.py'
        spec = importlib.util.spec_from_file_location('c02_public_formatter', formatter)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        try:
            record['native_result'] = module.summarize(regular(result)[0])
        except (OSError, Refusal, KeyError, ValueError, RuntimeError, TypeError):
            # A fully written atomic diagnostic remains useful when RESULT was
            # never written or was interrupted. It never acquires result PASS.
            checkpoint = work / 'dg18-c02-iso/operation/DIAGNOSTICS.json'
            record['native_result'] = module.summarize_checkpoint(regular(checkpoint, 2048)[0])
    except (OSError, Refusal, KeyError, ValueError, RuntimeError, TypeError):
        record['native_result'] = {'status': 'NOT_AVAILABLE_OR_UNREADABLE_NO_CLAIM'}
    for name, key in (('ADAPTER_REFUSAL.json', 'adapter_refusal'), ('DISPATCH_FINISHED.json', 'dispatch_finished')):
        try:
            data = parse(regular(work / name, 8192)[0])
            if type(data) is not dict:
                continue
            if key == 'adapter_refusal':
                # This file is written exclusively from fixed-code exceptions below.
                code = data.get('reason_code')
                if type(code) is str and code in PUBLIC_REASON_CODES:
                    record[key] = code
            elif type(data.get('returncode')) is int and -255 <= data['returncode'] <= 255:
                record[key] = {'returncode': data['returncode'], 'automatic_retry': False}
        except (OSError, Refusal, KeyError, ValueError, TypeError):
            pass
    public_raw = encode(record)
    need(len(public_raw) <= PUBLIC_RESULT_BYTES, 'PUBLIC_SUMMARY_BYTE_BOUND')
    write_new(output / 'PUBLIC_RESULT.json', public_raw, 0o644)
    print('{"status":"PUBLIC_ALLOWLIST_SUMMARY_WRITTEN","raw_evidence_published":false}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'hold', 'public-summary'))
    parser.add_argument('--work', required=True)
    parser.add_argument('--run-id')
    parser.add_argument('--run-attempt')
    parser.add_argument('--workflow-commit')
    args = parser.parse_args()
    work = Path(args.work)
    need(work.is_absolute() and work.resolve(strict=True) == work and work.name == 'dg18-isolated-c02',
         'WORK_DIRECTORY')
    need(work.is_dir() and work.stat().st_uid == os.getuid()
         and stat.S_IMODE(work.stat().st_mode) == 0o700, 'PRIVATE_WORK_DIRECTORY_REQUIRED')
    if args.mode == 'prepare':
        prepare(work, args.run_id, args.run_attempt, args.workflow_commit)
    elif args.mode == 'hold':
        return hold(work)
    else:
        public_summary(work)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Refusal as exc:
        # Refusal codes are authored literals or a fixed private-command label.
        code = str(exc)
        try:
            index = sys.argv.index('--work')
            path = Path(sys.argv[index + 1]) / 'ADAPTER_REFUSAL.json'
            write_new(path, encode({'reason_code': code}), 0o400)
        except (ValueError, IndexError, OSError):
            pass
        print(json.dumps({'status': 'REFUSED_NO_RETRY', 'reason_code': code,
                          'original_acceptance': False}), flush=True)
        raise SystemExit(2)
    except Exception:
        print('{"status":"REFUSED_NO_RETRY","reason_code":"UNEXPECTED_ORCHESTRATION_FAILURE","original_acceptance":false}', flush=True)
        raise SystemExit(2)
