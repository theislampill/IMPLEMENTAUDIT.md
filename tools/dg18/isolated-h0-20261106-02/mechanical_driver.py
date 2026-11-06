"""Post-receiving driver for already-owned Native/Provider and pending scope.

No CLI entry point and no import-time effects. Root integration, independent
review, source admission and GO precede any call to run_existing(). This driver
does not allocate a native process, subject, store, grant or compaction.
"""
import hashlib
import json
from pathlib import Path
import queue
import threading


def require(ok, why):
    if not ok:
        raise ValueError(why)


def source_rows(path, maximum=2 * 1024 * 1024):
    path = Path(path)
    before = path.stat()
    require(path.resolve(strict=True) == path and before.st_nlink == 1
            and 0 < before.st_size <= maximum, 'DRIVER_SOURCE_BOUND')
    raw = path.read_bytes(); after = path.stat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'DRIVER_SOURCE_CHANGED')
    rows = []; offset = 0
    for line, wire in enumerate(raw.splitlines(keepends=True), 1):
        require(wire.endswith(b'\n'), 'DRIVER_PARTIAL_RECORD')
        row = json.loads(wire)
        rows.append({'row': row, 'locator': {'offset': offset, 'bytes': len(wire),
                    'sha256': hashlib.sha256(wire).hexdigest(), 'embedded_ordinal': row['ordinal'],
                    'physical_line': line}})
        offset += len(wire)
    return rows, {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                  'physical': {'device': before.st_dev, 'inode': before.st_ino}}


def run_existing(*, native, provider, pending, source, scope, evidence_directory, progress=None, diagnostic=None):
    """Use exact existing Native.rpc/wait_turn and Provider.route interfaces.

    `scope` must be an existing eligible COMPLETED_RESUMED_BOUNDARY version.
    The fixed source selector must already choose the reviewed new profile and
    point to this same already-owned native thread and MCP configuration.
    """
    def note(phase, completed=False):
        if progress is not None:
            progress(phase, completed)

    note('MECHANICAL_ENTRY')
    selected = source._np_selection()
    require(selected['profile_id'] == source.MECHANICAL_PROFILE
            and source.MECHANICAL_SELECTION_PIN is not None, 'ROOT_ADMITTED_MECHANICAL_SELECTION_REQUIRED')
    require(type(scope) is list and len(scope) == 1 and scope[0].get('kind') == 'COMPLETED_RESUMED_BOUNDARY',
            'ONE_EXISTING_ELIGIBLE_BOUNDARY_REQUIRED')
    fixed = selected['pending_owner']; root = selected['root_thread_id']; store = Path(fixed['store'])
    require(fixed['session_id'] == root and native.proc.poll() is None, 'EXISTING_OWNED_NATIVE_REQUIRED')
    observation = pending.OBSERVATION
    code = pending.nonprotected_code_identity()
    runtime = source._np_runtime(observation, code)
    episode = source._np_episode(runtime)
    temporary_context = {'profile_id': source.MECHANICAL_PROFILE, '_source_profile_code_pins': code}
    protocol = observation._mechanical_protocol(temporary_context)
    spawn_text = protocol.spawn_message(episode)
    parent_queue = queue.Queue(); child_queue = queue.Queue(); condition = threading.Condition()
    flow = {'child': None, 'child_requests': 0, 'closed': False}
    parent_path = Path(selected['root_source'])
    output = Path(evidence_directory)
    require(output.is_dir() and output.resolve(strict=True) == output, 'ROOT_OWNED_EVIDENCE_DIRECTORY_REQUIRED')

    def save(name, value):
        target = output / name
        require(not target.exists(), 'DRIVER_EVIDENCE_ALREADY_EXISTS')
        target.write_bytes(protocol.canonical(value) + b'\n')

    def route(request):
        thread = request.get('client_metadata', {}).get('thread_id')
        if thread == root:
            return parent_queue.get(timeout=90)
        with condition:
            require(not flow['closed'] and type(thread) is str and thread != root, 'UNEXPECTED_PROVIDER_THREAD')
            require(flow['child'] in (None, thread), 'SECOND_NATIVE_CHILD_REFUSED')
            flow['child'] = thread
            flow['child_requests'] += 1
            # Capability use is checked against the actual advertised schema.
            matches = [tool for namespace in request.get('tools', [])
                       if namespace.get('type') == 'namespace' and namespace.get('name') == protocol.NAMESPACE
                       for tool in namespace.get('tools', []) if tool.get('name') == protocol.TOOL]
            require(len(matches) == 1, 'ACTUAL_MECHANICAL_MCP_TOOL_NOT_ADVERTISED')
            condition.notify_all()
        return child_queue.get(timeout=180)

    previous_route = provider.route
    provider.route = route

    def parent_message(text):
        parent_queue.put({'text': text})
        native.rpc('turn/start', {'threadId': root, 'input': [{'type': 'text', 'text': 'Emit the next closed mechanical qualification record.'}]})
        terminal, _ = native.wait_turn(root)
        require(terminal['params']['turn']['status'] == 'completed', 'NATIVE_PARENT_TURN_FAILED')
        rows, _ = source_rows(parent_path)
        matched = []
        for record in rows:
            try:
                if protocol.public_text(record['row']) == text:
                    matched.append(record)
            except (ValueError, KeyError, TypeError):
                pass
        require(len(matched) == 1, 'ACTUAL_UNIQUE_PARENT_MESSAGE_REQUIRED')
        return matched[0]

    def operate(action, request):
        return pending.operate(store, root, fixed['owner_id'], action, request)

    try:
        note('PARENT_OPEN_MESSAGE')
        opened = parent_message('```ini\nCHILD_TASK=' + episode['logical_task'] +
                                '\nCHILD_SKILL_SELECTED=audit-state\nSTATUS=OPEN\nLOAD=UNVERIFIED\n```')
        note('PARENT_OPEN_MESSAGE', True)
        note('NATIVE_CHILD_SPAWN')
        parent_queue.put({'type': 'function', 'namespace': 'multi_agent_v1', 'name': 'spawn_agent',
                          'arguments': {'fork_context': False, 'message': spawn_text}})
        parent_queue.put({'text': 'The native mechanical child is started. Parent authorization records follow after its full LOAD.'})
        native.rpc('turn/start', {'threadId': root, 'input': [{'type': 'text', 'text': 'Start exactly the canonical mechanical child.'}]})
        terminal, _ = native.wait_turn(root)
        require(terminal['params']['turn']['status'] == 'completed', 'NATIVE_SPAWN_TURN_FAILED')
        with condition:
            require(condition.wait_for(lambda: flow['child_requests'] == 1, timeout=90), 'NATIVE_CHILD_START_UNAVAILABLE')
        rows, _ = source_rows(parent_path)
        calls = [r for r in rows if r['row']['payload'].get('type') == 'function_call'
                 and r['row']['payload'].get('namespace') == 'multi_agent_v1'
                 and r['row']['payload'].get('name') == 'spawn_agent'
                 and protocol.parse(r['row']['payload'].get('arguments')) == {'fork_context': False, 'message': spawn_text}]
        require(len(calls) == 1, 'UNIQUE_ACTUAL_SPAWN_REQUIRED')
        spawn = calls[0]
        replies = [r for r in rows if r['row']['payload'].get('type') == 'function_call_output'
                   and r['row']['payload'].get('call_id') == spawn['row']['payload']['call_id']]
        require(len(replies) == 1, 'ACTUAL_SPAWN_RESULT_REQUIRED')
        child = protocol.parse(replies[0]['row']['payload']['output'])['agent_id']
        require(child == flow['child'], 'NATIVE_PROVIDER_CHILD_DIFFERS')
        child_path = source._mechanical_child_path_v1(selected, child)
        child_rows, _ = source_rows(child_path)
        starts = [r for r in rows if r['row']['type'] == 'event_msg'
                  and r['row']['payload'].get('type') == 'task_started'
                  and r['locator']['offset'] < opened['locator']['offset']]
        require(starts and child_rows[1]['row']['payload'].get('type') == 'task_started', 'ACTUAL_ACTIVATION_REQUIRED')
        nominations = {'open': opened['locator'], 'spawn_call': spawn['locator'], 'spawn_output': replies[0]['locator'],
                       'child_activation': child_rows[1]['locator'], 'parent_turn_start': starts[-1]['locator']}
        note('NATIVE_CHILD_SPAWN', True)
        note('EXACT_RESERVATION')
        reserved = operate('reserve', {'child_id': child, 'bounded_purpose': 'Closed actual selected-prior and exact BIND retry qualification',
                                       'observation_source': nominations, 'scope': scope})
        save('RESERVED.json', reserved)
        note('EXACT_RESERVATION', True)

        def assignment():
            return pending.load(store, root)['assignments'][child]

        def child_operation(operation, request):
            stage = 'ARGUMENTS'; args = None; records = []; call = None; results = []
            try:
                stage = 'ARGUMENTS'
                args = protocol.arguments(source.MECHANICAL_SELECTION_PIN['sha256'], operation, request)
                stage = 'WAIT_COMPLETION'
                before = flow['child_requests']
                child_queue.put({'type': 'function', 'namespace': protocol.NAMESPACE, 'name': protocol.TOOL, 'arguments': args})
                with condition:
                    require(condition.wait_for(lambda: flow['child_requests'] == before + 1, timeout=90), 'NATIVE_MECHANICAL_CALL_DID_NOT_COMPLETE')
                stage = 'SOURCE_ROWS'
                records, _ = source_rows(child_path)
                stage = 'CALL_SELECTION'
                calls = [r for r in records if protocol.is_call(r['row']['payload'])
                         and r['row']['payload'].get('arguments') == protocol.arguments_wire(args)]
                require(calls, 'ACTUAL_MECHANICAL_CALL_ABSENT')
                call = calls[-1]
                stage = 'OUTPUT_SELECTION'
                results = [r for r in records if protocol.is_output(r['row']['payload'])
                           and r['row']['payload'].get('call_id') == call['row']['payload']['call_id']]
                require(len(results) == 1, 'ACTUAL_MECHANICAL_COMPLETION_ABSENT')
                stage = 'CONTEXT'
                context = assignment()['observation_source']
                stage = 'COMMAND_RESPONSE'
                text, pair = observation.command_response(context, 'child', call['locator'], results[0]['locator'], protocol.arguments_wire(args))
                stage = 'RESPONSE_JSON'
                return {'call': call['locator'], 'result': results[0]['locator']}, pair, json.loads(text)
            except BaseException as error:
                if diagnostic is not None:
                    try:
                        diagnostic(protocol=protocol, observation=observation, operation=operation, arguments=args, records=records, call=call, outputs=results, stage=stage, error=error)
                    except BaseException:
                        pass  # Observation failure must not replace the real owner failure.
                raise

        def observation_chain(identifier, label):
            current = assignment(); prepared = current['prepared'][identifier]; context = current['observation_source']
            skill = pending.selected_audit_state_pin()
            note(label + '_LOAD')
            load, load_pair, loaded = child_operation('LOAD', skill)
            require({k: loaded[k] for k in ('path', 'bytes', 'sha256')} == skill, 'FULL_SKILL_LOAD_REQUIRED')
            note(label + '_LOAD', True)
            note(label + '_AUTHORIZATION')
            route_record = parent_message('```ini\nCHILD_TASK=' + episode['logical_task'] +
                                          '\nCHILD_SKILL_ROUTE=audit-state\nLOAD=VERIFIED\nOBSERVATION_ID=' + identifier + '\n```')
            value = {'schema': 'implementaudit.compaction-use-authorization.v1',
                     'action': 'AUTHORIZE_BOUNDED_POST_COMPACTION_RECONCILIATION',
                     'parent_identity': prepared['obligation']['parent_identity'],
                     'actual_child_identity': prepared['obligation']['actual_child_identity'],
                     'obligation_digest': prepared['obligation_pin']['sha256'], 'observation_id': identifier,
                     'load_observation_identity': observation.digest(observation.canonical(load_pair)),
                     'selected_child': 'audit-state', 'skill_source_pin': skill, 'authority_ceiling': 'NONE'}
            authorized = parent_message('```json\n' + observation.canonical(value).decode('utf-8') + '\n```')
            note(label + '_AUTHORIZATION', True)
            delivery = {'child_id': child, 'phase': 'deliver', 'observation_id': identifier,
                        'authorization_evidence': {'load_call': load['call'], 'load_output': load['result'],
                                                   'route': route_record['locator'], 'authorization': authorized['locator']}}
            note(label + '_DELIVER')
            exchange, _, _ = child_operation('DELIVER', delivery)
            note(label + '_DELIVER', True)
            bind_request = {'child_id': child, 'phase': 'bind', 'observation_id': identifier, 'exchange': exchange}
            note(label + '_BIND')
            bound, pair, response = child_operation('BIND', bind_request)
            note(label + '_BIND', True)
            return bind_request, bound, pair, response

        prior_id = reserved['obligation']['observation_id']
        prior_request, prior_bind, prior_pair, prior_response = observation_chain(prior_id, 'PRIOR')
        note('PRIOR_EXACT_RETRY')
        retry_bind, retry_pair, retry_response = child_operation('BIND', prior_request)
        require(retry_response == prior_response and retry_pair['call'] != prior_pair['call'], 'ACTUAL_SUPPORTED_RETRY_REQUIRED')
        note('PRIOR_EXACT_RETRY', True)
        note('CURRENT_PREPARATION')
        current_preparation = operate('observe-child', {'child_id': child, 'phase': 'prepare'})
        current_id = current_preparation['obligation']['observation_id']
        current = assignment()
        require(current['prepared'][current_id]['observation']['revision'] > current['prepared'][prior_id]['observation']['revision'],
                'STRICTLY_LATER_OWNER_REVISION_REQUIRED')
        note('CURRENT_PREPARATION', True)
        current_request, current_bind, _, _ = observation_chain(current_id, 'CURRENT')
        current = assignment(); prepared = current['prepared'][current_id]
        note('SELECTED_OCCURRENCES_EXPORT')
        exported = observation.export_selected_occurrences(
            current['observation_source'], prepared, prepared['exchange'], current_request,
            store, root, fixed['owner_id'], prior_context=pending.prior_history_context(current, current_id))
        classes = sorted((r['population'], r['attempt_class'], r['semantic'], r['completion']) for r in exported['occurrences'])
        expected = sorted([('CURRENT', 'ORIGINAL', semantic, 'COMPLETED') for semantic in ('LOAD', 'EXCHANGE', 'BIND')] +
                          [('PRIOR', 'ORIGINAL', semantic, 'COMPLETED') for semantic in ('LOAD', 'EXCHANGE', 'BIND')] +
                          [('PRIOR', 'RETRY', 'BIND', 'COMPLETED')])
        require(classes == expected and current['return'] is None and current['join'] is None,
                'EXACT_PRIOR_RETRY_PREDICATE_NOT_ESTABLISHED')
        note('SELECTED_OCCURRENCES_EXPORT', True)
        result = {'schema': 'r5.h0-prior-candidate.native-mechanical-result.v1',
                  'status': 'MECHANICAL_PREDICATE_OBSERVED_PENDING_ROOT_RECEIVING',
                  'observation_p': prior_id, 'observation_c': current_id,
                  'original_p_bind': prior_bind, 'retry_p_bind': retry_bind, 'original_c_bind': current_bind,
                  'export': exported, 'public_return': None, 'public_join': None,
                  'result_consumer': 'UNQUALIFIED', 'provider': 'DETERMINISTIC_EMULATION',
                  'independent_cognition': False, 'original_acceptance': False, 'authority_ceiling': 'NONE'}
        save('MECHANICAL_RESULT.json', result)
        save('PENDING_MECHANICAL_FINAL.json', pending.load(store, root))
        note('CHILD_TERMINAL')
        child_queue.put({'text': 'The closed mechanical qualification has ended. No cognition, RETURN, JOIN or original acceptance is asserted.'})
        # Native.wait_turn filters by the selected thread, as in the retained harness.
        child_terminal, _ = native.wait_turn(child)
        require(child_terminal['params']['turn']['status'] == 'completed', 'NATIVE_CHILD_TERMINAL_FAILED')
        note('CHILD_TERMINAL', True)
        flow['closed'] = True
        save('SOURCE_PINS.json', {'parent': source_rows(parent_path)[1], 'child': source_rows(child_path)[1]})
        return result
    finally:
        provider.route = previous_route
        # Failed operations retain their real owner state and source; no replay,
        # pending reset, compensating BIND or automatic new native run occurs.
