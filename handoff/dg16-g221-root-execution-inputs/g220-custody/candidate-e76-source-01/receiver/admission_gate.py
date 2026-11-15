"""Require the later genuine independent verdict; return data, never a grant."""
import hashlib
import json
from pathlib import Path
import re
import stat

CURRENT_AUTHOR = '/root/g2_cold_review'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def check_seal(root, expected):
    raw = (root / 'SEAL.json').read_bytes()
    assert sha(raw) == expected, 'ADMISSION_REVIEW_OR_SUBJECT_SEAL'
    seal = json.loads(raw)
    names = set()
    for row in seal['members']:
        rel = Path(row['path'])
        assert not rel.is_absolute() and '..' not in rel.parts
        path = root / rel
        info = path.lstat()
        assert stat.S_ISREG(info.st_mode) and not path.is_symlink() and info.st_nlink == 1
        assert stat.S_IMODE(info.st_mode) == int(row['mode'], 8)
        data = path.read_bytes()
        assert (len(data), sha(data)) == (row['bytes'], row['sha256'])
        assert row['path'] not in names
        names.add(row['path'])
    assert len(names) == seal['member_count']
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'SEAL.json'}
    return seal

def require_review_selection(value, binding):
    """Bind the actual root-selected distinct actor; labels do not authenticate provenance."""
    reviewer = binding['composition_review_reviewer']
    assert type(reviewer) is str and re.fullmatch('/root/[a-z0-9_]+', reviewer)
    assert reviewer != CURRENT_AUTHOR, 'CURRENT_AUTHOR_CANNOT_REVIEW_FINAL_BINDING'
    required = dict(schema='dg16.current03.combined-review-root-selection.v1', actor='/root', session='52e9b813fb80',
                    status='ACTUAL_DISTINCT_REVIEWER_SELECTED_FOR_FINAL_BINDING', author=CURRENT_AUTHOR,
                    reviewer=reviewer, source_commit=binding['source_commit'], source_tree=binding['source_tree'],
                    branch=binding['branch'], control_branch=binding['control_branch'],
                    candidate_seal_sha256=binding['candidate_seal_sha256'], composition_seal_sha256=binding['composition_seal_sha256'],
                    final_tree=binding['final_tree'], effect_grant=False, native_currentness=False, original_awards=[])
    assert type(value) is dict and set(value) == set(required), 'ACTUAL_ROOT_REVIEW_SELECTION_SHAPE'
    assert all(type(value.get(k)) is type(v) and value[k] == v for k, v in required.items()), 'ACTUAL_ROOT_DISTINCT_REVIEW_SELECTION_JOIN'
    return reviewer

def require_final_review(review_dir, review_sha256, receiver_dir, receiver_sha256, composition_sha256):
    """Called by actual root admission after receiving a sealed scoped PASS."""
    review_dir, receiver_dir = Path(review_dir), Path(receiver_dir)
    assert all(type(v) is str and len(v) == 64 and set(v) <= set('0123456789abcdef')
               for v in (review_sha256, receiver_sha256, composition_sha256))
    check_seal(receiver_dir, receiver_sha256)
    check_seal(review_dir, review_sha256)
    binding = json.loads((receiver_dir / 'BINDING.json').read_bytes())
    # The later root admission also receives the actual commission's lane provenance.
    # This data gate never authenticates an actor from matching JSON labels alone.
    assert binding.get('composition_review_reviewer') != CURRENT_AUTHOR, 'CURRENT_AUTHOR_CANNOT_REVIEW_FINAL_BINDING'
    selection_raw = (receiver_dir / 'FINAL_REVIEW_SELECTION.json').read_bytes()
    assert binding['composition_review_selection'] == dict(bytes=len(selection_raw), sha256=sha(selection_raw)), 'ACTUAL_ROOT_REVIEW_SELECTION_DESCRIPTOR'
    selected_reviewer = require_review_selection(json.loads(selection_raw), binding)
    verdict_raw = (review_dir / 'VERDICT.json').read_bytes()
    verdict = json.loads(verdict_raw)
    required = dict(schema='dg16.full-g2-current-combined-binding-review.v1', state='FINAL', disposition='PASS',
                    blocking_findings=[], reviewer=selected_reviewer, current_delta_authorship=False,
                    receiver_seal_sha256=receiver_sha256, composition_seal_sha256=composition_sha256,
                    source_commit=binding['source_commit'], source_tree=binding['source_tree'],
                    final_tree=binding['final_tree'], candidate_seal_sha256=binding['candidate_seal_sha256'])
    assert all(type(verdict.get(k)) is type(v) and verdict[k] == v for k, v in required.items()), 'FINAL_EXACT_COMBINED_REVIEW_REQUIRED'
    assert binding['composition_review_seal_sha256'] is None
    assert binding['composition_review_gate'] == 'REQUIRE_LATER_EXACT_FINAL_REVIEW_IN_ROOT_EFFECT_ADMISSION'
    assert binding['composition_seal_sha256'] == composition_sha256
    assert verdict['receiver_binding_sha256'] == sha((receiver_dir / 'BINDING.json').read_bytes())
    assert verdict['admission_gate_sha256'] == sha((receiver_dir / 'admission_gate.py').read_bytes())
    return dict(schema='dg16.current-g2.final-independent-review-admission-check.v1', status='EXACT_FINAL_REVIEW_VERIFIED',
                review_seal_sha256=review_sha256, verdict_sha256=sha(verdict_raw),
                receiver_seal_sha256=receiver_sha256, composition_seal_sha256=composition_sha256,
                source_commit=binding['source_commit'], source_tree=binding['source_tree'], final_tree=binding['final_tree'],
                effect_grant_issued=False, original_acceptance=False)
