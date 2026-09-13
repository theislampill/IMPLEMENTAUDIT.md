#!/usr/bin/env python3
"""Shared LOAD visibility preparation and relay helpers.
No native launch, schema/profile selection, currentness or stage authority.
"""
import hashlib
import re
import json
import math
import os
import time
from pathlib import Path


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode('utf-8')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(predicate, reason):
    if not predicate:
        raise ValueError(reason)


def publish_once(path, raw):
    with Path(path).open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


ISOLATED_QUALIFICATION = 'ISOLATED_QUALIFICATION'


def isolated_identity(identity):
    require(isinstance(identity, dict) and 'selected_child' in identity and identity['selected_child'] is None,
            'Isolated qualification cannot select a governed child')
    logical = identity.get('logical_task')
    require(isinstance(logical, str) and re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,127}', logical),
            'Isolated qualification requires a stable logical task')
    for key in ('parent_thread_id', 'transaction_ref'):
        value = identity.get(key)
        require(isinstance(value, str) and 0 < len(value) <= 240 and value == value.strip() and
                not any(ord(char) < 32 or ord(char) == 127 for char in value),
                'Isolated qualification custody identity missing or malformed')
    source = identity.get('source_sha256')
    require(isinstance(source, str) and re.fullmatch(r'[0-9a-f]{64}', source),
            'Isolated qualification source digest missing')
    reason = identity.get('reason')
    require(isinstance(reason, str) and 0 < len(reason) <= 240 and reason == reason.strip() and
            not any(ord(char) < 32 or ord(char) == 127 for char in reason) and not reason.endswith('.') and
            'CHILD_SKILL_ROUTE' not in reason and "I'm using" not in reason,
            'Isolated qualification requires one truthful bounded reason')
    return logical, reason


def validate_isolated_qualification_plan(plan):
    require(isinstance(plan, dict) and plan.get('purpose') == ISOLATED_QUALIFICATION,
            'Exact isolated qualification purpose required')
    require('governor_dispatch' not in plan, 'Isolated qualification cannot carry governed dispatch')
    cfg = plan.get('visibility')
    require(isinstance(cfg, dict), 'Isolated qualification visibility binding missing')
    isolated_identity(cfg.get('identity'))
    source = plan.get('binding', {}).get('load_pins', {}).get('child_source', {})
    require(cfg['identity']['source_sha256'] == source.get('sha256'),
            'Isolated qualification source differs from exact LOAD input')
    return cfg


def isolated_qualification_marker(ready, ready_sha):
    require(ready.get('purpose') == ISOLATED_QUALIFICATION,
            'Unknown qualification presentation purpose')
    logical, reason = isolated_identity(ready.get('identity'))
    worker = ready.get('worker_thread_id')
    require(isinstance(worker, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,128}', worker),
            'Isolated qualification worker identity missing')
    process = ready.get('process_identity')
    require(isinstance(process, dict) and type(process.get('pid')) is int and process['pid'] > 0 and
            type(process.get('creation_filetime_100ns')) is int and process['creation_filetime_100ns'] > 0,
            'Isolated qualification PID and birth identity missing')
    prefixes = ready.get('raw_prefix')
    require(isinstance(prefixes, list) and len(prefixes) == 3 and
            all(isinstance(row, dict) and set(row) == {'path', 'bytes', 'sha256'} and
                isinstance(row['path'], str) and type(row['bytes']) is int and row['bytes'] >= 0 and
                isinstance(row['sha256'], str) and re.fullmatch(r'[0-9a-f]{64}', row['sha256'])
                for row in prefixes) and
            {Path(row['path']).name for row in prefixes} == {'stdout.bin', 'stderr.bin', 'sent.jsonl'},
            'Isolated qualification raw prefix binding missing')
    require('semantic_verdict' in ready and ready['semantic_verdict'] is None and
            'owner_stage_receipt' in ready and ready['owner_stage_receipt'] is None,
            'Isolated qualification READY cannot carry authority')
    require(digest(encode(ready)) == ready_sha, 'LOAD_READY digest does not bind the exact delivery tuple')
    return ('```ini\nISOLATED_QUALIFICATION=LOAD_READY\nLOGICAL_TASK=' + logical +
            '\nWORKER_TASK=' + worker + '\nSOURCE_SHA256=' + ready['identity']['source_sha256'] +
            '\nPROCESS_PID=' + str(process['pid']) +
            '\nPROCESS_BIRTH_FILETIME_100NS=' + str(process['creation_filetime_100ns']) +
            '\nLOAD_READY_SHA256=' + ready_sha + '\n```\n' +
            'The isolated qualification task ' + logical + ' has loaded the bound source to ' + reason + '.')


def is_parent_commentary_message(payload):
    """Current phase and legacy channel must agree when both are supplied."""
    if (not isinstance(payload, dict) or payload.get('type') != 'message' or
            payload.get('role') != 'assistant'):
        return False
    labels = [payload[key] for key in ('phase', 'channel') if key in payload]
    return bool(labels) and all(value == 'commentary' for value in labels)


def normal_logical_task(identity, worker=None):
    logical = identity.get('logical_task') if isinstance(identity, dict) else None
    require(isinstance(logical, str) and re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,127}', logical),
            'Governed visibility requires the bound stable logical task')
    require(logical not in ('audit-state', 'audit-assess', 'audit-andon', 'audit-implement') and
            not re.fullmatch(r'[0-9a-f]{32,64}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', logical),
            'Logical task cannot be a reserved skill, digest or physical UUID')
    require(logical not in (identity.get('selected_child'), identity.get('parent_thread_id'),
                            identity.get('transaction_ref'), worker),
            'Logical task cannot substitute a skill, transaction or physical identity')
    return logical


def marker_for(ready, ready_sha):
    """Canonical product announcement plus exact existing delivery custody.

    The normal event names its canonical logical task separately from physical
    worker custody. The READY digest retains source/process/transaction/LOAD
    evidence; formatting does not replace the caller's actual LOAD verification.
    """
    if 'purpose' in ready:
        return isolated_qualification_marker(ready, ready_sha)
    identity = ready['identity']
    child, reason = identity['selected_child'], identity['reason']
    require(child in ('audit-state', 'audit-assess', 'audit-andon', 'audit-implement'),
            'Announcement selected child is not a governed skill')
    logical = normal_logical_task(identity, ready['worker_thread_id'])
    require(isinstance(reason, str) and 0 < len(reason) <= 240 and reason == reason.strip() and
            not any(ord(char) < 32 or ord(char) == 127 for char in reason) and
            not reason.endswith('.'), 'Announcement requires one bounded reason without a terminal period')
    for value in (identity['parent_thread_id'], identity['transaction_ref'], ready['worker_thread_id']):
        require(isinstance(value, str) and value and not any(char in value for char in '\r\n'),
                'Announcement task/transaction custody identity missing or malformed')
    require(digest(encode(ready)) == ready_sha, 'LOAD_READY digest does not bind the exact delivery tuple')
    return ('```ini\nCHILD_TASK=' + logical + '\nCHILD_SKILL_ROUTE=' + child +
            '\nLOAD=VERIFIED\nWORKER_TASK=' + ready['worker_thread_id'] +
            '\nLOAD_READY_SHA256=' + ready_sha + '\n```\n' +
            "I'm using the `" + logical + '` holon with the `' + child + '` skill to ' + reason + '.')


def prepare_contract(plan, selected_child):
    """Validate preparation inputs only; never load a child or grant admission.

    The governor supplies its existing required-route result separately from
    the selected transport plan. Existing resolver/OPEN/currentness/receipt
    owners remain authoritative. Hashing source here is not worker LOAD.
    """
    if plan.get('purpose') == ISOLATED_QUALIFICATION:
        require(selected_child is None, 'Isolated preparation cannot select a governed child')
        validate_isolated_qualification_plan(plan)
    cfg = plan.get('visibility')
    require(isinstance(cfg, dict), 'Exact staged visibility binding required')
    identity = cfg.get('identity')
    require(isinstance(identity, dict) and identity.get('selected_child') == selected_child,
            'Selected child identity differs from required route')
    if plan.get('purpose') != ISOLATED_QUALIFICATION:
        normal_logical_task(identity)
    for key in ('parent_thread_id', 'transaction_ref', 'reason'):
        value = identity.get(key)
        require(isinstance(value, str) and value.strip() == value and value and
                not any(ord(c) < 32 or ord(c) == 127 for c in value),
                'Missing/malformed visibility identity: ' + key)
    require(len(identity['reason']) <= 240 and not identity['reason'].endswith('.'),
            'Visibility reason differs from announcement contract')
    binding = plan.get('binding')
    require(isinstance(binding, dict), 'Exact source pin binding required')
    load_pins = binding.get('load_pins')
    required_roles = {'child_source', 'shared_transcript_contract', 'frozen_open_envelope'}
    require(isinstance(load_pins, dict) and set(load_pins) == required_roles,
            'Exact capture LOAD source pin population required')
    pins = {}
    for role in sorted(required_roles):
        entry = load_pins.get(role)
        require(isinstance(entry, dict) and set(entry) == {'path', 'bytes', 'sha256'},
                'Exact source pin missing: ' + role)
        require(isinstance(entry['path'], str) and entry['path'] and
                type(entry['bytes']) is int and entry['bytes'] >= 0 and
                isinstance(entry['sha256'], str) and len(entry['sha256']) == 64 and
                all(c in '0123456789abcdef' for c in entry['sha256']),
                'Malformed source pin: ' + role)
        try:
            raw = Path(entry['path']).read_bytes()
        except OSError as error:
            raise ValueError('Unavailable source pin: ' + role) from error
        require(len(raw) == entry['bytes'] and digest(raw) == entry['sha256'],
                'Changed source pin: ' + role)
        pins[role] = dict(entry)
    return {'status': 'HOLD_UNBOUND_NATIVE_CAPTURE_PROFILE',
            'preparation': 'STRUCTURAL_BINDING_ONLY', 'launchable': False,
            'selected_child': selected_child, 'capsule_sha256': digest(encode(plan)),
            'source_pins': pins, 'visibility_module_sha256': digest(Path(__file__).read_bytes()),
            'unbound_consumer': 'qualified capture/profile and governor relay/ACK integration',
            'governed_announcement': None, 'semantic_verdict': None, 'owner_stage_receipt': None}


def wait_for_parent_visibility(*, ready, expected_identity, verify_load,
                               parent_checkpoint, verify_ack, check_deadline,
                               run, ack_timeout_seconds, use_request_identity,
                               clock=time.monotonic, pause=time.sleep, relay=print):
    """Portable portion of the retained staged_turns LOAD -> ACK barrier.

    This is a capture helper, not a launch path or an authority verifier.
    The future qualified capture MUST supply native LOAD evidence validation,
    its launch-owned parent capture checkpoint, native parent-row verification,
    deadline/cleanup custody, and the exact distinct USE request identity.
    verify_ack must independently reread native parent evidence and reject
    missing/foreign/duplicate/retroactive/non-assistant announcements; an ACK
    payload or this function's return never substitutes for that evidence.

    No native schema, executable, profile, model, command quoting or request ID
    is selected here. There is no default verifier, native launch or USE send.
    All exceptions propagate to the capture owner's existing containment.
    """
    require(all(callable(f) for f in (verify_load, parent_checkpoint, verify_ack, check_deadline)),
            'Qualified capture callbacks are unbound')
    require(type(ack_timeout_seconds) in (int, float) and math.isfinite(ack_timeout_seconds) and
            0 < ack_timeout_seconds <= 600, 'ACK deadline bound')
    require(ready.get('identity') == expected_identity, 'Foreign LOAD identity')
    require(ready.get('semantic_verdict') is None and ready.get('owner_stage_receipt') is None,
            'LOAD is not a verdict or stage receipt')
    require(use_request_identity is not None, 'Exact USE request identity missing')
    check_deadline()
    evidence = verify_load(ready)  # Native LOAD, source, process and phase belong to the capture owner.
    require(isinstance(evidence, dict) and evidence and evidence == ready.get('load_evidence'),
            'Verified native LOAD evidence missing or differs')
    raw = encode(ready)
    ready_sha = digest(raw)
    marker_for(ready, ready_sha)  # Validate format; do not emit a parent announcement.
    checkpoint = parent_checkpoint()  # Launch-owned evidence cursor; never chosen by the ACK.
    check_deadline()
    ready_path = Path(run) / 'LOAD_READY.json'
    publish_once(ready_path, raw)
    relay('LOAD_READY ' + str(ready_path) + ' ' + ready_sha, flush=True)
    deadline = clock() + ack_timeout_seconds
    ack_path = Path(run) / 'PARENT_VISIBILITY_ACK.json'
    while not ack_path.exists():
        check_deadline()
        require(clock() < deadline, 'Parent visibility ACK timeout; contain owned worker')
        pause(.05)
    check_deadline()
    require(clock() < deadline, 'Late ACK')
    ack_raw = ack_path.read_bytes()
    require(len(ack_raw) <= 4096, 'ACK byte bound')
    ack = json.loads(ack_raw)
    require(isinstance(ack, dict) and set(ack) == {
        'ready_sha256', 'parent_row_offset', 'parent_row_bytes', 'parent_row_sha256'}, 'ACK shape differs')
    require(ack['ready_sha256'] == ready_sha, 'Foreign readiness ACK')
    proof = verify_ack(ack, ready, ready_sha, checkpoint)
    require(isinstance(proof, dict) and proof, 'Native parent verification evidence missing')
    check_deadline()
    require(clock() < deadline, 'Parent verification exceeded ACK deadline')
    release = {'ready_sha256': ready_sha, 'ack_sha256': digest(ack_raw), 'parent_message': proof,
               'worker_thread_id': ready['worker_thread_id'],
               'use_request_identity': use_request_identity, 'delivery_status': 'PENDING'}
    publish_once(Path(run) / 'RELEASE.json', encode(release))
    return release  # Existing capture must bind and send USE to this SAME still-owned worker.
