"""Package-owned provider for the selected bounded native capture adapter.

The adapter is a source proposal. Currentness, recovery admission and runtime
qualification remain with their existing owners. No fixture or caller verdict
can select executable code or supply acceptance. Ordinary paths bypass this file.
"""
import argparse
import copy
import ctypes
from ctypes import wintypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
ADAPTER = ROOT / 'native-capture-adapter'
CAP = 1048576
MEMBERS = {'canary_protocol.py': '768f7823665cc154b30e6103eb5f7d77efd02e68c5afa4def61cd39f7a1579c4', 'capture.py': 'bd064f6425f43568ad5aef8ffb6222f2293672f94ec093774eed448f2a201cc4', 'load_visibility.py': 'e62cf0cadd02f6cac8989590b878bc8eb3db90791e7f60b1ee325d5776cb8f17', 'notification_policy.py': 'b89f6d184d3c90223ff06725d62d55679134b9dbb336af3d299f5fe97b7fdb7f', 'process_owner.py': '392c5db668fbef4eff4c66f51676cf066bfbfe3def28039cbc09bfec98430949', 'worker_profile.py': '0b1bc8d879f128df59200d4f22167d063e1f56c802cc7088113267417e9f8b82', 'worker_runtime.py': '2c2546705213e76f6148305eeb56c5b8ca93623bbb30cd8e5ca40e967fd2b873'}
ROUTE_SHA256 = 'e3d5bb061c3b3f1f3b1f3e505a594f56ed6ee67fe55f64f5a7480247cbcc3cf8'


def require(value, why):
    if not value:
        raise ValueError(why)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def package():
    require('capture.py' in MEMBERS, 'Selected capture source is unbound')
    capture_raw = None
    for name, expected in MEMBERS.items():
        path = ADAPTER / name
        for node in (path, *path.parents):
            require(not node.is_symlink() and not (node.exists() and
                    getattr(node.lstat(), 'st_file_attributes', 0) & 0x400), 'Aliased package member')
        require(isinstance(expected, str) and len(expected) == 64 and all(c in '0123456789abcdef' for c in expected),
                'Packaged source binding is invalid: ' + name)
        require(path.is_file(), 'Missing packaged dependency: ' + name)
        raw = path.read_bytes()
        require(digest(raw) == expected, 'Missing/changed packaged dependency: ' + name)
        if name == 'capture.py': capture_raw = raw
    require(capture_raw is not None, 'Selected capture source is unbound')
    path = ADAPTER / 'capture.py'
    spec = importlib.util.spec_from_file_location('selected_native_capture', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['selected_native_capture'] = module
    exec(compile(capture_raw, str(path), 'exec'), module.__dict__)
    return module


def bundle_plan(plan_sha256, bundle_root):
    root = Path(bundle_root)
    require(root.is_absolute() and root.is_dir(), 'Explicit absolute bundle root required')
    for node in (root, *root.parents):
        require(not node.is_symlink() and not (getattr(node.lstat(), 'st_file_attributes', 0) & 0x400), 'Aliased bundle root')
    path = root / 'THREAD_METADATA_PLAN.json'
    require(not path.is_symlink(), 'Aliased plan')
    raw = path.read_bytes()
    require(digest(raw) == plan_sha256, 'Plan differs from governor binding')
    plan = json.loads(raw)
    require(plan.get('purpose') != 'ISOLATED_QUALIFICATION', 'Governed capture cannot consume isolated qualification')
    require('visibility' in plan and plan['visibility']['identity']['selected_child'] in
            ('audit-state', 'audit-assess', 'audit-implement', 'audit-andon'), 'Governed dispatch cannot downgrade to ordinary')
    require(plan.get('adapter_source') == MEMBERS['capture.py'], 'Supported adapter selection missing or foreign')
    return plan


def preflight(plan_sha256, *, bundle_root):
    driver = package()
    plan = bundle_plan(plan_sha256, bundle_root)
    # The reviewed preflight retains its actual native/model/schema bounds.
    # An unknown host/settings selection is refused, never generalized by flags.
    return driver.preflight(plan_sha256, bundle_root=Path(bundle_root),
                            pins_sha256=plan['input_pins_sha256'])


def route_owner():
    path = ROOT / 'route-transaction.py'
    require(path.is_file() and digest(path.read_bytes()) == ROUTE_SHA256,
            'Existing packaged route owner missing or composition changed')
    return load(path, 'native_capture_existing_route_owner')


def require_governor_dispatch(context, plan):
    """Read already-OPEN authority through existing source functions; never OPEN.

    Locators are inputs, not permission. Each is reconciled against the owner's
    current ref, canonical record, package resolver, packet and live predicate.
    Recovery follows its existing native/custody/H0 attribution substitution.
    No ordinary currentness or effect authority is returned from that branch.
    """
    require(context['identity'] == plan['visibility']['identity'], 'Context/plan identity differs')
    require(context['parent_rollout'] == plan['visibility']['parent_rollout'] and
            context['parent_launch_offset'] == plan['visibility']['parent_launch_offset'],
            'Parent evidence locator/cursor differs from capture-owned plan')
    cfg = plan['governor_dispatch']
    allowed = {'controller', 'store', 'host_id', 'host_session_id', 'binding_generation',
               'request', 'packet', 'route_transaction_id', 'expected_record', 'repository',
               'recovery_capsule', 'native_binary', 'native_home', 'native_controller_cwd',
               'native_plugin_id', 'native_task', 'native_epoch_directory',
               'native_observation_successor_spec', 'native_observation_successor_sha256'}
    require(isinstance(cfg, dict) and set(cfg) <= allowed and 'native_recovery_observer' not in cfg,
            'Dispatch owner inputs contain unknown authority or callback')
    args = argparse.Namespace(**dict(cfg, requester_identity='governor', mirror_claim='ABSENT',
                                    writer_key=[], dependency_key=[]))
    owner = route_owner()
    repo = Path(cfg['repository']).resolve()
    common = owner.git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir')
    oid, record = owner.current_ref(repo, args.controller, route_transaction_id=args.route_transaction_id)
    require(record is not None and oid == args.expected_record, 'Current OPEN ref differs')
    owner.validate_canonical_route_record_bytes(repo, oid, record)
    require(record['decision'] == 'REQUIRED' and record['route_state'] == 'OPEN', 'Required OPEN absent')
    lifecycle = record['lifecycle']
    require(lifecycle['state'] == 'OPEN' and lifecycle['child_return'] is None and
            lifecycle['governor_decision'] is None and lifecycle['execution_evidence'] is None,
            'OPEN already advanced or consumed')
    child, canonical_reason = owner.mapped_child_route(record)
    # The governor owns its truthful bounded presentation reason; it is not
    # an authority input or required to equal the route map's stock wording.
    reason = context['identity']['reason']
    require(isinstance(reason, str) and 0 < len(reason) <= 240 and reason == reason.strip() and
            not reason.endswith('.') and not any(ord(c) < 32 or ord(c) == 127 for c in reason),
            'Malformed governor presentation reason')
    request = owner.read_request(args.request)
    raw, packet = owner.read_route_packet(args.packet, record['obligation_id'],
                                         args.route_transaction_id, expected_target=child)
    require(owner.bytes_identity(raw) == lifecycle['delivery']['packet'], 'OPEN packet differs')
    child_raw, child_path = owner.child_delivery_bytes(child)
    require({'identity': str(child_path), **owner.bytes_identity(child_raw)} == lifecycle['delivery']['child'],
            'Resolved child differs from OPEN delivery')
    child_pin = plan['binding']['load_pins']['child_source']
    require(str(child_path) == child_pin['path'] and len(child_raw) == child_pin['bytes'] and
            digest(child_raw) == child_pin['sha256'], 'Capture child source differs from actual resolver')
    envelope = plan['binding']['load_pins']['frozen_open_envelope']
    require(Path(envelope['path']).read_bytes() == raw, 'LOAD envelope is not exact owner-validated OPEN packet')
    transcript = ROOT.parent / 'references' / 'transcript-contract.md'
    shared = plan['binding']['load_pins']['shared_transcript_contract']
    require(Path(shared['path']).resolve() == transcript.resolve() and
            digest(transcript.read_bytes()) == shared['sha256'], 'Shared contract does not belong to selected package')
    logical_task = owner.open_logical_task(record)
    identity = {'selected_child': child, 'logical_task': logical_task, 'parent_thread_id': record['host_session_id'],
                'transaction_ref': record['route_transaction_id'], 'reason': reason,
                'source_sha256': digest(child_raw)}
    require(identity == context['identity'], 'Caller route/parent/reason/source identity differs from owner')
    require(record['host_session_id'] == args.host_session_id, 'Parent is not actual route host session')
    if record.get('schema') == owner.RECOVERY_RECORD_SCHEMA:
        owner.recovery_record_header_v1(record, args.controller)
        require(child == 'audit-state', 'Recovery cannot route another child')
        observer = owner.recovery_observer_from_args_v1(repo, args)
        capsule_raw, capsule = owner.read_recovery_capsule_v3(args.recovery_capsule)
        require(capsule == record['recovery_capsule'] and request == owner.recovery_request_v3(capsule),
                'Recovery capsule/request differs')
        require(owner.prepare_recovery_capsule_v3(repo, observer=observer) == capsule, 'Recovery custody/native proof changed')
        attributed = owner.recovery_binding_v3(repo, common, args, capsule, record['obligation_id'], args.route_transaction_id)
        require(attributed['correlation_id'] == record['host_correlation_id'], 'Recovery H0 attribution differs')
        owner.validate_recovery_packet_v3(packet, capsule, attributed['correlation_id'])
        if capsule['schema'] == owner.RECOVERY_ATTEMPT_CAPSULE_SCHEMA:
            owner.observe_recovery_attempt_v1(repo, observer, capsule, lifecycle['attempt_evidence'])
        used = Path(common) / 'implementaudit-recovery-capsules' / args.controller / (
            'native-v3-' + capsule['native_invocation_digest'].removeprefix('sha256:') + '.used')
        require(used.read_bytes() == owner.recovery_capsule_use_v3(capsule, args.route_transaction_id), 'Recovery one-use custody differs')
        require(owner.prepare_recovery_capsule_v3(repo, observer=observer) == capsule and
                owner.read_recovery_capsule_v3(args.recovery_capsule)[0] == capsule_raw, 'Recovery observation changed during readback')
        evidence = {'variant': 'SOURCE_OWNED_RECOVERY', 'record_oid': oid,
                    'host_correlation_id': attributed['correlation_id'],
                    'continuity_current': False, 'ordinary_effect_authority': 'NONE'}
    else:
        require(not cfg.get('recovery_capsule'), 'Recovery locator cannot select ordinary permission')
        current, actual, fingerprint = owner.validate_route_currentness(repo, common, args, request, record)
        owner.validate_source_event_binding(repo, common, args, current, request, packet['source_event'],
                                            record['obligation_id'], args.route_transaction_id)
        owner.post_route_currentness(repo, common, args, request, current, fingerprint, oid)
        evidence = {'variant': 'ORDINARY_VERIFIED_CURRENTNESS', 'record_oid': oid,
                    'current': current, 'predicate_evidence': actual, 'fingerprint': fingerprint}
    require(owner.current_ref(repo, args.controller, route_transaction_id=args.route_transaction_id) == (oid, record),
            'OPEN changed before dispatch return')
    return {'identity': identity, 'owner_evidence': evidence}


def capture(plan_sha256, run_name, *, bundle_root):
    plan, _, _ = preflight(plan_sha256, bundle_root=bundle_root)
    context = plan['parent_context']
    # The embedded context omits plan_sha256 to avoid a self-referential hash.
    context = dict(context, plan_sha256=plan_sha256)
    require(context['bundle_root'] == str(Path(bundle_root)) and context['run_name'] == run_name and
            Path(context['run']) == Path(bundle_root) / 'runs' / run_name, 'Capture bundle/run identity differs')
    require_governor_dispatch(context, plan)
    # No alternative ordinary launch branch is reachable through this provider.
    # The runtime-loaded governor contract owns actual transport qualification
    # and source adoption reconciliation. Provenance pins and this route check
    # grant neither. This explicit host call must follow that reconciliation.
    return package().capture(plan_sha256, run_name, bundle_root=Path(bundle_root),
                             pins_sha256=plan['input_pins_sha256'])


def decode_lines(raw, name):
    require(isinstance(raw, bytes) and len(raw) <= CAP and (not raw or raw.endswith(b'\n')),
            'Incomplete/over-bound ' + name)
    values = [json.loads(line) for line in raw.splitlines() if line.strip()]
    require(all(isinstance(row, dict) for row in values), 'Non-object ' + name)
    return values


def replay_load(plan, ready, prefixes, *, bundle_root):
    """Replay actual prefix through the retained native monitor and policy.

    The LOAD request is registered only after the observed startup reply and
    after all preceding requests have returned. No USE request/response is
    allowed. This validates receive ordering; sent bytes are write attempts,
    while the response/turn/items provide actual native observation evidence.
    """
    runtime = package().worker_runtime()
    exact = runtime.exact
    require(set(prefixes) == {'stdout.bin', 'stderr.bin', 'sent.jsonl'}, 'Prefix population differs')
    require(isinstance(prefixes['stderr.bin'], bytes) and len(prefixes['stderr.bin']) <= CAP, 'stderr bound')
    sent = decode_lines(prefixes['sent.jsonl'], 'sent ledger')
    frames = decode_lines(prefixes['stdout.bin'], 'native stdout')
    # Same pinned forbidden witnesses and raw/decoded comparisons as capture's
    # drain. A live process alone does not clear an already observed abnormality.
    markers = [Path(row['path']).read_bytes() for row in plan['forbidden_markers']]
    require(not any(marker.rstrip(b'\r\n') in prefixes[name] for marker in markers
                    for name in ('stdout.bin', 'stderr.bin')), 'Forbidden witness in captured stream')
    require(not any(marker.decode('ascii').rstrip('\r\n') in json.dumps(frame)
                    for marker in markers for frame in frames), 'Forbidden witness in decoded native frame')
    require(all(type(row['id']) is int for row in sent if 'id' in row),
            'Native outgoing request identity must be an exact integer')
    requests = {row['id']: row for row in sent if 'id' in row}
    require(len(requests) == sum('id' in row for row in sent), 'Duplicate request identity')
    turns = [row for row in sent if row.get('method') == 'turn/start']
    wanted = copy.deepcopy(plan['turn_start']); wanted['params']['threadId'] = ready['worker_thread_id']
    require(exact(turns, [wanted]) and exact(sent[-1], wanted) and wanted['id'] == 5 and 6 not in requests,
            'Missing exact LOAD or early/duplicate USE')
    for key in ('initialize', 'thread_start', 'unknown_thread_start'):
        require(exact(requests.get(plan[key]['id']), plan[key]), 'Startup request differs: ' + key)
    positive_index = next(index for index, row in enumerate(sent) if row.get('id') == plan['thread_start']['id'])
    before_positive = {row['id'] for row in sent[:positive_index] if 'id' in row}
    protocol = load(ADAPTER / 'canary_protocol.py', 'prefix_native_monitor')
    visibility = load(ADAPTER / 'load_visibility.py', 'prefix_native_visibility')
    policy = load(ADAPTER / 'notification_policy.py', 'prefix_native_policy')
    monitor = visibility.StagedProtocol(protocol.CanaryProtocol, plan['visibility']['load_spec'])
    policy_path = Path(bundle_root) / 'NOTIFICATION_DISPOSITIONS.json'
    require('notification_dispositions' not in plan or Path(plan['notification_dispositions']).resolve() == policy_path.resolve(),
            'Foreign policy locator differs from fixed capture bundle member')
    matrix = json.loads(policy_path.read_bytes())
    closed = policy.NotificationPolicy(plan, matrix, Path(matrix['schema_pin']['path']), {})
    seen = set(); replies = {}; thread = None; notification_threads = []
    reply_order = []
    expected_sent = [plan['initialize'], plan['after_successful_initialize']]
    consumed = {plan[key]['id'] for key in ('initialize', 'thread_start', 'unknown_thread_start')} | {5}
    require(exact([row for row in sent if 'id' not in row], [plan['after_successful_initialize']]),
            'Unreviewed outgoing notification')
    def response(request):
        require(exact(requests.get(request['id']), request), 'Readback request changed')
        require(request['id'] in replies, 'Readback response missing')
        consumed.add(request['id'])
        expected_sent.append(request)
        return replies[request['id']]
    for frame in frames:
        require(not ('id' in frame and 'method' in frame), 'Server request before parent visibility')
        if 'id' in frame:
            identity = frame['id']
            require(type(identity) is int and identity in requests and identity not in seen,
                    'Unsolicited/duplicate native response')
            require(('result' in frame) != ('error' in frame), 'Malformed response')
            seen.add(identity); replies[identity] = frame; reply_order.append(identity)
            if identity == plan['thread_start']['id']:
                result = frame['result']; runtime.schema_result(plan, 'ThreadStartResponse', result)
                thread = result['thread']['id']
                require(thread == ready['worker_thread_id'] and result['thread']['ephemeral'] is True,
                        'Wrong/non-ephemeral actual worker')
                for key, value in plan['expected_metadata'].items():
                    actual = result['thread'].get(key) if key in ('cliVersion', 'ephemeral') else result.get(key)
                    require(actual == value, 'Observed startup metadata differs: ' + key)
                monitor.bind_thread(thread)
                monitor.bind_settings(result, plan['expected_turn_settings']['LOAD'])
            if identity == 5:
                require(monitor.requested, 'LOAD response before bound startup/readbacks')
                monitor.response(frame)
        else:
            disposition = closed.route(frame, monitor, thread)
            if disposition == 'CANARY':
                monitor.observe(frame)
            elif disposition == 'THREAD_STARTED':
                # Capture sends the positive thread/start only after every
                # earlier sequential request has returned. A creation event
                # before that edge cannot have its permitted launch provenance.
                # The final exact ledger/response checks also bind this prefix.
                require(before_positive <= seen, 'Thread creation before permitted positive start')
                value = frame['params']['thread']['id']
                require(not notification_threads, 'Duplicate thread creation')
                notification_threads.append(value)
            else:
                require(disposition == 'HANDLED', 'Unknown notification disposition')
        if thread is not None and not monitor.requested and seen == set(requests) - {5}:
            startup_facts = {}
            runtime.validate_startup(plan, response, startup_facts)
            startup_facts['thread_metadata'] = {'thread_id': thread}
            require('result' in replies[plan['initialize']['id']], 'Initialization rejected')
            listing = copy.deepcopy(plan['profile_list']); profiles = []
            for page in range(4):
                result = response(listing)['result']
                runtime.schema_result(plan, 'PermissionProfileListResponse', result)
                profiles.extend(result['data'])
                cursor = result.get('nextCursor')
                if cursor is None:
                    break
                listing = {'id': 100 + page, 'method': 'permissionProfile/list',
                           'params': dict(listing['params'], cursor=cursor)}
            else:
                raise ValueError('Profile pagination exceeds retained bound')
            absent = plan['unknown_thread_start']['params']['permissions']
            require(all(sum(row.get('id') == name for row in profiles) == 1 and
                        any(row.get('id') == name and row.get('allowed') is True for row in profiles)
                        for name in ('worker_load', 'worker_use')) and
                    not any(row.get('id') == absent for row in profiles), 'Profile selector control differs')
            require(package().matching_error(replies[plan['unknown_thread_start']['id']], absent), 'Unknown profile control failed')
            expected_sent.extend([plan['unknown_thread_start'], plan['thread_start']])
            runtime.validate_thread_selection(plan, response, thread, startup_facts)
            expected_sent.append(wanted)
            require(exact(sent, expected_sent), 'Outgoing ledger differs from exact capture order/census')
            monitor.register_turn(wanted)
    require(seen == set(requests) and all(value == thread for value in notification_threads), 'Incomplete/foreign native prefix')
    require(consumed == set(requests), 'Unreviewed outgoing request in captured prefix')
    require(reply_order == [row['id'] for row in expected_sent if 'id' in row],
            'Native replies differ from exact sequential capture request order')
    evidence = monitor.qualify_load()
    require(evidence == ready['load_evidence'], 'Actual monitor replay differs from READY')
    return evidence


def require_live_process(identity):
    """Read-only identity/liveness query, no new process, job or authority."""
    require(os.name == 'nt', 'Selected adapter supports Windows only')
    require(set(identity) == {'pid', 'creation_filetime_100ns', 'creation_utc', 'identity_source'} and
            type(identity['pid']) is int and identity['pid'] > 0 and
            type(identity['creation_filetime_100ns']) is int, 'Actual process identity missing')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.c_void_p] * 4
    kernel.GetProcessTimes.restype = wintypes.BOOL
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x00100000 | 0x1000, False, identity['pid'])
    require(handle, 'Selected process unavailable')
    try:
        values = [wintypes.FILETIME() for _ in range(4)]
        require(kernel.GetProcessTimes(handle, *(ctypes.byref(v) for v in values)), 'Process creation read unavailable')
        ticks = (values[0].dwHighDateTime << 32) | values[0].dwLowDateTime
        require(ticks == identity['creation_filetime_100ns'] and kernel.WaitForSingleObject(handle, 0) == 258,
                'Worker exited or PID was reused')
    finally:
        require(kernel.CloseHandle(handle), 'Process query handle close failed')


def verify_load_ready(context, ready, prefixes):
    plan, _, helper = preflight(context['plan_sha256'], bundle_root=context['bundle_root'])
    require_governor_dispatch(context, plan)
    require(ready['identity'] == context['identity'] == plan['visibility']['identity'], 'READY identity differs')
    require(ready['semantic_verdict'] is None and ready['owner_stage_receipt'] is None, 'READY cannot carry authority')
    run = Path(context['run'])
    require(run == Path(context['bundle_root']) / 'runs' / context['run_name'], 'Foreign run')
    require(not any((run / name).exists() for name in ('PARENT_VISIBILITY_ACK.json', 'RELEASE.json', 'READBACK.json')),
            'Worker already released, disposed or terminal')
    invocation = json.loads((run / 'INVOCATION.json').read_bytes())
    require(invocation['plan'] == helper.file_record(Path(context['bundle_root']) / 'THREAD_METADATA_PLAN.json') and
            invocation['argv'] == plan['server_argv'] and invocation['cwd'] == plan['server_cwd'], 'Launch custody differs')
    launch = json.loads((run / 'PROCESS_CUSTODY.json').read_bytes())
    require(launch == {'plan_sha256': context['plan_sha256'], 'process_identity': ready['process_identity']},
            'READY process differs from retained launch custody')
    for name, raw in prefixes.items():
        path = run / name; helper.no_reparse(path)
        require(path.read_bytes() == raw, 'Held LOAD stream advanced after READY')
    for name in ('phase_capable_source_adoption', 'runtime_selection_acceptance'):
        require(ready[name] == plan['visibility'][name], 'READY provenance differs: ' + name)
    evidence = replay_load(plan, ready, prefixes, bundle_root=context['bundle_root'])
    require_live_process(ready['process_identity'])
    return {'load_evidence': evidence, 'worker_thread_id': ready['worker_thread_id'],
            'process_identity': ready['process_identity']}


def isolated_qualification_preflight(plan_sha256, *, bundle_root):
    """Exact isolated measurement inputs only; no route or effect authority."""
    driver = package()
    root = Path(bundle_root)
    require(root.is_absolute() and root.is_dir(), 'Explicit absolute bundle root required')
    for node in (root, *root.parents):
        require(not node.is_symlink() and not (getattr(node.lstat(), 'st_file_attributes', 0) & 0x400), 'Aliased bundle root')
    path = root / 'THREAD_METADATA_PLAN.json'
    require(not path.is_symlink(), 'Aliased plan')
    raw = path.read_bytes()
    require(len(raw) <= CAP and digest(raw) == plan_sha256, 'Isolated qualification plan differs')
    plan = json.loads(raw)
    visibility = load(ADAPTER / 'load_visibility.py', 'isolated_qualification_visibility')
    visibility.validate_isolated_qualification_plan(plan)
    require(plan.get('adapter_source') == MEMBERS['capture.py'], 'Supported adapter selection missing or foreign')
    return driver.preflight(plan_sha256, bundle_root=root, pins_sha256=plan['input_pins_sha256'])


def require_isolated_qualification_context(context, plan):
    # A source-owned discriminator is not a grant of native effect authority.
    fields = {'path_kind', 'purpose', 'bundle_root', 'plan_sha256', 'run_name', 'run',
              'identity', 'parent_rollout', 'parent_launch_offset'}
    require(isinstance(context, dict) and set(context) == fields and
            context['path_kind'] == 'isolated_qualification' and
            context['purpose'] == plan.get('purpose') == 'ISOLATED_QUALIFICATION',
            'Exact isolated qualification context required')
    require(context['identity'] == plan['visibility']['identity'] and
            context['parent_rollout'] == plan['visibility']['parent_rollout'] and
            context['parent_launch_offset'] == plan['visibility']['parent_launch_offset'],
            'Isolated qualification context differs from pinned plan')
    name = context['run_name']
    require(isinstance(name, str) and name and Path(name).name == name and name not in ('.', '..') and
            Path(context['run']) == Path(context['bundle_root']) / 'runs' / name,
            'Foreign isolated qualification run')


def capture_isolated_qualification(context):
    """Existing capture owner; caller must separately authorize one measurement."""
    require(isinstance(context, dict) and context.get('path_kind') == 'isolated_qualification' and
            context.get('purpose') == 'ISOLATED_QUALIFICATION', 'Exact isolated qualification context required')
    plan, _, _ = isolated_qualification_preflight(context['plan_sha256'], bundle_root=context['bundle_root'])
    require_isolated_qualification_context(context, plan)
    return package().capture(context['plan_sha256'], context['run_name'],
                             bundle_root=context['bundle_root'], pins_sha256=plan['input_pins_sha256'])


def verify_isolated_qualification_load_ready(context, ready, prefixes):
    """Isolated transport custody only; never substitutes for governed admission."""
    require(isinstance(context, dict) and context.get('path_kind') == 'isolated_qualification' and
            context.get('purpose') == 'ISOLATED_QUALIFICATION', 'Exact isolated qualification context required')
    plan, _, helper = isolated_qualification_preflight(context['plan_sha256'], bundle_root=context['bundle_root'])
    require_isolated_qualification_context(context, plan)
    require(ready.get('purpose') == plan['purpose'] and
            ready['identity'] == context['identity'] == plan['visibility']['identity'], 'Isolated READY identity differs')
    visibility = load(ADAPTER / 'load_visibility.py', 'isolated_ready_visibility')
    visibility.marker_for(ready, digest(encode(ready)))
    require(ready['semantic_verdict'] is None and ready['owner_stage_receipt'] is None, 'READY cannot carry authority')
    run = Path(context['run'])
    require(not any((run / name).exists() for name in ('PARENT_VISIBILITY_ACK.json', 'RELEASE.json', 'READBACK.json')),
            'Worker already released, disposed or terminal')
    invocation = json.loads((run / 'INVOCATION.json').read_bytes())
    require(invocation['plan'] == helper.file_record(Path(context['bundle_root']) / 'THREAD_METADATA_PLAN.json') and
            invocation['argv'] == plan['server_argv'] and invocation['cwd'] == plan['server_cwd'], 'Launch custody differs')
    launch = json.loads((run / 'PROCESS_CUSTODY.json').read_bytes())
    require(launch == {'plan_sha256': context['plan_sha256'], 'process_identity': ready['process_identity']},
            'READY process differs from retained launch custody')
    for name, raw in prefixes.items():
        path = run / name; helper.no_reparse(path)
        require(path.read_bytes() == raw, 'Held LOAD stream advanced after READY')
    for name in ('phase_capable_source_adoption', 'runtime_selection_acceptance'):
        require(ready[name] == plan['visibility'][name], 'READY provenance differs: ' + name)
    evidence = replay_load(plan, ready, prefixes, bundle_root=context['bundle_root'])
    require_live_process(ready['process_identity'])
    return {'load_evidence': evidence, 'worker_thread_id': ready['worker_thread_id'],
            'process_identity': ready['process_identity']}
