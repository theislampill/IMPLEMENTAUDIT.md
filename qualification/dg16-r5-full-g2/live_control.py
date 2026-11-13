"""Read an actual independently authored review and separate root consumption.

Only the selected read-only control branch is polled. No review, PASS, root
decision, product execution, retry, or extended deadline is created here.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import time

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
CONTROL_BRANCH = 'pro/dg16-r5-full-g2-direct-control-16-20261113'
REMOTE = 'https://github.com/' + REPOSITORY + '.git'
AUTHOR = '/root/linux02_delta_review'
ADAPTER_AUTHOR = '/root/source_package'
CURRENT_AUTHORS = ('/root/linux02_delta_review', '/root/source_package', '/root/original_acceptance_audit', '/root/g2_receiver_completion', '/root/g1_access08_author', '/root/g2_public_rebind', '/root/g2_diagnosis')
NAMES = ('CONTROL.json', 'INDEPENDENT_REVIEW.json', 'ROOT_CONSUMPTION.json')


class Refusal(ValueError):
    pass


def need(value, code):
    if not value: raise Refusal(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def descriptor(raw): return {'bytes': len(raw), 'sha256': sha(raw)}


def encode(value): return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def parse(raw):
    need(type(raw) is bytes and 0 < len(raw) <= 4096, 'LIVE_CONTROL_FILE_BOUND')
    def pairs(items):
        value = {}
        for key, item in items:
            need(key not in value, 'LIVE_CONTROL_DUPLICATE_KEY'); value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refusal('LIVE_CONTROL_NONFINITE')))


def validate(payload, request_raw, *, now):
    request = parse(request_raw)
    need(now < request['expires_utc_epoch'] and request['hold_seconds'] == 300, 'ACTUAL_REVIEW_WINDOW_EXPIRED')
    control = parse(payload['CONTROL.json'])
    fixed = {'schema': 'dg16.full-correspondence-live-control.v1', 'publisher': '/root', 'repository': REPOSITORY,
             'run_id': request['run_id'], 'run_attempt': 1, 'workflow_commit': request['workflow_commit'],
             'request_sha256': sha(request_raw), 'proof_sha256': request['proof']['sha256'],
             'private_observations_sha256': request['private_observations']['sha256']}
    need(type(control) is dict and set(control) == set(fixed) | {'decision', 'files'} and
         all(type(control[k]) is type(v) and control[k] == v for k, v in fixed.items()), 'LIVE_CONTROL_BINDING')
    if control['decision'] == 'STOP':
        need(set(payload) == {'CONTROL.json'} and control['files'] == {}, 'ROOT_STOP_POPULATION')
        return {'decision': 'STOP'}
    need(control['decision'] == 'CONSUME' and set(payload) == set(NAMES) and
         set(control['files']) == set(NAMES[1:]), 'LIVE_CONSUMPTION_POPULATION')
    for name in NAMES[1:]: need(control['files'][name] == descriptor(payload[name]), 'LIVE_DECISION_DIGEST')
    review = parse(payload['INDEPENDENT_REVIEW.json'])
    common = {'request_sha256': sha(request_raw), 'proof_sha256': request['proof']['sha256'],
              'private_observations_sha256': request['private_observations']['sha256'],
              'source_commit': request['source_commit'], 'source_tree': request['source_tree'],
              'policy_sha256': request['policy_sha256'], 'policy_adoption_sha256': request['policy_adoption_sha256']}
    fixed = {'schema': 'dg16.full-correspondence-independent-live-review.v1', 'authority': 'NONE',
             'decision': 'PASS', 'blocking_findings': [],
             'scope': 'ACTUAL_FULL_CORRESPONDENCE_PROOF_WHILE_PRIVATE_INPUTS_REMAIN_LIVE', **common}
    need(type(review) is dict and set(review) == set(fixed) | {'reviewer'} and
         all(type(review[k]) is type(v) and review[k] == v for k, v in fixed.items()) and
         type(review['reviewer']) is str and re.fullmatch(r'/root/[a-z0-9_]+', review['reviewer']) and review['reviewer'] not in CURRENT_AUTHORS,
         'ACTUAL_INDEPENDENT_LIVE_REVIEW_REQUIRED')
    root = parse(payload['ROOT_CONSUMPTION.json'])
    fixed = {'schema': 'dg16.full-correspondence-root-consumption.v1', 'author': '/root',
             'decision': 'CONSUME_AT_DECLARED_SCOPE_SUBJECT_TO_CLOSING_READBACK', 'one_shot': True,
             'review_sha256': sha(payload['INDEPENDENT_REVIEW.json']), 'reviewer': review['reviewer'],
             'automatic_full_G2_award': False, 'original_source_or_product_limits_changed': False, **common}
    need(type(root) is dict and set(root) == set(fixed) and
         all(type(root[k]) is type(v) and root[k] == v for k, v in fixed.items()), 'EXACT_ROOT_CONSUMPTION_REQUIRED')
    return {'decision': 'CONSUME', 'independent_reviewer': review['reviewer'],
            'review': descriptor(payload['INDEPENDENT_REVIEW.json']),
            'root_consumption': descriptor(payload['ROOT_CONSUMPTION.json'])}


def hold(work, request_raw, deadline, utility, git_path):
    request = parse(request_raw)
    need(request['control_branch'] == CONTROL_BRANCH and request['repository'] == REPOSITORY and
         request['control_path'] == 'qualification/dg16-full-g2-control/' + request['run_id'] + '-1', 'LIVE_CONTROL_LOCATION')
    need(not (work / 'CONSUMPTION_RESERVED.json').exists(), 'NO_REPEAT_LIVE_CONSUMPTION')
    records = []
    def git(arguments, *, missing=False):
        need(time.monotonic() < deadline, 'ACTUAL_REVIEW_WINDOW_EXPIRED')
        code, out, err = utility.capture('bounded-read-only-control', [git_path, *arguments], records,
                                        deadline, seconds=min(20, max(1, deadline-time.monotonic())))
        need(len(out) <= 65536 and len(err) <= 65536, 'LIVE_CONTROL_GIT_BOUND')
        if missing and code in (2, 128): return None
        need(code == 0, 'LIVE_CONTROL_GIT_REFUSED')
        return out
    def head():
        raw = git(['ls-remote', '--exit-code', '--refs', REMOTE, 'refs/heads/' + CONTROL_BRANCH], missing=True)
        if raw is None: return None
        expected = b'\trefs/heads/' + CONTROL_BRANCH.encode() + b'\n'
        need(len(raw) == 40 + len(expected) and raw[40:] == expected and re.fullmatch(rb'[0-9a-f]{40}', raw[:40]),
             'LIVE_CONTROL_REF_SHAPE')
        return raw[:40].decode()
    cache = work / 'control.git'
    git(['init', '--bare', '--quiet', str(cache)])
    seen = set()
    try:
        while time.monotonic() < deadline:
            commit = head()
            if commit and commit not in seen:
                seen.add(commit)
                git(['--git-dir', str(cache), 'fetch', '--quiet', '--no-tags', '--depth=2', REMOTE, commit])
                header = git(['--git-dir', str(cache), 'cat-file', '-p', commit])
                parents = re.findall(rb'(?m)^parent ([0-9a-f]{40})$', header)
                need(parents == [request['workflow_commit'].encode()], 'LIVE_CONTROL_SOLE_WORKFLOW_PARENT')
                prefix = request['control_path']
                tree = git(['--git-dir', str(cache), 'ls-tree', commit + ':' + prefix], missing=True)
                if tree is None: continue
                rows = tree.decode().splitlines(); names = []
                for row in rows:
                    parts = row.split('\t')
                    need(len(parts) == 2 and re.fullmatch('100644 blob [0-9a-f]{40}', parts[0]), 'LIVE_CONTROL_REGULAR_BLOB')
                    names.append(parts[1])
                need(len(names) == len(set(names)) and set(names) in ({'CONTROL.json'}, set(NAMES)), 'LIVE_CONTROL_BLOB_POPULATION')
                delta = git(['--git-dir', str(cache), 'diff-tree', '--no-commit-id', '--name-status', '-r',
                             request['workflow_commit'], commit]).decode().splitlines()
                need(sorted(delta) == sorted('A\t' + prefix + '/' + name for name in names), 'LIVE_CONTROL_EXACT_ONLY_ADDITIONS')
                payload = {}
                for name in names:
                    ref = commit + ':' + prefix + '/' + name
                    size = int(git(['--git-dir', str(cache), 'cat-file', '-s', ref]))
                    need(0 < size <= 4096, 'LIVE_CONTROL_FILE_BOUND')
                    raw = git(['--git-dir', str(cache), 'show', ref]); need(len(raw) == size, 'LIVE_CONTROL_BLOB_CHANGED')
                    payload[name] = raw
                result = validate(payload, request_raw, now=time.time())
                need(result['decision'] == 'CONSUME', 'ACTUAL_ROOT_STOP')
                need(head() == commit, 'LIVE_CONTROL_CHANGED_OR_EXPIRED')
                # The final read-only Git capture includes its own child
                # cleanup. Recheck both clocks after that complete call, at
                # the exclusive reservation boundary; never extend the hold.
                accepted_utc = time.time()
                need(time.monotonic() < deadline and accepted_utc < request['expires_utc_epoch'],
                     'LIVE_CONTROL_CHANGED_OR_EXPIRED')
                reserved = {'schema': 'dg16.live-consumption-reservation.v1', 'one_shot': True,
                            'request_sha256': sha(request_raw), 'control_commit': commit,
                            'accepted_utc_epoch': int(accepted_utc), **result}
                with (work / 'CONSUMPTION_RESERVED.json').open('xb') as stream:
                    stream.write(encode(reserved)); stream.flush(); os.fsync(stream.fileno())
                for name, raw in payload.items():
                    with (work / name).open('xb') as stream:
                        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
                return reserved
            remaining = deadline - time.monotonic()
            if remaining > 0: time.sleep(min(15, remaining))
        raise Refusal('ACTUAL_REVIEW_WINDOW_EXPIRED')
    finally:
        raw = encode({'commands': records, 'seen_commits': sorted(seen), 'automatic_retry': False})
        need(len(raw) <= 1024**2, 'LIVE_CONTROL_PRIVATE_LOG_BOUND')
        with (work / 'CONTROL_READS.json').open('xb') as stream: stream.write(raw)
