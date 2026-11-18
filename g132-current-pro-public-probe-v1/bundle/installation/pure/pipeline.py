# Exact bounded source projection; source module is never imported.
def need(ok, code):
    if not ok:
        raise ValueError(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def desc(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}

def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')

def parse(raw):
    def pairs(rows):
        result = {}
        for name, value in rows:
            need(name not in result, 'DUPLICATE_KEY')
            result[name] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'NONFINITE'))

def exact_path(path):
    path = Path(path)
    need(path.is_absolute() and path.is_relative_to(BASE)
         and path.resolve(strict=True) == path, 'CANONICAL_ROOT_PATH')
    return path

def read(path, maximum=4*1024**2, pin=None):
    path = exact_path(path)
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
         and before.st_uid == os.geteuid()
         and stat.S_IMODE(before.st_mode) in (0o400, 0o444, 0o600)
         and 0 < before.st_size <= maximum, 'OWNED_BOUNDED_INPUT')
    mark = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_uid,
                      s.st_gid, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        need(mark(os.fstat(fd)) == mark(before) and not os.listxattr(fd), 'INPUT_OPEN_CHANGED')
        raw = os.pread(fd, before.st_size+1, 0)
        need(len(raw) == before.st_size and mark(os.fstat(fd)) == mark(before)
             == mark(path.lstat()) and path.resolve(strict=True) == path,
             'INPUT_CLOSING_CHANGED')
    finally:
        os.close(fd)
    need(pin is None or sha(raw) == pin, 'ROOT_SELECTED_INPUT_HASH')
    return raw

def row(path, pin=None, maximum=4*1024**2):
    path = Path(path)
    raw = read(path, maximum, pin)
    return {'path': str(path), 'sha256': sha(raw)}

def current(operation, now):
    need(type(now) is int and type(operation['issued_unix_ms']) is int
         and type(operation['expires_unix_ms']) is int
         and operation['issued_unix_ms'] <= now < operation['expires_unix_ms']
         <= operation['issued_unix_ms'] + 600000, 'ORIGINAL_OPERATION_EXPIRED')

def fresh_path(path):
    path = Path(path)
    parent = exact_path(path.parent)
    st = parent.stat()
    need(stat.S_ISDIR(st.st_mode) and st.st_uid == os.geteuid()
         and stat.S_IMODE(st.st_mode) == 0o700 and not os.path.lexists(path),
         'FRESH_PRIVATE_OUTPUT')
    return path

def write_file(path, raw):
    path = fresh_path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            count = os.write(fd, raw[offset:])
            need(count > 0, 'OUTPUT_WRITE_PROGRESS')
            offset += count
        os.fsync(fd)
    finally:
        os.close(fd)
    need(read(path, max(1, len(raw))) == raw, 'OUTPUT_READBACK')
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

def episode_inputs(episode):
    episode = exact_path(episode)
    assembled = episode/'assembled'
    manifest_raw = read(assembled/'ROOT_SENDER_INSTALL_MANIFEST.json')
    manifest = parse(manifest_raw)
    entry_path = assembled/'root_sender_entry.py'
    entry_raw = read(entry_path, 1024**2)
    need(manifest['members']['root_sender_entry.py'] == desc(entry_raw), 'SENDER_ENTRY_INSTALL_JOIN')
    op_path = assembled/'packet/carrier/PRO_SENDER_OPERATION.json'
    op_raw = read(op_path, 65536)
    need(manifest['members']['packet/carrier/PRO_SENDER_OPERATION.json'] == desc(op_raw), 'SENDER_OPERATION_INSTALL_JOIN')
    op = parse(op_raw)
    current(op, time.time_ns()//1000000)
    return assembled, entry_path, entry_raw, op_path, op, manifest_raw

def dispatcher_selection(args):
    assembled, entry, _, operation_path, _, _ = episode_inputs(args.episode)
    receipt = row(args.late_receiving, args.late_receiving_sha256)
    helper_parent = fresh_path(args.install)
    # Binder creates this final directory directly: no post-bind relocation.
    selection = dict(entry_path=str(entry), operation_path=str(operation_path),
                     helper_path=str(helper_parent/'dispatcher_entry.py'),
                     python_path='/usr/bin/python3', late_sender_receiving_path=receipt['path'])
    raw = encode(selection)
    write_file(args.output, raw)
    return {'authority': 'NONE', 'selection': row(args.output),
            'Root_late_receiving': receipt, 'binder_output': str(helper_parent),
            'sender_started': False, 'actual_admission': False}
