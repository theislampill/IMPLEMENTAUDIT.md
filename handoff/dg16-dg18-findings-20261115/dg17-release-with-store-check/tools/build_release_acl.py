"""Build the proposed driver set with store custody (no authority; nothing is launched).
Base = dg17-next/release/author (read only). Output = dg17-acl/release/author (must not exist).
The operation record binds file paths, so the relocated set gets a new OPERATION_A sha."""
import difflib,hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).absolute().parent;WORK=HERE.parent
BASE=WORK.parent/'dg17-next'/'release'/'author';AUTH=WORK/'release'/'author'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=Path(p).read_bytes();return dict(bytes=len(b),path=str(p),sha256=sha(b))
def dump(op):return (json.dumps(op,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode('utf-8')
before={p.name:sha(p.read_bytes()) for p in sorted(BASE.iterdir())}
AUTH.mkdir(parents=True)
for n in before:
 if n not in ('stage_b.py','OPERATION_A.json','parent_launch_a.py','parent_launch_b.py','bind_stage_b.py'):(AUTH/n).write_bytes((BASE/n).read_bytes())
r=subprocess.run([sys.executable,str(HERE/'make_acl_stage_b.py'),str(BASE/'stage_b.py'),str(AUTH/'stage_b.py')],capture_output=True,text=True);assert r.returncode==0,r.stderr
OLD_B=before['stage_b.py'];NEW_B=sha((AUTH/'stage_b.py').read_bytes());OLD_OP=before['OPERATION_A.json']
def edit(name,pairs):
 t=(BASE/name).read_bytes().decode('utf-8')
 for x,y in pairs:
  assert t.count(x)==1,(name,x);t=t.replace(x,y)
 (AUTH/name).write_bytes(t.encode('utf-8'))
edit('parent_launch_b.py',[(OLD_B,NEW_B)])
raw0=(BASE/'OPERATION_A.json').read_bytes();orig=json.loads(raw0);op=json.loads(raw0);assert dump(orig)==raw0
prefix=str(BASE)+'\\';repinned=[]
for item in op['readset']:
 if item['path'].startswith(prefix):
  name=Path(item['path']).name;assert name not in ('parent_launch_a.py','bind_stage_b.py','OPERATION_A.json')
  item.update(pin(AUTH/name));repinned.append(name)
for key in ['rpc_module','constructor']:
 new=pin(AUTH/Path(op[key]['path']).name);assert new['sha256']==op[key]['sha256'];op[key]=new
op['episode_successor']=orig['episode_successor']+' Further delta (dg17-acl): stage_b.py creates the host-session store directory with an owner-only protected DACL and verifies owner and DACL through advapi32 immediately before step 02-owned-init; the packaged binding owner is unchanged.'
raw=dump(op);assert str(BASE) not in raw.decode('utf-8');(AUTH/'OPERATION_A.json').write_bytes(raw);NEW_OP=sha(raw)
edit('parent_launch_a.py',[(OLD_OP,NEW_OP)]);edit('bind_stage_b.py',[(OLD_OP,NEW_OP)])
# controls
chk=json.loads((AUTH/'OPERATION_A.json').read_bytes());assert dump(chk)==raw
for item in chk['readset']:
 if item['path'].startswith(str(AUTH)+'\\'):
  p=pin(item['path']);assert (p['bytes'],p['sha256'])==(item['bytes'],item['sha256']),item['path']
assert chk['binding_owner']==orig['binding_owner'] and sha(Path(chk['binding_owner']['path']).read_bytes())==chk['binding_owner']['sha256']
assert NEW_B in (AUTH/'parent_launch_b.py').read_text(encoding='utf-8') and OLD_B not in (AUTH/'parent_launch_b.py').read_text(encoding='utf-8')
for n in ['parent_launch_a.py','bind_stage_b.py']:
 t=(AUTH/n).read_text(encoding='utf-8');assert NEW_OP in t and OLD_OP not in t
for n in sorted(p.name for p in AUTH.glob('*.py')):compile((AUTH/n).read_bytes(),n,'exec')
assert {p.name:sha(p.read_bytes()) for p in sorted(BASE.iterdir())}==before,'base set must stay untouched'
changed_keys=sorted(k for k in set(chk)|set(orig) if chk.get(k)!=orig.get(k))
def strip(o):
 o=json.loads(json.dumps(o))
 for item in o['readset']:
  if Path(item['path']).parent in (BASE,AUTH):item.update(path=Path(item['path']).name,bytes=0,sha256='')
 for key in ['rpc_module','constructor']:o[key]['path']=Path(o[key]['path']).name
 o.pop('episode_successor');return o
files={}
for p in sorted(AUTH.iterdir()):
 b=p.read_bytes();o=(BASE/p.name).read_bytes();d=[l for l in difflib.unified_diff(o.decode('utf-8').splitlines(),b.decode('utf-8').splitlines(),lineterm='',n=0) if l[:1] in '+-' and l[:3] not in ('+++','---')]
 files[p.name]=dict(sha256=sha(b),bytes=len(b),previous_sha256=sha(o),changed=b!=o,added_lines=sum(l[0]=='+' for l in d),removed_lines=sum(l[0]=='-' for l in d))
pins=dict(authority='NONE - proposed source only',author_dir=str(AUTH),base_author_dir=str(BASE),operation_A_sha256=NEW_OP,operation_A_bytes=len(raw),previous_operation_A_sha256=OLD_OP,case=chk['case'],stage_a_driver_sha256=files['stage_a.py']['sha256'],stage_b_driver_sha256=NEW_B,previous_stage_b_driver_sha256=OLD_B,parent_launch_a=dict(OP_SHA=NEW_OP),parent_launch_b=dict(DRIVER_SHA=NEW_B),bind_stage_b=dict(A_SHA=NEW_OP),operation_keys_changed=changed_keys,only_author_paths_pins_and_successor_text_changed=strip(chk)==strip(orig),readset_author_items_repinned=sorted(repinned),binding_owner_sha256_unchanged=chk['binding_owner']['sha256'],files=files)
(AUTH.parent/'PINS.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in pins.items() if k!='files'},indent=1));print({k:(v['sha256'][:12],v['changed'],v['added_lines'],v['removed_lines']) for k,v in files.items()})
