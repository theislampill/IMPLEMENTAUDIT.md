"""Exact independent-review and root-policy data gate; never writes a decision."""
import hashlib
import json
import re

AUTHOR = '/root/linux02_delta_review'
DECISION_FILES = ('INDEPENDENT_COLD_REVIEW.json', 'ROOT_POLICY_ADOPTION.json')


class Refusal(ValueError):
    pass


def need(value, code):
    if not value: raise Refusal(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def parse(raw):
    need(type(raw) is bytes and 0 < len(raw) <= 65536, 'POLICY_RECORD_BOUND')
    def pairs(items):
        value = {}
        for key, item in items:
            need(key not in value, 'POLICY_RECORD_DUPLICATE_KEY'); value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refusal('POLICY_RECORD_NONFINITE')))


def digest(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def independent(identity):
    return type(identity) is str and re.fullmatch(r'/root/[a-z0-9_]+', identity) is not None and identity != AUTHOR


def validate(payload, bindings, policy):
    need(set(payload) == set(DECISION_FILES), 'POLICY_DECISION_POPULATION')
    review_raw, adoption_raw = (payload[name] for name in DECISION_FILES)
    review, adoption = parse(review_raw), parse(adoption_raw)
    expected = {'schema': 'dg16.full-correspondence-code-review.v1', 'decision': 'PASS',
                'authority': 'NONE', 'blocking_findings': [],
                'scope': 'EXACT_IMMUTABLE_FULL_CORRESPONDENCE_CODE_AND_POLICY', **bindings}
    need(type(review) is dict and set(review) == set(expected) | {'reviewer', 'candidate_seal_sha256'} and
         all(type(review[k]) is type(v) and review[k] == v for k, v in expected.items()) and
         independent(review['reviewer']) and digest(review['candidate_seal_sha256']), 'EXACT_INDEPENDENT_CODE_REVIEW_REQUIRED')
    expected = {'schema': 'dg16.full-correspondence-root-policy-adoption.v1', 'author': '/root',
                'decision': 'ADOPT_FOR_ONE_EXACT_PROSPECTIVE_EPISODE', 'one_shot': True,
                'candidate_seal_sha256': review['candidate_seal_sha256'],
                'independent_review_sha256': sha(review_raw), 'independent_reviewer': review['reviewer'],
                'finite_rules_unchanged': 13, 'finite_narrowings_unchanged': 6,
                'new_rules': [row['id'] for row in policy['new_rules']],
                'full_applicability': policy['full_applicability'], 'product_limits_changed': False,
                'original_acceptance_granted': False, **bindings}
    need(type(adoption) is dict and set(adoption) == set(expected) | {'independent_review_seal_sha256'} and
         all(type(adoption[k]) is type(v) and adoption[k] == v for k, v in expected.items()) and
         digest(adoption['independent_review_seal_sha256']), 'EXACT_ROOT_POLICY_ADOPTION_REQUIRED')
    return {'schema': 'dg16.actual-policy-gate-readback.v1', 'authority': 'NONE',
            'decision': 'EXACT_ROOT_ADOPTION_AND_INDEPENDENT_REVIEW_RECEIVED',
            'adoption_sha256': sha(adoption_raw), 'review_sha256': sha(review_raw),
            'reviewer': review['reviewer'], 'candidate_seal_sha256': review['candidate_seal_sha256'],
            'policy_sha256': bindings['policy_sha256'], 'receiver_inputs_sha256': bindings['receiver_inputs_sha256'],
            'source_commit': bindings['source_commit'], 'source_tree': bindings['source_tree'],
            'one_shot': True, 'original_acceptance_granted': False}
