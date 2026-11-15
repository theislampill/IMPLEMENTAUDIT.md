"""Fixed public-only transport staging outside the private root island.

Only completed existing core validators or exact fixed carrier exports supply
bytes. This file never traverses/copies a private directory or changes an
existing ancestor's ownership/mode. Final whole-tree receiving binds this file.
"""
import base64,hashlib,json,os,re,stat,sys,types
from pathlib import Path
BRANCH=None
CORE_RUN_SHA256=None
PHASES={
 'root-request':('public-request','ROOT_REQUEST_ELIGIBLE',('ROOT_REQUEST.json','SCOPE_RECEIVING.json','G1_RECEIVING.json','ARTIFACT_MANIFEST.json')),
 'final-request':('public-final-request','FINAL_REQUEST_ELIGIBLE',('FINAL_REQUEST.json','INDEPENDENT_PROOF_RECEIPT.json','ARTIFACT_MANIFEST.json')),
 'terminal':('public','PUBLIC_ELIGIBLE',('RESULT.json','HOST.json','SOURCE.json','OPERATION.json','G3.json','NSS.json','CLEANUP.json','FAILURE.json','ARTIFACT_MANIFEST.json')),
 'failure':('public-failure','FAILURE_ELIGIBLE',('RETENTION_FAILURE.json','ARTIFACT_MANIFEST.json'))}

def need(v,c):
 if not v:raise ValueError(c)

def parse(raw):
 def pairs(rows):
  v={}
  for k,x in rows:need(k not in v,'DUPLICATE_KEY');v[k]=x
  return v
 return json.loads(raw.decode('utf8'),object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE'))

def stamp(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid)

def read(path,limit):
 before=path.lstat();need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=limit,'PUBLIC_FILE_SHAPE')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  need(stamp(os.fstat(fd))==stamp(before) and not os.listxattr(fd),'PUBLIC_OPEN_CHANGED')
  body=os.pread(fd,limit+1,0)
  need(len(body)==before.st_size and stamp(os.fstat(fd))==stamp(before) and stamp(path.lstat())==stamp(before),'PUBLIC_CLOSING_CHANGED')
  return body
 finally:os.close(fd)

def context():
 e=os.environ;run=e.get('GITHUB_RUN_ID','')
 need(type(BRANCH) is str and e.get('GITHUB_ACTIONS')=='true' and e.get('GITHUB_REPOSITORY')=='theislampill/IMPLEMENTAUDIT.md'
      and e.get('GITHUB_EVENT_NAME')=='push' and e.get('GITHUB_REF')=='refs/heads/'+BRANCH
      and e.get('GITHUB_RUN_ATTEMPT')=='1' and re.fullmatch('[1-9][0-9]{0,19}',run),'EXPORT_CONTEXT')
 parent=Path(e['RUNNER_TEMP']);need(parent.is_absolute() and parent.resolve(strict=True)==parent,'EXPORT_PARENT')
 return run,parent

def stream_files(phase,raw):
 limit=131072 if phase=='tools' else 32768;need(len(raw)<=limit,'EXPORT_STREAM_BOUND');v=parse(raw)
 need(type(v) is dict and set(v)=={'schema','authority','result','files_base64','original_awards'} and v['authority']=='NONE' and v['original_awards']==[],'EXPORT_STREAM_FIELDS')
 names={'HOST_TOOL_OBSERVATION.json'} if phase=='tools' else {'REQUEST.json','RECIPIENT.pem'}
 need(v['schema']==('dg16.host-tool-observation-public-export.v1' if phase=='tools' else 'dg16.core-private-recipient-public-export.v1')
      and type(v['files_base64']) is dict and set(v['files_base64'])==names and type(v['result']) is dict,'EXPORT_STREAM_SCHEMA')
 need(v['result'].get('status')==('OBSERVED' if phase=='tools' else 'REQUEST_READY'),'EXPORT_STREAM_NOT_READY')
 if phase=='tools':need(v['result'].get('command_executed') is False and v['result'].get('crypto_capability_claim') is False,'EXPORT_OBSERVATION_SCOPE')
 result={}
 for name,text in v['files_base64'].items():
  need(type(text) is str,'EXPORT_BASE64_TYPE');body=base64.b64decode(text,validate=True)
  need(0<len(body)<=(65536 if phase=='tools' else 8192),'EXPORT_BODY_BOUND');result[name]=body
 return result

def stage(parent,run,phase,files):
 need(phase in (*PHASES,'tools','recipient') and type(run) is str and re.fullmatch('[1-9][0-9]{0,19}',run),'EXPORT_FIXED_DESTINATION')
 names=PHASES[phase][2] if phase in PHASES else (('HOST_TOOL_OBSERVATION.json',) if phase=='tools' else ('REQUEST.json','RECIPIENT.pem'))
 need(type(files) is dict and set(files)==set(names),'EXPORT_NAME')
 need(sum(map(len,files.values()))<=4*1024**2,'EXPORT_TOTAL_BOUND')
 root=parent/('dg16-g1-public-'+run+'-a1')
 try:os.mkdir(root,0o755)
 except FileExistsError:pass
 st=root.lstat();need(stat.S_ISDIR(st.st_mode) and not root.is_symlink() and stat.S_IMODE(st.st_mode)==0o755 and st.st_uid==os.geteuid() and st.st_gid==os.getegid(),'EXPORT_ROOT_CUSTODY')
 fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  need(stamp(os.fstat(fd))==stamp(st),'EXPORT_ROOT_CHANGED')
  os.mkdir(phase,0o755,dir_fd=fd);phase_fd=os.open(phase,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd)
  try:
   for name,body in sorted(files.items()):
    out=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o644,dir_fd=phase_fd)
    try:
     offset=0
     while offset<len(body):
      n=os.write(out,body[offset:]);need(n>0,'EXPORT_WRITE_PROGRESS');offset+=n
     os.fchmod(out,0o644);os.fsync(out)
    finally:os.close(out)
   os.fsync(phase_fd)
   need({p.name for p in (root/phase).iterdir()}==set(files),'EXPORT_POPULATION')
   for name,body in files.items():need(read(root/phase/name,1024**2)==body,'EXPORT_READBACK')
  finally:os.close(phase_fd)
 finally:os.close(fd)

def failure_files(core,output,context):
 # Use the existing closed projection and validator directly. Core preparation
 # may never have created output, so failure receiving must not require a new
 # private/core directory merely to retain an unknown-state observation.
 marker=output/'PUBLIC_ELIGIBLE'
 if marker.exists() and core.read_regular(marker,5)==b'true\n':return None
 raw=core.canonical(core.failure_observation(output,context))
 files={'RETENTION_FAILURE.json':raw,'ARTIFACT_MANIFEST.json':core.canonical(dict(schema='dg16.g1-hosted-failure-artifacts.v1',
  members=[dict(name='RETENTION_FAILURE.json',bytes=len(raw),sha256=core.digest(raw))]))}
 core.validate_failure_files(files)
 need(core.canonical(core.failure_observation(output,context))==raw,'FALLBACK_CLOSING_READBACK_REFUSED')
 core.validate_failure_files(files)
 return files

def core_files(phase,run):
 need(os.getuid()==os.geteuid()==0 and type(CORE_RUN_SHA256) is str and re.fullmatch('[0-9a-f]{64}',CORE_RUN_SHA256),'EXPORT_CORE_AUTHORITY')
 packet=Path('/dg16-g1-'+run)/'packet';path=packet/'run.py';raw=read(path,1024**2)
 need(hashlib.sha256(raw).hexdigest()==CORE_RUN_SHA256,'EXPORT_CORE_PIN')
 core=types.ModuleType('exact_public_export_core');core.__file__=str(path);exec(compile(raw,str(path),'exec'),core.__dict__)
 source=packet.parent/'source';output=packet.parent/'output';ctx=core.host_context(output,source)
 if phase=='failure':
  files=failure_files(core,output,ctx)
  need(read(path,1024**2)==raw,'EXPORT_CORE_CLOSING_CHANGED')
  return files
 if phase=='root-request':core.emit_root_request(output)
 elif phase=='final-request':core.emit_root_request(output,final=True)
 elif phase=='terminal':core.emit_public(output)
 else:need(False,'EXPORT_PHASE')
 directory,marker,names=PHASES[phase]
 need(core.read_regular(output/marker,5)==b'true\n','EXPORT_ELIGIBILITY_REQUIRED')
 files={name:core.read_regular(output/directory/name,1024**2) for name in names}
 need({p.name for p in (output/directory).iterdir()}==set(names),'EXPORT_CORE_POPULATION')
 need(read(path,1024**2)==raw,'EXPORT_CORE_CLOSING_CHANGED')
 return files

def main():
 need(sys.flags.isolated==1 and sys.dont_write_bytecode and len(sys.argv)==2 and os.getuid()==os.geteuid()==os.getgid()==os.getegid()==0,'FIXED_EXPORT_ENTRY')
 os.umask(0o022)
 phase=sys.argv[1];need(phase in (*PHASES,'tools','recipient'),'EXPORT_PHASE');run,parent=context()
 files=stream_files(phase,sys.stdin.buffer.read(131073)) if phase in ('tools','recipient') else core_files(phase,run)
 if files is not None:stage(parent,run,phase,files)
 print(json.dumps(dict(schema='dg16.fixed-public-staging-result.v1',authority='NONE',phase=phase,exported=files is not None,original_awards=[])),flush=True)
 return 0

if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception:
  print('{"authority":"NONE","schema":"dg16.fixed-public-staging-refusal.v1","status":"REFUSED","original_awards":[]}',flush=True);raise SystemExit(1)
