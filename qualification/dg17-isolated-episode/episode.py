#!/usr/bin/env python3
"""DG17-only hosted episode. No local execution route or original awards.

Maintained claim/activation/continuity owners supply all custody authority.
Command capture and child containment reuse the unchanged reviewed host utility.
"""
import argparse, ctypes, hashlib, json, os, platform, re, stat, sys, tarfile, time, types, urllib.request
from pathlib import Path

REPO = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg17-isolated-episode-01-20261106'
SOURCE = '0d57929be5bd15682b4e9da2c0209d5dff307843'
TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
PARENT = '481e529b691ed3d21169b07f376e357ae51f1f03'
MANIFEST_SHA = 'ed6a601d3a66997218195202cb5513363b5410b98489762324095a9030c261b4'
UTILITY_SHA = '429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'
PINS_SHA = 'ffbdea844b4e77e8ce7616712c0cda57a59995ab32efdf22f001fc41a61c5eaf'
CLAIM = 'skills/implementaudit/scripts/claim-run.sh'
AUTHOR = 'fixtures/controller-initialization/author_checkpoint.py'
DOCS = ('STATE.md', 'PROTOCOL.md', 'ROADMAP.md', 'THINKING.md', 'sidecars.md', 'tools.md', 'context.md', 'phases/phase-1.md')
STEPS = ('prepare', 'initialize', 'discover', 'invalidate', 'read-state', 'read-roadmap', 'resume', 'verify', 'require', 'predicates', 'runtime', 'catalogue', 'receive')
PUBLIC = ('RESULT.json', 'SOURCE.json', 'HOST.json', 'CURRENTNESS.json', 'PREDICATES.json', 'CATALOGUE.json', 'CLEANUP.json', 'FAILURE.json', 'ARTIFACT_MANIFEST.json')
PURPOSE = 'Qualify seven selected claim identity predicate methods and one offline Codex catalog and ordinary cleanup cycle against the frozen DG17 subject; retain actual results without original acceptance.'
NEXT = 'Run only the seven selected pure methods and the explicitly reviewed offline catalog cleanup cycle, receive bounded observations and preserve final source and live currentness evidence.'
ARCHIVE_URL = 'https://github.com/openai/codex/releases/download/rust-v0.167.0-alpha.4/codex-x86_64-unknown-linux-musl.tar.gz'
ARCHIVE_SHA = 'c4fd6fdeedf0ae78cc4d1d9dde4282c57a4a67c38319e3575b9a1e4d46c9ccc6'
ARCHIVE_BYTES = 123815356
BINARY_SHA = '57c94ea520df28beb76955316c5c48f672550fe42c6cff7003badb76e1ee10d8'
BINARY_BYTES = 324012616
EXPECTED_METHODS = {
    'test_windows_api_difference_preserves_both_mutation_checks',
    'test_unqualified_runtime_retains_strict_chain',
    'test_required_windows_metadata_refuses_missing_and_wrong_types',
    'test_qualified_windows_split_is_accepted_by_each_binder',
    'test_each_common_or_same_api_field_mutation_is_refused',
    'test_other_runtimes_keep_the_strict_chain',
    'test_missing_or_wrong_type_common_metadata_fails_closed',
}
PREDICATE_SCOPE = {
    'direct_source_applicability': ['T06', 'T08', 'Y04', 'BINDING_POSITIVE'],
    'component_only': ['T12'],
    'indirect_inherited_scope_only': ['NESTED/P01'],
    'narrow_receiving_input_only': ['T14'],
    'ceiling': 'SYNTHETIC_IDENTITY_PREDICATES_ONLY_NO_NATIVE_OR_ORIGINAL_AWARD',
}

class Refusal(Exception): pass
def need(test, code):
    if not test: raise Refusal(code)
def digest(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value): return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
def read(path, limit=1048576):
    path = Path(path); before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= limit, 'FILE_SHAPE')
    with path.open('rb') as stream: raw = stream.read(limit+1)
    after = path.lstat()
    need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) and len(raw) == before.st_size, 'FILE_CHANGED')
    return raw
def save(path, value):
    path = Path(path); tmp = path.with_name(path.name+'.next')
    with tmp.open('xb') as out: out.write(encoded(value)); out.flush(); os.fsync(out.fileno())
    os.chmod(tmp, 0o600); os.replace(tmp, path)
def stream_hash(path):
    h = hashlib.sha256(); size = 0
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''): size += len(chunk); h.update(chunk)
    return size, h.hexdigest()
def catalogue_schema_matches(value, schema):
    # The pinned result schema uses only this small, closed keyword set.
    allowed = {'$schema', 'title', 'type', 'additionalProperties', 'required', 'properties', 'const', 'enum', 'anyOf', 'minimum', 'maximum', 'maxItems', 'items', 'pattern'}
    need(type(schema) is dict and set(schema) <= allowed, 'CATALOGUE_SCHEMA_KEYWORD')
    if 'anyOf' in schema:
        need(set(schema) == {'anyOf'}, 'CATALOGUE_SCHEMA_COMBINATION')
        return any(catalogue_schema_matches(value, part) for part in schema['anyOf'])
    expected = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool, 'null': type(None)}
    if 'type' in schema:
        need(schema['type'] in expected, 'CATALOGUE_SCHEMA_TYPE')
        if type(value) is not expected[schema['type']]: return False
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']): return False
    if 'enum' in schema and not any(type(value) is type(item) and value == item for item in schema['enum']): return False
    if type(value) is dict:
        need(schema.get('additionalProperties') is False, 'CATALOGUE_SCHEMA_OBJECT_NOT_CLOSED')
        props = schema['properties']
        if not set(schema['required']) <= set(value) <= set(props): return False
        if not all(catalogue_schema_matches(item, props[key]) for key, item in value.items()): return False
    if type(value) is list:
        if 'maxItems' in schema and len(value) > schema['maxItems']: return False
        if 'items' in schema and not all(catalogue_schema_matches(item, schema['items']) for item in value): return False
    if 'minimum' in schema and (type(value) is not int or value < schema['minimum']): return False
    if 'maximum' in schema and (type(value) is not int or value > schema['maximum']): return False
    if 'pattern' in schema and (type(value) is not str or re.search(schema['pattern'], value) is None): return False
    return True
def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'CATALOGUE_DUPLICATE_KEY'); result[key] = value
    return result
def receive_catalogue(state, packet, raw):
    schema_raw = read(packet/'PUBLIC_RESULT_SCHEMA.json')
    state['catalogue_validation'] = {'valid': False, 'schema_sha256': digest(schema_raw), 'result_sha256': digest(raw), 'result_bytes': len(raw)}
    value = json.loads(raw, object_pairs_hook=unique_object)
    need(catalogue_schema_matches(value, json.loads(schema_raw)), 'CATALOGUE_RESULT_SCHEMA')
    state['catalogue'] = value; state['catalogue_validation']['valid'] = True
def catalogue_success(value, uid, gid):
    flags = ('source_identity_verified', 'runtime_identity_verified', 'runtime_reported_version_matches', 'native_process_started', 'currentness_before', 'currentness_after')
    if value.get('status') != 'OBSERVED_CATALOG_AND_PRESENT_CLEANUP' or not all(value.get(key) is True for key in flags): return False
    if value.get('source_commit') != SOURCE or value.get('source_tree') != TREE or value.get('runtime_sha256') != BINARY_SHA or value.get('runtime_bytes') != BINARY_BYTES or value.get('runtime_version') != '0.167.0-alpha.4': return False
    if value.get('failure') is not None or any(value.get(key) != 0 for key in ('unexpected_lifecycle_notification_count', 'unexpected_server_request_count', 'nonmetadata_outbound_count')): return False
    if value.get('calls') != [{'method': method, 'status': 'OBSERVED'} for method in ('initialize', 'plugin/read', 'skills/list', 'hooks/list')]: return False
    git = value.get('git_startup_admission') or {}
    if git.get('profile') != 'LINUX_STANDARD_GIT_EMPTY_OR_SAFE_DIRECTORY_V1' or not all(git.get(key) is True for key in ('before_passed', 'after_passed', 'identities_unchanged', 'global_config_paths_absent', 'source_store_owned_physical', 'source_common_dir_matches', 'source_redirections_absent')): return False
    counts = {'ABSENT': 0, 'EMPTY': 0, 'SAFE_DIRECTORY_WILDCARD': 1}
    if git.get('system_config_state') not in counts or git.get('system_config_entries') != counts[git['system_config_state']] or git.get('includes_expanded') is not False or git.get('selected_helper_count') != 3 or not git.get('before_identity_sha256') or git.get('before_identity_sha256') != git.get('after_identity_sha256'): return False
    if git['system_config_state'] == 'ABSENT':
        if git.get('system_config_bytes') != 0 or git.get('system_config_sha256') is not None: return False
    elif not git.get('system_config_sha256') or (git['system_config_state'] == 'SAFE_DIRECTORY_WILDCARD' and git.get('system_config_bytes', 0) <= 0): return False
    if git.get('source_config_profile') != 'OWNED_CHECKOUT_CORE_ORIGIN_V1' or git.get('source_git_config_entries') not in (6, 7) or git.get('source_active_hook_count') != 0: return False
    offline = value.get('offline') or {}
    if offline.get('uid') != uid or offline.get('gid') != gid or offline.get('external_routes') != 0 or not all(offline.get(key) is True for key in ('verified', 'namespace_differs_from_parent', 'only_loopback', 'effective_permitted_ambient_capabilities_zero', 'no_new_privileges')): return False
    catalog = value.get('catalog') or {}; skills = catalog.get('skills', [])
    names = {'implementaudit', 'audit-state', 'audit-assess', 'audit-implement', 'audit-andon'}
    if catalog.get('source_matches') is not True or catalog.get('five_exact_skill_paths') is not True or len(skills) != 5 or {row['name'] for row in skills} != names or catalog.get('other_skill_count') != 0: return False
    if not all(row['path'] == 'skills/'+row['name']+'/SKILL.md' and row['path_matches_frozen_source'] is True for row in skills): return False
    if value.get('configured_skills') is None or value.get('configured_hooks') is None: return False
    cleanup = value.get('cleanup') or {}
    if not all(cleanup.get(key) is True for key in ('close_returned', 'reader_joined', 'private_seal_unchanged')) or cleanup.get('parent_returncode') != 0 or cleanup.get('transport_remaining_owned_count') != 0 or cleanup.get('close_error_type') is not None or cleanup.get('containment') is not None: return False
    for key in ('after_close', 'after_seal'):
        snap = cleanup.get(key) or {}
        if snap.get('full_session_scope_available') is not True or snap.get('launch_directory_empty') is not True or any(snap.get(field) != 0 for field in ('living_owned_processes', 'owned_zombies', 'uncertain_owned_candidates')): return False
    return True
def receive_private_seal(state, output):
    root = output/'private/native-catalogue'; path = root/'PRIVATE_EVIDENCE_SEAL.json'; raw = read(path)
    need(digest(raw) == state['catalogue']['private_evidence_seal_sha256'], 'CATALOGUE_PRIVATE_SEAL_BINDING')
    declared = json.loads(raw); need(set(declared) == {'schema', 'files'} and declared['schema'] == 'dg17.t12.private-byte-seal.v1', 'CATALOGUE_PRIVATE_SEAL_SHAPE')
    observed = []
    for item in sorted(root.rglob('*')):
        if item == path: continue
        info = item.lstat()
        if stat.S_ISREG(info.st_mode):
            size, sha = stream_hash(item); after = item.lstat()
            need((info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'CATALOGUE_PRIVATE_MEMBER_CHANGED')
            observed.append({'path': item.relative_to(root).as_posix(), 'bytes': size, 'sha256': sha})
        elif not stat.S_ISDIR(info.st_mode): observed.append({'path': item.relative_to(root).as_posix(), 'kind': 'NONREGULAR'})
    need(observed == declared['files'] and read(path) == raw, 'CATALOGUE_PRIVATE_SEAL_READBACK')
    state['catalogue_validation']['private_seal_verified_after_child_reaping'] = True
    state['catalogue_validation']['private_member_count'] = len(observed)
    for name in ('gate-before.stdout', 'gate-after.stdout'):
        need(read(root/name) == (state['receipt']+'\n').encode(), 'CATALOGUE_EXACT_RECEIPT_BINDING')
    state['catalogue_validation']['same_receipt_private_readbacks_verified'] = True
def utility(packet):
    raw = read(packet/'host_utility.py'); need(digest(raw) == UTILITY_SHA, 'UTILITY_PIN')
    module = types.ModuleType('dg17_retained_host_utility'); module.__file__ = str(packet/'host_utility.py')
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module
def packet_check(packet):
    raw = read(packet/'INPUT_PINS.json'); need(digest(raw) == PINS_SHA, 'PACKET_UNSEALED_OR_CHANGED')
    pins = json.loads(raw)
    for name, row in pins.items():
        need(re.fullmatch(r'[A-Za-z0-9_.-]+', name) is not None, 'INPUT_PATH')
        content = read(packet/name)
        need(len(content) == row['bytes'] and digest(content) == row['sha256'], 'INPUT_PIN')
    return pins
def source_check(source, packet):
    raw = read(packet/'SOURCE_MANIFEST.json'); need(digest(raw) == MANIFEST_SHA, 'MANIFEST_PIN')
    manifest = json.loads(raw); need(manifest['expected_tree'] == TREE and manifest['file_count'] == 1755 and manifest['total_bytes'] == 165855954, 'MANIFEST_SUBJECT')
    members = manifest['members']; seen = set(); total = 0
    for row in members:
        path = source/row['path']; info = path.lstat()
        need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and stat.S_IMODE(info.st_mode) == (0o755 if row['mode'] == '100755' else 0o644), 'SOURCE_FILE_SHAPE')
        size, sha = stream_hash(path)
        need(size == row['bytes'] and sha == row['sha256'], 'SOURCE_BYTES')
        seen.add(row['path']); total += size
    need(len(seen) == 1755 and total == 165855954, 'SOURCE_POPULATION')
    observed = set()
    for parent, dirs, files in os.walk(source, followlinks=False):
        here = Path(parent)
        for name in list(dirs):
            path = here/name; need(not path.is_symlink(), 'SOURCE_DIRECTORY_ALIAS')
            if here == source and name in ('.git', '.IMPLEMENTAUDIT'): dirs.remove(name)
        for name in files: observed.add((here/name).relative_to(source).as_posix())
    need(observed == seen, 'SOURCE_EXTRA_OR_MISSING_MEMBER')
    return {'commit': SOURCE, 'tree': TREE, 'parent': PARENT, 'files': len(seen), 'bytes': total, 'all_manifest_members_match': True}
def canonical_hashes(source, state):
    return {name: digest(read(source/state['run_root']/name)) for name in DOCS}
def command(state, output, u, label, argv, seconds=60):
    env_args = ['/usr/bin/env', 'HOME='+str(output/'home'), 'CODEX_HOME='+str(output/'home/codex'), 'TMPDIR='+str(output/'tmp')]
    state['active_command'] = label; save(output/'private/episode.json', state)
    try:
        try:
            rc, stdout, stderr = u.capture(label, env_args+argv, state['commands'], time.monotonic()+seconds+5, seconds=seconds)
        except BaseException as exc:
            captured = getattr(exc, 'captured', None)
            if captured is not None:
                for suffix in ('stdout', 'stderr'):
                    raw = captured[suffix]; need(type(raw) is bytes and len(raw) <= 32768, 'FAILURE_CAPTURE_SHAPE')
                    with (output/'private'/f'{len(state["commands"]):03d}-{label}.{suffix}').open('xb') as f: f.write(raw)
            raise
        for suffix, raw in (('stdout', stdout), ('stderr', stderr)):
            with (output/'private'/f'{len(state["commands"]):03d}-{label}.{suffix}').open('xb') as f: f.write(raw)
        state['active_command'] = None
        need(rc == 0, 'COMMAND_NONZERO_'+label)
        return stdout
    finally:
        save(output/'private/episode.json', state)
def owner(state, source, output, u, label, *args):
    need(Path.cwd() == source, 'OWNER_CWD')
    return command(state, output, u, label, ['/usr/bin/bash', str(source/CLAIM), *args])
def current(state, source, output, u, label):
    need(state.get('receipt') is not None, 'CURRENTNESS_NOT_ESTABLISHED')
    raw = owner(state, source, output, u, label, '--require-current-continuity', state['controller'])
    need(raw == (state['receipt']+'\n').encode(), 'CURRENTNESS_RECEIPT_DIFFERS')
    state['currentness'].append({'role': label, 'receipt_sha256': digest(raw), 'same_source_cwd': True, 'verified': True})
    save(output/'private/episode.json', state)
def acquire_runtime(output):
    archive = output/'private/codex.tar.gz'; started = time.monotonic(); count = 0; h = hashlib.sha256()
    with urllib.request.urlopen(ARCHIVE_URL, timeout=30) as response, archive.open('xb') as f:
        while True:
            chunk = response.read(1048576)
            if not chunk: break
            count += len(chunk); need(count <= ARCHIVE_BYTES and time.monotonic()-started < 180, 'ARCHIVE_BOUND')
            h.update(chunk); f.write(chunk)
    need(count == ARCHIVE_BYTES and h.hexdigest() == ARCHIVE_SHA, 'ARCHIVE_PIN')
    binary = output/'private/codex-input'
    with tarfile.open(archive, 'r:gz') as tar:
        members = tar.getmembers()
        need(len(members) == 1 and members[0].isreg() and members[0].name == 'codex-x86_64-unknown-linux-musl' and members[0].size == BINARY_BYTES, 'ARCHIVE_MEMBERS')
        with tar.extractfile(members[0]) as inp, binary.open('xb') as out:
            while True:
                chunk = inp.read(1048576)
                if not chunk: break
                out.write(chunk)
    need(stream_hash(binary) == (BINARY_BYTES, BINARY_SHA), 'BINARY_PIN')
    os.chmod(binary, 0o700)
    return {'archive_sha256': ARCHIVE_SHA, 'archive_bytes': ARCHIVE_BYTES, 'binary_sha256': BINARY_SHA, 'binary_bytes': BINARY_BYTES, 'version_subject': 'codex-cli 0.167.0-alpha.4', 'input_retained_until_host_teardown': True}
def execute(step, state, source, output, packet, u):
    if step == 'prepare':
        need(os.getuid() == os.geteuid() > 0 and os.getgid() == os.getegid() > 0, 'ORDINARY_RUNNER_IDENTITY')
        need(not source.exists(), 'SOURCE_NOT_FRESH')
        for label, args in [('git-init', ['init', '--quiet', '--initial-branch=dg17-bootstrap', str(source)]), ('git-remote', ['-C', str(source), 'remote', 'add', 'origin', 'https://github.com/'+REPO+'.git']), ('git-fetch', ['-c', 'protocol.https.allow=always', '-C', str(source), 'fetch', '--quiet', '--depth=2', '--no-tags', 'origin', SOURCE]), ('git-checkout', ['-C', str(source), 'checkout', '--quiet', '--detach', SOURCE])]:
            command(state, output, u, label, ['/usr/bin/git', *args], seconds=180)
        os.chdir(source)
        head = command(state, output, u, 'head-identity', ['/usr/bin/git', 'rev-parse', 'HEAD', 'HEAD^{tree}'])
        need(head.decode().splitlines() == [SOURCE, TREE], 'HEAD_TREE')
        body = command(state, output, u, 'head-parent', ['/usr/bin/git', 'cat-file', '-p', 'HEAD'])
        need(body.split(b'\n\n', 1)[0].splitlines()[:2] == [('tree '+TREE).encode(), ('parent '+PARENT).encode()], 'PARENT')
        need(command(state, output, u, 'fresh-controller-refs', ['/usr/bin/git', 'for-each-ref', '--format=%(refname)', 'refs/implementaudit']) == b'', 'IMPORTED_CONTROLLER_REFS')
        need(not command(state, output, u, 'fresh-source-clean', ['/usr/bin/git', 'status', '--porcelain=v1', '--untracked-files=all']), 'SOURCE_DIRTY')
        tools = {}
        for name in ('python3', 'git', 'bash', 'env', 'unshare', 'setpriv'):
            path, observed = u.trusted(name); need(path is not None, 'HOST_TOOL_'+name); tools[name] = observed
        sudo = Path('/usr/bin/sudo').resolve(strict=True)
        for path in (sudo, *sudo.parents):
            info = path.lstat(); need(info.st_uid == 0 and not info.st_mode & 0o022, 'SUDO_ANCESTRY')
        need(stat.S_IMODE(sudo.stat().st_mode) == 0o4755, 'SUDO_EXPECTED_SETUID_MODE')
        size, sha = stream_hash(sudo)
        tools['sudo'] = {'canonical': str(sudo), 'bytes': size, 'sha256': sha, 'root_owned_nonwritable_chain': True, 'mode': '04755', 'admitted_effect': 'ONE_NEW_NETWORK_NAMESPACE_THEN_DROP_TO_ACTUAL_RUNNER_UID_AND_GID_WITH_NO_NEW_PRIVILEGES'}
        state['host'] = {'platform': platform.system(), 'kernel': platform.release(), 'python': list(sys.version_info[:3]), 'uid': os.getuid(), 'gid': os.getgid(), 'tools': tools, 'provider_calls': 0}
        state['source_before'] = source_check(source, packet)
    elif step == 'initialize':
        raw = owner(state, source, output, u, 'fresh-claim', '--controller', state['controller'], 'dg17-isolated-native')
        run = raw.decode('ascii').strip(); need(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/dg17-isolated-native-[A-Za-z0-9]{6}', run), 'RUN_ROOT')
        state['run_root'] = run; save(output/'private/episode.json', state)
        authored = json.loads(command(state, output, u, 'author-task', ['/usr/bin/python3', '-I', '-S', '-B', str(source/AUTHOR), '--repo', str(source), '--run-root', run, '--source', str(source), '--purpose', PURPOSE, '--next-action', NEXT]))
        need(set(authored) == set(DOCS) and authored == canonical_hashes(source, state), 'AUTHOR_READBACK')
        inspected = json.loads(owner(state, source, output, u, 'inspect-initialization', '--inspect-controller-initialization', state['controller'], '--run-root', run))
        init = inspected['initialization_token']; need(re.fullmatch('refs/implementaudit/controller-initializations/'+state['controller']+r'/[0-9a-f]{32}@[0-9a-f]{40}', init), 'PREPARATION_TOKEN')
        activated = json.loads(owner(state, source, output, u, 'activate-initialization', '--activate-controller', state['controller'], '--run-root', run, '--expected-initialization', init))
        need(activated.get('status') == 'BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS' and activated.get('authority_ceiling') == 'ELIGIBLE_FOR_NORMAL_CURRENTNESS_ONLY', 'ACTIVATION')
        state['canonical_before'] = canonical_hashes(source, state)
    elif step == 'discover':
        parts = owner(state, source, output, u, 'discover', '--current-controller', state['controller']).decode().strip().split('\t')
        need(len(parts) == 4 and parts[0] == state['controller'] and Path(parts[1]) == source and Path(parts[2]) == source/state['run_root'], 'DISCOVERY')
    elif step == 'invalidate':
        owner(state, source, output, u, 'invalidate', '--invalidate-continuity', state['controller'], '--boundary', 'new-session', '--event', 'dg17-hosted-'+state['context']['run_id']+'-attempt-1')
    elif step in ('read-state', 'read-roadmap'):
        name = 'STATE.md' if step == 'read-state' else 'ROADMAP.md'; raw = read(source/state['run_root']/name)
        with (output/'private'/(step+'.read')).open('xb') as f: f.write(raw)
        state['reads'][name] = {'sha256': digest(raw), 'completed_host_action_ordinal': len(state['completed'])+1}
    elif step == 'resume':
        need(set(state['reads']) == {'STATE.md', 'ROADMAP.md'} and state['reads']['STATE.md']['completed_host_action_ordinal'] < state['reads']['ROADMAP.md']['completed_host_action_ordinal'], 'SEPARATE_READS')
        for name, row in state['reads'].items(): need(digest(read(source/state['run_root']/name)) == row['sha256'], 'READ_CHANGED')
        raw = owner(state, source, output, u, 'resume', '--resume-controller', state['controller'], '--boundary', 'new-session', '--epoch', 'G0001')
        receipt = raw.decode().strip(); need(re.fullmatch('refs/implementaudit/continuity-receipts/'+state['controller']+r'/G0001@[0-9a-f]{40}', receipt), 'RECEIPT')
        state['receipt'] = receipt
    elif step == 'verify':
        need(owner(state, source, output, u, 'verify', '--verify-resume-receipt', state['receipt']) == (state['receipt']+'\n').encode(), 'VERIFY')
    elif step == 'require': current(state, source, output, u, 'initial-currentness')
    elif step == 'predicates':
        current(state, source, output, u, 'before-predicates')
        start = len(state['commands']); failure = None
        try:
            command(state, output, u, 'seven-portable-methods', ['/usr/bin/python3', '-I', '-B', str(source/'tests/shell_companion_source_custody.py'), 'CompanionIdentityPredicate', 'CompanionLoadIdentityPredicate', '-v'])
        except BaseException as exc: failure = exc
        capture = state['commands'][start] if len(state['commands']) > start else None
        stderr_path = output/'private'/f'{start+1:03d}-seven-portable-methods.stderr'
        stderr = read(stderr_path, 32768).decode('utf-8') if stderr_path.exists() else ''
        rows = re.findall(r'^(test_[a-zA-Z0-9_]+) \(([^\n]+)\) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$', stderr, re.MULTILINE)
        passed = failure is None and len(rows) == 7 and {r[0] for r in rows} == EXPECTED_METHODS and all(r[2] == 'ok' for r in rows) and bool(re.search(r'Ran 7 tests in [0-9.]+s\s+OK\s*$', stderr))
        state['predicates'] = {'status': 'PASS_SEVEN_PORTABLE_METHODS' if passed else 'FAILED_OR_PARTIAL', 'methods': [{'method': x[0], 'identity': x[1], 'status': x[2]} for x in rows], 'test_source_sha256': digest(read(source/'tests/shell_companion_source_custody.py')), 'command': capture, 'source_applicability': PREDICATE_SCOPE, 'live_mechanical_receiving_complete': False, 'native_windows_qualification': False, 'new_original_awards': []}
        if failure is not None: raise failure
        need(passed, 'SEVEN_METHOD_RESULT')
        current(state, source, output, u, 'after-predicates')
        state['predicates']['live_mechanical_receiving_complete'] = True
    elif step == 'runtime':
        current(state, source, output, u, 'before-runtime-acquisition'); state['runtime'] = acquire_runtime(output)
        version = command(state, output, u, 'codex-version', [str(output/'private/codex-input'), '--version']).decode().strip()
        need(version == 'codex-cli 0.167.0-alpha.4', 'CODEX_VERSION'); state['runtime']['observed_version'] = version
        current(state, source, output, u, 'after-runtime-acquisition')
    elif step == 'catalogue':
        current(state, source, output, u, 'before-catalogue')
        netns = os.readlink('/proc/self/ns/net')
        try:
            command(state, output, u, 'offline-native-catalogue', ['/usr/bin/sudo', '-n', '/usr/bin/unshare', '--net', '--', '/usr/bin/setpriv', '--reuid', str(os.getuid()), '--regid', str(os.getgid()), '--clear-groups', '--no-new-privs', '/usr/bin/python3', '-I', '-S', '-B', str(packet/'catalogue_probe.py'), '--source', str(source), '--episode', str(output), '--binary', str(output/'private/codex-input'), '--controller', state['controller'], '--receipt', state['receipt'], '--expected-uid', str(os.getuid()), '--expected-gid', str(os.getgid()), '--parent-netns', netns], seconds=180)
        finally:
            if (output/'private/CATALOGUE_RESULT.json').exists():
                receive_catalogue(state, packet, read(output/'private/CATALOGUE_RESULT.json', 65536))
                record = state['commands'][-1]
                state['catalogue_validation']['captured_result_matches'] = False
                if record.get('name') == 'offline-native-catalogue' and record.get('streams_complete') is True:
                    captured = json.loads(read(output/'private'/f'{len(state["commands"]):03d}-offline-native-catalogue.stdout', 32768), object_pairs_hook=unique_object)
                    need(catalogue_schema_matches(captured, json.loads(read(packet/'PUBLIC_RESULT_SCHEMA.json'))) and captured == state['catalogue'], 'CATALOGUE_CAPTURE_DIFFERS')
                    state['catalogue_validation']['captured_result_matches'] = True
        current(state, source, output, u, 'after-catalogue')
    elif step == 'receive':
        current(state, source, output, u, 'before-receiving')
        need(state.get('predicates', {}).get('status') == 'PASS_SEVEN_PORTABLE_METHODS', 'PREDICATES_NOT_RECEIVED')
        need(state.get('catalogue_validation', {}).get('valid') is True and state['catalogue_validation'].get('captured_result_matches') is True and catalogue_success(state.get('catalogue', {}), os.getuid(), os.getgid()), 'CATALOGUE_NOT_RECEIVED')
        git = state['catalogue']['git_startup_admission']; admitted = state['host']['tools']['git']
        need(git['git_sha256'] == admitted['sha256'] and git['git_bytes'] == admitted['bytes'], 'CATALOGUE_GIT_BINDING')
        need(stream_hash(output/'private/codex-input') == (BINARY_BYTES, BINARY_SHA), 'RECEIVED_RUNTIME_CHANGED')
        receive_private_seal(state, output)
        state['catalogue_validation']['semantic_receiving_passed'] = True
        state['source_after'] = source_check(source, packet)
        need(state['source_after'] == state['source_before'] and canonical_hashes(source, state) == state['canonical_before'], 'FINAL_SOURCE_OR_STATE_DRIFT')
        current(state, source, output, u, 'after-receiving')
        state['bounded_receiving_complete'] = True
    else: raise Refusal('UNKNOWN_STEP')

def export(state, output, packet):
    if 'catalogue' in state:
        try:
            need(catalogue_schema_matches(state['catalogue'], json.loads(read(packet/'PUBLIC_RESULT_SCHEMA.json'))), 'CATALOGUE_EXPORT_SCHEMA')
        except BaseException as exc:
            state.pop('catalogue', None); state['failed'] = True; state['bounded_receiving_complete'] = False
            state['failures'].append({'step': 'export', 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode()), 'message_bytes': len(str(exc).encode())})
    docs = {
        'RESULT.json': {'schema': 'dg17.isolated-hosted-result.v1', 'context': state['context'], 'completed': state['completed'], 'failed': state['failed'], 'bounded_receiving_complete': state.get('bounded_receiving_complete', False), 'catalogue_validation': state.get('catalogue_validation'), 'local_currentness_transfer': False, 'original_acceptance': False, 'whole_T12': False, 'whole_T14': False, 'new_original_awards': []},
        'SOURCE.json': {'before': state.get('source_before'), 'after': state.get('source_after'), 'canonical_unchanged': state.get('canonical_unchanged')},
        'HOST.json': {'host': state.get('host'), 'runtime': state.get('runtime')},
        'CURRENTNESS.json': {'checks': state['currentness'], 'reads': state['reads'], 'local_or_future_transfer': False},
        'PREDICATES.json': state.get('predicates', {'status': 'NOT_COMPLETED'}),
        'CATALOGUE.json': state.get('catalogue', {'status': 'NOT_COMPLETED'}),
        'CLEANUP.json': {'commands': state['commands'], 'active_step': state.get('active_step'), 'active_command': state.get('active_command'), 'all_recorded_commands_reaped': all(x.get('cleanup', {}).get('echild') is True for x in state['commands']), 'private_roots_retained_until_disposable_host_teardown': True},
        'FAILURE.json': {'failures': state['failures']}}
    files = {name: encoded(value) for name, value in docs.items()}; need(all(len(raw) <= 65536 for raw in files.values()) and sum(map(len, files.values())) <= 262144, 'PUBLIC_BOUND')
    files['ARTIFACT_MANIFEST.json'] = encoded({'schema': 'dg17.public-artifact-manifest.v1', 'members': [{'name': name, 'bytes': len(raw), 'sha256': digest(raw)} for name, raw in sorted(files.items())]})
    public = output/'public'; public.mkdir(exist_ok=True)
    for name, raw in files.items():
        with (public/name).open('xb') as f: f.write(raw)
    print(json.dumps({'status': 'FAILED_RETAINED' if state['failed'] else 'BOUNDED_OBSERVATIONS_RETAINED', 'completed_steps': len(state['completed']), 'original_acceptance': False}))

def main():
    p = argparse.ArgumentParser(); p.add_argument('--step', choices=(*STEPS, 'finalize'), required=True); p.add_argument('--output', required=True); p.add_argument('--source', required=True); a = p.parse_args()
    packet = Path(__file__).absolute().parent; output = Path(a.output).absolute(); source = Path(a.source).absolute(); env = os.environ
    need(env.get('GITHUB_ACTIONS') == 'true' and env.get('RUNNER_ENVIRONMENT') == 'github-hosted' and env.get('GITHUB_REPOSITORY') == REPO and env.get('GITHUB_REF') == 'refs/heads/'+BRANCH and env.get('GITHUB_EVENT_NAME') == 'push' and env.get('GITHUB_RUN_ATTEMPT') == '1', 'ACTUAL_HOSTED_EVENT_REQUIRED')
    run_id = env['GITHUB_RUN_ID']; need(re.fullmatch(r'[0-9]{1,20}', run_id), 'RUN_ID')
    need(re.fullmatch(r'[0-9a-f]{40}', env.get('GITHUB_SHA', '')), 'WORKFLOW_COMMIT')
    need(output == Path(env['RUNNER_TEMP'])/('dg17-episode-'+run_id+'-1') and source == Path(env['GITHUB_WORKSPACE'])/'dg17-qualified-source', 'OWNED_PATHS')
    packet_check(packet); u = utility(packet)
    lib = ctypes.CDLL(None, use_errno=True); need(lib.prctl(36, 1, 0, 0, 0) == 0, 'SUBREAPER')
    if a.step == 'prepare':
        output.mkdir(mode=0o700)
        for name in ('private', 'home', 'tmp'): (output/name).mkdir(mode=0o700)
        state = {'context': {'repository': REPO, 'branch': BRANCH, 'run_id': run_id, 'attempt': 1, 'workflow_commit': env['GITHUB_SHA']}, 'controller': 'dg17-hosted-'+run_id+'-a1', 'run_root': None, 'receipt': None, 'completed': [], 'commands': [], 'currentness': [], 'reads': {}, 'failed': False, 'failures': [], 'active_step': None, 'active_command': None}
    else:
        state = json.loads(read(output/'private/episode.json'))
        need(state['context']['run_id'] == run_id and state['context']['workflow_commit'] == env['GITHUB_SHA'], 'EPISODE_IDENTITY')
    if source.exists(): os.chdir(source)
    if a.step == 'finalize':
        if state.get('active_step') is not None or state.get('active_command') is not None or state['completed'] != list(STEPS) or not state.get('receipt') or not all(row.get('cleanup', {}).get('echild') is True for row in state['commands']) or state.get('bounded_receiving_complete') is not True:
            state['failed'] = True
            state['bounded_receiving_complete'] = False
            code = 'UNCERTAIN_PREDECESSOR' if state.get('active_step') is not None or state.get('active_command') is not None else 'INCOMPLETE_EPISODE'
            state['failures'].append({'step': 'finalize', 'exception_type': 'Refusal', 'message_sha256': digest(code.encode()), 'message_bytes': len(code)})
        if state.get('receipt') and state.get('active_step') is None and state.get('active_command') is None and all(x.get('cleanup', {}).get('echild') is True for x in state['commands']):
            try:
                current(state, source, output, u, 'final-currentness')
                state['canonical_unchanged'] = canonical_hashes(source, state) == state['canonical_before']
                state['source_after'] = source_check(source, packet)
                need(state['canonical_unchanged'] and state['source_after'] == state['source_before'], 'FINAL_SOURCE_OR_STATE_DRIFT')
                if state.get('bounded_receiving_complete') is True:
                    need(digest(read(output/'private/CATALOGUE_RESULT.json', 65536)) == state['catalogue_validation']['result_sha256'] and catalogue_success(state['catalogue'], os.getuid(), os.getgid()), 'FINAL_CATALOGUE_RESULT_DRIFT')
                    receive_private_seal(state, output)
                    state['catalogue_validation']['final_private_seal_verified'] = True
            except BaseException as exc:
                state['failed'] = True; state['bounded_receiving_complete'] = False; state['failures'].append({'step': 'finalize', 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode()), 'message_bytes': len(str(exc).encode())})
        export(state, output, packet); save(output/'private/episode.json', state); return 1 if state['failed'] else 0
    need(not state['failed'] and state['active_step'] is None and state['active_command'] is None and state['completed'] == list(STEPS[:STEPS.index(a.step)]), 'STEP_SEQUENCE_OR_UNCERTAIN_PREDECESSOR')
    state['active_step'] = a.step; save(output/'private/episode.json', state)
    try:
        execute(a.step, state, source, output, packet, u)
        state['completed'].append(a.step); state['active_step'] = None
    except BaseException as exc:
        state['failed'] = True
        state['failures'].append({'step': a.step, 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode()), 'message_bytes': len(str(exc).encode())})
        if state['active_command'] is None: state['active_step'] = None
    finally: save(output/'private/episode.json', state)
    print(json.dumps({'step': a.step, 'complete': a.step in state['completed'], 'failed': state['failed']}))
    return 1 if state['failed'] else 0

if __name__ == '__main__':
    try: sys.exit(main())
    except BaseException as exc:
        if isinstance(exc, SystemExit): raise
        print(json.dumps({'status': 'BOOTSTRAP_REFUSED', 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode())})); sys.exit(1)
