#!/usr/bin/env python3
"""Exact source-profile composition controls; no authentic host admission.

The default exercises this checkout. --source-root selects an independently
materialized, immutable published-source composition for the same controls.
It never supplies source pins or replaces a production acceptance predicate.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile


ROOT = Path(__file__).absolute().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def snapshot(root):
    return {str(p.relative_to(root)): (p.stat().st_mode & 0o7777,
            hashlib.sha256(p.read_bytes()).hexdigest())
            for p in sorted(root.rglob('*')) if p.is_file()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, default=ROOT)
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args()
    source = args.source_root.absolute()
    scripts = source / 'skills/implementaudit/scripts'
    graph = load(scripts / 'compile-work-graph.py', 'composition_graph')
    owner, _, _ = graph._native_static_owner_module_v1()
    claim, validate = [(scripts / name).read_bytes()
                       for name in ('claim-run.sh', 'validate-run-root.sh')]
    adapter, sources, adapter_source = graph._native_six_source_transport_v1(owner, claim, validate)
    profile = adapter._source_profile(sources)
    names = tuple(row[0] for row in profile)
    assert names[:2] == ('claim-run.sh', 'validate-run-root.sh')
    assert adapter._sources(owner, sources, scripts)[1]
    checked = []
    for label, bad in (
        ('omitted-member', sources[:-1]),
        ('extra-member', sources + sources[:1]),
        ('reordered-members', sources[1:] + sources[:1]),
        ('changed-buffer', ((sources[0][0], sources[0][1] + b'\n'),) + sources[1:]),
        ('mutable-population', list(sources)),
        ('foreign-path', ((str(source / names[0]), sources[0][1]),) + sources[1:]),
    ):
        try:
            adapter._sources(owner, bad, scripts)
        except adapter.ContinuityTransportError as exc:
            assert exc.code == 'CONTINUITY_TRANSPORT_SOURCE_REFUSED', (label, exc.code)
            checked.append(label)
        else:
            raise AssertionError('unqualified source accepted: ' + label)
    fixture_owner = load(ROOT / 'fixtures/canonical-state-rotation/claim_transaction_test.py',
                         'composition_fixture')
    fixture_owner.POST = scripts
    results = []
    with tempfile.TemporaryDirectory(prefix='work-graph-composition-') as temporary:
        fixture = fixture_owner.Fixture(persistent_repo=Path(temporary) / 'repository')
        try:
            for name in names:
                if not (fixture.scripts / name).exists():
                    shutil.copyfile(scripts / name, fixture.scripts / name)
            for arguments in (('--current-controller',),
                              ('--require-current-continuity', fixture_owner.CONTROLLER),
                              ('--verify-resume-receipt', fixture.receipt)):
                expected = fixture.claim(*arguments)
                assert expected.returncode == 0, expected.stderr.decode()
                before = snapshot(fixture.repo)
                try:
                    observed = adapter.call_readonly_v1(owner, repository=str(fixture.repo),
                                                       sources=sources, arguments=arguments)
                except adapter.ContinuityTransportError as exc:
                    if exc.code not in {'CONTINUITY_TRANSPORT_UNSUPPORTED_HOST',
                                        'CONTINUITY_TRANSPORT_UNAVAILABLE',
                                        'CONTINUITY_TRANSPORT_NAMESPACE_REFUSED'}:
                        raise
                    results.append(dict(command=arguments[0], status='UNSUPPORTED_HOST',
                                        code=exc.code, stderr=exc.stderr.decode('utf-8', 'replace')))
                    assert snapshot(fixture.repo) == before
                    break
                assert (observed['returncode'], observed['stdout'], observed['stderr']) == (
                    expected.returncode, expected.stdout, expected.stderr), observed
                assert tuple(row['name'] for row in observed['closure']['members']) == names
                assert all(row['seals'] == 15 and row['readonly'] and row['links'] == 1
                           for row in observed['closure']['members'])
                received = dict(schema='implementaudit.native-continuity-closure.v1',
                    execution=observed['closure'],
                    transport=dict(path=str(adapter_source[0]), bytes=len(adapter_source[1]),
                        sha256=hashlib.sha256(adapter_source[1]).hexdigest(), mode=adapter_source[2]))
                owner._native_check_continuity_closure_v1(received, fixture.repo,
                    scripts / 'compile-work-graph.py',
                    dict(claim_sha256=hashlib.sha256(claim).hexdigest(),
                         validate_sha256=hashlib.sha256(validate).hexdigest()))
                assert snapshot(fixture.repo) == before, 'readonly composition changed repository bytes'
                results.append(dict(command=arguments[0], status='PASS', closure=observed['closure']))
        finally:
            fixture.close()
    report = dict(scope='CONSTRUCTED_LEGACY_CURRENTNESS_AND_SOURCE_CUSTODY',
                  native_admission='NOT_ESTABLISHED', sources=profile,
                  transport_sha256=hashlib.sha256(adapter_source[1]).hexdigest(),
                  source_controls=checked, commands=results)
    if args.evidence:
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
