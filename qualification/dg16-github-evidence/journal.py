#!/usr/bin/env python3
"""Bounded create-only public observation journal. Records are not authority.

Called only through the pinned channel bootstrap. No network, crypto, subprocess,
provider replay, acceptance, or raw connector/materialization output is supported.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

LIMIT = 262144


def need(value):
    if not value:
        raise ValueError("JOURNAL_REFUSED")


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf8")


def parse(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            need(key not in value)
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False))


def descriptor(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid)


def safe(value):
    """Reject secret-bearing transport representations, including on failures."""
    if isinstance(value, dict):
        for key, item in value.items():
            need(key not in {"download_url", "file_uri", "file_id", "private_key",
                             "raw_result", "raw_history", "signed_url", "credentials"})
            safe(item)
    elif isinstance(value, list):
        for item in value:
            safe(item)
    elif isinstance(value, str):
        need(not re.search(r"(?i)(?:[?&](?:sig|token|access_token)=|bearer\s|BEGIN .*PRIVATE KEY)", value))
    else:
        need(value is None or type(value) in (bool, int))


def open_directory(path):
    need(os.name == "posix" and os.getuid() == os.geteuid())
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path)
    before = path.lstat()
    need(stat.S_ISDIR(before.st_mode) and before.st_uid == os.geteuid()
         and stat.S_IMODE(before.st_mode) == 0o700)
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    need(identity(os.fstat(fd)) == identity(before) == identity(path.lstat()))
    return path, fd, identity(before)


def check_directory(path, fd, mark):
    need(identity(os.fstat(fd)) == mark == identity(path.lstat()))


def read(fd, name):
    f = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=fd)
    try:
        before = os.fstat(f)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
             and before.st_uid == os.geteuid() and stat.S_IMODE(before.st_mode) == 0o600
             and 0 < before.st_size <= LIMIT)
        raw = bytearray()
        while len(raw) <= LIMIT:
            chunk = os.read(f, min(65536, LIMIT + 1 - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
        stamp = lambda s: (*identity(s), s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        need(len(raw) == before.st_size and stamp(before) == stamp(os.fstat(f))
             == stamp(os.stat(name, dir_fd=fd, follow_symlinks=False)))
        return bytes(raw)
    finally:
        os.close(f)


def write(fd, name, value):
    safe(value)
    raw = encode(value)
    need(0 < len(raw) <= LIMIT)
    f = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                0o600, dir_fd=fd)
    try:
        os.fchmod(f, 0o600)
        view = memoryview(raw)
        while view:
            count = os.write(f, view)
            need(count > 0)
            view = view[count:]
        os.fsync(f)
    finally:
        os.close(f)
    os.fsync(fd)
    need(read(fd, name) == raw)
    return descriptor(raw)


def act(root, action, payload):
    need(action in {"begin", "intent", "result", "finish", "unknown"})
    need(type(payload) is dict and re.fullmatch(r"[0-9a-f]{64}", payload.get("operation_key", "")))
    key = payload["operation_key"]
    path, parent, parent_mark = open_directory(root)
    fd = None
    try:
        if action == "begin":
            # EEXIST is terminal even for a new caller nonce or a half-written slot.
            os.mkdir(key, mode=0o700, dir_fd=parent)
            os.fsync(parent)
        slot = path / key
        _, fd, mark = open_directory(slot)
        check_directory(path, parent, parent_mark)
        names = set(os.listdir(fd))
        need(len(names) <= 70 and all(re.fullmatch(r"(?:INTENT|FINAL|UNKNOWN)\.json|[0-9]{3}\.(?:intent|result)\.json", n)
                                     for n in names))
        if action == "begin":
            need(not names and type(payload.get("action_count")) is int and 0 < payload["action_count"] <= 32)
            receipt = write(fd, "INTENT.json", payload)
        else:
            original = read(fd, "INTENT.json")
            initial = parse(original)
            need(payload.get("initial") == descriptor(original))
            need("FINAL.json" not in names and "UNKNOWN.json" not in names)
            count = initial["action_count"]
            index = payload.get("index")
            if action in {"intent", "result"}:
                need(type(index) is int and 0 <= index < count)
                wanted = {"INTENT.json"}
                for i in range(index):
                    for suffix in ("intent", "result"):
                        name = f"{i:03d}.{suffix}.json"
                        wanted.add(name)
                        read(fd, name)
                if action == "result":
                    name = f"{index:03d}.intent.json"
                    wanted.add(name)
                    need(payload.get("intent") == descriptor(read(fd, name)))
                need(names == wanted)
                receipt = write(fd, f"{index:03d}.{action}.json", payload)
            elif action == "finish":
                wanted = {"INTENT.json"} | {f"{i:03d}.{suffix}.json" for i in range(count)
                                                   for suffix in ("intent", "result")}
                need(names == wanted and type(payload.get("records")) is list and len(payload["records"]) == count)
                for i, row in enumerate(payload["records"]):
                    need(row["intent"] == descriptor(read(fd, f"{i:03d}.intent.json"))
                         and row["result"] == descriptor(read(fd, f"{i:03d}.result.json")))
                receipt = write(fd, "FINAL.json", payload)
            else:
                need(payload.get("status") == "UNKNOWN_NO_RETRY")
                receipt = write(fd, "UNKNOWN.json", payload)
        check_directory(slot, fd, mark)
        check_directory(path, parent, parent_mark)
        return {"status": "PERSISTED_AND_READ_BACK", "authority": "NONE", "operation_key": key,
                "action": action, "record": receipt}
    finally:
        if fd is not None:
            os.close(fd)
        os.close(parent)


if __name__ == "__main__":
    try:
        need(len(sys.argv) == 4 and len(sys.argv[3].encode("utf8")) <= LIMIT)
        result = act(sys.argv[1], sys.argv[2], parse(sys.argv[3]))
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    except BaseException:
        # Error text and arbitrary paths/provider data never cross this boundary.
        print('{"status":"JOURNAL_REFUSED","authority":"NONE"}')
        raise SystemExit(1)
