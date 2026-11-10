import hashlib
import json
import re
import stat
CANDIDATE="dg17-9077-codex20-apparmor-preparation05"
ORIGINAL14="REQUIRED_UNMET_UNWAIVED_UNRETIRED"
LIMITS= { "source_limit_bytes":4194304,"public_result_limit_bytes":65536,"outer_stream_limit_bytes":32768,"stderr_limit_bytes":65536,"outer_timeout_seconds":30,"root_watchdog_seconds":20,"root_kill_after_seconds":5,"owned_cleanup_seconds":4,"owned_live_child_limit":8,"parser_timeout_ms":10000,"freshness_ms":5000,"include_nodes":32,"include_edges":64,"include_bytes":262144,"feature_nodes":256,"feature_bytes":65536,"feature_depth":8,"model_calls":0,"helper_attempt_limit":0,}
PROFILE_SHA="11d39094f044f0cda0febb3ad517b830301da6b2ce929664af09ee9e4dd264f9"
SOURCE_FIXED= { "utility_sha256":"429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c","profile_sha256":PROFILE_SHA,"readme_sha256":"4fe5017b356227ddc57ddcb489e75e6437c6e2d2972c0a8545af437734124c83","episode_sha256":"4dc7aacb793e1d65ed1fa51335800fbfaa7c9af777369877f2828113006a8466","preparer_sha256":"03afcc3f26311249459d019d15dd55fd835e99b9cc2b6f3ff9f748cf44436488",}
SOURCE_FIELDS=set ( SOURCE_FIXED)| { "manifest_sha256","module_sha256","receiver_sha256","bridge_sha256"}
CONTEXT_FIELDS= { "repository","branch","run_id","attempt","workflow_commit","job_name"}
HOST_FIELDS= { "boot_id_sha256","kernel_release_sha256","kernel_version_sha256","machine","uid","gid","pid","process_start_ticks","mount_namespace_sha256","user_namespace_sha256","lsm_label_sha256"}
ROW_FIELDS= { "path","state","kind","bytes","sha256","custody_sha256","mode","uid","gid","nlink","errno"}
ROOTS= { "/etc/apparmor.d/tunables/global","/etc/apparmor.d/local/bwrap-userns-restrict","/etc/apparmor.d/local/unpriv_bwrap"}
TUNABLES="/etc/apparmor.d/tunables/"
class Refusal ( ValueError):
 pass
def _require ( condition,code):
 if not condition:
  raise Refusal ( code)
def _keys ( value,fields,code):
 _require ( type ( value)is dict and set ( value)==fields,code)
def _int ( value,low,high,code):
 _require ( type ( value)is int and low<=value<=high,code)
def _sha ( value,code):
 _require ( type ( value)is str and re.fullmatch ( r"[0-9a-f]{64}",value)is not None,code)
def _encoded ( value):
 return ( json.dumps ( value,sort_keys=True,separators= ( ",",":"),ensure_ascii=True,allow_nan=False)+"\n").encode ( "ascii")
def _digest ( raw):
 return hashlib.sha256 ( raw).hexdigest ()
EMPTY_SHA=_digest ( b"")
def _context ( value):
 code="CONTEXT_BINDING"
 _keys ( value,CONTEXT_FIELDS,code)
 _require ( value [ "repository"]=="theislampill/IMPLEMENTAUDIT.md"and value [ "branch"]=="pro/dg17-isolated-episode-01-20261106"and value [ "job_name"]=="dg17-bounded",code)
 _int ( value [ "attempt"],1,1,code)
 _require ( type ( value [ "run_id"])is str and re.fullmatch ( r"[1-9][0-9]{0,18}",value [ "run_id"])is not None,code)
 _require ( type ( value [ "workflow_commit"])is str and re.fullmatch ( r"[0-9a-f]{40}",value [ "workflow_commit"])is not None,code)
def _source ( value):
 _keys ( value,SOURCE_FIELDS,"SOURCE_BINDING")
 for item in value.values ():
  _sha ( item,"SOURCE_BINDING")
 _require ( all ( value [ key]==expected for key,expected in SOURCE_FIXED.items ()),"SOURCE_BINDING")
def _host ( value):
 code="CURRENT_HOST_MISMATCH"
 _keys ( value,HOST_FIELDS,code)
 for key in HOST_FIELDS:
  if key.endswith ( "_sha256"):
   _sha ( value [ key],code)
 _require ( value [ "machine"]=="x86_64"and value [ "lsm_label_sha256"]==_digest ( b"unconfined\n"),code)
 for key in ( "uid","gid"):
  _int ( value [ key],1,4294967294,code)
 _int ( value [ "pid"],1,2147483647,code)
 _int ( value [ "process_start_ticks"],1,9223372036854775807,code)
def _row ( value,path,code,kinds= ( "FILE",),absent=False,executable=False,bound=65536):
 _keys ( value,ROW_FIELDS,code)
 _require ( type ( value [ "path"])is str and value [ "path"]==path,code)
 _require ( type ( value [ "state"])is str and value [ "state"]in { "PRESENT","ABSENT","UNKNOWN","INVALID"},code)
 _int ( value [ "bytes"],0,bound,code)
 if value [ "state"]!="PRESENT":
  _require ( value [ "bytes"]==0 and all ( value [ key]is None for key in ( "kind","sha256","mode","uid","gid","nlink")),code)
  _int ( value [ "errno"],1,4095,code)
  _require ( absent and value [ "state"]=="ABSENT"and value [ "errno"]==2,code)
  _sha ( value [ "custody_sha256"],code)
  return
 _require ( type ( value [ "kind"])is str and value [ "kind"]in kinds and value [ "errno"]is None,code)
 _sha ( value [ "sha256"],code)
 _sha ( value [ "custody_sha256"],code)
 _int ( value [ "mode"],0,65535,code)
 _int ( value [ "uid"],0,0,code)
 _int ( value [ "gid"],0,0,code)
 _int ( value [ "nlink"],1,4096,code)
 expected_type= { "FILE":stat.S_IFREG,"DIRECTORY":stat.S_IFDIR,"CHAR":stat.S_IFCHR} [ value [ "kind"]]
 _require ( stat.S_IFMT ( value [ "mode"])==expected_type and not value [ "mode"]&0o7000,code)
 if value [ "kind"]=="CHAR":
  _require ( path=="/dev/null"and value [ "mode"]==stat.S_IFCHR|0o666 and value [ "nlink"]==1,code)
 else:
  _require ( not value [ "mode"]&0o022,code)
  if value [ "kind"]=="FILE":
   _require ( value [ "nlink"]==1,code)
 if executable:
  _require ( value [ "mode"]&0o111==0o111,code)
def _include_path ( path):
 if type ( path)is not str or len ( path)>512:
  return False
 if path in ROOTS:
  return True
 if not path.startswith ( TUNABLES):
  return False
 parts=path [ len ( TUNABLES):].split ( "/")
 return len ( parts)<=7 and all ( re.fullmatch ( r"[A-Za-z0-9_+-][A-Za-z0-9_.+-]{0,79}",part)is not None for part in parts)
def _includes ( value):
 code="INCLUDE_CLOSURE"
 _keys ( value, { "state","code","nodes","edges","sha256"},code)
 _require ( value [ "state"]=="COMPLETE"and value [ "code"]is None,code)
 nodes,edges=value [ "nodes"],value [ "edges"]
 _require ( type ( nodes)is list and 3<=len ( nodes)<=32,code)
 _require ( type ( edges)is list and len ( edges)<=64,code)
 rows= {}
 total=0
 for node in nodes:
  _keys ( node,ROW_FIELDS,code)
  path=node [ "path"]
  _require ( _include_path ( path)and path not in rows,code)
  _row ( node,path,code,kinds= ( "FILE","DIRECTORY"),absent=True)
  if path in ROOTS:
   _require ( node [ "kind"]in ( "FILE",None),code)
  rows [ path]=node
  total+=node [ "bytes"]
 _require ( list ( rows)==sorted ( rows)and ROOTS<=set ( rows)and total<=262144,code)
 _require ( rows [ TUNABLES+"global"] [ "state"]=="PRESENT",code)
 links= { path: []for path in rows}
 incoming= { path: []for path in rows}
 encodings= []
 for edge in edges:
  _keys ( edge, { "from","to","optional","kind"},code)
  start,end=edge [ "from"],edge [ "to"]
  _require ( type ( start)is str and type ( end)is str and start in rows and end in rows,code)
  _require ( type ( edge [ "optional"])is bool and type ( edge [ "kind"])is str and edge [ "kind"]in { "INCLUDE","MEMBER"},code)
  _require ( start.startswith ( TUNABLES)and end.startswith ( TUNABLES)and rows [ start] [ "state"]=="PRESENT",code)
  if edge [ "kind"]=="MEMBER":
   _require ( rows [ start] [ "kind"]=="DIRECTORY"and edge [ "optional"]is False and end.rsplit ( "/",1) [ 0]==start,code)
  else:
   _require ( rows [ start] [ "kind"]=="FILE",code)
  _require ( rows [ end] [ "state"]=="PRESENT"or edge [ "optional"],code)
  links [ start].append ( end)
  incoming [ end].append ( edge)
  encodings.append ( _encoded ( edge))
 _require ( encodings==sorted ( set ( encodings)),code)
 for path,node in rows.items ():
  if node [ "kind"]=="DIRECTORY":
   listing=_encoded ( sorted ( child.rsplit ( "/",1) [ 1]for child in links [ path]))
   _require ( node [ "bytes"]==len ( listing)and node [ "sha256"]==_digest ( listing),code)
  if node [ "state"]=="ABSENT"and path not in ROOTS:
   _require ( incoming [ path]and all ( edge [ "optional"]for edge in incoming [ path]),code)
 heights= {}
 def walk ( path,active):
  _require ( path not in active,code)
  if path not in heights:
   heights [ path]=max ( ( walk ( child,active| { path})+1 for child in links [ path]),default=0)
   _require ( heights [ path]<=8,code)
  return heights [ path]
 for root in sorted ( ROOTS):
  walk ( root,set ())
 _require ( set ( heights)==set ( rows),code)
 _sha ( value [ "sha256"],code)
 _require ( value [ "sha256"]==_digest ( _encoded ( { "nodes":nodes,"edges":edges})),code)
def _features ( value):
 code="FEATURE_STATE"
 _keys ( value, { "state","code","node_count","total_bytes","sha256","root_custody_sha256"},code)
 _require ( value [ "state"]=="COMPLETE"and value [ "code"]is None,code)
 _int ( value [ "node_count"],1,256,code)
 _int ( value [ "total_bytes"],0,65536,code)
 _sha ( value [ "sha256"],code)
 _sha ( value [ "root_custody_sha256"],code)
def _loaded ( value):
 code="LOADED_STATE_UNRESOLVED"
 _keys ( value, { "state","code","bytes","sha256","relevant","attachment_coverage","custody","read_interface"},code)
 _require ( value [ "state"]=="OBSERVED"and value [ "code"]is None and value [ "attachment_coverage"]=="UNOBSERVED",code)
 _require ( value [ "read_interface"]=="INHERITED_READONLY_FIXED_PROFILES_FD_V1",code)
 _int ( value [ "bytes"],0,65536,code)
 _sha ( value [ "sha256"],code)
 _row ( value [ "custody"],"/sys/kernel/security/apparmor/profiles",code)
 _require ( value [ "bytes"]==value [ "custody"] [ "bytes"]and value [ "sha256"]==value [ "custody"] [ "sha256"],code)
 _require ( type ( value [ "relevant"])is list and len ( value [ "relevant"])<=8,code)
 for item in value [ "relevant"]:
  _keys ( item, { "name","mode"},code)
  _require ( type ( item [ "name"])is str and item [ "name"]in { "BWRAP","UNPRIV_BWRAP","BWRAP_ATTACHMENT_NAME","BWRAP_STACK"},code)
  _require ( type ( item [ "mode"])is str and item [ "mode"]in { "enforce","complain","kill","unconfined"},code)
 _require ( not value [ "relevant"],"LOADED_PROFILE_CONFLICT")
def validate_snapshot ( snapshot,expected_context,expected_source):
 _context ( expected_context)
 _source ( expected_source)
 _keys ( snapshot, { "schema","candidate_identity","context","source","monotonic_ns","host","confinement","helper","parser","null_config","abi","installed_profile","installed_extra","includes","features","loaded","apparmor_enabled"},"SNAPSHOT_FIELDS")
 _require ( snapshot [ "schema"]=="dg17.apparmor.same-host.snapshot.v1"and snapshot [ "candidate_identity"]==CANDIDATE,"SNAPSHOT_FIELDS")
 _context ( snapshot [ "context"])
 _source ( snapshot [ "source"])
 _require ( snapshot [ "context"]==expected_context,"CONTEXT_BINDING")
 _require ( snapshot [ "source"]==expected_source,"SOURCE_BINDING")
 _int ( snapshot [ "monotonic_ns"],0,9223372036854775807,"FRESHNESS")
 _host ( snapshot [ "host"])
 confinement=snapshot [ "confinement"]
 _keys ( confinement, { "no_new_privs","cap_inh","cap_prm","cap_eff","cap_bnd","cap_amb"},"CONFINEMENT")
 for key,val in confinement.items ():
  required=1 if key=="no_new_privs"else 0
  _int ( val,required,required,"CONFINEMENT")
 helper=snapshot [ "helper"]
 _row ( helper,"/usr/bin/bwrap","HELPER_IDENTITY",executable=True,bound=72160)
 _require ( helper [ "bytes"]==72160 and helper [ "sha256"]=="e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71","HELPER_IDENTITY")
 _row ( snapshot [ "parser"],"/usr/sbin/apparmor_parser","PARSER_CUSTODY",executable=True,bound=2097152)
 _require ( snapshot [ "parser"] [ "bytes"]>=64,"PARSER_CUSTODY")
 _row ( snapshot [ "null_config"],"/dev/null","NULL_CONFIG",kinds= ( "CHAR",),bound=3)
 _require ( snapshot [ "null_config"] [ "bytes"]==3 and snapshot [ "null_config"] [ "sha256"]==_digest ( b"1:3"),"NULL_CONFIG")
 _row ( snapshot [ "abi"],"/etc/apparmor.d/abi/4.0","ABI_STATE")
 _require ( snapshot [ "abi"] [ "bytes"]>0,"ABI_STATE")
 for key,path in ( ( "installed_profile","/etc/apparmor.d/bwrap-userns-restrict"), ( "installed_extra","/usr/share/apparmor/extra-profiles/bwrap-userns-restrict")):
  row=snapshot [ key]
  _row ( row,path,"INSTALLED_PROFILE_CONFLICT",absent=True)
  _require ( row [ "state"]=="ABSENT"or ( row [ "bytes"]==1936 and row [ "sha256"]==PROFILE_SHA),"INSTALLED_PROFILE_CONFLICT")
 _includes ( snapshot [ "includes"])
 _features ( snapshot [ "features"])
 _loaded ( snapshot [ "loaded"])
 enabled=snapshot [ "apparmor_enabled"]
 _row ( enabled,"/sys/module/apparmor/parameters/enabled","APPARMOR_DISABLED",bound=2)
 _require ( ( enabled [ "bytes"],enabled [ "sha256"])in { ( 1,_digest ( b"Y")), ( 2,_digest ( b"Y\n"))},"APPARMOR_DISABLED")
def _cleanup ( value):
 code="PARSER_CLEANUP"
 _keys ( value, { "echild","pidfd_signals","retained_status_count","retained_statuses_sha256","reaped_statuses","reaped_statuses_truncated"},code)
 _require ( value [ "echild"]is True and type ( value [ "reaped_statuses_truncated"])is bool,code)
 _int ( value [ "pidfd_signals"],0,4096,code)
 _require ( value [ "pidfd_signals"]==0,code)
 _int ( value [ "retained_status_count"],0,4096,code)
 _sha ( value [ "retained_statuses_sha256"],code)
 sample=value [ "reaped_statuses"]
 _require ( type ( sample)is list and len ( sample)<=8,code)
 pids=set ()
 for row in sample:
  _keys ( row, { "pid","returncode"},code)
  _int ( row [ "pid"],1,2147483647,code)
  _int ( row [ "returncode"],-64,255,code)
  _require ( row [ "pid"]not in pids,code)
  pids.add ( row [ "pid"])
 count=value [ "retained_status_count"]
 _require ( len ( sample)==min ( count,8)and value [ "reaped_statuses_truncated"]is ( count>8),code)
 if count<=8:
  body= ( json.dumps ( sample,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+"\n").encode ( "ascii")
  _require ( value [ "retained_statuses_sha256"]==_digest ( body),code)
def validate_capture ( value,mode):
 _require ( mode in ( "VERSION","COMPILE"),"PARSER_INTERFACE")
 _keys ( value, { "mode","interface","configuration","process_started","pidfd_acquired","returncode","start_errno","timeout","output_bound_exceeded","internal_failure","streams_complete","stdout_bytes","stdout_sha256","stderr_bytes","stderr_sha256","elapsed_ms","cleanup","version"},"PARSER_CAPTURE")
 _require ( value [ "mode"]==mode and value [ "interface"]=="NOBLE4_FIXED_NO_LOAD_V1"and value [ "configuration"]=="FIXED_EMPTY_DEV_NULL","PARSER_INTERFACE")
 for key in ( "process_started","pidfd_acquired","streams_complete"):
  _require ( value [ key]is True,"PARSER_CAPTURE")
 for key in ( "timeout","output_bound_exceeded","internal_failure"):
  _require ( value [ key]is False,"PARSER_CAPTURE")
 _int ( value [ "returncode"],0,0,"PARSER_CAPTURE")
 _require ( value [ "start_errno"]is None,"PARSER_CAPTURE")
 _int ( value [ "stdout_bytes"],0,32768,"PARSER_STREAM_BOUND")
 _int ( value [ "stderr_bytes"],0,65536,"PARSER_STREAM_BOUND")
 _sha ( value [ "stdout_sha256"],"PARSER_CAPTURE")
 _sha ( value [ "stderr_sha256"],"PARSER_CAPTURE")
 _int ( value [ "elapsed_ms"],0,10000,"PARSER_TIME_BOUND")
 _cleanup ( value [ "cleanup"])
 _require ( value [ "stderr_bytes"]==0 and value [ "stderr_sha256"]==EMPTY_SHA,"PARSER_CAPTURE")
 if mode=="VERSION":
  _require ( value [ "version"]=="4.0.1"and value [ "stdout_bytes"]>0 and value [ "stdout_sha256"]!=EMPTY_SHA,"PARSER_VERSION")
 else:
  _require ( value [ "version"]is None,"PARSER_VERSION")
  _require ( value [ "stdout_bytes"]==0 and value [ "stdout_sha256"]==EMPTY_SHA,"PARSER_CAPTURE")
def _object ( pairs):
 result= {}
 for key,value in pairs:
  _require ( key not in result,"RECORD_JSON")
  result [ key]=value
 return result
def _constant ( _value):
 raise Refusal ( "RECORD_JSON")
def receive_record ( raw,expected_context,expected_source,current_host,now_ns):
 _require ( type ( raw)is bytes and 1<=len ( raw)<=65536,"RECORD_SIZE")
 try:
  record=json.loads ( raw.decode ( "ascii"),object_pairs_hook=_object,parse_constant=_constant)
  _require ( _encoded ( record)==raw,"RECORD_CANONICAL")
 except ( UnicodeError,ValueError,TypeError,OverflowError,RecursionError)as error:
  if isinstance ( error,Refusal):
   raise
  raise Refusal ( "RECORD_JSON")from None
 _keys ( record, { "schema","candidate_identity","context","source","limits","before","after","version_capture","compile_capture","authority","original14","original_awards","native_execution","security_policy_changed","model_inference","original_acceptance","adoption"},"RECORD_FIELDS")
 _require ( record [ "schema"]=="dg17.apparmor.same-host.observation.v1"and record [ "candidate_identity"]==CANDIDATE,"RECORD_FIELDS")
 _context ( expected_context)
 _source ( expected_source)
 _context ( record [ "context"])
 _source ( record [ "source"])
 _require ( record [ "context"]==expected_context,"CONTEXT_BINDING")
 _require ( record [ "source"]==expected_source,"SOURCE_BINDING")
 _keys ( record [ "limits"],set ( LIMITS),"LIMITS_BINDING")
 for key,bound in LIMITS.items ():
  _int ( record [ "limits"] [ key],bound,bound,"LIMITS_BINDING")
 _require ( record [ "authority"]=="NONE"and record [ "original14"]==ORIGINAL14 and type ( record [ "original_awards"])is list and not record [ "original_awards"],"AUTHORITY_CLAIM")
 for key in ( "native_execution","security_policy_changed","model_inference","original_acceptance","adoption"):
  _require ( record [ key]is False,"AUTHORITY_CLAIM")
 before,after=record [ "before"],record [ "after"]
 validate_snapshot ( before,expected_context,expected_source)
 validate_snapshot ( after,expected_context,expected_source)
 validate_capture ( record [ "version_capture"],"VERSION")
 validate_capture ( record [ "compile_capture"],"COMPILE")
 _int ( now_ns,0,9223372036854775807,"FRESHNESS")
 start,end=before [ "monotonic_ns"],after [ "monotonic_ns"]
 elapsed=record [ "version_capture"] [ "elapsed_ms"]+record [ "compile_capture"] [ "elapsed_ms"]
 _require ( start<=end<=now_ns and end-start<=20000000000 and now_ns-end<=5000000000 and elapsed*1000000<=end-start,"FRESHNESS")
 _require ( { key:val for key,val in before.items ()if key!="monotonic_ns"}== { key:val for key,val in after.items ()if key!="monotonic_ns"},"STATE_DRIFT")
 _host ( current_host)
 _require ( current_host==after [ "host"],"CURRENT_HOST_MISMATCH")
 return { "schema":"dg17.apparmor.same-host.receipt.v1","candidate_identity":CANDIDATE,"status":"RECEIVED_SAME_HOST_NO_LOAD_OBSERVATION","authority":"NONE","original14":ORIGINAL14,"observation_sha256":_digest ( raw),"context":dict ( expected_context),"source":dict ( expected_source),"host":dict ( current_host),"observed_from_ns":start,"observed_to_ns":end,"received_at_ns":now_ns,"original_awards": [],"security_policy_changed":False,"native_execution":False,"model_inference":False,"original_acceptance":False,"substantive_acceptance":False,"whole_cell_acceptance":False,"adoption":False,"limitations": [ "SOURCE_ONLY_WITHOUT_CUSTODY_OR_ACTIVATION_AUTHORITY","NOT_TRANSFERABLE_OR_FUTURE_READINESS","EXCLUSIVE_APPARMOR_NAMESPACE_OWNERSHIP_UNPROVED","LOADED_ATTACHMENT_COVERAGE_UNOBSERVED"],}
