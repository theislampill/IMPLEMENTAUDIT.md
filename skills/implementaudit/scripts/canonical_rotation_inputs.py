#!/usr/bin/env python3
"""Unadmitted exact native usage / configured-headroom input mechanics.

The production resolver intentionally refuses until the existing calibration and
host source owners admit an exact issuer/grant/semantic contract. Caller JSON,
matching hashes, and a callable returning True confer no authority. This module
opens no connection, starts no watcher, calls no model, and owns no publication.

An admitted owner must feed an unbroken, version-pinned stream from its ALREADY
OPEN connection, enforce this gate on EVERY context-changing request/injection,
and exclude other writers to the selected native thread. A completed turn is
required; autonomous in-flight model/tool work cannot be leased. Feed unexpected
records, disconnects, config changes, and grant withdrawal into invalidation.
The gate is an in-process integration obligation, not a lock on a remote server
or protection against another client that bypasses the existing owner.

The health value means headroom against a CONFIGURED usable operational budget
using exact upstream-accounted usage at its cutoff. It is neither measured model
capacity nor the UI's estimated remaining-context percentage. Experimental
rawResponse/completed is pinned to 0.153.4, not claimed as a stable public API.
"""
from __future__ import annotations

import copy
from contextlib import contextmanager
from collections import namedtuple
import re
import threading
import time


class NativeInputError(ValueError):
    """Native input custody, semantics, freshness, or lease is not established."""


class NativeInputOutcomeUnknown(NativeInputError):
    """An issued/uncertain publisher effect needs reconciliation, never blind retry."""


NATIVE_BINARY_SHA256 = '444a3f0008050605cae73cd9b7a2dcac61294062dfaab56dd20430fd6498518b'
HEALTH_SEMANTICS = 'CONFIGURED_OPERATIONAL_HEADROOM_EXACT_USAGE_AT_CUTOFF'
_SUBJECT_KEYS = {'controller', 'claim_id', 'run_root_identity', 'receipt_token',
                 'state_sha256', 'roadmap_sha256'}
_USAGE_KEYS = {'inputTokens', 'outputTokens', 'totalTokens', 'cachedInputTokens',
               'cacheWriteInputTokens', 'reasoningOutputTokens'}


def _require(condition, reason):
    if not condition:
        raise NativeInputError(reason)


def _integer(value, minimum=0):
    return type(value) is int and minimum <= value <= 2**63 - 1


def _text(value):
    return type(value) is str and 0 < len(value) <= 512 and not any(ord(c) < 32 for c in value)


def _sha(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def parse_exact_usage_v1(message, thread_id, turn_id, received_at_unix_ms, stream_revision):
    """Parse exact native counters only; parsing never authenticates a producer.

    Arbitrary usageMetadata and all model/tool/reasoning bodies are discarded.
    Receipt time/revision must come from the source-owned live stream; passing a
    retained probe here proves parser compatibility only.
    """
    _require(type(message) is dict and set(message) == {'method', 'params'}
             and message['method'] == 'rawResponse/completed', 'EXACT_RAW_EVENT_REQUIRED')
    params = message['params']
    _require(type(params) is dict
             and {'threadId', 'turnId', 'responseId', 'usage'} <= set(params)
             and set(params) <= {'threadId', 'turnId', 'responseId', 'usage', 'usageMetadata'},
             'EXACT_EVENT_SHAPE')
    _require(_text(thread_id) and _text(turn_id)
             and params['threadId'] == thread_id and params['turnId'] == turn_id,
             'FOREIGN_NATIVE_SUBJECT')
    response = params['responseId']
    _require(_text(response) and re.fullmatch(r'resp_[A-Za-z0-9_-]+', response) is not None,
             'RESPONSE_ID_REQUIRED')
    usage = params['usage']
    _require(type(usage) is dict and _USAGE_KEYS - {'cacheWriteInputTokens'} <= set(usage)
             and set(usage) <= _USAGE_KEYS, 'EXACT_USAGE_REQUIRED')
    usage = dict(usage, cacheWriteInputTokens=usage.get('cacheWriteInputTokens', 0))
    _require(all(_integer(value) for value in usage.values())
             and usage['totalTokens'] == usage['inputTokens'] + usage['outputTokens']
             and usage['cachedInputTokens'] <= usage['inputTokens']
             and usage['cacheWriteInputTokens'] <= usage['inputTokens']
             and usage['reasoningOutputTokens'] <= usage['outputTokens'], 'INVALID_EXACT_USAGE')
    _require(_integer(received_at_unix_ms) and _integer(stream_revision, 1), 'INVALID_SOURCE_CUTOFF')
    return {'thread_id': thread_id, 'turn_id': turn_id, 'response_id': response,
            'usage': usage, 'received_at_unix_ms': received_at_unix_ms,
            'stream_revision': stream_revision}


def configured_headroom_bp_v1(exact_used_tokens, configured_usable_tokens):
    """Ceil remaining basis points so rounding cannot fire the <=2500 arm early."""
    _require(_integer(exact_used_tokens) and _integer(configured_usable_tokens, 1),
             'INVALID_CONFIGURED_BUDGET')
    remaining = max(configured_usable_tokens - exact_used_tokens, 0)
    return (remaining * 10000 + configured_usable_tokens - 1) // configured_usable_tokens


def _validate_binding(binding):
    required = {'issuer', 'grant_sha256', 'producer_sha256', 'semantic_contract_sha256',
                'host', 'budget_policy', 'tokenizer', 'subject', 'source_bytes',
                'source_tokens', 'thread_id', 'turn_id'}
    _require(type(binding) is dict and set(binding) == required, 'INCOMPLETE_OWNER_BINDING')
    _require(_text(binding['issuer']) and _text(binding['thread_id']) and _text(binding['turn_id'])
             and all(_sha(binding[key]) for key in
                     ('grant_sha256', 'producer_sha256', 'semantic_contract_sha256')),
             'INVALID_OWNER_IDENTITIES')
    subject = binding['subject']
    _require(type(subject) is dict and set(subject) == _SUBJECT_KEYS
             and all(_text(value) for value in subject.values())
             and _sha(subject['state_sha256']) and _sha(subject['roadmap_sha256']), 'INVALID_PAIR_SUBJECT')
    host = binding['host']
    _require(type(host) is dict
             and set(host) == {'name', 'version', 'binary_sha256', 'effective_config_sha256', 'model'}
             and host['name'] == 'codex' and host['version'] == '0.153.4'
             and host['binary_sha256'] == NATIVE_BINARY_SHA256
             and _sha(host['effective_config_sha256']) and _text(host['model']), 'UNSUPPORTED_HOST_BINDING')
    policy = binding['budget_policy']
    _require(type(policy) is dict
             and set(policy) == {'id', 'configured_usable_tokens', 'maximum_age_ms'}
             and _text(policy['id']) and _integer(policy['configured_usable_tokens'], 1)
             and _integer(policy['maximum_age_ms'], 1) and policy['maximum_age_ms'] <= 30000,
             'INVALID_BUDGET_POLICY')
    tokenizer = binding['tokenizer']
    _require(type(tokenizer) is dict
             and set(tokenizer) == {'name', 'implementation', 'version', 'encoding_sha256'}
             and all(_text(value) for value in tokenizer.values()) and _sha(tokenizer['encoding_sha256'])
             and _integer(binding['source_bytes']) and _integer(binding['source_tokens']),
             'INVALID_MEASURED_SOURCE_BINDING')


class NativeInputState:
    """One native response candidate held by the existing connection owner.

    Constructing this object proves no custody or admission. Only the fixed
    resolver may select it for the production path. A poisoned/consumed candidate
    is never reset: the existing owner must acquire a genuinely newer source
    cutoff and retain its replay census before selecting another candidate.
    """
    def __init__(self, binding):
        _validate_binding(binding)
        self._binding = copy.deepcopy(binding)
        self._gate = threading.RLock()
        # Incoming revocation must never wait for a potentially slow canonical
        # publisher. This lock protects only short state reads/writes; no external
        # callback, filesystem operation, or outgoing send runs while it is held.
        self._signal_lock = threading.RLock()
        self._revision = 0
        self._snapshot = None
        self._received_monotonic_ns = None
        self._quiescent = False
        self._problem = None
        self._connected = True
        self._admission_live = True
        self._active_lease = None
        self._consumed = False

    def observe(self, message):
        """Feed every native record after acquisition starts, never filtered JSON."""
        with self._signal_lock:
            self._revision += 1
            try:
                _require(not self._problem and self._connected and not self._consumed,
                         'NATIVE_CANDIDATE_INVALIDATED')
                _require(type(message) is dict and set(message) == {'method', 'params'}, 'UNCERTAIN_STREAM')
                method, params = message['method'], message['params']
                thread, turn = self._binding['thread_id'], self._binding['turn_id']
                if method == 'rawResponse/completed':
                    _require(self._snapshot is None, 'DUPLICATE_OR_REPLAYED_RESPONSE')
                    self._snapshot = parse_exact_usage_v1(
                        message, thread, turn, time.time_ns() // 1000000, self._revision)
                    self._received_monotonic_ns = time.monotonic_ns()
                elif method == 'turn/completed':
                    _require(type(params) is dict and params.get('threadId') == thread
                             and type(params.get('turn')) is dict and params['turn'].get('id') == turn
                             and params['turn'].get('status') == 'completed'
                             and self._snapshot is not None and not self._quiescent,
                             'QUIESCENT_TURN_REQUIRED')
                    self._quiescent = True
                elif method == 'thread/tokenUsage/updated':
                    # Recognized ancillary UI/accounting event; never a numerator.
                    _require(type(params) is dict and params.get('threadId') == thread
                             and params.get('turnId') == turn, 'FOREIGN_NATIVE_SUBJECT')
                elif method == 'thread/status/changed':
                    _require(type(params) is dict and params.get('threadId') == thread
                             and params.get('status') == {'type': 'idle'} and self._quiescent,
                             'NATIVE_THREAD_NOT_QUIESCENT')
                else:
                    raise NativeInputError('CONTEXT_CHANGE_OR_UNKNOWN_RECORD')
            except NativeInputError as exc:
                self._problem = str(exc)
                raise

    def invalidate(self, reason):
        with self._signal_lock:
            self._revision += 1
            self._problem = 'OWNER_INVALIDATION:' + str(reason)

    def disconnect(self):
        with self._signal_lock:
            self._connected = False
            self.invalidate('STREAM_DISCONNECTED')

    def withdraw_admission(self):
        with self._signal_lock:
            self._admission_live = False
            self.invalidate('GRANT_WITHDRAWN')

    @contextmanager
    def context_change(self, reason):
        """Existing owner wraps the actual send/injection, not a later notification."""
        with self._gate:
            _require(self._active_lease is None, 'CONTEXT_MUTATION_BLOCKED_BY_LEASE')
            self.invalidate(reason)
            yield

    def _verify(self, subject, source_bytes, source_tokens, *, attempted_lease=False):
        # Caller holds _signal_lock; never call external code from this method.
        _require(not self._problem and self._connected and self._admission_live
                 and (not self._consumed or attempted_lease),
                 'SOURCE_OR_GRANT_INVALIDATED')
        _require(self._snapshot is not None and self._quiescent, 'EXACT_QUIESCENT_CUTOFF_REQUIRED')
        _require(type(subject) is dict and subject == self._binding['subject']
                 and _integer(source_bytes) and source_bytes == self._binding['source_bytes']
                 and _integer(source_tokens) and source_tokens == self._binding['source_tokens'],
                 'CANONICAL_SUBJECT_OR_MEASUREMENT_CHANGED')
        maximum = self._binding['budget_policy']['maximum_age_ms']
        wall_age = time.time_ns() // 1000000 - self._snapshot['received_at_unix_ms']
        mono_age = time.monotonic_ns() - self._received_monotonic_ns
        _require(0 <= wall_age <= maximum and 0 <= mono_age <= maximum * 1000000,
                 'STALE_FUTURE_OR_UNCERTAIN_CUTOFF')


def _resolve_existing_owner_v1():
    """Fixed source selection point; no plugin path, callback, JSON grant, or fallback.

    Changing this requires the existing owner's separate source/issuer/grant and
    live host integration admission. It must return that owner's already-held
    NativeInputState and enforce its replay census and exclusive native custody.
    """
    raise NativeInputError('OWNER_UNAVAILABLE_NO_ADMITTED_NATIVE_INPUT_SOURCE')


_EffectCheckpoint = namedtuple('_EffectCheckpoint',
    'source_revision grant_sha256 response_id deadline_unix_ms ordinal')


class _PublisherGuard:
    """Source checkpoints for existing RetainedInputs.verify / update_refs.

    before_effect() returns the expected source revision and grant token for the
    existing publisher's real CAS boundary. This module does NOT add those fields
    to a Git transaction or invent a currentness store. Strict prevention of a
    racing effect requires the actual source owner and publisher to enforce that
    comparison atomically. Without it, after_effect()/finish detect a changed
    source and report UNKNOWN outcome instead of certifying success.
    """
    def __init__(self, lease, subject, source_bytes, source_tokens):
        self._lease = lease
        self._subject = copy.deepcopy(subject)
        self._counts = source_bytes, source_tokens
        self._started = 0
        self._completed = 0
        self._pending = None
        self._unknown = False

    def _unknown_error(self):
        self._unknown = True
        return NativeInputOutcomeUnknown('NATIVE_EFFECT_OUTCOME_UNKNOWN_RECONCILIATION_REQUIRED')

    def _require_known_outcome(self):
        if self._unknown:
            raise self._unknown_error()

    def verify(self):
        """Call after the existing retained-input checks, also before each effect."""
        self._require_known_outcome()
        lease, state = self._lease, self._lease._state
        try:
            _require(not lease._closed and state._active_lease is lease, 'LEASE_EXPIRED')
            _require(_resolve_existing_owner_v1() is state, 'EXISTING_OWNER_BINDING_CHANGED')
            with state._signal_lock:
                state._verify(self._subject, *self._counts, attempted_lease=lease._attempted)
                _require(state._revision == lease._revision, 'STREAM_CHANGED_AFTER_LEASE')
        except NativeInputError as exc:
            if self._started:
                raise self._unknown_error() from exc
            raise

    def before_effect(self):
        """Immediately before the actual existing publisher commit/CAS checkpoint."""
        self._require_known_outcome()
        if self._pending is not None:
            raise self._unknown_error()
        self.verify()
        self._started += 1
        state = self._lease._state
        self._pending = _EffectCheckpoint(
            self._lease._revision, state._binding['grant_sha256'],
            state._snapshot['response_id'], state._snapshot['received_at_unix_ms']
            + state._binding['budget_policy']['maximum_age_ms'], self._started)
        return self._pending

    def after_effect(self, checkpoint):
        """Immediately after the attempted effect; a race cannot become success."""
        try:
            self._require_known_outcome()
            _require(self._pending is not None and checkpoint is self._pending,
                     'EFFECT_CHECKPOINT_MISMATCH')
            self.verify()
        except NativeInputError as exc:
            raise self._unknown_error() from exc
        self._pending = None
        self._completed += 1

    def _finish(self):
        # Recheck even if the publisher forgot or swallowed after_effect.
        self.verify()
        _require(self._started > 0 and self._pending is None
                 and self._started == self._completed, 'PUBLISHER_CHECKPOINT_MISSING')


class _RotationInputLease:
    def __init__(self, state):
        self._state = state
        self._revision = state._revision
        self._closed = False
        self._attempted = False
        self._observation = copy.deepcopy(state._binding)
        self._observation.update(
            exact_usage=copy.deepcopy(state._snapshot), cutoff_revision=self._revision,
            context_health_bp=configured_headroom_bp_v1(
                state._snapshot['usage']['totalTokens'],
                state._binding['budget_policy']['configured_usable_tokens']),
            health_semantics=HEALTH_SEMANTICS,
            authority_ceiling='INPUT_ONLY_NO_CURRENTNESS_OR_PUBLICATION_AUTHORITY')

    @property
    def observation(self):
        return copy.deepcopy(self._observation)

    def admit(self, current_subject, measured_source_bytes, measured_source_tokens, publish):
        """Call publish(observation, guard) under the outgoing mutation gate.

        publish receives an immutable-by-copy observation, not effect authority.
        The publisher must call guard.before_effect() immediately before each
        actual commit/CAS checkpoint and guard.after_effect(token) immediately
        afterward. Incoming signals use a separate short lock and remain visible.
        The publisher still owns actual source-CAS integration and canonical pair
        checks. Once entered, any callback exception is conservatively UNKNOWN:
        an exception class cannot prove that uninstrumented effects did not run.
        Unknown is sticky even if a callback restores an owner or checkpoint.
        There is no claim of remote or cross-store atomicity here.
        """
        state = self._state
        with state._gate:
            _require(not self._closed and not self._attempted and state._active_lease is self,
                     'LEASE_EXPIRED_OR_ALREADY_ATTEMPTED')
            guard = _PublisherGuard(self, current_subject, measured_source_bytes, measured_source_tokens)
            guard.verify()
            _require(callable(publish), 'EXISTING_PUBLISHER_REQUIRED')
            self._attempted = True
            with state._signal_lock:
                state._consumed = True
            try:
                result = publish(self.observation, guard)
            except BaseException as exc:
                raise guard._unknown_error() from exc
            try:
                guard._finish()
            except NativeInputError as exc:
                raise guard._unknown_error() from exc
            return result


@contextmanager
def rotation_input_lease_v1(subject, measured_source_bytes, measured_source_tokens):
    """Production entry: fails closed until an existing native owner is selected."""
    state = _resolve_existing_owner_v1()
    _require(type(state) is NativeInputState, 'EXISTING_OWNER_CAPABILITY_REQUIRED')
    with state._gate:
        with state._signal_lock:
            state._verify(subject, measured_source_bytes, measured_source_tokens)
            _require(state._active_lease is None, 'NATIVE_INPUT_LEASE_ALREADY_HELD')
            lease = _RotationInputLease(state)
            state._active_lease = lease
    try:
        yield lease
    finally:
        with state._gate:
            lease._closed = True
            state._active_lease = None
