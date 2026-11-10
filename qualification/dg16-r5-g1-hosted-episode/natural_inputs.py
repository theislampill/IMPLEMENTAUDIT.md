"""Body acquisition seam for original RLGWO input scope, without L04 awards.

Full G2/Q02 is a separate DG16 conjunction. This module does not require the
whole current G2 private archive merely because G2 and G3 use different hosts.
The admitted original comparison scope, its actual bytes and applicability
must be received explicitly before a natural G3 successor can consume them.
"""
from pathlib import Path

E = _HOST_EVIDENCE_IO
SOURCE_COMMIT = '19c222a2db624de15b77415481f34f3d7a4475a7'
SOURCE_TREE = '714407ef4284174786340c087624f92ef19967c0'


def receive(root, binding_raw, *, expected_binding_sha256):
    E.need(E.sha(binding_raw) == expected_binding_sha256, 'NATURAL_BINDING_PIN_REFUSED')
    value = E.parse(binding_raw)
    E.need(value.get('schema') == 'dg16.original-rlgwo-body-input-binding.v1'
           and value.get('state') == 'EXACT_RECEIVED_INPUT_SCOPE'
           and value.get('owner_amendment') == 5638756153
           and value.get('consumer_source_commit') == SOURCE_COMMIT
           and value.get('consumer_source_tree') == SOURCE_TREE,
           'NATURAL_INPUT_SCOPE_NOT_RECEIVED')
    E.need(value.get('full_g2_relation') == 'INDEPENDENT_DG16_Q02_REQUIREMENT'
           and value.get('currentness_transfer') is False and value.get('original_awards') == [],
           'NATURAL_INPUT_SCOPE_PROMOTION_REFUSED')
    members = value.get('members')
    root = Path(root)
    before = E.bind_bodies(root, members)
    roles = value.get('roles')
    required = {'completed_comparison', 'source_applicability', 'original_scope_receiving', 'acquisition'}
    E.need(type(roles) is dict and required <= set(roles)
           and all(type(names) is list and names and len(names) == len(set(names))
                   and all(name in members for name in names) for names in roles.values()),
           'NATURAL_REQUIRED_BODY_ROLE_MISSING')
    acquisition_name = roles['acquisition']
    E.need(len(acquisition_name) == 1, 'NATURAL_ACQUISITION_POPULATION')
    acquisition_raw = E.read(root / acquisition_name[0])
    acquisition = E.parse(acquisition_raw)
    E.need(acquisition.get('schema') == 'dg16.original-comparison-body-acquisition.v1'
           and acquisition.get('status') == 'ACTUAL_BYTES_RECEIVED_AT_DECLARED_SCOPE'
           and acquisition.get('members') == {name: members[name] for name in value.get('acquired_members', [])}
           and set(value.get('acquired_members', [])) >= set(roles['completed_comparison'])
           and acquisition.get('source_identity') == value.get('producer_source_identity')
           and acquisition.get('scope') == value.get('original_comparison_scope'),
           'NATURAL_BODY_ACQUISITION_NOT_ESTABLISHED')
    mode = value.get('acquisition_mode')
    E.need(mode in ('RETAINED_BODY_RECEIVING', 'ADMITTED_PRIVATE_TRANSFER_RECEIVING'),
           'NATURAL_ACQUISITION_MODE_REFUSED')
    if mode == 'ADMITTED_PRIVATE_TRANSFER_RECEIVING':
        E.need('private_transfer_admission' in roles and len(roles['private_transfer_admission']) == 1,
               'PRIVATE_TRANSFER_ADMISSION_REQUIRED')
        grant = E.parse(E.read(root / roles['private_transfer_admission'][0]))
        E.need(grant.get('schema') == 'dg16.exact-private-body-transfer-admission.v1'
               and grant.get('members') == acquisition['members']
               and grant.get('donor_host_identity') == acquisition.get('donor_host_identity')
               and grant.get('receiving_host_identity') == acquisition.get('receiving_host_identity')
               and grant.get('publication') == 'PRIVATE_ONLY_NO_PUBLIC_RAW_EXPORT'
               and grant.get('currentness_transfer') is False,
               'PRIVATE_TRANSFER_SCOPE_REFUSED')
        E.need(acquisition.get('complete_bytes') is True and acquisition.get('donor_closure_received') is True,
               'PRIVATE_TRANSFER_ACTUAL_CLOSURE_REQUIRED')
    # The original semantic adequacy remains the separately received root scope.
    # Read it, do not infer it from BWP/G2 names or a completed-label field.
    E.need(len(roles['original_scope_receiving']) == 1 and len(roles['source_applicability']) == 1,
           'NATURAL_RECEIVING_ROLE_POPULATION')
    receiving_raw = E.read(root / roles['original_scope_receiving'][0])
    applicability_raw = E.read(root / roles['source_applicability'][0])
    receiving = E.parse(receiving_raw)
    relation = E.parse(applicability_raw)
    E.need(receiving.get('schema') == 'dg16.original-rlgwo-input-scope-receiving.v1'
           and receiving.get('owner_amendment') == 5638756153
           and receiving.get('completed_comparison_members') == {name: members[name] for name in roles['completed_comparison']}
           and receiving.get('source_applicability_sha256') == E.sha(applicability_raw)
           and receiving.get('acquisition_sha256') == E.sha(acquisition_raw)
           and receiving.get('status') == 'ORIGINAL_COMPARISON_INPUT_SCOPE_RECEIVED'
           and receiving.get('original_L04_award') is False, 'ORIGINAL_RLGWO_INPUT_RECEIVING_REQUIRED')
    E.need(relation.get('schema') == 'dg16.original-comparison-source-applicability.v1'
           and relation.get('producer_source_identity') == value.get('producer_source_identity')
           and relation.get('consumer_source_commit') == SOURCE_COMMIT
           and relation.get('consumer_source_tree') == SOURCE_TREE
           and relation.get('scope') == value.get('original_comparison_scope')
           and relation.get('currentness_transfer') is False, 'NATURAL_SOURCE_RELATION_REFUSED')
    E.need(E.bind_bodies(root, members) == before, 'NATURAL_BODY_CLOSING_CHANGED')
    return dict(schema='dg16.original-comparison-local-body-readback.v1', authority='NONE',
                input_binding_sha256=E.sha(binding_raw), bodies=before,
                receiving_sha256=E.sha(receiving_raw), acquisition_mode=mode,
                full_g2_relation='INDEPENDENT_DG16_Q02_REQUIREMENT',
                currentness_transfer=False, native_natural_transition_proven=False, original_awards=[])
