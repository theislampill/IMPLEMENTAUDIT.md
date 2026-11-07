#!/usr/bin/env python3
"""Conservative prerequisite for a separately admitted disposable hosted run.

Never changes namespace policy, file ownership/modes, the warning guard or PATH.
An available executable and an unmatched warning are insufficient: namespace
execution must succeed. Importing this module has no process or install effect.
"""
from pathlib import Path
import hashlib
import json
import os
import platform
import re
import selectors
import signal
import stat
import subprocess
import time

PATH = '/usr/local/bin:/usr/bin:/bin'  # exact unchanged startup_subject environment
BWRAP = '/usr/bin/bwrap'
PROBE_ARGV = [BWRAP, '--unshare-user', '--unshare-net', '--ro-bind', '/', '/', '/bin/true']
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC', 'PYTHONDONTWRITEBYTECODE': '1'}
SCHEMA = 'dg18.c02.system-bwrap-binding.v1'


class Refusal(Exception):
    pass


def need(condition, code):
    if not condition:
        raise Refusal(code)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(st):
    return [st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid, st.st_nlink,
            st.st_size, st.st_mtime_ns, st.st_ctime_ns]


def group_absent(proc):
    try:
        os.killpg(proc.pid, 0)
    except ProcessLookupError:
        return True
    return False


def close_owned(proc):
    # A reaped numeric PGID cannot authorize a later signal.
    for sig in (signal.SIGTERM, signal.SIGKILL):
        if proc.poll() is not None:
            return 'CLOSED' if group_absent(proc) else 'UNKNOWN'
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            continue
        return 'CLOSED' if group_absent(proc) else 'UNKNOWN'
    return 'UNKNOWN'


def run_bounded(argv, *, timeout, limit, env=None, cwd='/'):
    """Real owned process with finite two-stream capture and unreaped-child cleanup."""
    need(type(argv) is list and argv and all(type(x) is str for x in argv), 'HOST_ARGV')
    proc = subprocess.Popen(argv, cwd=cwd, env=ENV if env is None else env,
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True, bufsize=0)
    capture = {'stdout': bytearray(), 'stderr': bytearray()}
    timed_out = overflow = False
    selector = selectors.DefaultSelector()
    deadline = time.monotonic() + timeout
    cleanup = 'UNKNOWN'
    try:
        for key, stream in (('stdout', proc.stdout), ('stderr', proc.stderr)):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, key)
        while selector.get_map():
            left = deadline - time.monotonic()
            if left <= 0:
                timed_out = True
                break
            for entry, _ in selector.select(min(left, .05)):
                chunk = os.read(entry.fd, 65536)
                if not chunk:
                    selector.unregister(entry.fileobj)
                    continue
                target = capture[entry.data]
                if len(target) + len(chunk) > limit:
                    target.extend(chunk[:max(0, limit-len(target))])
                    overflow = True
                    break
                target.extend(chunk)
            if overflow:
                break
        if not (timed_out or overflow):
            try:
                proc.wait(timeout=max(.001, deadline-time.monotonic()))
            except subprocess.TimeoutExpired:
                timed_out = True
    finally:
        cleanup = close_owned(proc)
        selector.close()
        proc.stdout.close()
        proc.stderr.close()
    return dict(returncode=proc.returncode, timed_out=timed_out, overflow=overflow,
                cleanup=cleanup, **{k: bytes(v) for k, v in capture.items()})


def checked(argv, *, timeout=10, limit=65536):
    result = run_bounded(argv, timeout=timeout, limit=limit)
    need(result['returncode'] == 0 and result['cleanup'] == 'CLOSED' and
         not result['timed_out'] and not result['overflow'], 'HOST_COMMAND_REFUSED')
    return result['stdout']


def protected_chain(invocation):
    """Observe protected invocation and resolved ancestry without changing it."""
    need(os.geteuid() != 0, 'BWRAP_NONROOT_REQUIRED')
    path = Path(invocation)
    need(path.is_absolute() and '..' not in path.parts, 'BWRAP_SYSTEM_PATH')
    resolved = path.resolve(strict=True)
    need(str(resolved).startswith(('/usr/', '/lib/', '/lib64/', '/bin/', '/etc/')),
         'BWRAP_SYSTEM_PATH')
    records = {}
    for leaf in (path, resolved):
        for node in (leaf, *leaf.parents):
            st = node.lstat()
            link = os.readlink(node) if stat.S_ISLNK(st.st_mode) else None
            need(st.st_uid == 0 and st.st_uid != os.geteuid(), 'BWRAP_PATH_OWNER')
            if link is None:
                need(not st.st_mode & 0o022 and not os.access(node, os.W_OK, effective_ids=True),
                     'BWRAP_PATH_MUTABLE')
            records[str(node)] = {'identity': identity(st), 'link': link}
    return path, resolved, records


def recheck_chain(records):
    for name, record in records.items():
        node = Path(name)
        need(identity(node.lstat()) == record['identity'] and
             (os.readlink(node) if node.is_symlink() else None) == record['link'],
             'BWRAP_ANCESTOR_RACE')


def protected_directory(invocation):
    path, resolved, records = protected_chain(invocation)
    need(stat.S_ISDIR(resolved.lstat().st_mode), 'BWRAP_SEARCH_DIRECTORY_SHAPE')
    recheck_chain(records)
    return {'invocation': str(path), 'resolved': str(resolved), 'path_chain': records}


def protected_file(invocation, *, executable=False, limit=134217728):
    """Require root-owned, unmodifiable system file and protected ancestry.

    This accepts a conservative subset of upstream's policy-dependent selector.
    No readonly-policy carveout makes a mutable invocation path appear trusted.
    """
    path, resolved, records = protected_chain(invocation)
    before = resolved.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 < before.st_size <= limit,
         'BWRAP_FILE_SHAPE')
    need(not executable or (bool(before.st_mode & 0o111) and os.access(path, os.X_OK, effective_ids=True)),
         'BWRAP_NOT_EXECUTABLE')
    digest, size = hashlib.sha256(), 0
    fd = os.open(resolved, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        need(identity(before) == identity(os.fstat(fd)), 'BWRAP_FILE_RACE')
        while chunk := os.read(fd, 1048576):
            size += len(chunk)
            need(size <= limit, 'BWRAP_FILE_BOUND')
            digest.update(chunk)
        need(identity(before) == identity(os.fstat(fd)) == identity(resolved.lstat()) and size == before.st_size,
             'BWRAP_FILE_RACE')
    finally:
        os.close(fd)
    recheck_chain(records)
    return {'invocation': str(path), 'resolved': str(resolved), 'sha256': digest.hexdigest(),
            'bytes': size, 'path_chain': records}


def parse_ldd(raw):
    need(len(raw) <= 65536, 'BWRAP_DEPENDENCY_BOUND')
    paths = []
    for line in raw.decode('ascii', 'strict').splitlines():
        line = line.strip()
        if not line:
            continue
        if re.fullmatch(r'linux-vdso\.so\.\d+ \(0x[0-9a-fA-F]+\)', line):
            continue
        match = re.fullmatch(r'(?:[A-Za-z0-9_.+-]+ => )?(/[^\s]+) \(0x[0-9a-fA-F]+\)', line)
        need(match is not None, 'BWRAP_DEPENDENCY_UNRESOLVED')
        paths.append(match.group(1))
    need(0 < len(paths) <= 32 and len(paths) == len(set(paths)), 'BWRAP_DEPENDENCY_POPULATION')
    return sorted(paths)


def parse_package(owner, status):
    need(owner in (b'bubblewrap: /usr/bin/bwrap\n', b'bubblewrap:amd64: /usr/bin/bwrap\n'), 'BWRAP_PACKAGE_OWNER')
    match = re.fullmatch(rb'ii \t(bubblewrap(?::amd64)?)\t([A-Za-z0-9.+:~\-]+)\tamd64\n', status)
    need(match is not None, 'BWRAP_PACKAGE_NOT_INSTALLED')
    return {'package': 'bubblewrap', 'architecture': 'amd64', 'version': match.group(2).decode(),
            'package_owner_sha256': sha(owner), 'package_status_sha256': sha(status)}


def os_release():
    binding = protected_file('/etc/os-release', limit=65536)
    raw = Path(binding['resolved']).read_bytes()
    need(sha(raw) == binding['sha256'], 'BWRAP_OS_CHANGED')
    fields = dict(re.findall(rb'^([A-Z_]+)="?([^"\n]+)"?$', raw, re.M))
    need(fields.get(b'ID') == b'ubuntu' and fields.get(b'VERSION_ID') == b'24.04' and
         platform.machine() == 'x86_64', 'BWRAP_HOST_OS')
    return binding


def inspect_binding():
    """Read/hash system metadata only; no namespace operation or package mutation."""
    search_directories = [protected_directory(p) for p in PATH.split(':')]
    need(not os.path.lexists('/usr/local/bin/bwrap'), 'BWRAP_EARLIER_PATH_ENTRY')
    need(Path('/bin/bwrap').resolve(strict=True) == Path(BWRAP).resolve(strict=True), 'BWRAP_ALIAS_MISMATCH')
    tools = {p: protected_file(p, executable=True) for p in ('/usr/bin/dpkg-query', '/usr/bin/ldd', '/bin/true')}
    binary = protected_file(BWRAP, executable=True)
    package = parse_package(checked(['/usr/bin/dpkg-query', '-S', BWRAP]),
                            checked(['/usr/bin/dpkg-query', '-W', '-f=${db:Status-Abbrev}\t${binary:Package}\t${Version}\t${Architecture}\n', 'bubblewrap']))
    dependencies = [protected_file(p) for p in parse_ldd(checked(['/usr/bin/ldd', BWRAP]))]
    result = {'schema': SCHEMA, 'path': PATH, 'binary': binary, 'os_release': os_release(),
              'package': package, 'tools': tools, 'dependencies': dependencies, 'euid': os.geteuid(),
              'search_directories': search_directories}
    # Recheck every participant and its protected ancestry after all commands.
    for binding in [binary, result['os_release'], *tools.values(), *dependencies]:
        same_binding(binding, protected_file(binding['invocation'], executable=binding in tools.values() or binding == binary))
    for binding in search_directories:
        same_binding(binding, protected_directory(binding['invocation']))
    need(not os.path.lexists('/usr/local/bin/bwrap'), 'BWRAP_EARLIER_PATH_ENTRY')
    return result


def same_binding(expected, observed):
    need(encoded(expected) == encoded(observed), 'BWRAP_BINDING_CHANGED')


def accept_probe(result):
    need(result['returncode'] == 0 and not result['timed_out'] and not result['overflow'] and
         result['cleanup'] == 'CLOSED', 'BWRAP_NAMESPACE_NOT_AFFIRMATIVE')
    return {'schema': 'dg18.c02.bwrap-namespace-probe.v1', 'status': 'AFFIRMATIVE_SUCCESS',
            'argv': PROBE_ARGV, 'exit_code': 0, 'cleanup': 'CLOSED',
            'stdout_bytes': len(result['stdout']), 'stderr_bytes': len(result['stderr']),
            'stdout_sha256': sha(result['stdout']), 'stderr_sha256': sha(result['stderr']),
            'timed_out': False, 'overflow': False, 'deadline_ms': 500}


def namespace_probe(expected):
    same_binding(expected, inspect_binding())
    result = run_bounded(PROBE_ARGV, timeout=.5, limit=65536)
    accepted = accept_probe(result)
    same_binding(expected, inspect_binding())
    return accepted


def prepare():
    binding = inspect_binding()
    probe = namespace_probe(binding)
    return {'binding': binding, 'binding_sha256': sha(encoded(binding)), 'probe': probe,
            'authority': 'PREREQUISITE_ONLY_NO_NATIVE_GRANT'}


def recheck(prepared, *, affirmative=False):
    need(prepared['binding_sha256'] == sha(encoded(prepared['binding'])), 'BWRAP_BINDING_DIGEST')
    need(prepared['probe']['status'] == 'AFFIRMATIVE_SUCCESS' and prepared['probe']['exit_code'] == 0,
         'BWRAP_PREPARATION_NOT_AFFIRMATIVE')
    same_binding(prepared['binding'], inspect_binding())
    if affirmative:
        return namespace_probe(prepared['binding'])
    return None
