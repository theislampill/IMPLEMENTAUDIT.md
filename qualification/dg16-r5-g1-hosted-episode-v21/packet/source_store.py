#!/usr/bin/env python3
"""Complete only the loose storage of the already selected published HEAD.

Git hash-object may leave an existing packed object packed. A fresh private
object directory makes the maintained Git command produce its ordinary loose
representation. Only those verified bytes are copied exclusively into an absent
slot in the fresh checkout. No commit identity, ref, parent or pack is changed.
"""
import hashlib
import os
from pathlib import Path
import stat
import zlib

LIMIT=1024**2


def need(value,code):
    if not value:raise ValueError(code)


def commit_body(raw, expected_oid, expected_tree=None, expected_parent=None):
    need(type(raw) is bytes and 0<len(raw)<=LIMIT,'COMMIT_BODY_BOUND')
    need(type(expected_oid) is str and len(expected_oid)==40 and all(c in '0123456789abcdef' for c in expected_oid),'COMMIT_OID_SHAPE')
    whole=b'commit '+str(len(raw)).encode()+b'\0'+raw
    need(hashlib.sha1(whole).hexdigest()==expected_oid,'COMMIT_OBJECT_ID_DIFFERS')
    header,separator,_=raw.partition(b'\n\n');need(separator,'COMMIT_HEADER_UNTERMINATED')
    lines=header.splitlines();need(lines and lines[0].startswith(b'tree '),'COMMIT_TREE_MISSING')
    tree=lines[0][5:].decode('ascii','strict')
    parents=[line[7:].decode('ascii','strict') for line in lines if line.startswith(b'parent ')]
    need(len(tree)==40 and all(c in '0123456789abcdef' for c in tree)
         and all(len(p)==40 and all(c in '0123456789abcdef' for c in p) for p in parents),'COMMIT_IDENTITY_SHAPE')
    if expected_tree is not None:need(tree==expected_tree,'COMMIT_TREE_DIFFERS')
    if expected_parent is not None:need(parents==[expected_parent],'COMMIT_PARENT_DIFFERS')
    return dict(oid=expected_oid,tree=tree,parents=parents,body_bytes=len(raw),body_sha256=hashlib.sha256(raw).hexdigest())


def verify_loose(raw, body, oid):
    need(type(raw) is bytes and 0<len(raw)<=LIMIT,'LOOSE_OBJECT_BOUND')
    decoder=zlib.decompressobj();whole=decoder.decompress(raw,LIMIT+1)
    need(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
         and len(whole)<=LIMIT,'LOOSE_OBJECT_ENCODING_REFUSED')
    need(whole==b'commit '+str(len(body)).encode()+b'\0'+body
         and hashlib.sha1(whole).hexdigest()==oid,'LOOSE_OBJECT_BODY_DIFFERS')
    return dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def preserved_storage(source, read_regular):
    """Close the actual refs and packs; hashes are private preparation evidence."""
    git=Path(source)/'.git';rows={};total=0
    for selected in ('refs','objects/pack'):
        base=git/selected
        need(base.is_dir() and not base.is_symlink(),'PRESERVED_STORAGE_DIRECTORY_REQUIRED')
        for parent,dirs,files in os.walk(base,followlinks=False):
            for name in dirs:
                path=Path(parent)/name;info=path.lstat()
                need(stat.S_ISDIR(info.st_mode) and info.st_uid==os.geteuid()
                     and not info.st_mode&0o022,'PRESERVED_STORAGE_DIRECTORY_REFUSED')
            for name in files:
                path=Path(parent)/name;raw=read_regular(path,128*1024**2);total+=len(raw)
                need(total<=256*1024**2 and len(rows)<4096,'PRESERVED_STORAGE_BOUND')
                rows[path.relative_to(git).as_posix()]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    packed=git/'packed-refs'
    if packed.exists() or packed.is_symlink():
        raw=read_regular(packed,LIMIT);rows['packed-refs']={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    return rows


def retain_actual_head(source, private, oid, tree, command, read_regular, write_private):
    source,private=Path(source),Path(private)
    preserved=preserved_storage(source,read_regular)
    rc,body,err=command('selected-head-body',['/usr/bin/git','-C',str(source),'cat-file','commit','HEAD'],seconds=20)
    need(rc==0 and not err,'HEAD_BODY_READ_REFUSED')
    identity=commit_body(body,oid,tree)
    need(read_regular(source/'.git/HEAD',1024)==(oid+'\n').encode(),'DETACHED_SELECTED_HEAD_REQUIRED')
    target=source/'.git/objects'/oid[:2]/oid[2:]
    if target.exists() or target.is_symlink():
        retained=verify_loose(read_regular(target,LIMIT),body,oid)
        need(preserved_storage(source,read_regular)==preserved,'REF_OR_PACK_STORAGE_CHANGED')
        return dict(status='EXISTING_ACTUAL_LOOSE_HEAD_VERIFIED',identity=identity,loose=retained,refs_changed=False,packs_removed=False)
    body_path=private/'selected-head.body';write_private(body_path,body)
    store=private/'fresh-head-object-store';store.mkdir(mode=0o700,exist_ok=False)
    # This fixed shell only redirects the exact held body into the maintained
    # Git command. None of its operands is evaluated as shell source.
    argv=['/usr/bin/env','GIT_OBJECT_DIRECTORY='+str(store),'/usr/bin/bash','-c',
        'exec /usr/bin/git -C "$1" hash-object -w -t commit --stdin < "$2"',
        'r5-c5-retain-head',str(source),str(body_path)]
    rc,out,err=command('write-selected-head-loose',argv,seconds=20)
    need(rc==0 and not err and out==(oid+'\n').encode(),'GIT_LOOSE_HEAD_WRITE_REFUSED')
    generated=read_regular(store/oid[:2]/oid[2:],LIMIT);retained=verify_loose(generated,body,oid)
    objects=source/'.git/objects';before=objects.lstat()
    need(stat.S_ISDIR(before.st_mode) and before.st_uid==os.geteuid()==0 and not before.st_mode&0o022,'OBJECT_STORE_CUSTODY_REFUSED')
    parent=os.open(objects,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    directory=None
    try:
        need((os.fstat(parent).st_dev,os.fstat(parent).st_ino)==(before.st_dev,before.st_ino),
             'OBJECT_STORE_OPEN_CHANGED')
        try:os.mkdir(oid[:2],0o755,dir_fd=parent)
        except FileExistsError:pass
        directory=os.open(oid[:2],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
        info=os.fstat(directory)
        need(info.st_uid==0 and not info.st_mode&0o022,'LOOSE_PREFIX_CUSTODY_REFUSED')
        fd=os.open(oid[2:],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o444,dir_fd=directory)
        try:
            with os.fdopen(fd,'wb',closefd=False) as stream:
                stream.write(generated);stream.flush();os.fsync(fd)
        finally:os.close(fd)
        os.fsync(directory);os.fsync(parent)
    finally:
        if directory is not None:os.close(directory)
        os.close(parent)
    need(read_regular(target,LIMIT)==generated,'LOOSE_HEAD_READBACK_DIFFERS')
    need(read_regular(source/'.git/HEAD',1024)==(oid+'\n').encode(),'SELECTED_HEAD_CHANGED')
    need((objects.lstat().st_dev,objects.lstat().st_ino)==(before.st_dev,before.st_ino)
         and preserved_storage(source,read_regular)==preserved,'REF_OR_PACK_STORAGE_CHANGED')
    return dict(status='ACTUAL_GIT_GENERATED_LOOSE_HEAD_RETAINED',identity=identity,loose=retained,
        refs_changed=False,packs_removed=False,new_commit_created=False)
