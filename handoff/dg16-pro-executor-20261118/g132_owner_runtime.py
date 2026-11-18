#!/usr/bin/env python3
"""Current-Linux composition of exact public owner functions.

Loading is inert. The smoke actions use only explicit synthetic public bodies.
bind-dispatcher consumes an existing actual admission; it never authors one.
No command here starts the private sender, changes a ref, or invokes an MCP API.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import select
import stat
import sys
import termios
import time
import types
import warnings

PINS = {
    'binary': ('root-final-operators-01/binary_publish_v3.py', 'e6277edd4f97bac470b1762be8cf80d1e4a21fe05f10ef168bc61e83d47599ef'),
    'control': ('root-final-operators-01/control_process_v3.py', 'acccc8b7b994e83dc05068a1edd98002600eafbcf2c2292767970b2e46856b64'),
    'binder': ('dispatcher-templates-02/bind_dispatcher.py', 'c59aa4cd4228cb4c081c191ad3d8b026e17765ef39b069d74de0778de48303ad'),
}
G3_PIN = 'b85cca1550ff8e7c1c89778180e53a5c70f306f0c8725ba60ef3ccd4bbc3a6ad'
SCOPE = 'SYNTHETIC_TRANSPORT_ONLY_NO_ORIGINAL_INPUTS'
READY = 'READY_FOR_EPHEMERAL_DOWNLOAD_RESULT_LENGTH_FRAME'


def need(ok, code):
    if not ok:
        raise ValueError(code)


def enc(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                       allow_nan=False)+'\n').encode('ascii')


def desc(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def parse(raw):
    def pairs(rows):
        out = {}
        for name, item in rows:
            need(name not in out, 'DUPLICATE_KEY')
            out[name] = item
        return out
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'NONFINITE'))


def read(path, maximum, pin=None, source=False):
    p = Path(path)
    need(p.is_absolute() and p.resolve(strict=True) == p
         and all(not x.is_symlink() for x in p.parents), 'CURRENT_NONALIAS_PATH')
    s = p.lstat()
    need(stat.S_ISREG(s.st_mode) and s.st_nlink == 1 and s.st_uid == os.geteuid()
         and 0 < s.st_size <= maximum
         and stat.S_IMODE(s.st_mode) in ((0o400, 0o444) if source else (0o400, 0o600)), 'CURRENT_FILE_CUSTODY')
    mark = lambda v: (v.st_dev, v.st_ino, v.st_mode, v.st_uid, v.st_gid, v.st_nlink,
                      v.st_size, v.st_mtime_ns, v.st_ctime_ns)
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        need(mark(os.fstat(fd)) == mark(s) and not os.listxattr(fd), 'OPEN_CHANGED')
        raw = os.pread(fd, maximum+1, 0)
        need(len(raw) == s.st_size and mark(os.fstat(fd)) == mark(s) == mark(p.lstat()), 'READ_CHANGED')
    finally:
        os.close(fd)
    if pin is not None:
        need(desc(raw)['sha256'] == pin, 'EXACT_RECEIVED_SOURCE')
    return raw


def module(path, pin):
    raw = read(path, 1024*1024, pin, source=True)
    m = types.ModuleType('received_owner_'+pin[:16])
    m.__file__ = str(path)
    # Record syntax warnings locally; do not mix diagnostic text with a frame.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        exec(compile(raw, str(path), 'exec'), m.__dict__)
    m._composition_source = {'path': str(path), **desc(raw), 'syntax_warnings': len(caught)}
    return m


def owner(cfg, name):
    relative, pin = PINS[name]
    return module(Path(cfg['upstream_root'])/relative, pin)


def private_root(cfg):
    root = Path(cfg['root'])
    need(root.is_absolute() and root.resolve(strict=True) == root and not root.is_symlink(), 'CURRENT_ROOT_PATH')
    info = root.lstat()
    need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid()
         and stat.S_IMODE(info.st_mode) == 0o700 and not os.listxattr(root), 'CURRENT_ROOT_CUSTODY')
    return root


def current(cfg):
    now = time.time_ns()//1000000
    need(cfg['fixture_scope'] == SCOPE and cfg['spec']['issued_ms'] <= now < cfg['spec']['expires_ms']
         <= cfg['spec']['issued_ms']+600000, 'SYNTHETIC_CURRENT_WINDOW')
    private_root(cfg)
    return now


def frame(maximum, seconds):
    need(sys.stdin.isatty() and 0 < seconds <= 45, 'ORIGINAL_BOUNDED_TTY_FRAME')
    before = termios.tcgetattr(0)
    altered = list(before)
    altered[6] = list(before[6])
    altered[3] &= ~(termios.ECHO | termios.ICANON)
    altered[6][termios.VMIN] = 1
    altered[6][termios.VTIME] = 0
    termios.tcsetattr(0, termios.TCSANOW, altered)
    deadline = time.monotonic()+seconds
    try:
        print(READY, flush=True)
        header = b''
        while not header.endswith(b'\n'):
            need(time.monotonic() < deadline and len(header) <= 8, 'FRAME_HEADER_BOUND')
            if select.select([0], [], [], min(.1, max(0, deadline-time.monotonic())))[0]:
                block = os.read(0, 1)
                need(block, 'FRAME_EOF')
                header += block
        need(re.fullmatch(rb'[1-9][0-9]*\n', header), 'FRAME_LENGTH')
        size = int(header)
        need(size <= maximum, 'FRAME_BODY_BOUND')
        raw = b''
        while len(raw) < size:
            need(time.monotonic() < deadline, 'FRAME_EXPIRED')
            if select.select([0], [], [], min(.1, max(0, deadline-time.monotonic())))[0]:
                block = os.read(0, min(65536, size-len(raw)))
                need(block, 'FRAME_EOF')
                raw += block
        return raw
    finally:
        termios.tcsetattr(0, termios.TCSANOW, before)


def emit(value):
    sys.stdout.buffer.write(enc(value))
    sys.stdout.buffer.flush()


def publish_smoke(cfg, payload):
    current(cfg)
    need(re.fullmatch(r'engineering/g132-portability-smoke-[a-z0-9-]{1,80}', cfg['branch'])
         and re.fullmatch('[0-9a-f]{40}', payload['parent_sha']), 'FRESH_ENGINEERING_SMOKE_ONLY')
    B, D = owner(cfg, 'binary'), owner(cfg, 'control')
    root = private_root(cfg)

    class CurrentJournal(D.Journal):
        """Only the old fixed ROOT check is replaced by this explicit local root.

        All original check/reserve/write/close implementations remain in D.
        """
        def __init__(self):
            self.path = root/'source-publication-journal'
            need(not os.path.lexists(self.path), 'ONE_SOURCE_PUBLICATION_JOURNAL')
            self.path.mkdir(mode=0o700)
            self.fd = os.open(self.path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            self.identity = self.mark(os.fstat(self.fd))
            self.names, self.bytes = set(), 0
            self.check()

    files = {
        'CONTROL.json': enc({'schema': 'dg16.g132-synthetic-public-control.v1', 'authority': 'NONE',
            'fixture_scope': SCOPE, 'run_id': cfg['spec']['context']['run_id'],
            'controller': cfg['spec']['actor']['controller'], 'original_awards': []}),
        'INPUTS.cms': b'G132 PORTABILITY FIXTURE ONLY. NOT CMS. NO PRIVATE INPUT. NO ENCRYPTION.\n',
    }
    request = enc({'fixture_scope': SCOPE, 'files': {n: desc(b) for n, b in files.items()}})

    class SyntheticContent:
        # This is an explicit fixture predicate, never the original private policy.
        MAX_CONTROL = MAX_CIPHERTEXT = 16384

        @staticmethod
        def validate_control(control, cipher, actual_request, now):
            need(control == files['CONTROL.json'] and cipher == files['INPUTS.cms']
                 and actual_request == request and now < cfg['spec']['expires_ms'], 'EXACT_SYNTHETIC_BODIES_ONLY')

    plan = {'repository': cfg['spec']['context']['repository'], 'branch': cfg['branch'],
            'parent_sha': payload['parent_sha'], 'context': cfg['spec']['context'],
            'files': {n: {**desc(b), 'git_blob': B.git('blob', b)} for n, b in files.items()},
            'expected_tree': B.tiny_tree(files), 'expires_unix_ms': cfg['spec']['expires_ms'],
            'fixture_scope': SCOPE}
    journal = CurrentJournal()
    def scoped_emit(value):
        if value.get('event') == 'complete':
            value = {'event': 'complete', 'receipt': {'authority': 'NONE', 'fixture_scope': SCOPE,
                'exact_owner_receipt': value['receipt'], 'original_acceptance': False,
                'original_content_policy_exercised': False,
                'owner_functions': ['binary_publish_v3.run', 'write_call', 'read_plan', 'receive',
                                    'file_readback.decode_file_result', 'control_process_v3.Journal.write'],
                'private_key_operation': False}}
        emit(value)
    try:
        result = B.run(SyntheticContent, None, plan, files, request, journal, D.metadata_guard,
                       frame, scoped_emit, lambda: time.time_ns()//1000000, lambda: current(cfg))
        need(result is not None, 'SOURCE_PUBLICATION_UNKNOWN_NO_REPLAY')
    finally:
        journal.close()


def g3(cfg, action, payload):
    now = current(cfg)
    G = module(cfg['g3_source'], G3_PIN)
    if action == 'g3-request':
        shared = min(600, (cfg['spec']['expires_ms']-now)//1000)
        need(shared >= 180, 'SYNTHETIC_G3_WINDOW')
        hold = min(300, shared-120)
        digest = hashlib.sha256(b'G132 SYNTHETIC: NO NATIVE OBSERVATION').hexdigest()
        request = {'schema': 'dg16.g3-root-consumption-request.v2', 'authority': 'NONE',
            'source_commit': G.SOURCE_COMMIT, 'source_tree': G.SOURCE_TREE, 'source_parent': G.SOURCE_PARENT,
            'run_id': cfg['spec']['context']['run_id'], 'attempt': 1, 'nonce': digest[:32],
            'control_branch': G.CONTROL_BRANCH, 'control_path': G.CONTROL_PATH, 'root': G.ROOT,
            'join': G.JOIN, 'original_scope_sha256': G.SCOPE_SHA,
            **{k: digest for k in ('graph_sha256', 'dispatch_sha256', 'transition_sha256', 'join_sha256',
                                  'scope_return_sha256', 'g1_return_sha256', 'complete_input_key')},
            'returned_nodes': G.SELECTED, 'issued_unix_ms': now, 'expires_unix_ms': now+hold*1000,
            'hold_seconds': hold, 'shared_expires_unix_ms': now+shared*1000, 'shared_window_seconds': shared,
            'decision_before': G.BEFORE, 'decision_after': G.AFTER, 'original_total': 157,
            'original_awards': 0, 'full_g2': 'NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST', 'status': 'ROOT_REQUEST_READY'}
        raw = G.encode(request)
        G.validate_public_request(raw)
        proposal = {'schema': 'dg16.g3-root-consumption-decision.v2', 'issuer': 'R5_ROOT_GOVERNOR',
            'successor': 'PRO-EXECUTOR-01, designated by owner', 'action': 'CONSUME_COMPONENT_RETURNS_ONLY',
            'request_sha256': G.sha(raw),
            **{k: request[k] for k in ('run_id', 'attempt', 'nonce', 'source_commit', 'source_tree',
                                     'graph_sha256', 'dispatch_sha256', 'join_sha256', 'decision_before',
                                     'decision_after', 'full_g2', 'expires_unix_ms')},
            'outputs': {G.PAIR: request['g1_return_sha256'], G.SCOPE: request['scope_return_sha256']},
            'consumed_nodes': G.SELECTED, 'owner_arrangement': G.OWNER_ARRANGEMENT,
            'original_awards': 0, 'issued_unix_ms': now}
        return {'raw': raw.decode('ascii'), 'fixture_scope': SCOPE, 'decision_proposal': proposal,
                'proposal_is_issued_decision': False, 'source': G._composition_source}
    raw = payload['request']['raw'].encode('utf-8')
    request = G.validate_public_request(raw)
    if action == 'g3-validate-request':
        return {'request_sha256': G.sha(raw), 'fixture_scope': SCOPE, 'source': G._composition_source}
    decision_raw = payload['decision']['raw'].encode('utf-8')
    G.validate_decision(decision_raw, request, G.sha(raw), now)
    if action == 'g3-validate-decision':
        return {'request_sha256': G.sha(raw), 'decision_sha256': G.sha(decision_raw),
                'fixture_scope': SCOPE, 'strict_original_validator_returned': True,
                'effect_grant': False, 'source': G._composition_source}
    need(action == 'g3-consume-probe' and os.getuid() == os.geteuid() > 0, 'NONROOT_REFUSAL_PROBE_ONLY')
    private = private_root(cfg)/'g3-consumer-refusal'
    private.mkdir(mode=0o700, exist_ok=False)
    api = {'source': cfg['repo_path'], 'private': str(private), 'run_root': 'NO_SYNTHETIC_NATIVE_RUN',
           'controller': cfg['spec']['actor']['controller'], 'deadline_monotonic': time.monotonic()+30}
    try:
        # The public function is decorated by the exact original @guarded;
        # it takes one API argument and creates its own genuine diagnostic.
        G.consume(api)
    except G.Refusal as exc:
        need(str(exc) == 'ACTUAL_ROOT_CUSTODY_REQUIRED', 'UNEXPECTED_SOURCE_CONSUMER_REFUSAL')
        diagnostic_raw = read(private/'G3_EFFECT_STATE.json', 4096)
        diagnostic = G.validate_effect_state(diagnostic_raw)
        need(diagnostic['failed'] and not diagnostic['consumption_reserved']
             and not diagnostic['root_consumed']
             and all(value == 'NOT_STARTED' for value in diagnostic['effects'].values()), 'SOURCE_REFUSAL_EFFECT_BOUNDARY')
        return {'status': 'ACTUAL_ORIGINAL_G3_CONSUMER_REFUSED', 'refusal': str(exc),
                'actual_consumer_invoked': True, 'successful_original_consumption': False,
                'uid': os.getuid(), 'euid': os.geteuid(), 'gid': os.getgid(), 'egid': os.getegid(),
                'request_sha256': G.sha(raw), 'decision_sha256': G.sha(decision_raw),
                'actual_diagnostic': {'path': str(private/'G3_EFFECT_STATE.json'), **desc(diagnostic_raw)},
                'fixture_scope': SCOPE, 'source': G._composition_source, 'original_awards': []}
    raise ValueError('UNEXPECTED_ORIGINAL_CONSUMER_RETURN')


def bind_dispatcher(cfg):
    """Requires actual operation, actual late receiving and existing admission."""
    B = owner(cfg, 'binder')
    admission = read(cfg['admission']['path'], 16384, cfg['admission']['sha256'])
    files = B.bind(cfg['selection'], admission)
    binding = B.parse(files['DISPATCHER_BINDING.json']) if hasattr(B, 'parse') else parse(files['DISPATCHER_BINDING.json'])
    operation = parse(read(cfg['selection']['operation_path'], 65536, binding['operation']['sha256']))
    need(binding['sender_uid'] == os.getuid() == os.geteuid()
         and binding['sender_gid'] == os.getgid() == os.getegid()
         and time.time_ns()//1000000 < operation['expires_unix_ms'], 'CURRENT_ACTUAL_DISPATCHER_OWNER')
    bridge = cfg['linux_bridge']
    bridge_raw = read(bridge['path'], 1024*1024, bridge['sha256'], source=True)
    output = Path(cfg['selection']['helper_path']).parent
    need(output.is_absolute() and output.parent.resolve(strict=True) == output.parent
         and not os.path.lexists(output), 'FRESH_CURRENT_DISPATCHER_INSTALL')
    output.mkdir(mode=0o700)
    for name, raw in files.items():
        with (output/name).open('xb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        (output/name).chmod(0o400)
        need(read(output/name, 1024*1024) == raw, 'EXACT_BOUND_MEMBER_READBACK')
    result = {'schema': 'dg16.pro-linux-dispatcher-selection.v1', 'authority': 'NONE',
              'dispatcher': {'path': str(output/'dispatcher_entry.py'), 'descriptor': desc(files['dispatcher_entry.py'])},
              'sender_entry': {'path': cfg['selection']['entry_path'], **binding['entry'],
                               'deadline_ms': operation['expires_unix_ms']},
              'linux_bridge': {'path': bridge['path'], **desc(bridge_raw)}, 'original_binder': B._composition_source,
              'legacy_dispatch_js_executed': False, 'actual_admission_created': False,
              'sender_started': False, 'effect_grant': False, 'original_awards': []}
    with (output/'PRO_LINUX_SELECTION.json').open('xb') as handle:
        handle.write(enc(result))
    (output/'PRO_LINUX_SELECTION.json').chmod(0o400)
    return result


def main():
    need(sys.platform == 'linux' and sys.flags.isolated and sys.dont_write_bytecode
         and os.getuid() == os.geteuid() and os.getgid() == os.getegid(), 'ACTUAL_ISOLATED_LINUX')
    need(len(sys.argv) in (4, 5), 'ACTION_CONFIG_PIN_PAYLOAD')
    action, path, pin = sys.argv[1:4]
    cfg = parse(read(path, 65536, pin))
    payload = parse(base64.b64decode(sys.argv[4], validate=True)) if len(sys.argv) == 5 else {}
    if action == 'publish-smoke':
        publish_smoke(cfg, payload)
    else:
        if action == 'bind-dispatcher':
            result = bind_dispatcher(cfg)
        elif action in ('sender-fixture-start', 'sender-fixture-terminal'):
            current(cfg)
            fixture = module(cfg['sender_fixture_path'], payload['helper_sha256'])
            result = fixture.start_fixture() if action == 'sender-fixture-start' else fixture.terminal_fixture()
        else:
            result = g3(cfg, action, payload)
        emit({'event': 'complete', 'receipt': result})


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        emit({'event': 'failure', 'status': 'REFUSED_OR_UNKNOWN_NO_REPLAY', 'authority': 'NONE'})
        raise SystemExit(1)
