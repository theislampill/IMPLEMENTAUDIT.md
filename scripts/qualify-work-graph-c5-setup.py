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
HOSTED_SOURCE_URL = 'https://github.com/theislampill/IMPLEMENTAUDIT.md.git'
HOSTED_LOADER_PIN = {'bytes': 11983, 'sha256': '033018ae7f13c94cb85f2a7922b04644e989684b0eee2d1bde19586b02997204'}


class HostedPrerequisiteDeadline(BaseException):
    """End the whole operation; ordinary input refusals must not consume this."""


def hosted_current_owner(root):
    """Load only the existing current C5 owner from its held, hash-bound buffer."""
    from pathlib import Path
    import types
    path = Path(root) / 'scripts/load-work-graph-c5-executor.py'
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        opening = identity(os.fstat(fd))
        if not stat.S_ISREG(opening[2]) or opening[3] != 1 or opening[4] != HOSTED_LOADER_PIN['bytes']:
            raise ValueError('hosted current loader pin differs')
        raw = os.pread(fd, HOSTED_LOADER_PIN['bytes'] + 1, 0)
        if hashlib.sha256(raw).hexdigest() != HOSTED_LOADER_PIN['sha256']:
            raise ValueError('hosted current loader pin differs')
        module = types.ModuleType('c5_hosted_current_source_loader')
        module.__file__ = str(path)
        exec(compile(raw, str(path), 'exec'), module.__dict__)
        current = module._Engine(module.CURRENT_PROFILE).load()
        if (identity(os.fstat(fd)) != opening or identity(os.lstat(path)) != opening
                or os.pread(fd, len(raw) + 1, 0) != raw):
            raise ValueError('hosted current loader changed during loading')
        return current
    finally:
        os.close(fd)


def hosted_pin_receiving(base, name, pin, objects):
    """Report an existing selection; this observer never changes its pin."""
    try:
        observed = base.capture_selector(name, objects)
        match = observed['kind'] == 'FILE' and all(observed.get(key) == value for key, value in pin.items())
        return dict(path=name, expected=dict(pin), observed=observed, match=match)
    except (OSError, ValueError) as exc:
        return dict(path=name, expected=dict(pin), observed=None, match=False, reason=str(exc)[:512])


def hosted_nss_receiving(provider, observed, objects, process_identity):
    try:
        if process_identity != dict(uid=0, euid=0, gid=0, egid=0):
            raise ValueError('C5 provider selected NSS profile requires actual observer UID/GID zero')
        provider._validate_nss(observed, objects)
        return dict(match=True, identity=process_identity)
    except (OSError, ValueError, KeyError) as exc:
        return dict(match=False, identity=process_identity, reason=str(exc)[:512])


def hosted_git(arguments, cwd, records, *, wall_seconds=60, stream_limit=4194304):
    """Bound ordinary Git command custody; never inherit Actions configuration."""
    environment = dict(ENV, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null',
                       GIT_TERMINAL_PROMPT='0', GIT_ASKPASS='/bin/false')
    command = ['/usr/bin/git', '-c', 'credential.helper=', '-c', 'core.askPass=/bin/false',
               '-c', 'core.hooksPath=/dev/null', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false'] + list(arguments)
    baseline = fds()
    began = time.monotonic()
    streams = {'stdout': bytearray(), 'stderr': bytearray()}
    sizes = dict(stdout=0, stderr=0)
    eof = dict(stdout=False, stderr=False)
    overflow = timed_out = waited = group_absent = False
    process = selector = None
    failure = None
    cleanup_errors = []
    record = dict(arguments=list(arguments), environment=environment, pid=None,
        process_handle_returned=False, process_creation_outcome='UNOBSERVED_NO_HANDLE_RETURNED',
        command_received=False, exception=None, wait_reaped=False, owned_group_absent=False,
        descriptor_restoration=False)
    records.append(record)
    try:
        process = subprocess.Popen(command, cwd=cwd, env=environment, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True,
                                   start_new_session=True)
        record.update(pid=process.pid, process_handle_returned=True, process_creation_outcome='HANDLE_RETURNED')
        selector = selectors.DefaultSelector()
        for name in streams:
            stream = getattr(process, name)
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while selector.get_map():
            timed_out = time.monotonic() - began > wall_seconds
            if timed_out or overflow:
                failure = 'hosted Git wall bound' if timed_out else 'hosted Git output bound'
                break
            for key, _ in selector.select(timeout=min(0.05, wall_seconds)):
                raw = os.read(key.fileobj.fileno(), 16384)
                if not raw:
                    eof[key.data] = True
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                sizes[key.data] += len(raw)
                streams[key.data].extend(raw[:max(0, stream_limit - len(streams[key.data]))])
                overflow |= sizes[key.data] > stream_limit
        if failure is None:
            try:
                process.wait(timeout=max(0.001, wall_seconds - (time.monotonic() - began)))
                waited = True
            except subprocess.TimeoutExpired:
                timed_out = True
                failure = 'hosted Git wall bound'
    except BaseException as exc:
        record['exception'] = dict(type=type(exc).__name__, reason=str(exc)[:512])
        raise
    finally:
        # No wait/poll occurs before the timeout kill: the unreaped direct child
        # still owns this new session's numerical group identity.
        if process is not None and process.returncode is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except OSError as exc:
                cleanup_errors.append(dict(operation='kill_owned_group', reason=str(exc)[:512]))
            try:
                process.wait(timeout=5)
                waited = True
            except subprocess.TimeoutExpired:
                failure = 'hosted Git child not reaped within cleanup bound'
            except OSError as exc:
                cleanup_errors.append(dict(operation='wait_owned_child', reason=str(exc)[:512]))
        if process is not None:
            # Close both pipes even when selector creation/registration never completed.
            for name in streams:
                try:
                    getattr(process, name).close()
                except OSError as exc:
                    cleanup_errors.append(dict(operation='close_' + name, reason=str(exc)[:512]))
        if selector is not None:
            try:
                selector.close()
            except OSError as exc:
                cleanup_errors.append(dict(operation='close_selector', reason=str(exc)[:512]))
        if process is not None:
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                group_absent = True
            except OSError as exc:
                cleanup_errors.append(dict(operation='observe_group_absence', reason=str(exc)[:512]))
        restored = fds() == baseline
        record.update(returncode=process.returncode if process is not None else None,
            elapsed_seconds=time.monotonic() - began, cleanup_errors=cleanup_errors,
            wait_reaped=waited, owned_group_absent=group_absent, descriptor_restoration=restored,
            eof=eof, output_overflow=overflow, timed_out=timed_out, stream_bytes=sizes,
            stream_sha256={name: hashlib.sha256(raw).hexdigest() for name, raw in streams.items()},
            stderr_excerpt=bytes(streams['stderr'][:1024]).decode('utf-8', 'replace'),
            hashes_cover='captured prefix only' if overflow else 'captured bytes')
        record['command_received'] = (not failure and not cleanup_errors and record['exception'] is None
            and waited and group_absent and restored and process is not None and process.returncode == 0)
    if not record['command_received']:
        raise ValueError(failure or 'hosted Git refused or ordinary command custody incomplete')
    return bytes(streams['stdout'])


def prepare_hosted_source(executing_root, output, expected_commit, *, records=None):
    """Prepare genuine standalone public Git storage, never copy Actions .git."""
    from pathlib import Path
    import re
    executing_root, output = Path(executing_root).resolve(), Path(output).absolute()
    actual_output = output.resolve()
    if (actual_output == executing_root or executing_root in actual_output.parents
            or actual_output in executing_root.parents or actual_output != output):
        raise ValueError('hosted source/output alias or overlap')
    if not re.fullmatch('[0-9a-f]{40}', expected_commit):
        raise ValueError('hosted expected source commit must be an exact object identity')
    before = os.lstat(output)
    if (not stat.S_ISDIR(before.st_mode) or stat.S_IMODE(before.st_mode) != 0o700
            or before.st_uid != os.geteuid() or before.st_gid != os.getegid() or any(output.iterdir())):
        raise ValueError('hosted source output must be a fresh owned empty directory')
    source = output / 'source'
    if records is None:
        records = []
    hosted_git(['clone', '--no-local', '--no-hardlinks', '--no-checkout',
                '--', HOSTED_SOURCE_URL, str(source)], output, records)
    branch = hosted_git(['-C', str(source), 'symbolic-ref', '--short', 'HEAD'], output, records).decode('ascii', 'strict').strip()
    if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._/-]{0,127}', branch):
        raise ValueError('hosted fresh clone tracking branch is unsupported')
    tracking = hosted_git(['-C', str(source), 'config', '--local', '--get-regexp', '^branch\\.'],
                          output, records).decode('utf-8', 'strict').splitlines()
    expected_tracking = ['branch.' + branch + '.remote origin', 'branch.' + branch + '.merge refs/heads/' + branch]
    if len(tracking) != 2 or set(tracking) != set(expected_tracking):
        raise ValueError('hosted actual fresh clone tracking section differs; no removal')
    # Established fresh-clone preparation: only the observed new tracking
    # section is removed. Source objects and the original checkout are untouched.
    hosted_git(['-C', str(source), 'config', '--local', '--remove-section', 'branch.' + branch], output, records)
    hosted_git(['-C', str(source), 'fetch', '--no-tags', '--no-recurse-submodules',
                'origin', expected_commit], output, records)
    hosted_git(['-C', str(source), 'checkout', '--detach', expected_commit], output, records)
    observed = hosted_git(['-C', str(source), 'show', '-s', '--format=%H%n%T%n%P', 'HEAD'],
                          output, records).decode('ascii', 'strict').splitlines()
    if (len(observed) != 3 or observed[0] != expected_commit or not re.fullmatch('[0-9a-f]{40}', observed[1])
            or any(not re.fullmatch('[0-9a-f]{40}', value) for value in observed[2].split())):
        raise ValueError('hosted fresh source identity differs')
    shallow = hosted_git(['-C', str(source), 'rev-parse', '--is-shallow-repository'], output, records)
    clean = hosted_git(['-C', str(source), 'status', '--porcelain=v1', '--untracked-files=all', '--ignored'], output, records)
    if shallow != b'false\n' or clean:
        raise ValueError('hosted fresh source is shallow or not clean')
    hosted_git(['-C', str(source), 'fsck', '--strict', '--full'], output, records)
    objects = hosted_git(['-C', str(source), 'rev-list', '--objects', '--all', '--missing=print'], output, records)
    if any(line.startswith(b'?') for line in objects.splitlines()):
        raise ValueError('hosted fresh source has missing objects')
    return dict(path=str(source), expected_commit=expected_commit, source_commit=observed[0],
                source_tree=observed[1], ordered_parents=observed[2].split(), clean=True,
                complete_objects=True, object_rows=len(objects.splitlines()),
                object_listing_sha256=hashlib.sha256(objects).hexdigest(), commands=records,
                repository=HOSTED_SOURCE_URL, credential_source='NONE')


def receive_hosted_inputs(current):
    """Receive selected data; only the unchanged owner decides full startup."""
    base, provider = current.B, current.D
    objects = {}
    current.CHECK()
    process_identity = dict(uid=os.getuid(), euid=os.geteuid(), gid=os.getgid(), egid=os.getegid())
    pins = [hosted_pin_receiving(base, name, pin, objects)
            for selection in (provider.SPEC['startup_pins'], provider.SPEC['native_pins'])
            for name, pin in selection.items()]
    system_pin = base.SPEC['runtime_pins'][base.SPEC['python_target']]
    aliases = []
    for name in base._PYTHON_ALIASES:
        pin = dict(resolved=base.SPEC['python_target'], sha256=system_pin['sha256'], mode=0o755)
        received = hosted_pin_receiving(base, name, pin, objects)
        if received['observed'] is not None and received['observed']['kind'] == 'MISSING':
            received.update(match=True, disposition='MISSING_ALLOWED_BY_EXISTING_OWNER')
        aliases.append(received)
    nss = dict(files={name: base.capture_selector(name, objects, limit=65536)
                      for name in ('/etc/passwd', '/etc/nsswitch.conf')},
               nscd={name: base.capture_selector(name, objects) for name in base._NSCD})
    nss_result = hosted_nss_receiving(provider, nss, objects, process_identity)
    absent = {name: base.capture_selector(name, objects) for name in provider._ABSENT}
    full_startup = dict(match=False)
    try:
        startup = provider._startup(objects)
        full_startup = dict(match=True, identity=startup['identity'], provider_execution=False)
    except (OSError, ValueError) as exc:
        full_startup['reason'] = str(exc)[:512]
    if len(objects) > current.P.RUNTIME_BOUNDS['entries'] or sum(map(len, objects.values())) > current.P.RUNTIME_BOUNDS['unique_bytes']:
        raise ValueError('hosted selected input object bound exceeded')
    bookends = True
    for received in pins + aliases:
        if received['observed'] is not None:
            bookends &= base.capture_selector(received['path'], {}) == received['observed']
    for name, opening in dict(nss['files'], **nss['nscd'], **absent).items():
        bookends &= base.capture_selector(name, {}) == opening
    current.CHECK()
    return dict(profile=provider.PROFILE, pins=pins, system_aliases=aliases,
                identity=process_identity, nss=dict(observation=nss, result=nss_result), absent=absent,
                selected_bookends_equal=bookends, unchanged_owner_full_startup=full_startup,
                provider_acquired=False, provider_imports=0, native_admission=False,
                overall_admission='UNQUALIFIED', object_count=len(objects), object_bytes=sum(map(len, objects.values())))


def receive_hosted_prerequisites(expected_commit):
    from pathlib import Path
    import re
    import tempfile
    if not re.fullmatch('[0-9a-f]{40}', expected_commit):
        raise ValueError('hosted expected source commit must be an exact object identity')
    if (os.getuid(), os.geteuid(), os.getgid(), os.getegid()) != (0, 0, 0, 0):
        raise ValueError('hosted prerequisite receiving requires actual observer UID/GID zero')
    for which, value in [(resource.RLIMIT_AS, 1610612736), (resource.RLIMIT_CPU, 120),
                         (resource.RLIMIT_FSIZE, 268435456), (resource.RLIMIT_NOFILE, 256)]:
        resource.setrlimit(which, (value, value))
    def deadline(signum, frame):
        raise HostedPrerequisiteDeadline('hosted prerequisite receiving wall bound')
    root = Path(__file__).resolve().parents[1]
    baseline = fds()
    result = dict(schema='dg16.hosted-input-prerequisite.v1', authority='NONE', expected_commit=expected_commit,
                  original19_started=False, provider_acquired=False, provider_imports=0,
                  native_admission=False, overall_admission='UNQUALIFIED', deadline_exceeded=False)
    phase = 'current_owner_receiving'
    old_alarm = signal.signal(signal.SIGALRM, deadline)
    try:
        signal.alarm(240)
        current = hosted_current_owner(root)
        result['current_profile'] = current.PROFILE
        result['loader'] = HOSTED_LOADER_PIN
        phase = 'host_input_receiving'
        try:
            result['host_inputs'] = receive_hosted_inputs(current)
        except (OSError, ValueError) as exc:
            result['host_inputs'] = dict(outcome='REFUSED', reason=str(exc)[:512])
        phase = 'source_preparation'
        output = Path(tempfile.mkdtemp(prefix='implementaudit-c5-hosted-inputs-'))
        result['disposable_source_root'] = str(output)
        source_attempt = dict(commands=[], expected_commit=expected_commit)
        result['source_preparation'] = source_attempt
        try:
            source = prepare_hosted_source(root, output, expected_commit, records=source_attempt['commands'])
            result['source_preparation'] = source
            phase = 'source_receiving'
            actual_source = Path(source['path'])
            executing = current.B.capture_selector(root / 'scripts/qualify-work-graph-c5-setup.py', {})
            received = current.B.capture_selector(actual_source / 'scripts/qualify-work-graph-c5-setup.py', {})
            if executing['sha256'] != received['sha256'] or executing['bytes'] != received['bytes']:
                raise ValueError('hosted executing observer does not match the exact fresh source')
            objects = {}
            captured = current.B.complete_source(actual_source, objects)
            current.P.validate_git_namespace(captured['state'], objects)
            contract = current.B._producer_contract(captured['state'])
            source_identity = current.captured_source_identity(captured, objects,
                dict(source_commit=source['source_commit'], source_tree=source['source_tree']))
            current.CHECK()
            result['source_receiving'] = dict(outcome='SOURCE_INPUTS_RECEIVED', identity=source_identity,
                files=len(captured['state']['files']), directories=len(captured['state']['directories']),
                objects=len(objects), object_bytes=sum(map(len, objects.values())), contract=contract,
                state_sha256=hashlib.sha256(json.dumps(captured['state'], sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                observer_sha256=executing['sha256'], runtime_complete=False)
        except (OSError, ValueError) as exc:
            result['source_receiving'] = dict(outcome='REFUSED', reason=str(exc)[:512])
    except HostedPrerequisiteDeadline as exc:
        result['deadline_exceeded'] = True
        result['terminal'] = dict(outcome='DEADLINE_EXCEEDED', phase=phase, reason=str(exc)[:512])
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_alarm)
    result['descriptor_restoration'] = fds() == baseline
    raw = json.dumps(result, sort_keys=True, separators=(',', ':'))
    if len(raw.encode()) > 2097152:
        raise ValueError('hosted prerequisite selected evidence bound exceeded')
    print(raw)
    return 2 if result['deadline_exceeded'] or not result['descriptor_restoration'] else 0


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
        if len(sys.argv) == 3 and sys.argv[1] == '--receive-hosted-prerequisites':
            raise SystemExit(receive_hosted_prerequisites(sys.argv[2]))
        if sys.argv[1:]:
            raise ValueError('unsupported setup observer arguments')
        raise SystemExit(main())
    finally:
        emergency_cleanup()
