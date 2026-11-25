"""Fixed core G1/Q06 composition at V21; natural L04 remains separately unreceived.

V21 route: every input body is acquired by the pinned public-input selector
(public_inputs.py) from the exact index; the encrypted carrier and private
sender are not part of this population. Replacing a binding requires new exact
packet pins and independent whole-host receiving, not a runtime override.
"""
from pathlib import Path
import os
import re

E = _HOST_EVIDENCE_IO
R = _ROOT_PLACEMENT
S = _PUBLIC_INPUTS
BINDING_SHA256 = 'ed058bc3e63f59dc8a05638efcf1432380fbcfd8541c461ae93050bf7ca1ec39'
SOURCE_COMMIT = '338c4c36d2ac95ca24345bc92fe8c53d66eaa15d'
SOURCE_TREE = '53498df783ed441744ae5080982c2d5e59c34bbc'
SUBJECT = dict(commit=SOURCE_COMMIT, tree=SOURCE_TREE)
SUCCESSOR = 'OPUS-5.5-DG16, sole DG16 executor designated by owner'
CORE_SCOPE = 'CORE_G1_Q06_NATURAL_L04_SEPARATE'
NATURAL_SCOPE = 'ORIGINAL_RLGWO_PREREQUISITE_AND_NATURAL_SHAPE_NOT_RECEIVED'
CORE_OPERATION = 'ONE_ORIGINAL_G1_PAIR_AND_TWO_STAGE_CORE_G3_L04_SEPARATE'
RECEIVING = 'handoff/astra-dg16-dg18/V21_PUBLIC_RECEIVING/'
ROLE_NAMES = {1: 'COMPOSITION_ROOT_ADMISSION.json', 2: 'COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json',
    3: 'COMPOSITION_PLACEMENT_RECEIVING.json', 4: 'PLACEMENT_EVIDENCE_INDEX.json', 5: 'PLACEMENT_DIAGNOSTIC.json',
    6: 'PLACEMENT_INDEPENDENT_RECEIVING.json', 7: 'PLACEMENT_ROOT_RECEIVING.json', 8: 'SOURCE_ACQUISITION.json',
    9: 'PACKAGE_TERMINAL_RECEIVING.json', 10: 'PACKAGE_BODY_RECEIVING.json', 11: 'PACKAGE_ROOT_RECEIVING.json'}
ARTIFACT_MANIFEST = 'PLACEMENT_ARTIFACT_MANIFEST.json'
PLACEMENT_RUN = dict(run=45600842791, attempt=1, job=139159019005, artifact=15014764482)
PLACEMENT_OPERATOR = 'ef29f80ed69dcf35f7efdd0329526c8012df5813'
PLACEMENT_ZIP_SHA256 = '747bc69fc5b52b87c3c6ebc61d2b82f17c56f37c22bbf01097256deb43a60548'
DIAGNOSED_PLACEMENT_MODULE_SHA256 = '18a93f8206a42435f73580ca65cf16d20dad96cb337b84a6d30104cce772ad4a'
PROPERTIES = ('P1_ROOT_CREDENTIALS', 'P2_ROOT_ANCESTOR_CUSTODY', 'P3_EXCLUSIVE_FRESH_ISLAND', 'P4_FIXED_SIBLINGS',
              'P5_FD_ROUTE', 'P6_ANCESTRY_NO_DRIFT', 'P7_CLOSING_CURRENTNESS')
NATIVE_PREDICATES = ('fixed_receiver_identity', 'wrong_receiver_refusal', 'current_native_intake',
                     'later_invalidation_refusal', 'host_and_diagnosed_intake')
ADOPTION_REVIEW = 'a110768823dbd936157ea50037d85b43fcb92cbc'
BRIDGE_COMMIT = 'bab695df767276fbe8b133aa35b05b1c8c93d290'
APPLICABILITY_POPULATION = dict(commit=BRIDGE_COMMIT,
    path='handoff/opus-dg16-v21-applicability-20261125/inputs/NATIVE_SOURCE_APPLICABILITY.V21-COMPUTABLE.json',
    bytes=38923, sha256='9a073972b3f0599b1ddc9ce98a9643ef27414fa6b168fa7aa1b0b7bd24326033')
REPLACED_FIELDS = ['compiler_normalized_ast_sha256', 'receiver_non_windows_ast_sha256', 'semantic_report_sha256']


def binding():
    path = Path(__file__).with_name('HOST_COMPOSITION.json')
    raw = E.read_packet(path)
    E.need(E.sha(raw) == BINDING_SHA256, 'COMPOSITION_PIN_REFUSED')
    value = E.parse(raw)
    expected = {'schema', 'authority', 'effects_authorized', 'source_commit', 'source_tree',
                'state', 'workflow_branch', 'control_branch', 'source_branch', 'component_scope', 'natural_scope',
                'full_g2_relation', 'original_awards', 'root_scope_clarification_sha256', 'whole_host_review',
                'placement', 'public_input_index', 'input_route', 'successor'}
    E.need(type(value) is dict and set(value) == expected, 'CORE_COMPOSITION_FIELDS')
    E.need(value.get('schema') == 'dg16.current-g1-g3-fixed-root-core-composition.v3'
           and value.get('source_commit') == SOURCE_COMMIT and value.get('source_tree') == SOURCE_TREE
           and value.get('successor') == SUCCESSOR,
           'COMPOSITION_SUBJECT_REFUSED')
    E.need(value['component_scope'] == CORE_SCOPE and value['natural_scope'] == NATURAL_SCOPE
           and value['full_g2_relation'] == 'INDEPENDENT_DG16_Q02_REQUIREMENT'
           and value['authority'] == 'NONE' and value['effects_authorized'] is False
           and value['original_awards'] == []
           and value['input_route'] == 'PINNED_PUBLIC_INPUT_SELECTOR_NO_CARRIER_NO_PRIVATE_SENDER'
           and value['root_scope_clarification_sha256'] == '86d043c05fd6313f970d141395a6ec0fdaac8c145e9c83e429a7745430a4845c'
           and value['whole_host_review'] == 'EXTERNAL_PRELAUNCH_GATE_NOT_A_SELF_REFERENTIAL_HASH_INPUT',
           'CORE_COMPONENT_SCOPE_REQUIRED')
    return value


def paths(value, context):
    E.need(value.get('state') == 'REVIEWED_EXACT_COMPOSITION'
           and type(value.get('placement')) is dict, 'PLACEMENT_NOT_QUALIFIED')
    E.need(value['placement'] == dict(profile=R.PROFILE,
        source_template='/dg16-g1-{run_id}/source', private_output_template='/dg16-g1-{run_id}/output',
        packet_template='/dg16-g1-{run_id}/packet'), 'FIXED_ROOT_PLACEMENT_REQUIRED')
    return R.paths(context)


def _receiving_ref(name, raw):
    return dict(path=RECEIVING + name, bytes=len(raw), sha256=E.sha(raw))


def check_admission(raw, bodies, support, context):
    """Role 1 is Root's last issuance on the fixed inputs and operation (prospective contract)."""
    admission = E.parse(raw)
    E.need(type(admission) is dict and set(admission) == {'schema', 'issuer', 'successor', 'source_commit', 'source_tree',
           'workflow_branch', 'control_branch', 'source_branch', 'run_attempt', 'automatic_retry', 'original_awards',
           'prospective_operation', 'component_scope', 'input_route', 'input_sha256'}, 'CORE_ADMISSION_FIELDS')
    E.need(admission.get('schema') == 'dg16.current-core-host-root-admission.v2'
           and admission['issuer'] == 'R5_ROOT_GOVERNOR' and admission['successor'] == SUCCESSOR
           and admission['component_scope'] == CORE_SCOPE
           and admission.get('source_commit') == SOURCE_COMMIT and admission.get('source_tree') == SOURCE_TREE
           and admission.get('workflow_branch') == context['branch']
           and admission.get('run_attempt') == 1 and admission.get('automatic_retry') is False
           and admission.get('original_awards') == []
           and admission.get('input_route') == 'PINNED_PUBLIC_INPUT_SELECTOR_NO_CARRIER_NO_PRIVATE_SENDER'
           and admission.get('prospective_operation') == CORE_OPERATION,
           'ROOT_ADMISSION_SCOPE_REFUSED')
    expected = {ROLE_NAMES[role]: E.sha(body) for role, body in bodies.items() if role != 1}
    expected.update({name: E.sha(body) for name, body in support.items()})
    E.need(admission.get('input_sha256') == expected, 'ROOT_ADMISSION_BODY_BINDING')
    return admission


def check_native_adoption(raw, packet):
    """Role 2: Root's bounded source-applicability adoption (not native qualification)."""
    adopted = E.parse(raw)
    E.need(type(adopted) is dict and set(adopted) == {'issuer', 'decision', 'subject', 'independent_review_delivery',
        'comparison', 'comparison_pairs', 'replaces_for_this_operator', 'limits', 'population', 'bridge',
        'unchanged_members', 'changed_members', 'reviewed_changed_member_rows', 'counts', 'native_predicates',
        'native_qualification', 'windows_qualification', 'new_operation_grants', 'original_awards'},
        'NATIVE_APPLICABILITY_ADOPTION_FIELDS')
    applicability_raw = E.read_packet(packet / 'NATIVE_SOURCE_APPLICABILITY.json')
    applicability = E.parse(applicability_raw)
    changed = sorted(r['path'] for r in applicability['members'] if r['retained_unchanged'] is False)
    rows = adopted['reviewed_changed_member_rows']
    E.need(adopted['issuer'] == 'Astra Root' and adopted['decision'] == 'ADOPTED_FOR_SOURCE_APPLICABILITY_ONLY'
           and adopted['subject'] == SUBJECT and adopted['independent_review_delivery'] == ADOPTION_REVIEW
           and adopted['population'] == APPLICABILITY_POPULATION
           and len(applicability_raw) == APPLICABILITY_POPULATION['bytes']
           and E.sha(applicability_raw) == APPLICABILITY_POPULATION['sha256']
           and adopted['replaces_for_this_operator'] == REPLACED_FIELDS
           and adopted['unchanged_members'] == applicability['unchanged_count'] == 69
           and adopted['changed_members'] == applicability['changed_count'] == 20 == len(changed)
           and type(rows) is dict and sorted(rows) == changed
           and all(v in ('COVERED', 'PARTIAL') for v in rows.values())
           and adopted['counts'] == dict(COVERED=sum(v == 'COVERED' for v in rows.values()),
                                         PARTIAL=sum(v == 'PARTIAL' for v in rows.values()), OPEN=0)
           and adopted['native_predicates'] == {name: 'OPEN' for name in NATIVE_PREDICATES}
           and adopted['native_qualification'] is False and adopted['windows_qualification'] == 'DG18_SEPARATE'
           and adopted['new_operation_grants'] == [] and adopted['original_awards'] == [],
           'NATIVE_APPLICABILITY_ADOPTION_REQUIRED')
    E.need(applicability.get('source_commit') == SOURCE_COMMIT and applicability.get('source_tree') == SOURCE_TREE
           and applicability.get('schema') == 'dg16.current-native-source-applicability.v1'
           and applicability.get('native_qualification') is False, 'NATIVE_APPLICABILITY_POPULATION_SUBJECT')
    return adopted


def check_placement(bodies, support):
    """Roles 3-7: Root's diagnostic-scope placement receiving; the core still checks its own live placement."""
    r2, r3, r4, r5, r6, r7 = (bodies[n] for n in (2, 3, 4, 5, 6, 7))
    scope = E.parse(r3)
    E.need(scope == dict(issuer='Astra Root', subject=SUBJECT, decision='ACCEPTED_PUBLIC_REPLACEMENT_AT_DIAGNOSTIC_SCOPE',
        observed_run=PLACEMENT_RUN['run'], attempt=1, job=PLACEMENT_RUN['job'], artifact=PLACEMENT_RUN['artifact'],
        cause='UNPROVED', placement_evidence_index=_receiving_ref(ROLE_NAMES[4], r4),
        source_applicability_adoption=_receiving_ref(ROLE_NAMES[2], r2),
        native_transfer='NONE; core must check its actual current placement and complete the five native prerequisite predicates',
        original_awards=[]), 'WORKING_PLACEMENT_SCOPE_REFUSED')
    index = E.parse(r4)
    E.need(index == dict(product=SUBJECT, run=PLACEMENT_RUN['run'], scope='PUBLIC_PLACEMENT_DIAGNOSTIC_ONLY',
        roles={'5': _receiving_ref(ROLE_NAMES[5], r5), '6': _receiving_ref(ROLE_NAMES[6], r6),
               '7': _receiving_ref(ROLE_NAMES[7], r7)}), 'EXACT_WORKING_PLACEMENT_INDEX_REQUIRED')
    receipt = E.parse(r5)
    E.need(receipt.get('schema') == 'dg16.placement-only-diagnostic-receipt.v2' and receipt.get('status') == 'COMPLETE'
           and receipt.get('authority') == 'NONE' and receipt.get('failure') is None and receipt.get('cause') == 'UNPROVED'
           and receipt.get('profile') == R.PROFILE and receipt.get('original_awards') == []
           and receipt.get('context') == dict(branch='engineering/opus-dg16-placement-diag-trigger-20261125', run_attempt=1,
                                              run_id=str(PLACEMENT_RUN['run']), workflow_commit=PLACEMENT_OPERATOR)
           and receipt.get('recorded_subject', {}).get('commit') == SOURCE_COMMIT
           and receipt.get('recorded_subject', {}).get('tree') == SOURCE_TREE
           and receipt.get('modules', {}).get('root_placement', {}).get('sha256') == DIAGNOSED_PLACEMENT_MODULE_SHA256
           and receipt.get('properties') == {p: 'OBSERVED' for p in PROPERTIES}, 'PLACEMENT_DIAGNOSTIC_RECEIPT_REFUSED')
    independent = E.parse(r6)
    E.need(independent.get('schema') == 'dg16.placement-only-diagnostic-receiving.v2'
           and independent.get('status') == 'RECEIVED_AT_DIAGNOSTIC_SCOPE' and independent.get('authority') == 'NONE'
           and independent.get('cause') == 'UNPROVED' and independent.get('original_awards') == []
           and independent.get('commit') == PLACEMENT_OPERATOR and independent.get('run_id') == PLACEMENT_RUN['run']
           and independent.get('job_id') == PLACEMENT_RUN['job'] and independent.get('artifact_id') == PLACEMENT_RUN['artifact']
           and independent.get('artifact_zip_sha256') == PLACEMENT_ZIP_SHA256
           and independent.get('receipt') == dict(bytes=len(r5), sha256=E.sha(r5))
           and independent.get('replaces') == 'NOTHING_WITHOUT_NEW_ROOT_COMPOSITION'
           and independent.get('file_pins', {}).get('qualification/dg16-placement-diagnostic/root_placement.py')
               == DIAGNOSED_PLACEMENT_MODULE_SHA256
           and independent.get('properties') == {p: 'REDERIVED' for p in PROPERTIES}, 'PLACEMENT_INDEPENDENT_RECEIVING_REFUSED')
    manifest_raw = support[ARTIFACT_MANIFEST]
    E.need(E.parse(manifest_raw) == dict(schema='dg16.placement-only-diagnostic-artifacts.v1',
           members=[dict(bytes=len(r5), name='RECEIPT.json', sha256=E.sha(r5))]), 'PLACEMENT_ARTIFACT_MANIFEST_REFUSED')
    root = E.parse(r7)
    E.need(type(root) is dict and root.get('issuer') == 'Astra Root'
           and root.get('decision') == 'ACCEPTED_AT_HOST_PLACEMENT_DIAGNOSTIC_SCOPE' and root.get('subject') == SUBJECT
           and root.get('operator_commit') == PLACEMENT_OPERATOR and root.get('run_id') == PLACEMENT_RUN['run']
           and root.get('attempt') == 1 and root.get('job_id') == PLACEMENT_RUN['job']
           and root.get('artifact_id') == PLACEMENT_RUN['artifact'] and root.get('provider_zip_sha256') == PLACEMENT_ZIP_SHA256
           and root.get('artifact_manifest') == _receiving_ref(ARTIFACT_MANIFEST, manifest_raw)
           and root.get('role_5') == _receiving_ref(ROLE_NAMES[5], r5) and root.get('role_6') == _receiving_ref(ROLE_NAMES[6], r6)
           and root.get('properties') == {p: 'REDERIVED' for p in PROPERTIES} and root.get('cause') == 'UNPROVED'
           and root.get('live_decisions_issued') == 0 and root.get('new_operation_grants') == []
           and root.get('original_awards') == [], 'PLACEMENT_ROOT_RECEIVING_REFUSED')
    return dict(scope=scope, index=index, receipt=receipt, independent=independent, root=root)


def require_launch(packet, source, output, context, g3, *, phase='live'):
    """Before clone, setup, controller creation, NSS change or any native call."""
    selected = S.admit(packet)  # first HELD role refuses here, before any body is read
    value = binding()
    E.need(value['public_input_index'] == dict(path=S.INDEX_NAME, sha256=selected['index_sha256']),
           'COMPOSITION_PUBLIC_INDEX_BINDING')
    E.need(value.get('state') == 'REVIEWED_EXACT_COMPOSITION', 'CURRENT_HOST_COMPOSITION_UNRESOLVED')
    wanted = paths(value, context)
    E.need(wanted == dict(source=source, private_output=output, packet=packet), 'COMPOSITION_PLACEMENT_MISMATCH')
    E.need(value.get('workflow_branch') == context['branch'], 'COMPOSITION_WORKFLOW_MISMATCH')
    E.need(g3.NATURAL_SCOPE == value['natural_scope'] == NATURAL_SCOPE
           and value['component_scope'] == CORE_SCOPE, 'CORE_COMPONENT_SCOPE_REQUIRED')
    E.need(selected['names'] == ROLE_NAMES and set(selected['support']) == {ARTIFACT_MANIFEST}, 'FIXED_COMPOSITION_ROLE_PATH')
    bodies, support = selected['bodies'], selected['support']
    check_admission(bodies[1], bodies, support, context)
    check_native_adoption(bodies[2], packet)
    placement = check_placement(bodies, support)
    E.need(S.admit(packet)['bodies'] == bodies, 'PUBLIC_INPUT_CLOSING_CHANGED')
    custody = R.require_current(context, packet, phase=phase)
    E.need(len(os.sched_getaffinity(0)) >= 2, 'DECLARED_HOST_CAPACITY_UNAVAILABLE')
    staged = dict(root_admission=bodies[1], placement_receiving=bodies[3], placement_evidence_index=bodies[4],
                  native_applicability_adoption=bodies[2])
    return dict(binding=value, bodies=staged, placement_bodies={ROLE_NAMES[n]: bodies[n] for n in (5, 6, 7)},
                placement=placement, public_inputs=selected, custody=custody)


def check_placement_current(source, output, admission, context):
    """Exact fresh ancestry/ACL/owner/mode observations, with no ancestor repair."""
    value = binding()
    wanted = paths(value, context)
    E.need(wanted['source'] == source and wanted['private_output'] == output,
           'FIXED_ROOT_PLACEMENT_CHANGED')
    E.need(admission.get('source_commit') == SOURCE_COMMIT and admission.get('source_tree') == SOURCE_TREE,
           'PLACEMENT_ADMISSION_CHANGED')
    return R.require_current(context, wanted['packet'], phase='live')
