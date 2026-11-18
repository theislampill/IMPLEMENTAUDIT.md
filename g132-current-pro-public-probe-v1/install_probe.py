"""Copy one exact public source bundle to a fresh actual root directory only."""
import hashlib,json,os,re,stat,sys
from pathlib import Path,PurePosixPath
PIN='51997476c3dce0d593ff2fd9b37ec38e354be295824ca150a00ecba159963ef1'
def need(v,c):
 if not v:raise ValueError(c)
def read(p,maximum):
 need(p.is_absolute() and p.resolve(strict=True)==p and all(not x.is_symlink() for x in p.parents),'SOURCE_PATH')
 before=p.lstat();need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<before.st_size<=maximum,'SOURCE_BODY')
 mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  need(mark(os.fstat(fd))==mark(before) and not os.listxattr(fd),'SOURCE_OPEN')
  raw=os.pread(fd,maximum+1,0);need(len(raw)==before.st_size and mark(os.fstat(fd))==mark(before)==mark(p.lstat()),'SOURCE_CLOSE');return raw
 finally:os.close(fd)
def main():
 need([os.getuid(),os.geteuid(),os.getgid(),os.getegid()]==[0,0,0,0] and sys.flags.isolated and sys.dont_write_bytecode,'ACTUAL_ROOT_COPY_ONLY')
 need(len(sys.argv)==3,'EXACT_COPY_ARGUMENTS');source=Path(sys.argv[1]);target=Path(sys.argv[2])
 need(target.parent==Path('/') and re.fullmatch('g132-public-probe-[1-9][0-9]{0,19}-a1',target.name) and not os.path.lexists(target),'FRESH_PUBLIC_ROOT')
 raw=read(source/'BUNDLE_MANIFEST.json',65536);need(hashlib.sha256(raw).hexdigest()==PIN,'FIXED_PUBLIC_BUNDLE')
 manifest=json.loads(raw);files=manifest['files'];need(0<len(files)<=200 and sum(p['bytes'] for p in files.values())<=16*1024**2,'PUBLIC_COPY_BOUND')
 target.mkdir(mode=0o700)
 for name,pin in sorted(files.items()):
  path=PurePosixPath(name);need(str(path)==name and not path.is_absolute() and '..' not in path.parts,'FIXED_PUBLIC_MEMBER')
  body=read(source/'bundle'/name,1024**2);need({'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}==pin,'PUBLIC_BODY_PIN')
  out=target/name;out.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
  fd=os.open(out,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC,0o400)
  try:
   view=memoryview(body)
   while view:
    n=os.write(fd,view);need(n>0,'COPY_PROGRESS');view=view[n:]
   os.fsync(fd)
  finally:os.close(fd)
  need(read(out,1024**2)==body,'PUBLIC_COPY_READBACK')
 print(json.dumps({'scope':'PUBLIC_PROBE_SOURCE_COPY_ONLY','source_members':len(files),'original_stage_started':False}))
if __name__=='__main__':main()
