#!/usr/bin/env python3
"""DG17 StageA: one non-root fixed package GET; no package/ELF execution."""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import signal
import ssl
import stat
import sys
import time
import types
import urllib.error
import urllib.request

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg17-isolated-episode-01-20261106'
OPERATION = 'ONE_PINNED_UBUNTU_BWRAP_DEB_DATA_ACQUISITION'
FILENAME = 'bubblewrap_0.9.0-1ubuntu0.3_amd64.deb'
URL = 'https://archive.ubuntu.com/ubuntu/pool/main/b/bubblewrap/' + FILENAME
PACKAGE_BYTES = 50436
PACKAGE_SHA = '2461f1beee9cb04c8942739fe1a2b37e7b7c2a3d518f0779dc75f9245baa3094'
UTILITY_SHA = '429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'
PRODUCTION_FILES = frozenset(('acquire.py', 'host_utility.py', 'PUBLIC_SCHEMAS.json', 'INPUTS.json'))
BASE_CAPTURE = frozenset(('name', 'process_started', 'returncode', 'timeout',
    'output_bound_exceeded', 'pidfd_acquired', 'internal_failure', 'reason_code',
    'stream_digest_scope', 'streams_complete', 'stdout_bytes', 'stderr_bytes',
    'stdout_sha256', 'stderr_sha256', 'cleanup'))
CLEANUP_FIELDS = frozenset(('echild', 'pidfd_signals', 'retained_status_count',
    'retained_statuses_sha256', 'reaped_statuses', 'reaped_statuses_truncated'))
SUCCESS = 'RAW_PACKAGE_BYTES_RECEIVED_INNER_UNRECEIVED'
FAILED = 'FAILED_OR_UNRECEIVED'
PHASES = ('INPUT_BEFORE', 'HOST_ADMISSION', 'WORKER_CAPTURE', 'WORKER_RECEIVING',
          'BODY_READBACK', 'INPUT_AFTER', 'HTTP_OPEN', 'HTTP_HEADERS', 'HTTP_BODY',
          'WORKER_INPUT_AFTER', 'WORKER_RESULT_WRITE', 'PUBLIC_EXPORT')


class Refusal(RuntimeError):
    pass


def need(value, code):
    if not value:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def strict_json(raw):
    need(type(raw) is bytes and len(raw) <= 131072, 'JSON_REFUSED')
    def pairs(items):
        obj = {}
        for k, v in items:
            need(k not in obj, 'JSON_REFUSED'); obj[k] = v
        return obj
    def bad(_):
        raise Refusal('JSON_REFUSED')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=bad)
    except (UnicodeError, ValueError, RecursionError):
        raise Refusal('JSON_REFUSED') from None


def identity(info):
    return {'device': info.st_dev, 'inode': info.st_ino, 'uid': info.st_uid,
            'gid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode),
            'bytes': info.st_size, 'nlink': info.st_nlink,
            'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}


def file_bytes(path, maximum, private=False):
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid()
         and before.st_gid == os.getgid() and before.st_nlink == 1
         and not before.st_mode & 0o6022 and before.st_size <= maximum,
         'FILE_IDENTITY_REFUSED')
    if private:
        need(stat.S_IMODE(before.st_mode) == 0o600, 'PRIVATE_MODE_REFUSED')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        need(identity(os.fstat(fd)) == identity(before), 'FILE_CHANGED')
        parts = []; count = 0
        while True:
            data = os.read(fd, min(8192, maximum + 1 - count))
            if not data:
                break
            parts.append(data); count += len(data)
            need(count <= maximum, 'FILE_BOUND_REFUSED')
        need(count == before.st_size and identity(os.fstat(fd)) == identity(before)
             and identity(path.lstat()) == identity(before), 'FILE_CHANGED')
        return b''.join(parts), identity(before)
    finally:
        os.close(fd)


def save_new(path, raw):
    need(type(raw) is bytes and len(raw) <= 131072, 'FILE_BOUND_REFUSED')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        first = os.fstat(fd)
        need(stat.S_ISREG(first.st_mode) and first.st_nlink == 1
             and first.st_uid == os.getuid() and first.st_gid == os.getgid()
             and stat.S_IMODE(first.st_mode) == 0o600, 'FILE_IDENTITY_REFUSED')
        left = memoryview(raw)
        while left:
            n = os.write(fd, left); need(n > 0, 'FILE_WRITE_REFUSED'); left = left[n:]
        os.fsync(fd)
        last = os.fstat(fd)
        need((last.st_dev, last.st_ino) == (first.st_dev, first.st_ino)
             and identity(last) == identity(path.lstat()), 'FILE_CHANGED')
    finally:
        os.close(fd)
    received, _ = file_bytes(path, len(raw), True)
    need(received == raw, 'FILE_READBACK_REFUSED')


def directory(path):
    info = path.lstat()
    need(path.is_absolute() and path.resolve(strict=True) == path
         and stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid()
         and info.st_gid == os.getgid() and stat.S_IMODE(info.st_mode) == 0o700,
         'OWNED_DIRECTORY_REFUSED')


def input_snapshot(root, expected):
    need(re.fullmatch('[0-9a-f]{64}', expected or '') is not None
         and root.resolve(strict=True) == root, 'INPUT_MANIFEST_REFUSED')
    with os.scandir(root) as entries:
        names = [entry.name for entry in entries]
    need(set(names) == PRODUCTION_FILES and len(names) == len(PRODUCTION_FILES), 'INPUT_POPULATION_REFUSED')
    raw, info = file_bytes(root/'INPUTS.json', 16384)
    need(sha(raw) == expected, 'INPUT_MANIFEST_REFUSED')
    obj = strict_json(raw)
    need(type(obj) is dict and set(obj) == {'schema', 'operation', 'package', 'members'}
         and obj['schema'] == 'dg17.bwrap.data-inputs.v1' and obj['operation'] == OPERATION
         and obj['package'] == {'url': URL, 'filename': FILENAME, 'bytes': PACKAGE_BYTES, 'sha256': PACKAGE_SHA}
         and type(obj['members']) is list and len(obj['members']) == 3, 'INPUT_MANIFEST_REFUSED')
    rows = [{'path': 'INPUTS.json', 'bytes': len(raw), 'sha256': sha(raw), 'identity': info}]
    seen = set()
    for row in obj['members']:
        need(type(row) is dict and set(row) == {'path', 'bytes', 'sha256'}
             and row['path'] in PRODUCTION_FILES - {'INPUTS.json'} and row['path'] not in seen
             and type(row['bytes']) is int and 0 < row['bytes'] <= 131072
             and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']), 'INPUT_MANIFEST_REFUSED')
        seen.add(row['path']); body, ident = file_bytes(root/row['path'], 131072)
        need(len(body) == row['bytes'] and sha(body) == row['sha256'], 'INPUT_BYTES_REFUSED')
        rows.append({**row, 'identity': ident})
    need(seen == PRODUCTION_FILES - {'INPUTS.json'}, 'INPUT_POPULATION_REFUSED')
    helper = next(r for r in rows if r['path'] == 'host_utility.py')
    need(helper['bytes'] == 54556 and helper['sha256'] == UTILITY_SHA, 'UTILITY_PIN_REFUSED')
    return sorted(rows, key=lambda r: r['path'])


def load_utility(root):
    raw, _ = file_bytes(root/'host_utility.py', 60000)
    need(sha(raw) == UTILITY_SHA, 'UTILITY_PIN_REFUSED')
    module = types.ModuleType('dg17_exact_data_custody')
    module.__file__ = str(root/'host_utility.py')
    # Only the hash-pinned inherited source is compiled. Package bytes never enter this site.
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def safe_failure(exc, phase):
    inherited = ('RUN_WATCHDOG', 'PROCESS_START_REFUSED', 'PIDFD_ACQUISITION_REFUSED',
                 'CHILD_CLEANUP_UNCERTAIN', 'CAPTURE_BOUND_REFUSED')
    own = type(exc) is Refusal and re.fullmatch('[A-Z][A-Z0-9_]{0,63}', str(exc))
    code = str(exc) if own or type(exc).__name__ == 'Refusal' and str(exc) in inherited else 'OBSERVATION_REFUSED'
    allowed = ('Refusal', 'HTTPError', 'URLError', 'TimeoutError', 'OSError',
               'PermissionError', 'FileNotFoundError', 'SSLError', 'RuntimeError', 'ValueError')
    kind = type(exc).__name__
    number = getattr(exc, 'errno', None)
    return {'phase': phase, 'code': code, 'exception_type': kind if kind in allowed else 'OTHER',
            'errno': number if type(number) is int and 0 <= number <= 4096 else None}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Refusal('REDIRECT_REFUSED')


def response_admission(response):
    need(response.geturl() == URL and type(response.status) is int
         and response.status == 200, 'HTTP_STATUS_REFUSED')
    lengths = response.headers.get_all('Content-Length', [])
    need(len(lengths) <= 1 and (not lengths or
         re.fullmatch('[0-9]{1,10}', lengths[0]) and int(lengths[0]) == PACKAGE_BYTES),
         'HTTP_LENGTH_REFUSED')


def consume_body(response, write, deadline, expected_bytes, expected_sha, clock=time.monotonic):
    count = 0; hashed = hashlib.sha256()
    while True:
        need(clock() < deadline, 'TRANSFER_DEADLINE_REFUSED')
        chunk = response.read(min(8192, expected_bytes + 1 - count))
        need(type(chunk) is bytes, 'HTTP_BODY_REFUSED')
        if not chunk:
            break
        count += len(chunk)
        need(count <= expected_bytes, 'HTTP_BODY_SIZE_REFUSED')
        write(chunk); hashed.update(chunk)
    digest = hashed.hexdigest()
    need(count == expected_bytes, 'HTTP_BODY_SIZE_REFUSED')
    need(digest == expected_sha, 'PACKAGE_HASH_REFUSED')
    return {'bytes': count, 'sha256': digest}


def worker(root, output):
    directory(output); directory(output/'private'); directory(output/'home'); directory(output/'tmp')
    raw, _ = file_bytes(output/'private/WORKER_INPUT.json', 16384, True); admission = strict_json(raw)
    need(type(admission) is dict and set(admission) == {'manifest_sha256', 'input_snapshot_sha256'}
         and all(type(x) is str and re.fullmatch('[0-9a-f]{64}', x) for x in admission.values()), 'WORKER_INPUT_REFUSED')
    result = {'schema': 'dg17.bwrap.data-worker.v1', 'status': FAILED,
              'request_started': False, 'response_status': None, 'complete': False,
              'bytes': None, 'sha256': None, 'input_before_sha256': None,
              'input_after_sha256': None, 'failure': None}
    phase = 'INPUT_BEFORE'
    try:
        need(os.getuid() == os.geteuid() and os.getgid() == os.getegid()
             and os.geteuid() != 0 and os.getegid() != 0, 'NONROOT_REQUIRED')
        before = input_snapshot(root, admission['manifest_sha256'])
        result['input_before_sha256'] = sha(encoded(before))
        need(result['input_before_sha256'] == admission['input_snapshot_sha256'], 'INPUT_CHANGED')
        context = ssl.create_default_context()
        need(context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED, 'TLS_PROFILE_REFUSED')
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect(),
                                            urllib.request.HTTPSHandler(context=context))
        request = urllib.request.Request(URL, headers={'Accept': 'application/vnd.debian.binary-package',
                  'Accept-Encoding': 'identity'}, method='GET')
        deadline = time.monotonic() + 30
        phase = 'HTTP_OPEN'; result['request_started'] = True
        with opener.open(request, timeout=10) as response:
            phase = 'HTTP_HEADERS'
            if type(response.status) is int and 100 <= response.status <= 599:
                result['response_status'] = response.status
            response_admission(response)
            fd = os.open(output/'private/package.part', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
            try:
                initial = os.fstat(fd)
                need(stat.S_ISREG(initial.st_mode) and initial.st_nlink == 1
                     and initial.st_uid == os.getuid() and initial.st_gid == os.getgid()
                     and stat.S_IMODE(initial.st_mode) == 0o600, 'FILE_IDENTITY_REFUSED')
                def write(chunk):
                    left = memoryview(chunk)
                    while left:
                        n = os.write(fd, left); need(n > 0, 'FILE_WRITE_REFUSED'); left = left[n:]
                phase = 'HTTP_BODY'
                observed = consume_body(response, write, deadline, PACKAGE_BYTES, PACKAGE_SHA)
                os.fsync(fd)
                after = os.fstat(fd)
                need(after.st_dev == initial.st_dev and after.st_ino == initial.st_ino
                     and after.st_size == PACKAGE_BYTES and after.st_nlink == 1
                     and after.st_uid == initial.st_uid and after.st_gid == initial.st_gid
                     and stat.S_IMODE(after.st_mode) == 0o600, 'FILE_CHANGED')
            finally:
                os.close(fd)
        phase = 'BODY_READBACK'
        body, _ = file_bytes(output/'private/package.part', PACKAGE_BYTES, True)
        need(len(body) == PACKAGE_BYTES and sha(body) == PACKAGE_SHA, 'PACKAGE_HASH_REFUSED')
        result.update(observed)
        phase = 'WORKER_INPUT_AFTER'
        result['input_after_sha256'] = sha(encoded(input_snapshot(root, admission['manifest_sha256'])))
        need(result['input_after_sha256'] == result['input_before_sha256'], 'INPUT_CHANGED')
        result['status'] = SUCCESS; result['complete'] = True
    except BaseException as exc:
        if type(exc) is urllib.error.HTTPError and type(exc.code) is int and 100 <= exc.code <= 599:
            result['response_status'] = exc.code
        result['failure'] = safe_failure(exc, phase)
    raw = encoded(result); need(len(raw) <= 4096, 'WORKER_RESULT_BOUND')
    try:
        save_new(output/'private/WORKER_RESULT.json', raw)
    except BaseException as exc:
        if result['failure'] is None:
            result['failure'] = safe_failure(exc, 'WORKER_RESULT_WRITE')
        result['status'] = FAILED; result['complete'] = False; raw = encoded(result)
    sys.stdout.buffer.write(raw); sys.stdout.buffer.flush()
    return 0 if result['status'] == SUCCESS else 1


def cleanup_complete(clean):
    if type(clean) is not dict or set(clean) != CLEANUP_FIELDS:
        return False
    count = clean['retained_status_count']; rows = clean['reaped_statuses']
    if not (clean['echild'] is True and type(clean['pidfd_signals']) is int
            and 0 <= clean['pidfd_signals'] <= 4096
            and type(count) is int and 0 <= count <= 4096
            and type(clean['retained_statuses_sha256']) is str
            and re.fullmatch('[0-9a-f]{64}', clean['retained_statuses_sha256']) is not None
            and type(rows) is list and len(rows) == min(count, 8)
            and clean['reaped_statuses_truncated'] is (count > 8)):
        return False
    if not all(type(row) is dict and set(row) == {'pid', 'returncode'}
               and type(row['pid']) is int and 1 <= row['pid'] <= 2147483647
               and type(row['returncode']) is int and -255 <= row['returncode'] <= 255
               for row in rows):
        return False
    # The inherited owner hashes canonical JSON with a final LF. Beyond eight,
    # the private owner retains the count/hash but exports only its first eight.
    retained = (json.dumps(rows, sort_keys=True, indent=2, ensure_ascii=True,
                           allow_nan=False)+'\n').encode('ascii')
    return count > 8 or clean['retained_statuses_sha256'] == sha(retained)


def capture_complete(row, stdout, stderr):
    if type(row) is not dict or set(row) != BASE_CAPTURE:
        return False
    return (row['name'] == 'official-package-acquisition' and row['process_started'] is True
        and type(row['returncode']) is int and -255 <= row['returncode'] <= 255
        and row['streams_complete'] is True and row['timeout'] is False
        and row['output_bound_exceeded'] is False and row['pidfd_acquired'] is True
        and row['internal_failure'] is None and type(row['reason_code']) is str
        and re.fullmatch('[A-Z][A-Z0-9_]{0,63}', row['reason_code']) is not None
        and row['stream_digest_scope'] == 'CAPTURED_BYTES_ONLY'
        and type(row['stdout_bytes']) is int and row['stdout_bytes'] == len(stdout)
        and type(row['stderr_bytes']) is int and row['stderr_bytes'] == len(stderr)
        and row['stdout_sha256'] == sha(stdout) and row['stderr_sha256'] == sha(stderr)
        and cleanup_complete(row['cleanup']))


def start_failure_received(row):
    return (type(row) is dict and set(row) == {'name', 'process_started', 'returncode', 'start_errno', 'reason_code'}
        and row['name'] == 'official-package-acquisition' and row['process_started'] is False
        and row['returncode'] is None
        and (row['start_errno'] is None or type(row['start_errno']) is int and 0 <= row['start_errno'] <= 4096)
        and row['reason_code'] in ('START_FILE_MISSING', 'START_PERMISSION_REFUSED', 'START_FORMAT_REFUSED', 'START_OS_REFUSED'))


def request_projection(worker_obj, worker_observed, capture_invoked, start_failed):
    observed = worker_observed is True and type(worker_obj) is dict
    return {'url_sha256': sha(URL.encode()), 'observation_received': observed,
            'started': observed and worker_obj['request_started'] is True,
            'unstarted_proven': not capture_invoked or start_failed is True
                or observed and worker_obj['request_started'] is False,
            'status': worker_obj['response_status'] if observed else None,
            'complete': observed and worker_obj['complete'] is True, 'redirects_followed': 0}


def failure_valid(obj):
    return (type(obj) is dict and set(obj) == {'phase', 'code', 'exception_type', 'errno'}
        and obj['phase'] in PHASES and type(obj['code']) is str
        and re.fullmatch('[A-Z][A-Z0-9_]{0,63}', obj['code']) is not None
        and obj['exception_type'] in ('Refusal', 'HTTPError', 'URLError', 'TimeoutError', 'OSError',
            'PermissionError', 'FileNotFoundError', 'SSLError', 'RuntimeError', 'ValueError', 'OTHER')
        and (obj['errno'] is None or type(obj['errno']) is int and 0 <= obj['errno'] <= 4096))


def worker_shape(obj):
    keys = {'schema', 'status', 'request_started', 'response_status', 'complete', 'bytes',
            'sha256', 'input_before_sha256', 'input_after_sha256', 'failure'}
    if not (type(obj) is dict and set(obj) == keys and obj['schema'] == 'dg17.bwrap.data-worker.v1'
            and obj['status'] in (SUCCESS, FAILED) and type(obj['request_started']) is bool
            and (obj['response_status'] is None or type(obj['response_status']) is int and 100 <= obj['response_status'] <= 599)
            and type(obj['complete']) is bool
            and (obj['bytes'] is None or type(obj['bytes']) is int and 0 <= obj['bytes'] <= PACKAGE_BYTES)
            and all(obj[key] is None or type(obj[key]) is str and re.fullmatch('[0-9a-f]{64}', obj[key])
                    for key in ('sha256', 'input_before_sha256', 'input_after_sha256'))):
        return False
    if obj['status'] == FAILED:
        return obj['complete'] is False and failure_valid(obj['failure'])
    return obj['failure'] is None


def worker_received(obj, snapshot_sha):
    keys = {'schema', 'status', 'request_started', 'response_status', 'complete', 'bytes',
            'sha256', 'input_before_sha256', 'input_after_sha256', 'failure'}
    return (type(obj) is dict and set(obj) == keys and obj['schema'] == 'dg17.bwrap.data-worker.v1'
            and obj['status'] == SUCCESS and obj['request_started'] is True
            and type(obj['response_status']) is int and obj['response_status'] == 200
            and obj['complete'] is True and type(obj['bytes']) is int and obj['bytes'] == PACKAGE_BYTES
            and obj['sha256'] == PACKAGE_SHA and obj['failure'] is None
            and obj['input_before_sha256'] == obj['input_after_sha256'] == snapshot_sha)


def schema_valid(value, node):
    if 'anyOf' in node:
        return set(node) == {'anyOf'} and any(schema_valid(value, x) for x in node['anyOf'])
    if 'const' in node and (type(value) is not type(node['const']) or value != node['const']): return False
    if 'enum' in node and not any(type(value) is type(v) and value == v for v in node['enum']): return False
    typ = node.get('type')
    mapping = {'object': dict, 'array': list, 'integer': int, 'string': str, 'boolean': bool, 'null': type(None)}
    if typ and type(value) is not mapping[typ]: return False
    if typ == 'object':
        props = node.get('properties', {})
        if not set(node.get('required', [])) <= set(value): return False
        if node.get('additionalProperties') is False and not set(value) <= set(props): return False
        return all(k not in props or schema_valid(v, props[k]) for k, v in value.items())
    if typ == 'array': return len(value) <= node.get('maxItems', len(value)) and all(schema_valid(v, node['items']) for v in value)
    if typ == 'integer': return node.get('minimum', value) <= value <= node.get('maximum', value)
    if typ == 'string' and 'pattern' in node: return re.fullmatch(node['pattern'], value) is not None
    return True


def publication_chain(path):
    rows = []
    for item in (path, *path.parents):
        info = item.lstat()
        need(stat.S_ISDIR(info.st_mode) and info.st_uid in (0, os.getuid())
             and not info.st_mode & 0o022, 'PUBLICATION_PARENT_REFUSED')
        rows.append({'device': info.st_dev, 'inode': info.st_ino, 'uid': info.st_uid,
                     'gid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode)})
    return rows


def publication_file(info):
    need(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid()
         and info.st_gid == os.getgid() and info.st_nlink == 1
         and stat.S_IMODE(info.st_mode) in (0o600, 0o644) and info.st_size == 0,
         'PUBLICATION_FILE_REFUSED')
    return identity(info)


def admit_publication_sink(env):
    path = Path(env.get('GITHUB_OUTPUT', ''))
    expected_parent = Path(env['RUNNER_TEMP'])/'_runner_file_commands'
    need(path.is_absolute() and path.parent == expected_parent
         and path.resolve(strict=True) == path
         and re.fullmatch(r'set_output_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', path.name),
         'PUBLICATION_PATH_REFUSED')
    chain = publication_chain(path.parent)
    before = publication_file(path.lstat())
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        need(publication_file(os.fstat(fd)) == before == publication_file(path.lstat()),
             'PUBLICATION_FILE_CHANGED')
    except BaseException:
        os.close(fd)
        raise
    return fd, path, before, chain


def commit_publication(sink, status):
    # All public files have already passed complete closed readback. Only this
    # current step's previously admitted, still-empty platform file can signal.
    fd, path, before, chain = sink
    need(type(status) is int and status in (0, 1), 'PUBLICATION_STATUS_REFUSED')
    need(publication_chain(path.parent) == chain
         and publication_file(os.fstat(fd)) == before == publication_file(path.lstat()),
         'PUBLICATION_FILE_CHANGED')
    signal.setitimer(signal.ITIMER_REAL, 0)
    written = os.write(fd, b'publication_ready=true\n')
    # Publication eligibility commits before this fixed write. No later I/O or
    # assertions pretend to retract it. Process exit closes the held descriptor.
    os._exit(status if written == len(b'publication_ready=true\n') else 1)


def parent(root, output):
    env = os.environ
    need(env.get('GITHUB_ACTIONS') == 'true' and env.get('RUNNER_ENVIRONMENT') == 'github-hosted'
         and env.get('GITHUB_REPOSITORY') == REPOSITORY and env.get('GITHUB_EVENT_NAME') == 'push'
         and env.get('GITHUB_REF') == 'refs/heads/'+BRANCH and env.get('GITHUB_RUN_ATTEMPT') == '1', 'HOSTED_EVENT_REQUIRED')
    run = env.get('GITHUB_RUN_ID', ''); commit = env.get('GITHUB_SHA', '')
    need(re.fullmatch('[0-9]{1,20}', run) and re.fullmatch('[0-9a-f]{40}', commit), 'HOSTED_IDENTITY_REFUSED')
    need(os.geteuid() == os.getuid() != 0 and os.getegid() == os.getgid() != 0
         and platform.system() == 'Linux' and platform.machine() == 'x86_64'
         and sys.version_info[:2] == (3, 12), 'HOST_PROFILE_REFUSED')
    need(output == Path(env['RUNNER_TEMP'])/('dg17-bwrap-data-'+run+'-a1')
         and output.is_absolute() and output.parent.resolve(strict=True) == output.parent
         and not root.is_relative_to(output), 'OUTPUT_PATH_REFUSED')
    publication_sink = admit_publication_sink(env)
    os.umask(0o077); output.mkdir(mode=0o700)
    for name in ('private', 'public', 'home', 'tmp'): (output/name).mkdir(mode=0o700)
    directory(output)
    context = {'repository': REPOSITORY, 'branch': BRANCH, 'run_id': run, 'attempt': 1, 'workflow_commit': commit}
    expected = env.get('DG17_DATA_INPUTS_SHA256', '')
    failure = None; phase = 'INPUT_BEFORE'; records = []; stdout = b''; stderr = b''
    before = after = None; schemas = None; worker_obj = None; body = None; u = None; observed = None
    record = None; capture_ok = False; capture_success = False; quiescent = False; private_streams = False
    private_record = None; retention_failure = False; worker_observed = False; tools_before = tools_after = None
    capture_invoked = False
    before_retained = after_retained = False
    started = time.monotonic()
    try:
        before = input_snapshot(root, expected)
        schema_raw, _ = file_bytes(root/'PUBLIC_SCHEMAS.json', 131072); schemas = strict_json(schema_raw)
        save_new(output/'private/INPUT_BEFORE.json', encoded(before)); before_retained = True
        u = load_utility(root)
        phase = 'HOST_ADMISSION'
        tool, python_fact = u.trusted('python3'); env_tool, env_fact = u.trusted('env')
        need(tool is not None and re.fullmatch(r'/usr/bin/python3(?:\.12)?', tool), 'PYTHON_TOOL_REFUSED')
        need(Path(sys.executable).resolve(strict=True) == Path(tool)
             and env_tool == '/usr/bin/env', 'CONTROL_TOOL_REFUSED')
        tools_before = {'python': python_fact, 'env': env_fact}
        save_new(output/'private/TOOLS_BEFORE.json', encoded(tools_before))
        libc = ctypes.CDLL(None, use_errno=True)
        need(libc.prctl(36, 1, 0, 0, 0) == 0, 'SUBREAPER_REFUSED')
        need(not u.children(), 'INITIAL_CHILDREN_REFUSED')
        try: os.waitpid(-1, os.WNOHANG); raise Refusal('INITIAL_CHILDREN_REFUSED')
        except ChildProcessError: pass
        save_new(output/'private/WORKER_INPUT.json', encoded({'manifest_sha256': expected, 'input_snapshot_sha256': sha(encoded(before))}))
        need(input_snapshot(root, expected) == before, 'INPUT_CHANGED')
        phase = 'WORKER_CAPTURE'
        argv = ['/usr/bin/env', 'HOME='+str(output/'home'), 'TMPDIR='+str(output/'tmp'),
                '/usr/bin/python3', '-I', '-S', '-B', str(root/'acquire.py'), '--worker', '--output', str(output)]
        try:
            capture_invoked = True
            rc, stdout, stderr = u.capture('official-package-acquisition', argv, records,
                                           min(started+45, time.monotonic()+45), seconds=40)
        except BaseException as exc:
            failure = safe_failure(exc, phase)
            captured = getattr(exc, 'captured', None)
            if type(captured) is dict:
                stdout = captured.get('stdout', b''); stderr = captured.get('stderr', b'')
            rc = None
        finally:
            try:
                need(type(stdout) is bytes and type(stderr) is bytes and len(stdout) <= 32768 and len(stderr) <= 32768, 'CAPTURE_STREAM_REFUSED')
                save_new(output/'private/worker.stdout', stdout); save_new(output/'private/worker.stderr', stderr)
                private_streams = True
            except BaseException as exc:
                retention_failure = True
                if failure is None: failure = safe_failure(exc, phase)
            try:
                raw_record = encoded(records)
                save_new(output/'private/CAPTURE.json', raw_record); private_record = raw_record
            except BaseException as exc:
                retention_failure = True
                if failure is None: failure = safe_failure(exc, phase)
        need(failure is None, 'CAPTURE_REFUSED')
        need(len(records) == 1, 'CAPTURE_POPULATION_REFUSED'); record = records[0]
        capture_ok = capture_complete(record, stdout, stderr)
        capture_success = capture_ok and record['returncode'] == 0 and rc == 0
        need(capture_ok and rc == record['returncode'], 'CAPTURE_INCOMPLETE')
        phase = 'WORKER_RECEIVING'
        private_result, _ = file_bytes(output/'private/WORKER_RESULT.json', 4096, True)
        need(private_result == stdout, 'WORKER_RESULT_BINDING_REFUSED')
        parsed = strict_json(stdout); need(worker_shape(parsed), 'WORKER_RESULT_SHAPE_REFUSED')
        worker_obj = parsed; worker_observed = True
        if worker_obj['status'] == FAILED:
            need(rc == 1, 'WORKER_RESULT_STATUS_REFUSED')
            failure = worker_obj['failure']
            raise Refusal('WORKER_DECLARED_FAILURE')
        need(capture_success, 'CAPTURE_NOT_SUCCESSFUL')
        need(worker_received(worker_obj, sha(encoded(before))), 'WORKER_RESULT_REFUSED')
        phase = 'BODY_READBACK'
        body, _ = file_bytes(output/'private/package.part', PACKAGE_BYTES, True)
        need(len(body) == PACKAGE_BYTES and sha(body) == PACKAGE_SHA, 'PACKAGE_HASH_REFUSED')
        observed = {'bytes': len(body), 'sha256': sha(body), 'verified': True, 'retained': True}
        phase = 'INPUT_AFTER'
        after = input_snapshot(root, expected)
        save_new(output/'private/INPUT_AFTER.json', encoded(after)); after_retained = True
        need(after == before, 'INPUT_CHANGED')
        _, python_fact = u.trusted('python3'); _, env_fact = u.trusted('env')
        tools_after = {'python': python_fact, 'env': env_fact}
        save_new(output/'private/TOOLS_AFTER.json', encoded(tools_after))
        need(tools_after == tools_before, 'CONTROL_TOOL_CHANGED')
        need(not u.children(), 'FINAL_CHILDREN_REFUSED')
        try: os.waitpid(-1, os.WNOHANG); raise Refusal('FINAL_CHILDREN_REFUSED')
        except ChildProcessError: quiescent = True
        need(time.monotonic() < started+50, 'DRIVER_DEADLINE_REFUSED')
    except BaseException as exc:
        if failure is None: failure = safe_failure(exc, phase)
    # No executable operation occurs after the capture or an admission refusal.
    if records and record is None: record = records[0] if len(records) == 1 else None
    if u is not None and not quiescent:
        try:
            need(not u.children(), 'FINAL_CHILDREN_REFUSED')
            try: os.waitpid(-1, os.WNOHANG); raise Refusal('FINAL_CHILDREN_REFUSED')
            except ChildProcessError: quiescent = True
        except BaseException:
            quiescent = False
    if before is not None and after is None:
        try:
            after = input_snapshot(root, expected)
            save_new(output/'private/INPUT_AFTER.json', encoded(after)); after_retained = True
        except BaseException: pass
    bindings_ok = before is not None and after == before
    tools_unchanged = tools_before is not None and tools_before == tools_after
    good = (failure is None and capture_success and quiescent and bindings_ok and before_retained
            and after_retained and tools_unchanged and observed is not None)
    clean = record.get('cleanup', {}) if type(record) is dict else {}
    def maybe_int(value): return value if type(value) is int else None
    def maybe_digest(value): return value if type(value) is str and re.fullmatch('[0-9a-f]{64}', value) else None
    capture = {'schema': 'dg17.bwrap.data-capture.v1', 'record_count': len(records),
               'capture_invoked': capture_invoked, 'start_failure_record_received': start_failure_received(record),
               'complete_record_received': capture_ok, 'complete_success_record_received': capture_success,
               'process_started': record.get('process_started') if type(record) is dict and type(record.get('process_started')) is bool else None,
               'returncode': maybe_int(record.get('returncode')) if type(record) is dict else None,
               'streams_complete': type(record) is dict and record.get('streams_complete') is True,
               'pidfd_acquired': type(record) is dict and record.get('pidfd_acquired') is True,
               'timeout': type(record) is dict and record.get('timeout') is True,
               'output_bound_exceeded': type(record) is dict and record.get('output_bound_exceeded') is True,
               'private_streams_retained': private_streams, 'retention_failure': retention_failure,
               'private_record_retained': private_record is not None,
               'private_record_bytes': len(private_record) if private_record is not None else None,
               'private_record_sha256': sha(private_record) if private_record is not None else None,
               'stdout_bytes': len(stdout), 'stdout_sha256': sha(stdout),
               'stderr_bytes': len(stderr), 'stderr_sha256': sha(stderr),
               'cleanup_echild': clean.get('echild') is True, 'no_owned_children_and_wait_echild': quiescent,
               'pidfd_signals': maybe_int(clean.get('pidfd_signals')),
               'retained_status_count': maybe_int(clean.get('retained_status_count')),
               'retained_statuses_sha256': maybe_digest(clean.get('retained_statuses_sha256')),
               'input_bindings': {'manifest_sha256': maybe_digest(expected),
                   'before_sha256': sha(encoded(before)) if before is not None else None,
                   'after_sha256': sha(encoded(after)) if after is not None else None,
                   'before_retained': before_retained, 'after_retained': after_retained, 'unchanged': bindings_ok},
               'control_tools': {'before_sha256': sha(encoded(tools_before)) if tools_before is not None else None,
                   'after_sha256': sha(encoded(tools_after)) if tools_after is not None else None, 'unchanged': tools_unchanged}}
    result = {'schema': 'dg17.bwrap.package-data.v1', 'operation': OPERATION,
              'status': SUCCESS if good else FAILED, 'context': context,
              'expected_package': {'filename': FILENAME, 'bytes': PACKAGE_BYTES, 'sha256': PACKAGE_SHA},
              'observed_package': observed or {'bytes': None, 'sha256': None, 'verified': False, 'retained': False},
              'request': request_projection(worker_obj, worker_observed, capture_invoked, start_failure_received(record)),
              'capture': {'received': capture_ok, 'success_received': capture_success, 'record_sha256': sha(encoded(capture))},
              'cleanup': {'no_owned_children': quiescent, 'wait_echild': quiescent, 'host_teardown_observed': False},
              'failure': failure, 'inner_receiving': 'UNRECEIVED_NO_DECODE_PERFORMED',
              'authority': {key: False for key in ('package_installation', 'bwrap_executed', 'system_file_created',
                           'sysctl_or_security_policy_write', 'currentness', 'native_content', 'original_acceptance')}}
    phase = 'PUBLIC_EXPORT'
    directory(output/'public')
    need(schemas is not None and set(schemas) == {'RESULT.json', 'CAPTURE.json'}
         and schema_valid(result, schemas['RESULT.json']) and schema_valid(capture, schemas['CAPTURE.json']), 'PUBLIC_SCHEMA_REFUSED')
    docs = {'RESULT.json': encoded(result), 'CAPTURE.json': encoded(capture)}
    need(len(docs['RESULT.json']) <= 4096 and len(docs['CAPTURE.json']) <= 8192, 'PUBLIC_BOUND_REFUSED')
    if good: docs[FILENAME] = body
    manifest = {'schema': 'dg17.bwrap.data-artifact-manifest.v1', 'members': [
        {'path': name, 'bytes': len(raw), 'sha256': sha(raw)} for name, raw in sorted(docs.items())]}
    docs['ARTIFACT_MANIFEST.json'] = encoded(manifest)
    need(len(docs['ARTIFACT_MANIFEST.json']) <= 1024 and sum(len(v) for v in docs.values()) <= 65536, 'PUBLIC_BOUND_REFUSED')
    for name, raw in docs.items(): save_new(output/'public'/name, raw)
    with os.scandir(output/'public') as entries:
        names = [entry.name for entry in entries]
    need(set(names) == set(docs) and len(names) == len(docs), 'PUBLIC_POPULATION_REFUSED')
    for name, raw in docs.items():
        actual, _ = file_bytes(output/'public'/name, len(raw), True)
        need(actual == raw, 'PUBLIC_READBACK_REFUSED')
    print(json.dumps({'operation': OPERATION, 'status': result['status'], 'raw_package_exported': good}, separators=(',', ':')), flush=True)
    commit_publication(publication_sink, 0 if good else 1)


def budget_expired(_number, _frame):
    raise Refusal('DRIVER_DEADLINE_REFUSED')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', required=True); parser.add_argument('--worker', action='store_true')
    args = parser.parse_args(); root = Path(__file__).absolute().parent; output = Path(args.output).absolute()
    if args.worker:
        return worker(root, output)
    # One self-signal deadline, no watchdog child/thread and no foreign PID.
    # Successful receiving still requires the capture's actual closed custody.
    signal.signal(signal.SIGALRM, budget_expired)
    signal.setitimer(signal.ITIMER_REAL, 50)
    try:
        return parent(root, output)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BaseException as exc:
        if isinstance(exc, SystemExit): raise
        sys.stderr.write(json.dumps({'schema': 'dg17.bwrap.data-entry-failure.v1', 'status': FAILED,
                                    'failure': safe_failure(exc, 'PUBLIC_EXPORT')}, separators=(',', ':'))+'\n')
        sys.exit(1)
