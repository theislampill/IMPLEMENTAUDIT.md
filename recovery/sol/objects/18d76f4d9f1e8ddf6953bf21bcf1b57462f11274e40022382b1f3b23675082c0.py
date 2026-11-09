"""Source-only maintained composition using a pinned byte-view on Windows.

The original POSIX reader is not executed or qualified by this adapter.  All
inputs are verified and cached before author code runs. Only a fresh owned
output tree may be written; process/network/ctypes operations are refused.
Historical issuer bodies are consumed as data, never as a new native grant.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types
from datetime import datetime, timezone

assert len(sys.argv)==4
stage,actual_body_path,expected_body_sha=sys.argv[1:]
assert stage in ('bind-carrier','finish') and len(expected_body_sha)==64
ROOT = Path(__file__).resolve().parent
RECEIVED = ROOT / 'received'
OUT = ROOT / ('current04-'+stage+'-01')
H = lambda b: hashlib.sha256(b).hexdigest()
DESC = lambda b: dict(bytes=len(b), sha256=H(b))
MARK = lambda s: (s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_nlink)

def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'))+'\n').encode()

def checked(path, expected):
    st = path.lstat()
    assert stat.S_ISREG(st.st_mode) and not path.is_symlink(), path.name
    raw = path.read_bytes()
    assert DESC(raw) == expected, path.name
    assert MARK(path.lstat()) == MARK(st), path.name
    return raw

# Pin every recovered carrier body, not just its manifest file.
receipt = json.loads((ROOT/'CARRIER_BYTE_RECEIVING.json').read_bytes())
assert receipt['seal_sha256'] == 'f49edeb2886dc90c43978301a4440826349e097a5a76b33b6f93df5a28f0a6a1'
cache = {}
for row in receipt['files']:
    name = row['member']
    cache[name] = checked(RECEIVED/name, {k:row[k] for k in ('bytes','sha256')})
assert len(cache) == 374
assert H(cache['SEAL.json']) == receipt['seal_sha256']
recovery_raw = (ROOT/'role-input-recovery/RECEIPT.json').read_bytes()
assert H(recovery_raw) == 'a1028ddf529c17b7db465acd4298b8434db20b7cffe0924ade5875ac84425e2c'
recovery = json.loads(recovery_raw)
retained = {}
for row in recovery['rows']:
    retained[row['required_name']] = checked(Path(row['destination']),
        dict(bytes=row['required_bytes'], sha256=row['required_sha256']))
assert len(retained)==7 and sum(map(len,retained.values()))==249986
overlay = {}
for name, size, digest in (
    ('operation.py',23009,'458ce32d996272a4049034bc372cea61b8870a6f76d6a30f3e819093b57c774d'),
    ('run.py',152906,'a369f5a0f9693d9cc1127e75db7476e2e49b4af6e6059cf2c6175129a3b09872')):
    overlay[name] = checked(ROOT.parent/'g1/candidate-final'/name, dict(bytes=size,sha256=digest))
assert not OUT.exists()
source_manifest = {n:DESC(b) for n,b in cache.items() if n.startswith('source/author/')}
events = {}

def inside(path, root):
    try:
        return Path(os.path.abspath(path)).is_relative_to(root)
    except (TypeError, ValueError):
        return False

def fence(event, args):
    if (event.startswith(('subprocess.', 'socket.', 'ctypes.')) or
        event in ('os.system','os.exec','os.posix_spawn','os.fork','os.kill','os.killpg',
                  'os.spawn','os.startfile','os.putenv','os.unsetenv')):
        raise PermissionError('SOURCE_ONLY_EFFECT_REFUSED')
    if event == 'open':
        path, mode, flags = args
        if not inside(path, OUT):
            raise PermissionError('NON_OWNED_OPEN_REFUSED')
    if event in ('os.mkdir','os.chmod','os.remove','os.rmdir','os.rename','os.link','os.symlink'):
        if event in ('os.rename','os.link','os.symlink') or not inside(args[0], OUT):
            raise PermissionError('NON_OWNED_MUTATION_REFUSED')
    events[event] = events.get(event,0)+1


ISSUER_ROOT = ROOT.parents[1]/'astra-successor-reconciliation-20261108/g1-current04-issuer'
issuer_raw=(ISSUER_ROOT/'ISSUER_RECEIPT.json').read_bytes()
assert H(issuer_raw)=='0a4ab4df939a1044e996577de2ee72d069365c7dd79eda77bc814c0c7fb3f2a9'
issuer=json.loads(issuer_raw)
assert issuer['actual_issuer']=='01a1953f-a15b-7811-aa72-3538ebb03562'
selection_raw=checked(ISSUER_ROOT/'SELECTION.json',issuer['selection'])
fresh_roles={n:checked(ISSUER_ROOT/'private-roles'/n,pin) for n,pin in issuer['roles'].items()}
assert len(fresh_roles)==4


prior_directory=ROOT/('current04-prepare-01/prepare' if stage=='bind-carrier' else 'current04-bind-carrier-01/bind-carrier')
prior_phase_raw=(prior_directory/'PHASE.json').read_bytes()
prior_phase=json.loads(prior_phase_raw)
assert prior_phase['phase']==('prepare' if stage=='bind-carrier' else 'bind-carrier')
assert prior_phase['authority']=='NONE' and prior_phase['original_awards']==[]
for name,pin in prior_phase['members'].items():
    cache['current04-prior/'+name]=checked(prior_directory/name,pin)
cache['current04-prior/PHASE.json']=prior_phase_raw
actual_path=Path(actual_body_path).resolve(strict=True)
assert actual_path.parent==ISSUER_ROOT.resolve(strict=True)
assert actual_path.name==('CARRIER_ADMISSION.json' if stage=='bind-carrier' else 'BOOTSTRAP_ADMISSION.json')
actual_body=actual_path.read_bytes()
assert len(actual_body)<=16384 and H(actual_body)==expected_body_sha

sys.addaudithook(fence)

# Load exact author algorithms; no generated host/native entry is imported.
loaded = {}
for name in ('workflow','compose','refusal_render','publication'):
    module = types.ModuleType(name)
    module.__file__ = str(RECEIVED/'source/author'/f'{name}.py')
    sys.modules[name] = module
    exec(compile(cache[f'source/author/{name}.py'], module.__file__, 'exec'), module.__dict__)
    loaded[name] = module
C, W, R = loaded['compose'], loaded['workflow'], loaded['refusal_render']

def byte_read(path, limit=64*1024**2):
    path = Path(path)
    try:
        key = path.relative_to(RECEIVED).as_posix()
    except ValueError:
        key = None
    if key in cache:
        raw = cache[key]
        assert len(raw)<=limit
        return raw
    assert inside(path, OUT), 'BYTE_VIEW_SCOPE'
    st = path.lstat()
    assert stat.S_ISREG(st.st_mode) and not path.is_symlink() and st.st_nlink==1
    raw = path.read_bytes()
    assert len(raw)==st.st_size<=limit and MARK(path.lstat())==MARK(st)
    return raw

def byte_population(path):
    prefix = Path(path).relative_to(RECEIVED).as_posix().rstrip('/')+'/'
    result = {n[len(prefix):]:b for n,b in cache.items() if n.startswith(prefix)}
    assert result, 'BYTE_VIEW_EMPTY'
    return result

class ArchivePath(type(Path())):
    def read_text(self, *args, **kwargs):
        assert not args and not kwargs
        return byte_read(self).decode('utf8')

C.read, C.population, R.Path = byte_read, byte_population, ArchivePath



for name,raw in overlay.items():cache['source/templates/core/'+name]=raw
new_template_index={n[len('source/templates/'):]:C.desc(raw) for n,raw in cache.items() if n.startswith('source/templates/')}
assert len(new_template_index)==42
cache['source/inputs/TEMPLATE_INDEX.json']=C.encode(new_template_index)
prior=C.read_phase(RECEIVED/'current04-prior',prior_phase['phase'])
result=C.bind_carrier(prior,actual_body) if stage=='bind-carrier' else C.finish(prior,actual_body)
OUT.mkdir()
phase=C.write_phase(OUT/stage,result,stage)
for name,raw in result.items():
    assert (OUT/stage/name).read_bytes()==raw
    if name.endswith('.py'):ast.parse(raw)
request_name='BOOTSTRAP_ADMISSION_REQUIREMENTS.json' if stage=='bind-carrier' else 'COMPOSITION_RESULT.json'
report=dict(schema='dg16.g1-current04-actual-composition-phase-receiving.v1',utc=datetime.now(timezone.utc).isoformat(),
    stage=stage,authority='SOURCE_COMPOSITION_ONLY_NO_PUBLICATION_OR_NATIVE_EFFECT',
    actual_root_issuer_receipt=DESC(issuer_raw),actual_root_body=DESC(actual_body),body_path=str(actual_path),
    prior_phase=DESC(prior_phase_raw),maintained_algorithm='compose.'+('bind_carrier' if stage=='bind-carrier' else 'finish'),
    result_phase=phase,result_members=len(result),request_name=request_name,request=DESC(result[request_name]),
    original_awards=[],actual_native_or_provider_effects=0,
    public_manifest=DESC(result['PUBLIC_PACKET_MANIFEST.json']),audit_events=events)
raw=(json.dumps(report,indent=2)+'\n').encode()
with (OUT/'PHASE_RECEIPT.json').open('xb') as stream:stream.write(raw)
assert (OUT/'PHASE_RECEIPT.json').read_bytes()==raw
print(json.dumps(dict(stage=stage,receipt=DESC(raw),request_name=request_name,request=report['request'],public_manifest=report['public_manifest'],members=len(result))))
