#!/usr/bin/python3
"""Independent bounded receiver. No writes to subject/store, RPC, JOIN, or resume.

Standalone execution is gated by the same sealed preparation, independent review,
and exact root GO as the prospective runner. Writes are only receiver evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time

sys.dont_write_bytecode = True
BASE = Path('/UNBOUND_C02_06_PARENT')
LANE = Path('/UNBOUND_C02_06_PACKET')
SUBJECT = Path('/tmp/dg18-isolated-c02-20261106-01')
CONTROLLER = 'dg18-isolated-c02-20261106-01'
OWNED_BINARY = Path('/tmp/dg18-isolated-c02-bin-20261106-01/codex')
INPUT_SHA256 = 'UNBOUND_PENDING_HOST_PREPARATION'
SOURCE_HEAD = '35bf9823856eb4efe254b882954120480632230e'
SOURCE_TREE = 'abe08aabc83de3b27c43e6acf28646fb089f0f34'
ENV = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'LANG': 'C', 'TZ': 'UTC',
       'PYTHONDONTWRITEBYTECODE': '1', 'IMPLEMENTAUDIT_PYTHON': '/usr/bin/python3',
       'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null',
       'GIT_CONFIG_SYSTEM': '/dev/null', 'GIT_OPTIONAL_LOCKS': '0', 'GIT_TERMINAL_PROMPT': '0'}


def need(ok, reason):
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
            need(key not in result, 'DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def read(path, maximum=4 * 1024 * 1024):
    path = Path(path)
    need(path.is_absolute(), 'NON_ABSOLUTE_READ')
    for component in (path, *path.parents):
        st = component.lstat()
        need(not stat.S_ISLNK(st.st_mode), 'SYMLINK_READ')
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= maximum,
         'UNSAFE_OR_OVERSIZED_FILE')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        with os.fdopen(fd, 'rb') as stream:
            raw = stream.read(maximum + 1)
            opened = os.fstat(stream.fileno())
    finally:
        pass
    after = path.lstat()
    stamp = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    need(len(raw) <= maximum and stamp(before) == stamp(opened) == stamp(after), 'FILE_CHANGED_DURING_READ')
    return raw, stamp(after)


def write(path, value):
    raw = value if isinstance(value, bytes) else canonical(value) + b'\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)


def gate(go_sha):
    need(bool(re.fullmatch('[0-9a-f]{64}', go_sha)), 'EXACT_ROOT_GO_SHA_REQUIRED')
    raw, go_identity = read(LANE / 'ROOT_GO.json', 65536)
    need(sha(raw) == go_sha, 'ROOT_GO_CHANGED')
    go = decode(raw)
    seal_raw, seal_identity = read(LANE / 'SEALED_PREPARATION.json')
    seal = decode(seal_raw)
    required = {'schema': 'implementaudit.r5.c02-native-tail-root-go.v1', 'author': '/root', 'decision': 'GO',
        'subject': str(SUBJECT), 'controller': CONTROLLER, 'owned_binary': str(OWNED_BINARY),
        'preparation_sha256': sha(seal_raw),
        'source_commit': SOURCE_HEAD, 'source_tree': SOURCE_TREE, 'one_shot': True,
        'allocation_authorized': ['fresh-subject', 'fresh-controller', 'owned-binary-copy', 'one-native-app-server',
                                  'one-loopback-emulated-provider', 'local-emulated-MCP', 'existing-host-store',
                                  'controlled-C02', 'one-later-native-compaction-resume', 'independent-readback']}
    need(all(go.get(k) == v for k, v in required.items()), 'ROOT_GO_SCOPE')
    review_raw, review_identity = read(LANE / 'INDEPENDENT_TECHNICAL_REVIEW.json')
    review = decode(review_raw)
    need(sha(review_raw) == go['independent_review_sha256']
         and review['schema'] == 'implementaudit.r5.c02-native-tail-independent-review.v1'
         and review['decision'] == 'PASS' and review['blocking_findings'] == []
         and review['preparation_sha256'] == sha(seal_raw)
         and isinstance(review['reviewer'], str) and review['reviewer'].startswith('/root/')
         and review['reviewer'] not in ('/root/r5_c02_successor_prepare', '/root/h0_c02_or') and review['reviewer'] == '/root/c02_cold_review', 'INDEPENDENT_REVIEW_SCOPE')
    need(seal['schema'] == 'implementaudit.r5.c02-native-tail-sealed-preparation.v1'
         and seal['authority'] == 'PREPARATION_ONLY' and seal['input_manifest_sha256'] == INPUT_SHA256,
         'PREPARATION_SEAL_SCOPE')
    names, identities = set(), {}
    for item in seal['files']:
        path = LANE / item['name']
        need(path.parent == LANE and item['name'] not in names, 'SEALED_PATH_SCOPE')
        names.add(item['name'])
        data, identity = read(path)
        need(len(data) == item['bytes'] and sha(data) == item['sha256']
             and stat.S_IMODE(identity[2]) == item['mode'], 'SEALED_FILE_CHANGED')
        identities[item['name']] = list(identity)
    need({'c02_native_tail.py', 'receive_tail.py', 'INPUT_MANIFEST.json', 'PROTOCOL_PLAN.json',
          'DESIGN.md', 'VERIFICATION.json'} <= names, 'SEALED_PREPARATION_INCOMPLETE')
    return {'go': sha(raw), 'review': sha(review_raw), 'seal': sha(seal_raw),
            'go_identity': list(go_identity), 'review_identity': list(review_identity),
            'seal_identity': list(seal_identity), 'sealed_identities': identities}


def verify_native_protocol(request, authorization):
    """Read only actual recorded stdio; this function sends no RPC or event."""
    pin = request['protocol_after_boundary']
    prefix = request['protocol_prefix']
    expected_path = LANE / 'operation/native/protocol.jsonl'
    need(pin['path'] == prefix['path'] == str(expected_path), 'PROTOCOL_PATH_SCOPE')
    raw, identity = read(expected_path, 32 * 1024 * 1024)
    physical = {'device': identity[0], 'inode': identity[1]}
    need(physical == pin['physical'] == prefix['physical'] and len(raw) == pin['bytes']
         and sha(raw) == pin['sha256'] and raw.endswith(b'\n'), 'PROTOCOL_EXACT_CUTOFF')
    cut = prefix['bytes']
    need(type(cut) is int and 0 < cut < len(raw) and raw[cut - 1:cut] == b'\n'
         and sha(raw[:cut]) == prefix['sha256'], 'PROTOCOL_PREFIX_CHANGED')
    cold = request['corrected_cold_checkpoint']
    cold_raw, _ = read(LANE / 'operation/independent-corrected/RESULT.json')
    cold_request_raw, _ = read(LANE / 'operation/READBACK_CORRECTED_REQUEST.json')
    need(sha(cold_raw) == cold['result_sha256'] and sha(cold_request_raw) == cold['request_sha256'],
         'CORRECTED_COLD_CHECKPOINT_CHANGED')
    cold_result, cold_request = decode(cold_raw), decode(cold_request_raw)
    need(cold_result['status'] == 'PASS' and cold_result['phase'] == 'corrected'
         and cold_result['canonical_currentness'] == 'CURRENT_CORRECTED_G0003'
         and cold_result['authorization'] == authorization
         and cold_request['corrected'] == request['corrected']
         and cold_request['corrected_managed'] == request['corrected_managed']
         and cold_request['runtime_pins'] == request['runtime_pins'], 'CORRECTED_COLD_CHECKPOINT_SCOPE')
    rows, offset, prior_mono = [], 0, 0
    for sequence, wire in enumerate(raw.splitlines(keepends=True), 1):
        value = decode(wire)
        need(set(value) == {'sequence', 'monotonic_ns', 'direction', 'value'}
             and value['sequence'] == sequence and type(value['monotonic_ns']) is int
             and value['monotonic_ns'] > prior_mono, 'PROTOCOL_SEQUENCE_OR_TIME')
        prior_mono = value['monotonic_ns']
        value['offset'] = offset
        rows.append(value)
        offset += len(wire)
    need(rows and rows[0]['direction'] == 'lifecycle' and rows[0]['value']['event'] == 'started',
         'PROTOCOL_NATIVE_START')
    lifecycle = rows[0]['value']
    need(lifecycle['argv'] == [str(OWNED_BINARY), 'app-server', '--listen', 'stdio://']
         and lifecycle['cwd'] == str(SUBJECT) and lifecycle['home'] == str(LANE / 'operation/home')
         and type(lifecycle['pid']) is int and lifecycle['pid'] > 0, 'SAME_OWNED_NATIVE_PROCESS')
    need(all(row['direction'] in ('send', 'recv_raw') for row in rows[1:]), 'NATIVE_PROTOCOL_INTERRUPTION')
    sends = [row for row in rows if row['direction'] == 'send']
    receives = []
    for row in rows:
        if row['direction'] == 'recv_raw':
            need(isinstance(row['value'], str) and row['value'].endswith('\n'), 'NATIVE_WIRE_LINE')
            obj = decode(row['value'])
            need(isinstance(obj, dict), 'NATIVE_WIRE_OBJECT')
            receives.append((row, obj))
    thread_starts = [row for row in sends if row['value'].get('method') == 'thread/start']
    need(len(thread_starts) == 1 and thread_starts[0]['offset'] < cut, 'ONE_SAME_NATIVE_THREAD')
    def response(send):
        matches = [(row, obj) for row, obj in receives if obj.get('id') == send['value']['id'] and 'method' not in obj]
        need(len(matches) == 1 and matches[0][0]['sequence'] > send['sequence']
             and 'result' in matches[0][1] and 'error' not in matches[0][1], 'NATIVE_RPC_RESPONSE_IDENTITY')
        return matches[0]
    _, start_response = response(thread_starts[0])
    need(start_response['result']['thread']['id'] == request['thread_id'], 'NATIVE_THREAD_IDENTITY')
    tail_sends = [row for row in sends if row['offset'] >= cut]
    need([row['value'].get('method') for row in tail_sends] == ['thread/compact/start', 'turn/start', 'thread/read'],
         'EXACT_LATER_NATIVE_RPC_SEQUENCE')
    compact, resumed, fence = tail_sends
    plan = decode(read(LANE / 'PROTOCOL_PLAN.json')[0])
    need(compact['value']['params'] == {'threadId': request['thread_id']}
         and resumed['value']['params'] == {'threadId': request['thread_id'],
             'input': [{'type': 'text', 'text': plan['resume_prompt']}]}
         and fence['value']['params'] == {'threadId': request['thread_id'], 'includeTurns': False},
         'LATER_NATIVE_RPC_SCOPE')
    compact_reply, _ = response(compact)
    resume_reply, resume_value = response(resumed)
    fence_reply, fence_value = response(fence)
    need(resume_value['result']['turn']['id'] == request['resume_turn_id']
         and fence_value['result']['thread']['id'] == request['thread_id'], 'RESUME_AND_FENCE_THREAD_IDENTITY')
    def completed(turn_id):
        matches = [(row, obj) for row, obj in receives if obj.get('method') == 'turn/completed'
            and obj.get('params', {}).get('threadId') == request['thread_id']
            and obj['params'].get('turn', {}).get('id') == turn_id]
        need(len(matches) == 1 and matches[0][1]['params']['turn']['status'] == 'completed', 'ACTUAL_COMPLETED_NATIVE_TURN')
        return matches[0][0]
    compact_done, resume_done = completed(request['compact_turn_id']), completed(request['resume_turn_id'])
    need(compact['sequence'] < compact_reply['sequence'] < compact_done['sequence'] < resumed['sequence']
         < resume_reply['sequence'] < resume_done['sequence'] < fence['sequence'] < fence_reply['sequence'],
         'NATIVE_COMPLETION_RESUME_FENCE_ORDER')
    need(cold_result['finished_monotonic_ns'] <= cold['driver_observed_after_monotonic_ns'] < compact['monotonic_ns'],
         'BOUNDARY_NOT_GENUINELY_LATER_THAN_CORRECTED_COLD_READBACK')
    withdrawal = [row for row in sends if row['offset'] < cut
        and row['monotonic_ns'] > cold['driver_observed_after_monotonic_ns']]
    need(len(withdrawal) == 1 and withdrawal[0]['value']['method'] == 'thread/read'
         and withdrawal[0]['value']['params'] == {'threadId': request['thread_id'], 'includeTurns': False},
         'OLD_INTERVAL_WITHDRAWAL_REQUEST_ABSENT')
    response(withdrawal[0])
    return {'source': pin, 'prefix_bytes': cut, 'prefix_sha256': prefix['sha256'],
        'native_pid': lifecycle['pid'], 'thread_id': request['thread_id'],
        'corrected_cold_result_sha256': cold['result_sha256'],
        'compact_request_sequence': compact['sequence'], 'compact_completed_sequence': compact_done['sequence'],
        'resumed_request_sequence': resumed['sequence'], 'resumed_completed_sequence': resume_done['sequence'],
        'read_fence_response_sequence': fence_reply['sequence'], 'captured_rows': len(rows),
        'same_native_process_and_thread': True, 'genuinely_later_than_corrected_cold_checkpoint': True}


def payload(raw):
    parts = raw.split(b'```json\n')
    need(len(parts) == 2 and b'\n```' in parts[1], 'CANONICAL_BODY_FENCE')
    return decode(parts[1].split(b'\n```', 1)[0])['payload']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--go-sha256', required=True)
    args = parser.parse_args()
    authorization = gate(args.go_sha256)  # FIRST: no subject/store reads before this.
    request_raw, request_identity = read(args.request)
    request = decode(request_raw)
    phase = request['phase']
    need(phase in ('corrected', 'later') and request['subject'] == str(SUBJECT)
         and request['controller'] == CONTROLLER, 'READER_SUBJECT_SCOPE')
    need(args.request == LANE / 'operation' / ('READBACK_' + phase.upper() + '_REQUEST.json'), 'REQUEST_PATH_SCOPE')
    out = LANE / 'operation' / ('independent-' + phase)
    need(not out.exists(), 'ONE_SHOT_READER_OUTPUT_EXISTS')
    out.mkdir()
    result = {'status': 'IN_PROGRESS', 'phase': phase, 'authorization': authorization,
              'read_only_subject': True, 'native_RPC': False, 'native_JOIN': False,
              'automatic_retry': False, 'original_acceptance': False, 'started_monotonic_ns': time.monotonic_ns()}
    commands = []
    current_child = None
    def expiry(signum, frame):
        raise TimeoutError('INDEPENDENT_READBACK_WATCHDOG_180S')
    signal.signal(signal.SIGALRM, expiry)
    signal.signal(signal.SIGTERM, lambda signum, frame: (_ for _ in ()).throw(RuntimeError('READER_PARENT_TERMINATION')))
    signal.setitimer(signal.ITIMER_REAL, 180)
    scripts = SUBJECT / 'skills/implementaudit/scripts'
    env = dict(ENV, TMPDIR=str(SUBJECT / '.task-tmp'))
    def command(argv, success=True):
        nonlocal current_child
        n = len(commands) + 1
        start = time.monotonic_ns()
        current_child = subprocess.Popen(list(map(str, argv)), cwd=SUBJECT, env=env,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        stdout = stderr = b''
        interrupted = None
        try:
            stdout, stderr = current_child.communicate(timeout=45)
        except BaseException as exc:
            interrupted = exc
            if current_child.poll() is None:
                os.killpg(current_child.pid, signal.SIGKILL)
            try:
                stdout, stderr = current_child.communicate(timeout=5)
            except BaseException:
                pass
        finally:
            rc = current_child.returncode
            current_child = None
        need(len(stdout) + len(stderr) <= 8 * 1024 * 1024, 'COMMAND_OUTPUT_BOUND')
        write(out / f'{n:03d}.stdout', stdout)
        write(out / f'{n:03d}.stderr', stderr)
        row = {'sequence': n, 'argv': list(map(str, argv)), 'returncode': rc,
               'elapsed_ms': (time.monotonic_ns() - start) / 1e6,
               'stdout_sha256': sha(stdout), 'stderr_sha256': sha(stderr)}
        row['interrupted'] = interrupted is not None
        commands.append(row)
        if interrupted is not None:
            raise interrupted
        need(not success or rc == 0, 'READ_COMMAND_FAILED_' + str(n))
        return rc, stdout, stderr
    def claim(*argv, success=True):
        return command(['/usr/bin/bash', scripts / 'claim-run.sh', *argv], success)
    def git(*argv):
        return command(['/usr/bin/git', *argv])[1]
    def refs():
        rows = git('for-each-ref', '--format=%(refname) %(objectname)', 'refs/implementaudit/').decode().splitlines()
        need(len(rows) <= 128, 'REF_BOUND')
        return dict(row.split(' ', 1) for row in rows)
    try:
        for item in request['runtime_pins']:
            p = Path(item['path'])
            need(p.is_relative_to(SUBJECT), 'RUNTIME_PIN_SCOPE')
            raw, identity = read(p)
            need(sha(raw) == item['sha256'] and len(raw) == item['bytes']
                 and stat.S_IMODE(identity[2]) == item['mode'], 'RUNTIME_PIN_CHANGED')
        before = refs()
        need(before == request['refs'], 'REF_SNAPSHOT_CHANGED_BEFORE_READ')
        need(git('rev-parse', 'HEAD').decode().strip() == request['subject_head']
             and git('rev-parse', 'HEAD^{tree}').decode().strip() == request['subject_tree'], 'SUBJECT_REVISION_CHANGED')
        receipt = request['corrected']['receipt_token']
        pointer_token = request['corrected']['pointer_token']
        for name in ('pointer', 'marker', 'controller'):
            need(before[request['refs_names'][name]] == request['corrected_managed'][name], 'CORRECTED_IDENTITY_CHANGED_' + name)
        if phase == 'corrected':
            resolved = decode(claim('--resolve-canonical-generation', CONTROLLER)[1])
            need(resolved == request['corrected'], 'PUBLIC_CORRECTED_RESOLUTION_CHANGED')
            need(claim('--require-current-continuity', CONTROLLER)[1].decode().strip() == receipt, 'CORRECTED_CURRENTNESS')
            need(claim('--verify-resume-receipt', receipt)[1].decode().strip() == receipt, 'CORRECTED_RECEIPT')
            roles = {role: claim('--read-canonical-state', CONTROLLER, '--role', role,
                '--expected-pointer', pointer_token)[1] for role in ('STATE', 'ROADMAP')}
            result['canonical_currentness'] = 'CURRENT_CORRECTED_G0003'
        else:
            refusals = {}
            for label, argv in [
                ('require', ['--require-current-continuity', CONTROLLER]),
                ('resolve', ['--resolve-canonical-generation', CONTROLLER]),
                ('verify_corrected_receipt', ['--verify-resume-receipt', receipt]),
                ('read_canonical_state', ['--read-canonical-state', CONTROLLER, '--role', 'STATE', '--expected-pointer', pointer_token])]:
                rc, stdout, stderr = claim(*argv, success=False)
                need(rc != 0 and b'current generation is stale after a newer boundary' in stderr + stdout,
                     'MISSING_EXACT_STALE_REFUSAL_' + label)
                refusals[label] = {'returncode': rc, 'stdout_sha256': sha(stdout), 'stderr_sha256': sha(stderr)}
            pre_resume = decode(claim('--resolve-resume-generation', CONTROLLER)[1])
            need(pre_resume['status'] == 'PRE_RESUME_EVIDENCE' and pre_resume['pointer_token'] == pointer_token
                 and pre_resume['invalidation_token'] == request['new_invalidation_token']
                 and pre_resume['receipt_token'] == receipt and pre_resume['boundary'] == 'host-reported-compaction',
                 'PUBLIC_PRE_RESUME_IDENTITY')
            roles = {role: claim('--read-resume-state', CONTROLLER, '--role', role,
                '--expected-pointer', pointer_token, '--expected-invalidation', request['new_invalidation_token'])[1]
                for role in ('STATE', 'ROADMAP')}
            result.update(canonical_currentness='STALE_AFTER_NEWER_BOUNDARY_EXPECTED',
                          stale_refusals=refusals, public_pre_resume_read_only=True)
        for role, raw in roles.items():
            need(sha(canonical(payload(raw))) == request['protected_role_payload_sha256'][role], 'PROTECTED_PAYLOAD_CHANGED_' + role)
            need(sha(raw) == request['corrected_role_sha256'][role], 'CORRECTED_ROLE_BYTES_CHANGED_' + role)
            write(out / (role + '.md'), raw)
        run = Path(request['run_root'])
        need(run.is_relative_to(SUBJECT / '.IMPLEMENTAUDIT/runs'), 'RUN_ROOT_SCOPE')
        for role in ('STATE', 'ROADMAP'):
            raw, _ = read(run / (role + '.md'))
            need(sha(raw) == request['legacy_role_sha256'][role], 'LEGACY_ROLE_CHANGED')
        for name, expected in request['canonical_artifacts'].items():
            p = Path(expected['path'])
            need(p.is_relative_to(run / 'state-generations'), 'CANONICAL_ARTIFACT_SCOPE')
            raw, identity = read(p)
            need(sha(raw) == expected['sha256'], 'CANONICAL_ARTIFACT_CHANGED_' + name)
            write(out / name, raw)
        receipt_blob = git('cat-file', 'blob', receipt.split('@', 1)[1])
        need(len(receipt_blob.rstrip(b'\n').split(b'\t')) == 14, 'RECEIPT_FIELD_COUNT')
        write(out / 'CORRECTED_RECEIPT.tsv', receipt_blob)
        objects = {}
        retained_bytes = 0
        for ref, oid in before.items():
            need(re.fullmatch('[0-9a-f]{40}', oid) is not None, 'REF_OID')
            if oid in objects:
                objects[oid]['refs'].append(ref)
                continue
            size = int(git('cat-file', '-s', oid))
            need(size <= 4 * 1024 * 1024 and retained_bytes + size <= 32 * 1024 * 1024, 'REF_OBJECT_BYTE_BOUND')
            typ = git('cat-file', '-t', oid).decode().strip()
            need(typ in ('blob', 'tree', 'commit'), 'UNEXPECTED_OBJECT_KIND')
            raw = git('cat-file', typ, oid)
            need(len(raw) == size and hashlib.sha1(typ.encode() + b' ' + str(size).encode() + b'\0' + raw).hexdigest() == oid, 'OBJECT_BYTES_IDENTITY')
            write(out / 'ref-objects' / oid, raw)
            objects[oid] = {'type': typ, 'bytes': size, 'sha256': sha(raw), 'refs': [ref]}
            retained_bytes += size
        if phase == 'later':
            token = request['new_invalidation_token']
            ref, oid = token.split('@', 1)
            need(before[ref] == oid and oid != request['corrected_managed']['invalidation'], 'NEW_INVALIDATION_NOT_CURRENT_OR_NOT_NEW')
            actual = git('cat-file', 'blob', oid)
            expected = ('\t'.join(['implementaudit.continuity-invalidation.v1', CONTROLLER,
                request['corrected_managed']['controller'], request['claim_id'], 'host-reported-compaction', request['boundary_id']]) + '\n').encode()
            need(actual == expected, 'SOURCE_BOUND_INVALIDATION_BLOB')
            write(out / 'NEW_INVALIDATION.tsv', actual)
            store = LANE / 'operation/host-store'
            pending_path = store / 'compaction-audits-v1' / sha(request['thread_id'].encode()) / 'pending.json'
            pending_raw, pending_identity = read(pending_path)
            pending = decode(pending_raw)
            need(sha(pending_raw) == request['pending_sha256'] and pending['session_id'] == request['thread_id']
                 and pending['source_problem'] is None, 'PENDING_SNAPSHOT_IDENTITY')
            row = pending['observations'][request['boundary_id']]
            proof = row['proof']
            need(row['id'] == 'boundary-' + sha(canonical(proof)) and row['kind'] == 'COMPLETED_RESUMED_BOUNDARY'
                 and row['version'] == 1 and row['consumed_version'] == 0, 'PENDING_BOUNDARY_NOT_FRESH_UNCONSUMED')
            assignment = pending['assignments'][request['logical_reservation']]
            need(assignment['scope'] == [{'id': row['id'], 'kind': row['kind'], 'version': 1}]
                 and assignment['return'] is None and assignment['join'] is None
                 and assignment['native_lifecycle'] == 'NOT_CLAIMED', 'UNEXPECTED_RESULT_OR_JOIN')
            protocol_proof = verify_native_protocol(request, authorization)
            write(out / 'ACTUAL_NATIVE_PROTOCOL_PROOF.json', protocol_proof)
            transcript = Path(request['rollout']['path'])
            need(transcript.is_relative_to(LANE / 'operation/home/sessions'), 'ROLLOUT_SCOPE')
            raw, identity = read(transcript, 32 * 1024 * 1024)
            need({'device': identity[0], 'inode': identity[1]} == proof['source']['physical'] == request['rollout']['physical'], 'ROLLOUT_PHYSICAL_ID')
            need(len(raw) == request['rollout']['bytes'] and sha(raw) == request['rollout']['sha256'], 'ROLLOUT_CUTOFF_CHANGED')
            prefix = request['pre_boundary_source']
            need(sha(raw[:prefix['bytes']]) == prefix['sha256'], 'CORRECTED_SOURCE_PREFIX_CHANGED')
            first = raw.splitlines(keepends=True)[0]
            meta = decode(first)['payload']
            need(sha(first) == proof['source']['session_meta_sha256'] and meta['id'] == request['thread_id']
                 and meta['session_id'] == request['thread_id'] and meta['cli_version'] == '0.166.0', 'NATIVE_SESSION_META')
            canonical_markers = 0
            for descriptor in proof['markers']:
                need(descriptor['offset'] >= prefix['bytes'], 'MARKER_PRECEDES_CORRECTED_COLD_CHECKPOINT')
                wire = raw[descriptor['offset']:descriptor['offset'] + descriptor['bytes']]
                need(sha(wire) == descriptor['sha256'], 'MARKER_EXACT_BYTES')
                native_row = decode(wire)
                native_payload = native_row['payload']
                is_canonical = native_row['type'] == 'compacted' or (native_row['type'] == 'event_msg' and native_payload.get('type') == 'context_compacted')
                need(is_canonical == descriptor['canonical'] and 'metadata' not in native_row, 'NATIVE_MARKER_KIND')
                canonical_markers += int(is_canonical)
            resume = proof['resume']
            wire = raw[resume['offset']:resume['offset'] + resume['bytes']]
            need(sha(wire) == resume['sha256'] and canonical_markers == 1, 'RESUME_BYTES_OR_MARKER_COUNT')
            resumed = decode(wire)
            need(resumed['payload']['turn_id'] == proof['resume_turn'] == request['resume_turn_id']
                 and resume['offset'] > max(item['offset'] for item in proof['markers'])
                 and (resumed['type'] == 'turn_context' or (resumed['type'] == 'event_msg' and resumed['payload']['type'] == 'task_started')),
                 'RESUME_ORDER_OR_IDENTITY')
            status = decode(command(['/usr/bin/python3', '-I', '-B', scripts / 'compaction-audit-pending.py',
                '--store', store, '--session', request['thread_id'], '--owner-id', request['census_owner'], 'status'])[1])
            need(status['audit_state_required'] is True and status['state_dependent_decisions_held'] is True
                 and status['decision'] == 'WAIT_EXISTING_AUDIT' and status['source_problem'] is None
                 and status['pending'] == assignment['scope'], 'PUBLIC_PENDING_STATUS')
            binding = decode(command(['/usr/bin/python3', '-I', '-B', scripts / 'host-session-binding.py',
                '--store', store, 'lookup', '--host-id', 'codex', '--host-session-id', request['thread_id']])[1])
            need(binding == request['host_lookup'], 'HOST_BINDING_CHANGED')
            need(read(pending_path) == (pending_raw, pending_identity), 'PENDING_CHANGED_DURING_READ')
            write(out / 'PENDING.json', pending_raw)
            write(out / 'PENDING_STATUS.json', status)
            write(out / 'HOST_LOOKUP.json', binding)
            write(out / 'ROLLOUT_PIN.json', request['rollout'])
            result.update(boundary_id=row['id'], pending_unconsumed=True, audit_state_required=True,
                          native_lifecycle='NOT_CLAIMED', source_physical_record_verified=True,
                          later_native_protocol_verified=True)
        need(refs() == before, 'REF_SNAPSHOT_CHANGED_DURING_READ')
        need(read(args.request) == (request_raw, request_identity), 'READBACK_REQUEST_CHANGED')
        need(gate(args.go_sha256) == authorization, 'AUTHORIZATION_CHANGED_DURING_READ')
        for item in request['runtime_pins']:
            raw, identity = read(item['path'])
            need(sha(raw) == item['sha256'] and len(raw) == item['bytes']
                 and stat.S_IMODE(identity[2]) == item['mode'], 'RUNTIME_CHANGED_DURING_READ')
        write(out / 'REFS.json', before)
        write(out / 'REF_OBJECTS.json', objects)
        result.update(status='PASS', marker_preserved=True, protected_payload_preserved=True,
                      legacy_roles_preserved=True, refs_stable=True, retained_object_bytes=retained_bytes,
                      scope='INDEPENDENT_PUBLIC_READERS_AND_EXACT_RAW_OBJECTS_ONLY')
    except BaseException as exc:
        result.update(status='FAIL_PRESERVED_NO_RETRY', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        write(out / 'COMMANDS.json', commands)
        result['finished_monotonic_ns'] = time.monotonic_ns()
        write(out / 'RESULT.json', result)
    print(json.dumps({'status': result['status'], 'phase': phase, 'output': str(out)}, sort_keys=True))


if __name__ == '__main__':
    main()
