"""Pure successor selection around the original public binder; no issuer act.

Inputs are externally selected descriptors. A matching hash is not authority or
fresh recipient provenance. This module never creates adoption/review bodies,
opens a key, writes files, or admits an effect. The original bind_public checks
remain intact and still require all exact externally issued input bodies.
"""
import hashlib
import re
import types

ORIGINAL_BINDER_SHA256 = 'a6545228f277408d361996b9c7a5d4aecde0e25ea5efe7443f482d535da2e5c3'
ISSUER = 'PRO-EXECUTOR-01'
RETAINED_ADOPTION = '99d3315c8c8cd894f66dc04bfebb7a5519abe232fca3f4205d90a8690e6180df'
RETAINED_RECIPIENT = '1d81ea8b4ff7b906d88dd6e70b28a9c555918dcf7f5b14a6f32c41f557d86cc0'


def need(value, code):
    if not value:
        raise ValueError(code)


def digest(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) and value != '0' * 64


def prepare_binder(original_bytes, adoption_sha256, recipient_descriptor):
    """Prepare exact issuer/adoption selection; do not issue an installation.

    The returned bind_public wrapper first binds the selected new recipient and
    adoption, then delegates to the unchanged original bind_public function.
    The prepared_source field is inspection evidence, not an executable grant.
    """
    need(type(original_bytes) is bytes and
         hashlib.sha256(original_bytes).hexdigest() == ORIGINAL_BINDER_SHA256,
         'ORIGINAL_BINDER_PIN')
    need(digest(adoption_sha256) and type(recipient_descriptor) is dict and
         set(recipient_descriptor) == {'bytes', 'sha256'} and
         type(recipient_descriptor['bytes']) is int and 0 < recipient_descriptor['bytes'] <= 8192 and
         digest(recipient_descriptor['sha256']), 'EXACT_NEW_ADOPTION_SELECTION')
    selected_recipient = dict(recipient_descriptor)
    need(adoption_sha256 != RETAINED_ADOPTION and selected_recipient['sha256'] != RETAINED_RECIPIENT,
         'RETAINED_ADOPTION_OR_RECIPIENT')
    original = types.ModuleType('exact_original_public_binder')
    exec(compile(original_bytes, '<exact-original-public-binder>', 'exec'), original.__dict__)
    prepared = original.assignments(original_bytes, {
        'ISSUER': repr(ISSUER),
        'RETAINED_HOST_ADOPTION_ISSUER': repr(ISSUER),
        'RETAINED_HOST_ADOPTION_SHA256': repr(adoption_sha256),
    })
    bound = types.ModuleType('selected_successor_public_binder')
    exec(compile(prepared, '<selected-successor-public-binder>', 'exec'), bound.__dict__)

    def bind_public(structural, public, inputs):
        raw = inputs.get('host_adoption') if type(inputs) is dict else None
        need(type(raw) is bytes and hashlib.sha256(raw).hexdigest() == adoption_sha256,
             'EXACT_NEW_ADOPTION_SELECTION')
        adoption = bound.parse(raw)
        need(adoption.get('issuer_thread') == ISSUER and adoption.get('recipient') == selected_recipient,
             'EXACT_NEW_ADOPTION_SELECTION')
        return bound.bind_public(structural, public, inputs)

    return types.SimpleNamespace(
        ISSUER=ISSUER, RETAINED_HOST_ADOPTION_ISSUER=ISSUER,
        RETAINED_HOST_ADOPTION_SHA256=adoption_sha256,
        prepared_source=prepared, bind_public=bind_public, requirements=bound.requirements,
    )
