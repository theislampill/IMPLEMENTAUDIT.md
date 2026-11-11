"""Read exact prospective independent/root bodies; never create a decision."""
import re
from pathlib import Path

E = _HOST_EVIDENCE_IO
P = _G2_NATIVE_PROFILE
FILES = ('NATIVE_INDEPENDENT_REVIEW.json', 'ROOT_NATIVE_APPLICABILITY_ADOPTION.json')
AUTHORS = ('/root/original_acceptance_audit', '/root/g2_receiver_completion', '/root/source_package', '/root/linux02_delta_review', '/root/g1_access08_author', '/root/g2_public_rebind', '/root/g2_diagnosis')
PREDICATES = ('fixed_receiver_identity', 'wrong_receiver_refusal', 'current_native_intake',
              'later_invalidation_refusal', 'ordinary_host_source_currentness_custody')
TESTS = ('test_native_intake_uses_current_original14_not_retired_root',
         'test_native_intake_later_boundary_prevents_return')
BINDINGS = ('source_commit', 'source_tree', 'source_manifest_sha256', 'source_applicability_sha256',
            'profile_sha256', 'probe_sha256', 'native_receiver_sha256', 'native_admission_sha256',
            'adapter_sha256', 'pair_driver_sha256', 'utility_sha256', 'policy_sha256',
            'receiver_inputs_sha256', 'historical_prerequisite_sha256')
need = E.need


def independent(value):
    return type(value) is str and re.fullmatch(r'/root/[a-z0-9_]+', value) is not None and value not in AUTHORS


def validate(payload, bindings, historical):
    need(type(payload) is dict and set(payload) == set(FILES), 'ACTUAL_NATIVE_REVIEW_OR_ADOPTION_MISSING')
    need(type(bindings) is dict and set(bindings) == set(BINDINGS), 'G2_NATIVE_ADMISSION_BINDING_POPULATION')
    for name, value in bindings.items():
        size = 40 if name in ('source_commit', 'source_tree') else 64
        need(type(value) is str and re.fullmatch('[0-9a-f]{' + str(size) + '}', value),
             'G2_NATIVE_ADMISSION_BINDING_SHAPE')
    need(bindings['source_commit'] == '5f899a653df20073ed6691f898d9c9f630f0c100'
         and bindings['source_tree'] == 'e7af9906e32eea314e33bddb7aeaf6bcff9242b0',
         'G2_NATIVE_ADMISSION_SOURCE')
    need(type(historical) is dict and set(historical) == set(P.HOST_FIELDS), 'G2_NATIVE_ADMISSION_HOST_REFERENCE')
    for raw in payload.values():
        need(type(raw) is bytes and 0 < len(raw) <= 65536, 'G2_NATIVE_ADMISSION_BODY_BOUND')
    review_raw, adoption_raw = (payload[name] for name in FILES)
    review, adoption = E.parse(review_raw), E.parse(adoption_raw)
    common = dict(profile=P.PROFILE, predicates=list(PREDICATES), maintained_cases=list(TESTS),
        host_fields=list(P.MATCH_FIELDS), historical_host_profile_sha256=E.sha(E.encode(historical)),
        retained_unchanged_members=86, changed_members=3, current_only=True, **bindings)
    expected = dict(schema='dg16.g2-current-native-independent-review.v1', authority='NONE',
        decision='PASS', scope='EXACT_CURRENT_ONLY_ORDINARY_G2_SOURCE_HOST_BODY_RECEIVING',
        blocking_findings=[], **common)
    need(type(review) is dict and set(review) == set(expected) | {'reviewer', 'candidate_seal_sha256'}
         and all(type(review[k]) is type(v) and review[k] == v for k, v in expected.items())
         and independent(review['reviewer']) and type(review['candidate_seal_sha256']) is str
         and re.fullmatch('[0-9a-f]{64}', review['candidate_seal_sha256']), 'G2_NATIVE_INDEPENDENT_REVIEW_REQUIRED')
    expected = dict(schema='dg16.g2-current-native-root-applicability-adoption.v1', author='/root',
        decision='ADOPT_FOR_ONE_EXACT_PROSPECTIVE_EPISODE', one_shot=True,
        independent_review_sha256=E.sha(review_raw), independent_reviewer=review['reviewer'],
        candidate_seal_sha256=review['candidate_seal_sha256'],
        unchanged_host_fields_required=True, changed_host_requires_separate_qualification=True,
        historical_receipt_transfer=False, all_89_equal=False, nine_case_replay_selected=False,
        full_G1_required=False, full_G3_required=False, natural_RLGWO_required=False,
        product_limits_changed=False, original_awards=[], **common)
    need(type(adoption) is dict and set(adoption) == set(expected) | {'independent_review_seal_sha256'}
         and all(type(adoption[k]) is type(v) and adoption[k] == v for k, v in expected.items())
         and type(adoption['independent_review_seal_sha256']) is str
         and re.fullmatch('[0-9a-f]{64}', adoption['independent_review_seal_sha256']),
         'G2_NATIVE_ROOT_APPLICABILITY_ADOPTION_REQUIRED')
    return dict(schema='dg16.g2-current-native-admission-readback.v1', authority='NONE',
        source_commit=bindings['source_commit'], source_tree=bindings['source_tree'], profile=P.PROFILE,
        review_sha256=E.sha(review_raw), adoption_sha256=E.sha(adoption_raw), reviewer=review['reviewer'],
        candidate_seal_sha256=review['candidate_seal_sha256'], bindings=bindings,
        historical_host_profile_sha256=common['historical_host_profile_sha256'],
        one_shot=True, current_only=True, original_awards=[])


def read(directory, bindings, historical):
    directory = Path(directory)
    try:
        payload = {name: E.read_packet(directory / name, 65536) for name in FILES}
    except FileNotFoundError:
        raise E.Refusal('ACTUAL_NATIVE_REVIEW_OR_ADOPTION_MISSING') from None
    result = validate(payload, bindings, historical)
    need(all(E.read_packet(directory / name, 65536) == raw for name, raw in payload.items()),
         'G2_NATIVE_ADMISSION_BODY_CHANGED')
    return result, payload
