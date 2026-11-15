#!/usr/bin/env python3
"""Distinct source review only; no route entrypoint, publication, or native call."""
import ast
import copy
import datetime
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile
import types
import unittest

sys.dont_write_bytecode = True
BASE = Path('/workspace/scratch/0269e6626329')
REPO = BASE / 'm5-source'
PRODUCT = BASE / 'm5-product-205aeab7'
ORIGINAL = BASE / 'm5-source-recovery/original-route-source'
OUT = BASE / 'm5-review'
HANDOFF = REPO / 'handoff/dg16-m5-source-20261115'
PREFIX = 'qualification/dg16-installed-runtime05/'
COMMIT = '21c53ac61f6db57f0bb8ddfdabeb254420e109c2'
TREE = '298bc72039ccf0ec6ed52e85594fe832818e1de1'
PARENT = '07a57141b74b5e7861a3145174582347837d075c'
ORIGINAL_COMMIT = '9493cb25ec976aebb056191ec4eafa086d6b44d6'
SOURCE = '205aeab7c93299b0666b261485ab5658d8e183de'
SOURCE_TREE = '9ffbaf95080092bf4a45b8772a97ed16068544a7'
BRANCH = 'engineering/pro-executor-dg16-m5-source-20261115'
ENV = {**os.environ, 'GIT_OPTIONAL_LOCKS': '0', 'PYTHONDONTWRITEBYTECODE': '1'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def git(repo, *args):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', str(repo), *args], env=ENV)


def describe(path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': sha(data), 'mode': oct(stat.S_IMODE(path.stat().st_mode))}


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def command(label, argv, expected):
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    proc = subprocess.run(argv, cwd=OUT, env=ENV, capture_output=True, timeout=30)
    (OUT / (label + '.stdout.txt')).write_bytes(proc.stdout)
    (OUT / (label + '.stderr.txt')).write_bytes(proc.stderr)
    record = {'argv': argv, 'cwd': str(OUT), 'exit_code': proc.returncode,
              'started_utc': start, 'ended_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'stdout': describe(OUT / (label + '.stdout.txt')), 'stderr': describe(OUT / (label + '.stderr.txt'))}
    dump(label + '.json', record)
    assert proc.returncode == expected, (label, proc.returncode)
    return record


def main():
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    assert git(REPO, 'show', '-s', '--format=%H%n%T%n%P', 'HEAD').decode().splitlines() == [COMMIT, TREE, PARENT]
    assert git(REPO, 'status', '--porcelain', '--untracked-files=all') == b''
    receipt = BASE / 'm5-source-recovery/FROZEN_SOURCE_CANDIDATE_RECEIPT.json'
    assert describe(receipt)['sha256'] == 'e0f50c967114c8da787361a8a8c49f88f53348728ddceacbb8df94a10ecb7d9e'
    manifest_file = HANDOFF / 'SOURCE_PACKET_MANIFEST.json'
    assert describe(manifest_file)['sha256'] == '1068764f35a15d9610e8cf01dda9ea85861546e33da844d17839aac39a40a75c'
    manifest = json.loads(manifest_file.read_text())
    rows = manifest['members']
    assert len(rows) == len({r['path'] for r in rows}) == manifest['files'] == 64
    assert sum(r['bytes'] for r in rows) == manifest['total_bytes'] == 2286337
    for row in rows:
        rel = PurePosixPath(row['path']); path = REPO / row['path']
        assert not rel.is_absolute() and '..' not in rel.parts and not path.is_symlink() and path.is_file()
        assert path.resolve().is_relative_to(REPO)
        assert path.read_bytes() == git(REPO, 'show', COMMIT + ':' + row['path'])
        assert path.stat().st_size == row['bytes'] and sha(path.read_bytes()) == row['sha256']
        assert git(REPO, 'ls-tree', COMMIT, '--', row['path']).decode().split()[0] == row['git_mode']
        assert stat.S_IMODE(path.stat().st_mode) == (0o755 if row['git_mode'] == '100755' else 0o644)
    changes = [line.split('\t') for line in git(REPO, 'diff', '--name-status', PARENT, COMMIT).decode().splitlines()]
    assert len(changes) == 65 and all(status == 'A' for status, path in changes)
    assert {path for status, path in changes} == {r['path'] for r in rows} | {manifest_file.relative_to(REPO).as_posix()}
    assert git(REPO, 'diff', '--check', PARENT, COMMIT) == b''
    binding = json.loads((HANDOFF / 'CURRENT_BINDING.json').read_text())
    generated = []
    for row in binding['members']:
        name = 'workflow.yml' if row['path'].startswith('.github/') else Path(row['path']).name
        old = git(REPO, 'show', ORIGINAL_COMMIT + ':' + row['path'])
        assert old == (ORIGINAL / name).read_bytes()
        new = (REPO / row['path']).read_bytes()
        assert (len(old), sha(old)) == (row['original_bytes'], row['original_sha256'])
        assert (len(new), sha(new)) == (row['current_bytes'], row['current_sha256'])
        generated.append(row)
    assert len(generated) == 6
    source_manifest = json.loads((REPO / PREFIX / 'SOURCE_MANIFEST.json').read_text())
    assert git(PRODUCT, 'rev-parse', 'HEAD', 'HEAD^{tree}').decode().splitlines() == [SOURCE, SOURCE_TREE]
    assert git(PRODUCT, 'status', '--porcelain', '--untracked-files=all') == b''
    source_rows = {}
    for entry in git(PRODUCT, 'ls-tree', '-rz', '--full-tree', 'HEAD').split(b'\0'):
        if not entry: continue
        header, name = entry.split(b'\t', 1); mode, kind, blob = header.decode().split(); path = name.decode()
        actual = PRODUCT / path; data = actual.read_bytes()
        assert kind == 'blob' and mode in ('100644', '100755') and not actual.is_symlink()
        assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == blob
        assert stat.S_IMODE(actual.stat().st_mode) == (0o755 if mode == '100755' else 0o644)
        source_rows[path] = {'path': path, 'mode': mode, 'git_blob': blob, 'bytes': len(data), 'sha256': sha(data)}
    assert source_manifest['members'] == sorted(source_rows.values(), key=lambda r: r['path'])
    assert source_manifest['file_count'] == len(source_rows) == 1766
    assert source_manifest['total_bytes'] == sum(r['bytes'] for r in source_rows.values()) == 167023692
    assert source_manifest['commit'] == SOURCE and source_manifest['tree'] == SOURCE_TREE
    ast_checks = []
    constants_allowed = {
        'run.py': {'BRANCH', 'SOURCE_COMMIT', 'SOURCE_TREE', 'SUPPORT_SHA', 'INSTALLED_SHA', 'MANIFEST_SHA'},
        'installed_runtime.py': {'SOURCE_COMMIT', 'SOURCE_TREE'},
        'host_support.py': {'SOURCE_COMMIT', 'SOURCE_TREE', 'MANIFEST_SHA'}, 'host_utility.py': set()}
    body_allowed = {'run.py': {'public_project'}, 'host_support.py': {'read_manifest', 'verify_source'},
                    'installed_runtime.py': set(), 'host_utility.py': set()}
    class RestorePopulation(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is int and node.value in (1766, 167023692):
                node.value = {1766: 1759, 167023692: 166402972}[node.value]
            return node
    for name in constants_allowed:
        old, new = ast.parse((ORIGINAL / name).read_bytes()), ast.parse((REPO / PREFIX / name).read_bytes())
        assert len(old.body) == len(new.body)
        changes_seen = []; constants_seen = []; count = 0
        for a, b in zip(old.body, new.body):
            if isinstance(a, (ast.FunctionDef, ast.ClassDef)): count += 1
            if ast.dump(a) == ast.dump(b): continue
            if isinstance(a, ast.Assign) and isinstance(b, ast.Assign):
                assert len(a.targets) == len(b.targets) == 1 and isinstance(a.targets[0], ast.Name)
                assert a.targets[0].id == b.targets[0].id and a.targets[0].id in constants_allowed[name]
                assert isinstance(a.value, ast.Constant) and isinstance(b.value, ast.Constant)
                constants_seen.append(a.targets[0].id)
            else:
                assert isinstance(a, ast.FunctionDef) and isinstance(b, ast.FunctionDef)
                assert a.name == b.name and a.name in body_allowed[name]
                assert ast.dump(a) == ast.dump(RestorePopulation().visit(copy.deepcopy(b)))
                changes_seen.append(a.name)
        assert set(constants_seen) == constants_allowed[name] and set(changes_seen) == body_allowed[name]
        ast_checks.append({'path': name, 'top_level_functions_and_classes': count,
                           'changed_constants': constants_seen, 'population_only_function_changes': changes_seen})
    assert sum(r['top_level_functions_and_classes'] for r in ast_checks) == 93
    oldworkflow = (ORIGINAL / 'workflow.yml').read_text()
    newworkflow = (REPO / '.github/workflows/dg16-installed-runtime05.yml').read_text()
    expected = oldworkflow.replace('name: DG16 installed runtime 05\n', 'name: DG16 M5 current source qualification\n')
    expected = expected.replace('pro/dg16-r5-installed-runtime-05r7-20261106', BRANCH)
    expected = expected.replace('8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b', SOURCE)
    oldhash, newhash = generated[0]['original_sha256'], generated[0]['current_sha256']
    assert oldworkflow.count(oldhash) == newworkflow.count(newhash) == 17
    assert expected.replace(oldhash, newhash) == newworkflow
    dump('STATIC_READBACK.json', {'candidate_commit': COMMIT, 'candidate_tree': TREE, 'parent': PARENT,
        'manifest': describe(manifest_file), 'manifest_members': 64, 'manifest_bytes': 2286337,
        'changed_files': 65, 'all_additive': True, 'all_member_git_and_content_modes_match': True,
        'originals_independently_read_from_git_commit': ORIGINAL_COMMIT, 'original_and_current_files': generated,
        'selected_product': {'commit': SOURCE, 'tree': SOURCE_TREE, 'files': 1766, 'bytes': 167023692,
                             'manifest_sha256': sha((REPO / PREFIX / 'SOURCE_MANIFEST.json').read_bytes())},
        'ast': ast_checks, 'all_93_functions_preserved_except_three_derived_population_bodies': True,
        'workflow_exact_binding_substitution_only': True})

    # This reviewed author harness supplies fixture construction only. Execute a
    # deliberately selected subset, with output and all temporary copies owned
    # by this receiver. No product entrypoint or installed operation is selected.
    temporary = OUT / 'temporary'; temporary.mkdir()
    tempfile.tempdir = str(temporary)
    evidence = OUT / 'focused'; evidence.mkdir()
    harness = module(HANDOFF / 'tools/check_current_binding.py', 'receiver_selected_source_harness')
    harness.ARGS = types.SimpleNamespace(repository=REPO, original_dir=ORIGINAL, source=PRODUCT,
        packages=HANDOFF / 'validation/new-package-fixture-build/artifacts', evidence=evidence)
    selected = [
        'test_003_live_loader_and_whole_source_verifier',
        'test_005_new_fixture_archive_parser_and_package_identity',
        'test_007_archive_checksum_tamper_refuses', 'test_008_archive_source_drift_refuses',
        'test_010_workflow_complete_step_chain_and_safety', 'test_012_complete_output_shape_and_transport',
        'test_013_partial_failure_output_remains_unqualified', 'test_output_same_process_receiver',
        'test_output_elapsed_expired', 'test_output_package_over_reserve', 'test_output_build_replay',
        'test_module_tamper_host_support', 'test_manifest_tamper_refuses']
    stream = io.StringIO()
    tests = unittest.TestSuite(harness.Checks(name) for name in selected)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(tests)
    (OUT / 'FOCUSED_TESTS.stderr.txt').write_text(stream.getvalue())
    assert result.wasSuccessful() and result.testsRun == 13 and not result.skipped
    sample = harness.Checks('test_012_complete_output_shape_and_transport')
    adapter = harness.Checks.adapter
    boundaries = []
    for kind, value in [('reserve_exact_limit', 587824), ('elapsed_exact_watchdog', 2400)]:
        state, context = sample.complete_fixture()
        if kind == 'reserve_exact_limit': state['packages']['artifacts']['canonical_plugin']['bytes'] = value
        else: state['ended_monotonic'] = state['started_monotonic'] + value
        assert sample.project(state, context)['RESULT.json']['status'] == 'PASS'
        boundaries.append({'case': kind, 'value': value, 'synthetic_status': 'PASS'})
    state, context = sample.complete_fixture()
    docs = sample.project(state, context)
    assert docs['SOURCE.json']['before_complete'] is True and docs['SOURCE.json']['after_complete'] is True
    assert [r['route'] for r in docs['ROUTES.json']['routes']] == list(adapter.ROUTES)
    assert all(r['first_normal_resume_verified'] and r['distinct_receiver_process'] and
               r['receiver_final_currentness'] and r['closing_currentness'] for r in docs['ROUTES.json']['routes'])
    files, envelopes = adapter.build_transport(docs)
    boundaries.append({'case': 'complete_current_source_cross_document_conjunction', 'synthetic_status': 'PASS',
                       'public_file_count': len(files), 'bytes': sum(map(len, files.values())),
                       'envelope_bytes': sum(map(len, envelopes))})
    dump('FOCUSED_RESULTS.json', {'scope': 'LOCAL_SYNTHETIC_SOURCE_CHECKS_ONLY; NO_HOSTED_ROUTE_EVIDENCE',
        'selected_author_controls': selected, 'tests': 13, 'passes': 13, 'failures': 0, 'errors': 0, 'skips': 0,
        'additional_receiver_boundary_cases': boundaries, 'product_entrypoint_executions': 0,
        'installed_routes_launched': 0, 'old_27_suite_rerun': False, 'GitHub_environment_fabricated': False,
        'authority': 'NONE', 'original_acceptance': False})
    command('GENERATOR_CHECK', [sys.executable, '-B', str(HANDOFF / 'tools/bind_current_source.py'),
        '--original-dir', str(ORIGINAL), '--source', str(PRODUCT), '--repository', str(REPO), '--check'], 0)
    lint = BASE / 'm5-source-recovery/actionlint-1.7.12/actionlint'
    assert sha(lint.read_bytes()) == 'c872d6db8c6bf83a8eaa704fc93999f027d55dffbc63b8a6abdccb47df5f4cd4'
    command('ACTIONLINT_DEFAULT', [str(lint), '-no-color', str(REPO / '.github/workflows/dg16-installed-runtime05.yml')], 1)
    diagnostic = (OUT / 'ACTIONLINT_DEFAULT.stdout.txt').read_text()
    assert diagnostic.count('[runner-label]') == 1 and 'label "ubuntu-26.04" is unknown.' in diagnostic
    command('ACTIONLINT_LABEL_ONLY', [str(lint), '-no-color', '-ignore', '^label "ubuntu-26[.]04" is unknown[.]',
                                    str(REPO / '.github/workflows/dg16-installed-runtime05.yml')], 0)
    assert (OUT / 'ACTIONLINT_LABEL_ONLY.stdout.txt').read_bytes() == (OUT / 'ACTIONLINT_LABEL_ONLY.stderr.txt').read_bytes() == b''
    assert git(REPO, 'status', '--porcelain', '--untracked-files=all') == b''
    assert git(PRODUCT, 'status', '--porcelain', '--untracked-files=all') == b''
    for row in rows:
        assert describe(REPO / row['path'])['sha256'] == row['sha256']
    dump('EXECUTION.json', {'started_utc': start, 'ended_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'result': 'PASS_AT_SOURCE_REVIEW_SCOPE', 'candidate_unchanged': True, 'selected_product_unchanged': True,
        'source_review_receiver': '/root/dg18_engineering', 'candidate_author': '/root/dg18_independent_review',
        'remote_effects': False, 'native_or_protected_effects': False, 'controller_changes': False,
        'source_suite_rerun': False, 'historical_bodies_recovered': False})
    print(json.dumps({'result': 'PASS_AT_SOURCE_REVIEW_SCOPE', 'candidate': COMMIT, 'tree': TREE,
                      'manifest_members': 64, 'selected_tests': 13, 'additional_boundary_cases': 3,
                      'output': str(OUT)}, indent=2))


if __name__ == '__main__':
    main()
