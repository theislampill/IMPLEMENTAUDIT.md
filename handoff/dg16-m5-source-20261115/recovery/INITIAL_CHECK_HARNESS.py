#!/usr/bin/env python3
"""Focused offline checks of the M5 binding, exact driver and output shapes.

The synthetic projector inputs are unit-test data, never GitHub event records,
host admission, controller receipts, actual installed-route results or authority.
The real package parser uses the separately retained A/B package bytes. No test
executes installers, claims, model/native operations, provisioning or a CI job.
"""
import argparse
import ast
import copy
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import types
import unittest

sys.dont_write_bytecode = True


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = ARGS.repository.resolve(strict=True)
        cls.packet = cls.repo / 'qualification/dg16-installed-runtime05'
        cls.original = ARGS.original_dir.resolve(strict=True)
        cls.source = ARGS.source.resolve(strict=True)
        cls.packages = ARGS.packages.resolve(strict=True)
        cls.evidence = ARGS.evidence.resolve(strict=True)
        cls.bind = module(Path(__file__).with_name('bind_current_source.py'), 'binding')
        cls.run = module(cls.packet / 'run.py', 'current_adapter')
        cls.u = cls.run.load_module('host_utility', cls.run.UTILITY_SHA)
        cls.h = cls.run.load_module('host_support', cls.run.SUPPORT_SHA)
        cls.installed = cls.run.load_module('installed_runtime', cls.run.INSTALLED_SHA)
        cls.manifest = cls.h.read_manifest(cls.u)
        cls.package_cache = {}

    def refused(self, function, code):
        with self.assertRaises(Exception) as caught:
            function()
        self.assertEqual(str(caught.exception), code)

    def copied_packages(self, temporary, role='A'):
        output = Path(temporary) / 'episode'
        target = output / 'private/packages'
        target.mkdir(parents=True, mode=0o700)
        for name in ('IMPLEMENTAUDIT.plugin.zip', 'IMPLEMENTAUDIT.skill', 'CHECKSUMS.txt'):
            shutil.copyfile(self.packages / role / name, target / name)
            (target / name).chmod(0o600)
        return output

    def package_snapshot(self, role='A'):
        if role not in self.package_cache:
            with tempfile.TemporaryDirectory(prefix='m5-package-parser-') as temporary:
                output = self.copied_packages(temporary, role)
                self.package_cache[role] = self.installed.archive_snapshot(self.source, output, self.manifest, self.u.parse_json)
            (self.evidence / ('ACTUAL_PACKAGE_PARSE_' + role + '.json')).write_bytes(canonical(self.package_cache[role]))
        return copy.deepcopy(self.package_cache[role])

    def complete_fixture(self):
        context = {'test_fixture': 'SYNTHETIC_OUTPUT_SHAPE_ONLY', 'run_id': 'NOT_A_GITHUB_RUN'}
        state = self.run.fresh_state(context, Path('/fixture/source'), Path('/fixture/output'),
                                     types.SimpleNamespace(identities=lambda path: [0, 0, 0]))
        state.update(completed=list(self.run.STEPS), finalized=True, finalization_attempted=True,
                     all_children_reaped=True, source_unchanged=True, venv_unchanged=True,
                     packages_unchanged=True, installed_unchanged=True, runtime_unchanged=True,
                     final_currentness=True, started_monotonic=100, ended_monotonic=101)
        source = {'file_count': 1766, 'total_bytes': 167023692,
                  'manifest_sha256': self.run.MANIFEST_SHA, 'all_members_match': True}
        state['source_before'] = dict(source); state['source_after'] = dict(source)
        state['venv'] = {'file_or_alias_count': 1, 'total_file_bytes': 1, 'members': {'synthetic': {'bytes': 1}}}
        state['host'] = {'os': {'ID': 'ubuntu', 'VERSION_ID': '26.04'}, 'python_version': [3, 14, 4],
                         'architecture': 'x86_64', 'uid': 1001, 'kernel': '0-fixture', 'image_os': 'ubuntu26',
                         'image_version': '00000000.0.0', 'boot_identity_sha256': '0' * 64, 'tools': {}}
        for name in ('bash', 'python3', 'git', 'env'):
            state['host']['tools'][name] = {'available': True, 'requested': '/usr/bin/' + name,
                'canonical': '/usr/bin/python3.14' if name == 'python3' else '/usr/bin/' + name,
                'bytes': 1, 'sha256': '0' * 64, 'root_owned_nonwritable_chain': True,
                'setid_or_file_capabilities': False}
        state['setup'] = {'status': 'COMPLETED', 'canonical': '/usr/bin/sudo', 'bytes': 1, 'sha256': '0' * 64,
                          'mode': 0o4755, 'uid': 0, 'alias_and_ancestor_count': 1,
                          'aliases_and_ancestors_sha256': '0' * 64, 'elapsed_seconds': 1,
                          'zopfli_version': '0.2.3.post1', 'module_bytes': 1, 'module_sha256': '0' * 64}
        state['packages'] = self.package_snapshot()
        state['installed'] = {}
        for route in self.run.ROUTES:
            role = 'canonical_plugin' if route.startswith('plugin-') else 'standalone_compatibility'
            state['installed'][route] = {'role': role, 'source': dict(self.installed.SOURCE_BINDING),
                                        'files': copy.deepcopy(state['packages']['artifacts'][role]['members'])}
            state['subjects'][route] = {'status': 'FIRST_NORMAL_RESUME_VERIFIED'}
            state['received'][route] = {'status': 'PASS', 'owner_pid': 1, 'receiver_pid': 2,
                'receipt_body_sha256': '0' * 64, 'request_sha256': '1' * 64,
                'objects': {'SYNTHETIC_TEST_ONLY': {}}, 'run_population': {'SYNTHETIC_TEST_ONLY': {}},
                'final_currentness': True}
            state['closing_subjects'][route] = {'currentness': True, 'refs_unchanged': True, 'documents_unchanged': True}
        state['phases'] = [{'stage': step, 'status': 'COMPLETED', 'elapsed_seconds': 0, 'command_count': 0,
                           'own_children_reaped': True, 'own_max_rss_kib': 0, 'reaped_child_max_rss_kib': 0,
                           'rlimit_nofile': [1, 1]} for step in (*self.run.STEPS, 'finalize')]
        state['commands'] = [{'label': 'build-two-release-roles', 'ordinal': 1, 'stage': 'build',
                              'capture': {'process_started': True, 'returncode': 0, 'streams_complete': True,
                                          'cleanup': {'echild': True}}}]
        state['command_count'] = 1
        return state, context

    def project(self, state, context):
        return self.run.public_project(state, context, self.manifest)

    def test_001_reproduction_and_full_source_identity(self):
        expected = self.bind.rebind(self.original, self.source)
        self.assertEqual(len(expected), 7)
        for relative, raw in expected.items():
            self.assertEqual((self.repo / relative).read_bytes(), raw, relative)
        self.assertEqual(len(self.manifest), 1766)
        self.assertEqual(sum(row['bytes'] for row in self.manifest.values()), 167023692)
        self.assertEqual(self.run.MANIFEST_SHA, '328bfd9ba1711260d6efa19ed8fcf45651d375e7c3685b9ce50bd03f1c3803ee')

    def test_002_all_functions_unchanged_except_derived_population(self):
        reverse = {self.bind.SOURCE_COMMIT: self.bind.OLD_SOURCE, self.bind.SOURCE_TREE: self.bind.OLD_TREE,
                   self.bind.BRANCH: self.bind.OLD_BRANCH, 1766: 1759, 167023692: 166402972}
        for name in ('installed_runtime.py', 'host_support.py', 'SOURCE_MANIFEST.json'):
            reverse[sha((self.packet / name).read_bytes())] = self.bind.ORIGINAL[name][1]
        class Normalize(ast.NodeTransformer):
            def visit_Constant(inner, node):
                if type(node.value) in (str, int) and node.value in reverse:
                    node.value = reverse[node.value]
                return node
        result = []
        for name in ('run.py', 'installed_runtime.py', 'host_support.py', 'host_utility.py'):
            old = ast.parse((self.original / name).read_bytes())
            current = ast.parse((self.packet / name).read_bytes())
            self.assertEqual(ast.dump(old), ast.dump(Normalize().visit(current)), name)
            old_functions = {node.name: ast.dump(node) for node in old.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
            new_functions = {node.name: ast.dump(node) for node in ast.parse((self.packet / name).read_bytes()).body
                             if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
            changed = sorted(key for key in old_functions if old_functions[key] != new_functions[key])
            self.assertEqual(changed, {'run.py': ['public_project'], 'host_support.py': ['read_manifest', 'verify_source']}.get(name, []))
            result.append({'path': name, 'function_and_class_count': len(old_functions),
                           'body_changes_only_derived_population': changed})
        (self.evidence / 'AST_COMPARISON.json').write_bytes(canonical(result))
        self.assertEqual((self.packet / 'host_utility.py').read_bytes(), (self.original / 'host_utility.py').read_bytes())

    def test_003_live_loader_and_whole_source_verifier(self):
        for name, digest in [('host_utility', self.run.UTILITY_SHA), ('host_support', self.run.SUPPORT_SHA),
                             ('installed_runtime', self.run.INSTALLED_SHA)]:
            self.assertEqual(sha((self.packet / (name + '.py')).read_bytes()), digest)
            self.run.load_module(name, digest)
        observed = self.h.verify_source(self.source, self.manifest, self.u)
        self.assertEqual(observed, {'file_count': 1766, 'total_bytes': 167023692,
                                    'manifest_sha256': self.run.MANIFEST_SHA, 'all_members_match': True})
        (self.evidence / 'ACTUAL_SOURCE_VERIFICATION.json').write_bytes(canonical(observed))

    def test_004_exact_budgets_routes_and_authority(self):
        self.assertEqual(self.run.ROUTES, ('plugin-codex', 'plugin-claude', 'standalone-codex', 'standalone-claude'))
        self.assertEqual(self.installed.ROUTES, self.run.ROUTES)
        self.assertEqual((self.run.RUN_SECONDS, self.run.FINAL_SECONDS, self.run.SETUP_SECONDS, self.run.BUILD_SECONDS),
                         (2400, 180, 600, 600))
        text = (self.packet / 'installed_runtime.py').read_text()
        self.assertIn("'e4af32dc219e8c041d62170b960cdb465f0cdfebdb7e414d0f45b7726cc31488'", text)
        self.assertIn('len(raw) <= 589824 - 2000', text)
        self.assertIn("original_acceptance=False", (self.packet / 'run.py').read_text())

    def test_005_current_A_B_archive_parser_and_package_identity(self):
        a, b = self.package_snapshot('A'), self.package_snapshot('B')
        self.assertEqual(a, b)
        expected = {'canonical_plugin': (584971, 'a43f018d4d3cc6d6257eeacfd8b5b834588410564ac33b0c8022d01a0ca71e58', 75),
                    'standalone_compatibility': (580360, 'd1b89ec4113b0c57d925e2f5aeec16c1baa471985b918e6fc3e54e808fad7f1e', 72)}
        for role, (size, digest, count) in expected.items():
            row = a['artifacts'][role]
            self.assertEqual((row['bytes'], row['sha256'], len(row['members'])), (size, digest, count))
            self.assertEqual(row['source'], self.installed.SOURCE_BINDING)
            self.assertGreaterEqual(589824 - size, 2000)

    def test_006_archive_extra_file_refuses(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = self.copied_packages(temporary)
            (output / 'private/packages/UNEXPECTED').write_bytes(b'fixture')
            self.refused(lambda: self.installed.archive_snapshot(self.source, output, self.manifest, self.u.parse_json),
                         'PACKAGE_OUTPUT_POPULATION_REFUSED')

    def test_007_archive_checksum_tamper_refuses(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = self.copied_packages(temporary)
            path = output / 'private/packages/IMPLEMENTAUDIT.plugin.zip'
            raw = path.read_bytes(); path.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
            self.refused(lambda: self.installed.archive_snapshot(self.source, output, self.manifest, self.u.parse_json),
                         'PACKAGE_CHECKSUM_OR_RESERVE_REFUSED')

    def test_008_archive_source_drift_refuses(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = self.copied_packages(temporary)
            manifest = copy.deepcopy(self.manifest)
            manifest['skills/implementaudit/SKILL.md']['sha256'] = '0' * 64
            self.refused(lambda: self.installed.archive_snapshot(self.source, output, manifest, self.u.parse_json),
                         'PACKAGE_SOURCE_DRIFT')

    def test_009_actual_local_main_fails_closed_without_admitted_host(self):
        self.assertNotEqual(os.environ.get('GITHUB_ACTIONS'), 'true')
        with tempfile.TemporaryDirectory(prefix='m5-real-main-') as temporary:
            output = Path(temporary) / 'never-created'
            argv = [sys.executable, '-I', '-S', '-B', str(self.packet / 'run.py'), '--step', 'prepare',
                    '--source', str(self.source), '--output', str(output)]
            result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, b'DG16_INSTALLED_RUNTIME_STATUS {"status":"UNQUALIFIED","code":"ADAPTER_CLOSED_REFUSAL","authority":"NONE"}\n')
            self.assertEqual(result.stderr, b'')
            self.assertFalse(output.exists())
            (self.evidence / 'ACTUAL_LOCAL_MAIN_REFUSAL.json').write_bytes(canonical({
                'argv': argv, 'exit_code': result.returncode, 'stdout': result.stdout.decode(),
                'stderr': result.stderr.decode(), 'output_created': False,
                'environment_fabricated': False, 'actual_python': list(sys.version_info[:3])}))
        self.refused(lambda: self.run.host_context(self.source, self.evidence), 'EVENT_GUARD_REFUSED')
        self.refused(lambda: self.run.inventory(self.u), 'HOST_RUNTIME_REFUSED')

    def test_010_workflow_complete_step_chain_and_safety(self):
        import yaml
        workflow = yaml.load((self.repo / self.bind.WORKFLOW).read_text(), Loader=yaml.BaseLoader)
        self.assertEqual(set(workflow['on']), {'push'})
        self.assertEqual(workflow['on']['push'], {'branches': [self.bind.BRANCH],
                         'paths': [self.bind.WORKFLOW, self.bind.PREFIX + '**']})
        self.assertEqual(workflow['permissions'], {'contents': 'read'})
        self.assertEqual(workflow['concurrency']['cancel-in-progress'], 'false')
        self.assertEqual(set(workflow['jobs']), {'qualify-four-installed-layouts'})
        job = workflow['jobs']['qualify-four-installed-layouts']
        self.assertEqual(job['runs-on'], 'ubuntu-26.04'); self.assertEqual(job['timeout-minutes'], '45')
        expected_if = "github.repository == 'theislampill/IMPLEMENTAUDIT.md' && github.event_name == 'push' && " + \
                      "github.ref == 'refs/heads/" + self.bind.BRANCH + "' && github.event.deleted == false && github.event.created == true && github.run_attempt == '1'"
        self.assertEqual(' '.join(job['if'].split()), expected_if)
        steps = job['steps']; self.assertEqual(len(steps), 20)
        for index, (ref, path, depth) in enumerate([('${{ github.sha }}', 'packet', '1'), (self.bind.SOURCE_COMMIT, 'qualified-source', '2')]):
            self.assertEqual(steps[index]['uses'], 'actions/checkout@11d5960a326750d5838078e36cf38b85af677262')
            self.assertEqual(steps[index]['with'], {'ref': ref, 'path': path, 'fetch-depth': depth,
                'persist-credentials': 'false', 'set-safe-directory': 'false', 'submodules': 'false', 'lfs': 'false'})
        runs = steps[2:-1]
        self.assertEqual([step['id'] for step in runs], [name.replace('-', '_') for name in (*self.run.STEPS, 'finalize', 'emit')])
        adapter_sha = sha((self.packet / 'run.py').read_bytes())
        for step, operation in zip(runs, (*self.run.STEPS, 'finalize', 'emit')):
            body = step['run']; self.assertEqual(step['shell'], 'bash')
            self.assertEqual(body.count(adapter_sha), 1)
            self.assertIn('/usr/bin/sha256sum "$adapter"', body)
            argument = '--emit-public' if operation == 'emit' else '--step ' + operation
            self.assertIn('/usr/bin/python3 -I -S -B "$adapter" ' + argument, body)
            self.assertIn('--source "$GITHUB_WORKSPACE/qualified-source"', body)
            self.assertIn('--output "$RUNNER_TEMP/dg16-installed05-$GITHUB_RUN_ID-$GITHUB_RUN_ATTEMPT"', body)
            if operation in ('finalize', 'emit'): self.assertEqual(step['if'], 'always()')
            else: self.assertNotIn('if', step)
            checked = subprocess.run(['bash', '-n'], input=body.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            self.assertEqual((checked.returncode, checked.stdout, checked.stderr), (0, b'', b''), operation)
        upload = steps[-1]
        self.assertEqual(upload['uses'], 'actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02')
        self.assertEqual(upload['if'], "always() && steps.emit.outcome == 'success' && steps.emit.outputs.eligible == 'true'")
        self.assertEqual([line.rsplit('/', 1)[-1] for line in upload['with']['path'].splitlines()],
                         [*self.run.PUBLIC_NAMES, 'ARTIFACT_MANIFEST.json'])
        self.assertEqual(upload['with']['if-no-files-found'], 'error')
        self.assertEqual(upload['with']['include-hidden-files'], 'false')
        (self.evidence / 'WORKFLOW_STRUCTURE.json').write_bytes(canonical({'bash_bodies_checked': len(runs),
            'phase_sequence': [name for name in (*self.run.STEPS, 'finalize', 'emit')], 'upload_names': [*self.run.PUBLIC_NAMES, 'ARTIFACT_MANIFEST.json'],
            'event_created_required': True, 'attempt_one_required': True, 'permissions': {'contents': 'read'}}))

    def test_011_real_host_feasibility_only(self):
        root = self.repo / 'handoff/dg16-m5-source-20261115/host-observation'
        raw = (root / 'G220_HOST_WIRE.json').read_bytes()
        self.assertEqual((len(raw), sha(raw)), (33335, '7f775ecd0b0fa6051de24bdc3b686172b86396d955add780a6adadeee965d6d4'))
        outer = json.loads(raw); self.assertEqual(outer['name'], 'HOST.json')
        observed = outer['document']
        self.assertEqual(observed['os'], {'ID': 'ubuntu', 'VERSION_ID': '26.04'})
        self.assertEqual(observed['python_version'], [3, 14, 4])
        self.assertEqual((observed['architecture'], observed['image_os'], observed['image_version']),
                         ('x86_64', 'ubuntu26', '20261111.82.6'))
        self.assertEqual(observed['uid'], 1001)
        descriptor = json.loads((root / 'G220_HOST_DESCRIPTOR.json').read_bytes())
        self.assertEqual((descriptor['run_id'], descriptor['job_id'], descriptor['run_conclusion']),
                         (43640583300, 132587057176, 'failure'))
        self.assertEqual(descriptor['sha256'], sha(raw))

    def test_012_complete_output_shape_and_transport(self):
        state, context = self.complete_fixture()
        docs = self.project(state, context)
        self.assertEqual(set(docs), set(self.run.PUBLIC_NAMES))
        self.assertEqual(docs['RESULT.json']['status'], 'PASS')
        self.assertEqual(docs['RESULT.json']['authority'], 'NONE')
        for key in ('original_acceptance', 'native_application_discovery', 'windows', 'whole_cell_claim',
                    'public_release', 'audit_closure', 'governed_phase_completion_claimed', 'automatic_retry'):
            self.assertIs(docs['RESULT.json'][key], False, key)
        self.assertEqual(docs['SOURCE.json']['commit'], self.bind.SOURCE_COMMIT)
        self.assertEqual(docs['SOURCE.json']['tree'], self.bind.SOURCE_TREE)
        self.assertIs(docs['SOURCE.json']['before_complete'], True); self.assertIs(docs['SOURCE.json']['after_complete'], True)
        self.assertEqual([row['status'] for row in docs['ROUTES.json']['routes']], ['RECEIVED'] * 4)
        files, lines = self.run.build_transport(docs)
        self.assertEqual(set(files), {*self.run.PUBLIC_NAMES, 'ARTIFACT_MANIFEST.json'})
        self.assertEqual(len(lines), 9)
        for line in lines:
            self.assertTrue(line.startswith(b'DG16_INSTALLED_RUNTIME '))
            envelope = json.loads(line.split(b' ', 1)[1]); raw = files[envelope['name']]
            self.assertEqual(envelope['utf8_json'].encode('ascii'), raw)
            self.assertEqual((envelope['bytes'], envelope['sha256']), (len(raw), sha(raw)))
            self.assertLessEqual(len(line), self.run.ENVELOPE_LIMIT)
        self.assertLessEqual(sum(map(len, files.values())), self.run.TOTAL_LIMIT)
        self.assertLessEqual(sum(map(len, lines)), self.run.LOG_LIMIT)
        manifest = json.loads(files['ARTIFACT_MANIFEST.json'])
        self.assertFalse(manifest['private_outputs_included']); self.assertEqual(manifest['authority'], 'NONE')
        self.assertEqual(manifest['files'], [{'name': name, 'bytes': len(raw), 'sha256': sha(raw)}
                         for name, raw in sorted(files.items()) if name != 'ARTIFACT_MANIFEST.json'])
        (self.evidence / 'SYNTHETIC_COMPLETE_OUTPUT_SHAPE.json').write_bytes(canonical({
            'scope': 'SYNTHETIC_UNIT_TEST_ONLY_NOT_HOSTED_RESULT', 'documents': docs,
            'transport_files': manifest['files'], 'transport_total_bytes': sum(map(len, files.values())),
            'transport_envelope_bytes': sum(map(len, lines))}))

    def test_013_partial_failure_output_remains_unqualified(self):
        state, context = self.complete_fixture()
        state.update(completed=['prepare'], finalized=False, finalization_attempted=False,
                     final_currentness=None, received={}, closing_subjects={}, subjects={},
                     active_step='initialize', pending_command={'label': 'parent-author', 'ordinal': 2},
                     all_children_reaped=False, interrupted_predecessor_observed=True)
        state['phases'] = state['phases'][:1]
        state['failures'] = [{'stage': 'initialize', 'code': 'UNCLASSIFIED_PRIVATE_DIAGNOSTIC',
                             'exception_type': 'RuntimeError', 'errno': None, 'diagnostic_bytes': 33,
                             'diagnostic_sha256': sha(b'SYNTHETIC_PRIVATE_DIAGNOSTIC_TEST')}]
        docs = self.project(state, context); files, _ = self.run.build_transport(docs)
        self.assertEqual(docs['RESULT.json']['status'], 'UNQUALIFIED')
        self.assertTrue(docs['FAILURE.json']['present'])
        self.assertTrue(docs['CLEANUP.json']['unknown_pending_step'])
        self.assertTrue(docs['CLEANUP.json']['unknown_pending_command'])
        self.assertNotIn(b'SYNTHETIC_PRIVATE_DIAGNOSTIC_TEST', b''.join(files.values()))
        observed = self.run.failed_state_observation(state, context, self.manifest)
        self.assertFalse(observed['original_acceptance']); self.assertFalse(observed['currentness_authority'])
        (self.evidence / 'SYNTHETIC_FAILURE_OUTPUT_SHAPE.json').write_bytes(canonical({
            'scope': 'SYNTHETIC_UNIT_TEST_ONLY_NOT_HOSTED_RESULT', 'documents': docs, 'failed_state_observation': observed}))

    def test_014_fallback_minimum_transport(self):
        documents = {'RESULT.json': {'status': 'UNQUALIFIED', 'authority': 'NONE', 'original_acceptance': False},
                     'FAILURE.json': {'present': True, 'fallback': True}}
        files, lines = self.run.build_transport(documents)
        self.assertEqual(set(files), {'RESULT.json', 'FAILURE.json', 'ARTIFACT_MANIFEST.json'})
        self.assertEqual(len(lines), 3)

    def test_015_transport_extra_population_refuses(self):
        state, context = self.complete_fixture(); docs = self.project(state, context); docs['PRIVATE.json'] = {}
        self.refused(lambda: self.run.build_transport(docs), 'PUBLIC_POPULATION_REFUSED')

    def test_016_transport_missing_required_result_refuses(self):
        self.refused(lambda: self.run.build_transport({'FAILURE.json': {}}), 'PUBLIC_POPULATION_REFUSED')

    def test_017_transport_file_limit_refuses(self):
        self.refused(lambda: self.run.build_transport({'RESULT.json': {'body': 'x' * self.run.FILE_LIMIT}, 'FAILURE.json': {}}),
                     'PUBLIC_FILE_BOUND')

    def test_018_transport_aggregate_limit_refuses(self):
        docs = {name: {'body': 'x' * 60000} for name in self.run.PUBLIC_NAMES}
        self.refused(lambda: self.run.build_transport(docs), 'PUBLIC_TOTAL_BOUND')

    def test_019_transport_nonfinite_json_refuses(self):
        with self.assertRaises(ValueError):
            self.run.build_transport({'RESULT.json': {'body': float('nan')}, 'FAILURE.json': {}})


def mutation_case(name, mutate, expected_code=None):
    def test(self):
        state, context = self.complete_fixture()
        mutate(state)
        if expected_code:
            self.refused(lambda: self.project(state, context), expected_code)
        else:
            self.assertEqual(self.project(state, context)['RESULT.json']['status'], 'UNQUALIFIED')
    setattr(Checks, 'test_output_' + name, test)


for flag in ('finalized', 'all_children_reaped', 'source_unchanged', 'venv_unchanged',
             'packages_unchanged', 'installed_unchanged', 'runtime_unchanged', 'final_currentness'):
    mutation_case(flag, lambda state, flag=flag: state.update({flag: False}))
mutation_case('incomplete_steps', lambda state: state['completed'].pop())
mutation_case('active_step', lambda state: state.update(active_step='build'))
mutation_case('pending_command', lambda state: state.update(pending_command={'label': 'parent-author', 'ordinal': 2}))
mutation_case('elapsed_expired', lambda state: state.update(ended_monotonic=2501))
mutation_case('ending_absent', lambda state: state.pop('ended_monotonic'))
mutation_case('received_route_absent', lambda state: state['received'].pop('plugin-codex'))
mutation_case('closing_route_absent', lambda state: state['closing_subjects'].pop('standalone-claude'))
mutation_case('same_process_receiver', lambda state: state['received']['plugin-codex'].update(receiver_pid=1))
mutation_case('first_resume_absent', lambda state: state['subjects']['plugin-codex'].update(status='UNSTARTED'))
mutation_case('receiver_currentness', lambda state: state['received']['plugin-claude'].update(final_currentness=False))
mutation_case('closing_documents_drift', lambda state: state['closing_subjects']['standalone-codex'].update(documents_unchanged=False))
mutation_case('phase_failed', lambda state: state['phases'][0].update(status='FAILED'))
mutation_case('phase_child_unknown', lambda state: state['phases'][0].update(own_children_reaped=False))
mutation_case('phase_sequence', lambda state: state['phases'].reverse())
mutation_case('build_not_observed', lambda state: state['commands'][0]['capture'].update(process_started=False))
mutation_case('build_replay', lambda state: state['commands'].append(dict(state['commands'][0], ordinal=2)), 'PUBLIC_BUILD_REPLAY_REFUSED')
mutation_case('host_profile', lambda state: state['host'].update(python_version=[3, 12, 14]), 'PUBLIC_HOST_IDENTITY_REFUSED')
mutation_case('host_tools_incomplete', lambda state: state['host']['tools'].pop('env'), 'PUBLIC_TOOL_POPULATION_REFUSED')
mutation_case('host_tool_custody', lambda state: state['host']['tools']['python3'].update(root_owned_nonwritable_chain=False), 'PUBLIC_TOOL_CUSTODY_REFUSED')
mutation_case('host_tool_setid', lambda state: state['host']['tools']['bash'].update(setid_or_file_capabilities=True), 'PUBLIC_TOOL_CUSTODY_REFUSED')
mutation_case('package_old_source', lambda state: state['packages']['artifacts']['canonical_plugin']['source'].update(commit='0' * 40), 'PUBLIC_PACKAGE_SOURCE_REFUSED')
mutation_case('package_over_reserve', lambda state: state['packages']['artifacts']['canonical_plugin'].update(bytes=587825), 'PUBLIC_INTEGER_REFUSED')
mutation_case('package_members_incomplete', lambda state: state['packages']['artifacts']['canonical_plugin']['members'].pop('skills/implementaudit/SKILL.md'), 'PUBLIC_PACKAGE_MEMBER_COUNT_REFUSED')
mutation_case('installed_parity', lambda state: state['installed']['plugin-codex']['files'].pop('skills/implementaudit/SKILL.md'), 'PUBLIC_INSTALLED_PARITY_REFUSED')
mutation_case('state_foreign_context', lambda state: state.update(context={'test_fixture': 'FOREIGN'}), 'PUBLIC_STATE_BINDING_REFUSED')
mutation_case('unexpected_route', lambda state: state['received'].update(fifth_route={}), 'PUBLIC_STATE_POPULATION_REFUSED')
mutation_case('integer_bool', lambda state: state.update(command_count=True), 'PUBLIC_INTEGER_REFUSED')


def module_tamper_case(name):
    def test(self):
        with tempfile.TemporaryDirectory(prefix='m5-loader-negative-') as temporary:
            target = Path(temporary)
            for path in self.packet.iterdir():
                if path.is_file(): shutil.copyfile(path, target / path.name)
            path = target / (name + '.py'); path.write_bytes(path.read_bytes() + b'\n# synthetic tamper\n')
            runner = module(target / 'run.py', 'tampered_adapter_' + name)
            expected = {'host_utility': runner.UTILITY_SHA, 'host_support': runner.SUPPORT_SHA,
                        'installed_runtime': runner.INSTALLED_SHA}[name]
            self.refused(lambda: runner.load_module(name, expected), 'ADAPTER_MODULE_DIGEST_REFUSED')
    setattr(Checks, 'test_module_tamper_' + name, test)


for dependency in ('host_utility', 'host_support', 'installed_runtime'):
    module_tamper_case(dependency)


def manifest_tamper(self):
    with tempfile.TemporaryDirectory(prefix='m5-manifest-negative-') as temporary:
        target = Path(temporary)
        shutil.copyfile(self.packet / 'host_support.py', target / 'host_support.py')
        (target / 'SOURCE_MANIFEST.json').write_bytes((self.packet / 'SOURCE_MANIFEST.json').read_bytes() + b' ')
        support = module(target / 'host_support.py', 'tampered_manifest_support')
        self.refused(lambda: support.read_manifest(self.u), 'SOURCE_MANIFEST_DIGEST_REFUSED')


setattr(Checks, 'test_manifest_tamper_refuses', manifest_tamper)


class Ledger(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test); self.started = time.monotonic()
    def addSuccess(self, test):
        super().addSuccess(test)
        RECORDS.append({'case': test.id().split('.')[-1], 'status': 'PASS', 'elapsed_seconds': time.monotonic() - self.started})
    def addFailure(self, test, err):
        super().addFailure(test, err)
        RECORDS.append({'case': test.id().split('.')[-1], 'status': 'FAIL', 'elapsed_seconds': time.monotonic() - self.started})
    def addError(self, test, err):
        super().addError(test, err)
        RECORDS.append({'case': test.id().split('.')[-1], 'status': 'ERROR', 'elapsed_seconds': time.monotonic() - self.started})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repository', 'original-dir', 'source', 'packages', 'evidence'):
        parser.add_argument('--' + name, type=Path, required=True)
    ARGS = parser.parse_args()
    ARGS.evidence.mkdir(parents=True, exist_ok=False)
    RECORDS = []
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    result = unittest.TextTestRunner(verbosity=2, resultclass=Ledger).run(suite)
    report = {'schema': 'dg16.m5-binding-focused-controls.v1',
              'scope': 'OFFLINE_SOURCE_BINDING_AND_SYNTHETIC_OUTPUT_SHAPES; NO_LIVE_ROUTE_EVIDENCE',
              'tests': result.testsRun, 'passes': sum(row['status'] == 'PASS' for row in RECORDS),
              'failures': len(result.failures), 'errors': len(result.errors), 'skips': len(result.skipped),
              'python': sys.version, 'pyyaml': importlib.metadata.version('PyYAML'), 'controls': RECORDS,
              'environment_fabricated': False, 'authority': 'NONE', 'original_acceptance': False}
    (ARGS.evidence / 'CONTROL_RESULTS.json').write_bytes(canonical(report))
    raise SystemExit(0 if result.wasSuccessful() else 1)
