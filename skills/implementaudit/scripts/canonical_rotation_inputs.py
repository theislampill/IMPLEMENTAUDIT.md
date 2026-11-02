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


def _native_notification_v1(message):
    _require(type(message) is dict and set(message) in ({'method', 'params'},
        {'method', 'params', 'emittedAtMs'}) and type(message.get('method')) is str
        and type(message.get('params')) is dict, 'UNCERTAIN_STREAM')
    if 'emittedAtMs' in message:
        _require(_integer(message['emittedAtMs']), 'INVALID_NATIVE_EMISSION_METADATA')
    return message['method'], message['params']


def parse_exact_usage_v1(message, thread_id, turn_id, received_at_unix_ms, stream_revision):
    """Parse exact native counters only; parsing never authenticates a producer.

    Arbitrary usageMetadata and all model/tool/reasoning bodies are discarded.
    Receipt time/revision must come from the source-owned live stream; passing a
    retained probe here proves parser compatibility only.
    """
    method, params = _native_notification_v1(message)
    _require(method == 'rawResponse/completed', 'EXACT_RAW_EVENT_REQUIRED')
    _require(type(params) is dict
             and {'threadId', 'turnId', 'responseId', 'usage'} <= set(params)
             and set(params) <= {'threadId', 'turnId', 'responseId', 'usage', 'usageMetadata'},
             'EXACT_EVENT_SHAPE')
    _require('usageMetadata' not in params or type(params['usageMetadata']) is dict, 'EXACT_EVENT_METADATA_SHAPE')
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


def validate_reported_window_v1(record, binding, exact, cutoff_revision):
    """Reported configured window, not a measurement of physical capacity.

    UI usage counters never replace the raw exact numerator. A conservative
    operational budget may be lower than the host-reported window, never higher.
    Receipt clocks/revision are retained owner observations, not JSON send time.
    """
    _require(type(record) is dict and set(record) == {'schema','thread_id','turn_id',
             'model_context_window','received_at_unix_ms','received_monotonic_ns','stream_revision'}
             and record['schema'] == 'implementaudit.native-reported-window.v1'
             and record['thread_id'] == binding['thread_id'] and record['turn_id'] == binding['turn_id']
             and all(_integer(record[key], 1) for key in ('model_context_window','stream_revision'))
             and all(_integer(record[key]) for key in ('received_at_unix_ms','received_monotonic_ns'))
             and exact['stream_revision'] < record['stream_revision'] <= cutoff_revision
             and exact['received_at_unix_ms'] <= record['received_at_unix_ms']
             and binding['budget_policy']['configured_usable_tokens'] <= record['model_context_window'],
             'CURRENT_REPORTED_WINDOW_REQUIRED_OR_POLICY_EXCEEDS_HOST_REPORT')
    return record


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
        self._last_receipt_monotonic_ns = None
        self._reported_window = None
        self._quiescent = False
        self._problem = None
        self._connected = True
        self._admission_live = True
        self._active_lease = None
        self._consumed = False

    def observe(self, message, *, received_at_unix_ms=None, received_monotonic_ns=None):
        """Consume the actual live callback clocks, never timestamps in JSON.

        The existing owner supplies both clocks before logging or queue delay.
        Omission preserves the original immediate-callback API. Neither form
        authenticates custody or grants admission; source/issuer checks remain.
        """
        wall_now, mono_now = time.time_ns() // 1000000, time.monotonic_ns()
        supplied = received_at_unix_ms is not None or received_monotonic_ns is not None
        wall = received_at_unix_ms if supplied else wall_now
        mono = received_monotonic_ns if supplied else mono_now
        with self._signal_lock:
            self._revision += 1
            try:
                _require(not self._problem and self._connected and not self._consumed,
                         'NATIVE_CANDIDATE_INVALIDATED')
                _require(_integer(wall) and _integer(mono) and wall <= wall_now and mono <= mono_now
                         and (self._last_receipt_monotonic_ns is None or mono >= self._last_receipt_monotonic_ns),
                         'INVALID_OR_REORDERED_LIVE_RECEIPT_CLOCKS')
                self._last_receipt_monotonic_ns = mono
                method, params = _native_notification_v1(message)
                thread, turn = self._binding['thread_id'], self._binding['turn_id']
                if method == 'rawResponse/completed':
                    _require(self._snapshot is None, 'DUPLICATE_OR_REPLAYED_RESPONSE')
                    self._snapshot = parse_exact_usage_v1(
                        message, thread, turn, wall, self._revision)
                    self._received_monotonic_ns = mono
                elif method == 'turn/completed':
                    _require(set(params) == {'threadId','turn'} and params.get('threadId') == thread
                             and type(params.get('turn')) is dict and set(params['turn']) <= {'id','status','items','itemsView','startedAt','completedAt','durationMs','error'}
                             and params['turn'].get('error') is None and params['turn'].get('id') == turn
                             and params['turn'].get('status') == 'completed'
                             and self._snapshot is not None and not self._quiescent,
                             'QUIESCENT_TURN_REQUIRED')
                    self._quiescent = True
                elif method == 'thread/tokenUsage/updated':
                    _require(set(params) == {'threadId', 'turnId', 'tokenUsage'}
                             and params.get('threadId') == thread and params.get('turnId') == turn
                             and type(params['tokenUsage']) is dict, 'FOREIGN_NATIVE_SUBJECT')
                    usage = params['tokenUsage']
                    _require(set(usage) == {'last','total','modelContextWindow'}
                             and all(type(usage[key]) is dict and _USAGE_KEYS - {'cacheWriteInputTokens'} <= set(usage[key]) <= _USAGE_KEYS
                                     and all(_integer(value) for value in usage[key].values()) for key in ('last','total'))
                             and self._reported_window is None and self._snapshot is not None,
                             'UNKNOWN_DUPLICATE_OR_UNBOUND_WINDOW_EVENT')
                    record = {'schema':'implementaudit.native-reported-window.v1','thread_id':thread,'turn_id':turn,
                              'model_context_window':usage['modelContextWindow'], 'received_at_unix_ms':wall,
                              'received_monotonic_ns':mono,'stream_revision':self._revision}
                    self._reported_window = validate_reported_window_v1(record, self._binding, self._snapshot, self._revision)
                elif method == 'account/rateLimits/updated':
                    _require(set(params) == {'rateLimits'} and type(params['rateLimits']) is dict
                             and set(params['rateLimits']) <= {'credits', 'individualLimit', 'limitId', 'limitName',
                                 'planType', 'primary', 'secondary', 'rateLimitReachedType', 'spendControlReached'},
                             'UNKNOWN_ACCOUNT_TELEMETRY')
                elif method == 'turn/moderationMetadata':
                    _require(set(params) == {'threadId', 'turnId', 'metadata'}
                             and params['threadId'] == thread and params['turnId'] == turn
                             and type(params['metadata']) is dict, 'FOREIGN_NATIVE_SUBJECT')
                elif method == 'thread/status/changed':
                    _require(set(params) == {'threadId', 'status'} and params.get('threadId') == thread
                             and params.get('status') == {'type': 'idle'} and self._snapshot is not None,
                             'NATIVE_THREAD_NOT_QUIESCENT')
                    # Idle may precede turn/completed in the actual stream. It
                    # is ancillary only; the matching completion still owns
                    # the sole transition to _quiescent.
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
        validate_reported_window_v1(self._reported_window, self._binding, self._snapshot, self._revision)
        _require(type(subject) is dict and subject == self._binding['subject']
                 and _integer(source_bytes) and source_bytes == self._binding['source_bytes']
                 and _integer(source_tokens) and source_tokens == self._binding['source_tokens'],
                 'CANONICAL_SUBJECT_OR_MEASUREMENT_CHANGED')
        maximum = self._binding['budget_policy']['maximum_age_ms']
        wall_age = time.time_ns() // 1000000 - self._snapshot['received_at_unix_ms']
        mono_age = time.monotonic_ns() - self._received_monotonic_ns
        _require(0 <= wall_age <= maximum and 0 <= mono_age <= maximum * 1000000,
                 'STALE_FUTURE_OR_UNCERTAIN_CUTOFF')


def _resolve_existing_owner_v1(controller=None):
    """Fixed physical existing-claim receiver; its source selection is None by default."""
    import hashlib
    import os
    from pathlib import Path
    import stat
    import sys
    import types
    path = Path(__file__).absolute().with_name('claim-run-rotation.py')
    before = os.lstat(path)
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or getattr(before, 'st_file_attributes', 0) & 0x400:
        raise NativeInputError('NATIVE_CLAIM_RECEIVER_ALIAS')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(512 * 1024 + 1)
        after = os.fstat(stream.fileno())
    identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)
    if identity(before) != identity(opened) or identity(opened) != identity(after) or len(raw) != before.st_size or len(raw) > 512 * 1024:
        raise NativeInputError('NATIVE_CLAIM_RECEIVER_CHANGED')
    name = '_native_existing_claim_receiver_' + hashlib.sha256(os.fsencode(path) + b'\0' + raw).hexdigest()
    if name not in sys.modules:
        module = types.ModuleType(name)
        module.__file__ = str(path)
        sys.modules[name] = module
        try:
            exec(compile(raw, str(path), 'exec'), module.__dict__)
        except BaseException:
            sys.modules.pop(name, None)
            raise
    return sys.modules[name]._resolve_native_input_state_v1(sys.modules[__name__], controller)


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
            cancellation = getattr(state, '_native_cancellation_wait', None)
            if cancellation is not None:
                try:
                    cancellation.check()
                except Exception as exc:
                    raise NativeInputError('NATIVE_SOURCE_CANCELLED_OR_UNAVAILABLE') from exc
            _require(not lease._closed and state._active_lease is lease, 'LEASE_EXPIRED')
            _require(_resolve_existing_owner_v1(self._subject['controller']) is state, 'EXISTING_OWNER_BINDING_CHANGED')
            with state._signal_lock:
                state._verify(self._subject, *self._counts, attempted_lease=lease._attempted)
                _require(state._revision == lease._revision, 'STREAM_CHANGED_AFTER_LEASE')
        except NativeInputError as exc:
            if self._started:
                raise self._unknown_error() from exc
            raise

    def ref_guards_v1(self):
        self.verify()
        expected = getattr(self._lease._state, '_native_revision_guards', None)
        if expected is None:
            return {}  # Existing declared mechanics fixtures; never durable admission.
        if type(expected) is not dict or len(expected) != 2 or any(
                type(ref) is not str or type(oid) is not str or re.fullmatch('[0-9a-f]{40}', oid) is None
                for ref, oid in expected.items()):
            raise self._unknown_error()
        controller = self._subject['controller']
        if set(expected) != {'refs/implementaudit/rotation-input-sources/' + controller,
                             'refs/implementaudit/rotation-input-grants/' + controller}:
            raise self._unknown_error()
        return dict(expected)

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
            exact_usage=copy.deepcopy(state._snapshot),
            reported_window=copy.deepcopy(state._reported_window), cutoff_revision=self._revision,
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
    state = _resolve_existing_owner_v1(subject.get('controller') if type(subject) is dict else None)
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
