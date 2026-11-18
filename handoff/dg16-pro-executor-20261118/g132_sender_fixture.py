#!/usr/bin/env python3
"""Explicit public-metadata fixture for the exact dispatcher owner functions.

This is not root_sender_entry, an admitted original sender, or a native event
producer. No admission or PRO_SENDER_OPERATION body is created. The original
binding() gate is not represented as passed. A separately admitted ordinary
smoke may exercise transport using these deliberately synthetic broker inputs.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import time
import types
import warnings

CONFIGURATION_SHA256=None
DISPATCHER_SHA = '6841057bd780588688f193e7959a1dda60dca42bbe5ef5995bca14147cb79f73'
SCOPE = 'SYNTHETIC_TRANSPORT_ONLY_NO_ORIGINAL_INPUTS'


def need(ok, code):
    if not ok:
        raise ValueError(code)


def read(path, pin, maximum=1024*1024):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path, 'FIXTURE_SOURCE_PATH')
    before = path.lstat()
    mark = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_uid, s.st_gid,
                      s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_uid == os.geteuid()
         and stat.S_IMODE(before.st_mode) in (0o400, 0o444) and 0 < before.st_size <= maximum, 'FIXTURE_RECEIVED_FILE')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        need(mark(os.fstat(fd)) == mark(before) and not os.listxattr(fd), 'FIXTURE_OPEN_CHANGED')
        raw = os.pread(fd, maximum+1, 0)
        need(len(raw) == before.st_size and hashlib.sha256(raw).hexdigest() == pin
             and mark(os.fstat(fd)) == mark(before) == mark(path.lstat()), 'FIXTURE_READ_CHANGED')
    finally:
        os.close(fd)
    return raw


def inputs():
    need(sys.flags.isolated and sys.dont_write_bytecode and os.getuid() == os.geteuid() > 0
         and os.getgid() == os.getegid(), 'CURRENT_NONROOT_FIXTURE')
    raw = read(Path(__file__).with_name('SMOKE_CONFIGURATION.json'), CONFIGURATION_SHA256, 65536)
    cfg = json.loads(raw)
    need(cfg['fixture_scope'] == SCOPE and time.time_ns()//1000000 < cfg['spec']['expires_ms'], 'FIXTURE_WINDOW')
    source = Path(cfg['upstream_root'])/'dispatcher-templates-02/dispatcher_entry.py'
    owner_raw = read(source, DISPATCHER_SHA)
    D = types.ModuleType('exact_dispatcher_functions_for_explicit_fixture')
    D.__file__ = str(source)
    with warnings.catch_warnings(record=True):
        warnings.simplefilter('always')
        exec(compile(owner_raw, str(source), 'exec'), D.__dict__)
    ctx = cfg['spec']['context']
    root = Path(cfg['root'])/'sender-fixture'
    # These are fixture arguments to public functions, never an original body.
    b = {'context': ctx, 'sender_uid': os.getuid(), 'sender_gid': os.getgid(),
         'operation_path': str(root/'packet/carrier/PRO_SENDER_OPERATION.json'),
         'operation': D.desc(D.encode({'fixture_scope': SCOPE, 'configuration_sha256': CONFIGURATION_SHA256})),
         'journal_path': str(root/'dispatcher-journal'), 'nonce': CONFIGURATION_SHA256[:32],
         'source_commit': ctx['source_commit'], 'source_tree': ctx['source_tree'],
         'carrier_binding_sha256': D.sha(b'FIXTURE: NO ACTUAL CARRIER'),
         'input_index_sha256': D.sha(b'FIXTURE: NO ORIGINAL INPUTS'),
         'limits': {'journal_bytes': D.MAX_BYTES, 'journal_entries': D.MAX_ENTRIES,
                    'tool_result_bytes': D.RESULT_MAX, 'chunk_bytes': D.CHUNK_MAX, 'metadata_reads': 18}}
    op = {'expires_unix_ms': cfg['spec']['expires_ms'], 'artifact_id': 'FIXTURE_NO_PRIVATE_ARTIFACT'}
    need(not Path(b['operation_path']).exists(), 'NO_FORGED_ORIGINAL_OPERATION_BODY')
    return cfg, D, root, b, op


class FixtureBroker:
    def __init__(self, D, b, op):
        self.D, self.b, self.op = D, b, op

    def inspect(self, ordinal):
        D, b, op = self.D, self.b, self.op
        request = {'ordinal': ordinal, 'phase': D.PHASES[ordinal//6], 'kind': D.KINDS[ordinal%6],
            'context': b['context'], 'nonce': b['nonce'], 'operation_sha256': b['operation']['sha256'],
            'source_commit': b['source_commit'], 'source_tree': b['source_tree'],
            'carrier_binding_sha256': b['carrier_binding_sha256'], 'artifact_id': op['artifact_id'],
            'tool': D.TOOL, 'method': 'GET', 'arguments': {'url': D.endpoint(b, op, ordinal)}}
        return {'request': request, 'request_sha256': D.sha(D.encode(request)), 'fetch_permitted': False}

    def reserve(self, ordinal):
        D, b, op = self.D, self.b, self.op
        request = self.inspect(ordinal)
        return {'tool': D.TOOL, 'arguments': request['request']['arguments'], 'ordinal': ordinal,
            'nonce': b['nonce'], 'intent_sha256': D.sha(D.encode({'fixture_scope': SCOPE, 'ordinal': ordinal, 'nonce': b['nonce']})),
            'request_sha256': request['request_sha256'],
            'deadline_monotonic': time.monotonic()+(op['expires_unix_ms']-time.time_ns()//1000000)/1000}

    def publish(self, ordinal, intent, raw, call_ref):
        D, b = self.D, self.b
        return {'status': 'COMMITTED_REPLY', 'fetch_permitted': False,
            'reply': {'status': 'RECEIVED', 'ordinal': ordinal, 'nonce': b['nonce'],
                'intent_sha256': intent, 'tool_result': D.desc(raw), 'tool_call_ref': call_ref,
                'fixture_scope': SCOPE, 'original_provider_policy_exercised': False}}


def start_fixture():
    cfg, D, root, b, op = inputs()
    root.mkdir(mode=0o700, exist_ok=False)
    markers = root/('dg16-private-sender-'+b['context']['run_id']+'-a1')
    markers.mkdir(mode=0o700)
    for ordinal in range(18):
        fd = os.open(markers/('BROKER_%02d_REQUEST_READY'%ordinal), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(fd)
    marker = D.encode({'fixture_scope': SCOPE, 'authority': 'NONE', 'original_sender_invoked': False,
                      'original_admission_created': False, 'original_operation_body_created': False})
    with (root/'FIXTURE_ONLY.json').open('xb') as handle:
        handle.write(marker)
    (root/'FIXTURE_ONLY.json').chmod(0o400)
    return {'status': 'EXPLICIT_FIXTURE_PRODUCER_STARTED', 'fixture_scope': SCOPE,
            'original_sender_invoked': False, 'automatic_retry': False}


def terminal_fixture():
    cfg, D, root, b, op = inputs()
    with D.Journal(b) as journal:
        end = D.parse(journal.read('END.json'))
        need(end['reads'] == 18 and end['authority'] == 'NONE', 'ACTUAL_DISPATCHER_END')
        returns = {}
        for ordinal in range(18):
            row = D.parse(journal.read(D.name(ordinal, 'PUBLISHED.json')))
            need(row['broker_status'] == 'RECEIVED', 'ACTUAL_FIXTURE_PUBLISHED')
            returns[str(ordinal)] = D.desc(journal.read(D.name(ordinal, 'RESULT.raw')))
    return {'status': 'EXACT_18_OWNER_DISPATCH_STEPS_WITH_FIXTURE_BROKER', 'fixture_scope': SCOPE,
        'owner_source_sha256': DISPATCHER_SHA, 'owner_functions': ['Journal', 'reserve', 'complete_result', 'publish'],
        'actual_tool_result_descriptors': returns, 'journal_path': b['journal_path'],
        'original_binding_gate_passed': False, 'original_sender_invoked': False,
        'encryption_performed': False, 'original_admission_created': False, 'original_awards': []}


def main():
    cfg, D, root, b, op = inputs()
    action = sys.argv[1]
    if action == 'initialize':
        need(len(sys.argv) == 2, 'FIXED_ARGUMENTS')
        with D.Journal(b, create=True):
            pass
        return {'status': 'INITIALIZED', 'fetch_permitted': False}
    with D.Journal(b) as journal:
        if action == 'finish':
            need(len(sys.argv) == 2, 'FIXED_ARGUMENTS')
            rows = journal.census()
            for ordinal in range(18):
                need(D.parse(journal.read(D.name(ordinal, 'PUBLISHED.json')))['broker_status'] == 'RECEIVED', 'ALL_18_RECEIVED')
            journal.write('END.json', D.encode({'schema': 'dg16.root-dispatch-journal-end.v1',
                'authority': 'NONE', 'reads': 18, 'prefix': rows, 'original_awards': []}))
            return {'status': 'DISPATCH_18_COMPLETE_SENDER_TERMINAL_SEPARATE', 'fetch_permitted': False}
        ordinal = int(sys.argv[2])
        D.integer(ordinal, 0, 17)
        if action == 'ready':
            need(len(sys.argv) == 3 and D.name(ordinal, 'INTENT.json') not in journal.census(), 'FIXTURE_READY_ONCE')
            return {'status': 'READY' if D.marker_ready(b, op, ordinal) else 'PENDING', 'fetch_permitted': False}
        if action == 'reserve':
            need(len(sys.argv) == 3, 'FIXED_ARGUMENTS')
            return D.reserve(b, op, journal, ordinal, FixtureBroker(D, b, op))
        if action == 'chunk':
            need(len(sys.argv) == 5, 'FIXED_ARGUMENTS')
            return {'status': 'CHUNK_RETAINED', **journal.append_result(ordinal, int(sys.argv[3]), base64.b64decode(sys.argv[4], validate=True))}
        if action == 'complete':
            need(len(sys.argv) == 6, 'FIXED_ARGUMENTS')
            return D.complete_result(b, journal, ordinal, int(sys.argv[3]), sys.argv[4], sys.argv[5])
        need(action == 'publish' and len(sys.argv) == 3, 'FIXED_ACTION')
        return D.publish(b, journal, ordinal, FixtureBroker(D, b, op))


if __name__ == '__main__':
    try:
        print(json.dumps(main(), sort_keys=True, separators=(',', ':')), flush=True)
    except BaseException:
        print('{"status":"FIXTURE_REFUSED_OR_UNKNOWN_NO_REPLAY","authority":"NONE"}', flush=True)
        raise SystemExit(1)
