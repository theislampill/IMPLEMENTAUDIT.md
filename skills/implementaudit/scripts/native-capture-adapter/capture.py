"""Bounded same-worker LOAD/ACK/USE capture. Default is preflight only.
Native execution belongs root within existing authorization, never this preparation run.
Raw config responses stay in bounded private run/stdout.bin; summaries use a projection.
Transport completion is not semantic/governor acceptance.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time

HERE = Path(__file__).resolve().parent
OWNER = HERE / 'process_owner.py'
OWNER_SHA = '392c5db668fbef4eff4c66f51676cf066bfbfe3def28039cbc09bfec98430949'
WORKER_RUNTIME_SHA256 = '2c2546705213e76f6148305eeb56c5b8ca93623bbb30cd8e5ca40e967fd2b873'
CAP = 1048576


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def matching_error(message, absent):
    if not isinstance(message, dict) or 'result' in message:
        return False
    error = message.get('error')
    if not isinstance(error, dict) or not isinstance(error.get('message'), str):
        return False
    # Exact 0.153.4 command/exec and thread/start rejection surfaces, bound
    # to root-threadless-03 and root-thread-metadata-01 respectively.
    # Request-id correlation remains enforced by response() before this matcher.
    suffix = f'default_permissions refers to undefined profile `{absent}`'
    expected = ('invalid permission profile: ' + suffix,
                'failed to load configuration: ' + suffix)
    return type(error.get('code')) is int and error['code'] == -32600 and error['message'] in expected


def classify_read(name, message, marker):
    result = message.get('result')
    if not isinstance(result, dict):
        return 'INCONCLUSIVE_PROTOCOL_OR_LAUNCH_ERROR'
    if not isinstance(result.get('stdout'), str) or not isinstance(result.get('stderr'), str) or type(result.get('exitCode')) is not int:
        return 'INCONCLUSIVE_INVALID_RESPONSE'
    stdout, stderr = result['stdout'].encode('utf-8'), result['stderr'].encode('utf-8')
    if name != 'allowed' and marker in stdout + stderr:
        return 'FAIL_WITH_WITNESS_READ_EXCLUSION'
    if name == 'allowed':
        return 'EXACT_ALLOWED_READ_OBSERVED' if result['exitCode'] == 0 and stdout == marker and not stderr else 'INCONCLUSIVE_POSITIVE_CONTROL'
    # The pinned PS catch emits exit 13 for a failed ReadAllBytes call. Generic
    # startup errors, missing files and transport failures must not earn credit.
    denied = b'UnauthorizedAccessException' in stderr and (b'access' in stderr.lower() and b'denied' in stderr.lower())
    if result['exitCode'] == 13 and stdout == b'' and denied:
        return 'EXCLUDED_EXISTING_MARKER_ACCESS_DENIED'
    return 'INCONCLUSIVE_NO_READ_DENIAL_WITNESS'


def worker_runtime():
    path = HERE / 'worker_runtime.py'
    expected = WORKER_RUNTIME_SHA256
    if not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
        raise ValueError('Selected worker runtime source is unbound')
    for node in (path, *path.parents):
        if node.is_symlink() or (node.exists() and getattr(node.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Aliased worker runtime source')
    if not path.is_file():
        raise ValueError('Selected worker runtime source is missing')
    raw = path.read_bytes()
    if digest(raw) != expected:
        raise ValueError('Selected worker runtime source differs')
    spec = importlib.util.spec_from_file_location('bound_worker_runtime', path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def preflight(plan_sha, *, bundle_root, pins_sha256):
    return worker_runtime().preflight(bundle_root, plan_sha, OWNER, OWNER_SHA, pins_sha256, HERE)


def load_notification_policy():
    path = HERE / 'notification_policy.py'
    spec = importlib.util.spec_from_file_location('private_notification_policy', path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module



def capture(plan_sha, run_name, *, bundle_root, pins_sha256):
    bundle_root = Path(bundle_root)
    plan, pins, helper = preflight(plan_sha, bundle_root=bundle_root, pins_sha256=pins_sha256)
    if "visibility" not in plan:
        raise ValueError("Governed capture cannot downgrade to ordinary")
    if plan['visibility'].get('load_spec',{}).get('context_contract',{}).get('scope')!='SOURCE_INPUT':
        raise ValueError('Synthetic context or unresolved context cannot enter native capture')
    runtime = worker_runtime()
    if not run_name or Path(run_name).name != run_name or run_name in ('.', '..'):
        raise ValueError('One new run directory name required')
    run = bundle_root / 'runs' / run_name
    helper.no_reparse(run)
    if run.exists():
        raise ValueError('Existing attempt: reconcile partial effects before retry')
    run.parent.mkdir(exist_ok=True)
    run.mkdir()
    helper.write_json_new(run / 'INVOCATION.json', {'plan': helper.file_record(bundle_root / 'THREAD_METADATA_PLAN.json'), 'argv': plan['server_argv'],
        'cwd': plan['server_cwd'], 'authority': 'ROOT_SELECTED_BOUNDED_WORKER_LOAD_USE', 'consumer_qualification': 'NONE',
        'wall_seconds': 60, 'raw_cap_bytes_per_stream': CAP, 'owner': helper.file_record(OWNER)})
    module_path = HERE / 'canary_protocol.py'
    module_spec = importlib.util.spec_from_file_location('owned_canary_protocol', module_path)
    module = importlib.util.module_from_spec(module_spec)
    exec(compile(module_path.read_bytes(), str(module_path), 'exec'), module.__dict__)
    visibility_path = HERE / 'load_visibility.py'
    visibility_spec = importlib.util.spec_from_file_location('owned_load_visibility', visibility_path)
    visibility = importlib.util.module_from_spec(visibility_spec)
    visibility_spec.loader.exec_module(visibility)
    staged_turns = visibility.staged_turns
    canary = (visibility.StagedProtocol(module.CanaryProtocol, plan['visibility']['load_spec'])
              if 'visibility' in plan else module.CanaryProtocol())
    policy_module = load_notification_policy()
    matrix = json.loads((bundle_root / 'NOTIFICATION_DISPOSITIONS.json').read_bytes())
    notifications = policy_module.NotificationPolicy(plan, matrix, Path(matrix['schema_pin']['path']),
        json.loads((bundle_root / 'HOOK_OBSERVATION_CONTRACT.json').read_bytes()))
    events = queue.Queue(maxsize=1024)
    abort = threading.Event()
    protocol_lock = threading.RLock()
    requests_sent = {}
    responses_seen = set()
    thread_notifications = []
    positive_thread_id = None
    protocol_frames = 0
    protocol_anomalies = []
    threads = []
    errors = []
    counts = {'stdout': 0, 'stderr': 0}
    process = owner = None
    assigned = False
    facts = {'status': 'LAUNCH_NOT_OBSERVED', 'steps': [], 'errors': errors,
        'process': None, 'initial_thread_id': None, 'exit_code': None,
        'owned_job_pids_before_containment': None, 'owned_job_pids_after_containment': None,
        'job_closed': False, 'process_handle_closed': False, 'sent_stream_closed': False, 'input_pins_post_match': False,
        'consumer_launch_ready': False, 'consumer_or_governor_qualification': 'NONE'}
    forbidden_markers = [Path(row['path']).read_bytes() for row in plan['forbidden_markers']]
    config_raw_frames = {}
    sent = (run / 'sent.jsonl').open('xb', buffering=0)
    deadline = time.monotonic() + 60

    def fail_protocol(reason):
        # Called under protocol_lock; retain exact anomaly before stopping sends.
        protocol_anomalies.append(reason)
        abort.set()
        raise ValueError(reason)

    def witness_marker():
        with protocol_lock:
            facts['forbidden_marker_in_protocol'] = True
            abort.set()

    def observe_frame(message):
        nonlocal positive_thread_id, protocol_frames
        with protocol_lock:
            protocol_frames += 1
            if not isinstance(message, dict):
                fail_protocol('Non-object protocol message')
            if 'method' in message and 'id' in message:
                fail_protocol('Unexpected server request; no approval/setup response sent')
            if 'id' in message:
                identity = message['id']
                if type(identity) is not int or identity not in requests_sent:
                    fail_protocol('Unsolicited or mismatched response identity; frame SHA256: ' + canary.diagnostic_descriptor(message)['sha256'])
                if identity in responses_seen:
                    fail_protocol('Duplicate response identity: ' + str(identity))
                if ('result' in message) == ('error' in message):
                    fail_protocol('Response must contain exactly result or error')
                responses_seen.add(identity)
                if identity == plan['thread_start']['id']:
                    result = message.get('result')
                    thread = result.get('thread') if isinstance(result, dict) else None
                    candidate = thread.get('id') if isinstance(thread, dict) else None
                    if isinstance(candidate, str) and candidate:
                        positive_thread_id = candidate
                    if thread_notifications and (positive_thread_id is None or any(value != positive_thread_id for value in thread_notifications)):
                        fail_protocol('Positive thread notification disagrees with returned thread identity')
                if identity == 5 or ('visibility' in plan and identity == 6):
                    canary.response(message)
                return
            method = message.get('method')
            if not isinstance(method, str) or not method or 'result' in message or 'error' in message:
                fail_protocol('Malformed notification or missing response identity')
            try:
                disposition = notifications.route(message, canary, positive_thread_id)
            except Exception as exc:
                fail_protocol('Notification: ' + str(exc))
            if disposition == 'HANDLED':
                return
            if disposition == 'CANARY':
                try:
                    canary.observe(message)
                except Exception as exc:
                    fail_protocol('Canary: ' + str(exc))
                return
            if disposition != 'THREAD_STARTED':
                fail_protocol('No admitted notification disposition: ' + method)
            if method == 'thread/started':
                if plan['thread_start']['id'] not in requests_sent:
                    fail_protocol('Thread creation notification before permitted positive start')
                params = message.get('params')
                thread = params.get('thread') if isinstance(params, dict) else None
                identity = thread.get('id') if isinstance(thread, dict) else None
                if not isinstance(identity, str) or not identity:
                    fail_protocol('Malformed thread creation identity')
                if thread_notifications:
                    fail_protocol('Duplicate thread creation notification')
                thread_notifications.append(identity)
                if positive_thread_id is not None and identity != positive_thread_id:
                    fail_protocol('Thread creation notification identity mismatch')
                notifications.accept_thread_started_diagnostic(message,canary)

    def drain(pipe, name):
        pending = b''
        raw_line_offset = 0
        marker_tail = b''
        scan_only = False
        try:
            with (run / (name + '.bin')).open('xb', buffering=0) as stream:
                while True:
                    chunk = pipe.read(4096)
                    if not chunk:
                        break
                    previous = counts[name]
                    counts[name] += len(chunk)
                    retained = chunk[:max(0, CAP - previous)]
                    stream.write(retained)
                    # Inspect only retained bytes, including the bounded cap prefix.
                    over_cap = counts[name] > CAP
                    if over_cap:
                        abort.set()
                    marker_window = marker_tail + retained
                    if any(marker.rstrip(b'\r\n') in marker_window for marker in forbidden_markers):
                        witness_marker()
                    marker_tail = marker_window[-128:]
                    if name == 'stdout':
                        pending += retained
                        while b'\n' in pending:
                            line, pending = pending.split(b'\n', 1)
                            line_offset = raw_line_offset
                            raw_line_offset += len(line) + 1
                            if line.strip():
                                try:
                                    message = json.loads(line)
                                    if isinstance(message, dict) and message.get('id') == 10:
                                        config_raw_frames[10] = {'path': str(run / 'stdout.bin'), 'offset': line_offset,
                                            'bytes': len(line)+1, 'sha256': digest(line+b'\n'), 'private_raw': True}
                                    # Witness recognition precedes semantic validation and
                                    # continues after its first failure, without resuming it.
                                    for forbidden in forbidden_markers:
                                        if forbidden in line or forbidden.decode('ascii').rstrip('\r\n') in json.dumps(message):
                                            witness_marker()
                                    if scan_only:
                                        canary.record_unadmitted(message)
                                    if not scan_only:
                                        observe_frame(message)
                                        if not over_cap:
                                            events.put_nowait(message)
                                except Exception as exc:
                                    if not scan_only:
                                        errors.append(name + ': ' + type(exc).__name__ + ': ' + str(exc))
                                    scan_only = True
                                    abort.set()
                    if over_cap:
                        raise RuntimeError(name + ' output cap reached; raw retained only to cap')
                if pending.strip():
                    raise ValueError('Partial final JSONL frame')
        except BaseException as exc:
            errors.append(name + ': ' + type(exc).__name__ + ': ' + str(exc))
            abort.set()

    def check_deadline():
        if abort.is_set() or facts.get('forbidden_marker_in_protocol', False) or time.monotonic() >= deadline:
            raise RuntimeError('Protocol capture aborted or overall deadline reached')
        if process.poll() is not None:
            raise RuntimeError('Server exited before requested protocol completion')

    def send(message):
        check_deadline()
        raw = (json.dumps(message, separators=(',', ':')) + '\n').encode('utf-8')
        delivered = threading.Event()
        def write_stdin():
            try:
                # Serialize recognition of an anomaly with the next write.
                # A blocked writer remains bounded by the main-thread deadline
                # and retained owned-job termination; check_deadline takes no lock.
                with protocol_lock:
                    check_deadline()
                    if 'id' in message:
                        identity = message['id']
                        if type(identity) is not int or identity in requests_sent:
                            fail_protocol('Invalid or reused outgoing request identity')
                        if identity == 5 or ('visibility' in plan and identity == 6):
                            canary.register_turn(message)
                        requests_sent[identity] = message['method']
                    sent.write(raw)
                    process.stdin.write(raw)
                    process.stdin.flush()
            except BaseException as exc:
                errors.append('stdin: ' + str(exc))
                abort.set()
            finally:
                delivered.set()
        writer = threading.Thread(target=write_stdin, daemon=True)
        writer.start()
        threads.append(writer)
        while not delivered.wait(.05):
            check_deadline()
        if abort.is_set():
            raise RuntimeError('Request delivery failed')

    def response(request):
        send(request)
        while True:
            check_deadline()
            try:
                message = events.get(timeout=.05)
            except queue.Empty:
                continue
            if 'id' not in message:
                continue
            if message['id'] != request['id']:
                raise ValueError('Unexpected/duplicate response identity')
            if ('result' in message) == ('error' in message):
                raise ValueError('Response must contain exactly result or error')
            summary = message
            if request['method'] == 'config/read':
                summary = {'id': request['id'], 'selection': runtime.validate_config(plan, message.get('result')),
                           'raw_frame': config_raw_frames.get(request['id']), 'not_raw_response': True}
            facts['steps'].append({'request_id': request['id'], 'method': request['method'], 'response': summary})
            return message

    try:
        owner = helper.Win32Owner()
        env = dict(os.environ)
        env.update(plan['process_environment'])
        for key in ('CODEX_SESSION_ID', 'CODEX_THREAD_ID'):
            env.pop(key, None)
        process = subprocess.Popen(plan['server_argv'], cwd=plan['server_cwd'], env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            bufsize=0, shell=False, creationflags=0x00000004 | subprocess.CREATE_NO_WINDOW)
        facts['process'] = owner.creation_identity(process)
        helper.write_json_new(run / 'PROCESS_CUSTODY.json', {'plan_sha256': plan_sha, 'process_identity': facts['process']})
        owner.assign(process)
        assigned = True
        for name in ('stdout', 'stderr'):
            reader = threading.Thread(target=drain, args=(getattr(process, name), name), daemon=True)
            reader.start()
            threads.append(reader)
        facts['initial_thread_id'] = owner.resume_initial_thread(process)
        initialized = response(plan['initialize'])
        if 'error' in initialized:
            raise ValueError('Initialization rejected')
        send(plan['after_successful_initialize'])
        runtime.validate_startup(plan, response, facts)
        listing = plan['profile_list']
        profiles = []
        for page in range(4):
            result = response(listing).get('result', {})
            runtime.schema_result(plan, 'PermissionProfileListResponse', result)
            if not isinstance(result.get('data'), list):
                raise ValueError('Profile listing unavailable')
            profiles.extend(result['data'])
            cursor = result.get('nextCursor')
            if cursor is None:
                break
            listing = {'id': 100 + page, 'method': 'permissionProfile/list', 'params': dict(listing['params'], cursor=cursor)}
        else:
            raise ValueError('Profile listing exceeds bounded pagination')
        unknown = plan['unknown_thread_start']
        absent = unknown['params']['permissions']
        intended = plan['thread_start']['params']['permissions']
        if not all(sum(row.get('id') == name for row in profiles) == 1 and any(row.get('id') == name and row.get('allowed') is True for row in profiles) for name in ('worker_load', 'worker_use')) or any(row.get('id') == absent for row in profiles):
            raise ValueError('Intended profile unavailable or negative-control profile exists')
        rejected = response(unknown)
        if not matching_error(rejected, absent):
            raise ValueError('Unknown profile was not specifically rejected; no selector proof')
        facts['unknown_profile_rejection'] = True
        thread_reply = response(plan['thread_start'])
        result = thread_reply.get('result')
        if not isinstance(result, dict):
            raise ValueError('Thread metadata creation rejected')
        runtime.schema_result(plan, 'ThreadStartResponse', result)
        selected = result.get('activePermissionProfile')
        thread = result.get('thread')
        if not isinstance(selected, dict) or selected.get('id') != intended:
            raise ValueError('Returned active profile mismatch or unavailable')
        if not isinstance(thread, dict) or not isinstance(thread.get('id'), str) or not thread['id'] or thread.get('ephemeral') is not True:
            raise ValueError('Missing exact ephemeral thread identity')
        if result.get('cwd') != plan['server_cwd'] or result.get('approvalPolicy') != 'never':
            raise ValueError('Returned cwd or approval policy differs')
        sources = result.get('instructionSources')
        if not isinstance(sources, list) or not all(isinstance(path, str) for path in sources):
            raise ValueError('Instruction-source metadata missing or malformed')
        facts['thread_metadata'] = {'thread_id': thread['id'], 'ephemeral': True, 'activePermissionProfile': selected,
            'instructionSources': sources, 'cwd': result['cwd'], 'approvalPolicy': result['approvalPolicy'],
            'model': result.get('model'), 'modelProvider': result.get('modelProvider'),
            'runtimeWorkspaceRoots': result.get('runtimeWorkspaceRoots'), 'cliVersion': thread.get('cliVersion')}
        expected = plan['expected_metadata']
        for key in ('instructionSources', 'cwd', 'approvalPolicy', 'model', 'modelProvider', 'runtimeWorkspaceRoots', 'cliVersion'):
            if facts['thread_metadata'][key] != expected[key]:
                raise ValueError('Canary metadata differs: ' + key)
        if selected != expected['activePermissionProfile']:
            raise ValueError('Canary active permission profile provenance differs')
        canary.bind_thread(thread['id'])
        canary.bind_settings(result, plan['expected_turn_settings']['LOAD'])
        runtime.validate_thread_selection(plan, response, thread['id'], facts)
        if 'visibility' in plan:
            def flush_prefix():
                # Drain uses unbuffered raw files. Exact immutable prefix length
                # is retained while later notifications may append to those files.
                records = []
                for name in ('stdout.bin', 'stderr.bin', 'sent.jsonl'):
                    path = run / name
                    with path.open('rb') as stream:
                        length = path.stat().st_size
                        raw = stream.read(length)
                    if len(raw) != length:
                        raise ValueError('Capture prefix changed while reading')
                    records.append({'path': str(path), 'bytes': length,
                                    'sha256': hashlib.sha256(raw).hexdigest()})
                return records
            def wait_event():
                try:
                    events.get(timeout=.05)
                except queue.Empty:
                    pass
            facts['staged_visibility'] = staged_turns(plan=plan, canary=canary,
                response=response, check_deadline=check_deadline, wait_event=wait_event,
                process_identity=facts['process'], flush_raw=flush_prefix, run=run)
            facts['status'] = facts['staged_visibility']['status']
        else:
            turn_request = json.loads(json.dumps(plan['turn_start']))
            turn_request['params']['threadId'] = thread['id']
            facts['model_start_requests_sent'] = 1
            response(turn_request)
            while not canary.completed:
                check_deadline()
                try:
                    events.get(timeout=.05)
                except queue.Empty:
                    continue
            facts['complete_tool_inventory_observed'] = False
            facts['source_bytes_loaded_verified'] = False
            facts['status'] = 'MODEL_CANARY_TRANSPORT_COMPLETE_COMPONENT_NONVERDICT'
    except BaseException as exc:
        errors.append(type(exc).__name__ + ': ' + str(exc))
        if facts['status'] == 'LAUNCH_NOT_OBSERVED':
            facts['status'] = 'INCONCLUSIVE_STARTUP_PROTOCOL_OR_CONTROL_FAILURE'
    finally:
        try:
            if process is not None:
                # Closing a pipe while a writer is blocked can itself block; job
                # termination below releases all owned readers/writers first.
                if assigned:
                    facts['owned_job_pids_before_containment'] = owner.process_ids()
                    if facts['owned_job_pids_before_containment']:
                        owner.terminate()
                elif process.poll() is None:
                    process.terminate()  # exact retained process, still suspended
                process.wait(timeout=10)
                facts['exit_code'] = process.returncode
                if assigned:
                    end = time.monotonic() + 10
                    while owner.process_ids() and time.monotonic() < end:
                        time.sleep(.05)
                    facts['owned_job_pids_after_containment'] = owner.process_ids()
                    if facts['owned_job_pids_after_containment']:
                        raise RuntimeError('Owned job did not become empty')
        except BaseException as exc:
            errors.append('containment: ' + str(exc))
        finally:
            if owner is not None:
                try:
                    owner.close()
                    facts['job_closed'] = True
                except BaseException as exc:
                    errors.append('job close: ' + str(exc))
            if process is not None:
                drain_deadline = time.monotonic() + 2
                for worker in threads:
                    worker.join(timeout=max(0, drain_deadline - time.monotonic()))
                unsettled = any(worker.is_alive() for worker in threads)
                if unsettled:
                    errors.append('Capture thread did not settle after containment')
                    facts['pipe_close_deferred_for_unsettled_thread'] = True
                else:
                    for pipe in (process.stdin, process.stdout, process.stderr):
                        try:
                            pipe.close()
                        except Exception as exc:
                            errors.append('pipe close: ' + str(exc))
                try:
                    process._handle.Close()
                    facts['process_handle_closed'] = True
                except BaseException as exc:
                    errors.append('process handle close: ' + str(exc))
            try:
                sent.close()
                facts['sent_stream_closed'] = True
            except BaseException as exc:
                errors.append('sent stream close: ' + str(exc))
        try:
            facts['input_pins_post_match'] = all(helper.file_record(Path(row['path'])) == row for row in pins)
        except BaseException as exc:
            errors.append('post pins: ' + str(exc))
        # Validate the entire settled receive tail, including notifications and
        # responses queued after the last expected response. If a capture thread
        # did not settle, do not wait for its protocol lock or claim completeness.
        settled = not any(worker.is_alive() for worker in threads)
        if settled:
            with protocol_lock:
                missing = sorted(set(requests_sent) - responses_seen)
                mismatch = bool(thread_notifications) and (positive_thread_id is None or any(value != positive_thread_id for value in thread_notifications))
                if mismatch and not protocol_anomalies:
                    protocol_anomalies.append('Settled thread notification identity mismatch')
                complete = not missing and not protocol_anomalies and canary.transport_complete() and notifications.complete()
                facts['protocol_ledger'] = {'requests_sent': dict(requests_sent), 'responses_seen': sorted(responses_seen),
                    'thread_notifications': list(thread_notifications), 'positive_thread_id': positive_thread_id,
                    'frames_observed': protocol_frames, 'anomalies': list(protocol_anomalies), 'missing_response_ids': missing}
                facts['protocol_validation_complete'] = complete
                if not complete:
                    errors.append('Settled protocol validation failed')
        else:
            facts['protocol_validation_complete'] = False
        # P-01: settled drain evidence and earlier failures dominate later
        # custody normalization; errors and pin facts remain separately visible.
        failure_with_witness = (facts.get('forbidden_marker_in_protocol', False) or
                                facts['status'] == 'FAIL_WITH_WITNESS_READ_EXCLUSION')
        if facts['status'] in ('MODEL_CANARY_TRANSPORT_COMPLETE_COMPONENT_NONVERDICT', 'TWO_TURN_TRANSPORT_COMPLETE_NONVERDICT') and (errors or not settled or
                not facts.get('protocol_validation_complete', False) or
                not all(facts.get(key, False) for key in
                        ('job_closed', 'process_handle_closed', 'sent_stream_closed'))):
            facts['status'] = 'INCONCLUSIVE_CAPTURE_OR_CUSTODY_FAILURE'
        if not facts['input_pins_post_match']:
            facts['status'] = 'INCONCLUSIVE_INPUT_DRIFT'
        if failure_with_witness:
            facts['status'] = 'FAIL_WITH_WITNESS_READ_EXCLUSION'
        facts['stream_observed_bytes'] = counts
        model_requests = [key for key, method in requests_sent.items() if method == 'turn/start']
        facts['model_start_requests_sent'] = len(model_requests)
        facts['model_start_requests_attempted'] = len(model_requests)
        facts['model_start_responses_observed'] = sum(key in responses_seen for key in model_requests)
        facts['model_start_request_count_basis'] = 'RETAINED_WRITE_ATTEMPTS_NOT_DELIVERY_OR_COMPLETION'
        facts['component_read_exclusion_verdict'] = 'FAIL_WITH_WITNESS' if failure_with_witness else 'NOT_ADJUDICATED'
        facts['complete_tool_inventory_observed'] = False
        if settled:
            helper.write_json_new(run / 'MODEL_TOOL_TRACE.json', dict(canary.snapshot(), notification_policy=notifications.snapshot()))
            helper.write_json_new(run / 'MODEL_MESSAGES.json', {'messages': canary.public_final_messages(), 'authority': 'UNTRUSTED_MODEL_OUTPUT'})
        else:
            facts['model_trace_snapshot_skipped_unsettled'] = True
        facts['files'] = [helper.file_record(path) for path in sorted(run.iterdir()) if path.is_file()]
        helper.write_json_new(run / 'READBACK.json', facts)
    print(json.dumps({'status': facts['status'], 'readback': str(run / 'READBACK.json'), 'consumer_launch_ready': False}))
    return 0 if facts['status'] in ('MODEL_CANARY_TRANSPORT_COMPLETE_COMPONENT_NONVERDICT', 'TWO_TURN_TRANSPORT_COMPLETE_NONVERDICT') else 2
