"""Bounded local source generation/controls; no hosted/native/private operation."""
import argparse
import ast
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import sys
import types
import zipfile
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'selection-controls-01'
BASE=ROOT.parent
REPO=BASE.parent.parent
H=lambda b:hashlib.sha256(b).hexdigest()
D=lambda b:dict(bytes=len(b),sha256=H(b))
MARK=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_nlink)

def read_owned(p,maximum=16*1024**2):
    s=p.lstat();assert stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_size<=maximum
    raw=p.read_bytes();assert MARK(p.lstat())==MARK(s) and len(raw)==s.st_size;return raw

archive=Path('C:/Users/theis/Downloads/G2_CURRENT03_SOURCE_CANDIDATE_20261107.zip')
archive_raw=read_owned(archive)
assert D(archive_raw)==dict(bytes=2537258,sha256='2d494416aed0a77d60c28ea47dc9e1cc9411fed9271b4d844aae17c453be4fc0')
with zipfile.ZipFile(io.BytesIO(archive_raw)) as z:
    assert len(z.namelist())==len(set(z.namelist()))==255
    seal=json.loads(z.read('packet/SEAL.json'));packet={}
    assert len(seal['members'])==219
    for row in seal['members']:
        n=row['path'];assert not n.startswith('/') and '..' not in Path(n).parts and '\\' not in n
        info=z.getinfo('packet/'+n);assert not info.is_dir() and info.file_size==row['bytes'] and info.file_size<=4*1024**2
        raw=z.read(info);assert D(raw)=={k:row[k] for k in ('bytes','sha256')};packet[n]=raw
    assert len(packet)==219 and sum(map(len,packet.values()))==9200297
host_root=REPO/'plans/astra-successor-reconciliation-20261108/g2-direct-openssl/source'
host_names=('CAPTURE_DIAGNOSTIC_CATALOG.json','CODE_MANIFEST.json','HOST_COMPONENT_SEAL.json','bound_child.py',
 'capture_evidence.py','fs_carrier.py','fs_command.py','fs_io.py','fs_protocol.py','fs_runner.py','fs_transport.py',
 'full_g2_hooks.py','protected_bridge.py','protected_preflight.py')
host={n:read_owned(host_root/n) for n in host_names}
assert H(host['protected_preflight.py'])=='ae2b291462fc543b5ed0f25401ab50d6792c51c820ff1f40961fbf28a4e595d7'
assert H(host['protected_bridge.py'])=='1f3c8ee0e567ce16edb257019f0a717290706fa557c3752dd25d77b5249f59d0'
witness_root=REPO/'plans/astra-successor-reconciliation-20261108/direct-encrypt-qualification-01'
locations=dict(root=witness_root/'ASTRA_MAXIMUM_ROOT_RECEIVING.json',public=witness_root/'ACTUAL_PUBLIC_DELIVERY.json',
 provider=witness_root/'PROVIDER_RECEIVING.json',
 independent=BASE/'g1-current03-recovered/g2-public-receiving/FINAL.json',
 source_root=host_root.parent/'ASTRA_SOURCE_RECEIVING.json')
records={n:read_owned(p) for n,p in locations.items()}
extension=read_owned(ROOT/'source/direct_host_profile_v2.py')
assert not OUT.exists()
events={}

def inside(path):
    try:return Path(os.path.abspath(path)).is_relative_to(OUT)
    except (TypeError,ValueError):return False

def fence(event,args):
    if event.startswith(('subprocess.','socket.','ctypes.')) or event in (
      'os.system','os.exec','os.posix_spawn','os.fork','os.kill','os.killpg','os.spawn','os.startfile','os.putenv','os.unsetenv'):
        raise PermissionError('SOURCE_ONLY_EFFECT_REFUSED')
    if event=='open' and not inside(args[0]):raise PermissionError('NON_OWNED_OPEN_REFUSED')
    if event in ('os.mkdir','os.chmod','os.remove','os.rmdir','os.rename','os.link','os.symlink'):
        if event in ('os.rename','os.link','os.symlink') or not inside(args[0]):raise PermissionError('NON_OWNED_MUTATION_REFUSED')
    events[event]=events.get(event,0)+1

sys.addaudithook(fence)
M=types.ModuleType('direct_host_profile');M.__file__=str(ROOT/'source/direct_host_profile_v2.py')
exec(compile(extension,M.__file__,'exec'),M.__dict__)

public,receiver,requirements,proof=M.compose(packet,host,records)
assert proof['host_source_bound'] is False and proof['final_public_receiver_bound'] is False
source_expected=M.selection_expected('pro/dg16-source-fixture-not-an-adoption','pro/dg16-source-control-fixture-not-an-adoption',M.validate_witness(records))
fixture=M.encode(source_expected)
bound_public,bound_receiver,_,bound_proof=M.compose(packet,host,records,fixture)
assert bound_proof['host_source_bound'] is True and bound_proof['final_public_receiver_bound'] is False
assert b'FINAL_COMPOSITION_READY = True' in bound_public[M.PREFIX+'run.py']
assert b'BOUND = True' in bound_public[M.PREFIX+'protected_bridge.py']
assert b'RUNTIME_BINDING_SHA=None' in bound_receiver['public_receiver.py']
assert b'BINDING_SHA=None' in bound_receiver['public_receiver.py']
for name,pin in json.loads(packet['inputs/capacity_r1/CODE_MANIFEST.json'])['members'].items():
 assert bound_receiver['component/'+name]==packet['inputs/capacity_r1/'+name]
changed=copy.deepcopy(source_expected);changed['effect_grant']=True
try:M.compose(packet,host,records,M.encode(changed))
except ValueError as e:assert str(e)=='ACTUAL_HOST_SELECTION_REQUIRED'
else:raise AssertionError('EFFECT_FLAG_ACCEPTED')
for name,raw in bound_public.items():
 if name.endswith('.py'):ast.parse(raw)
rt=ast.parse(bound_public[M.PREFIX+'run.py']);lit=lambda n:ast.literal_eval(next(x.value for x in rt.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id==n for y in x.targets)))
assert lit('PROTECTED_BRIDGE_SHA')==H(bound_public[M.PREFIX+'protected_bridge.py'])
assert bound_public[M.WORKFLOW].count(H(bound_public[M.PREFIX+'run.py']).encode())==20
root_template=M.parse(bound_receiver['ROOT_BINDING_TEMPLATE.json'])
assert root_template['actual_maximum_qualification_received'] is False and root_template['session'] is None
OUT.mkdir()
report=dict(schema='dg16.direct-host-source-selection-controls.v1',utc=datetime.now(timezone.utc).isoformat(),
 source_extension=D(extension),controls=5,result='PASS_BOUNDED_PURE_SOURCE_SELECTION_AND_CHAIN_CONTROLS',
 fixtures='IN_MEMORY_SYNTHETIC_DATA_NOT_ACTUAL_ROOT_ISSUANCE_OR_ADOPTION',
 actual_host_adoption_supplied=False,actual_final_public_receiver=False,actual_private_role=False,
 output_candidate_written=False,actual_hosted_native_crypto_or_key_effects=0,
 cases=['unboundsource','selection-boundsource_chain20pins','receiverstaysunboundandprivateunchanged','effectgrantrefusal','allpythonAST'],original_awards=[])
raw=(json.dumps(report,indent=2)+'\n').encode()
with (OUT/'RECEIPT.json').open('xb') as f:f.write(raw)
assert (OUT/'RECEIPT.json').read_bytes()==raw
print(json.dumps(D(raw)))
