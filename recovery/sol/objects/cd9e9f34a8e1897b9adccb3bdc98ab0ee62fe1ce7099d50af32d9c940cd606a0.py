"""Root-invoked, one-shot Linux TTY artifact role. No MCP dispatch or auto-resume.

Root must issue/authenticate the configuration and admission outside this
process. Exact matching JSON is not authentication. Only the pinned existing
receiver and resolver perform acquisition, durable receiving and one body GET.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
import types
import urllib.parse

ISSUER = '01a1953f-a15b-7811-aa72-3538ebb03562'
ROLE_ROOT = Path('/home/agent/dg16-g1-current04-operators/public-receiver-02')
RECEIVER_SHA = '378846f9cfd5f60ce3e3b48adb3c2e3c7cf94a701ed9aee46e5ba3072f4fc122'
RESOLVER_SHA = 'b2ac1130149d9878a3a00c7d8ba214743920a1aede38cb6b75699e14a2d03530'
PROFILE = 'ONE_PINNED_G1_FRAMED_TTY_ROLE_V1'


def need(ok, code):
    if not ok:
        raise ValueError(code)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def parse(raw):
    def pairs(rows):
        out = {}
        for key, value in rows:
            need(key not in out, 'DUPLICATE_KEY')
            out[key] = value
        return out
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'NONFINITE'))


def no_credentials(raw):
    """Reject credential-shaped unexpected metadata before Session.retain writes.

    Download wrappers deliberately bypass this function: the pinned resolver
    retains only its validated redacted note, while the original stays in RAM.
    """
    value = parse(raw)
    secret_keys = {'authorization', 'password', 'accesstoken', 'refreshtoken',
                   'clientsecret', 'secretaccesskey', 'apikey', 'token',
                   'completiontoken', 'credential', 'credentials'}
    query_keys = secret_keys | {'sig', 'signature', 'xgoogsignature', 'xgoogcredential'}
    def visit(item, depth=0):
        need(depth <= 64, 'METADATA_DEPTH')
        if type(item) is dict:
            for key, child in item.items():
                if re.sub('[-_]', '', key.lower()) in secret_keys:
                    need(child in (None, '', False), 'CREDENTIAL_METADATA_REFUSED')
                visit(child, depth+1)
        elif type(item) is list:
            for child in item:
                visit(child, depth+1)
        elif type(item) is str:
            need(not re.search(r'(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}|\bgh[pousr]_[A-Za-z0-9]{20,}', item),
                 'CREDENTIAL_METADATA_REFUSED')
            for url in re.findall(r'https?://[^\s<>"\']+', item):
                parts = urllib.parse.urlsplit(url)
                keys = {re.sub('[-_]', '', urllib.parse.unquote(k).lower()) for k in urllib.parse.parse_qs(parts.query)}
                need(not parts.username and not parts.password and
                     not keys.intersection(query_keys) and
                     not any(k.startswith('xamz') for k in keys) and
                     not (parts.hostname or '').endswith('.oaiusercontent.com'),
                     'SIGNED_METADATA_REFUSED')
            if item.lstrip().startswith(('{', '[')):
                try:
                    nested = parse(item.encode())
                except (ValueError, TypeError, RecursionError):
                    return
                visit(nested, depth+1)
    visit(value)


def run_role(R, X, session, deadline_unix_ms, *, previous=None, actual_root_raw=None,
             emit=None, now_ms=None, transport=None):
    """Actual role loop; tests inject inert R/X/transport, never a real GET."""
    emit = emit or (lambda v: print(encode(v).decode(), end='', flush=True))
    now_ms = now_ms or (lambda: time.time_ns()//1000000)
    pending = None
    raw = None
    def remaining():
        left = (deadline_unix_ms-now_ms())/1000
        need(left > 0, 'EXISTING_ROOT_DEADLINE_EXPIRED')
        return left
    try:
        need(type(deadline_unix_ms) is int and 0 < deadline_unix_ms-now_ms() <= 600000,
             'EXISTING_ROOT_DEADLINE_REQUIRED')
        for kind in R.ORDER:
            remaining()
            pending = kind
            intent = session.reserve(kind)  # Existing O_EXCL/fsync intent, not a planned substitute.
            remaining()                    # Reservation itself may cross the deadline.
            emit({'event': 'intent', 'intent': intent})
            raw = X.read_ephemeral_frame(R.MAX_RESULT, seconds=min(45.0, remaining()))
            need(type(raw) is bytes and 0 < len(raw) <= R.MAX_RESULT, 'ACTUAL_FRAME_BOUND')
            remaining()
            if kind == 'download':
                X.receive_download_for_resolution(R, session, raw)
                remaining()
                original_watchdog = X.WATCHDOG_SECONDS
                try:
                    X.WATCHDOG_SECONDS = min(original_watchdog, remaining())
                    def bounded_transport(url, maximum, seconds):
                        timeout = min(seconds, remaining())
                        return (X.fetch_once if transport is None else transport)(url, maximum, timeout)
                    outcome = X.resolve(R, session, raw, transport=bounded_transport)
                finally:
                    X.WATCHDOG_SECONDS = original_watchdog
                    raw = None
                remaining()
                need(outcome.get('status') == 'RECEIVED', 'BODY_REFUSED_OR_UNKNOWN')
                emit({'event': 'retained', 'kind': kind, 'body_get_done': True,
                      'receipt': outcome})
            else:
                no_credentials(raw)  # No error-shaped signed/token-bearing data reaches disk.
                receipt = session.retain(kind, raw)
                raw = None
                remaining()
                emit({'event': 'retained', 'kind': kind, 'receipt': receipt})
            pending = None
        remaining()
        pending = 'receiving'
        got = session.receive(now_ms(), previous=previous, actual_root_raw=actual_root_raw)
        remaining()
        saved = R.parse(R.read(session.path/'RECEIVING.json'))
        need(R.encode(saved) == R.encode(got['receipt']), 'SAVED_RECEIVING_CHANGED')
        if session.plan['phase'] in ('tools', 'g3_initial', 'g3_final'):
            requirements = R.requirements(session.s, got)
            session.write('REQUIREMENTS.json', R.encode(requirements))  # Requests only; never issuer bytes.
        remaining()
        emit({'event': 'complete', 'receipt': got['receipt']})
        return got
    except BaseException:
        raw = None
        try:
            session.write('ROLE_UNKNOWN.json', R.encode(dict(authority='NONE',
                          status='UNKNOWN_NO_REPLAY', pending=pending, automatic_retry=False,
                          raw_frame_retained=False, no_effect_inferred=False)))
        except BaseException:
            pass
        emit({'event': 'failure', 'status': 'UNKNOWN_NO_REPLAY'})
        return None
    finally:
        raw = None


def owned_read(path, maximum, *, source=False):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path and
         path.is_relative_to(ROLE_ROOT), 'FIXED_ROLE_PATH')
    for parent in reversed(path.parents):
        info = parent.lstat()
        need(stat.S_ISDIR(info.st_mode) and not parent.is_symlink() and
             not getattr(info, 'st_file_attributes', 0) & 0x400, 'ROLE_ANCESTOR_ALIAS')
    before = path.lstat()
    modes = (0o400, 0o444) if source else (0o400, 0o600)
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
         before.st_uid == os.geteuid() and stat.S_IMODE(before.st_mode) in modes and
         0 <= before.st_size <= maximum, 'ROLE_FILE_CUSTODY')
    fd = os.open(path, os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    mark = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_uid, s.st_gid,
                      s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    try:
        need(mark(os.fstat(fd)) == mark(before), 'ROLE_FILE_OPEN_CHANGED')
        chunks = []; count = 0
        while True:
            block = os.read(fd, min(65536, maximum+1-count))
            if not block:
                break
            chunks.append(block); count += len(block)
            need(count <= maximum, 'ROLE_FILE_BOUND')
        need(count == before.st_size and mark(os.fstat(fd)) == mark(before) == mark(path.lstat()),
             'ROLE_FILE_CLOSING_CHANGED')
        return b''.join(chunks)
    finally:
        os.close(fd)


def main(argv=None):
    need(os.name == 'posix' and sys.platform == 'linux' and os.getuid() == os.geteuid() > 0
         and sys.flags.isolated and sys.dont_write_bytecode and sys.stdin.isatty(),
         'ROOT_INVOKED_ISOLATED_NONROOT_LINUX_TTY_REQUIRED')
    argv = sys.argv[1:] if argv is None else argv
    need(len(argv) == 4 and argv[0] == '--configuration' and
         argv[2] == '--configuration-sha256' and re.fullmatch('[0-9a-f]{64}', argv[3]),
         'ACTUAL_CONFIGURATION_AND_HASH_REQUIRED')
    config_raw = owned_read(argv[1], 65536)
    need(digest(config_raw) == argv[3], 'ACTUAL_CONFIGURATION_CHANGED')
    c = parse(config_raw)
    fields = {'schema','issuer_thread','phase','context','session_directory','deadline_unix_ms',
              'admission','initial_session','actual_root_decision'}
    need(type(c) is dict and set(c) == fields and c['schema'] == 'dg16.g1-framed-role-configuration.v1'
         and c['issuer_thread'] == ISSUER, 'EXACT_ROOT_CONFIGURATION')
    def bound_input(row, maximum):
        need(type(row) is dict and set(row) == {'path','sha256'}, 'EXACT_INPUT_DESCRIPTOR')
        body = owned_read(row['path'], maximum)
        need(digest(body) == row['sha256'], 'ROOT_INPUT_CHANGED')
        return body
    context_raw = bound_input(c['context'], 16384)
    admission = parse(bound_input(c['admission'], 65536))
    expected = dict(schema='dg16.g1-framed-role-admission.v1', issuer_thread=ISSUER,
                    status='ADMIT_ONE_ROOT_FRAMED_ARTIFACT_ROLE', profile=PROFILE,
                    phase=c['phase'], context=c['context'], session_directory=c['session_directory'],
                    deadline_unix_ms=c['deadline_unix_ms'], receiver_sha256=RECEIVER_SHA,
                    resolver_sha256=RESOLVER_SHA, automatic_retry=False, original_awards=[])
    need(admission == expected and type(admission['deadline_unix_ms']) is int,
         'ACTUAL_ROOT_ROLE_ADMISSION_REQUIRED')
    need(type(c['deadline_unix_ms']) is int and 0 < c['deadline_unix_ms']-time.time_ns()//1000000 <= 600000,
         'EXISTING_ROOT_DEADLINE_REQUIRED')
    loaded = []
    for name, wanted in (('receiver', RECEIVER_SHA), ('resolve_artifact', RESOLVER_SHA)):
        path = ROLE_ROOT/'author'/(name+'.py')
        body = owned_read(path, 1024**2, source=True)
        need(digest(body) == wanted, 'FIXED_ROOT_DEPENDENCY_CHANGED')
        m = types.ModuleType('root_framed_'+name); m.__file__ = str(path)
        exec(compile(body, str(path), 'exec'), m.__dict__)
        loaded.append(m)
    R, X = loaded
    s = R.Sources(); context = R.parse(context_raw); s.context(context)
    directory = Path(c['session_directory'])
    need(directory.is_absolute() and directory.parent.resolve(strict=True) == directory.parent
         and directory.is_relative_to(ROLE_ROOT/'sessions') and not os.path.lexists(directory),
         'FRESH_SELECTED_ROLE_DIRECTORY')
    previous = None
    if c['initial_session'] is not None:
        old_path = Path(c['initial_session'])
        need(old_path.is_absolute() and old_path.resolve(strict=True) == old_path and
             old_path.is_relative_to(ROLE_ROOT/'sessions'), 'FIXED_INITIAL_SESSION')
        old = R.Session(old_path, s); saved = R.parse(R.read(old.path/'RECEIVING.json'))
        previous = old.receive(saved['observed_unix_ms'], save=False)
        need(R.encode(previous['receipt']) == R.encode(saved), 'INITIAL_RECEIVING_CHANGED')
    actual_root_raw = None if c['actual_root_decision'] is None else bound_input(c['actual_root_decision'], 8192)
    need(time.time_ns()//1000000 < c['deadline_unix_ms'], 'ROOT_DEADLINE_BEFORE_SESSION')
    session = R.Session.create(directory, s, c['phase'], context)
    session.write('ROLE_CONFIGURATION.json', R.encode(dict(configuration_sha256=argv[3],
                  admission=c['admission'], deadline_unix_ms=c['deadline_unix_ms'],
                  authentication='ACTUAL_NATIVE_ROOT_INVOCATION_AND_HISTORY_REQUIRED_NOT_JSON_LABELS')))
    return 0 if run_role(R, X, session, c['deadline_unix_ms'], previous=previous,
                         actual_root_raw=actual_root_raw) is not None else 1


if __name__ == '__main__':
    try:
        status = main()
    except BaseException:
        print('{"event":"failure","status":"UNKNOWN_NO_REPLAY"}', flush=True)
        status = 1
    raise SystemExit(status)
