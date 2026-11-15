"""Fixed external tool-adoption receiving entry; whole immutable workflow must bind this file."""
import hashlib
import os
from pathlib import Path
import stat
import sys
import types

COMMON_SHA256 = '5d8fc0f0a25b80f611536a15da882b71047d760a2e42120abdcf12f1cc1f578d'

def main():
    if len(sys.argv)!=1 or sys.flags.isolated!=1 or sys.dont_write_bytecode is not True:
        raise ValueError('FIXED_ISOLATED_ENTRY_ONLY')
    path=Path(__file__).absolute().with_name('entry_common.py')
    info=path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or not 0<info.st_size<=1024*1024:
        raise ValueError('ENTRY_COMMON_SHAPE')
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK)
    stamp=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid)
    try:
        raw=os.pread(fd,1024*1024+1,0)
        if (len(raw)!=info.st_size or hashlib.sha256(raw).hexdigest()!=COMMON_SHA256
            or stamp(os.fstat(fd))!=stamp(info) or stamp(path.lstat())!=stamp(info) or os.listxattr(fd)):
            raise ValueError('ENTRY_COMMON_PIN')
    finally:os.close(fd)
    entry=types.ModuleType('exact_external_carrier_entry');entry.__file__=str(path)
    exec(compile(raw,str(path),'exec'),entry.__dict__)
    value=entry.adopt_tools();entry.emit_tools(value)
    return 0 if value['status']=='ADOPTED' else 1

if __name__=='__main__':
    try:code=main()
    except BaseException:
        print('{"authority":"NONE","code":"EXTERNAL_ENTRY_OR_CURRENTNESS_REFUSED","original_awards":[],"schema":"dg16.core-private-carrier-entry-refusal.v1","status":"REFUSED"}',flush=True)
        code=1
    raise SystemExit(code)
