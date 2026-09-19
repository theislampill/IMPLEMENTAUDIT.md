#!/usr/bin/env python3
"""Maintained fission integration controls, with no host or campaign effects.

The static reader is exercised as checker code, not replaced by the production
loader. Mutations are in-memory source values. CLI cases own temporary roots.
"""
from __future__ import annotations
import argparse
import ast
import importlib.util
import inspect
import json
import os
import posixpath
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

P = argparse.ArgumentParser()
P.add_argument('--source', type=Path, required=True)
ARGS, UNIT_ARGS = P.parse_known_args()
ROOT = ARGS.source.resolve()
PREFIX = 'skills/implementaudit/scripts/'
OWNERS = {
    'route_request_policy.py': ('route-transaction.py', '_load_route_request_policy'),
    'canonical_hot_projection.py': ('rotate-canonical-state.py', '_load_hot_projection_module'),
    'operational_query_policy.py': ('operational-evidence.py', '_load_query_policy_module'),
}
LEAVES = {
    'eval/lib/host_command_policy.py': 'HostCommandPolicy',
    PREFIX + 'route_request_policy.py': 'validate_request',
    PREFIX + 'canonical_hot_projection.py': 'HotProjectionRenderer',
    PREFIX + 'operational_query_policy.py': 'SnapshotQueryPolicy',
    PREFIX + 'closure_automatic_effects.py': 'trigger_matches',
}

def load(relative: str):
    path = ROOT / relative
    name = '_fission_test_' + path.stem.replace('-', '_')
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError('No source loader for ' + relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def checker_namespace():
    text = (ROOT / 'scripts/check-helper-reachability.sh').read_text()
    body = text.split("<<'PY'\n", 1)[1].rsplit('\nPY', 1)[0]
    tree = ast.parse(body)
    names = {'SourceValue', 'unknown', 'PythonEdges', 'shell_code', 'shell_python_module_route'}
    chosen = [node for node in tree.body
              if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names]
    ns = dict(ast=ast, posixpath=posixpath, PurePosixPath=PurePosixPath, re=re)
    exec(compile(ast.Module(body=chosen, type_ignores=[]), 'selected-reachability-checker', 'exec'), ns)
    return ns


def payloads():
    return {p.relative_to(ROOT).as_posix(): p.read_bytes()
            for p in (ROOT / PREFIX).rglob('*.py')}


class FissionIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = checker_namespace()
        cls.payload = payloads()

    def test_new_runtime_owners_have_internal_applicability_rows(self):
        text = (ROOT / 'skills/implementaudit/references/repo-state-comparison.md').read_text()
        rows = [line for line in text.splitlines() if line.startswith('helper-route: ')]
        for leaf in (*OWNERS, 'closure_automatic_effects.py'):
            with self.subTest(leaf=leaf):
                matching = [line for line in rows if line.startswith('helper-route: scripts/' + leaf + '|')]
                self.assertEqual(len(matching), 1, 'Missing or duplicated runtime owner registration: ' + leaf)
                self.assertEqual(matching[0].split('|')[1], 'I')

    def test_maintained_test_entry_points_are_registered_once(self):
        package = (ROOT / 'tests/package-contract.test.sh').read_text()
        host = (ROOT / 'tests/eval-harness.test.sh').read_text()
        self.assertEqual(package.count('tests/fission-integration-contract.py'), 1,
                         'Fission integration/refusal checks are not in maintained package validation')
        self.assertEqual(host.count('eval/test_host_command_policy.py'), 1,
                         'Direct host-policy controls are not in maintained eval validation')

    def test_leaf_responsibilities_are_direct_and_inspectable(self):
        for relative, symbol in LEAVES.items():
            with self.subTest(owner=relative):
                module = load(relative)
                self.assertTrue(inspect.getsource(getattr(module, symbol)).strip())
                tree = ast.parse((ROOT / relative).read_bytes())
                imports = [node.module or '' for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
                imports += [a.name for node in ast.walk(tree) if isinstance(node, ast.Import) for a in node.names]
                self.assertFalse(any(any(s in name for s in ('hosts', 'route-transaction',
                    'operational-evidence', 'rotate-canonical-state', 'b3v4_rederive',
                    'candidate_matrix_rederive')) for name in imports))

    def test_static_reader_follows_real_verified_buffer_loaders(self):
        for leaf, (caller, function) in OWNERS.items():
            with self.subTest(leaf=leaf):
                engine = self.ns['PythonEdges'](self.payload)
                loaded, _, _ = engine.inspect(PREFIX + caller, function)
                self.assertIn(PREFIX + leaf, loaded, 'Checked-buffer source edge is not inspectable')

    def test_static_reader_does_not_infer_execution_from_filenames(self):
        mutations = {
            'substituted_buffer': ('exec(compile(_source, _path, "exec"), _module.__dict__)',
                                  'exec(compile(b"pass", _path, "exec"), _module.__dict__)'),
            'no_execution': ('exec(compile(_source, _path, "exec"), _module.__dict__)', 'pass'),
            'different_compile_path': ('compile(_source, _path, "exec")', 'compile(_source, "elsewhere.py", "exec")'),
            'text_stream': ('_os.fdopen(_fd, "rb")', '_os.fdopen(_fd, "r")'),
            'partial_read': ('_stream.read(_ROUTE_REQUEST_POLICY_BYTES + 1)', '_stream.read(1)'),
        }
        original = self.payload[PREFIX + 'route-transaction.py'].decode()
        for name, (before, after) in mutations.items():
            with self.subTest(mutation=name):
                self.assertEqual(original.count(before), 1, 'Mutation preimage changed')
                mutated = dict(self.payload)
                mutated[PREFIX + 'route-transaction.py'] = original.replace(before, after).encode()
                loaded, _, _ = self.ns['PythonEdges'](mutated).inspect(
                    PREFIX + 'route-transaction.py', '_load_route_request_policy')
                self.assertNotIn(PREFIX + 'route_request_policy.py', loaded)

    def test_real_shell_checked_buffer_edge(self):
        fn = self.ns.get('shell_python_module_route')
        self.assertTrue(callable(fn), 'No bounded shell-to-checked-buffer source-edge reader')
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        self.assertTrue(fn('closure_automatic_effects.py', text, self.payload,
                           PREFIX + 'check-closure-surface.sh'))

    def test_shell_edge_refuses_nonexecuting_or_unbound_substitutes(self):
        fn = self.ns.get('shell_python_module_route')
        self.assertTrue(callable(fn), 'No bounded shell-to-checked-buffer source-edge reader')
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        header = next(line for line in text.splitlines()
                      if '"${py_cmd[@]}" - ' in line and 'closure_automatic_effects.py' in line)
        cases = {
            'commented_header': text.replace(header, '# ' + header),
            'wrong_operand': text.replace(header, header.replace('/closure_automatic_effects.py', '/missing.py')),
            'wrong_interpreter': text.replace('py_cmd=(python)', 'py_cmd=(other-program)'),
            'literal_data_not_call': "cat <<'UNEXECUTED_DATA'\n" + text + '\nUNEXECUTED_DATA\n',
            'removed_exec': text.replace('exec(compile(_source, _path, "exec"), _module.__dict__)', 'pass'),
            'wrong_buffer': text.replace('compile(_source, _path, "exec")', 'compile(b"pass", _path, "exec")'),
            'wrong_argv': text.replace('_os.path.abspath(_sys.argv[1])', '_os.path.abspath(_sys.argv[9])'),
        }
        for name, mutated in cases.items():
            with self.subTest(mutation=name):
                self.assertNotEqual(mutated, text)
                self.assertFalse(fn('closure_automatic_effects.py', mutated, self.payload,
                                    PREFIX + 'check-closure-surface.sh'))

    def test_new_leaf_sources_are_whitespace_clean(self):
        for relative in LEAVES:
            with self.subTest(owner=relative):
                self.assertEqual([n for n, line in enumerate((ROOT / relative).read_text().splitlines(), 1)
                                  if line.rstrip(" \t") != line], [])

    def test_shell_edge_refuses_interpreter_state_and_multiline_data(self):
        fn = self.ns['shell_python_module_route']
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        header = next(line for line in text.splitlines()
                      if '"${py_cmd[@]}" - ' in line and 'closure_automatic_effects.py' in line)
        for label, mutation in {
            'scalar_overwrite': text.replace(header, '  py_cmd=not-python\n' + header),
            'array_append': text.replace(header, '  py_cmd+=(not-a-python-script)\n' + header),
            'array_element': text.replace(header, '  py_cmd[0]=not-python\n' + header),
            'unset_command': text.replace(header, '  unset py_cmd\n' + header),
            'multiline_double_quoted_data': 'message="\n' + text.replace('"', '\\"') + '\n"\n',
            'uninvoked_loader': text.replace('_closure_effects = _load_closure_effects()', '_closure_effects = None'),
        }.items():
            with self.subTest(mutation=label):
                self.assertFalse(fn('closure_automatic_effects.py', mutation, self.payload,
                                    PREFIX + 'check-closure-surface.sh'))

    def test_shell_edge_refuses_unset_words_and_unresolved_operands(self):
        fn = self.ns['shell_python_module_route']
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        header = next(line for line in text.splitlines()
                      if '"${py_cmd[@]}" - ' in line and 'closure_automatic_effects.py' in line)
        for statement in (
                'unset "py_cmd"', "unset 'py_cmd[0]'", 'unset -- py_cmd',
                "unset 'py_'cmd", r'un\set p\y_cmd',
                'unset unrelated py_cmd', 'unset -v -- "py_cmd"',
                'unset -v "py_cmd[@]"', 'unset -vn -- py_cmd',
                'builtin unset "py_cmd"', "command -- unset 'py_cmd[0]'",
                'command -p unset -- py_cmd', 'command -pp unset -- py_cmd',
                'builtin -- unset -- py_cmd', 'command -- builtin unset "py_cmd"',
                'un""set py_cmd', ':; unset "py_cmd"',
                'if true; then unset "py_cmd"; fi',
                'unset \\\n  "py_cmd"', 'unset "py_cmd" # trailing comment',
                'unset_target=py_cmd; unset "$unset_target"',
                'unset -- ${unset_target}', 'unset -- "${!unset_name}"',
                'unset -- unrelated[$unset_index]', 'unset -z py_cmd',
                'unset -fv unrelated',
                'R135_TAG=1 unset py_cmd', 'R135_TAG= unset "py_cmd"',
                "R135_TAG='two words' R135_OTHER=2 unset -- 'py_cmd[0]'",
                'R135_TAG+=1 unset py_cmd', 'R135_TAG=1 builtin unset py_cmd',
                'R135_TAG=1 command -- unset py_cmd',
                'if R135_TAG=1 unset py_cmd; then :; fi',
                "R135_TAG='; unset unrelated' unset py_cmd"):
            with self.subTest(statement=statement):
                mutation = text.replace(header, '  ' + statement + '\n' + header)
                self.assertNotEqual(mutation, text)
                self.assertFalse(fn('closure_automatic_effects.py', mutation, self.payload,
                                    PREFIX + 'check-closure-surface.sh'))

    def test_shell_edge_preserves_unset_data_and_unrelated_operations(self):
        fn = self.ns['shell_python_module_route']
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        header = next(line for line in text.splitlines()
                      if '"${py_cmd[@]}" - ' in line and 'closure_automatic_effects.py' in line)
        for statement in (
                '# unset "py_cmd"', "message='unset py_cmd'",
                "message='unset\npy_cmd'",
                "printf '%s\\n' 'unset py_cmd' >/dev/null",
                "printf '%s\\n' unset py_cmd >/dev/null",
                "printf '%s\\n' ';' unset py_cmd >/dev/null",
                "message='a; unset py_cmd'",
                "builtin printf '%s' 'unset py_cmd' >/dev/null",
                'unset unrelated', "unset -- 'py_cmd_suffix'",
                "unset -v -- 'unrelated[0]'", 'unset -f py_cmd',
                'command -v unset >/dev/null', 'command -V unset >/dev/null',
                'R135_TAG=1 unset unrelated', 'R135_TAG=1 unset -f py_cmd',
                "R135_TAG='unset py_cmd' printf '%s' '; unset py_cmd' >/dev/null",
                "R135_TAG=';' R135_OTHER=2 printf '%s' unset py_cmd >/dev/null",
                'R135_TAG=1 command -v unset >/dev/null', 'R135_TAG=1',
                '# R135_TAG=1 unset py_cmd', "R135_TAG='unset py_cmd'"):
            with self.subTest(statement=statement):
                mutation = text.replace(header, '  ' + statement + '\n' + header)
                self.assertTrue(fn('closure_automatic_effects.py', mutation, self.payload,
                                   PREFIX + 'check-closure-surface.sh'))

    def test_route_policy_positive_and_typed_refusals(self):
        m = load(PREFIX + 'route_request_policy.py')
        digest = 'sha256:' + 'a' * 64
        request = dict(schema=m.REQUEST_SCHEMA, predicate_version=m.PREDICATE_VERSION,
            boundary=dict(kind='test', event_id='event', digest=digest),
            scope=dict(identity='scope', digest=digest),
            action=dict(identity='action', digest=digest, **{'class': 'read'}, argv=['read']),
            inputs=[dict(identity='input', path='source', digest=digest)])
        self.assertEqual(m.validate_request(request), request)
        for value in (None, 1, [], {'schema': 'wrong'}):
            with self.subTest(value=value), self.assertRaises(m.RequestRefusal):
                m.validate_request(value)
        for raw in (b'\xff', b'{', b'[]', b'{"a":1,"a":2}'):
            with self.subTest(raw=raw), self.assertRaises(m.RequestRefusal):
                m.decoded_artifact(raw, 'test')

    def test_query_noniterable_refusal_and_positive_neighbours(self):
        m = load(PREFIX + 'operational-evidence.py')
        for invalid in (None, True, False, 0, 1, 1.5):
            with self.subTest(value=invalid):
                with self.assertRaises(m.OperationalEvidenceError) as caught:
                    m.evaluate_currentness(dict(schema_version=m.SNAPSHOT_PAYLOAD_SCHEMA,
                        families=invalid, collections={}))
                self.assertIn('six frozen families', str(caught.exception))
        for valid in (list(m.FAMILIES), tuple(m.FAMILIES)):
            result = m.evaluate_currentness(dict(schema_version=m.SNAPSHOT_PAYLOAD_SCHEMA,
                families=valid, collections={}))
            self.assertEqual(result['authority_ceiling'], 'READ_ONLY_OBSERVATION')

    def test_hot_projection_bounds_and_injected_validation(self):
        m = load(PREFIX + 'canonical_hot_projection.py')
        class Refusal(Exception):
            pass
        def reject_fields(_):
            raise Refusal('field validation reached')
        renderer = m.HotProjectionRenderer(error_type=Refusal,
            validate_fields=reject_fields, validate_dependencies=lambda *a: None)
        self.assertEqual(renderer._hot_value_v1('value'), 'value')
        for invalid in ('', 'a|b', 'a\nb', 'a\rb', None, 1):
            with self.subTest(value=invalid), self.assertRaises(Refusal):
                renderer._hot_value_v1(invalid)
        with self.assertRaises(Refusal):
            renderer._render_lines_v1(['x' * 4097])
        with self.assertRaisesRegex(Refusal, 'field validation reached'):
            renderer.render_state_template_v1({}, None, None)

    def test_closure_block_scalar_cli_refusals(self):
        bash = shutil.which('bash')
        self.assertIsNotNone(bash, 'Bash must be available on PATH for closure CLI tests')
        bash = str(Path(bash).resolve())
        with tempfile.TemporaryDirectory(prefix='fission closure contract ') as tmp:
            root = Path(tmp)
            workflow = root / '.github/workflows'
            workflow.mkdir(parents=True)
            plan = root / 'plan.md'
            plan.write_text('automatic-effect-preflight: event: push | ref: main | workflows: none | '
                            'effects: none | post-state-readback: trigger-read-only | excluded-outcomes: none\n')
            for key in ('branches', 'branches-ignore'):
                for scalar in ('>', '|', '>-', '|+', '>2-', '|2+'):
                    with self.subTest(key=key, scalar=scalar):
                        (workflow / 'check.yml').write_text('on:\n  push:\n    ' + key + ': ' + scalar +
                            '\n      main\njobs:\n  check:\n    runs-on: ubuntu-latest\n')
                        result = subprocess.run([bash, str(ROOT / PREFIX / 'check-closure-surface.sh'),
                            '--automatic-effects', str(root), 'push', 'main', str(plan)],
                            capture_output=True, text=True, timeout=20,
                            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn('unsupported aliased/tagged/block branch-filter scalar',
                                      result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0], *UNIT_ARGS])
