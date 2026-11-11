"""Fixed core G1/Q06 composition; natural L04 remains separately unreceived.

The shipped binding is explicitly unresolved. Replacing it requires new exact
packet pins and independent whole-host receiving, not a runtime override.
"""
from pathlib import Path
import os
import re

E = _HOST_EVIDENCE_IO
R = _ROOT_PLACEMENT
BINDING_SHA256 = '9d43b693d725c75175ebe776be8f99f0fb7ce3a5e30211898a333bfd70a4f17b'
SOURCE_COMMIT = '32f659266b5a08fddb1a0a398eb3eabf0b20e313'
SOURCE_TREE = 'd58e3aba361339cc922cba36a1a544cb6ad8bcd8'
CORE_SCOPE = 'CORE_G1_Q06_NATURAL_L04_SEPARATE'
NATURAL_SCOPE = 'ORIGINAL_RLGWO_PREREQUISITE_AND_NATURAL_SHAPE_NOT_RECEIVED'
CORE_OPERATION = 'ONE_ORIGINAL_G1_PAIR_AND_TWO_STAGE_CORE_G3_L04_SEPARATE'


def binding():
    path = Path(__file__).with_name('HOST_COMPOSITION.json')
    raw = E.read_packet(path)
    E.need(E.sha(raw) == BINDING_SHA256, 'COMPOSITION_PIN_REFUSED')
    value = E.parse(raw)
    expected = {'schema', 'authority', 'effects_authorized', 'source_commit', 'source_tree',
                'state', 'workflow_branch', 'component_scope', 'natural_scope', 'full_g2_relation',
                'original_awards', 'root_scope_clarification_sha256', 'whole_host_review', 'placement',
                'root_admission', 'placement_receiving', 'placement_evidence_index', 'native_applicability_adoption'}
    E.need(type(value) is dict and set(value) == expected, 'CORE_COMPOSITION_FIELDS')
    E.need(value.get('schema') == 'dg16.current-g1-g3-fixed-root-core-composition.v2'
           and value.get('source_commit') == SOURCE_COMMIT and value.get('source_tree') == SOURCE_TREE,
           'COMPOSITION_SUBJECT_REFUSED')
    E.need(value['component_scope'] == CORE_SCOPE and value['natural_scope'] == NATURAL_SCOPE
           and value['full_g2_relation'] == 'INDEPENDENT_DG16_Q02_REQUIREMENT'
           and value['authority'] == 'NONE' and value['effects_authorized'] is False
           and value['original_awards'] == []
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


def received_input(packet, descriptor):
    E.need(type(descriptor) is dict and set(descriptor) == {'path', 'bytes', 'sha256'},
           'COMPOSITION_BODY_DESCRIPTOR_REQUIRED')
    E.safe_name(descriptor['path'])
    raw = E.read_packet(packet / descriptor['path'], 16 * 1024**2)
    E.need(len(raw) == descriptor['bytes'] and E.sha(raw) == descriptor['sha256'],
           'COMPOSITION_ACTUAL_BODY_CHANGED')
    return raw


def require_launch(packet, source, output, context, g3, *, phase='live'):
    """Before clone, setup, controller creation, NSS change or any native call."""
    value = binding()
    E.need(value.get('state') == 'REVIEWED_EXACT_COMPOSITION', 'CURRENT_HOST_COMPOSITION_UNRESOLVED')
    wanted = paths(value, context)
    E.need(wanted == dict(source=source, private_output=output, packet=packet), 'COMPOSITION_PLACEMENT_MISMATCH')
    E.need(value.get('workflow_branch') == context['branch'], 'COMPOSITION_WORKFLOW_MISMATCH')
    E.need(g3.NATURAL_SCOPE == value['natural_scope'] == NATURAL_SCOPE
           and value['component_scope'] == CORE_SCOPE, 'CORE_COMPONENT_SCOPE_REQUIRED')
    required = ('root_admission', 'placement_receiving', 'placement_evidence_index',
                'native_applicability_adoption')
    role_names = dict(root_admission='COMPOSITION_ROOT_ADMISSION.json',
        placement_receiving='COMPOSITION_PLACEMENT_RECEIVING.json',
        placement_evidence_index='COMPOSITION_PLACEMENT_EVIDENCE_INDEX.json',
        native_applicability_adoption='COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json')
    for name in required:
        E.need(type(value.get(name)) is dict and value[name].get('path') == 'private-inputs/' + role_names[name],
               'FIXED_COMPOSITION_ROLE_PATH')
    bodies = {name: received_input(packet, value.get(name)) for name in required}
    # Immutable root receiving is the source of prospective authority, not a
    # favorable status supplied by this program. Its exact bytes must have been
    # bound in the reviewed composition, including these exact input digests.
    admission = E.parse(bodies['root_admission'])
    E.need(type(admission) is dict and set(admission) == {'schema', 'issuer', 'source_commit', 'source_tree',
           'workflow_branch', 'run_attempt', 'automatic_retry', 'original_awards', 'prospective_operation',
           'component_scope', 'input_sha256'}, 'CORE_ADMISSION_FIELDS')
    E.need(admission.get('schema') == 'dg16.current-core-host-root-admission.v1'
           and admission['issuer'] == 'R5_ROOT_GOVERNOR' and admission['component_scope'] == CORE_SCOPE
           and admission.get('source_commit') == SOURCE_COMMIT and admission.get('source_tree') == SOURCE_TREE
           and admission.get('workflow_branch') == context['branch']
           and admission.get('run_attempt') == 1 and admission.get('automatic_retry') is False
           and admission.get('original_awards') == []
           and admission.get('prospective_operation') == CORE_OPERATION,
           'ROOT_ADMISSION_SCOPE_REFUSED')
    E.need(admission.get('input_sha256') == {name: E.sha(raw) for name, raw in bodies.items() if name != 'root_admission'},
           'ROOT_ADMISSION_BODY_BINDING')
    adopted = E.parse(bodies['native_applicability_adoption'])
    E.need(adopted.get('schema') == 'dg16.current-native-applicability-root-adoption.v1'
           and adopted.get('source_commit') == SOURCE_COMMIT and adopted.get('source_tree') == SOURCE_TREE
           and adopted.get('applicability_sha256') == E.sha(E.read_packet(packet / 'NATIVE_SOURCE_APPLICABILITY.json'))
           and adopted.get('unchanged_members') == 86 and adopted.get('changed_members') == 3
           and adopted.get('windows_qualification') == 'DG18_SEPARATE'
           and adopted.get('original_awards') == [], 'NATIVE_APPLICABILITY_ADOPTION_REQUIRED')
    placement = E.parse(bodies['placement_receiving'])
    E.need(type(placement) is dict and set(placement) == {'schema', 'source_commit', 'source_tree',
        'observed_source_commit', 'placement', 'status', 'cause', 'original_awards', 'evidence_scope',
        'evidence_index_sha256', 'source_applicability_sha256', 'native_transfer'}, 'WORKING_PLACEMENT_FIELDS')
    E.need(placement == dict(schema='dg16.actual-working-root-placement-receiving.v1',
        source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE,
        observed_source_commit='3e0f4b6d05eb086017ce721d40459fdbd68714dd', placement=value['placement'],
        status='ACTUAL_ROOT_ISLAND_FD_ROUTE_RECEIVED_AT_DIAGNOSTIC_SCOPE', cause='UNPROVED', original_awards=[],
        evidence_scope='ACCESS09_RUN42311009492_A1_JOB128212159527_I0_ONLY',
        evidence_index_sha256=E.sha(bodies['placement_evidence_index']),
        source_applicability_sha256=E.sha(bodies['native_applicability_adoption']),
        native_transfer='NONE_FRESH_NATIVE_BANK_AND_ORIGINAL_PAIR_REQUIRED'), 'WORKING_PLACEMENT_SCOPE_REFUSED')
    index = E.parse(bodies['placement_evidence_index'])
    expected_members = {
        'placement/ACCESS09_DIAGNOSTIC.json': dict(bytes=29107, sha256='5a56b0705e77314c587020dda0d45522a68bf5c93d4187281971b13cea4f95ae'),
        'placement/ACCESS09_FINAL.json': dict(bytes=5113, sha256='61d6afe0d5cb5bca26c435c4529788816161d484714ec3e89148d24186b945c1'),
        'placement/ACCESS09_ROOT_RECEIVING.json': dict(bytes=1961, sha256='40ce62326d8e9b759a5db150bf41a99dc77c05580342989aa33e06df2b0bedd3')}
    E.need(type(index) is dict and set(index) == {'schema', 'scope', 'members'}
        and index == dict(schema='dg16.received-placement-evidence-index.v1',
            scope=placement['evidence_scope'], members=expected_members), 'EXACT_WORKING_PLACEMENT_INDEX_REQUIRED')
    acquired = E.bind_bodies(packet / 'private-inputs', index['members'], require_owner=False)
    E.need(acquired and E.bind_bodies(packet / 'private-inputs', index['members'], require_owner=False) == acquired,
           'PLACEMENT_EVIDENCE_CLOSING_CHANGED')
    custody = R.require_current(context, packet, phase=phase)
    E.need(len(os.sched_getaffinity(0)) >= 2, 'DECLARED_HOST_CAPACITY_UNAVAILABLE')
    return dict(binding=value, bodies=bodies, placement_bodies=acquired, custody=custody)


def check_placement_current(source, output, admission, context):
    """Exact fresh ancestry/ACL/owner/mode observations, with no ancestor repair."""
    value = binding()
    wanted = paths(value, context)
    E.need(wanted['source'] == source and wanted['private_output'] == output,
           'FIXED_ROOT_PLACEMENT_CHANGED')
    E.need(admission.get('source_commit') == SOURCE_COMMIT and admission.get('source_tree') == SOURCE_TREE,
           'PLACEMENT_ADMISSION_CHANGED')
    return R.require_current(context, wanted['packet'], phase='live')
