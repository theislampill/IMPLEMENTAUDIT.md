"""Bounded ordinary-file acquisition; no POSIX custody equivalence claim.

Windows pins every ancestor with a no-delete-sharing handle, opens the leaf
without following reparse points, rejects ADS and multi-link files, and compares
named/descriptor bookends. This module never changes ACLs or grants privacy.
"""
import contextlib
import os
from pathlib import Path
import stat


def need(value, code):
    if not value:
        raise ValueError(code)


def mark(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
            s.st_mtime_ns, s.st_ctime_ns)


def canonical(path):
    p = Path(path)
    need(p.is_absolute() and '..' not in p.parts and p.resolve(strict=True) == p,
         'CANONICAL_PATH_REQUIRED')
    if os.name == 'nt':
        need(p.drive and not str(p).startswith('\\\\') and
             all(':' not in x for x in p.parts[1:]), 'LOCAL_PATH_NO_ADS')
    return p


if os.name == 'nt':
    import ctypes
    from ctypes import wintypes as W
    import msvcrt
    K = ctypes.WinDLL('kernel32', use_last_error=True)
    K.CreateFileW.argtypes = (W.LPCWSTR, W.DWORD, W.DWORD, W.LPVOID,
                              W.DWORD, W.DWORD, W.HANDLE)
    K.CreateFileW.restype = W.HANDLE
    K.CloseHandle.argtypes = (W.HANDLE,)
    K.CloseHandle.restype = W.BOOL
    K.GetFileInformationByHandleEx.argtypes = (W.HANDLE, ctypes.c_int,
                                               W.LPVOID, W.DWORD)
    K.GetFileInformationByHandleEx.restype = W.BOOL
    class AttributeTag(ctypes.Structure):
        _fields_ = [('attributes', W.DWORD), ('tag', W.DWORD)]

    def handle(path, directory=False):
        # OPEN_EXISTING, OPEN_REPARSE_POINT. Ancestors remain pinned until
        # payload closing validation, preventing a directory rename/swap.
        access = 0 if directory else 0x80000000
        share = 3 if directory else 1
        flags = 0x00200000 | (0x02000000 if directory else 0)
        h = K.CreateFileW(str(path), access, share, None, 3, flags, None)
        if h == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        tag = AttributeTag()
        try:
            if not K.GetFileInformationByHandleEx(h, 9, ctypes.byref(tag), ctypes.sizeof(tag)):
                raise ctypes.WinError(ctypes.get_last_error())
            need(not tag.attributes & 0x400, 'REPARSE_POINT_REFUSED')
            need(bool(tag.attributes & 0x10) == directory, 'PHYSICAL_TYPE_REFUSED')
            return h
        except BaseException:
            K.CloseHandle(h)
            raise


def read_file(path, maximum=4 * 1024**2):
    need(type(maximum) is int and maximum >= 0, 'READ_LIMIT')
    p = canonical(path)
    with contextlib.ExitStack() as stack:
        for parent in reversed(p.parents):
            s = parent.lstat()
            need(stat.S_ISDIR(s.st_mode) and not parent.is_symlink() and
                 not getattr(s, 'st_file_attributes', 0) & 0x400, 'ANCESTOR_REFUSED')
            if os.name == 'nt':
                h = handle(parent, True)
                stack.callback(K.CloseHandle, h)
        before = p.lstat()
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             0 <= before.st_size <= maximum and not p.is_symlink() and
             not getattr(before, 'st_file_attributes', 0) & 0x400, 'ORDINARY_SINGLE_FILE_BOUND')
        if os.name == 'nt':
            h = handle(p)
            try:
                fd = msvcrt.open_osfhandle(h, os.O_RDONLY | os.O_BINARY)
            except BaseException:
                K.CloseHandle(h)
                raise
        else:
            fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
        stack.callback(os.close, fd)
        need(mark(os.fstat(fd)) == mark(before), 'OPEN_IDENTITY_CHANGED')
        chunks, count = [], 0
        while True:
            chunk = os.read(fd, min(65536, maximum + 1 - count))
            if not chunk:
                break
            chunks.append(chunk)
            count += len(chunk)
            need(count <= maximum, 'READ_BOUND_EXCEEDED')
        need(count == before.st_size and mark(os.fstat(fd)) == mark(before) == mark(p.lstat()),
             'CLOSING_IDENTITY_CHANGED')
        return b''.join(chunks)
