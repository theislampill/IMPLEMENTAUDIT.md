#!/usr/bin/env python3
"""Reproduce the current binding of the exact original M5 source runner.

Offline source engineering only. This script does not execute routes, install
dependencies, contact GitHub, issue authority, or publish a branch.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
ORIGINAL_COMMIT = '9493cb25ec976aebb056191ec4eafa086d6b44d6'
OLD_SOURCE = '8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b'
OLD_TREE = '0da374609f7fea2463a2926f3603b976620bd10e'
OLD_BRANCH = 'pro/dg16-r5-installed-runtime-05r7-20261106'
SOURCE_COMMIT = '205aeab7c93299b0666b261485ab5658d8e183de'
SOURCE_TREE = '9ffbaf95080092bf4a45b8772a97ed16068544a7'
BRANCH = 'engineering/pro-executor-dg16-m5-source-20261115'
PREFIX = 'qualification/dg16-installed-runtime05/'
WORKFLOW = '.github/workflows/dg16-installed-runtime05.yml'
BINDING = 'handoff/dg16-m5-source-20261115/CURRENT_BINDING.json'
ORIGINAL = {
    'run.py': (74835, 'fbcb15e3c154b6558ffdac49cb86cccc8a727c67d668b3718bbda5d1a0e866c0'),
    'installed_runtime.py': (29033, '9a511c8010fd29f4c10c96d366d786660e4613e34e6fe00fdb73e0c34f2a772a'),
    'host_support.py': (9406, '17ca3afa3d32d95c39da704229a191099f789493f8b0c15b39098ffc57516166'),
    'host_utility.py': (54556, '429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'),
    'SOURCE_MANIFEST.json': (493323, '466aa14af0ff6e2cde20bb2727511625b7297cfa00a3b4d529b11492f5b4486f'),
    'workflow.yml': (16958, 'f89a46811b3ddb88084f7492caa561f50329fc7712c5a6c088612c9a24efb244'),
}


def need(value, message):
    if not value:
        raise RuntimeError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def git(source, *arguments):
    return subprocess.check_output(['git', '-C', str(source), *arguments], stderr=subprocess.PIPE)


def source_manifest(source):
    need(git(source, 'rev-parse', 'HEAD', 'HEAD^{tree}').decode().splitlines() ==
         [SOURCE_COMMIT, SOURCE_TREE], 'SELECTED_SOURCE_IDENTITY_REFUSED')
    need(git(source, 'status', '--porcelain=v1', '--untracked-files=all') == b'', 'SELECTED_SOURCE_DIRTY')
    rows = []
    for entry in git(source, 'ls-tree', '-rz', '--full-tree', 'HEAD').split(b'\0'):
        if not entry:
            continue
        header, name = entry.split(b'\t', 1)
        mode, kind, oid = header.decode('ascii').split()
        relative = name.decode('utf-8')
        need(mode in ('100644', '100755') and kind == 'blob', 'SOURCE_TREE_LEAF_REFUSED')
        path = source / relative
        info = path.lstat()
        need(stat.S_ISREG(info.st_mode) and not info.st_mode & 0o6000 and
             bool(info.st_mode & 0o111) == (mode == '100755'), 'SOURCE_WORKTREE_MODE_REFUSED')
        raw = path.read_bytes()
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == oid,
             'SOURCE_WORKTREE_BLOB_REFUSED')
        rows.append({'path': relative, 'mode': mode, 'git_blob': oid, 'bytes': len(raw), 'sha256': sha(raw)})
    rows.sort(key=lambda row: row['path'])
    total = sum(row['bytes'] for row in rows)
    need(len(rows) == 1766 and total == 167023692, 'CURRENT_SOURCE_POPULATION_REFUSED')
    need(git(source, 'status', '--porcelain=v1', '--untracked-files=all') == b'', 'SELECTED_SOURCE_CHANGED')
    return canonical({'schema': 'dg16.linux-native-source-manifest.v2', 'repository': REPOSITORY,
                      'commit': SOURCE_COMMIT, 'tree': SOURCE_TREE, 'file_count': len(rows),
                      'total_bytes': total, 'members': rows})


def replace(text, old, new, count=1):
    need(text.count(old) == count, 'ORIGINAL_REPLACEMENT_POPULATION_REFUSED: ' + old)
    return text.replace(old, new)


def assignment(text, name, old, new):
    return replace(text, name + ' = ' + repr(old) + '\n', name + ' = ' + repr(new) + '\n')


def rebind(original_dir, source):
    original = {}
    for name, (size, digest) in ORIGINAL.items():
        path = original_dir / name
        need(path.is_file() and not path.is_symlink(), 'ORIGINAL_FILE_SHAPE_REFUSED: ' + name)
        raw = path.read_bytes()
        need(len(raw) == size and sha(raw) == digest, 'ORIGINAL_FILE_DIGEST_REFUSED: ' + name)
        original[name] = raw
    manifest = source_manifest(source)
    manifest_sha = sha(manifest)
    result = {'SOURCE_MANIFEST.json': manifest, 'host_utility.py': original['host_utility.py']}
    for name in ('installed_runtime.py', 'host_support.py', 'run.py'):
        text = original[name].decode('utf-8')
        text = assignment(text, 'SOURCE_COMMIT', OLD_SOURCE, SOURCE_COMMIT)
        text = assignment(text, 'SOURCE_TREE', OLD_TREE, SOURCE_TREE)
        if name in ('host_support.py', 'run.py'):
            text = assignment(text, 'MANIFEST_SHA', ORIGINAL['SOURCE_MANIFEST.json'][1], manifest_sha)
        if name == 'host_support.py':
            text = replace(text, "m['file_count']==1759", "m['file_count']==1766")
            text = replace(text, "m['total_bytes']==166402972 and len(m['members'])==1759",
                           "m['total_bytes']==167023692 and len(m['members'])==1766")
            text = replace(text, 'total==166402972', 'total==167023692')
        if name == 'run.py':
            text = assignment(text, 'BRANCH', OLD_BRANCH, BRANCH)
            text = assignment(text, 'SUPPORT_SHA', ORIGINAL['host_support.py'][1], sha(result['host_support.py']))
            text = assignment(text, 'INSTALLED_SHA', ORIGINAL['installed_runtime.py'][1], sha(result['installed_runtime.py']))
            text = replace(text, "'file_count':1759,'total_bytes':166402972",
                           "'file_count':1766,'total_bytes':167023692", count=3)
        result[name] = text.encode('utf-8')
    workflow = original['workflow.yml'].decode('utf-8')
    workflow = replace(workflow, 'name: DG16 installed runtime 05\n',
                       'name: DG16 M5 current source qualification\n')
    workflow = replace(workflow, OLD_BRANCH, BRANCH, count=2)
    workflow = replace(workflow, OLD_SOURCE, SOURCE_COMMIT)
    workflow = replace(workflow, ORIGINAL['run.py'][1], sha(result['run.py']), count=17)
    result['workflow.yml'] = workflow.encode('utf-8')
    files = {WORKFLOW if name == 'workflow.yml' else PREFIX + name: raw for name, raw in result.items()}
    bindings = []
    for name in ORIGINAL:
        path = WORKFLOW if name == 'workflow.yml' else PREFIX + name
        bindings.append({'path': path, 'original_bytes': len(original[name]), 'original_sha256': sha(original[name]),
                         'current_bytes': len(result[name]), 'current_sha256': sha(result[name]),
                         'byte_identical': original[name] == result[name]})
    files[BINDING] = canonical({
        'schema': 'dg16.m5-current-source-binding.v1', 'repository': REPOSITORY,
        'original_runner_commit': ORIGINAL_COMMIT, 'original_source_commit': OLD_SOURCE, 'original_source_tree': OLD_TREE,
        'source_commit': SOURCE_COMMIT, 'source_tree': SOURCE_TREE, 'source_manifest_sha256': manifest_sha,
        'file_count': 1766, 'total_bytes': 167023692, 'prospective_branch': BRANCH,
        'authority': 'NONE', 'original_acceptance': False, 'native_operation_authorized': False,
        'historical_credit_relabelled': False, 'host_profile_changed': False, 'route_semantics_changed': False,
        'members': bindings,
        'scope': 'CURRENT_SOURCE_FOUR_DISPOSABLE_LINUX_ROUTES; LIVE_RESULT_PENDING',
        'budget': {'cap_bytes': 589824, 'reserve_bytes': 2000, 'revision': 4},
    })
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-dir', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    original = args.original_dir.resolve(strict=True)
    repository = args.repository.resolve(strict=True)
    need(repository != source and not repository.is_relative_to(source) and
         not original.is_relative_to(repository), 'ISOLATED_OUTPUT_REQUIRED')
    files = rebind(original, source)
    for relative, raw in files.items():
        destination = repository / relative
        if args.check:
            need(destination.is_file() and not destination.is_symlink() and destination.read_bytes() == raw,
                 'GENERATED_BINDING_MISMATCH: ' + relative)
        else:
            if destination.exists():
                need(destination.is_file() and not destination.is_symlink() and destination.read_bytes() == raw,
                     'REFUSE_OVERWRITE_DIFFERENT_CANDIDATE: ' + relative)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open('xb') as stream:
                    stream.write(raw)
                os.chmod(destination, 0o644)
    print(json.dumps({'status': 'VERIFIED' if args.check else 'GENERATED', 'files': len(files),
                      'source_commit': SOURCE_COMMIT, 'source_tree': SOURCE_TREE, 'authority': 'NONE'}, sort_keys=True))


if __name__ == '__main__':
    main()
