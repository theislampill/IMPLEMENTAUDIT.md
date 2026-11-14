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
HOSTED_LOADER_PIN = {'bytes': 17279, 'sha256': '4aa8a08b2b54a3cad7c60f58a1de68c5d062205d77adf8deb359867f370fd9d5'}
HOSTED_PUBLIC_STREAMING_LOADER_PIN = {'bytes': 19193, 'sha256': '55684c8ad3e79b9d511e20bd550295e27f55ceade6867c9b70950c0f21f4199c'}
HOSTED_CURRENT105_LOADER_PIN = {'bytes': 20466, 'sha256': 'cc2b2306e05d0845a0dcc809aaa886427009633a7390d7cdb664fbb9884aced9'}
HOSTED_CURRENT105_COMPOSED_LOADER_PIN = {'bytes': 21822, 'sha256': '391fa6ef90ee331e0d7fe1cbf2a460bc8223b2641e4b0e0a865a873ecfc5a0e0'}
HOSTED_R4_COMPOSED_LOADER_PIN = {'bytes': 29572, 'sha256': '37bd1aeef96ee43d6d845a80ae234b602cc840305e8cf08344450730b56baabd'}

HOSTED_R4_BUILD_LOCAL_LOADER_PIN = {'bytes': 33475, 'sha256': '4285ac2ee8fd9353a14cdf5af4552bd0b5e3c7bdc1d7595610f3fa3d2faddb49'}

HOSTED_R4_INITIALIZATION_LOADER_PIN = {'bytes': 36344, 'sha256': 'e6f0b41c728006241bc1c6ebb85d0a09b73943e8b413c8699bba99fa9f3d03e1'}

HOSTED_R5_WINDOWS_INITIALIZATION_LOADER_PIN = {'bytes': 39282, 'sha256': '042cf21f807ce52ac3522285458f1c0407415c1f0883370f1d73404abd9e97d1'}

HOSTED_R5_WINDOWS_CAPTURE_LOADER_PIN = {'bytes': 42146, 'sha256': 'ca1647e90d766fb7035c4bdba06c2d7d6651ddca505b6ce98863e76ea8348e5d'}


HOSTED_R5_DG17_COMPOSED_LOADER_PIN = {'bytes': 58016, 'sha256': 'fb416808867945e763d5ed175d49722fc21ca4e4cc933deb5471fd43ada1a33c'}
# Current builder successor loader; the V9 row above stays an exact historical pair.
HOSTED_R5_BUDGET5_BUILDER_LOADER_PIN = {'bytes': 59606, 'sha256': 'eba57563d794e86dfd2429b9ba75ebe5e77f226bd527a9becea6386b2f641554'}
# Current compiler successor loader; the V10 row above stays an exact historical pair.
HOSTED_R5_DG17_OWNER_TEMPORARY_LOADER_PIN = {'bytes': 61142, 'sha256': '378844cf42ccd83009b0f1b0b42c800b2f303eb9a3ac0f4709a72788f2414943'}


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
        pins = (HOSTED_LOADER_PIN, HOSTED_PUBLIC_STREAMING_LOADER_PIN,
                HOSTED_CURRENT105_LOADER_PIN, HOSTED_CURRENT105_COMPOSED_LOADER_PIN,
                HOSTED_R4_COMPOSED_LOADER_PIN, HOSTED_R4_BUILD_LOCAL_LOADER_PIN, HOSTED_R4_INITIALIZATION_LOADER_PIN, HOSTED_R5_WINDOWS_INITIALIZATION_LOADER_PIN, HOSTED_R5_WINDOWS_CAPTURE_LOADER_PIN, HOSTED_R5_DG17_COMPOSED_LOADER_PIN,
                HOSTED_R5_BUDGET5_BUILDER_LOADER_PIN, HOSTED_R5_DG17_OWNER_TEMPORARY_LOADER_PIN)
        if not stat.S_ISREG(opening[2]) or opening[3] != 1 or opening[4] not in tuple(pin['bytes'] for pin in pins):
            raise ValueError('hosted current loader pin differs')
        raw = os.pread(fd, max(pin['bytes'] for pin in pins) + 1, 0)
        observed = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        if observed not in pins:
            raise ValueError('hosted current loader pin differs')
        module = types.ModuleType('c5_hosted_current_source_loader')
        module.__file__ = str(path)
        exec(compile(raw, str(path), 'exec'), module.__dict__)
        if observed == HOSTED_LOADER_PIN:
            current = module._Engine(module.CURRENT_PROFILE).load()
        elif observed == HOSTED_PUBLIC_STREAMING_LOADER_PIN:
            current = module._Engine(module.CURRENT_PROFILE,
                source_revision=module.PUBLIC_STREAMING_SOURCE_REVISION).load()
        elif observed == HOSTED_CURRENT105_LOADER_PIN:
            current = module._Engine(module.CURRENT_PROFILE,
                source_revision=module.CURRENT105_SOURCE_REVISION).load()
        elif observed == HOSTED_CURRENT105_COMPOSED_LOADER_PIN:
            current = module._Engine(module.CURRENT_PROFILE,
                source_revision=module.CURRENT105_COMPOSED_SOURCE_REVISION).load()
        elif observed == HOSTED_R4_COMPOSED_LOADER_PIN:
            current = module._Engine(module.CURRENT_PROFILE,
                source_revision=module.R4_COMPOSED_SOURCE_REVISION).load()
        elif observed == HOSTED_R4_BUILD_LOCAL_LOADER_PIN:
            current = module._Engine(module.R4_BUILD_CACHE_PROFILE,
                source_revision=module.R4_BUILD_CACHE_SOURCE_REVISION).load()
        elif observed == HOSTED_R4_INITIALIZATION_LOADER_PIN:
            current = module._Engine(module.R4_BUILD_CACHE_PROFILE,
                source_revision=module.R4_INITIALIZATION_SOURCE_REVISION).load()
        elif observed == HOSTED_R5_WINDOWS_INITIALIZATION_LOADER_PIN:
            current = module._Engine(module.R4_BUILD_CACHE_PROFILE,
                source_revision=module.R5_WINDOWS_INITIALIZATION_SOURCE_REVISION).load()
        elif observed == HOSTED_R5_DG17_OWNER_TEMPORARY_LOADER_PIN:
            current = module._Engine(module.R5_HOSTED_PROFILE,
                source_revision=module.R5_DG17_OWNER_TEMPORARY_SOURCE_REVISION).load()
        elif observed == HOSTED_R5_BUDGET5_BUILDER_LOADER_PIN:
            current = module._Engine(module.R5_HOSTED_PROFILE,
                source_revision=module.R5_BUDGET5_BUILDER_SOURCE_REVISION).load()
        elif observed == HOSTED_R5_DG17_COMPOSED_LOADER_PIN:
            current = module._Engine(module.R5_HOSTED_PROFILE,
                source_revision=module.R5_DG17_COMPOSED_SOURCE_REVISION).load()
        else:
            current = module._Engine(module.R4_BUILD_CACHE_PROFILE,
                source_revision=module.R5_WINDOWS_CAPTURE_SOURCE_REVISION).load()
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
        loader_raw = current.SOURCES['scripts/load-work-graph-c5-executor.py'][0]
        result['loader'] = {'bytes': len(loader_raw), 'sha256': hashlib.sha256(loader_raw).hexdigest()}
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



# AppArmor v4.0.1 bwrap-userns-restrict shape, with private job-only names.
# Setup gets userns capabilities; every exec stacks a capability-denying domain.
HOSTED_BWRAP_NAMES = ("implementaudit-c5-bwrap-v1", "implementaudit-c5-unpriv-bwrap-v1")
HOSTED_BWRAP_RECEIPT = "implementaudit-c5-bwrap-v1.json"
HOSTED_BWRAP_EXPORT_AGGREGATE = 4 * 1024**2
# A raw load record may contain a large permission DFA unrelated to its
# attachment. Keep the existing aggregate ceiling and the separate 64-KiB
# attachment-DFA ceiling; do not confuse total record size with match work.
HOSTED_BWRAP_EXPORT_LIMIT = HOSTED_BWRAP_EXPORT_AGGREGATE
HOSTED_BWRAP_POLICY_SHA256 = 'b3f303f76b8f2c097f92ca5e41b6e0126cd34a10df1d5d0e67b9e86e92e322af'
HOSTED_BWRAP_POLICY = b"""# Job-local CI adaptation of the AppArmor v4.0.1 bwrap/userns child boundary.
abi <abi/4.0>,
profile implementaudit-c5-bwrap-v1 /usr/bin/bwrap flags=(attach_disconnected) {
  allow capability,
  allow file rwlkm /{**,},
  allow network,
  allow unix,
  allow ptrace,
  allow signal,
  allow mqueue,
  allow io_uring,
  allow userns,
  allow mount,
  allow umount,
  allow pivot_root,
  allow dbus,
  allow px /** -> implementaudit-c5-bwrap-v1//&implementaudit-c5-unpriv-bwrap-v1,
}
profile implementaudit-c5-unpriv-bwrap-v1 flags=(attach_disconnected) {
  allow file rwlkm /{**,},
  allow network,
  allow unix,
  allow ptrace,
  allow signal,
  allow mqueue,
  allow io_uring,
  allow userns,
  allow mount,
  allow umount,
  allow pivot_root,
  allow dbus,
  allow pix /** -> &implementaudit-c5-unpriv-bwrap-v1,
  audit deny capability,
}
"""


def _bwrap_need(value, message):
    if not value:
        raise ValueError(message)


def _bwrap_read(path, maximum=4096):
    _bwrap_need(type(maximum) is int and 0 < maximum <= HOSTED_BWRAP_EXPORT_LIMIT,
                "hosted bwrap policy read bound differs")
    before = os.stat(path, follow_symlinks=False)
    _bwrap_need(stat.S_ISREG(before.st_mode), "hosted bwrap policy input is not a regular file")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        _bwrap_need(identity(os.fstat(fd)) == identity(before), "hosted bwrap policy input changed at open")
        raw = bytearray()
        while True:
            block = os.read(fd, min(65536, maximum + 1 - len(raw)))
            if not block:
                break
            raw.extend(block)
            _bwrap_need(len(raw) <= maximum, "hosted bwrap policy read bound exceeded")
        _bwrap_need(identity(os.fstat(fd)) == identity(before)
                    == identity(os.stat(path, follow_symlinks=False)),
                    "hosted bwrap policy input changed during read")
        return bytes(raw)
    finally:
        os.close(fd)


def _bwrap_regular(path, maximum):
    from pathlib import Path
    path = Path(path)
    for item in (path, *path.parents):
        info = item.lstat()
        _bwrap_need(not stat.S_ISLNK(info.st_mode) and info.st_uid == info.st_gid == 0
                    and not info.st_mode & 0o022, "hosted bwrap policy input custody differs")
    before = path.lstat()
    _bwrap_need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= maximum,
                "hosted bwrap policy input type/size differs")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        _bwrap_need(identity(os.fstat(fd)) == identity(before), "hosted bwrap policy input changed at open")
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(maximum + 1)
        _bwrap_need(len(raw) == before.st_size and identity(os.fstat(fd)) == identity(before)
                    == identity(path.lstat()), "hosted bwrap policy input changed during read")
        return raw, identity(before)
    finally:
        os.close(fd)


def _bwrap_disk_policies():
    from pathlib import Path
    entries = list(Path('/etc/apparmor.d').iterdir())
    _bwrap_need(len(entries) <= 4096, "hosted AppArmor policy directory exceeds bound")
    found = [str(path) for path in entries if 'bwrap' in path.name.lower() or 'bubblewrap' in path.name.lower()]
    extra = Path('/usr/share/apparmor/extra-profiles/bwrap-userns-restrict')
    try:
        extra.lstat()
        found.append(str(extra))
    except FileNotFoundError:
        pass
    return found


def hosted_bwrap_policy_context():
    _bwrap_need(not _bwrap_disk_policies(), "existing bwrap policy file refuses a second definition")
    paths = {'/sys/module/apparmor/parameters/enabled': 'Y',
             '/proc/sys/kernel/apparmor_restrict_unprivileged_userns': '1',
             '/proc/sys/kernel/unprivileged_userns_clone': '1'}
    current = {name: _bwrap_read(name, 32).decode('ascii').strip() for name in paths}
    _bwrap_need(current == paths, "hosted bwrap policy requires the unchanged restricted AppArmor host")
    _bwrap_need(hashlib.sha256(HOSTED_BWRAP_POLICY).hexdigest() == HOSTED_BWRAP_POLICY_SHA256,
                "hosted bwrap policy definition pin differs")
    files = {}
    for path, maximum in [('/usr/bin/bwrap', PIN['bytes']),
                          ('/usr/sbin/apparmor_parser', 4*1024**2), ('/etc/apparmor.d/abi/4.0', 65536)]:
        raw, observed = _bwrap_regular(path, maximum)
        files[path] = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), identity=observed)
    _bwrap_need({k: files['/usr/bin/bwrap'][k] for k in PIN} == PIN
                and stat.S_IMODE(files['/usr/bin/bwrap']['identity'][2]) == 0o755,
                "hosted bwrap policy launcher pin differs")
    _bwrap_need(not os.listxattr('/usr/bin/bwrap', follow_symlinks=False),
                "hosted bwrap policy launcher has unqualified extended metadata")
    return dict(global_state=current, files=files)


def hosted_bwrap_policy_inventory():
    from pathlib import Path
    import re
    root = Path('/sys/kernel/security/apparmor/policy/profiles')
    entries = sorted(root.iterdir())
    _bwrap_need(len(entries) <= 4096, "hosted AppArmor policy population exceeds bound")
    result = {}
    for entry in entries:
        _bwrap_need(stat.S_ISDIR(entry.lstat().st_mode), "hosted AppArmor policy entry is aliased")
        name = _bwrap_read(entry / 'name').decode('utf-8').strip()
        row = {key: _bwrap_read(entry / key).decode('utf-8').strip() for key in ('attach', 'mode', 'sha256')}
        _bwrap_need(name not in result and re.fullmatch('[0-9a-f]{64}', row['sha256']),
                    "hosted AppArmor policy identity is missing or duplicated")
        result[name] = row
    return result


def _bwrap_policy_refusal(message, name, row, guard):
    data = dict(name=name, record=row, guard=guard, truncated=False,
        predicates=dict(reserved_name=name in HOSTED_BWRAP_NAMES,
            name_heuristic='bwrap' in name.lower() or 'bubblewrap' in name.lower(),
            opaque_attachment=row['attach'] == '<unknown>', unresolved_variable='@{' in row['attach']))
    raw = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    if len(raw.encode('ascii')) > 16384:
        data.update(name=name[:128], record={key: value[:128] for key, value in row.items()},
            truncated=True, complete_record_sha256=hashlib.sha256(raw.encode('ascii')).hexdigest(),
            complete_record_bytes=len(raw))
        raw = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    return message + '; kernel_record=' + raw


def hosted_bwrap_policy_delta(before, after=None, *, opaque_proofs=None, expected_owned=None):
    import re
    proofs = {} if opaque_proofs is None else opaque_proofs
    _bwrap_need(type(proofs) is dict and set(proofs) <= set(before), 'opaque proof population differs')
    if expected_owned is not None:
        _bwrap_need(type(expected_owned) is dict and set(expected_owned) == set(HOSTED_BWRAP_NAMES)
                    and all(type(value) is str and re.fullmatch('[0-9a-f]{64}', value)
                            for value in expected_owned.values()), 'compiled owned profile identity differs')
    for name, row in before.items():
        _bwrap_need(type(row) is dict and set(row) == {'attach', 'mode', 'sha256'}
                    and all(type(value) is str for value in row.values()), "unknown loaded policy shape")
        attachment = row['attach']
        proof = proofs.get(name)
        proven = (type(proof) is dict and set(proof) == {'name', 'profile_sha256', 'raw_sha256', 'targets', 'result'}
            and proof['name'] == name and proof['profile_sha256'] == row['sha256']
            and type(proof['raw_sha256']) is str and re.fullmatch('[0-9a-f]{64}', proof['raw_sha256'])
            and type(proof['targets']) is list and proof['targets'] == ['/usr/bin/bwrap', '/bin/bwrap']
            and proof['result'] == 'PROVED_DFA_NOMATCH_BOTH_FIXED_PATHS')
        _bwrap_need(name not in HOSTED_BWRAP_NAMES and 'bwrap' not in name.lower()
                    and 'bubblewrap' not in name.lower() and (attachment != '<unknown>' or proven)
                    and '@{' not in attachment, _bwrap_policy_refusal(
                        "existing or opaque bwrap AppArmor policy refuses replacement", name, row, "name_or_opaque"))
        if attachment.startswith('/'):
            prefix = re.split(r'[*?\[{]', attachment, maxsplit=1)[0]
            _bwrap_need(not any(target == attachment or prefix != attachment and target.startswith(prefix)
                               for target in ('/usr/bin/bwrap', '/bin/bwrap')),
                        _bwrap_policy_refusal("existing attachment may already govern bwrap", name, row, "target_attachment"))
    if after is not None:
        _bwrap_need(set(after) == set(before) | set(HOSTED_BWRAP_NAMES)
                    and all(after[name] == row for name, row in before.items()),
                    "hosted bwrap policy changed an unrelated policy")
        for name, attach in zip(HOSTED_BWRAP_NAMES, ('/usr/bin/bwrap', HOSTED_BWRAP_NAMES[1])):
            row = after[name]
            _bwrap_need(type(row) is dict and set(row) == {'attach', 'mode', 'sha256'}
                        and (row['attach'] == attach or expected_owned is not None
                             and name == HOSTED_BWRAP_NAMES[0] and row['attach'] == '<unknown>')
                        and row['mode'] == 'enforce'
                        and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']),
                        "hosted bwrap policy activation readback differs")
            if expected_owned is not None:
                _bwrap_need(row['sha256'] == expected_owned[name], 'loaded policy differs from exact approved compilation')


def _bwrap_selected_export(entry, root, maximum=HOSTED_BWRAP_EXPORT_LIMIT):
    """Receive one kernel-linked raw export; this cannot admit or load policy."""
    from pathlib import Path
    import re
    # policy is a kernel magic link: readlink's apparmorfs:[ino] is not a
    # userspace pathname. Keep that kernel traversal and validate only the
    # documented relative links from a top-level profile to one raw export.
    root = Path(root).absolute()
    entry = Path(entry)
    _bwrap_need(entry.parent == root / 'profiles', 'selected kernel export path is not a top-level profile')
    names = {'raw_data': 'raw_data', 'raw_sha256': 'sha256', 'raw_abi': 'abi'}
    links = {name: os.readlink(entry / name) for name in names}
    parts = {name: Path(link).parts for name, link in links.items()}
    _bwrap_need(all(len(value) == 5 and value[:3] == ('..', '..', 'raw_data')
                and value[3] not in ('.', '..') and value[4] == names[name] for name, value in parts.items())
                and len({value[3] for value in parts.values()}) == 1,
                'selected kernel export path is outside one raw policy record')
    paths = {name: root / 'raw_data' / value[3] / value[4] for name, value in parts.items()}
    directories = (entry, root / 'profiles', root / 'raw_data', paths['raw_data'].parent)
    directory_info = {path: path.lstat() for path in directories}
    _bwrap_need(all(stat.S_ISDIR(info.st_mode) for info in directory_info.values()),
                'selected kernel export directory is aliased')
    observed = {path: identity(path.lstat()) for path in (*directories, *paths.values())}
    _bwrap_need(type(maximum) is int and 0 < maximum <= HOSTED_BWRAP_EXPORT_LIMIT,
                'selected kernel export aggregate bound exhausted')
    # AppArmor rawdata_open allocates/decompresses the immutable load record
    # before the first read. Its raw_data inode advertises uncompressed size;
    # reject that work before open, not merely after reading maximum+1 bytes.
    # Other sysfs fields can advertise a page for a short value, so this check
    # belongs to this selected raw-export path, not the generic text reader.
    def read_raw():
        advertised = paths['raw_data'].lstat()
        _bwrap_need(stat.S_ISREG(advertised.st_mode) and 0 < advertised.st_size <= maximum,
                    'selected kernel export advertised size exceeds bound')
        raw = _bwrap_read(paths['raw_data'], maximum)
        _bwrap_need(len(raw) == advertised.st_size,
                    'selected kernel export length differs from advertised size')
        return raw
    raw = read_raw()
    digest = _bwrap_read(paths['raw_sha256'], 128).decode('ascii').strip()
    abi = _bwrap_read(paths['raw_abi'], 32).decode('ascii').strip()
    _bwrap_need(re.fullmatch('[0-9a-f]{64}', digest) and hashlib.sha256(raw).hexdigest() == digest,
                'selected kernel raw export hash differs')
    _bwrap_need(re.fullmatch('v[0-9]+', abi), 'selected kernel raw export ABI is unsupported')
    _bwrap_need(links == {name: os.readlink(entry / name) for name in names}
                and read_raw() == raw
                and _bwrap_read(paths['raw_sha256'], 128).decode('ascii').strip() == digest
                and _bwrap_read(paths['raw_abi'], 32).decode('ascii').strip() == abi
                and observed == {path: identity(path.lstat()) for path in observed},
                'selected kernel export changed during readback')
    return dict(bytes=len(raw), sha256=digest, abi=abi, base64=base64.b64encode(raw).decode('ascii'),
                kernel_path=str(paths['raw_data']),
                scope='RAW_LOAD_EXPORT_LINKED_TO_SELECTED_PROFILE_NOT_DECODED_ATTACHMENT')


def diagnose_hosted_bwrap_policy(selected_name='1password'):
    """Read a retained refusal without policy effects or admission authority."""
    from pathlib import Path
    source_names = {'1password': '1password', 'tcpdump': 'usr.bin.tcpdump'}
    _bwrap_need(type(selected_name) is str and selected_name in source_names,
                'unsupported selected policy diagnostic selection')
    _bwrap_root()
    context = hosted_bwrap_policy_context()
    before = hosted_bwrap_policy_inventory()
    selected = before.get(selected_name)
    _bwrap_need(selected is not None and selected['attach'] == '<unknown>',
                'selected opaque record changed; diagnostic is inapplicable')
    root = Path('/sys/kernel/security/apparmor/policy')
    entries = list((root / 'profiles').iterdir())
    _bwrap_need(len(entries) <= 4096, 'selected policy lookup exceeds bound')
    matched = [entry for entry in entries if _bwrap_read(entry / 'name').decode('utf-8').strip() == selected_name]
    _bwrap_need(len(matched) == 1, 'selected policy lookup is missing or ambiguous')
    exported = _bwrap_selected_export(matched[0], root)
    try:
        proof = _bwrap_prove_nonmatch(base64.b64decode(exported['base64'], validate=True), selected_name, selected)
        attachment_observation = dict(status='PROVED_NOMATCH', proof=proof)
    except (ValueError, UnicodeError) as exc:
        attachment_observation = dict(status='REFUSED', reason=str(exc)[:256])
    sources = {}
    for name in ('/etc/apparmor.d/' + source_names[selected_name],
                 '/etc/apparmor.d/local/' + source_names[selected_name]):
        try:
            raw, observed = _bwrap_regular(name, 16384)
        except FileNotFoundError:
            sources[name] = dict(status='ABSENT_AT_READ')
        else:
            sources[name] = dict(status='READ_ONLY_SOURCE_NOT_LOADED_EQUIVALENCE', bytes=len(raw),
                sha256=hashlib.sha256(raw).hexdigest(), identity=observed,
                base64=base64.b64encode(raw).decode('ascii'))
    _bwrap_need(hosted_bwrap_policy_inventory() == before and hosted_bwrap_policy_context() == context,
                'selected diagnostic inventory or input bookends differ')
    print(json.dumps(dict(schema='implementaudit.selected-opaque-policy-diagnostic.v1',
        authority='NONE', policy_operations=0, selected_name=selected_name, selected_record=selected,
        exported=exported, source_files=sources, parser=context['files']['/usr/sbin/apparmor_parser'],
        attachment_observation=attachment_observation, raw_export_bound=HOSTED_BWRAP_EXPORT_LIMIT,
        parser_version='NOT_EXECUTED; BINARY_IDENTITY_ONLY',
        interpretation='READ_ONLY_OBSERVATION_NO_ATTACHMENT_OR_ADMISSION_VERDICT',
        inventory_input_bookends_equal=True), sort_keys=True))
    return 0


def _bwrap_v5_profiles(raw):
    """Closed ABI5 framing and profile hashes, not a policy authorization."""
    import struct
    _bwrap_need(type(raw) is bytes and 0 < len(raw) <= HOSTED_BWRAP_EXPORT_LIMIT,
                'compiled policy export bound differs')
    position = 0
    nodes = 0
    def take(count):
        nonlocal position
        _bwrap_need(0 <= count <= len(raw) - position, 'truncated compiled policy export')
        value = raw[position:position + count]
        position += count
        return value
    def number(width):
        return int.from_bytes(take(width), 'little')
    def string():
        value = take(number(2))
        _bwrap_need(value and value[-1] == 0, 'compiled policy string is not terminated')
        return value[:-1]
    def node(depth=0, parents=(), previous=()):
        nonlocal nodes
        nodes += 1
        _bwrap_need(depth <= 16 and nodes <= 8192, 'compiled policy structure exceeds bound')
        start = position
        kind = number(1)
        name = None
        if kind == 4:
            name = string()
            _bwrap_need(b'\0' not in name and len(name) <= 4096, 'compiled policy field name differs')
            kind = number(1)
        data_start = position
        if kind in (0, 1, 2, 3):
            value = number((1, 2, 4, 8)[kind])
        elif kind == 5:
            value = string()
        elif kind == 6:
            count = number(4)
            data_start = position
            value = take(count)
        elif kind in (7, 9, 11):
            count = number(2) if kind == 11 else None
            _bwrap_need(count is None or count <= 4096, 'compiled policy array exceeds bound')
            ending = {7: 8, 9: 10, 11: 12}[kind]
            value = []
            while position < len(raw) and raw[position] != ending:
                value.append(node(depth + 1, parents + ((kind, name),), value if kind == 7 and name == b'perms' else ()))
            if kind == 11 and name == b'net_allowed_af':
                # ABI5 counts network records; each carries three unnamed
                # u16 values (allow, audit, quiet), not one scalar element.
                _bwrap_need(depth == 1 and all(item['kind'] == 1 and item['name'] is None
                            for item in value), 'unsupported compiled network array')
                count *= 3
            if kind == 11 and name is None and parents[-1:] == ((7, b'perms'),):
                # AppArmor5 ABI5 permission tables count records, each14 U32s.
                _bwrap_need(parents in (((7, b'profile'), (7, b'policydb'), (7, b'perms')), ((7, b'profile'), (7, b'perms')))
                            and len(previous) == 1 and previous[0]['kind'] == 2
                            and previous[0]['name'] == b'version' and previous[0]['value'] == 1,
                            'unsupported compiled permission table context or version')
                _bwrap_need(all(item['kind'] == 2 and item['name'] is None for item in value)
                            and len(value) == count * 14
                            and all(value[i]['value'] == 0 for i in range(0, len(value), 14)),
                            'unsupported compiled permission record')
                count *= 14
            _bwrap_need(number(1) == ending and (count is None or len(value) == count),
                        'compiled policy container differs')
        else:
            raise ValueError('unsupported compiled policy token')
        if kind == 7 and name == b'perms':
            _bwrap_need(parents in (((7, b'profile'), (7, b'policydb')), ((7, b'profile'),))
                        and len(value) == 2 and value[0]['kind'] == 2
                        and value[0]['name'] == b'version' and value[0]['value'] == 1
                        and value[1]['kind'] == 11 and value[1]['name'] is None,
                        'unsupported compiled permission table framing')
        return dict(kind=kind, name=name, value=value, start=start, end=position, data_start=data_start)
    result = {}
    while position < len(raw):
        version = node()
        _bwrap_need((version['kind'], version['name'], version['value']) == (2, b'version', 5),
                    'unsupported compiled policy ABI or namespace')
        profile = node()
        _bwrap_need(profile['kind'] == 7 and profile['name'] == b'profile', 'compiled profile framing differs')
        fields = profile['value']
        _bwrap_need(fields and fields[0]['kind'] == 5 and fields[0]['name'] is None
                    and b'\0' not in fields[0]['value'], 'compiled profile name differs')
        name = fields[0]['value'].decode('utf-8')
        _bwrap_need(name and name not in result, 'compiled profile name is missing or duplicated')
        xmatch = None
        if len(fields) > 1 and fields[1]['kind'] == 6 and fields[1]['name'] == b'aadfa':
            item = fields[1]
            pad = (-(item['data_start'] - (item['end'] & 7))) % 8
            _bwrap_need(item['value'][:pad] == b'\0' * pad and len(fields) > 3
                        and fields[2]['kind'] == 2 and fields[2]['name'] is None
                        and fields[3]['kind'] == 7 and fields[3]['name'] == b'flags',
                        'unsupported compiled attachment framing')
            xmatch = item['value'][pad:]
        else:
            _bwrap_need(len(fields) > 1 and fields[1]['kind'] == 7 and fields[1]['name'] == b'flags',
                        'unsupported compiled attachment fields')
        digest = hashlib.sha256(struct.pack('<I', 5) + raw[profile['start']:profile['end']]).hexdigest()
        result[name] = dict(sha256=digest, xmatch=xmatch, abi=5)
    return result


def _bwrap_dfa_nonmatch(dfa, path):
    """Conservative direct/differential attachment check; only state0 proves nonmatch."""
    import struct
    _bwrap_need(type(dfa) is bytes and 24 <= len(dfa) <= 65536, 'unsupported attachment DFA bound')
    magic, header, size, flags = struct.unpack_from('>IIIH', dfa)
    _bwrap_need(magic == 0x1b5e783d and 14 <= header <= size == len(dfa) and flags in (0, 1),
                'unsupported attachment DFA header')
    position = header
    tables = {}
    widths = {1: 4, 2: 4, 3: 2, 4: 2, 5: 1, 7: 4, 8: 2}
    while position < len(dfa):
        _bwrap_need(position + 12 <= len(dfa), 'truncated attachment table')
        ident, width, high, count = struct.unpack_from('>HHII', dfa, position)
        end = position + 12 + width * count
        _bwrap_need(ident in widths and ident not in tables and width == widths[ident]
                    and high == 0 and 0 < count <= 65535 and end <= len(dfa), 'unsupported attachment table')
        tables[ident] = [int.from_bytes(dfa[i:i + width], 'big') for i in range(position + 12, end, width)]
        position = (end + 7) // 8 * 8
    _bwrap_need(position == len(dfa) and {1, 2, 3, 4, 7, 8} <= set(tables), 'attachment tables incomplete')
    states = len(tables[2])
    differential = 0x80000000
    _bwrap_need(states >= 2 and all(len(tables[i]) == states for i in (1, 4, 7))
                and len(tables[3]) == len(tables[8]) and tables[1][0] == 0
                and all(value & ~(0x00ffffff | differential) == 0
                        and (not value & differential or flags == 1) for value in tables[2])
                and all((value & 0x00ffffff) + 255 < len(tables[3]) for value in tables[2])
                and all(value < states for ident in (3, 4, 8) for value in tables[ident])
                and (5 not in tables or len(tables[5]) == 256), 'unsupported attachment states')
    # Differential defaults retry the SAME byte. Validate the default graph
    # first, so corrupt self-loops or longer cycles cannot stall that retry.
    resolved = set()
    for initial in range(states):
        current = initial
        chain = set()
        while tables[2][current] & differential and current not in resolved:
            _bwrap_need(current not in chain, 'cyclic differential attachment default')
            chain.add(current)
            current = tables[4][current]
        resolved.update(chain)
    def retry_transition(initial, character, cached):
        chain = []
        state = initial
        while state not in cached:
            base = tables[2][state]
            slot = (base & 0x00ffffff) + character
            if tables[3][slot] == state:
                cached[state] = tables[8][slot]
                break
            if not base & differential:
                cached[state] = tables[4][state]
                break
            chain.append(state)
            state = tables[4][state]
        result = cached[state]
        for state in chain:
            cached[state] = result
        return result
    # Attachment leftmatch uses direct defaults until its loop fallback calls
    # the differential matcher. Overapproximate every possible switch point;
    # checking only an all-direct and an all-retry traversal is insufficient.
    possible = {1}
    for character in path.encode('ascii'):
        if 5 in tables:
            character = tables[5][character]
        # A fallback beginning at state0 returns immediately. Preserve that
        # rejecting result as well as any table transition from state0.
        following = {0} if 0 in possible else set()
        cached = {}
        for state in possible:
            base = tables[2][state]
            slot = (base & 0x00ffffff) + character
            following.add(tables[8][slot] if tables[3][slot] == state else tables[4][state])
            following.add(retry_transition(state, character, cached))
        possible = following
    return possible == {0}


def _bwrap_prove_nonmatch(raw, name, row):
    _bwrap_need(type(row) is dict and set(row) == {'attach', 'mode', 'sha256'}
                and all(type(value) is str for value in row.values()) and row['attach'] == '<unknown>',
                'opaque attachment record differs')
    profiles = _bwrap_v5_profiles(raw)
    _bwrap_need(name in profiles and profiles[name]['sha256'] == row['sha256'],
                'compiled attachment profile identity differs')
    targets = ['/usr/bin/bwrap', '/bin/bwrap']
    _bwrap_need(all(_bwrap_dfa_nonmatch(profiles[name]['xmatch'], target) for target in targets),
                'existing compiled attachment may govern bwrap')
    return dict(name=name, profile_sha256=row['sha256'], raw_sha256=hashlib.sha256(raw).hexdigest(),
                targets=targets, result='PROVED_DFA_NOMATCH_BOTH_FIXED_PATHS')


def _bwrap_resolve_opaque(inventory):
    """Fresh kernel bytes only; no name exemptions or caller-supplied exports."""
    from pathlib import Path
    root = Path('/sys/kernel/security/apparmor/policy')
    selected = {name: row for name, row in inventory.items() if row['attach'] == '<unknown>'
                and name not in HOSTED_BWRAP_NAMES and 'bwrap' not in name.lower()
                and 'bubblewrap' not in name.lower()}
    if not selected:
        return {}
    entries = list((root / 'profiles').iterdir())
    _bwrap_need(len(entries) <= 4096, 'compiled attachment inventory exceeds bound')
    indexed = {}
    for entry in entries:
        _bwrap_need(stat.S_ISDIR(entry.lstat().st_mode), 'compiled attachment entry is aliased')
        name = _bwrap_read(entry / 'name').decode('utf-8').strip()
        _bwrap_need(name not in indexed, 'compiled attachment name is duplicated')
        indexed[name] = entry
    proofs = {}
    total = 0
    for name, row in selected.items():
        try:
            _bwrap_need(name in indexed, 'compiled attachment entry disappeared')
            exported = _bwrap_selected_export(indexed[name], root,
                min(HOSTED_BWRAP_EXPORT_LIMIT, HOSTED_BWRAP_EXPORT_AGGREGATE - total))
            total += exported['bytes']
            proofs[name] = _bwrap_prove_nonmatch(base64.b64decode(exported['base64'], validate=True), name, row)
        except (OSError, ValueError, UnicodeError) as exc:
            raise ValueError(_bwrap_policy_refusal('unresolved compiled attachment: ' + str(exc)[:256],
                name, row, 'compiled_attachment')) from exc
    _bwrap_need(hosted_bwrap_policy_inventory() == inventory, 'compiled attachment inventory changed')
    return proofs


def _bwrap_compile_userspace(policy):
    """One no-load compilation; explicitly request uncompressed userspace output.

    AppArmor5's -c controls only its output container. Keep old4.x argv and all
    ABI/profile/hash/oracle checks; never use this helper for a kernel operation.
    Version query and compile share the original20-second/64-KiB/8-KiB budget.
    """
    import re
    stop = time.monotonic() + 20
    version = subprocess.run(['/usr/sbin/apparmor_parser', '--version'], env=dict(ENV), cwd='/',
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=max(0.001, stop-time.monotonic()), check=False)
    _bwrap_need(version.returncode == 0 and 0 < len(version.stdout) <= 2048
                and len(version.stderr) <= 8192, 'userspace compiler version refused')
    line = version.stdout.splitlines()[0]
    match = re.fullmatch(rb'AppArmor parser version ([0-9]+)(?:\.[0-9]+){1,2}(?:-[A-Za-z0-9.+-]+)?', line)
    _bwrap_need(match is not None, 'userspace compiler version shape differs')
    argv = ['/usr/sbin/apparmor_parser', '--config-file=/dev/null', '--skip-cache',
        '--skip-read-cache', '--jobs=0', '--skip-kernel-load', '--stdout']
    if int(match.group(1)) >= 5:
        argv.append('--zstd-compress-level=0')
    remaining = stop-time.monotonic()
    _bwrap_need(remaining > 0, 'userspace compiler deadline exhausted')
    result = subprocess.run(argv, input=policy, env=dict(ENV), cwd='/', stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=remaining, check=False)
    _bwrap_need(time.monotonic() <= stop and result.returncode == 0
                and 0 < len(result.stdout) <= 65536-len(version.stdout)
                and len(result.stderr) <= 8192-len(version.stderr),
                'approved policy compilation failed or exceeded bound')
    return result.stdout


def _bwrap_expected_compilation():
    """Compile approved bytes to stdout, with kernel loading and caches disabled."""
    profiles = _bwrap_v5_profiles(_bwrap_compile_userspace(HOSTED_BWRAP_POLICY))
    _bwrap_need(set(profiles) == set(HOSTED_BWRAP_NAMES), 'approved compiled profile population differs')
    return {name: row['sha256'] for name, row in profiles.items()}


def hosted_bwrap_policy_parser(mode):
    _bwrap_need(mode in ('--skip-kernel-load', '--add'), "unsupported hosted policy operation")
    result = subprocess.run(['/usr/sbin/apparmor_parser', '--config-file=/dev/null', '--skip-cache',
        '--skip-read-cache', '--jobs=0', mode], input=HOSTED_BWRAP_POLICY, env=dict(ENV), cwd='/',
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20, check=False)
    _bwrap_need(len(result.stdout) <= 8192 and len(result.stderr) <= 8192 and result.returncode == 0,
                'hosted bwrap policy parser refused: ' + result.stderr[:2048].decode('utf-8', 'replace'))
    return dict(exit_code=result.returncode, stdout=result.stdout.decode('utf-8', 'replace'),
                stderr=result.stderr.decode('utf-8', 'replace'))


def create_hosted_bwrap_receipt(parent):
    current = os.fstat(parent)
    _bwrap_need(stat.S_ISDIR(current.st_mode) and current.st_uid == os.geteuid()
                and current.st_gid == os.getegid() and not current.st_mode & 0o022,
                "hosted bwrap receipt parent custody differs")
    fd = os.open(HOSTED_BWRAP_RECEIPT, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                 0o600, dir_fd=parent)
    os.fchmod(fd, 0o600)
    return fd


def _bwrap_store(fd, value):
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()
    _bwrap_need(len(raw) <= 16384, "hosted bwrap receipt exceeds bound")
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    view = memoryview(raw)
    while view:
        count = os.write(fd, view)
        _bwrap_need(count > 0, "hosted bwrap receipt write stalled")
        view = view[count:]
    os.fsync(fd)
    _bwrap_need(os.pread(fd, len(raw) + 1, 0) == raw, "hosted bwrap receipt readback differs")


def _bwrap_root():
    _bwrap_need(os.geteuid() == os.getegid() == 0, "hosted bwrap policy requires explicit root invocation")
    _bwrap_need(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted",
                "hosted bwrap policy is restricted to an explicitly selected ephemeral GitHub-hosted job")


def provision_hosted_bwrap_policy():
    _bwrap_root()
    context = hosted_bwrap_policy_context()
    before = hosted_bwrap_policy_inventory()
    opaque_proofs = _bwrap_resolve_opaque(before)
    hosted_bwrap_policy_delta(before, opaque_proofs=opaque_proofs)
    expected = _bwrap_expected_compilation()
    _bwrap_need(hosted_bwrap_policy_context() == context and hosted_bwrap_policy_inventory() == before,
                'hosted bwrap pre-add inputs or policy changed')
    parent = os.open('/run', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    fd = None
    try:
        fd = create_hosted_bwrap_receipt(parent)
        record = dict(schema='implementaudit.hosted-bwrap-policy.v2', state='PENDING',
            profile_sha256=HOSTED_BWRAP_POLICY_SHA256, context=context, loaded={}, compiled_profiles=expected)
        _bwrap_store(fd, record); os.fsync(parent)
        command = hosted_bwrap_policy_parser('--add')  # One add, never replace or retry.
        after = hosted_bwrap_policy_inventory()
        hosted_bwrap_policy_delta(before, after, opaque_proofs=_bwrap_resolve_opaque(after), expected_owned=expected)
        _bwrap_need(hosted_bwrap_policy_context() == context, "hosted bwrap activation input/global state changed")
        record.update(state='ACTIVE', loaded={name: after[name] for name in HOSTED_BWRAP_NAMES})
        _bwrap_store(fd, record)
        print(json.dumps(dict(scope='EPHEMERAL_CI_BWRAP_POLICY_ONLY_NO_NATIVE_ACCEPTANCE',
            profile_sha256=HOSTED_BWRAP_POLICY_SHA256, loaded=record['loaded'], parser=command,
            compiled_profiles=expected, resolved_opaque_count=len(opaque_proofs),
            opaque_proofs_sha256=hashlib.sha256(json.dumps(opaque_proofs, sort_keys=True,
                separators=(',', ':')).encode()).hexdigest(),
            global_state_unchanged=True, receipt='/run/' + HOSTED_BWRAP_RECEIPT), sort_keys=True))
        return 0
    finally:
        if fd is not None: os.close(fd)
        os.close(parent)


def hosted_bwrap_policy_observation(record, current, before, *, opaque_proofs=None):
    _bwrap_need(type(record) is dict, 'hosted bwrap receipt shape differs')
    keys = {'schema', 'state', 'profile_sha256', 'context', 'loaded'}
    version2 = record.get('schema') == 'implementaudit.hosted-bwrap-policy.v2'
    if version2:
        keys.add('compiled_profiles')
    _bwrap_need(set(record) == keys
                and record['schema'] in ('implementaudit.hosted-bwrap-policy.v1', 'implementaudit.hosted-bwrap-policy.v2')
                and record['state'] == 'ACTIVE'
                and record['profile_sha256'] == HOSTED_BWRAP_POLICY_SHA256
                and set(record['loaded']) == set(HOSTED_BWRAP_NAMES),
                "pending, malformed or different bwrap policy receipt; retain for VM disposal")
    _bwrap_need(json.dumps(current, sort_keys=True) == json.dumps(record['context'], sort_keys=True)
                and all(before.get(name) == row for name, row in record['loaded'].items()),
                "hosted bwrap observation inputs or loaded policy changed")
    foreign = {name: row for name, row in before.items() if name not in HOSTED_BWRAP_NAMES}
    hosted_bwrap_policy_delta(foreign, before, opaque_proofs=opaque_proofs,
                             expected_owned=record['compiled_profiles'] if version2 else None)



def finalize_hosted_bwrap_policy():
    """Read/record only; never unload a label or unlink its receipt.

    A snapshot cannot exclude a subsequent ordinary exec/fork. The dedicated
    hosted VM's disposal is the only teardown boundary for this job-local policy.
    """
    from pathlib import Path
    _bwrap_root()
    path = Path('/run') / HOSTED_BWRAP_RECEIPT
    before = hosted_bwrap_policy_inventory()  # Mandatory even when no receipt exists.
    try:
        path.lstat()
    except FileNotFoundError:
        _bwrap_need(not any(name in before for name in HOSTED_BWRAP_NAMES),
                    "unreceipted bwrap policy observed; retain for VM disposal")
        print(json.dumps(dict(scope='EPHEMERAL_CI_BWRAP_POLICY_OBSERVATION_ONLY',
            status='NO_OWNED_POLICY_OBSERVED', kernel_policy_unloaded=False, receipt_unlinked=False,
            retained_until='EPHEMERAL_VM_DISPOSAL', observation_limit='SNAPSHOT_ONLY_NOT_LAUNCH_EXCLUSION')))
        return 0
    raw, observed = _bwrap_regular(path, 16384)
    _bwrap_need(stat.S_IMODE(observed[2]) == 0o600, "hosted bwrap receipt mode differs")
    def unique(items):
        result = {}
        for key, value in items:
            _bwrap_need(key not in result, "duplicate hosted bwrap receipt field")
            result[key] = value
        return result
    record = json.loads(raw, object_pairs_hook=unique)
    hosted_bwrap_policy_observation(record, hosted_bwrap_policy_context(), before,
                                   opaque_proofs=_bwrap_resolve_opaque(before))
    print(json.dumps(dict(scope='EPHEMERAL_CI_BWRAP_POLICY_OBSERVATION_ONLY',
        status='ACTIVE_POLICY_AND_RECEIPT_RETAINED', profile_sha256=HOSTED_BWRAP_POLICY_SHA256,
        loaded=record['loaded'], kernel_policy_unloaded=False, receipt_unlinked=False,
        retained_until='EPHEMERAL_VM_DISPOSAL', observation_limit='SNAPSHOT_ONLY_NOT_LAUNCH_EXCLUSION'), sort_keys=True))
    return 0


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
        if sys.argv[1:] == ['--diagnose-hosted-bwrap-policy']:
            raise SystemExit(diagnose_hosted_bwrap_policy())
        if len(sys.argv) == 3 and sys.argv[1] == '--diagnose-hosted-bwrap-policy':
            raise SystemExit(diagnose_hosted_bwrap_policy(sys.argv[2]))
        if sys.argv[1:] == ['--provision-hosted-bwrap-policy']:
            raise SystemExit(provision_hosted_bwrap_policy())
        if sys.argv[1:] == ['--finalize-hosted-bwrap-policy']:
            raise SystemExit(finalize_hosted_bwrap_policy())
        if sys.argv[1:] == ['--provision-hosted-launcher']:
            raise SystemExit(provision_hosted_launcher())
        if len(sys.argv) == 3 and sys.argv[1] == '--receive-hosted-prerequisites':
            raise SystemExit(receive_hosted_prerequisites(sys.argv[2]))
        if sys.argv[1:]:
            raise ValueError('unsupported setup observer arguments')
        raise SystemExit(main())
    finally:
        emergency_cleanup()
