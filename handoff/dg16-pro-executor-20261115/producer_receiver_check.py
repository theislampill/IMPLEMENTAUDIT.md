#!/usr/bin/env python3
"""Feed actual pinned producers through the unchanged G221 receiving chain.

This is deterministic source qualification, never a hosted G2 award. Supply
stdout from both actual producers at product commit 205aeab7; their original
temporary directories must still exist. Capture and normalization owners are
loaded unchanged and by their published source identities.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
PRODUCT = '205aeab7c93299b0666b261485ab5658d8e183de'
REPO = Path(__file__).resolve().parents[2]
Q = REPO / 'qualification/dg16-r5-full-g2'
OLD = REPO / 'handoff/dg16-g221-root-execution-inputs/g220-custody/candidate-e76-source-01/candidate/public/qualification/dg16-r5-full-g2'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--product', type=Path, required=True)
    parser.add_argument('--durability', type=Path, required=True)
    parser.add_argument('--loader', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.product.resolve(strict=True)
    assert subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() == PRODUCT
    assert not args.output.exists(), 'FRESH_OUTPUT_REQUIRED'
    args.output.mkdir(mode=0o700)
    E = load('pro_exact_evidence', Q / 'full_evidence.py')
    P = load('pro_exact_pending', Q / 'pending_relation.py')
    O = load('pro_g220_pending', OLD / 'pending_relation.py')
    driver = load('pro_exact_pair_driver', Q / 'pair_driver.py')
    owner = driver.load_owner(source)
    profile = E.strict((Q / 'OUTPUT_ROLES.json').read_bytes())
    manifest = E.strict((Q / 'SOURCE_MANIFEST.json').read_bytes())
    peers = [E.strict((source / 'source-peers' / group / 'SOURCE_MANIFEST.json').read_bytes())
             for group in ('native-runtime', 'route-graph')]
    raw = args.durability.read_bytes() + args.loader.read_bytes()
    capture = args.output / 'capture'
    E.capture_declared(raw, capture, owner, complete=True)
    received, physical = E.receive_declared(raw, capture, owner)
    checks = []

    def check(name, action, refusal=None):
        try:
            value = action()
        except Exception as error:
            if refusal is None or str(error) != refusal:
                raise AssertionError(name + ': unexpected ' + type(error).__name__ + ': ' + str(error)) from error
            checks.append({'name': name, 'result': 'EXPECTED_REFUSAL', 'reason': str(error)})
            return
        assert refusal is None, name + ': invalid input accepted'
        checks.append({'name': name, 'result': 'PASS'})
        return value

    summaries = {}
    for role in E.ROLES:
        item = received[role]
        root = item['root']
        token = '<' + role.upper() + '_ARTIFACT_ROOT>'
        records = [E.strict(row) for row in item['files']['process-records.jsonl'].splitlines()]
        # The authentic producer re-enters python3, while the unchanged pair
        # driver passes runtime / 'python' to full.receive (pair_driver.py:471).
        # Preserve that real cross-interface distinction in this rehearsal.
        runtime = str(Path(records[0]['command'][0]).with_name('python'))
        assert Path(runtime).is_file(), 'REAL_PAIR_RUNTIME_INTERPRETER_REQUIRED'
        normalize = lambda receiver, value: receiver.normalize(value, role, profile, manifest, peers, E,
                                                               source=str(source), runtime_python=runtime)
        value = check(role + ':complete-actual-capture-and-normalize', lambda: normalize(P, item))
        summaries[role] = value[1]
        check(role + ':historical-receiver-refuses', lambda: normalize(O, item),
              'PENDING_CONTROL_POPULATION' if role == 'pending_durability' else 'PENDING_COMMAND_SHAPE')
        # Every real argv row, rather than a hand-written representative.
        for row in records:
            P.command(row, root, token, str(source), runtime)
        checks.append({'name': role + ':all-real-command-rows', 'result': 'PASS', 'rows': len(records)})
        key = 'control_names' if role == 'pending_durability' else 'controls'
        original = item['report'][key]
        mutations = {
            'missing': original[:-1],
            'extra': original + ['unexpected-valid-looking-control'],
            'reordered': original[1:] + original[:1],
            'renamed': ['different-name'] + original[1:],
            'case-changed': [original[0].upper()] + original[1:],
            'other-role': P.CONTROL_NAMES['pending_loader' if role == 'pending_durability' else 'pending_durability'],
        }
        for name, names in mutations.items():
            changed = copy.deepcopy(item)
            changed['report'][key] = names
            if role == 'pending_durability':
                changed['report']['controls'] = len(names)
            changed['files']['report.json'] = P.encoded(changed['report'], indent=2)
            check(role + ':reject-' + name, lambda c=changed: normalize(P, c), 'PENDING_CONTROL_POPULATION')
        for alias in ['python', 'python3.14', '/usr/bin/python3', 'python3']:
            changed = copy.deepcopy(records[0])
            changed['command'][0] = (runtime.rsplit('/', 1)[0] + '/' + alias
                                     if alias in ('python', 'python3.14') else alias)
            check(role + ':reject-interpreter-' + alias,
                  lambda c=changed: P.command(c, root, token, str(source), runtime), 'PENDING_COMMAND_SHAPE')

    # The genuine producer cannot be detached from its captured bytes.
    check('capture:reject-changed-stdout', lambda: E.receive_declared(raw + b' ', capture, owner),
          'EXTERNAL_CAPTURE_ENVELOPE')
    # A separate disposable capture is deliberately invalidated; preserve the positive capture.
    mutant = args.output / 'capture-mutated'
    E.capture_declared(raw, mutant, owner, complete=True)
    path = mutant / 'pending_durability/report.json'
    path.write_bytes(path.read_bytes() + b' ')
    check('capture:reject-altered-retained-producer-file', lambda: E.receive_declared(raw, mutant, owner),
          'EXTERNAL_PHYSICAL_OR_BYTE_READBACK')
    # Final untouched positive readback after the adversarial pass.
    E.receive_declared(raw, capture, owner)
    result = {'scope': 'ACTUAL_PRODUCER_CAPTURE_RECEIVE_NORMALIZE_SOURCE_QUALIFICATION_ONLY',
              'original_acceptance': False, 'full_119_pair_executed': False,
              'product_commit': PRODUCT, 'product_tree': profile['source_tree'],
              'source_pins': {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in [Q / 'full_evidence.py', Q / 'pending_relation.py',
                                        Q / 'pair_driver.py', Q / 'OUTPUT_ROLES.json', Q / 'SOURCE_MANIFEST.json']},
              'producer_stdout': {name: E.desc(path.read_bytes()) for name, path in
                                  [('durability', args.durability), ('loader', args.loader)]},
              'receiving': physical, 'summaries': summaries, 'checks': checks,
              'check_count': len(checks), 'failures': 0}
    (args.output / 'RESULT.json').write_bytes(E.encode(result, indent=2))
    print(json.dumps({'checks': len(checks), 'failures': 0,
                      'process_rows': sum(x['processes'] for x in summaries.values()),
                      'roles': list(summaries), 'scope': result['scope'],
                      'result_path': str(args.output / 'RESULT.json')}, sort_keys=True))


if __name__ == '__main__':
    main()
