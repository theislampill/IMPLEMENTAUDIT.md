#!/usr/bin/env python3
"""Portable R0033/R0035 source-interface and static-security controls.

Native currentness is explicitly injected. No canonical claim/controller,
host-source admission, real lifecycle, acceptance or campaign credit is tested.
Only the supplied repository's exact source files and owned temporary fixtures
are used. Production source pins are checked, never rewritten by this fixture.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import contextlib
import copy
import ctypes
import hashlib
import io
import json
import os
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
import zlib

GOLDEN_PATH = Path(__file__).resolve().with_name('native-route-v1-golden.json')
V1_GOLDEN_SHA256 = 'a49725e1e14126bd62752645ea1445f4077183e919d5208ea0c26d578f2df18c'
RECEIPT = 'refs/implementaudit/continuity-receipts/injected-source-control/G000A@' + 'a' * 40
WORK = RT = WG = GIT = BASH = None
BASELINE = []


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    raw = path.read_bytes()
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def expected_small_read_set(root):
    """Independent two-file fixture oracle for the retained v1 value format."""
    members = [
        ['nested', 'DIRECTORY', (root / 'data/nested').stat().st_mode & 4095],
        ['nested/two.txt', (root / 'data/nested/two.txt').stat().st_mode & 4095, hashlib.sha256(b'two').hexdigest()],
        ['one.txt', (root / 'data/one.txt').stat().st_mode & 4095, hashlib.sha256(b'one').hexdigest()],
    ]
    return {'path:absent.txt': {'status': 'MISSING', 'sha256': None},
        'path:data': {'status': 'PRESENT_DIRECTORY',
                      'sha256': h([(root / 'data').stat().st_mode & 4095, members])}}


def h(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def ident(text):
    return {'identity': text, 'digest': 'sha256:' + h({'identity': text})}


def seal(value):
    value = copy.deepcopy(value)
    value.pop('digest', None)
    value['digest'] = h(value)
    return value


def record(root):
    scope = ident('review:bounded')
    boundary = {'kind': 'handoff-resume', 'event_id': 'nonprotected-source-control'}
    boundary['digest'] = 'sha256:' + h(boundary)
    action = {'identity': 'review', 'class': 'INDEPENDENT_REVIEW', 'argv': ['route-trigger', 'INDEPENDENT_REVIEW']}
    action['digest'] = 'sha256:' + h(action)
    return dict(schema='implementaudit.route-decision.v1', predicate_version='R0033.route-predicate.v1',
        controller_id='bounded-control', claim_id='1' * 32, explicit_run_root=str(root),
        continuity_generation='G000A', continuity_receipt='refs/implementaudit/continuity-receipts/bounded-control/G000A@' + 'a' * 40,
        host_id='source-control-host', host_session_id='source-control-session', host_binding_generation='G000B',
        host_correlation_id='sha256:' + 'b' * 64, scope=scope, boundary=boundary, action=action,
        inputs=[dict(identity='test-input', path='input.txt', digest='sha256:' + 'c' * 64, status='CURRENT')],
        record_identity='sha256:' + 'd' * 64, expiry_fingerprint='sha256:' + 'e' * 64,
        decision='REQUIRED', classification='MECHANICALLY_REQUIRED', route_transaction_id='sha256:' + 'f' * 64,
        obligation_id='sha256:' + '1' * 64, route_state='UNSATISFIED')


def summary(rec):
    return dict(controller_id=rec['controller_id'], controller_record_oid='2' * 40,
        ref='refs/implementaudit/route-decisions/' + rec['controller_id'], record_oid='3' * 40,
        **{k: rec[k] for k in ('record_identity', 'decision', 'classification', 'route_transaction_id', 'obligation_id', 'route_state')})


def export_value(rec):
    """Actual new adapter, with pre-existing native IO predicates injected."""
    route = summary(rec)
    with patch.object(RT, 'validate_pure_current_route', return_value=route), \
         patch.object(RT, 'current_ref', return_value=(route['record_oid'], rec)), \
         patch.object(RT, 'validate_canonical_route_record_bytes'):
        return RT.read_current_route_scope_v1(WORK, rec['controller_id'])


def binding(rec):
    return dict(acquisition='NATIVE_CONTINUITY_VERIFIED', controller=rec['controller_id'], claim=rec['claim_id'],
        receipt=rec['continuity_receipt'], epoch=rec['continuity_generation'], candidate_head='4' * 40,
        candidate_tree='5' * 40, worktree_digest='6' * 64, continuity_helper_digest='7' * 64,
        read_set={}, input_root_identity='8' * 64)


def node(name, *, kind='TASK', scopes=(), requires=()):
    return dict(id=name, parent=None if name == 'root' else 'root', kind=kind, state='OPEN', requires=list(requires),
        optional=[], reads=[], writes=[], acceptance=[], resources=[], authority=[], effect='READ_ONLY',
        authorization='PERMITTED', independence='KNOWN', resource_demand=1, rank=0, route_scopes=list(scopes),
        logical_delivery=None, future_consumer=None, invalidators=[], independent_results=True,
        context=dict(locality='GOVERNOR', governor_cost=1, child_cost=2, return_cost=1, useful_value=3), done_evidence=None)


def fenced(value):
    return ('```implementaudit-work-graph\n' + json.dumps(value, ensure_ascii=False) + '\n```\n').encode()


def snapshot(rec, *, version=2):
    first = dict(schema='implementaudit.work-graph-route-fact.v1',
        scope=rec['scope']['identity'], obligation=rec['obligation_id'], generation='G000A', binding='legacy',
        continuity='legacy', status='SATISFIED', satisfaction='caller-yes', expected_satisfaction='caller-yes', source_digest='9' * 64)
    nodes = [node('root', kind='PLAN'), node('scoped', scopes=[rec['scope']['identity']]),
        node('scoped_two', scopes=[rec['scope']['identity'], 'second-boundary']),
        node('dependent', requires=['scoped']), node('independent'), node('uncovered', scopes=['second-boundary'])]
    state = dict(schema='implementaudit.native-state.v1', campaign='source-control', root='root', original_scope='source-interface',
        nodes=sorted(n['id'] for n in nodes), event=dict(id='event-one', kind='REDERIVE', subject='root'),
        context=dict(host_capacity=4, operator_ceiling=None, reserve=0, route_facts=[] if version == 2 else [first], outstanding_deliveries=[]))
    return {'STATE.md': fenced(state), 'ROADMAP.md': fenced(dict(schema='implementaudit.native-roadmap.v1', phases=[])),
            'tasks/controls.md': fenced(dict(schema='implementaudit.native-spec.v1', nodes=nodes))}


def native_compile(rec):
    observed = WG._RouteScopeObservation(export_value(rec), WG._NATIVE_ROUTE_OBSERVATION_KEY)
    # Explicit fixture injection. This is not acquired native evidence.
    return WG._compile_native_documents_v1(snapshot(rec), binding(rec), _route_observation=observed)


class Controls(unittest.TestCase):
    def setUp(self):
        self.rec = record(WORK / 'disposable-run')

    def test_01_v1_remains_unavailable_and_unchanged(self):
        raw = GOLDEN_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), V1_GOLDEN_SHA256)
        golden = json.loads(raw)
        snap, bound = snapshot(self.rec, version=1), binding(self.rec)
        actual_input = {'documents': {k: v.decode('utf-8') for k, v in snap.items()}, 'binding': bound}
        self.assertEqual(h(actual_input), golden['input_sha256'])
        self.assertEqual(golden['expected'], WG._compile_native_documents_v1(snap, bound))
        self.assertEqual(WG._native_route_block({'status': 'SATISFIED', 'satisfaction': 'yes', 'expected_satisfaction': 'yes'}, 'NATIVE_CONTINUITY_VERIFIED'), 'ROUTE_PRODUCER_UNAVAILABLE')

    def test_02_current_export_calls_existing_owner_guards(self):
        route = summary(self.rec)
        with patch.object(RT, 'validate_pure_current_route', return_value=route) as live, \
             patch.object(RT, 'current_ref', return_value=(route['record_oid'], self.rec)) as read, \
             patch.object(RT, 'validate_canonical_route_record_bytes') as canonical:
            result = RT.read_current_route_scope_v1(WORK, self.rec['controller_id'])
        self.assertEqual(live.call_count, 2)
        self.assertEqual(read.call_count, 1)
        self.assertEqual(canonical.call_count, 1)
        self.assertEqual(result['scope'], self.rec['scope'])
        self.assertEqual(result['establishes'], [])

    def test_03_complete_positive_and_uncovered_scope(self):
        graph = native_compile(self.rec)
        relation = WG.export_native_route_relation_v1(graph)
        self.assertEqual(relation['node_population'], ['dependent', 'independent', 'root', 'scoped', 'scoped_two', 'uncovered'])
        self.assertEqual(relation['direct_nodes'], ['scoped', 'scoped_two'])
        self.assertEqual(relation['affected_nodes'], ['dependent', 'root', 'scoped', 'scoped_two'])
        self.assertEqual(relation['independent_nodes'], ['independent', 'uncovered'])
        self.assertEqual(relation['uncovered_nodes'], ['scoped_two', 'uncovered'])
        states = {n['id']: n for n in graph['nodes']}
        self.assertEqual(states['independent']['state'], 'READY')
        self.assertIn('ROUTE_UNSATISFIED', states['scoped']['blocked_reasons'])
        self.assertIn('ROUTE_SCOPE_UNCOVERED', states['uncovered']['blocked_reasons'])
        self.assertEqual(relation['authority'], 'NONE')

    def test_04_wrong_obligation_transaction_generation_receipt_source(self):
        route = summary(self.rec)
        for key in ('obligation_id', 'route_transaction_id'):
            foreign = copy.deepcopy(self.rec)
            foreign[key] = 'sha256:' + '0' * 64
            with self.subTest(key=key), patch.object(RT, 'validate_pure_current_route', return_value=route), \
                 patch.object(RT, 'current_ref', return_value=(route['record_oid'], foreign)), \
                 patch.object(RT, 'validate_canonical_route_record_bytes'), redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
                RT.read_current_route_scope_v1(WORK, self.rec['controller_id'])
        for bucket, key, bad in [('owner', 'continuity_generation', 'G0009'),
                ('owner', 'continuity_receipt', self.rec['continuity_receipt'].replace('G000A', 'G0009')),
                ('source', 'producer_sha256', '0' * 64)]:
            with self.subTest(key=key):
                foreign = export_value(self.rec)
                foreign[bucket][key] = bad
                observed = WG._RouteScopeObservation(seal(foreign), WG._NATIVE_ROUTE_OBSERVATION_KEY)
                with self.assertRaises(WG.WorkGraphError):
                    WG._compile_native_documents_v1(snapshot(self.rec), binding(self.rec), _route_observation=observed)

    def test_05_wrong_node_and_incomplete_mapping(self):
        graph = native_compile(self.rec)
        for key, value in [('affected_nodes', ['independent']), ('node_population', ['scoped']),
                           ('obligation_id', 'sha256:' + '0' * 64), ('route_transaction_id', 'sha256:' + '0' * 64)]:
            with self.subTest(key=key):
                relation = WG.export_native_route_relation_v1(graph)
                relation[key] = value
                relation = seal(relation)
                with self.assertRaises(WG.WorkGraphError):
                    WG.validate_native_route_relation_v1(graph, relation)

    def test_06_incomplete_source_population(self):
        snap = snapshot(self.rec)
        state = WG._native_document(snap['STATE.md'], 'STATE.md', 'implementaudit.native-state.v1')
        state['nodes'].remove('independent')
        snap['STATE.md'] = fenced(state)
        with self.assertRaisesRegex(WG.WorkGraphError, 'population'):
            WG._compile_native_documents_v1(snap, binding(self.rec))

    def test_07_changed_scope_and_bad_scope_digest(self):
        changed = copy.deepcopy(self.rec)
        changed['scope'] = ident('other-scope')
        observed = WG._RouteScopeObservation(export_value(changed), WG._NATIVE_ROUTE_OBSERVATION_KEY)
        with self.assertRaisesRegex(WG.WorkGraphError, 'scope is absent'):
            WG._compile_native_documents_v1(snapshot(self.rec), binding(self.rec), _route_observation=observed)
        changed['scope']['digest'] = 'sha256:' + '0' * 64
        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            export_value(changed)

    def test_08_satisfaction_recomputes_only_affected_and_keeps_second_boundary(self):
        first = native_compile(self.rec)
        satisfied = copy.deepcopy(self.rec)
        satisfied.update(route_state='SATISFIED', record_identity='sha256:' + '2' * 64,
                         lifecycle={'governor_decision': {'digest': 'sha256:' + '3' * 64}})
        second = native_compile(satisfied)
        delta = WG.diff_native_graphs_v1(first, second)
        self.assertEqual(delta['invalidated'], ['dependent', 'root', 'scoped', 'scoped_two'])
        self.assertEqual(delta['preserved'], ['independent', 'uncovered'])
        states = {n['id']: n for n in second['nodes']}
        self.assertEqual(states['scoped']['state'], 'READY')
        self.assertEqual(states['scoped_two']['state'], 'BLOCKED')
        self.assertEqual(states['scoped_two']['blocked_reasons'], ['ROUTE_SCOPE_UNCOVERED'])

    def test_09_raw_dictionary_boolean_and_constructed_injection_refuse(self):
        for injected in (export_value(self.rec), True, {'authenticated': True}, object()):
            with self.subTest(type=type(injected).__name__), self.assertRaises(WG.WorkGraphError):
                WG._compile_native_documents_v1(snapshot(self.rec), binding(self.rec), _route_observation=injected)
        observed = WG._RouteScopeObservation(export_value(self.rec), WG._NATIVE_ROUTE_OBSERVATION_KEY)
        constructed = binding(self.rec)
        constructed['acquisition'] = 'CONSTRUCTED_FILESYSTEM'
        with self.assertRaisesRegex(WG.WorkGraphError, 'constructed'):
            WG._compile_native_documents_v1(snapshot(self.rec), constructed, _route_observation=observed)

    def test_10_changed_route_after_export_refuses(self):
        first = summary(self.rec)
        changed = dict(first, record_oid='4' * 40)
        with patch.object(RT, 'validate_pure_current_route', side_effect=[first, changed]), \
             patch.object(RT, 'current_ref', return_value=(first['record_oid'], self.rec)), \
             patch.object(RT, 'validate_canonical_route_record_bytes'), redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            RT.read_current_route_scope_v1(WORK, self.rec['controller_id'])

    def test_11_source_pinned_loader_and_drift_refusal(self):
        module, path, raw = WG._native_route_scope_module_v1()
        self.assertTrue(callable(module.read_current_route_scope_v1))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), WG._NATIVE_ROUTE_PRODUCER_SHA256)
        with tempfile.TemporaryDirectory(prefix='source-drift-', dir=WORK) as root:
            root = Path(root)
            (root / 'route-transaction.py').write_bytes(raw + b'\n')
            local_graph = types.ModuleType('_drift_graph')
            local_graph.__file__ = str(root / 'compile-work-graph.py')
            exec(compile(Path(WG.__file__).read_bytes(), local_graph.__file__, 'exec'), local_graph.__dict__)
            with self.assertRaisesRegex(local_graph.WorkGraphError, 'source identity changed'):
                local_graph._native_route_scope_module_v1()

    def test_12_non_ascii_scope_preserved(self):
        self.rec['scope'] = ident('مراجعة:نطاق-α')
        result = export_value(self.rec)
        self.assertEqual(result['scope'], self.rec['scope'])
        graph = native_compile(self.rec)
        self.assertEqual(WG.export_native_route_relation_v1(graph)['scope'], self.rec['scope'])

    def test_13_no_override_public_path_acquires_and_rechecks(self):
        with tempfile.TemporaryDirectory(prefix='public-path-', dir=WORK) as root:
            root = Path(root)
            rec = record(root)
            for name, raw in snapshot(rec).items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            before = {k: v for k, v in binding(rec).items() if k not in {'read_set', 'input_root_identity'}}
            fake_producer = types.SimpleNamespace(read_current_route_scope_v1=unittest.mock.Mock(return_value=export_value(rec)))
            with patch.object(WG, '_native_continuity', return_value=before) as continuity, \
                 patch.object(WG, '_native_route_scope_module_v1', return_value=(fake_producer, Path(RT.__file__), Path(RT.__file__).read_bytes())) as loader:
                graph = WG.read_native_run_v1(root, root)
            self.assertEqual(continuity.call_count, 2)
            self.assertEqual(fake_producer.read_current_route_scope_v1.call_count, 2)
            self.assertEqual(loader.call_count, 2)
            self.assertEqual(graph['schema'], 'implementaudit.native-work-graph.v2')
            self.assertEqual(graph['authority'], 'NONE')
            changed = copy.deepcopy(export_value(rec))
            changed['route']['record_oid'] = '4' * 40
            fake_producer.read_current_route_scope_v1 = unittest.mock.Mock(side_effect=[export_value(rec), seal(changed)])
            with patch.object(WG, '_native_continuity', return_value=before), \
                 patch.object(WG, '_native_route_scope_module_v1', return_value=(fake_producer, Path(RT.__file__), Path(RT.__file__).read_bytes())), \
                 self.assertRaisesRegex(WG.WorkGraphError, 'route changed'):
                WG.read_native_run_v1(root, root)

    def test_14_canonical_graph_bridge_population_scope_and_dependency(self):
        graph = native_compile(self.rec)
        cells = [dict(id=n['id'], deps=n['requires'], optional_deps=n['optional'],
                      route_scopes=n['route_scopes'], state=n['state']) for n in graph['nodes']]
        canonical = dict(schema='implementaudit.work-graph.v1', population={'total_cells': len(cells)},
                         cells=cells, serialization_groups={})
        raw = json.dumps(canonical).encode()
        joined = WG.bind_native_route_relation_v1(graph, raw)
        self.assertEqual(joined['canonical_work_graph_sha256'], hashlib.sha256(raw).hexdigest())
        for fault in ('population', 'scope', 'dependency'):
            changed = copy.deepcopy(canonical)
            if fault == 'population':
                changed['cells'] = [c for c in changed['cells'] if c['id'] != 'independent']
                changed['population']['total_cells'] -= 1
            elif fault == 'scope':
                next(c for c in changed['cells'] if c['id'] == 'scoped')['route_scopes'] = ['wrong-scope']
            else:
                next(c for c in changed['cells'] if c['id'] == 'dependent')['deps'] = []
            with self.subTest(fault=fault), self.assertRaises(WG.WorkGraphError):
                WG.bind_native_route_relation_v1(graph, json.dumps(changed).encode())

    def test_15_native_context_testimony_never_satisfies(self):
        snap = snapshot(self.rec, version=1)
        observed = WG._RouteScopeObservation(export_value(self.rec), WG._NATIVE_ROUTE_OBSERVATION_KEY)
        graph = WG._compile_native_documents_v1(snap, binding(self.rec), _route_observation=observed)
        scoped = next(n for n in graph['nodes'] if n['id'] == 'scoped')
        self.assertEqual(scoped['state'], 'BLOCKED')
        self.assertIn('ROUTE_UNSATISFIED', scoped['blocked_reasons'])


@contextlib.contextmanager
def disposable(prefix):
    path = Path(tempfile.mkdtemp(prefix=prefix, dir=WORK)).absolute()
    try:
        yield path
    finally:
        resolved = path.resolve(strict=True)
        resolved.relative_to(WORK.resolve(strict=True))
        if resolved != path or path.is_symlink():
            raise RuntimeError('disposable cleanup custody changed; retained')
        shutil.rmtree(path)


def git(repo, *args):
    environment = {k: v for k, v in os.environ.items() if not k.upper().startswith('GIT_')}
    environment.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT='0')
    return subprocess.run([str(GIT), '-C', str(repo), *args], env=environment,
        capture_output=True, check=True)


def object_file(repo, kind, raw):
    encoded = kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw
    oid = hashlib.sha1(encoded).hexdigest()
    target = repo / '.git/objects' / oid[:2] / oid[2:]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(zlib.compress(encoded))
    return oid


def git_fixture(root):
    """Synthetic Git dataset; no git commit, clone, source refs or controller."""
    (root / '.git/objects').mkdir(parents=True)
    (root / '.git/refs/heads').mkdir(parents=True)
    (root / '.git/HEAD').write_bytes(b'ref: refs/heads/main\n')
    (root / '.git/config').write_bytes(b'[core]\nrepositoryformatversion = 0\nbare = false\n')
    files = {'.gitattributes': b'*.txt filter=ownedprobe\n', 'data.txt': b'old-content\n'}
    tree = b''
    for name, raw in sorted(files.items()):
        (root / name).write_bytes(raw)
        oid = object_file(root, 'blob', raw)
        tree += b'100644 ' + name.encode() + b'\0' + bytes.fromhex(oid)
        git(root, 'update-index', '--add', '--cacheinfo', '100644,' + oid + ',' + name)
    tree_oid = object_file(root, 'tree', tree)
    commit = (f'tree {tree_oid}\nauthor Source Control <fixture@example.invalid> 0 +0000\n'
              f'committer Source Control <fixture@example.invalid> 0 +0000\n\nSynthetic source-security fixture.\n').encode()
    oid = object_file(root, 'commit', commit)
    (root / '.git/refs/heads/main').write_text(oid + '\n', encoding='ascii')
    (root / 'data.txt').write_bytes(b'changed-content\n')
    probe = root / 'filter_probe.py'
    probe.write_text('import pathlib,sys\npathlib.Path(sys.argv[1]).write_text("executed")\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n', encoding='utf-8')
    marker = root / 'owned_filter_marker'
    command = '"' + sys.executable.replace('\\', '/') + '" "' + str(probe).replace('\\', '/') + '" "' + str(marker).replace('\\', '/') + '"'
    return marker, command


def configure_filter(root, command):
    git(root, 'config', 'filter.ownedprobe.clean', command)
    git(root, 'config', 'filter.ownedprobe.required', 'true')


def current_answer(root, arguments):
    if arguments[0] == '--current-controller':
        return 'injected-source-control\t' + str(root) + '\t' + str(root) + '\t' + '1' * 32
    return RECEIPT


def documents(root):
    (root / 'STATE.md').write_bytes(b'state-source\n')
    (root / 'ROADMAP.md').write_bytes(b'roadmap-source\n')
    (root / 'tasks').mkdir()


class SecurityControls(unittest.TestCase):
    def setUp(self):
        WG._native_static_owner_module_v1()  # Positive source-pin gate before every negative.

    def test_01_actual_filter_execution_RED_then_native_Git_GREEN(self):
        with disposable('git-filter-') as root:
            marker, command = git_fixture(root)
            configure_filter(root, command)
            # Operative unsafe-command positive control, not a replay of native
            # currentness or an import of the historical private donor stack.
            git(root, 'diff', '--binary', 'HEAD')
            self.assertTrue(marker.is_file())
            BASELINE.append({'control': 'local-filter-execution', 'positive_control': 'DIRECT_GIT_EXECUTED_OWNED_MARKER'})
            marker.unlink()
            with patch.object(WG, '_native_claim_call_v1', side_effect=lambda owner, route, repo, args, a, b: current_answer(root, args)):
                value = WG._native_continuity(root, root)
            self.assertFalse(marker.exists())
            self.assertEqual(value['receipt'], RECEIPT)

    def test_02_actual_config_race_stays_in_fixed_read_view(self):
        with disposable('git-race-') as root:
            marker, command = git_fixture(root)
            owner, _, _ = WG._native_static_owner_module_v1()
            original_view = owner._git_read_view
            @contextlib.contextmanager
            def raced_view(repository):
                with original_view(repository) as view:
                    configure_filter(root, command)
                    yield view
            with patch.object(owner, '_git_read_view', raced_view):
                result = owner._run_git(root, 'diff', '--no-ext-diff', '--no-textconv', '--binary', 'HEAD', text=False)
            self.assertEqual(result.returncode, 0)
            self.assertFalse(marker.exists())
            git(root, 'diff', '--binary', 'HEAD')
            self.assertTrue(marker.exists(), 'race operand must be execution-capable in the unsafe path')
            BASELINE.append({'control': 'post-view-config-race', 'baseline': 'UNSAFE_DIRECT_GIT_EXECUTED_OWNED_MARKER', 'green': 'FIXED_VIEW_NO_MARKER'})

    def test_03_shell_environment_inert_helper_control(self):
        if BASH is None:
            self.skipTest('bash is unavailable on this platform')
        with disposable('shell-env-') as root:
            owner, _, _ = WG._native_static_owner_module_v1()
            route, _, _ = WG._native_route_scope_module_v1()
            marker = root / 'bash_env_executed'
            startup = root / 'startup.sh'
            startup.write_text('printf unsafe > "' + str(marker).replace('\\', '/') + '"\n', encoding='utf-8')
            environment = dict(os.environ, BASH_ENV=str(startup).replace('\\', '/'))
            subprocess.run([str(BASH), '-c', 'printf inert'], env=environment, capture_output=True, check=True)
            self.assertTrue(marker.exists())
            marker.unlink()
            with patch.dict(os.environ, {'BASH_ENV': str(startup), 'ENV': str(startup), 'PYTHONPATH': str(root),
                                         'GIT_EXTERNAL_DIFF': 'must-not-execute', 'IMPLEMENTAUDIT_BASE': 'foreign'}):
                value = WG._native_claim_call_v1(owner, route, root, ['--current-controller'],
                    b"printf 'inert-private-helper-control\\n'\n", b'exit 0\n')
            self.assertEqual(value, 'inert-private-helper-control')
            self.assertFalse(marker.exists())
            BASELINE.append({'control': 'BASH_ENV', 'baseline': 'EXECUTED_OWNED_MARKER', 'green': 'STRICT_CHILD_ENV_NO_MARKER', 'native_helper_execution': False})

    def test_04_source_file_and_cumulative_real_bounds(self):
        with disposable('source-bytes-') as root:
            documents(root)
            (root / 'STATE.md').write_bytes(b'x' * (WG.NATIVE_SOURCE_MAX_FILE_BYTES + 1))
            self.assertEqual(len((root / 'STATE.md').read_bytes()), WG.NATIVE_SOURCE_MAX_FILE_BYTES + 1)
            with self.assertRaises(WG.WorkGraphError):
                WG._native_source_snapshot(root)
            BASELINE.append({'control': 'source-file-byte-bound', 'operand': 'UNBOUNDED_OWNED_READ_CONFIRMED', 'bytes': WG.NATIVE_SOURCE_MAX_FILE_BYTES + 1})
            (root / 'STATE.md').write_bytes(b'state')
            for i in range(17):
                (root / 'tasks' / f'{i:02}.md').write_bytes(b'x' * WG.NATIVE_SOURCE_MAX_FILE_BYTES)
            self.assertGreater(sum(p.stat().st_size for p in root.rglob('*.md')), WG.NATIVE_SOURCE_MAX_TOTAL_BYTES)
            with self.assertRaises(WG.WorkGraphError):
                WG._native_source_snapshot(root)
            BASELINE.append({'control': 'source-cumulative-byte-bound', 'operand': 'ACTUAL_SOURCE_TOTAL_EXCEEDS_4_MIB'})

    def test_05_actual_ignored_entry_population_is_bounded(self):
        with disposable('source-count-') as root:
            documents(root)
            for i in range(WG.NATIVE_SOURCE_MAX_ENTRIES):
                (root / 'tasks' / f'{i:04}.dat').touch()
            self.assertEqual(len(list((root / 'tasks').iterdir())), WG.NATIVE_SOURCE_MAX_ENTRIES)
            with self.assertRaises(WG.WorkGraphError):
                WG._native_source_snapshot(root)
            BASELINE.append({'control': 'ignored-entry-population', 'operand': 'ACTUAL_IGNORED_ENTRY_COUNT_CONFIRMED'})

    def test_06_hardlink_and_junction_before_content(self):
        with disposable('source-alias-') as root:
            docs = root / 'documents'
            docs.mkdir()
            documents(docs)
            target = root / 'owned_target.md'
            target.write_bytes(b'owned alias target\n')
            (docs / 'STATE.md').unlink()
            os.link(target, docs / 'STATE.md')
            self.assertEqual((docs / 'STATE.md').read_bytes(), target.read_bytes())
            self.assertGreater((docs / 'STATE.md').stat().st_nlink, 1)
            with self.assertRaises(WG.WorkGraphError):
                WG._native_source_snapshot(docs)
            BASELINE.append({'control': 'hardlink-alias', 'operand': 'ACTUAL_HARDLINK_CONTENT_READABLE'})
            (docs / 'STATE.md').unlink()
            (docs / 'STATE.md').write_bytes(b'state')
            outside = root / 'owned-outside'
            outside.mkdir()
            (outside / 'outside.md').write_bytes(b'owned junction target\n')
            link = docs / 'plans'
            if os.name == 'nt':
                subprocess.run([(os.environ.get('COMSPEC') or shutil.which('cmd.exe') or 'cmd.exe'), '/d', '/c',
                    'mklink', '/J', str(link), str(outside)], capture_output=True, check=True)
            else:
                link.symlink_to(outside, target_is_directory=True)
            try:
                with self.assertRaises(WG.WorkGraphError):
                    WG._native_source_snapshot(docs)
                BASELINE.append({'control': 'directory-reparse-alias', 'green': 'REFUSED_WITH_ACTUAL_ALIAS'})
            finally:
                os.rmdir(link) if os.name == 'nt' else link.unlink()

    def test_07_input_format_compatibility_and_alias_boundaries(self):
        with disposable('input-reads-') as root:
            (root / 'data').mkdir()
            (root / 'data/nested').mkdir()
            (root / 'data/one.txt').write_bytes(b'one')
            (root / 'data/nested/two.txt').write_bytes(b'two')
            nodes = [{'reads': ['path:data', 'path:absent.txt'], 'invalidators': []}]
            self.assertEqual(expected_small_read_set(root), WG._acquire_native_read_set(nodes, root))
            os.link(root / 'data/one.txt', root / 'alias.txt')
            with self.assertRaises(WG.WorkGraphError):
                WG._acquire_native_read_set(nodes, root)
            BASELINE.append({'control': 'input-hardlink', 'green': 'REFUSED_WITH_ACTUAL_ALIAS'})

    def test_08_declared_input_count_and_real_file_byte_bound(self):
        with disposable('input-bounds-') as root:
            nodes = [{'reads': ['path:missing-' + str(i) for i in range(WG.NATIVE_READ_MAX_ENTRIES + 1)], 'invalidators': []}]
            self.assertEqual(len(nodes[0]['reads']), WG.NATIVE_READ_MAX_ENTRIES + 1)
            self.assertEqual(WG._acquire_native_read_set([{'reads': [], 'invalidators': []}], root), {})
            with self.assertRaises(WG.WorkGraphError):
                WG._acquire_native_read_set(nodes, root)
            target = root / 'too-large.bin'
            with target.open('wb') as stream:
                stream.truncate(WG.NATIVE_READ_MAX_FILE_BYTES + 1)
            with self.assertRaises(WG.WorkGraphError):
                WG._acquire_native_read_set([{'reads': ['path:too-large.bin'], 'invalidators': []}], root)
            BASELINE.append({'control': 'input-count-and-byte-bounds', 'operand': '4097_DECLARED_INPUTS_WITH_EMPTY_READ_POSITIVE', 'green': 'REFUSED_REAL_16_MIB_PLUS_ONE_FILE'})

    def test_09_changed_tracked_content_still_invalidates_without_full_diff(self):
        with disposable('tracked-change-') as root:
            marker, command = git_fixture(root)
            configure_filter(root, command)
            with patch.object(WG, '_native_claim_call_v1', side_effect=lambda owner, route, repo, args, a, b: current_answer(root, args)):
                first = WG._native_continuity(root, root)
                (root / 'data.txt').write_bytes(b'different-content\n')
                second = WG._native_continuity(root, root)
                repeated = WG._native_continuity(root, root)
            self.assertNotEqual(first['worktree_digest'], second['worktree_digest'])
            self.assertEqual(second, repeated)
            self.assertFalse(marker.exists())


@unittest.skipUnless(os.name == 'nt', 'Windows handle-directory query control')
class HandleQueryControls(unittest.TestCase):
    def test_multiple_pages_unicode_names_and_population_bound(self):
        graph = WG
        owner, _, _ = graph._native_static_owner_module_v1()
        with disposable('directory-query-pages-') as root:
            expected = [f'file-{i:04}-long-name-Ω.txt' for i in range(600)]
            for name in expected:
                (root / name).write_bytes(b'owned small file\n')
            kernel = owner._snapshot_windows_kernel_v1()
            real_query = kernel.GetFileInformationByHandleEx
            real_query.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
            real_query.restype = ctypes.c_int
            classes = []
            def observed_query(*args):
                classes.append(args[1])
                return real_query(*args)
            kernel.GetFileInformationByHandleEx = observed_query
            with patch.object(owner, '_snapshot_windows_kernel_v1', return_value=kernel), \
                 patch.object(graph.os, 'scandir', side_effect=AssertionError('Windows pathname enumeration is forbidden')):
                rows, mode = graph._native_static_directory_v1(owner, root, dict(entries=0, maximum_entries=601))
            self.assertEqual([name for name, directory, mode in rows], expected)
            self.assertTrue(all(not directory and mode == 0o666 for name, directory, mode in rows))
            self.assertEqual(mode, 0o777)
            self.assertEqual(classes[0], 0xB)
            self.assertTrue(all(value == 0xA for value in classes[1:]))
            self.assertGreaterEqual(len(classes), 3)
            with self.assertRaises(graph.WorkGraphError):
                graph._native_static_directory_v1(owner, root, dict(entries=0, maximum_entries=599))
            self.query_calls = len(classes)


@contextlib.contextmanager
def directory_race_fixture():
    root = Path(tempfile.mkdtemp(prefix='held-directory-race-', dir=WORK)).absolute()
    empty = root / 'empty'
    peer = root / 'peer'
    empty.mkdir()
    peer.mkdir()
    (peer / 'out-of-scope-name.txt').write_bytes(b'owned peer fixture\n')
    try:
        yield root, empty, peer
    finally:
        if empty.exists() and empty.lstat().st_file_attributes & 0x400:
            os.rmdir(empty)
        root.resolve(strict=True).relative_to(WORK.resolve(strict=True))
        shutil.rmtree(root)


def junction_while_held(kernel, empty, peer):
    """Metadata-only access succeeds despite a separately held read handle."""
    kernel.DeviceIoControl.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
        ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p]
    kernel.DeviceIoControl.restype = ctypes.c_int
    handle = kernel.CreateFileW(str(empty), 0x100, 7, None, 3, 0x02200000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    substitute = ('\\??\\' + str(peer)).encode('utf-16-le')
    display = str(peer).encode('utf-16-le')
    names = substitute + b'\0\0' + display + b'\0\0'
    raw = struct.pack('<IHHHHHH', 0xA0000003, 8 + len(names), 0,
                      0, len(substitute), len(substitute) + 2, len(display)) + names
    buffer = ctypes.create_string_buffer(raw)
    count = ctypes.c_uint32()
    try:
        if not kernel.DeviceIoControl(handle, 0x000900A4, buffer, len(raw), None, 0, ctypes.byref(count), None):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        kernel.CloseHandle(handle)
    if not empty.lstat().st_file_attributes & 0x400:
        raise AssertionError('junction mutation did not occur')


@unittest.skipUnless(os.name == 'nt', 'Windows metadata-only junction race control')
class DirectoryRaceControl(unittest.TestCase):
    def test_held_empty_parent_never_enumerates_peer(self):
        owner, _, _ = WG._native_static_owner_module_v1()
        real_query = WG._native_windows_directory_rows_v1
        for unsafe_positive in (True, False):
            observed = []
            with directory_race_fixture() as (root, empty, peer):
                def raced_query(current_owner, kernel, handle, requested, budget):
                    junction_while_held(kernel, empty, peer)
                    if unsafe_positive:
                        # Operative reference of the old pathname mechanism,
                        # not an import or execution of a private native owner.
                        with os.scandir(empty) as entries:
                            rows = [(entry.name, False, 0o666) for entry in entries]
                    else:
                        rows = real_query(current_owner, kernel, handle, requested, budget)
                    observed.extend(name for name, directory, mode in rows)
                    return rows
                with patch.object(WG, '_native_windows_directory_rows_v1', raced_query):
                    if unsafe_positive:
                        with self.assertRaises(WG.WorkGraphError):
                            WG._native_static_directory_v1(owner, empty, dict(entries=0, maximum_entries=8))
                    else:
                        with patch.object(WG.os, 'scandir', side_effect=AssertionError('Windows pathname enumeration is forbidden')), self.assertRaises(WG.WorkGraphError):
                            WG._native_static_directory_v1(owner, empty, dict(entries=0, maximum_entries=8))
                self.assertEqual(observed, ['out-of-scope-name.txt'] if unsafe_positive else [])
                self.assertEqual((peer / 'out-of-scope-name.txt').read_bytes(), b'owned peer fixture\n')


SOURCE_MEMBERS = {
    'scripts/operational-evidence.py': 'scripts/operational-evidence.py',
    'scripts/operational_query_policy.py': 'scripts/operational_query_policy.py',
    **{f'skills/implementaudit/scripts/{name}': f'source-peers/route-graph/skills/implementaudit/scripts/{name}'
       for name in ('route-transaction.py', 'route_request_policy.py', 'compile-work-graph.py')},
    **{f'skills/implementaudit/scripts/{name}': f'skills/implementaudit/scripts/{name}'
       for name in ('claim-run.sh', 'validate-run-root.sh')},
}


def assemble_test_source(repo, canonical):
    """Seven exact source members; helper operations remain injected/inert."""
    hashes = {}
    for target_relative, source_relative in SOURCE_MEMBERS.items():
        source = repo / source_relative
        before = source.lstat()
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or source.is_symlink()
                or source.resolve(strict=True) != source or before.st_size > 2 * 1024 * 1024
                or getattr(before, 'st_file_attributes', 0) & 0x400):
            raise ValueError('source member custody/size refused: ' + source_relative)
        raw = source.read_bytes()
        after = source.lstat()
        identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if identity(before) != identity(after) or len(raw) != before.st_size:
            raise ValueError('source member changed during copy: ' + source_relative)
        target = canonical / target_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        if target.read_bytes() != raw:
            raise ValueError('temporary source copy differs: ' + source_relative)
        hashes[source_relative] = hashlib.sha256(raw).hexdigest()
    return hashes


def suite_tests(name):
    loader = unittest.defaultTestLoader
    if name == 'route':
        return list(loader.loadTestsFromTestCase(Controls))
    if name == 'security':
        return list(loader.loadTestsFromTestCase(SecurityControls))
    if name == 'directory':
        return ([SecurityControls(method) for method in (
            'test_04_source_file_and_cumulative_real_bounds',
            'test_05_actual_ignored_entry_population_is_bounded',
            'test_06_hardlink_and_junction_before_content',
            'test_07_input_format_compatibility_and_alias_boundaries',
            'test_08_declared_input_count_and_real_file_byte_bound')]
        + [Controls('test_13_no_override_public_path_acquires_and_rechecks'),
           HandleQueryControls('test_multiple_pages_unicode_names_and_population_bound')])
    return list(loader.loadTestsFromTestCase(DirectoryRaceControl))


def main():
    global WORK, RT, WG, GIT, BASH
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--suite', choices=('route', 'security', 'directory', 'directory-race'), required=True)
    parser.add_argument('--case', action='append', default=[], help='Exact existing method name; repeat to run a focused subset')
    parser.add_argument('--list', action='store_true', help='List the selected population without source/native acquisition')
    args = parser.parse_args()
    available = suite_tests(args.suite)
    names = {test._testMethodName for test in available}
    if set(args.case) - names:
        parser.error('unknown case in the selected suite')
    selected = [test for test in available if not args.case or test._testMethodName in args.case]
    if args.list:
        print(json.dumps({'suite': args.suite, 'suite_population': len(available),
                          'selected': [test._testMethodName for test in selected]}))
        return 0
    repo = args.repo_root.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix='native-peer-controls-') as temporary:
        WORK = Path(temporary).absolute()
        canonical = WORK / 'canonical'
        hashes = assemble_test_source(repo, canonical)
        scripts = canonical / 'skills/implementaudit/scripts'
        RT = load(scripts / 'route-transaction.py', '_portable_r0033_owner')
        WG = load(scripts / 'compile-work-graph.py', '_portable_r0035_owner')
        route_sha = hashes['source-peers/route-graph/skills/implementaudit/scripts/route-transaction.py']
        needs_static = args.suite != 'route' or any(test._testMethodName == 'test_13_no_override_public_path_acquires_and_rechecks' for test in selected)
        preconditions = {
            'route_source_pin_matches': WG._NATIVE_ROUTE_PRODUCER_SHA256 == route_sha,
            'static_source_pin_matches': WG._NATIVE_STATIC_OWNER_SHA256 == hashes['scripts/operational-evidence.py'],
        }
        if not preconditions['route_source_pin_matches'] or needs_static and not preconditions['static_source_pin_matches']:
            print(json.dumps({'status': 'PRECONDITION_SOURCE_PIN_MISMATCH', 'scope': 'SOURCE_INTERFACE_ONLY',
                              'native_admission': 'NOT_ESTABLISHED', 'preconditions': preconditions, 'sources': hashes}))
            return 2
        GIT = shutil.which('git')
        # Match the native owner's shell, including Git Bash on Windows. The
        # System32 WSL launcher does not consume Windows BASH_ENV paths.
        BASH = RT.trusted_host_executable(WORK, 'bash')
        if args.suite == 'security' and GIT is None:
            raise RuntimeError('Git executable required for the selected security controls')
        stream = io.StringIO()
        with patch.dict(os.environ, {'TEMP': str(WORK), 'TMP': str(WORK), 'TMPDIR': str(WORK)}), \
             patch.object(tempfile, 'tempdir', str(WORK)):
            result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.TestSuite(selected))
        sys.stderr.write(stream.getvalue())
        print(json.dumps({'suite': args.suite, 'suite_population': len(available), 'tests_run': result.testsRun,
            'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
            'skip_reasons': [reason for test, reason in result.skipped], 'passed': result.wasSuccessful(),
            'scope': 'SOURCE_INTERFACE_AND_OWNED_STATIC_SECURITY_FIXTURES_WITH_INJECTED_CURRENTNESS',
            'native_admission': 'NOT_ESTABLISHED', 'canonical_claim_operations': 0,
            'preconditions': preconditions, 'sources': hashes, 'operative_controls': BASELINE}))
        return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
