#!/usr/bin/env python3
"""New F02 controls; import fixture definitions only, never prior test groups.

Run: python -I -S -B THIS_FILE COLD_SOURCE NEW_OWNED_SCRATCH
Real owner CLI parsing and custody writes operate only on synthetic local files.
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import traceback
from unittest import mock

SOURCE, SCRATCH = (Path(value).resolve() for value in sys.argv[1:3])
assert not SCRATCH.exists(), 'Scratch must be new'
spec = importlib.util.spec_from_file_location('persistent_refusal_fixture', SOURCE / 'tests/compaction-hold-fixture.py')
fx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fx)
obs, owner = fx.obs, fx.owner
CALL_ID = 'heldout-reused-occurrence-id'
CLI, DETAILS = [], {}


def invoke(fixture, label, action, request):
    argv = ['compaction-audit-pending.py', '--store', str(fixture.store),
            '--session', fixture.session, '--owner-id', fixture.owner, action]
    stdin, stdout = io.TextIOWrapper(io.BytesIO(fx.canonical(request))), io.StringIO()
    with mock.patch.object(sys, 'argv', argv), mock.patch.object(sys, 'stdin', stdin), contextlib.redirect_stdout(stdout):
        code = owner.main()
    raw = stdout.getvalue()
    reply = json.loads(raw)
    CLI.append({'case': fixture.root.name, 'label': label, 'argv': argv, 'stdin': request,
                'exit_code': code, 'stdout': raw})
    return code, reply


def compact(result):
    code, reply = result
    return {'exit_code': code, 'reason': reply.get('reason'), 'status': reply.get('status')}


def latches(fixture):
    assignment = fixture.state()['assignments'][fixture.child]
    return {key: copy.deepcopy(assignment.get(key, {})) for key in ('hold_failures', 'hold_refusals')}


def replace_frame(fixture, locator, payload):
    path = fixture.logs['child']
    raw = path.read_bytes()
    old = raw[locator['offset']:locator['offset'] + locator['bytes']]
    row = json.loads(old)
    row['payload'] = payload
    wire = fx.canonical(row)
    assert len(wire) < locator['bytes'], (len(wire), locator['bytes'])
    wire += b' ' * (locator['bytes'] - len(wire) - 1) + b'\n'
    path.write_bytes(raw[:locator['offset']] + wire + raw[locator['offset'] + locator['bytes']:])
    return {'locator': locator, 'before_sha256': hashlib.sha256(old).hexdigest(),
            'replacement_sha256': hashlib.sha256(wire).hexdigest()}


def neutral():
    return {'type': 'message', 'id': 'neutral', 'role': 'assistant', 'phase': 'commentary',
            'content': [{'type': 'output_text', 'text': 'Neutral gap'}]}


def initial(name, inherited_marker=False):
    fixture = fx.Fixture(name, inherited=22)
    path = fixture.logs['child']
    rows = [json.loads(wire) for wire in path.read_bytes().splitlines()]
    for ordinal in (1, 11, 22):
        rows[ordinal]['payload'] = {'type': 'custom_tool_call_output', 'call_id': CALL_ID, 'output': []}
    if inherited_marker:
        rows[10]['payload'] = {**neutral(), 'padding': 'x' * 800}
    path.write_bytes(b''.join(fx.canonical(row) + b'\n' for row in rows))
    fixture.reserved = fixture.reserve()
    deliver = {'child_id': fixture.child, 'phase': 'deliver',
               'observation_id': fixture.reserved['obligation']['observation_id'],
               'authorization_evidence': fixture.authorize(fixture.reserved)}
    code, packet = invoke(fixture, 'deliver', 'observe-child', deliver)
    assert code == 0, packet
    delivery = fixture.exchange(obs.delivery_tool_input(fixture.store, fixture.session, fixture.owner, deliver), json.dumps(packet))
    bind = {'child_id': fixture.child, 'phase': 'bind', 'observation_id': deliver['observation_id'], 'exchange': delivery}
    if inherited_marker:
        assignment = fixture.state()['assignments'][fixture.child]
        prepared = assignment['prepared'][deliver['observation_id']]
        exchange = obs.completed_exchange(assignment['observation_source'], prepared, delivery,
                                          fixture.store, fixture.session, fixture.owner, owner.selected_audit_state_pin())
        wires = path.read_bytes().splitlines(keepends=True)
        locator = {'offset': sum(map(len, wires[:10])), 'bytes': len(wires[10])}
        replace_frame(fixture, locator, {'type': 'custom_tool_call', 'name': 'exec', 'call_id': CALL_ID,
            'input': '// COMPACTION_OBSERVATION_EXCHANGE=' + exchange['identity'] + '\ntext("Inherited only");'})
    call = fixture.row('child', 'response_item', {'type': 'custom_tool_call', 'name': 'exec', 'call_id': CALL_ID,
        'status': 'completed', 'input': obs.delivery_tool_input(fixture.store, fixture.session, fixture.owner, bind)})
    code, fixture.observed = invoke(fixture, 'initial-bind', 'observe-child', bind)
    assert code == 0, fixture.observed
    return fixture, bind, {'call': call, 'call_id': CALL_ID}


def entry(fixture):
    return copy.deepcopy(fixture.state()['assignments'][fixture.child]['prepared'][fixture.observed['observation_id']]['hold_prefix'])


def marked(fixture, identifier=CALL_ID):
    return {'type': 'custom_tool_call', 'name': 'exec', 'status': 'completed', 'call_id': identifier,
            'input': '// COMPACTION_OBSERVATION_EXCHANGE=' + fixture.observed['child_observation_exchange_identity'] +
                     '\ntext("Observed substantive early attempt");'}


def persistent_case(name, kind):
    # Break caught: first-error masking or loss of a witnessed refusal on retry.
    fixture, bind, pending = initial(name)
    immutable_entry = entry(fixture)
    if kind == 'unknown_before_marker':
        bad = fixture.row('child', 'response_item', {'type': 'ambiguous_material_event', 'padding': 'x' * 800})
        later = fixture.row('child', 'response_item', marked(fixture, 'distinct-later-attempt'))
    else:
        payload = marked(fixture, 'distinct-early-attempt' if kind == 'distinct' else CALL_ID)
        if kind == 'duplicate_without_marker':
            payload['input'] = '// COMPACTION_OBSERVATION_EXCHANGE=' + 'f' * 64 + '\ntext("Foreign episode");'
        elif kind == 'invalid_exec_marker':
            payload['name'] = 'other-tool'
        elif kind == 'unpaired_output':
            payload = {'type': 'custom_tool_call_output', 'call_id': ['invalid-id'], 'output': [], 'padding': 'x' * 600}
        bad = fixture.row('child', 'response_item', payload)
        later = None
    fixture.bound = fixture.end_exchange(pending, json.dumps(fixture.observed))
    first = invoke(fixture, 'observe-material-event', 'observe-child', bind)
    witnessed = latches(fixture)
    prefix_raw = fixture.logs['child'].read_bytes()[:immutable_entry['prefix_bytes']]
    replacements = [replace_frame(fixture, bad, neutral())]
    if later is not None:
        replacements.append(replace_frame(fixture, later, neutral()))
    retry = invoke(fixture, 'retry-after-neutral-replacement', 'observe-child', bind)
    again = invoke(fixture, 'exact-retry-after-refusal', 'observe-child', bind)
    request = fixture.result_request()
    returned = invoke(fixture, 'return-after-later-use', 'return', request)
    join = None
    if returned[0] == 0:
        join = invoke(fixture, 'join-after-bypassed-refusal', 'join', fixture.accept(returned[1]))
    detail = {'first': compact(first), 'retry': compact(retry), 'exact_retry': compact(again),
              'return': compact(returned), 'join_if_returned': compact(join) if join else None,
              'witnessed_latches': witnessed, 'replacements': replacements,
              'entry_unchanged': entry(fixture) == immutable_entry and
                  fixture.logs['child'].read_bytes()[:immutable_entry['prefix_bytes']] == prefix_raw}
    DETAILS[name] = detail
    early = kind in ('distinct', 'reused')
    first_reason = 'HOLD_EARLY_SAME_EPISODE_USE' if early else (
        'HOLD_UNCLASSIFIED_EVENT' if kind == 'unknown_before_marker' else
        'HOLD_UNPAIRED_TOOL_OUTPUT' if kind == 'unpaired_output' else 'HOLD_UNCLASSIFIED_TOOL_CALL')
    latched_reason = 'HOLD_EPISODE_PREVIOUSLY_DISQUALIFIED' if early else 'HOLD_EPISODE_PREVIOUSLY_REFUSED'
    assert first[0] == 2 and first[1].get('reason') == first_reason, detail
    for outcome in (retry, again, returned):
        assert outcome[0] == 2 and outcome[1].get('reason') == latched_reason, detail
    chosen, other = ('hold_failures', 'hold_refusals') if early else ('hold_refusals', 'hold_failures')
    assert witnessed[chosen] and not witnessed[other], detail
    refusal = witnessed[chosen][fixture.observed['observation_id']]
    assert refusal['reason'] == first_reason and refusal['authority'] == 'NONE', refusal
    evidence = refusal['evidence']
    assert evidence['record'] == bad and evidence['prefix']['path'] == str(fixture.logs['child']), evidence
    assert evidence['prefix']['prefix_bytes'] > immutable_entry['prefix_bytes'], evidence
    assert evidence['prefix']['physical'] == immutable_entry['physical'], evidence
    assert detail['entry_unchanged'] and latches(fixture) == witnessed, detail


def finish(fixture, bind):
    before = fixture.statebytes()
    immutable_entry = entry(fixture)
    for index in range(2):
        code, reply = invoke(fixture, 'stable-retry-' + str(index), 'observe-child', bind)
        assert code == 0 and reply == fixture.observed, reply
        assert fixture.statebytes() == before
    request = fixture.result_request()
    request['result_evidence']['bound_exchange'] = copy.deepcopy(fixture.bound)
    for locator in request['result_evidence']['bound_exchange'].values():
        locator['physical_line'] = None
    code, result = invoke(fixture, 'return', 'return', request)
    assert code == 0, result
    held = result['identity']['hold_history']
    assert held['prefix_bytes'] == fixture.bound['result']['offset'] + fixture.bound['result']['bytes'], held
    assert held['physical_records'] == fixture.bound['result']['physical_line'], held
    assert held['original_bind']['call']['locator'] == fixture.bound['call'], held
    assert held['original_bind']['result']['locator'] == fixture.bound['result'], held
    code, joined = invoke(fixture, 'logical-join', 'join', fixture.accept(result))
    assert code == 0 and joined['status'] == 'VERIFIED_LOGICAL_JOIN_PENDING_PROFILE', joined
    assert joined['pending_consumed'] is False and joined['host_producer_authenticated'] is False, joined
    assert joined['authority'] == 'NONE' and joined['canonical_currentness'] is False, joined
    assert entry(fixture) == immutable_entry and not any(latches(fixture).values())
    return {'original_end': held['prefix_bytes'], 'physical_records': held['physical_records'],
            'entry_unchanged': True, 'pending_consumed': False, 'host_producer_authenticated': False}


def join_retention(name, early):
    # Break caught: JOIN can forget its own witnessed gap refusal after restoration.
    fixture, bind, pending = initial(name)
    gap = fixture.row('child', 'response_item', {**neutral(), 'padding': 'x' * 1024})
    fixture.bound = fixture.end_exchange(pending, json.dumps(fixture.observed))
    original_wire = fixture.logs['child'].read_bytes()[gap['offset']:gap['offset'] + gap['bytes']]
    code, returned = invoke(fixture, 'valid-return-before-gap-change', 'return', fixture.result_request())
    assert code == 0, returned
    acceptance = fixture.accept(returned)
    payload = marked(fixture) if early else {'type': 'ambiguous_material_event'}
    replace_frame(fixture, gap, payload)
    first = invoke(fixture, 'join-observes-invalid-gap', 'join', acceptance)
    witnessed = latches(fixture)
    with fixture.logs['child'].open('r+b') as stream:
        stream.seek(gap['offset'])
        stream.write(original_wire)
    next_try = invoke(fixture, 'join-after-neutral-replacement', 'join', acceptance)
    DETAILS[name] = {'first': compact(first), 'next': compact(next_try), 'latches': witnessed}
    assert first[0] == 2 and first[1].get('reason') == (
        'HOLD_EARLY_SAME_EPISODE_USE' if early else 'HOLD_UNCLASSIFIED_EVENT'), DETAILS[name]
    assert next_try[0] == 2 and next_try[1].get('reason') == (
        'HOLD_EPISODE_PREVIOUSLY_DISQUALIFIED' if early else 'HOLD_EPISODE_PREVIOUSLY_REFUSED'), DETAILS[name]
    assert fixture.state()['assignments'][fixture.child]['join'] is None


def negatives():
    # Break caught: textual, inherited or foreign markers acquire a false early latch.
    fixture, bind, pending = initial('marker-negatives', inherited_marker=True)
    marker = marked(fixture)['input']
    fixture.message('child', 'Quoted input: ' + marker)
    fixture.message('child', marker)
    fixture.exchange('// COMPACTION_OBSERVATION_EXCHANGE=' + 'f' * 64 + '\ntext("Foreign episode");', marker)
    fixture.bound = fixture.end_exchange(pending, json.dumps(fixture.observed))
    DETAILS['marker-negatives'] = finish(fixture, bind)


def response_size(name, size):
    # Break caught: off-by-one physical frame bound or a moved original cutoff.
    fixture, bind, pending = initial(name)
    fixture.bound = fixture.end_exchange(pending, json.dumps(fixture.observed))
    locator = fixture.bound['result']
    path = fixture.logs['child']
    raw = path.read_bytes()
    row = json.loads(raw[locator['offset']:])
    nested = json.loads(row['payload']['output'][1]['text'])
    nested['output'] += ' ' * (size - locator['bytes'])
    row['payload']['output'][1]['text'] = json.dumps(nested)
    wire = fx.canonical(row) + b'\n'
    assert len(wire) == size
    path.write_bytes(raw[:locator['offset']] + wire)
    locator.update(bytes=len(wire), sha256=hashlib.sha256(wire).hexdigest())
    if size == 262144:
        fixture.row('child', 'response_item', {'type': 'custom_tool_call_output', 'call_id': CALL_ID, 'output': []})
        DETAILS[name] = {'frame_bytes': size, **finish(fixture, bind)}
    else:
        before = fixture.statebytes()
        result = invoke(fixture, 'overflow-refusal', 'observe-child', bind)
        DETAILS[name] = compact(result)
        assert result[0] == 2 and result[1].get('reason') == 'HOLD_PARTIAL_OR_OVERFLOW_FRAME', result
        assert fixture.statebytes() == before and not any(latches(fixture).values())


def incomplete(name, mode):
    # Break caught: incomplete or raced acquisition is converted into permanent evidence.
    fixture, bind, pending = initial(name)
    path = fixture.logs['child']
    base = path.read_bytes()
    if mode == 'partial':
        fixture.row('child', 'response_item', marked(fixture))
        path.write_bytes(path.read_bytes()[:-1])
    elif mode == 'missing_completion':
        pass
    elif mode == 'unsettled_foreign':
        fixture.begin_exchange('// COMPACTION_OBSERVATION_EXCHANGE=' + 'f' * 64 + '\ntext("Foreign episode");')
    elif mode == 'race':
        fixture.row('child', 'response_item', marked(fixture))
        fixture.bound = fixture.end_exchange(pending, json.dumps(fixture.observed))
    before = fixture.statebytes()
    if mode == 'race':
        physical, calls = obs.physical, [0]
        def racing_read(candidate):
            value = physical(candidate)
            if sys._getframe(1).f_code.co_name == 'hold_records' and str(candidate) == str(path):
                calls[0] += 1
                if calls[0] == 2:
                    info = path.stat()
                    os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns + 10000000))
                    value = physical(candidate)
            return value
        with mock.patch.object(obs, 'physical', racing_read):
            result = invoke(fixture, 'real-mtime-race', 'observe-child', bind)
        expected = 'HOLD_SOURCE_CHANGED_DURING_READ'
    else:
        result = invoke(fixture, 'incomplete-evidence', 'observe-child', bind)
        expected = ('HOLD_PARTIAL_OR_OVERFLOW_FRAME' if mode == 'partial' else
                    'HOLD_UNSETTLED_TOOL_CALL' if mode == 'unsettled_foreign' else 'HOLD_ORIGINAL_BIND_COMPLETION_UNPROVED')
    DETAILS[name] = compact(result)
    assert result[0] == 2 and result[1].get('reason') == expected, result
    assert fixture.statebytes() == before and not any(latches(fixture).values())
    path.write_bytes(base)
    fixture.line['child'] = len(base.splitlines())
    fixture.ordinal['child'] = json.loads(base.splitlines()[-1])['ordinal'] + 1
    fixture.bound = fixture.end_exchange(pending, json.dumps(fixture.observed))
    code, reply = invoke(fixture, 'complete-evidence-can-retry', 'observe-child', bind)
    assert code == 0 and reply == fixture.observed, reply


def record_count(name, count):
    # Break caught: count overflow becomes an early latch, or inherited bytes are omitted.
    fixture, bind, pending = initial(name)
    while fixture.line['child'] < count - 1:
        fixture.message('child', 'Physical coverage control')
    fixture.bound = fixture.end_exchange(pending, json.dumps(fixture.observed))
    before = fixture.statebytes()
    code, reply = invoke(fixture, 'record-count-boundary', 'observe-child', bind)
    DETAILS[name] = {'physical_records': count, 'exit_code': code, 'reason': reply.get('reason')}
    if count == 64:
        assert code == 0 and reply == fixture.observed, reply
    else:
        assert code == 2 and reply.get('reason') == 'HOLD_RECORD_COUNT_BOUND', reply
    assert fixture.statebytes() == before and not any(latches(fixture).values())


def total_bytes(name, total):
    # Break caught: reading beyond MAX_TOTAL or counting selected rather than physical bytes.
    fixture, bind, pending = initial(name)
    gaps = []
    for index in range(8):
        gaps.append(fixture.row('child', 'response_item', {**neutral(), 'padding': 'x' * 1000}))
    fixture.bound = fixture.end_exchange(pending, json.dumps(fixture.observed))
    path = fixture.logs['child']
    raw = path.read_bytes()
    output = raw[fixture.bound['result']['offset']:]
    remaining = total - gaps[0]['offset'] - len(output)
    padded = []
    for index, gap in enumerate(gaps):
        wire = raw[gap['offset']:gap['offset'] + gap['bytes']]
        size = min(262144, remaining - (len(gaps) - index - 1) * len(wire))
        assert len(wire) <= size <= 262144
        padded.append(wire[:-1] + b' ' * (size - len(wire)) + b'\n')
        remaining -= size
    assert remaining == 0
    child = raw[:gaps[0]['offset']] + b''.join(padded) + output
    assert len(child) == total
    path.write_bytes(child)
    fixture.bound['result']['offset'] = total - len(output)
    before = fixture.statebytes()
    code, reply = invoke(fixture, 'total-byte-boundary', 'observe-child', bind)
    DETAILS[name] = {'physical_bytes': total, 'exit_code': code, 'reason': reply.get('reason')}
    if total == 2097152:
        assert code == 0 and reply == fixture.observed, reply
    else:
        assert code == 2 and reply.get('reason') == 'HOLD_PARTIAL_OR_OVERFLOW_FRAME', reply
    assert fixture.statebytes() == before and not any(latches(fixture).values())


def invalid_completion(name, mode):
    # Break caught: stable malformed completion can be replaced to erase its refusal.
    fixture, bind, pending = initial(name)
    fixture.bound = fixture.end_exchange(pending, json.dumps(fixture.observed))
    original = copy.deepcopy(fixture.bound)
    path, locator = fixture.logs['child'], fixture.bound['result']
    raw = path.read_bytes()
    good = raw[locator['offset']:]
    row = json.loads(good)
    if mode == 'shape':
        row['payload']['output'] = []
    elif mode == 'nested_json':
        row['payload']['output'][1]['text'] = '{'
    else:
        nested = json.loads(row['payload']['output'][1]['text'])
        nested['output'] = '{"wrong":true}'
        row['payload']['output'][1]['text'] = json.dumps(nested)
    bad = fx.canonical(row)
    assert len(bad) < len(good)
    bad += b' ' * (len(good) - len(bad) - 1) + b'\n'
    path.write_bytes(raw[:locator['offset']] + bad)
    bad_locator = {**locator, 'sha256': hashlib.sha256(bad).hexdigest()}
    first = invoke(fixture, 'observe-invalid-completion', 'observe-child', bind)
    witnessed = latches(fixture)
    path.write_bytes(raw)
    fixture.bound = original
    retry = invoke(fixture, 'retry-after-original-completion-restored', 'observe-child', bind)
    returned = invoke(fixture, 'return-after-completion-restored', 'return', fixture.result_request())
    DETAILS[name] = {'first': compact(first), 'retry': compact(retry), 'return': compact(returned), 'latches': witnessed}
    assert first[0] == 2 and first[1].get('reason') != 'HOLD_EARLY_SAME_EPISODE_USE', DETAILS[name]
    assert witnessed['hold_refusals'] and not witnessed['hold_failures'], DETAILS[name]
    evidence = witnessed['hold_refusals'][fixture.observed['observation_id']]['evidence']
    assert evidence['record'] == bad_locator, evidence
    for result in (retry, returned):
        assert result[0] == 2 and result[1].get('reason') == 'HOLD_EPISODE_PREVIOUSLY_REFUSED', DETAILS[name]


def entry_rewrite():
    # Break caught: the original immutable entry is replaced or widened by a retry.
    fixture, bind, pending = initial('entry-prefix-rewrite')
    fixture.bound = fixture.end_exchange(pending, json.dumps(fixture.observed))
    path = fixture.logs['child']
    raw = path.read_bytes()
    wires = raw.splitlines(keepends=True)
    replace_frame(fixture, {'offset': len(wires[0]), 'bytes': len(wires[1])}, {'type': 'message'})
    before = fixture.statebytes()
    code, reply = invoke(fixture, 'changed-entry-prefix', 'observe-child', bind)
    DETAILS['entry-prefix-rewrite'] = {'exit_code': code, 'reason': reply.get('reason')}
    assert code == 2 and reply.get('reason') == 'HOLD_PRIOR_PREFIX_CHANGED', reply
    assert fixture.statebytes() == before and not any(latches(fixture).values())
    path.write_bytes(raw)
    code, reply = invoke(fixture, 'restored-entry-prefix', 'observe-child', bind)
    assert code == 0 and reply == fixture.observed, reply


cases = [('early-reused', lambda: persistent_case('early-reused', 'reused')),
         ('early-distinct', lambda: persistent_case('early-distinct', 'distinct')),
         ('duplicate-without-marker', lambda: persistent_case('duplicate-without-marker', 'duplicate_without_marker')),
         ('unknown-before-marker', lambda: persistent_case('unknown-before-marker', 'unknown_before_marker')),
         ('invalid-exec-marker', lambda: persistent_case('invalid-exec-marker', 'invalid_exec_marker')),
         ('unpaired-output', lambda: persistent_case('unpaired-output', 'unpaired_output')),
         ('join-material-refusal', lambda: join_retention('join-material-refusal', False)),
         ('join-early-refusal', lambda: join_retention('join-early-refusal', True)),
         ('marker-negatives', negatives),
         ('frame-262144', lambda: response_size('frame-262144', 262144)),
         ('frame-262145', lambda: response_size('frame-262145', 262145)),
         ('partial-frame', lambda: incomplete('partial-frame', 'partial')),
         ('missing-completion', lambda: incomplete('missing-completion', 'missing_completion')),
         ('unsettled-foreign', lambda: incomplete('unsettled-foreign', 'unsettled_foreign')),
         ('raced-read', lambda: incomplete('raced-read', 'race')),
         ('records-64', lambda: record_count('records-64', 64)),
         ('records-65', lambda: record_count('records-65', 65)),
         ('total-2097152', lambda: total_bytes('total-2097152', 2097152)),
         ('total-2097153', lambda: total_bytes('total-2097153', 2097153)),
         ('completion-output-shape', lambda: invalid_completion('completion-output-shape', 'shape')),
         ('completion-nested-json', lambda: invalid_completion('completion-nested-json', 'nested_json')),
         ('completion-wrong-response', lambda: invalid_completion('completion-wrong-response', 'wrong_response')),
         ('entry-prefix-rewrite', entry_rewrite)]
records = []
for name, operation in cases:
    try:
        operation()
        record = {'case': name, 'status': 'PASS'}
    except Exception as exc:
        record = {'case': name, 'status': 'FAIL', 'error': str(exc), 'traceback': traceback.format_exc()}
    record['detail'] = DETAILS.get(name)
    records.append(record)
    print(json.dumps({'case': name, 'status': record['status'],
                      'error': record.get('error', '')[:280]}, sort_keys=True))
fx.put(SCRATCH / 'CLI_RECEIPTS.json', CLI)
fx.put(SCRATCH / 'RESULTS.json', {'schema': 'ordinary.compaction-f02-persistent-refusal-controls.v1',
    'records': records, 'cli_calls': len(CLI), 'fixture_reuse': 'Definitions only; no accepted test groups replayed',
    'authority': 'NONE', 'currentness': False, 'actual_runtime': 'UNQUALIFIED', 'native_host_capture': 'UNQUALIFIED'})
raise SystemExit(1 if any(record['status'] != 'PASS' for record in records) else 0)
