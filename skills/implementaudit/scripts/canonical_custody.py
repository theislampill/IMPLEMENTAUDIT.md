"""Private Windows filesystem substrate for the existing canonical-state owners.

No authority, ref publication, recovery, or schema decisions live here. Windows
opens one component relative to a retained parent, with reparse processing off;
all ancestors remain held without delete sharing until the operation finishes.
The parent-relative acquisition and long-name checks follow the accepted
repository-only operational-evidence reader. Writable files, directory creation,
change-time checks, enumeration and coordination locks are separately qualified.
"""
from __future__ import annotations

import contextlib
import contextvars
import ctypes
import hashlib
import os
from pathlib import Path, PureWindowsPath
import re
import stat
import subprocess
import threading
import time
from types import SimpleNamespace


class UnicodeString(ctypes.Structure):
    _fields_ = [("length", ctypes.c_ushort), ("maximum", ctypes.c_ushort), ("buffer", ctypes.c_void_p)]


class ObjectAttributes(ctypes.Structure):
    _fields_ = [("length", ctypes.c_ulong), ("root", ctypes.c_void_p),
                ("name", ctypes.POINTER(UnicodeString)), ("attributes", ctypes.c_ulong),
                ("security", ctypes.c_void_p), ("quality", ctypes.c_void_p)]


class IoStatus(ctypes.Structure):
    _fields_ = [("status", ctypes.c_void_p), ("information", ctypes.c_size_t)]


class FileTime(ctypes.Structure):
    _fields_ = [("low", ctypes.c_ulong), ("high", ctypes.c_ulong)]


class FileInfo(ctypes.Structure):
    _fields_ = [("attributes", ctypes.c_ulong), ("creation", FileTime),
                ("access", FileTime), ("write", FileTime), ("volume", ctypes.c_ulong),
                ("size_high", ctypes.c_ulong), ("size_low", ctypes.c_ulong),
                ("links", ctypes.c_ulong), ("index_high", ctypes.c_ulong), ("index_low", ctypes.c_ulong)]


class BasicInfo(ctypes.Structure):
    _fields_ = [("creation", ctypes.c_longlong), ("access", ctypes.c_longlong),
                ("write", ctypes.c_longlong), ("change", ctypes.c_longlong), ("attributes", ctypes.c_ulong)]


class DirectoryInfo(ctypes.Structure):
    _fields_ = [("next", ctypes.c_ulong), ("index", ctypes.c_ulong),
                ("creation", ctypes.c_longlong), ("access", ctypes.c_longlong),
                ("write", ctypes.c_longlong), ("change", ctypes.c_longlong),
                ("size", ctypes.c_longlong), ("allocation", ctypes.c_longlong),
                ("attributes", ctypes.c_ulong), ("name_length", ctypes.c_ulong),
                ("ea_size", ctypes.c_ulong), ("short_length", ctypes.c_byte),
                ("short_name", ctypes.c_wchar * 12), ("file_id", ctypes.c_longlong),
                ("name", ctypes.c_wchar * 1)]


def kernel():
    if os.name != "nt":
        raise OSError("Windows custody requires the actual Windows kernel")
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    p, u, b = ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int
    signatures = {
        "CreateFileW": ([ctypes.c_wchar_p, u, u, p, u, u, p], p),
        "CloseHandle": ([p], b), "GetDriveTypeW": ([ctypes.c_wchar_p], u),
        "GetFileInformationByHandle": ([p, p], b),
        "GetFileInformationByHandleEx": ([p, b, p, u], b),
        "SetFileInformationByHandle": ([p, b, p, u], b),
        "GetFinalPathNameByHandleW": ([p, ctypes.c_wchar_p, u, u], u),
        "GetVolumeInformationByHandleW": ([p, ctypes.c_wchar_p, u, p, p, p, ctypes.c_wchar_p, u], b),
        "FlushFileBuffers": ([p], b), "LocalFree": ([p], p),
        "GetCurrentProcess": ([], p),
    }
    for name, (args, result) in signatures.items():
        method = getattr(k, name)
        method.argtypes, method.restype = args, result
    return k


def component(name):
    if (not isinstance(name, str) or not name or name in {".", ".."}
            or any(c in name for c in "\\/:") or name.rstrip(" .") != name
            or any(ord(c) < 32 or ord(c) == 127 for c in name)
            or PureWindowsPath(name).is_reserved()):
        raise OSError("Windows device, stream, traversal or alias spelling refused")
    return name


def absolute_path(raw):
    spelling = os.fspath(raw)
    path = Path(spelling)
    if (not path.is_absolute() or not re.fullmatch(r"[A-Za-z]:", path.drive)
            or any(p in {".", "..", ""} for p in re.split(r"[\\/]", spelling[3:]) if spelling[3:])):
        raise OSError("custody requires a canonical absolute local-drive path")
    for part in path.parts[1:]:
        component(part)
    return path


def handle_name(k, handle):
    size = k.GetFinalPathNameByHandleW(handle, None, 0, 0)
    if not 0 < size <= 32768:
        raise OSError("canonical handle name unavailable or unbounded")
    buffer = ctypes.create_unicode_buffer(size)
    length = k.GetFinalPathNameByHandleW(handle, buffer, size, 0)
    if not 0 < length < size or not re.match(r"^\\\\\?\\[A-Za-z]:\\", buffer.value):
        raise OSError("canonical handle namespace is unsupported")
    return Path(buffer.value[4:])


def info(k, handle):
    value, basic = FileInfo(), BasicInfo()
    if not k.GetFileInformationByHandle(handle, ctypes.byref(value)):
        raise ctypes.WinError(ctypes.get_last_error())
    if not k.GetFileInformationByHandleEx(handle, 0, ctypes.byref(basic), ctypes.sizeof(basic)):
        raise ctypes.WinError(ctypes.get_last_error())
    if value.attributes != basic.attributes or value.attributes & 0x400:
        raise OSError("reparse point or changing attributes refused")
    directory = bool(value.attributes & 0x10)
    return SimpleNamespace(st_dev=value.volume, st_ino=(value.index_high << 32) | value.index_low,
        st_mode=(stat.S_IFDIR | 0o777) if directory else (stat.S_IFREG | (0o444 if value.attributes & 1 else 0o666)),
        st_size=(value.size_high << 32) | value.size_low, st_nlink=value.links,
        st_mtime_ns=basic.write * 100, st_ctime_ns=basic.change * 100,
        st_file_attributes=value.attributes)


def identity(value, *, directory=False):
    if directory:
        if not stat.S_ISDIR(value.st_mode):
            raise OSError("retained ancestor is not a directory")
        return value.st_dev, value.st_ino, value.st_mode, value.st_file_attributes
    if not stat.S_ISREG(value.st_mode) or value.st_nlink != 1:
        raise OSError("file is not a single-link regular object")
    return tuple(getattr(value, key) for key in
                 ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns", "st_file_attributes"))


@contextlib.contextmanager
def creation_security(k):
    """Claim-run output custody route: create owner-only protected permissions.

    Never change the security descriptor of an existing object.
    """
    api = ctypes.WinDLL("advapi32", use_last_error=True)
    fn = api.ConvertStringSecurityDescriptorToSecurityDescriptorW
    fn.argtypes = [ctypes.c_wchar_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
    fn.restype = ctypes.c_int
    descriptor = ctypes.c_void_p()
    if not fn("D:P(A;;FA;;;OW)", 1, ctypes.byref(descriptor), None):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        yield descriptor
    finally:
        k.LocalFree(descriptor)


def open_child(k, parent, name, *, directory=False, create=False, writable=False, shared_write=False):
    component(name)
    native = ctypes.WinDLL("ntdll")
    native.NtCreateFile.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_ulong,
        ctypes.POINTER(ObjectAttributes), ctypes.POINTER(IoStatus), ctypes.c_void_p,
        ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_ulong]
    native.NtCreateFile.restype = ctypes.c_long
    native.RtlNtStatusToDosError.argtypes = [ctypes.c_long]
    native.RtlNtStatusToDosError.restype = ctypes.c_ulong
    buffer = ctypes.create_unicode_buffer(name)
    length = len(name.encode("utf-16-le"))
    if length > 65532:
        raise OSError("component exceeds native length bound")
    text = UnicodeString(length, length + 2, ctypes.cast(buffer, ctypes.c_void_p))
    with creation_security(k) if create else contextlib.nullcontext(None) as security:
        attributes = ObjectAttributes(ctypes.sizeof(ObjectAttributes), parent, ctypes.pointer(text),
                                      0x40 | 0x1000, security, None)
        handle, status = ctypes.c_void_p(), IoStatus()
        access = 0xC0120081 if writable else (0x80100000 if directory else 0x00120081)
        result = native.NtCreateFile(ctypes.byref(handle), access, ctypes.byref(attributes), ctypes.byref(status),
            None, 0x80, 3 if directory or shared_write else 1, 2 if create else 1,
            0x20 | 0x00200000 | (1 if directory else 0x40), None, 0)
    if result < 0:
        raise ctypes.WinError(native.RtlNtStatusToDosError(result))
    return handle.value


class Directory:
    def __init__(self, path, *, create=False, create_root=None):
        self.path, self.k, self.nodes = absolute_path(path), kernel(), []
        self.closed = False
        if self.k.GetDriveTypeW(self.path.anchor) != 3:
            raise OSError("custody requires a fixed local volume")
        allowed = absolute_path(create_root) if create_root is not None else self.path
        try:
            handle = self.k.CreateFileW(self.path.anchor, 0x80120000, 3, None, 3, 0x02200000, None)
            if handle == ctypes.c_void_p(-1).value:
                raise ctypes.WinError(ctypes.get_last_error())
            self.nodes.append((handle, Path(self.path.anchor), None))
            self.nodes[-1] = (handle, Path(self.path.anchor), identity(info(self.k, handle), directory=True))
            if str(handle_name(self.k, handle)).casefold() != str(Path(self.path.anchor)).casefold():
                raise OSError('volume root aliases a different canonical name')
            filesystem = ctypes.create_unicode_buffer(64)
            if (not self.k.GetVolumeInformationByHandleW(handle, None, 0, None, None, None, filesystem, 64)
                    or filesystem.value != "NTFS"):
                raise OSError("canonical Windows custody is qualified only for NTFS")
            for part in self.path.parts[1:]:
                self.verify()
                child_path = self.nodes[-1][1] / part
                try:
                    child = open_child(self.k, self.handle, part, directory=True)
                except FileNotFoundError:
                    if not create or not child_path.is_relative_to(allowed):
                        raise
                    try:
                        child = open_child(self.k, self.handle, part, directory=True, create=True)
                    except FileExistsError:
                        child = open_child(self.k, self.handle, part, directory=True)
                self.nodes.append((child, child_path, None))
                self.nodes[-1] = (child, child_path, identity(info(self.k, child), directory=True))
                if str(handle_name(self.k, child)).casefold() != str(child_path).casefold():
                    raise OSError('directory spelling aliases a different canonical long name')
            self.verify()
        except BaseException:
            self.close()
            raise

    @property
    def handle(self):
        if self.closed or not self.nodes:
            raise OSError("directory custody is closed")
        return self.nodes[-1][0]

    def verify(self):
        if self.closed:
            raise OSError("directory custody is closed")
        for handle, path, expected in self.nodes:
            # Every directory was acquired with GENERIC_READ and no delete
            # sharing. Its canonical long name was checked at acquisition;
            # native rename/delete exclusion keeps that name bound until close.
            # Recheck the full retained object identities and reparse metadata.
            if identity(info(self.k, handle), directory=True) != expected:
                raise OSError("canonical directory identity or attributes changed")

    def names(self):
        self.verify()
        buffer, names, kind = ctypes.create_string_buffer(65536), [], 11
        while True:
            if not self.k.GetFileInformationByHandleEx(self.handle, kind, buffer, len(buffer)):
                code = ctypes.get_last_error()
                if code == 18:  # ERROR_NO_MORE_FILES
                    break
                raise ctypes.WinError(code)
            kind, offset = 10, 0
            while True:
                row = DirectoryInfo.from_buffer(buffer, offset)
                end = offset + DirectoryInfo.name.offset + row.name_length
                if row.name_length % 2 or end > len(buffer):
                    raise OSError("malformed native directory enumeration")
                name = buffer.raw[offset + DirectoryInfo.name.offset:end].decode("utf-16-le", "strict")
                if name not in {".", ".."}:
                    names.append(component(name))
                if len(names) > 16384:
                    raise OSError("directory population exceeds bounded enumeration")
                if not row.next:
                    break
                if row.next < DirectoryInfo.name.offset or offset + row.next >= len(buffer):
                    raise OSError("malformed native directory offset")
                offset += row.next
        self.verify()
        if len(names) != len(set(names)):
            raise OSError("directory population changed during enumeration")
        return names

    def flush(self):
        self.verify()
        if len(self.nodes) < 2:
            raise OSError("volume-root flushing is outside canonical custody")
        parent = self.nodes[-2][0]
        handle = open_child(self.k, parent, self.path.name, directory=True, writable=True)
        try:
            if identity(info(self.k, handle), directory=True) != self.nodes[-1][2]:
                raise OSError("directory flush selected a different object")
            if not self.k.FlushFileBuffers(handle):
                raise ctypes.WinError(ctypes.get_last_error())
            self.verify()
        finally:
            if not self.k.CloseHandle(handle):
                raise OSError("directory flush handle cleanup failed")

    def close(self):
        nodes, self.nodes, self.closed = self.nodes, [], True
        failed = False
        for handle, _, _ in reversed(nodes):
            failed |= not bool(self.k.CloseHandle(handle))
        if failed:
            raise OSError("Windows directory handle cleanup failed")

    def __enter__(self):
        return self

    def __exit__(self, kind, value, traceback):
        try:
            if kind is None:
                self.verify()
        finally:
            self.close()


class File:
    def __init__(self, directory, name, *, maximum=64 * 1024 * 1024,
                 create=False, writable=False, shared_write=False):
        import msvcrt
        self.directory, self.path, self.maximum = directory, directory.path / component(name), maximum
        self.fd, self.handle = None, None
        directory.verify()
        try:
            self.handle = open_child(directory.k, directory.handle, name, create=create,
                                     writable=writable, shared_write=shared_write)
            self.expected = identity(self.stat())
            self.verify()
            self.fd = msvcrt.open_osfhandle(self.handle, os.O_BINARY | (os.O_RDWR if writable else os.O_RDONLY))
        except BaseException:
            self.close()
            raise

    def stat(self):
        value = info(self.directory.k, self.handle)
        identity(value)
        if value.st_size > self.maximum:
            raise OSError("file exceeds bounded allocation")
        return value

    def verify(self, *, changed=False):
        self.directory.verify()
        current = identity(self.stat())
        if ((current[:2] if changed else current) != (self.expected[:2] if changed else self.expected)
                or str(handle_name(self.directory.k, self.handle)).casefold() != str(self.path).casefold()):
            raise OSError("retained file identity, content metadata or canonical name changed")

    def read(self):
        self.verify()
        os.lseek(self.fd, 0, os.SEEK_SET)
        chunks, size = [], 0
        while size <= self.maximum:
            raw = os.read(self.fd, min(1024 * 1024, self.maximum + 1 - size))
            if not raw:
                break
            chunks.append(raw)
            size += len(raw)
        self.verify()
        if size != self.stat().st_size:
            raise OSError("bounded file changed while reading")
        return b"".join(chunks)

    def write(self, data, mode):
        if self.stat().st_size != 0 or len(data) > self.maximum:
            raise OSError("exclusive output is not empty or exceeds the bound")
        remaining = memoryview(data)
        while remaining:
            count = os.write(self.fd, remaining)
            if not count:
                raise OSError("protected write made no progress")
            remaining = remaining[count:]
        k = self.directory.k
        if not k.FlushFileBuffers(self.handle):
            raise ctypes.WinError(ctypes.get_last_error())
        if not mode & stat.S_IWUSR:
            basic = BasicInfo()
            basic.attributes = self.stat().st_file_attributes | 1
            if not k.SetFileInformationByHandle(self.handle, 0, ctypes.byref(basic), ctypes.sizeof(basic)):
                raise ctypes.WinError(ctypes.get_last_error())
            if not k.FlushFileBuffers(self.handle):
                raise ctypes.WinError(ctypes.get_last_error())
        self.verify(changed=True)
        self.expected = identity(self.stat())
        if self.read() != data:
            raise OSError("exclusive output readback differs")
        self.directory.flush()

    def close(self):
        if self.fd is not None:
            fd, self.fd, self.handle = self.fd, None, None
            os.close(fd)
        elif self.handle is not None:
            handle, self.handle = self.handle, None
            if not self.directory.k.CloseHandle(handle):
                raise OSError("Windows file handle cleanup failed")

    def __enter__(self):
        return self

    def __exit__(self, kind, value, traceback):
        try:
            if kind is None:
                self.verify()
        finally:
            self.close()


@contextlib.contextmanager
def lock(path, *, blocking):
    import msvcrt
    path = absolute_path(path)
    # The existing claim writer uses msvcrt.locking on the same first byte.
    with Directory(path.parent, create=True, create_root=path.parent) as parent:
        try:
            held = File(parent, path.name, maximum=1, create=True, writable=True, shared_write=True)
            created = True
        except FileExistsError:
            held = File(parent, path.name, maximum=1, writable=True, shared_write=True)
            created = False
        locked = False
        try:
            deadline = time.monotonic() + (30 if blocking else 0)
            while True:
                try:
                    os.lseek(held.fd, 0, os.SEEK_SET)
                    msvcrt.locking(held.fd, msvcrt.LK_NBLCK, 1)
                    locked = True
                    break
                except OSError as exc:
                    if exc.errno not in {13, 11, 36} or not blocking or time.monotonic() >= deadline:
                        raise
                    time.sleep(0.02)
            if created:
                held.write(b"\0", 0o600)
            else:
                held.verify(changed=True)
                held.expected = identity(held.stat())
            if held.read() != b"\0":
                raise OSError("coordination gate is not an exact one-byte gate")
            yield
            held.verify()
        finally:
            if locked:
                os.lseek(held.fd, 0, os.SEEK_SET)
                msvcrt.locking(held.fd, msvcrt.LK_UNLCK, 1)
            held.close()


def peak_process_memory():
    """Peak working-set bytes of this process only; never process-tree evidence."""
    class Counters(ctypes.Structure):
        _fields_ = [("size", ctypes.c_ulong), ("faults", ctypes.c_ulong)] + [
            (name, ctypes.c_size_t) for name in ("peak", "working", "peak_paged", "paged",
                "peak_nonpaged", "nonpaged", "pagefile", "peak_pagefile")]
    api, k = ctypes.WinDLL("psapi", use_last_error=True), kernel()
    api.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
    api.GetProcessMemoryInfo.restype = ctypes.c_int
    counters = Counters()
    counters.size = ctypes.sizeof(counters)
    if not api.GetProcessMemoryInfo(k.GetCurrentProcess(), ctypes.byref(counters), counters.size) or not counters.peak:
        raise OSError("native process peak-memory observation unavailable")
    return counters.peak


_GIT_SCOPE = contextvars.ContextVar('canonical_git_read_scope', default=None)


class GitReadScope:
    """One operation's custody with a fresh Git process per object lookup.

    A process is closed after its bounded info/content exchange: Git's internal
    packed-object caches must never cross separate readbacks. Windows refs use
    native directory/config custody and exact loose/packed grammar. The existing
    owner still performs every expected-old CAS and consequential readback.
    """
    def __init__(self, repo, executable, environment):
        self.repo, self.executable, self.environment = Path(repo).absolute(), executable, dict(environment)
        self.process = None
        self.worker = None
        self.native_handles = []
        self.common = None

    def command(self, *args):
        return [self.executable, '--no-replace-objects', '-C', str(self.repo),
                '-c', 'core.hooksPath=' + os.devnull, *args]

    def read_command(self, *args):
        try:
            return subprocess.run(self.command(*args), env=self.environment,
                                  capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError) as exc:
            raise OSError('bounded Git observation failed or timed out; no effect authority') from exc

    def start(self):
        if self.process is None:
            self.process = subprocess.Popen(self.command('cat-file', '--batch-command'),
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                env=self.environment, close_fds=True)

    def exchange(self, command, oid, maximum, *, contents=False, blob_only=True):
        self.start()
        answer = []

        def read():
            try:
                self.process.stdin.write(command.encode('ascii') + b' ' + oid.encode('ascii') + b'\n')
                self.process.stdin.flush()
                header = self.process.stdout.readline(128)
                match = re.fullmatch(rb'([0-9a-f]{40}) (blob|tree|commit|tag) ([0-9]+)\n', header)
                if match is None or match[1].decode('ascii') != oid or blob_only and match[2] != b'blob':
                    raise OSError('Git object reader refused a missing, non-blob or mismatched object')
                size = int(match[3])
                if size > maximum:
                    raise OSError('Git object exceeds the bounded read')
                if not contents:
                    answer.append(size)
                    return
                body = self.process.stdout.read(size + 1)
                if (len(body) != size + 1 or body[-1:] != b'\n'
                        or hashlib.sha1(b'blob ' + str(size).encode('ascii') + b'\0' + body[:-1]).hexdigest() != oid):
                    raise OSError('Git object byte readback differs from its exact identity')
                answer.append(body[:-1])
            except BaseException as exc:
                answer.append(exc)

        self.worker = threading.Thread(target=read, daemon=True)
        self.worker.start()
        self.worker.join(30)
        if self.worker.is_alive():
            self.close_process()
            raise OSError('Git object read timed out; no effect or retry authority')
        self.worker = None
        if not answer or isinstance(answer[0], BaseException):
            self.close_process()
            raise OSError('Git object reader failed exact bounded readback') from (answer[0] if answer else None)
        return answer[0]

    def object(self, oid, maximum):
        if not isinstance(oid, str) or re.fullmatch(r'[0-9a-f]{40}', oid) is None or type(maximum) is not int or maximum < 0:
            raise OSError('invalid bounded object request')
        try:
            size = self.exchange('info', oid, maximum)
            # Check size before requesting content, then check it and the hash
            # again. Close before any subsequent readback can reuse Git caches.
            return self.exchange('contents', oid, size, contents=True)
        finally:
            self.close_process()

    def _native_ref_custody(self):
        if self.common is not None:
            for held in self.native_handles:
                held.verify()
            return
        result = self.read_command('rev-parse', '--path-format=absolute',
                                  '--git-common-dir', '--git-dir', '--show-object-format', '--show-toplevel')
        rows = result.stdout.decode('utf-8', 'strict').splitlines()
        if result.returncode or len(rows) != 4 or rows[2] != 'sha1' or Path(rows[3]) != self.repo:
            raise OSError('native ref custody requires the exact SHA-1 repository')
        common, git_dir = absolute_path(rows[0]), absolute_path(rows[1])
        for path in dict.fromkeys((self.repo, common, git_dir)):
            self.native_handles.append(Directory(path))
        # Hold Git's routing/configuration inputs against replacement; no ref
        # value is held or cached across expected-old publication.
        for path in (self.repo / '.git', git_dir / 'commondir', common / 'config'):
            try:
                held_directory = Directory(path)
            except FileNotFoundError:
                if path == self.repo / '.git' or path == git_dir / 'commondir' and git_dir != common:
                    raise OSError('Git routing input disappeared before custody')
                continue
            except NotADirectoryError:
                pass
            else:
                self.native_handles.append(held_directory)
                continue
            try:
                parent = Directory(path.parent)
                try:
                    held = File(parent, path.name)
                except BaseException:
                    parent.close()
                    raise
            except (FileNotFoundError, IsADirectoryError):
                if path == self.repo / '.git' or path == git_dir / 'commondir' and git_dir != common:
                    raise OSError('Git routing input changed during custody')
                continue
            self.native_handles.extend((parent, held))
        storage = self.read_command('config', '--get', 'extensions.refStorage')
        if storage.returncode not in (0, 1) or (storage.returncode == 0 and storage.stdout.strip() not in (b'', b'files')):
            raise OSError('native ref custody requires the files backend')
        repeated = self.read_command('rev-parse', '--path-format=absolute',
            '--git-common-dir', '--git-dir', '--show-object-format', '--show-toplevel')
        if repeated.returncode or repeated.stdout != result.stdout:
            raise OSError('Git routing changed while acquiring native custody')
        self.common = common

    @staticmethod
    def optional_file(path, maximum):
        try:
            with Directory(path.parent) as parent:
                try:
                    with File(parent, path.name, maximum=maximum) as held:
                        return held.read()
                except FileNotFoundError:
                    parent.verify()
                    return None
        except FileNotFoundError:
            return None

    def ref(self, ref):
        return self.refs([ref])[ref]

    def refs(self, refs):
        """One fresh bounded population observation, without ref-value caching.

        Every loose name and the packed population retain before/after physical
        checks. Git independently verifies each present name/object in bounded
        groups; exact absence still uses Git's distinct absence operation.
        Nothing is retained across this observation or an authority CAS.
        """
        if (type(refs) not in (list, tuple) or any(not isinstance(ref, str)
                or not re.fullmatch(r'refs/implementaudit/[A-Za-z0-9._/-]+', ref)
                or '..' in ref or any(not part or part.endswith('.lock') for part in ref.split('/'))
                for ref in refs) or len(refs) != len(set(refs))):
            raise OSError('ref escapes the exact authority namespace')
        if not refs:
            return {}
        if len(refs) > 64:
            # Bound the simultaneous loose-file population as well as argv.
            # Each group is independently fresh; the caller's real CAS still
            # verifies the complete expected-old population atomically.
            result = {}
            for offset in range(0, len(refs), 64):
                result.update(self.refs(refs[offset:offset + 64]))
            return result
        self._native_ref_custody()
        loose = {ref: self.optional_file(self.common.joinpath(*ref.split('/')), 4096) for ref in refs}
        packed = self.optional_file(self.common / 'packed-refs', 64 * 1024 * 1024)
        packed_oids = dict.fromkeys(refs)
        encoded = {ref.encode('ascii'): ref for ref in refs}
        if packed is not None:
            if packed and not packed.endswith(b'\n') or b'\r' in packed:
                raise OSError('packed ref population is incomplete')
            can_peel = False
            for row in packed.split(b'\n')[:-1]:
                if row.startswith(b'#'):
                    can_peel = False
                    continue
                if re.fullmatch(rb'\^[0-9a-f]{40}', row):
                    if not can_peel:
                        raise OSError('packed ref has an orphan or repeated peeled record')
                    can_peel = False
                    continue
                match = re.fullmatch(rb'([0-9a-f]{40}) (refs/[^\x00-\x20\x7f]+)', row)
                if match is None:
                    raise OSError('packed ref population is malformed')
                can_peel = True
                if match[2] in encoded:
                    ref = encoded[match[2]]
                    if packed_oids[ref] is not None:
                        raise OSError('packed authority ref is duplicated')
                    packed_oids[ref] = match[1].decode('ascii')
        result = {}
        for ref, raw in loose.items():
            if raw is not None:
                if re.fullmatch(rb'[0-9a-f]{40}\n', raw) is None:
                    raise OSError('loose authority ref is symbolic, broken or malformed')
                result[ref] = raw[:-1].decode('ascii')
            else:
                result[ref] = packed_oids[ref]
        # Git remains the semantic ref reader: physical grammar alone cannot
        # establish object existence or Git's packed-ref ordering/interpretation.
        present = [ref for ref in refs if result[ref] is not None]
        while present:
            group, characters = [], 0
            while present and len(group) < 64:
                if group and characters + len(present[0]) > 12000:
                    break
                ref = present.pop(0)
                group.append(ref)
                characters += len(ref) + 1
            checked = self.read_command('show-ref', '--verify', '--', *group)
            found = {}
            if checked.returncode or not checked.stdout.endswith(b'\n') or b'\r' in checked.stdout:
                raise OSError('Git refused the physical authority ref or its current object')
            for row in checked.stdout.split(b'\n')[:-1]:
                match = re.fullmatch(rb'([0-9a-f]{40}) (refs/implementaudit/[A-Za-z0-9._/-]+)', row)
                if match is None:
                    raise OSError('Git returned a malformed authority-ref population')
                ref = match[2].decode('ascii')
                if ref not in group or ref in found:
                    raise OSError('Git returned a foreign or duplicate authority ref')
                found[ref] = match[1].decode('ascii')
            if found != {ref: result[ref] for ref in group}:
                raise OSError('Git refused the complete physical authority-ref population')
        for ref in refs:
            if result[ref] is not None:
                continue
            checked = self.read_command('show-ref', '--exists', ref)
            if checked.returncode != 2 or checked.stdout:
                raise OSError('Git did not confirm exact authority-ref absence')
        if (any(self.optional_file(self.common.joinpath(*ref.split('/')), 4096) != loose[ref] for ref in refs)
                or self.optional_file(self.common / 'packed-refs', 64 * 1024 * 1024) != packed):
            raise OSError('authority ref population changed during Git readback')
        for held in self.native_handles:
            held.verify()
        return result

    def close_process(self):
        if self.process is not None:
            process, self.process = self.process, None
            try:
                if self.worker is not None and self.worker.is_alive():
                    if process.poll() is None:
                        process.kill()
                else:
                    try:
                        process.stdin.close()
                    except OSError:
                        pass  # A dead read-only child can close its pipe first.
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                if self.worker is not None:
                    self.worker.join(5)
                    if self.worker.is_alive():
                        raise OSError('owned Git reader did not terminate')
            finally:
                for stream in (process.stdin, process.stdout):
                    try:
                        stream.close()
                    except OSError:
                        pass
                self.worker = None

    def close(self):
        try:
            self.close_process()
        finally:
            handles, self.native_handles = self.native_handles, []
            for held in reversed(handles):
                held.close()


@contextlib.contextmanager
def git_scope(repo, executable, environment):
    current = _GIT_SCOPE.get()
    if current is not None:
        if current.repo != Path(repo).absolute() or current.executable != executable:
            raise OSError('nested Git custody changed the repository or executable binding')
        # A nested deterministic helper reuses the caller owner's already fixed
        # process environment; it cannot replace it or start a second reader.
        yield current
        return
    selected = GitReadScope(repo, executable, environment)
    token = _GIT_SCOPE.set(selected)
    try:
        yield selected
    finally:
        try:
            selected.close()
        finally:
            _GIT_SCOPE.reset(token)


def read_object(repo, oid, maximum):
    selected = _GIT_SCOPE.get()
    if selected is None:
        return NotImplemented
    if selected.repo != Path(repo).absolute():
        raise OSError('object request changed its repository binding')
    return selected.object(oid, maximum)


def current_ref(repo, ref):
    selected = _GIT_SCOPE.get()
    if selected is None or os.name != 'nt':
        return NotImplemented
    if selected.repo != Path(repo).absolute():
        raise OSError('ref request changed its repository binding')
    return selected.ref(ref)


def current_refs(repo, refs):
    selected = _GIT_SCOPE.get()
    if selected is None or os.name != 'nt':
        return NotImplemented
    if selected.repo != Path(repo).absolute():
        raise OSError('ref request changed its repository binding')
    return selected.refs(refs)
