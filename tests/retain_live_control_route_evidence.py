"""Retain only bounded public synthetic evidence; exclude Git stores and TLS keys."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat

root = Path(os.environ['G2_ROUTE_EVIDENCE'])
public = Path(os.environ['G2_PUBLIC_EVIDENCE'])
public.mkdir(mode=0o700, exist_ok=False)
summary = {'schema': 'dg16.full-consumer-route-smoke.v1',
           'scope': 'SYNTHETIC_NON_ACCEPTANCE_FULL_CONSUMER_ROUTE',
           'authority': 'NONE', 'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': 1,
           'workflow_commit': os.environ['GITHUB_SHA'],
           'checkout_outcome': os.environ['CHECKOUT_OUTCOME'],
           'preflight_outcome': os.environ['PREFLIGHT_OUTCOME'],
           'suite_outcome': os.environ['SUITE_OUTCOME'],
           'original_acceptance': False, 'full_G2': False, 'M2': False,
           'full_pair_executed': False, 'original_control_replayed': False,
           'genuine_reviewer_or_root_decision_claim': False,
           'protected_G132_effect': False, 'provider_write_by_test': False,
           'automatic_retry': False, 'cases': []}
safe = {'REQUEST.json', 'TEST_SCOPE.json', 'route-result.json',
        'consumed/CONSUMPTION_RESERVED.json', 'consumed/CONTROL_READS.json',
        'consumed/CONTROL.json', 'consumed/INDEPENDENT_REVIEW.json',
        'consumed/ROOT_CONSUMPTION.json'}
members = []


def keep(source, relative):
    assert not source.is_symlink() and stat.S_ISREG(source.stat().st_mode)
    raw = source.read_bytes()
    assert len(raw) <= 131072
    target = public / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    members.append({'path': relative, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    assert len(members) <= 128 and sum(row['bytes'] for row in members) <= 2 * 1024 * 1024


if root.is_dir():
    for case in sorted(root.iterdir()):
        if case.is_dir() and not case.is_symlink() and (case / 'TEST_SCOPE.json').is_file():
            for relative in sorted(safe):
                source = case / relative
                if source.is_file():
                    keep(source, case.name + '/' + relative)
            result = case / 'route-result.json'
            if result.is_file():
                data = json.loads(result.read_text())
                summary['cases'].append({'case': case.name, 'accepted': data['accepted'],
                    'refusal': data['refusal'], 'reservation_present': data['reservation_present'],
                    'capture_count': len(data.get('commands', [])),
                    'all_captures_reaped': all(row.get('cleanup', {}).get('echild') is True
                                             for row in data.get('commands', []))})
for name in ('PREFLIGHT.json', 'SUITE.log'):
    path = root.parent / (root.name + '-' + name)
    if path.is_file():
        keep(path, name)
(public / 'RESULT.json').write_text(json.dumps(summary, sort_keys=True, indent=2) + '\n')
raw = (public / 'RESULT.json').read_bytes()
members.append({'path': 'RESULT.json', 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
(public / 'MANIFEST.json').write_text(json.dumps({'scope': summary['scope'], 'members': members},
                                               sort_keys=True, indent=2) + '\n')
print('DG16_FULL_CONSUMER_ROUTE ' + json.dumps(summary, sort_keys=True, separators=(',', ':')))
