"""Read actual public source and fresh receiving paths; never issue a runtime.

This is a one-shot observation helper for the selected existing production
workspace. Its output cannot replace recipient adoption, independent source or
combined review, fresh currentness, native evidence, or a protected launch grant.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

SOURCE_COMMIT = '205aeab7c93299b0666b261485ab5658d8e183de'
SOURCE_TREE = '9ffbaf95080092bf4a45b8772a97ed16068544a7'
MANIFEST_SHA = '328bfd9ba1711260d6efa19ed8fcf45651d375e7c3685b9ce50bd03f1c3803ee'


def checked(command, cwd):
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=30)
    if result.returncode:
        raise RuntimeError('READ_ONLY_GIT_FAILED')
    return result.stdout


def identity(path):
    value = path.lstat()
    return [value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid,
            value.st_nlink, value.st_size, value.st_mtime_ns, value.st_ctime_ns]


def main():
    source, workspace, manifest_path, output = map(Path, sys.argv[1:])
    for path in (source, workspace, manifest_path, output.parent):
        if not path.is_absolute() or path.resolve(strict=True) != path:
            raise RuntimeError('ACTUAL_CANONICAL_PATH_REQUIRED')
    acquisition = workspace/'public-acquisition'
    if source == workspace or source.is_relative_to(workspace) or workspace.is_relative_to(source):
        raise RuntimeError('DISJOINT_MAINTAINED_SOURCE_REQUIRED')
    if acquisition.exists() or list(workspace.iterdir()):
        raise RuntimeError('FRESH_EMPTY_WORKSPACE_REQUIRED')
    if stat.S_IMODE(workspace.stat().st_mode) != 0o700:
        raise RuntimeError('PRIVATE_OPERATION_PARENT_REQUIRED')
    head = checked(['git', 'rev-parse', 'HEAD', 'HEAD^{tree}'], source).decode().splitlines()
    if head != [SOURCE_COMMIT, SOURCE_TREE] or checked(['git', 'status', '--porcelain=v1', '-uall'], source):
        raise RuntimeError('EXACT_CLEAN_MAINTAINED_SOURCE_REQUIRED')
    raw = manifest_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA:
        raise RuntimeError('ORIGINAL_SOURCE_MANIFEST_PIN')
    manifest = json.loads(raw)
    if (manifest['commit'], manifest['tree'], manifest['file_count'], manifest['total_bytes']) != (
            SOURCE_COMMIT, SOURCE_TREE, 1766, 167023692):
        raise RuntimeError('ORIGINAL_SOURCE_POPULATION')
    git_rows = checked(['git', 'ls-tree', '-rz', 'HEAD'], source).split(b'\0')
    expected_git = {}
    for item in git_rows:
        if not item:
            continue
        left, path = item.split(b'\t', 1)
        mode, kind, blob = left.decode().split()
        if kind != 'blob':
            raise RuntimeError('BLOB_POPULATION_REQUIRED')
        expected_git[path.decode()] = (mode, blob)
    if set(expected_git) != {m['path'] for m in manifest['members']}:
        raise RuntimeError('EXACT_GIT_MANIFEST_POPULATION')
    total = 0
    for member in manifest['members']:
        rel = Path(member['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise RuntimeError('SOURCE_MEMBER_PATH')
        path = source/rel
        before = identity(path)
        if not stat.S_ISREG(before[2]) or before[5] != 1 or path.resolve(strict=True) != path:
            raise RuntimeError('REGULAR_SINGLE_LINK_SOURCE_REQUIRED')
        body = path.read_bytes()
        after = identity(path)
        mode = '100755' if stat.S_IMODE(after[2]) & 0o111 else '100644'
        blob = hashlib.sha1(b'blob %d\0'%len(body)+body).hexdigest()
        if before != after or (mode, blob) != expected_git[member['path']] or (
                len(body), hashlib.sha256(body).hexdigest(), mode, blob) != (
                member['bytes'], member['sha256'], member['mode'], member['git_blob']):
            raise RuntimeError('SOURCE_MEMBER_IDENTITY_OR_BYTES_CHANGED: '+member['path'])
        total += len(body)
    if total != 167023692 or checked(['git', 'status', '--porcelain=v1', '-uall'], source):
        raise RuntimeError('SOURCE_CLOSING_READBACK')
    if acquisition.exists() or list(workspace.iterdir()):
        raise RuntimeError('WORKSPACE_CLOSING_READBACK')
    report = dict(schema='root.G221.actual-public-path-observation.v1', actor='/root',
        successor='PRO-EXECUTOR-01, designated by owner', issuer_thread='PRO-EXECUTOR-01',
        observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE,
        maintained_source_root=str(source), workspace_root=str(workspace),
        receiver_output_root=str(acquisition), source_manifest_sha256=MANIFEST_SHA,
        source_file_count=1766, source_total_bytes=total,
        complete_physical_hash_and_git_blob_join=True, source_worktree_clean=True,
        workspace_empty=True, receiver_output_absent=True, workspace_mode='0700',
        workspace_identity=identity(workspace), source_root_identity=identity(source),
        effect_grant=False, recipient_adoption_issued=False, runtime_binding_issued=False,
        original_acceptance=False, native_currentness=False,
        remaining='Fresh recipient precedes final runtime/adoption binding; recheck actual currentness before use')
    with output.open('x') as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write('\n')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
