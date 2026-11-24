"""Recompute the V03 packet's chained digests bottom-up (no execution of packet code)."""
import hashlib, json, re, sys
from pathlib import Path
root = Path(sys.argv[1]); Q = root / 'qualification/dg16-r5-full-g2'
C, T = '2e72a912136607e464e953c71fc8e2b44d047d92', '192970f5103fc46d3c303a93d775eb83c04d2734'
OC, OT = '51416b2f156b341c4a5f09029e2c6ceb5b30b1e7', '9c3913ceaa95f3f36b0377fe2dba4a302afcba89'
BRANCH = 'engineering/opus-dg16-v03-2e72-20261124'
sha = lambda b: hashlib.sha256(b).hexdigest()
fsha = lambda name: sha((Q / name).read_bytes())
enc = lambda v: (json.dumps(v, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
def setconst(name, consts):
    p = Q / name; s = p.read_bytes().decode()
    for key, value in consts.items():
        pat = re.compile(r'^(%s ?= ?)(\'[^\']*\'|\d+)$' % re.escape(key), re.M)
        assert len(pat.findall(s)) == 1, (name, key)
        s = pat.sub(lambda m: m.group(1) + (repr(value) if isinstance(value, str) else str(value)), s)
    p.write_bytes(s.encode())
out = {}
# 1. RELATION_INPUTS over the relation modules and the three data profiles.
ri = json.loads((Q / 'RELATION_INPUTS.json').read_bytes())
ri['files'] = {n: {'bytes': (Q / n).stat().st_size, 'sha256': fsha(n)} for n in ri['files']}
ri.update(source_commit=C, source_tree=T); (Q / 'RELATION_INPUTS.json').write_bytes(enc(ri))
out['RELATION_INPUTS_SHA'] = fsha('RELATION_INPUTS.json'); out['FULL_RELATION_SHA'] = fsha('full_relation.py')
# 2. POLICY: identity, counts and receiver hashes only; rule text unchanged except the one test-count token.
pol_raw = (Q / 'POLICY.json').read_bytes(); pol = json.loads(pol_raw)
manifest = json.loads((Q / 'SOURCE_MANIFEST.json').read_bytes())
slots = json.loads((Q / 'REPORT_SLOTS.json').read_bytes())
cmd = json.loads(Path(sys.argv[2]).read_bytes())          # command_stream.py output for 2e72
prior = pol.get('successor_rebinding', {})
pol['successor_rebinding'] = {'authority': 'NONE',
    'rule_author': pol['author'],                       # unchanged original rule author (top-level "author")
    'rebinding_author': '/root/opus_dg16', 'delegated_builder': '/root/opus_dg16_subagent',
    'predecessor_policy_sha256': prior.get('predecessor_policy_sha256', sha(pol_raw)),
    'predecessor_source_commit': OC,
    'rule_text_changed': 'unittest_report_diagnostic_elapsed declared-method count token only (2094 to 2113)',
    'count_provenance': 'measured slot population of REPORT_SLOTS ed2a62ec on 2e72a912 by regenerator acdcbeae',
    'scope': 'mechanical rebinding; not an independent review or a Root adoption',
    'requires': 'fresh independent code/policy review and actual Root pre-run adoption'}
fa = pol['full_applicability']
fa.update(command_stream_sha256=cmd['command_stream_sha256'], mapped_nodes=cmd['mapped_nodes'],
          registered_tests=cmd['registered_tests'], registry_sha256=cmd['registry_sha256'],
          source_report_slots=slots['slot_count'], source_selected_tests=sum(s['test_count'] for s in slots['slots']))
for rule in pol['new_rules']:
    rule['proposed_relation'] = rule['proposed_relation'].replace('and2094declaredmethods', 'and%ddeclaredmethods' % fa['source_selected_tests'])
pol.update(source_commit=C, source_tree=T, full_receiver_sha256=out['FULL_RELATION_SHA'], receiver_inputs_sha256=out['RELATION_INPUTS_SHA'])
(Q / 'POLICY.json').write_bytes(enc(pol)); out['POLICY_SHA'] = fsha('POLICY.json')
out['DIAGNOSTICS_SHA'] = fsha('pair_diagnostics.py'); out['CAPTURE_EVIDENCE_SHA'] = fsha('capture_evidence.py')
# 3. pair_driver.
setconst('pair_driver.py', {'OWNER_SHA256': cmd['owner_sha256'], 'SOURCE_COMMIT': C, 'SOURCE_TREE': T,
    'DIAGNOSTICS_SHA': out['DIAGNOSTICS_SHA'], 'FULL_RELATION_SHA': out['FULL_RELATION_SHA'],
    'RELATION_INPUTS_SHA': out['RELATION_INPUTS_SHA'], 'POLICY_SHA': out['POLICY_SHA'],
    'POLICY_CONTROL_SHA': fsha('policy_control.py'), 'CAPTURE_EVIDENCE_SHA': out['CAPTURE_EVIDENCE_SHA'],
    'CHECKOUT_PREPARE_SHA': fsha('checkout_prepare.py')})
out['PAIR_DRIVER_SHA'] = fsha('pair_driver.py')
# 4. run.py (adapter).
setconst('run.py', {'BRANCH': BRANCH, 'SOURCE_COMMIT': C, 'SOURCE_TREE': T, 'UTILITY_SHA': fsha('host_utility.py'),
    'MANIFEST_SHA': fsha('SOURCE_MANIFEST.json'), 'PAIR_DRIVER_SHA': out['PAIR_DRIVER_SHA'], 'DIAGNOSTICS_SHA': out['DIAGNOSTICS_SHA'],
    'FULL_RELATION_SHA': out['FULL_RELATION_SHA'], 'RELATION_INPUTS_SHA': out['RELATION_INPUTS_SHA'], 'POLICY_SHA': out['POLICY_SHA'],
    'POLICY_CONTROL_SHA': fsha('policy_control.py'), 'LIVE_CONTROL_SHA': fsha('live_control.py'),
    'CHECKOUT_PREPARE_SHA': fsha('checkout_prepare.py'), 'CAPTURE_EVIDENCE_SHA': out['CAPTURE_EVIDENCE_SHA']})
s = (Q / 'run.py').read_bytes().decode()
for old, new in ((r"m['file_count']==1785", "m['file_count']==%d" % manifest['file_count']),
                 (r"len(m['members'])==1785", "len(m['members'])==%d" % manifest['file_count']),
                 ("168345951", str(manifest['total_bytes']))):
    if old in s: s = s.replace(old, new)
(Q / 'run.py').write_bytes(s.encode())
out['ADAPTER_SHA'] = fsha('run.py')
# 5. workflow: branch, source ref, parent check, adapter digest.
wf = root / '.github/workflows/dg16-r5-full-g2.yml'; w = wf.read_bytes().decode()
w = re.sub(r"pro/dg16-g2-current-51416-20261120-01|engineering/opus-dg16-v03-2e72-20261124(?!-control)", BRANCH, w)
w = w.replace(OC, C)
w = re.sub(r"'[0-9a-f]{64}'", "'%s'" % out['ADAPTER_SHA'], w)
wf.write_bytes(w.encode()); out['WORKFLOW_SHA'] = sha(wf.read_bytes())
for name in sorted(p.name for p in Q.iterdir()): out['file:' + name] = fsha(name)
print(json.dumps(out, indent=1))
