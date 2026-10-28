#!/usr/bin/python3.12
"""Observe one fixed C5 namespace/proc setup prerequisite.

This is a repo-only ordinary setup observation, with no original C5 or native
admission. The namespace/proc prefix belongs to work-graph-c5-executor.py;
the launcher pin is the public genuine-execution-profile fixture and the
120-byte filter is VerifierTaskSession.SECCOMP. No provider/source image,
private archive, historical identity or executable target is introduced.
"""
import base64
import fcntl
import hashlib
import json
import os
import resource
import selectors
import signal
import stat
import subprocess
import time

TARGET = '/__c5_proc_setup_intentionally_absent_target__'
PIN = {'bytes': 72160, 'sha256': '52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712'}
FILTER = base64.b64decode('IAAAAAQAAAAVAAEAPgAAwAYAAAAAAACAIAAAAAAAAAA1AAkAAAAAQBUABwAQAQAAFQAGADQBAAAVAAYAswEAABUAAQA4AAAABgAAAAAA/38gAAAAEAAAAEUAAQAAAAAQBgAAAAAA/38GAAAAAQAFAAYAAAAmAAUA')
FILTER_SHA = 'df124088b9f6eabc9d06654bae67a6b8a09706936ccab78d358d0165a98fe4da'
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC'}
TEMPLATE = ['--unshare-all', '--unshare-user', '--die-with-parent', '--new-session', '--clearenv', '--cap-drop', 'ALL', '--perms', '0755', '--dir', '/proc', '--perms', '0755', '--dir', '/dev', '--proc', '/proc', '--remount-ro', '/proc', '--symlink', '/proc/self/fd', '/dev/fd', '--dev-bind', '/dev/null', '/dev/null', '--remount-ro', '/', '--chdir', '/', '--seccomp', 'OWNED_SEALED_SECCOMP_FD']
OWNED_CHILD = None
OWNED_PIDFD = None


HOSTED_PACKAGE_URL = 'https://snapshot.ubuntu.com/ubuntu/20260901T000000Z/pool/main/b/bubblewrap/bubblewrap_0.9.0-1ubuntu0.1_amd64.deb'
HOSTED_PACKAGE_PIN = {'bytes': 50178, 'sha256': '1b506492bd9c7fd0cdb4f02ac822f1d3e336b0aead5113c1239baf8db5db562a'}


def hosted_download():
    import urllib.request

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *_args, **_kwargs):
            raise ValueError('hosted launcher package redirect refused')

    request = urllib.request.Request(HOSTED_PACKAGE_URL, headers={'User-Agent': 'implementaudit-c5-setup/1'})
    with urllib.request.build_opener(NoRedirect).open(request, timeout=10) as response:
        if response.status != 200 or response.geturl() != HOSTED_PACKAGE_URL:
            raise ValueError('hosted launcher package origin changed')
        size = response.headers.get('Content-Length')
        if size is not None and size != str(HOSTED_PACKAGE_PIN['bytes']):
            raise ValueError('hosted launcher package length changed')
        return response.read(HOSTED_PACKAGE_PIN['bytes'] + 1)


def hosted_archive_data(raw):
    if len(raw) > HOSTED_PACKAGE_PIN['bytes'] or raw[:8] != b'!<arch>\n':
        raise ValueError('hosted launcher archive header differs')
    offset, members = 8, []
    while offset < len(raw):
        header = raw[offset:offset + 60]
        if len(header) != 60 or header[58:] != b'`\n' or len(members) >= 3:
            raise ValueError('hosted launcher archive member differs')
        try:
            name = header[:16].decode('ascii').strip().rstrip('/')
            size = int(header[48:58])
        except (UnicodeError, ValueError) as error:
            raise ValueError('hosted launcher archive metadata differs') from error
        offset += 60
        if size < 0 or size > len(raw) - offset:
            raise ValueError('hosted launcher archive member is truncated')
        members.append((name, raw[offset:offset + size]))
        offset += size + size % 2
    if (offset != len(raw) or [name for name, _ in members] !=
            ['debian-binary', 'control.tar.zst', 'data.tar.zst'] or members[0][1] != b'2.0\n'):
        raise ValueError('hosted launcher archive selection differs')
    return members[2][1]


def hosted_tar_launcher(raw):
    import io
    import tarfile
    if len(raw) > 1048576:
        raise ValueError('hosted launcher tar exceeds its bound')
    try:
        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:') as archive:
            members = archive.getmembers()
            selected = [member for member in members if member.name == './usr/bin/bwrap']
            if len(members) > 64 or len(selected) != 1:
                raise ValueError('hosted launcher tar selection differs')
            member = selected[0]
            if (not member.isreg() or member.mode != 0o755 or member.uid != 0 or member.gid != 0
                    or member.size != PIN['bytes'] or member.linkname):
                raise ValueError('hosted launcher tar member metadata differs')
            stream = archive.extractfile(member)
            with stream:
                launcher = stream.read(PIN['bytes'] + 1)
    except (tarfile.TarError, OSError) as error:
        raise ValueError('hosted launcher tar is invalid') from error
    if len(launcher) != PIN['bytes'] or hashlib.sha256(launcher).hexdigest() != PIN['sha256']:
        raise ValueError('hosted launcher pin differs')
    return launcher


def decode_hosted_launcher(raw):
    # Linux provider preparation only; this supplies no native governance event.
    if len(raw) != HOSTED_PACKAGE_PIN['bytes'] or hashlib.sha256(raw).hexdigest() != HOSTED_PACKAGE_PIN['sha256']:
        raise ValueError('hosted launcher package pin differs')
    compressed = hosted_archive_data(raw)
    import ctypes
    library = ctypes.CDLL('/lib/x86_64-linux-gnu/libzstd.so.1')
    library.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
    library.ZSTD_decompress.restype = ctypes.c_size_t
    library.ZSTD_isError.argtypes = [ctypes.c_size_t]
    library.ZSTD_isError.restype = ctypes.c_uint
    output = ctypes.create_string_buffer(1048576)
    size = library.ZSTD_decompress(output, len(output), compressed, len(compressed))
    if library.ZSTD_isError(size) or not 0 < size <= len(output):
        raise ValueError('hosted launcher zstd data is invalid or exceeds its bound')
    return hosted_tar_launcher(output.raw[:size])


def hosted_parent():
    opened = []
    try:
        for name, path in [('/', '/'), ('usr', '/usr'), ('bin', '/usr/bin')]:
            fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                         dir_fd=opened[-1][0] if opened else None)
            opened.append((fd, path))
            observed = os.fstat(fd)
            if (not stat.S_ISDIR(observed.st_mode) or observed.st_uid != 0 or observed.st_gid != 0
                    or observed.st_mode & 0o022 or identity(observed) != identity(os.lstat(path))):
                raise ValueError('hosted launcher parent metadata differs')
        try:
            os.stat('bwrap', dir_fd=opened[-1][0], follow_symlinks=False)
        except FileNotFoundError:
            return opened
        raise FileExistsError('hosted launcher target already exists')
    except BaseException:
        for fd, _ in reversed(opened):
            os.close(fd)
        raise


def write_hosted_launcher(parent, raw):
    if len(raw) != PIN['bytes'] or hashlib.sha256(raw).hexdigest() != PIN['sha256']:
        raise ValueError('hosted launcher pin differs')
    directory = os.fstat(parent)
    if (not stat.S_ISDIR(directory.st_mode) or directory.st_uid != os.geteuid()
            or directory.st_gid != os.getegid() or directory.st_mode & 0o022):
        raise ValueError('hosted launcher parent metadata differs')
    fd = os.open('bwrap', os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                 0o755, dir_fd=parent)
    try:
        os.fchmod(fd, 0o755)
        offset = 0
        while offset < len(raw):
            count = os.write(fd, raw[offset:])
            if count <= 0:
                raise ValueError('hosted launcher write stalled; exclusive target retained')
            offset += count
        os.fsync(fd)
        before = identity(os.fstat(fd))
        received = os.pread(fd, PIN['bytes'] + 1, 0)
        after = identity(os.fstat(fd))
        if (before != after or after != identity(os.stat('bwrap', dir_fd=parent, follow_symlinks=False))
                or not stat.S_ISREG(after[2]) or stat.S_IMODE(after[2]) != 0o755 or after[3] != 1
                or after[4] != PIN['bytes'] or after[7:] != [os.geteuid(), os.getegid()] or received != raw):
            raise ValueError('hosted launcher exclusive write/readback differs; target retained')
        return dict(PIN, opening=before, closing=after, mode='0755', exclusive_creation=True)
    finally:
        os.close(fd)


def provision_hosted_launcher():
    if os.geteuid() != 0 or os.getegid() != 0:
        raise ValueError('hosted launcher provision requires explicit root invocation')
    for which, value in [(resource.RLIMIT_AS, 134217728), (resource.RLIMIT_CPU, 5),
                         (resource.RLIMIT_FSIZE, 131072), (resource.RLIMIT_NOFILE, 32)]:
        resource.setrlimit(which, (value, value))
    opened = hosted_parent()
    def deadline(_signal, _frame):
        raise TimeoutError('hosted launcher provision exceeded20seconds; any exclusive target is retained')
    previous = signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 20)
    try:
        launcher = decode_hosted_launcher(hosted_download())
        result = write_hosted_launcher(opened[-1][0], launcher)
        for fd, path in opened:
            current = os.fstat(fd)
            if (identity(current) != identity(os.lstat(path)) or current.st_uid != 0
                    or current.st_gid != 0 or current.st_mode & 0o022):
                raise ValueError('hosted launcher parent changed; exclusive target retained')
        print(json.dumps({'scope': 'LINUX_LAUNCHER_PROVISION_ONLY_NO_C5_OR_NATIVE_ACCEPTANCE',
                          'package': dict(HOSTED_PACKAGE_PIN, url=HOSTED_PACKAGE_URL),
                          'target': '/usr/bin/bwrap', 'launcher': result}, sort_keys=True, separators=(',', ':')))
        return 0
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
        for fd, _ in reversed(opened):
            os.close(fd)


def identity(s):
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
            s.st_mtime_ns, s.st_ctime_ns, s.st_uid, s.st_gid]


def fds():
    result = {}
    for name in os.listdir('/proc/self/fd'):
        try:
            result[name] = identity(os.fstat(int(name)))[:4]
        except OSError:
            pass
    return result


def host():
    selected = {'Uid', 'Gid', 'NSpid', 'NStgid', 'CapInh', 'CapPrm', 'CapEff',
                'CapBnd', 'CapAmb', 'NoNewPrivs', 'Seccomp', 'Seccomp_filters'}
    with open('/proc/self/status') as source:
        status = {k: v.strip() for line in source for k, v in [line.split(':', 1)] if k in selected}
    return {'pid': os.getpid(), 'ppid': os.getppid(), 'sid': os.getsid(0),
            'pgid': os.getpgrp(), 'status': status,
            'namespaces': {n: os.readlink('/proc/self/ns/' + n) for n in ['user', 'mnt', 'pid', 'net']}}


def seal(raw, name):
    fd = os.memfd_create(name, os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    done = 0
    while done < len(raw):
        written = os.write(fd, raw[done:])
        if written <= 0:
            raise RuntimeError('memfd short write')
        done += written
    os.lseek(fd, 0, os.SEEK_SET)
    fcntl.fcntl(fd, fcntl.F_ADD_SEALS, 15)
    assert fcntl.fcntl(fd, fcntl.F_GET_SEALS) == 15
    assert os.lseek(fd, 0, os.SEEK_CUR) == 0
    return fd


def main():
    global OWNED_CHILD, OWNED_PIDFD
    assert len(FILTER) == 120 and hashlib.sha256(FILTER).hexdigest() == FILTER_SHA
    assert signal.getsignal(signal.SIGCHLD) == signal.SIG_DFL
    baseline = fds()
    opening = host()
    for which, value in [(resource.RLIMIT_AS, 134217728), (resource.RLIMIT_CPU, 5),
                         (resource.RLIMIT_FSIZE, 65536), (resource.RLIMIT_NOFILE, 32)]:
        resource.setrlimit(which, (value, value))
    launcher = os.open('/usr/bin/bwrap', os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    before = identity(os.fstat(launcher))
    assert stat.S_ISREG(before[2]) and before[3] == 1 and before[4] == PIN['bytes']
    assert hashlib.sha256(os.pread(launcher, PIN['bytes'] + 1, 0)).hexdigest() == PIN['sha256']
    assert identity(os.lstat('/usr/bin/bwrap')) == before
    secfd = seal(FILTER, 'c5-ordinary-capability-seccomp')
    arguments = [str(secfd) if s == 'OWNED_SEALED_SECCOMP_FD' else s for s in TEMPLATE]
    argraw = b'\0'.join(s.encode() for s in arguments) + b'\0'
    argfd = seal(argraw, 'c5-ordinary-capability-arguments')
    command = ['/usr/bin/bwrap', '--args', str(argfd), TARGET]
    assert all(os.lseek(fd, 0, os.SEEK_CUR) == 0 for fd in (argfd, secfd))
    began = time.monotonic()
    process = subprocess.Popen(command, cwd='/', env=ENV, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               close_fds=True, pass_fds=(argfd, secfd), start_new_session=True)
    OWNED_CHILD = process
    pidfd = os.pidfd_open(process.pid)
    OWNED_PIDFD = pidfd
    streams = {'stdout': bytearray(), 'stderr': bytearray()}
    sizes = {'stdout': 0, 'stderr': 0}
    eof = {'stdout': False, 'stderr': False}
    selector = selectors.DefaultSelector()
    for name in streams:
        stream = getattr(process, name)
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ, name)
    waited = None
    killed = False
    timeout = False
    overflow = False
    while True:
        elapsed = time.monotonic() - began
        if waited is None:
            observed = os.wait4(process.pid, os.WNOHANG)
            if observed[0]:
                waited = observed
                process.returncode = os.waitstatus_to_exitcode(observed[1])
                timeout |= elapsed > 5
        if (elapsed > 5 or overflow) and waited is None and not killed:
            timeout = elapsed > 5
            try:
                signal.pidfd_send_signal(pidfd, signal.SIGKILL, None, 0)
            except ProcessLookupError:
                pass
            killed = True
        for key, _ in selector.select(timeout=0.02):
            raw = os.read(key.fileobj.fileno(), 4096)
            name = key.data
            if raw:
                sizes[name] += len(raw)
                streams[name].extend(raw[:max(0, 4096 - len(streams[name]))])
                overflow |= sizes[name] > 4096
            else:
                eof[name] = True
                selector.unregister(key.fileobj)
                key.fileobj.close()
        if waited is not None and not selector.get_map():
            break
        if elapsed > 10:
            break
    for key in list(selector.get_map().values()):
        selector.unregister(key.fileobj)
        key.fileobj.close()
    selector.close()
    if waited is None:
        observed = os.wait4(process.pid, os.WNOHANG)
        if observed[0]:
            waited = observed
            process.returncode = os.waitstatus_to_exitcode(observed[1])
    if waited is None:
        raise RuntimeError('ordinary setup child did not reap within cleanup bound')
    try:
        os.killpg(process.pid, 0)
        group_absent = False
    except ProcessLookupError:
        group_absent = True
    after = identity(os.fstat(launcher))
    pin_current = (after == before == identity(os.lstat('/usr/bin/bwrap')) and
                   hashlib.sha256(os.pread(launcher, PIN['bytes'] + 1, 0)).hexdigest() == PIN['sha256'])
    for fd in (argfd, secfd, pidfd, launcher):
        os.close(fd)
    closing = host()
    descriptor_restoration = fds() == baseline
    complete = bool(waited is not None and all(eof.values()) and not timeout and not overflow and
                    group_absent and pin_current and descriptor_restoration and opening == closing)
    stderr = bytes(streams['stderr'])
    expected = ('bwrap: execvp ' + TARGET + ': No such file or directory\n').encode()
    if complete and process.returncode == 1 and not streams['stdout'] and stderr == expected:
        classification = 'SETUP_REACHED_ABSENT_TARGET'
    elif complete and process.returncode == 1 and stderr == b"bwrap: Can't mount proc on /newroot/proc: Operation not permitted\n":
        classification = 'PROC_MOUNT_EPERM'
    else:
        classification = 'OTHER_REFUSAL_OR_INCOMPLETE'
    result = {'schema': 'dg16.ordinary-setup-capability.v1', 'authority': 'NONE',
              'original19_started': False, 'provider_acquired': False, 'native_admission': False,
              'argv': command, 'arguments': arguments, 'environment': ENV, 'cwd': '/',
              'launcher': dict(PIN, opening=before, closing=after, current=pin_current),
              'seccomp_sha256': FILTER_SHA, 'argument_sha256': hashlib.sha256(argraw).hexdigest(),
              'parent_opening': opening, 'parent_closing': closing,
              'classification': classification, 'complete_custody': complete,
              'exit_code': process.returncode, 'elapsed_seconds': time.monotonic() - began,
              'wait4_reaped': waited is not None, 'raw_wait_status': waited[1] if waited else None,
              'rusage': {'maxrss_kib': waited[2].ru_maxrss, 'user_seconds': waited[2].ru_utime,
                         'system_seconds': waited[2].ru_stime} if waited else None,
              'owned_group_absent': group_absent, 'descriptor_restoration': descriptor_restoration,
              'timed_out': timeout, 'overflow': overflow, 'pidfd_kill': killed, 'eof': eof,
              'stream_bytes': sizes, 'stdout': bytes(streams['stdout']).decode('utf-8', 'replace'),
              'stderr': stderr.decode('utf-8', 'replace')}
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))
    return 0 if complete else 2


def emergency_cleanup():
    # Only this process owns wait custody; no numerical PID can be recycled
    # until its unreaped direct child has been waited. Never signal after reap.
    child = OWNED_CHILD
    if child is None or child.returncode is not None:
        return
    try:
        if OWNED_PIDFD is not None:
            signal.pidfd_send_signal(OWNED_PIDFD, signal.SIGKILL, None, 0)
        else:
            os.kill(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        observed = os.wait4(child.pid, os.WNOHANG)
        if observed[0]:
            child.returncode = os.waitstatus_to_exitcode(observed[1])
            return
        time.sleep(0.01)
    raise RuntimeError('ordinary setup child cleanup remains unproved')


if __name__ == '__main__':
    import sys
    try:
        if sys.argv[1:] == ['--provision-hosted-launcher']:
            raise SystemExit(provision_hosted_launcher())
        if sys.argv[1:]:
            raise ValueError('unsupported setup observer arguments')
        raise SystemExit(main())
    finally:
        emergency_cleanup()
