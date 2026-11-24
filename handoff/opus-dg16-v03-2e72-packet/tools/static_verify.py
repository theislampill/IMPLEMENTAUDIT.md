"""Read-only consistency checks of the rebound packet against a disposable 2e72 source copy.
Loads only relation/capture-evidence modules (no run.py, no pair_driver, no verifier run)."""
import hashlib, importlib.util, json, re, sys, types
from pathlib import Path
packet, source = Path(sys.argv[1]), Path(sys.argv[2])
Q = packet / 'qualification/dg16-r5-full-g2'
sha = lambda b: hashlib.sha256(b).hexdigest(); f = lambda n: sha((Q / n).read_bytes())
def consts(name):
    return dict(re.findall(r"^([A-Z_0-9]+) ?= ?'([^']*)'", (Q / name).read_text(), re.M))
ok = []
def check(label, cond): ok.append((label, bool(cond))); print(('PASS ' if cond else 'FAIL ') + label)
run, drv, cap, chk = consts('run.py'), consts('pair_driver.py'), consts('capture_evidence.py'), consts('checkout_prepare.py')
for k, n in [('MANIFEST_SHA', 'SOURCE_MANIFEST.json'), ('PAIR_DRIVER_SHA', 'pair_driver.py'), ('DIAGNOSTICS_SHA', 'pair_diagnostics.py'),
             ('FULL_RELATION_SHA', 'full_relation.py'), ('RELATION_INPUTS_SHA', 'RELATION_INPUTS.json'), ('POLICY_SHA', 'POLICY.json'),
             ('POLICY_CONTROL_SHA', 'policy_control.py'), ('LIVE_CONTROL_SHA', 'live_control.py'), ('CHECKOUT_PREPARE_SHA', 'checkout_prepare.py'),
             ('CAPTURE_EVIDENCE_SHA', 'capture_evidence.py'), ('UTILITY_SHA', 'host_utility.py')]:
    check('run.py ' + k, run[k] == f(n))
for k, n in [('DIAGNOSTICS_SHA', 'pair_diagnostics.py'), ('FULL_RELATION_SHA', 'full_relation.py'), ('RELATION_INPUTS_SHA', 'RELATION_INPUTS.json'),
             ('POLICY_SHA', 'POLICY.json'), ('POLICY_CONTROL_SHA', 'policy_control.py'), ('CAPTURE_EVIDENCE_SHA', 'capture_evidence.py')]:
    check('pair_driver.py ' + k, drv[k] == f(n))
owner_raw = (source / 'scripts/qualify-work-graph-verifier.py').read_bytes()
check('owner pins', drv['OWNER_SHA256'] == cap['OWNER_SHA'] == chk['OWNER_SHA'] == sha(owner_raw))
check('compiler pin', chk['COMPILER_SHA'] == sha((source / 'skills/implementaudit/scripts/compile-work-graph.py').read_bytes()))
check('catalog pin', cap['CATALOG_SHA'] == f('CAPTURE_DIAGNOSTIC_CATALOG.json'))
wf = (packet / '.github/workflows/dg16-r5-full-g2.yml').read_text()
check('workflow adapter digest', set(re.findall(r"'([0-9a-f]{64})'", wf)) == {f('run.py')})
check('workflow source ref', '51416b2f' not in wf and 'ref: ' + run['SOURCE_COMMIT'] in wf and run['BRANCH'] in wf)
pol = json.loads((Q / 'POLICY.json').read_bytes()); ri = json.loads((Q / 'RELATION_INPUTS.json').read_bytes())
check('policy receiver bindings', pol['receiver_inputs_sha256'] == run['RELATION_INPUTS_SHA'] and pol['full_receiver_sha256'] == run['FULL_RELATION_SHA'])
check('relation inputs files', all(ri['files'][n] == {'bytes': (Q / n).stat().st_size, 'sha256': f(n)} for n in ri['files']))
# full_relation.load / source_profiles against the actual 2e72 source.
spec = importlib.util.spec_from_file_location('owner', source / 'scripts/qualify-work-graph-verifier.py')
owner = importlib.util.module_from_spec(spec); sys.modules['owner'] = owner; spec.loader.exec_module(owner)
def loader(name, expected):
    raw = (Q / name).read_bytes(); assert sha(raw) == expected
    m = types.ModuleType('pk_' + name.replace('.', '_')); m.__file__ = str(Q / name); exec(compile(raw, str(Q / name), 'exec'), m.__dict__); return m
full = loader('full_relation.py', run['FULL_RELATION_SHA'])
check('policy/inputs canonical encoding', (Q / 'POLICY.json').read_bytes() == full.encode(pol) and (Q / 'RELATION_INPUTS.json').read_bytes() == full.encode(ri))
relation = full.load(Q, ri, loader, lambda p, limit=None: json.loads(Path(p).read_bytes()))
check('full_relation.load (112/2113, registry pin)', True)
facts, peers = full.source_profiles(source, owner, relation)
check('source_profiles: %d closure/role pins equal actual 2e72 bytes' % len(facts['members']), True)
reg = (source / 'scripts/verify-package.sh').read_bytes()
check('REGISTRY_SHA', full.REGISTRY_SHA == sha(reg) == pol['full_applicability']['registry_sha256'])
# capture_evidence success-path admission against the actual owner.
cev = loader('capture_evidence.py', run['CAPTURE_EVIDENCE_SHA'])
cat = cev.load_catalog(); compiled = cev.compiled_owner(source, cat); cev.admit_owner(owner, compiled)
check('capture_evidence load_catalog/compiled_owner/admit_owner', True)
# manifest vs actual tree (same rules as run.py verify_source, minus .git).
m = json.loads((Q / 'SOURCE_MANIFEST.json').read_bytes())
files = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
check('manifest population == source files', files == {r['path'] for r in m['members']})
check('run.py manifest counts', ("m['file_count']==%d" % m['file_count']) in (Q / 'run.py').read_text() and str(m['total_bytes']) in (Q / 'run.py').read_text())
print('ALL_PASS' if all(c for _, c in ok) else 'SOME_FAIL')
