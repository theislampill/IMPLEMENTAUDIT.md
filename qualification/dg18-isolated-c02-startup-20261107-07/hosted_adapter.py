#!/usr/bin/env python3
"""One fresh, independently admitted C02 startup observation; no protected tail.

Only reviewed closed projections reach the public artifact directories. This
adapter does not initialize a product controller, send initialized, or start a
thread/model turn. The retained native guard still refuses configWarning.
"""
from pathlib import Path
import argparse
import ast
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
import types
import urllib.request
import importlib.util


def _load_host_dependency(name):
    # -I deliberately excludes the checkout from import search paths.
    # Only these reviewed adjacent modules are loaded by absolute path.
    path = Path(__file__).resolve().with_name(name + '.py')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


bwrap_host = _load_host_dependency('bwrap_host')
signed_distro_setup = _load_host_dependency('signed_distro_setup')

REPO = 'theislampill/IMPLEMENTAUDIT.md'
REMOTE = 'https://github.com/' + REPO + '.git'
BRANCH = 'pro/dg18-isolated-c02-startup-20261107-07'
CONTROL_BRANCH = 'pro/dg18-isolated-c02-startup-control-20261107-07'
PREFIX = 'qualification/dg18-isolated-c02-startup-20261107-07'
WORKFLOW = '.github/workflows/dg18-isolated-c02-startup-20261107-07.yml'
REVIEWER = '/root/c02_startup04_review'
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
               'same-host-closed-extractor', 'owned-process-cleanup',
               'first-other-warning-encryption', 'validated-ciphertext-export', 'one-affirmative-prelaunch-bwrap-probe']
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


def immutable_code_binding(work):
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


def code_binding(work):
    binding = immutable_code_binding(work)
    binding['warning_custody'] = custody_binding(work)
    return binding


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
    # Fresh reviewed hosted preparation may install one signed distro package.
    # This prerequisite has no native startup/admission authority.
    setup = signed_distro_setup.install_if_missing(work)
    bwrap = bwrap_host.prepare()
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
    request = {'schema': 'dg18.c02.startup-host-preparation.v3', 'authority': 'PREPARATION_ONLY',
        'repository': REPO, 'branch': BRANCH, 'workflow_commit': commit, 'run_id': run_id,
        'run_attempt': attempt, 'job': 'startup', 'nonce': os.urandom(32).hex(),
        'created_unix_seconds': int(time.time()), 'hold_seconds': HOLD_SECONDS,
        'source_scope': SOURCE, 'binary_sha256': BINARY_SHA, 'binary_bytes': BINARY_SIZE,
        'archive_sha256': ARCHIVE_SHA, 'archive_bytes': ARCHIVE_SIZE,
        'code_manifest_sha256': bindings['manifest_sha256'],
        'code_files': [{'path': k, 'sha256': v['sha256'], 'bytes': v['bytes']} for k,v in sorted(bindings['files'].items())],
        'systems': bindings['systems'], 'subject_head': head,
        'bwrap_binding_sha256': bwrap['binding_sha256'],
        'bwrap_dependencies_sha256': sha(bwrap_host.encoded(bwrap)),
        'bwrap_package': bwrap['binding']['package'], 'bwrap_probe': bwrap['probe'],
        'system_setup': {k: v for k, v in setup.items() if k != 'system_tools'},
        'warning_custody': {k: v for k, v in bindings['warning_custody'].items() if k != 'crypto_manifest'},
        'subject_prestate': 'FRESH_MINIMAL_GIT_FIXTURE_NO_PRODUCT_BOOTSTRAP',
        'config_constructor': 'RETAIN_ORIGINAL_VALUES_REBIND_OWNED_PATHS_AND_LOOPBACK',
        'control_branch': CONTROL_BRANCH, 'control_path': 'startup/' + run_id + '/1',
        'allocation_after_GO': ALLOCATIONS, 'execution_authorized': False,
        'original_acceptance': False, 'historical_warning_cause_resolved': False}
    raw = encode(request)
    need(len(raw) <= MAX_PUBLIC, 'PREPARATION_PUBLIC_BOUND')
    write_new(work / 'PREPARATION.json', raw)
    write_new(work / 'public-preparation' / 'PREPARATION.json', raw, 0o644)
    write_new(work / 'public-preparation' / 'CRYPTO_DEPENDENCIES.json',
              custody_module(work).canonical(bindings['warning_custody']['crypto_manifest']), 0o644)
    write_new(work / 'public-preparation/BWRAP_DEPENDENCIES.json', bwrap_host.encoded(bwrap), 0o644)
    write_new(work / 'private/SYSTEM_SETUP.json', encode(setup))
    state = {'schema': 'dg18.c02.startup-private-state.v3', 'preparation_sha256': sha(raw),
             'deadline_monotonic_ns': time.monotonic_ns() + HOLD_SECONDS * 1000000000,
             'code': bindings, 'binary': binary, 'subject_head': head, 'bwrap': bwrap}
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
    fixed = {'schema': 'dg18.c02.startup-control.v3', 'publisher': '/root', 'repository': REPO,
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
    review_fixed = {'schema': 'dg18.c02.startup-host-review.v3', 'reviewer': REVIEWER,
        'decision': 'PASS', 'blocking_findings': [], 'preparation_sha256': sha(prep_raw),
        'code_manifest_sha256': prep['code_manifest_sha256'], 'run_id': prep['run_id'],
        'workflow_commit': prep['workflow_commit'], 'independent_of_authors': True,
        'recipient_sha256': prep['warning_custody']['recipient_sha256'],
        'crypto_dependency_sha256': prep['warning_custody']['crypto_dependency_sha256'],
        'bwrap_binding_sha256': prep['bwrap_binding_sha256'],
        'affirmative_namespace_probe_received': True}
    need(type(review) is dict and all(review.get(k) == v and type(review.get(k)) is type(v)
         for k,v in review_fixed.items()), 'REVIEW_SCOPE')
    go = parse(payload['ROOT_GO.json'])
    go_fixed = {'schema': 'dg18.c02.startup-root-go.v3', 'author': '/root', 'decision': 'GO',
        'preparation_sha256': sha(prep_raw), 'code_manifest_sha256': prep['code_manifest_sha256'],
        'independent_review_sha256': sha(payload['INDEPENDENT_TECHNICAL_REVIEW.json']),
        'run_id': prep['run_id'], 'workflow_commit': prep['workflow_commit'], 'nonce': prep['nonce'],
        'source_scope': SOURCE, 'binary_sha256': BINARY_SHA, 'one_shot': True,
        'allocation_authorized': ALLOCATIONS, 'protected_tail_authorized': False,
        'model_turn_authorized': False, 'product_currentness_claimed': False,
        'reservation_checked': True, 'automatic_retry': False,
        'recipient_sha256': prep['warning_custody']['recipient_sha256'],
        'crypto_dependency_sha256': prep['warning_custody']['crypto_dependency_sha256'],
        'bwrap_binding_sha256': prep['bwrap_binding_sha256']}
    need(type(go) is dict and set(go) == set(go_fixed) and all(go.get(k) == v and type(go[k]) is type(v)
         for k,v in go_fixed.items()), 'GO_SCOPE')
    return 'GO'


def verify_held(work, state, prep_raw):
    need(state['schema'] == 'dg18.c02.startup-private-state.v3' and
         state['preparation_sha256'] == sha(prep_raw) and
         time.monotonic_ns() < state['deadline_monotonic_ns'], 'HELD_BINDING_OR_EXPIRY')
    need(code_binding(work) == state['code'], 'HELD_CODE_CHANGED')
    bwrap_host.recheck(state['bwrap'])
    need(parse(prep_raw)['bwrap_binding_sha256'] == state['bwrap']['binding_sha256'] and
         regular(work / 'public-preparation/BWRAP_DEPENDENCIES.json', 262144)[0] == bwrap_host.encoded(state['bwrap']) and
         parse(prep_raw)['bwrap_dependencies_sha256'] == sha(bwrap_host.encoded(state['bwrap'])), 'HELD_BWRAP_CHANGED')
    need(regular(work / 'owned-bin/codex', BINARY_SIZE, keep=False)[1] == state['binary'], 'HELD_BINARY_CHANGED')
    need(regular(work / 'public-preparation/PREPARATION.json')[0] == prep_raw, 'PUBLIC_PREP_CHANGED')
    need(regular(work / 'public-preparation/CRYPTO_DEPENDENCIES.json', 65536)[0] ==
         custody_module(work).canonical(state['code']['warning_custody']['crypto_manifest']), 'PUBLIC_CRYPTO_CHANGED')
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
    result = {'schema': 'dg18.c02.startup-host-result.v2', 'authority': 'OBSERVATION_ONLY',
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
        request = {'schema': 'dg18.c02.startup-diagnostic-request.v2', 'nonce': prep['nonce'],
            'binary_sha256': BINARY_SHA, 'authored_config_sha256': sha(config),
            'root_authorization_sha256': sha(payload['ROOT_GO.json']),
            'independent_review_sha256': sha(payload['INDEPENDENT_TECHNICAL_REVIEW.json']),
            'host_preparation_sha256': sha(prep_raw), 'source_commit': SOURCE,
            'recipient_sha256': prep['warning_custody']['recipient_sha256'],
            'crypto_dependency_sha256': prep['warning_custody']['crypto_dependency_sha256'],
            'binary': str(work / 'owned-bin/codex'), 'home': str(work / 'home'),
            'subject': str(work / 'subject'), 'evidence_parent': str(work / 'evidence'),
            'not_before_unix_ms': now, 'expires_unix_ms': min(now + 60000,
                (int(prep['created_unix_seconds']) + HOLD_SECONDS) * 1000)}
        prepared = module.prepare(request)
        spec = prepared.launch_spec()
        require_unexpired(state, prep)
        # Positive namespace execution immediately precedes native allocation.
        probe = bwrap_host.recheck(state['bwrap'], affirmative=True)
        write_new(work / 'private/PRELAUNCH_BWRAP.json', bwrap_host.encoded(probe))
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
    need(type(value) is dict and set(value) == keys and value['schema'] == 'dg18.c02.startup-host-result.v2' and
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


def public_result(work, run_id, attempt, commit):
    # Public source/system integrity remains mandatory. Crypto capability is a
    # native admission prerequisite, not a prerequisite for exporting its refusal.
    binding = immutable_code_binding(work)
    identity = workflow_identity(run_id, attempt, commit)
    module, _ = modules(work)
    if (work / 'RESULT.json').exists():
        prep_raw = regular(work / 'PREPARATION.json', MAX_PUBLIC)[0]
        prep = parse(prep_raw)
        need(preparation_identity(prep) == identity and prep['code_manifest_sha256'] == binding['manifest_sha256'], 'RESULT_PREPARATION_BINDING')
        value = parse(regular(work / 'RESULT.json', MAX_PUBLIC)[0])
        raw = validate_result(value, module)
        need(value['preparation_sha256'] == sha(prep_raw), 'RESULT_PREPARATION_CHANGED')
    else:
        failure = parse(regular(work / 'ADAPTER_FAILURE.json', MAX_PUBLIC)[0])
        raw = validate_failure(failure, identity, binding)
        if failure['context'] == 'PREPARATION':
            prep_raw = regular(work / 'PREPARATION.json', MAX_PUBLIC)[0]
            prep = parse(prep_raw)
            need(preparation_identity(prep) == identity and prep['code_manifest_sha256'] == binding['manifest_sha256']
                 and sha(prep_raw) == failure['preparation_sha256'], 'FAILURE_PREPARATION_CHANGED')
        else:
            need(not (work / 'PREPARATION.json').exists(), 'FAILURE_PREPARATION_UNEXPECTED')
    out = work / 'public-result'
    out.mkdir(mode=0o700)
    write_new(out / 'PUBLIC_RESULT.json', raw, 0o644)


def custody_module(work):
    candidate = work / 'worker' / PREFIX / 'candidate'
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
    module = importlib.import_module('warning_custody')
    need(Path(module.__file__).resolve(strict=True) == candidate / 'warning_custody.py', 'CUSTODY_MODULE_LOCATION')
    return module


def custody_binding(work):
    custody = custody_module(work)
    recipient = custody.load_recipient()
    manifest = custody.dependency_manifest()
    raw = custody.canonical(manifest)
    return {'recipient_sha256': recipient['recipient_sha256'], 'crypto_dependency_sha256': sha(raw),
            'crypto_dependency_bytes': len(raw), 'crypto_manifest': manifest}


def public_custody(work):
    """Separate exact-ciphertext gate; its failure cannot erase PUBLIC_RESULT.json."""
    binding = code_binding(work)
    module, _ = modules(work)
    result = parse(validate_result(parse(regular(work / 'RESULT.json', MAX_PUBLIC)[0]), module))
    startup = result['startup']
    if startup is None or startup['warning_custody']['status'] != 'SEALED':
        return
    status = startup['warning_custody']
    need(result['root_cleanup'] == 'CLOSED' and result['provider_closed'] is True and
         result['provider_requests'] == 0 and result['provider_armed_steps'] == 0,
         'CUSTODY_EFFECT_BOUNDARY')
    current = binding['warning_custody']
    need(current['recipient_sha256'] == status['recipient_sha256'] and
         current['crypto_dependency_sha256'] == status['crypto_dependency_sha256'], 'CUSTODY_DEPENDENCY_CHANGED')
    prep_raw = regular(work / 'PREPARATION.json', MAX_PUBLIC)[0]
    need(sha(prep_raw) == result['preparation_sha256'], 'CUSTODY_PREPARATION_CHANGED')
    prep = parse(prep_raw)
    need(type(prep['nonce']) is str and re.fullmatch('[0-9a-f]{64}', prep['nonce']), 'CUSTODY_NONCE')
    custody = custody_module(work)
    path = work / 'evidence' / ('startup-diagnostic-' + prep['nonce']) / 'private' / 'WARNING.enc.json'
    envelope, _ = regular(path, custody.MAX_ENVELOPE)
    need(sha(envelope) == status['ciphertext_sha256'] and len(envelope) == status['ciphertext_bytes'], 'CUSTODY_ARTIFACT_CHANGED')
    header, _ = custody.validate_envelope(envelope, expected_request_digest=startup['request_digest'],
        expected_crypto_sha256=status['crypto_dependency_sha256'], expected_recipient_sha256=status['recipient_sha256'])
    need(header['record_ordinal'] == startup['observer']['records'], 'CUSTODY_ORDINAL_CHANGED')
    out = work / 'public-custody'
    out.mkdir(mode=0o700)
    write_new(out / 'WARNING.enc.json', envelope, 0o644)


def workflow_identity(run_id, attempt, commit):
    need(type(run_id) is str and re.fullmatch('[1-9][0-9]{0,23}', run_id) and attempt == '1'
         and type(commit) is str and re.fullmatch('[0-9a-f]{40}', commit), 'RESULT_WORKFLOW_IDENTITY')
    return {'run_id': run_id, 'run_attempt': attempt, 'workflow_commit': commit}


def preparation_identity(prep):
    need(type(prep) is dict and prep.get('schema') == 'dg18.c02.startup-host-preparation.v3', 'RESULT_PREPARATION_SCHEMA')
    return workflow_identity(prep.get('run_id'), prep.get('run_attempt'), prep.get('workflow_commit'))


# This observation path never calls a preparation, package, namespace or native
# operation. Phase means the public source callsite at which failure escaped;
# it does not attest completion, effects, cleanup, or the historical cause.
FAILURE_ROLES = {
    'ADAPTER': 'hosted_adapter.py',
    'BWRAP_HOST': 'bwrap_host.py',
    'SIGNED_DISTRO_SETUP': 'signed_distro_setup.py',
    'APT_TRANSACTION_GUARD': 'apt_transaction_guard.py',
    'WARNING_CUSTODY': 'candidate/warning_custody.py',
}
FAILURE_PHASES = ('ENTRY_VALIDATION', 'CODE_AND_CRYPTO_BINDING',
    'CHECKOUT_VALIDATION', 'SYSTEM_PACKAGE_SETUP', 'BWRAP_ADMISSION',
    'BINARY_ACQUISITION', 'SUBJECT_FIXTURE', 'PREPARATION_PUBLICATION')
FAILURE_TYPE_NAMES = ('ADAPTER_REFUSAL', 'BWRAP_REFUSAL', 'APT_REFUSAL', 'CUSTODY_REFUSAL',
    'PERMISSION_ERROR', 'FILE_NOT_FOUND_ERROR', 'FILE_EXISTS_ERROR',
    'NOT_A_DIRECTORY_ERROR', 'IS_A_DIRECTORY_ERROR', 'OS_ERROR', 'TIMEOUT_ERROR',
    'TYPE_ERROR', 'VALUE_ERROR', 'KEY_ERROR', 'ATTRIBUTE_ERROR', 'IMPORT_ERROR',
    'MODULE_NOT_FOUND_ERROR', 'UNICODE_DECODE_ERROR', 'KEYBOARD_INTERRUPT', 'SYSTEM_EXIT')
FAILURE_SCAN_MAX, FAILURE_FRAMES_MAX, FAILURE_LINE_MAX = 64, 8, 65535


def build_failure_codebook(sources):
    """Deterministic source-only generator; no imports or execution of input."""
    need(type(sources) is dict and set(sources) == set(FAILURE_ROLES), 'DIAGNOSTIC_SOURCE_ROLES')
    files, functions, sites, phases, path_calls = [], [], [], [], []
    path_contract = path_guard_source_contract(sources['BWRAP_HOST'])
    local_types = {'ADAPTER': 'ADAPTER_REFUSAL', 'BWRAP_HOST': 'BWRAP_REFUSAL',
                   'APT_TRANSACTION_GUARD': 'APT_REFUSAL', 'WARNING_CUSTODY': 'CUSTODY_REFUSAL'}
    for role, path in FAILURE_ROLES.items():
        raw = sources[role]
        need(type(raw) is bytes and 0 < len(raw) <= 262144, 'DIAGNOSTIC_SOURCE_BOUND')
        tree = ast.parse(raw, filename=path)
        need(len(raw.splitlines()) <= FAILURE_LINE_MAX, 'DIAGNOSTIC_LINE_BOUND')
        files.append({'role': role, 'path': path, 'bytes': len(raw), 'sha256': sha(raw)})

        def path_call(node, current):
            if role not in ('BWRAP_HOST', 'SIGNED_DISTRO_SETUP') or current is None or not isinstance(node, ast.Call):
                return
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) and role == 'BWRAP_HOST' else (
                fn.attr if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) and fn.value.id == 'host' and role == 'SIGNED_DISTRO_SETUP' else None)
            if name not in ('protected_chain', 'protected_file', 'protected_directory'):
                return
            literal = node.args[0].value if node.args and isinstance(node.args[0], ast.Constant) and type(node.args[0].value) is str else None
            path_calls.append({'role': role, 'function': current, 'first_line': node.lineno,
                               'last_line': node.end_lineno, 'call_role': name.upper(),
                               'literal_invocation_role': path_contract['invocation_paths'].get(literal)})

        def visit(node, scope='', lookup=(), current=None, in_function=False):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                sep = '.<locals>.' if in_function else ('.' if scope else '')
                qualified = scope + sep + node.name
                is_function = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                root = lookup if in_function else lookup + (node.name,)
                if is_function:
                    row = {'role': role, 'function': qualified, 'lookup': list(root),
                           'first_line': node.lineno, 'last_line': node.end_lineno}
                    functions.append(row)
                    if role == 'ADAPTER' and qualified == 'prepare':
                        anchors = {'bindings': 'CODE_AND_CRYPTO_BINDING', 'worker': 'CHECKOUT_VALIDATION',
                            'setup': 'SYSTEM_PACKAGE_SETUP', 'bwrap': 'BWRAP_ADMISSION',
                            'binary': 'BINARY_ACQUISITION', 'request': 'PREPARATION_PUBLICATION'}
                        starts = [('ENTRY_VALIDATION', node.lineno)]
                        for statement in node.body:
                            if isinstance(statement, ast.Assign) and len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
                                name = statement.targets[0].id
                                if name in anchors:
                                    starts.append((anchors[name], statement.lineno))
                            if isinstance(statement, ast.For):
                                starts.append(('SUBJECT_FIXTURE', statement.lineno))
                        need(tuple(label for label, _ in starts) == FAILURE_PHASES, 'DIAGNOSTIC_PREPARE_SHAPE')
                        for index, (label, start) in enumerate(starts):
                            end = starts[index + 1][1] - 1 if index + 1 < len(starts) else node.end_lineno
                            phases.append({'phase': label, 'first_line': start, 'last_line': end})
                for child in node.body:
                    visit(child, qualified, root, qualified if is_function else None, is_function)
                return
            if isinstance(node, (ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                # A public containing function pauses at this source expression;
                # anonymous runtime frames themselves remain unqualified.
                for child in ast.walk(node):
                    path_call(child, current)
                return
            path_call(node, current)
            if isinstance(node, ast.Call) and current is not None:
                call, literal, kind = node.func, None, None
                if isinstance(call, ast.Name) and call.id == 'need' and len(node.args) >= 2:
                    literal, kind = node.args[1], local_types.get(role)
                elif isinstance(call, ast.Name) and call.id in ('Refusal', 'CustodyRefusal') and node.args:
                    literal, kind = node.args[0], local_types.get(role)
                elif role == 'SIGNED_DISTRO_SETUP' and isinstance(call, ast.Attribute) and isinstance(call.value, ast.Name) and call.attr == 'need' and len(node.args) >= 2:
                    literal, kind = node.args[1], {'host': 'BWRAP_REFUSAL', 'gate': 'APT_REFUSAL'}.get(call.value.id)
                if kind and isinstance(literal, ast.Constant) and type(literal.value) is str and re.fullmatch('[A-Z][A-Z0-9_]{0,95}', literal.value):
                    sites.append({'role': role, 'function': current, 'first_line': node.lineno,
                                  'last_line': node.end_lineno, 'exception_type': kind, 'code': literal.value})
            # Lambda/comprehension code has no declared-function row and cannot
            # qualify as a published frame or confer a literal refusal code.
            for child in ast.iter_child_nodes(node):
                visit(child, scope, lookup, current, in_function)
        visit(tree)
    need(len(phases) == len(FAILURE_PHASES), 'DIAGNOSTIC_PREPARE_ABSENT')
    return {'schema': 'dg18.c02.startup-failure-codebook.v2', 'source_scope': SOURCE,
            'files': files, 'functions': functions, 'literal_refusal_sites': sites,
            'prepare_source_phases': phases, 'path_guard_contract': path_contract,
            'path_guard_call_sites': path_calls}


def load_failure_codebook(binding):
    bundle = Path(__file__).resolve(strict=True).parent
    sources = {}
    for role, name in FAILURE_ROLES.items():
        raw, stamp = regular(bundle / name, 262144)
        expected = binding['files'][PREFIX + '/' + name]
        need(stamp['sha256'] == expected['sha256'] and len(raw) == expected['bytes'], 'DIAGNOSTIC_SOURCE_PIN')
        sources[role] = raw
    need(sum(map(len, sources.values())) <= 524288, 'DIAGNOSTIC_SOURCES_BOUND')
    raw, stamp = regular(bundle / 'FAILURE_CODEBOOK.json', 262144)
    expected = binding['files'][PREFIX + '/FAILURE_CODEBOOK.json']
    need(stamp['sha256'] == expected['sha256'] and len(raw) == expected['bytes'], 'DIAGNOSTIC_CODEBOOK_PIN')
    book = parse(raw)
    need(raw == encode(build_failure_codebook(sources)), 'DIAGNOSTIC_CODEBOOK_SHAPE')
    return book, sources, stamp['sha256']


def failure_code_key(code, depth=0):
    """Compare only exact builtin code/constant metadata; never repr or locals."""
    need(type(code) is types.CodeType and depth < 32, 'DIAGNOSTIC_CODE_SHAPE')

    def constant(value):
        kind = type(value)
        if value is None or value is Ellipsis:
            return ('NONE' if value is None else 'ELLIPSIS',)
        if kind in (str, bytes, int, bool):
            return (kind.__name__, value)
        if kind is float:
            return ('float', value.hex())
        if kind is complex:
            return ('complex', value.real.hex(), value.imag.hex())
        if kind in (tuple, frozenset):
            rows = tuple(constant(item) for item in value)
            return (kind.__name__, rows if kind is tuple else frozenset(rows))
        if kind is types.CodeType:
            return ('code', failure_code_key(value, depth + 1))
        raise Refusal('DIAGNOSTIC_CONSTANT_SHAPE')
    return (code.co_argcount, code.co_posonlyargcount, code.co_kwonlyargcount,
            code.co_nlocals, code.co_stacksize, code.co_flags, code.co_code,
            code.co_names, code.co_varnames, code.co_freevars, code.co_cellvars,
            code.co_filename, code.co_name, code.co_qualname, code.co_firstlineno,
            code.co_linetable, code.co_exceptiontable, tuple(constant(v) for v in code.co_consts))


def failure_compiled_functions(raw, path):
    root = compile(raw, str(path), 'exec', dont_inherit=True, optimize=0)
    found = {}
    def walk(code):
        for item in code.co_consts:
            if type(item) is types.CodeType:
                if not item.co_name.startswith('<'):
                    need(item.co_qualname not in found, 'DIAGNOSTIC_AMBIGUOUS_FUNCTION')
                    found[item.co_qualname] = item
                walk(item)
    walk(root)
    return found


def failure_frame_registry(book, sources):
    bundle = Path(__file__).resolve(strict=True).parent
    modules = {'ADAPTER': globals(), 'BWRAP_HOST': vars(bwrap_host),
               'SIGNED_DISTRO_SETUP': vars(signed_distro_setup),
               'APT_TRANSACTION_GUARD': vars(signed_distro_setup.gate)}
    custody = sys.modules.get('warning_custody')
    if type(custody) is types.ModuleType:
        modules['WARNING_CUSTODY'] = vars(custody)
    registry = {}
    for role, namespace in modules.items():
        path = bundle / FAILURE_ROLES[role]
        if namespace.get('__file__') != str(path):
            continue
        compiled = failure_compiled_functions(sources[role], path)
        roots = {}
        for row in book['functions']:
            if row['role'] != role:
                continue
            lookup = tuple(row['lookup'])
            if lookup not in roots:
                value = namespace.get(lookup[0])
                for part in lookup[1:]:
                    value = vars(value).get(part) if type(value) is type else None
                roots[lookup] = value
            value = roots[lookup]
            if type(value) is not types.FunctionType or value.__globals__ is not namespace:
                continue
            expected_root = compiled.get(value.__code__.co_qualname)
            if expected_root is None or failure_code_key(value.__code__) != failure_code_key(expected_root):
                continue
            pending = [value.__code__]
            while pending:
                code = pending.pop()
                if code.co_qualname == row['function'] and code.co_firstlineno == row['first_line']:
                    registry[id(code)] = (code, namespace, row)
                pending.extend(c for c in code.co_consts if type(c) is types.CodeType)
    return registry


def unknown_path_guard():
    return {'schema': 'dg18.c02.path-mutability-observation.v1', 'status': 'UNKNOWN',
            'call_site': None, 'invocation_role': None, 'node_role': None,
            'resolution_relation': None, 'chain_role': None, 'ancestry_index': None,
            'ancestry_depth': None, 'node_symlink': None, 'mode_write_mask': None,
            'group_write': None, 'other_write': None, 'mode_nonwritable': None,
            'effective_write_access': None, 'effective_ids': None, 'access_mode': None,
            'predicate_result': None}


def path_guard_source_contract(raw):
    """Extract only fixed literal role maps from the reviewed public module."""
    names = {'PATH_GUARD_PATHS', 'PATH_GUARD_NODES', 'PATH_GUARD_POSITION_MAX'}
    values = {}
    for node in ast.parse(raw).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
            need(node.targets[0].id not in values, 'PATH_OBSERVATION_CONTRACT_DUPLICATE')
            values[node.targets[0].id] = ast.literal_eval(node.value)
    need(set(values) == names and type(values['PATH_GUARD_POSITION_MAX']) is int and
         values['PATH_GUARD_POSITION_MAX'] == 64, 'PATH_OBSERVATION_CONTRACT')
    for name in ('PATH_GUARD_PATHS', 'PATH_GUARD_NODES'):
        table = values[name]
        need(type(table) is dict and 0 < len(table) <= 32 and len(set(table.values())) == len(table), 'PATH_OBSERVATION_ROLE_TABLE')
        need(all(type(path) is str and path.startswith('/') and '..' not in Path(path).parts and
                 type(role) is str and re.fullmatch('[A-Z][A-Z0-9_]{0,63}', role) for path, role in table.items()), 'PATH_OBSERVATION_ROLE_SHAPE')
    return {'invocation_paths': values['PATH_GUARD_PATHS'], 'node_paths': values['PATH_GUARD_NODES'],
            'position_max': values['PATH_GUARD_POSITION_MAX'], 'mode_mask': 0o022,
            'effective_ids': True, 'access_mode': 'W_OK', 'unevaluated': 'NOT_EVALUATED'}


def path_guard_public_call(frames, book):
    matches = []
    for frame in frames:
        for site in book['path_guard_call_sites']:
            if frame['role'] == site['role'] and frame['function'] == site['function'] and site['first_line'] <= frame['line'] <= site['last_line']:
                matches.append((site, frame))
    # Prefer the actual public binding call; chain-entry callers still qualify
    # direct protected_file/protected_directory calls without inventing a caller.
    selected = next(((site, frame) for site, frame in matches if site['call_role'] != 'PROTECTED_CHAIN'),
                    matches[0] if matches else None)
    if selected is None:
        return None
    site, frame = selected
    return {'role': site['role'], 'function': site['function'], 'line': frame['line'],
            'call_role': site['call_role'], 'literal_invocation_role': site['literal_invocation_role']}


def validate_path_guard(value, diagnostic, book):
    need(type(value) is dict and set(value) == set(unknown_path_guard()), 'PATH_OBSERVATION_SCHEMA')
    if value == unknown_path_guard():
        return
    need(value['schema'] == 'dg18.c02.path-mutability-observation.v1' and value['status'] == 'OBSERVED', 'PATH_OBSERVATION_SCHEMA')
    need(diagnostic['exception_type'] == 'BWRAP_REFUSAL' and diagnostic['refusal_code'] == 'BWRAP_PATH_MUTABLE', 'PATH_OBSERVATION_REFUSAL')
    sites = failure_refusal_sites(diagnostic['frames'], book, 'BWRAP_REFUSAL')
    need(any(site['code'] == 'BWRAP_PATH_MUTABLE' and site['role'] == 'BWRAP_HOST' and site['function'] == 'protected_chain' for site in sites), 'PATH_OBSERVATION_GUARD_SITE')
    expected_call = path_guard_public_call(diagnostic['frames'], book)
    need(expected_call is not None and type(value['call_site']) is dict and
         set(value['call_site']) == set(expected_call) and
         all(type(value['call_site'][key]) is type(expected) and value['call_site'][key] == expected for key, expected in expected_call.items()), 'PATH_OBSERVATION_CALL_SITE')
    contract = book['path_guard_contract']
    paths, nodes = contract['invocation_paths'], contract['node_paths']
    need(type(value['invocation_role']) is str and value['invocation_role'] in {*paths.values(), 'UNLISTED_SYSTEM_PATH'} and
         type(value['node_role']) is str and value['node_role'] in {*paths.values(), *nodes.values(), 'UNLISTED_SYSTEM_NODE'}, 'PATH_OBSERVATION_ROLE')
    literal = expected_call['literal_invocation_role']
    need(literal is None or value['invocation_role'] == literal, 'PATH_OBSERVATION_LITERAL_PATH')
    need(type(value['resolution_relation']) is str and value['resolution_relation'] in ('SAME', 'DIFFERENT') and
         type(value['chain_role']) is str and value['chain_role'] in ('INVOCATION', 'RESOLVED'), 'PATH_OBSERVATION_CHAIN')
    index, depth = value['ancestry_index'], value['ancestry_depth']
    need(type(index) is int and type(depth) is int and 0 <= index <= depth <= contract['position_max'], 'PATH_OBSERVATION_POSITION')
    need((value['node_role'] == 'ROOT') == (index == depth), 'PATH_OBSERVATION_ROOT_POSITION')
    if value['invocation_role'] != 'UNLISTED_SYSTEM_PATH' and (value['chain_role'] == 'INVOCATION' or value['resolution_relation'] == 'SAME'):
        path = Path(next(path for path, role in paths.items() if role == value['invocation_role']))
        population = (path, *path.parents)
        need(depth == len(population) - 1, 'PATH_OBSERVATION_INVOCATION_DEPTH')
        text = str(population[index])
        need(value['node_role'] == nodes.get(text, paths.get(text, 'UNLISTED_SYSTEM_NODE')), 'PATH_OBSERVATION_NODE_ROLE')
    mask = value['mode_write_mask']
    need(type(mask) is int and mask in (0, 2, 16, 18) and value['node_symlink'] is False and
         value['effective_ids'] is True and type(value['access_mode']) is str and value['access_mode'] == 'W_OK' and value['predicate_result'] is False, 'PATH_OBSERVATION_OPERANDS')
    need(type(value['group_write']) is bool and value['group_write'] == bool(mask & 0o020) and
         type(value['other_write']) is bool and value['other_write'] == bool(mask & 0o002) and
         type(value['mode_nonwritable']) is bool and value['mode_nonwritable'] == (mask == 0), 'PATH_OBSERVATION_MODE_TERMS')
    if mask:
        need(type(value['effective_write_access']) is str and value['effective_write_access'] == 'NOT_EVALUATED', 'PATH_OBSERVATION_SHORT_CIRCUIT')
    else:
        need(value['effective_write_access'] is True, 'PATH_OBSERVATION_ACCESS_TERM')


def project_path_guard(exc, diagnostic, book):
    try:
        if type(exc) is not bwrap_host.Refusal or diagnostic['exception_type'] != 'BWRAP_REFUSAL' or diagnostic['refusal_code'] != 'BWRAP_PATH_MUTABLE':
            return unknown_path_guard()
        contract = book['path_guard_contract']
        need(bwrap_host.PATH_GUARD_PATHS == contract['invocation_paths'] and bwrap_host.PATH_GUARD_NODES == contract['node_paths'] and
             type(bwrap_host.PATH_GUARD_POSITION_MAX) is int and bwrap_host.PATH_GUARD_POSITION_MAX == contract['position_max'], 'PATH_OBSERVATION_RUNTIME_CONTRACT')
        captured = object.__getattribute__(exc, '__dict__').get('_c02_path_mutability')
        fields = set(unknown_path_guard()) - {'schema', 'status', 'call_site'}
        need(type(captured) is dict and set(captured) == fields | {'schema'} and
             captured['schema'] == 'dg18.c02.path-mutability-capture.v1', 'PATH_OBSERVATION_CAPTURE_SHAPE')
        # Only known scalar fields are copied; validation precedes publication.
        value = {'schema': 'dg18.c02.path-mutability-observation.v1', 'status': 'OBSERVED',
                 'call_site': path_guard_public_call(diagnostic['frames'], book),
                 **{key: captured[key] for key in fields}}
        validate_path_guard(value, diagnostic, book)
        return value
    except BaseException:
        return unknown_path_guard()  # Keep the already qualified outer diagnosis.


def unknown_failure_diagnostic(digest=None, stack='UNKNOWN'):
    return {'schema': 'dg18.c02.startup-failure-diagnostic.v2',
            'codebook_sha256': digest, 'status': 'UNKNOWN', 'phase': 'UNKNOWN',
            'exception_type': 'UNKNOWN', 'refusal_code': 'UNKNOWN', 'frames': [], 'stack': stack,
            'path_guard': unknown_path_guard()}


def failure_phase(frames, book):
    locations = [row['line'] for row in frames if row['role'] == 'ADAPTER' and row['function'] == 'prepare']
    if len(locations) != 1:
        return 'UNKNOWN'
    return next((row['phase'] for row in book['prepare_source_phases']
                 if row['first_line'] <= locations[0] <= row['last_line']), 'UNKNOWN')


def failure_refusal_sites(frames, book, kind):
    return [site for site in book['literal_refusal_sites'] if site['exception_type'] == kind and
            any(frame['role'] == site['role'] and frame['function'] == site['function'] and
                site['first_line'] <= frame['line'] <= site['last_line'] for frame in frames)]


def project_failure_diagnostic(exc, binding):
    """Observe one exception; any unqualified metadata yields closed UNKNOWN."""
    try:
        book, sources, digest = load_failure_codebook(binding)
        registry = failure_frame_registry(book, sources)
        frames, filtered, count, seen_frames = [], False, 0, set()
        tb = BaseException.__traceback__.__get__(exc)
        while tb is not None:
            count += 1
            if count > FAILURE_SCAN_MAX:
                return unknown_failure_diagnostic(digest, 'FRAME_LIMIT')
            if id(tb.tb_frame) in seen_frames:
                return unknown_failure_diagnostic(digest)
            seen_frames.add(id(tb.tb_frame))
            code = tb.tb_frame.f_code
            match = registry.get(id(code))
            if match is not None and match[0] is code and tb.tb_frame.f_globals is match[1]:
                row, line = match[2], tb.tb_lineno
                qualified = type(line) is int and 0 < line <= FAILURE_LINE_MAX and row['first_line'] <= line <= row['last_line']
                qualified = qualified and any(start <= tb.tb_lasti < end and found == line for start, end, found in code.co_lines())
                if qualified:
                    frames.append({'role': row['role'], 'function': row['function'], 'line': line})
                else:
                    filtered = True
            else:
                filtered = True
            tb = tb.tb_next
        if not frames:
            return unknown_failure_diagnostic(digest, 'FOREIGN_FILTERED' if filtered else 'UNKNOWN')
        limited = len(frames) > FAILURE_FRAMES_MAX
        if limited:
            frames = frames[:2] + frames[-(FAILURE_FRAMES_MAX - 2):]
        stack = 'FRAME_LIMIT' if limited else ('FOREIGN_FILTERED' if filtered else 'PUBLIC_ONLY')
        known = [(Refusal, 'ADAPTER_REFUSAL'), (bwrap_host.Refusal, 'BWRAP_REFUSAL'),
                 (signed_distro_setup.gate.Refusal, 'APT_REFUSAL')]
        custody = sys.modules.get('warning_custody')
        if type(custody) is types.ModuleType and vars(custody).get('__file__') == str(Path(__file__).resolve().parent / FAILURE_ROLES['WARNING_CUSTODY']):
            known.append((custody.CustodyRefusal, 'CUSTODY_REFUSAL'))
        known.extend(zip((PermissionError, FileNotFoundError, FileExistsError, NotADirectoryError,
            IsADirectoryError, OSError, TimeoutError, TypeError, ValueError, KeyError, AttributeError,
            ImportError, ModuleNotFoundError, UnicodeDecodeError, KeyboardInterrupt, SystemExit), FAILURE_TYPE_NAMES[4:]))
        kind = next((label for cls, label in known if type(exc) is cls), 'UNKNOWN')
        refusal = 'UNKNOWN' if kind == 'UNKNOWN' or kind in FAILURE_TYPE_NAMES[:4] else 'NOT_APPLICABLE'
        if kind in FAILURE_TYPE_NAMES[:4]:
            arguments = BaseException.args.__get__(exc)
            if type(arguments) is tuple and len(arguments) == 1 and type(arguments[0]) is str:
                refusal = next((site['code'] for site in failure_refusal_sites(frames, book, kind)
                                if arguments[0] == site['code']), 'UNKNOWN')
        diagnostic = {'schema': 'dg18.c02.startup-failure-diagnostic.v2', 'codebook_sha256': digest,
                'status': 'SOURCE_BOUND' if stack == 'PUBLIC_ONLY' else 'PARTIAL_SOURCE_BOUND',
                'phase': failure_phase(frames, book), 'exception_type': kind,
                'refusal_code': refusal, 'frames': frames, 'stack': stack}
        diagnostic['path_guard'] = project_path_guard(exc, diagnostic, book)
        return diagnostic
    except BaseException:
        # The original failure remains the record_failure input and broad result.
        return unknown_failure_diagnostic()


def validate_failure_diagnostic(value, binding):
    need(type(value) is dict and set(value) == set(unknown_failure_diagnostic()), 'DIAGNOSTIC_SCHEMA')
    need(value['schema'] == 'dg18.c02.startup-failure-diagnostic.v2', 'DIAGNOSTIC_SCHEMA')
    try:
        book, sources, digest = load_failure_codebook(binding)
    except BaseException:
        need(value == unknown_failure_diagnostic(), 'DIAGNOSTIC_UNQUALIFIED')
        return
    if value == unknown_failure_diagnostic():
        return  # Observation itself may have failed; never suppress broad failure.
    need(type(value['codebook_sha256']) is str and value['codebook_sha256'] == digest, 'DIAGNOSTIC_BINDING')
    need(type(value['status']) is str and value['status'] in ('SOURCE_BOUND', 'PARTIAL_SOURCE_BOUND', 'UNKNOWN') and
         type(value['stack']) is str and value['stack'] in ('PUBLIC_ONLY', 'FOREIGN_FILTERED', 'FRAME_LIMIT', 'UNKNOWN'), 'DIAGNOSTIC_ENUM')
    need(type(value['frames']) is list and len(value['frames']) <= FAILURE_FRAMES_MAX, 'DIAGNOSTIC_FRAME_BOUND')
    if value['status'] == 'UNKNOWN':
        need(value['stack'] in ('UNKNOWN', 'FOREIGN_FILTERED', 'FRAME_LIMIT') and
             value == unknown_failure_diagnostic(digest, value['stack']), 'DIAGNOSTIC_UNKNOWN')
        return
    need(value['frames'] and value['status'] == ('SOURCE_BOUND' if value['stack'] == 'PUBLIC_ONLY' else 'PARTIAL_SOURCE_BOUND')
         and value['stack'] != 'UNKNOWN' and
         (value['stack'] != 'FRAME_LIMIT' or len(value['frames']) == FAILURE_FRAMES_MAX), 'DIAGNOSTIC_STATUS')
    compiled = {}
    bundle = Path(__file__).resolve(strict=True).parent
    for frame in value['frames']:
        need(type(frame) is dict and set(frame) == {'role', 'function', 'line'} and
             type(frame['role']) is str and frame['role'] in FAILURE_ROLES and
             type(frame['function']) is str and type(frame['line']) is int and
             0 < frame['line'] <= FAILURE_LINE_MAX, 'DIAGNOSTIC_FRAME_SHAPE')
        row = next((entry for entry in book['functions'] if entry['role'] == frame['role'] and
                    entry['function'] == frame['function']), None)
        need(row is not None and row['first_line'] <= frame['line'] <= row['last_line'], 'DIAGNOSTIC_FRAME_SITE')
        if frame['role'] not in compiled:
            compiled[frame['role']] = failure_compiled_functions(sources[frame['role']], bundle / FAILURE_ROLES[frame['role']])
        code = compiled[frame['role']].get(frame['function'])
        need(code is not None and frame['line'] in {line for _, _, line in code.co_lines() if line is not None}, 'DIAGNOSTIC_EXECUTABLE_SITE')
    need(type(value['phase']) is str and value['phase'] == failure_phase(value['frames'], book), 'DIAGNOSTIC_PHASE')
    kind, refusal = value['exception_type'], value['refusal_code']
    need(type(kind) is str and kind in (*FAILURE_TYPE_NAMES, 'UNKNOWN') and type(refusal) is str, 'DIAGNOSTIC_EXCEPTION_ENUM')
    if kind in FAILURE_TYPE_NAMES[:4]:
        need(refusal == 'UNKNOWN' or refusal in {row['code'] for row in failure_refusal_sites(value['frames'], book, kind)}, 'DIAGNOSTIC_REFUSAL_SITE')
    else:
        need(refusal == ('UNKNOWN' if kind == 'UNKNOWN' else 'NOT_APPLICABLE'), 'DIAGNOSTIC_REFUSAL_ENUM')
    validate_path_guard(value['path_guard'], value, book)


def record_failure(work, args, exc):
    """Retain a closed failure even when crypto refused before PREPARATION existed."""
    binding = immutable_code_binding(work)
    preparation_sha256 = None
    if (work / 'PREPARATION.json').exists():
        prep_raw = regular(work / 'PREPARATION.json', MAX_PUBLIC)[0]
        prep = parse(prep_raw)
        identity = preparation_identity(prep)
        need(prep['code_manifest_sha256'] == binding['manifest_sha256'], 'FAILURE_CODE_CHANGED')
        preparation_sha256 = sha(prep_raw)
        context = 'PREPARATION'
        if args.action == 'prepare':
            need(identity == workflow_identity(args.run_id, args.attempt, args.commit), 'FAILURE_CONTEXT_CHANGED')
    else:
        need(args.action == 'prepare', 'FAILURE_CONTEXT_UNAVAILABLE')
        identity = workflow_identity(args.run_id, args.attempt, args.commit)
        context = 'WORKFLOW_ARGUMENTS'
    reason = 'ADAPTER_REFUSAL' if isinstance(exc, Refusal) else ('INTERRUPTED' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'UNEXPECTED_EXCEPTION')
    domain, role = 'ADAPTER', 'NOT_APPLICABLE'
    custody = sys.modules.get('warning_custody')
    closed = custody.closed_preflight_failure(exc) if custody is not None else None
    if closed is not None:
        domain, reason, role = 'CUSTODY_PREFLIGHT', closed['reason'], closed['module_role']
    reserved = (work / 'DISPATCH_RESERVED.json').exists()
    value = {'schema': 'dg18.c02.startup-adapter-failure.v4', 'stage': args.action,
        'failure_domain': domain, 'reason': reason, 'module_role': role, **identity,
        'code_manifest_sha256': binding['manifest_sha256'], 'preparation_sha256': preparation_sha256,
        'context': context, 'dispatch_reserved': reserved, 'native_reach': 'UNKNOWN' if reserved else 'NOT_DISPATCHED',
        'raw_evidence_published': False, 'original_acceptance': False, 'automatic_retry': False,
        'diagnostic': project_failure_diagnostic(exc, binding)}
    write_new(work / 'ADAPTER_FAILURE.json', validate_failure(value, identity, binding))


def validate_failure(value, identity, binding):
    keys = {'schema','stage','failure_domain','reason','module_role','run_id','run_attempt','workflow_commit',
            'code_manifest_sha256','preparation_sha256','context','dispatch_reserved','native_reach',
            'raw_evidence_published','original_acceptance','automatic_retry','diagnostic'}
    need(type(value) is dict and set(value) == keys and value['schema'] == 'dg18.c02.startup-adapter-failure.v4', 'ADAPTER_FAILURE_SCHEMA')
    need(all(type(value[k]) is type(v) and value[k] == v for k, v in identity.items())
         and value['code_manifest_sha256'] == binding['manifest_sha256'], 'ADAPTER_FAILURE_BINDING')
    need(value['stage'] in {'prepare','hold'} and type(value['dispatch_reserved']) is bool and
         value['native_reach'] == ('UNKNOWN' if value['dispatch_reserved'] else 'NOT_DISPATCHED') and
         all(value[k] is False for k in ('raw_evidence_published','original_acceptance','automatic_retry')), 'ADAPTER_FAILURE_SCOPE')
    if value['failure_domain'] == 'CUSTODY_PREFLIGHT':
        custody = sys.modules['warning_custody']
        need(type(value['reason']) is str and value['reason'] in custody.PREFLIGHT_CODES and
             type(value['module_role']) is str and value['module_role'] in custody.PREFLIGHT_ROLES, 'ADAPTER_FAILURE_CRYPTO_ENUM')
    else:
        need(value['failure_domain'] == 'ADAPTER' and value['reason'] in {'ADAPTER_REFUSAL','UNEXPECTED_EXCEPTION','INTERRUPTED'}
             and value['module_role'] == 'NOT_APPLICABLE', 'ADAPTER_FAILURE_ENUM')
    if value['context'] == 'WORKFLOW_ARGUMENTS':
        need(value['stage'] == 'prepare' and value['preparation_sha256'] is None, 'ADAPTER_FAILURE_CONTEXT')
    else:
        need(value['context'] == 'PREPARATION' and type(value['preparation_sha256']) is str and
             re.fullmatch('[0-9a-f]{64}', value['preparation_sha256']), 'ADAPTER_FAILURE_CONTEXT')
    validate_failure_diagnostic(value['diagnostic'], binding)
    raw = encode(value)
    need(len(raw) <= MAX_PUBLIC, 'ADAPTER_FAILURE_PUBLIC_BOUND')
    return raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare','hold','public-result','public-custody'])
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
        if args.action == 'public-custody':
            public_custody(work)
        else:
            public_result(work, args.run_id, args.attempt, args.commit)
        return 0
    except BaseException as exc:
        # Failure artifacts survive ordinary failures, independently of worker
        # exit status. Retain exact traceback privately, never in public logs.
        if args.action not in {'public-result', 'public-custody'}:
            try:
                import traceback
                private_dir(work)
                write_new(work / 'PRIVATE_FAILURE.txt', traceback.format_exc().encode())
                record_failure(work, args, exc)
            except BaseException:
                pass
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
