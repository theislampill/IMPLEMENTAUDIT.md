"""Primary Sol's single admitted A invocation; inert without --execute."""
import argparse,base64,hashlib,json,os,stat,subprocess,sys,time,types
from pathlib import Path
B=Path(__file__).resolve().parent
OP_SHA='49981532c823dc9e456c8238877fec002f9f7368eaa4eb55a43c1d639931d651'
DRIVER_SHA='d24fe5fdb87eb1cd6c2b3482475de3cbe9b4b811d5e39921d497064dad45c2d8'
RPC_SHA='fd860cbf6f46fe03229ccfd64fda88490204158b6ac09c8b610eecb7b8139c89'
JOB=Path(r'C:/workspace/ai/improveimplementaudit/plans/thread9-cbal-next-issue-20261014/R0039_215/execution-20261022/windows_job_measure.py')
JOB_SHA='6dc21e695a1a8ab5feee620d13a2ce9539736adc2632e07327396f0ff8391bda'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(path,value):
 with path.open('x',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n')
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
 ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');ap.add_argument('--grant',type=Path);args=ap.parse_args()
 if not args.execute:print('INERT: exact owner/resource admission required');return 0
 raw=capture(B/'OPERATION_A.json',OP_SHA,keep=True);op=json.loads(raw)
 for item in op['readset']:capture(item['path'],item['sha256'],item['bytes'],item.get('physical_identity'))
 driver_path=B/'stage_a.py';driver=capture(driver_path,DRIVER_SHA,keep=True)
 capture(B/'native_rpc.py',RPC_SHA,keep=True)
 job_buffer=capture(JOB,JOB_SHA,keep=True)
 assert not Path(op['case']).exists()
 assert Path(sys.executable).resolve()==Path(op['python']['path']).resolve()
 codex_home=Path(op['expected_codex_home']);assert codex_home.is_dir()
 grant_path=args.grant;assert grant_path is not None and grant_path.is_absolute()
 grant_raw=grant_path.read_bytes();grant=json.loads(grant_raw)
 assert grant['issuer']==op['issuer'] and grant['stage']=='A' and grant['operation_sha256']==OP_SHA and grant['owner_approval_sha256']==op['owner_approval']['sha256'] and grant['resource_ack_received'] is True
 window=Path('C:\\workspace\\ai\\improveimplementaudit\\plans\\astra-r3-execution-20261114-01\\dg17-native-20261114-01\\EPISODE_WINDOW_02.json');out=Path('C:\\workspace\\ai\\improveimplementaudit\\plans\\astra-r3-execution-20261114-01\\dg17-native-20261114-01\\parent-A-02')
 assert not window.exists() and not out.exists()
 helper=types.ModuleType('dg17_parent_owned_job');helper.__file__=str(JOB);exec(compile(job_buffer,str(JOB),'exec'),helper.__dict__)
 started=time.perf_counter_ns()
 save(window,dict(window_start_ns=started,total_seconds=900,operation_sha256=OP_SHA,owner_approval_sha256=op['owner_approval']['sha256'],actual_Root_grant_sha256=sha(grant_raw)))
 argv=[str(driver_path),'--grant',str(grant_path),'--window-start-ns',str(started)]
 encoded=base64.b64encode(driver).decode('ascii')
 loader='import base64,sys;sys.argv='+repr(argv)+';exec(compile(base64.b64decode('+repr(encoded)+'),'+repr(str(driver_path)) +",'exec'),{'__name__':'__main__','__file__':"+repr(str(driver_path))+'})'
 command=[op['python']['path'],'-I','-S','-B','-c',loader]
 assert len(subprocess.list2cmdline(command))<30000
 env=os.environ|{'CODEX_HOME':str(codex_home),'PYTHONDONTWRITEBYTECODE':'1'}
 result=helper.measure(command,B,env,out,diagnostic_timeout_seconds=max(1,900-(time.perf_counter_ns()-started)/1e9))
 save(Path('C:\\workspace\\ai\\improveimplementaudit\\plans\\astra-r3-execution-20261114-01\\dg17-native-20261114-01\\PARENT_STAGE_A_JOB_RESULT_02.json'),result)
 print(json.dumps({k:result.get(k) for k in ['exit_code','elapsed_ms','terminal_active_processes','terminal_breakaway_allowed','assigned_before_resume']}),flush=True)
 return result['exit_code']
if __name__=='__main__':raise SystemExit(main())
