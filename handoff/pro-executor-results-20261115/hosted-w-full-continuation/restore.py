#!/usr/bin/env python3
"""Restore one retained, unexecuted Windows subject; never create its authority.

The workflow invokes the unchanged maintained execute command separately.
Capture retains observed bytes only; it cannot establish a failed effect's outcome.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import tarfile

ROOT = Path(r'D:\a\_temp\dg18-w-full-43721708486-1')
PINS = {
    'PREPARATION.json': (2435, 'a7017e0b6cbde535be6b83741800edd91e93190c0828af867beaf2c0e9d82190'),
    'operation/OPERATION.json': (43816, 'e0ac5d2992e44b45e838802c571fa84e27542aa72afab6ebb05c015e3207ec23'),
    'SUBJECT.tar': (3891200, 'a52764e3ffb8a9fca86e19c5417af84afa3c48a44d072d97454c29acad11f193'),
}
REFERENCE_NAMES = ('OWNER_GRANT_REFERENCE.txt',)


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def save(path, value):
    with path.open('xb') as stream:
        stream.write(value if isinstance(value, bytes) else canonical(value))


def physical(path):
    path = Path(path).absolute()
    need('..' not in path.parts, 'Parent traversal refused')
    for node in (path, *path.parents):
        info = node.lstat()
        need(not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400,
             'Alias/reparse path refused: ' + str(node))
    return path.resolve(strict=True)


def identity(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def pinned(path, expected):
    path = physical(path)
    need(path.is_file() and path.stat().st_size == expected[0], 'Original length differs: ' + str(path))
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == expected[1], 'Original digest differs: ' + str(path))
    return raw


def job_identity():
    need(os.environ.get('GITHUB_RUN_ID', '').isdigit() and os.environ.get('GITHUB_RUN_ATTEMPT') == '1',
         'This continuation is restricted to one first hosted attempt')
    return {'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': '1'}


def tar_members(archive):
    members = archive.getmembers()
    names = [m.name for m in members]
    need(len(members) == 223 and len(set(n.casefold() for n in names)) == 223,
         'Original archive member population differs')
    need(sum(m.isfile() for m in members) == 156 and sum(m.isdir() for m in members) == 67,
         'Original archive file/directory population differs')
    need(sum(m.size for m in members) == 3493153, 'Original subject byte population differs')
    for member in members:
        path = PurePosixPath(member.name)
        need(path.parts and path.parts[0] == 'subject' and str(path) == member.name
             and not path.is_absolute() and '..' not in path.parts
             and '\\' not in member.name and ':' not in member.name
             and (member.isfile() or member.isdir()), 'Unsafe original tar member')
    return members


def restore(args):
    out = physical(args.out.parent) / args.out.name
    out.mkdir(exist_ok=False)
    job = job_identity()
    owned = False
    try:
        artifact, source = physical(args.artifact), physical(args.source)
        raw = {name: pinned(artifact / name, pin) for name, pin in PINS.items()}
        plan = json.loads(raw['operation/OPERATION.json'])
        preparation = json.loads(raw['PREPARATION.json'])
        request, snapshot = plan['request'], plan['prepared']['snapshot']
        need(preparation['protected_execute_called'] is False,
             'Received operation is not the unexecuted preparation')
        need(str(source) == request['source_root'] and ROOT / 'subject' == Path(request['subject_root']),
             'Exact original source/subject paths are required')
        need(ROOT / 'operation/OPERATION.json' == Path(preparation['plan']['plan']),
             'Exact original operation location is required')
        need(Path(sys.executable).samefile(request['tools']['python']['path']),
             'The selected physical Python differs')
        for item in request['tools'].values():
            image = physical(item['path'])
            need(hashlib.sha256(image.read_bytes()).hexdigest() == item['sha256'],
                 'Original native executable changed: ' + str(image))
        for name, expected in snapshot['recorders'].items():
            pinned(source / 'scripts' / name, (expected['bytes'], expected['sha256']))
        references = {}
        for name in REFERENCE_NAMES:
            path = physical(Path(__file__).parent / name)
            need(path.is_file() and 0 < path.stat().st_size <= 8192, 'Actual external reference required: ' + name)
            body = path.read_bytes()
            need(body.decode('utf-8').strip() and b'\0' not in body, 'Empty or invalid external reference: ' + name)
            references[name] = identity(body)
            save(out / name, body)
        for name in ('TEMP', 'TMP'):
            os.environ[name] = str(physical(os.environ[name]))
            need(os.environ[name] == preparation['maintained_environment'][name],
                 'Original physical temporary directory differs: ' + name)
        physical(ROOT.parent)
        need(not os.path.lexists(ROOT), 'Original target exists; never overwrite or reset a previous attempt')
        ROOT.mkdir(exist_ok=False)
        owned = True
        save(out / 'RESTORATION_ATTEMPT.json', {**job, 'created_root': str(ROOT),
             'plan_sha256': PINS['operation/OPERATION.json'][1], 'protected_execute_called': False})
        inventory = []
        with tarfile.open(artifact / 'SUBJECT.tar', 'r:') as archive:
            members = tar_members(archive)
            archive.extractall(ROOT, members=members, filter='data')
            for member in members:
                restored = physical(ROOT / member.name)
                if member.isdir():
                    need(restored.is_dir(), 'Restored directory differs')
                    continue
                # The data filter intentionally adds owner write permission;
                # restore the exact pinned mode, including read-only Git objects.
                os.chmod(restored, member.mode)
                expected = archive.extractfile(member).read()
                actual = restored.read_bytes()
                need(actual == expected and stat.S_IMODE(restored.stat().st_mode) == member.mode,
                     'Restored member bytes/mode differ: ' + member.name)
                inventory.append({'path': member.name, **identity(actual), 'mode': member.mode})
            actual_names = {'subject', *('subject/' + p.relative_to(ROOT / 'subject').as_posix()
                                        for p in (ROOT / 'subject').rglob('*'))}
            need(actual_names == {m.name for m in members}, 'Restored population differs from the original')
        (ROOT / 'operation').mkdir()
        save(ROOT / 'operation/OPERATION.json', raw['operation/OPERATION.json'])
        spec = importlib.util.spec_from_file_location('received_windows_recorder', source / 'scripts/run-r0039-windows-resume.py')
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        observed = driver.source_snapshot(request)
        need(driver.Q.same_json(observed, snapshot), 'Restored source/subject/tools/environment differ from prepared snapshot')
        save(out / 'RESTORATION.json', {**job, 'status': 'EXACT_UNEXECUTED_SUBJECT_RESTORED',
             'original_artifact_id': 14163814811, 'original_run_id': 43721708486,
             'plan_sha256': PINS['operation/OPERATION.json'][1], 'source_snapshot': observed,
             'restored_files_before_source_readback': inventory, 'external_reference_files': references,
             'authority': 'REFERENCES_RECEIVED_BY_ROOT_NOT_AUTHENTICATED_BY_THIS_HELPER',
             'new_claims': 0, 'new_boundaries': 0, 'currentness_earned': False,
             'protected_execute_called': False})
        print('Exact unexecuted subject restored; maintained execute remains a separate operation.')
    except BaseException as error:
        save(out / 'RESTORATION_FAILURE.json', {**job, 'exception': type(error).__name__,
             'detail': str(error), 'owned_root_created': owned, 'protected_execute_called': False})
        raise


def capture(args):
    # This is an unqualified observation of this job's own restored namespace.
    # It never calls an owner, repairs a file, or removes an existing capture.
    if not args.out.exists():
        print('No restoration output exists; no subject capture attempted.')
        return
    out = physical(args.out)
    marker = out / 'RESTORATION_ATTEMPT.json'
    if not marker.exists():
        print('This job did not claim the restoration namespace; no subject capture attempted.')
        return
    record = json.loads(marker.read_bytes())
    need(all(record[k] == v for k, v in job_identity().items()) and record['created_root'] == str(ROOT),
         'Foreign restoration namespace; capture refused')
    try:
        subject = physical(ROOT / 'subject')
        paths = sorted(subject.rglob('*'))
        need(len(paths) <= 512, 'Observed subject population exceeds capture bound')
        inventory, total = [], 0
        for path in paths:
            physical(path)
            info = path.stat()
            need(stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode), 'Unexpected subject entry type')
            if path.is_file():
                need(info.st_size <= 2 * 1024 * 1024, 'Observed file exceeds capture bound')
                total += info.st_size
                need(total <= 12 * 1024 * 1024, 'Observed subject exceeds capture byte bound')
                inventory.append({'path': 'subject/' + path.relative_to(subject).as_posix(),
                                  **identity(path.read_bytes())})
        archive_path = out / 'SUBJECT_AFTER.tar'
        with tarfile.open(archive_path, 'x') as archive:
            archive.add(subject, arcname='subject')
        with tarfile.open(archive_path, 'r:') as archive:
            captured = {m.name: identity(archive.extractfile(m).read()) for m in archive.getmembers() if m.isfile()}
        need(captured == {item['path']: {'bytes': item['bytes'], 'sha256': item['sha256']} for item in inventory},
             'Subject changed while captured; retained archive is unverified')
        save(out / 'SUBJECT_CAPTURE.json', {**job_identity(),
             'status': 'UNQUALIFIED_POST_ATTEMPT_BYTES_RETAINED',
             'archive': identity(archive_path.read_bytes()), 'files': inventory,
             'authority': 'NO_CURRENTNESS_TRANSITION_OR_NATIVE_ACCEPTANCE',
             'automatic_retry': False, 'cleanup_or_compensation': False})
    except BaseException as error:
        save(out / 'SUBJECT_CAPTURE_FAILURE.json', {'exception': type(error).__name__,
             'detail': str(error), 'retained_archive_completeness': 'UNVERIFIED',
             'automatic_retry': False, 'cleanup_or_compensation': False})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    stage = subs.add_parser('restore')
    stage.add_argument('--artifact', type=Path, required=True)
    stage.add_argument('--source', type=Path, required=True)
    stage.add_argument('--out', type=Path, required=True)
    retain = subs.add_parser('capture')
    retain.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(os.name == 'nt' and sys.platform == 'win32', 'Authentic Windows required; no restoration attempted')
    (restore if args.action == 'restore' else capture)(args)


if __name__ == '__main__':
    main()
