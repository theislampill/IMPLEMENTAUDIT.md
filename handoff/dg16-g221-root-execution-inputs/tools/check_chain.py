#!/usr/bin/env python3
"""FABLE G221: structural pin-chain check of an author universe (candidate-e76-source-01 + author/).

Every check is a join the original consumers make (pair_driver.relation_context before the decision gate,
run.py module pins, workflow guards, bind_public_successor template/module pins, candidate seal members,
composer candidate pin). Run on the G220 base (must be all-true: proves the checker) and on the regenerated tree.

argv: <universe> <label> <json-out>
"""
import hashlib, json, re, sys
from pathlib import Path

root, label, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
C = root / 'candidate-e76-source-01'; Q = C / 'candidate/public/qualification/dg16-r5-full-g2'
D = C / 'candidate/public/qualification/dg16-r5-full-g2-decisions'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
fsha = lambda path: sha(Path(path).read_bytes())
desc = lambda path: {'bytes': len(Path(path).read_bytes()), 'sha256': fsha(path)}
canon = lambda value: (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
const = lambda text, name: re.search(r"(?m)^%s\s*=\s*'([0-9a-f]{64})'" % name, text).group(1)
results = []


def check(name, ok, detail=None):
    results.append({'check': name, 'ok': bool(ok), 'detail': detail})
    print(f'[{label}] {"PASS" if ok else "FAIL"}  {name}' + (f' :: {json.dumps(detail, sort_keys=True)[:230]}' if detail is not None else ''))


inputs = json.loads((Q / 'RELATION_INPUTS.json').read_bytes()); policy = json.loads((Q / 'POLICY.json').read_bytes())
driver = (Q / 'pair_driver.py').read_text(); run = (Q / 'run.py').read_text()
check('RELATION_INPUTS.files == physical {bytes, sha256} of all 8 relation inputs',
      all(inputs['files'][n] == desc(Q / n) for n in inputs['files']) and len(inputs['files']) == 8,
      {'pending_relation.py': inputs['files']['pending_relation.py']})
check('RELATION_INPUTS.json canonical encoding (full_relation.encode)', (Q / 'RELATION_INPUTS.json').read_bytes() == canon(inputs))
check('pair_driver.RELATION_INPUTS_SHA == sha256(RELATION_INPUTS.json)', const(driver, 'RELATION_INPUTS_SHA') == fsha(Q / 'RELATION_INPUTS.json'), fsha(Q / 'RELATION_INPUTS.json'))
check('POLICY.json canonical encoding; pair_driver.POLICY_SHA == sha256(POLICY.json)',
      (Q / 'POLICY.json').read_bytes() == canon(policy) and const(driver, 'POLICY_SHA') == fsha(Q / 'POLICY.json'), fsha(Q / 'POLICY.json'))
check('POLICY.receiver_inputs_sha256 == RELATION_INPUTS_SHA; POLICY.full_receiver_sha256 == pair_driver.FULL_RELATION_SHA == sha256(full_relation.py)',
      policy['receiver_inputs_sha256'] == fsha(Q / 'RELATION_INPUTS.json') and
      policy['full_receiver_sha256'] == const(driver, 'FULL_RELATION_SHA') == fsha(Q / 'full_relation.py'))
check('POLICY / RELATION_INPUTS source commit + tree', (policy['source_commit'], policy['source_tree'], inputs['source_commit'], inputs['source_tree']) ==
      ('205aeab7c93299b0666b261485ab5658d8e183de', '9ffbaf95080092bf4a45b8772a97ed16068544a7') * 2)
RUN_PINS = {'UTILITY_SHA': 'host_utility.py', 'MANIFEST_SHA': 'SOURCE_MANIFEST.json', 'PAIR_DRIVER_SHA': 'pair_driver.py',
            'DIAGNOSTICS_SHA': 'pair_diagnostics.py', 'FULL_RELATION_SHA': 'full_relation.py', 'RELATION_INPUTS_SHA': 'RELATION_INPUTS.json',
            'POLICY_SHA': 'POLICY.json', 'POLICY_CONTROL_SHA': 'policy_control.py', 'LIVE_CONTROL_SHA': 'live_control.py',
            'CHECKOUT_PREPARE_SHA': 'checkout_prepare.py', 'CAPTURE_EVIDENCE_SHA': 'capture_evidence.py',
            'PROTECTED_BRIDGE_SHA': 'protected_bridge.py', 'CURRENT_HOST_SHA': 'current_host.py', 'NATIVE_INTEGRATION_SHA': 'native_integration.py',
            'NATIVE_PROFILE_SHA': 'native_profile.py', 'NATIVE_ADMISSION_SHA': 'native_admission.py', 'NATIVE_EVIDENCE_IO_SHA': 'evidence_io.py'}
bad = {k: v for k, v in RUN_PINS.items() if const(run, k) != fsha(Q / v)}
check('run.py: %d file pins == physical packet files' % len(RUN_PINS), not bad, bad or None)
check('run.CURRENT_HOST_REQUEST_SHA == sha256(decisions/CURRENT_HOST_QUALIFICATION_REQUEST.json)',
      const(run, 'CURRENT_HOST_REQUEST_SHA') == fsha(D / 'CURRENT_HOST_QUALIFICATION_REQUEST.json'), fsha(D / 'CURRENT_HOST_QUALIFICATION_REQUEST.json'))
request = json.loads((D / 'CURRENT_HOST_QUALIFICATION_REQUEST.json').read_bytes()); b = request['source_bindings']
check('request.source_bindings pair_driver / policy / receiver_inputs / source_manifest == physical',
      (b['pair_driver_sha256'], b['policy_sha256'], b['receiver_inputs_sha256'], b['source_manifest_sha256']) ==
      (fsha(Q / 'pair_driver.py'), fsha(Q / 'POLICY.json'), fsha(Q / 'RELATION_INPUTS.json'), fsha(Q / 'SOURCE_MANIFEST.json')))
workflow = (C / 'candidate/public/.github/workflows/dg16-r5-full-g2.yml').read_text()
literals = re.findall(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])', workflow)
check('workflow: every 64-hex literal == sha256(run.py)', literals and set(literals) == {fsha(Q / 'run.py')}, {'literals': len(literals), 'run.py': fsha(Q / 'run.py')})
manifest = json.loads((Q / 'SOURCE_MANIFEST.json').read_bytes())
members = manifest.get('members') or manifest.get('files')
check('SOURCE_MANIFEST.json untouched: 1766 members / 167023692 bytes; pending_relation.py is not a member',
      fsha(Q / 'SOURCE_MANIFEST.json') == '328bfd9ba1711260d6efa19ed8fcf45651d375e7c3685b9ce50bd03f1c3803ee' and len(members) == 1766 and
      sum(m['bytes'] for m in members) == 167023692 and not any('pending_relation' in m['path'] for m in members),
      {'file_count': manifest.get('file_count'), 'total_bytes': manifest.get('total_bytes'), 'members': len(members)})
template = json.loads((C / 'receiver/BINDING_TEMPLATE.json').read_bytes())
packet = sorted(p.name for p in Q.iterdir())
check('receiver/BINDING_TEMPLATE.modules == physical {bytes, sha256} of all %d packet files' % len(packet),
      sorted(template['modules']) == packet and all(template['modules'][n] == desc(Q / n) for n in packet), {'modules': len(template['modules'])})
root_template = json.loads((C / 'receiver/ROOT_BINDING_TEMPLATE.json').read_bytes())
check('receiver/ROOT_BINDING_TEMPLATE.workflow_sha256 == sha256(workflow)', root_template['workflow_sha256'] == sha(workflow.encode()), root_template['workflow_sha256'])
binder = (root / 'author/bind_public_successor.py').read_text()
check('author/bind_public_successor.TEMPLATE_PINS == {sha256(BINDING_TEMPLATE.json)}',
      re.search(r"TEMPLATE_PINS = \{'([0-9a-f]{64})'\}", binder).group(1) == fsha(C / 'receiver/BINDING_TEMPLATE.json'), fsha(C / 'receiver/BINDING_TEMPLATE.json'))
seal = json.loads((C / 'SEAL.json').read_bytes())
mismatch = [m['path'] for m in seal['members'] if {'bytes': m['bytes'], 'sha256': m['sha256']} != desc(C / m['path'])]
physical = sorted(p.relative_to(C).as_posix() for p in C.rglob('*') if p.is_file() and p.name != 'SEAL.json')
check('candidate SEAL.json: %d members == physical tree, 0 mismatches, no unsealed file' % seal['member_count'],
      not mismatch and seal['member_count'] == len(seal['members']) and sorted(m['path'] for m in seal['members']) == physical, mismatch or None)
for name in ('compose-candidate-bound.py', 'compose-final-bound.py'):
    text = (root / 'author' / name).read_text()
    check('author/%s PINS[candidate] == sha256(candidate SEAL.json)' % name,
          re.search(r"PINS = \{'candidate': '([0-9a-f]{64})'", text).group(1) == fsha(C / 'SEAL.json'), fsha(C / 'SEAL.json'))
out.write_text(json.dumps({'label': label, 'results': results}, indent=1) + '\n')
failed = [r['check'] for r in results if not r['ok']]
print(f'[{label}] SUMMARY checks={len(results)} failed={len(failed)}')
sys.exit(1 if failed else 0)
