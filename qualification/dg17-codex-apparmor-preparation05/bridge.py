import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import stat
import sys
import time
import types
DIRECTORY="qualification/dg17-codex-apparmor-preparation05"
IDENTITY="dg17-9077-codex20-apparmor-preparation05"
SCRIPT_SHA="e4f116003174fe1400960da43b32594157826760ca31c3781a6b765ade82ed0a"
CODE_SHA="fbc15a7cdb0ed37ceb87162b49400a18b8fd2ed2f80a124fb131c067a8d7cc93"
LOOP_SHA="e04d2c081998a08de53cf0f214cd1b9ae531fc5abc1d1bf79206b43c69570433"
FIELDS= ( "source","manifest-sha","context","context-sha","output","uid","gid","parent-mnt","parent-net","profiles-fd","capsule-code-sha","capsule-script-sha")
CAPS= { "CapEff","CapPrm","CapAmb","CapInh","CapBnd"}
ENV_KEYS= ( "GITHUB_ACTIONS","RUNNER_ENVIRONMENT","GITHUB_EVENT_NAME","GITHUB_REPOSITORY","GITHUB_REF","GITHUB_RUN_ID","GITHUB_RUN_ATTEMPT","GITHUB_SHA","GITHUB_JOB")
PROFILES="/sys/kernel/security/apparmor/profiles"
OUTER_FIELDS= ( "process_started","pidfd_acquired","returncode","start_errno","timeout","output_bound_exceeded","internal_failure","streams_complete","stdout_bytes","stdout_sha256","stderr_bytes","stderr_sha256","cleanup")
CLEANUP_FIELDS= ( "echild","pidfd_signals","retained_status_count","retained_statuses_sha256","reaped_statuses","reaped_statuses_truncated")
ARTIFACTS= { "observation": ( "OBSERVATION.json",65536),"worker_receipt": ( "WORKER_RECEIPT.json",16384),"capsule_admission": ( "CAPSULE_ADMISSION.json",16384),"capsule_result": ( "CAPSULE_RESULT.json",16384)}
SCOPE= { "authority":"NONE","original14":"REQUIRED_UNMET_UNWAIVED_UNRETIRED","original_awards": [],"native_execution":False,"security_policy_changed":False}
READ_CODE="def read ( path,bound):\n path=Path ( path)\n if not path.is_absolute ()or path.resolve ( strict=True)!=path:raise ValueError ()\n with os.fdopen ( os.open ( path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC),'rb')as stream:\n  before=os.fstat ( stream.fileno ())\n  if not stat.S_ISREG ( before.st_mode)or before.st_nlink!=1 or not 0<before.st_size<=bound:raise ValueError ()\n  raw=stream.read ( bound+1);after=os.fstat ( stream.fileno ());named=path.lstat ()\n  identity=lambda v:tuple ( getattr ( v,'st_'+k)for k in ( 'dev','ino','mode','uid','gid','nlink','size','mtime_ns','ctime_ns'))\n  if len ( raw)!=before.st_size or identity ( before)!=identity ( after)or identity ( after)!=identity ( named):raise ValueError ()\n  return raw\n"
exec ( compile ( READ_CODE,"dg17-bounded-reader","exec"))
BOOTSTRAP='import hashlib,json,os,re,stat,sys\nfrom pathlib import Path\n'+READ_CODE+"try:\n path=Path ( sys.argv [ 1]);pin=sys.argv [ 2]\n if path.parts [ -3:]!= ( 'qualification','dg17-codex-apparmor-preparation05','bridge.py')or not re.fullmatch ( '[0-9a-f]{64}',pin):raise ValueError ()\n manifest=read ( path.parent/'INPUT_PINS.json',16384)\n if hashlib.sha256 ( manifest).hexdigest ()!=pin:raise ValueError ()\n value=json.loads ( manifest);rows=value [ 'files']\n if value [ 'schema']!='dg17.apparmor.preparation-source.v1'or len ( rows)!=8:raise ValueError ()\n row,= [ r for r in rows if r [ 'path']=='qualification/dg17-codex-apparmor-preparation05/bridge.py']\n if set ( row)!= { 'path','bytes','sha256'}or type ( row [ 'bytes'])is not int or not 0<row [ 'bytes']<=65536:raise ValueError ()\n raw=read ( path,row [ 'bytes'])\n if len ( raw)!=row [ 'bytes']or hashlib.sha256 ( raw).hexdigest ()!=row [ 'sha256']:raise ValueError ()\nexcept BaseException:\n sys.stderr.write ( 'DG17_RECEIVED_SOURCE_REFUSED\\n');raise SystemExit ( 1)\nsys.argv= [ str ( path),*sys.argv [ 3:]]\nexec ( compile ( raw,str ( path),'exec'), { '__name__':'__main__','__file__':str ( path),'_RECEIVED_BRIDGE_BYTES':raw})\n"
class Refusal ( ValueError):
 pass
def need ( ok,code):
 if ok is not True:
  raise Refusal ( code)
def sha ( raw):
 return hashlib.sha256 ( raw).hexdigest ()
def enc ( value):
 return ( json.dumps ( value,sort_keys=True,separators= ( ",",":"),ensure_ascii=True,allow_nan=False)+"\n").encode ( "ascii")
def pretty ( value):
 return ( json.dumps ( value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+"\n").encode ( "ascii")
def closed_environment ( context):
 need ( type ( context)is dict and set ( context)== { "repository","branch","run_id","attempt","workflow_commit","job_name"},"CONTEXT")
 need ( context [ "repository"]=="theislampill/IMPLEMENTAUDIT.md"and context [ "branch"]=="pro/dg17-isolated-episode-01-20261106"and context [ "job_name"]=="dg17-bounded"and type ( context [ "attempt"])is int and context [ "attempt"]==1 and type ( context [ "run_id"])is str and re.fullmatch ( "[1-9][0-9]{0,18}",context [ "run_id"])is not None and type ( context [ "workflow_commit"])is str and re.fullmatch ( "[0-9a-f]{40}",context [ "workflow_commit"])is not None,"CONTEXT")
 return dict ( zip ( ENV_KEYS, ( "true","github-hosted","push",context [ "repository"],"refs/heads/"+context [ "branch"],context [ "run_id"],"1",context [ "workflow_commit"],"dg17-bounded")))
def actual_context ( context):
 expected=closed_environment ( context)
 need ( all ( os.environ.get ( k)==v for k,v in expected.items ()),"ACTUAL_PARENT_CONTEXT")
 return expected
def drop_argv ( uid,gid,code,args):
 need ( type ( uid)is int and type ( gid)is int and 0<uid<4294967295 and 0<gid<4294967295 and type ( code)is str and type ( args)is list and all ( type ( x)is str for x in args),"DROP_ARGUMENTS")
 return [ "/usr/bin/setpriv","--inh-caps=-all","--ambient-caps=-all","--bounding-set=-all","--reuid",str ( uid),"--regid",str ( gid),"--clear-groups","--no-new-privs","/usr/bin/python3","-I","-S","-B","-c",code,*args]
FD_CODE="def descriptor_snapshot ():\n info=os.fstat ( 3);path=os.stat ( '/sys/kernel/security/apparmor/profiles',follow_symlinks=False)\n identity=lambda v: { k:getattr ( v,'st_'+k)for k in ( 'dev','ino','mode','uid','gid','nlink','size','mtime_ns','ctime_ns')}\n need ( identity ( info)==identity ( path)and stat.S_ISREG ( info.st_mode)and info.st_uid==info.st_gid==0 and info.st_nlink==1 and not info.st_mode&0o022,'PROFILES_DESCRIPTOR_IDENTITY')\n flags=fcntl.fcntl ( 3,fcntl.F_GETFL)\n need ( flags&os.O_ACCMODE==os.O_RDONLY and not flags&getattr ( os,'O_PATH',0),'PROFILES_DESCRIPTOR_ACCESS')\n return { 'fd':3,'path':'/sys/kernel/security/apparmor/profiles','access':'O_RDONLY','identity':identity ( info)}\ndef namespace_binding ():\n result= {}\n for kind,name in ( ( 'mnt','mount_namespace_sha256'), ( 'user','user_namespace_sha256')):\n  info=os.stat ( '/proc/self/ns/'+kind)\n  raw= ( json.dumps ( { 'dev':info.st_dev,'ino':info.st_ino},sort_keys=True,separators= ( ',',':'))+'\\n').encode ( 'ascii')\n  result [ name]=sha ( raw)\n return result\ndef context_environment ():\n names= ( 'GITHUB_ACTIONS','RUNNER_ENVIRONMENT','GITHUB_EVENT_NAME','GITHUB_REPOSITORY','GITHUB_REF','GITHUB_RUN_ID','GITHUB_RUN_ATTEMPT','GITHUB_SHA','GITHUB_JOB')\n raw= ( json.dumps ( { k:os.environ.get ( k)for k in names},sort_keys=True,separators= ( ',',':'))+'\\n').encode ( 'ascii')\n return sha ( raw)\ndef child_start ( pid):\n with open ( '/proc/'+str ( pid)+'/stat','rb')as stream:raw=stream.read ( 4097)\n need ( len ( raw)<=4096 and b') 'in raw,'CHILD_PROCESS_STAT')\n fields=raw [ raw.rfind ( b') ')+2:].split ()\n need ( len ( fields)>=20 and re.fullmatch ( rb'[0-9]+',fields [ 19])is not None,'CHILD_PROCESS_START')\n return int ( fields [ 19])\ndef run ():\n try:return inherited_run ()\n finally:os.close ( 3)\n"
def derive ( episode,manifest_sha256):
 need ( type ( manifest_sha256)is str and re.fullmatch ( "[0-9a-f]{64}",manifest_sha256)is not None,"DERIVATION_MANIFEST_PIN")
 need ( sha ( episode.CAPSULE_SCRIPT.encode ())==SCRIPT_SHA and sha ( episode.CAPSULE_CODE.encode ())==CODE_SHA and episode.LOOPBACK_INITIALIZER_SHA==LOOP_SHA,"ORIGINAL_CAPSULE_PIN")
 script,code=episode.CAPSULE_SCRIPT,episode.CAPSULE_CODE
 tail='"$'+'{@:9}"\n'
 old='exec /usr/bin/setpriv --reuid "$1" --regid "$2" --clear-groups --no-new-privs /usr/bin/python3 -I -S -B -c "$3" "$1" "$2" "$4" "$5" "$6" "$7" "$8" '+tail
 new='exec /usr/bin/python3 -I -S -B -c '+shlex.quote ( BOOTSTRAP)+' "$8" '+manifest_sha256+' --root "$1" "$2" "$3" "$4" "$5" "$6" "$7" '+tail
 need ( script.count ( old)==1,"SCRIPT_DERIVATION")
 script=script.replace ( old,new)
 edits= ( ( "('CapEff','CapPrm','CapAmb')","('CapEff','CapPrm','CapAmb','CapInh','CapBnd')"), ( "'network':network_snapshot(network_parent)}","'network':network_snapshot(network_parent),'profiles_descriptor':descriptor_snapshot(),""'namespace_binding':namespace_binding(),'context_environment_sha256':context_environment()}"), ( "def run():\n","def inherited_run():\n"), ( "child_rc=None;after=None;failure=None","child_rc=None;child_pid=None;child_start_ticks=None;after=None;failure=None"), ( "argv=['/usr/bin/python3','-I','-S','-B',*sys.argv[7:]]","argv=['/usr/bin/python3','-I','-S','-B','-c',"+repr ( BOOTSTRAP)+",sys.argv[7],"+repr ( manifest_sha256)+",*sys.argv[8:]]"), ( "child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,close_fds=True)","child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,close_fds=True,pass_fds=(3,))\n""        child_pid=child.pid;child_start_ticks=child_start(child.pid)"), ( "'child_returncode':child_rc,'failure':failure}","'child_returncode':child_rc,'failure':failure,'child_pid':child_pid,'child_start_ticks':child_start_ticks}"), ( "dg17.private-view-admission.v3","dg17.apparmor-capsule-admission.v1"), ( "dg17.private-view-result.v3","dg17.apparmor-capsule-result.v1"), ( "if __name__=='__main__':",FD_CODE+"\nif __name__=='__main__':"),)
 for old,new in edits:
  need ( code.count ( old)==1,"CODE_DERIVATION")
  code=code.replace ( old,new)
 return { "script":script,"code":code,"script_sha256":sha ( script.encode ()),"code_sha256":sha ( code.encode ())}
def load ( source,expected_sha):
 source=Path ( source)
 manifest=read ( source/DIRECTORY/"INPUT_PINS.json",16384)
 need ( type ( expected_sha)is str and re.fullmatch ( "[0-9a-f]{64}",expected_sha)is not None and sha ( manifest)==expected_sha,"MANIFEST_PIN")
 value=json.loads ( manifest)
 rows=value.get ( "files")
 need ( type ( rows)is list and len ( rows)==8,"MANIFEST_POPULATION")
 chosen= [ r for r in rows if type ( r)is dict and r.get ( "path")==DIRECTORY+"/admission.py"]
 need ( len ( chosen)==1 and type ( chosen [ 0].get ( "bytes"))is int and 0<chosen [ 0] [ "bytes"]<=1048576,"MODULE_ROW")
 raw=read ( source/DIRECTORY/"admission.py",chosen [ 0] [ "bytes"])
 need ( len ( raw)==chosen [ 0] [ "bytes"]and sha ( raw)==chosen [ 0].get ( "sha256"),"MODULE_PIN")
 a=types.ModuleType ( "dg17_apparmor_admission")
 a.__file__=str ( source/DIRECTORY/"admission.py")
 exec ( compile ( raw,a.__file__,"exec"),a.__dict__)
 binding,bodies=a.source_closure ( source,manifest,expected_sha,time.monotonic ()+20)
 current_bridge=bodies [ DIRECTORY+"/bridge.py"]
 need ( read ( Path ( __file__).absolute (),65536)==current_bridge and globals ().get ( "_RECEIVED_BRIDGE_BYTES",current_bridge)==current_bridge,"RUNNING_BRIDGE_PIN")
 objects= [ a]
 for path in ( a.UTILITY_PATH,a.EPISODE_PATH,a.PREPARER_PATH,DIRECTORY+"/receiver.py"):
  objects.append ( a.loaded_module ( bodies [ path],"dg17_bridge_"+Path ( path).stem))
 return ( *objects,binding,bodies,manifest)
def arguments ( args):
 need ( type ( args)is list and len ( args)==24 and args [ ::2]== [ "--"+x for x in FIELDS]and all ( type ( x)is str for x in args),"WORKER_ARGUMENTS")
 result=dict ( zip ( FIELDS,args [ 1::2]))
 for key in ( "manifest-sha","context-sha","capsule-code-sha","capsule-script-sha"):
  need ( re.fullmatch ( "[0-9a-f]{64}",result [ key])is not None,"WORKER_DIGEST")
 for key in ( "uid","gid"):
  need ( re.fullmatch ( "[1-9][0-9]{0,9}",result [ key])is not None and int ( result [ key])<4294967295,"WORKER_IDENTITY")
 need ( result [ "profiles-fd"]=="3"and re.fullmatch ( r"mnt:\[[0-9]+\]",result [ "parent-mnt"])is not None and re.fullmatch ( r"net:\[[0-9]+\]",result [ "parent-net"])is not None,"WORKER_BINDING")
 for key in ( "source","context","output"):
  need ( Path ( result [ key]).is_absolute (),"WORKER_PATH")
 need ( Path ( result [ "context"])==Path ( result [ "output"])/"private/CONTEXT.json","CONTEXT_PATH")
 return result
def context_file ( row,a):
 path=Path ( row [ "context"])
 info,parent=path.lstat (),path.parent.lstat ()
 need ( info.st_uid==int ( row [ "uid"])and stat.S_IMODE ( info.st_mode)==0o600 and parent.st_uid==int ( row [ "uid"])and stat.S_ISDIR ( parent.st_mode)and stat.S_IMODE ( parent.st_mode)==0o700,"CONTEXT_CUSTODY")
 raw=read ( path,4096)
 need ( sha ( raw)==row [ "context-sha"],"CONTEXT_PIN")
 context=a.strict ( raw,4096)
 closed_environment ( context)
 return context
def write ( path,raw,limit=65536):
 path=Path ( path)
 info=path.parent.lstat ()
 need ( type ( raw)is bytes and len ( raw)<=limit and path.parent.resolve ( strict=True)==path.parent and stat.S_ISDIR ( info.st_mode)and info.st_uid==os.getuid ()and stat.S_IMODE ( info.st_mode)==0o700,"OUTPUT_CUSTODY")
 fd=os.open ( path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 with os.fdopen ( fd,"wb")as stream:
  stream.write ( raw);stream.flush ();os.fsync ( stream.fileno ())
def install_fd ( fd):
 need ( type ( fd)is int and fd>3,"ROOT_OPEN_DESCRIPTOR")
 try:
  os.fstat ( 3)
 except OSError as exc:
  need ( exc.errno==errno.EBADF,"FD3_CUSTODY")
 else:
  raise Refusal ( "FD3_ALREADY_OWNED")
 os.dup2 ( fd,3,inheritable=True)
 os.close ( fd)
def root_entry ( args):
 need ( type ( args)is list and len ( args)==31 and os.getuid ()==os.geteuid ()==os.getgid ()==os.getegid ()==0,"ROOT_ARGUMENTS")
 row=arguments ( args [ 7:])
 a,u,e,p,r,binding,bodies,manifest=load ( row [ "source"],row [ "manifest-sha"])
 derived=derive ( e,row [ "manifest-sha"]);context=context_file ( row,a)
 need ( args [ :2]== [ row [ "uid"],row [ "gid"]]and args [ 2]==derived [ "code"]and args [ 3:7]== [ str ( Path ( row [ "output"])/"private/CAPSULE_ADMISSION.json"),str ( Path ( row [ "output"])/"private/CAPSULE_RESULT.json"),row [ "parent-mnt"],row [ "parent-net"]]and row [ "capsule-code-sha"]==derived [ "code_sha256"]and row [ "capsule-script-sha"]==derived [ "script_sha256"],"ROOT_SOURCE_ARGUMENTS")
 opened,installed=None,False
 try:
  opened=a.open_loaded_profiles ()
  install_fd ( opened);opened=None;installed=True
  with a.held ( PROFILES,time.monotonic ()+2,descriptor=3):
   pass
  environment=u.safe_environment ()
  need ( not set ( environment)&set ( ENV_KEYS),"BASE_ENVIRONMENT_CHANGED")
  environment.update ( closed_environment ( context))
  capsule_args= [ *args [ :2],*args [ 3:7],str ( Path ( row [ "source"])/DIRECTORY/"bridge.py"),*args [ 7:]]
  os.execve ( "/usr/bin/setpriv",drop_argv ( int ( row [ "uid"]),int ( row [ "gid"]),derived [ "code"],capsule_args),environment)
  raise Refusal ( "ROOT_EXEC_RETURNED")
 finally:
  if opened is not None:
   os.close ( opened)
  if installed:
   os.close ( 3)
def worker_entry ( args):
 try:
  row=arguments ( args)
  a,u,e,p,r,binding,bodies,manifest=load ( row [ "source"],row [ "manifest-sha"])
  context=context_file ( row,a);actual_context ( context);derived=derive ( e,row [ "manifest-sha"])
  need ( os.getuid ()==os.geteuid ()==int ( row [ "uid"])and os.getgid ()==os.getegid ()==int ( row [ "gid"])and row [ "capsule-code-sha"]==derived [ "code_sha256"]and row [ "capsule-script-sha"]==derived [ "script_sha256"],"WORKER_SOURCE_CONTEXT")
  need ( ctypes.CDLL ( None,use_errno=True).prctl ( 36,1,0,0,0)==0,"WORKER_SUBREAPER")
  a.owned_quiescent ( u)
  session=a.SameHostAdmission ( Path ( row [ "source"]),manifest,row [ "manifest-sha"],context,3)
  raw=session.observe ()
  write ( Path ( row [ "output"])/"private/OBSERVATION.json",raw)
  receipt=session.receive_current ( raw)
  result=enc ( receipt)
  write ( Path ( row [ "output"])/"private/WORKER_RECEIPT.json",result,16384)
  sys.stdout.buffer.write ( result);sys.stdout.buffer.flush ()
  return 0
 finally:
  os.close ( 3)
def snapshot_valid ( value,uid,gid,parent_mnt,parent_net,e,context):
 if type ( value)is not dict:
  return False
 additions= { "profiles_descriptor","namespace_binding","context_environment_sha256"}
 if not additions<=set ( value)or value [ "context_environment_sha256"]!=sha ( enc ( closed_environment ( context))):
  return False
 caps=value.get ( "capabilities")
 if type ( caps)is not dict or set ( caps)!=CAPS or any ( type ( v)is not int or v!=0 for v in caps.values ()):
  return False
 descriptor=value [ "profiles_descriptor"]
 if type ( descriptor)is not dict or set ( descriptor)!= { "fd","path","access","identity"}:
  return False
 if type ( descriptor [ "fd"])is not int or descriptor [ "fd"]!=3 or descriptor [ "path"]!=PROFILES or descriptor [ "access"]!="O_RDONLY":
  return False
 ident=descriptor [ "identity"]
 keys= { "dev","ino","mode","uid","gid","nlink","size","mtime_ns","ctime_ns"}
 if type ( ident)is not dict or set ( ident)!=keys or any ( type ( v)is not int or v<0 for v in ident.values ()):
  return False
 if not stat.S_ISREG ( ident [ "mode"])or ident [ "uid"]!=0 or ident [ "gid"]!=0 or ident [ "nlink"]!=1 or ident [ "mode"]&0o022:
  return False
 ns=value [ "namespace_binding"]
 if type ( ns)is not dict or set ( ns)!= { "mount_namespace_sha256","user_namespace_sha256"}or any ( type ( v)is not str or re.fullmatch ( "[0-9a-f]{64}",v)is None for v in ns.values ()):
  return False
 original= { k:v for k,v in value.items ()if k not in additions}
 original [ "capabilities"]= { k:caps [ k]for k in ( "CapEff","CapPrm","CapAmb")}
 return e.capsule_snapshot_valid ( original,uid,gid,parent_mnt,parent_net)
def receive_result ( value,context,source,e,r,now_ns):
 fields= { "schema","candidate_identity","context","source","parent_host","derivation","capsule","outer_capture","observation","worker_receipt","source_bookends_equal","host_bookends_equal",*SCOPE}
 need ( type ( value)is dict and set ( value)==fields and value [ "schema"]=="dg17.apparmor.preparation-bridge.v1"and value [ "candidate_identity"]==IDENTITY and value [ "context"]==context and value [ "source"]==source,"BRIDGE_FIELDS")
 r._context ( context);r._source ( source);r._host ( value [ "parent_host"])
 need ( all ( value [ k]==v and type ( value [ k])is type ( v)for k,v in SCOPE.items ())and value [ "source_bookends_equal"]is True and value [ "host_bookends_equal"]is True,"BRIDGE_SCOPE")
 derived=derive ( e,source [ "manifest_sha256"])
 expected= { "script_sha256":derived [ "script_sha256"],"code_sha256":derived [ "code_sha256"],"original_script_sha256":SCRIPT_SHA,"original_code_sha256":CODE_SHA,"loopback_initializer_sha256":LOOP_SHA}
 need ( value [ "derivation"]==expected,"BRIDGE_DERIVATION")
 cap=value [ "capsule"]
 keys= { "parent_mnt","parent_net","child_argv_sha256","admission","result","outside_before_sha256","outside_after_sha256"}
 need ( type ( cap)is dict and set ( cap)==keys and re.fullmatch ( r"mnt:\[[0-9]+\]",cap [ "parent_mnt"])is not None and re.fullmatch ( r"net:\[[0-9]+\]",cap [ "parent_net"])is not None and cap [ "outside_before_sha256"]==cap [ "outside_after_sha256"],"CAPSULE_BINDING")
 for key in ( "child_argv_sha256","outside_before_sha256","outside_after_sha256"):
  r._sha ( cap [ key],"CAPSULE_BINDING")
 first,terminal=cap [ "admission"],cap [ "result"]
 need ( type ( first)is dict and set ( first)== { "schema","child_argv_sha256","snapshot"}and first [ "schema"]=="dg17.apparmor-capsule-admission.v1"and first [ "child_argv_sha256"]==cap [ "child_argv_sha256"],"CAPSULE_ADMISSION")
 need ( type ( terminal)is dict and set ( terminal)== { "schema","before_sha256","child_argv_sha256","before","after","child_returncode","failure","child_pid","child_start_ticks"}and terminal [ "schema"]=="dg17.apparmor-capsule-result.v1"and terminal [ "before_sha256"]==sha ( pretty ( first))and terminal [ "child_argv_sha256"]==cap [ "child_argv_sha256"]and terminal [ "failure"]is None and type ( terminal [ "child_returncode"])is int and terminal [ "child_returncode"]==0 and first [ "snapshot"]==terminal [ "before"]==terminal [ "after"],"CAPSULE_RESULT")
 host=value [ "parent_host"]
 need ( snapshot_valid ( first [ "snapshot"],host [ "uid"],host [ "gid"],cap [ "parent_mnt"],cap [ "parent_net"],e,context),"CAPSULE_STATE")
 observation,receipt=value [ "observation"],value [ "worker_receipt"]
 need ( type ( observation)is dict and type ( receipt)is dict,"WORKER_RESULT")
 worker_host=observation [ "after"] [ "host"]
 for key in ( "boot_id_sha256","kernel_release_sha256","kernel_version_sha256","machine","uid","gid","user_namespace_sha256","lsm_label_sha256"):
  need ( worker_host [ key]==host [ key],"PARENT_WORKER_HOST_JOIN")
 need ( type ( terminal [ "child_pid"])is int and worker_host [ "pid"]==terminal [ "child_pid"]and type ( terminal [ "child_start_ticks"])is int and worker_host [ "process_start_ticks"]==terminal [ "child_start_ticks"],"ACTUAL_CHILD_PID_JOIN")
 for key,expected_value in first [ "snapshot"] [ "namespace_binding"].items ():
  need ( worker_host [ key]==expected_value,"CAPSULE_NAMESPACE_JOIN")
 need ( observation [ "before"] [ "loaded"] [ "custody"] [ "custody_sha256"]==observation [ "after"] [ "loaded"] [ "custody"] [ "custody_sha256"]==sha ( enc ( first [ "snapshot"] [ "profiles_descriptor"] [ "identity"])),"CAPSULE_DESCRIPTOR_JOIN")
 regenerated=r.receive_record ( enc ( observation),context,source,worker_host,receipt.get ( "received_at_ns"))
 need ( regenerated==receipt and type ( now_ns)is int and receipt [ "received_at_ns"]<=now_ns<=receipt [ "received_at_ns"]+5000000000,"WORKER_RECEIPT_JOIN")
 outer=value [ "outer_capture"]
 need ( type ( outer)is dict and set ( outer)==set ( OUTER_FIELDS),"OUTER_FIELDS")
 need ( all ( outer [ k]is True for k in ( "process_started","pidfd_acquired","streams_complete"))and all ( outer [ k]is False for k in ( "timeout","output_bound_exceeded","internal_failure"))and type ( outer [ "returncode"])is int and outer [ "returncode"]==0 and outer [ "start_errno"]is None and type ( outer [ "stdout_bytes"])is int and outer [ "stdout_bytes"]==len ( enc ( receipt))<=32768 and outer [ "stdout_sha256"]==sha ( enc ( receipt))and type ( outer [ "stderr_bytes"])is int and outer [ "stderr_bytes"]==0 and outer [ "stderr_sha256"]==sha ( b""),"OUTER_CAPTURE")
 r._cleanup ( outer [ "cleanup"])
 need ( len ( enc ( value))<=65536,"PUBLIC_BOUND")
 return { "schema":"dg17.apparmor.preparation-bridge-receipt.v1","status":"RECEIVED_OWNED_NO_LOAD_PREPARATION","candidate_identity":IDENTITY,"observation_sha256":sha ( enc ( value)),"context":context,"source":source,"activation_authority":"NONE",**SCOPE}
def outer_record ( records):
 if len ( records)!=1 or type ( records [ 0])is not dict:
  return None
 record=records [ 0]
 result= { key:record.get ( key)for key in OUTER_FIELDS}
 result [ "internal_failure"]=record.get ( "internal_failure")is not None
 if type ( result [ "cleanup"])is dict:
  result [ "cleanup"]= { key:result [ "cleanup"].get ( key)for key in CLEANUP_FIELDS}
 return result
def artifact_facts ( output):
 facts,bodies= {}, {}
 for key, ( name,bound)in ARTIFACTS.items ():
  try:
   body=read ( output/"private"/name,bound)
   facts [ key]= { "state":"CAPTURED","bytes":len ( body),"sha256":sha ( body)}
   bodies [ key]=body
  except FileNotFoundError:
   facts [ key]= { "state":"UNAVAILABLE","bytes":None,"sha256":None}
  except Exception:
   facts [ key]= { "state":"REFUSED","bytes":None,"sha256":None}
 return facts,bodies
def receive_failure ( value,context,source,r):
 keys= { "schema","candidate_identity","context","source","parent_host","stage","outer_capture","private_streams","bookends","artifacts","parser_stages","cleanup_state",*SCOPE}
 need ( type ( value)is dict and set ( value)==keys and value [ "schema"]=="dg17.apparmor.preparation-bridge-failure.v1"and value [ "candidate_identity"]==IDENTITY and value [ "context"]==context and value [ "source"]==source and all ( value [ k]==v and type ( value [ k])is type ( v)for k,v in SCOPE.items ()),"FAILURE_FIELDS")
 r._context ( context);r._source ( source);r._host ( value [ "parent_host"])
 need ( value [ "stage"]in ( "OUTER_CAPTURE","BOOKENDS","WORKER_RECEIVING","RESULT_RECEIVING")and value [ "cleanup_state"]in ( "QUIESCENT","UNESTABLISHED"),"FAILURE_STAGE")
 outer=value [ "outer_capture"]
 if outer is not None:
  need ( type ( outer)is dict and set ( outer)==set ( OUTER_FIELDS),"FAILURE_OUTER")
  for key in ( "process_started","pidfd_acquired","timeout","output_bound_exceeded","internal_failure","streams_complete"):
   need ( outer [ key]is None or type ( outer [ key])is bool,"FAILURE_OUTER")
  for key,low,high in ( ( "returncode",-128,255), ( "start_errno",1,4096), ( "stdout_bytes",0,32768), ( "stderr_bytes",0,32768)):
   if outer [ key]is not None:
    r._int ( outer [ key],low,high,"FAILURE_OUTER")
  for key in ( "stdout_sha256","stderr_sha256"):
   if outer [ key]is not None:
    r._sha ( outer [ key],"FAILURE_OUTER")
  cleanup=outer [ "cleanup"]
  if cleanup is not None:
   need ( type ( cleanup)is dict and set ( cleanup)==set ( CLEANUP_FIELDS)and type ( cleanup [ "echild"])is bool,"FAILURE_CLEANUP")
   r._int ( cleanup [ "pidfd_signals"],0,4096,"FAILURE_CLEANUP")
   r._cleanup ( dict ( cleanup,echild=True,pidfd_signals=0))
 streams=value [ "private_streams"]
 need ( type ( streams)is dict and set ( streams)== { "stdout","stderr"}and all ( v in ( "RETAINED","UNAVAILABLE")for v in streams.values ()),"FAILURE_STREAMS")
 bookends=value [ "bookends"]
 need ( type ( bookends)is dict and set ( bookends)== { "source","parent_host","outside","helper","context"},"FAILURE_BOOKENDS")
 for row in bookends.values ():
  need ( type ( row)is dict and set ( row)== { "state","before_sha256","after_sha256"}and row [ "state"]in ( "EQUAL","CHANGED","REFUSED","UNOBSERVED"),"FAILURE_BOOKENDS")
  r._sha ( row [ "before_sha256"],"FAILURE_BOOKENDS")
  if row [ "state"]in ( "EQUAL","CHANGED"):
   r._sha ( row [ "after_sha256"],"FAILURE_BOOKENDS")
   need ( ( row [ "before_sha256"]==row [ "after_sha256"])is ( row [ "state"]=="EQUAL"),"FAILURE_BOOKENDS")
  else:
   need ( row [ "after_sha256"]is None,"FAILURE_BOOKENDS")
 need ( bookends [ "source"] [ "before_sha256"]==sha ( enc ( source))and bookends [ "parent_host"] [ "before_sha256"]==sha ( enc ( value [ "parent_host"]))and bookends [ "context"] [ "before_sha256"]==sha ( enc ( closed_environment ( context))),"FAILURE_BINDING")
 facts=value [ "artifacts"]
 need ( type ( facts)is dict and set ( facts)==set ( ARTIFACTS),"FAILURE_ARTIFACTS")
 for key,row in facts.items ():
  need ( type ( row)is dict and set ( row)== { "state","bytes","sha256"}and row [ "state"]in ( "CAPTURED","UNAVAILABLE","REFUSED"),"FAILURE_ARTIFACTS")
  if row [ "state"]=="CAPTURED":
   r._int ( row [ "bytes"],1,ARTIFACTS [ key] [ 1],"FAILURE_ARTIFACTS");r._sha ( row [ "sha256"],"FAILURE_ARTIFACTS")
  else:
   need ( row [ "bytes"]is None and row [ "sha256"]is None,"FAILURE_ARTIFACTS")
 stages=value [ "parser_stages"]
 need ( type ( stages)is dict and set ( stages)== { "version","compile"}and all ( v in ( "CAPTURE_VALID","REFUSED","UNAVAILABLE")for v in stages.values ()),"FAILURE_PARSER_STAGES")
 need ( all ( ( v=="UNAVAILABLE")== ( facts [ "observation"] [ "state"]!="CAPTURED")for v in stages.values ()),"FAILURE_OBSERVATION_STAGE_JOIN")
 need ( len ( enc ( value))<=65536,"PUBLIC_BOUND")
 return { "schema":"dg17.apparmor.preparation-bridge-receipt.v1","status":"RECEIVED_BOUNDED_FAILURE_ONLY","candidate_identity":IDENTITY,"observation_sha256":sha ( enc ( value)),"context":context,"source":source,"activation_authority":"NONE",**SCOPE}
def parent_arguments ( source,output,context_sha,pin,uid,gid,host,derived):
 values= ( str ( source),pin,str ( output/"private/CONTEXT.json"),context_sha,str ( output),str ( uid),str ( gid),host [ "parent_mount_namespace"],host [ "parent_net_namespace"],"3",derived [ "code_sha256"],derived [ "script_sha256"])
 return [ part for pair in zip ( ( "--"+key for key in FIELDS),values)for part in pair]
def run_parent ( source_root,expected_manifest_sha256,expected_context):
 actual_context ( expected_context)
 need ( os.getuid ()==os.geteuid ()>0 and os.getgid ()==os.getegid ()>0,"PARENT_OWNER")
 source=Path ( source_root)
 need ( source==Path ( os.environ [ "GITHUB_WORKSPACE"])/"packet","PARENT_SOURCE")
 output=Path ( os.environ [ "RUNNER_TEMP"])/ ( "dg17-apparmor-"+expected_context [ "run_id"]+"-a1")
 need ( output.parent.is_absolute ()and output.parent.resolve ( strict=True)==output.parent,"PARENT_OUTPUT")
 a,u,e,p,r,binding,bodies,manifest=load ( source,expected_manifest_sha256)
 derived=derive ( e,expected_manifest_sha256)
 need ( ctypes.CDLL ( None,use_errno=True).prctl ( 36,1,0,0,0)==0,"PARENT_SUBREAPER")
 a.owned_quiescent ( u)
 output.mkdir ( mode=0o700)
 for name in ( "private","public","home","tmp"):
  ( output/name).mkdir ( mode=0o700)
 context_raw=enc ( expected_context)
 write ( output/"private/CONTEXT.json",context_raw,4096)
 tools= {}
 for name in ( "bash","unshare","setpriv","python3","env","timeout"):
  path,fact=u.trusted ( name)
  expected=r"/usr/bin/python3(?:\.[0-9]{1,2})?"if name=="python3"else"/usr/bin/"+name
  need ( path is not None and re.fullmatch ( expected,path)is not None,"PARENT_TOOL")
  tools [ name]=fact
 tools [ "mount"]=e.mount_role ();tools [ "sudo"]=p.root_tools ( u) [ "sudo"]
 state= { "host": { "tools":tools}}
 outside=e.capsule_host_snapshot ( state,u)
 parent_host=a.PhysicalIO ( time.monotonic ()+20).host_binding ()
 helper=p.physical_helper ()
 need ( helper.get ( "status")=="PHYSICAL_HELPER_ADMITTED"and helper.get ( "bytes")==72160 and helper.get ( "sha256")==a.HELPER_SHA,"PARENT_HELPER")
 args=parent_arguments ( source,output,sha ( context_raw),expected_manifest_sha256,os.getuid (),os.getgid (),outside,derived)
 arguments ( args)
 child= [ "/usr/bin/python3","-I","-S","-B","-c",BOOTSTRAP,str ( source/DIRECTORY/"bridge.py"),expected_manifest_sha256,*args]
 argv= [ "/usr/bin/env","HOME="+str ( output/"home"),"CODEX_HOME="+str ( output/"home/codex"),"TMPDIR="+str ( output/"tmp"),"/usr/bin/sudo","-n","/usr/bin/timeout","--signal=TERM","--kill-after=5s","20s","/usr/bin/unshare","--mount","--net","--propagation","private","--","/usr/bin/bash","--noprofile","--norc","-c",derived [ "script"],"dg17-private-view",str ( os.getuid ()),str ( os.getgid ()),derived [ "code"],str ( output/"private/CAPSULE_ADMISSION.json"),str ( output/"private/CAPSULE_RESULT.json"),outside [ "parent_mount_namespace"],outside [ "parent_net_namespace"],str ( source/DIRECTORY/"bridge.py"),*args]
 records= [];deadline=time.monotonic ()+30
 rc,stdout,stderr,capture_ok=None,None,None,False
 try:
  rc,stdout,stderr=u.capture ( "apparmor-preparation-capsule",argv,records,deadline,seconds=30)
  capture_ok=True
 except BaseException as exc:
  captured=getattr ( exc,"captured",None)
  if type ( captured)is dict:
   rc,stdout,stderr= ( captured.get ( key)for key in ( "returncode","stdout","stderr"))
 cleanup_state="QUIESCENT"
 try:
  a.owned_quiescent ( u)
 except BaseException:
  cleanup_state="UNESTABLISHED"
 streams= {}
 for name,raw in ( ( "stdout",stdout), ( "stderr",stderr)):
  streams [ name]="UNAVAILABLE"
  if type ( raw)is bytes and len ( raw)<=32768:
   write ( output/"private"/ ( "CAPSULE."+name),raw,32768)
   streams [ name]="RETAINED"
 need ( len ( records)<=1,"OUTER_POPULATION")
 write ( output/"private/OUTER_CAPTURE.json",pretty ( records))
 outer=outer_record ( records)
 baseline= { "source":binding,"parent_host":parent_host,"outside":outside,"helper":helper,"context":closed_environment ( expected_context)}
 checks= { "source":lambda:a.source_closure ( source,manifest,expected_manifest_sha256,min ( deadline,time.monotonic ()+2)) [ 0],"parent_host":lambda:a.PhysicalIO ( min ( deadline,time.monotonic ()+2)).host_binding (),"outside":lambda:e.capsule_host_snapshot ( state,u),"helper":p.physical_helper,"context":lambda:actual_context ( expected_context)}
 bookends,fresh= {}, {}
 for key,call in checks.items ():
  row= { "state":"UNOBSERVED","before_sha256":sha ( enc ( baseline [ key])),"after_sha256":None}
  if time.monotonic ()<deadline:
   try:
    fresh [ key]=call ();row [ "after_sha256"]=sha ( enc ( fresh [ key]))
    row [ "state"]="EQUAL"if row [ "before_sha256"]==row [ "after_sha256"]else"CHANGED"
   except BaseException:
    row [ "state"]="REFUSED"
  bookends [ key]=row
 facts,available=artifact_facts ( output)
 stage="OUTER_CAPTURE"
 try:
  need ( capture_ok and rc==0 and cleanup_state=="QUIESCENT"and all ( v=="RETAINED"for v in streams.values ()),"OUTER_RETURN")
  stage="BOOKENDS"
  need ( all ( row [ "state"]=="EQUAL"for row in bookends.values ()),"PARENT_BOOKENDS")
  stage="WORKER_RECEIVING"
  observation=a.strict ( available [ "observation"],65536)
  receipt_raw=available [ "worker_receipt"]
  need ( stdout==receipt_raw,"WORKER_STDOUT_JOIN")
  proofs= {}
  for key in ( "capsule_admission","capsule_result"):
   proofs [ key]=json.loads ( available [ key],object_pairs_hook=e.unique_object)
   need ( pretty ( proofs [ key])==available [ key],"CAPSULE_ENCODING")
  capsule= { "parent_mnt":outside [ "parent_mount_namespace"],"parent_net":outside [ "parent_net_namespace"],"child_argv_sha256":sha ( e.encoded ( child)),"admission":proofs [ "capsule_admission"],"result":proofs [ "capsule_result"],"outside_before_sha256":sha ( e.encoded ( outside)),"outside_after_sha256":sha ( e.encoded ( fresh [ "outside"]))}
  result= { "schema":"dg17.apparmor.preparation-bridge.v1","candidate_identity":IDENTITY,"context":expected_context,"source":binding,"parent_host":parent_host,"derivation": { "script_sha256":derived [ "script_sha256"],"code_sha256":derived [ "code_sha256"],"original_script_sha256":SCRIPT_SHA,"original_code_sha256":CODE_SHA,"loopback_initializer_sha256":LOOP_SHA},"capsule":capsule,"outer_capture":outer,"observation":observation,"worker_receipt":a.strict ( receipt_raw,16384),"source_bookends_equal":True,"host_bookends_equal":True,**SCOPE}
  stage="RESULT_RECEIVING"
  received=receive_result ( result,expected_context,binding,e,r,time.monotonic_ns ())
 except BaseException:
  parser_stages= { "version":"UNAVAILABLE","compile":"UNAVAILABLE"}
  if"observation"in available:
   for name in parser_stages:
    try:
     observation=a.strict ( available [ "observation"],65536)
     need ( observation [ "context"]==expected_context and observation [ "source"]==binding,"FAILURE_OBSERVATION_BINDING")
     r.validate_capture ( observation [ name+"_capture"],name.upper ())
     parser_stages [ name]="CAPTURE_VALID"
    except BaseException:
     parser_stages [ name]="REFUSED"
  result= { "schema":"dg17.apparmor.preparation-bridge-failure.v1","candidate_identity":IDENTITY,"context":expected_context,"source":binding,"parent_host":parent_host,"stage":stage,"outer_capture":outer,"private_streams":streams,"bookends":bookends,"artifacts":facts,"parser_stages":parser_stages,"cleanup_state":cleanup_state,**SCOPE}
  received=receive_failure ( result,expected_context,binding,r)
 write ( output/"public/RESULT.json",enc ( result))
 write ( output/"public/RECEIPT.json",enc ( received))
 return received
if __name__=="__main__":
 try:
  raise SystemExit ( root_entry ( sys.argv [ 2:])if len ( sys.argv)>1 and sys.argv [ 1]=="--root"else worker_entry ( sys.argv [ 1:]))
 except SystemExit:
  raise
 except BaseException:
  sys.stderr.write ( "DG17_APPARMOR_BRIDGE_REFUSED\n")
  raise SystemExit ( 1)
