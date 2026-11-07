#!/usr/bin/env python3
"""Root-wrapper seam for an already admitted, owned startup process.

Call prepare() before root launches anything. Root independently verifies and consumes
fresh effect-time admission, launches the exact argv/env in the returned private spec,
then calls observe_owned(). This module contains no native launcher or authority issuer.
"""
from pathlib import Path
from dataclasses import dataclass
import hashlib
import json
import os
import re
import selectors
import signal
import stat
import subprocess
import time
import warning_custody as custody

from startup_diagnostic import (Observer, ConfigSnapshot, Refusal, need, sha, encoded,
    validate_public, load_pinned, MAX_FRAME, MAX_STDOUT, MAX_STDERR, MAX_CONFIG)

OFFICIAL_BINARY_SHA256 = 'b8a11fedf24b2dfb59a70c9e52b030f9a508dcd49cd2dd0d41956f4c785156b8'
OFFICIAL_BINARY_BYTES = 319346888
REQUEST_SCHEMA = 'dg18.c02.startup-diagnostic-request.v2'
RECEIPT_SCHEMA = 'dg18.c02.startup-observation-receipt.v2'
INIT_SECONDS = 10.0
AFTER_REPLY_SECONDS = 1.0
CLOSE_SECONDS = 1.0
TERM_SECONDS = 1.0
KILL_SECONDS = 1.0
FIXED_ENV = {'PATH': '/usr/local/bin:/usr/bin:/bin', 'LANG': 'C.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1'}
DIGEST_KEYS = {'nonce', 'binary_sha256', 'authored_config_sha256', 'root_authorization_sha256',
               'independent_review_sha256', 'host_preparation_sha256', 'recipient_sha256', 'crypto_dependency_sha256'}
PATH_KEYS = {'binary', 'home', 'subject', 'evidence_parent'}
REQUEST_KEYS = DIGEST_KEYS | PATH_KEYS | {'schema', 'source_commit', 'not_before_unix_ms', 'expires_unix_ms'}
STAT_KEYS = ('st_dev','st_ino','st_mode','st_uid','st_nlink','st_size','st_mtime_ns','st_ctime_ns')
CLEANUP_RESULTS = {'NOT_ACQUIRED', 'ROOT_CLEANUP_REQUIRED', 'CLOSED', 'TERMINATED', 'KILLED', 'UNKNOWN'}
RUN_RESULTS = {'PREPARED', 'PREFLIGHT_REFUSED', 'STOPPED', 'PROCESS_BINDING_REFUSED', 'INTERRUPTED', 'INTERNAL_FAILURE'}
PRIVATE_FAILURE_CODES = {'PREPARED_REQUEST_CHANGED', 'PATH_NOT_CANONICAL', 'SYMLINK_INPUT',
    'PRIVATE_OWNED_DIRECTORY_REQUIRED', 'OWNED_SINGLE_REGULAR_INPUT_REQUIRED', 'PRIVATE_FILE_MODE',
    'INPUT_CHANGED_DURING_OPEN', 'INPUT_CHANGED_DURING_READ', 'INPUT_SIZE_CHANGED',
    'HOME_SUBJECT_SEPARATION', 'EVIDENCE_SEPARATION', 'PIN_MEMBER_TYPE', 'PIN_MEMBER_CHANGED', 'PIN_VARIANT', 'PIN_AST_SHAPE',
    'AUTHORED_CONFIG_PREIMAGE_CHANGED', 'BINARY_PREIMAGE_CHANGED', 'CONFIG_PREIMAGE_CHANGED',
    'REQUEST_WINDOW', 'LIVE_OWNED_POPEN_REQUIRED', 'PROCESS_ARGV_OR_TEXT_MODE',
    'OWNED_SESSION_REQUIRED', 'PROCESS_PARENT_OR_UID', 'LIVE_CMDLINE_MISMATCH',
    'LIVE_ENVIRONMENT_CARDINALITY', 'LIVE_ENVIRONMENT_MISMATCH', 'LIVE_CWD_MISMATCH',
    'LIVE_EXECUTABLE_PATH_MISMATCH', 'LIVE_EXECUTABLE_LIMIT', 'LIVE_EXECUTABLE_DIGEST_MISMATCH',
    'OWNED_PIPE_REQUIRED', 'OWNED_PIPE_IDENTITY'}

def closed_failure(exc):
    if isinstance(exc, Refusal) and exc.code in PRIVATE_FAILURE_CODES:
        return exc.code
    return 'FILE_MISSING' if isinstance(exc, FileNotFoundError) else 'UNCLASSIFIED_FAILURE'



def fingerprint(st):
    return tuple(getattr(st, k) for k in STAT_KEYS)


def canonical(path):
    p = Path(path)
    need(p.is_absolute() and '..' not in p.parts and str(p) == str(path), 'PATH_NOT_CANONICAL')
    for node in (p, *p.parents):
        need(not stat.S_ISLNK(node.lstat().st_mode), 'SYMLINK_INPUT')
    need(p.resolve(strict=True) == p, 'PATH_NOT_CANONICAL')
    return p


def secure_directory(path):
    p = canonical(path); st = p.stat()
    need(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid() and stat.S_IMODE(st.st_mode) == 0o700,
         'PRIVATE_OWNED_DIRECTORY_REQUIRED')
    return p


def stable_file(path, limit, *, private=False, keep=True):
    p = canonical(path)
    before = p.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid() and before.st_nlink == 1
         and before.st_size <= limit, 'OWNED_SINGLE_REGULAR_INPUT_REQUIRED')
    if private:
        need(stat.S_IMODE(before.st_mode) == 0o600, 'PRIVATE_FILE_MODE')
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
    parts = []; digest = hashlib.sha256(); count = 0
    try:
        need(fingerprint(before) == fingerprint(os.fstat(fd)), 'INPUT_CHANGED_DURING_OPEN')
        while True:
            raw = os.read(fd, min(1048576, limit + 1 - count))
            if not raw:
                break
            count += len(raw)
            need(count <= limit, 'INPUT_SIZE_CHANGED')
            digest.update(raw)
            if keep:
                parts.append(raw)
        need(fingerprint(before) == fingerprint(os.fstat(fd)) == fingerprint(p.lstat()), 'INPUT_CHANGED_DURING_READ')
    finally:
        os.close(fd)
    return b''.join(parts), digest.hexdigest(), fingerprint(before)


def private_write(directory, name, raw):
    need('/' not in name and name not in {'.','..'}, 'PRIVATE_FILENAME')
    fd = os.open(directory / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    except BaseException:
        raise


def atomic_public(root, receipt):
    data = validate_receipt(receipt)
    stage = root / 'PUBLIC.json.new'
    fd = os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    os.replace(stage, root / 'PUBLIC.json')


def validate_request(request):
    need(type(request) is dict and set(request) == REQUEST_KEYS, 'REQUEST_KEYS')
    need(request['schema'] == REQUEST_SCHEMA, 'REQUEST_SCHEMA')
    need(request['source_commit'] == '35bf9823856eb4efe254b882954120480632230e', 'GUARD_SOURCE_SCOPE')
    for key in DIGEST_KEYS:
        need(type(request[key]) is str and re.fullmatch('[0-9a-f]{64}', request[key]) and request[key] != '0'*64,
             'REQUEST_DIGEST_FIELD')
    need(request['binary_sha256'] == OFFICIAL_BINARY_SHA256, 'OFFICIAL_BINARY_PIN')
    need(request['recipient_sha256'] == custody.RECIPIENT_SHA256, 'RECIPIENT_PIN')
    for key in PATH_KEYS:
        need(type(request[key]) is str and len(request[key].encode()) <= 4096, 'REQUEST_PATH_FIELD')
    for key in ('not_before_unix_ms','expires_unix_ms'):
        need(type(request[key]) is int and 0 <= request[key] < 2**63, 'REQUEST_CLOCK_FIELD')
    now = time.time_ns() // 1000000
    need(request['not_before_unix_ms'] <= now < request['expires_unix_ms'] and
         request['expires_unix_ms'] - request['not_before_unix_ms'] <= 600000, 'REQUEST_WINDOW')


@dataclass
class Prepared:
    request: dict
    request_digest: str
    root: Path
    private: Path
    config: ConfigSnapshot
    config_identity: tuple
    binary_identity: tuple
    pinned: tuple
    receipt: dict
    used: bool = False

    def launch_spec(self):
        need(sha(encoded(self.request)) == self.request_digest == self.receipt.get('request_digest'),
             'PREPARED_REQUEST_CHANGED')
        validate_request(self.request)
        # Specification only. No subprocess, model, listener or grant is created.
        return {'argv': [self.request['binary'], 'app-server', '--listen', 'stdio://'],
                'cwd': self.request['subject'], 'env': dict(FIXED_ENV, HOME=self.request['home'], CODEX_HOME=self.request['home']),
                'stdin': 'PIPE', 'stdout': 'PIPE', 'stderr': 'PIPE', 'text': False,
                'bufsize': 0, 'start_new_session': True}


def prepare(request):
    """Validate exact inputs and create private failure retention before root's launch.

    Digest fields bind records only; this function does not authenticate or consume
    a review/GO. Root's separately reviewed admission wrapper must do that.
    """
    validate_request(request)
    request = json.loads(encoded(request))
    digest = sha(encoded(request))
    parent = secure_directory(request['evidence_parent'])
    root = parent / ('startup-diagnostic-' + request['nonce'])
    root.mkdir(mode=0o700, exist_ok=False)  # exclusive nonce reuse refusal
    private = root / 'private'; private.mkdir(mode=0o700)
    receipt = {'schema': RECEIPT_SCHEMA, 'authority': 'NONE', 'request_digest': digest,
               'status': 'PREPARED', 'observer': None, 'process_bound': False,
               'cleanup': 'NOT_ACQUIRED', 'private_retention': 'RETAINED_LOCAL_ONLY',
               'stdout_bytes_retained': 0, 'stderr_bytes_retained': 0,
               'stdout_truncated': False, 'stderr_truncated': False,
               'elapsed_bucket': 'UNDER_1_SECOND', 'admission_established_by_candidate': False,
        'warning_custody': custody.initial_status(digest, request['crypto_dependency_sha256'])}
    private_write(private, 'request.json', encoded(request))
    try:
        home = secure_directory(request['home']); subject = secure_directory(request['subject'])
        need(home != subject and not home.is_relative_to(subject) and not subject.is_relative_to(home), 'HOME_SUBJECT_SEPARATION')
        need(all(parent != p and not parent.is_relative_to(p) and not p.is_relative_to(parent)
                 for p in (home, subject)), 'EVIDENCE_SEPARATION')
        pinned = load_pinned()
        custody.preflight(request)
        config_raw, config_sha, config_identity = stable_file(home / 'config.toml', MAX_CONFIG, private=True)
        private_write(private, 'authored-config.toml', config_raw)
        need(config_sha == request['authored_config_sha256'], 'AUTHORED_CONFIG_PREIMAGE_CHANGED')
        config = ConfigSnapshot(config_raw, config_sha, home, subject)
        _, binary_sha, binary_identity = stable_file(request['binary'], 536870912, keep=False)
        need(binary_sha == request['binary_sha256'] and binary_identity[5] == OFFICIAL_BINARY_BYTES and
             binary_identity[2] & 0o111, 'BINARY_PREIMAGE_CHANGED')
        private_write(private, 'input-identities.json', encoded({'config_stat': config_identity, 'binary_stat': binary_identity}))
        atomic_public(root, receipt)
        return Prepared(request, digest, root, private, config, config_identity, binary_identity, pinned, receipt)
    except BaseException as exc:
        receipt['status'] = 'PREFLIGHT_REFUSED'
        private_write(private, 'preflight-refusal.json', encoded({'status': 'PREFLIGHT_REFUSED', 'failure_code': closed_failure(exc), 'native_acquired_by_component': False}))
        atomic_public(root, receipt)
        raise Refusal('PREFLIGHT_REFUSED') from None


def verify_owned_process(proc, *, argv, env, cwd, binary_sha256):
    """Bind a Popen handle to a direct Linux child with exclusive stdio/session.

    This is custody evidence, not native source or permission authority.
    """
    need(type(proc) is subprocess.Popen and proc.poll() is None and type(proc.pid) is int, 'LIVE_OWNED_POPEN_REQUIRED')
    need(proc.args == argv and proc.text_mode in (None, False), 'PROCESS_ARGV_OR_TEXT_MODE')
    need(os.getpgid(proc.pid) == proc.pid and os.getsid(proc.pid) == proc.pid, 'OWNED_SESSION_REQUIRED')
    procroot = Path('/proc') / str(proc.pid)
    status = (procroot / 'status').read_text()
    ppid = re.search(r'^PPid:\s+(\d+)$', status, re.M)
    uid = re.search(r'^Uid:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$', status, re.M)
    need(ppid is not None and int(ppid[1]) == os.getpid() and uid is not None and
         all(int(v) == os.getuid() for v in uid.groups()), 'PROCESS_PARENT_OR_UID')
    need((procroot / 'cmdline').read_bytes().split(b'\0')[:-1] == [x.encode() for x in argv], 'LIVE_CMDLINE_MISMATCH')
    actual_env = (procroot / 'environ').read_bytes().split(b'\0')
    need(len([v for v in actual_env if v]) == len(env), 'LIVE_ENVIRONMENT_CARDINALITY')
    need(set(v for v in actual_env if v) == {k.encode()+b'='+v.encode() for k,v in env.items()}, 'LIVE_ENVIRONMENT_MISMATCH')
    need(os.readlink(procroot / 'cwd') == cwd, 'LIVE_CWD_MISMATCH')
    # /proc/<pid>/exe is intentionally a kernel symlink: hash the actual mapped executable.
    need(os.readlink(procroot / 'exe') == argv[0], 'LIVE_EXECUTABLE_PATH_MISMATCH')
    digest = hashlib.sha256(); count = 0
    with (procroot / 'exe').open('rb') as stream:
        while True:
            raw = stream.read(1048576)
            if not raw:
                break
            count += len(raw); need(count <= 536870912, 'LIVE_EXECUTABLE_LIMIT'); digest.update(raw)
    need(digest.hexdigest() == binary_sha256, 'LIVE_EXECUTABLE_DIGEST_MISMATCH')
    for fd_number, stream in enumerate((proc.stdin, proc.stdout, proc.stderr)):
        need(stream is not None and not stream.closed, 'OWNED_PIPE_REQUIRED')
        fd = stream.fileno(); parent_stat = os.fstat(fd); child_stat = (procroot/'fd'/str(fd_number)).stat()
        need(stat.S_ISFIFO(parent_stat.st_mode) and parent_stat.st_dev == child_stat.st_dev and
             parent_stat.st_ino == child_stat.st_ino, 'OWNED_PIPE_IDENTITY')
    return True


class Capture:
    def __init__(self, private):
        self.files = {}
        self.counts = {'stdout': 0, 'stderr': 0}
        self.truncated = {'stdout': False, 'stderr': False}
        self.failed = False
        try:
            for name in self.counts:
                fd = os.open(private / (name + '.bin'), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                self.files[name] = os.fdopen(fd, 'wb', buffering=0)
        except OSError:
            self.failed = True

    def write(self, name, data):
        limit = MAX_STDOUT if name == 'stdout' else MAX_STDERR
        remaining = limit - self.counts[name]
        piece = data[:remaining]
        if self.failed:
            return False
        try:
            written = self.files[name].write(piece)
            self.counts[name] += written
            if written != len(piece):
                self.failed = True
                return False
        except OSError:
            self.failed = True
            return False
        if len(data) > remaining:
            self.truncated[name] = True
        return len(data) <= remaining

    def close(self):
        for stream in self.files.values():
            try:
                stream.flush(); os.fsync(stream.fileno())
            except OSError:
                self.failed = True
            finally:
                stream.close()


def group_exists(pid):
    try:
        os.killpg(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def stop_owned(proc, sel, capture):
    """Only called after custody binding. Drain owned pipes while stopping bounded group."""
    def drain_until(deadline):
        while time.monotonic() < deadline:
            if proc.poll() is not None and not group_exists(proc.pid):
                # Drain already-buffered owned bytes without extending the deadline.
                wait = 0
            else:
                wait = min(0.05, max(0, deadline-time.monotonic()))
            events = sel.select(wait)
            for key, _ in events:
                try:
                    raw = os.read(key.fd, 8192)
                except OSError:
                    raw = b''
                if raw:
                    capture.write(key.data, raw)
                else:
                    sel.unregister(key.fileobj)
            if proc.poll() is not None and not group_exists(proc.pid) and not events:
                return True
        return proc.poll() is not None and not group_exists(proc.pid)
    try:
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.close()
        if drain_until(time.monotonic()+CLOSE_SECONDS):
            return 'CLOSED'
        cleanup = 'CLOSED'
        for sig, wait, result in ((signal.SIGTERM, TERM_SECONDS, 'TERMINATED'), (signal.SIGKILL, KILL_SECONDS, 'KILLED')):
            # The caller owns all poll/wait custody until this function returns.
            # A poll can reap the leader during either drain. Once reaped, a
            # numeric PGID can prove absence, but cannot authorize another signal.
            if proc.poll() is not None:
                return cleanup if not group_exists(proc.pid) else 'UNKNOWN'
            try:
                os.killpg(proc.pid, sig)
            except ProcessLookupError:
                pass
            else:
                cleanup = result
            if drain_until(time.monotonic()+wait):
                return cleanup
        return 'UNKNOWN'
    finally:
        try:
            proc.wait(timeout=0.05)
        except subprocess.TimeoutExpired:
            pass
        for stream in (proc.stdout, proc.stderr):
            if stream and not stream.closed:
                stream.close()
        sel.close()


def drive_owned_pipes(observer, proc, private):
    """Transport loop; caller has already proved ownership. Also used with inert producers."""
    capture = Capture(private)
    sel = selectors.DefaultSelector()
    buffer = bytearray()
    started = time.monotonic(); reply_at = None
    cleanup = 'UNKNOWN'
    try:
        for name, stream in (('stdout', proc.stdout), ('stderr', proc.stderr)):
            os.set_blocking(stream.fileno(), False)
            sel.register(stream, selectors.EVENT_READ, name)
        if capture.failed:
            observer.finish('RETENTION_FAILURE')
        # Inspect already readable stdout before preparing any request. This is
        # observed read order; it cannot prove the emitter's causal timing.
        if observer.terminal == 'OPEN':
            for key, _ in sel.select(0):
                raw = os.read(key.fd, 8192)
                if raw and not capture.write(key.data, raw):
                    observer.finish('RETENTION_FAILURE' if capture.failed else
                        ('TOTAL_STDOUT_LIMIT' if key.data == 'stdout' else 'STDERR_LIMIT'))
                if key.data == 'stdout':
                    if raw:
                        line, sep, _ = raw.partition(b'\n')
                        if sep:
                            observer.frame(line)
                        else:
                            observer.finish('UNSOLICITED_BEFORE_SEND')
                    else:
                        observer.finish('EOF')
        if observer.terminal == 'OPEN':
            request = observer.request()
            private_write(private, 'initialize-request.jsonl', request)
            try:
                # A single nonblocking sub-PIPE_BUF write; partial write is terminal.
                os.set_blocking(proc.stdin.fileno(), False)
                sent = os.write(proc.stdin.fileno(), request)
                if sent != len(request):
                    observer.finish('WRITE_FAILURE')
            except OSError:
                observer.finish('WRITE_FAILURE')
        while observer.terminal == 'OPEN':
            now = time.monotonic()
            if now - started >= INIT_SECONDS:
                observer.finish('INITIALIZE_TIMEOUT'); break
            if reply_at is not None and now - reply_at >= AFTER_REPLY_SECONDS:
                observer.finish('MATCHED_REPLY_THEN_QUIET'); break
            events = sel.select(min(0.05, max(0, INIT_SECONDS-(now-started))))
            for key, _ in events:
                try:
                    raw = os.read(key.fd, 8192)
                except OSError:
                    observer.finish('READ_FAILURE'); break
                if not raw:
                    sel.unregister(key.fileobj)
                    if key.data == 'stdout':
                        observer.finish('TRUNCATED_FRAME' if buffer else 'EOF')
                    continue
                complete = capture.write(key.data, raw)
                if not complete:
                    observer.finish('RETENTION_FAILURE' if capture.failed else
                        ('TOTAL_STDOUT_LIMIT' if key.data == 'stdout' else 'STDERR_LIMIT'))
                    break
                if key.data == 'stderr':
                    continue
                buffer.extend(raw)
                while b'\n' in buffer and observer.terminal == 'OPEN':
                    line, _, rest = buffer.partition(b'\n'); buffer[:] = rest
                    if len(line) > MAX_FRAME:
                        observer.finish('FRAME_LIMIT'); break
                    observer.frame(bytes(line))
                    if observer.reply and reply_at is None:
                        reply_at = time.monotonic()
                if len(buffer) > MAX_FRAME and observer.terminal == 'OPEN':
                    observer.finish('FRAME_LIMIT')
                if observer.terminal != 'OPEN':
                    break
            if proc.poll() is not None and not sel.get_map() and observer.terminal == 'OPEN':
                observer.finish('PROCESS_EXIT')
    except (KeyboardInterrupt, SystemExit):
        observer.finish('INTERRUPTED')
    except Exception:
        observer.finish('INTERNAL_FAILURE')
    finally:
        try:
            cleanup = stop_owned(proc, sel, capture)
        except Exception:
            cleanup = 'UNKNOWN'
        finally:
            capture.close()
    return {'cleanup': cleanup,
            'private_retention': 'PARTIAL_RETENTION_FAILURE' if capture.failed else 'RETAINED_LOCAL_ONLY', 'stdout_bytes_retained': capture.counts['stdout'],
            'stderr_bytes_retained': capture.counts['stderr'], 'stdout_truncated': capture.truncated['stdout'],
            'stderr_truncated': capture.truncated['stderr'], 'elapsed_bucket': elapsed_bucket(time.monotonic()-started)}


def elapsed_bucket(seconds):
    return 'UNDER_1_SECOND' if seconds < 1 else ('UNDER_5_SECONDS' if seconds < 5 else ('UNDER_15_SECONDS' if seconds < 15 else '15_SECONDS_OR_MORE'))


def retain_warning_custody(prepared, receipt):
    """Post-cleanup observation only; never replace the original guard/terminal result."""
    status = receipt['warning_custody']
    if status['status'] != 'NOT_REACHED':
        return
    report = receipt.get('observer')
    warning = report.get('warning') if type(report) is dict else None
    if type(warning) is not dict or warning.get('category') != 'OTHER_SCHEMA_VALID' or warning.get('profile') != 'CLOSED_STARTUP_WARNING':
        status['status'] = 'NOT_REQUIRED'
        return
    if receipt.get('process_bound') is not True or receipt.get('cleanup') not in {'CLOSED', 'TERMINATED', 'KILLED'}:
        status['status'] = 'CLEANUP_UNRESOLVED'
        return
    failure = 'CRYPTO_REFUSED'
    try:
        custody.preflight(prepared.request)
        failure = 'CAPTURE_REFUSED'
        capture, _, _ = stable_file(prepared.private / 'stdout.bin', MAX_STDOUT, private=True)
        frame = custody.select_frame(capture, report, prepared.config)
        failure = 'CRYPTO_REFUSED'
        recipient = custody.load_recipient()
        envelope = custody.encrypt_frame(frame, public_key=bytes.fromhex(recipient['public_key_hex']),
            request_digest=prepared.request_digest, crypto_sha256=prepared.request['crypto_dependency_sha256'],
            record_ordinal=report['records'])
        custody.validate_envelope(envelope, expected_request_digest=prepared.request_digest,
            expected_crypto_sha256=prepared.request['crypto_dependency_sha256'],
            expected_recipient_sha256=prepared.request['recipient_sha256'])
        failure = 'WRITE_FAILED'
        private_write(prepared.private, 'WARNING.enc.json', envelope)
        status.update(status='SEALED', ciphertext_sha256=sha(envelope), ciphertext_bytes=len(envelope))
    except BaseException:
        # No arbitrary exception string or private warning has a public output slot.
        status['status'] = failure


def observe_owned(prepared, proc):
    """Consume one prepared session after root's independent effect-time admission.

    No retry and no new process is created. Binding failure leaves the alleged process
    to its root owner; this component cannot safely kill an unbound process group.
    """
    need(type(prepared) is Prepared and not prepared.used, 'PREPARED_SESSION_REQUIRED')
    prepared.used = True
    receipt = prepared.receipt
    observer = None
    try:
        validate_request(prepared.request)
        spec = prepared.launch_spec()
        # Hold the originally bound authored file and executable identity up to receive.
        need(fingerprint(Path(prepared.request['binary']).lstat()) == prepared.binary_identity, 'BINARY_PREIMAGE_CHANGED')
        need(fingerprint((Path(prepared.request['home'])/'config.toml').lstat()) == prepared.config_identity, 'CONFIG_PREIMAGE_CHANGED')
        verify_owned_process(proc, argv=spec['argv'], env=spec['env'], cwd=spec['cwd'], binary_sha256=prepared.request['binary_sha256'])
        receipt['process_bound'] = True
    except BaseException as exc:
        receipt['status'] = 'PROCESS_BINDING_REFUSED'; receipt['cleanup'] = 'ROOT_CLEANUP_REQUIRED'
        private_write(prepared.private, 'binding-refusal.json', encoded({'status': 'PROCESS_BINDING_REFUSED', 'failure_code': closed_failure(exc), 'initialized_sent': False}))
        atomic_public(prepared.root, receipt)
        return receipt
    try:
        observer = Observer(prepared.config, prepared.request_digest, pinned=prepared.pinned, process=proc)
        receipt.update(drive_owned_pipes(observer, proc, prepared.private))
        receipt['observer'] = observer.report()
        receipt['status'] = 'INTERRUPTED' if observer.terminal == 'INTERRUPTED' else 'STOPPED'
        private_write(prepared.private, 'terminal.json', encoded({'request_digest': prepared.request_digest,
            'guard_result': observer.guard_result, 'terminal': observer.terminal,
            'cleanup': receipt['cleanup'], 'native_exit_status': proc.returncode}))
        retain_warning_custody(prepared, receipt)
        atomic_public(prepared.root, receipt)
        return receipt
    except BaseException:
        # Unexpected outer failures still retain prior raw files; the root receives no success claim.
        receipt['status'] = 'INTERNAL_FAILURE'
        receipt['cleanup'] = 'ROOT_CLEANUP_REQUIRED' if group_exists(proc.pid) else receipt['cleanup']
        receipt['observer'] = None
        atomic_public(prepared.root, receipt)
        return receipt


def validate_receipt(value):
    keys = {'schema','authority','request_digest','status','observer','process_bound','cleanup','private_retention',
            'stdout_bytes_retained','stderr_bytes_retained','stdout_truncated','stderr_truncated','elapsed_bucket',
            'admission_established_by_candidate', 'warning_custody'}
    need(type(value) is dict and set(value) == keys, 'PUBLIC_RECEIPT_KEYS')
    need(value['schema'] == RECEIPT_SCHEMA and value['authority'] == 'NONE' and
         type(value['private_retention']) is str and value['private_retention'] in
         {'RETAINED_LOCAL_ONLY','PARTIAL_RETENTION_FAILURE'}, 'PUBLIC_RECEIPT_CONSTANTS')
    need(type(value['request_digest']) is str and re.fullmatch('[0-9a-f]{64}', value['request_digest']), 'PUBLIC_RECEIPT_BINDING')
    need(type(value['status']) is str and value['status'] in RUN_RESULTS and
         type(value['cleanup']) is str and value['cleanup'] in CLEANUP_RESULTS and
         type(value['elapsed_bucket']) is str and value['elapsed_bucket'] in {'UNDER_1_SECOND','UNDER_5_SECONDS','UNDER_15_SECONDS','15_SECONDS_OR_MORE'}, 'PUBLIC_RECEIPT_ENUM')
    for key in ('process_bound','stdout_truncated','stderr_truncated','admission_established_by_candidate'):
        need(type(value[key]) is bool, 'PUBLIC_RECEIPT_BOOL')
    need(value['admission_established_by_candidate'] is False, 'PUBLIC_AUTHORITY')
    for key, maximum in (('stdout_bytes_retained', MAX_STDOUT), ('stderr_bytes_retained', MAX_STDERR)):
        need(type(value[key]) is int and 0 <= value[key] <= maximum, 'PUBLIC_RECEIPT_COUNT')
    if value['observer'] is not None:
        validate_public(value['observer'])
        need(value['observer']['request_digest'] == value['request_digest'], 'PUBLIC_CROSS_REQUEST')
    custody.validate_status(value['warning_custody'], expected_request_digest=value['request_digest'])
    if value['warning_custody']['status'] == 'SEALED':
        need(value['process_bound'] is True and value['cleanup'] in {'CLOSED', 'TERMINATED', 'KILLED'}
             and type(value['observer']) is dict and type(value['observer']['warning']) is dict
             and value['observer']['warning']['profile'] == 'CLOSED_STARTUP_WARNING'
             and value['observer']['warning']['category'] == 'OTHER_SCHEMA_VALID', 'PUBLIC_CUSTODY_TRIGGER')
    return encoded(value)


if __name__ == '__main__':
    # Deliberately no command line native launcher or GO interpretation.
    print('{"schema":"dg18.c02.startup-seam.v1","status":"ROOT_ADMISSION_WRAPPER_REQUIRED","authority":"NONE"}')
    raise SystemExit(2)
