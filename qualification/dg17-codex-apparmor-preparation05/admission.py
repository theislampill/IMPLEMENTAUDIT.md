import contextlib
import ctypes
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import time
import types
IDENTITY="dg17-9077-codex20-apparmor-preparation05"
DIRECTORY="qualification/dg17-codex-apparmor-preparation05"
UTILITY_PATH="qualification/dg17-codex-routing/host_utility.py"
EPISODE_PATH="qualification/dg17-codex-routing/episode.py"
PREPARER_PATH="qualification/dg17-codex-host-preparation02/prepare.py"
UTILITY_SHA="429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c"
EPISODE_SHA="4dc7aacb793e1d65ed1fa51335800fbfaa7c9af777369877f2828113006a8466"
PREPARER_SHA="03afcc3f26311249459d019d15dd55fd835e99b9cc2b6f3ff9f748cf44436488"
PROFILE_SHA="11d39094f044f0cda0febb3ad517b830301da6b2ce929664af09ee9e4dd264f9"
README_SHA="4fe5017b356227ddc57ddcb489e75e6437c6e2d2972c0a8545af437734124c83"
HELPER_SHA="e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71"
ETC="/etc/apparmor.d/"
FEATURE_ROOT="/sys/kernel/security/apparmor/features"
LOADED="/sys/kernel/security/apparmor/profiles"
PARSER="/usr/sbin/apparmor_parser"
HELPER="/usr/bin/bwrap"
INSTALLED=ETC+"bwrap-userns-restrict"
EXTRA="/usr/share/apparmor/extra-profiles/bwrap-userns-restrict"
OPTIONALS= ( ETC+"local/bwrap-userns-restrict",ETC+"local/unpriv_bwrap")
INCLUDE_ROOTS= ( ETC+"tunables/global",*OPTIONALS)
ENABLED="/sys/module/apparmor/parameters/enabled"
LIMITS= { "source_limit_bytes":4194304,"public_result_limit_bytes":65536,"outer_stream_limit_bytes":32768,"stderr_limit_bytes":65536,"outer_timeout_seconds":30,"root_watchdog_seconds":20,"root_kill_after_seconds":5,"owned_cleanup_seconds":4,"owned_live_child_limit":8,"parser_timeout_ms":10000,"freshness_ms":5000,"include_nodes":32,"include_edges":64,"include_bytes":262144,"feature_nodes":256,"feature_bytes":65536,"feature_depth":8,"model_calls":0,"helper_attempt_limit":0,}
SEGMENT=re.compile ( r"[A-Za-z0-9_+-][A-Za-z0-9_.+-]{0,79}\Z")
FIXED= { HELPER,PARSER,"/dev/null",ETC+"abi/4.0",INSTALLED,EXTRA,ENABLED,LOADED}
SOURCE_PATHS=tuple ( sorted ( ( DIRECTORY+"/admission.py",DIRECTORY+"/receiver.py",DIRECTORY+"/bridge.py",DIRECTORY+"/bwrap-userns-restrict",DIRECTORY+"/README",UTILITY_PATH,EPISODE_PATH,PREPARER_PATH)))
class Refusal ( ValueError):
 pass
def need ( value,code):
 if value is not True:
  raise Refusal ( code)
def sha ( raw):
 return hashlib.sha256 ( raw).hexdigest ()
def encoded ( value):
 return ( json.dumps ( value,sort_keys=True,separators= ( ",",":"),ensure_ascii=True,allow_nan=False)+"\n").encode ( "ascii")
def strict ( raw,bound):
 need ( type ( raw)is bytes and 0<len ( raw)<=bound,"JSON_BOUND")
 def pairs ( items):
  output= {}
  for key,value in items:
   need ( key not in output,"JSON_DUPLICATE")
   output [ key]=value
  return output
 def reject ( value):
  raise Refusal ( "JSON_NONFINITE")
 try:
  value=json.loads ( raw.decode ( "ascii"),object_pairs_hook=pairs,parse_constant=reject)
 except ( UnicodeError,json.JSONDecodeError):
  raise Refusal ( "JSON_SYNTAX")from None
 need ( encoded ( value)==raw,"JSON_ENCODING")
 return value
def stat_identity ( info):
 return { key:getattr ( info,"st_"+key)for key in ( "dev","ino","mode","uid","gid","nlink","size","mtime_ns","ctime_ns")}
def ancestry_identity ( info):
 return tuple ( getattr ( info,"st_"+key)for key in ( "dev","ino","mode","uid","gid"))
class Node:
 def __init__ ( self,row,raw=None,entries=None):
  self.row,self.raw,self.entries=row,raw,entries
def unavailable ( path,state,number=None,absence_custody=None):
 return Node ( { "path":path,"state":state,"kind":None,"bytes":0,"sha256":None,"custody_sha256":absence_custody if state=="ABSENT"else None,"mode":None,"uid":None,"gid":None,"nlink":None,"errno":number if type ( number)is int and 0<=number<=4096 else None})
class MissingLeaf ( OSError):
 pass
@contextlib.contextmanager
def held ( path,deadline,host=True,pseudo=False,char=False,descriptor=None):
 need ( type ( path)is str and path.startswith ( "/")and"\x00"not in path,"PHYSICAL_PATH")
 parts=path [ 1:].split ( "/")
 need ( all ( part and part not in ( ".","..")for part in parts),"PHYSICAL_PATH")
 handles,anchors= [], []
 try:
  handles.append ( os.open ( "/",os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC))
  for part in parts [ :-1]:
   need ( time.monotonic ()<deadline,"READ_DEADLINE")
   current=os.fstat ( handles [ -1])
   need ( not host or current.st_uid==0 and current.st_gid==0 and not current.st_mode&0o022,"PHYSICAL_ANCESTRY")
   child=os.open ( part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=handles [ -1])
   anchors.append ( ( handles [ -1],part,child,ancestry_identity ( os.fstat ( child))))
   handles.append ( child)
  parent=os.fstat ( handles [ -1])
  need ( not host or parent.st_uid==0 and parent.st_gid==0 and not parent.st_mode&0o022,"PHYSICAL_ANCESTRY")
  if descriptor is None:
   try:
    fd=os.open ( parts [ -1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=handles [ -1])
   except FileNotFoundError as exc:
    try:
     os.stat ( parts [ -1],dir_fd=handles [ -1],follow_symlinks=False)
    except FileNotFoundError:
     missing=MissingLeaf ( errno.ENOENT,"ABSENT_LEAF")
     missing.custody_sha256=sha ( encoded ( { "parent":stat_identity ( os.fstat ( handles [ -1])),"leaf":parts [ -1]}))
     raise missing from None
    raise Refusal ( "ABSENCE_CHANGED")from exc
  else:
   need ( type ( descriptor)is int and 2<descriptor<1048576,"INHERITED_DESCRIPTOR")
   flags=fcntl.fcntl ( descriptor,fcntl.F_GETFL)
   need ( flags&os.O_ACCMODE==os.O_RDONLY and not flags&getattr ( os,"O_PATH",0),"INHERITED_READONLY")
   fd=os.dup ( descriptor)
  handles.append ( fd)
  before=os.fstat ( fd)
  need ( stat_identity ( before)==stat_identity ( os.stat ( parts [ -1],dir_fd=handles [ -2],follow_symlinks=False)),"INHERITED_PATH_BINDING")
  need ( stat.S_ISREG ( before.st_mode)or stat.S_ISDIR ( before.st_mode)or char and stat.S_ISCHR ( before.st_mode),"PHYSICAL_KIND")
  need ( not host or before.st_uid==before.st_gid==0,"PHYSICAL_OWNER")
  need ( not host or char or not before.st_mode&0o022,"PHYSICAL_WRITABLE")
  need ( not stat.S_ISREG ( before.st_mode)or before.st_nlink==1,"PHYSICAL_LINKS")
  yield fd,before
  need ( stat_identity ( before)==stat_identity ( os.fstat ( fd))==stat_identity ( os.stat ( parts [ -1],dir_fd=handles [ -2],follow_symlinks=False)),"PHYSICAL_CHANGED")
 finally:
  changed=False
  for parent_fd,name,child_fd,initial in anchors:
   try:
    changed=changed or ancestry_identity ( os.fstat ( child_fd))!=initial
    changed=changed or ancestry_identity ( os.stat ( name,dir_fd=parent_fd,follow_symlinks=False))!=initial
   except OSError:
    changed=True
  for fd in reversed ( handles):
   os.close ( fd)
  need ( not changed,"PHYSICAL_ANCESTRY_CHANGED")
def read_fd ( fd,bound,deadline):
 raw=bytearray ()
 while len ( raw)<=bound:
  need ( time.monotonic ()<deadline,"READ_DEADLINE")
  part=os.read ( fd,min ( 65536,bound+1-len ( raw)))
  if not part:
   break
  raw.extend ( part)
 need ( len ( raw)<=bound,"READ_BOUND")
 return bytes ( raw)
def present_node ( path,info,raw,entries=None,kind=None):
 if kind is None:
  kind="DIRECTORY"if entries is not None else"FILE"
 body=encoded ( entries)if entries is not None else raw
 return Node ( { "path":path,"state":"PRESENT","kind":kind,"bytes":len ( body),"sha256":sha ( body),"custody_sha256":sha ( encoded ( stat_identity ( info))),"mode":info.st_mode,"uid":info.st_uid,"gid":info.st_gid,"nlink":info.st_nlink,"errno":None},raw,entries)
def safe_segments ( path):
 return all ( SEGMENT.fullmatch ( part)is not None for part in path.split ( "/"))
class PhysicalIO:
 def __init__ ( self,deadline,loaded_profiles_fd=None):
  self.deadline=deadline
  self.loaded_profiles_fd=loaded_profiles_fd
 def allowed ( self,path):
  if path in FIXED or path in OPTIONALS:
   return True
  if path.startswith ( ETC+"tunables/"):
   suffix=path [ len ( ETC):]
   return len ( suffix.split ( "/"))<=8 and safe_segments ( suffix)
  if path==FEATURE_ROOT:
   return True
  if path.startswith ( FEATURE_ROOT+"/"):
   suffix=path [ len ( FEATURE_ROOT)+1:]
   return len ( suffix.split ( "/"))<=LIMITS [ "feature_depth"]and safe_segments ( suffix)
  return False
 def read_node ( self,path,bound):
  need ( self.allowed ( path)and type ( bound)is int and 0<bound<=LIMITS [ "source_limit_bytes"],"FIXED_READ_SURFACE")
  if path==LOADED and self.loaded_profiles_fd is None:
   return unavailable ( path,"UNKNOWN")
  try:
   with held ( path,self.deadline,char=path=="/dev/null",pseudo=path.startswith ( "/sys/"),descriptor=self.loaded_profiles_fd if path==LOADED else None)as ( fd,info):
    if stat.S_ISDIR ( info.st_mode):
     entries= []
     cap=LIMITS [ "feature_nodes"]if path.startswith ( FEATURE_ROOT)else LIMITS [ "include_nodes"]
     with os.scandir ( fd)as iterator:
      for entry in iterator:
       need ( time.monotonic ()<self.deadline,"READ_DEADLINE")
       need ( len ( entries)<cap and SEGMENT.fullmatch ( entry.name)is not None,"DIRECTORY_BOUND_OR_NAME")
       entries.append ( entry.name)
     entries.sort ()
     need ( len ( encoded ( entries))<=bound,"DIRECTORY_BOUND")
     return present_node ( path,info,None,entries)
    if path=="/dev/null":
     need ( stat.S_ISCHR ( info.st_mode)and os.major ( info.st_rdev)==1 and os.minor ( info.st_rdev)==3,"EMPTY_CONFIGURATION")
     return present_node ( path,info,b"1:3",kind="CHAR")
    need ( stat.S_ISREG ( info.st_mode)and info.st_size<=bound,"READ_FILE_BOUND")
    if path==LOADED:
     need ( os.lseek ( fd,0,os.SEEK_SET)==0,"PROFILES_RESEEK")
    raw=read_fd ( fd,bound,self.deadline)
    need ( path.startswith ( "/sys/")or len ( raw)==info.st_size,"READ_SIZE")
    if path in ( PARSER,HELPER):
     need ( not info.st_mode&0o6022 and bool ( info.st_mode&0o111),"EXECUTABLE_MODE")
     need ( len ( raw)>=64 and raw [ :7]==b"\x7fELF\x02\x01\x01"and int.from_bytes ( raw [ 16:18],"little")in ( 2,3)and int.from_bytes ( raw [ 18:20],"little")==62,"EXECUTABLE_ELF")
     try:
      caps=os.getxattr ( fd,"security.capability")
     except OSError as exc:
      need ( exc.errno in ( errno.ENODATA,errno.ENOTSUP),"EXECUTABLE_CAPABILITIES_UNKNOWN")
      caps=b""
     need ( caps==b"","EXECUTABLE_CAPABILITIES")
    return present_node ( path,info,raw)
  except MissingLeaf as exc:
   return unavailable ( path,"ABSENT",errno.ENOENT,exc.custody_sha256)
  except OSError as exc:
   return unavailable ( path,"UNKNOWN",exc.errno)
  except Refusal:
   return unavailable ( path,"INVALID")
 def proc ( self,path,bound):
  allowed= { "/proc/sys/kernel/random/boot_id","/proc/sys/kernel/osrelease","/proc/sys/kernel/version","/proc/"+str ( os.getpid ())+"/status","/proc/"+str ( os.getpid ())+"/stat","/proc/"+str ( os.getpid ())+"/attr/current"}
  need ( path in allowed,"PROC_SURFACE")
  with held ( path,self.deadline,host=False,pseudo=True)as ( fd,info):
   need ( stat.S_ISREG ( info.st_mode),"PROC_KIND")
   return read_fd ( fd,bound,self.deadline)
 def confinement_state ( self):
  raw=self.proc ( "/proc/"+str ( os.getpid ())+"/status",16384)
  wanted= { "NoNewPrivs":"no_new_privs","CapInh":"cap_inh","CapPrm":"cap_prm","CapEff":"cap_eff","CapBnd":"cap_bnd","CapAmb":"cap_amb"}
  values= {}
  for line in raw.splitlines ():
   if b":"not in line:
    continue
   key,value=line.split ( b":",1)
   name=key.decode ( "ascii","strict")
   if name not in wanted:
    continue
   need ( wanted [ name]not in values,"PROCESS_STATUS_DUPLICATE")
   token=value.strip ()
   need ( re.fullmatch ( rb"[01]"if name=="NoNewPrivs"else rb"[0-9a-f]{16}",token)is not None,"PROCESS_STATUS_VALUE")
   values [ wanted [ name]]=int ( token,10 if name=="NoNewPrivs"else 16)
  need ( set ( values)==set ( wanted.values ()),"PROCESS_STATUS_FIELDS")
  return values
 def host_binding ( self):
  boot=self.proc ( "/proc/sys/kernel/random/boot_id",128)
  need ( re.fullmatch ( rb"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\n",boot)is not None,"BOOT_IDENTITY")
  release=self.proc ( "/proc/sys/kernel/osrelease",256)
  version=self.proc ( "/proc/sys/kernel/version",1024)
  label=self.proc ( "/proc/"+str ( os.getpid ())+"/attr/current",256)
  need ( release and version and label and b"\x00"not in release+version+label,"HOST_TEXT")
  raw_stat=self.proc ( "/proc/"+str ( os.getpid ())+"/stat",4096)
  marker=raw_stat.rfind ( b") ")
  need ( marker>0,"PROCESS_STAT")
  fields=raw_stat [ marker+2:].split ()
  need ( len ( fields)>=20 and re.fullmatch ( rb"[0-9]+",fields [ 19])is not None,"PROCESS_START")
  namespaces= {}
  for kind in ( "mnt","user"):
   path="/proc/"+str ( os.getpid ())+"/ns/"+kind
   fd=os.open ( path,os.O_RDONLY|os.O_CLOEXEC)
   try:
    info=os.fstat ( fd)
    current=os.stat ( path)
    need ( ( info.st_dev,info.st_ino)== ( current.st_dev,current.st_ino),"NAMESPACE_DRIFT")
    namespaces [ kind]=sha ( encoded ( { "dev":info.st_dev,"ino":info.st_ino}))
   finally:
    os.close ( fd)
  need ( os.getuid ()==os.geteuid ()>0 and os.getgid ()==os.getegid ()>0,"UNPRIVILEGED_OWNED_PROCESS")
  need ( os.uname ().machine=="x86_64","HOST_MACHINE")
  return { "boot_id_sha256":sha ( boot.rstrip ( b"\n")),"kernel_release_sha256":sha ( release),"kernel_version_sha256":sha ( version),"machine":"x86_64","uid":os.getuid (),"gid":os.getgid (),"pid":os.getpid (),"process_start_ticks":int ( fields [ 19]),"mount_namespace_sha256":namespaces [ "mnt"],"user_namespace_sha256":namespaces [ "user"],"lsm_label_sha256":sha ( label)}
def aare_values ( value):
 need ( type ( value)is str and 0<len ( value)<=65536,"INCLUDE_SYNTAX")
 position,count=0,0
 while position<len ( value):
  while position<len ( value)and value [ position].isspace ():
   position+=1
  if position==len ( value):
   break
  count+=1
  need ( count<=256,"INCLUDE_BOUND")
  quoted=value [ position]=='"'
  if quoted:
   end=value.find ( '"',position+1)
   need ( end>=0 and ( end+1==len ( value)or value [ end+1].isspace ()),"INCLUDE_SYNTAX")
   token,position=value [ position+1:end],end+1
  else:
   end=position
   while end<len ( value)and not value [ end].isspace ():
    end+=1
   token,position=value [ position:end],end
  need ( quoted or bool ( token),"INCLUDE_SYNTAX")
  token=re.sub ( r"@\{[A-Za-z_][A-Za-z0-9_]*\}","VAR",token)
  stack,index= [],0
  while index<len ( token):
   char=token [ index]
   if char=="[":
    end=token.find ( "]",index+1)
    need ( end>=0,"INCLUDE_SYNTAX")
    body=token [ index+1:end]
    if body.startswith ( "^"):
     body=body [ 1:]
    need ( bool ( body)and re.fullmatch ( r"[A-Za-z0-9_./*?+:=!\-]+",body)is not None,"INCLUDE_SYNTAX")
    index=end
   elif char=="{":
    need ( len ( stack)<8,"INCLUDE_BOUND")
    stack.append ( False)
   elif char==",":
    need ( bool ( stack),"INCLUDE_SYNTAX")
    stack [ -1]=True
   elif char=="}":
    need ( bool ( stack)and stack.pop ()is True,"INCLUDE_SYNTAX")
   else:
    need ( re.fullmatch ( r"[A-Za-z0-9_./*?+:=!\-]",char)is not None or quoted and char==" ","INCLUDE_SYNTAX")
   index+=1
  need ( not stack,"INCLUDE_SYNTAX")
 need ( count>0,"INCLUDE_SYNTAX")
def include_statements ( raw,local=False):
 need ( type ( raw)is bytes and len ( raw)<=65536 and b"\x00"not in raw,"INCLUDE_SYNTAX")
 try:
  lines=raw.decode ( "ascii").splitlines ()
 except UnicodeError:
  raise Refusal ( "INCLUDE_SYNTAX")from None
 includes= []
 for line in lines:
  line=line.strip ()
  if not line or line.startswith ( "#")and re.match ( r"#\s*include\b",line)is None:
   continue
  need ( not local,"CUSTOM_LOCAL_RULES")
  match=re.fullmatch ( r"(?:#\s*)?include\s+(?:(if exists)\s+)?<([^>]+)>\s*(?:#.*)?",line)
  if match:
   relative=match [ 2]
   need ( relative.startswith ( "tunables/")and len ( relative.split ( "/"))<=8 and safe_segments ( relative),"INCLUDE_SCOPE")
   includes.append ( ( ETC+relative,match [ 1]is not None))
   continue
  code=line.split ( "#",1) [ 0].strip ()
  match=re.fullmatch ( r"@\{[A-Za-z_][A-Za-z0-9_]*\}\s*(?:\+=|=)\s*(.+)",code)
  need ( match is not None,"INCLUDE_SYNTAX")
  aare_values ( match [ 1])
 return includes
def include_closure ( io):
 nodes,edges,visiting,complete= {}, [],set (),set ()
 total=0
 code=None
 def visit ( path,optional,depth):
  nonlocal total
  need ( depth<=8 and len ( nodes)<LIMITS [ "include_nodes"]or path in nodes,"INCLUDE_BOUND")
  need ( path not in visiting,"INCLUDE_CYCLE")
  if path in complete:
   if not optional:
    need ( nodes [ path] [ "state"]=="PRESENT","INCLUDE_UNAVAILABLE")
   return
  node=io.read_node ( path,65536)
  nodes [ path]=node.row
  total+=node.row [ "bytes"]
  need ( total<=LIMITS [ "include_bytes"],"INCLUDE_BOUND")
  if node.row [ "state"]=="ABSENT"and optional:
   complete.add ( path)
   return
  need ( node.row [ "state"]=="PRESENT","INCLUDE_UNAVAILABLE")
  visiting.add ( path)
  if node.row [ "kind"]=="DIRECTORY":
   need ( path not in OPTIONALS and type ( node.entries)is list and len ( node.entries)<=LIMITS [ "include_nodes"],"INCLUDE_SYNTAX")
   for name in node.entries:
    need ( type ( name)is str and SEGMENT.fullmatch ( name)is not None,"INCLUDE_SYNTAX")
    child=path+"/"+name
    need ( len ( edges)<LIMITS [ "include_edges"],"INCLUDE_BOUND")
    edges.append ( { "from":path,"to":child,"optional":False,"kind":"MEMBER"})
    visit ( child,False,depth+1)
  else:
   need ( node.row [ "kind"]=="FILE","INCLUDE_SYNTAX")
   for child,child_optional in include_statements ( node.raw,local=path in OPTIONALS):
    need ( len ( edges)<LIMITS [ "include_edges"],"INCLUDE_BOUND")
    edges.append ( { "from":path,"to":child,"optional":child_optional,"kind":"INCLUDE"})
    visit ( child,child_optional,depth+1)
  visiting.remove ( path)
  complete.add ( path)
 try:
  for root in INCLUDE_ROOTS:
   visit ( root,root in OPTIONALS,0)
 except ( Refusal,OSError,ValueError)as exc:
  known= { "INCLUDE_UNAVAILABLE","INCLUDE_SYNTAX","INCLUDE_SCOPE","INCLUDE_CYCLE","INCLUDE_BOUND","CUSTOM_LOCAL_RULES","INCLUDE_DRIFT"}
  code=str ( exc)if isinstance ( exc,Refusal)and str ( exc)in known else"INCLUDE_UNAVAILABLE"
  for root in INCLUDE_ROOTS:
   if root not in nodes:
    nodes [ root]=unavailable ( root,"UNKNOWN").row
 population= { "nodes": [ nodes [ path]for path in sorted ( nodes)],"edges":sorted ( edges,key=encoded)}
 return { "state":"REFUSED"if code else"COMPLETE","code":code,**population,"sha256":sha ( encoded ( population))}
def feature_closure ( io):
 rows,total,code= [],0,None
 root_custody=None
 def visit ( path,depth):
  nonlocal total,root_custody
  need ( depth<=LIMITS [ "feature_depth"]and len ( rows)<LIMITS [ "feature_nodes"],"FEATURE_BOUND")
  node=io.read_node ( path,65536 if path==FEATURE_ROOT else 4096)
  need ( node.row [ "state"]=="PRESENT","FEATURE_UNAVAILABLE")
  if path==FEATURE_ROOT:
   root_custody=node.row [ "custody_sha256"]
  rows.append ( node.row)
  total+=node.row [ "bytes"]
  need ( total<=LIMITS [ "feature_bytes"],"FEATURE_BOUND")
  if node.row [ "kind"]=="DIRECTORY":
   need ( type ( node.entries)is list,"FEATURE_SHAPE")
   for name in node.entries:
    need ( type ( name)is str and SEGMENT.fullmatch ( name)is not None,"FEATURE_SHAPE")
    visit ( path+"/"+name,depth+1)
  else:
   need ( node.row [ "kind"]=="FILE"and type ( node.raw)is bytes and b"\x00"not in node.raw,"FEATURE_SHAPE")
 try:
  visit ( FEATURE_ROOT,0)
 except ( Refusal,OSError,ValueError)as exc:
  known= { "FEATURE_UNAVAILABLE","FEATURE_BOUND","FEATURE_SHAPE","FEATURE_DRIFT"}
  code=str ( exc)if isinstance ( exc,Refusal)and str ( exc)in known else"FEATURE_UNAVAILABLE"
 return { "state":"REFUSED"if code else"COMPLETE","code":code,"node_count":len ( rows),"total_bytes":total,"sha256":sha ( encoded ( sorted ( rows,key=lambda row:row [ "path"]))),"root_custody_sha256":root_custody}
def loaded_projection ( io):
 node=io.read_node ( LOADED,65536)
 result= { "state":"UNKNOWN","code":"LOADED_UNAVAILABLE","bytes":node.row [ "bytes"],"sha256":node.row [ "sha256"],"relevant": [],"attachment_coverage":"UNOBSERVED","read_interface":"INHERITED_READONLY_FIXED_PROFILES_FD_V1","custody":node.row}
 if node.row [ "state"]!="PRESENT":
  return result
 try:
  need ( type ( node.raw)is bytes and len ( node.raw)<=65536 and b"\x00"not in node.raw,"LOADED_BOUND")
  for line in node.raw.decode ( "ascii").splitlines ():
   need ( 0<len ( line)<=1024,"LOADED_BOUND")
   match=re.fullmatch ( r"(.+) \((enforce|complain|kill|unconfined)\)",line)
   need ( match is not None,"LOADED_SYNTAX")
   name=match [ 1]
   if name=="bwrap":
    label="BWRAP"
   elif name=="unpriv_bwrap":
    label="UNPRIV_BWRAP"
   elif name=="/usr/bin/bwrap":
    label="BWRAP_ATTACHMENT_NAME"
   elif re.search ( r"(?:^|[/&:])(?:bwrap|unpriv_bwrap)(?:$|[/&:])",name):
    label="BWRAP_STACK"
   else:
    continue
   need ( len ( result [ "relevant"])<8,"LOADED_BOUND")
   result [ "relevant"].append ( { "name":label,"mode":match [ 2]})
  result [ "relevant"].sort ( key=encoded)
  result.update ( state="OBSERVED",code=None)
 except ( Refusal,UnicodeError)as exc:
  result.update ( state="INVALID",code=str ( exc)if isinstance ( exc,Refusal)else"LOADED_SYNTAX")
 return result
def collect_snapshot ( io,context,source,now_ns):
 return { "schema":"dg17.apparmor.same-host.snapshot.v1","candidate_identity":IDENTITY,"context":dict ( context),"source":dict ( source),"monotonic_ns":now_ns,"host":io.host_binding (),"confinement":io.confinement_state (),"helper":io.read_node ( HELPER,72160).row,"parser":io.read_node ( PARSER,2097152).row,"null_config":io.read_node ( "/dev/null",64).row,"abi":io.read_node ( ETC+"abi/4.0",65536).row,"installed_profile":io.read_node ( INSTALLED,65536).row,"installed_extra":io.read_node ( EXTRA,65536).row,"includes":include_closure ( io),"features":feature_closure ( io),"loaded":loaded_projection ( io),"apparmor_enabled":io.read_node ( ENABLED,16).row,}
def parser_argv ( mode,executable_fd,profile_fd=None):
 need ( type ( executable_fd)is int and 2<executable_fd<1048576,"PARSER_DESCRIPTOR")
 base= [ "/proc/self/fd/"+str ( executable_fd),"--config-file=/dev/null"]
 if mode=="VERSION":
  need ( profile_fd is None,"PARSER_MODE")
  return [ *base,"--version"]
 need ( mode=="COMPILE"and type ( profile_fd)is int and 2<profile_fd<1048576 and profile_fd!=executable_fd,"PARSER_MODE")
 return [ *base,"--skip-kernel-load","--skip-cache","--jobs=0","--abort-on-error","--Werror","--base=/etc/apparmor.d","/proc/self/fd/"+str ( profile_fd)]
def empty_capture ( mode):
 return { "mode":mode,"interface":"NOBLE4_FIXED_NO_LOAD_V1","configuration":"FIXED_EMPTY_DEV_NULL","process_started":False,"pidfd_acquired":False,"returncode":None,"start_errno":None,"timeout":False,"output_bound_exceeded":False,"internal_failure":True,"streams_complete":False,"stdout_bytes":0,"stdout_sha256":sha ( b""),"stderr_bytes":0,"stderr_sha256":sha ( b""),"elapsed_ms":0,"cleanup":None,"version":None}
def owned_quiescent ( utility):
 need ( utility.children ()== [],"OWNED_CHILDREN")
 try:
  os.waitpid ( -1,os.WNOHANG|0x40000000)
 except ChildProcessError:
  return
 raise Refusal ( "OWNED_ECHILD")
@contextlib.contextmanager
def profile_memory ( raw):
 need ( type ( raw)is bytes and len ( raw)==1936 and sha ( raw)==PROFILE_SHA,"PROFILE_INPUT")
 need ( all ( hasattr ( fcntl,name)for name in ( "F_SEAL_WRITE","F_SEAL_GROW","F_SEAL_SHRINK","F_SEAL_SEAL","F_ADD_SEALS","F_GET_SEALS"))and hasattr ( os,"memfd_create")and hasattr ( os,"MFD_CLOEXEC")and hasattr ( os,"MFD_ALLOW_SEALING"),"PROFILE_SEALS_UNAVAILABLE")
 fd=os.memfd_create ( "dg17-apparmor-exact-profile",os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING)
 try:
  offset=0
  while offset<len ( raw):
   count=os.write ( fd,raw [ offset:])
   need ( count>0,"PROFILE_WRITE")
   offset+=count
  os.lseek ( fd,0,os.SEEK_SET)
  seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
  fcntl.fcntl ( fd,fcntl.F_ADD_SEALS,seals)
  need ( fcntl.fcntl ( fd,fcntl.F_GET_SEALS)==seals,"PROFILE_SEALS")
  need ( read_fd ( fd,1936,time.monotonic ()+1)==raw,"PROFILE_READBACK")
  os.lseek ( fd,0,os.SEEK_SET)
  yield fd
 finally:
  os.close ( fd)
class FixedParser:
 def __init__ ( self,io,utility,receiver,context,source,profile,deadline):
  self.io,self.utility,self.receiver=io,utility,receiver
  self.context,self.source,self.profile,self.deadline=context,source,profile,deadline
 def run ( self,mode,baseline):
  result=empty_capture ( mode)
  records,started= [],time.monotonic ()
  output=b""
  try:
   current=collect_snapshot ( self.io,self.context,self.source,time.monotonic_ns ())
   self.receiver.validate_snapshot ( current,self.context,self.source)
   need ( { key:value for key,value in baseline.items ()if key!="monotonic_ns"}== { key:value for key,value in current.items ()if key!="monotonic_ns"},"PARSER_STATE_DRIFT")
   owned_quiescent ( self.utility)
   with held ( PARSER,self.deadline)as ( fd,info):
    raw=read_fd ( fd,2097152,self.deadline)
    row=present_node ( PARSER,info,raw).row
    need ( row==baseline [ "parser"],"PARSER_CUSTODY_DRIFT")
    try:
     caps=os.getxattr ( fd,"security.capability")
    except OSError as exc:
     need ( exc.errno in ( errno.ENODATA,errno.ENOTSUP),"PARSER_CAPABILITIES_UNKNOWN")
     caps=b""
    need ( caps==b"","PARSER_CAPABILITIES")
    if mode=="VERSION":
     _,output,_=self.utility.capture ( "apparmor-version",parser_argv ( mode,fd),records,self.deadline,seconds=10,fds= ( fd,))
    else:
     with profile_memory ( self.profile)as profile_fd:
      _,output,_=self.utility.capture ( "apparmor-no-load",parser_argv ( mode,fd,profile_fd),records,self.deadline,seconds=10,fds= ( fd,profile_fd))
    need ( present_node ( PARSER,os.fstat ( fd),raw).row==baseline [ "parser"],"PARSER_CUSTODY_DRIFT")
  except BaseException:
   result [ "internal_failure"]=True
  else:
   result [ "internal_failure"]=False
  if records:
   record=records [ -1]
   for key in ( "process_started","pidfd_acquired","returncode","start_errno","timeout","output_bound_exceeded","streams_complete","stdout_bytes","stdout_sha256","stderr_bytes","stderr_sha256"):
    if key in record:
     result [ key]=record [ key]
   result [ "internal_failure"]=result [ "internal_failure"]or record.get ( "internal_failure")is not None
   cleanup=record.get ( "cleanup")
   if type ( cleanup)is dict:
    fields= ( "echild","pidfd_signals","retained_status_count","retained_statuses_sha256","reaped_statuses","reaped_statuses_truncated")
    if set ( fields).issubset ( cleanup):
     result [ "cleanup"]= { key:cleanup [ key]for key in fields}
    if cleanup.get ( "code")is not None:
     result [ "internal_failure"]=True
  result [ "elapsed_ms"]=max ( 0,int ( ( time.monotonic ()-started)*1000))
  if mode=="VERSION"and not result [ "internal_failure"]:
   match=re.match ( rb"\AAppArmor parser version ([0-9]+\.[0-9]+\.[0-9]+)\n",output)
   if match and len ( match [ 1])<=32:
    result [ "version"]=match [ 1].decode ( "ascii")
  return result
def source_read ( path,bound,deadline):
 with held ( str ( path),deadline,host=False)as ( fd,info):
  need ( stat.S_ISREG ( info.st_mode)and info.st_nlink==1 and 0<info.st_size<=bound,"SOURCE_FILE")
  raw=read_fd ( fd,bound,deadline)
  need ( len ( raw)==info.st_size,"SOURCE_SIZE")
  return raw
def source_closure ( root,manifest_raw,expected_sha,deadline):
 need ( type ( expected_sha)is str and re.fullmatch ( "[0-9a-f]{64}",expected_sha)is not None and sha ( manifest_raw)==expected_sha,"INDEPENDENT_SOURCE_PIN")
 manifest=strict ( manifest_raw,16384)
 need ( type ( manifest)is dict and set ( manifest)== { "schema","files"}and manifest [ "schema"]=="dg17.apparmor.preparation-source.v1","SOURCE_MANIFEST")
 rows=manifest [ "files"]
 need ( type ( rows)is list and len ( rows)==len ( SOURCE_PATHS),"SOURCE_POPULATION")
 need ( all ( type ( row)is dict and set ( row)== { "path","bytes","sha256"}for row in rows),"SOURCE_ROW")
 need ( [ row [ "path"]for row in rows]==list ( SOURCE_PATHS),"SOURCE_PATHS")
 bodies,total= {},0
 for row in rows:
  need ( type ( row [ "bytes"])is int and 0<row [ "bytes"]<=LIMITS [ "source_limit_bytes"]and type ( row [ "sha256"])is str and re.fullmatch ( "[0-9a-f]{64}",row [ "sha256"])is not None,"SOURCE_ROW_VALUE")
  total+=row [ "bytes"]
  need ( total<=LIMITS [ "source_limit_bytes"],"SOURCE_AGGREGATE")
  raw=source_read ( root/row [ "path"],row [ "bytes"],deadline)
  need ( len ( raw)==row [ "bytes"]and sha ( raw)==row [ "sha256"],"SOURCE_BODY_PIN")
  bodies [ row [ "path"]]=raw
 need ( sha ( bodies [ UTILITY_PATH])==UTILITY_SHA,"UTILITY_PIN")
 need ( sha ( bodies [ EPISODE_PATH])==EPISODE_SHA and sha ( bodies [ PREPARER_PATH])==PREPARER_SHA,"CALLER_REUSE_PIN")
 need ( len ( bodies [ DIRECTORY+"/bwrap-userns-restrict"])==1936 and sha ( bodies [ DIRECTORY+"/bwrap-userns-restrict"])==PROFILE_SHA,"PROFILE_PIN")
 need ( len ( bodies [ DIRECTORY+"/README"])==1928 and sha ( bodies [ DIRECTORY+"/README"])==README_SHA,"README_PIN")
 source= { "manifest_sha256":expected_sha,"module_sha256":sha ( bodies [ DIRECTORY+"/admission.py"]),"receiver_sha256":sha ( bodies [ DIRECTORY+"/receiver.py"]),"utility_sha256":UTILITY_SHA,"bridge_sha256":sha ( bodies [ DIRECTORY+"/bridge.py"]),"episode_sha256":EPISODE_SHA,"preparer_sha256":PREPARER_SHA,"profile_sha256":PROFILE_SHA,"readme_sha256":README_SHA}
 return source,bodies
def loaded_module ( raw,name):
 value=types.ModuleType ( name)
 exec ( compile ( raw,name,"exec"),value.__dict__)
 return value
def environment_context ( expected):
 need ( type ( expected)is dict and set ( expected)== { "repository","branch","run_id","attempt","workflow_commit","job_name"},"CONTEXT_FIELDS")
 need ( expected [ "repository"]=="theislampill/IMPLEMENTAUDIT.md"and expected [ "branch"]=="pro/dg17-isolated-episode-01-20261106"and expected [ "job_name"]=="dg17-bounded"and type ( expected [ "attempt"])is int and expected [ "attempt"]==1 and type ( expected [ "run_id"])is str and re.fullmatch ( "[1-9][0-9]{0,18}",expected [ "run_id"])is not None and type ( expected [ "workflow_commit"])is str and re.fullmatch ( "[0-9a-f]{40}",expected [ "workflow_commit"])is not None,"CONTEXT_VALUES")
 names= { "GITHUB_ACTIONS":"true","RUNNER_ENVIRONMENT":"github-hosted","GITHUB_EVENT_NAME":"push","GITHUB_REPOSITORY":expected [ "repository"],"GITHUB_REF":"refs/heads/"+expected [ "branch"],"GITHUB_RUN_ID":expected [ "run_id"],"GITHUB_RUN_ATTEMPT":str ( expected [ "attempt"]),"GITHUB_SHA":expected [ "workflow_commit"],"GITHUB_JOB":expected [ "job_name"]}
 need ( all ( os.environ.get ( name)==value for name,value in names.items ()),"ACTUAL_CONTEXT")
 return dict ( expected)
def open_loaded_profiles ():
 need ( os.getuid ()==os.geteuid ()==0 and os.getgid ()==os.getegid ()==0,"PROFILES_ROOT_OPENER")
 duplicate=None
 try:
  with held ( LOADED,time.monotonic ()+20)as ( fd,info):
   need ( stat.S_ISREG ( info.st_mode)and info.st_nlink==1 and fcntl.fcntl ( fd,fcntl.F_GETFL)&os.O_ACCMODE==os.O_RDONLY,"PROFILES_OPENER_CUSTODY")
   duplicate=os.dup ( fd)
   os.set_inheritable ( duplicate,False)
  return duplicate
 except BaseException:
  if duplicate is not None:
   os.close ( duplicate)
  raise
class SameHostAdmission:
 def __init__ ( self,source_root,manifest_raw,expected_manifest_sha256,expected_context,loaded_profiles_fd):
  self.deadline=time.monotonic ()+20
  self.root=Path ( source_root)
  need ( self.root.is_absolute (),"SOURCE_ROOT")
  self.manifest_raw,self.manifest_sha=manifest_raw,expected_manifest_sha256
  self.source,bodies=source_closure ( self.root,manifest_raw,expected_manifest_sha256,self.deadline)
  need ( source_read ( Path ( __file__).absolute (),LIMITS [ "source_limit_bytes"],self.deadline)==bodies [ DIRECTORY+"/admission.py"],"RUNNING_MODULE_PIN")
  self.receiver=loaded_module ( bodies [ DIRECTORY+"/receiver.py"],"dg17_apparmor_receiver")
  self.utility=loaded_module ( bodies [ UTILITY_PATH],"dg17_apparmor_owned_utility")
  self.context=environment_context ( expected_context)
  self.io=PhysicalIO ( self.deadline,loaded_profiles_fd)
  self.profile=bodies [ DIRECTORY+"/bwrap-userns-restrict"]
  self.initial_host=self.io.host_binding ()
  value=ctypes.c_int ()
  libc=ctypes.CDLL ( None,use_errno=True)
  need ( libc.prctl ( 37,ctypes.byref ( value),0,0,0)==0 and value.value==1,"EXISTING_SUBREAPER_REQUIRED")
  owned_quiescent ( self.utility)
  self.observed=None
  self.used=False
  self.started=False
 def observe ( self):
  need ( not self.started and self.observed is None and not self.used and time.monotonic ()<self.deadline,"ONE_USE_OPERATION")
  self.started=True
  environment_context ( self.context)
  before=collect_snapshot ( self.io,self.context,self.source,time.monotonic_ns ())
  need ( before [ "host"]==self.initial_host,"INITIAL_HOST_DRIFT")
  parser=FixedParser ( self.io,self.utility,self.receiver,self.context,self.source,self.profile,self.deadline)
  version=empty_capture ( "VERSION")
  compile_capture=empty_capture ( "COMPILE")
  try:
   self.receiver.validate_snapshot ( before,self.context,self.source)
  except self.receiver.Refusal:
   pass
  else:
   version=parser.run ( "VERSION",before)
  try:
   self.receiver.validate_capture ( version,"VERSION")
  except self.receiver.Refusal:
   pass
  else:
   compile_capture=parser.run ( "COMPILE",before)
  after=collect_snapshot ( self.io,self.context,self.source,time.monotonic_ns ())
  source_after,_=source_closure ( self.root,self.manifest_raw,self.manifest_sha,self.deadline)
  need ( self.source==source_after,"SOURCE_DRIFT")
  environment_context ( self.context)
  result= { "schema":"dg17.apparmor.same-host.observation.v1","candidate_identity":IDENTITY,"context":self.context,"source":self.source,"limits":LIMITS,"before":before,"after":after,"version_capture":version,"compile_capture":compile_capture,"authority":"NONE","original14":"REQUIRED_UNMET_UNWAIVED_UNRETIRED","original_awards": [],"native_execution":False,"security_policy_changed":False,"model_inference":False,"original_acceptance":False,"adoption":False}
  raw=encoded ( result)
  need ( len ( raw)<=LIMITS [ "public_result_limit_bytes"],"PUBLIC_BOUND")
  self.observed=raw
  return raw
 def receive_current ( self,raw):
  need ( self.observed is not None and not self.used and type ( raw)is bytes and raw==self.observed,"OWNED_OBSERVATION_REQUIRED")
  self.used=True
  need ( time.monotonic ()<self.deadline,"OWNED_OPERATION_EXPIRED")
  environment_context ( self.context)
  source,_=source_closure ( self.root,self.manifest_raw,self.manifest_sha,self.deadline)
  current=collect_snapshot ( self.io,self.context,source,time.monotonic_ns ())
  self.receiver.validate_snapshot ( current,self.context,self.source)
  prior=strict ( raw,LIMITS [ "public_result_limit_bytes"]) [ "after"]
  need ( { key:value for key,value in prior.items ()if key!="monotonic_ns"}== { key:value for key,value in current.items ()if key!="monotonic_ns"},"LIVE_STATE_DRIFT")
  owned_quiescent ( self.utility)
  return self.receiver.receive_record ( raw,self.context,self.source,current [ "host"],time.monotonic_ns ())
