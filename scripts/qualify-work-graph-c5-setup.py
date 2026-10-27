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
    try:
        raise SystemExit(main())
    finally:
        emergency_cleanup()
