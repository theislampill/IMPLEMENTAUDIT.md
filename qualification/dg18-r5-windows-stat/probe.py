#!/usr/bin/env python3
"""One bounded Windows metadata observation; no claim/controller execution."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import time

SOURCE_COMMIT = '539aa846e37eab2dd527912d5e5eaa95f69d61cf'
COMPANION = 'skills/implementaudit/scripts/claim-run-rotation.py'
SOURCE_BYTES = 288439
SOURCE_SHA256 = 'ce40c4410011e46b209df718207b58c15d18e60db1379e7b66b24f04616637f9'
FIELDS = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_ctime_ns', 'st_mtime_ns')


def require(value, label):
    if not value:
        raise RuntimeError(label)


def metadata(info):
    result = {name: int(getattr(info, name)) for name in FIELDS}
    result['st_birthtime_ns'] = int(info.st_birthtime_ns)
    result['st_file_attributes'] = int(info.st_file_attributes)
    require(all(-(1 << 127) <= v < (1 << 128) for v in result.values()), 'METADATA_RANGE')
    return result


def capture(path, expected_bytes, expected_sha256):
    before = os.lstat(path)
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
            'SOURCE_NOT_SINGLE_LINK_REGULAR')
    require(not before.st_file_attributes & 0x400, 'SOURCE_REPARSE_POINT')
    require(before.st_size == expected_bytes, 'SOURCE_SIZE')
    descriptor = os.open(path, os.O_RDONLY | os.O_BINARY | getattr(os, 'O_NOFOLLOW', 0)
                         | getattr(os, 'O_NONBLOCK', 0))
    with os.fdopen(descriptor, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(expected_bytes + 1)
        after = os.fstat(stream.fileno())
        current = os.lstat(path)
    require(len(raw) == expected_bytes and hashlib.sha256(raw).hexdigest() == expected_sha256,
            'SOURCE_BYTES_OR_DIGEST')
    values = dict(zip(('path_before', 'fd_opened', 'fd_after', 'path_current'),
                      map(metadata, (before, opened, after, current))))
    comparisons = {}
    for left, right in (('path_before', 'fd_opened'), ('fd_opened', 'fd_after'),
                        ('fd_after', 'path_current'), ('path_before', 'path_current')):
        comparisons[left + '__' + right] = [name for name in FIELDS
                                           if values[left][name] != values[right][name]]
    return {'observations': values, 'differing_original_fields': comparisons,
            'original_seven_field_chain_equal': all(not v for v in comparisons.values()),
            'captured_bytes': len(raw), 'captured_sha256': hashlib.sha256(raw).hexdigest(),
            'descriptor_closed': True, 'scope': 'ONE_NONATOMIC_SEQUENCE_NO_ORIGIN_OR_CONTINUITY_PROOF'}


def write_owned(path, data):
    with path.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(os.name == 'nt' and sys.version_info[:3] == (3, 12, 10), 'EXACT_WINDOWS_PYTHON_REQUIRED')
    require(os.environ.get('GITHUB_RUN_ATTEMPT') == '1', 'ONE_ATTEMPT_REQUIRED')
    run_id = os.environ.get('GITHUB_RUN_ID', '')
    require(run_id.isascii() and run_id.isdecimal(), 'RUN_ID_REQUIRED')
    require(args.output.name == 'dg18-win-stat-' + run_id + '-1', 'OUTPUT_IDENTITY')
    require(args.output.parent.resolve() == Path(os.environ['RUNNER_TEMP']).resolve(), 'OUTPUT_PARENT')
    args.output.mkdir(exist_ok=False)
    source = args.source / COMPANION
    result = {'schema': 'dg18.windows-stat-observation.v1', 'status': 'OBSERVATION_ONLY',
              'run_id': run_id, 'attempt': 1, 'python': '3.12.10',
              'platform': 'Windows', 'source_commit': SOURCE_COMMIT,
              'source_companion': COMPANION, 'source_sha256': SOURCE_SHA256,
              'source': capture(source, SOURCE_BYTES, SOURCE_SHA256),
              'authority': 'NONE', 'owner_calls': 0, 'original_acceptance_delta': 0,
              'historical_failed_field_not_observed': True}
    control = args.output / 'owned-control.bin'
    initial = b'owned metadata control before\n'
    changed = b'owned metadata control after!\n'
    write_owned(control, initial)
    result['new_owned_file'] = capture(control, len(initial), hashlib.sha256(initial).hexdigest())
    # One deliberate 50ms separation makes the controlled rewrite observable;
    # no retry loop or wait for any owner/host event is involved.
    time.sleep(0.05)
    with control.open('r+b') as stream:
        mutation_before = metadata(os.fstat(stream.fileno()))
        stream.seek(0)
        stream.write(changed)
        stream.truncate()
        stream.flush()
        os.fsync(stream.fileno())
        mutation_after = metadata(os.fstat(stream.fileno()))
    result['owned_write_control'] = {'fd_before': mutation_before, 'fd_after': mutation_after,
        'differing_fields': [n for n in FIELDS if mutation_before[n] != mutation_after[n]],
        'descriptor_closed': True}
    result['rewritten_owned_file'] = capture(control, len(changed), hashlib.sha256(changed).hexdigest())
    control.unlink()
    result['owned_control_removed'] = not control.exists()
    raw = (json.dumps(result, sort_keys=True, indent=2) + '\n').encode('utf-8')
    require(len(raw) <= 32768, 'OUTPUT_LIMIT')
    (args.output / 'OBSERVATION.json').write_bytes(raw)
    require((args.output / 'OBSERVATION.json').read_bytes() == raw, 'OUTPUT_READBACK')
    envelope = {'name': 'OBSERVATION.json', 'bytes': len(raw),
                'sha256': hashlib.sha256(raw).hexdigest(), 'utf8_json': raw.decode('utf-8')}
    print('DG18_WIN_STAT_JSON ' + json.dumps(envelope, ensure_ascii=True, separators=(',', ':')))


if __name__ == '__main__':
    main()
