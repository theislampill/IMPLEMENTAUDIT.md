#!/usr/bin/env python3
"""Encode the live-window control files and check them with the packet's OWN live_control.validate. Authority NONE.

It writes local files only. It does not review, decide, consume or publish: the independent review is the reviewer's
act, ROOT_CONSUMPTION/CONTROL are Root's act, and the control-branch commit is Root's publication. Field names and fixed
values are exactly those live_control.validate requires (g220-custody/.../live_control.py lines 50-88); G220 never
reached this step, so there is no historical instance of these three files.

  review   [INDEPENDENT-REVIEWER]  REQUEST.json + reviewer label            -> INDEPENDENT_REVIEW.json
  consume  [ROOT-SUCCESSOR]        REQUEST.json + the reviewer's file       -> ROOT_CONSUMPTION.json, CONTROL.json, ADDITIONS.json
  stop     [ROOT-SUCCESSOR]        REQUEST.json                             -> CONTROL.json (decision STOP, no other file)

usage: live_control_payload.py review  --request F --reviewer LABEL --out F
       live_control_payload.py consume --request F --review F --live-control <packet>/live_control.py --author LABEL --publisher LABEL --out-dir D
       live_control_payload.py stop    --request F --live-control <packet>/live_control.py --publisher LABEL --out-dir D
REQUEST.json is the file of that name in the run's live artifact, byte for byte (its sha256 is bound into every body).
"""
import argparse, hashlib, importlib.util, json, sys, time
from pathlib import Path

sha = lambda raw: hashlib.sha256(raw).hexdigest()
desc = lambda raw: {'bytes': len(raw), 'sha256': sha(raw)}
encode = lambda value: (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()   # == live_control.encode
p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
s = p.add_subparsers(dest='cmd', required=True)
c = s.add_parser('review'); [c.add_argument('--' + n, required=True) for n in ('request', 'reviewer', 'out')]
c = s.add_parser('consume'); [c.add_argument('--' + n, required=True) for n in ('request', 'review', 'live-control', 'author', 'publisher', 'out-dir')]
c.add_argument('--now', type=float)
c = s.add_parser('stop'); [c.add_argument('--' + n, required=True) for n in ('request', 'live-control', 'publisher', 'out-dir')]
c.add_argument('--now', type=float)
a = p.parse_args()
for name in ('reviewer', 'author', 'publisher'):
    value = getattr(a, name, None)
    if value is not None and (not value or '<' in value): raise SystemExit('UNFILLED_IDENTITY_LABEL --' + name)
request_raw = Path(a.request).read_bytes(); request = json.loads(request_raw)
common = {'request_sha256': sha(request_raw), 'proof_sha256': request['proof']['sha256'],
          'private_observations_sha256': request['private_observations']['sha256'],
          'source_commit': request['source_commit'], 'source_tree': request['source_tree'],
          'policy_sha256': request['policy_sha256'], 'policy_adoption_sha256': request['policy_adoption_sha256']}


def write(path, raw):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as handle: handle.write(raw)
    print('%s  %5d  %s' % (sha(raw), len(raw), path))


if a.cmd == 'review':
    write(a.out, encode({'schema': 'dg16.full-correspondence-independent-live-review.v1', 'authority': 'NONE', 'decision': 'PASS',
                         'blocking_findings': [], 'scope': 'ACTUAL_FULL_CORRESPONDENCE_PROOF_WHILE_PRIVATE_INPUTS_REMAIN_LIVE',
                         'reviewer': a.reviewer, **common}))
    sys.exit(0)
spec = importlib.util.spec_from_file_location('packet_live_control', a.live_control); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
now = a.now if a.now is not None else time.time()
assert request['control_branch'] == L.CONTROL_BRANCH and request['repository'] == L.REPOSITORY and \
    request['control_path'] == 'qualification/dg16-full-g2-control/' + request['run_id'] + '-1', 'LIVE_CONTROL_LOCATION'
control = {'schema': 'dg16.full-correspondence-live-control.v1', 'publisher': a.publisher, 'repository': L.REPOSITORY,
           'run_id': request['run_id'], 'run_attempt': 1, 'workflow_commit': request['workflow_commit'],
           'request_sha256': sha(request_raw), 'proof_sha256': request['proof']['sha256'],
           'private_observations_sha256': request['private_observations']['sha256']}
if a.cmd == 'stop':
    payload = {'CONTROL.json': encode({**control, 'decision': 'STOP', 'files': {}})}
else:
    review_raw = Path(a.review).read_bytes(); review = json.loads(review_raw)
    root_raw = encode({'schema': 'dg16.full-correspondence-root-consumption.v1', 'author': a.author,
                       'decision': 'CONSUME_AT_DECLARED_SCOPE_SUBJECT_TO_CLOSING_READBACK', 'one_shot': True,
                       'review_sha256': sha(review_raw), 'reviewer': review['reviewer'], 'automatic_full_G2_award': False,
                       'original_source_or_product_limits_changed': False, **common})
    payload = {'CONTROL.json': encode({**control, 'decision': 'CONSUME',
                                       'files': {'INDEPENDENT_REVIEW.json': desc(review_raw), 'ROOT_CONSUMPTION.json': desc(root_raw)}}),
               'INDEPENDENT_REVIEW.json': review_raw, 'ROOT_CONSUMPTION.json': root_raw}
checked = L.validate(payload, request_raw, now=now)           # the packet's own validator; raises Refusal(code) on any mismatch
out = Path(a.out_dir)
for name, raw in payload.items():
    if name != 'INDEPENDENT_REVIEW.json' or a.cmd == 'stop': write(out / name, raw)
additions = [dict(path=request['control_path'] + '/' + name, mode='100644', git_blob=hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest(), **desc(raw))
             for name, raw in sorted(payload.items())]
write(out / 'ADDITIONS.json', encode(dict(authority='NONE', control_branch=L.CONTROL_BRANCH, sole_parent=request['workflow_commit'],
      additions=additions, packet_validate=checked, expires_utc_epoch=request['expires_utc_epoch'])))
print(json.dumps(dict(packet_validate=checked['decision'], files=len(payload), seconds_remaining=round(request['expires_utc_epoch'] - now, 1))))
