"""Bounded saved-data/source controls; no native worker or host configuration writes.

The default mode requires the exact independently captured input pins.
The explicit synthetic mode replaces only environment fixture data and its
test-local policy selection; it grants no historical/native policy proof.
No raw saved response, private HOME entry or full environment map is serialized.
"""
import argparse
import ast
import builtins
import copy
import ctypes
import hashlib
import importlib.util
import io
import json
import os
from contextlib import contextmanager
from pathlib import Path, PureWindowsPath
import sys
import types
import unittest
from unittest.mock import patch

SOURCE = WORK = INPUTS = RUNTIME = PROFILE = PROVIDER = PLAN = RESPONSE = POLICY = None
FIXTURE_REPLACEMENTS = {}
SYNTHETIC_POLICY = None
SYNTHETIC_SOURCE_POLICY_SELECTIONS = set()

def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
def pin(path):
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}
def captured(row):
    raw = Path(row['path']).read_bytes()
    if len(raw) != row['bytes'] or sha(raw) != row['sha256']:
        raise AssertionError('Pinned test input changed')
    return raw
def load(path, name, *, synthetic_policy=True):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return fixture_policy_module(module) if synthetic_policy else module

def fixture_policy_module(module):
    """Keep verified code loaders intact; select synthetic data only in tests.

    This test-local selector substitution cannot qualify the source owner's
    actual policy selection. File-pin, source-hash, value, and purpose checks
    still execute, including the existing wrong-selection negative controls.
    """
    if SYNTHETIC_POLICY is None: return module
    leaf = Path(module.__file__).name
    if leaf == 'worker_profile.py':
        SYNTHETIC_SOURCE_POLICY_SELECTIONS.add(module.COMPLETE_ENVIRONMENT_POLICY_SHA256)
        module.COMPLETE_ENVIRONMENT_POLICY_SHA256 = SYNTHETIC_POLICY['sha256']
    for owner, name in (('native-worker-capture.py', 'package'),
                        ('capture.py', 'worker_runtime'),
                        ('worker_runtime.py', 'worker_profile')):
        if leaf == owner:
            original = getattr(module, name)
            def selected(*args, _original=original, **kwargs):
                return fixture_policy_module(_original(*args, **kwargs))
            setattr(module, name, selected)
    return module
def call(fn):
    try: return True, fn(), None
    except (ValueError, TypeError, KeyError, RuntimeError) as exc: return False, None, str(exc)
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if isinstance(value, bytes) else (json.dumps(value, indent=2) + '\n').encode()
    with path.open('xb') as stream: stream.write(raw)
    return pin(path)

def synthetic_plan_environment(plan, response=None):
    if SYNTHETIC_POLICY is None: return
    plan['config_source_pins'] = [FIXTURE_REPLACEMENTS.get(row['path'], row)
                                 for row in plan['config_source_pins']]
    if 'complete_environment_policy' in plan['binding']:
        plan['binding']['complete_environment_policy'] = copy.deepcopy(SYNTHETIC_POLICY)
    if response is not None:
        response['config']['shell_environment_policy']['set'][INPUTS['approved_name']] = 'SYNTHETIC_' + '0' * 54

def synthetic_environment():
    """Use saved response shape with an owned, visibly synthetic HOME fixture.

    Never read or re-pin the mutable HOME or project configuration. The
    historical inputs remain unchanged and available to the strict default.
    """
    global POLICY, SYNTHETIC_POLICY
    name = INPUTS['approved_name']; value = 'SYNTHETIC_' + '0' * 54
    home = write(WORK / 'fixtures/SYNTHETIC_HOME.toml',
        ('# Synthetic source-test data; no native qualification.\n'
         '[shell_environment_policy.set]\n' + name + '=' + json.dumps(value) + '\n'
         '[mcp_servers.cua_repl]\ncommand="SYNTHETIC"\n'
         '[mcp_servers.https-mcp-tafsir-net-mcp]\nurl="https://example.invalid"\n'
         '[mcp_servers.node_repl]\ncommand="SYNTHETIC"\n').encode())
    empty = write(WORK / 'fixtures/SYNTHETIC_PROJECT.toml', b'# Synthetic empty project layer.\n')
    for row in PLAN['config_source_pins']:
        FIXTURE_REPLACEMENTS[row['path']] = home if row['path'] == INPUTS['home_config']['path'] else empty
    captured(POLICY)
    policy = dict(schema='ordinary.effective-config.synthetic-policy-fixture.v1',
        home_config=home, selector='SYNTHETIC_SOURCE_TEST_ONLY',
        scope='Owned synthetic environment fixture; no historical or native proof',
        native_qualification=False)
    policy['approved_existing_entry'] = dict(name=name, value_sha256=sha(value.encode()),
        value_bytes=len(value), value_source='Owned SYNTHETIC_HOME.toml test data')
    prescribed = PLAN['profile_proposal']['effective_config_projection']['shell_environment_policy']['set']
    complete_sha = sha(canonical(dict(prescribed, **{name: value})))
    policy['expected_complete_set_sha256_for_synthetic_fixture'] = complete_sha
    policy['synthetic_fixture'] = True
    POLICY = SYNTHETIC_POLICY = write(WORK / 'fixtures/SYNTHETIC_POLICY.json', policy)
    INPUTS.update(home_config=home, policy=POLICY, complete_set_sha256=complete_sha,
        fixture_scope='SYNTHETIC_ENVIRONMENT_WITH_SAVED_RESPONSE_SHAPE; NOT_HISTORICAL_NATIVE_PROOF')
    synthetic_plan_environment(PLAN, RESPONSE)
    write(WORK / 'fixtures/SYNTHETIC_INPUTS.json', INPUTS)

MISSING = object()

def bind_silent_load(plan, ready_text=None):
    cfg = plan['visibility']; binding = plan['binding']
    binding['load_input'] = PROFILE.silent_load_input(binding, ready_text or cfg['load_spec']['ready_text'])
    cfg['load_input'] = copy.deepcopy(binding['load_input'])
    cfg['load_spec']['load_prompt'] = binding['load_input'][0]['text']


def custody_fixture(name, purpose='ISOLATED_QUALIFICATION', policy=True, repin_profile=None, prompt_ready=None):
    """Coherent caller data cannot choose code or grant policy applicability."""
    fixture = WORK / 'custody-fixtures' / name
    old_bundle = Path(INPUTS['plan']['path']).parent
    old_source = old_bundle.parent / 'candidate/implementaudit'
    original = (old_bundle / 'INPUT_PINS.json').read_bytes()
    assert sha(original) == PLAN['input_pins_sha256']
    replacements = {}
    for leaf in ('NOTIFICATION_DISPOSITIONS.json', 'HOOK_OBSERVATION_CONTRACT.json', 'JSONSCHEMA_RUNTIME.json'):
        replacements[str(old_bundle / leaf)] = write(fixture / leaf, (old_bundle / leaf).read_bytes())
    files = []
    for row in json.loads(original)['files']:
        path = Path(row['path'])
        if path.is_relative_to(old_source): row = pin(SOURCE / path.relative_to(old_source))
        row = FIXTURE_REPLACEMENTS.get(row['path'], row)
        row = replacements.get(row['path'], row)
        if repin_profile is not None and Path(row['path']) == SOURCE / 'skills/implementaudit/scripts/native-capture-adapter/worker_profile.py':
            row = dict(row, bytes=len(repin_profile), sha256=sha(repin_profile))
        files.append(row)
    plan = copy.deepcopy(PLAN)
    plan['adapter_source'] = PROVIDER.MEMBERS['capture.py']
    if purpose is MISSING: plan.pop('purpose')
    else: plan['purpose'] = purpose
    if policy:
        plan['binding']['complete_environment_policy'] = copy.deepcopy(POLICY); files.append(POLICY)
    else:
        config = write(fixture / 'SYNTHETIC_MCP.toml', b'[mcp_servers.cua_repl]\ncommand="SYNTHETIC"\n[mcp_servers.https-mcp-tafsir-net-mcp]\nurl="https://example.invalid"\n[mcp_servers.node_repl]\ncommand="SYNTHETIC"\n')
        files.append(config); plan['config_source_pins'] = [config]
    if purpose != 'ISOLATED_QUALIFICATION':
        cfg = plan['visibility']; cfg['identity']['selected_child'] = 'audit-assess'
        body = json.loads(cfg['load_spec']['expected_output']); body['identity'] = cfg['identity']
        text = json.dumps(body, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n'
        cfg['load_spec']['expected_output'] = text; cfg['load_spec']['ready_text'] = 'LOAD_READY_ONLY ' + sha(text.encode('ascii'))
    # Construct internally consistent untrusted caller metadata using the
    # no-policy producer; applicability must still be enforced by preflight.
    bind_silent_load(plan, prompt_ready)
    bare = copy.deepcopy(plan['binding']); bare.pop('complete_environment_policy', None)
    prepared = PROFILE.prepare(bare, json.loads(captured(PLAN['schemas']['ConfigSchema'])), json.loads(captured(PLAN['schemas']['ClientRequest'])))
    prepared['binding_sha256'] = sha(canonical(plan['binding']))
    plan['profile_proposal'] = prepared
    for key in ('server_argv', 'server_cwd', 'thread_start', 'turn_start', 'use_turn_start'): plan[key] = prepared[key]
    pins = write(fixture / 'INPUT_PINS.json', {'files': files}); plan['input_pins_sha256'] = pins['sha256']
    plan_pin = write(fixture / 'THREAD_METADATA_PLAN.json', plan)
    return fixture, plan_pin, plan

def public_preflight(case):
    root, row, plan = case
    method = PROVIDER.isolated_qualification_preflight if plan.get('purpose') == 'ISOLATED_QUALIFICATION' else PROVIDER.preflight
    return method(row['sha256'], bundle_root=root)

def execution_canary_bytes(raw):
    head = b"__import__('builtins')._policy_custody_probe()\nraise ValueError('SYNTHETIC_CHANGED_CODE_EXECUTED')\n#"
    assert len(raw) > len(head)
    return head + b' ' * (len(raw) - len(head))

class PolicyCustodyTests(unittest.TestCase):
    def test_source_preflight_binds_silent_prompt_to_actual_ready_output_digest(self):
        case = custody_fixture('wrong-silent-ready-token', prompt_ready='LOAD_READY_ONLY ' + '0' * 64)
        with self.assertRaisesRegex(ValueError, 'Silent LOAD prompt differs from exact output/readiness binding'):
            public_preflight(case)

    def setUp(self):
        self.binding = copy.deepcopy(PLAN['binding']); self.binding['complete_environment_policy'] = copy.deepcopy(POLICY)
        self.prescribed = PLAN['profile_proposal']['effective_config_projection']['shell_environment_policy']['set']
        self.schema = json.loads(captured(PLAN['schemas']['ConfigSchema']))
        self.requests = json.loads(captured(PLAN['schemas']['ClientRequest']))
        self.adapter = SOURCE / 'skills/implementaudit/scripts/native-capture-adapter'

    def test_prepare_and_complete_environment_require_explicit_isolated_purpose(self):
        for purpose in (MISSING, None, 'UNKNOWN', 'NATURALLY_WARRANTED_WORKER', 'OFFLINE_FIXTURE', 'ISOLATED_QUALIFICATION'):
            kwargs = {} if purpose is MISSING else {'purpose': purpose}
            want = purpose == 'ISOLATED_QUALIFICATION'
            for name, fn in [('prepare', lambda: PROFILE.prepare(self.binding, self.schema, self.requests, **kwargs)),
                    ('complete', lambda: PROFILE.complete_environment(self.binding, self.prescribed, **kwargs))]:
                with self.subTest(consumer=name, purpose=str(purpose) if purpose is not MISSING else 'MISSING'):
                    ok, _, _ = call(fn); self.assertEqual(ok, want)
            bare = copy.deepcopy(self.binding); bare.pop('complete_environment_policy')
            ok, value, _ = call(lambda: PROFILE.complete_environment(bare, self.prescribed, **kwargs))
            self.assertTrue(ok)
            if ok: self.assertEqual(set(value), {'PATH', 'PATHEXT', 'SystemRoot'})

    def test_runtime_purpose_matrix_and_no_policy_three_entry_behavior(self):
        for purpose in (MISSING, None, 'UNKNOWN', 'NATURALLY_WARRANTED_WORKER', 'OFFLINE_FIXTURE', 'ISOLATED_QUALIFICATION'):
            plan = copy.deepcopy(PLAN); plan['binding'] = copy.deepcopy(self.binding)
            if purpose is MISSING: plan.pop('purpose')
            else: plan['purpose'] = purpose
            with self.subTest(purpose=str(purpose) if purpose is not MISSING else 'MISSING'):
                ok, _, _ = call(lambda: RUNTIME.validate_config(plan, RESPONSE)); self.assertEqual(ok, purpose == 'ISOLATED_QUALIFICATION')
                plan['binding'].pop('complete_environment_policy')
                trimmed = copy.deepcopy(RESPONSE); trimmed['config']['shell_environment_policy']['set'].pop(INPUTS['approved_name'])
                ok, _, _ = call(lambda: RUNTIME.validate_config(plan, trimmed)); self.assertTrue(ok)

    def test_public_preflight_scope_matrix_rejects_coherent_relabels(self):
        for index, purpose in enumerate((MISSING, None, 'UNKNOWN', 'NATURALLY_WARRANTED_WORKER', 'OFFLINE_FIXTURE', 'ISOLATED_QUALIFICATION')):
            for policy in (True, False):
                case = custody_fixture('purpose-' + str(index) + '-' + str(policy), purpose, policy)
                want = purpose == 'ISOLATED_QUALIFICATION' if policy else purpose in ('ISOLATED_QUALIFICATION', 'NATURALLY_WARRANTED_WORKER', 'OFFLINE_FIXTURE')
                with self.subTest(purpose=index, policy=policy):
                    ok, _, _ = call(lambda: public_preflight(case)); self.assertEqual(ok, want)

    def test_package_executes_only_its_once_verified_capture_buffer(self):
        path = self.adapter / 'capture.py'; raw = path.read_bytes(); changed = execution_canary_bytes(raw)
        reads, executed = [], []; reader = Path.read_bytes
        def later(candidate):
            if candidate == path:
                reads.append(1); return raw if len(reads) == 1 else changed
            return reader(candidate)
        with patch.object(builtins, '_policy_custody_probe', lambda: executed.append(True), create=True), patch.object(Path, 'read_bytes', later):
            ok, module, _ = call(PROVIDER.package)
        self.assertTrue(ok); self.assertEqual(executed, []); self.assertEqual(len(reads), 1)
        if ok: self.assertTrue(callable(getattr(module, 'preflight', None)))

    def test_package_missing_wrong_or_drifted_capture_binding_never_executes(self):
        path = self.adapter / 'capture.py'; changed = execution_canary_bytes(path.read_bytes()); reader = Path.read_bytes
        for name in ('missing', 'wrong', 'same_size_drift'):
            mapping = dict(PROVIDER.MEMBERS)
            if name == 'missing': mapping.pop('capture.py')
            elif name == 'wrong': mapping['capture.py'] = '0' * 64
            executed = []
            def swapped(candidate): return changed if candidate == path else reader(candidate)
            with self.subTest(case=name), patch.object(PROVIDER, 'MEMBERS', mapping), patch.object(builtins, '_policy_custody_probe', lambda: executed.append(True), create=True), patch.object(Path, 'read_bytes', swapped):
                ok, _, _ = call(PROVIDER.package); self.assertFalse(ok); self.assertEqual(executed, [])

    def test_capture_runtime_checks_source_before_and_after_actual_preflight(self):
        driver = PROVIDER.package(); case = custody_fixture('runtime-before-after')
        path = self.adapter / 'worker_runtime.py'; changed = execution_canary_bytes(path.read_bytes()); reader = Path.read_bytes
        for when in ('before', 'after'):
            if when == 'after': public_preflight(case)
            executed = []
            def swapped(candidate): return changed if candidate == path else reader(candidate)
            with self.subTest(when=when), patch.object(builtins, '_policy_custody_probe', lambda: executed.append(True), create=True), patch.object(Path, 'read_bytes', swapped):
                ok, _, _ = call(driver.worker_runtime); self.assertFalse(ok); self.assertEqual(executed, [])
        for expected in (None, '0' * 64):
            executed = []
            with self.subTest(trusted_binding=expected), patch.object(driver, 'WORKER_RUNTIME_SHA256', expected, create=True), patch.object(builtins, '_policy_custody_probe', lambda: executed.append(True), create=True), patch.object(Path, 'read_bytes', swapped):
                ok, _, _ = call(driver.worker_runtime); self.assertFalse(ok); self.assertEqual(executed, [])

    def test_preflight_profile_drift_and_coherent_caller_repin_cannot_select_code(self):
        driver = PROVIDER.package(); runtime = driver.worker_runtime()
        path = self.adapter / 'worker_profile.py'; raw = path.read_bytes(); changed = execution_canary_bytes(raw); reader = Path.read_bytes
        opener = Path.open
        for coherent in (False, True):
            case = custody_fixture('preflight-profile-' + str(coherent), repin_profile=changed if coherent else None)
            fixture, row, plan = case; reads, executed = [], []
            def swapped(candidate):
                if candidate == path:
                    reads.append(1)
                    return changed
                return reader(candidate)
            def opened(candidate, *args, **kwargs):
                # file_record hashes through open(), while the old code loader
                # separately uses read_bytes(). Model both streams only when
                # the caller metadata is coherently re-pinned to changed bytes.
                if coherent and candidate == path: return io.BytesIO(changed)
                return opener(candidate, *args, **kwargs)
            with self.subTest(coherent_repin=coherent), patch.object(builtins, '_policy_custody_probe', lambda: executed.append(True), create=True), patch.object(Path, 'open', opened), patch.object(Path, 'read_bytes', swapped):
                ok, _, _ = call(lambda: runtime.preflight(fixture, row['sha256'], driver.OWNER, driver.OWNER_SHA, plan['input_pins_sha256'], self.adapter))
                self.assertFalse(ok); self.assertEqual(executed, [])
        case = custody_fixture('preflight-profile-unbound'); fixture, row, plan = case
        for expected in (None, '0' * 64):
            with self.subTest(trusted_binding=expected), patch.object(runtime, 'WORKER_PROFILE_SHA256', expected, create=True):
                ok, _, _ = call(lambda: runtime.preflight(fixture, row['sha256'], driver.OWNER, driver.OWNER_SHA, plan['input_pins_sha256'], self.adapter))
                self.assertFalse(ok)

    def test_runtime_and_profile_loaders_compile_only_the_verified_buffer(self):
        driver = PROVIDER.package(); runtime = driver.worker_runtime(); reader = Path.read_bytes
        for path, loader in ((self.adapter / 'worker_runtime.py', driver.worker_runtime),
                            (self.adapter / 'worker_profile.py', runtime.worker_profile)):
            raw = reader(path); changed = execution_canary_bytes(raw); reads, executed = [], []
            def later(candidate):
                if candidate == path:
                    reads.append(1); return raw if len(reads) == 1 else changed
                return reader(candidate)
            with self.subTest(member=path.name), patch.object(builtins, '_policy_custody_probe', lambda: executed.append(True), create=True), patch.object(Path, 'read_bytes', later):
                ok, _, _ = call(loader); self.assertTrue(ok); self.assertEqual(executed, []); self.assertEqual(len(reads), 1)

    def test_runtime_profile_drift_after_preflight_cannot_accept_fifth_entry(self):
        case = custody_fixture('runtime-profile-drift'); plan, _, _ = public_preflight(case)
        driver = PROVIDER.package(); runtime = driver.worker_runtime()
        fifth = copy.deepcopy(RESPONSE); fifth['config']['shell_environment_policy']['set']['UNAPPROVED_FIFTH'] = 'synthetic'
        ok, _, _ = call(lambda: runtime.validate_config(plan, fifth)); self.assertFalse(ok)
        path = self.adapter / 'worker_profile.py'; original = path.read_bytes()
        changed = original.replace(b'return dict(prescribed, **{name: value})', b"return dict(prescribed, **{name: value}, UNAPPROVED_FIFTH='synthetic')")
        self.assertNotEqual(sha(original), sha(changed)); reader = Path.read_bytes
        def swapped(candidate): return changed if candidate == path else reader(candidate)
        with patch.object(Path, 'read_bytes', swapped):
            ok, _, _ = call(lambda: runtime.validate_config(plan, fifth)); self.assertFalse(ok)

    def test_runtime_missing_wrong_profile_binding_refuses_before_execution(self):
        runtime = PROVIDER.package().worker_runtime(); plan = copy.deepcopy(PLAN); plan['binding'] = self.binding
        path = self.adapter / 'worker_profile.py'; changed = execution_canary_bytes(path.read_bytes()); reader = Path.read_bytes
        for expected in (None, '0' * 64):
            executed = []
            def swapped(candidate): return changed if candidate == path else reader(candidate)
            with self.subTest(trusted_binding=expected), patch.object(runtime, 'WORKER_PROFILE_SHA256', expected, create=True), patch.object(builtins, '_policy_custody_probe', lambda: executed.append(True), create=True), patch.object(Path, 'read_bytes', swapped):
                ok, _, _ = call(lambda: runtime.validate_config(plan, RESPONSE)); self.assertFalse(ok); self.assertEqual(executed, [])

    def test_verified_runtime_and_profile_modules_can_be_reused_without_reread(self):
        driver = PROVIDER.package(); runtime = driver.worker_runtime()
        loader = getattr(runtime, 'worker_profile', None); self.assertTrue(callable(loader), 'Source-bound profile loader is absent')
        if not callable(loader): return
        profile = loader(); reader = Path.read_bytes; paths = {self.adapter / 'worker_runtime.py', self.adapter / 'worker_profile.py'}
        def no_code_read(path):
            if path in paths: raise AssertionError('A retained implementation must not reread its code')
            return reader(path)
        with patch.object(Path, 'read_bytes', no_code_read):
            self.assertEqual(runtime.project_config({'x': False}, {'x': False}), {'x': False})
            ok, complete, _ = call(lambda: profile.complete_environment(self.binding, self.prescribed, purpose='ISOLATED_QUALIFICATION'))
        self.assertTrue(ok)
        if ok: self.assertEqual(sha(canonical(complete)), INPUTS['complete_set_sha256'])

    def test_affected_loaders_preserve_alias_refusal(self):
        driver = PROVIDER.package(); runtime = driver.worker_runtime()
        plan = copy.deepcopy(PLAN); plan['binding'] = self.binding
        original = Path.is_symlink
        for target, fn in [(self.adapter / 'capture.py', PROVIDER.package),
                (self.adapter / 'worker_runtime.py', driver.worker_runtime),
                (self.adapter / 'worker_profile.py', lambda: runtime.validate_config(plan, RESPONSE))]:
            def alias(path): return path == target or original(path)
            with self.subTest(target=target.name), patch.object(Path, 'is_symlink', alias):
                ok, _, _ = call(fn); self.assertFalse(ok)

    def test_affected_loaders_preserve_parent_reparse_flag_refusal(self):
        driver = PROVIDER.package(); runtime = driver.worker_runtime()
        plan = copy.deepcopy(PLAN); plan['binding'] = self.binding
        original = Path.lstat
        def reparse(path):
            result = original(path)
            if path == self.adapter:
                return types.SimpleNamespace(st_mode=result.st_mode, st_file_attributes=0x400)
            return result
        for name, fn in [('package', PROVIDER.package), ('runtime', driver.worker_runtime),
                         ('profile', lambda: runtime.validate_config(plan, RESPONSE))]:
            with self.subTest(loader=name), patch.object(Path, 'lstat', reparse):
                ok, _, _ = call(fn); self.assertFalse(ok)

class EffectiveConfigTests(unittest.TestCase):
    def setUp(self):
        self.plan = copy.deepcopy(PLAN)
        self.plan['binding']['complete_environment_policy'] = copy.deepcopy(POLICY)
        self.response = copy.deepcopy(RESPONSE)

    def test_seventeen_saved_separator_pairs_are_accepted_as_ordered_same_paths(self):
        expected = PLAN['profile_proposal']['effective_config_projection']['skills']['config']
        actual = RESPONSE['config']['skills']['config']
        self.assertEqual((len(actual), len(expected)), (17, 17))
        ok, _, _ = call(lambda: RUNTIME.project_config({'skills': {'config': actual}}, {'skills': {'config': expected}}))
        self.assertTrue(ok, 'The observed separator-only representation still refuses')

    def test_skill_list_rejects_identity_order_kind_count_and_boolean_changes(self):
        expected = [{'path': 'C:/Synthetic/A/SKILL.md', 'enabled': False},
                    {'path': 'C:/Synthetic/B/SKILL.md', 'enabled': False}]
        cases = {}
        for name, field, value in [('drive', 'path', 'D:/Synthetic/A/SKILL.md'),
            ('case', 'path', 'C:/synthetic/A/SKILL.md'), ('alias', 'path', 'C:/SYNTH~1/A/SKILL.md'),
            ('relative', 'path', 'Synthetic/A/SKILL.md'), ('traversal', 'path', 'C:/Synthetic/../A/SKILL.md'),
            ('dot', 'path', 'C:/Synthetic/./A/SKILL.md'), ('integer_false', 'enabled', 0),
            ('float_false', 'enabled', 0.0), ('enabled_true', 'enabled', True), ('enabled_string', 'enabled', 'false')]:
            rows = copy.deepcopy(expected); rows[0][field] = value; cases[name] = rows
        cases.update(reorder=list(reversed(expected)), missing=expected[:1], extra=expected + [expected[0]],
            duplicate=[expected[0], expected[0]], kind=[{'name': 'A', 'enabled': False}, expected[1]],
            extra_field=[{**expected[0], 'name': 'A'}, expected[1]])
        for name, actual in cases.items():
            with self.subTest(case=name):
                ok, _, _ = call(lambda: RUNTIME.project_config({'skills': {'config': actual}}, {'skills': {'config': expected}}))
                self.assertFalse(ok)
        for name, rows in [('duplicate', [expected[0], expected[0]]),
            ('relative', [{'path': 'relative/SKILL.md', 'enabled': False}]),
            ('traversal', [{'path': 'C:/Synthetic/../A/SKILL.md', 'enabled': False}])]:
            with self.subTest(coherent_invalid=name):
                ok, _, _ = call(lambda: RUNTIME.project_config({'skills': {'config': rows}}, {'skills': {'config': rows}}))
                self.assertFalse(ok)

    def test_breadcrumbs_are_structural_complete_and_never_echo_values(self):
        expected = {'skills': {'config': [{'path': 'C:/Synthetic/A', 'enabled': False}]}}
        actual = {'skills': {'config': [{'path': 'C:/Synthetic/DIFFERENT', 'enabled': False}]}}
        ok, _, error = call(lambda: RUNTIME.project_config(actual, expected))
        self.assertFalse(ok); self.assertIn('config.skills.config[0].path', error)
        self.assertNotIn('DIFFERENT', error)
        private_key = 'PRIVATE/key=VALUE'
        ok, _, error = call(lambda: RUNTIME.project_config({'safe': {private_key: True}}, {'safe': {private_key: False}}))
        self.assertFalse(ok); self.assertIn('config.safe', error); self.assertNotIn(private_key, error)

    def test_other_lists_and_unrelated_exact_values_are_not_normalized(self):
        for actual, expected in [({'other': ['C:\\Synthetic']}, {'other': ['C:/Synthetic']}),
                ({'features': {'plugins': 0}}, {'features': {'plugins': False}}),
                ({'features': {'plugins': True}}, {'features': {'plugins': False}})]:
            ok, _, _ = call(lambda: RUNTIME.project_config(actual, expected)); self.assertFalse(ok)
        ok, _, _ = call(lambda: RUNTIME.project_config({'features': {'plugins': False}, 'unselected': None}, {'features': {'plugins': False}}))
        self.assertTrue(ok)

    def test_actual_saved_config_passes_only_with_owner_complete_policy(self):
        ok, _, _ = call(lambda: RUNTIME.validate_config(self.plan, self.response))
        self.assertTrue(ok, 'Saved response fails with both justified corrections and the explicit policy')
        ok, _, error = call(lambda: RUNTIME.validate_config(PLAN, self.response))
        self.assertFalse(ok); self.assertIn('config.shell_environment_policy.set', error)

    def test_runtime_rejects_extra_or_drifted_complete_environment_entries(self):
        approved_name = INPUTS['approved_name']
        for name, key, value in [('extra', 'UNAPPROVED_FIFTH', 'synthetic'),
                ('approved_drift', approved_name, 'synthetic-drift'), ('requested_drift', 'PATHEXT', '.OTHER')]:
            result = copy.deepcopy(self.response); result['config']['shell_environment_policy']['set'][key] = value
            with self.subTest(case=name):
                ok, _, error = call(lambda: RUNTIME.validate_config(self.plan, result))
                self.assertFalse(ok); self.assertIn('config.shell_environment_policy.set', error)

    def test_runtime_retains_permission_and_mcp_exclusions(self):
        for name in ('grant', 'depth', 'network', 'mcp', 'feature'):
            result = copy.deepcopy(self.response); config = result['config']
            if name == 'grant': config['permissions']['worker_load']['filesystem']['C:/UNAPPROVED'] = 'read'
            elif name == 'depth': config['permissions']['worker_load']['filesystem']['glob_scan_max_depth'] = 3
            elif name == 'network': config['permissions']['worker_load']['network']['enabled'] = True
            elif name == 'mcp': config['mcp_servers']['cua_repl']['enabled'] = 0
            else: config['features']['plugins'] = True
            with self.subTest(case=name):
                ok, _, _ = call(lambda: RUNTIME.validate_config(self.plan, result)); self.assertFalse(ok)

    def test_profile_binds_policy_without_serializing_the_approved_value(self):
        ok, proposal, _ = call(lambda: PROFILE.prepare(self.plan['binding'],
            json.loads(captured(PLAN['schemas']['ConfigSchema'])), json.loads(captured(PLAN['schemas']['ClientRequest'])), purpose=self.plan.get('purpose')))
        self.assertTrue(ok, 'Profile cannot bind the explicit complete policy')
        if ok:
            self.assertEqual(len(proposal['effective_config_projection']['shell_environment_policy']['set']), 3)
            self.assertNotIn(INPUTS['approved_name'], '\n'.join(proposal['server_argv']))
            self.assertEqual(proposal['effective_config_projection']['shell_environment_policy']['inherit'], 'none')

    def test_policy_pin_drift_refuses_at_profile_and_runtime(self):
        plan = copy.deepcopy(self.plan); plan['binding']['complete_environment_policy']['sha256'] = '0' * 64
        ok, _, _ = call(lambda: PROFILE.prepare(plan['binding'], json.loads(captured(PLAN['schemas']['ConfigSchema'])),
            json.loads(captured(PLAN['schemas']['ClientRequest'])), purpose=plan.get('purpose'))); self.assertFalse(ok)
        ok, _, _ = call(lambda: RUNTIME.validate_config(plan, self.response)); self.assertFalse(ok)

    def test_explicit_null_policy_is_not_an_absent_policy(self):
        plan = copy.deepcopy(self.plan); plan['binding']['complete_environment_policy'] = None
        ok, _, _ = call(lambda: PROFILE.prepare(plan['binding'], json.loads(captured(PLAN['schemas']['ConfigSchema'])),
            json.loads(captured(PLAN['schemas']['ClientRequest'])), purpose=plan.get('purpose'))); self.assertFalse(ok)
        result = copy.deepcopy(self.response)
        result['config']['shell_environment_policy']['set'].pop(INPUTS['approved_name'])
        ok, _, _ = call(lambda: RUNTIME.validate_config(plan, result)); self.assertFalse(ok)

    def test_policy_derivation_consumes_the_same_captured_bytes_it_hashes(self):
        original = captured(POLICY); reads = []; original_reader = Path.read_bytes
        def changing_read(path):
            if str(path) == POLICY['path']:
                reads.append(1)
                return original if len(reads) == 1 else b'{}'
            return original_reader(path)
        prescribed = PLAN['profile_proposal']['effective_config_projection']['shell_environment_policy']['set']
        with patch.object(Path, 'read_bytes', changing_read):
            ok, complete, _ = call(lambda: PROFILE.complete_environment(self.plan['binding'], prescribed, purpose=self.plan.get('purpose')))
        self.assertTrue(ok)
        if ok: self.assertEqual(sha(canonical(complete)), INPUTS['complete_set_sha256'])
        self.assertEqual(len(reads), 1)

    def test_home_value_derivation_consumes_the_same_captured_bytes_it_hashes(self):
        method = getattr(PROFILE, 'complete_environment', None)
        self.assertTrue(callable(method), 'Complete environment policy consumer is absent')
        if not callable(method): return
        home_pin = INPUTS['home_config']; original = captured(home_pin); reads = []
        original_reader = Path.read_bytes
        def changing_read(path):
            if str(path) == home_pin['path']:
                reads.append(1)
                return original if len(reads) == 1 else b'[shell_environment_policy.set]\nUNAPPROVED="later"\n'
            return original_reader(path)
        prescribed = PLAN['profile_proposal']['effective_config_projection']['shell_environment_policy']['set']
        with patch.object(Path, 'read_bytes', changing_read):
            ok, complete, _ = call(lambda: method(self.plan['binding'], prescribed, purpose=self.plan.get('purpose')))
        self.assertTrue(ok)
        if ok: self.assertEqual(sha(canonical(complete)), INPUTS['complete_set_sha256'])
        self.assertEqual(len(reads), 1)

    def test_real_preflight_checks_policy_and_native_file_map_merge(self):
        old_bundle = Path(INPUTS['plan']['path']).parent
        old_source = old_bundle.parent / 'candidate/implementaudit'
        raw = (old_bundle / 'INPUT_PINS.json').read_bytes()
        self.assertEqual(sha(raw), PLAN['input_pins_sha256'])
        original_pins = json.loads(raw)['files']
        cases = [('approved', True, True, None), ('unapproved_existing', False, False, None),
            ('fifth_entry', True, False, '[shell_environment_policy.set]\nUNAPPROVED_FIFTH="synthetic"\n'),
            ('approved_drift', True, False, '[shell_environment_policy.set]\n' + INPUTS['approved_name'] + '="synthetic-drift"\n'),
            ('CLI_prescribed_value_wins', True, True, '[shell_environment_policy.set]\nPATHEXT=".OTHER"\n'),
            ('empty_map_does_not_clear', False, False, '[shell_environment_policy]\nset={}\n')]
        for name, selected, want, overlay in cases:
            fixture = WORK / 'preflight' / name
            replacements = {}
            for filename in ('NOTIFICATION_DISPOSITIONS.json', 'HOOK_OBSERVATION_CONTRACT.json', 'JSONSCHEMA_RUNTIME.json'):
                replacements[str(old_bundle / filename)] = write(fixture / filename, (old_bundle / filename).read_bytes())
            files = []
            for row in original_pins:
                path = Path(row['path'])
                if path.is_relative_to(old_source):
                    row = pin(SOURCE / path.relative_to(old_source))
                row = FIXTURE_REPLACEMENTS.get(row['path'], row)
                files.append(replacements.get(row['path'], row))
            plan = copy.deepcopy(PLAN)
            plan['adapter_source'] = PROVIDER.MEMBERS['capture.py']
            if selected:
                plan['binding']['complete_environment_policy'] = copy.deepcopy(POLICY)
                files.append(POLICY)
            if overlay is not None:
                entry = write(fixture / 'SYNTHETIC_OVERLAY.toml', overlay.encode())
                files.append(entry); plan['config_source_pins'].append(entry)
            prepared_ok, prepared, _ = call(lambda: PROFILE.prepare(plan['binding'],
                json.loads(captured(PLAN['schemas']['ConfigSchema'])), json.loads(captured(PLAN['schemas']['ClientRequest'])), purpose=plan.get('purpose')))
            # The baseline cannot prepare the new binding. Its original proposal
            # is retained solely so the actual preflight can report that refusal.
            if prepared_ok:
                plan['profile_proposal'] = prepared
                for key in ('server_argv', 'server_cwd', 'thread_start', 'turn_start', 'use_turn_start'):
                    plan[key] = prepared[key]
            pins = write(fixture / 'INPUT_PINS.json', {'files': files})
            plan['input_pins_sha256'] = pins['sha256']
            plan_pin = write(fixture / 'THREAD_METADATA_PLAN.json', plan)
            ok, _, error = call(lambda: PROVIDER.isolated_qualification_preflight(plan_pin['sha256'], bundle_root=fixture))
            with self.subTest(case=name):
                self.assertEqual(ok, want)
                if not want: self.assertIn('environment', error.lower())

class McpRuntimeSelectionTests(unittest.TestCase):
    def setUp(self):
        scope = INPUTS['mcp_attempt03']
        self.plan = json.loads(captured(scope['plan']))
        wire = captured(scope['stdout'])
        def frame(row):
            raw = wire[row['offset']:row['offset'] + row['bytes']]
            self.assertEqual(sha(raw), row['sha256'])
            return json.loads(raw)
        self.config = frame(scope['config_frame'])['result']
        synthetic_plan_environment(self.plan, self.config)
        thread = frame(scope['thread_frame'])['result']['thread']
        self.thread = scope['thread_id']; self.assertEqual(thread['id'], self.thread)
        self.reply = json.loads(captured(scope['status_fixture']))
        self.request = json.loads(captured(scope['request_fixture']))
        self.names = ['cua_repl', 'https-mcp-tafsir-net-mcp', 'node_repl']

    def facts(self, plan=None, config=None):
        return {'effective_selection': RUNTIME.validate_config(plan or self.plan, config or self.config),
                'thread_metadata': {'thread_id': self.thread, 'ephemeral': True}}

    def select(self, reply=None, plan=None, facts=None, thread=None):
        calls = []; selected_plan = self.plan if plan is None else plan
        selected_facts = self.facts(selected_plan) if facts is None else facts
        value = self.reply if reply is None else reply
        def response(request):
            calls.append(copy.deepcopy(request)); return copy.deepcopy(value)
        ok, _, error = call(lambda: RUNTIME.validate_thread_selection(selected_plan, response,
            self.thread if thread is None else thread, selected_facts))
        return ok, selected_facts, calls, error

    def test_actual_complete_three_disabled_rows_report_no_active_selection(self):
        ok, facts, calls, error = self.select()
        self.assertTrue(ok, error)
        self.assertEqual(calls, [self.request])
        result = facts.get('mcp_runtime_selection')
        self.assertIsInstance(result, dict)
        if isinstance(result, dict):
            self.assertEqual(result['selection'], 'NO_ACTIVE_MCP_SELECTION')
            self.assertEqual(result['registered_disabled_names'], self.names)
            self.assertEqual(result['registered_disabled_count'], 3)
            self.assertEqual(result['response_identity']['id'], 13)
            self.assertEqual(result['response_identity']['thread_id'], self.thread)
            self.assertEqual(result['response_identity']['canonical_response_sha256'], sha(canonical(self.reply)))
            self.assertIs(result['complete_tool_inventory_observed'], False)
        self.assertNotIn('mcp_runtime_selection_empty', facts)
        self.assertIsNot(facts.get('complete_tool_inventory_observed'), True)

    def test_empty_status_with_three_declared_configured_names_refuses(self):
        reply = copy.deepcopy(self.reply); reply['result']['data'] = []
        self.assertFalse(self.select(reply=reply)[0])

    def test_complete_registry_larger_than_requested_page_cannot_qualify(self):
        plan = copy.deepcopy(self.plan); config = copy.deepcopy(self.config)
        names = ['synthetic_' + str(index) for index in range(101)]
        plan['binding']['mcp_names'] = names
        registry = {name: {'enabled': False} for name in names}
        plan['profile_proposal']['effective_config_projection']['mcp_servers'] = copy.deepcopy(registry)
        config['config']['mcp_servers'] = registry
        facts = self.facts(plan, config)
        reply = {'id': 13, 'result': {'data': [{**self.reply['result']['data'][0], 'name': name} for name in names], 'nextCursor': None}}
        self.assertFalse(self.select(reply=reply, plan=plan, facts=facts)[0])

    def test_genuinely_empty_declared_and_observed_registry_is_distinct_positive(self):
        plan = copy.deepcopy(self.plan); config = copy.deepcopy(self.config)
        plan['binding']['mcp_names'] = []; plan['binding'].pop('complete_environment_policy')
        plan['profile_proposal']['effective_config_projection']['mcp_servers'] = {}
        config['config']['mcp_servers'] = {}
        config['config']['shell_environment_policy']['set'] = copy.deepcopy(plan['profile_proposal']['effective_config_projection']['shell_environment_policy']['set'])
        facts = self.facts(plan, config); reply = {'id': 13, 'result': {'data': [], 'nextCursor': None}}
        ok, facts, _, error = self.select(reply=reply, plan=plan, facts=facts)
        self.assertTrue(ok, error)
        result = facts.get('mcp_runtime_selection'); self.assertIsInstance(result, dict)
        if isinstance(result, dict): self.assertEqual(result['registered_disabled_count'], 0)

    def test_config_registry_and_declared_names_must_agree_completely(self):
        for case in ('extra_disabled', 'missing', 'missing_registry', 'wrong_enabled', 'empty_declared', 'duplicate_declared', 'case_alias'):
            plan = copy.deepcopy(self.plan); config = copy.deepcopy(self.config)
            if case == 'extra_disabled': config['config']['mcp_servers']['extra'] = {'enabled': False}
            elif case == 'missing': config['config']['mcp_servers'].pop('node_repl')
            elif case == 'missing_registry': config['config'].pop('mcp_servers')
            elif case == 'wrong_enabled': config['config']['mcp_servers']['node_repl']['enabled'] = 0
            elif case == 'empty_declared': plan['binding']['mcp_names'] = []
            elif case == 'duplicate_declared': plan['binding']['mcp_names'].append('node_repl')
            else: plan['binding']['mcp_names'][0] = 'CUA_REPL'
            with self.subTest(case=case):
                ok, _, _ = call(lambda: RUNTIME.validate_config(plan, config)); self.assertFalse(ok)

    def test_row_name_population_is_typed_unique_exact_and_complete(self):
        for case in ('missing', 'extra', 'duplicate', 'case_alias', 'unknown', 'numeric', 'null', 'dict'):
            reply = copy.deepcopy(self.reply); rows = reply['result']['data']
            if case == 'missing': rows.pop()
            elif case == 'extra': rows.append({**rows[0], 'name': 'extra'})
            elif case == 'duplicate': rows[1] = copy.deepcopy(rows[0])
            else: rows[0]['name'] = {'case_alias': 'CUA_REPL', 'unknown': 'foreign', 'numeric': 1, 'null': None, 'dict': {}}[case]
            with self.subTest(case=case): self.assertFalse(self.select(reply=reply)[0])

    def test_every_other_runtime_status_and_unavailable_value_refuses(self):
        schema = json.loads(captured(self.plan['schemas']['ListMcpServerStatusResponse']))
        values = [x for x in schema['definitions']['McpServerConnectionStatus']['enum'] if x != 'disabled']
        values += [None, '', 'unknown', 0, False, [], {}]
        for status in values:
            reply = copy.deepcopy(self.reply); reply['result']['data'][0]['runtimeStatus'] = status
            with self.subTest(status=status): self.assertFalse(self.select(reply=reply)[0])

    def test_disabled_rows_with_capabilities_auth_or_plugin_information_refuse(self):
        variants = [('tools', {'t': {'name': 't', 'inputSchema': {}}}),
            ('resources', [{'name': 'r', 'uri': 'test://resource'}]),
            ('resourceTemplates', [{'name': 'r', 'uriTemplate': 'test://{name}'}]),
            ('pluginId', 'synthetic'), ('serverInfo', {'name': 'synthetic', 'version': '1'})]
        auth = json.loads(captured(self.plan['schemas']['ListMcpServerStatusResponse']))['definitions']['McpAuthStatus']['enum']
        variants += [('authStatus', x) for x in auth if x != 'unsupported']
        for field, value in variants:
            reply = copy.deepcopy(self.reply); reply['result']['data'][0][field] = value
            with self.subTest(field=field, value=value): self.assertFalse(self.select(reply=reply)[0])

    def test_all_row_fields_are_explicit_and_empty_containers_are_typed(self):
        for field in self.reply['result']['data'][0]:
            reply = copy.deepcopy(self.reply); reply['result']['data'][0].pop(field)
            with self.subTest(missing=field): self.assertFalse(self.select(reply=reply)[0])
        for field, values in [('tools', [None, [], False, 0, '']), ('resources', [None, {}, False, 0, '']),
                ('resourceTemplates', [None, {}, False, 0, '']), ('pluginId', ['', False, 0, {}]),
                ('serverInfo', ['', False, 0, {}]), ('authStatus', [None, False, 0, [], {}])]:
            for value in values:
                reply = copy.deepcopy(self.reply); reply['result']['data'][0][field] = value
                with self.subTest(field=field, value=value): self.assertFalse(self.select(reply=reply)[0])
        reply = copy.deepcopy(self.reply); reply['result']['data'][0]['unknown'] = None
        self.assertFalse(self.select(reply=reply)[0])

    def test_result_and_envelope_are_closed_with_explicit_null_cursor(self):
        for case in ('missing_cursor', 'string_cursor', 'empty_cursor', 'false_cursor', 'extra_result', 'missing_data',
                     'null_data', 'dict_data', 'extra_frame', 'error_frame', 'missing_result', 'wrong_id', 'float_id'):
            reply = copy.deepcopy(self.reply)
            if case == 'missing_cursor': reply['result'].pop('nextCursor')
            elif case in ('string_cursor', 'empty_cursor', 'false_cursor'): reply['result']['nextCursor'] = {'string_cursor': 'next', 'empty_cursor': '', 'false_cursor': False}[case]
            elif case == 'extra_result': reply['result']['unknown'] = None
            elif case == 'missing_data': reply['result'].pop('data')
            elif case in ('null_data', 'dict_data'): reply['result']['data'] = None if case == 'null_data' else {}
            elif case == 'extra_frame': reply['unknown'] = None
            elif case == 'error_frame': reply['error'] = {'code': 0, 'message': 'synthetic'}
            elif case == 'missing_result': reply.pop('result')
            elif case == 'wrong_id': reply['id'] = 14
            else: reply['id'] = 13.0
            with self.subTest(case=case): self.assertFalse(self.select(reply=reply)[0])

    def test_exact_request_and_same_thread_scope_are_required(self):
        for case in ('id', 'method', 'detail', 'limit', 'cursor', 'preset_thread', 'thread_mismatch', 'missing_thread'):
            plan = copy.deepcopy(self.plan); facts = self.facts(); reply = {'id': 13, 'result': {'data': [], 'nextCursor': None}}
            request = plan['readbacks']['mcp']
            if case == 'id': request['id'] = 14
            elif case == 'method': request['method'] = 'different'
            elif case == 'detail': request['params']['detail'] = 'summary'
            elif case == 'limit': request['params']['limit'] = 100.0
            elif case == 'cursor': request['params']['cursor'] = 'next'
            elif case == 'preset_thread': request['params']['threadId'] = 'foreign'
            elif case == 'thread_mismatch': facts['thread_metadata']['thread_id'] = 'foreign'
            else: facts.pop('thread_metadata')
            with self.subTest(case=case):
                ok, _, calls, _ = self.select(reply=reply, plan=plan, facts=facts)
                self.assertFalse(ok); self.assertEqual(calls, [])

    def test_missing_or_changed_config_corroboration_cannot_be_treated_as_empty(self):
        for case in ('absent', 'kind', 'names', 'count', 'disabled_type', 'extra_field'):
            facts = self.facts()
            if case == 'absent': facts.pop('effective_selection')
            elif case == 'kind': facts['effective_selection']['kind'] = 'UNVALIDATED'
            else:
                scope = facts['effective_selection'].setdefault('mcp_registry', {})
                if case == 'names': scope['registered_names'] = []
                elif case == 'count': scope['registered_count'] = False
                elif case == 'disabled_type': scope['all_enabled_false'] = 1
                else: scope['extra'] = None
            reply = {'id': 13, 'result': {'data': [], 'nextCursor': None}}
            with self.subTest(case=case):
                ok, _, calls, _ = self.select(reply=reply, facts=facts)
                self.assertFalse(ok); self.assertEqual(calls, [])

ORIGINAL_INTEGRATION_METHODS = frozenset({
    'EffectiveConfigTests.test_profile_binds_policy_without_serializing_the_approved_value',
    'EffectiveConfigTests.test_policy_pin_drift_refuses_at_profile_and_runtime',
    'EffectiveConfigTests.test_explicit_null_policy_is_not_an_absent_policy',
    'EffectiveConfigTests.test_real_preflight_checks_policy_and_native_file_map_merge',
    'PolicyCustodyTests.test_prepare_and_complete_environment_require_explicit_isolated_purpose',
    'PolicyCustodyTests.test_public_preflight_scope_matrix_rejects_coherent_relabels',
    'PolicyCustodyTests.test_capture_runtime_checks_source_before_and_after_actual_preflight',
    'PolicyCustodyTests.test_preflight_profile_drift_and_coherent_caller_repin_cannot_select_code',
    'PolicyCustodyTests.test_runtime_profile_drift_after_preflight_cannot_accept_fifth_entry',
    'PolicyCustodyTests.test_source_preflight_binds_silent_prompt_to_actual_ready_output_digest',
})
ORIGINAL_CLASSES = (EffectiveConfigTests, PolicyCustodyTests, McpRuntimeSelectionTests)
ORIGINAL_IDENTITIES_SHA256 = '9863b71311478c2685b7517a94dd1ecde8574ba885b4b8ea406c3b5e657429b3'
ORIGINAL_BODIES_SHA256 = '9ebd718a693c86d51a0b7f85939c34169d65bc148fc13d14cc6571ea10a41a6b'
ORIGINAL_ASSERTIONS_SHA256 = '81725e0fc2408ba680961d4abb255ad0166312ab338734f127582a130f1e275e'
COMPONENT_CUSTODY_CALLS = []


def profile_component_binding():
    """Finite test descriptors, deliberately not native/file pins."""
    def token(name, path): return {'path': path, 'test_double': name}
    binding = {
        'native': token('native', 'C:/SOURCE_COMPONENT_ONLY/cli/codex.exe'),
        'code_mode_host': token('companion', 'C:/SOURCE_COMPONENT_ONLY/cli/codex-code-mode-host.exe'),
        'python': token('python', 'C:/SOURCE_COMPONENT_ONLY/python/python.exe'),
        'powershell': token('powershell', 'C:/SOURCE_COMPONENT_ONLY/shell/pwsh.exe'),
        'python_root': 'C:/SOURCE_COMPONENT_ONLY/python', 'cwd': 'C:/SOURCE_COMPONENT_ONLY/work',
        'loader': token('loader', 'C:/SOURCE_COMPONENT_ONLY/reader/reader.py'),
        'load_pins': {name: token(name, 'C:/SOURCE_COMPONENT_ONLY/load/' + name + '.md') for name in sorted(PROFILE.ROLES)},
        'use_pins': [token('use', 'C:/SOURCE_COMPONENT_ONLY/hot/state.md')],
        'excluded_paths': ['C:/SOURCE_COMPONENT_ONLY/excluded/witness.txt'],
        'disabled_skill_paths': [], 'mcp_names': [],
        'model': 'gpt-6-astra', 'provider': 'openai', 'effort': 'low',
        'load_command': "& 'C:/SOURCE_COMPONENT_ONLY/python/python.exe' -I -S -B 'C:/SOURCE_COMPONENT_ONLY/reader/reader.py'",
        'use_command': "Write-Output 'SOURCE_COMPONENT_ONLY'", 'use_expected_output': 'SOURCE_COMPONENT_ONLY\n',
        'use_terminal_text': 'SOURCE_COMPONENT_ONLY', 'complete_environment_policy': copy.deepcopy(POLICY),
    }
    binding['load_input'] = PROFILE.silent_load_input(binding, 'LOAD_READY_ONLY ' + 'b' * 64)
    binding['use_input'] = PROFILE.silent_use_input(binding)
    return binding


def component_tokens(binding):
    return ([binding[key] for key in ('native', 'code_mode_host', 'python', 'powershell', 'loader')]
            + list(binding['load_pins'].values()) + binding['use_pins'])


@contextmanager
def component_file_custody(binding):
    """Mock only the reviewed non-pin descriptors and one virtual shadow path.

    Real schema, profile, policy file, HOME file, projection, and source-loader
    checks are retained. This binding must never enter combined preflight.
    """
    tokens = copy.deepcopy(component_tokens(binding))
    original_exists = Path.exists
    shadow = Path('C:/SOURCE_COMPONENT_ONLY/cli/codex-resources/codex-code-mode-host.exe')
    def checked(value):
        assert value in tokens and set(value) == {'path', 'test_double'}, 'Unselected component descriptor'
        COMPONENT_CUSTODY_CALLS.append(value['test_double'])
        return PROFILE.path_literal(value['path'])
    def exists(path):
        return False if path == shadow else original_exists(path)
    with patch.object(PROFILE, 'checked_pin', checked), patch.object(Path, 'exists', exists):
        yield


def component_schemas():
    return tuple(json.loads(captured(PLAN['schemas'][name])) for name in ('ConfigSchema', 'ClientRequest'))


def component_prescribed(binding):
    return {'PATH': str(PureWindowsPath(binding['powershell']['path']).parent),
            'PATHEXT': '.EXE', 'SystemRoot': 'C:\\Windows'}


class ProfileComponentTests(unittest.TestCase):
    def test_context_basis_policy_purpose_matrix(self):
        binding = profile_component_binding(); schemas = component_schemas()
        prescribed = component_prescribed(binding)
        with component_file_custody(binding):
            for purpose in (MISSING, None, 'UNKNOWN', 'NATURALLY_WARRANTED_WORKER', 'OFFLINE_FIXTURE', 'ISOLATED_QUALIFICATION'):
                kwargs = {} if purpose is MISSING else {'purpose': purpose}
                want = purpose == 'ISOLATED_QUALIFICATION'
                for consumer, fn in (
                        ('context_basis', lambda: PROFILE.prepare_context_basis(binding, *schemas, **kwargs)),
                        ('complete_environment', lambda: PROFILE.complete_environment(binding, prescribed, **kwargs))):
                    with self.subTest(consumer=consumer, purpose='MISSING' if purpose is MISSING else purpose):
                        ok, _, error = call(fn)
                        self.assertEqual(ok, want)
                        if not want:
                            self.assertEqual(error, 'Complete environment policy requires explicit ISOLATED_QUALIFICATION purpose')
                bare = copy.deepcopy(binding); bare.pop('complete_environment_policy')
                ok, value, error = call(lambda: PROFILE.complete_environment(bare, prescribed, **kwargs))
                self.assertTrue(ok, error)
                if ok: self.assertEqual(value, prescribed)
                if ok: self.assertEqual(set(value), {'PATH', 'PATHEXT', 'SystemRoot'})

    def test_context_basis_binds_policy_without_serializing_the_approved_value(self):
        binding = profile_component_binding()
        with component_file_custody(binding):
            result = PROFILE.prepare_context_basis(binding, *component_schemas(), purpose='ISOLATED_QUALIFICATION')
        proposal = result['profile_proposal_without_context']
        self.assertEqual(result['status'], 'CONTEXT_INPUT_REQUIRED')
        self.assertIs(result['native_attempt_enabled'], False)
        self.assertNotIn('context_contract', proposal)
        self.assertNotIn('context_contract', result)
        self.assertEqual(len(proposal['effective_config_projection']['shell_environment_policy']['set']), 3)
        self.assertNotIn(INPUTS['approved_name'], '\n'.join(proposal['server_argv']))
        self.assertEqual(proposal['effective_config_projection']['shell_environment_policy']['inherit'], 'none')
        self.assertNotIn('SYNTHETIC_' + '0' * 54, json.dumps(proposal))
        self.assertNotIn('SYNTHETIC_' + '0' * 54, '\n'.join(proposal['server_argv']))

    def test_context_basis_policy_drift_and_explicit_null_refuse_at_selection(self):
        binding = profile_component_binding(); schemas = component_schemas()
        with component_file_custody(binding):
            positive = PROFILE.prepare_context_basis(binding, *schemas, purpose='ISOLATED_QUALIFICATION')
            self.assertEqual(positive['status'], 'CONTEXT_INPUT_REQUIRED')
            for name, value in (('policy_drift', dict(POLICY, sha256='0' * 64)), ('explicit_null', None)):
                bad = copy.deepcopy(binding); bad['complete_environment_policy'] = value
                with self.subTest(case=name), self.assertRaisesRegex(ValueError, '^Complete environment policy selection differs$'):
                    PROFILE.prepare_context_basis(bad, *schemas, purpose='ISOLATED_QUALIFICATION')


class SourceLoaderComponentTests(unittest.TestCase):
    def test_capture_runtime_refuses_drift_before_and_after_verified_source_load(self):
        path = SOURCE / 'skills/implementaudit/scripts/native-capture-adapter/worker_runtime.py'
        raw = path.read_bytes(); changed = execution_canary_bytes(raw); reader = Path.read_bytes
        self.assertEqual(len(changed), len(raw))
        for when in ('before_source_load', 'after_source_load'):
            driver = PROVIDER.package()
            if when == 'after_source_load':
                self.assertTrue(callable(driver.worker_runtime().worker_profile))
            executed = []
            def swapped(candidate): return changed if candidate == path else reader(candidate)
            with self.subTest(when=when, case='same_size_drift'), patch.object(builtins, '_policy_custody_probe', lambda: executed.append(True), create=True), patch.object(Path, 'read_bytes', swapped):
                with self.assertRaisesRegex(ValueError, '^Selected worker runtime source differs$'):
                    driver.worker_runtime()
            self.assertEqual(executed, [])
            for expected, reason in ((None, 'Selected worker runtime source is unbound'), ('0' * 64, 'Selected worker runtime source differs')):
                with self.subTest(when=when, binding=expected), patch.object(driver, 'WORKER_RUNTIME_SHA256', expected), patch.object(builtins, '_policy_custody_probe', lambda: executed.append(True), create=True), patch.object(Path, 'read_bytes', swapped):
                    with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                        driver.worker_runtime()
                self.assertEqual(executed, [])
            self.assertTrue(callable(driver.worker_runtime().worker_profile))

    def test_runtime_profile_drift_cannot_accept_fifth_entry(self):
        runtime = PROVIDER.package().worker_runtime()
        plan = copy.deepcopy(PLAN); plan['binding']['complete_environment_policy'] = copy.deepcopy(POLICY)
        ok, _, error = call(lambda: runtime.validate_config(plan, RESPONSE))
        self.assertTrue(ok, error)
        fifth = copy.deepcopy(RESPONSE); fifth['config']['shell_environment_policy']['set']['UNAPPROVED_FIFTH'] = 'synthetic'
        ok, _, error = call(lambda: runtime.validate_config(plan, fifth))
        self.assertFalse(ok)
        self.assertIn('config.shell_environment_policy.set', error)
        path = SOURCE / 'skills/implementaudit/scripts/native-capture-adapter/worker_profile.py'
        original = path.read_bytes()
        changed = original.replace(b'return dict(prescribed, **{name: value})', b"return dict(prescribed, **{name: value}, UNAPPROVED_FIFTH='synthetic')")
        self.assertNotEqual(sha(original), sha(changed)); reader = Path.read_bytes
        def swapped(candidate): return changed if candidate == path else reader(candidate)
        with patch.object(Path, 'read_bytes', swapped), self.assertRaisesRegex(ValueError, '^Selected worker profile source differs$'):
            runtime.validate_config(plan, fifth)


def original_source_inventory(raw=None):
    tree = ast.parse(Path(__file__).read_bytes() if raw is None else raw)
    names = {cls.__name__ for cls in ORIGINAL_CLASSES}
    containers = [('', tree.body)] + [(node.name + '.', node.body) for node in tree.body if isinstance(node, ast.ClassDef) and node.name in names]
    methods = []; assertions = []
    for prefix, body in containers:
        for method in body:
            if not isinstance(method, ast.FunctionDef): continue
            if not prefix and method.name not in ('custody_fixture', 'execution_canary_bytes', 'main'): continue
            identity = prefix + method.name
            if method.name.startswith('test_'):
                methods.append([identity, sha(ast.dump(method, include_attributes=False).encode())])
            for node in ast.walk(method):
                if isinstance(node, ast.Assert) or (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr.startswith('assert')):
                    assertions.append([identity, sha(ast.dump(node, include_attributes=False).encode())])
    identities = [row[0] for row in methods]
    validate_original_identities(identities)
    if sha(canonical(sorted(methods))) != ORIGINAL_BODIES_SHA256:
        raise ValueError('Original method bodies differ')
    if len(assertions) != 104 or sha(canonical(sorted(assertions))) != ORIGINAL_ASSERTIONS_SHA256:
        raise ValueError('Original assertions differ')
    return {'original_total': 39, 'original_assertions_preserved': 104,
            'original_identities': sorted(identities), 'original_method_bodies_sha256': ORIGINAL_BODIES_SHA256,
            'original_assertions_sha256': ORIGINAL_ASSERTIONS_SHA256}


def validate_original_identities(identities):
    if (len(identities) != 39 or len(set(identities)) != 39
            or sha(canonical(sorted(identities))) != ORIGINAL_IDENTITIES_SHA256):
        raise ValueError('Original method inventory differs')
    if len(ORIGINAL_INTEGRATION_METHODS) != 10 or not ORIGINAL_INTEGRATION_METHODS < set(identities):
        raise ValueError('Original integration boundary differs')


def case_identity(case): return '.'.join(case.id().rsplit('.', 2)[-2:])


def selected_tests(layer):
    inventory = original_source_inventory()
    original = [case for cls in ORIGINAL_CLASSES for case in unittest.defaultTestLoader.loadTestsFromTestCase(cls)]
    validate_original_identities([case_identity(case) for case in original])
    added = [case for cls in (ProfileComponentTests, SourceLoaderComponentTests) for case in unittest.defaultTestLoader.loadTestsFromTestCase(cls)]
    if len(added) != 5 or len({case_identity(case) for case in added}) != 5:
        raise ValueError('Added component population differs')
    if layer == 'components':
        original_selected = [case for case in original if case_identity(case) not in ORIGINAL_INTEGRATION_METHODS]
        selected = original_selected + added
    elif layer == 'integration':
        original_selected = [case for case in original if case_identity(case) in ORIGINAL_INTEGRATION_METHODS]
        selected = original_selected
    elif layer == 'full':
        original_selected = original; selected = original
    else: raise ValueError('Unknown explicit test layer')
    if not selected: raise ValueError('Empty selected test population')
    component_selected = [case_identity(case) for case in original_selected if case_identity(case) not in ORIGINAL_INTEGRATION_METHODS]
    return unittest.TestSuite(selected), dict(inventory, test_layer=layer,
        original_components_selected=len(component_selected), original_component_identities=component_selected,
        original_integration_selected=sum(case_identity(case) in ORIGINAL_INTEGRATION_METHODS for case in original_selected),
        added_component_identities=[case_identity(case) for case in added] if layer == 'components' else [],
        added_components_selected=5 if layer == 'components' else 0,
        integration_held=sorted(ORIGINAL_INTEGRATION_METHODS), selected_identities=[case_identity(case) for case in selected],
        all_original_methods_qualified=False, actual_preflight_qualified=False, native_qualified=False)


def integration_prerequisite_holds():
    """Body-free early refusal; remaining real integration gates stay in place."""
    holds = []
    for name in ('code_mode_host', 'use_command', 'use_expected_output', 'use_terminal_text', 'context_input'):
        if name not in PLAN['binding']: holds.append('missing_binding:' + name)
    if PLAN['binding']['native']['sha256'] != '081e4de4be8e38fac6ed4d95e3b1a0b9f6d31c090ddc36e1696b349fe406f575':
        holds.append('native_pin_not_selected_by_current_source')
    if PLAN.get('native_version') != '0.154.0-alpha.6.2': holds.append('native_version_not_selected_by_current_source')
    context = PLAN['binding'].get('context_input')
    if context is not None:
        try: document = json.loads(captured(context))
        except (OSError, ValueError, KeyError, TypeError, AssertionError):
            holds.append('context_input_custody_unavailable_or_changed')
        else:
            if document.get('scope') != 'SOURCE_INPUT' or document.get('status') != 'COMPLETE' or document.get('unresolved') != []:
                holds.append('complete_source_input_context_required')
    return holds


def component_boundary_guards():
    rows = []
    def refusal(name, fn, reason):
        try: fn()
        except ValueError as exc:
            if str(exc) != reason: raise AssertionError(name + ': wrong refusal cause') from exc
            rows.append({'name': name, 'result': 'PASS', 'reason': reason})
        else: raise AssertionError(name + ': refusal missing')
    binding = profile_component_binding(); schemas = component_schemas()
    checked = PROFILE.checked_pin; exists = Path.exists
    with component_file_custody(binding):
        basis = PROFILE.prepare_context_basis(binding, *schemas, purpose='ISOLATED_QUALIFICATION')
        assert basis['status'] == 'CONTEXT_INPUT_REQUIRED'
        assert Path.exists(WORK)
        refusal('real_prepare_still_requires_context',
            lambda: PROFILE.prepare(binding, *schemas, purpose='ISOLATED_QUALIFICATION'),
            'Independent context input and request/profile basis required')
        bad = dict(binding['native'], bytes=0, sha256='0' * 64)
        try: PROFILE.checked_pin(bad)
        except AssertionError: rows.append({'name': 'mock_rejects_nonselected_descriptor', 'result': 'PASS'})
        else: raise AssertionError('Component mock accepted a fabricated file pin')
    assert PROFILE.checked_pin is checked and Path.exists is exists
    rows.append({'name': 'file_custody_mock_restored', 'result': 'PASS'})
    for token in component_tokens(binding):
        refusal('restored_checked_pin_rejects_' + token['test_double'], lambda token=token: PROFILE.checked_pin(token), 'exact file pin required')
    refusal('restored_prepare_rejects_descriptor',
        lambda: PROFILE.prepare(binding, *schemas, purpose='ISOLATED_QUALIFICATION'), 'exact file pin required')
    profile_path = SOURCE / 'skills/implementaudit/scripts/native-capture-adapter/worker_profile.py'
    cold = load(profile_path, 'effective_component_cold_profile', synthetic_policy=False)
    refusal('restored_source_selector_rejects_synthetic_policy',
        lambda: cold.complete_environment({'complete_environment_policy': POLICY}, component_prescribed(binding), purpose='ISOLATED_QUALIFICATION'),
        'Complete environment policy selection differs')
    policy_body = json.loads(captured(POLICY)); home_raw = captured(policy_body['home_config'])
    drifted_policy = write(WORK / 'guards/POLICY_FILE_DRIFT.json', captured(POLICY) + b' ')
    stale_policy_pin = dict(POLICY, path=drifted_policy['path'])
    refusal('real_policy_file_bytes_drift_refuses',
        lambda: PROFILE.complete_environment({'complete_environment_policy': stale_policy_pin}, component_prescribed(binding), purpose='ISOLATED_QUALIFICATION'),
        'Complete environment file pin differs')
    approved_name = INPUTS['approved_name']; approved_value = 'SYNTHETIC_' + '0' * 54
    def home_entry(value, extra=''):
        return ('[shell_environment_policy.set]\n' + approved_name + '=' + json.dumps(value) + '\n' + extra).encode()
    variants = (
        ('home_positive', home_raw, None),
        ('home_file_drift', home_raw + b'\n# synthetic drift\n', 'Complete environment file pin differs'),
        ('home_population', home_entry(approved_value, 'UNAPPROVED_FIFTH="synthetic"\n'), 'Complete environment HOME entry population differs'),
        ('home_value_digest', home_entry('X' * 64), 'Approved complete environment value differs'),
        ('home_value_size', home_entry('X' * 63), 'Approved complete environment value differs'),
    )
    for name, raw, reason in variants:
        home = write(WORK / ('guards/' + name + '.toml'), raw)
        variant = copy.deepcopy(policy_body)
        variant['home_config'] = dict(policy_body['home_config'], path=home['path']) if name == 'home_file_drift' else home
        variant_pin = write(WORK / ('guards/' + name + '-policy.json'), variant)
        with patch.object(PROFILE, 'COMPLETE_ENVIRONMENT_POLICY_SHA256', variant_pin['sha256']):
            selected_binding = {'complete_environment_policy': variant_pin}
            operation = lambda: PROFILE.complete_environment(selected_binding, component_prescribed(binding), purpose='ISOLATED_QUALIFICATION')
            if reason is None:
                complete = operation()
                assert complete == dict(component_prescribed(binding), **{approved_name: approved_value})
                rows.append({'name': 'real_home_file_positive', 'result': 'PASS'})
            else: refusal('real_' + name + '_refuses', operation, reason)
    context = INPUTS['component_context_fixture']; document = json.loads(captured(context)); basis_sha = document['basis_sha256']
    assert document['scope'] == 'OFFLINE_SYNTHETIC'
    contract = cold.context_contract_from_input({'context_input': context}, basis_sha, purpose='OFFLINE_FIXTURE')
    assert contract['scope'] == 'OFFLINE_SYNTHETIC'
    rows.append({'name': 'real_offline_context_positive', 'result': 'PASS'})
    refusal('real_context_rejects_synthetic_isolated_input',
        lambda: cold.context_contract_from_input({'context_input': context}, basis_sha, purpose='ISOLATED_QUALIFICATION'),
        'Synthetic context cannot qualify native input')
    refusal('real_context_rejects_missing_input',
        lambda: cold.context_contract_from_input({}, basis_sha, purpose='OFFLINE_FIXTURE'),
        'Independent context input and request/profile basis required')
    refusal('real_context_rejects_wrong_basis',
        lambda: cold.context_contract_from_input({'context_input': context}, '0' * 64, purpose='OFFLINE_FIXTURE'),
        'Context source or generated request/profile basis differs')
    unresolved = copy.deepcopy(document); unresolved['status'] = 'UNRESOLVED'; unresolved['unresolved'] = ['SOURCE_COMPONENT_ONLY']
    unresolved_pin = write(WORK / 'guards/UNRESOLVED_CONTEXT.json', unresolved)
    refusal('real_context_rejects_unresolved_input',
        lambda: cold.context_contract_from_input({'context_input': unresolved_pin}, basis_sha, purpose='OFFLINE_FIXTURE'),
        'Unresolved production context inputs prevent preparation')
    runtime = PROVIDER.package().worker_runtime(); expected = runtime.WORKER_PROFILE_SHA256
    raw = profile_path.read_bytes(); changed = execution_canary_bytes(raw); executed = []; reader = Path.read_bytes
    caller_row = {'path': str(profile_path), 'bytes': len(changed), 'sha256': sha(changed)}
    assert caller_row['sha256'] != expected and len(raw) == len(changed)
    def swapped(path): return changed if path == profile_path else reader(path)
    with patch.object(builtins, '_policy_custody_probe', lambda: executed.append(True), create=True), patch.object(Path, 'read_bytes', swapped):
        refusal('cold_source_loader_ignores_caller_repin', runtime.worker_profile, 'Selected worker profile source differs')
    assert runtime.WORKER_PROFILE_SHA256 == expected and executed == []
    rows.append({'name': 'caller_repin_never_changes_trusted_source_digest_or_executes', 'result': 'PASS'})
    identities = original_source_inventory()['original_identities']
    refusal('inventory_rejects_missing_original', lambda: validate_original_identities(identities[:-1]), 'Original method inventory differs')
    refusal('inventory_rejects_duplicate_original', lambda: validate_original_identities(identities[:-1] + [identities[0]]), 'Original method inventory differs')
    raw_test = Path(__file__).read_bytes()
    main_node = next(node for node in ast.parse(raw_test).body if isinstance(node, ast.FunctionDef) and node.name == 'main')
    main_assertion = next(node for node in main_node.body if isinstance(node, ast.Assert))
    lines = raw_test.splitlines(keepends=True)
    lines[main_assertion.lineno - 1] = b'    pass  # source inventory negative control\n'
    missing_assertion = b''.join(lines)
    assert missing_assertion != raw_test
    refusal('inventory_rejects_removed_original_assertion', lambda: original_source_inventory(missing_assertion), 'Original assertions differ')
    renamed_method = raw_test.replace(b'def test_seventeen_saved_separator_pairs_are_accepted_as_ordered_same_paths(', b'def test_changed_original_identity(', 1)
    refusal('inventory_rejects_changed_original_identity', lambda: original_source_inventory(renamed_method), 'Original method inventory differs')
    return {'scope': 'SOURCE_COMPONENT_ONLY', 'checks': rows, 'count': len(rows),
        'all_passed': True, 'combined_preflight_called': False, 'native_called': False,
        'source_policy_selection_qualified': False, 'integration_qualified': False}


class RecordedComponentResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.case_results = {}
    def addSuccess(self, test):
        super().addSuccess(test); self.case_results[case_identity(test)] = 'PASS'
    def addFailure(self, test, err):
        super().addFailure(test, err); self.case_results[case_identity(test)] = 'FAIL'
    def addError(self, test, err):
        super().addError(test, err); self.case_results[case_identity(test)] = 'ERROR'
    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None: self.case_results[case_identity(test)] = 'SUBTEST_FAILURE'


def main():
    global SOURCE, WORK, INPUTS, RUNTIME, PROFILE, PROVIDER, PLAN, RESPONSE, POLICY
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--test-layer', choices=('full', 'components', 'integration'), default='full',
        help='Explicit component selection retains the ten original integration obligations')
    parser.add_argument('--synthetic-environment', action='store_true',
        help='Use owned synthetic environment fixtures; never historical/native qualification')
    args = parser.parse_args()
    if args.synthetic_environment != (args.test_layer == 'components'):
        parser.error('--synthetic-environment is required only with --test-layer components')
    root = args.output_root.resolve(strict=True); SOURCE = args.source.resolve(); WORK = args.work_dir.resolve()
    if not args.work_dir.is_absolute() or WORK == root or not WORK.is_relative_to(root):
        raise SystemExit('Test output escaped the explicit owned root')
    WORK.mkdir(parents=True, exist_ok=False)
    suite, selection = selected_tests(args.test_layer)
    write(WORK / 'SELECTION.json', selection)
    def audit(event, values):
        if event in ('subprocess.Popen', 'os.system', 'os.spawn', 'ctypes.dlopen', 'os.putenv', 'os.unsetenv') or event.startswith('socket.'):
            raise AssertionError('Effective config tests prohibit process/network/environment effects')
        if event == 'open' and isinstance(values[0], str):
            path = Path(values[0])
            if path.name.lower() == 'config.toml':
                raise AssertionError('Effective config tests prohibit real configuration reads')
            if values[0].replace('\\', '/').upper().startswith('C:/SOURCE_COMPONENT_ONLY/'):
                raise AssertionError('Component descriptors must never read real files')
            mode = values[1]
            if isinstance(mode, str) and any(flag in mode for flag in 'wax+') and not path.resolve().is_relative_to(WORK):
                raise AssertionError('Effective config output escaped its owned work directory')
    sys.addaudithook(audit)
    INPUTS = json.loads(args.inputs.read_bytes())
    PLAN = json.loads(captured(INPUTS['plan']))
    wire = captured(INPUTS['stdout']); frame = INPUTS['frame']
    selected = wire[frame['offset']:frame['offset'] + frame['bytes']]
    assert sha(selected) == frame['sha256']
    RESPONSE = json.loads(selected)['result']; POLICY = INPUTS['policy']
    if args.test_layer != 'components':
        holds = integration_prerequisite_holds()
        if holds:
            report = dict(selection, status='INTEGRATION_PREREQUISITES_HELD', tests=0,
                failures=0, errors=0, input_prerequisite_holds=holds,
                test=pin(Path(__file__)), saved_input_pins=pin(args.inputs),
                suite_executed=False, native_executed=False, actual_source_policy_selection_qualified=False)
            write(WORK / 'RESULTS.json', report)
            print(json.dumps(report)); return 1
    if args.synthetic_environment: synthetic_environment()
    captured(POLICY); captured(INPUTS['home_config'])
    scripts = SOURCE / 'skills/implementaudit/scripts'
    RUNTIME = load(scripts / 'native-capture-adapter/worker_runtime.py', 'effective_runtime')
    PROFILE = load(scripts / 'native-capture-adapter/worker_profile.py', 'effective_profile')
    PROVIDER = load(scripts / 'native-worker-capture.py', 'effective_provider')
    bind_silent_load(PLAN)
    guards = component_boundary_guards() if args.test_layer == 'components' else None
    if guards is not None: write(WORK / 'COMPONENT_GUARDS.json', guards)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordedComponentResult).run(suite)
    write(WORK / 'TEST.log', stream.getvalue().encode())
    report = {**selection, 'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'status': ('COMPONENT_ONLY_PASS_INTEGRATION_HELD' if result.wasSuccessful() else 'COMPONENT_FAILURE_INTEGRATION_HELD') if args.test_layer == 'components' else 'SOURCE_TEST_RESULT_NO_NATIVE_CREDIT',
        'suite_executed': True,
        'original_component_results': {name: status for name, status in result.case_results.items() if name in selection['original_component_identities']},
        'added_component_results': {name: status for name, status in result.case_results.items() if name in selection['added_component_identities']},
        'boundary_guards': pin(WORK / 'COMPONENT_GUARDS.json') if guards is not None else None,
        'boundary_guard_count': guards['count'] if guards is not None else 0,
        'component_file_custody_mock_calls': len(COMPONENT_CUSTODY_CALLS),
        'source_profile': pin(scripts / 'native-capture-adapter/worker_profile.py'),
        'source_runtime': pin(scripts / 'native-capture-adapter/worker_runtime.py'),
        'test': pin(Path(__file__)), 'saved_input_pins': pin(args.inputs), 'native_executed': False,
        'saved_data_consumer_replay_only': not args.synthetic_environment,
        'synthetic_environment_fixture': args.synthetic_environment,
        'test_local_policy_selection': SYNTHETIC_POLICY,
        'source_policy_selection_before_test_substitution': sorted(SYNTHETIC_SOURCE_POLICY_SELECTIONS),
        'actual_source_policy_selection_qualified': False,
        'raw_private_values_emitted': False}
    write(WORK / 'RESULTS.json', report)
    print(json.dumps(report)); return 0 if result.wasSuccessful() else 1

if __name__ == '__main__': raise SystemExit(main())
