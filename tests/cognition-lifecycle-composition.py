#!/usr/bin/env python3
"""Compose real value/record consumers without promoting them to host authority."""
import argparse
import ast
import copy
import contextlib
import io
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def retained_source_map_controls(source):
    """Closed value domains only; no retained record or native authority is issued."""
    route = load('retained_route_source_owner', source)
    def values(names):
        return {name: 'sha256:' + hashlib.sha256(name.encode()).hexdigest() for name in names}
    legacy4 = values(('SKILL.md', 'route-obligations.md', 'route-transaction.py', 'claim-run.sh'))
    legacy5 = {**legacy4, **values(('resolve-internal-skill.py',))}
    current12 = {**legacy5, **values(('claim-run-rotation.py', 'rotate-canonical-state.py',
        'canonical_hot_projection.py', 'canonical_custody.py', 'canonical_rotation_inputs.py',
        'read-canonical-pair.py', 'validate-run-root.sh'))}
    missing = {key: value for key, value in current12.items() if key != 'canonical_rotation_inputs.py'}
    extra = {**current12, **values(('foreign-owner.py',))}
    cases = (
        ('preserved-legacy-four', legacy4, True, True),
        ('canonical-legacy-five', legacy5, False, True),
        ('canonical-current-twelve', current12, False, True),
        ('partial-current-domain', missing, False, False),
        ('foreign-added-domain', extra, False, False),
        ('current-domain-cannot-be-preserved-legacy', current12, True, False),
    )
    for name, value, preserved, accepted in cases:
        output, code, returned = io.StringIO(), 0, None
        with contextlib.redirect_stdout(output):
            try:
                returned = route.retained_route_source_digests_v1(value, preserved)
            except SystemExit as exc:
                code = exc.code
        assert (code == 0) == accepted, (name, code, output.getvalue())
        if accepted:
            assert returned is value, name
        else:
            result = json.loads(output.getvalue())
            assert code == 2 and result['decision'] == 'PENDING' and result['advance_allowed'] is False
            assert result['error'] == 'stale unsatisfied route package source digests has the wrong shape'
        print('PASS retained-source-map-' + name)
    return len(cases)


def original14_history_no_invocation_controls(source):
    """Constructed receiving inputs must refuse before calling an unknown CLI."""
    with tempfile.TemporaryDirectory(prefix='r33-history-profile-') as raw:
        repo = Path(raw)
        scripts = repo / 'scripts'
        scripts.mkdir()
        captured = scripts / 'route-transaction.py'
        captured.write_bytes(source.read_bytes())
        (scripts / 'route_request_policy.py').write_bytes(source.with_name('route_request_policy.py').read_bytes())
        (scripts / 'claim-run.sh').write_text('# deliberately unsupported owner source\n')
        route = load('original14_history_no_invocation_owner', captured)
        run = repo / '.IMPLEMENTAUDIT/runs/history'
        run.mkdir(parents=True)
        foreign = repo / 'foreign/history'
        foreign.mkdir(parents=True)
        controller, claim = 'constructed-history', 'a' * 32
        prefix = 'refs/implementaudit/continuity-receipts/' + controller + '/'
        token = prefix + 'G0002@' + 'b' * 40
        current = prefix + 'G0003@' + 'c' * 40
        fields = ['implementaudit.continuity-receipt.v3', controller, claim,
            '.IMPLEMENTAUDIT/runs/history', 'G0002', 'd' * 40,
            'refs/implementaudit/current-generations/' + controller, 'e' * 40,
            *(['f' * 64] * 4), 'constructed action', prefix + 'G0001@' + 'a' * 40]
        original = route.subprocess.run
        calls = []

        def forbid(*args, **kwargs):
            calls.append(args)
            raise AssertionError('unsupported historical owner must not be invoked')

        route.subprocess.run = forbid
        try:
            cases = (
                ('missing-enclosing-tip', None, str(run), 'requires its enclosing current receipt'),
                ('foreign-full-root', current, str(foreign), 'identity is malformed or foreign'),
                ('unsupported-owner-profile', current, str(run), 'owner source profile is unsupported'),
            )
            for name, tip, explicit_root, error in cases:
                output, code = io.StringIO(), 0
                with contextlib.redirect_stdout(output):
                    try:
                        route.original14_retained_predecessor_v1(repo, token, fields,
                            controller=controller, claim=claim, run_identity=run.name,
                            generation='G0002', current_receipt=tip, explicit_run_root=explicit_root)
                    except SystemExit as exc:
                        code = exc.code
                result = json.loads(output.getvalue())
                assert code == 2 and result['decision'] == 'REQUIRED'
                assert result['advance_allowed'] is False and error in result['error']
                assert calls == [], (name, calls)
                assert sorted(path.name for path in run.parent.iterdir()) == ['history']
                print('PASS original14-history-' + name + '-without-owner-call')
        finally:
            route.subprocess.run = original
    return len(cases)


def retained_history_tip_forwarding_control(source):
    """Constructed structural seams; exercise real outer/inner tip forwarding."""
    route = load('retained_history_tip_forwarding_owner', source)
    controller, claim = 'constructed-tip', 'a' * 32
    repo = Path('/constructed-history-tip')
    run = str(repo / '.IMPLEMENTAUDIT/runs/example')
    prefix = 'refs/implementaudit/continuity-receipts/' + controller + '/'
    receipts = {number: prefix + f'G{number:04X}@' + str(number) * 40 for number in (1, 2, 3)}
    predecessor = {'controller_id': controller, 'claim_id': claim, 'explicit_run_root': run,
        'host_id': 'constructed-host', 'host_session_id': 'constructed-session',
        'decision': 'REQUIRED', 'route_state': 'UNSATISFIED', 'child_lifecycle_owned': False,
        'continuity_generation': 'G0001', 'continuity_receipt': receipts[1],
        'host_binding_generation': 'G0001', 'obligation_id': 'constructed-old-obligation',
        'route_transaction_id': 'constructed-old-transaction',
        'boundary': {'event_id': 'constructed-old-event', 'digest': 'sha256:' + '1' * 64}}
    retained = {**predecessor, 'continuity_generation': 'G0002', 'continuity_receipt': receipts[2],
        'host_binding_generation': 'G0002', 'obligation_id': 'constructed-retained-obligation',
        'route_transaction_id': 'constructed-retained-transaction', 'predecessor_record_oid': 'a' * 40,
        'boundary': {'event_id': 'constructed-retained-event', 'digest': 'sha256:' + '2' * 64}}
    current = {'claim_id': claim, 'explicit_run_root': run,
               'continuity_generation': 'G0003', 'continuity_receipt': receipts[3]}
    args = argparse.Namespace(controller=controller, host_id='constructed-host',
                              host_session_id='constructed-session', binding_generation='G0003')
    observed = []
    route.validate_canonical_route_record_bytes = lambda *a, **k: None
    route.candidate_request_from_record = lambda *a, **k: {}
    route.validate_route_record_semantics = lambda *a, **k: None
    route.git_blob_bytes = lambda repo, oid, *a, **k: (
        json.dumps(predecessor).encode() if oid == 'a' * 40 else b'constructed terminal receipt')
    route.canonical_ref_oid = lambda repo, ref, *a, **k: '1' * 40

    def owner_link(repo, token, **context):
        assert token == receipts[2] and context['generation'] == 'G0002'
        assert context['current_receipt'] == receipts[3], 'historical endpoint replaced live owner tip'
        assert context['explicit_run_root'] == run
        observed.append(context)
        return receipts[1]

    route.validated_v3_predecessor = owner_link
    actual_chain = route.validate_terminal_continuity_chain

    class SegmentObserved(Exception):
        pass

    def stop_after_segment(*a, **context):
        assert context['current_generation'] == 'G0002' and context['current_receipt'] == receipts[2]
        assert actual_chain(*a, **context) == [('G0001', receipts[1]), ('G0002', receipts[2])]
        raise SegmentObserved()

    route.validate_terminal_continuity_chain = stop_after_segment
    original_run = route.subprocess.run

    def forbid(*a, **k):
        raise AssertionError('constructed forwarding guard must not execute a process')

    route.subprocess.run = forbid
    try:
        try:
            route.require_active_route_recovery(repo, str(repo / '.git'), args, current, {},
                'b' * 40, retained, 'REQUIRED', 'MECHANICALLY_REQUIRED', 'new-obligation', 'new-transaction')
        except SegmentObserved:
            pass
        else:
            raise AssertionError('historical segment was not observed')
    finally:
        route.subprocess.run = original_run
    assert len(observed) == 1
    print('PASS retained-history-segment-preserves-live-owner-tip-forwarding')
    return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--governor', type=Path, default=ROOT / 'skills/implementaudit')
    parser.add_argument('--retained-source-map-only', action='store_true')
    parser.add_argument('--original14-history-only', action='store_true')
    parser.add_argument('--history-tip-forwarding-only', action='store_true')
    args = parser.parse_args()
    route_source = ROOT / 'source-peers/route-graph/skills/implementaudit/scripts/route-transaction.py'
    if args.history_tip_forwarding_only:
        count = retained_history_tip_forwarding_control(route_source)
        print(json.dumps({'controls': count, 'scope': 'CONSTRUCTED_RETAINED_SEGMENT_FORWARDING',
                          'native_authority': False}, sort_keys=True))
        return
    if args.original14_history_only:
        count = original14_history_no_invocation_controls(route_source)
        print(json.dumps({'controls': count, 'scope': 'CONSTRUCTED_ORIGINAL14_NO_INVOCATION',
                          'native_authority': False}, sort_keys=True))
        return
    count = retained_source_map_controls(route_source)
    if args.retained_source_map_only:
        print(json.dumps({'controls': count, 'scope': 'RETAINED_SOURCE_MAP_VALUES_ONLY',
                          'native_authority': False}, sort_keys=True))
        return
    count += original14_history_no_invocation_controls(route_source)
    count += retained_history_tip_forwarding_control(route_source)
    scripts = args.governor.resolve() / 'scripts'
    support = load('support_fixtures', ROOT / 'tests/evidential-support-cases.py')
    yields = load('yield_fixtures', ROOT / 'tests/nonterminal-yield-cases.py')
    terminal = load('terminal_fixtures', ROOT / 'tests/host_session_terminal.py')
    terminal.SOURCE = scripts

    def check(condition, name):
        nonlocal count
        assert condition, name
        count += 1
        print('PASS ' + name)

    with tempfile.TemporaryDirectory(prefix='r33-r37-compose-') as raw:
        root = Path(raw)
        packet = support.envelope()
        result = support.result_for(packet)

        def validate(original, returned=None, current=None):
            inputs = {'original.json': original}
            command = [sys.executable, '-B', str(scripts / 'validate-audit-implement-return.py'),
                       '--envelope', str(root / 'original.json')]
            if returned is not None:
                inputs.update({'return.json': returned, 'current.json': current})
                command += ['--result', str(root / 'return.json'), '--current-envelope', str(root / 'current.json')]
            for name, value in inputs.items():
                (root / name).write_text(json.dumps(value), encoding='utf-8')
            completed = subprocess.run(command, text=True, capture_output=True)
            return completed.returncode, json.loads(completed.stdout)

        code, value = validate(packet, result, packet)
        check(code == 0 and value['status'] == 'VALID' and value['authority'] == 'NONE'
              and 'object_closed' not in value, 'returned-support-is-value-evidence-only')
        changed = copy.deepcopy(packet)
        changed['subject']['configuration'] = 'new-configuration-after-child-return'
        code, value = validate(packet, result, changed)
        check(code == 2 and 'envelope drift' in value['error'], 'L2-post-child-drift-refuses-consumption')
        direct = copy.deepcopy(packet)
        direct['entry'] = 'DIRECT'
        check(validate(direct)[0] == 2, 'direct-entry-does-not-acquire-governed-child')
        chained = copy.deepcopy(result)
        chained['next_child'] = 'audit-andon'
        check(validate(packet, chained, packet)[0] == 2, 'child-result-cannot-route-another-child')
        cheap = copy.deepcopy(packet)
        cheap['semantic_need'] = 'ORDINARY_REVERSIBLE'
        check(validate(cheap)[1]['status'] == 'BYPASS', 'ordinary-reversible-zero-child-path')

        # Call the unchanged pending owner's actual closed value functions.
        # This does not call its authenticated mutation/admission/JOIN path.
        source = ROOT / 'source-peers/native-runtime/skills/implementaudit/scripts/compaction-audit-pending.py'
        tree = ast.parse(source.read_bytes())
        names = {'Refusal', 'require', 'canonical', 'digest', 'blank', 'add_observation',
                 'outstanding', 'scope_owners', 'available_scope', 'decision'}
        nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
        assert {n.name for n in nodes} == names
        namespace = {'json': json, 'hashlib': hashlib}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                if node.targets[0].id in {'CEILING', 'SCHEMA'}:
                    namespace[node.targets[0].id] = ast.literal_eval(node.value)
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), namespace)
        pending = namespace['blank']('same-session')
        namespace['add_observation'](pending, 'physical-b1', 'COMPLETED_RESUMED_BOUNDARY',
                                     {'currentness': 'UNRESOLVED', 'measured_epoch': None})
        for stage in ('RETURNED', 'ACCEPTED'):
            pending['assignments']['child-1'] = {
                'scope': [{'id': 'physical-b1', 'version': 1, 'kind': 'COMPLETED_RESUMED_BOUNDARY'}],
                'stage': stage, 'result': result}
            decision = namespace['decision'](pending)
            check(decision['audit_state_required'] and decision['decision'] == 'WAIT_EXISTING_AUDIT'
                  and decision['effect_authority'] is False,
                  'success-shaped-' + stage + '-without-JOIN-retains-obligation')

        def yield_record(name, changes=None, suffix=''):
            run = yields.write_case(root / name, changes, suffix=suffix)
            before = yields.inventory(run)
            completed = subprocess.run(['bash', str(scripts / 'validate-run-root.sh'),
                                        '--nonterminal-yield', str(run)], text=True, capture_output=True)
            assert before == yields.inventory(run), 'record consumer mutated evidence'
            return completed

        open_yield = yield_record('open-after-return')
        check(open_yield.returncode == 0 and 'source-only' in open_yield.stdout,
              'truthful-open-yield-after-child-is-not-closure')
        for marker in ('AUDIT_COMPLETE', 'IMPLEMENTAUDIT_RUN_COMPLETE', 'AUDIT_HANDOFF', 'ANDON_HANDOFF'):
            check(yield_record('claim-' + marker, suffix='\n' + marker + '\n').returncode != 0,
                  'child-success-cannot-launder-' + marker + '-through-yield')
        check(yield_record('abandonment', {'Next action': 'none'}).returncode != 0,
              'TY6-bare-abandonment-is-not-yield')

        # The selected live Stop adapter still refuses native effect claims.
        # Its existing test owner denies scans, processes and writes during main.
        case = terminal.TerminalTests('test_absent_physical_data_zero_scan')
        case.setUp()
        try:
            unbound = case.invoke('UNBOUND')
            check(unbound['disposition'] == 'NO_ACTIVE_AUDIT_OBJECT', 'unbound-host-cheap-path')
            if os.name == 'posix':
                case.init()
                bound = case.bind()
                assert bound.returncode == 0, bound.stdout + bound.stderr
                for message in ('AUDIT_COMPLETE', 'Child returned SUPPORTED; no JOIN is present.', None):
                    case.event['last_assistant_message'] = message
                    output = case.invoke('UNAVAILABLE')
                    check(output['reason'] == 'UNSUPPORTED_HOST_EFFECT_AUTHENTICATION'
                          and output['effect_accepted'] is False,
                          'bound-stop-does-not-promote-' + ('forced-end' if message is None else message))
        finally:
            case.doCleanups()
    print(json.dumps({'controls': count, 'result': 'PASS', 'scope': 'PORTABLE_COMPOSITION_ONLY',
                      'native_activation': 'UNPROVED', 'native_JOIN_consumption': 'UNPROVED'}, sort_keys=True))


if __name__ == '__main__':
    main()
