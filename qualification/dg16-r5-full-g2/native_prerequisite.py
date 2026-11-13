SOURCE_FILES = 1766
SOURCE_BYTES = 167022772
"""Actual ordinary-G2 current-only native receiving; no launch API.

The immutable run adapter supplies actual fresh currentness and physical checks.
Retained-body reconsumption has no live-currentness authority of its own.
"""
from pathlib import Path
import re
import types

E = _HOST_EVIDENCE_IO
P = _G2_NATIVE_PROFILE
A = _G2_NATIVE_ADMISSION
SOURCE_COMMIT = 'e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'
SOURCE_TREE = 'ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7'
PROFILE = P.PROFILE
TESTS = A.TESTS
PREDICATES = A.PREDICATES
COMPILER = 'skills/implementaudit/scripts/compile-work-graph.py'
RECEIVER = 'scripts/operational-evidence.py'
COMPILER_SHA = '0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d'
RECEIVER_SHA = '5950164adb0e0e1d9c6ff4481ccb43cbff94a13ae1fb6578fb6a172a431e69ed'
APPLICABILITY_SHA = '600618dcd0aedb67cb2cbfc1f51ab9d67fb0d64047d066455f0443e5edc18909'
PROBE_SHA256 = 'aed50e967ffe3e876ed59d5f3fe4873be45965ff14441832baf9a70408b188c4'
SUPPORT = ('HOST.json', 'SOURCE_CLOSURE.json', 'SOURCE_CUSTODY.json', 'ADMISSION.json',
           'SOURCE_APPLICABILITY.json', 'CAPTURE.json', 'BEFORE_CURRENTNESS.json', 'AFTER_CURRENTNESS.json',
           *A.FILES)
Refusal = E.Refusal
need = E.need


def descriptor(raw):
    return dict(bytes=len(raw), sha256=E.sha(raw))


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


def native_invocation(probe_path, source, output, python_path):
    """Capture the exact reviewed probe bytes under the actual checked Python."""
    need(python_path == P.PYTHON, 'G2_NATIVE_SYSTEM_INTERPRETER_REQUIRED')
    path = Path(probe_path)
    raw = E.read_packet(path, 128 * 1024)
    need(E.sha(raw) == PROBE_SHA256, 'NATIVE_PROBE_PROGRAM_PIN')
    code = '__file__=' + repr(str(path)) + '\n' + raw.decode('utf-8', 'strict')
    return [python_path, '-I', '-S', '-B', '-c', code, '--source', str(source), '--output', str(output)]


def observe_result(root):
    """Read complete private result bytes, including failed maintained cases."""
    raw = E.read(root / 'RESULT.json', 4 * 1024**2)
    value = E.parse(raw)
    keys = {'schema', 'authority', 'source_commit', 'source_tree', 'test_population', 'tests_run',
            'success', 'rows', 'members', 'fixed_receiver', 'wrong_receiver', 'before', 'after',
            'source_unchanged', 'recording_scope', 'original_awards'}
    need(type(value) is dict and set(value) == keys and value['schema'] == 'dg16.focused-native-actual-result.v1'
         and value['authority'] == 'NONE' and value['source_commit'] == SOURCE_COMMIT and value['source_tree'] == SOURCE_TREE
         and value['test_population'] == list(TESTS) and type(value['tests_run']) is int and 1 <= value['tests_run'] <= 2
         and type(value['success']) is bool and value['original_awards'] == [] and value['source_unchanged'] is True
         and value['fixed_receiver'] == 'FIXED_RECEIVER.json' and value['wrong_receiver'] == 'WRONG_RECEIVER.json'
         and value['before'] == 'SOURCE_OPEN.json' and value['after'] == 'SOURCE_CLOSE.json'
         and value['recording_scope'] == 'ACTUAL_MAINTAINED_CASE_COMMAND_STREAMS_AND_NATIVE_RETURN_OR_CLOSE',
         'G2_NATIVE_RESULT_SHAPE')
    held = E.bind_bodies(root, value['members'], maximum=4 * 1024**2)
    census = E.census(root, file_bytes=4 * 1024**2, total_bytes=64 * 1024**2, entries=4096)
    need(set(census['files']) == set(held) | {'RESULT.json'}, 'NATIVE_BODY_POPULATION_CHANGED')
    rows = value['rows']
    need(type(rows) is list and len(rows) == value['tests_run']
         and [r.get('test') for r in rows] == list(TESTS[:len(rows)]), 'G2_NATIVE_OBSERVED_CASE_POPULATION')
    public_rows = []
    row_keys = {'test', 'outcome', 'tests_run', 'runner', 'commands', 'native_graphs', 'native_observations',
                'diagnostic_bytes', 'diagnostic_sha256'}
    for row in rows:
        need(type(row) is dict and set(row) == row_keys and row['outcome'] in ('PASS', 'FAIL')
             and type(row['tests_run']) is int and 0 <= row['tests_run'] <= 1, 'G2_NATIVE_OBSERVED_CASE_SHAPE')
        name = E.safe_name(row['runner'])
        need(name in held, 'G2_NATIVE_RUNNER_MISSING')
        body = E.read(root / name)
        need(len(body) == row['diagnostic_bytes'] and E.sha(body) == row['diagnostic_sha256'], 'NATIVE_CASE_RUNNER_BODY')
        for field in ('commands', 'native_graphs', 'native_observations'):
            need(type(row[field]) is list and len(row[field]) <= 2048
                 and len(set(row[field])) == len(row[field]) and all(E.safe_name(n) in held for n in row[field]),
                 'G2_NATIVE_CASE_MEMBER_LINK')
        for name in row['commands']:
            command = E.parse(E.read(root / name))
            need(type(command.get('argv')) is list and type(command.get('returncode')) is int,
                 'NATIVE_CASE_COMMAND_BODY')
            for stream in ('stdout', 'stderr'):
                need(E.safe_name(command[stream]) in held
                     and E.sha(E.read(root / command[stream])) == command[stream + '_sha256'],
                     'NATIVE_CASE_STREAM_CHANGED')
        public_rows.append({key: row[key] for key in ('test', 'outcome', 'tests_run', 'diagnostic_bytes', 'diagnostic_sha256')})
    need(value['success'] == (len(rows) == 2 and all(r['outcome'] == 'PASS' and r['tests_run'] == 1 for r in rows)),
         'G2_NATIVE_SUCCESS_FLAG')
    need(E.bind_bodies(root, value['members'], maximum=4 * 1024**2) == held, 'NATIVE_RAW_CLOSING_CHANGED')
    projection = dict(schema='dg16.g2-current-native-observed-result.v1', authority='NONE',
        source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE, profile=PROFILE,
        test_population=list(TESTS), tests_run=value['tests_run'], success=value['success'], rows=public_rows,
        raw_result=descriptor(raw), native_operations_proven_by_summary=False, original_awards=[])
    return value, raw, projection


def context_scope(context):
    keys = {'controller', 'initial_receipt', 'probe_path', 'python_path', 'bash_path',
            'admission_bindings', 'historical_profile', 'source_closure', 'source_custody', 'runtime_sha256'}
    need(type(context) is dict and set(context) == keys and type(context['controller']) is str
         and re.fullmatch('[a-z0-9][a-z0-9-]{0,127}', context['controller']), 'G2_NATIVE_CONTEXT_SHAPE')
    need(type(context['initial_receipt']) is str and re.fullmatch('refs/implementaudit/continuity-receipts/'
         + re.escape(context['controller']) + r'/G0001@[0-9a-f]{40}', context['initial_receipt']),
         'NATIVE_INITIAL_RECEIPT_SCOPE')
    need(context['python_path'] == P.PYTHON and type(context['bash_path']) is str
         and context['bash_path'].startswith('/usr/'), 'G2_NATIVE_CONTEXT_TOOL_PATH')


def require_full_source_closure(closure, expected):
    need(closure == expected and closure.get('all_members_match') is True
         and closure.get('file_count') == SOURCE_FILES and closure.get('total_bytes') == SOURCE_BYTES,
         'NATIVE_FULL_SOURCE_CLOSURE_DIFFERS')


def build_receiving(private, source, context):
    """Pure actual-body reconsumption; no live authority is inferred here."""
    context_scope(context)
    private, source = Path(private), Path(source)
    native, raw_root = private / 'native-prerequisite', private / 'native-run'
    support_raw = {name: E.read(native / name) for name in SUPPORT}
    support = {name: E.parse(raw) for name, raw in support_raw.items()}
    host = support['HOST.json']
    P.validate_host(host)
    need(all(P.compare_historical(host, context['historical_profile']).values()),
         'G2_NATIVE_CHANGED_HOST_APPLICABILITY_UNRECEIVED')
    need(host['tools']['bash']['canonical'] == context['bash_path']
         and host['tools']['python3']['canonical'] == context['python_path'], 'G2_NATIVE_CAPTURE_TOOL_BINDING')
    closure = support['SOURCE_CLOSURE.json']
    require_full_source_closure(closure, context['source_closure'])
    need(support['SOURCE_CUSTODY.json'] == context['source_custody'], 'G2_NATIVE_SOURCE_CUSTODY_CHANGED')
    need(E.sha(support_raw['SOURCE_APPLICABILITY.json']) == APPLICABILITY_SHA, 'G2_NATIVE_APPLICABILITY_BODY_PIN')
    applicability = source_applicability(source, support['SOURCE_APPLICABILITY.json'])
    admission = A.validate({name: support_raw[name] for name in A.FILES}, context['admission_bindings'], context['historical_profile'])
    need(support['ADMISSION.json'] == admission, 'NATIVE_ACTUAL_ADMISSION_CHANGED')
    for name in ('BEFORE_CURRENTNESS.json', 'AFTER_CURRENTNESS.json'):
        streams = check_capture(private, support[name], argv=[context['bash_path'],
            str(source / 'skills/implementaudit/scripts/claim-run.sh'), '--require-current-continuity', context['controller']])
        need(streams['stdout'].decode('ascii').strip() == context['initial_receipt'] and not streams['stderr'],
             'NATIVE_ACTUAL_CURRENTNESS_BODY_REFUSED')
    result, result_raw, observed = observe_result(raw_root)
    streams = check_capture(private, support['CAPTURE.json'], returncode=0 if result['success'] else 1,
        argv=native_invocation(context['probe_path'], source, raw_root, context['python_path']))
    need(not streams['stderr'], 'NATIVE_PARENT_STDERR_UNQUALIFIED')
    parent = E.parse(streams['stdout'])
    need(parent == dict(schema='dg16.focused-native-parent-return.v1', result_bytes=len(result_raw),
         result_sha256=E.sha(result_raw), success=result['success'], tests_run=result['tests_run'],
         source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE), 'NATIVE_ACTUAL_PARENT_RETURN_DIFFERS')
    process_open = E.parse(E.read(raw_root / 'HOST_OPEN.json'))
    process_close = E.parse(E.read(raw_root / 'HOST_CLOSE.json'))
    need(process_open == process_close, 'G2_NATIVE_PROCESS_CLOSING_CHANGED')
    P.validate_process(process_open, host)
    source_open = E.parse(E.read(raw_root / 'SOURCE_OPEN.json'))
    source_close = E.parse(E.read(raw_root / 'SOURCE_CLOSE.json'))
    need(source_open == source_close, 'NATIVE_SOURCE_CLOSURE_REFUSED')
    for name, row in source_open.items():
        need(E.file_record(source / E.safe_name(name), 4 * 1024**2) == row, 'NATIVE_RECEIVER_CLOSING_IDENTITY_CHANGED')
    predicates = {}
    if result['success']:
        predicates = check_case_bodies(raw_root, result, projection_reader(source))
        fixed = E.parse(E.read(raw_root / 'FIXED_RECEIVER.json'))
        need(fixed['actual_path'] == str(source / RECEIVER), 'NATIVE_RECEIVER_PHYSICAL_PATH_CHANGED')
        predicates['ordinary_host_source_currentness_custody'] = E.sha(E.encode(dict(
            host=E.sha(support_raw['HOST.json']), process=E.sha(E.encode(process_open)),
            source_custody=E.sha(support_raw['SOURCE_CUSTODY.json']), admission=E.sha(support_raw['ADMISSION.json']),
            actual_positive=predicates['current_native_intake'])))
        need(tuple(predicates) == PREDICATES, 'NATIVE_PREDICATE_POPULATION')
    raw_custody = E.census(raw_root, file_bytes=4 * 1024**2, total_bytes=64 * 1024**2, entries=4096)
    support_custody = {name: E.file_record(native / name, 4 * 1024**2) for name in SUPPORT}
    command_custody = {}
    for name in ('CAPTURE.json', 'BEFORE_CURRENTNESS.json', 'AFTER_CURRENTNESS.json'):
        for stream in ('stdout', 'stderr'):
            relative = E.safe_name(support[name][stream + '_private'])
            command_custody[relative] = E.file_record(private / relative, 32768)
    custody = dict(raw=raw_custody, support=support_custody, commands=command_custody, source=applicability)
    actual = dict(schema='dg16.g2-actual-current-native-body-receiving.v1', authority='NONE',
        source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE, profile=PROFILE,
        controller=context['controller'], receipt_sha256=E.sha(context['initial_receipt'].encode()),
        raw_result=descriptor(result_raw), supporting_bodies={name: descriptor(raw) for name, raw in support_raw.items()},
        predicates=predicates, all_five_predicates_received=result['success'],
        custody_sha256=E.sha(E.encode(custody)), observed_result=observed, original_awards=[],
        native_case_scope='TWO_CONSTRUCTED_ORIGINAL14_CONTROLS_NOT_ORIGINAL_CAMPAIGN',
        unchanged_controls='86_SOURCE_MEMBERS_TWO_REVIEWED_LINUX_OWNER_DELTAS_AND_ONE_EXACT_FIXTURE_REPAIR')
    record = dict(schema='dg16.g2-current-only-native-receiving.v1', authority='NONE', profile=PROFILE,
        source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE, controller=context['controller'],
        receipt_sha256=E.sha(context['initial_receipt'].encode()), host_facts_sha256=E.sha(support_raw['HOST.json']),
        admission_sha256=E.sha(support_raw['ADMISSION.json']), source_applicability_sha256=APPLICABILITY_SHA,
        source_closure_sha256=E.sha(support_raw['SOURCE_CLOSURE.json']), runtime_sha256=context['runtime_sha256'],
        actual_receiving_sha256=E.sha(E.encode(actual)), raw_result=descriptor(result_raw),
        predicates={name: dict(disposition='ACTUAL_RECEIVED_AT_DECLARED_PREDICATE', evidence_sha256=digest)
                    for name, digest in predicates.items()}, tests_run=result['tests_run'],
        same_checkout_current_at_receiving=True, live_currentness_transferred=False, historical_receipt_transfer=False,
        eligible_for_full_pair=result['success'], original_awards=[],
        status='RECEIVED_CURRENT_CHANGED_NATIVE_PREDICATES' if result['success'] else 'RECEIVED_FAILED_CURRENT_NATIVE_EVIDENCE')
    need(source_applicability(source, support['SOURCE_APPLICABILITY.json']) == applicability
         and E.census(raw_root, file_bytes=4 * 1024**2, total_bytes=64 * 1024**2, entries=4096) == raw_custody
         and all(E.read(native / name) == raw for name, raw in support_raw.items()), 'NATIVE_CLOSING_CUSTODY_CHANGED')
    return dict(custody=custody, actual=actual, record=record, observed=observed,
                view=dict(controller=context['controller'], source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE,
                    receipt=context['initial_receipt'], host=host, source_closure=closure,
                    source_custody=support['SOURCE_CUSTODY.json'], admission=admission,
                    runtime_sha256=context['runtime_sha256'], scope='CURRENT_G0001_ORDINARY_G2'))


def retained_readback(private, built):
    private = Path(private)
    need(E.read(private / 'native-prerequisite/CUSTODY.json', 16 * 1024**2) == E.encode(built['custody'])
         and E.read(private / 'native-prerequisite/ACTUAL_RECEIVING.json') == E.encode(built['actual'])
         and E.read(private / 'NATIVE_PREREQUISITE_RECEIVING.json', 16384) == E.encode(built['record']),
         'NATIVE_RETAINED_EVIDENCE_OR_RECEIVING_CHANGED')


def reconsume(private, source, context):
    """Reconsume retained bodies only; cannot grant present currentness."""
    built = build_receiving(private, source, context)
    retained_readback(private, built)
    return built['record']


def receive(private, source, context, check_live, *, create=False):
    """Two fresh actual checks supplied only by the immutable host adapter."""
    need(callable(check_live) and type(create) is bool, 'ACTUAL_NATIVE_LIVE_CHECK_REQUIRED')
    before = check_live()
    built = build_receiving(private, source, context)
    need(before == built['view'], 'G2_NATIVE_LIVE_SUBJECT_OR_CUSTODY_MISMATCH')
    after = check_live()
    need(after == before, 'NATIVE_LIVE_CLOSING_CHANGED')
    # The live owner call itself is inside the receiving interval. Reconsume
    # complete bodies after it before creating or accepting any receipt.
    need(build_receiving(private, source, context) == built, 'NATIVE_CLOSING_CUSTODY_CHANGED')
    if create:
        private = Path(private)
        E.write_once(private / 'native-prerequisite/CUSTODY.json', E.encode(built['custody']), 16 * 1024**2)
        E.write_once(private / 'native-prerequisite/ACTUAL_RECEIVING.json', E.encode(built['actual']))
        E.write_once(private / 'NATIVE_PREREQUISITE_RECEIVING.json', E.encode(built['record']), 16384)
    retained_readback(private, built)
    return built['record']
