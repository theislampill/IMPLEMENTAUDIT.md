SOURCE_FILES = 1761
SOURCE_BYTES = 166514973
"""Actual private native receiving for the exact 8ee4 Linux delta.

No process is launched here. The immutable host supplies actual fresh checks;
this receiver reconsumes every referenced result, command stream and body.
"""
from pathlib import Path
import re
import types

E = _HOST_EVIDENCE_IO
SOURCE_COMMIT = '19c222a2db624de15b77415481f34f3d7a4475a7'
SOURCE_TREE = '714407ef4284174786340c087624f92ef19967c0'
PROFILE = 'DG16_8EE4_LINUX_CHANGED_NATIVE_BINDING_V1'
TESTS = ('test_native_intake_uses_current_original14_not_retired_root',
         'test_native_intake_later_boundary_prevents_return')
PREDICATES = ('fixed_receiver_identity', 'wrong_receiver_refusal', 'current_native_intake',
              'later_invalidation_refusal', 'host_and_diagnosed_intake')
COMPILER = 'skills/implementaudit/scripts/compile-work-graph.py'
RECEIVER = 'scripts/operational-evidence.py'
COMPILER_SHA = '0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d'
RECEIVER_SHA = '5950164adb0e0e1d9c6ff4481ccb43cbff94a13ae1fb6578fb6a172a431e69ed'
PROBE_SHA256 = '04b7ff2a8f6ccf64fb1cb3d469759cf9f42bd5f8a7dfa5296bbf8bf4f348c4f9'
SUPPORT = ('HOST.json', 'SOURCE_CLOSURE.json', 'ADMISSION.json', 'PLACEMENT.json',
           'SOURCE_APPLICABILITY.json', 'CAPTURE.json', 'BEFORE_CURRENTNESS.json', 'AFTER_CURRENTNESS.json')
Refusal = E.Refusal
need = E.need


def descriptor(raw):
    return dict(bytes=len(raw), sha256=E.sha(raw))


def native_invocation(probe_path, source, output):
    """Execute captured exact program bytes, not a later interpreter path read."""
    path = Path(probe_path)
    raw = E.read_packet(path, 128 * 1024)
    need(E.sha(raw) == PROBE_SHA256, 'NATIVE_PROBE_PROGRAM_PIN')
    code = '__file__=' + repr(str(path)) + '\n' + raw.decode('utf-8', 'strict')
    return ['/usr/bin/python3.12', '-I', '-S', '-B', '-c', code,
            '--source', str(source), '--output', str(output)]


def check_capture(root, row, *, returncode=0, argv=None):
    need(type(row) is dict and row.get('process_started') is True and row.get('returncode') == returncode
         and row.get('pidfd_acquired') is True and row.get('streams_complete') is True
         and row.get('stream_digest_scope') == 'CAPTURED_BYTES_ONLY'
         and row.get('timeout') is False and row.get('output_bound_exceeded') is False
         and row.get('internal_failure') is None and row.get('cleanup', {}).get('echild') is True,
         'NATIVE_CAPTURE_CUSTODY_OR_OUTCOME')
    if argv is not None:
        need(row.get('argv') == argv, 'NATIVE_CAPTURE_COMMAND_CHANGED')
    bodies = {}
    for name in ('stdout', 'stderr'):
        relative = E.safe_name(row.get(name + '_private', ''))
        raw = E.read(root / relative, 32768)
        need(len(raw) == row.get(name + '_bytes') and E.sha(raw) == row.get(name + '_sha256'),
             'NATIVE_CAPTURE_STREAM_CHANGED')
        bodies[name] = raw
    return bodies


def projection_reader(source):
    path = source / COMPILER
    raw = E.read(path)
    need(len(raw) == 262144 and E.sha(raw) == COMPILER_SHA, 'NATIVE_PURE_RECEIVER_SOURCE')
    module = types.ModuleType('native_prerequisite_pure_projection_reader')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    need(E.read(path) == raw, 'NATIVE_PURE_RECEIVER_CLOSING')
    return module


def check_case_bodies(root, result, compiler):
    need(result.get('schema') == 'dg16.focused-native-actual-result.v1' and result.get('authority') == 'NONE'
         and result.get('source_commit') == SOURCE_COMMIT and result.get('source_tree') == SOURCE_TREE
         and result.get('test_population') == list(TESTS) and result.get('tests_run') == 2
         and result.get('success') is True and result.get('original_awards') == [], 'FOCUSED_NATIVE_RESULT_REFUSED')
    members = result.get('members')
    held = E.bind_bodies(root, members, maximum=4 * 1024**2)
    actual = E.census(root, file_bytes=4 * 1024**2, total_bytes=64 * 1024**2, entries=4096)
    need(set(actual['files']) == set(members) | {'RESULT.json'}, 'NATIVE_BODY_POPULATION_CHANGED')
    for name in ('SOURCE_OPEN.json', 'SOURCE_CLOSE.json', 'FIXED_RECEIVER.json', 'WRONG_RECEIVER.json'):
        need(name in members, 'NATIVE_REQUIRED_BODY_MISSING')
    before = E.parse(E.read(root / 'SOURCE_OPEN.json'))
    after = E.parse(E.read(root / 'SOURCE_CLOSE.json'))
    need(before == after and result.get('source_unchanged') is True, 'NATIVE_SOURCE_CLOSURE_REFUSED')
    need(before[COMPILER]['bytes'] == 262144 and before[COMPILER]['sha256'] == COMPILER_SHA
         and before[RECEIVER]['bytes'] == 422801 and before[RECEIVER]['sha256'] == RECEIVER_SHA,
         'NATIVE_ACTUAL_SOURCE_PINS')
    fixed_raw = E.read(root / 'FIXED_RECEIVER.json')
    fixed = E.parse(fixed_raw)
    need(fixed.get('schema') == 'dg16.actual-fixed-receiver.v1'
         and fixed.get('compiler') == before[COMPILER] and fixed.get('receiver') == before[RECEIVER]
         and fixed.get('closing') == before and fixed.get('physical_loader_returned') is True
         and fixed.get('actual_body_sha256') == RECEIVER_SHA, 'FIXED_RECEIVER_BODY_REFUSED')
    wrong_raw = E.read(root / 'WRONG_RECEIVER.json')
    wrong = E.parse(wrong_raw)
    wrong_compiler = E.read(root / 'wrong-source' / COMPILER)
    wrong_receiver = E.read(root / 'wrong-source' / RECEIVER)
    need(wrong.get('schema') == 'dg16.actual-wrong-receiver.v1' and E.sha(wrong_compiler) == COMPILER_SHA
         and wrong.get('compiler_sha256') == COMPILER_SHA and wrong.get('expected_receiver_sha256') == RECEIVER_SHA
         and wrong.get('wrong_receiver_sha256') == E.sha(wrong_receiver) != RECEIVER_SHA
         and wrong.get('wrong_receiver_bytes') == len(wrong_receiver) == 422801
         and wrong.get('actual_refusal') == dict(type='WorkGraphError',
            message='native static source owner is unavailable or changed', cause='OSError')
         and wrong.get('product_source_edited') is False, 'WRONG_RECEIVER_BODY_REFUSED')
    rows = result.get('rows')
    need(type(rows) is list and [r.get('test') for r in rows] == list(TESTS), 'NATIVE_CASE_POPULATION')
    for row in rows:
        need(row.get('outcome') == 'PASS' and row.get('tests_run') == 1, 'NATIVE_CASE_FAILED_OR_SKIPPED')
        runner = E.read(root / E.safe_name(row['runner']))
        need(len(runner) == row.get('diagnostic_bytes') and E.sha(runner) == row.get('diagnostic_sha256')
             and b'\nOK\n' in runner, 'NATIVE_CASE_RUNNER_BODY')
        need(type(row.get('commands')) is list and row['commands'] and len(row['commands']) <= 512,
             'NATIVE_CASE_COMMAND_POPULATION')
        for name in row['commands']:
            need(name in members, 'NATIVE_COMMAND_BODY_MISSING')
            command = E.parse(E.read(root / name))
            need(type(command.get('argv')) is list and type(command.get('returncode')) is int,
                 'NATIVE_CASE_COMMAND_BODY')
            for stream in ('stdout', 'stderr'):
                need(command.get(stream) in members, 'NATIVE_CASE_STREAM_MISSING')
                need(E.sha(E.read(root / command[stream])) == command.get(stream + '_sha256'),
                     'NATIVE_CASE_STREAM_CHANGED')
    positive, later = rows
    need(positive.get('native_graphs'), 'ACTUAL_CURRENT_NATIVE_GRAPH_REQUIRED')
    graphs = [E.parse(E.read(root / E.safe_name(name))) for name in positive['native_graphs']]
    need(any(g.get('campaign') == 'portable-fixture'
             and g.get('binding', {}).get('acquisition') == 'NATIVE_CONTINUITY_VERIFIED' for g in graphs),
         'CURRENT_ORIGINAL14_NOT_ACTUALLY_RECEIVED')
    for graph in graphs:
        frontier = compiler.select_native_frontier_v1(graph)
        need(frontier.get('selected') == ['PREP', 'SIB']
             and 'ROUTE_PRODUCER_UNAVAILABLE' in frontier['blocked']['ADMIT'],
             'ACTUAL_CURRENT_GRAPH_SEMANTICS_REFUSED')
    invalidations = []
    for name in later['commands']:
        command = E.parse(E.read(root / name))
        if '--invalidate-continuity' in command['argv']:
            need(command['returncode'] == 0, 'LATER_INVALIDATION_DID_NOT_SUCCEED')
            invalidations.append(name)
    closes = []
    for name in later.get('native_observations', []):
        close = E.parse(E.read(root / E.safe_name(name)))
        if close.get('status') == 'REFUSED' and close.get('exception_type') == 'WorkGraphError':
            need(close.get('opened') in members, 'LATER_NATIVE_OPEN_BODY_MISSING')
            opened = E.parse(E.read(root / close['opened']))
            need(opened.get('binding', {}).get('acquisition') == 'NATIVE_CONTINUITY_VERIFIED', 'LATER_NATIVE_OPEN_SCOPE')
            compiler.select_native_frontier_v1(opened)
            order = lambda p: int(Path(p).name.split('-', 1)[0])
            need(any(order(close['opened']) < order(cmd) < order(name) for cmd in invalidations),
                 'INVALIDATION_NOT_BETWEEN_OPEN_AND_CLOSE')
            closes.append(name)
    need(closes, 'ACTUAL_LATER_INVALIDATION_REFUSAL_REQUIRED')
    need(E.bind_bodies(root, members, maximum=4 * 1024**2) == held, 'NATIVE_RAW_CLOSING_CHANGED')
    return dict(fixed_receiver_identity=E.sha(fixed_raw), wrong_receiver_refusal=E.sha(wrong_raw),
                current_native_intake=E.sha(E.encode(positive)), later_invalidation_refusal=E.sha(E.encode(later)))


def source_applicability(source, value):
    need(value.get('schema') == 'dg16.current-native-source-applicability.v1'
         and value.get('source_commit') == SOURCE_COMMIT and value.get('source_tree') == SOURCE_TREE
         and value.get('unchanged_count') == 86 and value.get('changed_count') == 3
         and value.get('compiler_normalized_ast_sha256') == 'd655e32697528bd808de557a8b8b3e665d321784fdbbe01eb2964790c7255d86'
         and value.get('receiver_non_windows_ast_sha256') == '699eb2680c1a97ebda8f68f0e2ef6fae0a19e027fdd768e5057c0c9ecfcaca52',
         'NATIVE_APPLICABILITY_SCOPE_REFUSED')
    rows = value.get('members')
    need(type(rows) is list and len(rows) == 89 and len({r['path'] for r in rows}) == 89, 'NATIVE_APPLICABILITY_POPULATION')
    observed = {}
    for row in rows:
        name = E.safe_name(row['path'])
        actual = E.file_record(source / name, 128 * 1024**2)
        need(actual['bytes'] == row['current']['bytes'] and actual['sha256'] == row['current']['sha256']
             and actual['mode'] == (0o755 if row['current']['mode'] == '100755' else 0o644),
             'NATIVE_CURRENT_SOURCE_BODY_CHANGED')
        equal = row['current'] == row['retained']
        need(equal == row['retained_unchanged'] and (equal or name in (COMPILER, RECEIVER, 'fixtures/canonical-state-rotation/owned_stdio_source_boundaries_test.py')),
             'NATIVE_UNCHANGED_APPLICABILITY_FALSE')
        if name == 'fixtures/canonical-state-rotation/owned_stdio_source_boundaries_test.py':
            need(row['current']['bytes'] == 33227 and row['current']['sha256'] == '528f1e693d0745b90a8ea2ededd570962f929e8f2c76b115c6e011386a03e0f7'
                 and row['retained']['sha256'] == 'e166953fae131a4aa0e35d4a0ca694ae9bcc918ef7e5e66e21d230ab3bbeb6cf'
                 and row['retained_unchanged'] is False, 'NATIVE_FIXTURE_REPAIR_SCOPE')
        observed[name] = actual
    return observed


def receive(private, source, context, check_live, *, current=True, create=False):
    """Receive actual evidence. G0002 checks do not rename consumed G0001 facts.

    check_live is wired solely by immutable run.py. It performs actual owner,
    full source, host, placement and canonical checks, not a saved digest.
    """
    need(type(current) is bool and callable(check_live), 'ACTUAL_NATIVE_LIVE_CHECK_REQUIRED')
    private = Path(private)
    native = private / 'native-prerequisite'
    before_live = check_live(current)
    need(before_live['controller'] == context['controller'] and before_live['source_commit'] == SOURCE_COMMIT
         and before_live['source_tree'] == SOURCE_TREE, 'NATIVE_LIVE_SUBJECT_MISMATCH')
    support_raw = {name: E.read(native / name) for name in SUPPORT}
    support = {name: E.parse(raw) for name, raw in support_raw.items()}
    host = support['HOST.json']
    need(before_live['host'] == host and host.get('uid') == host.get('euid') == host.get('gid') == host.get('egid') == 0
         and host.get('os') == {'ID': 'ubuntu', 'VERSION_ID': '24.04'}
         and host.get('python_version') == [3, 12, 3], 'NATIVE_FRESH_HOST_DIFFERS')
    closure = support['SOURCE_CLOSURE.json']
    need(closure == before_live['source_closure'] and closure.get('all_members_match') is True
         and closure.get('file_count') == SOURCE_FILES and closure.get('total_bytes') == SOURCE_BYTES,
         'NATIVE_FULL_SOURCE_CLOSURE_DIFFERS')
    applicability = source_applicability(source, support['SOURCE_APPLICABILITY.json'])
    admission = support['ADMISSION.json']
    need(admission == before_live['admission'] and admission.get('source_commit') == SOURCE_COMMIT
         and admission.get('source_tree') == SOURCE_TREE and admission.get('original_awards') == [],
         'NATIVE_ACTUAL_ADMISSION_CHANGED')
    need(support['PLACEMENT.json'] == before_live['placement'], 'NATIVE_QUALIFIED_PLACEMENT_CHANGED')
    initial_receipt = context['initial_receipt']
    need(re.fullmatch('refs/implementaudit/continuity-receipts/' + re.escape(context['controller'])
                      + r'/G0001@[0-9a-f]{40}', initial_receipt), 'NATIVE_INITIAL_RECEIPT_SCOPE')
    for name in ('BEFORE_CURRENTNESS.json', 'AFTER_CURRENTNESS.json'):
        streams = check_capture(private, support[name], argv=['/usr/bin/bash', str(source / 'skills/implementaudit/scripts/claim-run.sh'),
                                  '--require-current-continuity', context['controller']])
        need(streams['stdout'].decode('ascii').strip() == initial_receipt and not streams['stderr'],
             'NATIVE_ACTUAL_CURRENTNESS_BODY_REFUSED')
    if current:
        need(before_live['receipt'] == initial_receipt, 'NATIVE_CURRENT_RECEIPT_MISMATCH')
    else:
        need(before_live.get('scope') == 'RETAINED_CONSUMED_G0001_WITH_ACTUAL_CURRENT_G0002'
             and before_live['receipt'] != initial_receipt, 'NATIVE_CONSUMED_SCOPE_NOT_ESTABLISHED')
        need(E.read(private / 'g3/inputs/NATIVE_PREREQUISITE_RECEIVING.json', 8192)
             == E.read(private / 'NATIVE_PREREQUISITE_RECEIVING.json', 8192), 'NATIVE_CONSUMED_RECEIPT_CHANGED')
    streams = check_capture(private, support['CAPTURE.json'],
        argv=native_invocation(context['probe_path'], source, private / 'native-run'))
    need(not streams['stderr'], 'NATIVE_PARENT_STDERR_UNQUALIFIED')
    parent = E.parse(streams['stdout'])
    result_raw = E.read(private / 'native-run/RESULT.json')
    need(parent == dict(schema='dg16.focused-native-parent-return.v1', result_bytes=len(result_raw),
        result_sha256=E.sha(result_raw), success=True, tests_run=2, source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE),
        'NATIVE_ACTUAL_PARENT_RETURN_DIFFERS')
    result = E.parse(result_raw)
    predicates = check_case_bodies(private / 'native-run', result, projection_reader(source))
    fixed = E.parse(E.read(private / 'native-run/FIXED_RECEIVER.json'))
    need(fixed['actual_path'] == str(source / RECEIVER), 'NATIVE_RECEIVER_PHYSICAL_PATH_CHANGED')
    for name in (COMPILER, RECEIVER):
        need(fixed['closing'][name] == E.file_record(source / name, 4 * 1024**2), 'NATIVE_RECEIVER_CLOSING_IDENTITY_CHANGED')
    predicates['host_and_diagnosed_intake'] = E.sha(E.encode(dict(host=E.sha(support_raw['HOST.json']),
        placement=E.sha(support_raw['PLACEMENT.json']), admission=E.sha(support_raw['ADMISSION.json']),
        actual_positive=predicates['current_native_intake'])))
    need(tuple(predicates) == PREDICATES, 'NATIVE_PREDICATE_POPULATION')
    raw_custody = E.census(private / 'native-run', file_bytes=4 * 1024**2, total_bytes=64 * 1024**2, entries=4096)
    supporting_custody = {name: E.file_record(native / name, 4 * 1024**2) for name in SUPPORT}
    command_custody = {}
    for key in ('CAPTURE.json', 'BEFORE_CURRENTNESS.json', 'AFTER_CURRENTNESS.json'):
        for stream in ('stdout', 'stderr'):
            name = support[key][stream + '_private']
            command_custody[name] = E.file_record(private / name, 32768)
    custody = dict(raw=raw_custody, support=supporting_custody, commands=command_custody, source=applicability)
    actual = dict(schema='dg16.actual-native-five-predicate-receiving.v1', authority='NONE',
        source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE, controller=context['controller'],
        receipt_sha256=E.sha(initial_receipt.encode()), raw_result_sha256=E.sha(result_raw),
        supporting_bodies={name: descriptor(raw) for name, raw in support_raw.items()},
        predicates=predicates, custody_sha256=E.sha(E.encode(custody)), original_awards=[],
        native_case_scope='TWO_ACTUAL_CONSTRUCTED_ORIGINAL14_CONTROLS_NOT_ORIGINAL_CAMPAIGN',
        unchanged_controls='86_SOURCE_MEMBERS_TWO_OWNER_DELTAS_AND_ONE_EXACT_FIXTURE_REPAIR')
    record = dict(schema='dg16.g3-current-native-prerequisite.v1', authority='NONE', profile=PROFILE,
        source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE, controller=context['controller'],
        receipt_sha256=E.sha(initial_receipt.encode()), host_facts_sha256=E.sha(support_raw['HOST.json']),
        admission_sha256=E.sha(support_raw['ADMISSION.json']), source_applicability_sha256=E.sha(support_raw['SOURCE_APPLICABILITY.json']),
        source_closure_sha256=E.sha(support_raw['SOURCE_CLOSURE.json']), actual_receiving_sha256=E.sha(E.encode(actual)),
        predicates={name: dict(disposition='ACTUAL_RECEIVED_AT_DECLARED_PREDICATE', evidence_sha256=digest)
                    for name, digest in predicates.items()}, unchanged_controls='RETAINED_AT_EXACT_APPLICABILITY',
        same_checkout_current=True, original_awards=[], status='CURRENT_NATIVE_PREREQUISITES_RECEIVED')
    after_live = check_live(current)
    need(after_live == before_live and source_applicability(source, support['SOURCE_APPLICABILITY.json']) == applicability,
         'NATIVE_LIVE_CLOSING_CHANGED')
    need(E.census(private / 'native-run', file_bytes=4 * 1024**2, total_bytes=64 * 1024**2, entries=4096) == raw_custody
         and all(E.read(native / name) == raw for name, raw in support_raw.items()), 'NATIVE_CLOSING_CUSTODY_CHANGED')
    if create:
        need(current, 'NATIVE_RECEIPT_CREATE_ONLY_CURRENT')
        E.write_once(native / 'CUSTODY.json', E.encode(custody), 16 * 1024**2)
        E.write_once(native / 'ACTUAL_RECEIVING.json', E.encode(actual))
        E.write_once(private / 'NATIVE_PREREQUISITE_RECEIVING.json', E.encode(record), 8192)
    else:
        need(E.read(native / 'CUSTODY.json', 16 * 1024**2) == E.encode(custody)
             and E.read(native / 'ACTUAL_RECEIVING.json') == E.encode(actual)
             and E.read(private / 'NATIVE_PREREQUISITE_RECEIVING.json', 8192) == E.encode(record),
             'NATIVE_RETAINED_EVIDENCE_OR_RECEIVING_CHANGED')
    return E.sha(E.encode(record))
