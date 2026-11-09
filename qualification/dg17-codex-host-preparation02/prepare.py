"""DG17 exact official-package member preparation; no package install or native probe.

The callable main is restricted to one actual isolated hosted push. Source tests
use inert decoding, predicates, and temporary new files; they do not call main.
"""
import base64
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import selectors
import signal
import stat
import subprocess
import sys
import time
import types

REPOSITORY = "theislampill/IMPLEMENTAUDIT.md"
BRANCH = "pro/dg17-isolated-episode-01-20261106"
MEMBER_BYTES = 72160
MEMBER_SHA256 = "e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71"
PACKAGE_SHA256 = "2461f1beee9cb04c8942739fe1a2b37e7b7c2a3d518f0779dc75f9245baa3094"
PACKAGE_COPYRIGHT_NOTICE = 'Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/\nUpstream-Name: bubblewrap\nSource: https://github.com/containers/bubblewrap/\n\nFiles: *\nCopyright:\n 2016 Alexander Larsson\n 2021 Simon McVittie\n 2022 Collabora Ltd.\nLicense: LGPL-2+\n\nFiles: bubblewrap.jpg\nCopyright: none\nLicense: pd-bubblewrap.jpg\n Placed in the public domain by the photographer "dancing_stupidity".\n\nFiles: debian/*\nCopyright:\n 2016 Laszlo Boszormenyi (GCS) <gcs@debian.org>\n 2016-2024 Simon McVittie\n 2016-2024 Collabora Ltd.\nLicense: LGPL-2+\n\nFiles:\n git.mk\nCopyright:\n 2009, Red Hat, Inc.\n 2010-2013 Behdad Esfahbod\nLicense: permissive-git.mk\n Copying and distribution of this file, with or without modification,\n is permitted in any medium without royalty provided the copyright\n notice and this notice are preserved.\n\nFiles: m4/attributes.m4\nCopyright:\n 2006-2008 Diego Pettenò <flameeyes@gmail.com>\n 2006-2008 xine project\n 2012 Lucas De Marchi <lucas.de.marchi@gmail.com>\nLicense: GPL-2+ with Autoconf exception\n\nLicense: LGPL-2+\n This library is free software; you can redistribute it and/or\n modify it under the terms of the GNU Library General Public\n License as published by the Free Software Foundation; either\n version 2 of the License, or (at your option) any later version.\n .\n This library is distributed in the hope that it will be useful,\n but WITHOUT ANY WARRANTY; without even the implied warranty of\n MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU\n Library General Public License for more details.\n .\n You should have received a copy of the GNU Library General Public\n License along with this library; if not, write to the Free Software\n Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301\n USA.\n .\n On Debian systems, the full text of the GNU Library General Public License\n version 2 can be found in the file `/usr/share/common-licenses/LGPL-2\'.\n\nLicense: GPL-2+ with Autoconf exception\n This program is free software; you can redistribute it and/or modify\n it under the terms of the GNU General Public License as published by\n the Free Software Foundation; either version 2, or (at your option)\n any later version.\n .\n This program is distributed in the hope that it will be useful,\n but WITHOUT ANY WARRANTY; without even the implied warranty of\n MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n GNU General Public License for more details.\n .\n You should have received a copy of the GNU General Public License\n along with this program; if not, write to the Free Software\n Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA\n 02110-1301, USA.\n .\n As a special exception, the copyright owners of the\n macro gives unlimited permission to copy, distribute and modify the\n configure scripts that are the output of Autoconf when processing the\n Macro. You need not follow the terms of the GNU General Public\n License when using or distributing such scripts, even though portions\n of the text of the Macro appear in them. The GNU General Public\n License (GPL) does govern all other use of the material that\n constitutes the Autoconf Macro.\n .\n This special exception to the GPL applies to versions of the\n Autoconf Macro released by this project. When you make and\n distribute a modified version of the Autoconf Macro, you may extend\n this special exception to the GPL to apply to your modified version as\n well.\n'
SOURCE_PACKAGE_FILES = (
    "https://archive.ubuntu.com/ubuntu/pool/main/b/bubblewrap/bubblewrap_0.9.0.orig.tar.xz",
    "https://archive.ubuntu.com/ubuntu/pool/main/b/bubblewrap/bubblewrap_0.9.0-1ubuntu0.3.debian.tar.xz",
    "https://archive.ubuntu.com/ubuntu/pool/main/b/bubblewrap/bubblewrap_0.9.0-1ubuntu0.3.dsc",
)
B64_BYTES = 96217
B64_SHA256 = "06cf45cd324bdaab73c9f38def8288af80bdd395bf926c2a08c10e2a28625f65"
HOST_UTILITY_SHA256 = "429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c"
ROOT_SOURCE_SHA256 = "33f85ecb00111dcd77ebd54e44a2b5b9241a6bca76c4880cca99be4ac3bdc8c3"
ROOT_SOURCE = '"""Fixed exclusive exact-member writer. Invoked only as reviewed inline source.\n\nNo package scripts, package parser, downloaded execution, permission repair,\nexisting-leaf overwrite, security setting change or pathname cleanup exists.\n"""\nimport hashlib\nimport json\nimport os\nimport re\nimport signal\nimport stat\nimport sys\n\nMEMBER_BYTES = 72160\nMEMBER_SHA256 = "e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71"\nGO = b"DG17_BWRAP_GO_2\\n"\n\n\ndef need(ok, code):\n    if not ok:\n        raise RuntimeError(code)\n\n\ndef sha(raw):\n    return hashlib.sha256(raw).hexdigest()\n\n\ndef identity(value):\n    return {key: getattr(value, "st_" + key) for key in ("dev", "ino", "mode", "uid", "gid", "nlink", "size", "mtime_ns", "ctime_ns")}\n\n\ndef open_chain(path):\n    need(type(path) is str and path.startswith("/") and "\\x00" not in path, "INPUT_PATH")\n    parts = path[1:].split("/")\n    need(all(part and part not in (".", "..") for part in parts), "INPUT_PATH")\n    handles = [os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)]\n    try:\n        for part in parts[:-1]:\n            handles.append(os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=handles[-1]))\n        leaf = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=handles[-1])\n        handles.append(leaf)\n        return handles\n    except BaseException:\n        for descriptor in reversed(handles): os.close(descriptor)\n        raise\n\n\ndef input_memory(path, uid, gid):\n    handles = open_chain(path)\n    try:\n        parent, descriptor = handles[-2:]\n        info = os.fstat(parent)\n        need(stat.S_ISDIR(info.st_mode) and info.st_uid == uid and info.st_gid == gid and stat.S_IMODE(info.st_mode) == 0o700, "INPUT_PARENT")\n        before = os.fstat(descriptor)\n        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_uid == uid and before.st_gid == gid\n             and stat.S_IMODE(before.st_mode) == 0o600 and before.st_size == MEMBER_BYTES, "INPUT_FILE")\n        raw = bytearray()\n        while len(raw) <= MEMBER_BYTES:\n            part = os.read(descriptor, min(65536, MEMBER_BYTES + 1 - len(raw)))\n            if not part: break\n            raw.extend(part)\n        need(len(raw) == MEMBER_BYTES and sha(raw) == MEMBER_SHA256, "INPUT_BYTES")\n        need(identity(before) == identity(os.fstat(descriptor)) == identity(os.stat(path.rsplit("/", 1)[1], dir_fd=parent, follow_symlinks=False)), "INPUT_DRIFT")\n        return bytes(raw)\n    finally:\n        for descriptor in reversed(handles): os.close(descriptor)\n\n\ndef target_chain():\n    handles = [os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)]\n    try:\n        for name in ("usr", "bin"):\n            handles.append(os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=handles[-1]))\n        for descriptor in handles:\n            info = os.fstat(descriptor)\n            need(stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and info.st_gid == 0 and not info.st_mode & 0o022, "TARGET_ANCESTRY")\n        return handles\n    except BaseException:\n        for descriptor in reversed(handles): os.close(descriptor)\n        raise\n\n\ndef require_absent(parent):\n    try: os.stat("bwrap", dir_fd=parent, follow_symlinks=False)\n    except FileNotFoundError: return\n    raise RuntimeError("TARGET_NOT_ABSENT")\n\n\ndef create_exact(parent, raw, expected_uid=0, expected_gid=0):\n    """Only caller is fixed run(), using the held /usr/bin descriptor and UID0.\n\n    Descriptor parameters permit inert temporary-file source tests. Production\n    argv cannot select a target name, directory, owner, mode or byte population.\n    """\n    need(len(raw) == MEMBER_BYTES and sha(raw) == MEMBER_SHA256, "WRITE_INPUT_BYTES")\n    descriptor = os.open("bwrap", os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent)\n    committed = False\n    try:\n        start = os.fstat(descriptor)\n        need(stat.S_ISREG(start.st_mode) and start.st_uid == expected_uid and start.st_gid == expected_gid\n             and stat.S_IMODE(start.st_mode) == 0o600 and start.st_nlink == 1 and start.st_size == 0, "NEW_INODE")\n        offset = 0\n        while offset < len(raw):\n            count = os.write(descriptor, raw[offset:])\n            need(type(count) is int and count > 0, "WRITE_PROGRESS")\n            offset += count\n        os.fsync(descriptor); os.lseek(descriptor, 0, os.SEEK_SET)\n        received = bytearray()\n        while len(received) <= MEMBER_BYTES:\n            part = os.read(descriptor, min(65536, MEMBER_BYTES + 1 - len(received)))\n            if not part: break\n            received.extend(part)\n        need(bytes(received) == raw, "NEW_INODE_READBACK")\n        try: caps = os.getxattr(descriptor, "security.capability")\n        except OSError as exc:\n            need(exc.errno in (61, 95), "NEW_INODE_CAPABILITIES_UNKNOWN"); caps = b""\n        need(caps == b"", "NEW_INODE_CAPABILITIES")\n        current = os.fstat(descriptor)\n        need(current.st_uid == expected_uid and current.st_gid == expected_gid and current.st_nlink == 1\n             and current.st_size == MEMBER_BYTES and (current.st_dev, current.st_ino) == (start.st_dev, start.st_ino), "NEW_INODE_CHANGED")\n        os.fchmod(descriptor, 0o755); os.fsync(descriptor)\n        final = os.fstat(descriptor)\n        at_path = os.stat("bwrap", dir_fd=parent, follow_symlinks=False)\n        need(identity(final) == identity(at_path) and stat.S_IMODE(final.st_mode) == 0o755, "NEW_INODE_PATH_BINDING")\n        committed = True\n        return identity(final)\n    finally:\n        if not committed:\n            try: os.fchmod(descriptor, 0o600); os.fsync(descriptor)\n            except OSError: pass\n        os.close(descriptor)\n\n\ndef emit(value):\n    raw = (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\\n").encode("ascii")\n    need(len(raw) <= 4096, "ROOT_OUTPUT_BOUND")\n    sys.stdout.buffer.write(raw); sys.stdout.buffer.flush()\n\n\ndef run():\n    need(len(sys.argv) == 6 and os.getuid() == os.geteuid() == 0 and os.getgid() == os.getegid() == 0, "ROOT_IDENTITY_ARGUMENTS")\n    path, uid_text, gid_text, nonce, source_sha = sys.argv[1:]\n    need(re.fullmatch("[1-9][0-9]{0,9}", uid_text) and re.fullmatch("[1-9][0-9]{0,9}", gid_text), "OWNER_IDENTITY")\n    need(re.fullmatch("[0-9a-f]{32}", nonce) and re.fullmatch("[0-9a-f]{64}", source_sha), "ROOT_BINDING")\n    signal.signal(signal.SIGALRM, signal.SIG_DFL)\n    signal.setitimer(signal.ITIMER_REAL, 10.0)\n    need(0 < signal.getitimer(signal.ITIMER_REAL)[0] <= 10.0, "ROOT_TIMER")\n    with open("/proc/self/cmdline", "rb") as stream: command = stream.read(32769)\n    need(len(command) <= 32768 and command.endswith(b"\\x00"), "ROOT_COMMAND_BOUND")\n    parts = command[:-1].split(b"\\x00")\n    need(len(parts) == 11 and parts[1:5] == [b"-I", b"-S", b"-B", b"-c"] and sha(parts[5]) == source_sha, "ROOT_INLINE_SOURCE")\n    raw = input_memory(path, int(uid_text), int(gid_text))\n    handles = target_chain()\n    try:\n        parent = handles[-1]; require_absent(parent)\n        emit({"schema": "dg17.bwrap.root-ready.v2", "nonce": nonce, "source_sha256": source_sha,\n              "input_sha256": sha(raw), "input_bytes": len(raw), "target_absent": True,\n              "uid": 0, "gid": 0, "timer_seconds": 10, "writer_pid": os.getpid(), "target_parent": identity(os.fstat(parent))})\n        go = os.read(0, len(GO) + 1)\n        need(go == GO, "ROOT_GO_REFUSED")\n        require_absent(parent)\n        result = create_exact(parent, raw)\n        for descriptor, parent_descriptor, name in ((handles[1], handles[0], "usr"), (handles[2], handles[1], "bin")):\n            need((os.fstat(descriptor).st_dev, os.fstat(descriptor).st_ino) ==\n                 (os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False).st_dev, os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False).st_ino), "TARGET_ANCESTRY_CHANGED")\n        emit({"schema": "dg17.bwrap.root-created.v2", "nonce": nonce, "source_sha256": source_sha,\n              "input_sha256": sha(raw), "input_bytes": len(raw), "created": result, "writer_pid": os.getpid(), "go_received": True})\n    finally:\n        for descriptor in reversed(handles): os.close(descriptor)\n\n\nif __name__ == "__main__":\n    try: run()\n    except BaseException:\n        sys.stderr.write("DG17_BWRAP_ROOT_WRITE_REFUSED\\n")\n        raise SystemExit(1)\n'
GO = b"DG17_BWRAP_GO_2\n"
PREFIX = "DG17_HOST_PREPARATION_V2 "
MAX_STREAM = 32768


class Refusal(ValueError):
    pass


def need(value, code):
    if value is not True:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def strict(raw, bound):
    need(type(raw) is bytes and 0 < len(raw) <= bound, "JSON_BOUND")
    def pairs(items):
        output = {}
        for key, value in items:
            need(key not in output, "JSON_DUPLICATE"); output[key] = value
        return output
    def reject(value): raise Refusal("JSON_NONFINITE")
    try: value = json.loads(raw.decode("ascii"), object_pairs_hook=pairs, parse_constant=reject)
    except (UnicodeError, json.JSONDecodeError): raise Refusal("JSON_SYNTAX") from None
    need(encoded(value) == raw, "JSON_ENCODING")
    return value


def identity(value):
    return {key: getattr(value, "st_" + key) for key in ("dev", "ino", "mode", "uid", "gid", "nlink", "size", "mtime_ns", "ctime_ns")}


def read_regular(path, bound):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path, "READ_PHYSICAL_PATH")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= bound, "READ_FILE")
        raw = bytearray()
        while len(raw) <= bound:
            part = os.read(descriptor, min(65536, bound + 1 - len(raw)))
            if not part: break
            raw.extend(part)
        need(len(raw) == before.st_size and identity(before) == identity(os.fstat(descriptor)) == identity(path.lstat()), "READ_CHANGED")
        return bytes(raw)
    finally: os.close(descriptor)


def decode_member(raw):
    need(type(raw) is bytes and len(raw) == B64_BYTES and sha(raw) == B64_SHA256 and raw.endswith(b"\n"), "MEMBER_TRANSPORT_PIN")
    try: member = base64.b64decode(raw[:-1], validate=True)
    except ValueError: raise Refusal("MEMBER_BASE64") from None
    need(base64.b64encode(member) + b"\n" == raw and len(member) == MEMBER_BYTES and sha(member) == MEMBER_SHA256, "MEMBER_IDENTITY")
    need(member[:7] == b"\x7fELF\x02\x01\x01" and int.from_bytes(member[16:18], "little") in (2, 3)
         and int.from_bytes(member[18:20], "little") == 62, "MEMBER_ELF")
    return member


def _boot_bytes():
    descriptor = os.open("/proc/sys/kernel/random/boot_id", os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(descriptor); raw = os.read(descriptor, 129)
        need(stat.S_ISREG(before.st_mode) and identity(before) == identity(os.fstat(descriptor)), "BOOT_FILE")
        return raw
    finally: os.close(descriptor)


def boot_identity(reader=_boot_bytes):
    raw = reader()
    need(type(raw) is bytes and len(raw) <= 128 and re.fullmatch(rb"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\n", raw) is not None, "BOOT_IDENTITY")
    return sha(raw.rstrip(b"\n"))


def physical_helper():
    """Same physical bwrap constraints as the unchanged native helper gate."""
    for path in (Path("/"), Path("/usr"), Path("/usr/bin")):
        info = path.lstat()
        need(path.resolve(strict=True) == path and stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and not info.st_mode & 0o022, "HELPER_ANCESTRY")
    alias = Path("/bin"); alias_info = alias.lstat()
    need(stat.S_ISLNK(alias_info.st_mode) and alias_info.st_uid == 0 and os.readlink(alias) in ("usr/bin", "/usr/bin")
         and alias.resolve(strict=True) == Path("/usr/bin"), "HELPER_BIN_ALIAS")
    path = Path("/usr/bin/bwrap")
    try: before = path.lstat()
    except FileNotFoundError: return {"status": "EXACT_ENOENT", "errno": errno.ENOENT}
    need(stat.S_ISREG(before.st_mode) and before.st_uid == 0 and not before.st_mode & 0o6022 and bool(before.st_mode & 0o111)
         and 64 <= before.st_size <= 67108864 and path.resolve(strict=True) == path, "HELPER_FILE_SHAPE")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        need(identity(before) == identity(os.fstat(descriptor)), "HELPER_OPEN_DRIFT")
        header = os.read(descriptor, 64)
        need(len(header) == 64 and header[:7] == b"\x7fELF\x02\x01\x01" and int.from_bytes(header[16:18], "little") in (2, 3)
             and int.from_bytes(header[18:20], "little") == 62, "HELPER_ELF")
        digest = hashlib.sha256(header); count = len(header)
        while True:
            block = os.read(descriptor, 1048576)
            if not block: break
            count += len(block); need(count <= before.st_size, "HELPER_READ_BOUND"); digest.update(block)
        try: caps = os.getxattr(descriptor, "security.capability")
        except OSError as exc:
            need(exc.errno in (errno.ENODATA, errno.ENOTSUP), "HELPER_CAPABILITIES_UNKNOWN"); caps = b""
        need(caps == b"" and count == before.st_size and identity(before) == identity(os.fstat(descriptor)) == identity(path.lstat()), "HELPER_IDENTITY_DRIFT")
        need((Path("/bin") / "bwrap").resolve(strict=True) == path and identity(alias_info) == identity(alias.lstat()), "HELPER_ALIAS_DRIFT")
        return {"status": "PHYSICAL_HELPER_ADMITTED", "identity": identity(before), "bytes": count, "sha256": digest.hexdigest(),
                "elf": "ELF64_LSB_X86_64", "file_capabilities": False, "bin_alias_same_file": True}
    finally: os.close(descriptor)


def root_tools(u):
    observations = {}
    for name in ("python3", "timeout"):
        path, observed = u.trusted(name)
        need(path is not None, "ROOT_TOOL_REFUSED"); observations[name] = observed
    path = Path("/usr/bin/sudo")
    need(path.resolve(strict=True) == path, "SUDO_PHYSICAL_PATH")
    for ancestor in (path, *path.parents):
        info = ancestor.lstat(); need(info.st_uid == 0 and not info.st_mode & 0o022, "SUDO_ANCESTRY")
    info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o4755, "SUDO_ROLE")
    raw = read_regular(path, 67108864)
    try: caps = os.getxattr(path, "security.capability")
    except OSError as exc:
        need(exc.errno in (errno.ENODATA, errno.ENOTSUP), "SUDO_CAPABILITIES_UNKNOWN"); caps = b""
    need(caps == b"", "SUDO_CAPABILITIES")
    observations["sudo"] = {"identity": identity(info), "bytes": len(raw), "sha256": sha(raw), "mode": "04755",
        "admitted_effect": "EXCLUSIVE_EXACT_PACKAGE_MEMBER_ONLY_NO_EXISTING_LEAF_REPAIR"}
    return observations


def ready_value(raw, nonce):
    value = strict(raw, 4096)
    need(type(value) is dict and set(value) == {"schema", "nonce", "source_sha256", "input_sha256", "input_bytes", "target_absent", "uid", "gid", "timer_seconds", "writer_pid", "target_parent"}, "ROOT_READY_FIELDS")
    need(value["schema"] == "dg17.bwrap.root-ready.v2" and value["nonce"] == nonce and value["source_sha256"] == ROOT_SOURCE_SHA256
         and value["input_sha256"] == MEMBER_SHA256 and type(value["input_bytes"]) is int and value["input_bytes"] == MEMBER_BYTES
         and value["target_absent"] is True and type(value["uid"]) is int and value["uid"] == 0
         and type(value["gid"]) is int and value["gid"] == 0 and type(value["timer_seconds"]) is int and value["timer_seconds"] == 10
         and type(value["writer_pid"]) is int and value["writer_pid"] > 0, "ROOT_READY_IDENTITY")
    parent = value["target_parent"]
    need(type(parent) is dict and set(parent) == {"dev", "ino", "mode", "uid", "gid", "nlink", "size", "mtime_ns", "ctime_ns"}
         and all(type(item) is int for item in parent.values()) and stat.S_ISDIR(parent["mode"])
         and parent["uid"] == parent["gid"] == 0 and not parent["mode"] & 0o022, "ROOT_READY_PARENT")
    return value


def created_value(raw, nonce, ready):
    value = strict(raw, 4096)
    need(type(value) is dict and set(value) == {"schema", "nonce", "source_sha256", "input_sha256", "input_bytes", "created", "writer_pid", "go_received"}, "ROOT_CREATED_FIELDS")
    need(value["schema"] == "dg17.bwrap.root-created.v2" and value["nonce"] == nonce and value["source_sha256"] == ROOT_SOURCE_SHA256
         and value["input_sha256"] == MEMBER_SHA256 and type(value["input_bytes"]) is int and value["input_bytes"] == MEMBER_BYTES
         and value["writer_pid"] == ready["writer_pid"] and value["go_received"] is True, "ROOT_CREATED_IDENTITY")
    row = value["created"]
    need(type(row) is dict and set(row) == {"dev", "ino", "mode", "uid", "gid", "nlink", "size", "mtime_ns", "ctime_ns"}
         and all(type(item) is int for item in row.values()) and stat.S_ISREG(row["mode"])
         and row["uid"] == row["gid"] == 0 and stat.S_IMODE(row["mode"]) == 0o755 and row["nlink"] == 1
         and row["size"] == MEMBER_BYTES and row["dev"] > 0 and row["ino"] > 0, "ROOT_CREATED_FILE")
    return value


def capture_root(argv, nonce, u, private):
    """One fixed root chain, READY/16-byte GO, bounded streams and actual waits.

    The admitted adopted-status population for success is exactly empty. Direct
    zero plus global ECHILD is required. Any observed adopted status, even zero,
    refuses; no unknown sudo/PAM process is classified by name or successful exit.
    """
    start = time.monotonic(); deadline = start + 30.0
    record = {"process_started": False, "pidfd_acquired": False, "ready_received": False, "go_sent": False,
        "returncode": None, "streams_complete": False, "timeout": False, "output_bound_exceeded": False,
        "global_echild": False, "adopted_statuses": [], "failure": None, "start_errno": None,
        "signal_attempted": False, "privileged_signal_permission_assumed": False}
    streams = [bytearray(), bytearray()]; ready = None; process = None; anchor = None
    def fail(code):
        if record["failure"] is None: record["failure"] = code
    def close_input():
        if process is not None and process.stdin is not None and not process.stdin.closed:
            process.stdin.close()
    try:
        process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=u.safe_environment(), start_new_session=True, close_fds=True)
        record["process_started"] = True
        try: anchor = os.pidfd_open(process.pid); record["pidfd_acquired"] = True
        except OSError: fail("PIDFD_ACQUISITION_REFUSED"); close_input()
        os.set_blocking(process.stdin.fileno(), False) if not process.stdin.closed else None
        with selectors.DefaultSelector() as selected:
            for index, stream in enumerate((process.stdout, process.stderr)):
                os.set_blocking(stream.fileno(), False); selected.register(stream, selectors.EVENT_READ, index)
            while selected.get_map() and time.monotonic() < deadline:
                if not record["go_sent"] and time.monotonic() > start + 5.0:
                    fail("READY_DEADLINE"); close_input()
                for key, _ in selected.select(0.05):
                    chunk = os.read(key.fileobj.fileno(), 4096)
                    if not chunk: selected.unregister(key.fileobj); continue
                    remaining = MAX_STREAM - len(streams[key.data]); streams[key.data].extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        record["output_bound_exceeded"] = True; fail("OUTPUT_BOUND"); close_input()
                    if key.data == 1 and chunk:
                        fail("STDERR_PRESENT"); close_input()
                    if key.data == 0 and not record["go_sent"] and record["failure"] is None and b"\n" in streams[0]:
                        first = bytes(streams[0]).split(b"\n", 1)[0] + b"\n"
                        try:
                            ready = ready_value(first, nonce)
                            need(bytes(streams[0]) == first and time.monotonic() <= start + 5.0, "READY_TRANSCRIPT")
                            need(os.write(process.stdin.fileno(), GO) == 16, "GO_WRITE")
                            record["ready_received"] = True; record["go_sent"] = True; close_input()
                        except (Refusal, OSError): fail("READY_OR_GO_REFUSED"); close_input()
            record["streams_complete"] = not selected.get_map() and not record["output_bound_exceeded"]
        close_input()
        while process.poll() is None and time.monotonic() < deadline: time.sleep(0.01)
        record["returncode"] = process.returncode
        if process.returncode is None:
            record["timeout"] = True; fail("PARENT_WATCHDOG")
            if anchor is not None and not record["signal_attempted"]:
                record["signal_attempted"] = True
                try: signal.pidfd_send_signal(anchor, signal.SIGKILL)
                except OSError as exc: record["signal_errno"] = exc.errno
        # The fixed writer has its own noncatching10s timer; the fixed root
        # timeout uses15s TERM +5s KILL. We still require observed terminality.
        end = min(deadline + 4.0, time.monotonic() + 4.0)
        while time.monotonic() < end:
            try: pid, status = os.waitpid(-1, os.WNOHANG | 0x40000000)
            except ChildProcessError: record["global_echild"] = True; break
            if pid:
                need(len(record["adopted_statuses"]) < 4096, "WAIT_STATUS_BOUND")
                need(os.WIFEXITED(status) or os.WIFSIGNALED(status), "WAIT_STATUS_KIND")
                code = os.waitstatus_to_exitcode(status)
                if pid == process.pid and record["returncode"] is None: record["returncode"] = code; process.returncode = code
                else: record["adopted_statuses"].append({"pid": pid, "returncode": code})
            else:
                u.children()  # unchanged eight-live-child/160-character bound
                time.sleep(0.01)
    except BaseException as exc:
        fail(str(exc) if isinstance(exc, Refusal) else "ROOT_CAPTURE_REFUSED")
        if not record["process_started"]: record["start_errno"] = getattr(exc, "errno", None)
    finally:
        close_input()
        # A parser, census or I/O exception must not bypass the same bounded
        # drain/wait owner. No unsent GO is sent from this failure path.
        if process is not None and not record["global_echild"]:
            try:
                with selectors.DefaultSelector() as remaining:
                    for index, stream in enumerate((process.stdout, process.stderr)):
                        if stream is not None and not stream.closed:
                            os.set_blocking(stream.fileno(), False); remaining.register(stream, selectors.EVENT_READ, index)
                    while remaining.get_map() and time.monotonic() < deadline:
                        for key, _ in remaining.select(0.05):
                            chunk = os.read(key.fileobj.fileno(), 4096)
                            if not chunk: remaining.unregister(key.fileobj); continue
                            space = MAX_STREAM - len(streams[key.data]); streams[key.data].extend(chunk[:space])
                            if len(chunk) > space: record["output_bound_exceeded"] = True; fail("OUTPUT_BOUND")
                    record["streams_complete"] = not remaining.get_map() and not record["output_bound_exceeded"]
                while process.poll() is None and time.monotonic() < deadline: time.sleep(0.01)
                if process.returncode is not None: record["returncode"] = process.returncode
                if process.returncode is None:
                    record["timeout"] = True; fail("PARENT_WATCHDOG")
                    if anchor is not None and not record["signal_attempted"]:
                        record["signal_attempted"] = True
                        try: signal.pidfd_send_signal(anchor, signal.SIGKILL)
                        except OSError as exc: record["signal_errno"] = exc.errno
                end = deadline + 4.0
                while time.monotonic() < end:
                    try: pid, status = os.waitpid(-1, os.WNOHANG | 0x40000000)
                    except ChildProcessError: record["global_echild"] = True; break
                    if not pid: time.sleep(0.01); continue
                    need(os.WIFEXITED(status) or os.WIFSIGNALED(status), "WAIT_STATUS_KIND")
                    code = os.waitstatus_to_exitcode(status)
                    if pid == process.pid and record["returncode"] is None: record["returncode"] = code; process.returncode = code
                    else:
                        need(len(record["adopted_statuses"]) < 4096, "WAIT_STATUS_BOUND")
                        record["adopted_statuses"].append({"pid": pid, "returncode": code})
            except BaseException:
                fail("ROOT_FINAL_WAIT_UNCERTAIN")
        if anchor is not None: os.close(anchor)
        if process is not None:
            for stream in (process.stdout, process.stderr):
                if stream is not None: stream.close()
        for name, body in (("root.stdout", bytes(streams[0])), ("root.stderr", bytes(streams[1]))):
            descriptor = os.open(private / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
            with os.fdopen(descriptor, "wb") as stream: stream.write(body); stream.flush(); os.fsync(stream.fileno())
        record.update(stdout_bytes=len(streams[0]), stdout_sha256=sha(streams[0]), stderr_bytes=len(streams[1]), stderr_sha256=sha(streams[1]),
            stream_digest_scope="CAPTURED_BYTES_ONLY", private_streams_retained=True, elapsed_ms=int((time.monotonic() - start) * 1000))
    admitted = (record["failure"] is None and record["returncode"] == 0 and record["pidfd_acquired"] is True
         and record["ready_received"] is True and record["go_sent"] is True and record["streams_complete"] is True
         and record["global_echild"] is True and record["adopted_statuses"] == [] and record["stderr_bytes"] == 0)
    if not admitted:
        fail("ROOT_CAPTURE_NOT_RECEIVED")
        return record, ready, None
    lines = bytes(streams[0]).splitlines(keepends=True)
    try:
        need(len(lines) == 2 and ready is not None, "ROOT_TRANSCRIPT_POPULATION")
        return record, ready, created_value(lines[1], nonce, ready)
    except Refusal as exc:
        fail(str(exc)); return record, ready, None


def public_capture(value):
    result = dict(value); statuses = result.pop("adopted_statuses")
    result.update(adopted_status_count=len(statuses), adopted_statuses=statuses[:8],
        adopted_statuses_truncated=len(statuses) > 8, adopted_statuses_sha256=sha(encoded(statuses)))
    return result


def environment():
    env = os.environ
    need(env.get("GITHUB_ACTIONS") == "true" and env.get("RUNNER_ENVIRONMENT") == "github-hosted" and
         env.get("GITHUB_REPOSITORY") == REPOSITORY and env.get("GITHUB_REF") == "refs/heads/" + BRANCH and
         env.get("GITHUB_EVENT_NAME") == "push" and env.get("GITHUB_RUN_ATTEMPT") == "1" and env.get("GITHUB_JOB") == "dg17-bounded", "ACTUAL_HOSTED_EVENT")
    need(re.fullmatch("[1-9][0-9]{0,18}", env.get("GITHUB_RUN_ID", "")) is not None and re.fullmatch("[0-9a-f]{40}", env.get("GITHUB_SHA", "")) is not None, "ACTUAL_HOSTED_IDENTITY")
    need(os.getuid() == os.geteuid() > 0 and os.getgid() == os.getegid() > 0, "ORDINARY_OWNER")
    return {"repository": REPOSITORY, "branch": BRANCH, "run_id": env["GITHUB_RUN_ID"], "attempt": 1, "workflow_commit": env["GITHUB_SHA"], "job_name": "dg17-bounded"}


def main():
    result = {"schema": "dg17.codex20.host-preparation.v2", "status": "FAILED_OR_UNRECEIVED", "context": None,
        "package_sha256": PACKAGE_SHA256, "member_sha256": MEMBER_SHA256, "member_bytes": MEMBER_BYTES,
        "source_sha256": None, "root_source_sha256": ROOT_SOURCE_SHA256, "input_transport_sha256": B64_SHA256,
        "before": None, "after": None, "root_capture": None, "root_ready": None, "root_created": None,
        "root_tools": None, "host_identity": None, "member_decoded": False, "root_calls": 0, "failure": None,
        "native_execution": False, "security_policy_changed": False, "package_scripts_executed": False,
        "package_companions_applied": False, "existing_helper_modified": False, "host_teardown_observed": False,
        "authority": "NONE", "original_awards": []}
    try:
        result["context"] = environment()
        path = Path(__file__).absolute(); workspace = Path(os.environ["GITHUB_WORKSPACE"])
        need(path == workspace / "packet/qualification/dg17-codex-host-preparation02/prepare.py", "CALLER_PATH")
        result["source_sha256"] = sha(read_regular(path, 1048576))
        need(sha(ROOT_SOURCE.encode("utf8")) == ROOT_SOURCE_SHA256 and len(GO) == 16, "INLINE_ROOT_PIN")
        raw = read_regular(workspace / "packet/qualification/dg17-codex-routing/host_utility.py", 1048576)
        need(sha(raw) == HOST_UTILITY_SHA256, "QUALIFIED_UTILITY_PIN")
        u = types.ModuleType("dg17_qualified_host_utility"); exec(compile(raw, "qualified-host-utility", "exec"), u.__dict__)
        lib = ctypes.CDLL(None, use_errno=True); need(lib.prctl(36, 1, 0, 0, 0) == 0, "SUBREAPER")
        try: os.waitpid(-1, os.WNOHANG | 0x40000000)
        except ChildProcessError: pass
        else: raise Refusal("INITIAL_CHILD_POPULATION")
        need(u.children() == [], "INITIAL_CHILD_CENSUS")
        result["host_identity"] = {"boot_id_sha256": boot_identity(), "root_device": Path("/").stat().st_dev,
            "root_inode": Path("/").stat().st_ino, "uid": os.getuid(), "gid": os.getgid()}
        result["before"] = physical_helper()
        if result["before"]["status"] == "PHYSICAL_HELPER_ADMITTED":
            result["after"] = physical_helper()
            need(result["before"] == result["after"], "EXISTING_HELPER_CHANGED")
            result["status"] = "EXISTING_VALID_UNCHANGED"
        else:
            member = decode_member(read_regular(path.parent / "BWRAP_INPUT.b64", B64_BYTES)); result["member_decoded"] = True
            result["root_tools"] = root_tools(u)
            private = Path(os.environ["RUNNER_TEMP"]) / ("dg17-host-preparation-" + result["context"]["run_id"] + "-a1")
            need(private.parent.resolve(strict=True) == private.parent, "PRIVATE_PARENT")
            private.mkdir(mode=0o700)
            staged = private / "bwrap.member.data"
            descriptor = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
            with os.fdopen(descriptor, "wb") as stream: stream.write(member); stream.flush(); os.fsync(stream.fileno())
            need(read_regular(staged, MEMBER_BYTES) == member, "STAGED_READBACK")
            nonce = secrets.token_hex(16)
            argv = ["/usr/bin/sudo", "-n", "/usr/bin/timeout", "--signal=TERM", "--kill-after=5s", "15s",
                "/usr/bin/python3", "-I", "-S", "-B", "-c", ROOT_SOURCE, str(staged), str(os.getuid()), str(os.getgid()), nonce, ROOT_SOURCE_SHA256]
            result["root_calls"] = 1
            capture, ready, created = capture_root(argv, nonce, u, private)
            descriptor = os.open(private / "root.capture.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
            capture_raw = encoded(capture); need(len(capture_raw) <= 262144, "PRIVATE_CAPTURE_BOUND")
            with os.fdopen(descriptor, "wb") as stream: stream.write(capture_raw); stream.flush(); os.fsync(stream.fileno())
            result.update(root_capture=public_capture(capture), root_ready=ready, root_created=created)
            need(capture["failure"] is None and created is not None, "ROOT_CAPTURE_NOT_RECEIVED")
            result["after"] = physical_helper()
            need(result["after"]["status"] == "PHYSICAL_HELPER_ADMITTED" and result["after"]["bytes"] == MEMBER_BYTES
                 and result["after"]["sha256"] == MEMBER_SHA256 and result["after"]["identity"] == created["created"], "CREATED_PARENT_READBACK")
            result["status"] = "CREATED_EXACT_MEMBER_AND_CUSTODY_RECEIVED"
    except BaseException as exc:
        result["failure"] = {"code": str(exc) if isinstance(exc, Refusal) else "HOST_PREPARATION_REFUSED",
            "exception_type": type(exc).__name__, "errno": getattr(exc, "errno", None)}
    raw = encoded(result)
    need(len(raw) <= 16384, "PUBLIC_PREPARATION_BOUND")
    print(PREFIX + raw.decode("ascii").rstrip("\n"), flush=True)
    return 0 if result["status"] in ("EXISTING_VALID_UNCHANGED", "CREATED_EXACT_MEMBER_AND_CUSTODY_RECEIVED") else 1


if __name__ == "__main__":
    sys.exit(main())
