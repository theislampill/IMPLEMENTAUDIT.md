"""Root-invoked G1 event configuration/issuance. No provider or host APIs.

The issue-* commands are future actual Root acts, not author authority. Inspect
and pure constructors issue nothing. G3 semantic decisions are exact externally
authenticated input files and are never inferred or synthesized here.
"""
import argparse,hashlib,json,os,re,stat,sys,time,types
from pathlib import Path,PurePosixPath

ISSUER='01a1953f-a15b-7811-aa72-3538ebb03562'
ROOT=PurePosixPath('/home/agent/dg16-g1-current04-operators/public-receiver-02')
ROLE_PATH='/home/agent/dg16-g1-current04-operators/framed-role-02/role_process_v4.py'
CONTROL_PATH='/home/agent/dg16-g1-current04-operators/framed-role-02/control_process_v3.py'
RECEIVER_SHA='378846f9cfd5f60ce3e3b48adb3c2e3c7cf94a701ed9aee46e5ba3072f4fc122'
RESOLVER_SHA='b2ac1130149d9878a3a00c7d8ba214743920a1aede38cb6b75699e14a2d03530'
ROLE_SHA='cd9e9f34a8e1897b9adccb3bdc98ab0ee62fe1ce7099d50af32d9c940cd606a0'
CONTROL_SHA='c381d6faa55513ee1a3e368ec9f5d7c2867e704ca0b2ab0dae18187b36ba8f43'
CALLBACK_SHA='94e1f736a251f61f5817750d4ae571c8328fc769ec6f760055c7bc0240a340bb'
WINDOWS_IO_SHA='0bfbe734edcf52a59fc9f4ceb0acbeda2b15991a9ca000def8a28bea3a5c1106'
PROVIDER_SLOTS_SHA='3b92c9b555823fc6853d324f018e6e62eb39908160df0de677f9a7c5021a5fc0'
WORKFLOW_COMMIT='f9ba187e8f5520956f0f16cf13c0a706e8360b96'
PHASES=('tools','recipient','g3_initial','g3_final','terminal','failure')

def need(v,c):
 if not v:raise ValueError(c)
def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return {'bytes':len(b),'sha256':sha(b)}
def parse(b):
 def pairs(rows):
  d={}
  for k,v in rows:need(k not in d,'DUPLICATE_JSON_KEY');d[k]=v
  return d
 return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE_JSON'))
def read(path,maximum):
 p=Path(path);need(p.is_absolute() and p.resolve(strict=True)==p,'CANONICAL_INPUT_PATH')
 for a in p.parents:need(not a.is_symlink(),'INPUT_ANCESTOR_ALIAS')
 s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and 0<s.st_size<=maximum,'BOUNDED_INPUT_FILE')
 fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0)|getattr(os,'O_CLOEXEC',0)|getattr(os,'O_BINARY',0))
 try:
  mark=lambda v:(v.st_dev,v.st_ino,v.st_mode,v.st_nlink,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
  need(mark(os.fstat(fd))==mark(s),'INPUT_OPEN_CHANGED');raw=b''
  while len(raw)<=maximum:
   b=os.read(fd,min(65536,maximum+1-len(raw)))
   if not b:break
   raw+=b
  need(len(raw)==s.st_size and mark(s)==mark(os.fstat(fd))==mark(p.lstat()),'INPUT_CLOSING_CHANGED');return raw
 finally:os.close(fd)
def bound(row,maximum):
 need(type(row) is dict and set(row)=={'path','sha256'} and re.fullmatch('[0-9a-f]{64}',row['sha256']),'EXACT_INPUT_DESCRIPTOR')
 b=read(row['path'],maximum);need(sha(b)==row['sha256'],'BOUND_INPUT_CHANGED');return b
def module_at(path,pin):
 b=read(path,1024**2);need(sha(b)==pin,'FIXED_SOURCE_PIN');m=types.ModuleType('root_event_'+Path(path).stem);m.__file__=str(path);exec(compile(b,str(path),'exec'),m.__dict__);return m
def receiver():return module_at(ROOT/'author/receiver.py',RECEIVER_SHA)
def context(R,s,c):
 s.context(c);need(set(c)=={'repository','branch','workflow_commit','workflow_path','run_id','run_attempt','job_name'} and c['workflow_commit']==WORKFLOW_COMMIT and c['branch']=='pro/dg16-g1-original-g3-04-20261109' and c['run_attempt']==1 and type(c['run_attempt']) is int,'EXACT_APPROVED_F9BA_EVENT')
def deadline(now,opened,ends):
 need(all(type(x) is int for x in (now,opened,ends)) and opened<=now<ends<=opened+600000,'EXISTING_EVENT_WINDOW_NO_RESET')
def inside(path,parent):
 p=PurePosixPath(path);need(p.is_absolute() and '..' not in p.parts and p.is_relative_to(parent),'FIXED_EVENT_OUTPUT');return p
def selection(kind,configuration_path,configuration_raw,shell_title):
 need(type(shell_title) is str and len(shell_title)<=512 and not re.search('[\r\n\0\x07\x1b]',shell_title),'ACTUAL_RECEIVED_SHELL_TITLE')
 return dict(distribution='Ubuntu',user='agent',python='/usr/bin/python3',rolePath=ROLE_PATH if kind=='role' else CONTROL_PATH,
  roleSha256=ROLE_SHA if kind=='role' else CONTROL_SHA,configurationPath=str(configuration_path),configurationSha256=sha(configuration_raw),shellTitle=shell_title)
def role_documents(R,s,phase,c,opened,ends,out,shell_title,now,initial_session=None,actual_root_decision=None):
 """Pure exact role_v4 constructors; returned bytes are not actual issuance."""
 context(R,s,c);need(phase in PHASES,'PUBLIC_ROLE_ONLY');deadline(now,opened,ends);out=inside(out,ROOT/'event-configurations')
 if phase=='g3_final':need(initial_session is not None and actual_root_decision is not None,'FINAL_INITIAL_ROOT_INPUTS_REQUIRED')
 else:need(initial_session is None and actual_root_decision is None,'NO_UNRELATED_INITIAL_ROOT_INPUTS')
 if initial_session is not None:inside(initial_session,ROOT/'sessions')
 ctx=encode(c);need(len(ctx)<=16384,'CONTEXT_SIZE');context_row={'path':str(out/'CONTEXT.json'),'sha256':sha(ctx)}
 session=str(ROOT/'sessions'/out.name)
 grant=dict(schema='dg16.g1-framed-role-admission.v1',issuer_thread=ISSUER,status='ADMIT_ONE_ROOT_FRAMED_ARTIFACT_ROLE',profile='ONE_PINNED_G1_FRAMED_TTY_ROLE_V1',phase=phase,context=context_row,session_directory=session,deadline_unix_ms=ends,receiver_sha256=RECEIVER_SHA,resolver_sha256=RESOLVER_SHA,automatic_retry=False,original_awards=[])
 admission=encode(grant)
 config=dict(schema='dg16.g1-framed-role-configuration.v1',issuer_thread=ISSUER,phase=phase,context=context_row,session_directory=session,deadline_unix_ms=ends,admission={'path':str(out/'ROLE_ADMISSION.json'),'sha256':sha(admission)},initial_session=initial_session,actual_root_decision=actual_root_decision)
 raw=encode(config);need(len(raw)<=65536 and len(admission)<=65536,'ROLE_CONFIGURATION_SIZE')
 return {'CONTEXT.json':ctx,'ROLE_ADMISSION.json':admission,'ROLE_CONFIGURATION.json':raw,
  'WINDOWS_SELECTION.json':encode(selection('role',out/'ROLE_CONFIGURATION.json',raw,shell_title))}
def provider_check(R,s,c,phase,value,now,opened,ends):
 need(type(value) is dict and set(value)=={'schema','context','observed_unix_ms','results','authentication_receiving'} and value['schema']=='dg16.g1-root-provider-readback-inputs.v1' and value['context']==c,'EXACT_PROVIDER_READBACK_INPUTS')
 need(type(value['observed_unix_ms']) is int and opened<=value['observed_unix_ms']<=now<ends,'PROVIDER_CURRENT_EVENT_CUTOFF')
 need(set(value['results'])=={'run','attempt','jobs','workflow'},'FOUR_COMPLETE_PROVIDER_RESULTS')
 # External Root owns native provenance. Retain a body-checked descriptor to
 # that actual safe receiving record, never assert authentication from labels.
 provenance=bound(value['authentication_receiving'],65536);need(provenance,'ACTUAL_PROVIDER_RECEIVING_BODY')
 snapshot={};pins={}
 for kind,row in value['results'].items():
  raw=bound(row,R.MAX_RESULT);_,snapshot[kind]=s.B.unwrap_tool_result(raw,s.endpoint(c,1,kind),kind=kind,context=c,workflow_sha256=s.binding['workflow_sha256'],artifact_id=1);pins[kind]=desc(raw)
 statuses=('in_progress','completed') if phase in ('terminal','failure') else ('in_progress',)
 facts,_=R.execution_join(s,snapshot,c,now,statuses)
 return dict(provider_facts=facts,full_results=pins,authentication_receiving=desc(provenance),source_authentication='ACTUAL_ROOT_NATIVE_PROVENANCE_REQUIRED_EXTERNALLY')
def received_session(R,s,path,previous=None,actual_root_raw=None):
 inside(path,ROOT/'sessions');session=R.Session(Path(path),s);saved=R.parse(R.read(session.path/'RECEIVING.json'))
 got=session.receive(saved['observed_unix_ms'],previous=previous,save=False,actual_root_raw=actual_root_raw)
 need(R.encode(got['receipt'])==R.encode(saved),'SAVED_ACTUAL_RECEIVING_CHANGED');return got
def tools_decision(R,s,got,issued,expires,now):
 """Only actual Root supplies issuance/expiry; no G3 judgments are generated."""
 context(R,s,got['context']);need(got['phase']=='tools' and all(type(x) is int for x in (issued,expires,now)),'ACTUAL_TOOLS_RECEIVING_AND_ISSUANCE')
 req=R.requirements(s,got);need(req['root_supplied_fields']==['issued_unix_ms','expires_unix_ms'],'EXACT_TOOLS_ROOT_FIELDS')
 body=R.encode(dict(req['required_fixed_fields'],issued_unix_ms=issued,expires_unix_ms=expires))
 R.validate_control(s,got,body,now);need(len(body)<=16384,'TOOLS_BODY_DRIVER_BOUND');return body
def control_documents(R,s,got,body,parent_sha,parent_raw,opened,ends,out,shell_title,now,
                      artifact_session,initial_session=None,initial_body_row=None,initial_publication_row=None,initial_control=None):
 """Pure exact control_v3/FINAL_CALLBACK_HANDOFF construction; no root judgment."""
 context(R,s,got['context']);deadline(now,opened,ends);need(got['phase'] in ('tools','g3_initial','g3_final'),'CONTROL_PHASE_ONLY')
 out=inside(out,ROOT/'event-configurations');inside(artifact_session,ROOT/'sessions')
 need(len(body)<=16384 and re.fullmatch('[0-9a-f]{40}',parent_sha),'BODY_AND_CURRENT_PARENT')
 R.validate_control(s,got,body,now)
 request=got['receipt']['details']['request'] if got['phase'].startswith('g3_') else None
 if request is not None:need(ends<=request['expires_unix_ms'],'NO_G3_WINDOW_EXTENSION')
 else:need(ends<=parse(body)['expires_unix_ms'],'NO_TOOLS_ADOPTION_WINDOW_EXTENSION')
 plan=R.publication_plan(s,got,body,parent_sha,now,initial_control)
 call=R.control_read_plan(plan,'0'*40)[0]
 parent=R.unwrap_control(parent_raw,call['arguments']['url'])
 need(parent.get('ref')=='refs/heads/'+plan['branch'] and parent.get('object',{}).get('type')=='commit' and parent['object']['sha']==parent_sha,'ACTUAL_CURRENT_PARENT_REF')
 if got['phase']=='g3_final':need(initial_control is not None and initial_session is not None and initial_body_row is not None and initial_publication_row is not None,'ACTUAL_INITIAL_PUBLISHED_CONTROL_REQUIRED')
 else:need(all(v is None for v in (initial_control,initial_session,initial_body_row,initial_publication_row)),'NO_UNRELATED_INITIAL_CONTROL')
 body_row={'path':str(out/'DECISION.json'),'sha256':sha(body)};parent_row={'path':str(out/'PARENT_REF_RESULT.json'),'sha256':sha(parent_raw)}
 journal=str(ROOT/'control-sessions'/out.name)
 grant=dict(schema='dg16.g1-root-control-publication-admission.v1',issuer_thread=ISSUER,status='ADMIT_EXACT_THREE_GUARDED_CONTROL_WRITES_AND_READBACK',phase=got['phase'],context=got['context'],body=body_row,artifact_receiving=R.desc(R.encode(got['receipt'])),parent_sha=parent_sha,parent_ref_result=parent_row,plan_contract_sha256=R.sha(R.encode({k:v for k,v in plan.items() if k!='root_body_validation_at_unix_ms'})),journal_directory=journal,deadline_unix_ms=ends,tools=plan['supported_tool_order'],automatic_retry=False,original_awards=[])
 admission=encode(grant)
 cfg=dict(schema='dg16.g1-root-control-driver-configuration.v1',issuer_thread=ISSUER,artifact_session=artifact_session,initial_session=initial_session,initial_body=initial_body_row,initial_publication=initial_publication_row,body=body_row,parent_sha=parent_sha,parent_ref_result=parent_row,deadline_unix_ms=ends,journal_directory=journal,admission={'path':str(out/'CONTROL_ADMISSION.json'),'sha256':sha(admission)})
 raw=encode(cfg);plan_raw=R.encode(plan)
 need(len(raw)<=65536 and len(admission)<=65536 and len(plan_raw)<=262144 and plan_raw.isascii(),'EXACT_CONTROL_CONFIGURATION_AND_CALLBACK_PLAN_SIZE')
 return {'DECISION.json':body,'PARENT_REF_RESULT.json':parent_raw,'CONTROL_ADMISSION.json':admission,'CONTROL_CONFIGURATION.json':raw,'TRUSTED_PUBLICATION_PLAN.json':plan_raw,
  'TRUSTED_PLAN_DESCRIPTOR.json':encode(dict(path=str(out/'TRUSTED_PUBLICATION_PLAN.json'),**desc(plan_raw),trust='ROOT_AUTHENTICATES_EXACT_ACTUAL_PLAN_OUTSIDE_TTY_NOT_SELF_AUTHENTICATED')),
  'WINDOWS_SELECTION.json':encode(selection('control',out/'CONTROL_CONFIGURATION.json',raw,shell_title))}
def write_documents(out,files):
 need(os.name=='posix' and sys.platform=='linux' and os.getuid()==os.geteuid()>0,'ACTUAL_ROOT_NONROOT_POSIX_ISSUANCE_ONLY');out=Path(inside(out,ROOT/'event-configurations'))
 need(out.parent.resolve(strict=True)==out.parent and not os.path.lexists(out),'FRESH_CONFIGURATION_DIRECTORY')
 for name in ('ROLE_CONFIGURATION.json','CONTROL_CONFIGURATION.json'):
  if name in files:
   cfg=parse(files[name]);future=Path(cfg.get('session_directory',cfg.get('journal_directory','')))
   need(future.is_absolute() and not os.path.lexists(future),'FRESH_ROLE_OR_CONTROL_JOURNAL_REQUIRED')
 out.mkdir(mode=0o700)
 for name,raw in files.items():
  need(re.fullmatch('[A-Z0-9_.]+',name) and type(raw) is bytes,'CLOSED_OUTPUT_FILE')
  p=out/name;fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
  try:
   os.fchmod(fd,0o600);v=memoryview(raw)
   while v:n=os.write(fd,v);need(n>0,'SHORT_WRITE');v=v[n:]
   os.fsync(fd)
  finally:os.close(fd)
  need(read(p,max(1,len(raw)))==raw,'EXACT_ISSUANCE_READBACK')
 receipt=encode(dict(schema='dg16.g1-root-event-issuance-readback.v1',issuer_thread=ISSUER,files={n:desc(b) for n,b in files.items()},actual_native_root_invocation_required=True,provider_or_control_calls_performed=False))
 p=out/'ISSUANCE_READBACK.json';fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:
  os.fchmod(fd,0o600);v=memoryview(receipt)
  while v:n=os.write(fd,v);need(n>0,'COMMIT_SHORT_WRITE');v=v[n:]
  os.fsync(fd)
 finally:os.close(fd)
 need(read(p,65536)==receipt,'ISSUANCE_COMMIT_READBACK')
 marker=out/'ISSUANCE_COMMITTED';fd=os.open(marker,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:os.fchmod(fd,0o600);os.fsync(fd)
 finally:os.close(fd)
 fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
 return desc(receipt)
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['inspect-role','issue-role','inspect-tools-decision','issue-tools-decision','inspect-control','issue-control']);p.add_argument('inputs',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 R=receiver();s=R.Sources();v=parse(read(a.inputs,65536));now=time.time_ns()//1000000;out=inside(a.output,ROOT/'event-configurations')
 if a.action.endswith('tools-decision'):
  need(set(v)=={'schema','artifact_session','issued_unix_ms','expires_unix_ms'} and v['schema']=='dg16.g1-root-tools-decision-input.v1','EXACT_TOOLS_DECISION_INPUTS')
  got=received_session(R,s,v['artifact_session']);body=tools_decision(R,s,got,v['issued_unix_ms'],v['expires_unix_ms'],now);files={'DECISION.json':body}
 elif a.action.endswith('role'):
  need(set(v)=={'schema','phase','context','window_opened_unix_ms','deadline_unix_ms','provider_readback','shell_title','initial_session','actual_root_decision'} and v['schema']=='dg16.g1-root-role-issuance-input.v1','EXACT_ROLE_INPUTS')
  context(R,s,v['context']);deadline(now,v['window_opened_unix_ms'],v['deadline_unix_ms'])
  provider=provider_check(R,s,v['context'],v['phase'],parse(bound(v['provider_readback'],65536)),now,v['window_opened_unix_ms'],v['deadline_unix_ms'])
  if v['phase']=='g3_final':
   previous=received_session(R,s,v['initial_session']);root_raw=bound(v['actual_root_decision'],8192)
   need(previous['phase']=='g3_initial' and previous['context']==v['context'],'ACTUAL_INITIAL_SAME_CONTEXT')
   initial_raw=previous['files']['ROOT_REQUEST.json'];s.I.validate_root(root_raw,initial_raw,R.parse(initial_raw))
  files=role_documents(R,s,v['phase'],v['context'],v['window_opened_unix_ms'],v['deadline_unix_ms'],out,v['shell_title'],now,v['initial_session'],v['actual_root_decision'])
  files['PROVIDER_BINDING.json']=encode(provider)
 else:
  need(set(v)=={'schema','artifact_session','decision','parent_sha','parent_ref_result','window_opened_unix_ms','deadline_unix_ms','shell_title','initial_session','initial_body','initial_publication'} and v['schema']=='dg16.g1-root-control-issuance-input.v1','EXACT_CONTROL_INPUTS')
  previous=None;first_body=None;initial_control=None
  if v['initial_session'] is not None:
   previous=received_session(R,s,v['initial_session']);first_body=bound(v['initial_body'],8192);published=parse(bound(v['initial_publication'],65536))
   need(published['phase']=='g3_initial' and published['context']==previous['context'] and published['root_body']==R.desc(first_body) and published['artifact_receiving']==R.desc(R.encode(previous['receipt'])) and published['published_commit']==v['parent_sha'],'ACTUAL_INITIAL_PUBLICATION_PARENT_JOIN')
   initial_control=dict(body=first_body,receiving=previous,published_commit=published['published_commit'])
  got=received_session(R,s,v['artifact_session'],previous,first_body)
  body=bound(v['decision'],16384);parent_raw=bound(v['parent_ref_result'],R.MAX_RESULT)
  module_at(CONTROL_PATH,CONTROL_SHA).metadata_guard(parent_raw)
  files=control_documents(R,s,got,body,v['parent_sha'],parent_raw,v['window_opened_unix_ms'],v['deadline_unix_ms'],out,v['shell_title'],now,v['artifact_session'],v['initial_session'],v['initial_body'],v['initial_publication'],initial_control)
 result=dict(authority='NONE',action=a.action,output=str(out),files={n:desc(b) for n,b in files.items()},actual_admission_issued=False,provider_calls=0,host_or_control_publication=False)
 if a.action.startswith('issue-'):result['issuance_readback']=write_documents(out,files);result['actual_admission_issued']=True
 print(encode(result).decode(),end='')
if __name__=='__main__':
 try:main()
 except BaseException:print('{"authority":"NONE","status":"REFUSED_NO_EFFECT_AUTHORITY_INFERRED"}');raise SystemExit(1)
