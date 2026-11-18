#!/usr/bin/env python3
"""Bounded Linux transport support for the Pro operator; no network or MCP API.

This is an operator journal and physical I/O helper, never a native-event,
currentness, admission, encryption, or original-G1/G3 authority. Source callers
must separately receive its exact bytes and supply live model-side capabilities.
"""
import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import selectors
import signal
import stat
import subprocess
import sys
import time

MAX_FRAME = 4 * 1024 * 1024
MAX_RECORD = 65536
MAX_JOURNAL = 8 * 1024 * 1024
MAX_STEPS = 128
CHUNK = 8192
DISPATCH_ACTIONS = {'initialize', 'ready', 'reserve', 'chunk', 'complete', 'publish', 'finish'}


class Refusal(Exception):
    pass


def need(value, code):
    if not value:
        raise Refusal(code)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def parse(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, 'DUPLICATE_KEY')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _value: need(False, 'NONFINITE'))


def descriptor(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def mark(value):
    # Inodes and nanosecond timestamps can exceed JavaScript's exact integer range.
    return [str(item) for item in (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_uid, value.st_gid, value.st_size, value.st_mtime_ns, value.st_ctime_ns)]


def absolute(value):
    need(isinstance(value, str) and value.startswith('/') and '\x00' not in value,
         'ABSOLUTE_PATH_REQUIRED')
    path = Path(value)
    need(str(path) == value and '..' not in path.parts and path.resolve(strict=True) == path,
         'CANONICAL_NONALIAS_PATH_REQUIRED')
    for parent in reversed(path.parents):
        info = parent.lstat()
        need(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode), 'ANCESTOR_ALIAS')
    return path


def read_owned(value, maximum, *, pin=None, source=False, mode=None):
    path = absolute(value)
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
         and before.st_uid == os.geteuid() and 0 <= before.st_size <= maximum,
         'OWNED_ORDINARY_BOUNDED_FILE')
    if source:
        need(stat.S_IMODE(before.st_mode) in (0o400, 0o444), 'RECEIVED_READONLY_SOURCE_REQUIRED')
    if mode is not None:
        need(stat.S_IMODE(before.st_mode) == mode, 'EXACT_PRIVATE_FILE_MODE')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        need(mark(os.fstat(fd)) == mark(before) and not os.listxattr(fd), 'FILE_OPEN_CHANGED')
        raw = os.pread(fd, maximum + 1, 0)
        need(len(raw) == before.st_size and mark(os.fstat(fd)) == mark(before)
             and mark(path.lstat()) == mark(before), 'FILE_READ_CHANGED')
    finally:
        os.close(fd)
    if pin is not None:
        need(descriptor(raw) == pin, 'EXACT_SOURCE_OR_DATA_PIN')
    return raw, mark(before)


def directory(value):
    path = absolute(value)
    info = path.lstat()
    need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid()
         and stat.S_IMODE(info.st_mode) == 0o700 and not os.listxattr(path), 'OWNED_PRIVATE_DIRECTORY')
    return path, mark(info)


def identity(root):
    path, root_mark = directory(root)
    exe = Path(sys.executable).resolve(strict=True)
    executable = exe.stat()
    # These are current kernel/process facts, not a model/session identity.
    stable = {'platform': sys.platform, 'uid': os.getuid(), 'euid': os.geteuid(),
              'gid': os.getgid(), 'egid': os.getegid(), 'python_path': str(exe),
              'python_identity': mark(executable),
              'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
              'journal_root': str(path), 'journal_root_identity': [root_mark[i] for i in (0, 1, 2, 4, 5)]}
    return {'stable': stable, 'process': {'pid': os.getpid(), 'ppid': os.getppid(),
            'start_ticks': Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19]},
            'authority': 'NONE', 'native_model_identity': 'NOT_OBSERVED'}


def write_once(folder, name, raw):
    need(len(raw) <= MAX_RECORD, 'RECORD_BOUND')
    target = folder / name
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            count = os.write(fd, raw[offset:])
            need(count > 0, 'WRITE_PROGRESS')
            offset += count
        os.fsync(fd)
    finally:
        os.close(fd)
    dfd = os.open(folder, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)
    need(read_owned(str(target), MAX_RECORD)[0] == raw, 'DURABLE_READBACK')
    return descriptor(raw)


def journal(action, value):
    root, _ = directory(value['root'])
    key = value['key']
    need(isinstance(key, str) and re.fullmatch('[0-9a-f]{64}', key), 'SUBJECT_KEY')
    folder = root / key
    if action == 'open':
        need(identity(str(root))['stable'] == value['host_identity'], 'HOST_IDENTITY_CHANGED')
        need(type(value['max_steps']) is int and 1 <= value['max_steps'] <= MAX_STEPS, 'STEP_BOUND')
        # Subject key is independent of actor, nonce, deadline and callback labels.
        need(hashlib.sha256(value['subject_json'].encode()).hexdigest() == key, 'SUBJECT_KEY_BINDING')
        parse(value['subject_json'])
        folder.mkdir(mode=0o700, exist_ok=False)
        write_once(folder, 'START.json', encode(value))
        write_once(folder, 'LOCK', b'')
    directory(str(folder))
    lock = os.open(folder / 'LOCK', os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        start = parse(read_owned(str(folder / 'START.json'), MAX_RECORD)[0])
        need(start['key'] == key and identity(str(root))['stable'] == start['host_identity'], 'SESSION_HOST_CHANGED')
        files = {}
        for member in folder.iterdir():
            need(member.name in {'START.json', 'LOCK', 'FINISH.json', 'UNKNOWN.json'}
                 or re.fullmatch(r'[0-9]{3}\.(INTENT|RESULT)\.json', member.name), 'JOURNAL_UNKNOWN_MEMBER')
            raw, _ = read_owned(str(member), MAX_RECORD)
            need(stat.S_IMODE(member.stat().st_mode) == 0o600, 'JOURNAL_MODE')
            files[member.name] = raw
        need(len(files) <= 2 * MAX_STEPS + 4 and sum(map(len, files.values())) <= MAX_JOURNAL, 'JOURNAL_RESOURCE_BOUND')
        if action == 'open':
            return {'status': 'OPENED_ONCE', 'key': key, 'identity': identity(str(root)),
                    'start': descriptor(files['START.json'])}
        need('FINISH.json' not in files and 'UNKNOWN.json' not in files, 'SPENT_SUBJECT_NO_REPLAY')
        if action == 'unknown':
            return {'status': 'UNKNOWN_NO_REPLAY', 'record': write_once(folder, 'UNKNOWN.json', encode(value))}
        index = value['index']
        need(type(index) is int and 0 <= index <= start['max_steps'], 'ORDINAL_BOUND')
        for prior in range(index):
            need(f'{prior:03d}.INTENT.json' in files and f'{prior:03d}.RESULT.json' in files, 'PREVIOUS_STEP_UNSETTLED')
        need(not any(name[:3].isdigit() and int(name[:3]) > index for name in files), 'OUT_OF_ORDER')
        if action == 'reserve':
            need(index < start['max_steps'] and time.time_ns() // 1000000 < start['expires_ms'], 'EXPIRED_OR_STEP_BOUND')
            name = f'{index:03d}.INTENT.json'
            return {'status': 'RESERVED_ONCE', 'index': index, 'record': write_once(folder, name, encode(value))}
        if action == 'complete':
            intent_name = f'{index:03d}.INTENT.json'
            need(intent_name in files and descriptor(files[intent_name]) == value['intent'], 'EXACT_INTENT_REQUIRED')
            return {'status': 'RETURN_RECORDED', 'index': index,
                    'record': write_once(folder, f'{index:03d}.RESULT.json', encode(value))}
        need(action == 'finish' and not any(name.startswith(f'{index:03d}.') for name in files), 'PENDING_STEP_AT_TERMINAL')
        need(time.time_ns() // 1000000 < start['expires_ms'], 'TERMINAL_AFTER_DEADLINE')
        return {'status': 'TERMINAL_RECORDED', 'record': write_once(folder, 'FINISH.json', encode(value))}
    finally:
        os.close(lock)


def read_chunk(value):
    root, _ = directory(value['exchange_root'])
    path = absolute(value['path'])
    need(path.is_relative_to(root), 'EXCHANGE_PATH_ESCAPE')
    raw, physical = read_owned(str(path), MAX_FRAME, pin=value['descriptor'], mode=0o600)
    offset, count = value['offset'], value['count']
    need(type(offset) is int and type(count) is int and 0 <= offset < len(raw) and 1 <= count <= CHUNK, 'CHUNK_BOUND')
    need(time.time_ns() // 1000000 < value['deadline_ms'], 'ORIGINAL_FRAME_EXPIRED')
    part = raw[offset:offset + count]
    return {'offset': offset, 'count': len(part), 'total_bytes': len(raw),
            'whole_file_sha256': descriptor(raw)['sha256'], 'physical': physical,
            'chunk_base64': base64.b64encode(part).decode('ascii')}


def read_intent(value):
    root, _ = directory(value['exchange_root'])
    path = absolute(value['path'])
    need(path.is_relative_to(root), 'EXCHANGE_PATH_ESCAPE')
    raw, physical = read_owned(str(path), MAX_RECORD, mode=0o600)
    need(descriptor(raw)['sha256'] == value['sha256'], 'DURABLE_INTENT_PIN')
    need(time.time_ns() // 1000000 < value['deadline_ms'], 'ORIGINAL_FRAME_EXPIRED')
    return {'intent': parse(raw), 'physical': physical, 'descriptor': descriptor(raw)}


def invoke(value):
    """Only the existing dispatcher command grammar, in a pinned local process."""
    source = value['source']
    raw, physical = read_owned(source['path'], 1024 * 1024, pin=source['descriptor'], source=True)
    args = value['args']
    need(type(args) is list and 1 <= len(args) <= 8 and args[0] in DISPATCH_ACTIONS
         and all(isinstance(item, str) and '\x00' not in item and len(item) <= 65536 for item in args), 'DISPATCH_COMMAND_GRAMMAR')
    left = (value['deadline_ms'] - time.time_ns() // 1000000) / 1000
    need(0 < left <= 600, 'DISPATCH_DEADLINE')
    loader = "import hashlib,json,os,pathlib,stat,sys; p=pathlib.Path(sys.argv[1]); mark=lambda s:[str(v) for v in (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)]; expected=json.loads(sys.argv[3]); assert p.resolve(strict=True)==p and all(not x.is_symlink() for x in p.parents); fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC); assert mark(os.fstat(fd))==expected and mark(p.lstat())==expected and not os.listxattr(fd); b=os.pread(fd,1048577,0); assert hashlib.sha256(b).hexdigest()==sys.argv[2] and mark(os.fstat(fd))==expected; os.close(fd); sys.argv=[str(p),*sys.argv[4:]]; exec(compile(b,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})"
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_JOURNAL, MAX_JOURNAL))
    child = subprocess.Popen([sys.executable, '-I', '-B', '-c', loader, source['path'],
                              source['descriptor']['sha256'], json.dumps(physical), *args], stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
                             env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}, preexec_fn=limits)
    selector = selectors.DefaultSelector()
    selector.register(child.stdout, selectors.EVENT_READ, 'out')
    selector.register(child.stderr, selectors.EVENT_READ, 'err')
    streams = {'out': bytearray(), 'err': bytearray()}
    deadline = time.monotonic() + min(45, left)
    try:
        while selector.get_map():
            need(time.monotonic() < deadline, 'HELPER_COMPLETION_UNKNOWN')
            for key, _ in selector.select(min(.1, max(0, deadline-time.monotonic()))):
                block = os.read(key.fileobj.fileno(), 8192)
                if not block:
                    selector.unregister(key.fileobj)
                else:
                    streams[key.data].extend(block)
                    need(sum(map(len, streams.values())) <= MAX_RECORD, 'HELPER_OUTPUT_BOUND')
        need(child.wait(timeout=max(.01, deadline-time.monotonic())) == 0 and not streams['err'], 'HELPER_REFUSED')
        need(read_owned(source['path'], 1024*1024, pin=source['descriptor'], source=True)[1] == physical, 'HELPER_PHYSICAL_CHANGED')
        return {'status': 'PINNED_HELPER_RETURNED', 'result': parse(bytes(streams['out'])),
                'actual_process': {'pid': child.pid, 'exit_code': child.returncode}, 'source_identity': physical}
    finally:
        selector.close()
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=5)
        child.stdout.close()
        child.stderr.close()


def main():
    need(sys.platform == 'linux' and os.getuid() == os.geteuid()
         and os.getgid() == os.getegid() and sys.flags.isolated and sys.dont_write_bytecode,
         'ACTUAL_ISOLATED_LINUX_REQUIRED')
    need(len(sys.argv) == 3 and len(sys.argv[2]) <= 256 * 1024, 'COMMAND_BOUND')
    value = parse(base64.b64decode(sys.argv[2], validate=True))
    action = sys.argv[1]
    if action == 'identity':
        result = identity(value['root'])
    elif action in {'open', 'reserve', 'complete', 'finish', 'unknown'}:
        result = journal(action, value)
    elif action == 'read-chunk':
        result = read_chunk(value)
    elif action == 'read-intent':
        result = read_intent(value)
    else:
        need(action == 'invoke', 'UNKNOWN_HOST_ACTION')
        result = invoke(value)
    print(encode(result).decode(), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        # Raw stdout/stderr, paths, arbitrary exceptions and tool bodies are not diagnostics.
        code = str(exc) if isinstance(exc, Refusal) else 'HOST_OPERATION_REFUSED_OR_UNKNOWN'
        print(json.dumps({'status': 'REFUSED_OR_UNKNOWN', 'code': code,
                          'authority': 'NONE', 'automatic_retry': False}), flush=True)
        sys.exit(1)
