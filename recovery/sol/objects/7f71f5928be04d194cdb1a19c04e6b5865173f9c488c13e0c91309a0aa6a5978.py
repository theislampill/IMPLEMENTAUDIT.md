"""Guarded two-leaf binary publication plans/Root event CLI; no tools in Python.

No encryption or private key operation exists here. Root alone reads actual
post-encryption files and executes five exact admitted MCP writes/readbacks.
"""
import argparse,ast,base64,hashlib,json,os,re,stat,sys,time,types,urllib.parse
from pathlib import Path
ROOT=Path('/home/agent/dg16-g1-current04-operators/public-receiver-02')
ISSUER='01a1953f-a15b-7811-aa72-3538ebb03562'
MAX_RESULT=4*1024**2
FILE_READER_SHA='ab938a99ce3971caaa5e740bf4c079e3245cf0893ea358580c3661807104dcb1'
CONTROL_DRIVER_SHA='c381d6faa55513ee1a3e368ec9f5d7c2867e704ca0b2ab0dae18187b36ba8f43'
READBACK_PROFILE='FIRST_PARTY_BASE64_FILE_AT_PUBLISHED_COMMIT'
FRAME_SECONDS=45
ARGUMENT_CHUNK_BYTES=8192
TOOLS=('mcp__codex_apps__github_create_blob','mcp__codex_apps__github_create_blob','mcp__codex_apps__github_create_tree','mcp__codex_apps__github_create_commit','mcp__codex_apps__github_update_ref')
def need(ok,code):
 if not ok:raise ValueError(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def desc(raw):return dict(bytes=len(raw),sha256=sha(raw))
def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def parse(raw):
 def pairs(rows):
  d={}
  for k,v in rows:need(k not in d,'DUPLICATE_KEY');d[k]=v
  return d
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE'))
def git(kind,raw):return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def tiny_tree(files):return git('tree',b''.join(b'100644 '+n.encode()+b'\0'+bytes.fromhex(git('blob',files[n])) for n in sorted(files)))
def plan(P,V,binding,request,terminal,control,cipher,now_ms):
 need(type(terminal) is dict and terminal.get('schema')=='dg16.root-sender-terminal-export.v1' and terminal.get('authority')=='NONE'
  and terminal.get('publication_performed') is False and terminal.get('original_awards')==[],'ACTUAL_SENDER_TERMINAL_REQUIRED')
 result=terminal['result'];need(result['status']=='PAYLOAD_READY' and result['cleanup_complete'] is True and result['original_awards']==[],'SINGLE_ENCRYPTION_PAYLOAD_READY_REQUIRED')
 files={'CONTROL.json':control,'INPUTS.cms':cipher}
 need(terminal['ciphertext_members']=={n:desc(b) for n,b in files.items()} and result['request_sha256']==sha(request),'ACTUAL_SENDER_OUTPUT_DESCRIPTORS')
 P.validate_control(control,cipher,request,now_ms)
 need(binding['repository']=='theislampill/IMPLEMENTAUDIT.md' and type(binding['control_parent']) is str and re.fullmatch('[0-9a-f]{40}',binding['control_parent']),'ACTUAL_SELECTED_PARENT')
 branch=binding['control_branch'];need(type(branch) is str and re.fullmatch(r'pro/[A-Za-z0-9][A-Za-z0-9/_-]{0,180}',branch) and '..' not in branch and '//' not in branch,'FIXED_CIPHER_BRANCH')
 # Actual whole response bound is independently enforced on every frame too.
 need(len(base64.b64encode(cipher))+65536<=MAX_RESULT,'MCP_BASE64_BLOB_TRANSPORT_BOUND')
 q=P.parse(request,P.MAX_REQUEST)
 return dict(readback_profile=READBACK_PROFILE,file_reader_source_sha256=FILE_READER_SHA,frame_seconds=FRAME_SECONDS,argument_chunk_bytes=ARGUMENT_CHUNK_BYTES,schema='dg16.binary-cipher-publication-plan.v1',authority='NONE',repository=binding['repository'],branch=branch,parent_sha=binding['control_parent'],
  context={k:q[k] for k in P.CONTEXT_KEYS},request=desc(request),sender_terminal=desc(encode(terminal)),files={n:dict(**desc(b),git_blob=git('blob',b)) for n,b in files.items()},
  expected_tree=tiny_tree(files),expires_unix_ms=q['expires_unix_ms'],supported_tool_order=list(TOOLS),effect_grant=False,automatic_retry=False,original_awards=[])
def result_sha(raw):
 v=parse(raw);need(type(v) is dict and set(v)<={'content','structuredContent','isError','_meta'} and v.get('isError') is False,'ACTUAL_WRITE_RESULT')
 need(type(v.get('_meta',{})) is dict and not any(v.get('_meta',{}).get(k) for k in ('truncated','isTruncated','partial','hasMore')),'COMPLETE_WRITE_RESULT')
 h=v.get('structuredContent',{}).get('sha');need(type(h) is str and re.fullmatch('[0-9a-f]{40}',h),'ACTUAL_WRITE_SHA');return h
def write_call(p,files,previous):
 need(set(files)=={'CONTROL.json','INPUTS.cms'} and p['expected_tree']==tiny_tree(files)
  and p['files']=={n:dict(**desc(b),git_blob=git('blob',b)) for n,b in files.items()},'EXACT_TWO_INPUT_BODIES')
 i=len(previous);need(0<=i<5,'EXACT_FIVE_WRITES')
 expected=(p['files']['CONTROL.json']['git_blob'],p['files']['INPUTS.cms']['git_blob'],p['expected_tree'])
 for j,raw in enumerate(previous[:3]):need(result_sha(raw)==expected[j],'PREVIOUS_ACTUAL_OBJECT_CHANGED')
 repo=p['repository']
 if i==0:args=dict(repository_full_name=repo,content=files['CONTROL.json'].decode('utf8'),encoding='utf-8')
 elif i==1:args=dict(repository_full_name=repo,content=base64.b64encode(files['INPUTS.cms']).decode('ascii'),encoding='base64')
 elif i==2:args=dict(repository_full_name=repo,tree_elements=[dict(path=n,mode='100644',type='blob',sha=p['files'][n]['git_blob']) for n in sorted(files)])
 elif i==3:args=dict(repository_full_name=repo,tree_sha=p['expected_tree'],parent_sha=p['parent_sha'],message='DG16 exact encrypted input control run '+p['context']['run_id'])
 else:args=dict(repository_full_name=repo,branch_name=p['branch'],sha=result_sha(previous[3]),expected_sha=p['parent_sha'],force=False)
 return dict(tool=TOOLS[i],arguments=args,ordinal=i,authority='NONE',automatic_retry=False)
def read_plan(p,published):
 need(type(published) is str and re.fullmatch('[0-9a-f]{40}',published),'ACTUAL_PUBLISHED_COMMIT')
 api='https://api.github.com/repos/'+p['repository'];ref=api+'/git/ref/heads/'+urllib.parse.quote(p['branch'],safe='/')
 calls=[('ref',dict(tool='mcp__codex_apps__github_fetch',arguments={'url':ref})),
  ('commit',dict(tool='mcp__codex_apps__github_fetch',arguments={'url':api+'/git/commits/'+published})),
  ('tree',dict(tool='mcp__codex_apps__github_fetch',arguments={'url':api+'/git/trees/'+p['expected_tree']}))]
 for key,name in (('blob-control','CONTROL.json'),('blob-cipher','INPUTS.cms')):
  calls.append((key,dict(tool='mcp__codex_apps__github_fetch_file',arguments=dict(repository_full_name=p['repository'],path=name,ref=published,encoding='base64'))))
 calls.append(('closing_ref',dict(tool='mcp__codex_apps__github_fetch',arguments={'url':ref})))
 return calls

def file_reader():
 path=Path(__file__).resolve().parent/'file_readback.py'
 raw=read_exact(path,1024**2,FILE_READER_SHA);m=types.ModuleType('actual_file_base64_reader');m.__file__=str(path)
 exec(compile(raw,str(path),'exec'),m.__dict__);return m

def frame_remaining(intent,now_ms):
 start=intent['frame_started_unix_ms'];end=intent['frame_deadline_unix_ms'];grant=intent['expires_unix_ms']
 need(all(type(x) is int for x in (start,end,grant,now_ms)) and start<=now_ms<end<=min(start+45000,grant),'ORIGINAL_FRAME_WINDOW_EXPIRED')
 return (end-now_ms)/1000

def unwrap(raw,url):
 v=parse(raw);need(type(v) is dict and v.get('isError') is False and type(v.get('_meta',{})) is dict and not any(v.get('_meta',{}).get(k) for k in ('truncated','isTruncated','partial','hasMore')),'COMPLETE_READ_RESULT')
 sc=v.get('structuredContent');need(type(sc) is dict and sc.get('url')==sc.get('display_url')==url and type(sc.get('content')) is str,'ACTUAL_READ_ENDPOINT')
 if 'structuredContent' in sc:need(sc['structuredContent'].get('content')==sc['content'] and sc['structuredContent'].get('display_url')==url,'NESTED_READ_CHANGED')
 value=parse(sc['content'].encode());need(type(value) is dict,'READ_OBJECT');return value
def receive(P,V,p,files,writes,reads,request,now_ms):
 P.validate_control(files['CONTROL.json'],files['INPUTS.cms'],request,now_ms);published=result_sha(writes[3])
 calls=dict(read_plan(p,published));need(set(reads)==set(calls),'ALL_SIX_READBACKS_REQUIRED')
 rows={k:unwrap(reads[k],calls[k]['arguments']['url']) for k in ('ref','commit','tree','closing_ref')}
 ref,commit,tree=rows['ref'],rows['commit'],rows['tree']
 need(ref==rows['closing_ref'] and ref.get('ref')=='refs/heads/'+p['branch'] and ref.get('object',{}).get('type')=='commit'
  and ref['object']['sha']==commit.get('sha')==published and published!=p['parent_sha'],'PUBLISHED_REF_COMMIT_BINDING')
 need(type(commit.get('parents')) is list and len(commit['parents'])==1 and commit['parents'][0].get('sha')==p['parent_sha'],'CONTROL_ONE_FRESH_COMMIT')
 need(commit.get('tree',{}).get('sha')==tree.get('sha')==p['expected_tree'] and tree.get('truncated') is False
  and type(tree.get('tree')) is list and len(tree['tree'])==2,'CONTROL_TREE_BINDING')
 need({r.get('path') for r in tree['tree']}=={'CONTROL.json','INPUTS.cms'},'CONTROL_TREE_POPULATION')
 expected={n:p['files'][n] for n in files};D=file_reader();returned={}
 for r in tree['tree']:
  name=r['path'];f=expected[name]
  need((r.get('mode'),r.get('type'),r.get('sha'),r.get('size'))==('100644','blob',f['git_blob'],f['bytes']),'CONTROL_EXACT_TREE_LEAF')
  key='blob-control' if name=='CONTROL.json' else 'blob-cipher'
  returned[name]=D.decode_file_result(reads[key],calls[key],dict(bytes=f['bytes'],sha256=f['sha256'],git_blob_sha=f['git_blob']),P.MAX_CONTROL if name=='CONTROL.json' else P.MAX_CIPHERTEXT)
 need(returned==files,'BOTH_ACTUAL_BINARY_BODY_READBACKS_CHANGED')
 return dict(schema='dg16.binary-cipher-publication-receiving.v1',authority='NONE',context=p['context'],branch=p['branch'],published_commit=published,
  sole_parent=p['parent_sha'],tree=p['expected_tree'],files=p['files'],readbacks={k:desc(v) for k,v in reads.items()},root_tool_history_authentication_required=True,
  readback_profile='FIRST_PARTY_BASE64_FILE_AT_PUBLISHED_COMMIT',actual_read_calls=calls,
  effect_grant=False,private_key_operation=False,original_awards=[])

def run(P,V,p,files,request,journal,guard,frame,emit,now_ms,current_source):
 """No MCP in Python. Root privately reads bound argument chunks, then calls."""
 writes=[];reads={};pending=None
 def current():
  need(now_ms()<p['expires_unix_ms'] and callable(current_source),'PUBLICATION_WINDOW_EXPIRED_OR_SOURCE_UNBOUND')
  current_source();P.validate_control(files['CONTROL.json'],files['INPUTS.cms'],request,now_ms())
 def exchange(kind,call):
  nonlocal pending
  current();pending=kind;args=encode(call['arguments']);need(len(args)<=MAX_RESULT,'ARGUMENT_FILE_BOUND');journal.reserve(len(args)+MAX_RESULT+65536)
  journal.write(kind+'.ARGUMENTS.json',args)
  started=now_ms();frame_deadline=min(started+45000,p['expires_unix_ms'])
  intent=dict(schema='dg16.binary-publication-exclusive-intent.v1',authority='NONE',kind=kind,tool=call['tool'],arguments=desc(args),
   arguments_path=str(journal.path/(kind+'.ARGUMENTS.json')),expires_unix_ms=p['expires_unix_ms'],
   frame_started_unix_ms=started,frame_deadline_unix_ms=frame_deadline,automatic_retry=False)
  iraw=encode(intent);journal.write(kind+'.INTENT.json',iraw);current()
  emit(dict(event='intent',intent=intent,intent_sha256=sha(iraw),intent_path=str(journal.path/(kind+'.INTENT.json'))))
  raw=frame(MAX_RESULT,frame_remaining(intent,now_ms()));d=desc(raw) if type(raw) is bytes else None
  try:
   need(type(raw) is bytes and 0<len(raw)<=MAX_RESULT,'FULL_ACTUAL_RESPONSE_BOUND');guard(raw)
  except BaseException:
   journal.write(kind+'.REJECTED.json',encode(dict(authority='NONE',actual_result=d,raw_retained=False,automatic_retry=False)));raise
  # Actual late returned write remains evidence; qualification follows retention.
  journal.write(kind+'.RETURNED.json',encode(dict(authority='NONE',actual_result=d,returned_ms=now_ms(),source_acceptance=False)))
  journal.write(kind+'.RESULT.json',raw);current();frame_remaining(intent,now_ms());pending=None;return raw
 try:
  current();journal.write('PLAN.json',encode(p))
  for i in range(5):
   call=write_call(p,files,writes);raw=exchange('WRITE'+str(i),call)
   if i<3:need(result_sha(raw)==(p['files']['CONTROL.json']['git_blob'],p['files']['INPUTS.cms']['git_blob'],p['expected_tree'])[i],'ACTUAL_CREATED_OBJECT')
   elif i==3:result_sha(raw)
   else:
    v=parse(raw);need(v.get('isError') is False,'ACTUAL_GUARDED_UPDATE_REF')
   writes.append(raw);emit(dict(event='retained',kind='WRITE'+str(i),actual_result=desc(raw)))
  for key,call in read_plan(p,result_sha(writes[3])):
   reads[key]=exchange('READ_'+key.upper(),call)
   emit(dict(event='retained',kind='READ_'+key.upper(),actual_result=desc(reads[key])))
  current();result=receive(P,V,p,files,writes,reads,request,now_ms());journal.write('RECEIVING.json',encode(result));current();emit(dict(event='complete',receipt=result));return result
 except BaseException:
  try:journal.write('UNKNOWN.json',encode(dict(authority='NONE',status='UNKNOWN_NO_REPLAY',pending=pending,automatic_retry=False)))
  except BaseException:pass
  emit(dict(event='failure',status='UNKNOWN_NO_REPLAY'));return None

def read_exact(path,maximum,pin=None,private=False):
 p=Path(path);need(p.is_absolute() and p.resolve(strict=True)==p,'PHYSICAL_PATH');s=p.lstat()
 need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode) in ((0o600,) if private else (0o400,0o444,0o600)) and 0<s.st_size<=maximum,'OWNED_INPUT')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC);mark=lambda v:(v.st_dev,v.st_ino,v.st_mode,v.st_uid,v.st_gid,v.st_nlink,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
 try:
  need(mark(os.fstat(fd))==mark(s),'OPEN_CHANGED');b=b''
  while len(b)<=maximum:
   part=os.read(fd,min(65536,maximum+1-len(b)))
   if not part:break
   b+=part
  need(len(b)==s.st_size and mark(os.fstat(fd))==mark(s)==mark(p.lstat()),'CLOSING_CHANGED')
 finally:os.close(fd)
 if pin:need(sha(b)==pin,'ACTUAL_SOURCE_INPUT_PIN')
 return b
def driver_module(path):
 raw=read_exact(path,1024**2,CONTROL_DRIVER_SHA);m=types.ModuleType('exact_control_journal');m.__file__=str(path);exec(compile(raw,str(path),'exec'),m.__dict__);return m
def chunk(intent_path,intent_sha,offset,count,driver_path):
 need(type(offset) is int and offset>=0 and type(count) is int and 1<=count<=8192,'ROOT_CHUNK_BOUND')
 D=driver_module(driver_path);iraw=D.read_owned(intent_path,65536);need(sha(iraw)==intent_sha,'DURABLE_ACTUAL_INTENT_SHA');i=parse(iraw)
 need(i['schema']=='dg16.binary-publication-exclusive-intent.v1','ACTUAL_CHUNK_WINDOW');frame_remaining(i,time.time_ns()//1000000)
 ap=Path(i['arguments_path']);need(ap.parent==Path(intent_path).parent and ap.name==i['kind']+'.ARGUMENTS.json','FIXED_ARGUMENTS_FILE')
 need(ap.is_absolute() and ap.resolve(strict=True)==ap,'ARGUMENT_FILE_NONALIAS');before=ap.lstat()
 need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.geteuid() and stat.S_IMODE(before.st_mode)==0o600
  and 0<before.st_size==i['arguments']['bytes']<=MAX_RESULT and offset<=before.st_size,'OWNED_ARGUMENT_FILE')
 fd=os.open(ap,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 try:
  need(mark(os.fstat(fd))==mark(before),'ARGUMENT_OPEN_CHANGED');h=hashlib.sha256();pos=0
  while pos<before.st_size:
   frame_remaining(i,time.time_ns()//1000000)
   block=os.pread(fd,min(65536,before.st_size-pos),pos);need(block,'ARGUMENT_TRUNCATED');pos+=len(block);h.update(block)
  need(h.hexdigest()==i['arguments']['sha256'],'WHOLE_ARGUMENT_SHA')
  part=os.pread(fd,min(count,before.st_size-offset),offset)
  need(mark(os.fstat(fd))==mark(before)==mark(ap.lstat()),'CHUNK_CLOSING_CHANGED');frame_remaining(i,time.time_ns()//1000000)
 finally:os.close(fd)
 return dict(authority='NONE',offset=offset,count=len(part),total_bytes=before.st_size,whole_file_sha256=h.hexdigest(),chunk_base64=base64.b64encode(part).decode(),frame_started_unix_ms=i['frame_started_unix_ms'],frame_deadline_unix_ms=i['frame_deadline_unix_ms'],expires_unix_ms=i['expires_unix_ms'])

def main():
 need(os.name=='posix' and sys.platform=='linux' and os.getuid()==os.geteuid()>0 and sys.flags.isolated and sys.dont_write_bytecode,'ROOT_NONROOT_ISOLATED_SOURCE_PROCESS')
 a=argparse.ArgumentParser();sub=a.add_subparsers(dest='command',required=True)
 c=sub.add_parser('read-arguments-chunk');c.add_argument('--intent',required=True);c.add_argument('--intent-sha256',required=True);c.add_argument('--offset',type=int,required=True);c.add_argument('--count',type=int,required=True);c.add_argument('--control-driver',required=True)
 r=sub.add_parser('publish');r.add_argument('--configuration',required=True);r.add_argument('--configuration-sha256',required=True)
 args=a.parse_args()
 if args.command=='read-arguments-chunk':print(encode(chunk(args.intent,args.intent_sha256,args.offset,args.count,args.control_driver)).decode(),end='');return
 need(sys.stdin.isatty(),'EXISTING_NOECHO_TTY_REQUIRED')
 cfg=parse(read_exact(args.configuration,65536,args.configuration_sha256));need(cfg['issuer_thread']==ISSUER,'ACTUAL_ROOT_ISSUER_CONFIGURATION')
 def bound(name,maxbytes):
  row=cfg[name];return read_exact(row['path'],maxbytes,row['sha256'])
 D=driver_module(cfg['control_driver_path']);entry_raw=bound('sender_entry',1024**2);install_raw=bound('sender_install_manifest',4*1024**2);manifest=parse(install_raw)
 need(manifest['members']['root_sender_entry.py']==desc(entry_raw),'ACTUAL_SENDER_INSTALL_SOURCE')
 terminal_raw=bound('sender_terminal',65536);terminal=parse(terminal_raw);need(terminal['result']['status']=='PAYLOAD_READY','NO_REENCRYPTION_OR_UNREADY_READ')
 E=types.ModuleType('actual_root_sender_source');E.__file__=cfg['sender_entry']['path'];exec(compile(entry_raw,E.__file__,'exec'),E.__dict__)
 loader,m,binding,selection,archive=E.inputs() # Never sender(); no encryption.
 directory=m.carrier.session_path(binding,selection['operation']['context'],root=True)
 outcome_raw=m.files.read_file(directory/'OUTCOME.json',65536,private=True)[0];outcome=m.policy.parse(outcome_raw,65536)
 need(outcome['public']==terminal['result'] and outcome['public']['cleanup_complete'] is True,'ACTUAL_SINGLE_SENDER_OUTCOME')
 files={n:m.files.read_file(directory/n,m.policy.MAX_CONTROL if n=='CONTROL.json' else m.policy.MAX_CIPHERTEXT,private=True)[0] for n in ('CONTROL.json','INPUTS.cms')}
 request=m.provider.artifact_files(archive)['REQUEST.json'];V=m.provider
 m.carrier.require_auth_enveloped(files['INPUTS.cms'])
 now=lambda:time.time_ns()//1000000
 p=plan(m.policy,V,binding,request,terminal,files['CONTROL.json'],files['INPUTS.cms'],now());p['expires_unix_ms']=min(p['expires_unix_ms'],selection['operation']['expires_unix_ms'],cfg['deadline_unix_ms'])
 parent=unwrap(bound('parent_ref_result',MAX_RESULT),'https://api.github.com/repos/'+p['repository']+'/git/ref/heads/'+urllib.parse.quote(p['branch'],safe='/'))
 need(parent.get('ref')=='refs/heads/'+p['branch'] and parent.get('object',{}).get('type')=='commit' and parent['object']['sha']==p['parent_sha'],'ACTUAL_EXPECTED_PARENT_REF')
 receiving_raw=bound('sender_receiving',4*1024**2);admission=parse(bound('admission',65536))
 expected=dict(schema='dg16.root-binary-cipher-publication-admission.v2',issuer_thread=ISSUER,context=p['context'],branch=p['branch'],parent_sha=p['parent_sha'],
  sender_receiving=desc(receiving_raw),sender_install_manifest=desc(install_raw),sender_terminal=desc(terminal_raw),parent_ref_result=cfg['parent_ref_result'],files=p['files'],request=p['request'],
  readback_profile=READBACK_PROFILE,file_reader_source_sha256=FILE_READER_SHA,frame_seconds=FRAME_SECONDS,argument_chunk_bytes=ARGUMENT_CHUNK_BYTES,
  expected_tree=p['expected_tree'],journal_directory=cfg['journal_directory'],deadline_unix_ms=p['expires_unix_ms'],tools=list(TOOLS),automatic_retry=False,private_key_operation=False,original_awards=[])
 need(admission==expected and now()<p['expires_unix_ms'],'ACTUAL_ROOT_BINARY_PUBLICATION_ADMISSION')
 Rraw=read_exact(cfg['resolver_path'],1024**2,'b2ac1130149d9878a3a00c7d8ba214743920a1aede38cb6b75699e14a2d03530');X=types.ModuleType('exact_noecho_frame');X.__file__=cfg['resolver_path'];exec(compile(Rraw,X.__file__,'exec'),X.__dict__)
 journal=D.Journal(cfg['journal_directory'])
 try:
  def current_source():m.carrier.current_binding(binding);m.sender_policy.current(selection);loader.current()
  result=run(m.policy,V,p,files,request,journal,D.metadata_guard,lambda maximum,seconds:X.read_ephemeral_frame(maximum,seconds),lambda e:print(encode(e).decode(),end='',flush=True),now,current_source)
 finally:journal.close()
 need(result is not None,'UNKNOWN_BINARY_PUBLICATION_NO_REPLAY')
if __name__=='__main__':
 try:main()
 except BaseException:print('{"event":"failure","status":"UNKNOWN_NO_REPLAY","authority":"NONE"}',flush=True);raise SystemExit(1)
