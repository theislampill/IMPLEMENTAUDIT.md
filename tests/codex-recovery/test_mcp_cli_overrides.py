"""CLI-key regression for the bounded worker profile; no native/config effects.

The producer is real. Schema shapes here are intentionally minimal because
the break under test is CLI key-path meaning, not JSON Schema behavior; exact
native schemas are also checked by the caller-bundle preflight.
"""
import argparse
import copy
from contextlib import nullcontext
import ctypes
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

PROFILE = WORK = None

def pin(path):
    raw = path.read_bytes()
    return {'path': str(path.resolve()), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def fixture_literal(path):
    absolute = str(path.resolve())
    return absolute if sys.platform == 'win32' else '/' + absolute

def fixture_pin(path):
    record = pin(path)
    record['path'] = fixture_literal(path)
    return record

def portable_fixture_pin(profile, root):
    """Keep real byte pins while preserving a synthetic dual-absolute path spelling."""
    if sys.platform == 'win32':
        return nullcontext()
    original = profile.pin
    root = root.resolve()
    def pinned(value):
        if isinstance(value, str) and value.startswith('//') and Path(value).resolve().is_relative_to(root):
            raw = Path(value).read_bytes()
            return {'path': value, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        return original(value)
    return patch.object(profile, 'pin', pinned)

def bind_synthetic_context(profile, binding, root):
    """Use the existing independent source fixture, never observed frames or home config."""
    path = Path(__file__).with_name('test_native_context_contract.py')
    spec = importlib.util.spec_from_file_location('mcp_context_fixture', path)
    fixture = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), 'exec'), fixture.__dict__)
    fixture.WORK = root
    basis = profile.prepare_context_basis(binding, {'type': 'object'}, {'type': 'object'}, purpose='OFFLINE_FIXTURE')
    context, _, _ = fixture.factory_input(basis['basis_sha256'])
    binding.update(context)
    return basis['profile_proposal_without_context']

def synthetic_binding(profile, root):
    """Complete inert profile selection, shared with the silent-LOAD consumer tests."""
    def file(relative):
        path = root / relative; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(('SYNTHETIC_ONLY ' + relative).encode())
        return fixture_pin(path)
    native = file('native/codex.exe')
    code_mode_host = file('native/codex-code-mode-host.exe')
    python = file('runtime/python.exe')
    powershell = file('shell/pwsh.exe')
    loader = file('load/loader.py')
    loads = {role: file('load/' + role + '.txt') for role in
             ('child_source', 'shared_transcript_contract', 'frozen_open_envelope')}
    use = file('use/input.txt'); denied = file('excluded/witness.txt')
    quote = lambda value: "'" + value.replace("'", "''") + "'"
    command = '& ' + quote(python['path']) + ' -I -S -B ' + quote(loader['path'])
    binding = {'native': native, 'code_mode_host': code_mode_host, 'python': python, 'powershell': powershell,
        'python_root': fixture_literal(root / 'runtime'), 'cwd': fixture_literal(root),
        'load_pins': loads, 'loader': loader, 'use_pins': [use], 'excluded_paths': [denied['path']],
        'disabled_skill_paths': [], 'mcp_names': ['cua_repl', 'https-mcp-tafsir-net-mcp', 'node_repl'],
        'model': 'gpt-6-astra', 'provider': 'openai', 'effort': 'low',
        'load_command': command, 'use_command': "Write-Output 'SYNTHETIC_USE'",
        'use_expected_output': 'SYNTHETIC_USE\n', 'use_terminal_text': 'SYNTHETIC_USE_ONLY'}
    binding['load_input'] = profile.silent_load_input(binding, 'LOAD_READY_ONLY ' + '0' * 64)
    binding['use_input'] = profile.silent_use_input(binding)
    baseline = bind_synthetic_context(profile, binding, root)
    return binding, baseline

def apply_boolean_mcp_flags(base, flags):
    """Independent narrow oracle: literal dot segments, exact boolean false.

    This does not parse the LHS as TOML and does not model a native invocation.
    The asserted subset is exactly the MCP disabling flags produced here.
    """
    result = copy.deepcopy(base)
    for flag in flags:
        key, value = flag.split('=', 1)
        assert value == 'false'
        parts = key.split('.')
        assert parts[0] == 'mcp_servers' and parts[-1] == 'enabled'
        table = result
        for part in parts[:-1]: table = table.setdefault(part, {})
        table[parts[-1]] = False
    return result

class McpCliOverrideTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.binding, _ = synthetic_binding(PROFILE, self.root)

    def prepare(self, names=None):
        binding = copy.deepcopy(self.binding)
        if names is not None:
            binding['mcp_names'] = names
            binding.pop('context_input')
            bind_synthetic_context(PROFILE, binding, self.root)
        return PROFILE.prepare(binding, {'type': 'object'}, {'type': 'object'}, purpose='OFFLINE_FIXTURE')

    def flags(self, result):
        return [value for value in result['profile_overrides'] if value.startswith('mcp_servers.')]

    def test_actual_three_names_emit_literal_cli_paths(self):
        result = self.prepare()
        expected = ['mcp_servers.cua_repl.enabled=false',
            'mcp_servers.https-mcp-tafsir-net-mcp.enabled=false', 'mcp_servers.node_repl.enabled=false']
        self.assertEqual(self.flags(result), expected)
        actual_argv = result['server_argv']
        self.assertEqual([actual_argv[index + 1] for index, value in enumerate(actual_argv[:-1])
            if value == '--config' and actual_argv[index + 1].startswith('mcp_servers.')], expected)

    def test_cli_application_disables_existing_servers_without_phantom_tables(self):
        base = {'mcp_servers': {'cua_repl': {'command': 'SYNTHETIC_CUA', 'enabled': False},
            'https-mcp-tafsir-net-mcp': {'url': 'https://example.invalid/mcp', 'enabled': True},
            'node_repl': {'command': 'SYNTHETIC_NODE', 'args': ['--fixture'], 'enabled': True}}}
        actual = apply_boolean_mcp_flags(base, self.flags(self.prepare()))
        expected = copy.deepcopy(base)
        for row in expected['mcp_servers'].values(): row['enabled'] = False
        self.assertEqual(actual, expected)
        self.assertTrue(all('command' in row or 'url' in row for row in actual['mcp_servers'].values()))

    def test_projection_matches_literal_cli_effect(self):
        result = self.prepare()
        actual = apply_boolean_mcp_flags({}, self.flags(result))['mcp_servers']
        self.assertEqual(result['effective_config_projection']['mcp_servers'], actual)
        self.assertEqual(set(actual), set(self.binding['mcp_names']))

    def test_dot_and_assignment_names_are_explicitly_refused(self):
        for name in ('cua.repl', 'cua=repl', '', 'a\x00b', 'a\nb', 'a\rb',
                     '"quoted"', "'quoted'", 'space name', 'a\\b', '名前'):
            with self.subTest(name=repr(name)), self.assertRaisesRegex(ValueError,
                    '^MCP name is not representable in the bounded native CLI key grammar$'):
                self.prepare([name])

    def test_context_is_bound_to_the_exact_profile_and_cannot_be_missing_or_reused(self):
        result = self.prepare()
        self.assertEqual(result['context_contract']['scope'], 'OFFLINE_SYNTHETIC')
        self.assertFalse(result['native_attempt_enabled'])
        for change, cause in (
                (lambda binding: binding.pop('context_input'), 'Independent context input and request/profile basis required'),
                (lambda binding: binding.update(mcp_names=['another_valid_name']), 'Context source or generated request/profile basis differs')):
            binding = copy.deepcopy(self.binding); change(binding)
            with self.subTest(cause=cause), self.assertRaisesRegex(ValueError, '^' + cause + '$'):
                PROFILE.prepare(binding, {'type': 'object'}, {'type': 'object'}, purpose='OFFLINE_FIXTURE')

    def test_cli_validator_rejects_phantoms_missing_flags_and_wrong_boolean(self):
        validate = getattr(PROFILE, 'cli_override_projection', None)
        self.assertTrue(callable(validate), 'Native CLI semantic validation is absent')
        for overrides in (['mcp_servers."cua_repl".enabled=false'], [], ['mcp_servers={}'],
                          ['mcp_servers.cua_repl.enabled="false"'],
                          ['mcp_servers.cua_repl.enabled=false\nother=true'],
                          ['mcp_servers.cua_repl.enabled=false', 'mcp_servers.cua_repl.enabled=false']):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                validate(overrides, ['cua_repl'])

    def test_rhs_inline_map_paths_keep_quotes_spaces_dots_and_equals(self):
        validate = getattr(PROFILE, 'cli_override_projection', None)
        self.assertTrue(callable(validate), 'Native CLI semantic validation is absent')
        overrides = ['mcp_servers.cua_repl.enabled=false',
            'permissions.worker_load.filesystem={"C:/Program Files/runtime.v1"="read"}',
            'shell_environment_policy.set={"VALUE"="a=b", "QUOTED"="a\\\"b"}']
        value = validate(overrides, ['cua_repl'])
        self.assertEqual(value['permissions']['worker_load']['filesystem'], {'C:/Program Files/runtime.v1': 'read'})
        self.assertEqual(value['shell_environment_policy']['set'], {'VALUE': 'a=b', 'QUOTED': 'a"b'})

    def test_transport_validation_preserves_exact_named_inheritance(self):
        validate = getattr(PROFILE, 'validate_mcp_transports', None)
        self.assertTrue(callable(validate), 'Inherited transport validation is absent')
        projection = {'mcp_servers': {'cua_repl': {'enabled': False}, 'http-server': {'enabled': False}}}
        layers = [{'cua_repl': {'command': 'SYNTHETIC_CMD', 'args': ['fixture'], 'enabled': False},
                   'http-server': {'url': 'https://example.invalid', 'http_headers': {'FIXTURE': 'retained'}}},
                  {'cua_repl': {}}]
        before = copy.deepcopy(layers)
        result = validate(projection, ['cua_repl', 'http-server'], layers)
        self.assertEqual(layers, before)
        self.assertTrue(result['transport_fields_preserved'])
        self.assertTrue(result['no_phantom_keys'])
        self.assertEqual(result['names'], ['cua_repl', 'http-server'])

    def test_disabled_partial_or_missing_server_cannot_qualify_transport(self):
        validate = getattr(PROFILE, 'validate_mcp_transports', None)
        self.assertTrue(callable(validate), 'Inherited transport validation is absent')
        projection = {'mcp_servers': {'cua_repl': {'enabled': False}}}
        for layers in ([{}], [{'cua_repl': {'enabled': False}}],
                       [{'cua_repl': {'command': 'SYNTHETIC'}, 'omitted': {'command': 'OTHER', 'enabled': False}}]):
            with self.subTest(layers=layers), self.assertRaises(ValueError):
                validate(projection, ['cua_repl'], layers)

    def test_raw_safe_names_keep_case_digits_hyphens_and_underscores(self):
        result = self.prepare(['Server_2-a'])
        self.assertEqual(self.flags(result), ['mcp_servers.Server_2-a.enabled=false'])

    def test_existing_non_mcp_values_and_model_choices_are_preserved(self):
        result = self.prepare()
        config = result['effective_config_projection']
        self.assertEqual((result['thread_start']['params']['model'],
            result['thread_start']['params']['modelProvider'], result['turn_start']['params']['effort']),
            ('gpt-6-astra', 'openai', 'low'))
        self.assertFalse(result['thread_start']['params']['allowProviderModelFallback'])
        self.assertEqual(config['shell_environment_policy']['inherit'], 'none')
        self.assertEqual(config['shell_environment_policy']['set']['SystemRoot'], 'C:\\Windows')
        self.assertFalse(config['permissions']['worker_load']['network']['enabled'])
        self.assertFalse(config['permissions']['worker_use']['network']['enabled'])
        self.assertEqual(config['permissions']['worker_load']['filesystem'][':root'], 'deny')

    def test_only_literal_boolean_false_can_disable_selected_mcp(self):
        for value in ('0', '0.0', 'true', '"false"'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                PROFILE.cli_override_projection(['mcp_servers.safe.enabled=' + value], ['safe'])
        for value in (0, 0.0, True, 'false'):
            with self.subTest(projection=value), self.assertRaises(ValueError):
                PROFILE.validate_mcp_transports({'mcp_servers': {'safe': {'enabled': value}}},
                    ['safe'], [{'safe': {'command': 'SYNTHETIC'}}])

    def test_native_transport_field_types_refuse_before_launch(self):
        # Literal cases derive from pinned RawMcpServerConfig and its transport types.
        cases = [
            {'command': 7}, {'url': 7}, {'command': 'SYNTHETIC', 'args': 'one'},
            {'command': 'SYNTHETIC', 'args': ['one', 7]},
            {'command': 'SYNTHETIC', 'env': []}, {'command': 'SYNTHETIC', 'env': {'X': 7}},
            {'command': 'SYNTHETIC', 'cwd': 7}, {'command': 'SYNTHETIC', 'env_vars': 'X'},
            {'command': 'SYNTHETIC', 'env_vars': [7]},
            {'command': 'SYNTHETIC', 'env_vars': [{'source': 'local'}]},
            {'command': 'SYNTHETIC', 'env_vars': [{'name': 7}]},
            {'command': 'SYNTHETIC', 'env_vars': [{'name': 'X', 'source': 7}]},
            {'command': 'SYNTHETIC', 'env_vars': [{'name': 'X', 'source': 'other'}]},
            {'command': 'SYNTHETIC', 'env_vars': [{'name': 'X', 'extra': 'bad'}]},
            {'url': 'https://example.invalid', 'http_headers': []},
            {'url': 'https://example.invalid', 'http_headers': {'X': 7}},
            {'url': 'https://example.invalid', 'env_http_headers': 'X'},
            {'url': 'https://example.invalid', 'env_http_headers': {'X': False}},
            {'url': 'https://example.invalid', 'bearer_token_env_var': 7},
            {'url': 'https://example.invalid', 'http_headers_helper': 7},
            {'url': 'https://example.invalid', 'environment_id': 7},
            {'url': 'https://example.invalid', 'oauth_resource': 7},
            {'url': 'https://example.invalid', 'auth': 7},
            {'url': 'https://example.invalid', 'auth': 'invented'},
            {'url': 'https://example.invalid', 'oauth': 'bad'},
            {'url': 'https://example.invalid', 'oauth': {'client_id': 7}},
            {'url': 'https://example.invalid', 'oauth': {'callback_url': 7}},
            *({'url': 'https://example.invalid', 'oauth': {'callback_port': port}}
              for port in (-1, 65536, 1.0, True)),
        ]
        for row in cases:
            before = copy.deepcopy(row)
            with self.subTest(row=row), self.assertRaises(ValueError):
                PROFILE.validate_mcp_transports({'mcp_servers': {'safe': {'enabled': False}}}, ['safe'], [{'safe': row}])
            self.assertEqual(row, before)

    def test_native_transport_incompatible_fields_refuse_even_when_empty(self):
        stdio_fields = {'url': 'https://example.invalid', 'bearer_token_env_var': '',
            'bearer_token': '', 'http_headers_helper': '', 'http_headers': {}, 'env_http_headers': {},
            'oauth': {}, 'oauth_resource': '', 'auth': 'oauth'}
        http_fields = {'args': [], 'env': {}, 'env_vars': [], 'cwd': '', 'bearer_token': ''}
        for base, fields in (({'command': 'SYNTHETIC'}, stdio_fields), ({'url': 'https://example.invalid'}, http_fields)):
            for key, value in fields.items():
                with self.subTest(transport=base, field=key), self.assertRaises(ValueError):
                    PROFILE.validate_mcp_transports({'mcp_servers': {'safe': {'enabled': False}}},
                        ['safe'], [{'safe': {**base, key: value}}])

    def test_http_header_helper_requires_nonempty_local_command(self):
        for fields in ({'http_headers_helper': ''}, {'http_headers_helper': '  '},
                       {'http_headers_helper': 'SYNTHETIC', 'environment_id': 'remote'},
                       {'http_headers_helper': 'SYNTHETIC', 'environment_id': ''}):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                PROFILE.validate_mcp_transports({'mcp_servers': {'safe': {'enabled': False}}},
                    ['safe'], [{'safe': {'url': 'https://example.invalid', **fields}}])

    def test_native_supported_transport_shapes_preserve_inputs(self):
        cases = [
            {'command': 'SYNTHETIC', 'args': [], 'env': {'X': 'value'}, 'cwd': 'C:/Synthetic',
             'env_vars': ['X', {'name': 'Y'}, {'name': 'Z', 'source': 'local'}, {'name': 'R', 'source': 'remote'}]},
            {'url': 'https://example.invalid', 'http_headers': {'X': 'value'}, 'env_http_headers': {'Y': 'ENV'},
             'bearer_token_env_var': 'TOKEN', 'http_headers_helper': 'SYNTHETIC', 'environment_id': 'local',
             'auth': 'oauth', 'oauth_resource': 'RESOURCE',
             'oauth': {'client_id': 'CLIENT', 'callback_url': 'http://example.invalid', 'callback_port': 65535}},
            {'url': 'https://example.invalid', 'auth': 'chatgpt', 'environment_id': 'remote'},
            {'url': 'https://example.invalid', 'http_headers_helper': 'SYNTHETIC', 'oauth': {'callback_port': 0}},
        ]
        for row in cases:
            row['unrelated_metadata'] = {'preserve': ['a=b', 'x.y']}
            layers = [{'safe': row}, {'safe': {}}]
            before = copy.deepcopy(layers)
            with self.subTest(row=row):
                result = PROFILE.validate_mcp_transports({'mcp_servers': {'safe': {'enabled': False}}}, ['safe'], layers)
                self.assertEqual(layers, before)
                self.assertTrue(result['transport_fields_preserved'])
                self.assertIs(result['selected_transport_shapes'][0]['enabled_after'], False)

def main():
    global PROFILE, WORK
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    output_root = args.output_root.resolve(strict=True)
    WORK = args.work_dir.resolve()
    if (not args.output_root.is_absolute() or not args.work_dir.is_absolute() or
            not output_root.is_dir() or WORK == output_root or not WORK.is_relative_to(output_root)):
        raise SystemExit('Test work directory is outside the explicit output root')
    WORK.mkdir(parents=True, exist_ok=False)
    path = args.source / 'skills/implementaudit/scripts/native-capture-adapter/worker_profile.py'
    spec = importlib.util.spec_from_file_location('tested_worker_profile', path)
    PROFILE = importlib.util.module_from_spec(spec); spec.loader.exec_module(PROFILE)
    def forbid(event, args):
        if event in ('subprocess.Popen', 'os.system', 'os.spawn', 'ctypes.dlopen') or event.startswith('socket.'):
            raise AssertionError('MCP override tests prohibit native/process/network effects')
    sys.addaudithook(forbid)
    stream = io.StringIO()
    with portable_fixture_pin(PROFILE, WORK):
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(McpCliOverrideTests))
    (WORK / 'TEST.log').write_text(stream.getvalue(), encoding='utf8')
    record = {'source': pin(path), 'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'successful': result.wasSuccessful(), 'synthetic_inputs_only': True, 'native_executed': False}
    (WORK / 'RESULTS.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf8')
    print(json.dumps(record)); return 0 if result.wasSuccessful() else 1

if __name__ == '__main__': raise SystemExit(main())
