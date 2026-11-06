#!/usr/bin/python3
"""Prepare by default; execute one exact, reviewed fresh C02 plus native tail only after root GO.

No historical Subject constructor is imported or invoked. Default preparation
reads and hashes pinned inputs and parses source; it never imports an owner,
checks the prospective subject, opens a socket, extracts Codex or launches it.
"""
from __future__ import annotations
import argparse
import ast
import contextlib
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import resource
import signal
import stat
import subprocess
import sys
import tarfile
import time
import traceback

sys.dont_write_bytecode = True
BASE = Path('/UNBOUND_C02_06_PARENT')
LANE = Path('/UNBOUND_C02_06_PACKET')
SOURCE = Path('/UNBOUND_PUBLIC_SOURCE_CHECKOUT')
INPUT_PATH = LANE / 'INPUT_MANIFEST.json'
INPUT_SHA256 = 'UNBOUND_PENDING_HOST_PREPARATION'
SOURCE_HEAD = '35bf9823856eb4efe254b882954120480632230e'
SOURCE_TREE = 'abe08aabc83de3b27c43e6acf28646fb089f0f34'
SUBJECT = Path('/tmp/dg18-isolated-c02-20261106-01')
CONTROLLER = 'dg18-isolated-c02-20261106-01'
OWNED_BINARY = Path('/tmp/dg18-isolated-c02-bin-20261106-01/codex')
OUTPUT = LANE / 'operation'
ENV = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'LANG': 'C', 'TZ': 'UTC',
       'IMPLEMENTAUDIT_PYTHON': '/usr/bin/python3', 'PYTHONDONTWRITEBYTECODE': '1',
       'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null',
       'GIT_CONFIG_SYSTEM': '/dev/null', 'GIT_OPTIONAL_LOCKS': '0', 'GIT_TERMINAL_PROMPT': '0'}
STALE = 'current generation is stale after a newer boundary'
MISSING_FRESH = 'C02 fresh-transition grant is missing, revoked, or outside exact scope/code/applicability'
WITHDRAWN = 'C02_LIVE_INTERVAL_UNAVAILABLE'


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def decode(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def stamp(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def physical(path):
    path = Path(path)
    require(path.is_absolute(), 'NON_ABSOLUTE_INPUT')
    for component in (path, *path.parents):
        st = component.lstat()
        require(not stat.S_ISLNK(st.st_mode), 'SYMLINK_INPUT')
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'NONREGULAR_OR_SHARED_INPUT')
    return info


def read_regular(path, maximum=4 * 1024 * 1024):
    path = Path(path)
    before = physical(path)
    require(before.st_size <= maximum, 'INPUT_BYTE_BOUND')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        raw = stream.read(maximum + 1)
        opened = os.fstat(stream.fileno())
    after = physical(path)
    require(len(raw) <= maximum and stamp(before) == stamp(opened) == stamp(after), 'INPUT_CHANGED_DURING_READ')
    return raw, stamp(after)


def streamed_pin(path):
    path = Path(path)
    before = physical(path)
    digest = hashlib.sha256()
    size = 0
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        while block := stream.read(1024 * 1024):
            size += len(block)
            digest.update(block)
        opened = os.fstat(stream.fileno())
    require(stamp(before) == stamp(opened) == stamp(physical(path)) and size == before.st_size,
            'STREAMED_INPUT_CHANGED')
    return {'path': str(path), 'bytes': size, 'sha256': digest.hexdigest()}, stamp(before)


def verify_inputs(*, full=True, original_identities=None):
    raw, _ = read_regular(INPUT_PATH)
    require(sha(raw) == INPUT_SHA256, 'INPUT_MANIFEST_CHANGED')
    manifest = decode(raw)
    require(manifest['source_root'] == str(SOURCE) and manifest['source_commit'] == SOURCE_HEAD
            and manifest['source_tree'] == SOURCE_TREE and manifest['prospective_subject'] == str(SUBJECT)
            and manifest['prospective_controller'] == CONTROLLER, 'INPUT_MANIFEST_SCOPE')
    payload, identities, seen, destinations = {}, {}, set(), set()
    for item in manifest['members']:
        require(item['key'] not in payload and item['path'] not in seen, 'DUPLICATE_INPUT')
        seen.add(item['path'])
        if 'destination' in item:
            require(item['destination'] not in destinations and not Path(item['destination']).is_absolute()
                    and '..' not in Path(item['destination']).parts, 'DUPLICATE_OR_UNSAFE_DESTINATION')
            destinations.add(item['destination'])
        if item['category'] in ('official-binary-archive', 'system-runtime'):
            if full:
                actual, identity = streamed_pin(item['path'])
                require(actual['bytes'] == item['bytes'] and actual['sha256'] == item['sha256'], 'LARGE_INPUT_CHANGED_' + item['key'])
            else:
                identity = stamp(physical(item['path']))
                require(original_identities is not None and identity == tuple(original_identities[item['key']]), 'LARGE_INPUT_CUSTODY_CHANGED')
            payload[item['key']] = None
        else:
            content, identity = read_regular(item['path'])
            require(len(content) == item['bytes'] and sha(content) == item['sha256'], 'INPUT_CHANGED_' + item['key'])
            payload[item['key']] = content
        require(stat.S_IMODE(identity[2]) == item['mode'], 'INPUT_MODE_CHANGED_' + item['key'])
        if item['category'] == 'system-runtime':
            require(str(Path(item['invocation']).resolve(strict=True)) == item['path'], 'SYSTEM_EXECUTABLE_SYMLINK_CHANGED')
        identities[item['key']] = identity
    return manifest, payload, identities, raw


def write(path, value, *, replace=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if isinstance(value, bytes) else canonical(value) + b'\n'
    with path.open('wb' if replace else 'xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


DIAGNOSTIC_SCHEMA = 'dg18.c02.diagnostics.v2'
DIAGNOSTIC_BYTES = 2048
DIAGNOSTIC_SEND_STAGES = ('BEFORE_SEND', 'RECORD', 'WRITE', 'FLUSH')
DIAGNOSTIC_NATIVE_FIELDS = ('first_ingress', 'first_send', 'send_cleanup', 'disconnect')
DIAGNOSTIC_REASONS = (
    'COMPACTION_WITH_OUTSTANDING_WORK',
    'DUPLICATE_ITEM',
    'DUPLICATE_OR_UNKNOWN_REQUEST_ID',
    'EXISTING_OWNER_QUEUE_REQUIRED',
    'FOREIGN_OR_INACTIVE_NATIVE_TURN',
    'FOREIGN_OR_UNKNOWN_NATIVE_SCOPE',
    'FOREIGN_REQUEST_SCOPE',
    'FRESH_CANARY_EARLY_MCP_SCOPE_MISMATCH',
    'FRESH_CANARY_PENDING_HOOK',
    'FRESH_CANARY_RAW_ITEM_STATUS',
    'FRESH_CANARY_TOOL_OR_RESULT_AUTHORITY_NOT_ADMITTED',
    'FRESH_CANARY_UNKNOWN_WIRE_SHAPE',
    'FRESH_CANARY_UNSOLICITED_EARLY_MCP',
    'INITIALIZATION_ORDER',
    'MCP_STARTUP_NOT_SETTLED',
    'MISSING_IMMEDIATE_CANCELLATION',
    'NATIVE_INGRESS_CLOSED_OR_UNKNOWN',
    'NATIVE_RESPONSE_ID_TYPE',
    'NATIVE_SERVER_REQUEST_NOT_ADMITTED',
    'NO_COMPLETE_CURRENT_OWNER_QUIESCENCE_FENCE',
    'OUTGOING_EFFECT_UNKNOWN',
    'OVERLAPPING_TURN_NOT_ADMITTED',
    'OWNED_QUEUE_REJECTED_INGRESS',
    'PINNED_LIFECYCLE_VALIDATOR_REQUIRED',
    'RAW_TOOLS_OR_UNKNOWN_ITEM',
    'READ_FENCE_SCOPE',
    'REQUEST_BEFORE_INITIALIZATION',
    'REQUEST_OUTSIDE_CONSERVATIVE_PROFILE',
    'REQUEST_PARAMS_SHAPE',
    'RESPONSE_SHAPE',
    'SECOND_SESSION_OR_THREAD_NOT_ADMITTED',
    'SELECTED_THREAD_RESPONSE_CHANGED',
    'THREAD_CREATION_SCOPE',
    'TOOLS_OR_UNKNOWN_ITEM_NOT_ADMITTED',
    'TURN_CREATION_SCOPE',
    'TURN_TERMINAL_WITH_PENDING_OR_UNKNOWN_WORK',
    'UNEXPECTED_NATIVE_THREAD',
    'UNKNOWN',
    'UNKNOWN_DELTA_ITEM',
    'UNKNOWN_DUPLICATE_OR_FAILED_RESPONSE',
    'UNKNOWN_ITEM_COMPLETION',
    'UNKNOWN_NATIVE_EVENT_REQUIRES_PROFILE_REVIEW',
    'UNKNOWN_NATIVE_NOTIFICATION_SHAPE',
    'UNKNOWN_NATIVE_RECORD',
    'UNKNOWN_NATIVE_RESPONSE_ENVELOPE',
    'UNKNOWN_OWNER_REQUEST',
    'UNREQUESTED_NATIVE_TURN',
    'UNSELECTED_NATIVE_RESUME',
)
DIAGNOSTIC_PHASES = (
    'AUTHORIZED', 'SUBJECT_INIT', 'ROTATION', 'SOURCE_LOAD', 'BINARY_EXTRACT', 'BINARY_VERSION',
    'PROVIDER_SETUP', 'NATIVE_LAUNCH', 'NATIVE_INIT', 'THREAD_START', 'SEED_TURN', 'SOURCE_SELECT',
    'C02_INTERVAL', 'CONTROLLED_FAULT', 'APPEND_MATERIALIZE', 'MATERIALIZE_RETRY', 'APPEND',
    'APPEND_RETRY', 'C02_NEGATIVES', 'FRESH_GRANT', 'CORRECTION', 'CORRECTION_RETRY',
    'CORRECTED_READBACK', 'LEASE_WITHDRAW', 'LATER_COMPACT', 'LATER_RESUME', 'LATER_REGISTER',
    'LATER_PENDING', 'LATER_INVALIDATE', 'LATER_READBACK', 'CLEANUP', 'INPUT_VERIFY', 'COMPLETE')
DIAGNOSTIC_MILESTONES = (
    'INIT', 'ROTATE', 'BIN', 'PROVIDER', 'NATIVE', 'RPC_INIT', 'THREAD', 'SEED', 'SELECT',
    'INTERVAL', 'FAULT', 'REVISIONS', 'REV_RETRY', 'APPEND', 'APP_RETRY', 'NEGATIVE',
    'FRESH_GRANT', 'CORRECT', 'CORR_RETRY', 'READBACK', 'WITHDRAW', 'COMPACT', 'RESUME',
    'REGISTER', 'PENDING', 'INVALIDATE', 'RECEIVE', 'CLEANUP', 'INPUTS')
DIAGNOSTIC_CATEGORIES = (
    'TYPE_ERROR', 'KEY_ERROR', 'INDEX_ERROR', 'ATTRIBUTE_ERROR', 'VALUE_ERROR', 'RUNTIME_ERROR',
    'ASSERTION_ERROR', 'TIMEOUT', 'SUBPROCESS_TIMEOUT', 'FILE_NOT_FOUND', 'PERMISSION_ERROR',
    'OS_ERROR', 'MEMORY_ERROR', 'INTERRUPTED', 'SYSTEM_EXIT', 'OTHER')
DIAGNOSTIC_SITES = {
    'execute': 'EXECUTE', '__init__': 'INIT', 'command': 'COMMAND', 'check_bindings': 'BIND',
    'extract_owned_binary': 'BINARY', 'configure_native': 'CONFIG', 'native_call': 'CALL',
    'completed_turn': 'TURN', 'fixed_selection': 'SELECT', 'controlled_transaction': 'C02',
    'pending_tail': 'TAIL', 'owned': 'OWNED', 'expect_owner_refusal': 'NEGATIVE',
    'receive': 'RECEIVE', 'check_binary_custody': 'CUSTODY', 'shutdown': 'CLEANUP',
    'source_still_withdrawn': 'WITHDRAW', 'require': 'REQUIRE', 'read_regular': 'READ',
    'physical': 'PHYSICAL', 'verify_inputs': 'INPUTS', 'streamed_pin': 'STREAM',
    'write': 'WRITE', 'load': 'LOAD', 'gate': 'GATE', 'fresh_bodies': 'BODIES'}


def diagnostic_projection(value):
    """Validate a closed observation; absent completion never proves no effect."""
    def check(ok):
        if not ok:
            raise ValueError('MALFORMED_DIAGNOSTICS_REFUSED')
    check(type(value) is dict and set(value) ==
          {'schema', 'phase', 'completed', 'failure', 'finalization_failure', 'native'})
    check(value['schema'] == DIAGNOSTIC_SCHEMA and type(value['schema']) is str)
    check(type(value['phase']) is str and value['phase'] in DIAGNOSTIC_PHASES)
    completed = value['completed']
    check(type(completed) is list and len(completed) <= len(DIAGNOSTIC_MILESTONES)
          and all(type(item) is str and item in DIAGNOSTIC_MILESTONES for item in completed))
    indices = [DIAGNOSTIC_MILESTONES.index(item) for item in completed]
    check(indices == sorted(set(indices)))
    output = {'schema': DIAGNOSTIC_SCHEMA, 'phase': value['phase'], 'completed': list(completed)}
    for name in ('failure', 'finalization_failure'):
        failure = value[name]
        if failure is None:
            output[name] = None
            continue
        check(type(failure) is dict and set(failure) == {'phase', 'category', 'sites'})
        check(type(failure['phase']) is str and failure['phase'] in DIAGNOSTIC_PHASES)
        check(type(failure['category']) is str and failure['category'] in DIAGNOSTIC_CATEGORIES)
        sites = failure['sites']
        check(type(sites) is list and len(sites) <= 3)
        for site in sites:
            check(type(site) is str and len(site) <= 24 and re.fullmatch('[A-Z_]+:[1-9][0-9]{0,4}', site) is not None)
            check(site.split(':', 1)[0] in DIAGNOSTIC_SITES.values())
        output[name] = {'phase': failure['phase'], 'category': failure['category'], 'sites': list(sites)}
    native = value['native']
    if native is None:
        output['native'] = None
    else:
        check(type(native) is dict and set(native) == set(DIAGNOSTIC_NATIVE_FIELDS))
        output['native'] = {}
        for name in DIAGNOSTIC_NATIVE_FIELDS:
            failure = native[name]
            if failure is None:
                output['native'][name] = None
                continue
            expected = {'category', 'reason', 'stage'} if name == 'first_send' else {'category', 'reason'}
            check(type(failure) is dict and set(failure) == expected)
            check(type(failure['category']) is str and failure['category'] in DIAGNOSTIC_CATEGORIES)
            check(type(failure['reason']) is str and failure['reason'] in DIAGNOSTIC_REASONS)
            projected = {'category': failure['category'], 'reason': failure['reason']}
            if name == 'first_send':
                check(type(failure['stage']) is str and failure['stage'] in DIAGNOSTIC_SEND_STAGES)
                projected['stage'] = failure['stage']
            output['native'][name] = projected
    check(len(json.dumps(output, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()) + 1 <= DIAGNOSTIC_BYTES)
    return output


def diagnostic_store(results, value):
    """Commit one bounded observation atomically inside the already owned output."""
    value = diagnostic_projection(value)
    raw = canonical(value) + b'\n'
    target, temporary = OUTPUT / 'DIAGNOSTICS.json', OUTPUT / 'DIAGNOSTICS.next'
    if os.path.lexists(target):
        info = physical(target)
        require(info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o600,
                'DIAGNOSTIC_CUSTODY_CHANGED')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        directory = os.open(OUTPUT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.lexists(temporary):
            temporary.unlink()
    results['diagnostics'] = value


def diagnostic_mark(results, phase, *, completed=None, native=None):
    value = copy.deepcopy(results.get('diagnostics', {'schema': DIAGNOSTIC_SCHEMA,
        'phase': 'AUTHORIZED', 'completed': [], 'failure': None, 'finalization_failure': None, 'native': None}))
    value['phase'] = phase
    if native is not None:
        value['native'] = native.diagnostic_snapshot()
    if completed is not None:
        require(completed not in value['completed'], 'DIAGNOSTIC_MILESTONE_REPEATED')
        value['completed'].append(completed)
    diagnostic_store(results, value)


def diagnostic_failure(results, exc, *, finalization=False, native=None):
    value = copy.deepcopy(results['diagnostics'])
    name = 'finalization_failure' if finalization else 'failure'
    if value[name] is not None:
        return
    category = 'OTHER'
    for exception, code in ((TypeError, 'TYPE_ERROR'), (KeyError, 'KEY_ERROR'),
        (IndexError, 'INDEX_ERROR'), (AttributeError, 'ATTRIBUTE_ERROR'), (ValueError, 'VALUE_ERROR'),
        (RuntimeError, 'RUNTIME_ERROR'), (AssertionError, 'ASSERTION_ERROR'), (TimeoutError, 'TIMEOUT'),
        (subprocess.TimeoutExpired, 'SUBPROCESS_TIMEOUT'), (FileNotFoundError, 'FILE_NOT_FOUND'),
        (PermissionError, 'PERMISSION_ERROR'), (OSError, 'OS_ERROR'), (MemoryError, 'MEMORY_ERROR'),
        (KeyboardInterrupt, 'INTERRUPTED'), (SystemExit, 'SYSTEM_EXIT')):
        if isinstance(exc, exception):
            category = code
            break
    sites, frame = [], exc.__traceback__
    for _ in range(64):
        if frame is None:
            break
        code = frame.tb_frame.f_code
        if code.co_filename == __file__ and code.co_name in DIAGNOSTIC_SITES and 0 < frame.tb_lineno < 100000:
            sites.append(DIAGNOSTIC_SITES[code.co_name] + ':' + str(frame.tb_lineno))
        frame = frame.tb_next
    value[name] = {'phase': value['phase'], 'category': category, 'sites': sites[-3:]}
    if native is not None:
        value['native'] = native.diagnostic_snapshot()
    diagnostic_store(results, value)



def gate(go_sha):
    require(bool(go_sha and re.fullmatch('[0-9a-f]{64}', go_sha)), 'EXACT_ROOT_GO_SHA_REQUIRED')
    raw, identity = read_regular(LANE / 'ROOT_GO.json', 65536)
    require(sha(raw) == go_sha, 'ROOT_GO_CHANGED')
    go = decode(raw)
    seal_raw, seal_identity = read_regular(LANE / 'SEALED_PREPARATION.json')
    seal = decode(seal_raw)
    required = {'schema': 'implementaudit.r5.c02-native-tail-root-go.v1', 'author': '/root', 'decision': 'GO',
        'subject': str(SUBJECT), 'controller': CONTROLLER, 'owned_binary': str(OWNED_BINARY),
        'preparation_sha256': sha(seal_raw),
        'source_commit': SOURCE_HEAD, 'source_tree': SOURCE_TREE, 'one_shot': True,
        'allocation_authorized': ['fresh-subject', 'fresh-controller', 'owned-binary-copy', 'one-native-app-server',
                                  'one-loopback-emulated-provider', 'local-emulated-MCP', 'existing-host-store',
                                  'controlled-C02', 'one-later-native-compaction-resume', 'independent-readback']}
    require(all(go.get(k) == v for k, v in required.items()), 'ROOT_GO_SCOPE')
    review_raw, review_identity = read_regular(LANE / 'INDEPENDENT_TECHNICAL_REVIEW.json')
    review = decode(review_raw)
    require(sha(review_raw) == go['independent_review_sha256']
            and review['schema'] == 'implementaudit.r5.c02-native-tail-independent-review.v1'
            and review['decision'] == 'PASS' and review['blocking_findings'] == []
            and review['preparation_sha256'] == sha(seal_raw)
            and isinstance(review['reviewer'], str) and review['reviewer'].startswith('/root/')
            and review['reviewer'] not in ('/root/r5_c02_successor_prepare', '/root/h0_c02_or') and review['reviewer'] == '/root/c02_cold_review', 'INDEPENDENT_REVIEW_SCOPE')
    require(seal['schema'] == 'implementaudit.r5.c02-native-tail-sealed-preparation.v1'
            and seal['authority'] == 'PREPARATION_ONLY' and seal['input_manifest_sha256'] == INPUT_SHA256,
            'PREPARATION_SEAL_SCOPE')
    names = set()
    sealed_identities = {}
    for item in seal['files']:
        path = LANE / item['name']
        require(path.parent == LANE and item['name'] not in names, 'SEALED_PATH_SCOPE')
        names.add(item['name'])
        content, observed = read_regular(path)
        require(len(content) == item['bytes'] and sha(content) == item['sha256']
                and stat.S_IMODE(observed[2]) == item['mode'], 'SEALED_ARTIFACT_CHANGED_' + item['name'])
        sealed_identities[item['name']] = observed
    require({'c02_native_tail.py', 'receive_tail.py', 'INPUT_MANIFEST.json', 'PROTOCOL_PLAN.json',
             'DESIGN.md', 'VERIFICATION.json'} <= names, 'SEALED_PREPARATION_INCOMPLETE')
    return {'bytes': raw, 'sha256': sha(raw), 'identity': identity, 'review_bytes': review_raw,
            'review_sha256': sha(review_raw), 'review_identity': review_identity,
            'seal_sha256': sha(seal_raw), 'seal_identity': seal_identity, 'sealed_identities': sealed_identities}


def prepare_check():
    manifest, payload, identities, raw = verify_inputs(full=True)
    owner = payload['runtime/skills/implementaudit/scripts/claim-run-rotation.py']
    source = payload['runtime/skills/implementaudit/scripts/compaction-source-owner-codex-app.py']
    pending = payload['runtime/skills/implementaudit/scripts/compaction-audit-pending.py']
    tree = ast.parse(owner)
    accepted = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_NATIVE_SOURCE_OWNER_TEMPLATE_SHA256S' for t in node.targets):
            # The set contains one name and one literal. Resolve only the literal
            # assignment/set, never import or execute the claim owner.
            accepted = set()
            literal_names = {target.id: ast.literal_eval(n.value) for n in tree.body
                if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)
                for target in n.targets if isinstance(target, ast.Name)}
            for element in node.value.elts:
                accepted.add(literal_names[element.id] if isinstance(element, ast.Name) else ast.literal_eval(element))
    require(accepted is not None and sha(source) in accepted, 'CURRENT_SOURCE_OWNER_NOT_IN_FIXED_ACCEPTING_TEMPLATE_SET')
    require(source.count(b'OWNED_STDIO_SELECTION_PIN = None') == 1, 'FIXED_SELECTION_LITERAL_CHANGED')
    required_owner = ['materialize_c02_owner_revisions_v1', 'prepare_c02_correction_v1', 'publish_c02_correction_v1',
                      'run_c02_correction_v1', 'require_current_generation_join_v1', 'invalidate_current_generation_v1']
    names = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    require(set(required_owner) <= names, 'CURRENT_OWNER_INTERFACE_CHANGED')
    require(b'Logical reservation/cutoff only.' in pending and b'fresh-canary-physical-reservation-policy.v1' in pending
            and b'SOURCE_REGISTERED_PHYSICAL_ONLY' in pending and b'ADMITTED_JOIN_ABSENT' in pending,
            'PENDING_SCOPE_CONTRACT_CHANGED')
    require(MISSING_FRESH.encode() in owner and STALE.encode() in owner and WITHDRAWN.encode() in source,
            'EXPECTED_REFUSAL_CONTRACT_CHANGED')
    parsed = []
    for name in ('c02_native_tail.py', 'receive_tail.py'):
        ast.parse(read_regular(LANE / name)[0], filename=name)
        parsed.append(name)
    for key, value in payload.items():
        if key.startswith(('retained/', 'retained-reference/')) and key.endswith('.py'):
            ast.parse(value, filename=key)
            parsed.append(key)
    return {'status': 'PREPARATION_CHECK_PASS', 'authority': 'NONE', 'input_manifest_sha256': INPUT_SHA256,
            'pinned_input_count': len(manifest['members']), 'current_native_source_template_sha256': sha(source),
            'historical_reference_bytes': len(payload['history/reviewed-r4-source-owner']), 'parsed_python': parsed,
            'subject_probed': False, 'owner_imported_or_invoked': False, 'binary_extracted_or_launched': False,
            'socket_or_network_allocated': False, 'actual_transaction_or_tail_proved': False,
            'execution_requires_independent_review_and_root_GO': True}


def group(owner, value):
    return {'owner': owner, 'value': value}


def fresh_bodies(s):
    """Current format helper only; every fixture semantic group is replaced."""
    template = decode(s.inputs['runtime/fixtures/canonical-state-rotation/v2/source.json'])['bodies']
    bodies = copy.deepcopy(template)
    record = lambda name, description, status, refs: {'record_id': name, 'status': status,
        'description': description, 'scope': 'the exact root-authorized fresh C02 and physical pending-boundary subject', 'evidence_refs': refs}
    instruction = lambda name, issuer, description, refs: {'record_id': name, 'issuer': issuer,
        'subject': description, 'scope': 'one fresh subject only; unchanged original acceptance criteria',
        'applicability': 'APPLIES', 'status': 'ACTIVE', 'evidence_refs': refs, 'issued_epoch': 'G0001',
        'expires_at': None, 'supersedes': []}
    state_values = {
      'identity': {'controller_id': CONTROLLER, 'claim_id': s.context['claim_id'],
        'run_root_identity': s.context['run_root_identity'], 'audit_object': 'Fresh controlled C02 and genuinely later physical native boundary admission',
        'candidate': s.head, 'tree': s.tree, 'package': 'exact copied runtime ' + SOURCE_HEAD, 'pull_request': None, 'release': None},
      'continuation': {'phase': '1', 'status': 'open', 'next_action': s.next_action, 'route': 'ordinary',
        'last_check': 'Actual fresh controller initialization activated; future native allocation requires exact retained root GO'},
      'instructions': [instruction('owner-continuation', '/root preparation scope', 'Preparation scope data only; exact root GO and independent review authorize this fresh operation.', ['order'])],
      'authorisations': [instruction('exact-one-shot-root-go', '/root under the standing owner continuation',
        'Allocate and execute precisely the reviewed fresh controlled C02 and later physical native-boundary pending admission with independent readback', ['go', 'review'])],
      'terminal': {'one_shots': [], 'markers': [], 'handoffs': [], 'external_effects': []},
      'andons': [], 'original_reds': [], 'pending_boundaries': [],
      'non_verdicts': [record('no-original-award', 'This scoped engineering operation does not award any original DG18 criterion, closure or release.', 'PRESERVED', ['order'])],
      'evidence_ceilings': [record('emulated-provider-only', 'The official native process and physical transcript are real; all provider text and usage and the local MCP acknowledgment are explicitly emulated.', 'ACTIVE', ['protocol']),
        record('pending-only-tail', 'The later boundary remains pending and audit_state_required; logical reservation is not child cognition, native result acceptance or JOIN.', 'ACTIVE', ['protocol']),
        record('resource-scope', 'Bounded Linux process ownership and cleanup are checked; no Windows envelope or resource acceptance is claimed.', 'ACTIVE', ['protocol'])],
      'steers': [],
      'rollback': {'status': 'AVAILABLE', 'target': None, 'conditions': ['Preserve any failure without automatic retry or compensation; further work requires separate root direction.'], 'evidence_refs': ['go']},
      'runtime_artifacts': []}
    frontier = {'DONE': ['truthful-fresh-initialization'], 'ACTIVE': ['controlled-c02-and-later-native-boundary'],
                'READY': [], 'BLOCKED': ['independent-original-receiving']}
    roadmap_values = {'frontier': frontier,
      'obligations': [record('full-controlled-c02', 'Obtain fresh complete census and configured append/fresh grants; check exact retries, refusal, payload and marker preservation, then independent cold currentness.', 'OPEN', ['protocol']),
        record('later-boundary-admission', 'Withdraw the old C02 interval, complete native compaction and resumed turn, admit exact physical source through existing pending owner and canonical invalidation, and preserve unresolved pending/stale state.', 'OPEN', ['protocol'])],
      'deferrals': [], 'dependencies': [], 'compensations': [],
      'planning': {'goal': 'One concrete C02 transaction followed by a genuinely later native boundary on the same corrected subject',
        'action_selection': {'selected': ['fresh owner initialization', 'controlled C02', 'physical native compaction/resume', 'existing pending and invalidation owners', 'independent cold receiving'],
          'omitted': ['native child result or JOIN', 'real provider usage', 'original acceptance'], 'rationale': 'Exercise the exact C02 acceptance edge while preserving its authority limits.'},
        'scope_boundaries': ['one previously absent subject', 'one native app process', 'one later compaction', 'pending remains unconsumed'], 'baseline_ref': s.head}}
    for role, values in [('STATE', state_values), ('ROADMAP', roadmap_values)]:
        require(set(values) == set(template[role]['payload']), 'CURRENT_GROUP_POPULATION_CHANGED')
        body = bodies[role]
        body['payload'] = {name: group(template[role]['payload'][name]['owner'], value) for name, value in values.items()}
        body['pair_id'] = 'r5-c02-native-tail-actual-subject'
        body['continuity'] = {'projection_generation_id': 'G0001', 'continuity_epoch': 'G0001', 'invalidation_oid': None,
            'predecessor_receipt_ref_oid': None, 'expected_receipt_ref': 'refs/implementaudit/continuity-receipts/' + CONTROLLER + '/G0001',
            'expected_receipt_schema': 'implementaudit.continuity-receipt.v2', 'boundary': 'new-session', 'reconciled': True}
        body['transition'], body['archive_pointers'], body['history'], body['artifact_refs'] = None, [], [], []
        lines = s.authored[role].decode().splitlines()
        epoch_lines = [line for line in lines if re.search(r'current\s+epoch\s*:', line, re.I)]
        require(epoch_lines == (['Current epoch: G0001'] if role == 'STATE' else []), 'ACTUAL_AUTHOR_EPOCH_SPELLING_CHANGED')
        body['payload']['native_guards'] = group(role + '.md', {'schema_version': 'implementaudit.native-guard-profile.v1',
            'lines': [line for line in lines if line != 'Current epoch: G0001']})
    s.artifacts = {'go': s.go['bytes'], 'review': s.go['review_bytes'], 'order': s.inputs['owner-continuation'],
        'input_manifest': s.input_manifest_raw, 'initialization': canonical(s.activation), 'protocol': s.inputs['protocol-plan'],
        'r4_reviewed_source_owner': s.inputs['history/reviewed-r4-source-owner'],
        'work_graph': canonical({'schema': 'r5.actual-c02-native-tail-task-frontier.v1', 'frontier': frontier,
            'authority': 'TASK_FACTS_ONLY_NOT_NATIVE_DG16_GRAPH_ADMISSION'})}
    bodies['STATE']['artifact_refs'] = [{'artifact_id': 'receipt', 'owner': 'claim-run.sh', 'role': 'CONTINUITY_RECEIPT',
        'locator': 'refs/implementaudit/continuity-receipts/' + CONTROLLER + '/G0001', 'object_format': 'sha1'}]
    for aid, locator in [('go', 'evidence/root-go.json'), ('review', 'evidence/independent-review.json'),
        ('order', 'evidence/owner-continuation.md'), ('input_manifest', 'evidence/input-manifest.json'),
        ('initialization', 'evidence/initialization.json'), ('protocol', 'evidence/protocol-plan.json'),
        ('r4_reviewed_source_owner', 'evidence/historical-r4-source-owner.py')]:
        bodies['STATE']['artifact_refs'].append({'artifact_id': aid, 'owner': 'STATE.md', 'role': 'EVIDENCE', 'locator': locator, 'object_format': 'sha1'})
    bodies['ROADMAP']['artifact_refs'] = [{'artifact_id': 'work_graph', 'owner': 'WORK_GRAPH.json', 'role': 'WORK_GRAPH',
                                         'locator': 'WORK_GRAPH.json', 'object_format': 'sha1'}]
    bodies['STATE']['payload']['runtime_artifacts']['value'] = sorted(['receipt', *s.artifacts])
    bodies['STATE']['history'] = [{'record_id': 'historical-reviewed-r4-source-owner', 'record_kind': 'artifact.historical',
        'owner': 'R0033/continuity', 'status': 'PRESERVED', 'payload': {
            'text': s.inputs['history/reviewed-r4-source-owner'].decode(), 'evidence_refs': ['r4_reviewed_source_owner'],
            'original_scope': 'Exact R4 handoff-v3 postimage used as retained historical reference, not as the current executing source',
            'current_applicability': 'INVALIDATED_CURRENT_USE',
            'historical_refusal': 'Preserved historical reviewed source bytes confer no current producer, code, grant, or acceptance authority.'}}]
    for role in ('STATE', 'ROADMAP'):
        for ref in bodies[role]['artifact_refs']:
            if ref['role'] != 'CONTINUITY_RECEIPT':
                write(s.run / ref['locator'], s.artifacts[ref['artifact_id']])
    return bodies


class FreshSubject:
    """Actual current initialization. No inheritance from retained Subject."""
    def __init__(self, manifest, inputs, identities, manifest_raw, go):
        self.input_manifest, self.inputs, self.input_identities = manifest, inputs, identities
        self.input_manifest_raw, self.go = manifest_raw, go
        self.source, self.repo, self.out, self.controller = SOURCE, SUBJECT, OUTPUT, CONTROLLER
        self.sequence, self.commands, self.copied = 0, [], {}
        self.repo.mkdir(exist_ok=False)
        self.evidence = self.out / 'evidence'
        self.evidence.mkdir()
        (self.repo / '.task-tmp').mkdir()
        self.env = dict(ENV, TMPDIR=str(self.repo / '.task-tmp'))
        self.scripts = self.repo / 'skills/implementaudit/scripts'
        for member in manifest['members']:
            if member['category'] in ('current-runtime', 'current-support'):
                target = self.repo / member['destination']
                write(target, inputs[member['key']])
                os.chmod(target, member['mode'])
                self.copied[str(target)] = {'raw': inputs[member['key']], 'mode': member['mode']}
            elif member['category'] == 'retained-executed-support':
                target = self.out / 'support' / Path(member['path']).name
                write(target, inputs[member['key']])
                os.chmod(target, member['mode'])
                self.copied[str(target)] = {'raw': inputs[member['key']], 'mode': member['mode']}
        self.check_bindings()
        self.git('-c', 'init.templateDir=', 'init', '-q', '-b', 'qualification', '--object-format=sha1')
        write(self.repo / '.gitignore', b'.IMPLEMENTAUDIT/\n.task-tmp/\nskills/\nfixtures/\n')
        write(self.repo / 'TASK.md', ('# Actual fresh controlled C02 and later native boundary\n\n'
            'Execute the exact reviewed single-subject C02 and physical pending-boundary operation.\n'
            'Source commit: ' + SOURCE_HEAD + '\nSource tree: ' + SOURCE_TREE + '\n'
            'Input manifest SHA256: ' + INPUT_SHA256 + '\n'
            'All provider text and usage and local MCP responses are explicitly emulated.\n'
            'The later native boundary remains pending; no original award or child JOIN is authorized.\n').encode())
        write(self.repo / 'INPUT_BINDING.json', {'source_commit': SOURCE_HEAD, 'source_tree': SOURCE_TREE,
            'input_manifest_sha256': INPUT_SHA256, 'root_go_sha256': go['sha256'],
            'review_sha256': go['review_sha256'], 'sealed_preparation_sha256': go['seal_sha256'],
            'authority': 'THIS_ONE_FRESH_CONTROLLED_SUBJECT_ONLY'})
        self.git('add', '--', '.gitignore', 'TASK.md', 'INPUT_BINDING.json')
        self.git('-c', 'user.name=R5 controlled C02 native tail', '-c', 'user.email=r5-c02-tail@example.invalid',
                 '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null', 'commit', '-qm',
                 'Define actual bounded fresh C02 and native tail task')
        self.head = self.git('rev-parse', 'HEAD').stdout.decode().strip()
        self.tree = self.git('rev-parse', 'HEAD^{tree}').stdout.decode().strip()
        relative = self.claim('--controller', CONTROLLER, 'R5 fresh C02 native tail').stdout.decode().strip()
        require(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9-]+-[A-Za-z0-9]{6}', relative) is not None, 'UNEXPECTED_FRESH_RUN_ROOT')
        self.run = self.repo / relative
        self.next_action = 'Execute controlled C02, independently receive its correction, then admit one later physical native boundary while preserving the pending audit obligation'
        self.command(['/usr/bin/python3', '-I', '-B', self.repo / 'fixtures/controller-initialization/author_checkpoint.py',
            '--repo', self.repo, '--run-root', relative, '--source', self.repo,
            '--purpose', 'Execute one root-authorized fresh controlled C02 and later physical native-boundary pending admission with current exact owners and independent readback.',
            '--next-action', self.next_action])
        inspection = decode(self.claim('--inspect-controller-initialization', CONTROLLER, '--run-root', relative).stdout)
        require(not inspection['missing_files'] and inspection['current_controller_oid'] is None, 'FRESH_INITIALIZATION_NOT_COMPLETE')
        write(self.evidence / 'INITIALIZATION_INSPECTION.json', inspection)
        self.activation = decode(self.claim('--activate-controller', CONTROLLER, '--run-root', relative,
            '--expected-initialization', inspection['initialization_token']).stdout)
        require(self.activation['status'] == 'BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS', 'INITIALIZATION_NOT_BOUND')
        self.authored = {role: (self.run / (role + '.md')).read_bytes() for role in ('STATE', 'ROADMAP')}
        for name in ('STATE.md', 'ROADMAP.md', 'PROTOCOL.md', 'THINKING.md', 'sidecars.md', 'tools.md', 'context.md', 'phases/phase-1.md'):
            write(self.evidence / 'initial-authored' / name, (self.run / name).read_bytes())
        self.owner = load(self.scripts / 'claim-run-rotation.py', 'r5_c02_tail_current_claim_owner')
        with contextlib.chdir(self.repo):
            self.context = self.owner.discover(CONTROLLER)
        self.factory = load(self.repo / 'fixtures/canonical-state-rotation/protected_projection_v2_test.py', 'r5_c02_tail_current_format_helper')
        self.bodies = fresh_bodies(self)
        self.original = self.factory.render_pair(self.bodies)
        require(sum(map(len, self.original.values())) > 131072, 'REAL_HISTORICAL_REFERENCE_DOES_NOT_TRIGGER_ROTATION')
        for role, raw in self.original.items():
            write(self.run / (role + '.md'), raw, replace=True)
            write(self.evidence / 'preimage' / (role + '.md'), raw)
        self.legacy = self.claim('--resume-controller', CONTROLLER, '--boundary', 'new-session', '--epoch', 'G0001').stdout.decode().strip()
        require(self.claim('--verify-resume-receipt', self.legacy).stdout.decode().strip() == self.legacy, 'FRESH_LEGACY_RECEIPT')
        require(self.claim('--require-current-continuity', CONTROLLER).stdout.decode().strip() == self.legacy, 'FRESH_LEGACY_CURRENTNESS')
        self.artifacts['receipt'] = self.git('cat-file', 'blob', self.legacy.split('@', 1)[1]).stdout
        self.owner_map = self.run / 'owner-map.json'
        write(self.owner_map, {'schema': 'implementaudit.rotation-owner-map.v2',
            'owner_map': self.factory.build_owner_map(self.bodies, self.original, self.artifacts)})
        parsed = self.factory.MODULE.parse_canonical_pair_v2(self.original['STATE'], self.original['ROADMAP'],
            owner_map=decode(self.owner_map.read_bytes())['owner_map'], artifacts=self.artifacts)
        write(self.evidence / 'PREIMAGE.json', {key: parsed[key] for key in ('schema_version', 'authority_ceiling',
            'payload', 'owner_map', 'source_hashes', 'current_continuity', 'current_receipt_ref_oid',
            'archive_population', 'protected_manifest')})
        write(self.evidence / 'INITIAL.json', {'controller': CONTROLLER, 'claim_id': self.context['claim_id'],
            'run_root_identity': self.context['run_root_identity'], 'subject_head': self.head, 'subject_tree': self.tree,
            'runtime_source_commit': SOURCE_HEAD, 'runtime_source_tree': SOURCE_TREE, 'activation': self.activation,
            'legacy_receipt': self.legacy, 'pair_bytes': {role: len(raw) for role, raw in self.original.items()},
            'truthful_initialization': True, 'old_Subject_constructor_called': False, 'fixture_authority_records': False})
        self.check_bindings()

    def check_bindings(self, *, full=False):
        manifest, inputs, identities, raw = verify_inputs(full=full, original_identities=self.input_identities)
        require(manifest == self.input_manifest and inputs == self.inputs and identities == self.input_identities
                and raw == self.input_manifest_raw, 'ORIGINAL_INPUT_CUSTODY_CHANGED')
        require(gate(self.go['sha256']) == self.go, 'ROOT_GO_OR_REVIEW_CUSTODY_CHANGED')
        for name, expected in self.copied.items():
            current, identity = read_regular(name)
            require(current == expected['raw'] and stat.S_IMODE(identity[2]) == expected['mode'], 'OWNED_COPY_CHANGED_' + Path(name).name)

    def command(self, argv, expect=0, input_bytes=None, timeout=45):
        self.check_bindings()
        self.sequence += 1
        n = self.sequence
        started = time.monotonic_ns()
        child = subprocess.Popen(list(map(str, argv)), cwd=self.repo, env=self.env,
            stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        timed_out = False
        stdout = stderr = b''
        try:
            stdout, stderr = child.communicate(input=input_bytes, timeout=timeout)
        except BaseException:
            timed_out = True
            if child.poll() is None:
                if str(LANE / 'receive_tail.py') in list(map(str, argv)):
                    # The reader handles TERM by killing/reaping its one active
                    # read-command group and writing failure evidence first.
                    os.killpg(child.pid, signal.SIGTERM)
                    try:
                        stdout, stderr = child.communicate(timeout=7)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid, signal.SIGKILL)
                else:
                    os.killpg(child.pid, signal.SIGKILL)
            try:
                stdout, stderr = child.communicate(timeout=5)
            except BaseException:
                pass
            raise
        finally:
            require(len(stdout) + len(stderr) <= 8 * 1024 * 1024, 'COMMAND_OUTPUT_BOUND')
            write(self.evidence / f'{n:03d}.stdout', stdout)
            write(self.evidence / f'{n:03d}.stderr', stderr)
            self.commands.append({'sequence': n, 'argv': list(map(str, argv)), 'cwd': str(self.repo),
                'returncode': child.returncode, 'interrupted': timed_out, 'elapsed_ms': (time.monotonic_ns() - started) / 1e6,
                'stdout_sha256': sha(stdout), 'stderr_sha256': sha(stderr)})
            write(self.evidence / 'COMMANDS.json', self.commands, replace=True)
            self.check_bindings()
        require(expect is None or child.returncode == expect, 'COMMAND_FAILED_' + str(n))
        return subprocess.CompletedProcess(list(map(str, argv)), child.returncode, stdout, stderr)

    def git(self, *args, **kw):
        return self.command(['/usr/bin/git', *args], **kw)

    def claim(self, *args, **kw):
        return self.command(['/usr/bin/bash', self.scripts / 'claim-run.sh', *args], **kw)

    def refs(self):
        rows = self.git('for-each-ref', '--format=%(refname) %(objectname)', 'refs/implementaudit/').stdout.decode().splitlines()
        require(len(rows) <= 128, 'REF_BOUND')
        return dict(row.split(' ', 1) for row in rows)

    def managed(self):
        refs = self.refs()
        return {name: refs.get(self.context[name + '_ref']) for name in ('controller', 'pointer', 'marker', 'invalidation')}

    def runtime_pins(self):
        return [{'path': name, 'bytes': len(item['raw']), 'sha256': sha(item['raw']), 'mode': item['mode']}
            for name, item in sorted(self.copied.items()) if Path(name).is_relative_to(self.repo)]


def allocation_tree(s):
    """Scoped file inventory around the negative fresh-grant attempt; no host scan."""
    records = {}
    total = 0
    for root_name in ('state-generations', 'continuity-epochs', 'epochs'):
        root = s.run / root_name
        if not root.exists():
            records[root_name] = None
            continue
        for path in sorted(root.rglob('*')):
            if path.is_dir():
                continue
            raw, _ = read_regular(path)
            total += len(raw)
            require(len(records) < 512 and total <= 32 * 1024 * 1024, 'ALLOCATION_TREE_BOUND')
            records[str(path.relative_to(s.run))] = {'bytes': len(raw), 'sha256': sha(raw)}
    return records


def public_corrected_request(s):
    corrected = decode(s.claim('--resolve-canonical-generation', CONTROLLER).stdout)
    require(corrected['pointer']['continuity_epoch'] == 'G0003'
            and corrected['pointer']['projection_generation_id'] == 'G0003', 'CORRECTED_GENERATION_NOT_G0003')
    roles = {role: s.claim('--read-canonical-state', CONTROLLER, '--role', role,
        '--expected-pointer', corrected['pointer_token']).stdout for role in ('STATE', 'ROADMAP')}
    artifacts = {}
    for name, key in [('protected-state.json', 'protected_manifest_path'), ('archive-manifest.json', 'archive_manifest_path')]:
        path = Path(corrected[key])
        raw, _ = read_regular(path)
        artifacts[name] = {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}
    return {'schema': 'implementaudit.r5.c02-native-tail-readback-request.v1', 'phase': 'corrected',
        'subject': str(SUBJECT), 'controller': CONTROLLER, 'claim_id': s.context['claim_id'], 'run_root': str(s.run),
        'subject_head': s.head, 'subject_tree': s.tree, 'runtime_pins': s.runtime_pins(), 'corrected': corrected,
        'refs': s.refs(), 'refs_names': {name: s.context[name + '_ref'] for name in ('controller', 'pointer', 'marker', 'invalidation')},
        'corrected_managed': s.managed(), 'canonical_artifacts': artifacts,
        'protected_role_payload_sha256': {role: sha(canonical(s.bodies[role]['payload'])) for role in ('STATE', 'ROADMAP')},
        'corrected_role_sha256': {role: sha(raw) for role, raw in roles.items()},
        'legacy_role_sha256': {role: sha(raw) for role, raw in s.original.items()}}


def receive(s, request):
    path = OUTPUT / ('READBACK_' + request['phase'].upper() + '_REQUEST.json')
    write(path, request)
    receipt = s.command(['/usr/bin/python3', '-I', '-B', LANE / 'receive_tail.py', '--request', path,
        '--go-sha256', s.go['sha256']], timeout=190)
    result = decode(read_regular(OUTPUT / ('independent-' + request['phase']) / 'RESULT.json')[0])
    require(result['status'] == 'PASS', 'INDEPENDENT_READBACK_FAILED')
    return {'result': result, 'stdout_sha256': sha(receipt.stdout), 'request_sha256': sha(read_regular(path)[0])}


def extract_owned_binary(s):
    item = next(x for x in s.input_manifest['members'] if x['key'] == 'official-binary-archive')
    actual, identity = streamed_pin(item['path'])
    require(actual['sha256'] == item['sha256'] and actual['bytes'] == item['bytes']
            and identity == s.input_identities[item['key']], 'ARCHIVE_PRE_EXTRACTION_CHANGED')
    target = OWNED_BINARY
    target.parent.mkdir(mode=0o700, exist_ok=False)
    # No extractall and no original dg17 binary use. Exactly one fixed member.
    with tarfile.open(item['path'], 'r:gz') as archive:
        found = [m for m in archive.getmembers() if m.name == item['archive_member']]
        require(len(found) == 1 and found[0].isfile() and found[0].size == item['extracted_bytes'], 'OFFICIAL_MEMBER_IDENTITY')
        stream = archive.extractfile(found[0])
        require(stream is not None, 'OFFICIAL_MEMBER_MISSING')
        digest = hashlib.sha256()
        count = 0
        with target.open('xb') as output:
            while block := stream.read(1024 * 1024):
                count += len(block)
                require(count <= item['extracted_bytes'], 'OFFICIAL_MEMBER_OVERSIZED')
                digest.update(block)
                output.write(block)
            output.flush()
            os.fsync(output.fileno())
        require(count == item['extracted_bytes'] and digest.hexdigest() == item['extracted_sha256'], 'OWNED_BINARY_PIN_MISMATCH')
    os.chmod(target, 0o755)
    started_wall, started_mono = time.time_ns(), time.monotonic_ns()
    pin, identity = streamed_pin(target)
    expected_content = {'path': str(target), 'bytes': item['extracted_bytes'], 'sha256': item['extracted_sha256']}
    content_ok = pin['bytes'] == expected_content['bytes'] and pin['sha256'] == expected_content['sha256']
    mode_ok = stat.S_IMODE(identity[2]) == 0o755
    if not content_ok or not mode_ok:
        content_differences = {field: {'expected': expected_content[field], 'observed': pin[field]}
            for field in ('bytes', 'sha256') if expected_content[field] != pin[field]}
        # No expected metadata baseline has been admitted. Persist only the
        # measured stamp and comparisons supported by official content/mode
        # requirements, before either original refusal predicate can throw.
        write(OUTPUT / 'OWNED_BINARY_POST_COPY_REJECTION.json', {
            'schema': 'implementaudit.r5.c02-owned-binary-post-copy-rejection.v1',
            'status': 'REJECTED_POST_COPY_CONTENT' if not content_ok else 'REJECTED_POST_CHMOD_MODE',
            'phase': 'post_chmod', 'path': str(target),
            'started_wall_time_ns': started_wall, 'started_monotonic_ns': started_mono,
            'finished_wall_time_ns': time.time_ns(), 'finished_monotonic_ns': time.monotonic_ns(),
            'expected_metadata_status': 'UNAVAILABLE_NOT_ADMITTED', 'expected': None,
            'observed': named_stamp(identity), 'differing_fields': None, 'differences': None,
            'expected_content': expected_content, 'observed_content': dict(pin),
            'content_differing_fields': list(content_differences), 'content_differences': content_differences,
            'observed_mode': stat.S_IMODE(identity[2]), 'required_mode': 0o755,
            'mode_difference': {'expected': 0o755, 'observed': stat.S_IMODE(identity[2])} if not mode_ok else None,
            'source_archive': actual, 'source_member': item['archive_member'],
            'authority': 'CUSTODY_DIAGNOSTIC_ONLY'})
    require(content_ok, 'OWNED_BINARY_POST_COPY_MISMATCH')
    require(mode_ok, 'OWNED_BINARY_POST_CHMOD_MODE_NOT_0755')
    # Only an admitted observation can establish the immutable metadata baseline.
    write(OUTPUT / 'OWNED_BINARY_CUSTODY_BASELINE.json', {
        'schema': 'implementaudit.r5.c02-owned-binary-custody-baseline.v1',
        'status': 'EXPECTED_BASELINE_RECORDED',
        'phase': 'post_chmod', 'path': str(target), 'wall_time_ns': time.time_ns(),
        'monotonic_ns': time.monotonic_ns(), 'expected': named_stamp(identity),
        'observed': named_stamp(identity), 'differing_fields': [], 'differences': {},
        'expected_content': dict(pin), 'observed_content': dict(pin),
        'observed_mode': stat.S_IMODE(identity[2]), 'required_mode': 0o755,
        'source_archive': actual, 'source_member': item['archive_member'],
        'authority': 'CUSTODY_DIAGNOSTIC_ONLY'})
    s.binary_pin, s.binary_identity = pin, identity
    s.binary_custody_sequence = 0
    write(OUTPUT / 'OWNED_BINARY_PIN.json', {**pin, 'mode': 0o755, 'source_archive': actual,
        'source_member': item['archive_member'], 'independent_owned_copy': True})
    s.check_bindings(full=True)
    return target


def configure_native(home, provider, plan):
    text = f'''model = "{plan['model']}"
model_provider = "{plan['provider']}"
model_context_window = {plan['model_context_window']}
[projects.{json.dumps(str(SUBJECT))}]
trust_level = "trusted"
[features]
hooks = true
apps = false
[model_providers.{plan['provider']}]
name = "R5 explicitly emulated Responses transport"
base_url = "{provider.url}"
wire_api = "responses"
requires_openai_auth = false
request_max_retries = 0
stream_max_retries = 0
[mcp_servers.cua_repl]
command = "/usr/bin/python3"
args = [{json.dumps(str(OUTPUT / 'support/local_mcp_canary.py'))}, "--log", {json.dumps(str(OUTPUT / 'managed-mcp.jsonl'))}]
'''
    write(home / 'config.toml', text.encode())
    return sha(text.encode())


def snapshot(path, evidence_path):
    raw, identity = read_regular(path, 32 * 1024 * 1024)
    require(raw.endswith(b'\n'), 'ROLLOUT_PARTIAL_RECORD')
    write(evidence_path, raw)
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw),
            'physical': {'device': identity[0], 'inode': identity[1]}}, raw


def source_still_withdrawn(src):
    try:
        src.verify()
    except ValueError as exc:
        require(str(exc) == WITHDRAWN, 'UNEXPECTED_SOURCE_WITHDRAWAL_REASON')
        return str(exc)
    raise RuntimeError('OLD_C02_INTERVAL_SURVIVED_OR_WAS_RESTORED')


def pin_small(path):
    raw, _ = read_regular(path)
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}


def evidence_shape(value):
    if isinstance(value, bytes):
        return {'bytes': len(value), 'sha256': sha(value)}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: evidence_shape(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [evidence_shape(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return {'type_only': type(value).__name__}


def owned(s, label, function, *args, **kwargs):
    """Guard each in-process owner step; record even an expected refusal."""
    s.check_bindings()
    start = time.monotonic_ns()
    record = {'label': label, 'started_monotonic_ns': start}
    try:
        result = function(*args, **kwargs)
        record['status'] = 'RETURNED'
        record['result_sha256'] = sha(canonical(evidence_shape(result)))
        return result
    except BaseException as exc:
        record.update(status='RAISED', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        record['finished_monotonic_ns'] = time.monotonic_ns()
        s.owner_steps.append(record)
        write(OUTPUT / 'OWNER_STEPS.json', s.owner_steps, replace=True)
        s.check_bindings()


def expect_owner_refusal(s, label, function, expected, *args, **kwargs):
    try:
        owned(s, label, function, *args, **kwargs)
    except s.owner.RotationError as exc:
        require(str(exc) == expected, 'WRONG_EXACT_OWNER_REFUSAL_' + label)
        return str(exc)
    raise RuntimeError('OWNER_OPERATION_NOT_REFUSED_' + label)


def named_stamp(identity):
    fields = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    require(identity is None or len(identity) == len(fields), 'OWNED_BINARY_STAMP_SHAPE')
    return dict(zip(fields, identity)) if identity is not None else dict.fromkeys(fields)


def check_binary_custody(s, phase, reason, *, method=None, full=False):
    """Persist an exact named comparison before returning or raising; never rebaseline.

    The seven-field comparison remains mandatory. A matching per-RPC stamp does
    not claim a new content hash. Finalization and safely observable mismatches
    stream the bytes; failed observations retain the information already seen.
    """
    expected = named_stamp(s.binary_identity)
    observed_identity = None
    observed_pin = None
    hashed_identity = None
    observation_errors = []
    failure = None
    started_wall, started_mono = time.time_ns(), time.monotonic_ns()
    try:
        # lstat first retains named fields even if physical() then rejects the
        # link/type/parent custody. No symlink target is read for diagnostics.
        observed_identity = stamp(Path(s.binary_pin['path']).lstat())
        checked_identity = stamp(physical(s.binary_pin['path']))
        require(checked_identity == observed_identity, 'OWNED_BINARY_CHANGED_DURING_OBSERVATION')
        if full or observed_identity != s.binary_identity:
            try:
                observed_pin, hashed_identity = streamed_pin(s.binary_pin['path'])
                require(hashed_identity == observed_identity, 'OWNED_BINARY_CHANGED_DURING_HASH')
            except BaseException as exc:
                observation_errors.append({'stage': 'content_hash', 'error_type': type(exc).__name__, 'error': str(exc)})
                # Fatal control flow keeps the original exception object even
                # after a known mismatch. Ordinary diagnostic IO failures stay
                # subordinate to that mismatch. The outer handler persists the
                # available observations before rethrowing the saved exception.
                if isinstance(exc, (TimeoutError, KeyboardInterrupt, SystemExit)) or observed_identity == s.binary_identity:
                    raise
        require(observed_identity == s.binary_identity
                and (not full or observed_pin == s.binary_pin)
                and not observation_errors, reason)
    except BaseException as exc:
        failure = exc
        observation_errors.append({'stage': 'custody_check', 'error_type': type(exc).__name__, 'error': str(exc)})
    observed = named_stamp(observed_identity)
    differences = {field: {'expected': expected[field], 'observed': observed[field]}
                   for field in expected if expected[field] != observed[field]}
    record = {'schema': 'implementaudit.r5.c02-owned-binary-custody-observation.v1',
        'phase': phase, 'method': method, 'path': s.binary_pin['path'],
        'started_wall_time_ns': started_wall, 'started_monotonic_ns': started_mono,
        'finished_wall_time_ns': time.time_ns(), 'finished_monotonic_ns': time.monotonic_ns(),
        'expected': expected, 'observed': observed, 'differing_fields': list(differences),
        'differences': differences, 'expected_content': dict(s.binary_pin),
        'observed_content': observed_pin,
        'content_observed_stamp': named_stamp(hashed_identity) if hashed_identity is not None else None,
        'content_stamp_differences': {field: {'expected': expected[field], 'observed': value}
            for field, value in named_stamp(hashed_identity).items() if expected[field] != value}
            if hashed_identity is not None else None,
        'observed_size_from_stamp': observed['st_size'],
        'content_hash_status': 'AVAILABLE' if observed_pin is not None else
            ('UNAVAILABLE' if full or failure is not None else 'NOT_REHASHED_MATCHING_STAMP'),
        'observation_errors': observation_errors,
        'status': 'REFUSED' if failure is not None else 'MATCH',
        'authority': 'CUSTODY_DIAGNOSTIC_ONLY'}
    s.binary_custody_sequence += 1
    record['sequence'] = s.binary_custody_sequence
    # Exclusive, flushed/fsynced evidence write is before the original refusal.
    # Failure to persist also stops before RPC and never permits rebaselining.
    write(OUTPUT / 'binary-custody' / f'{s.binary_custody_sequence:03d}.json', record)
    if failure is not None:
        raise failure
    return record


def native_call(s, native, method, params):
    s.check_bindings()
    check_binary_custody(s, 'before_native_rpc', 'OWNED_BINARY_CUSTODY_CHANGED', method=method)
    require(native.proc.poll() is None, 'NATIVE_PROCESS_DIED')
    value = native.rpc(method, params, timeout=s.plan['bounds']['rpc_seconds'])
    s.check_bindings()
    return value


def completed_turn(s, native, thread_id, expected_id=None):
    value, _ = native.wait_turn(thread_id, timeout=s.plan['bounds']['turn_seconds'])
    turn = value['params']['turn']
    require(value['params']['threadId'] == thread_id and turn['status'] == 'completed'
            and isinstance(turn['id'], str) and (expected_id is None or turn['id'] == expected_id),
            'NATIVE_TURN_NOT_MATCHING_COMPLETED')
    s.check_bindings()
    return {'id': turn['id'], 'status': turn['status'], 'notification_sha256': sha(canonical(value))}


def fixed_selection(s, source, pending, native, home, tid, rollout):
    source_pin, _ = snapshot(rollout, s.evidence / 'NATIVE_SOURCE_BEFORE_C02.jsonl')
    process = source.fresh_canary_process_identity_v1(native.proc)
    capture = {'schema': 'implementaudit.fresh-native-live-canary-capture.v1', 'thread_id': tid,
        'native_version': s.plan['native_version'], 'native_executable_sha256': s.binary_pin['sha256'],
        'pid': native.proc.pid, 'proc_start_ticks': process['proc_start_ticks'], 'proc_host_pid': process['host_pid'],
        'argv': native.argv, 'cwd': str(s.repo), 'codex_home': str(home), 'source': source_pin,
        'capture_script_sha256': pin_small(LANE / 'c02_native_tail.py')['sha256'],
        'usage_origin': s.plan['usage_origin'], 'authority_ceiling': 'NONE'}
    write(OUTPUT / 'LIVE_CAPTURE.json', capture)
    configured = {'issuer': s.plan['issuer'], 'census_owner': s.plan['census_owner'],
        'decision_path': str(OUTPUT / 'issuer-output/decision.json'),
        'source_contract_locator': source.FRESH_CANARY_PROFILE,
        'owner_decision_locator': 'root GO ' + s.go['sha256'] + ' over reviewed preparation ' + s.go['seal_sha256']}
    selected = {'schema': 'implementaudit.codex-fresh-canary-provider-selection.v1',
        'profile_id': source.FRESH_CANARY_PROFILE, 'root_thread_id': tid, 'root_agent_path': '/root',
        'root_source': str(rollout), 'session_root': str(home / 'sessions'), 'cwd': str(s.repo),
        'cli_version': s.plan['cli_version'], 'native_version': s.plan['native_version'],
        'native_executable': s.binary_pin, 'codex_home': str(home),
        'runtime_helpers': {name: pin_small(s.scripts / name) for name in
            ('bounded_native_reader.py', 'bounded_source_owner.py', 'bounded_file_custody.py')},
        'episode_owner': {'module_pin': pin_small(s.scripts / 'claim-run-rotation.py'),
                          'repository': str(s.repo), 'controller': CONTROLLER},
        'pending_owner': {'store': str(OUTPUT / 'host-store'), 'session_id': tid, 'owner_id': configured['census_owner']},
        'producer_capture_pin': pin_small(OUTPUT / 'LIVE_CAPTURE.json'),
        'capture_producer_pin': pin_small(LANE / 'c02_native_tail.py'),
        'tool_evidence_contract': 'REAL_NATIVE_TRANSPORT_EMULATED_RESPONSES_NO_RESULT_AUTHORITY_V1',
        'c02_adjudication': configured}
    require(selected['profile_id'] == s.plan['profile'], 'UNEXPECTED_FRESH_PROFILE')
    selection_path = OUTPUT / 'SOURCE_SELECTION.json'
    write(selection_path, selected)
    selection_pin = pin_small(selection_path)
    target = s.scripts / 'compaction-source-owner-codex-app.py'
    template = s.copied[str(target)]['raw']
    old = b'OWNED_STDIO_SELECTION_PIN = None'
    require(template.count(old) == 1, 'FIXED_LITERAL_NOT_UNIQUE')
    materialized = template.replace(old, ('OWNED_STDIO_SELECTION_PIN = ' + repr(selection_pin)).encode())
    write(target, materialized, replace=True)
    s.copied[str(target)]['raw'] = materialized
    # The only in-memory assignment mirrors the documented fixed pin literal.
    # No live/census seal, getter, grant, materializer, or callback is replaced.
    source.OWNED_STDIO_SELECTION_PIN = selection_pin
    for path in (OUTPUT / 'LIVE_CAPTURE.json', selection_path):
        s.copied[str(path)] = {'raw': read_regular(path)[0], 'mode': stat.S_IMODE(physical(path).st_mode)}
    code = pending.nonprotected_code_identity()
    runtime = source._np_runtime(pending.OBSERVATION, code)
    write(OUTPUT / 'SELECTION_MATERIALIZATION.json', {'template_sha256': sha(template),
        'materialized_sha256': sha(materialized), 'selection_pin': selection_pin,
        'sole_replacement': 'OWNED_STDIO_SELECTION_PIN', 'code': code, 'process': process,
        'no_callback_or_capability_seal_assignment': True})
    s.check_bindings()
    return configured, code, runtime


def controlled_transaction(s, source, pending, native, tid, configured, code, runtime, results):
    owner = s.owner
    with contextlib.chdir(s.repo):
        joined = owned(s, 'C02_PREDECESSOR_CURRENT', owner.require_current_generation_join_v1, s.context)
        require(joined['pointer']['continuity_epoch'] == 'G0002', 'C02_PREDECESSOR_NOT_G0002')
        withdrew = False
        src = None
        try:
            with source.acquire_selected_c02_interval_v1(runtime, owner, s.context, native.ledger, native.proc, code) as src:
                results['source_admission'] = 'MAINTAINED_FIXED_OWNER_REAL_PROCESS_REAL_PIPE_FULL_SOURCE_SCAN'
                diagnostic_mark(results, 'C02_INTERVAL', completed='INTERVAL')
                live_join = source._fresh_canary_live_claim_join_v1(runtime, owner, s.context, native.ledger, native.proc)
                write(s.evidence / 'LIVE_CLAIM_JOIN.json', live_join)
                subject = {key: s.context[key] for key in ('controller', 'claim_id', 'run_root_identity')}
                event = s.plan['controlled_event']
                policy = {'schema': 'dg18.r4.prospective-canary-policy.v1', 'scope': 'FRESH_CONTROLLED_CANARY_ONLY',
                    'native_authority': False, 'repo': str(s.repo), 'subject': subject, 'issuer': configured['issuer'],
                    'event_id': event, 'expected_old': src.expected_old, 'source_cutoff': src.source_cutoff,
                    'append_authorized': True, 'conditional_fresh_authorized': True,
                    'provenance': 'Exact root GO ' + s.go['sha256'] + '; real native transport with explicitly emulated text/usage; no original award'}
                write(OUTPUT / 'PROSPECTIVE_POLICY.json', policy)
                diagnostic_mark(results, 'CONTROLLED_FAULT')
                token = owned(s, 'CONTROLLED_FAULT', src.inject_controlled_fault, event)
                observation = {'schema': 'implementaudit.c02-observation.v1', **subject,
                    'pointer_oid': joined['pointer_oid'], 'marker_oid': joined['marker_oid'],
                    'receipt_oid': joined['receipt_token'].split('@')[1], 'invalidation_oid': token.split('@')[1],
                    'event_id': event, 'boundary': 'new-session', 'later_boundaries': []}
                census = src.census_facts_v1()
                write(s.evidence / 'CENSUS_AFTER_CONTROLLED_EVENT.json', census)
                diagnostic_mark(results, 'CONTROLLED_FAULT', completed='FAULT')
                issuer_request = {'repo': str(s.repo), 'subject': subject, 'observed': observation,
                    'expected_old': src.expected_old, 'source_cutoff': src.source_cutoff,
                    'refs': {key: s.context[key + '_ref'] for key in ('controller', 'pointer', 'marker', 'invalidation')},
                    'code_sha256': pin_small(s.scripts / 'claim-run-rotation.py')['sha256'],
                    'projection_code_sha256': pin_small(s.scripts / 'rotate-canonical-state.py')['sha256'],
                    # Retained issuer contract uses canonical JSON WITH its LF.
                    'evidence_sha256': sha(canonical(census) + b'\n')}
                write(OUTPUT / 'ISSUER_REQUEST.json', issuer_request)
                s.command(['/usr/bin/python3', '-I', '-B', OUTPUT / 'support/canary_issuer.py',
                    '--policy', OUTPUT / 'PROSPECTIVE_POLICY.json', '--request', OUTPUT / 'ISSUER_REQUEST.json',
                    '--out', OUTPUT / 'issuer-output'])
                proposal = decode(read_regular(OUTPUT / 'issuer-output/proposal.json')[0])
                with source.selected_c02_materializer_session_v1(runtime, s.context, src):
                    with owner.c02_owned_operation_v1(s.context, token, proposal, _selected_source_owner=source):
                        diagnostic_mark(results, 'APPEND_MATERIALIZE')
                        first = owned(s, 'APPEND_OWNER_REVISIONS', owner.materialize_c02_owner_revisions_v1, s.context, token, proposal)
                        require(first['status'] == 'OWNER_REVISIONS_MATERIALIZED', 'FIRST_MATERIALIZATION_STATUS')
                        diagnostic_mark(results, 'APPEND_MATERIALIZE', completed='REVISIONS')
                        before_retry = s.refs()
                        diagnostic_mark(results, 'MATERIALIZE_RETRY')
                        again = owned(s, 'APPEND_OWNER_REVISIONS_EXACT_RETRY', owner.materialize_c02_owner_revisions_v1, s.context, token, proposal)
                        require(again['status'] == 'EXACT_REVISION_RETRY_NO_EFFECT' and s.refs() == before_retry,
                                'MATERIALIZATION_RETRY_EFFECT')
                        diagnostic_mark(results, 'MATERIALIZE_RETRY', completed='REV_RETRY')
                        diagnostic_mark(results, 'APPEND')
                        prepared = owned(s, 'PREPARE_APPEND', owner.prepare_c02_correction_v1, s.context, token, proposal)
                        appended = owned(s, 'APPEND_CORRECTION_RECORD', owner.publish_c02_correction_v1, s.context, prepared)
                        require(appended['status'] == 'APPENDED_NO_CURRENTNESS', 'APPEND_STATUS')
                        diagnostic_mark(results, 'APPEND', completed='APPEND')
                        owned(s, 'OBSERVE_ACTUAL_ADJUDICATION', src.observe_adjudication, appended['record_oid'])
                        write(s.evidence / 'APPEND_RECORD.json', owner._c02_read_correction_v1(s.context, appended['record_oid']))
                        write(s.evidence / 'CENSUS_AFTER_APPEND.json', src.census_facts_v1())
                        before_retry = s.refs()
                        diagnostic_mark(results, 'APPEND_RETRY')
                        repeated_plan = owned(s, 'PREPARE_EXACT_APPEND_RETRY', owner.prepare_c02_correction_v1, s.context, token, proposal)
                        repeat = owned(s, 'EXACT_APPEND_RETRY', owner.publish_c02_correction_v1, s.context, repeated_plan)
                        require(repeat['status'] == 'EXACT_RETRY_NO_EFFECT' and s.refs() == before_retry, 'APPEND_RETRY_EFFECT')
                        diagnostic_mark(results, 'APPEND_RETRY', completed='APP_RETRY')
                        diagnostic_mark(results, 'C02_NEGATIVES')
                        stale = expect_owner_refusal(s, 'APPEND_STAYS_STALE', owner.require_current_generation_join_v1, STALE, s.context)
                        census_refusal = expect_owner_refusal(s, 'RETAINED_INCOMPLETE_CENSUS_NEGATIVE', owner.run_c02_correction_v1,
                            'C02 fresh transition requires a complete source census including its prior adjudication',
                            s.context, appended['record_oid'])
                        # Existing owner only: publish its now-complete census while
                        # requesting APPEND_ONLY. This does NOT request the fresh grant.
                        refreshed = owned(s, 'APPEND_ONLY_COMPLETE_CENSUS_REFRESH', owner.materialize_c02_owner_revisions_v1,
                            s.context, token, proposal)
                        require(refreshed['status'] == 'OWNER_REVISIONS_MATERIALIZED'
                                and refreshed['effect'] == 'APPEND_ONLY_NO_CURRENTNESS'
                                and refreshed['grant_oid'] == first['grant_oid'], 'APPEND_ONLY_REFRESH_NOT_DISTINCT')
                        refs_before_denial, allocation_before_denial = s.refs(), allocation_tree(s)
                        missing = expect_owner_refusal(s, 'DISTINCT_FRESH_GRANT_ABSENT', owner.run_c02_correction_v1,
                            MISSING_FRESH, s.context, appended['record_oid'])
                        require(s.refs() == refs_before_denial and allocation_tree(s) == allocation_before_denial,
                                'MISSING_FRESH_GRANT_NEGATIVE_ALLOCATED_OR_PUBLISHED')
                        write(s.evidence / 'MISSING_FRESH_GRANT_REFUSAL.json', {'refusal': missing,
                            'ref_snapshot': refs_before_denial, 'scoped_allocation_snapshot': allocation_before_denial,
                            'ref_and_allocation_snapshots_unchanged': True, 'append_only_refresh': refreshed,
                            'prior_incomplete_census_refusal_separately_labeled': census_refusal})
                        diagnostic_mark(results, 'C02_NEGATIVES', completed='NEGATIVE')
                        diagnostic_mark(results, 'FRESH_GRANT')
                        fresh = owned(s, 'DISTINCT_FRESH_GRANT_MATERIALIZATION', owner.materialize_c02_owner_revisions_v1,
                            s.context, token, proposal, correction_record_oid=appended['record_oid'])
                        require(fresh['status'] == 'OWNER_REVISIONS_MATERIALIZED'
                                and fresh['effect'] == 'C02_FRESH_TRANSITION'
                                and fresh['grant_oid'] != refreshed['grant_oid'], 'FRESH_GRANT_NOT_DISTINCT')
                        diagnostic_mark(results, 'FRESH_GRANT', completed='FRESH_GRANT')
                        diagnostic_mark(results, 'CORRECTION')
                        corrected = owned(s, 'CORRECT_FRESH', owner.run_c02_correction_v1, s.context, appended['record_oid'])
                        require(corrected['status'] == 'CORRECTED_FRESH', 'CORRECTED_STATUS')
                        diagnostic_mark(results, 'CORRECTION', completed='CORRECT')
                        before_retry = s.refs()
                        diagnostic_mark(results, 'CORRECTION_RETRY')
                        retry = owned(s, 'CORRECT_EXACT_RETRY', owner.run_c02_correction_v1, s.context, appended['record_oid'])
                        require(retry['status'] == 'ALREADY_CORRECTED' and s.refs() == before_retry, 'CORRECTION_RETRY_EFFECT')
                        diagnostic_mark(results, 'CORRECTION_RETRY', completed='CORR_RETRY')
                        actual = owned(s, 'CORRECTED_CURRENT_JOIN', owner.require_current_generation_join_v1, s.context)
                        require(actual['marker_oid'] == joined['marker_oid']
                                and actual['protected_manifest']['PRESERVED_PAYLOAD']['payload']
                                    == joined['protected_manifest']['PRESERVED_PAYLOAD']['payload'], 'CORRECTION_PAYLOAD_OR_MARKER_CHANGED')
                        results['c02'] = {'event_token': token, 'first_materialization': first, 'materialization_retry': again,
                            'append': appended, 'append_retry': repeat, 'append_stays_stale': stale,
                            'initial_incomplete_census_refusal': census_refusal, 'append_only_census_refresh': refreshed,
                            'missing_distinct_fresh_grant_refusal': missing, 'fresh_materialization': fresh,
                            'correction': corrected, 'correction_retry': retry, 'protected_payload_equal': True, 'marker_preserved': True}
                diagnostic_mark(results, 'CORRECTED_READBACK')
                corrected_request = public_corrected_request(s)
                results['corrected_cold_readback'] = receive(s, corrected_request)
                diagnostic_mark(results, 'CORRECTED_READBACK', completed='READBACK')
                results['corrected_cold_checkpoint_monotonic_ns'] = time.monotonic_ns()
                src.verify()
                # Genuine next request permanently withdraws the held source.
                # The later native boundary will be proved separately below.
                diagnostic_mark(results, 'LEASE_WITHDRAW')
                native_call(s, native, 'thread/read', {'threadId': tid, 'includeTurns': False})
                results['old_source_withdrawal'] = source_still_withdrawn(src)
                withdrew = True
        except ValueError as exc:
            require(withdrew and str(exc) == WITHDRAWN, 'UNEXPECTED_C02_SOURCE_CONTEXT_FAILURE')
            results['old_source_context_exit'] = str(exc)
        require(withdrew and results.get('old_source_context_exit') == WITHDRAWN, 'OLD_C02_CONTEXT_NOT_IRREVOCABLY_WITHDRAWN')
        diagnostic_mark(results, 'LEASE_WITHDRAW', completed='WITHDRAW')
        return corrected_request, src


def pending_tail(s, source, pending, native, provider, home, tid, rollout, corrected, old_src, results):
    plan = s.plan
    pre_source, pre_raw = snapshot(rollout, s.evidence / 'NATIVE_SOURCE_AFTER_CORRECTED_COLD_READBACK.jsonl')
    for wire in pre_raw.splitlines():
        row = decode(wire)
        require(not (row.get('type') == 'compacted' or
            row.get('type') == 'event_msg' and row.get('payload', {}).get('type') == 'context_compacted'),
            'PREEXISTING_NATIVE_COMPACTION_MARKER')
    protocol_path = OUTPUT / 'native/protocol.jsonl'
    protocol_prefix, _ = snapshot(protocol_path, s.evidence / 'PROTOCOL_BEFORE_LATER_BOUNDARY.jsonl')
    diagnostic_mark(results, 'LATER_COMPACT')
    provider.arm({'text': plan['compact_text'], 'usage': plan['compact_usage']})
    compaction_request = native_call(s, native, 'thread/compact/start', {'threadId': tid})
    compacted = completed_turn(s, native, tid)
    require(compacted['id'] != results['initial_completed_turn']['id'], 'COMPACTION_TURN_REUSED')
    diagnostic_mark(results, 'LATER_COMPACT', completed='COMPACT')
    diagnostic_mark(results, 'LATER_RESUME')
    provider.arm({'text': plan['resume_text'], 'usage': plan['resume_usage']})
    resume_started = native_call(s, native, 'turn/start', {'threadId': tid,
        'input': [{'type': 'text', 'text': plan['resume_prompt']}]})
    resumed = completed_turn(s, native, tid, resume_started['turn']['id'])
    require(resumed['id'] not in (compacted['id'], results['initial_completed_turn']['id']), 'RESUME_TURN_NOT_NEW')
    diagnostic_mark(results, 'LATER_RESUME', completed='RESUME')
    native_call(s, native, 'thread/read', {'threadId': tid, 'includeTurns': False})
    native.ledger.acquire().verify()  # Transport fence only; not a C02 interval.
    source_still_withdrawn(old_src)
    protocol_tail, _ = snapshot(protocol_path, s.evidence / 'PROTOCOL_AFTER_LATER_BOUNDARY.jsonl')
    after_source, after_raw = snapshot(rollout, s.evidence / 'NATIVE_SOURCE_AFTER_LATER_BOUNDARY.jsonl')
    require(after_source['physical'] == pre_source['physical'] and len(after_raw) > len(pre_raw)
            and after_raw[:len(pre_raw)] == pre_raw, 'LATER_SOURCE_NOT_APPEND_ONLY_ON_SAME_PHYSICAL_TRANSCRIPT')
    diagnostic_mark(results, 'LATER_REGISTER')
    store = OUTPUT / 'host-store'
    binding = s.scripts / 'host-session-binding.py'
    s.command(['/usr/bin/python3', '-I', '-B', binding, '--store', store, 'init', '--owner-id', plan['census_owner']])
    s.command(['/usr/bin/python3', '-I', '-B', binding, '--store', store, 'bind', '--owner-id', plan['census_owner'],
        '--host-id', 'codex', '--host-session-id', tid, '--controller-id', CONTROLLER,
        '--claim-id', s.context['claim_id'], '--explicit-run-root', s.run,
        '--repository-identity', s.repo, '--git-common-directory-identity', s.repo / '.git', '--worktree-identity', s.repo,
        '--activation-event-id', 'r5-c02-native-tail-actual-native',
        '--activation-receipt', corrected['corrected']['receipt_token'], '--continuity-generation', 'G0003',
        '--continuity-receipt', corrected['corrected']['receipt_token']])
    host_lookup = decode(s.command(['/usr/bin/python3', '-I', '-B', binding, '--store', store,
        'lookup', '--host-id', 'codex', '--host-session-id', tid]).stdout)
    def operate(label, action, request):
        return owned(s, label, pending.operate, store, tid, plan['census_owner'], action, request)
    with contextlib.chdir(s.repo):
        registered = operate('REGISTER_ACTUAL_LATER_SOURCE', 'register-source',
            {'task_id': tid, 'transcript': str(rollout), 'expected_bytes': after_source['bytes'], 'expected_sha256': after_source['sha256']})
        require(registered['status'] == 'SOURCE_REGISTERED_PHYSICAL_ONLY', 'SOURCE_NOT_REGISTERED_PHYSICALLY')
        diagnostic_mark(results, 'LATER_REGISTER', completed='REGISTER')
        state = pending.load(store, tid)
        require(state['source_problem'] is None and len(state['observations']) == 1 and not state['assignments'], 'LATER_SOURCE_SCOPE_AMBIGUOUS')
        row = next(iter(state['observations'].values()))
        proof = row['proof']
        require(row['id'] == 'boundary-' + sha(canonical(proof)) and row['kind'] == 'COMPLETED_RESUMED_BOUNDARY'
                and row['version'] == 1 and row['consumed_version'] == 0
                and proof['resume_turn'] == resumed['id']
                and proof['source']['physical'] == after_source['physical']
                and all(item['offset'] >= pre_source['bytes'] for item in proof['markers']), 'LATER_NATIVE_PROOF_NOT_NEW_OR_COMPLETE')
        status = pending.decision(state)
        require(status['decision'] == 'AUDIT_STATE_REQUIRED' and status['audit_state_required'], 'NEW_BOUNDARY_NOT_PENDING')
        diagnostic_mark(results, 'LATER_PENDING')
        reservation = operate('RESERVE_LOGICAL_PENDING_SCOPE', 'reserve', {'child_id': plan['logical_reservation']})
        observation = operate('OBSERVE_LOGICAL_PENDING_SCOPE', 'observe-child', {'child_id': plan['logical_reservation']})
        state = pending.load(store, tid)
        assignment = state['assignments'][plan['logical_reservation']]
        scope = [{'id': row['id'], 'kind': row['kind'], 'version': 1}]
        require(assignment['scope'] == scope and assignment['return'] is None and assignment['join'] is None
                and assignment['native_lifecycle'] == 'NOT_CLAIMED', 'PENDING_ASSIGNMENT_EXCEEDS_LOGICAL_SCOPE')
        require(state['observations'][row['id']]['consumed_version'] == 0, 'BOUNDARY_CONSUMED_WITHOUT_COGNITION')
        decision = pending.decision(state)
        require(decision['decision'] == 'WAIT_EXISTING_AUDIT' and decision['audit_state_required']
                and decision['state_dependent_decisions_held'] and decision['source_problem'] is None
                and decision['pending'] == scope, 'PENDING_AUDIT_STATE_NOT_HELD')
        write(s.evidence / 'LATER_PENDING_ADMISSION.json', {'registration': registered,
            'reservation': reservation, 'observation': observation, 'decision': decision,
            'source_boundary': row, 'logical_reservation_is_not_native_child': True})
        diagnostic_mark(results, 'LATER_PENDING', completed='PENDING')
    pending_path = store / 'compaction-audits-v1' / sha(tid.encode()) / 'pending.json'
    pending_raw, _ = read_regular(pending_path)
    pre_invalid_refs = s.refs()
    diagnostic_mark(results, 'LATER_INVALIDATE')
    newer = s.claim('--invalidate-continuity', CONTROLLER, '--boundary', 'host-reported-compaction',
        '--event', row['id']).stdout.decode().strip()
    require(re.fullmatch(r'[A-Za-z0-9/_-]+@[0-9a-f]{40}', newer) is not None, 'NEW_INVALIDATION_TOKEN_SHAPE')
    current = s.managed()
    require(all(current[name] == corrected['corrected_managed'][name] for name in ('controller', 'pointer', 'marker'))
            and current['invalidation'] == newer.split('@', 1)[1]
            and current['invalidation'] != corrected['corrected_managed']['invalidation'], 'LATER_INVALIDATION_EFFECT')
    diagnostic_mark(results, 'LATER_INVALIDATE', completed='INVALIDATE')
    request = copy.deepcopy(corrected)
    request.update(phase='later', refs=s.refs(), new_invalidation_token=newer, boundary_id=row['id'], thread_id=tid,
        logical_reservation=plan['logical_reservation'], census_owner=plan['census_owner'],
        pending_sha256=sha(pending_raw), rollout=after_source, pre_boundary_source=pre_source,
        resume_turn_id=resumed['id'], compact_turn_id=compacted['id'], protocol_prefix=protocol_prefix,
        protocol_after_boundary=protocol_tail,
        corrected_cold_checkpoint={
            'result_sha256': pin_small(OUTPUT / 'independent-corrected/RESULT.json')['sha256'],
            'request_sha256': results['corrected_cold_readback']['request_sha256'],
            'driver_observed_after_monotonic_ns': results['corrected_cold_checkpoint_monotonic_ns']},
        host_lookup=host_lookup)
    results['later_native'] = {'compaction_rpc_result_sha256': sha(canonical(compaction_request)),
        'completed_compaction_turn': compacted, 'completed_resumed_turn': resumed,
        'registered_source': after_source, 'pre_boundary_source': pre_source,
        'boundary_id': row['id'], 'new_invalidation_token': newer, 'prior_ref_snapshot': pre_invalid_refs,
        'pending_admission': decision, 'old_source_still_withdrawn': source_still_withdrawn(old_src)}
    diagnostic_mark(results, 'LATER_READBACK')
    results['later_cold_readback'] = receive(s, request)
    require(read_regular(pending_path)[0] == pending_raw, 'FINAL_PENDING_STATE_CHANGED')
    source_still_withdrawn(old_src)
    diagnostic_mark(results, 'LATER_READBACK', completed='RECEIVE')
    return request


def own_group_exists(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def shutdown(native, provider):
    """Bounded shutdown of only the objects/process group allocated by this run."""
    result = {'owned_native_process': None, 'provider': None, 'errors': []}
    if native is not None and hasattr(native, 'proc'):
        proc = native.proc
        try:
            result['owned_native_process'] = native.close()
        except BaseException as exc:
            result['errors'].append({'resource': 'native.close', 'type': type(exc).__name__, 'error': str(exc)})
        if own_group_exists(proc.pid):
            try:
                os.killpg(proc.pid, signal.SIGKILL)
                if proc.poll() is None:
                    proc.wait(timeout=3)
                deadline = time.monotonic() + 3
                while own_group_exists(proc.pid) and time.monotonic() < deadline:
                    time.sleep(0.05)
            except BaseException as exc:
                result['errors'].append({'resource': 'owned_process_group', 'type': type(exc).__name__, 'error': str(exc)})
        result['direct_process_reaped'] = proc.poll() is not None
        result['owned_process_group_absent'] = not own_group_exists(proc.pid)
        reader = getattr(native, 'reader', None)
        if reader is not None:
            reader.join(timeout=3)
        result['native_reader_stopped'] = reader is None or not reader.is_alive()
        for handle in (proc.stdin, proc.stdout, getattr(native, 'capture', None), getattr(native, 'stderr', None)):
            if handle is not None and not handle.closed:
                try:
                    handle.close()
                except BaseException as exc:
                    result['errors'].append({'resource': 'native_owned_handle', 'type': type(exc).__name__, 'error': str(exc)})
        result['native_handles_closed'] = all(handle is None or handle.closed for handle in
            (proc.stdin, proc.stdout, getattr(native, 'capture', None), getattr(native, 'stderr', None)))
    elif native is not None:
        for name in ('capture', 'stderr'):
            handle = getattr(native, name, None)
            if handle is not None:
                handle.close()
        result['native_not_started'] = True
    if provider is not None and hasattr(provider, 'server'):
        try:
            thread = getattr(provider, 'thread', None)
            if thread is not None and thread.is_alive():
                result['provider'] = provider.close()
            else:
                # shutdown() waits for serve_forever; a partial constructor may
                # have opened its socket but never started that thread.
                provider.release.set()
                provider.server.server_close()
                result['provider'] = {'provider_thread_joined': True, 'partial_constructor': True,
                    'request_count': len(provider.requests), 'remaining_armed_steps': provider.steps.qsize()}
        except BaseException as exc:
            result['errors'].append({'resource': 'provider.close', 'type': type(exc).__name__, 'error': str(exc)})
    elif provider is not None:
        result['provider_not_started'] = True
    if provider is not None and hasattr(provider, 'server'):
        result['provider_socket_closed'] = provider.server.socket.fileno() == -1
        result['provider_thread_stopped'] = not getattr(provider, 'thread', None) or not provider.thread.is_alive()
    return result


def execute(go_sha):
    # These reads precede ALL subject probing, directories, owner imports, binary
    # extraction, sockets, native launch and resource-limit changes.
    go = gate(go_sha)
    manifest, inputs, identities, manifest_raw = verify_inputs(full=True)
    require(gate(go_sha) == go, 'AUTHORIZATION_CHANGED_BEFORE_ALLOCATION')
    require(not os.path.lexists(SUBJECT), 'PROSPECTIVE_SUBJECT_ALREADY_EXISTS_NO_RETRY')
    OUTPUT.mkdir(mode=0o700, exist_ok=False)  # One-shot allocation boundary.
    results = {'status': 'IN_PROGRESS', 'root_go_sha256': go['sha256'], 'preparation_sha256': go['seal_sha256'],
        'independent_review_sha256': go['review_sha256'], 'input_manifest_sha256': INPUT_SHA256,
        'original_acceptance': False, 'original_OR_award': False, 'closure': False, 'release': False,
        'provider_text_and_usage': 'EXPLICIT_LOCAL_EMULATION', 'native_result_JOIN': False,
        'automatic_retry': False, 'resources_and_evidence_retained_at': str(OUTPUT)}
    write(OUTPUT / 'ATTEMPT.json', results)
    diagnostic_mark(results, 'AUTHORIZED')
    s = native = provider = None
    error = None
    def expiry(signum, frame):
        raise TimeoutError('ONE_SHOT_OPERATION_WATCHDOG')
    signal.signal(signal.SIGALRM, expiry)
    signal.setitimer(signal.ITIMER_REAL, 900)
    try:
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        diagnostic_mark(results, 'SUBJECT_INIT')
        s = FreshSubject.__new__(FreshSubject)
        FreshSubject.__init__(s, manifest, inputs, identities, manifest_raw, go)
        diagnostic_mark(results, 'SUBJECT_INIT', completed='INIT')
        s.owner_steps = []
        s.plan = decode(inputs['protocol-plan'])
        diagnostic_mark(results, 'ROTATION')
        rotation = decode(s.claim('--rotate-canonical-state', CONTROLLER, '--owner-map', s.owner_map).stdout)
        require(rotation['status'] == 'ROTATED', 'INITIAL_ROTATION_STATUS')
        results['initial_rotation'] = rotation
        diagnostic_mark(results, 'ROTATION', completed='ROTATE')
        diagnostic_mark(results, 'SOURCE_LOAD')
        source = load(s.scripts / 'compaction-source-owner-codex-app.py', 'r5_c02_tail_fixed_source_owner')
        pending = load(s.scripts / 'compaction-audit-pending.py', 'r5_c02_tail_existing_pending_owner')
        diagnostic_mark(results, 'BINARY_EXTRACT')
        binary = extract_owned_binary(s)
        diagnostic_mark(results, 'BINARY_VERSION')
        version = s.command([binary, '--version']).stdout.decode().strip()
        require(version == s.plan['native_version'], 'OFFICIAL_BINARY_VERSION')
        diagnostic_mark(results, 'BINARY_VERSION', completed='BIN')
        diagnostic_mark(results, 'PROVIDER_SETUP')
        transport = load(OUTPUT / 'support/native_transport.py', 'r5_c02_tail_pinned_transport')
        responses = load(OUTPUT / 'support/local_responses_canary.py', 'r5_c02_tail_pinned_emulated_provider')
        home = OUTPUT / 'home'
        home.mkdir(mode=0o700)
        provider = responses.Provider.__new__(responses.Provider)
        responses.Provider.__init__(provider, OUTPUT / 'provider')
        require(provider.url.startswith('http://127.0.0.1:'), 'PROVIDER_NOT_EXCLUSIVE_LOOPBACK')
        results['native_config_sha256'] = configure_native(home, provider, s.plan)
        s.copied[str(home / 'config.toml')] = {'raw': read_regular(home / 'config.toml')[0], 'mode': 0o600}
        os.chmod(home / 'config.toml', 0o600)
        diagnostic_mark(results, 'PROVIDER_SETUP', completed='PROVIDER')
        diagnostic_mark(results, 'NATIVE_LAUNCH')
        native = transport.Native.__new__(transport.Native)
        transport.Native.__init__(native, binary, home, s.repo, OUTPUT / 'native', ledger_factory=source.FreshCanaryQuiescenceV1)
        diagnostic_mark(results, 'NATIVE_LAUNCH', completed='NATIVE')
        diagnostic_mark(results, 'NATIVE_INIT')
        results['initialize'] = native_call(s, native, 'initialize', {'clientInfo':
            {'name': 'r5_c02_native_tail_actual_controlled_canary', 'version': 'r5'}, 'capabilities': {'experimentalApi': True}})
        native.send({'method': 'initialized', 'params': {}})
        diagnostic_mark(results, 'NATIVE_INIT', completed='RPC_INIT')
        diagnostic_mark(results, 'THREAD_START')
        started = native_call(s, native, 'thread/start', {'cwd': str(s.repo), 'model': s.plan['model'],
            'modelProvider': s.plan['provider'], 'approvalPolicy': 'never', 'sandbox': 'read-only',
            'environments': [], 'ephemeral': False})
        tid, rollout = started['thread']['id'], Path(started['thread']['path'])
        require(isinstance(tid, str) and tid and rollout.is_relative_to(home / 'sessions'), 'FRESH_NATIVE_THREAD_SCOPE')
        results['native_thread_id'] = tid
        diagnostic_mark(results, 'THREAD_START', completed='THREAD')
        diagnostic_mark(results, 'SEED_TURN')
        provider.arm({'text': s.plan['initial_text'], 'usage': s.plan['initial_usage']})
        initial = native_call(s, native, 'turn/start', {'threadId': tid,
            'input': [{'type': 'text', 'text': s.plan['initial_prompt']}]})
        results['initial_completed_turn'] = completed_turn(s, native, tid, initial['turn']['id'])
        native_call(s, native, 'thread/read', {'threadId': tid, 'includeTurns': False})
        native.ledger.acquire().verify()
        diagnostic_mark(results, 'SEED_TURN', completed='SEED')
        diagnostic_mark(results, 'SOURCE_SELECT')
        configured, code, runtime = fixed_selection(s, source, pending, native, home, tid, rollout)
        diagnostic_mark(results, 'SOURCE_SELECT', completed='SELECT')
        diagnostic_mark(results, 'C02_INTERVAL')
        corrected, old_src = controlled_transaction(s, source, pending, native, tid, configured, code, runtime, results)
        later = pending_tail(s, source, pending, native, provider, home, tid, rollout, corrected, old_src, results)
        results['post_tail_refs'] = later['refs']
        results['post_tail_pending_sha256'] = later['pending_sha256']
        results['status'] = 'PENDING_CLEANUP_AND_FINAL_INPUT_VERIFICATION'
        results['scope'] = 'FRESH_CONTROLLED_C02_PLUS_NEW_LATER_NATIVE_BOUNDARY_ADMITTED_PENDING'
        results['expected_final_currentness'] = 'STALE_AFTER_NEWER_BOUNDARY_EXPECTED'
        results['audit_state_required'] = True
        results['boundary_consumed_version'] = 0
        results['native_lifecycle'] = 'NOT_CLAIMED'
        diagnostic_mark(results, 'CLEANUP')
    except BaseException as exc:
        error = exc
        results.update(status='FAIL_PRESERVED_NO_RETRY', error_type=type(exc).__name__, error=str(exc),
                       traceback=traceback.format_exc())
        diagnostic_failure(results, exc, native=native)
        diagnostic_mark(results, 'CLEANUP')
    finally:
        signal.setitimer(signal.ITIMER_REAL, 40)
        try:
            results['shutdown'] = shutdown(native, provider)
            # Always capture the binary after owned shutdown, including when a
            # later cleanup/input assertion fails. Defer ordinary custody
            # refusal until the original cleanup/input checks have run.
            binary_custody_error = None
            if s is not None and hasattr(s, 'binary_pin'):
                try:
                    results['final_binary_custody'] = check_binary_custody(s, 'finalization_after_shutdown',
                        'OWNED_BINARY_CHANGED_DURING_EXECUTION', full=True)
                except BaseException as exc:
                    results['final_binary_custody_failure'] = {'error_type': type(exc).__name__, 'error': str(exc)}
                    if isinstance(exc, (TimeoutError, KeyboardInterrupt, SystemExit)):
                        raise
                    binary_custody_error = exc
            clean = results['shutdown']
            if native is not None and hasattr(native, 'proc'):
                require(clean.get('direct_process_reaped') and clean.get('owned_process_group_absent')
                        and clean.get('native_reader_stopped') and clean.get('native_handles_closed')
                        and not clean['errors'], 'OWNED_NATIVE_CLEANUP_INCOMPLETE')
            require(not clean['errors'], 'RESOURCE_CLEANUP_FAILED')
            if provider is not None and hasattr(provider, 'server'):
                require(clean.get('provider_socket_closed') and clean.get('provider_thread_stopped'), 'PROVIDER_CLEANUP_INCOMPLETE')
                if error is None:
                    require(clean['provider']['request_count'] == 3 and clean['provider']['remaining_armed_steps'] == 0,
                            'UNEXPECTED_PROVIDER_REQUEST_OR_STEP_COUNT')
            diagnostic_mark(results, 'CLEANUP', completed='CLEANUP', native=native)
            diagnostic_mark(results, 'INPUT_VERIFY')
            if s is not None:
                s.check_bindings(full=True)
                if binary_custody_error is not None:
                    raise binary_custody_error
                if error is None:
                    require(s.refs() == results['post_tail_refs'], 'POST_SHUTDOWN_REFS_CHANGED')
                    pending_path = OUTPUT / 'host-store/compaction-audits-v1' / sha(results['native_thread_id'].encode()) / 'pending.json'
                    require(sha(read_regular(pending_path)[0]) == results['post_tail_pending_sha256'], 'POST_SHUTDOWN_PENDING_CHANGED')
            else:
                final_manifest, final_inputs, final_identities, final_raw = verify_inputs(full=True)
                require((final_manifest, final_inputs, final_identities, final_raw)
                        == (manifest, inputs, identities, manifest_raw) and gate(go_sha) == go,
                        'INPUTS_CHANGED_AFTER_EARLY_FAILURE')
            results['post_input_verification'] = 'PASS'
            diagnostic_mark(results, 'INPUT_VERIFY', completed='INPUTS')
            if error is None:
                diagnostic_mark(results, 'COMPLETE')
                results['status'] = 'PASS'
        except BaseException as exc:
            if error is None:
                error = exc
            results.update(status='FAIL_PRESERVED_NO_RETRY', finalization_error_type=type(exc).__name__, finalization_error=str(exc))
            diagnostic_failure(results, exc, finalization=True, native=native)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            write(OUTPUT / 'RESULT.json', results)
    print(json.dumps({'status': results['status'], 'output': str(OUTPUT),
        'original_acceptance': False, 'pending_audit_required': results.get('audit_state_required', 'NOT_REACHED')}, sort_keys=True))
    if error is not None:
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--prepare-check', action='store_true', help='Pure pinned-input/AST checks only; default mode.')
    modes.add_argument('--execute', action='store_true', help='One-shot execution; exact independent review and root GO mandatory.')
    parser.add_argument('--go-sha256', help='Exact SHA256 of the root-created ROOT_GO.json; never inferred.')
    args = parser.parse_args()
    if args.execute:
        return execute(args.go_sha256)
    require(args.go_sha256 is None, 'GO_NOT_USED_IN_PREPARATION')
    print(json.dumps(prepare_check(), sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
