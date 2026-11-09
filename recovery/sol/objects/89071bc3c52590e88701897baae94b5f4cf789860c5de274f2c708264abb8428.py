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

ROOT = Path(__file__).resolve().parent
RECEIVED = ROOT / 'received'
OUT = ROOT / 'current04-prepare-01'
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


# Execute actual maintained prepare against an explicitly revised template
# byte population; derive its exact index rather than bypass templates().
original_template_index=DESC(cache['source/inputs/TEMPLATE_INDEX.json'])
for name,raw in overlay.items():cache['source/templates/core/'+name]=raw
new_template_index={n[len('source/templates/'):]:C.desc(raw) for n,raw in cache.items() if n.startswith('source/templates/')}
assert len(new_template_index)==42
cache['source/inputs/TEMPLATE_INDEX.json']=C.encode(new_template_index)
private=dict(retained,**fresh_roles)
assert set(private)==set(C.RETAINED)|set(C.PLACEMENT)|set(C.ROLES.values())
selection=C.parse(selection_raw)
assert selection['branch']=='pro/dg16-g1-original-g3-04-20261109'
prepared=C.prepare(selection,private)
prefix='tree/'+W.CORE+'/'
core={n[len(prefix):]:raw for n,raw in prepared.items() if n.startswith(prefix)}
for name,digest in C.literal(core['run.py'],'MODULE_PINS').items():assert H(core[name+'.py'])==digest
for name,digest in C.literal(core['run.py'],'G3_DATA_PINS').items():assert H(core[name])==digest
assert core['operation.py']==overlay['operation.py']
assert C.literal(core['run.py'],'BRANCH')==selection['branch']
assert C.literal(core['g3_receiving.py'],'JOB_BRANCH')==selection['branch']
assert C.literal(core['g3_receiving.py'],'CONTROL_BRANCH')==selection['g3_control_branch']
assert C.parse(prepared['CARRIER_ADMISSION_REQUIREMENTS.json'])['actual_admission'] is False
OUT.mkdir()
phase=C.write_phase(OUT/'prepare',prepared,'prepare')
# Root requested isolated private source inputs, never part of public tree.
private_root=OUT/'private-inputs';private_root.mkdir()
for name,raw in private.items():
    target=private_root/name;target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as stream:stream.write(raw)
    assert target.read_bytes()==raw
with (OUT/'REVISED_TEMPLATE_INDEX.json').open('xb') as stream:stream.write(cache['source/inputs/TEMPLATE_INDEX.json'])
request=prepared['CARRIER_ADMISSION_REQUIREMENTS.json']
report=dict(schema='dg16.g1-current04-actual-prepare-receiving.v1',utc=datetime.now(timezone.utc).isoformat(),
    authority='SOURCE_COMPOSITION_ONLY_NO_PUBLICATION_OR_NATIVE_EFFECT',actual_root_issuer_receipt=DESC(issuer_raw),
    actual_selection=DESC(selection_raw),actual_four_roles={n:DESC(raw) for n,raw in fresh_roles.items()},
    retained_seven={n:DESC(raw) for n,raw in retained.items()},private_source_population=len(private),
    windows_copies_not_linux_custody=True,original_template_index=original_template_index,
    revised_template_index=DESC(cache['source/inputs/TEMPLATE_INDEX.json']),
    actual_maintained_algorithms=['compose.templates','compose.role_check','compose.prepare','compose.core_bind','workflow.render','compose.write_phase'],
    prepare_phase=phase,prepare_members=len(prepared),run=DESC(core['run.py']),operation=DESC(core['operation.py']),
    carrier_requirements=DESC(request),fresh_original_g3_roles='ACTUAL_ASSIGNMENT_REQUIRED_BEFORE_NATIVE_ADMISSION',
    actual_native_or_provider_effects=0,original_awards=[],audit_events=events)
raw=(json.dumps(report,indent=2)+'\n').encode()
with (OUT/'PREPARE_RECEIPT.json').open('xb') as stream:stream.write(raw)
assert (OUT/'PREPARE_RECEIPT.json').read_bytes()==raw
print(json.dumps(dict(receipt=DESC(raw),carrier_requirements=DESC(request),run=DESC(core['run.py']),members=len(prepared))))
