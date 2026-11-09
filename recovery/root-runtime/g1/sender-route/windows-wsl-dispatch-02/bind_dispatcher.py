"""Offline root-owned binding only. No sender/tool/command invocation."""
import ast,hashlib,json,os,re,stat,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
SOURCE='7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'
TREE='6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e'
def need(v,c):
 if not v:raise ValueError(c)
def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return dict(bytes=len(b),sha256=sha(b))
def read(path):
 path=Path(path);s=path.lstat();need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size<=4*1024**2,'ORDINARY_INPUT')
 mark=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_nlink,x.st_uid,x.st_gid,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  need(mark(os.fstat(fd))==mark(s) and not os.listxattr(fd),'INPUT_OPEN_CHANGED');raw=os.pread(fd,4*1024**2+1,0)
  need(len(raw)==s.st_size and mark(os.fstat(fd))==mark(s) and mark(path.lstat())==mark(s),'INPUT_CHANGED');return raw
 finally:os.close(fd)

def literal(raw,name):
 hits=[n.value for n in ast.parse(raw).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)];need(len(hits)==1,'EXACT_LITERAL');return ast.literal_eval(hits[0])
def derive(selection):
 need(type(selection) is dict and set(selection)=={'entry_path','operation_path','helper_path','python_path','late_sender_receiving_path'},'ROOT_SELECTION_FIELDS')
 for p in selection.values():need(type(p) is str and p.startswith('/') and str(Path(p))==p and '..' not in Path(p).parts,'FIXED_PATH')
 entry=Path(selection['entry_path']);op_path=Path(selection['operation_path']);packet=op_path.parent.parent
 need(op_path==packet/'carrier/PRO_SENDER_OPERATION.json' and packet.name=='packet' and entry==packet.parent/'root_sender_entry.py','FIXED_ROOT_SENDER_LAYOUT')
 need(Path(selection['helper_path']).name=='dispatcher_entry.py','FIXED_HELPER_FILENAME')
 eraw=read(entry);opraw=read(op_path);op=json.loads(opraw);need(encode(op)==opraw and op.get('schema')=='dg16.pro-private-sender-operation.v1','ACTUAL_CANONICAL_OPERATION')
 need(type(op['issued_unix_ms']) is int and type(op['expires_unix_ms']) is int and 0<=op['issued_unix_ms']<op['expires_unix_ms']<=op['issued_unix_ms']+600000,'BOUNDED_OPERATION_INTERVAL')
 need(literal(eraw,'ENTRY_STATE')=='REVIEWED_EXACT_ROOT_SENDER_ENTRY' and literal(eraw,'FIXED_PACKET_DIRECTORY')==str(packet) and literal(eraw,'LOADER_DESCRIPTOR')==desc(read(packet/'carrier/carrier_loader.py')),'ACTUAL_LATE_ENTRY_BINDING')
 root_broker=read(packet/'carrier/tool_broker.py');need(desc(root_broker)=={'bytes': 21952, 'sha256': '827d4c32a2d5be3d48bdc370fdfe3df763cb7b8792421092294e3e9c65c5fbed'},'EXACT_ARTIFACT_LIST_BROKER_REQUIRED')
 need(literal(read(packet/'carrier/sender_policy.py'),'PROVIDER_PROFILE')=='ROOT_SUPPORTED_GITHUB_FETCH_ARTIFACT_LIST_FILE_BROKER_V2' and json.loads(read(packet/'carrier/PRO_SENDER_COMPOSITION.json'))['provider_profile']=='ROOT_SUPPORTED_GITHUB_FETCH_ARTIFACT_LIST_FILE_BROKER_V2','ROOT_ONLY_LISTING_PROFILE_REQUIRED')
 need(literal(read(packet/'carrier/carrier_loader.py'),'MODULE_PINS')['tool_broker']==desc(root_broker),'BROKER_LOADER_PIN_REQUIRED')
 ctx=op['context'];need(set(ctx)=={'repository','branch','workflow_commit','workflow_path','run_id','run_attempt','job_name'} and ctx['repository']=='theislampill/IMPLEMENTAUDIT.md' and ctx['workflow_path']=='.github/workflows/dg16-r5-g1-hosted-episode.yml' and ctx['job_name']=='qualify' and type(ctx['run_attempt']) is int and ctx['run_attempt']==1 and re.fullmatch('[1-9][0-9]{0,19}',ctx['run_id']) and re.fullmatch('[0-9a-f]{40}',ctx['workflow_commit']),'ACTUAL_CONTEXT')
 need(op['source_commit']==SOURCE and op['source_tree']==TREE and op['original_awards']==[] and type(op['sender_uid']) is int and op['sender_uid']>0 and type(op['sender_gid']) is int and op['sender_gid']>=0,'ACTUAL_SELECTED_SOURCE_IDENTITY')
 journal=str(packet.parent/('dg16-root-tool-dispatch-'+ctx['run_id']+'-a1'))
 limits=dict(journal_bytes=8*1024**2,journal_entries=128,tool_result_bytes=4*1024**2,chunk_bytes=49152,metadata_reads=18)
 b=dict(schema='dg16.fixed-root-supported-tool-dispatcher.v2',state='ACTUAL_ROOT_ADMITTED_LATE_SENDER_DISPATCH',entry_path=str(entry),entry=desc(eraw),operation_path=str(op_path),operation=desc(opraw),context=ctx,source_commit=SOURCE,source_tree=TREE,carrier_binding_sha256=op['carrier_binding_sha256'],input_index_sha256=op['input_index_sha256'],nonce=op['nonce'],sender_uid=op['sender_uid'],sender_gid=op['sender_gid'],journal_path=journal,admission=None,limits=limits,original_awards=[])
 expected=dict(schema='dg16.root-supported-tool-dispatch-admission.v1',issuer='R5_ROOT_GOVERNOR',operation='ONE_SEQUENTIAL_18_FIXED_READ_DISPATCH_ARTIFACT_LIST_V2',entry_path=b['entry_path'],entry=b['entry'],operation_body=b['operation'],context=ctx,source_commit=SOURCE,source_tree=TREE,carrier_binding_sha256=b['carrier_binding_sha256'],input_index_sha256=b['input_index_sha256'],nonce=b['nonce'],sender_uid=b['sender_uid'],sender_gid=b['sender_gid'],journal_path=journal,limits=limits,automatic_retry=False,crypto_or_native_effect_grant=False,original_awards=[])
 # The actual root late-sender receiving is retained as a separate exact input;
 # a hash is not substituted for its provenance or a new effect decision.
 evidence=dict(path=selection['late_sender_receiving_path'],**desc(read(Path(selection['late_sender_receiving_path']))))
 return b,expected,evidence

def bind(selection,admission_raw):
 b,expected,evidence=derive(selection);need(json.loads(admission_raw)==expected and admission_raw==encode(expected),'ACTUAL_DISPATCHER_ADMISSION_REQUIRED');b['admission']=desc(admission_raw);braw=encode(b)
 need(selection['python_path']=='/usr/bin/python3','WSL_SELECTED_INTERPRETER')
 helper=read(BASE/'dispatcher_entry.py');old=b'BINDING_SHA256=None';need(helper.count(old)==1,'TEMPLATE_BINDING');helper=helper.replace(old,('BINDING_SHA256='+repr(sha(braw))).encode());compile(helper,'dispatcher_entry.py','exec')
 js=read(BASE/'dispatch.js').decode();need(js.count('const HELPER_PATH = null;')==1 and js.count('const HELPER_SHA256 = null;')==1 and js.count('const PYTHON = "/usr/local/bin/python3";')==1,'JS_TEMPLATE_BINDING')
 js=js.replace('const HELPER_PATH = null;','const HELPER_PATH = '+json.dumps(selection['helper_path'])+';').replace('const HELPER_SHA256 = null;','const HELPER_SHA256 = '+json.dumps(sha(helper))+';').replace('const PYTHON = "/usr/local/bin/python3";','const PYTHON = '+json.dumps(selection['python_path'])+';')
 need(js.count('const OP_EXPIRES_UNIX_MS = null;')==1,'DISPATCH_EXPIRY_PLACEHOLDER')
 opraw=read(Path(b['operation_path']));need(desc(opraw)==b['operation'],'WSL_OPERATION_CHANGED')
 js=js.replace('const OP_EXPIRES_UNIX_MS = null;', 'const OP_EXPIRES_UNIX_MS = '+str(json.loads(opraw)['expires_unix_ms'])+';')
 out={'dispatcher_entry.py':helper,'dispatch.js':js.encode(),'DISPATCHER_BINDING.json':braw,'DISPATCHER_ADMISSION.json':admission_raw,'ROOT_LATE_RECEIVING.json':read(Path(selection['late_sender_receiving_path']))}
 out['INSTALL_MANIFEST.json']=encode(dict(schema='dg16.fixed-dispatcher-install-manifest.v1',authority='NONE',helper_path=selection['helper_path'],owner_uid=b['sender_uid'],owner_gid=b['sender_gid'],directory_mode=0o700,file_mode=0o400,members={n:desc(raw) for n,raw in out.items()},actual_late_receiving=evidence,actual_execution='ROOT_ONLY_AFTER_SEPARATE_CURRENTNESS_AND_ADMISSION',original_awards=[]))
 return out

def main():
 need(len(sys.argv) in (4,5),'USAGE_REQUIREMENTS_OR_BIND');mode=sys.argv[1];selection=json.loads(read(Path(sys.argv[2])));out=Path(sys.argv[-1]);need(not out.exists(),'FRESH_OUTPUT_REQUIRED')
 if mode=='requirements' and len(sys.argv)==4:
  _,expected,evidence=derive(selection);files={'DISPATCHER_ADMISSION_REQUIREMENTS.json':encode(dict(schema='dg16.dispatcher-root-admission-requirements.v1',authority='NONE',actual_admission=False,expected_body=expected,actual_late_receiving=evidence,original_awards=[]))}
 else:need(mode=='bind' and len(sys.argv)==5,'FIXED_BIND_MODE');files=bind(selection,read(Path(sys.argv[3])))
 out.mkdir(mode=0o700)
 for name,raw in files.items():
  with (out/name).open('xb') as f:f.write(raw)
  (out/name).chmod(0o400);need(read(out/name)==raw,'WRITE_READBACK')
 print(json.dumps({n:desc(b) for n,b in files.items()},sort_keys=True))
if __name__=='__main__':main()
