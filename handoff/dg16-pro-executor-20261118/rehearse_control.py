#!/usr/bin/env python3
"""NON-ACCEPTANCE GitHub control rehearsal using the unchanged original consumer.

The review-shaped PASS and Root consumption are explicitly synthetic vectors.
This proves only live transport/serialization/topology/reservation mechanics.
It cannot receive an original G2 run or award M2, G1, G3, or DG16.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def desc(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}


def need(value, code):
    if not value:
        raise ValueError(code)


def load(args):
    root = args.packet.resolve(strict=True)
    selection_raw = (root / 'SELECTION.json').read_bytes()
    need(sha(selection_raw) == args.selection_sha256, 'IMMUTABLE_REHEARSAL_SELECTION')
    selection = json.loads(selection_raw)
    request_raw = (root / 'REQUEST.json').read_bytes()
    proof_raw = (root / 'PROOF.json').read_bytes()
    fixture_raw = (root / 'INPUT_FIXTURE.txt').read_bytes()
    need(selection['request'] == desc(request_raw) and
         selection['proof'] == desc(proof_raw) and
         selection['fixture'] == desc(fixture_raw), 'IMMUTABLE_REHEARSAL_INPUTS')
    request, proof = json.loads(request_raw), json.loads(proof_raw)
    need(request['rehearsal_only'] is True and request['original_acceptance'] is False and
         request['run_id'].startswith('NON_ACCEPTANCE_REHEARSAL_') and
         request['control_branch'].startswith('engineering/g2-control-rehearsal-') and
         proof['scope'] == 'SYNTHETIC_PROTOCOL_CONFORMANCE_ONLY' and
         proof['original_acceptance'] is False, 'SYNTHETIC_ONLY_NO_ORIGINAL_RECEIVING')
    spec = importlib.util.spec_from_file_location('make_control', Path(__file__).with_name('make_control.py'))
    formatter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(formatter)
    validator = formatter.load_validator(root / 'live_control_original.py', selection['validator_sha256'])
    need(selection['allowed_runtime_global_adaptations'] == {'CONTROL_BRANCH': request['control_branch']}
         and validator.REMOTE == selection['REMOTE_unchanged'], 'ONLY_DECLARED_BRANCH_ADAPTATION')
    validator.CONTROL_BRANCH = request['control_branch']
    return root, selection, request_raw, proof_raw, formatter, validator


class ReadOnlyCapture:
    """Concrete subprocess capture for the original consumer's public Git reads."""
    @staticmethod
    def capture(label, argv, records, deadline, *, seconds):
        started = time.time()
        timeout = min(seconds, deadline - time.monotonic())
        need(timeout > 0, 'REHEARSAL_DEADLINE')
        result = subprocess.run(argv, capture_output=True, timeout=timeout, check=False)
        records.append({'label': label, 'argv': argv, 'started_utc_epoch': started,
                        'finished_utc_epoch': time.time(), 'returncode': result.returncode,
                        'stdout': desc(result.stdout), 'stderr': desc(result.stderr)})
        return result.returncode, result.stdout, result.stderr


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--selection-sha256', required=True)
    parser.add_argument('--step', choices=('format', 'hold'), required=True)
    parser.add_argument('--root-decision')
    args = parser.parse_args()
    root, selection, request_raw, proof_raw, formatter, validator = load(args)
    request = json.loads(request_raw)
    started = time.time()
    if args.step == 'format':
        payload = formatter.build_payload(request_raw, proof_raw,
            (root / 'INDEPENDENT_REVIEW.json').read_bytes(), validator=validator,
            root_decision=args.root_decision, successor='PRO-EXECUTOR-01, designated by owner',
            now=time.time())
        formatter.write_bundle(root / 'control', payload)
        print(json.dumps({'scope': 'SYNTHETIC_PROTOCOL_CONFORMANCE_ONLY',
                          'original_acceptance': False, 'files': {k: desc(v) for k, v in payload.items()}},
                         sort_keys=True))
        return
    work = root / 'consumer'
    work.mkdir(mode=0o700, exist_ok=False)
    report = {'scope': 'SYNTHETIC_PROTOCOL_CONFORMANCE_ONLY', 'original_acceptance': False,
              'full_G2': False, 'M2': False, 'selection_sha256': args.selection_sha256,
              'started_utc_epoch': started, 'validator_sha256': selection['validator_sha256'],
              'runtime_global_adaptations': selection['allowed_runtime_global_adaptations'],
              'REMOTE': validator.REMOTE}
    try:
        remaining = request['expires_utc_epoch'] - time.time()
        need(remaining > 0, 'REHEARSAL_WINDOW_EXPIRED')
        reservation = validator.hold(work, request_raw, time.monotonic() + remaining,
                                     ReadOnlyCapture(), '/usr/bin/git')
        need(desc((root / 'INPUT_FIXTURE.txt').read_bytes()) == selection['fixture'],
             'PUBLIC_FIXTURE_CHANGED_DURING_HOLD')
        report.update(status='CONSUMED_SYNTHETIC_VECTOR', reservation=reservation)
    except BaseException as exc:
        report.update(status='REFUSED_OR_INCOMPLETE', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        report['finished_utc_epoch'] = time.time()
        report['elapsed_seconds'] = report['finished_utc_epoch'] - started
        raw = (json.dumps(report, sort_keys=True, indent=2) + '\n').encode()
        with (root / 'REHEARSAL_RESULT.json').open('xb') as stream:
            stream.write(raw)
        print(json.dumps(report, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
