"""Ordinary G2 host integration, called only by the immutable full adapter.

This module never chooses a historical nine-case replay or a G1/G3 route.
Actual owner calls remain inside the admitted host's existing process custody.
"""
import os
from pathlib import Path
import re
import time

H = _HOST_ADAPTER
U = _HOST_UTILITY
E = _HOST_EVIDENCE_IO
P = _G2_NATIVE_PROFILE
A = _G2_NATIVE_ADMISSION
N = _G2_NATIVE_RECEIVER
C = _G2_CURRENT_HOST
need = H.need
DIRECTORY = Path(H.__file__).parent
HISTORICAL_COMMIT = '3e0f4b6d05eb086017ce721d40459fdbd68714dd'
HISTORICAL_TREE = 'f8741d0293ce2fd1b4b2b2e9dfa1e28d153cd81a'
STATUSES = ('NOT_ASSESSED', 'CURRENT_CHANGED_PREDICATES_REQUIRED', 'CHANGED_HOST_APPLICABILITY_UNRECEIVED',
            'CURRENT_NATIVE_STARTED', 'CURRENT_NATIVE_PASSED_UNRECEIVED', 'CURRENT_NATIVE_FAILED_UNRECEIVED',
            'RECEIVED_CURRENT_CHANGED_NATIVE_PREDICATES', 'RECEIVED_FAILED_CURRENT_NATIVE_EVIDENCE')
DISPOSITIONS = ('VALIDATED_NINE_CASES_UNRECEIVED', 'NOT_OBSERVED', 'UNRECEIVED_INVALID_OR_INCOMPLETE', 'VALIDATED_TWO_CASES_UNRECEIVED',
                'RECEIVED_CURRENT_CHANGED_NATIVE_PREDICATES', 'RECEIVED_FAILED_CURRENT_NATIVE_EVIDENCE')


def request_admission(host, episode):
    need(C.hex64(H.CURRENT_HOST_REQUEST_SHA), 'G2_CURRENT_HOST_REQUEST_UNISSUED')
    raw = E.read_packet(DIRECTORY.parent / 'dg16-r5-full-g2-decisions/CURRENT_HOST_QUALIFICATION_REQUEST.json', 16384)
    return C.validate_request(raw, H.CURRENT_HOST_REQUEST_SHA,
        C.source_bindings(H, N.PROBE_SHA256, N.APPLICABILITY_SHA), host, episode)


def admit_host(state, host, source, output, step):
    native = state['native']
    need(native['requirement'] is not None, 'NATIVE_REQUIREMENT_MISSING')
    if native['requirement']['host_exact_match']:
        return
    admitted = request_admission(host, state['context'])
    if native['current_host_request'] is None:
        need(step == 'provision', 'G2_CURRENT_HOST_MISSING_PRE_SETUP_ADMISSION')
        native['current_host_request'] = E.parse(E.encode(admitted))
    else:
        C.require_same_admission(native['current_host_request'], admitted)
    if step in ('pair', 'receive', 'prepare-review', 'hold') or (step == 'finalize' and not state['failed']):
        need(native['receiving'] is not None and native['body_receiving'] is not None
             and native['receiving']['eligible_for_full_pair'] is True,
             'G2_CURRENT_HOST_FRESH_RECEIVING_REQUIRED')
        qualified = native['body_receiving'].get('current_host_qualification')
        C.validate_earned(qualified, admitted, native['result'])


def history():
    raw = E.read_packet(DIRECTORY / 'EARNED_NATIVE_PREREQUISITE_04.json', 16384)
    need(E.sha(raw) == H.PREREQUISITE_SHA, 'EARNED_PREREQUISITE_DIGEST_REFUSED')
    value = E.parse(raw)
    need(value['schema'] == 'dg16.native-bank-earned-prerequisite.v2' and value['run_id'] == '42123891532'
         and value['tests_run'] == 9 and value['native_receiving']['status'] == 'RECEIVED_AT_DECLARED_SCOPE'
         and value['selected_source_commit'] == HISTORICAL_COMMIT and value['selected_source_tree'] == HISTORICAL_TREE
         and value['overall_closing_currentness_verified_before_teardown'] is False
         and value['receipt_transfer_authority'] is False and value['new_controller_required'] is True,
         'G2_NATIVE_HISTORICAL_RECORD_CHANGED')
    return value


def applicability(source):
    raw = E.read_packet(DIRECTORY / 'NATIVE_SOURCE_APPLICABILITY.json', 65536)
    need(E.sha(raw) == N.APPLICABILITY_SHA, 'G2_NATIVE_APPLICABILITY_BODY_PIN')
    value = E.parse(raw)
    observed = N.source_applicability(source, value)
    retained_raw = E.read_packet(DIRECTORY / 'UNCHANGED_BANK_SOURCE_CLOSURE.json', 65536)
    need(E.sha(retained_raw) == H.NATIVE_CLOSURE_SHA, 'NATIVE_CLOSURE_MANIFEST_CHANGED')
    retained = E.parse(retained_raw)
    rule = retained['population_rule']
    physical = set(rule['exact_files'])
    for prefix in rule['whole_subtrees']:
        canonical_prefix = E.safe_name(prefix.removesuffix('/'))
        need(prefix in (canonical_prefix, canonical_prefix + '/'), 'NATIVE_CLOSURE_DIRECTORY_REFUSED')
        root = source / canonical_prefix
        need(root.resolve(strict=True) == root and root.is_dir(), 'NATIVE_CLOSURE_DIRECTORY_REFUSED')
        for parent, dirs, files in os.walk(root, followlinks=False):
            for name in dirs:
                path = Path(parent) / name
                need(path.is_dir() and not path.is_symlink(), 'NATIVE_CLOSURE_DIRECTORY_REFUSED')
            physical.update((Path(parent) / name).relative_to(source).as_posix() for name in files)
    need(physical == set(observed) and len(observed) == 89, 'NATIVE_CLOSURE_POPULATION_REFUSED')
    return dict(manifest_sha256=N.APPLICABILITY_SHA, historical_manifest_sha256=H.NATIVE_CLOSURE_SHA,
        exact_directory_population=True, file_count=89, total_bytes=sum(v['bytes'] for v in observed.values()),
        unchanged_members=86, changed_members=3, all_89_equal=False,
        unchanged_consumed_closure=False, applicability='REVIEWED_LINUX_SEMANTICS_PLUS_ACTUAL_CHANGED_PREDICATES_REQUIRED')


def requirement(host, source):
    earned = history()
    fields = P.compare_historical(host, earned['host_prerequisite'])
    closure = applicability(source)
    need(closure['total_bytes'] == 3200688, 'G2_NATIVE_CURRENT_CLOSURE_BYTES')
    observed = P.validate_host(host)
    return dict(schema='dg16.g2-current-native-requirement.v1', authority='NONE', profile=P.PROFILE,
        historical_run_id=earned['run_id'], historical_source_commit=earned['historical_source_commit'],
        historical_source_tree=earned['historical_source_tree'], selected_source_commit=H.SOURCE_COMMIT,
        selected_source_tree=H.SOURCE_TREE, source_exact_match=False, host_exact_match=all(fields.values()),
        host_field_matches=fields, observed_native_profile_sha256=E.sha(E.encode(observed)),
        historical_native_profile_sha256=E.sha(E.encode(earned['host_prerequisite'])),
        source_dependency_applicability=closure, historical_overall_closing_currentness=False,
        requires_fresh_changed_predicates=True, whole_nine_replay_selected=False,
        changed_host_requires_separate_qualification=not all(fields.values()), historical_receipt_transfer=False)


def bindings():
    return dict(source_commit=H.SOURCE_COMMIT, source_tree=H.SOURCE_TREE,
        source_manifest_sha256=H.MANIFEST_SHA, source_applicability_sha256=N.APPLICABILITY_SHA,
        profile_sha256=H.NATIVE_PROFILE_SHA, probe_sha256=N.PROBE_SHA256,
        native_receiver_sha256=H.NATIVE_RECEIVER_SHA, native_admission_sha256=H.NATIVE_ADMISSION_SHA,
        adapter_sha256=E.sha(E.read_packet(Path(H.__file__), 256 * 1024)),
        pair_driver_sha256=H.PAIR_DRIVER_SHA, utility_sha256=H.UTILITY_SHA,
        policy_sha256=H.POLICY_SHA, receiver_inputs_sha256=H.RELATION_INPUTS_SHA,
        historical_prerequisite_sha256=H.PREREQUISITE_SHA)


def admission():
    return A.read(DIRECTORY.parent / 'dg16-r5-full-g2-decisions', bindings(), history()['host_prerequisite'])


def source_custody(state, source, output):
    need(H.identities(source) == state['source_directory_identity']
         and H.identities(source / '.git') == state['git_directory_identity']
         and H.identities(output) == state['output_directory_identity'], 'G2_NATIVE_CHECKOUT_IDENTITY_CHANGED')
    return dict(source=state['source_directory_identity'], git=state['git_directory_identity'],
        output=state['output_directory_identity'], source_ancestors=E.ancestors(source / 'skills'),
        private_ancestors=E.ancestors(output / 'private/episode.json'),
        workflow_context=state['context'])


def capture(state, output, label, argv, seconds=90):
    """Bind actual capture output and argv privately, including refused calls."""
    rows = state['native_commands']
    need(len(rows) < H.NATIVE_COMMAND_COUNT and time.monotonic() < state['deadline_monotonic'],
         'NATIVE_COMMAND_RECORD_BOUND')
    ordinal = len(rows)
    prefix = 'native-command-%03d' % ordinal
    failure = None
    try:
        rc, out, err = U.capture('current-native-' + label, argv, rows,
            state['deadline_monotonic'], seconds=seconds)
    except U.Refusal as exc:
        failure = exc
        observed = getattr(exc, 'captured', None)
        if observed is None:
            # The utility can refuse before returning owned stream bytes. Its
            # metadata remains evidence, but zero bytes would be an invented
            # complete stream. Preserve only what was actually returned.
            need(len(rows) in (ordinal, ordinal + 1), 'G2_NATIVE_CAPTURE_RECORD_MISSING')
            if len(rows) == ordinal + 1:
                row = E.parse(E.encode(rows[-1]))
                row.update(argv=argv, stream_retention='UNAVAILABLE_FROM_CAPTURE_EXCEPTION')
                E.write_once(output / 'private' / (prefix + '.capture.json'), E.encode(row), 128 * 1024)
                H.native_commands_summary(state)
            raise
        rc, out, err = observed['returncode'], observed['stdout'], observed['stderr']
    need(len(rows) == ordinal + 1, 'G2_NATIVE_CAPTURE_RECORD_MISSING')
    row = E.parse(E.encode(rows[-1]))
    row.update(argv=argv, stdout_private=prefix + '.stdout', stderr_private=prefix + '.stderr')
    for stream, raw in (('stdout', out), ('stderr', err)):
        E.write_once(output / 'private' / row[stream + '_private'], raw, 32768)
    E.write_once(output / 'private' / (prefix + '.capture.json'), E.encode(row), 128 * 1024)
    H.native_commands_summary(state)
    if failure is not None:
        failure.native_capture = row
        failure.native_streams = (rc, out, err)
        raise failure
    return rc, out, err, row


def live_view(state, source, output, label):
    """Fresh maintained owner, full source, runtime, host/tool and admission."""
    need(state['receipt'] is not None and state['runtime'] is not None, 'G2_NATIVE_CURRENT_CONTROLLER_REQUIRED')
    tools, host = H.inventory(U)
    P.validate_host(host)
    need(host == state['bound_host'], 'HOST_TOOLCHAIN_CHANGED')
    current_requirement = requirement(host, source)
    need(current_requirement == state['native']['requirement'], 'NATIVE_REQUIREMENT_CHANGED')
    if not current_requirement['host_exact_match']:
        C.require_same_admission(state['native']['current_host_request'], request_admission(host, state['context']))
    closure = H.verify_source(source, H.read_manifest(U), U, True)
    need(closure == state['docs']['SOURCE.json']['before'], 'NATIVE_FULL_SOURCE_CLOSURE_DIFFERS')
    runtime = H.runtime_snapshot(source, state, U)
    need(runtime == state['runtime'], 'CLAIMED_RUNTIME_CHANGED')
    received_admission, payload = admission()
    need(received_admission == state['native_admission'], 'NATIVE_ACTUAL_ADMISSION_CHANGED')
    need(H.actual_policy_adoption(U) == state['policy_adoption'], 'POLICY_ADOPTION_CHANGED_BEFORE_PAIR')
    custody = source_custody(state, source, output)
    argv = [tools['bash'], str(source / H.OWNER), '--require-current-continuity', state['controller']]
    rc, out, err, row = capture(state, output, label, argv)
    need(rc == 0 and not err and out.decode('ascii').strip() == state['receipt'], 'CURRENT_RECEIPT_CHANGED')
    view = dict(controller=state['controller'], source_commit=H.SOURCE_COMMIT, source_tree=H.SOURCE_TREE,
        receipt=state['receipt'], host=host, source_closure=closure, source_custody=custody,
        admission=received_admission, runtime_sha256=E.sha(E.encode(runtime)), scope='CURRENT_G0001_ORDINARY_G2')
    return view, row, payload


def context(state, source, output, view):
    value = dict(controller=state['controller'], initial_receipt=state['receipt'],
        probe_path=str(DIRECTORY / 'native_probe.py'), python_path=view['host']['tools']['python3']['canonical'],
        bash_path=view['host']['tools']['bash']['canonical'], admission_bindings=bindings(),
        historical_profile=history()['host_prerequisite'], source_closure=view['source_closure'],
        source_custody=view['source_custody'], runtime_sha256=view['runtime_sha256'])
    if state['native']['current_host_request'] is not None:
        value['current_host_request'] = state['native']['current_host_request']
    return value


def summary_capture(row):
    return dict(primary_returncode=row.get('returncode'), streams_complete=row.get('streams_complete', False),
        stdout_bytes=row.get('stdout_bytes', 0), stdout_sha256=row.get('stdout_sha256', E.sha(b'')),
        stderr_bytes=row.get('stderr_bytes', 0), stderr_sha256=row.get('stderr_sha256', E.sha(b'')))


def observe_raw(native, output):
    native['result_disposition'] = 'UNRECEIVED_INVALID_OR_INCOMPLETE'
    try:
        _result, _raw, observed = N.observe_result(output / 'private/native-run')
    except (E.Refusal, OSError, ValueError, TypeError, KeyError):
        return None
    native['result'] = observed
    native['result_disposition'] = ('VALIDATED_NINE_CASES_UNRECEIVED' if observed['schema'] == C.OBSERVED_SCHEMA else 'VALIDATED_TWO_CASES_UNRECEIVED')
    return observed


def receipt(native, currentness_sha256):
    record = native['body_receiving']
    need(type(record) is dict, 'G2_NATIVE_BODY_RECEIVING_REQUIRED')
    qualified = record['eligible_for_full_pair'] and native['started'] and native['capture_custody_accepted']
    qualified = qualified and native['currentness_before_bank'] and native['currentness_after_bank']
    qualified = qualified and native['result'] is not None and native['result']['success']
    need(qualified == record['eligible_for_full_pair'], 'G2_NATIVE_RECEIVING_STATE_CHANGED')
    result = dict(schema='dg16.full-registry-current-native-receiving.v2', authority='NONE', profile=P.PROFILE,
        status=record['status'], source_commit=H.SOURCE_COMMIT, source_tree=H.SOURCE_TREE,
        receipt_transfer_authority=False, while_same_checkout_current=True,
        requirement_sha256=E.sha(H.canonical(native['requirement'])),
        native_result_sha256=E.sha(H.canonical(native['result'])),
        body_receiving_sha256=E.sha(E.encode(record)), currentness_sha256=currentness_sha256,
        actual_case_count=native['result']['tests_run'], expected_case_count=(9 if native['current_host_request'] is not None else 2), expected_predicate_count=5,
        eligible_for_full_pair=qualified, eligible_delta='EXACT_CURRENT_NATIVE_PREREQUISITE_ONLY_NO_ORIGINAL_AWARD',
        original_acceptance=False, G1=False, C5=False, full_G2=False, G3=False, full_T14=False)
    if native['current_host_request'] is not None:
        current = record.get('current_host_qualification')
        if qualified:
            C.validate_earned(current, native['current_host_request'], native['result'])
        else:
            need(current is None, 'G2_CURRENT_HOST_FAILED_QUALIFICATION_PRESENT')
        result['current_host_qualification_sha256'] = E.sha(E.encode(current)) if current is not None else None
    return result


def verify_current(state, source, output):
    native = state['native']
    need(native['receiving'] is not None and native['context'] is not None, 'G2_NATIVE_BODY_RECEIVING_REQUIRED')
    def fresh():
        return live_view(state, source, output, 'receiving-live-readback')[0]
    actual = N.receive(output / 'private', source, native['context'], fresh)
    need(actual == native['body_receiving'] and actual['eligible_for_full_pair'], 'CURRENT_NATIVE_PREREQUISITE_NOT_RECEIVED')
    return actual


def operation(step, state, source, output):
    native, private = state['native'], output / 'private'
    need(native['requirement'] is not None, 'NATIVE_REQUIREMENT_MISSING')
    if not native['requirement']['host_exact_match']:
        C.require_same_admission(native['current_host_request'], request_admission(state['bound_host'], state['context']))
    support = private / 'native-prerequisite'
    if step == 'native-bank':
        need(not native['started'] and native['receiving'] is None and not support.exists()
             and not (private / 'native-run').exists(), 'NATIVE_NO_REPEAT')
        view, before, payload = live_view(state, source, output, 'before-focused-probe')
        native['context'] = context(state, source, output, view)
        support.mkdir(mode=0o700)
        for name, value in [('HOST.json', view['host']), ('SOURCE_CLOSURE.json', view['source_closure']),
                            ('SOURCE_CUSTODY.json', view['source_custody']), ('ADMISSION.json', view['admission']),
                            ('BEFORE_CURRENTNESS.json', before)]:
            E.write_once(support / name, E.encode(value))
        if native['current_host_request'] is not None:
            request_raw = E.read_packet(DIRECTORY.parent / 'dg16-r5-full-g2-decisions/CURRENT_HOST_QUALIFICATION_REQUEST.json', 16384)
            need(E.sha(request_raw) == H.CURRENT_HOST_REQUEST_SHA, 'G2_CURRENT_HOST_REQUEST_PIN')
            E.write_once(support / 'CURRENT_HOST_QUALIFICATION_REQUEST.json', request_raw, 16384)
        E.write_once(support / 'SOURCE_APPLICABILITY.json', E.read_packet(DIRECTORY / 'NATIVE_SOURCE_APPLICABILITY.json', 65536))
        for name, raw in payload.items(): E.write_once(support / name, raw, 65536)
        native['currentness_before_bank'] = True
        native['started'], native['status'] = True, 'CURRENT_NATIVE_STARTED'
        argv = N.native_invocation(DIRECTORY / 'native_probe.py', source, private / 'native-run', native['context']['python_path'],
            current_host_bank=native['current_host_request'] is not None)
        try:
            rc, out, err, captured = capture(state, output, 'two-maintained-cases', argv, H.NATIVE_BANK_SECONDS)
        except U.Refusal as exc:
            if hasattr(exc, 'native_capture'):
                E.write_once(support / 'CAPTURE.json', E.encode(exc.native_capture), 128 * 1024)
                native['capture_observation'] = summary_capture(exc.native_capture)
                observe_raw(native, output)
            native['status'] = 'CURRENT_NATIVE_FAILED_UNRECEIVED'
            raise
        E.write_once(support / 'CAPTURE.json', E.encode(captured), 128 * 1024)
        native['capture_observation'] = summary_capture(captured)
        native['capture_custody_accepted'] = True
        observed = observe_raw(native, output)
        after_view, after, _payload = live_view(state, source, output, 'after-focused-probe')
        E.write_once(support / 'AFTER_CURRENTNESS.json', E.encode(after))
        need(after_view == view, 'NATIVE_LIVE_CLOSING_CHANGED')
        native['currentness_after_bank'] = True
        native['status'] = 'CURRENT_NATIVE_FAILED_UNRECEIVED'
        need(observed is not None and rc == 0 and not err and observed['success'], 'G2_NATIVE_TWO_CASES_NOT_QUALIFIED')
        native['status'] = 'CURRENT_NATIVE_PASSED_UNRECEIVED'
    elif step == 'native-receive':
        need(native['started'] and native['capture_custody_accepted'] and native['result'] is not None
             and native['context'] is not None, 'NATIVE_CAPTURE_CUSTODY_NOT_ELIGIBLE')
        need(native['receiving'] is None and native['body_receiving'] is None, 'NATIVE_NO_REPEAT_RECEIVING')
        latest = []
        def fresh():
            view, row, _payload = live_view(state, source, output, 'receive-focused-raw')
            latest.append(row)
            return view
        body = N.receive(private, source, native['context'], fresh, create=True)
        need(len(latest) == 2, 'G2_NATIVE_RECEIVING_LIVE_BOOKENDS')
        native['body_receiving'] = body
        currentness = E.read(private / latest[-1]['stdout_private'], 32768)
        E.write_once(private / 'native-receiving-currentness.stdout', currentness, 512)
        received = receipt(native, E.sha(currentness))
        E.write_once(private / 'live-current-native-receiving.json', H.canonical(received), 16384)
        native['receiving'] = received
        native['status'] = native['result_disposition'] = received['status']
        native['eligible_for_full_pair'] = received['eligible_for_full_pair']
        need(native['eligible_for_full_pair'], 'G2_NATIVE_TWO_CASES_NOT_QUALIFIED')
    else:
        raise H.Refusal('UNKNOWN_NATIVE_STEP')


def projection(state, output, verify_private=False):
    native = state['native']
    base = set(H.new_native_state())
    need(type(native) is dict and base <= set(native) <= base | {'capture_observation'}, 'NATIVE_STATE_KEYS_REFUSED')
    need(native['status'] in STATUSES and native['result_disposition'] in DISPOSITIONS, 'NATIVE_STATUS_REFUSED')
    for name in ('started', 'capture_custody_accepted', 'currentness_before_bank', 'currentness_after_bank',
                 'eligible_for_full_pair', 'closing_currentness_verified_before_teardown'):
        need(type(native[name]) is bool, 'NATIVE_BOOLEAN_REFUSED')
    if native['requirement'] is not None:
        need(state['bound_host'] is not None and native['requirement'] == requirement(state['bound_host'], Path(state['source_path'])),
             'NATIVE_REQUIREMENT_READBACK_CHANGED')
    captured = native.get('capture_observation')
    if captured is not None:
        need(type(captured) is dict and set(captured) == {'primary_returncode', 'streams_complete',
             'stdout_bytes', 'stdout_sha256', 'stderr_bytes', 'stderr_sha256'}
             and (captured['primary_returncode'] is None or type(captured['primary_returncode']) is int)
             and type(captured['streams_complete']) is bool, 'NATIVE_CAPTURE_SHAPE_REFUSED')
        for stream in ('stdout', 'stderr'):
            need(type(captured[stream + '_bytes']) is int and 0 <= captured[stream + '_bytes'] <= 32768
                 and type(captured[stream + '_sha256']) is str and re.fullmatch('[0-9a-f]{64}', captured[stream + '_sha256']),
                 'NATIVE_CAPTURE_BOUND')
        if verify_private:
            row = E.parse(E.read(output / 'private/native-prerequisite/CAPTURE.json'))
            need(summary_capture(row) == captured, 'NATIVE_CAPTURE_READBACK_CHANGED')
            for stream in ('stdout', 'stderr'):
                body = E.read(output / 'private' / E.safe_name(row[stream + '_private']), 32768)
                need(N.descriptor(body) == {'bytes': captured[stream + '_bytes'], 'sha256': captured[stream + '_sha256']},
                     'NATIVE_CAPTURE_READBACK_CHANGED')
    else:
        need(native['result'] is None and not native['capture_custody_accepted'], 'NATIVE_CAPTURE_MISSING')
    if native['result'] is not None:
        _value, _raw, observed = N.observe_result(output / 'private/native-run')
        need(observed == native['result'], 'NATIVE_RESULT_READBACK_CHANGED')
    received = native['receiving']
    if received is not None:
        need(native['body_receiving'] is not None and native['context'] is not None
             and type(received.get('currentness_sha256')) is str
             and re.fullmatch('[0-9a-f]{64}', received['currentness_sha256'])
             and received == receipt(native, received['currentness_sha256']), 'NATIVE_RECEIPT_SCOPE_CHANGED')
        if verify_private:
            body = N.reconsume(output / 'private', Path(state['source_path']), native['context'])
            need(body == native['body_receiving'], 'NATIVE_RETAINED_EVIDENCE_OR_RECEIVING_CHANGED')
            need(E.read(output / 'private/live-current-native-receiving.json', 16384) == H.canonical(received)
                 and E.sha(E.read(output / 'private/native-receiving-currentness.stdout', 512)) == received['currentness_sha256'],
                 'NATIVE_RECEIPT_READBACK_CHANGED')
    else:
        need(native['body_receiving'] is None, 'G2_NATIVE_ORPHAN_BODY_RECEIPT')
    need(native['eligible_for_full_pair'] == (received is not None and received['eligible_for_full_pair'] is True),
         'NATIVE_ELIGIBILITY_CHANGED')
    result = dict(schema='dg16.full-registry-current-native-prerequisite.v2', authority='NONE', profile=P.PROFILE,
        bank='tests/work-graph-original14-receiving-cases.py', expected_tests=list(C.BANK_TESTS if native['current_host_request'] is not None else N.TESTS), expected_predicates=list(N.PREDICATES),
        status=native['status'], requirement=native['requirement'], started=native['started'],
        capture_custody_accepted=native['capture_custody_accepted'], capture_observation=captured,
        result=native['result'], result_disposition=native['result_disposition'], receiving=received,
        currentness_before_bank=native['currentness_before_bank'], currentness_after_bank=native['currentness_after_bank'],
        qualified_for_pair_at_receiving=native['eligible_for_full_pair'],
        closing_currentness_verified_before_teardown=native['closing_currentness_verified_before_teardown'],
        bank_watchdog_seconds=H.NATIVE_BANK_SECONDS, elapsed_subtraction=0, command_records=H.native_commands_summary(state),
        historical_bank=dict(source_commit=history()['historical_source_commit'], source_tree=history()['historical_source_tree'],
            applicability_source_commit=HISTORICAL_COMMIT, applicability_source_tree=HISTORICAL_TREE,
            receipt_sha256=H.PREREQUISITE_SHA, tests_run=9, transferred=False),
        original_acceptance=False, full_G2=False, C5=False, G1=False, G3=False)
    if native['current_host_request'] is not None:
        result['current_host_request'] = native['current_host_request']
        result['current_host_qualification'] = None if native['body_receiving'] is None else native['body_receiving'].get('current_host_qualification')
    return result
