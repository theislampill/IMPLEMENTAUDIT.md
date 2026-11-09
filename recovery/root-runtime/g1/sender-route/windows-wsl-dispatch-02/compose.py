"""Build the scoped second revision from the verified first Windows transport."""
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
PREV=HERE.parent/'windows-wsl-dispatch'
UPSTREAM=HERE.parent/'recovered-g1-g3-root-binding-r2/author'
def read(path,pin=None):
    b=path.read_bytes()
    if pin is not None and hashlib.sha256(b).hexdigest()!=pin:raise ValueError(path.name)
    return b.decode()
def change(s,a,b):
    if s.count(a)!=1:raise ValueError(a)
    return s.replace(a,b)
def build():
    js=read(PREV/'dispatch.js','85305bf51dbff8b7104561937f0f0ce5113e9f3c441f1cb51b751b31d60fa4f2')
    start=js.index(' const loader=')
    end=js.index('\n const cmd=',start)
    loader=("import hashlib,os,pathlib,stat,sys; p=pathlib.Path(sys.argv[1]); pin=sys.argv[2]; "
        "mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns); "
        "s=p.lstat(); assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode) in (0o400,0o444) and 0<s.st_size<=1048576; "
        "fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC); "
        "opened=os.fstat(fd); assert mark(opened)==mark(s) and stat.S_ISREG(opened.st_mode) and not os.listxattr(fd); "
        "raw=os.pread(fd,s.st_size+1,0); assert len(raw)==s.st_size and hashlib.sha256(raw).hexdigest()==pin and mark(os.fstat(fd))==mark(s) and mark(p.lstat())==mark(s); "
        "os.close(fd); sys.argv=[str(p),*sys.argv[3:]]; exec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})")
    import json
    js=js[:start]+' const loader='+json.dumps(loader)+';'+js[end:]
    binder=read(PREV/'bind_dispatcher.py','b9c9f870cf2361a0abf1dd7090b5a4c6688a4f74891c6f7990ec3f28cada767a')
    binder=change(binder,'os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC','os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC')
    helper=read(UPSTREAM/'dispatcher_entry.py')
    helper=change(helper,'flags=os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC|','flags=os.O_WRONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC|')
    for n,data in {'dispatch.js':js,'bind_dispatcher.py':binder,'dispatcher_entry.py':helper}.items():
        (HERE/n).write_bytes(data.encode())
if __name__=='__main__':build()
