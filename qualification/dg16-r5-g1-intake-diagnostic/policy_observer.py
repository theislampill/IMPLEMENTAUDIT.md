#!/usr/bin/env python3
"""Parent-owned fresh kmsg window. No writer, tracing hook or policy operation.

Window alone touches the fixed device during a separately authorized episode.
Parsing/projection is closed, bounded and pure. Raw records and private scalars
never enter public output. Recognized text is not target-process attribution.
"""
import errno
import hashlib
import json
import os
import re
import stat
import time

SCHEMA = 'dg16.g1-parent-kmsg-window.v1'
SETUP_SHA256 = '5caa2b1771c41b9c13328b44c72b45ff73d65832b6892cc6bc61cfb54bd6cbf1'
POLICY_SHA256 = 'b3f303f76b8f2c097f92ca5e41b6e0126cd34a10df1d5d0e67b9e86e92e322af'
TRANSPORT_SHA256 = 'a6ecc502ef72cdd280684353899f306a3d5dbd1a858c2ae9b39269e047d04760'
BWRAP_SHA256 = '52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712'
PROFILES = {
    b'implementaudit-c5-bwrap-v1': 'SOURCE_SETUP_PROFILE_LITERAL',
    b'implementaudit-c5-unpriv-bwrap-v1': 'SOURCE_CHILD_PROFILE_LITERAL',
    b'implementaudit-c5-bwrap-v1//&implementaudit-c5-unpriv-bwrap-v1':
        'SOURCE_STACKED_TRANSITION_LITERAL',
}
CAPABILITIES = ('chown', 'dac_override', 'dac_read_search', 'fowner', 'fsetid',
    'kill', 'setgid', 'setuid', 'setpcap', 'linux_immutable', 'net_bind_service',
    'net_broadcast', 'net_admin', 'net_raw', 'ipc_lock', 'ipc_owner', 'sys_module',
    'sys_rawio', 'sys_chroot', 'sys_ptrace', 'sys_pacct', 'sys_admin', 'sys_boot',
    'sys_nice', 'sys_resource', 'sys_time', 'sys_tty_config', 'mknod', 'lease',
    'audit_write', 'audit_control', 'setfcap', 'mac_override', 'mac_admin',
    'syslog', 'wake_alarm', 'block_suspend', 'audit_read', 'perfmon', 'bpf',
    'checkpoint_restore')
MAX_READ = 8192
MAX_RAW_BYTES = 131072
MAX_RECORDS = 64
MAX_DRAIN_NS = 100000000
MAX_SAMPLES = 4
MAX_PUBLIC_BYTES = 6144
COUNTS = ('NON_KERNEL_RECORD', 'UNSUPPORTED_KMSG_FLAGS', 'UNSUPPORTED_KMSG_BODY',
    'OTHER_KERNEL_RECORD', 'UNKNOWN_APPARMOR_RECORD', 'OTHER_PROFILE_APPARMOR_RECORD',
    'RECOGNIZED_PROFILE_CAPABILITY_DENIAL', 'UNSUPPORTED_KMSG_HEADER')
UNKNOWN_REASONS = ('LINE_OR_PREFIX', 'FIELD_SHAPE', 'DUPLICATE_KEY',
    'FIELD_POPULATION', 'LITERAL_OR_SCALAR', 'CAPABILITY_PAIR')
STATUSES = ('NOT_ATTEMPTED', 'API_UNAVAILABLE', 'OPEN_UNAVAILABLE',
    'DEVICE_IDENTITY_REFUSED', 'SEEK_UNAVAILABLE', 'ABORTED_BEFORE_DRAIN',
    'READ_EAGAIN', 'READ_LOSS_EPIPE', 'READ_EINVAL_UNSUPPORTED_SIZE_OR_API',
    'READ_UNAVAILABLE', 'READ_ZERO', 'RECORD_COUNT_BOUND', 'RAW_BYTE_BOUND',
    'DRAIN_TIME_BOUND', 'RECORD_FRAMING_REFUSED', 'SEQUENCE_DISCONTINUITY',
    'DEVICE_CUSTODY_REFUSED', 'OBSERVER_SHAPE_REFUSED', 'OBSERVER_INTERRUPTED')
READ_STATUSES = STATUSES[6:]
EMPTY_HASH = hashlib.sha256(b'').hexdigest()


class Refusal(Exception):
    pass


class GrammarRefusal(Exception):
    pass


def need(ok):
    if not ok:
        raise Refusal('CLOSED_POLICY_OBSERVATION_REFUSED')


def grammar(ok, code):
    if not ok:
        raise GrammarRefusal(code)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
        ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptor(raw):
    need(type(raw) is bytes)
    return dict(bytes=len(raw), sha256=sha(raw))


def integer(value, maximum=2**64-1):
    return type(value) is int and 0 <= value <= maximum


def hash_value(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def keys(value, names):
    need(type(value) is dict and len(value) == len(names)
         and all(type(key) is str for key in value) and set(value) == set(names))


def validate_descriptor(value, maximum):
    keys(value, ('bytes', 'sha256'))
    need(integer(value['bytes'], maximum) and hash_value(value['sha256']))
    if value['bytes'] == 0:
        need(value['sha256'] == EMPTY_HASH)


def decimal(raw, maximum):
    need(type(raw) is bytes and len(raw) <= 20
         and re.fullmatch(b'(?:0|[1-9][0-9]*)', raw) is not None)
    value = int(raw)
    need(value <= maximum)
    return value


def kmsg_header(raw):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_READ)
    prefix, sep, body = raw.partition(b';')
    need(bool(sep) and len(prefix) <= 128)
    fields = prefix.split(b',')
    need(len(fields) == 4)
    priority = decimal(fields[0], 2047)
    sequence = decimal(fields[1], 2**64-1)
    timestamp = decimal(fields[2], 2**64-1)
    need(0 < len(fields[3]) <= 16 and re.fullmatch(b'[A-Za-z-]+', fields[3]) is not None)
    return priority, sequence, timestamp, fields[3], body


def audit_fields(body):
    grammar(type(body) is bytes and body.endswith(b'\n') and body.count(b'\n') == 1
        and b'\\' not in body and all(32 <= c < 127 for c in body[:-1]), 'LINE_OR_PREFIX')
    match = re.match(rb'audit: type=1400 audit\(([0-9]{1,20}\.[0-9]{1,9}:[0-9]{1,20})\): ', body)
    grammar(match is not None, 'LINE_OR_PREFIX')
    tail = body[match.end():-1]
    fields = {}
    position = 0
    token = re.compile(rb'([a-z_]{1,24})=(?:"([^"\x00-\x1f\x7f]*)"|([A-Za-z0-9_.:/&+\-]+))(?: |$)')
    while position < len(tail):
        item = token.match(tail, position)
        grammar(item is not None and len(fields) < 16, 'FIELD_SHAPE')
        key = item.group(1)
        value = item.group(2) if item.group(2) is not None else item.group(3)
        grammar(key not in fields, 'DUPLICATE_KEY')
        grammar(len(value) <= 1024, 'FIELD_SHAPE')
        fields[key] = value
        position = item.end()
    required = {b'apparmor', b'operation', b'profile', b'pid', b'comm', b'capability', b'capname'}
    grammar(required <= set(fields) <= required | {b'class', b'parent'}, 'FIELD_POPULATION')
    grammar(fields[b'apparmor'] == b'DENIED' and fields[b'operation'] == b'capable'
        and (b'class' not in fields or fields[b'class'] == b'cap')
        and 0 < len(fields[b'comm']) <= 16, 'LITERAL_OR_SCALAR')
    try:
        need(decimal(fields[b'pid'], 2**31-1) > 0)
        if b'parent' in fields:
            decimal(fields[b'parent'], 2**31-1)
        number = decimal(fields[b'capability'], len(CAPABILITIES)-1)
    except Refusal:
        raise GrammarRefusal('LITERAL_OR_SCALAR') from None
    grammar(fields[b'capname'] == CAPABILITIES[number].encode('ascii'), 'CAPABILITY_PAIR')
    return fields, number


def classify(raw, ordinal):
    try:
        priority, sequence, timestamp, flags, body = kmsg_header(raw)
    except Refusal:
        return 'UNSUPPORTED_KMSG_HEADER', None, None, None
    if priority >> 3 != 0:
        return 'NON_KERNEL_RECORD', sequence, None, None
    if flags != b'-':
        return 'UNSUPPORTED_KMSG_FLAGS', sequence, None, None
    if not body.endswith(b'\n') or body.count(b'\n') != 1:
        return 'UNSUPPORTED_KMSG_BODY', sequence, None, None
    if not (body.startswith(b'audit: type=1400 ') or b'apparmor=' in body):
        return 'OTHER_KERNEL_RECORD', sequence, None, None
    try:
        fields, number = audit_fields(body)
    except GrammarRefusal as exc:
        reason = exc.args[0]
        need(type(reason) is str and reason in UNKNOWN_REASONS)
        return 'UNKNOWN_APPARMOR_RECORD', sequence, None, reason
    role = PROFILES.get(fields[b'profile'])
    if role is None:
        return 'OTHER_PROFILE_APPARMOR_RECORD', sequence, None, None
    row = dict(ordinal=ordinal, sequence=sequence, record=descriptor(raw), profile_role=role,
        operation='CAPABLE', capability_number=number, capability_name=CAPABILITIES[number],
        class_field='CAP' if b'class' in fields else 'NOT_PRESENT',
        audit_pid=descriptor(fields[b'pid']), comm=descriptor(fields[b'comm']),
        comm_role='LITERAL_BWRAP' if fields[b'comm'] == b'bwrap' else 'UNKNOWN',
        process_attribution='UNESTABLISHED')
    return 'RECOGNIZED_PROFILE_CAPABILITY_DENIAL', sequence, row, None


def empty():
    return dict(schema=SCHEMA, authority='NONE', status='NOT_ATTEMPTED', errno=None,
        attempted=False, opened=False, device_identity_checked=False,
        close_on_exec_checked=False, nonblocking_checked=False, seek_end_completed=False,
        case_launch_attempted=False, case_process_started=False, case_capture_complete=False,
        case_child_custody_established=False, closing_custody='NOT_CHECKED', close_status='NOT_OPENED',
        records=0, raw_bytes=0, framed_raw_sha256=EMPTY_HASH,
        categories={key:0 for key in COUNTS}, unknown_reasons={key:0 for key in UNKNOWN_REASONS},
        first_sequence=None, last_sequence=None, sequence_discontinuity=None,
        recognized_count=0, recognized_sha256=sha(canonical([])), samples=[], samples_omitted=0,
        setup_source_sha256=SETUP_SHA256, policy_definition_sha256=POLICY_SHA256,
        scope='PARENT_SEEK_END_THROUGH_POST_CAPTURE_DRAIN_INTERVAL_ONLY',
        cursor='NEW_READER_SEEK_END_ZERO_ONCE_NO_REPOSITION',
        raw_hash_framing='U64BE_LENGTH_THEN_RECORD_IN_READ_ORDER',
        completeness='ONLY_RETURNED_RECORDS_NO_ABSENCE_OR_RATE_LIMIT_CLAIM',
        observer_actor='DIAGNOSTIC_PARENT_ONLY', process_attribution='UNESTABLISHED',
        denied_object='UNESTABLISHED', policy_cause='UNESTABLISHED', raw_kernel_records_public=False)


def directory_identity(info):
    need(type(info) is os.stat_result and stat.S_ISDIR(info.st_mode)
        and info.st_uid == 0 and not info.st_mode & 0o022)
    return info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid


def device_identity(info):
    need(type(info) is os.stat_result and stat.S_ISCHR(info.st_mode)
        and info.st_rdev == os.makedev(1, 11) and info.st_uid == 0 and info.st_gid == 0
        and info.st_nlink == 1 and not info.st_mode & 0o022)
    return (info.st_dev, info.st_ino, info.st_mode, info.st_rdev,
        info.st_uid, info.st_gid, info.st_nlink)


def os_errno(exc):
    value = exc.errno
    return value if integer(value, 4096) else None


class Window:
    def __init__(self, api=os, clock=time.monotonic_ns):
        self.api, self.clock = api, clock
        self.fd, self.identity, self.ancestors = None, None, None
        self.record = empty()
        self.closed = False

    def check_custody(self):
        need(self.fd is not None and not self.closed)
        need([directory_identity(self.api.lstat(p)) for p in ('/', '/dev')] == self.ancestors)
        need(device_identity(self.api.fstat(self.fd)) == self.identity
            == device_identity(self.api.lstat('/dev/kmsg')))
        need(self.api.get_inheritable(self.fd) is False and self.api.get_blocking(self.fd) is False)

    def start(self):
        need(not self.record['attempted'])
        self.record['attempted'] = True
        api = self.api
        names = ('O_RDONLY', 'O_NOFOLLOW', 'O_NONBLOCK', 'O_CLOEXEC', 'SEEK_END',
            'get_inheritable', 'get_blocking', 'lstat', 'fstat', 'open', 'close', 'lseek', 'read')
        if not all(hasattr(api, name) for name in names):
            self.record['status'] = 'API_UNAVAILABLE'
            return False
        try:
            self.ancestors = [directory_identity(api.lstat(p)) for p in ('/', '/dev')]
            before = device_identity(api.lstat('/dev/kmsg'))
            fd = api.open('/dev/kmsg', api.O_RDONLY | api.O_NOFOLLOW | api.O_NONBLOCK | api.O_CLOEXEC)
            need(type(fd) is int and 0 <= fd < 2**31)
            self.fd = fd
            self.record['opened'] = True
            need(fd < 4096)
            self.identity = device_identity(api.fstat(fd))
            need(self.identity == before == device_identity(api.lstat('/dev/kmsg')))
            self.record['device_identity_checked'] = True
            need(api.get_inheritable(fd) is False)
            self.record['close_on_exec_checked'] = True
            need(api.get_blocking(fd) is False)
            self.record['nonblocking_checked'] = True
        except OSError as exc:
            self.record.update(status='OPEN_UNAVAILABLE', errno=os_errno(exc))
            self.close()
            return False
        except Refusal:
            self.record['status'] = 'DEVICE_IDENTITY_REFUSED'
            self.close()
            return False
        except BaseException:
            self.record['status'] = 'OBSERVER_INTERRUPTED'
            self.close()
            raise
        try:
            offset = api.lseek(self.fd, 0, api.SEEK_END)
            need(type(offset) is int and offset == 0)
            self.record.update(status='ABORTED_BEFORE_DRAIN', seek_end_completed=True)
            return True
        except OSError as exc:
            self.record.update(status='SEEK_UNAVAILABLE', errno=os_errno(exc))
        except Refusal:
            self.record['status'] = 'SEEK_UNAVAILABLE'
        except BaseException:
            self.record['status'] = 'OBSERVER_INTERRUPTED'
            self.close()
            raise
        self.close()
        return False

    def mark_case_attempted(self):
        need(self.fd is not None and not self.closed and self.record['seek_end_completed']
            and not self.record['case_launch_attempted'])
        self.record['case_launch_attempted'] = True

    def drain(self, process_started, capture_complete, child_custody_established):
        need(self.record['case_launch_attempted'] and self.fd is not None and not self.closed)
        rows, raw_hash, previous = [], hashlib.sha256(), None
        try:
            need(type(process_started) is bool and type(capture_complete) is bool
                and type(child_custody_established) is bool)
            need(not (capture_complete or child_custody_established) or process_started)
            self.record.update(case_process_started=process_started, case_capture_complete=capture_complete,
                case_child_custody_established=child_custody_established)
            try:
                self.check_custody()
            except (OSError, Refusal):
                self.record['status'] = 'DEVICE_CUSTODY_REFUSED'
                return None
            start = self.clock()
            need(integer(start, 2**63-1))
            while True:
                now = self.clock()
                need(integer(now, 2**63-1) and now >= start)
                if now-start >= MAX_DRAIN_NS:
                    self.record['status'] = 'DRAIN_TIME_BOUND'
                    break
                if self.record['records'] >= MAX_RECORDS:
                    self.record['status'] = 'RECORD_COUNT_BOUND'
                    break
                if self.record['raw_bytes'] + MAX_READ > MAX_RAW_BYTES:
                    self.record['status'] = 'RAW_BYTE_BOUND'
                    break
                try:
                    raw = self.api.read(self.fd, MAX_READ)
                except OSError as exc:
                    number = os_errno(exc)
                    status = ('READ_EAGAIN' if number in (errno.EAGAIN, errno.EWOULDBLOCK) else
                        'READ_LOSS_EPIPE' if number == errno.EPIPE else
                        'READ_EINVAL_UNSUPPORTED_SIZE_OR_API' if number == errno.EINVAL else 'READ_UNAVAILABLE')
                    self.record.update(status=status, errno=number)
                    break
                need(type(raw) is bytes and len(raw) <= MAX_READ)
                if not raw:
                    self.record['status'] = 'READ_ZERO'
                    break
                ordinal = self.record['records']
                self.record['records'] += 1
                self.record['raw_bytes'] += len(raw)
                raw_hash.update(len(raw).to_bytes(8, 'big'));raw_hash.update(raw)
                category, sequence, row, unknown = classify(raw, ordinal)
                self.record['categories'][category] += 1
                if unknown is not None:
                    self.record['unknown_reasons'][unknown] += 1
                if sequence is not None:
                    if self.record['first_sequence'] is None:
                        self.record['first_sequence'] = sequence
                    self.record['last_sequence'] = sequence
                if row is not None:
                    rows.append(row)
                if category == 'UNSUPPORTED_KMSG_HEADER':
                    self.record['status'] = 'RECORD_FRAMING_REFUSED'
                    break
                if previous is not None and sequence != previous+1:
                    self.record.update(status='SEQUENCE_DISCONTINUITY', sequence_discontinuity=dict(
                        ordinal=ordinal, previous_sequence=previous, observed_sequence=sequence))
                    break
                previous = sequence
        except Refusal:
            self.record['status'] = 'OBSERVER_SHAPE_REFUSED'
        except BaseException:
            self.record['status'] = 'OBSERVER_INTERRUPTED'
            raise
        finally:
            self.record.update(framed_raw_sha256=raw_hash.hexdigest(), recognized_count=len(rows),
                recognized_sha256=sha(canonical(rows)), samples=rows[:MAX_SAMPLES],
                samples_omitted=max(0, len(rows)-MAX_SAMPLES))
            try:
                self.check_custody()
                self.record['closing_custody'] = 'MATCHED'
            except (OSError, Refusal):
                self.record['closing_custody'] = 'REFUSED'
            finally:
                self.close()
        return self.public()

    def close(self):
        if self.fd is None or self.closed:
            return
        self.closed = True
        fd, self.fd = self.fd, None
        try:
            self.api.close(fd)
            self.record['close_status'] = 'CLOSED'
        except BaseException:
            # Never close a potentially reused descriptor a second time.
            self.record['close_status'] = 'CLOSE_UNAVAILABLE'
            raise

    def public(self):
        validate(self.record)
        return json.loads(canonical(self.record))


def validate(value):
    template = empty()
    keys(value, template)
    mutable = {'status', 'errno', 'attempted', 'opened', 'device_identity_checked',
        'close_on_exec_checked', 'nonblocking_checked', 'seek_end_completed',
        'case_launch_attempted', 'case_process_started', 'case_capture_complete',
        'case_child_custody_established', 'closing_custody', 'close_status', 'records',
        'raw_bytes', 'framed_raw_sha256', 'categories', 'unknown_reasons', 'first_sequence',
        'last_sequence', 'sequence_discontinuity', 'recognized_count', 'recognized_sha256',
        'samples', 'samples_omitted'}
    for key in set(template)-mutable:
        need(type(value[key]) is type(template[key]) and value[key] == template[key])
    need(type(value['status']) is str and value['status'] in STATUSES
        and (value['errno'] is None or integer(value['errno'], 4096)))
    boolean_keys = ('attempted', 'opened', 'device_identity_checked', 'close_on_exec_checked',
        'nonblocking_checked', 'seek_end_completed', 'case_launch_attempted', 'case_process_started',
        'case_capture_complete', 'case_child_custody_established')
    need(all(type(value[key]) is bool for key in boolean_keys))
    chain = [value[key] for key in boolean_keys[:8]]
    need(all(not chain[n] or chain[n-1] for n in range(1, len(chain))))
    need(not (value['case_capture_complete'] or value['case_child_custody_established']) or value['case_process_started'])
    need(type(value['close_status']) is str and value['close_status'] in ('NOT_OPENED', 'CLOSED', 'CLOSE_UNAVAILABLE'))
    need((value['close_status'] == 'NOT_OPENED') is (not value['opened']))
    need(type(value['closing_custody']) is str and value['closing_custody'] in ('NOT_CHECKED', 'MATCHED', 'REFUSED'))
    need(value['closing_custody'] == 'NOT_CHECKED' or value['case_launch_attempted'])
    if value['status'] == 'NOT_ATTEMPTED':
        need(not value['attempted'] and value['errno'] is None)
    else:
        need(value['attempted'])
    if value['status'] in STATUSES[:6]:
        need(not value['case_launch_attempted'] and value['closing_custody'] == 'NOT_CHECKED'
            and integer(value['records'], MAX_RECORDS) and value['records'] == 0)
    if value['status'] == 'API_UNAVAILABLE':
        need(not value['opened'] and value['errno'] is None)
    if value['status'] in ('OPEN_UNAVAILABLE', 'DEVICE_IDENTITY_REFUSED', 'SEEK_UNAVAILABLE'):
        need(not value['seek_end_completed'])
    if value['status'] == 'ABORTED_BEFORE_DRAIN':
        need(value['seek_end_completed'])
    if value['status'] in READ_STATUSES and value['status'] != 'OBSERVER_INTERRUPTED':
        need(value['case_launch_attempted'] and value['closing_custody'] != 'NOT_CHECKED')
    need(integer(value['records'], MAX_RECORDS) and integer(value['raw_bytes'], MAX_RAW_BYTES)
        and hash_value(value['framed_raw_sha256']) and hash_value(value['recognized_sha256']))
    keys(value['categories'], COUNTS);keys(value['unknown_reasons'], UNKNOWN_REASONS)
    need(all(integer(n, MAX_RECORDS) for n in value['categories'].values())
        and sum(value['categories'].values()) == value['records'])
    need(all(integer(n, MAX_RECORDS) for n in value['unknown_reasons'].values())
        and sum(value['unknown_reasons'].values()) == value['categories']['UNKNOWN_APPARMOR_RECORD'])
    count, samples = value['recognized_count'], value['samples']
    need(integer(count, MAX_RECORDS) and count == value['categories']['RECOGNIZED_PROFILE_CAPABILITY_DENIAL']
        and type(samples) is list and len(samples) == min(count, MAX_SAMPLES)
        and integer(value['samples_omitted'], MAX_RECORDS) and count == len(samples)+value['samples_omitted'])
    malformed = value['categories']['UNSUPPORTED_KMSG_HEADER']
    need(malformed in (0, 1) and (malformed == 1) is (value['status'] == 'RECORD_FRAMING_REFUSED'))
    valid_headers = value['records']-malformed
    discontinuity = value['sequence_discontinuity']
    if value['records'] == 0:
        need(value['raw_bytes'] == 0 and value['framed_raw_sha256'] == EMPTY_HASH)
    else:
        need(value['records'] <= value['raw_bytes'] <= value['records']*MAX_READ and value['case_launch_attempted'])
    if valid_headers == 0:
        need(value['first_sequence'] is None and value['last_sequence'] is None)
    else:
        need(integer(value['first_sequence']) and integer(value['last_sequence']))
    if value['status'] == 'SEQUENCE_DISCONTINUITY':
        keys(discontinuity, ('ordinal', 'previous_sequence', 'observed_sequence'))
        need(value['records'] >= 2 and malformed == 0
            and integer(discontinuity['ordinal'], MAX_RECORDS-1)
            and integer(discontinuity['previous_sequence']) and integer(discontinuity['observed_sequence'])
            and discontinuity['ordinal'] == value['records']-1
            and discontinuity['previous_sequence'] == value['first_sequence']+value['records']-2
            and discontinuity['observed_sequence'] == value['last_sequence']
            and discontinuity['observed_sequence'] != discontinuity['previous_sequence']+1)
    else:
        need(discontinuity is None)
        if valid_headers:
            need(value['last_sequence'] == value['first_sequence']+valid_headers-1)
    expected_errno = {'READ_EAGAIN':errno.EAGAIN, 'READ_LOSS_EPIPE':errno.EPIPE,
        'READ_EINVAL_UNSUPPORTED_SIZE_OR_API':errno.EINVAL}
    if value['status'] in expected_errno:
        need(value['errno'] == expected_errno[value['status']])
    elif value['status'] == 'READ_UNAVAILABLE':
        need(value['errno'] not in expected_errno.values())
    elif value['status'] not in ('OPEN_UNAVAILABLE', 'SEEK_UNAVAILABLE'):
        need(value['errno'] is None)
    if value['status'] == 'RECORD_COUNT_BOUND':
        need(value['records'] == MAX_RECORDS)
    if value['status'] == 'RAW_BYTE_BOUND':
        need(value['raw_bytes']+MAX_READ > MAX_RAW_BYTES)
    previous, sampled_bytes = -1, 0
    for row in samples:
        keys(row, ('ordinal', 'sequence', 'record', 'profile_role', 'operation',
            'capability_number', 'capability_name', 'class_field', 'audit_pid', 'comm',
            'comm_role', 'process_attribution'))
        number = row['capability_number']
        need(integer(row['ordinal'], MAX_RECORDS-1) and previous < row['ordinal'] < value['records']
            and integer(row['sequence']) and type(row['profile_role']) is str and row['profile_role'] in PROFILES.values()
            and type(row['operation']) is str and row['operation'] == 'CAPABLE'
            and integer(number, len(CAPABILITIES)-1) and type(row['capability_name']) is str
            and row['capability_name'] == CAPABILITIES[number]
            and type(row['class_field']) is str and row['class_field'] in ('CAP', 'NOT_PRESENT')
            and type(row['comm_role']) is str and row['comm_role'] in ('LITERAL_BWRAP', 'UNKNOWN')
            and type(row['process_attribution']) is str and row['process_attribution'] == 'UNESTABLISHED')
        expected = (discontinuity['observed_sequence'] if discontinuity is not None
            and row['ordinal'] == discontinuity['ordinal'] else value['first_sequence']+row['ordinal'])
        need(row['sequence'] == expected)
        previous = row['ordinal']
        for key, maximum in (('record', MAX_READ), ('audit_pid', 10), ('comm', 16)):
            validate_descriptor(row[key], maximum);need(row[key]['bytes'] > 0)
        need(row['record']['bytes'] > row['audit_pid']['bytes']+row['comm']['bytes'])
        sampled_bytes += row['record']['bytes']
        need((row['comm_role'] == 'LITERAL_BWRAP') is (row['comm'] == descriptor(b'bwrap')))
    # Samples are the first recognized rows; omitted recognized rows follow them.
    need(previous+1+value['samples_omitted'] <= value['records'])
    # Every unsampled record came from one nonempty read of at most MAX_READ.
    unsampled = value['records']-len(samples)
    need(sampled_bytes+unsampled <= value['raw_bytes'] <= sampled_bytes+unsampled*MAX_READ)
    if not value['samples_omitted']:
        need(value['recognized_sha256'] == sha(canonical(samples)))
    need(len(canonical(value)) <= MAX_PUBLIC_BYTES)
    return value


def read_complete(value):
    validate(value)
    return value['status'] == 'READ_EAGAIN' and value['closing_custody'] == 'MATCHED' and value['close_status'] == 'CLOSED'
