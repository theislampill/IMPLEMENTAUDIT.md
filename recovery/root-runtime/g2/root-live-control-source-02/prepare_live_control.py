#!/usr/bin/env python3
"""Prepare root-selected live consumption after actual independent receiving.

No provider call or automatic decision trigger. The root must first read the
actual live evidence and independent final review, then create the exact input.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import time
import types

ROOT = Path('/home/agent/dg16-g2-current04-public-20261109')
HERE = ROOT
RECEIVER = Path('/home/agent/dg16-g2-current04-public-20261109/bound-public-receiver')
COMPOSITION = ROOT/'composition'
LIVE = Path('/home/agent/dg16-g2-current04-public-20261109/public-receiving/live')
OUT = ROOT/'public-control-preparation'


def encode(v):
    return (json.dumps(v, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)+'\n').encode('ascii')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def desc(raw):
    return dict(bytes=len(raw), sha256=sha(raw))


def acquire(path, limit):
    st = path.lstat()
    assert stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and 0 <= st.st_size <= limit
    fd = os.open(path, os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        raw = os.read(fd, limit+1)
        end = os.fstat(fd)
        identity = lambda x: (x.st_dev,x.st_ino,x.st_mode,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
        assert identity(st) == identity(end) == identity(path.lstat()) and len(raw) == st.st_size
        return raw
    finally:
        os.close(fd)


def load(path):
    m = types.ModuleType('root_live_'+path.stem)
    m.__file__ = str(path)
    exec(compile(acquire(path, 131072), str(path), 'exec', dont_inherit=True), m.__dict__)
    return m


def verify_seal(directory, wanted):
    raw=acquire(directory/'SEAL.json', 131072)
    assert sha(raw)==wanted
    seal=json.loads(raw)
    names=set()
    for row in seal['members']:
        rel=Path(row['path'])
        assert not rel.is_absolute() and '..' not in rel.parts and row['path'] not in names
        path=directory/rel
        assert stat.S_IMODE(path.lstat().st_mode)==int(row['mode'],8)
        assert desc(acquire(path, 8*1024**2))=={k:row[k] for k in ('bytes','sha256')}
        names.add(row['path'])
    assert len(names)==seal['member_count']
    assert {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}==names|{'SEAL.json'}


def tree_id(rows):
    root={}
    for row in rows:
        node=root;parts=row['path'].split('/')
        for part in parts[:-1]:
            node=node.setdefault(part,{})
            assert isinstance(node,dict)
        assert parts[-1] not in node
        node[parts[-1]]=(row['mode'],row['git_blob'])
    def visit(node):
        raw=b''
        for name,value in sorted(node.items(),key=lambda x:(x[0]+('/' if isinstance(x[1],dict) else '')).encode()):
            mode,oid=('40000',visit(value)) if isinstance(value,dict) else value
            raw+=mode.encode()+b' '+name.encode()+b'\0'+bytes.fromhex(oid)
        return hashlib.sha1(b'tree '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    return visit(root)


def write(path, raw):
    with path.open('xb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    assert acquire(path, 4*1024**2) == raw


def review_directory(path):
    if ROOT is None:raise ValueError('SUCCESSOR_RUNTIME_BINDING_REQUIRED')
    reviewed=Path(path).resolve(strict=True)
    if reviewed==ROOT or not reviewed.is_relative_to(ROOT):raise ValueError('SUCCESSOR_REVIEW_DIRECTORY_SCOPE')
    return reviewed


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root-input', type=Path, required=True)
    args = p.parse_args()
    selected_raw = acquire(args.root_input, 16384)
    selected = json.loads(selected_raw)
    assert set(selected) == {'schema','actor','decision','receiver_seal_sha256',
        'independent_review_directory','independent_review_seal_sha256',
        'independent_review_body_sha256','request_sha256','proof_sha256',
        'actual_workflow_commit','actual_run_id','actual_evidence_and_review_read',
        'current_control_branch_absence_received','automatic_replay','issuer_thread','session','independent_reviewer'}
    assert selected['schema'] == 'dg16.current-g2.public-root-live-decision-input.v2'
    assert selected['actor'] == '/root' and selected['decision'] == 'CONSUME_AFTER_ACTUAL_INDEPENDENT_REVIEW'
    assert selected['actual_evidence_and_review_read'] is True
    assert selected['current_control_branch_absence_received'] is True and selected['automatic_replay'] is False
    assert selected['issuer_thread'] == selected['session'] == '01a1953f-a15b-7811-aa72-3538ebb03562'
    assert selected['independent_reviewer'] != '/root'
    verify_seal(RECEIVER, selected['receiver_seal_sha256'])
    R = load(RECEIVER/'public_receiver.py')
    assert R.BINDING_SHA == 'a0750feb79bbbe00c20b852bb179989a8dce89669130effbb6a8433774f0b6e9'
    binding, composition, _gate, modules, _catalog, _manifest = R.verified()
    review_dir = review_directory(selected['independent_review_directory'])
    verify_seal(review_dir, selected['independent_review_seal_sha256'])
    review_raw = acquire(review_dir/'INDEPENDENT_REVIEW.json', 4096)
    assert sha(review_raw) == selected['independent_review_body_sha256']
    review = json.loads(review_raw)
    assert review['reviewer'] == selected['independent_reviewer'] and review['decision'] == 'PASS'
    final = json.loads(acquire(review_dir/'FINAL.json', 16384))
    assert final['state'] == 'FINAL' and final['disposition'] == 'PASS'
    assert final['reviewer'] == review['reviewer'] and final['actual_live_evidence_reviewed'] is True
    assert final['receiver_binding_sha256'] == R.BINDING_SHA
    archive = acquire(LIVE/'ARTIFACT.zip', 400000)
    files = R.decode_zip(archive, 'live')
    metadata = json.loads(acquire(LIVE/'PUBLIC_METADATA.json', 262144))
    observation = R.inspect(files, 'live', run_id=selected['actual_run_id'],
        workflow_commit=selected['actual_workflow_commit'], metadata=metadata, archive=desc(archive))
    request_raw = files['REQUEST.json']; request = json.loads(request_raw)
    assert sha(request_raw) == selected['request_sha256'] == final['request_sha256']
    assert sha(files['PROOF.json']) == selected['proof_sha256'] == final['proof_sha256']
    assert request['control_branch'] == binding['control_branch']
    common = dict(request_sha256=sha(request_raw), proof_sha256=request['proof']['sha256'],
        private_observations_sha256=request['private_observations']['sha256'],
        source_commit=request['source_commit'], source_tree=request['source_tree'],
        policy_sha256=request['policy_sha256'], policy_adoption_sha256=request['policy_adoption_sha256'])
    root = dict(schema='dg16.full-correspondence-root-consumption.v1', author='/root',
        decision='CONSUME_AT_DECLARED_SCOPE_SUBJECT_TO_CLOSING_READBACK', one_shot=True,
        review_sha256=sha(review_raw), reviewer=review['reviewer'], automatic_full_G2_award=False,
        original_source_or_product_limits_changed=False, **common)
    root_raw = encode(root)
    control = dict(schema='dg16.full-correspondence-live-control.v1', publisher='/root',
        repository=binding['repository'], run_id=request['run_id'], run_attempt=1,
        workflow_commit=request['workflow_commit'], request_sha256=sha(request_raw),
        proof_sha256=request['proof']['sha256'], private_observations_sha256=request['private_observations']['sha256'],
        decision='CONSUME', files={'INDEPENDENT_REVIEW.json':desc(review_raw),'ROOT_CONSUMPTION.json':desc(root_raw)})
    payload={'CONTROL.json':encode(control),'INDEPENDENT_REVIEW.json':review_raw,'ROOT_CONSUMPTION.json':root_raw}
    checked=modules['live_control.py'].validate(payload, request_raw, now=time.time())
    assert checked['decision'] == 'CONSUME' and time.time() < request['expires_utc_epoch']
    leaves_raw=acquire(Path(__file__).parent/'EXPECTED_LEAVES.json', 2*1024**2)
    assert sha(leaves_raw)=='21421736447e752a2140f1a440345210491d74502b896806f6e7f8e133c47dfe', 'ROOT_HOST_LEAF_INDEX_CHANGED'
    leaves=json.loads(leaves_raw)['members']
    assert len(leaves)==1805 and tree_id(leaves)==binding['final_tree'], 'ROOT_HOST_LEAF_TREE_CHANGED'
    names={r['path'] for r in leaves}; added=[]; elements=[]
    for name, raw in sorted(payload.items()):
        path=request['control_path']+'/'+name
        assert path not in names and len(raw)<=4096
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        added.append(dict(path=path,mode='100644',git_blob=blob,**desc(raw)))
        elements.append(dict(path=path,mode='100644',type='blob',content=raw.decode('ascii')))
    tree=tree_id(leaves+added)
    assert not OUT.exists(), 'ONE_SHOT_CONTROL_ALREADY_PRESENT_RECONCILE'
    OUT.mkdir(mode=0o700)
    for name,raw in payload.items():write(OUT/name,raw)
    write(OUT/'ROOT_LIVE_DECISION_INPUT.json',selected_raw)
    write(OUT/'ROOT_LIVE_OBSERVATION.json',encode(observation))
    write(OUT/'CreateTree.json',encode(dict(repository_full_name=binding['repository'],
        base_tree_sha=binding['final_tree'],tree_elements=elements)))
    write(OUT/'PUBLICATION_REQUEST.json',encode(dict(schema='dg16.current-g2.actual-live-control-publication-request.v1',
        actor='/root',branch=binding['control_branch'],sole_parent=request['workflow_commit'],
        expected_tree=tree,additions=added,run_id=request['run_id'],run_attempt=1,
        request_sha256=sha(request_raw),proof_sha256=sha(files['PROOF.json']),
        independent_review_seal_sha256=selected['independent_review_seal_sha256'],
        expires_utc_epoch=request['expires_utc_epoch'],automatic_retry=False,original_awards=[],
        admission='ROOT_MUST_PERSIST_EXACT_ONE_SHOT_EFFECT_GRANT_BEFORE_PROVIDER_WRITE')))
    print(json.dumps(dict(expected_tree=tree,files=3,seconds_remaining=request['expires_utc_epoch']-time.time(),provider_effects=0)))


if __name__ == '__main__':
    main()
