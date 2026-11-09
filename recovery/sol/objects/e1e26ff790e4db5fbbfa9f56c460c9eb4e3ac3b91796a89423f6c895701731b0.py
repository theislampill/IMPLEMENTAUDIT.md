"""One-process private journal + native Root callback bridge; no network fallback.

No raw tool result, download/materialization wrapper or duplicate native history
is ever serialized. Losing this process loses the frame: UNKNOWN, never replay.
"""
import dataclasses
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat

CORE_SHA='2b481d09dd7501fa7c22a3f9cb98c3c088293322cdaf26b2e8e35b5a64c59d32'
PREPARATION_SHA='6c7a67e3bf5ee1375e221ab68162da463be2fe63788d850e88ecc4a0ca6eebcd'
ISSUER='01a1953f-a15b-7811-aa72-3538ebb03562'
TOOL='mcp__codex_apps__github_fetch'
DOWNLOAD='mcp__codex_apps__github_download_workflow_artifact'
CAP=32*1024**2
def need(ok,code):
 if not ok:raise ValueError(code)
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return dict(bytes=len(b),sha256=sha(b))
def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()

@dataclasses.dataclass(frozen=True)
class NativeReply:
 result:bytes
 history:bytes
 provenance:dict

class RootBridge:
 """Root implements these against actual first-party tools and no-echo frames.

 No implementation exists here. Returning matching JSON is not authentication.
 admit must receive genuine native Root admission/provenance and return an
 opaque live capability. supported/body must return actual native histories.
 """
 def now_ms(self):raise NotImplementedError('ACTUAL_ROOT_BRIDGE_CLOCK_REQUIRED')
 def admit(self,admission_raw,preparation,context,role):raise NotImplementedError('ACTUAL_NATIVE_ROOT_ADMISSION_BRIDGE_REQUIRED')
 def supported(self,capability,tool,arguments,intent):raise NotImplementedError('ACTUAL_FIRST_PARTY_MCP_BRIDGE_REQUIRED')
 def body(self,capability,download_result,download_history,arguments,intent):raise NotImplementedError('ACTUAL_NO_ECHO_EPHEMERAL_BODY_BRIDGE_REQUIRED')
 def release(self,capability):pass

class PrivateJournal:
 """Actual POSIX held/no-follow, exclusive, bounded private writer."""
 def __init__(self,path):
  need(os.name=='posix' and os.getuid()==os.geteuid()>0,'NONROOT_POSIX_WRITER_REQUIRED')
  self.path=Path(path);need(self.path.is_absolute() and self.path.parent.resolve(strict=True)==self.path.parent and not os.path.lexists(self.path),'FRESH_ROLE_DIRECTORY_REQUIRED')
  self.path.mkdir(mode=0o700);self.fd=os.open(self.path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
  self.identity=self._identity(os.fstat(self.fd));self.bytes=0;self.entries=0;self.names=set()
  self._check()
 @staticmethod
 def _identity(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid)
 def _check(self):
  s=os.fstat(self.fd);need(self._identity(s)==self.identity==self._identity(self.path.lstat()) and s.st_uid==os.geteuid()
   and stat.S_IMODE(s.st_mode)==0o700 and not os.listxattr(self.fd) and self.path.resolve(strict=True)==self.path
   and set(os.listdir(self.fd))==self.names,'PRIVATE_JOURNAL_CUSTODY')
 def write(self,name,body):
  self._check();need(type(name) is str and re.fullmatch('[A-Za-z0-9_.-]{1,100}',name) and name not in ('.','..') and type(body) is bytes
   and self.bytes+len(body)<=CAP and self.entries<64,'PRIVATE_JOURNAL_BOUND')
  fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
  try:
   os.fchmod(fd,0o600);view=memoryview(body)
   while view:
    n=os.write(fd,view);need(n>0,'PRIVATE_SHORT_WRITE');view=view[n:]
   os.fsync(fd)
  finally:os.close(fd)
  os.fsync(self.fd);fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=self.fd)
  try:
   s=os.fstat(fd);need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode)==0o600 and s.st_size==len(body),'PRIVATE_FILE_CUSTODY')
   chunks=[];left=len(body)+1
   while left:
    b=os.read(fd,min(left,1024**2))
    if not b:break
    chunks.append(b);left-=len(b)
   end=os.fstat(fd);named=os.stat(name,dir_fd=self.fd,follow_symlinks=False)
   mark=lambda v:(v.st_dev,v.st_ino,v.st_mode,v.st_uid,v.st_gid,v.st_nlink,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
   need(b''.join(chunks)==body and mark(s)==mark(end)==mark(named) and not os.listxattr(fd),'PRIVATE_WRITE_READBACK')
  finally:os.close(fd)
  self.names.add(name);self.bytes+=len(body);self.entries+=1;self._check()
 def close(self):
  if self.fd is not None:os.close(self.fd);self.fd=None

class OperationalSession:
 def __init__(self,core,preparation_raw,admission_raw,context,role,bridge):
  need(isinstance(bridge,RootBridge),'ACTUAL_ROOT_CALLBACK_BRIDGE_REQUIRED')
  need(sha(preparation_raw)==PREPARATION_SHA,'ACTUAL_OPERATOR_PREPARATION_PIN')
  prep=json.loads(preparation_raw);grant=json.loads(admission_raw);now=bridge.now_ms()
  need(role in ('live','terminal') and prep['actor']==ISSUER and core.actual_installation['receiver_seal_sha256']==prep['public_receiver_seal']
   and core.b['final_tree']==prep['workflow_tree'] and context['workflow_commit']==prep['workflow_commit'] and context['branch']==prep['workflow_branch'],'ACTUAL_INSTALLED_PUBLIC_SUBJECT')
  expected_dir=core.runtime['receiver_output_root']+'/'+role
  need(grant.get('schema')=='dg16.public-only-operator-admission.v1' and grant.get('issuer_thread')==ISSUER
   and grant.get('context')==context and grant.get('role')==role and grant.get('session_directory')==expected_dir
   and grant.get('preparation_sha256')==PREPARATION_SHA and grant.get('receiver_seal_sha256')==prep['public_receiver_seal']
   and grant.get('effect_grant') is True and grant.get('source_root_write_granted') is True and grant.get('automatic_retry') is False
   and grant.get('private_or_cipher') is False and type(grant.get('issued_ms')) is int and type(grant.get('expires_ms')) is int
   and grant['issued_ms']<=now<grant['expires_ms']<=grant['issued_ms']+300000,'GENUINE_PER_ROLE_ROOT_ADMISSION_REQUIRED')
  # The native bridge authenticates the real Root act before the first write.
  capability=bridge.admit(admission_raw,prep,context,role);need(capability is not None,'NATIVE_ADMISSION_NOT_RECEIVED')
  self.core=core;self.bridge=bridge;self.capability=capability;self.closed=False;self.secret_frame_live=True
  self.expires_ms=grant['expires_ms'];self.download=None;self.history=None;self.result=None
  self.state=core.plan(context,role,now,sha(admission_raw));self.state['expires_ms']=self.state['opened_ms']+300000
  self.journal=PrivateJournal(expected_dir)
  self.journal.write('PLAN.json',encode(dict(schema='dg16.actual-public-operator-journal.v1',authority='NONE',role=role,context=context,
   admission=desc(admission_raw),preparation=desc(preparation_raw),expires_ms=self.expires_ms,automatic_retry=False,
   volatile_frame_required=True,reconstruct_from_disk=False,private_or_cipher=False)))
 @classmethod
 def resume(cls,*args,**kwargs):raise ValueError('UNKNOWN_VOLATILE_FRAME_EXTINCT_NO_REPLAY_OR_DUPLICATE_GET')
 def _now(self):
  need(not self.closed and self.secret_frame_live,'UNKNOWN_EPHEMERAL_FRAME_EXTINCT')
  now=self.bridge.now_ms();need(now<self.expires_ms,'UNKNOWN_OPERATOR_EXPIRED_NO_RETRY');return now
 def _memory(self):
  rows=list(self.state['entries'])+([self.state['pending']] if self.state['pending'] else [])
  return sum(len(e.get('tool_result',b''))+len(e.get('history',b'')) for e in rows)
 def _unknown(self):
  # Never log exception text, frame contents, URLs or history on rejection.
  try:
   if not self.closed:self.journal.write('UNKNOWN.json',encode(dict(status='UNKNOWN_NO_RETRY',authority='NONE',raw_frame_retained=False,reconstruct_from_disk=False)))
  except BaseException:pass # Partial journal/expiry is UNKNOWN, never a secret diagnostic.
  finally:self.close()
 def step(self):
  try:
   now=self._now();need(self.journal.bytes+self._memory()+2*4*1024**2+65536<=CAP,'TOTAL_DISK_AND_VOLATILE_32MIB_BOUND')
   self.state,res=self.core.reserve(self.state,now);ordinal=res['ordinal'];prefix='%02d.'%ordinal
   self.journal.write(prefix+'RESERVATION.json',encode(res))
   self.state,intent=self.core.intent(self.state,self._now(),{'issuer_thread':ISSUER,'reservation':desc(encode(res)),'native_root_persisted':True})
   self.journal.write(prefix+'INTENT.json',encode(intent))
   if intent['kind']=='body':
    need(self.download is not None and self.history is not None,'UNKNOWN_DOWNLOAD_FRAME_EXTINCT')
    reply=self.bridge.body(self.capability,self.download,self.history,intent['arguments'],intent)
   else:
    need(intent['tool'] in (TOOL,DOWNLOAD),'NO_UNSUPPORTED_TOOL_OR_GH_FALLBACK')
    reply=self.bridge.supported(self.capability,intent['tool'],intent['arguments'],intent)
   need(isinstance(reply,NativeReply),'ACTUAL_NATIVE_REPLY_REQUIRED')
   self.state=self.core.result(self.state,reply.result,reply.history,reply.provenance,self.bridge.now_ms())
   # Persist only descriptors/provenance; even ordinary raw wrappers/history
   # stay memory-only. No rejection path serializes the core state.
   ref=reply.provenance.get('tool_call_ref');need(type(ref) is str and re.fullmatch('[A-Za-z0-9_-]{1,160}',ref),'SAFE_ACTUAL_CALL_REFERENCE')
   note=dict(schema='dg16.public-operator-redacted-result.v1',authority='NONE',ordinal=ordinal,kind=intent['kind'],
    original_complete_result=desc(reply.result),native_history=desc(reply.history),actual_tool_call_ref=ref,
    raw_result_persisted=False,duplicate_history_persisted=False,external_native_provenance_authentication_required=True)
   if intent['kind']=='download':
    self.download=reply.result;self.history=reply.history
    if self.state['status']!='REFUSED_NO_RETRY':note['validated_redacted_download']=self.state['pending']['parsed']
   if intent['kind']=='body' and self.state['status']!='REFUSED_NO_RETRY':note['validated_public_archive']=self.state['pending']['parsed']['archive']
   self.journal.write(prefix+'RESULT_NOTE.json',encode(note))
   need(self.state['status']!='REFUSED_NO_RETRY','UNKNOWN_TOOL_RESULT_OR_PROVENANCE_REFUSED')
   self.state,receiving=self.core.receive_result(self.state,self._now());self.journal.write(prefix+'RECEIVING.json',encode(receiving))
   return dict(ordinal=ordinal,kind=intent['kind'],received=True,authority='NONE')
  except BaseException:
   self._unknown();raise ValueError('UNKNOWN_NO_RETRY_NO_SECRET_DIAGNOSTIC') from None
 def finish(self):
  try:
   files=self.core.receive_public(self.state,self._now());metadata=json.loads(files['PUBLIC_METADATA.json'])
   run=metadata['run'];commit=metadata['commit'];artifact=metadata['artifact']
   # Only the receiver-required public schema crosses to disk. Unknown provider
   # text, signed URLs, download URLs and token-bearing extras are discarded.
   phase='in_progress' if self.state['role']=='live' else 'completed'
   conclusion=run.get('conclusion');need(conclusion in (None,'success','failure','cancelled','timed_out','action_required','neutral','skipped','stale','startup_failure'),'PUBLIC_CONCLUSION_ENUM')
   safe_run={k:run[k] for k in ('id','run_attempt','head_sha','head_branch','event')};safe_run.update(status=phase,conclusion=conclusion,repository={'full_name':self.state['context']['repository']})
   safe_commit=dict(sha=commit['sha'],tree={'sha':commit['tree']['sha']},parents=[{'sha':p['sha']} for p in commit['parents']])
   safe_artifact={k:artifact[k] for k in ('id','name','expired','size_in_bytes','digest')};safe_artifact['workflow_run']={k:artifact['workflow_run'][k] for k in ('id','head_sha','head_branch')}
   files['PUBLIC_METADATA.json']=encode(dict(run=safe_run,commit=safe_commit,artifact=safe_artifact))
   need(self.journal.bytes+self._memory()+sum(map(len,files.values()))<=CAP,'FINAL_TOTAL_32MIB_BOUND')
   for name,body in files.items():self.journal.write(name,body)
   self.result=dict(status='PUBLIC_BODY_AND_METADATA_RECEIVED_REQUIRES_INDEPENDENT_RECEIVING',authority='NONE',role=self.state['role'],archive=desc(files['ARTIFACT.zip']),automatic_retry=False)
   self.close();return self.result
  except BaseException:
   self._unknown();raise ValueError('UNKNOWN_NO_RETRY_NO_SECRET_DIAGNOSTIC') from None
 def close(self):
  if not self.closed:
   self.secret_frame_live=False;self.download=None;self.history=None;self.state=None
   try:self.bridge.release(self.capability)
   except BaseException:self.release_status='UNKNOWN'
   finally:
    self.capability=None
    try:self.journal.close()
    finally:self.closed=True

def main():
 import argparse,sys
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('bridge-module','core-source','configuration','preparation','admission'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args()
 need(os.name=='posix' and sys.platform=='linux' and os.getuid()==os.geteuid()>0 and sys.flags.isolated and sys.dont_write_bytecode,'NONROOT_ISOLATED_POSIX_OPERATOR_REQUIRED')
 # Root-owned adapter factory must be separately received/reviewed. It exposes
 # actual in-process callbacks; no GH/curl/script/network fallback is supplied.
 spec=importlib.util.spec_from_file_location('actual_root_first_party_bridge',a.bridge_module);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 core_raw=a.core_source.read_bytes();need(sha(core_raw)==CORE_SHA,'FROZEN_OPERATOR_V2_CORE')
 core_module=__import__('types').ModuleType('exact_v2_public_core');core_module.__file__=str(a.core_source)
 exec(compile(core_raw,str(a.core_source),'exec'),core_module.__dict__)
 configuration=json.loads(a.configuration.read_bytes());bridge,core,context,role=module.create_received_root_bridge(configuration,core_module,RootBridge,NativeReply)
 need(isinstance(core,core_module.PublicOperator),'EXACT_V2_CORE_INSTANCE_REQUIRED')
 session=OperationalSession(core,a.preparation.read_bytes(),a.admission.read_bytes(),context,role,bridge)
 try:
  for _ in range(10):session.step()
  result=session.finish();print(encode(result).decode(),end='')
 finally:session.close()

if __name__=='__main__':
 try:main()
 except BaseException:print('{"status":"UNKNOWN_NO_RETRY","authority":"NONE"}');raise SystemExit(1)
