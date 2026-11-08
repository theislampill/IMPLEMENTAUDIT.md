"""Generated exact two-module child loader; no current effect admission."""
import hashlib
import os
from pathlib import Path
import stat
import sys
import types
PINS = {'fs_protocol': {'bytes': 11788, 'sha256': 'b44eedcc53a94fae84370241b6c5928b3bf34821e9e05ce8fb8dc516c800d541'}, 'fs_command': {'bytes': 6160, 'sha256': 'cd6aae49b89fc3bc0da0a4c95bf903255f801eb2d8c811e5aaa52acd7299929c'}}
def main():
    root=Path(__file__).absolute().parent
    if root.resolve(strict=True)!=root:raise SystemExit('CHILD_CODE_PATH')
    for name in ('fs_protocol','fs_command'):
        path=root/(name+'.py');before=path.lstat();expected=PINS[name]
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size!=expected['bytes'] or before.st_mode&0o022:
            raise SystemExit('CHILD_CODE_SHAPE')
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            raw=os.read(fd,expected['bytes']+1);after=os.fstat(fd)
            if (after.st_dev,after.st_ino)!=(before.st_dev,before.st_ino) or len(raw)!=expected['bytes'] or hashlib.sha256(raw).hexdigest()!=expected['sha256']:
                raise SystemExit('CHILD_CODE_PIN')
        finally:os.close(fd)
        module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
        exec(compile(raw,str(path),'exec'),module.__dict__)
    sys.modules['fs_command'].child_main(sys.argv[1:])
if __name__=='__main__':main()
