#!/usr/bin/env python3
"""DG16 placement-only diagnostic operator (proposal; no authority, no awards).

Runs once, as UID 0, on a disposable GitHub-hosted ubuntu-24.04 runner, from a
root-owned 0700 copy of the checked pinned files. It observes only the host
placement properties that the G1/G3 core binds through the private ACCESS09
roles, and emits every observation publicly:

  P1 ROOT_CREDENTIALS        real/effective uid/gid are 0
  P2 ROOT_ANCESTOR_CUSTODY   '/' is a root:root directory, no g/o write, no POSIX ACL
  P3 EXCLUSIVE_FRESH_ISLAND  /dg16-g1-<run_id> absent, created exclusively 0700, root, no ACL
  P4 FIXED_SIBLINGS          packet/ 0700 (with a 0400 write_new probe, a nested 0700 dir and
                             read_file readback), then source/ and output/ 0755 as the core
                             creates them, observed with the live-phase observe_fd(fd)
  P5 FD_ROUTE                launcher provisioned by the pinned V21 setup if absent; the
                             pinned job-local bwrap AppArmor policy provisioned as the core does;
                             the held packet FD bound read-only by the pinned bwrap into a new user
                             namespace whose uid 0 is mapped to host root, with all capabilities
                             dropped (ACCESS09 row I0 operator)
  P6 ANCESTRY_NO_DRIFT       full ancestry/ACL/mount/credential snapshot unchanged across P5
  P7 CLOSING_CURRENTNESS     policy still active, launcher unchanged, no remaining children,
                             path/FD joins and observations unchanged at close

Placement is a host property, not a property of the recorded product subject.
Observation functions are imported from exact pinned copies of
root_placement.py (b393a905) and access_matrix.py (f447037c); bootstrap() and
require_current() are NOT called (they require Root admission and a packet).
No cleanup: the runner is disposable and the core forbids recursive removal.
"""
import base64, errno, glob, hashlib, json, os, re, resource, stat, subprocess, sys, time, types
from pathlib import Path

SCHEMA = 'dg16.placement-only-diagnostic-receipt.v2'
MANIFEST_SCHEMA = 'dg16.placement-only-diagnostic-artifacts.v1'
MARKER = 'DG16_PLACEMENT_DIAG_EVIDENCE'
CHUNK_CHARS = 4096
REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
TRIGGER_BRANCH = 'engineering/opus-dg16-placement-diag-trigger-20261125'
SUBJECT = dict(commit='338c4c36d2ac95ca24345bc92fe8c53d66eaa15d', tree='53498df783ed441744ae5080982c2d5e59c34bbc',
               relation='RECORDED_PRODUCT_SUBJECT_ONLY_PLACEMENT_IS_A_HOST_PROPERTY')
MODULES = {
    'root_placement': dict(bytes=17123, sha256='18a93f8206a42435f73580ca65cf16d20dad96cb337b84a6d30104cce772ad4a',
                           origin='b393a9057c249335e6cdf4ccbb898d192b0830b8:qualification/dg16-r5-g1-hosted-episode/root_placement.py'),
    'access_matrix': dict(bytes=67584, sha256='d0c192b858c5c806e3001d002bf013bb4add480e7ed818112c7ee16162763082',
                          origin='f447037c5bafefb35b9bd11b5090ce3c681c4756:qualification/dg16-r5-g1-intake-diagnostic/access_matrix.py')}
# Maintained, already-qualified V21 launcher/policy route (executed, not reimplemented).
SETUP = dict(path='scripts/qualify-work-graph-c5-setup.py', bytes=86876,
             sha256='5e999f80140c517331943ecbac4215719d8f9416923672b7741788fe0ad673a9',
             origin='338c4c36d2ac95ca24345bc92fe8c53d66eaa15d:scripts/qualify-work-graph-c5-setup.py')
LAUNCHER_PACKAGE = dict(url='https://snapshot.ubuntu.com/ubuntu/20260901T000000Z/pool/main/b/bubblewrap/bubblewrap_0.9.0-1ubuntu0.1_amd64.deb',
                        bytes=50178, sha256='1b506492bd9c7fd0cdb4f02ac822f1d3e336b0aead5113c1239baf8db5db562a')
PROVISION_SCOPE = 'LINUX_LAUNCHER_PROVISION_ONLY_NO_C5_OR_NATIVE_ACCEPTANCE'
RETRY_LINE = b'urllib.error.HTTPError: HTTP Error 502: Bad Gateway'
EXEC_DIR = 'qualification/dg16-placement-diagnostic'
EXEC_PARENT = '/run'
EXEC_FILES = (EXEC_DIR + '/diagnose.py', EXEC_DIR + '/root_placement.py', EXEC_DIR + '/access_matrix.py', SETUP['path'])
PROBE = b'DG16_PLACEMENT_FIXED_NONSECRET_PROBE\n'
STEPS = ('HOSTED_CONTEXT', 'CREDENTIALS', 'EXEC_CUSTODY', 'HOST_FACTS', 'ROOT_OBSERVE', 'ISLAND_ABSENT_BEFORE',
         'ISLAND_CREATE', 'PACKET_CREATE', 'SOURCE_OUTPUT_ABSENT_AT_PACKET', 'BOOTSTRAP_CLOSING_CUSTODY',
         'PACKET_FILE_CUSTODY', 'SENTINEL_CREATE', 'FIXED_SIBLINGS_CREATE', 'LIVE_CURRENT', 'ANCESTRY_BEFORE',
         'LAUNCHER_PROVISION', 'TOOL_PIN', 'POLICY_PROVISION', 'FD_ROUTE', 'ANCESTRY_AFTER', 'POLICY_FINAL',
         'TOOL_AFTER', 'CLOSING_CURRENT')
PROPERTIES = {
    'P1_ROOT_CREDENTIALS': ('CREDENTIALS',),
    'P2_ROOT_ANCESTOR_CUSTODY': ('ROOT_OBSERVE',),
    'P3_EXCLUSIVE_FRESH_ISLAND': ('ISLAND_ABSENT_BEFORE', 'ISLAND_CREATE'),
    'P4_FIXED_SIBLINGS': ('PACKET_CREATE', 'SOURCE_OUTPUT_ABSENT_AT_PACKET', 'BOOTSTRAP_CLOSING_CUSTODY',
                          'PACKET_FILE_CUSTODY', 'FIXED_SIBLINGS_CREATE', 'LIVE_CURRENT'),
    'P5_FD_ROUTE': ('SENTINEL_CREATE', 'LAUNCHER_PROVISION', 'TOOL_PIN', 'POLICY_PROVISION', 'FD_ROUTE'),
    'P6_ANCESTRY_NO_DRIFT': ('ANCESTRY_BEFORE', 'ANCESTRY_AFTER'),
    'P7_CLOSING_CURRENTNESS': ('POLICY_FINAL', 'TOOL_AFTER', 'CLOSING_CURRENT')}
DEADLINE_SECONDS = 300
ROUTE_SECONDS = 10
PROVISION_SECONDS = 60
STREAM_BYTES = 8192
POLICY_STREAM_BYTES = 65536
RECEIPT_BYTES = 524288
FD_CEILING = 32
BWRAP_BYTES = 72160
SOURCE_MODE, OUTPUT_MODE = 0o755, 0o755  # git clone under umask 022; run.py output.mkdir(mode=0o755).


class Refused(Exception):
    pass


def need(value, code):
    if not value:
        raise Refused(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_bytes(path, pin, code):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        info = os.fstat(fd)
        need(stat.S_ISREG(info.st_mode) and info.st_size == pin['bytes'], code + '_SHAPE')
        raw = b''
        while len(raw) <= pin['bytes']:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                break
            raw += chunk
    finally:
        os.close(fd)
    need(len(raw) == pin['bytes'] and sha(raw) == pin['sha256'], code + '_PIN')
    return raw


def load(name, here):
    """Exact pinned module bytes, executed into a fresh module; no sys.path use."""
    path = here / (name + '.py')
    raw = pinned_bytes(path, MODULES[name], 'MODULE_' + name.upper())
    module = types.ModuleType('dg16_placement_' + name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def hosted_context(environ):
    need(environ.get('GITHUB_ACTIONS') == 'true' and environ.get('RUNNER_ENVIRONMENT') == 'github-hosted', 'HOSTED_REQUIRED')
    need(environ.get('GITHUB_REPOSITORY') == REPOSITORY and environ.get('GITHUB_EVENT_NAME') == 'push'
         and environ.get('GITHUB_REF') == 'refs/heads/' + TRIGGER_BRANCH, 'TRIGGER_SCOPE_REQUIRED')
    need(environ.get('GITHUB_RUN_ATTEMPT') == '1', 'FIRST_ATTEMPT_REQUIRED')
    run_id, commit = environ.get('GITHUB_RUN_ID', ''), environ.get('GITHUB_SHA', '')
    need(re.fullmatch('[0-9]{1,20}', run_id) and re.fullmatch('[0-9a-f]{40}', commit), 'RUN_IDENTITY_SHAPE')
    return dict(run_id=run_id, run_attempt=1, branch=TRIGGER_BRANCH, workflow_commit=commit)


def exec_custody(here, run_id):
    """Item 7: the operator runs only from a root-owned 0700 copy of exactly the checked bytes."""
    root = here.parent.parent
    need(str(here) == str(root / EXEC_DIR) and str(root.parent) == EXEC_PARENT
         and root.name == 'dg16-placement-exec-' + run_id + '-a1', 'EXEC_LAYOUT')
    dirs = {}
    for rel in ('.', 'qualification', EXEC_DIR, 'scripts'):
        info = os.lstat(root / rel)
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == info.st_gid == 0 and stat.S_IMODE(info.st_mode) == 0o700,
             'EXEC_DIRECTORY_CUSTODY')
        dirs[rel] = dict(mode=info.st_mode, uid=info.st_uid, gid=info.st_gid)
    parent = os.lstat(root.parent)  # Root-owned parent: no runner-user rename or replacement.
    need(stat.S_ISDIR(parent.st_mode) and parent.st_uid == parent.st_gid == 0 and not parent.st_mode & 0o022,
         'EXEC_PARENT_CUSTODY')
    files = {}
    for rel in EXEC_FILES:
        info = os.lstat(root / rel)
        need(stat.S_ISREG(info.st_mode) and info.st_uid == info.st_gid == 0 and stat.S_IMODE(info.st_mode) == 0o400
             and info.st_nlink == 1, 'EXEC_FILE_CUSTODY')
        with open(root / rel, 'rb') as f:
            raw = f.read(1 << 20)
        files[rel] = dict(bytes=len(raw), sha256=sha(raw), mode=info.st_mode)
    entries = sorted(str(p.relative_to(root)) for p in root.rglob('*'))
    need(entries == sorted(set(EXEC_FILES) | {'qualification', EXEC_DIR, 'scripts'}), 'EXEC_POPULATION')
    for rel, pin in ((EXEC_FILES[1], MODULES['root_placement']), (EXEC_FILES[2], MODULES['access_matrix']), (SETUP['path'], SETUP)):
        need(files[rel]['bytes'] == pin['bytes'] and files[rel]['sha256'] == pin['sha256'], 'EXEC_FILE_PIN')
    return dict(root=str(root), parent=dict(path=EXEC_PARENT, mode=parent.st_mode, uid=parent.st_uid, gid=parent.st_gid),
                directories=dirs, files=files)


def small_text(path, limit=4096):
    try:
        with open(path, 'rb') as f:
            raw = f.read(limit + 1)
    except OSError as exc:
        return dict(readable=False, errno=exc.errno)
    if len(raw) > limit:
        return dict(readable=True, bounded=False, bytes=len(raw))
    return dict(readable=True, bounded=True, bytes=len(raw), sha256=sha(raw), text=raw.decode('utf-8', 'replace'))


def file_fact(path, limit):
    resolved = Path(path).resolve(strict=True)
    fd = os.open(resolved, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        raw = os.read(fd, limit + 1)
        closing = os.fstat(fd)
        xattrs = sorted(os.listxattr(fd))
    finally:
        os.close(fd)
    path_closing = resolved.stat()
    keys = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_uid, s.st_gid, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    return dict(path=str(resolved), bytes=len(raw), sha256=sha(raw), mode=before.st_mode, uid=before.st_uid,
                gid=before.st_gid, device=before.st_dev, inode=before.st_ino, nlink=before.st_nlink, xattrs=xattrs,
                custody_stable=keys(before) == keys(closing) == keys(path_closing), complete=len(raw) <= limit)


def host_facts(environ):
    release = {}
    for line in small_text('/etc/os-release').get('text', '').splitlines():
        key, _, value = line.partition('=')
        if key in ('ID', 'VERSION_ID'):
            release[key] = value.strip('"')
    facts = dict(os_release=release, kernel=os.uname().release, machine=os.uname().machine,
                 image_os=environ.get('ImageOS', ''), image_version=environ.get('ImageVersion', ''),
                 python=list(sys.version_info[:3]), executable=sys.executable)
    for label, path in (('apparmor_enabled', '/sys/module/apparmor/parameters/enabled'),
                        ('apparmor_restrict_unprivileged_userns', '/proc/sys/kernel/apparmor_restrict_unprivileged_userns'),
                        ('max_user_namespaces', '/proc/sys/user/max_user_namespaces'),
                        ('unprivileged_userns_clone', '/proc/sys/kernel/unprivileged_userns_clone'),
                        ('bwrap_apparmor_profile', '/etc/apparmor.d/bwrap-userns-restrict'),
                        ('bwrap_apparmor_extra_profile', '/usr/share/apparmor/extra-profiles/bwrap-userns-restrict'),
                        ('self_confinement', '/proc/self/attr/current')):
        facts[label] = small_text(path, 65536)
    for label, path in (('bwrap_before', '/usr/bin/bwrap'), ('python3_12', '/usr/bin/python3.12')):
        try:
            facts[label] = file_fact(path, 16 * 1024**2)
        except OSError as exc:
            facts[label] = dict(errno=exc.errno)
    return facts


def stream(raw, limit=STREAM_BYTES):
    return dict(bytes=len(raw), sha256=sha(raw), base64=base64.b64encode(raw[:limit]).decode('ascii'),
                complete=len(raw) <= limit)


def child_limits():
    # Same per-child bounds as the ACCESS09 I0 capture.
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (268435456, 268435456))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def bounded_run(command, seconds, monotonic, limit=STREAM_BYTES, **kw):
    row = dict(argv=command, returncode=None, timeout=False, stdout=None, stderr=None, elapsed_ns=None)
    t0 = monotonic()
    try:
        done = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=seconds, close_fds=True, **kw)
    except subprocess.TimeoutExpired as exc:
        row.update(timeout=True, stdout=stream(exc.stdout or b'', limit), stderr=stream(exc.stderr or b'', limit))
        return row, None, None
    finally:
        row['elapsed_ns'] = int((monotonic() - t0) * 1e9)
    row.update(returncode=done.returncode, stdout=stream(done.stdout, limit), stderr=stream(done.stderr, limit))
    return row, done.stdout, done.stderr


def final_line(raw):
    body = raw[:-1] if raw.endswith(b'\n') else raw
    return body.rsplit(b'\n', 1)[-1]


def launcher_provision(exec_root, O, environ, monotonic):
    """If /usr/bin/bwrap is absent, run the pinned V21 provisioner as the core does.

    One single retry, exactly as dg17-structural.yml: only if the first attempt's final
    stderr line is the HTTP 502 line and /usr/bin/bwrap is still absent (no write yet).
    """
    rec = O['launcher_provision'] = dict(before=None, mode=None, setup=None, package=dict(LAUNCHER_PACKAGE),
                                         attempts=[], record=None)
    try:
        info = os.lstat('/usr/bin/bwrap')
    except FileNotFoundError:
        info = None
    rec['before'] = 'ABSENT' if info is None else dict(device=info.st_dev, inode=info.st_ino, mode=info.st_mode,
                                                       uid=info.st_uid, gid=info.st_gid, bytes=info.st_size)
    if info is not None:
        rec['mode'] = 'PREEXISTING_NOT_PROVISIONED'
        return
    rec['mode'] = 'PROVISIONED_BY_MAINTAINED_V21_SETUP'
    path = Path(exec_root) / SETUP['path']
    pinned_bytes(path, SETUP, 'SETUP')
    rec['setup'] = dict(SETUP)
    command = ['/usr/bin/python3.12', '-I', '-S', '-B', str(path), '--provision-hosted-launcher']
    for attempt in (1, 2):
        row, out, err = bounded_run(command, PROVISION_SECONDS, monotonic, env=dict(environ))
        row['attempt'] = attempt
        rec['attempts'].append(row)
        need(not row['timeout'], 'LAUNCHER_PROVISION_TIMEOUT')
        if row['returncode'] == 0:
            break
        retry = (attempt == 1 and final_line(err) == RETRY_LINE and not os.path.lexists('/usr/bin/bwrap'))
        row['retry_eligible'] = retry
        need(retry, 'LAUNCHER_PROVISION_REFUSED')
    need(len(out) <= STREAM_BYTES and err == b'', 'LAUNCHER_PROVISION_REFUSED')
    value = json.loads(out)
    launcher = value.get('launcher', {}) if type(value) is dict else {}
    need(type(value) is dict and value.get('scope') == PROVISION_SCOPE and value.get('target') == '/usr/bin/bwrap'
         and value.get('package') == LAUNCHER_PACKAGE and launcher.get('bytes') == BWRAP_BYTES
         and launcher.get('mode') == '0755' and launcher.get('exclusive_creation') is True
         and launcher.get('opening') == launcher.get('closing'), 'LAUNCHER_PROVISION_RECORD')
    rec['record'] = value


def policy_run(exec_root, O, key, flag, environ, monotonic, code):
    """The core's exact policy argv: /usr/bin/env GITHUB_ACTIONS=true RUNNER_ENVIRONMENT=github-hosted ..."""
    command = ['/usr/bin/env', 'GITHUB_ACTIONS=true', 'RUNNER_ENVIRONMENT=github-hosted', '/usr/bin/python3.12',
               '-I', '-S', '-B', str(Path(exec_root) / SETUP['path']), flag]
    pinned_bytes(Path(exec_root) / SETUP['path'], SETUP, 'SETUP')
    row, out, err = bounded_run(command, PROVISION_SECONDS, monotonic, POLICY_STREAM_BYTES, env=dict(environ))
    row['environment_keys'] = sorted(environ)
    row['record'] = None
    O[key] = row
    need(not row['timeout'] and row['returncode'] == 0 and err == b'' and len(out) <= POLICY_STREAM_BYTES, code)
    row['record'] = json.loads(out)
    return row['record']


def joins(R, root_fd, base_name, base_fd, packet_fd, extra=()):
    """require_current() path/FD closing joins, without receipt or manifest."""
    result = {}
    result['root'] = R.identity(os.stat('/', follow_symlinks=False)) == R.identity(os.fstat(root_fd))
    result['island'] = R.identity(os.stat(base_name, dir_fd=root_fd, follow_symlinks=False)) == R.identity(os.fstat(base_fd))
    result['packet'] = R.identity(os.stat('packet', dir_fd=base_fd, follow_symlinks=False)) == R.identity(os.fstat(packet_fd))
    for name, fd in extra:
        result[name] = R.identity(os.stat(name, dir_fd=base_fd, follow_symlinks=False)) == R.identity(os.fstat(fd))
    need(all(result.values()), 'PATH_FD_JOIN_REFUSED')
    return result


def children():
    found = {}
    for path in sorted(glob.glob('/proc/self/task/*/children')):
        with open(path, 'rb') as f:
            found[path.split('/')[4]] = f.read(4096).decode('ascii', 'replace').split()
    return found


def observe(environ, here, monotonic=time.monotonic):
    started = monotonic()
    receipt = dict(schema=SCHEMA, authority='NONE', original_awards=[], cause='UNPROVED',
                   scope='PLACEMENT_ONLY_FRESH_ROOT_ISLAND_FIXED_SIBLINGS_AND_FD_ROUTE',
                   recorded_subject=dict(SUBJECT), modules={k: dict(v) for k, v in MODULES.items()}, setup=dict(SETUP),
                   context=None, profile=None, host=None, observations={},
                   steps=[dict(step=s, result='NOT_ATTEMPTED', code=None) for s in STEPS],
                   properties={p: 'NOT_OBSERVED' for p in PROPERTIES},
                   cleanup='NONE_DISPOSABLE_RUNNER_NO_RECURSIVE_REMOVAL',
                   bounds=dict(deadline_seconds=DEADLINE_SECONDS, route_seconds=ROUTE_SECONDS,
                               provision_seconds=PROVISION_SECONDS, launcher_attempts_max=2,
                               stream_bytes=STREAM_BYTES, policy_stream_bytes=POLICY_STREAM_BYTES,
                               receipt_bytes=RECEIPT_BYTES, fd_ceiling=FD_CEILING),
                   status='REFUSED', failure=None, elapsed_ns=None)
    O = receipt['observations']
    rows = {r['step']: r for r in receipt['steps']}
    held = []
    state = {}

    def run(name, fn):
        need(monotonic() - started < DEADLINE_SECONDS, 'DEADLINE')
        rows[name]['result'] = 'ATTEMPTED'
        value = fn()
        rows[name]['result'] = 'PASS'
        return value

    try:
        R = load('root_placement', here)
        A = load('access_matrix', here)
        receipt['profile'] = R.PROFILE
        context = run('HOSTED_CONTEXT', lambda: hosted_context(environ))
        receipt['context'] = context
        wanted = R.paths(context)
        packet_path = wanted['packet']
        base_name = packet_path.parent.name
        O['paths'] = {k: str(v) for k, v in wanted.items()}

        def credentials():
            O['credentials'] = R.credentials()
            O['parent_status'] = A.proc_observation()
        run('CREDENTIALS', credentials)
        O['exec'] = run('EXEC_CUSTODY', lambda: exec_custody(here, context['run_id']))
        receipt['host'] = run('HOST_FACTS', lambda: host_facts(environ))

        def root_observe():
            fd = R.open_dir('/'); held.append(fd); state['root_fd'] = fd
            O['root'] = R.observe_fd(fd)
        run('ROOT_OBSERVE', root_observe)

        def island_absent():
            O['island_absent_before'] = R.absent(base_name, state['root_fd'])
            need(O['island_absent_before'], 'ISLAND_NOT_FRESH')
        run('ISLAND_ABSENT_BEFORE', island_absent)

        def island_create():
            os.mkdir(base_name, 0o700, dir_fd=state['root_fd'])  # Exclusive; EEXIST refuses.
            fd = R.open_dir(base_name, state['root_fd']); held.append(fd); state['base_fd'] = fd
            O['island'] = R.observe_fd(fd, 0o700)
        run('ISLAND_CREATE', island_create)

        def packet_create():
            os.mkdir('packet', 0o700, dir_fd=state['base_fd'])
            fd = R.open_dir('packet', state['base_fd']); held.append(fd); state['packet_fd'] = fd
            O['packet'] = R.observe_fd(fd, 0o700)
        run('PACKET_CREATE', packet_create)

        def source_output_absent():
            O['source_output_absent_at_packet'] = dict(
                source=R.absent('source', state['base_fd']), output=R.absent('output', state['base_fd']))
            need(all(O['source_output_absent_at_packet'].values()), 'SOURCE_OUTPUT_MUST_BE_ABSENT')
        run('SOURCE_OUTPUT_ABSENT_AT_PACKET', source_output_absent)

        def bootstrap_closing():
            need(R.observe_fd(state['root_fd']) == O['root'] and R.observe_fd(state['base_fd'], 0o700) == O['island']
                 and R.observe_fd(state['packet_fd'], 0o700) == O['packet'], 'BOOTSTRAP_CLOSING_CUSTODY')
        run('BOOTSTRAP_CLOSING_CUSTODY', bootstrap_closing)

        def packet_files():
            # Maintained write_new (0600 -> fchmod 0400, fsync), a nested 0700 dir, read_file readback.
            R.write_new('probe', PROBE, state['packet_fd'])
            info = os.stat('probe', dir_fd=state['packet_fd'], follow_symlinks=False)
            fd = os.open('probe', os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=state['packet_fd'])
            try:
                xattrs = sorted(os.listxattr(fd))
            finally:
                os.close(fd)
            readback = R.read_file(packet_path / 'probe', 4096)
            need(readback == PROBE, 'PROBE_READBACK')
            os.mkdir('nested', 0o700, dir_fd=state['packet_fd'])
            nfd = R.open_dir('nested', state['packet_fd']); held.append(nfd); state['nested_fd'] = nfd
            O['packet_files'] = dict(
                probe=dict(device=info.st_dev, inode=info.st_ino, mode=info.st_mode, nlink=info.st_nlink, uid=info.st_uid,
                           gid=info.st_gid, bytes=info.st_size, xattrs=xattrs, readback_sha256=sha(readback)),
                nested=R.observe_fd(nfd, 0o700))
        run('PACKET_FILE_CUSTODY', packet_files)

        def sentinel():
            # Diagnostic-only object (absent from the core packet profile): same bytes/mode as ACCESS09 I0.
            fd = os.open('sentinel', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o644,
                         dir_fd=state['packet_fd'])
            try:
                need(os.write(fd, A.SENTINEL) == len(A.SENTINEL), 'SENTINEL_WRITE')
                info = os.fstat(fd)
            finally:
                os.close(fd)
            O['sentinel'] = dict(device=info.st_dev, inode=info.st_ino, mode=info.st_mode, uid=info.st_uid,
                                 gid=info.st_gid, bytes=len(A.SENTINEL), sha256=sha(A.SENTINEL))
        run('SENTINEL_CREATE', sentinel)

        def siblings():
            for name, mode in (('source', SOURCE_MODE), ('output', OUTPUT_MODE)):
                os.mkdir(name, mode, dir_fd=state['base_fd'])
                fd = R.open_dir(name, state['base_fd']); held.append(fd); state[name + '_fd'] = fd
                O[name] = R.observe_fd(fd)  # Live phase: require_current() observes these without a mode.
        run('FIXED_SIBLINGS_CREATE', siblings)

        extra = lambda: (('source', state['source_fd']), ('output', state['output_fd']))

        def current():
            return dict(root=R.observe_fd(state['root_fd']), island=R.observe_fd(state['base_fd'], 0o700),
                        packet=R.observe_fd(state['packet_fd'], 0o700), source=R.observe_fd(state['source_fd']),
                        output=R.observe_fd(state['output_fd']))

        def live_current():
            observed = current()
            need(all(observed[k] == O[k] for k in observed), 'LIVE_OBSERVATION_CHANGED')
            O['live_joins'] = joins(R, state['root_fd'], base_name, state['base_fd'], state['packet_fd'], extra())
        run('LIVE_CURRENT', live_current)

        def ancestry_before():
            state['before'] = A.snapshot(str(packet_path), state['packet_fd'])
            O['ancestry_before'] = state['before']
            A.check_snapshot(A.project_snapshot(state['before']))
        run('ANCESTRY_BEFORE', ancestry_before)

        exec_root = O['exec']['root']
        run('LAUNCHER_PROVISION', lambda: launcher_provision(exec_root, O, environ, monotonic))

        def tool_pin():
            fact = O['launcher'] = file_fact('/usr/bin/bwrap', 16 * 1024**2)
            need(fact.get('path') == '/usr/bin/bwrap' and fact.get('custody_stable') is True
                 and fact.get('bytes') == BWRAP_BYTES and fact.get('sha256') == A.BWRAP_SHA and fact.get('nlink') == 1
                 and fact.get('uid') == 0 and fact.get('gid') == 0 and stat.S_IMODE(fact['mode']) == 0o755
                 and fact.get('xattrs') == [], 'TOOL_PRECONDITION')
            record = O['launcher_provision']['record']
            if record is not None:  # Same-host join: installed object is the one observed and launched.
                closing = record['launcher']['closing']
                need(record['launcher']['sha256'] == A.BWRAP_SHA and closing[:3] == [fact['device'], fact['inode'], fact['mode']]
                     and closing[7:] == [0, 0], 'LAUNCHER_INSTALL_JOIN')
        run('TOOL_PIN', tool_pin)

        def policy_provision():
            value = policy_run(exec_root, O, 'policy_provision', '--provision-hosted-bwrap-policy', environ, monotonic,
                               'POLICY_PROVISION_REFUSED')
            need(type(value) is dict and value.get('scope') == 'EPHEMERAL_CI_BWRAP_POLICY_ONLY_NO_NATIVE_ACCEPTANCE'
                 and value.get('global_state_unchanged') is True, 'POLICY_PROVISION_RECORD')
        run('POLICY_PROVISION', policy_provision)

        def fd_route():
            fd = state['packet_fd']
            command = A.argv('/usr/bin/bwrap', str(packet_path), fd, 'FD')
            count = len(os.listdir('/proc/self/fd'))
            route = O['fd_route'] = dict(argv=command, argv_sha256=sha(A.canonical(command)), target_fd=fd,
                                         diagnostic_fd_count=count, returncode=None, timeout=False,
                                         stdout=None, stderr=None, elapsed_ns=None, payload_valid=False,
                                         child_limits=dict(cpu_seconds=5, address_space_bytes=268435456, core_bytes=0))
            need(count <= FD_CEILING, 'DIAGNOSTIC_FD_BOUND')
            row, out, err = bounded_run(command, ROUTE_SECONDS, monotonic, pass_fds=(fd,), env=A.environment(),
                                        start_new_session=True, preexec_fn=child_limits)
            route.update({k: row[k] for k in ('returncode', 'timeout', 'stdout', 'stderr', 'elapsed_ns')})
            need(not row['timeout'], 'FD_ROUTE_TIMEOUT')
            need(len(out) <= STREAM_BYTES and len(err) <= STREAM_BYTES, 'FD_ROUTE_STREAM_BOUND')
            need(row['returncode'] == 0 and err == b'', 'FD_ROUTE_CHILD_REFUSED')
            payload = json.loads(out)
            need(out == A.canonical(payload), 'PAYLOAD_ENCODING')
            A.validate_payload(payload, dict(route='FD', before=A.project_snapshot(state['before'])))
            route['payload_valid'] = True
        run('FD_ROUTE', fd_route)

        def ancestry_after():
            after = A.snapshot(str(packet_path), state['packet_fd'])
            O['ancestry_after'] = after
            need(A.project_snapshot(after) == A.project_snapshot(state['before']), 'ANCESTRY_DRIFT')
        run('ANCESTRY_AFTER', ancestry_after)

        def policy_final():
            value = policy_run(exec_root, O, 'policy_final', '--finalize-hosted-bwrap-policy', environ, monotonic,
                               'POLICY_FINAL_REFUSED')
            need(type(value) is dict and value.get('status') == 'ACTIVE_POLICY_AND_RECEIPT_RETAINED'
                 and value.get('loaded') == O['policy_provision']['record'].get('loaded'), 'POLICY_FINAL_RECORD')
        run('POLICY_FINAL', policy_final)

        def tool_after():
            O['launcher_after'] = file_fact('/usr/bin/bwrap', 16 * 1024**2)
            need(O['launcher_after'] == O['launcher'], 'TOOL_CHANGED')
            O['children_after'] = children()
            need(all(v == [] for v in O['children_after'].values()), 'CHILDREN_REMAIN')
        run('TOOL_AFTER', tool_after)

        def closing():
            observed = current()
            O['closing'] = observed
            need(all(observed[k] == O[k] for k in observed), 'CLOSING_OBSERVATION_CHANGED')
            O['closing_joins'] = joins(R, state['root_fd'], base_name, state['base_fd'], state['packet_fd'], extra())
        run('CLOSING_CURRENT', closing)
        receipt['status'] = 'COMPLETE'
    except Exception as exc:  # Every refusal is recorded once; nothing is retried except the declared 502 case.
        if isinstance(exc, OSError):
            code = 'OS_' + (errno.errorcode.get(exc.errno, str(exc.errno)) if exc.errno else 'UNKNOWN')
        else:
            first = exc.args[0] if exc.args else None
            code = first if type(first) is str and re.fullmatch('[A-Z0-9_]{1,64}', first) else \
                'UNCLASSIFIED_' + type(exc).__name__[:40].upper()
        receipt['failure'] = code
        for r in receipt['steps']:
            if r['result'] == 'ATTEMPTED':
                r.update(result='REFUSED', code=code)
    finally:
        for fd in reversed(held):
            try:
                os.close(fd)
            except OSError:
                pass
    for prop, steps in PROPERTIES.items():
        receipt['properties'][prop] = 'OBSERVED' if all(rows[s]['result'] == 'PASS' for s in steps) else 'NOT_OBSERVED'
    receipt['elapsed_ns'] = int((monotonic() - started) * 1e9)
    if receipt['status'] == 'COMPLETE' and receipt['elapsed_ns'] > DEADLINE_SECONDS * 10**9:
        receipt.update(status='REFUSED', failure='DEADLINE')
    return receipt


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('ascii')


def transport_lines(files):
    """Numbered <= 4 KiB base64 chunks per member, preceded by one count line."""
    lines = []
    for name in ('RECEIPT.json', 'ARTIFACT_MANIFEST.json'):
        text = base64.b64encode(files[name]).decode('ascii')
        chunks = [text[i:i + CHUNK_CHARS] for i in range(0, len(text), CHUNK_CHARS)] or ['']
        lines.append('%s_COUNT %s %d %d %s' % (MARKER, name, len(chunks), len(files[name]), sha(files[name])))
        lines.extend('%s %s %d/%d %s' % (MARKER, name, i, len(chunks), c) for i, c in enumerate(chunks, 1))
    return lines


def publish(receipt, output):
    raw = encode(receipt)
    if len(raw) > RECEIPT_BYTES:
        receipt = dict(schema=SCHEMA, authority='NONE', original_awards=[], cause='UNPROVED', status='REFUSED',
                       failure='RECEIPT_BOUND', oversize=dict(bytes=len(raw), sha256=sha(raw)))
        raw = encode(receipt)
    files = {'RECEIPT.json': raw}
    files['ARTIFACT_MANIFEST.json'] = encode(dict(schema=MANIFEST_SCHEMA, members=[
        dict(name='RECEIPT.json', bytes=len(raw), sha256=sha(raw))]))
    output = Path(output)
    os.mkdir(output, 0o755)
    public = output / 'public'
    os.mkdir(public, 0o755)
    for name in ('RECEIPT.json', 'ARTIFACT_MANIFEST.json'):
        fd = os.open(public / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o644)
        try:
            data = files[name]
            need(os.write(fd, data) == len(data), 'PUBLIC_WRITE')
            os.fchmod(fd, 0o644)
        finally:
            os.close(fd)
    return files, transport_lines(files)


def main(argv):
    need(len(argv) == 3 and argv[1] == '--output' and os.path.isabs(argv[2]), 'USAGE: diagnose.py --output ABSOLUTE_NEW_DIR')
    receipt = observe(dict(os.environ), Path(os.path.abspath(__file__)).parent)
    files, lines = publish(receipt, argv[2])
    out = sys.stdout
    for line in lines:
        out.write(line + '\n')
    out.write(MARKER + '_SUMMARY status=' + receipt['status'] + ' failure=' + str(receipt.get('failure'))
              + ' receipt_sha256=' + sha(files['RECEIPT.json']) + ' receipt_bytes=' + str(len(files['RECEIPT.json'])) + '\n')
    out.flush()
    return 0 if receipt['status'] == 'COMPLETE' else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
