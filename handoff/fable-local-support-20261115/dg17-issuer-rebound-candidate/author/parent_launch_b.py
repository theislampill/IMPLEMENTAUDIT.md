"""Root-only conditional B parent; same900s clock and original Job. Inert without --execute."""
import argparse,hashlib,json,os,stat,subprocess,sys,time,types
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=Path('C:\\workspace\\ai\\improveimplementaudit\\plans\\astra-r3-execution-20261114-01\\dg17-native-20261114-01')
DRIVER_SHA='590a92cc09b835a4a50af8e40364cd6337fecc7d0fbbb08b956fdd4c335e0dd1'
JOB=Path('C:/workspace/ai/improveimplementaudit/plans/thread9-cbal-next-issue-20261014/R0039_215/execution-20261022/windows_job_measure.py')
JOB_SHA='6dc21e695a1a8ab5feee620d13a2ce9539736adc2632e07327396f0ff8391bda'
def capture(path,pin,size=None,physical=None,keep=False):
 path=Path(path);a=path.lstat()
 assert stat.S_ISREG(a.st_mode) and not getattr(a,'st_file_attributes',0)&1024
 if physical:assert (a.st_dev,a.st_ino,a.st_nlink)==tuple(physical)
 if size is not None:assert a.st_size==size
 def identity(s):return (s.st_dev,s.st_ino,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,getattr(s,'st_file_attributes',0),getattr(s,'st_reparse_tag',0))
 h=hashlib.sha256();parts=[];total=0
 fd=os.open(path,os.O_RDONLY|os.O_BINARY|os.O_NOINHERIT|getattr(os,'O_NONBLOCK',0))
 with os.fdopen(fd,'rb') as f:
  d=os.fstat(f.fileno());assert stat.S_ISREG(d.st_mode) and identity(d)==identity(a)
  while True:
   chunk=f.read(min(1024*1024,a.st_size+1-total))
   if not chunk:break
   total+=len(chunk);assert total<=a.st_size,'Input grew beyond its admitted physical bound'
   h.update(chunk)
   if keep:parts.append(chunk)
  e=os.fstat(f.fileno());assert identity(e)==identity(d) and e.st_mode==d.st_mode
 z=path.lstat();assert identity(z)==identity(a) and z.st_mode==a.st_mode
 assert h.hexdigest()==pin,str(path)
 return b''.join(parts) if keep else None


def main():
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--grant',type=Path);args=p.parse_args()
 if not args.execute:print('INERT: original independent post-A and RootB admission required');return
 assert args.grant is not None
 op_raw=(ROOT/'OPERATION_B_BOUND.json').read_bytes();op=json.loads(op_raw);g=json.loads(args.grant.read_bytes());assert g['issuer']==op['issuer'] and g['stage']=='B' and g['operation_sha256']==hashlib.sha256(op_raw).hexdigest()
 assert g['post_A_sha256']==op['post_A']['sha256'] and g['owner_approval_sha256']==op['owner_approval']['sha256']
 post=capture(op['post_A']['path'],op['post_A']['sha256'],keep=True);actual=json.loads(post);start=actual['window_start_ns']/1e9;assert time.perf_counter()<start+570
 for item in op['readset']:capture(item['path'],item['sha256'],item.get('bytes'))
 driver_path=HERE/'stage_b.py';capture(driver_path,DRIVER_SHA);job=capture(JOB,JOB_SHA,keep=True)
 env=os.environ|{'CODEX_HOME':op['expected_codex_home'],'PYTHONDONTWRITEBYTECODE':'1'}
 argv=[str(driver_path),'--grant',str(args.grant)]
 loader='import os,stat,hashlib,sys;from pathlib import Path;'+repr('')+'\n'+"def capture(path,pin,size=None,physical=None,keep=False):\n path=Path(path);a=path.lstat()\n assert stat.S_ISREG(a.st_mode) and not getattr(a,'st_file_attributes',0)&1024\n if physical:assert (a.st_dev,a.st_ino,a.st_nlink)==tuple(physical)\n if size is not None:assert a.st_size==size\n def identity(s):return (s.st_dev,s.st_ino,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,getattr(s,'st_file_attributes',0),getattr(s,'st_reparse_tag',0))\n h=hashlib.sha256();parts=[];total=0\n fd=os.open(path,os.O_RDONLY|os.O_BINARY|os.O_NOINHERIT|getattr(os,'O_NONBLOCK',0))\n with os.fdopen(fd,'rb') as f:\n  d=os.fstat(f.fileno());assert stat.S_ISREG(d.st_mode) and identity(d)==identity(a)\n  while True:\n   chunk=f.read(min(1024*1024,a.st_size+1-total))\n   if not chunk:break\n   total+=len(chunk);assert total<=a.st_size,'Input grew beyond its admitted physical bound'\n   h.update(chunk)\n   if keep:parts.append(chunk)\n  e=os.fstat(f.fileno());assert identity(e)==identity(d) and e.st_mode==d.st_mode\n z=path.lstat();assert identity(z)==identity(a) and z.st_mode==a.st_mode\n assert h.hexdigest()==pin,str(path)\n return b''.join(parts) if keep else None\n"+'\nraw=capture('+repr(str(driver_path))+','+repr(DRIVER_SHA)+',keep=True)\nsys.argv='+repr(argv)+'\nexec(compile(raw,'+repr(str(driver_path))+",'exec'),{'__name__':'__main__','__file__':"+repr(str(driver_path))+'})'
 command=[op['python']['path'],'-I','-S','-B','-c',loader];assert len(subprocess.list2cmdline(command))<30000
 helper=types.ModuleType('dg17_original_parent_B_job');helper.__file__=str(JOB);exec(compile(job,str(JOB),'exec'),helper.__dict__)
 out=ROOT/'parent-B-01';assert not out.exists();remaining=900-(time.perf_counter()-start);assert remaining>0
 result=helper.measure(command,HERE,env,out,diagnostic_timeout_seconds=remaining)
 target=ROOT/'PARENT_STAGE_B_JOB_RESULT.json';assert not target.exists();target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps(dict(exit_code=result['exit_code'],elapsed_global_seconds=time.perf_counter()-start)))
if __name__=='__main__':main()
