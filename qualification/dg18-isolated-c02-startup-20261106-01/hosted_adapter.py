#!/usr/bin/env python3
"""One fresh, independently admitted C02 startup observation; no protected tail.

Only reviewed closed projections reach the public artifact directories. This
adapter does not initialize a product controller, send initialized, or start a
thread/model turn. The retained native guard still refuses configWarning.
"""
from pathlib import Path
import argparse
import hashlib
import importlib
import json
import os
import re
import signal
import stat
import subprocess
import sys
import tarfile
import time
import urllib.request

REPO = 'theislampill/IMPLEMENTAUDIT.md'
REMOTE = 'https://github.com/' + REPO + '.git'
BRANCH = 'pro/dg18-isolated-c02-startup-20261106-01'
CONTROL_BRANCH = 'pro/dg18-isolated-c02-startup-control-20261106-01'
PREFIX = 'qualification/dg18-isolated-c02-startup-20261106-01'
WORKFLOW = '.github/workflows/dg18-isolated-c02-startup-20261106-01.yml'
REVIEWER = '/root/c02_startup_review'
SOURCE = '35bf9823856eb4efe254b882954120480632230e'
ARCHIVE_URL = 'https://registry.npmjs.org/@openai/codex/-/codex-0.166.0-linux-x64.tgz'
ARCHIVE_SIZE = 172325449
ARCHIVE_SHA = 'cbc00a26d3d0e2ceefc4be8891f8a81ef1e349b3b175bc0ae308762bc001fd93'
BINARY_MEMBER = 'package/vendor/x86_64-unknown-linux-musl/bin/codex'
BINARY_SIZE = 319346888
BINARY_SHA = 'b8a11fedf24b2dfb59a70c9e52b030f9a508dcd49cd2dd0d41956f4c785156b8'
HOLD_SECONDS = 1200
MAX_PUBLIC = 16384
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC',
       'PYTHONDONTWRITEBYTECODE': '1', 'GIT_CONFIG_NOSYSTEM': '1',
       'GIT_CONFIG_SYSTEM': '/dev/null', 'GIT_CONFIG_GLOBAL': '/dev/null',
       'GIT_TERMINAL_PROMPT': '0', 'GIT_OPTIONAL_LOCKS': '0'}
ALLOCATIONS = ['fresh-git-fixture', 'fresh-private-home', 'owned-pinned-binary',
               'one-native-app-server', 'one-unarmed-loopback-provider',
               'configured-owned-MCP-only-if-native-startup-invokes-it',
               'one-initialize-request', 'bounded-private-capture',
               'same-host-closed-extractor', 'owned-process-cleanup']
CONTROL_NAMES = {'CONTROL.json', 'INDEPENDENT_TECHNICAL_REVIEW.json', 'ROOT_GO.json'}


class Refusal(Exception):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, 'DUPLICATE_JSON_KEY')
            out[key] = value
        return out
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refusal('NONFINITE_JSON')))


def ident(st):
    return [st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid,
            st.st_nlink, st.st_size, st.st_mtime_ns, st.st_ctime_ns]


def regular(path, limit=1048576, keep=True):
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts, 'INPUT_PATH')
    for node in (path, *path.parents):
        need(not stat.S_ISLNK(node.lstat().st_mode), 'INPUT_SYMLINK')
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= limit,
         'INPUT_REGULAR_BOUND')
    digest, total, chunks = hashlib.sha256(), 0, []
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        need(ident(before) == ident(os.fstat(stream.fileno())), 'INPUT_CHANGED')
        while True:
            block = stream.read(min(1048576, limit + 1 - total))
            if not block:
                break
            total += len(block)
            need(total <= limit, 'INPUT_SIZE')
            digest.update(block)
            if keep:
                chunks.append(block)
        need(ident(before) == ident(os.fstat(stream.fileno())) == ident(path.lstat()), 'INPUT_CHANGED')
    return b''.join(chunks), {'sha256': digest.hexdigest(), 'bytes': total, 'identity': ident(before)}


def write_new(path, raw, mode=0o600):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.chmod(path, mode)


def private_dir(path):
    need(path.is_absolute() and '..' not in path.parts, 'WORK_PATH')
    for node in (path, *path.parents):
        need(not stat.S_ISLNK(node.lstat().st_mode), 'WORK_SYMLINK')
    st = path.lstat()
    need(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid() and stat.S_IMODE(st.st_mode) == 0o700,
         'PRIVATE_DIRECTORY')


def git(args, timeout=30, missing=False):
    done = subprocess.run(['/usr/bin/git', *args], env=ENV, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=timeout)
    need(len(done.stdout) <= 1048576, 'GIT_OUTPUT_BOUND')
    if missing and done.returncode:
        return None
    need(done.returncode == 0, 'GIT_READ_OR_FIXTURE_FAILED')
    return done.stdout


def system_binding(path):
    invocation = Path(path)
    chain = []
    current = invocation
    for _ in range(8):
        st = current.lstat()
        chain.append({'path': str(current), 'identity': ident(st),
                      'link': os.readlink(current) if stat.S_ISLNK(st.st_mode) else None})
        if not stat.S_ISLNK(st.st_mode):
            break
        target = Path(os.readlink(current))
        current = Path(os.path.abspath(target if target.is_absolute() else current.parent / target))
    else:
        raise Refusal('SYSTEM_LINK_BOUND')
    need(current == invocation.resolve(strict=True), 'SYSTEM_RESOLUTION')
    _, receipt = regular(current, 134217728, keep=False)
    need(receipt['identity'][3] == 0 and not receipt['identity'][2] & 0o022, 'SYSTEM_OWNER_MODE')
    return {'invocation': path, 'chain': chain, 'resolved': str(current), **receipt}


def code_binding(work):
    worker, bundle = work / 'worker', work / 'worker' / PREFIX
    manifest_raw, manifest_id = regular(bundle / 'CODE_MANIFEST.json')
    manifest = parse(manifest_raw)
    need(set(manifest) == {'schema', 'source_scope', 'files'} and
         manifest['schema'] == 'dg18.c02.startup-code-manifest.v1' and
         manifest['source_scope'] == SOURCE, 'CODE_MANIFEST')
    names, ids = set(), {}
    for entry in manifest['files']:
        need(set(entry) == {'path', 'bytes', 'sha256', 'mode'}, 'CODE_MEMBER')
        name = entry['path']
        need(type(name) is str and not Path(name).is_absolute() and '..' not in Path(name).parts and
             (name.startswith(PREFIX + '/') or name == WORKFLOW) and name not in names,
             'CODE_MEMBER_PATH')
        names.add(name)
        raw, stamp = regular(worker / name)
        need(stamp['sha256'] == entry['sha256'] and len(raw) == entry['bytes'] and
             stat.S_IMODE(stamp['identity'][2]) == entry['mode'] == 0o644, 'CODE_PIN')
        ids[name] = stamp
    actual = {str(p.relative_to(worker)) for p in bundle.rglob('*') if not p.is_dir()}
    need(actual == (names - {WORKFLOW}) | {PREFIX + '/CODE_MANIFEST.json'}, 'CODE_POPULATION')
    need(Path(__file__).resolve(strict=True) == bundle / 'hosted_adapter.py', 'ADAPTER_LOCATION')
    return {'manifest_sha256': sha(manifest_raw), 'manifest_identity': manifest_id,
            'files': ids, 'systems': {p: system_binding(p) for p in ('/usr/bin/python3', '/usr/bin/git')}}


def download_binary(work):
    archive = work / 'codex-0.166.0-linux-x64.tgz'
    end, size, digest = time.monotonic() + 240, 0, hashlib.sha256()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(ARCHIVE_URL, timeout=30) as response, archive.open('xb') as stream:
        need(response.geturl() == ARCHIVE_URL, 'ARCHIVE_REDIRECT')
        while True:
            need(time.monotonic() < end, 'ARCHIVE_DEADLINE')
            chunk = response.read(1048576)
            if not chunk:
                break
            size += len(chunk)
            need(size <= ARCHIVE_SIZE, 'ARCHIVE_SIZE')
            digest.update(chunk)
            stream.write(chunk)
    os.chmod(archive, 0o600)
    need(size == ARCHIVE_SIZE and digest.hexdigest() == ARCHIVE_SHA, 'ARCHIVE_PIN')
    target = work / 'owned-bin' / 'codex'
    target.parent.mkdir(mode=0o700)
    found = False
    with tarfile.open(archive, 'r:gz') as tar:
        for index, member in enumerate(tar):
            need(index < 1000, 'ARCHIVE_MEMBER_BOUND')
            if member.name != BINARY_MEMBER:
                continue
            need(not found and member.isfile() and member.size == BINARY_SIZE, 'BINARY_MEMBER')
            found = True
            source = tar.extractfile(member)
            need(source is not None, 'BINARY_MEMBER')
            count, checksum = 0, hashlib.sha256()
            with target.open('xb') as out:
                while True:
                    block = source.read(1048576)
                    if not block:
                        break
                    count += len(block)
                    need(count <= BINARY_SIZE, 'BINARY_SIZE')
                    checksum.update(block)
                    out.write(block)
            need(count == BINARY_SIZE and checksum.hexdigest() == BINARY_SHA, 'BINARY_PIN')
    need(found, 'BINARY_MISSING')
    os.chmod(target, 0o700)
    return regular(target, BINARY_SIZE, keep=False)[1]


def prepare(work, run_id, attempt, commit):
    private_dir(work)
    need(re.fullmatch('[1-9][0-9]{0,23}', run_id) and attempt == '1' and
         re.fullmatch('[0-9a-f]{40}', commit), 'WORKFLOW_IDENTITY')
    bindings = code_binding(work)
    worker = work / 'worker'
    need(git(['-C', str(worker), 'rev-parse', 'HEAD']).decode().strip() == commit and
         not git(['-C', str(worker), 'status', '--porcelain=v1', '--untracked-files=no']), 'CHECKOUT_CHANGED')
    binary = download_binary(work)
    for name in ('subject', 'home', 'evidence', 'private', 'public-preparation'):
        (work / name).mkdir(mode=0o700)
    subject = work / 'subject'
    git(['-c', 'init.templateDir=', 'init', '-q', '-b', 'startup-diagnostic', '--object-format=sha1', str(subject)])
    write_new(subject / 'TASK.md', b'# Fresh C02 startup observation\n\nOne initialize request only. No product controller, canonical pair, rotation, correction, thread or model turn.\n')
    git(['-C', str(subject), 'add', '--', 'TASK.md'])
    git(['-C', str(subject), '-c', 'user.name=DG18 isolated startup', '-c',
         'user.email=dg18-startup@example.invalid', '-c', 'commit.gpgsign=false',
         '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'Define isolated startup diagnostic'])
    head = git(['-C', str(subject), 'rev-parse', 'HEAD']).decode().strip()
    request = {'schema': 'dg18.c02.startup-host-preparation.v1', 'authority': 'PREPARATION_ONLY',
        'repository': REPO, 'branch': BRANCH, 'workflow_commit': commit, 'run_id': run_id,
        'run_attempt': attempt, 'job': 'startup', 'nonce': os.urandom(32).hex(),
        'created_unix_seconds': int(time.time()), 'hold_seconds': HOLD_SECONDS,
        'source_scope': SOURCE, 'binary_sha256': BINARY_SHA, 'binary_bytes': BINARY_SIZE,
        'archive_sha256': ARCHIVE_SHA, 'archive_bytes': ARCHIVE_SIZE,
        'code_manifest_sha256': bindings['manifest_sha256'],
        'code_files': [{'path': k, 'sha256': v['sha256'], 'bytes': v['bytes']} for k,v in sorted(bindings['files'].items())],
        'systems': bindings['systems'], 'subject_head': head,
        'subject_prestate': 'FRESH_MINIMAL_GIT_FIXTURE_NO_PRODUCT_BOOTSTRAP',
        'config_constructor': 'RETAIN_ORIGINAL_VALUES_REBIND_OWNED_PATHS_AND_LOOPBACK',
        'control_branch': CONTROL_BRANCH, 'control_path': 'startup/' + run_id + '/1',
        'allocation_after_GO': ALLOCATIONS, 'execution_authorized': False,
        'original_acceptance': False, 'historical_warning_cause_resolved': False}
    raw = encode(request)
    need(len(raw) <= MAX_PUBLIC, 'PREPARATION_PUBLIC_BOUND')
    write_new(work / 'PREPARATION.json', raw)
    write_new(work / 'public-preparation' / 'PREPARATION.json', raw, 0o644)
    state = {'schema': 'dg18.c02.startup-private-state.v1', 'preparation_sha256': sha(raw),
             'deadline_monotonic_ns': time.monotonic_ns() + HOLD_SECONDS * 1000000000,
             'code': bindings, 'binary': binary, 'subject_head': head}
    write_new(work / 'PRIVATE_STATE.json', encode(state), 0o400)


def control_head():
    raw = git(['ls-remote', '--exit-code', '--refs', REMOTE, 'refs/heads/' + CONTROL_BRANCH], missing=True)
    if raw is None:
        return None
    need(re.fullmatch(rb'[0-9a-f]{40}\trefs/heads/' + CONTROL_BRANCH.encode() + rb'\n', raw), 'CONTROL_REF')
    return raw[:40].decode()


def read_control(work, commit, prefix):
    cache = work / 'control-cache.git'
    git(['--git-dir', str(cache), 'fetch', '--quiet', '--no-tags', '--depth=1', REMOTE, commit])
    raw = git(['--git-dir', str(cache), 'ls-tree', commit + ':' + prefix], missing=True)
    if raw is None:
        return None
    names = []
    for row in raw.decode('ascii').splitlines():
        fields = row.split('\t')
        need(len(fields) == 2 and re.fullmatch('100644 blob [0-9a-f]{40}', fields[0]), 'CONTROL_ENTRY')
        names.append(fields[1])
    need(len(names) == len(set(names)) and set(names) in ({'CONTROL.json'}, CONTROL_NAMES), 'CONTROL_POPULATION')
    payload = {}
    for name in names:
        ref = commit + ':' + prefix + '/' + name
        count = int(git(['--git-dir', str(cache), 'cat-file', '-s', ref]))
        need(0 < count <= 65536, 'CONTROL_SIZE')
        raw = git(['--git-dir', str(cache), 'show', ref])
        need(len(raw) == count, 'CONTROL_SIZE_CHANGED')
        payload[name] = raw
    return payload


def validate_control(payload, prep_raw):
    prep, control = parse(prep_raw), parse(payload['CONTROL.json'])
    fixed = {'schema': 'dg18.c02.startup-control.v1', 'publisher': '/root', 'repository': REPO,
             'run_id': prep['run_id'], 'run_attempt': '1', 'workflow_commit': prep['workflow_commit'],
             'preparation_sha256': sha(prep_raw), 'code_manifest_sha256': prep['code_manifest_sha256']}
    need(type(control) is dict and set(control) == set(fixed) | {'decision', 'files'} and
         all(control.get(k) == v for k,v in fixed.items()), 'CONTROL_BINDING')
    need(control['decision'] in ('GO','STOP'), 'CONTROL_DECISION')
    if control['decision'] == 'STOP':
        need(set(payload) == {'CONTROL.json'} and control['files'] == {}, 'STOP_POPULATION')
        return 'STOP'
    need(set(payload) == CONTROL_NAMES and type(control['files']) is dict and
         set(control['files']) == CONTROL_NAMES - {'CONTROL.json'}, 'GO_POPULATION')
    for name in CONTROL_NAMES - {'CONTROL.json'}:
        need(control['files'][name] == {'sha256': sha(payload[name]), 'bytes': len(payload[name])}, 'CONTROL_PIN')
    review = parse(payload['INDEPENDENT_TECHNICAL_REVIEW.json'])
    review_fixed = {'schema': 'dg18.c02.startup-host-review.v1', 'reviewer': REVIEWER,
        'decision': 'PASS', 'blocking_findings': [], 'preparation_sha256': sha(prep_raw),
        'code_manifest_sha256': prep['code_manifest_sha256'], 'run_id': prep['run_id'],
        'workflow_commit': prep['workflow_commit'], 'independent_of_authors': True}
    need(type(review) is dict and all(review.get(k) == v and type(review.get(k)) is type(v)
         for k,v in review_fixed.items()), 'REVIEW_SCOPE')
    go = parse(payload['ROOT_GO.json'])
    go_fixed = {'schema': 'dg18.c02.startup-root-go.v1', 'author': '/root', 'decision': 'GO',
        'preparation_sha256': sha(prep_raw), 'code_manifest_sha256': prep['code_manifest_sha256'],
        'independent_review_sha256': sha(payload['INDEPENDENT_TECHNICAL_REVIEW.json']),
        'run_id': prep['run_id'], 'workflow_commit': prep['workflow_commit'], 'nonce': prep['nonce'],
        'source_scope': SOURCE, 'binary_sha256': BINARY_SHA, 'one_shot': True,
        'allocation_authorized': ALLOCATIONS, 'protected_tail_authorized': False,
        'model_turn_authorized': False, 'product_currentness_claimed': False,
        'reservation_checked': True, 'automatic_retry': False}
    need(type(go) is dict and set(go) == set(go_fixed) and all(go.get(k) == v and type(go[k]) is type(v)
         for k,v in go_fixed.items()), 'GO_SCOPE')
    return 'GO'


def verify_held(work, state, prep_raw):
    need(state['schema'] == 'dg18.c02.startup-private-state.v1' and
         state['preparation_sha256'] == sha(prep_raw) and
         time.monotonic_ns() < state['deadline_monotonic_ns'], 'HELD_BINDING_OR_EXPIRY')
    need(code_binding(work) == state['code'], 'HELD_CODE_CHANGED')
    need(regular(work / 'owned-bin/codex', BINARY_SIZE, keep=False)[1] == state['binary'], 'HELD_BINARY_CHANGED')
    need(regular(work / 'public-preparation/PREPARATION.json')[0] == prep_raw, 'PUBLIC_PREP_CHANGED')
    need(git(['-C', str(work / 'subject'), 'rev-parse', 'HEAD']).decode().strip() == state['subject_head'] and
         not git(['-C', str(work / 'subject'), 'status', '--porcelain=v1']), 'SUBJECT_CHANGED')
    need(set(p.name for p in (work / 'home').iterdir()) == set(), 'HOME_CHANGED')
    for name in ('subject','home','evidence','private'):
        private_dir(work / name)
    require_unexpired(state, parse(prep_raw))


def require_unexpired(state, prep):
    # The fixed preparation window is never renewed by code hashing, remote
    # control retrieval, configuration authoring or component preparation.
    need(time.monotonic_ns() < state['deadline_monotonic_ns'] and
         int(prep['created_unix_seconds']) * 1000 <= time.time_ns() // 1000000 <
         (int(prep['created_unix_seconds']) + HOLD_SECONDS) * 1000,
         'HELD_BINDING_OR_EXPIRY')


def modules(work):
    candidate = work / 'worker' / PREFIX / 'candidate'
    support = work / 'worker' / PREFIX / 'support'
    sys.path[:0] = [str(candidate), str(support)]
    return importlib.import_module('startup_subject'), importlib.import_module('local_responses_canary')


def config_bytes(work, url):
    return ('model="dg18-emulated-model"\nmodel_provider="dg18_canary"\nmodel_context_window=258400\n'
        '[projects.' + json.dumps(str(work / 'subject')) + ']\ntrust_level="trusted"\n'
        '[features]\nhooks=true\napps=false\n'
        '[model_providers.dg18_canary]\nname="R5 explicitly emulated Responses transport"\n'
        'base_url=' + json.dumps(url) + '\nwire_api="responses"\nrequires_openai_auth=false\n'
        'request_max_retries=0\nstream_max_retries=0\n[mcp_servers.cua_repl]\ncommand="/usr/bin/python3"\n'
        'args=' + json.dumps([str(work / 'worker' / PREFIX / 'support/local_mcp_canary.py'),
                              '--log', str(work / 'private/managed-mcp.jsonl')]) + '\n').encode()


def root_cleanup(proc):
    if proc is None:
        return 'NOT_ACQUIRED'
    # Once the child is reaped, the numeric process-group ID alone is not a
    # fresh identity. Do not signal a potentially reused group in that case.
    if proc.poll() is not None:
        try:
            os.killpg(proc.pid, 0)
        except ProcessLookupError:
            return 'CLOSED'
        return 'UNKNOWN'
    for sig in (signal.SIGTERM, signal.SIGKILL):
        # Every escalation gets its own live, unreaped-child check. poll() can
        # itself reap; after that only read-only group absence checks are safe.
        if proc.poll() is not None:
            try:
                os.killpg(proc.pid, 0)
            except ProcessLookupError:
                return 'CLOSED'
            return 'UNKNOWN'
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
        else:
            # wait() reaped the leader: never advance to another signal.
            try:
                os.killpg(proc.pid, 0)
            except ProcessLookupError:
                return 'CLOSED'
            return 'UNKNOWN'
        try:
            os.killpg(proc.pid, 0)
        except ProcessLookupError:
            return 'CLOSED'
    return 'UNKNOWN'


def execute(work, payload, commit, state, prep_raw):
    verify_held(work, state, prep_raw)
    prep = parse(prep_raw)
    need(control_head() == commit, 'CONTROL_MOVED')
    require_unexpired(state, prep)
    # Exclusive, retained consumption precedes every listener or native allocation.
    write_new(work / 'DISPATCH_RESERVED.json', encode({'control_commit': commit,
        'preparation_sha256': sha(prep_raw), 'root_go_sha256': sha(payload['ROOT_GO.json']),
        'one_shot': True, 'automatic_retry': False}), 0o400)
    for name, raw in payload.items():
        write_new(work / 'private' / name, raw)
    module, transport = modules(work)
    proc = provider = None
    result = {'schema': 'dg18.c02.startup-host-result.v1', 'authority': 'OBSERVATION_ONLY',
        'preparation_sha256': sha(prep_raw), 'root_go_sha256': sha(payload['ROOT_GO.json']),
        'dispatch_reserved': True, 'native_started': False, 'status': 'FAILED_BEFORE_OBSERVATION',
        'startup': None, 'root_cleanup': 'NOT_ACQUIRED', 'provider_closed': False,
        'provider_requests': None, 'provider_armed_steps': None, 'subject_head_unchanged': False,
        'original_acceptance': False, 'historical_warning_cause_resolved': False,
        'product_controller_created': False, 'protected_tail_executed': False, 'authentic_OR': False,
        'raw_evidence_published': False, 'automatic_retry': False}
    try:
        require_unexpired(state, prep)
        provider = transport.Provider(work / 'private/provider')
        config = config_bytes(work, provider.url)
        write_new(work / 'home/config.toml', config)
        now = time.time_ns() // 1000000
        request = {'schema': 'dg18.c02.startup-diagnostic-request.v1', 'nonce': prep['nonce'],
            'binary_sha256': BINARY_SHA, 'authored_config_sha256': sha(config),
            'root_authorization_sha256': sha(payload['ROOT_GO.json']),
            'independent_review_sha256': sha(payload['INDEPENDENT_TECHNICAL_REVIEW.json']),
            'host_preparation_sha256': sha(prep_raw), 'source_commit': SOURCE,
            'binary': str(work / 'owned-bin/codex'), 'home': str(work / 'home'),
            'subject': str(work / 'subject'), 'evidence_parent': str(work / 'evidence'),
            'not_before_unix_ms': now, 'expires_unix_ms': min(now + 60000,
                (int(prep['created_unix_seconds']) + HOLD_SECONDS) * 1000)}
        prepared = module.prepare(request)
        spec = prepared.launch_spec()
        require_unexpired(state, prep)
        proc = subprocess.Popen(spec['argv'], cwd=spec['cwd'], env=spec['env'], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False, bufsize=0, start_new_session=True)
        result['native_started'] = True
        write_new(work / 'private/NATIVE_STARTED.json', encode({'pid': proc.pid,
            'request_sha256': prepared.request_digest, 'preparation_sha256': sha(prep_raw)}))
        result['startup'] = module.observe_owned(prepared, proc)
        module.validate_receipt(result['startup'])
        result['status'] = 'OBSERVATION_RETURNED'
    except BaseException:
        # Raw exception and arbitrary native strings remain private, so root's
        # own failure is retained even if the component never wrote a checkpoint.
        import traceback
        write_new(work / 'private/EXECUTION_FAILURE.txt', traceback.format_exc().encode())
        result['status'] = 'FAILED_WITH_PRIVATE_EVIDENCE'
    finally:
        result['root_cleanup'] = root_cleanup(proc)
        if provider is not None:
            try:
                cleanup = provider.close()
                result['provider_closed'] = cleanup['provider_thread_joined'] is True
                result['provider_requests'] = min(cleanup['request_count'], 32)
                result['provider_armed_steps'] = min(cleanup['remaining_armed_steps'], 32)
            except BaseException:
                result['provider_closed'] = False
        try:
            result['subject_head_unchanged'] = git(['-C', str(work / 'subject'), 'rev-parse', 'HEAD']).decode().strip() == state['subject_head']
        except BaseException:
            pass
        # Retain a component checkpoint even when observe_owned did not return.
        if result['startup'] is None:
            try:
                path = work / 'evidence' / ('startup-diagnostic-' + prep['nonce']) / 'PUBLIC.json'
                checkpoint = parse(regular(path, MAX_PUBLIC)[0])
                module.validate_receipt(checkpoint)
                result['startup'] = checkpoint
            except BaseException:
                pass
        raw = validate_result(result, module)
        write_new(work / 'RESULT.json', raw)
    return 0 if result['status'] == 'OBSERVATION_RETURNED' else 1


def validate_result(value, module):
    keys = {'schema','authority','preparation_sha256','root_go_sha256','dispatch_reserved','native_started',
        'status','startup','root_cleanup','provider_closed','provider_requests','provider_armed_steps',
        'subject_head_unchanged','original_acceptance','historical_warning_cause_resolved',
        'product_controller_created','protected_tail_executed','authentic_OR','raw_evidence_published','automatic_retry'}
    need(type(value) is dict and set(value) == keys and value['schema'] == 'dg18.c02.startup-host-result.v1' and
         value['authority'] == 'OBSERVATION_ONLY', 'RESULT_SCHEMA')
    for name in ('preparation_sha256','root_go_sha256'):
        need(type(value[name]) is str and re.fullmatch('[0-9a-f]{64}', value[name]), 'RESULT_BINDING')
    for name in ('dispatch_reserved','native_started','provider_closed','subject_head_unchanged'):
        need(type(value[name]) is bool, 'RESULT_BOOL')
    for name in ('original_acceptance','historical_warning_cause_resolved','product_controller_created',
                 'protected_tail_executed','authentic_OR','raw_evidence_published','automatic_retry'):
        need(value[name] is False, 'RESULT_AUTHORITY')
    need(value['status'] in {'FAILED_BEFORE_OBSERVATION','FAILED_WITH_PRIVATE_EVIDENCE','OBSERVATION_RETURNED'} and
         value['root_cleanup'] in {'NOT_ACQUIRED','CLOSED','UNKNOWN'}, 'RESULT_ENUM')
    for name in ('provider_requests','provider_armed_steps'):
        need(value[name] is None or type(value[name]) is int and 0 <= value[name] <= 32, 'RESULT_COUNT')
    if value['startup'] is not None:
        module.validate_receipt(value['startup'])
    raw = encode(value)
    need(len(raw) <= MAX_PUBLIC, 'RESULT_PUBLIC_BOUND')
    return raw


def hold(work):
    prep_raw = regular(work / 'PREPARATION.json')[0]
    prep = parse(prep_raw)
    state = parse(regular(work / 'PRIVATE_STATE.json')[0])
    verify_held(work, state, prep_raw)
    git(['init', '--bare', '--quiet', str(work / 'control-cache.git')])
    seen = set()
    while time.monotonic_ns() < state['deadline_monotonic_ns']:
        commit = control_head()
        if commit is not None and commit not in seen:
            payload = read_control(work, commit, prep['control_path'])
            seen.add(commit)
            if payload is not None:
                need(validate_control(payload, prep_raw) == 'GO', 'OWNER_STOP')
                return execute(work, payload, commit, state, prep_raw)
        time.sleep(min(15, max(0, (state['deadline_monotonic_ns'] - time.monotonic_ns()) / 1e9)))
    raise Refusal('HOLD_EXPIRED')


def public_result(work):
    # A separate gate runs even after a nonzero worker exit, preserving failure evidence.
    code_binding(work)
    module, _ = modules(work)
    if (work / 'RESULT.json').exists():
        raw = validate_result(parse(regular(work / 'RESULT.json', MAX_PUBLIC)[0]), module)
    else:
        failure = parse(regular(work / 'ADAPTER_FAILURE.json', MAX_PUBLIC)[0])
        need(type(failure) is dict and set(failure) == {'schema','stage','reason','dispatch_reserved',
             'native_reach','raw_evidence_published','original_acceptance','automatic_retry'} and
             failure['schema'] == 'dg18.c02.startup-adapter-failure.v1' and
             failure['stage'] in {'prepare','hold'} and failure['reason'] in
             {'ADAPTER_REFUSAL','UNEXPECTED_EXCEPTION','INTERRUPTED'} and
             type(failure['dispatch_reserved']) is bool and
             failure['native_reach'] in {'NOT_DISPATCHED','UNKNOWN'} and
             failure['raw_evidence_published'] is False and failure['original_acceptance'] is False and
             failure['automatic_retry'] is False, 'ADAPTER_FAILURE_SCHEMA')
        raw = encode(failure)
    out = work / 'public-result'
    out.mkdir(mode=0o700)
    write_new(out / 'PUBLIC_RESULT.json', raw, 0o644)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare','hold','public-result'])
    parser.add_argument('--work', required=True)
    parser.add_argument('--run-id')
    parser.add_argument('--attempt')
    parser.add_argument('--commit')
    args = parser.parse_args()
    work = Path(args.work)
    os.umask(0o077)
    try:
        if args.action == 'prepare':
            prepare(work, args.run_id, args.attempt, args.commit)
            return 0
        if args.action == 'hold':
            return hold(work)
        public_result(work)
        return 0
    except BaseException as exc:
        # Failure artifacts survive ordinary failures, independently of worker
        # exit status. Retain exact traceback privately, never in public logs.
        if args.action != 'public-result':
            try:
                import traceback
                private_dir(work)
                write_new(work / 'PRIVATE_FAILURE.txt', traceback.format_exc().encode())
                reserved = (work / 'DISPATCH_RESERVED.json').exists()
                write_new(work / 'ADAPTER_FAILURE.json', encode({
                    'schema': 'dg18.c02.startup-adapter-failure.v1', 'stage': args.action,
                    'reason': 'ADAPTER_REFUSAL' if isinstance(exc, Refusal) else
                              ('INTERRUPTED' if isinstance(exc, (KeyboardInterrupt,SystemExit)) else 'UNEXPECTED_EXCEPTION'),
                    'dispatch_reserved': reserved, 'native_reach': 'UNKNOWN' if reserved else 'NOT_DISPATCHED',
                    'raw_evidence_published': False, 'original_acceptance': False, 'automatic_retry': False}))
            except BaseException:
                pass
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
