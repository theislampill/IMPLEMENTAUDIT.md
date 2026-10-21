"""Constructed owner-transaction controls; no native performance/authority credit.

Frozen baseline at 8e2999fc: ordinary result = 6 full route validations;
R0035 native orchestration = 4. The required successor uses 2 enclosing checks.
The independent projection oracle below does not call producer formatters.
"""
import argparse
import base64
import contextlib
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
PEERS = ROOT / 'source-peers/route-graph/skills/implementaudit/scripts'


def load(name):
    path = PEERS / name
    module = types.ModuleType('cost_control_' + name.replace('.', '_'))
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def digest(value):
    return 'sha256:' + hashlib.sha256(value if type(value) is bytes else raw(value)).hexdigest()


def wire(value, identity=None):
    data = value if type(value) is bytes else raw(value)
    result = {'bytes': len(data), 'digest': digest(data), 'bytes_b64': base64.b64encode(data).decode()}
    if identity is not None: result['identity'] = identity
    return result


class Refusal(ValueError):
    pass


class Harness:
    def __init__(self, root):
        self.rt, self.wg, self.root = load('route-transaction.py'), load('compile-work-graph.py'), root
        self.input = root / 'input.txt'; self.input.write_bytes(b'original exact input\n')
        self.source_digest = digest(Path(self.rt.__file__).read_bytes())
        self.controller, self.controller_oid = 'cost-control', '1' * 40
        self.current = dict(controller_id=self.controller, controller_record_oid=self.controller_oid,
            repository_identity=str(root), claim_id='2' * 32, explicit_run_root=str(root),
            continuity_generation='G0001', continuity_receipt='refs/implementaudit/continuity-receipts/cost-control/G0001@' + '3' * 40,
            boundary_kind='handoff-resume', boundary_event_id='fixture-boundary', next_action='fixture-review')
        boundary = {'kind': self.current['boundary_kind'], 'event_id': self.current['boundary_event_id']}
        boundary['digest'] = digest(boundary)
        scope = {'identity': self.current['next_action']}; scope['digest'] = digest(scope)
        action = {'identity': 'fixture-review', 'class': 'REQUIRED_INTERNAL_CHILD', 'argv': ['route-trigger', 'IMMUTABLE_INDEPENDENT_REVIEW']}
        action['digest'] = digest(action)
        self.request = {'schema': 'implementaudit.route-decision-request.v1', 'predicate_version': 'R0033.route-predicate.v1',
            'boundary': boundary, 'scope': scope, 'action': action,
            'inputs': [{'identity': 'input', 'path': 'input.txt', 'digest': digest(self.input.read_bytes())}]}
        self.record = {}; self.objects = {}; self.oid = '6' * 40
        self.child_digest = digest(b'fixture skill')
        self.producer_bytes = b'fixed source fixture'
        self.source_read_count = 0

    def package(self, *args, **kwargs):
        return ({'head': 'a' * 40, 'tree': 'b' * 40, 'source_digests': {'route-transaction.py': self.source_digest},
                 'action_executable': {'requested': 'route-trigger', 'resolved': 'R0033:built-in', 'digest': digest(self.request['action']['argv'])}},
                {'identity': '/constructed/audit-assess/SKILL.md', 'digest': self.child_digest})

    def canonical(self, repo, oid, record, **kwargs):
        if record.get('record_identity') != digest({k: v for k, v in record.items() if k != 'record_identity'}):
            raise Refusal('canonical record digest differs')

    def lineage(self, repo, oid, record, **kwargs):
        if record['lifecycle']['delivery'] != self.opened['lifecycle']['delivery']:
            raise Refusal('lineage delivery differs')

    def git(self, repo, *args, **kwargs):
        if args[:1] != ('for-each-ref',): raise AssertionError('unexpected native Git call')
        return 'refs/implementaudit/controllers/' + self.controller + '\t' + self.controller_oid + '\n' + self.rt.ref_name(self.controller) + '\t' + self.oid

    @contextlib.contextmanager
    def patched(self):
        with contextlib.ExitStack() as stack:
            real_digest = self.rt.file_digest
            def source_digest(path):
                return self.source_digest if Path(path) == Path(self.rt.__file__) else real_digest(path)
            for name, replacement in {
                'pure_route_environment': lambda: {}, 'current_controller': lambda *a, **k: copy.deepcopy(self.current),
                'executing_package_evidence': self.package, 'current_ref': lambda *a, **k: (self.oid, copy.deepcopy(self.record)),
                'validate_canonical_route_record_bytes': self.canonical, 'validate_lifecycle_predecessor_chain': self.lineage,
                'RouteObjectReader': lambda *a: contextlib.nullcontext(None),
                'git_blob_bytes': lambda repo, oid, *a, **k: raw(self.objects[oid]), 'git': self.git, 'file_digest': source_digest,
                'fail': lambda message, **kwargs: (_ for _ in ()).throw(Refusal(message)),
            }.items(): stack.enter_context(patch.object(self.rt, name, side_effect=replacement))
            self.create_records()
            self.validation = stack.enter_context(patch.object(self.rt, 'validate_pure_current_route', wraps=self.rt.validate_pure_current_route))
            yield self

    def create_records(self):
        basis = self.rt.route_semantic_basis(self.root, self.current, self.request, 'G0001')
        decision, classification, invalidators, evidence, fingerprint, transaction, obligation = self.rt.route_semantics_from_basis(
            self.current, self.request, 'G0001', digest('correlation'), basis)
        packet = {'schema': 'implementaudit.route-packet.v1', 'obligation_id': obligation, 'route_transaction_id': transaction,
            'target_identity': 'audit-assess', 'source_event': {'schema': 'implementaudit.source-event.v1', 'source_identity': 'fixture-source',
            'provenance': {'schema': 'implementaudit.source-event-provenance.v1', 'event_id': 'fixture-source', 'host_correlation_id': digest('correlation')},
            'body': 'Constructed immutable review input', 'kind': 'one-shot-action', 'reactivation': {'reopen': False, 'target_changed': False, 'invalidating_evidence': False}}}
        delivery = {'packet': wire(packet), 'child': wire(b'fixture skill', '/constructed/audit-assess/SKILL.md')}
        returned = {'schema': 'implementaudit.child-return.v1', 'obligation_id': obligation, 'route_transaction_id': transaction,
            'packet_digest': delivery['packet']['digest'], 'status': 'RETURNED', 'payload': {'bounded_review': 'fixture'}}
        accepted = {'schema': 'implementaudit.governor-route-decision.v1', 'obligation_id': obligation, 'route_transaction_id': transaction,
            'return_digest': wire(returned)['digest'], 'outcome': 'SATISFIED', 'reason': 'Constructed scoped receiving'}
        rec = {'schema': 'implementaudit.route-decision.v1', 'predicate_version': 'R0033.route-predicate.v1',
            **{k: self.current[k] for k in ('controller_id', 'claim_id', 'explicit_run_root', 'continuity_generation', 'continuity_receipt')},
            'host_id': 'codex', 'host_session_id': 'fixture-session', 'host_binding_generation': 'G0001', 'host_correlation_id': digest('correlation'),
            'boundary': self.request['boundary'], 'scope': self.request['scope'], 'action': self.request['action'],
            'inputs': basis['observed_inputs'], 'package': basis['package'], 'child_source': basis['child_source'],
            'evidence': {k: evidence[k] for k in ('owner', 'authority', 'effect', 'dependency')}, 'expiry_fingerprint': fingerprint,
            'decision': decision, 'classification': classification, 'invalidators': invalidators, 'route_transaction_id': transaction,
            'obligation_id': obligation, 'history_query': None, 'route_state': 'OPEN', 'predecessor_record_oid': '0' * 40,
            'lifecycle': {'state': 'OPEN', 'logical_task': 'fixture-review-task', 'delivery': delivery,
                'child_return': None, 'governor_decision': None, 'governor_decision_count': 0, 'execution_evidence': None}}
        def seal(value): value['record_identity'] = digest({k: v for k, v in value.items() if k != 'record_identity'}); return value
        self.opened = seal(copy.deepcopy(rec)); self.objects['4' * 40] = self.opened
        rec['route_state'] = rec['lifecycle']['state'] = 'RETURNED'; rec['predecessor_record_oid'] = '4' * 40
        rec['lifecycle']['child_return'] = wire(returned); self.objects['5' * 40] = seal(copy.deepcopy(rec))
        rec['route_state'] = rec['lifecycle']['state'] = 'SATISFIED'; rec['predecessor_record_oid'] = '5' * 40
        rec['lifecycle']['governor_decision'] = wire(accepted); rec['lifecycle']['governor_decision_count'] = 1
        self.record = seal(rec)

    def summary(self):
        return {'controller_id': self.controller, 'controller_record_oid': self.controller_oid, 'ref': self.rt.ref_name(self.controller),
            'record_oid': self.oid, **{k: self.record[k] for k in ('record_identity', 'decision', 'classification', 'route_transaction_id', 'obligation_id', 'route_state')}}

    def expected_scope(self):
        rec = self.record
        value = {'schema': 'implementaudit.current-route-scope.v1', 'authority_ceiling': 'READ_ONLY_CURRENT_ROUTE_FACT', 'establishes': [],
            'route': self.summary(), 'scope': rec['scope'], 'boundary': rec['boundary'],
            'owner': {k: rec[k] for k in ('controller_id', 'claim_id', 'explicit_run_root', 'continuity_generation', 'continuity_receipt')},
            'host': {k: rec[k] for k in ('host_id', 'host_session_id', 'host_binding_generation', 'host_correlation_id')},
            'source': {'predicate_version': rec['predicate_version'], 'record_schema': rec['schema'], 'producer_sha256': self.source_digest[7:],
                'record_sha256': hashlib.sha256(json.dumps(rec, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode() + b'\n').hexdigest()},
            'expiry_fingerprint': rec['expiry_fingerprint'], 'satisfaction': rec['lifecycle']['governor_decision']['digest']}
        return {**value, 'digest': digest(value)[7:]}

    def expected_opening(self):
        rec, opened = self.record, self.opened
        value = {'schema': 'implementaudit.r0033-current-episode-binding.v1', 'route_current': self.summary(), 'open_record_oid': '4' * 40,
            'open_record_identity': opened['record_identity'], 'logical_task': 'fixture-review-task', 'selected_child_role': 'audit-assess',
            'selected_child_target': 'independently assess the exact immutable review packet',
            'packet_pin': {k: opened['lifecycle']['delivery']['packet'][k] for k in ('bytes', 'digest')},
            'skill_pin': {k: opened['lifecycle']['delivery']['child'][k] for k in ('identity', 'bytes', 'digest')},
            'host_and_scope': {k: rec[k] for k in ('host_id', 'host_session_id', 'host_binding_generation', 'host_correlation_id',
                'continuity_generation', 'continuity_receipt', 'obligation_id', 'route_transaction_id', 'controller_id', 'claim_id', 'explicit_run_root')},
            'canonical_route_currentness': 'VALIDATED_AT_READ', 'authority_ceiling': 'NONE'}
        opening = {k: value[k] for k in ('open_record_oid', 'open_record_identity', 'logical_task', 'selected_child_role', 'selected_child_target', 'packet_pin', 'skill_pin', 'host_and_scope')}
        return {**value, 'opening_digest': digest(opening), 'binding_digest': digest(value)}

    def expected_result(self):
        return {'status': self.record['route_state'], 'canonical_route': self.summary(), 'opening': self.expected_opening(), 'scope': self.record['scope'],
            'packet': self.record['lifecycle']['delivery']['packet'], 'child_return': self.record['lifecycle']['child_return'],
            'governor_decision': self.record['lifecycle']['governor_decision']}

    @contextlib.contextmanager
    def graph_patched(self, on_projection=None, legacy=False, mutate_observation=False):
        binding = dict(acquisition='NATIVE_CONTINUITY_VERIFIED', controller=self.controller, claim=self.current['claim_id'],
            receipt=self.current['continuity_receipt'], epoch='G0001', candidate_head='a' * 40, candidate_tree='b' * 40,
            worktree_digest='c' * 64, continuity_helper_digest='d' * 64)
        snapshot = {'STATE.md': b'fixture state', 'ROADMAP.md': b'fixture roadmap'}
        self.graph_snapshot, self.graph_binding, self.graph_read_set = snapshot, binding, {}
        nodes = [{'id': 'review', 'route_scopes': [self.record['scope']['identity']]}]
        producer = types.SimpleNamespace(read_current_route_scope_v1=self.rt.read_current_route_scope_v1) if legacy else self.rt
        def compile_docs(snap, bound, *, acquire_only=False, _route_observation=None):
            if acquire_only: return {'nodes': copy.deepcopy(nodes)}
            value = {'nodes': copy.deepcopy(nodes), 'route': self.wg._route_observation_value(_route_observation)}
            if mutate_observation: _route_observation.value['scope']['identity'] = 'foreign mutation'
            if on_projection: on_projection()
            return value
        with contextlib.ExitStack() as stack:
            self.continuity = stack.enter_context(patch.object(self.wg, '_native_continuity', side_effect=lambda *a: copy.deepcopy(binding)))
            self.documents = stack.enter_context(patch.object(self.wg, '_native_source_snapshot', side_effect=lambda *a: copy.deepcopy(snapshot)))
            self.readset = stack.enter_context(patch.object(self.wg, '_acquire_native_read_set', side_effect=lambda *a: copy.deepcopy(self.graph_read_set)))
            stack.enter_context(patch.object(self.wg, '_compile_native_documents_v1', side_effect=compile_docs))
            # Explicit source-only composition; ROOT alone updates production pins.
            stack.enter_context(patch.object(self.wg, '_NATIVE_ROUTE_PRODUCER_SHA256', self.source_digest[7:]))
            stack.enter_context(patch.object(self.wg, '_native_route_scope_module_v1', side_effect=lambda: (producer, Path(self.rt.__file__), self.producer_bytes)))
            yield


class RouteCostControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='route-cost-controls-'); self.addCleanup(self.temp.cleanup)
        self.h = Harness(Path(self.temp.name))
        self.scope = self.h.patched(); self.scope.__enter__(); self.addCleanup(self.scope.__exit__, None, None, None)

    def test_ordinary_two_full_validations_and_independent_oracle(self):
        actual = self.h.rt.read_current_ordinary_result_v1(self.h.root, self.h.controller)
        self.assertEqual(actual, self.h.expected_result())
        self.assertEqual(self.h.validation.call_count, 2, 'baseline is six nested full validations')

    def test_r35_two_full_validations_and_original_fences(self):
        with self.h.graph_patched(): actual = self.h.wg.read_native_run_v1(self.h.root, self.h.root)
        self.assertEqual(actual['route'], self.h.expected_scope())
        self.assertEqual(self.h.validation.call_count, 2, 'baseline is four full validations')
        self.assertEqual((self.h.continuity.call_count, self.h.documents.call_count, self.h.readset.call_count), (2, 2, 2))

    def test_standalone_scope_and_opening_preserve_oracle(self):
        self.assertEqual(self.h.rt.read_current_route_scope_v1(self.h.root, self.h.controller), self.h.expected_scope())
        self.assertEqual(self.h.validation.call_count, 2)
        self.h.validation.reset_mock()
        self.assertEqual(self.h.rt.read_current_episode_binding_v1(self.h.root, self.h.controller), self.h.expected_opening())
        self.assertEqual(self.h.validation.call_count, 2)

    def test_legacy_r35_owner_keeps_original_double_read(self):
        with self.h.graph_patched(legacy=True): actual = self.h.wg.read_native_run_v1(self.h.root, self.h.root)
        self.assertEqual(actual['route'], self.h.expected_scope())
        self.assertEqual(self.h.validation.call_count, 4)

    def test_pinned_input_drift_with_refs_unchanged_is_rejected(self):
        original = self.h.summary()
        with self.h.graph_patched(on_projection=lambda: self.h.input.write_bytes(b'changed while deriving\n')):
            with self.assertRaisesRegex(Refusal, 'live predicate'):
                self.h.wg.read_native_run_v1(self.h.root, self.h.root)
        self.assertEqual(self.h.summary(), original)
        self.assertEqual(self.h.validation.call_count, 2)

    def test_receipt_package_and_child_source_drift_are_rejected(self):
        changes = (lambda: self.h.current.update(continuity_receipt=self.h.current['continuity_receipt'][:-40] + '9' * 40),
                   lambda: setattr(self.h, 'source_digest', digest('changed owner source')),
                   lambda: setattr(self.h, 'child_digest', digest('changed child source')))
        for change in changes:
            with self.subTest(change=change):
                current, source, child = copy.deepcopy(self.h.current), self.h.source_digest, self.h.child_digest
                with self.assertRaises(Refusal):
                    with self.h.rt.current_route_observation_v1(self.h.root, self.h.controller) as observed:
                        observed.ordinary_result_bytes(); change()
                self.h.current, self.h.source_digest, self.h.child_digest = current, source, child

    def test_resealed_foreign_open_lineage_is_rejected(self):
        self.h.objects['4' * 40]['host_session_id'] = 'foreign-session'
        opened = self.h.objects['4' * 40]
        opened['record_identity'] = digest({k: v for k, v in opened.items() if k != 'record_identity'})
        with self.assertRaisesRegex(Refusal, 'OPEN identity changed'):
            self.h.rt.read_current_ordinary_result_v1(self.h.root, self.h.controller)

    def test_mutation_of_each_yielded_projection_is_rejected(self):
        for method in ('scope_bytes', 'opening_bytes', 'ordinary_result_bytes'):
            with self.subTest(method=method):
                with self.h.rt.current_route_observation_v1(self.h.root, self.h.controller) as observed:
                    value = getattr(observed, method)()
                    self.assertIs(type(value), bytes)
                    with self.assertRaises(TypeError): value[0] = 123

    def test_closed_view_and_foreign_issuer_cannot_be_reused(self):
        with self.h.rt.current_route_observation_v1(self.h.root, self.h.controller) as observed:
            value = observed.scope_bytes()
        self.assertEqual(json.loads(value), self.h.expected_scope())
        with self.assertRaisesRegex(Refusal, 'closed'): observed.scope_bytes()
        with self.assertRaisesRegex(Refusal, 'source owner'):
            self.h.rt._CurrentRouteReadV1(object(), self.h.root, self.h.oid, self.h.record, self.h.summary())
        self.h.input.write_bytes(b'changed after prior successful read\n')
        with self.assertRaisesRegex(Refusal, 'live predicate'):
            self.h.rt.read_current_ordinary_result_v1(self.h.root, self.h.controller)

    def test_r35_retains_document_readset_continuity_and_source_fences(self):
        changes = (
            lambda: self.h.graph_snapshot.update({'STATE.md': b'changed'}),
            lambda: self.h.graph_read_set.update({'path:new': {'status': 'MISSING', 'sha256': None}}),
            lambda: self.h.graph_binding.update(receipt='changed'),
            lambda: setattr(self.h, 'producer_bytes', b'changed source fixture'),
        )
        for change in changes:
            with self.subTest(change=change):
                self.h.producer_bytes = b'fixed source fixture'
                with self.h.graph_patched(on_projection=change), self.assertRaises(self.h.wg.WorkGraphError):
                    self.h.wg.read_native_run_v1(self.h.root, self.h.root)

    def test_r35_refuses_mutation_of_its_provisional_owner_observation(self):
        with self.h.graph_patched(mutate_observation=True), self.assertRaisesRegex(self.h.wg.WorkGraphError, 'provisional native route observation was mutated'):
            self.h.wg.read_native_run_v1(self.h.root, self.h.root)

    def test_open_and_returned_ordinary_facts_keep_the_same_oracle(self):
        for oid, rec in (('4' * 40, self.h.opened), ('5' * 40, self.h.objects['5' * 40])):
            with self.subTest(state=rec['route_state']):
                self.h.oid, self.h.record = oid, copy.deepcopy(rec)
                self.h.validation.reset_mock()
                self.assertEqual(self.h.rt.read_current_ordinary_result_v1(self.h.root, self.h.controller), self.h.expected_result())
                self.assertEqual(self.h.validation.call_count, 2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--repo-root', type=Path, default=ROOT)
    args, remainder = parser.parse_known_args(); ROOT = args.repo_root.resolve(strict=True)
    PEERS = ROOT / 'source-peers/route-graph/skills/implementaudit/scripts'
    unittest.main(argv=[__file__, *remainder])
