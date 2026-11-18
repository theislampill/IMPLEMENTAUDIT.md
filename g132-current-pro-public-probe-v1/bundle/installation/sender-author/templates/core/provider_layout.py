#!/usr/bin/env python3
"""One explicit layout conversion immediately after fresh owned provisioning.

This is not a repair for an existing provider. The enclosing reviewed adapter
must have just allocated provider05 exclusively and completed the unchanged
fixed-wheel/RECORD recipe. Any refusal consumes that attempted provider; no
retry, chmod/chown, prior-provider mutation or best-effort repair is supported.
"""
import hashlib
import os
from pathlib import Path
import stat

ROOT='/usr/lib/implementaudit-c5-r5-hosted-python312-05-v1'
PYTHON_BYTES=8020928
PYTHON_SHA256='e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f'


def need(value, code):
    if not value: raise ValueError(code)


def stamp(info):
    return (info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,
        info.st_mtime_ns,info.st_ctime_ns,info.st_uid,info.st_gid)


def copy_descriptor(info, raw):
    need(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode)==0o755
         and info.st_nlink==1 and info.st_uid==info.st_gid==0 and info.st_size==PYTHON_BYTES
         and len(raw)==PYTHON_BYTES and hashlib.sha256(raw).hexdigest()==PYTHON_SHA256,
         'FRESH_EXACT_OWNED_INTERPRETER_COPY_REQUIRED')
    return dict(identity=list(stamp(info)),bytes=len(raw),sha256=PYTHON_SHA256,mode=0o755,uid=0,gid=0)


def convert_fresh_owned_provider05(root):
    root=Path(root)
    need(str(root)==ROOT and os.getuid()==os.geteuid()==os.getgid()==os.getegid()==0,
         'EXACT_FRESH_ROOT_PROVIDER_REQUIRED')
    ancestry={}
    for path in reversed((root/'bin',*(root/'bin').parents)):
        info=path.lstat()
        need(stat.S_ISDIR(info.st_mode) and info.st_uid==info.st_gid==0
             and not info.st_mode&0o022 and not path.is_symlink(),'TRUSTED_PROVIDER_ANCESTRY_REQUIRED')
        ancestry[str(path)]=stamp(info)
    fd=os.open(root/'bin',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    copies={};result=dict(status='INCOMPLETE',canonical='bin/python3.12',aliases={},authority='NONE')
    try:
        need(stamp(os.fstat(fd))==ancestry[str(root/'bin')],'PROVIDER_BIN_CHANGED')
        for name in ('python','python3','python3.12'):
            before=os.stat(name,dir_fd=fd,follow_symlinks=False)
            file_fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=fd)
            try:
                need(stamp(os.fstat(file_fd))==stamp(before) and not os.listxattr(file_fd),'INTERPRETER_COPY_CHANGED')
                with os.fdopen(file_fd,'rb',closefd=False) as stream: raw=stream.read(PYTHON_BYTES+1)
                copies[name]=copy_descriptor(before,raw)
                need(stamp(os.fstat(file_fd))==stamp(before)
                     and stamp(os.stat(name,dir_fd=fd,follow_symlinks=False))==stamp(before),'INTERPRETER_COPY_CHANGED')
            finally: os.close(file_fd)
        need(len({tuple(row['identity'][:2]) for row in copies.values()})==3,'COPIES_MUST_BE_DISTINCT_OWNED_OBJECTS')
        for name in ('python','python3'):
            # Revalidate every fixed copy immediately before each bounded write.
            for untouched in ('python3.12',name):
                need(list(stamp(os.stat(untouched,dir_fd=fd,follow_symlinks=False)))==copies[untouched]['identity'],
                     'INTERPRETER_COPY_CHANGED_BEFORE_CONVERSION')
            os.unlink(name,dir_fd=fd)
            os.symlink('python3.12',name,dir_fd=fd)
            info=os.stat(name,dir_fd=fd,follow_symlinks=False)
            need(stat.S_ISLNK(info.st_mode) and info.st_uid==info.st_gid==0 and info.st_nlink==1
                 and os.readlink(name,dir_fd=fd)=='python3.12' and not os.listxattr(root/'bin'/name,follow_symlinks=False),
                 'NEW_ALIAS_READBACK_REFUSED')
            result['aliases']['bin/'+name]=dict(target='python3.12',identity=list(stamp(info)),copied_preimage=copies[name])
        os.fsync(fd)
        need(list(stamp(os.stat('python3.12',dir_fd=fd,follow_symlinks=False)))==copies['python3.12']['identity'],
             'CANONICAL_COPY_CHANGED')
        for path,opening in ancestry.items():
            observed=stamp(Path(path).lstat())
            # The bin namespace legitimately changes; its identity/type/owner
            # stays fixed. All other ancestor metadata remains exact.
            selected=(0,1,2,7,8) if path==str(root/'bin') else range(len(opening))
            need(all(observed[i]==opening[i] for i in selected),'PROVIDER_ANCESTRY_CHANGED')
        result.update(status='ONE_OWNED_COPY_TWO_RELATIVE_ALIASES_PREPARED_NATIVE_UNQUALIFIED',canonical_copy=copies['python3.12'])
        return result
    finally: os.close(fd)


if __name__=='__main__':
    raise SystemExit('CALL_IMMEDIATELY_AFTER_REVIEWED_EXCLUSIVE_PROVIDER05_ALLOCATION')
