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


class RetainedSeedControls(unittest.TestCase):
    def seed(self, function, capsule, legacy=False):
        tree=ast.parse((ROOT / PREFIX / 'route-transaction.py').read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==function)
        start=next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Assign)
                   and any(isinstance(t,ast.Name) and t.id=='identity_seed' for t in n.targets))
        end=next(i for i,n in enumerate(fn.body[start+1:],start+1) if isinstance(n,ast.Assign)
                 and any(isinstance(t,ast.Name) and t.id in {'transaction_id','expected_transaction'} for t in n.targets))
        req={'action':{'argv':['route-trigger','IMMUTABLE_INDEPENDENT_REVIEW']}}
        owner={'controller_record_oid':'a'*40,'claim_id':'claim','continuity_receipt':'receipt'}
        record={**owner,'host_binding_generation':'G0001'}
        ns={'request':req,'retained_request':req,'current':owner,'owner':owner,'record':record,
            'package':{'identity':'package'},'child_source':{'identity':'child'},
            'host_binding_generation':'G0001','recovery_capsule':capsule,
            'preserved_unopenable':legacy,'repo':ROOT,
            'post_compaction_recovery_capsule':lambda root,request:capsule}
        exec(compile(ast.Module(body=fn.body[start:end],type_ignores=[]),'exact-source-seed','exec'),ns)
        return ns['identity_seed']
    def test_retained_null_capsule_seed_matches_creation(self):
        self.assertEqual(self.seed('route_semantic_basis',None),self.seed('validate_stale_unsatisfied_custody',None))
    def test_retained_selected_capsule_seed_matches_creation(self):
        cap={'capsule_digest':'sha256:'+'b'*64}
        self.assertEqual(self.seed('route_semantic_basis',cap),self.seed('validate_stale_unsatisfied_custody',cap))
    def test_allowlisted_legacy_keeps_original_seed_layout(self):
        self.assertNotIn('recovery_capsule_digest',self.seed('validate_stale_unsatisfied_custody',None,legacy=True))


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

    def test_closure_cleanup_removes_all_owned_roots_and_preserves_neighbours(self):
        text = (ROOT / 'tests/closure-surface-contract.test.sh').read_text()
        match = re.search(r'^cleanup_full\(\) \{\n.*?^\}', text, re.M | re.S)
        self.assertIsNotNone(match)
        with tempfile.TemporaryDirectory(prefix='closure-cleanup-control-') as base:
            base = Path(base)
            for code in (0, 7):
                with self.subTest(exit_code=code):
                    roots = [base / (name + str(code)) for name in ('assets', 'work', 'effects')]
                    for root in roots:
                        root.mkdir(); (root / 'owned').write_text('fixture')
                    neighbour = base / ('neighbour' + str(code))
                    neighbour.write_text('must survive')
                    script = match.group(0) + '\ntrap cleanup_full EXIT\nexit "$4"\n'
                    script = 'v0400_asset_tmp="$1"; tmp="$2"; effect_tmp="$3"\n' + script
                    completed = subprocess.run(['bash', '-c', script, 'cleanup-control',
                        *map(str, roots), str(code)], capture_output=True)
                    self.assertEqual(completed.returncode, code, completed.stderr)
                    self.assertTrue(all(not root.exists() for root in roots))
                    self.assertEqual(neighbour.read_text(), 'must survive')


    def test_shell_edge_refuses_loop_and_getopts_writes(self):
        fn = self.ns['shell_python_module_route']
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        header = next(line for line in text.splitlines()
                      if '"${py_cmd[@]}" - ' in line and 'closure_automatic_effects.py' in line)
        for statement, expected in (
                ('for py_cmd in false; do :; done', 'false'),
                ('getopts x py_cmd -x', 'x')):
            with self.subTest(statement=statement):
                actual = subprocess.run(['bash', '--noprofile', '--norc', '-c',
                    'py_cmd=(python); ' + statement + '; printf "%s" "${py_cmd[0]-UNSET}"'],
                    capture_output=True, text=True, timeout=5, check=True)
                self.assertEqual(actual.stdout, expected)
                self.assertFalse(fn('closure_automatic_effects.py',
                    text.replace(header, '  ' + statement + '\n' + header), self.payload,
                    PREFIX + 'check-closure-surface.sh'))

    def test_shell_edge_refuses_redirected_builtin_writes(self):
        fn = self.ns['shell_python_module_route']
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        header = next(line for line in text.splitlines()
                      if '"${py_cmd[@]}" - ' in line and 'closure_automatic_effects.py' in line)
        for statement, expected in (
                ('< /dev/null read -a py_cmd || :', 'UNSET'),
                ('read < /dev/null -a py_cmd || :', 'UNSET'),
                ('>/dev/null printf -v py_cmd %s false', 'false'),
                ('printf >/dev/null -v py_cmd %s false', 'false'),
                ('read 3</dev/null -u 3 -a py_cmd || :', 'UNSET'),
                ('builtin read </dev/null -a py_cmd || :', 'UNSET'),
                ('mapfile </dev/null -t py_cmd', 'UNSET'),
                ('unset >/dev/null py_cmd', 'UNSET')):
            with self.subTest(statement=statement):
                actual = subprocess.run(['bash', '--noprofile', '--norc', '-c',
                    'py_cmd=(python); ' + statement + '; printf "%s" "${py_cmd[0]-UNSET}"'],
                    capture_output=True, text=True, timeout=5, check=True)
                self.assertEqual(actual.stdout, expected)
                self.assertFalse(fn('closure_automatic_effects.py',
                    text.replace(header, '  ' + statement + '\n' + header), self.payload,
                    PREFIX + 'check-closure-surface.sh'))

    def test_shell_edge_refuses_interpreter_function_shadow(self):
        fn = self.ns['shell_python_module_route']
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        header = next(line for line in text.splitlines()
                      if '"${py_cmd[@]}" - ' in line and 'closure_automatic_effects.py' in line)
        for statement in ('python() { :; }', 'function python { :; }',
                          'function python () { :; }', 'python ( ) { :; }'):
            with self.subTest(statement=statement):
                actual = subprocess.run(['bash', '--noprofile', '--norc', '-c',
                    statement + '; type -t python'], capture_output=True, text=True,
                    timeout=5, check=True)
                self.assertEqual(actual.stdout.strip(), 'function')
                self.assertFalse(fn('closure_automatic_effects.py',
                    text.replace(header, '  ' + statement + '\n' + header), self.payload,
                    PREFIX + 'check-closure-surface.sh'))

    def test_shell_edge_preserves_unrelated_implicit_writes_and_quoted_redirects(self):
        fn = self.ns['shell_python_module_route']
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        header = next(line for line in text.splitlines()
                      if '"${py_cmd[@]}" - ' in line and 'closure_automatic_effects.py' in line)
        for statement in (
                'for other in false; do :; done', 'getopts x other -x',
                '< /dev/null read -a other || :', 'read < /dev/null -a other || :',
                'printf >/dev/null -v other %s false', 'unset >/dev/null other',
                "printf '%s' 'for py_cmd in false; do :; done' >/dev/null",
                "printf '%s' 'getopts x py_cmd -x' >/dev/null",
                "printf '%s' '>/dev/null' '-v' 'py_cmd' >/dev/null",
                'other_function() { :; }', "message='python ( ) { :; }'",
                'command -v python >/dev/null 2>&1'):
            with self.subTest(statement=statement):
                actual = subprocess.run(['bash', '--noprofile', '--norc', '-c',
                    'py_cmd=(python); ' + statement + '; printf "%s" "${py_cmd[0]-UNSET}"'],
                    capture_output=True, text=True, timeout=5, check=True)
                self.assertEqual(actual.stdout, 'python')
                self.assertTrue(fn('closure_automatic_effects.py',
                    text.replace(header, '  ' + statement + '\n' + header), self.payload,
                    PREFIX + 'check-closure-surface.sh'))

    def test_query_canonical_values_refuse_cycles_and_excess_depth(self):
        m = load(PREFIX + 'operational-evidence.py')
        cycle = []
        cycle.append(cycle)
        deep = []
        for _ in range(1600):
            deep = [deep]
        for payload in (cycle, deep):
            for placement in ('record', 'omitted'):
                with self.subTest(placement=placement, cycle=payload is cycle):
                    record = dict(id='a', family=m.FAMILIES[0],
                                  currentness=dict(state='CURRENT', invalidators=[]))
                    snapshot = dict(schema_version=m.SNAPSHOT_PAYLOAD_SCHEMA,
                                    families=list(m.FAMILIES), collections=dict(rows=[record]))
                    if placement == 'record':
                        record['data'] = payload
                    else:
                        snapshot['missing_or_omitted_state'] = payload
                    with self.assertRaises(m.OperationalEvidenceError) as caught:
                        m.evaluate_currentness(snapshot)
                    self.assertEqual(caught.exception.code, 'OE_JSON_MODEL_INVALID')
        value = {'rows': [[{'text': 'valid', 'number': 4}]]}
        self.assertEqual(json.loads(m.canonical_json_v1(value)), value)

    def test_query_rejects_mapping_family_census(self):
        m = load(PREFIX + 'operational-evidence.py')
        for families in (dict.fromkeys(m.FAMILIES),):
            for operation in (m.evaluate_currentness,
                              lambda snapshot: m.query_family(snapshot, m.FAMILIES[0]),
                              lambda snapshot: m.explain_history_why_v1(snapshot, 'absent')):
                with self.subTest(families=type(families).__name__, operation=operation):
                    snapshot = dict(schema_version=m.SNAPSHOT_PAYLOAD_SCHEMA,
                                    families=families, collections={})
                    with self.assertRaises(m.OperationalEvidenceError) as caught:
                        operation(snapshot)
                    self.assertEqual(caught.exception.code, 'OE_QUERY_SNAPSHOT_INVALID')
        valid = dict(schema_version=m.SNAPSHOT_PAYLOAD_SCHEMA,
                     families=list(m.FAMILIES), collections={})
        self.assertEqual(m.evaluate_currentness(valid)['families'], list(m.FAMILIES))

    def test_query_walks_deep_collections_and_refuses_container_cycles(self):
        m = load(PREFIX + 'operational-evidence.py')
        row = dict(id='deep', family=m.FAMILIES[0],
                   currentness=dict(state='CURRENT', invalidators=[]))
        value = row
        for index in range(1600):
            value = {'level': value} if index % 2 else [value]
        snapshot = dict(schema_version=m.SNAPSHOT_PAYLOAD_SCHEMA,
                        families=list(m.FAMILIES), collections={'root': value})
        self.assertEqual(m.query_family(snapshot, m.FAMILIES[0])['rows'][0]['record'], row)
        cyclic = {}; cyclic['self'] = cyclic
        snapshot['collections'] = cyclic
        with self.assertRaises(m.OperationalEvidenceError) as caught:
            m.evaluate_currentness(snapshot)
        self.assertEqual(caught.exception.code, 'OE_QUERY_SNAPSHOT_INVALID')
        # Repeated inert containers are not cycles; repeated record IDs are
        # independently refused by the pre-existing identity contract.
        snapshot['collections'] = {'a': [], 'b': []}
        snapshot['collections']['b'] = snapshot['collections']['a']
        self.assertEqual(m.query_family(snapshot, m.FAMILIES[0])['rows'], [])

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

    def test_shell_edge_refuses_builtin_and_indirect_interpreter_writes(self):
        fn = self.ns['shell_python_module_route']
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        header = next(line for line in text.splitlines()
                      if '"${py_cmd[@]}" - ' in line and 'closure_automatic_effects.py' in line)
        for statement in (
                'mapfile -t py_cmd < /dev/null', 'readarray py_cmd < /dev/null',
                'read -a py_cmd < /dev/null || :', 'read -r py_cmd < /dev/null || :',
                'printf -v py_cmd %s false', "printf -v 'py_cmd[0]' %s false",
                'builtin printf -v py_cmd %s false', 'command mapfile -t py_cmd < /dev/null',
                "eval 'unset py_cmd'", 'source ./opaque.sh', '. ./opaque.sh',
                'declare -n selected=py_cmd; unset selected',
                'typeset -n selected=py_cmd; unset selected',
                'mapfile -C clear_interpreter py_cmd < /dev/null',
                'read -a "$selected_array" < /dev/null || :',
                'printf -v "$selected_array" %s false'):
            with self.subTest(statement=statement):
                mutation = text.replace(header, '  ' + statement + '\n' + header)
                self.assertFalse(fn('closure_automatic_effects.py', mutation, self.payload,
                                    PREFIX + 'check-closure-surface.sh'))

    def test_shell_edge_preserves_unrelated_builtin_destinations_and_data(self):
        fn = self.ns['shell_python_module_route']
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        header = next(line for line in text.splitlines()
                      if '"${py_cmd[@]}" - ' in line and 'closure_automatic_effects.py' in line)
        for statement in (
                'mapfile -t unrelated < /dev/null', 'readarray unrelated < /dev/null',
                'read -a unrelated < /dev/null || :', 'read -r unrelated < /dev/null || :',
                'read -- unrelated < /dev/null || :',
                'read -p py_cmd unrelated < /dev/null || :',
                "printf -v unrelated '%s' py_cmd", "printf '%s' 'mapfile py_cmd' >/dev/null",
                "message='eval unset py_cmd'", '# source ./opaque.sh',
                'declare -a unrelated', 'command -v mapfile >/dev/null'):
            with self.subTest(statement=statement):
                mutation = text.replace(header, '  ' + statement + '\n' + header)
                self.assertTrue(fn('closure_automatic_effects.py', mutation, self.payload,
                                   PREFIX + 'check-closure-surface.sh'))

    def test_shell_edge_refuses_opaque_arithmetic_interpreter_changes(self):
        fn = self.ns['shell_python_module_route']
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        header = next(line for line in text.splitlines()
                      if '"${py_cmd[@]}" - ' in line and 'closure_automatic_effects.py' in line)
        for statement in ("let 'py_cmd[0]++'", "builtin let 'py_cmd[0]++'",
                          "R=1 command let 'py_cmd[0]++'", '(( py_cmd[0]++ ))',
                          ': "$((py_cmd[0]++))"', ': $((py_cmd[0]++))',
                          "operand='py_cmd[0]++'; : \"$((operand))\"",
                          "operand='py_cmd[0]++'; : \"$((operand + 1))\""):
            with self.subTest(statement=statement):
                actual = subprocess.run(['bash', '--noprofile', '--norc', '-c',
                    'py_cmd=(python); ' + statement + '; printf "%s" "${py_cmd[0]}"'],
                    capture_output=True, text=True, check=True)
                self.assertEqual(actual.stdout, '1', 'Arithmetic witness did not change the interpreter')
                mutation = text.replace(header, '  ' + statement + '\n' + header)
                self.assertFalse(fn('closure_automatic_effects.py', mutation, self.payload,
                                    PREFIX + 'check-closure-surface.sh'))

    def test_shell_edge_preserves_declaration_lookup_and_inert_arithmetic(self):
        fn = self.ns['shell_python_module_route']
        text = (ROOT / (PREFIX + 'check-closure-surface.sh')).read_text()
        header = next(line for line in text.splitlines()
                      if '"${py_cmd[@]}" - ' in line and 'closure_automatic_effects.py' in line)
        for statement in ('declare -p py_cmd >/dev/null', 'typeset -p -- py_cmd >/dev/null',
                          'command -v let >/dev/null', '# (( py_cmd[0]++ ))',
                          ': "$((1 + 1))"', 'counter=0\ncounter=$((counter + 1))',
                          "printf '%s' '$((py_cmd[0]++))' >/dev/null",
                          "printf '%s' '(( py_cmd[0]++ ))' >/dev/null",
                          'printf "%s" "\\$((py_cmd[0]++))" >/dev/null'):
            with self.subTest(statement=statement):
                actual = subprocess.run(['bash', '--noprofile', '--norc', '-c',
                    'py_cmd=(python); ' + statement + '\nprintf "%s" "${py_cmd[0]}"'],
                    capture_output=True, text=True, check=True)
                self.assertEqual(actual.stdout, 'python', 'Positive neighbour changed the interpreter')
                mutation = text.replace(header, '  ' + statement + '\n' + header)
                self.assertTrue(fn('closure_automatic_effects.py', mutation, self.payload,
                                   PREFIX + 'check-closure-surface.sh'))

    def test_why_rejects_malformed_relation_and_contrary_shapes(self):
        import copy
        m = load(PREFIX + 'operational-evidence.py')
        def row(identity):
            return dict(id=identity, family=m.FAMILIES[0],
                        currentness=dict(state='CURRENT', invalidators=[]))
        for field, values in {
            'source_entity_id': [None, [], {}, 0, ''],
            'target_entity_id': [None, [], {}, 0, ''],
            'relation_type': [None, [], {}, 0, ''],
            'contrary_evidence': [None, 0, 'opposed', {}, [None]]
        }.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    a, b, relation = row('a'), row('b'), row('r')
                    relation.update(relation_type='depends-on', source_entity_id='a', target_entity_id='b')
                    (a if field == 'contrary_evidence' else relation)[field] = value
                    snapshot = dict(schema_version=m.SNAPSHOT_PAYLOAD_SCHEMA, families=list(m.FAMILIES),
                                    collections=dict(rows=[a, b, relation]))
                    before = copy.deepcopy(snapshot)
                    with self.assertRaises(m.OperationalEvidenceError) as caught:
                        m.explain_history_why_v1(snapshot, 'a')
                    self.assertEqual(caught.exception.code, 'OE_QUERY_SNAPSHOT_INVALID')
                    self.assertEqual(snapshot, before)

    def test_why_retains_lineage_contrary_evidence_and_cycle_refusal(self):
        m = load(PREFIX + 'operational-evidence.py')
        def row(identity):
            return dict(id=identity, family=m.FAMILIES[0],
                        currentness=dict(state='CURRENT', invalidators=[]))
        a, b, relation = row('a'), row('b'), row('r')
        a['contrary_evidence'] = ['contrary-open']
        relation.update(relation_type='depends-on', source_entity_id='a', target_entity_id='b')
        snapshot = dict(schema_version=m.SNAPSHOT_PAYLOAD_SCHEMA, families=list(m.FAMILIES),
                        collections=dict(rows=[a, b, relation]))
        why = m.explain_history_why_v1(snapshot, 'a')
        self.assertEqual([r['id'] for r in why['chain']], ['a', 'b'])
        self.assertEqual(why['contrary_evidence'], ['contrary-open'])
        relation['target_entity_id'] = 'a'
        with self.assertRaises(m.OperationalEvidenceError) as caught:
            m.explain_history_why_v1(snapshot, 'a')
        self.assertEqual(caught.exception.code, 'OE_WHY_CYCLE')

    def test_why_lineage_exceeds_python_call_stack_without_losing_edges(self):
        m = load(PREFIX + 'operational-evidence.py')
        count = 1300
        rows = [dict(id='node-' + str(i), family=m.FAMILIES[0],
                     currentness=dict(state='CURRENT', invalidators=[])) for i in range(count)]
        relations = [dict(id='edge-' + str(i), family=m.FAMILIES[0],
                     currentness=dict(state='CURRENT', invalidators=[]), relation_type='depends-on',
                     source_entity_id='node-' + str(i), target_entity_id='node-' + str(i + 1))
                     for i in range(count - 1)]
        snapshot = dict(schema_version=m.SNAPSHOT_PAYLOAD_SCHEMA, families=list(m.FAMILIES),
                        collections=dict(rows=rows, relations=relations))
        why = m.explain_history_why_v1(snapshot, 'node-0')
        self.assertEqual([r['id'] for r in why['chain']], ['node-' + str(i) for i in range(count)])
        self.assertEqual(len(why['relations']), count - 1)
        relations[-1]['target_entity_id'] = 'node-0'
        with self.assertRaises(m.OperationalEvidenceError) as caught:
            m.explain_history_why_v1(snapshot, 'node-0')
        self.assertEqual(caught.exception.code, 'OE_WHY_CYCLE')

    def test_branch_globs_preserve_slash_negation_and_documented_operators(self):
        m = load(PREFIX + 'closure_automatic_effects.py')
        # Independent expectations from GitHub's filter-pattern contract, not fnmatch.
        cases = [
            (['publication/*'], 'publication/a/b', False),
            (['**', '!publication/*'], 'publication/a/b', True),
            (['publication/**'], 'publication/a/b', True),
            (['*'], 'main', True), (['*'], 'release/v1', False),
            (['feature/*'], 'feature/a', True),
            (['octo?'], 'oct', True), (['octo?'], 'octo', True), (['octo?'], 'octox', False),
            (['v[12].[0-9]+.[0-9]+'], 'v1.10.1', True),
            (['v[12].[0-9]+.[0-9]+'], 'v3.10.1', False),
            (['[CB]at'], 'Cat', True), (['[CB]at'], 'Bat', True),
            ([r'a\+b'], 'a+b', True),
            (['releases/**', '!releases/**-alpha'], 'releases/beta/3-alpha', False),
            (['releases/**', '!releases/**-alpha', 'releases/beta/3-alpha'], 'releases/beta/3-alpha', True),
        ]
        for patterns, branch, expected in cases:
            with self.subTest(patterns=patterns, branch=branch):
                self.assertEqual(m.pattern_matches(patterns, branch), expected)

    def test_branch_globs_refuse_unsupported_or_malformed_patterns(self):
        m = load(PREFIX + 'closure_automatic_effects.py')
        for pattern in ('[', '[]', '[z-a]', 'a++', '\\', '***'):
            with self.subTest(pattern=pattern), self.assertRaises(SystemExit):
                m.pattern_matches([pattern], 'publication/a/b')

    def test_reusable_workflow_does_not_claim_complete_direct_effects(self):
        m = load(PREFIX + 'closure_automatic_effects.py')
        for target in ('./.github/workflows/deploy.yml', 'owner/repo/.github/workflows/deploy.yml@main'):
            nodes = m.parse_yaml_nodes('on: push\njobs:\n  publish:\n    uses: ' + target + '\n')
            with self.subTest(target=target), self.assertRaisesRegex(SystemExit, 'reusable workflow'):
                m.direct_effects('fixture.yml', '.github/workflows/fixture.yml', nodes)

    def test_direct_deployment_and_unmatched_reusable_workflow_neighbours(self):
        m = load(PREFIX + 'closure_automatic_effects.py')
        nodes = m.parse_yaml_nodes('on: push\njobs:\n  publish:\n    steps:\n      - uses: actions/deploy-pages@v4\n')
        self.assertEqual(m.direct_effects('fixture.yml', '.github/workflows/fixture.yml', nodes),
                         {'workflow-run:.github/workflows/fixture.yml', 'deployment:github-pages'})
        nodes = m.parse_yaml_nodes('on:\n  push:\n    branches: [other]\njobs:\n  publish:\n    uses: ./.github/workflows/deploy.yml\n')
        self.assertFalse(m.trigger_matches('fixture.yml', nodes, 'push', 'main'))

    def test_fr05_escaped_yaml_branch_is_an_explicit_refusal(self):
        m = load(PREFIX + 'closure_automatic_effects.py')
        for scalar in (r'"\u006dain"', r'"\x6dain"', r'"\U0000006dain"'):
            for filters in ('    branches: [' + scalar + ']\n',
                            '    branches:\n      - ' + scalar + '\n'):
                body = 'on:\n  push:\n' + filters
                with self.subTest(scalar=scalar, filters=filters):
                    nodes = m.parse_yaml_nodes(body)
                    with self.assertRaisesRegex(SystemExit, 'unsupported.*quoted.*scalar'):
                        m.trigger_matches('fixture.yml', nodes, 'push', 'main')

    def test_fr05_literal_quoted_and_single_quote_glob_neighbours(self):
        m = load(PREFIX + 'closure_automatic_effects.py')
        for scalar, branch, expected in [('"main"', 'main', True),
                                          ("'main'", 'main', True),
                                          ('main', 'main', True),
                                          ('"other"', 'main', False),
                                          (r"'a\+b'", 'a+b', True),
                                          (r"'\u006dain'", 'main', False)]:
            with self.subTest(scalar=scalar):
                nodes = m.parse_yaml_nodes('on:\n  push:\n    branches: [' + scalar + ']\n')
                self.assertEqual(m.trigger_matches('fixture.yml', nodes, 'push', branch), expected)

    def test_yaml_mapping_keys_share_scalar_refusal(self):
        m = load(PREFIX + 'closure_automatic_effects.py')
        for key in (r'"pu\u0073h"', r'"u\u0073es"', r'"branc\x68es"',
                    r'"j\U0000006fbs"', r'"u\"ses"', '"unclosed'):
            with self.subTest(key=key), self.assertRaisesRegex(SystemExit, 'unsupported.*quoted'):
                m.mapping_entry(key + ': value')
        for key in ('uses', '"uses"', "'uses'"):
            with self.subTest(key=key):
                self.assertEqual(m.mapping_entry(key + ': actions/deploy-pages@v4'),
                                 ('uses', 'actions/deploy-pages@v4'))

    def test_yaml_escaped_keys_refuse_at_trigger_and_action_boundaries(self):
        m = load(PREFIX + 'closure_automatic_effects.py')
        for body in (
                '"o\\u006e": push\n',
                'on:\n  "pu\\u0073h":\n    branches: [main]\n',
                'on:\n  push:\n    "branc\\u0068es": [main]\n'):
            with self.subTest(body=body), self.assertRaisesRegex(SystemExit, 'unsupported.*quoted'):
                m.trigger_matches('fixture.yml', m.parse_yaml_nodes(body), 'push', 'main')
        for body in (
                'on: push\n"j\\u006fbs":\n  publish:\n    steps: []\n',
                'on: push\njobs:\n  "publi\\u0073h":\n    steps: []\n',
                'on: push\njobs:\n  publish:\n    "step\\u0073": []\n',
                'on: push\njobs:\n  publish:\n    steps:\n      - "u\\u0073es": actions/deploy-pages@v4\n',
                'on: push\njobs:\n  publish:\n    steps:\n      - name: publish\n        "u\\u0073es": actions/deploy-pages@v4\n'):
            with self.subTest(body=body), self.assertRaisesRegex(SystemExit, 'unsupported.*quoted'):
                m.direct_effects('fixture.yml', '.github/workflows/fixture.yml', m.parse_yaml_nodes(body))

    def test_yaml_literal_keys_preserve_trigger_and_deployment(self):
        m = load(PREFIX + 'closure_automatic_effects.py')
        for key in ('push', '"push"', "'push'"):
            for uses in ('uses', '"uses"', "'uses'"):
                body = ('on:\n  ' + key + ':\n    branches: [main]\njobs:\n  publish:\n'
                        '    steps:\n      - ' + uses + ': actions/deploy-pages@v4\n')
                nodes = m.parse_yaml_nodes(body)
                with self.subTest(key=key, uses=uses):
                    self.assertTrue(m.trigger_matches('fixture.yml', nodes, 'push', 'main'))
                    self.assertFalse(m.trigger_matches('fixture.yml', nodes, 'push', 'other'))
                    self.assertEqual(m.direct_effects('fixture.yml', '.github/workflows/fixture.yml', nodes),
                                     {'workflow-run:.github/workflows/fixture.yml', 'deployment:github-pages'})

    def test_fr05_escaped_branch_cannot_admit_empty_effect_plan(self):
        m = load(PREFIX + 'closure_automatic_effects.py')
        with tempfile.TemporaryDirectory(prefix='fr05-effects-') as directory:
            root = Path(directory)
            workflow = root / '.github/workflows/publish.yml'
            workflow.parent.mkdir(parents=True)
            workflow.write_text('on:\n  push:\n    branches: ["\\u006dain"]\n'
                                'jobs:\n  publish:\n    runs-on: ubuntu-latest\n'
                                '    steps:\n      - uses: actions/deploy-pages@v4\n')
            plan = root / 'plan.md'
            plan.write_text('automatic-effect-preflight: event:push|ref:main|workflows:none|'
                            'effects:none|post-state-readback:trigger-read-only|'
                            'excluded-outcomes:no automatic effects\n')
            with self.assertRaisesRegex(SystemExit, 'unsupported.*quoted.*scalar'):
                m.main([str(root), 'push', 'main', str(plan)])

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


    def test_query_omission_census_requires_array_in_every_projection(self):
        m = load(PREFIX + 'operational-evidence.py')
        for invalid in (None, 0, True, 'missing', {}, {'hidden': 'gap'}):
            for query in (m.evaluate_currentness,
                          lambda snapshot: m.query_family(snapshot, m.FAMILIES[0])):
                with self.subTest(value=invalid, query=query):
                    snapshot = dict(schema_version=m.SNAPSHOT_PAYLOAD_SCHEMA,
                        families=list(m.FAMILIES), collections={},
                        missing_or_omitted_state=invalid)
                    with self.assertRaises(m.OperationalEvidenceError) as caught:
                        query(snapshot)
                    self.assertEqual(caught.exception.code, 'OE_QUERY_SNAPSHOT_INVALID')
        for omitted in ([], ['unknown'], [{'scope': 'x', 'state': 'UNKNOWN'}]):
            snapshot = dict(schema_version=m.SNAPSHOT_PAYLOAD_SCHEMA,
                families=list(m.FAMILIES), collections={}, missing_or_omitted_state=omitted)
            result = m.query_family(snapshot, m.FAMILIES[0])
            self.assertEqual(result['missing_or_omitted_state'], omitted)
            self.assertEqual(snapshot['missing_or_omitted_state'], omitted)

class NativeBoundaryBindingsTests(unittest.TestCase):
    """Exercise real source loaders and the exact final-fence AST, not host trust."""
    def test_native_capture_resolves_its_exact_route_owner(self):
        provider = load(PREFIX + 'native-worker-capture.py')
        owner = provider.route_owner()
        self.assertEqual(Path(owner.__file__).resolve(), ROOT / PREFIX / 'route-transaction.py')

    def test_parent_capture_loader_follows_exact_provider(self):
        parent = load(PREFIX + 'child-parent-visibility.py')
        provider = parent.selected_capture()
        owner = provider.route_owner()
        self.assertEqual(Path(owner.__file__).resolve(), ROOT / PREFIX / 'route-transaction.py')

    def test_native_capture_rejects_modified_route_owner(self):
        provider = load(PREFIX + 'native-worker-capture.py')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'route-transaction.py').write_bytes(
                (ROOT / PREFIX / 'route-transaction.py').read_bytes() + b'\n# foreign postimage\n')
            provider.ROOT = root
            with self.assertRaisesRegex(ValueError, 'route owner missing or composition changed'):
                provider.route_owner()

    def final_fence(self, route_size, other_size, *, mutated=False):
        oe = load(PREFIX + 'operational-evidence.py')
        tree = ast.parse((ROOT / PREFIX / 'operational-evidence.py').read_text())
        selected = [node for node in ast.walk(tree) if isinstance(node, ast.If)
                    and '$native.final_file_fence' in ast.unparse(node.test)]
        self.assertEqual(len(selected), 1)
        with tempfile.TemporaryDirectory() as td:
            route, other = Path(td) / 'route.py', Path(td) / 'other.json'
            route.write_bytes(b'x' * route_size)
            other.write_bytes(b'y' * other_size)
            expected = {route: route.read_bytes(), other: other.read_bytes()}
            if mutated:
                route.write_bytes(b'z' * route_size)
            namespace = dict(_native_file=oe._native_file, _error=oe._error,
                             file_fence=expected, route_validator_path=route)
            exec(compile(ast.Module(body=selected, type_ignores=[]),
                         'exact-production-final-file-fence', 'exec'), namespace)

    def test_route_above_default_bound_remains_valid(self):
        self.final_fence(256 * 1024 + 1, 128)

    def test_route_exact_opening_bound_remains_valid(self):
        self.final_fence(512 * 1024, 256 * 1024)

    def test_route_above_opening_bound_is_refused(self):
        with self.assertRaises(Exception) as caught:
            self.final_fence(512 * 1024 + 1, 1)
        self.assertTrue(hasattr(caught.exception, 'code'))

    def test_other_files_do_not_gain_route_bound(self):
        with self.assertRaises(Exception) as caught:
            self.final_fence(1, 256 * 1024 + 1)
        self.assertTrue(hasattr(caught.exception, 'code'))

    def test_same_size_route_mutation_is_refused(self):
        with self.assertRaises(Exception) as caught:
            self.final_fence(300000, 1, mutated=True)
        self.assertEqual(caught.exception.code, 'OE_NATIVE_CURRENT_CHANGED')

if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0], *UNIT_ARGS])
