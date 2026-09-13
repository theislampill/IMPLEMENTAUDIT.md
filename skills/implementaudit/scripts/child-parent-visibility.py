#!/usr/bin/env python3
"""Parent consumer for the selected Codex capture/rollout adapter.
No native-version/model/host-path default and no acceptance or receipt authority.
Expected marker text is not actual parent narration.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

CAPTURE_SOURCE_SHA256 = '14609a29ce1d41ea95851bd44d82c499f9eea169ceb335d208891908b9a5ffc7'
SHARED_SOURCE_SHA256 = 'b7ab2c5e850a7c6664882d5cb5b74400208da8e7ad57a73bf035f02bd0586e13'
_shared = None

def shared():
    global _shared
    if _shared is None:
        path = Path(__file__).resolve().with_name('child-load-visibility.py')
        raw = path.read_bytes()
        if path.is_symlink() or hashlib.sha256(raw).hexdigest() != SHARED_SOURCE_SHA256:
            raise ValueError('Shared visibility source differs')
        spec = importlib.util.spec_from_file_location('shared_child_visibility', path)
        module = importlib.util.module_from_spec(spec)
        exec(compile(raw, str(path), 'exec'), module.__dict__)
        _shared = module
    return _shared

def encode(value): return shared().encode(value)
def digest(raw): return shared().digest(raw)
def require(condition, reason): return shared().require(condition, reason)
def publish_once(path, raw): return shared().publish_once(path, raw)
def marker_for(ready, sha): return shared().marker_for(ready, sha)
def is_parent_commentary_message(payload): return shared().is_parent_commentary_message(payload)

def verify_parent_ack(ack, ready, ready_sha, parent_rollout, launch_offset, ready_offset):
    """Read actual native parent assistant bytes, not an ACK-supplied message.

    parent_rollout and launch_offset are governor-owned launch inputs, never
    selected by the child or ACK. Scan only the bounded run suffix for exactly
    one marker. A late retrospective marker cannot release an already used turn.
    """
    require(set(ack) == {'ready_sha256', 'parent_row_offset', 'parent_row_bytes', 'parent_row_sha256'},
            'ACK shape differs')
    require(ack['ready_sha256'] == ready_sha, 'Foreign readiness ACK')
    path = Path(parent_rollout)
    with path.open('rb') as stream:
        first = stream.readline(65537)
        require(len(first) <= 65536, 'Parent session metadata bound')
        meta = json.loads(first)
        require(meta.get('type') == 'session_meta' and meta.get('payload', {}).get('id') ==
                ready['identity']['parent_thread_id'], 'Wrong native parent session')
        stream.seek(launch_offset)
        raw = stream.read(4 * 1024 * 1024 + 1)
    require(len(raw) <= 4 * 1024 * 1024 and (not raw or raw.endswith(b'\n')), 'Parent suffix incomplete/over bound')
    marker = marker_for(ready, ready_sha)
    matches = []
    offset = launch_offset
    for line in raw.splitlines(keepends=True):
        row = json.loads(line)
        payload = row.get('payload', {})
        if (row.get('type') == 'response_item' and is_parent_commentary_message(payload) and
                payload.get('content') == [{'type': 'output_text', 'text': marker}]):
            matches.append((offset, line))
        offset += len(line)
    require(len(matches) == 1, 'Missing or duplicate truthful parent marker')
    offset, row = matches[0]
    require(offset >= ready_offset and offset == ack['parent_row_offset'] and
            len(row) == ack['parent_row_bytes'] and digest(row) == ack['parent_row_sha256'],
            'Parent marker is retroactive, foreign or byte-unbound')
    return {'path': str(path), 'offset': offset, 'bytes': len(row), 'sha256': digest(row)}


def exact_pin(path, expected):
    path = Path(path)
    raw = path.read_bytes()
    require(set(expected) == {'path', 'bytes', 'sha256'} and
            path.resolve() == Path(expected['path']).resolve() and
            len(raw) == expected['bytes'] and digest(raw) == expected['sha256'], 'File pin differs')
    return raw


def load_package_module(name, expected_sha):
    require(isinstance(expected_sha, str) and len(expected_sha) == 64,
            'Corrected selected capture dependency is unbound')
    path = Path(__file__).resolve().with_name(name)
    require(path.is_file() and not path.is_symlink(), 'Selected package dependency is missing')
    raw = path.read_bytes()
    require(digest(raw) == expected_sha, 'Selected package dependency changed')
    spec = importlib.util.spec_from_file_location('selected_' + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def selected_capture():
    # Set only by the existing package/capture source generator after exact
    # corrected-source review. A capsule cannot select code or assert acceptance.
    return load_package_module('native-worker-capture.py', CAPTURE_SOURCE_SHA256)


def read_prefixes(ready, run, capture_cap):
    require(type(capture_cap) is int and capture_cap > 0, 'Selected capture prefix bound missing')
    rows = ready.get('raw_prefix')
    require(isinstance(rows, list) and len(rows) == 3, 'Exact capture prefix population missing')
    expected_names = {'stdout.bin', 'stderr.bin', 'sent.jsonl'}
    result = {}
    for row in rows:
        require(isinstance(row, dict) and set(row) == {'path', 'bytes', 'sha256'}, 'Prefix shape differs')
        path = Path(row['path'])
        require(path.name in expected_names and path.name not in result and
                path.resolve().parent == run.resolve() and not path.is_symlink(), 'Foreign/duplicate prefix path')
        require(type(row['bytes']) is int and 0 <= row['bytes'] <= capture_cap, 'Prefix length exceeds selected capture bound')
        with path.open('rb') as stream:
            raw = stream.read(row['bytes'])
        require(len(raw) == row['bytes'] and digest(raw) == row['sha256'], 'Capture prefix differs')
        result[path.name] = raw
    require(set(result) == expected_names, 'Capture prefix dependency missing')
    return result


def verified_ready(context, ready_pin, capture):
    """Capture owns native evidence and admission; no caller PASS substitutes.

    verify_load_ready must reuse the corrected existing native monitor/policy
    and launch custody, not trust READY claims. It also preserves any existing
    route-specific pre-USE receipt requirement. It must not impose a blanket
    receipt gate: observed LOAD and formal lifecycle credit remain distinct.
    """
    ready_path = Path(ready_pin['path'])
    require(ready_path.name == 'LOAD_READY.json' and ready_path.resolve().parent ==
            Path(context['run']).resolve(), 'Foreign READY location')
    ready_raw = exact_pin(ready_path, ready_pin)
    ready = json.loads(ready_raw)
    require(ready.get('identity') == context['identity'], 'Wrong child/source/route identity')
    require(ready.get('semantic_verdict') is None and ready.get('owner_stage_receipt') is None,
            'READY cannot confer verdict or host receipt authority')
    prefixes = read_prefixes(ready, ready_path.parent, capture.CAP)
    if context.get('path_kind') == 'isolated_qualification':
        proof = capture.verify_isolated_qualification_load_ready(context, ready, prefixes)
    else:
        proof = capture.verify_load_ready(context, ready, prefixes)
    require(isinstance(proof, dict) and proof.get('load_evidence') == ready.get('load_evidence') and
            isinstance(proof.get('load_evidence'), dict) and proof['load_evidence'],
            'Actual verified LOAD evidence is missing')
    require(proof.get('worker_thread_id') == ready.get('worker_thread_id') and
            proof.get('process_identity') == ready.get('process_identity'), 'Wrong actual worker/process')
    marker_for(ready, digest(ready_raw))  # Format validation; this emits no parent narration.
    return ready, digest(ready_raw), proof


def inspect_load(context, ready_pin, capture):
    ready, ready_sha, proof = verified_ready(context, ready_pin, capture)
    parent = Path(context['parent_rollout'])
    with parent.open('rb') as stream:
        first = stream.readline(65537)
    require(len(first) <= 65536, 'Parent metadata bound')
    metadata = json.loads(first)
    require(metadata.get('type') == 'session_meta' and metadata.get('payload', {}).get('id') ==
            context['identity']['parent_thread_id'], 'Foreign actual parent session')
    floor = parent.stat().st_size
    require(type(context['parent_launch_offset']) is int and
            0 <= context['parent_launch_offset'] <= floor, 'Invalid launch-owned parent cursor')
    inspection = {'context_sha256': digest(encode(context)), 'ready_sha256': ready_sha,
                  'parent_ready_offset': floor, 'load_proof_sha256': digest(encode(proof)),
                  'worker_thread_id': ready['worker_thread_id'], 'narration_performed': False,
                  'semantic_verdict': None, 'host_stage_receipt': None}
    path = Path(context['run']) / 'PARENT_LOAD_INSPECTION.json'
    publish_once(path, encode(inspection))
    return {'status': 'LOAD_INSPECTED_AWAIT_ACTUAL_PARENT_COMMENTARY',
            'inspection': {'path': str(path), 'bytes': len(encode(inspection)), 'sha256': digest(encode(inspection))},
            'expected_announcement_text': marker_for(ready, ready_sha),
            'narration_performed': False, 'USE_released': False, 'authority': None}


def acknowledge_load(context, ready_pin, inspection_pin, capture):
    ready, ready_sha, proof = verified_ready(context, ready_pin, capture)
    inspection_path = Path(context['run']) / 'PARENT_LOAD_INSPECTION.json'
    inspection = json.loads(exact_pin(inspection_path, inspection_pin))
    require(inspection['context_sha256'] == digest(encode(context)) and
            inspection['ready_sha256'] == ready_sha and inspection['worker_thread_id'] == ready['worker_thread_id'] and
            inspection['load_proof_sha256'] == digest(encode(proof)), 'Inspection/source/LOAD identity changed')
    parent = Path(context['parent_rollout'])
    launch_offset = context['parent_launch_offset']
    with parent.open('rb') as stream:
        stream.seek(launch_offset)
        suffix = stream.read(4 * 1024 * 1024 + 1)
    require(len(suffix) <= 4 * 1024 * 1024 and (not suffix or suffix.endswith(b'\n')), 'Parent suffix incomplete/over bound')
    expected = marker_for(ready, ready_sha)
    matches = []
    offset = launch_offset
    for line in suffix.splitlines(keepends=True):
        row = json.loads(line)
        payload = row.get('payload', {})
        if (row.get('type') == 'response_item' and is_parent_commentary_message(payload) and
                payload.get('content') == [{'type': 'output_text', 'text': expected}]):
            matches.append((offset, line))
        offset += len(line)
    require(len(matches) == 1, 'No actual matching parent commentary or duplicate marker')
    offset, raw_row = matches[0]
    ack = {'ready_sha256': ready_sha, 'parent_row_offset': offset,
           'parent_row_bytes': len(raw_row), 'parent_row_sha256': digest(raw_row)}
    native_proof = verify_parent_ack(ack, ready, ready_sha, parent, launch_offset, inspection['parent_ready_offset'])
    # Recheck selected capture/LOAD before the one write that can release USE.
    verified_ready(context, ready_pin, capture)
    require(verify_parent_ack(ack, ready, ready_sha, parent, launch_offset,
                             inspection['parent_ready_offset']) == native_proof,
            'Actual parent presentation changed before ACK')
    path = Path(context['run']) / 'PARENT_VISIBILITY_ACK.json'
    publish_once(path, encode(ack))
    return {'status': 'ACTUAL_PARENT_ROW_BOUND_ACK_PUBLISHED', 'parent_row': native_proof,
            'ack_sha256': digest(encode(ack)), 'narration_performed_by_consumer': False,
            'USE_delivery': 'UNVERIFIED_CAPTURE_OWNS_SEND', 'authority': None,
            'host_stage_receipt': None, 'semantic_verdict': None}


def launch_capture(context, capture):
    """Concrete existing-capture call site, separately effect-admitted.

    The final selected source implements require_governor_dispatch by calling
    the existing route/resolver/OPEN/currentness or exact recovery owners.
    No purpose label, file pin or true boolean can replace that owner call.
    Capture still owns native Popen, job, deadlines, raw streams and cleanup.
    """
    plan, pins, owner = capture.preflight(context['plan_sha256'], bundle_root=context['bundle_root'])
    admission = capture.require_governor_dispatch(context, plan)
    require(isinstance(admission, dict) and admission.get('identity') == context['identity'] and
            isinstance(admission.get('owner_evidence'), dict) and admission['owner_evidence'],
            'Existing governor dispatch owner evidence missing')
    # Source-owned requirement, not a self-attested allow flag. Missing selected
    # implementation raises before the native capture call.
    return capture.capture(context['plan_sha256'], context['run_name'], bundle_root=context['bundle_root'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('inspect-load', 'ack-load', 'launch'))
    parser.add_argument('--context', required=True, type=Path)
    parser.add_argument('--context-sha256', required=True)
    parser.add_argument('--ready-pin', type=Path)
    parser.add_argument('--inspection-pin', type=Path)
    parser.add_argument('--execute-admitted-capture', action='store_true')
    parser.add_argument('--execute-isolated-qualification', action='store_true')
    args = parser.parse_args()
    raw = args.context.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.context_sha256:
        raise ValueError('Context pin differs')
    context = json.loads(raw)
    if context.get('path_kind') == 'ordinary':
        if (context.get('identity') is not None or args.operation == 'launch' or
                args.ready_pin is not None or args.inspection_pin is not None or args.execute_admitted_capture or args.execute_isolated_qualification):
            raise ValueError('Governed work cannot downgrade to ordinary')
        print(json.dumps({'status': 'ORDINARY_PATH_UNCHANGED', 'governed_marker': None}))
        return 0
    capture = selected_capture()
    if args.operation == 'launch':
        if context.get('path_kind') == 'isolated_qualification':
            require(args.execute_isolated_qualification and not args.execute_admitted_capture,
                    'Isolated capture requires its separately authorized explicit call')
            return capture.capture_isolated_qualification(context)
        require(args.execute_admitted_capture and not args.execute_isolated_qualification, 'Native launch requires the separate effect-admitted call')
        return launch_capture(context, capture)
    require(not args.execute_admitted_capture and not args.execute_isolated_qualification and args.ready_pin is not None, 'Parent operation inputs differ')
    ready_pin = json.loads(args.ready_pin.read_bytes())
    if args.operation == 'inspect-load':
        require(args.inspection_pin is None, 'Unexpected prior inspection')
        result = inspect_load(context, ready_pin, capture)
    else:
        require(args.inspection_pin is not None, 'Verified LOAD inspection missing')
        result = acknowledge_load(context, ready_pin, json.loads(args.inspection_pin.read_bytes()), capture)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, AttributeError, TypeError) as error:
        print(json.dumps({'status': 'REFUSED', 'reason': str(error), 'authority': None}), file=sys.stderr)
        raise SystemExit(2)
