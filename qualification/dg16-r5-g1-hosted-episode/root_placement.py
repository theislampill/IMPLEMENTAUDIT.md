"""Fixed fresh root-island bootstrap. No CLI, native calls or path override.

The reviewed external wrapper pins the bootstrap admission and complete public
manifest. These functions do not grant an effect. Failure leaves owned partial
objects for explicit receiving; no recursive cleanup or ancestor repair occurs.
"""
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

SOURCE = 'c29d617a6f39a25e422e40b697bef35938e7a73c'
TREE = 'd690248f5cac8db10e564c23159b50d90dae40d0'
RECEIPT = 'ROOT_PLACEMENT_RECEIPT.json'
PUBLIC_MANIFEST = 'PUBLIC_PACKET_MANIFEST.json'
PROFILE = 'FRESH_ROOT_ISLAND_FIXED_SIBLINGS_V1'
MAX_FILES = 128
MAX_FILE_BYTES = 16 * 1024**2
MAX_TOTAL_BYTES = 64 * 1024**2
CORE_FILES = {'HOST_COMPOSITION.json', 'host_composition.py', 'run.py', 'root_placement.py',
 'natural_inputs.py', 'NATIVE_SOURCE_APPLICABILITY.json', 'ADVERSE_APPLICABILITY.json',
 'ORIGINAL_SCOPE.json', 'PROVIDER_SETUP.json', 'SOURCE_MANIFEST.json', 'operation.py',
 'native_probe.py', 'native_prerequisite.py', 'evidence_io.py', 'host_utility.py',
 'input_setup.py', 'source_store.py', 'provider_layout.py', 'nss_configuration.py', 'g3_receiving.py', 'proof_consumer.py', 'INDEPENDENT_PROOF_PINS.json'}


def need(value, code):
    if not value:
        raise ValueError(code)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def parse(raw):
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'DUPLICATE_KEY')
            result[k] = v
        return result
    return json.loads(raw.decode('utf8'), object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'NONFINITE_JSON'))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def paths(context):
    need(type(context) is dict and type(context.get('run_id')) is str
         and re.fullmatch('[0-9]{1,20}', context['run_id'])
         and type(context.get('run_attempt')) is int and context['run_attempt'] == 1
         and type(context.get('branch')) is str and 0 < len(context['branch']) <= 256
         and type(context.get('workflow_commit')) is str and re.fullmatch('[0-9a-f]{40}', context['workflow_commit']),
         'FIXED_ROOT_CONTEXT')
    base = Path('/dg16-g1-' + context['run_id'])
    return dict(source=base / 'source', private_output=base / 'output', packet=base / 'packet')


def credentials():
    result = [os.getuid(), os.geteuid(), os.getgid(), os.getegid()]
    need(result == [0, 0, 0, 0], 'ROOT_CREDENTIALS_REQUIRED')
    return result


def identity(info):
    return dict(device=info.st_dev, inode=info.st_ino, mode=info.st_mode,
                uid=info.st_uid, gid=info.st_gid)


def observe_fd(fd, mode=None):
    before = os.fstat(fd)
    need(stat.S_ISDIR(before.st_mode) and before.st_uid == before.st_gid == 0
         and not (stat.S_IMODE(before.st_mode) & 0o022)
         and (mode is None or stat.S_IMODE(before.st_mode) == mode), 'DIRECTORY_CUSTODY')
    acls = []
    for attribute in ('system.posix_acl_access', 'system.posix_acl_default'):
        try:
            os.getxattr(fd, attribute)
        except OSError as exc:
            need(exc.errno == errno.ENODATA, 'ACL_ABSENCE_NOT_OBSERVED')
            acls.append(dict(attribute=attribute, result='ABSENT', errno=exc.errno))
        else:
            need(False, 'ACL_PRESENT')
    need(identity(os.fstat(fd)) == identity(before), 'DIRECTORY_CHANGED')
    return dict(identity=identity(before), acls=acls)


def open_dir(name, parent=None):
    return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent)


def file_stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_uid, info.st_gid, info.st_mtime_ns, info.st_ctime_ns)


def read_file(path, maximum):
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
         and 0 <= before.st_size <= maximum, 'ORDINARY_PUBLIC_BODY_REQUIRED')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        need(file_stamp(os.fstat(fd)) == file_stamp(before) and not os.listxattr(fd), 'PUBLIC_BODY_OPEN_CHANGED')
        raw = b''
        while len(raw) <= maximum:
            chunk = os.read(fd, min(1024**2, maximum + 1 - len(raw)))
            if not chunk:
                break
            raw += chunk
        need(len(raw) == before.st_size and file_stamp(os.fstat(fd)) == file_stamp(before) and file_stamp(path.lstat()) == file_stamp(before),
             'PUBLIC_BODY_CLOSING_CHANGED')
        return raw
    finally:
        os.close(fd)


def manifest(raw):
    need(type(raw) is bytes and len(raw) <= 128 * 1024, 'PUBLIC_MANIFEST_BOUND')
    value = parse(raw)
    need(type(value) is dict and set(value) == {'schema', 'members'}
         and value['schema'] == 'dg16.fixed-root-public-manifest.v1', 'PUBLIC_MANIFEST_SCHEMA')
    members = value['members']
    need(type(members) is dict and len(CORE_FILES) < len(members) <= MAX_FILES,
         'PUBLIC_MANIFEST_POPULATION')
    need({n for n in members if '/' not in n} == CORE_FILES
         and any(n.startswith('carrier/') for n in members), 'PUBLIC_MANIFEST_CORE_CARRIER_REQUIRED')
    total = 0
    for name, row in members.items():
        path = PurePosixPath(name)
        need(str(path) == name and not path.is_absolute() and '..' not in path.parts
             and 0 < len(path.parts) <= 4 and all(re.fullmatch('[A-Za-z0-9_.-]{1,128}', p) for p in path.parts)
             and (name in CORE_FILES or (path.parts[0] == 'carrier' and len(path.parts) > 1)), 'PUBLIC_MEMBER_PATH')
        need(type(row) is dict and set(row) == {'bytes', 'sha256', 'mode'}
             and type(row['bytes']) is int and 0 <= row['bytes'] <= MAX_FILE_BYTES
             and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256'])
             and type(row['mode']) is int and row['mode'] == 0o400, 'PUBLIC_MEMBER_DESCRIPTOR')
        total += row['bytes']
    need(total <= MAX_TOTAL_BYTES, 'PUBLIC_TOTAL_BOUND')
    return members


def absent(name, parent):
    try:
        os.stat(name, dir_fd=parent, follow_symlinks=False)
    except FileNotFoundError:
        return True
    return False


def write_new(name, raw, parent):
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                 0o600, dir_fd=parent)
    try:
        count = 0
        while count < len(raw):
            n = os.write(fd, raw[count:])
            need(n > 0, 'WRITE_PROGRESS')
            count += n
        os.fchmod(fd, 0o400)  # Only this newly created owned file.
        os.fsync(fd)
    finally:
        os.close(fd)


def bootstrap(context, public_manifest_raw, admission_raw, expected_admission_sha256):
    """Called only by the final independently reviewed and root-admitted wrapper.

    The expected digest is a wrapper literal, never an environment-selected value.
    Source staging is this module's directory; only exact manifest bodies are copied.
    """
    credentials()
    wanted = paths(context)
    need(type(expected_admission_sha256) is str and re.fullmatch('[0-9a-f]{64}', expected_admission_sha256)
         and type(admission_raw) is bytes and len(admission_raw) <= 16384
         and sha(admission_raw) == expected_admission_sha256, 'BOOTSTRAP_ADMISSION_PIN')
    admission = parse(admission_raw)
    need(type(admission) is dict and set(admission) == {'schema', 'issuer', 'operation', 'source_commit',
         'source_tree', 'workflow_branch', 'run_attempt', 'automatic_retry', 'original_awards', 'manifest_sha256'}
         and type(admission['run_attempt']) is int and admission['automatic_retry'] is False
         and admission == dict(schema='dg16.fixed-root-bootstrap-admission.v1', issuer='R5_ROOT_GOVERNOR',
             operation='CREATE_EXCLUSIVE_ROOT_ISLAND_AND_EXACT_PUBLIC_PACKET_ONLY', source_commit=SOURCE,
             source_tree=TREE, workflow_branch=context['branch'], run_attempt=1, automatic_retry=False,
             original_awards=[], manifest_sha256=sha(public_manifest_raw)), 'BOOTSTRAP_ADMISSION_SCOPE')
    members = manifest(public_manifest_raw)
    staging = Path(__file__).absolute().parent
    bodies = {}
    for name, row in sorted(members.items()):
        p = staging / name
        # Reject aliases at every staging ancestor, including carrier directories.
        for ancestor in p.parents:
            need(stat.S_ISDIR(ancestor.lstat().st_mode), 'STAGING_ANCESTOR_ALIAS')
        raw = read_file(p, MAX_FILE_BYTES)
        need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'PUBLIC_BODY_PIN')
        bodies[name] = raw
    held = []
    try:
        root_fd = open_dir('/'); held.append(root_fd)
        root = observe_fd(root_fd)
        base_name = wanted['packet'].parent.name
        os.mkdir(base_name, 0o700, dir_fd=root_fd)  # Exclusive; existing path always refuses.
        base_fd = open_dir(base_name, root_fd); held.append(base_fd)
        base = observe_fd(base_fd, 0o700)
        os.mkdir('packet', 0o700, dir_fd=base_fd)
        packet_fd = open_dir('packet', base_fd); held.append(packet_fd)
        packet = observe_fd(packet_fd, 0o700)
        directories = {'': packet_fd}
        for name, raw in bodies.items():
            parts = name.split('/')
            parent = ''
            for part in parts[:-1]:
                child = parent + '/' + part if parent else part
                if child not in directories:
                    os.mkdir(part, 0o700, dir_fd=directories[parent])
                    fd = open_dir(part, directories[parent]); held.append(fd)
                    observe_fd(fd, 0o700); directories[child] = fd
                parent = child
            write_new(parts[-1], raw, directories[parent])
        need(absent('source', base_fd) and absent('output', base_fd), 'SOURCE_OUTPUT_MUST_BE_ABSENT')
        need(observe_fd(root_fd) == root and observe_fd(base_fd, 0o700) == base
             and observe_fd(packet_fd, 0o700) == packet, 'BOOTSTRAP_CLOSING_CUSTODY')
        receipt = dict(schema='dg16.fixed-root-placement-runtime.v1', profile=PROFILE,
            context={k: context[k] for k in ('run_id', 'run_attempt', 'branch', 'workflow_commit')},
            credentials=[0, 0, 0, 0], root=root, island=base, packet=packet,
            manifest_sha256=sha(public_manifest_raw), bootstrap_admission_sha256=expected_admission_sha256,
            source_output_at_creation='ABSENT', original_awards=[], cause='UNPROVED')
        # Exact destination readback, before emitting successful receipt.
        for name, raw in bodies.items():
            need(read_file(wanted['packet'] / name, MAX_FILE_BYTES) == raw, 'PUBLIC_INSTALL_READBACK')
        write_new(PUBLIC_MANIFEST, public_manifest_raw, base_fd)
        write_new(RECEIPT, encode(receipt), base_fd)
        need(read_file(wanted['packet'].parent / RECEIPT, 16384) == encode(receipt), 'RECEIPT_READBACK')
        need(require_current(context, wanted['packet'], phase='pre_prepare')['receipt'] == receipt,
             'BOOTSTRAP_FINAL_CURRENT_JOIN')
        return receipt
    finally:
        for fd in reversed(held):
            os.close(fd)


def public_current(packet, receipt):
    """Exact public census; carrier alone owns the separate private body census."""
    path = packet.parent / PUBLIC_MANIFEST
    info = path.lstat()
    need(info.st_uid == info.st_gid == 0 and stat.S_IMODE(info.st_mode) == 0o400,
         'RUNTIME_MANIFEST_CUSTODY')
    raw = read_file(path, 128 * 1024)
    need(sha(raw) == receipt['manifest_sha256'], 'RUNTIME_MANIFEST_BINDING')
    members = manifest(raw)
    expected_dirs = {'.'}
    for name in members:
        expected_dirs.update(str(p) for p in PurePosixPath(name).parents if str(p) != '.')
    seen_files, seen_dirs, pending = set(), set(), [packet]
    count = 0
    while pending:
        here = pending.pop()
        relative = here.relative_to(packet).as_posix()
        need(relative in expected_dirs, 'PUBLIC_DIRECTORY_POPULATION')
        fd = open_dir(here)
        try:
            observed = observe_fd(fd, 0o700)
            need(identity(here.lstat()) == observed['identity'], 'PUBLIC_DIRECTORY_CHANGED')
        finally:
            os.close(fd)
        seen_dirs.add(relative)
        for child in here.iterdir():
            count += 1
            need(count <= MAX_FILES * 4 + 1, 'PUBLIC_ENTRY_BOUND')
            name = child.relative_to(packet).as_posix()
            if name == 'private-inputs':
                # Exact fixed separate private island; carrier checks all bodies.
                fd = open_dir(child)
                try:
                    observed = observe_fd(fd, 0o700)
                    need(identity(child.lstat()) == observed['identity'], 'PRIVATE_INPUT_DIRECTORY_CHANGED')
                finally:
                    os.close(fd)
                continue
            info = child.lstat()
            if stat.S_ISDIR(info.st_mode):
                pending.append(child)
            else:
                need(name in members and info.st_uid == info.st_gid == 0
                     and stat.S_IMODE(info.st_mode) == 0o400, 'PUBLIC_FILE_POPULATION_CUSTODY')
                body = read_file(child, MAX_FILE_BYTES)
                need(len(body) == members[name]['bytes'] and sha(body) == members[name]['sha256'],
                     'PUBLIC_CURRENT_BODY_CHANGED')
                seen_files.add(name)
    need(seen_files == set(members) and seen_dirs == expected_dirs, 'PUBLIC_CENSUS_INCOMPLETE')
    return dict(manifest_sha256=sha(raw), public_files=len(seen_files), public_directories=len(seen_dirs))


def require_current(context, packet, *, phase='live'):
    """Reobserve physical custody; a copied JSON receipt alone cannot satisfy it."""
    credentials()
    wanted = paths(context)
    need(packet == wanted['packet'] and phase in ('pre_prepare', 'live'), 'FIXED_PACKET_REQUIRED')
    held = []
    try:
        root_fd = open_dir('/'); held.append(root_fd)
        base_fd = open_dir(packet.parent.name, root_fd); held.append(base_fd)
        packet_fd = open_dir('packet', base_fd); held.append(packet_fd)
        observations = dict(root=observe_fd(root_fd), island=observe_fd(base_fd, 0o700),
                            packet=observe_fd(packet_fd, 0o700))
        receipt_path = packet.parent / RECEIPT
        info = receipt_path.lstat()
        need(info.st_uid == info.st_gid == 0 and stat.S_IMODE(info.st_mode) == 0o400, 'RUNTIME_RECEIPT_CUSTODY')
        receipt = parse(read_file(receipt_path, 16384))
        need(type(receipt) is dict and set(receipt) == {'schema', 'profile', 'context', 'credentials', 'root',
             'island', 'packet', 'manifest_sha256', 'bootstrap_admission_sha256', 'source_output_at_creation',
             'original_awards', 'cause'} and receipt['schema'] == 'dg16.fixed-root-placement-runtime.v1'
             and receipt['profile'] == PROFILE and receipt['context'] == {k: context[k] for k in
                 ('run_id', 'run_attempt', 'branch', 'workflow_commit')}
             and receipt['credentials'] == [0, 0, 0, 0] and receipt['source_output_at_creation'] == 'ABSENT'
             and receipt['original_awards'] == [] and receipt['cause'] == 'UNPROVED'
             and all(type(receipt[k]) is str and re.fullmatch('[0-9a-f]{64}', receipt[k]) for k in
                 ('manifest_sha256', 'bootstrap_admission_sha256'))
             and all(receipt[k] == observations[k] for k in observations), 'RUNTIME_RECEIPT_BINDING')
        public_current(packet, receipt)
        if phase == 'pre_prepare':
            need(absent('source', base_fd) and absent('output', base_fd), 'SOURCE_OUTPUT_MUST_BE_ABSENT')
        else:
            for name in ('source', 'output'):
                fd = open_dir(name, base_fd); held.append(fd)
                observations[name] = observe_fd(fd)
                need(identity(os.stat(name, dir_fd=base_fd, follow_symlinks=False)) == identity(os.fstat(fd)),
                     'RUNTIME_CHILD_REPLACED')
        # Path/FD closing joins do not rely on directory timestamps or a sampled process census.
        for name, fd in (('/', root_fd), (packet.parent.name, base_fd)):
            target = os.stat(name, dir_fd=None if name == '/' else root_fd, follow_symlinks=False)
            need(identity(target) == identity(os.fstat(fd)), 'RUNTIME_PARENT_REPLACED')
        need(identity(os.stat('packet', dir_fd=base_fd, follow_symlinks=False)) == identity(os.fstat(packet_fd)),
             'RUNTIME_PACKET_REPLACED')
        return dict(receipt=receipt, observations=observations)
    finally:
        for fd in reversed(held):
            os.close(fd)
