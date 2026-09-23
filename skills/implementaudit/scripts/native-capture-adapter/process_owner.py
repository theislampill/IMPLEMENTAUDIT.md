"""Retained process/job owner dependency closure; no standalone launcher."""
import argparse

import ctypes

from ctypes import wintypes

import datetime

import hashlib

import json

import os

from pathlib import Path

import stat

import subprocess

import threading

import time

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def no_reparse(path):
    for node in (path, *path.parents):
        if node.exists() and (node.is_symlink() or
                getattr(node.lstat(), 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
            raise RuntimeError('reparse path is not an owned evidence path')

def file_record(path, max_bytes=None):
    no_reparse(path)
    before = path.stat()
    if max_bytes is not None and before.st_size > max_bytes:
        return {'path': str(path), 'bytes': before.st_size, 'digest': None,
                'digest_not_read': 'FILE_EXCEEDS_CAPTURE_BOUND'}
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(65536), b''):
            digest.update(chunk)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError('evidence changed while being hashed')
    return {'path': str(path), 'bytes': after.st_size, 'sha256': digest.hexdigest()}

def write_json_new(path, value):
    raw = (json.dumps(value, indent=2) + '\n').encode('utf8')
    with path.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}

class IO_COUNTERS(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in
                ('ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount',
                 'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]

class BASIC_LIMIT(ctypes.Structure):
    _fields_ = [('PerProcessUserTimeLimit', ctypes.c_longlong), ('PerJobUserTimeLimit', ctypes.c_longlong),
                ('LimitFlags', wintypes.DWORD), ('MinimumWorkingSetSize', ctypes.c_size_t),
                ('MaximumWorkingSetSize', ctypes.c_size_t), ('ActiveProcessLimit', wintypes.DWORD),
                ('Affinity', ctypes.c_size_t), ('PriorityClass', wintypes.DWORD), ('SchedulingClass', wintypes.DWORD)]

class EXTENDED_LIMIT(ctypes.Structure):
    _fields_ = [('BasicLimitInformation', BASIC_LIMIT), ('IoInfo', IO_COUNTERS),
                ('ProcessMemoryLimit', ctypes.c_size_t), ('JobMemoryLimit', ctypes.c_size_t),
                ('PeakProcessMemoryUsed', ctypes.c_size_t), ('PeakJobMemoryUsed', ctypes.c_size_t)]

class THREADENTRY32(ctypes.Structure):
    _fields_ = [('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD), ('th32ThreadID', wintypes.DWORD),
                ('th32OwnerProcessID', wintypes.DWORD), ('tpBasePri', wintypes.LONG),
                ('tpDeltaPri', wintypes.LONG), ('dwFlags', wintypes.DWORD)]

class Win32Owner:
    """Unshared job owns only the newly created suspended worker and its descendants."""
    def __init__(self):
        if os.name != 'nt':
            raise RuntimeError('this actual process observer requires Windows')
        self.k = ctypes.WinDLL('kernel32', use_last_error=True)
        signatures = {
            'CreateJobObjectW': ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
            'SetInformationJobObject': ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD], wintypes.BOOL),
            'AssignProcessToJobObject': ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
            'QueryInformationJobObject': ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p], wintypes.BOOL),
            'TerminateJobObject': ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
            'TerminateProcess': ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
            'GetProcessTimes': ([wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p], wintypes.BOOL),
            'CreateToolhelp32Snapshot': ([wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
            'Thread32First': ([wintypes.HANDLE, ctypes.POINTER(THREADENTRY32)], wintypes.BOOL),
            'Thread32Next': ([wintypes.HANDLE, ctypes.POINTER(THREADENTRY32)], wintypes.BOOL),
            'OpenThread': ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
            'ResumeThread': ([wintypes.HANDLE], wintypes.DWORD),
            'CloseHandle': ([wintypes.HANDLE], wintypes.BOOL),
        }
        for name, (args, result) in signatures.items():
            getattr(self.k, name).argtypes = args
            getattr(self.k, name).restype = result
        self.job = self.k.CreateJobObjectW(None, None)
        self.ok(self.job, 'create owned job')
        info = EXTENDED_LIMIT()
        info.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        try:
            self.ok(self.k.SetInformationJobObject(self.job, 9, ctypes.byref(info), ctypes.sizeof(info)), 'set owned job containment')
        except BaseException:
            self.k.CloseHandle(self.job)
            self.job = None
            raise

    @staticmethod
    def ok(result, operation):
        if not result:
            raise OSError(ctypes.get_last_error(), operation)

    def creation_identity(self, process):
        times = [wintypes.FILETIME() for _ in range(4)]
        self.ok(self.k.GetProcessTimes(int(process._handle), *(ctypes.byref(t) for t in times)), 'read retained process creation time')
        ticks = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
        created = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=ticks // 10)
        return {'pid': process.pid, 'creation_filetime_100ns': ticks, 'creation_utc': created.isoformat(),
                'identity_source': 'GetProcessTimes on retained Popen process handle'}

    def assign(self, process):
        self.ok(self.k.AssignProcessToJobObject(self.job, int(process._handle)), 'assign exact suspended worker to owned job')

    def resume_initial_thread(self, process):
        snapshot = self.k.CreateToolhelp32Snapshot(0x00000004, 0)
        if snapshot == ctypes.c_void_p(-1).value:
            raise OSError(ctypes.get_last_error(), 'snapshot initial worker thread')
        ids = []
        try:
            entry = THREADENTRY32(); entry.dwSize = ctypes.sizeof(entry)
            result = self.k.Thread32First(snapshot, ctypes.byref(entry))
            while result:
                if entry.th32OwnerProcessID == process.pid:
                    ids.append(entry.th32ThreadID)
                result = self.k.Thread32Next(snapshot, ctypes.byref(entry))
            if ctypes.get_last_error() != 18:  # ERROR_NO_MORE_FILES
                raise OSError(ctypes.get_last_error(), 'enumerate initial worker thread')
        finally:
            self.ok(self.k.CloseHandle(snapshot), 'close thread snapshot handle')
        if len(ids) != 1:
            raise RuntimeError('suspended new worker does not have one exact initial thread')
        thread = self.k.OpenThread(0x0002, False, ids[0])  # THREAD_SUSPEND_RESUME
        self.ok(thread, 'open initial worker thread')
        try:
            previous = self.k.ResumeThread(thread)
            if previous != 1:
                raise RuntimeError('initial worker suspension count was not exactly one')
        finally:
            self.ok(self.k.CloseHandle(thread), 'close initial worker thread handle')
        return ids[0]

    def process_ids(self):
        # JobObjectBasicProcessIdList, bounded to 4096 owned process identifiers.
        buffer = ctypes.create_string_buffer(8 + 4096 * ctypes.sizeof(ctypes.c_size_t))
        self.ok(self.k.QueryInformationJobObject(self.job, 3, buffer, len(buffer), None), 'query owned job process membership')
        assigned, count = (wintypes.DWORD * 2).from_buffer(buffer)
        if count > 4096 or assigned != count:
            raise RuntimeError('owned job process population exceeded or changed during observation')
        values = (ctypes.c_size_t * count).from_buffer(buffer, 8)
        return sorted(int(v) for v in values)

    def terminate(self):
        self.ok(self.k.TerminateJobObject(self.job, 0xC0DE0001), 'contain only owned job processes')

    def close(self):
        if self.job is not None:
            self.ok(self.k.CloseHandle(self.job), 'close owned job handle')
            self.job = None
