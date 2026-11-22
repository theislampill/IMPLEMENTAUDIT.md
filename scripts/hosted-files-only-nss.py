#!/usr/bin/python3.12
"""Finite ordinary hosted NSS preparation; no provider/original acceptance.

The public entry point fixes /etc, UID/GID zero, and one hosted image. The file
lease also supports disposable filesystem fixtures for source-only controls.
An atomic exchange retains the original inode as the backup. No path is deleted:
name observations cannot exclude a concurrent privileged replacement. Original
target restoration is separate from the unqualified residual left for VM disposal.
"""
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat

MAX_BYTES = 65536
TARGET = 'nsswitch.conf'
IMAGE = {'ImageOS': 'ubuntu24', 'ImageVersion': '20261116.376.1'}

def files_only_bytes(raw):
    """Change only one supported passwd service list; preserve other bytes."""
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_BYTES or b'\0' in raw or b'\r' in raw:
        raise ValueError('unsupported bounded NSS bytes')
    raw.decode('ascii', 'strict')
    lines = raw.splitlines(keepends=True)
    selected = [i for i, line in enumerate(lines)
                if line.split(b'#', 1)[0].partition(b':')[0].strip() == b'passwd']
    if len(selected) != 1:
        raise ValueError('exactly one passwd NSS row required')
    index = selected[0]
    match = re.fullmatch(rb'([ \t]*passwd[ \t]*:[ \t]*)(files(?:[ \t]+systemd)?)([ \t]*(?:#[^\n]*)?)(\n?)', lines[index])
    if match is None:
        raise ValueError('unsupported passwd NSS service/action layout')
    lines[index] = match[1] + b'files' + match[3] + match[4]
    return b''.join(lines)

def _identity(value):
    return dict(dev=value.st_dev, ino=value.st_ino, mode=value.st_mode,
                links=value.st_nlink, bytes=value.st_size, uid=value.st_uid,
                gid=value.st_gid, mtime_ns=value.st_mtime_ns, ctime_ns=value.st_ctime_ns)

def _stable(value):
    # renameat2 changes ctime. It cannot be restored and is reported explicitly.
    return {k: v for k, v in value.items() if k != 'ctime_ns'}

def _pin(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())

def _exchange(parent, left, right):
    libc = ctypes.CDLL(None, use_errno=True)
    function = getattr(libc, 'renameat2', None)
    if function is None:
        raise ValueError('atomic renameat2 exchange is unavailable')
    function.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    function.restype = ctypes.c_int
    if function(parent, os.fsencode(left), parent, os.fsencode(right), 2) != 0:
        error = ctypes.get_errno()
        raise OSError(error, 'atomic NSS exchange failed')

class FilesOnlyNSSLease:
    """Hold original and replacement descriptors for one bounded continuation."""
    def __init__(self, parent, receipt, *, expected_uid, expected_gid):
        self.path = Path(parent).absolute()
        self.receipt_path = Path(receipt).absolute()
        self.uid, self.gid = expected_uid, expected_gid
        self.parent = self.original = self.replacement = self.receipt = None
        self.backup_name = None
        self.original_raw = self.replacement_raw = None
        self.original_open = self.replacement_open = None
        self.active_original = self.active_replacement = None
        self.replacement_created = None
        self.entered = False
        self.parent_anchor = None
        self.record = dict(schema='g132.hosted-files-only-nss.v2', authority='NONE',
                           state='NEW', original_execution=False, restoration_verified=False,
                           original_bytes_exported=False, ctime_restoration_claim=False,
                           cleanup_complete=False, backup_removed=False,
                           replacement_deletion_attempted=False,
                           restoration_scope='CLOSING_ORIGINAL_TARGET_SNAPSHOT_ONLY',
                           replacement_cleanup=dict(disposition='NONE_ALLOCATED'))

    def _parent_current(self):
        fd = os.fstat(self.parent)
        path = os.lstat(self.path)
        fields = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_uid, s.st_gid)
        if fields(fd) != self.parent_anchor or fields(path) != self.parent_anchor:
            raise ValueError('NSS parent custody changed')

    def _read(self, fd):
        before = _identity(os.fstat(fd))
        if (not stat.S_ISREG(before['mode']) or stat.S_IMODE(before['mode']) != 0o644
                or before['links'] != 1 or before['uid'] != self.uid or before['gid'] != self.gid
                or not 0 < before['bytes'] <= MAX_BYTES or os.listxattr(fd)):
            raise ValueError('NSS file kind/mode/owner/link/metadata is unsupported')
        raw = os.pread(fd, MAX_BYTES + 1, 0)
        if len(raw) != before['bytes'] or _identity(os.fstat(fd)) != before:
            raise ValueError('NSS held bytes changed during readback')
        return raw, before

    def _named(self, name, fd):
        return _identity(os.stat(name, dir_fd=self.parent, follow_symlinks=False)) == _identity(os.fstat(fd))

    def _store(self, state):
        self.record['state'] = state
        if self.receipt is None:
            return
        raw = (json.dumps(self.record, sort_keys=True, separators=(',', ':')) + '\n').encode()
        if len(raw) > 16384:
            raise ValueError('NSS receipt exceeds fixed bound')
        os.ftruncate(self.receipt, 0)
        offset = 0
        while offset < len(raw):
            count = os.pwrite(self.receipt, raw[offset:], offset)
            if count <= 0:
                raise ValueError('NSS receipt write stalled')
            offset += count
        os.fsync(self.receipt)
        if os.pread(self.receipt, len(raw) + 1, 0) != raw:
            raise ValueError('NSS receipt readback differs')

    def __enter__(self):
        try:
            self.parent = os.open(self.path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            parent = os.fstat(self.parent)
            self.parent_anchor = (parent.st_dev, parent.st_ino, parent.st_mode, parent.st_uid, parent.st_gid)
            if (parent.st_uid != self.uid or parent.st_gid != self.gid or parent.st_mode & 0o022
                    or os.listxattr(self.parent)):
                raise ValueError('NSS parent owner/mode/metadata is unsupported')
            self._parent_current()
            receipt_parent = os.open(self.receipt_path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            try:
                rp = os.fstat(receipt_parent)
                if rp.st_uid != self.uid or rp.st_gid != self.gid or rp.st_mode & 0o077:
                    raise ValueError('NSS receipt parent is not privately owned')
                self.receipt = os.open(self.receipt_path.name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=receipt_parent)
                os.fchmod(self.receipt, 0o600)
                os.fsync(receipt_parent)
            finally:
                os.close(receipt_parent)
            self.original = os.open(TARGET, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=self.parent)
            fcntl.flock(self.original, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.original_raw, self.original_open = self._read(self.original)
            if not self._named(TARGET, self.original):
                raise ValueError('NSS opening path is not the held original')
            self.replacement_raw = files_only_bytes(self.original_raw)
            self.record.update(opening=dict(identity=self.original_open, **_pin(self.original_raw)),
                               prepared=_pin(self.replacement_raw), parent=str(self.path))
            self._store('OPENING_BOUND_NO_EFFECT')
            if self.original_raw == self.replacement_raw:
                self.active_original = self.original_open
                self._store('ACTIVE_ALREADY_FILES_ONLY')
                self.entered = True
                return self
            self.backup_name = '.implementaudit-g132-nss-' + secrets.token_hex(16)
            self.record['backup_name'] = self.backup_name
            self.replacement = os.open(self.backup_name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o644, dir_fd=self.parent)
            os.fchmod(self.replacement, 0o644)
            self.replacement_created = _identity(os.fstat(self.replacement))
            offset = 0
            while offset < len(self.replacement_raw):
                count = os.pwrite(self.replacement, self.replacement_raw[offset:], offset)
                if count <= 0:
                    raise ValueError('NSS exclusive replacement write stalled')
                offset += count
            os.fsync(self.replacement)
            raw, self.replacement_open = self._read(self.replacement)
            if raw != self.replacement_raw or not self._named(self.backup_name, self.replacement):
                raise ValueError('NSS exclusive replacement readback differs')
            self._parent_current()
            if self._read(self.original) != (self.original_raw, self.original_open) or not self._named(TARGET, self.original):
                raise ValueError('NSS original changed before exchange')
            self._store('EXCHANGE_INTENT_ORIGINAL_AND_REPLACEMENT_HELD')
            _exchange(self.parent, TARGET, self.backup_name)
            os.fsync(self.parent)
            if not self._named(TARGET, self.replacement) or not self._named(self.backup_name, self.original):
                raise ValueError('NSS exchange path readback differs')
            original, self.active_original = self._read(self.original)
            replacement, self.active_replacement = self._read(self.replacement)
            if (original != self.original_raw or replacement != self.replacement_raw
                    or _stable(self.active_original) != _stable(self.original_open)
                    or _stable(self.active_replacement) != _stable(self.replacement_open)):
                raise ValueError('NSS exchange changed protected bytes or metadata')
            self.record['active'] = dict(original=self.active_original, replacement=self.active_replacement)
            self._store('ACTIVE_FILES_ONLY_ORIGINAL_RETAINED')
            self.entered = True
            return self
        except BaseException:
            try:
                self._finish()
            finally:
                self._close()
            raise

    def _finish(self):
        try:
            if self.original_raw is None:
                self._store('REFUSED_NO_EFFECT')
                return
            self._parent_current()
            original, current = self._read(self.original)
            if original != self.original_raw or _stable(current) != _stable(self.original_open):
                raise ValueError('NSS retained original drifted; restoration refused')
            if self.active_original is not None and current != self.active_original:
                raise ValueError('NSS active original metadata drifted')
            uninstalled = False
            if self.replacement is not None and not self.entered and self._named(TARGET, self.original):
                # An owned write failure before exchange has never changed NSS.
                # Receive its bounded prefix, but do not unlink any name. Even a
                # final fstat is not exclusion for the following path operation.
                part = _identity(os.fstat(self.replacement))
                created = self.replacement_created
                keys = ('dev', 'ino', 'mode', 'links', 'uid', 'gid')
                if (created is None or any(part[k] != created[k] for k in keys)
                        or not 0 <= part['bytes'] <= len(self.replacement_raw)
                        or os.listxattr(self.replacement)
                        or os.pread(self.replacement, MAX_BYTES + 1, 0) != self.replacement_raw[:part['bytes']]
                        or not self._named(self.backup_name, self.replacement)
                        or _identity(os.fstat(self.replacement)) != part):
                    raise ValueError('uninstalled owned NSS replacement drifted')
                uninstalled = True
            if self.replacement is not None and not uninstalled:
                replacement, current_new = self._read(self.replacement)
                if (replacement != self.replacement_raw or self.replacement_open is None
                        or _stable(current_new) != _stable(self.replacement_open)
                        or (self.active_replacement is not None and current_new != self.active_replacement)):
                    raise ValueError('NSS owned replacement drifted; restoration refused')
                if self._named(TARGET, self.replacement) and self._named(self.backup_name, self.original):
                    self._store('RESTORE_INTENT')
                    _exchange(self.parent, TARGET, self.backup_name)
                    os.fsync(self.parent)
                if not self._named(TARGET, self.original) or not self._named(self.backup_name, self.replacement):
                    raise ValueError('NSS closing names differ; retain for VM disposal')
            elif self.replacement is None and not self._named(TARGET, self.original):
                raise ValueError('NSS no-op original name drifted')
            raw, closing = self._read(self.original)
            if raw != self.original_raw or _stable(closing) != _stable(self.original_open) or not self._named(TARGET, self.original):
                raise ValueError('NSS closing original readback differs')
            if self.replacement is not None:
                retained = _identity(os.fstat(self.replacement))
                remaining = os.pread(self.replacement, MAX_BYTES + 1, 0)
                if not 0 <= len(remaining) <= MAX_BYTES or len(remaining) != retained['bytes'] or _identity(os.fstat(self.replacement)) != retained:
                    raise ValueError('NSS retained replacement closing snapshot differs')
                self.record['replacement_cleanup'] = dict(
                    disposition='NO_DELETION_VM_DISPOSAL_REQUIRED', held_identity=retained,
                    **_pin(remaining), created_name=self.backup_name,
                    name_matches_held_snapshot=self._named(self.backup_name, self.replacement),
                    name_exclusion_proven=False, remaining_namespace_qualified=False)
            self.record.update(closing=dict(identity=closing, **_pin(raw)), restoration_verified=True,
                               original_inode_restored=True, cleanup_complete=self.replacement is None)
            if self.entered:
                state = 'RESTORED_REPLACEMENT_RETAINED' if self.replacement is not None else 'UNCHANGED_FILES_ONLY_CLOSED'
            else:
                state = 'REFUSED_ORIGINAL_TARGET_PRESENT_REPLACEMENT_RETAINED' if self.replacement is not None else 'REFUSED_INPUT_UNCHANGED'
            self._store(state)
        except BaseException as error:
            self.record.update(restoration_verified=False, cleanup_complete=False,
                               cleanup_error=type(error).__name__ + ': ' + str(error)[:512])
            self._store('RESTORATION_REFUSED_RETAIN_FOR_VM_DISPOSAL')
            raise

    def _close(self):
        for name in ('replacement', 'original', 'receipt', 'parent'):
            fd = getattr(self, name)
            if fd is not None:
                os.close(fd)
                setattr(self, name, None)

    def __exit__(self, kind, error, traceback):
        try:
            self._finish()
        finally:
            self._close()
        return False

def hosted_files_only_nss(receipt):
    """Fixed production effect: ordinary same-boot disposable hosted use only."""
    expected = dict(IMAGE, GITHUB_ACTIONS='true', RUNNER_ENVIRONMENT='github-hosted',
                    GITHUB_REPOSITORY='theislampill/IMPLEMENTAUDIT.md', GITHUB_RUN_ATTEMPT='1')
    if any(os.environ.get(k) != v for k, v in expected.items()) or (os.getuid(), os.geteuid(), os.getgid(), os.getegid()) != (0, 0, 0, 0):
        raise ValueError('NSS preparation requires the exact prospective ordinary hosted image and UID/GID zero')
    return FilesOnlyNSSLease('/etc', receipt, expected_uid=0, expected_gid=0)
