#!/usr/bin/env python3
"""Fail-closed APT V3 transaction gate, invoked only by separately admitted setup.

The pre hook inspects APT's actual ordered package actions before any dpkg call.
It checks the full clean package prestate under APT's retained frontend lock.
The post hook reconciles the completed package state under that same lock.
Import is inert. No subprocess, package operation or permission repair exists here.
"""
from pathlib import Path
import fcntl
import fnmatch
import hashlib
import json
import os
import re
import shlex
import signal
import stat
import struct
import sys
from urllib.parse import unquote_to_bytes

SCHEMA = 'dg18.c02.apt-transaction-request.v1'
APT_VERSIONS = ('2.8.3', '2.8.4ubuntu0.1')
STATUS = '/var/lib/dpkg/status'
FRONTEND_LOCK = '/var/lib/dpkg/lock-frontend'
VERSION = r'[A-Za-z0-9.+:~\-]+'
CAPTURE_LIMIT = 1048576
REQUEST_LIMIT = 8388608
STATUS_LIMIT = 33554432
HOOK_SECONDS = 10
FLOCK_FORMAT = 'hhqqi4x'  # supported Linux amd64 ABI; qualified by an owned-file test


class Refusal(Exception):
    pass


def need(value, code):
    if not value:
        raise Refusal(code)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(st):
    return [st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid, st.st_nlink,
            st.st_size, st.st_mtime_ns, st.st_ctime_ns]


def read_regular(path, limit, owner=None, digest=None):
    """Stable single-link, non-symlink leaf read; never follows a final symlink."""
    path = Path(path)
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
         0 <= before.st_size <= limit and not before.st_mode & 0o022, 'APT_GATE_FILE_SHAPE')
    need(owner is None or before.st_uid == owner, 'APT_GATE_FILE_OWNER')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        need(identity(before) == identity(os.fstat(fd)), 'APT_GATE_FILE_RACE')
        body = bytearray()
        while chunk := os.read(fd, min(1048576, limit + 1 - len(body))):
            body.extend(chunk)
            need(len(body) <= limit, 'APT_GATE_FILE_BOUND')
        need(len(body) == before.st_size and identity(before) == identity(os.fstat(fd)) ==
             identity(path.lstat()), 'APT_GATE_FILE_RACE')
    finally:
        os.close(fd)
    raw = bytes(body)
    need(digest is None or sha(raw) == digest, 'APT_GATE_FILE_DIGEST')
    return raw, identity(before)


def protected_ancestry(path):
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts, 'APT_GATE_PATH')
    for parent in (path, *path.parents):
        st = parent.lstat()
        need(st.st_uid == 0 and not st.st_mode & 0o022 and
             (stat.S_ISREG(st.st_mode) if parent == path else stat.S_ISDIR(st.st_mode)),
             'APT_GATE_PROTECTED_PATH')


def package_records(raw):
    """Read the complete Deb822 database, retaining every field in each hash."""
    need(0 < len(raw) <= STATUS_LIMIT and raw.endswith(b'\n') and b'\0' not in raw,
         'APT_GATE_STATUS_BOUND')
    records = {}
    for paragraph in raw.decode('utf-8', 'strict').strip().split('\n\n'):
        fields, last = {}, None
        for line in paragraph.splitlines():
            if line[:1] in (' ', '\t'):
                need(last is not None, 'APT_GATE_STATUS_CONTINUATION')
                fields[last] += '\n' + line
                continue
            need(':' in line, 'APT_GATE_STATUS_FIELD')
            key, value = line.split(':', 1)
            need(re.fullmatch(r'[A-Za-z][A-Za-z0-9-]*', key) and key not in fields,
                 'APT_GATE_STATUS_DUPLICATE_FIELD')
            fields[key], last = value.lstrip(), key
        name, arch = fields.get('Package', ''), fields.get('Architecture', '')
        version, state = fields.get('Version', ''), fields.get('Status', '')
        need(re.fullmatch(r'[a-z0-9][a-z0-9+.-]+', name) and
             re.fullmatch(r'[a-z0-9][a-z0-9-]*', arch) and
             re.fullmatch(VERSION, version), 'APT_GATE_STATUS_IDENTITY')
        need(state in ('install ok installed', 'hold ok installed', 'deinstall ok config-files') and
             not fields.get('Triggers-Pending') and not fields.get('Triggers-Awaited'),
             'APT_GATE_UNCLEAN_PACKAGE_STATE')
        key = name + ':' + arch
        need(key not in records, 'APT_GATE_STATUS_DUPLICATE_PACKAGE')
        records[key] = {'version': version, 'status': state, 'record_sha256': sha(encoded(fields))}
    need(records, 'APT_GATE_EMPTY_PACKAGE_STATE')
    return records


def read_snapshot():
    protected_ancestry(STATUS)
    updates = Path('/var/lib/dpkg/updates')
    st = updates.lstat()
    need(stat.S_ISDIR(st.st_mode) and st.st_uid == 0 and not st.st_mode & 0o022 and
         not list(updates.iterdir()), 'APT_GATE_PENDING_DPKG_UPDATES')
    pending = '/var/lib/dpkg/triggers/Unincorp'
    protected_ancestry(pending)
    pending_raw, _ = read_regular(pending, CAPTURE_LIMIT, owner=0)
    need(not pending_raw.strip(), 'APT_GATE_PENDING_TRIGGERS')
    raw, binding = read_regular(STATUS, STATUS_LIMIT, owner=0)
    records = package_records(raw)
    need(not list(updates.iterdir()), 'APT_GATE_PENDING_DPKG_UPDATES')
    return {'records': records, 'records_sha256': sha(encoded(records)),
            'status_sha256': sha(raw), 'status_identity': binding}


def require_supported_apt(snapshot):
    records = snapshot['records']
    apt, library = records.get('apt:amd64'), records.get('libapt-pkg6.0t64:amd64')
    need(apt and library and apt['status'] == library['status'] == 'install ok installed' and
         apt['version'] == library['version'] and apt['version'] in APT_VERSIONS,
         'APT_GATE_UNQUALIFIED_APT_VERSION')
    need(not any(key.split(':')[0] == 'bubblewrap' for key in records), 'APT_GATE_BUBBLEWRAP_PRESENT')
    return apt['version']


def dpkg_configuration():
    """Bind the existing dpkg config without changing or bypassing its policy."""
    paths = [Path('/etc/dpkg/dpkg.cfg')]
    directory = Path('/etc/dpkg/dpkg.cfg.d')
    def fragments():
        st = directory.lstat()
        need(stat.S_ISDIR(st.st_mode) and st.st_uid == 0 and not st.st_mode & 0o022,
             'APT_GATE_DPKG_CONFIG_DIRECTORY')
        # dpkg documents a shell pattern: only the FIRST character is restricted.
        # The trailing '*' includes dotted names and other suffix characters.
        return sorted(p for p in directory.iterdir()
                      if fnmatch.fnmatchcase(p.name, '[0-9a-zA-Z_-]*'))
    selected = fragments()
    paths += selected
    result = {}
    for path in paths:
        protected_ancestry(path)
        raw, binding = read_regular(path, 65536, owner=0)
        for line in raw.decode('ascii', 'strict').splitlines():
            option = line.strip()
            need(not option or option.startswith('#') or
                 option in ('no-debsig', 'log /var/log/dpkg.log', 'log=/var/log/dpkg.log'),
                 'APT_GATE_DPKG_CONFIG_OPTION')
        result[str(path)] = {'sha256': sha(raw), 'identity': binding}
    names = [str(path) for path in selected]
    need([str(path) for path in fragments()] == names, 'APT_GATE_DPKG_CONFIG_POPULATION_CHANGED')
    # Recheck every captured member, including main config, before accepting
    # the census. A changed byte/identity or added/removed eligible name refuses.
    for path in paths:
        protected_ancestry(path)
        raw, binding = read_regular(path, 65536, owner=0)
        need(result[str(path)] == {'sha256': sha(raw), 'identity': binding},
             'APT_GATE_DPKG_CONFIG_CHANGED_DURING_CAPTURE')
    need([str(path) for path in fragments()] == names, 'APT_GATE_DPKG_CONFIG_POPULATION_CHANGED')
    return result


def decode_config(text):
    need(not re.search(r'%(?![0-9A-Fa-f]{2})', text), 'APT_GATE_PROTOCOL_ESCAPE')
    return unquote_to_bytes(text).decode('utf-8', 'strict')


def validate_protocol(raw, request):
    need(0 < len(raw) <= CAPTURE_LIMIT and raw.endswith(b'\n') and b'\0' not in raw,
         'APT_GATE_PROTOCOL_BOUND')
    lines = raw.decode('utf-8', 'strict').splitlines()
    need(lines and lines.pop(0) == 'VERSION 3' and '' in lines, 'APT_GATE_PROTOCOL_VERSION')
    end = lines.index('')
    config = {}
    for line in lines[:end]:
        need('=' in line, 'APT_GATE_PROTOCOL_CONFIG')
        key, value = line.split('=', 1)
        config.setdefault(decode_config(key).lower(), []).append(decode_config(value))
    for key, expected in request['critical_config'].items():
        need(config.get(key.lower()) == [expected], 'APT_GATE_EFFECTIVE_CONFIG')
    forbidden = ('dpkg::pre-invoke', 'dpkg::options', 'debug::', 'apt::update::',
                 'apt::install::', 'dpkg::chroot-directory')
    need(not any(any(key == prefix or key.startswith(prefix + '::') or
                     (prefix.endswith('::') and key.startswith(prefix)) for prefix in forbidden)
                 for key in config), 'APT_GATE_EXTRA_HOOK_OR_OVERRIDE')
    need(config.get('dpkg::pre-install-pkgs::') == [request['pre_command']] and
         config.get('dpkg::post-invoke::') == [request['post_command']], 'APT_GATE_HOOK_POPULATION')
    need(all(key in ('dpkg::pre-install-pkgs::', 'dpkg::post-invoke::') for key in config
             if key.startswith(('dpkg::pre-install-pkgs', 'dpkg::post-invoke'))),
         'APT_GATE_HOOK_POPULATION')
    rows = [line.split() for line in lines[end + 1:]]
    need(len(rows) == 2 and all(len(row) == 9 for row in rows), 'APT_GATE_TRANSACTION_POPULATION')
    expected = ['bubblewrap', '-', '-', 'none', '<', request['version'], 'amd64']
    need(all(row[:7] == expected and row[7] in ('none', 'foreign', 'allowed', 'same') for row in rows) and
         rows[0][7] == rows[1][7], 'APT_GATE_TRANSACTION_IDENTITY')
    archive = Path(rows[0][8])
    need(archive.is_absolute() and archive.parent == Path(request['directory']) / 'archives' and
         re.fullmatch(r'bubblewrap_[A-Za-z0-9.+:%~\-]+_amd64\.deb', archive.name) and
         rows[1][8] == '**CONFIGURE**', 'APT_GATE_TRANSACTION_ACTION')
    return {'install': ['bubblewrap=' + request['version']], 'upgrade': [], 'remove': [],
            'archive': str(archive), 'protocol_sha256': sha(raw)}


def proc_record(pid):
    raw = Path('/proc/' + str(pid) + '/stat').read_bytes()
    tail = raw.rsplit(b') ', 1)[1].split()
    need(len(tail) >= 20, 'APT_GATE_PROC_STAT')
    return {'pid': pid, 'ppid': int(tail[1]), 'start_ticks': int(tail[19])}


def lock_owner(path=FRONTEND_LOCK):
    """Query only. F_GETLK neither acquires nor releases a system lock."""
    need(struct.calcsize(FLOCK_FORMAT) == 32, 'APT_GATE_LOCK_ABI')
    before = Path(path).lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'APT_GATE_LOCK_FILE_SHAPE')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        need(identity(before) == identity(os.fstat(fd)), 'APT_GATE_LOCK_FILE_CHANGED')
        result = fcntl.fcntl(fd, fcntl.F_GETLK,
                             struct.pack(FLOCK_FORMAT, fcntl.F_WRLCK, os.SEEK_SET, 0, 0, 0))
        need(identity(before) == identity(os.fstat(fd)) == identity(Path(path).lstat()),
             'APT_GATE_LOCK_FILE_CHANGED')
    finally:
        os.close(fd)
    kind, whence, start, length, pid = struct.unpack(FLOCK_FORMAT, result)
    need(kind == fcntl.F_WRLCK and whence == os.SEEK_SET and start == length == 0 and pid > 0,
         'APT_GATE_FRONTEND_LOCK_NOT_HELD')
    return pid


def check_tool_bindings(request, after=False):
    for path, binding in request['tools'].items():
        resolved = Path(path).resolve(strict=True)
        need(str(resolved) == binding['resolved'], 'APT_GATE_TOOL_PATH_CHANGED')
        for name, saved in binding['path_chain'].items():
            current = Path(name).lstat()
            observed = identity(current)
            wanted = list(saved['identity'])
            # Only post-install parent directory entry timestamps/sizes may move.
            if after and stat.S_ISDIR(observed[2]) and stat.S_ISDIR(wanted[2]):
                observed[6:] = wanted[6:] = [None, None, None]
            need(observed == wanted and current.st_uid == 0 and
                 ((os.readlink(name) if stat.S_ISLNK(current.st_mode) else None) == saved['link']),
                 'APT_GATE_TOOL_BINDING_CHANGED')
        read_regular(resolved, 134217728, owner=0, digest=binding['sha256'])


def custody(request, after=False):
    need(os.geteuid() == 0 and os.environ.get('DPKG_FRONTEND_LOCKED') == 'true',
         'APT_GATE_FRONTEND_CUSTODY')
    protected_ancestry(FRONTEND_LOCK)
    check_tool_bindings(request, after=after)
    owner = lock_owner()
    pid, ancestors = os.getppid(), []
    for _ in range(8):
        record = proc_record(pid)
        ancestors.append(record)
        if pid == owner:
            break
        need(pid > 1 and record['ppid'] != pid, 'APT_GATE_LOCK_OWNER_NOT_ANCESTOR')
        pid = record['ppid']
    need(pid == owner, 'APT_GATE_LOCK_OWNER_NOT_ANCESTOR')
    process = Path('/proc/' + str(owner))
    need(process.stat().st_uid == 0 and os.readlink(process / 'exe') ==
         request['tools']['/usr/bin/apt-get']['resolved'], 'APT_GATE_APT_PROCESS_IDENTITY')
    executable = (process / 'exe').stat()
    bound = request['tools']['/usr/bin/apt-get']['path_chain'][
        request['tools']['/usr/bin/apt-get']['resolved']]['identity']
    need(identity(executable) == bound, 'APT_GATE_APT_PROCESS_BINARY')
    command = (process / 'cmdline').read_bytes()
    need(len(command) <= 65536 and command == b'\0'.join(x.encode() for x in request['apt_argv']) + b'\0',
         'APT_GATE_APT_PROCESS_ARGV')
    need(dpkg_configuration() == request['dpkg_configuration'], 'APT_GATE_DPKG_CONFIG_CHANGED')
    need(lock_owner() == owner and proc_record(owner) == ancestors[-1], 'APT_GATE_LOCK_CUSTODY_CHANGED')
    return ancestors[-1]


def reconcile(before, after, version):
    old, new = before['records'], after['records']
    additions, removals = set(new) - set(old), set(old) - set(new)
    need(additions == {'bubblewrap:amd64'} and not removals and
         all(old[name] == new[name] for name in old), 'APT_GATE_ACTUAL_EFFECT_POPULATION')
    added = new['bubblewrap:amd64']
    need(added['version'] == version and added['status'] == 'install ok installed',
         'APT_GATE_ACTUAL_EFFECT_VERSION')
    return {'install': ['bubblewrap=' + version], 'upgrade': [], 'remove': [],
            'unchanged_package_count': len(old), 'install_count': len(additions)}


def write_receipt(path, receipt):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(encoded(receipt))
        stream.flush()
        os.fsync(stream.fileno())


def load_receipt(path):
    raw, _ = read_regular(path, CAPTURE_LIMIT, owner=0)
    return json.loads(raw), sha(raw)


def run_gate(mode, request, request_sha, protocol=None):
    need(request['schema'] == SCHEMA and mode in ('pre', 'post') and
         re.fullmatch(VERSION, request['version']), 'APT_GATE_REQUEST')
    directory = Path(request['directory'])
    st = directory.lstat()
    need(stat.S_ISDIR(st.st_mode) and not st.st_mode & 0o022 and
         identity(st)[:2] == request['directory_identity'] and st.st_uid == request['owner_uid'],
         'APT_GATE_WORKSPACE_CUSTODY')
    need(read_regular(request['base_config_path'], CAPTURE_LIMIT, owner=request['owner_uid'])[0] ==
         request['base_config'].encode() and
         read_regular(request['source_path'], CAPTURE_LIMIT, owner=request['owner_uid'])[0] ==
         request['source'].encode(), 'APT_GATE_CONFIG_INPUT_CHANGED')
    # Install config includes this request's digest; compare a deterministic
    # rendering here instead of making a self-referential request digest.
    need(read_regular(request['install_config_path'], CAPTURE_LIMIT, owner=request['owner_uid'])[0] ==
         install_config(request, request_sha), 'APT_GATE_INSTALL_CONFIG_CHANGED')
    process = custody(request, after=(mode == 'post'))
    snapshot = read_snapshot()
    if mode == 'pre':
        need(snapshot == request['prestate'], 'APT_GATE_FULL_PRESTATE_CHANGED')
        require_supported_apt(snapshot)
        transaction = validate_protocol(protocol, bound_request(request, request_sha))
        archive_raw, archive_id = read_regular(transaction['archive'], 16777216, owner=0)
        transaction.update(archive_sha256=sha(archive_raw), archive_bytes=len(archive_raw),
                           archive_identity=archive_id)
        receipt = {'schema': 'dg18.c02.apt-before-dpkg.v1', 'status': 'EXACT_ACTUAL_TRANSACTION_ADMITTED',
                   'request_sha256': request_sha, 'apt_process': process,
                   'prestate_sha256': snapshot['records_sha256'], 'transaction': transaction}
    else:
        pre, pre_sha = load_receipt(directory / 'PRE_DPKG.json')
        need(pre['schema'] == 'dg18.c02.apt-before-dpkg.v1' and
             pre['status'] == 'EXACT_ACTUAL_TRANSACTION_ADMITTED' and
             pre['request_sha256'] == request_sha and pre['apt_process'] == process and
             pre['prestate_sha256'] == request['prestate']['records_sha256'], 'APT_GATE_PRE_RECEIPT')
        effects = reconcile(request['prestate'], snapshot, request['version'])
        receipt = {'schema': 'dg18.c02.apt-after-dpkg.v1', 'status': 'EXACT_ACTUAL_EFFECTS_RECONCILED',
                   'request_sha256': request_sha, 'pre_receipt_sha256': pre_sha, 'apt_process': process,
                   'poststate_sha256': snapshot['records_sha256'], 'effects': effects}
    need(read_snapshot() == snapshot and custody(request, after=(mode == 'post')) == process,
         'APT_GATE_FINAL_CUSTODY_CHANGED')
    write_receipt(directory / ('PRE_DPKG.json' if mode == 'pre' else 'POST_DPKG.json'), receipt)
    return receipt


def bootstrap_command(helper, helper_sha, mode, request_path, request_sha):
    # No shell evaluation of request data. Paths/hex are bounded before quoting.
    values = [str(helper), helper_sha, 'exec', str(helper), mode, str(request_path), request_sha]
    need(all(re.fullmatch(r'[A-Za-z0-9_./:+\-]+', x) for x in values), 'APT_GATE_COMMAND_VALUE')
    # The bootstrap reads once and executes the exact hashed bytes, so the
    # interpreter never reopens a mutable script path after checking its digest.
    code = ('import sys,os,stat,hashlib; p=sys.argv.pop(1); h=sys.argv.pop(1); '
            'f=os.open(p,os.O_RDONLY|os.O_NOFOLLOW); s=os.fstat(f); '
            'b=os.read(f,131073); t=os.fstat(f); os.close(f); '
            'assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and len(b)<=131072 '
            'and s==t and len(b)==s.st_size and hashlib.sha256(b).hexdigest()==h; '
            'sys.argv.pop(0); m=sys.argv.pop(0); __file__=sys.argv[0]; exec(compile(b,p,m))')
    command = '/usr/bin/python3 -I -B -c ' + shlex.quote(code) + ' ' + ' '.join(shlex.quote(x) for x in values)
    need('"' not in command and '\n' not in command, 'APT_GATE_CONFIG_QUOTING')
    return command


def bound_request(request, request_sha):
    bound = dict(request)
    args = (request['helper_path'], request['helper_sha256'])
    bound['pre_command'] = bootstrap_command(*args, 'pre', request['request_path'], request_sha)
    bound['post_command'] = bootstrap_command(*args, 'post', request['request_path'], request_sha)
    return bound


def install_config(request, request_sha):
    bound = bound_request(request, request_sha)
    return (request['base_config'] +
            'Dir::State::status "/var/lib/dpkg/status";\nDir::Bin::dpkg "/usr/bin/dpkg";\n'
            'DPkg::Tools::Options::/usr/bin/python3::Version "3";\n'
            'DPkg::Tools::Options::/usr/bin/python3::InfoFD "0";\n'
            'DPkg::Pre-Install-Pkgs { "' + bound['pre_command'] + '"; };\n'
            'DPkg::Post-Invoke { "' + bound['post_command'] + '"; };\n').encode()


def main(argv):
    need(len(argv) == 4 and argv[1] in ('pre', 'post') and
         re.fullmatch(r'[0-9a-f]{64}', argv[3]), 'APT_GATE_ARGUMENTS')
    def timeout(_signum, _frame):
        raise Refusal('APT_GATE_TIMEOUT')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(HOOK_SECONDS)
    try:
        raw, _ = read_regular(argv[2], REQUEST_LIMIT, digest=argv[3])
        request = json.loads(raw)
        need(argv[2] == request['request_path'], 'APT_GATE_REQUEST_PATH')
        protocol = None
        if argv[1] == 'pre':
            need(os.environ.get('APT_HOOK_INFO_FD') == '0', 'APT_GATE_INFO_FD')
            protocol = sys.stdin.buffer.read(CAPTURE_LIMIT + 1)
        run_gate(argv[1], request, argv[3], protocol)
    finally:
        signal.alarm(0)


if __name__ == '__main__':
    try:
        main(sys.argv)
    except Exception as exc:
        # Fixed class/code only. Never copy a config, path, package inventory or
        # arbitrary process output into the public preparation log.
        print(str(exc) if isinstance(exc, Refusal) else 'APT_GATE_UNEXPECTED_REFUSAL', file=sys.stderr)
        sys.exit(74)
