"""Exact prospective NSS preparation in this disposable Ubuntu24 G1 VM only.

The maintained files-only gate is unchanged. This administrative preparation
must run before controller creation and before any G1 acquisition. No account
database, credential, ownership, acceptance limit or product source is changed.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat

BEFORE_BYTES = 526
BEFORE_SHA = 'b953df1d0016f515fc052ca6bb0ccd092b8d13c8789c51c4eaef2b0461574e57'
AFTER_BYTES = 518
AFTER_SHA = '5cde76a7763cef05fea9a086f5db0025459d489ee658a8369602e415e47beff7'
PHASES = ('RESERVED', 'PREIMAGE_RETAINED', 'TEMPORARY_CREATED', 'REPLACE_OUTCOME_UNKNOWN',
          'CONFIGURED_AND_READ_BACK', 'CONFIGURATION_REFUSED')


def need(ok, code):
    if not ok:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode('ascii')


def identity(info):
    return [info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns, info.st_uid, info.st_gid]


def transform(raw):
    need(type(raw) is bytes and len(raw) == BEFORE_BYTES and sha(raw) == BEFORE_SHA,
         'NSS_CONFIGURATION_PREIMAGE_REFUSED')
    old = b'passwd:         files systemd\n'
    new = b'passwd:         files\n'
    need(raw.splitlines(keepends=True).count(old) == 1, 'NSS_CONFIGURATION_ROW_REFUSED')
    after = raw.replace(old, new, 1)
    need(len(after) == AFTER_BYTES and sha(after) == AFTER_SHA,
         'NSS_CONFIGURATION_POSTIMAGE_REFUSED')
    # All other rows and their ordering, spacing and line endings stay exact.
    need([r for r in raw.splitlines(keepends=True) if r != old] ==
         [r for r in after.splitlines(keepends=True) if r != new],
         'NSS_CONFIGURATION_OTHER_ROW_CHANGED')
    return after


def read_target(directory_fd):
    before = os.stat('nsswitch.conf', dir_fd=directory_fd, follow_symlinks=False)
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
         and before.st_uid == before.st_gid == 0 and stat.S_IMODE(before.st_mode) == 0o644
         and 0 < before.st_size <= 65536, 'NSS_CONFIGURATION_TARGET_CUSTODY')
    fd = os.open('nsswitch.conf', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                 dir_fd=directory_fd)
    try:
        need(identity(os.fstat(fd)) == identity(before) and not os.listxattr(fd),
             'NSS_CONFIGURATION_TARGET_OPEN_CHANGED')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(65537)
        need(len(raw) == before.st_size and identity(os.fstat(fd)) == identity(before)
             and identity(os.stat('nsswitch.conf', dir_fd=directory_fd, follow_symlinks=False)) == identity(before),
             'NSS_CONFIGURATION_TARGET_READ_CHANGED')
        return raw, identity(before)
    finally:
        os.close(fd)


def prepare(private, run_id, write_once):
    """One exact configured-host effect; every uncertain replacement is retained.

    The private output function is the reviewed adapter's exclusive writer.
    Only this fresh journal can enter; its existence forbids a repeated call.
    """
    need(os.getuid() == os.geteuid() == os.getgid() == os.getegid() == 0,
         'NSS_CONFIGURATION_ACTUAL_ROOT_REQUIRED')
    need(type(run_id) is str and re.fullmatch('[1-9][0-9]{5,19}', run_id),
         'NSS_CONFIGURATION_RUN_ID')
    private = Path(private)
    journal = private/'NSS_CONFIGURATION.json'
    need(not journal.exists() and not journal.is_symlink(), 'NSS_CONFIGURATION_NO_REPLAY')
    value = dict(schema='dg16.g1-nss-configuration.v1', authority='NONE', phase='RESERVED',
        target='/etc/nsswitch.conf', run_id=run_id, scope='EXACT_EPHEMERAL_G1_VM_CONFIGURATION_BEFORE_CONTROLLER',
        before=None, after=None, replacement='NOT_STARTED', temporary_created=False,
        temporary_removed=False, configured=False, failure_code=None,
        changed_rows=['passwd'], original_gate_unchanged=True, ownership_changed=False,
        product_source_changed=False, disposition='RETAIN_CONFIGURED_FILE_UNTIL_VM_DISPOSAL')

    def checkpoint():
        raw = encode(value)
        need(len(raw) <= 8192, 'NSS_CONFIGURATION_JOURNAL_BOUND')
        temporary = journal.with_suffix('.next')
        write_once(temporary, raw)
        os.replace(temporary, journal)
        fd = os.open(private, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    checkpoint()
    directory_fd = None
    temporary_name = '.implementaudit-r5-g1-nss-'+run_id+'-a1.tmp'
    temporary_identity = None
    try:
        root = os.lstat('/')
        etc = os.lstat('/etc')
        for entry in (root, etc):
            need(stat.S_ISDIR(entry.st_mode) and entry.st_uid == entry.st_gid == 0
                 and not entry.st_mode & 0o022, 'NSS_CONFIGURATION_ANCESTRY_REFUSED')
        directory_fd = os.open('/etc', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        opened = os.fstat(directory_fd)
        need((opened.st_dev, opened.st_ino, opened.st_mode, opened.st_uid, opened.st_gid) ==
             (etc.st_dev, etc.st_ino, etc.st_mode, etc.st_uid, etc.st_gid),
             'NSS_CONFIGURATION_DIRECTORY_CHANGED')
        before, physical = read_target(directory_fd)
        value['before'] = dict(bytes=len(before), sha256=sha(before), physical=physical)
        write_once(private/'NSS_CONFIGURATION_BEFORE.raw', before)
        after = transform(before)
        value['phase'] = 'PREIMAGE_RETAINED'
        checkpoint()
        fd = os.open(temporary_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                     0o644, dir_fd=directory_fd)
        temporary_identity = identity(os.fstat(fd))
        value['temporary_created'] = True
        value['phase'] = 'TEMPORARY_CREATED'
        try:
            checkpoint()
            with os.fdopen(fd, 'wb', closefd=False) as stream:
                stream.write(after)
                stream.flush()
                os.fsync(fd)
            info = os.fstat(fd)
            need(stat.S_ISREG(info.st_mode) and info.st_uid == info.st_gid == 0
                 and stat.S_IMODE(info.st_mode) == 0o644 and info.st_nlink == 1
                 and info.st_size == len(after) and not os.listxattr(fd),
                 'NSS_CONFIGURATION_TEMPORARY_CUSTODY')
            temporary_identity = identity(info)
        finally:
            os.close(fd)
        need(read_target(directory_fd) == (before, physical), 'NSS_CONFIGURATION_PREIMAGE_CHANGED')
        need(identity(os.stat(temporary_name, dir_fd=directory_fd, follow_symlinks=False)) == temporary_identity,
             'NSS_CONFIGURATION_TEMPORARY_CHANGED')
        value['replacement'] = 'STARTED_OUTCOME_UNKNOWN'
        value['configured'] = None
        value['phase'] = 'REPLACE_OUTCOME_UNKNOWN'
        checkpoint()
        os.replace(temporary_name, 'nsswitch.conf', src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        os.fsync(directory_fd)
        actual, physical_after = read_target(directory_fd)
        value['after'] = dict(bytes=len(actual), sha256=sha(actual), physical=physical_after)
        # A normal rename can update ctime. Preserve its actual new value and
        # require every unaffected physical field, including the same inode.
        need(actual == after and physical_after[:6] == temporary_identity[:6]
             and physical_after[7:] == temporary_identity[7:],
             'NSS_CONFIGURATION_REPLACEMENT_READBACK')
        write_once(private/'NSS_CONFIGURATION_AFTER.raw', actual)
        value.update(replacement='COMPLETED', configured=True, phase='CONFIGURED_AND_READ_BACK')
        checkpoint()
        return value
    except BaseException as exc:
        code = str(exc)
        value['failure_code'] = code if code in REFUSALS else 'NSS_CONFIGURATION_UNCLASSIFIED_REFUSAL'
        value['phase'] = 'CONFIGURATION_REFUSED'
        checkpoint()
        raise
    finally:
        if directory_fd is not None:
            # Remove only the new temporary inode if replacement never began.
            # After an uncertain replacement, leave all observations for readback.
            if temporary_identity is not None and value['replacement'] == 'NOT_STARTED':
                try:
                    observed = os.stat(temporary_name, dir_fd=directory_fd, follow_symlinks=False)
                    if (observed.st_dev, observed.st_ino) == tuple(temporary_identity[:2]):
                        os.unlink(temporary_name, dir_fd=directory_fd)
                        os.fsync(directory_fd)
                        value['temporary_removed'] = True
                        checkpoint()
                except FileNotFoundError:
                    pass
            os.close(directory_fd)


def verify_configured(value):
    # The adapter supplies its guarded, exact private journal readback.
    need(type(value) is dict, 'NSS_CONFIGURATION_NOT_COMPLETED')
    need(value.get('configured') is True and value.get('replacement') == 'COMPLETED',
         'NSS_CONFIGURATION_NOT_COMPLETED')
    fd = os.open('/etc', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        raw, physical = read_target(fd)
    finally:
        os.close(fd)
    need(value['after'] == dict(bytes=len(raw), sha256=sha(raw), physical=physical)
         and len(raw) == AFTER_BYTES and sha(raw) == AFTER_SHA, 'NSS_CONFIGURATION_FINAL_CHANGED')
    return dict(configured=True, bytes=len(raw), sha256=sha(raw),
                physical_sha256=sha(encode(physical)), original_gate_unchanged=True,
                disposition='RETAIN_CONFIGURED_FILE_UNTIL_VM_DISPOSAL')


def public_state(value):
    """Validate the finite private journal and construct its public effect facts."""
    fields={'schema','authority','phase','target','run_id','scope','before','after','replacement',
        'temporary_created','temporary_removed','configured','failure_code','changed_rows',
        'original_gate_unchanged','ownership_changed','product_source_changed','disposition'}
    need(type(value) is dict and set(value)==fields
         and value['schema']=='dg16.g1-nss-configuration.v1' and value['authority']=='NONE'
         and value['target']=='/etc/nsswitch.conf' and type(value['run_id']) is str
         and re.fullmatch('[1-9][0-9]{5,19}',value['run_id'])
         and value['scope']=='EXACT_EPHEMERAL_G1_VM_CONFIGURATION_BEFORE_CONTROLLER'
         and value['phase'] in PHASES
         and value['replacement'] in ('NOT_STARTED','STARTED_OUTCOME_UNKNOWN','COMPLETED')
         and value['changed_rows']==['passwd'] and value['original_gate_unchanged'] is True
         and value['ownership_changed'] is False and value['product_source_changed'] is False
         and value['disposition']=='RETAIN_CONFIGURED_FILE_UNTIL_VM_DISPOSAL',
         'NSS_CONFIGURATION_JOURNAL_SCHEMA')
    for key in ('temporary_created','temporary_removed'):
        need(type(value[key]) is bool,'NSS_CONFIGURATION_JOURNAL_SCHEMA')
    need(value['configured'] is None or type(value['configured']) is bool,
         'NSS_CONFIGURATION_JOURNAL_SCHEMA')
    need(value['failure_code'] is None or value['failure_code'] in REFUSALS
         or value['failure_code']=='NSS_CONFIGURATION_UNCLASSIFIED_REFUSAL',
         'NSS_CONFIGURATION_JOURNAL_SCHEMA')
    observations={}
    for name in ('before','after'):
        row=value[name]
        if row is None:
            observations[name]=None
            continue
        need(type(row) is dict and set(row)=={'bytes','sha256','physical'}
             and type(row['bytes']) is int and 0<row['bytes']<=65536
             and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['sha256'])
             and type(row['physical']) is list and len(row['physical'])==9
             and all(type(x) is int and 0<=x<2**64 for x in row['physical']),
             'NSS_CONFIGURATION_JOURNAL_SCHEMA')
        observations[name]=dict(bytes=row['bytes'],sha256=row['sha256'],
            physical_sha256=sha(encode(row['physical'])))
    need((value['replacement']=='COMPLETED')==(value['configured'] is True)
         and (value['replacement']!='STARTED_OUTCOME_UNKNOWN' or value['configured'] is None)
         and (value['replacement']!='NOT_STARTED' or value['configured'] is False),
         'NSS_CONFIGURATION_JOURNAL_CONTRADICTION')
    if value['configured'] is True:
        need(value['before'] is not None and value['after'] is not None
             and value['before']['bytes']==BEFORE_BYTES and value['before']['sha256']==BEFORE_SHA
             and value['after']['bytes']==AFTER_BYTES and value['after']['sha256']==AFTER_SHA
             and value['temporary_created'] is True and value['temporary_removed'] is False,
             'NSS_CONFIGURATION_JOURNAL_CONTRADICTION')
    need(not value['temporary_removed'] or value['temporary_created']
         and value['replacement']=='NOT_STARTED','NSS_CONFIGURATION_JOURNAL_CONTRADICTION')
    return dict(schema='dg16.g1-nss-effect-observation.v1',authority='NONE',
        phase=value['phase'],replacement=value['replacement'],configured=value['configured'],
        temporary_creation_recorded=value['temporary_created'],temporary_removal_recorded=value['temporary_removed'],
        temporary_false_meaning='NO_DURABLE_COMPLETION_OBSERVATION_NOT_PROOF_OF_ABSENCE',
        failure_code=value['failure_code'],before=observations['before'],after=observations['after'],
        changed_rows=['passwd'],original_gate_unchanged=True,ownership_changed=False,
        product_source_changed=False,disposition=value['disposition'])


REFUSALS = frozenset({
    'NSS_CONFIGURATION_PREIMAGE_REFUSED', 'NSS_CONFIGURATION_ROW_REFUSED',
    'NSS_CONFIGURATION_POSTIMAGE_REFUSED', 'NSS_CONFIGURATION_OTHER_ROW_CHANGED',
    'NSS_CONFIGURATION_TARGET_CUSTODY', 'NSS_CONFIGURATION_TARGET_OPEN_CHANGED',
    'NSS_CONFIGURATION_TARGET_READ_CHANGED', 'NSS_CONFIGURATION_ACTUAL_ROOT_REQUIRED',
    'NSS_CONFIGURATION_RUN_ID', 'NSS_CONFIGURATION_NO_REPLAY', 'NSS_CONFIGURATION_JOURNAL_BOUND',
    'NSS_CONFIGURATION_ANCESTRY_REFUSED', 'NSS_CONFIGURATION_DIRECTORY_CHANGED',
    'NSS_CONFIGURATION_TEMPORARY_CUSTODY', 'NSS_CONFIGURATION_PREIMAGE_CHANGED',
    'NSS_CONFIGURATION_TEMPORARY_CHANGED', 'NSS_CONFIGURATION_REPLACEMENT_READBACK',
    'NSS_CONFIGURATION_NOT_COMPLETED', 'NSS_CONFIGURATION_FINAL_CHANGED',
    'NSS_CONFIGURATION_JOURNAL_SCHEMA', 'NSS_CONFIGURATION_JOURNAL_CONTRADICTION'})


if __name__ == '__main__':
    raise SystemExit('REVIEWED_HOSTED_ADAPTER_CALL_ONLY')
