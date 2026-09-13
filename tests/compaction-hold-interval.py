#!/usr/bin/env python3
"""Focused F02 tests through real pending-owner entrypoints; synthetic, no origin credit.

Usage: python -I -S -B compaction-hold-interval.py SOURCE_ROOT OWNED_NEW_SCRATCH [CASE ...]
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import traceback
from unittest import mock

spec = importlib.util.spec_from_file_location('hold_fixture', Path(__file__).with_name('compaction-hold-fixture.py'))
fx = importlib.util.module_from_spec(spec); spec.loader.exec_module(fx)
Fixture, obs, owner = fx.Fixture, fx.obs, fx.owner


def start(name, inherited=0, fixture=None):
    f = fixture or Fixture(name, inherited); f.reserved = f.reserve(); o = f.reserved['obligation']
    deliver = {'child_id': f.child, 'phase': 'deliver', 'observation_id': o['observation_id'],
               'authorization_evidence': f.authorize(f.reserved)}
    packet = f.op('observe-child', deliver)
    exchange = f.exchange(obs.delivery_tool_input(f.store, f.session, f.owner, deliver), json.dumps(packet))
    context = f.state()['assignments'][f.child]['observation_source']
    eid = obs.digest(obs.canonical({k: obs.resolve_record(context, 'child', v)[1] for k, v in exchange.items()}))
    bind = {'child_id': f.child, 'phase': 'bind', 'observation_id': o['observation_id'], 'exchange': exchange}
    return f, bind, eid


def marked(eid):
    return '// COMPACTION_OBSERVATION_EXCHANGE=' + eid + '\ntext("Premature marked audit USE");'


def finish_bind(f, bind):
    pending = f.begin_exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind))
    rc, f.observed = f.cli('observe-child', bind)
    assert rc == 0, f.observed
    f.bound = f.end_exchange(pending, json.dumps(f.observed))


def refuse(call, expected):
    try:
        call()
    except (ValueError, OSError, KeyError) as exc:
        assert expected in str(exc), (expected, str(exc))
        return str(exc)
    raise AssertionError('ACCEPTED_FORBIDDEN_' + expected)


def valid():
    f, bind, eid = start('valid'); finish_bind(f, bind)
    rc, result = f.cli('return', f.result_request()); assert rc == 0, result
    rc, joined = f.cli('join', f.accept(result)); assert rc == 0, joined
    assert joined['status'] == 'VERIFIED_LOGICAL_JOIN_PENDING_PROFILE'
    assert joined['host_producer_authenticated'] is False and joined['pending_consumed'] is False
    assert joined['authority'] == 'NONE' and joined['canonical_currentness'] is False
    return {'status': joined['status'], 'host_producer_authenticated': False, 'pending_consumed': False}


def exact_early():
    f, bind, eid = start('exact-early'); early = f.exchange(marked(eid), 'Premature marked audit USE completed')
    rc, bound = f.cli('observe-child', bind)
    if rc == 0:
        f.observed = bound
        f.bound = f.exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind), json.dumps(bound))
        rc_return, result = f.cli('return', f.result_request())
        joined = f.cli('join', f.accept(result)) if rc_return == 0 else None
        (fx.SCRATCH / 'EXACT_EARLY_ACCEPTANCE.json').write_text(json.dumps({
            'early': early, 'bound': f.bound, 'selected_later_use': f.request['result_evidence']['use'],
            'return': {'exit': rc_return, 'result': result}, 'join': joined,
            'synthetic_only': True, 'authority': 'NONE'}, indent=2))
        raise AssertionError('EARLY_USE_ACCEPTED_BY_BIND_RETURN_JOIN ' + str((rc_return, joined[0] if joined else None)))
    assert 'HOLD_EARLY_SAME_EPISODE_USE' in bound['reason'], bound
    assert f.state()['assignments'][f.child]['return'] is None
    return {'reason': bound['reason'], 'early': early}


def early_after_bind_decision():
    f, bind, eid = start('between-bind-and-response')
    pending = f.begin_exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind))
    rc, f.observed = f.cli('observe-child', bind); assert rc == 0, f.observed
    early = f.exchange(marked(eid), 'Early call after helper decision, before full host response')
    f.bound = f.end_exchange(pending, json.dumps(f.observed))
    rc, result = f.cli('return', f.result_request())
    assert rc == 2 and 'HOLD_EARLY_SAME_EPISODE_USE' in result['reason'], result
    assert f.state()['assignments'][f.child]['return'] is None
    return {'reason': result['reason'], 'early': early}


def permanent_breach():
    f, bind, eid = start('permanent-breach'); f.exchange(marked(eid), 'early')
    rc, result = f.cli('observe-child', bind)
    assert rc == 2 and result['reason'] == 'HOLD_EARLY_SAME_EPISODE_USE', result
    failure = f.state()['assignments'][f.child]['hold_failures']
    # Preparing another observation must not erase the old episode's breach.
    again = f.op('observe-child', {'child_id': f.child, 'phase': 'prepare'})
    rc, result = f.cli('observe-child', bind)
    # prepare removed exchange authorization; the persistent failure is checked
    # before it can authorize a new bind, even if malformed proof refuses first.
    assert rc == 2 and f.state()['assignments'][f.child]['hold_failures'] == failure
    return {'failure': failure, 'retry_reason': result['reason'], 'later_observation': again['obligation']['observation_id']}


def attempted_early():
    f, bind, eid = start('attempt-without-response')
    f.row('child', 'response_item', {'type': 'custom_tool_call', 'name': 'exec', 'call_id': 'attempt-only',
        'status': 'in_progress', 'input': marked(eid)})
    rc, result = f.cli('observe-child', bind)
    assert rc == 2 and result['reason'] == 'HOLD_EARLY_SAME_EPISODE_USE', result
    return {'reason': result['reason'], 'claim': 'observable attempted call only'}


def during_bind():
    f, bind, eid = start('overlapping-bind')
    command = obs.delivery_tool_input(f.store, f.session, f.owner, bind)
    call = f.row('child', 'response_item', {'type': 'custom_tool_call', 'name': 'exec', 'call_id': 'open-bind',
        'status': 'completed', 'input': command})
    rc, f.observed = f.cli('observe-child', bind); assert rc == 0, f.observed
    f.exchange(marked(eid), 'during open bind')
    output = f.row('child', 'response_item', {'type': 'custom_tool_call_output', 'call_id': 'open-bind', 'output': [
        {'type': 'input_text', 'text': 'Script completed\nOutput:\n'},
        {'type': 'input_text', 'text': json.dumps({'chunk_id': 'bind-response', 'wall_time_seconds': .1,
          'exit_code': 0, 'original_token_count': 100, 'output': json.dumps(f.observed)})}]})
    f.bound = {'call': call, 'result': output}
    rc, result = f.cli('return', f.result_request())
    assert rc == 2 and result['reason'] == 'HOLD_EARLY_SAME_EPISODE_USE', result
    return {'reason': result['reason']}


def non_use_traffic():
    f, bind, eid = start('non-use-traffic')
    f.message('child', 'Quoted documentation: ' + marked(eid))
    # An actual separate exchange has a distinct episode identity. Its output
    # also quotes the current marker; neither is a matching current tool USE.
    f.exchange(marked('a' * 64), 'Output-only quoted marker: ' + marked(eid))
    # Same text in another actor's physical source is not this child's call.
    f.row('parent', 'response_item', {'type': 'custom_tool_call', 'name': 'exec', 'call_id': 'foreign-child-event',
        'status': 'completed', 'input': marked(eid)})
    finish_bind(f, bind)
    rc, result = f.cli('return', f.result_request()); assert rc == 0, result
    rc, joined = f.cli('join', f.accept(result)); assert rc == 0, joined
    assert joined['pending_consumed'] is False and joined['host_producer_authenticated'] is False
    return {'status': joined['status'], 'false_early_use_findings': 0}


def unknown_call():
    f, bind, eid = start('unclassified-call')
    f.exchange('text("unclassified tool, not proof of private cognition");', 'unknown')
    rc, result = f.cli('observe-child', bind)
    assert rc == 2 and result['reason'] == 'HOLD_UNCLASSIFIED_TOOL_CALL', result
    return {'reason': result['reason'], 'early_same_episode_use_claimed': False}


def missing_interval():
    f, bind, eid = start('sparse-ranges')
    note = f.message('child', 'this intervening physical row is not caller-selectable')
    state = f.state(); source = state['assignments'][f.child]['observation_source']['child']
    # Corrupt only the allowed read windows to model a caller omitting one row.
    end = f.logs['child'].stat().st_size
    source['allowed_ranges'] = [{'offset': 0, 'bytes': note['offset']},
        {'offset': note['offset'] + note['bytes'], 'bytes': 128}]
    owner.save(f.store, state)
    rc, result = f.cli('observe-child', bind)
    assert rc == 2 and result['reason'] == 'HOLD_CONTIGUOUS_RANGE_REQUIRED', result
    return {'reason': result['reason'], 'omitted_offset': note['offset'], 'whole_end': end}


def event_gap():
    f, bind, eid = start('event-gap'); f.ordinal['child'] += 1
    f.message('child', 'a missing event cannot count as absence')
    rc, result = f.cli('observe-child', bind)
    assert rc == 2 and result['reason'] == 'HOLD_EVENT_GAP_OR_DUPLICATE', result
    return {'reason': result['reason']}


def partial_frame():
    f, bind, eid = start('partial-frame')
    with f.logs['child'].open('ab') as stream: stream.write(b'{"partial":')
    rc, result = f.cli('observe-child', bind)
    assert rc == 2 and result['reason'] == 'HOLD_PARTIAL_OR_OVERFLOW_FRAME', result
    return {'reason': result['reason']}


def record_overflow():
    f, bind, eid = start('record-overflow')
    for _ in range(64): f.message('child', 'bounded event')
    rc, result = f.cli('observe-child', bind)
    assert rc == 2 and result['reason'] == 'HOLD_RECORD_COUNT_BOUND', result
    return {'reason': result['reason']}


def byte_overflow():
    f, bind, eid = start('byte-overflow')
    with f.logs['child'].open('ab') as stream: stream.write(b' ' * obs.MAX_TOTAL)
    rc, result = f.cli('observe-child', bind)
    assert rc == 2 and result['reason'] == 'HOLD_PREFIX_BYTE_BOUND', result
    return {'reason': result['reason']}


def prefix_change():
    f, bind, eid = start('prefix-change'); f.message('child', 'bounded-note-A')
    finish_bind(f, bind)
    path = f.logs['child']; before = path.read_bytes()
    assert before.count(b'bounded-note-A') == 1
    path.write_bytes(before.replace(b'bounded-note-A', b'bounded-note-B'))
    rc, result = f.cli('return', f.result_request())
    assert rc == 2 and result['reason'] == 'HOLD_PRIOR_PREFIX_CHANGED', result
    return {'reason': result['reason']}


def join_revalidates():
    f, bind, eid = start('join-revalidation'); f.message('child', 'before-bind-A')
    finish_bind(f, bind)
    rc, result = f.cli('return', f.result_request()); assert rc == 0, result
    acceptance = f.accept(result)
    path = f.logs['child']; path.write_bytes(path.read_bytes().replace(b'before-bind-A', b'before-bind-B'))
    rc, joined = f.cli('join', acceptance)
    assert rc == 2 and joined['reason'] == 'HOLD_PRIOR_PREFIX_CHANGED', joined
    assert f.state()['assignments'][f.child]['join'] is None
    return {'reason': joined['reason']}


def preflight_no_read():
    f, bind, eid = start('preflight-no-read')
    context = f.state()['assignments'][f.child]['observation_source']
    results = []
    # This reader's entire prefix budget/window proof must precede its open.
    for change, reason in ((lambda c: c['child'].update(allowed_ranges=[{'offset': 1, 'bytes': 10}]), 'HOLD_CONTIGUOUS_RANGE_REQUIRED'),
                           (lambda c: c['child'].update(physical={'device': -1, 'inode': -1}), 'HOLD_SOURCE_PHYSICAL_CHANGED')):
        altered = copy.deepcopy(context); change(altered)
        with mock.patch('builtins.open', side_effect=AssertionError('CONTENT_IO_BEFORE_PREFLIGHT')):
            results.append(refuse(lambda: obs.hold_records(altered), reason))
    with mock.patch('builtins.open', side_effect=AssertionError('CONTENT_IO_BEFORE_PREFLIGHT')):
        results.append(refuse(lambda: obs.hold_records(context, obs.MAX_TOTAL + 1), 'HOLD_PREFIX_BYTE_BOUND'))
    return {'refusals_before_open': results}


def join_cannot_launder_early():
    f, bind, eid = start('join-no-laundering')
    pending = f.begin_exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind))
    rc, f.observed = f.cli('observe-child', bind); assert rc == 0, f.observed
    note = f.message('child', 'Mutable synthetic gap note ' + 'x' * 400)
    f.bound = f.end_exchange(pending, json.dumps(f.observed))
    rc, result = f.cli('return', f.result_request()); assert rc == 0, result
    # Change only an unselected synthetic gap row, keeping every selected
    # locator and the immutable entry prefix intact. JOIN must scan it again.
    path = f.logs['child']; raw = path.read_bytes()
    changed = json.loads(raw[note['offset']:note['offset'] + note['bytes']])
    changed['payload'] = {'type': 'custom_tool_call', 'name': 'exec', 'call_id': 'gap-early',
        'status': 'in_progress', 'input': marked(eid), 'padding': ''}
    remaining = note['bytes'] - len(fx.canonical(changed) + b'\n')
    assert remaining >= 0
    changed['payload']['padding'] = ' ' * remaining
    wire = fx.canonical(changed) + b'\n'; assert len(wire) == note['bytes']
    path.write_bytes(raw[:note['offset']] + wire + raw[note['offset'] + note['bytes']:])
    rc, result = f.cli('join', f.accept(result))
    assert rc == 2 and result['reason'] == 'HOLD_EARLY_SAME_EPISODE_USE', result
    return {'reason': result['reason'], 'mutation_control': 'synthetic unselected gap row changed after RETURN; no validator bypass'}


def record_read_ceiling():
    f, bind, eid = start('record-read-ceiling')
    with f.logs['child'].open('ab') as stream: stream.write(b'x' * (obs.MAX_RECORD + 1))
    context = f.state()['assignments'][f.child]['observation_source']
    opened = open; reads = []
    class BoundedReader:
        def __init__(self, stream): self.stream = stream
        def __enter__(self): return self
        def __exit__(self, *args): return self.stream.__exit__(*args)
        def fileno(self): return self.stream.fileno()
        def readline(self, limit):
            assert 0 < limit <= obs.MAX_RECORD, ('READ_PAST_RECORD_CEILING', limit)
            assert self.stream.tell() + limit <= f.logs['child'].stat().st_size
            reads.append(limit)
            return self.stream.readline(limit)
    with mock.patch('builtins.open', lambda *a, **k: BoundedReader(opened(*a, **k))):
        reason = refuse(lambda: obs.hold_records(context), 'HOLD_PARTIAL_OR_OVERFLOW_FRAME')
    return {'reason': reason, 'max_requested_read': max(reads), 'record_limit': obs.MAX_RECORD}


def physical_replacement():
    f, bind, eid = start('physical-replacement'); finish_bind(f, bind)
    request = f.result_request()
    path = f.logs['child']; replacement = path.with_suffix('.replacement')
    replacement.write_bytes(path.read_bytes()); replacement.replace(path)
    rc, result = f.cli('return', request)
    assert rc == 2 and result['reason'] == 'SOURCE_PHYSICAL_ID_CHANGED', result
    return {'reason': result['reason'], 'unchanged_bytes_are_not_unchanged_source': True}


def bind_attempt(f, bind):
    pending = f.begin_exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind))
    rc, reply = f.cli('observe-child', bind)
    pair = f.end_exchange(pending, json.dumps(reply), rc)
    return rc, reply, pair


def logical_finish(f, request=None):
    rc, result = f.cli('return', request or f.result_request())
    assert rc == 0, result
    rc, joined = f.cli('join', f.accept(result))
    assert rc == 0, joined
    assert joined['status'] == 'VERIFIED_LOGICAL_JOIN_PENDING_PROFILE'
    assert joined['pending_consumed'] is False and joined['host_producer_authenticated'] is False
    assert result['identity']['bound_exchange']['call']['locator'] == f.bound['call']
    assert result['identity']['bound_exchange']['result']['locator'] == f.bound['result']
    assert result['identity']['hold_history']['prefix_bytes'] == f.bound['result']['offset'] + f.bound['result']['bytes']
    return {'return': result, 'join': joined}


def exact_retry(name, legal_use=False, large_tail=False):
    # Break: a duplicate request reopens the completed hold or changes its identity.
    f, bind, _ = start(name); finish_bind(f, bind)
    before = f.statebytes()
    request = f.result_request() if legal_use or large_tail else None
    if large_tail:
        for _ in range(70): f.message('child', 'Settled post-cutoff physical record')
        f.message('child', 'x' * (2 * 1024 * 1024))
    rc, reply, retry = bind_attempt(f, bind)
    assert rc == 0 and reply == f.observed, (rc, reply)
    assert f.statebytes() == before, 'EXACT_RETRY_CHANGED_PENDING_STATE'
    actual = logical_finish(f, request)
    evidence = {'original': f.bound, 'retry': retry, 'entry_unchanged': True, **actual}
    fx.put(fx.SCRATCH / (name + '-actual.json'), evidence)
    return {'original_response_end': f.bound['result']['offset'] + f.bound['result']['bytes'],
            'physical_records': actual['return']['identity']['hold_history']['physical_records'],
            'pending_consumed': False, 'host_producer_authenticated': False}


def retry_response(): return exact_retry('retry-response')
def retry_legal_use(): return exact_retry('retry-legal-use', legal_use=True)
def retry_large_tail(): return exact_retry('retry-large-tail', large_tail=True)


def alternate_bind_occurrence():
    # Break: RETURN accepts a later identical call as the original completion.
    f, bind, _ = start('alternate-bind-occurrence'); finish_bind(f, bind)
    later = f.exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind), json.dumps(f.observed))
    request = f.result_request(); request['result_evidence']['bound_exchange'] = later
    rc, result = f.cli('return', request)
    assert rc == 2 and result['reason'] == 'BOUND_EXCHANGE_NOT_ORIGINAL', (rc, result)
    assert not f.state()['assignments'][f.child].get('hold_failures')
    request['result_evidence']['bound_exchange'] = f.bound
    actual = logical_finish(f, request)
    return {'reason': result['reason'], 'original_still_valid': actual['join']['pending_consumed'] is False}


def missing_original_completion():
    # Break: a completed later retry substitutes for an original call with no output.
    f, bind, _ = start('missing-original-completion')
    pending = f.begin_exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind))
    rc, f.observed = f.cli('observe-child', bind); assert rc == 0, f.observed
    f.exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind), json.dumps(f.observed))
    rc, reply, _ = bind_attempt(f, bind)
    assert rc == 2 and reply['reason'] in ('HOLD_ORIGINAL_BIND_COMPLETION_UNPROVED', 'HOLD_UNSETTLED_TOOL_CALL'), (rc, reply)
    assert not f.state()['assignments'][f.child].get('hold_failures')
    f.bound = f.end_exchange(pending, json.dumps(f.observed))
    rc, reply, _ = bind_attempt(f, bind)
    assert rc == 0 and reply == f.observed, (rc, reply)
    logical_finish(f)
    return {'missing_refused_then_original_completed': True, 'pending_consumed': False}


def original_response_failure():
    # Break: a later success replaces the original failed or partial response.
    results = []
    for kind in ('failed', 'partial'):
        f, bind, _ = start('original-response-' + kind)
        pending = f.begin_exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind))
        rc, f.observed = f.cli('observe-child', bind); assert rc == 0, f.observed
        if kind == 'failed':
            f.bound = f.end_exchange(pending, json.dumps(f.observed), 2)
            reason = 'FULL_SUCCESSFUL_HOST_RESPONSE_REQUIRED'
        else:
            response = f.row('child', 'response_item', {'type': 'custom_tool_call_output',
                'call_id': pending['call_id'], 'output': [{'type': 'input_text', 'text': 'partial'}]})
            f.bound = {'call': pending['call'], 'result': response}
            reason = 'FULL_HOST_OUTPUT_SHAPE'
        f.exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind), json.dumps(f.observed))
        rc, reply, _ = bind_attempt(f, bind)
        assert rc == 2 and reply['reason'] == reason, (rc, reply)
        assert not f.state()['assignments'][f.child].get('hold_failures')
        results.append(reason)
    return {'refusals': results}


def original_call_custody():
    # Break: a successful helper decision lacks one provable pending original call.
    results = []
    for count in (0, 2):
        f, bind, _ = start('original-call-count-' + str(count))
        for _ in range(count): f.begin_exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind))
        rc, reply = f.cli('observe-child', bind)
        assert rc == 2 and reply['reason'] in ('HOLD_ORIGINAL_BIND_CALL_UNPROVED', 'HOLD_UNSETTLED_TOOL_CALL'), (rc, reply)
        assert not f.state()['assignments'][f.child]['observations']
        results.append(reply['reason'])
    return {'refusals': results}


def early_scan_response_gap():
    # Break: cached or later-cutoff retries erase an executed early USE in the gap.
    f, bind, eid = start('early-scan-response-gap')
    pending = f.begin_exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind))
    rc, f.observed = f.cli('observe-child', bind); assert rc == 0, f.observed
    f.exchange(marked(eid), 'Actual early USE after initial scan, before response')
    f.bound = f.end_exchange(pending, json.dumps(f.observed))
    rc, reply, _ = bind_attempt(f, bind)
    assert rc == 2 and reply['reason'] == 'HOLD_EARLY_SAME_EPISODE_USE', (rc, reply)
    failures = f.state()['assignments'][f.child]['hold_failures']
    rc, result = f.cli('return', f.result_request())
    assert rc == 2 and result['reason'] == 'HOLD_EPISODE_PREVIOUSLY_DISQUALIFIED', result
    rc, reply, _ = bind_attempt(f, bind)
    assert rc == 2 and reply['reason'] == 'HOLD_EPISODE_PREVIOUSLY_DISQUALIFIED', reply
    assert f.state()['assignments'][f.child]['hold_failures'] == failures
    return {'permanent_failure': failures}


def completed_prefix_boundary():
    # Break: counting only active rows or enlarging a completed hold changes 64/65.
    results = []
    for total in (64, 65):
        f, bind, _ = start('completed-prefix-' + str(total), inherited=22)
        for _ in range(total - 29): f.message('child', 'Active bounded hold note')
        finish_bind(f, bind)
        assert f.bound['result']['physical_line'] == total
        request = f.result_request()
        rc, reply, _ = bind_attempt(f, bind)
        if total == 64:
            assert rc == 0 and reply == f.observed, (rc, reply)
            actual = logical_finish(f, request)
            assert actual['return']['identity']['hold_history']['physical_records'] == 64
        else:
            assert rc == 2 and reply['reason'] == 'HOLD_RECORD_COUNT_BOUND', (rc, reply)
            rc, reply = f.cli('return', request)
            assert rc == 2 and reply['reason'] == 'HOLD_RECORD_COUNT_BOUND', reply
        results.append({'completed_physical_records': total, 'exit': rc})
    return {'boundary': results, 'inherited_physical_records': 22}


def retry_read_race():
    # Break: an append during bounded read becomes a permanent fabricated breach.
    f, bind, _ = start('retry-read-race'); finish_bind(f, bind)
    real_open = open; injected = []
    class RacingReader:
        def __init__(self, stream): self.stream = stream
        def __enter__(self): self.stream.__enter__(); return self
        def __exit__(self, *args): return self.stream.__exit__(*args)
        def __getattr__(self, name): return getattr(self.stream, name)
        def readline(self, limit):
            raw = self.stream.readline(limit)
            if not injected:
                injected.append(f.message('child', 'Append during physical hold reading'))
            return raw
    def opened(path, *args, **kwargs):
        stream = real_open(path, *args, **kwargs)
        return RacingReader(stream) if Path(path) == f.logs['child'] and args == ('rb',) else stream
    pending = f.begin_exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind))
    with mock.patch('builtins.open', opened): rc, reply = f.cli('observe-child', bind)
    f.end_exchange(pending, json.dumps(reply), rc)
    assert rc == 2 and reply['reason'] == 'HOLD_SOURCE_CHANGED_DURING_READ', (rc, reply)
    assert not f.state()['assignments'][f.child].get('hold_failures')
    rc, settled, _ = bind_attempt(f, bind)
    assert rc == 0 and settled == f.observed, (rc, settled)
    logical_finish(f)
    return {'transient_reason': reply['reason'], 'settled_retry_exit': rc, 'permanent_failure': False}


def retry_scope_guards():
    # Break: returning the cached reply bypasses request, child or exchange checks.
    f, bind, _ = start('retry-scope-guards'); finish_bind(f, bind)
    before = f.statebytes(); results = []
    for label in ('child', 'observation', 'cutoff', 'exchange', 'exchange-extra'):
        changed = copy.deepcopy(bind)
        if label == 'child': changed['child_id'] = 'another-child'
        elif label == 'observation': changed['observation_id'] = 'another-observation'
        elif label == 'cutoff': changed['completed_cutoff'] = f.bound['result']['offset'] + f.bound['result']['bytes']
        elif label == 'exchange': changed['exchange']['result']['sha256'] = '0' * 64
        else: changed['exchange']['caller_completed'] = True
        rc, reply = f.cli('observe-child', changed)
        assert rc == 2 and f.statebytes() == before, (label, rc, reply)
        results.append({'changed': label, 'reason': reply['reason']})
    rc, reply, _ = bind_attempt(f, bind)
    assert rc == 0 and reply == f.observed, (rc, reply)
    logical_finish(f)
    return {'refusals': results, 'exact_retry_still_valid': True}


def r2_start(name, collision=True):
    f = Fixture(name, inherited=22)
    path = f.logs['child']; rows = [json.loads(wire) for wire in path.read_bytes().splitlines()]
    inherited_id = 'active-bind-id' if collision else 'legacy-bind-id'
    rows[1]['payload'] = {'type': 'custom_tool_call', 'name': 'exec', 'call_id': inherited_id,
        'status': 'completed', 'input': marked('a' * 64)}
    rows[2]['payload'] = {'type': 'custom_tool_call_output', 'call_id': inherited_id, 'output': [
        {'type': 'input_text', 'text': 'Script completed\nOutput:\n'},
        {'type': 'input_text', 'text': json.dumps({'chunk_id': 'inherited-output', 'wall_time_seconds': .1,
          'exit_code': 0, 'original_token_count': 100, 'output': 'Inherited completed work only'})}]}
    path.write_bytes(b''.join(fx.canonical(row) + b'\n' for row in rows))
    f, bind, eid = start(name, fixture=f)
    # Same-episode marker text in inherited execution is semantically excluded;
    # it still occupies a complete physical frame and the initial prefix hash.
    wires = path.read_bytes().splitlines(keepends=True); inherited = json.loads(wires[1])
    inherited['payload']['input'] = marked(eid)
    changed = fx.canonical(inherited) + b'\n'; assert len(changed) == len(wires[1])
    wires[1] = changed; path.write_bytes(b''.join(wires))
    return f, bind, eid


def r2_begin(f, bind, call_id='active-bind-id'):
    call = f.row('child', 'response_item', {'type': 'custom_tool_call', 'name': 'exec', 'call_id': call_id,
        'status': 'completed', 'input': obs.delivery_tool_input(f.store, f.session, f.owner, bind)})
    return {'call': call, 'call_id': call_id}


def r2_finish(f, bind):
    pending = r2_begin(f, bind)
    rc, f.observed = f.cli('observe-child', bind); assert rc == 0, f.observed
    f.bound = f.end_exchange(pending, json.dumps(f.observed))


def r2_retry(f, bind, race=False):
    real_open = open; endpoints = []; injected = []
    class Reader:
        def __init__(self, stream): self.stream = stream
        def __enter__(self): self.stream.__enter__(); return self
        def __exit__(self, *args): return self.stream.__exit__(*args)
        def __getattr__(self, name): return getattr(self.stream, name)
        def readline(self, limit):
            raw = self.stream.readline(limit); endpoints.append(self.stream.tell())
            if race and not injected: injected.append(f.message('child', 'Append during inherited-prefix read'))
            return raw
    def opened(path, *args, **kwargs):
        stream = real_open(path, *args, **kwargs)
        return Reader(stream) if Path(path) == f.logs['child'] and args == ('rb',) else stream
    with mock.patch('builtins.open', opened): rc, reply, pair = bind_attempt(f, bind)
    return rc, reply, pair, endpoints


def r2_pair(collision):
    # Break: an inherited matching ID terminates discovery before the selected active call.
    name = 'r2-collision' if collision else 'r2-distinct'
    f, bind, _ = r2_start(name, collision); r2_finish(f, bind)
    assert f.bound['call']['physical_line'] == 28 and f.bound['result']['physical_line'] == 29
    assert f.bound['call']['embedded_ordinal'] == 27 and f.bound['result']['embedded_ordinal'] == 28
    before = f.statebytes(); rc, reply, retry, endpoints = r2_retry(f, bind)
    unchanged = f.statebytes() == before
    return_rc, result = f.cli('return', f.result_request())
    join_rc, joined = f.cli('join', f.accept(result)) if return_rc == 0 else (None, None)
    end = f.bound['result']['offset'] + f.bound['result']['bytes']
    evidence = {'collision': collision, 'original_bind': f.bound, 'original_response_end': end,
        'initial_bind_exit': 0, 'retry_exit': rc, 'retry_response': reply, 'retry_pair': retry,
        'state_unchanged': unchanged, 'read_endpoints': endpoints, 'return_exit': return_rc,
        'return': result, 'join_exit': join_rc, 'join': joined,
        'hold_failures': f.state()['assignments'][f.child].get('hold_failures', {})}
    fx.put(fx.SCRATCH / (name + '-actual.json'), evidence)
    assert rc == 0 and reply == f.observed and unchanged, (rc, reply)
    assert return_rc == 0 and join_rc == 0, (return_rc, result, join_rc, joined)
    assert joined['pending_consumed'] is False and joined['host_producer_authenticated'] is False
    assert result['identity']['bound_exchange']['call']['locator'] == f.bound['call']
    assert result['identity']['bound_exchange']['result']['locator'] == f.bound['result']
    assert result['identity']['hold_history']['prefix_bytes'] == max(endpoints) == end
    assert result['identity']['hold_history']['physical_records'] == 29
    assert not evidence['hold_failures']
    return {'original_response_end': end, 'max_read_endpoint': max(endpoints), 'physical_records': 29,
            'pending_consumed': False, 'host_producer_authenticated': False}


def r2_collision(): return r2_pair(True)
def r2_distinct(): return r2_pair(False)


def r2_settled():
    # Break: ID repair widens the original cutoff or reopens it after legal USE.
    f, bind, _ = r2_start('r2-settled'); r2_finish(f, bind)
    request = f.result_request(); before = f.statebytes()
    for _ in range(70): f.message('child', 'Settled suffix after original completion')
    f.message('child', 'x' * (2 * 1024 * 1024))
    end = f.bound['result']['offset'] + f.bound['result']['bytes']; retries = []
    for _ in range(2):
        rc, reply, pair, endpoints = r2_retry(f, bind)
        assert rc == 0 and reply == f.observed and f.statebytes() == before, (rc, reply)
        assert max(endpoints) == end, (max(endpoints), end)
        retries.append({'pair': pair, 'read_endpoints': endpoints})
    actual = logical_finish(f, request)
    fx.put(fx.SCRATCH / 'r2-settled-actual.json', {'original': f.bound, 'original_response_end': end,
        'retries': retries, 'state_unchanged': True, **actual})
    return {'original_response_end': end, 'recorded_retries': 2, 'pending_consumed': False}


def r2_missing():
    # Break: inherited output or a later retry proves the still-absent active response.
    f, bind, _ = r2_start('r2-missing'); pending = r2_begin(f, bind)
    rc, f.observed = f.cli('observe-child', bind); assert rc == 0, f.observed
    later = f.exchange(obs.delivery_tool_input(f.store, f.session, f.owner, bind), json.dumps(f.observed))
    before = f.statebytes(); rc, reply, _, _ = r2_retry(f, bind)
    assert rc == 2 and reply['reason'] in ('HOLD_ORIGINAL_BIND_COMPLETION_UNPROVED', 'HOLD_UNSETTLED_TOOL_CALL'), (rc, reply)
    request = {'child_id': f.child, 'observation_id': bind['observation_id'], 'result_evidence': {
        'bound_exchange': later, 'use': later, 'child_final': later['result'], 'parent_delivery': later['result']}}
    rc_return, refused = f.cli('return', request)
    assert rc_return == 2 and refused['reason'] == 'HOLD_ORIGINAL_BIND_COMPLETION_UNPROVED', refused
    assert f.statebytes() == before and not f.state()['assignments'][f.child].get('hold_failures')
    f.bound = f.end_exchange(pending, json.dumps(f.observed))
    rc, reply, _, _ = r2_retry(f, bind); assert rc == 0 and reply == f.observed, (rc, reply)
    logical_finish(f)
    return {'missing_return_reason': refused['reason'], 'proper_original_later_completed': True}


def r2_active_ambiguity():
    # Break: ignoring an inherited decoy also ignores active duplicates or pre-call output.
    results = []
    for kind in ('duplicate', 'two-pending', 'pre-call-output', 'overlap'):
        f, bind, _ = r2_start('r2-active-' + kind)
        if kind == 'pre-call-output':
            f.row('child', 'response_item', {'type': 'custom_tool_call_output', 'call_id': 'active-bind-id', 'output': []})
        pending = r2_begin(f, bind)
        if kind == 'overlap':
            rc, f.observed = f.cli('observe-child', bind); assert rc == 0, f.observed
        if kind in ('duplicate', 'overlap'): r2_begin(f, bind)
        if kind == 'two-pending': r2_begin(f, bind, 'other-active-bind')
        if kind == 'overlap': f.bound = f.end_exchange(pending, json.dumps(f.observed))
        rc, reply = f.cli('observe-child', bind)
        want = 'HOLD_UNPAIRED_TOOL_OUTPUT' if kind == 'pre-call-output' else 'HOLD_UNSETTLED_TOOL_CALL' if kind == 'two-pending' else 'HOLD_UNCLASSIFIED_TOOL_CALL'
        assert rc == 2 and reply['reason'] == want, (kind, rc, reply)
        assert not f.state()['assignments'][f.child].get('hold_failures')
        results.append({'variant': kind, 'reason': reply['reason']})
    return {'refusals': results}


def r2_early_gap():
    # Break: an inherited decoy masks the real active USE before original response.
    f, bind, eid = r2_start('r2-early-gap'); pending = r2_begin(f, bind)
    rc, f.observed = f.cli('observe-child', bind); assert rc == 0, f.observed
    f.exchange(marked(eid), 'True active early USE in the response gap')
    f.bound = f.end_exchange(pending, json.dumps(f.observed))
    rc, reply, _, _ = r2_retry(f, bind)
    assert rc == 2 and reply['reason'] == 'HOLD_EARLY_SAME_EPISODE_USE', (rc, reply)
    failures = f.state()['assignments'][f.child]['hold_failures']
    rc, result = f.cli('return', f.result_request())
    assert rc == 2 and result['reason'] == 'HOLD_EPISODE_PREVIOUSLY_DISQUALIFIED', result
    rc, reply, _, _ = r2_retry(f, bind)
    assert rc == 2 and reply['reason'] == 'HOLD_EPISODE_PREVIOUSLY_DISQUALIFIED', reply
    assert f.state()['assignments'][f.child]['hold_failures'] == failures
    return {'persistent_failure': failures}


def r2_integrity():
    # Break: occurrence pairing bypasses source, prefix, ordinal or caller-locator guards.
    results = []
    for kind in ('prefix', 'source', 'return-locator', 'ordinal', 'metadata'):
        f, bind, _ = r2_start('r2-integrity-' + kind); r2_finish(f, bind)
        path = f.logs['child']; raw = path.read_bytes()
        if kind == 'prefix':
            assert b'Inherited physical history' in raw
            path.write_bytes(raw.replace(b'Inherited physical history', b'Inherited physical historX', 1))
            want = 'HOLD_PRIOR_PREFIX_CHANGED'
        elif kind == 'source':
            replacement = path.with_suffix('.replacement'); replacement.write_bytes(raw); replacement.replace(path)
            want = 'SOURCE_PHYSICAL_ID_CHANGED'
        elif kind == 'return-locator':
            request = f.result_request(); request['result_evidence']['bound_exchange'] = copy.deepcopy(f.bound)
            request['result_evidence']['bound_exchange']['call']['offset'] += 1
            rc, reply = f.cli('return', request)
            assert rc == 2 and reply['reason'] == 'BOUND_EXCHANGE_NOT_ORIGINAL', (rc, reply)
            results.append({'variant': kind, 'reason': reply['reason']}); continue
        elif kind == 'ordinal':
            wires = raw.splitlines(keepends=True); row = json.loads(wires[5]); row['ordinal'] = 7
            replacement = fx.canonical(row) + b'\n'; assert len(replacement) == len(wires[5])
            wires[5] = replacement; path.write_bytes(b''.join(wires)); want = 'HOLD_EVENT_GAP_OR_DUPLICATE'
        else:
            path.write_bytes(raw.replace(b'0.153.4', b'0.153.5', 1)); want = 'RECORD_PIN_CHANGED'
        rc, reply = f.cli('observe-child', bind)
        assert rc == 2 and reply['reason'] == want, (kind, rc, reply)
        assert not f.state()['assignments'][f.child].get('hold_failures')
        results.append({'variant': kind, 'reason': reply['reason']})
    return {'refusals': results}


def r2_bad_original():
    # Break: discovery skips a bad eligible original output to accept a later good one.
    results = []
    for kind in ('partial', 'mismatched'):
        f, bind, _ = r2_start('r2-bad-original-' + kind); pending = r2_begin(f, bind)
        rc, f.observed = f.cli('observe-child', bind); assert rc == 0, f.observed
        if kind == 'partial':
            f.row('child', 'response_item', {'type': 'custom_tool_call_output', 'call_id': pending['call_id'], 'output': []})
            want = 'FULL_HOST_OUTPUT_SHAPE'
        else:
            wrong = {**f.observed, 'observation_id': 'another-observation'}
            f.end_exchange(pending, json.dumps(wrong)); want = 'FULL_MECHANICAL_BIND_RESPONSE_REQUIRED'
        f.end_exchange(pending, json.dumps(f.observed))
        rc, reply, _, _ = r2_retry(f, bind)
        assert rc == 2 and reply['reason'] == want, (kind, rc, reply)
        assert not f.state()['assignments'][f.child].get('hold_failures')
        results.append({'variant': kind, 'reason': reply['reason']})
    return {'refusals': results}


def r2_record_bounds():
    # Break: inherited decoys are skipped for the completed-prefix record ceiling.
    results = []
    for count in (64, 65):
        f, bind, _ = r2_start('r2-records-' + str(count))
        for _ in range(count - 29): f.message('child', 'Active counted frame')
        r2_finish(f, bind); assert f.bound['result']['physical_line'] == count
        request = f.result_request(); rc, reply, _, _ = r2_retry(f, bind)
        if count == 64:
            assert rc == 0 and reply == f.observed, (rc, reply)
            actual = logical_finish(f, request)
            assert actual['return']['identity']['hold_history']['physical_records'] == 64
        else:
            assert rc == 2 and reply['reason'] == 'HOLD_RECORD_COUNT_BOUND', (rc, reply)
            rc, result = f.cli('return', request)
            assert rc == 2 and result['reason'] == 'HOLD_RECORD_COUNT_BOUND', result
        results.append({'physical_records': count, 'exit': rc})
    return {'boundary': results, 'inherited_frames_counted': 22}


def r2_byte_frame_bounds():
    # Break: pairing discovery relaxes whole-prefix or individual-frame byte bounds.
    results = []
    for kind, size, want in [('prefix', 2 * 1024 * 1024, 'HOLD_PREFIX_BYTE_BOUND'),
                             ('frame', 256 * 1024, 'HOLD_PARTIAL_OR_OVERFLOW_FRAME')]:
        f, bind, _ = r2_start('r2-bytes-' + kind)
        f.message('child', 'x' * size); r2_begin(f, bind)
        rc, reply = f.cli('observe-child', bind)
        assert rc == 2 and reply['reason'] == want, (rc, reply)
        assert not f.state()['assignments'][f.child]['observations']
        results.append({'variant': kind, 'reason': reply['reason']})
    return {'refusals': results}


def r2_read_race():
    # Break: a read race becomes permanent, or a settled collision retry stays refused.
    f, bind, _ = r2_start('r2-read-race'); r2_finish(f, bind)
    rc, reply, _, _ = r2_retry(f, bind, race=True)
    assert rc == 2 and reply['reason'] == 'HOLD_SOURCE_CHANGED_DURING_READ', (rc, reply)
    assert not f.state()['assignments'][f.child].get('hold_failures')
    rc, reply, _, endpoints = r2_retry(f, bind)
    assert rc == 0 and reply == f.observed, (rc, reply)
    assert max(endpoints) == f.bound['result']['offset'] + f.bound['result']['bytes']
    logical_finish(f)
    return {'transient_refusal': True, 'settled_retry_exit': 0, 'permanent_failure': False}


CASES = {'r2_collision': r2_collision, 'r2_distinct': r2_distinct, 'r2_settled': r2_settled,
         'r2_missing': r2_missing, 'r2_active_ambiguity': r2_active_ambiguity, 'r2_early_gap': r2_early_gap,
         'r2_integrity': r2_integrity, 'r2_bad_original': r2_bad_original, 'r2_record_bounds': r2_record_bounds,
         'r2_byte_frame_bounds': r2_byte_frame_bounds, 'r2_read_race': r2_read_race,
         'retry_response': retry_response, 'retry_legal_use': retry_legal_use, 'retry_large_tail': retry_large_tail,
         'alternate_bind_occurrence': alternate_bind_occurrence, 'missing_original_completion': missing_original_completion,
         'original_response_failure': original_response_failure, 'original_call_custody': original_call_custody,
         'early_scan_response_gap': early_scan_response_gap, 'completed_prefix_boundary': completed_prefix_boundary,
         'retry_read_race': retry_read_race,
         'retry_scope_guards': retry_scope_guards,
         'valid': valid, 'exact_early': exact_early, 'early_after_bind_decision': early_after_bind_decision,
         'permanent_breach': permanent_breach, 'attempted_early': attempted_early, 'during_bind': during_bind,
         'non_use_traffic': non_use_traffic, 'unknown_call': unknown_call, 'missing_interval': missing_interval,
         'event_gap': event_gap, 'partial_frame': partial_frame, 'record_overflow': record_overflow,
         'byte_overflow': byte_overflow, 'prefix_change': prefix_change, 'join_revalidates': join_revalidates,
         'preflight_no_read': preflight_no_read, 'join_cannot_launder_early': join_cannot_launder_early,
         'record_read_ceiling': record_read_ceiling, 'physical_replacement': physical_replacement}


if __name__ == '__main__':
    records = []
    for name in sys.argv[3:] or CASES:
        try:
            evidence = CASES[name](); row = {'case': name, 'status': 'PASS', 'evidence': evidence}
        except Exception as exc:
            row = {'case': name, 'status': 'FAIL', 'error': str(exc), 'traceback': traceback.format_exc()}
        records.append(row)
        print(json.dumps({'case': name, 'status': row['status'],
            **({'evidence': row['evidence']} if row['status'] == 'PASS' else {'error': row['error'][:200]})}))
    (fx.SCRATCH / 'RESULTS.json').write_text(json.dumps(records, indent=2))
    raise SystemExit(1 if any(r['status'] != 'PASS' for r in records) else 0)
