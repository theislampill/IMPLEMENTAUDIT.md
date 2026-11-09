"""One fixed bootstrap entry, externally pinned by the actual received tree.

No path argument, repair, runtime role selector, sender or native operation.
The root-issued admission is a literal hash input; this entry cannot issue it.
"""
import hashlib,json,os,re,stat,sys,types
from pathlib import Path
BRANCH=None
PLACEMENT_DESCRIPTOR=None
MANIFEST_SHA256=None
ADMISSION_SHA256=None

def need(v,c):
 if not v:raise ValueError(c)
def read(p,limit):
 s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and 0<=s.st_size<=limit,'BOOTSTRAP_FILE_CUSTODY')
 stamp=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  need(stamp(os.fstat(fd))==stamp(s) and not os.listxattr(fd),'BOOTSTRAP_OPEN_CHANGED');raw=os.pread(fd,limit+1,0)
  need(len(raw)==s.st_size and stamp(os.fstat(fd))==stamp(s) and stamp(p.lstat())==stamp(s),'BOOTSTRAP_BODY_CHANGED');return raw
 finally:os.close(fd)
def context():
 e=os.environ;run=e.get('GITHUB_RUN_ID','');commit=e.get('GITHUB_SHA','')
 need(sys.flags.isolated==1 and sys.dont_write_bytecode and len(sys.argv)==1,'BOOTSTRAP_FIXED_ENTRY')
 need(type(BRANCH) is str and e.get('GITHUB_ACTIONS')=='true' and e.get('RUNNER_ENVIRONMENT')=='github-hosted' and e.get('GITHUB_REPOSITORY')=='theislampill/IMPLEMENTAUDIT.md' and e.get('GITHUB_EVENT_NAME')=='push' and e.get('GITHUB_REF')=='refs/heads/'+BRANCH and e.get('GITHUB_RUN_ATTEMPT')=='1' and e.get('GITHUB_JOB')=='qualify' and re.fullmatch('[1-9][0-9]{5,19}',run) and re.fullmatch('[0-9a-f]{40}',commit),'BOOTSTRAP_CONTEXT')
 workflow='.github/workflows/dg16-r5-g1-hosted-episode.yml'
 need(e.get('GITHUB_WORKFLOW_SHA')==commit and e.get('GITHUB_WORKFLOW_REF')=='theislampill/IMPLEMENTAUDIT.md/'+workflow+'@refs/heads/'+BRANCH,'BOOTSTRAP_WORKFLOW_CURRENTNESS')
 return dict(repository=e['GITHUB_REPOSITORY'],branch=BRANCH,workflow_commit=commit,workflow_path=workflow,run_id=run,run_attempt=1,job_name='qualify')
def main():
 os.umask(0o022);ctx=context();entry=Path(__file__).absolute().parent
 expected=Path(os.environ['GITHUB_WORKSPACE'])/'packet/qualification/dg16-r5-g1-hosted-entry'
 need(entry==expected and entry.resolve(strict=True)==entry,'BOOTSTRAP_FIXED_CHECKOUT')
 placement=entry.parent/'dg16-r5-g1-hosted-episode/root_placement.py';raw=read(placement,1024**2)
 need(type(PLACEMENT_DESCRIPTOR) is dict and PLACEMENT_DESCRIPTOR==dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()),'BOOTSTRAP_PLACEMENT_PIN')
 manifest=read(entry/'PUBLIC_PACKET_MANIFEST.json',128*1024);admission=read(entry/'BOOTSTRAP_ADMISSION.json',16384)
 need(hashlib.sha256(manifest).hexdigest()==MANIFEST_SHA256 and hashlib.sha256(admission).hexdigest()==ADMISSION_SHA256,'BOOTSTRAP_EXTERNAL_PINS')
 module=types.ModuleType('exact_fixed_root_bootstrap');module.__file__=str(placement);exec(compile(raw,str(placement),'exec'),module.__dict__)
 module.bootstrap(ctx,manifest,admission,ADMISSION_SHA256)
 need(read(placement,1024**2)==raw,'BOOTSTRAP_SOURCE_CLOSING_CHANGED')
 print('{"authority":"NONE","original_awards":[],"schema":"dg16.fixed-bootstrap-entry-result.v1","status":"INSTALLED"}',flush=True)
 return 0
if __name__=='__main__':
 try:code=main()
 except BaseException:
  print('{"authority":"NONE","original_awards":[],"schema":"dg16.fixed-bootstrap-entry-result.v1","status":"REFUSED"}',flush=True);code=1
 raise SystemExit(code)
