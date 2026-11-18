# Exact bounded source projection; source module is never imported.
MAX_FILES = 128

MAX_FILE_BYTES = 16 * 1024**2

MAX_TOTAL_BYTES = 64 * 1024**2

CORE_FILES = {'HOST_COMPOSITION.json', 'host_composition.py', 'run.py', 'root_placement.py',
 'natural_inputs.py', 'NATIVE_SOURCE_APPLICABILITY.json', 'ADVERSE_APPLICABILITY.json',
 'ORIGINAL_SCOPE.json', 'PROVIDER_SETUP.json', 'SOURCE_MANIFEST.json', 'operation.py',
 'native_probe.py', 'native_prerequisite.py', 'evidence_io.py', 'host_utility.py',
 'input_setup.py', 'source_store.py', 'provider_layout.py', 'nss_configuration.py', 'g3_receiving.py', 'proof_consumer.py', 'INDEPENDENT_PROOF_PINS.json'}

RETAINED_M4_FILES = {'retained-m4/M4_FINAL_CHECK.json', 'retained-m4/M4_INDEPENDENT_REPORT.md', 'retained-m4/M4_INDEPENDENT_RESULT.json', 'retained-m4/M4_ROOT_RECEIVING.json'}

def need(value, code):
    if not value:
        raise ValueError(code)

def parse(raw):
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'DUPLICATE_KEY')
            result[k] = v
        return result
    return json.loads(raw.decode('utf8'), object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'NONFINITE_JSON'))

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
    need(type(members) is dict and len(CORE_FILES) < len(members) <= MAX_FILES
         and RETAINED_M4_FILES <= set(members),
         'PUBLIC_MANIFEST_POPULATION')
    need({n for n in members if '/' not in n} == CORE_FILES
         and any(n.startswith('carrier/') for n in members), 'PUBLIC_MANIFEST_CORE_CARRIER_REQUIRED')
    total = 0
    for name, row in members.items():
        path = PurePosixPath(name)
        need(str(path) == name and not path.is_absolute() and '..' not in path.parts
             and 0 < len(path.parts) <= 4 and all(re.fullmatch('[A-Za-z0-9_.-]{1,128}', p) for p in path.parts)
             and (name in CORE_FILES or name in RETAINED_M4_FILES
                  or (path.parts[0] == 'carrier' and len(path.parts) > 1)), 'PUBLIC_MEMBER_PATH')
        need(type(row) is dict and set(row) == {'bytes', 'sha256', 'mode'}
             and type(row['bytes']) is int and 0 <= row['bytes'] <= MAX_FILE_BYTES
             and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256'])
             and type(row['mode']) is int and row['mode'] == 0o400, 'PUBLIC_MEMBER_DESCRIPTOR')
        total += row['bytes']
    need(total <= MAX_TOTAL_BYTES, 'PUBLIC_TOTAL_BOUND')
    return members
