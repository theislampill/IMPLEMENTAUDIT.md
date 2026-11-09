"""Root-only public source install/configuration/readback; no live admission.

No ledger/history access, provider operation or G2 execution occurs unless Root
explicitly invokes run with an independently issued actual per-role admission.
"""
import argparse,base64,hashlib,json,os,re,stat,sys,time,types
from pathlib import Path

THREAD='01a1953f-a15b-7811-aa72-3538ebb03562'
TARGET='/home/agent/dg16-g2-current04-public-20261109/root-operation-driver-01'
PREP='6c7a67e3bf5ee1375e221ab68162da463be2fe63788d850e88ecc4a0ca6eebcd'
CORE='2b481d09dd7501fa7c22a3f9cb98c3c088293322cdaf26b2e8e35b5a64c59d32'
BRIDGE='cb9dab7c3920b7dbea359c22552501d2a434a1ef37883939eee0e7a2d1b4064f'
OPERATOR='e1e26ff790e4db5fbbfa9f56c460c9eb4e3ac3b91796a89423f6c895701731b0'

def need(v,c):
 if not v:raise ValueError(c)
def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def desc(b):return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def parse(b):
 def pairs(rows):
  d={}
  for k,v in rows:need(k not in d,'DUPLICATE_JSON_KEY');d[k]=v
  return d
 return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE_JSON'))
def read(p,maximum=4*1024**2,private=False):
 p=Path(p);need(p.is_absolute() and p.resolve(strict=True)==p,'PHYSICAL_PATH')
 for a in p.parents:need(not a.is_symlink(),'ANCESTOR_ALIAS')
 a=p.lstat();need(stat.S_ISREG(a.st_mode) and a.st_nlink==1 and 0<a.st_size<=maximum,'ORDINARY_BOUNDED_FILE')
 if private:need(os.name=='posix' and a.st_uid==os.geteuid() and stat.S_IMODE(a.st_mode)==0o600,'PRIVATE_CONFIGURATION')
 fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0)|getattr(os,'O_CLOEXEC',0)|getattr(os,'O_BINARY',0))
 try:
  mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  need(mark(os.fstat(fd))==mark(a),'OPEN_CHANGED');b=b''
  while len(b)<=maximum:
   c=os.read(fd,min(65536,maximum+1-len(b)))
   if not c:break
   b+=c
  need(len(b)==a.st_size and mark(a)==mark(os.fstat(fd))==mark(p.lstat()),'CLOSING_CHANGED');return b
 finally:os.close(fd)
def write(p,b,mode=0o600):
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode)
 try:
  os.fchmod(fd,mode);view=memoryview(b)
  while view:n=os.write(fd,view);need(n>0,'SHORT_WRITE');view=view[n:]
  os.fsync(fd)
 finally:os.close(fd)
 need(read(p,max(len(b),1))==b,'WRITE_READBACK')
def posix():need(os.name=='posix' and sys.platform=='linux' and os.getuid()==os.geteuid()>0,'NONROOT_LINUX_REQUIRED')
def validate_context(c):
 need(type(c) is dict and set(c)==set('repository branch run_id run_attempt workflow_commit source_commit source_tree workflow_path job_name'.split()),'EXACT_CONTEXT_FIELDS')
 fixed={'repository':'theislampill/IMPLEMENTAUDIT.md','branch':'pro/dg16-r5-full-g2-direct-host-01-20261109','run_attempt':1,
 'workflow_commit':'7f618adc702912f760d87f68fe9c94cc419e844c','source_commit':'7e2b00b3a2a16fc6033a5eabe4fc795f6249366f',
 'source_tree':'6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e','workflow_path':'.github/workflows/dg16-r5-full-g2.yml','job_name':'full-registry-raw-pair'}
 need(all(type(c[k]) is type(v) and c[k]==v for k,v in fixed.items()) and type(c['run_id']) is str and re.fullmatch('[1-9][0-9]{0,19}',c['run_id']),'EXACT_ACTUAL_EVENT_CONTEXT')
def installed(root):
 root=Path(root);posix();need(str(root)==TARGET and root.resolve(strict=True)==root,'EXACT_INSTALLED_ROOT')
 m=parse(read(root/'INSTALL_MANIFEST.json'))
 for n,d in m['members'].items():
  need(not Path(n).is_absolute() and '..' not in Path(n).parts,'MANIFEST_PATH')
  p=root/n;need(desc(read(p))==d and p.stat().st_uid==os.geteuid() and stat.S_IMODE(p.stat().st_mode)==0o444,'INSTALLED_SOURCE_CHANGED')
 return m
def make_configuration(root,context,role,turn,source_author):
 validate_context(context);need(role in ('live','terminal') and re.fullmatch('[0-9a-f-]{36}',turn) and type(source_author) is str and re.fullmatch('/root(?:/[A-Za-z0-9_-]+)*',source_author),'ACTUAL_ROOT_ROLE_BINDING')
 root=str(root)
 return dict(configuration_path=root+'/'+role+'.configuration.json',turn_id=turn,
  native_history_module=root+'/root_native_history.py',body_resolver_module=root+'/resolve_artifact.py',
  core_sources={n:root+'/core/'+n for n in ('root_acquire.py','root_common.py','public_receiver.py','prepare_live_control.py','shared_broker.py')},
  installation_receipt=root+'/FINAL_RECEIVER_INSTALLATION.json',receiver_seal=root+'/PUBLIC_RECEIVER_SEAL.json',
  public_binding=root+'/BINDING.json',runtime=root+'/SUCCESSOR_RUNTIME_BINDING.json',source_author=source_author,
  context=context,role=role,driver_journal_directory=root+'/driver-journal-'+role,
  driver_channel_directory=root+'/public-channel-'+role)
def install(bundle,destination):
 posix();bundle=Path(bundle).resolve(strict=True);dest=Path(destination)
 need(str(dest)==TARGET and not os.path.lexists(dest) and dest.parent.resolve(strict=True)==dest.parent,'EXACT_FRESH_INSTALL_DESTINATION')
 raw=read(bundle/'INSTALL_MANIFEST.json');m=parse(raw);files={}
 for n,d in m['members'].items():
  need(not Path(n).is_absolute() and '..' not in Path(n).parts,'INSTALL_MEMBER_PATH');b=read(bundle/'payload'/n);need(desc(b)==d,'INSTALL_SOURCE_PIN');files[n]=b
 need(desc(files['root_operator.py'])['sha256']==OPERATOR and desc(files['concrete_root_bridge.py'])['sha256']==BRIDGE and desc(files['public_operator_v2.py'])['sha256']==CORE,'FROZEN_OPERATOR_PINS')
 dest.mkdir(mode=0o700)
 for n,b in files.items():
  p=dest/n;p.parent.mkdir(mode=0o700,parents=True,exist_ok=True);write(p,b,0o444)
 write(dest/'INSTALL_MANIFEST.json',raw,0o444);installed(dest)
 receipt=dict(status='EXACT_PUBLIC_DRIVER_SOURCES_INSTALLED',authority='NONE',root=str(dest),manifest=desc(raw),members=len(files),uid=os.geteuid(),history_read=False,session_opened=False,live_admission_issued=False)
 write(dest/'INSTALLATION_READBACK.json',encode(receipt));return receipt
def configure(root,event,role,turn,author):
 installed(root);c=parse(read(event));cfg=make_configuration(root,c,role,turn,author);raw=encode(cfg);write(Path(cfg['configuration_path']),raw)
 return dict(status='EXACT_CONFIGURATION_CREATED_REQUIRES_NATIVE_ROOT_ADMISSION',authority='NONE',configuration_path=cfg['configuration_path'],configuration=desc(raw),context=c,role=role,turn_id=turn,live_admission_issued=False,required_admission_addition={'configuration_sha256':desc(raw)['sha256']})
def configuration(path):
 raw=read(path,private=True);cfg=parse(raw);root=Path(path).parent;installed(root)
 need(cfg==make_configuration(root,cfg['context'],cfg['role'],cfg['turn_id'],cfg['source_author']) and cfg['configuration_path']==str(path),'EXACT_CONFIGURATION_BODY');return root,cfg,raw
def launch(configuration_path,admission_path):
 need(sys.flags.isolated and sys.dont_write_bytecode,'ISOLATED_OPERATOR_PROCESS')
 root,cfg,raw=configuration(configuration_path);grant_raw=read(admission_path,private=True);g=parse(grant_raw);now=time.time_ns()//1000000
 need(g.get('configuration_sha256')==desc(raw)['sha256'] and g.get('issuer_thread')==THREAD and g.get('context')==cfg['context'] and g.get('role')==cfg['role'] and g.get('effect_grant') is True and g.get('source_root_write_granted') is True and g.get('private_or_cipher') is False and g.get('automatic_retry') is False and type(g.get('issued_ms')) is int and type(g.get('expires_ms')) is int and g['issued_ms']<=now<g['expires_ms']<=g['issued_ms']+300000,'ACTUAL_CONFIGURATION_BOUND_ROLE_ADMISSION_REQUIRED')
 def module(name,path,pin=None):
  code=read(path);need(pin is None or desc(code)['sha256']==pin,'EXACT_EXECUTING_SOURCE')
  m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m;exec(compile(code,str(path),'exec'),m.__dict__);return m
 O=module('fixed_unchanged_root_operator',root/'root_operator.py',OPERATOR)
 C=module('fixed_public_operator_core',root/'public_operator_v2.py',CORE)
 B=module('fixed_concrete_root_bridge',root/'concrete_root_bridge.py',BRIDGE)
 T=module('fixed_public_record_transport',root/'record_transport.py')
 bridge,core,context,role=B.create_received_root_bridge(cfg,C,O.RootBridge,O.NativeReply)
 channel=T.RecordTransport(cfg,raw);bridge.emit=channel.emit;bridge.frame=channel.frame
 session=None
 try:
  session=O.OperationalSession(core,read(root/'PUBLIC_OPERATOR_PREPARATION.json'),grant_raw,context,role,bridge)
  for _ in range(10):session.step()
  result=session.finish();channel.emit(result)
 except BaseException:
  if channel.created:channel.emit({'status':'UNKNOWN_NO_RETRY','authority':'NONE'})
  raise ValueError('UNKNOWN_ROLE_COMPLETION_NO_REPLAY') from None
 finally:
  if session is not None:session.close()
def note(configuration_path,note_raw):
 root,cfg,raw=configuration(configuration_path);v=parse(note_raw);need(type(v) is dict and v.get('authority')=='NONE' and len(note_raw)<=8192,'SAFE_DRIVER_NOTE')
 allowed={'driver_start_intent','driver_tool_intent','driver_wire_descriptor','driver_body_intent_observed','driver_body_received_observed'}
 need(v.get('event') in allowed or v.get('status') in ('UNKNOWN_NO_RETRY','TERMINAL_READ_BACK'),'FIXED_DRIVER_NOTE_KIND')
 text=encode(v);need(not any(x in text.lower() for x in (b'download_url',b'file_uri',b'file_reference',b'authorization',b'?sig=',b'token',b'raw_history',b'wire":"')),'SECRET_NOTE_REFUSED')
 p=Path(cfg['driver_journal_directory'])
 if v.get('event')=='driver_start_intent':need(not os.path.lexists(p),'DRIVER_RESTART_REFUSED');p.mkdir(mode=0o700)
 need(p.is_dir() and not p.is_symlink() and p.stat().st_uid==os.geteuid() and stat.S_IMODE(p.stat().st_mode)==0o700,'DRIVER_JOURNAL_CUSTODY')
 rows=list(p.iterdir());need(len(rows)<64 and sum(x.stat().st_size for x in rows)+len(text)<=131072,'DRIVER_JOURNAL_BOUND')
 write(p/('%02d.note.json'%len(rows)),text);return dict(status='SAFE_DRIVER_NOTE_RETAINED',note=desc(text))
def readback(configuration_path):
 _,cfg,_=configuration(configuration_path);runtime=parse(read(cfg['runtime']));p=Path(runtime['receiver_output_root'])/cfg['role']
 need(p.resolve(strict=True)==p and not p.is_symlink() and stat.S_IMODE(p.stat().st_mode)==0o700 and p.stat().st_uid==os.geteuid(),'ROLE_TERMINAL_DIRECTORY')
 files={};total=0
 for f in p.iterdir():
  need(re.fullmatch('[A-Za-z0-9_.-]{1,100}',f.name),'ROLE_FILE_NAME');b=read(f,32*1024**2);total+=len(b);need(total<=32*1024**2 and stat.S_IMODE(f.stat().st_mode)==0o600,'ROLE_FILE_BOUND_MODE');files[f.name]=desc(b)
 need(len(files)<=64 and {'ARTIFACT.zip','PUBLIC_METADATA.json','PROVIDER_RECEIVING.json','PLAN.json'}<=set(files) and 'UNKNOWN.json' not in files,'COMPLETE_PUBLIC_TERMINAL_FILES')
 need(files['ARTIFACT.zip']['bytes']<=262144,'BORROWED_BODY_CAP')
 return dict(status='EXACT_TERMINAL_PUBLIC_FILES_READ_BACK',authority='NONE',role=cfg['role'],archive=files['ARTIFACT.zip'],files=files,original_acceptance=False)
def record_action(configuration_path,action,cursor=None,descriptor=None):
 root,cfg,raw=configuration(configuration_path);m=types.ModuleType('fixed_channel_reader');m.__file__=str(root/'record_transport.py');exec(compile(read(root/'record_transport.py'),m.__file__,'exec'),m.__dict__)
 if action=='drain':return m.drain(cfg,raw,cursor)
 return m.respond(cfg,raw,cursor,descriptor)
def main():
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
 a=s.add_parser('install');a.add_argument('bundle',type=Path);a.add_argument('destination',type=Path)
 a=s.add_parser('configure');a.add_argument('root',type=Path);a.add_argument('event',type=Path);a.add_argument('role');a.add_argument('turn');a.add_argument('source_author')
 for action in ('run','note','readback','drain','respond'):
  a=s.add_parser(action);a.add_argument('configuration',type=Path)
  if action=='run':a.add_argument('admission',type=Path)
  if action=='note':a.add_argument('note_base64')
  if action in ('drain','respond'):a.add_argument('cursor',type=int)
  if action=='respond':a.add_argument('descriptor_base64')
 a=p.parse_args()
 if a.action=='install':v=install(a.bundle,a.destination)
 elif a.action=='configure':v=configure(a.root,a.event,a.role,a.turn,a.source_author)
 elif a.action=='run':return launch(a.configuration,a.admission)
 elif a.action=='note':v=note(a.configuration,base64.b64decode(a.note_base64,validate=True))
 elif a.action=='drain':v=record_action(a.configuration,'drain',a.cursor)
 elif a.action=='respond':v=record_action(a.configuration,'respond',a.cursor,base64.b64decode(a.descriptor_base64,validate=True))
 else:v=readback(a.configuration)
 print(encode(v).decode(),end='')
if __name__=='__main__':
 try:main()
 except BaseException:print('{"status":"UNKNOWN_NO_RETRY","authority":"NONE"}');raise SystemExit(1)
