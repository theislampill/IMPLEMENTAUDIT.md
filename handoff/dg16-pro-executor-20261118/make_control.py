#!/usr/bin/env python3
"""Format an already-authored independent G2 review and an explicit Root choice.

This operator utility does not create a review or infer PASS. It does not publish,
launch, extend a deadline, or award G2. Use the validator from the selected
workflow commit, not whichever copy happens to be on the results branch.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import time
import types


ROOT_DECISION = 'CONSUME_AT_DECLARED_SCOPE_SUBJECT_TO_CLOSING_READBACK'
NAMES = ('CONTROL.json', 'INDEPENDENT_REVIEW.json', 'ROOT_CONSUMPTION.json')


def need(condition, code):
    if not condition:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptor(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def load_validator(path, expected_sha256):
    raw = Path(path).read_bytes()
    need(re.fullmatch(r'[0-9a-f]{64}', expected_sha256 or '') and
         sha(raw) == expected_sha256, 'SELECTED_VALIDATOR_SHA256_MISMATCH')
    module = types.ModuleType('selected_g2_live_control')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def build_payload(request_raw, proof_raw, review_raw, *, validator,
                  root_decision, successor=None, now):
    """Pure formatter; `now` is supplied for deterministic non-acceptance tests.

    The production CLI always uses the real wall clock. The caller must provide
    a genuine independent review at the request's scope; schema validity alone
    cannot establish reviewer independence or live evidence custody.
    """
    need(root_decision == ROOT_DECISION, 'EXPLICIT_ROOT_CONSUMPTION_REQUIRED')
    request = validator.parse(request_raw)
    review = validator.parse(review_raw)
    need(descriptor(proof_raw) == request['proof'], 'ACTUAL_PROOF_BYTES_MISMATCH')
    need(request['repository'] == validator.REPOSITORY and
         request['control_branch'] == validator.CONTROL_BRANCH and
         re.fullmatch(r'[A-Za-z0-9_-]+', request['run_id']) and
         request['control_path'] == 'qualification/dg16-full-g2-control/' + request['run_id'] + '-1',
         'SELECTED_CONTROL_LOCATION_MISMATCH')
    common = {
        'request_sha256': sha(request_raw),
        'proof_sha256': request['proof']['sha256'],
        'private_observations_sha256': request['private_observations']['sha256'],
        **{key: request[key] for key in
           ('source_commit', 'source_tree', 'policy_sha256', 'policy_adoption_sha256')},
    }
    root = {
        'schema': 'dg16.full-correspondence-root-consumption.v1',
        'author': '/root', 'decision': root_decision, 'one_shot': True,
        'review_sha256': sha(review_raw), 'reviewer': review['reviewer'],
        'automatic_full_G2_award': False,
        'original_source_or_product_limits_changed': False, **common,
    }
    control = {
        'schema': 'dg16.full-correspondence-live-control.v1',
        'publisher': '/root', 'repository': request['repository'],
        'run_id': request['run_id'], 'run_attempt': request['run_attempt'],
        'workflow_commit': request['workflow_commit'],
        'request_sha256': common['request_sha256'],
        'proof_sha256': common['proof_sha256'],
        'private_observations_sha256': common['private_observations_sha256'],
        'decision': 'CONSUME',
    }
    if successor is not None:
        need(type(successor) is str and bool(successor), 'EXPLICIT_SUCCESSOR_REQUIRED')
        root['successor'] = successor
        control['successor'] = successor
    payload = {'INDEPENDENT_REVIEW.json': review_raw,
               'ROOT_CONSUMPTION.json': encode(root)}
    control['files'] = {name: descriptor(raw) for name, raw in payload.items()}
    payload['CONTROL.json'] = encode(control)
    validator.validate(payload, request_raw, now=now)
    return payload


def write_bundle(output, payload):
    """Create one fresh bundle; existing or partial output is never overwritten."""
    need(set(payload) == set(NAMES) and all(type(raw) is bytes for raw in payload.values()),
         'EXACT_CONTROL_BUNDLE_REQUIRED')
    output = Path(output)
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    for name in NAMES:
        with (output / name).open('xb') as stream:
            stream.write(payload[name])
            stream.flush()
            os.fsync(stream.fileno())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validator', required=True, type=Path)
    parser.add_argument('--validator-sha256', required=True)
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--proof', required=True, type=Path)
    parser.add_argument('--independent-review', required=True, type=Path)
    parser.add_argument('--root-decision', required=True, choices=[ROOT_DECISION])
    parser.add_argument('--successor')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    validator = load_validator(args.validator, args.validator_sha256)
    request_raw = args.request.read_bytes()
    payload = build_payload(request_raw, args.proof.read_bytes(),
        args.independent_review.read_bytes(), validator=validator,
        root_decision=args.root_decision, successor=args.successor, now=time.time())
    # Recheck immediately before the only local mutation; no historical clock option.
    validator.validate(payload, request_raw, now=time.time())
    write_bundle(args.output, payload)
    print(json.dumps({'status': 'FORMATTED_AND_VALIDATED_ONLY',
                      'publication': False, 'original_acceptance': False,
                      'files': {name: descriptor(payload[name]) for name in NAMES}},
                     sort_keys=True))


if __name__ == '__main__':
    main()
