#!/usr/bin/env python3
"""Prepare disposable public source/configuration for Root's model-side smoke.

Only local files and exact existing public Git objects are read/written. This
does not create an admission, call GitHub, start a sender, or consume G3.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

OPERATOR = 'd76c1e9c22fd816fbc6ddcac0080625b8f087d23'
PREFIX = 'handoff/fable-local-support-20261115/dg16-g132-owner-local/public-operator/'
APPROVED = '301aeecde08ba6f169bc3cd837eae6f6ad068219'
INDEX = '17efb4b30df56a5a97bc3a9a72579478a3b4850a15e544c0e76a1374116056cf'
PINS = {
    'root-final-operators-01/binary_publish_v3.py': 'e6277edd4f97bac470b1762be8cf80d1e4a21fe05f10ef168bc61e83d47599ef',
    'root-final-operators-01/control_process_v3.py': 'acccc8b7b994e83dc05068a1edd98002600eafbcf2c2292767970b2e46856b64',
    'root-final-operators-01/file_readback.py': 'ab938a99ce3971caaa5e740bf4c079e3245cf0893ea358580c3661807104dcb1',
    'dispatcher-templates-02/bind_dispatcher.py': 'c59aa4cd4228cb4c081c191ad3d8b026e17765ef39b069d74de0778de48303ad',
    'dispatcher-templates-02/dispatcher_entry.py': '6841057bd780588688f193e7959a1dda60dca42bbe5ef5995bca14147cb79f73',
    'dispatcher-templates-02/dispatch.js': 'ed48969832fc789dcc8ed3a238f355c43b3908c82b61ba9f835684c56e1a7c68',
}
G3_PIN = 'b85cca1550ff8e7c1c89778180e53a5c70f306f0c8725ba60ef3ccd4bbc3a6ad'


def need(ok, code):
    if not ok:
        raise ValueError(code)


def desc(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def enc(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)+'\n').encode('ascii')


def save(path, raw):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with path.open('xb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    path.chmod(0o400)
    need(path.read_bytes() == raw, 'LOCAL_READBACK')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--branch', required=True)
    parser.add_argument('--parent', required=True)
    parser.add_argument('--controller', required=True)
    parser.add_argument('--continuity-receipt', required=True)
    parser.add_argument('--assignment-ref', required=True)
    parser.add_argument('--run-id', default='43853354399')
    parser.add_argument('--workflow-commit', default='625f310d04cb5b5a1f02901cfdcf3c3815730a5e')
    args = parser.parse_args()
    need(sys.platform == 'linux' and os.getuid() == os.geteuid() > 0, 'CURRENT_NONROOT_LINUX')
    repo, root = args.repo, args.root
    need(repo.is_absolute() and repo.resolve(strict=True) == repo
         and root.is_absolute() and root.parent.resolve(strict=True) == root.parent
         and not os.path.lexists(root), 'FRESH_DISPOSABLE_PATH')
    need(re.fullmatch('engineering/g132-portability-smoke-[a-z0-9-]{1,80}', args.branch)
         and re.fullmatch('[0-9a-f]{40}', args.parent)
         and re.fullmatch('[0-9a-f]{40}', args.workflow_commit)
         and re.fullmatch('[1-9][0-9]{5,19}', args.run_id), 'EXACT_PUBLIC_SMOKE_SELECTION')
    for value in (args.controller, args.continuity_receipt, args.assignment_ref):
        need(value and len(value) <= 4096 and all(32 <= ord(c) < 127 for c in value), 'PUBLIC_ACTOR_SELECTION')
    root.mkdir(mode=0o700)
    upstream = root/'received-public-operator'
    rows = []
    def receive(commit, path, pin, output):
        raw = subprocess.check_output(['git', '-C', str(repo), 'show', commit+':'+path], timeout=45)
        need(desc(raw)['sha256'] == pin, 'EXACT_PUBLIC_GIT_SOURCE')
        save(output, raw)
        rows.append({'commit': commit, 'path': path, 'received_path': str(output), **desc(raw)})
    receive(OPERATOR, PREFIX+'OPERATOR_PINS.json', INDEX, upstream/'OPERATOR_PINS.json')
    index = json.loads((upstream/'OPERATOR_PINS.json').read_bytes())
    for path, pin in PINS.items():
        need(index[path]['sha256'] == pin, 'PUBLISHED_OPERATOR_INDEX')
        receive(OPERATOR, PREFIX+path, pin, upstream/path)
    g3_source = root/'received-approved/g3_receiving.py'
    receive(APPROVED, 'qualification/dg16-r5-g1-hosted-episode/g3_receiving.py', G3_PIN, g3_source)
    journal = root/'operator-journal'
    journal.mkdir(mode=0o700)
    now = time.time_ns()//1000000
    spec = {'schema': 'dg16.pro-functions-operator.v1', 'role': 'public-observation',
        'context': {'repository': 'theislampill/IMPLEMENTAUDIT.md', 'run_id': args.run_id, 'run_attempt': 1,
            'workflow_commit': args.workflow_commit, 'source_commit': 'e76a07b2bae7c945e5a9d529ed8cf9069f4c9064',
            'source_tree': 'ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7',
            'workflow_path': '.github/workflows/dg16-r5-g1-hosted-episode.yml'},
        'actor': {'surface': 'ChatGPT-functions', 'controller': args.controller,
            'continuity_receipt': args.continuity_receipt, 'assignment_ref': args.assignment_ref},
        'operator_source': {'commit': OPERATOR, 'index_sha256': INDEX},
        'issued_ms': now, 'expires_ms': now+590000}
    cfg = {'schema': 'dg16.pro-owner-smoke-configuration.v1', 'fixture_scope': 'SYNTHETIC_TRANSPORT_ONLY_NO_ORIGINAL_INPUTS',
        'root': str(root), 'repo_path': str(repo), 'upstream_root': str(upstream), 'g3_source': str(g3_source),
        'branch': args.branch, 'parent_sha': args.parent, 'spec': spec,
        'sender_fixture_path': str(root/'received-sender-fixture/dispatcher_entry.py')}
    raw = enc(cfg)
    config_path = root/'SMOKE_CONFIGURATION.json'
    save(config_path, raw)
    here = Path(__file__).resolve().parent
    template = (here/'g132_sender_fixture.py').read_bytes()
    placeholder = b'CONFIGURATION_SHA256=None'
    need(template.count(placeholder) == 1, 'EXACT_FIXTURE_CONFIGURATION_SEAM')
    sender_fixture = template.replace(placeholder, ('CONFIGURATION_SHA256='+repr(desc(raw)['sha256'])).encode('ascii'))
    fixture_path = Path(cfg['sender_fixture_path'])
    save(fixture_path, sender_fixture)
    save(fixture_path.with_name('SMOKE_CONFIGURATION.json'), raw)
    def local(path):
        return {'path': str(path), **desc(path.read_bytes())}
    setup = {'configuration': {'path': str(config_path), 'raw': raw.decode('ascii'), **desc(raw)},
        'linux': {'python_path': '/usr/bin/python3', 'helper_path': str(here/'g132_linux_host.py'),
            'helper_sha256': desc((here/'g132_linux_host.py').read_bytes())['sha256'], 'journal_root': str(journal)},
        'bridge': local(here/'g132_operator_bridge.js'), 'owner_runtime': local(here/'g132_owner_runtime.py'),
        'sender_fixture': {'path': str(fixture_path), 'descriptor': desc(sender_fixture)},
        'sender_fixture_template': local(here/'g132_sender_fixture.py'),
        'functions_smoke': local(here/'g132_functions_smoke.js'),
        'codec': local(repo/'qualification/dg16-github-evidence/channel.js'),
        'source_receiving': rows, 'actual_admission': False, 'remote_effects': 0, 'original_awards': []}
    save(root/'LOCAL_SETUP.json', enc(setup))
    print(json.dumps(setup, sort_keys=True, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
