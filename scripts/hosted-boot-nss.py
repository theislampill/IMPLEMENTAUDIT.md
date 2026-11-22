#!/usr/bin/python3.12
"""Exact boot-scoped NSS provisioning for a separate ordinary observation.

Configured administrative state is retained until VM disposal, matching the
original NSS owner's lifecycle. No path is unlinked, overwritten or rolled back.
An atomic exchange preserves both directory entries. A privileged concurrent
writer is not excluded: names and held files are checked snapshots, and any
ambiguous effect remains uncertain. Local descriptor closure is reported apart
from administrative retention; a later reader never recovers predecessor custody.
"""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import stat

BEFORE = dict(bytes=526, sha256='b953df1d0016f515fc052ca6bb0ccd092b8d13c8789c51c4eaef2b0461574e57')
AFTER = dict(bytes=518, sha256='5cde76a7763cef05fea9a086f5db0025459d489ee658a8369602e415e47beff7')
OLD_ROW = b'passwd:         files systemd\n'
NEW_ROW = b'passwd:         files\n'
OPERATION = 'G132_BOOT_NSS_20261122_01'
REF = 'refs/heads/pro/dg16-g132-boot-nss-20261122-01'
WORKFLOW = 'theislampill/IMPLEMENTAUDIT.md/.github/workflows/dg16-g132-boot-nss.yml@' + REF
DISPOSITION = 'RETAIN_CONFIGURED_FILE_UNTIL_VM_DISPOSAL'
MAX_BYTES = 65536
JOURNAL_BYTES = 16384
TARGET = 'nsswitch.conf'
STAGES = ('00-reserved.json', '01-prepared.json', '02-exchange-intent.json', '03-configured.json')


def need(value, reason):
    if not value:
        raise ValueError(reason)


def pin(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def identity(value):
    return dict(dev=value.st_dev, ino=value.st_ino, mode=value.st_mode, links=value.st_nlink,
                bytes=value.st_size, uid=value.st_uid, gid=value.st_gid,
                mtime_ns=value.st_mtime_ns, ctime_ns=value.st_ctime_ns)


def anchor(value):
    return {k: identity(value)[k] for k in ('dev', 'ino', 'mode', 'uid', 'gid')}


def stable(value):
    # renameat2 changes ctime; bytes and all other recorded file fields must hold.
    return {k: v for k, v in value.items() if k != 'ctime_ns'}


def descriptors():
    result = {}
    for name in os.listdir('/proc/self/fd'):
        try:
            value = os.fstat(int(name))
        except OSError:
            continue  # The directory enumeration descriptor is already closed.
        result[name] = (value.st_dev, value.st_ino, value.st_mode)
    return result


def _exchange(left_fd, left, right_fd, right):
    libc = ctypes.CDLL(None, use_errno=True)
    function = getattr(libc, 'renameat2', None)
    need(function is not None, 'atomic exchange unavailable')
    function.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    function.restype = ctypes.c_int
    if function(left_fd, os.fsencode(left), right_fd, os.fsencode(right), 2) != 0:
        raise OSError(ctypes.get_errno(), 'atomic boot NSS exchange failed')


class Refusal(ValueError):
    def __init__(self, record):
        self.record = record
        super().__init__('boot NSS operation refused; retained record describes bounded outcome')


class _BootNSSFiles:
    """Internal disposable-file seam; public entries fix /etc and exact pins."""
    def __init__(self, parent, context, *, expected_uid, expected_gid, before_pin, after_pin):
        self.path = Path(parent).absolute()
        need(self.path.resolve() == self.path, 'boot NSS parent alias refused')
        need(re.fullmatch('[1-9][0-9]{0,19}', context.get('run_id', '')), 'boot NSS run identity refused')
        need(len(canonical(context)) <= 4096, 'boot NSS context exceeds bound')
        self.context = json.loads(canonical(context))
        self.uid, self.gid = expected_uid, expected_gid
        self.before_pin, self.after_pin = dict(before_pin), dict(after_pin)
        self.slot_name = '.implementaudit-g132-boot-nss-' + context['run_id'] + '-1'
        self.slot_path = self.path / self.slot_name
        self.owned = []
        self.records = []
        self.parent = self.slot = None
        self.parent_anchor = self.slot_anchor = None
        self.result = dict(schema='g132.boot-nss.v1', authority='NONE', context=self.context,
                           state='NEW', configured=None, exchange_attempted=False,
                           administrative_disposition=DISPOSITION, vm_disposal_observed=False,
                           original_execution=False, raw_bytes_exported=False,
                           deletion_attempted=False, restoration_attempted=False,
                           descriptor_restoration=False, children_spawned=False,
                           predecessor_process_custody_recovered=False,
                           custody_scope='NAMED_AND_HELD_CLOSING_SNAPSHOTS_NO_PRIVILEGED_WRITER_EXCLUSION',
                           state_directory=self.slot_name, before_pin=self.before_pin, after_pin=self.after_pin)

    def _open(self, name, flags, *, directory=None, mode=0o600):
        fd = os.open(name, flags | os.O_NOFOLLOW | os.O_CLOEXEC, mode, dir_fd=directory)
        self.owned.append(fd)
        return fd

    def _parents(self):
        need(anchor(os.fstat(self.parent)) == self.parent_anchor == anchor(os.lstat(self.path)),
             'boot NSS parent binding changed')
        need(not os.listxattr(self.parent), 'boot NSS parent metadata changed')
        if self.slot is not None:
            need(anchor(os.fstat(self.slot)) == self.slot_anchor
                 == anchor(os.stat(self.slot_name, dir_fd=self.parent, follow_symlinks=False)),
                 'boot NSS private state directory binding changed')
            need(not os.listxattr(self.slot), 'boot NSS private state metadata changed')

    def _open_parents(self, create):
        self.parent = self._open(self.path, os.O_RDONLY | os.O_DIRECTORY)
        value = os.fstat(self.parent)
        need(stat.S_ISDIR(value.st_mode) and not value.st_mode & 0o022
             and (value.st_uid, value.st_gid) == (self.uid, self.gid)
             and not os.listxattr(self.parent), 'boot NSS parent metadata refused')
        self.parent_anchor = anchor(value)
        self._parents()
        if create:
            os.mkdir(self.slot_name, mode=0o700, dir_fd=self.parent)  # Exclusive durable no-replay reservation.
            os.fsync(self.parent)
        self.slot = self._open(self.slot_name, os.O_RDONLY | os.O_DIRECTORY, directory=self.parent)
        value = os.fstat(self.slot)
        need(stat.S_ISDIR(value.st_mode) and stat.S_IMODE(value.st_mode) == 0o700
             and (value.st_uid, value.st_gid) == (self.uid, self.gid)
             and value.st_dev == self.parent_anchor['dev'] and not os.listxattr(self.slot),
             'boot NSS private state directory metadata refused')
        self.slot_anchor = anchor(value)
        self._parents()

    def _read(self, fd, mode, maximum=MAX_BYTES):
        before = identity(os.fstat(fd))
        need(stat.S_ISREG(before['mode']) and stat.S_IMODE(before['mode']) == mode
             and before['links'] == 1 and (before['uid'], before['gid']) == (self.uid, self.gid)
             and 0 < before['bytes'] <= maximum and not os.listxattr(fd),
             'boot NSS bounded regular file metadata refused')
        raw = os.pread(fd, maximum + 1, 0)
        need(len(raw) == before['bytes'] and identity(os.fstat(fd)) == before,
             'boot NSS held bytes changed during readback')
        return raw, before

    def _named(self, directory, name, fd):
        need(identity(os.stat(name, dir_fd=directory, follow_symlinks=False)) == identity(os.fstat(fd)),
             'boot NSS named entry differs from held file')

    def _create(self, name, raw, mode):
        need(0 < len(raw) <= MAX_BYTES, 'boot NSS created file exceeds bound')
        self._parents()
        fd = self._open(name, os.O_RDWR | os.O_CREAT | os.O_EXCL, directory=self.slot, mode=mode)
        os.fchmod(fd, mode)
        offset = 0
        while offset < len(raw):
            count = os.pwrite(fd, raw[offset:], offset)
            need(count > 0, 'boot NSS exclusive write stalled')
            offset += count
        os.fsync(fd)
        os.fsync(self.slot)
        received, value = self._read(fd, mode)
        self._named(self.slot, name, fd)
        need(received == raw, 'boot NSS exclusive file readback differs')
        return fd, value

    def _check_records(self):
        for name, fd, raw, value in self.records:
            need(self._read(fd, 0o600, JOURNAL_BYTES) == (raw, value), 'boot NSS journal drifted')
            self._named(self.slot, name, fd)

    def _append(self, name, payload):
        need(name == STAGES[len(self.records)] if len(self.records) < len(STAGES) else False,
             'boot NSS finite journal order differs')
        self._parents()
        self._check_records()
        previous = None if not self.records else dict(name=self.records[-1][0], **pin(self.records[-1][2]))
        row = dict(schema='g132.boot-nss-journal.v1', name=name, context=self.context,
                   previous=previous, administrative_disposition=DISPOSITION, payload=payload)
        raw = canonical(row)
        need(len(raw) <= JOURNAL_BYTES, 'boot NSS journal exceeds bound')
        fd, value = self._create(name, raw, 0o600)
        self.records.append((name, fd, raw, value))
        self._check_records()

    def _held(self, fd, name, directory, raw, value, mode):
        need(self._read(fd, mode) == (raw, value), 'boot NSS held file drifted')
        self._named(directory, name, fd)

    def _configure(self):
        self._open_parents(create=True)
        self._append(STAGES[0], dict(parent=self.parent_anchor, slot=self.slot_anchor, configured=False))
        original = self._open(TARGET, os.O_RDONLY | os.O_NONBLOCK, directory=self.parent)
        before, opening = self._read(original, 0o644)
        self._named(self.parent, TARGET, original)
        need(pin(before) == self.before_pin and before.count(OLD_ROW) == 1,
             'boot NSS exact original preimage differs')
        after = before.replace(OLD_ROW, NEW_ROW, 1)
        need(pin(after) == self.after_pin, 'boot NSS exact configured postimage differs')
        preimage, private_opening = self._create('preimage.raw', before, 0o600)
        replacement, replacement_opening = self._create('exchange-member', after, 0o644)
        prepared = dict(before_pin=self.before_pin, after_pin=self.after_pin, original=opening,
                        replacement=replacement_opening, private_preimage=private_opening, configured=False)
        self._append(STAGES[1], prepared)
        self._held(original, TARGET, self.parent, before, opening, 0o644)
        self._held(replacement, 'exchange-member', self.slot, after, replacement_opening, 0o644)
        self._held(preimage, 'preimage.raw', self.slot, before, private_opening, 0o600)
        self._append(STAGES[2], dict(configured=None, effect='ATOMIC_EXCHANGE_OUTCOME_UNKNOWN_UNTIL_READBACK'))
        self.result['state'] = 'EXCHANGE_OUTCOME_UNCERTAIN'
        self.result['exchange_attempted'] = True
        # This does not exclude a privileged replacement after the observations.
        # Exchange retains both entries; no destructive path cleanup follows.
        _exchange(self.parent, TARGET, self.slot, 'exchange-member')
        os.fsync(self.parent)
        os.fsync(self.slot)
        before_now, original_now = self._read(original, 0o644)
        after_now, replacement_now = self._read(replacement, 0o644)
        need(before_now == before and after_now == after
             and stable(original_now) == stable(opening)
             and stable(replacement_now) == stable(replacement_opening),
             'boot NSS exchange changed protected bytes or metadata')
        self._held(original, 'exchange-member', self.slot, before, original_now, 0o644)
        self._held(replacement, TARGET, self.parent, after, replacement_now, 0o644)
        self._held(preimage, 'preimage.raw', self.slot, before, private_opening, 0o600)
        self._append(STAGES[3], dict(configured=True, target=replacement_now, retained_original=original_now,
                                    private_preimage=private_opening, before_pin=self.before_pin, after_pin=self.after_pin))
        self._parents()
        self._held(original, 'exchange-member', self.slot, before, original_now, 0o644)
        self._held(replacement, TARGET, self.parent, after, replacement_now, 0o644)
        self._held(preimage, 'preimage.raw', self.slot, before, private_opening, 0o600)
        self._check_records()
        self.result.update(state='CONFIGURED_AND_READ_BACK', configured=True,
                           configured_target=replacement_now, retained_original=original_now,
                           private_preimage=private_opening,
                           journal=[dict(name=name, **pin(raw)) for name, _, raw, _ in self.records])

    def _verify(self):
        self._open_parents(create=False)
        need(set(os.listdir(self.slot)) == set(STAGES) | {'preimage.raw', 'exchange-member'},
             'boot NSS journal incomplete, refused or has an unexpected member')
        rows = []
        for name in STAGES:
            fd = self._open(name, os.O_RDONLY | os.O_NONBLOCK, directory=self.slot)
            raw, value = self._read(fd, 0o600, JOURNAL_BYTES)
            self._named(self.slot, name, fd)
            row = json.loads(raw)
            previous = None if not self.records else dict(name=self.records[-1][0], **pin(self.records[-1][2]))
            need(canonical(row) == raw and set(row) == {'schema', 'name', 'context', 'previous', 'administrative_disposition', 'payload'}
                 and row['schema'] == 'g132.boot-nss-journal.v1' and row['name'] == name
                 and row['context'] == self.context and row['previous'] == previous
                 and row['administrative_disposition'] == DISPOSITION, 'boot NSS journal binding differs')
            self.records.append((name, fd, raw, value))
            rows.append(row['payload'])
        reserved, prepared, intent, configured = rows
        need(reserved == dict(parent=self.parent_anchor, slot=self.slot_anchor, configured=False),
             'boot NSS journal parent/slot identity differs')
        need(intent == dict(configured=None, effect='ATOMIC_EXCHANGE_OUTCOME_UNKNOWN_UNTIL_READBACK')
             and prepared['before_pin'] == configured['before_pin'] == self.before_pin
             and prepared['after_pin'] == configured['after_pin'] == self.after_pin
             and prepared['configured'] is False and configured['configured'] is True
             and stable(prepared['original']) == stable(configured['retained_original'])
             and stable(prepared['replacement']) == stable(configured['target'])
             and prepared['private_preimage'] == configured['private_preimage'],
             'boot NSS journal transition differs')
        held = []
        for directory, name, mode, expected_pin, expected_identity in (
                (self.parent, TARGET, 0o644, self.after_pin, configured['target']),
                (self.slot, 'exchange-member', 0o644, self.before_pin, configured['retained_original']),
                (self.slot, 'preimage.raw', 0o600, self.before_pin, configured['private_preimage'])):
            fd = self._open(name, os.O_RDONLY | os.O_NONBLOCK, directory=directory)
            raw, value = self._read(fd, mode)
            need(pin(raw) == expected_pin and value == expected_identity, 'boot NSS current content/identity differs')
            self._held(fd, name, directory, raw, value, mode)
            held.append((fd, name, directory, raw, value, mode))
        self._parents()
        self._check_records()
        # Retain every opened file through the whole receive and recheck the
        # earlier inputs after the later reads. This is still a snapshot, not
        # exclusion of a future privileged writer.
        for binding in held:
            self._held(*binding)
        self.result.update(state='CONFIGURED_CURRENT_READBACK', configured=True,
                           configured_target=configured['target'], retained_original=configured['retained_original'],
                           private_preimage=configured['private_preimage'],
                           journal=[dict(name=name, **pin(raw)) for name, _, raw, _ in self.records])

    def _run(self, create):
        need(not self.owned and not self.records, 'boot NSS owner instance is one-use')
        baseline = descriptors()
        failure = None
        try:
            self._configure() if create else self._verify()
        except BaseException as error:
            failure = dict(type=type(error).__name__, reason=str(error)[:384])
            self.result.update(configured=None, state=('EXCHANGE_OUTCOME_UNCERTAIN'
                               if self.result['exchange_attempted'] else 'REFUSED_NO_EXCHANGE'))
            # A failed attempt never becomes resumable. If a completion record
            # already exists, a retained refusal marker also blocks later readers.
            if create and self.slot is not None:
                try:
                    self._create('99-refused.json', canonical(dict(schema='g132.boot-nss-refusal.v1',
                                 context=self.context, failure=failure, configured=None,
                                 exchange_attempted=self.result['exchange_attempted'])), 0o600)
                    self.result['refusal_marker_retained'] = True
                except BaseException as marker_error:
                    self.result['refusal_marker_failure'] = type(marker_error).__name__
        finally:
            close_errors = []
            for fd in reversed(self.owned):
                try:
                    os.close(fd)
                except OSError as error:
                    close_errors.append(dict(fd=fd, errno=error.errno))
            self.owned.clear()
            self.result['descriptor_restoration'] = not close_errors and descriptors() == baseline
            if close_errors:
                self.result['descriptor_close_errors'] = close_errors
        if not self.result['descriptor_restoration']:
            failure = failure or dict(type='DescriptorClosure', reason='owned descriptor closure differs')
        if failure is not None:
            self.result['failure'] = failure
            raise Refusal(self.result)
        return self.result

    def provision(self):
        return self._run(True)

    def verify(self):
        return self._run(False)


def _hosted(context):
    expected = dict(GITHUB_ACTIONS='true', RUNNER_ENVIRONMENT='github-hosted',
                    GITHUB_REPOSITORY='theislampill/IMPLEMENTAUDIT.md', GITHUB_RUN_ATTEMPT='1',
                    GITHUB_EVENT_NAME='push', GITHUB_JOB='qualify', GITHUB_REF=REF,
                    ImageOS='ubuntu24', ImageVersion='20261116.376.1')
    need(all(os.environ.get(k) == v == context.get(k) for k, v in expected.items()),
         'boot NSS exact ordinary hosted context refused')
    need((os.getuid(), os.geteuid(), os.getgid(), os.getegid()) == (0, 0, 0, 0), 'boot NSS root identity required')
    host = os.environ.get('GITHUB_SHA', '')
    need(re.fullmatch('[0-9a-f]{40}', host) and os.environ.get('GITHUB_WORKFLOW_SHA') == host
         and context.get('host_commit') == host and context.get('workflow_ref') == WORKFLOW
         and os.environ.get('GITHUB_WORKFLOW_REF') == WORKFLOW
         and context.get('run_id') == os.environ.get('GITHUB_RUN_ID')
         and context.get('operation') == OPERATION
         and all(re.fullmatch('[0-9a-f]{40}', context.get(k, '')) for k in ('source_commit', 'source_tree')),
         'boot NSS operation/source/provider binding refused')
    with open('/proc/sys/kernel/random/boot_id', 'rb') as stream:
        boot = stream.read(65).decode('ascii').strip()
    need(re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', boot)
         and context.get('boot_id') == boot, 'boot NSS boot identity differs')
    return _BootNSSFiles('/etc', context, expected_uid=0, expected_gid=0, before_pin=BEFORE, after_pin=AFTER)


def provision_hosted(context):
    return _hosted(context).provision()


def verify_configured(context):
    return _hosted(context).verify()
